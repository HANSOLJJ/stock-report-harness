# F6-FX-16 후속: TSM FY2025 가 companyfacts 에 없는 사유를 세 가설로 가른다.
#  H1 2026-04-16 제출분이 FY2025 20-F 가 아니다
#  H2 매출이 내가 본 개념 외의 다른 IFRS 개념으로 태깅됐다
#  H3 companyfacts 반영이 누락/지연됐다
# 값 대량 수집이 아니라 존재 여부와 개념 이름까지만 본다.
import io
import json
import os
import datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw")

d = json.load(io.open(os.path.join(RAW, "sec-TSM-companyfacts.json"), encoding="utf-8"))
facts = d["facts"]

print("=" * 78)
print("A. companyfacts 안에 2025 회계연도 관측이 하나라도 있는가")
print("=" * 78)

end_2025 = []          # end 가 2025-12-31 인 모든 사실
filed_2026 = set()     # 2026 년에 제출된 것으로 표시된 accession
any_end_by_year = {}

for tax, concepts in facts.items():
    for cname, body in concepts.items():
        for unit, entries in (body.get("units") or {}).items():
            for e in entries:
                en = e.get("end")
                if en:
                    y = en[:4]
                    any_end_by_year[y] = any_end_by_year.get(y, 0) + 1
                if en == "2025-12-31":
                    end_2025.append((tax, cname, unit, e.get("start"), e.get("val"),
                                     e.get("form"), e.get("filed"), e.get("accn"), e.get("fy"), e.get("fp")))
                if (e.get("filed") or "").startswith("2026"):
                    filed_2026.add((e.get("accn"), e.get("form"), e.get("filed")))

print("end 연도별 사실 수:", dict(sorted(any_end_by_year.items())))
print("end == 2025-12-31 인 사실 수:", len(end_2025))
if end_2025:
    print("  샘플 10건:")
    for r in end_2025[:10]:
        print("   ", r)

print()
print("=" * 78)
print("B. 2026 년에 제출된 것으로 표시된 accession 이 companyfacts 안에 있는가")
print("=" * 78)
if filed_2026:
    for a in sorted(filed_2026):
        print("   ", a)
else:
    print("   없음 — companyfacts 의 모든 사실이 2025 년 이전 제출분에서 왔다")

print()
print("=" * 78)
print("C. 가장 최근 제출 accession (companyfacts 기준)")
print("=" * 78)
accns = {}
for tax, concepts in facts.items():
    for cname, body in concepts.items():
        for unit, entries in (body.get("units") or {}).items():
            for e in entries:
                a = e.get("accn")
                f = e.get("filed")
                if a and f:
                    accns[a] = max(accns.get(a, ""), f)
for a, f in sorted(accns.items(), key=lambda kv: kv[1], reverse=True)[:6]:
    print("   %s  filed=%s" % (a, f))

print()
print("=" * 78)
print("D. 연간 매출 후보 개념 전수 — 2025 연간 값을 가진 개념이 있는가")
print("=" * 78)
found_any_2025_annual = []
for tax, concepts in facts.items():
    for cname, body in concepts.items():
        for unit, entries in (body.get("units") or {}).items():
            for e in entries:
                s, en = e.get("start"), e.get("end")
                if not s or not en:
                    continue
                days = (dt.date.fromisoformat(en) - dt.date.fromisoformat(s)).days
                if 350 <= days <= 380 and en.startswith("2025"):
                    found_any_2025_annual.append((tax, cname, unit, s, en, e.get("val"),
                                                  e.get("form"), e.get("filed")))
print("2025 연간(350~380일) 관측 수:", len(found_any_2025_annual))
for r in found_any_2025_annual[:15]:
    print("   ", r)

out = {
    "end_year_histogram": dict(sorted(any_end_by_year.items())),
    "facts_with_end_2025_12_31": len(end_2025),
    "sample_end_2025": end_2025[:20],
    "accessions_filed_in_2026": sorted(filed_2026),
    "latest_accessions_in_companyfacts": sorted(
        accns.items(), key=lambda kv: kv[1], reverse=True)[:6],
    "annual_2025_observations": found_any_2025_annual[:30],
}
io.open(os.path.join(HERE, "tsm-fy2025-diagnosis.json"), "w", encoding="utf-8").write(
    json.dumps(out, ensure_ascii=False, indent=1, default=str))
print("\nsaved tsm-fy2025-diagnosis.json")
