# 저장된 Finnhub 원자료만 읽어 2A+2E 가 연속 회계분기 창을 이루는지 기계 검증한다 (신규 API 호출 없음)
"""`na>=2 / ne>=2` 는 **개수 확인이지 창 검증이 아니다.**

이 스크립트는 12개사 각각에 대해 실제로 선택될 2A(최근 확정 2개)와 2E(다음 전망 2개)를
집어내고, 그 넷이 **중복 없이 연속한 회계분기**를 이루는지 확인한다.

판정을 넷으로 분리한다. 앞 단계를 통과해야 다음 단계를 볼 수 있다.

    raw-availability : 실적 2행·전망 2행이 원자료에 존재하는가
    window-verified  : 그 4행이 중복·누락·역순 없이 연속 회계분기인가
    basis-verified   : 회계기준·통화·주식기준이 **증거로** 확인되는가
    score-ready      : 위 셋을 모두 통과했는가

**unknown 은 추측으로 통과시키지 않는다.** 원자료에 없는 항목은 `unknown` 으로 남긴다.

## period 필드를 회계기간 종료일로 단정하지 않는다

NVDA 의 `stock/earnings` 행에 `period=2026-09-30` 이 있는데 수집 시점(2026-09-09)보다
뒤인데도 `actual` 이 채워져 있다. 회계기간 종료일이라면 성립할 수 없다.

그래서 창 연결에는 `period` 를 쓰지 않고 **회계 라벨 (year, quarter)** 을 쓴다.
`period` 의 의미는 저장된 SEC 근거와 대조해 별도로 판정하고, 확정되지 않으면
`unknown` 으로 둔다.

입력 — 모두 저장 자료다. 네트워크를 쓰지 않는다.
    ./_raw/finnhub/<TICKER>.json                      (커밋됨)
    ../f6h-feasibility-08/_raw/<TICKER>.json          (SEC companyconcept, gitignore·재생성 가능)

사용:
    python verify_window.py
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
FINNHUB = HERE / "_raw" / "finnhub"
SEC = HERE.parent / "f6h-feasibility-08" / "_raw"   # 저장된 SEC 원본(비커밋, 재생성 가능)

TICKERS = ["META", "NVDA", "GOOGL", "MSFT", "AMZN", "AAPL", "ORCL", "PLTR", "TSLA", "SPCX", "TSM", "BABA"]
UNKNOWN = "unknown"


def _d(s: str) -> date:
    return date(int(s[:4]), int(s[5:7]), int(s[8:10]))


def fq_index(year: int, quarter: int) -> int:
    """회계분기 일련번호. 연속성 판정의 유일한 기준이다."""
    return year * 4 + (quarter - 1)


def calendar_quarter_end(d: date) -> date:
    """d 를 포함하는 달력분기의 종료일."""
    q_end_month = ((d.month - 1) // 3 + 1) * 3
    last = {3: 31, 6: 30, 9: 30, 12: 31}[q_end_month]
    return date(d.year, q_end_month, last)


def load_finnhub(ticker: str) -> tuple[list[dict], list[dict], list[str]]:
    """(과거행, 미래행, 파싱 경고). 원문 경로와 배열 인덱스를 함께 붙인다."""
    path = FINNHUB / f"{ticker}.json"
    warn: list[str] = []
    if not path.is_file():
        return [], [], [f"원자료 없음: {path}"]
    rec = json.loads(path.read_text(encoding="utf-8"))
    past, fut = [], []
    try:
        rows = json.loads(rec["past"]["body"])
        for i, r in enumerate(rows if isinstance(rows, list) else []):
            past.append({**r, "_src": f"_raw/finnhub/{ticker}.json:past.body[{i}]"})
    except Exception as e:
        warn.append(f"past 파싱 실패: {type(e).__name__}")
    try:
        rows = json.loads(rec["future"]["body"]).get("earningsCalendar", [])
        for i, r in enumerate(rows):
            fut.append({**r, "_src": f"_raw/finnhub/{ticker}.json:future.body.earningsCalendar[{i}]"})
    except Exception as e:
        warn.append(f"future 파싱 실패: {type(e).__name__}")
    return past, fut, warn


def sec_quarter_ends(ticker: str) -> list[date] | None:
    """SEC XBRL 의 분기(약 90일) 종료일. 없으면 None(=대조 불가)."""
    path = SEC / f"{ticker}.json"
    if not path.is_file():
        return None
    try:
        rows = json.loads(path.read_text(encoding="utf-8"))["units"]["USD/shares"]
    except Exception:
        return None
    ends = set()
    for r in rows:
        s, e = r.get("start"), r.get("end")
        if s and e and 80 <= (_d(e) - _d(s)).days <= 100:
            ends.add(_d(e))
    return sorted(ends) or None


def pick_window(past: list[dict], fut: list[dict]) -> dict:
    """2A 와 2E 를 실제 선택 규칙대로 집는다. 회계 라벨로만 정렬한다."""
    def keyed(rows, need_actual):
        out = []
        for r in rows:
            y, q = r.get("year"), r.get("quarter")
            if not isinstance(y, int) or not isinstance(q, int) or not 1 <= q <= 4:
                continue
            val = r.get("actual") if need_actual else r.get("epsEstimate")
            if val is None:
                continue
            if not need_actual and r.get("epsActual") is not None:
                continue  # 이미 발표된 행은 전망이 아니다
            out.append({"y": y, "q": q, "idx": fq_index(y, q), "val": val, "raw": r})
        return sorted(out, key=lambda x: x["idx"])

    a = keyed(past, True)
    e = keyed(fut, False)
    return {"actual_all": a, "forecast_all": e, "a2": a[-2:], "e2": e[:2]}


def verify(ticker: str) -> dict:
    past, fut, warn = load_finnhub(ticker)
    w = pick_window(past, fut)
    a2, e2 = w["a2"], w["e2"]
    res: dict = {"ticker": ticker, "warnings": list(warn),
                 "n_actual": len(w["actual_all"]), "n_forecast": len(w["forecast_all"]),
                 "a2": a2, "e2": e2, "issues": []}

    # 1) raw-availability
    res["raw_availability"] = len(a2) == 2 and len(e2) == 2
    if not res["raw_availability"]:
        res["issues"].append(f"행 부족(실적 {len(w['actual_all'])}·전망 {len(w['forecast_all'])})")

    # 2) window-verified — 중복·누락·순서
    if res["raw_availability"]:
        idxs = [x["idx"] for x in a2 + e2]
        labels = [f"{x['y']}Q{x['q']}" for x in a2 + e2]
        if len(set(idxs)) != 4:
            res["issues"].append(f"회계분기 중복 {labels}")
        if any(b - a != 1 for a, b in zip(idxs, idxs[1:])):
            res["issues"].append(f"연속하지 않음 {labels}")
        # 전체 실적/전망 목록 자체의 중복도 본다
        for name, rows in (("실적", w["actual_all"]), ("전망", w["forecast_all"])):
            ids = [x["idx"] for x in rows]
            if len(set(ids)) != len(ids):
                res["issues"].append(f"{name} 목록에 중복 회계분기")
        # 두 endpoint 가 같은 회계분기를 각각 실적과 전망으로 내놓으면 창이 겹친다
        overlap = {x["idx"] for x in w["actual_all"]} & {x["idx"] for x in w["forecast_all"]}
        if overlap:
            res["issues"].append(f"endpoint 간 회계분기 중복 {sorted(overlap)}")
        res["window_verified"] = not res["issues"]
        res["window_labels"] = labels
    else:
        res["window_verified"] = False
        res["window_labels"] = [f"{x['y']}Q{x['q']}" for x in a2 + e2]

    # 3) basis-verified — Finnhub 은 기준 필드를 주지 않는다. 추측하지 않는다.
    fields = {}
    sample = (a2 + e2)[0]["raw"] if (a2 + e2) else {}
    for key in ("currency", "share_basis", "accounting", "asOf"):
        fields[key] = sample.get(key, UNKNOWN) if key in sample else UNKNOWN
    res["basis_fields"] = fields
    res["basis_verified"] = all(v not in (UNKNOWN, None) for v in fields.values())

    # 4) score-ready
    res["score_ready"] = bool(res["raw_availability"] and res["window_verified"] and res["basis_verified"])

    # period 의미 대조 — 저장된 SEC 근거가 있을 때만
    ends = sec_quarter_ends(ticker)
    if ends is None:
        res["period_semantics"] = UNKNOWN
        res["period_note"] = "저장된 SEC 분기 근거 없음 — 대조 불가"
    else:
        cal_ends = {calendar_quarter_end(e) for e in ends}
        periods = {_d(r["period"]) for r in past if r.get("period")}
        overlap = [p for p in periods if p in cal_ends]
        exact = [p for p in periods if p in set(ends)]
        res["period_semantics"] = {
            "finnhub_period_수": len(periods),
            "SEC_회계종료일과_일치": len(exact),
            "SEC_회계종료일의_달력분기말과_일치": len(overlap),
        }
        res["period_note"] = ("period 가 회계종료일 자체와는 다르고 그 종료일이 속한 달력분기 말과 맞는다"
                              if len(overlap) > len(exact) else
                              "판정 보류 — 두 가설이 갈리지 않는다")
    return res


def main() -> None:
    meta = json.loads((HERE / "_raw" / "meta.json").read_text(encoding="utf-8"))
    collected = meta["collected_at_utc"]
    print("=" * 118)
    print(f"F6-H 창 검증 — Finnhub 저장 원자료만 사용 (수집 시점 UTC {collected}, 신규 호출 없음)")
    print("=" * 118)

    results = [verify(t) for t in TICKERS]

    print()
    print("[1] 선택된 2A / 2E 와 창 판정")
    print(f"{'티커':6} {'2A':>17} {'2E':>17} {'raw':>5} {'window':>7} {'basis':>7} {'score':>7}  문제")
    for r in results:
        a = " ".join(f"{x['y']}Q{x['q']}" for x in r["a2"]) or "-"
        e = " ".join(f"{x['y']}Q{x['q']}" for x in r["e2"]) or "-"
        print(f"{r['ticker']:6} {a:>17} {e:>17} "
              f"{'O' if r['raw_availability'] else 'X':>5} {'O' if r['window_verified'] else 'X':>7} "
              f"{'O' if r['basis_verified'] else 'X':>7} {'O' if r['score_ready'] else 'X':>7}  "
              f"{'; '.join(r['issues'] + r['warnings'])}")

    print()
    print("[2] 선택 행의 원문 경로·라벨·period·발표일·값")
    print(f"{'티커':6} {'구분':4} {'회계라벨':>9} {'period':>12} {'발표일':>12} {'값':>9}  원문 경로")
    for r in results:
        for tag, rows, is_a in (("2A", r["a2"], True), ("2E", r["e2"], False)):
            for x in rows:
                raw = x["raw"]
                # 필드가 아예 없는 것과 값이 비어 있는 것을 구분한다. 없으면 unknown 이다.
                per = raw.get("period") if "period" in raw else UNKNOWN
                dt = raw.get("date") if "date" in raw else UNKNOWN
                print(f"{r['ticker']:6} {tag:4} {x['y']}Q{x['q']:<7} {per:>12} {dt:>12} {x['val']:>9} "
                      f" {raw['_src']}")

    print()
    print("[3] period 필드 의미 — 저장된 SEC 근거와 대조")
    print(f"{'티커':6} {'period수':>9} {'SEC회계종료일과 일치':>20} {'달력분기말과 일치':>18}  판정")
    for r in results:
        ps = r["period_semantics"]
        if ps == UNKNOWN:
            print(f"{r['ticker']:6} {'-':>9} {'-':>20} {'-':>18}  unknown — {r['period_note']}")
        else:
            print(f"{r['ticker']:6} {ps['finnhub_period_수']:>9} {ps['SEC_회계종료일과_일치']:>20} "
                  f"{ps['SEC_회계종료일의_달력분기말과_일치']:>18}  {r['period_note']}")

    print()
    print("[4] basis 필드 — Finnhub 응답에 존재하는가")
    print(f"{'티커':6} {'currency':>10} {'share_basis':>12} {'accounting':>11} {'asOf':>8}")
    for r in results:
        f = r["basis_fields"]
        print(f"{r['ticker']:6} {f['currency']:>10} {f['share_basis']:>12} {f['accounting']:>11} {f['asOf']:>8}")

    print()
    print("=" * 118)
    n = len(results)
    for key, label in (("raw_availability", "raw-availability"), ("window_verified", "window-verified"),
                       ("basis_verified", "basis-verified"), ("score_ready", "score-ready")):
        ok = sum(1 for r in results if r[key])
        print(f"  {label:18} {ok}/{n}")
    print("=" * 118)


if __name__ == "__main__":
    main()
