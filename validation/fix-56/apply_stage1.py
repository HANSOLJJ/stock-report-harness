# FIX-56 1단계: 5차 리뷰 B·D 반영 — spacex-xai P2 산출(점수 변경) · 긴장 둘 · 감사 경로와 설명
"""보존 원문만 읽는다. 신규 조회 없음.

- SPCX S-1/A `3cf9799:validation/offb-24/_raw/spcx_s1a_20260603.htm` (FY2025 매출 18,674M — 감사 연결손익계산서 F-5)
- SPCX 10-Q companyfacts `validation/f6-avail-15/_raw/SPCX.companyfacts.json` (H1'26 12,508 · H1'25 8,138 · 암호자산 1,098)
- BABA 20-F `3cf9799:validation/offb-24/_raw/baba-20260331.htm` (주석 6 리스 합계 21,726 · 주석 19 유동 4,318 · 비유동 17,408)

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
M = "FIX-56 1단계"
REVIEW_B = "obsreg 5차 리뷰 B(financial-calc, review-obsreg 8b98b56)"
REVIEW_D = "obsreg 5차 리뷰 D(Gemini output-readability, review-obsreg 97034e8)"


def load(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def dump(p: Path, d: dict) -> None:
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def find(items: list[dict], key: str, value: str) -> dict:
    hit = [x for x in items if x.get(key) == value]
    assert len(hit) == 1, f"{key}={value} 가 {len(hit)}건"
    return hit[0]


# ------------------------------------------------------------------ S1 TTM 매출 관측

TTM_FULL = {
    "observation_id": "spacex-xai.revenue_ttm_full.fix56",
    "company_id": "spacex-xai",
    "metric": "revenue_ttm_full",
    "value": 23044000000.0,
    "unit": "USD",
    "as_of": "2026-06-30",
    "observed_at": "2026-09-16",
    "kind": "derived",
    "source_id": "SRC-SEC-SPCX-S1A-2026",
    "status": "verified",
    "period": {"start": "2025-07-01", "end": "2026-06-30"},
    "basis": {
        "period_basis": "ttm",
        "why_separate_metric": (
            "같은 회사의 `spacex-xai.revenue_ttm.f6reg28` 은 **분기값(2026Q2)** 이다 — P3 의 전년 동기 대조를 세우려고 "
            "그렇게 등록했다. P2 는 12개월 매출이 필요하므로 지표 이름 하나에 두 뜻을 담지 않고 갈랐다. "
            "`revenue_ttm` 이 트랙을 정하는 관측이라 id·metric 을 바꾸지 않고 새 지표를 옆에 둔다."),
        "formula": "FY2025 + H1'2026 − H1'2025",
        "components": [
            {"label": "FY2025 (2025-01-01~2025-12-31)", "value": 18674000000.0, "sign": "+",
             "source_id": "SRC-SEC-SPCX-S1A-2026", "accession": "0001628280-26-040364", "form": "S-1/A",
             "where": "감사 연결손익계산서 F-5 `Revenue … $ 18,674`(같은 값이 MD&A 연도 비교표·세그먼트 주석·지역별 주석에도 있다)",
             "quote": "In 2025, we generated revenue on a consolidated basis of $18,674 million",
             "preserved": "3cf9799:validation/offb-24/_raw/spcx_s1a_20260603.htm",
             "why_not_companyfacts": "보존 SPCX companyfacts 의 `RevenueFromContractWithCustomerExcludingAssessedTax` 에는 연간 사실이 없다(분기·반기 4건뿐). 연간 값은 S-1/A 문면에서 읽었다."},
            {"label": "H1'2026 (2026-01-01~2026-06-30)", "value": 12508000000.0, "sign": "+",
             "source_id": "SRC-SEC-SPCX-10Q-2026Q2", "accession": "0001628280-26-052535", "form": "10-Q",
             "tag": "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax",
             "preserved": "validation/f6-avail-15/_raw/SPCX.companyfacts.json"},
            {"label": "H1'2025 (2025-01-01~2025-06-30)", "value": 8138000000.0, "sign": "-",
             "source_id": "SRC-SEC-SPCX-10Q-2026Q2", "accession": "0001628280-26-052535", "form": "10-Q",
             "tag": "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax",
             "preserved": "validation/f6-avail-15/_raw/SPCX.companyfacts.json"},
        ],
        "arithmetic": "18,674 + 12,508 − 8,138 = 23,044 (백만 USD)",
        "cited_source_ids": ["SRC-SEC-SPCX-S1A-2026", "SRC-SEC-SPCX-10Q-2026Q2"],
        "same_value_elsewhere": (
            "`spacex-xai.operating_margin_ttm.f6reg28` 의 분모(basis.denominator)가 같은 23,044M 이다. 그 관측은 이 값을 "
            "비율 안에 숨겨 두었을 뿐이라 P2 가 읽을 수 없었다 — 여기서 **값 자체를 관측으로 세운다.**"),
        "consumed_by": "policies.f6.parameters.P2.input_alternatives.revenue_ttm — P2 가 `revenue_ttm` 대신 이 지표를 먼저 읽는다.",
        "why_now": f"[{M}] {REVIEW_B} high — `listed_newly` 트랙이 P2 를 만들지 않는데 P2 입력은 이 실행 안에 다 있었다. 사용자 결정 2026-09-16(C-24).",
    },
    "raw": "TTM 매출 23,044M (FY2025 18,674 + H1'26 12,508 − H1'25 8,138)",
    "note": f"{M}. 12개월 매출 — P2 전용. 분기값 `revenue_ttm` 과 다른 지표다.",
}


def fix_observations(doc: dict) -> list[str]:
    items = doc["items"]
    out: list[str] = []
    ids = {o["observation_id"] for o in items}

    # --- S1 TTM 매출 등록
    if TTM_FULL["observation_id"] not in ids:
        anchor = items.index(find(items, "observation_id", "spacex-xai.operating_margin_ttm.f6reg28"))
        items.insert(anchor + 1, json.loads(json.dumps(TTM_FULL)))
        out.append(f"+ {TTM_FULL['observation_id']} = 23,044M (TTM 매출, P2 입력)")
    else:
        idx = items.index(find(items, "observation_id", TTM_FULL["observation_id"]))
        items[idx] = json.loads(json.dumps(TTM_FULL))

    # --- S1 분기 관측에 "이제 등록됐다" 를 적는다
    q = find(items, "observation_id", "spacex-xai.revenue_ttm.f6reg28")
    ttm_c = q["basis"]["ttm_is_constructible"]
    registered = f"[{M}] 이 TTM 을 관측으로 등록했다 — `{TTM_FULL['observation_id']}`. P2 가 그 지표를 읽는다."
    if ttm_c.get("registered_as") != registered:
        ttm_c["registered_as"] = registered
        out.append("spacex-xai.revenue_ttm.f6reg28: ttm_is_constructible 에 등록 관측 id 연결")

    # --- S3 spacex-xai 순현금: 암호자산 판단 · P2 가 이 값을 읽는다는 사실
    nc = find(items, "observation_id", "spacex-xai.net_cash.nc37")
    excluded = nc["basis"]["components"]["excluded_nonmarketable_present"]
    crypto_key = "us-gaap:CryptoAssetFairValueNoncurrent"
    crypto = {
        "value": 1098000000.0,
        "as_of": "2026-06-30",
        "why": (
            "**암호자산은 유가증권이 아니다.** 정의가 더하는 것은 `현금및현금성자산 + 시장성 유가증권` 이고 "
            "암호자산은 ASU 2023-08 이후 재무제표에 따로 세우는 별개 자산군이다. 회사도 **비유동**으로만 태그했다"
            "(`CryptoAssetFairValueNoncurrent` 1,098 · 유동 태그 0건 · 원가 661 · 보유 18,712 단위). "
            "단기 처분 의도를 가리키는 표시가 없다."),
        "if_included": (
            "넣으면 순현금이 60,301 → 61,399M 이 되어 legacy 60,300 과의 수렴"
            "(basis.why_this_match_matters)이 깨진다. P2 는 80.27 → 80.22 로 움직이고 **밴드 -2 는 그대로다.**"),
        "decided_at": DATE,
        "review": f"{REVIEW_B} medium — 포함·제외 어느 목록에도 없었다.",
    }
    if excluded.get(crypto_key) != crypto:
        excluded[crypto_key] = crypto
        out.append("spacex-xai.net_cash.nc37: 암호자산 1,098 제외 판단 기록")

    comp = nc["basis"]["completeness"]
    kept = (
        f"[{M} 갱신] **이제 점수에 닿는다.** `listed_newly` 트랙이 P2 를 계산하게 바뀌어(C-24) 이 값이 "
        "EV 조정 분모로 들어간다. 비유동 운용리스 결측만큼 순현금이 **과대**라는 방향은 그대로이고, 크기는 여전히 "
        "확인하지 못했다. 다만 P2 밴드가 -2 에서 -1 로 갈리려면 순현금이 1,449,120M 이상이어야 한다"
        "((1,910,000 − 20 × 23,044)) — 리스 비유동분 규모로는 어떤 값이든 밴드가 바뀌지 않는다. "
        "**값을 고치지 않고 한계를 남긴다.** palantir 는 같은 결함(유동분 결측)으로 관측 등록 자체를 하지 않았다 "
        "— 두 회사의 처리가 다르다는 사실도 여기 남긴다."
    )
    if comp.get("why_value_kept") != kept:
        comp["why_value_kept"] = kept
        out.append("spacex-xai.net_cash.nc37: `점수에 닿는 자리가 없다` 서술을 P2 산출 이후로 갱신")

    # --- S3 alibaba 리스 줄·인용문
    ali = find(items, "observation_id", "alibaba.net_cash.nc37")
    rows = ali["basis"]["components"]["rows"]
    lease_row = {
        "kind": "lease",
        "label": "Total operating lease liabilities",
        "rmb_million": 21726.0,
        "usd_million": None,
        "line": "Total operating lease liabilities (Note 19) | 21,726",
        "quote": "Total operating lease liabilities (Note 19) 21,726",
        "where": "주석 6 리스 — 만기 스케줄 하단 합계(F-40). 5,346 + 4,397 + 3,609 + 3,017 + 2,497 + 7,971 = 26,837, `Less: imputed interest (5,111)` → 21,726",
        "cross_check": {
            "note_19": "주석 19 `Accrued expenses, accounts payable and other liabilities` — 유동 `Operating lease liabilities (Note 6) 4,318` + 비유동 `Operating lease liabilities (Note 6) 17,408` = 21,726",
            "matched": True,
        },
        "why": "차입 5행과 같은 기준으로 줄·인용문을 채웠다. 값은 바뀌지 않는다.",
        "preserved": "3cf9799:validation/offb-24/_raw/baba-20260331.htm",
        "recorded_at": DATE,
        "review": f"{REVIEW_B} medium — 리스 21,726 만 rows 에 줄·인용문이 없었다.",
    }
    existing = [r for r in rows if r.get("kind") == "lease"]
    if not existing:
        rows.append(lease_row)
        out.append("alibaba.net_cash.nc37: 리스 21,726 줄·인용문 추가 (주석 6 합계 = 주석 19 유동 4,318 + 비유동 17,408)")
    elif existing[0] != lease_row:
        rows[rows.index(existing[0])] = lease_row

    # --- S3 alibaba P2 기준일 어긋남과 민감도
    mcap = find(items, "observation_id", "alibaba.market_cap.v15")
    asof = {
        "what": (
            "**시총과 순현금의 기준일이 다르다.** 시총은 2026-09-02 이고 8월 증자(710M주, 약 $10.2B)를 이미 반영했는데, "
            "P2 의 순현금은 20-F 기준일 2026-03-31 이라 그 조달 대금이 들어 있지 않다. EV 가 그만큼 과대다."),
        "sensitivity": {
            "as_reported": {"net_cash_usd": 49838648883.73442, "ev_sales": 1.4835570590243028, "band": "0~8", "score": 0},
            "plus_august_raise_10_2b": {"net_cash_usd": 60038648883.73442, "ev_sales": 1.4148506697030425, "band": "0~8", "score": 0},
            "conclusion": "1.4836 → 1.4149 로 움직이고 **밴드 0 은 그대로다.** 첫 경계가 8 배라 멀다.",
        },
        "why_not_corrected": (
            "증자 후 순현금을 실측한 자료가 보존 원문에 없다(다음 20-F 는 FY2027). 추정치를 관측으로 세우지 않고 "
            "사실과 민감도만 남긴다."),
        "recorded_at": DATE,
        "review": f"{REVIEW_B} medium",
    }
    if mcap["basis"].get("p2_asof_mismatch") != asof:
        mcap["basis"]["p2_asof_mismatch"] = asof
        out.append("alibaba.market_cap.v15: P2 기준일 어긋남과 민감도 기록 (밴드 0 불변)")

    # --- S3 amazon 364일 여신
    amzn = find(items, "observation_id", "amazon.undrawn_credit.fix54")
    sens = amzn["basis"]["sensitivity"]
    ex364 = {"runway_years": 9.523698924731182, "g3_step": 0}
    if sens.get("ex_364_day_only") != ex364:
        sens["ex_364_day_only"] = ex364
        out.append("amazon.undrawn_credit.fix54: 364일 여신만 뺀 민감도 추가 (9.52년, step 0)")
    short_note = (
        f"[{M}] {REVIEW_B} medium — 364일 여신 5,000M 은 **2026-10 만기**이고 연장은 "
        "`may be extended for one additional period of 364 days subject to approval by the lenders` 라 "
        "회사가 단독으로 늘릴 수 없다. 이 시설만 빼면 런웨이 9.95 → 9.52년이고, **미인출 여신 37,500M 을 전부 빼도 "
        "6.73년**(현금 78,213M ÷ 연 소진 11,625M)이라 G3 step 0 과 F9 -2 가 그대로다. 잔존 기간 요건 자체는 미결 C-23 이다."
    )
    if amzn["basis"].get("short_term_facility_note") != short_note:
        amzn["basis"]["short_term_facility_note"] = short_note
        out.append("amazon.undrawn_credit.fix54: 364일 여신 만기·연장 조건과 전액 제외 민감도 서술")
    return out


# ------------------------------------------------------------------ S2·S3 판단

def fix_judgments(doc: dict) -> list[str]:
    out: list[str] = []
    f9 = find(doc["items"], "judgment_id", "openai.F9")
    ev = f9["evidence"]
    old_bep = ("게이트 1 ❌ 손익분기 목표가 2030년으로 후퇴 — 손실률 구간과 무관하게 BEP 후퇴만으로 -5"
               "(방향이 악화라 완화 조건 A 실패)")
    new_bep = ("게이트 1 ❌ 손익분기 목표가 2030년으로 후퇴 — 손실률 구간과 무관하게 BEP 후퇴만으로 "
               f"~~-5~~ (superseded [{M}] — C-06 재척도 전 척도다. 현재 척도는 **-4**) "
               "(방향이 악화라 완화 조건 A 실패)")
    old_floor = "이미 -5(바닥)이라 추가 하향 없음, 바닥이 아니었다면 더 내려갔을 항목"
    new_floor = (f"이미 ~~-5(바닥)~~ (superseded [{M}] — 현재 바닥은 **-4** 다) 바닥이라 추가 하향 없음, "
                 "바닥이 아니었다면 더 내려갔을 항목")
    rescale = (f"📐 **[{M} 재척도 표시 {DATE}] 현재 척도는 -4 다.** C-06 `proposed_v15_boundaries` 로 ⑨ G1 밴드가 "
               "-2/-3/-4 로 바뀌고 하한도 -5 → -4 가 됐다(bep_retreat -4). 엔진 경로는 `G1 BEP 후퇴 → -4` → "
               "`G3/G4 생략(이미 하한)` 이고 **F9 = -4** 다. 아래 게이트 1·마지막 줄의 `-5` 는 v1.5 문면이며 재척도 전 점수다. "
               f"판정 입력(bep_retreat=yes)은 바뀌지 않았다. {REVIEW_B} medium.")
    if rescale not in ev:
        ev.insert(0, rescale)
        out.append("openai.F9: 현재 척도 -4 를 근거란 첫 줄로")
    for old, new in ((old_bep, new_bep), (old_floor, new_floor)):
        if old in ev:
            ev[ev.index(old)] = new
            out.append("openai.F9: `-5` 문면에 superseded 표시")
    return out


# ------------------------------------------------------------------ 규칙

P2_ALT_NOTE = (
    f"[{M}] `revenue_ttm` 은 신규 상장 트랙에서 **분기값**으로 등록된다 — P3 의 전년 동기 대조를 세우려고 그렇게 쓴다"
    "(spacex-xai.revenue_ttm.f6reg28). P2 는 12개월 매출이라야 하므로 `revenue_ttm_full` 관측이 있으면 그것을 **먼저** 읽는다. "
    "지표 이름 하나에 두 뜻을 담지 않는다. 단위가 같은 지표만 대체로 선언할 수 있다(schema 가 검사한다)."
)
NEWLY_SELECT = (
    "listed 이나 **전년 TTM 을 복원할 기간 사실이 없어 P3 를 분기 전년 동기로 계산하는 기업**. 티커가 아니라 "
    "`revenue_ttm` 관측의 basis.period_basis 로 판정한다. **P1·P2 가 성립하지 않는다는 뜻이 아니다** — "
    "P2 는 입력이 있으면 계산하고(optional_parameters), P1 은 parameters_excluded_note 를 본다."
)
NEWLY_OPTIONAL_NOTE = (
    f"[{M}] P2 는 시총·순현금·12개월 매출이 다 있을 때만 만든다. 하나라도 없으면 지금까지처럼 만들지 않고 "
    "결과 `calc.parameters_optional_unmet` 에 사유를 적는다 — 없다고 F6 전체를 pending 으로 세우지 않는다."
)
NEWLY_EXCLUDED_NOTE = (
    f"[{M}] **P1 은 트랙에 두지 않았다.** 이 트랙에 든 기업의 순이익이 음수라 `requires_positive` 를 넘지 못한다"
    "(spacex-xai 순이익 TTM -8,218M). 트랙에서 뺀 것과 입력이 없어 못 만드는 것은 다르므로, 회사마다 어느 쪽인지를 "
    "결과 `calc.parameters_not_in_track.P1` 이 다시 적는다 — 흑자로 돌아서면 그 칸이 `would_compute=true` 로 바뀌고 "
    "트랙을 다시 볼 신호가 된다."
)
C24 = {
    "id": "C-24",
    "status": "resolved",
    "blocking": False,
    "affects": ["F6"],
    "summary": "신규 상장 트랙이 P2 를 만들지 않는데 P2 입력은 실행 안에 다 있다 — 계산할 것인가",
    "recommendation": "계산한다. 상장사 열두 곳에 같은 잣대를 대는 쪽이다.",
    "choices": ["p3_only_v17", "compute_p2_when_inputs_exist"],
    "chosen": "compute_p2_when_inputs_exist",
    "decided_at": DATE,
    "decided_by": "사용자",
    "scope": {
        "what_changed": (
            "`listed_newly.parameters` 에 P2 를 넣고 `optional_parameters` 로 입력이 있을 때만 만들게 했다. "
            "P2 는 `input_alternatives` 로 12개월 매출 지표(`revenue_ttm_full`)를 먼저 읽는다."),
        "score_impact": (
            "**spacex-xai F6 -1 → -3, 총점 11 → 9.** P2 = (1,910,000 − 60,301) ÷ 23,044 = 80.27 → 밴드 -2, "
            "P3 0, 소계 -2, P4 short_history 한 칸 → -3, 트랙 바닥 -3. 다른 13개사는 불변이다."),
        "why_not_p1": "순이익이 음수라 requires_positive 를 넘지 못한다 — 트랙 정의의 parameters_excluded_note 참조.",
        "review": f"{REVIEW_B} high",
    },
}
C25 = {
    "id": "C-25",
    "status": "pending",
    "blocking": False,
    "affects": ["F6"],
    "summary": "신규 상장 트랙의 바닥 -3 이 P2 를 계산하게 된 뒤에도 맞는지",
    "recommendation": (
        "이번 실행은 바닥을 건드리지 않는다. 바닥 -3 은 P3 하나(범위 -3~0)로만 점수를 내던 트랙의 값인데, "
        "C-24 로 P2(-2~0)가 더해져 소계 범위가 -5 까지 넓어졌다. spacex-xai 는 소계 -2 에 P4 한 칸이라 -3 이고 "
        "**바닥에 정확히 닿지만 절단되지는 않는다**(floor_applied 없음). 다음 라운드에서 정한다."),
    "choices": ["keep_minus_3", "widen_to_minus_5_like_listed_tracks", "recompute_from_parameter_ranges"],
    "implementation_status": {
        "verdict": "not_implemented",
        "checked_at": DATE,
        "checked_by": f"worker ({M})",
        "evidence": [
            "calc_f6_params.compute_listed 는 track['floor'] 를 그대로 읽는다 — 파라미터 구성에서 역산하지 않는다",
            "이번 실행에서 floor 로 절단된 회사는 없다(spacex-xai 는 보정 후 -3 으로 바닥과 같다)",
        ],
    },
    "pending_recheck": {
        "what": "listed_newly 바닥을 -3 으로 둘지, 파라미터 범위에 맞춰 넓힐지.",
        "why": f"{M} 지시 — 바닥 자체는 별도 사안이라 미결로 등재한다.",
        "trigger": "신규 상장 트랙에서 소계가 -3 아래로 내려가 실제로 절단이 발생할 때, 또는 다음 라운드",
        "when": "2026-11",
    },
}


def fix_rules(rules: dict) -> list[str]:
    out: list[str] = []
    f6 = rules["policies"]["f6"]

    p2 = f6["parameters"]["P2"]
    if p2.get("input_alternatives") != {"revenue_ttm": ["revenue_ttm_full"]}:
        p2["input_alternatives"] = {"revenue_ttm": ["revenue_ttm_full"]}
        out.append("P2: input_alternatives revenue_ttm → revenue_ttm_full")
    if p2.get("input_alternatives_note") != P2_ALT_NOTE:
        p2["input_alternatives_note"] = P2_ALT_NOTE
        out.append("P2: input_alternatives_note")

    newly = f6["tracks"]["listed_newly"]
    if newly["parameters"] != ["P2", "P3"]:
        newly["parameters"] = ["P2", "P3"]
        out.append("listed_newly: parameters [P3] → [P2, P3]")
    for key, value in (("optional_parameters", ["P2"]),
                       ("optional_parameters_note", NEWLY_OPTIONAL_NOTE),
                       ("parameters_excluded_note", NEWLY_EXCLUDED_NOTE),
                       ("select", NEWLY_SELECT)):
        if newly.get(key) != value:
            newly[key] = value
            out.append(f"listed_newly: {key}")

    decisions = rules["decisions"]
    for spec in (C24, C25):
        cur = [d for d in decisions if d["id"] == spec["id"]]
        if not cur:
            decisions.append(json.loads(json.dumps(spec)))
            out.append(f"+ decisions {spec['id']} ({spec['status']})")
        elif cur[0] != spec:
            decisions[decisions.index(cur[0])] = json.loads(json.dumps(spec))

    # --- S2 TEN-RB-Q10 에 amazon.F3 · palantir.F3
    ten = find(rules["open_tensions"], "id", "TEN-RB-Q10")
    for jid in ("amazon.F3", "palantir.F3"):
        if jid not in ten["judgment_ids"]:
            ten["judgment_ids"].append(jid)
            out.append(f"TEN-RB-Q10: judgment_ids += {jid}")
    affected = {a["judgment_id"] for a in ten["affected"]}
    new_affected = [
        {
            "company_id": "amazon",
            "judgment_id": "amazon.F3",
            "why": ("근거란의 가속도 줄이 `✅후발 가속도` 한 줄뿐이고 **수치가 없다.** 채점규칙 145행이 요구하는 것은 "
                    "실측 성장률의 변화인데 성장률 하나조차 적혀 있지 않아 가속도 pass 를 재현할 수 없다."),
            "source_lines": ["채점규칙 145행", "채점규칙 153행"],
        },
        {
            "company_id": "palantir",
            "judgment_id": "palantir.F3",
            "why": ("근거란 두 줄(`온톨로지는 모방 난이도 높음` · `AI가 데이터 이전을 자동화하면 전환비용 해자가 약화`)에 "
                    "**가속도를 말하는 줄이 아예 없다.** acceleration=pass 를 받치는 문장이 판단 기록에 없다."),
            "source_lines": ["채점규칙 145행", "채점규칙 153행"],
        },
    ]
    for a in new_affected:
        if a["judgment_id"] not in affected:
            ten["affected"].append(a)
            out.append(f"TEN-RB-Q10: affected += {a['judgment_id']}")
        else:
            cur = find(ten["affected"], "judgment_id", a["judgment_id"])
            if cur != a:
                ten["affected"][ten["affected"].index(cur)] = a
    mark = f"[{M}] {REVIEW_B} medium — amazon.F3·palantir.F3 을 같은 성질로 넣었다."
    if mark not in ten["note"]:
        ten["note"] = ten["note"] + " " + mark
        out.append("TEN-RB-Q10: note 에 이번 추가 사유")
    return out


# ------------------------------------------------------------------ 실행

RUN_C24 = {
    "id": "C-24",
    "choice": "compute_p2_when_inputs_exist",
    "rationale": ("신규 상장 트랙도 입력이 성립하면 P2 를 계산한다. 상장사 열두 곳에 같은 잣대를 대는 쪽이다. "
                  "spacex-xai 는 P2 80.27(밴드 -2)이 붙어 F6 -1 → -3, 총점 11 → 9 가 된다. 규칙 v1.7 decisions C-24 를 "
                  f"실행 단위로 옮긴다. {M}."),
    "decided_by": "사용자",
    "decided_at": DATE,
}
RUN_ASSUMPTION = (
    f"[{M}] spacex-xai 의 12개월 매출은 `spacex-xai.revenue_ttm_full.fix56` 23,044M 이다 "
    "(S-1/A FY2025 18,674 + 10-Q H1'26 12,508 − H1'25 8,138). 같은 회사의 `revenue_ttm` 은 **분기값**이며 P3 전용이다 — "
    "두 지표를 섞지 않는다."
)


def fix_run(run: dict) -> list[str]:
    out: list[str] = []
    if not any(d["id"] == "C-24" for d in run["decisions"]):
        run["decisions"].append(json.loads(json.dumps(RUN_C24)))
        out.append("+ decisions C-24 (사용자 결정 — 신규 상장 트랙 P2 산출)")
    if RUN_ASSUMPTION not in run["assumptions"]:
        run["assumptions"].append(RUN_ASSUMPTION)
        out.append("+ assumptions 12개월 매출 지표 분리")
    return out


def main() -> int:
    registry = {c["company_id"]: c for c in load_json_strict(ROOT / "scorecard" / "companies.json")["companies"]}

    rules = load(RULES)
    rc = fix_rules(rules)
    validate_rules(rules)
    dump(RULES, rules)

    doc = load(RUN / "observations.json")
    oc = fix_observations(doc)
    validate_observations(doc, registry, RUN_ID)
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
