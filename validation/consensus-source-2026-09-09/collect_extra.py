# 미발표 분기 경계 확인용 Nasdaq /eps 와 독립 3사 교차검증용 TradingView 스캐너를 수집한다.
import io
import json
import os
import time

import fetchlib

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw")

TARGETS = [
    ("meta", "META", "NASDAQ"), ("nvidia", "NVDA", "NASDAQ"),
    ("alphabet", "GOOGL", "NASDAQ"), ("microsoft", "MSFT", "NASDAQ"),
    ("amazon", "AMZN", "NASDAQ"), ("apple", "AAPL", "NASDAQ"),
    ("oracle", "ORCL", "NYSE"), ("palantir", "PLTR", "NASDAQ"),
    ("tesla", "TSLA", "NASDAQ"), ("spacex-xai", "SPCX", "NASDAQ"),
]

TV_FIELDS = ("earnings_per_share_forecast_fq,earnings_per_share_forecast_next_fq,"
             "earnings_per_share_fq,earnings_per_share_forecast_next_fy,"
             "earnings_release_next_date,earnings_release_date,currency,fiscal_period_end_fq")

out = {"generated_at_utc": fetchlib.utcnow(), "companies": {}}
for cid, tk, exch in TARGETS:
    rec = {"ticker": tk}

    u = "https://api.nasdaq.com/api/quote/%s/eps" % tk
    r = fetchlib.get(u, referer="https://www.nasdaq.com/market-activity/stocks/%s/earnings" % tk.lower())
    rec["nasdaq_eps"] = {"url": u, "status": r["status"], "fetched_at_utc": fetchlib.utcnow()}
    if r["ok"]:
        io.open(os.path.join(RAW, "nasdaq-%s-eps.json" % cid), "w", encoding="utf-8").write(r["text"])
        try:
            rec["nasdaq_eps"]["data"] = json.loads(r["text"]).get("data")
        except Exception as e:
            rec["nasdaq_eps"]["parse_error"] = str(e)
    else:
        rec["nasdaq_eps"]["error"] = r["error"]
    time.sleep(0.7)

    for ex in ([exch] if exch != "NYSE" else ["NYSE", "NASDAQ"]):
        u2 = "https://scanner.tradingview.com/symbol?symbol=%s%%3A%s&fields=%s&no_404=true" % (ex, tk, TV_FIELDS)
        r2 = fetchlib.get(u2, referer="https://www.tradingview.com/symbols/%s-%s/forecast/" % (ex, tk))
        if r2["ok"] and r2["bytes"] > 5:
            rec["tradingview"] = {"url": u2, "status": r2["status"],
                                  "fetched_at_utc": fetchlib.utcnow()}
            try:
                rec["tradingview"]["data"] = json.loads(r2["text"])
            except Exception as e:
                rec["tradingview"]["parse_error"] = str(e)
            io.open(os.path.join(RAW, "tv-%s.json" % cid), "w", encoding="utf-8").write(r2["text"])
            break
        rec["tradingview"] = {"url": u2, "status": r2["status"], "error": r2.get("error")}
        time.sleep(0.5)
    time.sleep(0.7)

    out["companies"][cid] = rec
    ne = (rec.get("nasdaq_eps", {}).get("data") or {}).get("earningsPerShare") or []
    up = [x for x in ne if x.get("type") == "UpcomingQuarter"]
    tv = (rec.get("tradingview", {}) or {}).get("data") or {}
    print("%-12s upcoming=%d  tv_next_fq=%s" % (
        cid, len(up), tv.get("earnings_per_share_forecast_next_fq")))

io.open(os.path.join(HERE, "collect-extra.json"), "w", encoding="utf-8").write(
    json.dumps(out, ensure_ascii=False, indent=1))
print("saved collect-extra.json")
