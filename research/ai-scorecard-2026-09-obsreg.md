---
slug: ai-scorecard-2026-09-obsreg
report_type: ai_scorecard
plan_source: plan/ai-scorecard-2026-09-obsreg.md
run_id: ai-scorecard-2026-09-obsreg
as_of: 2026-09-02
rule_version: v1.7
observations_hash: d696e0c1a0b17933c37d26db25ddfd9a8252118807242defd908ba9c085770aa
judgments_hash: 5a28676508f6a6877dc046137c074f0b2a4a4c41d75dece6d9fce8727c2105ec
created_at: 2026-09-11
---
# 리서치 — AI 기업 9-factor 채점표 — SEC 실측 관측 반영(v1.7)

실행 `ai-scorecard-2026-09-obsreg` 의 원자료·판단 입력·출처를 정리한다. 관측 332건, 판단 114건.

## 원자료

### Alphabet / Google

| 지표 | 값 | 상태 | 종류 | 출처 | 원문 | 비고 |
| --- | --- | --- | --- | --- | --- | --- |
| capex_ttm | $132.4B | legacy_unverified | actual | SRC-v15-html | $132.4B |  |
| cash | $55.9B | verified | actual | SRC-SEC-FACTS-F6 | 현금및현금성자산 55.9B (버퍼 242.5B 는 basis 에 보존) | CASH-FCF-35. **순수 현금으로 등록한다** — 설계 지침 6.4. 유동성 버퍼와 총계는 basis.preserved_wider_def |
| cash | $242.5B | legacy_unverified | actual | SRC-v15-html | $242.5B | [CASH-FCF-35 대체됨 → alphabet.cash.cashfcf35]  |
| credit_rating | AA급 | legacy_unverified | text | SRC-v15-html | AA급 | 별표 J 교차검증 전용 — 점수 입력 아님 |
| debt_ebitda | 0.7 | legacy_unverified | actual | SRC-v15-html | 0.68 |  |
| fcf_ttm | $53.3B | verified | derived | SRC-SEC-FACTS-F6 | TTM FCF 53.3B = OCF 185.7B - CapEx 132.4B | CASH-FCF-35. SEC 실측. OCF·CapEx 구성요소를 basis 에 남겼다 |
| fcf_ttm | $53.3B | legacy_unverified | actual | SRC-v15-html | +$53.3B | [CASH-FCF-35 대체됨 → alphabet.fcf_ttm.cashfcf35]  |
| market_cap | $4.12T | legacy_unverified | actual | SRC-v15-html | $4.12T |  |
| net_borrowing_ttm | $70.1B | legacy_unverified | actual | SRC-v15-html | +$70.1B | 차환 제외 순증 |
| net_cash | $121.7B | verified | derived | SRC-SEC-FACTS-F6 | 현금+증권 242.5B − 차입 100.2B − 리스 20.6B = 121.7B | NETCASH-37. SEC 보존 원자료 실측. **정의는 legacy 역산 작업 정의다** |
| net_cash | $121.7B | legacy_unverified | actual | SRC-v15-html | +$121.7B | [NETCASH-37 대체됨 → alphabet.net_cash.nc37]  |
| net_income_ttm | $244.2B | verified | derived | SRC-SEC-FACTS-F6 | 2025-07-01~2026-06-30 244,205,000,000 | F6-REG-28. F6-SPEC-18 수집기 |
| nonop_share | 51% | legacy_unverified | actual | SRC-v15-html | 51% ⚠️ |  |
| ntm_per | 25.3 | legacy_unverified | estimate | SRC-v15-html | 25.3 |  |
| offbalance_note | 총 약정 $707B | legacy_unverified | text | SRC-v15-html | 총 약정 $707B | 부외 약정 원문(A/B/C 분류 전) |
| operating_income_ttm | $147.6B | verified | derived | SRC-SEC-FACTS-F6 | 2025-07-01~2026-06-30 147,628,000,000 | F6-REG-28. G1-FILL-27 기준값 |
| price | 337.12 | legacy_unverified | actual | SRC-v15-html | $337.12 |  |
| ps_ratio | 9.3 | legacy_unverified | actual | SRC-v15-html | 9.3 |  |
| quarter_note | Q2 (7/22) \| $119.8B (+24%) · GCP $24.8B(+82%) 영업이익 $8.8B \| 조정 $2.85 (컨센 $2.89 하회) \| Q2 사상 첫 마이너스 · TTM +$53B | legacy_unverified | text | SRC-v15-html |  | 최근 분기 실적 원문(③⑨ 참고). TTM 대체 금지 |
| revenue_ttm | $445.9B | verified | derived | SRC-SEC-FACTS-F6 | 2025-07-01~2026-06-30 445,866,000,000 | F6-REG-28. G1-FILL-27 기준값 |
| revenue_ttm_prior | $371.4B | verified | derived | SRC-SEC-FACTS-F6 | 2024-07-01~2025-06-30 371,399,000,000 | F6-REG-28. F6-SPEC-18 수집기 |
| runway_years | — | not_applicable | derived | SRC-v15-html | ∞ | TTM FCF 흑자라 런웨이 산식 적용 대상 아님(원문 ∞) |
| ttm_per | 16.9 | legacy_unverified | actual | SRC-v15-html | 16.9 |  |

### Amazon / AWS

| 지표 | 값 | 상태 | 종류 | 출처 | 원문 | 비고 |
| --- | --- | --- | --- | --- | --- | --- |
| capex_ttm | $173.0B | legacy_unverified | actual | SRC-v15-html | $173.0B |  |
| cash | $78.2B | verified | actual | SRC-SEC-FACTS-F6 | 현금및현금성자산 78.2B (버퍼 123.0B 는 basis 에 보존) | CASH-FCF-35. **순수 현금으로 등록한다** — 설계 지침 6.4. 유동성 버퍼와 총계는 basis.preserved_wider_def |
| cash | $123.0B | legacy_unverified | actual | SRC-v15-html | $123.0B | [CASH-FCF-35 대체됨 → amazon.cash.cashfcf35]  |
| contracted_revenue | $496.0B | verified | actual | SRC-SEC-AMZN-10Q-2026Q2 | RPO approximately $496 billion (2026-06-30) | OBS-REG-25. 승계 관측 amazon.contracted_revenue.v15(parse_failed)를 대체한다. **parse_fai |
| contracted_revenue | — | parse_failed | actual | SRC-v15-rule | AWS 백로그(수백 $B급) — 숫자 미공시 | [OBS-REG-25 대체됨 → amazon.contracted_revenue.obsreg25] 규칙 v1.5 ⑨ 게이트 4 적용표 |
| credit_rating | AA급 | legacy_unverified | text | SRC-v15-html | AA급 | 별표 J 교차검증 전용 — 점수 입력 아님 |
| debt_ebitda | 1.4 | legacy_unverified | actual | SRC-v15-html | 1.35 |  |
| fcf_ttm | -$11.6B | verified | derived | SRC-SEC-FACTS-F6 | TTM FCF -11.6B = OCF 161.4B - CapEx 173.0B | CASH-FCF-35. SEC 실측. OCF·CapEx 구성요소를 basis 에 남겼다 |
| fcf_ttm | -$11.6B | legacy_unverified | actual | SRC-v15-html | -$11.6B | [CASH-FCF-35 대체됨 → amazon.fcf_ttm.cashfcf35]  |
| market_cap | $2.75T | legacy_unverified | actual | SRC-v15-html | $2.75T |  |
| net_borrowing_ttm | $75.2B | legacy_unverified | actual | SRC-v15-html | +$75.2B | 차환 제외 순증 |
| net_cash | -$119.3B | verified | derived | SRC-SEC-FACTS-F6 | 현금+증권 123.0B − 차입 132.5B − 리스 109.8B = -119.3B | NETCASH-37. SEC 보존 원자료 실측. **정의는 legacy 역산 작업 정의다** |
| net_cash | -$128.7B | legacy_unverified | actual | SRC-v15-html | -$128.7B | [NETCASH-37 대체됨 → amazon.net_cash.nc37]  |
| net_income_ttm | $135.3B | verified | derived | SRC-SEC-FACTS-F6 | 2025-07-01~2026-06-30 135,281,000,000 | F6-REG-28. F6-SPEC-18 수집기 |
| nonop_share | 46% | legacy_unverified | actual | SRC-v15-html | 46% ⚠️ |  |
| ntm_per | 27.5 | legacy_unverified | estimate | SRC-v15-html | 27.5 |  |
| offbalance_B | $267.3B | verified | derived | SRC-SEC-AMZN-10Q-2026Q2 | 미개시 리스 $137,214M + 무조건 구매약정 $130,065M = $267,279M (2026-06-30) | OBS-REG-25. 승계 관측 amazon.offbalance_B.v15($106B, 출처 불명)를 대체한다. **106,000 은 2026Q |
| offbalance_B | $106.0B | legacy_unverified | actual | SRC-v15-rule | 미개시 리스 $106B(3/31) | [OBS-REG-25 대체됨 → amazon.offbalance_B.obsreg25] 규칙 v1.5 ⑨ 게이트 4 적용표 |
| offbalance_note | 미개시 리스 $106B | legacy_unverified | text | SRC-v15-html | 미개시 리스 $106B | 부외 약정 원문(A/B/C 분류 전) |
| operating_income_ttm | $93.7B | verified | derived | SRC-SEC-FACTS-F6 | 2025-07-01~2026-06-30 93,712,000,000 | F6-REG-28. G1-FILL-27 기준값 |
| price | 254.98 | legacy_unverified | actual | SRC-v15-html | $254.98 |  |
| ps_ratio | 3.6 | legacy_unverified | actual | SRC-v15-html | 3.6 |  |
| quarter_note | Q2 (7/30) \| $200.61B (+20%) · AWS $42.2B(+37%) 18분기 최고 \| $5.75 ⚠️ 평가익 포함 \| TTM -$11.6B 실측 확정 | legacy_unverified | text | SRC-v15-html |  | 최근 분기 실적 원문(③⑨ 참고). TTM 대체 금지 |
| revenue_ttm | $775.7B | verified | derived | SRC-SEC-FACTS-F6 | 2025-07-01~2026-06-30 775,680,000,000 | F6-REG-28. G1-FILL-27 기준값 |
| revenue_ttm_prior | $670.0B | verified | derived | SRC-SEC-FACTS-F6 | 2024-07-01~2025-06-30 670,038,000,000 | F6-REG-28. F6-SPEC-18 수집기 |
| runway_years | 10.6 | legacy_unverified | derived | SRC-v15-html | 10.6년 | 원본 계산값(현금 ÷ 연 소진) |
| ttm_per | 20.5 | legacy_unverified | actual | SRC-v15-html | 20.5 |  |

### Meta

| 지표 | 값 | 상태 | 종류 | 출처 | 원문 | 비고 |
| --- | --- | --- | --- | --- | --- | --- |
| capex_ttm | $89.3B | legacy_unverified | actual | SRC-v15-html | $89.3B |  |
| cash | $15.5B | verified | actual | SRC-SEC-FACTS-F6 | 현금및현금성자산 15.5B (버퍼 90.3B 는 basis 에 보존) | CASH-FCF-35. **순수 현금으로 등록한다** — 설계 지침 6.4. 유동성 버퍼와 총계는 basis.preserved_wider_def |
| cash | $90.3B | legacy_unverified | actual | SRC-v15-html | $90.3B | [CASH-FCF-35 대체됨 → meta.cash.cashfcf35]  |
| credit_rating | AA- | legacy_unverified | text | SRC-v15-html | AA- | 별표 J 교차검증 전용 — 점수 입력 아님 |
| debt_ebitda | 1.0 | legacy_unverified | actual | SRC-v15-html | 0.99 |  |
| fcf_ttm | $41.0B | verified | derived | SRC-SEC-FACTS-F6 | TTM FCF 41.0B = OCF 130.3B - CapEx 89.3B | CASH-FCF-35. SEC 실측. OCF·CapEx 구성요소를 basis 에 남겼다 |
| fcf_ttm | $41.0B | legacy_unverified | actual | SRC-v15-html | +$41.0B | [CASH-FCF-35 대체됨 → meta.fcf_ttm.cashfcf35]  |
| market_cap | $1.51T | legacy_unverified | actual | SRC-v15-html | $1.51T |  |
| net_borrowing_ttm | $51.7B | legacy_unverified | actual | SRC-v15-html | +$51.7B | 차환 제외 순증 |
| net_cash | -$22.1B | verified | derived | SRC-SEC-FACTS-F6 | 현금+증권 90.3B − 차입 83.7B − 리스 28.7B = -22.1B | NETCASH-37. SEC 보존 원자료 실측. **정의는 legacy 역산 작업 정의다** |
| net_cash | -$22.1B | legacy_unverified | actual | SRC-v15-html | -$22.1B | [NETCASH-37 대체됨 → meta.net_cash.nc37]  |
| net_income_ttm | $68.1B | verified | derived | SRC-SEC-FACTS-F6 | 2025-07-01~2026-06-30 68,098,000,000 | F6-REG-28. F6-SPEC-18 수집기 |
| nonop_share | 1% | legacy_unverified | actual | SRC-v15-html | 1% |  |
| ntm_per | 17.9 | legacy_unverified | estimate | SRC-v15-html | 17.9 |  |
| offbalance_note | 리스 $279B + 계약 $349B = $628B | legacy_unverified | text | SRC-v15-html | 리스 $279B + 계약 $349B = $628B | 부외 약정 원문(A/B/C 분류 전) |
| operating_income_ttm | $86.9B | verified | derived | SRC-SEC-FACTS-F6 | 2025-07-01~2026-06-30 86,926,000,000 | F6-REG-28. G1-FILL-27 기준값 |
| price | 592.85 | legacy_unverified | actual | SRC-v15-html | $592.85 |  |
| ps_ratio | 6.6 | legacy_unverified | actual | SRC-v15-html | 6.6 |  |
| quarter_note | Q2 (7/29) \| $60.80B (+28%) \| $6.18 (컨센 $7.14 하회) \| Q2 +$0.78B (-91%) · TTM +$41B | legacy_unverified | text | SRC-v15-html |  | 최근 분기 실적 원문(③⑨ 참고). TTM 대체 금지 |
| revenue_ttm | $228.2B | verified | derived | SRC-SEC-FACTS-F6 | 2025-07-01~2026-06-30 228,247,000,000 | F6-REG-28. G1-FILL-27 기준값 |
| revenue_ttm_prior | $178.8B | verified | derived | SRC-SEC-FACTS-F6 | 2024-07-01~2025-06-30 178,805,000,000 | F6-REG-28. F6-SPEC-18 수집기 |
| runway_years | — | not_applicable | derived | SRC-v15-html | ∞ | TTM FCF 흑자라 런웨이 산식 적용 대상 아님(원문 ∞) |
| ttm_per | 21.8 | legacy_unverified | actual | SRC-v15-html | 21.8 |  |

### Microsoft

| 지표 | 값 | 상태 | 종류 | 출처 | 원문 | 비고 |
| --- | --- | --- | --- | --- | --- | --- |
| capex_ttm | $116.0B | legacy_unverified | actual | SRC-v15-html | $116.0B |  |
| cash | $20.9B | verified | actual | SRC-SEC-FACTS-F6 | 현금및현금성자산 20.9B (버퍼 76.8B 는 basis 에 보존) | CASH-FCF-35. **순수 현금으로 등록한다** — 설계 지침 6.4. 유동성 버퍼와 총계는 basis.preserved_wider_def |
| cash | $76.8B | legacy_unverified | actual | SRC-v15-html | $76.8B | [CASH-FCF-35 대체됨 → microsoft.cash.cashfcf35]  |
| credit_rating | AAA급 | legacy_unverified | text | SRC-v15-html | AAA급 | 별표 J 교차검증 전용 — 점수 입력 아님 |
| debt_ebitda | 0.6 | legacy_unverified | actual | SRC-v15-html | 0.64 |  |
| fcf_ttm | $67.0B | verified | derived | SRC-SEC-FACTS-F6 | TTM FCF 67.0B = OCF 182.9B - CapEx 115.9B | CASH-FCF-35. SEC 실측. OCF·CapEx 구성요소를 basis 에 남겼다 |
| fcf_ttm | $67.0B | legacy_unverified | actual | SRC-v15-html | +$67.0B | [CASH-FCF-35 대체됨 → microsoft.fcf_ttm.cashfcf35]  |
| market_cap | $3.69T | legacy_unverified | actual | SRC-v15-html | $3.69T |  |
| net_borrowing_ttm | -$3.0B | legacy_unverified | actual | SRC-v15-html | -$3.0B | 차환 제외 순증 |
| net_cash | -$52.0B | verified | derived | SRC-SEC-FACTS-F6 | 현금+증권 76.8B − 차입 40.3B − 리스 88.5B = -52.0B | NETCASH-37. SEC 보존 원자료 실측. **정의는 legacy 역산 작업 정의다** |
| net_cash | -$52.0B | legacy_unverified | actual | SRC-v15-html | -$52.0B | [NETCASH-37 대체됨 → microsoft.net_cash.nc37]  |
| net_income_ttm | $133.7B | verified | actual | SRC-SEC-FACTS-F6 | 2025-07-01~2026-06-30 133,749,000,000 | F6-REG-28. F6-SPEC-18 수집기 |
| nonop_share | 6% | legacy_unverified | actual | SRC-v15-html | 6% |  |
| ntm_per | 25.4 | legacy_unverified | estimate | SRC-v15-html | 25.4 |  |
| offbalance_note | 미분리 (QTS $3.9B만 확인) | legacy_unverified | text | SRC-v15-html | 미분리 (QTS $3.9B만 확인) | 부외 약정 원문(A/B/C 분류 전) |
| operating_income_ttm | $155.2B | verified | actual | SRC-SEC-FACTS-F6 | 2025-07-01~2026-06-30 155,237,000,000 | F6-REG-28. G1-FILL-27 기준값 |
| price | 496.82 | legacy_unverified | actual | SRC-v15-html | $496.82 |  |
| ps_ratio | 11.1 | legacy_unverified | actual | SRC-v15-html | 11.1 |  |
| quarter_note | Q4 FY26 (7/29) \| $90B (+18%) · 🆕 Azure $29.42B(+42%) 최초 달러 공시 \| non-GAAP $4.74 (컨센 $4.24 상회) \| TTM +$67B · capex 감축 | legacy_unverified | text | SRC-v15-html |  | 최근 분기 실적 원문(③⑨ 참고). TTM 대체 금지 |
| revenue_ttm | $331.8B | verified | actual | SRC-SEC-FACTS-F6 | 2025-07-01~2026-06-30 331,839,000,000 | F6-REG-28. G1-FILL-27 기준값 |
| revenue_ttm_prior | $281.7B | verified | actual | SRC-SEC-FACTS-F6 | 2024-07-01~2025-06-30 281,724,000,000 | F6-REG-28. F6-SPEC-18 수집기 |
| runway_years | — | not_applicable | derived | SRC-v15-html | ∞ | TTM FCF 흑자라 런웨이 산식 적용 대상 아님(원문 ∞) |
| ttm_per | 27.9 | legacy_unverified | actual | SRC-v15-html | 27.9 |  |

### TSMC

| 지표 | 값 | 상태 | 종류 | 출처 | 원문 | 비고 |
| --- | --- | --- | --- | --- | --- | --- |
| capex_ttm | $46.9B | legacy_unverified | actual | SRC-v15-html | $46.9B |  |
| cash | $88.2B | verified | actual | SRC-SEC-TSM-20F-FY2025 | 현금및현금성자산 88.2B (버퍼 99.7B 는 basis 에 보존) | CASH-FCF-35. **순수 현금으로 등록한다** — 설계 지침 6.4. 유동성 버퍼와 총계는 basis.preserved_wider_def |
| cash | $110.6B | legacy_unverified | actual | SRC-v15-html | $110.6B | [CASH-FCF-35 대체됨 → tsmc.cash.cashfcf35]  |
| credit_rating | AA-급 | legacy_unverified | text | SRC-v15-html | AA-급 | 별표 J 교차검증 전용 — 점수 입력 아님 |
| debt_ebitda | 0.3 | legacy_unverified | actual | SRC-v15-html | 0.34 |  |
| fcf_ttm | $32.0B | verified | derived | SRC-SEC-TSM-20F-FY2025 | TTM FCF 32.0B = OCF 72.5B - CapEx 40.6B | CASH-FCF-35. SEC 실측. OCF·CapEx 구성요소를 basis 에 남겼다 |
| fcf_ttm | $36.0B | legacy_unverified | actual | SRC-v15-html | +$36.0B | [CASH-FCF-35 대체됨 → tsmc.fcf_ttm.cashfcf35]  |
| market_cap | $2.15T | legacy_unverified | actual | SRC-v15-html | $2.15T ✱ |  |
| net_borrowing_ttm | $100M | legacy_unverified | actual | SRC-v15-html | +$0.1B | 차환 제외 순증 |
| net_cash | $69.9B | verified | derived | SRC-SEC-TSM-20F-FY2025 | NT$백만 3,262,634.8 − 1,032,987.7 − 35,428.0 = 2,194,219.1 ÷ 31.37 = 69.9B USD | NETCASH-37. **보존 20-F 문면 실측** — companyfacts 에 이 기준일 금액 사실이 없다 |
| net_cash | $77.0B | legacy_unverified | actual | SRC-v15-html | +$77.0B | [NETCASH-37 대체됨 → tsmc.net_cash.nc37]  |
| net_income_ttm | $54.0B | verified | actual | SRC-SEC-TSM-20F-FY2025 | FY2025 순이익 NT$1,695,124.9백만 | F6-REG-28 / TSM-EDGAR-29. 손익계산서 NET INCOME 행 |
| nonop_share | 7% | legacy_unverified | actual | SRC-v15-html | 7% |  |
| ntm_per | 19.4 | legacy_unverified | estimate | SRC-v15-html | 19.4 ✱ |  |
| offbalance_note | 미확인 | legacy_unverified | text | SRC-v15-html | 미확인 | 부외 약정 원문(A/B/C 분류 전) |
| operating_income_ttm | $61.7B | verified | actual | SRC-SEC-TSM-20F-FY2025 | FY2025 영업이익 NT$1,936,091.7백만 | F6-REG-28 / TSM-EDGAR-29. INCOME FROM OPERATIONS 행. MD&A 반올림 1,936,092 가 아니라 **감 |
| operating_margin_ttm | 51% | verified | derived | SRC-SEC-TSM-20F-FY2025 | FY2025 영업이익률 +50.83% | F6-REG-28 / TSM-EDGAR-29. FY2024 45.68% 에서 +5.15%p |
| price | 415.5 | legacy_unverified | actual | SRC-v15-html | $415.50 |  |
| ps_ratio | 15.4 | legacy_unverified | actual | SRC-v15-html | 15.4 |  |
| quarter_note | Q2 (7/16) \| $40.2B (+36%) · HPC 66% \| GM 67.7% / OpM 60.3% 역대 최고 · 2026 가이던스 +30%→+40% 이상 \| TTM +$36B · capex $60~64B | legacy_unverified | text | SRC-v15-html |  | 최근 분기 실적 원문(③⑨ 참고). TTM 대체 금지 |
| revenue_ttm | $121.4B | verified | actual | SRC-SEC-TSM-20F-FY2025 | FY2025 매출 NT$3,809,054.3백만 (US$121,423.5백만) | F6-REG-28 / TSM-EDGAR-29. **EDGAR 원문 우회 건**이다 — basis.bypass 에 사유·검산·복귀 조건을 남겼다 |
| revenue_ttm_prior | $92.3B | verified | actual | SRC-SEC-TSM-20F-FY2025 | FY2024 매출 NT$2,894,307.7백만 (같은 표 둘째 열) | F6-REG-28. **당해와 같은 환율 31.37 로 환산**했다. 공시 USD 를 그대로 쓰지 않았다 |
| runway_years | — | not_applicable | derived | SRC-v15-html | ∞ | TTM FCF 흑자라 런웨이 산식 적용 대상 아님(원문 ∞) |
| ttm_per | 30.9 | legacy_unverified | actual | SRC-v15-html | 30.9 |  |

### Alibaba

| 지표 | 값 | 상태 | 종류 | 출처 | 원문 | 비고 |
| --- | --- | --- | --- | --- | --- | --- |
| capex_ttm | $23.1B | legacy_unverified | actual | SRC-v15-html | $23.1B |  |
| cash | $19.1B | verified | actual | SRC-SEC-BABA-20F-FY2026 | 현금및현금성자산 19.1B (버퍼 41.6B 는 basis 에 보존) | CASH-FCF-35. **순수 현금으로 등록한다** — 설계 지침 6.4. 유동성 버퍼와 총계는 basis.preserved_wider_def |
| cash | $56.8B | legacy_unverified | actual | SRC-v15-html | $56.8B | [CASH-FCF-35 대체됨 → alibaba.cash.cashfcf35]  |
| contracted_revenue | — | not_disclosed | actual | SRC-SEC-BABA-20F-FY2026 | 미공시 — ASC 606 실무적 간편법 선언 | OBS-REG-25. **회사가 공시하지 않겠다고 선언한 회계정책이다.** '이 문서에 없다' 와 다르다 — 찾아도 없을 것이 선언돼 있다. C |
| contracted_revenue | — | not_disclosed | actual | SRC-v15-rule | — | [OBS-REG-25 대체됨 → alibaba.contracted_revenue.obsreg25] 규칙 v1.5 ⑨ 게이트 4 적용표 |
| credit_rating | A급 | legacy_unverified | text | SRC-v15-html | A급 | 별표 J 교차검증 전용 — 점수 입력 아님 |
| debt_ebitda | 2.7 | legacy_unverified | actual | SRC-v15-html | 2.68 |  |
| fcf_ttm | -$7.2B | verified | derived | SRC-SEC-BABA-20F-FY2026 | TTM FCF -7.2B = OCF 11.0B - CapEx 18.3B | CASH-FCF-35. SEC 실측. OCF·CapEx 구성요소를 basis 에 남겼다 |
| fcf_ttm | -$11.4B | legacy_unverified | actual | SRC-v15-html | -$11.4B | [CASH-FCF-35 대체됨 → alibaba.fcf_ttm.cashfcf35]  |
| market_cap | $270.0B | legacy_unverified | actual | SRC-v15-html | $270B |  |
| net_borrowing_ttm | $7.5B | legacy_unverified | actual | SRC-v15-html | +$7.5B | 차환 제외 순증 |
| net_cash | $17.5B | legacy_unverified | actual | SRC-v15-html | +$17.5B |  |
| net_income_ttm | $15.0B | verified | actual | SRC-SEC-BABA-FACTS | 2025-04-01~2026-03-31 103,592,000,000 CNY | F6-REG-28. **당해와 같은 환율 6.8980 으로 환산**했다 |
| nonop_share | 54% | legacy_unverified | actual | SRC-v15-html | 54% ⚠️ |  |
| ntm_per | 16.7 | legacy_unverified | estimate | SRC-v15-html | 16.7 ✱ |  |
| offbalance_B | $36.9B | verified | derived | SRC-SEC-BABA-20F-FY2026 | 자본약정 RMB54,136M + 기타약정 RMB200,062M = RMB254,198M (2026-03-31) → US$36,851M @6.89 | OBS-REG-25. **원 통화는 RMB 다.** 스키마가 unit 을 지표 단위(USD)로 강제해 RMB 를 그대로 둘 자리가 없어 20-F |
| offbalance_B | — | not_disclosed | actual | SRC-v15-rule | 미확인 | [OBS-REG-25 대체됨 → alibaba.offbalance_B.obsreg25] 규칙 v1.5 ⑨ 게이트 4 적용표 |
| offbalance_note | 미확인 (증자 $10.2B) | legacy_unverified | text | SRC-v15-html | 미확인 (증자 $10.2B) | 부외 약정 원문(A/B/C 분류 전) |
| operating_income_ttm | $7.3B | verified | actual | SRC-SEC-BABA-FACTS | FY2026 영업이익 RMB50,150M (US$7,270M) | OBS-REG-25 / G1-TTM-26. 연간 기준. |
| operating_margin_ttm | 5% | verified | derived | SRC-SEC-BABA-FACTS | FY2026 영업이익률 +4.899% | OBS-REG-25 / G1-TTM-26. **양수다** — G1 을 통과한다. **연간 기준이라는 한계는 F6 P4 가 이미 한 칸 내린다.  |
| price | 111.76 | legacy_unverified | actual | SRC-v15-html | $111.76 |  |
| ps_ratio | 1.8 | legacy_unverified | actual | SRC-v15-html | 1.8 |  |
| quarter_note | 6월 분기 (8/20) \| $39.64B (+9%) · 클라우드 +26% \| non-GAAP $1.26 (컨센 $1.51 하회) · 영업흑자 복귀 \| 분기 -$6.6B · TTM -$11.4B · 완충 $41B+$10.2B | legacy_unverified | text | SRC-v15-html |  | 최근 분기 실적 원문(③⑨ 참고). TTM 대체 금지 |
| revenue_ttm | $148.4B | verified | actual | SRC-SEC-BABA-FACTS | FY2026 매출 RMB1,023,670M (US$148,401M) | OBS-REG-25 / G1-TTM-26. **연간 기준이다.** F6 P4 가 기간 단위 TTM 아님으로 한 칸 내린다. 같은 한계를 F9 에 |
| revenue_ttm_prior | $144.4B | verified | actual | SRC-SEC-BABA-FACTS | 2024-04-01~2025-03-31 996,347,000,000 CNY | F6-REG-28. **당해와 같은 환율 6.8980 으로 환산**했다 |
| runway_years | 5.0 | legacy_unverified | derived | SRC-v15-html | 5.0년 | 원본 계산값(현금 ÷ 연 소진) |
| ttm_per | 25.8 | legacy_unverified | actual | SRC-v15-html | 25.8 |  |

### Anthropic

| 지표 | 값 | 상태 | 종류 | 출처 | 원문 | 비고 |
| --- | --- | --- | --- | --- | --- | --- |
| arr | $65.0B | legacy_unverified | run_rate | SRC-v15-rule | ARR $65B(7월 런레이트) | 규칙 v1.5 ⑥ 비상장 절 |
| arr_prior | $47.0B | legacy_unverified | run_rate | SRC-v15-md | ARR $47B → $65B (직전 런레이트) | PRIV-IMPL-31 / C-12. P3 입력. 시점 라벨이 원문에 없어 null 이다 |
| cash | — | not_disclosed | actual | SRC-v15-md | 미공시 | PRIV-IMPL-31 / C-20. 승계 관측 anthropic.cash.v15 의 결측 유형을 등록한다. **값은 그대로 없다** — 라벨만 |
| cash | — | not_disclosed | actual | SRC-v15-html | 미공시 | [PRIV-IMPL-31 대체됨 → anthropic.cash.priv31]  |
| contracted_revenue | $65.0B | incompatible_basis | actual | SRC-v15-rule | ARR $65B — 계약 수입 아님(C-07) | 규칙 v1.5 ⑨ 게이트 4 적용표 |
| credit_rating | 비상장 | legacy_unverified | text | SRC-v15-html | 비상장 | 별표 J 교차검증 전용 — 점수 입력 아님 |
| cumulative_raised | $125.0B | legacy_unverified | actual | SRC-v15-md | 약 $125B(2021년~) | PRIV-IMPL-31 / C-12. 승계 관측 anthropic.cumulative_raised.v15 를 대체한다 — **값은 같고 모순 기 |
| cumulative_raised | $125.0B | legacy_unverified | actual | SRC-v15-rule | 약 $125B(2021년~) | [PRIV-IMPL-31 대체됨 → anthropic.cumulative_raised.priv31] 규칙 v1.5 ⑥ 비상장 절 |
| debt_ebitda | — | not_disclosed | actual | SRC-v15-md | — | PRIV-IMPL-31 / C-20. 승계 관측 anthropic.debt_ebitda.v15 의 결측 유형을 등록한다. **값은 그대로 없다* |
| debt_ebitda | — | not_disclosed | actual | SRC-v15-html | — | [PRIV-IMPL-31 대체됨 → anthropic.debt_ebitda.priv31]  |
| fcf_ttm | — | not_disclosed | actual | SRC-v15-md | 미공시 | PRIV-IMPL-31 / C-20. 승계 관측 anthropic.fcf_ttm.v15 의 결측 유형을 등록한다. **값은 그대로 없다** —  |
| fcf_ttm | — | not_disclosed | actual | SRC-v15-html | 미공시 | [PRIV-IMPL-31 대체됨 → anthropic.fcf_ttm.priv31] 비상장 FCF 미공시 |
| net_cash | — | not_disclosed | actual | SRC-v15-md | — | PRIV-IMPL-31 / C-20. 승계 관측 anthropic.net_cash.v15 의 결측 유형을 등록한다. **값은 그대로 없다** — |
| net_cash | — | not_disclosed | actual | SRC-v15-html | — | [PRIV-IMPL-31 대체됨 → anthropic.net_cash.priv31]  |
| offbalance_B | $300.0B | incompatible_basis | actual | SRC-v15-rule | 컴퓨트 약정 $300B(연 ~$50B) — 기간·범위가 RPO 와 다름(C-07) | 규칙 v1.5 ⑨ 게이트 4 적용표 |
| offbalance_note | 컴퓨트 $300B | legacy_unverified | text | SRC-v15-html | 컴퓨트 $300B | 부외 약정 원문(A/B/C 분류 전) |
| operating_margin_ttm | — | not_disclosed | derived | SRC-v15-md | 미공시 — 비상장이라 TTM 영업손익 공시 의무 없음 | PRIV-IMPL-31 / C-20. G1 판정 보류의 근거 라벨. 통과도 실패도 아니다 |
| post_money_valuation | $965.0B | legacy_unverified | actual | SRC-v15-rule | $965B | 규칙 v1.5 ⑥ 비상장 절 |
| ps_ratio | 30.0 | legacy_unverified | estimate | SRC-v15-md | TTM 보정 ~30~39배 (밸류 $965B, Q2 매출 $10.9B 역산) | PRIV-IMPL-31 / C-12. **P2 분모는 arr 이 아니라 TTM 보정 매출이다.** 구간 추정이라 estimate_range 를  |
| quarter_note | Q2 \| $10.9B · 런레이트 $65B(7월) \| 첫 영업흑자 $559M \| 외부 조달 의존 · FCF 미공시 | legacy_unverified | text | SRC-v15-html |  | 최근 분기 실적 원문(③⑨ 참고). TTM 대체 금지 |
| runway_years | — | not_disclosed | derived | SRC-v15-html | 판정 불가 | FCF 미공시로 소진율을 만들 수 없음(원문 판정 불가) |

### Apple

| 지표 | 값 | 상태 | 종류 | 출처 | 원문 | 비고 |
| --- | --- | --- | --- | --- | --- | --- |
| capex_ttm | $10.0B | legacy_unverified | actual | SRC-v15-html | $10.0B |  |
| cash | $39.5B | verified | actual | SRC-SEC-FACTS-F6 | 현금및현금성자산 39.5B (버퍼 62.4B 는 basis 에 보존) | CASH-FCF-35. **순수 현금으로 등록한다** — 설계 지침 6.4. 유동성 버퍼와 총계는 basis.preserved_wider_def |
| cash | $146.5B | legacy_unverified | actual | SRC-v15-html | $146.5B | [CASH-FCF-35 대체됨 → apple.cash.cashfcf35]  |
| credit_rating | AA급 | legacy_unverified | text | SRC-v15-html | AA급 | 별표 J 교차검증 전용 — 점수 입력 아님 |
| debt_ebitda | 0.5 | legacy_unverified | actual | SRC-v15-html | 0.45 |  |
| fcf_ttm | $136.7B | verified | derived | SRC-SEC-FACTS-F6 | TTM FCF 136.7B = OCF 146.7B - CapEx 10.0B | CASH-FCF-35. SEC 실측. OCF·CapEx 구성요소를 basis 에 남겼다 |
| fcf_ttm | $136.7B | legacy_unverified | actual | SRC-v15-html | +$136.7B | [CASH-FCF-35 대체됨 → apple.fcf_ttm.cashfcf35]  |
| market_cap | $4.74T | legacy_unverified | actual | SRC-v15-html | $4.74T |  |
| net_borrowing_ttm | -$17.3B | legacy_unverified | actual | SRC-v15-html | -$17.3B | 차환 제외 순증 |
| net_cash | $62.2B | legacy_unverified | actual | SRC-v15-html | +$62.2B |  |
| net_income_ttm | $128.9B | verified | derived | SRC-SEC-FACTS-F6 | 2025-06-28~2026-06-27 128,930,000,000 | F6-REG-28. F6-SPEC-18 수집기 |
| nonop_share | 1% | legacy_unverified | actual | SRC-v15-html | 1% |  |
| ntm_per | 35.5 | legacy_unverified | estimate | SRC-v15-html | 35.5 |  |
| offbalance_note | 미확인 | legacy_unverified | text | SRC-v15-html | 미확인 | 부외 약정 원문(A/B/C 분류 전) |
| operating_income_ttm | $154.9B | verified | derived | SRC-SEC-FACTS-F6 | 2025-06-28~2026-06-27 154,859,000,000 | F6-REG-28. G1-FILL-27 기준값 |
| price | 324.96 | legacy_unverified | actual | SRC-v15-html | $324.96 |  |
| ps_ratio | 10.2 | legacy_unverified | actual | SRC-v15-html | 10.2 |  |
| quarter_note | 6월 분기 (7/30) \| $109.4B (+16%) \| $2.02 상회 (Services 하회) \| TTM +$137B | legacy_unverified | text | SRC-v15-html |  | 최근 분기 실적 원문(③⑨ 참고). TTM 대체 금지 |
| revenue_ttm | $466.8B | verified | derived | SRC-SEC-FACTS-F6 | 2025-06-28~2026-06-27 466,823,000,000 | F6-REG-28. G1-FILL-27 기준값 |
| revenue_ttm_prior | $408.6B | verified | derived | SRC-SEC-FACTS-F6 | 2024-06-29~2025-06-28 408,625,000,000 | F6-REG-28. F6-SPEC-18 수집기 |
| runway_years | — | not_applicable | derived | SRC-v15-html | ∞ | TTM FCF 흑자라 런웨이 산식 적용 대상 아님(원문 ∞) |
| ttm_per | 37.3 | legacy_unverified | actual | SRC-v15-html | 37.3 |  |

### NVIDIA

| 지표 | 값 | 상태 | 종류 | 출처 | 원문 | 비고 |
| --- | --- | --- | --- | --- | --- | --- |
| capex_ttm | $7.4B | legacy_unverified | actual | SRC-v15-html | $7.4B |  |
| cash | $22.4B | verified | actual | SRC-SEC-FACTS-F6 | 현금및현금성자산 22.4B (버퍼 56.6B 는 basis 에 보존) | CASH-FCF-35. **순수 현금으로 등록한다** — 설계 지침 6.4. 유동성 버퍼와 총계는 basis.preserved_wider_def |
| cash | $62.5B | legacy_unverified | actual | SRC-v15-html | $62.5B | [CASH-FCF-35 대체됨 → nvidia.cash.cashfcf35]  |
| credit_rating | AA~A급 | legacy_unverified | text | SRC-v15-html | AA~A급 | 별표 J 교차검증 전용 — 점수 입력 아님 |
| debt_ebitda | 0.2 | legacy_unverified | actual | SRC-v15-html | 0.19 |  |
| fcf_ttm | $127.0B | verified | derived | SRC-SEC-FACTS-F6 | TTM FCF 127.0B = OCF 134.4B - CapEx 7.4B | CASH-FCF-35. SEC 실측. OCF·CapEx 구성요소를 basis 에 남겼다 |
| fcf_ttm | $127.0B | legacy_unverified | actual | SRC-v15-html | +$127.0B | [CASH-FCF-35 대체됨 → nvidia.fcf_ttm.cashfcf35]  |
| market_cap | $5.42T | legacy_unverified | actual | SRC-v15-html | $5.42T |  |
| net_borrowing_ttm | $24.9B | legacy_unverified | actual | SRC-v15-html | +$24.9B | 차환 제외 순증 |
| net_cash | $24.6B | verified | derived | SRC-SEC-FACTS-F6 | 현금+증권 63.4B − 차입 33.4B − 리스 5.5B = 24.6B | NETCASH-37. SEC 보존 원자료 실측. **정의는 legacy 역산 작업 정의다** |
| net_cash | $23.6B | legacy_unverified | actual | SRC-v15-html | +$23.6B | [NETCASH-37 대체됨 → nvidia.net_cash.nc37]  |
| net_income_ttm | $192.9B | verified | derived | SRC-SEC-FACTS-F6 | 2025-07-28~2026-07-26 192,879,000,000 | F6-REG-28. F6-SPEC-18 수집기 |
| nonop_share | 14% | legacy_unverified | actual | SRC-v15-html | 14% ᵃ |  |
| ntm_per | 18.0 | legacy_unverified | estimate | SRC-v15-html | 18.0 |  |
| offbalance_note | 보증 $105B + 잔존가치 25% + 백스톱 + $6.3B (우발·C종) | legacy_unverified | text | SRC-v15-html | 보증 $105B + 잔존가치 25% + 백스톱 + $6.3B (우발·C종) | 부외 약정 원문(A/B/C 분류 전) |
| operating_income_ttm | $197.6B | verified | derived | SRC-SEC-FACTS-F6 | 2025-07-28~2026-07-26 197,579,000,000 | F6-REG-28. G1-FILL-27 기준값 |
| price | 224.41 | legacy_unverified | actual | SRC-v15-html | $224.41 |  |
| ps_ratio | 17.9 | legacy_unverified | actual | SRC-v15-html | 17.9 |  |
| quarter_note | Q2 FY27 (8/26) \| $96.2B (+106%) · DC $89.0B (+117%) \| GAAP $2.46 / non-GAAP $2.22 · DC 컨센 $86.3B 상회 \| TTM +$127B · 환원 $26B | legacy_unverified | text | SRC-v15-html |  | 최근 분기 실적 원문(③⑨ 참고). TTM 대체 금지 |
| revenue_ttm | $303.0B | verified | derived | SRC-SEC-FACTS-F6 | 2025-07-28~2026-07-26 302,970,000,000 | F6-REG-28. G1-FILL-27 기준값 |
| revenue_ttm_prior | $165.2B | verified | derived | SRC-SEC-FACTS-F6 | 2024-07-29~2025-07-27 165,218,000,000 | F6-REG-28. F6-SPEC-18 수집기 |
| runway_years | — | not_applicable | derived | SRC-v15-html | ∞ | TTM FCF 흑자라 런웨이 산식 적용 대상 아님(원문 ∞) |
| ttm_per | 27.5 | legacy_unverified | actual | SRC-v15-html | 27.5 |  |

### Palantir

| 지표 | 값 | 상태 | 종류 | 출처 | 원문 | 비고 |
| --- | --- | --- | --- | --- | --- | --- |
| capex_ttm | $40M | legacy_unverified | actual | SRC-v15-html | $0.04B |  |
| cash | $2.0B | verified | actual | SRC-SEC-FACTS-F6 | 현금및현금성자산 2.0B (버퍼 9.4B 는 basis 에 보존) | CASH-FCF-35. **순수 현금으로 등록한다** — 설계 지침 6.4. 유동성 버퍼와 총계는 basis.preserved_wider_def |
| cash | $9.4B | legacy_unverified | actual | SRC-v15-html | $9.4B | [CASH-FCF-35 대체됨 → palantir.cash.cashfcf35]  |
| credit_rating | 무차입 | legacy_unverified | text | SRC-v15-html | 무차입 | 별표 J 교차검증 전용 — 점수 입력 아님 |
| debt_ebitda | 0.1 | legacy_unverified | actual | SRC-v15-html | 0.08 |  |
| fcf_ttm | $3.4B | verified | derived | SRC-SEC-FACTS-F6 | TTM FCF 3.4B = OCF 3.4B - CapEx 0.0B | CASH-FCF-35. SEC 실측. OCF·CapEx 구성요소를 basis 에 남겼다 |
| fcf_ttm | $3.4B | legacy_unverified | actual | SRC-v15-html | +$3.4B | [CASH-FCF-35 대체됨 → palantir.fcf_ttm.cashfcf35]  |
| market_cap | $407.0B | legacy_unverified | actual | SRC-v15-html | $407B |  |
| net_borrowing_ttm | — | not_disclosed | actual | SRC-v15-html | 없음 | 차환 제외 순증 |
| net_cash | $9.2B | legacy_unverified | actual | SRC-v15-html | +$9.2B |  |
| net_income_ttm | $3.0B | verified | derived | SRC-SEC-FACTS-F6 | 2025-07-01~2026-06-30 3,016,692,000 | F6-REG-28. F6-SPEC-18 수집기 |
| nonop_share | 14% | legacy_unverified | actual | SRC-v15-html | 14% ᵇ |  |
| ntm_per | 89.0 | legacy_unverified | estimate | SRC-v15-html | 89.0 |  |
| offbalance_note | 없음 | legacy_unverified | text | SRC-v15-html | 없음 | 부외 약정 원문(A/B/C 분류 전) |
| operating_income_ttm | $2.6B | verified | derived | SRC-SEC-FACTS-F6 | 2025-07-01~2026-06-30 2,634,652,000 | F6-REG-28. G1-FILL-27 기준값 |
| price | 169.46 | legacy_unverified | actual | SRC-v15-html | $169.46 |  |
| ps_ratio | 66.2 | legacy_unverified | actual | SRC-v15-html | 66.2 |  |
| quarter_note | Q2 (8/3) \| $1.94B (+92.8%) · 4분기 연속 상회 \| $0.41 (컨센 $0.35 상회) \| TTM +$3.4B | legacy_unverified | text | SRC-v15-html |  | 최근 분기 실적 원문(③⑨ 참고). TTM 대체 금지 |
| revenue_ttm | $6.2B | verified | derived | SRC-SEC-FACTS-F6 | 2025-07-01~2026-06-30 6,155,941,000 | F6-REG-28. G1-FILL-27 기준값 |
| revenue_ttm_prior | $3.4B | verified | derived | SRC-SEC-FACTS-F6 | 2024-07-01~2025-06-30 3,440,587,000 | F6-REG-28. F6-SPEC-18 수집기 |
| runway_years | — | not_applicable | derived | SRC-v15-html | ∞ | TTM FCF 흑자라 런웨이 산식 적용 대상 아님(원문 ∞) |
| ttm_per | 144.9 | legacy_unverified | actual | SRC-v15-html | 144.9 |  |

### SpaceX + xAI

| 지표 | 값 | 상태 | 종류 | 출처 | 원문 | 비고 |
| --- | --- | --- | --- | --- | --- | --- |
| capex_ttm | $42.4B | legacy_unverified | actual | SRC-v15-html | $42.4B |  |
| cash | $93.5B | verified | actual | SRC-SEC-FACTS-F6 | 현금및현금성자산 93.5B (버퍼 93.5B 는 basis 에 보존) | CASH-FCF-35. **순수 현금으로 등록한다** — 설계 지침 6.4. 유동성 버퍼와 총계는 basis.preserved_wider_def |
| cash | $100.0B | legacy_unverified | actual | SRC-v15-html | $100.0B | [CASH-FCF-35 대체됨 → spacex-xai.cash.cashfcf35]  |
| contracted_revenue | $47.5B | verified | actual | SRC-SEC-SPCX-10Q-2026Q2 | Backlog $47,461M (2026-06-30) | OBS-REG-25. 승계 관측 spacex-xai.contracted_revenue.v15($47.5B, legacy_unverified)를  |
| contracted_revenue | $47.5B | legacy_unverified | actual | SRC-v15-rule | 백로그 $47.5B | [OBS-REG-25 대체됨 → spacex-xai.contracted_revenue.obsreg25] 규칙 v1.5 ⑨ 게이트 4 적용표 |
| credit_rating | 무등급 | legacy_unverified | text | SRC-v15-html | 무등급 | 별표 J 교차검증 전용 — 점수 입력 아님 |
| debt_ebitda | 5.8 | legacy_unverified | actual | SRC-v15-html | 5.78 ⚠️ |  |
| fcf_ttm | -$32.3B | verified | derived | SRC-SEC-FACTS-F6 | TTM FCF -32.3B = OCF 9.9B - CapEx 42.2B | CASH-FCF-35. SEC 실측. OCF·CapEx 구성요소를 basis 에 남겼다 |
| fcf_ttm | -$32.5B | legacy_unverified | actual | SRC-v15-html | -$32.5B | [CASH-FCF-35 대체됨 → spacex-xai.fcf_ttm.cashfcf35]  |
| market_cap | $1.91T | legacy_unverified | actual | SRC-v15-html | $1.91T |  |
| net_borrowing_ttm | $102.0B | legacy_unverified | actual | SRC-v15-html | +$102.0B | 차환 제외 순증 |
| net_cash | $54.6B | verified | derived | SRC-SEC-FACTS-F6 | 현금+증권 94.4B − 차입 39.4B − 리스 0.3B = 54.6B | NETCASH-37. SEC 보존 원자료 실측. **정의는 legacy 역산 작업 정의다** |
| net_cash | $60.3B | legacy_unverified | actual | SRC-v15-html | +$60.3B | [NETCASH-37 대체됨 → spacex-xai.net_cash.nc37]  |
| net_income_ttm | -$8.2B | verified | derived | SRC-SEC-FACTS-F6 | TTM -8,218백만 | F6-REG-28. S-1/A 감사 손익계산서 FY2025 + 10-Q 2026 상반기 - 10-Q 2025 상반기. **매출 쌍(분기)과 기준 |
| nonop_share | — | not_disclosed | actual | SRC-v15-html | 적자 |  |
| ntm_per | 111.0 | legacy_unverified | estimate | SRC-v15-html | 111 |  |
| offbalance_B | $29.6B | verified | derived | SRC-SEC-SPCX-10Q-2026Q2 | 미개시 리스 $1,627M(2025-12-31) + 무조건 구매약정 $27,955M(2026-06-30) = $29,582M | OBS-REG-25. **기준일이 섞인 합계다.** 구성요소별 기준일·출처를 basis.components 에 남겼다. 관측을 둘로 쪼개지 않은 |
| offbalance_B | — | not_disclosed | actual | SRC-v15-rule | 미확인 | [OBS-REG-25 대체됨 → spacex-xai.offbalance_B.obsreg25] 규칙 v1.5 ⑨ 게이트 4 적용표 |
| offbalance_note | 미확인 | legacy_unverified | text | SRC-v15-html | 미확인 | 부외 약정 원문(A/B/C 분류 전) |
| operating_income_ttm | -$3.7B | verified | derived | SRC-SEC-FACTS-F6 | TTM -3,732백만 | F6-REG-28. S-1/A 감사 손익계산서 FY2025 + 10-Q 2026 상반기 - 10-Q 2025 상반기. **매출 쌍(분기)과 기준 |
| operating_margin_ttm | -16% | verified | derived | SRC-SEC-FACTS-F6 | TTM 영업손실률 -16.195% | F6-REG-28. 승계 legacy -14.9% 를 실측 -16.195% 로 교체한다. 재척도 밴드에서 둘 다 -3 이라 점수는 안 바뀌고 근 |
| operating_margin_ttm | -15% | legacy_unverified | actual | SRC-v15-html | -$0.09 (컨센 -$0.26 상회) · 영업적자 -14.9% | [F6-REG-28 대체됨 → spacex-xai.operating_margin_ttm.f6reg28] EARN 열의 영업적자율. 규칙 ⑨ 표는 |
| price | 140.71 | legacy_unverified | actual | SRC-v15-html | $140.71 |  |
| ps_ratio | 82.9 | legacy_unverified | actual | SRC-v15-html | 82.9 |  |
| quarter_note | Q2 (8/4) \| $7.8B (+92%) · Starlink 1,200만 · AI 세그먼트 $2.56B(+247%) \| -$0.09 (컨센 -$0.26 상회) · 영업적자 -14.9% \| TTM -$32.5B · 현금 $100B | legacy_unverified | text | SRC-v15-html |  | 최근 분기 실적 원문(③⑨ 참고). TTM 대체 금지 |
| revenue_ttm | $7.8B | verified | actual | SRC-SEC-FACTS-F6 | 2026 Q2 매출 $7,814M | F6-REG-28. **분기 전년 동기 기준이다** |
| revenue_ttm_prior | $4.1B | verified | actual | SRC-SEC-FACTS-F6 | 2025 Q2 매출 $4,071M | F6-REG-28. 같은 분기 전년 동기 |
| runway_years | 3.1 | legacy_unverified | derived | SRC-v15-html | 3.1년 | 원본 계산값(현금 ÷ 연 소진) |
| ttm_per | — | not_disclosed | actual | SRC-v15-html | 적자 | 적자 |

### Tesla

| 지표 | 값 | 상태 | 종류 | 출처 | 원문 | 비고 |
| --- | --- | --- | --- | --- | --- | --- |
| capex_ttm | $12.9B | legacy_unverified | actual | SRC-v15-html | $12.9B |  |
| cash | $15.2B | verified | actual | SRC-SEC-FACTS-F6 | 현금및현금성자산 15.2B (버퍼 43.5B 는 basis 에 보존) | CASH-FCF-35. **순수 현금으로 등록한다** — 설계 지침 6.4. 유동성 버퍼와 총계는 basis.preserved_wider_def |
| cash | $43.5B | legacy_unverified | actual | SRC-v15-html | $43.5B | [CASH-FCF-35 대체됨 → tesla.cash.cashfcf35]  |
| credit_rating | 투자등급 | legacy_unverified | text | SRC-v15-html | 투자등급 | 별표 J 교차검증 전용 — 점수 입력 아님 |
| debt_ebitda | 1.3 | legacy_unverified | actual | SRC-v15-html | 1.27 |  |
| fcf_ttm | $5.8B | verified | derived | SRC-SEC-FACTS-F6 | TTM FCF 5.8B = OCF 18.7B - CapEx 12.9B | CASH-FCF-35. SEC 실측. OCF·CapEx 구성요소를 basis 에 남겼다 |
| fcf_ttm | $5.8B | legacy_unverified | actual | SRC-v15-html | +$5.8B | [CASH-FCF-35 대체됨 → tesla.fcf_ttm.cashfcf35]  |
| market_cap | $1.41T | legacy_unverified | actual | SRC-v15-html | $1.41T |  |
| net_borrowing_ttm | $1.8B | legacy_unverified | actual | SRC-v15-html | +$1.8B | 차환 제외 순증 |
| net_cash | $27.4B | verified | derived | SRC-SEC-FACTS-F6 | 현금+증권 43.5B − 차입 9.1B − 리스 7.0B = 27.4B | NETCASH-37. SEC 보존 원자료 실측. **정의는 legacy 역산 작업 정의다** |
| net_cash | $27.4B | legacy_unverified | actual | SRC-v15-html | +$27.4B | [NETCASH-37 대체됨 → tesla.net_cash.nc37]  |
| net_income_ttm | $3.8B | verified | derived | SRC-SEC-FACTS-F6 | 2025-07-01~2026-06-30 3,804,000,000 | F6-REG-28. F6-SPEC-18 수집기 |
| nonop_share | 18% | legacy_unverified | actual | SRC-v15-html | 18% ᵇ |  |
| ntm_per | 187.5 | legacy_unverified | estimate | SRC-v15-html | 187.5 |  |
| offbalance_note | 미확인 | legacy_unverified | text | SRC-v15-html | 미확인 | 부외 약정 원문(A/B/C 분류 전) |
| operating_income_ttm | $4.4B | verified | derived | SRC-SEC-FACTS-F6 | 2025-07-01~2026-06-30 4,372,000,000 | F6-REG-28. G1-FILL-27 기준값 |
| price | 357.01 | legacy_unverified | actual | SRC-v15-html | $357.01 |  |
| ps_ratio | 13.6 | legacy_unverified | actual | SRC-v15-html | 13.6 |  |
| quarter_note | Q2 (7/22) \| $28.24B (+26%) \| $0.33 (컨센 $0.53 하회) · 영업흑자 마진 4% \| TTM +$5.8B | legacy_unverified | text | SRC-v15-html |  | 최근 분기 실적 원문(③⑨ 참고). TTM 대체 금지 |
| revenue_ttm | $103.6B | verified | derived | SRC-SEC-FACTS-F6 | 2025-07-01~2026-06-30 103,619,000,000 | F6-REG-28. G1-FILL-27 기준값 |
| revenue_ttm_prior | $92.7B | verified | derived | SRC-SEC-FACTS-F6 | 2024-07-01~2025-06-30 92,720,000,000 | F6-REG-28. F6-SPEC-18 수집기 |
| runway_years | — | not_applicable | derived | SRC-v15-html | ∞ | TTM FCF 흑자라 런웨이 산식 적용 대상 아님(원문 ∞) |
| ttm_per | 370.5 | legacy_unverified | actual | SRC-v15-html | 370.5 |  |

### Oracle

| 지표 | 값 | 상태 | 종류 | 출처 | 원문 | 비고 |
| --- | --- | --- | --- | --- | --- | --- |
| capex_ttm | $55.7B | legacy_unverified | actual | SRC-v15-html | $55.7B |  |
| cash | $31.3B | verified | actual | SRC-SEC-FACTS-F6 | 현금및현금성자산 31.3B (버퍼 31.9B 는 basis 에 보존) | CASH-FCF-35. **순수 현금으로 등록한다** — 설계 지침 6.4. 유동성 버퍼와 총계는 basis.preserved_wider_def |
| cash | $31.9B | legacy_unverified | actual | SRC-v15-html | $31.9B | [CASH-FCF-35 대체됨 → oracle.cash.cashfcf35]  |
| contracted_revenue | $638.0B | legacy_unverified | actual | SRC-v15-rule | RPO $638B | 규칙 v1.5 ⑨ 게이트 4 적용표 |
| credit_rating | BBB- ⚠️ | legacy_unverified | text | SRC-v15-html | BBB- ⚠️ | 별표 J 교차검증 전용 — 점수 입력 아님 |
| debt_ebitda | 5.0 | legacy_unverified | actual | SRC-v15-html | 5.03 ⚠️ |  |
| fcf_ttm | -$23.7B | verified | derived | SRC-SEC-FACTS-F6 | TTM FCF -23.7B = OCF 32.0B - CapEx 55.7B | CASH-FCF-35. SEC 실측. OCF·CapEx 구성요소를 basis 에 남겼다 |
| fcf_ttm | -$23.7B | legacy_unverified | actual | SRC-v15-html | -$23.7B | [CASH-FCF-35 대체됨 → oracle.fcf_ttm.cashfcf35]  |
| market_cap | $443.7B | legacy_unverified | actual | SRC-v15-html | $443.7B |  |
| net_borrowing_ttm | $40.2B | legacy_unverified | actual | SRC-v15-html | +$40.2B | 차환 제외 순증 |
| net_cash | -$135.5B | verified | derived | SRC-SEC-FACTS-F6 | 현금+증권 31.9B − 차입 129.5B − 리스 37.9B = -135.5B | NETCASH-37. SEC 보존 원자료 실측. **정의는 legacy 역산 작업 정의다** |
| net_cash | -$135.5B | legacy_unverified | actual | SRC-v15-html | -$135.5B | [NETCASH-37 대체됨 → oracle.net_cash.nc37]  |
| net_income_ttm | $17.1B | verified | actual | SRC-SEC-FACTS-F6 | 2025-06-01~2026-05-31 17,087,000,000 | F6-REG-28. F6-SPEC-18 수집기 |
| nonop_share | -15% | legacy_unverified | actual | SRC-v15-html | -15% ᶜ |  |
| ntm_per | 19.1 | legacy_unverified | estimate | SRC-v15-html | 19.1 |  |
| offbalance_B | $250.0B | legacy_unverified | actual | SRC-v15-rule | 리스 $250B(15~20년) | 규칙 v1.5 ⑨ 게이트 4 적용표 |
| offbalance_note | 리스 $250B(15~20년) | legacy_unverified | text | SRC-v15-html | 리스 $250B(15~20년) | 부외 약정 원문(A/B/C 분류 전) |
| operating_income_ttm | $20.6B | verified | actual | SRC-SEC-FACTS-F6 | 2025-06-01~2026-05-31 20,606,000,000 | F6-REG-28. G1-FILL-27 기준값 |
| price | 154.04 | legacy_unverified | actual | SRC-v15-html | $154.04 |  |
| ps_ratio | 6.6 | legacy_unverified | actual | SRC-v15-html | 6.6 |  |
| quarter_note | Q4 FY26 (3~5월) \| $19.2B (+21%) · OCI $5.8B (+93%) \| 영업마진 33.2% \| TTM -$23.7B · 현금 $31.9B · 런웨이 1.3년 | legacy_unverified | text | SRC-v15-html |  | 최근 분기 실적 원문(③⑨ 참고). TTM 대체 금지 |
| revenue_ttm | $67.4B | verified | actual | SRC-SEC-FACTS-F6 | 2025-06-01~2026-05-31 67,357,000,000 | F6-REG-28. G1-FILL-27 기준값 |
| revenue_ttm_prior | $57.4B | verified | actual | SRC-SEC-FACTS-F6 | 2024-06-01~2025-05-31 57,399,000,000 | F6-REG-28. F6-SPEC-18 수집기 |
| runway_years | 1.3 | legacy_unverified | derived | SRC-v15-html | 1.3년 ⚠️ | 원본 계산값(현금 ÷ 연 소진) |
| ttm_per | 26.4 | legacy_unverified | actual | SRC-v15-html | 26.4 |  |

### OpenAI

| 지표 | 값 | 상태 | 종류 | 출처 | 원문 | 비고 |
| --- | --- | --- | --- | --- | --- | --- |
| arr | $40.0B | legacy_unverified | run_rate | SRC-v15-rule | 런레이트 $40B+(8/20) | 규칙 v1.5 ⑥ 비상장 절 |
| arr_prior | $25.0B | legacy_unverified | run_rate | SRC-v15-md | ARR $25B → $40B (2~4월 정체 구간) | PRIV-IMPL-31 / C-12. P3 입력. arr 시점 표기가 원문 안에서 갈리나 금액은 같아 점수 영향 없음 |
| cash | — | not_disclosed | actual | SRC-v15-md | 미공시 | PRIV-IMPL-31 / C-20. 승계 관측 openai.cash.v15 의 결측 유형을 등록한다. **값은 그대로 없다** — 라벨만 붙인 |
| cash | — | not_disclosed | actual | SRC-v15-html | 미공시 | [PRIV-IMPL-31 대체됨 → openai.cash.priv31]  |
| contracted_revenue | $40.0B | incompatible_basis | actual | SRC-v15-rule | ARR $40B — 계약 수입 아님(C-07) | 규칙 v1.5 ⑨ 게이트 4 적용표 |
| credit_rating | 비상장 | legacy_unverified | text | SRC-v15-html | 비상장 | 별표 J 교차검증 전용 — 점수 입력 아님 |
| cumulative_raised | $185.0B | legacy_unverified | actual | SRC-v15-rule | 약 $180~190B(중간값) | 규칙 v1.5 ⑥ 비상장 절 |
| debt_ebitda | — | not_disclosed | actual | SRC-v15-md | — | PRIV-IMPL-31 / C-20. 승계 관측 openai.debt_ebitda.v15 의 결측 유형을 등록한다. **값은 그대로 없다** — |
| debt_ebitda | — | not_disclosed | actual | SRC-v15-html | — | [PRIV-IMPL-31 대체됨 → openai.debt_ebitda.priv31]  |
| fcf_ttm | — | not_disclosed | actual | SRC-v15-md | 미공시 | PRIV-IMPL-31 / C-20. 승계 관측 openai.fcf_ttm.v15 의 결측 유형을 등록한다. **값은 그대로 없다** — 라벨만 |
| fcf_ttm | — | not_disclosed | actual | SRC-v15-html | 미공시 | [PRIV-IMPL-31 대체됨 → openai.fcf_ttm.priv31] 비상장 FCF 미공시 |
| net_cash | — | not_disclosed | actual | SRC-v15-md | — | PRIV-IMPL-31 / C-20. 승계 관측 openai.net_cash.v15 의 결측 유형을 등록한다. **값은 그대로 없다** — 라벨 |
| net_cash | — | not_disclosed | actual | SRC-v15-html | — | [PRIV-IMPL-31 대체됨 → openai.net_cash.priv31]  |
| offbalance_B | $338.0B | incompatible_basis | actual | SRC-v15-rule | 컴퓨트 약정 $338B+(연 ~$60B) (C-07) | 규칙 v1.5 ⑨ 게이트 4 적용표 |
| offbalance_note | 컴퓨트 $338B+ | legacy_unverified | text | SRC-v15-html | 컴퓨트 $338B+ | 부외 약정 원문(A/B/C 분류 전) |
| operating_margin_ttm | — | not_disclosed | derived | SRC-v15-md | 미공시 — 비상장이라 TTM 영업손익 공시 의무 없음 | PRIV-IMPL-31 / C-20. G1 판정 보류의 근거 라벨. 통과도 실패도 아니다 |
| post_money_valuation | $852.0B | legacy_unverified | actual | SRC-v15-rule | $852B | 규칙 v1.5 ⑥ 비상장 절 |
| ps_ratio | 39.0 | legacy_unverified | estimate | SRC-v15-md | TTM 보정 약 39배 (밸류 $852B) | PRIV-IMPL-31 / C-12. P2 분모는 TTM 보정 매출 |
| quarter_note | — \| 런레이트 $40B+ (8/20) \| 2026 GAAP 손실 ~$60B 전망 \| BEP 2030 | legacy_unverified | text | SRC-v15-html |  | 최근 분기 실적 원문(③⑨ 참고). TTM 대체 금지 |
| runway_years | — | not_disclosed | derived | SRC-v15-html | 판정 불가 | FCF 미공시로 소진율을 만들 수 없음(원문 판정 불가) |

## 판단 입력

### Alphabet / Google

| Factor | 종류 | 점수 | 입력 | 상태 | 검토 | 비고 |
| --- | --- | --- | --- | --- | --- | --- |
| ① 네트워크 | score | 5 | — | carried | legacy:v1.5 2026-09-02 |  |
| ② 게임체인저 | score | 4 | — | carried | legacy:v1.5 2026-09-02 | C-03: 경로 매핑 미확정 — 승계 점수 |
| ③ Last Mover | criteria | — | imitation=fail, revenue_model=pass, acceleration=partial, door_closed=fail | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 ③ 판정표 |
| ④ 호황 이후 | score | 5 | — | carried | legacy:v1.5 2026-09-02 |  |
| ⑤ 아군 | grade | — | A=2, H=-1 | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 별표 G 판정표 |
| ⑦ 순환금융 | matrix | — | funding_dependent_share=small, own_money_returns=yes | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 별표 I 판정표 |
| ⑧ 비대칭 의존 | score | -1 | — | carried | legacy:v1.5 2026-09-02 |  |
| ⑨ 적자 깊이 | gate_inputs | — | fcf_trend=deteriorating, bep_retreat=no, buffer_erosion=no, direction_A=unknown, direction_B=unknown, coverage_comparable=unknown, operating_result_reviewed=profit | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 ⑨ 적용표(추세·BEP·커버리지 비교 가능성) |

### Amazon / AWS

| Factor | 종류 | 점수 | 입력 | 상태 | 검토 | 비고 |
| --- | --- | --- | --- | --- | --- | --- |
| ① 네트워크 | score | 5 | — | carried | legacy:v1.5 2026-09-02 |  |
| ② 게임체인저 | score | 4 | — | carried | legacy:v1.5 2026-09-02 | C-03: 경로 매핑 미확정 — 승계 점수 |
| ③ Last Mover | criteria | — | imitation=fail, revenue_model=pass, acceleration=pass, door_closed=fail | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 ③ 판정표 |
| ④ 호황 이후 | score | 5 | — | carried | legacy:v1.5 2026-09-02 |  |
| ⑤ 아군 | grade | — | A=2, H=-1 | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 별표 G 판정표 |
| ⑦ 순환금융 | matrix | — | funding_dependent_share=small, own_money_returns=yes | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 별표 I 판정표 |
| ⑧ 비대칭 의존 | score | -1 | — | carried | legacy:v1.5 2026-09-02 |  |
| ⑨ 적자 깊이 | gate_inputs | — | fcf_trend=unknown, bep_retreat=no, buffer_erosion=no, direction_A=unknown, direction_B=unknown, coverage_comparable=yes, operating_result_reviewed=profit | new | 설계진행 2026-09-11 | 규칙 v1.5 ⑨ 적용표(추세·BEP·커버리지 비교 가능성) |

### Meta

| Factor | 종류 | 점수 | 입력 | 상태 | 검토 | 비고 |
| --- | --- | --- | --- | --- | --- | --- |
| ① 네트워크 | score | 5 | — | carried | legacy:v1.5 2026-09-02 |  |
| ② 게임체인저 | score | 4 | — | carried | legacy:v1.5 2026-09-02 | C-03: 경로 매핑 미확정 — 승계 점수 |
| ③ Last Mover | criteria | — | imitation=partial, revenue_model=pass, acceleration=partial, door_closed=fail | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 ③ 판정표 |
| ④ 호황 이후 | score | 3 | — | carried | legacy:v1.5 2026-09-02 |  |
| ⑤ 아군 | grade | — | A=1, H=-1 | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 별표 G 판정표 |
| ⑦ 순환금융 | matrix | — | funding_dependent_share=small, own_money_returns=no | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 별표 I 판정표 |
| ⑧ 비대칭 의존 | score | -1 | — | carried | legacy:v1.5 2026-09-02 |  |
| ⑨ 적자 깊이 | gate_inputs | — | fcf_trend=deteriorating, bep_retreat=no, buffer_erosion=no, direction_A=unknown, direction_B=unknown, coverage_comparable=unknown, operating_result_reviewed=profit | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 ⑨ 적용표(추세·BEP·커버리지 비교 가능성) |

### Microsoft

| Factor | 종류 | 점수 | 입력 | 상태 | 검토 | 비고 |
| --- | --- | --- | --- | --- | --- | --- |
| ① 네트워크 | score | 5 | — | carried | legacy:v1.5 2026-09-02 |  |
| ② 게임체인저 | score | 3 | — | carried | legacy:v1.5 2026-09-02 | C-03: 경로 매핑 미확정 — 승계 점수 |
| ③ Last Mover | criteria | — | imitation=fail, revenue_model=pass, acceleration=pass, door_closed=fail | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 ③ 판정표 |
| ④ 호황 이후 | score | 4 | — | carried | legacy:v1.5 2026-09-02 |  |
| ⑤ 아군 | grade | — | A=2, H=-1 | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 별표 G 판정표 |
| ⑦ 순환금융 | matrix | — | funding_dependent_share=small, own_money_returns=yes | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 별표 I 판정표 |
| ⑧ 비대칭 의존 | score | -1 | — | carried | legacy:v1.5 2026-09-02 |  |
| ⑨ 적자 깊이 | gate_inputs | — | fcf_trend=stable, bep_retreat=no, buffer_erosion=no, direction_A=unknown, direction_B=unknown, coverage_comparable=unknown, operating_result_reviewed=profit | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 ⑨ 적용표(추세·BEP·커버리지 비교 가능성) |

### TSMC

| Factor | 종류 | 점수 | 입력 | 상태 | 검토 | 비고 |
| --- | --- | --- | --- | --- | --- | --- |
| ① 네트워크 | score | 2 | — | carried | legacy:v1.5 2026-09-02 |  |
| ② 게임체인저 | score | 5 | — | carried | legacy:v1.5 2026-09-02 | C-03: 경로 매핑 미확정 — 승계 점수 |
| ③ Last Mover | criteria | — | imitation=pass, revenue_model=fail, acceleration=pass, door_closed=fail | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 ③ 판정표 |
| ④ 호황 이후 | score | 4 | — | carried | legacy:v1.5 2026-09-02 |  |
| ⑤ 아군 | grade | — | A=2, H=-1 | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 별표 G 판정표 |
| ⑦ 순환금융 | matrix | — | funding_dependent_share=small, own_money_returns=no | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 별표 I 판정표 |
| ⑧ 비대칭 의존 | score | -4 | — | carried | legacy:v1.5 2026-09-02 |  |
| ⑨ 적자 깊이 | gate_inputs | — | fcf_trend=stable, bep_retreat=no, buffer_erosion=no, direction_A=unknown, direction_B=unknown, coverage_comparable=unknown, operating_result_reviewed=profit | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 ⑨ 적용표(추세·BEP·커버리지 비교 가능성) |

### Alibaba

| Factor | 종류 | 점수 | 입력 | 상태 | 검토 | 비고 |
| --- | --- | --- | --- | --- | --- | --- |
| ① 네트워크 | score | 4 | — | carried | legacy:v1.5 2026-09-02 |  |
| ② 게임체인저 | score | 4 | — | carried | legacy:v1.5 2026-09-02 | C-03: 경로 매핑 미확정 — 승계 점수 |
| ③ Last Mover | criteria | — | imitation=partial, revenue_model=pass, acceleration=pass, door_closed=fail | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 ③ 판정표 |
| ④ 호황 이후 | score | 4 | — | carried | legacy:v1.5 2026-09-02 |  |
| ⑤ 아군 | grade | — | A=1, H=-1 | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 별표 G 판정표 |
| ⑦ 순환금융 | matrix | — | funding_dependent_share=small, own_money_returns=no | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 별표 I 판정표 |
| ⑧ 비대칭 의존 | score | -4 | — | carried | legacy:v1.5 2026-09-02 |  |
| ⑨ 적자 깊이 | gate_inputs | — | fcf_trend=unknown, bep_retreat=no, buffer_erosion=no, direction_A=unknown, direction_B=unknown, coverage_comparable=yes, operating_result_reviewed=profit | new | 설계진행 2026-09-11 | 규칙 v1.5 ⑨ 적용표(추세·BEP·커버리지 비교 가능성) |

### Anthropic

| Factor | 종류 | 점수 | 입력 | 상태 | 검토 | 비고 |
| --- | --- | --- | --- | --- | --- | --- |
| ① 네트워크 | score | 4 | — | carried | legacy:v1.5 2026-09-02 |  |
| ② 게임체인저 | score | 5 | — | carried | legacy:v1.5 2026-09-02 | C-03: 경로 매핑 미확정 — 승계 점수 |
| ③ Last Mover | criteria | — | imitation=partial, revenue_model=pass, acceleration=fail, door_closed=fail | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 ③ 판정표 |
| ④ 호황 이후 | score | 4 | — | carried | legacy:v1.5 2026-09-02 |  |
| ⑤ 아군 | grade | — | A=2, H=0 | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 별표 G 판정표 |
| ⑥ 가격 | score | -3 | private=True | carried | legacy:v1.5 2026-09-02 | C-12: 비상장 정성 예외(TTM 보정·자본효율 근거는 원문) |
| ⑦ 순환금융 | score | -1 | — | carried | legacy:v1.5 2026-09-02 | C-09: 매트릭스 입력(환류 여부) 원문 없음 — 승계 점수 |
| ⑧ 비대칭 의존 | score | -3 | — | new | worker(HANSOLJJ) — C-13 F8-ANTH-33 8ddb0ae 기반 2026-09-11 | F8-ANTH-33 반영(2026-09-11). **점수 -3 은 바뀌지 않았고 근거란만 바뀌었다.** 2차 증언(증권사 자료)을 1차 공시(A |
| ⑨ 적자 깊이 | gate_inputs | — | fcf_trend=unknown, bep_retreat=no, buffer_erosion=no, direction_A=unknown, direction_B=unknown, coverage_comparable=no, operating_result_reviewed=unknown, fcf_not_disclosed_reason=anthropic.fcf_not_disclosed | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 ⑨ 적용표(추세·BEP·커버리지 비교 가능성) |

### Apple

| Factor | 종류 | 점수 | 입력 | 상태 | 검토 | 비고 |
| --- | --- | --- | --- | --- | --- | --- |
| ① 네트워크 | score | 5 | — | carried | legacy:v1.5 2026-09-02 |  |
| ② 게임체인저 | score | 2 | — | carried | legacy:v1.5 2026-09-02 | C-03: 경로 매핑 미확정 — 승계 점수 |
| ③ Last Mover | criteria | — | imitation=fail, revenue_model=pass, acceleration=fail, door_closed=fail | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 ③ 판정표 |
| ④ 호황 이후 | score | 3 | — | carried | legacy:v1.5 2026-09-02 |  |
| ⑤ 아군 | grade | — | A=1, H=-1 | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 별표 G 판정표 |
| ⑦ 순환금융 | matrix | — | funding_dependent_share=small, own_money_returns=no | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 별표 I 판정표 |
| ⑧ 비대칭 의존 | score | -3 | — | carried | legacy:v1.5 2026-09-02 |  |
| ⑨ 적자 깊이 | gate_inputs | — | fcf_trend=stable, bep_retreat=no, buffer_erosion=no, direction_A=unknown, direction_B=unknown, coverage_comparable=unknown, operating_result_reviewed=profit | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 ⑨ 적용표(추세·BEP·커버리지 비교 가능성) |

### NVIDIA

| Factor | 종류 | 점수 | 입력 | 상태 | 검토 | 비고 |
| --- | --- | --- | --- | --- | --- | --- |
| ① 네트워크 | score | 2 | — | carried | legacy:v1.5 2026-09-02 |  |
| ② 게임체인저 | score | 5 | — | carried | legacy:v1.5 2026-09-02 | C-03: 경로 매핑 미확정 — 승계 점수 |
| ③ Last Mover | criteria | — | imitation=fail, revenue_model=pass, acceleration=fail, door_closed=fail | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 ③ 판정표 |
| ④ 호황 이후 | score | 5 | — | carried | legacy:v1.5 2026-09-02 |  |
| ⑤ 아군 | grade | — | A=1, H=-2 | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 별표 G 판정표 |
| ⑦ 순환금융 | matrix | — | funding_dependent_share=large, own_money_returns=yes | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 별표 I 판정표 |
| ⑧ 비대칭 의존 | score | -3 | — | carried | legacy:v1.5 2026-09-02 |  |
| ⑨ 적자 깊이 | gate_inputs | — | fcf_trend=stable, bep_retreat=no, buffer_erosion=no, direction_A=unknown, direction_B=unknown, coverage_comparable=unknown, operating_result_reviewed=profit | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 ⑨ 적용표(추세·BEP·커버리지 비교 가능성) |

### Palantir

| Factor | 종류 | 점수 | 입력 | 상태 | 검토 | 비고 |
| --- | --- | --- | --- | --- | --- | --- |
| ① 네트워크 | score | 2 | — | carried | legacy:v1.5 2026-09-02 |  |
| ② 게임체인저 | score | 3 | — | carried | legacy:v1.5 2026-09-02 | C-03: 경로 매핑 미확정 — 승계 점수 |
| ③ Last Mover | criteria | — | imitation=partial, revenue_model=partial, acceleration=pass, door_closed=fail | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 ③ 판정표 |
| ④ 호황 이후 | score | 3 | — | carried | legacy:v1.5 2026-09-02 |  |
| ⑤ 아군 | grade | — | A=1, H=-2 | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 별표 G 판정표 |
| ⑦ 순환금융 | matrix | — | funding_dependent_share=small, own_money_returns=no | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 별표 I 판정표 |
| ⑧ 비대칭 의존 | score | -3 | — | carried | legacy:v1.5 2026-09-02 |  |
| ⑨ 적자 깊이 | gate_inputs | — | fcf_trend=stable, bep_retreat=no, buffer_erosion=no, direction_A=unknown, direction_B=unknown, coverage_comparable=unknown, operating_result_reviewed=profit | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 ⑨ 적용표(추세·BEP·커버리지 비교 가능성) |

### SpaceX + xAI

| Factor | 종류 | 점수 | 입력 | 상태 | 검토 | 비고 |
| --- | --- | --- | --- | --- | --- | --- |
| ① 네트워크 | score | 3 | — | carried | legacy:v1.5 2026-09-02 |  |
| ② 게임체인저 | score | 4 | — | carried | legacy:v1.5 2026-09-02 | C-03: 경로 매핑 미확정 — 승계 점수 |
| ③ Last Mover | criteria | — | imitation=partial, revenue_model=pass, acceleration=pass, door_closed=fail | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 ③ 판정표 |
| ④ 호황 이후 | score | 5 | — | carried | legacy:v1.5 2026-09-02 |  |
| ⑤ 아군 | grade | — | A=1, H=-1 | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 별표 G 판정표 |
| ⑦ 순환금융 | matrix | — | funding_dependent_share=small, own_money_returns=no | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 별표 I 판정표 |
| ⑧ 비대칭 의존 | score | -3 | — | carried | legacy:v1.5 2026-09-02 |  |
| ⑨ 적자 깊이 | gate_inputs | — | fcf_trend=unknown, bep_retreat=no, buffer_erosion=no, direction_A=unknown, direction_B=unknown, coverage_comparable=yes, operating_result_reviewed=loss | new | 설계진행 2026-09-11 | 규칙 v1.5 ⑨ 적용표(추세·BEP·커버리지 비교 가능성) |

### Tesla

| Factor | 종류 | 점수 | 입력 | 상태 | 검토 | 비고 |
| --- | --- | --- | --- | --- | --- | --- |
| ① 네트워크 | score | 2 | — | carried | legacy:v1.5 2026-09-02 |  |
| ② 게임체인저 | score | 3 | — | carried | legacy:v1.5 2026-09-02 | C-03: 경로 매핑 미확정 — 승계 점수 |
| ③ Last Mover | criteria | — | imitation=fail, revenue_model=pass, acceleration=pass, door_closed=fail | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 ③ 판정표 |
| ④ 호황 이후 | score | 4 | — | carried | legacy:v1.5 2026-09-02 |  |
| ⑤ 아군 | grade | — | A=0, H=-1 | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 별표 G 판정표 |
| ⑦ 순환금융 | matrix | — | funding_dependent_share=small, own_money_returns=yes | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 별표 I 판정표 |
| ⑧ 비대칭 의존 | score | -2 | — | carried | legacy:v1.5 2026-09-02 |  |
| ⑨ 적자 깊이 | gate_inputs | — | fcf_trend=deteriorating, bep_retreat=no, buffer_erosion=no, direction_A=unknown, direction_B=unknown, coverage_comparable=unknown, operating_result_reviewed=profit | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 ⑨ 적용표(추세·BEP·커버리지 비교 가능성) |

### Oracle

| Factor | 종류 | 점수 | 입력 | 상태 | 검토 | 비고 |
| --- | --- | --- | --- | --- | --- | --- |
| ① 네트워크 | score | 3 | — | carried | legacy:v1.5 2026-09-02 |  |
| ② 게임체인저 | score | 2 | — | carried | legacy:v1.5 2026-09-02 | C-03: 경로 매핑 미확정 — 승계 점수 |
| ③ Last Mover | criteria | — | imitation=fail, revenue_model=pass, acceleration=pass, door_closed=fail | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 ③ 판정표 |
| ④ 호황 이후 | score | 3 | — | carried | legacy:v1.5 2026-09-02 |  |
| ⑤ 아군 | grade | — | A=1, H=-1 | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 별표 G 판정표 |
| ⑦ 순환금융 | matrix | — | funding_dependent_share=large, own_money_returns=yes | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 별표 I 판정표 |
| ⑧ 비대칭 의존 | score | -4 | — | carried | legacy:v1.5 2026-09-02 |  |
| ⑨ 적자 깊이 | gate_inputs | — | fcf_trend=unknown, bep_retreat=no, buffer_erosion=no, direction_A=unknown, direction_B=unknown, coverage_comparable=yes, operating_result_reviewed=profit | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 ⑨ 적용표(추세·BEP·커버리지 비교 가능성) |

### OpenAI

| Factor | 종류 | 점수 | 입력 | 상태 | 검토 | 비고 |
| --- | --- | --- | --- | --- | --- | --- |
| ① 네트워크 | score | 4 | — | carried | legacy:v1.5 2026-09-02 |  |
| ② 게임체인저 | score | 4 | — | carried | legacy:v1.5 2026-09-02 | C-03: 경로 매핑 미확정 — 승계 점수 |
| ③ Last Mover | criteria | — | imitation=fail, revenue_model=fail, acceleration=pass, door_closed=fail | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 ③ 판정표 |
| ④ 호황 이후 | score | 4 | — | carried | legacy:v1.5 2026-09-02 |  |
| ⑤ 아군 | grade | — | A=2, H=-3 | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 별표 G 판정표 |
| ⑥ 가격 | score | -4 | private=True | carried | legacy:v1.5 2026-09-02 | C-12: 비상장 정성 예외(TTM 보정·자본효율 근거는 원문) |
| ⑦ 순환금융 | score | -1 | — | carried | legacy:v1.5 2026-09-02 | C-09: 매트릭스 입력(환류 여부) 원문 없음 — 승계 점수 |
| ⑧ 비대칭 의존 | score | -4 | — | carried | legacy:v1.5 2026-09-02 |  |
| ⑨ 적자 깊이 | gate_inputs | — | fcf_trend=unknown, bep_retreat=yes, buffer_erosion=no, direction_A=unknown, direction_B=unknown, coverage_comparable=no, operating_result_reviewed=loss, fcf_not_disclosed_reason=openai.fcf_not_disclosed | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 ⑨ 적용표(추세·BEP·커버리지 비교 가능성) |

## 출처

| ID | 제목 | 발행 | URL | 접근일 | 이해상충 |
| --- | --- | --- | --- | --- | --- |
| SRC-v15-html | AI기업_채점표_v1.5.html (D·VAL·EARN·FIN·BORR·TRIG) | 내부 기준선 | (URL 없음 — 만들지 않음) | 2026-09-11 | 작성자 Claude=Anthropic (긴장 #4·#11) |
| SRC-v15-md | AI기업_채점표_v1.5.md (순위표·원자료) | 내부 기준선 | (URL 없음 — 만들지 않음) | 2026-09-11 | 작성자 Claude=Anthropic (긴장 #4·#11) |
| SRC-v15-rule | AI기업_채점규칙_v1.5.md (③ 사다리·별표 G·별표 I·⑨ 적용표·⑥ 비상장) | 내부 규칙 | (URL 없음 — 만들지 않음) | 2026-09-11 | — |
| SRC-SEC-SPCX-10Q-2026Q2 | SpaceX/xAI Form 10-Q (2026-06-30) — Note 3 Revenue · Note 16 Commitments | SEC EDGAR | https://www.sec.gov/Archives/edgar/data/1181412/000162828026052535/spcx-20260630.htm | 2026-09-11 | — |
| SRC-SEC-SPCX-S1A-2026 | SpaceX/xAI Form S-1/A (2026-06-03) — Note 11 Leases (F-36) | SEC EDGAR | https://www.sec.gov/Archives/edgar/data/1181412/000162828026040364/ | 2026-09-11 | — |
| SRC-SEC-AMZN-10Q-2026Q2 | Amazon Form 10-Q (2026-06-30) — Note 1 Accounting Policies · Commitments 표 | SEC EDGAR | https://www.sec.gov/Archives/edgar/data/1018724/000101872426000026/amzn-20260630.htm | 2026-09-11 | — |
| SRC-SEC-BABA-20F-FY2026 | Alibaba Form 20-F (FY2026, 2026-03-31) — Note 2(g) · Note 27 · Exchange Rate Information | SEC EDGAR | https://www.sec.gov/Archives/edgar/data/1577552/000119312526231755/baba-20260331.htm | 2026-09-11 | — |
| SRC-SEC-BABA-FACTS | SEC XBRL companyfacts CIK0001577552 (Alibaba) — us-gaap Revenues · OperatingIncomeLoss | SEC EDGAR | https://data.sec.gov/api/xbrl/companyfacts/CIK0001577552.json | 2026-09-11 | — |
| SRC-SEC-FACTS-F6 | SEC XBRL companyfacts 12개사 (F6 TTM 입력 재구성) | SEC EDGAR | https://data.sec.gov/api/xbrl/companyfacts/ | 2026-09-10 | — |
| SRC-SEC-TSM-20F-FY2025 | TSMC Form 20-F (FY2025, 2025-12-31) — 연결손익계산서 F-6 · 환율 Note 3 (F-13) | SEC EDGAR | https://www.sec.gov/Archives/edgar/data/1046179/000162828026025362/tsm-20251231.htm | 2026-09-11 | — |

## 미결 항목

| 기업 | 항목 | 상태 | 내용 |
| --- | --- | --- | --- |
| spacex-xai | ttm_per | not_disclosed | 적자 |
| spacex-xai | nonop_share | not_disclosed | 적자 |
| apple | runway_years | not_applicable | TTM FCF 흑자라 런웨이 산식 적용 대상 아님(원문 ∞) |
| nvidia | runway_years | not_applicable | TTM FCF 흑자라 런웨이 산식 적용 대상 아님(원문 ∞) |
| microsoft | runway_years | not_applicable | TTM FCF 흑자라 런웨이 산식 적용 대상 아님(원문 ∞) |
| alphabet | runway_years | not_applicable | TTM FCF 흑자라 런웨이 산식 적용 대상 아님(원문 ∞) |
| meta | runway_years | not_applicable | TTM FCF 흑자라 런웨이 산식 적용 대상 아님(원문 ∞) |
| tsmc | runway_years | not_applicable | TTM FCF 흑자라 런웨이 산식 적용 대상 아님(원문 ∞) |
| tesla | runway_years | not_applicable | TTM FCF 흑자라 런웨이 산식 적용 대상 아님(원문 ∞) |
| palantir | runway_years | not_applicable | TTM FCF 흑자라 런웨이 산식 적용 대상 아님(원문 ∞) |
| anthropic | cash | not_disclosed | [PRIV-IMPL-31 대체됨 → anthropic.cash.priv31]  |
| anthropic | fcf_ttm | not_disclosed | [PRIV-IMPL-31 대체됨 → anthropic.fcf_ttm.priv31] 비상장 FCF 미공시 |
| anthropic | runway_years | not_disclosed | FCF 미공시로 소진율을 만들 수 없음(원문 판정 불가) |
| anthropic | net_cash | not_disclosed | [PRIV-IMPL-31 대체됨 → anthropic.net_cash.priv31]  |
| anthropic | debt_ebitda | not_disclosed | [PRIV-IMPL-31 대체됨 → anthropic.debt_ebitda.priv31]  |
| openai | cash | not_disclosed | [PRIV-IMPL-31 대체됨 → openai.cash.priv31]  |
| openai | fcf_ttm | not_disclosed | [PRIV-IMPL-31 대체됨 → openai.fcf_ttm.priv31] 비상장 FCF 미공시 |
| openai | runway_years | not_disclosed | FCF 미공시로 소진율을 만들 수 없음(원문 판정 불가) |
| openai | net_cash | not_disclosed | [PRIV-IMPL-31 대체됨 → openai.net_cash.priv31]  |
| openai | debt_ebitda | not_disclosed | [PRIV-IMPL-31 대체됨 → openai.debt_ebitda.priv31]  |
| palantir | net_borrowing_ttm | not_disclosed | 차환 제외 순증 |
| amazon | contracted_revenue | parse_failed | [OBS-REG-25 대체됨 → amazon.contracted_revenue.obsreg25] 규칙 v1.5 ⑨ 게이트 4 적용표 |
| alibaba | offbalance_B | not_disclosed | [OBS-REG-25 대체됨 → alibaba.offbalance_B.obsreg25] 규칙 v1.5 ⑨ 게이트 4 적용표 |
| alibaba | contracted_revenue | not_disclosed | [OBS-REG-25 대체됨 → alibaba.contracted_revenue.obsreg25] 규칙 v1.5 ⑨ 게이트 4 적용표 |
| spacex-xai | offbalance_B | not_disclosed | [OBS-REG-25 대체됨 → spacex-xai.offbalance_B.obsreg25] 규칙 v1.5 ⑨ 게이트 4 적용표 |
| anthropic | offbalance_B | incompatible_basis | 규칙 v1.5 ⑨ 게이트 4 적용표 |
| anthropic | contracted_revenue | incompatible_basis | 규칙 v1.5 ⑨ 게이트 4 적용표 |
| openai | offbalance_B | incompatible_basis | 규칙 v1.5 ⑨ 게이트 4 적용표 |
| openai | contracted_revenue | incompatible_basis | 규칙 v1.5 ⑨ 게이트 4 적용표 |
| alibaba | contracted_revenue | not_disclosed | OBS-REG-25. **회사가 공시하지 않겠다고 선언한 회계정책이다.** '이 문서에 없다' 와 다르다 — 찾아도 없을 것이 선언돼 있다. C-16 의 유일한 대상이다 |
| anthropic | fcf_ttm | not_disclosed | PRIV-IMPL-31 / C-20. 승계 관측 anthropic.fcf_ttm.v15 의 결측 유형을 등록한다. **값은 그대로 없다** — 라벨만 붙인다 |
| anthropic | cash | not_disclosed | PRIV-IMPL-31 / C-20. 승계 관측 anthropic.cash.v15 의 결측 유형을 등록한다. **값은 그대로 없다** — 라벨만 붙인다 |
| anthropic | net_cash | not_disclosed | PRIV-IMPL-31 / C-20. 승계 관측 anthropic.net_cash.v15 의 결측 유형을 등록한다. **값은 그대로 없다** — 라벨만 붙인다 |
| anthropic | debt_ebitda | not_disclosed | PRIV-IMPL-31 / C-20. 승계 관측 anthropic.debt_ebitda.v15 의 결측 유형을 등록한다. **값은 그대로 없다** — 라벨만 붙인다 |
| anthropic | operating_margin_ttm | not_disclosed | PRIV-IMPL-31 / C-20. G1 판정 보류의 근거 라벨. 통과도 실패도 아니다 |
| openai | fcf_ttm | not_disclosed | PRIV-IMPL-31 / C-20. 승계 관측 openai.fcf_ttm.v15 의 결측 유형을 등록한다. **값은 그대로 없다** — 라벨만 붙인다 |
| openai | cash | not_disclosed | PRIV-IMPL-31 / C-20. 승계 관측 openai.cash.v15 의 결측 유형을 등록한다. **값은 그대로 없다** — 라벨만 붙인다 |
| openai | net_cash | not_disclosed | PRIV-IMPL-31 / C-20. 승계 관측 openai.net_cash.v15 의 결측 유형을 등록한다. **값은 그대로 없다** — 라벨만 붙인다 |
| openai | debt_ebitda | not_disclosed | PRIV-IMPL-31 / C-20. 승계 관측 openai.debt_ebitda.v15 의 결측 유형을 등록한다. **값은 그대로 없다** — 라벨만 붙인다 |
| openai | operating_margin_ttm | not_disclosed | PRIV-IMPL-31 / C-20. G1 판정 보류의 근거 라벨. 통과도 실패도 아니다 |
| alphabet | ⑨ 적자 깊이 | unknown 입력 | direction_A, direction_B, coverage_comparable |
| amazon | ⑨ 적자 깊이 | unknown 입력 | fcf_trend, direction_A, direction_B |
| meta | ⑨ 적자 깊이 | unknown 입력 | direction_A, direction_B, coverage_comparable |
| microsoft | ⑨ 적자 깊이 | unknown 입력 | direction_A, direction_B, coverage_comparable |
| tsmc | ⑨ 적자 깊이 | unknown 입력 | direction_A, direction_B, coverage_comparable |
| alibaba | ⑨ 적자 깊이 | unknown 입력 | fcf_trend, direction_A, direction_B |
| anthropic | ⑨ 적자 깊이 | unknown 입력 | fcf_trend, direction_A, direction_B, operating_result_reviewed |
| apple | ⑨ 적자 깊이 | unknown 입력 | direction_A, direction_B, coverage_comparable |
| nvidia | ⑨ 적자 깊이 | unknown 입력 | direction_A, direction_B, coverage_comparable |
| palantir | ⑨ 적자 깊이 | unknown 입력 | direction_A, direction_B, coverage_comparable |
| spacex-xai | ⑨ 적자 깊이 | unknown 입력 | fcf_trend, direction_A, direction_B |
| tesla | ⑨ 적자 깊이 | unknown 입력 | direction_A, direction_B, coverage_comparable |
| oracle | ⑨ 적자 깊이 | unknown 입력 | fcf_trend, direction_A, direction_B |
| openai | ⑨ 적자 깊이 | unknown 입력 | fcf_trend, direction_A, direction_B |

- legacy_unverified 관측 203건은 기준선 열람용이며 이번 실행에서 재검증되지 않았다.
- 미결 규칙 결정: C-03, C-05, C-06, C-13, C-16 (실행 선택: C-05=apply, C-06=proposed_v15_boundaries, C-16=downgrade, C-12=p2_with_capped_promotion, C-20=defer_to_private_g2)
