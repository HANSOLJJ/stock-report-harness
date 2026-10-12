# 규칙 v2.1 테스트: v2.0 대비 차이(① 5점 AI 수익화 조건, ⑥ 성장 조정 배수·이익 조정, ⑦ 네 칸 −3, 함정 −17)와 계산·스키마를 잠근다
from __future__ import annotations

import copy
import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard.calc_qual import compute_f1  # noqa: E402
from scorecard.engine import COMPANIES_PATH  # noqa: E402
from scorecard.inputs import JudgmentLookup  # noqa: E402
from scorecard.render_common import _lockin_trace, lockin_calc_text  # noqa: E402
from scorecard.rules import load_rules  # noqa: E402
from scorecard.schema import (SchemaError, load_json_strict, validate_companies, validate_cross_refs,  # noqa: E402
                              validate_judgments)
from scorecard.stages import _check_judgment_changes  # noqa: E402

V20, V21 = load_rules("v2.0"), load_rules("v2.1")
COMPANIES = validate_companies(load_json_strict(COMPANIES_PATH))

MONETIZED = {"ai_monetized_channel": "work", "ai_monetized_measure": "seats", "ai_monetized_share": 0.62,
             "ai_monetized_period": "2026-04-01~2026-06-30", "ai_separate_billing_evidence": ["EV-nvidia-001"],
             "ai_price_uplift_evidence": ["EV-nvidia-002"]}


def rules_json(name: str) -> dict:
    return json.loads((ROOT / "scorecard" / "rules" / f"{name}.json").read_text(encoding="utf-8"))


def company() -> dict:
    return {"company_id": "acme", "display_name": "Acme", "aliases": [], "type": "업무", "listed": True, "ticker": "ACME",
            "exchange": "NASDAQ", "share_basis": "common", "adr_ratio": None, "reporting_currency": "USD", "scope": "test"}


def lockin(cid: str = "acme", status: str = "new", **inputs) -> dict:
    base = {"channel_consumer": "no", "channel_work": "yes", "channel_trade": "no",
            "loop": "pass", "switching": "pass", "substitutes": "pass", "pricing": "pass", "pricing_sustained_quarters": 8,
            "durability_discount": "no", "ai_monetized_in_channel": "unknown"}
    base.update(inputs)
    return {"judgment_id": f"{cid}.F1", "company_id": cid, "factor": "F1", "kind": "lockin", "score": None,
            "inputs": base, "evidence": ["시험"], "reviewer": "tester", "reviewed_at": "2026-10-12", "status": status}


def validate(*items: dict, rules=V21) -> list[dict]:
    return validate_judgments({"schema": "scorecard.judgments/1", "run_id": "t", "items": list(items)}, COMPANIES, rules.payload)


class DiffTest(unittest.TestCase):
    """v2.0 과 v2.1 의 차이가 선언한 자리에만 있다."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.v20, cls.v21 = rules_json("v2.0"), rules_json("v2.1")

    def test_v20_file_unchanged(self):
        # 승인된 rejudge(v2.0) 실행의 rules 해시. 이 값이 바뀌면 그 승인이 깨진다.
        digest = hashlib.sha256((ROOT / "scorecard" / "rules" / "v2.0.json").read_bytes()).hexdigest()
        approved = json.loads((ROOT / "output" / "ai-scorecard-2026-10-rejudge" / "results.json").read_text(encoding="utf-8"))
        self.assertEqual(digest, approved["input_hashes"]["rules"])

    def test_top_level_differs_only_where_declared(self):
        self.assertEqual(set(self.v20), set(self.v21))
        changed = {k for k in self.v21 if self.v21[k] != self.v20[k]}
        self.assertEqual(changed, {"rule_version", "note", "factors", "policies", "scoring", "decisions", "checklist"})
        self.assertEqual({i["id"] for i in self.v21["checklist"] if i not in self.v20["checklist"]}, {"Q01"})
        self.assertEqual({k for k in self.v21["policies"] if self.v21["policies"][k] != self.v20["policies"][k]}, {"f6"})
        self.assertEqual({d["id"] for d in self.v21["decisions"] if d not in self.v20["decisions"]}, {"C-12"})
        self.assertEqual(self.v21["scoring"]["trap_min_active"], -17)
        self.assertEqual(self.v21["rule_version"], "v2.1")
        self.assertTrue(self.v21["note"].startswith(self.v20["note"] + " | v2.1: "))

    def test_changed_factors(self):
        changed = {f for f in self.v21["factors"] if self.v21["factors"][f] != self.v20["factors"][f]}
        self.assertEqual(changed, {"F1", "F4", "F6", "F7", "F8"})
        self.assertEqual((self.v21["factors"]["F4"]["mode"], self.v21["factors"]["F8"]["mode"]), ("survival", "axes"))
        self.assertEqual(self.v21["scoring"]["score_step"], 0.5)
        ranges = {f: self.v21["factors"][f]["range"] for f in ("F6", "F7", "F8", "F9")}
        self.assertEqual(ranges, {"F6": [-5, 0], "F7": [-3, 0], "F8": [-5, 0], "F9": [-4, 0]})
        self.assertEqual(sum(r[0] for r in ranges.values()), self.v21["scoring"]["trap_min_active"])

    def test_f1_gate_and_evidence_spec(self):
        f1 = self.v21["factors"]["F1"]
        gate = f1["ladder"]["top_score_requires_ai_monetized"]
        self.assertEqual((gate["input"], gate["requires"], gate["cap"]), ("ai_monetized_in_channel", "yes", 4))
        self.assertEqual(f1["monetization_evidence"]["share_min_exclusive"], 0.5)
        self.assertEqual(set(f1["monetization_evidence"]["inputs"]),
                         {"ai_monetized_channel", "ai_monetized_measure", "ai_monetized_share", "ai_monetized_period",
                          "ai_separate_billing_evidence", "ai_price_uplift_evidence"})
        old = self.v20["factors"]["F1"]
        self.assertEqual({k: v for k, v in f1["ladder"].items() if k != "top_score_requires_ai_monetized"}, old["ladder"])


class F1GateTest(unittest.TestCase):
    def score(self, rules, **inputs) -> dict:
        return compute_f1(company(), JudgmentLookup([lockin(**inputs)]), rules)

    def test_five_needs_yes(self):
        for value in ("partial", "no", "unknown"):
            with self.subTest(value=value):
                r = self.score(V21, ai_monetized_in_channel=value)
                self.assertEqual(r["score"], 4)
                self.assertTrue(r["calc"]["ai_monetization_gate"]["applied"])
                self.assertIn("AI 수익화", " ".join(r["warnings"]))
        r = self.score(V21, ai_monetized_in_channel="yes", **MONETIZED)
        self.assertEqual(r["score"], 5)
        self.assertFalse(r["calc"]["ai_monetization_gate"]["applied"])

    def test_four_and_below_untouched(self):
        # 가격 실측이 미확인이면 사다리는 4 다. 상한 4 는 아무것도 바꾸지 않는다.
        r = self.score(V21, pricing="unknown", ai_monetized_in_channel="no")
        self.assertEqual(r["score"], 4)
        self.assertFalse(r["calc"]["ai_monetization_gate"]["applied"])
        r = self.score(V21, loop="fail", switching="fail", pricing="fail", ai_monetized_in_channel="no")
        self.assertEqual(r["score"], 0)

    def test_v20_has_no_gate(self):
        r = self.score(V20, ai_monetized_in_channel="no")
        self.assertEqual(r["score"], 5)
        self.assertNotIn("ai_monetization_gate", r["calc"])


class MonetizationSchemaTest(unittest.TestCase):
    def test_yes_needs_all_inputs_in_v21(self):
        with self.assertRaisesRegex(SchemaError, "판정 재료"):
            validate(lockin("nvidia", ai_monetized_in_channel="yes"))
        validate(lockin("nvidia", ai_monetized_in_channel="yes", **MONETIZED))

    def test_share_must_be_majority(self):
        for share in (0.5, 0.07):
            with self.subTest(share=share), self.assertRaisesRegex(SchemaError, "과반"):
                validate(lockin("nvidia", ai_monetized_in_channel="yes", **{**MONETIZED, "ai_monetized_share": share}))

    def test_both_evidence_lists_needed(self):
        for key in ("ai_separate_billing_evidence", "ai_price_uplift_evidence"):
            with self.subTest(key=key), self.assertRaisesRegex(SchemaError, key):
                validate(lockin("nvidia", ai_monetized_in_channel="yes", **{**MONETIZED, key: []}))

    def test_channel_must_be_a_real_channel(self):
        with self.assertRaisesRegex(SchemaError, "실질 채널"):
            validate(lockin("nvidia", ai_monetized_in_channel="yes", **{**MONETIZED, "ai_monetized_channel": "consumer"}))

    def test_value_domains(self):
        bads = {"ai_monetized_measure": "users", "ai_monetized_share": 1.2, "ai_monetized_period": " ",
                "ai_separate_billing_evidence": ["nvidia-001"], "ai_price_uplift_evidence": "EV-nvidia-002"}
        for key, value in bads.items():
            with self.subTest(key=key), self.assertRaisesRegex(SchemaError, key):
                validate(lockin("nvidia", ai_monetized_in_channel="partial", **{**MONETIZED, key: value}))

    def test_partial_needs_nothing(self):
        validate(lockin("nvidia", ai_monetized_in_channel="partial"))

    def test_v20_does_not_require_inputs(self):
        validate(lockin("nvidia", ai_monetized_in_channel="yes"), rules=V20)


class MonetizationCrossRefTest(unittest.TestCase):
    SRC = [{"source_id": "S"}]

    def ev(self, eid: str, status: str = "confirmed") -> dict:
        return {"evidence_id": eid, "source_id": "S", "status": status}

    def test_evidence_must_exist_and_be_confirmed(self):
        j = validate(lockin("nvidia", ai_monetized_in_channel="yes", **MONETIZED))
        with self.assertRaisesRegex(SchemaError, "AI 수익화 근거"):
            validate_cross_refs([], j, [self.ev("EV-nvidia-001")], self.SRC)
        with self.assertRaisesRegex(SchemaError, "확정되지 않았다"):
            validate_cross_refs([], j, [self.ev("EV-nvidia-001"), self.ev("EV-nvidia-002", "candidate")], self.SRC)
        validate_cross_refs([], j, [self.ev("EV-nvidia-001"), self.ev("EV-nvidia-002")], self.SRC)


class ChangeShapeTest(unittest.TestCase):
    def test_cli_only_monetization_shapes(self):
        self.assertEqual(_check_judgment_changes("F1", {"ai_monetized_share": 0.6, "ai_separate_billing_evidence": ["EV-a-001"],
                                                        "ai_monetized_channel": "work"}, V21), "lockin")
        bads = ({"ai_monetized_share": "0.6"}, {"ai_separate_billing_evidence": "EV-a-001"}, {"ai_monetized_period": ""},
                {"ai_price_uplift_evidence": [3]})
        for bad in bads:
            with self.subTest(bad=bad), self.assertRaisesRegex(SchemaError, "모양"):
                _check_judgment_changes("F1", bad, V21)

    def test_growth_rates_shape_still_checked(self):
        with self.assertRaisesRegex(SchemaError, "숫자 목록"):
            _check_judgment_changes("F3", {"acceleration_growth_rates": ["a", "b"]}, V21)


class TraceTextTest(unittest.TestCase):
    def test_gate_is_named_not_called_a_clip(self):
        r = compute_f1(company(), JudgmentLookup([lockin(ai_monetized_in_channel="no")]), V21)
        text = _lockin_trace(r["calc"])
        self.assertIn("상한 4 = 4", text)
        self.assertNotIn("로 자름", text)
        vals = dict(lockin(ai_monetized_in_channel="no")["inputs"])
        self.assertIn("(5점 조건)", lockin_calc_text(V21, r, vals))
        r20 = compute_f1(company(), JudgmentLookup([lockin(ai_monetized_in_channel="no")]), V20)
        self.assertIn("(점수 밖 표시)", lockin_calc_text(V20, r20, vals))

    def test_share_shown_with_measure(self):
        j = lockin(ai_monetized_in_channel="yes", **MONETIZED)
        r = compute_f1(company(), JudgmentLookup([j]), V21)
        self.assertIn("좌석 62%(5점 조건)", lockin_calc_text(V21, r, dict(j["inputs"])))


# ------------------------------------------------------------------ ⑥ · ⑦
from scorecard.calc_f6 import compute_f6  # noqa: E402
from scorecard.calc_qual import compute_f7  # noqa: E402
from scorecard.inputs import ObsLookup  # noqa: E402

PARENT = {"ownership_scope": "parent_attributable"}


def obs(metric: str, value, cid: str = "acme", basis: dict | None = None, kind: str = "actual") -> dict:
    return {"observation_id": f"{cid}.{metric}.t", "company_id": cid, "metric": metric, "value": value, "unit": "USD",
            "as_of": "2026-10-12", "kind": kind, "source_id": "SRC-t", "status": "verified",
            "period": {"start": "2025-07-01", "end": "2026-06-30"}, "basis": basis, "raw": None, "note": None}


def listed_obs(*, market_cap=2000.0, net_income=10.0, revenue=130.0, revenue_prior=100.0, net_cash=0.0,
               pretax=None, operating_income=None, gains=None, tax=None, gains_basis=None, tax_basis=None,
               pretax_basis=None) -> ObsLookup:
    items = [obs("market_cap", market_cap), obs("net_cash", net_cash), obs("net_income_ttm", net_income, basis=PARENT),
             obs("revenue_ttm", revenue, basis={"period_basis": "ttm"}),
             obs("revenue_ttm_prior", revenue_prior, basis={"period_basis": "ttm"})]
    for metric, value, basis in (("pretax_income_ttm", pretax, pretax_basis), ("operating_income_ttm", operating_income, None),
                                 ("equity_investment_gains_ttm", gains, gains_basis), ("income_tax_ttm", tax, tax_basis)):
        if value is not None:
            items.append(obs(metric, value, basis=basis))
    return ObsLookup(items)


def run21(c12: str | None = "growth_adjusted_ps") -> dict:
    return {"run_id": "t", "rule_version": "v2.1", "as_of": "2026-10-12",
            "decisions": [{"id": "C-12", "choice": c12}] if c12 else []}


def private_company() -> dict:
    return {**company(), "listed": False, "ticker": None, "exchange": None, "share_basis": "private"}


class F6GrowthAdjustedTest(unittest.TestCase):
    def f6(self, **kw) -> dict:
        return compute_f6(company(), listed_obs(**kw), JudgmentLookup([]), V21, run21())

    def test_p1_is_per_over_growth(self):
        # PER 2000/40=50, 성장 30% → 50/30=1.67 → −1. EV/매출 2000/130=15.4 → −1. 합 −2.
        r = self.f6(net_income=40.0)
        p1 = r["calc"]["parameters"]["P1"]
        self.assertAlmostEqual(p1["value"], 50 / 30)
        self.assertEqual((p1["score"], r["calc"]["parameters"]["P2"]["score"], r["score"]), (-1, -1, -2))
        self.assertNotIn("P3", r["calc"]["parameters"])
        self.assertTrue(r["calc"]["parameters_not_in_track"]["P3"]["absorbed"])

    def test_bands(self):
        for value, want in ((0.99, 0), (1.0, -1), (1.99, -1), (2.0, -2), (3.99, -2), (4.0, -3), (40.0, -3)):
            self.assertEqual(V21.f6_parameter_band("P1", value)[0], want, msg=f"P1 {value}")

    def test_monotonic_when_earnings_turn_negative(self):
        # 외부 검토 2차 사례: PER 200·성장 30% 가 −3 인데 같은 가격에 적자로 바뀌면 P3 0 으로 점수가 좋아지던 결함.
        profit = self.f6(net_income=10.0)
        self.assertEqual(profit["calc"]["parameters"]["P1"]["score"], -3)
        for ni in (0.0, -10.0):
            with self.subTest(net_income=ni):
                r = self.f6(net_income=ni)
                self.assertEqual(r["status"], "ok")
                self.assertEqual(r["calc"]["parameters"]["P1"]["score"], -3)
                self.assertLessEqual(r["score"], profit["score"])

    def test_growth_floor(self):
        self.assertEqual(self.f6(net_income=200.0)["calc"]["parameters"]["P1"]["score"], 0)       # 10/30 = 0.33
        for revenue, prior in ((130.0, 130.0), (130.0, 160.0), (104.9, 100.0)):                    # 0%·−19%·4.9%
            with self.subTest(revenue=revenue, prior=prior):
                r = self.f6(net_income=200.0, revenue=revenue, revenue_prior=prior)
                self.assertEqual(r["calc"]["parameters"]["P1"]["score"], -3)

    def test_range_floor_minus_five(self):
        r = self.f6(net_income=-1.0, market_cap=5000.0, revenue=101.0)
        self.assertEqual(r["score"], -5)       # P1 −3 + P2 −2 = −5


class F6EarningsAdjustmentTest(unittest.TestCase):
    def f6(self, **kw) -> dict:
        return compute_f6(company(), listed_obs(**kw), JudgmentLookup([]), V21, run21())

    def test_alphabet_like_adjustment(self):
        # 순이익 2442, 평가이익 1490, 법인세 551 / 세전 2993(18.4%) → 조정 순이익 ≈ 1226, 조정 PER 43008/1226 ≈ 35.1.
        r = self.f6(market_cap=43008.0, net_income=2442.0, pretax=2993.0, operating_income=1476.0, gains=1490.0, tax=551.0,
                    revenue=120.05, revenue_prior=100.0)
        p1 = r["calc"]["parameters"]["P1"]
        adj = p1["earnings_adjustment"]
        self.assertTrue(adj["applied"])
        self.assertAlmostEqual(adj["effective_tax_rate"], 551 / 2993)
        self.assertAlmostEqual(p1["net_income_used"], 2442 - 1490 * (1 - 551 / 2993))
        self.assertAlmostEqual(p1["per_used"], 35.1, delta=0.1)
        self.assertAlmostEqual(p1["per_reported"], 43008 / 2442)
        # 조정했으므로 영업외 비중(51%) 조건을 보지 않는다
        self.assertEqual(r["calc"]["p4"]["conditions_hit"], [])
        self.assertIn("nonop_share_skipped", r["calc"]["p4"])

    def test_tax_is_not_derived_from_parent_net_income(self):
        # 연결 세전 100, 법인세 20, 비지배 10 → 모회사 순이익 70. 세전 − 순이익(30)이 아니라 공시 법인세(20)로 20% 다.
        r = self.f6(net_income=70.0, pretax=100.0, operating_income=60.0, gains=10.0, tax=20.0)
        p1 = r["calc"]["parameters"]["P1"]
        self.assertAlmostEqual(p1["earnings_adjustment"]["effective_tax_rate"], 0.20)
        self.assertAlmostEqual(p1["net_income_used"], 70 - 10 * 0.8)

    def test_not_adjustable_falls_back_to_reported_and_p4(self):
        cases = {"세전 0 이하": dict(pretax=-5.0, tax=1.0), "세율 범위 밖": dict(pretax=100.0, tax=60.0),
                 "법인세 없음": dict(pretax=100.0, tax=None),
                 "태그 겹침": dict(pretax=100.0, tax=20.0, gains_basis={"components": [{"tag": "A"}, {"tag": "A"}]}),
                 # 두 관측이 모두 범위를 밝혔는데 다를 때만 막는다(한쪽만 밝혔으면 비교할 것이 없다)
                 "범위 다름": dict(pretax=100.0, tax=20.0, tax_basis={"ownership_scope": "parent_attributable"},
                                pretax_basis={"ownership_scope": "consolidated_incl_nci"})}
        for name, kw in cases.items():
            with self.subTest(case=name):
                r = self.f6(net_income=70.0, operating_income=30.0, gains=50.0, **kw)
                p1 = r["calc"]["parameters"]["P1"]
                self.assertFalse(p1["earnings_adjustment"]["applied"])
                self.assertEqual(p1["net_income_used"], 70.0)
                if kw["pretax"] > 0:
                    # 보고 순이익으로 돌아가면 영업외 비중 조건이 살아 있다
                    self.assertIn("nonop_share", r["calc"]["p4"]["conditions_hit"])

    def test_no_gains_observation_is_v20_behaviour(self):
        r = self.f6(net_income=70.0, pretax=100.0, operating_income=30.0)
        self.assertFalse(r["calc"]["parameters"]["P1"]["earnings_adjustment"]["applied"])
        self.assertIn("nonop_share", r["calc"]["p4"]["conditions_hit"])

    def test_loss_raises_adjusted_income(self):
        r = self.f6(net_income=70.0, pretax=100.0, operating_income=110.0, gains=-10.0, tax=20.0)
        self.assertAlmostEqual(r["calc"]["parameters"]["P1"]["net_income_used"], 70 + 10 * 0.8)

    def test_adjustment_to_nonpositive_is_minus_three(self):
        r = self.f6(net_income=50.0, pretax=100.0, operating_income=-20.0, gains=120.0, tax=20.0)
        p1 = r["calc"]["parameters"]["P1"]
        self.assertLessEqual(p1["net_income_used"], 0)
        self.assertEqual(p1["score"], -3)


class F6PrivateGrowthTest(unittest.TestCase):
    def f6(self, *, ps=40.0, rng=None, revenue=None, prior=None, c12="growth_adjusted_ps") -> dict:
        items = [obs("ps_ratio", ps, basis={"estimate_range": rng} if rng else None, kind="estimate")]
        if revenue is not None:
            items.append(obs("revenue_ttm", revenue))
        if prior is not None:
            items.append(obs("revenue_ttm_prior", prior))
        return compute_f6(private_company(), ObsLookup(items), JudgmentLookup([]), V21, run21(c12))

    def test_growth_adjusted_bands_and_ceiling(self):
        for revenue, want in ((200.0, -2), (130.0, -3), (108.0, -5)):     # 40/100=0.4 · 40/30=1.33 · 40/8=5
            with self.subTest(revenue=revenue):
                r = self.f6(ps=40.0, revenue=revenue, prior=100.0)
                self.assertEqual((r["score"], r["calc"]["growth_adjusted"]["path"]), (want, "growth_adjusted"))
                self.assertNotIn("correction", r["calc"])

    def test_zero_and_negative_growth_are_worst(self):
        for prior in (100.0, 120.0, 102.0):                      # 성장 0%·−17%·−2%
            with self.subTest(prior=prior):
                r = self.f6(ps=40.0, revenue=100.0, prior=prior)
                self.assertEqual((r["score"], r["calc"]["growth_adjusted"]["path"]), (-5, "below_growth_floor"))

    def test_fallback_without_revenue(self):
        r = self.f6(ps=41.24)
        self.assertEqual((r["score"], r["calc"]["growth_adjusted"]["path"]), (-4, "fallback_private_bands"))
        self.assertNotIn("correction", r["calc"])

    def test_nonpositive_revenue_is_pending(self):
        self.assertEqual(self.f6(ps=40.0, revenue=0.0, prior=100.0)["status"], "pending_data")

    def test_estimate_range_spanning_growth_bands_is_pending(self):
        self.assertEqual(self.f6(ps=40.0, rng=[30.0, 90.0], revenue=130.0, prior=100.0)["status"], "pending_data")   # 1.0~3.0
        self.assertEqual(self.f6(ps=40.0, rng=[31.0, 50.0], revenue=130.0, prior=100.0)["score"], -3)               # 1.03~1.67

    def test_old_choice_is_refused_in_v21(self):
        r = self.f6(c12="p2_with_capped_promotion", revenue=130.0, prior=100.0)
        self.assertEqual(r["status"], "needs_rule_decision")


class F7FourCellsTest(unittest.TestCase):
    def test_four_cells(self):
        want = {("small", "no"): 0, ("small", "yes"): -1, ("large", "no"): -2, ("large", "yes"): -3}
        for (share, back), score in want.items():
            j = {"judgment_id": "acme.F7", "company_id": "acme", "factor": "F7", "kind": "matrix", "score": None,
                 "inputs": {"funding_dependent_share": share, "own_money_returns": back}, "evidence": ["시험"],
                 "reviewer": "t", "reviewed_at": "2026-10-12", "status": "new"}
            with self.subTest(cell=(share, back)):
                self.assertEqual(compute_f7(company(), JudgmentLookup([j]), V21)["score"], score)
        j["inputs"] = {"funding_dependent_share": "large", "own_money_returns": "yes"}
        self.assertEqual(compute_f7(company(), JudgmentLookup([j]), V20)["score"], -2)


# ------------------------------------------------------------------ ④ · ⑧ · 0.5 단위
from scorecard.aggregate import summarize_company  # noqa: E402
from scorecard.calc_qual import compute_f4, compute_f8  # noqa: E402
from scorecard.render_md import fmt_score  # noqa: E402

ALL_SOLD = {"chip": "sold", "server": "sold", "platform": "sold", "cloud": "sold", "model": "sold", "app": "sold"}


def survival(cid: str = "acme", status: str = "new", **inputs) -> dict:
    base = {"layers": dict(ALL_SOLD), "primary_layer": "chip", "non_ai_revenue_share": 0.07}
    base.update(inputs)
    return {"judgment_id": f"{cid}.F4", "company_id": cid, "factor": "F4", "kind": "survival", "score": None, "inputs": base,
            "evidence": ["시험"], "reviewer": "t", "reviewed_at": "2026-10-12", "status": status}


def axes(cid: str = "acme", status: str = "new", **inputs) -> dict:
    base = {"customer": {"status": "absent_disclosed"}, "commitment": {"status": "confirmed", "multiple": 0.3},
            "supply": {"status": "confirmed", "rung": -1}, "geopolitics": {"status": "confirmed", "rung": -1}}
    base.update(inputs)
    return {"judgment_id": f"{cid}.F8", "company_id": cid, "factor": "F8", "kind": "axes", "score": None, "inputs": base,
            "evidence": ["시험"], "reviewer": "t", "reviewed_at": "2026-10-12", "status": status}


class F4SurvivalTest(unittest.TestCase):
    def score(self, **inputs) -> dict:
        return compute_f4(company(), JudgmentLookup([survival(**inputs)]), V21)

    def test_nvidia_like_pickaxe(self):
        # 여섯 층 판매(6 → 상한 2.5) + AI 무관 매출 7%(0.5) = 3
        r = self.score()
        self.assertEqual((r["score"], r["calc"]["vertical"], r["calc"]["diversification"]), (3, 2.5, 0.5))

    def test_meta_like_ads_survive(self):
        layers = {"chip": "self", "server": "self", "platform": "none", "cloud": "none", "model": "self", "app": "sold"}
        r = self.score(layers=layers, primary_layer="app", non_ai_revenue_share=0.98)
        self.assertEqual((r["calc"]["vertical"], r["calc"]["diversification"], r["score"]), (2.5, 2.5, 5))

    def test_half_points(self):
        layers = {"chip": "sold", "server": "self", "platform": "none", "cloud": "none", "model": "none", "app": "none"}
        r = self.score(layers=layers, non_ai_revenue_share=0.85)          # 1.5 + 2.5 = 4
        self.assertEqual(r["score"], 4)
        self.assertIsInstance(r["score"], int)
        r = self.score(layers=layers, non_ai_revenue_share=0.6)           # 1.5 + 2 = 3.5
        self.assertEqual(r["score"], 3.5)

    def test_tiers(self):
        for share, want in ((0.8, 2.5), (0.79, 2), (0.5, 2), (0.2, 1), (0.05, 0.5), (0.049, 0), (0.0, 0)):
            with self.subTest(share=share):
                self.assertEqual(self.score(non_ai_revenue_share=share)["calc"]["diversification"], want)

    def test_preparing_counts_zero(self):
        layers = dict(ALL_SOLD, chip="preparing", server="none", platform="none", cloud="none", model="none")
        r = self.score(layers=layers, primary_layer="app", layer_triggers={"chip": "TRG-111"}, non_ai_revenue_share=0.0)
        self.assertEqual((r["calc"]["vertical"], r["calc"]["preparing"], r["score"]), (1.0, ["chip"], 1))

    def test_unknowns_make_no_score(self):
        self.assertEqual(self.score(layers=dict(ALL_SOLD, model="unknown"))["status"], "needs_judgment")
        self.assertEqual(self.score(non_ai_revenue_share="unknown")["status"], "needs_judgment")

    def test_carried_score_kind_is_not_used(self):
        j = {**survival(), "kind": "score", "score": 5, "inputs": {}, "status": "carried", "carried_from": "run:x"}
        self.assertEqual(compute_f4(company(), JudgmentLookup([j]), V21)["status"], "needs_judgment")


class F8AxesTest(unittest.TestCase):
    def score(self, **inputs) -> dict:
        return compute_f8(company(), JudgmentLookup([axes(**inputs)]), V21)

    def test_worst_axis_decides(self):
        r = self.score(customer={"status": "confirmed", "recognized_share": 0.1, "contract_share": 0.36},
                       commitment={"status": "confirmed", "multiple": 1.68})
        self.assertEqual((r["score"], r["calc"]["deciding_axes"]), (-3, ["customer"]))
        self.assertEqual(r["calc"]["axes"]["commitment"]["score"], -2)

    def test_customer_bands(self):
        for share, dedicated, want in ((0.09, "no", 0), (0.1, "no", -2), (0.3, "no", -3), (0.6, "no", -3),
                                       (0.5, "yes", -4), (0.95, "yes", -5), (0.42, "yes", -3)):
            with self.subTest(share=share, dedicated=dedicated):
                r = self.score(customer={"status": "confirmed", "recognized_share": share, "dedicated_assets": dedicated},
                               supply={"status": "absent_disclosed"}, geopolitics={"status": "absent_disclosed"})
                self.assertEqual(r["calc"]["axes"]["customer"]["score"], want)

    def test_commitment_bands(self):
        for multiple, want in ((0.49, 0), (0.5, -2), (2.99, -2), (3.0, -3), (19.9, -3), (20.0, -4)):
            with self.subTest(multiple=multiple):
                r = self.score(commitment={"status": "confirmed", "multiple": multiple})
                self.assertEqual(r["calc"]["axes"]["commitment"]["score"], want)

    def test_geopolitics_axis(self):
        r = self.score(geopolitics={"status": "confirmed", "rung": -4})
        self.assertEqual((r["score"], r["calc"]["deciding_axes"]), (-4, ["geopolitics"]))

    def test_policy_default_minus_one(self):
        r = self.score(customer={"status": "not_disclosed"}, commitment={"status": "absent_disclosed"},
                       supply={"status": "absent_disclosed"}, geopolitics={"status": "not_applicable"})
        self.assertEqual(r["score"], -1)
        self.assertTrue(r["calc"]["axes"]["customer"]["policy_default"])
        self.assertFalse(r["calc"]["assessment_complete"])
        self.assertIn("정책 기본값", " ".join(r["warnings"]))
        # 다른 축이 더 깊으면 기본값은 영향이 없다
        r = self.score(customer={"status": "not_found"}, geopolitics={"status": "confirmed", "rung": -3})
        self.assertEqual(r["score"], -3)

    def test_absent_disclosed_is_zero_not_default(self):
        r = self.score(supply={"status": "absent_disclosed"}, geopolitics={"status": "absent_disclosed"})
        self.assertEqual(r["score"], 0)
        self.assertTrue(r["calc"]["assessment_complete"])

    def test_all_defaults_make_no_score(self):
        r = self.score(customer={"status": "not_found"}, commitment={"status": "not_disclosed"},
                       supply={"status": "not_found"}, geopolitics={"status": "not_disclosed"})
        self.assertEqual(r["status"], "needs_judgment")


class SurvivalAxesSchemaTest(unittest.TestCase):
    def test_valid_pair(self):
        validate(survival("nvidia"), axes("nvidia"))

    def test_survival_shapes(self):
        bads = {"여섯 칸": dict(layers={"chip": "sold"}), "칸 값": dict(layers=dict(ALL_SOLD, chip="maybe")),
                "주 레이어": dict(primary_layer="cloud", layers=dict(ALL_SOLD, cloud="self")),
                "몫": dict(non_ai_revenue_share=1.3),
                "트리거": dict(layers=dict(ALL_SOLD, model="preparing"))}
        for name, kw in bads.items():
            with self.subTest(case=name), self.assertRaises(SchemaError):
                validate(survival("nvidia", **kw))
        validate(survival("nvidia", layers=dict(ALL_SOLD, model="preparing"), layer_triggers={"model": "TRG-111"}))

    def test_axes_shapes(self):
        bads = {"상태": dict(customer={"status": "maybe"}), "확인됨 재료": dict(commitment={"status": "confirmed"}),
                "칸": dict(supply={"status": "confirmed", "rung": -6}), "모르는 키": dict(geopolitics={"status": "confirmed", "rung": -1, "x": 1})}
        for name, kw in bads.items():
            with self.subTest(case=name), self.assertRaises(SchemaError):
                validate(axes("nvidia", **kw))

    def test_supply_floor_when_compute_is_bought(self):
        no_compute = dict(ALL_SOLD, chip="none", cloud="none", server="none", platform="none")
        with self.assertRaisesRegex(SchemaError, "공급 축을 0"):
            validate(survival("anthropic", layers=no_compute, primary_layer="model", non_ai_revenue_share=0.0),
                     axes("anthropic", supply={"status": "confirmed", "rung": 0}))
        with self.assertRaisesRegex(SchemaError, "공급 축을 0"):
            validate(survival("anthropic", layers=no_compute, primary_layer="model", non_ai_revenue_share=0.0),
                     axes("anthropic", supply={"status": "absent_disclosed"}))
        validate(survival("anthropic", layers=no_compute, primary_layer="model", non_ai_revenue_share=0.0),
                 axes("anthropic", supply={"status": "confirmed", "rung": -3}))
        # v2.0 규칙에는 이 검사가 없다(그 규칙은 survival·axes 를 새 판단으로 받지 않으므로 score 로 대조)

    def test_v20_reads_but_does_not_score_survival(self):
        # v1.9 가 lockin 을 받던 선례와 같다: 옛 규칙은 새 kind 를 읽되 계산 경로가 없어 점수를 만들지 않는다.
        validate(survival("nvidia"), rules=V20)
        from scorecard.calc_qual import compute_manual
        self.assertEqual(compute_manual("F4", company(), JudgmentLookup([survival()]), V20)["status"], "needs_judgment")

    def test_share_evidence_cross_ref(self):
        j = validate(survival("nvidia", non_ai_share_evidence=["EV-nvidia-009"]))
        with self.assertRaisesRegex(SchemaError, "AI 무관 매출 몫·보유표 근거"):
            validate_cross_refs([], j, [], [{"source_id": "S"}])
        validate_cross_refs([], j, [{"evidence_id": "EV-nvidia-009", "source_id": "S", "status": "confirmed"}], [{"source_id": "S"}])


class SurvivalAxesTextTest(unittest.TestCase):
    def test_survival_line(self):
        from scorecard.render_common import survival_calc_text
        layers = {"chip": "sold", "server": "self", "platform": "none", "cloud": "none", "model": "preparing", "app": "none"}
        r = compute_f4(company(), JudgmentLookup([survival(layers=layers, layer_triggers={"model": "TRG-111"},
                                                             non_ai_revenue_share=0.6)]), V21)
        self.assertEqual(survival_calc_text(V21, r["calc"]),
                         "수직 1.5: 칩 판매 · 서버·네트워크 자체 사용 · 모델 준비 중 + 다각화 2: AI 무관 매출 60% = 3.5")

    def test_axes_line_names_defaults_and_deciding_axis(self):
        from scorecard.render_common import axes_calc_text
        r = compute_f8(company(), JudgmentLookup([axes(customer={"status": "not_found"},
                                                       geopolitics={"status": "confirmed", "rung": -4})]), V21)
        self.assertEqual(axes_calc_text(V21, r["calc"]),
                         "고객 -1(탐색 미완, 정책 기본값) · 약정 0 · 공급 -1 · 지정학 -4 → 가장 낮은 축 지정학 = -4")


class SurvivalReportTest(unittest.TestCase):
    """④ 보유표 표·비교 그룹 안 순위·산점도 색. 옛 실행의 초안은 한 글자도 바뀌지 않는다."""

    def results(self) -> dict:
        def summary(cid, name, layers, primary, share, total, rank):
            f4 = compute_f4({**company(), "company_id": cid}, JudgmentLookup([survival(cid, layers=layers, primary_layer=primary,
                                                                   non_ai_revenue_share=share)]), V21)
            return {"company_id": cid, "display_name": name, "type": "업무", "factors": {"F4": f4}, "total": total,
                    "rank": rank, "complete": rank is not None}
        model_only = {"chip": "none", "server": "none", "platform": "none", "cloud": "none", "model": "sold", "app": "sold"}
        return {"companies": [
            summary("openai", "OpenAI", model_only, "model", 0.0, 1, 3),
            summary("anthropic", "Anthropic", model_only, "model", 0.0, 2, 2),
            summary("amazon", "Amazon", dict(ALL_SOLD), "cloud", 0.9, 13, 1),
            summary("meta", "Meta", model_only, "app", 0.98, None, None)]}

    def test_rows_and_groups(self):
        from scorecard.render_common import comparison_groups, survival_rows
        res = self.results()
        self.assertEqual([r["company_id"] for r in survival_rows(res)], ["amazon", "anthropic", "openai", "meta"])
        groups = comparison_groups(res)
        self.assertEqual({k: [m["company_id"] for m in v] for k, v in groups.items()},
                         {"model": ["anthropic", "openai"], "cloud": ["amazon"]})      # 미완료(Meta)는 그룹 순위에 없다

    def test_dot_class_uses_group_only_when_present(self):
        from scorecard.render_html import dot_class
        res = self.results()
        self.assertEqual(dot_class(res["companies"][0]), "layer-model")
        self.assertEqual(dot_class({"type": "업무", "factors": {"F4": {"score": 4, "calc": None}}}), "work")

    def test_cell_evidence_in_formula_line(self):
        from scorecard.render_common import survival_calc_text
        j = survival(layers={"chip": "sold", "server": "none", "platform": "none", "cloud": "none", "model": "none", "app": "none"},
                     layer_evidence={"chip": ["EV-acme-001", "EV-acme-002"]}, non_ai_revenue_share=0.0)
        r = compute_f4(company(), JudgmentLookup([j]), V21)
        self.assertIn("칩 판매 [EV-acme-001, EV-acme-002]", survival_calc_text(V21, r["calc"]))

    def test_v20_draft_rerender_is_unchanged(self):
        from scorecard.engine import load_context
        from scorecard.render_md import render_draft
        from scorecard.stages import load_baseline
        slug = "ai-scorecard-2026-10-recheck"
        ctx = load_context(slug)
        results = json.loads((ROOT / "output" / slug / "results.json").read_text(encoding="utf-8"))
        scores, _o, triggers = load_baseline(ctx.run["baseline_id"])
        committed = (ROOT / "output" / slug / "draft.md").read_text(encoding="utf-8").replace("\r\n", "\n")
        self.assertEqual(render_draft(ctx, results, scores, triggers), committed)


class HalfStepTest(unittest.TestCase):
    def test_sum_keeps_ints_and_halves(self):
        def fr(score):
            return {"score": score, "status": "ok", "pending": None}
        factors = {f: fr(s) for f, s in zip(("F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9"), (4, 4, 3, 3.5, 4, -2, -1, -2, 0))}
        s = summarize_company(company(), factors)
        self.assertEqual((s["moat"], s["trap"], s["total"]), (18.5, -5, 13.5))
        factors["F4"] = fr(4)
        s = summarize_company(company(), factors)
        self.assertEqual((s["moat"], s["total"]), (19, 14))
        self.assertIsInstance(s["moat"], int)

    def test_fmt_score(self):
        self.assertEqual([fmt_score(v) for v in (None, 4, 4.0, 4.5, -2.5)], ["—", "4", "4", "4.5", "-2.5"])


if __name__ == "__main__":
    unittest.main()
