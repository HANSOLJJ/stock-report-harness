# MCAP-36: 차입금 개념을 추측하지 않고 탐색한다.
# 기준 대차대조표일에 시점 사실이 있는 개념 중 이름이 부채성인 것을 전부 나열한다.
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "g1-fill-27b-2026-09-11"))
from build_ttm import load  # noqa: E402

C13 = ("C:/Users/noble/orca/workspaces/stock-report-harness/C-13/validation/"
       "cash-fcf-35/cash_fcf_35_results.json")
cash13 = {it["company_id"]: it for it in json.load(io.open(C13, encoding="utf-8"))["items"]}

PAT = re.compile(r"(?i)debt|borrow|notesPayable|bonds|loans|lease|commercialPaper|financingLiab")

for cid in ("oracle", "tesla", "tsmc", "alibaba", "spacex-xai"):
    d, _, _ = load(cid)
    facts = d["facts"]
    c = cash13[cid]
    on, unit = c["balance_sheet_date"], c["currency"]
    print("=" * 108)
    print("%s | 기준 대차대조표일 %s | 통화 %s" % (cid, on, unit))
    print("=" * 108)
    found = []
    for tax, cs in facts.items():
        for cname, body in cs.items():
            if not PAT.search(cname):
                continue
            for u, es in (body.get("units") or {}).items():
                if u != unit:
                    continue
                for e in es:
                    if e.get("start") or e.get("end") != on:
                        continue
                    found.append((("%s:%s" % (tax, cname)), e["val"], e.get("form")))
    seen = {}
    for name, val, form in found:
        seen.setdefault(name, (val, form))
    for name in sorted(seen):
        val, form = seen[name]
        print("   %-68s %18s  %s" % (name[:68], "{:,.0f}".format(val), form))
    if not seen:
        print("   (해당 날짜에 부채성 시점 사실 없음)")
    print()
