# Reverse DCF 의 가정 의존성을 정량화한다 — 시장가에서 implied growth 를 역산하고 가정 격자로 민감도를 잰다
"""Reverse DCF 는 전망치를 없애지 않는다. 전망치를 **가정으로 옮길 뿐**이다.

    EV = Σ_{t=1..N} FCF0·(1+g)^t / (1+r)^t  +  [FCF0·(1+g)^N·(1+g_t) / (r-g_t)] / (1+r)^N

시장가(EV)와 현재 FCF0 를 넣고 g 를 역산한다. 겉보기에는 전망이 없다. 그러나 우변에
**r(WACC), g_t(terminal growth), N(명시적 예측 기간)** 세 가정이 들어간다. 이 스크립트는
그 세 가정을 격자로 흔들어 implied g 가 얼마나 움직이는지 측정한다.

핵심 출력
    1. 기업별 implied g 와 가정 격자에서의 범위(spread)
    2. WACC 1%p 변화당 implied g 변화 — 가정 의존성의 크기
    3. FCF0 가 음수라 역산 자체가 성립하지 않는 기업 목록

입력은 현재 실행의 관측(market_cap, fcf_ttm, net_cash)만 쓴다. 새로 수집하지 않는다.

사용:
    python reverse_dcf.py
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / "scorecard" / "runs" / "ai-scorecard-2026-09-baseline"

# 가정 격자. 어느 하나도 관측이 아니다.
WACCS = [0.08, 0.09, 0.10, 0.11, 0.12]
TERMINALS = [0.020, 0.025, 0.030]
HORIZONS = [5, 10, 15]
BASE = (0.10, 0.025, 10)  # 흔히 쓰는 기본 가정

# F6 밴드 경계(참고용). implied g 를 점수로 옮길 때 어떤 눈금이 필요한지 보기 위함이다.
F6_BANDS = [20, 29, 42, 62, 90]


def load() -> dict[str, dict]:
    obs = json.loads((RUN / "observations.json").read_text(encoding="utf-8"))["items"]
    companies = {c["company_id"]: c for c in
                 json.loads((ROOT / "scorecard" / "companies.json").read_text(encoding="utf-8"))["companies"]}
    by: dict[str, dict] = {}
    for o in obs:
        by.setdefault(o["company_id"], {})[o["metric"]] = o["value"]
    out = {}
    for cid, m in by.items():
        c = companies[cid]
        out[cid] = {"listed": c["listed"], "name": c["display_name"],
                    "market_cap": m.get("market_cap"), "fcf": m.get("fcf_ttm"),
                    "net_cash": m.get("net_cash"), "ps": m.get("ps_ratio")}
    return out


def pv(fcf0: float, g: float, r: float, gt: float, n: int) -> float:
    """2단계 DCF 의 현재가치. g 에 대해 단조증가라 이분법으로 역산할 수 있다."""
    if r <= gt:
        return float("inf")
    total = sum(fcf0 * (1 + g) ** t / (1 + r) ** t for t in range(1, n + 1))
    terminal = fcf0 * (1 + g) ** n * (1 + gt) / (r - gt)
    return total + terminal / (1 + r) ** n


def implied_growth(ev: float, fcf0: float, r: float, gt: float, n: int) -> float | None:
    """EV 를 만족하는 g 를 이분법으로 찾는다. FCF0 <= 0 이면 성립하지 않는다."""
    if fcf0 is None or fcf0 <= 0 or ev is None or ev <= 0 or r <= gt:
        return None
    lo, hi = -0.60, 1.50
    if pv(fcf0, hi, r, gt, n) < ev:
        return None  # 150% 성장으로도 시장가를 설명하지 못한다
    if pv(fcf0, lo, r, gt, n) > ev:
        return None  # -60% 로도 시장가보다 크다
    for _ in range(200):
        mid = (lo + hi) / 2
        if pv(fcf0, mid, r, gt, n) < ev:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def main() -> None:
    data = load()
    listed = {k: v for k, v in data.items() if v["listed"]}

    print("=" * 104)
    print("1. 입력 가용성 — 현재 실행 관측만 사용")
    print("=" * 104)
    have, missing = [], []
    for cid, v in sorted(listed.items()):
        ok = v["market_cap"] is not None and v["fcf"] is not None and v["net_cash"] is not None
        (have if ok else missing).append(cid)
    print(f"  market_cap·fcf_ttm·net_cash 3종 보유: {len(have)}/{len(listed)}개사")
    print(f"  누락: {missing or '없음'}")
    print("  ※ revenue_ttm·operating_margin_ttm·ocf_ttm 은 관측이 없다(P/S 로 매출을 역산할 수는 있으나 파생값이다)")

    print()
    print("=" * 104)
    print("2. FCF0 부호 — 역산 성립 여부")
    print("=" * 104)
    neg = [(cid, listed[cid]["fcf"]) for cid in sorted(listed) if (listed[cid]["fcf"] or 0) <= 0]
    print(f"  FCF 양수 {len(listed) - len(neg)}/{len(listed)}개사")
    print(f"  FCF 음수(역산 불가): " + ", ".join(f"{c}({v/1e9:.1f}B)" for c, v in neg))

    print()
    print("=" * 104)
    print(f"3. implied growth 와 가정 민감도 (기본 WACC {BASE[0]:.0%}, terminal {BASE[1]:.1%}, N={BASE[2]})")
    print("=" * 104)
    print(f"{'기업':12} {'EV(B)':>9} {'FCF(B)':>8} {'기본 g':>8} {'격자 최소':>9} {'격자 최대':>9} {'폭(%p)':>8} {'ΔWACC1%p':>9}")
    rows = []
    for cid in sorted(listed):
        v = listed[cid]
        if v["market_cap"] is None or v["fcf"] is None:
            continue
        ev = v["market_cap"] - (v["net_cash"] or 0)
        base = implied_growth(ev, v["fcf"], *BASE)
        if base is None:
            print(f"{cid:12} {ev/1e9:>9,.0f} {(v['fcf'] or 0)/1e9:>8,.1f}   역산 불가(FCF<=0 또는 해 없음)")
            continue
        grid = [implied_growth(ev, v["fcf"], r, gt, n)
                for r in WACCS for gt in TERMINALS for n in HORIZONS]
        grid = [g for g in grid if g is not None]
        lo, hi = min(grid), max(grid)
        # WACC 1%p 민감도 — 나머지 가정 고정
        g9 = implied_growth(ev, v["fcf"], 0.09, BASE[1], BASE[2])
        g11 = implied_growth(ev, v["fcf"], 0.11, BASE[1], BASE[2])
        dw = (g11 - g9) / 2 if (g9 is not None and g11 is not None) else None
        rows.append((cid, base, lo, hi, dw))
        print(f"{cid:12} {ev/1e9:>9,.0f} {v['fcf']/1e9:>8,.1f} {base:>7.1%} {lo:>8.1%} {hi:>8.1%}"
              f" {(hi-lo)*100:>7.1f} {dw*100 if dw is not None else float('nan'):>8.1f}")

    if rows:
        spreads = sorted((hi - lo) * 100 for _, _, lo, hi, _ in rows)
        dws = sorted(abs(d) * 100 for *_, d in rows if d is not None)
        print("-" * 104)
        print(f"  격자 폭 중앙값 {spreads[len(spreads)//2]:.1f}%p · 최대 {spreads[-1]:.1f}%p")
        print(f"  WACC 1%p 당 implied g 변화 중앙값 {dws[len(dws)//2]:.1f}%p · 최대 {dws[-1]:.1f}%p")

    print()
    print("=" * 104)
    print("4. 가정 하나만 바꿔도 순위가 바뀌는가 (WACC 8% vs 12%, 나머지 고정)")
    print("=" * 104)
    pair = []
    for cid in sorted(listed):
        v = listed[cid]
        if v["market_cap"] is None or (v["fcf"] or 0) <= 0:
            continue
        ev = v["market_cap"] - (v["net_cash"] or 0)
        g8 = implied_growth(ev, v["fcf"], 0.08, BASE[1], BASE[2])
        g12 = implied_growth(ev, v["fcf"], 0.12, BASE[1], BASE[2])
        if g8 is not None and g12 is not None:
            pair.append((cid, g8, g12))
    if pair:
        r8 = {c: i for i, (c, _, _) in enumerate(sorted(pair, key=lambda x: x[1]))}
        r12 = {c: i for i, (c, _, _) in enumerate(sorted(pair, key=lambda x: x[2]))}
        inv = sum(1 for a in r8 for b in r8 if a < b and (r8[a]-r8[b])*(r12[a]-r12[b]) < 0)
        print(f"{'기업':12} {'g@8%':>8} {'g@12%':>8} {'순위8%':>7} {'순위12%':>8}")
        for c, g8, g12 in sorted(pair, key=lambda x: x[1]):
            print(f"{c:12} {g8:>7.1%} {g12:>7.1%} {r8[c]+1:>7} {r12[c]+1:>8}")
        print(f"\n  순위 역전 쌍 {inv}/{len(pair)*(len(pair)-1)//2}")
        print("  ※ WACC 를 전 종목에 똑같이 흔들면 순위는 보존된다. 수준만 통째로 이동한다.")

    print()
    print("=" * 104)
    print("5. 인접 기업 간 격차 대 가정 오차 — 기업별 WACC 를 쓰면 순위가 지켜지는가")
    print("=" * 104)
    base_g = sorted(((c, g) for c, g, _, _, _ in rows), key=lambda x: x[1])
    gaps = [(base_g[i + 1][1] - base_g[i][1]) * 100 for i in range(len(base_g) - 1)]
    if gaps:
        srt = sorted(gaps)
        med_gap = srt[len(srt) // 2]
        dws2 = sorted(abs(d) * 100 for *_, d in rows if d is not None)
        med_dw = dws2[len(dws2) // 2]
        print("  기본 가정에서의 implied g 순서와 인접 격차")
        for i in range(len(base_g) - 1):
            print(f"    {base_g[i][0]:12} {base_g[i][1]:>6.1%}  ->  {base_g[i+1][0]:12} {base_g[i+1][1]:>6.1%}   격차 {gaps[i]:.1f}%p")
        print(f"\n  인접 격차 중앙값 {med_gap:.1f}%p · 최소 {min(gaps):.1f}%p")
        print(f"  WACC 1%p 당 implied g 변화 중앙값 {med_dw:.1f}%p")
        print(f"  -> 기업별 WACC 가 {med_gap/med_dw:.2f}%p 만 달라도 인접 두 기업의 순서가 뒤집힌다")
        print(f"  -> 최소 격차 기준으로는 {min(gaps)/med_dw:.2f}%p 차이면 뒤집힌다")
        print("  실제 DCF 는 기업별 베타로 WACC 를 달리 잡는다. 전 종목 동일 WACC 는 위험이 큰 기업의")
        print("  요구수익률을 낮게 잡아 implied g 를 작게 만들고 그만큼 좋아 보이게 하는 편향을 낳는다.")


if __name__ == "__main__":
    main()
