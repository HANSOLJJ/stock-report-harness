# 승인 전 실행의 기준일을 뒤로 옮기는 set-as-of(stages.move_as_of)를 임시 샌드박스에서 잠근다
from __future__ import annotations

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
os.environ["SCORECARD_DOTENV"] = ""

import scorecard_cli  # noqa: E402
from report_contract_lib import frontmatter_value, read_markdown  # noqa: E402
from scorecard import stages  # noqa: E402
from scorecard.paths import run_paths  # noqa: E402
from scorecard.schema import SchemaError, load_json_strict  # noqa: E402
from tests.test_collect_stage import SLUG, Sandbox  # noqa: E402

REASON = "2026-10-14 투자자 설명회 보도를 근거로 넣는다"


class MoveAsOfTest(unittest.TestCase):
    def setUp(self) -> None:
        self.box = Sandbox(as_of="2026-09-29")
        self.addCleanup(self.box.close)
        self.run_path = self.box.run_dir / "run.json"
        self.plan_path = run_paths(SLUG).plan

    def _baseline_line(self) -> str:
        return stages._PLAN_BASELINE_RE.search(read_markdown(self.plan_path)[1]).group(0)

    def test_moves_as_of_and_cutoff_together_and_rerenders_plan(self) -> None:
        baseline = self._baseline_line()
        out = stages.move_as_of(SLUG, "2026-10-02", reason=REASON)
        run = load_json_strict(self.run_path)
        self.assertEqual(run["as_of"], "2026-10-02")
        self.assertEqual(run["info_cutoff"], "2026-10-02")
        self.assertEqual(run["price_as_of"], "2026-09-29")
        self.assertEqual(run["assumptions"][-1], f"분석 기준일은 2026-10-02 이다({REASON})")
        self.assertEqual(out["moved"], {"as_of": ["2026-09-29", "2026-10-02"], "info_cutoff": ["2026-09-29", "2026-10-02"]})
        fm, body, _, _ = read_markdown(self.plan_path)
        self.assertEqual(frontmatter_value(fm, "as_of"), "2026-10-02")
        self.assertEqual(frontmatter_value(fm, "info_cutoff"), "2026-10-02")
        self.assertEqual(frontmatter_value(fm, "request"), "근거 계층 시험")
        self.assertIn("분석 기준일 `as_of` 2026-10-02 · 가격 기준일 2026-09-29 · 정보 컷오프 2026-10-02", body)
        self.assertNotIn("2026-09-29 · 정보 컷오프 2026-09-29", body)
        self.assertEqual(self._baseline_line(), baseline)

    def test_cli_takes_the_lock_and_prints_the_move(self) -> None:
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = scorecard_cli.main(["set-as-of", SLUG, "--as-of", "2026-10-02", "--reason", REASON])
        self.assertEqual(code, 0, err.getvalue())
        self.assertIn("as_of: 2026-09-29 → 2026-10-02", out.getvalue())
        self.assertEqual(json.loads((self.box.run_dir / ".lock").read_text(encoding="utf-8"))["stage"], "set-as-of")

    def test_collect_window_follows_new_cutoff(self) -> None:
        stages.move_as_of(SLUG, "2026-10-02", reason=REASON)
        out = stages.collect(SLUG, kinds=("news",), since="2026-09-30", dry_run=True, now="2026-10-02T00:00:00Z")
        self.assertEqual(out["window"], {"since": "2026-09-30", "until": "2026-10-02"})

    def test_rejects_same_or_earlier_date_and_leaves_files(self) -> None:
        before = (self.run_path.read_bytes(), self.plan_path.read_bytes())
        for day in ("2026-09-29", "2026-09-01"):
            with self.subTest(day=day), self.assertRaisesRegex(SchemaError, "뒤로만"):
                stages.move_as_of(SLUG, day, reason=REASON)
        with self.assertRaisesRegex(SchemaError, "YYYY-MM-DD"):
            stages.move_as_of(SLUG, "2026-10-32", reason=REASON)
        with self.assertRaisesRegex(SchemaError, "--reason"):
            stages.move_as_of(SLUG, "2026-10-02", reason="  ")
        self.assertEqual((self.run_path.read_bytes(), self.plan_path.read_bytes()), before)

    def test_keeps_separately_recorded_cutoff(self) -> None:
        run = load_json_strict(self.run_path)
        run["info_cutoff"] = "2026-09-20"
        self.run_path.write_text(json.dumps(run, ensure_ascii=False, indent=2), encoding="utf-8")
        out = stages.move_as_of(SLUG, "2026-10-02", reason=REASON)
        self.assertEqual(load_json_strict(self.run_path)["info_cutoff"], "2026-09-20")
        self.assertNotIn("info_cutoff", out["moved"])

    def test_agent_session_cannot_move_approved_run(self) -> None:
        (self.box.run_dir / "approval.json").write_text("{}", encoding="utf-8")
        before = self.run_path.read_bytes()
        with mock.patch.object(stages, "agent_session_markers", return_value=["CLAUDECODE"]), \
                mock.patch.object(stages, "approval_is_valid", return_value=True), \
                self.assertRaisesRegex(SchemaError, "기준일 변경"):
            stages.move_as_of(SLUG, "2026-10-02", reason=REASON)
        self.assertEqual(self.run_path.read_bytes(), before)

    def test_invalid_approval_does_not_block(self) -> None:
        (self.box.run_dir / "approval.json").write_text("{}", encoding="utf-8")
        with mock.patch.object(stages, "agent_session_markers", return_value=["CLAUDECODE"]), \
                mock.patch.object(stages, "approval_is_valid", return_value=False):
            stages.move_as_of(SLUG, "2026-10-02", reason=REASON)
        self.assertEqual(load_json_strict(self.run_path)["as_of"], "2026-10-02")

    def test_rejects_run_whose_rule_file_changed(self) -> None:
        run = load_json_strict(self.run_path)
        run["rule_hash"] = "0" * 64
        self.run_path.write_text(json.dumps(run, ensure_ascii=False, indent=2), encoding="utf-8")
        with self.assertRaisesRegex(SchemaError, "규칙 파일"):
            stages.move_as_of(SLUG, "2026-10-02", reason=REASON)


if __name__ == "__main__":
    unittest.main()
