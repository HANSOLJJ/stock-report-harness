# F6-FX-16: TSM·BABA 의 SEC 택소노미와 개념 이름, 20-F 위치를 확인한다.
# 값 대량 수집이 아니라 경로·가용성 확인이 목적이므로 개념 목록과 최신 소수 관측만 본다.
import io
import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "consensus-source-2026-09-09"))
import fetchlib  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw")
os.makedirs(RAW, exist_ok=True)

# SEC 는 식별 가능한 User-Agent 를 요구한다. 개인 연락처는 넣지 않는다.
SEC_UA = "stock-report-harness F6-FX validation (contact via repository issues)"
H_DATA = {"User-Agent": SEC_UA, "Accept-Encoding": "gzip, deflate", "Host": "data.sec.gov"}
H_WWW = {"User-Agent": SEC_UA, "Accept-Encoding": "gzip, deflate", "Host": "www.sec.gov"}

PAUSE = 0.7  # SEC 요청 한도(10 req/s) 대비 충분히 여유


def save(name, text):
    io.open(os.path.join(RAW, name), "w", encoding="utf-8").write(text)


def resolve_ciks(tickers):
    """SEC 공식 티커-CIK 매핑으로 해석한다. CIK 를 추측하지 않는다."""
    u = "https://www.sec.gov/files/company_tickers.json"
    r = fetchlib.get(u, hdrs=H_WWW, timeout=60)
    out = {"url": u, "status": r["status"], "fetched_at_utc": fetchlib.utcnow()}
    if not r["ok"]:
        out["error"] = r["error"]
        return out
    save("sec-company_tickers.json", r["text"])
    d = json.loads(r["text"])
    want = {t.upper() for t in tickers}
    hits = {}
    for _, row in d.items():
        t = str(row.get("ticker", "")).upper()
        if t in want:
            hits[t] = {"cik": str(row.get("cik_str")).zfill(10),
                       "title": row.get("title")}
    out["resolved"] = hits
    return out


def companyfacts(cik):
    u = "https://data.sec.gov/api/xbrl/companyfacts/CIK%s.json" % cik
    r = fetchlib.get(u, hdrs=H_DATA, timeout=90)
    return u, r


def summarize_facts(text):
    """택소노미별 개념 목록과 단위를 요약한다. 값은 최신 소수만 본다."""
    d = json.loads(text)
    facts = d.get("facts", {})
    summary = {"entityName": d.get("entityName"), "cik": d.get("cik"),
               "taxonomies": {}}
    for tax, concepts in facts.items():
        units_seen = {}
        for cname, cbody in concepts.items():
            for unit in (cbody.get("units") or {}):
                units_seen[unit] = units_seen.get(unit, 0) + 1
        summary["taxonomies"][tax] = {
            "concept_count": len(concepts),
            "units_histogram": units_seen,
            "sample_concepts": sorted(concepts.keys())[:8],
        }
    return summary, facts


REV_KEYS = ["Revenue", "Revenues", "RevenueFromContractsWithCustomers",
            "RevenueFromContractWithCustomerExcludingAssessedTax",
            "RevenueFromSaleOfGoods", "RevenueFromRenderingOfServices"]
NI_KEYS = ["ProfitLoss", "ProfitLossAttributableToOwnersOfParent", "NetIncomeLoss"]
OP_KEYS = ["OperatingIncomeLoss", "ProfitLossFromOperatingActivities",
           "GrossProfit"]


def find_concepts(facts, keys):
    found = []
    for tax, concepts in facts.items():
        for cname in concepts:
            if any(k.lower() == cname.lower() or k.lower() in cname.lower() for k in keys):
                units = list((concepts[cname].get("units") or {}).keys())
                # 최신 연간 관측 1건만 확인한다(대량 수집 아님).
                latest = None
                for u in units:
                    rows = [e for e in concepts[cname]["units"][u]
                            if e.get("start") and e.get("end")]
                    rows.sort(key=lambda e: e["end"])
                    if rows:
                        e = rows[-1]
                        latest = {"unit": u, "start": e.get("start"), "end": e.get("end"),
                                  "val": e.get("val"), "form": e.get("form"),
                                  "fy": e.get("fy"), "fp": e.get("fp")}
                found.append({"taxonomy": tax, "concept": cname,
                              "units": units, "latest_annualish": latest,
                              "label": concepts[cname].get("label")})
    return found


def recent_filings(cik, forms=("20-F", "6-K")):
    u = "https://data.sec.gov/submissions/CIK%s.json" % cik
    r = fetchlib.get(u, hdrs=H_DATA, timeout=60)
    if not r["ok"]:
        return u, r, []
    d = json.loads(r["text"])
    rf = d.get("filings", {}).get("recent", {})
    rows = []
    for i, form in enumerate(rf.get("form", [])):
        if form in forms:
            rows.append({
                "form": form,
                "period_of_report": rf.get("reportDate", [None] * 999)[i],
                "filing_date": rf.get("filingDate", [None] * 999)[i],
                "accession": rf.get("accessionNumber", [None] * 999)[i],
                "primary_doc": rf.get("primaryDocument", [None] * 999)[i],
            })
    rows.sort(key=lambda x: x["filing_date"], reverse=True)
    return u, r, rows


def main():
    targets = ["TSM", "BABA"]
    out = {"task": "F6-FX-16", "generated_at_utc": fetchlib.utcnow(),
           "sec_user_agent": SEC_UA, "companies": {}}

    res = resolve_ciks(targets)
    out["cik_resolution"] = res
    print("CIK 해석:", json.dumps(res.get("resolved", {}), ensure_ascii=False))
    time.sleep(PAUSE)

    for tk, info in (res.get("resolved") or {}).items():
        cik = info["cik"]
        rec = {"ticker": tk, "cik": cik, "sec_title": info["title"]}

        u, r = companyfacts(cik)
        rec["companyfacts_url"] = u
        rec["companyfacts_status"] = r["status"]
        rec["companyfacts_fetched_at_utc"] = fetchlib.utcnow()
        if r["ok"]:
            save("sec-%s-companyfacts.json" % tk, r["text"])
            summ, facts = summarize_facts(r["text"])
            rec["facts_summary"] = summ
            rec["revenue_concepts"] = find_concepts(facts, REV_KEYS)
            rec["netincome_concepts"] = find_concepts(facts, NI_KEYS)
            rec["operating_concepts"] = find_concepts(facts, OP_KEYS)
            print("\n== %s (%s) %s" % (tk, cik, summ.get("entityName")))
            for tax, meta in summ["taxonomies"].items():
                print("   택소노미 %-12s 개념 %4d  단위 %s" % (
                    tax, meta["concept_count"], meta["units_histogram"]))
        else:
            rec["companyfacts_error"] = r["error"]
            print("%s companyfacts 실패: %s" % (tk, r["error"]))
        time.sleep(PAUSE)

        u2, r2, rows = recent_filings(cik)
        rec["submissions_url"] = u2
        rec["submissions_status"] = r2["status"]
        if r2["ok"]:
            save("sec-%s-submissions.json" % tk, r2["text"])
        rec["recent_20f_6k"] = rows[:8]
        f20 = [x for x in rows if x["form"] == "20-F"]
        rec["latest_20f"] = f20[0] if f20 else None
        if f20:
            a = f20[0]["accession"].replace("-", "")
            rec["latest_20f_url"] = (
                "https://www.sec.gov/Archives/edgar/data/%d/%s/%s"
                % (int(cik), a, f20[0]["primary_doc"]))
            rec["latest_20f_index"] = (
                "https://www.sec.gov/Archives/edgar/data/%d/%s/"
                % (int(cik), a))
            print("   최신 20-F: %s (기간 %s) -> %s" % (
                f20[0]["filing_date"], f20[0]["period_of_report"], rec["latest_20f_url"]))
        time.sleep(PAUSE)

        out["companies"][tk] = rec

    io.open(os.path.join(HERE, "sec-fx-16.json"), "w", encoding="utf-8").write(
        json.dumps(out, ensure_ascii=False, indent=1))
    print("\nsaved sec-fx-16.json")


if __name__ == "__main__":
    main()
