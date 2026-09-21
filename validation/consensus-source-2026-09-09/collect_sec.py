# NTM-SOURCE-05: SEC EDGAR 공시로 공식 회계분기 종료일·발표 시점·GAAP 기본/희석 EPS·주식수·통화를 확인한다.
# 공급사 값을 이 원문과 대조하되, 수치 근접만으로 기준을 확정하지 않는다.
import io
import json
import os
import time

import fetchlib

HERE = os.path.dirname(os.path.abspath(__file__))
RAW2 = os.path.join(HERE, "raw-05")
os.makedirs(RAW2, exist_ok=True)

# StockAnalysis 스냅샷이 선언한 CIK 를 사용한다(vendor-meta-05.json).
CIK = {
    "meta": "0001326801", "nvidia": "0001045810", "alphabet": "0001652044",
    "microsoft": "0000789019", "amazon": "0001018724", "apple": "0000320193",
    "oracle": "0001341439", "palantir": "0001321655", "tesla": "0001318605",
    "spacex-xai": "0001181412",
}

# SEC 는 식별 가능한 User-Agent 를 요구한다. 개인 연락처는 넣지 않는다.
SEC_HDRS = {
    "User-Agent": "stock-report-harness NTM validation (contact via repository issues)",
    "Accept-Encoding": "gzip, deflate",
    "Host": "data.sec.gov",
}

CONCEPTS = ["EarningsPerShareDiluted", "EarningsPerShareBasic"]


def norm(cik):
    return "CIK" + cik.zfill(10) if not cik.startswith("CIK") else cik


def main():
    out = {"generated_at_utc": fetchlib.utcnow(), "companies": {}}
    for cid, cik in CIK.items():
        rec = {"cik": cik, "urls": {}, "fetched_at_utc": {}, "http_status": {}}

        u = "https://data.sec.gov/submissions/%s.json" % norm(cik)
        r = fetchlib.get(u, hdrs=SEC_HDRS)
        rec["urls"]["submissions"] = u
        rec["fetched_at_utc"]["submissions"] = fetchlib.utcnow()
        rec["http_status"]["submissions"] = r["status"]
        if r["ok"]:
            io.open(os.path.join(RAW2, "sec-%s-submissions.json" % cid), "w",
                    encoding="utf-8").write(r["text"])
            try:
                d = json.loads(r["text"])
                rec["entity_name"] = d.get("name")
                rec["tickers"] = d.get("tickers")
                rec["exchanges"] = d.get("exchanges")
                rec["fiscal_year_end_mmdd"] = d.get("fiscalYearEnd")
                rec["sic_description"] = d.get("sicDescription")
                rf = d.get("filings", {}).get("recent", {})
                rows = []
                for i, form in enumerate(rf.get("form", [])):
                    if form in ("10-Q", "10-K", "8-K"):
                        rows.append({
                            "form": form,
                            "period_of_report": rf.get("reportDate", [None] * 99)[i],
                            "filing_date": rf.get("filingDate", [None] * 99)[i],
                            "accession": rf.get("accessionNumber", [None] * 99)[i],
                            "primary_doc": rf.get("primaryDocument", [None] * 99)[i],
                        })
                    if len(rows) >= 25:
                        break
                rec["recent_filings"] = rows
            except Exception as e:
                rec["parse_error_submissions"] = str(e)
        else:
            rec["fetch_error_submissions"] = r["error"]
        time.sleep(0.35)

        for concept in CONCEPTS:
            u2 = ("https://data.sec.gov/api/xbrl/companyconcept/%s/us-gaap/%s.json"
                  % (norm(cik), concept))
            r2 = fetchlib.get(u2, hdrs=SEC_HDRS)
            rec["urls"][concept] = u2
            rec["fetched_at_utc"][concept] = fetchlib.utcnow()
            rec["http_status"][concept] = r2["status"]
            if not r2["ok"]:
                rec.setdefault("fetch_errors", {})[concept] = r2["error"]
                time.sleep(0.35)
                continue
            io.open(os.path.join(RAW2, "sec-%s-%s.json" % (cid, concept)), "w",
                    encoding="utf-8").write(r2["text"])
            try:
                d2 = json.loads(r2["text"])
                units = d2.get("units", {})
                unit_key = next(iter(units), None)
                rec.setdefault("xbrl_units", {})[concept] = list(units.keys())
                # 분기(약 3개월) 관측만 추린다.
                qs = []
                for e in units.get(unit_key, []):
                    st, en = e.get("start"), e.get("end")
                    if not st or not en:
                        continue
                    import datetime as dt
                    days = (dt.date.fromisoformat(en) - dt.date.fromisoformat(st)).days
                    if 80 <= days <= 100:
                        qs.append({"start": st, "end": en, "val": e.get("val"),
                                   "fy": e.get("fy"), "fp": e.get("fp"),
                                   "form": e.get("form"), "filed": e.get("filed"),
                                   "frame": e.get("frame")})
                qs.sort(key=lambda x: (x["end"], x["filed"]))
                rec.setdefault("quarterly", {})[concept] = qs[-8:]
            except Exception as e:
                rec.setdefault("parse_errors", {})[concept] = str(e)
            time.sleep(0.35)

        out["companies"][cid] = rec
        q = (rec.get("quarterly") or {}).get("EarningsPerShareDiluted") or []
        print("%-11s %-42s FYend=%s  10-Q/K=%d  dilQ=%d  last=%s" % (
            cid, (rec.get("entity_name") or "?")[:42], rec.get("fiscal_year_end_mmdd"),
            len(rec.get("recent_filings") or []), len(q),
            (q[-1]["end"] + " " + str(q[-1]["val"])) if q else "-"))

    io.open(os.path.join(HERE, "sec-05.json"), "w", encoding="utf-8").write(
        json.dumps(out, ensure_ascii=False, indent=1))
    print("saved sec-05.json")


if __name__ == "__main__":
    main()
