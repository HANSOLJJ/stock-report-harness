# worker 계산기의 설계 계약 위반을 독립적으로 재현하고 수정 후 회귀를 검증한다.
from __future__ import annotations

import sys
import unittest
from pathlib import Path

WORKER = Path(__file__).resolve().parents[2] / "worker"
sys.path.insert(0, str(WORKER / "scripts"))
sys.path.insert(0, str(WORKER / "tests"))

from test_scorecard_calc import RULES, company, decision, judgment, obs, run
from scorecard.calc_f6 import compute_f6
from scorecard.calc_f9 import compute_f9
from scorecard.inputs import JudgmentLookup, ObsLookup
from scorecard.schema import SchemaError, validate_judgments, validate_observations


def f9(items, *, listed=True, decisions=None, **overrides):
    inputs = {
        "fcf_trend": "unknown", "bep_retreat": "no", "buffer_erosion": "no",
        "direction_A": "unknown", "direction_B": "unknown", "coverage_comparable": "unknown",
    }
    inputs.update(overrides)
    return compute_f9(company(listed=listed), ObsLookup(items),
                      JudgmentLookup([judgment("F9", "gate_inputs", inputs)]),
                      RULES, run(decisions))


class ScorecardReview(unittest.TestCase):
    def test_r01_duplicate_eps_quarters_must_not_score(self):
        basis = {"currency": "USD", "share_basis": "common"}
        items = [obs("price", 100, basis=basis),
                 obs("ntm_eps", 4, basis={**basis, "quarters": ["2026Q3"] * 4})]
        result = compute_f6(company(), ObsLookup(items), JudgmentLookup([]), RULES, run())
        self.assertNotEqual(result["status"], "ok", result)

    def test_r01_unaligned_share_basis_must_not_score(self):
        items = [obs("price", 100, basis={"share_basis": "adr", "currency": "USD"}),
                 obs("ntm_eps", 4, basis={"quarters": ["2026Q3", "2026Q4", "2027Q1", "2027Q2"],
                                         "share_basis": "common", "currency": "TWD"})]
        result = compute_f6(company(), ObsLookup(items), JudgmentLookup([]), RULES, run())
        self.assertNotEqual(result["status"], "ok", result)

    def test_r01_valid_aligned_quarters_still_score(self):
        basis = {"currency": "USD", "share_basis": "common"}
        items = [obs("price", 100, basis=basis),
                 obs("ntm_eps", 4, basis={**basis,
                     "quarters": ["2026Q3", "2026Q4", "2027Q1", "2027Q2"]})]
        result = compute_f6(company(), ObsLookup(items), JudgmentLookup([]), RULES, run())
        self.assertEqual((result["status"], result["score"]), ("ok", -1), result)

    def test_r01_unidentifiable_quarters_must_not_score(self):
        basis = {"currency": "USD", "share_basis": "common"}
        items = [obs("price", 100, basis=basis),
                 obs("ntm_eps", 4, basis={**basis, "quarters": ["A", "B", "C", "D"]})]
        result = compute_f6(company(), ObsLookup(items), JudgmentLookup([]), RULES, run())
        self.assertNotEqual(result["status"], "ok", result)

    def test_r02_unknown_coverage_comparability_must_not_score(self):
        result = f9([obs("operating_margin_ttm", 0.1), obs("fcf_ttm", -10), obs("cash", 100),
                     obs("contracted_revenue", 638), obs("offbalance_B", 250)])
        self.assertNotEqual(result["status"], "ok", result)

    def test_r03_explicit_diagnose_only_keeps_g1_score(self):
        result = f9([obs("operating_margin_ttm", -0.05), obs("fcf_ttm", -50), obs("cash", 10),
                     obs("contracted_revenue", 10), obs("offbalance_B", 5)],
                    decisions=[decision("C-06", "proposed_v15_boundaries"),
                               decision("C-05", "diagnose_only")], coverage_comparable="yes")
        self.assertEqual((result["status"], result["score"]), ("ok", -3), result)

    def test_r04_absent_private_fcf_is_not_confirmed_nondisclosure(self):
        result = f9([obs("operating_margin_ttm", 0.05)], listed=False)
        self.assertNotEqual(result["status"], "ok", result)

    def test_r05_nan_observation_rejected(self):
        payload = {"schema": "scorecard.observations/1", "run_id": "r",
                   "items": [obs("ntm_per", float("nan"), basis={"method": "consensus_4q_sum"})]}
        with self.assertRaises(SchemaError):
            validate_observations(payload, {"acme": company()}, "r")

    def test_r05_infinity_observation_rejected(self):
        payload = {"schema": "scorecard.observations/1", "run_id": "r",
                   "items": [obs("cash", float("inf"))]}
        with self.assertRaises(SchemaError):
            validate_observations(payload, {"acme": company()}, "r")

    def test_r06_empty_qualitative_evidence_rejected(self):
        item = judgment("F1", "score", score=5)
        item["evidence"] = []
        with self.assertRaises(SchemaError):
            validate_judgments({"schema": "scorecard.judgments/1", "run_id": "r", "items": [item]},
                               {"acme": company()}, RULES.payload, "r")


if __name__ == "__main__":
    unittest.main(verbosity=2)
