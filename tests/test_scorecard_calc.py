# 설계 지침 12.1 계산 검증(T-01~T-12)을 표준 unittest 로 고정한 계산기 테스트
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard.aggregate import rank_companies, summarize_company  # noqa: E402
from scorecard.calc_f6 import compute_f6  # noqa: E402
from scorecard.calc_f9 import compute_f9  # noqa: E402
from scorecard.calc_qual import compute_f2, compute_f3, compute_f5, compute_f7, compute_manual  # noqa: E402
from scorecard.inputs import JudgmentLookup, ObsLookup  # noqa: E402
from scorecard.rules import load_rules  # noqa: E402
from scorecard.schema import SchemaError, validate_judgments  # noqa: E402

RULES = load_rules("v1.5")


def company(cid: str = "acme", listed: bool = True, ctype: str = "업무") -> dict:
    return {
        "company_id": cid,
        "display_name": cid.title(),
        "aliases": [],
        "type": ctype,
        "listed": listed,
        "ticker": "ACME" if listed else None,
        "exchange": "NASDAQ" if listed else None,
        "share_basis": "common" if listed else "private",
        "adr_ratio": None,
        "reporting_currency": "USD",
        "scope": "test",
    }


def obs(metric: str, value, cid: str = "acme", status: str = "verified", basis: dict | None = None, kind: str = "actual") -> dict:
    from scorecard.schema import METRICS

    return {
        "observation_id": f"{cid}.{metric}.{status}",
        "company_id": cid,
        "metric": metric,
        "value": value,
        "unit": METRICS[metric]["unit"],
        "as_of": "2026-09-02",
        "kind": kind,
        "source_id": "SRC-test",
        "status": status,
        "basis": basis,
    }


def judgment(factor: str, kind: str, inputs: dict | None = None, score: int | None = None, cid: str = "acme", status: str = "new") -> dict:
    return {
        "judgment_id": f"{cid}.{factor}",
        "company_id": cid,
        "factor": factor,
        "kind": kind,
        "score": score,
        "inputs": inputs or {},
        "evidence": ["test"],
        "reviewer": "tester",
        "reviewed_at": "2026-09-02",
        "status": status,
        "carried_from": "baseline:v1.5" if status == "carried" else None,
    }


def run(decisions: list[dict] | None = None) -> dict:
    return {"decisions": decisions or []}


def decision(did: str, choice: str) -> dict:
    return {"id": did, "choice": choice, "rationale": "test", "decided_by": "tester", "decided_at": "2026-09-02"}


def ntm(per: float, method: str = "vendor_forward_pe_verified_ntm") -> ObsLookup:
    return ObsLookup([obs("ntm_per", per, basis={"method": method})])


class TestF6(unittest.TestCase):
    def test_t01_band_boundaries_half_open(self):
        expectations = {
            19.999: 0, 20.0: -1, 20.001: -1,
            28.999: -1, 29.0: -2, 29.001: -2,
            41.999: -2, 42.0: -3, 42.001: -3,
            61.999: -3, 62.0: -4, 62.001: -4,
            89.999: -4, 90.0: -5, 90.001: -5,
        }
        for per, score in expectations.items():
            result = compute_f6(company(), ntm(per), JudgmentLookup([]), RULES, run())
            self.assertEqual(result["status"], "ok", per)
            self.assertEqual(result["score"], score, per)

    def test_t01_display_rounding_does_not_change_band(self):
        # 19.996 은 화면에 20.0 으로 보이지만 판정은 내부 값으로 0점
        result = compute_f6(company(), ntm(19.996), JudgmentLookup([]), RULES, run())
        self.assertEqual(result["score"], 0)

    def test_t02_boundary_flag_only_warns(self):
        exact = compute_f6(company(), ntm(20 * 1.03), JudgmentLookup([]), RULES, run())
        inside = compute_f6(company(), ntm(20 * 1.02), JudgmentLookup([]), RULES, run())
        outside = compute_f6(company(), ntm(20 * 1.031), JudgmentLookup([]), RULES, run())
        self.assertTrue(exact["calc"]["boundary"]["flag"])
        self.assertTrue(inside["calc"]["boundary"]["flag"])
        self.assertFalse(outside["calc"]["boundary"]["flag"])
        self.assertEqual({exact["score"], inside["score"], outside["score"]}, {-1})

    def test_t03_missing_or_bad_eps_blocks(self):
        # EPS 합 0 이하
        lookup = ObsLookup([obs("price", 100.0), obs("ntm_eps", -1.0, basis={"quarters": ["Q1", "Q2", "Q3", "Q4"]})])
        result = compute_f6(company(), lookup, JudgmentLookup([]), RULES, run())
        self.assertEqual(result["status"], "pending_data")
        # 분기 3개뿐
        lookup = ObsLookup([obs("price", 100.0), obs("ntm_eps", 5.0, basis={"quarters": ["Q1", "Q2", "Q3"]})])
        result = compute_f6(company(), lookup, JudgmentLookup([]), RULES, run())
        self.assertEqual(result["status"], "pending_data")
        # 관측 없음
        result = compute_f6(company(), ObsLookup([]), JudgmentLookup([]), RULES, run())
        self.assertEqual(result["status"], "pending_data")
        # forwardPE 필드명만 (method 없음)
        result = compute_f6(company(), ObsLookup([obs("ntm_per", 25.0)]), JudgmentLookup([]), RULES, run())
        self.assertEqual(result["status"], "pending_data")

    def test_price_over_eps_path(self):
        base = {"share_basis": "common", "currency": "USD"}
        lookup = ObsLookup([obs("price", 100.0, basis=base), obs("ntm_eps", 4.0, basis={**base, "quarters": ["2026Q3", "2026Q4", "2027Q1", "2027Q2"]})])
        result = compute_f6(company(), lookup, JudgmentLookup([]), RULES, run())
        self.assertEqual(result["score"], -1)
        self.assertAlmostEqual(result["calc"]["ntm_per"], 25.0)
        # 식별 불가 라벨은 채점하지 않는다 (R01 보강)
        lookup = ObsLookup([obs("price", 100.0, basis=base), obs("ntm_eps", 4.0, basis={**base, "quarters": ["A", "B", "C", "D"]})])
        self.assertEqual(compute_f6(company(), lookup, JudgmentLookup([]), RULES, run())["status"], "pending_data")

    def test_c13_proxy_requires_decision(self):
        result = compute_f6(company(), ntm(19.4, "annual_weighted_proxy"), JudgmentLookup([]), RULES, run())
        self.assertEqual(result["status"], "needs_rule_decision")
        self.assertEqual(result["pending"]["decision_id"], "C-13")

    def test_c13_accept_proxy_no_longer_scores(self):
        """F6 정책: 근사는 정식 점수를 만들지 않는다. 결정은 기록으로 남고 값은 참고로만 보존한다."""
        result = compute_f6(company(), ntm(19.4, "annual_weighted_proxy"), JudgmentLookup([]), RULES, run([decision("C-13", "accept_proxy_with_flag")]))
        self.assertEqual(result["status"], "pending_data")
        self.assertIsNone(result["score"])
        self.assertAlmostEqual(result["calc"]["ntm_per"], 19.4)
        self.assertEqual(result["calc"]["method"], "annual_weighted_proxy")
        self.assertNotIn("decision_id", result["pending"])

    def test_c13_reject_is_settled_not_undecided(self):
        # 거절은 내려진 결정이다. 규칙 미결로 남아 계속 결정을 요구하면 안 된다.
        result = compute_f6(company(), ntm(19.4, "annual_weighted_proxy"), JudgmentLookup([]), RULES, run([decision("C-13", "reject_proxy")]))
        self.assertEqual(result["status"], "pending_data")
        self.assertIsNone(result["score"])
        self.assertNotIn("decision_id", result["pending"])
        self.assertAlmostEqual(result["calc"]["ntm_per"], 19.4)

    def test_private_multiples_and_manual_score(self):
        c = company(listed=False)
        lookup = ObsLookup([obs("post_money_valuation", 965e9), obs("arr", 65e9), obs("cumulative_raised", 125e9)])
        result = compute_f6(c, lookup, JudgmentLookup([]), RULES, run())
        self.assertEqual(result["status"], "needs_judgment")
        self.assertAlmostEqual(result["calc"]["valuation_over_arr"], 965 / 65)
        result = compute_f6(c, lookup, JudgmentLookup([judgment("F6", "score", score=-3)]), RULES, run())
        self.assertEqual(result["score"], -3)
        self.assertEqual(result["status"], "ok")


class TestQualitative(unittest.TestCase):
    def test_t04_f3_all_combinations(self):
        weights = {"pass": 1.0, "partial": 0.5, "fail": 0.0}
        for imitation in weights:
            for revenue in weights:
                for accel in weights:
                    for door in ("pass", "fail", "unknown"):
                        j = judgment("F3", "criteria", {"imitation": imitation, "revenue_model": revenue, "acceleration": accel, "door_closed": door})
                        result = compute_f3(company(), JudgmentLookup([j]), RULES)
                        points = weights[imitation] + weights[revenue] + weights[accel]
                        if points == 0:
                            expected = 1
                        elif points <= 1:
                            expected = 2
                        elif points <= 2:
                            expected = 3
                        elif imitation != "pass":
                            expected = 3
                        elif door == "pass":
                            expected = 5
                        else:
                            expected = 4
                        self.assertEqual(result["score"], expected, (imitation, revenue, accel, door))
        unknown = judgment("F3", "criteria", {"imitation": "unknown", "revenue_model": "pass", "acceleration": "pass", "door_closed": "fail"})
        self.assertEqual(compute_f3(company(), JudgmentLookup([unknown]), RULES)["status"], "needs_judgment")

    def test_t05_f5_grades(self):
        for A in (0, 1, 2):
            for H in (0, -1, -2, -3):
                j = judgment("F5", "grade", {"A": A, "H": H})
                result = compute_f5(company(), JudgmentLookup([j]), RULES)
                self.assertEqual(result["score"], 3 + A + H)
                self.assertGreaterEqual(result["score"], 0)
        bad = judgment("F5", "grade", {"A": 3, "H": 0})
        with self.assertRaises(SchemaError):
            validate_judgments({"schema": "scorecard.judgments/1", "run_id": "r", "items": [bad]}, {"acme": company()}, RULES.payload, "r")

    def test_t06_f7_matrix(self):
        cases = {("small", "no"): 0, ("large", "no"): -2, ("small", "yes"): -1, ("large", "yes"): -3}
        for (share, returns), expected in cases.items():
            j = judgment("F7", "matrix", {"funding_dependent_share": share, "own_money_returns": returns})
            self.assertEqual(compute_f7(company(), JudgmentLookup([j]), RULES)["score"], expected)
        unknown = judgment("F7", "matrix", {"funding_dependent_share": "unknown", "own_money_returns": "yes"})
        self.assertEqual(compute_f7(company(), JudgmentLookup([unknown]), RULES)["status"], "needs_judgment")
        direct = judgment("F7", "score", score=-4)
        with self.assertRaises(SchemaError):
            validate_judgments({"schema": "scorecard.judgments/1", "run_id": "r", "items": [direct]}, {"acme": company()}, RULES.payload, "r")
        new_score = judgment("F7", "score", score=-1, status="new")
        with self.assertRaises(SchemaError):
            validate_judgments({"schema": "scorecard.judgments/1", "run_id": "r", "items": [new_score]}, {"acme": company()}, RULES.payload, "r")

    def test_f2_requires_decision_and_carried_allowed(self):
        paths = judgment("F2", "paths", {"performance_leap": "pass", "paradigm_adaptation": "fail", "standard_capture": "pass", "top_rank": "no"})
        result = compute_f2(company(), JudgmentLookup([paths]), RULES, run())
        self.assertEqual(result["status"], "needs_rule_decision")
        result = compute_f2(company(), JudgmentLookup([paths]), RULES, run([decision("C-03", "activate_candidate_mapping")]))
        self.assertEqual(result["score"], 4)
        # 3경로 전부 통과는 후보 매핑에 없으므로 기본값 없이 미결
        three = judgment("F2", "paths", {"performance_leap": "pass", "paradigm_adaptation": "pass", "standard_capture": "pass", "top_rank": "no"})
        result = compute_f2(company(), JudgmentLookup([three]), RULES, run([decision("C-03", "activate_candidate_mapping")]))
        self.assertEqual(result["status"], "needs_rule_decision")
        carried = judgment("F2", "score", score=5, status="carried")
        result = compute_f2(company(), JudgmentLookup([carried]), RULES, run())
        self.assertEqual((result["score"], result["status"]), (5, "carried_score"))

    def test_f1_component_cap(self):
        j = judgment("F1", "score", score=4)
        result = compute_manual("F1", company(ctype="부품"), JudgmentLookup([j]), RULES)
        self.assertEqual(result["status"], "error")
        j = judgment("F1", "score", score=2)
        self.assertEqual(compute_manual("F1", company(ctype="부품"), JudgmentLookup([j]), RULES)["score"], 2)


class TestF9(unittest.TestCase):
    def gates(self, *items, cid="acme", gi=None, listed=True, decisions=None):
        lookup = ObsLookup(list(items))
        inputs = {"fcf_trend": "unknown", "bep_retreat": "no", "buffer_erosion": "no", "direction_A": "unknown", "direction_B": "unknown", "coverage_comparable": "unknown"}
        if gi:
            inputs.update(gi)
        j = judgment("F9", "gate_inputs", inputs, cid=cid)
        return compute_f9(company(cid, listed=listed), lookup, JudgmentLookup([j]), RULES, run(decisions))

    def test_t07_fcf_sign_normalization(self):
        # OCF 100, capex 120 → 표준 FCF -20 (부호 역전·이중 차감 없음)
        from scorecard.baseline_import import standard_fcf

        self.assertEqual(standard_fcf(100.0, 120.0), -20.0)
        self.assertEqual(standard_fcf(100.0, -120.0), -20.0)

    def test_g2_positive_trend(self):
        stable = self.gates(obs("operating_margin_ttm", 0.3), obs("fcf_ttm", 50e9), gi={"fcf_trend": "stable"})
        self.assertEqual(stable["score"], 0)
        worse = self.gates(obs("operating_margin_ttm", 0.3), obs("fcf_ttm", 50e9), gi={"fcf_trend": "deteriorating"})
        self.assertEqual(worse["score"], -1)
        unknown = self.gates(obs("operating_margin_ttm", 0.3), obs("fcf_ttm", 50e9))
        self.assertEqual(unknown["status"], "needs_judgment")

    def test_t09_runway_boundaries(self):
        burn = 10e9
        cases = {
            30.0001e9: -2, 30e9: -2, 29.999e9: -3,
            10.0001e9: -3, 10e9: -3, 9.999e9: -4,
        }
        for cash, expected in cases.items():
            result = self.gates(obs("operating_margin_ttm", 0.1), obs("fcf_ttm", -burn), obs("cash", cash),
                                obs("contracted_revenue", 100e9), obs("offbalance_B", 50e9), gi={"coverage_comparable": "yes"})
            self.assertEqual(result["score"], expected, cash)
        # 확정 미인출 여신은 산입, 제한 현금·예상 조달은 관측 자체가 없어 산입 불가
        result = self.gates(obs("operating_margin_ttm", 0.1), obs("fcf_ttm", -burn), obs("cash", 25e9), obs("undrawn_credit", 5e9),
                            obs("contracted_revenue", 100e9), obs("offbalance_B", 50e9), gi={"coverage_comparable": "yes"})
        self.assertEqual(result["score"], -2)

    def test_t10_g1_requires_decision_then_bands(self):
        pending = self.gates(obs("operating_margin_ttm", -0.149), obs("fcf_ttm", -32.5e9), obs("cash", 100e9))
        self.assertEqual(pending["status"], "needs_rule_decision")
        self.assertEqual(pending["pending"]["decision_id"], "C-06")
        dec = [decision("C-06", "proposed_v15_boundaries"), decision("C-05", "diagnose_only"), decision("C-16", "hold")]
        for margin, expected in ((-0.05, -3), (-0.10, -3), (-0.1001, -4), (-0.30, -4), (-0.3001, -5)):
            result = self.gates(obs("operating_margin_ttm", margin), obs("fcf_ttm", -1e9), obs("cash", 100e9), decisions=dec)
            self.assertEqual(result["score"], expected, margin)
        # 방향 완화는 최대 한 단계, -3 아래로 못 감
        relief = self.gates(obs("operating_margin_ttm", -0.05), obs("fcf_ttm", -1e9), obs("cash", 100e9),
                            gi={"direction_A": "pass", "direction_B": "pass"}, decisions=dec)
        self.assertEqual(relief["score"], -3)
        relief = self.gates(obs("operating_margin_ttm", -0.2), obs("fcf_ttm", -1e9), obs("cash", 100e9),
                            gi={"direction_A": "pass", "direction_B": "pass"}, decisions=dec)
        self.assertEqual(relief["score"], -3)
        # BEP 후퇴는 -5, 하한 -5 유지. 이미 하한이면 C-05/C-16 결정 없이도 확정된다
        bep = self.gates(obs("fcf_ttm", -60e9), obs("cash", 10e9), gi={"bep_retreat": "yes"}, decisions=dec)
        self.assertEqual(bep["score"], -5)
        floor_no_decision = self.gates(obs("fcf_ttm", -60e9), obs("cash", 10e9), gi={"bep_retreat": "yes"})
        self.assertEqual((floor_no_decision["score"], floor_no_decision["status"]), (-5, "ok"))
        # G1 실패 뒤 G3 가 더 깎는 경우 C-05 미결이면 대기, apply 면 반영
        deeper = self.gates(obs("operating_margin_ttm", -0.05), obs("fcf_ttm", -50e9), obs("cash", 10e9),
                            obs("contracted_revenue", 10e9), obs("offbalance_B", 5e9), gi={"coverage_comparable": "yes"},
                            decisions=[decision("C-06", "proposed_v15_boundaries")])
        self.assertEqual(deeper["status"], "needs_rule_decision")
        self.assertEqual(deeper["pending"]["decision_id"], "C-05")
        applied = self.gates(obs("operating_margin_ttm", -0.05), obs("fcf_ttm", -50e9), obs("cash", 10e9),
                             obs("contracted_revenue", 10e9), obs("offbalance_B", 5e9), gi={"coverage_comparable": "yes"},
                             decisions=[decision("C-06", "proposed_v15_boundaries"), decision("C-05", "apply")])
        self.assertEqual(applied["score"], -5)
        # FCF 0 은 미결
        zero = self.gates(obs("operating_margin_ttm", 0.1), obs("fcf_ttm", 0.0))
        self.assertEqual(zero["status"], "needs_rule_decision")

    def test_t11_coverage_rules(self):
        base = [obs("operating_margin_ttm", 0.1), obs("fcf_ttm", -10e9), obs("cash", 100e9)]
        ok = self.gates(*base, obs("contracted_revenue", 638e9), obs("offbalance_B", 250e9), gi={"coverage_comparable": "yes"})
        self.assertEqual(ok["score"], -2)
        low = self.gates(*base, obs("contracted_revenue", 100e9), obs("offbalance_B", 250e9), gi={"coverage_comparable": "yes"})
        self.assertEqual(low["score"], -3)
        # 기간·범위가 다른 자료(ARR 대체)는 자료 대기, 비교 가능성 미확인은 판단 대기 — C-16 으로 보내지 않는다
        arr_like = self.gates(*base, obs("contracted_revenue", 65e9), obs("offbalance_B", 50e9), gi={"coverage_comparable": "no"})
        self.assertEqual(arr_like["status"], "pending_data")
        unknown = self.gates(*base, obs("contracted_revenue", 638e9), obs("offbalance_B", 250e9), gi={"coverage_comparable": "unknown"})
        self.assertEqual(unknown["status"], "needs_judgment")
        # 수집 실패·관측 부재는 자료 대기 (미공시 위험으로 둔갑 금지)
        absent = self.gates(*base, gi={"coverage_comparable": "yes"})
        self.assertEqual(absent["status"], "pending_data")
        failed = self.gates(*base, obs("contracted_revenue", None, status="parse_failed"), obs("offbalance_B", 250e9), gi={"coverage_comparable": "yes"})
        self.assertEqual(failed["status"], "pending_data")
        # 확인된 미공시만 C-16 정책 대상
        nd = [obs("contracted_revenue", None, status="not_disclosed"), obs("offbalance_B", None, status="not_disclosed")]
        pending = self.gates(*base, *nd, gi={"coverage_comparable": "yes"})
        self.assertEqual((pending["status"], pending["pending"]["decision_id"]), ("needs_rule_decision", "C-16"))
        hold = self.gates(*base, *nd, gi={"coverage_comparable": "yes"}, decisions=[decision("C-16", "hold")])
        self.assertEqual(hold["score"], -2)
        down = self.gates(*base, *nd, gi={"coverage_comparable": "yes"}, decisions=[decision("C-16", "downgrade")])
        self.assertEqual(down["score"], -3)
        zero_b = self.gates(*base, obs("contracted_revenue", 10e9), obs("offbalance_B", 0.0), gi={"coverage_comparable": "yes"})
        self.assertEqual(zero_b["score"], -2)

    def test_private_not_disclosed_dedupe(self):
        result = self.gates(obs("operating_margin_ttm", 0.05), obs("fcf_ttm", None, status="not_disclosed"), listed=False)
        self.assertEqual(result["score"], -2)
        self.assertEqual(result["status"], "ok")
        gates = [p["gate"] for p in result["calc"]["path"]]
        self.assertIn("G4", gates)
        g4 = [p for p in result["calc"]["path"] if p["gate"] == "G4"][0]
        self.assertEqual(g4["result"], "undetermined")

    def test_missing_ttm_margin_is_pending(self):
        result = self.gates(obs("fcf_ttm", -1e9), obs("cash", 10e9))
        self.assertEqual(result["status"], "pending_data")


class TestAggregate(unittest.TestCase):
    def factors(self, scores: dict[str, int | None], status="ok") -> dict:
        out = {}
        for f in ("F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9"):
            score = scores.get(f, 0)
            out[f] = {"factor": f, "score": score, "status": status if score is not None else "pending_data", "basis": "manual",
                      "judgment_id": None, "observation_ids": [], "calc": {}, "warnings": [], "pending": None if score is not None else {"kind": "data", "message": "x"}}
        return out

    def test_t12_ties_and_incomplete(self):
        a = summarize_company(company("a"), self.factors({"F1": 5, "F2": 5, "F3": 5, "F4": 3, "F6": -1}))
        b = summarize_company(company("b"), self.factors({"F1": 5, "F2": 5, "F3": 5, "F4": 1, "F6": 0}))
        c = summarize_company(company("c"), self.factors({"F1": 5, "F2": 5, "F3": 5, "F4": 1, "F6": 0}))
        d = summarize_company(company("d"), self.factors({"F1": 5, "F2": 5, "F3": 5, "F4": 1, "F6": 0}))
        e = summarize_company(company("e"), self.factors({"F1": 3}))
        x = summarize_company(company("x"), self.factors({"F1": 5, "F9": None}))
        ranked = rank_companies([a, b, c, d, e, x])
        ranks = {r["company_id"]: r["rank"] for r in ranked["ranking"]}
        self.assertEqual(ranks, {"a": 1, "b": 2, "c": 2, "d": 2, "e": 5})
        self.assertEqual([i["company_id"] for i in ranked["population"]["incomplete"]], ["x"])
        self.assertFalse(x["complete"])
        self.assertIsNone(x["total"])


class TestReviewRegressions(unittest.TestCase):
    """설계진행 Codex SCORECARD-REVIEW-01 (R01~R06) 재현을 저장소 테스트로 고정한다."""

    def f9(self, items, *, listed=True, decisions=None, **overrides):
        inputs = {"fcf_trend": "unknown", "bep_retreat": "no", "buffer_erosion": "no", "direction_A": "unknown", "direction_B": "unknown", "coverage_comparable": "unknown"}
        inputs.update(overrides)
        return compute_f9(company(listed=listed), ObsLookup(items), JudgmentLookup([judgment("F9", "gate_inputs", inputs)]), RULES, run(decisions))

    def test_r01_duplicate_or_nonconsecutive_quarters(self):
        base = {"share_basis": "common", "currency": "USD"}
        dup = [obs("price", 100, basis=base), obs("ntm_eps", 4, basis={**base, "quarters": ["Q1"] * 4})]
        self.assertEqual(compute_f6(company(), ObsLookup(dup), JudgmentLookup([]), RULES, run())["status"], "pending_data")
        gap = [obs("price", 100, basis=base), obs("ntm_eps", 4, basis={**base, "quarters": ["2026Q3", "2026Q4", "2027Q2", "2027Q3"]})]
        self.assertEqual(compute_f6(company(), ObsLookup(gap), JudgmentLookup([]), RULES, run())["status"], "pending_data")
        ok = [obs("price", 100, basis=base), obs("ntm_eps", 4, basis={**base, "quarters": ["2026Q3", "2026Q4", "2027Q1", "2027Q2"]})]
        self.assertEqual(compute_f6(company(), ObsLookup(ok), JudgmentLookup([]), RULES, run())["score"], -1)

    def test_r01_basis_alignment(self):
        items = [obs("price", 100, basis={"share_basis": "adr", "currency": "USD"}), obs("ntm_eps", 4, basis={"quarters": ["Q1", "Q2", "Q3", "Q4"], "share_basis": "common", "currency": "TWD"})]
        self.assertEqual(compute_f6(company(), ObsLookup(items), JudgmentLookup([]), RULES, run())["status"], "pending_data")
        missing = [obs("price", 100), obs("ntm_eps", 4, basis={"quarters": ["Q1", "Q2", "Q3", "Q4"]})]
        self.assertEqual(compute_f6(company(), ObsLookup(missing), JudgmentLookup([]), RULES, run())["status"], "pending_data")

    def test_r02_unknown_comparability_does_not_score(self):
        result = self.f9([obs("operating_margin_ttm", 0.1), obs("fcf_ttm", -10.0), obs("cash", 100.0), obs("contracted_revenue", 638.0), obs("offbalance_B", 250.0)])
        self.assertEqual(result["status"], "needs_judgment")
        self.assertIsNone(result["score"])

    def test_r03_explicit_diagnose_only_keeps_g1(self):
        result = self.f9([obs("operating_margin_ttm", -0.05), obs("fcf_ttm", -50.0), obs("cash", 10.0), obs("contracted_revenue", 10.0), obs("offbalance_B", 5.0)],
                         decisions=[decision("C-06", "proposed_v15_boundaries"), decision("C-05", "diagnose_only")], coverage_comparable="yes")
        self.assertEqual((result["status"], result["score"]), ("ok", -3))

    def test_r04_absent_private_fcf_is_pending(self):
        result = self.f9([obs("operating_margin_ttm", 0.05)], listed=False)
        self.assertEqual(result["status"], "pending_data")
        confirmed = self.f9([obs("operating_margin_ttm", 0.05), obs("fcf_ttm", None, status="not_disclosed")], listed=False)
        self.assertEqual((confirmed["status"], confirmed["score"]), ("ok", -2))

    def test_r05_non_finite_rejected(self):
        from scorecard.schema import validate_observations

        for value in (float("nan"), float("inf"), float("-inf")):
            payload = {"schema": "scorecard.observations/1", "run_id": "r", "items": [obs("cash", value)]}
            with self.assertRaises(SchemaError):
                validate_observations(payload, {"acme": company()}, "r")

    def test_r05_json_constants_rejected(self):
        import tempfile
        from scorecard.schema import load_json_strict

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "x.json"
            path.write_text('{"value": NaN}', encoding="utf-8")
            with self.assertRaises(SchemaError):
                load_json_strict(path)

    def test_review2_g1_fail_without_cash_is_pending(self):
        # 재무 계산 리뷰: G1 실패 + FCF 음수 + 현금 관측 없음 → 런웨이 진단 불가를 조용히 넘기지 않는다
        dec = [decision("C-06", "proposed_v15_boundaries"), decision("C-05", "apply")]
        result = self.f9([obs("operating_margin_ttm", -0.05), obs("fcf_ttm", -50.0), obs("contracted_revenue", 10.0), obs("offbalance_B", 5.0)],
                         decisions=dec, coverage_comparable="yes")
        self.assertEqual(result["status"], "pending_data")
        diag = self.f9([obs("operating_margin_ttm", -0.05), obs("fcf_ttm", -50.0)], decisions=[decision("C-06", "proposed_v15_boundaries"), decision("C-05", "diagnose_only")])
        self.assertEqual((diag["status"], diag["score"]), ("ok", -3))
        # 소진율(TTM FCF) 관측 자체가 없거나 수집 실패여도 런웨이 진단을 조용히 건너뛰지 않는다
        for fcf_obs in ([], [obs("fcf_ttm", None, status="collection_failed")]):
            result = self.f9([obs("operating_margin_ttm", -0.05), *fcf_obs, obs("cash", 10.0), obs("contracted_revenue", 10.0), obs("offbalance_B", 5.0)],
                             decisions=dec, coverage_comparable="yes")
            self.assertEqual(result["status"], "pending_data", fcf_obs)

    def test_review2_zero_margin_needs_decision(self):
        result = self.f9([obs("operating_margin_ttm", 0.0), obs("fcf_ttm", 50.0)], fcf_trend="stable")
        self.assertEqual((result["status"], result["pending"]["decision_id"]), ("needs_rule_decision", "C-06"))

    def test_review2_negative_obligation_and_duplicate_observation_rejected(self):
        from scorecard.schema import validate_observations

        with self.assertRaises(SchemaError):
            validate_observations({"schema": "scorecard.observations/1", "run_id": "r", "items": [obs("offbalance_B", -50.0)]}, {"acme": company()}, "r")
        dup = {"schema": "scorecard.observations/1", "run_id": "r", "items": [obs("market_cap", 1.0), {**obs("market_cap", 2.0), "observation_id": "acme.market_cap.other"}]}
        with self.assertRaises(SchemaError):
            validate_observations(dup, {"acme": company()}, "r")

    def test_review3_not_applicable_needs_reason_and_no_value(self):
        # A: 적용 제외와 실제 미공시를 한 상태로 묶지 않는다
        from scorecard.schema import validate_observations

        ok = {**obs("runway_years", None, status="not_applicable"), "note": "TTM FCF 흑자라 산식 적용 대상 아님"}
        validate_observations({"schema": "scorecard.observations/1", "run_id": "r", "items": [ok]}, {"acme": company()}, "r")
        for bad in ({**ok, "note": ""}, {**ok, "value": 3.0}):
            with self.assertRaises(SchemaError):
                validate_observations({"schema": "scorecard.observations/1", "run_id": "r", "items": [bad]}, {"acme": company()}, "r")

    def test_review3_verified_flow_metric_requires_period(self):
        # B: 신규 재무 흐름 지표는 기간 없이 통과하면 안 된다. 과거 이관분은 예외
        from scorecard.schema import validate_observations

        def check(items):
            validate_observations({"schema": "scorecard.observations/1", "run_id": "r", "items": items}, {"acme": company()}, "r")

        with self.assertRaises(SchemaError):
            check([obs("fcf_ttm", -1.0)])
        with self.assertRaises(SchemaError):
            check([obs("operating_margin_ttm", -0.1)])
        check([{**obs("fcf_ttm", -1.0), "period": {"start": "2025-07-01", "end": "2026-06-30"}}])
        check([obs("fcf_ttm", -1.0, status="legacy_unverified")])
        check([obs("cash", 1.0)])  # 스톡 지표는 as_of 로 충분
        # 기간이 있기만 하면 안 된다. 역전된 기간은 분모를 조용히 망가뜨린다
        with self.assertRaises(SchemaError):
            check([{**obs("fcf_ttm", -1.0), "period": {"start": "2026-06-30", "end": "2025-07-01"}}])
        check([{**obs("fcf_ttm", -1.0), "period": {"start": "2026-06-30", "end": "2026-06-30"}}])  # 같은 날은 허용

    def test_review3_approved_by_must_be_nonblank(self):
        from scorecard.schema import validate_approval

        base = {"schema": "scorecard.approval/1", "run_id": "r", "approval_id": "x", "approved_by": "noble",
                "approved_at": "2026-09-08", "hashes": {k: "h" for k in ("rules", "observations", "judgments", "run", "results", "draft")}}
        validate_approval(dict(base), "r")
        for bad in ("", "   ", None, 7):
            with self.assertRaises(SchemaError):
                validate_approval({**base, "approved_by": bad}, "r")

    def test_r06_empty_evidence_rejected(self):
        item = judgment("F1", "score", score=5)
        for bad in ([], [""], ["  "]):
            item["evidence"] = bad
            with self.assertRaises(SchemaError):
                validate_judgments({"schema": "scorecard.judgments/1", "run_id": "r", "items": [item]}, {"acme": company()}, RULES.payload, "r")


if __name__ == "__main__":
    unittest.main()


# ------------------------------------------------------------------ F6 정책 구현 (F6-IMPLEMENT-06)

def qobs(label: str, value: float, cid: str = "acme", source: str = "SRC-q", status: str = "verified",
         currency: str = "USD", share_basis: str = "common", accounting: str = "gaap",
         basis_verified: bool | None = None) -> dict:
    """분기 EPS 관측 하나. label 은 YYYYQn 이며 period 종료월이 분기를 정한다."""
    year, q = int(label[:4]), int(label[5])
    end_month = q * 3
    start_month = end_month - 2
    last_day = {3: 31, 6: 30, 9: 30, 12: 31}[end_month]
    basis = {"currency": currency, "share_basis": share_basis, "accounting": accounting}
    if basis_verified is not None:
        basis["basis_verified"] = basis_verified
    o = obs("ntm_eps_quarter", value, cid=cid, status=status, basis=basis, kind="estimate")
    o["observation_id"] = f"{cid}.q.{label}"
    o["source_id"] = source
    o["period"] = {"start": f"{year}-{start_month:02d}-01", "end": f"{year}-{end_month:02d}-{last_day}"}
    return o


PRICE_BASIS = {"share_basis": "common", "currency": "USD"}
FOUR = ["2026Q3", "2026Q4", "2027Q1", "2027Q2"]


class TestF6QuarterlyPolicy(unittest.TestCase):
    """승인된 F6 정책: 부분 확보는 점수를 만들지 않고, 4분기는 관문을 통과해야 한다."""

    def _lookup(self, quarters, price: float = 100.0, **kw):
        rows = [qobs(lbl, val, **kw) for lbl, val in quarters]
        return ObsLookup([obs("price", price, basis=PRICE_BASIS), *rows])

    def test_two_quarters_pending_no_score(self):
        lookup = self._lookup([("2026Q3", 1.0), ("2026Q4", 1.0)])
        r = compute_f6(company(), lookup, JudgmentLookup([]), RULES, run())
        self.assertEqual(r["status"], "pending_data")
        self.assertIsNone(r["score"])
        self.assertEqual(r["calc"]["coverage"]["secured"], 2)
        self.assertEqual(r["calc"]["coverage"]["required"], 4)

    def test_two_quarters_never_doubled(self):
        """2Q×2 금지. 합계·PER 이 계산되어서는 안 된다."""
        lookup = self._lookup([("2026Q3", 1.0), ("2026Q4", 1.0)])
        r = compute_f6(company(), lookup, JudgmentLookup([]), RULES, run())
        self.assertNotIn("ntm_eps", r["calc"])
        self.assertNotIn("ntm_per", r["calc"])

    def test_three_quarters_pending(self):
        lookup = self._lookup([("2026Q3", 1.0), ("2026Q4", 1.0), ("2027Q1", 1.0)])
        r = compute_f6(company(), lookup, JudgmentLookup([]), RULES, run())
        self.assertEqual(r["status"], "pending_data")
        self.assertEqual(r["calc"]["coverage"]["secured"], 3)

    def test_four_quarters_scores_and_flags_reapproval(self):
        lookup = self._lookup([(q, 1.0) for q in FOUR])
        r = compute_f6(company(), lookup, JudgmentLookup([]), RULES, run())
        self.assertEqual(r["status"], "ok")
        self.assertAlmostEqual(r["calc"]["ntm_eps"], 4.0)
        self.assertAlmostEqual(r["calc"]["ntm_per"], 25.0)
        self.assertEqual(r["calc"]["method"], "consensus_4q_sum")
        self.assertTrue(r["calc"]["requires_reapproval"])
        self.assertEqual(r["score"], -1)

    def test_vendor_mixing_blocked(self):
        rows = [qobs(q, 1.0, source="SRC-a" if i < 2 else "SRC-b") for i, q in enumerate(FOUR)]
        lookup = ObsLookup([obs("price", 100.0, basis=PRICE_BASIS), *rows])
        r = compute_f6(company(), lookup, JudgmentLookup([]), RULES, run())
        self.assertEqual(r["status"], "pending_data")
        self.assertIn("공급사 혼합 금지", r["pending"]["message"])

    def test_non_consecutive_quarters_blocked(self):
        lookup = self._lookup([("2026Q3", 1.0), ("2026Q4", 1.0), ("2027Q1", 1.0), ("2027Q3", 1.0)])
        r = compute_f6(company(), lookup, JudgmentLookup([]), RULES, run())
        self.assertEqual(r["status"], "pending_data")
        self.assertIn("연속", r["pending"]["message"])

    def test_unverified_quarter_blocked(self):
        rows = [qobs(q, 1.0, status="legacy_unverified" if i == 0 else "verified") for i, q in enumerate(FOUR)]
        lookup = ObsLookup([obs("price", 100.0, basis=PRICE_BASIS), *rows])
        r = compute_f6(company(), lookup, JudgmentLookup([]), RULES, run())
        self.assertEqual(r["status"], "pending_data")
        self.assertIn("verified", r["pending"]["message"])

    def test_accounting_basis_required(self):
        rows = [qobs(q, 1.0) for q in FOUR]
        for o in rows:
            o["basis"].pop("accounting")
        lookup = ObsLookup([obs("price", 100.0, basis=PRICE_BASIS), *rows])
        r = compute_f6(company(), lookup, JudgmentLookup([]), RULES, run())
        self.assertEqual(r["status"], "pending_data")
        self.assertIn("회계 기준", r["pending"]["message"])

    def test_currency_mismatch_with_price_blocked(self):
        lookup = self._lookup([(q, 1.0) for q in FOUR], currency="CNY")
        r = compute_f6(company(), lookup, JudgmentLookup([]), RULES, run())
        self.assertEqual(r["status"], "pending_data")
        self.assertIn("기준", r["pending"]["message"])

    def test_adr_company_requires_basis_verification(self):
        c = company(cid="tsmc")
        c["share_basis"] = "adr"
        c["adr_ratio"] = 5
        price = obs("price", 100.0, cid="tsmc", basis={"share_basis": "adr", "currency": "USD"})
        rows = [qobs(q, 1.0, cid="tsmc", share_basis="adr") for q in FOUR]
        r = compute_f6(c, ObsLookup([price, *rows]), JudgmentLookup([]), RULES, run())
        self.assertEqual(r["status"], "pending_data")
        self.assertIn("basis 검산", r["pending"]["message"])
        rows_ok = [qobs(q, 1.0, cid="tsmc", share_basis="adr", basis_verified=True) for q in FOUR]
        r2 = compute_f6(c, ObsLookup([price, *rows_ok]), JudgmentLookup([]), RULES, run())
        self.assertEqual(r2["status"], "ok")

    def test_zero_or_negative_sum_not_scored(self):
        lookup = self._lookup([("2026Q3", -1.0), ("2026Q4", 0.5), ("2027Q1", 0.2), ("2027Q2", 0.3)])
        r = compute_f6(company(), lookup, JudgmentLookup([]), RULES, run())
        self.assertEqual(r["status"], "pending_data")
        self.assertIsNone(r["score"])

    def test_quarterly_path_overrides_legacy_ntm_per(self):
        """분기 관측이 있으면 승계 ntm_per 로 우회 채점되지 않는다."""
        rows = [qobs(q, 1.0) for q in FOUR[:2]]
        lookup = ObsLookup([obs("price", 100.0, basis=PRICE_BASIS),
                            obs("ntm_per", 25.0, basis={"method": "vendor_forward_pe_verified_ntm"}), *rows])
        r = compute_f6(company(), lookup, JudgmentLookup([]), RULES, run())
        self.assertEqual(r["status"], "pending_data")
        self.assertIsNone(r["score"])


class TestSpacexSingleEntity(unittest.TestCase):
    """SPCX 단일 법인 범위가 기업 레지스트리에 반영돼 있는지 고정한다."""

    def setUp(self):
        import json
        from pathlib import Path
        root = Path(__file__).resolve().parents[1]
        data = json.loads((root / "scorecard" / "companies.json").read_text(encoding="utf-8"))
        self.entry = next(c for c in data["companies"] if c["company_id"].startswith("spacex"))

    def test_ticker_and_exchange_recorded(self):
        self.assertEqual(self.entry["ticker"], "SPCX")
        self.assertEqual(self.entry["exchange"], "NASDAQ")
        self.assertTrue(self.entry["listed"])

    def test_scope_is_single_entity_not_sum(self):
        self.assertIn("단일 법인", self.entry["scope"])
        self.assertNotIn("합산 평가 범위", self.entry["scope"])

    def test_us_common_share_basis(self):
        self.assertEqual(self.entry["share_basis"], "common")
        self.assertEqual(self.entry["reporting_currency"], "USD")
