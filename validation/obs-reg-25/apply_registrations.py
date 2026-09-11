# 새 실행에 OFFB 실측 관측 6건과 alibaba 연간 영업손익을 등록하고 coverage_comparable 판정을 기록한다
"""**승인된 실행은 건드리지 않는다.** 대상은 새 실행 `ai-scorecard-2026-09-obsreg` 뿐이다.

## 왜 이 형태인가

**하나. 기준일이 섞인 합계는 합계만 남기지 않는다.**
SPCX `offbalance_B` 는 2025-12-31 기준 미개시 리스와 2026-06-30 기준 구매약정의 합이다.
구성요소를 관측 둘로 쪼갤 수 없다 — `ObsLookup.number()` 는 기업·지표당 값을 **하나만** 돌려주므로
둘로 두면 한쪽이 조용히 버려진다. 그래서 합계 관측 하나에 `basis.components` 로 각 구성요소의
기준일·출처·금액을 남긴다. 합계를 읽는 쪽은 값을 얻고, 감사하는 쪽은 섞였다는 사실을 본다.

**둘. 통화는 사라지지 않게 한다.**
스키마는 `unit == METRICS[metric]["unit"]` 를 강제한다(`offbalance_B` 는 `USD`). RMB 를 그대로 넣을
자리가 없고, `unit: "RMB"` 는 검증에서 걸린다. 그래서 **20-F 가 스스로 선언한 환율**로 환산해
USD 로 넣고 원화폐·원금액·환율·환율 출처를 `basis` 에 남긴다. 외부 환율을 끌어오지 않는다 —
20-F 가 "RMB6.8980 to US$1.00, 2026-03-31, 연준 H.10" 이라고 문서 안에 적어 두었고, 같은 문서가
자본약정 RMB54,136M 을 US$7,848M 으로 환산해 두어 **환산을 문서 자체로 검산할 수 있다.**

**셋. `as_of` 는 기준일이 아니라 관측 시점이다.**
`ObsLookup.get()` 은 `(status 등급, as_of)` 로 정렬해 하나를 고른다 — `as_of` 는 **최신성 키**다.
여기에 공시 기준일(2026-06-30 등)을 넣었더니 승계 관측(2026-09-02)이 더 최신으로 뽑혀
`alibaba.contracted_revenue` 의 새 `missing_type` 이 엔진에 닿지 않았다(실제로 한 번 겪었다).
그래서 `as_of` 는 **원문을 연 날(2026-09-11)** 로 두고 공시 기준일은 `basis.measured_as_of` 에 적는다.
자료 자체는 전부 정보 컷오프(2026-09-02) 이전에 접수된 것이다(10-Q 2026-08-04 · 20-F 2026-05-20 · S-1/A 2026-06-03).

**넷. 기존 관측을 지우지 않는다.**
교체 대상(AMZN `offbalance_B` 106,000 · SPCX `contracted_revenue` 47,500)은 남겨 두고
`note` 에 대체 관계를 적는다. `ObsLookup` 이 `verified` 를 `legacy_unverified` 보다 우선하므로
계산에는 새 값이 쓰이고, 이력은 보존된다.

사용:
    python validation/obs-reg-25/apply_registrations.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
RUN_ID = "ai-scorecard-2026-09-obsreg"
RUN = ROOT / "scorecard" / "runs" / RUN_ID

FILED = "2026-09-11"          # 우리가 원문을 열어 확인한 날
CNY_PER_USD = 6.8980          # 20-F "Exchange Rate Information" 선언값(2026-03-31, 연준 H.10)

# ------------------------------------------------------------------ 출처
SOURCES = [
    {"source_id": "SRC-SEC-SPCX-10Q-2026Q2",
     "title": "SpaceX/xAI Form 10-Q (2026-06-30) — Note 3 Revenue · Note 16 Commitments",
     "publisher": "SEC EDGAR", "url": "https://www.sec.gov/Archives/edgar/data/1181412/000162828026052535/spcx-20260630.htm",
     "accessed_at": FILED, "sha256": "2b6762e149c2af81f1f840acb7541e0df8b420cb18e0058d59b451721418ff88",
     "conflict_of_interest": None,
     "note": "접수번호 0001628280-26-052535(2026-08-04). 원문 보존 C-13 3cf9799:validation/offb-24/_raw/spcx-20260630.htm"},
    {"source_id": "SRC-SEC-SPCX-S1A-2026",
     "title": "SpaceX/xAI Form S-1/A (2026-06-03) — Note 11 Leases (F-36)",
     "publisher": "SEC EDGAR", "url": "https://www.sec.gov/Archives/edgar/data/1181412/000162828026040364/",
     "accessed_at": FILED, "sha256": "fd8aea349e7f8550e4e3ccc4c72b06796ee27d2bfa2bff4891c6a21d11404a88",
     "conflict_of_interest": None,
     "note": "접수번호 0001628280-26-040364. 미개시 리스는 10-Q 가 아니라 이 문서에만 있다. url 은 접수 디렉터리 — 문서명은 보존 파일 spcx_s1a_20260603.htm"},
    {"source_id": "SRC-SEC-AMZN-10Q-2026Q2",
     "title": "Amazon Form 10-Q (2026-06-30) — Note 1 Accounting Policies · Commitments 표",
     "publisher": "SEC EDGAR", "url": "https://www.sec.gov/Archives/edgar/data/1018724/000101872426000026/amzn-20260630.htm",
     "accessed_at": FILED, "sha256": "d07b8a88fa442c2c55bd65b3f1d336ca16e7d1e9fda831e1063d24adea60e4eb",
     "conflict_of_interest": None,
     "note": "원문 보존 C-13 3cf9799:validation/offb-24/_raw/amzn-20260630.htm"},
    {"source_id": "SRC-SEC-BABA-20F-FY2026",
     "title": "Alibaba Form 20-F (FY2026, 2026-03-31) — Note 2(g) · Note 27 · Exchange Rate Information",
     "publisher": "SEC EDGAR", "url": "https://www.sec.gov/Archives/edgar/data/1577552/000119312526231755/baba-20260331.htm",
     "accessed_at": FILED, "sha256": "7be73cb49925934f89e0a9f4bb1f91c64474a2695c6f357735b39609401e02da",
     "conflict_of_interest": None,
     "note": "접수번호 0001193125-26-231755. 원문 보존 C-13 3cf9799:validation/offb-24/_raw/baba-20260331.htm"},
    {"source_id": "SRC-SEC-BABA-FACTS",
     "title": "SEC XBRL companyfacts CIK0001577552 (Alibaba) — us-gaap Revenues · OperatingIncomeLoss",
     "publisher": "SEC EDGAR", "url": "https://data.sec.gov/api/xbrl/companyfacts/CIK0001577552.json",
     "accessed_at": FILED, "sha256": "66f5eb1c036515728219ec6983e6d74be34201eb5abbeb4d5120b0aa5dd5ff9f",
     "conflict_of_interest": None,
     "note": "원문 보존 C-13 HANSOLJJ/C-13:validation/f6-avail-15b/_raw/CIK0001577552_BABA.json. 신규 네트워크 호출 없음"},
]

# ------------------------------------------------------------------ 관측
BABA_OFFB_CNY = 254_198_000_000
BABA_OFFB_USD = 36_851_000_000          # 254,198 / 6.8980 = 36,850.97 → 백만 USD 반올림(20-F 편의환산 표기와 동일)

NEW_OBS = [
    # ---------- SPCX
    {"observation_id": "spacex-xai.contracted_revenue.obsreg25", "company_id": "spacex-xai",
     "metric": "contracted_revenue", "value": 47_461_000_000.0, "unit": "USD", "as_of": FILED,
     "kind": "actual", "source_id": "SRC-SEC-SPCX-10Q-2026Q2", "status": "verified",
     "basis": {"measured_as_of": "2026-06-30",
               "statement": "Backlog totaled $ 47,461 million as of June 30, 2026",
               "location": "10-Q Note 3 - Revenue (p.13)",
               "xbrl_tag": "us-gaap:RevenueRemainingPerformanceObligation",
               "recognition_schedule": {"within_1y": 0.56, "1y_to_3y": 0.34, "thereafter": 0.10},
               "contains_deferred_revenue": 14_286_000_000,
               "caution": "백로그 안에 이연수익 14,286 이 포함돼 있다 — 이연수익과 더하면 중복이다"},
     "raw": "Backlog $47,461M (2026-06-30)",
     "note": "OBS-REG-25. 승계 관측 spacex-xai.contracted_revenue.v15($47.5B, legacy_unverified)를 대체한다 — 반올림값이 아니라 원문 수치다"},
    {"observation_id": "spacex-xai.offbalance_B.obsreg25", "company_id": "spacex-xai",
     "metric": "offbalance_B", "value": 29_582_000_000.0, "unit": "USD", "as_of": FILED,
     "kind": "derived", "source_id": "SRC-SEC-SPCX-10Q-2026Q2", "status": "verified",
     "basis": {"measured_as_of": "2026-06-30", "aggregation": "sum_of_components", "mixed_as_of": True,
               "components": [
                   {"label": "미개시 운용리스", "value": 1_627_000_000, "as_of": "2025-12-31",
                    "source_id": "SRC-SEC-SPCX-S1A-2026", "location": "S-1/A Note 11 Leases (F-36)",
                    "statement": "not yet commenced for the aggregate lease payments of $1,627 million and an average lease term of 7.2 years",
                    "note": "10-Q 에는 이 수치가 없다. 10-Q 는 리스 포트폴리오에 중요한 변동이 없다고만 적는다"},
                   {"label": "무조건적 비취소 구매약정", "value": 27_955_000_000, "as_of": "2026-06-30",
                    "source_id": "SRC-SEC-SPCX-10Q-2026Q2", "location": "10-Q Note 16 Commitments (p.27)",
                    "by_year": {"2026_remaining": 2_728, "2027": 22_244, "2028": 2_172, "2029": 809,
                                "2030": 2, "thereafter": 0, "unit": "USD million"},
                    "note": "Spectrum 거래분은 현금과 Class A 보통주 혼합 지급이고 분해가 미공시다"}],
               "as_of_span": {"earliest": "2025-12-31", "latest": "2026-06-30",
                              "stale_component_share": 0.055,
                              "note": "이른 기준일 구성요소는 합계의 5.5% 다"}},
     "raw": "미개시 리스 $1,627M(2025-12-31) + 무조건 구매약정 $27,955M(2026-06-30) = $29,582M",
     "note": "OBS-REG-25. **기준일이 섞인 합계다.** 구성요소별 기준일·출처를 basis.components 에 남겼다. "
             "관측을 둘로 쪼개지 않은 이유는 ObsLookup 이 지표당 값을 하나만 돌려줘 한쪽이 조용히 버려지기 때문이다"},
    # ---------- AMZN
    {"observation_id": "amazon.contracted_revenue.obsreg25", "company_id": "amazon",
     "metric": "contracted_revenue", "value": 496_000_000_000.0, "unit": "USD", "as_of": FILED,
     "kind": "actual", "source_id": "SRC-SEC-AMZN-10Q-2026Q2", "status": "verified",
     "basis": {"measured_as_of": "2026-06-30",
               "statement": "those commitments not yet recognized were approximately $ 496 billion as of June 30, 2026",
               "location": "10-Q Note 1 — ACCOUNTING POLICIES AND SUPPLEMENTAL DISCLOSURES",
               "approximate": True,
               "precision": "원문이 approximately 이고 십억 단위로만 적는다 — 유효숫자 3자리",
               "scope": "원계약 1년 초과 계약만(primarily AWS). 1년 이하 계약은 빠져 있어 과소계상 방향",
               "weighted_average_remaining_years": 6.4,
               "xbrl": "us-gaap:RevenueRemainingPerformanceObligation 태깅은 2020-06 에서 끊겼다 — 본문 서술로만 공시된다"},
     "raw": "RPO approximately $496 billion (2026-06-30)",
     "note": "OBS-REG-25. 승계 관측 amazon.contracted_revenue.v15(parse_failed)를 대체한다. "
             "**parse_failed 는 정직한 라벨이었다** — XBRL 전용 파서로는 구조적으로 못 읽는다"},
    {"observation_id": "amazon.offbalance_B.obsreg25", "company_id": "amazon",
     "metric": "offbalance_B", "value": 267_279_000_000.0, "unit": "USD", "as_of": FILED,
     "kind": "derived", "source_id": "SRC-SEC-AMZN-10Q-2026Q2", "status": "verified",
     "basis": {"measured_as_of": "2026-06-30", "aggregation": "sum_of_components", "mixed_as_of": False,
               "location": "10-Q Commitments 표 (2026-06-30)",
               "components": [
                   {"label": "Leases not yet commenced", "value": 137_214_000_000},
                   {"label": "Unconditional purchase obligations", "value": 130_065_000_000}],
               "excluded": [
                   {"label": "Other commitments", "value": 18_366_000_000,
                    "reason": "설계진행 지시로 제외. 지시 사유는 '각주 3 내용 미확인' 이었으나 "
                              "각주 3 본문은 원문에 있다 — REPORT.md 4.1 참조",
                    "footnote_3": "asset retirement obligations, rent and tenant improvements for build-to-suit "
                                  "lease arrangements under construction, digital media content agreements "
                                  "with initial terms greater than one year",
                    "if_included": 285_645_000_000}],
               "table_total": 650_034_000_000,
               "scope": "Thereafter 열까지 포함 — 분모가 과대계상 방향",
               "alternative_denominator": {"label": "미개시 리스만", "value": 137_214_000_000,
                                           "note": "C-13 이 병기한 값. G4 가 묻는 것이 미래 지출 전체라 채택하지 않았다"}},
     "raw": "미개시 리스 $137,214M + 무조건 구매약정 $130,065M = $267,279M (2026-06-30)",
     "note": "OBS-REG-25. 승계 관측 amazon.offbalance_B.v15($106B, 출처 불명)를 대체한다. "
             "**106,000 은 2026Q2 약정표의 어느 행과도 일치하지 않는다** — 역산해 맞추지 않고 실측값으로 교체했다"},
    # ---------- BABA
    {"observation_id": "alibaba.offbalance_B.obsreg25", "company_id": "alibaba",
     "metric": "offbalance_B", "value": float(BABA_OFFB_USD), "unit": "USD", "as_of": FILED,
     "kind": "derived", "source_id": "SRC-SEC-BABA-20F-FY2026", "status": "verified",
     "basis": {"measured_as_of": "2026-03-31", "aggregation": "sum_of_components", "mixed_as_of": False,
               "original_currency": "CNY", "original_value": BABA_OFFB_CNY,
               "fx_rate": CNY_PER_USD, "fx_quote": "CNY per USD", "fx_rate_as_of": "2026-03-31",
               "fx_rate_source": "20-F 'Exchange Rate Information' 자체 선언 — RMB6.8980 to US$1.00, "
                                 "the exchange rate on March 31, 2026 set forth in the H.10 statistical "
                                 "release of the Federal Reserve Board",
               "fx_verification": [
                   {"check": "20-F 가 자본약정 RMB54,136M 을 US$7,848M 으로 스스로 환산한다",
                    "recomputed_usd_million": round(54_136 / CNY_PER_USD, 2), "agrees": True},
                   {"check": "companyfacts FY2026 Revenues CNY 1,023,670M / USD 148,401M 역산",
                    "implied_rate": round(1_023_670 / 148_401, 4), "agrees": True}],
               "components": [
                   {"label": "자본약정 (capital commitments)", "value_cny": 54_136_000_000,
                    "location": "20-F Note 27(a)",
                    "by_term": {"no_later_than_1y": 53_484, "1y_to_5y": 652, "unit": "CNY million"}},
                   {"label": "기타약정 (other commitments)", "value_cny": 200_062_000_000,
                    "location": "20-F Note 27(c)",
                    "scope": "코로케이션·대역폭·저작권·마케팅",
                    "by_term": {"no_later_than_1y": 57_441, "1y_to_5y": 133_598, "over_5y": 9_023,
                                "unit": "CNY million"}}],
               "excluded": [
                   {"label": "투자약정 (investment commitments)", "value_cny": 14_501_000_000,
                    "location": "20-F Note 27(b)",
                    "reason": "지분투자·M&A 대금은 영업 지출이 아니라 투자 지출이다. "
                              "G4 가 묻는 것은 미래 지출이 대응 수입으로 덮이는가이고 지분 취득은 계약 수입을 낳지 않는다"}],
               "not_disclosed": {"label": "미개시 리스",
                                 "note": "20-F 전문에 'not yet commenced' 0건. 다만 미공시인지 중요성 미달인지 "
                                         "갈리지 않아 없는 것으로 단정하지 않는다(C-13 검토 반영)"},
               "rounding": "백만 USD 단위 반올림 — 20-F 자체 편의환산 표기와 같은 자리"},
     "raw": "자본약정 RMB54,136M + 기타약정 RMB200,062M = RMB254,198M (2026-03-31) → US$36,851M @6.8980",
     "note": "OBS-REG-25. **원 통화는 RMB 다.** 스키마가 unit 을 지표 단위(USD)로 강제해 RMB 를 그대로 둘 자리가 없어 "
             "20-F 가 스스로 선언한 환율로 환산하고 원화폐·원금액·환율·환율 출처를 basis 에 남겼다. "
             "외부 환율 출처를 쓰지 않았다 — 환산 근거가 문서 안에 있고 문서 자체로 검산된다"},
    {"observation_id": "alibaba.contracted_revenue.obsreg25", "company_id": "alibaba",
     "metric": "contracted_revenue", "value": None, "unit": "USD", "as_of": FILED,
     "kind": "actual", "source_id": "SRC-SEC-BABA-20F-FY2026", "status": "not_disclosed",
     "missing_type": "not_disclosed_confirmed",
     "basis": {"measured_as_of": "2026-03-31",
               "statement": "The Company applies the practical expedient to not disclose the value of "
                            "unsatisfied performance obligations for contracts with an original expected "
                            "duration of one year or less and contracts for which revenue is recognized at "
                            "the amount to which the Company has the right to invoice for services performed",
               "location": "20-F Note 2(g) Revenue recognition, 'Practical expedients and exemptions' (F-21)",
               "note_on_location": "설계진행 지시서는 Note 2(t) 라고 적었으나 소항목은 (g) 다. 쪽수(F-21)와 문면은 같다",
               "absence_check": {"remaining performance obligation": 0, "backlog": 0, "not yet commenced": 0,
                                 "scope": "20-F 전문"},
               "limit": "선언된 면제는 1년 이하 계약과 청구권 기준 계약만 덮는다. "
                        "1년 초과 계약분은 면제로 설명되지 않으며 Note 5 의 '중요하지 않다' 서술이 그 자리를 메운다",
               "unchecked": "6-K 361건은 확인하지 않았다. RPO 는 연차 주석 항목이고 면제가 선언돼 있어 개연성이 낮다"},
     "raw": "미공시 — ASC 606 실무적 간편법 선언",
     "note": "OBS-REG-25. **회사가 공시하지 않겠다고 선언한 회계정책이다.** "
             "'이 문서에 없다' 와 다르다 — 찾아도 없을 것이 선언돼 있다. C-16 의 유일한 대상이다"},
    # ---------- alibaba FY2026 연간 영업손익 (G1-TTM-26)
    {"observation_id": "alibaba.revenue_ttm.obsreg25", "company_id": "alibaba",
     "metric": "revenue_ttm", "value": 148_401_000_000.0, "unit": "USD", "as_of": FILED,
     "kind": "actual", "source_id": "SRC-SEC-BABA-FACTS", "status": "verified",
     "period": {"start": "2025-04-01", "end": "2026-03-31"},
     "basis": {"measured_as_of": "2026-03-31", "period_basis": "annual",
               "why_not_ttm": "FY2026 회계연도 전체다. TTM 이 아니다 — metric 이름이 _ttm 인 것은 "
                              "기존 12개사 관측·F9 코드·스키마가 얽혀 이름을 바꾸지 않기로 한 결과이고, "
                              "기간은 period 와 이 필드로 선언한다",
               "original_currency": "CNY", "original_value": 1_023_670_000_000,
               "usd_basis": "20-F 자체 편의환산(us-gaap Revenues 의 USD 단위 값)이지 우리가 환산한 값이 아니다",
               "implied_rate": round(1_023_670 / 148_401, 4),
               "xbrl_tag": "us-gaap:Revenues", "accession": "0001193125-26-231755", "form": "20-F"},
     "raw": "FY2026 매출 RMB1,023,670M (US$148,401M)",
     "note": "OBS-REG-25 / G1-TTM-26. **연간 기준이다.** F6 P4 가 기간 단위 TTM 아님으로 한 칸 내린다. "
             "같은 한계를 F9 에서 또 세지 않는다"},
    {"observation_id": "alibaba.operating_income_ttm.obsreg25", "company_id": "alibaba",
     "metric": "operating_income_ttm", "value": 7_270_000_000.0, "unit": "USD", "as_of": FILED,
     "kind": "actual", "source_id": "SRC-SEC-BABA-FACTS", "status": "verified",
     "period": {"start": "2025-04-01", "end": "2026-03-31"},
     "basis": {"measured_as_of": "2026-03-31", "period_basis": "annual",
               "original_currency": "CNY", "original_value": 50_150_000_000,
               "usd_basis": "20-F 자체 편의환산(us-gaap OperatingIncomeLoss 의 USD 단위 값)",
               "implied_rate": round(50_150 / 7_270, 4),
               "xbrl_tag": "us-gaap:OperatingIncomeLoss", "accession": "0001193125-26-231755", "form": "20-F"},
     "raw": "FY2026 영업이익 RMB50,150M (US$7,270M)",
     "note": "OBS-REG-25 / G1-TTM-26. 연간 기준."},
    {"observation_id": "alibaba.operating_margin_ttm.obsreg25", "company_id": "alibaba",
     "metric": "operating_margin_ttm", "value": round(50_150 / 1_023_670, 6), "unit": "ratio",
     "as_of": FILED, "kind": "derived", "source_id": "SRC-SEC-BABA-FACTS", "status": "verified",
     "period": {"start": "2025-04-01", "end": "2026-03-31"},
     "basis": {"measured_as_of": "2026-03-31", "period_basis": "annual",
               "formula": "OperatingIncomeLoss / Revenues (같은 기간·같은 통화)",
               "numerator_cny": 50_150_000_000, "denominator_cny": 1_023_670_000_000,
               "currency_note": "비율이라 통화가 상쇄된다. CNY 원값으로 계산했고 USD 편의환산으로 계산해도 같다",
               "cross_check_usd": round(7_270 / 148_401, 6),
               "xbrl_tags": ["us-gaap:OperatingIncomeLoss", "us-gaap:Revenues"],
               "accession": "0001193125-26-231755", "form": "20-F"},
     "raw": "FY2026 영업이익률 +4.899%",
     "note": "OBS-REG-25 / G1-TTM-26. **양수다** — G1 을 통과한다. "
             "**연간 기준이라는 한계는 F6 P4 가 이미 한 칸 내린다. F9 에서 또 깎지 않는다.**"},
]

# 승계 관측 중 대체 대상. 지우지 않고 대체 관계만 note 에 남긴다.
SUPERSEDED = {
    "spacex-xai.contracted_revenue.v15": "spacex-xai.contracted_revenue.obsreg25",
    "spacex-xai.offbalance_B.v15": "spacex-xai.offbalance_B.obsreg25",
    "amazon.contracted_revenue.v15": "amazon.contracted_revenue.obsreg25",
    "amazon.offbalance_B.v15": "amazon.offbalance_B.obsreg25",
    "alibaba.offbalance_B.v15": "alibaba.offbalance_B.obsreg25",
    "alibaba.contracted_revenue.v15": "alibaba.contracted_revenue.obsreg25",
}

# ------------------------------------------------------------------ 판단 (coverage_comparable)
COVERAGE = {
    "spacex-xai": {
        "coverage_comparable": "yes",
        "evidence": [
            "G4 커버리지 1.604 = 백로그 47,461 / B종 29,582 (2026-06-30 기준 관측)",
            "판정 근거 1 — 미개시 리스 1,627 은 2025-12-31 기준(S-1/A)이라 분모의 5.5% 가 6개월 이른 시점이다",
            "판정 근거 2 — 무조건 약정 중 Spectrum 분은 현금과 Class A 보통주 혼합 지급이고 분해가 미공시다",
            "판정 근거 3 — 2027년 지출 22,244 가 전체 약정의 80% 로 편중돼 있다. 총액만 보면 이 편중이 사라진다",
            "판정 근거 4 — 백로그 안에 이연수익 14,286 이 포함돼 있다. 이연수익과 더하면 중복이다",
            "그럼에도 yes 인 이유 — 주식 지급분이 섞여 있으면 현금 의무를 과대계상하므로 분모가 크게 잡히고 "
            "커버리지가 보수적으로 나온다. 우리에게 불리한 방향이라 안전하다. 기준일 차가 걸린 1,627 은 분모의 5.5% 로 작다",
            "판정 주체 설계진행(2026-09-11, OBS-REG-25 지시서)",
        ],
    },
    "amazon": {
        "coverage_comparable": "yes",
        "evidence": [
            "G4 커버리지 1.856 = RPO 496,000 / B종 267,279 (2026-06-30 기준 관측)",
            "판정 근거 1 — 분자는 원계약 1년 초과 계약만 담아 과소계상된다",
            "판정 근거 2 — 분모는 Thereafter 열까지 담아 과대계상된다",
            "즉 양쪽 편의가 다 보수적이라 커버리지가 낮게 나온다. 우리에게 불리한 방향이라 안전하다",
            "분모 선택 — 미개시 리스만 쓰면 3.615 가 되지만 G4 가 묻는 것은 미래 지출 전체이므로 "
            "구매약정을 합한 267,279 를 분모로 쓴다. C-13 이 두 값을 병기해 뒀다",
            "판정 주체 설계진행(2026-09-11, OBS-REG-25 지시서)",
        ],
    },
    "alibaba": {
        "coverage_comparable": "yes",
        "operating_result_reviewed": "profit",
        "evidence": [
            "**분모만 있고 분자가 없다.** B종 약정 US$36,851M(RMB254,198M, 2026-03-31)은 있으나 계약 수입은 미공시다",
            "판정의 뜻 — 두 수치가 확보됐다면 같은 범위와 기간으로 비교 가능하다는 것이고, 분자 부재는 별개 사실이다",
            "yes 로 두어야 엔진이 결측 유형 분기로 내려가 C-16 이 alibaba 계약수입의 not_disclosed_confirmed 를 본다. "
            "no 나 unknown 이면 그 앞에서 멈춰 '회사가 안 낸 것' 과 '우리가 안 찾은 것' 이 같은 자리에 묻힌다",
            "G1 — FY2026 연간 영업이익률 +4.899%(영업이익 RMB50,150M / 매출 RMB1,023,670M, 20-F 0001193125-26-231755)라 "
            "operating_result_reviewed=profit. 연간 기준이라는 한계는 F6 P4 가 이미 한 칸 내리므로 F9 에서 또 세지 않는다",
            "판정 주체 설계진행(2026-09-11, OBS-REG-25 지시서 · G1-TTM-26)",
        ],
    },
}


def main() -> int:
    sys.path.insert(0, str(ROOT / "scripts"))
    from scorecard.rules import load_rules
    from scorecard.schema import load_json_strict, validate_judgments, validate_observations

    registry = {c["company_id"]: c for c in load_json_strict(ROOT / "scorecard" / "companies.json")["companies"]}

    bar = "=" * 104
    print(bar)
    print(f"OBS-REG-25 — 새 실행 {RUN_ID} 에 관측·판단 반영 (승인 실행 미변경)")
    print(bar)

    # ---------------- sources
    sources = load_json_strict(RUN / "sources.json")
    have = {s["source_id"] for s in sources["items"]}
    added = [s for s in SOURCES if s["source_id"] not in have]
    sources["items"].extend(added)
    print(f"\n[1] 출처 {len(added)}건 추가")
    for s in added:
        print(f"  {s['source_id']:26} {s['title'][:66]}")

    # ---------------- observations
    obs = load_json_strict(RUN / "observations.json")
    by_id = {o["observation_id"]: o for o in obs["items"]}
    print(f"\n[2] 관측 — 신규 {len(NEW_OBS)}건 · 대체 표시 {len(SUPERSEDED)}건 (기존 {len(obs['items'])}건)")
    for old_id, new_id in SUPERSEDED.items():
        old = by_id.get(old_id)
        if old is None:
            print(f"  ! 대체 대상 없음 {old_id}")
            continue
        mark = f"[OBS-REG-25 대체됨 → {new_id}] "
        if not str(old.get("note") or "").startswith("[OBS-REG-25"):
            old["note"] = mark + (old.get("note") or "")
        print(f"  대체  {old_id:42} value={old['value']!s:>16} status={old['status']}")
    for item in NEW_OBS:
        obs["items"].append(item)
        v = "null" if item["value"] is None else f"{item['value']:,.6g}"
        print(f"  신규  {item['observation_id']:42} value={v:>16} status={item['status']}"
              + (f" missing_type={item['missing_type']}" if "missing_type" in item else ""))
    validate_observations(obs, registry, RUN_ID)

    # ---------------- judgments
    jud = load_json_strict(RUN / "judgments.json")
    rules = load_rules(load_json_strict(RUN / "run.json")["rule_version"])
    print(f"\n[3] 판단 — coverage_comparable 기록 {len(COVERAGE)}건")
    for j in jud["items"]:
        upd = COVERAGE.get(j["company_id"]) if j["factor"] == "F9" else None
        if not upd:
            continue
        before = {k: j["inputs"].get(k) for k in ("coverage_comparable", "operating_result_reviewed")}
        for key, value in upd.items():
            if key == "evidence":
                continue
            j["inputs"][key] = value
        j["evidence"] = list(j["evidence"]) + upd["evidence"]
        j["previous_judgment_id"] = j["judgment_id"]
        j["judgment_id"] = f"{j['company_id']}.F9.obsreg25"
        j["status"] = "new"
        j["reviewer"] = "설계진행"
        j["reviewed_at"] = FILED
        j.pop("carried_from", None)
        after = {k: j["inputs"].get(k) for k in ("coverage_comparable", "operating_result_reviewed")}
        print(f"  {j['company_id']:12} {before} -> {after}")
    validate_judgments(jud, registry, rules.payload, RUN_ID)

    # ---------------- run.decisions 사유 정밀화
    run = load_json_strict(RUN / "run.json")
    detail = {
        "C-05": "G1 실패 뒤 G3·G4 를 실제로 적용한다. 설계진행 2026-09-11 확정.",
        "C-06": "G1 밴드를 -2/-3/-4 로 재척도하고 floor -4, bep_retreat -4, buffer_erosion_min -3, "
                "relief_cap -2 로 둔다. 함정 재배분 -18 보존. 스텝 값은 그대로. 설계진행 2026-09-11 확정.",
    }
    for d in run["decisions"]:
        if d["id"] in detail:
            d["rationale"] = detail[d["id"]]
    run["assumptions"] = list(run["assumptions"]) + [
        "OFFB-24/24B 실측 관측 6건은 보존된 SEC 원문에서 직접 재확인했다(validation/obs-reg-25/verify_values.py, 대조 34건 불일치 0건)",
        "alibaba 의 B종 약정과 연간 영업손익은 원 통화가 CNY 이고 20-F 가 스스로 선언한 환율(RMB6.8980/US$1.00, 2026-03-31, 연준 H.10)로 환산했다. 원화폐·원금액·환율은 관측 basis 에 남겼다",
        "alibaba 영업손익은 FY2026 연간이며 TTM 이 아니다. 기간 단위 한계는 F6 P4 가 한 칸 내리고 F9 에서는 다시 세지 않는다",
        "alibaba 의 fcf_ttm·cash 는 여전히 legacy_unverified 이고 기간 정의가 없다. 영업손익을 연간으로 선언한 이상 이 둘도 같은 연간 기준으로 다시 뽑아야 한다(후속)",
    ]

    # ---------------- 저장
    from scorecard.schema import write_json
    write_json(RUN / "sources.json", sources)
    write_json(RUN / "observations.json", obs)
    write_json(RUN / "judgments.json", jud)
    write_json(RUN / "run.json", run)
    print(f"\n[4] 저장 — 관측 {len(obs['items'])}건 · 판단 {len(jud['items'])}건 · 출처 {len(sources['items'])}건")
    print(f"    다음: python scripts/scorecard_cli.py calculate {RUN_ID}")
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    sys.exit(main())
