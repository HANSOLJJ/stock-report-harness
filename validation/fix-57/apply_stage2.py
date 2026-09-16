# FIX-57 2단계: 6차 리뷰 A 분담 반영 — 긴장 등록 범위 · 결측 라벨 정리 · 결측 요건의 규칙 등재 (점수 불변)
"""보존 원문만 읽는다. 신규 조회 없음.

- anthropic·openai 보도자료 `ffaf318:validation/priv-arr-17b/_raw/…` (계약 수입 부재 재검색)
- 결측 구조 기준 `validation/miss-label-23/reclassify.py` (규칙으로 옮긴다)

재실행해도 같은 결과가 나온다. 파일은 LF 로 쓴다.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard.rules import load_rules  # noqa: E402
from scorecard.schema import load_json_strict, validate_observations, validate_rules, validate_run  # noqa: E402

RUN_ID = "ai-scorecard-2026-09-obsreg"
RUN = ROOT / "scorecard" / "runs" / RUN_ID
RULES = ROOT / "scorecard" / "rules" / "v1.7.json"
DATE = "2026-09-16"
M = "FIX-57 2단계"
REVIEW_A = "obsreg 6차 리뷰 A 분담(Claude 독립 세션 · 부재 주장 전수·Q23)"


def load(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def dump(p: Path, d: dict) -> None:
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def find(items: list[dict], key: str, value: str) -> dict:
    hit = [x for x in items if x.get(key) == value]
    assert len(hit) == 1, f"{key}={value} 가 {len(hit)}건"
    return hit[0]


# ------------------------------------------------------------------ S1 긴장 등록 범위

RA4_JUDGMENTS = ["anthropic.F2", "meta.F2", "alibaba.F2", "openai.F2"]
RA4_SUBJECT = ("F2 근거란이 모델 간 성능을 비교하면서 어느 하네스로 잰 값인지 적지 않는다 — "
               "채점규칙 22행 `비교는 같은 하네스끼리만` 을 확인할 수 없다")
RA4_DIRECTION = (
    "하향 가능. anthropic 은 `Opus 5 ARC-AGI-3 30.2%` 가 ②5 를 받치는 자리라 **5 → 4** 가 걸린다(C-03 세대 격차 기준). "
    f"[{M} 범위 확대] meta·alibaba·openai 는 해당 줄이 경로 판정의 유일한 근거가 아니라 점수 경로가 더 멀지만, "
    "같은 잣대를 댄 이상 재검토 대상도 같아야 한다. **이 등록은 재판정하지 않는다** — 점수 넷 다 그대로다.")
RA4_RECHECKER = (
    "**anthropic.F2 는 비 Claude 세션이 재판정한다** — Anthropic 점수이고 채점규칙 384행이 제3자 재검토를 약속한 "
    f"바로 그 자리다. [{M} · {REVIEW_A} medium] **나머지 셋은 그 제약이 필요 없다** — meta·alibaba 는 Anthropic 과 "
    "이해관계가 없고, openai 는 경쟁사라 하향 판정에 이해상충이 있으나 이 긴장의 방향이 하향이라 자사 유리로 기울 "
    "여지가 없다(TEN-RA3-01 이 openai.F4 를 권장으로 둔 것과 같은 판단이다). 셋은 2026-11 재채점 때 판단자가 본다.")
RA4_AFFECTED = [
    {"company_id": "meta", "judgment_id": "meta.F2",
     "why": ("`Tau3-Bench Banking 52%로 전 모델 1위` 가 여러 모델을 한 줄에 세우는데 채점표 264행 원문에 하네스 표기가 없다. "
             "성능 경로 ✅ 를 받치는 여러 줄 중 하나라 이 줄 하나로 경로가 뒤집히지는 않는다."),
     "source_lines": ["채점표 264행", "채점규칙 22행"]},
    {"company_id": "alibaba", "judgment_id": "alibaba.F2",
     "why": ("`HLE 43.6%로 프론티어 미달` 이 프론티어 모델과의 비교인데 채점표 375행 원문에 하네스 표기가 없다. "
             "**미달 판정 쪽이라 방향이 자사에 유리하지 않다.** 943행 지표 표도 모델별 수치만 적는다."),
     "source_lines": ["채점표 375행", "채점표 943행", "채점규칙 22행"]},
    {"company_id": "openai", "judgment_id": "openai.F2",
     "why": ("`FrontierMath Tier 4 v2 97.6%(Fable 5.1 87.8%)` 는 **한 줄에서 두 모델을 직접 비교**하는데 채점표 732행 "
             "원문에 하네스 표기가 없다. 같은 근거란의 ARC-AGI-3 줄은 `표준 하네스 62.7%` 로 적어 두 줄의 기준이 다르다."),
     "source_lines": ["채점표 732행", "채점규칙 22행"]},
]
RA4_NOTE_ADD = (
    f" [{M} · {REVIEW_A} medium] **근거란 표기만으로는 AGENTS.md 71행의 승계 판단 예외가 서지 않는다** — 예외는 "
    "`규칙 파일 open_tensions 에 재검토 시점과 함께 등록` 을 요구한다. FIX-56 2단계가 meta·alibaba·openai 의 F2 "
    "근거란에 같은 표기를 대고도 긴장에는 anthropic 하나만 두어 재검토 시점 없는 fail 이 셋 남았다. 셋을 이 긴장의 "
    "judgment_ids 에 넣고 회사별 사유를 affected 에 적는다. 재판정 주체의 차이는 rechecker 에 있다.")


def fix_rules(rules: dict) -> list[str]:
    out: list[str] = []
    t = find(rules["open_tensions"], "id", "TEN-RA4-01")
    if t["judgment_ids"] != RA4_JUDGMENTS:
        t["judgment_ids"] = list(RA4_JUDGMENTS)
        out.append("TEN-RA4-01: judgment_ids 에 meta.F2·alibaba.F2·openai.F2 추가")
    for key, value in (("subject", RA4_SUBJECT), ("direction", RA4_DIRECTION), ("rechecker", RA4_RECHECKER)):
        if t[key] != value:
            t[key] = value
            out.append(f"TEN-RA4-01: {key}")
    if t.get("affected") != RA4_AFFECTED:
        t["affected"] = json.loads(json.dumps(RA4_AFFECTED))
        out.append("TEN-RA4-01: affected 세 건(회사별 사유·원문 행)")
    # 비 Claude 재판정은 anthropic.F2 하나에만 걸린다 — 갈래 선언을 그 사실에 맞춘다(FIX-56 2단계 구조).
    if t.get("third_party_recheck") != "partial":
        t["third_party_recheck"] = "partial"
        out.append("TEN-RA4-01: third_party_recheck committed → partial")
    if t.get("third_party_scope") != ["anthropic.F2"]:
        t["third_party_scope"] = ["anthropic.F2"]
        out.append("TEN-RA4-01: third_party_scope = [anthropic.F2]")
    if RA4_NOTE_ADD.strip() not in t.get("note", ""):
        t["note"] = t.get("note", "") + RA4_NOTE_ADD
        out.append("TEN-RA4-01: note 에 범위 확대 사유")

    if rules["policies"].get("missing_types") != MISSING_TYPES_POLICY:
        rules["policies"]["missing_types"] = json.loads(json.dumps(MISSING_TYPES_POLICY))
        out.append("policies.missing_types: `확인된 미공시` 성립 요건을 규칙으로 (schema 가 관측에서 검사)")
    return out


# ------------------------------------------------------------------ S4 결측 요건

MISSING_TYPES_POLICY = {
    "note": (f"[{M} · {REVIEW_A} medium] `not_disclosed_confirmed` 는 C-16 으로 **G4 에서 한 칸을 깎는다.** "
             "그런데 성립 요건이 `validation/miss-label-23/reclassify.py` 안에만 있어 규칙만 읽어서는 확인할 수 없었다. "
             "여기 선언하고 `schema.validate_observations` 가 관측마다 검사한다 — 선언만 두면 C-11 과 같은 형태가 된다."),
    "not_disclosed_confirmed": {
        "why": ("`우리가 못 찾았다` 와 `공개된 적이 없다` 는 다르다. 뒤의 것만 기업 위험으로 셀 수 있다. "
                "애매하면 `unverified` 다 — 승격 금지."),
        "source": "MISS-LABEL-23 구조 기준(설계진행 확정 문구) · validation/miss-label-23/reclassify.py classify()",
        "routes": {
            "structural": {
                "applies_to": "unlisted",
                "metrics": ["revenue_ttm", "revenue_ttm_prior", "operating_income_ttm", "net_income_ttm",
                            "ocf_ttm", "capex_ttm", "cash", "undrawn_credit", "net_borrowing_ttm",
                            "fcf_ttm", "net_cash", "debt_ebitda", "operating_margin_ttm", "nonop_share",
                            "runway_years", "contracted_revenue", "offbalance_B"],
                "why": ("감사 재무제표를 제출할 의무가 없는 기업의 재무제표 항목(과 그로부터만 도출되는 값)은 "
                        "**정의상 공개된 적이 없다.** 근거는 우리의 탐색량이 아니라 구조다. "
                        "**상장사에는 이 논거가 성립하지 않는다** — 정기보고서에 있을 수 있다."),
            },
            "issuer_declared": {
                "applies_to": "any",
                "required_basis_keys": ["statement", "location"],
                "why": ("발행사가 제출본에서 **공시하지 않는다고 스스로 밝힌** 경우다(예: ASC 606 실무적 간편법 선언). "
                        "그 문면(`statement`)과 위치(`location`)를 관측 basis 에 인용해야 한다. "
                        "상장사가 이 라벨을 받을 수 있는 유일한 길이다."),
                "example": "alibaba.contracted_revenue.obsreg25 — 20-F Note 2(g) 실무적 간편법 선언",
            },
        },
        "otherwise": "unverified — 개념상 값이 없으면 not_applicable, 선행 입력 결측이면 indeterminate 가 먼저다.",
        "consumers": ["calc_f9._g4 → C-16 한 칸 강등", "calc_f9._g2 비상장 경로(C-20)", "calc_f6_params._blocked_reasons 표시"],
    },
}


# ------------------------------------------------------------------ S3 비상장 계약 수입 라벨

PRIVATE_CONTRACTED = {
    "anthropic": {"arr": 65000000000.0, "arr_obs": "anthropic.arr.v15", "raw_was": "ARR $65B — 계약 수입 아님(C-07)"},
    "openai": {"arr": 40000000000.0, "arr_obs": "openai.arr.v15", "raw_was": "ARR $40B — 계약 수입 아님(C-07)"},
}
G4_ROUTE = {
    "anthropic": ("G4 는 `coverage_comparable=no` 로 **C-07 비교 불가**에서 먼저 멈춘다(계약 수입과 컴퓨트 약정의 기간·범위가 "
                  "다르다). 그 뒤 C-20 경로가 `no_extra_penalty_because` 로 G2 에서 이미 깎은 같은 미공시 사유의 중복 감점을 "
                  "막는다. **C-16 한 칸 강등에 닿지 않는다.**"),
    "openai": ("G1 이 BEP 후퇴로 이미 하한 -4 라 **G3·G4 를 통째로 건너뛴다.** 이 라벨이 읽히는 자리가 없다."),
}


def fix_observations(doc: dict) -> list[str]:
    items = doc["items"]
    out: list[str] = []

    for cid, spec in PRIVATE_CONTRACTED.items():
        o = find(items, "observation_id", f"{cid}.contracted_revenue.v15")
        if o["value"] is None and o.get("missing_type") == "not_disclosed_confirmed":
            continue
        o["value"] = None
        o["status"] = "not_disclosed"
        o["missing_type"] = "not_disclosed_confirmed"
        o["raw"] = "미공시 — 비상장이라 계약 수입(ASC 606 잔여 수행의무)을 제출할 의무가 없다"
        o["basis"] = {
            "criterion": "비상장이라 공시 의무가 없고 이 지표는 감사 재무제표 주석 항목이다 — 구조적으로 확인된 미공시",
            "criterion_source": "rules.policies.missing_types.not_disclosed_confirmed.routes.structural",
            "label_meaning": ("**구조적 미공시**다. `회사가 어디에도 공개하지 않았다` 는 확인이 아니라 "
                              "`제출 의무가 없어 이 형태의 수치가 존재한 적이 없다` 는 뜻이다."),
            "value_moved": {
                "was": {"status": "incompatible_basis", "value": spec["arr"], "raw": spec["raw_was"]},
                "why": (f"[{M} · {REVIEW_A} medium] **계약 수입 칸에 ARR 이 들어 있었다.** 지표와 값이 어긋나고, "
                        "`incompatible_basis` 라벨이 부재 판정 앞에서 멈춰 결측 유형이 붙지 않았다. "
                        f"같은 값은 `{spec['arr_obs']}` 에 이미 있으므로 여기서는 지우고 부재로 세운다."),
                "same_value_lives_in": spec["arr_obs"],
                "c07_still_holds": ("ARR 과 컴퓨트 약정의 기간·범위가 다르다는 C-07 판정은 그대로다 — 그 사실은 판단 입력 "
                                    f"`{cid}.F9.inputs.coverage_comparable = no` 와 `{cid}.offbalance_B.v15` 가 담는다. "
                                    "이 관측이 값을 들고 있을 이유가 아니었다."),
            },
            "score_path": G4_ROUTE[cid],
            "checked_scope": {
                "preserved_release": ("보존 보도자료 전문(태그를 걷은 본문)에서 `remaining performance obligation` · "
                                      "`performance obligation` · `unsatisfied performance` · `backlog` · `contracted` · "
                                      "`committed revenue` **전부 0건**이고 `RPO` 도 단어 경계로 0건이다"
                                      "(부분 문자열 `rpo` 는 `purpose`·`corporation` 안에서만 잡힌다 — 단어로는 없다). "
                                      "ffaf318:validation/priv-arr-17b/_raw/. 공개된 수치는 조달액·밸류·run-rate·매출뿐이다."),
                "not_searched": "감사 재무제표(제출 의무가 없어 보존본 없음) · 투자설명 자료 · 언론 보도 — 새로 받지 않았다(외부 조회 규칙).",
            },
            "recorded_at": DATE,
            "review": f"{REVIEW_A} medium",
        }
        out.append(f"{cid}.contracted_revenue.v15: ARR 값을 빼고 부재(not_disclosed_confirmed)로 — 값은 {spec['arr_obs']} 에 있다")

    # S4 spacex-xai 기준 불일치 사유를 현재 사실로
    note_new = (
        "S-1/A 감사 손익계산서 FY2025 + 10-Q 2026 상반기 - 10-Q 2025 상반기. **매출 쌍(분기)과 기준이 다르다.** "
        f"[{M} 사유 갱신 · {REVIEW_A} low] 전에는 `listed_newly 트랙은 매출과 손익을 함께 쓰는 계산(P2)을 하지 않으므로` "
        "라고 적었는데 **C-24 가 그 트랙에 P2 를 넣었다.** 결론은 그대로다 — P2 의 입력은 시총·순현금·**매출**이라 "
        "손익을 읽지 않고(`policies.f6.parameters.P2.inputs`), 손익을 읽는 P1 은 순이익이 음수라 이 트랙에서 성립하지 "
        "않는다(`calc.parameters_not_in_track.P1`). P4 의 `nonop_share` 도 세전이익이 음수라 산출되지 않는다. "
        "**기준이 섞여 계산되는 자리는 여전히 없다.**")
    for metric in ("operating_income_ttm", "net_income_ttm"):
        o = find(items, "observation_id", f"spacex-xai.{metric}.f6reg28")
        if o["basis"].get("basis_mismatch_note") != note_new:
            o["basis"]["basis_mismatch_note"] = note_new
            out.append(f"spacex-xai.{metric}.f6reg28: 기준 불일치 사유를 C-24 이후 사실로")

    # S4 alibaba `확인된 미공시` 가 어느 경로로 서는지
    ali = find(items, "observation_id", "alibaba.contracted_revenue.obsreg25")
    route = (f"[{M} · {REVIEW_A} low] 이 라벨은 **발행사 선언 경로**로 선다"
             "(`rules.policies.missing_types.not_disclosed_confirmed.routes.issuer_declared`). "
             "상장사는 구조 기준이 성립하지 않으므로 이 경로뿐이고, 요건인 `statement`·`location` 이 이 basis 에 있다. "
             "요건이 규칙 밖(수집 스크립트)에만 있던 것을 이번에 규칙으로 옮겼고 스키마가 관측마다 검사한다.")
    if ali["basis"].get("label_route") != route:
        ali["basis"]["label_route"] = route
        out.append("alibaba.contracted_revenue.obsreg25: 라벨이 어느 경로로 서는지 명시")
    return out


def fix_run(run: dict) -> list[str]:
    out: list[str] = []
    line = (f"[{M} · {REVIEW_A} medium] 비상장 2사의 **계약 수입은 부재**다(`not_disclosed_confirmed`, 구조 기준). "
            "전에는 그 칸에 ARR 이 값으로 들어 있어 지표와 값이 어긋났다 — ARR 은 `anthropic.arr.v15`·`openai.arr.v15` 에 "
            "그대로 있고 F6 비상장 P2 가 그것을 읽는다. G4 는 anthropic 이 C-07 비교 불가·C-20 중복 방지로, "
            "openai 가 G1 하한으로 막혀 **두 회사 모두 C-16 한 칸 강등에 닿지 않는다.** 점수 불변.")
    if line not in run["assumptions"]:
        run["assumptions"].append(line)
        out.append("+ assumptions 비상장 계약 수입 라벨과 점수 경로")
    return out


def main() -> int:
    registry = {c["company_id"]: c for c in load_json_strict(ROOT / "scorecard" / "companies.json")["companies"]}

    rules = load(RULES)
    rc = fix_rules(rules)
    validate_rules(rules)
    dump(RULES, rules)
    policy = load_rules("v1.7").payload["policies"].get("missing_types")

    doc = load(RUN / "observations.json")
    oc = fix_observations(doc)
    validate_observations(doc, registry, RUN_ID, missing_policy=policy)
    dump(RUN / "observations.json", doc)

    run = load(RUN / "run.json")
    runc = fix_run(run)
    run["rule_hash"] = load_rules("v1.7").hash
    validate_run(run, RUN_ID)
    dump(RUN / "run.json", run)

    for title, items in (("규칙", rc), ("관측", oc), ("실행", runc)):
        print(f"{title} 변경 {len(items)}")
        for c in items:
            print("  " + c)
    print("rule_hash", run["rule_hash"][:12])
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    sys.exit(main())
