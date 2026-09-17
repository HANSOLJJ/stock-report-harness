# FIX-58 2단계: 7차 리뷰 A 분담 반영 — 부재 주장의 검색 범위(상대방 제출본 포함) · 확인 불가 기록 (점수 불변)
"""보존 원문만 읽는다. 신규 조회 없음.

- Amazon 10-Q `3cf9799:validation/offb-24/_raw/amzn-20260630.htm` (Anthropic $20.0B 여신 · OpenAI 약정)
- Amazon 10-K `3cf9799:validation/offb-24/_raw/amzn-20251231.htm`
- SpaceX S-1/A `3cf9799:validation/offb-24/_raw/spcx_s1a_20260603.htm` (Anthropic 클라우드 $1.25B/월)
- SpaceX 10-Q `3cf9799:validation/offb-24/_raw/spcx-20260630.htm` (주석 17 관계자 거래)
- openai 보도자료 `ffaf318:validation/priv-arr-17b/_raw/openai_accelerating_official_2026-03-31.html`

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
M = "FIX-58 2단계"
REVIEW_A = "obsreg 7차 리뷰 A 분담(Claude 독립 세션 · 부재 주장 전수)"
AMZN_10Q = "3cf9799:validation/offb-24/_raw/amzn-20260630.htm"
SPCX_S1A = "3cf9799:validation/offb-24/_raw/spcx_s1a_20260603.htm"
SPCX_10Q = "3cf9799:validation/offb-24/_raw/spcx-20260630.htm"


def load(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def dump(p: Path, d: dict) -> None:
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def find(items: list[dict], key: str, value: str) -> dict:
    hit = [x for x in items if x.get(key) == value]
    assert len(hit) == 1, f"{key}={value} 가 {len(hit)}건"
    return hit[0]


# ------------------------------------------------------------------ S2 상대방 제출본 전수

COUNTERPARTY_SWEEP = {
    "checked_at": DATE,
    "review": f"{REVIEW_A} medium",
    "why": ("비상장 2사의 부재 주장을 **회사 자체 발표로만** 세운 자리가 있었다. 비상장사는 제출 의무가 없지만 "
            "**거래 상대방이 상장사면 그 제출본에 나온다** — 부재를 세우기 전에 보존된 상대방 제출본을 봐야 한다."),
    "scope": ("저장소에 보존된 제출본·발표문 전수(htm 기준 8건 · companyfacts 12건)에서 `Anthropic`·`OpenAI`·`xAI` 를 "
              "태그를 걷은 본문으로 훑었다. 보존된 제출본은 Amazon 10-K/10-Q · Alibaba 20-F · SpaceX S-1/A·10-Q · "
              "TSMC 20-F 뿐이다 — Alphabet·Microsoft·Oracle·NVIDIA 제출본은 어느 커밋에도 없다."),
    "hits": {
        "amzn-20260630.htm": {"Anthropic": 31, "OpenAI": 15},
        "amzn-20251231.htm": {"Anthropic": 12, "OpenAI": 0},
        "spcx_s1a_20260603.htm": {"Anthropic": 9, "OpenAI": 2},
        "spcx-20260630.htm": {"Anthropic": 0, "OpenAI": 0},
        "baba-20260331.htm": {"Anthropic": 0, "OpenAI": 0},
        "tsm-20251231.htm": {"Anthropic": 0, "OpenAI": 0},
    },
    "found": [
        {"what": "anthropic 미인출 여신", "where": f"Amazon 10-Q Note 4 Non-Marketable Investments ({AMZN_10Q})",
         "fact": ("`we entered into a financing arrangement to make available to Anthropic an aggregate facility not to "
                  "exceed $ 20.0 billion that will expire 30 months after an Anthropic liquidity event` · "
                  "`in Q2 2026, we exercised our option … investing $ 5.0 billion in Anthropic Series H nonvoting "
                  "preferred stock, which reduced the amount available under the facility to $ 15.0 billion`"),
         "registered": False,
         "why_not": "run.json 전제 참조 — 설계 지침 6.4 의 `조건이 확인된 확정 미인출 여신` 과 성격이 다르다."},
        {"what": "anthropic 컴퓨트 약정(네 번째 공급자)", "where": f"SpaceX S-1/A ({SPCX_S1A})",
         "fact": ("`in May 2026, we entered into Cloud Services Agreements with Anthropic PBC … approximately 325,000 "
                  "NVIDIA GPUs … the customer has agreed to pay us $1.25 billion per month through May 2029` · "
                  "`After the initial three-month period, the agreements may be terminated by either party upon 90 days' notice.`"),
         "registered": False,
         "why_not": ("**무조건 약정이 아니다** — 90일 통지로 어느 쪽이든 해지할 수 있어 B종(미개시 **무조건** 약정)의 "
                     "요건을 채우지 못한다. 잔여 기간 전액(2026-05~2029-05 약 36개월 × $1.25B ≈ $45B)을 약정으로 세면 "
                     "해지 가능한 계약을 확정 의무로 읽는 것이다. 사실은 관측 basis 에 적고 값은 만들지 않는다."),
         "affects": "anthropic.offbalance_B.v15 (300,000M) 은 Google Cloud·AWS 둘만 센다 — 이 네 번째가 빠져 있다."},
        {"what": "anthropic 전환사채(부채 존재)", "where": f"Amazon 10-K·10-Q ({AMZN_10Q})",
         "fact": ("`From Q3 2023 to Q4 2025, we invested $ 8.0 billion in convertible notes from Anthropic` · "
                  "2026-06-30 Amazon 장부상 전환사채 공정가치 `approximately … $ 97.9 billion`"),
         "registered": False,
         "why_not": ("Anthropic **자신의** 부채 잔액이 아니다 — Amazon 한 곳이 보유한 몫의 공정가치이고 전환분·미전환분이 "
                     "섞여 있다. `debt_ebitda` 는 부채와 EBITDA 가 둘 다 있어야 하고 EBITDA 는 어느 제출본에도 없다. "
                     "**다만 `부채 공시가 전혀 없다` 는 서술은 더 이상 쓰지 않는다.**")},
        {"what": "openai 컴퓨트 약정(AWS 몫)", "where": f"Amazon 10-Q ({AMZN_10Q})",
         "fact": ("`In Q1 2026, AWS and OpenAI Group PBC (\"OpenAI\") announced an expansion of the existing $ 38.0 billion "
                  "multi-year commitment and commercial arrangement with OpenAI by $ 100.0 billion over 8.0 years`"),
         "registered": False,
         "why_not": ("`openai.offbalance_B.v15` 이 이미 같은 구성으로 338,000M+ 를 담고 있다(Oracle $300B+ · AWS $38B · "
                     "증액 $100B). **상대방 제출본이 AWS 몫을 확인해 준다** — 값은 바뀌지 않고 근거가 회사 발표에서 "
                     "제출본으로 올라간다.")},
        {"what": "openai 조달", "where": f"Amazon 10-Q ({AMZN_10Q})",
         "fact": "`We invested $28.7 billion in OpenAI's Series C Preferred Stock for the six months ended June 30, 2026` · 이후 잔여 `$21.3 billion`",
         "registered": False,
         "why_not": "조달액이지 현금·FCF·부채가 아니다. `openai.cumulative_raised.v15` 는 v1.5 승계값이고 이번 실행이 재측정하지 않는다."},
    ],
    "not_found": ("현금·TTM FCF·TTM 영업손익·EBITDA 는 **상대방 제출본에도 없다.** 상대방은 자기 투자·약정만 적는다 — "
                  "부재 판정 다섯(cash·fcf_ttm·net_cash·debt_ebitda·operating_margin_ttm)의 결론은 그대로다."),
    "gap": ("**Alphabet·Microsoft 제출본이 보존돼 있지 않다.** anthropic 의 최대 공급자(Google Cloud)와 openai 의 "
            "최대 주주(Microsoft) 쪽을 같은 방식으로 볼 수 없다. 다음 수집 1순위다 — 긴장 TEN-RA5-01 참조."),
}

CREDIT_ASSUMPTION_OLD_FRAGMENT = "anthropic 보도자료에는 여신 관련 표현이 광역 검색으로도 0건이고"
CREDIT_ASSUMPTION_NEW_FRAGMENT = (
    f"anthropic 보도자료에는 여신 관련 표현이 광역 검색으로도 0건이지만 [{M} 정정 · {REVIEW_A} medium] "
    "**회사 자체 발표에 없을 뿐 상대방 제출본에는 있다** — 보존 Amazon 10-Q 가 "
    "`a financing arrangement to make available to Anthropic an aggregate facility not to exceed $ 20.0 billion` 과 "
    "`reduced the amount available under the facility to $ 15.0 billion` 을 공시한다. **그래도 관측으로 등록하지 않는다**: "
    "(1) 인출 가능액이 컴퓨트 납품 이정표에 따라 열리고 `At inception, there is no amount available to be drawn against` "
    "라 시작 시점에는 0 이며, (2) 인출 형태가 현금 차입이 아니라 `new Anthropic convertible notes or … Anthropic common "
    "stock` 이고, (3) 만기가 날짜가 아니라 `30 months after an Anthropic liquidity event` 라 유동성 사건 기준이다. "
    "설계 지침 6.4 의 `조건이 확인된 확정 미인출 여신` 은 기준일에 인출 가능한 확정 한도를 뜻하므로 셋 다 어긋난다. "
    "anthropic 은 C-20 경로라 G3 를 계산하지 않아 어차피 점수에 닿지 않는다. 그리고 ")


# ------------------------------------------------------------------ S4 긴장

TEN_RA5_01 = {
    "id": "TEN-RA5-01",
    "status": "open",
    "recheck_at": "2026-11",
    "review_finding": f"RA5-01(7차 리뷰 A 분담 medium) · {REVIEW_A}",
    "judgment_ids": ["anthropic.F8"],
    "subject": "anthropic.F8 이 -4 로 내려가지 않는 유일한 근거(`Alphabet 제출본에 Anthropic 0건`)를 확인할 수 없다",
    "tension": ("`anthropic.F8.f8anth33` 은 Google 몫의 훈련/서빙 구분이 미공시라 하향하지 않았고, 그 미공시의 근거로 "
                "`Alphabet 10-K(FY2025)·10-Q(2026 Q1·Q2) 본문에 Anthropic 이 0건` 을 든다. **그런데 알파벳 제출본이 "
                "어느 커밋에도 보존돼 있지 않다** — 저장소의 보존 제출본은 Amazon·Alibaba·SpaceX·TSMC 넷뿐이다. "
                "0건이라는 부재 주장 자체를 재현할 수 없다."),
    "direction": ("하향 가능(-3 → -4). 다만 **이번 실행은 하향하지 않는다** — 확인하지 못한 부재로 하향하면 "
                  "`미공시를 아니다로 읽지 않는다` 는 원칙을 그 자리에서 어긴다. 방향만 등록한다."),
    "rechecker": "**비 Claude 세션이 재판정한다** — Anthropic 점수이고 조율자·worker 가 Claude 라 이해상충이다(TEN-RC-02 와 같은 사유).",
    "third_party_recheck": "committed",
    "why_carried_exception": ("승계 판단이 아니라 **이번 실행이 만든 판단**이다(F8-ANTH-33). 그래서 예외가 아니라 "
                              "정식 긴장으로 등록하고 근거란에도 확인 불가를 적었다."),
    "score_impact_now": "없다. -3 그대로다.",
    "trigger": ("알파벳 제출본(10-K FY2025 · 10-Q 2026 Q1·Q2)이 `_raw` 에 보존되면 그 즉시 재검토한다. "
                "**다음 수집 1순위다.** 보존되면 (1) `Anthropic` 출현 여부를 재현하고 (2) 출현하면 훈련/서빙 구분을 "
                "읽어 F8 판정을 다시 댄다."),
    "related_tensions": ["TEN-RC-02"],
    "note": (f"[{M}] 7차 리뷰 A 분담이 보존 `_raw` 11곳을 전수 확인해 알파벳 제출본이 없다는 것을 밝혔다. "
             "같은 전수에서 **Amazon 제출본에는 Anthropic 이 31건** 있고 AWS 약정·전환사채·여신을 공시한다 — "
             "공급자마다 보존 여부가 갈려 한쪽만 볼 수 있는 상태다(관측 basis.counterparty_sweep)."),
}


# ------------------------------------------------------------------ 관측

def fix_observations(doc: dict) -> list[str]:
    items = doc["items"]
    out: list[str] = []

    # --- S1 amazon 계약 수입 승계 관측
    am = find(items, "observation_id", "amazon.contracted_revenue.v15")
    if am.get("missing_type") != "unverified":
        am["status"] = "not_disclosed"
        am["missing_type"] = "unverified"
        am["basis"] = {
            "label_correction": {
                "was": {"status": "parse_failed", "missing_type": None},
                "is": {"status": "not_disclosed", "missing_type": "unverified"},
                "corrected_at": DATE,
                "review": f"{REVIEW_A} medium",
                "why": ("raw 문면 `AWS 백로그(수백 $B급) — 숫자 미공시` 가 **확정 부재를 단정**하는데 같은 실행의 "
                        "`amazon.contracted_revenue.obsreg25`(496,000M, verified)가 보존 10-Q 문면 "
                        "`those commitments not yet recognized were approximately $ 496 billion as of June 30, 2026` 를 "
                        "인용한다. **숫자는 공시돼 있다** — v1.5 작성자가 찾지 못했을 뿐이다. "
                        "alibaba·spacex-xai 의 옛 B종 관측을 `미확인` 계열로 내린 것과 같은 처리다."),
                "raw_kept": "raw 는 v1.5 원문이라 고치지 않는다. 라벨만 사실에 맞춘다.",
                "status_note": ("status 에 `미확인` 값이 없어 not_disclosed 를 두고 missing_type 이 이유를 말한다 — "
                                "alibaba.offbalance_B.v15 와 같은 방식이다."),
                "superseded_enough": ("대체된 관측이라 엔진은 읽지 않는다(ObsLookup 이 verified 를 먼저 고른다). "
                                      "라벨이 미공시의 증거처럼 읽히므로 고쳤다."),
                "score_path": ("점수 경로에 닿지 않는다 — amazon G4 는 verified 대체 관측 496,000M 을 읽고 "
                               "커버리지 1.8557 · step 0 이다. 값·점수 불변."),
            },
        }
        out.append("amazon.contracted_revenue.v15: 확정 부재 단정을 `미확인` 으로 (대체 관측이 숫자를 공시한다)")

    # --- S2 상대방 제출본 전수를 비상장 관측에 남긴다
    for cid in ("anthropic", "openai"):
        changed = 0
        for metric in ("fcf_ttm", "cash", "net_cash", "debt_ebitda", "operating_margin_ttm"):
            o = find(items, "observation_id", f"{cid}.{metric}.priv31")
            if o["basis"]["checked_scope"].get("counterparty_filings") != COUNTERPARTY_SWEEP:
                o["basis"]["checked_scope"]["counterparty_filings"] = json.loads(json.dumps(COUNTERPARTY_SWEEP))
                changed += 1
        if changed:
            out.append(f"{cid} priv31 {changed}건: 상대방 제출본 전수 결과를 checked_scope 에")

    # --- S2 anthropic 부외 약정에 네 번째 공급자
    ao = find(items, "observation_id", "anthropic.offbalance_B.v15")
    fourth = (f"[{M} · {REVIEW_A} medium] **네 번째 공급자가 이 값에 빠져 있다.** 보존 SpaceX S-1/A 가 "
              f"`in May 2026, we entered into Cloud Services Agreements with Anthropic PBC … approximately 325,000 NVIDIA "
              f"GPUs … the customer has agreed to pay us $1.25 billion per month through May 2029` 를 공시한다({SPCX_S1A}). "
              "이 값 300,000M 은 v1.5 가 든 Google Cloud $200B/5년 + AWS $100B/10년 둘만 센다. "
              "**그래도 값을 늘리지 않았다** — 같은 문단이 `After the initial three-month period, the agreements may be "
              "terminated by either party upon 90 days' notice` 라고 적어 **무조건 약정이 아니다.** B종은 미개시 "
              "**무조건** 약정이고, 해지 가능한 계약의 잔여 총액(약 36개월 × $1.25B ≈ $45B)을 확정 의무로 세지 않는다. "
              "이 관측은 어차피 `incompatible_basis`(C-07)라 G4 가 비교하지 않는다 — 점수에 닿지 않는다.")
    if (ao.get("basis") or {}).get("fourth_supplier_not_counted") != fourth:
        ao["basis"] = dict(ao.get("basis") or {})
        ao["basis"]["fourth_supplier_not_counted"] = fourth
        out.append("anthropic.offbalance_B.v15: 네 번째 공급자(xAI 클라우드) 사실과 세지 않은 사유")

    # --- S3 openai 1차 출처 연결
    oa = find(items, "observation_id", "openai.arr_prior.priv31")
    link = {
        "source_id_kept": "SRC-v15-md",
        "why_not_moved": (f"[{M} · {REVIEW_A} medium] anthropic 쪽은 보존 보도자료가 값을 **그대로 인용**해서"
                          "(`our run-rate revenue crossed $47 billion`) source_id 를 그 발표로 옮겼다. openai 는 다르다 — "
                          "같은 날짜 발표문에 매출 수치가 여럿 있지만(`We are now generating $2B in revenue per month` = "
                          "연환산 약 $24B · `$1B in revenue` · `$1B per quarter` · `enterprise … more than 40% of our revenue`) "
                          "**이 관측의 값 25,000M 을 그대로 적은 문장이 없다.** 근사치가 비슷하다는 이유로 출처를 옮기지 않는다."),
        "related_primary_source": "SRC-OPENAI-FUNDING-2026",
        "what_it_says": "2026-03-31 발표문 `We are now generating $2B in revenue per month` — 연환산 약 $24B. 이 관측의 `2~4월 정체 구간` 과 시점이 겹친다.",
        "absence_claim_that_was_wrong": (
            "보존 `ffaf318:validation/priv-arr-17b/_raw/external_reporting_raw.json` 의 "
            "`openai.identified_financial_events[oai-01].note` 가 `공식 발표문에는 매출, ARR, 런레이트 수치가 일체 "
            "포함되어 있지 않음` 이라고 적고 `oai-02` 도 `공식 1차 발표치 부재` 라고 적는다. **둘 다 사실이 아니다.** "
            "그 파일은 보존 원자료라 고치지 않고, **이번 실행은 그 주장을 어디에서도 인용하지 않는다**(저장소 전체 검색 0건). "
            "openai 1차 출처 연결이 비어 있던 이유는 그 주장이 아니라 위 `why_not_moved` 다."),
        "recorded_at": DATE,
    }
    if oa["basis"].get("primary_source_link") != link:
        oa["basis"]["primary_source_link"] = json.loads(json.dumps(link))
        out.append("openai.arr_prior.priv31: 1차 출처를 옮기지 않은 사유와 틀린 부재 주장 기록")

    # --- S5 oracle 여신 주사 문면
    orc = find(items, "observation_id", "oracle.undrawn_credit.fix54")
    sweep = ("[FIX-55 2단계] 광역 정규식 주사(`Unused|Undrawn|RemainingBorrowingCapacity|LineOfCreditFacility`)를 보존 "
             "companyfacts 12개 파일에 다시 돌렸다. oracle 은 **그 정규식 기준 0건**이다. "
             f"[{M} 문면 정정 · {REVIEW_A} low] `0건` 은 **선언한 정규식 기준**이라는 뜻이고 여신 태그가 하나도 없다는 "
             "뜻이 아니다 — 같은 파일에 `us-gaap:LineOfCredit`(2011-03-14, 값 0)이 있고 정규식의 "
             "`LineOfCreditFacility` 에 걸리지 않는다. **결론은 그대로다**: 실행 기준일 근처에 인출 가능한 확정 한도를 "
             "가리키는 사실이 없다(2011년 값은 15년 전이고 0 이다). oracle 은 미등록 아홉 곳 중 **유일하게 G3 가 점수를 "
             "내는 회사**라 이 문면을 좁혀 둔다 — 런웨이 1.32년 · F9 -3 은 그대로다.")
    if orc["basis"]["broad_tag_sweep"] != sweep:
        orc["basis"]["broad_tag_sweep"] = sweep
        out.append("oracle.undrawn_credit.fix54: 주사 `0건` 을 정규식 기준으로 좁힘 (결론 불변)")

    # --- S5 palantir 부외 재검색 태그
    pal = find(items, "observation_id", "palantir.offbalance_note.v15")
    lc = pal["basis"]["label_correction"]
    add = (f" [{M} 태그 확대 · {REVIEW_A} low] 재검색 태그가 둘뿐이었다. 같은 파일에 "
           "`LesseeOperatingLeaseLiabilityUndiscountedExcessAmount` 63,201천(2025-12-31)이 더 있으나 "
           "**1단계 S2 에서 확인했듯 이 개념은 미개시 약정이 아니라 인식된 리스부채의 내재이자(할인차금)다** "
           "— 부외 약정 후보가 아니다. 셋 어느 쪽도 palantir 의 2026-06-30 부외 약정 잔고를 주지 않으므로 "
           "결론 `미확인` 은 그대로다.")
    if add.strip() not in lc["why"]:
        lc["why"] = lc["why"] + add
        out.append("palantir.offbalance_note.v15: 재검색 태그를 셋으로 넓힘 (할인차금 결론과 함께, `미확인` 불변)")

    # --- S5 apple 철회된 단정에 취소선
    ap = find(items, "observation_id", "apple.lease_liabilities.nc37")
    old_ws = ap["basis"]["why_superseded"]
    if not old_ws.startswith("~~"):
        ap["basis"]["why_superseded"] = (
            f"~~{old_ws}~~ (superseded [{M}] · {REVIEW_A} low — 같은 관측의 label_correction 이 "
            "`not_disclosed_confirmed` 를 `unverified` 로 내리며 `발행사가 분기에는 공시하지 않는다` 는 단정을 이미 "
            "철회했는데 이 줄만 단정형으로 남아 있었다. palantir 쪽은 FIX-56 2단계에서 같은 형태로 고쳐졌다. "
            "확인한 것은 보존 companyfacts 의 표준 태그뿐이고 10-Q 전문은 보존하지도 검색하지도 않았다.)")
        out.append("apple.lease_liabilities.nc37: 철회된 단정에 취소선 (palantir 과 같은 형태)")
    return out


# ------------------------------------------------------------------ 판단

def fix_judgments(doc: dict) -> list[str]:
    out: list[str] = []
    items = doc["items"]

    # --- S4 anthropic.F8 확인 불가
    f8 = find(items, "judgment_id", "anthropic.F8.f8anth33")
    marker = f"📐 **[{M}] 이 하향 차단의 근거를 확인할 수 없다.**"
    if not any(marker in e for e in f8["evidence"]):
        f8["evidence"].insert(0, (
            f"{marker} -4 로 내려가지 않는 유일한 근거는 아래 `Alphabet 10-K·10-Q 본문에 Anthropic 이 0건` 인데, "
            f"**알파벳 제출본이 저장소 어느 커밋에도 보존돼 있지 않다**({REVIEW_A} — 보존 `_raw` 11곳 전수 확인). "
            "0건이라는 부재 주장 자체를 재현할 수 없다. **점수는 -3 그대로 둔다** — 확인하지 못한 부재로 하향하면 "
            "`미공시를 아니다로 읽지 않는다` 는 이 판단 자신의 원칙을 그 자리에서 어긴다. 재검토는 **TEN-RA5-01**"
            "(2026-11 · 발동 조건은 알파벳 제출본 보존 · 방향 하향 가능 · 비 Claude 세션). "
            "다음 수집 **1순위**는 알파벳 10-K(FY2025)·10-Q(2026 Q1·Q2) 보존이다."))
        out.append("anthropic.F8.f8anth33: 하향 차단 근거가 확인 불가라는 사실 (점수 -3 불변)")

    fourth = (f"🆕 [{M}] **네 번째 외부 공급자** — 보존 SpaceX S-1/A 가 `in May 2026, we entered into Cloud Services "
              f"Agreements with Anthropic PBC … approximately 325,000 NVIDIA GPUs … $1.25 billion per month through May 2029` "
              f"를 공시한다({SPCX_S1A}). 공급자가 Google·Amazon·Microsoft 셋이 아니라 **넷이고 xAI(Grok)도 경쟁자**다 — "
              "`컴퓨트 100% 외부 + 공급자가 전부 경쟁자` 라는 이 판단의 뼈대는 그대로이고 오히려 한 건 더 늘었다. "
              "**점수 -3 은 바꾸지 않는다** — 공급자 수가 아니라 의존 구조가 점수를 정하고, 이 사실은 상대방 제출본에서 "
              "이번에 처음 확인됐다.")
    if fourth not in f8["evidence"]:
        f8["evidence"].append(fourth)
        out.append("anthropic.F8.f8anth33: 네 번째 공급자(xAI) 상대방 공시 사실 (점수 불변)")

    # --- S5 spacex-xai.F7 반대 방향 사실
    f7 = find(items, "judgment_id", "spacex-xai.F7")
    add = (f"🆕 [{M} · {REVIEW_A} low] **반대 방향 사실 — 클라우드 계약 상대가 Tesla 가 아니다.** 보존 S-1/A 가 그 계약을 "
           f"`Cloud Services Agreements with Anthropic PBC … $1.25 billion per month through May 2029` 로 공시한다"
           f"({SPCX_S1A}) — 위 `상대 미공시 · Tesla 면 관계사 순환` 우려의 조건이 성립하지 않는다. 관계자 거래는 따로 "
           f"공시돼 있고 규모가 작다: 보존 10-Q 주석 17 이 Tesla Megapack 구입 $295M(3개월)·$329M(6개월), "
           f"2025-12-31 기준 Megapack $506M·Cybertruck $131M 을 적고 "
           f"`Other transactions with Tesla and other related parties during the six months ended June 30, 2026 and 2025 "
           f"were immaterial.` 로 맺는다({SPCX_10Q}). **F7 0 은 그대로**이고 근거가 `루프 없음` 에서 "
           f"`상대가 확인됐고 관계자 거래는 immaterial` 로 올라간다.")
    if add not in f7["evidence"]:
        f7["evidence"].append(add)
        out.append("spacex-xai.F7: 클라우드 계약 상대와 관계자 거래 규모 (점수 0 불변)")
    return out


# ------------------------------------------------------------------ 규칙·실행

def fix_rules(rules: dict) -> list[str]:
    out: list[str] = []
    tensions = rules["open_tensions"]
    cur = [t for t in tensions if t["id"] == TEN_RA5_01["id"]]
    if not cur:
        tensions.append(json.loads(json.dumps(TEN_RA5_01)))
        out.append("+ open_tensions TEN-RA5-01 (anthropic.F8 근거 확인 불가)")
    elif cur[0] != TEN_RA5_01:
        tensions[tensions.index(cur[0])] = json.loads(json.dumps(TEN_RA5_01))
    return out


CONFLICT_ASSUMPTION = (
    f"[{M} · {REVIEW_A} low] **작성자 이해상충** — 이 채점표를 Anthropic 이 만든 Claude 가 작성했고 Anthropic 이 채점 "
    "대상에 들어 있다(채점규칙 384행 · HANDOVER 75행 · 운영이력 긴장 #4·#11). 실행 기록만 읽는 독자에게도 보이도록 "
    "여기 적는다 — 출처별 문구는 sources.json 의 `conflict_of_interest` 에, 제3자 재검토 약속은 초안 `알려진 한계` 절에 "
    "있다. Anthropic 점수에 걸린 긴장은 비 Claude 세션이 재판정한다(TEN-RC-02 · TEN-RC3-01 · TEN-RA4-01 · TEN-RA5-01).")

SWEEP_ASSUMPTION = (
    f"[{M} · {REVIEW_A} medium] 비상장 2사의 부재 주장을 **상대방 제출본까지 넓혀** 다시 봤다. 보존 제출본에서 "
    "`Anthropic` 은 Amazon 10-Q 31건·10-K 12건·SpaceX S-1/A 9건, `OpenAI` 는 Amazon 10-Q 15건·S-1/A 2건 나온다. "
    "여기서 **여신·컴퓨트 약정·전환사채·조달**은 확인되지만 **현금·TTM FCF·TTM 영업손익·EBITDA 는 상대방 제출본에도 "
    "없다** — 부재 판정 다섯의 결론은 그대로다. 확인된 사실은 관측 basis.checked_scope.counterparty_filings 에 적었고 "
    "어느 것도 관측으로 등록하지 않았다(사유는 각 항목의 why_not). **Alphabet·Microsoft 제출본이 보존돼 있지 않아** "
    "anthropic 의 최대 공급자와 openai 의 최대 주주 쪽은 같은 방식으로 볼 수 없다 — 다음 수집 1순위이고 "
    "긴장 TEN-RA5-01 의 발동 조건이다.")


def fix_run(run: dict) -> list[str]:
    out: list[str] = []
    a = run["assumptions"]
    hits = [i for i, x in enumerate(a) if CREDIT_ASSUMPTION_OLD_FRAGMENT in x]
    if hits:
        a[hits[0]] = a[hits[0]].replace(CREDIT_ASSUMPTION_OLD_FRAGMENT, CREDIT_ASSUMPTION_NEW_FRAGMENT)
        out.append("assumptions: 비상장 여신 사유를 `상대방 제출본에는 있다` 로 정정 (등록하지 않는 사유 셋)")
    for line, label in ((SWEEP_ASSUMPTION, "상대방 제출본 전수 결과"), (CONFLICT_ASSUMPTION, "작성자 이해상충")):
        if line not in a:
            a.append(line)
            out.append(f"+ assumptions {label}")
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
