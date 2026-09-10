# verify_window.py 의 창 검증 게이트가 실제로 걸러내는지 저장 원자료 사본으로 재현 검사한다 (신규 API 호출 없음)
"""R1 재검토(설계진행 9d06eec) W1~W4 가 다시 통과하지 않는지 확인한다.

저장 원자료는 **읽기만** 한다. 각 검사는 메모리 사본을 변형해 `verify_rows()` 에 넘긴다.
파일에 쓰지 않으므로 `_raw/` 는 그대로다.

검사 목록
    T1  최신 실적을 전망으로 옮기면 asof 가 막는다            (W1 · 이전에는 통과했다)
    T1b 기준일 전 발표된 분기가 실적 목록에 없으면 막는다     (W1)
    T2  창 4행 중 1행에만 basis 를 주면 통과가 아니다         (W2 · 이전에는 score-ready 까지 갔다)
    T2b 행 간 basis 값이 어긋나면 conflict 다                 (W2)
    T2c 2A 와 2E 사이 basis 가 어긋나면 conflict 다           (W2)
    T3  실적 값이 비수치 문자열이면 막는다                    (W3 · 이전에는 통과했다)
    T3b NaN·inf 도 막는다                                     (W3)
    T3c 원문 경로 키가 없는 행에서 죽지 않는다                (R2 재검토 지적)
    T4  음수 EPS 는 결측이 아니다                             (W3 · SPCX -0.09)
    T5  변형이 없으면 저장 자료 판정이 그대로다               (검증기가 상수 출력이 아님)

사용:
    python verify_window_tests.py
"""
from __future__ import annotations

import copy
import sys
from datetime import date

from verify_window import BASIS_KEYS, load_finnhub, verify_rows

BASE = date(2026, 9, 9)          # 저장 원자료의 수집일(UTC)
FAILURES: list[str] = []
RAN = 0


def check(name: str, cond: bool, detail: str = "") -> None:
    global RAN
    RAN += 1
    mark = "PASS" if cond else "FAIL"
    print(f"  [{mark}] {name}{('  — ' + detail) if detail else ''}")
    if not cond:
        FAILURES.append(name)


def rows(ticker: str) -> tuple[list[dict], list[dict]]:
    past, fut, _ = load_finnhub(ticker)
    return copy.deepcopy(past), copy.deepcopy(fut)


def t1_moved_actual_into_forecast() -> None:
    """META 최신 실적 2026Q2 를 전망 목록으로 옮긴다. 이전 검증기는 window=True 였다."""
    past, fut = rows("META")
    moved = next(r for r in past if (r["year"], r["quarter"]) == (2026, 2))
    past = [r for r in past if r is not moved]
    fut.append({"symbol": "META", "year": 2026, "quarter": 2, "date": "2026-07-29",
                "epsEstimate": moved["estimate"], "epsActual": None,
                "_src": "테스트 변형 — 실적을 전망으로 이동"})
    r = verify_rows("META", past, fut, BASE)
    check("T1 라벨 연속성은 여전히 통과한다(이름이 보증하는 범위)", r["label_continuity"],
          f"창 {r['window_labels']}")
    check("T1 asof 가 막는다", not r["asof_anchored"], "; ".join(r["asof_issues"]))
    check("T1 score-ready 가 아니다", not r["score_ready"])


def t1b_reported_missing_from_actuals() -> None:
    """기준일 전 발표된 분기가 실적 목록에 없으면 2A 가 '최근 확정 2개'라는 전제가 깨진다."""
    past, fut = rows("META")
    fut.append({"symbol": "META", "year": 2026, "quarter": 3, "date": "2026-09-01",
                "epsEstimate": 6.6602, "epsActual": 6.70,
                "_src": "테스트 변형 — 기준일 전 발표된 분기"})
    r = verify_rows("META", past, fut, BASE)
    check("T1b asof 가 막는다", not r["asof_anchored"], "; ".join(r["asof_issues"]))


def _fill(row: dict, **kv) -> None:
    row.update(kv)


def t2_single_row_basis() -> None:
    """창 4행 중 첫 행에만 기준 필드를 준다. 이전 검증기는 score_ready=True 였다."""
    past, fut = rows("META")
    first = next(r for r in past if (r["year"], r["quarter"]) == (2026, 1))
    _fill(first, currency="USD", share_basis="common", accounting="us-gaap", asOf="2026-09-01")
    r = verify_rows("META", past, fut, BASE)
    check("T2 basis 가 통과하지 않는다", not r["basis_verified"], str(r["basis_fields"]))
    check("T2 partial 로 표시된다", all(str(v).startswith("partial") for v in r["basis_fields"].values()))
    check("T2 score-ready 가 아니다", not r["score_ready"])


def t2b_conflicting_rows() -> None:
    """4행 전부 채우되 한 행만 다른 값을 준다."""
    past, fut = rows("META")
    sel = [(past, (2026, 1)), (past, (2026, 2)), (fut, (2026, 3)), (fut, (2026, 4))]
    for i, (src, key) in enumerate(sel):
        row = next(r for r in src if (r["year"], r["quarter"]) == key)
        _fill(row, currency="KRW" if i == 3 else "USD", share_basis="common",
              accounting="ifrs-full" if i == 3 else "us-gaap", asOf="2026-09-01")
    r = verify_rows("META", past, fut, BASE)
    check("T2b conflict 로 낸다", not r["basis_verified"], str(r["basis_fields"]))
    check("T2b currency 가 conflict", r["basis_fields"]["currency"].startswith("conflict"))
    check("T2b 값이 상수가 아니라 입력을 읽는다", "KRW" in r["basis_fields"]["currency"])


def t2c_cross_endpoint_conflict() -> None:
    """2A 는 USD, 2E 는 TWD 로 준다. 두 endpoint 사이 불일치를 따로 낸다."""
    past, fut = rows("META")
    for src, key, cur in ((past, (2026, 1), "USD"), (past, (2026, 2), "USD"),
                          (fut, (2026, 3), "TWD"), (fut, (2026, 4), "TWD")):
        row = next(r for r in src if (r["year"], r["quarter"]) == key)
        _fill(row, currency=cur, share_basis="common", accounting="us-gaap", asOf="2026-09-01")
    r = verify_rows("META", past, fut, BASE)
    check("T2c 2A-2E 일치가 conflict", r["basis_cross_endpoint"]["currency"] == "conflict",
          str(r["basis_cross_endpoint"]))
    check("T2c basis 통과 아님", not r["basis_verified"])
    check("T2c 나머지 필드는 match", all(r["basis_cross_endpoint"][k] == "match"
                                      for k in BASIS_KEYS if k != "currency"))


def t3_non_numeric_actual() -> None:
    """최신 실적을 문자열로 바꾼다. 이전 검증기는 raw=True, window=True 였다."""
    past, fut = rows("META")
    next(r for r in past if (r["year"], r["quarter"]) == (2026, 2))["actual"] = "NOT_A_NUMBER"
    r = verify_rows("META", past, fut, BASE)
    check("T3 raw-availability 가 막는다", not r["raw_availability"], "; ".join(r["issues"]))
    check("T3 자리가 밀리지 않는다(2026Q2 가 창에 남는다)", "2026Q2" in r["window_labels"],
          str(r["window_labels"]))
    check("T3 score-ready 가 아니다", not r["score_ready"])


def t3b_nan_inf() -> None:
    past, fut = rows("META")
    next(r for r in past if (r["year"], r["quarter"]) == (2026, 2))["actual"] = float("nan")
    check("T3b NaN 이 막힌다", not verify_rows("META", past, fut, BASE)["raw_availability"])
    past, fut = rows("META")
    next(r for r in fut if (r["year"], r["quarter"]) == (2026, 3))["epsEstimate"] = float("inf")
    check("T3b inf 가 막힌다", not verify_rows("META", past, fut, BASE)["raw_availability"])


def t3c_row_without_src() -> None:
    """호출자가 원문 경로 키를 채우지 않아도 죽지 않는다(R2 재검토 지적)."""
    past, fut = rows("META")
    row = next(r for r in past if (r["year"], r["quarter"]) == (2026, 2))
    row.pop("_src", None)
    row["actual"] = "NOT_A_NUMBER"
    try:
        r = verify_rows("META", past, fut, BASE)
    except KeyError as e:
        check("T3c _src 없는 행에서 죽지 않는다", False, f"KeyError: {e}")
        return
    check("T3c _src 없는 행에서 죽지 않는다", not r["raw_availability"], "; ".join(r["issues"]))


def t4_negative_is_not_missing() -> None:
    """음수 EPS 는 정상 값이다. SPCX -0.09 로 확인한다."""
    past, fut, _ = load_finnhub("SPCX")
    w = verify_rows("SPCX", past, fut, BASE)
    got = [x for x in w["a2"] if x["val"] == -0.09]
    check("T4 SPCX -0.09 가 실적으로 잡힌다", bool(got) and got[0]["ok"], str(w["window_labels"]))
    # 음수만으로 실격되지 않는다는 것을 창이 완성되는 종목에서도 확인한다
    past, fut = rows("META")
    for r in past:
        r["actual"] = -abs(r["actual"])
    for r in fut:
        if r.get("epsEstimate") is not None:
            r["epsEstimate"] = -abs(r["epsEstimate"])
    r = verify_rows("META", past, fut, BASE)
    check("T4 전부 음수여도 raw·label·asof 는 통과한다",
          r["raw_availability"] and r["label_continuity"] and r["asof_anchored"])


def t5_unmodified_matches_stored() -> None:
    """변형 없이 돌리면 저장 자료의 판정이 나온다. 상수 출력이 아님을 함께 본다."""
    tickers = ["META", "NVDA", "GOOGL", "MSFT", "AMZN", "AAPL", "ORCL", "PLTR", "TSLA", "SPCX", "TSM", "BABA"]
    res = []
    for t in tickers:
        past, fut, warn = load_finnhub(t)
        res.append(verify_rows(t, past, fut, BASE, warn))
    n = {k: sum(1 for r in res if r[k]) for k in
         ("raw_availability", "label_continuity", "asof_anchored", "basis_verified", "score_ready")}
    check("T5 raw 11/12", n["raw_availability"] == 11, str(n))
    check("T5 label 11/12", n["label_continuity"] == 11)
    check("T5 asof 11/12", n["asof_anchored"] == 11)
    check("T5 basis 0/12", n["basis_verified"] == 0)
    check("T5 score-ready 0/12", n["score_ready"] == 0)
    baba = next(r for r in res if r["ticker"] == "BABA")
    check("T5 BABA 자릿수 표시가 켜진다(판정 아님)", baba["magnitude"]["flagged"]
          and baba["label_continuity"], f"배수 {baba['magnitude']['ratio']:.2f}")


def main() -> int:
    print("=" * 78)
    print(f"verify_window.py 재현 검사 — 저장 원자료 사본만 사용 · 기준일 {BASE.isoformat()}")
    print("=" * 78)
    for fn in (t1_moved_actual_into_forecast, t1b_reported_missing_from_actuals,
               t2_single_row_basis, t2b_conflicting_rows, t2c_cross_endpoint_conflict,
               t3_non_numeric_actual, t3b_nan_inf, t3c_row_without_src, t4_negative_is_not_missing,
               t5_unmodified_matches_stored):
        print(f"\n{fn.__name__}")
        fn()
    print("\n" + "=" * 78)
    if FAILURES:
        print(f"검사 {RAN}건 중 실패 {len(FAILURES)}건: {FAILURES}")
        return 1
    print(f"검사 {RAN}건 전부 통과")
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    sys.exit(main())
