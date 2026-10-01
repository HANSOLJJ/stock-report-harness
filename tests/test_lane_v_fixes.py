# 레인 V 독립 검증 발견 F-1·F-2·F-3·F-4·F-7 의 수정(2026-10-01 레인 H)을 잠그는 테스트
from __future__ import annotations

import inspect
import io
import json
import os
import sys
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import scorecard_cli  # noqa: E402
from scorecard import stages  # noqa: E402
from scorecard.paths import run_paths  # noqa: E402
from scorecard.schema import SchemaError  # noqa: E402
from tests.test_collect_stage import SLUG, Sandbox  # noqa: E402
from tests.test_hooks import TempRootCase, guard, shell, write  # noqa: E402
from tests.test_run_lock import human_env  # noqa: E402

OBS = "ai-scorecard-2026-09-obsreg"
APPROVAL = f"output/{OBS}/approval.json"
BASELINE_TRIGGERS = "scorecard/baseline/v1.5/triggers.json"
INIT = "uv run --frozen python -X utf8 scripts/scorecard_cli.py init {slug} --as-of 2026-09-17 --title x --request y --rule v1.7{force}"
SHELLS = ("Bash", "PowerShell")


def cli(*argv: str, code: int = 0) -> str:
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        got = scorecard_cli.main(list(argv))
    assert got == code, f"{argv} → {got}\n{out.getvalue()}\n{err.getvalue()}"
    return out.getvalue() + err.getvalue()


class HookCaseTable(TempRootCase):
    """F-3·F-7: 보호 경로는 쓰기 대상일 때만 막는다. 읽기 언급은 통과하고, 인터프리터는 언급만 해도 막는다."""

    def kind(self, payload: dict) -> str:
        return guard.protect_sensitive_files(payload, root=self.root).kind

    def test_reads_pass(self):
        for target in (APPROVAL, f"output/{OBS}/run.json", BASELINE_TRIGGERS, "scorecard/history.csv"):
            for cmd in (f"cat {target}", f"cat {target}; echo done", f"rg approved_by {target}", f"git show HEAD:{target}",
                        f"head -5 {target}", f"ls {target}", f"git diff -- {target}", f"grep -n x {target} | head"):
                for tool in SHELLS:
                    with self.subTest(tool=tool, cmd=cmd):
                        self.assertEqual(self.kind(shell(tool, cmd)), "allow")

    def test_writes_blocked(self):
        for target in (APPROVAL, f"output/{OBS}/draft.md", BASELINE_TRIGGERS, "scorecard/rules/v1.7.json"):
            for cmd in (f"echo x > {target}", f"echo x >> {target}", f"rm {target}", f"rm -f {target}", f"cp x.json {target}",
                        f"mv {target} /tmp/x", f"sed -i s/a/b/ {target}", f"echo x | tee {target}", f"cat a.json; touch {target}",
                        f"git checkout HEAD -- {target}", f"git restore {target}", f"chmod 644 {target}", f"truncate -s 0 {target}"):
                for tool in SHELLS:
                    with self.subTest(tool=tool, cmd=cmd):
                        self.assertEqual(self.kind(shell(tool, cmd)), "block")

    def test_interpreter_mentioning_protected_path_blocked(self):
        for target in (APPROVAL, BASELINE_TRIGGERS, f"output/{OBS}"):
            for cmd in (f"python -c \"open('{target}', 'w')\"",
                        f"uv run --frozen python -X utf8 -c \"print(open('{target}').read())\"",
                        f"uv run python scripts/x.py {target}",
                        f"node -e \"require('fs').writeFileSync('{target}', '')\""):
                for tool in SHELLS:
                    with self.subTest(tool=tool, cmd=cmd):
                        self.assertEqual(self.kind(shell(tool, cmd)), "block")

    def test_interpreter_reading_from_pipe_passes(self):
        self.assertEqual(self.kind(shell("Bash", f"cat {APPROVAL} | python -c \"import json,sys; print(json.load(sys.stdin))\"")), "allow")

    def test_baseline_tree_blocked_for_file_tools(self):
        for tool in ("Write", "Edit"):
            for rel in (BASELINE_TRIGGERS, "scorecard/baseline/v1.5/scores.json", "scorecard/baseline/v2/new.json"):
                with self.subTest(tool=tool, rel=rel):
                    self.assertEqual(self.kind(write(rel, tool=tool)), "block")
        self.assertEqual(self.kind(write("scorecard/baselines.md")), "allow")

    def test_windows_paths_and_cd(self):
        self.assertEqual(self.kind(shell("PowerShell", "echo x > scorecard\\baseline\\v1.5\\triggers.json")), "block")
        self.assertEqual(self.kind(shell("PowerShell", "cat scorecard\\baseline\\v1.5\\triggers.json")), "allow")
        self.assertEqual(self.kind(shell("Bash", f"cd output/{OBS} && rm draft.md")), "block")
        self.assertEqual(self.kind(shell("Bash", "cd scorecard && echo x > baseline/v1.5/triggers.json")), "block")
        self.assertEqual(self.kind(shell("Bash", f"cd output/{OBS} && cat draft.md")), "allow")

    def test_quoted_text_is_not_a_redirect(self):
        self.assertEqual(self.kind(shell("Bash", f"git commit -m \"{APPROVAL} > 보호\"")), "allow")

    def test_unbalanced_quotes_fall_back_to_mention(self):
        self.assertEqual(self.kind(shell("Bash", f"cat {APPROVAL} 'unbalanced")), "block")
        self.assertEqual(self.kind(shell("Bash", "echo 'unbalanced")), "allow")

    def test_env_prefix_does_not_hide_the_verb(self):
        self.assertEqual(self.kind(shell("Bash", f"env -u CLAUDECODE X=1 rm {APPROVAL}")), "block")
        self.assertEqual(self.kind(shell("Bash", f"X=1 cat {APPROVAL}")), "allow")


class InitForceHookTest(TempRootCase):
    """F-1: `init … --force` 는 승인 파일이 있는 실행을 가리키면 훅이 막는다. 맨 슬러그도 대상 폴더로 해석한다."""

    def setUp(self) -> None:
        super().setUp()
        self.put(f"output/{OBS}/approval.json", "{}")
        self.put("output/ai-scorecard-2026-10-new/run.json", "{}")

    def kind(self, cmd: str, tool: str = "Bash") -> guard.Decision:
        return guard.protect_sensitive_files(shell(tool, cmd), root=self.root)

    def test_force_on_approved_slug_blocked(self):
        for slug in (OBS, f"output/{OBS}", f"output/{OBS}/"):
            for force in (" --force", " --fo"):
                for tool in SHELLS:
                    with self.subTest(slug=slug, force=force, tool=tool):
                        d = self.kind(INIT.format(slug=slug, force=force), tool)
                        self.assertEqual(d.kind, "block")
                        self.assertIn("승인 기록", d.text)
        self.assertEqual(self.kind(f"uv run python scripts/scorecard_cli.py init --force --as-of 2026-09-17 {OBS}").kind, "block")
        self.assertEqual(self.kind(f"uv run python scripts\\scorecard_cli.py init {OBS} --force", "PowerShell").kind, "block")

    def test_force_on_unapproved_slug_and_plain_init_pass(self):
        for tool in SHELLS:
            with self.subTest(tool=tool):
                self.assertEqual(self.kind(INIT.format(slug="ai-scorecard-2026-10-new", force=" --force"), tool).kind, "allow")
                self.assertEqual(self.kind(INIT.format(slug="ai-scorecard-2026-10-absent", force=" --force"), tool).kind, "allow")
                self.assertEqual(self.kind(INIT.format(slug=OBS, force=""), tool).kind, "allow")


class StageAgentRefusalTest(unittest.TestCase):
    """F-2: 에이전트 거부는 `stages.approve`·`stages.revoke` 본체에 있다. CLI 에는 따로 없다."""

    def test_approve_and_revoke_refuse_each_marker_before_anything(self):
        for key in stages.AGENT_ENV_MARKERS:
            with self.subTest(marker=key), human_env(**{key: "1"}):
                with self.assertRaisesRegex(SchemaError, f"에이전트 세션.*{key}"):
                    stages.approve("ai-scorecard-없는-실행", approved_by="user")
                with self.assertRaisesRegex(SchemaError, f"에이전트 세션.*{key}"):
                    stages.revoke("ai-scorecard-없는-실행", by="user", note="n")

    def test_opt_in_and_human_shell_reach_the_real_checks(self):
        for ctx, kw in ((human_env(CLAUDECODE="1"), {"allow_agent_session": True}), (human_env(), {})):
            with ctx:
                with self.assertRaises(SchemaError) as caught:
                    stages.revoke("ai-scorecard-없는-실행", by="user", note="n", **kw)
                self.assertIn("취소할 승인이 없다", str(caught.exception))

    def test_cli_has_no_separate_refusal(self):
        self.assertFalse(hasattr(scorecard_cli, "_refuse_agent_session"))
        self.assertNotIn("agent_session_markers", inspect.getsource(scorecard_cli.cmd_approve))
        self.assertNotIn("agent_session_markers", inspect.getsource(scorecard_cli.cmd_revoke))
        self.assertNotIn("allow_agent_session", inspect.getsource(scorecard_cli))

    def test_cli_still_refuses_through_the_stage(self):
        with human_env(AI_AGENT="1"):
            self.assertIn("에이전트 세션(AI_AGENT)", cli("approve", "ai-scorecard-없는-실행", "--by", "user", code=1))


class InitForceStageTest(unittest.TestCase):
    """F-1: 승인 파일이 있는 실행을 --force 로 덮어쓰면 에이전트 세션은 거부하고, 사람 세션은 경고하고 진행한다."""

    ARGS = ("--as-of", "2026-09-29", "--title", "근거 계층 시험", "--request", "근거 계층 시험", "--companies", "nvidia", "--rule", "v1.8")

    def setUp(self) -> None:
        self.box = Sandbox(("nvidia",))
        self.addCleanup(self.box.close)
        self.approval = self.box.run_dir / "approval.json"
        self.approval.write_text("{}", encoding="utf-8")
        self.run_bytes = (self.box.run_dir / "run.json").read_bytes()

    def test_agent_session_refused_and_nothing_changes(self):
        with human_env(CLAUDECODE="1", SCORECARD_AGENT="me"):
            with self.assertRaisesRegex(SchemaError, "승인 기록이 지워진다"):
                stages.init_run(SLUG, as_of="2026-09-29", title="t", request="r", companies=["nvidia"], rule_version="v1.8", force=True)
            self.assertIn("에이전트 세션", cli("init", SLUG, *self.ARGS, "--force", code=1))
        self.assertTrue(self.approval.exists())
        self.assertEqual((self.box.run_dir / "run.json").read_bytes(), self.run_bytes)

    def test_human_session_warns_and_overwrites(self):
        with human_env(SCORECARD_AGENT="me"):
            out = cli("init", SLUG, *self.ARGS, "--force")
        self.assertIn("[경고]", out)
        self.assertIn("승인 기록이 지워", out)
        self.assertFalse(self.approval.exists())

    def test_force_without_approval_has_no_warning_in_agent_session(self):
        self.approval.unlink()
        with human_env(CLAUDECODE="1", SCORECARD_AGENT="me"):
            out = cli("init", SLUG, *self.ARGS, "--force")
        self.assertNotIn("[경고]", out)
        self.assertIn("다음: uv run --frozen python -X utf8 scripts/scorecard_cli.py collect", out)


class GuidanceTest(unittest.TestCase):
    """F-4: 에이전트가 읽는 안내에 approve 실행이 없고, plan 흐름에 collect 가 있으며, 안내는 uv run 형식이다."""

    def test_draft_next_step_is_awaiting_user_report(self):
        src = inspect.getsource(scorecard_cli.cmd_draft)
        self.assertIn("승인 대기 보고", src)
        self.assertNotIn("approve", src)

    def test_every_guidance_uses_uv_run(self):
        src = inspect.getsource(scorecard_cli)
        self.assertNotIn("python scripts/", src)
        self.assertIn("uv run --frozen python -X utf8 scripts/scorecard_cli.py init <slug>", scorecard_cli.__doc__)

    def test_plan_flow_includes_collect(self):
        box = Sandbox(("nvidia",))
        self.addCleanup(box.close)
        plan = run_paths(SLUG).plan.read_text(encoding="utf-8")
        self.assertIn("- 흐름: plan → collect → research → calculate → draft → review → awaiting_user → build", plan)


if __name__ == "__main__":
    unittest.main()
