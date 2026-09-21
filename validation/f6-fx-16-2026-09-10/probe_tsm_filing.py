# F6-FX-16 후속: TSM 2026-04-16 제출분(0001628280-26-025362)의 실제 문서 구성과
# XBRL 재무제표 산출물 존재 여부를 EDGAR 에서 확인한다. 값은 수집하지 않는다.
import io
import json
import os
import re
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "consensus-source-2026-09-09"))
import fetchlib  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw")

SEC_UA = "stock-report-harness F6-FX validation (contact via repository issues)"
H_WWW = {"User-Agent": SEC_UA, "Accept-Encoding": "gzip, deflate", "Host": "www.sec.gov"}
H_DATA = {"User-Agent": SEC_UA, "Accept-Encoding": "gzip, deflate", "Host": "data.sec.gov"}

CIK = "1046179"
ACCNS = [
    ("FY2025", "0001628280-26-025362"),   # 2026-04-16 제출, 문제의 건
    ("FY2024", "0001193125-25-083423"),   # 2025-04-17 제출, 정상 반영된 건 (대조군)
]

out = {"generated_at_utc": fetchlib.utcnow(), "filings": {}}

for label, accn in ACCNS:
    a = accn.replace("-", "")
    base = "https://www.sec.gov/Archives/edgar/data/%s/%s/" % (CIK, a)
    rec = {"accession": accn, "index_url": base + "index.json"}
    print("=" * 78)
    print("%s  %s" % (label, accn))

    r = fetchlib.get(base + "index.json", hdrs=H_WWW, timeout=60)
    rec["index_status"] = r["status"]
    if r["ok"]:
        io.open(os.path.join(RAW, "edgar-index-%s.json" % label), "w",
                encoding="utf-8").write(r["text"])
        d = json.loads(r["text"])
        items = d.get("directory", {}).get("item", [])
        rec["file_count"] = len(items)
        names = [it.get("name", "") for it in items]
        rec["files_sample"] = sorted(names)[:40]

        # XBRL 재무제표 산출물의 존재 신호
        signals = {
            "FilingSummary.xml": any(n == "FilingSummary.xml" for n in names),
            "Financial_Report.xlsx": any(n == "Financial_Report.xlsx" for n in names),
            "R_htm_render_files": sum(1 for n in names if re.match(r"^R\d+\.htm$", n)),
            "xml_instance": [n for n in names if n.endswith("_htm.xml") or
                             (n.endswith(".xml") and not n.startswith("R") and
                              n not in ("FilingSummary.xml",))][:12],
            "xsd_schema": [n for n in names if n.endswith(".xsd")][:5],
            "cal_def_lab_pre": [n for n in names
                                if re.search(r"_(cal|def|lab|pre)\.xml$", n)][:8],
        }
        rec["xbrl_signals"] = signals
        print("  파일 %d개" % len(items))
        for k, v in signals.items():
            print("    %-22s %s" % (k, v))
    else:
        rec["index_error"] = r["error"]
        print("  index 조회 실패:", r["error"])
    time.sleep(0.8)
    out["filings"][label] = rec

# 라이브 API 로 재확인 (스냅샷이 아니라 현재 상태)
print("\n" + "=" * 78)
print("라이브 companyconcept 재확인 — ifrs-full:Revenue")
u = "https://data.sec.gov/api/xbrl/companyconcept/CIK0001046179/ifrs-full/Revenue.json"
r = fetchlib.get(u, hdrs=H_DATA, timeout=60)
print("  status", r["status"])
if r["ok"]:
    io.open(os.path.join(RAW, "sec-TSM-concept-Revenue-live.json"), "w",
            encoding="utf-8").write(r["text"])
    d = json.loads(r["text"])
    ends = set()
    accs = set()
    for unit, entries in d.get("units", {}).items():
        for e in entries:
            if e.get("end"):
                ends.add(e["end"][:4])
            if e.get("accn"):
                accs.add((e["accn"], e.get("filed")))
    out["live_revenue_end_years"] = sorted(ends)
    out["live_revenue_latest_accn"] = sorted(accs, key=lambda x: x[1], reverse=True)[:4]
    print("  end 연도:", sorted(ends))
    print("  최근 accession:", sorted(accs, key=lambda x: x[1], reverse=True)[:4])

io.open(os.path.join(HERE, "tsm-filing-probe.json"), "w", encoding="utf-8").write(
    json.dumps(out, ensure_ascii=False, indent=1))
print("\nsaved tsm-filing-probe.json")
