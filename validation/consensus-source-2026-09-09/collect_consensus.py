# NTM-SOURCE-04 수집기: 담당 10개사의 다음 4개 미발표 회계분기 EPS 컨센서스를 원천별로 수집한다.
# 원천을 섞어 하나의 NTM 을 만들지 않고, 원천별 묶음을 그대로 보존한다.
import io
import json
import os
import time

import fetchlib
import devalue

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw")

# company_id -> (Nasdaq/거래 티커, StockAnalysis 슬러그)
TARGETS = [
    ("meta", "META", "meta"),
    ("nvidia", "NVDA", "nvda"),
    ("alphabet", "GOOGL", "googl"),
    ("microsoft", "MSFT", "msft"),
    ("amazon", "AMZN", "amzn"),
    ("apple", "AAPL", "aapl"),
    ("oracle", "ORCL", "orcl"),
    ("palantir", "PLTR", "pltr"),
    ("tesla", "TSLA", "tsla"),
    ("spacex-xai", "SPCX", "spcx"),
]

NASDAQ_FORECAST = "https://api.nasdaq.com/api/analyst/%s/earnings-forecast"
NASDAQ_INFO = "https://api.nasdaq.com/api/quote/%s/info?assetclass=stocks"
NASDAQ_SUMMARY = "https://api.nasdaq.com/api/quote/%s/summary?assetclass=stocks"
SA_FORECAST_DATA = "https://stockanalysis.com/stocks/%s/forecast/__data.json"
SA_FORECAST_PAGE = "https://stockanalysis.com/stocks/%s/forecast/"


def save_raw(name, text):
    io.open(os.path.join(RAW, name), "w", encoding="utf-8").write(text)


def collect_nasdaq(cid, ticker):
    """Nasdaq 공개 API. 분기별 평균/최대/최소/전망치 수를 4분기 이상 제공한다."""
    out = {"source": "nasdaq_api", "urls": {}, "fetched_at_utc": {}, "http_status": {}}
    for key, tmpl in (("earnings_forecast", NASDAQ_FORECAST),
                      ("info", NASDAQ_INFO),
                      ("summary", NASDAQ_SUMMARY)):
        url = tmpl % ticker
        r = fetchlib.get(url, referer="https://www.nasdaq.com/market-activity/stocks/%s/earnings" % ticker.lower())
        out["urls"][key] = url
        out["fetched_at_utc"][key] = fetchlib.utcnow()
        out["http_status"][key] = r["status"]
        if r["ok"]:
            save_raw("nasdaq-%s-%s.json" % (cid, key), r["text"])
            try:
                out[key] = json.loads(r["text"]).get("data")
            except Exception as e:
                out[key] = None
                out.setdefault("parse_errors", {})[key] = str(e)
        else:
            out[key] = None
            out.setdefault("fetch_errors", {})[key] = r["error"]
        time.sleep(0.8)
    return out


def collect_stockanalysis(cid, slug):
    """StockAnalysis SvelteKit __data.json. 회계분기 종료일과 마지막 발표 분기 인덱스를 제공한다."""
    out = {"source": "stockanalysis_data_json", "urls": {}, "fetched_at_utc": {}, "http_status": {}}
    url = SA_FORECAST_DATA % slug
    r = fetchlib.get(url, referer=SA_FORECAST_PAGE % slug)
    out["urls"]["forecast_data"] = url
    out["page_url"] = SA_FORECAST_PAGE % slug
    out["fetched_at_utc"]["forecast_data"] = fetchlib.utcnow()
    out["http_status"]["forecast_data"] = r["status"]
    if not r["ok"]:
        out["fetch_error"] = r["error"]
        return out
    save_raw("sa-%s-forecast-data.json" % cid, r["text"])
    try:
        doc = json.loads(r["text"])
    except Exception as e:
        out["parse_error"] = str(e)
        return out
    # estimates 노드를 찾는다 (노드 인덱스는 라우트에 따라 달라질 수 있다).
    hydrated = None
    for i in range(len(doc.get("nodes", []))):
        try:
            d = devalue.node_data(r["text"], i)
        except Exception:
            continue
        if isinstance(d, dict) and "estimates" in d:
            hydrated = d
            out["node_index"] = i
            break
    if hydrated is None:
        out["parse_error"] = "estimates 노드를 찾지 못함"
        return out
    est = hydrated.get("estimates") or {}
    tbl = (est.get("table") or {}).get("quarterly") or {}
    out["quarterly"] = {k: tbl.get(k) for k in
                        ("dates", "fiscalYear", "fiscalQuarter", "eps", "adjustedEps",
                         "analysts", "revenue", "lastDate", "peForward")}
    out["annual"] = {k: ((est.get("table") or {}).get("annual") or {}).get(k) for k in
                     ("dates", "fiscalYear", "eps", "adjustedEps", "analysts", "lastDate")}
    out["estimates_source_label"] = est.get("estimatesSource") or hydrated.get("estimatesSource")
    out["meta_label"] = hydrated.get("meta")
    return out


def main():
    os.makedirs(RAW, exist_ok=True)
    result = {
        "task": "NTM-SOURCE-04",
        "generated_at_utc": fetchlib.utcnow(),
        "method_doc": "설계진행/validation/consensus-research-method.md",
        "note": "원천별 수집 결과를 그대로 보존한다. 원천 혼합·소급 적용 금지.",
        "companies": [],
    }
    for cid, ticker, slug in TARGETS:
        print("collecting %s (%s / %s)" % (cid, ticker, slug))
        rec = {"company_id": cid, "ticker": ticker, "stockanalysis_slug": slug}
        rec["nasdaq"] = collect_nasdaq(cid, ticker)
        rec["stockanalysis"] = collect_stockanalysis(cid, slug)
        q = ((rec["nasdaq"].get("earnings_forecast") or {}).get("quarterlyForecast") or {}).get("rows")
        saq = (rec["stockanalysis"].get("quarterly") or {}).get("dates")
        print("   nasdaq quarterly rows=%s  sa dates=%s" % (
            len(q) if q else 0, len(saq) if saq else 0))
        result["companies"].append(rec)
        time.sleep(1.0)
    io.open(os.path.join(HERE, "collect-raw.json"), "w", encoding="utf-8").write(
        json.dumps(result, ensure_ascii=False, indent=1))
    print("saved collect-raw.json")


if __name__ == "__main__":
    main()
