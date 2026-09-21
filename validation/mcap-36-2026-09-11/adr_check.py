# MCAP-36: ADR 2사(TSM·BABA)의 주식수가 ADR 기준인지 원주 기준인지 가른다.
# ADR 비율(TSM 5:1, BABA 8:1)로 나눠떨어지는지, 주가 단위와 맞는지를 본다.
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "g1-fill-27b-2026-09-11"))
from build_ttm import load  # noqa: E402

EXTRA = [("ifrs-full", "NumberOfSharesIssuedAndFullyPaid"),
         ("ifrs-full", "NumberOfSharesAuthorised"),
         ("ifrs-full", "WeightedAverageShares"),
         ("dei", "EntityCommonStockSharesOutstanding"),
         ("us-gaap", "CommonStockSharesOutstanding")]
RATIO = {"tsmc": 5, "alibaba": 8}   # 원주 : ADR/ADS  (ADS 1주당 원주 n주)

for cid in ("tsmc", "alibaba"):
    d, origin, rel = load(cid)
    facts = d["facts"]
    print("=" * 96)
    print("%s | %s | ADR 비율 원주 %d : ADS 1" % (cid, d.get("entityName"), RATIO[cid]))
    print("=" * 96)
    for tax, cname in EXTRA:
        body = facts.get(tax, {}).get(cname)
        if not body:
            continue
        rows = []
        for unit, es in (body.get("units") or {}).items():
            for e in es:
                rows.append((e.get("end"), e.get("val"), unit, e.get("form"), e.get("filed")))
        rows.sort()
        last = rows[-1]
        print("  %-46s 건수 %-4d 최신 %s  %s" % (
            "%s:%s" % (tax, cname), len(rows), last[0], "{:,}".format(last[1])))
        # 최근 3건
        for r in rows[-3:]:
            print("       %s  %18s  unit=%s form=%s filed=%s" % (
                r[0], "{:,}".format(r[1]), r[2], r[3], r[4]))
    print()

# 두 개념 사이의 배수를 본다 — ADR 비율과 일치하면 단위가 갈린 것이다
print("=" * 96)
print("단위 판정 — dei 값과 원주 개념 값의 배수가 ADR 비율과 맞는가")
print("=" * 96)
for cid in ("tsmc", "alibaba"):
    d, _, _ = load(cid)
    f = d["facts"]

    def latest(tax, cname):
        b = f.get(tax, {}).get(cname)
        if not b:
            return None
        rows = [(e.get("end"), e.get("val")) for u, es in (b.get("units") or {}).items() for e in es]
        return sorted(rows)[-1] if rows else None

    dei = latest("dei", "EntityCommonStockSharesOutstanding")
    ifrs = latest("ifrs-full", "NumberOfSharesIssuedAndFullyPaid")
    ug = latest("us-gaap", "CommonStockSharesOutstanding")
    print("  %-9s dei=%s  ifrs_issued=%s  usgaap_out=%s" % (
        cid,
        ("%s@%s" % ("{:,}".format(dei[1]), dei[0])) if dei else "없음",
        ("%s@%s" % ("{:,}".format(ifrs[1]), ifrs[0])) if ifrs else "없음",
        ("%s@%s" % ("{:,}".format(ug[1]), ug[0])) if ug else "없음"))
    base = ifrs or ug
    if dei and base and dei[1]:
        r = base[1] / dei[1]
        print("       배수 = %.4f   (ADR 비율 %d 과 %s)" % (
            r, RATIO[cid], "일치 → dei 는 ADS 수, 상대는 원주 수" if abs(r - RATIO[cid]) < 0.05
            else "불일치 → 같은 단위이거나 다른 사유"))
