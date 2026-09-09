# NTM-SOURCE-04 원천 탐색: 분기별 EPS 컨센서스(평균/최소/최대/전망치 수)를 노출하는 공개 경로를 후보별로 시험한다.
import io, json, os, re, sys, time, gzip, zlib
import urllib.request, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")


def get(url, timeout=30, hdrs=None, referer=None):
    h = {"User-Agent": UA,
         "Accept": "text/html,application/xhtml+xml,application/json;q=0.9,*/*;q=0.8",
         "Accept-Language": "en-US,en;q=0.9",
         "Accept-Encoding": "gzip, deflate"}
    if referer:
        h["Referer"] = referer
    if hdrs:
        h.update(hdrs)
    req = urllib.request.Request(url, headers=h)
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read()
            enc = (r.headers.get("Content-Encoding") or "").lower()
            if enc == "gzip":
                raw = gzip.decompress(raw)
            elif enc == "deflate":
                raw = zlib.decompress(raw, -zlib.MAX_WBITS)
            return dict(ok=True, status=r.status, final_url=r.geturl(),
                        ctype=r.headers.get("Content-Type"), bytes=len(raw),
                        elapsed=round(time.time() - t0, 2),
                        text=raw.decode("utf-8", "replace"))
    except urllib.error.HTTPError as e:
        body = b""
        try:
            body = e.read()
        except Exception:
            pass
        return dict(ok=False, status=e.code, final_url=url, ctype=None,
                    bytes=len(body), elapsed=round(time.time() - t0, 2),
                    text=body.decode("utf-8", "replace"), error="HTTPError %s" % e.code)
    except Exception as e:
        return dict(ok=False, status=None, final_url=url, ctype=None, bytes=0,
                    elapsed=round(time.time() - t0, 2), text="",
                    error="%s: %s" % (type(e).__name__, e))


SYM = "NVDA"
CANDIDATES = [
    ("stockanalysis_forecast_data", "https://stockanalysis.com/stocks/nvda/forecast/__data.json"),
    ("stockanalysis_api_forecast", "https://stockanalysis.com/api/symbol/s/nvda/forecast"),
    ("stockanalysis_api_overview", "https://stockanalysis.com/api/symbol/s/nvda/overview"),
    ("yahoo_quotesummary_earningstrend",
     "https://query2.finance.yahoo.com/v10/finance/quoteSummary/NVDA?modules=earningsTrend"),
    ("yahoo_v6_quotesummary",
     "https://query1.finance.yahoo.com/v6/finance/quoteSummary/NVDA?modules=earningsTrend"),
    ("nasdaq_earnings_forecast", "https://api.nasdaq.com/api/analyst/NVDA/earnings-forecast"),
    ("nasdaq_eps_forecast", "https://api.nasdaq.com/api/company/NVDA/earnings-forecast"),
    ("seekingalpha_estimates",
     "https://seekingalpha.com/api/v3/symbols/nvda/estimates?filter[estimates_data_items]=eps_normalized_actual,eps_normalized_consensus_mean,eps_normalized_consensus_low,eps_normalized_consensus_high,eps_normalized_num_of_estimates&filter[period_type]=quarterly&period_type=quarterly"),
    ("tipranks_forecast", "https://www.tipranks.com/api/stocks/getForecast/?tickers=NVDA"),
    ("marketbeat_forecast", "https://www.marketbeat.com/stocks/NASDAQ/NVDA/forecast/"),
    ("zacks_detailed_estimates", "https://www.zacks.com/stock/quote/NVDA/detailed-estimates"),
    ("wsj_research_ratings", "https://www.wsj.com/market-data/quotes/NVDA/research-ratings"),
    ("barchart_analyst_estimates", "https://www.barchart.com/stocks/quotes/NVDA/analyst-estimates"),
    ("investing_earnings", "https://www.investing.com/equities/nvidia-corp-earnings"),
    ("finviz_quote", "https://finviz.com/quote.ashx?t=NVDA"),
    ("alphavantage_earnings_estimates",
     "https://www.alphavantage.co/query?function=EARNINGS_ESTIMATES&symbol=NVDA&apikey=demo"),
    ("stocktwits_estimates", "https://api.stocktwits.com/api/2/streams/symbol/NVDA.json"),
    ("valley_public", "https://www.valley.town/financials/quote/NVDA:US/expert-forecast/total?period=Interim"),
]

KEYWORDS = ["consensus", "estimate", "Estimate", "numberOfAnalysts", "numOfEstimates",
            "low", "high", "median", "quarter", "Quarter", "FY2027", "FY2028",
            "2.47", "2.74", "2.75", "3.20", "3.67"]

out = []
for name, url in CANDIDATES:
    r = get(url)
    hit = [k for k in KEYWORDS if k in r["text"]] if r["text"] else []
    rec = dict(name=name, url=url, ok=r["ok"], status=r["status"], ctype=r["ctype"],
               bytes=r["bytes"], elapsed=r["elapsed"], error=r.get("error"),
               keyword_hits=hit, head=r["text"][:400])
    out.append(rec)
    print("%-34s status=%-5s bytes=%-9s hits=%s %s" % (
        name, r["status"], r["bytes"], ",".join(hit[:8]), r.get("error") or ""))
    if r["ok"] and r["bytes"] > 0:
        fn = os.path.join(HERE, "raw", "probe-%s.txt" % name)
        io.open(fn, "w", encoding="utf-8").write(r["text"])
    time.sleep(1.0)

io.open(os.path.join(HERE, "raw", "probe-summary.json"), "w", encoding="utf-8").write(
    json.dumps(out, ensure_ascii=False, indent=1))
