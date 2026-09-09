# TSM 및 BABA에 대한 Nasdaq 공개 API 분기 EPS 전망치 수집 및 검증 스크립트
from __future__ import annotations

import gzip
import io
import json
import os
import time
import urllib.error
import urllib.request
import zlib
from typing import Any

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
)

HERE = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(HERE, "raw")
SNAPSHOTS_DIR = os.path.join(HERE, "snapshots")


def http_get(url: str, referer: str | None = None, timeout: int = 30) -> dict[str, Any]:
    headers = {
        "User-Agent": UA,
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate",
    }
    if referer:
        headers["Referer"] = referer

    req = urllib.request.Request(url, headers=headers)
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
            enc = (resp.headers.get("Content-Encoding") or "").lower()
            if enc == "gzip":
                raw = gzip.decompress(raw)
            elif enc == "deflate":
                raw = zlib.decompress(raw, -zlib.MAX_WBITS)
            return {
                "ok": True,
                "status": resp.status,
                "url": resp.geturl(),
                "elapsed": round(time.time() - t0, 2),
                "text": raw.decode("utf-8", "replace"),
                "error": None,
            }
    except urllib.error.HTTPError as e:
        body = b""
        try:
            body = e.read()
        except Exception:
            pass
        return {
            "ok": False,
            "status": e.code,
            "url": url,
            "elapsed": round(time.time() - t0, 2),
            "text": body.decode("utf-8", "replace"),
            "error": f"HTTPError {e.code}",
        }
    except Exception as e:
        return {
            "ok": False,
            "status": None,
            "url": url,
            "elapsed": round(time.time() - t0, 2),
            "text": "",
            "error": f"{type(e).__name__}: {e}",
        }


def collect_nasdaq_ticker(ticker: str) -> dict[str, Any]:
    print(f"[{ticker}] Collecting Nasdaq API...")
    os.makedirs(RAW_DIR, exist_ok=True)
    os.makedirs(SNAPSHOTS_DIR, exist_ok=True)

    endpoints = {
        "earnings_forecast": f"https://api.nasdaq.com/api/analyst/{ticker}/earnings-forecast",
        "info": f"https://api.nasdaq.com/api/quote/{ticker}/info?assetclass=stocks",
        "summary": f"https://api.nasdaq.com/api/quote/{ticker}/summary?assetclass=stocks",
    }

    out: dict[str, Any] = {
        "ticker": ticker,
        "collected_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "endpoints": {},
    }

    for name, url in endpoints.items():
        ref = f"https://www.nasdaq.com/market-activity/stocks/{ticker.lower()}/earnings"
        res = http_get(url, referer=ref)
        raw_path = os.path.join(RAW_DIR, f"nasdaq-{ticker.lower()}-{name}.json")
        with open(raw_path, "w", encoding="utf-8") as f:
            f.write(res["text"])

        parsed_data = None
        if res["ok"] and res["text"]:
            try:
                parsed_json = json.loads(res["text"])
                parsed_data = parsed_json.get("data")
            except Exception as e:
                print(f"  Parse error for {name}: {e}")

        out["endpoints"][name] = {
            "url": url,
            "status": res["status"],
            "ok": res["ok"],
            "raw_file": raw_path,
            "data": parsed_data,
        }
        time.sleep(0.5)

    return out


def main():
    print("=== TSM / BABA Nasdaq 공개 API 수집 시작 ===")
    tsm_res = collect_nasdaq_ticker("TSM")
    baba_res = collect_nasdaq_ticker("BABA")

    output_path = os.path.join(HERE, "nasdaq_raw_collected.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({"tsm": tsm_res, "baba": baba_res}, f, ensure_ascii=False, indent=2)

    print(f"수집 완료. 결과 저장: {output_path}")

    # 요약 출력
    for t_name, t_data in [("TSM", tsm_res), ("BABA", baba_res)]:
        ef = t_data["endpoints"]["earnings_forecast"].get("data")
        print(f"\n--- [{t_name}] Earnings Forecast Data ---")
        if not ef:
            print("No earnings forecast data found!")
            continue
        qf = ef.get("quarterlyForecast")
        if qf:
            rows = qf.get("rows") or []
            print(f"Quarterly Forecast Rows Count: {len(rows)}")
            for r in rows:
                print("  Row:", r)
        else:
            print("No quarterlyForecast section in data.")

        yearly = ef.get("yearlyForecast")
        if yearly:
            y_rows = yearly.get("rows") or []
            print(f"Yearly Forecast Rows Count: {len(y_rows)}")
            for y in y_rows:
                print("  Yearly Row:", y)


if __name__ == "__main__":
    main()
