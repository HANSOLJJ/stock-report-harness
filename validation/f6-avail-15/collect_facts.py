# SEC companyfacts 를 12개 상장사에 대해 한 번씩 받아 저장한다 (값 판단은 하지 않고 저장만)
"""F6-AVAIL-15 의 수집 단계다. **판정은 `inventory.py` 가 한다.**

이 스크립트는 두 가지만 한다.

    1. `www.sec.gov/files/company_tickers.json` 으로 티커→CIK 를 해석한다. CIK 를 손으로 적지 않는다.
    2. 각 사 `data.sec.gov/api/xbrl/companyfacts/CIK##########.json` 을 받아 `_raw/` 에 저장한다.

## 왜 companyfacts 인가

과제가 "보유 태그 인벤토리" 를 요구한다. `companyconcept` 은 태그를 하나씩 찍어 보는 것이라
**후보 목록에 없는 개념을 놓친다.** 회사마다 쓰는 매출 개념이 다르다는 것이 확인 항목 1 이므로
전체 태그를 봐야 한다.

## 응답 본문은 커밋하지 않는다

`companyfacts` 는 요청 하나가 그 회사의 모든 태그와 값을 통째로 돌려준다. 과제 조건인
"값을 대량 수집하지 말 것" 과 형식상 부딪히므로 **저장소에는 파생 인벤토리만 남긴다.**
`_raw/` 는 `.gitignore` 로 막혀 있다.

## SEC 접근 조건

`data.sec.gov` 는 v1.6 allowed 이나 조건이 붙어 있다 — User-Agent 표기와 요청 한도다.
User-Agent 는 `SEC_UA` 환경변수를 쓰고, 없으면 이 저장소의 커밋 연락처로 채운다.
요청 간격은 SEC 권고(10 req/s)보다 훨씬 느린 1 초로 둔다. 총 13 회다.

사용:
    export SEC_UA="your-app your@email"      # 선택. 없으면 저장소 커밋 연락처를 쓴다
    python collect_facts.py
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = HERE / "_raw"

TICKERS = ["META", "NVDA", "GOOGL", "MSFT", "AMZN", "AAPL", "ORCL", "PLTR", "TSLA", "SPCX", "TSM", "BABA"]
SLEEP_SEC = 1.0                      # SEC 권고 한도(10 req/s)보다 크게 느리게 둔다
UA = os.environ.get("SEC_UA") or "stock-report-harness F6-AVAIL-15 (contact: hansol.jung@digitalcoms.net)"


def get(url: str, timeout: int = 60) -> tuple[int, bytes]:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Encoding": "gzip, deflate"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read()
            if r.headers.get("Content-Encoding") == "gzip":
                import gzip
                body = gzip.decompress(body)
            return r.status, body
    except urllib.error.HTTPError as e:
        return e.code, e.read()[:500]
    except Exception as e:
        return 0, f"{type(e).__name__}: {e}".encode()


def resolve_ciks() -> dict[str, int]:
    """티커→CIK. 손으로 적지 않고 SEC 목록에서 해석한다."""
    status, body = get("https://www.sec.gov/files/company_tickers.json")
    if status != 200:
        raise SystemExit(f"company_tickers.json 실패: HTTP {status} {body[:200]!r}")
    (RAW / "company_tickers.json").write_bytes(body)
    table = json.loads(body)
    by_ticker = {row["ticker"].upper(): (int(row["cik_str"]), row["title"]) for row in table.values()}
    out, missing = {}, []
    for t in TICKERS:
        if t in by_ticker:
            out[t] = by_ticker[t]
        else:
            missing.append(t)
    if missing:
        print(f"  [경고] SEC 티커 목록에 없음: {missing}")
    return out


def main() -> int:
    RAW.mkdir(parents=True, exist_ok=True)
    started = datetime.now(timezone.utc).isoformat()
    print(f"조회 시점(UTC) {started}")
    print(f"User-Agent: {UA}")
    print(f"요청 간격 {SLEEP_SEC}s · 총 {len(TICKERS) + 1} 회")

    print("\n[1] 티커 → CIK 해석")
    ciks = resolve_ciks()
    for t, (cik, title) in ciks.items():
        print(f"  {t:6} CIK {cik:>10}  {title}")
    time.sleep(SLEEP_SEC)

    print("\n[2] companyfacts 수집")
    meta = {"collected_at_utc": started, "user_agent": UA, "tickers": TICKERS,
            "ciks": {t: v[0] for t, v in ciks.items()},
            "titles": {t: v[1] for t, v in ciks.items()},
            "not_in_sec_ticker_list": [t for t in TICKERS if t not in ciks],
            "http": {}}
    for t in TICKERS:
        if t not in ciks:
            meta["http"][t] = "cik_unresolved"
            print(f"  {t:6} CIK 미해석 — 건너뜀")
            continue
        cik = ciks[t][0]
        status, body = get(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json")
        meta["http"][t] = status
        if status == 200:
            (RAW / f"{t}.companyfacts.json").write_bytes(body)
            print(f"  {t:6} HTTP 200  {len(body):>10,} B 저장")
        else:
            (RAW / f"{t}.error.txt").write_bytes(body)
            print(f"  {t:6} HTTP {status}  {body[:120]!r}")
        time.sleep(SLEEP_SEC)

    meta["finished_at_utc"] = datetime.now(timezone.utc).isoformat()
    (RAW / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n완료 — _raw/meta.json 에 조회 시점·CIK·응답 코드 기록")
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    sys.exit(main())
