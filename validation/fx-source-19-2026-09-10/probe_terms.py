# FX-SOURCE-19 2단계: 약관·정책 문서만 조회한다(PRIV-ARR-17 표준).
# 내용/데이터 페이지는 이 단계에서 조회하지 않는다.
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

# (라벨, URL, 종류) — robots 는 별도 단계에서 이미 받음
DOCS = [
    ("api.stlouisfed.org-robots", "https://api.stlouisfed.org/robots.txt", "robots"),
    ("fred-api-terms", "https://fred.stlouisfed.org/docs/api/terms_of_use.html", "terms"),
    ("fred-legal", "https://fred.stlouisfed.org/legal/", "terms"),
    ("frb-legal", "https://www.federalreserve.gov/legal.htm", "terms"),
    ("frb-privacy-terms", "https://www.federalreserve.gov/privacy-terms.htm", "terms"),
    ("fmp-terms", "https://site.financialmodelingprep.com/terms-of-service", "terms"),
    ("bis-terms", "https://www.bis.org/terms_conditions.htm", "terms"),
    ("exchangerate-terms", "https://exchangerate.host/terms", "terms"),
    ("frankfurter-terms", "https://frankfurter.dev/legal/", "terms"),
]

KEYS = [
    r"non-?commercial", r"personal use", r"commercial use", r"redistribut",
    r"public domain", r"copyright", r"free of charge", r"attribution",
    r"[Aa]utomated", r"scrap", r"crawl", r"rate limit", r"API key",
    r"may not", r"prohibit", r"restrict",
]


def text_of(html):
    t = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", html)
    t = re.sub(r"(?s)<[^>]+>", " ", t)
    t = t.replace("&nbsp;", " ").replace("&amp;", "&")
    t = re.sub(r"&[a-zA-Z#0-9]+;", " ", t)
    return re.sub(r"\s+", " ", t).strip()


log = []
for name, url, kind in DOCS:
    r = fetchlib.get(url, timeout=45)
    head = "== %-26s %-5s %-8s %s" % (name, r["status"], r["bytes"], r.get("error") or "")
    print(head)
    log.append(head + "\n   " + url)
    if not r["ok"] or not r["text"]:
        log.append("")
        time.sleep(1.0)
        continue
    io.open(os.path.join(RAW, "doc-%s.html" % name), "w", encoding="utf-8").write(r["text"])
    body = r["text"] if kind == "robots" else text_of(r["text"])
    io.open(os.path.join(RAW, "doc-%s.txt" % name), "w", encoding="utf-8").write(body)
    if kind == "robots":
        print("      " + "\n      ".join(body.strip().splitlines()[:12]))
        log.append(body[:1200])
    else:
        hits = 0
        for k in KEYS:
            for m in list(re.finditer(k, body))[:1]:
                seg = body[max(0, m.start() - 220):m.start() + 320]
                print("   [%-16s] ...%s..." % (k[:16], seg[:260]))
                log.append("   [%s] ...%s..." % (k, seg))
                hits += 1
        log.append("   (키워드 매치 %d)" % hits)
    log.append("")
    time.sleep(1.2)

io.open(os.path.join(HERE, "terms-log.txt"), "w", encoding="utf-8").write(
    "조회 시각 UTC %s\n\n" % fetchlib.utcnow() + "\n".join(log))
print("\nsaved terms-log.txt")
