# DATALINK-14: robots.txt 가 명시적으로 allow 한 sitemap 으로 실제 상품 페이지 URL 을 찾는다.
# robots.txt 가 disallow 한 /api/*.json*, /api/v3/databases/*/data|codes 는 조회하지 않는다.
import gzip
import io
import os
import re
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "consensus-source-2026-09-09"))
import fetchlib  # noqa: E402
import urllib.request  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw")

DISALLOWED = [
    re.compile(r"/api/.*\.csv"), re.compile(r"/api/.*\.xml"),
    re.compile(r"/api/.*\.xls"), re.compile(r"/api/.*\.json"),
    re.compile(r"/api/v3/databases/[^/]+/data"),
    re.compile(r"/api/v3/databases/[^/]+/codes"),
    re.compile(r"/search/"),
]


def robots_blocked(url):
    return any(p.search(url) for p in DISALLOWED)


def fetch_gz(url):
    req = urllib.request.Request(url, headers={"User-Agent": fetchlib.UA})
    with urllib.request.urlopen(req, timeout=40) as r:
        raw = r.read()
    try:
        return gzip.decompress(raw).decode("utf-8", "replace")
    except Exception:
        return raw.decode("utf-8", "replace")


def main():
    url = "https://data.nasdaq.com/sitemap.xml.gz"
    assert not robots_blocked(url)
    try:
        txt = fetch_gz(url)
    except Exception as e:
        print("sitemap 실패: %s: %s" % (type(e).__name__, e))
        return
    io.open(os.path.join(RAW, "dl-sitemap.xml"), "w", encoding="utf-8").write(txt)
    locs = re.findall(r"<loc>([^<]+)</loc>", txt)
    print("sitemap entries: %d" % len(locs))
    for l in locs[:40]:
        print("  ", l)

    subs = [l for l in locs if l.endswith(".xml") or l.endswith(".gz")]
    zacks = [l for l in locs if "ZACKS" in l.upper() or "zacks" in l.lower()]
    print("\n하위 sitemap %d건, ZACKS 직접 매치 %d건" % (len(subs), len(zacks)))
    for l in zacks[:30]:
        print("   Z:", l)

    found = []
    for s in subs[:12]:
        try:
            t2 = fetch_gz(s)
        except Exception as e:
            print("  하위 실패 %s: %s" % (s, e))
            continue
        l2 = re.findall(r"<loc>([^<]+)</loc>", t2)
        z2 = [x for x in l2 if "zacks" in x.lower()]
        print("  %s -> %d개 (zacks %d)" % (s, len(l2), len(z2)))
        found.extend(z2)
        io.open(os.path.join(RAW, "dl-sitemap-%s" % s.rstrip("/").split("/")[-1].replace(".gz", "")),
                "w", encoding="utf-8").write(t2)
        time.sleep(0.8)
    if found:
        io.open(os.path.join(HERE, "zacks-urls.txt"), "w", encoding="utf-8").write("\n".join(sorted(set(found))))
        print("\nZACKS URL %d건 저장" % len(set(found)))
        for x in sorted(set(found))[:30]:
            print("   ", x)


if __name__ == "__main__":
    main()
