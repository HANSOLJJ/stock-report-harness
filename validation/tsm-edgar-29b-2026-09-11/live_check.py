# TSM-EDGAR-29B: SEC 가 그 사이 FY2025 를 채웠는지 라이브로 재확인한다.
# 채웠다면 우회 자체가 불필요하므로 권고가 달라진다. SEC 만 호출한다.
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "consensus-source-2026-09-09"))
from fetchlib import get  # noqa: E402

CIK = "0001046179"  # TSM
OUT = os.path.join(HERE, "raw")
os.makedirs(OUT, exist_ok=True)

targets = [("ifrs-full", "RevenueFromContractsWithCustomers"),
           ("ifrs-full", "ProfitLossFromOperatingActivities")]

for tax, cname in targets:
    url = ("https://data.sec.gov/api/xbrl/companyconcept/CIK%s/%s/%s.json" % (CIK, tax, cname))
    try:
        body = get(url)
    except Exception as e:
        print("%-46s 조회 실패: %s" % (cname, e))
        continue
    d = body if isinstance(body, dict) else json.loads(body)
    io.open(os.path.join(OUT, "live-companyconcept-%s.json" % cname), "w",
            encoding="utf-8").write(json.dumps(d, ensure_ascii=False, indent=1))
    twd = [e for e in (d.get("units") or {}).get("TWD", [])
           if e.get("start") and 350 <= (
               __import__("datetime").date.fromisoformat(e["end"])
               - __import__("datetime").date.fromisoformat(e["start"])).days <= 380]
    ends = sorted({e["end"] for e in twd})
    fy25 = [e for e in twd if e["end"].startswith("2025-12")]
    print("%-46s TWD 연간 최신 end=%s  | FY2025 관측 %d건 %s" % (
        cname, ends[-1] if ends else "-", len(fy25),
        ("값=" + "{:,}".format(fy25[-1]["val"])) if fy25 else ""))
