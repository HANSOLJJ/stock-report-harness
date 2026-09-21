# OFFB-24B: SPCX·BABA·AMZN 의 최신 정기보고서를 찾아 미개시 B종 약정 주석을 조사한다.
# 원천은 data.sec.gov 와 www.sec.gov 뿐이다.
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

UA = "stock-report-harness OFFB-24B validation (contact via repository issues)"
H_DATA = {"User-Agent": UA, "Accept-Encoding": "gzip, deflate", "Host": "data.sec.gov"}
H_WWW = {"User-Agent": UA, "Accept-Encoding": "gzip, deflate", "Host": "www.sec.gov"}

TARGETS = {
    "SPCX": {"cik": "0001181412", "forms": ("10-K", "10-Q", "S-1", "424B4", "8-K")},
    "BABA": {"cik": "0001577552", "forms": ("20-F", "6-K")},
    "AMZN": {"cik": "0001018724", "forms": ("10-K", "10-Q")},
}

out = {"generated_at_utc": fetchlib.utcnow(), "targets": {}}
for tk, meta in TARGETS.items():
    cik = meta["cik"]
    u = "https://data.sec.gov/submissions/CIK%s.json" % cik
    r = fetchlib.get(u, hdrs=H_DATA, timeout=60)
    rec = {"cik": cik, "submissions_url": u, "status": r["status"],
           "fetched_at_utc": fetchlib.utcnow()}
    print("== %s CIK %s  status=%s" % (tk, cik, r["status"]))
    if r["ok"]:
        io.open(os.path.join(RAW, "sec-%s-submissions.json" % tk), "w",
                encoding="utf-8").write(r["text"])
        d = json.loads(r["text"])
        rec["entity_name"] = d.get("name")
        rec["fiscal_year_end"] = d.get("fiscalYearEnd")
        rf = d.get("filings", {}).get("recent", {})
        rows = []
        for i, form in enumerate(rf.get("form", [])):
            if form in meta["forms"]:
                rows.append({
                    "form": form,
                    "period": rf.get("reportDate", [None] * 9999)[i],
                    "filed": rf.get("filingDate", [None] * 9999)[i],
                    "accession": rf.get("accessionNumber", [None] * 9999)[i],
                    "primary_doc": rf.get("primaryDocument", [None] * 9999)[i],
                })
        rows.sort(key=lambda x: x["filed"], reverse=True)
        rec["filings"] = rows[:14]
        print("   %s  FYend=%s  총 %d건" % (rec["entity_name"], rec["fiscal_year_end"], len(rows)))
        for x in rows[:8]:
            url = ("https://www.sec.gov/Archives/edgar/data/%d/%s/%s"
                   % (int(cik), x["accession"].replace("-", ""), x["primary_doc"]))
            x["url"] = url
            print("     %-7s period=%-11s filed=%s  %s" % (x["form"], x["period"], x["filed"], x["primary_doc"]))
    else:
        rec["error"] = r["error"]
    out["targets"][tk] = rec
    time.sleep(0.8)

io.open(os.path.join(HERE, "filings-index.json"), "w", encoding="utf-8").write(
    json.dumps(out, ensure_ascii=False, indent=1))
print("\nsaved filings-index.json")
