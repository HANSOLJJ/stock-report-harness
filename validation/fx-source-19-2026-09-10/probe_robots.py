# FX-SOURCE-19 1단계: 후보 host 의 robots.txt 만 먼저 조회한다.
# PRIV-ARR-17 표준 — robots.txt 와 약관·정책 문서는 확인 목적으로 조회 가능,
# 그 외 내용 페이지는 약관 확인 뒤에만. 이 단계에서는 robots.txt 만 본다.
import io
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "consensus-source-2026-09-09"))
import fetchlib  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw")
os.makedirs(RAW, exist_ok=True)

HOSTS = [
    # 이미 allowed 인 둘 — 새 등재 없이 해결되는지 먼저 본다
    ("finnhub.io", "https://finnhub.io/robots.txt"),
    ("financialmodelingprep.com", "https://financialmodelingprep.com/robots.txt"),
    # 공적 기관 후보
    ("federalreserve.gov", "https://www.federalreserve.gov/robots.txt"),
    ("fred.stlouisfed.org", "https://fred.stlouisfed.org/robots.txt"),
    ("bis.org", "https://www.bis.org/robots.txt"),
    ("cbc.gov.tw", "https://www.cbc.gov.tw/robots.txt"),
    ("safe.gov.cn", "https://www.safe.gov.cn/robots.txt"),
    ("chinamoney.com.cn", "https://www.chinamoney.com.cn/robots.txt"),
    # 민간 무료 API 후보
    ("exchangerate.host", "https://exchangerate.host/robots.txt"),
    ("frankfurter.dev", "https://frankfurter.dev/robots.txt"),
    ("open.er-api.com", "https://open.er-api.com/robots.txt"),
]

log = []
for name, url in HOSTS:
    r = fetchlib.get(url, timeout=40)
    line = "%-28s %-5s %-7s %s" % (name, r["status"], r["bytes"], r.get("error") or "")
    print(line)
    log.append("== %s  (%s)\n   status=%s bytes=%s %s" % (
        name, url, r["status"], r["bytes"], r.get("error") or ""))
    if r["ok"] and r["text"]:
        io.open(os.path.join(RAW, "robots-%s.txt" % name), "w", encoding="utf-8").write(r["text"])
        body = r["text"]
        print("      " + "\n      ".join(body.strip().splitlines()[:14]))
        log.append("---- 본문 ----\n" + body.strip()[:2500])
    elif r["text"]:
        io.open(os.path.join(RAW, "robots-%s-err.txt" % name), "w",
                encoding="utf-8").write(r["text"])
    log.append("")
    time.sleep(1.0)

io.open(os.path.join(HERE, "robots-log.txt"), "w", encoding="utf-8").write(
    "조회 시각 UTC %s\n\n" % fetchlib.utcnow() + "\n".join(log))
print("\nsaved robots-log.txt")
