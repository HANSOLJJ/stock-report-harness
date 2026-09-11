# 비상장 2사의 C-12·C-20 입력을 등록한다 — ps_ratio·arr_prior 신설, 결측 유형 등록, 모순 기록 (네트워크 없음)
"""**승인된 실행은 건드리지 않는다.** 대상은 `ai-scorecard-2026-09-obsreg` 뿐이다.

## 값은 전부 v1.5 원본에서 직접 뽑았다

`AI기업_채점규칙_v1.5.md`(sha256 `57beb84a…`, `v1.5.json` 선언값과 일치)와 같은 폴더의
`AI기업_채점표_v1.5.md` 다. 선행 조사 두 건(C-13 `03e1e57` · NTM `b0a2587`)이 준 값도
**그대로 믿지 않고 원본 문장에서 다시 읽었다.** `verify_private.py` 가 그 대조다.

## 세 가지 판단

**하나. P2 분모는 `arr` 이 아니라 TTM 보정 매출이다.**
구간표 `-2` 칸 괄호가 "ARR 배수 — TTM 보정 필수" 라고 명시한다. ARR 은 특정 시점 월매출 ×12
런레이트라 TTM 보다 과대하고, 보정 없이 쓰면 비상장사가 부당하게 싸 보인다(v1.5 645~647행).
그래서 `ps_ratio`(밸류÷TTM 매출)를 등록한다. 원본이 TTM 추정 배수를 직접 주므로 그 값을 쓰되
**어떻게 얻은 값인지**를 `basis` 에 남긴다.

**둘. anthropic 의 `~30~39` 는 구간이라 값을 하나 고를 수 없다.**
낮은 끝(30)을 값으로 두고 `basis.estimate_range` 에 `[30, 39]` 를 남긴다. 낮은 끝은 기업에
가장 덜 불리한 쪽이므로, 그 끝에서도 밴드가 `30x+`(−4)이면 판정이 견고하다는 뜻이다.
계산기가 양 끝이 같은 밴드에 드는지 확인하고 **갈리면 값을 고르지 않고 보류한다.**

**셋. 모순은 값을 고르지 않고 갈린다는 사실을 남긴다.**
Series H 조달액이 같은 문서 안에서 `$30B`(⑨절)와 `$65B`(비상장 ⑥ 표)로 갈린다. 이것이
`cumulative_raised` 를 통해 자본효율을 움직이고, **그 구간이 보정 임계 0.50 을 가로지른다.**
값을 고르지 않고 민감도를 `basis` 에 남긴다 — F6-REG-28 의 환율 밴드 민감도와 같은 장치다.

사용:
    python validation/priv-impl-31/apply_private_inputs.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
RUN_ID = "ai-scorecard-2026-09-obsreg"
RUN = ROOT / "scorecard" / "runs" / RUN_ID

OBSERVED_AT = "2026-09-11"
AS_OF = "2026-09-02"          # v1.5 기준선 시점. 원본이 시점 라벨을 주지 않는 값이 있다.

SRC = "SRC-v15-md"            # AI기업_채점표_v1.5.md — 기존 실행에 이미 등재된 출처
SRC_RULE = "SRC-v15-rule"

# ---------------------------------------------------------------- 모순 기록
SERIES_H = {
    "field": "anthropic Series H 조달액",
    "values": [
        {"value": 30_000_000_000, "location": "AI기업_채점표_v1.5.md ⑨적자깊이 — '완충이 외부 조달뿐이다 … "
                                              "Series H $30B($965B 밸류)에 기댄다'"},
        {"value": 65_000_000_000, "location": "AI기업_채점표_v1.5.md 비상장 ⑥ 표 — "
                                              "'$965B (2026/5 Series H $65B)'"},
    ],
    "same_document": True,
    "not_resolved": "**어느 쪽이 맞는지 정하지 않는다.** 두 표기가 같은 문서 안에서 갈리고 "
                    "외부 확인 경로가 이번 과제 범위 밖이다. $65B 는 anthropic 의 ARR 값과 같아 "
                    "표 작성 중 옮겨 적혔을 가능성도 있으나 그것도 추측이라 단정하지 않는다.",
}

# ---------------------------------------------------------------- 등록 대상
NEW_OBS: list[dict] = []


def add(cid, metric, value, *, unit, kind, status, basis, raw, note, missing_type=None,
        period=None, source_id=SRC):
    item = {
        "observation_id": f"{cid}.{metric}.priv31", "company_id": cid, "metric": metric,
        "value": value, "unit": unit, "as_of": AS_OF, "observed_at": OBSERVED_AT,
        "kind": kind, "source_id": source_id, "status": status, "basis": basis,
        "raw": raw, "note": note,
    }
    if missing_type:
        item["missing_type"] = missing_type
    if period:
        item["period"] = period
    NEW_OBS.append(item)


def build(obs_items: list[dict]) -> None:
    got = {(o["company_id"], o["metric"]): o for o in obs_items}

    def val(cid, metric):
        o = got.get((cid, metric))
        return None if o is None else o["value"]

    # ---------- P2 입력 : ps_ratio (밸류 ÷ TTM 보정 매출)
    add("anthropic", "ps_ratio", 30.0, unit="ratio", kind="estimate", status="legacy_unverified",
        basis={
            "formula": "post_money_valuation ÷ TTM 보정 매출",
            "estimate_range": [30.0, 39.0],
            "range_is_source_given": True,
            "derivation": "v1.5 원본이 TTM 추정 배수를 직접 준다 — '분모를 TTM으로 맞추면 약 30~39배"
                          "(Q2 매출 $10.9B 역산)'. 우리가 만든 값이 아니다.",
            "anchor": "Q2 매출 $10.9B. ARR $65B 런레이트를 그대로 나눈 14.8배가 아니라 "
                      "분기 실적에서 TTM 을 역산한 값이다.",
            "why_not_arr": "밸류÷ARR 은 14.8x 로 NVIDIA(17.9)보다 싸 보인다. 분모를 맞추면 30~39x 로 "
                           "Palantir(TTM P/S 66.2, ⑥-4)의 절반 수준이다(v1.5 654행).",
            "band_check": "30 과 39 가 모두 '30x+' 구간이라 범위가 판정을 가르지 않는다. "
                           "값으로는 낮은 끝 30 을 썼다 — 기업에 가장 덜 불리한 끝에서도 -4 라는 뜻이다.",
            "precision": "⚠️ 정밀도 열위. 비상장이라 NTM PER 산출 불가이고 경계 규칙도 미적용이다(v1.5 678행).",
            "source_lines": "AI기업_채점표_v1.5.md ⑥가격 항목 · AI기업_채점규칙_v1.5.md 649~654행",
        },
        raw="TTM 보정 ~30~39배 (밸류 $965B, Q2 매출 $10.9B 역산)",
        note="PRIV-IMPL-31 / C-12. **P2 분모는 arr 이 아니라 TTM 보정 매출이다.** "
             "구간 추정이라 estimate_range 를 함께 남겼고 계산기가 양 끝의 밴드를 확인한다")

    add("openai", "ps_ratio", 39.0, unit="ratio", kind="estimate", status="legacy_unverified",
        basis={
            "formula": "post_money_valuation ÷ TTM 보정 매출",
            "estimate_range": [39.0, 39.0],
            "range_is_source_given": True,
            "derivation": "v1.5 원본 — 'post-money $852B ÷ ARR $40B = 21.3배 — TTM 보정 시 약 39배'. "
                          "원본이 단일값으로 준다.",
            "why_not_arr": "밸류÷ARR 21.3x 는 런레이트 기준이라 과대 평가된다.",
            "precision": "⚠️ 정밀도 열위 · 경계 규칙 미적용.",
            "source_lines": "AI기업_채점표_v1.5.md ⑥가격 항목 · AI기업_채점규칙_v1.5.md 652행",
        },
        raw="TTM 보정 약 39배 (밸류 $852B)",
        note="PRIV-IMPL-31 / C-12. P2 분모는 TTM 보정 매출")

    # ---------- P3 입력 : arr_prior (신설)
    add("anthropic", "arr_prior", 47_000_000_000.0, unit="USD", kind="run_rate",
        status="legacy_unverified",
        basis={
            "period_label": None,
            "period_label_missing": "**원문에 직전 시점 라벨이 없다.** v1.5 는 'ARR이 $47B→$65B로 늘며 "
                                    "배수가 내려왔다' 고만 적고 $47B 가 언제 기준인지 말하지 않는다. "
                                    "지어내지 않고 null 로 둔다.",
            "current_label": "$65B 는 7월 기준이라고 원문이 적는다",
            "kind_note": "kind=run_rate. **ARR 이 아니라 런레이트다**(PRIV-ARR-17). 이름이 arr_prior 인 것은 "
                         "기존 12개사 관측·스키마와 얽혀 이름을 바꾸지 않기로 한 결과다.",
            "growth_implied": 65 / 47 - 1,
            "source_lines": "AI기업_채점표_v1.5.md anthropic ⑥가격 항목",
        },
        raw="ARR $47B → $65B (직전 런레이트)",
        note="PRIV-IMPL-31 / C-12. P3 입력. 시점 라벨이 원문에 없어 null 이다")

    add("openai", "arr_prior", 25_000_000_000.0, unit="USD", kind="run_rate",
        status="legacy_unverified",
        basis={
            "period_label": "2~4월 정체 구간",
            "current_label": "$40B 는 8/20 기준 — 다만 원문 안에서 시점 표기가 갈린다(아래 contradiction)",
            "kind_note": "kind=run_rate. ARR 이 아니라 런레이트다.",
            "growth_implied": 40 / 25 - 1,
            "contradiction": {
                "field": "openai arr 시점 라벨",
                "values": ["7월(2회 표기)", "8/20(2회 표기)"],
                "value_agrees": "금액 $40B 는 네 표기가 모두 같다",
                "not_resolved": "**시점을 고르지 않는다.** 값이 같아 P3·P2 에는 영향이 없고, "
                                "영향이 없다는 사실까지 적어 둔다.",
            },
            "source_lines": "AI기업_채점표_v1.5.md openai ⑥가격 항목",
        },
        raw="ARR $25B → $40B (2~4월 정체 구간)",
        note="PRIV-IMPL-31 / C-12. P3 입력. arr 시점 표기가 원문 안에서 갈리나 금액은 같아 점수 영향 없음")

    # ---------- C-20 : 결측 유형 등록
    #  MISS-LABEL-23 의 구조 기준 — 공시 의무가 없는 기업의 지표가 감사 재무제표 항목이거나
    #  그로부터만 도출되는 값이면 not_disclosed_confirmed 다. 재분류를 제안으로만 내고
    #  관측에 등록하지 않아 _g2 와 _g1 이 결측유형 미분류로 떨어졌다.
    STRUCTURAL = "비상장이라 공시 의무가 없고 이 지표는 감사 재무제표 항목이거나 그로부터만 도출된다 — 구조적으로 확인된 미공시"
    for cid in ("anthropic", "openai"):
        for metric, unit in (("fcf_ttm", "USD"), ("cash", "USD"),
                             ("net_cash", "USD"), ("debt_ebitda", "ratio")):
            old = got.get((cid, metric))
            add(cid, metric, None, unit=unit, kind="actual", status="not_disclosed",
                missing_type="not_disclosed_confirmed",
                basis={"reclassification_of": old["observation_id"] if old else None,
                       "criterion": STRUCTURAL,
                       "criterion_source": "MISS-LABEL-23 구조 기준 (validation/miss-label-23/reclassify.py "
                                           "AUDITED_STATEMENT_METRICS)",
                       "why_now": "재분류를 제안으로만 내고 관측에 등록하지 않아 _g2 와 _g1 이 "
                                  "'결측유형 미분류' 로 떨어졌다. C-20 이 그 자리에서 막혔다.",
                       "raw_was": (old or {}).get("raw")},
                raw=(old or {}).get("raw") or "미공시",
                note=f"PRIV-IMPL-31 / C-20. 승계 관측 {old['observation_id'] if old else '?'} 의 "
                     f"결측 유형을 등록한다. **값은 그대로 없다** — 라벨만 붙인다")

        # G1 이 읽을 영업손익 결측 유형. 관측 자체가 없어 새로 만든다.
        add(cid, "operating_margin_ttm", None, unit="ratio", kind="derived", status="not_disclosed",
            missing_type="not_disclosed_confirmed",
            basis={"criterion": STRUCTURAL,
                   "criterion_source": "MISS-LABEL-23 구조 기준",
                   "why_registered": "C-20 의 판정 근거다. **자료가 없다는 것만으로는 부족하고** "
                                     "구조적 미공시라는 라벨이 관측에 있어야 G1 이 판정 보류 후 "
                                     "비상장 경로로 보낸다. 라벨이 없으면 단순 pending 이다.",
                   "not_a_loss_claim": "**적자라고 단정하는 것이 아니다.** TTM 영업손익을 모른다는 뜻이고 "
                                       "단일 분기 영업흑자를 통과 근거로도 쓰지 않는다.",
                   "single_quarter_known": ("anthropic Q2 첫 영업흑자 $559M(매출 $10.9B, 마진 5%) — "
                                            "**분기 하나이고 TTM 이 아니다**" if cid == "anthropic" else
                                            "openai 2026 GAAP 손실 약 $60B 전망 · BEP 2030 — 전망이지 실적이 아니다")},
            raw="미공시 — 비상장이라 TTM 영업손익 공시 의무 없음",
            note="PRIV-IMPL-31 / C-20. G1 판정 보류의 근거 라벨. 통과도 실패도 아니다")

    # ---------- 모순 기록 : cumulative_raised 에 민감도
    anth_raised = val("anthropic", "cumulative_raised")
    anth_arr = val("anthropic", "arr")
    if anth_raised and anth_arr:
        delta = SERIES_H["values"][1]["value"] - SERIES_H["values"][0]["value"]
        scenarios = []
        for label, raised in (("원본 표기 그대로", anth_raised),
                              ("125B 가 Series H 를 65B 로 포함했다면 → 30B 로 교체", anth_raised - delta),
                              ("125B 가 Series H 를 30B 로 포함했다면 → 65B 로 교체", anth_raised + delta)):
            eff = anth_arr / raised
            scenarios.append({"assumption": label, "cumulative_raised": raised,
                              "capital_efficiency": round(eff, 4),
                              "meets_threshold_0_50": eff >= 0.50})
        add("anthropic", "cumulative_raised", float(anth_raised), unit="USD", kind="actual",
            status="legacy_unverified",
            basis={
                "contradiction": SERIES_H,
                "impact": "이 값이 P4 자본효율(arr ÷ cumulative_raised)의 분모다.",
                "sensitivity": scenarios,
                "straddles_threshold": True,
                "straddle_note": "**모순 구간이 보정 임계 0.50 을 가로지른다.** 세 시나리오의 자본효율이 "
                                 "0.41~0.72 이고 그중 하나(65B 포함 가정)만 임계 미달이다. "
                                 "그 경우 보정이 붙지 않아 anthropic F6 가 -3 이 아니라 -4 가 된다. "
                                 "**값을 고르지 않았고, 갈린다는 사실과 그 결과를 여기 남긴다.**",
                "registered_value_is": "원본이 자본효율 0.52 를 계산할 때 쓴 값(약 $125B, 2021년~) 그대로다. "
                                       "우리가 조정하지 않았다.",
            },
            raw="약 $125B(2021년~)",
            note="PRIV-IMPL-31 / C-12. 승계 관측 anthropic.cumulative_raised.v15 를 대체한다 — "
                 "**값은 같고 모순 기록과 민감도만 추가한다**")


def main() -> int:
    sys.path.insert(0, str(ROOT / "scripts"))
    from scorecard.rules import load_rules
    from scorecard.schema import load_json_strict, validate_observations, write_json

    registry = {c["company_id"]: c for c in load_json_strict(ROOT / "scorecard" / "companies.json")["companies"]}
    obs = load_json_strict(RUN / "observations.json")
    by_id = {o["observation_id"]: o for o in obs["items"]}

    bar = "=" * 112
    print(bar)
    print(f"PRIV-IMPL-31 — {RUN_ID} 에 비상장 C-12·C-20 입력 등록 (승인 실행 미변경 · 네트워크 없음)")
    print(bar)

    build(obs["items"])
    print(f"\n[1] 관측 {len(NEW_OBS)}건 등록")
    print(f"  {'회사':11} {'metric':22} {'값':>16} {'status':18} 결측유형")
    for item in NEW_OBS:
        v = "null" if item["value"] is None else f"{item['value']:,.6g}"
        print(f"  {item['company_id']:11} {item['metric']:22} {v:>16} {item['status']:18} "
              f"{item.get('missing_type', '-')}")
        obs["items"].append(item)

    # 승계 관측은 지우지 않고 대체 표시만 한다.
    print("\n[2] 승계 관측 대체 표시")
    for item in NEW_OBS:
        old_id = f"{item['company_id']}.{item['metric']}.v15"
        old = by_id.get(old_id)
        if old is None:
            continue
        if not str(old.get("note") or "").startswith("[PRIV-IMPL-31"):
            old["note"] = f"[PRIV-IMPL-31 대체됨 → {item['observation_id']}] " + (old.get("note") or "")
        print(f"  {old_id:44} → {item['observation_id']}")

    validate_observations(obs, registry, RUN_ID)

    # ---------------- run.decisions
    run = load_json_strict(RUN / "run.json")
    have = {d["id"] for d in run["decisions"]}
    for did, choice, why in (
            ("C-12", "p2_with_capped_promotion",
             "비상장 F6 는 P2 가 점수를 내고 P3·P4 가 합쳐서 최대 한 칸 올린다. P2 는 밸류÷TTM 보정 매출에 "
             "v1.5 비상장 구간표를 그대로 쓰고, 보정은 ARR 성장률 0.30 이상과 자본효율 0.50 이상을 "
             "둘 다 요구한다. 결과가 v1.5 발표 점수와 같다는 약점을 규칙 파일 private_correction.weakness 에 "
             "적어 두었다. 설계진행 2026-09-11 사용자 확정(d57e70e)."),
            ("C-20", "defer_to_private_g2",
             "비상장이고 TTM 영업손익이 구조적 미공시면 G1 을 통과시키지 않고 판정 보류로 둔 뒤 G2 비상장 "
             "경로로 보낸다. 단일 분기 영업흑자를 통과 근거로 쓰지 않고, 동시에 F9 를 영구 미완료로도 두지 "
             "않는다. 설계진행 2026-09-11 사용자 확정(d57e70e).")):
        if did not in have:
            run["decisions"].append({"id": did, "choice": choice, "rationale": why,
                                     "decided_by": "사용자", "decided_at": "2026-09-11"})
            print(f"\n[3] run.decisions 에 {did} = {choice} 추가")

    run["assumptions"] = list(run["assumptions"]) + [
        "비상장 2사의 F6·F9 입력은 v1.5 원본(AI기업_채점규칙_v1.5.md sha256 57beb84a… · AI기업_채점표_v1.5.md)에서 "
        "직접 읽었다. 선행 조사가 준 값도 원문 문장으로 다시 대조했다(validation/priv-impl-31/verify_private.py)",
        "anthropic 의 P2 배수는 원본이 구간(~30~39)으로 주므로 낮은 끝을 값으로 두고 estimate_range 를 남겼다. "
        "양 끝이 같은 밴드라 판정이 갈리지 않으며, 갈리는 경우 계산기가 값을 고르지 않고 보류한다",
        "anthropic Series H 조달액이 원본 안에서 $30B·$65B 로 갈린다. 값을 고르지 않았고 자본효율 민감도"
        "(0.41~0.72)를 관측 basis 에 남겼다. 이 구간이 보정 임계 0.50 을 가로지른다",
        "비상장 2사의 결측 유형은 MISS-LABEL-23 구조 기준으로 등록했다. 값은 그대로 없고 라벨만 붙였다",
    ]

    write_json(RUN / "observations.json", obs)
    write_json(RUN / "run.json", run)
    load_rules(run["rule_version"])
    print(f"\n[4] 저장 — 관측 {len(obs['items'])}건 · 결정 {len(run['decisions'])}건")
    print(f"    다음: python scripts/scorecard_cli.py calculate {RUN_ID}")
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    sys.exit(main())
