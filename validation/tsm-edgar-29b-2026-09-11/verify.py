# TSM-EDGAR-29B: 채택값의 주변 사실을 검증한다.
# (1) 제출본 신원 (2) companyfacts FY2025 부재 재확인 (3) 표 내부 산술 (4) 제출 원문 대조 (5) 환산율 근거
import io
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "..", "f6-fx-16-2026-09-10", "raw")
ext = json.load(io.open(os.path.join(HERE, "tsm-fy2025-extract.json"), encoding="utf-8"))

print("=" * 96)
print("(1) 제출본 신원 — submissions 인덱스에서 확인")
print("=" * 96)
sub = json.load(io.open(os.path.join(RAW, "sec-TSM-submissions.json"), encoding="utf-8"))
r = sub["filings"]["recent"]
cols = ["accessionNumber", "form", "filingDate", "reportDate", "primaryDocument",
        "isXBRL", "isInlineXBRL"]
for i, f in enumerate(r["form"]):
    if f in ("20-F", "20-F/A"):
        row = {c: r[c][i] for c in cols if c in r}
        print("   ", json.dumps(row, ensure_ascii=False))
        if len([1 for j, g in enumerate(r["form"][:i + 1]) if g.startswith("20-F")]) >= 3:
            break

print()
print("=" * 96)
print("(2) companyfacts FY2025 부재 재확인 — 지시서 전제를 그대로 믿지 않는다")
print("=" * 96)
cf = json.load(io.open(os.path.join(RAW, "sec-TSM-companyfacts.json"), encoding="utf-8"))
facts = cf["facts"]
print("   companyfacts 스냅샷 생성 시각: 파일 mtime 기준 2026-09-10, entityName=%s" % cf.get("entityName"))
for concept in ("ifrs-full:RevenueFromContractsWithCustomers",
                "ifrs-full:Revenue",
                "ifrs-full:ProfitLossFromOperatingActivities"):
    tax, cname = concept.split(":")
    body = facts.get(tax, {}).get(cname)
    if not body:
        print("   %-52s 개념 자체가 없음" % concept)
        continue
    ends = sorted({e["end"] for u, es in (body.get("units") or {}).items()
                   for e in es if u == "TWD"})
    yrs = sorted({e[:4] for e in ends})
    print("   %-52s TWD 관측 연도 %s  (최신 end=%s)" % (concept, ",".join(yrs), ends[-1] if ends else "-"))

# FY2025 를 가진 개념이 정말 하나도 없는지 전수 확인 (부재의 사유를 찾으라는 교훈 적용)
hits2025 = []
for tax, cs in facts.items():
    for cname, body in cs.items():
        for u, es in (body.get("units") or {}).items():
            for e in es:
                if (e.get("end") or "").startswith("2025-12") and e.get("start", "").startswith("2025-01"):
                    hits2025.append((tax, cname, u, e.get("accn"), e.get("form")))
print("\n   2025 회계연도(2025-01~2025-12) 전체 기간 사실 개수: %d" % len(hits2025))
for h in sorted(set(hits2025))[:10]:
    print("      ", h)

# 2026-04 제출본이 companyfacts 에 기여한 사실
accn_target = "0001628280-26-025362"
contrib = []
for tax, cs in facts.items():
    for cname, body in cs.items():
        for u, es in (body.get("units") or {}).items():
            for e in es:
                if e.get("accn") == accn_target:
                    contrib.append((tax, cname, u, e.get("start"), e.get("end")))
print("\n   accn %s 가 companyfacts 에 기여한 사실 %d건" % (accn_target, len(contrib)))
for c in sorted(set(contrib))[:10]:
    print("      ", c)

print()
print("=" * 96)
print("(3) 표 내부 산술 검증 — 채택값이 표 안에서 스스로 맞는가")
print("=" * 96)
rows = json.load(io.open(os.path.join(HERE, "r4-parsed.json"), encoding="utf-8"))
byl = {}
for r in rows:
    if r["nums"] and r["label"] not in byl:
        byl[r["label"]] = r["nums"]
C = {"2025TWD": 0, "2025USD": 1, "2024TWD": 2, "2023TWD": 3}
for colname, ci in C.items():
    g = byl["NET REVENUE"][ci] - byl["COST OF REVENUE"][ci]
    gp = byl["GROSS PROFIT"][ci]
    op = gp - byl["Total operating expenses"][ci] + byl["OTHER OPERATING INCOME AND EXPENSES, NET"][ci]
    opd = byl["INCOME FROM OPERATIONS"][ci]
    print("   %-9s  매출-매출원가=%s vs 매출총이익=%s  [%s]   총이익-영업비용+기타=%s vs 영업이익=%s  [%s]" % (
        colname, "{:,.1f}".format(g), "{:,.1f}".format(gp), "OK" if abs(g - gp) < 0.15 else "불일치",
        "{:,.1f}".format(op), "{:,.1f}".format(opd), "OK" if abs(op - opd) < 0.15 else "불일치"))

print()
print("=" * 96)
print("(4) 제출 원문 20-F 본문과 대조 — R4 는 EDGAR 렌더링이므로 별개 경로다")
print("=" * 96)
txt = io.open(os.path.join(RAW, "20F-TSM-FY2025.txt"), encoding="utf-8", errors="replace").read()
flat = re.sub(r"[\u00a0\s]+", " ", txt)
for label, want in (("NET REVENUE FY2025", "3,809,054,3"), ("NET REVENUE FY2025", "3,809,054.3"),
                    ("INCOME FROM OPERATIONS FY2025", "1,936,091.7"),
                    ("NET REVENUE FY2024", "2,894,307.7"),
                    ("INCOME FROM OPERATIONS FY2024", "1,322,053.0")):
    n = flat.count(want)
    if n:
        i = flat.find(want)
        print("   %-32s %-14s 출현 %d회  …%s…" % (label, want, n,
                                                flat[max(0, i - 95):i + 22].strip()))
    else:
        print("   %-32s %-14s 출현 0회" % (label, want))

print()
print("=" * 96)
print("(5) 편의환산율 근거 — 원문에 명시된 환율 문장")
print("=" * 96)
for m in re.finditer(r"(NT\$\s?31\.[0-9]{2}|convenience|noon buying rate|H\.10|Federal Reserve)", flat):
    i = m.start()
    seg = flat[max(0, i - 210):i + 210].strip()
    print("   …%s…" % seg)
    print("   " + "-" * 90)
