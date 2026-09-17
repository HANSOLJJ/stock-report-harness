# FIX-62: openai.F9 를 C-20 비상장 경로로 — 사용자가 앞선 결정을 뒤집었다 (openai F9 -4 → -2, 총점 2 → 4)
"""보존 원문만 읽는다. 신규 조회 없음.

- 비 Claude 판정 `review-obsreg validation/openai-f9-route/gemini.md`
- 9차 재무 계산 재판정 `review-obsreg reviews/_parts/ai-scorecard-2026-09-obsreg/financial-calc.md` (체크리스트 Q11)
- 채점규칙 v1.5 388~390행(별표 D) · 470·494·603행 — E:/…/AI_company_analysis_factor

재실행해도 같은 결과가 나온다. 파일은 LF 로 쓴다.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard.rules import load_rules  # noqa: E402
from scorecard.schema import load_json_strict, validate_rules, validate_run  # noqa: E402

RUN_ID = "ai-scorecard-2026-09-obsreg"
RUN = ROOT / "scorecard" / "runs" / RUN_ID
RULES = ROOT / "scorecard" / "rules" / "v1.7.json"
DATE = "2026-09-17"
M = "FIX-62"


def load(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def dump(p: Path, d: dict) -> None:
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def find(items: list[dict], key: str, value: str) -> dict:
    hit = [x for x in items if x.get(key) == value]
    assert len(hit) == 1, f"{key}={value} 가 {len(hit)}건"
    return hit[0]


# ------------------------------------------------------------------ C-29 뒤집기

C29 = {
    "id": "C-29",
    "status": "resolved",
    "blocking": False,
    "affects": ["F9"],
    "summary": "BEP 목표 후퇴와 C-20 비상장 경로 중 무엇이 앞서는가 — 앞선 결정(BEP 우선)을 뒤집는다",
    "recommendation": "C-20 이 앞선다. 비상장이고 영업손익이 구조적 미공시면 BEP 후퇴가 기록돼 있어도 비상장 경로로 보낸다.",
    "choices": ["bep_retreat_first", "c20_private_route_first"],
    "chosen": "c20_private_route_first",
    "superseded_choice": "bep_retreat_first",
    "decided_at": DATE,
    "decided_by": "사용자",
    "confirmed_model": {
        "rule": ("**C-20 탐지가 먼저 선다.** `company.listed` 가 false 이고 영업손익 관측의 `missing_type` 이 "
                 "`not_disclosed_confirmed` 이면 `bep_retreat` 값과 무관하게 G1 을 판정 보류로 두고 G2 비상장 조항으로 "
                 "보낸다. BEP 후퇴 점수(`g1_bep_retreat_score`)는 상장사이거나 구조적 미공시가 아닌 경우에만 선다."),
        "why": [
            "**BEP 목표 후퇴는 전망이지 측정된 실적이 아니다.** 채점규칙 별표 D 388~390행 — `계획·발표·포지션은 0점이고 "
            "출하·매출·채택률처럼 지금 측정되는 것만 센다`. 그 목표로 가장 깊은 칸을 주는 것은 이 조항과 어긋난다.",
            "**C-20 이 명시적으로 버린 `assume_loss` 와 같은 형태다.** `policies.f9.g1_private_undisclosed_route."
            "why_not_assume_loss` 가 `TTM 영업손익을 모르는데 적자라고 단정하는 것이다` 라고 적는다. openai 의 TTM "
            "영업손익은 구조적 미공시이고 `operating_result_reviewed: loss` 의 근거도 전망이다.",
            "**판정 둘이 같은 방향이다.** 비 Claude 판정(Gemini 독립 세션 2026-09-17, `validation/openai-f9-route/"
            "gemini.md`)이 `C-20 우선` 으로 판정했고, 9차 재무 계산 재판정(Claude 독립 세션)이 같은 자리를 체크리스트 "
            "**Q11 fail · 승계 예외 불성립**으로 판정했다 — `results.json` 의 openai F9 가 `status: ok · basis: computed` "
            "라 이번 실행의 엔진과 정책값이 만든 점수이기 때문이다.",
            "v1.5 가 openai 손익을 적은 자리가 전부 전망·목표다 — 채점표 769·785행이 `전망` 을 명시하고 867행이 "
            "현금·FCF 를 `미공시`, 런웨이를 `판정 불가` 로 분류한다.",
        ],
        "superseded_reasons": {
            "what_was_argued": ("밀린 쪽(`bep_retreat_first`)의 근거는 v1.5 문면이다 — 채점규칙 470행 "
                                "`| **-5** | 손실률 **-30% 초과** · 또는 **BEP 목표가 후퇴** |` 가 BEP 후퇴를 **독립 조건**으로 적고, "
                                "494·603행이 그것을 OpenAI 에 **이름으로** 적용한다. FIX-59 가 이 근거로 우선순위를 확정했었다."),
            "why_not_chosen": ("**같은 v1.5 안에서 별표 D 와 충돌한다.** 470행은 ⑨ 적용표의 칸이고 별표 D 는 전 factor 에 걸리는 "
                               "일반 조항이다. 사용자가 일반 조항과 독립 판정 둘을 따르는 쪽을 골랐다. "
                               "**밀린 근거를 지우지 않는다** — 다시 들 수 있는 자리이고 충돌 자체는 남아 있다(TEN-RA6-01)."),
        },
        "score_impact": "**openai F9 -4 → -2, 총점 2 → 4.** 단독 13위가 되고 oracle 이 단독 14위가 된다. 나머지 12개사 불변.",
        "why_anthropic_unchanged": "anthropic 은 `bep_retreat: no` 라 전에도 C-20 경로였다 — 이 결정으로 바뀌는 것이 없다.",
    },
    "scope": {
        "what_changed": "calc_f9.compute_f9 의 G1 갈림 — C-20 탐지를 `bep_retreat` 보다 앞에 둔다.",
        "reversal_of": "FIX-59(2026-09-17) 가 `policies.f9.g1_bep_retreat_precedence` 로 확정했던 반대 방향. 같은 날 뒤집혔다.",
        "not_changed": ("BEP 후퇴 점수값(`g1_bep_retreat_score` -4)과 상장사 경로는 그대로다. "
                        "상장 적자 기업에 BEP 후퇴가 기록되면 여전히 그 점수를 받는다."),
    },
}

PRECEDENCE_REVERSED = {
    "status": "superseded",
    "superseded_at": DATE,
    "superseded_by": "C-29 (사용자 결정 2026-09-17 — 같은 날 앞선 결정을 뒤집었다)",
    "what_it_said": ("~~`bep_retreat: yes` 가 C-20 비상장 판정보다 앞선다. BEP 후퇴가 기록되면 G1 은 그 자리에서 실패로 "
                     "판정되고 `g1_bep_retreat_score`(-4)를 받는다 — 비상장이고 TTM 영업손익이 구조적 미공시여도 "
                     "`g1_private_undisclosed_route`(C-20) 로 내려가지 않는다.~~ (superseded)"),
    "why_it_was_written": ("FIX-59 가 채점규칙 470·494·603행을 근거로 당시 코드 동작을 문면으로 확정했다. 근거 자체는 "
                           "그대로 유효한 인용이고 C-29 의 `superseded_reasons` 에 옮겨 두었다."),
    "what_is_true_now": ("**C-20 이 앞선다.** 비상장 + 영업손익 구조적 미공시면 `bep_retreat` 와 무관하게 비상장 경로로 간다. "
                         "BEP 후퇴 점수는 상장사이거나 구조적 미공시가 아닌 경우에만 선다(C-29)."),
    "where_in_code": ("calc_f9.compute_f9 — `if margin is None:` 안에서 `_private_undisclosed_operating(...)` 검사가 "
                      "`bep_retreat` 갈림보다 먼저 선다. C-20 경로로 들어가면서 BEP 후퇴가 기록돼 있으면 경로에 "
                      "`bep_retreat_not_applied` 를 남긴다."),
    "kept_why": ("**지우지 않는다.** 같은 날 두 번 결정이 뒤집힌 자리라, 무엇을 근거로 무엇을 골랐다가 무엇으로 바꿨는지가 "
                 "남아야 다음 사람이 세 번째로 같은 길을 돌지 않는다."),
    "why_openai_differs_from_anthropic": ("**이제 둘이 같은 경로다.** 전에는 판단 입력 `bep_retreat`(openai yes · anthropic no)가 "
                                          "경로를 갈랐으나, C-29 뒤로는 둘 다 C-20 비상장 경로로 간다. "
                                          "openai 는 그 위에 `bep_retreat: yes` 가 기록만 남는다(경로 기록의 "
                                          "`bep_retreat_not_applied`)."),
}

TEN_RA5_02_RESOLVED = {
    "status": "resolved",
    "resolved_at": DATE,
    "resolution": ("**해소됐다 — 긴장이 가리킨 방향으로 결정됐다.** 사용자가 2026-09-17 에 C-20 우선(C-29)을 골라 "
                   "openai.F9 가 -4 → **-2**, 총점 2 → **4** 가 됐다. 이 긴장이 `상향 가능` 으로 적은 그대로다. "
                   "비 Claude 재판정 약속도 이행됐다 — Gemini 독립 세션이 판정했고 9차 재무 계산 재판정이 같은 방향으로 "
                   "체크리스트 Q11 을 fail 로 봤다."),
    "what_remains": ("**v1.5 내부 충돌 자체는 남는다** — 470행(BEP 후퇴 = 독립 조건) 대 별표 D 388~390행(계획·발표는 0점). "
                     "이번 결정은 그 충돌을 없앤 것이 아니라 한쪽을 골랐다. 새 긴장 **TEN-RA6-01** 로 옮긴다."),
    # 아래 넷은 `현행 유지` 를 전제로 쓰였다. 해소와 어긋나므로 같이 고친다(FIX-61 이 잡은 문면 모순과 같은 종류다).
    "direction": ("**상향으로 결정됐다.** C-20 우선으로 판정해 openai F9 -4 → **-2**, 총점 2 → **4** 가 됐고 단독 13위, "
                  "oracle 이 단독 14위다. 긴장이 적었던 방향 그대로다(C-29)."),
    "score_impact_now": "**반영됐다.** openai F9 -2 · 총점 4 다. 이 긴장이 예고한 상향이 그대로 일어났다.",
    "rechecker": ("**이행됐다** — 비 Claude 세션(Gemini, 2026-09-17)이 `C-20 우선` 으로 판정했고 9차 재무 계산 재판정이 "
                  "같은 방향으로 체크리스트 Q11 을 fail 로 보았다. 남은 충돌의 재판정자는 TEN-RA6-01 이 잇는다."),
    "trigger": ("**발동해 닫혔다** — 비 Claude 재판정과 9차 재판정이 함께 왔고 사용자가 2026-09-17 에 판정을 따랐다. "
                "openai 의 TTM 영업손익 공시는 이제 TEN-RA6-01 의 발동 조건이다."),
    "decision_id": "C-29",
    "related_tensions": ["TEN-RA3-01", "TEN-RA6-01"],
    "note": ("[FIX-59] 사용자가 2026-09-17 에 넷 중 `FIX-59 만 하고 승인` 을 골랐고 이 자리는 `현행 유지 + 긴장 등록` 으로 정했다. "
             "[FIX-62] **같은 날 그 결정을 뒤집었다**(C-29). anthropic 과의 차이를 만들던 판단 입력 한 칸"
             "(`bep_retreat` no 대 yes)은 이제 경로를 가르지 않는다 — 둘 다 C-20 비상장 경로다."),
}

TEN_RA6_01 = {
    "id": "TEN-RA6-01",
    "status": "open",
    "recheck_at": "2026-11",
    "review_finding": "RA6-01(v1.5 내부 충돌 — C-29 결정으로 한쪽을 골랐으나 충돌은 남는다) · 사용자 결정 2026-09-17",
    "judgment_ids": ["openai.F9"],
    "subject": "채점규칙 470행(BEP 목표 후퇴 = 독립 감점 조건)과 별표 D 388~390행(계획·발표·포지션은 0점)이 v1.5 안에서 충돌한다",
    "tension": (
        "470행은 ⑨ 적용표에서 `| **-5** | 손실률 **-30% 초과** · 또는 **BEP 목표가 후퇴** |` 로 **목표 후퇴를 독립 "
        "감점 조건**으로 적고 494·603행이 OpenAI 에 이름으로 적용한다. 그런데 별표 D 388~390행은 전 factor 에 걸리는 "
        "일반 조항으로 `계획·발표·포지션은 0점이고 출하·매출·채택률처럼 지금 측정되는 것만 센다` 고 적는다. "
        "**BEP 목표는 계획이다.** 둘 중 하나를 고르지 않으면 같은 사실이 조항에 따라 -4 도 되고 0 도 된다. "
        "C-29 가 별표 D 쪽을 골랐으나 470행 문면은 그대로 남아 있다."),
    "direction": ("판정하지 않는다. 470행을 살리면 openai F9 가 다시 -4(총점 2)가 되고, 별표 D 를 살리면 지금처럼 "
                  "-2(총점 4)다. **이번 실행은 별표 D 쪽이다**(C-29)."),
    "rechecker": ("**비 Claude 세션이 재판정한다** — openai 는 Anthropic 경쟁사이고, 이 자리는 같은 날 두 번 뒤집힌 "
                  "만큼 판정자를 바꿔 다시 보는 편이 안전하다."),
    "third_party_recheck": "committed",
    "why_carried_exception": ("승계 판단이지만 **이번 실행이 이 자리의 잣대를 두 번 바꿨다**(FIX-59 확정 → C-29 뒤집기). "
                              "예외로 넘기지 않고 정식 긴장으로 둔다."),
    "score_impact_now": "없다. C-29 로 이미 반영됐고 openai F9 -2 · 총점 4 다.",
    "trigger": ("2026-11 재채점, 또는 openai 의 TTM 영업손익이 공시·확보될 때. 실측 손익이 들어오면 BEP 전망에 기대지 "
                "않고 손실률 밴드로 직접 판정할 수 있어 이 충돌이 openai 에서는 사라진다 — 다만 조항 충돌 자체는 "
                "다른 회사에 다시 걸릴 수 있다."),
    "decision_id": "C-29",
    "related_tensions": ["TEN-RA5-02"],
    "note": (f"[{M}] TEN-RA5-02 가 해소되면서 그 안의 `v1.5 내부 충돌` 부분만 여기로 옮겼다. "
             "충돌을 없앤 것이 아니라 한쪽을 골랐을 뿐이라는 사실을 남긴다."),
}

RUN_C29 = {
    "id": "C-29",
    "choice": "c20_private_route_first",
    "rationale": ("비상장이고 영업손익이 구조적 미공시면 BEP 후퇴가 기록돼 있어도 C-20 비상장 경로로 보낸다. "
                  "**앞선 결정(FIX-59 의 bep_retreat 우선)을 뒤집은 것이다.** 근거는 판정 둘(비 Claude Gemini 독립 "
                  "세션의 `C-20 우선` · 9차 재무 계산 재판정의 Q11 fail)과 별표 D 388~390행이다. "
                  f"openai F9 -4 → -2, 총점 2 → 4. 규칙 v1.7 decisions C-29 를 실행 단위로 옮긴다. {M}."),
    "decided_by": "사용자",
    "decided_at": DATE,
}

RUN_ASSUMPTION = (
    f"[{M} · 사용자 결정 2026-09-17] **openai.F9 경로를 뒤집었다.** 같은 날 FIX-59 가 `bep_retreat 우선` 으로 확정한 "
    "것을 C-29 로 되돌려 **C-20 비상장 경로가 앞선다.** openai F9 -4 → **-2**, 총점 2 → **4**(단독 13위 · oracle 단독 "
    "14위). 근거는 판정 둘이 같은 방향이라는 것이다 — 비 Claude 판정(Gemini)의 `C-20 우선` 과 9차 재무 계산 재판정의 "
    "체크리스트 Q11 fail. 둘 다 **BEP 목표 후퇴는 전망이지 측정된 실적이 아니다**를 근거로 들었고, 그것은 C-20 이 "
    "명시적으로 버린 `assume_loss` 와 같은 형태다. 밀린 근거(채점규칙 470·494·603행)는 지우지 않고 C-29 에 남겼으며, "
    "**v1.5 내부 충돌 자체는 TEN-RA6-01 로 11월 재채점 입력이 된다.** anthropic 은 전부터 C-20 경로라 불변이다.")


def fix_rules(rules: dict) -> list[str]:
    out: list[str] = []
    decisions = rules["decisions"]
    cur = [d for d in decisions if d["id"] == "C-29"]
    if not cur:
        decisions.append(json.loads(json.dumps(C29)))
        out.append("+ decisions C-29 (C-20 우선 — 앞선 결정 뒤집기, 사용자)")
    elif cur[0] != C29:
        decisions[decisions.index(cur[0])] = json.loads(json.dumps(C29))

    prec = rules["policies"]["f9"]["g1_bep_retreat_precedence"]
    src = prec.get("superseded_record", prec)          # 재실행이면 이미 옮겨 둔 것에서 읽는다
    keep = {k: src[k] for k in ("rule", "source_lines", "rescale_note", "where_in_code", "user_choice",
                                "decided_at", "decided_by") if k in src}
    assert keep.get("rule", "").startswith("**`bep_retreat: yes` 가"), "옛 문면이 사라졌다 — 보존 대상 확인"
    # 손실률 밴드와의 순서는 **뒤집히지 않았다** — 상장사 경로에서 여전히 참이라 최상위에 남긴다.
    band = prec.get("also_precedes_loss_band") or src["also_precedes_loss_band"]
    # FIX-61 이 쓴 문장은 `C-20 앞에서도 먼저 본다` 를 전제한다. C-29 뒤로는 그 부분만 사실이 아니다.
    band = band.replace("FIX-59 는 C-20 과의 순서를 적었지만 코드는 그 전에 `bep_retreat` 를 먼저 본다",
                        "**C-20 비상장 경로 다음** 자리에서는 `bep_retreat` 를 손실률 밴드보다 먼저 본다"
                        "(C-20 자체보다는 뒤로 밀렸다 — C-29)")
    want = {**PRECEDENCE_REVERSED, "also_precedes_loss_band": band, "superseded_record": keep}
    if prec != want:
        rules["policies"]["f9"]["g1_bep_retreat_precedence"] = json.loads(json.dumps(want))
        out.append("policies.f9.g1_bep_retreat_precedence: 뒤집힌 기록으로 (옛 문면·근거는 보존)")

    t = find(rules["open_tensions"], "id", "TEN-RA5-02")
    for key, value in TEN_RA5_02_RESOLVED.items():
        if t.get(key) != value:
            t[key] = value
            out.append(f"TEN-RA5-02: {key}")

    cur6 = [x for x in rules["open_tensions"] if x["id"] == "TEN-RA6-01"]
    if not cur6:
        rules["open_tensions"].append(json.loads(json.dumps(TEN_RA6_01)))
        out.append("+ open_tensions TEN-RA6-01 (v1.5 470행 대 별표 D 충돌 — 11월 입력)")
    elif cur6[0] != TEN_RA6_01:
        rules["open_tensions"][rules["open_tensions"].index(cur6[0])] = json.loads(json.dumps(TEN_RA6_01))
    return out


OLD_RESCALE_TAIL = ("엔진 경로는 `G1 BEP 후퇴 → -4` → `G3/G4 생략(이미 하한)` 이고 **F9 = -4** 다. "
                    "아래 게이트 1·마지막 줄의 `-5` 는 v1.5 문면이며 재척도 전 점수다. 판정 입력(bep_retreat=yes)은 바뀌지 않았다. "
                    "obsreg 5차 리뷰 B(financial-calc, review-obsreg 8b98b56) medium.")
NEW_RESCALE_TAIL = ("~~엔진 경로는 `G1 BEP 후퇴 → -4` → `G3/G4 생략(이미 하한)` 이고 **F9 = -4** 다.~~ "
                    "**[FIX-62 2026-09-17] 경로가 바뀌었다** — 사용자가 C-29 로 앞선 결정을 뒤집어 "
                    "`G1 판정 보류(C-20 비상장 경로)` → `G2 비상장 FCF 미공시 -2` → `G3 생략` → `G4 비교 불가(추가 감점 없음)` 이고 "
                    "**F9 = -2** 다. BEP 후퇴 기록은 그대로이나 경로를 가르지 않는다(전망·목표는 별표 D 388~390행에서 0점). "
                    "아래 게이트 1·마지막 줄의 `-5` 는 v1.5 문면이며 재척도 전 점수다. 판정 입력(bep_retreat=yes)은 바뀌지 않았다. "
                    "obsreg 5차 리뷰 B(financial-calc, review-obsreg 8b98b56) medium · 9차 재판정 Q11.")


def fix_judgments(payload: dict) -> list[str]:
    """openai.F9 근거란 맨 앞 표시 줄이 아직 `F9 = -4` 라고 말한다 — 초안까지 그대로 흘러간다."""
    out: list[str] = []
    j = find(payload["items"], "judgment_id", "openai.F9")
    for key in ("evidence", "notes", "rationale"):
        for i, line in enumerate(j.get(key) or []):
            if OLD_RESCALE_TAIL in line:
                j[key][i] = line.replace(OLD_RESCALE_TAIL, NEW_RESCALE_TAIL)
                out.append(f"openai.F9.{key}[{i}]: 재척도 표시 줄을 새 경로로")
    assert out or any(NEW_RESCALE_TAIL in x for v in j.values() if isinstance(v, list) for x in v
                      if isinstance(x, str)), "낡은 표시 줄도 새 표시 줄도 찾지 못했다"
    # 새 문장이 채점규칙 별표 D 를 인용하므로 출처 목록에도 그 문서가 서야 한다(FIX-52 인용 검사).
    if "SRC-v15-rule" not in j["source_ids"]:
        j["source_ids"] = sorted({*j["source_ids"], "SRC-v15-rule"})
        out.append("openai.F9.source_ids: SRC-v15-rule 추가(별표 D 인용)")
    return out


def fix_run(run: dict) -> list[str]:
    out: list[str] = []
    if not any(d["id"] == "C-29" for d in run["decisions"]):
        run["decisions"].append(json.loads(json.dumps(RUN_C29)))
        out.append("+ decisions C-29 (실행 단위)")
    if RUN_ASSUMPTION not in run["assumptions"]:
        run["assumptions"].append(RUN_ASSUMPTION)
        out.append("+ assumptions openai.F9 경로 뒤집기와 근거")
    return out


def main() -> int:
    load_json_strict(ROOT / "scorecard" / "companies.json")

    rules = load(RULES)
    rc = fix_rules(rules)
    validate_rules(rules)
    dump(RULES, rules)

    jpath = RUN / "judgments.json"
    judgments = load(jpath)
    jc = fix_judgments(judgments)
    dump(jpath, judgments)

    run = load(RUN / "run.json")
    runc = fix_run(run)
    run["rule_hash"] = load_rules("v1.7").hash
    validate_run(run, RUN_ID)
    dump(RUN / "run.json", run)

    for title, items in (("규칙", rc), ("판단", jc), ("실행", runc)):
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
