# F6-H(최근 확정 2분기 + 향후 2분기)와 F6-N(향후 4분기)의 창 차이를 SEC 실적으로 백테스트한다
"""F6-H 를 두 축으로 나눠 측정한다. 둘은 서로 다른 질문이다.

축 A — **추정 정확도**: F6-H 가 *자기 창*(k-1..k+2)의 실현 합을 얼마나 맞히는가.
    F6-H = A(k-1) + A(k) + E(k+1) + E(k+2)   를   A(k-1)+A(k)+A(k+1)+A(k+2) 와 비교.
    앞 2개가 확정값이라 전망 오차가 절반으로 희석된다. 공급사 컨센서스와 실적을
    같은 원천에서 가져와 기준을 맞춘다.

축 B — **창 이동**: F6-H 창과 F6-N 창이 애초에 다른 12개월을 덮는다는 사실.
    F6-H(k-1..k+2) 를 F6-N(k+1..k+4) 과 비교. 이건 정확도가 아니라 **무엇을 재는가**
    의 차이이며, 기존 F6 구간표를 그대로 쓸 수 있는지를 가른다.

첫 보고서는 축 B 를 축 A 로 오독해 "F6-H 가 부정확하다" 고 결론냈다. 틀렸다.
축 A 로 보면 F6-H 는 자기 창을 정확히 맞힌다. 보완 지시(msg_6f18a5cb31aa)에 따라
두 축을 분리한다.

입력
    SEC XBRL us-gaap/EarningsPerShareDiluted   (축 B, allowlist 등재)
    Finnhub stock/earnings estimate·actual     (축 A, 같은 원천 쌍)

한계
    - 공급사 estimate 는 **발표 직전 컨센서스**다. 실제 F6-H 의 E(k+2) 는 2분기 앞
      추정이라 오차가 더 크다. 축 A 결과는 하한이다.
    - 컨센서스에 asOf 가 없어 point-in-time 무결성을 검증하지 못한다.
    - 시점별 검증 가격을 allowlist 원천에서 얻지 못해 순위 비교는 수행하지 않는다.
"""
from __future__ import annotations

import json
import math
import os
import sys
import time
import urllib.request
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = HERE / "_raw"

# 미국 정기보고(10-Q/10-K) 제출사만. TSM·BABA 는 20-F 라 분기 XBRL 이 없다(보고서 3.2).
CIKS = {
    "AAPL": 320193, "AMZN": 1018724, "GOOGL": 1652044, "META": 1326801,
    "MSFT": 789019, "NVDA": 1045810, "ORCL": 1341439, "PLTR": 1321655,
    "TSLA": 1318605, "SPCX": 1181412,
}
CONCEPT = "https://data.sec.gov/api/xbrl/companyconcept/CIK{cik:010d}/us-gaap/EarningsPerShareDiluted.json"

# F6 밴드 경계와 인접 배율. 밴드 전환 확률 계산에 쓴다.
BANDS = [20, 29, 42, 62, 90]
BAND_RATIO = 1.45


def fetch() -> None:
    ua = os.environ.get("SEC_UA")
    if not ua:
        sys.exit("SEC_UA 환경변수가 필요하다 (SEC 는 User-Agent 표기를 요구한다)")
    RAW.mkdir(exist_ok=True)
    for ticker, cik in CIKS.items():
        req = urllib.request.Request(CONCEPT.format(cik=cik), headers={"User-Agent": ua})
        with urllib.request.urlopen(req, timeout=60) as resp:
            (RAW / f"{ticker}.json").write_bytes(resp.read())
        print(f"  {ticker} 저장")
        time.sleep(0.3)  # SEC 요청 한도 준수


def _d(s: str) -> date:
    return date(int(s[:4]), int(s[5:7]), int(s[8:10]))


def quarters(ticker: str) -> list[tuple[date, float, bool]]:
    """(종료일, EPS, 파생여부) 시계열.

    **미국 제출사는 회계 4분기 EPS 를 XBRL 에 따로 태깅하지 않는다.** 10-K 에 연간만
    싣기 때문이다(보고서 3.1). 그래서 4분기는 `연간 - (1~3분기 합)` 으로 복원한다.
    희석 EPS 는 가중평균 주식수가 기간마다 달라 완전히 가산적이지 않으므로 복원값에는
    오차가 있다. 파생 여부를 함께 돌려주어 보고서에서 구분한다.

    같은 기간이 여러 제출에 나오면 **최초 제출값**을 쓴다. 당시 알 수 있던 값이다.
    """
    path = RAW / f"{ticker}.json"
    if not path.is_file():
        return []
    rows = json.loads(path.read_text(encoding="utf-8"))["units"]["USD/shares"]
    q_raw: dict[str, dict] = {}
    a_raw: dict[str, dict] = {}
    for r in rows:
        start, end, val = r.get("start"), r.get("end"), r.get("val")
        if not start or not end or val is None:
            continue
        days = (_d(end) - _d(start)).days
        bucket = q_raw if 80 <= days <= 100 else (a_raw if 350 <= days <= 380 else None)
        if bucket is None:
            continue
        if end not in bucket or r.get("filed", "9999") < bucket[end].get("filed", "9999"):
            bucket[end] = r
    merged: dict[date, tuple[float, bool]] = {
        _d(e): (float(r["val"]), False) for e, r in q_raw.items()
    }
    for end, ann in a_raw.items():
        a_end, a_start = _d(end), _d(ann["start"])
        inside = [(_d(e), float(r["val"])) for e, r in q_raw.items() if a_start < _d(e) < a_end]
        if len(inside) != 3:
            continue  # 3개가 아니면 나머지 한 분기를 특정할 수 없다
        if a_end in merged:
            continue
        merged[a_end] = (round(float(ann["val"]) - sum(v for _, v in inside), 4), True)
    series = sorted((d, v, derived) for d, (v, derived) in merged.items())
    # 분기가 끊긴 구간은 창 계산이 성립하지 않는다. 연속 구간만 남긴다.
    out: list[tuple[date, float, bool]] = []
    for item in series:
        if out and not 60 <= (item[0] - out[-1][0]).days <= 130:
            out = []
        out.append(item)
    return out


def windows(series: list[tuple[date, float]]) -> list[dict]:
    """각 시점 k 에서 F6-H 와 F6-N 을 만든다. k-1 과 k+4 가 모두 있어야 한다."""
    vals = [v for _, v, _ in series]
    ends = [d for d, _, _ in series]
    out = []
    for k in range(1, len(vals) - 4):
        f6h = sum(vals[k - 1:k + 3])
        f6n = sum(vals[k + 1:k + 5])
        if f6n == 0:
            continue
        out.append({"as_of_after": ends[k].isoformat(), "f6h": f6h, "f6n": f6n,
                    "err": (f6h - f6n) / abs(f6n)})
    return out


VENDOR = RAW / "vendor"


def vendor_quarters(ticker: str) -> list[dict]:
    """공급사(Finnhub) stock/earnings 의 (period, estimate, actual). 추정과 실적이 같은 기준이다."""
    path = VENDOR / f"pe_{ticker}.json"
    if not path.is_file():
        return []
    rows = json.loads(path.read_text(encoding="utf-8"))
    rows = [r for r in rows if r.get("estimate") is not None and r.get("actual") is not None]
    return sorted(rows, key=lambda r: r["period"])


def axis_a(ticker: str) -> dict | None:
    """축 A — F6-H 가 자기 창의 실현 합을 얼마나 맞히는가."""
    rows = vendor_quarters(ticker)
    if len(rows) < 4:
        return None
    a1, a2, q3, q4 = rows[-4:]
    f6h = a1["actual"] + a2["actual"] + q3["estimate"] + q4["estimate"]
    realized = a1["actual"] + a2["actual"] + q3["actual"] + q4["actual"]
    out = {"ticker": ticker, "f6h": f6h, "realized": realized,
           "q3_err": (q3["estimate"] - q3["actual"]) / abs(q3["actual"]) if q3["actual"] else None,
           "q4_err": (q4["estimate"] - q4["actual"]) / abs(q4["actual"]) if q4["actual"] else None,
           "window": f"{a1['period']}~{q4['period']}"}
    # 실현 합이 0 이하이면 비율 오차가 의미를 잃는다. APE 를 0 으로 두지 않고 별도로 남긴다.
    out["total_err"] = (f6h - realized) / abs(realized) if realized > 0 else None
    out["nonpositive_realized"] = realized <= 0
    return out


def band_flip_probability(err: float) -> float:
    """EPS 오차가 PER 을 1/(1+e) 배로 옮긴다. 밴드 안에서 로그균등이라고 볼 때의 전환 확률."""
    return min(1.0, abs(math.log(1 + err)) / math.log(BAND_RATIO)) if err > -1 else 1.0


def band_of(per: float) -> int:
    for i, upper in enumerate(BANDS):
        if per < upper:
            return -i
    return -5


TICKERS_VENDOR = ["META", "NVDA", "GOOGL", "MSFT", "AMZN", "AAPL", "ORCL", "PLTR", "TSLA", "TSM", "BABA"]


def report_axis_a() -> None:
    print("=" * 100)
    print("축 A — F6-H 가 자기 창의 실현 합을 맞히는 정확도 (공급사 추정·실적 동일 원천)")
    print("=" * 100)
    print(f"{'티커':6} {'창':>24} {'F6-H':>9} {'실현합':>9} {'합산오차':>9} | {'Q3 2E':>9} {'Q4 2E':>9}")
    totals, perq, skipped = [], [], []
    for ticker in TICKERS_VENDOR:
        r = axis_a(ticker)
        if not r:
            continue
        if r["nonpositive_realized"]:
            skipped.append((ticker, r["realized"]))
            tot = "  실현합<=0"
        else:
            totals.append(abs(r["total_err"]))
            tot = f"{r['total_err']:+8.2%}"
        for key in ("q3_err", "q4_err"):
            if r[key] is not None:
                perq.append(abs(r[key]))
        q3 = f"{r['q3_err']:+8.1%}" if r["q3_err"] is not None else "       —"
        q4 = f"{r['q4_err']:+8.1%}" if r["q4_err"] is not None else "       —"
        print(f"{ticker:6} {r['window']:>24} {r['f6h']:>9.3f} {r['realized']:>9.3f} {tot} | {q3:>9} {q4:>9}")
    for label, sample in (("합산 오차(축 A)", sorted(totals)), ("분기별 2E 오차", sorted(perq))):
        if sample:
            med = sample[len(sample) // 2]
            print(f"\n{label}: n={len(sample)} · 중앙값 {med:.2%} · 최대 {sample[-1]:.2%}"
                  f" → PER {med/(1+med):.1%} 이동 → 밴드 전환 확률 {band_flip_probability(med):.0%}")
    if skipped:
        print("\n실현 합이 0 이하라 APE 를 계산하지 않은 종목:", ", ".join(f"{t}({v:.3f})" for t, v in skipped))
    print("\n한계: 공급사 estimate 는 발표 직전 컨센서스라 2분기 앞 추정보다 정확하다. 축 A 결과는 하한이다.")
    print("      컨센서스에 asOf 가 없어 point-in-time 무결성은 검증하지 못했다.")


def report() -> None:
    report_axis_a()
    print()
    print("=" * 100)
    print("축 B — F6-H 창과 F6-N 창의 차이 (정확도가 아니라 '무엇을 재는가'. 구간표 재조정 필요성 판단용)")
    print("=" * 100)
    all_err: list[float] = []
    latest: dict[str, dict] = {}
    print(f"{'티커':6} {'분기수':>5} {'표본':>4} {'중앙오차':>9} {'최소':>8} {'최대':>8}   최근 창 F6-H / F6-N")
    for ticker in CIKS:
        series = quarters(ticker)
        wins = windows(series)
        if not wins:
            print(f"{ticker:6} {len(series):>5} {0:>4}   — 표본 부족(연속 6개 분기 필요)")
            continue
        errs = sorted(w["err"] for w in wins)
        all_err.extend(abs(e) for e in errs)
        med = errs[len(errs) // 2]
        last = wins[-1]
        latest[ticker] = last
        print(f"{ticker:6} {len(series):>5} {len(wins):>4} {med:>+8.1%} {errs[0]:>+8.1%} {errs[-1]:>+8.1%}"
              f"   {last['f6h']:.3f} / {last['f6n']:.3f} ({last['err']:+.1%}, ~{last['as_of_after']})")

    # 두 창이 모두 흑자이고 분모가 지나치게 작지 않은 구간만 따로 본다.
    # 적자 전환 구간은 비율이 폭주해 분포를 왜곡한다(F6 도 EPS<=0 이면 채점하지 않는다).
    clean = [abs(w["err"]) for t in CIKS for w in windows(quarters(t))
             if w["f6h"] > 0 and w["f6n"] > 0.20]
    for label, sample in (("전체", sorted(all_err)), ("정상(양쪽 흑자·F6-N>0.20)", sorted(clean))):
        if not sample:
            continue
        med = sample[len(sample) // 2]
        p90 = sample[int(len(sample) * 0.9)]
        print("-" * 96)
        print(f"{label} 표본 {len(sample)}개 · 절대오차 중앙값 {med:.1%} · 90분위 {p90:.1%} · 최대 {sample[-1]:.1%}")
        for lbl, e in (("중앙값", med), ("90분위", p90)):
            print(f"  {lbl} {e:.1%} → PER {e/(1+e):.1%} 이동 → 밴드 전환 확률 {band_flip_probability(e):.0%}")

    # 부호 편향 — 오차가 방향을 가지는지
    signed = []
    for ticker in CIKS:
        wins = windows(quarters(ticker))
        signed.extend(w["err"] for w in wins)
    if signed:
        neg = sum(1 for e in signed if e < 0)
        print(f"\n부호: 음수 {neg}/{len(signed)} ({neg/len(signed):.0%}) — 음수는 F6-H 가 F6-N 보다 작다는 뜻이고 PER 을 키워 점수를 낮춘다")

    # 순위 안정성은 수행하지 않는다.
    # 시점별 검증 가격이 allowlist 원천에서 나오지 않는다(Finnhub stock/candle 은 무료 등급 403).
    # 과거 창에 현재 주가를 붙이면 시점이 어긋나므로 하드코딩 스냅샷을 쓰지 않는다.
    print("\n순위 안정성: 미수행 — 검증된 시점별 가격을 allowlist 원천에서 확보하지 못했다(보고서 3.4.3)")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "report"
    if cmd == "fetch":
        fetch()
    else:
        report()
