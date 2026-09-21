"""QWEN-NTM-DATA-03 보강 2: 저장된 원문 HTML 에서 회계연도 말일의 직접 증거만 컴팩트하게 추출한다.

derive_fy_end.py 의 'Current Qtr. = 회계연도 1분기' 가정은 역년 회사에서 성립하지 않아 폐기했다.
대신 이미 받아 둔 원문에서 기간말 날짜(M/D/YYYY) 와 'FY … (Mon YYYY)' 류 라벨만 뽑아
직접 증거가 있는지 확인한다. 출력을 작게 유지한다.
"""
import io
import os
import re
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
CIDS = ["meta", "nvidia", "alphabet", "microsoft", "amazon",
        "apple", "oracle", "palantir", "tesla", "spacex-xai"]

DATE = re.compile(r"\b(\d{1,2}/\d{1,2}/20\d\d)\b")
FYMON = re.compile(r"FY\s*20\d\d\s*\(([A-Za-z]{3}\s*20\d\d)\)")
MONYY = re.compile(r"\b([A-Z][a-z]{2})\s+(20\d\d)\b")
PEREND = re.compile(r"(?:Period End|Fiscal Year End|FY End|Quarter Ended|period ending)", re.I)

for cid in CIDS:
    for kind in ("forecast", "overview"):
        p = os.path.join(HERE, "raw-%s-%s.html" % (cid, kind))
        if not os.path.isfile(p):
            continue
        h = io.open(p, encoding="utf-8").read()
        dates = []
        for d in DATE.findall(h):
            if d not in dates:
                dates.append(d)
        fymon = list(dict.fromkeys(FYMON.findall(h)))
        perend = [m.group(0) for m in PEREND.finditer(h)][:4]
        # 월 라벨 중 분기말 후보(3/6/9/12월 계열) 만 집계
        mons = Counter("%s %s" % (m, y) for m, y in MONYY.findall(h))
        top = [k for k, v in mons.most_common(8)]
        if dates or fymon or perend:
            print("%-12s %-9s dates=%s  FY(Mon)=%s  perend=%s" % (
                cid, kind, dates[:10] or "-", fymon[:6] or "-", perend or "-"))
            print("%-12s %-9s month-labels(top8)=%s" % ("", "", top))
print()
print("=== 판별 ===")
print("  M/D/YYYY 형태 기간말이 원문에 있으면 회계연도 말일의 직접 증거로 쓸 수 있다.")
print("  없으면 Yahoo 의 Earnings History 에서만 오는 값이므로(이번 수집에는 미포함) 간접 근거로 남는다.")
