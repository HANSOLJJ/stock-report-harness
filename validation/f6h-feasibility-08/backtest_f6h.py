# F6-H(최근 확정 2분기 + 향후 2분기)와 F6-N(향후 4분기)의 창 차이를 SEC 실적으로 백테스트한다
"""SEC XBRL 분기 EPS 로 F6-H 와 F6-N 의 차이를 측정한다.

두 창은 모두 4개 분기지만 기준점이 다르다.

    분기 인덱스 :  k-1   k   k+1  k+2  k+3  k+4
    F6-H        :  ■    ■    ■    ■
    F6-N        :             ■    ■    ■    ■

F6-H 는 뒤쪽 2개가 확정 실적이고 앞쪽 2개가 전망이다. 이 스크립트는 **전망 자리에도
실적을 넣어** 추정 오차를 0 으로 만든 뒤 창 차이만 분리해 측정한다. 따라서 결과는
F6-H 오차의 **하한**이다. 실제로는 여기에 2개 분기의 추정 오차가 더 얹힌다.

입력  : SEC companyconcept us-gaap/EarningsPerShareDiluted (allowlist 등재 원천)
출력  : 기업별 오차 분포, 밴드 전환 확률, 순위 안정성

사용:
    export SEC_UA="your-app research contact:you@example.com"
    python backtest_f6h.py fetch     # SEC 원본을 ./_raw 에 내려받는다
    python backtest_f6h.py report    # 분석 결과를 출력한다
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


def band_flip_probability(err: float) -> float:
    """EPS 오차가 PER 을 1/(1+e) 배로 옮긴다. 밴드 안에서 로그균등이라고 볼 때의 전환 확률."""
    return min(1.0, abs(math.log(1 + err)) / math.log(BAND_RATIO)) if err > -1 else 1.0


def band_of(per: float) -> int:
    for i, upper in enumerate(BANDS):
        if per < upper:
            return -i
    return -5


def report() -> None:
    print("=" * 96)
    print("F6-H(2A+2E) 대 F6-N(4E) — 창 차이만 측정 (추정 오차 0 가정, 따라서 하한)")
    print("=" * 96)
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

    # 순위 안정성 — 같은 주가로 두 지표의 PER 순위를 비교한다 (단면 민감도)
    prices = json.loads((HERE / "prices.json").read_text(encoding="utf-8")) if (HERE / "prices.json").is_file() else {}
    rows = [(t, w, prices.get(t)) for t, w in latest.items() if prices.get(t) and w["f6h"] > 0 and w["f6n"] > 0]
    if rows:
        print("\n순위 안정성 (같은 주가, 최근 창 기준 — 시점 정렬이 아닌 단면 민감도)")
        print(f"{'티커':6} {'주가':>9} {'PER(F6-H)':>10} {'PER(F6-N)':>10} {'밴드H':>6} {'밴드N':>6} {'밴드차':>6}")
        per_h, per_n = {}, {}
        flips = 0
        for t, w, p in rows:
            ph, pn = p / w["f6h"], p / w["f6n"]
            per_h[t], per_n[t] = ph, pn
            bh, bn = band_of(ph), band_of(pn)
            flips += bh != bn
            print(f"{t:6} {p:>9.2f} {ph:>10.1f} {pn:>10.1f} {bh:>6} {bn:>6} {bh-bn:>+6}")
        rank_h = {t: i for i, t in enumerate(sorted(per_h, key=per_h.get))}
        rank_n = {t: i for i, t in enumerate(sorted(per_n, key=per_n.get))}
        inv = sum(1 for a in rank_h for b in rank_h
                  if a < b and (rank_h[a] - rank_h[b]) * (rank_n[a] - rank_n[b]) < 0) // 1
        pairs = len(rows) * (len(rows) - 1) // 2
        print(f"\n밴드가 달라지는 기업 {flips}/{len(rows)} · 순위 역전 쌍 {inv}/{pairs}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "report"
    if cmd == "fetch":
        fetch()
    else:
        report()
