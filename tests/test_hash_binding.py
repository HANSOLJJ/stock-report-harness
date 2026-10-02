# 승인·입력 해시에 sources·evidence·triggers 를 결속하되 기존 두 실행(승인 6키)의 승인·재계산 결과가 그대로인지 잠근다
from __future__ import annotations

import io
import re
import shutil
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard import compare, engine, render_html, stages, validate  # noqa: E402
from scorecard.schema import SchemaError, approval_id_for, load_json_strict, validate_approval  # noqa: E402
from scorecard.stages import approval_mismatches, current_hashes  # noqa: E402

BASELINE = "ai-scorecard-2026-09-baseline"
OBSREG = "ai-scorecard-2026-09-obsreg"
SIX = ["rules", "observations", "judgments", "run", "results", "draft"]


class ExistingRunsTest(unittest.TestCase):
    def test_both_runs_stay_approved(self):
        for slug in (BASELINE, OBSREG):
            with self.subTest(slug=slug):
                approval = load_json_strict(engine.run_dir(slug) / "approval.json")
                self.assertEqual(sorted(approval["hashes"]), sorted(SIX))   # 옛 승인은 6키다
                self.assertTrue(stages.status(slug)["approval_valid"])
                self.assertEqual(approval_mismatches(approval["hashes"], current_hashes(slug)), [])
                self.assertTrue(compare.approval_state(slug)["valid"])

    def test_current_hashes_add_sources_only(self):
        for slug in (BASELINE, OBSREG):
            with self.subTest(slug=slug):
                self.assertEqual(sorted(current_hashes(slug)), sorted(SIX + ["sources"]))

    def test_recompute_values_unchanged(self):
        self.assertEqual(engine.recompute_matches(BASELINE), (
            False,
            "0942c342f010781ea41f2cec51a5082c5f5f58cdfe76078bb7c3e5b29bbffec0",
            "200d7b01afc3cf39f95bd776bfcc930499fbe57f3f110aa6140b8563c00f813a",
        ))
        ok, stored, fresh = engine.recompute_matches(OBSREG)
        self.assertTrue(ok)
        self.assertEqual(stored, "4a3f6c05b206ef81f370ac7765a1a948fe1e9cf6d1999c142bac4f124e04910b")

    def test_input_hashes_have_no_evidence_keys(self):
        for slug in (BASELINE, OBSREG):
            with self.subTest(slug=slug):
                ctx = engine.load_context(slug)
                self.assertEqual(sorted(ctx.hashes), ["judgments", "observations", "rules", "run", "sources"])
                self.assertEqual(engine.load_results(slug)["input_hashes"], ctx.hashes)


class ApprovalRuleTest(unittest.TestCase):
    CUR = {**{k: k * 4 for k in SIX}, "sources": "s"}

    def test_legacy_approval_ignores_sources(self):
        self.assertEqual(approval_mismatches({k: k * 4 for k in SIX}, self.CUR), [])

    def test_sources_compared_when_approved(self):
        self.assertEqual(approval_mismatches({**{k: k * 4 for k in SIX}, "sources": "old"}, self.CUR), ["sources"])

    def test_new_evidence_after_approval_invalidates(self):
        cur = {**self.CUR, "evidence": "e"}
        self.assertEqual(approval_mismatches({k: k * 4 for k in SIX}, cur), ["evidence"])
        self.assertEqual(approval_mismatches({**{k: k * 4 for k in SIX}, "evidence": "e"}, cur), [])
        self.assertEqual(approval_mismatches({**{k: k * 4 for k in SIX}, "evidence": "old"}, cur), ["evidence"])
        # 승인 뒤 파일을 지워도 무효다.
        self.assertEqual(approval_mismatches({**{k: k * 4 for k in SIX}, "triggers": "t"}, self.CUR), ["triggers"])

    def test_missing_required_key_is_never_valid(self):
        self.assertEqual(approval_mismatches({}, self.CUR), sorted(SIX))
        self.assertEqual(approval_mismatches({k: k * 4 for k in SIX if k != "draft"}, self.CUR), ["draft"])

    def test_validate_approval_optional_keys(self):
        base = {"schema": "scorecard.approval/1", "run_id": "r", "approval_id": approval_id_for("r", {k: "h" for k in SIX}),
                "approved_by": "u", "approved_at": "2026-09-30", "hashes": {k: "h" for k in SIX}}
        validate_approval(base, "r")
        validate_approval({**base, "hashes": {**base["hashes"], "sources": "s", "evidence": "e", "triggers": "t"}}, "r")
        with self.assertRaises(SchemaError):
            validate_approval({**base, "hashes": {**base["hashes"], "citations": "c"}}, "r")
        with self.assertRaises(SchemaError):
            validate_approval({**base, "hashes": {k: "h" for k in SIX[:-1]}}, "r")


class NoDirectComparisonTest(unittest.TestCase):
    """승인 해시를 dict 등호로 직접 비교하는 줄이 scripts/ 에 없다. 비교는 approval_mismatches 한 곳이다."""

    PATTERN = re.compile(r"hashes[\"'\])]*\)?\s*[!=]=\s*current_hashes\(|current_hashes\([^)]*\)\s*[!=]=")

    def test_pattern_catches_the_old_forms(self):
        for line in ('if approval["hashes"] != current_hashes(slug):',
                     'out["approval_valid"] = approval.get("hashes") == current_hashes(slug)',
                     "if current_hashes(slug) != approval['hashes']:"):
            with self.subTest(line=line):
                self.assertRegex(line, self.PATTERN)

    def test_no_direct_comparison_in_scripts(self):
        hits = []
        for path in sorted((ROOT / "scripts").rglob("*.py")):
            for no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if self.PATTERN.search(line):
                    hits.append(f"{path.relative_to(ROOT).as_posix()}:{no}: {line.strip()}")
        self.assertEqual(hits, [])


class ExistingRunsBuildTest(unittest.TestCase):
    """기존 두 실행을 임시 사본으로 빌드해도 awaiting_user 로 멈추지 않는다. 정본 폴더와 history.csv 는 건드리지 않는다."""

    def setUp(self) -> None:
        self.dir = Path(tempfile.mkdtemp())
        self.saved = (engine.OUTPUT_DIR, render_html.HISTORY_CSV, validate.HISTORY_CSV)
        output = self.dir / "output"
        for slug in (BASELINE, OBSREG):
            shutil.copytree(self.saved[0] / slug, output / slug)
        history = self.dir / "history.csv"
        shutil.copyfile(self.saved[1], history)
        engine.OUTPUT_DIR = output
        render_html.HISTORY_CSV = validate.HISTORY_CSV = history
        self.addCleanup(self._restore)

    def _restore(self) -> None:
        engine.OUTPUT_DIR, render_html.HISTORY_CSV, validate.HISTORY_CSV = self.saved
        shutil.rmtree(self.dir, ignore_errors=True)

    def test_obsreg_builds(self):
        lock = engine.OUTPUT_DIR / OBSREG / ".lock"
        lock.write_text('{"owner": "term_old", "started_utc": "2026-10-01T00:00:00Z", "stage": "review-template"}', encoding="utf-8")
        buf = io.StringIO()
        try:
            with redirect_stdout(buf):
                html, _extra, _none = render_html.build_scorecard(OBSREG)
        except SystemExit as exc:
            self.fail(f"{OBSREG} 빌드가 멈췄다: {exc}\n{buf.getvalue()[-2000:]}")
        self.assertTrue(html.is_file())
        self.assertTrue(html.is_relative_to(self.dir))
        self.assertIn("ok - approval hashes match current inputs", buf.getvalue())
        self.assertFalse(lock.exists())   # 2026-10-02 빌드가 끝나면 잠금을 지운다

    def test_baseline_stops_only_on_its_known_recompute_mismatch(self):
        """baseline 은 레인 E 이전부터 재계산 해시가 저장값과 다르다(0942c342… ≠ 200d7b01…). 그 사유로만 멈추고
        승인 검사는 통과한다. awaiting_user 로 멈추지 않는다."""
        lock = engine.OUTPUT_DIR / BASELINE / ".lock"
        lock.write_text('{"owner": "term_old"}', encoding="utf-8")
        buf = io.StringIO()
        with redirect_stdout(buf), self.assertRaises(SystemExit) as caught:
            render_html.build_scorecard(BASELINE)
        self.assertTrue(lock.exists())   # 실패한 빌드는 잠금을 남긴다
        out = buf.getvalue()
        self.assertNotIn("awaiting_user", str(caught.exception))
        self.assertIn("ok - approval hashes match current inputs", out)
        errors = [line for line in out.splitlines() if line.strip().startswith("error -")]
        self.assertEqual(errors, ["  error - 재계산 결과가 저장된 results.json 과 다름 (결정론 위반 또는 규칙 변경)"])


if __name__ == "__main__":
    unittest.main()
