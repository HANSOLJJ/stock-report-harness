# FIX-54 1단계 S1·S2: 확정 미인출 여신을 14개사 전수로 등록한다 — spacex-xai F9 -4→-3 (설계 지침 6.4, alibaba 와 같은 기준)
"""보존 원문(3cf9799 offb-24 · f14a235 tsm-edgar-29 · validation/f6-avail-15 companyfacts)만 읽는다. 신규 조회 없음.

- 원문에 조건(한도·미인출·만기·약정 준수)이 확인된 시설: verified 로 등록한다.
- 원문이 보존돼 있지 않거나 검색되지 않는 회사: 값 없이 not_disclosed · missing_type=unverified 로 **왜 없는지**를 남긴다.
  engine 의 obs.number 는 이 관측을 숫자로 쓰지 않으므로 G3 계산은 이전과 같다(0 대입이 아니라 '확인 안 함' 표시).

재실행해도 같은 결과가 나온다. 파일은 LF 로 쓴다.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard.schema import load_json_strict, validate_observations  # noqa: E402

RUN_ID = "ai-scorecard-2026-09-obsreg"
RUN = ROOT / "scorecard" / "runs" / RUN_ID
DATE = "2026-09-15"
SUFFIX = "fix54"
SPCX_RAW = "3cf9799:validation/offb-24/_raw/spcx-20260630.htm"
AMZN_RAW = "3cf9799:validation/offb-24/_raw/amzn-20260630.htm"


def load(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def dump(p: Path, d: dict) -> None:
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def verified(cid: str, value: float, as_of: str, source_id: str, basis: dict, raw: str, note: str) -> dict:
    return {"observation_id": f"{cid}.undrawn_credit.{SUFFIX}", "company_id": cid, "metric": "undrawn_credit",
            "value": value, "unit": "USD", "as_of": as_of, "observed_at": DATE, "kind": "actual",
            "source_id": source_id, "status": "verified", "basis": basis, "raw": raw, "note": note}


SPACEX = verified(
    "spacex-xai", 4355000000.0, "2026-06-30", "SRC-SEC-SPCX-10Q-2026Q2",
    {
        "form": "10-Q", "accession": "0001628280-26-052535", "measured_as_of": "2026-06-30",
        "definition": "설계 지침 6.4 런웨이 분자의 `조건이 확인된 확정 미인출 여신`",
        "facility": "Amended SpaceX Credit Facility (senior unsecured revolving)",
        "quotes": {
            "capacity": "In May 2026, SpaceX amended the SpaceX Credit Facility to increase the borrowing capacity up to $ 5,000 million (“Amended SpaceX Credit Facility”). As part of the Amended SpaceX Credit Facility, the sublimit for performance letters of credit was increased to $ 2,000 million.",
            "maturity": "terminates, and all outstanding loans become due and payable, on May 19, 2031",
            "undrawn": "As of June 30, 2026, no amounts were outstanding under the SpaceX Credit Facility.",
            "covenants": "As of June 30, 2026, the Company was in compliance with all covenants under the SpaceX Credit Facility.",
            "letters_of_credit": "The Company had outstanding letters of credit of $ 645 million at June 30, 2026 related to various customer contracts, insurance agreements, and facility lease agreements. All of the outstanding letters of credit were collateralized by restricted cash.",
        },
        "locations": "Note 12 Debt(p.18) · Note 16 Commitments — Letters of Credit and Surety Bonds(p.27) · MD&A(p.48). 보존 htm 은 9줄이라 행 번호 대신 절 이름으로 적는다 — " + SPCX_RAW,
        "narrowing": ("**확인된 하한으로 좁혔다.** 한도 5,000M 에서 신용장 645M 전액을 뺀 4,355M. 신용장이 이 시설의 performance LC "
                      "sublimit(2,000M) 안에서 발행됐는지 문면이 정하지 않는다 — 발행 위치가 미확정이라 보수적으로 전액 차감했다."),
        "sensitivity": {
            "lower_bound_4355": {"undrawn": 4355000000, "runway_years": round((93522 + 4355) / 32348, 6), "g3_step": 0, "boundary_flag": True},
            "if_lc_outside_5000": {"undrawn": 5000000000, "runway_years": round((93522 + 5000) / 32348, 6), "g3_step": 0, "boundary_flag": True},
            "conclusion": "두 경우 모두 런웨이 3년 이상이라 G3 step 0 · 경계 표시 true 로 결론이 같다.",
        },
        "excluded": [
            {"what": "X Corp. Secured First Lien Revolving Credit Facility $500M",
             "why": "`In February 2025, X Corp. … amended … and reduced the Secured First Lien Revolving Credit Facility commitment to $ 0` — 약정 한도가 0 이다. 합산하지 않는다."},
        ],
        "why_now": "3차 리뷰 B FC-01. alibaba(FIX-53 2단계)와 같은 기준의 누락이었다.",
    },
    "미인출 회전여신 확인 하한 US$4,355M (한도 5,000 − 신용장 645, 2026-06-30)",
    "FIX-54 1단계 S1. 보수적 하한. 신용장이 시설 밖이면 5,000M — 결론 같음(basis.sensitivity).",
)

AMAZON = verified(
    "amazon", 37500000000.0, "2026-06-30", "SRC-SEC-AMZN-10Q-2026Q2",
    {
        "form": "10-Q", "accession": "0001018724-26-000026", "measured_as_of": "2026-06-30",
        "definition": "설계 지침 6.4 런웨이 분자의 `조건이 확인된 확정 미인출 여신`",
        "components": [
            {"facility": "Credit Agreement (unsecured revolving)", "capacity": 15000000000, "outstanding": 0, "maturity": "2028-11"},
            {"facility": "Short-Term Credit Agreement (364-day revolving)", "capacity": 5000000000, "outstanding": 0,
             "maturity": "2026-10", "condition": "may be extended for one additional period of 364 days subject to approval by the lenders"},
            {"facility": "Term Loan (unsecured delayed draw)", "capacity": 17500000000, "outstanding": 0,
             "maturity": "인출일부터 3년", "condition": "single draw on any business day on or prior to September 30, 2026, after which any undrawn commitments will automatically terminate"},
        ],
        "quotes": {
            "revolvers": "We have an aggregate $ 20.0 billion in unsecured revolving credit facilities … There were no borrowings outstanding under the Credit Agreement and the Short-Term Credit Agreement as of December 31, 2025 and June 30, 2026.",
            "term_loan": "In June 2026, we entered into a $ 17.5 billion unsecured delayed draw term loan … There were no borrowings outstanding under the Term Loan as of June 30, 2026.",
            "letters_of_credit": "Standby letters of credit … do not reduce the amount of borrowings available under our credit facilities.",
        },
        "locations": "Note 5 Debt · MD&A 유동성. 보존 htm 은 9줄이라 절 이름으로 적는다 — " + AMZN_RAW,
        "conditions_note": ("세 시설 모두 기준일 미인출이다. 364일 여신(2026-10 만기)과 지연인출 약정(2026-09-30 까지 단일 인출)은 "
                            "기준일·정보 컷오프(2026-09-02) 현재 유효한 약정이지만 만기가 가깝다. 재무 약정(covenant) 문장은 원문에 없다."),
        "sensitivity": {
            "all_37_5": {"runway_years": round((78213 + 37500) / 11625, 6), "g3_step": 0},
            "long_term_only_15": {"runway_years": round((78213 + 15000) / 11625, 6), "g3_step": 0},
            "none": {"runway_years": round(78213 / 11625, 6), "g3_step": 0},
            "conclusion": "어느 경우든 3년 이상이라 F9 -2 는 같다.",
        },
        "excluded": [
            {"what": "Commercial Paper Programs up to $30.0B", "why": "발행 한도 프로그램이지 약정 여신이 아니다(인수 약정 없음)."},
            {"what": "other short-term credit facilities (working capital)", "why": "한도 금액이 원문에 없다. 인출액 325M 만 있다."},
        ],
        "why_now": "3차 리뷰 B FC-02. alibaba·spacex-xai 와 같은 기준으로 원문에 있는 시설을 등록한다.",
    },
    "미인출 약정 US$37.5B (회전 15.0 + 364일 5.0 + 지연인출 17.5, 2026-06-30)",
    "FIX-54 1단계 S2. 점수 불변(런웨이 3년 이상 구간).",
)

NO_TEXT = {
    "apple": "보존된 10-Q/10-K 본문이 없다. companyfacts 에 최근 기준일의 여신 한도 태그가 없다(CommercialPaper 1,997M 만).",
    "microsoft": "보존된 10-K 본문이 없다. companyfacts 의 LineOfCreditFacilityMaximumBorrowingCapacity 최신값이 2014-09-30 이다.",
    "nvidia": "보존된 10-Q 본문이 없다. companyfacts 의 여신 태그 최신값이 2017-01-29 이다.",
    "alphabet": "보존된 10-Q 본문이 없다. companyfacts 의 여신 한도 태그 최신값이 2015-09-30 이다.",
    "meta": "보존된 10-Q 본문이 없다. companyfacts 의 여신 태그 최신값이 2013-09-30 이다.",
    "oracle": ("보존된 10-K 본문이 없다. companyfacts 에 최근 기준일의 여신 태그가 없다. **oracle 은 FCF 음수라 G3 가 점수에 닿는다** — "
               "런웨이 3년(step 0)에 닿으려면 현금 31,289M 에 약 39,770M 이상의 확정 미인출 여신이 더해져야 한다. 확인하지 못했다."),
    "palantir": "보존된 10-Q 본문이 없다. companyfacts 의 여신 한도 태그 최신값이 2021-12-31 이다.",
    "tesla": "보존된 10-Q 본문이 없다. companyfacts 의 여신 한도 태그 최신값이 2016-12-31 이다.",
    "tsmc": "보존 20-F(f14a235)는 있으나 `credit facilit`·`unused credit`·`lines of credit`·`unutilized` 전문 검색 0건이다. FCF 양수라 G3 에 닿지 않는다.",
}
# 비상장 둘은 관측으로 등록하지 않는다 — 인용할 원천(source_id)이 없고, v1.5 이관 원천(SRC-v15-*)을 달면 출처를 지어내게 된다.
# 부재 사유는 validation/fix-54/undrawn-credit-census.md 표에 적는다(G3 는 FCF 미공시로 건너뛴다).
PRIVATE_ABSENT = {"anthropic": "비상장이고 차입 약정 원문이 없다", "openai": "비상장이고 차입 약정 원문이 없다"}


def unverified(cid: str, why: str) -> dict:
    return {"observation_id": f"{cid}.undrawn_credit.{SUFFIX}", "company_id": cid, "metric": "undrawn_credit",
            "value": None, "unit": "USD", "as_of": "2026-06-30", "observed_at": DATE, "kind": "actual",
            "source_id": "SRC-SEC-FACTS-F6",
            "status": "not_disclosed", "missing_type": "unverified",
            "basis": {"why": why, "not_fetched": "외부 조회 규칙상 새로 받지 않았다. 원문이 보존되면 다시 본다.",
                      "engine_effect": "숫자가 아니라 G3 분자에 들어가지 않는다(이전과 같음)."},
            "raw": None, "note": "FIX-54 1단계 S2 전수 — 확정 미인출 여신 미확인(우리가 확인하지 않았다)."}


def main() -> int:
    registry = {c["company_id"]: c for c in load_json_strict(ROOT / "scorecard" / "companies.json")["companies"]}
    path = RUN / "observations.json"
    obs = load(path)
    new = [SPACEX, AMAZON] + [unverified(cid, why) for cid, why in NO_TEXT.items()]
    ids = {o["observation_id"] for o in new} | {f"{cid}.undrawn_credit.{SUFFIX}" for cid in PRIVATE_ABSENT}
    obs["items"] = [o for o in obs["items"] if o["observation_id"] not in ids] + new
    validate_observations(obs, registry, RUN_ID)
    dump(path, obs)
    print(f"등록 verified 2건(spacex-xai 4,355M · amazon 37,500M) · 미확인 표시 {len(NO_TEXT)}건 · alibaba 는 FIX-53 등록분 유지")
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    sys.exit(main())
