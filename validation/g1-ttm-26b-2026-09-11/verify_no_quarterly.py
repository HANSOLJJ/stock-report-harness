# G1-TTM-26B: 분기 행 부재를 전 개념 전수로 확인하고, 부재의 '이유'까지 원문에서 찾는다.
# (memory: search-for-absence-explanation — 값 이름으로만 검색하고 끝내지 않는다)
import datetime as dt
import io
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
CF = os.path.join(HERE, "..", "f6-fx-16-2026-09-10", "raw", "sec-BABA-companyfacts.json")
SUB = os.path.join(HERE, "..", "offb-24b-2026-09-11", "raw", "sec-BABA-submissions.json")
F20 = os.path.join(HERE, "..", "f6-fx-16-2026-09-10", "raw", "20F-BABA-FY2026.txt")

d = json.load(io.open(CF, encoding="utf-8"))
facts = d["facts"]

print("=" * 90)
print("A. 전 개념 전수 — 80~100일(분기) 관측이 하나라도 있는가")
print("=" * 90)
buckets = {}
quarterly = []
halfyear = []
for tax, concepts in facts.items():
    for cname, body in concepts.items():
        for unit, entries in (body.get("units") or {}).items():
            for e in entries:
                s, en = e.get("start"), e.get("end")
                if not s or not en:
                    continue
                days = (dt.date.fromisoformat(en) - dt.date.fromisoformat(s)).days
                k = (days // 30) * 30
                buckets[k] = buckets.get(k, 0) + 1
                if 80 <= days <= 100:
                    quarterly.append((tax, cname, unit, s, en, e.get("val"), e.get("form")))
                if 170 <= days <= 190:
                    halfyear.append((tax, cname, unit, s, en, e.get("val"), e.get("form")))

print("기간 길이 히스토그램 (30일 단위 버킷 → 건수):")
for k in sorted(buckets):
    print("   %3d~%3d일 : %5d" % (k, k + 29, buckets[k]))
print()
print("80~100일(분기) 관측: **%d건**" % len(quarterly))
for q in quarterly[:8]:
    print("   ", q)
print()
print("170~190일(반기) 관측: %d건" % len(halfyear))
seen = set()
for h in halfyear:
    key = (h[3], h[4], h[6])
    if key in seen:
        continue
    seen.add(key)
    print("    %s ~ %s  form=%s  (%s %s)" % (h[3], h[4], h[6], h[1], h[2]))

print()
print("=" * 90)
print("B. 제출 이력 — 10-Q 가 실제로 있는가")
print("=" * 90)
if os.path.exists(SUB):
    s = json.load(io.open(SUB, encoding="utf-8"))
    rf = s.get("filings", {}).get("recent", {})
    from collections import Counter
    c = Counter(rf.get("form", []))
    print("   최근 제출 양식 분포: %s" % json.dumps(dict(c.most_common(10)), ensure_ascii=False))
    print("   10-Q 건수: **%d**" % c.get("10-Q", 0))
    print("   20-F 건수: %d,  6-K 건수: %d" % (c.get("20-F", 0), c.get("6-K", 0)))
else:
    print("   submissions 스냅샷 없음")

print()
print("=" * 90)
print("C. 부재의 '이유' 를 20-F 원문에서 찾는다 (값 이름 검색으로 끝내지 않는다)")
print("=" * 90)
t = io.open(F20, encoding="utf-8").read()
for p in [r"foreign private issuer",
          r"not required to file periodic reports and financial statements .{0,120}",
          r"exempt from certain disclosure requirements",
          r"as frequently or as promptly as domestic",
          r"quarterly"]:
    ms = list(re.finditer(p, t, re.I))
    print("  [%-52s] %d건" % (p[:52], len(ms)))
    for m in ms[:1]:
        seg = re.sub(r"\s+", " ", t[max(0, m.start() - 400):m.start() + 500])
        print("     ...%s..." % seg)
        print()
