# 공급원별로 12개 상장사를 동일 API·동일 시점·동일 필드로 조회해 F6-H(2A+2E) 충족 여부를 비교한다
"""종목별로 사이트를 골라 섞지 않는다. **공급원 하나가 12개사를 모두 커버하는가**를 본다.

F6-H 는 최근 확정 2개 분기 실적(2A)과 향후 2개 분기 컨센서스(2E)를 요구한다.
따라서 한 공급원이 두 가지를 모두 줘야 한다.

공급원
    finnhub  : stock/earnings(2A·과거 컨센서스) + calendar/earnings(2E)   [v1.6 allowlist]
    fmp      : stable/analyst-estimates?period=quarter                     [v1.6 allowlist]
    sec      : XBRL 분기 EPS — 실적만. 전망 없음                            [v1.6 allowlist]
    yahoo    : yfinance earnings_estimate(2E) + earnings_dates(2A)         [allowlist 미등재]

allowlist 미등재 공급원은 조사 대상에는 넣되 **채택 후보로 취급하지 않는다**
(`../f6-policy-decision-05/` 2.2, v1.6 rules.sources).

api.nasdaq.com 은 생산 배제라 호출하지 않는다(v1.6 denied).

사용:
    export FINNHUB_KEY=...  FMP_API_KEY=...  SEC_UA="app contact:you@example.com"
    python collect.py            # _raw/<provider>/<TICKER>.json 저장 + _raw/meta.json
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = HERE / "_raw"

TICKERS = ["META", "NVDA", "GOOGL", "MSFT", "AMZN", "AAPL", "ORCL", "PLTR", "TSLA", "SPCX", "TSM", "BABA"]
CIKS = {"AAPL": 320193, "AMZN": 1018724, "GOOGL": 1652044, "META": 1326801, "MSFT": 789019,
        "NVDA": 1045810, "ORCL": 1341439, "PLTR": 1321655, "TSLA": 1318605, "SPCX": 1181412}
# TSM·BABA 는 20-F 제출사라 SEC 에 분기 EPS 가 없다. CIK 는 있으나 분기 개념이 없어 제외한다.

WINDOW = ("2026-09-01", "2029-12-31")   # 전망 분기 조회 창


def get(url: str, timeout: int = 40) -> tuple[int, str]:
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=timeout) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")[:400]
    except Exception as e:  # 네트워크 실패도 기록에 남긴다
        return 0, f"{type(e).__name__}: {e}"


UA = os.environ.get("SEC_UA", "stock-report-harness research")


def save(provider: str, ticker: str, payload: dict) -> None:
    d = RAW / provider
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{ticker}.json").write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")


def collect_finnhub(key: str) -> None:
    for t in TICKERS:
        past = get(f"https://finnhub.io/api/v1/stock/earnings?symbol={t}&token={key}")
        time.sleep(0.35)
        fut = get(f"https://finnhub.io/api/v1/calendar/earnings?from={WINDOW[0]}&to={WINDOW[1]}&symbol={t}&token={key}")
        time.sleep(0.35)
        save("finnhub", t, {"past": {"http": past[0], "body": past[1]},
                            "future": {"http": fut[0], "body": fut[1]}})
        print(f"  finnhub {t}: past {past[0]} / future {fut[0]}")


def collect_fmp(key: str) -> None:
    for t in TICKERS:
        r = get(f"https://financialmodelingprep.com/stable/analyst-estimates?symbol={t}&period=quarter&limit=8&apikey={key}")
        time.sleep(0.3)
        save("fmp", t, {"quarter": {"http": r[0], "body": r[1]}})
        print(f"  fmp {t}: {r[0]}")


def collect_sec() -> None:
    for t in TICKERS:
        cik = CIKS.get(t)
        if cik is None:
            save("sec", t, {"note": "20-F 제출사 — SEC XBRL 에 분기 EPS 개념 없음", "http": None})
            print(f"  sec {t}: 분기 개념 없음(20-F)")
            continue
        r = get(f"https://data.sec.gov/api/xbrl/companyconcept/CIK{cik:010d}/us-gaap/EarningsPerShareDiluted.json")
        time.sleep(0.3)
        save("sec", t, {"quarterly_eps": {"http": r[0], "body": r[1][:400] if r[0] != 200 else "(본문 생략 — 크기)"},
                        "has_forecast": False})
        print(f"  sec {t}: {r[0]} (전망 없음)")


def collect_yahoo() -> None:
    try:
        import yfinance as yf
    except ImportError:
        print("  yahoo: yfinance 미설치 — 건너뜀")
        return
    for t in TICKERS:
        rec: dict = {"allowlisted": False,
                     "note": "상류 Yahoo API 가 personal use only — 채택 후보 아님"}
        try:
            tk = yf.Ticker(t)
            est = tk.earnings_estimate
            rec["earnings_estimate"] = json.loads(est.to_json(orient="index")) if est is not None else None
            ed = tk.earnings_dates
            rec["earnings_dates"] = json.loads(ed.reset_index().to_json(orient="records", date_format="iso")) if ed is not None else None
            info = tk.info
            rec["basis"] = {k: info.get(k) for k in ("currency", "financialCurrency", "quoteType", "exchange")}
        except Exception as e:
            rec["error"] = f"{type(e).__name__}: {e}"
        save("yahoo", t, rec)
        print(f"  yahoo {t}: {'ok' if 'error' not in rec else rec['error'][:40]}")


def main() -> None:
    RAW.mkdir(exist_ok=True)
    started = datetime.now(timezone.utc).isoformat()
    fh, fm = os.environ.get("FINNHUB_KEY"), os.environ.get("FMP_API_KEY")
    print(f"조회 시점(UTC): {started}")
    print("finnhub"); collect_finnhub(fh) if fh else print("  FINNHUB_KEY 없음 — 건너뜀")
    print("fmp"); collect_fmp(fm) if fm else print("  FMP_API_KEY 없음 — 건너뜀")
    print("sec"); collect_sec()
    print("yahoo"); collect_yahoo()
    (RAW / "meta.json").write_text(json.dumps({
        "collected_at_utc": started,
        "finished_at_utc": datetime.now(timezone.utc).isoformat(),
        "tickers": TICKERS,
        "forecast_window": WINDOW,
        "excluded": {"api.nasdaq.com": "v1.6 rules.sources denied — 생산 배제이므로 호출하지 않음"},
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print("완료 — _raw/meta.json 에 조회 시점 기록")


if __name__ == "__main__":
    sys.exit(main())
