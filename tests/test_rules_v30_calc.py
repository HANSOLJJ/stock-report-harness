# 규칙 v3.0 연속값 계산(계획 S3) — 곡선 기준점·반올림·⑥ 상장·비상장·⑨ 게이트·⑧ 배수·합산 정리를 잠그고 옛 규칙 결과가 그대로인지 본다
from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard.aggregate import _score_sum  # noqa: E402
from scorecard.calc_f6 import compute_f6  # noqa: E402
from scorecard.calc_f9 import compute_f9  # noqa: E402
from scorecard.calc_qual import compute_f8  # noqa: E402
from scorecard.inputs import JudgmentLookup, ObsLookup  # noqa: E402
from scorecard.rules import RULES_DIR, RuleSet, load_rules, piecewise  # noqa: E402

V30 = load_rules("v3.0")
V21 = load_rules("v2.1")
PARENT = {"ownership_scope": "parent_attributable"}


def company(listed: bool = True) -> dict:
    base = {"company_id": "acme", "display_name": "Acme", "aliases": [], "type": "업무", "listed": True, "ticker": "ACME",
            "exchange": "NASDAQ", "share_basis": "common", "adr_ratio": None, "reporting_currency": "USD", "scope": "test"}
    if not listed:
        base.update({"listed": False, "ticker": None, "exchange": None, "share_basis": "private"})
    return base


def obs(metric: str, value, *, basis: dict | None = None, kind: str = "actual", missing_type: str | None = None) -> dict:
    item = {"observation_id": f"acme.{metric}.t", "company_id": "acme", "metric": metric, "value": value, "unit": "USD",
            "as_of": "2026-10-12", "kind": kind, "source_id": "SRC-t", "status": "verified" if value is not None else "not_disclosed",
            "period": {"start": "2025-07-01", "end": "2026-06-30"}, "basis": basis, "raw": None, "note": None}
    if missing_type:
        item["missing_type"] = missing_type
    return item


def listed_obs(*, market_cap=2000.0, net_income=40.0, revenue=130.0, revenue_prior=100.0, pretax=None, operating_income=None):
    items = [obs("market_cap", market_cap), obs("net_cash", 0.0), obs("net_income_ttm", net_income, basis=PARENT),
             obs("revenue_ttm", revenue, basis={"period_basis": "ttm"}),
             obs("revenue_ttm_prior", revenue_prior, basis={"period_basis": "ttm"})]
    if pretax is not None:
        items.append(obs("pretax_income_ttm", pretax))
    if operating_income is not None:
        items.append(obs("operating_income_ttm", operating_income))
    return ObsLookup(items)


def run(version: str, decisions: dict[str, str] | None = None) -> dict:
    return {"run_id": "t", "rule_version": version, "as_of": "2026-10-12",
            "decisions": [{"id": k, "choice": v} for k, v in (decisions or {}).items()]}


def judgment(factor: str, kind: str, inputs: dict) -> dict:
    return {"judgment_id": f"acme.{factor}", "company_id": "acme", "factor": factor, "kind": kind, "score": None,
            "inputs": inputs, "evidence": ["시험"], "reviewer": "tester", "reviewed_at": "2026-10-12", "status": "new"}


class PiecewiseTest(unittest.TestCase):
    def check(self, curve: dict, cases: list[tuple[float, float]]) -> None:
        for x, want in cases:
            with self.subTest(x=x):
                self.assertAlmostEqual(piecewise(curve, x), want, places=9)

    def test_p1_halves_every_doubling(self):
        self.check(V30.f6["parameters"]["P1"]["curve"],
                   [(0, 0), (0.5, 0), (1, 0), (2 ** 0.5, -2), (2, -4), (4, -8), (8, -12), (16, -12)])

    def test_p2_points(self):
        self.check(V30.f6["parameters"]["P2"]["curve"], [(4, 0), (8, 0), (14, -2), (20, -4), (30, -6), (40, -8), (50, -8)])

    def test_f9_runway_coverage_loss(self):
        self.check(V30.f9["g3_runway_curve"], [(0, -8), (0.5, -6), (1, -4), (2, -2), (3, 0), (5, 0)])
        self.check(V30.f9["g4_coverage_curve"], [(0, -4), (0.5, -2), (1, 0), (2, 0)])
        self.check(V30.f9["g1_loss_curve"], [(0, -8), (0.15, -12), (0.30, -16), (0.5, -16)])

    def test_acceleration_examples_from_rules_md(self):
        curve = V30.payload["factors"]["F3"]["acceleration"]["curve"]
        for ratio, want in ((1.480 / 1.409, 4.51), (2.166 / 2.180, 2.81), (13 / 9, 6), (3.1 / 3.3, 1.18), (0.9, 0), (1.0, 3)):
            with self.subTest(ratio=ratio):
                self.assertEqual(V30.round_score(piecewise(curve, ratio)), want)


class RoundScoreTest(unittest.TestCase):
    def test_v30_rounds_once_half_up(self):
        for value, want in ((12.6049, 12.6), (12.605, 12.61), (12.0, 12), (-11.995, -12), (-5.408, -5.41)):
            with self.subTest(value=value):
                got = V30.round_score(value)
                self.assertEqual(got, want)
                self.assertIs(type(got), type(want))

    def test_old_rules_return_the_value_untouched(self):
        self.assertEqual(V21.round_score(4.123456), 4.123456)
        self.assertIsNone(V30.round_score(None))


class F6ListedContinuousTest(unittest.TestCase):
    def f6(self, rules=V30, **kw) -> dict:
        return compute_f6(company(), listed_obs(**kw), JudgmentLookup([]), rules, run(rules.version))

    def test_per_over_growth_and_ev_sales_are_continuous(self):
        # PER 2000/40 = 50, 성장 30% → x = 1.667 → −4·log2(1.667) = −2.95. EV/매출 2000/130 = 15.4 → −2.46. 합 −5.41.
        r = self.f6()
        p1, p2 = r["calc"]["parameters"]["P1"], r["calc"]["parameters"]["P2"]
        self.assertAlmostEqual(p1["value"], 50 / 30)
        self.assertAlmostEqual(p1["score"], -2.9475, places=3)
        self.assertAlmostEqual(p2["score"], -4 * (2000 / 130 - 8) / 12)
        self.assertEqual(r["score"], -5.41)
        self.assertTrue(p1["boundary"]["continuous"])
        self.assertFalse(any("경계 ⚠️" in w for w in r["warnings"]))

    def test_floor_minus_twenty(self):
        # P1 −12(이익 0 이하) + P2 −8(EV/매출 495배) = −20 이라 아직 하한 절단은 아니다
        r = self.f6(net_income=-1.0, market_cap=50000.0, revenue=101.0)
        self.assertEqual(r["calc"]["parameters"]["P1"]["score"], -12)
        self.assertEqual(r["score"], -20)
        self.assertNotIn("floor_applied", r["calc"])
        # 여기에 P4 −4 가 더해지면 −24 → −20 으로 자른다
        cut = self.f6(net_income=70.0, pretax=100.0, operating_income=30.0, market_cap=50000.0, revenue=101.0)
        self.assertEqual((cut["calc"]["subtotal_before_p4"], cut["score"]), (-20, -20))
        self.assertTrue(cut["calc"]["floor_applied"])

    def test_p4_is_minus_four_once(self):
        # 영업외 비중 (100 − 30) ÷ 100 = 0.7 → P4. 지분 평가손익 관측이 없어 P1 은 조정하지 않는다.
        r = self.f6(net_income=70.0, pretax=100.0, operating_income=30.0)
        self.assertEqual(r["calc"]["p4"]["demotion_steps"], 4)
        self.assertEqual(r["score"], V30.round_score(r["calc"]["subtotal_before_p4"] - 4))

    def test_no_five_percent_cliff_but_zero_growth_is_floor(self):
        # 2026-10-15 사용자 결정: 성장 3% 는 곡선이 정한다. PER 10 ÷ 3 = 3.33 → −4·log2(3.33) = −6.95. 옛 규칙은 5% 절벽이다.
        r = self.f6(market_cap=400.0, revenue=103.0)
        p1 = r["calc"]["parameters"]["P1"]
        self.assertAlmostEqual(p1["score"], -6.947, places=2)
        self.assertNotIn("미만", str(p1.get("band")))
        self.assertTrue(self.f6(rules=V21, market_cap=400.0, revenue=103.0)["calc"]["parameters"]["P1"]["band"].startswith("성장 5% 미만"))
        for revenue in (100.0, 99.0):   # 성장 0%·−1% 는 PER 을 성장으로 나눌 수 없어 −12
            with self.subTest(revenue=revenue):
                p1 = self.f6(market_cap=400.0, revenue=revenue)["calc"]["parameters"]["P1"]
                self.assertEqual((p1["score"], p1["band"]), (-12, "성장 0% 이하"))

    def test_newly_listed_track_takes_no_p4_for_its_own_data_shortage(self):
        # 2026-10-15 사용자 결정: 신규 상장 트랙은 이력 부족·분기 기준을 이미 반영한다. SpaceX 는 −8 → −12 였다.
        from tests.test_scorecard_f6_v17 import f6obs
        obs = f6obs(market_cap=1000.0, net_cash=0.0, net_income=-50.0, revenue=100.0, revenue_prior=80.0, period_basis="quarterly_yoy")
        r = compute_f6(company(), obs, JudgmentLookup([]), V30, run("v3.0"))
        self.assertEqual(r["calc"]["track"], "listed_newly")
        self.assertEqual((r["calc"]["p4"]["conditions_hit"], r["calc"]["p4"]["demotion_steps"]), ([], 0))
        # 이력 부족은 트랙 자동 목록에서 뺐고, 관측이 판정하는 분기 기준은 걸린 뒤 트랙이 덜어 낸다
        self.assertEqual(r["calc"]["p4"]["conditions_excluded_by_track"], ["period_basis_not_ttm"])
        old = compute_f6(company(), obs, JudgmentLookup([]), V21, run("v2.1"))
        self.assertGreater(old["calc"]["p4"]["demotion_steps"], 0, "옛 규칙은 그대로 깎는다")

    def test_same_inputs_under_v21_stay_integer_bands(self):
        r = self.f6(rules=V21)
        self.assertEqual((r["calc"]["parameters"]["P1"]["score"], r["calc"]["parameters"]["P2"]["score"], r["score"]), (-1, -1, -2))
        self.assertIs(type(r["score"]), int)


class F6PrivateContinuousTest(unittest.TestCase):
    def f6(self, rules=V30, *, ps=40.0, rng=None, revenue=None, prior=None) -> dict:
        items = [obs("ps_ratio", ps, basis={"estimate_range": rng} if rng else None, kind="estimate")]
        if revenue is not None:
            items.append(obs("revenue_ttm", revenue))
        if prior is not None:
            items.append(obs("revenue_ttm_prior", prior))
        return compute_f6(company(listed=False), ObsLookup(items), JudgmentLookup([]), rules,
                          run(rules.version, {"C-12": "growth_adjusted_ps"}))

    def test_growth_adjusted_continuous(self):
        # 40 ÷ (30% × 100) = 1.333 → −8 − 4·log2(1.333) = −9.66
        r = self.f6(revenue=130.0, prior=100.0)
        self.assertEqual(r["score"], -9.66)
        self.assertEqual(r["calc"]["growth_adjusted"]["path"], "growth_adjusted")

    def test_ceiling_minus_eight(self):
        r = self.f6(ps=10.0, revenue=200.0, prior=100.0)          # 10 ÷ 100 = 0.1 → 첫 기준점 −8
        self.assertEqual(r["score"], -8)

    def test_fallback_without_revenue_uses_ps_curve(self):
        r = self.f6(ps=41.24)                                       # 30배 −12 와 100배 −20 사이 → −13.28
        self.assertEqual((r["score"], r["calc"]["growth_adjusted"]["path"]), (-13.28, "fallback_private_bands"))

    def test_range_needs_a_rule_choice(self):
        payload = copy.deepcopy(V30.payload)
        del payload["policies"]["f6"]["estimate_range_end"]
        undecided = RuleSet(payload, RULES_DIR / "v3.0.json")
        r = self.f6(rules=undecided, rng=[30.0, 50.0], revenue=130.0, prior=100.0)
        self.assertEqual(r["status"], "needs_rule_decision")
        self.assertIn("estimate_range_end", r["pending"]["message"])

    def test_range_mid_is_the_score_at_the_middle_multiple(self):
        # 2026-10-14 사용자 결정: v3.0 은 범위의 가운데 배수로 잰다. 20~60 의 가운데 40 → 40 ÷ 30 = 1.333 → −9.66
        self.assertEqual(V30.f6["estimate_range_end"], "mid")
        r = self.f6(ps=40.0, rng=[20.0, 60.0], revenue=130.0, prior=100.0)
        self.assertEqual((r["status"], r["score"]), ("ok", -9.66))
        self.assertEqual(r["calc"]["growth_adjusted"]["estimate_range"]["picked"], "범위 가운데 배수")
        # 두 끝 점수의 평균(−8·log 축의 비대칭 때문에 다르다)이 아니다
        ends = [V30.round_score(piecewise(V30.f6["private_growth_adjusted"]["curve"], x / 30)) for x in (20.0, 60.0)]
        self.assertNotEqual(r["score"], V30.round_score(sum(ends) / 2))
        fallback = self.f6(ps=40.0, rng=[20.0, 60.0])            # 성장 자료가 없으면 P/S 곡선의 가운데 배수
        self.assertEqual((fallback["status"], fallback["score"]), ("ok", V30.round_score(V30.f6_private_score(40.0)[0])))

    def test_range_end_choice_picks_that_end(self):
        payload = copy.deepcopy(V30.payload)
        payload["policies"]["f6"]["estimate_range_end"] = "low"
        chosen = RuleSet(payload, RULES_DIR / "v3.0.json")
        r = self.f6(rules=chosen, rng=[30.0, 50.0], revenue=130.0, prior=100.0)
        self.assertEqual(r["status"], "ok")
        self.assertEqual(r["score"], V30.round_score(piecewise(V30.f6["private_growth_adjusted"]["curve"], 30 / 30)))
        self.assertEqual(r["calc"]["growth_adjusted"]["estimate_range"]["picked"], "낮은 끝 배수")

    def test_v21_range_behaviour_unchanged(self):
        self.assertEqual(self.f6(rules=V21, rng=[31.0, 50.0], revenue=130.0, prior=100.0)["score"], -3)


class F9ContinuousTest(unittest.TestCase):
    def f9(self, *items: dict, gi: dict | None = None, decisions: dict | None = None, rules=V30) -> dict:
        inputs = {"fcf_trend": "unknown", "bep_retreat": "no", "buffer_erosion": "no", "direction_A": "unknown",
                  "direction_B": "unknown", "coverage_comparable": "unknown"}
        inputs.update(gi or {})
        return compute_f9(company(), ObsLookup(list(items)), JudgmentLookup([judgment("F9", "gate_inputs", inputs)]),
                          rules, run(rules.version, decisions))

    def test_loss_ratio_is_continuous_without_c06(self):
        r = self.f9(obs("operating_margin_ttm", -0.15), obs("fcf_ttm", -1e9), obs("cash", 100e9),
                    decisions={"C-05": "diagnose_only"})
        self.assertEqual(r["score"], -12)
        g1 = next(p for p in r["calc"]["path"] if p.get("gate") == "G1" and "score" in p)
        self.assertEqual(g1["band"], "연속값(g1_loss_curve)")

    def test_v21_still_asks_for_c06(self):
        r = self.f9(obs("operating_margin_ttm", -0.15), obs("fcf_ttm", -1e9), obs("cash", 100e9),
                    decisions={"C-05": "diagnose_only"}, rules=V21)
        self.assertEqual(r["status"], "needs_rule_decision")

    def test_runway_and_coverage_add_continuously(self):
        # G2 −8, 런웨이 20 ÷ 10 = 2년 → −2, 커버리지 5 ÷ 10 = 0.5배 → −2. 합 −12.
        r = self.f9(obs("operating_margin_ttm", 0.1), obs("fcf_ttm", -10e9), obs("cash", 20e9),
                    obs("contracted_revenue", 5e9), obs("offbalance_B", 10e9), gi={"coverage_comparable": "yes"})
        self.assertEqual(r["score"], -12)
        g3 = next(p for p in r["calc"]["path"] if p.get("gate") == "G3")
        self.assertEqual((g3["step"], g3["boundary"]["continuous"]), (-2, True))

    def test_confirmed_undisclosed_is_minus_four(self):
        r = self.f9(obs("operating_margin_ttm", 0.1), obs("fcf_ttm", -10e9), obs("cash", 60e9),
                    obs("contracted_revenue", 5e9), obs("offbalance_B", None, missing_type="not_disclosed_confirmed"),
                    gi={"coverage_comparable": "yes"}, decisions={"C-16": "downgrade"})
        self.assertEqual(r["score"], -12)                 # G2 −8, 런웨이 6년 0, 확인된 미공시 −4

    def test_positive_deteriorating_path_shows_policy_score(self):
        r = self.f9(obs("operating_margin_ttm", 0.3), obs("fcf_ttm", 50e9), gi={"fcf_trend": "deteriorating"})
        self.assertEqual(r["score"], -4)
        self.assertEqual(r["calc"]["path"][-1]["score"], -4)

    def test_floor_minus_sixteen(self):
        r = self.f9(obs("operating_margin_ttm", -0.6), obs("fcf_ttm", -1e9), obs("cash", 100e9),
                    decisions={"C-05": "diagnose_only"})
        self.assertEqual(r["score"], -16)


class F8MultiplierTest(unittest.TestCase):
    def inputs(self) -> dict:
        return {"customer": {"status": "absent_disclosed"}, "commitment": {"status": "absent_disclosed"},
                "supply": {"status": "confirmed", "rung": -3}, "geopolitics": {"status": "confirmed", "rung": -1}}

    def test_rung_times_four(self):
        r = compute_f8(company(), JudgmentLookup([judgment("F8", "axes", self.inputs())]), V30)
        self.assertEqual((r["score"], r["calc"]["rung"], r["calc"]["score_multiplier"]), (-12, -3, 4))
        self.assertEqual(r["calc"]["deciding_axes"], ["supply"])

    def test_v21_has_no_multiplier(self):
        r = compute_f8(company(), JudgmentLookup([judgment("F8", "axes", self.inputs())]), V21)
        self.assertEqual(r["score"], -3)
        self.assertNotIn("rung", r["calc"])


class ScoreSumTest(unittest.TestCase):
    def test_float_noise_is_removed(self):
        self.assertEqual(_score_sum([12.3, 8.4, 10.1, 20, 10]), 60.8)
        self.assertEqual(_score_sum([0.1, 0.2]), 0.3)

    def test_integers_and_halves_unchanged(self):
        self.assertEqual(_score_sum([4, 3, 2.5, 0.5]), 10)

    def test_adjusted_total_has_no_float_noise(self):
        # 2026-10-15: 시범 실행 Apple 의 과점 44.7 + 함정 −22.48 이 22.220000000000002 로 저장됐다
        from scorecard.aggregate import summarize_company
        scores = dict(zip(("F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9"), (12.27, 4, 3.43, 16, 9, -6.48, 0, -16, 0)))
        factors = {f: {"score": s, "status": "ok", "pending": None} for f, s in scores.items()}
        company = {"company_id": "apple", "display_name": "Apple", "type": "소비자", "listed": True}
        s = summarize_company(company, factors)
        self.assertEqual((s["moat"], s["trap"], s["total"]), (44.7, -22.48, 22.22))
        self.assertEqual(repr(s["total"]), "22.22")
        self.assertIs(type(_score_sum([4, 3])), int)
        self.assertEqual(_score_sum([4, 0.5]), 4.5)


if __name__ == "__main__":
    unittest.main()
