# MCAP-36: 12개사 발행주식수를 확정한다. 개념 선택 근거와 기준일을 함께 남긴다.
# 규약 — 기준일(2026-09-02)에 가장 가까운 '시점' 주식수를 쓴다. 기간평균은 쓰지 않는다.
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "g1-fill-27b-2026-09-11"))
from build_ttm import SOURCES, load  # noqa: E402

cov = json.load(io.open(os.path.join(HERE, "classes-netcash.json"), encoding="utf-8"))["classes"]

# 표지(차원 태깅)에서 뽑은 클래스 합. companyfacts 가 버리는 값이라 별도 경로다.
COVER = {
    "meta":     {"total": 2547506225, "asof": "2026-07-24", "src": "10-Q 0001628280-26-050705 Cover Page",
                 "classes": "A 2,205,128,509 + B 342,377,716"},
    "alphabet": {"total": 12230000000, "asof": "2026-07-15", "src": "10-Q 0001652044-26-000071 COVER PAGE",
                 "classes": "A 5,868M + C 5,527M + B 835M"},
    "palantir": {"total": 2403058480, "asof": "2026-07-27", "src": "10-Q 0001321655-26-000041 Cover Page",
                 "classes": "A 2,300,713,329 + B 101,340,151 + F 1,005,000"},
    "spacex-xai": {"total": 13181779945, "asof": "2026-07-28",
                   "src": "10-Q spcx-20260630.htm 표지 (C-13 _raw, SEC 원본)",
                   "classes": "A 7,696,293,669 + B 5,485,486,276"},
}
# ADR — 원주 수와 ADS 비율. 주가가 ADS(USD) 이므로 ADS 수로 환산해야 한다.
ADR = {"tsmc": {"ordinary": 25932524521, "asof": "2025-12-31", "ratio": 5,
                "src": "20-F 0001628280-26-025362 표지 — 'As of December 31, 2025, 25,932,524,521 Common Shares'",
                "concept": "dei:EntityCommonStockSharesOutstanding (원문 표지와 일치 확인)"},
       "alibaba": {"ordinary": 18580374278, "asof": "2026-03-31", "ratio": 8,
                   "src": "20-F FY2026 대차대조표 — '18,580,374,278 shares issued and outstanding as of March 31, 2026'",
                   "concept": "us-gaap:CommonStockSharesOutstanding (dei 는 10배 어긋나 사용 불가)"}}


def pick(cid):
    d, _, rel = load(cid)
    f = d["facts"]

    def latest(tax, cname):
        b = f.get(tax, {}).get(cname)
        if not b:
            return None
        rows = [(e.get("end"), e.get("val"), e.get("form"), e.get("filed"))
                for u, es in (b.get("units") or {}).items() for e in es]
        return sorted(rows)[-1] if rows else None

    if cid in ADR:
        a = ADR[cid]
        return {"basis": "ADS", "shares": a["ordinary"] / a["ratio"], "ordinary": a["ordinary"],
                "adr_ratio": a["ratio"], "asof": a["asof"], "concept": a["concept"],
                "source": a["src"], "path": "20-F 원문 대조"}
    if cid in COVER:
        c = COVER[cid]
        return {"basis": "보통주(전 클래스 합)", "shares": c["total"], "asof": c["asof"],
                "concept": "dei:EntityCommonStockSharesOutstanding (클래스별 차원 태깅)",
                "source": c["src"], "classes": c["classes"], "path": "표지 렌더링(차원)"}
    dei = latest("dei", "EntityCommonStockSharesOutstanding")
    ug = latest("us-gaap", "CommonStockSharesOutstanding")
    use = dei if dei else ug
    which = "dei:EntityCommonStockSharesOutstanding" if dei else "us-gaap:CommonStockSharesOutstanding"
    return {"basis": "보통주", "shares": use[1], "asof": use[0], "concept": which,
            "source": "%s %s" % (use[2], use[3]), "path": "companyfacts(무차원)",
            "crosscheck_usgaap": ug[1] if ug else None}


rows = {}
print("%-12s %-22s %-13s %-46s %s" % ("company", "주식수", "기준일", "개념", "경로"))
print("-" * 128)
for cid in SOURCES:
    r = pick(cid)
    rows[cid] = r
    print("%-12s %-22s %-13s %-46s %s" % (
        cid, "{:,.0f}".format(r["shares"]), r["asof"], r["concept"][:46], r["path"]))

io.open(os.path.join(HERE, "shares-final.json"), "w", encoding="utf-8").write(
    json.dumps(rows, ensure_ascii=False, indent=1))
print("\nADR 환산")
for cid in ADR:
    r = rows[cid]
    print("  %-9s 원주 %s ÷ %d = ADS %s" % (
        cid, "{:,}".format(r["ordinary"]), r["adr_ratio"], "{:,.0f}".format(r["shares"])))
print("\nsaved shares-final.json")
