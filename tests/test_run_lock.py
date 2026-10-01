# 실행 잠금(output/<run_id>/.lock)의 충돌·--take-lock 인수·잠금 없는 통과와 CLI approve·revoke 의 에이전트 세션 거부를 잠근다
from __future__ import annotations

import getpass
import io
import json
import os
import sys
import unittest
from collections.abc import Iterator
from contextlib import contextmanager, redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import scorecard_cli  # noqa: E402
from scorecard import stages  # noqa: E402
from scorecard.paths import run_paths  # noqa: E402
from scorecard.schema import SchemaError  # noqa: E402
from tests.test_collect_stage import SLUG, Sandbox  # noqa: E402


@contextmanager
def human_env(**extra: str) -> Iterator[None]:
    """에이전트 표지 변수를 모두 지운 환경. 테스트를 돌리는 세션이 에이전트여도 사람 셸처럼 만든다. `extra` 는 그 뒤에 더한다."""
    with mock.patch.dict(os.environ):
        for key in stages.AGENT_ENV_MARKERS:
            os.environ.pop(key, None)
        os.environ.update(extra)
        yield


class LockTestBase(unittest.TestCase):
    def setUp(self) -> None:
        self.box = Sandbox(("nvidia", "openai"))
        self.addCleanup(self.box.close)
        self.lock = self.box.run_dir / ".lock"

    def put_lock(self, owner: str) -> None:
        self.lock.write_text(json.dumps({"owner": owner, "started_utc": "2026-09-30T00:00:00Z", "stage": "research"}), encoding="utf-8")

    def read_lock(self) -> dict:
        return json.loads(self.lock.read_text(encoding="utf-8"))

    def cli(self, *argv: str, owner: str = "me", code: int = 0, env: dict | None = None) -> str:
        out, err = io.StringIO(), io.StringIO()
        with mock.patch.dict(os.environ, {"SCORECARD_AGENT": owner, **(env or {})}), redirect_stdout(out), redirect_stderr(err):
            got = scorecard_cli.main([str(a) for a in argv])
        self.assertEqual(got, code, f"{argv}\n{out.getvalue()}\n{err.getvalue()}")
        return out.getvalue() + err.getvalue()


class ClaimLockTest(LockTestBase):
    def test_no_lock_writes_owner_stage_and_time(self):
        stages.claim_lock(SLUG, "research", env={"SCORECARD_AGENT": "me"})
        lock = self.read_lock()
        self.assertEqual(sorted(lock), ["owner", "stage", "started_utc"])
        self.assertEqual((lock["owner"], lock["stage"]), ("me", "research"))
        self.assertRegex(lock["started_utc"], r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")

    def test_same_owner_keeps_start_and_updates_stage(self):
        self.put_lock("me")
        stages.claim_lock(SLUG, "calculate", env={"SCORECARD_AGENT": "me"})
        self.assertEqual(self.read_lock(), {"owner": "me", "started_utc": "2026-09-30T00:00:00Z", "stage": "calculate"})

    def test_other_owner_refused_and_lock_untouched(self):
        self.put_lock("other")
        before = self.lock.read_bytes()
        with self.assertRaisesRegex(SchemaError, "--take-lock"):
            stages.claim_lock(SLUG, "draft", env={"SCORECARD_AGENT": "me"})
        self.assertEqual(self.lock.read_bytes(), before)

    def test_take_lock_transfers_ownership(self):
        self.put_lock("other")
        stages.claim_lock(SLUG, "draft", take_lock=True, env={"SCORECARD_AGENT": "me"})
        lock = self.read_lock()
        self.assertEqual((lock["owner"], lock["stage"]), ("me", "draft"))
        self.assertNotEqual(lock["started_utc"], "2026-09-30T00:00:00Z")

    def test_unreadable_lock_needs_take_lock(self):
        self.lock.write_text("{깨짐", encoding="utf-8")
        with self.assertRaises(SchemaError):
            stages.claim_lock(SLUG, "research", env={"SCORECARD_AGENT": "me"})
        stages.claim_lock(SLUG, "research", take_lock=True, env={"SCORECARD_AGENT": "me"})
        self.assertEqual(self.read_lock()["owner"], "me")

    def test_owner_rule_matches_hook(self):
        self.assertEqual(stages.lock_owner({"SCORECARD_AGENT": "a", "ORCA_TERMINAL_HANDLE": "term_x"}), "a")
        self.assertEqual(stages.lock_owner({"ORCA_TERMINAL_HANDLE": "term_x"}), "term_x")
        self.assertEqual(stages.lock_owner({}), getpass.getuser())

    def test_approve_revoke_build_are_not_lock_stages(self):
        for stage in ("approve", "revoke", "build"):
            with self.subTest(stage=stage), self.assertRaises(SchemaError):
                stages.claim_lock(SLUG, stage, env={"SCORECARD_AGENT": "me"})


class CliLockTest(LockTestBase):
    def test_stage_refused_under_other_owner_then_taken_over(self):
        self.put_lock("other")
        out = self.cli("research", SLUG, code=1)
        self.assertIn("--take-lock", out)
        self.assertFalse(run_paths(SLUG).research.is_file())
        self.cli("research", SLUG, "--take-lock")
        self.assertTrue(run_paths(SLUG).research.is_file())
        self.assertEqual(self.read_lock()["owner"], "me")

    def test_stage_without_lock_passes_and_leaves_lock(self):
        self.assertFalse(self.lock.exists())
        self.cli("research", SLUG)
        self.cli("calculate", SLUG)
        self.assertEqual((self.read_lock()["owner"], self.read_lock()["stage"]), ("me", "calculate"))

    def test_every_lock_stage_refuses_other_owner(self):
        self.put_lock("other")
        for argv in (("collect", SLUG, "--kind", "news", "--dry-run"), ("research", SLUG), ("calculate", SLUG),
                     ("draft", SLUG), ("review-template", SLUG)):
            with self.subTest(stage=argv[0]):
                self.assertIn("--take-lock", self.cli(*argv, code=1))
        self.assertEqual(self.read_lock()["owner"], "other")

    def test_review_template_force_does_not_take_lock(self):
        self.put_lock("other")
        self.assertIn("--take-lock", self.cli("review-template", SLUG, "--force", code=1))

    def test_init_creates_lock_and_refuses_reinit_by_other(self):
        slug = "ai-scorecard-2026-09-locktest"
        args = ("init", slug, "--as-of", "2026-09-29", "--title", "잠금", "--request", "잠금", "--companies", "nvidia", "--rule", "v1.8")
        self.cli(*args, owner="first")
        lock = stages.lock_path(slug)
        self.assertEqual(json.loads(lock.read_text(encoding="utf-8"))["stage"], "init")
        self.assertIn("--take-lock", self.cli(*args, "--force", owner="second", code=1))
        self.cli(*args, "--force", "--take-lock", owner="second")
        self.assertEqual(json.loads(lock.read_text(encoding="utf-8"))["owner"], "second")

    def test_approve_does_not_touch_lock(self):
        self.put_lock("other")
        before = self.lock.read_bytes()
        with human_env():
            out = self.cli("approve", SLUG, "--by", "user", code=1)   # 계약 검증에서 멈추지만 잠금 때문은 아니다
        self.assertNotIn("--take-lock", out)
        self.assertEqual(self.lock.read_bytes(), before)


class AgentRefusalTest(LockTestBase):
    def test_each_marker_refuses_cli_approve(self):
        for key in stages.AGENT_ENV_MARKERS:
            with self.subTest(marker=key), human_env(**{key: "1"}):
                out = self.cli("approve", SLUG, "--by", "user", code=1)
                self.assertIn("에이전트 세션", out)
                self.assertIn(key, out)
                self.assertFalse((self.box.run_dir / "approval.json").exists())

    def test_orca_variables_alone_are_a_human_shell(self):
        orca = {"ORCA_TERMINAL_HANDLE": "term_h", "ORCA_WORKTREE_ID": "w", "ORCA_PANE_KEY": "p", "ORCA_AGENT_HOOK_TOKEN": "t"}
        with human_env(**orca):
            self.assertEqual(stages.agent_session_markers(), [])
            out = self.cli("approve", SLUG, "--by", "user", code=1)   # 계약 검증 실패로 멈춘다
        self.assertNotIn("에이전트 세션", out)

    def test_markers_helper(self):
        self.assertEqual(stages.agent_session_markers({}), [])
        self.assertEqual(stages.agent_session_markers({"CLAUDECODE": "1", "AI_AGENT": " "}), ["CLAUDECODE"])
        self.assertEqual(stages.agent_session_markers({"ORCA_AGENT_LAUNCH_TOKEN": "x", "CLAUDE_CODE_ENTRYPOINT": "cli"}),
                         ["CLAUDE_CODE_ENTRYPOINT", "ORCA_AGENT_LAUNCH_TOKEN"])

    def test_muse_tool_use_id_is_a_marker_and_release_info_is_not(self):
        """2026-10-01 레인 J: 레인 M 조사에서 Muse 세션은 CLAUDECODE·CLAUDE_CODE_ENTRYPOINT·AI_AGENT 가 없었다."""
        self.assertEqual(stages.agent_session_markers({"MUSE_TOOL_USE_ID": "toolu_x"}), ["MUSE_TOOL_USE_ID"])
        self.assertEqual(stages.agent_session_markers({"MUSE_RELEASE_INFO": "x"}), [])


if __name__ == "__main__":
    unittest.main()
