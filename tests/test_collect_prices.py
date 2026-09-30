# collect_prices 단위 테스트(네트워크 금지, DATA_ROOT는 tempfile)
from __future__ import annotations

import ast
import json
import re
import sys
import types
import unittest
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard import collect_prices  # noqa: E402
from scorecard.collect_prices import fetch_quote, price_observations, price_source_entry  # noqa: E402
from scorecard.schema import validate_observations  # noqa: E402

FIXTURE = ROOT / "tests" / "fixtures" / "yfinance_quotes.sample.json"

NVIDIA = {"company_id": "nvidia", "display_name": "NVIDIA", "listed": True, "ticker": "NVDA",
          "share_basis": "common", "adr_ratio": None, "reporting_currency": "USD"}
ANTHROPIC = {"company_id": "anthropic", "listed": False, "ticker": None,
             "share_basis": "private", "adr_ratio": None, "reporting_currency": "USD"}
OPENAI = {"company_id": "openai", "listed": False, "ticker": None,
          "share_basis": "private", "adr_ratio": None, "reporting_currency": "USD"}


def quotes() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


class ObservationsTest(unittest.TestCase):
    def test_two_observations_validate(self):
        # 2026-09-30 레인 E: 벤더 시총은 조회일이 종가일과 하루 이내일 때만 쓴다. NVDA 실측은 09-29 종가를 09-30 에 조회했다.
        quote = dict(quotes()["NVDA"], fetched_at="2026-09-30")
        obs = price_observations(NVIDIA, quote, source_id="SRC-YF-2026-09-29")
        self.assertEqual([o["metric"] for o in obs], ["price", "market_cap"])
        for item in obs:
            self.assertEqual(item["status"], "verified")
            self.assertEqual(item["kind"], "actual")
            self.assertEqual(item["as_of"], "2026-09-29")
        payload = {"schema": "scorecard.observations/1", "run_id": "t", "items": obs}
        companies = {"nvidia": {"listed": True}}
        self.assertEqual(validate_observations(payload, companies, "t"), obs)
        price = obs[0]
        self.assertEqual(price["unit"], "USD/share")
        self.assertEqual(price["basis"],
                         {"currency": "USD", "share_basis": "common", "adr_ratio": None})
        market = obs[1]
        self.assertEqual(market["unit"], "USD")
        self.assertEqual(market["basis"]["method"], "vendor_market_cap")

    def test_price_x_shares_fallback(self):
        quote = {"close": 10.0, "close_date": "2026-09-29", "market_cap": None,
                 "shares_outstanding": 100, "currency": "USD"}
        obs = price_observations(NVIDIA, quote, source_id="s")
        self.assertEqual(obs[1]["value"], 1000.0)
        self.assertEqual(obs[1]["basis"]["method"], "price_x_shares")
        self.assertEqual(obs[1]["basis"]["shares_timing"], "current_at_fetch")


class MarketCapTimingTest(unittest.TestCase):
    """2026-09-30 레인 E: 시총·발행주식수는 조회 시점 값이다. 종가 날짜와 어긋나면 벤더 시총을 쓰지 않는다."""

    TSMC = dict(NVIDIA, company_id="tsmc", ticker="TSM", share_basis="adr", adr_ratio=5)
    BABA = dict(NVIDIA, company_id="alibaba", ticker="BABA", share_basis="ads", adr_ratio=8)

    def cap(self, company: dict, **quote_kw) -> dict:
        quote = {"close": 10.0, "close_date": "2026-09-25", "market_cap": 5000.0,
                 "shares_outstanding": 100, "currency": "USD"}
        quote.update(quote_kw)
        return price_observations(company, quote, source_id="s")[1]

    def test_same_day_and_next_day_use_vendor(self):
        for fetched in ("2026-09-25", "2026-09-26"):
            with self.subTest(fetched=fetched):
                obs = self.cap(NVIDIA, fetched_at=fetched)
                self.assertEqual((obs["basis"]["method"], obs["value"]), ("vendor_market_cap", 5000.0))

    def test_historical_as_of_does_not_use_vendor(self):
        for fetched in ("2026-09-30", None):
            with self.subTest(fetched=fetched):
                obs = self.cap(NVIDIA, fetched_at=fetched)
                self.assertEqual(obs["basis"]["method"], "price_x_shares")
                self.assertEqual(obs["value"], 1000.0)
                self.assertEqual(obs["basis"]["shares_as_of"], fetched)
                self.assertEqual(obs["basis"]["shares_timing"], "current_at_fetch")
                self.assertEqual(obs["as_of"], "2026-09-25")

    def test_adr_never_uses_price_x_shares(self):
        for company in (self.TSMC, self.BABA):
            for kw in ({"fetched_at": "2026-09-30"}, {"fetched_at": None},
                       {"fetched_at": "2026-09-25", "market_cap": None}):
                with self.subTest(company=company["company_id"], kw=kw):
                    obs = self.cap(company, **kw)
                    self.assertEqual(obs["status"], "collection_failed")
                    self.assertIsNone(obs["value"])
                    self.assertNotEqual(obs["basis"]["method"], "price_x_shares")
                    self.assertIn("ADR", obs["note"])

    def test_adr_fresh_vendor_is_used(self):
        obs = self.cap(self.TSMC, fetched_at="2026-09-26")
        self.assertEqual((obs["status"], obs["value"]), ("verified", 5000.0))

    def test_failed_observations_still_validate(self):
        items = price_observations(self.TSMC, {"close": 10.0, "close_date": "2026-09-25", "market_cap": None,
                                               "shares_outstanding": 100, "currency": "USD"}, source_id="s")
        payload = {"schema": "scorecard.observations/1", "run_id": "t", "items": items}
        validate_observations(payload, {"tsmc": {"listed": True}}, "t")

    def test_unlisted_empty(self):
        quote = quotes()["NVDA"]
        self.assertEqual(price_observations(ANTHROPIC, quote,
                                            source_id="s"), [])
        self.assertEqual(price_observations(OPENAI, quote,
                                            source_id="s"), [])

    def test_non_usd_raises(self):
        quote = dict(quotes()["NVDA"], currency="KRW")
        with self.assertRaises(ValueError):
            price_observations(NVIDIA, quote, source_id="s")

    def test_no_eps_keys(self):
        quote = quotes()["NVDA"]
        obs = price_observations(NVIDIA, quote, source_id="s")
        blob = json.dumps(obs)
        self.assertNotIn("eps", blob.lower())
        for key in quote:
            self.assertNotIn("eps", key.lower())

    def test_collection_failed_without_any_cap_input(self):
        quote = dict(quotes()["SPCX"])
        obs = price_observations(
            dict(NVIDIA, company_id="spacex-xai", ticker="SPCX"),
            quote, source_id="s")
        self.assertEqual(obs[1]["status"], "collection_failed")
        self.assertIsNone(obs[1]["value"])


class SourceEntryTest(unittest.TestCase):
    def test_single_and_multi_ticker(self):
        one = price_source_entry("2026-09-29", tickers=["NVDA"], accessed_at="2026-09-30")
        self.assertEqual(one["source_id"], "SRC-YF-2026-09-29")
        self.assertEqual(one["url"], "https://finance.yahoo.com/quote/NVDA")
        self.assertEqual(one["publisher"], "Yahoo Finance via yfinance")
        self.assertIsNone(one["sha256"])
        self.assertNotIn("publisher_url", one)
        multi = price_source_entry("2026-09-29", tickers=["NVDA", "AAPL"], accessed_at="2026-09-30")
        self.assertEqual(len(multi["publisher_url"]), 2)


class FetchQuoteTest(unittest.TestCase):
    def _install_stub(self, rows: list[tuple[str, float]]):
        import pandas as pd

        class FastInfo:
            market_cap = 1000.0
            shares = 100
            currency = "USD"

        class Ticker:
            def __init__(self, ticker: str):
                self.ticker = ticker

            def history(self, **kw: object) -> object:
                idx = pd.to_datetime([d for d, _ in rows])
                return pd.DataFrame({"Close": [c for _, c in rows]}, index=idx)

            @property
            def fast_info(self) -> FastInfo:
                return FastInfo()

        stub = types.ModuleType("yfinance")
        stub.Ticker = Ticker
        sys.modules["yfinance"] = stub
        self.addCleanup(sys.modules.pop, "yfinance", None)

    def test_last_trading_day_on_or_before_asof(self):
        # price_as_of가 일요일이면 금요일 종가를 쓴다
        self._install_stub([("2026-09-25", 225.07), ("2026-09-28", 228.86)])
        quote = fetch_quote("NVDA", "2026-09-27")
        self.assertEqual(quote["close_date"], "2026-09-25")
        self.assertEqual(quote["close"], 225.07)
        self.assertEqual(quote["currency"], "USD")
        # 조회일을 남겨야 price_observations 가 벤더 시총의 시점을 판정한다.
        self.assertEqual(quote["fetched_at"], datetime.now(timezone.utc).date().isoformat())

    def test_no_rows_raises(self):
        self._install_stub([])
        with self.assertRaises(ValueError):
            fetch_quote("NVDA", "2026-09-29")


class ImportPinTest(unittest.TestCase):
    def test_yfinance_import_only_inside_fetch_quote(self):
        """yfinance import는 collect_prices.fetch_quote 함수 안 하나다."""
        tree = ast.parse((ROOT / "scripts" / "scorecard" / "collect_prices.py").read_text(
            encoding="utf-8"))
        hits = [(node.lineno, stack) for node, stack in _walk(tree) if _is_yf_import(node)]
        self.assertEqual(len(hits), 1)
        _, stack = hits[0]
        self.assertIn("fetch_quote", stack)

    def test_yfinance_importing_files_are_pinned(self):
        found = set()
        for path in sorted((ROOT / "scripts").rglob("*.py")):
            for line in path.read_text(encoding="utf-8").splitlines():
                if re.match(r"\s*(import yfinance|from yfinance)\b", line):
                    found.add(path.relative_to(ROOT).as_posix())
        # 2026-09-30 레인 A: build_report.py 의 종목 차트 yfinance 코드를 지워 scripts/ 전체에서 호출 지점은 하나다.
        self.assertEqual(found, {"scripts/scorecard/collect_prices.py"})


def _walk(tree: ast.AST) -> list[tuple[ast.AST, tuple[str, ...]]]:
    out: list[tuple[ast.AST, tuple[str, ...]]] = []

    def visit(node: ast.AST, stack: tuple[str, ...]) -> None:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            stack = stack + (node.name,)
        out.append((node, stack))
        for child in ast.iter_child_nodes(node):
            visit(child, stack)

    visit(tree, ())
    return out


def _is_yf_import(node: ast.AST) -> bool:
    if isinstance(node, ast.Import):
        return any(a.name.split(".")[0] == "yfinance" for a in node.names)
    if isinstance(node, ast.ImportFrom):
        return (node.module or "").split(".")[0] == "yfinance"
    return False


if __name__ == "__main__":
    unittest.main()
