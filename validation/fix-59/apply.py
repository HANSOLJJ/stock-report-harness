# FIX-59 마지막 반영: 8차 리뷰 전부 + openai.F9 경로 결정(사용자) + 승인 준비 (점수 불변)
"""보존 원문만 읽는다. 신규 조회 없음.

- 채점규칙 v1.5 470·494·603행 · 별표 D 388~390행 — E:/…/AI_company_analysis_factor
- `raw/`(밑줄 없음) 폴더까지 넓힌 보존 제출본 주사 — validation/offb-24b-…·f6-fx-16-…·mcap-36-…
- 8차 part 원문 review-obsreg e5a47d3 · openai.F9 판정 validation/openai-f9-route/gemini.md

재실행해도 같은 결과가 나온다. 파일은 LF 로 쓴다.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard.rules import load_rules  # noqa: E402
from scorecard.schema import load_json_strict, validate_judgments, validate_observations, validate_rules, validate_run  # noqa: E402

RUN_ID = "ai-scorecard-2026-09-obsreg"
RUN = ROOT / "scorecard" / "runs" / RUN_ID
RULES = ROOT / "scorecard" / "rules" / "v1.7.json"
DATE = "2026-09-17"
M = "FIX-59"
R8B = "obsreg 8차 리뷰 B(financial-calc, review-obsreg e5a47d3)"
R8A = "obsreg 8차 리뷰 A 분담(Claude 독립 세션, review-obsreg e5a47d3)"
R8D = "obsreg 8차 리뷰 D(Gemini output-readability)"
SPCX_S1A = "3cf9799:validation/offb-24/_raw/spcx_s1a_20260603.htm"
SPCX_10Q = "3cf9799:validation/offb-24/_raw/spcx-20260630.htm"
AMZN_10Q = "3cf9799:validation/offb-24/_raw/amzn-20260630.htm"


def load(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def dump(p: Path, d: dict) -> None:
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def find(items: list[dict], key: str, value: str) -> dict:
    hit = [x for x in items if x.get(key) == value]
    assert len(hit) == 1, f"{key}={value} 가 {len(hit)}건"
    return hit[0]


# ------------------------------------------------------------------ S1 openai.F9 경로

BEP_PRECEDENCE = {
    "rule": ("**`bep_retreat: yes` 가 C-20 비상장 판정보다 앞선다.** BEP 후퇴가 기록되면 G1 은 그 자리에서 실패로 "
             "판정되고 `g1_bep_retreat_score`(-4)를 받는다 — 비상장이고 TTM 영업손익이 구조적 미공시여도 "
             "`g1_private_undisclosed_route`(C-20) 로 내려가지 않는다."),
    "where_in_code": "calc_f9.compute_f9 — `if margin is None and not bep_retreat:` 가 그 우선순위다.",
    "source_lines": [
        "채점규칙 470행 `| **-5** | 손실률 **-30% 초과** · 또는 **BEP 목표가 후퇴** |` — **OR 조건**이라 손실률 수치가 없어도 후퇴 하나로 성립한다",
        "채점규칙 494행 `| **OpenAI** | BEP가 2030년으로 **후퇴** | -5 | 조건 A 실패(악화) | **-5** |` — v1.5 가 이름으로 적용했다",
        "채점규칙 603행 `| **-5** | 영업적자 **손실률 -30% 초과** 또는 **BEP 자체가 후퇴** | OpenAI(2026 손실 ~$60B 전망, **BEP 2030으로 후퇴**) |`",
    ],
    "rescale_note": "위 세 줄의 -5 는 C-06 재척도 전 값이다. 현재 하한은 -4 이고 `g1_bep_retreat_score` 가 -4 다.",
    "why_openai_differs_from_anthropic": (
        "**판단 입력 기록의 차이다.** `openai.F9.inputs.bep_retreat = yes` 이고 `anthropic.F9.inputs.bep_retreat = no` 다. "
        "둘 다 비상장이고 TTM 영업손익이 구조적 미공시(`not_disclosed_confirmed`)인데, openai 만 BEP 후퇴가 기록돼 있어 "
        "경로가 갈린다. 회사 성질이 아니라 **입력 한 칸**이 경로를 정한다."),
    "decided_at": DATE,
    "decided_by": "사용자 (2026-09-17)",
    "user_choice": ("비 Claude 판정자(Gemini)가 `C-20 우선`(openai F9 -2 · 총점 4)으로 판정했으나 **사용자가 현행 -4 유지 + "
                    "긴장 등록**을 골랐다. 판정 원문 `review-obsreg validation/openai-f9-route/gemini.md` · "
                    "조율자 기록 `설계진행 validation/openai-f9-route-decision.md`."),
}

TEN_RA5_02 = {
    "id": "TEN-RA5-02",
    "status": "open",
    "recheck_at": "2026-11",
    "review_finding": "RA5-02(openai.F9 경로 · 비 Claude 판정자 반대 의견) · obsreg 8차 라운드 사용자 결정 2026-09-17",
    "judgment_ids": ["openai.F9"],
    "subject": "BEP 후퇴가 C-20 비상장 판정보다 앞서는 것이 맞는지 — v1.5 안에서 두 문면이 충돌한다",
    "tension": (
        "현행 동작은 `bep_retreat: yes` 우선이고 근거는 채점규칙 470·494·603행이다(policies.f9.g1_bep_retreat_precedence). "
        "**그런데 같은 v1.5 의 별표 D 388~390행은 `계획·발표·포지션은 0점이고 출하·매출·채택률처럼 지금 측정되는 것만 센다` "
        "고 적는다.** BEP 목표 후퇴는 계획·전망이지 측정된 결과가 아니다. 비 Claude 판정자(Gemini)의 지적도 같다 — "
        "전망·목표로 손실을 단정하는 것은 **C-20 이 명시적으로 버린 `assume_loss` 와 같은 형태**다"
        "(`g1_private_undisclosed_route.why_not_assume_loss`: `TTM 영업손익을 모르는데 적자라고 단정하는 것이다`). "
        "openai 의 TTM 영업손익은 구조적 미공시이고 `operating_result_reviewed` 는 `loss` 로 기록돼 있는데 그 근거도 전망이다."),
    "direction": ("**상향 가능.** C-20 우선으로 판정하면 openai F9 -4 → **-2**, 총점 2 → **4** 로 단독 13위가 되고 "
                  "oracle 이 단독 14위가 된다. 이번 실행은 현행을 유지한다 — 사용자 결정."),
    "rechecker": ("**비 Claude 세션이 재판정한다** — 이미 한 번 비 Claude 판정자(Gemini)가 반대 의견을 냈고, openai 는 "
                  "Anthropic 경쟁사라 하향 유지 쪽에 이해상충이 있다(TEN-RA3-01 과 같은 사유이나 여기서는 방향이 "
                  "상향이라 제약을 확정으로 둔다)."),
    "third_party_recheck": "committed",
    "why_carried_exception": ("승계 판단이지만 **이번 실행이 이 자리의 잣대를 문면으로 확정했다**"
                              "(policies.f9.g1_bep_retreat_precedence 신설). 그래서 예외로 넘기지 않고 정식 긴장으로 둔다."),
    "score_impact_now": "없다. openai F9 -4 · 총점 2 그대로다.",
    "trigger": ("2026-11 재채점, 또는 openai 의 TTM 영업손익이 공시·확보될 때. 실측 손익이 들어오면 BEP 전망에 기대지 "
                "않고 손실률 밴드로 직접 판정할 수 있어 이 충돌 자체가 사라진다."),
    "decision_id": "C-20",
    "related_tensions": ["TEN-RA3-01"],
    "note": (f"[{M}] 사용자가 2026-09-17 에 넷 중 `FIX-59 만 하고 승인` 을 골랐고 이 자리는 `현행 유지 + 긴장 등록` 으로 "
             "정했다. anthropic 과의 차이는 회사 성질이 아니라 판단 입력 한 칸(`bep_retreat` no 대 yes)이라는 사실을 "
             "policies.f9.g1_bep_retreat_precedence.why_openai_differs_from_anthropic 에 적었다."),
}


# ------------------------------------------------------------------ S2 B 8차

HOW_TO_MEASURE = (
    "**대차대조표 줄을 기준으로 하고, 한 줄 안에 시장성과 비시장성이 섞이면 주석으로 내려가 가른다.** "
    f"[{M} 문면 정정 · {R8B} medium] 전에는 `대차대조표 줄만 쓴다` 로 시작해, nvidia 의 시장성 지분증권을 주석 태그"
    "(`EquitySecuritiesFvNi` 42,783M)로 넣은 FIX-58 1단계 정정과 방향이 어긋났다. **실제 기준은 처음부터 둘이었다** — "
    "alibaba 의 `Equity securities and other investments` 와 tsmc 의 FVTPL·FVOCI 비유동을 주석 분할로 가른 것이 같은 "
    "처리다. 쓰지 않는 것은 (1) **합계 줄**(LongTermInvestments 등)과 (2) **만기·공정가치 버킷**이다 — 버킷은 현금성자산 "
    "안의 증권까지 포함해 이중계상을 만든다(nvidia 만기 1년 이내 41,000 이 그 사례). 주석 분할은 대차대조표 줄을 "
    "**가르는** 것이고 버킷은 다른 축으로 **다시 세는** 것이라 성질이 다르다."
)

REMAINDER_SENSITIVITY = {
    "what": (f"[{M} · {R8B} medium] 리뷰어가 시장성 증권의 **잔여분**을 더해 봤다 — nvidia 만기 1~5년 채무증권 5,900 · "
             "alphabet 7,202 · microsoft 11,948. 네 회사 다 P2 밴드가 움직이지 않는다."),
    "cases": {
        "alphabet": {"p2_now": 8.9675, "p2_if_added": 8.9514, "band": "8~20", "changes": False},
        "microsoft": {"p2_now": 11.2765, "p2_if_added": 11.2405, "band": "8~20", "changes": False},
        "nvidia": {"p2_now": 17.6898, "p2_if_added": 17.6704, "band": "8~20", "changes": False},
        "oracle": {"p2_now": 8.5995, "p2_if_added": 8.2413, "band": "8~20", "changes": False},
    },
    "why_not_added": ("**만기 버킷은 쓰지 않는다**(how_to_measure). 잔여분이 버킷 공시에서 나오므로 더하면 이 실행이 "
                      "지운 이중계상을 되살린다. 값은 바꾸지 않고 민감도만 남긴다 — 밴드가 하나도 안 움직이므로 "
                      "이 선택이 점수를 만들지 않았다는 뜻이다."),
    "oracle_is_closest": ("oracle 이 8.5995 → 8.2413 으로 가장 많이 움직이지만 밴드 경계 8 까지 여전히 +3.0% 밖이다"
                          "(허용폭 3%). 다음 라운드에서 잔여분을 세기로 하면 oracle 이 먼저 경계에 닿는다."),
    "recorded_at": DATE,
}

C26_ADD = (
    f" [{M} · {R8B} medium] **G4 의 분자와 분모는 기준일도 성질도 다르다** — 분자 RPO 638,000M 은 2026-05-31 공시 사실"
    "(`oracle.contracted_revenue.fix57`, verified)이고 분모 250,000M 은 기준일이 2026-09-02 로 적힌 legacy 승계값이며 "
    "어느 공시 사실과도 맞지 않는다. 커버리지 2.552 는 그 둘의 비다. 임계 1.0 에서 멀어 오늘 step 은 갈리지 않지만, "
    "**범위를 정할 때 기준일도 같이 정해야 한다.**")


# ------------------------------------------------------------------ S3 A 분담 8차

RAW_SWEEP2 = {
    "checked_at": DATE,
    "review": f"{R8A} medium",
    "why": ("FIX-58 2단계의 전수가 `_raw`(밑줄) 폴더로만 범위를 잡았다. **밑줄 없는 `raw/` 폴더에도 제출본이 있다** — "
            "범위를 넓혀 다시 훑었다."),
    "how": ("`git log --all --diff-filter=A` 로 추가된 적 있는 모든 경로를 뽑아 `/raw/`(밑줄 없음)를 골라내고, "
            "제출본·표지 성격의 파일을 `git show <commit>:<path>` 로 읽어 태그를 `<[^>]+>` → 공백으로 걷은 뒤 "
            "`Anthropic`·`OpenAI`·`xAI` 를 대소문자 무시로 셌다."),
    "files": {
        "aff11c2:validation/offb-24b-2026-09-11/raw/AMZN-10Q-2026Q2.txt": {"Anthropic": 31, "OpenAI": 15, "xAI": 0,
                                                                          "note": "amzn-20260630.htm 과 같은 10-Q 의 다른 포착본 — 건수가 같다. 새 사실 없음."},
        "aff11c2:validation/offb-24b-2026-09-11/raw/SPCX-10Q-2026Q2.txt": {"Anthropic": 0, "OpenAI": 0, "xAI": 119,
                                                                           "note": "spcx-20260630.htm 과 같은 10-Q. 새 사실 없음."},
        "b96477d:validation/f6-fx-16-2026-09-10/raw/20F-BABA-FY2026.txt": {"Anthropic": 0, "OpenAI": 0, "xAI": 0},
        "b96477d:validation/f6-fx-16-2026-09-10/raw/20F-TSM-FY2025.txt": {"Anthropic": 0, "OpenAI": 0, "xAI": 0},
        "ff75add:validation/mcap-36-2026-09-11/raw/cover-alphabet-R1.htm.htm": {"Anthropic": 0, "OpenAI": 0, "xAI": 0,
                                                                                "note": "**alphabet 10-Q 표지 조각이다**(R1 COVER PAGE · 2026-06-30 · 문서 메타와 주식 수만). 본문이 아니다."},
        "ff75add:validation/mcap-36-2026-09-11/raw/cover-meta-R1.htm.htm": {"Anthropic": 0, "OpenAI": 0, "xAI": 0},
        "ff75add:validation/mcap-36-2026-09-11/raw/cover-palantir-R1.htm.htm": {"Anthropic": 0, "OpenAI": 0, "xAI": 0},
        "d900e2f:validation/f6-fx-16-2026-09-10/raw/edgar-R4-FY2025-income-statement.htm": {"Anthropic": 0, "OpenAI": 0, "xAI": 0},
    },
    "result": ("**새로 나오는 사실이 없다.** 넓힌 범위에서 나온 제출본은 이미 본 Amazon·SpaceX 10-Q 의 다른 포착본이거나 "
               "Alibaba·TSMC 20-F(0건)이거나 표지·개별 표 조각이다. 등록할 것이 없고 **점수에 닿는 변화도 없다.**"),
    "alphabet_correction": ("FIX-58 2단계가 `알파벳 제출본이 어느 커밋에도 보존돼 있지 않다` 고 적었는데 **표지 조각은 "
                           "있다**(위 cover-alphabet-R1). 다만 `Anthropic` 출현 여부를 다투는 것은 **본문**이고 표지에는 "
                           "문서 메타와 주식 수만 있어 그 판정을 받칠 수 없다. 서술을 `본문이 보존돼 있지 않다` 로 좁힌다 — "
                           "TEN-RA5-01 의 전제와 발동 조건은 그대로다."),
}

AWS_ANTHROPIC_FOUND = {
    "what": "anthropic 컴퓨트 약정(AWS 증액)",
    "where": f"Amazon 10-Q Accounting Pronouncements 앞 문단 ({AMZN_10Q})",
    "fact": ("`In Q2 2026, AWS and Anthropic announced an expansion of the strategic collaboration and existing "
             "multi-year commitment by more than $ 100.0 billion over 10.0 years, which includes contractual "
             "obligations related to the performance of AWS chips.`"),
    "registered": False,
    "why_not": (f"[{M} · {R8A} low] **같은 문단의 OpenAI 증액 문장만 목록에 있었고 이 Anthropic 증액 문장이 빠져 있었다.** "
                "`anthropic.F8.f8anth33` 이 FIX-53 3단계에서 이미 이 문면으로 라벨을 고쳤고(`기존 다년 약정 위의 증액` · "
                "`more than` 이라 하한), `anthropic.offbalance_B.v15` 300,000M 이 그 AWS 몫을 담고 있다. "
                "값은 바뀌지 않고 목록의 빠진 자리를 채운다."),
}

TAG_STRIP_METHOD = (
    f" [{M} · {R8A} low] **어휘 건수의 재현 방법** — 보존 파일을 `git show <commit>:<path>` 로 읽고 "
    "정규식 `<[^>]+>` 를 공백으로 바꿔 태그를 걷은 뒤 `html.unescape` 로 엔티티를 풀고 공백을 하나로 줄인 다음 "
    "대소문자를 무시하고 센다. **작업 트리 사본이 아니라 커밋된 사본을 본다.** 이 문서는 페이지 데이터(JSON)가 본문과 "
    "같은 문장을 한 번 더 실어 건수가 문단 수보다 크게 나온다 — 그 중복까지 포함한 수다.")

F7_FIX = {
    # 두 판본에 모두 있는 문면을 표식으로 쓴다 — FIX-58 문장과 이 정정본을 같이 잡아야 재실행이 멱등이다.
    "marker": "Cloud Services Agreements with Anthropic PBC",
    "new": (f"🆕 [{M} 정정 · {R8A} medium] **보존 원문에 Anthropic 클라우드 계약이 있다 — 다만 v1.5 가 말한 그 계약이라고 "
            f"단정하지 않는다.** SpaceX S-1/A 가 `in May 2026, we entered into Cloud Services Agreements with Anthropic "
            f"PBC … approximately 325,000 NVIDIA GPUs … $1.25 billion per month through May 2029` 를 공시한다({SPCX_S1A}). "
            f"위 v1.5 불릿의 `$6.7B 클라우드 계약` 과 **동일성을 보존 원문이 주지 않는다**(금액 체계가 다르고 v1.5 가 "
            f"상대·시점을 적지 않는다) — FIX-58 2단계가 같은 계약으로 읽은 것은 지나친 단정이었다. **`상대 미공시` 는 "
            f"그대로 남는다.** 관계자 거래는 따로 공시돼 있다: 보존 10-Q 주석 17 이 Tesla Megapack 구입 $295M(3개월)·"
            f"$329M(6개월)과 2025-12-31 기준 Megapack $506M·Cybertruck $131M 을 적고 "
            f"`Other transactions with Tesla and other related parties during the six months ended June 30, 2026 and "
            f"2025 were immaterial.` 로 맺는다. **다만 `규모가 작다` 로 뭉갤 수 없다** — 같은 주석에 Valor Equity "
            f"Partners(이사 Antonio Gracias)와의 AI 인프라 장비 리스가 있다 — `The Valor Transaction was deemed to be "
            f"a failed sale-leaseback transaction` 이고 **2026-06-30 기준 관련 부채가 유동 $2,039M · 비유동 $11,290M** "
            f"(직전 2025-12-31 은 $455M · $4,052M)이며 이자비용이 3개월 $327M · 6개월 $513M 이다({SPCX_10Q}). "
            f"관계자 거래를 `immaterial` 로 맺는 문장은 **Tesla 및 그 밖의 관계자에 대한 `기타` 거래**를 가리키고 "
            f"Valor 리스는 그 문장 앞에 따로 적혀 있다. **F7 0 은 그대로**다 — 별표 I 두 축(조달 의존 고객 비중 · "
            f"내 돈이 돌아오는가)에 닿는 사실이 아니고 Valor 는 고객이 아니라 장비 임대인이다."),
}

C03_SUCCESSION_NOTE = {
    "what": (f"[{M} · {R8A} medium] **F2 판단들은 `이번 실행이 잣대를 바꾸지 않았다` 는 요건을 엄밀히는 못 채운다.** "
             "이번 실행이 C-03 을 `paths_with_generation_gap_5` 로 확정하면서 F2 5점 칸의 기준을 "
             "`AA 종합 1위` 에서 `성능 도약이 세대 격차 수준` 으로 **교체**했다. AGENTS.md 71행의 승계 예외는 "
             "`이번 실행이 그 판단에 쓰인 잣대를 바꾸지 않았을 때` 를 요구한다."),
    "why_scores_unchanged": ("**점수는 바꾸지 않는다.** 14개사 F2 는 전부 `carried` score 판단이고, 새 기준(세대 격차)의 "
                             "판정은 이번 실행에서 하지 않았다 — 경로 수 산출은 판정 입력이 들어올 때 compute_f2 가 한다. "
                             "잣대를 바꾼 결과를 점수에 반영하지 않았으므로 지금 하향·상향할 근거가 없다."),
    "how_it_is_handled": ("예외로 조용히 넘기지 않고 **긴장으로 든다** — TEN-RA4-01(F2 하네스 표기, 판단 넷)과 "
                          "TEN-RA-02·TEN-RA3-01 이 C-03 계열이고 재검토 시점 2026-11 이 붙어 있다. "
                          "즉 요건을 못 채우는 자리를 **기록으로 대신 메운다**."),
    "recorded_at": DATE,
}


# ------------------------------------------------------------------ 적용

def fix_rules(rules: dict) -> list[str]:
    out: list[str] = []
    f9 = rules["policies"]["f9"]
    if f9.get("g1_bep_retreat_precedence") != BEP_PRECEDENCE:
        f9["g1_bep_retreat_precedence"] = json.loads(json.dumps(BEP_PRECEDENCE))
        out.append("policies.f9.g1_bep_retreat_precedence (bep_retreat 가 C-20 보다 앞선다 · 사용자 결정)")

    nc = rules["policies"]["f6"]["net_cash"]["securities_scope"]
    if nc["how_to_measure"] != HOW_TO_MEASURE:
        nc["how_to_measure"] = HOW_TO_MEASURE
        out.append("securities_scope.how_to_measure: `대차대조표 줄만` 을 주석 분할과 맞게 좁힘")
    if nc.get("remainder_sensitivity") != REMAINDER_SENSITIVITY:
        nc["remainder_sensitivity"] = json.loads(json.dumps(REMAINDER_SENSITIVITY))
        out.append("securities_scope.remainder_sensitivity: 잔여분 민감도 네 회사 (밴드 불변)")

    tensions = rules["open_tensions"]
    cur = [t for t in tensions if t["id"] == TEN_RA5_02["id"]]
    if not cur:
        tensions.append(json.loads(json.dumps(TEN_RA5_02)))
        out.append("+ open_tensions TEN-RA5-02 (openai.F9 경로 · 상향 가능)")
    elif cur[0] != TEN_RA5_02:
        tensions[tensions.index(cur[0])] = json.loads(json.dumps(TEN_RA5_02))

    ra4 = find(tensions, "id", "TEN-RA4-01")
    c03_line = (f" [{M} · {R8A} medium] **이 긴장은 승계 예외를 대신 메우는 자리다.** 이번 실행이 C-03 을 확정하며 F2 "
                "5점 칸의 잣대를 `AA 종합 1위` 에서 `성능 도약 세대 격차` 로 교체했으므로, F2 판단들은 "
                "`이번 실행이 잣대를 바꾸지 않았다` 는 AGENTS.md 71행 요건을 엄밀히는 못 채운다. 점수는 바꾸지 않고"
                "(전부 carried 이고 새 기준의 판정을 하지 않았다) 재검토 시점과 함께 여기 등록해 둔다 — "
                "rules.policies.f6 밖의 기록은 `succession_exception_gap` 에 있다.")
    if c03_line.strip() not in ra4.get("note", ""):
        ra4["note"] = ra4.get("note", "") + c03_line
        out.append("TEN-RA4-01: note 에 C-03 승계 예외 요건 기록")

    c03 = find(rules["decisions"], "id", "C-03")
    if c03.get("succession_exception_gap") != C03_SUCCESSION_NOTE:
        c03["succession_exception_gap"] = json.loads(json.dumps(C03_SUCCESSION_NOTE))
        out.append("decisions C-03: succession_exception_gap (F2 승계 예외 요건을 못 채운다는 사실)")

    c26 = find(rules["decisions"], "id", "C-26")
    if C26_ADD.strip() not in c26["recommendation"]:
        c26["recommendation"] = c26["recommendation"] + C26_ADD
        out.append("decisions C-26: 분자·분모의 기준일·성질 차이를 한 줄로 합침")
    return out


def fix_observations(doc: dict) -> list[str]:
    items = doc["items"]
    out: list[str] = []

    # --- S3 raw/ 범위 확대 주사 + AWS–Anthropic 문장 + 태그 제거 방법
    for cid in ("anthropic", "openai"):
        changed = 0
        for metric in ("fcf_ttm", "cash", "net_cash", "debt_ebitda", "operating_margin_ttm"):
            o = find(items, "observation_id", f"{cid}.{metric}.priv31")
            cs = o["basis"]["checked_scope"]
            cp = cs["counterparty_filings"]
            if cp.get("widened_sweep") != RAW_SWEEP2:
                cp["widened_sweep"] = json.loads(json.dumps(RAW_SWEEP2))
                changed += 1
            if not any(f["what"] == AWS_ANTHROPIC_FOUND["what"] for f in cp["found"]):
                cp["found"].append(json.loads(json.dumps(AWS_ANTHROPIC_FOUND)))
                changed += 1
            if TAG_STRIP_METHOD.strip() not in cs["preserved_release"]:
                cs["preserved_release"] = cs["preserved_release"] + TAG_STRIP_METHOD
                changed += 1
        if changed:
            out.append(f"{cid} priv31: raw/ 범위 확대 주사 · AWS–Anthropic 문장 · 태그 제거 방법 ({changed}곳)")
    return out


def fix_judgments(doc: dict) -> list[str]:
    out: list[str] = []
    f7 = find(doc["items"], "judgment_id", "spacex-xai.F7")
    idx = [i for i, e in enumerate(f7["evidence"]) if F7_FIX["marker"] in e]
    assert len(idx) == 1, "spacex-xai.F7 클라우드 계약 줄"
    if f7["evidence"][idx[0]] != F7_FIX["new"]:
        f7["evidence"][idx[0]] = F7_FIX["new"]
        out.append("spacex-xai.F7: 계약 동일성 단정 철회 · 관계자 거래 문면을 주석대로 (점수 0 불변)")

    f8 = find(doc["items"], "judgment_id", "anthropic.F8.f8anth33")
    narrow = "**알파벳 제출본 본문이 저장소 어느 커밋에도 보존돼 있지 않다**"
    for i, e in enumerate(f8["evidence"]):
        if "알파벳 제출본이 저장소 어느 커밋에도 보존돼 있지 않다" in e:
            f8["evidence"][i] = e.replace(
                "**알파벳 제출본이 저장소 어느 커밋에도 보존돼 있지 않다**",
                narrow + f" — [{M} 정정] 10-Q 표지 조각(`ff75add:validation/mcap-36-2026-09-11/raw/"
                         "cover-alphabet-R1.htm.htm`, 2026-06-30 COVER PAGE)은 있으나 문서 메타와 주식 수만 담아 "
                         "`Anthropic` 출현 여부를 받칠 수 없다")
            out.append("anthropic.F8.f8anth33: `보존돼 있지 않다` 를 `본문이 없다` 로 좁힘 (표지 조각은 있다)")
            break
    return out


def fix_run(run: dict) -> list[str]:
    out: list[str] = []
    a = run["assumptions"]
    line = (f"[{M} · 사용자 결정 2026-09-17] **openai.F9 경로를 현행 유지**했다. 비 Claude 판정자(Gemini)가 C-20 우선"
            "(F9 -2 · 총점 4)으로 판정했으나 사용자가 현행 -4 유지 + 긴장 등록을 골랐다. 우선순위 문면은 "
            "`policies.f9.g1_bep_retreat_precedence`(채점규칙 470·494·603행), 반대 의견과 상향 가능성은 "
            "**TEN-RA5-02**(2026-11 · 비 Claude 세션)에 있다. anthropic 과의 차이는 회사 성질이 아니라 판단 입력 "
            "한 칸(`bep_retreat` no 대 yes)이다.")
    if line not in a:
        a.append(line)
        out.append("+ assumptions openai.F9 경로 결정과 긴장")
    closing = (f"[{M}] **이 라운드는 여기서 끝난다.** 사용자가 2026-09-17 에 선택지 넷 중 `FIX-59 만 하고 승인` 을 "
               "골랐다 — 6·7·8차 연속 점수 변경이 0 이고 남은 발견이 전부 기록 수준이라는 근거다. 9차 리뷰는 하지 않고 "
               "조율자 검증 뒤 사용자 승인으로 간다. 남은 기록성 지적은 미결(C-23·C-25~C-28)과 긴장"
               "(TEN-RA5-01·TEN-RA5-02 포함)으로 옮겨 **2026-11 재채점의 입력**으로 쓴다.")
    if closing not in a:
        a.append(closing)
        out.append("+ assumptions 라운드 종료 결정과 근거")
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

    jud = load(RUN / "judgments.json")
    jc = fix_judgments(jud)
    validate_judgments(jud, registry, load_rules("v1.7").payload, RUN_ID)
    dump(RUN / "judgments.json", jud)

    run = load(RUN / "run.json")
    runc = fix_run(run)
    run["rule_hash"] = load_rules("v1.7").hash
    validate_run(run, RUN_ID)
    dump(RUN / "run.json", run)

    for title, items in (("규칙", rc), ("관측", oc), ("판단", jc), ("실행", runc)):
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
