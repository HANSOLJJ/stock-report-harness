# MCAP-36: 12개사 companyfacts 에서 주식수 관련 개념을 전수로 센다.
# 건수만 보지 않고 단위·축(member)·기준일 분포까지 본다. 0건이면 왜 0건인지를 같은 파일에서 찾는다.
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "g1-fill-27b-2026-09-11"))
from build_ttm import SOURCES, load  # noqa: E402

ASOF = "2026-09-02"

# 주식수 후보. 뜻이 각각 다르므로 한 번에 고르지 않고 먼저 존재 여부를 전부 본다.
CANDIDATES = [
    ("dei", "EntityCommonStockSharesOutstanding"),
    ("us-gaap", "CommonStockSharesOutstanding"),
    ("us-gaap", "CommonStockSharesIssued"),
    ("us-gaap", "WeightedAverageNumberOfSharesOutstandingBasic"),
    ("us-gaap", "WeightedAverageNumberOfDilutedSharesOutstanding"),
    ("ifrs-full", "NumberOfSharesOutstanding"),
    ("ifrs-full", "NumberOfSharesIssued"),
]


def scan(facts):
    out = {}
    for tax, cname in CANDIDATES:
        body = facts.get(tax, {}).get(cname)
        if not body:
            continue
        rows = []
        for unit, entries in (body.get("units") or {}).items():
            for e in entries:
                rows.append({"unit": unit, "end": e.get("end"), "start": e.get("start"),
                             "val": e.get("val"), "form": e.get("form"),
                             "filed": e.get("filed"), "accn": e.get("accn"),
                             "frame": e.get("frame")})
        if rows:
            out["%s:%s" % (tax, cname)] = rows
    return out


print("%-12s %-52s %-6s %-12s %s" % ("company", "concept", "건수", "최신 end", "최신 val"))
print("-" * 118)
summary = {}
for cid in SOURCES:
    d, origin, rel = load(cid)
    facts = d["facts"]
    found = scan(facts)
    summary[cid] = {"entity": d.get("entityName"), "cik": d.get("cik"),
                    "source_file": rel, "concepts": {}}
    if not found:
        print("%-12s %-52s %s" % (cid, "(주식수 후보 개념 전부 없음)", "★"))
    for k, rows in found.items():
        rows.sort(key=lambda r: (r["end"] or "", r["filed"] or ""))
        last = rows[-1]
        summary[cid]["concepts"][k] = {
            "count": len(rows),
            "units": sorted({r["unit"] for r in rows}),
            "latest": last,
            "ends": sorted({r["end"] for r in rows})[-3:],
        }
        print("%-12s %-52s %-6d %-12s %s" % (
            cid, k, len(rows), last["end"], "{:,}".format(last["val"]) if last["val"] else "-"))
    # 전체 facts 에서 shares 단위를 쓰는 개념 목록(후보 밖 포함)
    share_concepts = []
    for tax, cs in facts.items():
        for cname, body in cs.items():
            if "shares" in (body.get("units") or {}):
                share_concepts.append("%s:%s" % (tax, cname))
    summary[cid]["all_shares_unit_concepts"] = sorted(share_concepts)
    print("%-12s   └ shares 단위를 쓰는 개념 총 %d개" % (cid, len(share_concepts)))

io.open(os.path.join(HERE, "shares-inventory.json"), "w", encoding="utf-8").write(
    json.dumps(summary, ensure_ascii=False, indent=1))
print("\nsaved shares-inventory.json")
