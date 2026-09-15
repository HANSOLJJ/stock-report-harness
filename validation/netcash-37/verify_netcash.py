# 차입금·리스·유가증권을 보존 원자료에서 전부 재계산해 대조하고 net_cash 정의 근거를 집계한다 (네트워크 없음)
"""**받은 값을 정답으로 쓰지 않는다.** MCAP-36(커밋 0eb113d)의 차입금과 C-13(커밋 4074894)의 현금·증권을
보존 SEC companyfacts 와 보존 20-F 원문에서 다시 뽑아 대조한다.

## 이 검증기가 답하는 것 여덟

1. **MCAP-36 차입금이 재현되는가** — 각 사가 실제로 쓴 개념으로 다시 계산한다.
2. **MCAP-36 이 놓치거나 겹친 것** — 전수 훑기와 합계-구성요소 중복 검사.
3. **C-13 현금+증권이 재현되는가** — 대차대조표 줄만으로 다시 계산한다.
4. **'결측' 과 '0' 이 갈렸는가** — palantir 는 차입금이 없는 것이지 못 찾은 것이 아니다.
5. **'실측 불가' 가 진짜 불가인가** — apple 은 분기 미태깅, tsmc 는 20-F 를 읽으면 된다.
6. **유가증권 경계가 지켜지는가** — 지분법·비상장·제한현금·만기버킷이 빠졌는가.
7. **legacy 역산 정의 D 가 몇 개사에서 맞는가** — 규칙에 적은 근거가 실제와 같은지.
8. **6.4 를 P2 로 옮기면 얼마나 틀리는가** — alphabet 으로 재현한다.

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
    print("NETCASH-37 — 차입금·현금·유가증권 재검증 · net_cash 정의 근거")
    print(bar)

    ntm = blob_json(NTM)
    cash13 = {it["company_id"]: it["cash"] for it in blob_json(C13)["items"]}
    mine = {cid: measure.measure_us(cid, end) for cid, end in US_DATES.items()}
    cashm = {cid: measure.cash_marketable_us(cid, end) for cid, end in US_DATES.items()}
    from scorecard.rules import load_rules
    rules = load_rules("v1.7")
    spec = rules.f6_net_cash()

    print()
    print("[1] MCAP-36 차입금·리스를 각 사 개념으로 재계산 — 재현되는가")
    for cid in sorted(US_DATES):
        m, n = mine[cid], ntm[cid]
        if m["operating_lease_missing"]:
            # 2026-09-15 FIX-54 FC-03: 구성요소가 빠지면 measure 가 합계를 만들지 않는다. MCAP-36 값은 있는 쪽만 더한 부분 합이다.
            part = sum(measure.at(measure.facts(cid), t, US_DATES[cid], "USD") for t in m["operating_lease_concepts"])
            chk(m["operating_lease"] is None and close(part, n["operating_lease"]),
                f"{cid:11} operating_lease 합계 없음 — 부분 합 {part} 만 있고 빠진 개념 {m['operating_lease_missing']}")
        else:
            chk(close(m["operating_lease"], n["operating_lease"]),
                f"{cid:11} operating_lease {m['operating_lease']}")
        if not m["finance_lease_already_in_debt"]:
            chk(close(m["finance_lease"], n["finance_lease"]),
                f"{cid:11} finance_lease   {m['finance_lease']}")
        chk(close(m["debt_ex_lease"], n["debt_ex_lease"]) or cid in ("amazon", "palantir"),
            f"{cid:11} debt_ex_lease   내 {m['debt_ex_lease']} / MCAP-36 {n['debt_ex_lease']}")

    print()
    print("[2] MCAP-36 차입금에서 놓치거나 겹친 것 — **셋**")
    chk(close(mine["amazon"]["debt_ex_lease"], 132_549e6),
        "amazon: ShortTermBorrowings 325M 누락",
        "MCAP-36 의 단기차입 후보군이 **우선순위 fallback** 이라 LongTermDebtCurrent 가 먼저 걸리면 "
        "그 뒤를 안 본다. 같은 10-Q 에 별도 태깅된 항목이라 합산 대상이다. 132,224 → 132,549")
    spcx = mine["spacex-xai"]["finance_lease_already_in_debt"]
    chk(spcx is not None and close(spcx["excluded"], 1_079e6),
        "spacex-xai: 금융리스 1,079M **이중계상**",
        (spcx or {}).get("reason", "") + " MCAP-36 40,787 → 39,708")
    baba = measure.baba_measure()
    chk(close(baba["debt_ex_lease"], 259_996.0, 0.5),
        "alibaba: 차입금 103,311 → **259,996** RMB 백만 (누락 156,685)",
        "MCAP-36 은 전환사채와 은행차입만 잡았다. 보존 20-F 대차대조표에 무담보 선순위채 117,485 · "
        "교환사채 10,976 · 유동 은행차입 28,224 가 더 있다. 전부 문면과 US$ 칸 환산으로 확인")

    print()
    print("[3] C-13 현금+증권을 **대차대조표 줄만으로** 재계산 — 둘이 갈린다")
    for cid in sorted(US_DATES):
        c13 = cash13[cid].get("total_cash_and_all_securities")
        got = cashm[cid]["total"]
        same = close(got, c13)
        if same:
            chk(True, f"{cid:11} {got:>16,.0f} — C-13 과 동일")
        else:
            chk(cid in ("nvidia", "spacex-xai"),
                f"{cid:11} 내 {got:,.0f} / C-13 {c13:,.0f} — **정정 {got - c13:+,.0f}**")
    chk(close(cashm["nvidia"]["total"], 56_586e6),
        "nvidia: C-13 이 **만기 1년 이내 버킷 41,000 을 현금에 더했다**",
        "그 버킷은 대차대조표 줄이 아니라 공정가치 공시이고 현금성자산으로 분류된 증권까지 포함한다. "
        "현금 22,443 + 유가증권(현재) 34,143 = 56,586 이 옳고 6,857 이 이중계상돼 있었다")
    chk(close(cashm["spacex-xai"]["total"], 100_009e6),
        "spacex-xai: C-13 이 **제한현금 830 을 넣고 시장성 증권 6,487 을 빠뜨렸다**",
        "C-13 은 CashCashEquivalentsRestrictedCash… 합계 태그(94,352)를 썼다. "
        "현금 93,522 + MarketableSecuritiesCurrent 6,487 = 100,009 이 옳다")

    print()
    print("[4] '결측' 과 '0' 을 갈랐는가 — palantir")
    f = measure.facts("palantir")
    debt_tags = [t for t in ("LongTermDebtNoncurrent", "LongTermDebtCurrent", "LongTermDebt", "DebtCurrent",
                             "CommercialPaper", "ShortTermBorrowings", "NotesPayableCurrent",
                             "DebtLongtermAndShorttermCombinedAmount")
                 if measure.at(f, t, "2026-06-30", "USD") is not None]
    chk(not debt_tags, "2026-06-30 시점에 차입 부채 태그가 **한 건도 없다**", "검사한 태그 8종 전부 결측")
    liab = measure.at(f, "Liabilities", "2026-06-30", "USD")
    cur = measure.at(f, "LiabilitiesCurrent", "2026-06-30", "USD")
    parts = {t: measure.at(f, t, "2026-06-30", "USD")
             for t in ("OperatingLeaseLiabilityNoncurrent", "DeferredRevenueNoncurrent",
                       "OtherLiabilitiesNoncurrent")}
    chk(abs((liab - cur) - sum(parts.values())) < 1e6,
        f"비유동부채 {liab - cur:,.0f} 가 리스+이연수익+기타로 **전액 설명된다**",
        " + ".join(f"{k} {v:,.0f}" for k, v in parts.items()) + f" = {sum(parts.values()):,.0f}. "
        "**차입금은 결측이 아니라 0 이다.**")

    print()
    print("[5] '실측 불가' 가 진짜 불가인가 — 그리고 결측 유형이 붙었는가")
    node = measure.facts("apple").get("us-gaap", {}).get("OperatingLeaseLiability", {})
    ends = sorted({r["end"] for r in node.get("units", {}).get("USD", []) if not r.get("start")})
    chk(measure.at(measure.facts("apple"), "OperatingLeaseLiability", "2026-06-27", "USD") is None,
        "apple: 리스부채를 **10-K 에만 태깅**한다 — 기준일 2026-06-27 에 값이 없다",
        f"태깅된 일자는 전부 회계연도 말이다 — 최근 6개 {ends[-6:]}")
    chk(measure.at(measure.facts("palantir"), "OperatingLeaseLiabilityCurrent", "2026-06-30", "USD") is None
        and measure.at(measure.facts("palantir"), "OperatingLeaseLiability", "2026-06-30", "USD") is None,
        "palantir: 유동 리스부채가 **표준 태그로 없다** — 비유동분만 태깅",
        "유동분은 AccruedLiabilitiesCurrent 504,070천에 묻혀 있다")
    obs_items = json.loads((RUN / "observations.json").read_text(encoding="utf-8"))["items"]
    gaps = {o["company_id"]: o for o in obs_items
            if o["metric"] == "lease_liabilities" and o["observation_id"].endswith(".nc37")}
    chk(set(gaps) == {"apple", "palantir"}, "결측 관측 2건이 등록됐다", ", ".join(sorted(gaps)))
    for cid, o in sorted(gaps.items()):
        # 2026-09-15 FIX-54 2단계(3차 리뷰 A codex): companyfacts 표준 태그 결측만 확인했고 10-Q 전문은 보존·검색하지 않았다.
        # 발행사 미공시(not_disclosed_confirmed)로 올리지 않고 자료 범위에 맞게 unverified 로 둔다.
        chk(o["value"] is None and o["missing_type"] == "unverified",
            f"{cid:11} value=null · missing_type=unverified",
            "표준 태그 결측이지 발행사 미공시 확인이 아니다 — 10-Q 전문 미검색(basis.label_correction)")
    tsm_facts = measure.facts("tsmc")
    n_money = sum(1 for tags in tsm_facts.values() for node2 in tags.values()
                  for unit, rows in node2["units"].items() if unit in ("TWD", "USD")
                  for r in rows if r.get("end") == "2025-12-31" and not r.get("start"))
    chk(n_money == 0, "tsmc: 보존 companyfacts 에 2025-12-31 시점 **금액** 사실이 0건",
        "구조화 원천으로는 불가하고 **보존 20-F 로 간다**")

    print()
    print("[6] 유가증권 경계 — 시장성 있는 것만 남았는가")
    scope = spec["securities_scope"]
    chk("시장성" in scope["criterion"] and "청구권" in scope["criterion"],
        "규칙이 기준을 문장으로 갖고 있다", scope["criterion"])
    chk(len(scope["exclude"]) >= 5 and all(e.get("why") for e in scope["exclude"]),
        f"제외 항목 {len(scope['exclude'])}종 전부 사유를 갖고 있다",
        " / ".join(e["what"] for e in scope["exclude"]))
    big = {cid: cashm[cid]["excluded_present"] for cid in sorted(US_DATES)}
    total_excluded = sum(v["value"] for d in big.values() for v in d.values())
    chk(total_excluded > 400e9,
        f"미국 10개사에서 배제된 비시장성·합계 개념이 {total_excluded/1e9:,.0f}B 에 이른다",
        "alphabet 비상장지분 124,259 · amazon 122,300 · nvidia 47,898 등. **어느 것도 총계에 없다**")
    for cid in sorted(US_DATES):
        tags = {c["tag"] for c in cashm[cid]["concepts"]}
        chk(not (tags & {f"us-gaap:{t}" for t in measure.EXCLUDED_TAGS}),
            f"{cid:11} 총계에 배제 개념이 섞이지 않았다", "")
    tsm = measure.tsm_measure()
    chk(close(tsm["excluded_nonmarketable"], 22_632.0, 0.5),
        f"tsmc: 비시장성 {tsm['excluded_nonmarketable']:,.1f} NT$백만 제외",
        "비공개거래 지분 8,797.2 + 전환우선주 13,608.8 + SAFE 125.8 + 선물환 100.2. "
        "**주석 8·9 까지 내려가야 갈린다** — 대차대조표 줄만 보면 FVTPL·FVOCI 비유동에 통째로 숨는다")
    chk(close(baba["excluded_nonmarketable"], 390_168.0, 0.5),
        f"alibaba: 비시장성 {baba['excluded_nonmarketable']:,.0f} RMB백만 제외",
        "비상장 130,447 + 채무증권및대출 10,880 + 지분법 206,803 + 제한현금 42,038. "
        "**주석 11 이 그대로 갈라 준다.** 비상장 130,447 이 공정가치 계층표에 아예 없는 것이 "
        "시장가가 없다는 증거다")

    print()
    print("[7] legacy 역산 정의 D 의 근거 집계 — 규칙에 적은 것과 같은가")
    legacy = {o["company_id"]: o["value"] for o in obs_items
              if o["metric"] == "net_cash" and o["status"] == "legacy_unverified"}
    matched, differs, undecidable, partial_lease = [], [], [], []
    for cid in sorted(US_DATES):
        m = mine[cid]
        if cid == "apple":
            undecidable.append(cid)
            continue
        debt = 0.0 if cid == "palantir" else m["debt_ex_lease"]
        lease = m["lease_total"] or 0
        if m["lease_incomplete"]:
            # 2026-09-15 FIX-54 FC-03: 리스 구성요소가 빠진 회사는 **있는 쪽만 뺀 부분 합**으로 legacy 와 대조한다.
            # 결측을 0 으로 접은 것과 산술은 같으므로 그 사실을 따로 모아 규칙 evidence 와 맞춘다.
            f_ = measure.facts(cid)
            lease = sum(measure.at(f_, t, US_DATES[cid], "USD") for t in m["operating_lease_concepts"]) + (m["finance_lease"] or 0)
            partial_lease.append(cid)
        value = cashm[cid]["total"] - debt - lease
        lg = legacy[cid]
        (matched if abs(value - lg) <= max(abs(lg) * 0.002, 5e7) else differs).append((cid, value, lg))
    for cid, v in (("tsmc", tsm["net_cash_usd"]), ("alibaba", baba["net_cash_usd"])):
        lg = legacy[cid]
        (matched if abs(v - lg) <= max(abs(lg) * 0.002, 5e7) else differs).append((cid, v, lg))
    print(f"    일치 {len(matched)}개사")
    for cid, v, lg in sorted(matched):
        print(f"      {cid:11} 실측 {v/1e6:>12,.0f} / legacy {lg/1e6:>12,.0f} 백만 USD  ({(v-lg)/1e6:+,.0f})")
    print(f"    차이 {len(differs)}개사")
    for cid, v, lg in sorted(differs):
        print(f"      {cid:11} 실측 {v/1e6:>12,.0f} / legacy {lg/1e6:>12,.0f} 백만 USD  ({(v-lg)/1e6:+,.0f})")
    print(f"    판정 불가 {len(undecidable)}개사 — {', '.join(undecidable)}")

    spcx_v = next(v for cid, v, _ in matched if cid == "spacex-xai")
    chk(abs(spcx_v - legacy["spacex-xai"]) < 2e6,
        "**spacex-xai 가 legacy 60,300 과 100만 달러 차이로 맞는다**",
        "서로 독립인 두 정정이 있어야 나온다 — 금융리스 이중계상 제거(−1,079)와 유가증권 경계 적용"
        "(+5,657). **두 정정이 legacy 값 하나로 수렴하는 것이 이 경계의 가장 강한 증거다**")
    ev = spec["evidence"]
    chk(ev["matched"]["count"] == len(matched) == len(ev["matched"]["companies"]),
        f"규칙 evidence.matched.count {ev['matched']['count']} = 실제 일치 {len(matched)}개사")
    chk(set(ev["matched"]["companies"]) == {c for c, _, _ in matched},
        "일치 목록이 규칙과 같다", ", ".join(sorted(ev["matched"]["companies"])))
    chk(ev["differs"]["count"] == len(differs) and set(ev["differs"]["companies"]) == {c for c, _, _ in differs},
        f"규칙 evidence.differs.count {ev['differs']['count']} = 실제 차이 {len(differs)}개사",
        ", ".join(sorted(c for c, _, _ in differs)))
    chk(set(ev["undecidable"]) == set(undecidable), "판정 불가 목록이 규칙과 같다")
    chk(set((ev["matched"].get("partial_lease_basis") or {}).get("companies", [])) == set(partial_lease),
        f"**부분 리스 기준 일치**가 규칙에 적혀 있다 — {', '.join(partial_lease)}",
        "리스 구성요소 하나가 빠진 채로 legacy 와 맞았다. 완전 합산 기준의 일치가 아니다(FIX-54 FC-03)")
    chk(spec["status"] == "working_definition" and spec["provenance"]["kind"] == "legacy_reverse_engineered",
        "규칙이 이 정의를 **역산 작업 정의**로 선언한다 — 확정 정의가 나오면 대체된다")
    chk("아직 모른다" in ev["differs"]["note"],
        "**왜 안 맞는지 모른다는 것을 규칙이 말한다** — 모르는 것을 아는 척하지 않는다")

    print()
    print("[8] 설계 지침 6.4 를 P2 로 옮기면 — alphabet 재현")
    res = json.loads((RUN / "results.json").read_text(encoding="utf-8"))
    p2 = {c["company_id"]: (c["factors"]["F6"].get("calc") or {}).get("parameters", {}).get("P2")
          for c in res["companies"]}
    g = p2["alphabet"]["inputs"]
    pure = cash13["alphabet"]["cash_and_cash_equivalents"]
    wrong_nc = pure - mine["alphabet"]["debt_incl_lease"]
    right_nc = cashm["alphabet"]["total"] - mine["alphabet"]["debt_incl_lease"]
    chk(right_nc > 0 > wrong_nc,
        f"P2 net_cash {right_nc:,.0f} → 6.4 를 옮기면 {wrong_nc:,.0f} — **부호가 뒤집힌다**",
        f"차이 {right_nc - wrong_nc:,.0f} = 순수현금 {pure:,.0f} 와 현금+시장성증권 "
        f"{cashm['alphabet']['total']:,.0f} 의 간격")
    sep = spec["scope_separation"]
    chk({s["metric"] for s in sep["sites"]} == {"cash", "net_cash"},
        "규칙이 두 자리를 **서로 다른 지표**로 명시한다 — cash(6.4 런웨이) 대 net_cash(P2 EV 조정)")
    chk(rules.payload["policies"]["f9"].get("g3_cash_scope", {}).get("see")
        == "policies.f6.net_cash.scope_separation",
        "F9 쪽에도 상호 참조를 뒀다 — 어느 쪽에서 들어와도 걸린다")

    print()
    print("[9] 승인 대상 보존")
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
