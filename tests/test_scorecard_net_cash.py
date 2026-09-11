# net_cash 작업 정의와 '6.4 를 P2 로 옮기지 말 것' 적용범위 구분을 고정한다 (NETCASH-37)
"""이 테스트가 지키는 계약 넷.

1. **역산 정의는 스스로 역산이라고 말해야 한다.** `provenance.kind` 가 `legacy_reverse_engineered`
   이면 경고와 `supersede` 가 비어 있을 수 없다. 근거 없는 정의가 확정 정의처럼 굳는 것을 막는다.
2. **근거 숫자가 목록과 맞아야 한다.** 일치 개수를 손으로 적고 목록을 나중에 고치면 숫자만 거짓말로 남는다.
3. **두 자리가 다른 지표를 가리켜야 한다.** 이 블록의 존재 이유가 `cash`(6.4 런웨이)와
   `net_cash`(P2 EV 조정)를 가르는 것이라 하나로 접히면 의미가 사라진다.
4. **P2 산출물에 정의가 드러나야 한다.** 선언만 하고 읽는 코드가 없으면 다음 사람은 값만 본다.
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
from scorecard.inputs import JudgmentLookup, ObsLookup  # noqa: E402
from scorecard.rules import load_rules  # noqa: E402
from scorecard.schema import SchemaError, validate_rules  # noqa: E402

RULES = load_rules("v1.7")
RUN_DIR = ROOT / "scorecard" / "runs" / "ai-scorecard-2026-09-obsreg"


def company(cid: str = "acme") -> dict:
    return {"company_id": cid, "display_name": cid.title(), "aliases": [], "type": "업무",
            "listed": True, "ticker": "ACME", "exchange": "NASDAQ", "share_basis": "common",
            "adr_ratio": None, "reporting_currency": "USD", "scope": "test"}


def obs(metric: str, value, *, basis=None, status="verified") -> dict:
    return {"observation_id": f"acme.{metric}.t", "company_id": "acme", "metric": metric,
            "value": value, "unit": "USD" if metric != "price" else "USD/share",
            "as_of": "2026-09-02", "kind": "actual", "source_id": "SRC-t", "status": status,
            "period": None, "basis": basis, "raw": None, "note": None}


def mutated_rules(mutate) -> dict:
    payload = copy.deepcopy(RULES.payload)
    mutate(payload["policies"]["f6"]["net_cash"], payload)
    return payload


class NetCashDefinitionTest(unittest.TestCase):
    """규칙 블록 자체의 계약."""

    def setUp(self) -> None:
        self.spec = RULES.f6_net_cash()

    def test_accessor_returns_working_definition(self):
        self.assertEqual(self.spec["status"], "working_definition")
        self.assertEqual(self.spec["provenance"]["kind"], "legacy_reverse_engineered")
        self.assertIn("현금", self.spec["definition"])

    def test_reverse_engineered_must_declare_it_is_replaceable(self):
        for key, drop in (("warning", lambda s, p: s["provenance"].pop("warning")),
                          ("supersede", lambda s, p: s.pop("supersede"))):
            with self.subTest(key=key), self.assertRaises(SchemaError) as cm:
                validate_rules(mutated_rules(drop))
            self.assertIn("net_cash", str(cm.exception))

    def test_unknown_status_rejected(self):
        with self.assertRaises(SchemaError):
            validate_rules(mutated_rules(lambda s, p: s.update(status="final")))

    def test_matched_count_must_equal_list(self):
        """개수만 고치고 목록을 안 고치는 실수를 로드 시점에 잡는다."""
        def drop_one(spec, _payload):
            spec["evidence"]["matched"]["companies"].pop("tesla")
        with self.assertRaises(SchemaError) as cm:
            validate_rules(mutated_rules(drop_one))
        self.assertIn("count", str(cm.exception))

    def test_matched_list_is_what_we_actually_measured(self):
        """규칙이 주장하는 6개사가 실제 검증 결과와 같아야 한다."""
        self.assertEqual(set(self.spec["evidence"]["matched"]["companies"]),
                         {"microsoft", "tesla", "meta", "oracle", "alphabet", "palantir"})
        self.assertEqual(set(self.spec["evidence"]["differs"]["companies"]),
                         {"amazon", "nvidia", "spacex-xai", "tsmc"})

    def test_unknown_cause_is_stated_not_hidden(self):
        """**왜 안 맞는지 모른다는 것을 적어 둔다.** 모르는 것을 아는 척하면 다음 사람이 조사하지 않는다."""
        self.assertIn("아직 모른다", self.spec["evidence"]["differs"]["note"])
        self.assertTrue(self.spec["open_questions"])


class ScopeSeparationTest(unittest.TestCase):
    """6.4(런웨이)와 P2(EV 조정)를 가르는 계약. **같은 '현금' 이라는 말이 두 자리에서 다른 것을 가리킨다.**"""

    def setUp(self) -> None:
        self.sep = RULES.f6_net_cash()["scope_separation"]

    def test_two_sites_name_different_metrics(self):
        self.assertEqual({s["metric"] for s in self.sep["sites"]}, {"cash", "net_cash"})

    def test_runway_site_counts_only_usable_cash(self):
        site = next(s for s in self.sep["sites"] if s["metric"] == "cash")
        self.assertIn("6.4", site["site"])
        self.assertIn("환금성", site["counts"])

    def test_ev_site_counts_all_financial_assets(self):
        site = next(s for s in self.sep["sites"] if s["metric"] == "net_cash")
        self.assertIn("EV", site["site"])
        self.assertIn("환금성은 여기서 묻는 질문이 아니다", site["why"])

    def test_collapsing_to_one_metric_is_rejected(self):
        """두 자리가 같은 지표를 가리키면 이 블록은 아무것도 구분하지 않는다."""
        def collapse(spec, _payload):
            for site in spec["scope_separation"]["sites"]:
                site["metric"] = "cash"
        with self.assertRaises(SchemaError) as cm:
            validate_rules(mutated_rules(collapse))
        self.assertIn("서로 다른 지표", str(cm.exception))

    def test_unknown_metric_rejected(self):
        def bad(spec, _payload):
            spec["scope_separation"]["sites"][0]["metric"] = "free_cash"
        with self.assertRaises(SchemaError):
            validate_rules(mutated_rules(bad))

    def test_f9_side_cross_references_the_same_block(self):
        """6.4 를 고치러 온 사람도 걸려야 한다 — **한쪽에만 적으면 반쪽이다.**"""
        g3 = RULES.payload["policies"]["f9"]["g3_cash_scope"]
        self.assertEqual(g3["see"], "policies.f6.net_cash.scope_separation")
        self.assertEqual(g3["metric"], "cash")

    def test_alphabet_illustration_is_the_registered_gap(self):
        ill = self.sep["alphabet_illustration"]
        self.assertEqual(ill["all_securities_usd"] - ill["pure_cash_usd"], ill["gap_usd"])
        self.assertEqual(ill["gap_usd"], 186_563_000_000)


class P2EmitsDefinitionTest(unittest.TestCase):
    """**선언한 값은 읽는 코드가 있어야 한다.** P2 계산이 정의와 상태를 같이 찍는다."""

    def _f6(self):
        items = [obs("market_cap", 1_000e9), obs("net_income_ttm", 50e9),
                 obs("net_cash", 100e9), obs("revenue_ttm", 200e9, basis={"period_basis": "ttm"}),
                 obs("revenue_ttm_prior", 150e9)]
        run = {"run_id": "t", "as_of": "2026-09-02", "rule_version": "v1.7", "decisions": []}
        return compute_f6(company(), ObsLookup(items), JudgmentLookup([]), RULES, run)

    def test_p2_carries_definition_and_status(self):
        p2 = self._f6()["calc"]["parameters"]["P2"]
        got = p2["net_cash_definition"]
        self.assertEqual(got["status"], "working_definition")
        self.assertEqual(got["provenance"], "legacy_reverse_engineered")
        self.assertEqual(got["definition"], RULES.f6_net_cash()["definition"])

    def test_working_definition_raises_a_warning_but_not_a_penalty(self):
        """경고는 내되 **점수는 건드리지 않는다.** 정의 미확정은 기업의 성질이 아니다."""
        result = self._f6()
        self.assertTrue(any("net_cash 작업 정의" in w for w in result["warnings"]))
        p2 = result["calc"]["parameters"]["P2"]
        self.assertEqual(p2["value"], (1_000e9 - 100e9) / 200e9)    # EV/Sales 4.5
        self.assertEqual(p2["score"], 0)                            # 8 미만이라 0 칸. 경고가 있어도 그대로다


class RegisteredObservationsTest(unittest.TestCase):
    """실행에 등록된 실측 관측의 계약. **등록한 9개사와 안 한 3개사가 뒤섞이면 안 된다.**"""

    @classmethod
    def setUpClass(cls) -> None:
        cls.obs = json.loads((RUN_DIR / "observations.json").read_text(encoding="utf-8"))["items"]
        cls.results = json.loads((RUN_DIR / "results.json").read_text(encoding="utf-8"))

    def test_nine_measured_registrations(self):
        got = {o["company_id"] for o in self.obs if o["observation_id"].endswith(".net_cash.nc37")}
        self.assertEqual(got, {"microsoft", "amazon", "nvidia", "spacex-xai", "tesla", "meta",
                               "oracle", "alphabet", "tsmc"})

    def test_measured_observations_are_verified_and_carry_components(self):
        for o in self.obs:
            if not o["observation_id"].endswith(".net_cash.nc37"):
                continue
            with self.subTest(cid=o["company_id"]):
                self.assertEqual(o["status"], "verified")
                self.assertEqual(o["basis"]["definition_status"], "working_definition")
                self.assertIn("scope_warning", o["basis"])
                self.assertIn("components", o["basis"])

    def test_three_companies_keep_legacy_and_stay_flagged(self):
        """등록하지 못한 셋은 **legacy 그대로 남고 미검증 표시가 유지돼야** 한다."""
        flagged = {c["company_id"] for c in self.results["companies"]
                   if "net_cash" in ((c["factors"]["F6"].get("calc") or {})
                                     .get("unverified_inputs") or {})}
        self.assertEqual(flagged, {"apple", "palantir", "alibaba"})

    def test_market_cap_still_flagged_on_every_listed_company(self):
        """net_cash 를 실측해도 **P2 는 여전히 미검증 시총 위에 선다.** 그 사실이 사라지면 안 된다."""
        flagged = {c["company_id"] for c in self.results["companies"]
                   if "market_cap" in ((c["factors"]["F6"].get("calc") or {})
                                       .get("unverified_inputs") or {})}
        self.assertEqual(len(flagged), 11)

    def test_spacex_correction_is_recorded(self):
        """금융리스 이중계상을 뺐다는 것이 관측에 남아야 재검토가 가능하다."""
        o = next(o for o in self.obs if o["observation_id"] == "spacex-xai.net_cash.nc37")
        self.assertEqual(o["basis"]["correction_vs_mcap36"]["excluded"], 1_079_000_000)
        self.assertEqual(o["basis"]["components"]["finance_lease"], None)

    def test_amazon_correction_is_recorded(self):
        o = next(o for o in self.obs if o["observation_id"] == "amazon.net_cash.nc37")
        self.assertEqual(o["basis"]["components"]["debt_ex_lease"], 132_549_000_000)
        self.assertIn("us-gaap:ShortTermBorrowings", o["basis"]["components"]["debt_concepts"])

    def test_tsmc_measured_from_preserved_20f_not_companyfacts(self):
        o = next(o for o in self.obs if o["observation_id"] == "tsmc.net_cash.nc37")
        self.assertEqual(o["source_id"], "SRC-SEC-TSM-20F-FY2025")
        self.assertIn("금액 사실이 0건", o["basis"]["why_not_companyfacts"])
        self.assertEqual(o["basis"]["fx_rate"], 31.37)


if __name__ == "__main__":
    unittest.main()
