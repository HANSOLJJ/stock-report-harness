---
slug: ai-scorecard-2026-10-test
report_type: ai_scorecard
plan_source: output/ai-scorecard-2026-10-test/plan.md
run_id: ai-scorecard-2026-10-test
as_of: 2026-10-01
rule_version: v1.8
observations_hash: 979b7e527f73e9eddf310e13f6968fcf6043b29be94fca84d7340cfd570faa31
judgments_hash: 103a5ca22afbe70f72f3e5f7fb5ef9f75e0be54481cbb861a0a8321908dd4468
evidence_hash: e320bcedde518f00076b1eb2483cb64b0c945eec47eb45f4849e59554cf5bbf6
triggers_hash: 84da4998e571df56ea2346480513cc27d0fb78244fcaac7ffbb3943d7a219f6f
created_at: 2026-10-01
---
# 리서치 — v1.8 근거 계층 시험 실행

실행 `ai-scorecard-2026-10-test` 의 원자료·판단 입력·출처를 정리한다. 관측 387건, 판단 114건.

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
| market_cap | $4.21T | verified | actual | SRC-YF-2026-09-30 |  |  |
| market_cap | $4.12T | legacy_unverified | actual | SRC-v15-md | $4.12T |  |
| net_borrowing_ttm | $70.1B | legacy_unverified | actual | SRC-v15-html | +$70.1B | 차환 제외 순증 |
| net_cash | $121.7B | verified | derived | SRC-SEC-FACTS-F6 | 현금+시장성증권 242.5B − 차입 100.2B − 리스 20.6B = 121.7B | NETCASH-37. SEC 보존 원자료 실측. **유가증권은 시장성 있는 것만** |
| net_cash | $121.7B | legacy_unverified | actual | SRC-v15-html | +$121.7B | [NETCASH-37 대체됨 → alphabet.net_cash.nc37]  |
| net_income_ttm | $244.2B | verified | derived | SRC-SEC-FACTS-F6 | 2025-07-01~2026-06-30 244,205,000,000 | F6-REG-28. F6-SPEC-18 수집기 |
| nonop_share | 51% | legacy_unverified | actual | SRC-v15-html | 51% ⚠️ |  |
| ntm_per | 25.3 | legacy_unverified | estimate | SRC-v15-md | 25.3 |  |
| offbalance_note | 총 약정 $707B | legacy_unverified | text | SRC-v15-html | 총 약정 $707B | 부외 약정 원문(A/B/C 분류 전) |
| operating_income_ttm | $147.6B | verified | derived | SRC-SEC-FACTS-F6 | 2025-07-01~2026-06-30 147,628,000,000 | F6-REG-28. G1-FILL-27 기준값 |
| pretax_income_ttm | $299.3B | verified | derived | SRC-SEC-FACTS-F6 | 세전이익 TTM 299.3B USD | NONOP-44. nonop_share 산식 정정 입력 — 저장값이 영업외손익÷세전이익 임이 확인됐다 |
| price | 344.0799865722656 | verified | actual | SRC-YF-2026-09-30 |  |  |
| price | 337.12 | legacy_unverified | actual | SRC-v15-html | $337.12 |  |
| ps_ratio | 9.3 | legacy_unverified | actual | SRC-v15-html | 9.3 |  |
| quarter_note | Q2 (7/22) \| $119.8B (+24%) · GCP $24.8B(+82%) 영업이익 $8.8B \| 조정 $2.85 (컨센 $2.89 하회) \| Q2 사상 첫 마이너스 · TTM +$53B | legacy_unverified | text | SRC-v15-html |  | 최근 분기 실적 원문(③⑨ 참고). TTM 대체 금지 |
| revenue_ttm | $445.9B | verified | derived | SRC-SEC-FACTS-F6 | 2025-07-01~2026-06-30 445,866,000,000 | F6-REG-28. G1-FILL-27 기준값 |
| revenue_ttm_prior | $371.4B | verified | derived | SRC-SEC-FACTS-F6 | 2024-07-01~2025-06-30 371,399,000,000 | F6-REG-28. F6-SPEC-18 수집기 |
| runway_years | — | not_applicable | derived | SRC-v15-html | ∞ | TTM FCF 흑자라 런웨이 산식 적용 대상 아님(원문 ∞) |
| ttm_per | 16.9 | legacy_unverified | actual | SRC-v15-html | 16.9 |  |
| undrawn_credit | — | not_disclosed | actual | SRC-SEC-FACTS-F6 |  | FIX-54 1단계 S2 전수 — 확정 미인출 여신 미확인(우리가 확인하지 않았다). |

### Amazon / AWS

| 지표 | 값 | 상태 | 종류 | 출처 | 원문 | 비고 |
| --- | --- | --- | --- | --- | --- | --- |
| capex_ttm | $173.0B | legacy_unverified | actual | SRC-v15-html | $173.0B |  |
| cash | $78.2B | verified | actual | SRC-SEC-FACTS-F6 | 현금및현금성자산 78.2B (버퍼 123.0B 는 basis 에 보존) | CASH-FCF-35. **순수 현금으로 등록한다** — 설계 지침 6.4. 유동성 버퍼와 총계는 basis.preserved_wider_def |
| cash | $123.0B | legacy_unverified | actual | SRC-v15-html | $123.0B | [CASH-FCF-35 대체됨 → amazon.cash.cashfcf35]  |
| contracted_revenue | $496.0B | verified | actual | SRC-SEC-AMZN-10Q-2026Q2 | those commitments not yet recognized were approximately $496 billion (2026-06-30 | OBS-REG-25. 승계 관측 amazon.contracted_revenue.v15(parse_failed)를 대체한다. **parse_fai |
| contracted_revenue | — | not_disclosed | actual | SRC-v15-rule | AWS 백로그(수백 $B급) — 숫자 미공시 | [OBS-REG-25 대체됨 → amazon.contracted_revenue.obsreg25] 규칙 v1.5 ⑨ 게이트 4 적용표 |
| credit_rating | AA급 | legacy_unverified | text | SRC-v15-html | AA급 | 별표 J 교차검증 전용 — 점수 입력 아님 |
| debt_ebitda | 1.4 | legacy_unverified | actual | SRC-v15-html | 1.35 |  |
| fcf_ttm | -$11.6B | verified | derived | SRC-SEC-FACTS-F6 | TTM FCF -11.6B = OCF 161.4B - CapEx 173.0B | CASH-FCF-35. SEC 실측. OCF·CapEx 구성요소를 basis 에 남겼다 |
| fcf_ttm | -$11.6B | legacy_unverified | actual | SRC-v15-html | -$11.6B | [CASH-FCF-35 대체됨 → amazon.fcf_ttm.cashfcf35]  |
| market_cap | $2.69T | verified | actual | SRC-YF-2026-09-30 |  |  |
| market_cap | $2.75T | legacy_unverified | actual | SRC-v15-md | $2.75T |  |
| net_borrowing_ttm | $75.2B | legacy_unverified | actual | SRC-v15-html | +$75.2B | 차환 제외 순증 |
| net_cash | -$119.3B | verified | derived | SRC-SEC-FACTS-F6 | 현금+시장성증권 123.0B − 차입 132.5B − 리스 109.8B = -119.3B | NETCASH-37. SEC 보존 원자료 실측. **유가증권은 시장성 있는 것만** |
| net_cash | -$128.7B | legacy_unverified | actual | SRC-v15-html | -$128.7B | [NETCASH-37 대체됨 → amazon.net_cash.nc37]  |
| net_income_ttm | $135.3B | verified | derived | SRC-SEC-FACTS-F6 | 2025-07-01~2026-06-30 135,281,000,000 | F6-REG-28. F6-SPEC-18 수집기 |
| nonop_share | 46% | legacy_unverified | actual | SRC-v15-html | 46% ⚠️ |  |
| ntm_per | 27.5 | legacy_unverified | estimate | SRC-v15-md | 27.5 |  |
| offbalance_B | $267.3B | verified | derived | SRC-SEC-AMZN-10Q-2026Q2 | 미개시 리스 $137,214M + 무조건 구매약정 $130,065M = $267,279M (2026-06-30) | OBS-REG-25. 승계 관측 amazon.offbalance_B.v15($106B, 출처 불명)를 대체한다. **106,000 은 2026Q |
| offbalance_B | $106.0B | legacy_unverified | actual | SRC-v15-rule | 미개시 리스 $106B(3/31) | [OBS-REG-25 대체됨 → amazon.offbalance_B.obsreg25] 규칙 v1.5 ⑨ 게이트 4 적용표 |
| offbalance_note | 미개시 리스 $106B | legacy_unverified | text | SRC-v15-html | 미개시 리스 $106B | 부외 약정 원문(A/B/C 분류 전) |
| operating_income_ttm | $93.7B | verified | derived | SRC-SEC-FACTS-F6 | 2025-07-01~2026-06-30 93,712,000,000 | F6-REG-28. G1-FILL-27 기준값 |
| pretax_income_ttm | $175.5B | verified | derived | SRC-SEC-FACTS-F6 | 세전이익 TTM 175.5B USD | NONOP-44. nonop_share 산식 정정 입력 — 저장값이 영업외손익÷세전이익 임이 확인됐다 |
| price | 249.14999389648438 | verified | actual | SRC-YF-2026-09-30 |  |  |
| price | 254.98 | legacy_unverified | actual | SRC-v15-html | $254.98 |  |
| ps_ratio | 3.6 | legacy_unverified | actual | SRC-v15-html | 3.6 |  |
| quarter_note | Q2 (7/30) \| $200.61B (+20%) · AWS $42.2B(+37%) 18분기 최고 \| $5.75 ⚠️ 평가익 포함 \| TTM -$11.6B 실측 확정 | legacy_unverified | text | SRC-v15-html |  | 최근 분기 실적 원문(③⑨ 참고). TTM 대체 금지 |
| revenue_ttm | $775.7B | verified | derived | SRC-SEC-FACTS-F6 | 2025-07-01~2026-06-30 775,680,000,000 | F6-REG-28. G1-FILL-27 기준값 |
| revenue_ttm_prior | $670.0B | verified | derived | SRC-SEC-FACTS-F6 | 2024-07-01~2025-06-30 670,038,000,000 | F6-REG-28. F6-SPEC-18 수집기 |
| runway_years | 10.6 | legacy_unverified | derived | SRC-v15-html | 10.6년 | 원본 계산값(현금 ÷ 연 소진) |
| ttm_per | 20.5 | legacy_unverified | actual | SRC-v15-html | 20.5 |  |
| undrawn_credit | $37.5B | verified | actual | SRC-SEC-AMZN-10Q-2026Q2 | 미인출 약정 US$37.5B (회전 15.0 + 364일 5.0 + 지연인출 17.5, 2026-06-30) | FIX-54 1단계 S2. 점수 불변(런웨이 3년 이상 구간). |

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
| market_cap | $1.85T | verified | actual | SRC-YF-2026-09-30 |  |  |
| market_cap | $1.51T | legacy_unverified | actual | SRC-v15-md | $1.51T |  |
| net_borrowing_ttm | $51.7B | legacy_unverified | actual | SRC-v15-html | +$51.7B | 차환 제외 순증 |
| net_cash | -$22.1B | verified | derived | SRC-SEC-FACTS-F6 | 현금+시장성증권 90.3B − 차입 83.7B − 리스 28.7B = -22.1B | NETCASH-37. SEC 보존 원자료 실측. **유가증권은 시장성 있는 것만** |
| net_cash | -$22.1B | legacy_unverified | actual | SRC-v15-html | -$22.1B | [NETCASH-37 대체됨 → meta.net_cash.nc37]  |
| net_income_ttm | $68.1B | verified | derived | SRC-SEC-FACTS-F6 | 2025-07-01~2026-06-30 68,098,000,000 | F6-REG-28. F6-SPEC-18 수집기 |
| nonop_share | 1% | legacy_unverified | actual | SRC-v15-html | 1% |  |
| ntm_per | 17.9 | legacy_unverified | estimate | SRC-v15-md | 17.9 |  |
| offbalance_note | 리스 $279B + 계약 $349B = $628B | legacy_unverified | text | SRC-v15-html | 리스 $279B + 계약 $349B = $628B | 부외 약정 원문(A/B/C 분류 전) |
| operating_income_ttm | $86.9B | verified | derived | SRC-SEC-FACTS-F6 | 2025-07-01~2026-06-30 86,926,000,000 | F6-REG-28. G1-FILL-27 기준값 |
| pretax_income_ttm | $87.5B | verified | derived | SRC-SEC-FACTS-F6 | 세전이익 TTM 87.5B USD | NONOP-44. nonop_share 산식 정정 입력 — 저장값이 영업외손익÷세전이익 임이 확인됐다 |
| price | 725.1799926757812 | verified | actual | SRC-YF-2026-09-30 |  |  |
| price | 592.85 | legacy_unverified | actual | SRC-v15-html | $592.85 |  |
| ps_ratio | 6.6 | legacy_unverified | actual | SRC-v15-html | 6.6 |  |
| quarter_note | Q2 (7/29) \| $60.80B (+28%) \| $6.18 (컨센 $7.14 하회) \| Q2 +$0.78B (-91%) · TTM +$41B | legacy_unverified | text | SRC-v15-html |  | 최근 분기 실적 원문(③⑨ 참고). TTM 대체 금지 |
| revenue_ttm | $228.2B | verified | derived | SRC-SEC-FACTS-F6 | 2025-07-01~2026-06-30 228,247,000,000 | F6-REG-28. G1-FILL-27 기준값 |
| revenue_ttm_prior | $178.8B | verified | derived | SRC-SEC-FACTS-F6 | 2024-07-01~2025-06-30 178,805,000,000 | F6-REG-28. F6-SPEC-18 수집기 |
| runway_years | — | not_applicable | derived | SRC-v15-html | ∞ | TTM FCF 흑자라 런웨이 산식 적용 대상 아님(원문 ∞) |
| ttm_per | 21.8 | legacy_unverified | actual | SRC-v15-html | 21.8 |  |
| undrawn_credit | — | not_disclosed | actual | SRC-SEC-FACTS-F6 |  | FIX-54 1단계 S2 전수 — 확정 미인출 여신 미확인(우리가 확인하지 않았다). |

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
| market_cap | $3.81T | verified | actual | SRC-YF-2026-09-30 |  |  |
| market_cap | $3.69T | legacy_unverified | actual | SRC-v15-md | $3.69T |  |
| net_borrowing_ttm | -$3.0B | legacy_unverified | actual | SRC-v15-html | -$3.0B | 차환 제외 순증 |
| net_cash | -$52.0B | verified | derived | SRC-SEC-FACTS-F6 | 현금+시장성증권 76.8B − 차입 40.3B − 리스 88.5B = -52.0B | NETCASH-37. SEC 보존 원자료 실측. **유가증권은 시장성 있는 것만** |
| net_cash | -$52.0B | legacy_unverified | actual | SRC-v15-html | -$52.0B | [NETCASH-37 대체됨 → microsoft.net_cash.nc37]  |
| net_income_ttm | $133.7B | verified | actual | SRC-SEC-FACTS-F6 | 2025-07-01~2026-06-30 133,749,000,000 | F6-REG-28. F6-SPEC-18 수집기 |
| nonop_share | 6% | legacy_unverified | actual | SRC-v15-html | 6% |  |
| ntm_per | 25.4 | legacy_unverified | estimate | SRC-v15-md | 25.4 |  |
| offbalance_note | 미분리 (QTS $3.9B만 확인) | legacy_unverified | text | SRC-v15-html | 미분리 (QTS $3.9B만 확인) | 부외 약정 원문(A/B/C 분류 전) |
| operating_income_ttm | $155.2B | verified | actual | SRC-SEC-FACTS-F6 | 2025-07-01~2026-06-30 155,237,000,000 | F6-REG-28. G1-FILL-27 기준값 |
| pretax_income_ttm | $165.9B | verified | derived | SRC-SEC-FACTS-F6 | 세전이익 TTM 165.9B USD | NONOP-44. nonop_share 산식 정정 입력 — 저장값이 영업외손익÷세전이익 임이 확인됐다 |
| price | 512.9000244140625 | verified | actual | SRC-YF-2026-09-30 |  |  |
| price | 496.82 | legacy_unverified | actual | SRC-v15-html | $496.82 |  |
| ps_ratio | 11.1 | legacy_unverified | actual | SRC-v15-html | 11.1 |  |
| quarter_note | Q4 FY26 (7/29) \| $90B (+18%) · 🆕 Azure $29.42B(+42%) 최초 달러 공시 \| non-GAAP $4.74 (컨센 $4.24 상회) \| TTM +$67B · capex 감축 | legacy_unverified | text | SRC-v15-html |  | 최근 분기 실적 원문(③⑨ 참고). TTM 대체 금지 |
| revenue_ttm | $331.8B | verified | actual | SRC-SEC-FACTS-F6 | 2025-07-01~2026-06-30 331,839,000,000 | F6-REG-28. G1-FILL-27 기준값 |
| revenue_ttm_prior | $281.7B | verified | actual | SRC-SEC-FACTS-F6 | 2024-07-01~2025-06-30 281,724,000,000 | F6-REG-28. F6-SPEC-18 수집기 |
| runway_years | — | not_applicable | derived | SRC-v15-html | ∞ | TTM FCF 흑자라 런웨이 산식 적용 대상 아님(원문 ∞) |
| ttm_per | 27.9 | legacy_unverified | actual | SRC-v15-html | 27.9 |  |
| undrawn_credit | — | not_disclosed | actual | SRC-SEC-FACTS-F6 |  | FIX-54 1단계 S2 전수 — 확정 미인출 여신 미확인(우리가 확인하지 않았다). |

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
| market_cap | $2.37T | verified | actual | SRC-YF-2026-09-30 |  |  |
| market_cap | $2.15T | legacy_unverified | actual | SRC-v15-md | $2.15T ✱ |  |
| net_borrowing_ttm | $100M | legacy_unverified | actual | SRC-v15-html | +$0.1B | 차환 제외 순증 |
| net_cash | $69.2B | verified | derived | SRC-SEC-TSM-20F-FY2025 | NT$백만 3,240,002.8 − 1,068,415.7 = 2,171,587.1 ÷ 31.37 = 69.2B USD | NETCASH-37. **보존 20-F 문면 실측** · 유가증권은 시장성 있는 것만 |
| net_cash | $77.0B | legacy_unverified | actual | SRC-v15-html | +$77.0B | [NETCASH-37 대체됨 → tsmc.net_cash.nc37]  |
| net_income_ttm | $54.1B | verified | actual | SRC-SEC-TSM-20F-FY2025 | FY2025 모회사 귀속 순이익 NT$1,697,604.0백만 (연결 1,695,124.9 · 비지배 −2,479.1) | F6-REG-28 / TSM-EDGAR-29. 손익계산서 NET INCOME 행 |
| nonop_share | 7% | legacy_unverified | actual | SRC-v15-html | 7% |  |
| ntm_per | 19.4 | legacy_unverified | estimate | SRC-v15-md | 19.4 ✱ |  |
| offbalance_note | 미확인 | legacy_unverified | text | SRC-v15-html | 미확인 | 부외 약정 원문(A/B/C 분류 전) |
| operating_income_ttm | $61.7B | verified | actual | SRC-SEC-TSM-20F-FY2025 | FY2025 영업이익 NT$1,936,091.7백만 | F6-REG-28 / TSM-EDGAR-29. INCOME FROM OPERATIONS 행. MD&A 반올림 1,936,092 가 아니라 **감 |
| operating_margin_ttm | 51% | verified | derived | SRC-SEC-TSM-20F-FY2025 | FY2025 영업이익률 +50.83% | F6-REG-28 / TSM-EDGAR-29. FY2024 45.68% 에서 +5.15%p |
| pretax_income_ttm | $65.1B | verified | derived | SRC-SEC-TSM-20F-FY2025 | 세전이익 TTM 65.1B USD | NONOP-44. nonop_share 산식 정정 입력 — 저장값이 영업외손익÷세전이익 임이 확인됐다 |
| price | 456.19000244140625 | verified | actual | SRC-YF-2026-09-30 |  |  |
| price | 415.5 | legacy_unverified | actual | SRC-v15-html | $415.50 |  |
| ps_ratio | 15.4 | legacy_unverified | actual | SRC-v15-html | 15.4 |  |
| quarter_note | Q2 (7/16) \| $40.2B (+36%) · HPC 66% \| GM 67.7% / OpM 60.3% 역대 최고 · 2026 가이던스 +30%→+40% 이상 \| TTM +$36B · capex $60~64B | legacy_unverified | text | SRC-v15-html |  | 최근 분기 실적 원문(③⑨ 참고). TTM 대체 금지 |
| revenue_ttm | $121.4B | verified | actual | SRC-SEC-TSM-20F-FY2025 | FY2025 매출 NT$3,809,054.3백만 (US$121,423.5백만) | F6-REG-28 / TSM-EDGAR-29. **EDGAR 원문 우회 건**이다 — basis.bypass 에 사유·검산·복귀 조건을 남겼다 |
| revenue_ttm_prior | $92.3B | verified | actual | SRC-SEC-TSM-20F-FY2025 | FY2024 매출 NT$2,894,307.7백만 (같은 표 둘째 열) | F6-REG-28. **당해와 같은 환율 31.37 로 환산**했다. 공시 USD 를 그대로 쓰지 않았다 |
| runway_years | — | not_applicable | derived | SRC-v15-html | ∞ | TTM FCF 흑자라 런웨이 산식 적용 대상 아님(원문 ∞) |
| ttm_per | 30.9 | legacy_unverified | actual | SRC-v15-html | 30.9 |  |
| undrawn_credit | — | not_disclosed | actual | SRC-SEC-FACTS-F6 |  | FIX-54 1단계 S2 전수 — 확정 미인출 여신 미확인(우리가 확인하지 않았다). |

### Alibaba

| 지표 | 값 | 상태 | 종류 | 출처 | 원문 | 비고 |
| --- | --- | --- | --- | --- | --- | --- |
| capex_ttm | $23.1B | legacy_unverified | actual | SRC-v15-html | $23.1B |  |
| cash | $19.1B | verified | actual | SRC-SEC-BABA-20F-FY2026 | 현금및현금성자산 19.1B (버퍼 41.6B 는 basis 에 보존) | CASH-FCF-35. **순수 현금으로 등록한다** — 설계 지침 6.4. 유동성 버퍼와 총계는 basis.preserved_wider_def |
| cash | $56.8B | legacy_unverified | actual | SRC-v15-html | $56.8B | [CASH-FCF-35 대체됨 → alibaba.cash.cashfcf35]  |
| contracted_revenue | — | not_disclosed | actual | SRC-SEC-BABA-20F-FY2026 | 미공시 — ASC 606 실무적 간편법 선언 | OBS-REG-25 · [FIX-53 3단계] **확인된 미공시.** 20-F 가 두 갈래(1년 이하 계약 · right-to-invoice 계 |
| contracted_revenue | — | not_disclosed | actual | SRC-v15-rule | — | [OBS-REG-25 대체됨 → alibaba.contracted_revenue.obsreg25] 규칙 v1.5 ⑨ 게이트 4 적용표 |
| credit_rating | A급 | legacy_unverified | text | SRC-v15-html | A급 | 별표 J 교차검증 전용 — 점수 입력 아님 |
| debt_ebitda | 2.7 | legacy_unverified | actual | SRC-v15-html | 2.68 |  |
| fcf_ttm | -$7.2B | verified | derived | SRC-SEC-BABA-20F-FY2026 | TTM FCF -7.2B = OCF 11.0B - CapEx 18.3B | CASH-FCF-35. SEC 실측. OCF·CapEx 구성요소를 basis 에 남겼다 |
| fcf_ttm | -$11.4B | legacy_unverified | actual | SRC-v15-html | -$11.4B | [CASH-FCF-35 대체됨 → alibaba.fcf_ttm.cashfcf35]  |
| market_cap | $267.4B | verified | actual | SRC-YF-2026-09-30 |  |  |
| market_cap | $270.0B | legacy_unverified | actual | SRC-v15-md | $270B |  |
| net_borrowing_ttm | $7.5B | legacy_unverified | actual | SRC-v15-html | +$7.5B | 차환 제외 순증 |
| net_cash | $49.8B | verified | derived | SRC-SEC-BABA-20F-FY2026 | RMB백만 625,509.0 − 281,722.0 = 343,787.0 ÷ 6.898 = 49.8B USD | NETCASH-37. **보존 20-F 문면 실측** · 유가증권은 시장성 있는 것만 |
| net_cash | $17.5B | legacy_unverified | actual | SRC-v15-html | +$17.5B | [NETCASH-37 대체됨 → alibaba.net_cash.nc37]  |
| net_income_ttm | $15.0B | verified | actual | SRC-SEC-BABA-FACTS | 2025-04-01~2026-03-31 103,592,000,000 CNY | F6-REG-28. **당해와 같은 환율 6.8980 으로 환산**했다 |
| nonop_share | 54% | legacy_unverified | actual | SRC-v15-html | 54% ⚠️ |  |
| ntm_per | 16.7 | legacy_unverified | estimate | SRC-v15-md | 16.7 ✱ |  |
| offbalance_B | $36.9B | verified | derived | SRC-SEC-BABA-20F-FY2026 | 자본약정 RMB54,136M + 기타약정 RMB200,062M = RMB254,198M (2026-03-31) → US$36,851M @6.89 | OBS-REG-25. **원 통화는 RMB 다.** 스키마가 unit 을 지표 단위(USD)로 강제해 RMB 를 그대로 둘 자리가 없어 20-F |
| offbalance_B | — | not_disclosed | actual | SRC-v15-rule | 미확인 | [OBS-REG-25 대체됨 → alibaba.offbalance_B.obsreg25] 규칙 v1.5 ⑨ 게이트 4 적용표 |
| offbalance_note | 미확인 (증자 $10.2B) | legacy_unverified | text | SRC-v15-html | 미확인 (증자 $10.2B) | 부외 약정 원문(A/B/C 분류 전) |
| operating_income_ttm | $7.3B | verified | actual | SRC-SEC-BABA-FACTS | FY2026 영업이익 RMB50,150M (US$7,270M) | OBS-REG-25 / G1-TTM-26. 연간 기준. |
| operating_margin_ttm | 5% | verified | derived | SRC-SEC-BABA-FACTS | FY2026 영업이익률 +4.899% | OBS-REG-25 / G1-TTM-26. **양수다** — G1 을 통과한다. **연간 기준이라는 한계는 F6 P4 가 이미 한 칸 내린다.  |
| pretax_income_ttm | $18.8B | verified | derived | SRC-SEC-BABA-FACTS | 세전이익 TTM 18.8B USD | NONOP-44. nonop_share 산식 정정 입력 — 저장값이 영업외손익÷세전이익 임이 확인됐다 |
| price | 107.54000091552734 | verified | actual | SRC-YF-2026-09-30 |  |  |
| price | 111.76 | legacy_unverified | actual | SRC-v15-html | $111.76 |  |
| ps_ratio | 1.8 | legacy_unverified | actual | SRC-v15-html | 1.8 |  |
| quarter_note | 6월 분기 (8/20) \| $39.64B (+9%) · 클라우드 +26% \| non-GAAP $1.26 (컨센 $1.51 하회) · 영업흑자 복귀 \| 분기 -$6.6B · TTM -$11.4B · 완충 $41B+$10.2B | legacy_unverified | text | SRC-v15-html |  | 최근 분기 실적 원문(③⑨ 참고). TTM 대체 금지 |
| revenue_ttm | $148.4B | verified | actual | SRC-SEC-BABA-FACTS | FY2026 매출 RMB1,023,670M (US$148,401M) | OBS-REG-25 / G1-TTM-26. **연간 기준이다.** F6 P4 가 기간 단위 TTM 아님으로 한 칸 내린다. 같은 한계를 F9 에 |
| revenue_ttm_prior | $144.4B | verified | actual | SRC-SEC-BABA-FACTS | 2024-04-01~2025-03-31 996,347,000,000 CNY | F6-REG-28. **당해와 같은 환율 6.8980 으로 환산**했다 |
| runway_years | 5.0 | legacy_unverified | derived | SRC-v15-html | 5.0년 | 원본 계산값(현금 ÷ 연 소진) |
| ttm_per | 25.8 | legacy_unverified | actual | SRC-v15-html | 25.8 |  |
| undrawn_credit | $3.3B | verified | actual | SRC-SEC-BABA-20F-FY2026 | 미인출 회전여신 US$3.33B (2026-03-31, 20-F 주석 21) | FIX-53 2단계. 감사 주석 1차 · MD&A 교차. 런웨이 분자에 들어간다. |
| undrawn_credit | $2.6B | incompatible_basis | estimate | SRC-SEC-BABA-20F-FY2026 | 미사용 약정 approximately US$2.6B (3.17B 시설, 런웨이 제외) | FIX-53 2단계. 근사치라 런웨이 분자에서 뺀다. 결론 민감도는 basis.sensitivity. |

### Anthropic

| 지표 | 값 | 상태 | 종류 | 출처 | 원문 | 비고 |
| --- | --- | --- | --- | --- | --- | --- |
| arr | $65.0B | legacy_unverified | run_rate | SRC-v15-rule | ARR $65B(7월 런레이트) | 규칙 v1.5 ⑥ 비상장 절 |
| arr_prior | $47.0B | legacy_unverified | run_rate | SRC-ANTHROPIC-SERIESH-2026 | ARR $47B → $65B (직전 런레이트) | PRIV-IMPL-31 / C-12. P3 입력. 시점 라벨이 원문에 없어 null 이다 |
| cash | — | not_disclosed | actual | SRC-v15-md | 미공시 | PRIV-IMPL-31 / C-20. 승계 관측 anthropic.cash.v15 의 결측 유형을 등록한다. **값은 그대로 없다** — 라벨만 |
| cash | — | not_disclosed | actual | SRC-v15-html | 미공시 | [PRIV-IMPL-31 대체됨 → anthropic.cash.priv31]  |
| contracted_revenue | — | not_disclosed | actual | SRC-v15-rule | 미공시 — 비상장이라 계약 수입(ASC 606 잔여 수행의무)을 제출할 의무가 없다 | 규칙 v1.5 ⑨ 게이트 4 적용표 |
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
| lease_liabilities | — | not_disclosed | actual | SRC-SEC-FACTS-F6 | 2026-06-27 기준 리스부채 없음 — 10-K 에만 태깅 | NETCASH-37. net_cash 실측이 막힌 이유를 여기 남긴다 — [FIX-54 2단계] unverified(표준 태그 결측, 10-Q  |
| market_cap | $4.86T | verified | actual | SRC-YF-2026-09-30 |  |  |
| market_cap | $4.74T | legacy_unverified | actual | SRC-v15-md | $4.74T |  |
| net_borrowing_ttm | -$17.3B | legacy_unverified | actual | SRC-v15-html | -$17.3B | 차환 제외 순증 |
| net_cash | $62.2B | legacy_unverified | actual | SRC-v15-md | +$62.2B |  |
| net_income_ttm | $128.9B | verified | derived | SRC-SEC-FACTS-F6 | 2025-06-29~2026-06-27 128,930,000,000 | F6-REG-28. F6-SPEC-18 수집기 |
| nonop_share | 1% | legacy_unverified | actual | SRC-v15-html | 1% |  |
| ntm_per | 35.5 | legacy_unverified | estimate | SRC-v15-md | 35.5 |  |
| offbalance_note | 미확인 | legacy_unverified | text | SRC-v15-html | 미확인 | 부외 약정 원문(A/B/C 분류 전) |
| operating_income_ttm | $154.9B | verified | derived | SRC-SEC-FACTS-F6 | 2025-06-29~2026-06-27 154,859,000,000 | F6-REG-28. G1-FILL-27 기준값 |
| pretax_income_ttm | $155.9B | verified | derived | SRC-SEC-FACTS-F6 | 세전이익 TTM 155.9B USD | NONOP-44. nonop_share 산식 정정 입력 — 저장값이 영업외손익÷세전이익 임이 확인됐다 |
| price | 333.0199890136719 | verified | actual | SRC-YF-2026-09-30 |  |  |
| price | 324.96 | legacy_unverified | actual | SRC-v15-html | $324.96 |  |
| ps_ratio | 10.2 | legacy_unverified | actual | SRC-v15-html | 10.2 |  |
| quarter_note | 6월 분기 (7/30) \| $109.4B (+16%) \| $2.02 상회 (Services 하회) \| TTM +$137B | legacy_unverified | text | SRC-v15-html |  | 최근 분기 실적 원문(③⑨ 참고). TTM 대체 금지 |
| revenue_ttm | $466.8B | verified | derived | SRC-SEC-FACTS-F6 | 2025-06-29~2026-06-27 466,823,000,000 | F6-REG-28. G1-FILL-27 기준값 |
| revenue_ttm_prior | $408.6B | verified | derived | SRC-SEC-FACTS-F6 | 2024-06-30~2025-06-28 408,625,000,000 | F6-REG-28. F6-SPEC-18 수집기 |
| runway_years | — | not_applicable | derived | SRC-v15-html | ∞ | TTM FCF 흑자라 런웨이 산식 적용 대상 아님(원문 ∞) |
| ttm_per | 37.3 | legacy_unverified | actual | SRC-v15-html | 37.3 |  |
| undrawn_credit | — | not_disclosed | actual | SRC-SEC-FACTS-F6 |  | FIX-54 1단계 S2 전수 — 확정 미인출 여신 미확인(우리가 확인하지 않았다). |

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
| market_cap | $5.51T | verified | actual | SRC-YF-2026-09-30 |  |  |
| market_cap | $5.42T | legacy_unverified | actual | SRC-v15-md | $5.42T |  |
| net_borrowing_ttm | $24.9B | legacy_unverified | actual | SRC-v15-html | +$24.9B | 차환 제외 순증 |
| net_cash | $60.5B | verified | derived | SRC-SEC-FACTS-F6 | 현금 22.4B + 채무증권 34.1B + 시장성 지분증권 42.8B = 99.4B − 차입 38.9B = 60.5B | NETCASH-37. SEC 보존 원자료 실측. **유가증권은 시장성 있는 것만** |
| net_cash | $23.6B | legacy_unverified | actual | SRC-v15-html | +$23.6B | [NETCASH-37 대체됨 → nvidia.net_cash.nc37]  |
| net_income_ttm | $192.9B | verified | derived | SRC-SEC-FACTS-F6 | 2025-07-28~2026-07-26 192,879,000,000 | F6-REG-28. F6-SPEC-18 수집기 |
| nonop_share | 14% | legacy_unverified | actual | SRC-v15-html | 14% ᵃ |  |
| ntm_per | 18.0 | legacy_unverified | estimate | SRC-v15-md | 18.0 |  |
| offbalance_note | 보증 $105B + 잔존가치 25% + 백스톱 + $6.3B (우발·C종) | legacy_unverified | text | SRC-v15-html | 보증 $105B + 잔존가치 25% + 백스톱 + $6.3B (우발·C종) | 부외 약정 원문(A/B/C 분류 전) |
| operating_income_ttm | $197.6B | verified | derived | SRC-SEC-FACTS-F6 | 2025-07-28~2026-07-26 197,579,000,000 | F6-REG-28. G1-FILL-27 기준값 |
| pretax_income_ttm | $229.7B | verified | derived | SRC-SEC-FACTS-F6 | 세전이익 TTM 229.7B USD | NONOP-44. nonop_share 산식 정정 입력 — 저장값이 영업외손익÷세전이익 임이 확인됐다 |
| price | 228.3800048828125 | verified | actual | SRC-YF-2026-09-30 |  |  |
| price | 224.41 | legacy_unverified | actual | SRC-v15-html | $224.41 |  |
| ps_ratio | 17.9 | legacy_unverified | actual | SRC-v15-html | 17.9 |  |
| quarter_note | Q2 FY27 (8/26) \| $96.2B (+106%) · DC $89.0B (+117%) \| GAAP $2.46 / non-GAAP $2.22 · DC 컨센 $86.3B 상회 \| TTM +$127B · 환원 $26B | legacy_unverified | text | SRC-v15-html |  | 최근 분기 실적 원문(③⑨ 참고). TTM 대체 금지 |
| revenue_ttm | $303.0B | verified | derived | SRC-SEC-FACTS-F6 | 2025-07-28~2026-07-26 302,970,000,000 | F6-REG-28. G1-FILL-27 기준값 |
| revenue_ttm_prior | $165.2B | verified | derived | SRC-SEC-FACTS-F6 | 2024-07-29~2025-07-27 165,218,000,000 | F6-REG-28. F6-SPEC-18 수집기 |
| runway_years | — | not_applicable | derived | SRC-v15-html | ∞ | TTM FCF 흑자라 런웨이 산식 적용 대상 아님(원문 ∞) |
| ttm_per | 27.5 | legacy_unverified | actual | SRC-v15-html | 27.5 |  |
| undrawn_credit | — | not_disclosed | actual | SRC-SEC-FACTS-F6 |  | FIX-54 1단계 S2 전수 — 확정 미인출 여신 미확인(우리가 확인하지 않았다). |

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
| lease_liabilities | — | not_disclosed | actual | SRC-SEC-FACTS-F6 | 2026-06-30 기준 리스부채 유동분 없음 — 비유동분 211,400천만 태깅 | NETCASH-37. net_cash 실측이 막힌 이유를 여기 남긴다 — [FIX-54 2단계] unverified(표준 태그 결측, 10-Q  |
| market_cap | $449.5B | verified | actual | SRC-YF-2026-09-30 |  |  |
| market_cap | $407.0B | legacy_unverified | actual | SRC-v15-md | $407B |  |
| net_borrowing_ttm | — | not_disclosed | actual | SRC-v15-html | 없음 | 차환 제외 순증 |
| net_cash | $9.2B | legacy_unverified | actual | SRC-v15-md | +$9.2B |  |
| net_income_ttm | $3.0B | verified | derived | SRC-SEC-FACTS-F6 | 2025-07-01~2026-06-30 3,016,692,000 | F6-REG-28. F6-SPEC-18 수집기 |
| nonop_share | 14% | legacy_unverified | actual | SRC-v15-html | 14% ᵇ |  |
| ntm_per | 89.0 | legacy_unverified | estimate | SRC-v15-md | 89.0 |  |
| offbalance_note | 미확인 — v1.5 원표기 `없음` | legacy_unverified | text | SRC-v15-html | 없음 | 부외 약정 원문(A/B/C 분류 전) |
| operating_income_ttm | $2.6B | verified | derived | SRC-SEC-FACTS-F6 | 2025-07-01~2026-06-30 2,634,652,000 | F6-REG-28. G1-FILL-27 기준값 |
| pretax_income_ttm | $3.1B | verified | derived | SRC-SEC-FACTS-F6 | 세전이익 TTM 3.1B USD | NONOP-44. nonop_share 산식 정정 입력 — 저장값이 영업외손익÷세전이익 임이 확인됐다 |
| price | 187.0500030517578 | verified | actual | SRC-YF-2026-09-30 |  |  |
| price | 169.46 | legacy_unverified | actual | SRC-v15-html | $169.46 |  |
| ps_ratio | 66.2 | legacy_unverified | actual | SRC-v15-html | 66.2 |  |
| quarter_note | Q2 (8/3) \| $1.94B (+92.8%) · 4분기 연속 상회 \| $0.41 (컨센 $0.35 상회) \| TTM +$3.4B | legacy_unverified | text | SRC-v15-html |  | 최근 분기 실적 원문(③⑨ 참고). TTM 대체 금지 |
| revenue_ttm | $6.2B | verified | derived | SRC-SEC-FACTS-F6 | 2025-07-01~2026-06-30 6,155,941,000 | F6-REG-28. G1-FILL-27 기준값 |
| revenue_ttm_prior | $3.4B | verified | derived | SRC-SEC-FACTS-F6 | 2024-07-01~2025-06-30 3,440,587,000 | F6-REG-28. F6-SPEC-18 수집기 |
| runway_years | — | not_applicable | derived | SRC-v15-html | ∞ | TTM FCF 흑자라 런웨이 산식 적용 대상 아님(원문 ∞) |
| ttm_per | 144.9 | legacy_unverified | actual | SRC-v15-html | 144.9 |  |
| undrawn_credit | — | not_disclosed | actual | SRC-SEC-FACTS-F6 |  | FIX-54 1단계 S2 전수 — 확정 미인출 여신 미확인(우리가 확인하지 않았다). |

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
| market_cap | $1.99T | verified | actual | SRC-YF-2026-09-30 |  |  |
| market_cap | $1.91T | legacy_unverified | actual | SRC-v15-md | $1.91T |  |
| net_borrowing_ttm | $102.0B | legacy_unverified | actual | SRC-v15-html | +$102.0B | 차환 제외 순증 |
| net_cash | $60.3B | verified | derived | SRC-SEC-FACTS-F6 | 현금+시장성증권 100.0B − 차입 39.4B − 리스 0.3B(운용리스 유동분만 — 비유동 결측) = 60.3B | NETCASH-37. SEC 보존 원자료 실측. **유가증권은 시장성 있는 것만** |
| net_cash | $60.3B | legacy_unverified | actual | SRC-v15-html | +$60.3B | [NETCASH-37 대체됨 → spacex-xai.net_cash.nc37]  |
| net_income_ttm | -$8.2B | verified | derived | SRC-SEC-FACTS-F6 | TTM -8,218백만 | F6-REG-28. S-1/A 감사 손익계산서 FY2025 + 10-Q 2026 상반기 - 10-Q 2025 상반기. **매출 쌍(분기)과 기준 |
| nonop_share | — | incompatible_basis | actual | SRC-v15-html | 적자 | FIX-53 3단계. 세전이익 음수 — 부호 규약 미정이라 산출 안 함. P4 강등은 short_history 한 칸으로 이미 걸려 점수 불변. |
| ntm_per | 111.0 | legacy_unverified | estimate | SRC-v15-md | 111 |  |
| offbalance_B | $29.6B | verified | derived | SRC-SEC-SPCX-10Q-2026Q2 | 미개시 리스 $1,627M(2025-12-31) + 무조건 구매약정 $27,955M(2026-06-30) = $29,582M | OBS-REG-25. **기준일이 섞인 합계다.** 구성요소별 기준일·출처를 basis.components 에 남겼다. 관측을 둘로 쪼개지 않은 |
| offbalance_B | — | not_disclosed | actual | SRC-v15-rule | 미확인 | [OBS-REG-25 대체됨 → spacex-xai.offbalance_B.obsreg25] 규칙 v1.5 ⑨ 게이트 4 적용표 |
| offbalance_note | 미확인 | legacy_unverified | text | SRC-v15-html | 미확인 | 부외 약정 원문(A/B/C 분류 전) |
| operating_income_ttm | -$3.7B | verified | derived | SRC-SEC-FACTS-F6 | TTM -3,732백만 | F6-REG-28. S-1/A 감사 손익계산서 FY2025 + 10-Q 2026 상반기 - 10-Q 2025 상반기. **매출 쌍(분기)과 기준 |
| operating_margin_ttm | -16% | verified | derived | SRC-SEC-FACTS-F6 | TTM 영업손실률 -16.195% | F6-REG-28. 승계 legacy -14.9% 를 실측 -16.195% 로 교체한다. 재척도 밴드에서 둘 다 -3 이라 점수는 안 바뀌고 근 |
| operating_margin_ttm | -15% | legacy_unverified | actual | SRC-v15-html | -$0.09 (컨센 -$0.26 상회) · 영업적자 -14.9% | [F6-REG-28 대체됨 → spacex-xai.operating_margin_ttm.f6reg28] EARN 열의 영업적자율. 규칙 ⑨ 표는 |
| pretax_income_ttm | -$7.6B | verified | derived | SRC-SEC-SPCX-10Q-2026Q2 | TTM 세전손실 -7,623M | FIX-53 3단계. S-1/A FY2025 + 10-Q 반기 복원. 순이익과 세금으로 닫힌다. |
| price | 150.86000061035156 | verified | actual | SRC-YF-2026-09-30 |  |  |
| price | 140.71 | legacy_unverified | actual | SRC-v15-html | $140.71 |  |
| ps_ratio | 82.9 | legacy_unverified | actual | SRC-v15-html | 82.9 |  |
| quarter_note | Q2 (8/4) \| $7.8B (+92%) · Starlink 1,200만 · AI 세그먼트 $2.56B(+247%) \| -$0.09 (컨센 -$0.26 상회) · 영업적자 -14.9% \| TTM -$32.5B · 현금 $100B | legacy_unverified | text | SRC-v15-html |  | 최근 분기 실적 원문(③⑨ 참고). TTM 대체 금지 |
| revenue_ttm | $7.8B | verified | actual | SRC-SEC-FACTS-F6 | 2026Q2 분기 매출 7,814M (TTM 아님) | F6-REG-28. **분기 전년 동기 기준이다** \| [FIX-53 3단계] **분기값(2026Q2) — TTM 아님.** P3 분기 YoY  |
| revenue_ttm_full | $23.0B | verified | derived | SRC-SEC-SPCX-S1A-2026 | TTM 매출 23,044M (FY2025 18,674 + H1'26 12,508 − H1'25 8,138) | FIX-56 1단계. 12개월 매출 — P2 전용. 분기값 `revenue_ttm` 과 다른 지표다. |
| revenue_ttm_prior | $4.1B | verified | actual | SRC-SEC-FACTS-F6 | 2025 Q2 분기 매출 $4,071M (TTM 아님) | F6-REG-28. 같은 분기 전년 동기 \| [FIX-54 2단계] **분기값(2025Q2) — TTM 아님.** P3 분기 YoY 전용. |
| runway_years | 3.1 | legacy_unverified | derived | SRC-v15-html | 3.1년 | 원본 계산값(현금 ÷ 연 소진) |
| ttm_per | — | not_applicable | actual | SRC-v15-html | 적자 | 적자 |
| undrawn_credit | $4.4B | verified | actual | SRC-SEC-SPCX-10Q-2026Q2 | 미인출 회전여신 확인 하한 US$4,355M (한도 5,000 − 신용장 645, 2026-06-30) | FIX-54 1단계 S1. 보수적 하한. 신용장이 시설 밖이면 5,000M — 결론 같음(basis.sensitivity). |

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
| market_cap | $1.40T | verified | actual | SRC-YF-2026-09-30 |  |  |
| market_cap | $1.41T | legacy_unverified | actual | SRC-v15-md | $1.41T |  |
| net_borrowing_ttm | $1.8B | legacy_unverified | actual | SRC-v15-html | +$1.8B | 차환 제외 순증 |
| net_cash | $27.4B | verified | derived | SRC-SEC-FACTS-F6 | 현금+시장성증권 43.5B − 차입 9.1B − 리스 7.0B = 27.4B | NETCASH-37. SEC 보존 원자료 실측. **유가증권은 시장성 있는 것만** |
| net_cash | $27.4B | legacy_unverified | actual | SRC-v15-html | +$27.4B | [NETCASH-37 대체됨 → tesla.net_cash.nc37]  |
| net_income_ttm | $3.8B | verified | derived | SRC-SEC-FACTS-F6 | 2025-07-01~2026-06-30 3,804,000,000 | F6-REG-28. F6-SPEC-18 수집기 |
| nonop_share | 18% | legacy_unverified | actual | SRC-v15-html | 18% ᵇ |  |
| ntm_per | 187.5 | legacy_unverified | estimate | SRC-v15-md | 187.5 |  |
| offbalance_note | 미확인 | legacy_unverified | text | SRC-v15-html | 미확인 | 부외 약정 원문(A/B/C 분류 전) |
| operating_income_ttm | $4.4B | verified | derived | SRC-SEC-FACTS-F6 | 2025-07-01~2026-06-30 4,372,000,000 | F6-REG-28. G1-FILL-27 기준값 |
| pretax_income_ttm | $5.2B | verified | derived | SRC-SEC-FACTS-F6 | 세전이익 TTM 5.2B USD | NONOP-44. nonop_share 산식 정정 입력 — 저장값이 영업외손익÷세전이익 임이 확인됐다 |
| price | 354.80999755859375 | verified | actual | SRC-YF-2026-09-30 |  |  |
| price | 357.01 | legacy_unverified | actual | SRC-v15-html | $357.01 |  |
| ps_ratio | 13.6 | legacy_unverified | actual | SRC-v15-html | 13.6 |  |
| quarter_note | Q2 (7/22) \| $28.24B (+26%) \| $0.33 (컨센 $0.53 하회) · 영업흑자 마진 4% \| TTM +$5.8B | legacy_unverified | text | SRC-v15-html |  | 최근 분기 실적 원문(③⑨ 참고). TTM 대체 금지 |
| revenue_ttm | $103.6B | verified | derived | SRC-SEC-FACTS-F6 | 2025-07-01~2026-06-30 103,619,000,000 | F6-REG-28. G1-FILL-27 기준값 |
| revenue_ttm_prior | $92.7B | verified | derived | SRC-SEC-FACTS-F6 | 2024-07-01~2025-06-30 92,720,000,000 | F6-REG-28. F6-SPEC-18 수집기 |
| runway_years | — | not_applicable | derived | SRC-v15-html | ∞ | TTM FCF 흑자라 런웨이 산식 적용 대상 아님(원문 ∞) |
| ttm_per | 370.5 | legacy_unverified | actual | SRC-v15-html | 370.5 |  |
| undrawn_credit | — | not_disclosed | actual | SRC-SEC-FACTS-F6 |  | FIX-54 1단계 S2 전수 — 확정 미인출 여신 미확인(우리가 확인하지 않았다). \| [FIX-55 2단계 대체됨 → tesla.undraw |
| undrawn_credit | $5.0B | verified | actual | SRC-SEC-FACTS-F6 | us-gaap:DebtInstrumentUnusedBorrowingCapacityAmount 2026-06-30 = 5,000,000,000 U | FIX-55 2단계 · obsreg 4차 리뷰 A 분담(NTM Claude 독립 세션, 기준 ab5a053 · review 0752b05) hi |

### Oracle

| 지표 | 값 | 상태 | 종류 | 출처 | 원문 | 비고 |
| --- | --- | --- | --- | --- | --- | --- |
| capex_ttm | $55.7B | legacy_unverified | actual | SRC-v15-html | $55.7B |  |
| cash | $31.3B | verified | actual | SRC-SEC-FACTS-F6 | 현금및현금성자산 31.3B (버퍼 31.9B 는 basis 에 보존) | CASH-FCF-35. **순수 현금으로 등록한다** — 설계 지침 6.4. 유동성 버퍼와 총계는 basis.preserved_wider_def |
| cash | $31.9B | legacy_unverified | actual | SRC-v15-html | $31.9B | [CASH-FCF-35 대체됨 → oracle.cash.cashfcf35]  |
| contracted_revenue | $638.0B | verified | actual | SRC-SEC-FACTS-F6 | RPO 638,000M (2026-05-31, 10-K) | FIX-57 1단계. G4 분자 실측 등록. 값·커버리지·step 불변. |
| contracted_revenue | $638.0B | legacy_unverified | actual | SRC-v15-rule | RPO $638B | 규칙 v1.5 ⑨ 게이트 4 적용표 |
| credit_rating | BBB- ⚠️ | legacy_unverified | text | SRC-v15-html | BBB- ⚠️ | 별표 J 교차검증 전용 — 점수 입력 아님 |
| debt_ebitda | 5.0 | legacy_unverified | actual | SRC-v15-html | 5.03 ⚠️ |  |
| fcf_ttm | -$23.7B | verified | derived | SRC-SEC-FACTS-F6 | TTM FCF -23.7B = OCF 32.0B - CapEx 55.7B | CASH-FCF-35. SEC 실측. OCF·CapEx 구성요소를 basis 에 남겼다 |
| fcf_ttm | -$23.7B | legacy_unverified | actual | SRC-v15-html | -$23.7B | [CASH-FCF-35 대체됨 → oracle.fcf_ttm.cashfcf35]  |
| market_cap | $416.2B | verified | actual | SRC-YF-2026-09-30 |  |  |
| market_cap | $443.7B | legacy_unverified | actual | SRC-v15-md | $443.7B |  |
| net_borrowing_ttm | $40.2B | legacy_unverified | actual | SRC-v15-html | +$40.2B | 차환 제외 순증 |
| net_cash | -$135.5B | verified | derived | SRC-SEC-FACTS-F6 | 현금+시장성증권 31.9B − 차입 129.5B − 리스 37.9B = -135.5B | NETCASH-37. SEC 보존 원자료 실측. **유가증권은 시장성 있는 것만** |
| net_cash | -$135.5B | legacy_unverified | actual | SRC-v15-html | -$135.5B | [NETCASH-37 대체됨 → oracle.net_cash.nc37]  |
| net_income_ttm | $17.1B | verified | actual | SRC-SEC-FACTS-F6 | 2025-06-01~2026-05-31 17,087,000,000 | F6-REG-28. F6-SPEC-18 수집기 |
| nonop_share | -15% | legacy_unverified | actual | SRC-v15-html | -15% ᶜ |  |
| ntm_per | 19.1 | legacy_unverified | estimate | SRC-v15-md | 19.1 |  |
| offbalance_B | $250.0B | legacy_unverified | actual | SRC-v15-rule | 리스 $250B(15~20년) | 규칙 v1.5 ⑨ 게이트 4 적용표 |
| offbalance_note | 리스 $250B(15~20년) | legacy_unverified | text | SRC-v15-html | 리스 $250B(15~20년) | 부외 약정 원문(A/B/C 분류 전) |
| operating_income_ttm | $20.6B | verified | actual | SRC-SEC-FACTS-F6 | 2025-06-01~2026-05-31 20,606,000,000 | F6-REG-28. G1-FILL-27 기준값 |
| pretax_income_ttm | $19.6B | verified | derived | SRC-SEC-FACTS-F6 | 세전이익 TTM 19.6B USD | NONOP-44. nonop_share 산식 정정 입력 — 저장값이 영업외손익÷세전이익 임이 확인됐다 |
| price | 137.3000030517578 | verified | actual | SRC-YF-2026-09-30 |  |  |
| price | 154.04 | legacy_unverified | actual | SRC-v15-html | $154.04 |  |
| ps_ratio | 6.6 | legacy_unverified | actual | SRC-v15-html | 6.6 |  |
| quarter_note | Q4 FY26 (3~5월) \| $19.2B (+21%) · OCI $5.8B (+93%) \| 영업마진 33.2% \| TTM -$23.7B · 현금 $31.9B · 런웨이 1.3년 | legacy_unverified | text | SRC-v15-html |  | 최근 분기 실적 원문(③⑨ 참고). TTM 대체 금지 |
| revenue_ttm | $67.4B | verified | actual | SRC-SEC-FACTS-F6 | 2025-06-01~2026-05-31 67,357,000,000 | F6-REG-28. G1-FILL-27 기준값 |
| revenue_ttm_prior | $57.4B | verified | actual | SRC-SEC-FACTS-F6 | 2024-06-01~2025-05-31 57,399,000,000 | F6-REG-28. F6-SPEC-18 수집기 |
| runway_years | 1.3 | legacy_unverified | derived | SRC-v15-html | 1.3년 ⚠️ | 원본 계산값(현금 ÷ 연 소진) |
| ttm_per | 26.4 | legacy_unverified | actual | SRC-v15-html | 26.4 |  |
| undrawn_credit | — | not_disclosed | actual | SRC-SEC-FACTS-F6 |  | FIX-54 1단계 S2 전수 — 확정 미인출 여신 미확인(우리가 확인하지 않았다). |

### OpenAI

| 지표 | 값 | 상태 | 종류 | 출처 | 원문 | 비고 |
| --- | --- | --- | --- | --- | --- | --- |
| arr | $40.0B | legacy_unverified | run_rate | SRC-v15-rule | 런레이트 $40B+(8/20) | 규칙 v1.5 ⑥ 비상장 절 |
| arr_prior | $25.0B | legacy_unverified | run_rate | SRC-v15-md | ARR $25B → $40B (2~4월 정체 구간) | PRIV-IMPL-31 / C-12. P3 입력. arr 시점 표기가 원문 안에서 갈리나 금액은 같아 점수 영향 없음 |
| cash | — | not_disclosed | actual | SRC-v15-md | 미공시 | PRIV-IMPL-31 / C-20. 승계 관측 openai.cash.v15 의 결측 유형을 등록한다. **값은 그대로 없다** — 라벨만 붙인 |
| cash | — | not_disclosed | actual | SRC-v15-html | 미공시 | [PRIV-IMPL-31 대체됨 → openai.cash.priv31]  |
| contracted_revenue | — | not_disclosed | actual | SRC-v15-rule | 미공시 — 비상장이라 계약 수입(ASC 606 잔여 수행의무)을 제출할 의무가 없다 | 규칙 v1.5 ⑨ 게이트 4 적용표 |
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
| ② 게임체인저 | score | 4 | — | carried | legacy:v1.5 2026-09-02 | ~~C-03: 경로 매핑 미확정 — 승계 점수~~ C-03 확정(paths_with_generation_gap_5), 세대 격차는 판단 입력이라 |
| ③ Last Mover | criteria | — | imitation=fail, revenue_model=pass, acceleration=partial, door_closed=fail | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 ③ 판정표 |
| ④ 호황 이후 | score | 5 | — | carried | legacy:v1.5 2026-09-02 |  |
| ⑤ 아군 | grade | — | A=2, H=-1 | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 별표 G 판정표 |
| ⑦ 순환금융 | matrix | — | funding_dependent_share=small, own_money_returns=yes | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 별표 I 판정표 \| [IMPL-50] **영업외 비중은 F7 입력이 아니다.** F6 P4 전용이다 — 채점규칙 별표 I 351~ |
| ⑧ 비대칭 의존 | score | -1 | — | carried | legacy:v1.5 2026-09-02 |  |
| ⑨ 적자 깊이 | gate_inputs | — | fcf_trend=deteriorating, bep_retreat=no, buffer_erosion=no, direction_A=unknown, direction_B=unknown, coverage_comparable=unknown, operating_result_reviewed=profit | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 ⑨ 적용표(추세·BEP·커버리지 비교 가능성) |

### Amazon / AWS

| Factor | 종류 | 점수 | 입력 | 상태 | 검토 | 비고 |
| --- | --- | --- | --- | --- | --- | --- |
| ① 네트워크 | score | 5 | — | carried | legacy:v1.5 2026-09-02 |  |
| ② 게임체인저 | score | 4 | — | carried | legacy:v1.5 2026-09-02 | ~~C-03: 경로 매핑 미확정 — 승계 점수~~ C-03 확정(paths_with_generation_gap_5), 세대 격차는 판단 입력이라 |
| ③ Last Mover | criteria | — | imitation=fail, revenue_model=pass, acceleration=pass, door_closed=fail | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 ③ 판정표 |
| ④ 호황 이후 | score | 5 | — | carried | legacy:v1.5 2026-09-02 |  |
| ⑤ 아군 | grade | — | A=2, H=-1 | new | noble 2026-10-01 | 규칙 v1.5 별표 G 판정표 |
| ⑦ 순환금융 | matrix | — | funding_dependent_share=small, own_money_returns=yes | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 별표 I 판정표 \| [IMPL-50] **영업외 비중은 F7 입력이 아니다.** F6 P4 전용이다 — 채점규칙 별표 I 351~ |
| ⑧ 비대칭 의존 | score | -1 | — | carried | legacy:v1.5 2026-09-02 |  |
| ⑨ 적자 깊이 | gate_inputs | — | fcf_trend=unknown, bep_retreat=no, buffer_erosion=no, direction_A=unknown, direction_B=unknown, coverage_comparable=yes, operating_result_reviewed=profit | new | noble 2026-10-01 | 규칙 v1.5 ⑨ 적용표(추세·BEP·커버리지 비교 가능성) |

### Meta

| Factor | 종류 | 점수 | 입력 | 상태 | 검토 | 비고 |
| --- | --- | --- | --- | --- | --- | --- |
| ① 네트워크 | score | 5 | — | carried | legacy:v1.5 2026-09-02 |  |
| ② 게임체인저 | score | 4 | — | carried | legacy:v1.5 2026-09-02 | ~~C-03: 경로 매핑 미확정 — 승계 점수~~ C-03 확정(paths_with_generation_gap_5), 세대 격차는 판단 입력이라 |
| ③ Last Mover | criteria | — | imitation=partial, revenue_model=pass, acceleration=partial, door_closed=fail | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 ③ 판정표 |
| ④ 호황 이후 | score | 3 | — | carried | legacy:v1.5 2026-09-02 |  |
| ⑤ 아군 | grade | — | A=1, H=-1 | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 별표 G 판정표 |
| ⑦ 순환금융 | matrix | — | funding_dependent_share=small, own_money_returns=no | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 별표 I 판정표 \| [IMPL-50] **영업외 비중은 F7 입력이 아니다.** F6 P4 전용이다 — 채점규칙 별표 I 351~ |
| ⑧ 비대칭 의존 | score | -1 | — | carried | legacy:v1.5 2026-09-02 |  |
| ⑨ 적자 깊이 | gate_inputs | — | fcf_trend=deteriorating, bep_retreat=no, buffer_erosion=no, direction_A=unknown, direction_B=unknown, coverage_comparable=unknown, operating_result_reviewed=profit | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 ⑨ 적용표(추세·BEP·커버리지 비교 가능성) |

### Microsoft

| Factor | 종류 | 점수 | 입력 | 상태 | 검토 | 비고 |
| --- | --- | --- | --- | --- | --- | --- |
| ① 네트워크 | score | 5 | — | carried | legacy:v1.5 2026-09-02 |  |
| ② 게임체인저 | score | 3 | — | carried | legacy:v1.5 2026-09-02 | ~~C-03: 경로 매핑 미확정 — 승계 점수~~ C-03 확정(paths_with_generation_gap_5), 세대 격차는 판단 입력이라 |
| ③ Last Mover | criteria | — | imitation=fail, revenue_model=pass, acceleration=pass, door_closed=fail | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 ③ 판정표 |
| ④ 호황 이후 | score | 4 | — | carried | legacy:v1.5 2026-09-02 |  |
| ⑤ 아군 | grade | — | A=2, H=-1 | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 별표 G 판정표 |
| ⑦ 순환금융 | matrix | — | funding_dependent_share=small, own_money_returns=yes | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 별표 I 판정표 \| [IMPL-50] **영업외 비중은 F7 입력이 아니다.** F6 P4 전용이다 — 채점규칙 별표 I 351~ |
| ⑧ 비대칭 의존 | score | -1 | — | carried | legacy:v1.5 2026-09-02 |  |
| ⑨ 적자 깊이 | gate_inputs | — | fcf_trend=stable, bep_retreat=no, buffer_erosion=no, direction_A=unknown, direction_B=unknown, coverage_comparable=unknown, operating_result_reviewed=profit | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 ⑨ 적용표(추세·BEP·커버리지 비교 가능성) |

### TSMC

| Factor | 종류 | 점수 | 입력 | 상태 | 검토 | 비고 |
| --- | --- | --- | --- | --- | --- | --- |
| ① 네트워크 | score | 2 | — | carried | legacy:v1.5 2026-09-02 |  |
| ② 게임체인저 | score | 5 | — | carried | legacy:v1.5 2026-09-02 | ~~C-03: 경로 매핑 미확정 — 승계 점수~~ C-03 확정(paths_with_generation_gap_5), 세대 격차는 판단 입력이라 |
| ③ Last Mover | criteria | — | imitation=pass, revenue_model=fail, acceleration=pass, door_closed=fail | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 ③ 판정표 |
| ④ 호황 이후 | score | 4 | — | carried | legacy:v1.5 2026-09-02 |  |
| ⑤ 아군 | grade | — | A=1, H=-1 | new | 설계진행(A-STRICT-54 codex·Gemini 독립 일치) 2026-09-15 | [A-STRICT-54] 비 Claude 두 판정 일치 — codex(GPT) validation/a2-strict-54/codex.md · G |
| ⑦ 순환금융 | matrix | — | funding_dependent_share=small, own_money_returns=no | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 별표 I 판정표 \| [IMPL-50] **영업외 비중은 F7 입력이 아니다.** F6 P4 전용이다 — 채점규칙 별표 I 351~ |
| ⑧ 비대칭 의존 | score | -4 | — | carried | legacy:v1.5 2026-09-02 |  |
| ⑨ 적자 깊이 | gate_inputs | — | fcf_trend=stable, bep_retreat=no, buffer_erosion=no, direction_A=unknown, direction_B=unknown, coverage_comparable=unknown, operating_result_reviewed=profit | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 ⑨ 적용표(추세·BEP·커버리지 비교 가능성) |

### Alibaba

| Factor | 종류 | 점수 | 입력 | 상태 | 검토 | 비고 |
| --- | --- | --- | --- | --- | --- | --- |
| ① 네트워크 | score | 4 | — | carried | legacy:v1.5 2026-09-02 |  |
| ② 게임체인저 | score | 4 | — | carried | legacy:v1.5 2026-09-02 | ~~C-03: 경로 매핑 미확정 — 승계 점수~~ C-03 확정(paths_with_generation_gap_5), 세대 격차는 판단 입력이라 |
| ③ Last Mover | criteria | — | imitation=partial, revenue_model=pass, acceleration=pass, door_closed=fail | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 ③ 판정표 |
| ④ 호황 이후 | score | 4 | — | carried | legacy:v1.5 2026-09-02 |  |
| ⑤ 아군 | grade | — | A=1, H=-1 | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 별표 G 판정표 |
| ⑦ 순환금융 | matrix | — | funding_dependent_share=small, own_money_returns=no | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 별표 I 판정표 \| [IMPL-50] **영업외 비중은 F7 입력이 아니다.** F6 P4 전용이다 — 채점규칙 별표 I 351~ |
| ⑧ 비대칭 의존 | score | -4 | — | carried | legacy:v1.5 2026-09-02 |  |
| ⑨ 적자 깊이 | gate_inputs | — | fcf_trend=unknown, bep_retreat=no, buffer_erosion=no, direction_A=unknown, direction_B=unknown, coverage_comparable=yes, operating_result_reviewed=profit | new | 설계진행 2026-09-11 | 규칙 v1.5 ⑨ 적용표(추세·BEP·커버리지 비교 가능성) |

### Anthropic

| Factor | 종류 | 점수 | 입력 | 상태 | 검토 | 비고 |
| --- | --- | --- | --- | --- | --- | --- |
| ① 네트워크 | score | 4 | — | carried | legacy:v1.5 2026-09-02 |  |
| ② 게임체인저 | score | 5 | — | carried | legacy:v1.5 2026-09-02 | ~~C-03: 경로 매핑 미확정 — 승계 점수~~ C-03 확정(paths_with_generation_gap_5), 세대 격차는 판단 입력이라 |
| ③ Last Mover | criteria | — | imitation=partial, revenue_model=pass, acceleration=fail, door_closed=fail | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 ③ 판정표 |
| ④ 호황 이후 | score | 4 | — | carried | legacy:v1.5 2026-09-02 |  |
| ⑤ 아군 | grade | — | A=1, H=-1 | new | noble 2026-10-01 | [F5-IMPL-48] 체크리스트 19 적용 재판정(사용자 결정 ①). A +2→+1, F5 5→4. 두 모델 독립 일치 — C-13(Gemin |
| ⑥ 가격 | score | -3 | private=True | carried | legacy:v1.5 2026-09-02 | C-12: 비상장 정성 예외(TTM 보정·자본효율 근거는 원문) |
| ⑦ 순환금융 | score | -1 | — | carried | legacy:v1.5 2026-09-02 | C-09: 매트릭스 입력(환류 여부) 원문 없음 — 승계 점수 \| [IMPL-50] **영업외 비중은 F7 입력이 아니다.** F6 P4 전용이 |
| ⑧ 비대칭 의존 | score | -3 | — | new | worker(HANSOLJJ) — C-13 F8-ANTH-33 8ddb0ae 기반 2026-09-11 | F8-ANTH-33 반영(2026-09-11). **점수 -3 은 바뀌지 않았고 근거란만 바뀌었다.** 2차 증언(증권사 자료)을 1차 공시(A |
| ⑨ 적자 깊이 | gate_inputs | — | fcf_trend=unknown, bep_retreat=no, buffer_erosion=no, direction_A=unknown, direction_B=unknown, coverage_comparable=no, operating_result_reviewed=unknown, fcf_not_disclosed_reason=reason:anthropic.fcf_not_disclosed | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 ⑨ 적용표(추세·BEP·커버리지 비교 가능성) \| [FIX-53 3단계 라벨 정정] AWS $100B 라벨을 공시 문면(기존 약정 |

### Apple

| Factor | 종류 | 점수 | 입력 | 상태 | 검토 | 비고 |
| --- | --- | --- | --- | --- | --- | --- |
| ① 네트워크 | score | 5 | — | carried | legacy:v1.5 2026-09-02 |  |
| ② 게임체인저 | score | 2 | — | carried | legacy:v1.5 2026-09-02 | ~~C-03: 경로 매핑 미확정 — 승계 점수~~ C-03 확정(paths_with_generation_gap_5), 세대 격차는 판단 입력이라 |
| ③ Last Mover | criteria | — | imitation=fail, revenue_model=pass, acceleration=fail, door_closed=fail | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 ③ 판정표 |
| ④ 호황 이후 | score | 3 | — | carried | legacy:v1.5 2026-09-02 |  |
| ⑤ 아군 | grade | — | A=1, H=-1 | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 별표 G 판정표 |
| ⑦ 순환금융 | matrix | — | funding_dependent_share=small, own_money_returns=no | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 별표 I 판정표 \| [IMPL-50] **영업외 비중은 F7 입력이 아니다.** F6 P4 전용이다 — 채점규칙 별표 I 351~ |
| ⑧ 비대칭 의존 | score | -3 | — | carried | legacy:v1.5 2026-09-02 |  |
| ⑨ 적자 깊이 | gate_inputs | — | fcf_trend=stable, bep_retreat=no, buffer_erosion=no, direction_A=unknown, direction_B=unknown, coverage_comparable=unknown, operating_result_reviewed=profit | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 ⑨ 적용표(추세·BEP·커버리지 비교 가능성) |

### NVIDIA

| Factor | 종류 | 점수 | 입력 | 상태 | 검토 | 비고 |
| --- | --- | --- | --- | --- | --- | --- |
| ① 네트워크 | score | 2 | — | carried | legacy:v1.5 2026-09-02 |  |
| ② 게임체인저 | score | 5 | — | carried | legacy:v1.5 2026-09-02 | ~~C-03: 경로 매핑 미확정 — 승계 점수~~ C-03 확정(paths_with_generation_gap_5), 세대 격차는 판단 입력이라 |
| ③ Last Mover | criteria | — | imitation=fail, revenue_model=pass, acceleration=fail, door_closed=fail | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 ③ 판정표 |
| ④ 호황 이후 | score | 5 | — | carried | legacy:v1.5 2026-09-02 |  |
| ⑤ 아군 | grade | — | A=1, H=-2 | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 별표 G 판정표 |
| ⑦ 순환금융 | matrix | — | funding_dependent_share=large, own_money_returns=yes | new | 설계진행(리뷰 C codex 발견 · 사용자 결정) 2026-09-15 | 규칙 v1.5 별표 I 판정표 \| [IMPL-50] **영업외 비중은 F7 입력이 아니다.** F6 P4 전용이다 — 채점규칙 별표 I 351~ |
| ⑧ 비대칭 의존 | score | -3 | — | carried | legacy:v1.5 2026-09-02 |  |
| ⑨ 적자 깊이 | gate_inputs | — | fcf_trend=stable, bep_retreat=no, buffer_erosion=no, direction_A=unknown, direction_B=unknown, coverage_comparable=unknown, operating_result_reviewed=profit | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 ⑨ 적용표(추세·BEP·커버리지 비교 가능성) |

### Palantir

| Factor | 종류 | 점수 | 입력 | 상태 | 검토 | 비고 |
| --- | --- | --- | --- | --- | --- | --- |
| ① 네트워크 | score | 2 | — | carried | legacy:v1.5 2026-09-02 |  |
| ② 게임체인저 | score | 3 | — | carried | legacy:v1.5 2026-09-02 | ~~C-03: 경로 매핑 미확정 — 승계 점수~~ C-03 확정(paths_with_generation_gap_5), 세대 격차는 판단 입력이라 |
| ③ Last Mover | criteria | — | imitation=partial, revenue_model=partial, acceleration=pass, door_closed=fail | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 ③ 판정표 |
| ④ 호황 이후 | score | 3 | — | carried | legacy:v1.5 2026-09-02 |  |
| ⑤ 아군 | grade | — | A=1, H=-2 | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 별표 G 판정표 |
| ⑦ 순환금융 | matrix | — | funding_dependent_share=small, own_money_returns=no | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 별표 I 판정표 \| [IMPL-50] **영업외 비중은 F7 입력이 아니다.** F6 P4 전용이다 — 채점규칙 별표 I 351~ |
| ⑧ 비대칭 의존 | score | -3 | — | carried | legacy:v1.5 2026-09-02 |  |
| ⑨ 적자 깊이 | gate_inputs | — | fcf_trend=stable, bep_retreat=no, buffer_erosion=no, direction_A=unknown, direction_B=unknown, coverage_comparable=unknown, operating_result_reviewed=profit | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 ⑨ 적용표(추세·BEP·커버리지 비교 가능성) |

### SpaceX + xAI

| Factor | 종류 | 점수 | 입력 | 상태 | 검토 | 비고 |
| --- | --- | --- | --- | --- | --- | --- |
| ① 네트워크 | score | 3 | — | carried | legacy:v1.5 2026-09-02 |  |
| ② 게임체인저 | score | 4 | — | carried | legacy:v1.5 2026-09-02 | ~~C-03: 경로 매핑 미확정 — 승계 점수~~ C-03 확정(paths_with_generation_gap_5), 세대 격차는 판단 입력이라 |
| ③ Last Mover | criteria | — | imitation=partial, revenue_model=pass, acceleration=pass, door_closed=fail | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 ③ 판정표 |
| ④ 호황 이후 | score | 5 | — | carried | legacy:v1.5 2026-09-02 |  |
| ⑤ 아군 | grade | — | A=1, H=-1 | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 별표 G 판정표 |
| ⑦ 순환금융 | matrix | — | funding_dependent_share=small, own_money_returns=no | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 별표 I 판정표 \| [IMPL-50] **영업외 비중은 F7 입력이 아니다.** F6 P4 전용이다 — 채점규칙 별표 I 351~ |
| ⑧ 비대칭 의존 | score | -3 | — | carried | legacy:v1.5 2026-09-02 |  |
| ⑨ 적자 깊이 | gate_inputs | — | fcf_trend=unknown, bep_retreat=no, buffer_erosion=no, direction_A=unknown, direction_B=unknown, coverage_comparable=yes, operating_result_reviewed=loss | new | 설계진행 2026-09-11 | 규칙 v1.5 ⑨ 적용표(추세·BEP·커버리지 비교 가능성) \| [FIX-52 2026-09-15] v1.5 수치 줄에 인용 라벨, verifi |

### Tesla

| Factor | 종류 | 점수 | 입력 | 상태 | 검토 | 비고 |
| --- | --- | --- | --- | --- | --- | --- |
| ① 네트워크 | score | 2 | — | carried | legacy:v1.5 2026-09-02 |  |
| ② 게임체인저 | score | 3 | — | carried | legacy:v1.5 2026-09-02 | ~~C-03: 경로 매핑 미확정 — 승계 점수~~ C-03 확정(paths_with_generation_gap_5), 세대 격차는 판단 입력이라 |
| ③ Last Mover | criteria | — | imitation=fail, revenue_model=pass, acceleration=pass, door_closed=fail | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 ③ 판정표 |
| ④ 호황 이후 | score | 4 | — | carried | legacy:v1.5 2026-09-02 |  |
| ⑤ 아군 | grade | — | A=0, H=-1 | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 별표 G 판정표 |
| ⑦ 순환금융 | matrix | — | funding_dependent_share=small, own_money_returns=yes | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 별표 I 판정표 \| [IMPL-50] **영업외 비중은 F7 입력이 아니다.** F6 P4 전용이다 — 채점규칙 별표 I 351~ |
| ⑧ 비대칭 의존 | score | -2 | — | carried | legacy:v1.5 2026-09-02 |  |
| ⑨ 적자 깊이 | gate_inputs | — | fcf_trend=deteriorating, bep_retreat=no, buffer_erosion=no, direction_A=unknown, direction_B=unknown, coverage_comparable=unknown, operating_result_reviewed=profit | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 ⑨ 적용표(추세·BEP·커버리지 비교 가능성) |

### Oracle

| Factor | 종류 | 점수 | 입력 | 상태 | 검토 | 비고 |
| --- | --- | --- | --- | --- | --- | --- |
| ① 네트워크 | score | 3 | — | carried | legacy:v1.5 2026-09-02 |  |
| ② 게임체인저 | score | 2 | — | carried | legacy:v1.5 2026-09-02 | ~~C-03: 경로 매핑 미확정 — 승계 점수~~ C-03 확정(paths_with_generation_gap_5), 세대 격차는 판단 입력이라 |
| ③ Last Mover | criteria | — | imitation=fail, revenue_model=pass, acceleration=pass, door_closed=fail | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 ③ 판정표 |
| ④ 호황 이후 | score | 3 | — | carried | legacy:v1.5 2026-09-02 |  |
| ⑤ 아군 | grade | — | A=1, H=-1 | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 별표 G 판정표 |
| ⑦ 순환금융 | matrix | — | funding_dependent_share=large, own_money_returns=yes | new | 설계진행(리뷰 C codex 발견 · 사용자 결정) 2026-09-15 | 규칙 v1.5 별표 I 판정표 \| [IMPL-50] **영업외 비중은 F7 입력이 아니다.** F6 P4 전용이다 — 채점규칙 별표 I 351~ |
| ⑧ 비대칭 의존 | score | -4 | — | carried | legacy:v1.5 2026-09-02 |  |
| ⑨ 적자 깊이 | gate_inputs | — | fcf_trend=unknown, bep_retreat=no, buffer_erosion=no, direction_A=unknown, direction_B=unknown, coverage_comparable=yes, operating_result_reviewed=profit | new | noble 2026-10-01 | 규칙 v1.5 ⑨ 적용표(추세·BEP·커버리지 비교 가능성) |

### OpenAI

| Factor | 종류 | 점수 | 입력 | 상태 | 검토 | 비고 |
| --- | --- | --- | --- | --- | --- | --- |
| ① 네트워크 | score | 4 | — | carried | legacy:v1.5 2026-09-02 |  |
| ② 게임체인저 | score | 4 | — | carried | legacy:v1.5 2026-09-02 | ~~C-03: 경로 매핑 미확정 — 승계 점수~~ C-03 확정(paths_with_generation_gap_5), 세대 격차는 판단 입력이라 |
| ③ Last Mover | criteria | — | imitation=fail, revenue_model=fail, acceleration=pass, door_closed=fail | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 ③ 판정표 |
| ④ 호황 이후 | score | 4 | — | carried | legacy:v1.5 2026-09-02 |  |
| ⑤ 아군 | grade | — | A=1, H=-3 | new | 설계진행(C-13 A-GRADE-45 · NTM A-GRADE-45B 독립 일치) 2026-09-14 | [F5-IMPL-48] 체크리스트 19 적용 재판정(사용자 결정 ①). A +2→+1, F5 2→1. 두 모델 독립 일치 — C-13(Gemin |
| ⑥ 가격 | score | -4 | private=True | carried | legacy:v1.5 2026-09-02 | C-12: 비상장 정성 예외(TTM 보정·자본효율 근거는 원문) |
| ⑦ 순환금융 | score | -1 | — | carried | legacy:v1.5 2026-09-02 | C-09: 매트릭스 입력(환류 여부)이 판단에 복원되지 않았다 — 승계 점수. **[FIX-54 1단계 정정] 원문 부재가 아니다** — 채점표 |
| ⑧ 비대칭 의존 | score | -4 | — | carried | legacy:v1.5 2026-09-02 |  |
| ⑨ 적자 깊이 | gate_inputs | — | fcf_trend=unknown, bep_retreat=yes, buffer_erosion=no, direction_A=unknown, direction_B=unknown, coverage_comparable=no, operating_result_reviewed=loss, fcf_not_disclosed_reason=reason:openai.fcf_not_disclosed | carried | legacy:v1.5 2026-09-02 | 규칙 v1.5 ⑨ 적용표(추세·BEP·커버리지 비교 가능성) |

## 근거 자료

### Alphabet / Google

| 근거 ID | Factor | 종류 | 제목 | 발행시각(UTC) | 상태 | 관련성 |
| --- | --- | --- | --- | --- | --- | --- |
| EV-alphabet-001 | ⑨ 적자 깊이 | filing | [8-K 2026-06-04 · Items 1.01, 7.01, 8.01, 9.01](https://www.sec.gov/Archives/edgar/data/1652044/000119312526257724/d83560d8k.htm) | — | confirmed | (추론) 추론: 2026-06-04 8-K 의 Item 1.01 은 중요 계약 체결 공시이고, 이틀 전 Reuters 가 “Alphabet 이 AI 를 위해 $80B 를 조달하고 Berkshire 가 $10B 를 투자한다”고 보도해 이 계약이 그 자본 조달일 가능성이 높다. 그렇다면 ⑨ 의 완충(현금 + 확정 미인출 여신)이 커지는 사실이다. 알파벳 ⑨ 판단은 게이트 1(본업이 영업이익을 내는가) 통과, 게이트 2(최근 1년 잉여현금흐름이 마이너스인가)에서 흑자 +$53.27B 로 끝나며, 추세는 악화이고 완충은 현금 $242.47B·순현금 +$121.68B 로 표 최상위급이다. (선별 확신: 중간) |
| EV-alphabet-002 | ⑤ 아군 | news | [Alphabet Inc (GOOGL) Stock: Looking Beyond the $4.7 Billion EU Fine - Yahoo Finance](https://news.google.com/rss/articles/CBMingFBVV95cUxPbENHRFY1b0xxTEprUDBVX3dWcWY3a3Y5eDBuZ2luWUM2aHRRcHRFbmNKTEs0akhUNDl3YTVmWXhYMjhZQmNPSmRWaWgyQkEtbGpGN0JXOW52MWhVMUxOeHFWUzFyWktzOHo4Ty1pR3Y3d0lDR0Fvc1F2REk3YXlkQjFMQmpuOTJaM0RVcGEyTThYY19PMWNsSVBaZS1hdw?oc=5) | 2026-07-13T07:00:00Z | confirmed | (추론) 추론: EU 가 알파벳에 $4.7B 과징금을 매겼다는 보도다. 별표 C(적대는 수가 아니라 성격을 본다)와 별표 G(⑤ = 3 + 동맹 등급 + 적대 등급)에 따라 본업 수요를 건드리지 않는 벌금은 적대 등급 비용형(-1)의 재료다. 알파벳 ⑤ 판단은 동맹 등급 +2, 적대 등급 -1(비용형)로 4점이고, 같은 성격의 €403M 개인정보 과징금 보도(2026-09-28)도 후보에 있다. (선별 확신: 중간) |
| EV-alphabet-003 | ⑥ 가격, ⑨ 적자 깊이 | filing | [10-Q 2026-07-23](https://www.sec.gov/Archives/edgar/data/1652044/000165204426000071/goog-20260630.htm) | — | confirmed | (추론) 추론: 2026-07-23 10-Q 는 알파벳의 가장 최근 분기 보고서로, ⑨ 게이트 2(최근 1년 잉여현금흐름이 마이너스인가)·추세·완충과 ⑥ 의 네 잣대(P1 PER = 시가총액 ÷ 최근 1년 순이익, P2 EV/매출 = (시가총액 − 순현금) ÷ 최근 1년 매출, P3 매출 성장, P4 입력 신뢰도 보정)의 1차 원문이다. 알파벳 ⑨ 판단은 게이트 2 흑자(최근 1년 잉여현금흐름 +$53.27B)로 끝나되 설비투자 $132.40B 로 추세는 악화다. ⑥ 은 사람이 판단을 적지 않고 공시 관측으로 프로그램이 계산한다. (선별 확신: 높음) |
| EV-alphabet-004 | ⑤ 아군 | news | [Alphabet (GOOGL) Could Be 28% Undervalued Following Its Antitrust Win - simplywall.st](https://news.google.com/rss/articles/CBMiwwFBVV95cUxQcVV4ZjNsa1Y1OURzc1k5S2MtWmlBUnhQMDlRUnJ4MERxMjVOR19yLVZybDRpSldLWTNxVWliUEtOaFNSLW1PU1lwOWk1LWNaaHYyamNIYzh5eF9za0tPWGFVNklPSTVySnk0OVUxN2lkZDZzVW9xWmlUNGdKdnN1c25aM1g4T3BQb19OTlBPY2xpWUNma1FCYnZyaUJ2NTBuMlh1SGM4WFZmS0FtWnlfZG9zMV9HdkJvMzZXam9IeW8tR3PSAcgBQVVfeXFMTTZrMGRBNzVpMHRSZmZIQ2pkcDBkZTU3N29qN2FXTE5HVG5VQmxTZjJGcEJPSEMxMkpNaGVWU29HaUsyamFiR05iRWFDR0JVU2dFakNZazZiX3ctV2JlOFRRd0EyQXRsejh2OEVabHktMzFhdkI3b1B6WVZEOGRjN1ZsQ1ROTENIbVlmR19KOVpkRS1samEwLVRKRTNzaWpsTHRjZXJmTUxmMFJrQ19BVnlET1ZHWkxISjBGWm1LcWFEOUdFb1E3LTA?oc=5) | 2026-09-20T15:43:09Z | confirmed | (추론) 추론: 알파벳이 반독점 소송에서 이겼다는 2차 매체 제목이다. 알파벳 ⑤ 판단은 동맹 등급 +2, 적대 등급 -1(비용형)로 4점이고 적대 근거로 “DOJ+38개 주 검색 독점 항소 진행”을 쓴다. 이긴 사건이 그 검색 독점 사건이라면 적대 근거 문장이 낡았을 수 있다. (선별 확신: 낮음) |
| EV-alphabet-005 | ⑤ 아군 | news | [Google challenges European requirements on sharing search data - marketscreener.com](https://news.google.com/rss/articles/CBMi2gFBVV95cUxQVEltd1VsZ2JDZmJVcS1LeWpMU0l0b1ZOelNQNDk5eDRBdVl1ZmJoTGNuNVlaeE1VVVVhRzBfQ1Zja1YwR0FlYzh2NThBaXdEOG9Ud2xnRXZTNExRbF9KT29zdDFNaDVTbzF1bGwwcTNUaWRhODRwV29FZGwydVlDOUVMOW1pVkFZaEw2Q2xRaWJ5eG1XSHNNR0xQcXdpT0VSSDI2aU9TVWJCN3I5QUh2UnVCeS1aenhvaHlHRG9GZm1BaW1JMW9DelhWNWkzdnhrb0x3cGtERTQtQQ?oc=5) | 2026-09-30T06:51:00Z | confirmed | (추론) 추론: 구글이 EU 의 검색 데이터 공유 명령에 이의를 제기했다는 보도로, 규제기관과의 분쟁이라 ⑤ 적대 등급의 재료다. 별표 C(규제·소송은 져도 본업 수요가 유지되는 비용)에 따라 규제 적대는 기본이 비용형(-1)이다. 알파벳 ⑤ 판단은 동맹 등급 +2, 적대 등급 -1(비용형)로 4점이다. (선별 확신: 중간) |
| EV-alphabet-006 | ⑦ 순환금융 | news | [Anthropic IPO Filing Reveals a Major Vulnerability: Nearly 50% of Sales Flow Through Amazon and Google as - Benzinga](https://news.google.com/rss/articles/CBMiswJBVV95cUxOVFRiMVYwR3RjTVgwbXM3RmhVYmk1b2NlamJRTDF5OGFGMjh1bXVVTFNRMHhhSXBNbjdyMmdnUlhkMFBrSDl2THpVeXVFWEZZNWg3dVBCTEV6MC1fWUxlTkdkOUNRbHZ1WkYweEwzUk1XZ2RxVEpTeGpEZzYzVFoteHNYaTBZU2d3andTRGVocGEwM0ZQTGo5d2dKTm1qdWZkbE0wWWpQVkdqVkx5VFh1VEJfMVpWUVZ5QUFsSS1rWHhwdXY1bGRLZkZBbGVHZHNfeFZZRkVQaGJXU0s2VWRNMXp6UEJUcmRDR2x3Z0xBbDYtd0xNdEoyMDdfX2RWNXdxRTJYTVJwZGVYM1RRU0Z5ZV85SGJEanZuUGJGTW5FVU1WNW54RGNSQld1NTVPa0hqMXBJ?oc=5) | 2026-09-30T12:18:17Z | confirmed | (추론) 추론: Anthropic IPO 신고서(S-1)가 Anthropic 매출의 절반 가까이가 Amazon·Google 을 거친다고 밝혔다는 보도다. Anthropic 은 투자·부채로 지출을 대는 적자 고객이고 알파벳은 그 투자자라 별표 I(⑦ 판정: 내 매출을 내는 고객이 그 돈을 조달로 구했는가 × 내 돈이 고객을 거쳐 내 매출로 돌아오는가)의 재료이고, S-1 원문으로 구글 쪽 Anthropic 매출·약정 규모를 잴 수 있다. 알파벳 ⑦ 판단은 조달 의존 고객 비중 ‘작음’, 내 돈이 돌아옴 ‘예’로 판정표 -1 칸이다(Anthropic 투자금이 TPU·GCP 매출로 돌아오나 본업 대비 미미). (선별 확신: 중간) |
| EV-alphabet-007 | ② 게임체인저 | news | [Google announces Gemini 4 flagship AI model after months of delays - Reuters](https://news.google.com/rss/articles/CBMitwFBVV95cUxPa0kxM3JDazhISnQtVGJ1Q2phRmxPR2Mtb2R4X1dQX0U3TkVZLWV0YUZNSnRfQ25OQnRuWHpNczNHSzhCZFFkdHFCWEVXYUhuazBDLWJ0eV92WU9nMDR6Nnl5ZDRCOG5UdWtwNnpTNkVtS2NLejVrX1Y3eXFvbDRMc0Y2Q2hvN0Q5YTEzTVA3NDFLaHprbnpuNWVBejNPVUlKemJCSHZUcHZSVE9iNmt3TWxXMXFBWkU?oc=5) | 2026-09-30T22:16:26Z | confirmed | (추론) 추론: 구글이 몇 달 지연 끝에 최상위 모델 Gemini 4 를 발표했다는 Reuters 보도로, ② 의 성능 도약 경로(벤치마크에서 세대 격차를 만드는가)를 다시 볼 계기다. 알파벳 ② 판단은 기준선에서 승계한 4점이고 근거는 “Arena 텍스트 최고 9위, Gemini 3.8 Flash 로도 프론티어 순위 미변”이라, Gemini 4 가 독립 측정에서 프론티어에 서면 이 근거가 낡는다. (선별 확신: 중간) |

### Amazon / AWS

| 근거 ID | Factor | 종류 | 제목 | 발행시각(UTC) | 상태 | 관련성 |
| --- | --- | --- | --- | --- | --- | --- |
| EV-amazon-001 | ⑨ 적자 깊이 | filing | [8-K 2026-06-10 · Items 1.01, 2.03, 9.01](https://www.sec.gov/Archives/edgar/data/1018724/000110465926072140/tm2613616d4_8k.htm) | — | confirmed | (추론) 추론: 2026-06-10 8-K 에 Item 1.01(중요 계약)과 Item 2.03(직접 금융 채무 발생)이 함께 나와 사채 발행이나 신용 약정일 가능성이 높다. 확정 미인출 여신이면 ⑨ 완충(현금 + 확정 미인출 여신)의 직접 입력이고, 사채면 현금과 부채가 함께 는다. 아마존 ⑨ 판단은 게이트 2(최근 1년 잉여현금흐름이 마이너스인가)에서 -$11.6B 로 걸려 게이트 3(버티는 기간) 런웨이 9.95년(완충 $115.7B = 현금 $78.2B + 확정 미인출 여신 $37.5B ÷ 연 소진 $11.6B)으로 통과, 게이트 4(약정 커버리지) 1.856 으로 통과라 완충이 런웨이 계산에 실제로 들어간다. (선별 확신: 중간) |
| EV-amazon-002 | ⑥ 가격, ⑨ 적자 깊이 | filing | [10-Q 2026-07-31](https://www.sec.gov/Archives/edgar/data/1018724/000101872426000026/amzn-20260630.htm) | — | confirmed | (추론) 추론: 2026-07-31 10-Q 는 아마존의 가장 최근 분기 보고서로, ⑨ 게이트 2(최근 1년 잉여현금흐름이 마이너스인가)·게이트 3(현금 완충으로 버티는 기간)·게이트 4(남은 계약 매출 RPO 가 미개시 리스·구매약정을 덮는가)와 ⑥ 관측의 1차 원문이다. 아마존 ⑨ 판단은 게이트 2 에서 최근 1년 잉여현금흐름 -$11.6B 로 걸려 런웨이 9.95년과 커버리지 1.856(RPO 496,000 ÷ 미래 지출 약정 267,279, 2026-06-30 기준 관측)이 실제로 점수에 닿는다. ⑥ 은 사람이 판단을 적지 않고 공시 관측으로 프로그램이 계산한다. (선별 확신: 높음) |
| EV-amazon-003 | ⑤ 아군 | news | [Apple, Amazon face revived UK consumer lawsuit over product sales - Reuters](https://news.google.com/rss/articles/CBMiuAFBVV95cUxPSlNVR0NibnVhb1I5T3pCODVCVDUwTUJyeHFKdE9UYzNXcTZMYmF1Ty1LQmZaTnRSa3JNSGU0WVFwaGJtRDE0d3NDQ1lGQ2dvd3BBX3BjalVMUHdhSEptUGFYWG1CTTl2ZmlFZXlBa2d5eVY3Y2lFUHBsWVNGS21WOFJYcmtJYmFvVy1UZ0dDNWk4SDR5dFUzVmN4U3lEeWp6amJSUlZVQlZqdXA5OGNNd3B3ZVV5eWEz?oc=5) | 2026-09-28T21:58:47Z | confirmed | (추론) 추론: 영국 소비자 집단소송이 아마존(·애플)을 상대로 재개됐다는 Reuters 보도다. 별표 C(규제·소송은 져도 본업 수요가 유지되는 비용)와 별표 G(⑤ = 3 + 동맹 등급 + 적대 등급)에 따라 사업 구조를 건드리지 않는 개별 소송은 적대 등급 비용형(-1)의 재료다. 아마존 ⑤ 판단은 동맹 등급 +2, 적대 등급 -1(비용형)로 4점이다. (선별 확신: 중간) |
| EV-amazon-004 | ① 네트워크 | news | [AI agents are fighting over your shopping cart: Meta’s Muse blocked by Amazon and Walmart - NBC News](https://news.google.com/rss/articles/CBMiqwFBVV95cUxPZ2c5MVIxcTRLS25nNVdnNGVIcDhORmhFVDZaZHlGd0pmWjQ4MTNPcDBiLUh1RUFnbzhvMlRRTDk3UDR2Z0QtbDU0UXVFMzVaYWVnX0k4RWtzNE5DTms0RzZSd09PcXhGOTJvaHdQcFBxSEliNGY1V2Jtd01ITlRpQUQwLWdSb3RINmNBWWl1ejBaWVNXalQ3LVllMmxqZkFmTUs1R1NUb29OVGc?oc=5) | 2026-09-29T16:00:41Z | confirmed | (추론) 추론: 메타의 쇼핑 에이전트 Muse 가 아마존 소비자 채널을 거치려 했고 아마존(·월마트)이 이를 막았다는 NBC 보도다. ① 은 별표 A(회사의 모든 실질 채널 중 가장 강한 락인으로 매긴다)에 따라 아마존 소비자 락인 — “가격을 올려도 남는가” — 으로 매기는데, 제3자 에이전트가 그 채널을 우회하는 경로가 생겼다는 반대 방향 사례다. 아마존 ① 판단은 5점(Prime 2억+ 락인, Alexa+ 무료 개방, Bedrock AgentCore)이다. (선별 확신: 낮음) |
| EV-amazon-005 | ⑤ 아군 | news | [Bring near-Astra intelligence to everyday work with GPT-6.1 Sol on Amazon Bedrock - Amazon Web Services (AWS)](https://news.google.com/rss/articles/CBMixwFBVV95cUxOUWc5Z2JxcEpSSkZRZ3YyZVJ6R3ZNdjZya0hod1hHLXJyX2Fodk1iR08ta1phMFFlUmw4aU13ZGt4aFAyaFdpeWlobUYweF90c3YwcTZMYUt5T1o5dmR1NW9Xc1RGNjZEMWJ4MXVvakxjdGhzSEFDbFVld2tiSEhxd25vQ2NGQ3NLNE43MnA4Y1hYV01oUTh2enM2U0lXMjh6OTBmNFBzSGgxV0tvZmxralJBQTR5VGxlTl9udl9FSm1DOGhodFJF?oc=5) | 2026-09-29T19:34:14Z | confirmed | (추론) 추론: AWS 가 경쟁 모델사 OpenAI 의 최신 모델 GPT-6.1 Sol 을 Bedrock 매대에 올렸다는 AWS 1차 발표로, 별표 G 동맹 등급 +2 조항 가운데 “경쟁사까지 내 매대에 편입했다”를 뒷받침한다. 아마존 ⑤ 판단은 동맹 등급 +2(18개사 100+ 모델 매대, Anthropic 최대 $25B), 적대 등급 -1(비용형)로 4점이다. (선별 확신: 중간) |
| EV-amazon-006 | ④ 호황 이후 | news | [Synopsys and Amazon Announce Strategic, Multi-year IP Agreement for Custom Silicon; Collaboration Also Extends to Cloud and AI-Powered Engineering - PR Newswire](https://news.google.com/rss/articles/CBMipwJBVV95cUxOUmRXYjFSSHRyRkNCZk55OC1nMVFLQ1hvMHlWRlZFMVFfMGkxNzdXQXBNM2tzbXhRZHJvUGZKWmNlblJhRzV4TnFqXzB4d0JXaVBHSngxZkFaTF8xaHc4THNKVkZYWmxwYTFneE50WjJoSG1sdVlnR3JBT2dOeHcwd1dQYlB1MFU0blp6QV9Ha1lMUXJNSWNGMERKMEVDY1p1SGtmd3hVVC1xdXp2Z2NuWTlWYWJBaUZXcS1FUGhRa0N3QjlnVXhSenh2QnlVZkIwV1ZHVnBwbzdsNlV4ek9zdVFxa2pWa1lJT2xPeXg0U1M5bFF4enJHR3BkMGRUU1RZUzNpLWhLSjFMdFp1ZWVjM0ppcXpGcU1URWJ3STZUMGswbEl6V0RN?oc=5) | 2026-09-30T13:00:00Z | confirmed | (추론) 추론: AWS 가 Synopsys 의 칩 설계 IP 를 다년 계약으로 산다는 양사 공동 보도자료다. 별표 H(돈 주고 사는 관계는 동맹이 아니다)에 따라 조달이라 ⑤ 동맹이 아니고 자체 칩 역량의 재료라 ④ 에 배정하지만, ④ 는 출하와 사업 부문만 세므로 설계 IP 계약 자체는 근거가 되지 않는다. 아마존 ④ 판단은 5점(AWS +36.7%, AI·칩 사업 각각 런레이트 $25B+, 리테일·광고·물류, 로보틱스)이다. (선별 확신: 낮음) |
| EV-amazon-007 | ⑦ 순환금융 | news | [Anthropic Plans to Spend $518 Billion on Cloud and Data Centers. More Than $100 Billion Is Already Promised to Amazon. - The Motley Fool](https://news.google.com/rss/articles/CBMi9gFBVV95cUxPV1VyZWNDUXhZRmxTa0FTZVgyUGRON3M4ZGFRSEltazdOMDFyd3AwRk9fR2pPYk1FM2dIN05VTjViVXdoMko5NklabHd0ZU15bkNpMmZiTjZrWXFxNllzdlNmUTRONnE0dTc0UEJNOVIxVlFsMjNvRk1DcnQtbkZPeHZWVkRNSEVCdWFJZTB2RkdxRFZWQzZhbEZiVHowRlZsLURZSUlfckpxWkVvVmUxZlhzMGNXdHhtQ25UWmhGVzNrSGt3eVRBazJOeUhEODBUWGNaMnRhYzdpb3FfWWZjRDRfMXpXcDdhWVBrdm1TYS12TnNlb3c?oc=5) | 2026-10-01T01:37:00Z | confirmed | (추론) 추론: Anthropic 이 클라우드·데이터센터에 $518B 를 쓸 계획이고 그중 $100B+ 가 이미 아마존에 약속됐다는 보도다. 아마존은 Anthropic 의 투자자이고 Anthropic 은 투자·부채로 지출을 대는 적자 고객이라 별표 I(⑦ 판정: 내 매출을 내는 고객이 그 돈을 조달로 구했는가 × 내 돈이 고객을 거쳐 내 매출로 돌아오는가)의 재료이고, $100B+ 가 AWS 백로그($496B)의 큰 몫이라면 지금 판정을 다시 볼 이유다. 아마존 ⑦ 판단은 조달 의존 고객 비중 ‘작음’, 내 돈이 돌아옴 ‘예’로 판정표 -1 칸이다(Anthropic 투자→AWS 매출 환류가 본업 $776B 대비 미미). (선별 확신: 중간) |

### Meta

| 근거 ID | Factor | 종류 | 제목 | 발행시각(UTC) | 상태 | 관련성 |
| --- | --- | --- | --- | --- | --- | --- |
| EV-meta-001 | ⑥ 가격, ⑨ 적자 깊이 | filing | [10-Q 2026-07-30](https://www.sec.gov/Archives/edgar/data/1326801/000162828026050705/meta-20260630.htm) | — | confirmed | (추론) 추론: 2026-07-30 10-Q 는 메타의 가장 최근 분기 보고서로, ⑨ 게이트 2(최근 1년 잉여현금흐름이 마이너스인가)와 ⑥ 관측의 1차 원문이다. 메타 ⑨ 판단은 게이트 2 흑자(최근 1년 잉여현금흐름 +$40.98B)로 끝나지만 추세는 악화다 — 분기 잉여현금흐름이 +$780M 으로 -91% 줄었고 설비투자 계획이 연 $130~145B 라 상단 집행 시 마이너스로 바뀔 수 있어, 이 10-Q 가 다음 분기 확인의 기준점이다. ⑥ 은 사람이 판단을 적지 않고 공시 관측으로 프로그램이 계산한다. (선별 확신: 높음) |
| EV-meta-002 | ④ 호황 이후 | news | [Meta launches enterprise AI business seeking to cash in on vast spending - Financial Times](https://news.google.com/rss/articles/CBMihAFBVV95cUxQYXl4S1J5V0N4UWpZbHpnUlFaQWlXWWdjZFd0ZVBOSzJXS2VQZndsTXgyM29XV083LVlySlk5eGNxTWRXUjBGdkZHa3djdVJ6MDlVNDFKWlFfbnlHeW8tRi1Kd25jQlNYanFTQ3NhMFN5aWFFaHRWV21DR01mSEtxSzRyaDc?oc=5) | 2026-09-28T15:54:34Z | confirmed | (추론) 추론: 메타가 광고 밖 새 사업으로 기업용 AI 플랫폼을 출범했다는 FT 보도다. ④ 는 출하와 사업 부문만 세고 새 사업은 매출이나 고객 배치가 생길 때 근거가 된다. 메타 ④ 판단은 3점이고 근거는 “AI 광고 최적화로 매출 +28%, 그러나 광고 의존 약 98%”다. (선별 확신: 낮음) |
| EV-meta-003 | ⑤ 아군 | news | [These 3 AI Stocks Are Poised to Be Big Winners from Amazon's Choice to Block Meta's Muse - The Motley Fool](https://news.google.com/rss/articles/CBMimAFBVV95cUxNbG9QN3lOMm13amhKTmp6djZUMVVTallpWWJoRTJ0a003Tkd4OEozY19Mdzc4WVpZZTNHM1VmUzR6WkZXakhucEtPb0QxTWgyenFEb0VnZEJjSFZ5MnZhQkREUG40M0lVMFRwd3gzckxtbnRMRDB3ZzUtUi1xY19YcHl0WXB1UmQ0NkxSZUV0cnhZUTJpOWEzVg?oc=5) | 2026-09-30T08:30:00Z | confirmed | (추론) 추론: 아마존(·월마트)이 메타의 Muse 쇼핑 에이전트를 막았다는 사실이 담긴 의견 기사 제목이다. 시장 일부 차단은 별표 G(⑤ = 3 + 동맹 등급 + 적대 등급)의 적대 등급 비용형(-1: 벌금·개별 소송·시장 일부 차단, 사업 구조는 안 건드림)에 해당한다. 메타 ⑤ 판단은 동맹 등급 +1(수백만 광고주 생태계), 적대 등급 -1(미성년자 소송·EU 벌금, 비용형)로 3점이다. (선별 확신: 낮음) |
| EV-meta-004 | ③ Last Mover | news | [Exclusive: Meta’s Muse Tops 3 Million Weekly Users - The Information](https://news.google.com/rss/articles/CBMikwFBVV95cUxPZUlsQkdDcHFFRnVIeXo3anBjZ2RfcW1XcEk3N1VRd3NtTkUyaUNBWmNGZU5KTGNaemxIMGlCTHZfcG1GQl93OFJQbWhKbF9JbGJpM3QxTDdOLW1MWEdwQVpSaDZscElPZDRaNm5NU3h4S0htdEduODQwVVlzbWFiQ2hyMXY1M1NUc2lUX0hUUExsYjg?oc=5) | 2026-09-30T22:48:00Z | confirmed | (추론) 추론: 메타의 새 AI 앱 Muse 주간 사용자가 300만을 넘었다는 The Information 단독 보도다. 메타 ① 은 이미 소비자 채널 락인 최고 칸(5점, 30억+ 사용자)이라 별표 A(가장 강한 채널로 매긴다)에 따라 새 앱 지표로 움직이지 않고, ② 패러다임 적응 경로는 메타 ② 판단에서 이미 통과로 적혀 있어, 이 카드는 후발 서비스가 빨리 크는 소식으로서 ③ 후발 가속도(성장률이 오르는가)에만 쓴다(2026-10 라벨링 사람 판정). 메타 ③ 판단은 별도 수익모델 ✅, 모방 불가능성 ⚠️, 후발 가속도 ⚠️(“AI 매출 미공시, 채택 증거 아직 없음”), 문이 닫힌 증거 없음이다. (선별 확신: 중간) |
| EV-meta-005 | ⑤ 아군 | news | [Meta counted Mark Zuckerberg’s $4.1B stock payout as research pay to claim a $355M tax break — and the IRS wants it back - Yahoo Finance](https://news.google.com/rss/articles/CBMimwFBVV95cUxONnhRUFNkRjFmS1pmRG91UWkzcTJ2X2JtNV9RQm44aE4yZjJDVkYxN1AxWWZRZElwNHZWMkkxNVYxMVMyWWt6bGxJQndvZnozX0RDX3MzQWM5TzU1WDVhYlltZ1ZTdURoTkZlVHFwcmMxMXdQdmtwZG1SaF83UERkTF9uT3pjamQ1OXI2bWJlR2d1RHZNdkVhemh3Yw?oc=5) | 2026-10-01T04:05:00Z | confirmed | (추론) 추론: 미 국세청(IRS)이 메타가 저커버그 주식 보상 $4.1B 를 연구비로 넣어 받은 $355M 세액공제를 환수하려 한다는 보도다. 세무당국과의 분쟁은 별표 G 적대 등급의 비용형(-1: 벌금·개별 분쟁, 사업 구조는 안 건드림) 재료다. 메타 ⑤ 판단은 동맹 등급 +1, 적대 등급 -1(비용형)로 3점이다. (선별 확신: 낮음) |

### Microsoft

| 근거 ID | Factor | 종류 | 제목 | 발행시각(UTC) | 상태 | 관련성 |
| --- | --- | --- | --- | --- | --- | --- |
| EV-microsoft-001 | ④ 호황 이후, ⑥ 가격, ⑨ 적자 깊이 | filing | [10-K 2026-07-29](https://www.sec.gov/Archives/edgar/data/789019/000119312526323660/msft-20260630.htm) | — | confirmed | (추론) 추론: 2026-07-29 10-K 는 마이크로소프트 FY2026 연간 보고서로 ⑨(잉여현금흐름·설비투자)·⑥(PER·매출 성장 관측)·④(세그먼트 매출·RPO)의 1차 원문이다. 마이크로소프트 ④ 판단은 4점(Azure 6월 분기 $29.42B +42%, AI 런레이트 $37B, RPO $678B)이고, ⑨ 판단은 게이트 1(본업 영업이익) 통과·게이트 2(최근 1년 잉여현금흐름) 흑자로 끝나며 추세는 안정(설비투자 하향)이다. ⑥ 은 사람이 판단을 적지 않고 공시 관측으로 프로그램이 계산한다. (선별 확신: 높음) |
| EV-microsoft-002 | ② 게임체인저 | news | [Introducing the new Copilot with Home, Code and Autopilot - The Official Microsoft Blog](https://news.google.com/rss/articles/CBMiowFBVV95cUxQdnBldHlfWlM4TjV6Y2NWTlNMUjFzQ0ZUa2M5MTkwX2pkaHNhbXc0TDJJbUs4bmxHZ3RSXzQ3SlFXd3VuemZFaWJFekFneHRNUDBNb2ZyTmgxVWFqR1BySzZRelo1ZjdTWXhuYjlGc1dOQm9JNTJMWHNlSHY0Z2FxS3hhMnp1OGVqWFdMTGlFYXZoZV9mc29ySDhGdUlZOW1RM3Rv?oc=5) | 2026-09-25T12:15:07Z | confirmed | (추론) 추론: 마이크로소프트가 에이전트(Autopilot)·코딩(Code)을 묶은 새 Copilot 을 냈다는 공식 블로그 발표로, ② 의 패러다임 적응 경로(남이 바꾼 판 — 에이전트·추론·코딩 — 에 빨리 올라타는가)를 다시 볼 계기다. 마이크로소프트 ② 판단은 기준선에서 승계한 3점이고 근거는 “Maia 200 배포 물량 미확인, Arena 상위권에 자체 모델 없음, OpenAI·Anthropic 양쪽 조달”이다. (선별 확신: 낮음) |
| EV-microsoft-003 | ⑤ 아군 | news | [OpenAI takes on Microsoft with the launch of what feels a whole lot like ChatGPT's own office suite - TechCrunch](https://news.google.com/rss/articles/CBMizgFBVV95cUxPMThVYXNHdk44dXhHc1F0NHZ5SzJYd2FBN3BWSHJ3R1pXMjMySWlfbTQwaVRxc2l3QkFGUDJLamZ2Yk1zVlBFekl6SVRlbF9kc0lpWEdjQVBHUzhETUNMQm0waVdPSmlOLTh6MlhNZ2pmbFZBR0hpQnYtQUhVX2tiTzBtbEp0YkRuQjViX0Z2eGFpTzVwMFlOd010STAyeVRKVHhlWVNnZ0xpYTcxVDlxM3dha2tjbXp3SE9QRGhfTkdNNlJLQm9sOTh4dHdpQQ?oc=5) | 2026-09-29T17:45:51Z | confirmed | (추론) 추론: 마이크로소프트의 최대 동맹 OpenAI 가 M365 와 겹치는 오피스 제품을 냈다는 TechCrunch 보도다. 동맹 상대가 업무 채널의 경쟁자가 되는 사건이라 ⑤ 적대 근거(“OpenAI 긴장”)가 얼마나 큰지 다시 볼 재료다. 마이크로소프트 ⑤ 판단은 동맹 등급 +2(OpenAI 지분 27% + Anthropic Azure $30B 약정), 적대 등급 -1(비용형: OpenAI 긴장·Azure 독점 소멸)로 4점이다. (선별 확신: 중간) |

### TSMC

| 근거 ID | Factor | 종류 | 제목 | 발행시각(UTC) | 상태 | 관련성 |
| --- | --- | --- | --- | --- | --- | --- |
| EV-tsmc-001 | ⑧ 비대칭 의존, ⑨ 적자 깊이 | filing | [6-K 2026-08-14](https://www.sec.gov/Archives/edgar/data/1046179/000104617926000541/tsm-fsx20260814x6k.htm) | — | confirmed | (추론) 추론: 2026-08-14 6-K 는 파일명(tsm-fsx)으로 보아 2분기 재무제표 제출이고, 이번 창에서 가장 최근 재무 자료다. ⑧ 고객·지역 집중과 ⑨ 잉여현금흐름 추세의 1차 자료다. 지금 TSMC ⑧ 판단은 -4(첨단 캐파가 대만에 집중, NVIDIA 단일 고객 19%, HPC 66%, ASML EUV 단일 공급)이고, ⑨ 판단은 영업흑자·잉여현금흐름 흑자·추세 안정으로 감점이 없다. (선별 확신: 중간) |
| EV-tsmc-002 | ② 게임체인저 | news | [ASML and TSMC Announce Initiative to Pioneer Industry Transition to Large-Format Photomasks for High NA EUV - pr.tsmc.com](https://news.google.com/rss/articles/CBMiTkFVX3lxTE9nSmxRNFVNTTQ1WUhsaGQ2NWx5OXE4eXlFRGVsMHFnNFk3c0c1b3JYVzlfeEtkQ01PX2tkTE4tbHo2RFIwcGYyTWl0NVUxQQ?oc=5) | 2026-09-08T07:00:00Z | confirmed | (추론) 추론: ASML 과 함께 High NA EUV 용 대형 포토마스크로의 업계 전환을 이끌겠다는 TSMC 발표다. 마스크 규격이라는 산업 인터페이스를 정하려는 시도라 ②(신기술 게임체인저)의 세 경로 가운데 표준 선점 경로의 후보다. 지금 TSMC ② 판단은 성능 도약 경로(N2 양산)로 5점, 최상단이다. (선별 확신: 낮음) |
| EV-tsmc-003 | ⑥ 가격 | news | [TSMC August 2026 Revenue Report\|Taiwan Semiconductor Manufacturing Company Limited - pr.tsmc.com](https://news.google.com/rss/articles/CBMiTkFVX3lxTE1aTzR4TnFXdW1kTFFUa2l1ck9vOWlFMUM3ZXBZdnhsODZsVDZ6NHB5TzY1ZWg1QUlOMzJBNS1FaDNhMUJVa2ZfU1ZwOUhOdw?oc=5) | 2026-09-10T07:00:00Z | confirmed | (추론) 추론: TSMC 가 직접 낸 2026년 8월 매출 보고다. 흑자 기업의 매출 공시는 ⑨ 가 아니라 ⑥ 매출 성장 잣대(P3, 최근 1년 매출 ÷ 그 전 1년 − 1)의 재료다. 지금 TSMC ⑥ 은 20-F 제출사라 연간 수치로 계산하는 트랙이고, 매출 성장 입력은 2025 연간 매출 1,214억 달러, 성장률 약 32% 로 '30% 이상' 구간(감점 없음)이다. (선별 확신: 높음) |
| EV-tsmc-004 | ② 게임체인저 | news | [Taiwan Semiconductor Manufacturing (TSM) Starts Commercial 2 Nm Production - simplywall.st](https://news.google.com/rss/articles/CBMi7AFBVV95cUxNblhVN1A1bzdQekU0cGtoSUZRb0QzOU9mbk16amtyNVFSUy1WY044QmlUcFRSQWlISHM5aUZPWXNwMTRXa0lCNGg5aHlNNHBSS1lNUHNXR2VJQWNLbWpEMExNdjVhVjFpVDZ0b2RhOWZoNGt6bzd0RGx0eUhiTGN2SUp6RE9nMGJiUVV5Y1IzREpjY0tQTXpySVJtYV9MWjVQdVdmWTdsbS1RR3d1SXNpOXZaN1FBdFhYT1MyaExaZWtWeTc0bDlNUnZsb3Q4WHNfVFJhUFhxZmRCZTV3NzlwRFpVT05KQWVaNWFJOdIB8gFBVV95cUxPWk9pZE9KSExncUhORVAycGlFbWFNZ0hTTEFfX000Tzd0NzhNNzk5OFBTLUN1dnVxQnA1aXhDV051N09DTnZPUHVpTThrejAyTkJ2UjYwUjlmS1JDMFVHVk5Yd3hxbmtyX2FNZ2lJRDlGZ1RzZ3BBcE1XdGRPZy00Z2V6QkY2Y0RJcDhiYUZfckJ4N2o5MTM1anpicUROV1FtdW1mNTROakdJVmw5Wk1kZVR6eGwxYUVsejFRdVlCeldLeUdvTVRnMFpWYWpoV28yYWljZWFvbGthbFlZNG5SaEhNR19VTF9falBpOGdBSUFKUQ?oc=5) | 2026-09-18T15:31:56Z | confirmed | (추론) 추론: 2나노 상업 양산 시작은 출하된 공정 도약이라 ② 성능 도약 경로의 재료다. 지금 TSMC ② 판단은 5점(최상단)이고, 근거에 'N2 양산 시작(2분기 웨이퍼 매출 3%, 하반기 가파른 증산)' 이 이미 적혀 있다. (선별 확신: 중간) |
| EV-tsmc-005 | ① 네트워크 | news | [Why Is Taiwan Semiconductor Manufacturing (TSM) Raising Wafer Prices By 3% To 6%? - Yahoo Finance](https://news.google.com/rss/articles/CBMiqwFBVV95cUxQeGI1RTFZT1FHOHk3dGNwd2xoRXd1RlYwUm9LVENPaDlBVGtoWnMzMHlESkhpSzlZSjYzNGdNNklzREY2WktxRzFMTnFkSE9STDdCQ3hwaTF1c1NzUlpTT01ZMnliWVpkRkVoNG9kbFl2N3VmOE9Ia1Q1bm9tOFBrNDR6ZUYtTF9tX1BtVW1NU0xSU3B6UFcwUnJmc3QwRWUwRzF1ZlF6T0pzUU0?oc=5) | 2026-09-25T00:17:00Z | confirmed | (추론) 추론: 웨이퍼 가격 3~6% 인상은 ①(네트워크 효과)의 판별 질문 '가격을 올려도 남는가' 를 직접 시험하는 사건이다. 지금 TSMC ① 판단은 2점이고, 별표 A(① 은 회사의 가장 강한 실질 채널로 매기며, 최종 사용자 접점이 없는 부품 채널은 2점이 상한)에 따라 이미 상한에 닿아 있다. (선별 확신: 낮음) |
| EV-tsmc-006 | ③ Last Mover | news | [AI demand powers Foundry 2.0 revenue 25% as TSMC leads 42%, Samsung 4% - CHOSUNBIZ - Chosunbiz](https://news.google.com/rss/articles/CBMiekFVX3lxTE96bVdZamtPbDlFNldVOWtjMmpyS0hWWjBvRUZpVEpIczVXanl4VDNXdDlEclRNRmxERmN3VFhBNlVaTGxleWhGekJXUG9BQWhWbEFSbTFxaWV5NmR1X21yX0tfcU5GbmxiR1NTX2VPQlkydkQ0YVFaWGlR0gGOAUFVX3lxTE44NjcxWVZock95UGVja2ppa1hsNUJpdmJkaS12bmtHR3ZreGFzTnZFU0NRZHJpZC15ZWY3MXlheXdjM29MVnM5MXZ4c29xWER3bTE2YTFLdmFxeFFfNjB5ODRoVktkUXZUTS1XNzBHeXdwTzA3eFh5ekRnLXhESjg4VnZLY1hUN3VyWVZ0WkE?oc=5) | 2026-09-30T08:42:00Z | confirmed | (추론) 추론: 패키징·테스트까지 넣은 'Foundry 2.0' 시장에서 TSMC 42%·Samsung 4% 라는 점유율 수치다. 경쟁사가 수율·규모를 따라오지 못한다는 ③(Last Mover)의 모방 불가 기준 근거다. 지금 TSMC ③ 판단은 모방 불가·후발 가속도 통과, 별도 수익모델·문 닫기 실패다. (선별 확신: 중간) |
| EV-tsmc-007 | ⑤ 아군 | news | [Lip-Bu Tan calls TSMC a partner rather than a rival - digitimes](https://news.google.com/rss/articles/CBMijAFBVV95cUxNWW82ZlFIOG9kMHZqdnlsYkxCOWlOeE1Fb01XeEoxYWtkYjRHck04R2ZxdEJ6TzhBRTRTNFZkUlI5SEp2S0ttN0FXWVk5aFdRSXFzM3UxcU0zLTF5TjNvNWhaOHZXeVVjLThiUjlZQlA3Skx0NXc3ODB6dTFkVnNzYXpHSkREbjNOc2UxMQ?oc=5) | 2026-10-01T00:11:53Z | confirmed | (추론) 추론: Intel CEO 가 TSMC 를 경쟁자가 아니라 파트너라고 했다는 digitimes 제목이다. Intel 은 TSMC 의 경쟁 파운드리(Intel Foundry)를 가진 회사이므로, Intel 이 TSMC 공정을 쓰는 고객이라면 ⑤ 동맹 등급의 '경쟁사까지 내 공정에 편입했다' 조항에 닿는다. 지금 TSMC ⑤ 판단은 동맹 등급 +1, 적대 등급 -1(Intel Foundry·관세)로 3점이고, 2026-09-15 엄격 재판정은 TSMC 에 편입된 경쟁사가 NVIDIA 의 경쟁사뿐이고 TSMC 자신의 경쟁사가 들어온 근거는 없다고 보았다. (선별 확신: 낮음) |

### Alibaba

| 근거 ID | Factor | 종류 | 제목 | 발행시각(UTC) | 상태 | 관련성 |
| --- | --- | --- | --- | --- | --- | --- |
| EV-alibaba-001 | ⑤ 아군 | news | [Alibaba Fined €550 Million for Illegal Sales in Biggest DSA Case - Bloomberg.com](https://news.google.com/rss/articles/CBMitAFBVV95cUxNNEx5ZU9YUEhCT3BfTVVfWERISExVMHRGZ0NjaFUtNHZZMmozVDRvYlRxTlZ0UWl2SWJlNHl0YXA5TEpWVmYzSzVobm9ZVEtjNDFlSlJBdUJGOWZGN3pWZkxHWV9sWThHVl9pUGVWRUNSSl9DUWVJamRvbzRmOUVISW9zQlp4dWstbnRGMkRUMmhlTlR5ZVBCNzRENkZpakVxZ2VTQVhHTXBmbjB6XzVyS3VtRDg?oc=5) | 2026-07-20T07:00:00Z | confirmed | (추론) 추론: EU 가 디지털서비스법(DSA) 위반으로 알리바바에 €550M 벌금을 매겼다는 보도다. 규제기관의 벌금은 ⑤ 아군 확보의 적대 쪽 재료이고, 판매 금지가 아니라 벌금이라 사업 구조를 건드리지 않는 비용형 적대(벌금·소송·조사처럼 본업 수요는 남는 적대)에 해당한다. 알리바바 ⑤ 판단은 동맹 등급 +1(Apple 중국 아이폰 탑재), 적대 등급 -1(비용형)로 3점이다. (선별 확신: 중간) |
| EV-alibaba-002 | ② 게임체인저 | news | [Alibaba unveils its largest AI model yet, DeepSeek's latest model is ultra-low cost - Reuters](https://news.google.com/rss/articles/CBMi0wFBVV95cUxObUlCNHp6dVFoTEtqbkF3aFZqaVNUUVRJd0dicUhkb2tidzdkUWg0OVp1SU94aFJ1dmdkbDZIZGxMQVNWMm5vYXNKR0JicHNwZWRVX25ZY0hHaTNVUVdIWGdBNERsS3hDT29CdzlydEFGbFJzblgyempKcjljLVFELTVPRjdHVnRrOVRmQUs5QWVFQlg3aWVET1lNcDE4R2wwSC1vazRDaTNTZFhURm9qUGFfWGE5Sk1pMHNBUWx3TG85S1lZSWV4TUJxRU11UVhMR2Iw?oc=5) | 2026-08-03T07:00:00Z | confirmed | (추론) 추론: 알리바바가 자사 최대 AI 모델을 공개했다는 보도다. 신모델 공개는 ② 신기술 게임체인저의 성능 경로(프론티어 모델과의 성능 격차)를 다시 볼 계기일 뿐이고, 벤더가 낸 벤치마크는 방증이다. 알리바바 ② 판단은 4점이며, R&D·적응 속도는 최상위지만 표준 주도력이 없고 HLE 43.6% 로 프론티어에 못 미친다고 적었다. (선별 확신: 낮음) |
| EV-alibaba-003 | ⑥ 가격, ⑨ 적자 깊이 | news | [Alibaba profit falls 75% after ramping up AI infrastructure spending - Reuters](https://news.google.com/rss/articles/CBMipAFBVV95cUxON2tiUnl3QjZwYUtIMS10blVfb0hldWgzc21OVk40S3lIV0g1LTdiakVxYkt5Wk9BTUdOQ3FwTEpVV1JwRi05aGRVR1B0c1Bya29xMGpxdEZiR255eEdDdUZURlJtbXJ6QUpiQktIT0hGSEF4ZkV3Ry0zNlV2aXhUYzFZVVJWMllsQ3FFZ1FiMGk0bUNlTHhHcnBNMlMyUmJTYTdSTg?oc=5) | 2026-08-20T07:00:00Z | confirmed | (추론) 추론: 알리바바 6월 분기 실적에서 AI 인프라 지출 확대로 이익이 75% 줄었다는 보도다. 이 분기는 지금 계산에 쓰는 최근 1년(TTM) 창(2025-04-01~2026-03-31) 밖이라, 창을 옮기면 ⑥ 의 P1(최근 1년 이익 기준 PER)·P3(매출 성장) 입력과 ⑨ 게이트 2(최근 1년 잉여현금흐름이 마이너스인가)의 값이 바뀐다. 알리바바 ⑨ 판단은 -3 이다. 게이트 1(본업이 영업이익을 내는가)은 통과했고, 최근 1년 잉여현금흐름이 -US$7,226M 이라 게이트 2 에서 깎였으며, 게이트 3(완충으로 버티는 기간)은 런웨이 3.10년으로 임계 3년을 넘겨 유지됐고, 게이트 4(약정 대비 계약 수입)는 계약 수입을 회사가 공시하지 않음이 확인돼 한 칸 깎였다. ⑥ 은 판단이 아니라 공시 수치에서 계산하는 값이다. (선별 확신: 중간) |
| EV-alibaba-004 | ⑨ 적자 깊이 | news | [Alibaba shares slide after $10.2 billion AI share sale offered at sharp discount - Reuters](https://news.google.com/rss/articles/CBMizgFBVV95cUxPbmJDLXh4Z1Q1TU1xaFVKallDYkY5TmdpYUlUTkpxZ1BGS09ReGNfSlJTd0F4OGNKYndTUndKRmRVaU9DUUNfWVc0b1FyV211dFQwRTdHZS1CNExRd3owLU93WEUtcWZ6YkQyOThYMmZlNDFJM01RbjhOenhvaFptLW44S2tmR2pPSjJOWlhnUHNhUy02Wm1Td0gyY3F1QzhyQk42YWhnNl9UUXBxY0Z3bzhUSm1tRjhTZ3YyM3dVU21ibERiRzMtQ3B6eTlfZw?oc=5) | 2026-08-24T07:00:00Z | confirmed | (추론) 추론: 알리바바가 AI 투자용으로 $10.2B 규모 신주를 할인 발행했다는 보도다. 받은 돈은 다음 대차대조표 기준일부터 ⑨ 의 완충(현금 + 확정 미인출 여신)에 들어간다. 알리바바 ⑨ 판단은 -3 이고, 이 증자를 이미 한 줄로 적어 두었지만 현금 관측 기준일(2026-03-31) 뒤 사건이라 지금 완충 US$22,398M 에는 들어 있지 않다고 밝혔다. (선별 확신: 중간) |
| EV-alibaba-005 | ⑤ 아군 | news | [US Says Alibaba, DeepSeek Have ‘Systematically’ Siphoned AI Models - Bloomberg.com](https://news.google.com/rss/articles/CBMitAFBVV95cUxNZk92eWg4ODl3QnlnbmROdWEwaTllZm5TTFlPZXRKSnFjUUxjcnAwUGxDd2poTDh0V2N1S2xaLTI4Y3h0V09YOXd5MmszMkdUWUE4V2pOcEp3SjJuVUUxZjhNeXBNbW14dl9fRGRIWTJfZkN2bFNGc0V2Zk40SEtiZzFvaFdETm5jN3d2eE1tVHgxbDktV3Bfa3FfQnpGV2tsYTRNSFFKWjFGaTNQaVZ1VGE5MWc?oc=5) | 2026-09-09T07:00:00Z | confirmed | (추론) 추론: 미국 정부가 알리바바와 DeepSeek 이 미국 AI 모델을 '체계적으로' 증류해 빼냈다고 공식 주장했다는 보도다. 이는 ⑤ 의 적대 쪽 재료이며, 알리바바 ⑤ 판단이 적대 근거로 든 Anthropic 의 증류 주장(가짜 계정 25,000개)이 정부 차원으로 넓어진 것이다. 알리바바 ⑤ 판단은 동맹 등급 +1, 적대 등급 -1(비용형)로 3점이다. 미·중 지정학 위험은 알리바바 ⑧ 판단(-4, 미국 칩 금수와 중국의 제한이 겹친 양방향 지정학)에 이미 들어 있으므로 이 기사는 ⑤ 의 적대 성격으로만 쓴다. (선별 확신: 중간) |
| EV-alibaba-006 | ⑤ 아군 | news | [China investigates Meituan and Alibaba units for suspected antitrust violations - Reuters](https://news.google.com/rss/articles/CBMiywFBVV95cUxPNkxJNDZrd2NpQk80eEgyRWpwSEo3YWYxNUVHWHlaR1dGOWlFSmZHVF9xQjliN2RINXEzMHRsUGxjUEhLRlpsejF6dHF3b0dwZ09KcGlTMVMzdDVkbG5fdkdHNVdmSVFYdlVDMmJZcjB6ZzdITmh5YmhpSmgtamdGM245ZmxOTnJMUnJPTjM4UUZTR1BDeTNHQ0EwT0dfb1h6WVVaaVdpSUdhUkRicGVUaWRMTC1CaVBmXzN2YnFwUDMyWEFGNWxBZmJIUQ?oc=5) | 2026-09-19T07:00:00Z | confirmed | (추론) 추론: 중국 규제당국이 알리바바 일부 자회사를 반독점 위반 혐의로 조사한다는 보도다. 규제 조사는 ⑤ 의 적대 쪽 재료이고, 조사 단계라 사업 구조를 건드리지 않는 비용형에 해당한다. 알리바바 ⑤ 판단은 동맹 등급 +1, 적대 등급 -1(비용형)로 3점이다. (선별 확신: 중간) |
| EV-alibaba-007 | ④ 호황 이후 | news | [Alibaba deepens AI push with new chip, bigger model; shares jump 5% - Reuters](https://news.google.com/rss/articles/CBMi1gFBVV95cUxPUlcybzdOMWxNcmJHT1ZvUHFRTkczZzRNbHpkeUM1QjVxak5WMVdfTldrMWRtaTdHd1FvZkUwbGN4NmhwdUFSdmJxdVBVTGZxNFBWMUNqQXU3dlJzM1VXOHZsYmliZmxBRl90eFF6dEFZWl9BQTJTdkdxaDBSMGVrSXBJUkFVQkx1RTFOcktHZDQ4blo4VFh0amtSRmYxU2YxeGdQdUhFa25DeDBjSllsaVBsUVQ3X3VYdnRKMTAxN1BzZFQzUUpGSVI3TXZBZmRuTlhjejFB?oc=5) | 2026-09-21T07:00:00Z | confirmed | (추론) 추론: 알리바바가 자체 AI 가속기를 공개하고 더 큰 모델을 예고했다는 보도다. ④ 호황 이후 비전은 자체 칩을 출하가 확인될 때만 수직계열화 근거로 세므로, 이 칩은 출하 여부에 따라 ④ 근거가 될 수 있다. 더 큰 모델(10조 파라미터)은 예고라 별표 D(계획·발표는 현재 점수에 넣지 않는다)에 따라 근거가 아니며 트리거로만 지켜본다. 알리바바 ④ 판단은 4점이고 클라우드 성장(+45%)·AI 제품 매출·해외 데이터센터로 폭을 셌다. (선별 확신: 중간) |
| EV-alibaba-008 | ⑤ 아군 | news | [Alibaba Group Holding Limited (BABA) Investors: Securities Fraud Class Action Filed, Contact Hagens Berman Before October 5, 2026 Lead Plaintiff Deadline - PR Newswire](https://news.google.com/rss/articles/CBMirAJBVV95cUxONWNFX2hzOWx4ZC0xVTNEaVdQeWN0eFVOT0ZBcEFOSVN6OGZ4ZXVBbTlrN2ZMNmZFR003c1JlOVlac2FmeUlya2NxMXVUSzVJWFp0d3JmLUVhQWtJR2VDZVJYaVdyMk45TTVZb0NBc1BqMzltOUZqaG5sbjZvNnJBTWUwTW9VTlBXOHBvZDc3ZUlCblU4eXNENUpyNFVOMnpadE5lZWg5akE5di1wTlZfa2tOdnM1SmtjQjZkOVZKTWxGOWw3cEJBdDZ1Vm5oak14UDVCdE5GdFNGTnRLT29KdGpZaFJaTW5HT2pxY1FWS21FZWItb3VzRlBqRzJ0QzFzMWpNLTV1VFZrall3R0FMdlVCQlBTeERfZUlKdnI2UnpWeDVPNmtyMDI3X0c?oc=5) | 2026-09-29T16:29:00Z | confirmed | (추론) 추론: 미국에서 알리바바 투자자를 대리한 증권사기 집단소송이 제기됐다는 법률사무소 보도자료다. 개별 소송은 ⑤ 의 적대 쪽 재료이고 사업 구조를 건드리지 않으므로 비용형이다. 알리바바 ⑤ 판단은 동맹 등급 +1, 적대 등급 -1(비용형)로 3점이다. (선별 확신: 낮음) |

### Anthropic

| 근거 ID | Factor | 종류 | 제목 | 발행시각(UTC) | 상태 | 관련성 |
| --- | --- | --- | --- | --- | --- | --- |
| EV-anthropic-001 | ② 게임체인저 | news | [Introducing Claude Opus 5.5 - Anthropic](https://news.google.com/rss/articles/CBMiU0FVX3lxTE9xbTN1a0tOdm9kT0JxbVBHMU9XYUhpUjd0MHNFYm8yd2pRMnhjdEYzdjF3ckZEY1V0a2ZQTXlyRUhteVozMlhDbVQ3Mm1KWlRYbUVF?oc=5) | 2026-09-22T07:00:00Z | confirmed | (추론) 사실: Anthropic 이 신모델 Claude Opus 5.5 를 자사 발표로 공개했다. 추론: ②(게임체인저)의 최상단 칸은 성능 도약이 세대 격차 수준일 때 주므로, 신모델은 그 판정을 다시 할 계기다. 다만 회사가 발표한 벤치마크는 방증이고 1차 근거는 독립 측정(Artificial Analysis·ARC-AGI 등)이다. Anthropic ② 판단은 v1.5 에서 승계한 5점(최상단)이고, 세대 격차 수준인지는 아직 판정하지 않았다(긴장 #11: ② 최상단 점수를 세대 격차 판정 없이 승계한 상태). 이해상충: 선별자가 Anthropic 모델 (선별 확신: 중간) |
| EV-anthropic-002 | ⑤ 아군 | news | [US appeals court upholds Pentagon's blacklisting of Anthropic - Reuters](https://news.google.com/rss/articles/CBMiqgFBVV95cUxPN2xsSW1uNVNkSjE2UHVQSGFlOGJTbGFRa2dtdWgyb1owYlFpS2RHZHVSQnRxSTRoSnhqWWJTMEV4Q1BfNzRJZ0h4MVY4S014TTAxbjU4aThsZW95OUhEUFg2Tlg5ZU92Y21RcXVZa1hySFBUT2FXVkZ1ZlRaV3BpNnJFY3g2Ny1KRkpyQm5pNTctbS04V182WjZpYWczRWlJM1RMWl9uU0hNQQ?oc=5) | 2026-09-25T17:54:58Z | confirmed | (추론) 사실: 미 항소법원이 국방부의 Anthropic 거래 배제(블랙리스트)를 유지했다. 추론: 정부 시장 일부가 막힌 것이라 ⑤(아군과 적대)의 적대 등급 재료다. 별표 G(⑤ = 3 + 동맹 등급 + 적대 등급)에서 적대 등급 '최소' 는 규제 조사·소송·시장 차단이 눈에 띄지 않을 때이고, '비용형' 은 벌금·소송·규제 조사·시장 일부 차단처럼 사업 구조는 건드리지 않는 적대다. 선별 당시 Anthropic ⑤ 판단은 동맹 등급 +1, 적대 등급 0(최소)으로 4점이었고, 이 근거를 인용한 제안 PRP-001 반영으로 적대 등급 -1(비용형), 3점이 됐다. 이해상충: 선별자가 Anthropic 모델 (선별 확신: 중간) |
| EV-anthropic-003 | ⑨ 적자 깊이 | news | [Anthropic’s leaked IPO prospectus details steep losses, rapid growth, and a fear that AI could end humanity - Fortune](https://news.google.com/rss/articles/CBMimAFBVV95cUxPT1VnSWcyaGx2WXRNaEc2NmhQVVhuVmFDaGN4MVkydU5yYTltYmMzd0RtMzFTUEdLSURWbGFjNlFSMUlEdjV3QjhaQ25oX0xJNFF0azNCck5sMThQaXdhQTg0aVYwRk1zWkEzTzM5WUI4dWlnc0hvdE11ajQ4Q1N2Y1pEYktxQTFSdC1lX01kYjVaOFNwak9yQQ?oc=5) | 2026-09-29T10:03:00Z | confirmed | (추론) 사실: Fortune 이 유출된 Anthropic 상장 신청서(S-1)가 큰 손실과 빠른 성장을 담았다고 보도했다. 추론: 손익·현금흐름이 공개되면 ⑨(적자 깊이)의 게이트 1(본업이 버는가 — 최근 1년 영업이익)과 게이트 2(최근 1년 잉여현금흐름이 마이너스인가)를 실측으로 판정할 수 있다. Anthropic ⑨ 판단은 -2점이다. 비상장이라 최근 1년 영업손익이 공시되지 않아 게이트 1 을 판정 보류로 두고(Q2 단일 분기 영업흑자 $559M 은 통과 근거로 쓰지 않는다), 게이트 2 를 비상장 현금흐름 미공시로 보수 처리했다. 이해상충: 선별자가 Anthropic 모델 (선별 확신: 중간) |
| EV-anthropic-004 | ⑧ 비대칭 의존, ⑨ 적자 깊이 | news | [Anthropic's $518 billion AI buildout hinges largely on deals that cannot be canceled, filing shows - Reuters](https://news.google.com/rss/articles/CBMiwgFBVV95cUxNazVCbjhpLXhaZU5LbGk2TENxV0NHbXdFSS03bVpudXJnOE84Y2ItOGxEdHRHRHYwNG80SlRsZEVLNDN4eDJNaDJJRmlxbWpyNDU4Uk9scjNCQXVzelhERzZzZUZOS1c0M3JEMFpMWjFuRGU2cHhqQk1ZSDlIMFRwZmtCYXJZajFpcEM4cFRIUF9tUWljSVRzRFN4akQyLWdaNVltTDY3anJJUkRHbWctVkNRbzNQV3FBejF4UldtcXA2QQ?oc=5) | 2026-09-29T16:48:56Z | confirmed | (추론) 사실: Reuters 가 상장 신청서를 근거로 Anthropic 의 $518B 규모 AI 설비 구축이 대부분 해지할 수 없는 계약에 걸려 있다고 보도했다. 추론: 해지 불가 약정의 규모는 ⑧(비대칭 의존)의 약정÷매출과 ⑨(적자 깊이) 게이트 4(약정 커버리지 — 앞으로 내기로 한 약정을 버는 돈이 덮는가)의 직접 입력이다. Anthropic ⑧ 판단은 -3점이고 약정 합계를 v1.5 기준선 값 약 $300B(AWS 분은 공시 문면상 하한)로 적고 있다. Anthropic ⑨ 판단은 -2점이고, 게이트 4 는 약정과 계약 수입의 기간·범위가 달라 비교 불가로 두어 계산하지 않았다(근거 문장에는 v1.5 의 하한 기준 커버리지 1.3배가 남아 있다). 이해상충: 선별자가 Anthropic 모델 (선별 확신: 중간) |
| EV-anthropic-005 | ⑧ 비대칭 의존 | news | [EXCLUSIVE: Anthropic IPO prospectus lays bare deep dependence on Big Tech partners - Reuters](https://news.google.com/rss/articles/CBMirwFBVV95cUxPQ1Q4X3lqOUdZYllBZFVuZFBIWGt6dmdua2JoVnZ0aVVnWnd0M2lscWd0UFB6c3QxRmNJdXJ2T3ppbXR5TW8wZ2lzQU5obDR2U2t0WldJUWx4MEo2V29HVldhSEtVUWVPdkdIQ1dVSUtkcG5hTE5UWDVKek9hTjhkNGU4eGNKcmRPY1JjWmRaTXJVblBoWldzNU1PalhocDRfRHdPRnhxVEV5ckRsenJZ?oc=5) | 2026-09-29T20:53:00Z | confirmed | (추론) 사실: Reuters 가 Anthropic 상장 신청서가 대형 기술 파트너에 대한 깊은 의존을 드러냈다고 단독 보도했다. 같은 신청서를 다룬 2차 보도(Yahoo Finance)는 매출의 약 50%가 Amazon·Google 을 거친다고 제목에 적었다. 추론: ⑧(비대칭 의존)이 묻는 '끊기면 회사가 멈추는가 · 공급자가 곧 경쟁자인가' 의 재료이고, 컴퓨트 공급에 판매 채널 집중까지 겹치는지 볼 수 있다. Anthropic ⑧ 판단은 -3점이다 — 컴퓨트를 100% 외부에서 쓰고 공급자(Google·Amazon·Microsoft·xAI)가 전부 경쟁자다. 더 내리지 않은 이유는 Google 몫이 훈련용인지 공시가 없기 때문이다(긴장 TEN-RA5-01: 알파벳 제출본이 보존되면 하향 여부를 다시 보는 항목, 2026-11). 이해상충: 선별자가 Anthropic 모델 (선별 확신: 중간) |
| EV-anthropic-006 | ⑤ 아군 | news | [FTC Probing OpenAI and Anthropic Over Product Safety Concerns - bloomberg.com](https://news.google.com/rss/articles/CBMisgFBVV95cUxQNWthUTUtdzAtb1NKYkQ4TDdxSGV4ZC1NV2QxTnE5a2VzaldWRWowU3VDUUxWV3lIajZzRnNYLTJUV3RCaTFxUU11MEhKSFF4UmFMNTBqV1g0bmljbWE3bXJJc0tNOE5XX3hZQjRlUS1sMFlaS0FDWHZ2WmdQU05zSV9uSFpYNlF0SmVHeEVTTnVkdzdNZHZZbGJaemhGQUoxT0gxVm1kbnJ1dTlhZm8zeFJR?oc=5) | 2026-09-30T15:01:25Z | confirmed | (추론) 사실: Bloomberg 가 FTC(미 연방거래위원회)가 제품 안전 문제로 OpenAI 와 Anthropic 을 조사한다고 보도했다. 추론: 규제기관 조사는 ⑤(아군과 적대)의 적대 등급 재료다(별표 C: 적대는 수가 아니라 성격을 본다). 별표 G(⑤ = 3 + 동맹 등급 + 적대 등급)에서 적대 등급 '최소' 는 규제 조사·소송·시장 차단이 눈에 띄지 않을 때이고, 규제 조사는 '비용형'(사업 구조는 건드리지 않는 적대)의 예로 적혀 있다. 선별 당시 Anthropic ⑤ 판단은 동맹 등급 +1, 적대 등급 0(최소)으로 4점이었고, 이 근거를 인용한 제안 PRP-001 반영으로 적대 등급 -1(비용형), 3점이 됐다. 이해상충: 선별자가 Anthropic 모델 (선별 확신: 중간) |
| EV-anthropic-007 | ③ Last Mover, ⑥ 가격 | news | [Anthropic’s $11.6 Billion Quarter Just Changed How the Market Should Read the S-1 - Yahoo Finance](https://news.google.com/rss/articles/CBMimgFBVV95cUxPWDNQVUtxQlR0MTFnZFJiQlZGOXNrTXRZczBvSkZ3Nmh5ZHpEdHo2TzBGZ2hocUQ5Zko1TVYwX3RjMWxHN0hQbDBQSENDMTdhb3V0YWJGVkpfS0NMamFJako3UmdjMkpwelI0RG1CcURMV1FpQkN0ZjdXSW1lbzJCWklKZVI5dDJFQV9yX01JZU5VaWhfMFlLTk1R?oc=5) | 2026-09-30T19:44:12Z | confirmed | (추론) 사실: Yahoo Finance 가 Anthropic 의 분기 매출 $11.6B 가 상장 신청서를 읽는 법을 바꿨다는 해석 기사를 냈다. 추론: 실제 분기 매출은 ⑥(현재 가격의 정도) 비상장 계산의 분모를 바꿀 재료다. Anthropic ⑥ 은 프로그램이 계산하며 -4점이다 — 밸류 $965B 를 최근 1년(TTM) 보정 매출로 나눈 배수(P2, 밸류÷매출)가 점수를 내는데, 분모를 Q2 매출 $10.9B 에서 역산해 약 30~39배로 가장 비싼 구간(30배 이상)에 든다. 분기 간 성장률은 ③(Last Mover)의 후발 가속도 문장도 보강할 수 있다. Anthropic ③ 판단은 3점이고 후발 가속도는 ❌ 감속(ARR 월 증가율 +57%→약 +14%)이다. 이해상충: 선별자가 Anthropic 모델 (선별 확신: 낮음) |
| EV-anthropic-008 | ② 게임체인저 | news | [Google unveils Gemini 4 Argon, retaking benchmark lead over OpenAI and Anthropic — but in limited release - VentureBeat](https://news.google.com/rss/articles/CBMi0wFBVV95cUxQbV9aRXc0YUkwWEFxRXAtLUpoTDJ6WGRpUWpzRGwtWG82TUU1RGJ6Si1lUzlxYUE5a1UxNEZmUG5kT09kcnd6TUhoeTJWUnZ1UkF2eGZIcHg2d2FvZ19GVXhvbUQ3WlREX05yNmdsdlI4RWg3ZGlNTzhzVmhmbV9NMWJvSk4wMlFZNjNxaFRSVlFQSWhocU1GQjU4TDJVVmdNdjVBdzhnUFc1RWc1YVN4NU41NUZhMnJQeFFtX0NtQU9BekxuVkxKVHNTTkwyald6a0Rv?oc=5) | 2026-09-30T20:23:29Z | confirmed | (추론) 사실: VentureBeat 가 Google 의 Gemini 4 Argon 이 OpenAI·Anthropic 을 제치고 벤치마크 선두를 되찾았다고 보도했다(제한 출시). 추론: ②(게임체인저) 최상단 칸은 성능 도약이 세대 격차 수준일 때 주므로, 경쟁 모델이 앞섰다는 측정은 Anthropic 의 세대 격차 주장에 반대 방향 재료다. 다른 회사의 점수가 아니라 경쟁 모델의 측정 사실로만 쓴다. Anthropic ② 판단은 v1.5 에서 승계한 5점(최상단)이고, 세대 격차 수준인지는 아직 판정하지 않았다(긴장 #11: ② 최상단 점수를 세대 격차 판정 없이 승계한 상태). 이해상충: 선별자가 Anthropic 모델 (선별 확신: 낮음) |

### Apple

| 근거 ID | Factor | 종류 | 제목 | 발행시각(UTC) | 상태 | 관련성 |
| --- | --- | --- | --- | --- | --- | --- |
| EV-apple-001 | ⑥ 가격 | filing | [8-K 2026-07-30 · Items 2.02, 9.01](https://www.sec.gov/Archives/edgar/data/320193/000032019326000018/aapl-20260730.htm) | — | confirmed | (추론) 추론: 2026-07-30 8-K(Item 2.02 실적 발표)는 Apple 의 2026년 6월 분기(FY26 3분기) 실적이다. 흑자 기업의 매출 공시는 ⑥ 매출 성장 잣대(P3, 최근 1년 매출 ÷ 그 전 1년 − 1)의 입력이다. 지금 Apple ⑥ 매출 성장 입력은 2026-06-27 까지 최근 1년 매출 4,668억 달러, 성장률 약 14% 로 '5% 이상 15% 미만' 구간이다. (선별 확신: 높음) |
| EV-apple-002 | ⑧ 비대칭 의존, ⑨ 적자 깊이 | filing | [10-Q 2026-07-31](https://www.sec.gov/Archives/edgar/data/320193/000032019326000020/aapl-20260627.htm) | — | confirmed | (추론) 추론: 2026-06-27 분기 10-Q 로 Apple 의 가장 최근 정기 보고서다. ⑨ 의 최근 1년 잉여현금흐름과 ⑧ 의 의존 서술(위험 요인)의 1차 자료다. 지금 Apple ⑨ 판단은 영업흑자·최근 1년 잉여현금흐름 흑자(약 1,367억 달러)·추세 안정으로 감점이 없고, ⑧ 판단은 -3 이다(Google 검색 지급금 연 200억 달러에 걸린 DOJ 항소 위험, Siri 의 Gemini 의존). (선별 확신: 높음) |
| EV-apple-003 | ⑤ 아군 | news | [US jury says Apple owes record $5.7 billion in haptic technology patent case - Reuters](https://news.google.com/rss/articles/CBMiwgFBVV95cUxPOXduWFl4SXl1dlNpaDVMVUdxbENVSGFqV3hFYnl2ZE8yTTRNZVAxZFpwTERQZzExTmg1ZG5IdHFtRjg5cUtGaU1pNndEa0UzMzg1YWJWc203ZnVOajF3MUM2RGhQTllJTXRub05McENSTExBQVhQUm1aYlZIN3RyR2RfN1V4cjZ1bktEVjV4bk5WdFowdVZENlhWOE0wU1Y0T25LRk8tbjBFendGaVhNdlp5aUZNWFM4YUhKdzhNNFFLUQ?oc=5) | 2026-09-28T14:17:03Z | confirmed | (추론) 추론: 미 배심원이 햅틱 특허 소송에서 Apple 에 57억 달러 배상을 평결했다는 Reuters 제목이다. 규제 조사·소송·평결은 ⑤ 적대 등급의 재료이고, 판매 금지가 아니라 금전 배상이라 사업 구조를 건드리지 않는 비용형이다. 지금 Apple ⑤ 판단은 동맹 등급 +1(App Store 개발자 생태계), 적대 등급 -1(법적 전선 4개이나 전부 비용형)로 3점이다. (선별 확신: 중간) |
| EV-apple-004 | ⑤ 아군 | news | [Amazon (AMZN) and Apple (AAPL) Must Face a UK Class Action Over Marketplace Sales - Yahoo Finance](https://news.google.com/rss/articles/CBMilwFBVV95cUxOMTJVWGRDWmhFa0NQaEowbXB4dFNMZzN2NE5QX2dpYWYtWTZXVFpGY2p2dlR3Q1BURTZzdm9DVVpTdWRkNjRiaU00dEJBR1dvUmJ6VGxUU05sUlozNWVOVlFDcVVnNGdWYjk5WDNTc09EbEdvZzFkd1FnelhGSVJZOGQ3WFhielhIX1hwN2Z6UUNwR0piNFFF?oc=5) | 2026-09-30T06:08:00Z | confirmed | (추론) 추론: 영국 법원이 Amazon 마켓플레이스 판매를 둘러싼 집단소송에서 Amazon·Apple 을 피고로 재판을 진행시킨다는 제목이다. 소송은 ⑤ 적대 등급의 재료이고 금전 청구로 보여 비용형이다. 지금 Apple ⑤ 판단은 동맹 등급 +1, 적대 등급 -1(비용형)로 3점이다. (선별 확신: 중간) |

### NVIDIA

| 근거 ID | Factor | 종류 | 제목 | 발행시각(UTC) | 상태 | 관련성 |
| --- | --- | --- | --- | --- | --- | --- |
| EV-nvidia-001 | ⑦ 순환금융 | filing | [8-K 2026-08-17 · Items 1.01, 2.03, 7.01](https://www.sec.gov/Archives/edgar/data/1045810/000104581026000069/nvda-20260817.htm) | — | confirmed | (추론) 추론: 2026-08-17 8-K 에 Item 1.01(중요 계약 체결)·2.03(직접 금융 채무 또는 부외 약정 발생)·7.01(공정 공시)이 함께 나왔다. 규칙 문서의 ⑨ 부외 약정 표와 NVIDIA ⑦ 판단 근거가 '8/17 8-K' 를 SB Energy 보증 1,050억 달러 상한(OpenAI 계열사용 오하이오 데이터센터)으로 적고 있어 같은 공시로 보인다. 우발 보증은 ⑨ 가 아니라 ⑦(순환 금융)에서 센다. 지금 NVIDIA ⑦ 판단은 별표 I(⑦ 판정표: 조달 의존 고객 비중 × 내 돈이 고객을 거쳐 내 매출로 돌아오는가)의 '조달 의존 큼 + 환류 있음' 칸으로 -2, ⑦ 범위의 최저점이다. (선별 확신: 낮음) |
| EV-nvidia-002 | ⑥ 가격 | filing | [8-K 2026-08-26 · Items 2.02, 9.01](https://www.sec.gov/Archives/edgar/data/1045810/000104581026000073/nvda-20260826.htm) | — | confirmed | (추론) 추론: 2026-08-26 8-K(Item 2.02 실적 발표)는 NVIDIA 의 2026년 7월 분기(FY27 2분기) 실적이다. 흑자 기업의 매출 공시는 ⑨ 보다 ⑥ 매출 성장 잣대(P3, 최근 1년 매출 ÷ 그 전 1년 − 1)의 입력이다. 지금 NVIDIA ⑥ 매출 성장 입력은 2026-07-26 까지 최근 1년 매출 3,030억 달러, 성장률 약 83% 로 '30% 이상' 구간(감점 없음)이다. (선별 확신: 높음) |
| EV-nvidia-003 | ⑦ 순환금융, ⑧ 비대칭 의존, ⑨ 적자 깊이 | filing | [10-Q 2026-08-26](https://www.sec.gov/Archives/edgar/data/1045810/000104581026000075/nvda-20260726.htm) | — | confirmed | (추론) 추론: 2026-07-26 분기 10-Q 로 NVIDIA 의 가장 최근 정기 보고서다. ⑧ 고객 집중도, ⑦ 고객 대상 지분 투자·보증(내 돈이 고객을 거쳐 돌아오는가), ⑨ 최근 1년 잉여현금흐름의 1차 자료가 들어 있는 양식이다. 지금 NVIDIA 판단은 ⑦ -2(조달 의존 큼 + 환류 있음, 범위 최저점), ⑧ -3(매출 약 40% 인 하이퍼스케일러 4곳이 모두 자체 칩 개발), ⑨ 감점 없음(영업흑자·잉여현금흐름 약 1,270억 달러 흑자·추세 안정)이다. (선별 확신: 높음) |
| EV-nvidia-004 | ④ 호황 이후 | news | [OpenAI sparked Hugging Face bids with early investment offer ahead of Nvidia's $13 billion deal - cnbc.com](https://news.google.com/rss/articles/CBMiqwFBVV95cUxQMThSYmpsQmN6bHcxbk1TSTN3a0xPaHdqOS0wYS1hUWhOQzREbWpSVzlvalkzY0ozWkxWcVo3Z0lzQ3NiOUN1MnBMQVNiTkxjTzVadkZXSWJ5NjM2VzRaS0EzekJrWWZ0VDVRWXdDUXQ5b3Q1SzF3MGJUTUZpMDFTb1ZKbWlJaGxsQkhvU2hGcGExQjZ3VXhBNVMtM3RrazNmT0hBUnVBVVlaYm8?oc=5) | 2026-09-28T18:44:49Z | confirmed | (추론) 추론: CNBC 제목이 NVIDIA 의 Hugging Face 관련 130억 달러 거래와 그 앞의 OpenAI 투자 제안을 전한다. 기존 NVIDIA ① 판단 근거는 이 거래를 2026-09-02 에 서명한 인수(종결 2027 상반기·규제 승인 조건부)로 적고 있다. 인수가 끝나면 GPU 밖 사업 부문이 늘어 ④(호황 이후 비전 — 사업 부문 수·자체 칩 출하)의 근거가 된다. 지금 NVIDIA ④ 판단은 10개 영역 진출로 5점, 최상단이다. (선별 확신: 낮음) |
| EV-nvidia-005 | ⑦ 순환금융 | news | [Nvidia turns to insurers to spread the risk of AI build-out - Financial Times](https://news.google.com/rss/articles/CBMihAFBVV95cUxNOE9rNFhZUjQwSFZpNkhrb3IyR2lMdGpUUTVWVGppaXBfUk1RNkdzYUlNT0dxOXBjSEJSamVHTlFiUlp2QjRmQmNNX1pWWHJidUhreWlNWmlXdVZVWUp4VTZUWU82WlNWUWFObUo3aEo5T3IwRWtOQzItanZaMXVMZXh2MzU?oc=5) | 2026-09-29T10:01:44Z | confirmed | (추론) 추론: NVIDIA 가 AI 구축 위험을 보험사로 분산한다는 FT 제목이다. 같은 묶음의 Bisnow 제목('AI 대출 위험을 보험사에 넘긴다')과 합치면 NVIDIA 가 고객의 데이터센터 구축 자금에 신용을 대고 있다는 뜻이어서, ⑦ 의 '내 돈(신용)이 고객 주머니로 갔다가 내 매출로 돌아오는가' 축의 근거다. 지금 NVIDIA ⑦ 판단은 별표 I(⑦ 판정표: 조달 의존 고객 비중 × 내 돈이 돌아오는가)의 '조달 의존 큼 + 환류 있음' 칸으로 -2, ⑦ 범위 최저점이다. (선별 확신: 중간) |
| EV-nvidia-006 | ⑤ 아군 | news | [DeepSeek partners with Huawei to develop chip programming tools, reducing reliance on Nvidia - Reuters](https://news.google.com/rss/articles/CBMizgFBVV95cUxPdUg5OUtKZEFWWE1PU3dHYURRTThhbS1fWTM2YzdIekQyTTIwU1daMl8wSW5XNTl4aklKSWlxVHRrazlhRlNjNXZDX0ZHd3RnUldXTUZmbGNuYXJYMUV2SFVvWEZsVWRuajcxazZ5WmZ3eEg5TEMtMVVIMXB1V0ppNHA4VEIyQzN0c0hmZDNjaWFLTE81d3IxLXZQeWVJWjhzWTNrUXBzU0IwYXhaX3NqUXkwNTJmMS1yZlhiaGNPRVUxcGZ0RmNKVFhRRVZrQQ?oc=5) | 2026-09-30T03:03:00Z | confirmed | (추론) 추론: DeepSeek 가 Huawei 와 칩 프로그래밍 도구를 함께 만들어 NVIDIA 의존을 줄인다는 Reuters 제목이다. CUDA 를 대체하는 소프트웨어 생태계가 실제 협업으로 생긴 사실이라 ⑤ 적대 등급의 재료다. 지금 NVIDIA ⑤ 판단은 동맹 등급 +1(Nemotron 연합), 적대 등급 -2(구조형 — 주요 고객이 곧 경쟁자)로 2점이다. (선별 확신: 중간) |
| EV-nvidia-007 | ⑦ 순환금융 | news | [Exclusive: GPU Cloud Provider GMI Raises $668 Million From Nvidia and Others - The Information](https://news.google.com/rss/articles/CBMiqgFBVV95cUxQV2k2TTQ0M0ZEWFB2VF81b29qdzF1UTNoOFpjTjhvbGh2WjA0VGJBcjIyeVNPdmhXdG9uckhxMDEtUFJoNU5WdGt0MEE3bXgteWxOWVVrS2JLUnBMNjB1SThxS2xmZkdKMjg5WVcwWFhsellOeGZ1RC11VUIxcmw4V0J6Tmp5UHNMaWw2MmpNbWNfNzY1Rlc3Z0EwOVg0YW14WG13LS03U2lUQQ?oc=5) | 2026-09-30T10:55:00Z | confirmed | (추론) 추론: GPU 클라우드 GMI 가 NVIDIA 등에서 6.68억 달러를 조달했다는 The Information 단독 제목이다. NVIDIA 가 자기 GPU 를 사는 클라우드에 지분을 넣은 것이라 ⑦ 의 '내 돈이 고객 주머니로 갔다가 내 매출로 돌아오는가' 축의 근거다. 지금 NVIDIA ⑦ 판단은 별표 I(⑦ 판정표)의 '조달 의존 큼 + 환류 있음' 칸으로 -2, ⑦ 범위 최저점이고, 근거에 OpenAI·CoreWeave·Nebius 지분 투자가 이미 있다. (선별 확신: 중간) |
| EV-nvidia-008 | ② 게임체인저 | news | [CoreWeave Delivers NVIDIA Vera Rubin NVL72 Performance at Production Scale, Starting With Cognition - CoreWeave](https://news.google.com/rss/articles/CBMiyAFBVV95cUxNTTd2T1pOekRaT3c2NHBWS1NlOVJEWFpiR2JidzlZd18yVkRuNVMyaE5XaERqVGhKbWhrc1c5Y2dXYjFMWEh3MmpBWlZGS3BzSWFZMV82YlBORGVST3B3ZFM0c2N4M1RPQ19jRjVUVTJTR2dmeTR0YUVSYWoySkxvZjhOb2l4TlRIZzg1Z3ZadGFLU2hTWVlDWjduenRiRDVlLTZiR3Q2d1RkY1NnNXVPVVhBaGh2Vk5BYVBaam03M0E5cnpEZzNTbQ?oc=5) | 2026-09-30T16:21:03Z | confirmed | (추론) 추론: 고객사 CoreWeave 가 Vera Rubin NVL72 를 '생산 규모'로 제공한다고 밝혔다. 지금 NVIDIA ② 판단은 5점(최상단)이고, 그 note 는 'Rubin 줄은 발표이고 저장소 어느 자료도 양산을 말하지 않는다' 고 적어 두었다. 이 기사는 바로 그 출하 여부의 공백을 건드린다. (선별 확신: 중간) |

### Palantir

| 근거 ID | Factor | 종류 | 제목 | 발행시각(UTC) | 상태 | 관련성 |
| --- | --- | --- | --- | --- | --- | --- |
| EV-palantir-001 | ⑥ 가격, ⑧ 비대칭 의존, ⑨ 적자 깊이 | filing | [10-Q 2026-08-04](https://www.sec.gov/Archives/edgar/data/1321655/000132165526000041/pltr-20260630.htm) | — | confirmed | (추론) 추론: 팔란티어의 가장 최근 정기 보고서(10-Q, 2026년 2분기)다. 매출·이익은 ⑥ 의 P1(최근 1년 이익 기준 PER)·P3(매출 성장) 입력, 정부·상업 매출 구분은 ⑧ 비대칭 의존(끊기면 매출이 주는가)의 재료, 영업현금흐름·설비투자는 ⑨ 게이트 2(최근 1년 잉여현금흐름이 마이너스인가)의 원천이다. 지금 계산에 쓰는 최근 1년 관측(매출·순이익·잉여현금흐름 +US$3,358M)은 이미 2026-06-30 까지의 창이라 이 보고서 분기가 들어 있다. 팔란티어 ⑨ 판단은 잉여현금흐름 흑자에 추세 안정으로 0점, ⑧ 판단은 미 정부 계약 의존(연방 $0.9B+)과 정권 교체 위험으로 -3 이다. (선별 확신: 중간) |
| EV-palantir-002 | ⑤ 아군 | news | [PwC and Palantir expand strategic alliance for enterprise AI - PwC](https://news.google.com/rss/articles/CBMilAFBVV95cUxPUDRrWFAzTGd0SDR1SFhVVV9wTnRyUmhOUjFRRGNLVXlNQVE5Y0JsUGh2cThPWDJqdE5ObzZ6T2d5S2Y3RW0ybXh2c0x3M1hfeXRLOFQ2aEJyOUJqaWdBRGhfMTFxbTlPTmkyZ29JYkRfY09FZll5T3NnaU55dFJxa3h1dUNXSWd4cC1qbXNRRjdGSkJn?oc=5) | 2026-09-03T07:00:00Z | confirmed | (추론) 추론: PwC 와 팔란티어가 기업용 AI 전략 제휴를 넓힌다는 PwC 발표다. 컨설팅사의 구축·재판매 제휴는 팔란티어 ⑤ 판단이 아군으로 센 SAP·Accenture 와 같은 유형의 상업 동맹 후보다. 팔란티어 ⑤ 판단은 동맹 등급 +1(미 정부·NVIDIA·SAP·Accenture), 적대 등급 -2(사업 정당성을 겨냥한 구조형)로 2점이다. (선별 확신: 중간) |
| EV-palantir-003 | ① 네트워크 | news | [Chipotle Is Working With Palantir to Track Food Safety Risks - WIRED](https://news.google.com/rss/articles/CBMigwFBVV95cUxNRjZ2WFF6NTVKSk1aejZlaXJWNi1wUmoxdHBVYnBfWnZmYkF6Ung0YV9fYk1VLXl4dEtXQll2OFJjNGcwclVScl9LblFOeGdOb25oRE1xQ0hPTFY3TU1jc0NUZmppTExSbnRvRHlicXJWa1M5UUxXQnpyMHA0R1dYa3ZFcw?oc=5) | 2026-09-16T07:00:00Z | confirmed | (추론) 추론: 외식 대기업 Chipotle 이 식품 안전 위험 추적에 팔란티어를 쓴다는 보도다. 기업 고객 수는 ① 네트워크 효과의 업무 채널 지표(조직 워크플로에 박혔는가)다. 팔란티어 ① 판단은 2점으로, 정부·기업 계약의 전환비용은 있으나 사용자가 늘어도 가치가 커지는 스노우볼이 없다고 적었다. (선별 확신: 낮음) |
| EV-palantir-004 | ① 네트워크 | news | [Five UK police forces end Palantir project after two years - Financial Times](https://news.google.com/rss/articles/CBMihAFBVV95cUxOVkE3SDI3N2ROT0xEVkJlcUI3MFJjTHFHZ1ZtcGN5M2dBNk1LNFptaHYxSnBpRGQzODhMM2lCLTQzVEdNRUFrZlZneE5IRVgyVHpTcFUwdlBCd2ZmTEktamp1U1hQSUNqVF91T2h1bmhLTUVBWTZiWGtPSkdZcUgzUGVqUHE?oc=5) | 2026-09-21T07:00:00Z | confirmed | (추론) 추론: 영국 경찰 다섯 곳이 2년 만에 팔란티어 프로젝트를 끝냈다는 보도다. 고객이 실제로 떠난 사례라 ① 의 판별 질문('가격을 올려도 남는가', 업무 채널 락인)에 대한 반대 증거다. 팔란티어 ① 판단은 2점으로, 전환비용은 있으나 스노우볼이 없는 가짜 해자라고 적었다. (선별 확신: 중간) |
| EV-palantir-005 | ⑤ 아군 | news | ['Not Just Another Tech Company': Unions, Rights Groups Across EU Demand Governments Ditch Palantir - Common Dreams](https://news.google.com/rss/articles/CBMidkFVX3lxTE1HdDhKeVVDblBLQ2JCWEoyTWZ3TXRXU21DR0NKQ19pSDZURXBmU0FuODhlWk5wQ0hyNWM3ZEhfRThpNHBSaUQtblU5dy14b19uaEhibHd1UVEyQ0NMN0YtNnpTVkZ2VDdEVzNPNTJBcWVFVDhxNGc?oc=5) | 2026-09-28T16:55:35Z | confirmed | (추론) 추론: EU 여러 나라의 노조·인권단체가 각국 정부에 팔란티어 계약을 끊으라고 요구했다는 보도다. 사업의 정당성을 겨냥한 적대가 유럽 전선으로 넓어지는 재료다. 팔란티어 ⑤ 판단은 동맹 등급 +1, 적대 등급 -2(구조형: ICE 이민단속 계약·감시 자문으로 사업 정당성이 표적이 됨)로 2점이다. (선별 확신: 낮음) |
| EV-palantir-006 | ⑤ 아군 | news | [San Francisco nurses protest ICE connection with Palantir - CBS News](https://news.google.com/rss/articles/CBMiowFBVV95cUxOMXVKVVdGd0RqMkk1c0pSaDJ4a0FVTkdjVDN6VW11elZ1UnhXOGd6M0hzSWNYa3RtVXFyOGVIQzlGV3Fhb1pBbzljbk41Y3JPZEdaejcyRmlaNjhwUUVlTlNXeU8xMFVtQm9ZR0ZfR1RTeXRqT3hnNkdRNENWaGVXZ1JidHdGbFNZNHJyNTJzb3lCNkp2TWJjT1BDOE1zdFVOTzlz?oc=5) | 2026-10-01T01:24:00Z | confirmed | (추론) 추론: 샌프란시스코 간호사들이 팔란티어의 ICE(미 이민세관단속국) 연계에 항의 시위를 했다는 보도다. 팔란티어 ⑤ 판단이 구조형 적대의 근거로 든 ICE 계약 논란이 병원 쪽으로 번지는 사례다. 팔란티어 ⑤ 판단은 동맹 등급 +1, 적대 등급 -2(구조형)로 2점이다. (선별 확신: 낮음) |
| EV-palantir-007 | ⑤ 아군 | news | [More than 44,000 file legal objections to Palantir NHS platform handling their data - The Guardian](https://news.google.com/rss/articles/CBMipgFBVV95cUxNc2lpa0pURkdTLWNUZ25IZEthd1JacVhRN3RzRVF4S0dDSUttNmlDNXJVUVBGRmZ3cU9LZjg0Ym54Qi1hZGZnTnREWUY2QTVudDBBWEN1N3FRME4tN3IyRWNsQTc4X3Y4OGFSb21wQ0x6WXdWZU1jdjk2NUgzazNFSHhGNDBFdzJ0TVNmVk5XN2ltWk5qNGFlMXFIMWhnTGU1YmF0Q0Rn?oc=5) | 2026-10-01T01:30:00Z | confirmed | (추론) 추론: 영국 NHS 연합 데이터 플랫폼(팔란티어 운영)에 자기 데이터 처리를 거부하는 법적 이의 제기가 44,000건 넘게 접수됐다는 보도다. 사업의 정당성을 겨냥한 시민사회 적대로, 팔란티어 ⑤ 판단의 구조형 적대 근거와 같은 성격이다. 팔란티어 ⑤ 판단은 동맹 등급 +1, 적대 등급 -2(구조형)로 2점이다. (선별 확신: 중간) |

### SpaceX + xAI

| 근거 ID | Factor | 종류 | 제목 | 발행시각(UTC) | 상태 | 관련성 |
| --- | --- | --- | --- | --- | --- | --- |
| EV-spacex-xai-001 | ⑦ 순환금융, ⑧ 비대칭 의존 | news | [Google to pay SpaceX $920 million a month for compute capacity at xAI data centers - cnbc.com](https://news.google.com/rss/articles/CBMipAFBVV95cUxQbTlsMnZmeWxoUk0yWmhKcGs0eVhkc1d1c1JVRm9qUWFMQWVuTy1YcmFyVDBGTDhkOGwyRlBhNWFJWTVBTHNOOUlsSVFzVlB3bXFjZWZYaEhWblQwSU5yc00wU241V3BoVFEtTndGcURrVXc2eFBLMlFuZkdUSzdkUEpZNXctWHVvUjZTczUzRE4tNHA3eUgtVVN4NVZKWnZUd2NKRNIBqgFBVV95cUxNRGdVeDExV2J4SUxteXpvQVJqMWl2NmstN3lpR3dqaHU1djhwNkozR0pyZG5wZlhiRU9zSVdod0xyZWYwbEljVEpMOXdIelJzZFV3SVV3UHBvOUZzS3VKWGlLV3RIemFaZTFMOEh2ZlBDNW9fLXVlWXZSVU5RTGkxcHZzc1VSWU05SWdkMGtrZWR0aFJwb3FfZEs5bl9SQjJYWUJOTGVqU05iZw?oc=5) | 2026-06-05T07:00:00Z | confirmed | (추론) 추론: Google 이 xAI 데이터센터 컴퓨트를 쓰는 대가로 SpaceX 에 매달 $920M(연 약 $11B)을 낸다는 보도다. ⑦ 순환금융은 '내 매출을 내는 고객이 그 돈을 어디서 구했는가' 를 묻는데, Google 은 자기 영업이익으로 내는 고객이라 진짜 수요 쪽이다. 이 규모면 한 고객에 매출이 몰리는 ⑧ 비대칭 의존(끊기면 매출이 주는가)의 재료다. 스페이스X ⑦ 판단은 조달 의존 고객 비중이 작고 내 돈이 고객을 거쳐 돌아오지 않아 0점, ⑧ 판단은 머스크 개인·FAA 허가·국방·NVIDIA 의존으로 -3 이며 고객 집중 항목은 없다. (선별 확신: 중간) |
| EV-spacex-xai-002 | ⑤ 아군 | news | [Musk’s xAI, SpaceX hit with class action over data center ‘nuisance’ - Reuters](https://news.google.com/rss/articles/CBMiuAFBVV95cUxQbEFyQzQ4ZU9aVGpfNzdpR204a01GdlJQTFJvTERRNktfNTBVMDVyT2xXQWF0aTduWXNYUmVMRk8yT0s2RU5GZ0UwaVA3MlBOaGNGSFpXN01naTBHczNCdjU4WHV6empVc3ZPYTkxOGJrSkVmNnR2cW8wT0RlTnRDaV84dXVNVUtKZ21KTnktUERQWVlBTXdrZGkySTlQeG1fNkw4TWMycm9NWG5QMjdDc2dBQ3laYV9J?oc=5) | 2026-06-10T07:00:00Z | confirmed | (추론) 추론: xAI 데이터센터 인근 주민이 '생활 방해(nuisance)' 를 이유로 xAI·SpaceX 에 집단소송을 냈다는 보도다. 개별 소송은 ⑤ 의 적대 쪽 재료이고 사업 구조를 건드리지 않으므로 비용형이다. 스페이스X ⑤ 판단은 동맹 등급 +1(NASA·Space Force·국방부), 적대 등급 -1(비용형: EU 벌금·경쟁사·머스크 소송)로 3점이다. (선별 확신: 중간) |
| EV-spacex-xai-003 | ⑦ 순환금융, ⑨ 적자 깊이 | filing | [10-Q 2026-08-04](https://www.sec.gov/Archives/edgar/data/1181412/000162828026052535/spcx-20260630.htm) | — | confirmed | (추론) 추론: 스페이스X 의 가장 최근 정기 보고서(10-Q, 2026-06-30 기준)다. ⑨ 의 게이트 입력(영업손실률·최근 1년 잉여현금흐름·현금·약정)과 ⑦ 이 검토한 관계자 거래 주석의 원천이다. 스페이스X ⑨ 판단은 -3 이다. 게이트 1(본업이 영업이익을 내는가)에서 영업손실률 -16.2% 로 막혀 -10~-30% 구간에 들었고, 게이트 3(완충으로 버티는 기간)의 런웨이는 3.03년으로 임계 3년을 0.86% 차이로 넘겨 유지됐다. 스페이스X ⑦ 판단은 0점이며 이 보고서의 관계자 거래 주석(Tesla Megapack 구입·Valor 장비 리스)을 이미 검토했다. (선별 확신: 중간) |
| EV-spacex-xai-004 | ② 게임체인저 | news | [Introducing Grok 4.7 - xAI](https://news.google.com/rss/articles/CBMiP0FVX3lxTFBqb2x1bzQ3UkxTVDFCUVRjODMzbDJ5YTg3Nmh5Q2luZGdUTmctZmo1Ukp4c3RVdUhfSGZFc1p5SQ?oc=5) | 2026-09-21T07:00:00Z | confirmed | (추론) 추론: xAI 가 Grok 4.7 을 공개한 1차 발표다. 신모델 공개는 ② 신기술 게임체인저의 성능 경로를 다시 볼 계기이고, 벤더가 낸 벤치마크는 방증이다. 스페이스X ② 판단은 4점이다. Grok 4.6 이 Artificial Analysis Index 61(전체 6위)로 성능 경로를, Cursor 인수로 패러다임 적응 경로를 통과했고 표준 선점은 없다. (선별 확신: 중간) |
| EV-spacex-xai-005 | ⑤ 아군 | news | [SpaceX (SPCX) Wins $946 Million More from NASA. What Comes after the Space Station? - Yahoo Finance](https://news.google.com/rss/articles/CBMimAFBVV95cUxNcTRUVXc5OVB0U1hULWdWZlJtS2hwdFROWHlEMFkxM3FUVDhTWHBvVE1BSmlrc3BLTHJCc2JSeGUyX2toVG1STzd0NWFzYTZRN3lRbmI4bU1pN3YtbkJhQW9CaGEyTFFkWGN0VWpwSi1QdURIYUZXeGM2anAzMmFSZEdQb1RFTDF0bUEzckdtb3VWNm56a3RTWA?oc=5) | 2026-09-25T23:58:04Z | confirmed | (추론) 추론: SpaceX 가 NASA 에서 $946M 규모 계약을 추가로 따냈다는 2차 매체 보도다. 별표 H(조달과 동맹을 가르는 4문)의 판정 예시가 'SpaceX ← 미 정부' 를 동맹으로 보므로, 그 관계가 이어지고 커진다는 근거다. 스페이스X ⑤ 판단은 동맹 등급 +1(NASA·Space Force·국방부), 적대 등급 -1(비용형)로 3점이다. (선별 확신: 중간) |
| EV-spacex-xai-006 | ⑤ 아군 | news | [Elon Musk, SpaceXAI subpoenaed by NYC in AI safety investigation - cnbc.com](https://news.google.com/rss/articles/CBMiogFBVV95cUxNaVRaV1ZvZGVLN2Y3bG50TlZfTE14R1JfcXotZzRsR2FiZWFwaTJtUHNDbFhjbllzVzRFY3NHYXVmTGRmMVdWb3BfcTdJdzlSazVjQklmb0hQSmZEZVRqdm1tbTJxUURQc0JMZE4xUFFaN2tNZzRvMjQ3UnFPMVJYZkxmdElkMzNLN1ZuakJqX0VQNGdzNVF1TUNsX3hzZzhURUHSAacBQVVfeXFMUGlFS29DakNYYThBSEVpckxsWUtCN0RUX3VuaWdGa3JqOS14YU9wVEpSdjhBWTA3NzJGWFIyaUlQeS11UlRja0U2T0paSzVsZGJMRkE3NGotQi1XSmZ6Tm1nRlNMbkUydzYwalVaMHZkSHNDeExPQTRFOVk1Vl9pUEp4dWJUVDZSQnc2OURoMnVMVDNVdkNucUpSWEU1VnhGYk54UmxFWGM?oc=5) | 2026-09-28T19:01:56Z | confirmed | (추론) 추론: 뉴욕시가 AI 안전 조사로 머스크와 SpaceXAI 에 소환장을 냈다는 보도다. 지방정부 규제 조사는 ⑤ 의 적대 쪽 재료이고, 조사 단계라 비용형이다. 스페이스X ⑤ 판단은 동맹 등급 +1, 적대 등급 -1(비용형)로 3점이다. (선별 확신: 중간) |
| EV-spacex-xai-007 | ④ 호황 이후 | news | [SpaceX Launches Starship Flight 14, Deploys Starlink Satellites. - Investor's Business Daily](https://news.google.com/rss/articles/CBMingFBVV95cUxNaVRhMG1KOWZyTmRBVUxUeE5lakZDRVNKOG55NVh2ZGN2T2theGx0dzdhQU9SYUpLamdNWkJVcERKb05SM21vWDFoMmFZS2Q4ZUhESTA3VF9hVno0bGJnekhXeXdKM0VNcnZIaEliOXNERVhVczBMZ0pCN3k5TmdJNWxsUlZ6cDItbTJKNEowUlNIX0NCcXdYdGM0R3F1UQ?oc=5) | 2026-09-28T20:55:00Z | confirmed | (추론) 추론: Starship 14차 비행이 처음 궤도에 올라 Starlink 위성을 배치했다는 보도다. 실현된 성과라 ④ 호황 이후 비전(비AI 사업도 사업 부문으로 센다)의 근거다. 스페이스X ④ 판단은 5점으로 최고 구간이고 Starlink·Starship·xAI·X·Cursor·Terafab 을 부문으로 센다. (선별 확신: 중간) |
| EV-spacex-xai-008 | ⑦ 순환금융, ⑧ 비대칭 의존 | news | [Anthropic-SpaceX Compute Deal Size Revealed: Potential Spending Up to $84.5 Billion Nearly Doubles Prior Disclosure - TradingKey](https://news.google.com/rss/articles/CBMi0wFBVV95cUxOLVFGNlM4QjN1dW9aMUJ4Rmxfa3ZaeHlSN1htZVF2N29sdERIdE1zNE9MNHFkOEFtRlRxaVdtWGd3TVE4dE96MVZVeHhaM01fQVZLdnk3LTJKTC0yanhzQWg0dnViM09tdUd6TVRaeTI2a256ZzktQUFEeFk1ZDc5Z1FYcHdCUlhMNmQzWEtyRWREc0NmX2RwNnU3cG9pc19yUjNhVVhEZTZad0t2U3RsRktvdXVLaERIS3QxaVJTMjJiY2ttLWt0ekZ2a2ZtV1JiZUJv?oc=5) | 2026-09-30T09:12:12Z | confirmed | (추론) 추론: Anthropic 상장 신고서를 인용해, Anthropic 이 SpaceX 에 낼 컴퓨트 계약 총액이 최대 $84.5B 로 이전 공시의 두 배 가까이라는 보도다. SpaceX 쪽에서 보면 적자 고객(Anthropic)이 투자 유치·차입으로 마련한 돈으로 내는 매출이라 ⑦ 순환금융의 조달 의존 고객에 해당하고, 액수가 크면 ⑧ 의 고객 집중에도 해당한다. 스페이스X ⑦ 판단은 0점으로, Anthropic 계약(월 $1.25B, 2029년 5월까지)을 문면에 적고 있으나 조달 의존 고객 비중은 '작음'(Starlink 소비자·NASA·Space Force)으로 두었다. ⑧ 판단은 -3 이고 고객 집중 항목은 없다. (선별 확신: 중간) |

### Tesla

| 근거 ID | Factor | 종류 | 제목 | 발행시각(UTC) | 상태 | 관련성 |
| --- | --- | --- | --- | --- | --- | --- |
| EV-tesla-001 | ⑥ 가격, ⑨ 적자 깊이 | filing | [10-Q 2026-07-23](https://www.sec.gov/Archives/edgar/data/1318605/000162828026049270/tsla-20260630.htm) | — | confirmed | (추론) 추론: 테슬라의 가장 최근 정기 보고서(10-Q, 2026년 2분기)다. 영업현금흐름·설비투자는 ⑨ 게이트 2(최근 1년 잉여현금흐름이 마이너스인가)의, 매출·이익은 ⑥ 의 P1(최근 1년 이익 기준 PER)·P3(매출 성장)의 원천이다. CNBC(2026-07-22) 제목은 같은 분기를 '잉여현금흐름 마이너스 전환, 마진 하락' 으로 적는다. 테슬라 ⑨ 판단은 -1 이다. 게이트 1(본업이 영업이익을 내는가)을 통과했고, 게이트 2 의 최근 1년 잉여현금흐름은 +$5.76B 흑자이지만 영업이익이 57% 줄어 추세 악화로 본다. (선별 확신: 중간) |
| EV-tesla-002 | ④ 호황 이후 | news | [Tesla is beginning Semi electric truck deliveries - Reuters](https://news.google.com/rss/articles/CBMixgFBVV95cUxNX0ZFLVRhWm80M1ZOV2VHUUNXQXJPVVRXVEVRSkExYjRqRERCZ09WeVVUZzJuMUZYaUNObjVCY3BKWHVEb1FGMlRFN0o5ZEJ3NEJkWU52akcwODE0V0lFLXdEZVFVZGp2VHNYOUJodEQ1QVBQZmhpd2YwSDZ5U1hoOTlqMzlEMjg1NnlIbVRlQlRhSzZ4VzlsYUhDR1lNemd5SU9aVGpKRFNnWVF2Ukl2TDRhc1VtMk5SMHZGbHdVY0pUdm54OGc?oc=5) | 2026-09-24T23:09:00Z | confirmed | (추론) 추론: 테슬라가 Semi 전기 트럭 인도를 시작했다는 보도다. ④ 호황 이후 비전은 계획이 아니라 출하와 사업 부문을 세므로, 인도 개시는 ④ 에 쓸 수 있는 실측 사실이다. 테슬라 ④ 판단은 4점으로 에너지 저장·Optimus·로보택시·Terafab 으로 폭을 넓게 봤고, Optimus 는 아직 배치되지 않았다는 단서(긴장 #6: 배치 전 사업을 폭에 넣은 미해결 쟁점)를 달았다. (선별 확신: 중간) |
| EV-tesla-003 | ⑨ 적자 깊이 | filing | [8-K 2026-09-29 · Items 1.01, 1.02, 2.03, 9.01](https://www.sec.gov/Archives/edgar/data/1318605/000162828026063820/tsla-20260929.htm) | — | confirmed | (추론) 추론: 테슬라가 2026-09-29 신용계약 체결을 8-K 로 공시했다. Item 1.01(중요 계약 체결)·1.02(기존 계약 종료)·2.03(직접 금융 채무 발생)이 붙어 있고, 같은 날 Reuters·Bloomberg 제목은 규모를 $30B 로 적는다. 확정 미인출 여신은 ⑨ 완충(현금 + 확정 미인출 여신)의 직접 입력이다. 테슬라 ⑨ 판단은 -1 로, 게이트 1·2 를 통과해 완충을 쓰는 게이트 3 까지 가지 않는 경로다. 지금 관측된 확정 미인출 여신은 US$5,000M(2026-06-30)이다. (선별 확신: 중간) |
| EV-tesla-004 | ⑤ 아군 | news | [Safety group urges EU to reject Tesla FSD over speed offset - Reuters](https://news.google.com/rss/articles/CBMivwFBVV95cUxQQ0pPYVBiQTZoVXBmNnNuWlZLWVhwd0ZJckNOVWhhT3o4Q2cwLTVxZ1RaTy0zWVNJMHViYkNfZGVqTjB1ZFVJOUhtN18tZ3dNVDZZMW5RRU1vS0ZIWkpxbDZwS243UjFjMEJHa3p2Z2s0OUFFb3kxdlhCZXEwLVlRREdLdi1jWDlJcGpGY0ZZemVVakp0eWM0QXVjcGhCWDl5UzhaWG9VUEtrM1JXUDFINk1QUnNNOE85azBtZFdDOA?oc=5) | 2026-09-29T07:39:43Z | confirmed | (추론) 추론: 안전단체가 속도 허용 오차 설정을 이유로 EU 에 테슬라 FSD(감독형 자율주행) 승인을 거부하라고 요구했다는 보도다. 규제 전선의 반대는 ⑤ 의 적대 쪽 재료이고 사업 구조를 건드리지 않는 비용형이다. 테슬라 ⑤ 판단은 동맹 등급 0(유일한 아군 SpaceX 가 같은 지배주주 아래 관계사라 세지 않음), 적대 등급 -1(비용형: NHTSA FSD 조사·머스크 소송)로 2점이다. (선별 확신: 중간) |
| EV-tesla-005 | ⑦ 순환금융 | news | [Tesla Robotaxi fleets are the new crypto treasury for zombie companies - electrek.co](https://news.google.com/rss/articles/CBMilwFBVV95cUxPeFowNmhCbjY0d0prVHVhM0U0RExXUDE3V0Q3UFZDcVp4VktBV3pqNTl3c0dramhoMDdSUktrTmVVRWpNTGg4LXNuVW5NZmN4bTRiZlNGVlhIbUhmN3RzNkp1M0FQQktGTm9uX2p2dl9May1ZTFRydnVlOHhXM3o5NTBsV01iZ1ExNTNONGl0dERqWkxDVzNR?oc=5) | 2026-09-30T14:02:00Z | confirmed | (추론) 추론: 상장 부실기업들이 조달한 돈으로 테슬라 로보택시 차량을 사들인다는 칼럼이다. 사실이라면 ⑦ 순환금융의 질문('내 매출을 내는 고객이 그 돈을 어디서 구했는가')에서 조달 의존 고객에 해당한다. 테슬라 ⑦ 판단은 조달 의존 고객 비중이 작지만 관계사(xAI 투자·Terafab 합작) 사이로 내 돈이 돌아오는 구조가 있어 -1 이다. (선별 확신: 낮음) |
| EV-tesla-006 | ① 네트워크 | news | [2027 Tesla Model Y Performance gets $4500 price cut amid move to Chinese sourcing - carexpert.com.au](https://news.google.com/rss/articles/CBMiwgFBVV95cUxPREFlNGpsa1piQnlJUWpoTjFaVWxqWFh5ekQ2UkNra29kRUhQMm9qc3VFMDVtemRrekN6eXZFTVo4RkNSR0JQYzBvSkdHN1daMlM2Um5CcTlWbVJ6VHNDSWFEU29wSUREd0tMd3NNcEZDUEt5S3VOai1RWG9vREYtbFFVVTlWVnNtdnJPMDF3bE5ySnF0Q3U5N2VjWDJFR2R3WXVlYkJiMjA1Si1PRmFCUXB6WWh4TXdsXzZzUHhIWmRRUQ?oc=5) | 2026-10-01T00:30:00Z | confirmed | (추론) 추론: 호주에서 2027년형 Model Y Performance 가격이 $4,500 내렸다는 보도다. 가격 인하는 ① 의 판별 질문('가격을 올려도 남는가')에서 가격 결정력이 약하다는 신호다. 테슬라 ① 판단은 2점으로, 사용자 간 연결이 없어 스노우볼이 돌지 않고 가격 결정력이 없다(가격 인하 지속)고 적었다. (선별 확신: 낮음) |

### Oracle

| 근거 ID | Factor | 종류 | 제목 | 발행시각(UTC) | 상태 | 관련성 |
| --- | --- | --- | --- | --- | --- | --- |
| EV-oracle-001 | ⑤ 아군 | news | [Oracle and AWS Deepen Strategic Collaboration as Enterprise Adoption of Oracle AI Database@AWS Accelerates - Oracle](https://news.google.com/rss/articles/CBMi9AFBVV95cUxQZ185cDBzMXo5c2RXdTNrbFZiV0VuelJqdjVuN1Zld3VwU3NfdFVIck5HaGJSa3N6dzhwWWYxNVJxNkZ0aFktY0EzcGRNQ01wNm1mdnRvYUVKdDBKVTI1d044a3BfNEdFMEswTEhLSjBkX3pzNFNUdXRPanNaLWtySkx0d0VrQzRMVnhoMmFuNTVBZTJ6bTNWdE5DdGpwTHJwT3NWU01vejdYRngxbjltUTc0VmR6ZElWWGtDVHQzcGNoeWVjUHpRYjdBYXdBLWlGZ3BmdjRZSnlyWGhRTWFyOWJ6N2hHZEJSRHZfV1Mza2ZIZUF3?oc=5) | 2026-08-13T07:00:00Z | confirmed | (추론) 추론: Oracle 과 AWS 가 협력을 넓히고 Oracle AI Database@AWS 채택이 빨라진다는 Oracle 발표다. 경쟁 클라우드인 AWS 가 Oracle 데이터베이스를 자기 데이터센터·매대에서 고객에게 제공하는 관계라 ⑤ 동맹 등급의 근거 후보다. 지금 Oracle ⑤ 판단은 동맹 등급 +1(OpenAI 대형 계약·NVIDIA·TikTok 미국 법인·정부 클라우드), 적대 등급 -1(AWS·Azure·GCP 정면 경쟁, 비용형)로 3점이다. (선별 확신: 중간) |
| EV-oracle-002 | ⑥ 가격, ⑦ 순환금융 | filing | [8-K 2026-09-10 · Items 2.02, 8.01, 9.01](https://www.sec.gov/Archives/edgar/data/1341439/000119312526387905/orcl-20260910.htm) | — | confirmed | (추론) 추론: 2026-09-10 8-K(Item 2.02 실적 발표)는 Oracle 의 2026년 8월 분기(FY27 1분기) 실적이다. 흑자 기업이라 매출은 ⑥ 매출 성장 잣대(P3, 최근 1년 매출 ÷ 그 전 1년 − 1)의 입력이고, 같은 발표의 신규 AI 계약과 잔여 이행 의무(RPO, 계약했으나 아직 인식하지 않은 매출)는 ⑦ 의 'RPO ÷ 매출' 지표 근거다. 지금 Oracle ⑥ 매출 성장 입력은 2026-05-31 까지 최근 1년 매출 674억 달러, 성장률 약 17% 로 '15% 이상 30% 미만' 구간이고, ⑦ 판단은 '조달 의존 큼 + 환류 있음' 으로 -2(범위 최저점)다. (선별 확신: 높음) |
| EV-oracle-003 | ⑧ 비대칭 의존, ⑨ 적자 깊이 | filing | [10-Q 2026-09-11](https://www.sec.gov/Archives/edgar/data/1341439/000119312526389274/orcl-20260831.htm) | — | confirmed | (추론) 추론: 2026-08-31 분기 10-Q 로 Oracle 의 가장 최근 정기 보고서다. ⑨ 를 계산하는 현금·최근 1년 잉여현금흐름·RPO(계약했으나 아직 인식하지 않은 매출)와 ⑧ RPO 고객 집중의 1차 자료다. 지금 Oracle ⑨ 판단은 게이트 1(본업이 버는가) 통과, 게이트 2(최근 1년 잉여현금흐름) 마이너스 약 237억 달러, 게이트 3(버티는 기간) 약 1.3년으로 한 칸 하향, 게이트 4(약정 커버리지 = RPO ÷ 미개시 리스) 약 2.55배로 유지되어 -3 이고, 판단 입력 가운데 잉여현금흐름 추세(fcf_trend)는 '모름' 이다. ⑧ 판단은 -4(단일 고객이 백로그의 절반)다. (선별 확신: 높음) |
| EV-oracle-004 | ⑧ 비대칭 의존, ⑨ 적자 깊이 | news | [Oracle sends 'force majeure' notice about data center project — stock drops 3% - CNBC](https://news.google.com/rss/articles/CBMieEFVX3lxTE83OGFNcURydFoxR0o2WFYyX2ZTRkVUdno1UnNET2lrM0ZDVUdnZE11NWtMWFl1NnV1aU4tbXlLeFgtUEJVT2ZRY0tVcWxZWnpZR0g0a2owZDNYUHQ5Z05NZDY0aDAwUGhQMHZtUFZVd2lXX3Nnbkp5b9IBfkFVX3lxTE9xalhSV0NpQlJoUnQ4VDZGYUQtR1hnY1ZKMlVPVlRTelNaQk9qMTF5NzROY2xRcmFVNFJBQnY4QnlsVVRuOE53T1BtaDVxTXJlZlB2UzZhWmE2b0hPZmFlYlhZSDdDbU5lbEpGSnFvUGJtWVd5S1RZMGFvdG1Qdw?oc=5) | 2026-09-24T12:48:08Z | confirmed | (추론) 추론: Oracle 이 뉴멕시코 데이터센터(Project Jupiter) 공사에 불가항력 통보를 보냈다는 CNBC 제목이다. 약정 지출과 RPO 인식 시점에 닿아 ⑨ 게이트 4(약정 커버리지 = 계약된 수입 ÷ 미개시 약정)의 재료이고, 단일 고객을 위한 설비라 ⑧(비대칭 의존)의 재료다. 별표 I(⑦ 판정표)에 따라 이 선투자 위험은 ⑦ 이 아니라 ⑧·⑨ 에서 센다. 지금 Oracle ⑧ 판단은 -4(단일 고객이 백로그의 절반), ⑨ 판단은 -3(버티는 기간 약 1.3년으로 한 칸 하향, 약정 커버리지 약 2.55배로 유지)이다. (선별 확신: 중간) |
| EV-oracle-005 | ⑦ 순환금융, ⑧ 비대칭 의존 | news | [China’s Tencent leases 100,000 chips from Oracle to accelerate AI push, FT reports - Reuters](https://news.google.com/rss/articles/CBMiuwFBVV95cUxNR3F1ZTMtVFZsOVNXOEU4X09jTTI0RDVYNUJmQUNVVUhJQkV6YlRmdldFaWwyVzU1UnZLQl9Ia0tqTHlBZ09SUXZ6VC1kcEx6bjQyQlgxXzI1YVpwYldSV3NwNXZRRkFPSWQzclhFbE04anBtbnRZV2FwRUlIMmU2eVV3M0VscEE1Znd5bU5rNEhwWVVXdlR0c2tIbnlnald3VVBJdVFiTDZMUmhqV0x1bE1jVVR2STZ5bHdF?oc=5) | 2026-10-01T03:12:00Z | confirmed | (추론) 추론: Tencent 가 Oracle 에서 칩 10만 개를 70억 달러에 임차한다는 FT 보도를 Reuters 가 전했다. OpenAI 이외의 대형 고객이라 ⑧ 단일 고객 의존을 덜어 주는 반대 근거이고, Tencent 는 자기 영업이익으로 지불할 수 있는 고객이라 ⑦ 의 '조달 의존 고객 비중' 축 근거다. 지금 Oracle ⑦ 판단은 '조달 의존 큼 + 환류 있음' 으로 -2(범위 최저점), ⑧ 판단은 -4(단일 고객이 백로그의 절반)다. (선별 확신: 중간) |

### OpenAI

| 근거 ID | Factor | 종류 | 제목 | 발행시각(UTC) | 상태 | 관련성 |
| --- | --- | --- | --- | --- | --- | --- |
| EV-openai-001 | ② 게임체인저 | news | [Exclusive \| OpenAI Scraps Release of New AI Model Over Safety Concerns - WSJ](https://news.google.com/rss/articles/CBMihgFBVV95cUxNcC0xNDExdTJodUowZi1yeWdFN3M5RlpvY3FvZ1lQeHltWGVkeG01ZTVlaHJ0TldqVVRhekJhWl9ZRTRLNHRqX1NQQVFKMW5NRnhBTmlUNWNpX1FBX3Myc3VlaGIxbFZTZDZYRlYwTGNVLTUtNnJScGJWcm5rX0hMMmNadFFmZw?oc=5) | 2026-09-28T23:07:00Z | confirmed | (추론) 사실: WSJ 가 OpenAI 가 안전 문제로 새 AI 모델 출시를 접었다고 단독 보도했다. 추론: OpenAI ② 판단은 세 경로(성능 도약·패러다임 적응·표준 선점) 중 성능 도약과 패러다임 적응 둘을 통과해 4점이고, 적응 경로의 근거 하나가 GPT-5.5→5.6→6 의 연속 출시 속도다. 상위 모델 출시를 접은 것은 그 출시 속도에 반대 방향 사실이다. 출시되지 않은 모델은 성능 도약 경로에 세지 않는다. (선별 확신: 중간) |
| EV-openai-002 | ⑥ 가격 | news | [Scoop: OpenAI's annual recurring revenue nears $70B - axios.com](https://news.google.com/rss/articles/CBMiiAFBVV95cUxQT2xYcWJPOUFTTWFUWmpMSFN1UzdQc3ZoWmFFUEpsTFJFcjZBbkdqemNrN18ydnpIQnJyR09xMW9Ba2ZHWkFwRUMyMlZLcFkxQ1dDdl9mb1MxZnYwcExXcGNFTFQ3UHBTbERwM2pVYzdwcnZ6MnNSM3NHbE5VODFfaXNhX3dsQjF3?oc=5) | 2026-09-29T14:15:48Z | confirmed | (추론) 사실: Axios 가 OpenAI 의 연간 반복 매출(ARR)이 $70B 에 가까워졌다고 보도했다. 추론: 비상장 ⑥(현재 가격의 정도)은 밸류를 최근 1년(TTM) 보정 매출로 나눈 배수(P2, 밸류÷매출) 하나로 매기고, ARR 은 그 분모를 뒷받침하는 근거로만 쓴다. OpenAI ⑥ 은 프로그램이 계산하며 -4점이다 — post-money $852B 를 TTM 보정 매출로 나눈 약 39배로 가장 비싼 구간(30배 이상)에 들고, 한 칸 올리는 보정은 매출 성장이 런레이트라 인정되지 않고 자본효율(ARR÷누적 조달 0.22)도 기준 0.5 에 못 미쳐 걸리지 않았다. 비상장사의 ARR 보도는 ⑥ 분모의 근거로만 쓰므로 ③ 후발 가속도에는 배정하지 않았다. (선별 확신: 중간) |
| EV-openai-003 | ② 게임체인저 | news | [Introducing GPT-6.1 Sol - OpenAI](https://news.google.com/rss/articles/CBMiXkFVX3lxTE1fNFpCaXpwdjNfd3pjTWZ6X1ljNS03RTNaS2k2UE5LZ1ZnbHJVVWstREg4UWdKWjg3Y3FpT1JJTS1OOVA2SjR5WXBoZ3ZXX0ZTek9td3p3SHVsOHRSM0E?oc=5) | 2026-09-29T17:10:11Z | confirmed | (추론) 사실: OpenAI 가 신모델 GPT-6.1 Sol 을 자사 발표로 공개했다. 추론: 신모델은 ②(게임체인저)를 다시 볼 계기지만 회사가 발표한 벤치마크는 1차 근거가 아니고 독립 측정이 우선이다. OpenAI ② 판단은 세 경로(성능 도약·패러다임 적응·표준 선점) 중 둘을 통과해 4점이고, 최상단으로 못 가는 이유로 '종합 지능이 전작과 동점(AA Intelligence Index 61 = GPT-5.6 Sol 61)' 을 적고 있다. 최상단은 성능 도약이 세대 격차 수준일 때 준다. (선별 확신: 중간) |
| EV-openai-004 | ② 게임체인저 | news | [OpenAI Unveils Always-On AI Agent Dots, New $500 Paid Tier - Bloomberg.com](https://news.google.com/rss/articles/CBMiqwFBVV95cUxNVkdWY0tGVFAtWVplbzRxRmNxdzJaQ0JVSVFTbXBEZHVvZnJRRUtGNUF4Q05kU1ZyNGNUYjgwWld3WWltZWpmSUNuX3ZFX3czSDlhbFh6S1psUU1rTkRSdjlCYUlNak53b3dCZDRqcmZFMVNOMk1NWEFSNkJCTGR2enBRckM0STVVd3I2VmMtOUxnQVJCS1dZa0tNRmhwam9wYThHcUoteWU3NUU?oc=5) | 2026-09-29T17:22:25Z | confirmed | (추론) 사실: Bloomberg 가 OpenAI 가 상시 동작 AI 에이전트 Dots 와 월 $500 유료 요금제를 내놨다고 보도했다. 추론: 남이 먼저 연 판(Meta Muse)에 올라타는 것은 ②(게임체인저)의 패러다임 적응 경로 재료다. 다만 출시는 계기이고 이용자·유료 전환 같은 채택 수치가 있어야 근거가 된다. OpenAI ② 판단은 세 경로 중 성능 도약과 패러다임 적응 둘을 통과해 4점이다. (선별 확신: 낮음) |
| EV-openai-005 | ⑤ 아군 | news | [Advocates sue OpenAI over Hugging Face hack under California anti-hacking law - Politico](https://news.google.com/rss/articles/CBMixAFBVV95cUxQbFBxM0d5dzFnM25xWGt3ZVl1cVd3Rl9haHpyLVI3Wm1uWHItVjFMN2VsNVBEVVNQSDNXVlJabmkycmN2S1IxSy1oS2ZvSTk4RDV5U2h4Q3A0bXd2UzdUOENPbnFNcXRPaXBQUHNoSUI4YWM5VURwdzBoWmVGM2Q3VTlqemk1MkZhRDlkY3JvTHBYVEhiUWRyOXZkUzl5cHI1Z3I1eXduX3ZQMW9KbHNOYmh1Q2xyWG5NcUdZMU1MdnM3LXdF?oc=5) | 2026-09-29T19:14:00Z | confirmed | (추론) 사실: Politico 가 시민단체들이 OpenAI 에이전트의 Hugging Face 침해를 이유로 캘리포니아 해킹 금지법에 근거해 OpenAI 를 제소했다고 보도했다. 추론: 소송은 ⑤(아군과 적대)의 적대 등급 재료이고(별표 C: 적대는 수가 아니라 성격을 본다), 에이전트 제품의 적법성을 겨냥한다는 점에서 사업 정당성을 표적으로 한 '구조형' 쪽으로 읽힐 수 있다. OpenAI ⑤ 판단은 동맹 등급 +1, 적대 등급 -3(다발형: 구조형 적대가 여러 전선에서 동시에 진행되고 최대 파트너와도 긴장)으로 1점이다. (선별 확신: 중간) |
| EV-openai-006 | ③ Last Mover | news | [Disrupting a coordinated model-distillation campaign - OpenAI](https://news.google.com/rss/articles/CBMihAFBVV95cUxQbEgxOFhvU3ZzR0JYMjZDbWhRaXlQeGoyci1PRGhfWkFhSGpER29fLXZydWRybEdpVEhUX0dCZ3pwS0ViUWRxVy1NVXZNREVfN2pOMU96c2NmSmlpY1lheUwxMGxuVjlmTV9uSkszVHU0RFhVVVNNUU42TkNjb084cThtaWc?oc=5) | 2026-09-30T17:06:44Z | confirmed | (추론) 사실: OpenAI 가 경쟁 연구소의 조직적 모델 증류(다른 모델의 출력을 대량으로 받아 능력을 베끼는 학습) 시도를 차단했다고 발표했다. 추론: 모델 능력이 비교적 싸게 복제될 수 있다는 뜻이라 ③(Last Mover)의 모방 불가능성 실패 판정을 받치는 재료다. OpenAI ③ 판단은 2점이다 — 모방 불가능성 ❌, 별도 수익모델 ❌, 후발 가속도 ✅(ARR $25B 정체 뒤 7월 $40B 로 재가속). (선별 확신: 낮음) |
| EV-openai-007 | ⑤ 아군 | news | [FTC opens probe into AI giants including Anthropic and OpenAI - Reuters](https://news.google.com/rss/articles/CBMiwgFBVV95cUxQdzYzcTVSY1JmRld3cFRBRlRaX0w0YVZHTjU3NWVvVG5BcXFIZGFwdXViLXBLNnhJQ3d0RS13T2VURWdNQ19ySkJuVXNlV2NWX0E3LUExYUZQaFBsTTVEaC1NMXJtR0RGYlllQVotQmM3VlRaVmd2em04YWdzTXFkMjhsUlQ0b1JlcVJBRENNRFFBT1NLcU00YUtqU0N5LUlJa0YxaEhzdU1mR1lkUTJ0MFhLMjA3a1FJVlQ5RXpMOEIxdw?oc=5) | 2026-09-30T18:17:19Z | confirmed | (추론) 사실: Reuters 가 FTC(미 연방거래위원회)가 Anthropic·OpenAI 를 포함한 AI 대기업 조사를 열었다고 보도했다. 추론: 규제기관 조사는 ⑤(아군과 적대)의 적대 등급 재료다(별표 C: 적대는 수가 아니라 성격을 본다). OpenAI ⑤ 판단은 동맹 등급 +1, 적대 등급 -3(다발형: 구조형 적대가 여러 전선에서 동시에 진행되고 최대 파트너와도 긴장)으로 1점이고, 적대 근거는 MS 와의 긴장·Apple 소송·머스크 반독점 소송·MDL 3143 저작권 집단소송이다. (선별 확신: 중간) |
| EV-openai-008 | ⑤ 아군 | news | [OpenAI and Synopsys Announce GPT-Synopsys: Frontier Intelligence to Revolutionize Chip Design - Synopsys](https://news.google.com/rss/articles/CBMiyAFBVV95cUxPWmx4bUlpbGx3MEpZYlhQSnRtVDVxejJ5bnZoU3FabmRPaHdHdGM2Zjg5OEpydUxGQ3pac1BSX3psbnhieWpVVnFweWJ5czJfZk9vbU9TaTIyZm5ROW92RzZzWmJ0NlJjQVlZQnR0MGtyb3JzTW5NYWIxQVJsNi0zSHRLUS0xa2VFQ0FEQnpuWGpMQVFpa1RoSTYybTFzal9lQkZJYmNBLXFKaFVWQUNLSTN5TGY1WUgxbmwzY2lzVmRGbmhrSGJLMw?oc=5) | 2026-09-30T18:35:06Z | confirmed | (추론) 사실: Synopsys 가 OpenAI 와 칩 설계용 모델 GPT-Synopsys 를 함께 만든다고 발표했다. 추론: 별표 H(조달과 동맹을 가르는 4문)의 1문은 지분·독점·공동개발·재판매 권리·수수료 분배를 동맹 후보로 본다. 공동개발이고 OpenAI 가 모델을 공급하는 쪽이라 조달이 아니다. OpenAI ⑤ 판단은 동맹 등급 +1, 적대 등급 -3(다발형)으로 1점이다. 동맹 등급 최상단은 '지분이 걸린 동맹이 복수' 이거나 '경쟁사까지 내 매대·플랫폼에 편입' 일 때인데, 지금 지분이 걸린 동맹은 Stargate 하나뿐이라 서지 않았다. (선별 확신: 낮음) |

- `candidate` 근거는 새 판단(`status: new`)이 인용할 수 없다. 사람이 확인해 `confirmed` 로 올린 근거만 인용한다.

## 트리거(활성)

| ID | 기업 | Factor | 관찰 사실 | 조건 | 기한 | 근거 | 재검토 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| TRG-001 | Alphabet / Google | ② 게임체인저 | 구글이 2026-09-30 최상위 모델 Gemini 4 Argon 을 발표했고(제목 기준) 같은 날 구글 내부의 성능 회의론 보도도 나왔다. 알파벳 ② 판단은 기준선에서 승계한 4점이고 근거는 “프론티어 순위 미변”이다. | AA Intelligence Index·ARC-AGI-2·에이전트 실무 측정 같은 독립 측정에 Gemini 4 Argon 이 등재되면 | 2026-11-15 | EV-alphabet-007 | 알파벳 ② 의 성능 도약 경로(벤치마크에서 세대 격차를 만드는가) 통과 여부와, 그 격차가 ② 최고 칸의 조건인 세대 격차 수준인지 |
| TRG-002 | Alphabet / Google | ⑤ 아군 | 구글이 EU 의 검색 데이터 공유·AI 접근 개방 명령에 이의를 제기하고 EU 법원에 집행정지를 신청했다. 별도로 반독점 승소 보도(2차 매체)가 있다. 알파벳 ⑤ 판단은 동맹 등급 +2, 적대 등급 -1(비용형)로 4점이고 적대 근거는 “DOJ+38개 주 검색 독점 항소 진행”이다. | EU 법원의 집행정지 판단이 나오거나 명령 이행이 시작되면, 또는 승소한 사건이 무엇인지 판결문·주요 언론 같은 1차 자료로 확인되면 | 2026-12-31 | EV-alphabet-005, EV-alphabet-004 | 알파벳 ⑤ 적대 등급을 비용형으로 둘지(EU 명령이 검색 사업 구조를 건드리면 구조형 검토)와, 적대 근거 “DOJ+38개 주 항소”가 지금도 맞는지 |
| TRG-003 | Alphabet / Google | ⑦ 순환금융 | Anthropic IPO 신고서(S-1)가 Anthropic 매출의 절반 가까이가 Amazon·Google 을 거친다고 밝혔다는 보도가 있다. 알파벳 ⑦ 판단은 조달 의존 고객 비중 ‘작음’, 내 돈이 돌아옴 ‘예’로 별표 I(⑦ 순환금융 판정표) -1 칸이다. | Anthropic S-1 원문에서 구글 관련 컴퓨트 약정·매출 규모가 확인되면 | 2026-11-30 | EV-alphabet-006 | 알파벳 ⑦ 의 조달 의존 고객 비중을 ‘작음’으로 둘지 — 구글 쪽 Anthropic 매출·약정을 Google Cloud 매출·백로그와 견준다 |
| TRG-004 | Amazon / AWS | ⑦ 순환금융 | Anthropic 이 클라우드·데이터센터에 $518B 를 쓸 계획이고 그중 $100B+ 가 아마존에 약속됐다는 보도가 있다. 아마존 ⑦ 판단은 조달 의존 고객 비중 ‘작음’, 내 돈이 돌아옴 ‘예’로 별표 I(⑦ 순환금융 판정표) -1 칸이고, 근거에 “OpenAI $50B 투자 ⑦ 재검토 대기”가 남아 있다. | Anthropic S-1 원문이나 아마존 다음 10-Q 에서 Anthropic·OpenAI 약정의 규모·기간이 확인되면 | 2026-11-30 | EV-amazon-007 | 아마존 ⑦ 의 조달 의존 고객 비중을 ‘작음’으로 둘지 — Anthropic·OpenAI 약정을 AWS 백로그·매출과 견준다 |
| TRG-005 | Amazon / AWS | ⑨ 적자 깊이 | 아마존의 최근 1년 잉여현금흐름이 -$11.6B 로 마이너스라 ⑨ 게이트 2(최근 1년 잉여현금흐름이 마이너스인가)에 걸려 있고, 2026-06-10 에 중요 계약·직접 금융 채무 공시(8-K Items 1.01·2.03)가 있었다. 지금 런웨이는 9.95년(완충 $115.7B = 현금 $78.2B + 확정 미인출 여신 $37.5B), 약정 커버리지는 1.856 이다. | 2026년 3분기 10-Q 가 공시되면 | 2026-11-10 | EV-amazon-002, EV-amazon-001 | 아마존 ⑨ 게이트 3(현금 + 확정 미인출 여신으로 몇 년 버티는가)과 게이트 4(남은 계약 매출이 미래 지출 약정을 덮는가)를 새 분기의 최근 1년 잉여현금흐름·현금·확정 미인출 여신으로 다시 계산한다 |
| TRG-006 | Amazon / AWS | ① 네트워크 | 아마존이 메타 Muse 쇼핑 에이전트를 차단했다(제목 기준). 아마존 ① 판단은 5점(Prime 2억+ 소비자 락인)이다. | 에이전트 경로로의 소비자 이탈 수치(Prime 회원 수·쇼핑 트래픽)가 공시되거나 보도되면 | 2027-02-15 | EV-amazon-004 | 아마존 ① 소비자 채널 락인이 제3자 쇼핑 에이전트 경로에서도 유지되는지 |
| TRG-007 | Microsoft | ① 네트워크 | 마이크로소프트가 Copilot Business 라이선스에 사용량 기반 과금을 기본값으로 켠다는 보도(crn, 2026-09-30)가 있다. 계획 단계라 별표 D(계획·발표는 현재 점수에 넣지 않는다)에 따라 근거로 올리지 않았다. 마이크로소프트 ① 판단은 5점(Copilot 유료 시트 3,000만, Windows·M365 기본 탑재)이다. | FY27 1분기 실적에서 Copilot 유료 시트 수나 이탈이 공시되면 | 2026-11-10 | — | 가격 구조를 바꾼 뒤에도 Copilot 유료 시트가 유지되는지 — 마이크로소프트 ① 업무 채널 락인 |
| TRG-008 | Microsoft | ⑤ 아군 | OpenAI 가 M365 와 겹치는 오피스 제품을 냈고, 같은 주 마이크로소프트는 OpenAI 의 Dots 에이전트를 기업용으로 들여왔다. 마이크로소프트 ⑤ 판단은 동맹 등급 +2, 적대 등급 -1(비용형: OpenAI 긴장·Azure 독점 소멸)로 4점이다. | MS–OpenAI 계약 변경 공시나 M365 고객 이탈 수치가 나오면 | 2026-12-31 | EV-microsoft-003 | 마이크로소프트 ⑤ 적대 등급을 비용형으로 둘지, 구조형(주요 고객·파트너가 곧 경쟁자)으로 볼지 |
| TRG-009 | Microsoft | ② 게임체인저 | 마이크로소프트가 에이전트(Autopilot)·코딩(Code)을 묶은 새 Copilot 을 출시했다. 마이크로소프트 ② 판단은 기준선에서 승계한 3점이고 근거는 “Arena 상위권에 자체 모델 없음, OpenAI·Anthropic 양쪽 조달”이다. | 에이전트 실무 독립 측정(OSWorld·Terminal-Bench 등)이나 Autopilot 채택 수치가 공개되면 | 2026-12-31 | EV-microsoft-002 | 마이크로소프트 ② 의 패러다임 적응 경로(남이 바꾼 판 — 에이전트·코딩 — 에 빨리 올라타는가) 통과 여부 |
| TRG-010 | Meta | ⑨ 적자 깊이 | 메타의 최근 1년 잉여현금흐름은 +$40.98B 흑자지만 분기 잉여현금흐름이 -91% 줄었고 설비투자 계획이 연 $130~145B 로 늘었다. 메타 ⑨ 판단은 게이트 2(최근 1년 잉여현금흐름이 마이너스인가)에서 흑자로 끝나고 추세는 악화다. | 2026년 3분기 10-Q 가 공시되면 | 2026-11-10 | EV-meta-001 | 메타의 최근 1년 잉여현금흐름 부호와 추세 — 마이너스로 바뀌면 ⑨ 게이트 3(현금 + 확정 미인출 여신으로 몇 년 버티는가) 계산에 들어간다 |
| TRG-011 | Meta | ③ Last Mover | 메타 Muse 주간 사용자가 300만을 넘었다는 보도(The Information 단독)가 있다. 메타 ③ 판단에서 후발 가속도(성장률이 오르는가)는 “AI 매출 미공시, 채택 증거 아직 없음”으로 ⚠️ 절반 인정이다. | 메타가 3분기 실적에서 Muse 사용자나 수익화 수치를 공식 공시하면 | 2026-11-10 | EV-meta-004 | 메타 ③ 후발 가속도를 ⚠️ 절반 인정으로 둘지, 인정 쪽으로 볼지 |
| TRG-012 | Meta | ④ 호황 이후 | 메타가 기업용 AI 플랫폼을 출범하고 MongoDB CEO 를 책임자로 영입했다. 별표 D(계획·발표·인사는 현재 점수에 넣지 않는다)에 따라 지금은 근거가 아니다. 메타 ④ 판단은 3점(광고 의존 약 98%)이다. | 기업용 매출이나 고객 배치가 공시되면 | 2027-02-15 | EV-meta-002 | 메타 ④ 다각화 — 광고 밖 사업 부문이 실질 매출을 내는지 |
| TRG-013 | NVIDIA | ⑤ 아군 | 같은 주에 두 보도가 나왔다. 중국 당국이 ByteDance·Alibaba 의 NVIDIA 신형 칩 구매 허용을 검토한다는 보도(Reuters 가 The Information 인용)와, 미 의회가 국방수권법으로 중국 대상 AI 칩 수출을 막으려 하고 NVIDIA·AMD 가 행정부 개입을 요청한다는 보도(Politico)다. 지금 NVIDIA ⑤ 판단은 동맹 등급 +1, 적대 등급 -2(구조형 — 주요 고객이 곧 경쟁자)다. | 중국 당국의 구매 허용이나 미 의회의 수출 차단 조항 확정 가운데 하나가 정부 발표·법안 문안 같은 1차 자료로 확인될 때. | 2026-12-31 | — | 중국 시장 차단의 범위가 바뀌는지 본다. 시장 일부 차단은 비용형 적대라, 지금 구조형인 적대 등급을 바꾸려면 이것이 두 번째 구조형 전선이 되는지(다발형: 구조형 적대가 복수 전선에서 동시에 진행되고 최대 파트너와도 긴장)를 따진다. |
| TRG-014 | NVIDIA | ② 게임체인저 | 고객사 CoreWeave 가 Vera Rubin NVL72 를 생산 규모로 제공한다고 발표했다. 지금 NVIDIA ② 판단은 5점(최상단)이고, 그 note 는 Rubin 을 '발표' 로 적어 두었다. | NVIDIA 분기 실적이나 10-Q 에서 Rubin 매출 인식이 확인되거나, 독립 측정(MLPerf 등)에서 Rubin 의 세대 격차 수치가 나올 때. | 2026-11-30 | EV-nvidia-008 | ② 판단 note 의 Rubin 표기를 '발표' 에서 '출하' 로 고칠지, 성능 도약 경로의 세대 격차 근거를 벤더 발표가 아닌 독립 측정으로 바꿀 수 있는지 본다. |
| TRG-015 | NVIDIA | ④ 호황 이후, ⑤ 아군 | NVIDIA 의 Hugging Face 관련 130억 달러 거래가 보도됐다. 기존 NVIDIA ① 판단은 이 거래를 2026-09-02 에 서명한 인수(종결 2027 상반기·규제 승인 조건부)로 적고 있고, ⑤ 판단은 'HF 인수는 ⑤ 근거가 아니다' 라고 적어 두었다. 지금 NVIDIA ④ 는 5점(최상단)이다. | 거래 구조(인수인지 지분 투자인지)와 종결이 NVIDIA 공시로 확인될 때. | 2027-01-31 | EV-nvidia-004 | 인수로 종결되고 Hugging Face 매출이 NVIDIA 부문으로 잡히면 ④ 사업 부문 근거를 보강한다(점수는 이미 최상단). 지분 투자로 드러나면 ⑤ 동맹 등급('지분이 걸린 동맹이 복수')에 들어가는지 별표 H 3문(상대가 나를 떠날 수 있으면 동맹이 아니다)을 대어 본다. 기존 ① 판단 note(종결 시 업무 채널이 생겨 부품 채널 상한을 넘길 경로)도 함께 확인한다. |
| TRG-016 | TSMC | ⑤ 아군, ⑧ 비대칭 의존 | TSMC 가 애리조나에 이어 텍사스에 두 번째 미국 거점을 검토한다는 보도(Reuters, 소식통 인용)가 나왔다. 지금 TSMC ⑤ 판단의 적대 등급은 -1(Intel Foundry·관세로 강요된 미국 투자)이고, ⑧ 판단은 -4(첨단 캐파가 물리적으로 대만에 집중)다. | TSMC 이사회 결의(6-K)나 공식 발표로 텍사스 투자가 확정될 때. | 2026-12-31 | — | ⑧ 의 생산 지역 집중 근거와 ⑤ 의 관세·지정학 적대 근거가 달라지는지 본다. 확정돼도 별표 D(계획·발표는 점수 근거가 아니다)에 따라 공장이 가동·출하하기 전에는 근거 문장만 고친다. |
| TRG-017 | TSMC | ② 게임체인저, ⑥ 가격 | 2나노 상업 양산 시작이 2차 매체로 보도됐고, 3분기 실적 발표가 2026-10-15 로 예정돼 있다. 지금 TSMC ② 판단은 5점(최상단)이고 근거에 N2 양산 시작이 이미 있다. TSMC ⑥ 은 20-F 연간 수치로 계산하는 트랙이다. | 3분기 실적에서 N2 매출 비중과 분기 매출 성장률이 공개될 때. | 2026-10-31 | EV-tsmc-004 | N2 출하를 1차 자료로 확인해 ② 근거 문장을 보강한다. ⑥ 매출 성장 잣대(P3, 최근 1년 매출 ÷ 그 전 1년 − 1)는 연간 트랙이라 분기 실적으로 입력이 바뀌지 않으므로, 분기 성장률은 2026 연간 20-F 가 들어올 때까지 참고로만 남긴다. |
| TRG-018 | TSMC | ⑤ 아군 | Intel CEO 가 TSMC 를 경쟁자가 아니라 파트너라고 발언했다. 지금 TSMC ⑤ 판단은 동맹 등급 +1, 적대 등급 -1 이고, 2026-09-15 엄격 재판정은 TSMC 자신의 경쟁사(Intel Foundry·Samsung 파운드리)가 TSMC 공정에 들어온 근거가 없다고 보았다. | Intel 의 TSMC 위탁 생산 물량이나 계약이 Intel·TSMC 공시 또는 1차 발표로 확인될 때. | 2026-12-31 | EV-tsmc-007 | 동맹 등급의 '경쟁사까지 내 공정에 편입했다' 조항을 TSMC 에 다시 대 보고, 같은 잣대가 닿는 다른 회사가 있는지 함께 확인한다(체크리스트 Q03: 한 회사에 댄 잣대는 같은 잣대가 닿는 모든 회사에 댄다). |
| TRG-019 | Apple | ④ 호황 이후 | Apple 이 10월 13일 스마트홈 허브를 내놓을 계획이라는 Bloomberg 보도가 나왔다. 계획이라 별표 D(계획·발표는 점수 근거가 아니다)에 따라 근거로 올리지 않았다. 지금 Apple ④ 판단은 3점이다. | 출시 뒤 출하량이나 별도 매출이 공시·실적에서 확인될 때. | 2027-02-15 | — | 새 제품군이 ④(호황 이후 비전 — 사업 부문 수·자체 칩 출하)의 사업 부문으로 셀 만큼 매출·배치가 생겼는지 본다. |
| TRG-020 | Apple | ① 네트워크 | 메모리 칩 부족으로 Apple 이 제품 가격을 올린다는 보도(Stocktwits, '보도에 따르면')가 나왔다. 지금 Apple ① 판단은 5점(최상단, 20억 대 설치기반의 소비자 채널)이다. | 가격 인상이 확정되고 다음 분기 실적에서 iPhone 매출·설치기반 변화가 나올 때. | 2027-02-15 | — | ① 의 판별 질문 '가격을 올려도 남는가' 를 확인한다. 인상 뒤 이탈이 없으면 근거 문장을 보강하고, 매출·설치기반이 뚜렷이 줄면 ① 락인 판정을 아래쪽으로 다시 본다. |
| TRG-021 | Apple | ④ 호황 이후 | 규칙 별표 D(계획·발표는 점수 근거가 아니다)는 Apple Baltra(자체 AI 서버 칩)를 '2026 하반기 양산 예정, 양산 확인 시 상향' 으로 적어 두었다. 이번 후보 묶음에는 양산을 확인하는 기사가 없다. 지금 Apple ④ 판단은 3점이다. | Baltra 양산·배치가 Apple 공시나 1차 발표로 확인될 때. | 2026-12-31 | — | ④ 의 수직계열화 입력인 자체 칩 출하가 생겼는지 보고, 확인되면 ④ 를 위쪽으로 다시 본다. |
| TRG-022 | Oracle | ⑧ 비대칭 의존, ⑨ 적자 깊이 | 뉴멕시코 Project Jupiter 에 불가항력 통보가 보도됐고, 위스콘신 1.3GW 데이터센터 지연 가능성 보도(미확인)가 이어졌다. 지금 Oracle ⑧ 판단은 -4(단일 고객이 백로그의 절반), ⑨ 판단은 -3(버티는 기간 약 1.3년으로 한 칸 하향, 약정 커버리지 약 2.55배로 유지)이다. | Oracle 10-Q·8-K 에서 자본지출 약정 일정, RPO(계약했으나 아직 인식하지 않은 매출) 인식 시점, 고객 계약 조정 가운데 하나가 바뀐 것이 확인될 때. | 2026-12-20 | EV-oracle-004 | ⑨ 게이트 4(약정 커버리지 = 계약된 수입 ÷ 미개시 약정, 1배 미만이면 한 칸 하향)를 다시 계산하고, ⑧ 의 단일 고객 설비 의존 근거가 달라지는지 본다. |
| TRG-023 | Oracle | ⑦ 순환금융, ⑧ 비대칭 의존 | Tencent 가 Oracle 에서 칩 10만 개를 70억 달러에 임차한다는 FT 보도를 Reuters 가 전했다. 지금 Oracle ⑦ 판단은 '조달 의존 고객 비중 큼 + 내 돈 환류 있음' 으로 -2, ⑧ 판단은 -4(단일 고객이 백로그의 절반)다. | Oracle 실적 발표·공시나 Tencent 측 확인으로 계약 규모와 기간이 확인될 때. | 2026-12-20 | EV-oracle-005 | RPO 고객 구성이 얼마나 분산됐는지와 자기 영업이익으로 지불하는 고객의 비중이 늘었는지 본다. ⑦ 의 '조달 의존 큼' 과 ⑧ 의 단일 고객 의존 판정을 뒤집을 만큼인지가 기준이다. |
| TRG-024 | Oracle | ⑨ 적자 깊이 | Oracle ⑨ 판단의 잉여현금흐름 추세 입력(fcf_trend)이 '모름' 으로 남아 있고, 최신 10-Q(2026-08-31 분기)가 들어왔다. 지금 Oracle ⑨ 판단은 게이트 2(최근 1년 잉여현금흐름) 마이너스, 게이트 3(버티는 기간) 약 1.3년으로 한 칸 하향되어 -3 이다. | 다음 10-Q(2026-11-30 분기)까지 받아 최근 1년 잉여현금흐름의 추세를 판정할 수 있을 때. | 2026-12-20 | EV-oracle-003 | 추세 입력을 채우고 게이트 판정을 다시 확인한다. Oracle 은 잉여현금흐름이 마이너스라 점수는 버티는 기간과 약정 커버리지가 정하고, 추세 입력은 판단 기록을 채우는 의미가 크다(추론). |
| TRG-025 | Alibaba | ② 게임체인저, ④ 호황 이후 | 2026-09-21~23 알리바바가 자체 AI 가속기(Zhenwu V900)를 공개했고, 10조 파라미터 Qwen 모델과 2032년까지 20GW 데이터센터 계획이 함께 보도됐다. 셋 다 공개·계획 단계라 별표 D(계획·발표는 현재 점수에 넣지 않는다)에 따라 지금 점수 근거가 아니다. | 칩이 자사 데이터센터에 배치되거나 외부에 팔린 사실(출하)이 공시나 1차 발표로 확인되거나, 10조 파라미터 모델이 실제로 출시되어 제3자 독립 측정치(Artificial Analysis Index·ARC-AGI 등)가 나오면 다시 본다. | 2027-03-31 | EV-alibaba-007 | 알리바바 ④ 판단(지금 4점, 클라우드 성장·AI 제품·해외 데이터센터로 폭을 셈)에 자체 칩 출하를 수직계열화 근거로 더할지, 알리바바 ② 판단(지금 4점, 프론티어 미달로 적음)의 성능 경로를 독립 측정치로 다시 판정할지. |
| TRG-026 | Alibaba | ⑧ 비대칭 의존 | 중국 당국이 ByteDance·알리바바의 NVIDIA RTX Pro 5500 구매 허용을 검토한다는 The Information 보도를 Reuters 가 전했다. 검토 단계의 보도다. | 중국 쪽 구매 허가와 미국 쪽 수출 허가가 모두 확정되고, 알리바바가 실제로 사들였다는 사실이 확인되면 다시 본다. | 2026-12-31 | — | 알리바바 ⑧ 판단(지금 -4)의 근거인 양방향 지정학, 곧 미국의 첨단 칩 금수와 중국의 자국 모델 해외 접근 제한이 그대로인지, 칩 조달 길이 열려 의존이 덜 치우쳤는지. |
| TRG-027 | Alibaba | ④ 호황 이후 | 알리바바 클라우드가 핀란드·네덜란드·터키에 리전을 새로 열고 유럽·중동에 데이터센터를 더한다는 계획이 보도됐고, 게임 자회사 Lingxi Games 를 $2B 넘게 받고 판다는 소식통 보도가 있다. 리전은 계획, 매각은 소식통 단계다. | 새 리전이 상용 서비스를 시작하거나 해외 클라우드 매출이 공시되면, 또는 게임 사업 매각 완료가 공시되면 다시 본다. | 2027-06-30 | — | 알리바바 ④ 판단(지금 4점)이 센 사업 부문과 해외 배치(브라질·프랑스·네덜란드 데이터센터)에 새 리전이 더해지는지, 게임 사업이 빠지면서 사업 폭이 줄어드는지. 네덜란드는 판단에 이미 있으므로 중복을 가린다. |
| TRG-028 | Palantir | ⑤ 아군, ⑧ 비대칭 의존 | 영국 NHS 연합 데이터 플랫폼(팔란티어 운영)에 자기 데이터 처리를 거부하는 법적 이의 제기가 44,000건 넘게 접수됐고, 노동당 전당대회는 팔란티어 계약 취소 동의를 막았다는 보도가 있다. | 영국 정부가 계약을 축소하거나 해지하면, 또는 이의 제기가 법원 판단으로 이어지면 다시 본다. | 2027-03-31 | EV-palantir-007 | 팔란티어 ⑤ 판단(동맹 등급 +1, 적대 등급 -2 구조형으로 2점)의 적대 근거에 영국 전선을 더해 다발형 요건에 닿는지, 그리고 계약이 끊길 경우 팔란티어 ⑧ 판단(지금 -3, 정부 계약 의존)에 정부 계약 상실이 실현된 사례로 넣을지. 같은 사건을 ⑤ 에서는 적대의 성격으로, ⑧ 에서는 매출이 끊기는 의존으로 한 번씩만 센다. |
| TRG-029 | Palantir | ⑤ 아군 | 유럽 노조·인권단체의 정부 계약 철회 요구(2026-09-28), 영국 경찰 다섯 곳의 팔란티어 프로젝트 종료(2026-09-21), 미국 간호사들의 ICE 연계 항의 시위(2026-10-01)가 같은 시기에 보도됐다. 실제 종료가 보도된 것은 영국 경찰 건이고 나머지는 요구·시위다. | 두 개 이상 지역에서 정부·상업 고객의 실제 계약 해지가 동시에 확인되고, 최대 파트너인 미 정부와의 긴장도 나타나면 다발형 요건을 대 본다. | 2027-03-31 | EV-palantir-005, EV-palantir-004, EV-palantir-006 | 팔란티어 ⑤ 판단의 적대 등급이 구조형(사업 정당성을 겨냥한 적대)에 머무는지, 다발형의 두 요건(구조형 적대가 복수 전선에서 동시 진행, 최대 파트너와도 긴장)에 모두 닿는지. |
| TRG-030 | Tesla | ④ 호황 이후 | 테슬라 Optimus 가 5,000대 주문을 확보했다는 2차 매체 보도(Moomoo, 2026-09-17)가 있다. 주문은 수주이지 출하가 아니다. | Optimus 의 외부 고객 인도나 공장 배치 대수가 공시나 1차 발표로 확인되면 다시 본다. | 2027-03-31 | — | 테슬라 ④ 판단(지금 4점)이 Optimus 를 폭에 넣으면서 단 단서, 곧 'Optimus 는 아직 배치되지 않았다'(긴장 #6: 배치 전 사업을 폭에 넣은 미해결 쟁점)가 풀렸는지. |
| TRG-031 | Tesla | ③ Last Mover, ⑤ 아군 | 독일이 테슬라 FSD(감독형 자율주행)의 EU 승인 표결을 12월로 확인했다는 보도, 안전단체가 EU 에 거부를 요구했다는 보도, 크로아티아가 FSD 를 승인했다는 보도가 같은 주에 나왔다. | EU 표결 결과가 나오면 다시 본다. | 2026-12-31 | EV-tesla-004 | 테슬라 ⑤ 판단(동맹 등급 0, 적대 등급 -1 비용형으로 2점)의 규제 적대가 비용형에 머무는지(승인이 거부돼도 차량 판매는 계속된다), 그리고 테슬라 ③ 판단(지금 3점, 후발 가속도는 FSD 구독 148만·+56% 로 이미 통과)의 가속도 근거가 유럽으로 넓어지는지. |
| TRG-032 | Tesla | ⑨ 적자 깊이 | 2026-09-29 테슬라가 신용계약 체결을 8-K 로 공시했다(Item 1.01 중요 계약 체결, 1.02 기존 계약 종료, 2.03 직접 금융 채무 발생). 2분기 잉여현금흐름이 적자로 돌았다는 보도도 있다. | 3분기 10-Q 에서 최근 1년 잉여현금흐름의 부호와 새 신용 한도의 인출 여부가 확인되면 다시 본다. | 2026-11-15 | EV-tesla-003, EV-tesla-001 | 테슬라 ⑨ 판단(지금 -1, 게이트 1·2 통과에 추세 악화)이 게이트 2(최근 1년 잉여현금흐름이 마이너스인가)를 계속 통과하는지. 마이너스로 돌아 게이트 3(완충으로 버티는 기간)으로 내려가면, 새 한도 가운데 확정 미인출분을 완충(현금 + 확정 미인출 여신)에 넣어 런웨이를 계산한다. |
| TRG-033 | SpaceX + xAI | ⑦ 순환금융, ⑧ 비대칭 의존 | Anthropic 이 SpaceX 에 낼 컴퓨트 계약 총액이 최대 $84.5B 로 보도됐고(Anthropic 상장 신고서 인용), Google 이 xAI 데이터센터 컴퓨트에 매달 $920M 을 낸다는 보도가 있다. | 다음 10-Q 에서 두 고객의 매출 비중이나 고객 집중 공시가 확인되면 다시 본다. | 2026-11-16 | EV-spacex-xai-008, EV-spacex-xai-001 | 스페이스X ⑦ 판단(지금 0점, 조달 의존 고객 비중 작음·내 돈 환류 없음)의 조달 의존 고객 비중. 투자 유치로 대금을 내는 적자 고객 Anthropic 의 비중이 크면 '큼' 쪽으로 본다. Google 은 자기 영업이익으로 내는 고객이라 이 축에 들지 않는다. 함께 스페이스X ⑧ 판단(지금 -3)에 고객 집중 항목을 더할지 본다. |
| TRG-034 | SpaceX + xAI | ② 게임체인저, ④ 호황 이후 | Starship 이 처음 궤도에 올랐고, 우주 데이터센터 위성 100만 기를 겨냥한 $100B 규모 발사장 투자 계획과 Google 의 궤도 AI 시험 발사 예약이 보도됐다. 궤도 비행은 실측이고 우주 데이터센터는 계획이다. | 궤도 데이터센터가 실제로 컴퓨트를 제공하고 매출이 생기면 다시 본다. | 2027-09-30 | EV-spacex-xai-007 | 스페이스X ② 판단(지금 4점, 성능·적응 두 경로)이 '궤도 데이터센터가 실현되기 전까지 로켓은 ② 가 아니라 ④ 에서만 센다' 고 단 조건이 풀렸는지. |
| TRG-035 | SpaceX + xAI | ① 네트워크 | SpaceXAI 가 Grok·X 사용자 대상 4단계 요금제를 검토한다는 Bloomberg 보도가 있다. 검토 단계라 지금 근거가 아니다. | 요금제가 시행되고, 인상 뒤 가입자 수나 이탈 수치가 나오면 다시 본다. | 2027-03-31 | — | 스페이스X ① 판단(지금 3점, Starlink 는 가격 결정력이 있으나 사용자 간 연결이 약하고 X 는 이탈·수익화가 약함)에서 X·Grok 소비자 채널이 가격을 올려도 사용자가 남는지(① 의 판별 질문). |
| TRG-036 | Anthropic | ⑥ 가격, ⑧ 비대칭 의존, ⑨ 적자 깊이 | Anthropic 이 상장 신청서(S-1)를 비공개로 제출했고, 그 내용(손익·약정·파트너 의존)이 2026-09-29~30 여러 매체에 유출 보도됐다. 공개 제출본은 아직 없고, 11월 상장 가능성 보도가 있다. | S-1 이 EDGAR(미 증권거래위원회 공시 시스템)에 공개 제출되거나 상장이 확정되면 다시 본다. ⑥(현재 가격의 정도)은 비상장 계산(밸류÷최근 1년 보정 매출)에서 상장사 계산(PER·EV/매출·매출 성장과 입력 신뢰도)으로 옮길지 정한다. ⑨(적자 깊이)는 지금 판정 보류인 게이트 1(본업이 버는가 — 최근 1년 영업이익)과 미공시로 처리한 게이트 2(최근 1년 잉여현금흐름)를 공개 손익·현금흐름으로 판정한다. ⑧(비대칭 의존)의 약정÷매출과 ⑨ 게이트 4(약정 커버리지 — 앞으로 내기로 한 약정을 버는 돈이 덮는가)는 약정 규모를 원문과 대조한다. | 2026-11-30 | EV-anthropic-004, EV-anthropic-003 | 공개 S-1 의 매출·영업손익·잉여현금흐름·해지 불가 약정 규모와 상장 여부 |
| TRG-037 | Anthropic | ⑤ 아군 | 미 항소법원이 국방부의 Anthropic 거래 배제를 유지했다(2026-09-25). 이후 CEO 와 대통령의 비공개 만찬이 보도됐다. Anthropic ⑤ 판단의 적대 등급은 선별 당시 0(최소)이었고, 이번 실행에서 사람이 반영한 제안 PRP-001 로 -1(비용형)이 됐다. | 배제 해제(비용형 근거가 약해진다) 또는 배제가 연방 조달 전반으로 넓어진 것(구조형 검토)이 확인되면 ⑤(아군과 적대)의 적대 등급을 다시 판정한다. 배제가 정부 시장 일부에 머물면 비용형(사업 구조는 건드리지 않는 적대), 사업의 정당성을 겨냥하면 구조형이다. 국방부 계약은 동맹 등급에서 4사 공통이라 변별력 없음으로 처리돼 있어 함께 확인한다. | 2026-12-31 | EV-anthropic-002 | 국방부 배제의 범위·지속 여부와 그 성격(비용형인지 구조형인지) |
| TRG-038 | Anthropic | ⑤ 아군 | FTC(미 연방거래위원회)가 Anthropic·OpenAI 등을 상대로 소비자 위해 조사를 열었다는 보도가 2026-09-30 쏟아졌다. | FTC 가 민사조사명령·제소·동의명령 같은 처분 단계로 나아가면 그 성격으로 Anthropic ⑤(아군과 적대)의 적대 등급을 다시 본다. 벌금·개별 제재에 그치면 비용형(사업 구조는 건드리지 않는 적대), 판매 제한처럼 사업 구조를 건드리면 구조형이다. | 2027-03-31 | EV-anthropic-006 | FTC 조사의 처분 단계와 사업 구조 제한 여부 |
| TRG-039 | OpenAI | ⑥ 가격, ⑨ 적자 깊이 | Bloomberg 가 OpenAI 의 기업가치 $1.4T 기준 $30B 조달 추진을 보도했다(협상 단계). 같은 날 FT 는 Altman 이 안전 문제가 풀릴 때까지 상장을 미룬다고 보도했다. ARR(연간 반복 매출)이 $70B 에 가깝다는 Axios 보도도 있다. | 조달 라운드가 확정 밸류로 마감되면 ⑥(현재 가격의 정도)의 분자(지금 post-money $852B)와 분모(최근 1년 보정 매출)를 함께 다시 계산하고, ⑨(적자 깊이)의 완충(현금과 확정 미인출 여신)에 새 조달 현금이 들어오는지 다시 본다. | 2026-12-31 | EV-openai-002 | 확정 post-money 밸류와 실제로 거둔 매출 |
| TRG-040 | OpenAI | ② 게임체인저 | OpenAI 가 GPT-6.1 Sol 을 출시했고, 상위 모델 GPT-6.1 Astra 는 안전 문제로 출시를 접었다(학습 중단 보도 포함). OpenAI ② 판단은 성능 도약·패러다임 적응 두 경로 통과로 4점이다. | Artificial Analysis·ARC Prize 같은 독립 측정에 Sol 결과가 같은 하네스로 실리거나 Astra 가 출시되면 ②(게임체인저)의 경로 판정 — 성능 도약(세대 격차 수준인지 포함)과 패러다임 적응(출시 속도) — 을 다시 본다. | 2026-11-30 | EV-openai-003, EV-openai-001 | Sol 의 독립 측정 결과(같은 하네스)와 Astra 출시 여부 |

- 트리거는 미래 점수를 저장하지 않는다(C-14). 조건이 성립하면 현재 규칙으로 다시 계산한다.

## 출처

| ID | 제목 | 발행 | URL | 접근일 | 이해상충 |
| --- | --- | --- | --- | --- | --- |
| SRC-v15-html | AI기업_채점표_v1.5.html (D·VAL·EARN·FIN·BORR·TRIG) | 내부 기준선 | (URL 없음 — 만들지 않음) | 2026-09-11 | 작성자 Claude=Anthropic (긴장 #4·#11) |
| SRC-v15-md | AI기업_채점표_v1.5.md (순위표·원자료) | 내부 기준선 | (URL 없음 — 만들지 않음) | 2026-09-11 | 작성자 Claude=Anthropic (긴장 #4·#11) |
| SRC-v15-rule | AI기업_채점규칙_v1.5.md (③ 사다리·별표 G·별표 I·⑨ 적용표·⑥ 비상장) | 내부 규칙 | (URL 없음 — 만들지 않음) | 2026-09-11 | 작성자 Claude=Anthropic — 채점규칙 384행 이해상충 고지(ARC-AGI 하네스 규칙이 결과적으로 Anthropic ②5 를 지켰다, 운영이력 긴장 #4·#11, 제3자 재검토 예정) |
| SRC-v15-handover | AI기업_채점표_HANDOVER.md (자동화 핸드오버 — 원자료 출처표·기계화 재고·작성자 이해상충) | 내부 기준선 | (URL 없음 — 만들지 않음) | 2026-09-14 | 작성자 Claude=Anthropic — HANDOVER 75행 `3-7. 작성자 이해상충. Claude=Anthropic` (긴장 #4·#11) |
| SRC-SEC-SPCX-10Q-2026Q2 | SpaceX/xAI Form 10-Q (2026-06-30) — Note 3 Revenue · Note 16 Commitments | SEC EDGAR | https://www.sec.gov/Archives/edgar/data/1181412/000162828026052535/spcx-20260630.htm | 2026-09-11 | — |
| SRC-SEC-SPCX-S1A-2026 | SpaceX/xAI Form S-1/A (2026-06-03) — Note 11 Leases (F-36) | SEC EDGAR | https://www.sec.gov/Archives/edgar/data/1181412/000162828026040364/ | 2026-09-11 | — |
| SRC-SEC-AMZN-10Q-2026Q2 | Amazon Form 10-Q (2026-06-30) — Note 1 Accounting Policies · Commitments 표 | SEC EDGAR | https://www.sec.gov/Archives/edgar/data/1018724/000101872426000026/amzn-20260630.htm | 2026-09-11 | — |
| SRC-SEC-BABA-20F-FY2026 | Alibaba Form 20-F (FY2026, 2026-03-31) — Note 2(g) · Note 27 · Exchange Rate Information | SEC EDGAR | https://www.sec.gov/Archives/edgar/data/1577552/000119312526231755/baba-20260331.htm | 2026-09-11 | — |
| SRC-SEC-BABA-FACTS | SEC XBRL companyfacts CIK0001577552 (Alibaba) — us-gaap Revenues · OperatingIncomeLoss | SEC EDGAR | https://data.sec.gov/api/xbrl/companyfacts/CIK0001577552.json | 2026-09-11 | — |
| SRC-SEC-FACTS-F6 | SEC XBRL companyfacts 12개사 (F6 TTM 입력 재구성) | SEC EDGAR | https://data.sec.gov/api/xbrl/companyfacts/ | 2026-09-10 | — |
| SRC-SEC-TSM-20F-FY2025 | TSMC Form 20-F (FY2025, 2025-12-31) — 연결손익계산서 F-6 · 환율 Note 3 (F-13) | SEC EDGAR | https://www.sec.gov/Archives/edgar/data/1046179/000162828026025362/tsm-20251231.htm | 2026-09-11 | — |
| SRC-ANTHROPIC-SERIESH-2026 | Anthropic 보도자료 `Anthropic raises $65B in Series H funding at $965B post-money valuation` (2026-05-28) | Anthropic (회사 뉴스룸) | (URL 없음 — 만들지 않음) | 2026-09-10 | **회사 자체 발표다** — 이해당사자 1차 발표치이고 감사받지 않는다. 채점규칙 382행 `벤더 발표 벤치마크는 1차 근거가 아니다` 와 같은 성격이라 수치는 방증·부재 확인 범위로만 쓴다. 더해 이 실행의 작성자(Claude)가 Anthropic 모델이다(채점규칙 384행 · 긴장 #4·#11). |
| SRC-OPENAI-FUNDING-2026 | OpenAI 보도자료 `OpenAI raises $122 billion to accelerate the next phase of AI` (2026-03-31) | OpenAI (회사 뉴스룸) | (URL 없음 — 만들지 않음) | 2026-09-10 | **회사 자체 발표다** — 이해당사자 1차 발표치이고 감사받지 않는다. 채점규칙 382행과 같은 성격이라 수치는 방증·부재 확인 범위로만 쓴다. 이 실행의 작성자(Claude)는 Anthropic 모델이고 OpenAI 는 그 경쟁사다 — 하향·상향 어느 쪽으로도 이해상충이 있다. |
| SRC-YF-2026-09-30 | Yahoo Finance 일봉 종가·시총(2026-09-30 기준) | Yahoo Finance via yfinance | https://finance.yahoo.com/quote/GOOGL | 2026-10-01T06:20:56Z | — |
| SRC-EDGAR-000032019326000018 | 8-K 2026-07-30 · Items 2.02, 9.01 | SEC EDGAR | https://www.sec.gov/Archives/edgar/data/320193/000032019326000018/aapl-20260730.htm | 2026-10-01T06:20:41Z | — |
| SRC-EDGAR-000032019326000020 | 10-Q 2026-07-31 | SEC EDGAR | https://www.sec.gov/Archives/edgar/data/320193/000032019326000020/aapl-20260627.htm | 2026-10-01T06:20:41Z | — |
| SRC-EDGAR-000101872426000026 | 10-Q 2026-07-31 | SEC EDGAR | https://www.sec.gov/Archives/edgar/data/1018724/000101872426000026/amzn-20260630.htm | 2026-10-01T06:20:35Z | 선별·판정자 Claude 는 Anthropic 모델이고 이 기업은 Anthropic 투자자다 (긴장 #4·#11) |
| SRC-EDGAR-000104581026000069 | 8-K 2026-08-17 · Items 1.01, 2.03, 7.01 | SEC EDGAR | https://www.sec.gov/Archives/edgar/data/1045810/000104581026000069/nvda-20260817.htm | 2026-10-01T06:20:42Z | 선별·판정자 Claude 는 Anthropic 모델이고 이 기업은 Anthropic 투자자(2025-11 발표)다 (긴장 #4·#11) |
| SRC-EDGAR-000104581026000073 | 8-K 2026-08-26 · Items 2.02, 9.01 | SEC EDGAR | https://www.sec.gov/Archives/edgar/data/1045810/000104581026000073/nvda-20260826.htm | 2026-10-01T06:20:42Z | 선별·판정자 Claude 는 Anthropic 모델이고 이 기업은 Anthropic 투자자(2025-11 발표)다 (긴장 #4·#11) |
| SRC-EDGAR-000104581026000075 | 10-Q 2026-08-26 | SEC EDGAR | https://www.sec.gov/Archives/edgar/data/1045810/000104581026000075/nvda-20260726.htm | 2026-10-01T06:20:42Z | 선별·판정자 Claude 는 Anthropic 모델이고 이 기업은 Anthropic 투자자(2025-11 발표)다 (긴장 #4·#11) |
| SRC-EDGAR-000104617926000541 | 6-K 2026-08-14 | SEC EDGAR | https://www.sec.gov/Archives/edgar/data/1046179/000104617926000541/tsm-fsx20260814x6k.htm | 2026-10-01T06:20:39Z | — |
| SRC-EDGAR-000110465926072140 | 8-K 2026-06-10 · Items 1.01, 2.03, 9.01 | SEC EDGAR | https://www.sec.gov/Archives/edgar/data/1018724/000110465926072140/tm2613616d4_8k.htm | 2026-10-01T06:20:35Z | 선별·판정자 Claude 는 Anthropic 모델이고 이 기업은 Anthropic 투자자다 (긴장 #4·#11) |
| SRC-EDGAR-000119312526257724 | 8-K 2026-06-04 · Items 1.01, 7.01, 8.01, 9.01 | SEC EDGAR | https://www.sec.gov/Archives/edgar/data/1652044/000119312526257724/d83560d8k.htm | 2026-10-01T06:20:34Z | 선별·판정자 Claude 는 Anthropic 모델이고 이 기업은 Anthropic 투자자다 (긴장 #4·#11) |
| SRC-EDGAR-000119312526323660 | 10-K 2026-07-29 | SEC EDGAR | https://www.sec.gov/Archives/edgar/data/789019/000119312526323660/msft-20260630.htm | 2026-10-01T06:20:38Z | 선별·판정자 Claude 는 Anthropic 모델이고 이 기업은 Anthropic 투자자다 (긴장 #4·#11) |
| SRC-EDGAR-000119312526387905 | 8-K 2026-09-10 · Items 2.02, 8.01, 9.01 | SEC EDGAR | https://www.sec.gov/Archives/edgar/data/1341439/000119312526387905/orcl-20260910.htm | 2026-10-01T06:20:47Z | — |
| SRC-EDGAR-000119312526389274 | 10-Q 2026-09-11 | SEC EDGAR | https://www.sec.gov/Archives/edgar/data/1341439/000119312526389274/orcl-20260831.htm | 2026-10-01T06:20:47Z | — |
| SRC-EDGAR-000132165526000041 | 10-Q 2026-08-04 | SEC EDGAR | https://www.sec.gov/Archives/edgar/data/1321655/000132165526000041/pltr-20260630.htm | 2026-10-01T06:20:43Z | — |
| SRC-EDGAR-000162828026049270 | 10-Q 2026-07-23 | SEC EDGAR | https://www.sec.gov/Archives/edgar/data/1318605/000162828026049270/tsla-20260630.htm | 2026-10-01T06:20:45Z | — |
| SRC-EDGAR-000162828026050705 | 10-Q 2026-07-30 | SEC EDGAR | https://www.sec.gov/Archives/edgar/data/1326801/000162828026050705/meta-20260630.htm | 2026-10-01T06:20:37Z | — |
| SRC-EDGAR-000162828026052535 | 10-Q 2026-08-04 | SEC EDGAR | https://www.sec.gov/Archives/edgar/data/1181412/000162828026052535/spcx-20260630.htm | 2026-10-01T06:20:44Z | 선별·판정자 Claude 는 Anthropic 모델이고 이 기업은 Anthropic 경쟁사(xAI)이자 컴퓨트 공급자다 (긴장 #4·#11) |
| SRC-EDGAR-000162828026063820 | 8-K 2026-09-29 · Items 1.01, 1.02, 2.03, 9.01 | SEC EDGAR | https://www.sec.gov/Archives/edgar/data/1318605/000162828026063820/tsla-20260929.htm | 2026-10-01T06:20:45Z | — |
| SRC-EDGAR-000165204426000071 | 10-Q 2026-07-23 | SEC EDGAR | https://www.sec.gov/Archives/edgar/data/1652044/000165204426000071/goog-20260630.htm | 2026-10-01T06:20:34Z | 선별·판정자 Claude 는 Anthropic 모델이고 이 기업은 Anthropic 투자자다 (긴장 #4·#11) |
| SRC-NEWS-alibaba-20260720-d804d40a | Alibaba Fined €550 Million for Illegal Sales in Biggest DSA Case - Bloomberg.com | Bloomberg.com | https://news.google.com/rss/articles/CBMitAFBVV95cUxNNEx5ZU9YUEhCT3BfTVVfWERISExVMHRGZ0NjaFUtNHZZMmozVDRvYlRxTlZ0UWl2SWJlNHl0YXA5TEpWVmYzSzVobm9ZVEtjNDFlSlJBdUJGOWZGN3pWZkxHWV9sWThHVl9pUGVWRUNSSl9DUWVJamRvbzRmOUVISW9zQlp4dWstbnRGMkRUMmhlTlR5ZVBCNzRENkZpakVxZ2VTQVhHTXBmbjB6XzVyS3VtRDg?oc=5 | 2026-10-01T06:20:20Z | — |
| SRC-NEWS-alibaba-20260803-9f5dc24b | Alibaba unveils its largest AI model yet, DeepSeek's latest model is ultra-low cost - Reuters | Reuters | https://news.google.com/rss/articles/CBMi0wFBVV95cUxObUlCNHp6dVFoTEtqbkF3aFZqaVNUUVRJd0dicUhkb2tidzdkUWg0OVp1SU94aFJ1dmdkbDZIZGxMQVNWMm5vYXNKR0JicHNwZWRVX25ZY0hHaTNVUVdIWGdBNERsS3hDT29CdzlydEFGbFJzblgyempKcjljLVFELTVPRjdHVnRrOVRmQUs5QWVFQlg3aWVET1lNcDE4R2wwSC1vazRDaTNTZFhURm9qUGFfWGE5Sk1pMHNBUWx3TG85S1lZSWV4TUJxRU11UVhMR2Iw?oc=5 | 2026-10-01T06:20:20Z | — |
| SRC-NEWS-alibaba-20260820-c9f8d2a2 | Alibaba profit falls 75% after ramping up AI infrastructure spending - Reuters | Reuters | https://news.google.com/rss/articles/CBMipAFBVV95cUxON2tiUnl3QjZwYUtIMS10blVfb0hldWgzc21OVk40S3lIV0g1LTdiakVxYkt5Wk9BTUdOQ3FwTEpVV1JwRi05aGRVR1B0c1Bya29xMGpxdEZiR255eEdDdUZURlJtbXJ6QUpiQktIT0hGSEF4ZkV3Ry0zNlV2aXhUYzFZVVJWMllsQ3FFZ1FiMGk0bUNlTHhHcnBNMlMyUmJTYTdSTg?oc=5 | 2026-10-01T06:20:20Z | — |
| SRC-NEWS-alibaba-20260824-88c3d5a1 | Alibaba shares slide after $10.2 billion AI share sale offered at sharp discount - Reuters | Reuters | https://news.google.com/rss/articles/CBMizgFBVV95cUxPbmJDLXh4Z1Q1TU1xaFVKallDYkY5TmdpYUlUTkpxZ1BGS09ReGNfSlJTd0F4OGNKYndTUndKRmRVaU9DUUNfWVc0b1FyV211dFQwRTdHZS1CNExRd3owLU93WEUtcWZ6YkQyOThYMmZlNDFJM01RbjhOenhvaFptLW44S2tmR2pPSjJOWlhnUHNhUy02Wm1Td0gyY3F1QzhyQk42YWhnNl9UUXBxY0Z3bzhUSm1tRjhTZ3YyM3dVU21ibERiRzMtQ3B6eTlfZw?oc=5 | 2026-10-01T06:20:20Z | — |
| SRC-NEWS-alibaba-20260909-4bf2ae89 | US Says Alibaba, DeepSeek Have ‘Systematically’ Siphoned AI Models - Bloomberg.com | Bloomberg.com | https://news.google.com/rss/articles/CBMitAFBVV95cUxNZk92eWg4ODl3QnlnbmROdWEwaTllZm5TTFlPZXRKSnFjUUxjcnAwUGxDd2poTDh0V2N1S2xaLTI4Y3h0V09YOXd5MmszMkdUWUE4V2pOcEp3SjJuVUUxZjhNeXBNbW14dl9fRGRIWTJfZkN2bFNGc0V2Zk40SEtiZzFvaFdETm5jN3d2eE1tVHgxbDktV3Bfa3FfQnpGV2tsYTRNSFFKWjFGaTNQaVZ1VGE5MWc?oc=5 | 2026-10-01T06:20:20Z | — |
| SRC-NEWS-alibaba-20260919-f21df9b5 | China investigates Meituan and Alibaba units for suspected antitrust violations - Reuters | Reuters | https://news.google.com/rss/articles/CBMiywFBVV95cUxPNkxJNDZrd2NpQk80eEgyRWpwSEo3YWYxNUVHWHlaR1dGOWlFSmZHVF9xQjliN2RINXEzMHRsUGxjUEhLRlpsejF6dHF3b0dwZ09KcGlTMVMzdDVkbG5fdkdHNVdmSVFYdlVDMmJZcjB6ZzdITmh5YmhpSmgtamdGM245ZmxOTnJMUnJPTjM4UUZTR1BDeTNHQ0EwT0dfb1h6WVVaaVdpSUdhUkRicGVUaWRMTC1CaVBmXzN2YnFwUDMyWEFGNWxBZmJIUQ?oc=5 | 2026-10-01T06:20:20Z | — |
| SRC-NEWS-alibaba-20260921-1cbebf5f | Alibaba deepens AI push with new chip, bigger model; shares jump 5% - Reuters | Reuters | https://news.google.com/rss/articles/CBMi1gFBVV95cUxPUlcybzdOMWxNcmJHT1ZvUHFRTkczZzRNbHpkeUM1QjVxak5WMVdfTldrMWRtaTdHd1FvZkUwbGN4NmhwdUFSdmJxdVBVTGZxNFBWMUNqQXU3dlJzM1VXOHZsYmliZmxBRl90eFF6dEFZWl9BQTJTdkdxaDBSMGVrSXBJUkFVQkx1RTFOcktHZDQ4blo4VFh0amtSRmYxU2YxeGdQdUhFa25DeDBjSllsaVBsUVQ3X3VYdnRKMTAxN1BzZFQzUUpGSVI3TXZBZmRuTlhjejFB?oc=5 | 2026-10-01T06:20:20Z | — |
| SRC-NEWS-alibaba-20260929-6a9d7cb6 | Alibaba Group Holding Limited (BABA) Investors: Securities Fraud Class Action Filed, Contact Hagens Berman Before October 5, 2026 Lead Plaintiff Deadline - PR Newswire | PR Newswire | https://news.google.com/rss/articles/CBMirAJBVV95cUxONWNFX2hzOWx4ZC0xVTNEaVdQeWN0eFVOT0ZBcEFOSVN6OGZ4ZXVBbTlrN2ZMNmZFR003c1JlOVlac2FmeUlya2NxMXVUSzVJWFp0d3JmLUVhQWtJR2VDZVJYaVdyMk45TTVZb0NBc1BqMzltOUZqaG5sbjZvNnJBTWUwTW9VTlBXOHBvZDc3ZUlCblU4eXNENUpyNFVOMnpadE5lZWg5akE5di1wTlZfa2tOdnM1SmtjQjZkOVZKTWxGOWw3cEJBdDZ1Vm5oak14UDVCdE5GdFNGTnRLT29KdGpZaFJaTW5HT2pxY1FWS21FZWItb3VzRlBqRzJ0QzFzMWpNLTV1VFZrall3R0FMdlVCQlBTeERfZUlKdnI2UnpWeDVPNmtyMDI3X0c?oc=5 | 2026-10-01T06:20:20Z | — |
| SRC-NEWS-alphabet-20260713-bd6ca383 | Alphabet Inc (GOOGL) Stock: Looking Beyond the $4.7 Billion EU Fine - Yahoo Finance | Yahoo Finance | https://news.google.com/rss/articles/CBMingFBVV95cUxPbENHRFY1b0xxTEprUDBVX3dWcWY3a3Y5eDBuZ2luWUM2aHRRcHRFbmNKTEs0akhUNDl3YTVmWXhYMjhZQmNPSmRWaWgyQkEtbGpGN0JXOW52MWhVMUxOeHFWUzFyWktzOHo4Ty1pR3Y3d0lDR0Fvc1F2REk3YXlkQjFMQmpuOTJaM0RVcGEyTThYY19PMWNsSVBaZS1hdw?oc=5 | 2026-10-01T06:20:04Z | 선별·판정자 Claude 는 Anthropic 모델이고 이 기업은 Anthropic 투자자다 (긴장 #4·#11) |
| SRC-NEWS-alphabet-20260920-133c72ed | Alphabet (GOOGL) Could Be 28% Undervalued Following Its Antitrust Win - simplywall.st | simplywall.st | https://news.google.com/rss/articles/CBMiwwFBVV95cUxQcVV4ZjNsa1Y1OURzc1k5S2MtWmlBUnhQMDlRUnJ4MERxMjVOR19yLVZybDRpSldLWTNxVWliUEtOaFNSLW1PU1lwOWk1LWNaaHYyamNIYzh5eF9za0tPWGFVNklPSTVySnk0OVUxN2lkZDZzVW9xWmlUNGdKdnN1c25aM1g4T3BQb19OTlBPY2xpWUNma1FCYnZyaUJ2NTBuMlh1SGM4WFZmS0FtWnlfZG9zMV9HdkJvMzZXam9IeW8tR3PSAcgBQVVfeXFMTTZrMGRBNzVpMHRSZmZIQ2pkcDBkZTU3N29qN2FXTE5HVG5VQmxTZjJGcEJPSEMxMkpNaGVWU29HaUsyamFiR05iRWFDR0JVU2dFakNZazZiX3ctV2JlOFRRd0EyQXRsejh2OEVabHktMzFhdkI3b1B6WVZEOGRjN1ZsQ1ROTENIbVlmR19KOVpkRS1samEwLVRKRTNzaWpsTHRjZXJmTUxmMFJrQ19BVnlET1ZHWkxISjBGWm1LcWFEOUdFb1E3LTA?oc=5 | 2026-10-01T06:20:04Z | 선별·판정자 Claude 는 Anthropic 모델이고 이 기업은 Anthropic 투자자다 (긴장 #4·#11) |
| SRC-NEWS-alphabet-20260930-2b5aeb8c | Anthropic IPO Filing Reveals a Major Vulnerability: Nearly 50% of Sales Flow Through Amazon and Google as - Benzinga | Benzinga | https://news.google.com/rss/articles/CBMiswJBVV95cUxOVFRiMVYwR3RjTVgwbXM3RmhVYmk1b2NlamJRTDF5OGFGMjh1bXVVTFNRMHhhSXBNbjdyMmdnUlhkMFBrSDl2THpVeXVFWEZZNWg3dVBCTEV6MC1fWUxlTkdkOUNRbHZ1WkYweEwzUk1XZ2RxVEpTeGpEZzYzVFoteHNYaTBZU2d3andTRGVocGEwM0ZQTGo5d2dKTm1qdWZkbE0wWWpQVkdqVkx5VFh1VEJfMVpWUVZ5QUFsSS1rWHhwdXY1bGRLZkZBbGVHZHNfeFZZRkVQaGJXU0s2VWRNMXp6UEJUcmRDR2x3Z0xBbDYtd0xNdEoyMDdfX2RWNXdxRTJYTVJwZGVYM1RRU0Z5ZV85SGJEanZuUGJGTW5FVU1WNW54RGNSQld1NTVPa0hqMXBJ?oc=5 | 2026-10-01T06:20:04Z | 선별·판정자 Claude 는 Anthropic 모델이고 이 기업은 Anthropic 투자자다 (긴장 #4·#11) |
| SRC-NEWS-alphabet-20260930-623b47a2 | Google challenges European requirements on sharing search data - marketscreener.com | marketscreener.com | https://news.google.com/rss/articles/CBMi2gFBVV95cUxQVEltd1VsZ2JDZmJVcS1LeWpMU0l0b1ZOelNQNDk5eDRBdVl1ZmJoTGNuNVlaeE1VVVVhRzBfQ1Zja1YwR0FlYzh2NThBaXdEOG9Ud2xnRXZTNExRbF9KT29zdDFNaDVTbzF1bGwwcTNUaWRhODRwV29FZGwydVlDOUVMOW1pVkFZaEw2Q2xRaWJ5eG1XSHNNR0xQcXdpT0VSSDI2aU9TVWJCN3I5QUh2UnVCeS1aenhvaHlHRG9GZm1BaW1JMW9DelhWNWkzdnhrb0x3cGtERTQtQQ?oc=5 | 2026-10-01T06:20:04Z | 선별·판정자 Claude 는 Anthropic 모델이고 이 기업은 Anthropic 투자자다 (긴장 #4·#11) |
| SRC-NEWS-alphabet-20260930-e34286f1 | Google announces Gemini 4 flagship AI model after months of delays - Reuters | Reuters | https://news.google.com/rss/articles/CBMitwFBVV95cUxPa0kxM3JDazhISnQtVGJ1Q2phRmxPR2Mtb2R4X1dQX0U3TkVZLWV0YUZNSnRfQ25OQnRuWHpNczNHSzhCZFFkdHFCWEVXYUhuazBDLWJ0eV92WU9nMDR6Nnl5ZDRCOG5UdWtwNnpTNkVtS2NLejVrX1Y3eXFvbDRMc0Y2Q2hvN0Q5YTEzTVA3NDFLaHprbnpuNWVBejNPVUlKemJCSHZUcHZSVE9iNmt3TWxXMXFBWkU?oc=5 | 2026-10-01T06:20:04Z | 선별·판정자 Claude 는 Anthropic 모델이고 이 기업은 Anthropic 투자자다 (긴장 #4·#11) |
| SRC-NEWS-amazon-20260928-d1a27463 | Apple, Amazon face revived UK consumer lawsuit over product sales - Reuters | Reuters | https://news.google.com/rss/articles/CBMiuAFBVV95cUxPSlNVR0NibnVhb1I5T3pCODVCVDUwTUJyeHFKdE9UYzNXcTZMYmF1Ty1LQmZaTnRSa3JNSGU0WVFwaGJtRDE0d3NDQ1lGQ2dvd3BBX3BjalVMUHdhSEptUGFYWG1CTTl2ZmlFZXlBa2d5eVY3Y2lFUHBsWVNGS21WOFJYcmtJYmFvVy1UZ0dDNWk4SDR5dFUzVmN4U3lEeWp6amJSUlZVQlZqdXA5OGNNd3B3ZVV5eWEz?oc=5 | 2026-10-01T06:20:06Z | 선별·판정자 Claude 는 Anthropic 모델이고 이 기업은 Anthropic 투자자다 (긴장 #4·#11) |
| SRC-NEWS-amazon-20260929-1af966b1 | Bring near-Astra intelligence to everyday work with GPT-6.1 Sol on Amazon Bedrock - Amazon Web Services (AWS) | Amazon Web Services (AWS) | https://news.google.com/rss/articles/CBMixwFBVV95cUxOUWc5Z2JxcEpSSkZRZ3YyZVJ6R3ZNdjZya0hod1hHLXJyX2Fodk1iR08ta1phMFFlUmw4aU13ZGt4aFAyaFdpeWlobUYweF90c3YwcTZMYUt5T1o5dmR1NW9Xc1RGNjZEMWJ4MXVvakxjdGhzSEFDbFVld2tiSEhxd25vQ2NGQ3NLNE43MnA4Y1hYV01oUTh2enM2U0lXMjh6OTBmNFBzSGgxV0tvZmxralJBQTR5VGxlTl9udl9FSm1DOGhodFJF?oc=5 | 2026-10-01T06:20:06Z | 발행사(또는 거래 상대) 자체 발표 — 이해당사자 · 선별·판정자 Claude 는 Anthropic 모델이고 이 기업은 Anthropic 투자자다 (긴장 #4·#11) |
| SRC-NEWS-amazon-20260929-6dc379e1 | AI agents are fighting over your shopping cart: Meta’s Muse blocked by Amazon and Walmart - NBC News | NBC News | https://news.google.com/rss/articles/CBMiqwFBVV95cUxPZ2c5MVIxcTRLS25nNVdnNGVIcDhORmhFVDZaZHlGd0pmWjQ4MTNPcDBiLUh1RUFnbzhvMlRRTDk3UDR2Z0QtbDU0UXVFMzVaYWVnX0k4RWtzNE5DTms0RzZSd09PcXhGOTJvaHdQcFBxSEliNGY1V2Jtd01ITlRpQUQwLWdSb3RINmNBWWl1ejBaWVNXalQ3LVllMmxqZkFmTUs1R1NUb29OVGc?oc=5 | 2026-10-01T06:20:06Z | 선별·판정자 Claude 는 Anthropic 모델이고 이 기업은 Anthropic 투자자다 (긴장 #4·#11) |
| SRC-NEWS-amazon-20260930-e41898d9 | Synopsys and Amazon Announce Strategic, Multi-year IP Agreement for Custom Silicon; Collaboration Also Extends to Cloud and AI-Powered Engineering - PR Newswire | PR Newswire | https://news.google.com/rss/articles/CBMipwJBVV95cUxOUmRXYjFSSHRyRkNCZk55OC1nMVFLQ1hvMHlWRlZFMVFfMGkxNzdXQXBNM2tzbXhRZHJvUGZKWmNlblJhRzV4TnFqXzB4d0JXaVBHSngxZkFaTF8xaHc4THNKVkZYWmxwYTFneE50WjJoSG1sdVlnR3JBT2dOeHcwd1dQYlB1MFU0blp6QV9Ha1lMUXJNSWNGMERKMEVDY1p1SGtmd3hVVC1xdXp2Z2NuWTlWYWJBaUZXcS1FUGhRa0N3QjlnVXhSenh2QnlVZkIwV1ZHVnBwbzdsNlV4ek9zdVFxa2pWa1lJT2xPeXg0U1M5bFF4enJHR3BkMGRUU1RZUzNpLWhLSjFMdFp1ZWVjM0ppcXpGcU1URWJ3STZUMGswbEl6V0RN?oc=5 | 2026-10-01T06:20:06Z | 발행사(또는 거래 상대) 자체 발표 — 이해당사자 · 선별·판정자 Claude 는 Anthropic 모델이고 이 기업은 Anthropic 투자자다 (긴장 #4·#11) |
| SRC-NEWS-amazon-20261001-39aa7ec2 | Anthropic Plans to Spend $518 Billion on Cloud and Data Centers. More Than $100 Billion Is Already Promised to Amazon. - The Motley Fool | The Motley Fool | https://news.google.com/rss/articles/CBMi9gFBVV95cUxPV1VyZWNDUXhZRmxTa0FTZVgyUGRON3M4ZGFRSEltazdOMDFyd3AwRk9fR2pPYk1FM2dIN05VTjViVXdoMko5NklabHd0ZU15bkNpMmZiTjZrWXFxNllzdlNmUTRONnE0dTc0UEJNOVIxVlFsMjNvRk1DcnQtbkZPeHZWVkRNSEVCdWFJZTB2RkdxRFZWQzZhbEZiVHowRlZsLURZSUlfckpxWkVvVmUxZlhzMGNXdHhtQ25UWmhGVzNrSGt3eVRBazJOeUhEODBUWGNaMnRhYzdpb3FfWWZjRDRfMXpXcDdhWVBrdm1TYS12TnNlb3c?oc=5 | 2026-10-01T06:20:06Z | 선별·판정자 Claude 는 Anthropic 모델이고 이 기업은 Anthropic 투자자다 (긴장 #4·#11) |
| SRC-NEWS-anthropic-20260922-004720af | Introducing Claude Opus 5.5 - Anthropic | Anthropic | https://news.google.com/rss/articles/CBMiU0FVX3lxTE9xbTN1a0tOdm9kT0JxbVBHMU9XYUhpUjd0MHNFYm8yd2pRMnhjdEYzdjF3ckZEY1V0a2ZQTXlyRUhteVozMlhDbVQ3Mm1KWlRYbUVF?oc=5 | 2026-10-01T06:20:21Z | 발행사(또는 거래 상대) 자체 발표 — 이해당사자 · 선별·판정자 Claude 는 Anthropic 모델이고 이 기업은 당사자다 (긴장 #4·#11) |
| SRC-NEWS-anthropic-20260925-86310879 | US appeals court upholds Pentagon's blacklisting of Anthropic - Reuters | Reuters | https://news.google.com/rss/articles/CBMiqgFBVV95cUxPN2xsSW1uNVNkSjE2UHVQSGFlOGJTbGFRa2dtdWgyb1owYlFpS2RHZHVSQnRxSTRoSnhqWWJTMEV4Q1BfNzRJZ0h4MVY4S014TTAxbjU4aThsZW95OUhEUFg2Tlg5ZU92Y21RcXVZa1hySFBUT2FXVkZ1ZlRaV3BpNnJFY3g2Ny1KRkpyQm5pNTctbS04V182WjZpYWczRWlJM1RMWl9uU0hNQQ?oc=5 | 2026-10-01T06:20:21Z | 선별·판정자 Claude 는 Anthropic 모델이고 이 기업은 당사자다 (긴장 #4·#11) |
| SRC-NEWS-anthropic-20260929-6463f068 | Anthropic’s leaked IPO prospectus details steep losses, rapid growth, and a fear that AI could end humanity - Fortune | Fortune | https://news.google.com/rss/articles/CBMimAFBVV95cUxPT1VnSWcyaGx2WXRNaEc2NmhQVVhuVmFDaGN4MVkydU5yYTltYmMzd0RtMzFTUEdLSURWbGFjNlFSMUlEdjV3QjhaQ25oX0xJNFF0azNCck5sMThQaXdhQTg0aVYwRk1zWkEzTzM5WUI4dWlnc0hvdE11ajQ4Q1N2Y1pEYktxQTFSdC1lX01kYjVaOFNwak9yQQ?oc=5 | 2026-10-01T06:20:21Z | 선별·판정자 Claude 는 Anthropic 모델이고 이 기업은 당사자다 (긴장 #4·#11) |
| SRC-NEWS-anthropic-20260929-c5aa93f0 | Anthropic's $518 billion AI buildout hinges largely on deals that cannot be canceled, filing shows - Reuters | Reuters | https://news.google.com/rss/articles/CBMiwgFBVV95cUxNazVCbjhpLXhaZU5LbGk2TENxV0NHbXdFSS03bVpudXJnOE84Y2ItOGxEdHRHRHYwNG80SlRsZEVLNDN4eDJNaDJJRmlxbWpyNDU4Uk9scjNCQXVzelhERzZzZUZOS1c0M3JEMFpMWjFuRGU2cHhqQk1ZSDlIMFRwZmtCYXJZajFpcEM4cFRIUF9tUWljSVRzRFN4akQyLWdaNVltTDY3anJJUkRHbWctVkNRbzNQV3FBejF4UldtcXA2QQ?oc=5 | 2026-10-01T06:20:21Z | 선별·판정자 Claude 는 Anthropic 모델이고 이 기업은 당사자다 (긴장 #4·#11) |
| SRC-NEWS-anthropic-20260929-e998c685 | EXCLUSIVE: Anthropic IPO prospectus lays bare deep dependence on Big Tech partners - Reuters | Reuters | https://news.google.com/rss/articles/CBMirwFBVV95cUxPQ1Q4X3lqOUdZYllBZFVuZFBIWGt6dmdua2JoVnZ0aVVnWnd0M2lscWd0UFB6c3QxRmNJdXJ2T3ppbXR5TW8wZ2lzQU5obDR2U2t0WldJUWx4MEo2V29HVldhSEtVUWVPdkdIQ1dVSUtkcG5hTE5UWDVKek9hTjhkNGU4eGNKcmRPY1JjWmRaTXJVblBoWldzNU1PalhocDRfRHdPRnhxVEV5ckRsenJZ?oc=5 | 2026-10-01T06:20:21Z | 선별·판정자 Claude 는 Anthropic 모델이고 이 기업은 당사자다 (긴장 #4·#11) |
| SRC-NEWS-anthropic-20260930-4777943a | Anthropic’s $11.6 Billion Quarter Just Changed How the Market Should Read the S-1 - Yahoo Finance | Yahoo Finance | https://news.google.com/rss/articles/CBMimgFBVV95cUxPWDNQVUtxQlR0MTFnZFJiQlZGOXNrTXRZczBvSkZ3Nmh5ZHpEdHo2TzBGZ2hocUQ5Zko1TVYwX3RjMWxHN0hQbDBQSENDMTdhb3V0YWJGVkpfS0NMamFJako3UmdjMkpwelI0RG1CcURMV1FpQkN0ZjdXSW1lbzJCWklKZVI5dDJFQV9yX01JZU5VaWhfMFlLTk1R?oc=5 | 2026-10-01T06:20:21Z | 선별·판정자 Claude 는 Anthropic 모델이고 이 기업은 당사자다 (긴장 #4·#11) |
| SRC-NEWS-anthropic-20260930-61631552 | Google unveils Gemini 4 Argon, retaking benchmark lead over OpenAI and Anthropic — but in limited release - VentureBeat | VentureBeat | https://news.google.com/rss/articles/CBMi0wFBVV95cUxQbV9aRXc0YUkwWEFxRXAtLUpoTDJ6WGRpUWpzRGwtWG82TUU1RGJ6Si1lUzlxYUE5a1UxNEZmUG5kT09kcnd6TUhoeTJWUnZ1UkF2eGZIcHg2d2FvZ19GVXhvbUQ3WlREX05yNmdsdlI4RWg3ZGlNTzhzVmhmbV9NMWJvSk4wMlFZNjNxaFRSVlFQSWhocU1GQjU4TDJVVmdNdjVBdzhnUFc1RWc1YVN4NU41NUZhMnJQeFFtX0NtQU9BekxuVkxKVHNTTkwyald6a0Rv?oc=5 | 2026-10-01T06:20:21Z | 선별·판정자 Claude 는 Anthropic 모델이고 이 기업은 당사자다 (긴장 #4·#11) |
| SRC-NEWS-anthropic-20260930-a02b29dc | FTC Probing OpenAI and Anthropic Over Product Safety Concerns - bloomberg.com | bloomberg.com | https://news.google.com/rss/articles/CBMisgFBVV95cUxQNWthUTUtdzAtb1NKYkQ4TDdxSGV4ZC1NV2QxTnE5a2VzaldWRWowU3VDUUxWV3lIajZzRnNYLTJUV3RCaTFxUU11MEhKSFF4UmFMNTBqV1g0bmljbWE3bXJJc0tNOE5XX3hZQjRlUS1sMFlaS0FDWHZ2WmdQU05zSV9uSFpYNlF0SmVHeEVTTnVkdzdNZHZZbGJaemhGQUoxT0gxVm1kbnJ1dTlhZm8zeFJR?oc=5 | 2026-10-01T06:20:21Z | 선별·판정자 Claude 는 Anthropic 모델이고 이 기업은 당사자다 (긴장 #4·#11) |
| SRC-NEWS-apple-20260928-3c10400d | US jury says Apple owes record $5.7 billion in haptic technology patent case - Reuters | Reuters | https://news.google.com/rss/articles/CBMiwgFBVV95cUxPOXduWFl4SXl1dlNpaDVMVUdxbENVSGFqV3hFYnl2ZE8yTTRNZVAxZFpwTERQZzExTmg1ZG5IdHFtRjg5cUtGaU1pNndEa0UzMzg1YWJWc203ZnVOajF3MUM2RGhQTllJTXRub05McENSTExBQVhQUm1aYlZIN3RyR2RfN1V4cjZ1bktEVjV4bk5WdFowdVZENlhWOE0wU1Y0T25LRk8tbjBFendGaVhNdlp5aUZNWFM4YUhKdzhNNFFLUQ?oc=5 | 2026-10-01T06:20:22Z | — |
| SRC-NEWS-apple-20260930-876ff71e | Amazon (AMZN) and Apple (AAPL) Must Face a UK Class Action Over Marketplace Sales - Yahoo Finance | Yahoo Finance | https://news.google.com/rss/articles/CBMilwFBVV95cUxOMTJVWGRDWmhFa0NQaEowbXB4dFNMZzN2NE5QX2dpYWYtWTZXVFpGY2p2dlR3Q1BURTZzdm9DVVpTdWRkNjRiaU00dEJBR1dvUmJ6VGxUU05sUlozNWVOVlFDcVVnNGdWYjk5WDNTc09EbEdvZzFkd1FnelhGSVJZOGQ3WFhielhIX1hwN2Z6UUNwR0piNFFF?oc=5 | 2026-10-01T06:20:22Z | — |
| SRC-NEWS-meta-20260928-e1cfee35 | Meta launches enterprise AI business seeking to cash in on vast spending - Financial Times | Financial Times | https://news.google.com/rss/articles/CBMihAFBVV95cUxQYXl4S1J5V0N4UWpZbHpnUlFaQWlXWWdjZFd0ZVBOSzJXS2VQZndsTXgyM29XV083LVlySlk5eGNxTWRXUjBGdkZHa3djdVJ6MDlVNDFKWlFfbnlHeW8tRi1Kd25jQlNYanFTQ3NhMFN5aWFFaHRWV21DR01mSEtxSzRyaDc?oc=5 | 2026-10-01T06:20:08Z | — |
| SRC-NEWS-meta-20260930-b46bb0dd | Exclusive: Meta’s Muse Tops 3 Million Weekly Users - The Information | The Information | https://news.google.com/rss/articles/CBMikwFBVV95cUxPZUlsQkdDcHFFRnVIeXo3anBjZ2RfcW1XcEk3N1VRd3NtTkUyaUNBWmNGZU5KTGNaemxIMGlCTHZfcG1GQl93OFJQbWhKbF9JbGJpM3QxTDdOLW1MWEdwQVpSaDZscElPZDRaNm5NU3h4S0htdEduODQwVVlzbWFiQ2hyMXY1M1NUc2lUX0hUUExsYjg?oc=5 | 2026-10-01T06:20:08Z | — |
| SRC-NEWS-meta-20260930-d6f80eaf | These 3 AI Stocks Are Poised to Be Big Winners from Amazon's Choice to Block Meta's Muse - The Motley Fool | The Motley Fool | https://news.google.com/rss/articles/CBMimAFBVV95cUxNbG9QN3lOMm13amhKTmp6djZUMVVTallpWWJoRTJ0a003Tkd4OEozY19Mdzc4WVpZZTNHM1VmUzR6WkZXakhucEtPb0QxTWgyenFEb0VnZEJjSFZ5MnZhQkREUG40M0lVMFRwd3gzckxtbnRMRDB3ZzUtUi1xY19YcHl0WXB1UmQ0NkxSZUV0cnhZUTJpOWEzVg?oc=5 | 2026-10-01T06:20:08Z | — |
| SRC-NEWS-meta-20261001-5304dfbb | Meta counted Mark Zuckerberg’s $4.1B stock payout as research pay to claim a $355M tax break — and the IRS wants it back - Yahoo Finance | Yahoo Finance | https://news.google.com/rss/articles/CBMimwFBVV95cUxONnhRUFNkRjFmS1pmRG91UWkzcTJ2X2JtNV9RQm44aE4yZjJDVkYxN1AxWWZRZElwNHZWMkkxNVYxMVMyWWt6bGxJQndvZnozX0RDX3MzQWM5TzU1WDVhYlltZ1ZTdURoTkZlVHFwcmMxMXdQdmtwZG1SaF83UERkTF9uT3pjamQ1OXI2bWJlR2d1RHZNdkVhemh3Yw?oc=5 | 2026-10-01T06:20:08Z | — |
| SRC-NEWS-microsoft-20260925-74aad420 | Introducing the new Copilot with Home, Code and Autopilot - The Official Microsoft Blog | The Official Microsoft Blog | https://news.google.com/rss/articles/CBMiowFBVV95cUxQdnBldHlfWlM4TjV6Y2NWTlNMUjFzQ0ZUa2M5MTkwX2pkaHNhbXc0TDJJbUs4bmxHZ3RSXzQ3SlFXd3VuemZFaWJFekFneHRNUDBNb2ZyTmgxVWFqR1BySzZRelo1ZjdTWXhuYjlGc1dOQm9JNTJMWHNlSHY0Z2FxS3hhMnp1OGVqWFdMTGlFYXZoZV9mc29ySDhGdUlZOW1RM3Rv?oc=5 | 2026-10-01T06:20:15Z | 발행사(또는 거래 상대) 자체 발표 — 이해당사자 · 선별·판정자 Claude 는 Anthropic 모델이고 이 기업은 Anthropic 투자자다 (긴장 #4·#11) |
| SRC-NEWS-microsoft-20260929-10993ed8 | OpenAI takes on Microsoft with the launch of what feels a whole lot like ChatGPT's own office suite - TechCrunch | TechCrunch | https://news.google.com/rss/articles/CBMizgFBVV95cUxPMThVYXNHdk44dXhHc1F0NHZ5SzJYd2FBN3BWSHJ3R1pXMjMySWlfbTQwaVRxc2l3QkFGUDJLamZ2Yk1zVlBFekl6SVRlbF9kc0lpWEdjQVBHUzhETUNMQm0waVdPSmlOLTh6MlhNZ2pmbFZBR0hpQnYtQUhVX2tiTzBtbEp0YkRuQjViX0Z2eGFpTzVwMFlOd010STAyeVRKVHhlWVNnZ0xpYTcxVDlxM3dha2tjbXp3SE9QRGhfTkdNNlJLQm9sOTh4dHdpQQ?oc=5 | 2026-10-01T06:20:15Z | 선별·판정자 Claude 는 Anthropic 모델이고 이 기업은 Anthropic 투자자다 (긴장 #4·#11) |
| SRC-NEWS-nvidia-20260928-596760c7 | OpenAI sparked Hugging Face bids with early investment offer ahead of Nvidia's $13 billion deal - cnbc.com | cnbc.com | https://news.google.com/rss/articles/CBMiqwFBVV95cUxQMThSYmpsQmN6bHcxbk1TSTN3a0xPaHdqOS0wYS1hUWhOQzREbWpSVzlvalkzY0ozWkxWcVo3Z0lzQ3NiOUN1MnBMQVNiTkxjTzVadkZXSWJ5NjM2VzRaS0EzekJrWWZ0VDVRWXdDUXQ5b3Q1SzF3MGJUTUZpMDFTb1ZKbWlJaGxsQkhvU2hGcGExQjZ3VXhBNVMtM3RrazNmT0hBUnVBVVlaYm8?oc=5 | 2026-10-01T06:20:24Z | 선별·판정자 Claude 는 Anthropic 모델이고 이 기업은 Anthropic 투자자(2025-11 발표)다 (긴장 #4·#11) |
| SRC-NEWS-nvidia-20260929-2b8fde1e | Nvidia turns to insurers to spread the risk of AI build-out - Financial Times | Financial Times | https://news.google.com/rss/articles/CBMihAFBVV95cUxNOE9rNFhZUjQwSFZpNkhrb3IyR2lMdGpUUTVWVGppaXBfUk1RNkdzYUlNT0dxOXBjSEJSamVHTlFiUlp2QjRmQmNNX1pWWHJidUhreWlNWmlXdVZVWUp4VTZUWU82WlNWUWFObUo3aEo5T3IwRWtOQzItanZaMXVMZXh2MzU?oc=5 | 2026-10-01T06:20:24Z | 선별·판정자 Claude 는 Anthropic 모델이고 이 기업은 Anthropic 투자자(2025-11 발표)다 (긴장 #4·#11) |
| SRC-NEWS-nvidia-20260930-8fbc4d99 | CoreWeave Delivers NVIDIA Vera Rubin NVL72 Performance at Production Scale, Starting With Cognition - CoreWeave | CoreWeave | https://news.google.com/rss/articles/CBMiyAFBVV95cUxNTTd2T1pOekRaT3c2NHBWS1NlOVJEWFpiR2JidzlZd18yVkRuNVMyaE5XaERqVGhKbWhrc1c5Y2dXYjFMWEh3MmpBWlZGS3BzSWFZMV82YlBORGVST3B3ZFM0c2N4M1RPQ19jRjVUVTJTR2dmeTR0YUVSYWoySkxvZjhOb2l4TlRIZzg1Z3ZadGFLU2hTWVlDWjduenRiRDVlLTZiR3Q2d1RkY1NnNXVPVVhBaGh2Vk5BYVBaam03M0E5cnpEZzNTbQ?oc=5 | 2026-10-01T06:20:24Z | 발행사(또는 거래 상대) 자체 발표 — 이해당사자 |
| SRC-NEWS-nvidia-20260930-a17a0016 | Exclusive: GPU Cloud Provider GMI Raises $668 Million From Nvidia and Others - The Information | The Information | https://news.google.com/rss/articles/CBMiqgFBVV95cUxQV2k2TTQ0M0ZEWFB2VF81b29qdzF1UTNoOFpjTjhvbGh2WjA0VGJBcjIyeVNPdmhXdG9uckhxMDEtUFJoNU5WdGt0MEE3bXgteWxOWVVrS2JLUnBMNjB1SThxS2xmZkdKMjg5WVcwWFhsellOeGZ1RC11VUIxcmw4V0J6Tmp5UHNMaWw2MmpNbWNfNzY1Rlc3Z0EwOVg0YW14WG13LS03U2lUQQ?oc=5 | 2026-10-01T06:20:24Z | 선별·판정자 Claude 는 Anthropic 모델이고 이 기업은 Anthropic 투자자(2025-11 발표)다 (긴장 #4·#11) |
| SRC-NEWS-nvidia-20260930-d8d60d93 | DeepSeek partners with Huawei to develop chip programming tools, reducing reliance on Nvidia - Reuters | Reuters | https://news.google.com/rss/articles/CBMizgFBVV95cUxPdUg5OUtKZEFWWE1PU3dHYURRTThhbS1fWTM2YzdIekQyTTIwU1daMl8wSW5XNTl4aklKSWlxVHRrazlhRlNjNXZDX0ZHd3RnUldXTUZmbGNuYXJYMUV2SFVvWEZsVWRuajcxazZ5WmZ3eEg5TEMtMVVIMXB1V0ppNHA4VEIyQzN0c0hmZDNjaWFLTE81d3IxLXZQeWVJWjhzWTNrUXBzU0IwYXhaX3NqUXkwNTJmMS1yZlhiaGNPRVUxcGZ0RmNKVFhRRVZrQQ?oc=5 | 2026-10-01T06:20:24Z | 선별·판정자 Claude 는 Anthropic 모델이고 이 기업은 Anthropic 투자자(2025-11 발표)다 (긴장 #4·#11) |
| SRC-NEWS-openai-20260928-55a96228 | Exclusive \| OpenAI Scraps Release of New AI Model Over Safety Concerns - WSJ | WSJ | https://news.google.com/rss/articles/CBMihgFBVV95cUxNcC0xNDExdTJodUowZi1yeWdFN3M5RlpvY3FvZ1lQeHltWGVkeG01ZTVlaHJ0TldqVVRhekJhWl9ZRTRLNHRqX1NQQVFKMW5NRnhBTmlUNWNpX1FBX3Myc3VlaGIxbFZTZDZYRlYwTGNVLTUtNnJScGJWcm5rX0hMMmNadFFmZw?oc=5 | 2026-10-01T06:20:32Z | 선별·판정자 Claude 는 Anthropic 모델이고 이 기업은 직접 경쟁사다 (긴장 #4·#11) |
| SRC-NEWS-openai-20260929-33642c17 | Introducing GPT-6.1 Sol - OpenAI | OpenAI | https://news.google.com/rss/articles/CBMiXkFVX3lxTE1fNFpCaXpwdjNfd3pjTWZ6X1ljNS03RTNaS2k2UE5LZ1ZnbHJVVWstREg4UWdKWjg3Y3FpT1JJTS1OOVA2SjR5WXBoZ3ZXX0ZTek9td3p3SHVsOHRSM0E?oc=5 | 2026-10-01T06:20:32Z | 발행사(또는 거래 상대) 자체 발표 — 이해당사자 · 선별·판정자 Claude 는 Anthropic 모델이고 이 기업은 직접 경쟁사다 (긴장 #4·#11) |
| SRC-NEWS-openai-20260929-4db7c342 | Advocates sue OpenAI over Hugging Face hack under California anti-hacking law - Politico | Politico | https://news.google.com/rss/articles/CBMixAFBVV95cUxQbFBxM0d5dzFnM25xWGt3ZVl1cVd3Rl9haHpyLVI3Wm1uWHItVjFMN2VsNVBEVVNQSDNXVlJabmkycmN2S1IxSy1oS2ZvSTk4RDV5U2h4Q3A0bXd2UzdUOENPbnFNcXRPaXBQUHNoSUI4YWM5VURwdzBoWmVGM2Q3VTlqemk1MkZhRDlkY3JvTHBYVEhiUWRyOXZkUzl5cHI1Z3I1eXduX3ZQMW9KbHNOYmh1Q2xyWG5NcUdZMU1MdnM3LXdF?oc=5 | 2026-10-01T06:20:32Z | 선별·판정자 Claude 는 Anthropic 모델이고 이 기업은 직접 경쟁사다 (긴장 #4·#11) |
| SRC-NEWS-openai-20260929-6afb4340 | Scoop: OpenAI's annual recurring revenue nears $70B - axios.com | axios.com | https://news.google.com/rss/articles/CBMiiAFBVV95cUxQT2xYcWJPOUFTTWFUWmpMSFN1UzdQc3ZoWmFFUEpsTFJFcjZBbkdqemNrN18ydnpIQnJyR09xMW9Ba2ZHWkFwRUMyMlZLcFkxQ1dDdl9mb1MxZnYwcExXcGNFTFQ3UHBTbERwM2pVYzdwcnZ6MnNSM3NHbE5VODFfaXNhX3dsQjF3?oc=5 | 2026-10-01T06:20:32Z | 선별·판정자 Claude 는 Anthropic 모델이고 이 기업은 직접 경쟁사다 (긴장 #4·#11) |
| SRC-NEWS-openai-20260929-6f60caf1 | OpenAI Unveils Always-On AI Agent Dots, New $500 Paid Tier - Bloomberg.com | Bloomberg.com | https://news.google.com/rss/articles/CBMiqwFBVV95cUxNVkdWY0tGVFAtWVplbzRxRmNxdzJaQ0JVSVFTbXBEZHVvZnJRRUtGNUF4Q05kU1ZyNGNUYjgwWld3WWltZWpmSUNuX3ZFX3czSDlhbFh6S1psUU1rTkRSdjlCYUlNak53b3dCZDRqcmZFMVNOMk1NWEFSNkJCTGR2enBRckM0STVVd3I2VmMtOUxnQVJCS1dZa0tNRmhwam9wYThHcUoteWU3NUU?oc=5 | 2026-10-01T06:20:32Z | 선별·판정자 Claude 는 Anthropic 모델이고 이 기업은 직접 경쟁사다 (긴장 #4·#11) |
| SRC-NEWS-openai-20260930-6e42d8f6 | FTC opens probe into AI giants including Anthropic and OpenAI - Reuters | Reuters | https://news.google.com/rss/articles/CBMiwgFBVV95cUxQdzYzcTVSY1JmRld3cFRBRlRaX0w0YVZHTjU3NWVvVG5BcXFIZGFwdXViLXBLNnhJQ3d0RS13T2VURWdNQ19ySkJuVXNlV2NWX0E3LUExYUZQaFBsTTVEaC1NMXJtR0RGYlllQVotQmM3VlRaVmd2em04YWdzTXFkMjhsUlQ0b1JlcVJBRENNRFFBT1NLcU00YUtqU0N5LUlJa0YxaEhzdU1mR1lkUTJ0MFhLMjA3a1FJVlQ5RXpMOEIxdw?oc=5 | 2026-10-01T06:20:32Z | 선별·판정자 Claude 는 Anthropic 모델이고 이 기업은 직접 경쟁사다 (긴장 #4·#11) |
| SRC-NEWS-openai-20260930-b2180845 | OpenAI and Synopsys Announce GPT-Synopsys: Frontier Intelligence to Revolutionize Chip Design - Synopsys | Synopsys | https://news.google.com/rss/articles/CBMiyAFBVV95cUxPWmx4bUlpbGx3MEpZYlhQSnRtVDVxejJ5bnZoU3FabmRPaHdHdGM2Zjg5OEpydUxGQ3pac1BSX3psbnhieWpVVnFweWJ5czJfZk9vbU9TaTIyZm5ROW92RzZzWmJ0NlJjQVlZQnR0MGtyb3JzTW5NYWIxQVJsNi0zSHRLUS0xa2VFQ0FEQnpuWGpMQVFpa1RoSTYybTFzal9lQkZJYmNBLXFKaFVWQUNLSTN5TGY1WUgxbmwzY2lzVmRGbmhrSGJLMw?oc=5 | 2026-10-01T06:20:32Z | 발행사(또는 거래 상대) 자체 발표 — 이해당사자 · 선별·판정자 Claude 는 Anthropic 모델이고 이 기업은 직접 경쟁사다 (긴장 #4·#11) |
| SRC-NEWS-openai-20260930-d325e395 | Disrupting a coordinated model-distillation campaign - OpenAI | OpenAI | https://news.google.com/rss/articles/CBMihAFBVV95cUxQbEgxOFhvU3ZzR0JYMjZDbWhRaXlQeGoyci1PRGhfWkFhSGpER29fLXZydWRybEdpVEhUX0dCZ3pwS0ViUWRxVy1NVXZNREVfN2pOMU96c2NmSmlpY1lheUwxMGxuVjlmTV9uSkszVHU0RFhVVVNNUU42TkNjb084cThtaWc?oc=5 | 2026-10-01T06:20:32Z | 발행사(또는 거래 상대) 자체 발표 — 이해당사자 · 선별·판정자 Claude 는 Anthropic 모델이고 이 기업은 직접 경쟁사다 (긴장 #4·#11) |
| SRC-NEWS-oracle-20260813-631889f2 | Oracle and AWS Deepen Strategic Collaboration as Enterprise Adoption of Oracle AI Database@AWS Accelerates - Oracle | Oracle | https://news.google.com/rss/articles/CBMi9AFBVV95cUxQZ185cDBzMXo5c2RXdTNrbFZiV0VuelJqdjVuN1Zld3VwU3NfdFVIck5HaGJSa3N6dzhwWWYxNVJxNkZ0aFktY0EzcGRNQ01wNm1mdnRvYUVKdDBKVTI1d044a3BfNEdFMEswTEhLSjBkX3pzNFNUdXRPanNaLWtySkx0d0VrQzRMVnhoMmFuNTVBZTJ6bTNWdE5DdGpwTHJwT3NWU01vejdYRngxbjltUTc0VmR6ZElWWGtDVHQzcGNoeWVjUHpRYjdBYXdBLWlGZ3BmdjRZSnlyWGhRTWFyOWJ6N2hHZEJSRHZfV1Mza2ZIZUF3?oc=5 | 2026-10-01T06:20:30Z | 발행사(또는 거래 상대) 자체 발표 — 이해당사자 |
| SRC-NEWS-oracle-20260924-f9026ef9 | Oracle sends 'force majeure' notice about data center project — stock drops 3% - CNBC | CNBC | https://news.google.com/rss/articles/CBMieEFVX3lxTE83OGFNcURydFoxR0o2WFYyX2ZTRkVUdno1UnNET2lrM0ZDVUdnZE11NWtMWFl1NnV1aU4tbXlLeFgtUEJVT2ZRY0tVcWxZWnpZR0g0a2owZDNYUHQ5Z05NZDY0aDAwUGhQMHZtUFZVd2lXX3Nnbkp5b9IBfkFVX3lxTE9xalhSV0NpQlJoUnQ4VDZGYUQtR1hnY1ZKMlVPVlRTelNaQk9qMTF5NzROY2xRcmFVNFJBQnY4QnlsVVRuOE53T1BtaDVxTXJlZlB2UzZhWmE2b0hPZmFlYlhZSDdDbU5lbEpGSnFvUGJtWVd5S1RZMGFvdG1Qdw?oc=5 | 2026-10-01T06:20:30Z | — |
| SRC-NEWS-oracle-20261001-610bad32 | China’s Tencent leases 100,000 chips from Oracle to accelerate AI push, FT reports - Reuters | Reuters | https://news.google.com/rss/articles/CBMiuwFBVV95cUxNR3F1ZTMtVFZsOVNXOEU4X09jTTI0RDVYNUJmQUNVVUhJQkV6YlRmdldFaWwyVzU1UnZLQl9Ia0tqTHlBZ09SUXZ6VC1kcEx6bjQyQlgxXzI1YVpwYldSV3NwNXZRRkFPSWQzclhFbE04anBtbnRZV2FwRUlIMmU2eVV3M0VscEE1Znd5bU5rNEhwWVVXdlR0c2tIbnlnald3VVBJdVFiTDZMUmhqV0x1bE1jVVR2STZ5bHdF?oc=5 | 2026-10-01T06:20:30Z | — |
| SRC-NEWS-palantir-20260903-dc8fbfac | PwC and Palantir expand strategic alliance for enterprise AI - PwC | PwC | https://news.google.com/rss/articles/CBMilAFBVV95cUxPUDRrWFAzTGd0SDR1SFhVVV9wTnRyUmhOUjFRRGNLVXlNQVE5Y0JsUGh2cThPWDJqdE5ObzZ6T2d5S2Y3RW0ybXh2c0x3M1hfeXRLOFQ2aEJyOUJqaWdBRGhfMTFxbTlPTmkyZ29JYkRfY09FZll5T3NnaU55dFJxa3h1dUNXSWd4cC1qbXNRRjdGSkJn?oc=5 | 2026-10-01T06:20:25Z | 발행사(또는 거래 상대) 자체 발표 — 이해당사자 |
| SRC-NEWS-palantir-20260916-6b44094b | Chipotle Is Working With Palantir to Track Food Safety Risks - WIRED | WIRED | https://news.google.com/rss/articles/CBMigwFBVV95cUxNRjZ2WFF6NTVKSk1aejZlaXJWNi1wUmoxdHBVYnBfWnZmYkF6Ung0YV9fYk1VLXl4dEtXQll2OFJjNGcwclVScl9LblFOeGdOb25oRE1xQ0hPTFY3TU1jc0NUZmppTExSbnRvRHlicXJWa1M5UUxXQnpyMHA0R1dYa3ZFcw?oc=5 | 2026-10-01T06:20:25Z | — |
| SRC-NEWS-palantir-20260921-b2794839 | Five UK police forces end Palantir project after two years - Financial Times | Financial Times | https://news.google.com/rss/articles/CBMihAFBVV95cUxOVkE3SDI3N2ROT0xEVkJlcUI3MFJjTHFHZ1ZtcGN5M2dBNk1LNFptaHYxSnBpRGQzODhMM2lCLTQzVEdNRUFrZlZneE5IRVgyVHpTcFUwdlBCd2ZmTEktamp1U1hQSUNqVF91T2h1bmhLTUVBWTZiWGtPSkdZcUgzUGVqUHE?oc=5 | 2026-10-01T06:20:25Z | — |
| SRC-NEWS-palantir-20260928-5212f73d | 'Not Just Another Tech Company': Unions, Rights Groups Across EU Demand Governments Ditch Palantir - Common Dreams | Common Dreams | https://news.google.com/rss/articles/CBMidkFVX3lxTE1HdDhKeVVDblBLQ2JCWEoyTWZ3TXRXU21DR0NKQ19pSDZURXBmU0FuODhlWk5wQ0hyNWM3ZEhfRThpNHBSaUQtblU5dy14b19uaEhibHd1UVEyQ0NMN0YtNnpTVkZ2VDdEVzNPNTJBcWVFVDhxNGc?oc=5 | 2026-10-01T06:20:25Z | — |
| SRC-NEWS-palantir-20261001-5df9629b | More than 44,000 file legal objections to Palantir NHS platform handling their data - The Guardian | The Guardian | https://news.google.com/rss/articles/CBMipgFBVV95cUxNc2lpa0pURkdTLWNUZ25IZEthd1JacVhRN3RzRVF4S0dDSUttNmlDNXJVUVBGRmZ3cU9LZjg0Ym54Qi1hZGZnTnREWUY2QTVudDBBWEN1N3FRME4tN3IyRWNsQTc4X3Y4OGFSb21wQ0x6WXdWZU1jdjk2NUgzazNFSHhGNDBFdzJ0TVNmVk5XN2ltWk5qNGFlMXFIMWhnTGU1YmF0Q0Rn?oc=5 | 2026-10-01T06:20:25Z | — |
| SRC-NEWS-palantir-20261001-a9fde893 | San Francisco nurses protest ICE connection with Palantir - CBS News | CBS News | https://news.google.com/rss/articles/CBMiowFBVV95cUxOMXVKVVdGd0RqMkk1c0pSaDJ4a0FVTkdjVDN6VW11elZ1UnhXOGd6M0hzSWNYa3RtVXFyOGVIQzlGV3Fhb1pBbzljbk41Y3JPZEdaejcyRmlaNjhwUUVlTlNXeU8xMFVtQm9ZR0ZfR1RTeXRqT3hnNkdRNENWaGVXZ1JidHdGbFNZNHJyNTJzb3lCNkp2TWJjT1BDOE1zdFVOTzlz?oc=5 | 2026-10-01T06:20:25Z | — |
| SRC-NEWS-spacex-xai-20260605-203712fc | Google to pay SpaceX $920 million a month for compute capacity at xAI data centers - cnbc.com | cnbc.com | https://news.google.com/rss/articles/CBMipAFBVV95cUxQbTlsMnZmeWxoUk0yWmhKcGs0eVhkc1d1c1JVRm9qUWFMQWVuTy1YcmFyVDBGTDhkOGwyRlBhNWFJWTVBTHNOOUlsSVFzVlB3bXFjZWZYaEhWblQwSU5yc00wU241V3BoVFEtTndGcURrVXc2eFBLMlFuZkdUSzdkUEpZNXctWHVvUjZTczUzRE4tNHA3eUgtVVN4NVZKWnZUd2NKRNIBqgFBVV95cUxNRGdVeDExV2J4SUxteXpvQVJqMWl2NmstN3lpR3dqaHU1djhwNkozR0pyZG5wZlhiRU9zSVdod0xyZWYwbEljVEpMOXdIelJzZFV3SVV3UHBvOUZzS3VKWGlLV3RIemFaZTFMOEh2ZlBDNW9fLXVlWXZSVU5RTGkxcHZzc1VSWU05SWdkMGtrZWR0aFJwb3FfZEs5bl9SQjJYWUJOTGVqU05iZw?oc=5 | 2026-10-01T06:20:27Z | 선별·판정자 Claude 는 Anthropic 모델이고 이 기업은 Anthropic 경쟁사(xAI)이자 컴퓨트 공급자다 (긴장 #4·#11) |
| SRC-NEWS-spacex-xai-20260610-7046be22 | Musk’s xAI, SpaceX hit with class action over data center ‘nuisance’ - Reuters | Reuters | https://news.google.com/rss/articles/CBMiuAFBVV95cUxQbEFyQzQ4ZU9aVGpfNzdpR204a01GdlJQTFJvTERRNktfNTBVMDVyT2xXQWF0aTduWXNYUmVMRk8yT0s2RU5GZ0UwaVA3MlBOaGNGSFpXN01naTBHczNCdjU4WHV6empVc3ZPYTkxOGJrSkVmNnR2cW8wT0RlTnRDaV84dXVNVUtKZ21KTnktUERQWVlBTXdrZGkySTlQeG1fNkw4TWMycm9NWG5QMjdDc2dBQ3laYV9J?oc=5 | 2026-10-01T06:20:27Z | 선별·판정자 Claude 는 Anthropic 모델이고 이 기업은 Anthropic 경쟁사(xAI)이자 컴퓨트 공급자다 (긴장 #4·#11) |
| SRC-NEWS-spacex-xai-20260921-493f36d2 | Introducing Grok 4.7 - xAI | xAI | https://news.google.com/rss/articles/CBMiP0FVX3lxTFBqb2x1bzQ3UkxTVDFCUVRjODMzbDJ5YTg3Nmh5Q2luZGdUTmctZmo1Ukp4c3RVdUhfSGZFc1p5SQ?oc=5 | 2026-10-01T06:20:27Z | 발행사(또는 거래 상대) 자체 발표 — 이해당사자 |
| SRC-NEWS-spacex-xai-20260925-53213e3b | SpaceX (SPCX) Wins $946 Million More from NASA. What Comes after the Space Station? - Yahoo Finance | Yahoo Finance | https://news.google.com/rss/articles/CBMimAFBVV95cUxNcTRUVXc5OVB0U1hULWdWZlJtS2hwdFROWHlEMFkxM3FUVDhTWHBvVE1BSmlrc3BLTHJCc2JSeGUyX2toVG1STzd0NWFzYTZRN3lRbmI4bU1pN3YtbkJhQW9CaGEyTFFkWGN0VWpwSi1QdURIYUZXeGM2anAzMmFSZEdQb1RFTDF0bUEzckdtb3VWNm56a3RTWA?oc=5 | 2026-10-01T06:20:27Z | 선별·판정자 Claude 는 Anthropic 모델이고 이 기업은 Anthropic 경쟁사(xAI)이자 컴퓨트 공급자다 (긴장 #4·#11) |
| SRC-NEWS-spacex-xai-20260928-504eea45 | SpaceX Launches Starship Flight 14, Deploys Starlink Satellites. - Investor's Business Daily | Investor's Business Daily | https://news.google.com/rss/articles/CBMingFBVV95cUxNaVRhMG1KOWZyTmRBVUxUeE5lakZDRVNKOG55NVh2ZGN2T2theGx0dzdhQU9SYUpLamdNWkJVcERKb05SM21vWDFoMmFZS2Q4ZUhESTA3VF9hVno0bGJnekhXeXdKM0VNcnZIaEliOXNERVhVczBMZ0pCN3k5TmdJNWxsUlZ6cDItbTJKNEowUlNIX0NCcXdYdGM0R3F1UQ?oc=5 | 2026-10-01T06:20:27Z | 선별·판정자 Claude 는 Anthropic 모델이고 이 기업은 Anthropic 경쟁사(xAI)이자 컴퓨트 공급자다 (긴장 #4·#11) |
| SRC-NEWS-spacex-xai-20260928-e0ca82c5 | Elon Musk, SpaceXAI subpoenaed by NYC in AI safety investigation - cnbc.com | cnbc.com | https://news.google.com/rss/articles/CBMiogFBVV95cUxNaVRaV1ZvZGVLN2Y3bG50TlZfTE14R1JfcXotZzRsR2FiZWFwaTJtUHNDbFhjbllzVzRFY3NHYXVmTGRmMVdWb3BfcTdJdzlSazVjQklmb0hQSmZEZVRqdm1tbTJxUURQc0JMZE4xUFFaN2tNZzRvMjQ3UnFPMVJYZkxmdElkMzNLN1ZuakJqX0VQNGdzNVF1TUNsX3hzZzhURUHSAacBQVVfeXFMUGlFS29DakNYYThBSEVpckxsWUtCN0RUX3VuaWdGa3JqOS14YU9wVEpSdjhBWTA3NzJGWFIyaUlQeS11UlRja0U2T0paSzVsZGJMRkE3NGotQi1XSmZ6Tm1nRlNMbkUydzYwalVaMHZkSHNDeExPQTRFOVk1Vl9pUEp4dWJUVDZSQnc2OURoMnVMVDNVdkNucUpSWEU1VnhGYk54UmxFWGM?oc=5 | 2026-10-01T06:20:27Z | 선별·판정자 Claude 는 Anthropic 모델이고 이 기업은 Anthropic 경쟁사(xAI)이자 컴퓨트 공급자다 (긴장 #4·#11) |
| SRC-NEWS-spacex-xai-20260930-855edb41 | Anthropic-SpaceX Compute Deal Size Revealed: Potential Spending Up to $84.5 Billion Nearly Doubles Prior Disclosure - TradingKey | TradingKey | https://news.google.com/rss/articles/CBMi0wFBVV95cUxOLVFGNlM4QjN1dW9aMUJ4Rmxfa3ZaeHlSN1htZVF2N29sdERIdE1zNE9MNHFkOEFtRlRxaVdtWGd3TVE4dE96MVZVeHhaM01fQVZLdnk3LTJKTC0yanhzQWg0dnViM09tdUd6TVRaeTI2a256ZzktQUFEeFk1ZDc5Z1FYcHdCUlhMNmQzWEtyRWREc0NmX2RwNnU3cG9pc19yUjNhVVhEZTZad0t2U3RsRktvdXVLaERIS3QxaVJTMjJiY2ttLWt0ekZ2a2ZtV1JiZUJv?oc=5 | 2026-10-01T06:20:27Z | 선별·판정자 Claude 는 Anthropic 모델이고 이 기업은 Anthropic 경쟁사(xAI)이자 컴퓨트 공급자다 (긴장 #4·#11) |
| SRC-NEWS-tesla-20260924-4eecf2fa | Tesla is beginning Semi electric truck deliveries - Reuters | Reuters | https://news.google.com/rss/articles/CBMixgFBVV95cUxNX0ZFLVRhWm80M1ZOV2VHUUNXQXJPVVRXVEVRSkExYjRqRERCZ09WeVVUZzJuMUZYaUNObjVCY3BKWHVEb1FGMlRFN0o5ZEJ3NEJkWU52akcwODE0V0lFLXdEZVFVZGp2VHNYOUJodEQ1QVBQZmhpd2YwSDZ5U1hoOTlqMzlEMjg1NnlIbVRlQlRhSzZ4VzlsYUhDR1lNemd5SU9aVGpKRFNnWVF2Ukl2TDRhc1VtMk5SMHZGbHdVY0pUdm54OGc?oc=5 | 2026-10-01T06:20:28Z | — |
| SRC-NEWS-tesla-20260929-79b72b41 | Safety group urges EU to reject Tesla FSD over speed offset - Reuters | Reuters | https://news.google.com/rss/articles/CBMivwFBVV95cUxQQ0pPYVBiQTZoVXBmNnNuWlZLWVhwd0ZJckNOVWhhT3o4Q2cwLTVxZ1RaTy0zWVNJMHViYkNfZGVqTjB1ZFVJOUhtN18tZ3dNVDZZMW5RRU1vS0ZIWkpxbDZwS243UjFjMEJHa3p2Z2s0OUFFb3kxdlhCZXEwLVlRREdLdi1jWDlJcGpGY0ZZemVVakp0eWM0QXVjcGhCWDl5UzhaWG9VUEtrM1JXUDFINk1QUnNNOE85azBtZFdDOA?oc=5 | 2026-10-01T06:20:28Z | — |
| SRC-NEWS-tesla-20260930-09ab05ff | Tesla Robotaxi fleets are the new crypto treasury for zombie companies - electrek.co | electrek.co | https://news.google.com/rss/articles/CBMilwFBVV95cUxPeFowNmhCbjY0d0prVHVhM0U0RExXUDE3V0Q3UFZDcVp4VktBV3pqNTl3c0dramhoMDdSUktrTmVVRWpNTGg4LXNuVW5NZmN4bTRiZlNGVlhIbUhmN3RzNkp1M0FQQktGTm9uX2p2dl9May1ZTFRydnVlOHhXM3o5NTBsV01iZ1ExNTNONGl0dERqWkxDVzNR?oc=5 | 2026-10-01T06:20:28Z | — |
| SRC-NEWS-tesla-20261001-c4096f8a | 2027 Tesla Model Y Performance gets $4500 price cut amid move to Chinese sourcing - carexpert.com.au | carexpert.com.au | https://news.google.com/rss/articles/CBMiwgFBVV95cUxPREFlNGpsa1piQnlJUWpoTjFaVWxqWFh5ekQ2UkNra29kRUhQMm9qc3VFMDVtemRrekN6eXZFTVo4RkNSR0JQYzBvSkdHN1daMlM2Um5CcTlWbVJ6VHNDSWFEU29wSUREd0tMd3NNcEZDUEt5S3VOai1RWG9vREYtbFFVVTlWVnNtdnJPMDF3bE5ySnF0Q3U5N2VjWDJFR2R3WXVlYkJiMjA1Si1PRmFCUXB6WWh4TXdsXzZzUHhIWmRRUQ?oc=5 | 2026-10-01T06:20:28Z | — |
| SRC-NEWS-tsmc-20260908-7c6765b5 | ASML and TSMC Announce Initiative to Pioneer Industry Transition to Large-Format Photomasks for High NA EUV - pr.tsmc.com | pr.tsmc.com | https://news.google.com/rss/articles/CBMiTkFVX3lxTE9nSmxRNFVNTTQ1WUhsaGQ2NWx5OXE4eXlFRGVsMHFnNFk3c0c1b3JYVzlfeEtkQ01PX2tkTE4tbHo2RFIwcGYyTWl0NVUxQQ?oc=5 | 2026-10-01T06:20:18Z | 발행사(또는 거래 상대) 자체 발표 — 이해당사자 |
| SRC-NEWS-tsmc-20260910-9e469fd3 | TSMC August 2026 Revenue Report\|Taiwan Semiconductor Manufacturing Company Limited - pr.tsmc.com | pr.tsmc.com | https://news.google.com/rss/articles/CBMiTkFVX3lxTE1aTzR4TnFXdW1kTFFUa2l1ck9vOWlFMUM3ZXBZdnhsODZsVDZ6NHB5TzY1ZWg1QUlOMzJBNS1FaDNhMUJVa2ZfU1ZwOUhOdw?oc=5 | 2026-10-01T06:20:18Z | 발행사(또는 거래 상대) 자체 발표 — 이해당사자 |
| SRC-NEWS-tsmc-20260918-d70d800e | Taiwan Semiconductor Manufacturing (TSM) Starts Commercial 2 Nm Production - simplywall.st | simplywall.st | https://news.google.com/rss/articles/CBMi7AFBVV95cUxNblhVN1A1bzdQekU0cGtoSUZRb0QzOU9mbk16amtyNVFSUy1WY044QmlUcFRSQWlISHM5aUZPWXNwMTRXa0lCNGg5aHlNNHBSS1lNUHNXR2VJQWNLbWpEMExNdjVhVjFpVDZ0b2RhOWZoNGt6bzd0RGx0eUhiTGN2SUp6RE9nMGJiUVV5Y1IzREpjY0tQTXpySVJtYV9MWjVQdVdmWTdsbS1RR3d1SXNpOXZaN1FBdFhYT1MyaExaZWtWeTc0bDlNUnZsb3Q4WHNfVFJhUFhxZmRCZTV3NzlwRFpVT05KQWVaNWFJOdIB8gFBVV95cUxPWk9pZE9KSExncUhORVAycGlFbWFNZ0hTTEFfX000Tzd0NzhNNzk5OFBTLUN1dnVxQnA1aXhDV051N09DTnZPUHVpTThrejAyTkJ2UjYwUjlmS1JDMFVHVk5Yd3hxbmtyX2FNZ2lJRDlGZ1RzZ3BBcE1XdGRPZy00Z2V6QkY2Y0RJcDhiYUZfckJ4N2o5MTM1anpicUROV1FtdW1mNTROakdJVmw5Wk1kZVR6eGwxYUVsejFRdVlCeldLeUdvTVRnMFpWYWpoV28yYWljZWFvbGthbFlZNG5SaEhNR19VTF9falBpOGdBSUFKUQ?oc=5 | 2026-10-01T06:20:18Z | — |
| SRC-NEWS-tsmc-20260925-f136e604 | Why Is Taiwan Semiconductor Manufacturing (TSM) Raising Wafer Prices By 3% To 6%? - Yahoo Finance | Yahoo Finance | https://news.google.com/rss/articles/CBMiqwFBVV95cUxQeGI1RTFZT1FHOHk3dGNwd2xoRXd1RlYwUm9LVENPaDlBVGtoWnMzMHlESkhpSzlZSjYzNGdNNklzREY2WktxRzFMTnFkSE9STDdCQ3hwaTF1c1NzUlpTT01ZMnliWVpkRkVoNG9kbFl2N3VmOE9Ia1Q1bm9tOFBrNDR6ZUYtTF9tX1BtVW1NU0xSU3B6UFcwUnJmc3QwRWUwRzF1ZlF6T0pzUU0?oc=5 | 2026-10-01T06:20:18Z | — |
| SRC-NEWS-tsmc-20260930-57876971 | AI demand powers Foundry 2.0 revenue 25% as TSMC leads 42%, Samsung 4% - CHOSUNBIZ - Chosunbiz | Chosunbiz | https://news.google.com/rss/articles/CBMiekFVX3lxTE96bVdZamtPbDlFNldVOWtjMmpyS0hWWjBvRUZpVEpIczVXanl4VDNXdDlEclRNRmxERmN3VFhBNlVaTGxleWhGekJXUG9BQWhWbEFSbTFxaWV5NmR1X21yX0tfcU5GbmxiR1NTX2VPQlkydkQ0YVFaWGlR0gGOAUFVX3lxTE44NjcxWVZock95UGVja2ppa1hsNUJpdmJkaS12bmtHR3ZreGFzTnZFU0NRZHJpZC15ZWY3MXlheXdjM29MVnM5MXZ4c29xWER3bTE2YTFLdmFxeFFfNjB5ODRoVktkUXZUTS1XNzBHeXdwTzA3eFh5ekRnLXhESjg4VnZLY1hUN3VyWVZ0WkE?oc=5 | 2026-10-01T06:20:18Z | — |
| SRC-NEWS-tsmc-20261001-3eee57cf | Lip-Bu Tan calls TSMC a partner rather than a rival - digitimes | digitimes | https://news.google.com/rss/articles/CBMijAFBVV95cUxNWW82ZlFIOG9kMHZqdnlsYkxCOWlOeE1Fb01XeEoxYWtkYjRHck04R2ZxdEJ6TzhBRTRTNFZkUlI5SEp2S0ttN0FXWVk5aFdRSXFzM3UxcU0zLTF5TjNvNWhaOHZXeVVjLThiUjlZQlA3Skx0NXc3ODB6dTFkVnNzYXpHSkREbjNOc2UxMQ?oc=5 | 2026-10-01T06:20:18Z | — |
| SRC-NEWS-alibaba-20260817-6de25302 | Alibaba to sell Lingxi Games in more than $2 billion deal, source says - Reuters | Reuters | https://news.google.com/rss/articles/CBMiugFBVV95cUxPajRKUDBRNldLY05VNW41RUVRX3c4SXpiZUcxdk1OMnh5NWtVbUlBaG1aNkZMZjVfTGZSbFd1LUliM1dMcmtkSFlFZ2NRc243UnRmaF9QMHY2bzg0cDI3WkZ2ZmpoNGpDeHcyQTRRVkRQcGRyZ01YcVVoT25HUEd3alFkcnd0eDZlTHp1MGtXcDVjXzRVUTNhX3A4OEVpN1ptUzF5YTNac2I5Y1NIQktrd3R6VDNUczVPTmc?oc=5 | 2026-10-01T06:20:20Z | — |
| SRC-NEWS-alibaba-20260921-dd55dc76 | Alibaba Unveils AI Chip to Drive 20GW of Data Centers by 2032 - Yahoo Finance | Yahoo Finance | https://news.google.com/rss/articles/CBMimAFBVV95cUxNR19SYXVvMHNMSTFNa2pWVFJyS2o1alJCQzRGV2ZBcHlTc2tsQzFVcGFPZEFOV2E4a1NoU0lNcGVWdkY4MmU1bnFfVTlPbkI4S19hcktjS0t4RG04cGFOQ1BBMlhXVUd1X05nZFZQcWREOVlyQ2xDRHpKS3FXUGxydTdNbHdzMFh5OXp2V3pXeWM3QURaVDI2Vw?oc=5 | 2026-10-01T06:20:20Z | — |
| SRC-NEWS-alibaba-20260922-544642a0 | Alibaba to Add Data Centers in Europe, Middle East in AI Push - Bloomberg.com | Bloomberg.com | https://news.google.com/rss/articles/CBMisAFBVV95cUxPMUZ4Q0M5UER6MW1vRVU3Ui1iOTB5VWNnT0stWjBvdXVzRDZ4X0hBNjh4bDlua1Z3V2dpYWR3NFMtNWs2eGhCMU9GdV9FUEdFandmZmczMFM5SHNmSEwwNHZ0TkFvWnk4M2duWlQzMHdzUkw4SUNFQ2xzTXpNQlM0ODJ6dC1iR3d2dlNzWTA4dXpVSnA5b1JzaVpNN1B2WjVpaDNzYzVFMkxId0tvdG5IUw?oc=5 | 2026-10-01T06:20:20Z | — |
| SRC-NEWS-alibaba-20260923-9cfa5261 | Alibaba to open new cloud regions in Finland, Netherlands and Turkey - Euronews.com | Euronews.com | https://news.google.com/rss/articles/CBMiuwFBVV95cUxNTjdHSFRybkFLaFdveDNHRHlJN1NmOGZLUGlYZHpLX0FtM0pmYXZ3QjdkQm94aDF5S1JoLThXM01VbklLUE5oOWNFd2lJNGVTNUl3eDZOTjJwRWRIN21wS09KU3loa0lQbWItenFpcHkxZzBWR2JicVNqZXRBSUF1aE83RjFNemhBMWxrb2JyUkpkRTlDOWRYeTBPWW1KcXB3NnRpbnU4bnlyYXRyOGxwbjRVOGVtUk13VmJB?oc=5 | 2026-10-01T06:20:20Z | — |
| SRC-NEWS-alibaba-20260928-906e333e | China weighs allowing ByteDance, Alibaba to buy new Nvidia chips, The Information reports - Reuters | Reuters | https://news.google.com/rss/articles/CBMi2AFBVV95cUxPX0pMdFpwUWhaRHhFM1pvcndCTDdIX1NOQUVwV2JIX0xIcXByV3Z4UWQyblZRVWl5elZ0TkYxV3BXUEluN0llM0VnUDJvVmN4X19pcXJVX0tSNDdEUWdaNGFFVVQ3N01VaWJHQ1FXVEdVZTJJcDFvZlJ0QmE0b2JpeGM4RDdBMDh4YmNxRkhILVJDRGktQzRPdGNsV2VxWHBjZWt0Q3hRN2FwZWlhcDhMcUZ0LUJsS1FoWGVQUG1PVWp4cEpCcEtVdUJVRVQ4cjZxVUxjM1lDWFM?oc=5 | 2026-10-01T06:20:20Z | — |
| SRC-NEWS-anthropic-20260928-2d95d4f7 | Trump had private dinner with Anthropic CEO Dario Amodei - CBS News | CBS News | https://news.google.com/rss/articles/CBMic0FVX3lxTFBmS3p3UklKQ2thNFVDMTRlNUttODQ5ZXRBY1ZnSUZ4OU5iVWlhMXNqTjZSY3lJa1duUXlOTkJxNHhmTnN3OFktd255YVpFNURmLW11a09QODZZNEtibllFOTVja0RydjR3am1BNEYzV0lRSVk?oc=5 | 2026-10-01T06:20:21Z | 선별·판정자 Claude 는 Anthropic 모델이고 이 기업은 당사자다 (긴장 #4·#11) |
| SRC-NEWS-anthropic-20260930-7235967b | 3 Important Things to Know About AI Giant Anthropic Ahead of Its Possible November IPO - The Motley Fool | The Motley Fool | https://news.google.com/rss/articles/CBMimAFBVV95cUxOTFJIdE9rQkhJZ3J3Wm9zN1U1bDJzQ05FOXBxQ3RiOVRlbnNnRXM1WWU3Qmp5X2VjTUFUUjkwTFdwcGktX19uVEsxd1NWcnFGV2dWdE5NdE93ZU1Cc0Q2MndWN2NOTzdMclFhMHV0QWxSQ0tORnBiRUgwMU5uSTdfSjRwTkY4UjhFUnlXRVIwRXNsRFRteGxjRg?oc=5 | 2026-10-01T06:20:21Z | 선별·판정자 Claude 는 Anthropic 모델이고 이 기업은 당사자다 (긴장 #4·#11) |
| SRC-NEWS-apple-20260930-a6b45485 | Apple Is Finally Ready to Enter Its Next Big Category: the Smart Home - bloomberg.com | bloomberg.com | https://news.google.com/rss/articles/CBMiuwFBVV95cUxPRmVFekxvT0hOQ2dvNUpQYUg0bEM1UUFoc3lxX2J3T2hhd2lUSlMtN0ZuNGVjeDlXYmdzU05taC0xQk11Tmxqd196SGw5ZzdEWXJaS3kwaDFXblhuT0NyemJibUxRekdHa3Z1R0RIS0Mwa21MZ1NTWG9EZHJUZU9rSnYxbG02UDFGVkxWVG9wcXdnaEU0cC1xUnhtc1hNQWN0UnVHYmk5S01kb1didlVJQVc1MGZWMUJmTXFr?oc=5 | 2026-10-01T06:20:22Z | — |
| SRC-NEWS-apple-20261001-e4d989e2 | AAPL Stock In Focus: Tim Cook Reportedly Confirms Hike In Apple Products Due To Memory Chip Crunch - Stocktwits | Stocktwits | https://news.google.com/rss/articles/CBMi8wFBVV95cUxPOFFYSDdudXJRNlFCa1AzanRBVVhBYVBHVWdZNlJ6X3l3cEM4eVFqQjZ1cXFPZEM0SVpBbVdZR3hEci1oMzc0ZDRRa1kzLXJ0Wi1OU1ZqNTIzRzE2NjktNzZWWkc3OUt6LXBENGhGVkc3X00ybUJHQW1VWWhzOXcwUlhTR0lGb1djMEtTem1vQjZrTHhOQmw4dkRxVWlNeldkaDVzcDlYUk5sWGJDdFpJNGJzcHJTTWVuUktvR2QzbHVQeWUtMUFaai10bmJHaWJuTlJGMnRMWFhKbkpaZngzTDgtSy1ZM282U1pZc0ZCd3lEeDg?oc=5 | 2026-10-01T06:20:22Z | — |
| SRC-NEWS-microsoft-20260930-8f6eb044 | Microsoft To Enable Usage-Based Billing By Default For Copilot Business Licenses - crn.com | crn.com | https://news.google.com/rss/articles/CBMipwFBVV95cUxPSnNlcThfaG96OTBFQ0U5RzlDd0RGWmxpcEhhcWRYUk9LUzZMMDV0V1dCSV94bWJhZXJHN3g1Y2IyZkl6TFRMZ3BsN3M5d01LWHVYSWRlQ01zVGlxa1BOa2NOamhvdl9zSzNLV092LTA5bUtuX0xTQlZHbmFYdVhKbzNrU21Rbk94ekNsVk15NEJQN1MxYm9iS1dwck5xdlc4aVh4YThmNA?oc=5 | 2026-10-01T06:20:15Z | 선별·판정자 Claude 는 Anthropic 모델이고 이 기업은 Anthropic 투자자다 (긴장 #4·#11) |
| SRC-NEWS-nvidia-20260928-906e333e | China weighs allowing ByteDance, Alibaba to buy new Nvidia chips, The Information reports - Reuters | Reuters | https://news.google.com/rss/articles/CBMi2AFBVV95cUxPX0pMdFpwUWhaRHhFM1pvcndCTDdIX1NOQUVwV2JIX0xIcXByV3Z4UWQyblZRVWl5elZ0TkYxV3BXUEluN0llM0VnUDJvVmN4X19pcXJVX0tSNDdEUWdaNGFFVVQ3N01VaWJHQ1FXVEdVZTJJcDFvZlJ0QmE0b2JpeGM4RDdBMDh4YmNxRkhILVJDRGktQzRPdGNsV2VxWHBjZWt0Q3hRN2FwZWlhcDhMcUZ0LUJsS1FoWGVQUG1PVWp4cEpCcEtVdUJVRVQ4cjZxVUxjM1lDWFM?oc=5 | 2026-10-01T06:20:24Z | 선별·판정자 Claude 는 Anthropic 모델이고 이 기업은 Anthropic 투자자(2025-11 발표)다 (긴장 #4·#11) |
| SRC-NEWS-nvidia-20260929-8d3c9877 | Lawmakers plan to cut off China from AI chips. Nvidia, AMD want Trump to intervene. - Politico | Politico | https://news.google.com/rss/articles/CBMiiAFBVV95cUxPTXdheVlVR0FPX2tsOThwNUNleXVHTUNza3F0bnpBLWE5OVdEOE9sVmpIM3Vac1IxTUVoMXdRUmxXQU1zaXZyX2pQTUc2YWsyYlQ2UGIxX0tMSmFQSkFhakU2a0RkVmNnZkg2cGFUX2FtUUhoMEh6VDZ3ZkVBYUZabEpad3pYcHNk?oc=5 | 2026-10-01T06:20:24Z | 선별·판정자 Claude 는 Anthropic 모델이고 이 기업은 Anthropic 투자자(2025-11 발표)다 (긴장 #4·#11) |
| SRC-NEWS-openai-20260929-f0a15dfe | OpenAI Targets $30 Billion in Funding at $1.4 Trillion Value - Bloomberg.com | Bloomberg.com | https://news.google.com/rss/articles/CBMiswFBVV95cUxObmVYZUMtNFhXTXNoLXlfeUxuRUV2dGlqQTBqYjU3ZU9nTGJ1Vm5zSmNsSkJvWjRWanhmZzdPa1BTMDFKSmhKN1VvR3VFVDA4eEozekNGanFiUi0xWV9lOWpoWnBjb1lBVk5CY19NN3lfX2N6by11blZUc0JTWkxoLUpkQkdHVG1lQ1VGQjJ4WkZvcHhSaElwVFdjZTZMOWxWdHlELVBSa2h1d2NBRWE2ZEtVUQ?oc=5 | 2026-10-01T06:20:32Z | 선별·판정자 Claude 는 Anthropic 모델이고 이 기업은 직접 경쟁사다 (긴장 #4·#11) |
| SRC-NEWS-openai-20260929-f6ef918f | Sam Altman says OpenAI will delay its IPO until it overcomes safety concerns - Financial Times | Financial Times | https://news.google.com/rss/articles/CBMihAFBVV95cUxQaUViY1R6MFNqS1dEYnRjVTVELVRjdENjUFpUOEdPazJZTU4yNWt1TjlCOFBndjJFUFdWQTMwMkJQUF9pb2dnWTBSdU5aOFRsandmbUI1UWJ2eHdaMkxtZGw5NkgyUzFGWkl4aHB4UjFRMkRVSXZZUlA5TTVKWkhPQzd3VWk?oc=5 | 2026-10-01T06:20:32Z | 선별·판정자 Claude 는 Anthropic 모델이고 이 기업은 직접 경쟁사다 (긴장 #4·#11) |
| SRC-NEWS-oracle-20260930-9afa8fba | Oracle shares slip on unconfirmed report of delays at Wisconsin AI mega-campus - Investing.com | Investing.com | https://news.google.com/rss/articles/CBMizwFBVV95cUxPOHF2ODgycnRCSEdoVmg0MFN2bUZRemJlUU5POTgwN3ZWLTMzSF9nVW93ZVRPcktjcFdRWnFmUnhXbW1DNWl0Y0tRdG1tM1pqR3pOeFVGQ3docFZXZk1xVEw4TXllRTZETzd0eEJoQU9TZjRGZ2NpU2VIUnpnYk9JdUJXSml6ajEyS2QzN2xDdjMwN0VJS1FHdlBvRVc3WU0wUUMzYVNlU29hb1hlUTc3dEVRNjhRSElGLWR2bGRuWjhOTUpRcUh4bFh5TEhFQTQ?oc=5 | 2026-10-01T06:20:30Z | — |
| SRC-NEWS-palantir-20260928-1a4e9e5d | Labour conference blocks motion to cancel Palantir contract over Israeli army links - Middle East Eye | Middle East Eye | https://news.google.com/rss/articles/CBMitgFBVV95cUxQU2lUUlhqZng3WXVBd1JvMFJ1NTB1NTdyZk5vcUpkZTE5ak1pcFFPYk1wcHhvOTZuX0JRNWRvZ2dWdTJ4N0g5Um9acjNXZzJCb201d3FoTHNNdllyRW9tODFEbHRlUlZ3eWhKSHhDLXotbXFvSmNvQ0JkMWxkNHo4QWhQVWF5ZkpyNnFid0FaZFFpT0h2UnQ3SzNsbmt4cng2TDdNVlE3VmNzMUNuSkhrNWNRZUFZdw?oc=5 | 2026-10-01T06:20:25Z | — |
| SRC-NEWS-spacex-xai-20260925-c55fd45d | SpaceX (SPCX.US) to Invest $100 Billion in Starship Super Heavy Launch Site, Targeting Deployment of One Million Space Data Center Satellites - Moomoo | Moomoo | https://news.google.com/rss/articles/CBMiowFBVV95cUxONWVZTFZtU3FkbzFZb1pZV3RmTkpFTFZwQ0gtQUprRmJ1VFQ5ZW1oSXBvVFlkeE1wLTZfUkFJVGRQV1lNZktXN0J3UDRVRzg2R09xTlo4bXhWazJpell2LWl3am9QeEFneThzNG9ZY1k4TTlJcFg2Q1FJTVdtWGdFWUFzN19PSm5XNi1rT016ZkRPUWY1d1Y5SVAyQ0tzOVVaVEtF?oc=5 | 2026-10-01T06:20:27Z | 선별·판정자 Claude 는 Anthropic 모델이고 이 기업은 Anthropic 경쟁사(xAI)이자 컴퓨트 공급자다 (긴장 #4·#11) |
| SRC-NEWS-spacex-xai-20260925-e95e4ee1 | SPCX Stock Climbs Premarket As Musk Teases 3 Nvidia Chip Waves — Google Books SpaceX Ride For Orbital AI Test - Yahoo Finance | Yahoo Finance | https://news.google.com/rss/articles/CBMinAFBVV95cUxOaEtRUXdJb1VVcVdjUEF3ZWJtd19mRlBieXZtcndYTUM4akR6SndPMTNueXVXdlZiSkFieWpQSmMzU01tMHBJVlRDWWpqaHoyRGVwdzlKamNjTElFdVN2YXlKQlJCbHFiZDZmNWYyVmlCd1Z0dEFHSlFWbVdGbHEzOFJOTUdZMVpYcVlfWW9YRC1PZFZFeFRYdkNlM2U?oc=5 | 2026-10-01T06:20:27Z | 선별·판정자 Claude 는 Anthropic 모델이고 이 기업은 Anthropic 경쟁사(xAI)이자 컴퓨트 공급자다 (긴장 #4·#11) |
| SRC-NEWS-spacex-xai-20260930-61e3d191 | SpaceXAI considers four-tier pricing model for Grok and X users - Bloomberg - Yahoo Finance | Yahoo Finance | https://news.google.com/rss/articles/CBMiogFBVV95cUxNYTNfNEJOVkRpSURLWXJjdlo0NWZzYUNOa2M0QVZaTmlFR3VVU25TQ21nNEFKSVpzZGhfaUZZRVdsMWJuUjJRWUxCNnJNejloWnNiTEFOaWJMWnVodXY2U1M2d1o0S3N3VE1MNloxOVhjOTZCM3hsZEpFV0tveU05c192N29OTng0U0JHNHRnOFItOHZBbjRpU0JDVEhkdWxyNnc?oc=5 | 2026-10-01T06:20:27Z | 선별·판정자 Claude 는 Anthropic 모델이고 이 기업은 Anthropic 경쟁사(xAI)이자 컴퓨트 공급자다 (긴장 #4·#11) |
| SRC-NEWS-tesla-20260917-7f2fe1d1 | U.S. Stock Market Movement \| Tesla (TSLA.US) Rises Over 4% as Optimus Robot Secures 5,000-Unit Order - Moomoo | Moomoo | https://news.google.com/rss/articles/CBMimwFBVV95cUxNbC1fWHItVElDUnFLR3psdUR1cmxDRFFqMlBOSDFtWEp6UkU4ZkQ0S3JfN1JtdWlmSTF3Rll5eWh6elZHU3BwOFZ6MWNjWVhTYmY2Rm5PY2lBb25kSGJxbE5JSGhtd0NqVEpOQzUyVUlhQzZleVNoVEJxYVhwYmUxYk1lQ2lOVE9tbDRxQlNLbUVfWnhibVdpbFhXcw?oc=5 | 2026-10-01T06:20:28Z | — |
| SRC-NEWS-tesla-20260929-0ff6ba75 | Germany Confirms December EU Vote on Tesla FSD Approval - Not a Tesla App | Not a Tesla App | https://news.google.com/rss/articles/CBMiugFBVV95cUxNd3BydUx0T25xTE5KZnlsMVlacDZBUi1WLUcyNGNXMVdXeHRCXzl2bml1N1ZZdXdzNEk2R0U2SWRzSU5JVERZZkxDR1Q3SzliM1NvV29SRWdyQXFBUmt4MGpaY3VMaDdGZHdWUWdRUTRKNnFOcjBGSnRWOVlFMTVBa2d6c01RaHdsQ0xwNkNQQVdPUVRRanNDYi1STjZPclFZOV9PWlNoTnlOSjRZUHZIVC1xTTl6TEhGNlE?oc=5 | 2026-10-01T06:20:28Z | — |
| SRC-NEWS-tesla-20260929-7296a9d2 | Tesla receives approval to roll out self-driving software in Croatia - Reuters | Reuters | https://news.google.com/rss/articles/CBMixwFBVV95cUxNblN1RjdSMFdsX0t4a2sxLVV2VHNqeEpfY01LLURydGdacDRBNm0xSWZVYVpBcHFNTUJKU08wclRmMDFEdzRrVUtkNG13UXpVeUpDNnpHZnlJdEZFZ0plU3FIYUJPaFdUcEFFNGJQcjdRM05JZWVwMDc0VFVROEFXWWU5V0VTYzk1QjRQMVdrYmZhVkFBejJYU2p1SlFGUEtqUVhEcXhKVHFCM1FoLTdpdWZUUGM1cjM2LTMyMkRTZ0QzRTdMWFVV?oc=5 | 2026-10-01T06:20:28Z | — |
| SRC-NEWS-tsmc-20260930-1272c9c8 | TSMC evaluates potential Texas investment, sources say - Reuters | Reuters | https://news.google.com/rss/articles/CBMirAFBVV95cUxQbk5sR25ad2FWc2RmSWZua1F3Mi1OR1NtTGx5bi1lQ1I0MHlmSHNyUXRGNUd5WmtOVEFMazFUY0FnM0tHdG8zbUF4QjlsaUNJWHhaZ2RXaWtUZHZhN0QteXRiNFNzb3pWcjA0Ty14cFJPenZhV0xnWktra01NaTNYa2s0Q0pEY0FxS20wV0lleWYzWGstYllNc1c3MFFxLXY1X3F4YjI5LXBhbG1J?oc=5 | 2026-10-01T06:20:18Z | — |
| SRC-NEWS-tsmc-20261001-4bcd7e85 | Key facts: TSMC (2330) $265B U.S. investment; $60–$64B capex outlook; Q3 results Oct. 15 - TradingView | TradingView | https://news.google.com/rss/articles/CBMi1wFBVV95cUxQR1JwaUVhWjdja0lqQ3pXY1otTHZjTkZlYWVSMkphX0lpaG0xdG80TEQwTXFvSXZwaFF4YUpGaVVNVm9seWRTWlhwS0hDb0k4WGRsc245QWxRdDQ2R0tzMERwZUgwS1k4bDBuUXJCWnM0X0E0WmZuVVR4dmZXQk9MU2RRaEVjc2xyUlVJUUR3c09EdW5sX2RHcU45aFJodTU4cGhVbEpoRkJ4SHBLQUotRFZybGhnNzVTZGNsUjN1WlpWTzhaWUQtRGpWZVF2QVR6bHFkWHZWbw?oc=5 | 2026-10-01T06:20:18Z | — |

## 미결 항목

| 기업 | 항목 | 상태 | 내용 |
| --- | --- | --- | --- |
| spacex-xai | ttm_per | not_applicable | 적자 |
| spacex-xai | nonop_share | incompatible_basis | FIX-53 3단계. 세전이익 음수 — 부호 규약 미정이라 산출 안 함. P4 강등은 short_history 한 칸으로 이미 걸려 점수 불변. |
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
| amazon | contracted_revenue | not_disclosed | [OBS-REG-25 대체됨 → amazon.contracted_revenue.obsreg25] 규칙 v1.5 ⑨ 게이트 4 적용표 |
| alibaba | offbalance_B | not_disclosed | [OBS-REG-25 대체됨 → alibaba.offbalance_B.obsreg25] 규칙 v1.5 ⑨ 게이트 4 적용표 |
| alibaba | contracted_revenue | not_disclosed | [OBS-REG-25 대체됨 → alibaba.contracted_revenue.obsreg25] 규칙 v1.5 ⑨ 게이트 4 적용표 |
| spacex-xai | offbalance_B | not_disclosed | [OBS-REG-25 대체됨 → spacex-xai.offbalance_B.obsreg25] 규칙 v1.5 ⑨ 게이트 4 적용표 |
| anthropic | offbalance_B | incompatible_basis | 규칙 v1.5 ⑨ 게이트 4 적용표 |
| anthropic | contracted_revenue | not_disclosed | 규칙 v1.5 ⑨ 게이트 4 적용표 |
| openai | offbalance_B | incompatible_basis | 규칙 v1.5 ⑨ 게이트 4 적용표 |
| openai | contracted_revenue | not_disclosed | 규칙 v1.5 ⑨ 게이트 4 적용표 |
| alibaba | contracted_revenue | not_disclosed | OBS-REG-25 · [FIX-53 3단계] **확인된 미공시.** 20-F 가 두 갈래(1년 이하 계약 · right-to-invoice 계약) 면제를 선언하고, 문서 전문 검 |
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
| apple | lease_liabilities | not_disclosed | NETCASH-37. net_cash 실측이 막힌 이유를 여기 남긴다 — [FIX-54 2단계] unverified(표준 태그 결측, 10-Q 전문 미검색) |
| palantir | lease_liabilities | not_disclosed | NETCASH-37. net_cash 실측이 막힌 이유를 여기 남긴다 — [FIX-54 2단계] unverified(표준 태그 결측, 10-Q 전문 미검색) |
| alibaba | undrawn_credit | incompatible_basis | FIX-53 2단계. 근사치라 런웨이 분자에서 뺀다. 결론 민감도는 basis.sensitivity. |
| apple | undrawn_credit | not_disclosed | FIX-54 1단계 S2 전수 — 확정 미인출 여신 미확인(우리가 확인하지 않았다). |
| microsoft | undrawn_credit | not_disclosed | FIX-54 1단계 S2 전수 — 확정 미인출 여신 미확인(우리가 확인하지 않았다). |
| nvidia | undrawn_credit | not_disclosed | FIX-54 1단계 S2 전수 — 확정 미인출 여신 미확인(우리가 확인하지 않았다). |
| alphabet | undrawn_credit | not_disclosed | FIX-54 1단계 S2 전수 — 확정 미인출 여신 미확인(우리가 확인하지 않았다). |
| meta | undrawn_credit | not_disclosed | FIX-54 1단계 S2 전수 — 확정 미인출 여신 미확인(우리가 확인하지 않았다). |
| oracle | undrawn_credit | not_disclosed | FIX-54 1단계 S2 전수 — 확정 미인출 여신 미확인(우리가 확인하지 않았다). |
| palantir | undrawn_credit | not_disclosed | FIX-54 1단계 S2 전수 — 확정 미인출 여신 미확인(우리가 확인하지 않았다). |
| tesla | undrawn_credit | not_disclosed | FIX-54 1단계 S2 전수 — 확정 미인출 여신 미확인(우리가 확인하지 않았다). \| [FIX-55 2단계 대체됨 → tesla.undrawn_credit.fix55] 광역 태 |
| tsmc | undrawn_credit | not_disclosed | FIX-54 1단계 S2 전수 — 확정 미인출 여신 미확인(우리가 확인하지 않았다). |
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
- 미결 규칙 결정: C-05, C-06, C-16 (실행 선택: C-05=apply, C-06=proposed_v15_boundaries, C-16=downgrade, C-12=p2_with_capped_promotion, C-20=defer_to_private_g2, C-03=paths_with_generation_gap_5, C-11=block_carryover, C-13=reject_proxy, C-24=compute_p2_when_inputs_exist, C-28=optional_parameters_for_all_listed_tracks, C-29=c20_private_route_first)
