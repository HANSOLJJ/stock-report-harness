"""QWEN-NTM-DATA-03 수집기 연결성 점검: 공개 페이지 1건을 직접 받아 파싱 가능한지 확인한다.

worker·원본·C-13 은 건드리지 않는다. 이 스크립트는 자기 폴더에만 기록한다.
유료 가입·구매·계정 변경 없이 공개 페이지의 GET 만 수행한다.
"""
import sys
import time
import urllib.request

URL = "https://stockanalysis.com/stocks/meta/forecast/"
HDRS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/126.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "en-US,en;q=0.9",
}


def get(url, timeout=30):
    req = urllib.request.Request(url, headers=HDRS)
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=timeout) as r:
        body = r.read()
        return dict(status=r.status, final_url=r.geturl(),
                    ctype=r.headers.get("Content-Type"),
                    bytes=len(body), elapsed=round(time.time() - t0, 2),
                    text=body.decode("utf-8", "replace"))


if __name__ == "__main__":
    try:
        r = get(URL)
    except Exception as exc:
        print("FETCH FAILED: %s: %s" % (type(exc).__name__, exc))
        sys.exit(1)
    print("status=%s  bytes=%d  ctype=%s  elapsed=%ss" % (r["status"], r["bytes"], r["ctype"], r["elapsed"]))
    print("final_url=%s" % r["final_url"])
    t = r["text"]
    for probe in ["Forward PE", "non-GAAP", "EPS This Year", "EPS Next Year", "FY 2026",
                  "FY 2027", "Upgrade", "Pro", "Last updated", "Quarterly", "Annual"]:
        print("  %-16s in page: %s" % (probe, probe in t))
