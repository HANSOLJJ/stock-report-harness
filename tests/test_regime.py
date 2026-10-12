# 국면 지표(규칙 v2.1 2-C-1, 점수 없음)의 시장 지표 관측·설비투자 가속도·공급자 지원 비중·토큰 지수·트리거 조건을 잠그는 테스트
from __future__ import annotations

import json
import os
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
os.environ["SCORECARD_DOTENV"] = ""

from scorecard import stages  # noqa: E402
from scorecard.engine import COMPANIES_PATH  # noqa: E402
from scorecard.schema import (MARKET_COMPANY_ID, SchemaError, load_json_strict, validate_companies,  # noqa: E402
                              validate_observations, write_json)
from tests.test_collect_stage import SLUG, Sandbox  # noqa: E402

COMPANIES = validate_companies(load_json_strict(COMPANIES_PATH))


def token(value: float = 1.02, *, cid: str = MARKET_COMPANY_ID, metric: str = "token_price_index", segment: str | None = "frontier",
          as_of: str = "2026-08-16") -> dict:
    o = {"observation_id": f"{cid}.{metric}.{as_of}", "company_id": cid, "metric": metric, "value": value, "unit": "USD",
         "as_of": as_of, "kind": "actual", "source_id": "SRC-T", "status": "verified"}
    if segment is not None:
        o["basis"] = {"segment": segment}
    return o


def payload(*items: dict) -> dict:
    return {"schema": "scorecard.observations/1", "run_id": "x", "items": list(items)}


class MarketObservationTest(unittest.TestCase):
    def test_token_index_only_with_market_id(self):
        validate_observations(payload(token()), COMPANIES)
        for bad in (token(cid="nvidia"), token(metric="price_per_m"), token(segment=None), token(segment="retail"), token(-1.0)):
            with self.subTest(bad=(bad["company_id"], bad["metric"], (bad.get("basis") or {}).get("segment"), bad["value"])):
                with self.assertRaises(SchemaError):
                    validate_observations(payload(bad), COMPANIES)

    def test_from_run_keeps_market_observations(self):
        box = Sandbox(("nvidia",))
        self.addCleanup(box.close)
        obs_path = box.run_dir / "observations.json"
        obs = load_json_strict(obs_path)
        obs["items"].append(token())
        write_json(obs_path, obs)
        src_path = box.run_dir / "sources.json"
        src = load_json_strict(src_path) if src_path.is_file() else {"schema": "scorecard.sources/1", "run_id": SLUG, "items": []}
        src["items"].append({"source_id": "SRC-T", "title": "Silicon Data LLM Token Expenditure Index", "publisher": "Silicon Data",
                             "url": "https://www.silicondata.com/products/silicon-index/llm-token-expenditure-index",
                             "accessed_at": "2026-10-12", "sha256": None, "conflict_of_interest": None, "note": "공개 페이지 최신 값"})
        write_json(src_path, src)
        new = "ai-scorecard-2026-11-market"
        stages.init_run(new, from_run=SLUG, title="이어받기")
        items = load_json_strict(box.dir / "output" / new / "observations.json")["items"]
        self.assertEqual([o["metric"] for o in items if o["company_id"] == MARKET_COMPANY_ID], ["token_price_index"])


from scorecard.inputs import ObsLookup  # noqa: E402
from scorecard.regime import (TRIGGER_IDS, acceleration, calendar_key, company_capex, regime_board, regime_spec,  # noqa: E402
                              shift)
from scorecard.rules import load_rules  # noqa: E402

V20, V21 = load_rules("v2.0"), load_rules("v2.1")
SPEC = regime_spec(V21)
CAPEX = SPEC["capex"]
QUARTER_ENDS = ["2024-09-30", "2024-12-31", "2025-03-31", "2025-06-30", "2025-09-30", "2025-12-31", "2026-03-31", "2026-06-30"]


def q(cid: str, metric: str, end: str, value: float) -> dict:
    start = {"03-31": "01-01", "06-30": "04-01", "09-30": "07-01", "12-31": "10-01"}[end[5:]]
    return {"observation_id": f"{cid}.{metric}.{end}", "company_id": cid, "metric": metric, "value": value, "unit": "USD",
            "as_of": end, "kind": "derived", "source_id": "SRC-T", "status": "verified",
            "period": {"start": f"{end[:4]}-{start}", "end": end}}


def series(values: list[float]) -> dict:
    """마지막 값이 최근 분기인 달력 분기 시계열."""
    keys = [calendar_key(e) for e in QUARTER_ENDS[-len(values):]]
    return dict(zip(keys, values))


class AccelerationTest(unittest.TestCase):
    def test_calendar_key_aligns_offset_fiscal_quarters(self):
        self.assertEqual([calendar_key(e) for e in ("2026-05-31", "2025-08-31", "2025-11-30", "2026-02-28")],
                         [(2026, 2), (2025, 3), (2025, 4), (2026, 1)])
        self.assertEqual(shift((2026, 1), 4), (2025, 1))
        self.assertEqual(shift((2026, 1), 1), (2025, 4))

    def test_direction_follows_growth_change(self):
        # 1년 전 분기는 모두 100, 직전 분기 150(+50%) → 최근 분기 값으로 방향이 갈린다
        for last, want in ((180, "accelerating"), (150.5, "steady"), (120, "decelerating")):
            with self.subTest(last=last):
                r = acceleration(series([100, 100, 100, 100, 150, last]), CAPEX)
                self.assertEqual((r["status"], r["direction"]), ("ok", want))
        r = acceleration(series([100, 100, 100, 100, 150, 120]), CAPEX)
        self.assertAlmostEqual(r["change"], 0.2 - 0.5)

    def test_insufficient_below_six_quarters_or_gap(self):
        self.assertEqual(acceleration(series([100, 100, 100, 150, 160]), CAPEX)["status"], "insufficient")
        gappy = series([100, 100, 100, 100, 150, 160])
        del gappy[sorted(gappy)[1]]     # 직전 분기의 1년 전 값이 빠짐
        gappy[(2023, 1)] = 1.0          # 분기 수는 6 으로 맞춘다
        r = acceleration(gappy, CAPEX)
        self.assertEqual((r["status"], r.get("gap")), ("insufficient", True))

    def test_two_quarter_deceleration_needs_seven_quarters(self):
        self.assertIsNone(acceleration(series([100, 100, 100, 100, 190, 150]), CAPEX)["two_quarter_deceleration"])
        self.assertTrue(acceleration(series([100, 100, 100, 100, 190, 170, 150]), CAPEX)["two_quarter_deceleration"])
        self.assertFalse(acceleration(series([100, 100, 100, 100, 150, 170, 150]), CAPEX)["two_quarter_deceleration"])


class CapexBoardTest(unittest.TestCase):
    def test_finance_lease_added_only_when_complete(self):
        capex = [q("meta", "capex_quarterly", e, 100) for e in QUARTER_ENDS]
        full = [q("meta", "finance_lease_additions_quarterly", e, 10) for e in QUARTER_ENDS]
        r = company_capex(ObsLookup(capex + full), "meta", 8)
        self.assertEqual((r["definition"], set(r["values"].values())), ("cash_plus_finance_lease", {110}))
        r = company_capex(ObsLookup(capex + full[1:]), "meta", 8)
        self.assertEqual((r["definition"], r["finance_lease_partial"], set(r["values"].values())), ("cash_only", True, {100}))

    def test_basket_sums_only_complete_quarters(self):
        obs = ([q("meta", "capex_quarterly", e, 100) for e in QUARTER_ENDS]
               + [q("amazon", "capex_quarterly", e, 50) for e in QUARTER_ENDS[1:]])
        board = regime_board(obs, ["meta", "amazon", "nvidia"], SPEC)["capex"]
        self.assertEqual(board["basket"]["members"], ["amazon", "meta"])
        self.assertEqual(set(board["basket"]["values"].values()), {150})
        self.assertEqual(len(board["basket"]["values"]), 7)
        self.assertEqual(set(board["missing_from_run"]), {"microsoft", "alphabet", "oracle"})


def stock(metric: str, value: float, as_of: str, cid: str = "nvidia") -> dict:
    return {"observation_id": f"{cid}.{metric}.{as_of}", "company_id": cid, "metric": metric, "value": value, "unit": "USD",
            "as_of": as_of, "kind": "actual", "source_id": "SRC-T", "status": "verified"}


def revenue(value: float, end: str) -> dict:
    return {**stock("revenue_ttm", value, end), "period": {"start": "2025-01-01", "end": end}}


class SupplierTokenTest(unittest.TestCase):
    PARTS = ("supplier_guarantees", "supplier_customer_investments", "supplier_capacity_buyback")

    def board(self, obs: list[dict]) -> dict:
        return regime_board(obs, ["nvidia"], SPEC)

    def test_ratio_and_rising(self):
        obs = [stock(m, v, "2026-04-26") for m, v in zip(self.PARTS, (5, 10, 15))] + [revenue(300, "2026-04-26")]
        obs += [stock(m, v, "2026-07-26") for m, v in zip(self.PARTS, (10, 20, 30))] + [revenue(400, "2026-07-26")]
        board = self.board(obs)
        s = board["supplier"][0]
        self.assertEqual((s["latest"]["total"], s["latest"]["ratio"], s["previous_ratio"], s["rising"]), (60, 0.15, 0.1, True))
        self.assertEqual({t["id"]: t["status"] for t in board["triggers"]}["supplier_support_rising"], "met")

    def test_missing_component_makes_no_total(self):
        obs = [stock(m, 5, "2026-07-26") for m in self.PARTS[:2]] + [revenue(400, "2026-07-26")]
        board = self.board(obs)
        s = board["supplier"][0]
        self.assertEqual((s["latest"]["total"], s["latest"]["ratio"], s["rising"]), (None, None, None))
        self.assertEqual({t["id"]: t["status"] for t in board["triggers"]}["supplier_support_rising"], "insufficient")

    def test_token_index_change(self):
        t = self.board([token(2.0, as_of="2026-07-16"), token(1.5, as_of="2026-08-16")])["token"][0]
        self.assertEqual((t["value"], t["previous"]["value"], t["change"]), (1.5, 2.0, -0.25))


class RegimeRenderTest(unittest.TestCase):
    def test_trigger_ids_match_schema_whitelist(self):
        self.assertEqual({t["id"] for t in SPEC["trigger_conditions"]}, TRIGGER_IDS)

    def test_v20_has_no_regime_and_v21_renders_both_formats(self):
        from types import SimpleNamespace

        from scorecard import render_common as rc
        from scorecard.render_html import render_regime
        from scorecard.render_md import _regime_section
        self.assertIsNone(regime_spec(V20))
        obs = [q("meta", "capex_quarterly", e, 100 + i * 10) for i, e in enumerate(QUARTER_ENDS)] + [token()]
        results = {"companies": [{"company_id": "meta", "display_name": "Meta"}, {"company_id": "nvidia", "display_name": "NVIDIA"}]}
        ctx = SimpleNamespace(rules=V21, observations=obs, run={"companies": ["meta", "nvidia"]})
        md = "\n".join(_regime_section(rc.regime_view(ctx, results)))
        self.assertIn("## 국면 지표 — 점수 없음", md)
        # 100, 110, …, 170: 증가율이 +40% → +36.4% → +33.3% → +30.8% 로 줄어 2개 분기 연속 감속이다
        self.assertIn("| Meta | 현금만 | 2026Q2(2026-06-30) | $170.00 | +30.8% | +33.3% | -2.6%p | 감속 | 예 |", md)
        self.assertIn("2개 분기 연속 감속 | 충족 |", md)
        self.assertIn("프런티어 모델: $1.02(2026-08-16", md)
        self.assertNotIn("1국면", md)
        self.assertIn("<h3>국면 지표 — 점수 없음</h3>", render_regime(ctx, results))
        self.assertEqual(render_regime(SimpleNamespace(rules=V20, observations=obs, run=ctx.run), results), "")

    @unittest.skipUnless((ROOT / "output" / "ai-scorecard-2026-10-recheck" / "run.json").is_file(), "recheck 실행 없음")
    def test_research_lists_market_observations(self):
        import dataclasses

        from scorecard.engine import load_context
        from scorecard.render_md import render_research
        ctx = load_context("ai-scorecard-2026-10-recheck")
        hashes = {"observations": "0" * 64, "judgments": "0" * 64}
        plain = render_research(ctx, hashes=hashes)
        self.assertNotIn("### 시장 지표", plain)
        md = render_research(dataclasses.replace(ctx, observations=[*ctx.observations, token()]), hashes=hashes)
        self.assertIn("### 시장 지표", md)
        self.assertIn("| token_price_index | $1.02 | verified |", md)


if __name__ == "__main__":
    unittest.main()
