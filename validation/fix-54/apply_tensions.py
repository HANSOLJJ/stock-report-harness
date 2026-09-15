# FIX-54 1단계 S4·S6: alibaba F9 옛 점수 문구 정정과 3차 리뷰 C·B 가 짚은 승계 판단 긴장 등록 — 점수 불변
"""보존 원문(E:/…/AI_company_analysis_factor 의 채점규칙·채점표 v1.5)의 행 번호를 직접 대조해 적었다. 신규 조회 없음.

- S4 alibaba.F9.obsreg25: 활성 근거 `그러나 -2 유지` 는 v1.5 점수 문구다. 줄은 지우지 않고 superseded 표시와 현재 -3 경로를 붙인다.
- S6 open_tensions: TEN-RC3-01(anthropic·openai F7) · TEN-RC3-03(palantir·oracle F1) · TEN-RC3-04(tesla F5·F8) ·
  TEN-RC3-05(alibaba F3) 신규, TEN-RB-Q10 보강(oracle.F3 affected · microsoft 비교 후보 note). C-09 에 재검토 시점.
- openai.F7 note 의 `환류 여부 원문 없음` 을 정정한다(채점표 662행이 원문 후보). 입력 복원은 판단이라 하지 않는다.

지시서 행 번호와 보존 원문이 다른 곳은 원문 행을 적었다 — F7 매트릭스 321~322행(지시 322~323), v1.5 판정표 OpenAI·Anthropic -1 행 338행(지시 336).
재실행해도 같은 결과가 나온다. 파일은 LF 로 쓴다.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard.rules import load_rules  # noqa: E402
from scorecard.schema import load_json_strict, validate_judgments, validate_rules, validate_run  # noqa: E402

RUN_ID = "ai-scorecard-2026-09-obsreg"
RUN = ROOT / "scorecard" / "runs" / RUN_ID
RULES = ROOT / "scorecard" / "rules" / "v1.7.json"
DATE = "2026-09-15"
MARKER = "FIX-54 1단계"
REVIEW_C = "obsreg 3차 리뷰 C(Codex 독립 세션, 기준 커밋 04439f7 · review 169ca10)"
REVIEW_B = "obsreg 3차 리뷰 B(Codex 독립 세션, 기준 커밋 04439f7 · review 2c56e9f)"
CARRIED = "승계 판단의 기존 논리이고 이번 실행이 이 factor 의 잣대를 바꾸지 않았다. 재검토 시점과 함께 등록했으므로 AGENTS.md 리뷰 범위 — 승계 판단 예외에 해당한다."


def load(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def dump(p: Path, d: dict) -> None:
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def fix_judgments(jud: dict) -> list[str]:
    by = {j["judgment_id"]: j for j in jud["items"]}
    changed = []

    f9 = by["alibaba.F9.obsreg25"]
    old = "그러나 -2 유지: CapEx RMB 67,678M(+75%)로 FCF -$6.6B"
    if old in f9["evidence"]:
        i = f9["evidence"].index(old)
        f9["evidence"][i] = (f"~~그러나 -2 유지~~ (superseded [{MARKER}] — v1.5 점수 문구다. 이번 실행 점수는 -3): "
                             "CapEx RMB 67,678M(+75%)로 FCF -$6.6B")
        f9["evidence"].insert(i + 1, (
            f"📐 [{MARKER}] **현재 점수 -3 의 경로** — G1 통과(FY2026 영업이익률 +4.899%) → G2 TTM FCF US$-7,226M"
            "(2025-04-01~2026-03-31, alibaba.fcf_ttm.cashfcf35 — 위 줄의 -$6.6B 는 v1.5 서술이다)이라 -2 → G3 런웨이 3.10년"
            "(현금 US$19,068M + 확정 미인출 여신 US$3,330M = 22,398M ÷ 7,226M, alibaba.cash.cashfcf35 · alibaba.undrawn_credit.fix53). "
            "임계 3년 이상이라 추가 강등 0이고 거리 +3.3% 는 경계 허용폭 ±3% 밖이다 → G4 계약 수입이 확인된 미공시"
            "(not_disclosed_confirmed)라 C-16 실행 결정으로 한 칸 강등 → **-3**."))
        changed.append("alibaba.F9.obsreg25 evidence (그러나 -2 유지 superseded + 현재 경로)")

    f7 = by["openai.F7"]
    old_note = "C-09: 매트릭스 입력(환류 여부) 원문 없음 — 승계 점수"
    if f7["note"].startswith(old_note):
        f7["note"] = f7["note"].replace(old_note, (
            f"C-09: 매트릭스 입력(환류 여부)이 판단에 복원되지 않았다 — 승계 점수. **[{MARKER} 정정] 원문 부재가 아니다** — "
            "채점표_v1.5.md 662행 `OpenAI가 -1인 이유는 자기 Startup Fund가 API 고객에 투자하는 루프가 있어서고` 가 "
            "`small|yes`(-1, 채점규칙 322행) 입력의 원문 후보다. 외부 사실로 검증된 것은 아니고 입력 복원은 판단이라 이번에 하지 않았다(TEN-RC3-01)"), 1)
        changed.append("openai.F7 note (원문 후보 662행)")

    f7a = by["anthropic.F7"]
    if "TEN-RC3-01" not in f7a["note"]:
        f7a["note"] += (f" | [{MARKER}] TEN-RC3-01 — v1.5 매트릭스(채점규칙 321~322행) `small|no` 는 0 인데 v1.5 판정표 338행이 같은 근거"
                        "(AI 스타트업 고객 일부만 조달 의존)로 -1 을 준다. 원문 내부 모순을 승계했다. 재판정은 비 Claude 세션.")
        changed.append("anthropic.F7 note (TEN-RC3-01 안내)")
    return changed


TENSIONS = [
    {
        "id": "TEN-RC3-01",
        "status": "open",
        "recheck_at": "2026-11",
        "review_finding": f"RC3-01(high)·RC3-02(medium) · {REVIEW_C} · 체크리스트 Q02·Q03 fail",
        "judgment_ids": ["anthropic.F7", "openai.F7"],
        "decision_id": "C-09",
        "subject": "anthropic·openai F7 — 매트릭스 입력 없이 -1 을 승계했고 v1.5 매트릭스와 판정표가 서로 어긋난다",
        "tension": ("v1.5 매트릭스(채점규칙 321~322행)는 `조달 의존 고객 비중 작음 × 내 돈이 안 돌아옴` 을 0, `작음 × 돌아옴` 을 -1 로 준다. "
                    "v1.5 판정표 338행은 OpenAI·Anthropic 에 `매출은 일반 사용자·기업이 낸 진짜 돈 … AI 스타트업 고객 일부만 조달 의존` 이라는 "
                    "근거로 -1 을 주는데 이 문장은 환류(세로축)를 적지 않아 매트릭스로는 0 이다. **v1.5 내부 모순을 그대로 승계했다.** "
                    "두 판단 모두 inputs 가 비어 있어 엔진은 score -1 을 쓴다(C-09). openai 는 채점표 662행 `자기 Startup Fund가 API 고객에 "
                    "투자하는 루프` 가 `small|yes` 입력의 원문 후보이나 openai.F7 근거란에는 옮겨지지 않았다. anthropic 근거란에는 그런 루프 문장이 없다."),
        "direction": ("anthropic 상향 가능(-1 → 0). openai 는 662행을 입력으로 복원하면 -1 유지, 복원하지 못하면 anthropic 과 같은 문제. "
                      "이 등록은 입력을 복원하거나 판정하지 않는다 — 기존 -1 에 맞추려고 환류를 추정하지 않는다(C-09 권고)."),
        "rechecker": ("**비 Claude 세션이 재판정한다.** anthropic 점수이고 조율자·worker 가 Claude 라 이해상충이다(TEN-RC-02 와 같은 사유). "
                      "openai 는 Anthropic 경쟁사라 같은 세션에서 함께 본다."),
        "why_carried_exception": CARRIED,
        "score_impact_now": "없다.",
        "source_lines": ["채점규칙 321~322행", "채점규칙 338행", "채점표 662행"],
        "note": ("지시서 행 번호(322~323·336)와 보존 원문이 달라 원문 행을 적었다 — 321행 `내 돈이 안 돌아옴 | 0 | -2`, 322행 `내 돈이 돌아옴 | -1 | -3`, "
                 "336행은 0 점 행(Meta·Alibaba·…·SpaceX), 338행이 `-1 | OpenAI · Anthropic` 행이다. spacex-xai.F7 근거란이 662행을 승계하고 있다."),
    },
    {
        "id": "TEN-RC3-03",
        "status": "open",
        "recheck_at": "2026-11",
        "review_finding": f"RC3-03(high) · {REVIEW_C} · 체크리스트 Q02·Q03 fail",
        "judgment_ids": ["palantir.F1", "oracle.F1"],
        "subject": "palantir·oracle F1 — 업무 채널 전환비용을 한쪽은 가짜 해자로 빼고 한쪽은 락인으로 인정한다",
        "tension": ("채점규칙 407행 업무 채널 지표가 `유료 시트 · 기업 고객 수 · 전환비용` 이다. palantir.F1(2) 은 423행 `업무지만 스노우볼 없음"
                    "(가짜 해자) → 2` 와 채점표 584행 `정부·기업 계약의 전환비용은 실재하나 네트워크 효과가 아니다 … 가짜 해자(전환비용)` 로 전환비용을 "
                    "배제한다. oracle.F1(3) 은 채점표 533행 `엔터프라이즈 DB 락인은 수십 년째 강력 — 기간계 시스템 전환비용은 표에서 최상위급` 으로 "
                    "같은 지표를 근거로 쓴다. 전환비용을 업무 채널 지표로 인정하는 조건과 palantir 에만 붙은 스노우볼 필요조건을 함께 세우는 설명이 없다. "
                    "oracle 은 채점규칙 14개사 채널 매핑표(413~426행)에 없다."),
        "direction": "방향 미정 — 공통 정의를 세운 뒤 palantir 상향 또는 oracle 하향이 가능하다. 2 대 3 자체가 틀렸다는 판정이 아니다.",
        "rechecker": "2026-11 재채점 때 판단자(비 Claude 세션 권장). TEN-RC-02(anthropic F1 업무 채널)와 같은 F1 채널 기준 계열이라 함께 본다.",
        "why_carried_exception": CARRIED,
        "score_impact_now": "없다.",
        "source_lines": ["채점규칙 407행", "채점규칙 423행", "채점표 533행", "채점표 584행"],
        "related_tensions": ["TEN-RC-02"],
    },
    {
        "id": "TEN-RC3-04",
        "status": "open",
        "recheck_at": "2026-11",
        "review_finding": f"RC3-04(high) · {REVIEW_C} · 체크리스트 Q01·Q21 fail",
        "judgment_ids": ["tesla.F5", "tesla.F8"],
        "subject": "tesla F5·F8 — NHTSA 조사라는 같은 속성이 F5 H -1 과 F8 -2 에 반복된다",
        "tension": ("tesla.F5(H -1) 근거 `NHTSA FSD 조사 EA26002 격상(320만 대)`(채점표 703행)와 tesla.F8(-2) 근거 `NHTSA 조사`(채점표 714행)가 "
                    "같은 규제 위험이다. 채점규칙 262행 금지선은 `같은 관계` 가 아니라 `같은 속성` 이다. F5 는 적대세력, F8 은 대체 불가·사업 중단 "
                    "위험으로 갈라 설명돼 있지 않다. 두 factor 모두 다른 근거(F5 머스크 소송, F8 머스크 개인 의존·중국)가 함께 있어 NHTSA 가 몇 점을 "
                    "만들었는지 **중복 폭을 확인하지 못했다.**"),
        "direction": "속성 분리 설명 또는 한쪽 감점 축소(상향 가능). 판정하지 않는다.",
        "rechecker": "2026-11 재채점 때 판단자. TEN-RC-05(nvidia F5·F8 자체 칩 이탈 반복)와 같은 형태라 같은 잣대로 함께 본다.",
        "why_carried_exception": CARRIED,
        "score_impact_now": "없다.",
        "source_lines": ["채점표 703행", "채점표 714행", "채점규칙 262행"],
        "related_tensions": ["TEN-RC-05"],
    },
    {
        "id": "TEN-RC3-05",
        "status": "open",
        "recheck_at": "2026-11",
        "review_finding": f"RC3-05(medium) · {REVIEW_C} · 체크리스트 Q02 fail",
        "judgment_ids": ["alibaba.F3"],
        "subject": "alibaba F3 — 경쟁사 두 곳이 이미 오픈웨이트를 내는데 모방 불가능성이 partial 이다",
        "tension": ("채점규칙 75행 모방 불가능성은 `경쟁사 2곳 이상이 이미 하고 있으면 불인정` 이다. alibaba.F3 근거(채점표 380행)가 `메타(Glimmer)·"
                    "구글(Gemma)도 오픈웨이트를 내므로 유일하지 않고` 라고 스스로 두 곳을 적는데 입력은 partial 이다. 원문 판정표 102행도 `⚠️ 회수장치 "
                    "없음 … 2.5` 로 partial 이라 원천 내부 모순을 승계했다."),
        "direction": "하향 입력 가능(partial → fail). **점수는 바뀌지 않는다** — 아래 score_impact_now.",
        "rechecker": "2026-11 재채점 때 판단자.",
        "why_carried_exception": CARRIED,
        "score_impact_now": ("없다. imitation 을 fail 로 읽어도 revenue_model·acceleration 두 pass 로 통과점 2 → F3 3 이다(지금은 2.5 → 모방불가 "
                             "완전 pass 아님 상한 3). calc_qual.compute_f3 에 fail 입력을 넣어 확인했다(apply_tensions.py)."),
        "source_lines": ["채점규칙 75행", "채점규칙 102행", "채점표 380행"],
    },
]

Q10_AFFECTED = {
    "company_id": "oracle",
    "judgment_id": "oracle.F3",
    "why": ("FC-07 — acceleration=pass 근거가 `OCI 분기 $5.8B(+93%), FY26 연 $18.1B(+77%) · RPO $553B→$638B` 다. 분기 성장률과 연간 성장률은 "
            "기간 길이가 달라 비교 쌍이 아니고 RPO 는 잔고 차이다. 같은 길이·같은 지표의 직전 성장률이 없어 가속을 재현할 수 없다."),
    "source_lines": ["채점표 543행", "채점규칙 110행"],
}
Q10_NOTE = (f"[{MARKER}] {REVIEW_B} FC-07 로 oracle.F3 을 affected 에 넣었다. {REVIEW_C} RC3-10 — microsoft 는 보존 원문 안에 비교 후보가 있다: "
            "채점규칙 163행 `Azure +39→40→43% · Copilot 유료 시트 순증 +500만→+1,000만 · 단 AI 런레이트 YoY는 175%→123%로 둔화 | ✅ 가속`. "
            "활성 근거(시트 분기 +50% 하나)에는 이 비교가 빠져 있다. 기간·정의 일치와 순증을 성장률 변화로 읽는 검토 없이 pass·fail 을 바꾸지 않았고, "
            "재검토 자료를 외부에서만 찾아야 하는 상황은 아니다.")

C09_RECHECK = {
    "what": "anthropic.F7·openai.F7 의 두 축 입력 복원 또는 재판정 — TEN-RC3-01.",
    "why": "v1.5 매트릭스(채점규칙 321~322행)와 판정표 338행이 어긋나 승계 -1 을 매트릭스로 재현할 수 없다. openai 는 채점표 662행이 원문 후보다.",
    "trigger": "2026-11 재채점",
    "when": "2026-11",
    "note": "anthropic 점수라 비 Claude 세션이 판정한다. 기존 점수에 맞추려고 환류를 추정하지 않는다(이 결정의 recommendation).",
}


def check_alibaba_f3_invariant() -> None:
    """imitation=fail 로 읽어도 F3 가 3 인지 엔진 함수로 확인한다."""
    from scorecard.calc_qual import compute_f3

    class Lookup:
        def __init__(self, j: dict) -> None:
            self.j = j

        def get(self, cid: str, fid: str) -> dict:
            return self.j

    jud = {j["judgment_id"]: j for j in load(RUN / "judgments.json")["items"]}["alibaba.F3"]
    rules = load_rules("v1.7")
    now = compute_f3({"company_id": "alibaba"}, Lookup(jud), rules)
    alt = json.loads(json.dumps(jud))
    alt["inputs"]["imitation"] = "fail"
    fail = compute_f3({"company_id": "alibaba"}, Lookup(alt), rules)
    assert (now["score"], now["calc"]["pass_points"]) == (3, 2.5), now
    assert (fail["score"], fail["calc"]["pass_points"]) == (3, 2.0), fail
    print("alibaba F3 불변 확인: partial 2.5→3 · fail 2.0→3")


def main() -> int:
    check_alibaba_f3_invariant()
    registry = {c["company_id"]: c for c in load_json_strict(ROOT / "scorecard" / "companies.json")["companies"]}
    jud = load(RUN / "judgments.json")
    changed = fix_judgments(jud)
    validate_judgments(jud, registry, load_rules("v1.7").payload, RUN_ID)
    dump(RUN / "judgments.json", jud)

    rules = load(RULES)
    ids = [t["id"] for t in TENSIONS]
    rules["open_tensions"] = [t for t in rules["open_tensions"] if t["id"] not in ids] + TENSIONS
    q10 = next(t for t in rules["open_tensions"] if t["id"] == "TEN-RB-Q10")
    q10["affected"] = [a for a in q10.get("affected", []) if a.get("judgment_id") != "oracle.F3"] + [Q10_AFFECTED]
    q10["note"] = Q10_NOTE
    c09 = next(d for d in rules["decisions"] if d["id"] == "C-09")
    c09["pending_recheck"] = C09_RECHECK
    for c in rules.get("source_text_corrections") or []:
        if c["id"] == "STC-AWS-100B":
            c["note"] = ("FIX-53 3단계 보완(msg_da0ec25d3846). 소비자: render_common.apply_text_corrections(트리거 표 — 초안·HTML 공통, "
                         "FIX-54 1단계에서 render_md 에서 옮김).")
    validate_rules(rules)
    dump(RULES, rules)

    run = load(RUN / "run.json")
    run["rule_hash"] = load_rules("v1.7").hash
    validate_run(run, RUN_ID)
    dump(RUN / "run.json", run)
    print("판단 변경:", changed or "없음(이미 반영)")
    print("긴장:", ", ".join(ids), "+ TEN-RB-Q10 보강 · C-09 pending_recheck · rule_hash", run["rule_hash"][:12])
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    sys.exit(main())
