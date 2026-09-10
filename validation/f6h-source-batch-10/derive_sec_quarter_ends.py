# 저장된 SEC XBRL 원본에서 분기 종료일만 뽑아 커밋 가능한 작은 근거 파일로 남긴다 (신규 API 호출 없음)
"""`verify_window.py` 3절(period 의미 대조)의 근거를 저장소 안에 둔다.

R1 재검토 W5. `_raw/sec/<TICKER>.json` 은 커밋돼 있으나 본문이 `"(본문 생략 — 크기)"` 인
stub 이고, 검증기가 읽던 `../f6h-feasibility-08/_raw/` 는 비커밋이다. 그래서 커밋 트리만으로
3절이 재현되지 않았다.

대조에 필요한 것은 **분기(약 90일) 종료일 목록뿐**이므로 그것만 파생해 커밋한다.
원자료는 고치지 않는다. 이 스크립트는 읽기만 한다.

사용:
    python derive_sec_quarter_ends.py     # _derived/sec_quarter_ends.json 생성
"""
from __future__ import annotations

import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE.parent / "f6h-feasibility-08" / "_raw"      # 비커밋·재생성 가능
OUT = HERE / "_derived" / "sec_quarter_ends.json"

TICKERS = ["META", "NVDA", "GOOGL", "MSFT", "AMZN", "AAPL", "ORCL", "PLTR", "TSLA", "SPCX", "TSM", "BABA"]


def _d(s: str) -> date:
    return date(int(s[:4]), int(s[5:7]), int(s[8:10]))


def quarter_ends(path: Path) -> list[str] | None:
    try:
        rows = json.loads(path.read_text(encoding="utf-8"))["units"]["USD/shares"]
    except Exception:
        return None
    ends = set()
    for r in rows:
        s, e = r.get("start"), r.get("end")
        if s and e and 80 <= (_d(e) - _d(s)).days <= 100:
            ends.add(e)
    return sorted(ends) or None


def main() -> int:
    out: dict = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source": "SEC XBRL companyconcept — validation/f6h-feasibility-08/_raw/<TICKER>.json (비커밋·재생성 가능)",
        "rule": "units['USD/shares'] 중 start~end 간격이 80~100일인 행의 end 를 분기 종료일로 본다",
        "note": "원자료를 요약한 파생물이다. 값 자체(EPS)는 담지 않는다.",
        "quarter_ends": {},
        "missing": [],
    }
    for t in TICKERS:
        ends = quarter_ends(SRC / f"{t}.json")
        if ends is None:
            out["missing"].append(t)
        else:
            out["quarter_ends"][t] = ends
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"저장 {OUT}")
    print(f"  종료일 확보 {len(out['quarter_ends'])}개사 · 근거 없음 {out['missing']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
