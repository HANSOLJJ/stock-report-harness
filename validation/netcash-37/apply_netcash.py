# net_cash 를 실측 등록한다 — 현금+**시장성** 유가증권 − 총차입금 − 리스부채 (보존 원자료만, 네트워크 없음)
"""**승인된 실행은 건드리지 않는다.** 대상은 `ai-scorecard-2026-09-obsreg` 뿐이다.

## 유가증권 경계 (설계진행 2026-09-11 결정)

**팔아서 기업 청구권을 상환할 수 있는 자산만 뺀다.** 유가증권은 시장성 있는 것에 한하고
지분법 투자와 비상장 지분은 넣지 않는다. 규칙 `policies.f6.net_cash.securities_scope` 다.

이 경계를 적용하면서 **라운드 1 등록값 셋이 바뀌었다.**

| 회사 | 라운드 1 | 라운드 2 | 사유 |
|---|---:|---:|---|
| nvidia | 24,583 | **17,726** | C-13 이 만기 1년 이내 버킷(41,000)을 현금에 더해 현금성자산 안의 증권 6,857 이 이중계상됐다 |
| spacex-xai | 54,644 | **60,301** | C-13 이 제한현금 830 을 넣고 시장성 증권 6,487 을 빠뜨렸다 |
| tsmc | 69,946 | **69,225** | 비공개거래 지분 8,797.2 · 전환우선주 13,608.8 · SAFE 125.8 · 선물환 100.2 제외 |

**spacex 가 legacy 60,300 과 100만 달러 차이로 맞는다.** 서로 독립인 두 정정이 legacy 값 하나로
수렴하므로 이 경계가 옳다는 가장 강한 증거다. 일치가 여섯에서 **일곱**이 된다.

## 등록 10개사 · 미등록 2개사

alibaba 가 경계 확정으로 풀려 등록된다. apple·palantir 는 리스 태깅 공백이 그대로라
**값 대신 `lease_liabilities` 결측 관측에 `missing_type` 을 붙인다.**

사용:
    python validation/netcash-37/apply_netcash.py      # 여러 번 돌려도 같은 결과
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
RUN_ID = "ai-scorecard-2026-09-obsreg"
RUN = ROOT / "scorecard" / "runs" / RUN_ID
C13 = ("4074894", "validation/cash-fcf-35/cash_fcf_35_results.json")

OBSERVED_AT = "2026-09-11"
SUFFIX = ".nc37"
SRC_FACTS = "SRC-SEC-FACTS-F6"
SRC_TSM = "SRC-SEC-TSM-20F-FY2025"
SRC_BABA = "SRC-SEC-BABA-20F-FY2026"

US = {"microsoft": "2026-06-30", "amazon": "2026-06-30", "nvidia": "2026-07-26",
      "spacex-xai": "2026-06-30", "tesla": "2026-06-30", "meta": "2026-06-30",
      "oracle": "2026-05-31", "alphabet": "2026-06-30"}

# 리스 태깅 공백으로 net_cash 실측이 막힌 둘. **값을 만들지 않고 결측 유형을 단다.**
LEASE_GAP = {
    "apple": {
        "as_of": "2026-06-27",
        "missing_type": "not_disclosed_confirmed",
        "raw": "2026-06-27 기준 리스부채 없음 — 10-K 에만 태깅",
        "why": "리스 관련 태그 39종이 모두 존재하나 값이 붙은 일자는 전부 회계연도 말이다"
               "(최근 2020-09-26 · 2021-09-25 · 2022-09-24 · 2023-09-30 · 2024-09-28 · 2025-09-27). "
               "**발행사가 분기에는 공시하지 않는다** — 우리가 못 찾은 것이 아니라 그 시점에 없다. "
               "가장 최근 값 2025-09-27 은 9개월 전 다른 시점이라 대차대조 합산에 섞지 않는다.",
        "why_not_unverified": "`unverified` 는 우리가 아직 실측하지 못했다는 뜻인데 여기서는 "
                              "보존 companyfacts 전수를 확인했고 그 시점에 값 자체가 없다. "
                              "수집 공백이 아니라 공시 주기의 문제다.",
        "impact": "net_cash 실측이 막힌다. legacy 62,200 백만 USD 가 그대로 P2 에 쓰인다. "
                  "리스를 빼고 계산하면 146,517 - 84,344 = 62,173 으로 legacy 와 맞는데, "
                  "**legacy 도 같은 공백을 겪었다는 정황이지 정의가 다르다는 뜻이 아니다.**",
    },
    "palantir": {
        "as_of": "2026-06-30",
        "missing_type": "not_disclosed_confirmed",
        "raw": "2026-06-30 기준 리스부채 유동분 없음 — 비유동분 211,400천만 태깅",
        "why": "`OperatingLeaseLiabilityNoncurrent` 211,400천은 있으나 `...Current` 도 상위 합계 "
               "`OperatingLeaseLiability` 도 없다. 유동 리스부채는 대차대조표 면에 별도 줄이 없고 "
               "`AccruedLiabilitiesCurrent` 504,070천에 묻혀 있다. **발행사가 따로 공시하지 않는다.**",
        "why_not_unverified": "보존 companyfacts 의 2026-06-30 시점 사실 44건을 전수 확인했다. "
                              "유동 리스부채를 가리키는 개념이 없다.",
        "impact": "리스 총액이 불완전해 net_cash 실측이 막힌다. 비유동분만 빼면 9,197,699천이고 "
                  "legacy 9,200,000천과 맞아 **정의의 근거로는 쓰지만 관측으로는 등록하지 않는다.** "
                  "apple 과 같은 결함이므로 같게 다룬다.",
    },
}

sys.path.insert(0, str(HERE))
import measure  # noqa: E402


def c13_cash() -> dict[str, Any]:
    out = subprocess.run(["git", "show", f"{C13[0]}:{C13[1]}"], capture_output=True, cwd=ROOT)
    if out.returncode != 0:
        raise SystemExit("C-13 CASH-FCF-35 결과를 읽지 못했다")
    return {it["company_id"]: it for it in json.loads(out.stdout.decode("utf-8", "replace"))["items"]}


def main() -> int:  # noqa: C901
    sys.path.insert(0, str(ROOT / "scripts"))
    from scorecard.rules import load_rules
    from scorecard.schema import load_json_strict, validate_observations, write_json

    rules = load_rules("v1.7")
    spec = rules.f6_net_cash()
    scope = spec["securities_scope"]
    registry = {c["company_id"]: c
                for c in load_json_strict(ROOT / "scorecard" / "companies.json")["companies"]}
    cash13 = c13_cash()
    obs = load_json_strict(RUN / "observations.json")

    bar = "=" * 118
    print(bar)
    print(f"NETCASH-37 라운드 2 — 유가증권 경계 적용 · alibaba 등록 · 결측 유형 (승인 실행 미변경)")
    print(bar)

    # **멱등.** 이전 회차가 남긴 것을 먼저 걷어내고 다시 넣는다.
    before = len(obs["items"])
    obs["items"] = [o for o in obs["items"] if not o["observation_id"].endswith(SUFFIX)]
    for o in obs["items"]:
        note = str(o.get("note") or "")
        if note.startswith("[NETCASH-37 대체됨"):
            o["note"] = note.split("] ", 1)[1] or None
    print(f"\n[0] 이전 회차 관측 {before - len(obs['items'])}건 제거 — 이 스크립트는 멱등이다")
    by_id = {o["observation_id"]: o for o in obs["items"]}
    legacy = {o["company_id"]: o["value"] for o in obs["items"]
              if o["metric"] == "net_cash" and o["status"] == "legacy_unverified"}

    shared = {
        "definition": spec["definition"],
        "definition_status": spec["status"],
        "definition_warning": "**legacy 역산으로 세운 작업 정의다.** 확정 정의가 나오면 이 값도 재계산 "
                              "대상이다 (policies.f6.net_cash.supersede).",
        "securities_criterion": scope["criterion"],
        "scope_warning": "설계 지침 6.4 의 '사용 가능한 현금' 을 여기로 옮기지 말 것. 6.4 는 런웨이 절이고 "
                         "여기는 EV 조정이다 (policies.f6.net_cash.scope_separation).",
    }

    def matched(value: float, cid: str) -> bool:
        lg = legacy.get(cid)
        return lg is not None and abs(value - lg) <= max(abs(lg) * 0.002, 5e7)

    new: list[dict[str, Any]] = []
    print("\n[1] 미국 8개사 — 현금 + 시장성 유가증권 (대차대조표 줄만)")
    print(f"  {'회사':11} {'현금+증권':>12} {'C-13 총계':>12} {'정정':>10} {'차입+리스':>12} "
          f"{'net_cash':>12} {'legacy':>12}")
    for cid, end in sorted(US.items()):
        cm = measure.cash_marketable_us(cid, end)
        m = measure.measure_us(cid, end)
        src = cash13[cid]
        c13_total = src["cash"].get("total_cash_and_all_securities")
        if m["debt_incl_lease"] is None:
            # 2026-09-15 FIX-54 FC-03: 리스 구성요소가 빠지면 합계가 없다. 부분 합으로 등록하지 않는다.
            raise SystemExit(f"{cid}: 리스 구성요소 결측 {m['operating_lease_missing'] + m['finance_lease_missing']} — "
                             "net_cash 를 완전 합산할 수 없다. 재실행하려면 이 회사를 먼저 정리할 것")
        value = cm["total"] - m["debt_incl_lease"]
        basis: dict[str, Any] = {
            "measured_as_of": end, "form": src["latest_form"],
            "accession": src["accession_number"], "taxonomy": src["taxonomy"],
            **shared,
            "components": {
                "cash_and_marketable_securities": cm["total"],
                "cash_and_marketable_securities_concepts": cm["concepts"],
                "excluded_nonmarketable_present": cm["excluded_present"],
                "debt_ex_lease": m["debt_ex_lease"],
                "debt_concepts": [f"us-gaap:{t}" for t in m["debt_concepts"]],
                "operating_lease": m["operating_lease"],
                "finance_lease": m["finance_lease"],
                "lease_total": m["lease_total"],
                "debt_incl_lease": m["debt_incl_lease"],
            },
            "legacy_comparison": {"legacy_net_cash": legacy.get(cid),
                                  "diff": None if legacy.get(cid) is None else value - legacy[cid],
                                  "matched": matched(value, cid)},
        }
        fixes = []
        if c13_total is not None and abs(c13_total - cm["total"]) > 1:
            fixes.append({"what": "현금+증권 총계를 대차대조표 줄로 재계산",
                          "c13_value": c13_total, "corrected": cm["total"],
                          "why": ("C-13 이 만기 1년 이내 공정가치 버킷 41,000 을 현금에 더해 "
                                  "현금성자산 안의 증권 6,857 이 이중계상됐다. 만기 버킷은 "
                                  "대차대조표 줄이 아니다." if cid == "nvidia" else
                                  "C-13 이 제한현금 830 을 포함한 합계 태그를 쓰고 시장성 증권 "
                                  "6,487 을 빠뜨렸다. 제한현금은 팔아서 청구권을 상환할 수 있는 "
                                  "자산이 아니고 시장성 증권은 대상이다.")})
        if m["finance_lease_already_in_debt"]:
            fixes.append({"what": "금융리스 이중계상 제거",
                          "detail": m["finance_lease_already_in_debt"]["reason"],
                          "excluded": m["finance_lease_already_in_debt"]["excluded"],
                          "mcap36_value": 40787000000, "corrected": m["debt_incl_lease"]})
        if cid == "amazon":
            fixes.append({"what": "ShortTermBorrowings 325M 추가",
                          "why": "MCAP-36 의 단기차입 후보군이 우선순위 fallback 이라 "
                                 "LongTermDebtCurrent 가 먼저 걸리면 그 뒤를 안 본다.",
                          "mcap36_value": 241995000000, "corrected": m["debt_incl_lease"]})
        if fixes:
            basis["corrections"] = fixes
        if cid == "spacex-xai":
            basis["why_this_match_matters"] = spec["evidence"]["matched"]["spacex_note"]
        new.append({
            "observation_id": f"{cid}.net_cash{SUFFIX}", "company_id": cid, "metric": "net_cash",
            "value": float(value), "unit": "USD", "as_of": end, "observed_at": OBSERVED_AT,
            "kind": "derived", "source_id": SRC_FACTS, "status": "verified", "basis": basis,
            "raw": f"현금+시장성증권 {cm['total']/1e9:,.1f}B − 차입 {m['debt_ex_lease']/1e9:,.1f}B "
                   f"− 리스 {m['lease_total']/1e9:,.1f}B = {value/1e9:,.1f}B",
            "note": "NETCASH-37. SEC 보존 원자료 실측. **유가증권은 시장성 있는 것만**",
        })
        print(f"  {cid:11} {cm['total']/1e6:>12,.0f} {(c13_total or 0)/1e6:>12,.0f} "
              f"{('예' if fixes else '—'):>10} {m['debt_incl_lease']/1e6:>12,.0f} "
              f"{value/1e6:>12,.0f} {(legacy.get(cid) or 0)/1e6:>12,.0f}")

    print("\n[2] ADR 2개사 — 보존 20-F 문면")
    for cid, meas, src_id, unit in (("tsmc", measure.tsm_measure(), SRC_TSM, "NT$백만"),
                                    ("alibaba", measure.baba_measure(), SRC_BABA, "RMB백만")):
        value = meas["net_cash_usd"]
        as_of = "2025-12-31" if cid == "tsmc" else "2026-03-31"
        basis = {
            "measured_as_of": as_of, "form": "20-F",
            "original_currency": meas["currency"], "unit_scale": unit, "fx_rate": meas["fx"],
            "fx_rate_source": "20-F 자체 선언 편의환산 환율 (F6-REG-28 등록값과 동일)",
            **shared,
            "how_columns_were_pinned": "표를 파싱해 열을 세지 않았다. 각 행을 **문면에서 값 순서로 찾고** "
                                       "원문 US$ 칸을 발행사 선언 환율로 역검산했다. 값 하나가 틀리면 "
                                       "줄을 못 찾는다.",
            "components": {
                "cash_and_marketable_securities": meas["cash_all_securities"],
                "excluded_nonmarketable": meas["excluded_nonmarketable"],
                "debt_ex_lease": meas["debt_ex_lease"], "lease_total": meas["lease_total"],
                "debt_incl_lease": meas["debt_incl_lease"],
                "net_cash_native": meas["net_cash_native_million"],
                "rows": meas["rows"],
            },
            "legacy_comparison": {"legacy_net_cash": legacy.get(cid),
                                  "diff": value - legacy[cid], "matched": matched(value, cid)},
        }
        if cid == "tsmc":
            basis["why_not_companyfacts"] = ("보존 companyfacts 에 2025-12-31 시점 **금액 사실이 0건**"
                                             "이다. IFRS 태그가 2024-12-31 까지만 있다.")
            basis["lease_note"] = ("유동 리스부채 3,833.0 은 대차대조표 면에 없고 '미지급비용 및 "
                                   "기타유동부채' 에 들어간다. 주석 16 이 유동·비유동을 나눈다. "
                                   "**차입금 유동분(136,925.7)에는 리스가 없다** — 주석 18·19 다.")
            basis["open_item"] = ("`Other financial assets` 59,702.9(US$1,903.2M)를 **넣어 두었다.** "
                                  "대차대조표가 주석 35(담보제공 자산)를 참조하므로 일부가 제한돼 있을 "
                                  "수 있으나 20-F 가 내역을 주지 않는다. 다른 회사의 자금운용 예금을 "
                                  "시장성 증권으로 세면서 tsmc 만 빼면 기준이 어긋난다.")
        else:
            basis["how_securities_were_split"] = (
                "대차대조표의 `Equity securities and other investments` 두 줄(30,054 + 449,942 = "
                "479,996)이 **주석 11 에서 그대로 쪼개진다** — 상장주식 100,594 · 비상장 130,447 · "
                "채무증권및대출 10,880 · 기타 자금운용 238,075. 앞의 둘만 시장성이다. "
                "비상장 130,447 이 공정가치 계층표에 아예 없는 것이 시장가가 없다는 증거다.")
            basis["open_item"] = ("`Debt securities and loan investments` 10,880(US$1,577M)을 통째로 "
                                  "**뺐다.** 채무증권과 대출이 한 줄에 섞여 있고 20-F 가 나누지 않는다. "
                                  "시장성 있는 것에 **한한다**는 기준이라 증명하지 못한 줄은 넣지 않는다. "
                                  "넣어도 P2 밴드는 안 갈린다.")
        new.append({
            "observation_id": f"{cid}.net_cash{SUFFIX}", "company_id": cid, "metric": "net_cash",
            "value": float(value), "unit": "USD", "as_of": as_of, "observed_at": OBSERVED_AT,
            "kind": "derived", "source_id": src_id, "status": "verified", "basis": basis,
            "raw": f"{unit} {meas['cash_all_securities']:,.1f} − {meas['debt_incl_lease']:,.1f} "
                   f"= {meas['net_cash_native_million']:,.1f} ÷ {meas['fx']} = {value/1e9:,.1f}B USD",
            "note": "NETCASH-37. **보존 20-F 문면 실측** · 유가증권은 시장성 있는 것만",
        })
        print(f"  {cid:11} 현금+시장성 {meas['cash_all_securities']:>12,.1f} {unit} · "
              f"비시장성 제외 {meas['excluded_nonmarketable']:>11,.1f} → "
              f"net_cash ${value/1e6:>10,.0f}M (legacy ${legacy[cid]/1e6:,.0f}M)")

    print("\n[3] 리스 태깅 공백 2개사 — **값 대신 결측 유형을 단다**")
    for cid, g in LEASE_GAP.items():
        new.append({
            "observation_id": f"{cid}.lease_liabilities{SUFFIX}", "company_id": cid,
            "metric": "lease_liabilities", "value": None, "unit": "USD", "as_of": g["as_of"],
            "observed_at": OBSERVED_AT, "kind": "actual", "source_id": SRC_FACTS,
            # 값이 없으면 verified 를 쓸 수 없다. 기존 결측 관측과 같은 `not_disclosed` 를 쓴다.
            "status": "not_disclosed", "missing_type": g["missing_type"],
            "basis": {"measured_as_of": g["as_of"], "why": g["why"],
                      "why_not_unverified": g["why_not_unverified"], "impact": g["impact"],
                      "blocks_metric": "net_cash", "definition_ref": "policies.f6.net_cash"},
            "raw": g["raw"],
            "note": f"NETCASH-37. net_cash 실측이 막힌 이유를 여기 남긴다 — {g['missing_type']}",
        })
        print(f"  {cid:11} missing_type={g['missing_type']}  {g['raw']}")

    print(f"\n[4] 관측 {len(new)}건 추가 · 승계 대체 표시")
    replaced = 0
    for item in new:
        obs["items"].append(item)
        old = by_id.get(f"{item['company_id']}.{item['metric']}.v15")
        if old and not str(old.get("note") or "").startswith("[NETCASH-37"):
            old["note"] = f"[NETCASH-37 대체됨 → {item['observation_id']}] " + (old.get("note") or "")
            replaced += 1
    print(f"  legacy 관측 {replaced}건에 대체 표시")
    validate_observations(obs, registry, RUN_ID)

    run = load_json_strict(RUN / "run.json")
    run["rule_hash"] = rules.hash
    # 멱등을 위해 이 과제가 넣은 전제를 표식으로 걷어낸다. 문자열 내용으로 거르면 새 전제가
    # 우연히 조건을 비켜 가 회차마다 쌓인다.
    tag = "[NETCASH-37] "
    keep = [a for a in run["assumptions"] if not a.startswith(tag)]
    run["assumptions"] = keep + [tag + a for a in (
        "net_cash 를 10개사 실측 등록했다. 정의는 `현금 + 시장성 유가증권 − 총차입금 − 리스부채` 이고 "
        "**legacy 역산으로 세운 작업 정의**다(policies.f6.net_cash). 12개사 중 7개사가 반올림 이내로 맞고 "
        "4개사가 다르며 apple 은 판정 자체가 안 된다. 확정 정의가 나오면 이 값들도 재계산 대상이다",
        "유가증권은 **시장성 있는 것에 한한다**(설계진행 2026-09-11). 지분법 투자·비상장 지분·제한 현금·"
        "만기 버킷 공시는 넣지 않는다. EV 조정은 팔아서 기업 청구권을 상환할 수 있는 자산이 대상이기 "
        "때문이다. 제외 내역은 관측 basis.components 에 전부 남겼다",
        "apple·palantir 는 리스부채 태깅 공백으로 net_cash 를 등록하지 못했다. 값을 만들지 않고 "
        "lease_liabilities 결측 관측에 missing_type=not_disclosed_confirmed 를 붙여 **왜 막혔는지**를 "
        "남겼고 F6 calc.unverified_blocked_by 로 산출물에 드러난다",
        "설계 지침 6.4(런웨이 절, metric `cash`)와 F6 P2(EV 조정, metric `net_cash`)는 **다른 것을 센다**. "
        "alphabet 기준 1,865.6억 달러가 갈리고 부호까지 뒤집힌다. 한쪽 논거를 다른 쪽으로 옮기지 않는다",
    )]
    write_json(RUN / "observations.json", obs)
    write_json(RUN / "run.json", run)
    print(f"\n[5] 저장 — 관측 {len(obs['items'])}건 · run.rule_hash {rules.hash[:12]}…")
    print(f"    다음: python scripts/scorecard_cli.py calculate {RUN_ID}")
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    sys.exit(main())
