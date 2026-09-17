# FIX-61: 9차 재무 계산 재판정 반영 — FIX-59 가 만든 문면 모순 · 순손실 상장사 트랙 경로(C-28) · 기록 (점수 불변)
"""보존 원문만 읽는다. 신규 조회 없음.

- 9차 재판정 part: review-obsreg `reviews/_parts/ai-scorecard-2026-09-obsreg/financial-calc.md`

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
DATE = "2026-09-17"
M = "FIX-61"
R9 = "obsreg 9차 재무 계산 재판정(Claude 독립 세션)"


def load(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def dump(p: Path, d: dict) -> None:
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def find(items: list[dict], key: str, value: str) -> dict:
    hit = [x for x in items if x.get(key) == value]
    assert len(hit) == 1, f"{key}={value} 가 {len(hit)}건"
    return hit[0]


# ------------------------------------------------------------------ S1 C-06 문면

C06_SUMMARY_OLD = ("손실률 -10%·-30% 경계 중첩, FCF/영업손익 0, 완충 잠식, G2 안정/악화의 기계 정의 부재. "
                   "BEP 후퇴→-5 는 원문 OR 조건 그대로 활성(경고 표시)이며 손실률 경계와의 우선순위 명문화만 미결")
C06_SUMMARY_NEW = (
    "손실률 -10%·-30% 경계 중첩, FCF/영업손익 0, 완충 잠식, G2 안정/악화의 기계 정의 부재. "
    f"[{M} 정정 · {R9} medium] **BEP 후퇴의 우선순위는 더 이상 미결이 아니다** — 사용자 결정 2026-09-17 로 "
    "`policies.f9.g1_bep_retreat_precedence` 에 명문화했다(BEP 후퇴가 기록되면 손실률 밴드·C-20 비상장 경로보다 "
    "앞서 `g1_bep_retreat_score` 를 준다). 점수도 -5 가 아니라 **-4** 다(C-06 재척도). 남은 미결은 "
    "FCF·영업손익 0 처리와 완충 잠식·G2 추세의 기계 정의다")

BEP_ALSO_PRECEDES = (
    f"[{M} · {R9} medium] **손실률 밴드보다도 앞선다.** FIX-59 는 C-20 과의 순서를 적었지만 코드는 그 전에 "
    "`bep_retreat` 를 먼저 본다 — `margin` 값이 있어도 BEP 후퇴가 기록되면 밴드를 고르지 않는다. "
    "**다만 두 경로가 만나도 결과는 같다**: `g1_bep_retreat_score` -4 가 이미 `floor` 이고 "
    "`g1_bands_proposed` 의 가장 깊은 칸도 -4 라 어느 쪽을 먼저 보든 점수가 -4 다. 순서가 관측되지 않는다는 "
    "사실까지 적어 두어야 다음 사람이 이것을 열린 문제로 다시 들지 않는다.")


# ------------------------------------------------------------------ S2 순손실 상장사 트랙

LOSS_TRACK_NOTE = (
    f"[{M} · {R9} low · C-28 닫음] P1 은 **입력이 성립할 때만** 만든다. 순이익이 `requires_positive` 를 넘지 못하면 "
    "만들지 않고 결과 `calc.parameters_optional_unmet.P1` 에 사유를 적으며, **P2·P3 로 소계를 낸다.** "
    "전에는 P1 이 `missing` 으로 떨어져 이미 산출한 P2·P3 를 버리고 F6 전체가 `pending_data` 가 됐다 — "
    "같은 순손실이 `listed_newly` 에서는 소계가 나오고 여기서는 미완료가 되는 비대칭이었다. "
    "**이번 실행 점수는 바뀌지 않는다** — 두 트랙 상장 11개사의 순이익이 전부 양수다. "
    "**사유는 `requires_positive` 하나로 좁혔다**(`optional_parameters_causes`) — 순이익 관측이 아예 없는 것은 "
    "우리 수집 공백이라 예전처럼 factor 를 pending 으로 세운다. 순손실은 그 기업의 성질이고 결측은 우리 문제다.")

C28_CLOSE = {
    "status": "resolved",
    "chosen": "optional_parameters_for_all_listed_tracks",
    "decided_at": DATE,
    "decided_by": f"{R9} 지적 · 설계진행 지시({M})",
    "recommendation": (
        "`listed_ttm`·`listed_annual` 에도 `optional_parameters: [\"P1\"]` 을 두어 `listed_newly` 와 같은 경로로 만든다. "
        "순이익이 음수여서 P1 이 성립하지 않으면 사유를 `calc.parameters_optional_unmet.P1` 에 적고 P2·P3 로 소계를 낸다."),
    "implementation_status": {
        "verdict": "implemented",
        "checked_at": DATE,
        "checked_by": f"worker ({M})",
        "evidence": [
            "policies.f6.tracks.listed_ttm.optional_parameters = [P1] · listed_annual 도 같다",
            "calc_f6_params.compute_listed 의 선택 파라미터 경로가 그대로 P1 을 받는다(FIX-56 1단계 장치)",
            "합성 순손실 상장사 입력으로 소계가 P2·P3 로 나오고 pending_data 가 아닌 것을 단위 테스트로 고정했다",
            "이번 실행 11개사는 순이익이 전부 양수라 P1 이 그대로 산출된다 — 점수·상태 불변",
        ],
        "c24_scope_fix": ("선택 파라미터가 세 트랙으로 넓어지면서 C-24 분기가 범위 밖까지 끌 수 있었다. "
                          "C-24 는 신규 상장 트랙의 P2 만 가리키는 결정이므로 트랙·파라미터를 함께 보게 좁혔다."),
    },
    "remaining_question": (
        "**하나 남는다** — 순손실 상장사의 트랙 하한이다. `listed_ttm`·`listed_annual` 의 `floor` 는 -7 이고 "
        "P1 이 빠지면 소계 범위가 -5 까지로 좁아진다(P2 -2 + P3 -3). 하한이 그대로여도 절단이 일어나지 않아 "
        "점수는 같지만, `listed_newly` 가 P3 하나일 때 -3 이었던 것과 같은 성질의 물음이다 — **C-25 와 함께 본다.**"),
}


def fix_rules(rules: dict) -> list[str]:
    out: list[str] = []
    f9 = rules["policies"]["f9"]
    prec = f9["g1_bep_retreat_precedence"]
    if prec.get("also_precedes_loss_band") != BEP_ALSO_PRECEDES:
        prec["also_precedes_loss_band"] = BEP_ALSO_PRECEDES
        out.append("policies.f9.g1_bep_retreat_precedence: 손실률 밴드보다도 앞선다는 사실과 결과가 같다는 검산")

    c06 = find(rules["decisions"], "id", "C-06")
    if c06["summary"] == C06_SUMMARY_OLD:
        c06["summary"] = C06_SUMMARY_NEW
        out.append("decisions C-06: summary 의 `우선순위 명문화만 미결`·`-5` 정정 (나머지 미결은 그대로)")

    tracks = rules["policies"]["f6"]["tracks"]
    for tid in ("listed_ttm", "listed_annual"):
        t = tracks[tid]
        if t.get("optional_parameters") != ["P1"]:
            t["optional_parameters"] = ["P1"]
            out.append(f"tracks.{tid}: optional_parameters = [P1]")
        if t.get("optional_parameters_causes") != {"P1": ["requires_positive"]}:
            t["optional_parameters_causes"] = {"P1": ["requires_positive"]}
            out.append(f"tracks.{tid}: optional_parameters_causes = {{P1: [requires_positive]}}")
        if t.get("optional_parameters_note") != LOSS_TRACK_NOTE:
            t["optional_parameters_note"] = LOSS_TRACK_NOTE
            out.append(f"tracks.{tid}: optional_parameters_note")

    c28 = find(rules["decisions"], "id", "C-28")
    for key, value in C28_CLOSE.items():
        if c28.get(key) != value:
            c28[key] = json.loads(json.dumps(value)) if isinstance(value, dict) else value
            out.append(f"decisions C-28: {key}")
    c28.pop("pending_recheck", None)
    return out


# ------------------------------------------------------------------ S3 기록

ARR_PERIOD_NOTE = (
    f"[{M} · {R9} low] **`arr_growth` 의 기간이 미상이다.** 이 관측의 `period_label` 이 null 이고 v1.5 가 $47B 의 "
    "시점을 적지 않는다. 그래서 `anthropic.arr.v15`(7월 기준 $65B)와의 성장률 0.382979 가 **몇 개월치인지 알 수 없다.** "
    "지어내지 않는다 — 시점을 찍으면 그 순간 근거 없는 수가 된다. **지금은 점수에 닿지 않는다**: "
    "`private_correction` 의 승격 조건이 `kind: run_rate` 를 받지 않아(FIX-52) 이 값이 보정에 쓰이지 않기 때문이다. "
    "**그 제한이 풀리거나 진짜 ARR 이 들어오면 기간을 먼저 정해야 한다** — 연환산 성장률이 아니면 0.30 임계와 비교할 수 없다.")

C27_ORACLE_SAMPLE = (
    f" [{M} · {R9} low] **표본이 둘이 됐다.** oracle F6 P1 = 25.967109 로 밴드 경계 25 에서 **+3.87%** 이고, "
    "허용폭 3% 밖이라 경계 표시가 붙지 않는다. **이 한 칸이 oracle 총점 2 와 3 을 가른다** — P1 이 -1 대신 0 이면 "
    "F6 -3 → -2 이고 총점이 3 이 된다. alibaba G3(+3.32%)와 같은 성질이고 방향도 같다(둘 다 폭 바로 밖). "
    "폭을 정할 때 이 둘을 함께 본다.")

ORACLE_UNDRAWN_NOTE = (
    f"[{M} · {R9} low] **null 이 0 으로 세어진다.** `calc_f9._runway` 가 `undrawn or 0.0` 으로 받으므로 이 관측이 "
    "없는 것과 0 인 것이 런웨이에서 같아진다. **설계대로다** — C-04 가 완충을 `현금 + 확정 미인출 여신` 으로 좁혔고 "
    "확인되지 않은 여신을 넣지 않는 쪽이 보수적이다. **뒤집히려면 약 39.8B 이상이어야 한다**: 현재 런웨이 1.320991년"
    "(현금 31,289M ÷ 연 소진 23,686M)이고 임계 3년을 넘으려면 완충이 71,058M 이어야 해서 미인출 여신 39,769M 이 "
    "필요하다. oracle 은 미등록 아홉 곳 중 **유일하게 G3 가 점수를 내는 회사**라 이 크기를 적어 둔다.")


def fix_observations(doc: dict) -> list[str]:
    items = doc["items"]
    out: list[str] = []
    arr = find(items, "observation_id", "anthropic.arr_prior.priv31")
    if arr["basis"].get("period_unknown_blocks_growth") != ARR_PERIOD_NOTE:
        arr["basis"]["period_unknown_blocks_growth"] = ARR_PERIOD_NOTE
        out.append("anthropic.arr_prior.priv31: 성장률 기간 미상 — kind 제한이 풀리면 기간을 먼저 정한다")
    orc = find(items, "observation_id", "oracle.undrawn_credit.fix54")
    if orc["basis"].get("null_counts_as_zero") != ORACLE_UNDRAWN_NOTE:
        orc["basis"]["null_counts_as_zero"] = ORACLE_UNDRAWN_NOTE
        out.append("oracle.undrawn_credit.fix54: null 이 0 으로 세어지는 사실과 뒤집히는 크기(약 39.8B)")
    return out


def fix_rules_c27(rules: dict) -> list[str]:
    out: list[str] = []
    c27 = find(rules["decisions"], "id", "C-27")
    if C27_ORACLE_SAMPLE.strip() not in c27["recommendation"]:
        c27["recommendation"] = c27["recommendation"] + C27_ORACLE_SAMPLE
        out.append("decisions C-27: oracle P1(+3.87%)을 alibaba G3 와 함께 볼 표본으로")
    return out


RUN_C28 = {
    "id": "C-28",
    "choice": "optional_parameters_for_all_listed_tracks",
    "rationale": ("순손실 상장사의 F6 경로를 세 트랙에서 같게 한다 — `listed_ttm`·`listed_annual` 도 P1 을 선택 "
                  "파라미터로 두어 순이익이 음수면 P1 을 만들지 않고 P2·P3 로 소계를 낸다. 사유는 "
                  "`requires_positive` 하나로 좁혔다(결측은 예전처럼 pending). 규칙 v1.7 decisions C-28 resolved 를 "
                  f"실행 단위로 옮긴다. 이번 실행 11개사는 순이익이 전부 양수라 점수 불변. {M}."),
    "decided_by": f"{R9} 지적 · 설계진행 지시",
    "decided_at": DATE,
}


def fix_run(run: dict) -> list[str]:
    out: list[str] = []
    if not any(d["id"] == "C-28" for d in run["decisions"]):
        run["decisions"].append(json.loads(json.dumps(RUN_C28)))
        out.append("+ decisions C-28 (실행 단위로 옮김 — resolved 결정은 run.json 에 있어야 한다)")
    line = (f"[{M} · {R9}] 순손실 상장사의 F6 경로를 세 트랙에서 같게 했다 — `listed_ttm`·`listed_annual` 도 P1 을 "
            "선택 파라미터로 두어, 순이익이 음수면 P1 을 만들지 않고 사유를 적은 뒤 P2·P3 로 소계를 낸다"
            "(미결 C-28 닫음). **이번 실행 점수는 불변이다** — 두 트랙 상장 11개사의 순이익이 전부 양수라 "
            "P1 이 그대로 산출된다.")
    if line not in run["assumptions"]:
        run["assumptions"].append(line)
        out.append("+ assumptions 순손실 트랙 경로 통일과 점수 불변")
    return out


def main() -> int:
    registry = {c["company_id"]: c for c in load_json_strict(ROOT / "scorecard" / "companies.json")["companies"]}

    rules = load(RULES)
    rc = fix_rules(rules) + fix_rules_c27(rules)
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
