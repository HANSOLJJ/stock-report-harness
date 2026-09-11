# SRC-POLICY-32: Finnhub robots.txt 와 이용약관을 조회해 보존한다.
# PRIV-ARR-17 표준 — robots.txt 와 약관·정책 문서는 확인 목적으로 조회할 수 있다.
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "consensus-source-2026-09-09"))
from fetchlib import get  # noqa: E402

RAW = os.path.join(HERE, "raw")
TARGETS = [
    ("finnhub-robots.txt", "https://finnhub.io/robots.txt"),
    ("finnhub-terms-of-service.html", "https://finnhub.io/terms-of-service"),
    ("finnhub-privacy-policy.html", "https://finnhub.io/privacy-policy"),
]

meta = []
for name, url in TARGETS:
    r = get(url)
    ok = bool(r.get("ok")) and r.get("status") == 200
    body = r.get("text") or ""
    if body:
        io.open(os.path.join(RAW, name), "w", encoding="utf-8").write(body)
    meta.append({"file": name, "url": url, "status": r.get("status"),
                 "final_url": r.get("final_url"), "bytes": r.get("bytes"),
                 "ctype": r.get("ctype"), "error": r.get("error"),
                 "accessed_at": "2026-09-11", "saved": bool(body)})
    print("%-36s status=%-5s bytes=%-8s %s" % (name, r.get("status"), r.get("bytes"),
                                               "저장" if body else "본문 없음"))

io.open(os.path.join(HERE, "fetch-meta.json"), "w", encoding="utf-8").write(
    json.dumps({"accessed_at": "2026-09-11",
                "standard": "PRIV-ARR-17 — robots.txt 와 약관·정책 문서는 확인 목적 조회 허용",
                "items": meta}, ensure_ascii=False, indent=1))
print("\nsaved fetch-meta.json")
