# yfinance 가격·시총 관측 수집기(EPS·컨센서스 미수집)
from __future__ import annotations

from datetime import date, timedelta
from typing import Any


def fetch_quote(ticker: str, price_as_of: str) -> dict[str, Any]:
    """저장소에서 유일한 yfinance 호출 지점. import는 이 함수 안에서만 한다."""
    import yfinance as yf  # noqa: E402

    as_of = date.fromisoformat(price_as_of)
    stock = yf.Ticker(ticker)
    hist = stock.history(start=(as_of - timedelta(days=10)).isoformat(),
                         end=(as_of + timedelta(days=1)).isoformat(), auto_adjust=False)
    closes: list[tuple[str, float]] = []
    for idx, row in hist.iterrows():
        day = idx.date() if hasattr(idx, "date") else date.fromisoformat(str(idx)[:10])
        if day <= as_of:
            closes.append((day.isoformat(), float(row["Close"])))
    if not closes:
        raise ValueError(f"{ticker}: {price_as_of} 이하 거래일 종가 없음")
    close_date, close = closes[-1]

    market_cap = None
    shares_outstanding = None
    currency = None
    try:
        fast = stock.fast_info
        market_cap = fast.market_cap if fast.market_cap is not None else None
        shares_outstanding = fast.shares if fast.shares is not None else None
        currency = fast.currency
    except Exception:  # noqa: BLE001 — fast_info 실패는 info로 넘긴다
        pass
    if market_cap is None or shares_outstanding is None or currency is None:
        try:
            info = stock.info or {}
        except Exception:  # noqa: BLE001 — info 실패는 결측으로 둔다
            info = {}
        if market_cap is None:
            market_cap = info.get("marketCap")
        if shares_outstanding is None:
            shares_outstanding = info.get("sharesOutstanding")
        if currency is None:
            currency = info.get("currency")
    return {
        "close": close,
        "close_date": close_date,
        "market_cap": float(market_cap) if market_cap is not None else None,
        "shares_outstanding": int(shares_outstanding) if shares_outstanding is not None else None,
        "currency": currency,
    }


def price_observations(
    company: dict[str, Any], quote: dict[str, Any], *, price_as_of: str, source_id: str
) -> list[dict[str, Any]]:
    """상장사 가격·시총 관측 둘. 비상장은 빈 리스트. 통화 비USD는 예외."""
    if not company.get("listed"):
        return []
    currency = quote.get("currency")
    if currency != "USD":
        raise ValueError(f"{company.get('company_id')}: 통화 {currency!r} — USD만 관측한다")
    company_id = company["company_id"]
    close_date = quote["close_date"]
    price_obs = {
        "observation_id": f"{company_id}.price.{close_date}",
        "company_id": company_id,
        "metric": "price",
        "value": quote["close"],
        "unit": "USD/share",
        "as_of": close_date,
        "kind": "actual",
        "source_id": source_id,
        "status": "verified",
        "basis": {"currency": currency, "share_basis": company.get("share_basis"),
                  "adr_ratio": company.get("adr_ratio")},
    }
    market_cap = quote.get("market_cap")
    shares = quote.get("shares_outstanding")
    if market_cap is not None:
        method = "vendor_market_cap"
        value = market_cap
    elif shares is not None:
        method = "price_x_shares"
        value = quote["close"] * shares
    else:
        method = "price_x_shares"
        value = None
    market_obs = {
        "observation_id": f"{company_id}.market_cap.{close_date}",
        "company_id": company_id,
        "metric": "market_cap",
        "value": value,
        "unit": "USD",
        "as_of": close_date,
        "kind": "actual",
        "source_id": source_id,
        "status": "verified" if value is not None else "collection_failed",
        "basis": {"method": method, "shares_outstanding": shares},
    }
    _ = price_as_of
    return [price_obs, market_obs]


def price_source_entry(price_as_of: str, *, tickers: list[str], accessed_at: str) -> dict[str, Any]:
    entry: dict[str, Any] = {
        "source_id": f"SRC-YF-{price_as_of}",
        "title": f"Yahoo Finance 일봉 종가·시총({price_as_of} 기준)",
        "publisher": "Yahoo Finance via yfinance",
        "url": f"https://finance.yahoo.com/quote/{tickers[0]}",
        "accessed_at": accessed_at,
        "sha256": None,
        "conflict_of_interest": None,
        "note": "가격·시총 관측 전용, EPS·컨센서스 미수집",
    }
    if len(tickers) > 1:
        entry["publisher_url"] = [f"https://finance.yahoo.com/quote/{t}" for t in tickers]
    return entry
