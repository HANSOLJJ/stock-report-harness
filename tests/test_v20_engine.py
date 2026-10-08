# 규칙 v2.0 엔진: ② 독립 측정 없는 성능 도약과 세대 격차 개월 임계, ③ 지표 단계 상한, ②·⑦ 이어받은 score 판단의 미완료 처리를 잠근다
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard.calc_qual import compute_f2, compute_f3, compute_f7  # noqa: E402
from scorecard.inputs import JudgmentLookup  # noqa: E402
from scorecard.rules import load_rules  # noqa: E402
from tests.test_rules_v20 import company  # noqa: E402

V20 = load_rules("v2.0")
V19 = load_rules("v1.9")
C03 = {"id": "C-03", "choice": "paths_with_generation_gap_5", "rationale": "시험", "decided_by": "tester", "decided_at": "2026-10-08"}
RUN = {"run_id": "t", "rule_version": "v2.0", "decisions": [C03]}


def judgment(factor: str, kind: str, inputs: dict | None = None, *, score=None, status: str = "new") -> dict:
    return {"judgment_id": f"acme.{factor}", "company_id": "acme", "factor": factor, "kind": kind, "score": score,
            "inputs": inputs or {}, "evidence": ["시험"], "reviewer": "tester", "reviewed_at": "2026-10-08", "status": status,
            "carried_from": "run:prior" if status == "carried" else None}


def paths(**kw) -> dict:
    base = {"performance_leap": "pass", "paradigm_adaptation": "pass", "standard_capture": "fail", "top_rank": "unknown",
            "generation_gap": "yes", "leap_independent": "yes", "generation_gap_months": 12}
    base.update(kw)
    return base


class F2IndependenceTest(unittest.TestCase):
    def f2(self, inputs: dict, ctype: str = "업무", rules=V20) -> dict:
        return compute_f2(company(ctype=ctype), JudgmentLookup([judgment("F2", "paths", inputs)]), rules, RUN)

    def test_vendor_only_leap_counts_as_partial(self):
        r = self.f2(paths(leap_independent="no"))
        # 성능 도약이 부분으로 내려가 경로는 패러다임 하나 → 3. 세대 격차 yes 여도 5 가 아니다.
        self.assertEqual((r["score"], r["status"], r["calc"]["passed"], r["calc"]["performance_leap_used"]), (3, "ok", 1, "partial"))
        self.assertTrue(any("독립 측정" in w for w in r["warnings"]))
        self.assertEqual(self.f2(paths(leap_independent="unknown"))["score"], 3)

    def test_independent_leap_with_gap_is_five(self):
        r = self.f2(paths())
        self.assertEqual((r["score"], r["calc"]["generation_gap_months_threshold"], r["calc"]["generation_gap_months"]), (5, 6, 12))

    def test_model_threshold_is_six_months(self):
        r = self.f2(paths(generation_gap_months=5))
        self.assertEqual((r["score"], r["calc"]["passed"]), (4, 2))   # 경로 2개 → 4
        self.assertTrue(any("임계 6개월" in w for w in r["warnings"]))
        self.assertEqual(self.f2(paths(generation_gap_months=6))["score"], 5)

    def test_component_threshold_is_twelve_months(self):
        r = self.f2(paths(generation_gap_months=10), ctype="부품")
        self.assertEqual((r["score"], r["calc"]["generation_gap_months_threshold"]), (4, 12))
        self.assertEqual(self.f2(paths(generation_gap_months=12), ctype="부품")["score"], 5)

    def test_missing_months_is_not_guessed(self):
        inputs = paths()
        del inputs["generation_gap_months"]
        r = self.f2(inputs)
        self.assertEqual((r["score"], r["status"]), (None, "needs_judgment"))

    def test_v19_ignores_new_keys(self):
        """규칙 키가 없으면 지금 경로 그대로다 — 독립 측정·개월 수를 보지 않는다."""
        r = self.f2(paths(leap_independent="no", generation_gap_months=1), rules=V19)
        self.assertEqual(r["score"], 5)
        self.assertNotIn("performance_leap_used", r["calc"])
        self.assertNotIn("generation_gap_months_threshold", r["calc"])

    def test_carried_score_needs_judgment_in_v20_only(self):
        j = judgment("F2", "score", score=5, status="carried")
        r = compute_f2(company(), JudgmentLookup([j]), V20, RUN)
        self.assertEqual((r["score"], r["status"]), (None, "needs_judgment"))
        self.assertIn("이어받은 점수는 쓰지 않는다", r["pending"]["message"])
        r = compute_f2(company(), JudgmentLookup([j]), V19, RUN)
        self.assertEqual((r["score"], r["status"]), (5, "carried_score"))


class F3TierTest(unittest.TestCase):
    def f3(self, inputs: dict, rules=V20) -> dict:
        return compute_f3(company(), JudgmentLookup([judgment("F3", "criteria", inputs)]), rules)

    BASE = {"imitation": "fail", "revenue_model": "partial", "acceleration": "pass", "door_closed": "unknown"}

    def test_tier_c_pass_is_computed_as_partial(self):
        r = self.f3({**self.BASE, "acceleration_tier": "c", "acceleration_growth_rates": [0.2, 0.3]})
        # pass 면 1.5 → 3 이지만 c 단계 상한으로 partial → 1.0 → 2
        self.assertEqual((r["score"], r["calc"]["pass_points"], r["calc"]["criteria"]["acceleration"]), (2, 1.0, "partial"))
        self.assertEqual((r["calc"]["acceleration_tier"], r["calc"]["acceleration_input"]), ("c", "pass"))
        self.assertEqual(r["calc"]["acceleration_growth_rates"], [0.2, 0.3])
        self.assertTrue(any("최대 partial" in w for w in r["warnings"]))

    def test_tier_b_pass_counts(self):
        r = self.f3({**self.BASE, "acceleration_tier": "b", "acceleration_growth_rates": [0.2, 0.3]})
        self.assertEqual((r["score"], r["calc"]["pass_points"]), (3, 1.5))
        self.assertNotIn("acceleration_input", r["calc"])

    def test_tier_e_makes_no_score(self):
        r = self.f3({**self.BASE, "acceleration_tier": "e"})
        self.assertEqual((r["score"], r["status"]), (None, "needs_judgment"))

    def test_v19_calc_unchanged(self):
        r = self.f3(self.BASE, rules=V19)
        self.assertEqual(set(r["calc"]), {"criteria", "door_closed", "pass_points", "ladder_note"})
        self.assertEqual(r["score"], 3)


class F7KindTest(unittest.TestCase):
    def test_carried_score_needs_judgment_in_v20(self):
        j = judgment("F7", "score", score=-2, status="carried")
        r = compute_f7(company(), JudgmentLookup([j]), V20)
        self.assertEqual((r["score"], r["status"], r["basis"]), (None, "needs_judgment", "matrix"))
        self.assertIn("이어받은 점수는 쓰지 않는다", r["pending"]["message"])
        r = compute_f7(company(), JudgmentLookup([j]), V19)
        self.assertEqual((r["score"], r["status"]), (-2, "carried_score"))

    def test_matrix_still_computes(self):
        j = judgment("F7", "matrix", {"funding_dependent_share": "large", "own_money_returns": "yes"})
        self.assertEqual(compute_f7(company(), JudgmentLookup([j]), V20)["score"], -2)


if __name__ == "__main__":
    unittest.main()
