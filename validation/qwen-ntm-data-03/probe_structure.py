"""QWEN-NTM-DATA-03: StockAnalysis forecast 페이지 HTML 구조 조사.

분기 EPS 컨센서스가 무료 공개 HTML 안에 실제로 들어있는지, 유료 장벽인지 판별하기 위해
스크립트/JSON 페이로드와 표 구조를 덤프한다. 읽기 전용 조사 목적.
"""
import io
import json
import os
import re
import sys

from probe_fetch import get

HERE = os.path.dirname(os.path.abspath(__file__))
URL = "https://stockanalysis.com/stocks/meta/forecast/"

r = get(URL)
t = r["text"]
print("status=%s bytes=%d" % (r["status"], r["bytes"]))

# 1) JSON 페이로드 후보 탐색
print("\n=== 1. 스크립트 블록 / JSON 페이로드 후보 ===")
for pat in [r"window\.__NUXT__", r"__NEXT_DATA__", r"window\.__INITIAL_STATE__",
            r"<script[^>]*type=\"application/json\"", r"application/ld\+json",
            r"window\.__remixContext", r"data-page"]:
    hits = re.findall(pat, t)
    print("  %-46s %d건" % (pat, len(hits)))

scripts = re.findall(r"<script[^>]*>(.*?)</script>", t, re.S)
print("  <script> 블록 총 %d개" % len(scripts))
big = [(i, len(s)) for i, s in enumerate(scripts) if len(s) > 2000]
print("  2000자 초과 블록: %s" % big[:10])

# 2) 분기 관련 문자열 주변 문맥
print("\n=== 2. 'Quarterly' 주변 문맥 ===")
for m in re.finditer(r"Quarterly", t):
    a, b = max(0, m.start() - 200), min(len(t), m.end() + 200)
    frag = re.sub(r"\s+", " ", t[a:b])
    print("  @%d: ...%s..." % (m.start(), frag))
    print()

# 3) 분기 라벨 패턴 탐색 (Q3 2026, Sep 2026, FY 2026 등)
print("\n=== 3. 기간 라벨 패턴 ===")
for pat, name in [(r"\bQ[1-4]\s*20\d\d\b", "Q# YYYY"),
                  (r"\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+20\d\d\b", "Mon YYYY"),
                  (r"\bFY\s*20\d\d\b", "FY YYYY"),
                  (r"\b(20\d\d)\s*(E|A)\b", "YYYY E/A")]:
    hits = re.findall(pat, t)
    print("  %-12s %d건  표본=%s" % (name, len(hits), hits[:14]))

# 4) 'EPS This Year' / 'EPS Next Year' / Forward PE 값 위치
print("\n=== 4. 핵심 값 주변 문맥 ===")
for key in ["EPS This Year", "EPS Next Year", "Forward PE", "non-GAAP", "Last updated"]:
    for m in list(re.finditer(re.escape(key), t))[:2]:
        a, b = max(0, m.start() - 120), min(len(t), m.end() + 260)
        frag = re.sub(r"\s+", " ", t[a:b])
        print("  [%s] @%d: ...%s..." % (key, m.start(), frag))
        print()

# 5) 유료 장벽 표식
print("\n=== 5. 유료 장벽 표식 ===")
for key in ["Upgrade", ">Pro<", "\"Pro\"", "paywall", "pro-tier", "locked"]:
    print("  %-12s %d건" % (key, len(re.findall(re.escape(key), t))))

# 6) 표 구조 샘플
print("\n=== 6. <table> 개수와 첫 표 샘플 ===")
tables = re.findall(r"<table.*?</table>", t, re.S)
print("  <table> %d개" % len(tables))
for i, tb in enumerate(tables[:3]):
    txt = re.sub(r"<[^>]+>", "|", tb)
    txt = re.sub(r"\|+", "|", txt)
    print("  --- table %d (len=%d) ---" % (i, len(tb)))
    print("  " + re.sub(r"\s+", " ", txt)[:700])

with io.open(os.path.join(HERE, "meta-forecast-raw.html"), "w", encoding="utf-8") as f:
    f.write(t)
print("\n원문 저장: meta-forecast-raw.html (%d bytes)" % len(t.encode("utf-8")))
