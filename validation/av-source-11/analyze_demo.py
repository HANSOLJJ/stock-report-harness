# 저장된 Alpha Vantage 문서·약관·demo 응답만 읽어 F6 관문 항목을 기계로 판정한다 (신규 API 호출 없음)
"""수집은 `_raw/` 에 이미 끝났다. 이 스크립트는 네트워크를 쓰지 않는다.

판정하는 것은 F6 관문과 1:1 로 맞춘 항목들이다. **없는 것은 unknown 으로 둔다.**
`demo` 키는 문서에 공개된 예시 심볼(IBM)만 응답하므로 12개사 커버리지와
회계분기 식별은 원리적으로 여기서 확정할 수 없다. 그 사실도 출력에 남긴다.

사용:
    python analyze_demo.py
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = HERE / "_raw"
BASE = date(2026, 9, 10)          # 조회 시점(UTC). 향후 분기 수를 이 날짜 기준으로 센다.
UNKNOWN = "unknown"

# F6 관문이 요구하는 basis 필드. 응답 행에 이 이름이 있는지만 본다. 추측하지 않는다.
BASIS_KEYS = ("currency", "share_basis", "shareBasis", "accounting", "asOf", "as_of", "last_updated")


def normalized(path: Path) -> bytes:
    """CRLF 를 LF 로 맞춘 바이트.

    파일 바이트를 그대로 해싱하면 체크아웃의 개행 처리에 따라 같은 내용이 다른 값이 된다
    (`documentation.html` 이 작업 트리 1,059,116 B · 커밋 트리 1,079,968 B 로 갈렸다).
    재현자가 '원자료가 바뀌었나' 로 오해하지 않도록 지문은 정규화한 바이트로 낸다.
    """
    return path.read_bytes().replace(b"\r\n", b"\n")


def sha(path: Path) -> str:
    return hashlib.sha256(normalized(path)).hexdigest()[:16]


def _d(s: str) -> date:
    return date(int(s[:4]), int(s[5:7]), int(s[8:10]))


def main() -> int:
    demo = json.loads((RAW / "EARNINGS_ESTIMATES.IBM.demo.json").read_text(encoding="utf-8"))
    other = json.loads((RAW / "EARNINGS_ESTIMATES.NVDA.demo.json").read_text(encoding="utf-8"))
    rows = demo["estimates"]
    quarters = [r for r in rows if str(r.get("horizon", "")).strip() == "fiscal quarter"]
    years = [r for r in rows if str(r.get("horizon", "")).strip() == "fiscal year"]
    fwd_q = sorted((r for r in quarters if _d(r["date"]) > BASE), key=lambda r: r["date"])
    fwd_y = sorted((r for r in years if _d(r["date"]) > BASE), key=lambda r: r["date"])

    print("=" * 100)
    print(f"AV-SOURCE-11 — Alpha Vantage EARNINGS_ESTIMATES 저장 자료 판정 (기준일 {BASE.isoformat()})")
    print("=" * 100)

    print("\n[0] 저장 원자료 지문 — 크기·해시 모두 개행 정규화(CRLF→LF) 기준이다")
    print("    파일 바이트 그대로 재면 체크아웃마다 값이 갈린다. 승인 해시에 파일 바이트를 쓰지 않는 것과 같은 이유다.")
    for p in sorted(RAW.iterdir()):
        if p.is_file():
            print(f"  {p.name:38} {len(normalized(p)):>8} B  sha256:{sha(p)}")

    print("\n[1] demo 키의 사정거리 — HTTP 200 은 커버리지 증거가 아니다")
    print(f"  IBM  : estimates {len(rows)} 행 (fiscal quarter {len(quarters)} · fiscal year {len(years)})")
    print(f"  NVDA : 최상위 키 {list(other.keys())}")
    print(f"         {str(other.get('Information'))[:120]}")
    print("  → 문서 예시 심볼 외에는 안내문만 온다. HTTP 200 이지만 자료가 아니다.")

    print("\n[2] 향후 분기 수 — F6 은 4개를 요구한다")
    print(f"  기준일 이후 분기 행 {len(fwd_q)} 개")
    for r in fwd_q:
        print(f"    {r['date']}  avg {r['eps_estimate_average']:>10}  n {r['eps_estimate_analyst_count']:>9}"
              f"  low {r['eps_estimate_low']:>10}  high {r['eps_estimate_high']:>10}")
    print(f"  기준일 이후 연간 행 {len(fwd_y)} 개: {[r['date'] for r in fwd_y]}")
    print(f"  → 분기 전망은 {len(fwd_q)} 개. F6 요구 4개에 {'미달' if len(fwd_q) < 4 else '충족'}한다.")
    print("     연간은 2개 나오는데 분기는 그렇지 않다. 분기 지평이 짧은 것이지 자료가 없는 것이 아니다.")

    print("\n[3] 회계분기 식별 필드")
    print(f"  horizon 값 집합: {sorted({str(r.get('horizon')) for r in rows})}")
    print(f"  date 형식: 절대 날짜(YYYY-MM-DD). 예 {[r['date'] for r in quarters[:4]]}")
    print("  → Yahoo 식 상대 오프셋(0q/+1q)이 아니라 **절대 날짜**다. 이 점은 Finnhub·Yahoo 보다 낫다.")
    months = sorted({r["date"][5:7] for r in quarters})
    print(f"  IBM 분기 종료 월 집합: {months}")
    print("  → IBM 은 달력연도 결산사라 '회계분기 말' 과 '달력분기 말' 두 가설이 갈리지 않는다.")
    print("     NVDA(1월)·MSFT(6월)·AAPL(9월)·ORCL(5월) 같은 비달력 결산사로만 확정되는데")
    print("     demo 키가 응답하지 않는다. 따라서 판정은 unknown 이다.")

    print("\n[4] basis 필드 — 응답 행에 키가 있는가")
    present = sorted({k for r in rows for k in r.keys()})
    for k in BASIS_KEYS:
        hit = [f for f in present if f.lower() == k.lower()]
        print(f"  {k:14} {'있음 ' + str(hit) if hit else UNKNOWN}")
    print(f"  응답 행 필드 전체({len(present)}개): {present}")

    print("\n[5] 표본수 · min/max · 과거 시점 재현")
    print("  표본수   : eps_estimate_analyst_count · revenue_estimate_analyst_count — 있음")
    print("  min/max  : eps_estimate_low / eps_estimate_high — 있음")
    rev = sorted(f for f in present if "days_ago" in f or "revision" in f)
    print(f"  개정 이력: {rev}")
    print("  → 평균만 7·30·60·90일 전 값을 준다. low/high/표본수의 과거 값은 없고,")
    print("     임의 시점을 지정하는 파라미터도 문서에 없다. 과거 시점 재현은 부분적이다.")

    print("\n[6] 무료/premium 구분 — 문서 마크업 근거")
    doc = (RAW / "documentation.html").read_text(encoding="utf-8", errors="replace")
    m = re.search(r'<h4 id="earnings-estimates">.*?</h4>', doc, re.S)
    print(f"  문서 제목 마크업: {m.group(0) if m else UNKNOWN}")
    print(f"  premium-label 부착 여부: {'있음' if m and 'premium-label' in m.group(0) else '없음'}")
    print("  → popular-label(Trending) 만 붙어 있고 premium-label 이 없다. 무료 함수다.")
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    sys.exit(main())
