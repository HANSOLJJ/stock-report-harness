# IMPL-46 — 사용자 확정 4건 반영: F6 정본 parameters · C-13 reject_proxy · F2 [2,5] · openai F5 조달 배제 note
"""**조사가 아니라 결정 반영이다.** 점수는 한 칸도 안 바뀌어야 한다.

1. F6 엔진 정본 = `parameters`. `bands` 는 v1.5·v1.6 구버전, 실행 단위로만 선택. 코드는 안 지운다.
2. C-13 = `reject_proxy`. `ntm_per` 12건 basis 에 원천이 원천 정책 목록 어디에도 없다는 표시.
3. F2 range `[0,5]` → `[2,5]`. 근거는 **사다리 바닥이 2 이고 0·1 이 한 번도 안 나왔다**.
4. openai F5 판단에 Oracle $300B 조달 배제 note. A=+2 는 남은 근거로 선다.

사용:
    python validation/impl-46/apply_impl46.py     # 멱등
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
RUN = ROOT / "scorecard" / "runs" / "ai-scorecard-2026-09-obsreg"
RULES = ROOT / "scorecard" / "rules" / "v1.7.json"
DATE = "2026-09-14"

# alibaba·tsmc 는 원문이 StockAnalysis 값을 **버리고 직접 계산**했다 (✱ 표식).
AUTHOR_COMPUTED = {
    "alibaba": "StockAnalysis 값(13.92)이 CNY/USD 혼재라 버리고 FY27 $5.71·FY28 $8.03 을 7:5 가중해 직접 "
               "계산 (HANDOVER 39행 · 채점표 400행)",
    "tsmc": "StockAnalysis 가 TWD/USD 혼재라 버리고 NTM EPS 653 TWD ÷ 30.5 로 직접 계산 "
            "(HANDOVER 39행 · 채점표 239행)",
}


def load(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def dump(p: Path, obj) -> None:
    raw = p.read_text(encoding="utf-8")
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + ("\n" if raw.endswith("\n") else ""),
                 encoding="utf-8")


def main() -> int:
    rules = load(RULES)
    f6 = rules["policies"]["f6"]

    # ---------------------------------------------------------------- 1. F6 정본
    f6["canonical_mode"] = {
        "mode": "parameters",
        "decided_at": DATE,
        "decided_by": "사용자",
        "statement": "**F6 엔진 정본은 `parameters` 다.** P1 PER · P2 EV/Sales · P3 매출성장률 · P4 입력신뢰도.",
        "legacy_mode": {
            "mode": "bands",
            "what": "NTM PER 단일 구간표. v1.5·v1.6 규칙 파일의 `policies.f6.bands`.",
            "status": "**구버전.** 과거 실행을 재현하려고 코드와 검증을 남긴다. `run.json.rule_version` 으로 "
                      "v1.5·v1.6 을 고른 실행 단위에서만 선택된다. v1.7 이후 새 실행의 정본이 아니다.",
            "do_not_delete": "코드를 지우지 않는다 — 승인된 v1.5 실행(ai-scorecard-2026-09-baseline)이 이 경로로 "
                             "계산됐고 해시가 그 결과에 묶여 있다.",
        },
        "why": "무료·허용 원천 중 12개사 전부에 향후 4개 분기 컨센서스를 같은 기준으로 주는 곳이 없어 NTM PER 을 "
               "유지할 수 없다(F6H-BATCH-10·AV-SOURCE-11, F6-SPEC-18).",
    }

    # ---------------------------------------------------------------- 2. C-13
    dec = {x["id"]: x for x in rules["decisions"]}["C-13"]
    dec["status"] = "resolved"
    dec["chosen"] = "reject_proxy"
    dec["decided_at"] = DATE
    dec["decided_by"] = "사용자"
    dec["confirmed_model"] = {
        "mapping": "연간 EPS 가중 근사를 NTM 으로 쓰지 않는다. 4개 연속 미발표 분기 컨센서스만 NTM 이다.",
        "reasons": [
            "**종류가 다른 값이다.** 연간 둘을 남은 개월로 선형 안분한 것은 분기 컨센서스 넷의 합이 아니다. "
            "이름이 같다고 같은 수가 아니다.",
            "**accept_proxy_with_flag 를 골라도 채점되지 않는다.** v1.7 F6 정본(parameters)이 NTM PER 을 읽지 "
            "않으므로 근사를 받아들여도 쓸 자리가 없다.",
            "**환율 하나로 밴드가 갈린다.** tsmc 근사 19.4 는 20선에서 -3% 이고 TWD 환율 하나로 -1 이 가능하다"
            "(채점표 239행 · HANDOVER 39행). 근사가 경계를 가르는 값을 만든다.",
        ],
        "what_changed": "선택만 확정했다. 점수는 안 바뀐다.",
    }
    dec["superseded_choice"] = {
        "name": "accept_proxy_with_flag",
        "why_not": "근사임을 표시해도 종류가 다른 값이라는 사실이 안 바뀌고, parameters 정본에서는 쓰일 자리도 없다.",
    }
    dec["scope"] = {
        "what_this_is": "**bands 모드에서만 효력이 있다.** F6 정본이 parameters 라 v1.7 이후 실행의 점수에는 "
                        "닿지 않는다. v1.5·v1.6 을 고른 실행에서 NTM PER 근사를 받지 않는다는 뜻이다.",
        "score_impact": "없다.",
    }
    dec.pop("pending_recheck", None)

    # ---------------------------------------------------------------- 3. F2 range
    f2 = rules["factors"]["F2"]
    f2["range"] = [2, 5]
    f2["range_note"] = (
        "**`[2,5]` 다(사용자 확정 2026-09-14, PROPOSAL 안1).** 근거는 둘이다 — (1) **사다리 바닥이 2 다.** 경로 "
        "0개가 이미 최소이고 그 칸이 2점이라 경로 수 모델은 0·1 을 만들 수 없다. (2) **14개사에서 0·1 이 한 번도 "
        "나오지 않았다** — F2 뿐 아니라 다섯 과점 factor 어디에서도. 쓸 수 없는 칸을 범위에 두는 것이 어긋남이었다. "
        "| **F3 전례가 근거가 아니다.** F3 `[1,5]` 도 실측 최저가 2 라 자기 1점 칸을 못 쓰고 있어 정리된 자리가 "
        "아니라 같은 종류의 미정리 상태다(별건). | 이전 값 `[0,5]` 는 채점규칙 17행 `과점 factor 5개 — 각 0~5점` "
        "의 일괄 선언에서 왔다. | 합계 산식은 range 를 쓰지 않는다(aggregate.py 는 점수 합) — 범위 변경이 총점에 "
        "닿지 않는다.")
    dec03 = {x["id"]: x for x in rules["decisions"]}["C-03"]
    dec03["range_change"] = {
        "from": [0, 5], "to": [2, 5], "decided_at": DATE,
        "why": "사다리 바닥 2 · 14개사 0·1 실측 0회. F3 전례가 아니다.",
    }
    dump(RULES, rules)

    # ---------------------------------------------------------------- 2b. ntm_per 관측 basis
    obs = load(RUN / "observations.json")
    policy_lists = ["allowed", "denied", "not_adopted", "unlisted"]
    stamped = []
    for o in obs["items"]:
        if o["metric"] != "ntm_per":
            continue
        basis = dict(o.get("basis") or {})
        cid = o["company_id"]
        if cid in AUTHOR_COMPUTED:
            basis["source_vendor"] = "author_computed"
            basis["vendor_value_rejected"] = AUTHOR_COMPUTED[cid]
            basis["method"] = "annual_eps_weighted_proxy"
            basis["is_the_proxy_c13_rejects"] = ("**C-13 이 거부한 바로 그 근사다.** 연간 EPS 둘을 남은 개월로 "
                                                 "안분했다. 값은 남기되 NTM 으로 쓰지 않는다.")
        else:
            basis["source_vendor"] = "StockAnalysis"
            basis["source_field"] = "Forward PE"
        basis["vendor_not_in_source_policy"] = True
        basis["vendor_policy_check"] = (
            f"StockAnalysis 는 v1.7 원천 정책 **네 목록**({' · '.join(policy_lists)}) 어디에도 없다. "
            "허용도 금지도 미채택도 미등재 검토도 된 적 없는 원천이다(IMPL-46, 2026-09-14 확인).")
        basis["vendor_source_text"] = "채점규칙 629행 · HANDOVER 39행 · 채점표 794행"
        basis["not_read_by_engine"] = "F6 정본 parameters 가 ntm_per 를 읽지 않는다 — 점수에 닿지 않는다."
        o["basis"] = basis
        stamped.append((cid, basis["source_vendor"]))
    dump(RUN / "observations.json", obs)

    # ---------------------------------------------------------------- 4. openai F5
    jud = load(RUN / "judgments.json")
    j = next(x for x in jud["items"] if x["judgment_id"] == "openai.F5")
    marker = "[IMPL-46]"
    base_note = (j.get("note") or "").split(" | " + marker)[0]
    j["note"] = (base_note + " | " + marker + " **별표 G 조달 배제를 적용했다(사용자 확정 2026-09-14).** "
                 "A=+2 근거에서 **Oracle $300B 컴퓨트 계약을 뺀다** — 사는 쪽의 조달이고 동맹이 아니다. "
                 "**점수는 그대로 2 다**(3 + A +2 + H -3). 남는 A 근거: Amazon $50B 지분 투자 · SoftBank(Stargate 40%) · "
                 "Stargate LLC 공동 지분 · Broadcom Jalapeño 공동개발 · 미 국방부 CDAO 계약(4사 공통이라 변별력 없음). "
                 "**구분 주의 — Oracle 의 Stargate $7B 지분은 동맹으로 남는다.** 빠지는 것은 $300B 계약이지 Oracle "
                 "전체가 아니다. | 근거 셋: (1) 별표 G 197행 `조달 ≠ 동맹 — 돈 주고 사오는 관계는 아군이 아니다` "
                 "(2) 같은 규칙을 Apple 행에 적용 — 221행 `Gemini 연 $1B는 조달이라 불인정(별표 H)` "
                 "(3) 채점표 759행이 이미 `Oracle $300B 컴퓨트 계약 자체는 사는 쪽의 조달이라 동맹 근거가 아니다` 라고 "
                 "적는다. | **체크리스트 19(받은 투자)는 반영하지 않았다** — C-13 워크트리에서 별표 G A 기준 재판정이 "
                 "돌고 있고 결과에 따라 anthropic·openai F5 가 바뀔 수 있다.")
    dump(RUN / "judgments.json", jud)

    print("1. policies.f6.canonical_mode = parameters")
    print("2. C-13 resolved · reject_proxy · ntm_per 관측", len(stamped), "건 basis 표시")
    for cid, v in stamped:
        print(f"     {cid:11} {v}")
    print("3. F2 range =", rules["factors"]["F2"]["range"])
    print("4. openai.F5 note 추가 (inputs A/H 불변:", j["inputs"], ")")
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    sys.exit(main())
