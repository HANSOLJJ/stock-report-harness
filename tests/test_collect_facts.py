# SEC companyfacts 누계 복원 수집기(collect --kind facts)를 잠그는 테스트 — 누계·분기 혼재, 재작성, 기준일 뒤 제출, 52/53주, 회사 단위 실패
from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
os.environ["SCORECARD_DOTENV"] = ""

from scorecard import collect_filings, engine, registry, stages  # noqa: E402
from scorecard.collect_facts import duration_facts, fact_observations, pick_concept, quarter_series, quarterly_observations, ttm  # noqa: E402
from scorecard.schema import load_json_strict  # noqa: E402
from tests.test_collect_stage import NOW, SLUG, Sandbox  # noqa: E402

OCF = "NetCashProvidedByUsedInOperatingActivities"
CAPEX = "PaymentsToAcquirePropertyPlantAndEquipment"
CAPEX_NEW = "PaymentsToAcquireProductiveAssets"
TAX = "IncomeTaxExpenseBenefit"
CACHE = ROOT / "validation" / "f6-avail-15b" / "_raw"


def f(start: str, end: str, val: float, filed: str, accn: str = "0000000000-26-000001", form: str = "10-Q") -> dict:
    return {"start": start, "end": end, "val": val, "filed": filed, "accn": accn, "form": form}


def doc(**tags: list[dict]) -> dict:
    return {"facts": {"us-gaap": {tag: {"units": {"USD": rows}} for tag, rows in tags.items()}}}


# 달력 회계연도 회사의 2분기 누계 상황: 직전 연간 100, 전기 상반기 40, 당기 상반기 55
CAL = [
    f("2025-01-01", "2025-12-31", 100, "2026-02-01", form="10-K"),
    f("2025-01-01", "2025-06-30", 40, "2025-07-30"),
    f("2026-01-01", "2026-03-31", 20, "2026-04-30"),
    f("2025-01-01", "2025-03-31", 18, "2025-04-30"),
    f("2026-01-01", "2026-06-30", 55, "2026-07-30"),
]


def rows(items: list[dict], filed_until: str = "2026-09-30") -> list[dict]:
    return duration_facts(doc(X=items), "X", filed_until=filed_until)


class TtmTest(unittest.TestCase):
    def test_ytd_formula_and_period(self):
        res = ttm(rows(CAL))
        self.assertEqual(res["value"], 55 + 100 - 40)
        self.assertEqual(res["period"], {"start": "2025-07-01", "end": "2026-06-30"})
        self.assertEqual(res["formula"], "ytd")
        self.assertEqual([c["role"] for c in res["components"]], ["curr_ytd", "prior_fy", "prior_ytd"])
        self.assertEqual([c["val"] for c in res["components"]], [55, 100, 40])

    def test_value_follows_each_component(self):
        """입력을 바꾸면 판정이 따라오는지 본다 — 성분 셋 각각."""
        for idx, delta, want in ((4, 15, 130), (0, 10, 125), (1, 5, 110)):
            with self.subTest(idx=idx):
                items = [dict(r) for r in CAL]
                items[idx]["val"] += delta
                self.assertEqual(ttm(rows(items))["value"], want)

    def test_fy_direct_when_latest_is_fiscal_year_end(self):
        items = [*CAL, f("2026-01-01", "2026-12-31", 130, "2027-02-01", form="10-K")]
        res = ttm(rows(items, filed_until="2027-03-01"))
        self.assertEqual((res["value"], res["formula"]), (130, "fy_direct"))
        self.assertEqual(res["period"], {"start": "2026-01-01", "end": "2026-12-31"})

    def test_discrete_quarter_at_same_end_does_not_replace_ytd(self):
        """손익 항목처럼 3개월 사실과 누계가 같은 날 끝나면 긴 누계를 쓴다(누계·분기 혼재)."""
        items = [*CAL, f("2026-04-01", "2026-06-30", 35, "2026-07-30")]
        self.assertEqual(ttm(rows(items))["value"], 115)

    def test_restated_value_latest_filed_within_cutoff(self):
        items = [*CAL, f("2025-01-01", "2025-12-31", 102, "2026-05-01", form="10-K/A"),
                 f("2025-01-01", "2025-12-31", 999, "2026-10-15", form="10-K/A")]
        res = ttm(rows(items))
        fy = next(c for c in res["components"] if c["role"] == "prior_fy")
        self.assertEqual((fy["val"], fy.get("restated")), (102, True))
        self.assertEqual(res["value"], 55 + 102 - 40)

    def test_facts_filed_after_cutoff_are_dropped(self):
        res = ttm(rows(CAL, filed_until="2026-07-01"))
        self.assertEqual(res["value"], 20 + 100 - 18)
        self.assertEqual(res["period"]["end"], "2026-03-31")

    def test_missing_prior_fiscal_year_makes_no_value(self):
        res = ttm(rows([r for r in CAL if r["form"] != "10-K"]))
        self.assertIsNone(res["value"])
        self.assertIn("직전 회계연도의 연간 값이 없다", res["reason"])

    def test_missing_prior_ytd_makes_no_value(self):
        res = ttm(rows([r for r in CAL if r["end"] != "2025-06-30"]))
        self.assertIsNone(res["value"])
        self.assertIn("전기 같은 누계", res["reason"])

    def test_52_53_week_fiscal_year(self):
        items = [f("2024-09-29", "2025-09-27", 1000, "2025-10-31", form="10-K"),
                 f("2024-09-29", "2025-06-28", 700, "2025-08-01"),
                 f("2025-09-28", "2026-06-27", 760, "2026-07-31")]
        res = ttm(rows(items))
        self.assertEqual(res["value"], 1060)
        self.assertEqual(res["period"], {"start": "2025-06-29", "end": "2026-06-27"})

    def test_other_currency_units_are_ignored(self):
        cny = {"facts": {"us-gaap": {OCF: {"units": {"CNY": CAL}}}}}
        self.assertEqual(pick_concept(cny, (OCF,), filed_until="2026-09-30"), (None, []))


class ConceptTest(unittest.TestCase):
    def test_latest_concept_wins_over_stale_one(self):
        stale = [f("2016-01-01", "2016-12-31", 7, "2017-02-01", form="10-K")]
        tag, picked = pick_concept(doc(**{CAPEX: stale, CAPEX_NEW: CAL}), (CAPEX, CAPEX_NEW), filed_until="2026-09-30")
        self.assertEqual((tag, picked[-1]["end"]), (CAPEX_NEW, "2026-06-30"))

    def test_tie_keeps_first_candidate(self):
        tag, _ = pick_concept(doc(**{CAPEX: CAL, CAPEX_NEW: CAL}), (CAPEX, CAPEX_NEW), filed_until="2026-09-30")
        self.assertEqual(tag, CAPEX)

    def test_observations_and_missing_reasons(self):
        company = {"company_id": "nvidia", "ticker": "NVDA", "cik": 1045810}
        obs, results = fact_observations(company, doc(**{OCF: CAL, TAX: CAL[1:]}), source_id="SRC-T",
                                         observed_at="2026-10-01", filed_until="2026-09-30")
        self.assertEqual([o["metric"] for o in obs], ["ocf_ttm"])
        o = obs[0]
        self.assertEqual((o["observation_id"], o["value"], o["unit"], o["as_of"], o["kind"], o["status"]),
                         ("nvidia.ocf_ttm.sec20260630", 115, "USD", "2026-06-30", "derived", "verified"))
        self.assertEqual(o["basis"]["concept"], f"us-gaap:{OCF}")
        self.assertEqual({r["metric"]: r["status"] for r in results},
                         {"ocf_ttm": "collected", "capex_ttm": "no_concept", "income_tax_ttm": "insufficient"})


# 누계만 있는 현금흐름 항목의 두 회계연도: 분기 값은 2025년 10·15·20·25, 2026년 20·30
CHAIN = [
    f("2025-01-01", "2025-03-31", 10, "2025-04-30"), f("2025-01-01", "2025-06-30", 25, "2025-07-30"),
    f("2025-01-01", "2025-09-30", 45, "2025-10-30"), f("2025-01-01", "2025-12-31", 70, "2026-02-01", form="10-K"),
    f("2026-01-01", "2026-03-31", 20, "2026-04-30"), f("2026-01-01", "2026-06-30", 50, "2026-07-30"),
]
FL = "RightOfUseAssetObtainedInExchangeForFinanceLeaseLiability"


class QuarterTest(unittest.TestCase):
    def test_ytd_chain_becomes_quarters_with_q4_from_fy(self):
        qs = quarter_series(rows(CHAIN))
        self.assertEqual([(q["start"], q["end"], q["val"]) for q in qs],
                         [("2025-01-01", "2025-03-31", 10), ("2025-04-01", "2025-06-30", 15), ("2025-07-01", "2025-09-30", 20),
                          ("2025-10-01", "2025-12-31", 25), ("2026-01-01", "2026-03-31", 20), ("2026-04-01", "2026-06-30", 30)])
        self.assertEqual([q["formula"] for q in qs][:2], ["quarter_direct", "quarter_ytd_diff"])

    def test_direct_quarter_wins_and_mismatch_is_recorded(self):
        qs = {q["end"]: q for q in quarter_series(rows([*CHAIN, f("2026-04-01", "2026-06-30", 31, "2026-07-30")]))}
        self.assertEqual((qs["2026-06-30"]["val"], qs["2026-06-30"]["ytd_check"]["ytd_diff"]), (31, 30))

    def test_missing_ytd_leaves_gap(self):
        qs = quarter_series(rows([r for r in CHAIN if r["end"] != "2025-09-30"]))
        self.assertEqual([q["end"] for q in qs], ["2025-03-31", "2025-06-30", "2026-03-31", "2026-06-30"])

    def test_window_drops_stale_quarters_and_keeps_last_n(self):
        stale = [f("2022-01-01", "2022-03-31", 5, "2022-04-30")]
        obs, res = quarterly_observations({"company_id": "meta"}, doc(**{CAPEX: CHAIN, FL: stale}), source_id="SRC-T",
                                          observed_at="2026-09-30", filed_until="2026-09-29", keep=4)
        self.assertEqual([o["as_of"] for o in obs], ["2025-09-30", "2025-12-31", "2026-03-31", "2026-06-30"])
        self.assertEqual({o["metric"] for o in obs}, {"capex_quarterly"})
        self.assertEqual({r["metric"]: r["status"] for r in res},
                         {"capex_quarterly": "collected", "finance_lease_additions_quarterly": "insufficient"})
        self.assertEqual(obs[-1]["period"], {"start": "2026-04-01", "end": "2026-06-30"})
        self.assertEqual(obs[-1]["observation_id"], "meta.capex_quarterly.sec20260630")


@unittest.skipUnless((CACHE / "CIK0001652044_GOOGL.json").is_file(), "캐시 companyfacts 없음")
class RealCacheTest(unittest.TestCase):
    """저장소에 보존된 Alphabet companyfacts(2026-09-10 수집)로 원자료 성분과 대조한다."""

    def test_alphabet_ocf_capex_tax(self):
        d = json.loads((CACHE / "CIK0001652044_GOOGL.json").read_text(encoding="utf-8"))
        company = {"company_id": "alphabet", "ticker": "GOOGL", "cik": 1652044}
        obs, _ = fact_observations(company, d, source_id="SRC-T", observed_at="2026-09-10", filed_until="2026-09-10")
        got = {o["metric"]: o["value"] for o in obs}
        # 원자료 행(백만 달러): 당기 상반기 누계 + 2025 연간 − 2025 상반기 누계
        self.assertEqual(got["ocf_ttm"], 84_859_000_000 + 164_713_000_000 - 63_897_000_000)
        self.assertEqual(got["capex_ttm"], 80_598_000_000 + 91_447_000_000 - 39_643_000_000)
        self.assertEqual(got["income_tax_ttm"], 41_394_000_000 + 26_656_000_000 - 12_986_000_000)


class CollectStageTest(unittest.TestCase):
    def setUp(self) -> None:
        self.box = Sandbox(("nvidia", "tsmc", "openai"))
        self.addCleanup(self.box.close)
        self.files = Path(tempfile.mkdtemp())
        self.write({OCF: CAL, CAPEX: CAL, TAX: CAL})

    def write(self, tags: dict) -> None:
        (self.files / "CIK0001045810_NVDA.json").write_text(json.dumps(doc(**tags)), encoding="utf-8")

    def collect(self, **kw):
        return stages.collect(SLUG, kinds=("facts",), now=NOW, **kw)["facts"]

    def facts_obs(self) -> list[dict]:
        return [o for o in load_json_strict(self.box.run_dir / "observations.json")["items"]
                if o["source_id"].startswith("SRC-SEC-FACTS-")]

    def test_collects_observations_and_source(self):
        out = {r["company_id"]: r for r in self.collect(from_file=str(self.files))}
        self.assertEqual({k: v["status"] for k, v in out.items()},
                         {"nvidia": "collected", "tsmc": "skipped_no_cik", "openai": "skipped_no_cik"})
        self.assertEqual(out["nvidia"]["added"], ["ocf_ttm", "capex_ttm", "income_tax_ttm"])
        obs = self.facts_obs()
        self.assertEqual({o["metric"]: o["value"] for o in obs}, {"ocf_ttm": 115, "capex_ttm": 115, "income_tax_ttm": 115})
        self.assertEqual({o["source_id"] for o in obs}, {"SRC-SEC-FACTS-NVDA-20260930"})
        src = {s["source_id"]: s for s in load_json_strict(self.box.run_dir / "sources.json")["items"]}
        entry = src["SRC-SEC-FACTS-NVDA-20260930"]
        self.assertEqual(entry["url"], "https://data.sec.gov/api/xbrl/companyfacts/CIK0001045810.json")
        self.assertEqual(len(entry["sha256"]), 64)
        self.assertIn("제출일 2026-09-29 이하", entry["note"])     # 정보 기준일 = as_of

    def test_rerun_skips_same_values_and_refuses_different_ones(self):
        self.collect(from_file=str(self.files))
        again = {r["company_id"]: r for r in self.collect(from_file=str(self.files))}
        self.assertEqual((again["nvidia"]["status"], again["nvidia"]["existing"]),
                         ("skipped_existing", ["ocf_ttm", "capex_ttm", "income_tax_ttm"]))
        changed = [dict(r) for r in CAL]
        changed[4]["val"] = 60
        self.write({OCF: changed, CAPEX: CAL, TAX: CAL})
        bad = {r["company_id"]: r for r in self.collect(from_file=str(self.files))}
        self.assertEqual(bad["nvidia"]["status"], "failed")
        self.assertIn("다른 값", bad["nvidia"]["error"])
        self.assertEqual(len(self.facts_obs()), 3)

    def test_non_usd_reporter_is_skipped(self):
        registry.set_company_field("tsmc", "cik", 1046179, path=self.box.companies)
        out = {r["company_id"]: r for r in self.collect(from_file=str(self.files))}
        self.assertEqual(out["tsmc"]["status"], "skipped_currency")

    def test_dry_run_writes_nothing(self):
        before = (self.box.run_dir / "observations.json").read_bytes()
        out = {r["company_id"]: r for r in self.collect(dry_run=True)}
        self.assertEqual(out["nvidia"]["urls"], ["https://data.sec.gov/api/xbrl/companyfacts/CIK0001045810.json"])
        self.assertEqual((self.box.run_dir / "observations.json").read_bytes(), before)

    def test_cache_older_than_cutoff_is_refetched(self):
        os.environ["SEC_UA"] = "Test User test@example.com"
        self.addCleanup(os.environ.pop, "SEC_UA", None)
        sleep = mock.patch.object(collect_filings.time, "sleep")
        sleep.start()
        self.addCleanup(sleep.stop)
        bodies = iter([json.dumps(doc(**{OCF: CAL[:4]})).encode(), json.dumps(doc(**{OCF: CAL})).encode()])
        calls: list[str] = []

        def fetch(url, *, user_agent, **kw):
            calls.append(url)
            return next(bodies)

        real = collect_filings.sec_get
        collect_filings.sec_get("https://data.sec.gov/api/xbrl/companyfacts/CIK0001045810.json", fetch=fetch,
                                now="2026-09-01T00:00:00Z")     # 정보 기준일(2026-09-29) 전에 받은 캐시
        with mock.patch.object(collect_filings, "sec_get", lambda url, **kw: real(url, fetch=fetch, **kw)):
            out = {r["company_id"]: r for r in self.collect()}
        self.assertEqual(len(calls), 2)
        self.assertEqual(out["nvidia"]["status"], "collected")
        self.assertEqual({o["metric"]: o["as_of"] for o in self.facts_obs()}, {"ocf_ttm": "2026-06-30"})


class BasketStageTest(unittest.TestCase):
    """규칙에 국면 지표 바스켓이 있을 때만, 바스켓 회사에만 분기 관측을 낸다. 공급자(NVIDIA)는 매출총이익·매출 분기 값만 낸다."""

    extra: dict = {}

    def run_collect(self, rule_version: str) -> list[dict]:
        box = Sandbox(("meta", "nvidia"), rule_version=rule_version)
        self.addCleanup(box.close)
        registry.set_company_field("meta", "cik", 1326801, path=box.companies)
        files = Path(tempfile.mkdtemp())
        for name in ("CIK0001326801_META.json", "CIK0001045810_NVDA.json"):
            (files / name).write_text(json.dumps(doc(**{OCF: CAL, CAPEX: CHAIN, TAX: CAL, **self.extra.get(name, {})})), encoding="utf-8")
        stages.collect(SLUG, kinds=("facts",), from_file=str(files), now=NOW)
        return load_json_strict(box.run_dir / "observations.json")["items"]

    def test_v21_basket_company_gets_quarters(self):
        items = self.run_collect("v2.1")
        quarters = [o for o in items if o["metric"] == "capex_quarterly"]
        self.assertEqual({o["company_id"] for o in quarters}, {"meta"})
        self.assertEqual([o["value"] for o in quarters], [10, 15, 20, 25, 20, 30])

    def test_v21_supplier_gets_margin_quarters_only(self):
        self.extra = {"CIK0001045810_NVDA.json": {"GrossProfit": CHAIN, "Revenues": CHAIN}}
        items = self.run_collect("v2.1")
        nvidia = {o["metric"] for o in items if o["company_id"] == "nvidia" and o["metric"].endswith("_quarterly")}
        self.assertEqual(nvidia, {"gross_profit_quarterly", "revenue_quarterly"})     # 바스켓이 아니라 설비투자 분기 값은 없다
        self.assertFalse({o["metric"] for o in items if o["company_id"] == "meta"} & {"gross_profit_quarterly", "revenue_quarterly"})

    def test_rules_without_regime_emit_no_quarters(self):
        self.assertFalse([o for o in self.run_collect("v2.0") if o["metric"] == "capex_quarterly"])

    def test_regime_policy_validator(self):
        import copy
        from scorecard.schema import SchemaError, validate_rules
        base = json.loads((ROOT / "scorecard" / "rules" / "v2.1.json").read_text(encoding="utf-8"))
        for path, value in ((("scored",), True), (("capex", "quarters_kept"), 6), (("capex", "min_quarters"), 4),
                            (("capex", "flat_band"), 0.2), (("capex", "basket"), []),
                            (("margins", "quarters_shown"), 9), (("margins", "cloud_segments"), {})):
            with self.subTest(path=path, value=value):
                bad = copy.deepcopy(base)
                node = bad["policies"]["regime_indicators"]
                for key in path[:-1]:
                    node = node[key]
                node[path[-1]] = value
                with self.assertRaises(SchemaError):
                    validate_rules(bad)
        validate_rules(base)


if __name__ == "__main__":
    unittest.main()
