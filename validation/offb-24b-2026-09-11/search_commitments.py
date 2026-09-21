# OFFB-24B: 정기보고서 원문에서 미개시 확정 약정(B종)과 계약 수입 근거를 찾는다.
# 총액만 보지 않고 기간·연도별 지출·취소 조건·대응 수입 문맥을 함께 남긴다.
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
UA = "stock-report-harness OFFB-24B validation (contact via repository issues)"
H = {"User-Agent": UA, "Accept-Encoding": "gzip, deflate", "Host": "www.sec.gov"}

DOCS = [
    ("SPCX-10Q-2026Q2",
     "https://www.sec.gov/Archives/edgar/data/1181412/000162828026052535/spcx-20260630.htm"),
    ("AMZN-10Q-2026Q2",
     "https://www.sec.gov/Archives/edgar/data/1018724/000101872426000026/amzn-20260630.htm"),
]

# B종(미개시 확정 약정) 후보 문구
B_PAT = [
    r"have not yet commenced",
    r"not yet commenced",
    r"purchase obligation",
    r"unconditional purchase",
    r"[Cc]ommitments and [Cc]ontingencies",
    r"contractual obligation",
    r"minimum (?:lease|purchase) (?:payments|commitments)",
]
# 계약 수입(대응 수입) 후보 문구
REV_PAT = [
    r"remaining performance obligation",
    r"backlog",
    r"unearned revenue",
    r"deferred revenue",
]
CTX = 700


def strip_html(h):
    h = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", h)
    h = re.sub(r"(?s)<[^>]+>", " ", h)
    h = h.replace("&nbsp;", " ").replace("&amp;", "&").replace("&#8217;", "'")
    h = re.sub(r"&[a-zA-Z#0-9]+;", " ", h)
    return re.sub(r"\s+", " ", h)


def probe(name, url, patterns, label):
    fn = os.path.join(RAW, "%s.txt" % name)
    if os.path.exists(fn):
        txt = io.open(fn, encoding="utf-8").read()
        print("   (캐시 사용 %s)" % name)
    else:
        r = fetchlib.get(url, hdrs=H, timeout=180)
        print("   fetch status=%s bytes=%s %s" % (r["status"], r["bytes"], r.get("error") or ""))
        if not r["ok"]:
            return None
        io.open(os.path.join(RAW, "%s.html" % name), "w", encoding="utf-8").write(r["text"])
        txt = strip_html(r["text"])
        io.open(fn, "w", encoding="utf-8").write(txt)
        time.sleep(1.0)
    print("   본문 %d자" % len(txt))
    hits = 0
    for p in patterns:
        ms = list(re.finditer(p, txt))
        if not ms:
            print("   [%-38s] 0건" % p[:38])
            continue
        print("   [%-38s] %d건" % (p[:38], len(ms)))
        for m in ms[:2]:
            seg = txt[max(0, m.start() - 250):m.start() + CTX].strip()
            print("      ...%s..." % seg)
            print()
            hits += 1
    return txt


for name, url in DOCS:
    print("=" * 96)
    print(name, url)
    print("--- B종(미개시 확정 약정) 후보 ---")
    t = probe(name, url, B_PAT, "B")
    if t is not None:
        print("--- 계약 수입 후보 ---")
        for p in REV_PAT:
            ms = list(re.finditer(p, t))
            print("   [%-38s] %d건" % (p[:38], len(ms)))
            for m in ms[:2]:
                seg = t[max(0, m.start() - 250):m.start() + CTX].strip()
                print("      ...%s..." % seg)
                print()
