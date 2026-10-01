# FIX-54 1단계 S5 — 리스 결측 비합산 · P1 분자 모회사 귀속 · apple TTM 시작일 · TTM 성분 accession 을 고정한다
from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


def _load(name: str, path: Path):
    """검증 스크립트는 패키지가 아니라 경로로 읽는다 — `measure` 같은 짧은 이름이 sys.path 에서 다른 모듈을 가리지 않게."""
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


measure = _load("netcash37_measure", ROOT / "validation" / "netcash-37" / "measure.py")
collect_ttm = _load("f6spec18_collect_ttm", ROOT / "validation" / "f6-spec-18" / "collect_ttm.py")

from scorecard.calc_f6 import compute_f6  # noqa: E402
from scorecard.inputs import JudgmentLookup, ObsLookup  # noqa: E402
from scorecard.rules import load_rules  # noqa: E402
from tests._raw import require_raw  # noqa: E402
from tests.test_scorecard_f6_v17 import company, obs, run  # noqa: E402

RULES = load_rules("v1.7")
RUN_DIR = ROOT / "output" / "ai-scorecard-2026-09-obsreg"
RAW = ROOT / "validation" / "f6-avail-15" / "_raw"


def load(name: str) -> dict:
    return json.loads((RUN_DIR / name).read_text(encoding="utf-8"))


class LeaseCompletenessTest(unittest.TestCase):
    @require_raw(RAW / "SPCX.companyfacts.json", RAW / "PLTR.companyfacts.json", RAW / "TSLA.companyfacts.json")
    def test_missing_component_is_not_summed_as_zero(self):
        for cid, end, missing in (("spacex-xai", "2026-06-30", "OperatingLeaseLiabilityNoncurrent"),
                                  ("palantir", "2026-06-30", "OperatingLeaseLiabilityCurrent")):
            with self.subTest(cid=cid):
                m = measure.measure_us(cid, end)
                self.assertIsNone(m["operating_lease"])
                self.assertEqual(m["operating_lease_missing"], [missing])
                self.assertTrue(m["lease_incomplete"])
                self.assertIsNone(m["debt_incl_lease"])
        full = measure.measure_us("tesla", "2026-06-30")
        self.assertEqual(full["operating_lease"], 6738000000.0)       # 두 구성요소가 다 있으면 그대로 합한다

    def test_spacex_net_cash_marked_partial_not_substituted(self):
        o = {x["observation_id"]: x for x in load("observations.json")["items"]}["spacex-xai.net_cash.nc37"]
        self.assertEqual(o["value"], 60301000000.0)
        c = o["basis"]["completeness"]
        self.assertFalse(c["complete_sum"])
        self.assertIn("1,136", c["not_substituted"])
        self.assertIn("대신 빼지 않았다", c["not_substituted"])
        partial = RULES.payload["policies"]["f6"]["net_cash"]["evidence"]["matched"]["partial_lease_basis"]
        self.assertEqual(partial["companies"], ["palantir", "spacex-xai"])


class P1OwnershipScopeTest(unittest.TestCase):
    def test_tsmc_uses_parent_attributable(self):
        o = {x["observation_id"]: x for x in load("observations.json")["items"]}["tsmc.net_income_ttm.f6reg28"]
        self.assertEqual(o["basis"]["original_value"], 1697604000000.0)
        self.assertEqual(o["basis"]["ownership_correction"]["was"]["original_value"], 1695124900000.0)
        res = {c["company_id"]: c for c in load("results.json")["companies"]}
        p1 = res["tsmc"]["factors"]["F6"]["calc"]["parameters"]["P1"]
        self.assertAlmostEqual(p1["value"], 39.7298, places=3)
        self.assertEqual(p1["score"], -1)

    def test_every_net_income_declares_scope(self):
        items = [x for x in load("observations.json")["items"] if x["metric"] == "net_income_ttm" and x["status"] == "verified"]
        self.assertEqual(len(items), 12)
        for o in items:
            with self.subTest(oid=o["observation_id"]):
                self.assertEqual(o["basis"]["ownership_scope"], "parent_attributable")
        self.assertEqual(RULES.payload["policies"]["f6"]["parameters"]["P1"]["input_scope"], {"net_income_ttm": "parent_attributable"})

    def test_calc_refuses_other_scope(self):
        items = [obs("market_cap", 1000.0), obs("net_cash", 0.0), obs("net_income_ttm", 50.0, basis={"ownership_scope": "consolidated_incl_nci"}),
                 obs("revenue_ttm", 100.0, basis={"period_basis": "ttm"}), obs("revenue_ttm_prior", 80.0)]
        r = compute_f6(company(), ObsLookup(items), JudgmentLookup([]), RULES, run())
        self.assertEqual(r["status"], "pending_data")
        self.assertIn("소유 범위", r["pending"]["message"])


class AppleWindowTest(unittest.TestCase):
    def test_apple_starts_day_after_ytd_end(self):
        o = {x["observation_id"]: x for x in load("observations.json")["items"]}
        for oid in ("apple.revenue_ttm.f6reg28", "apple.operating_income_ttm.f6reg28", "apple.net_income_ttm.f6reg28",
                    "apple.pretax_income_ttm.nonop44", "apple.fcf_ttm.cashfcf35"):
            self.assertEqual(o[oid]["period"]["start"], "2025-06-29", oid)
        self.assertEqual(o["apple.revenue_ttm_prior.f6reg28"]["period"], {"start": "2024-06-30", "end": "2025-06-28"})

    @require_raw(RAW / "AAPL.companyfacts.json")
    def test_collector_q4_starts_next_day(self):
        doc = collect_ttm.load_facts("AAPL")
        rows, mix = collect_ttm.coalesce_series(doc, collect_ttm.NET_INCOME_TAGS, "USD")
        series, _ = collect_ttm.quarter_series(rows, RULES, mix)
        q4 = next(r for r in series if r["kind"] == "Q4_derived" and r["end"] == "2025-09-27")
        self.assertEqual(q4["start"], "2025-06-29")


class ComponentAccessionTest(unittest.TestCase):
    def test_every_reconstructed_ttm_has_component_accessions(self):
        items = load("observations.json")["items"]
        want = [x for x in items if x["status"] == "verified" and x.get("period") and x["company_id"] not in ("tsmc", "alibaba")
                and (x["observation_id"].endswith(("nonop44", "fcf_ttm.cashfcf35"))
                     or (x["observation_id"].endswith("f6reg28") and (x["basis"] or {}).get("period_basis") == "ttm"
                         and x["company_id"] != "spacex-xai" and x["metric"] != "operating_margin_ttm"))]
        self.assertEqual(len(want), 55)
        for o in want:
            with self.subTest(oid=o["observation_id"]):
                ca = o["basis"]["component_accessions"]
                self.assertTrue(ca["arithmetic"]["matches_value"])
                flat = []
                for it in ca["items"]:
                    flat += it.get("derived_from", [it])
                for c in flat:
                    self.assertRegex(c["accession"], r"^\d{10}-\d{2}-\d{6}$")
                    self.assertIn(c["form"], {"10-Q", "10-K", "S-1/A"})

    def test_review_examples(self):
        o = {x["observation_id"]: x for x in load("observations.json")["items"]}
        ni = o["alphabet.net_income_ttm.f6reg28"]["basis"]["component_accessions"]
        q4 = next(i for i in ni["items"] if i["role"] == "q4_derived")
        self.assertEqual([c["role"] for c in q4["derived_from"]], ["fy", "quarter_in_fy", "quarter_in_fy", "quarter_in_fy"])
        self.assertEqual(q4["derived_from"][0]["form"], "10-K")
        prior = o["meta.revenue_ttm_prior.f6reg28"]["basis"]["component_accessions"]
        self.assertEqual(prior["arithmetic"]["sum"], o["meta.revenue_ttm_prior.f6reg28"]["value"])


if __name__ == "__main__":
    unittest.main()
