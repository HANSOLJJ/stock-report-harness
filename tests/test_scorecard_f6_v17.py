# F6 v1.7 파라미터 모드(P1 PER·P2 EV/Sales·P3 성장률·P4 입력신뢰도) 계산기 고정 테스트
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard.calc_f6 import compute_f6  # noqa: E402
from scorecard.inputs import JudgmentLookup, ObsLookup  # noqa: E402
from scorecard.rules import load_rules  # noqa: E402
from scorecard.schema import SchemaError  # noqa: E402

RULES_V15 = load_rules("v1.5")
RULES_V16 = load_rules("v1.6")

# v1.7 은 지금 F9 정책-range 정합 검사에 걸려 로드되지 않는다(MISS-LABEL-23 과제 3).
# factors.F9.range 를 [-4,0] 으로 바꾸면서 policies.f9 를 그대로 둔 F6-SPEC-18 의 결함이다.
# **밴드를 임의로 고쳐 통과시키지 않는다** — 재척도는 C-06 결정 사항이다.
# 그래서 F6 회귀는 막힌 동안 skip 하고, 막혔다는 사실 자체를 아래에서 테스트로 고정한다.
try:
    RULES_V17 = load_rules("v1.7")
    V17_BLOCK: str | None = None
except SchemaError as exc:
    RULES_V17 = None
    V17_BLOCK = str(exc)

_SKIP = f"v1.7 이 F9 정책-range 검사에 걸려 로드 불가 (C-06 결정 대기): {V17_BLOCK}"


def company(cid: str = "acme", listed: bool = True, share_basis: str | None = None) -> dict:
    return {
        "company_id": cid, "display_name": cid.title(), "aliases": [], "type": "업무",
        "listed": listed, "ticker": "ACME" if listed else None,
        "exchange": "NASDAQ" if listed else None,
        "share_basis": share_basis or ("common" if listed else "private"),
        "adr_ratio": None, "reporting_currency": "USD", "scope": "test",
    }


PARENT = {"ownership_scope": "parent_attributable"}


def obs(metric: str, value, cid: str = "acme", basis: dict | None = None, kind: str = "actual") -> dict:
    return {
        "observation_id": f"{cid}.{metric}.t", "company_id": cid, "metric": metric,
        "value": value, "unit": "USD", "as_of": "2026-09-10", "kind": kind,
        "source_id": "SRC-t", "status": "verified", "period": None, "basis": basis,
        "raw": None, "note": None,
    }


def run() -> dict:
    return {"run_id": "t", "rule_version": "v1.7", "decisions": []}


def f6obs(cid: str = "acme", *, market_cap=1000.0, net_income=50.0, net_cash=0.0,
          revenue=100.0, revenue_prior=80.0, operating_income=None, pretax="auto",
          period_basis: str | None = "ttm", nonop_share=None) -> ObsLookup:
    """v1.7 F6 입력. None 을 넘기면 그 관측을 아예 만들지 않는다.

    `pretax` 를 안 주면 `operating_income` 이 있을 때만 `net_income` 과 같게 둔다 —
    세금이 0 인 회사를 뜻하고, 그러면 `nonop_share` 가 정정 전 산식과 같은 값이 나와
    기존 케이스의 의도가 유지된다.
    """
    items = []

    def add(metric, value, basis=None):
        if value is not None:
            items.append(obs(metric, value, cid=cid, basis=basis))

    add("market_cap", market_cap)
    add("net_cash", net_cash)
    # 2026-09-15 FIX-54 1단계 FC-04: P1 분자는 모회사 귀속 순이익이어야 한다 — verified 관측은 범위를 밝힌다.
    add("net_income_ttm", net_income, PARENT)
    add("operating_income_ttm", operating_income)
    # "auto" 는 안 준 것이고 None 은 **일부러 없앤 것**이다. 둘을 가른다.
    add("pretax_income_ttm",
        (net_income if operating_income is not None else None) if pretax == "auto" else pretax)
    add("nonop_share", nonop_share)
    rev_basis = {"period_basis": period_basis} if period_basis else {}
    add("revenue_ttm", revenue, rev_basis)
    add("revenue_ttm_prior", revenue_prior, rev_basis)
    return ObsLookup(items)


@unittest.skipIf(RULES_V17 is None, _SKIP)
class TestF6ParameterBands(unittest.TestCase):
    """반개방 구간. P1·P2 는 upper 미만, P3 는 lower 이상이다."""

    def test_p1_boundaries(self):
        for value, want in ((24.99, 0), (25.0, -1), (44.99, -1), (45.0, -2), (370.0, -2)):
            self.assertEqual(RULES_V17.f6_parameter_band("P1", value)[0], want, msg=f"P1 {value}")

    def test_p2_boundaries(self):
        for value, want in ((7.99, 0), (8.0, -1), (19.99, -1), (20.0, -2)):
            self.assertEqual(RULES_V17.f6_parameter_band("P2", value)[0], want, msg=f"P2 {value}")

    def test_p3_boundaries_are_lower_inclusive(self):
        """P3 만 이상이다. 30% 는 0 점이고 29.99% 는 -1 이다."""
        for value, want in ((0.834, 0), (0.30, 0), (0.2999, -1), (0.15, -1),
                            (0.1499, -2), (0.05, -2), (0.0499, -3), (-0.10, -3)):
            self.assertEqual(RULES_V17.f6_parameter_band("P3", value)[0], want, msg=f"P3 {value}")

    def test_parameter_minimums_match_factor_range(self):
        """파라미터 합계 하한이 factors.F6.range 하한과 같아야 배점 재배분이 규칙 안에서 검산된다."""
        total = sum(spec["score_range"][0] for spec in RULES_V17.f6_parameters().values())
        self.assertEqual(total, RULES_V17.factor_range("F6")[0])
        self.assertEqual(total, -7)

    def test_trap_sum_preserved(self):
        traps = sum(RULES_V17.factor_range(f)[0] for f in ("F6", "F7", "F8", "F9"))
        self.assertEqual(traps, -18)
        self.assertEqual(traps, RULES_V17.payload["scoring"]["trap_min_active"])


@unittest.skipIf(RULES_V17 is None, _SKIP)
class TestF6Tracks(unittest.TestCase):
    """트랙은 선언된 기간 기준으로 정한다. 자료가 없다고 무른 트랙으로 내려보내지 않는다."""

    def test_listed_ttm_scores(self):
        r = compute_f6(company(), f6obs(), JudgmentLookup([]), RULES_V17, run())
        self.assertEqual(r["status"], "ok")
        self.assertEqual(r["calc"]["track"], "listed_ttm")

    def test_adr_uses_annual_track_and_auto_p4(self):
        c = company(cid="tsmc", share_basis="adr")
        r = compute_f6(c, f6obs("tsmc", period_basis="annual"), JudgmentLookup([]), RULES_V17, run())
        self.assertEqual(r["calc"]["track"], "listed_annual")
        self.assertIn("period_basis_not_ttm", r["calc"]["p4"]["conditions_hit"])
        self.assertEqual(r["calc"]["p4"]["demotion_steps"], 1)

    def test_newly_listed_track_uses_p3_only(self):
        r = compute_f6(company(cid="spx"), f6obs("spx", period_basis="quarterly_yoy"),
                       JudgmentLookup([]), RULES_V17, run())
        self.assertEqual(r["calc"]["track"], "listed_newly")
        self.assertNotIn("P1", r["calc"]["parameters"])
        self.assertIn("short_history", r["calc"]["p4"]["conditions_hit"])

    def test_basis_mismatch_is_pending_not_silent(self):
        """ADR 인데 관측이 ttm 이라고 선언하면 조용히 넘기지 않는다."""
        c = company(cid="tsmc", share_basis="adr")
        r = compute_f6(c, f6obs("tsmc", period_basis="ttm"), JudgmentLookup([]), RULES_V17, run())
        self.assertIsNone(r["score"])
        self.assertEqual(r["status"], "pending_data")
        self.assertIn("기준 불일치", r["pending"]["message"])

    def test_missing_basis_is_pending(self):
        r = compute_f6(company(), f6obs(period_basis=None), JudgmentLookup([]), RULES_V17, run())
        self.assertIsNone(r["score"])
        self.assertIn("period_basis", r["pending"]["message"])

    def test_missing_input_does_not_demote_track(self):
        """입력이 없으면 pending 이다. 더 무른 신규상장 트랙으로 내려가 점수를 받지 않는다."""
        r = compute_f6(company(), f6obs(net_income=None), JudgmentLookup([]), RULES_V17, run())
        self.assertIsNone(r["score"])
        self.assertEqual(r["calc"]["track"], "listed_ttm")
        self.assertIn("net_income_ttm", r["pending"]["message"])


@unittest.skipIf(RULES_V17 is None, _SKIP)
class TestF6ParameterGuards(unittest.TestCase):

    def test_non_positive_net_income_is_pending_not_low_per(self):
        """적자면 PER 이 음수가 된다. 낮은 PER·0 점으로 대체하지 않는다."""
        r = compute_f6(company(), f6obs(net_income=-10.0), JudgmentLookup([]), RULES_V17, run())
        self.assertIsNone(r["score"])
        self.assertIn("0 이하", r["pending"]["message"])

    def test_ev_subtracts_net_cash_from_market_cap(self):
        """차입이 있으면(순현금 음수) EV 가 시총보다 크다. oracle 이 그 사례다."""
        r = compute_f6(company(), f6obs(net_cash=-200.0, revenue=100.0), JudgmentLookup([]), RULES_V17, run())
        self.assertAlmostEqual(r["calc"]["parameters"]["P2"]["value"], 12.0)

    def test_p3_uses_prior_revenue(self):
        r = compute_f6(company(), f6obs(revenue=130.0, revenue_prior=100.0), JudgmentLookup([]), RULES_V17, run())
        self.assertAlmostEqual(r["calc"]["parameters"]["P3"]["value"], 0.30)
        self.assertEqual(r["calc"]["parameters"]["P3"]["score"], 0)

    def test_boundary_flag_is_display_only(self):
        """경계 ±3% 는 표시다. 점수를 바꾸지 않는다."""
        r = compute_f6(company(), f6obs(market_cap=2480.0, net_income=100.0),
                       JudgmentLookup([]), RULES_V17, run())
        p1 = r["calc"]["parameters"]["P1"]
        self.assertAlmostEqual(p1["value"], 24.8)
        self.assertTrue(p1["boundary"]["flag"])
        self.assertEqual(p1["score"], 0)


@unittest.skipIf(RULES_V17 is None, _SKIP)
class TestF6P4(unittest.TestCase):
    """P4 는 소계에 한 칸만 걸린다. 여럿 걸려도 한 칸이다."""

    def test_nonop_share_is_nonoperating_over_pretax(self):
        """**영업외손익 ÷ 세전이익** 이다.

        정정 전에는 `(순이익 − 영업이익) / 순이익` 이었다. 그 산식은 분자에서 법인세를 안 되더해
        영업외 항목이 없는 흑자 납세 기업의 부호를 뒤집었고, 분모도 세전이 아니었다. 저장값 12건을
        보존 원자료로 역산해 **저장값이 옳고 재계산이 틀렸다**는 것이 확인됐다(NONOP-44).
        """
        r = compute_f6(company(), f6obs(pretax=100.0, operating_income=40.0),
                       JudgmentLookup([]), RULES_V17, run())
        p4 = r["calc"]["p4"]
        self.assertAlmostEqual(p4["nonop_share"], 0.60)      # (100 - 40) / 100
        self.assertEqual(p4["nonop_share_source"], "recomputed")
        self.assertIn("nonop_share", p4["conditions_hit"])

    def test_tax_no_longer_leaks_into_the_numerator(self):
        """세금만 있고 영업외 항목이 없는 회사는 **0 이어야** 한다. 옛 산식은 음수를 냈다."""
        r = compute_f6(company(), f6obs(net_income=70.0, pretax=100.0, operating_income=100.0),
                       JudgmentLookup([]), RULES_V17, run())
        self.assertAlmostEqual(r["calc"]["p4"]["nonop_share"], 0.0)
        self.assertNotIn("nonop_share", r["calc"]["p4"]["conditions_hit"])
        # 옛 산식이었다면 (70-100)/70 = -0.4286 으로 임계를 넘어 강등됐다.

    def test_recompute_disagreement_is_warned_not_hidden(self):
        r = compute_f6(company(), f6obs(pretax=100.0, operating_income=40.0, nonop_share=0.10),
                       JudgmentLookup([]), RULES_V17, run())
        self.assertTrue(any("저장값" in w for w in r["warnings"]))
        self.assertEqual(r["calc"]["p4"]["nonop_share_source"], "recomputed")

    def test_no_pretax_means_no_value_not_the_old_formula(self):
        """**세전이익이 없으면 값을 만들지 않는다.** 틀린 산식으로 되돌아가지 않는다."""
        r = compute_f6(company(), f6obs(net_income=100.0, operating_income=40.0, pretax=None,
                                        nonop_share=0.55), JudgmentLookup([]), RULES_V17, run())
        p4 = r["calc"]["p4"]
        self.assertIsNone(p4["nonop_share"])
        self.assertEqual(p4["nonop_share_source"], "unavailable")
        self.assertNotIn("nonop_share", p4["conditions_hit"])
        self.assertTrue(any("쓰지 않는다" in w for w in r["warnings"]))

    def test_negative_pretax_warns_that_the_sign_is_undefined(self):
        """적자 기업은 분모가 음수라 **정정해도 부호 규약이 서지 않는다.**"""
        r = compute_f6(company(), f6obs(pretax=-100.0, operating_income=-40.0),
                       JudgmentLookup([]), RULES_V17, run())
        self.assertTrue(any("부호 규약" in w for w in r["warnings"]))

    def test_multiple_conditions_still_one_step(self):
        c = company(cid="tsmc", share_basis="adr")
        r = compute_f6(c, f6obs("tsmc", period_basis="annual", pretax=100.0, operating_income=40.0),
                       JudgmentLookup([]), RULES_V17, run())
        self.assertEqual(len(r["calc"]["p4"]["conditions_hit"]), 2)
        self.assertEqual(r["calc"]["p4"]["demotion_steps"], 1)

    def test_floor_clamps_after_demotion(self):
        """P1 -2, P2 -2, P3 -3 에 P4 한 칸이면 -8 이지만 트랙 하한 -7 로 절단된다."""
        r = compute_f6(company(), f6obs(market_cap=1e6, net_income=100.0, pretax=100.0,
                                        operating_income=10.0,
                                        net_cash=0.0, revenue=100.0, revenue_prior=200.0),
                       JudgmentLookup([]), RULES_V17, run())
        self.assertEqual(r["calc"]["subtotal_before_p4"], -7)
        self.assertEqual(r["score"], -7)
        self.assertTrue(r["calc"]["floor_applied"])

    def test_newly_listed_floor_is_minus_three(self):
        r = compute_f6(company(cid="spx"), f6obs("spx", period_basis="quarterly_yoy",
                                                 revenue=100.0, revenue_prior=200.0),
                       JudgmentLookup([]), RULES_V17, run())
        self.assertEqual(r["calc"]["parameters"]["P3"]["score"], -3)
        self.assertEqual(r["score"], -3)


@unittest.skipIf(RULES_V17 is None, _SKIP)
class TestF6StaleAsOf(unittest.TestCase):
    """기준 시점 경과. **임계는 보고 주기에 상대적이다** — ttm·quarterly 6개월, annual 16개월.

    이 조건은 v1.7 에 선언돼 있었으나 `_p4()` 가 읽지 않았고 임계값도 없었다. 그래서 F6-REG-28
    직전까지 TSM 이 20개월 묵어 있는 동안 한 번도 걸리지 않았다. 선언에 소비자를 붙이고 여기서 고정한다.
    """

    def build(self, *, period_basis: str, end: str, as_of: str = "2026-09-02", cid: str = "acme",
              share_basis: str | None = None, **over):
        items = []

        def add(metric, value, basis=None, period=None):
            o = obs(metric, value, cid=cid, basis=basis)
            o["period"] = period
            items.append(o)

        add("market_cap", over.get("market_cap", 1000.0))
        add("net_cash", over.get("net_cash", 0.0))
        add("net_income_ttm", over.get("net_income", 50.0), PARENT)
        add("operating_income_ttm", over.get("operating_income", 49.0))
        per = {"start": "2025-01-01", "end": end}
        add("revenue_ttm", over.get("revenue", 100.0), {"period_basis": period_basis}, per)
        add("revenue_ttm_prior", over.get("revenue_prior", 80.0), {"period_basis": period_basis}, per)
        r = dict(run())
        r["as_of"] = as_of
        return compute_f6(company(cid=cid, share_basis=share_basis), ObsLookup(items),
                          JudgmentLookup([]), RULES_V17, r)

    def stale(self, result):
        return result["calc"]["p4"]["stale_asof"]

    def test_thresholds_are_declared_per_reporting_cycle(self):
        cond = {c["id"]: c for c in RULES_V17.f6_p4()["conditions"]}["stale_asof"]
        self.assertEqual(cond["thresholds_months"], {"ttm": 6, "quarterly": 6, "annual": 16})
        self.assertEqual(RULES_V17.f6_stale_months("ttm"), 6)
        self.assertEqual(RULES_V17.f6_stale_months("quarterly_yoy"), 6)   # basis_map 을 탄다
        self.assertEqual(RULES_V17.f6_stale_months("annual"), 16)

    def test_ttm_hits_over_six_months(self):
        ok = self.build(period_basis="ttm", end="2026-03-31")        # 5개월
        self.assertNotIn("stale_asof", ok["calc"]["p4"]["conditions_hit"])
        self.assertEqual(self.stale(ok)["months_elapsed"], 5)
        bad = self.build(period_basis="ttm", end="2026-01-31")       # 7개월
        self.assertIn("stale_asof", bad["calc"]["p4"]["conditions_hit"])
        self.assertTrue(any("기준 시점 경과" in w for w in bad["warnings"]))

    def test_boundary_is_strictly_greater(self):
        """'초과' 다. 정확히 6개월이면 걸리지 않는다."""
        six = self.build(period_basis="ttm", end="2026-03-02")
        self.assertEqual(self.stale(six)["months_elapsed"], 6)
        self.assertFalse(self.stale(six)["hit"])

    def test_annual_uses_sixteen_not_six(self):
        """**단일 임계는 안 된다.** 6 으로 두면 연간 신고자가 상시 걸려 FPI 를 두 번 깎는다."""
        r = self.build(period_basis="annual", end="2025-12-31", share_basis="adr")   # 8개월
        self.assertEqual(self.stale(r)["months_elapsed"], 8)
        self.assertEqual(self.stale(r)["limit_months"], 16)
        self.assertNotIn("stale_asof", r["calc"]["p4"]["conditions_hit"])
        # 같은 8개월을 ttm 기준으로 신고했다면 걸린다 — 임계가 주기에 상대적이라는 뜻이다.
        t = self.build(period_basis="ttm", end="2025-12-31")
        self.assertIn("stale_asof", t["calc"]["p4"]["conditions_hit"])

    def test_tsm_fy2024_would_have_been_caught(self):
        """**이 조건의 존재 이유다.** FY2024 였다면 20개월로 걸렸다."""
        r = self.build(period_basis="annual", end="2024-12-31", share_basis="adr")
        self.assertEqual(self.stale(r)["months_elapsed"], 20)
        self.assertTrue(self.stale(r)["hit"])
        # 그래도 P4 는 한 칸이다. period_basis_not_ttm 과 겹쳐도 두 번 깎지 않는다.
        self.assertEqual(set(r["calc"]["p4"]["conditions_hit"]), {"stale_asof", "period_basis_not_ttm"})
        self.assertEqual(r["calc"]["p4"]["demotion_steps"], 1)

    def test_skips_when_run_has_no_as_of(self):
        """기준일을 모르면 지어내지 않는다."""
        items = [obs(m, v, basis={"period_basis": "ttm"} if m == "revenue_ttm" else (PARENT if m == "net_income_ttm" else None))
                 for m, v in (("market_cap", 1000.0), ("net_cash", 0.0), ("net_income_ttm", 50.0),
                              ("revenue_ttm", 100.0), ("revenue_ttm_prior", 80.0))]
        r = compute_f6(company(), ObsLookup(items), JudgmentLookup([]), RULES_V17, run())
        self.assertFalse(r["calc"]["p4"]["stale_asof"]["checked"])
        self.assertNotIn("stale_asof", r["calc"]["p4"]["conditions_hit"])

    def test_current_run_has_nobody_stale(self):
        """현재 실행에서는 아무도 안 걸린다. **걸릴 일이 없는 것과 검사가 없는 것은 다르다.**"""
        import json
        run_dir = ROOT / "scorecard" / "runs" / "ai-scorecard-2026-09-obsreg"
        results = json.loads((run_dir / "results.json").read_text(encoding="utf-8"))
        checked, hit = 0, []
        for c in results["companies"]:
            stale = ((c["factors"]["F6"].get("calc") or {}).get("p4") or {}).get("stale_asof") or {}
            if stale.get("checked"):
                checked += 1
                self.assertLessEqual(stale["months_elapsed"], 8)
                if stale.get("hit"):
                    hit.append(c["company_id"])
        self.assertEqual(checked, 12, "상장 12개사 전부 검사돼야 한다 — 선언만 있고 안 읽히면 안 된다")
        self.assertEqual(hit, [])


@unittest.skipIf(RULES_V17 is None, _SKIP)
class TestF6Private(unittest.TestCase):
    """비상장은 배수를 계산하고, **C-12 확정 뒤로는 P2 로 점수도 낸다.**

    C-12 이전에는 밴드가 미정이라 점수를 만들지 않았다. 그 상태는
    `TestPrivateP2Guards.test_undecided_c12_still_pends`(test_scorecard_private.py)가
    밴드 선언을 지운 규칙으로 계속 고정한다.
    """

    def test_private_multiples_are_computed(self):
        items = [obs("post_money_valuation", 965e9, cid="anthropic"),
                 obs("arr", 65e9, cid="anthropic", kind="run_rate"),
                 obs("arr_prior", 47e9, cid="anthropic", kind="run_rate"),
                 obs("cumulative_raised", 125e9, cid="anthropic")]
        # FIX-52 로 compute_private 가 C-12 선택을 읽는다. 선택이 없으면 P2 검사 전에 needs_rule_decision 이라
        # 이 테스트가 보려는 'ps_ratio 없음 → arr 로 대체하지 않음' 에 닿으려면 구현된 선택을 넘겨야 한다.
        c12 = {**run(), "decisions": [{"id": "C-12", "choice": "p2_with_capped_promotion", "rationale": "t",
                                        "decided_by": "t", "decided_at": "2026-09-11"}]}
        r = compute_f6(company(cid="anthropic", listed=False), ObsLookup(items),
                       JudgmentLookup([]), RULES_V17, c12)
        m = r["calc"]["multiples"]
        self.assertAlmostEqual(m["post_money_over_arr"], 965 / 65)
        self.assertAlmostEqual(m["arr_growth"], 65 / 47 - 1)
        self.assertAlmostEqual(m["arr_over_cumulative_raised"], 65 / 125)
        # P2 입력(ps_ratio)이 없으므로 점수는 만들지 않는다 — arr 로 대체하지 않는다.
        self.assertIsNone(r["score"])
        self.assertEqual(r["status"], "pending_data")
        self.assertIn("arr 로 대체하지 않는다", r["pending"]["message"])

    def test_run_rate_kind_is_surfaced(self):
        """이름은 arr 인데 종류는 run_rate 다. 소비하는 쪽이 그 사실을 보게 한다."""
        items = [obs("arr", 65e9, cid="anthropic", kind="run_rate")]
        r = compute_f6(company(cid="anthropic", listed=False), ObsLookup(items),
                       JudgmentLookup([]), RULES_V17, run())
        self.assertTrue(any("런레이트" in n for n in r["calc"]["kind_notes"]))


class TestF6LegacyModeUnaffected(unittest.TestCase):
    """v1.5·v1.6 실행은 per_band 경로를 그대로 쓴다. v1.7 도입이 과거 실행을 바꾸지 않는다."""

    def test_mode_dispatch(self):
        self.assertEqual(RULES_V15.f6_mode, "per_band")
        self.assertEqual(RULES_V16.f6_mode, "per_band")
        if RULES_V17 is not None:
            self.assertEqual(RULES_V17.f6_mode, "parameters")

    def test_v15_still_scores_by_ntm_per(self):
        lookup = ObsLookup([obs("ntm_per", 25.0, basis={"method": "consensus_4q_sum"})])
        r = compute_f6(company(), lookup, JudgmentLookup([]), RULES_V15, run())
        self.assertEqual(r["status"], "ok")
        self.assertEqual(r["calc"]["ntm_per"], 25.0)
        self.assertNotIn("parameters", r["calc"])


@unittest.skipIf(RULES_V17 is None, _SKIP)
class TestF6FixRoundSpec(unittest.TestCase):
    """F6-FIX-21 로 확정된 규약이 규칙 파일에 남아 있는지 고정한다."""

    @classmethod
    def setUpClass(cls):
        cls.f6 = RULES_V17.f6
        cls.sources = RULES_V17.payload["sources"]

    def test_ttm_anchor_is_latest_available_quarter(self):
        w = self.f6["ttm_window"]
        self.assertEqual(w["anchor"], "latest_available_quarter_including_derived_q4")
        # 왜 다른 쪽이 아닌지가 남아야 다음 세션이 다시 흔들지 않는다.
        self.assertIn("3개월", w["why_not_latest_tagged_quarter"])
        self.assertIn("ORCL", w["why_not_latest_tagged_quarter"])
        self.assertIn("우연", w["why_not_latest_tagged_quarter"])

    def test_ttm_verification_rule_is_recorded(self):
        """4분기 합이 FY 태깅값과 같으면 복원값이 아니라 공시값이다 — 이것이 [A] 의 근거다."""
        self.assertIn("공시값", self.f6["ttm_window"]["verification"])

    def test_coalesce_is_per_period_not_per_company(self):
        c = self.f6["revenue_coalesce"]
        self.assertEqual(c["mode"], "per_period_fallback")
        self.assertTrue(c["record_provenance"])
        self.assertIn("기간마다", c["note"])
        self.assertGreaterEqual(len(c["priority"]), 3)

    def test_fx_separates_price_date_and_rate_date(self):
        """H.10 을 쓸 때는 시총 기준일과 환율 게시일을 나눠 남긴다.

        **F6-REG-28 에서 H.10 은 대체 경로가 됐다**(발행사 선언 환율 우선). 그래서 이 계약은
        `fallback_h10` 아래로 옮겨졌고, 옮겨졌을 뿐 없어지지 않았다는 것을 여기서 고정한다.
        """
        fb = self.f6["fx"]["fallback_h10"]
        self.assertEqual(fb["rate_source_host"], "www.federalreserve.gov")
        for key in ("price_date", "fx_rate_date", "fx_backfill_days"):
            self.assertIn(key, fb["date_fields"])

    def test_fx_backfill_limit_is_pending(self):
        """한도 없이 두면 무한 후퇴가 된다. 잠정값을 두되 확정이 아님을 표시한다."""
        fb = self.f6["fx"]["fallback_h10"]
        self.assertEqual(fb["backfill_limit_status"], "pending")
        self.assertIsInstance(fb["backfill_limit_days"], int)
        self.assertIn("잠정", fb["backfill_limit_note"])

    def test_fx_prefers_issuer_declared_rate(self):
        """**발행사 선언 환율이 먼저다.** H.10 은 선언이 없는 발행사에만 쓴다 (F6-REG-28 확정)."""
        fx = self.f6["fx"]
        self.assertEqual(fx["priority"], ["issuer_declared_convenience_rate", "h10_spot_at_price_date"])
        self.assertIn("발행사", fx["rule"])
        self.assertIn("f6-status-2026-09-10", fx["supersedes"])

    def test_fx_requires_same_rate_for_both_periods(self):
        """두 해에 서로 다른 환율을 쓰면 P3 성장률 밴드가 뜬다. 그 사례가 근거에 남아야 한다."""
        same = self.f6["fx"]["same_rate_for_both_periods"]
        self.assertIn("같은 환율", same["rule"])
        for token in ("6.8980", "7.2567", "32.79", "30.62", "한 칸"):
            self.assertIn(token, same["why"], f"{token} 근거가 빠졌다")

    def test_fx_records_that_skipping_conversion_breaks_p2(self):
        """P3 만의 문제가 아니라는 것을 규칙이 기억해야 한다."""
        note = self.f6["fx"]["no_conversion_breaks_p2"]
        self.assertIn("0.716", note)
        self.assertIn("두 칸", note)

    def test_h10_listed_with_permission_distinction(self):
        entry = next(e for e in self.sources["allowed"] if e["host"] == "www.federalreserve.gov")
        # 금지 없음과 명시 허가는 다르다. 그 구분이 note 에 남아야 한다.
        self.assertIn("금지 없음", entry["note"])
        self.assertIn("명시 허가", entry["note"])
        # 연방정부 저작물 원칙은 사이트 문서로 확인한 사실이 아니므로 근거로 쓰지 않는다.
        self.assertIn("등재 근거로 쓰지 않는다", entry["note"])

    def test_h10_note_records_why_and_crosscheck(self):
        """왜 이 출처인가와 교차 검증 대상이 남아야 한다.

        발행사가 실제로 쓰는 환율이라는 것이 채택 근거이고, 공시 환산치가 우리 조회를
        검산하는 기준이다. 둘 다 없으면 다음 세션이 출처를 다시 고르려 든다.
        """
        entry = next(e for e in self.sources["allowed"] if e["host"] == "www.federalreserve.gov")
        note = entry["note"]
        self.assertIn("왜 이 출처인가", note)
        self.assertIn("발행사가 실제로 쓰는 환율", note)
        self.assertIn("교차 검증 대상", note)
        # 공시 환산치 두 값과 각각의 기준일
        self.assertIn("31.37", note)
        self.assertIn("2025-12-31", note)
        self.assertIn("6.8980", note)
        self.assertIn("2026-03-31", note)
        # 같은 20-F 안에서도 항목마다 환율이 다르다는 단서
        self.assertIn("31.11", note)

    def test_three_sources_stay_not_adopted_after_narrowing(self):
        """**usage_scope 를 좁혀도 되살아나는 원천이 없다** (SCOPE-34, 2026-09-11).

        2026-09-10 은 '강등하지 말고 상태만 기록', 2026-09-11 오전은 합집합이라 '법인 배제로 하향',
        같은 날 오후는 personal 단독이라 '약관 사유는 해소'. **판단이 세 번 바뀐 것을 지우지 않는다.**
        해소된 뒤에도 셋 다 남는 사유가 있어 not_adopted 에 그대로 있다.
        """
        allowed = {e["host"] for e in self.sources["allowed"]}
        denied = {e["host"] for e in self.sources["denied"]}
        na = {e["host"]: e for e in self.sources["not_adopted"]}
        for host in ("financialmodelingprep.com", "finnhub.io", "www.alphavantage.co"):
            self.assertNotIn(host, allowed)
            self.assertNotIn(host, denied, "쓸 자격이 없는 것이 아니라 안 쓰기로 한 것이다")
            self.assertIn(host, na)
            self.assertIn("해소", na[host]["reopen_condition"], "약관 사유가 해소됐다는 사실이 있어야 한다")
        # 남은 사유의 **종류**가 정확해야 한다. 셋이 서로 다르다.
        self.assertEqual(na["www.alphavantage.co"]["reason_type"], "technical")
        self.assertEqual(na["financialmodelingprep.com"]["reason_type"], "technical")
        self.assertEqual(na["finnhub.io"]["reason_type"], "terms")
        self.assertEqual(na["data.nasdaq.com"]["reason_type"], "cost")

    def test_finnhub_is_the_only_one_with_terms_left(self):
        """Finnhub 만 약관 사유가 남는다 — 파생 결과 공유에 서면 승인이 필요하다."""
        entry = {e["host"]: e for e in self.sources["not_adopted"]}["finnhub.io"]
        self.assertIn("서면 승인", entry["reopen_condition"])
        self.assertIn("derived results", entry["reason"])

    def test_usage_scope_is_personal_only(self):
        """**세 번 되물은 건이다.** 확정값과 대체 관계가 선언에 남아야 한다."""
        scope = self.sources["usage_scope"]
        self.assertEqual(scope["scope"], "personal_internal_only")
        self.assertNotIn("scopes", scope, "scope 와 scopes 를 동시에 두지 않는다")
        self.assertIn("대체한다", scope["supersedes"])
        self.assertIn("corporate_internal_only", scope["supersedes"])
        self.assertIn("개인 사용조차 막는", scope["evaluation_rule"])

    def test_yahoo_is_denied_not_unlisted(self):
        """**SCOPE-34 검토에서 denied 로 확정됐다**(설계진행 2026-09-11).

        처음에는 `unlisted` 에 사유만 교체해 뒀다 — 지시가 `allowed` 로 올리는 것이었으므로
        `denied` 로 옮기는 것은 내가 정할 일이 아니라고 봤다. 검토에서 "제 지시가 잘못됐습니다"
        와 함께 `denied` 이전을 지시받았다. **판단 경위를 지우지 않고 여기 남긴다.**
        """
        denied = {e["host"]: e for e in self.sources["denied"]}
        allowed = {e["host"] for e in self.sources["allowed"]}
        unlisted = {e["host"] for e in self.sources.get("unlisted", [])}
        for host in ("query1.finance.yahoo.com", "query2.finance.yahoo.com"):
            self.assertIn(host, denied, "query2 도 별도 항목이어야 source_violation 이 잡는다")
            self.assertNotIn(host, allowed)
            self.assertNotIn(host, unlisted)
        entry = denied["query1.finance.yahoo.com"]
        # 사유가 둘 다 적혀 있어야 한다. 하나만 적으면 나머지가 해소됐을 때 오독된다.
        self.assertIn("Disallow: /", entry["reason"])
        self.assertIn("for any purpose", entry["reason"])
        self.assertIn("api.nasdaq.com", entry["note"], "같은 형태의 선례를 가리켜야 한다")

    def test_denied_note_records_the_pipeline_contradiction(self):
        """**정책은 금지하는데 프로젝트는 이미 쓴다.** 그 모순이 적혀 있어야 한다.

        다음 사람이 '왜 stock 은 쓰는데 scorecard 는 안 쓰나' 를 되묻지 않게 한다.
        """
        entry = {e["host"]: e for e in self.sources["denied"]}["query1.finance.yahoo.com"]
        self.assertIn("stock-research", entry["note"])
        self.assertIn("사용자 사안", entry["note"])
        self.assertIn("ClaudeBot", entry["note"], "우리 계열 에이전트를 이름으로 지목한 금지도 남긴다")

    def test_no_price_source_in_allowlist(self):
        """**결과를 숨기지 않는다.** F6 의 P1·P2 분자를 만들 가격 원천이 아직 없다."""
        allowed = {e["host"] for e in self.sources["allowed"]}
        self.assertEqual(allowed, {"data.sec.gov", "www.sec.gov", "www.federalreserve.gov"})

    def test_private_band_decided_by_c12(self):
        """C-12 확정(2026-09-11) 전에는 `private_bands` 가 null 이고 모드가 pending 이었다.

        **밴드를 임의로 채워 통과시킨 것이 아니라 사용자 확정 뒤에 반영했다.** 밴드 값이
        v1.5 구간표와 같은지는 `test_scorecard_private.py` 가 원본 대조로 고정한다.
        """
        self.assertIsNotNone(self.f6["private_bands"])
        self.assertEqual(self.f6["private_score_mode"], "p2_with_capped_promotion")
        self.assertEqual(self.f6["private_correction"]["cap_steps"], 1)
        self.assertTrue(self.f6["private_correction"]["require_all"])

    def test_v17_is_still_draft(self):
        self.assertEqual(RULES_V17.payload["status"], "draft")


class TestV17F9Rescaled(unittest.TestCase):
    """C-06 재척도(2026-09-11)로 v1.7 이 풀렸다는 것을 고정한다.

    MISS-LABEL-23 진행 중 v1.7 은 F9 정책-range 검사에 걸려 있었다. C-05·C-06 확정으로
    고칠 값이 정해져 제약이 해제됐고 이제 로드된다. **레벨은 올리고 스텝은 그대로**가 원칙이다.
    """

    def test_v17_loads_again(self):
        self.assertIsNone(V17_BLOCK, f"v1.7 이 아직 막혀 있다: {V17_BLOCK}")
        self.assertIsNotNone(RULES_V17)

    def test_levels_moved_up_one_notch(self):
        f9 = RULES_V17.f9
        self.assertEqual(f9["floor"], -4)
        self.assertEqual(f9["g1_bep_retreat_score"], -4)
        self.assertEqual(f9["g1_buffer_erosion_min_score"], -3)
        self.assertEqual(f9["g1_direction_relief_cap"], -2)
        self.assertEqual([b["score"] for b in f9["g1_bands_proposed"]], [-2, -3, -4])

    def test_steps_unchanged(self):
        """몇 칸 내리는지를 지정하는 값은 건드리지 않는다."""
        f9 = RULES_V17.f9
        self.assertEqual(f9["g1_direction_relief_step"], 1)
        self.assertEqual(f9["g2_fcf_negative"], -2)
        self.assertEqual(f9["g2_private_not_disclosed"], -2)
        self.assertEqual(f9["g2_fcf_positive_deteriorating"], -1)
        self.assertEqual((f9["g3_runway_keep_years"], f9["g3_runway_one_step_years"]), (3, 1))
        self.assertEqual(f9["g4_coverage_keep"], 1.0)

    def test_all_f9_scores_inside_range(self):
        """재척도가 끝났으니 정합 검사를 다시 통과해야 한다."""
        lo, hi = RULES_V17.factor_range("F9")
        self.assertEqual((lo, hi), (-4, 0))
        for b in RULES_V17.f9["g1_bands_proposed"]:
            self.assertTrue(lo <= b["score"] <= hi)

    def test_v15_untouched(self):
        """v1.5 는 승인 대상이라 재척도하지 않는다."""
        self.assertEqual(RULES_V15.f9["floor"], -5)
        self.assertEqual([b["score"] for b in RULES_V15.f9["g1_bands_proposed"]], [-3, -4, -5])
