# FIX-52 코드 결함 — C-03 확정 경로, run.json 결정 누락, C-12 run 전달, F9 경로 문자열의 정책 값 사용을 고정한다
"""이 테스트가 지키는 계약 넷.

1. **확정된 C-03 선택을 엔진이 실행할 수 있다.** 폐기 선택과 삭제된 키를 요구하지 않는다. 승계 F2 는 그대로다.
2. **규칙에서 resolved 된 결정은 run.decisions 에도 있다.** decision_choice 는 run 만 읽는다.
3. **C-12 선택을 실제로 읽는다.** 구현된 경로가 아닌 선택이면 needs_rule_decision 이다.
4. **F9 경로 문자열은 정책 값을 읽는다.** -5 가 박혀 -4 결과와 모순되지 않는다.
"""
from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard.calc_f6 import compute_f6  # noqa: E402
from scorecard.calc_qual import compute_f2  # noqa: E402
from scorecard.inputs import JudgmentLookup, ObsLookup  # noqa: E402
from scorecard.rules import decision_choice, load_rules  # noqa: E402

RULES = load_rules("v1.7")
RUN_DIR = ROOT / "output" / "ai-scorecard-2026-09-obsreg"


def company(listed=True):
    return {"company_id": "acme", "display_name": "Acme", "aliases": [], "type": "업무", "listed": listed,
            "ticker": "ACME" if listed else None, "exchange": "NASDAQ" if listed else None,
            "share_basis": "common" if listed else "private", "adr_ratio": None,
            "reporting_currency": "USD", "scope": "test"}


def run_with(**choices):
    return {"run_id": "t", "as_of": "2026-09-02", "rule_version": "v1.7",
            "decisions": [{"id": k.replace("_", "-"), "choice": v, "rationale": "t", "decided_by": "t",
                           "decided_at": "2026-09-02"} for k, v in choices.items()]}


def paths_judgment(**inputs):
    base = {"performance_leap": "pass", "paradigm_adaptation": "fail", "standard_capture": "fail", "top_rank": "no"}
    base.update(inputs)
    return {"judgment_id": "acme.F2", "company_id": "acme", "factor": "F2", "kind": "paths", "score": None,
            "inputs": base, "evidence": ["t"], "reviewer": "t", "reviewed_at": "2026-09-15", "status": "new"}


class C03ConfirmedPathTest(unittest.TestCase):
    RUN = run_with(C_03="paths_with_generation_gap_5")

    def f2(self, **inputs):
        return compute_f2(company(), JudgmentLookup([paths_judgment(**inputs)]), RULES, self.RUN)

    def test_path_counts_map_to_two_three_four(self):
        self.assertEqual(self.f2(performance_leap="fail")["score"], 2)
        self.assertEqual(self.f2(generation_gap="no")["score"], 3)
        self.assertEqual(self.f2(generation_gap="no", standard_capture="pass")["score"], 4)

    def test_generation_gap_gives_five_not_top_rank(self):
        """**5점 칸은 AA 종합 1위가 아니다.** top_rank=yes 만으로는 5 가 아니고 세대 격차가 필요하다."""
        self.assertEqual(self.f2(generation_gap="yes")["score"], 5)
        self.assertEqual(self.f2(generation_gap="no", top_rank="yes")["score"], 3)

    def test_missing_generation_gap_is_not_guessed(self):
        r = self.f2()
        self.assertEqual(r["status"], "needs_judgment")
        self.assertIn("세대 격차", r["pending"]["message"])

    def test_carried_f2_stays_carried(self):
        carried = {**paths_judgment(), "kind": "score", "score": 5, "inputs": {}, "status": "carried",
                   "carried_from": "baseline:v1.5"}
        r = compute_f2(company(), JudgmentLookup([carried]), RULES, self.RUN)
        self.assertEqual((r["score"], r["status"]), (5, "carried_score"))
        self.assertIn("C-03 확정", r["warnings"][0])

    def test_run_f2_unchanged_all_carried(self):
        res = json.loads((RUN_DIR / "results.json").read_text(encoding="utf-8"))
        for c in res["companies"]:
            with self.subTest(cid=c["company_id"]):
                self.assertEqual(c["factors"]["F2"]["status"], "carried_score")


class RunDecisionsTest(unittest.TestCase):
    def test_resolved_rule_decisions_are_in_run(self):
        run = json.loads((RUN_DIR / "run.json").read_text(encoding="utf-8"))
        for d in RULES.payload["decisions"]:
            if d["status"] == "resolved" and d.get("chosen"):
                with self.subTest(did=d["id"]):
                    self.assertEqual(decision_choice(run, RULES, d["id"]), d["chosen"])

    def test_c13_rationale_says_bands_only(self):
        run = json.loads((RUN_DIR / "run.json").read_text(encoding="utf-8"))
        c13 = next(d for d in run["decisions"] if d["id"] == "C-13")
        self.assertIn("bands 모드에서만 효력", c13["rationale"])


class C12ReadsRunTest(unittest.TestCase):
    def obs(self):
        items = []
        for metric, value, kind in (("ps_ratio", 30.0, "estimate"), ("arr", 65e9, "run_rate"),
                                    ("arr_prior", 47e9, "run_rate"), ("cumulative_raised", 125e9, "actual"),
                                    ("post_money_valuation", 965e9, "actual")):
            items.append({"observation_id": f"acme.{metric}.t", "company_id": "acme", "metric": metric,
                          "value": value, "unit": "ratio" if metric == "ps_ratio" else "USD",
                          "as_of": "2026-09-02", "kind": kind, "source_id": "SRC-t",
                          "status": "legacy_unverified", "period": None, "basis": None, "raw": None, "note": None})
        return ObsLookup(items)

    def test_implemented_choice_scores(self):
        r = compute_f6(company(listed=False), self.obs(), JudgmentLookup([]), RULES,
                       run_with(C_12="p2_with_capped_promotion"))
        self.assertEqual((r["status"], r["score"]), ("ok", -4))
        self.assertEqual(r["calc"]["c12_choice"], "p2_with_capped_promotion")

    def test_other_choice_needs_rule_decision(self):
        r = compute_f6(company(listed=False), self.obs(), JudgmentLookup([]), RULES,
                       run_with(C_12="manual_with_rationale"))
        self.assertEqual(r["status"], "needs_rule_decision")
        self.assertEqual(r["pending"]["decision_id"], "C-12")

    def test_missing_choice_is_not_defaulted(self):
        r = compute_f6(company(listed=False), self.obs(), JudgmentLookup([]), RULES, run_with())
        self.assertEqual(r["status"], "needs_rule_decision")


class F9StringsReadPolicyTest(unittest.TestCase):
    def test_no_hardcoded_minus_five_in_results(self):
        res = json.loads((RUN_DIR / "results.json").read_text(encoding="utf-8"))
        text = json.dumps([c["factors"]["F9"] for c in res["companies"]], ensure_ascii=False)
        self.assertNotIn("→ -5", text)
        self.assertNotIn("하한(-5)", text)

    def test_source_has_no_literal_band_numbers(self):
        src = (ROOT / "scripts" / "scorecard" / "calc_f9.py").read_text(encoding="utf-8")
        for literal in ('"BEP 후퇴 → -5"', "하한(-5)", "최소 -4\"", "상한 -3)"):
            with self.subTest(literal=literal):
                self.assertNotIn(literal, src)


if __name__ == "__main__":
    unittest.main()
