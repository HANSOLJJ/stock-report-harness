# 수집한 공급원별 원자료에서 F6-H(2A+2E) 충족 여부와 기준 항목을 표로 비교한다
"""`collect.py` 가 남긴 `_raw/` 를 읽어 공급원별로 판정한다. 네트워크를 쓰지 않는다.

판정 기준
    2A : 최근 확정 2개 분기 실적 EPS 를 그 공급원에서 얻는가
    2E : 향후 2개 분기 컨센서스 EPS 를 그 공급원에서 얻는가
    통과: 12개사 전부에서 2A·2E 를 모두 얻어야 한다. 종목별 공급원 혼합은 금지다.

사용:
    python compare.py
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = HERE / "_raw"
TICKERS = ["META", "NVDA", "GOOGL", "MSFT", "AMZN", "AAPL", "ORCL", "PLTR", "TSLA", "SPCX", "TSM", "BABA"]
TODAY = date(2026, 9, 9)


def load(provider: str, ticker: str) -> dict | None:
    p = RAW / provider / f"{ticker}.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.is_file() else None


def finnhub_counts(ticker: str) -> tuple[int, int, list]:
    """(2A 개수, 2E 개수, 음수/결측 메모)."""
    rec = load("finnhub", ticker) or {}
    notes = []
    try:
        past = json.loads(rec["past"]["body"])
    except Exception:
        past = []
    actuals = [r for r in past if isinstance(r, dict) and r.get("actual") is not None]
    neg = [r["period"] for r in actuals if r["actual"] < 0]
    if neg:
        notes.append(f"음수 실적 {len(neg)}건")
    try:
        fut = json.loads(rec["future"]["body"]).get("earningsCalendar", [])
    except Exception:
        fut = []
    ests = [r for r in fut if r.get("epsEstimate") is not None and r.get("epsActual") is None]
    return len(actuals), len(ests), notes


def fmp_status(ticker: str) -> str:
    rec = load("fmp", ticker) or {}
    q = rec.get("quarter", {})
    body = (q.get("body") or "")[:80].replace("\n", " ")
    return f"HTTP {q.get('http')} — {body}"


def yahoo_counts(ticker: str) -> tuple[int, int, dict, list]:
    rec = load("yahoo", ticker) or {}
    est = rec.get("earnings_estimate") or {}
    quarters = [k for k in ("0q", "+1q") if k in est]
    rows = [est[k] for k in quarters]
    n_e = sum(1 for r in rows if r.get("avg") is not None)
    dates = rec.get("earnings_dates") or []
    n_a = sum(1 for r in dates if r.get("Reported EPS") is not None)
    notes = []
    negs = [r for r in dates if isinstance(r.get("Reported EPS"), (int, float)) and r["Reported EPS"] < 0]
    if negs:
        notes.append(f"음수 실적 {len(negs)}건")
    # 통화는 전망 행 자체의 currency 를 읽는다. info.currency 는 매매 통화라 다를 수 있다.
    cur = sorted({r.get("currency") for r in rows if r.get("currency")}) or ["—"]
    trade = (rec.get("basis") or {}).get("currency")
    if trade and cur[0] != trade:
        notes.append(f"전망 통화 {cur[0]} != 매매 통화 {trade}")
    fields = {"currency": "/".join(cur),
              "trade_currency": trade,
              "n": bool(rows) and all(r.get("numberOfAnalysts") is not None for r in rows),
              "minmax": bool(rows) and all(r.get("low") is not None and r.get("high") is not None for r in rows)}
    return n_a, n_e, fields, notes


def main() -> None:
    meta = json.loads((RAW / "meta.json").read_text(encoding="utf-8"))
    print("=" * 110)
    print(f"F6-H 공급원별 일괄 확보 조사 — 조회 시점(UTC) {meta['collected_at_utc']}")
    print(f"대상 {len(TICKERS)}개사 · 전망 창 {meta['forecast_window'][0]}~{meta['forecast_window'][1]}")
    print(f"제외: {list(meta['excluded'])[0]} — {list(meta['excluded'].values())[0]}")
    print("=" * 110)

    print("\n[A] Finnhub — stock/earnings(2A) + calendar/earnings(2E)")
    print(f"{'티커':7} {'실적수':>6} {'전망수':>6} {'2A':>4} {'2E':>4} {'판정':>6}  비고")
    fh_pass = 0
    for t in TICKERS:
        na, ne, notes = finnhub_counts(t)
        ok = na >= 2 and ne >= 2
        fh_pass += ok
        print(f"{t:7} {na:>6} {ne:>6} {'O' if na>=2 else 'X':>4} {'O' if ne>=2 else 'X':>4} {'통과' if ok else '미달':>6}  {'; '.join(notes)}")
    print(f"  → 12개사 중 통과 {fh_pass}개사")

    print("\n[B] FMP — stable/analyst-estimates?period=quarter")
    for t in TICKERS[:3]:
        print(f"{t:7} {fmp_status(t)}")
    codes = {json.loads((RAW / 'fmp' / f'{t}.json').read_text(encoding='utf-8'))['quarter']['http'] for t in TICKERS}
    print(f"  → 12개사 응답 코드 집합 {codes} · 통과 0개사")

    print("\n[C] SEC XBRL — 실적 전용")
    us = sum(1 for t in TICKERS if (load('sec', t) or {}).get('quarterly_eps'))
    print(f"  분기 EPS 조회 가능 {us}/12 (20-F 제출사 TSM·BABA 제외)")
    print("  전망 필드 없음 → 2E 확보 0개사 · 통과 0개사")

    print()
    print("[D] Yahoo (yfinance) - earnings_estimate(2E) + earnings_dates(2A)  * allowlist 미등재")
    print(f"{'티커':7} {'실적수':>6} {'전망수':>6} {'2A':>4} {'2E':>4} {'전망통화':>8} {'매매통화':>8} {'표본n':>6} {'min/max':>8} {'판정':>6}  비고")
    y_pass = 0
    for t in TICKERS:
        na, ne, f, notes = yahoo_counts(t)
        ok = na >= 2 and ne >= 2
        y_pass += ok
        print(f"{t:7} {na:>6} {ne:>6} {'O' if na>=2 else 'X':>4} {'O' if ne>=2 else 'X':>4} "
              f"{f['currency']:>8} {str(f['trade_currency']):>8} {'O' if f['n'] else 'X':>6} "
              f"{'O' if f['minmax'] else 'X':>8} {'통과' if ok else '미달':>6}  {'; '.join(notes)}")
    print(f"  -> 12개사 중 통과 {y_pass}개사")

    print()
    print("[E] 기준 항목 비교 - 공급원이 무엇을 명시하는가")
    print(f"{'항목':22} {'Finnhub':>10} {'FMP(무료)':>11} {'SEC':>11} {'Yahoo':>10}")
    matrix = [
        ("2A 확보(12개사)", "11", "0", "10*", "11"),
        ("2E 확보(12개사)", "11", "0", "0", "12"),
        ("asOf/추정시각", "없음", "-", "filed 있음", "없음"),
        ("회계기준 명시", "없음", "-", "us-gaap", "없음"),
        ("통화 필드", "없음", "-", "단위에 포함", "있음"),
        ("ADR/ADS 기준 명시", "없음", "-", "없음", "없음"),
        ("표본 수", "없음", "-", "해당없음", "있음"),
        ("min/max", "없음", "-", "해당없음", "있음"),
    ]
    for row in matrix:
        print(f"{row[0]:22} {row[1]:>10} {row[2]:>11} {row[3]:>11} {row[4]:>10}")
    print("  * SEC 는 실적만. 20-F 제출사(TSM·BABA) 제외 10개사이며 회계 4분기는 연간에서 복원해야 한다.")


    print("\n" + "=" * 110)
    print("종합 — 한 공급원이 12개사 전체를 커버하는가")
    print("=" * 110)
    print(f"  Finnhub  {fh_pass}/12   (allowlist 등재)")
    print("  FMP      0/12    (allowlist 등재 · 무료 등급에서 분기 파라미터·심볼 차단)")
    print("  SEC      0/12    (allowlist 등재 · 전망 필드 자체가 없음)")
    print(f"  Yahoo    {y_pass}/12   (allowlist 미등재 — 채택 후보 아님)")


if __name__ == "__main__":
    main()
