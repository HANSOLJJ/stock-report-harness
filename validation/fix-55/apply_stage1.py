# FIX-55 1단계: 4차 리뷰 C·B·D 반영 — 승계 모순 다섯 긴장 등록 · C-11 문언 · 관측 서술 정정 · 여신 미결 등재 (점수 불변)
"""보존 원문만 읽는다. 신규 조회 없음.

- 채점규칙 v1.5 70·75·77·81·97~110·145·153·201·205·400·406·408행 · 채점표 v1.5 — E:/…/AI_company_analysis_factor
- 점수 영향은 엔진 함수(calc_qual.compute_f3)로 계산해 긴장에 적는다. **판정은 하지 않는다.**

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
DATE = "2026-09-16"
M = "FIX-55 1단계"
REVIEW_C = "obsreg 4차 리뷰 C(codex 독립 세션, 기준 ab5a053 · review 4e9071c)"
REVIEW_B = "obsreg 4차 리뷰 B(NTM Claude 독립 세션, 기준 ab5a053 · review 8e58a46)"
REVIEW_D = "obsreg 4차 리뷰 D(Gemini 독립 세션, 기준 ab5a053 · review b7debcd)"
CARRIED = "승계 판단의 기존 논리이고 이번 실행이 이 factor 의 잣대를 바꾸지 않았다. 재검토 시점과 함께 등록했으므로 AGENTS.md 리뷰 범위 — 승계 판단 예외에 해당한다."


def load(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def dump(p: Path, d: dict) -> None:
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


# ------------------------------------------------------------------ S1 긴장 다섯

TENSIONS = [
    {
        "id": "TEN-RC4-01",
        "status": "open",
        "recheck_at": "2026-11",
        "review_finding": f"RC4-01(high) · {REVIEW_C} · 체크리스트 Q12·Q13 fail",
        "judgment_ids": ["meta.F3", "anthropic.F3", "spacex-xai.F3"],
        "subject": "meta·anthropic·spacex-xai 의 F3 `imitation=partial` 이 partial 의 정의를 채우지 못한다",
        "tension": ("채점규칙 81행은 `⚠️(0.5)` 를 **자산은 있으나 아직 앞서지 못한 경우**로 정의한다 — `(1) 경쟁사가 구조적으로 못 베끼는 자산이 있고, "
                    "(2) 그 자산 덕에 실제로 앞서 있다 … 자산만 있고 아직 앞서지 못하면 ⚠️(0.5), 자산 자체가 없거나 ①의 재탕이면 ❌`. 세 판단의 근거는 "
                    "자산 자체가 복제 가능하다고 적는다 — meta `구글도 광고로 같은 걸 가능(Gemini Flash 저가) → 불인정`, anthropic `MCP는 개방 표준이라 "
                    "이미 경쟁사들이 채택했다`, spacex-xai `Colossus 규모는 자본이면 복제 가능(Stargate·Hyperion), 궤도 DC 미실현`. 같은 성질의 사유로 "
                    "amazon(97행)·microsoft(98행)·alphabet(99행)·apple(104행)·oracle(110행)은 ❌ 를 받았다. v1.5 판정표 100·101·106행이 셋에 ⚠️ 를 주므로 "
                    "**원천 내부 모순을 승계한 것**이다."),
        "direction": ("하향 가능. imitation 만 fail 로 읽으면 엔진 산술로 **anthropic 은 통과점 1.5 → 1.0 이라 F3 3 → 2**(총점 10 → 9), meta 는 2.0 → 1.5, "
                      "spacex-xai 는 2.5 → 2.0 이라 둘은 F3 3 그대로다. 이 등록은 재판정하지 않는다."),
        "rechecker": ("**anthropic 은 비 Claude 세션이 재판정한다** — Anthropic 점수이고 조율자·worker 가 Claude 라 이해상충이다(TEN-RC-02 와 같은 사유). "
                      "meta·spacex-xai 는 2026-11 재채점 때 판단자."),
        "why_carried_exception": CARRIED,
        "score_impact_now": "없다.",
        "source_lines": ["채점규칙 81행", "채점규칙 97~110행(판정표)", "채점규칙 100행", "채점규칙 101행", "채점규칙 106행"],
        "related_tensions": ["TEN-RC3-05"],
        "note": f"[{M}] 점수 가능성은 calc_qual.compute_f3 에 입력 하나만 바꿔 넣어 확인한 산술이다(validation/fix-55/apply_stage1.py). 판정이 아니다.",
    },
    {
        "id": "TEN-RC4-02",
        "status": "open",
        "recheck_at": "2026-11",
        "review_finding": f"RC4-02(medium) · {REVIEW_C} · 체크리스트 Q02·Q16 fail",
        "judgment_ids": ["openai.F1"],
        "subject": "openai F1 — 주채널은 소비자라고 적고 4점을 막는 근거는 거래 채널이다",
        "tension": ("openai.F1(승계 4점) 근거는 `[주채널: 소비자 — MAU·구독 / 보조: 거래 — OpenRouter] … ①을 결정한 건 이 소비자 채널이다` 로 시작하는데, "
                    "점수를 제한하는 두 줄은 `OpenRouter 평균 $0.74/M로 Anthropic($6.36)의 1/8.6` · `쓴 만큼 내고 언제든 갈아탈 수 있어 락인이 약함` 으로 "
                    "**거래 채널 지표**(채점규칙 408행 `OpenRouter 매출 점유율 · 평균 $/M(가격 결정력)`)다. 400행은 `락인은 채널별로 재고, ① 점수는 그중 "
                    "가장 강한 채널이 결정한다` 이고 406행의 소비자 지표는 `설치기반 · MAU · 구독 유지율 · 가격 인상 후 이탈 여부` 다. 얕은 채널로 깊은 "
                    "채널을 깎은 형태이고, anthropic F1 의 같은 계열 문제는 TEN-RC-02 로 등록돼 있다."),
        "direction": "방향 미정 — 소비자 채널 지표로 다시 재면 4 가 유지될 수도, 오르내릴 수도 있다. 4 가 틀렸다는 판정이 아니다.",
        "rechecker": "2026-11 재채점 때 판단자. TEN-RC-02(anthropic F1)·TEN-RC3-03(palantir·oracle F1)과 같은 F1 채널 기준 계열이라 함께 본다.",
        "why_carried_exception": CARRIED,
        "score_impact_now": "없다.",
        "source_lines": ["채점규칙 400행", "채점규칙 406행", "채점규칙 408행"],
        "related_tensions": ["TEN-RC-02", "TEN-RC3-03"],
    },
    {
        "id": "TEN-RC4-03",
        "status": "open",
        "recheck_at": "2026-11",
        "review_finding": f"RC4-03(medium) · {REVIEW_C} · 체크리스트 Q03 fail",
        "judgment_ids": ["spacex-xai.F5"],
        "subject": "spacex-xai F5 H=-1 의 근거가 적대의 종류가 아니라 수 비교다",
        "tension": ("spacex-xai.F5(A=+1, H=-1, 점수 3) 근거가 `동맹이 적보다 확실히 많지 않음 → 3` 이다. 채점규칙 201행 별표 C·G 는 "
                    "`적대 등급 H — 적대의 크기가 아니라 종류를 본다` 이고 205행은 `0 | 최소 | 규제 조사·소송·시장 차단이 눈에 띄지 않는다` 처럼 종류로 "
                    "칸을 나눈다. 열거된 적대(EU X DSA 벌금 · Amazon Kuiper · Blue Origin · OpenAI 머스크 소송 · 정치적 적대)를 비용형·구조형·다발형 중 "
                    "어디에 놓았는지 근거란이 적지 않는다."),
        "direction": "방향 미정 — 종류로 다시 대면 H 가 -1 에 머물 수도, 달라질 수도 있다. A 나 최종 3점을 이 등록이 판정하지 않는다.",
        "rechecker": "2026-11 재채점 때 판단자.",
        "why_carried_exception": CARRIED,
        "score_impact_now": "없다.",
        "source_lines": ["채점규칙 201행", "채점규칙 205행", "채점표 653행"],
    },
    {
        "id": "TEN-RC4-04",
        "status": "open",
        "recheck_at": "2026-11",
        "review_finding": f"RC4-04(medium) · {REVIEW_C} · 체크리스트 Q10 fail",
        "judgment_ids": ["tsmc.F3"],
        "subject": "tsmc F3 가속도 pass 의 근거가 가이던스(계획)다",
        "tension": ("tsmc.F3 근거가 `✅후발 가속도 — 매출 +31.6%(FY25) → +42.7%(FY26 가이던스), EPS +62%` 다. 채점규칙 77행은 `후발 가속도 … 계획·포지션은 "
                    "0점` 이고 145·153행은 **실측 성장률의 변화**(직전 분기 대비 성장률이 오르면 가속)를 요구한다. 가이던스는 다음 기간에 실제로 빨라졌다는 "
                    "관측이 아니다. v1.5 판정표 109행도 `+30→40%↑ 가이던스` 로 pass 를 주므로 원천 내부 모순을 승계했다."),
        "direction": "하향 가능. acceleration 만 fail 로 읽으면 통과점 2.0 → 1.0 이라 **F3 3 → 2**(tsmc 총점 10 → 9)다. 이 등록은 재판정하지 않는다.",
        "rechecker": "2026-11 재채점 때 판단자. 실측 성장률 쌍(FY26 실적)이 나오면 그 값으로 다시 잰다.",
        "why_carried_exception": CARRIED,
        "score_impact_now": "없다.",
        "source_lines": ["채점규칙 77행", "채점규칙 145행", "채점규칙 153행", "채점규칙 109행", "채점표 224행"],
        "related_tensions": ["TEN-RB-Q10"],
        "note": f"[{M}] TEN-RB-Q10 은 `성장률 하나로 가속 판정` 계열이고 이 건은 `계획을 실측으로 세움` 이라 따로 등록하되 같은 가속도 계열로 묶는다.",
    },
]


def fix_rules(rules: dict) -> list[str]:
    changed = []
    ids = {t["id"]: t for t in rules["open_tensions"]}
    for t in TENSIONS:
        if ids.get(t["id"]) != t:
            rules["open_tensions"] = [x for x in rules["open_tensions"] if x["id"] != t["id"]] + [t]
            changed.append(f"open_tensions {t['id']}")

    # RC4-05 — TEN-RC3-05 에 회수 장치 사유를 더한다(75행만 적혀 있었다).
    rc35 = next(t for t in rules["open_tensions"] if t["id"] == "TEN-RC3-05")
    add = (" **[FIX-55 1단계 · RC4-05]** 같은 판단에 두 번째 사유가 있다 — 채점규칙 70행 `\"공짜로 뿌린다\" 자체는 카운터 포지셔닝이 아니다 — 회수 장치가 "
           "있어야 한다` 이고 근거란 스스로 `오픈웨이트에는 회수 장치가 없다 … SiliconFlow·Novita·AWS Bedrock이 호스팅해 그쪽이 매출을 가져간다` 고 적는다. "
           "v1.5 판정표 102행도 `⚠️ 회수장치 없음` 으로 같은 칸에 partial 을 준다. 재검토는 75행(경쟁사 둘)과 70행(회수 장치) 두 사유를 함께 본다.")
    if add not in rc35["tension"]:
        rc35["tension"] += add
        rc35["source_lines"] = sorted(set(rc35["source_lines"]) | {"채점규칙 70행"})
        rc35["score_impact_now"] = (rc35["score_impact_now"].split(" calc_qual")[0]
                                    + " calc_qual.compute_f3 에 fail 입력을 넣어 확인했다(apply_tensions.py · apply_stage1.py). 회수 장치 사유로 읽어도 같다.")
        changed.append("TEN-RC3-05 회수 장치 사유(RC4-05)")

    # RC4-06 — C-11 이월 금지와 Q22 방증 허용의 문언을 맞춘다.
    c11 = next(d for d in rules["decisions"] if d["id"] == "C-11")
    scope_text = ("**이월 금지의 범위** — 막는 것은 (1) 영업외 비중을 ⑦ 두 축 입력이나 점수 산술에 넣는 것, (2) 비중 지표 자체를 순환금융의 증거로 세는 "
                  "것이다. 체크리스트 Q22 가 허용하는 `출처가 내 고객사일 때의 방증` 은 이월이 아니다 — 근거란에 `⑥ 소관이나 출처가 고객사라 방증` 처럼 "
                  "소관과 방증 성격을 함께 적는 문구만이고, 두 축 입력·점수는 그대로다(amazon.F7·nvidia.F7.fix52 근거란이 이 형태다). 두 문언은 충돌하지 "
                  "않으며 F7 코드는 두 축만 읽는다.")
    if c11["confirmed_model"].get("carryover_scope") != scope_text:
        c11["confirmed_model"]["carryover_scope"] = scope_text
        c11["confirmed_model"]["carryover_scope_recorded"] = f"{DATE} {M} — {REVIEW_C} RC4-06(문언 불일치)."
        changed.append("C-11 confirmed_model.carryover_scope")
    q22 = next(q for q in rules["checklist"] if q["id"] == "Q22")
    q22_tail = f" | [{M}] 방증은 근거란 문구만이고 두 축 입력·점수에는 넣지 않는다 — C-11 confirmed_model.carryover_scope 와 같은 뜻이다."
    if q22_tail not in q22.get("case", ""):
        q22["case"] = q22.get("case", "") + q22_tail
        changed.append("checklist Q22 case")
    cond = next(c for c in rules["policies"]["f6"]["p4"]["conditions"] if c["id"] == "nonop_share")
    scope_now = "F6 P4 전용. ⑦ 으로 이월하지 않는다 — 금지 범위는 C-11 confirmed_model.carryover_scope(산술 입력·증거 사용 금지, Q22 고객사 방증 문구는 허용)"
    if cond["scope"] != scope_now:
        cond["scope"] = scope_now
        changed.append("nonop_share scope 문언")

    # P4 period_basis_not_ttm — 선언대로 관측에서 판정한다(트랙 자동 목록에서 뺀다).
    pb = next(c for c in rules["policies"]["f6"]["p4"]["conditions"] if c["id"] == "period_basis_not_ttm")
    pb_note = ("기간 단위가 TTM 이 아님(연간 대체 등). **관측 basis.period_basis 로 판정한다** — 트랙 자동 목록이 아니라 자료가 정한다. "
               f"[{M} · {REVIEW_B}] 선언만 있고 `_p4()` 가 읽지 않아 listed_newly 인 spacex-xai 가 quarterly_yoy 인데도 빠졌다. "
               "이제 모든 트랙에서 관측으로 판정하므로 listed_annual 의 auto_p4_conditions 에서 뺐다(연간 관측이 스스로 annual 이라 결과는 같다).")
    if pb.get("note") != pb_note:
        pb["note"] = pb_note
        pb["judged_from"] = "observation.basis.period_basis (calc_f6_params._p4)"
        changed.append("period_basis_not_ttm note·judged_from")
    annual = rules["policies"]["f6"]["tracks"]["listed_annual"]
    if "auto_p4_conditions" in annual:
        annual.pop("auto_p4_conditions")
        annual["p4_note"] = f"[{M}] period_basis_not_ttm 은 관측 basis.period_basis 로 판정한다 — 트랙 자동 목록에 두지 않는다."
        changed.append("listed_annual auto_p4_conditions 제거")

    # C-23 — 확정 미인출 여신의 잔존 기간 요건(미결 등재만)
    c23 = {
        "id": "C-23",
        "status": "pending",
        "blocking": False,
        "affects": ["F9"],
        "summary": "런웨이 분자의 확정 미인출 여신에 잔존 기간 요건이 없다 — amazon 37.5B 중 22.5B 이 기준일 4주 뒤 소멸·만기",
        "recommendation": ("이번 실행은 기준을 바꾸지 않는다(설계 지침 6.4 는 `조건이 확인된 확정 미인출 여신` 만 요구하고 잔존 기간 요건이 없다). "
                           "다음 라운드에서 요건을 정한다 — 정하기 전까지 관측 basis.sensitivity 로 영향을 남긴다."),
        "choices": ["no_requirement_v15", "require_min_residual_term", "exclude_if_expires_before_next_recheck"],
        "implementation_status": {
            "verdict": "not_implemented",
            "checked_at": DATE,
            "checked_by": f"worker ({M})",
            "evidence": ["calc_f9._runway 는 undrawn_credit 관측값을 그대로 더한다 — 만기·소멸일을 읽지 않는다",
                         "amazon.undrawn_credit.fix54 basis.components 에 undrawn_terminates_on 2026-09-30 · matures_on_month 2026-10 이 있으나 표시용이다",
                         "amazon 은 15.0B 만 세도 런웨이 8.02년이라 세 경우 모두 G3 step 0 — 오늘 점수는 갈리지 않는다"],
        },
        "pending_recheck": {
            "what": "런웨이 분자의 확정 미인출 여신에 잔존 기간 요건을 둘지.",
            "why": f"{REVIEW_B} low — amazon 37,500M 중 22,500M 이 실행 기준일 2026-09-02 로부터 4주 안에 만기·소멸한다.",
            "trigger": "다음 라운드 또는 여신 관측이 점수를 가르는 사례가 나올 때",
            "when": "2026-11",
            "note": "등재만 하고 기준은 바꾸지 않았다. 오늘은 amazon 세 경우 모두 G3 step 0 이라 점수가 갈리지 않는다.",
        },
    }
    c23 = {k: v for k, v in c23.items() if v is not None}
    existing = next((d for d in rules["decisions"] if d["id"] == "C-23"), None)
    if existing != c23:
        rules["decisions"] = [d for d in rules["decisions"] if d["id"] != "C-23"] + [c23]
        changed.append("decisions C-23(여신 잔존 기간 요건 미결)")
    return changed


# ------------------------------------------------------------------ S3 판단·관측

def fix_judgments(jud: dict) -> list[str]:
    by = {j["judgment_id"]: j for j in jud["items"]}
    changed = []
    ev = by["spacex-xai.F9.obsreg25"]["evidence"]
    head = ("📐 [FIX-52 2026-09-15 · 값 갱신 FIX-55 1단계] **이 실행의 verified 값** — 영업손실률 -16.195%(TTM 2025-07-01~2026-06-30) · 순손실 -8,218M(TTM) · "
            "FCF -32,348M(TTM) · 현금 93,522M(2026-06-30) · 확정 미인출 여신 4,355M(spacex-xai.undrawn_credit.fix54) · **런웨이 3.03년"
            "(G3 계산 3.0258년, 임계 3년 대비 +0.86% ⚠️ 경계) · G3 step 0 · F9 -3**. 점수는 이 값으로 계산된다. ~~런웨이 2.89년(G3 계산)~~ "
            "(superseded [FIX-55 1단계] — FIX-54 가 확정 미인출 여신을 등록하기 전 값이다). 아래 `(v1.5 인용)` 라벨이 붙은 줄의 -14.9%·-$8.9B·-$32.5B·"
            "$100B·3년은 v1.5 채점표 문면이다.")
    if ev[0] != head:
        ev[0] = head
        changed.append("spacex-xai.F9.obsreg25 evidence[0] (런웨이 3.03년 갱신)")
    return changed


def fix_observations(doc: dict) -> list[str]:
    by = {o["observation_id"]: o for o in doc["items"]}
    changed = []

    # B medium — alibaba non-GAAP 런웨이 서술이 여신 등록 전 값이다.
    o = by["alibaba.fcf_ttm.cashfcf35"]
    nv = o["basis"]["non_gaap_variant"]
    note = ("20-F 가 토지사용권을 포함한 capex 와 제외한 non-GAAP 을 둘 다 준다. **GAAP 쪽(토지사용권 포함)을 등록한다** — 현금이 실제로 나간 금액이다. "
            f"[{M} 값 갱신] non-GAAP 을 쓰면 런웨이가 (19,068 + 3,330) / 6,757 = **3.31년**이고 등록값 기준은 3.10년이다. **둘 다 3년 이상이라 G3 판정은 "
            "갈리지 않는다**(step 0). ~~런웨이가 2.64년에서 2.82년이 되나 둘 다 3년 미만~~ (superseded — FIX-53 2단계가 확정 미인출 여신 3,330M 을 "
            "등록하기 전 값이다).")
    if nv.get("note") != note:
        nv["note"] = note
        nv["runway_recomputed_at"] = DATE
        changed.append("alibaba.fcf_ttm.cashfcf35 non_gaap_variant.note")

    # B low — tsmc 검산 칸이 등록된 모회사 귀속 순이익과 다른 순이익을 썼다.
    o = by["tsmc.pretax_income_ttm.nonop44"]
    cc = o["basis"]["cross_check_ni_plus_tax"]
    ni = by["tsmc.net_income_ttm.f6reg28"]["value"]
    tax = cc["tax_ttm_usd"]
    pretax = o["value"]
    gap = (ni + tax - pretax) / pretax
    if cc.get("net_income_source") != "tsmc.net_income_ttm.f6reg28":
        cc["ni_ttm_usd"] = ni
        cc["net_income_source"] = "tsmc.net_income_ttm.f6reg28"
        cc["relative_gap_superseded"] = {"value": cc["relative_gap"], "why": ("연결 전체 순이익 54,036.5(비지배 포함)로 계산해 0 에 가까웠다. 등록 관측은 "
                                                                             "모회사 귀속 54,115.5 다(FIX-54 FC-04)."), "superseded_at": DATE}
        cc["relative_gap"] = gap
        cc["note"] = (cc["note"] + f" [{M} · {REVIEW_B} low] **다른 회사와 같은 기준으로 맞췄다** — 분자는 등록된 net_income_ttm(모회사 귀속)이다. "
                      "tsmc 는 비지배지분 손실 -2,479.1 NT$백만이 세전 아래에 있어 어긋남이 +0.12% 로 남는다. 점수에는 닿지 않는다 — nonop_share 는 "
                      "세전이익과 영업이익만 읽는다.")
        changed.append(f"tsmc.pretax_income_ttm.nonop44 cross_check(relative_gap {gap:+.6f})")

    # B low — amazon 여신 잔존 기간 미결(C-23) 연결
    o = by["amazon.undrawn_credit.fix54"]
    residual = (f"[{M} · {REVIEW_B} low] 37,500M 중 22,500M(364일 5,000M · 지연인출 17,500M)이 실행 기준일 2026-09-02 로부터 4주 안에 만기·소멸한다. "
                "설계 지침 6.4 는 잔존 기간 요건을 두지 않아 규칙 위반은 아니고, 이번에 기준을 바꾸지 않았다. **미결로 등재했다 — 규칙 decisions C-23.** "
                "세 경우(37.5B·15.0B·0) 모두 G3 step 0 이라 오늘 점수는 갈리지 않는다(basis.sensitivity).")
    if o["basis"].get("residual_term_open_item") != residual:
        o["basis"]["residual_term_open_item"] = residual
        changed.append("amazon.undrawn_credit.fix54 residual_term_open_item(C-23)")

    # B low — oracle 은 G3 가 점수를 내는 유일한 미등록 기업. 다음 수집 1순위.
    o = by["oracle.undrawn_credit.fix54"]
    prio = (f"[{M} · {REVIEW_B} low] **다음 수집 1순위다.** 미등록 아홉 곳 중 oracle 만 FCF 음수라 G3 가 점수를 낸다(런웨이 1.32년, step -1). "
            "10-K 본문이 보존되면 이 한 건을 먼저 채운다. 이번에 값을 만들지 않았다 — 외부 조회 금지이고 원문이 없다.")
    if o["basis"].get("next_collection_priority") != prio:
        o["basis"]["next_collection_priority"] = prio
        changed.append("oracle.undrawn_credit.fix54 next_collection_priority")
    return changed


def fix_run(run: dict) -> list[str]:
    line = (f"확정 미인출 여신(FIX-54 S2)은 **상장 12개사만 관측으로 남겼다.** 비상장 anthropic·openai 는 관측을 만들지 않았다 — 인용할 보존 원문·source_id 가 "
            f"없어 `미확인` 조차 어느 자료를 봤는지 적을 수 없기 때문이다. 두 회사는 C-20 경로라 G3 가 생략돼 점수에 닿지 않는다. 근거는 "
            f"validation/fix-54/undrawn-credit-census.md 에 있다 [{M} · 4차 리뷰 B low — 처리 통일]")
    if line in run["assumptions"]:
        return []
    run["assumptions"].append(line)
    return ["run.json assumptions(비상장 여신 관측 부재 사유)"]


def check_f3_impacts() -> dict[str, tuple[int, int]]:
    """긴장에 적은 점수 가능성을 엔진 함수로 확인한다. 판정이 아니라 산술이다."""
    from scorecard.calc_qual import compute_f3

    class Lookup:
        def __init__(self, j: dict) -> None:
            self.j = j

        def get(self, cid: str, fid: str) -> dict:
            return self.j

    rules = load_rules("v1.7")
    jud = {j["judgment_id"]: j for j in load(RUN / "judgments.json")["items"]}
    out = {}
    for jid, key in (("meta.F3", "imitation"), ("anthropic.F3", "imitation"), ("spacex-xai.F3", "imitation"),
                     ("tsmc.F3", "acceleration"), ("alibaba.F3", "imitation")):
        j = jud[jid]
        now = compute_f3({"company_id": j["company_id"]}, Lookup(j), rules)
        alt_j = json.loads(json.dumps(j))
        alt_j["inputs"][key] = "fail"
        alt = compute_f3({"company_id": j["company_id"]}, Lookup(alt_j), rules)
        out[jid] = (now["score"], alt["score"])
        print(f"  {jid:14} {key} fail → F3 {now['score']} → {alt['score']} (통과점 {now['calc']['pass_points']} → {alt['calc']['pass_points']})")
    assert out["anthropic.F3"] == (3, 2) and out["tsmc.F3"] == (3, 2), out
    assert out["meta.F3"][1] == 3 and out["spacex-xai.F3"][1] == 3 and out["alibaba.F3"][1] == 3, out
    return out


def main() -> int:
    print("F3 단일 입력 변경 산술(판정 아님):")
    check_f3_impacts()
    registry = {c["company_id"]: c for c in load_json_strict(ROOT / "scorecard" / "companies.json")["companies"]}

    jud = load(RUN / "judgments.json")
    jc = fix_judgments(jud)
    validate_judgments(jud, registry, load_rules("v1.7").payload, RUN_ID)
    dump(RUN / "judgments.json", jud)

    doc = load(RUN / "observations.json")
    oc = fix_observations(doc)
    validate_observations(doc, registry, RUN_ID)
    dump(RUN / "observations.json", doc)

    rules = load(RULES)
    rc = fix_rules(rules)
    validate_rules(rules)
    dump(RULES, rules)

    run = load(RUN / "run.json")
    runc = fix_run(run)
    run["rule_hash"] = load_rules("v1.7").hash
    validate_run(run, RUN_ID)
    dump(RUN / "run.json", run)

    for title, items in (("판단", jc), ("관측", oc), ("규칙", rc), ("실행", runc)):
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
