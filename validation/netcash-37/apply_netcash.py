# net_cash 를 실측 등록한다 — 현금+유가증권 전체 − 총차입금 − 리스부채 (보존 원자료만, 네트워크 없음)
"""**승인된 실행은 건드리지 않는다.** 대상은 `ai-scorecard-2026-09-obsreg` 뿐이다.

## 등록 9개사 · 미등록 3개사

| | 회사 | 사유 |
|---|---|---|
| 등록 | microsoft·amazon·nvidia·spacex-xai·tesla·meta·oracle·alphabet | 보존 companyfacts 에 기준일 현금·차입·리스가 모두 있다 |
| 등록 | tsmc | companyfacts 에 2025-12-31 금액 사실이 0건이라 **보존 20-F 문면**에서 13개 행을 읽었다 |
| 미등록 | apple | 리스부채를 10-K 에만 태깅한다. 최근값은 9개월 전이라 대차대조 합산에 섞지 않는다 |
| 미등록 | palantir | 차입금 0 은 확인했으나 **유동 리스부채가 미태깅**이라 리스 총액이 불완전하다 |
| 미등록 | alibaba | 차입금 259,996 은 다 셌으나 '유가증권 전체' 의 범위가 1,056.6억 달러 폭으로 갈린다 |

apple·palantir 는 같은 결함(리스 태깅 공백)이라 **같게 다룬다.** 한쪽만 등록하면 기준이 둘이 된다.

## MCAP-36 수치를 세 군데 고쳤다

1. **amazon** `ShortTermBorrowings` 325M 이 빠졌다 — 단기차입 후보군이 우선순위 fallback 이라
   `LongTermDebtCurrent` 가 먼저 걸리면 그 뒤를 안 본다.
2. **spacex-xai** 금융리스 1,079M 이 이중계상됐다 — 총액 태그가 자본리스를 이미 포함한다.
3. **alibaba** 차입금 103,311 → 259,996 RMB 백만. 무담보 선순위채·교환사채·유동 은행차입이 빠졌다.
   (alibaba 는 어차피 현금 쪽이 안 정해져 등록하지 않는다. 값만 근거로 남긴다.)

사용:
    python validation/netcash-37/apply_netcash.py
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
SRC_FACTS = "SRC-SEC-FACTS-F6"
SRC_TSM = "SRC-SEC-TSM-20F-FY2025"

US = {"microsoft": "2026-06-30", "amazon": "2026-06-30", "nvidia": "2026-07-26",
      "spacex-xai": "2026-06-30", "tesla": "2026-06-30", "meta": "2026-06-30",
      "oracle": "2026-05-31", "alphabet": "2026-06-30"}

SKIPPED = {
    "apple": "리스부채를 10-K 에만 태깅해 기준일 2026-06-27 에 값이 없다. 가장 최근 리스는 2025-09-27 로 "
             "9개월 전 다른 시점이라 대차대조 합산에 섞지 않는다. 리스를 빼면 62,173 이 legacy 62,200 과 "
             "맞는데 이는 legacy 도 같은 공백을 겪었다는 정황이다",
    "palantir": "차입금이 **0 임을 확인했다** — 기준일 사실 44건에 차입 부채가 없고 비유동부채가 리스+이연수익"
                "+기타로 전액 설명된다. 그러나 유동 리스부채가 미태깅(OperatingLeaseLiabilityCurrent 없음)이라 "
                "리스 총액이 불완전하다. apple 과 같은 결함이므로 같게 다룬다",
    "alibaba": "차입금과 리스는 실측했다(259,996 + 21,726 RMB 백만). 갈리는 것은 현금 쪽이다 — 좁게 보면 "
               "net_cash 5,118, 넓게(제한현금·지분증권·지분법 투자 포함) 733,955 RMB 백만으로 폭이 1,056.6억 "
               "달러다. **한쪽을 고르는 것은 측정이 아니라 결정이라 여기서 하지 않는다**",
}

sys.path.insert(0, str(HERE))
import measure  # noqa: E402


def c13_cash() -> dict[str, Any]:
    out = subprocess.run(["git", "show", f"{C13[0]}:{C13[1]}"], capture_output=True, cwd=ROOT)
    if out.returncode != 0:
        raise SystemExit("C-13 CASH-FCF-35 결과를 읽지 못했다")
    return {it["company_id"]: it for it in json.loads(out.stdout.decode("utf-8", "replace"))["items"]}


def main() -> int:
    sys.path.insert(0, str(ROOT / "scripts"))
    from scorecard.rules import load_rules
    from scorecard.schema import load_json_strict, validate_observations, write_json

    rules = load_rules("v1.7")
    spec = rules.f6_net_cash()
    registry = {c["company_id"]: c
                for c in load_json_strict(ROOT / "scorecard" / "companies.json")["companies"]}
    cash13 = c13_cash()
    obs = load_json_strict(RUN / "observations.json")
    by_id = {o["observation_id"]: o for o in obs["items"]}
    legacy = {o["company_id"]: o["value"] for o in obs["items"]
              if o["metric"] == "net_cash" and o["status"] == "legacy_unverified"}

    bar = "=" * 118
    print(bar)
    print(f"NETCASH-37 — {RUN_ID} 에 net_cash 실측 등록 (승인 실행 미변경)")
    print(bar)

    shared_note = {
        "definition": spec["definition"],
        "definition_status": spec["status"],
        "definition_warning": "**legacy 역산으로 세운 작업 정의다.** 확정 정의가 나오면 이 값도 재계산 대상이다 "
                              "(policies.f6.net_cash.supersede).",
        "scope_warning": "설계 지침 6.4 의 '사용 가능한 현금' 을 여기로 옮기지 말 것. 6.4 는 런웨이 절이고 "
                         "여기는 EV 조정이다 (policies.f6.net_cash.scope_separation).",
    }

    new: list[dict[str, Any]] = []
    print(f"\n[1] 등록값 (백만 USD)")
    print(f"  {'회사':11} {'현금+증권':>12} {'차입금':>12} {'리스':>11} {'net_cash':>12} "
          f"{'legacy':>12} {'차이':>11}")
    for cid, end in sorted(US.items()):
        m = measure.measure_us(cid, end)
        src = cash13[cid]
        allsec = float(src["cash"]["total_cash_and_all_securities"])
        value = allsec - m["debt_incl_lease"]
        basis: dict[str, Any] = {
            "measured_as_of": end,
            "form": src["latest_form"], "accession": src["accession_number"],
            "taxonomy": src["taxonomy"],
            **shared_note,
            "components": {
                "cash_all_securities": allsec,
                "cash_all_securities_breakdown": {k: v for k, v in src["cash"].items() if k != "concept"},
                "debt_ex_lease": m["debt_ex_lease"],
                "debt_concepts": [f"us-gaap:{t}" for t in m["debt_concepts"]],
                "operating_lease": m["operating_lease"],
                "operating_lease_concepts": [f"us-gaap:{t}" for t in m["operating_lease_concepts"]],
                "finance_lease": m["finance_lease"],
                "finance_lease_concepts": [f"us-gaap:{t}" for t in m["finance_lease_concepts"]],
                "lease_total": m["lease_total"],
                "debt_incl_lease": m["debt_incl_lease"],
            },
            "legacy_comparison": {
                "legacy_net_cash": legacy.get(cid),
                "diff": None if legacy.get(cid) is None else value - legacy[cid],
                "matched": legacy.get(cid) is not None
                           and abs(value - legacy[cid]) <= max(abs(legacy[cid]) * 0.002, 5e7),
            },
        }
        if m["finance_lease_already_in_debt"]:
            basis["correction_vs_mcap36"] = {
                "what": "금융리스 이중계상 제거",
                "detail": m["finance_lease_already_in_debt"]["reason"],
                "excluded": m["finance_lease_already_in_debt"]["excluded"],
                "mcap36_value": 40787000000, "corrected": m["debt_incl_lease"],
            }
        if cid == "amazon":
            basis["correction_vs_mcap36"] = {
                "what": "ShortTermBorrowings 325M 추가",
                "detail": "MCAP-36 의 단기차입 후보군이 우선순위 fallback 이라 LongTermDebtCurrent 가 먼저 "
                          "걸리면 그 뒤를 안 본다. 같은 10-Q 에 별도 태깅된 항목이라 합산 대상이다.",
                "mcap36_value": 241995000000, "corrected": m["debt_incl_lease"],
            }
        new.append({
            "observation_id": f"{cid}.net_cash.nc37", "company_id": cid, "metric": "net_cash",
            "value": float(value), "unit": "USD", "as_of": end, "observed_at": OBSERVED_AT,
            "kind": "derived", "source_id": SRC_FACTS, "status": "verified", "basis": basis,
            "raw": f"현금+증권 {allsec/1e9:,.1f}B − 차입 {m['debt_ex_lease']/1e9:,.1f}B "
                   f"− 리스 {m['lease_total']/1e9:,.1f}B = {value/1e9:,.1f}B",
            "note": "NETCASH-37. SEC 보존 원자료 실측. **정의는 legacy 역산 작업 정의다**",
        })
        lg = legacy.get(cid)
        print(f"  {cid:11} {allsec/1e6:>12,.0f} {m['debt_ex_lease']/1e6:>12,.0f} "
              f"{m['lease_total']/1e6:>11,.0f} {value/1e6:>12,.0f} "
              f"{(lg or 0)/1e6:>12,.0f} {((value-(lg or 0))/1e6):>+11,.0f}")

    # ---------------- tsmc — 구조화 원천에 없어 보존 20-F 문면에서 읽는다
    t = measure.tsm_measure()
    value = t["net_cash_usd"]
    basis = {
        "measured_as_of": "2025-12-31",
        "form": "20-F", "original_currency": "TWD", "unit_scale": "NT$ 백만",
        "fx_rate": t["fx"],
        "fx_rate_source": "20-F 자체 선언 편의환산 환율 (F6-REG-28 등록값과 동일)",
        **shared_note,
        "why_not_companyfacts": "보존 companyfacts 에 2025-12-31 시점 **금액 사실이 0건**이다. IFRS 태그가 "
                                "2024-12-31 까지만 있어 구조화 원천으로는 실측이 불가하다.",
        "how_columns_were_pinned": "표를 파싱해 열을 세지 않았다. 13개 행을 **문면에서 값 순서로 찾고** "
                                   "US$ 칸을 31.37 로 역검산했다. 예: Bonds payable 856,227.5 / 31.37 = "
                                   "27,294.5 로 원문 US$ 칸과 일치한다. 값 하나가 틀리면 줄을 못 찾는다.",
        "components": {
            "cash_all_securities_ntd_million": t["cash_all_securities"],
            "debt_ex_lease_ntd_million": t["debt_ex_lease"],
            "lease_total_ntd_million": t["lease_total"],
            "debt_incl_lease_ntd_million": t["debt_incl_lease"],
            "net_cash_ntd_million": t["net_cash_native_million"],
            "rows": t["rows"],
        },
        "lease_note": "유동 리스부채 3,833.0 은 대차대조표 면에 없고 '미지급비용 및 기타유동부채' 에 들어간다. "
                      "주석 16 이 유동·비유동을 나눠 주므로 합계 35,428.0 을 쓴다. "
                      "**차입금 유동분(136,925.7)에는 리스가 없다** — 주석 18·19 이고 리스는 주석 16 이다.",
        "excluded": "지분법 투자 37,851.9 는 제외했다. 환금 목적 보유가 아니다.",
        "legacy_comparison": {"legacy_net_cash": legacy.get("tsmc"),
                              "diff": value - legacy["tsmc"], "matched": False},
    }
    new.append({
        "observation_id": "tsmc.net_cash.nc37", "company_id": "tsmc", "metric": "net_cash",
        "value": float(value), "unit": "USD", "as_of": "2025-12-31", "observed_at": OBSERVED_AT,
        "kind": "derived", "source_id": SRC_TSM, "status": "verified", "basis": basis,
        "raw": f"NT$백만 {t['cash_all_securities']:,.1f} − {t['debt_ex_lease']:,.1f} − "
               f"{t['lease_total']:,.1f} = {t['net_cash_native_million']:,.1f} ÷ 31.37 = "
               f"{value/1e9:,.1f}B USD",
        "note": "NETCASH-37. **보존 20-F 문면 실측** — companyfacts 에 이 기준일 금액 사실이 없다",
    })
    print(f"  {'tsmc':11} {t['cash_all_securities']/t['fx']:>12,.0f} "
          f"{t['debt_ex_lease']/t['fx']:>12,.0f} {t['lease_total']/t['fx']:>11,.0f} "
          f"{value/1e6:>12,.0f} {legacy['tsmc']/1e6:>12,.0f} "
          f"{(value-legacy['tsmc'])/1e6:>+11,.0f}")

    print(f"\n[2] 미등록 {len(SKIPPED)}개사 — **왜 못 하는지 남긴다**")
    for cid, why in SKIPPED.items():
        print(f"  {cid:11} {why}")

    print(f"\n[3] 관측 {len(new)}건 추가 · 승계 대체 표시")
    for item in new:
        obs["items"].append(item)
        old = by_id.get(f"{item['company_id']}.net_cash.v15")
        if old and not str(old.get("note") or "").startswith("[NETCASH-37"):
            old["note"] = f"[NETCASH-37 대체됨 → {item['observation_id']}] " + (old.get("note") or "")
            print(f"  대체  {old['observation_id']:34} → {item['observation_id']}")
    validate_observations(obs, registry, RUN_ID)

    run = load_json_strict(RUN / "run.json")
    # 규칙 파일이 이 과제에서 바뀌었다. 이 실행은 **승인 전**이라 다시 고정한다.
    # 승인된 ai-scorecard-2026-09-baseline 은 자기 rule_version(v1.5)을 가리키므로 영향이 없다.
    run["rule_hash"] = rules.hash
    run["assumptions"] = list(run["assumptions"]) + [
        "net_cash 를 9개사 실측 등록했다. 정의는 `현금 + 유가증권 전체 − 총차입금 − 리스부채` 이고 "
        "**legacy 역산으로 세운 작업 정의**다(policies.f6.net_cash). 12개사 중 6개사가 반올림 이내로 맞고 "
        "4개사가 다르며 2개사는 판정 자체가 안 된다. 확정 정의가 나오면 이 값들도 재계산 대상이다",
        "apple·palantir 는 리스부채 태깅 공백으로, alibaba 는 '유가증권 전체' 의 범위가 갈려 net_cash 를 "
        "등록하지 않았다. 셋 다 legacy 값이 그대로 남아 P2 가 미검증 입력 위에 선다",
        "설계 지침 6.4(런웨이 절, metric `cash`)와 F6 P2(EV 조정, metric `net_cash`)는 **다른 것을 센다**. "
        "alphabet 기준 1,865.6억 달러가 갈리고 부호까지 뒤집힌다. 한쪽 논거를 다른 쪽으로 옮기지 않는다",
    ]
    write_json(RUN / "observations.json", obs)
    write_json(RUN / "run.json", run)
    print(f"\n[4] 저장 — 관측 {len(obs['items'])}건 · run.rule_hash 재고정 {rules.hash[:12]}…")
    print(f"    다음: python scripts/scorecard_cli.py calculate {RUN_ID}")
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    sys.exit(main())
