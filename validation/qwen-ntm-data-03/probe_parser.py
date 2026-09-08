"""QWEN-NTM-DATA-03 파서 검증: price 추출 실패와 EPS Next Year 역전 의심 건을 원문으로 확인한다."""
import io
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))


def read(p):
    return io.open(os.path.join(HERE, p), encoding="utf-8").read()


def ctx(html, needle, before=150, after=400, n=3):
    out = []
    for i, m in enumerate(re.finditer(re.escape(needle), html)):
        if i >= n:
            break
        a, b = max(0, m.start() - before), min(len(html), m.end() + after)
        out.append(re.sub(r"\s+", " ", html[a:b]))
    return out


print("=" * 100)
print("[1] overview 의 주가 표기 구조 (meta)")
ov = read("raw-meta-overview.html")
for pat in [r"Stock Price", r"At close", r'"price"', r"data-price", r"class=\"[^\"]*price"]:
    hits = re.findall(pat, ov)
    print("  %-24s %d건" % (pat, len(hits)))
print()
for c in ctx(ov, "At close", 700, 200, 2):
    print("  ..." + c + "...\n")

print("=" * 100)
print("[2] forecast 의 EPS This/Next Year 구조 — meta(정상) vs alphabet(역전 의심)")
for cid in ("meta", "alphabet", "amazon"):
    fc = read("raw-%s-forecast.html" % cid)
    print("\n--- %s ---" % cid)
    for label in ("EPS This Year", "EPS Next Year"):
        for c in ctx(fc, label, 60, 520, 1):
            print("  [%s] ...%s..." % (label, c))

print("=" * 100)
print("[3] EPS 카드 4종의 라벨 전체 목록 (meta forecast)")
fc = read("raw-meta-forecast.html")
cards = re.findall(r'text-base font-normal text-gray-800 dark:text-dark-200">([^<]{3,40})</div>', fc)
print("  카드 라벨:", cards)
print()
print("[3b] alphabet forecast 카드 라벨")
fc2 = read("raw-alphabet-forecast.html")
cards2 = re.findall(r'text-base font-normal text-gray-800 dark:text-dark-200">([^<]{3,40})</div>', fc2)
print("  카드 라벨:", cards2)

print("=" * 100)
print("[4] 연간 EPS 표(Financial Forecast) 의 EPS 행 — alphabet")
for m in re.finditer(r"FY\s*(20\d\d)", fc2):
    seg = re.sub(r"<[^>]+>", "|", fc2[m.end(): m.end() + 200])
    print("  FY %s -> %s" % (m.group(1), re.sub(r"\|+", "|", seg)[:110]))
