# NTM-SOURCE-05: 공급사 공식 정의(EPS* 별표, 데이터 제공사 표기, 추정 갱신시각) 근거를 탐색한다.
import io
import os
import re
import time

import fetchlib

HERE = os.path.dirname(os.path.abspath(__file__))
RAW2 = os.path.join(HERE, "raw-05")
os.makedirs(RAW2, exist_ok=True)

CAND = [
    ("nasdaq_glossary_eps", "https://www.nasdaq.com/glossary/e/earnings-per-share"),
    ("nasdaq_earnings_page", "https://www.nasdaq.com/market-activity/stocks/nvda/earnings"),
    ("nasdaq_eps_forecast_help", "https://www.nasdaq.com/market-activity/quotes/earnings-forecast"),
    ("nasdaq_data_disclaimers", "https://www.nasdaq.com/data-disclaimers"),
    ("nasdaq_terms", "https://www.nasdaq.com/terms-and-conditions"),
    ("nasdaq_api_earnings_hdr", "https://api.nasdaq.com/api/analyst/NVDA/earnings-forecast"),
    ("nasdaq_api_quote_summary", "https://api.nasdaq.com/api/quote/NVDA/summary?assetclass=stocks"),
    ("nasdaq_api_earnings_date", "https://api.nasdaq.com/api/company/NVDA/earnings-date"),
    ("nasdaq_api_financial", "https://api.nasdaq.com/api/company/NVDA/financials?frequency=2"),
    ("nasdaq_api_dividends", "https://api.nasdaq.com/api/quote/NVDA/dividends?assetclass=stocks"),
    ("zacks_disclaimer", "https://www.zacks.com/stock/quote/NVDA/detailed-estimates"),
    ("stockanalysis_forecast_page", "https://stockanalysis.com/stocks/nvda/forecast/"),
]

PAT = [
    r"EPS\*", r"\*\s*EPS", r"excludes?[^<.]{0,80}", r"non-?GAAP", r"[Aa]djusted",
    r"[Dd]iluted", r"[Bb]asic", r"Zacks", r"[Dd]ata provided by[^<]{0,60}",
    r"[Ss]ource:[^<]{0,60}", r"[Ll]ast [Uu]pdated[^<]{0,40}", r"as of[^<]{0,40}",
    r"[Ss]plit[- ]adjusted", r"currency", r"USD",
]

for name, url in CAND:
    r = fetchlib.get(url, referer="https://www.nasdaq.com/market-activity/stocks/nvda/earnings")
    print("== %-28s status=%s bytes=%s" % (name, r["status"], r["bytes"]))
    if not r["ok"] or not r["text"]:
        print("   error:", r.get("error"))
        time.sleep(0.8)
        continue
    io.open(os.path.join(RAW2, "def-%s.txt" % name), "w", encoding="utf-8").write(r["text"])
    t = r["text"]
    seen = set()
    for p in PAT:
        for m in list(re.finditer(p, t))[:3]:
            seg = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", t[max(0, m.start() - 180):m.start() + 220]))
            key = seg[:90]
            if key in seen:
                continue
            seen.add(key)
            print("   [%s] ...%s..." % (p[:18], seg))
    time.sleep(0.8)
