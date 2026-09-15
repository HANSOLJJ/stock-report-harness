# FIX-54 2단계: 3차 리뷰 A(qwen·codex) 반영 — openai F4 긴장 · Spectrum 구성 · 결측 라벨 · 설명 정정 · 1단계에서 남긴 셋 (점수 불변)
"""보존 원문만 읽는다. 신규 조회 없음. 대조한 원문 위치는 각 기록에 적었다.

- 3cf9799:validation/offb-24/_raw/spcx-20260630.htm — Note 6 Spectrum Transactions · Note 16 Unconditional Obligations · MD&A Spectrum Transaction
- 3cf9799:validation/offb-24/_raw/baba-20260331.htm — Note 5(수행의무 문장) · Note 11(Debt investments)
- ffaf318:validation/priv-arr-17b/_raw/ 두 회사 조달 발표 — 재무 수치 검색
- validation/f6-avail-15/_raw/ AAPL·TSM companyfacts
- E:/…/AI_company_analysis_factor 채점규칙·채점표 v1.5(349·382·543행, 표 750~752행, HTML 1014·1015행)

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
DATE = "2026-09-15"
M = "FIX-54 2단계"
REVIEW_A = "obsreg 3차 리뷰 A(기준 04439f7 · review 2088a21)"
SPCX_10Q = "3cf9799:validation/offb-24/_raw/spcx-20260630.htm"
BABA_20F = "3cf9799:validation/offb-24/_raw/baba-20260331.htm"


def load(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def dump(p: Path, d: dict) -> None:
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


# ------------------------------------------------------------------ 판단

def fix_judgments(jud: dict) -> list[str]:
    by = {j["judgment_id"]: j for j in jud["items"]}
    changed = []

    ev = by["openai.F4"]["evidence"]
    if not any(f"[{M}]" in e for e in ev):
        ev[0] = ev[0].replace("OpenAI 공개 InferenceX 결과에서", "OpenAI 공개 InferenceX 결과(발표 — OpenAI)에서", 1)
        assert "(발표 — OpenAI)" in ev[0]
        assert ev[1].startswith("자기 모델이 아닌 외부 오픈모델")
        ev[1] = "(발표 — OpenAI, 같은 InferenceX 결과) " + ev[1]
        assert ev[2].startswith("배치 계획(Broadcom)")
        ev[2] = "(계획) " + ev[2]
        ev.append(f"📐 [{M}] 표기 — `(발표 — OpenAI)` 는 이해당사자 발표라 1차 근거가 아니고(채점규칙 382행), ④ 는 가점이라 실측만 센다(349행). "
                  "`(계획)` 은 배치 계획이다. 머리줄의 `초기 출하` 를 받치는 출하 실적·독립 측정은 저장소에 없다. 점수 4 는 승계 그대로이고 TEN-RA3-01 로 2026-11 재검토한다.")
        changed.append("openai.F4 evidence (발표·계획 표기)")

    ev = by["spacex-xai.F9.obsreg25"]["evidence"]
    old2 = "판정 근거 2 — 무조건 약정 중 Spectrum 분은 현금과 Class A 보통주 혼합 지급이고 분해가 미공시다"
    if old2 in ev:
        i = ev.index(old2)
        ev[i] = (f"~~{old2}~~ (superseded [{M}] — 틀린 문장이다) 판정 근거 2 — 약정표(Note 16)는 Spectrum 분을 `payable in cash and in the Company's "
                 "Class A common stock` 이라고만 적고 연도별 금액에서 따로 떼지 않는다. 거래 구성은 같은 10-Q MD&A 에 있다 — 총 약 $19.6B = 주식 약 $11.1B"
                 "(Class A 약 261.8M주 × $42.40, 인수 종결 때 발행) + 지정 EchoStar 채무 상환 최대 $8.5B(미달분 현금). 신용계약 지급은 2026년 $1,241M 중 "
                 "$856M 기지급(선급자산)·2027년 $828M. **약정표 $27,955M 안에서 Spectrum 이 연도별로 얼마인지는 문면으로 정해지지 않는다.**")
        j = next(k for k, e in enumerate(ev) if e.startswith("그럼에도 yes 인 이유"))
        ev[j] = ev[j] + (f" [{M}] 주식 지급분 약 $11.1B 가 표 안에 들어 있다고 보고 빼면 커버리지는 약 2.57, Spectrum 잔여분(주식 11.1 + 채무상환 8.5 + 신용계약 "
                         "잔여 1.21 ≈ $20.8B)을 모두 빼면 약 5.4 다. 셋 다 1 이상이라 G4 결과는 같고, spacex-xai G4 는 G1 실패 경로의 진단이라 점수에 닿지 않는다. "
                         "B종이 현금 부담만인지는 규칙이 정하지 않는다 — spacex-xai.offbalance_B.obsreg25 basis.spectrum.")
        changed.append("spacex-xai.F9.obsreg25 evidence (Spectrum 구성)")

    ev = by["alibaba.F9.obsreg25"]["evidence"]
    original41 = ("🆕 8/23 $10.2B 증자 발표(710M주, 할인 -8.4%, 희석 3.70%, 전액 풀스택 AI) — 완충 약 $41B로 확대. 조달은 소진을 메꾸는 것이지 줄이는 게 아니다 · "
                  "다만 Anthropic의 최대 허들(상장 전 증시)을 알리바바는 선제 조달로 지웠다")
    struck41 = (f"~~완충 약 $41B로 확대~~ (superseded [{M}] — v1.5 서술. 엔진 완충은 현금 US$19,068M + 확정 미인출 여신 US$3,330M = 22,398M"
                "(2026-03-31 관측)이다. 8월 증자는 현금 관측 기준일 뒤 사건이라 이 완충에 들어 있지 않다)")
    target41 = original41.replace("완충 약 $41B로 확대", struck41, 1)
    k = next(i for i, e in enumerate(ev) if "완충 약 $41B로 확대" in e)
    if ev[k] != target41:
        ev[k] = target41
        changed.append("alibaba.F9.obsreg25 evidence ($41B superseded)")
    return changed


# ------------------------------------------------------------------ 규칙

TEN_RA3_01 = {
    "id": "TEN-RA3-01",
    "status": "open",
    "recheck_at": "2026-11",
    "review_finding": f"RA3-01(qwen medium) · {REVIEW_A} · 체크리스트 Q05·Q09 fail",
    "judgment_ids": ["openai.F4"],
    "subject": "openai F4 4점의 3→4 상향 근거가 이해당사자 발표이고 배치 계획이 섞였다",
    "tension": ("openai.F4(승계 4점) 근거 첫 줄 `OpenAI 공개 InferenceX 결과에서 GB300 대비 Peak Throughput/kW …`(채점표 751행)가 상향의 1차 근거인데 "
                "OpenAI 자신의 발표다. 채점규칙 382행 `벤더 발표 벤치마크는 1차 근거가 아니다 — 독립 측정을 우선한다` · 349행 `가점은 실측만 … 근거마다 "
                "(실측)/(발표)를 표기한다` 를 어긴다. 머리줄(750행)의 `초기 출하` 는 `2026년 0.1GW 미만이라도 출하는 출하` 로 서 있는데 752행 "
                "`배치 계획(Broadcom): 2026년 0.1GW 미만 → 2027년 1.3GW → 2028년 … 5GW+` 는 계획이고, 출하 실적의 방증은 저장소에 없다(research/ 0건)."),
    "direction": "하향 가능(4 → 3). openai 총점이 2 → 1 이 되면 oracle(2)과의 13위 동률이 갈린다.",
    "rechecker": "2026-11 재채점 때 판단자(비 Claude 세션 권장 — OpenAI 는 Anthropic 경쟁사라 하향 판정에 이해상충이 있다).",
    "why_carried_exception": "승계 판단의 기존 논리이고 이번 실행이 F4 의 잣대를 바꾸지 않았다. 재검토 시점과 함께 등록했으므로 AGENTS.md 리뷰 범위 — 승계 판단 예외에 해당한다.",
    "score_impact_now": "없다.",
    "source_lines": ["채점규칙 349행", "채점규칙 382행", "채점표 750~752행"],
    "related_tensions": ["TEN-RA-02"],
    "note": f"[{M}] 근거란에 `(발표 — OpenAI)`·`(계획)` 표기를 붙였다. 사용자 결정(2026-09-15) — 라운드마다 새로 나오는 승계 판단 모순은 발견분만 긴장으로 등록한다.",
}


def fix_rules(rules: dict, results: dict) -> list[str]:
    changed = []
    ids = {t["id"] for t in rules["open_tensions"]}
    if "TEN-RA3-01" not in ids or next(t for t in rules["open_tensions"] if t["id"] == "TEN-RA3-01") != TEN_RA3_01:
        rules["open_tensions"] = [t for t in rules["open_tensions"] if t["id"] != "TEN-RA3-01"] + [TEN_RA3_01]
        changed.append("open_tensions TEN-RA3-01")

    cond = next(c for c in rules["policies"]["f6"]["p4"]["conditions"] if c["id"] == "nonop_share")
    sv = cond["stored_vs_recomputed"]
    table = {"unit": "저장값, 엔진 재계산값(세전 기준)"}
    for c in results["companies"]:
        p4 = (c["factors"]["F6"].get("calc") or {}).get("p4")
        if p4 and "nonop_share_stored" in p4:
            now = p4.get("nonop_share")
            table[c["company_id"]] = [p4["nonop_share_stored"], None if now is None else round(now, 4)]
    current = {
        "formula": cond["formula"],
        "since": "2026-09-14 resolution",
        "table": table,
        "table_source": "results.json F6 calc.p4 (nonop_share_stored · nonop_share) — 이 실행의 엔진 값",
        "note": ("**아래 최상위 키 중 recomputed_formula · table · which_is_used · why_signs_flip · sign_flipped · negative_denominator · "
                 "score_impact_today · where_it_does_decide 는 2026-09-11 옛 순이익 기준 산식 `(NI − OI) / NI` 의 기록이다.** 엔진은 2026-09-14 부터 "
                 "세전 기준 산식을 쓴다(resolution). 옛 기록은 왜 틀렸는지 남기려고 지우지 않는다. spacex-xai 는 세전이익이 음수라 산출하지 않는다(incompatible_basis)."),
        "recorded_by": f"{M} (3차 리뷰 D 후속, 1단계 회신에서 남긴 항목)",
    }
    if sv.get("current") != current:
        sv["current"] = current
        changed.append("nonop stored_vs_recomputed.current (세전 기준 표)")
    return changed


# ------------------------------------------------------------------ 관측

PRIV_SCOPE = {
    "anthropic": {
        "v15_raw": "SRC-v15-html FIN 표 Anthropic 행 `미공시 · 미공시 · 판정 불가 · — · —`(AI기업_채점표_v1.5.html 1014행)",
        "preserved_release": ("ffaf318:validation/priv-arr-17b/_raw/anthropic_series_h_official_2026-05-28.html — 본문에서 `cash` · `free cash` · `debt` · "
                              "`EBITDA` · `operating income` · `operating margin` 0건(`profit` 1건은 메뉴의 Nonprofits). 수치는 조달액·밸류·run-rate 뿐이다"),
    },
    "openai": {
        "v15_raw": "SRC-v15-html FIN 표 OpenAI 행 `미공시 · 미공시 · 판정 불가 · — · —`(AI기업_채점표_v1.5.html 1015행)",
        "preserved_release": ("ffaf318:validation/priv-arr-17b/_raw/openai_accelerating_official_2026-03-31.html — `cash` 1건은 `more revenue and more cashflow` "
                              "서술로 수치가 아니다. `free cash` · `debt` · `EBITDA` · `operating income` · `operating margin` 0건. 수치는 조달액 중심이다"),
    },
}
PRIV_METRICS = ("fcf_ttm", "cash", "net_cash", "debt_ebitda", "operating_margin_ttm")


def fix_observations(doc: dict) -> list[str]:
    by = {o["observation_id"]: o for o in doc["items"]}
    changed = []

    def put(o: dict, key: str, value, label: str) -> None:
        if o["basis"].get(key) != value:
            o["basis"][key] = value
            changed.append(f"{o['observation_id']} {label}")

    # 2. Spectrum
    o = by["spacex-xai.offbalance_B.obsreg25"]
    comp = next(c for c in o["basis"]["components"] if c["label"] == "무조건적 비취소 구매약정")
    new_note = ("Spectrum 거래 약정이 포함돼 있고 `payable in cash and in the Company's Class A common stock` 이다(Note 16). 연도별 표는 Spectrum 분을 따로 "
                "떼지 않는다. 거래 구성은 basis.spectrum")
    if comp["note"] != new_note:
        comp["note_superseded"] = {"text": comp["note"], "superseded_at": DATE, "why": f"{M} — 분해가 미공시라는 문장은 틀렸다(3차 리뷰 A codex high). 같은 10-Q MD&A 에 구성이 있다."}
        comp["note"] = new_note
        changed.append("spacex-xai.offbalance_B.obsreg25 components[1].note")
    put(o, "spectrum", {
        "consideration_quote": ("The total consideration for the acquisition of the Spectrum Licenses is approximately $19.6 billion, consisting of (i) approximately "
                                "$11.1 billion in equity, payable through the issuance of approximately 261.8 million shares of the Company's Class A common stock at "
                                "a fixed value of $42.40 per share, and (ii) up to $8.5 billion related to the payoff of designated EchoStar debt, with any shortfall "
                                "below $8.5 billion to be paid in cash. The allocation of cash and equity consideration is subject to certain adjustments based on "
                                "the amount of EchoStar debt satisfied at or prior to closing."),
        "commitment_table_quote": ("It also includes the Company's commitments under the Spectrum Transaction, which are payable in cash and in the Company's Class A "
                                   "common stock."),
        "credit_agreement_quote": ("Total payments expected to be made under the Spectrum Credit Agreement are $1,241 million in 2026, of which $856 million was paid as "
                                   "of June 30, 2026, and $828 million in 2027, assuming an expected closing date of November 30, 2027. … The $11.1 billion equity "
                                   "consideration will be issued at the Spectrum Acquisition Closing."),
        "prepaid": "$856M 은 Trust 에 이미 지급해 Other assets 의 선급자산으로 잡혀 있다(Note 6).",
        "locations": f"MD&A `Spectrum Transaction` · Note 6 `Spectrum Transactions` · Note 16 `Unconditional Obligations` — {SPCX_10Q}",
        "b_type_definition_check": {
            "rule_text": "채점규칙_v1.5.md 543행 `B. 미개시 약정 … 게이트 4로 — 지금 현금은 안 나가고 미래 런웨이를 갉는다`",
            "design_text": "docs/scorecard/design-guideline.md 250행 `B 미개시 확정 약정 — 계약 기간·연도별 지출·취소 조건·대응 수입을 기록하고 G4 대상 여부를 검토한다`",
            "finding": ("**B종이 현금 부담만인지, 주식으로 치르는 약정도 드는지 규칙이 정하지 않는다.** `런웨이를 갉는다`·`연도별 지출` 은 현금 부담을 시사하지만 "
                        "지급 수단을 기준으로 가르는 문장은 없다. v1.7 규칙 policies.f9 에도 B종 정의 키가 없다."),
        },
        "split_by_text": ("**약정표 $27,955M 안에서 Spectrum 이 연도별로 얼마인지 문면으로 정해지지 않는다.** 표에 Spectrum 열이 없고 주식·현금 배분도 종결 시점 채무 "
                          "상환액에 따라 조정된다. 2027년 22,244 가 주식 11.1B·채무상환 8.5B·신용계약 0.83B 를 품을 만한 크기이긴 하나 이것은 추정이다."),
        "decision": "정의 미정 · 분리 불가 → 값 29,582M 을 그대로 두고 민감도와 미결만 적는다(새 결정으로 만들지 않는다).",
        "sensitivity": {
            "as_registered": {"offbalance_B": 29582, "coverage": round(47461 / 29582, 3)},
            "exclude_equity_11_1B_if_inside_table": {"offbalance_B": 29582 - 11100, "coverage": round(47461 / (29582 - 11100), 3)},
            "exclude_all_spectrum_remaining_est": {"offbalance_B": 29582 - 20813, "coverage": round(47461 / (29582 - 20813), 3),
                                                   "remaining_est": "주식 11,100 + 채무상환 최대 8,500 + 신용계약 잔여(2026 385 + 2027 828) = 20,813 — 추정"},
            "unit": "USD million, 백로그 47,461 고정",
            "g4_result": "세 경우 모두 커버리지 1 이상 — G4 step 0 으로 같다.",
            "score_path": "spacex-xai 는 G1 실패 경로라 G4 는 진단(mode diagnostic)이고 F9 점수(-3)에 닿지 않는다.",
        },
        "review": f"{REVIEW_A} codex high",
        "recorded_at": DATE,
    }, "basis.spectrum")

    # 3a. 비상장 priv31 10건
    for cid, scope in PRIV_SCOPE.items():
        for metric in PRIV_METRICS:
            o = by[f"{cid}.{metric}.priv31"]
            put(o, "label_meaning", ("**구조적 미공시** — 공시 의무가 없는 비상장사이고(MISS-LABEL-23 구조 기준) 확인한 자료에 이 수치가 없다는 뜻이다. "
                                     "`회사가 어디에도 공개하지 않았다` 는 확인이 아니다. 라벨과 기준은 C-20(사용자 확정 2026-09-11)의 탐지 조건이라 유지한다."),
                "label_meaning")
            put(o, "checked_scope", {
                "v15_raw": scope["v15_raw"],
                "preserved_release": scope["preserved_release"],
                "not_searched": "감사 재무제표(제출 의무가 없어 보존본 없음) · 투자설명 자료 · 언론 보도 · 그 밖의 회사 게시물 — 새로 받지 않았다(외부 조회 규칙).",
                "review": f"{REVIEW_A} codex medium",
                "recorded_at": DATE,
            }, "checked_scope")

    # 3b. apple·palantir lease
    for cid in ("apple", "palantir"):
        o = by[f"{cid}.lease_liabilities.nc37"]
        if o.get("missing_type") != "unverified":
            o["basis"]["label_correction"] = {
                "was": "not_disclosed_confirmed", "is": "unverified", "corrected_at": DATE, "review": f"{REVIEW_A} codex medium",
                "why": ("확인한 것은 보존 companyfacts 의 표준 태그뿐이다. 10-Q 전문(커스텀 태그·주석·표)은 보존하지도 검색하지도 않았다. 데이터셋에 값이 없다는 것을 "
                        "발행사 미공시로 올릴 수 없다 — tsmc 가 같은 데이터셋 결측을 회사 미공시와 구별한 것과 같게 한다."),
                "score_path": ("이 라벨을 읽는 곳은 calc_f6_params._blocked_reasons(F6 P2 net_cash 가 legacy 인 사유 표시)뿐이다. C-16(G4)·C-20(G1)은 "
                               "contracted_revenue·offbalance_B·operating_margin_ttm·operating_income_ttm 만 읽는다. 점수 경로에 닿지 않는다."),
            }
            if "why_not_unverified" in o["basis"]:
                o["basis"]["why_not_unverified_superseded"] = o["basis"].pop("why_not_unverified")
            o["missing_type"] = "unverified"
            o["note"] = "NETCASH-37. net_cash 실측이 막힌 이유를 여기 남긴다 — [FIX-54 2단계] unverified(표준 태그 결측, 10-Q 전문 미검색)"
            changed.append(f"{o['observation_id']} missing_type unverified")
    o = by["apple.lease_liabilities.nc37"]
    old_why = "리스 관련 태그 39종이 모두 존재하나 값이 붙은 일자는 전부 회계연도 말이다(최근 2020-09-26 · 2021-09-25 · 2022-09-24 · 2023-09-30 · 2024-09-28 · 2025-09-27)."
    if o["basis"]["why"].startswith(old_why):
        o["basis"]["why_superseded"] = o["basis"]["why"]
        o["basis"]["why"] = ("리스 관련 태그 39종이 있다. 2020-06-27 까지는 분기말 사실도 있으나(예: FinanceLeaseLiability 2020-06-27) 그 뒤로 값이 붙은 일자는 회계연도 말뿐이다"
                             "(2020-09-26 · 2021-09-25 · 2022-09-24 · 2023-09-30 · 2024-09-28 · 2025-09-27). 2026-06-27 시점 사실이 없다. 가장 최근 값 2025-09-27 은 "
                             "9개월 전 다른 시점이라 대차대조 합산에 섞지 않는다. **데이터셋의 표준 태그 결측이지 발행사 미공시 확인이 아니다** — basis.label_correction.")
        changed.append("apple.lease_liabilities.nc37 why (2020-06-27 분기말)")

    # 3c. 승계 v15 null 라벨
    relabels = {
        "spacex-xai.ttm_per.v15": ("not_applicable", "not_applicable",
                                   "원문 `적자` — 적자 기업의 PER 은 정의되지 않는다(산출 불가). 손익은 S-1/A·10-Q 에 공시돼 있어 미공시가 아니다."),
        "anthropic.runway_years.v15": (None, "indeterminate",
                                       "원문 `판정 불가` — 런웨이는 적자 기업에 산출 대상이지만 선행 입력(FCF)이 없어 만들 수 없다. 회사가 런웨이를 미공시했다는 뜻이 아니다."),
        "openai.runway_years.v15": (None, "indeterminate",
                                    "원문 `판정 불가` — 런웨이는 적자 기업에 산출 대상이지만 선행 입력(FCF)이 없어 만들 수 없다. 회사가 런웨이를 미공시했다는 뜻이 아니다."),
        "palantir.net_borrowing_ttm.v15": (None, "unverified",
                                           "원문 `없음` 은 미공시가 아니라 v1.5 표기다. 상장사라 구조 기준이 서지 않고(MISS-LABEL-23 2.1), 최신 차입 태그 부재만으로 순증 0 도 확정하지 않는다."),
        "alibaba.offbalance_B.v15": (None, "unverified",
                                     "원문 `미확인` 은 v1.5 작성자가 확인하지 않았다는 뜻이다. 실제 약정 금액은 20-F Note 27 에 있고 alibaba.offbalance_B.obsreg25 가 대체했다."),
        "spacex-xai.offbalance_B.v15": (None, "unverified",
                                        "원문 `미확인` 은 v1.5 작성자가 확인하지 않았다는 뜻이다. 약정은 S-1/A Note 11·10-Q Note 16 에 있고 spacex-xai.offbalance_B.obsreg25 가 대체했다."),
    }
    for oid, (status, mtype, why) in relabels.items():
        o = by[oid]
        if o.get("missing_type") == mtype and (status is None or o["status"] == status):
            continue
        o["basis"] = o.get("basis") or {}
        o["basis"]["label_correction"] = {
            "was": {"status": o["status"], "missing_type": o.get("missing_type")},
            "is": {"status": status or o["status"], "missing_type": mtype},
            "why": why,
            "status_note": (None if status else "status 에는 `산출 불가`·`미확인` 값이 없어 not_disclosed 를 두고 missing_type 이 이유를 말한다 — undrawn_credit.fix54 와 같은 방식이다."),
            "superseded_enough": ("대체된 관측이라 엔진은 읽지 않는다(ObsLookup 은 verified 를 먼저 고른다). superseded 표시만으로 점수는 안전하지만 라벨이 미공시의 증거처럼 "
                                  "읽히므로 고쳤다." if "대체됨" in (o.get("note") or "") else None),
            "score_path": "점수 경로에 닿지 않는다 — 이 지표·회사의 결측 라벨을 읽는 계산이 없다(C-16·C-20 은 contracted_revenue·offbalance_B·영업손익만, 그리고 verified 대체 관측이 먼저 잡힌다).",
            "corrected_at": DATE, "review": f"{REVIEW_A} codex medium",
        }
        o["basis"]["label_correction"] = {k: v for k, v in o["basis"]["label_correction"].items() if v is not None}
        if status:
            o["status"] = status
        o["missing_type"] = mtype
        changed.append(f"{oid} relabel → {status or o['status']}/{mtype}")

    # 4. 설명 정정
    o = by["alibaba.contracted_revenue.obsreg25"]
    old_limit = "선언된 면제는 1년 이하 계약과 청구권 기준 계약만 덮는다. 1년 초과 계약분은 면제로 설명되지 않으며 Note 5 의 '중요하지 않다' 서술이 그 자리를 메운다"
    if o["basis"].get("limit") == old_limit:
        o["basis"]["limit_superseded"] = {"text": old_limit, "superseded_at": DATE, "why": f"{M} — Note 5 문장을 잔여 의무 설명으로 잘못 읽었다({REVIEW_A} codex medium)."}
        o["basis"]["limit"] = ("선언된 면제는 1년 이하 계약과 청구권 기준 계약만 덮는다. **1년 초과 계약의 잔여 수행의무는 면제로 설명되지 않고 금액도 없다.** "
                               "Note 5 의 `not material` 은 `The amount of revenue recognized for performance obligations satisfied (or partially satisfied) in prior "
                               "periods for contracts with expected duration of more than one year … were not material` — **과거에 이행한 의무에서 당기에 인식한 매출**이 "
                               f"중요하지 않다는 뜻이지 남은 의무가 작다는 뜻이 아니다({BABA_20F}). 전문 검색으로 확인한 RPO 수치 부재 판정은 그대로다.")
        changed.append("alibaba.contracted_revenue.obsreg25 limit")

    o = by["alibaba.net_cash.nc37"]
    row = next(r for r in o["basis"]["components"]["rows"] if r["label"] == "Debt securities and loan investments")
    old = "채무증권과 **대출**이 한 줄에 섞여 있다. 대출은 시장성이 없는데 20-F 가 나누지 않는다. 시장성을 증명하지 못한 줄은 넣지 않는다"
    if row.get("why") == old:
        row["why_superseded"] = old
        row["why"] = ("채무증권과 **대출**이 한 줄(10,880 RMB백만)에 섞여 있다. **합계 전체의 완전한 시장성 분할은 없다.** Note 11 에 부분 구분은 있다 — 공정가치옵션 "
                      "전환·교환채권 RMB2,989M(공정가치 계층 Level 3), 상각후원가 채무투자 중 2033년 만기 RMB4,764M, 지분법 피투자사 주주 대출 원금 RMB5,845M"
                      f"(담보 매각으로 회수 예정). 이 부분들로 시장성 금액을 산출하지 않았고 줄 전체를 넣지 않는 판단은 그대로다({BABA_20F} Note 11·12). 값 불변.")
        changed.append("alibaba.net_cash.nc37 Debt securities row why")

    o = by["tsmc.revenue_ttm_prior.f6reg28"]
    old = o["basis"].get("why_not_filed_usd", "")
    if "70,598.8" in old:
        o["basis"]["why_not_filed_usd_superseded"] = {"text": old, "superseded_at": DATE,
                                                      "why": f"{M} — 70,598.8 은 FY2023 값이고 예시 성장률도 FY2024 대 FY2023 쌍이었다({REVIEW_A} qwen low)."}
        o["basis"]["why_not_filed_usd"] = ("FY2024 20-F(accn 0001193125-25-083423)의 공시 USD 는 88,268.0M(그 해 환율 약 32.79)이고 FY2025 20-F 의 공시 USD 는 "
                                           "121,423.5M(31.37)이다. 두 공시 USD 로 성장률을 내면 +37.56%, 같은 환율(31.37)로 내면 현지통화와 같은 +31.60% 다. "
                                           "**이번 쌍에서는 둘 다 P3 0.3+ 밴드라 점수가 갈리지 않는다** — 그래도 환율이 섞이면 성장률이 6%p 뜨므로 같은 환율 원칙을 쓴다.")
        changed.append("tsmc.revenue_ttm_prior.f6reg28 why_not_filed_usd")

    o = by["spacex-xai.revenue_ttm_prior.f6reg28"]
    label = "**2025Q2 단일 분기(2025-04-01~2025-06-30) — TTM 아님.** metric 이름은 revenue_ttm_prior 이지만 값은 분기다."
    if o["basis"].get("period_label") != label:
        o["basis"]["period_label"] = label
        o["raw"] = "2025 Q2 분기 매출 $4,071M (TTM 아님)"
        o["note"] = "F6-REG-28. 같은 분기 전년 동기 | [FIX-54 2단계] **분기값(2025Q2) — TTM 아님.** P3 분기 YoY 전용."
        changed.append("spacex-xai.revenue_ttm_prior.f6reg28 period_label")

    # 5. amazon 지연인출 소멸일 — 초안 여신 설명이 읽는 구조 필드
    o = by["amazon.undrawn_credit.fix54"]
    for c in o["basis"]["components"]:
        if c["facility"].startswith("Term Loan") and c.get("undrawn_terminates_on") != "2026-09-30":
            c["undrawn_terminates_on"] = "2026-09-30"
            changed.append("amazon.undrawn_credit.fix54 Term Loan undrawn_terminates_on")
        if c["facility"].startswith("Short-Term Credit Agreement") and c.get("matures_on_month") != "2026-10":
            c["matures_on_month"] = "2026-10"
            changed.append("amazon.undrawn_credit.fix54 364일 matures_on_month")
    return changed


def main() -> int:
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
    rc = fix_rules(rules, load(RUN / "results.json"))
    validate_rules(rules)
    dump(RULES, rules)
    run = load(RUN / "run.json")
    run["rule_hash"] = load_rules("v1.7").hash
    validate_run(run, RUN_ID)
    dump(RUN / "run.json", run)

    for title, items in (("판단", jc), ("관측", oc), ("규칙", rc)):
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
