# DATALINK-14: data.nasdaq.com 의 robots.txt·약관·상품 페이지를 원문 보존용으로 조회한다.
# api.nasdaq.com 은 별도 호스트라 이 스크립트에서 절대 호출하지 않는다.
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

FORBIDDEN_HOST = "api.nasdaq.com"

TARGETS = [
    ("robots", "https://data.nasdaq.com/robots.txt"),
    ("terms", "https://data.nasdaq.com/terms"),
    ("terms_of_use", "https://data.nasdaq.com/terms-of-use"),
    ("tos", "https://data.nasdaq.com/tos"),
    ("privacy", "https://data.nasdaq.com/privacy"),
    ("zacks_ee", "https://data.nasdaq.com/databases/ZACKSE"),
    ("zacks_ee_alt", "https://data.nasdaq.com/databases/ZACKS/EE"),
    ("zacks_eeh_alt", "https://data.nasdaq.com/databases/ZACKS/EEH"),
    ("zacks_vendor", "https://data.nasdaq.com/vendors/ZACKS"),
    ("search_zacks", "https://data.nasdaq.com/search?query=zacks"),
    ("pricing", "https://data.nasdaq.com/pricing"),
    ("home", "https://data.nasdaq.com/"),
]


def main():
    log = []
    for name, url in TARGETS:
        assert FORBIDDEN_HOST not in url, "금지 호스트 호출 시도: %s" % url
        r = fetchlib.get(url, timeout=30)
        line = "%-16s %-5s %-9s %s  %s" % (
            name, r["status"], r["bytes"], r["final_url"], r.get("error") or "")
        print(line)
        log.append(line)
        if r["ok"] and r["bytes"] > 0:
            io.open(os.path.join(RAW, "dl-%s.txt" % name), "w", encoding="utf-8").write(r["text"])
        elif r["text"]:
            io.open(os.path.join(RAW, "dl-%s-err.txt" % name), "w", encoding="utf-8").write(r["text"])
        time.sleep(1.0)
    io.open(os.path.join(HERE, "probe-log.txt"), "w", encoding="utf-8").write(
        "조회 시각 UTC %s\n" % fetchlib.utcnow() + "\n".join(log))


if __name__ == "__main__":
    main()
