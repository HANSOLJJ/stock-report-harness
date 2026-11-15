# 국면 탭 시장 지표(금리·회사채 스프레드·GPU 임대료·토큰 단가)의 계산·수집·diff 허용·렌더를 잠그는 테스트
from __future__ import annotations

import json
import os
import re
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
os.environ["SCORECARD_DOTENV"] = ""

from scorecard import market_now as mn  # noqa: E402
from scorecard import render_common as rc  # noqa: E402
from scorecard import stages  # noqa: E402
from scorecard.schema import MARKET_COMPANY_ID, load_json_strict  # noqa: E402
from tests.test_collect_stage import SLUG, Sandbox  # noqa: E402

FX = json.loads((ROOT / "tests" / "node" / "fixtures" / "market_live.json").read_text(encoding="utf-8"))
NOW = "2026-09-30T01:00:00Z"
CSV = "observation_date,DGS10\n2026-09-25,4.10\n2026-09-26,.\n2026-09-28,\n2026-09-30,4.30\n"


def bodies(price_as_of: str, *, fail: set[str] = frozenset()) -> dict[str, str]:
    """원천 주소 → 응답 본문. fail 에 든 원천은 주소를 빼서 받기를 실패시킨다."""
    out: dict[str, str] = {}
    if "fred" not in fail:
        for _m, series, _n in mn.FRED_SERIES:
            out[mn.fred_csv_url(series, price_as_of)] = CSV
    if "vast" not in fail:
        for gpu in mn.GPU_TYPES:
            out[mn.vast_url(gpu)] = json.dumps({"offers": FX["offers"] if gpu != "B200" else []})
    if "openrouter" not in fail:
        models = [{**m, "created": m["created"] - 46 * 86400} for m in FX["models"]]  # 2026-11-15 → 2026-09-30 로 당긴다
        out[mn.OPENROUTER_URL] = json.dumps({"data": models})
    return out


def getter(table: dict[str, str]):
    def get(url: str) -> bytes:
        if url not in table:
            raise OSError(f"받지 못했다: {url}")
        return table[url].encode("utf-8")
    return get


class CalcTest(unittest.TestCase):
    def test_shared_fixture_matches_js(self):
        self.assertEqual(mn.gpu_rent(FX["offers"]), FX["expect_gpu"])
        self.assertEqual(mn.gpu_rent(FX["offers_even"])["value"], FX["expect_gpu_even"])
        self.assertIsNone(mn.gpu_rent([]))
        picks = mn.token_picks(FX["models"], FX["ref"])
        self.assertEqual([(p["lab"], p["model"]) for p in picks], [(p["lab"], p["model"]) for p in FX["expect_picks"]])
        for p, e in zip(picks, FX["expect_picks"]):
            self.assertAlmostEqual(p["blended"], e["blended"], places=9)
        self.assertAlmostEqual(mn.median([p["blended"] for p in picks]), FX["expect_token"], places=9)

    def test_fred_latest_skips_missing_and_future(self):
        self.assertEqual(mn.fred_latest(CSV, "2026-09-29"), ("2026-09-25", 4.10))
        self.assertEqual(mn.fred_latest(CSV, "2026-09-30"), ("2026-09-30", 4.30))
        self.assertIsNone(mn.fred_latest("observation_date,DGS10\n2026-09-26,.\n", "2026-09-29"))


class SnapshotTest(unittest.TestCase):
    def test_all_sources(self):
        snap = mn.snapshot("2026-09-29", today="2026-09-30", now=NOW, get=getter(bodies("2026-09-29")))
        by = {(o["metric"], (o["basis"] or {}).get("gpu")): o for o in snap["observations"]}
        self.assertEqual(by[("ust10y_yield", None)]["value"], 4.10)
        self.assertEqual(by[("ust10y_yield", None)]["as_of"], "2026-09-25")
        self.assertEqual(by[("gpu_rent_hourly", "H100 SXM")]["value"], 2.5)
        self.assertEqual(by[("gpu_rent_hourly", "H100 SXM")]["observation_id"], "_market.gpu_rent_hourly.h100-sxm.2026-09-30")
        # 호가가 없으면 값을 만들지 않는다(0 이 아니다)
        self.assertIsNone(by[("gpu_rent_hourly", "B200")]["value"])
        self.assertEqual(by[("gpu_rent_hourly", "B200")]["status"], "collection_failed")
        self.assertAlmostEqual(by[("token_blended_price", None)]["value"], 3.5, places=9)
        self.assertEqual({s["source_id"] for s in snap["sources"]},
                         {"SRC-FRED-2026-09-29", "SRC-VAST-2026-09-30", "SRC-OPENROUTER-2026-09-30"})

    def test_one_source_failing_keeps_others(self):
        snap = mn.snapshot("2026-09-29", today="2026-09-30", now=NOW, get=getter(bodies("2026-09-29", fail={"vast"})))
        metrics = {o["metric"] for o in snap["observations"]}
        self.assertEqual(metrics, {"ust10y_yield", "ig_oas", "hy_oas", "baa_spread", "token_blended_price"})
        self.assertEqual([r["status"] for r in snap["rows"] if r["metric"] == "gpu_rent_hourly"], ["failed"] * 3)
        self.assertNotIn("SRC-VAST-2026-09-30", {s["source_id"] for s in snap["sources"]})


class CollectDiffTest(unittest.TestCase):
    def setUp(self):
        self.box = Sandbox(("nvidia",))
        self.addCleanup(self.box.close)
        tmp = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8")
        json.dump(bodies("2026-09-29"), tmp)
        tmp.close()
        self.addCleanup(os.unlink, tmp.name)
        self.file = tmp.name

    def market_obs(self, slug: str) -> list[dict]:
        items = load_json_strict(self.box.dir / "output" / slug / "observations.json")["items"]
        return [o for o in items if o["company_id"] == MARKET_COMPANY_ID]

    def test_collect_writes_once_and_dry_run_writes_nothing(self):
        out = stages.collect(SLUG, kinds=("market",), dry_run=True)
        self.assertEqual(out["market"], [{"status": "dry_run", "price_as_of": "2026-09-29"}])
        self.assertEqual(self.market_obs(SLUG), [])
        stages.collect(SLUG, kinds=("market",), from_file=self.file, now=NOW)
        first = self.market_obs(SLUG)
        self.assertEqual(len(first), 8)
        again = stages.collect(SLUG, kinds=("market",), from_file=self.file, now=NOW)
        self.assertEqual(sum(1 for r in again["market"] if r["status"] == "skipped_existing"), 8)
        self.assertEqual(self.market_obs(SLUG), first)
        srcs = {s["source_id"] for s in load_json_strict(self.box.run_dir / "sources.json")["items"]}
        self.assertTrue({"SRC-FRED-2026-09-29", "SRC-VAST-2026-09-30", "SRC-OPENROUTER-2026-09-30"} <= srcs)

    def test_diff_allows_market_snapshot(self):
        from scorecard.compare import compare_inputs
        new = "ai-scorecard-2026-11-mktdiff"
        stages.init_run(new, from_run=SLUG, title="시장 지표 diff")
        stages.collect(new, kinds=("market",), from_file=self.file, now=NOW)
        res = compare_inputs(new, SLUG, set())
        self.assertTrue(res["ok"], res["violations"])
        self.assertEqual(len([x for x in res["by_file"]["observations"]["allowed"] if x.startswith("_market.")]), 8)


def obs(metric: str, value: float | None, as_of: str, basis: dict) -> dict:
    return {"observation_id": f"_market.{metric}.{as_of}.{basis.get('gpu', '')}", "company_id": MARKET_COMPANY_ID,
            "metric": metric, "value": value, "unit": mn.UNITS[metric], "as_of": as_of, "kind": "actual",
            "source_id": "SRC-X", "status": "verified", "basis": basis}


class RenderTest(unittest.TestCase):
    def ctx(self, items: list[dict]) -> SimpleNamespace:
        return SimpleNamespace(observations=items)

    def test_no_snapshot_draws_live_trend_only(self):
        """2026-11-15 사용자 결정: 시장 관측이 없는 실행도 지금 값 표와 추이 버튼을 낸다. 기준일 값(data-base)과 변화 칸은 없다."""
        from scorecard.render_html import render_market
        self.assertIsNone(rc.market_view(self.ctx([])))
        ctx = SimpleNamespace(observations=[], run={"as_of": "2026-10-27", "price_as_of": "2026-10-26"})
        html = render_market(ctx)
        self.assertIn('<button type="button" class="mkt-btn">다시 받기</button>', html)
        self.assertIn('<div class="mkt-charts"></div>', html)
        self.assertEqual(html.count("data-key="), len(rc.MARKET_ROWS))
        self.assertIn('data-key="gpu_rent_hourly:B200" data-kind="usd" data-unit="$/GPU·시간" data-base="" data-asof="2026-10-26"', html)
        self.assertEqual(html.count('data-base=""'), len(rc.MARKET_ROWS))
        self.assertNotIn("mkt-chg", html)
        self.assertIn("FRED BAA10Y", html)

    def test_latest_row_per_metric_and_html_hooks(self):
        from scorecard.render_html import render_market
        items = [obs("ust10y_yield", 4.0, "2026-09-20", {"series": "DGS10"}), obs("ust10y_yield", 4.1, "2026-09-25", {"series": "DGS10"}),
                 obs("gpu_rent_hourly", 2.5, "2026-09-30", {"gpu": "H200", "gpus": 3, "offers": 2}),
                 obs("token_blended_price", 3.5, "2026-09-30", {"segment": "frontier", "picks": [{"lab": "openai", "model": "openai/b", "blended": 4.0}]})]
        view = rc.market_view(self.ctx(items))
        self.assertEqual([r["key"] for r in view["rows"]], ["ust10y_yield", "gpu_rent_hourly:H200", "token_blended_price"])
        self.assertEqual(view["md_rows"][0][:3], ["미국채 10년물 금리", "4.10%", "2026-09-25"])
        self.assertIn("고른 모델: openai/b $4.00.", view["notes"])
        html = render_market(self.ctx(items))
        self.assertIn('data-key="gpu_rent_hourly:H200" data-kind="usd" data-unit="$/GPU·시간" data-base="2.5"', html)
        self.assertIn('<button type="button" class="mkt-btn">다시 받기</button>', html)
        self.assertIn('data-asof="2026-09-30"', html)
        self.assertIn('<div class="mkt-range" role="group" aria-label="차트 기간" hidden></div><div class="mkt-charts"></div>', html)
        self.assertIn('role="status" aria-live="polite"', html)

    def test_token_index_becomes_a_table_row_without_trend_hook(self):
        """2026-11-15 사용자 결정: 시장 지표 절이 있으면 토큰 단가 지수는 표의 한 줄이고 추이 스크립트가 읽는 data-key 가 없다."""
        from scorecard.render_html import render_market
        items = [obs("ust10y_yield", 4.1, "2026-09-25", {"series": "DGS10"})]
        tok = [{"segment": "broad", "value": 0.97, "as_of": "2026-10-10", "source_id": "SRC-SD", "previous": None, "change": None}]
        html = render_market(self.ctx(items), tok, "주의 문구.")
        row = re.search(r"<tr><td class=\"name\"><b>토큰 지출 지수\([^<]+\)</b></td>.*?</tr>", html)
        self.assertIsNotNone(row)
        self.assertNotIn("data-key", row.group(0))
        self.assertIn("$0.97", row.group(0))
        self.assertIn("과거 값이 유료라 추이를 그리지 않는다. 주의 문구.", html)
        self.assertEqual(html.count("data-key="), 1)
        live = render_market(self.ctx([]), tok)
        tok_row = re.search(r"<tr><td class=\"name\"><b>토큰 지출 지수\([^<]+\)</b></td>.*?</tr>", live)
        self.assertIsNotNone(tok_row, "시장 관측이 없어도 토큰 지수는 추이 절의 표 한 줄로 남는다")
        self.assertIn("$0.97", tok_row.group(0))
        self.assertNotIn("data-key", tok_row.group(0))


if __name__ == "__main__":
    unittest.main()
