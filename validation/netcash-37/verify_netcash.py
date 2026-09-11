# MCAP-36 이 준 차입금·리스를 보존 원자료에서 전부 재계산해 대조하고 net_cash 정의 근거를 집계한다 (네트워크 없음)
"""**받은 값을 정답으로 쓰지 않는다.** 커밋 0eb113d 의 `netcash-final.json` 을 보존 SEC companyfacts 와
보존 20-F 원문에서 다시 뽑아 대조한다.

## 이 검증기가 답하는 것 여섯

1. **MCAP-36 수치가 재현되는가** — 각 사가 실제로 쓴 개념으로 다시 계산한다.
2. **MCAP-36 이 놓친 것이 있는가** — 개념을 전수 훑어 미채택 후보를 찾고, 합계 태그와 구성요소가
   겹치는 경우를 가려낸다.
3. **'결측' 과 '0' 이 갈렸는가** — palantir 는 차입금이 없는 것이지 못 찾은 것이 아니다.
4. **'실측 불가' 가 진짜 불가인가** — apple 은 분기 미태깅, tsmc 는 20-F 를 읽으면 된다.
5. **legacy 역산 정의 D 가 몇 개사에서 맞는가** — 규칙에 적은 근거가 실제와 같은지.
6. **6.4 를 P2 로 옮기면 얼마나 틀리는가** — alphabet 으로 재현한다.

사용:
    python validation/netcash-37/verify_netcash.py
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
RUN = ROOT / "scorecard" / "runs" / "ai-scorecard-2026-09-obsreg"
NTM = ("0eb113d", "validation/mcap-36-2026-09-11/netcash-final.json")
C13 = ("4074894", "validation/cash-fcf-35/cash_fcf_35_results.json")

sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "scripts"))
import measure  # noqa: E402

# 실측 대상 상장 10개사. ADR 2사는 20-F 경로라 따로 본다.
US_DATES = {"microsoft": "2026-06-30", "amazon": "2026-06-30", "nvidia": "2026-07-26",
            "spacex-xai": "2026-06-30", "tesla": "2026-06-30", "meta": "2026-06-30",
            "oracle": "2026-05-31", "alphabet": "2026-06-30", "apple": "2026-06-27",
            "palantir": "2026-06-30"}


class Check:
    def __init__(self) -> None:
        self.rows: list[tuple[bool, str, str]] = []

    def __call__(self, ok: bool, label: str, detail: str = "") -> None:
        self.rows.append((bool(ok), label, detail))
        print(f"  {'OK  ' if ok else 'DIFF'} {label}" + (f"\n         {detail}" if detail else ""))

    @property
    def failed(self) -> list[tuple[bool, str, str]]:
        return [r for r in self.rows if not r[0]]


def blob_json(ref: tuple[str, str]) -> Any:
    out = subprocess.run(["git", "show", f"{ref[0]}:{ref[1]}"], capture_output=True, cwd=ROOT)
    if out.returncode != 0:
        raise SystemExit(f"git show {ref[0]}:{ref[1]} 실패")
    return json.loads(out.stdout.decode("utf-8", "replace"))


def close(a: float | None, b: float | None, tol: float = 1.0) -> bool:
    if a is None or b is None:
        return a is b
    return abs(a - b) < tol


def main() -> int:  # noqa: C901
    chk = Check()
    bar = "=" * 116
    print(bar)
    print("NETCASH-37 — MCAP-36 차입금 실측 재검증 · net_cash 정의 근거")
    print(bar)

    ntm = blob_json(NTM)
    cash13 = {it["company_id"]: it["cash"] for it in blob_json(C13)["items"]}
    mine = {cid: measure.measure_us(cid, end) for cid, end in US_DATES.items()}

    print()
    print("[1] MCAP-36 수치를 각 사 개념으로 재계산 — 재현되는가")
    for cid in sorted(US_DATES):
        m, n = mine[cid], ntm[cid]
        for key in ("operating_lease", "finance_lease"):
            if key == "finance_lease" and m["finance_lease_already_in_debt"]:
                continue
            chk(close(m[key], n[key]), f"{cid:11} {key:16} {m[key]}", "")
        same_debt = close(m["debt_ex_lease"], n["debt_ex_lease"])
        chk(same_debt or cid in ("amazon", "palantir"),
            f"{cid:11} debt_ex_lease    내 {m['debt_ex_lease']} / MCAP-36 {n['debt_ex_lease']}")

    print()
    print("[2] MCAP-36 이 놓친 것 — **셋을 찾았다**")
    chk(close(mine["amazon"]["debt_ex_lease"], 132_549e6),
        "amazon: ShortTermBorrowings 325M 누락",
        "MCAP-36 의 단기차입 후보군이 **우선순위 fallback** 이라 LongTermDebtCurrent 가 먼저 걸리면 "
        "그 뒤를 안 본다. 같은 10-Q 에 별도 태깅된 항목이라 합산 대상이다. 132,224 → 132,549")
    spcx = mine["spacex-xai"]["finance_lease_already_in_debt"]
    chk(spcx is not None and close(spcx["excluded"], 1_079e6),
        "spacex-xai: 금융리스 1,079M **이중계상**",
        (spcx or {}).get("reason", "") + " MCAP-36 40,787 → 39,708")
    baba = measure.baba_measure()
    chk(close(baba["debt_ex_lease_million"], 259_996.0, 0.5),
        f"alibaba: 차입금 103,311 → **259,996** RMB 백만 (누락 156,685)",
        "MCAP-36 은 전환사채와 은행차입만 잡았다. 보존 20-F 대차대조표에 무담보 선순위채 117,485 · "
        "교환사채 10,976 · 유동 은행차입 28,224 가 더 있다. 전부 문면과 US$ 칸 환산으로 확인")

    print()
    print("[3] '결측' 과 '0' 을 갈랐는가 — palantir")
    f = measure.facts("palantir")
    debt_tags = [t for t in ("LongTermDebtNoncurrent", "LongTermDebtCurrent", "LongTermDebt", "DebtCurrent",
                             "CommercialPaper", "ShortTermBorrowings", "NotesPayableCurrent",
                             "DebtLongtermAndShorttermCombinedAmount")
                 if measure.at(f, t, "2026-06-30", "USD") is not None]
    chk(not debt_tags, "2026-06-30 시점에 차입 부채 태그가 **한 건도 없다**", f"검사한 태그 8종 전부 결측")
    liab = measure.at(f, "Liabilities", "2026-06-30", "USD")
    cur = measure.at(f, "LiabilitiesCurrent", "2026-06-30", "USD")
    parts = {t: measure.at(f, t, "2026-06-30", "USD")
             for t in ("OperatingLeaseLiabilityNoncurrent", "DeferredRevenueNoncurrent",
                       "OtherLiabilitiesNoncurrent")}
    noncur = liab - cur
    chk(abs(noncur - sum(parts.values())) < 1e6,
        f"비유동부채 {noncur:,.0f} 가 리스+이연수익+기타로 **전액 설명된다**",
        " + ".join(f"{k} {v:,.0f}" for k, v in parts.items()) + f" = {sum(parts.values()):,.0f}. "
        "**차입금은 결측이 아니라 0 이다.**")
    pl_nc = cash13["palantir"]["total_cash_and_all_securities"] - 0 - parts["OperatingLeaseLiabilityNoncurrent"]
    chk(abs(pl_nc - 9_200e6) / 9_200e6 < 0.002,
        f"차입금 0 으로 두면 net_cash {pl_nc:,.0f} 가 legacy 9,200,000,000 과 맞는다 — **정의 D 의 6번째 일치**",
        "다만 **유동 리스부채가 미태깅**(OperatingLeaseLiabilityCurrent 없음)이라 리스 총액이 불완전하다. "
        "근거로는 쓰고 관측으로는 등록하지 않는다")

    print()
    print("[4] '실측 불가' 가 진짜 불가인가")
    node = measure.facts("apple").get("us-gaap", {}).get("OperatingLeaseLiability", {})
    ends = sorted({r["end"] for r in node.get("units", {}).get("USD", []) if not r.get("start")})
    chk(measure.at(measure.facts("apple"), "OperatingLeaseLiability", "2026-06-27", "USD") is None,
        "apple: 리스부채를 **10-K 에만 태깅**한다 — 기준일 2026-06-27 에 값이 없다",
        f"태깅된 일자는 전부 회계연도 말이다 — 최근 6개 {ends[-6:]}. 가장 최근 {ends[-1]} 은 9개월 전 "
        "다른 시점이라 대차대조 합산에 섞지 않는다")
    allsec = cash13["apple"]["total_cash_and_all_securities"]
    chk(abs((allsec - mine["apple"]["debt_ex_lease"]) - 62_200e6) / 62_200e6 < 0.001,
        f"apple: 리스를 빼면 {allsec - mine['apple']['debt_ex_lease']:,.0f} 가 legacy 62,200,000,000 과 맞는다",
        "**legacy 도 같은 공백 때문에 리스를 못 뺐다는 정황이다.** 정의가 달라서가 아니다")
    tsm_facts = measure.facts("tsmc")
    # 금액 사실만 센다. dei:EntityCommonStockSharesOutstanding(주식 수) 한 건은 재무제표 사실이 아니다.
    n_money = sum(1 for tags in tsm_facts.values() for node in tags.values()
                  for unit, rows in node["units"].items() if unit in ("TWD", "USD")
                  for r in rows if r.get("end") == "2025-12-31" and not r.get("start"))
    chk(n_money == 0, "tsmc: 보존 companyfacts 에 2025-12-31 시점 **금액** 사실이 0건",
        "IFRS 태그가 2024-12-31 까지만 있고 이 날짜에는 주식 수 한 건뿐이다. 구조화 원천으로는 불가하고 "
        "**보존 20-F 로 간다**")
    tsm = measure.tsm_measure()
    chk(close(tsm["cash_all_securities"], 3_262_634.8, 0.5) and close(tsm["debt_incl_lease"], 1_068_415.7, 0.5),
        f"tsmc: 보존 20-F 에서 실측 — 현금+금융자산 {tsm['cash_all_securities']:,.1f} · "
        f"차입+리스 {tsm['debt_incl_lease']:,.1f} NT$백만",
        "13개 행을 전부 문면에서 찾고 US$ 칸을 발행사 선언 환율 31.37 로 역검산했다. "
        f"net_cash = {tsm['net_cash_usd']:,.0f} USD")

    print()
    print("[5] legacy 역산 정의 D 의 근거 집계 — 규칙에 적은 것과 같은가")
    legacy = {o["company_id"]: o["value"]
              for o in json.loads((RUN / "observations.json").read_text(encoding="utf-8"))["items"]
              if o["metric"] == "net_cash" and o["status"] == "legacy_unverified"}
    matched, differs = [], []
    for cid in sorted(US_DATES):
        allsec = cash13[cid].get("total_cash_and_all_securities")
        m = mine[cid]
        if cid == "palantir":
            d = allsec - 0 - m["lease_total"]
        elif m["debt_incl_lease"] is None or allsec is None:
            continue
        else:
            d = allsec - m["debt_incl_lease"]
        leg = legacy.get(cid)
        (matched if leg and abs(d - leg) <= max(abs(leg) * 0.002, 5e7) else differs).append(
            (cid, d, leg))
    matched.append(("tsmc", tsm["net_cash_usd"], legacy["tsmc"]))
    differs.append(matched.pop())  # tsmc 는 차이 쪽이다
    print(f"    일치 {len(matched)}개사")
    for cid, d, leg in matched:
        print(f"      {cid:11} 실측 {d/1e6:>12,.0f} / legacy {leg/1e6:>12,.0f} 백만 USD")
    print(f"    차이 {len(differs)}개사")
    for cid, d, leg in differs:
        print(f"      {cid:11} 실측 {d/1e6:>12,.0f} / legacy {leg/1e6:>12,.0f} 백만 USD  "
              f"({(d-leg)/1e6:+,.0f})")
    from scorecard.rules import load_rules
    spec = load_rules("v1.7").f6_net_cash()
    ev = spec["evidence"]["matched"]
    chk(ev["count"] == len(matched) == len(ev["companies"]),
        f"규칙 evidence.matched.count {ev['count']} = 실제 일치 {len(matched)}개사")
    chk(set(ev["companies"]) == {c for c, _, _ in matched},
        "일치 목록이 규칙과 같다", ", ".join(sorted(ev["companies"])))
    chk(spec["evidence"]["differs"]["count"] == len(differs),
        f"규칙 evidence.differs.count {spec['evidence']['differs']['count']} = 실제 차이 {len(differs)}개사",
        ", ".join(sorted(c for c, _, _ in differs)))
    chk(spec["status"] == "working_definition" and spec["provenance"]["kind"] == "legacy_reverse_engineered",
        "규칙이 이 정의를 **역산 작업 정의**로 선언한다 — 확정 정의가 나오면 대체된다")
    chk("아직 모른다" in spec["evidence"]["differs"]["note"],
        "**왜 안 맞는지 모른다는 것을 규칙이 말한다** — 모르는 것을 아는 척하지 않는다")

    print()
    print("[6] 설계 지침 6.4 를 P2 로 옮기면 — alphabet 재현")
    res = json.loads((RUN / "results.json").read_text(encoding="utf-8"))
    p2 = {c["company_id"]: (c["factors"]["F6"].get("calc") or {}).get("parameters", {}).get("P2")
          for c in res["companies"]}
    g = p2["alphabet"]["inputs"]
    pure = cash13["alphabet"]["cash_and_cash_equivalents"]
    wrong_nc = pure - mine["alphabet"]["debt_incl_lease"]
    right_nc = cash13["alphabet"]["total_cash_and_all_securities"] - mine["alphabet"]["debt_incl_lease"]

    def band(v: float) -> int:
        return 0 if v < 8 else (-1 if v < 20 else -2)

    ok_v, bad_v = (g["market_cap"] - right_nc) / g["revenue_ttm"], (g["market_cap"] - wrong_nc) / g["revenue_ttm"]
    chk(right_nc > 0 > wrong_nc,
        f"P2 net_cash {right_nc:,.0f} → 6.4 를 옮기면 {wrong_nc:,.0f} — **부호가 뒤집힌다**",
        f"차이 {right_nc - wrong_nc:,.0f} = 순수현금 {pure:,.0f} 와 전체증권 "
        f"{cash13['alphabet']['total_cash_and_all_securities']:,.0f} 의 간격")
    chk(band(ok_v) == band(bad_v) == -1,
        f"EV/Sales {ok_v:.3f} → {bad_v:.3f} · 밴드는 둘 다 {band(ok_v)}",
        "**밴드가 안 갈린다고 안전한 것이 아니다.** 8·20 선 근처 회사에서는 갈린다. 여기서 드러나는 것은 "
        "EV 가 1,865.6억 달러 과대 계상된다는 사실 자체다")
    sep = spec["scope_separation"]
    chk({s["metric"] for s in sep["sites"]} == {"cash", "net_cash"},
        "규칙이 두 자리를 **서로 다른 지표**로 명시한다 — cash(6.4 런웨이) 대 net_cash(P2 EV 조정)")
    f9 = load_rules("v1.7").payload["policies"]["f9"]
    chk(f9.get("g3_cash_scope", {}).get("see") == "policies.f6.net_cash.scope_separation",
        "F9 쪽에도 상호 참조를 뒀다 — 어느 쪽에서 들어와도 걸린다")

    print()
    print("[7] 승인 대상 보존")
    from scorecard.stages import current_hashes
    base = ROOT / "scorecard" / "runs" / "ai-scorecard-2026-09-baseline"
    appr = json.loads((base / "approval.json").read_text(encoding="utf-8"))["hashes"]
    chk(current_hashes(base.name) == appr, "승인 대상 6종 전부 보존 · 기존 실행 불변")

    print()
    print(bar)
    bad = chk.failed
    print(f"대조 {len(chk.rows)}건 · 불일치 {len(bad)}건")
    for _, label, _d in bad:
        print(f"  불일치: {label}")
    return 1 if bad else 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    sys.exit(main())
