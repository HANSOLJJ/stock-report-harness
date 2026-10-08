# 규칙 v2.0 ② 세 경로 통과(세대 격차 없음)가 두 경로와 같은 4 로 계산되는 것을 잠근다(2026-10-08 Anthropic·NVIDIA 재판단)
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard.calc_qual import compute_f2  # noqa: E402
from scorecard.inputs import JudgmentLookup  # noqa: E402
from scorecard.rules import load_rules  # noqa: E402

RULES = load_rules("v2.0")
RUN = {"run_id": "t", "rule_version": "v2.0", "decisions": [{"id": "C-03", "choice": "paths_with_generation_gap_5"}]}
COMPANY = {"company_id": "anthropic", "type": "거래", "listed": False}


def judgment(**inputs) -> dict:
    base = {"performance_leap": "pass", "paradigm_adaptation": "pass", "standard_capture": "pass", "top_rank": "no",
            "generation_gap": "no", "leap_independent": "yes"}
    base.update(inputs)
    return {"judgment_id": "anthropic.F2", "company_id": "anthropic", "factor": "F2", "kind": "paths", "score": None,
            "inputs": base, "evidence": ["판정"], "reviewer": "t", "reviewed_at": "2026-10-08", "status": "new"}


class ThreePathsTest(unittest.TestCase):
    def test_three_passes_without_gap_score_four(self):
        r = compute_f2(COMPANY, JudgmentLookup([judgment()]), RULES, RUN)
        self.assertEqual((r["status"], r["score"], r["calc"]["passed"], r["calc"]["mapping_capped_from"]), ("ok", 4, 3, 3))
        self.assertTrue(any("세 경로" in w or "경로 3개" in w for w in r["warnings"]), r["warnings"])

    def test_two_passes_still_four_and_gap_still_five(self):
        two = compute_f2(COMPANY, JudgmentLookup([judgment(standard_capture="fail")]), RULES, RUN)
        self.assertEqual((two["status"], two["score"]), ("ok", 4))
        five = compute_f2(COMPANY, JudgmentLookup([judgment(generation_gap="yes", generation_gap_months=7)]), RULES, RUN)
        self.assertEqual((five["status"], five["score"]), ("ok", 5))


if __name__ == "__main__":
    unittest.main()
