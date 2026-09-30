# yfinance 가격·시총 관측 수집기(EPS·컨센서스 미수집)
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
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
        # fast_info·info 의 시총·발행주식수는 **조회 시점** 값이다. 종가 날짜와 어긋나는지 보려고 조회일을 남긴다.
        "fetched_at": datetime.now(timezone.utc).date().isoformat(),
    }


def _vendor_cap_is_fresh(quote: dict[str, Any]) -> bool:
    """조회일(UTC)이 종가 날짜와 같거나 하루 뒤일 때만 벤더 시총이 그 날짜의 값이다."""
    fetched = quote.get("fetched_at")
    if not fetched:
        return False
    gap = (date.fromisoformat(fetched) - date.fromisoformat(quote["close_date"])).days
    return 0 <= gap <= 1


def price_observations(company: dict[str, Any], quote: dict[str, Any], *, source_id: str) -> list[dict[str, Any]]:
    """상장사 가격·시총 관측 둘. 비상장은 빈 리스트. 통화 비USD는 예외.

    2026-09-30 레인 E: 시총은 조회 시점 값인데 관측 as_of 는 종가 날짜다. 과거 기준일로 조회하면
    둘이 어긋나므로 (1) 조회일이 종가일과 하루 이내일 때만 `vendor_market_cap` 을 쓰고 (2) 그 밖에는
    `price_x_shares` 로 계산하되 발행주식수가 조회 시점 값임을 basis 에 남긴다. (3) ADR·ADS 는 발행주식수가
    보통주인지 증서인지 보장되지 않으므로 `vendor_market_cap` 만 쓰고, 그것도 못 쓰면 `collection_failed` 다.
    """
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
    fetched = quote.get("fetched_at")
    is_adr = company.get("share_basis") in ("adr", "ads")
    note = None
    if market_cap is not None and _vendor_cap_is_fresh(quote):
        value = market_cap
        basis = {"method": "vendor_market_cap", "shares_outstanding": shares, "fetched_at": fetched}
    elif is_adr:
        # 추정으로 채우지 않는다. ADR 가격 × (무엇을 센 것인지 모르는) 주식수는 값이 아니다.
        value = None
        basis = {"method": "vendor_market_cap", "shares_outstanding": shares, "fetched_at": fetched}
        note = (f"ADR 시총은 종가일({close_date})과 하루 이내에 조회한 vendor_market_cap 만 쓴다 — "
                f"조회일 {fetched or '미상'}, 벤더 시총 {'있음' if market_cap is not None else '없음'}")
    elif shares is not None:
        value = quote["close"] * shares
        basis = {"method": "price_x_shares", "shares_outstanding": shares,
                 "shares_as_of": fetched, "shares_timing": "current_at_fetch"}
    else:
        value = None
        basis = {"method": "price_x_shares", "shares_outstanding": None,
                 "shares_as_of": fetched, "shares_timing": "current_at_fetch"}
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
        "basis": basis,
    }
    if note:
        market_obs["note"] = note
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
