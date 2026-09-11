# 12개사 cash·fcf_ttm 을 SEC 실측값으로 등록한다 — cash 는 순수 현금, 유동성 버퍼는 basis 에 보존 (네트워크 없음)
"""**승인된 실행은 건드리지 않는다.** 대상은 `ai-scorecard-2026-09-obsreg` 뿐이다.

## 핵심은 `cash` 의 정의다

설계 지침 6.4 는 **사용 가능한 현금 및 현금성자산만** 포함하고, 단기 투자자산을 넣으려면
**환금성 기준을 먼저 정하라**고 한다. **그 기준이 아직 없다.** 그래서 순수 현금
(`CashAndCashEquivalents`)으로 등록하고, 유동성 버퍼와 총계는 `basis` 에 **버리지 않고** 남긴다.
기준이 정해지면 그 자리에서 바로 쓸 수 있어야 한다.

## legacy 값은 무엇이었나 — **세 갈래였다**

| legacy `cash` 가 같았던 것 | 개사 |
|---|---|
| 유동성 버퍼(현금 + 단기투자) | **7** — microsoft·amazon·tesla·palantir·meta·oracle·alphabet |
| 총계(비유동 증권까지 포함) | **3** — apple·tsmc·alibaba |
| 어느 쪽도 아님 | **2** — nvidia(1.5% 차) · spacex-xai(6% 차, `현금 $100B(IPO)` 반올림 서술) |

설계진행은 7개사가 버퍼와 같다고 했고 그것은 맞다. **나머지 5개사가 무엇이었는지는 갈렸다.**
`legacy cash` 가 단일 정의가 아니었다는 뜻이고, 순수 현금으로 통일해야 할 이유가 하나 더 있다.

사용:
    python validation/cash-fcf-35/apply_cash_fcf.py
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
RUN_ID = "ai-scorecard-2026-09-obsreg"
RUN = ROOT / "scorecard" / "runs" / RUN_ID
SRC_BLOB = ("4074894", "validation/cash-fcf-35/cash_fcf_35_results.json")

OBSERVED_AT = "2026-09-11"
SRC_ID = "SRC-SEC-FACTS-F6"          # 보존 companyfacts. 이번 과제도 신규 호출 없음.
SRC_TSM = "SRC-SEC-TSM-20F-FY2025"
SRC_BABA = "SRC-SEC-BABA-20F-FY2026"

# 20-F 가 스스로 선언한 환율. F6-REG-28 에서 등록한 값과 **같은 값을 쓴다**.
# C-13 은 alibaba 에 6.8979 를 썼는데 20-F 문면은 6.8980 이다. 0.0015% 차라 반올림 결과가 같다.
FX = {"tsmc": 31.37, "alibaba": 6.8980}


def load_source() -> dict:
    out = subprocess.run(["git", "show", f"{SRC_BLOB[0]}:{SRC_BLOB[1]}"], capture_output=True)
    if out.returncode != 0:
        raise SystemExit("C-13 CASH-FCF-35 결과를 읽지 못했다")
    return json.loads(out.stdout.decode("utf-8", "replace"))


def usd(cash: dict, key: str, cid: str, native_key: str | None = None):
    """USD 값을 고른다. 현지통화 공시사는 **20-F 선언 환율**로 우리가 다시 환산해 대조한다."""
    if key in cash:
        return float(cash[key]), None
    direct = cash.get(f"{key}_usd")
    native = cash.get(native_key or f"{key}_native")
    if direct is None:
        return None, None
    recomputed = None if native is None else round(native / FX[cid], 0)
    return float(direct), recomputed


def main() -> int:
    sys.path.insert(0, str(ROOT / "scripts"))
    from scorecard.schema import load_json_strict, validate_observations, write_json

    registry = {c["company_id"]: c for c in load_json_strict(ROOT / "scorecard" / "companies.json")["companies"]}
    data = load_source()
    obs = load_json_strict(RUN / "observations.json")
    by_id = {o["observation_id"]: o for o in obs["items"]}

    bar = "=" * 118
    print(bar)
    print(f"CASH-FCF-35 — {RUN_ID} 에 12개사 cash·fcf_ttm 등록 (순수 현금 · 승인 실행 미변경)")
    print(bar)

    new: list[dict] = []
    print(f"\n[1] 등록값 — cash 는 **순수 현금**이다")
    print(f"  {'회사':11} {'순수현금(USD)':>18} {'유동버퍼':>18} {'fcf_ttm':>18} {'legacy cash':>17} legacy 정의")
    for it in data["items"]:
        cid = it["company_id"]
        c, cf, lg = it["cash"], it["cash_flows"], it.get("legacy_comparison", {})
        local = cid in FX
        src = {"tsmc": SRC_TSM, "alibaba": SRC_BABA}.get(cid, SRC_ID)

        pure, pure_re = usd(c, "cash_and_cash_equivalents", cid)
        buf, _ = usd(c, "liquid_cash_buffer", cid)
        tot = (c.get("total_cash_and_all_securities") or c.get("total_cash_and_all_financial_assets_usd")
               or c.get("total_cash_and_all_treasury_investments_legacy_usd"))
        fcf, fcf_re = usd(cf, "fcf_ttm", cid, native_key="fcf_ttm_native")
        ocf, _ = usd(cf, "ocf_ttm", cid, native_key="ocf_ttm_native")
        capex, _ = usd(cf, "capex_ttm", cid, native_key="capex_ttm_native")

        legacy_cash = lg.get("legacy_cash")

        def near(a, b):
            return a is not None and b is not None and abs(a - b) / max(abs(b), 1) < 0.002
        which = ("유동성 버퍼" if near(legacy_cash, buf) else
                 "총계(비유동 포함)" if near(legacy_cash, tot) else "어느 쪽도 아님")

        period = {"start": it["period_start"], "end": it["period_end"]}
        shared = {"measured_as_of": it["balance_sheet_date"], "form": it["latest_form"],
                  "accession": it["accession_number"], "taxonomy": it["taxonomy"],
                  "period_basis": it["period_basis"].lower()}
        if local:
            shared.update({"original_currency": it["currency"], "fx_rate": FX[cid],
                           "fx_rate_source": "20-F 자체 선언 편의환산 환율 (F6-REG-28 등록값과 동일)",
                           "fx_note": ("C-13 은 alibaba 에 6.8979 를 썼고 20-F 문면은 6.8980 이다. "
                                       "0.0015% 차이라 백만 단위 반올림 결과가 같다."
                                       if cid == "alibaba" else "C-13 과 같은 31.37 이다.")})

        # ---------------- cash (순수 현금)
        cash_basis = {
            **shared,
            "definition": "사용 가능한 현금 및 현금성자산만(설계 지침 6.4). 단기 투자자산을 넣지 않는다.",
            "concept": c.get("concept"),
            "why_pure_cash": "설계 지침 6.4 가 단기 투자자산을 포함하려면 **환금성 기준을 먼저 정하라**고 하는데 "
                             "그 기준이 아직 없다. 기준 없이 넓은 정의를 쓰면 완충이 과대계상되고 런웨이가 길어진다.",
            "preserved_wider_definitions": {
                "liquid_cash_buffer": buf,
                "liquid_cash_buffer_note": "현금 + 단기 투자자산. **환금성 기준이 정해지면 이 값을 쓴다.**",
                "total_including_noncurrent": tot,
                "restricted_cash": c.get("restricted_cash") or c.get("restricted_cash_usd"),
                "components": {k: v for k, v in c.items() if k != "concept"},
            },
            "legacy_comparison": {
                "legacy_cash": legacy_cash,
                "legacy_equaled": which,
                "note": "**legacy cash 의 정의가 12개사 안에서 세 갈래였다** — 7개사는 유동성 버퍼, "
                        "3개사는 비유동 증권까지 포함한 총계, 2개사는 어느 쪽도 아니다. "
                        "단일 정의가 아니었다는 것이 순수 현금으로 통일해야 할 이유다.",
                "diff_pct": lg.get("cash_pure_diff_pct"),
            },
        }
        if pure_re is not None:
            cash_basis["cross_check_recomputed_usd"] = {"recomputed": pure_re, "filed_or_reported": pure}

        # ---------------- fcf_ttm
        fcf_basis = {
            **shared,
            "formula": cf.get("fcf_formula"),
            "ocf_ttm": ocf, "ocf_concept": cf.get("ocf_concept"), "ocf_formula": cf.get("ocf_formula"),
            "capex_ttm": capex, "capex_concept": cf.get("capex_concept"),
            "capex_formula": cf.get("capex_formula"),
            "components": {k: v for k, v in cf.items() if k.endswith("_components")},
            "legacy_comparison": {"legacy_fcf_ttm": lg.get("legacy_fcf_ttm"),
                                  "diff_pct": lg.get("fcf_diff_pct")},
        }
        if cid == "alibaba":
            fcf_basis["non_gaap_variant"] = {
                "capex_non_gaap_usd": cf.get("capex_non_gaap_usd"),
                "fcf_non_gaap_usd": cf.get("fcf_non_gaap_usd"),
                "note": "20-F 가 토지사용권을 포함한 capex 와 제외한 non-GAAP 을 둘 다 준다. "
                        "**GAAP 쪽(토지사용권 포함)을 등록한다** — 현금이 실제로 나간 금액이다. "
                        "non-GAAP 을 쓰면 런웨이가 2.64년에서 2.82년이 되나 **둘 다 3년 미만이라 "
                        "G3 판정은 갈리지 않는다.**"}
        if fcf_re is not None:
            fcf_basis["cross_check_recomputed_usd"] = {"recomputed": fcf_re, "filed_or_reported": fcf}

        for metric, value, basis, raw in (
                ("cash", pure, cash_basis,
                 f"현금및현금성자산 {pure/1e9:,.1f}B (버퍼 {(buf or 0)/1e9:,.1f}B 는 basis 에 보존)"),
                ("fcf_ttm", fcf, fcf_basis,
                 f"TTM FCF {fcf/1e9:,.1f}B = OCF {(ocf or 0)/1e9:,.1f}B - CapEx {(capex or 0)/1e9:,.1f}B")):
            new.append({
                "observation_id": f"{cid}.{metric}.cashfcf35", "company_id": cid, "metric": metric,
                "value": float(value), "unit": "USD", "as_of": it["balance_sheet_date"],
                "observed_at": OBSERVED_AT, "kind": "derived" if metric == "fcf_ttm" else "actual",
                "source_id": src, "status": "verified",
                **({"period": period} if metric == "fcf_ttm" else {}),
                "basis": basis, "raw": raw,
                "note": ("CASH-FCF-35. **순수 현금으로 등록한다** — 설계 지침 6.4. "
                         "유동성 버퍼와 총계는 basis.preserved_wider_definitions 에 보존했다"
                         if metric == "cash" else
                         "CASH-FCF-35. SEC 실측. OCF·CapEx 구성요소를 basis 에 남겼다"),
            })
        print(f"  {cid:11} {pure:>18,.0f} {(buf or 0):>18,.0f} {fcf:>18,.0f} "
              f"{(legacy_cash or 0):>17,.0f} {which}")

    print(f"\n[2] 관측 {len(new)}건 추가 · 승계 대체 표시")
    for item in new:
        obs["items"].append(item)
        for suffix in (".v15", ".priv31"):
            old = by_id.get(f"{item['company_id']}.{item['metric']}{suffix}")
            if old and not str(old.get("note") or "").startswith("[CASH-FCF-35"):
                old["note"] = f"[CASH-FCF-35 대체됨 → {item['observation_id']}] " + (old.get("note") or "")
                print(f"  대체  {old['observation_id']:44} → {item['observation_id']}")
    validate_observations(obs, registry, RUN_ID)

    run = load_json_strict(RUN / "run.json")
    run["assumptions"] = list(run["assumptions"]) + [
        "cash 는 **순수 현금**(현금및현금성자산)으로 등록했다. 설계 지침 6.4 가 단기 투자자산을 포함하려면 "
        "환금성 기준을 먼저 정하라고 하는데 그 기준이 아직 없다. 유동성 버퍼·총계·제한현금은 관측 "
        "basis.preserved_wider_definitions 에 보존했고 기준이 정해지면 그대로 쓸 수 있다",
        "legacy cash 의 정의는 12개사 안에서 세 갈래였다 — 7개사는 유동성 버퍼, 3개사는 비유동 증권까지 "
        "포함한 총계, 2개사는 어느 쪽도 아니다. 단일 정의가 아니었다",
        "F6 의 P1·P2 는 여전히 legacy_unverified 인 market_cap 위에 선다. 점수를 깎지 않고 "
        "calc.unverified_inputs 와 경고로 드러낸다 — 우리 수집 공백을 기업 위험으로 바꾸지 않는다",
    ]
    write_json(RUN / "observations.json", obs)
    write_json(RUN / "run.json", run)
    print(f"\n[3] 저장 — 관측 {len(obs['items'])}건")
    print(f"    다음: python scripts/scorecard_cli.py calculate {RUN_ID}")
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    sys.exit(main())
