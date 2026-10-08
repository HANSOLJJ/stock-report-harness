# 규칙 v2.0 ③ 지표 단계 e(없음)에서 지연 조항의 실패는 받고 통과·부분은 막는 것을 잠근다(2026-10-08 Apple 재판단)
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard.calc_qual import compute_f3  # noqa: E402
from scorecard.inputs import JudgmentLookup  # noqa: E402
from scorecard.rules import load_rules  # noqa: E402
from scorecard.schema import SchemaError, _validate_judgment_inputs_for_rules  # noqa: E402

RULES = load_rules("v2.0")
COMPANY = {"company_id": "apple", "type": "소비자", "listed": True}


def judgment(acc: str, tier: str = "e") -> dict:
    return {"judgment_id": "apple.F3", "company_id": "apple", "factor": "F3", "kind": "criteria", "score": None,
            "inputs": {"imitation": "fail", "revenue_model": "pass", "acceleration": acc, "door_closed": "fail",
                       "acceleration_tier": tier},
            "evidence": ["판정"], "reviewer": "t", "reviewed_at": "2026-10-08", "status": "new"}


class TierEDelayTest(unittest.TestCase):
    def check(self, acc: str) -> None:
        _validate_judgment_inputs_for_rules("criteria", judgment(acc)["inputs"], RULES.payload["factors"]["F3"], "t")

    def test_schema_accepts_fail_and_unknown_but_not_pass_or_partial(self):
        self.check("unknown")
        self.check("fail")
        for acc in ("pass", "partial"):
            with self.assertRaisesRegex(SchemaError, "통과·부분으로 판정할 수 없다"):
                self.check(acc)

    def test_engine_scores_delay_fail_and_leaves_unknown_unscored(self):
        fail = compute_f3(COMPANY, JudgmentLookup([judgment("fail")]), RULES)
        self.assertEqual((fail["status"], fail["score"]), ("ok", 2))          # 통과점 1(수익모델) → 2
        self.assertNotIn("acceleration_input", fail["calc"])                   # 입력을 낮추지 않았다
        unknown = compute_f3(COMPANY, JudgmentLookup([judgment("unknown")]), RULES)
        self.assertEqual((unknown["status"], unknown["score"]), ("needs_judgment", None))
        partial = compute_f3(COMPANY, JudgmentLookup([judgment("partial")]), RULES)
        self.assertEqual((partial["status"], partial["calc"]["acceleration_input"]), ("needs_judgment", "partial"))


if __name__ == "__main__":
    unittest.main()
