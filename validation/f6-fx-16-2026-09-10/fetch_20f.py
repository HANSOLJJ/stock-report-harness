# F6-FX-16: 20-F 원문을 직접 받아 convenience translation 문구·환율·기준일·범위를 대조한다.
# 인용에 그치지 않고 원문을 열어 확인하는 것이 이 단계의 목적이다.
import io
import os
import re
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "consensus-source-2026-09-09"))
import fetchlib  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw")
os.makedirs(RAW, exist_ok=True)

SEC_UA = "stock-report-harness F6-FX validation (contact via repository issues)"
H = {"User-Agent": SEC_UA, "Accept-Encoding": "gzip, deflate", "Host": "www.sec.gov"}

DOCS = [
    ("TSM-FY2025",
     "https://www.sec.gov/Archives/edgar/data/1046179/000162828026025362/tsm-20251231.htm"),
    ("BABA-FY2026",
     "https://www.sec.gov/Archives/edgar/data/1577552/000119312526231755/baba-20260331.htm"),
]

PATTERNS = [
    r"solely for the convenience of the reader",
    r"convenience translation",
    r"convenience of the reader",
    r"[Tt]ranslations? of (?:Renminbi|RMB|NT\$|New Taiwan dollar)[^.]{0,200}",
    r"noon buying rate",
    r"H\.?10 statistical release",
    r"Federal Reserve Board",
    r"rate of (?:RMB|NT\$)?[\d,.]+ ?(?:to|per|=)",
    r"US\$1\.00",
    r"UNAUDITED",
    r"unaudited",
]


def strip_html(h):
    h = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", h)
    h = re.sub(r"(?s)<[^>]+>", " ", h)
    h = h.replace("&nbsp;", " ").replace("&amp;", "&").replace("&#8217;", "'")
    h = re.sub(r"&[a-zA-Z#0-9]+;", " ", h)
    return re.sub(r"[ \t]+", " ", h)


for name, url in DOCS:
    print("=" * 84)
    print(name, url)
    r = fetchlib.get(url, hdrs=H, timeout=180)
    print("  status=%s bytes=%s %s" % (r["status"], r["bytes"], r.get("error") or ""))
    if not r["ok"]:
        continue
    io.open(os.path.join(RAW, "20F-%s.html" % name), "w", encoding="utf-8").write(r["text"])
    txt = strip_html(r["text"])
    io.open(os.path.join(RAW, "20F-%s.txt" % name), "w", encoding="utf-8").write(txt)
    print("  본문 텍스트 %d자 저장" % len(txt))
    hits = 0
    for p in PATTERNS:
        for m in list(re.finditer(p, txt))[:2]:
            seg = re.sub(r"\s+", " ", txt[max(0, m.start() - 420):m.start() + 620]).strip()
            print("\n  [%s]" % p[:42])
            print("   ...%s..." % seg)
            hits += 1
    print("\n  총 매치 %d" % hits)
    time.sleep(1.0)
