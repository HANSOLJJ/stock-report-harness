# 저장된 Finnhub 원자료만 읽어 2A+2E 가 분석 기준일에 맞는 연속 회계분기 창인지 기계 검증한다 (신규 API 호출 없음)
"""`na>=2 / ne>=2` 는 **개수 확인이지 창 검증이 아니다.**

이 스크립트는 12개사 각각에 대해 실제로 선택될 2A(최근 확정 2개)와 2E(다음 전망 2개)를
집어내고, 그 넷이 중복 없이 연속한 회계분기인지, 그리고 **분석 기준일 기준으로** 실적과
전망의 자리가 맞는지 확인한다.

판정을 다섯으로 분리한다. 앞 단계를 통과해야 다음 단계를 볼 수 있다.

    raw-availability : 실적 2행·전망 2행이 원자료에 존재하고 값이 유한수인가
    label-continuity : 그 4행이 중복·누락·역순 없이 연속 회계분기인가
    asof-anchored    : 2E 가 기준일 이후 발표 예정이고 기준일 이전 발표분이 섞이지 않았는가
    basis-verified   : 회계기준·통화·주식기준이 **창 4행 전부에서** 일치 증거로 확인되는가
    score-ready      : 위 넷을 모두 통과했는가

**unknown 은 추측으로 통과시키지 않는다.** 원자료에 없는 항목은 `unknown` 으로 남긴다.

## R1 재검토(설계진행 9d06eec) 반영

W1. 이전 `window-verified` 는 회계 라벨의 내부 연속성만 봤고 날짜를 전혀 쓰지 않았다.
    이름을 `label-continuity` 로 바꾸고, 기준일 고정을 `asof-anchored` 로 분리해 추가했다.
W2. basis 를 창 첫 행 하나로 판정하던 것을 4행 전부에서 읽도록 고쳤다. 행 간 값이 어긋나면
    통과가 아니라 conflict 다. 2A·2E 두 endpoint 간 일치 여부도 따로 출력한다.
W3. 값이 필드로 존재하는 것과 계산 가능한 유한수인 것을 구분한다. 문자열·NaN·inf 는 실격이다.
    **음수 EPS 자체는 결측이 아니다**(SPCX -0.09 는 정상 값).
W4. 창 4행 값의 자릿수 정합과 surprise 부호 쏠림을 **표시 항목**으로 낸다. 판정에는 쓰지 않고
    원인도 단정하지 않는다.
W5. 3절 근거를 커밋된 `_derived/sec_quarter_ends.json` 에서 읽는다. 없으면 비커밋 원본으로
    떨어지되 근거 출처를 출력에 찍는다.
W6. 출력 인코딩을 코드에서 UTF-8 로 고정한다.

## period 필드를 회계기간 종료일로 단정하지 않는다

NVDA 의 `stock/earnings` 행에 `period=2026-09-30` 이 있는데 수집 시점(2026-09-09)보다
뒤인데도 `actual` 이 채워져 있다. 회계기간 종료일이라면 성립할 수 없다.

그래서 창 연결에는 `period` 를 쓰지 않고 **회계 라벨 (year, quarter)** 을 쓴다.
`period` 의 의미는 저장된 SEC 근거와 대조해 별도로 판정하고, 확정되지 않으면 `unknown` 으로 둔다.

입력 — 모두 저장 자료다. 네트워크를 쓰지 않는다.
    ./_raw/finnhub/<TICKER>.json                      (커밋됨)
    ./_derived/sec_quarter_ends.json                  (커밋됨 · derive_sec_quarter_ends.py 산출)
    ../f6h-feasibility-08/_raw/<TICKER>.json          (비커밋 대체 경로)

사용:
    python verify_window.py
"""
from __future__ import annotations

import json
import math
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
FINNHUB = HERE / "_raw" / "finnhub"
SEC_DERIVED = HERE / "_derived" / "sec_quarter_ends.json"     # 커밋된 근거
SEC_RAW = HERE.parent / "f6h-feasibility-08" / "_raw"         # 비커밋 원본(대체)

TICKERS = ["META", "NVDA", "GOOGL", "MSFT", "AMZN", "AAPL", "ORCL", "PLTR", "TSLA", "SPCX", "TSM", "BABA"]
BASIS_KEYS = ("currency", "share_basis", "accounting", "asOf")
UNKNOWN = "unknown"
MAGNITUDE_FLAG = 10.0   # 창 4행 값의 최대/최소 배수가 이 이상이면 표시한다(판정 아님)


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


def is_finite_number(v: object) -> bool:
    """계산 가능한 유한수인가. 음수는 정상이고 bool 은 수가 아니다."""
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)


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


def sec_quarter_ends(ticker: str) -> tuple[list[date] | None, str]:
    """(분기 종료일, 근거 출처). 커밋된 파생 파일을 먼저 보고 없으면 비커밋 원본으로 떨어진다."""
    if SEC_DERIVED.is_file():
        try:
            rec = json.loads(SEC_DERIVED.read_text(encoding="utf-8"))
            ends = rec.get("quarter_ends", {}).get(ticker)
            if ends:
                return [_d(s) for s in ends], "_derived(커밋)"
            return None, "_derived(커밋) 에 해당 종목 근거 없음"
        except Exception:
            pass
    path = SEC_RAW / f"{ticker}.json"
    if not path.is_file():
        return None, "근거 부재 - 커밋된 파생 파일도 비커밋 SEC 원본도 없음"
    try:
        rows = json.loads(path.read_text(encoding="utf-8"))["units"]["USD/shares"]
    except Exception:
        return None, "비커밋 SEC 원본 파싱 실패"
    ends = set()
    for r in rows:
        s, e = r.get("start"), r.get("end")
        if s and e and 80 <= (_d(e) - _d(s)).days <= 100:
            ends.add(_d(e))
    return (sorted(ends) or None), "비커밋 원본"


def pick_window(past: list[dict], fut: list[dict]) -> dict:
    """2A 와 2E 를 실제 선택 규칙대로 집는다. 회계 라벨로만 정렬한다.

    값이 **필드로 존재하되 유한수가 아닌** 행은 버리지 않고 ok=False 로 자리를 지킨다.
    버리면 뒤 분기가 조용히 올라와 창이 어긋난 채 통과하기 때문이다(W3).
    """
    def keyed(rows, need_actual):
        out = []
        for r in rows:
            y, q = r.get("year"), r.get("quarter")
            if not isinstance(y, int) or isinstance(y, bool):
                continue
            if not isinstance(q, int) or isinstance(q, bool) or not 1 <= q <= 4:
                continue
            key = "actual" if need_actual else "epsEstimate"
            if key not in r or r[key] is None:
                continue                      # 값 자체가 없다 - 결측이라 자리도 없다
            if not need_actual and r.get("epsActual") is not None:
                continue                      # 이미 발표된 행은 전망이 아니다
            val = r[key]
            out.append({"y": y, "q": q, "idx": fq_index(y, q), "val": val,
                        "ok": is_finite_number(val), "raw": r})
        return sorted(out, key=lambda x: x["idx"])

    a = keyed(past, True)
    e = keyed(fut, False)
    return {"actual_all": a, "forecast_all": e, "a2": a[-2:], "e2": e[:2]}


def basis_scan(a2: list[dict], e2: list[dict]) -> tuple[dict, dict, list[str]]:
    """창 4행 **전부**에서 기준 필드를 읽는다(W2).

    반환 — (필드별 상태, 2A·2E 사이 일치 상태, 문제 목록).
    한 행만 채워져 있으면 통과가 아니라 partial 이고, 행 간 값이 어긋나면 conflict 다.
    """
    rows = a2 + e2
    fields: dict[str, str] = {}
    cross: dict[str, str] = {}
    issues: list[str] = []

    def values(group, key):
        return [g["raw"][key] for g in group if key in g["raw"] and g["raw"][key] is not None]

    for k in BASIS_KEYS:
        present = values(rows, k)
        if not present:
            fields[k] = UNKNOWN
        elif len(present) < len(rows):
            fields[k] = f"partial{len(present)}/{len(rows)}"
            issues.append(f"{k} 가 창 {len(present)}/{len(rows)} 행에만 있음")
        else:
            uniq = sorted({str(v) for v in present})
            if len(uniq) == 1:
                fields[k] = uniq[0]
            else:
                fields[k] = "conflict:" + "|".join(uniq)
                issues.append(f"{k} 행 간 불일치 {uniq}")
        va = sorted({str(v) for v in values(a2, k)})
        ve = sorted({str(v) for v in values(e2, k)})
        if not va and not ve:
            cross[k] = UNKNOWN
        elif not va or not ve:
            cross[k] = "one-side"
        elif va == ve:
            cross[k] = "match"
        else:
            cross[k] = "conflict"
            issues.append(f"{k} 가 2A({va})와 2E({ve}) 사이에서 불일치")
    return fields, cross, issues


def magnitude_signal(rows: list[dict], actual_all: list[dict]) -> dict:
    """창 4행 값의 자릿수 정합과 surprise 부호 쏠림. **표시 항목이고 판정에 쓰지 않는다**(W4)."""
    vals = [abs(x["val"]) for x in rows if x["ok"] and x["val"] != 0]
    ratio = (max(vals) / min(vals)) if len(vals) >= 2 else None
    sp = [r["raw"].get("surprisePercent") for r in actual_all]
    sp = [v for v in sp if is_finite_number(v)]
    skew = None
    if len(sp) >= 3 and (all(v > 0 for v in sp) or all(v < 0 for v in sp)):
        sign = "+" if sp[0] > 0 else "-"
        skew = f"{sign} {len(sp)}/{len(sp)} · |평균| {sum(abs(v) for v in sp) / len(sp):.1f}%"
    return {"ratio": ratio,
            "flagged": bool(ratio is not None and ratio >= MAGNITUDE_FLAG),
            "surprise_skew": skew,
            "surprise_values": sp}


def verify_rows(ticker: str, past: list[dict], fut: list[dict], base: date,
                warn: list[str] | None = None) -> dict:
    """저장 자료가 아니라 넘겨받은 행으로 판정한다. 재현 테스트가 이 진입점을 쓴다."""
    w = pick_window(past, fut)
    a2, e2 = w["a2"], w["e2"]
    res: dict = {"ticker": ticker, "warnings": list(warn or []), "base_date": base.isoformat(),
                 "n_actual": len(w["actual_all"]), "n_forecast": len(w["forecast_all"]),
                 "a2": a2, "e2": e2, "issues": [], "asof_issues": [], "basis_issues": []}

    # 1) raw-availability - 행이 있고 값이 유한수인가(W3)
    bad = [x for x in a2 + e2 if not x["ok"]]
    res["numeric_ok"] = not bad
    for x in bad:
        # _src 는 load_finnhub 이 붙인다. 테스트가 직접 만든 행에는 없을 수 있어 죽지 않게 둔다.
        res["issues"].append(f"{x['y']}Q{x['q']} 값이 수가 아님({x['val']!r}) {x['raw'].get('_src', '?')}")
    res["raw_availability"] = len(a2) == 2 and len(e2) == 2 and res["numeric_ok"]
    if len(a2) != 2 or len(e2) != 2:
        res["issues"].append(f"행 부족(실적 {len(w['actual_all'])}·전망 {len(w['forecast_all'])})")

    res["window_labels"] = [f"{x['y']}Q{x['q']}" for x in a2 + e2]

    # 2) label-continuity - 중복·누락·순서. 날짜를 쓰지 않는다.
    cont: list[str] = []
    if res["raw_availability"]:
        idxs = [x["idx"] for x in a2 + e2]
        labels = res["window_labels"]
        if len(set(idxs)) != 4:
            cont.append(f"회계분기 중복 {labels}")
        if any(b - a != 1 for a, b in zip(idxs, idxs[1:])):
            cont.append(f"연속하지 않음 {labels}")
        for name, rows in (("실적", w["actual_all"]), ("전망", w["forecast_all"])):
            ids = [x["idx"] for x in rows]
            if len(set(ids)) != len(ids):
                cont.append(f"{name} 목록에 중복 회계분기")
        overlap = {x["idx"] for x in w["actual_all"]} & {x["idx"] for x in w["forecast_all"]}
        if overlap:
            cont.append(f"endpoint 간 회계분기 중복 {sorted(overlap)}")
    res["issues"].extend(cont)
    res["label_continuity"] = bool(res["raw_availability"] and not cont)

    # 3) asof-anchored - 기준일에 고정한다(W1)
    if res["raw_availability"]:
        for x in e2:
            raw = x["raw"]
            if "date" not in raw or raw["date"] is None:
                res["asof_issues"].append(f"2E {x['y']}Q{x['q']} 발표 예정일 없음 - 기준일 대조 불가")
                continue
            try:
                dt = _d(str(raw["date"]))
            except Exception:
                res["asof_issues"].append(f"2E {x['y']}Q{x['q']} 발표일 파싱 불가({raw['date']!r})")
                continue
            if dt <= base:
                res["asof_issues"].append(
                    f"2E {x['y']}Q{x['q']} 발표일 {dt.isoformat()} 이 기준일 {base.isoformat()} 이후가 아님")
        # 전망 목록에 기준일 전 이미 발표된 행이 2A 보다 뒤 분기로 남아 있으면
        # 2A 가 '최근 확정 2개'라는 전제가 깨진다.
        newest_a = max((x["idx"] for x in w["actual_all"]), default=None)
        for r in fut:
            y, q, dt = r.get("year"), r.get("quarter"), r.get("date")
            if not isinstance(y, int) or not isinstance(q, int) or not dt:
                continue
            try:
                d = _d(str(dt))
            except Exception:
                continue
            if r.get("epsActual") is not None and d <= base and newest_a is not None \
                    and fq_index(y, q) > newest_a:
                res["asof_issues"].append(f"{y}Q{q} 는 기준일 전 발표됐는데 실적 목록에 없음")
        res["asof_anchored"] = not res["asof_issues"]
    else:
        res["asof_anchored"] = False

    # 4) basis-verified - 창 4행 전부(W2). Finnhub 은 기준 필드를 주지 않는다. 추측하지 않는다.
    fields, cross, bissues = basis_scan(a2, e2)
    res["basis_fields"] = fields
    res["basis_cross_endpoint"] = cross
    res["basis_issues"] = bissues
    res["basis_verified"] = bool(
        len(a2) == 2 and len(e2) == 2 and not bissues
        and all(v != UNKNOWN and not v.startswith(("partial", "conflict")) for v in fields.values()))

    # 5) score-ready
    res["score_ready"] = bool(res["raw_availability"] and res["label_continuity"]
                              and res["asof_anchored"] and res["basis_verified"])

    # 표시 항목 - 판정에 쓰지 않는다(W4)
    res["magnitude"] = magnitude_signal(a2 + e2, w["actual_all"])

    # period 의미 대조 - 저장된 근거가 있을 때만
    ends, provenance = sec_quarter_ends(ticker)
    res["period_evidence"] = provenance
    if ends is None:
        res["period_semantics"] = UNKNOWN
        res["period_note"] = f"대조 불가 - {provenance}"
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
                              "판정 보류 - 두 가설이 갈리지 않는다")
    return res


def verify(ticker: str, base: date) -> dict:
    past, fut, warn = load_finnhub(ticker)
    return verify_rows(ticker, past, fut, base, warn)


def main() -> None:
    meta = json.loads((HERE / "_raw" / "meta.json").read_text(encoding="utf-8"))
    collected = meta["collected_at_utc"]
    base = _d(collected)          # 분석 기준일 = 원자료 수집일(UTC). 판정에 실제로 쓴다.
    evid = "커밋된 _derived/sec_quarter_ends.json" if SEC_DERIVED.is_file() else "부재 - 3절 근거 없음"
    print("=" * 118)
    print(f"F6-H 창 검증 - Finnhub 저장 원자료만 사용 (분석 기준일 UTC {base.isoformat()}, 신규 호출 없음)")
    print(f"  수집 시각 {collected} · 3절 SEC 근거 {evid}")
    print("=" * 118)

    results = [verify(t, base) for t in TICKERS]

    print()
    print("[1] 선택된 2A / 2E 와 창 판정")
    print(f"{'티커':6} {'2A':>17} {'2E':>17} {'raw':>5} {'label':>6} {'asof':>5} {'basis':>6} {'score':>6}  문제")
    for r in results:
        a = " ".join(f"{x['y']}Q{x['q']}" for x in r["a2"]) or "-"
        e = " ".join(f"{x['y']}Q{x['q']}" for x in r["e2"]) or "-"
        problems = r["issues"] + r["asof_issues"] + r["basis_issues"] + r["warnings"]
        print(f"{r['ticker']:6} {a:>17} {e:>17} "
              f"{'O' if r['raw_availability'] else 'X':>5} {'O' if r['label_continuity'] else 'X':>6} "
              f"{'O' if r['asof_anchored'] else 'X':>5} {'O' if r['basis_verified'] else 'X':>6} "
              f"{'O' if r['score_ready'] else 'X':>6}  {'; '.join(problems)}")
    print("  label = 회계 라벨 연속성(날짜 미사용) · asof = 분석 기준일 고정 검사")

    print()
    print("[2] 선택 행의 원문 경로·라벨·period·발표일·값")
    print(f"{'티커':6} {'구분':4} {'회계라벨':>9} {'period':>12} {'발표일':>12} {'값':>9}  원문 경로")
    for r in results:
        for tag, rows in (("2A", r["a2"]), ("2E", r["e2"])):
            for x in rows:
                raw = x["raw"]
                # 필드가 아예 없는 것과 값이 비어 있는 것을 구분한다. 없으면 unknown 이다.
                per = raw.get("period") if "period" in raw else UNKNOWN
                dt = raw.get("date") if "date" in raw else UNKNOWN
                print(f"{r['ticker']:6} {tag:4} {x['y']}Q{x['q']:<7} {str(per):>12} {str(dt):>12} "
                      f"{str(x['val']):>9}  {raw.get('_src', '?')}")

    print()
    print("[3] period 필드 의미 - 저장된 SEC 근거와 대조")
    print(f"{'티커':6} {'period수':>9} {'SEC회계종료일과 일치':>20} {'달력분기말과 일치':>18}  근거 / 판정")
    for r in results:
        ps = r["period_semantics"]
        if ps == UNKNOWN:
            print(f"{r['ticker']:6} {'-':>9} {'-':>20} {'-':>18}  unknown - {r['period_note']}")
        else:
            print(f"{r['ticker']:6} {ps['finnhub_period_수']:>9} {ps['SEC_회계종료일과_일치']:>20} "
                  f"{ps['SEC_회계종료일의_달력분기말과_일치']:>18}  {r['period_evidence']} / {r['period_note']}")

    print()
    print("[4] basis 필드 - 창 4행 전부에서 읽는다 (1행만 채워지면 partial 이고 통과가 아니다)")
    print(f"{'티커':6} {'currency':>10} {'share_basis':>12} {'accounting':>11} {'asOf':>8}   2A-2E 일치")
    for r in results:
        f = r["basis_fields"]
        cross = " ".join(f"{k[:4]}={v}" for k, v in r["basis_cross_endpoint"].items())
        print(f"{r['ticker']:6} {f['currency']:>10} {f['share_basis']:>12} {f['accounting']:>11} "
              f"{f['asOf']:>8}   {cross}")

    print()
    print("[5] 표시 항목 - 창 값 자릿수 정합과 surprise 부호 (판정 아님 · 원인 단정하지 않음)")
    print(f"{'티커':6} {'최대/최소 배수':>14} {'표시':>5}  surprise 부호 쏠림")
    for r in results:
        m = r["magnitude"]
        ratio = f"{m['ratio']:.2f}" if m["ratio"] is not None else "-"
        print(f"{r['ticker']:6} {ratio:>14} {'!' if m['flagged'] else '':>5}  {m['surprise_skew'] or '-'}")
    print(f"  ! 는 창 4행 값의 최대/최소가 {MAGNITUDE_FLAG:.0f}배 이상이라는 표시다. 기준 불일치의 가능성을")
    print("  가리킬 뿐이며 단위(ADS/보통주)·회계기준·통화 중 무엇인지는 저장 자료로 가르지 못한다.")

    print()
    print("=" * 118)
    n = len(results)
    for key, label in (("raw_availability", "raw-availability"), ("label_continuity", "label-continuity"),
                       ("asof_anchored", "asof-anchored"), ("basis_verified", "basis-verified"),
                       ("score_ready", "score-ready")):
        ok = sum(1 for r in results if r[key])
        print(f"  {label:18} {ok}/{n}")
    print("=" * 118)


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")   # W6 - cp949 콘솔에서도 죽지 않는다
    except Exception:
        pass
    main()
