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

RULES_V15 = load_rules("v1.5")
RULES_V16 = load_rules("v1.6")
RULES_V17 = load_rules("v1.7")


def company(cid: str = "acme", listed: bool = True, share_basis: str | None = None) -> dict:
    return {
        "company_id": cid, "display_name": cid.title(), "aliases": [], "type": "업무",
        "listed": listed, "ticker": "ACME" if listed else None,
        "exchange": "NASDAQ" if listed else None,
        "share_basis": share_basis or ("common" if listed else "private"),
        "adr_ratio": None, "reporting_currency": "USD", "scope": "test",
    }


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
          revenue=100.0, revenue_prior=80.0, operating_income=None,
          period_basis: str | None = "ttm", nonop_share=None) -> ObsLookup:
    """v1.7 F6 입력. None 을 넘기면 그 관측을 아예 만들지 않는다."""
    items = []

    def add(metric, value, basis=None):
        if value is not None:
            items.append(obs(metric, value, cid=cid, basis=basis))

    add("market_cap", market_cap)
    add("net_cash", net_cash)
    add("net_income_ttm", net_income)
    add("operating_income_ttm", operating_income)
    add("nonop_share", nonop_share)
    rev_basis = {"period_basis": period_basis} if period_basis else {}
    add("revenue_ttm", revenue, rev_basis)
    add("revenue_ttm_prior", revenue_prior, rev_basis)
    return ObsLookup(items)


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


class TestF6P4(unittest.TestCase):
    """P4 는 소계에 한 칸만 걸린다. 여럿 걸려도 한 칸이다."""

    def test_nonop_share_recomputed_from_raw(self):
        r = compute_f6(company(), f6obs(net_income=100.0, operating_income=40.0),
                       JudgmentLookup([]), RULES_V17, run())
        p4 = r["calc"]["p4"]
        self.assertAlmostEqual(p4["nonop_share"], 0.60)
        self.assertEqual(p4["nonop_share_source"], "recomputed")
        self.assertIn("nonop_share", p4["conditions_hit"])

    def test_recompute_disagreement_is_warned_not_hidden(self):
        r = compute_f6(company(), f6obs(net_income=100.0, operating_income=40.0, nonop_share=0.10),
                       JudgmentLookup([]), RULES_V17, run())
        self.assertTrue(any("저장값" in w for w in r["warnings"]))
        self.assertEqual(r["calc"]["p4"]["nonop_share_source"], "recomputed")

    def test_multiple_conditions_still_one_step(self):
        c = company(cid="tsmc", share_basis="adr")
        r = compute_f6(c, f6obs("tsmc", period_basis="annual", net_income=100.0, operating_income=40.0),
                       JudgmentLookup([]), RULES_V17, run())
        self.assertEqual(len(r["calc"]["p4"]["conditions_hit"]), 2)
        self.assertEqual(r["calc"]["p4"]["demotion_steps"], 1)

    def test_floor_clamps_after_demotion(self):
        """P1 -2, P2 -2, P3 -3 에 P4 한 칸이면 -8 이지만 트랙 하한 -7 로 절단된다."""
        r = compute_f6(company(), f6obs(market_cap=1e6, net_income=100.0, operating_income=10.0,
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


class TestF6Private(unittest.TestCase):
    """비상장은 배수만 계산하고 점수를 만들지 않는다. 밴드가 미정이다."""

    def test_private_has_no_score(self):
        items = [obs("post_money_valuation", 965e9, cid="anthropic"),
                 obs("arr", 65e9, cid="anthropic", kind="run_rate"),
                 obs("arr_prior", 47e9, cid="anthropic", kind="run_rate"),
                 obs("cumulative_raised", 125e9, cid="anthropic")]
        r = compute_f6(company(cid="anthropic", listed=False), ObsLookup(items),
                       JudgmentLookup([]), RULES_V17, run())
        self.assertIsNone(r["score"])
        self.assertEqual(r["status"], "needs_rule_decision")
        m = r["calc"]["multiples"]
        self.assertAlmostEqual(m["post_money_over_arr"], 965 / 65)
        self.assertAlmostEqual(m["arr_growth"], 65 / 47 - 1)
        self.assertAlmostEqual(m["arr_over_cumulative_raised"], 65 / 125)

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
        self.assertEqual(RULES_V17.f6_mode, "parameters")

    def test_v15_still_scores_by_ntm_per(self):
        lookup = ObsLookup([obs("ntm_per", 25.0, basis={"method": "consensus_4q_sum"})])
        r = compute_f6(company(), lookup, JudgmentLookup([]), RULES_V15, run())
        self.assertEqual(r["status"], "ok")
        self.assertEqual(r["calc"]["ntm_per"], 25.0)
        self.assertNotIn("parameters", r["calc"])


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
        fx = self.f6["fx"]
        self.assertEqual(fx["rate_source_host"], "www.federalreserve.gov")
        for key in ("price_date", "fx_rate_date", "fx_backfill_days"):
            self.assertIn(key, fx["date_fields"])

    def test_fx_backfill_limit_is_pending(self):
        """한도 없이 두면 무한 후퇴가 된다. 잠정값을 두되 확정이 아님을 표시한다."""
        fx = self.f6["fx"]
        self.assertEqual(fx["backfill_limit_status"], "pending")
        self.assertIsInstance(fx["backfill_limit_days"], int)
        self.assertIn("잠정", fx["backfill_limit_note"])

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

    def test_fmp_and_finnhub_stay_allowed_with_status_note(self):
        """사용자 결정이다. 강등하지 않고 상태만 적는다."""
        allowed = {e["host"]: e["note"] for e in self.sources["allowed"]}
        denied = {e["host"] for e in self.sources["denied"]}
        unlisted = {e["host"] for e in self.sources.get("unlisted", [])}
        for host in ("financialmodelingprep.com", "finnhub.io"):
            self.assertIn(host, allowed)
            self.assertNotIn(host, denied)
            self.assertNotIn(host, unlisted)
            self.assertIn("상태 고지", allowed[host])
        self.assertIn("무료 등급 전제가 깨진 상태", allowed["financialmodelingprep.com"])
        self.assertIn("약관 확인이 불가능", allowed["finnhub.io"])

    def test_private_band_still_pending(self):
        self.assertIsNone(self.f6["private_bands"])
        self.assertEqual(self.f6["private_score_mode"], "pending_rule_decision")

    def test_v17_is_still_draft(self):
        self.assertEqual(RULES_V17.payload["status"], "draft")
