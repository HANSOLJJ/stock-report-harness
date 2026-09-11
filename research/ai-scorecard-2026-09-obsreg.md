---
slug: ai-scorecard-2026-09-obsreg
report_type: ai_scorecard
plan_source: plan/ai-scorecard-2026-09-obsreg.md
run_id: ai-scorecard-2026-09-obsreg
as_of: 2026-09-02
rule_version: v1.7
observations_hash: 9b84660fc5c4b1ea3b20445e28e8de992f32fa4018754f07c538b7325cedc475
judgments_hash: 5dc79ac34c6172670ab8a0480156d34bf15a40b599b5198c2b101e641f76bec6
created_at: 2026-09-11
---
# 리서치 — AI 기업 9-factor 채점표 — OFFB 실측 관측 반영(v1.7)

실행 `ai-scorecard-2026-09-obsreg` 의 원자료·판단 입력·출처를 정리한다. 관측 236건, 판단 114건.

## 원자료

### Alphabet / Google

| 지표 | 값 | 상태 | 종류 | 출처 | 원문 | 비고 |
| --- | --- | --- | --- | --- | --- | --- |
| capex_ttm | $132.4B | legacy_unverified | actual | SRC-v15-html | $132.4B |  |
| cash | $242.5B | legacy_unverified | actual | SRC-v15-html | $242.5B |  |
| credit_rating | AA급 | legacy_unverified | text | SRC-v15-html | AA급 | 별표 J 교차검증 전용 — 점수 입력 아님 |
| debt_ebitda | 0.7 | legacy_unverified | actual | SRC-v15-html | 0.68 |  |
| fcf_ttm | $53.3B | legacy_unverified | actual | SRC-v15-html | +$53.3B |  |
| market_cap | $4.12T | legacy_unverified | actual | SRC-v15-html | $4.12T |  |
| net_borrowing_ttm | $70.1B | legacy_unverified | actual | SRC-v15-html | +$70.1B | 차환 제외 순증 |
| net_cash | $121.7B | legacy_unverified | actual | SRC-v15-html | +$121.7B |  |
| nonop_share | 51% | legacy_unverified | actual | SRC-v15-html | 51% ⚠️ |  |
| ntm_per | 25.3 | legacy_unverified | estimate | SRC-v15-html | 25.3 |  |
| offbalance_note | 총 약정 $707B | legacy_unverified | text | SRC-v15-html | 총 약정 $707B | 부외 약정 원문(A/B/C 분류 전) |
| price | 337.12 | legacy_unverified | actual | SRC-v15-html | $337.12 |  |
| ps_ratio | 9.3 | legacy_unverified | actual | SRC-v15-html | 9.3 |  |
| quarter_note | Q2 (7/22) \| $119.8B (+24%) · GCP $24.8B(+82%) 영업이익 $8.8B \| 조정 $2.85 (컨센 $2.89 하회) \| Q2 사상 첫 마이너스 · TTM +$53B | legacy_unverified | text | SRC-v15-html |  | 최근 분기 실적 원문(③⑨ 참고). TTM 대체 금지 |
| runway_years | — | not_applicable | derived | SRC-v15-html | ∞ | TTM FCF 흑자라 런웨이 산식 적용 대상 아님(원문 ∞) |
| ttm_per | 16.9 | legacy_unverified | actual | SRC-v15-html | 16.9 |  |

### Amazon / AWS

| 지표 | 값 | 상태 | 종류 | 출처 | 원문 | 비고 |
| --- | --- | --- | --- | --- | --- | --- |
| capex_ttm | $173.0B | legacy_unverified | actual | SRC-v15-html | $173.0B |  |
| cash | $123.0B | legacy_unverified | actual | SRC-v15-html | $123.0B |  |
| contracted_revenue | $496.0B | verified | actual | SRC-SEC-AMZN-10Q-2026Q2 | RPO approximately $496 billion (2026-06-30) | OBS-REG-25. 승계 관측 amazon.contracted_revenue.v15(parse_failed)를 대체한다. **parse_fai |
| contracted_revenue | — | parse_failed | actual | SRC-v15-rule | AWS 백로그(수백 $B급) — 숫자 미공시 | [OBS-REG-25 대체됨 → amazon.contracted_revenue.obsreg25] 규칙 v1.5 ⑨ 게이트 4 적용표 |
| credit_rating | AA급 | legacy_unverified | text | SRC-v15-html | AA급 | 별표 J 교차검증 전용 — 점수 입력 아님 |
| debt_ebitda | 1.4 | legacy_unverified | actual | SRC-v15-html | 1.35 |  |
| fcf_ttm | -$11.6B | legacy_unverified | actual | SRC-v15-html | -$11.6B |  |
| market_cap | $2.75T | legacy_unverified | actual | SRC-v15-html | $2.75T |  |
| net_borrowing_ttm | $75.2B | legacy_unverified | actual | SRC-v15-html | +$75.2B | 차환 제외 순증 |
| net_cash | -$128.7B | legacy_unverified | actual | SRC-v15-html | -$128.7B |  |
| nonop_share | 46% | legacy_unverified | actual | SRC-v15-html | 46% ⚠️ |  |
| ntm_per | 27.5 | legacy_unverified | estimate | SRC-v15-html | 27.5 |  |
| offbalance_B | $267.3B | verified | derived | SRC-SEC-AMZN-10Q-2026Q2 | 미개시 리스 $137,214M + 무조건 구매약정 $130,065M = $267,279M (2026-06-30) | OBS-REG-25. 승계 관측 amazon.offbalance_B.v15($106B, 출처 불명)를 대체한다. **106,000 은 2026Q |
| offbalance_B | $106.0B | legacy_unverified | actual | SRC-v15-rule | 미개시 리스 $106B(3/31) | [OBS-REG-25 대체됨 → amazon.offbalance_B.obsreg25] 규칙 v1.5 ⑨ 게이트 4 적용표 |
| offbalance_note | 미개시 리스 $106B | legacy_unverified | text | SRC-v15-html | 미개시 리스 $106B | 부외 약정 원문(A/B/C 분류 전) |
| price | 254.98 | legacy_unverified | actual | SRC-v15-html | $254.98 |  |
| ps_ratio | 3.6 | legacy_unverified | actual | SRC-v15-html | 3.6 |  |
| quarter_note | Q2 (7/30) \| $200.61B (+20%) · AWS $42.2B(+37%) 18분기 최고 \| $5.75 ⚠️ 평가익 포함 \| TTM -$11.6B 실측 확정 | legacy_unverified | text | SRC-v15-html |  | 최근 분기 실적 원문(③⑨ 참고). TTM 대체 금지 |
| runway_years | 10.6 | legacy_unverified | derived | SRC-v15-html | 10.6년 | 원본 계산값(현금 ÷ 연 소진) |
| ttm_per | 20.5 | legacy_unverified | actual | SRC-v15-html | 20.5 |  |

### Meta

| 지표 | 값 | 상태 | 종류 | 출처 | 원문 | 비고 |
| --- | --- | --- | --- | --- | --- | --- |
| capex_ttm | $89.3B | legacy_unverified | actual | SRC-v15-html | $89.3B |  |
| cash | $90.3B | legacy_unverified | actual | SRC-v15-html | $90.3B |  |
| credit_rating | AA- | legacy_unverified | text | SRC-v15-html | AA- | 별표 J 교차검증 전용 — 점수 입력 아님 |
| debt_ebitda | 1.0 | legacy_unverified | actual | SRC-v15-html | 0.99 |  |
| fcf_ttm | $41.0B | legacy_unverified | actual | SRC-v15-html | +$41.0B |  |
| market_cap | $1.51T | legacy_unverified | actual | SRC-v15-html | $1.51T |  |
| net_borrowing_ttm | $51.7B | legacy_unverified | actual | SRC-v15-html | +$51.7B | 차환 제외 순증 |
| net_cash | -$22.1B | legacy_unverified | actual | SRC-v15-html | -$22.1B |  |
| nonop_share | 1% | legacy_unverified | actual | SRC-v15-html | 1% |  |
| ntm_per | 17.9 | legacy_unverified | estimate | SRC-v15-html | 17.9 |  |
| offbalance_note | 리스 $279B + 계약 $349B = $628B | legacy_unverified | text | SRC-v15-html | 리스 $279B + 계약 $349B = $628B | 부외 약정 원문(A/B/C 분류 전) |
| price | 592.85 | legacy_unverified | actual | SRC-v15-html | $592.85 |  |
| ps_ratio | 6.6 | legacy_unverified | actual | SRC-v15-html | 6.6 |  |
| quarter_note | Q2 (7/29) \| $60.80B (+28%) \| $6.18 (컨센 $7.14 하회) \| Q2 +$0.78B (-91%) · TTM +$41B | legacy_unverified | text | SRC-v15-html |  | 최근 분기 실적 원문(③⑨ 참고). TTM 대체 금지 |
| runway_years | — | not_applicable | derived | SRC-v15-html | ∞ | TTM FCF 흑자라 런웨이 산식 적용 대상 아님(원문 ∞) |
| ttm_per | 21.8 | legacy_unverified | actual | SRC-v15-html | 21.8 |  |

### Microsoft

| 지표 | 값 | 상태 | 종류 | 출처 | 원문 | 비고 |
| --- | --- | --- | --- | --- | --- | --- |
| capex_ttm | $116.0B | legacy_unverified | actual | SRC-v15-html | $116.0B |  |
| cash | $76.8B | legacy_unverified | actual | SRC-v15-html | $76.8B |  |
| credit_rating | AAA급 | legacy_unverified | text | SRC-v15-html | AAA급 | 별표 J 교차검증 전용 — 점수 입력 아님 |
| debt_ebitda | 0.6 | legacy_unverified | actual | SRC-v15-html | 0.64 |  |
| fcf_ttm | $67.0B | legacy_unverified | actual | SRC-v15-html | +$67.0B |  |
| market_cap | $3.69T | legacy_unverified | actual | SRC-v15-html | $3.69T |  |
| net_borrowing_ttm | -$3.0B | legacy_unverified | actual | SRC-v15-html | -$3.0B | 차환 제외 순증 |
| net_cash | -$52.0B | legacy_unverified | actual | SRC-v15-html | -$52.0B |  |
| nonop_share | 6% | legacy_unverified | actual | SRC-v15-html | 6% |  |
| ntm_per | 25.4 | legacy_unverified | estimate | SRC-v15-html | 25.4 |  |
| offbalance_note | 미분리 (QTS $3.9B만 확인) | legacy_unverified | text | SRC-v15-html | 미분리 (QTS $3.9B만 확인) | 부외 약정 원문(A/B/C 분류 전) |
| price | 496.82 | legacy_unverified | actual | SRC-v15-html | $496.82 |  |
| ps_ratio | 11.1 | legacy_unverified | actual | SRC-v15-html | 11.1 |  |
| quarter_note | Q4 FY26 (7/29) \| $90B (+18%) · 🆕 Azure $29.42B(+42%) 최초 달러 공시 \| non-GAAP $4.74 (컨센 $4.24 상회) \| TTM +$67B · capex 감축 | legacy_unverified | text | SRC-v15-html |  | 최근 분기 실적 원문(③⑨ 참고). TTM 대체 금지 |
| runway_years | — | not_applicable | derived | SRC-v15-html | ∞ | TTM FCF 흑자라 런웨이 산식 적용 대상 아님(원문 ∞) |
| ttm_per | 27.9 | legacy_unverified | actual | SRC-v15-html | 27.9 |  |

### TSMC

| 지표 | 값 | 상태 | 종류 | 출처 | 원문 | 비고 |
| --- | --- | --- | --- | --- | --- | --- |
| capex_ttm | $46.9B | legacy_unverified | actual | SRC-v15-html | $46.9B |  |
| cash | $110.6B | legacy_unverified | actual | SRC-v15-html | $110.6B |  |
| credit_rating | AA-급 | legacy_unverified | text | SRC-v15-html | AA-급 | 별표 J 교차검증 전용 — 점수 입력 아님 |
| debt_ebitda | 0.3 | legacy_unverified | actual | SRC-v15-html | 0.34 |  |
| fcf_ttm | $36.0B | legacy_unverified | actual | SRC-v15-html | +$36.0B |  |
| market_cap | $2.15T | legacy_unverified | actual | SRC-v15-html | $2.15T ✱ |  |
| net_borrowing_ttm | $100M | legacy_unverified | actual | SRC-v15-html | +$0.1B | 차환 제외 순증 |
| net_cash | $77.0B | legacy_unverified | actual | SRC-v15-html | +$77.0B |  |
| nonop_share | 7% | legacy_unverified | actual | SRC-v15-html | 7% |  |
| ntm_per | 19.4 | legacy_unverified | estimate | SRC-v15-html | 19.4 ✱ |  |
| offbalance_note | 미확인 | legacy_unverified | text | SRC-v15-html | 미확인 | 부외 약정 원문(A/B/C 분류 전) |
| price | 415.5 | legacy_unverified | actual | SRC-v15-html | $415.50 |  |
| ps_ratio | 15.4 | legacy_unverified | actual | SRC-v15-html | 15.4 |  |
| quarter_note | Q2 (7/16) \| $40.2B (+36%) · HPC 66% \| GM 67.7% / OpM 60.3% 역대 최고 · 2026 가이던스 +30%→+40% 이상 \| TTM +$36B · capex $60~64B | legacy_unverified | text | SRC-v15-html |  | 최근 분기 실적 원문(③⑨ 참고). TTM 대체 금지 |
| runway_years | — | not_applicable | derived | SRC-v15-html | ∞ | TTM FCF 흑자라 런웨이 산식 적용 대상 아님(원문 ∞) |
| ttm_per | 30.9 | legacy_unverified | actual | SRC-v15-html | 30.9 |  |

### Alibaba

| 지표 | 값 | 상태 | 종류 | 출처 | 원문 | 비고 |
| --- | --- | --- | --- | --- | --- | --- |
| capex_ttm | $23.1B | legacy_unverified | actual | SRC-v15-html | $23.1B |  |
| cash | $56.8B | legacy_unverified | actual | SRC-v15-html | $56.8B |  |
| contracted_revenue | — | not_disclosed | actual | SRC-SEC-BABA-20F-FY2026 | 미공시 — ASC 606 실무적 간편법 선언 | OBS-REG-25. **회사가 공시하지 않겠다고 선언한 회계정책이다.** '이 문서에 없다' 와 다르다 — 찾아도 없을 것이 선언돼 있다. C |
| contracted_revenue | — | not_disclosed | actual | SRC-v15-rule | — | [OBS-REG-25 대체됨 → alibaba.contracted_revenue.obsreg25] 규칙 v1.5 ⑨ 게이트 4 적용표 |
| credit_rating | A급 | legacy_unverified | text | SRC-v15-html | A급 | 별표 J 교차검증 전용 — 점수 입력 아님 |
| debt_ebitda | 2.7 | legacy_unverified | actual | SRC-v15-html | 2.68 |  |
| fcf_ttm | -$11.4B | legacy_unverified | actual | SRC-v15-html | -$11.4B |  |
| market_cap | $270.0B | legacy_unverified | actual | SRC-v15-html | $270B |  |
| net_borrowing_ttm | $7.5B | legacy_unverified | actual | SRC-v15-html | +$7.5B | 차환 제외 순증 |
| net_cash | $17.5B | legacy_unverified | actual | SRC-v15-html | +$17.5B |  |
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
| runway_years | 5.0 | legacy_unverified | derived | SRC-v15-html | 5.0년 | 원본 계산값(현금 ÷ 연 소진) |
| ttm_per | 25.8 | legacy_unverified | actual | SRC-v15-html | 25.8 |  |

### Anthropic

| 지표 | 값 | 상태 | 종류 | 출처 | 원문 | 비고 |
| --- | --- | --- | --- | --- | --- | --- |
| arr | $65.0B | legacy_unverified | run_rate | SRC-v15-rule | ARR $65B(7월 런레이트) | 규칙 v1.5 ⑥ 비상장 절 |
| cash | — | not_disclosed | actual | SRC-v15-html | 미공시 |  |
| contracted_revenue | $65.0B | incompatible_basis | actual | SRC-v15-rule | ARR $65B — 계약 수입 아님(C-07) | 규칙 v1.5 ⑨ 게이트 4 적용표 |
| credit_rating | 비상장 | legacy_unverified | text | SRC-v15-html | 비상장 | 별표 J 교차검증 전용 — 점수 입력 아님 |
| cumulative_raised | $125.0B | legacy_unverified | actual | SRC-v15-rule | 약 $125B(2021년~) | 규칙 v1.5 ⑥ 비상장 절 |
| debt_ebitda | — | not_disclosed | actual | SRC-v15-html | — |  |
| fcf_ttm | — | not_disclosed | actual | SRC-v15-html | 미공시 | 비상장 FCF 미공시 |
| net_cash | — | not_disclosed | actual | SRC-v15-html | — |  |
| offbalance_B | $300.0B | incompatible_basis | actual | SRC-v15-rule | 컴퓨트 약정 $300B(연 ~$50B) — 기간·범위가 RPO 와 다름(C-07) | 규칙 v1.5 ⑨ 게이트 4 적용표 |
| offbalance_note | 컴퓨트 $300B | legacy_unverified | text | SRC-v15-html | 컴퓨트 $300B | 부외 약정 원문(A/B/C 분류 전) |
| post_money_valuation | $965.0B | legacy_unverified | actual | SRC-v15-rule | $965B | 규칙 v1.5 ⑥ 비상장 절 |
| quarter_note | Q2 \| $10.9B · 런레이트 $65B(7월) \| 첫 영업흑자 $559M \| 외부 조달 의존 · FCF 미공시 | legacy_unverified | text | SRC-v15-html |  | 최근 분기 실적 원문(③⑨ 참고). TTM 대체 금지 |
| runway_years | — | not_disclosed | derived | SRC-v15-html | 판정 불가 | FCF 미공시로 소진율을 만들 수 없음(원문 판정 불가) |

### Apple

| 지표 | 값 | 상태 | 종류 | 출처 | 원문 | 비고 |
| --- | --- | --- | --- | --- | --- | --- |
| capex_ttm | $10.0B | legacy_unverified | actual | SRC-v15-html | $10.0B |  |
| cash | $146.5B | legacy_unverified | actual | SRC-v15-html | $146.5B |  |
| credit_rating | AA급 | legacy_unverified | text | SRC-v15-html | AA급 | 별표 J 교차검증 전용 — 점수 입력 아님 |
| debt_ebitda | 0.5 | legacy_unverified | actual | SRC-v15-html | 0.45 |  |
| fcf_ttm | $136.7B | legacy_unverified | actual | SRC-v15-html | +$136.7B |  |
| market_cap | $4.74T | legacy_unverified | actual | SRC-v15-html | $4.74T |  |
| net_borrowing_ttm | -$17.3B | legacy_unverified | actual | SRC-v15-html | -$17.3B | 차환 제외 순증 |
| net_cash | $62.2B | legacy_unverified | actual | SRC-v15-html | +$62.2B |  |
| nonop_share | 1% | legacy_unverified | actual | SRC-v15-html | 1% |  |
| ntm_per | 35.5 | legacy_unverified | estimate | SRC-v15-html | 35.5 |  |
| offbalance_note | 미확인 | legacy_unverified | text | SRC-v15-html | 미확인 | 부외 약정 원문(A/B/C 분류 전) |
| price | 324.96 | legacy_unverified | actual | SRC-v15-html | $324.96 |  |
| ps_ratio | 10.2 | legacy_unverified | actual | SRC-v15-html | 10.2 |  |
| quarter_note | 6월 분기 (7/30) \| $109.4B (+16%) \| $2.02 상회 (Services 하회) \| TTM +$137B | legacy_unverified | text | SRC-v15-html |  | 최근 분기 실적 원문(③⑨ 참고). TTM 대체 금지 |
| runway_years | — | not_applicable | derived | SRC-v15-html | ∞ | TTM FCF 흑자라 런웨이 산식 적용 대상 아님(원문 ∞) |
| ttm_per | 37.3 | legacy_unverified | actual | SRC-v15-html | 37.3 |  |

### NVIDIA

| 지표 | 값 | 상태 | 종류 | 출처 | 원문 | 비고 |
| --- | --- | --- | --- | --- | --- | --- |
| capex_ttm | $7.4B | legacy_unverified | actual | SRC-v15-html | $7.4B |  |
| cash | $62.5B | legacy_unverified | actual | SRC-v15-html | $62.5B |  |
| credit_rating | AA~A급 | legacy_unverified | text | SRC-v15-html | AA~A급 | 별표 J 교차검증 전용 — 점수 입력 아님 |
| debt_ebitda | 0.2 | legacy_unverified | actual | SRC-v15-html | 0.19 |  |
| fcf_ttm | $127.0B | legacy_unverified | actual | SRC-v15-html | +$127.0B |  |
| market_cap | $5.42T | legacy_unverified | actual | SRC-v15-html | $5.42T |  |
| net_borrowing_ttm | $24.9B | legacy_unverified | actual | SRC-v15-html | +$24.9B | 차환 제외 순증 |
| net_cash | $23.6B | legacy_unverified | actual | SRC-v15-html | +$23.6B |  |
| nonop_share | 14% | legacy_unverified | actual | SRC-v15-html | 14% ᵃ |  |
| ntm_per | 18.0 | legacy_unverified | estimate | SRC-v15-html | 18.0 |  |
| offbalance_note | 보증 $105B + 잔존가치 25% + 백스톱 + $6.3B (우발·C종) | legacy_unverified | text | SRC-v15-html | 보증 $105B + 잔존가치 25% + 백스톱 + $6.3B (우발·C종) | 부외 약정 원문(A/B/C 분류 전) |
| price | 224.41 | legacy_unverified | actual | SRC-v15-html | $224.41 |  |
| ps_ratio | 17.9 | legacy_unverified | actual | SRC-v15-html | 17.9 |  |
| quarter_note | Q2 FY27 (8/26) \| $96.2B (+106%) · DC $89.0B (+117%) \| GAAP $2.46 / non-GAAP $2.22 · DC 컨센 $86.3B 상회 \| TTM +$127B · 환원 $26B | legacy_unverified | text | SRC-v15-html |  | 최근 분기 실적 원문(③⑨ 참고). TTM 대체 금지 |
| runway_years | — | not_applicable | derived | SRC-v15-html | ∞ | TTM FCF 흑자라 런웨이 산식 적용 대상 아님(원문 ∞) |
| ttm_per | 27.5 | legacy_unverified | actual | SRC-v15-html | 27.5 |  |

### Palantir

| 지표 | 값 | 상태 | 종류 | 출처 | 원문 | 비고 |
| --- | --- | --- | --- | --- | --- | --- |
| capex_ttm | $40M | legacy_unverified | actual | SRC-v15-html | $0.04B |  |
| cash | $9.4B | legacy_unverified | actual | SRC-v15-html | $9.4B |  |
| credit_rating | 무차입 | legacy_unverified | text | SRC-v15-html | 무차입 | 별표 J 교차검증 전용 — 점수 입력 아님 |
| debt_ebitda | 0.1 | legacy_unverified | actual | SRC-v15-html | 0.08 |  |
| fcf_ttm | $3.4B | legacy_unverified | actual | SRC-v15-html | +$3.4B |  |
| market_cap | $407.0B | legacy_unverified | actual | SRC-v15-html | $407B |  |
| net_borrowing_ttm | — | not_disclosed | actual | SRC-v15-html | 없음 | 차환 제외 순증 |
| net_cash | $9.2B | legacy_unverified | actual | SRC-v15-html | +$9.2B |  |
| nonop_share | 14% | legacy_unverified | actual | SRC-v15-html | 14% ᵇ |  |
| ntm_per | 89.0 | legacy_unverified | estimate | SRC-v15-html | 89.0 |  |
| offbalance_note | 없음 | legacy_unverified | text | SRC-v15-html | 없음 | 부외 약정 원문(A/B/C 분류 전) |
| price | 169.46 | legacy_unverified | actual | SRC-v15-html | $169.46 |  |
| ps_ratio | 66.2 | legacy_unverified | actual | SRC-v15-html | 66.2 |  |
| quarter_note | Q2 (8/3) \| $1.94B (+92.8%) · 4분기 연속 상회 \| $0.41 (컨센 $0.35 상회) \| TTM +$3.4B | legacy_unverified | text | SRC-v15-html |  | 최근 분기 실적 원문(③⑨ 참고). TTM 대체 금지 |
| runway_years | — | not_applicable | derived | SRC-v15-html | ∞ | TTM FCF 흑자라 런웨이 산식 적용 대상 아님(원문 ∞) |
| ttm_per | 144.9 | legacy_unverified | actual | SRC-v15-html | 144.9 |  |

### SpaceX + xAI

| 지표 | 값 | 상태 | 종류 | 출처 | 원문 | 비고 |
| --- | --- | --- | --- | --- | --- | --- |
| capex_ttm | $42.4B | legacy_unverified | actual | SRC-v15-html | $42.4B |  |
| cash | $100.0B | legacy_unverified | actual | SRC-v15-html | $100.0B |  |
| contracted_revenue | $47.5B | verified | actual | SRC-SEC-SPCX-10Q-2026Q2 | Backlog $47,461M (2026-06-30) | OBS-REG-25. 승계 관측 spacex-xai.contracted_revenue.v15($47.5B, legacy_unverified)를  |
| contracted_revenue | $47.5B | legacy_unverified | actual | SRC-v15-rule | 백로그 $47.5B | [OBS-REG-25 대체됨 → spacex-xai.contracted_revenue.obsreg25] 규칙 v1.5 ⑨ 게이트 4 적용표 |
| credit_rating | 무등급 | legacy_unverified | text | SRC-v15-html | 무등급 | 별표 J 교차검증 전용 — 점수 입력 아님 |
| debt_ebitda | 5.8 | legacy_unverified | actual | SRC-v15-html | 5.78 ⚠️ |  |
| fcf_ttm | -$32.5B | legacy_unverified | actual | SRC-v15-html | -$32.5B |  |
| market_cap | $1.91T | legacy_unverified | actual | SRC-v15-html | $1.91T |  |
| net_borrowing_ttm | $102.0B | legacy_unverified | actual | SRC-v15-html | +$102.0B | 차환 제외 순증 |
| net_cash | $60.3B | legacy_unverified | actual | SRC-v15-html | +$60.3B |  |
| nonop_share | — | not_disclosed | actual | SRC-v15-html | 적자 |  |
| ntm_per | 111.0 | legacy_unverified | estimate | SRC-v15-html | 111 |  |
| offbalance_B | $29.6B | verified | derived | SRC-SEC-SPCX-10Q-2026Q2 | 미개시 리스 $1,627M(2025-12-31) + 무조건 구매약정 $27,955M(2026-06-30) = $29,582M | OBS-REG-25. **기준일이 섞인 합계다.** 구성요소별 기준일·출처를 basis.components 에 남겼다. 관측을 둘로 쪼개지 않은 |
| offbalance_B | — | not_disclosed | actual | SRC-v15-rule | 미확인 | [OBS-REG-25 대체됨 → spacex-xai.offbalance_B.obsreg25] 규칙 v1.5 ⑨ 게이트 4 적용표 |
| offbalance_note | 미확인 | legacy_unverified | text | SRC-v15-html | 미확인 | 부외 약정 원문(A/B/C 분류 전) |
| operating_margin_ttm | -15% | legacy_unverified | actual | SRC-v15-html | -$0.09 (컨센 -$0.26 상회) · 영업적자 -14.9% | EARN 열의 영업적자율. 규칙 ⑨ 표는 -14.9% 를 TTM 손실률로 사용 |
| price | 140.71 | legacy_unverified | actual | SRC-v15-html | $140.71 |  |
| ps_ratio | 82.9 | legacy_unverified | actual | SRC-v15-html | 82.9 |  |
| quarter_note | Q2 (8/4) \| $7.8B (+92%) · Starlink 1,200만 · AI 세그먼트 $2.56B(+247%) \| -$0.09 (컨센 -$0.26 상회) · 영업적자 -14.9% \| TTM -$32.5B · 현금 $100B | legacy_unverified | text | SRC-v15-html |  | 최근 분기 실적 원문(③⑨ 참고). TTM 대체 금지 |
| runway_years | 3.1 | legacy_unverified | derived | SRC-v15-html | 3.1년 | 원본 계산값(현금 ÷ 연 소진) |
| ttm_per | — | not_disclosed | actual | SRC-v15-html | 적자 | 적자 |

### Tesla

| 지표 | 값 | 상태 | 종류 | 출처 | 원문 | 비고 |
| --- | --- | --- | --- | --- | --- | --- |
| capex_ttm | $12.9B | legacy_unverified | actual | SRC-v15-html | $12.9B |  |
| cash | $43.5B | legacy_unverified | actual | SRC-v15-html | $43.5B |  |
| credit_rating | 투자등급 | legacy_unverified | text | SRC-v15-html | 투자등급 | 별표 J 교차검증 전용 — 점수 입력 아님 |
| debt_ebitda | 1.3 | legacy_unverified | actual | SRC-v15-html | 1.27 |  |
| fcf_ttm | $5.8B | legacy_unverified | actual | SRC-v15-html | +$5.8B |  |
| market_cap | $1.41T | legacy_unverified | actual | SRC-v15-html | $1.41T |  |
| net_borrowing_ttm | $1.8B | legacy_unverified | actual | SRC-v15-html | +$1.8B | 차환 제외 순증 |
| net_cash | $27.4B | legacy_unverified | actual | SRC-v15-html | +$27.4B |  |
| nonop_share | 18% | legacy_unverified | actual | SRC-v15-html | 18% ᵇ |  |
| ntm_per | 187.5 | legacy_unverified | estimate | SRC-v15-html | 187.5 |  |
| offbalance_note | 미확인 | legacy_unverified | text | SRC-v15-html | 미확인 | 부외 약정 원문(A/B/C 분류 전) |
| price | 357.01 | legacy_unverified | actual | SRC-v15-html | $357.01 |  |
| ps_ratio | 13.6 | legacy_unverified | actual | SRC-v15-html | 13.6 |  |
| quarter_note | Q2 (7/22) \| $28.24B (+26%) \| $0.33 (컨센 $0.53 하회) · 영업흑자 마진 4% \| TTM +$5.8B | legacy_unverified | text | SRC-v15-html |  | 최근 분기 실적 원문(③⑨ 참고). TTM 대체 금지 |
| runway_years | — | not_applicable | derived | SRC-v15-html | ∞ | TTM FCF 흑자라 런웨이 산식 적용 대상 아님(원문 ∞) |
| ttm_per | 370.5 | legacy_unverified | actual | SRC-v15-html | 370.5 |  |

### Oracle

| 지표 | 값 | 상태 | 종류 | 출처 | 원문 | 비고 |
| --- | --- | --- | --- | --- | --- | --- |
| capex_ttm | $55.7B | legacy_unverified | actual | SRC-v15-html | $55.7B |  |
| cash | $31.9B | legacy_unverified | actual | SRC-v15-html | $31.9B |  |
| contracted_revenue | $638.0B | legacy_unverified | actual | SRC-v15-rule | RPO $638B | 규칙 v1.5 ⑨ 게이트 4 적용표 |
| credit_rating | BBB- ⚠️ | legacy_unverified | text | SRC-v15-html | BBB- ⚠️ | 별표 J 교차검증 전용 — 점수 입력 아님 |
| debt_ebitda | 5.0 | legacy_unverified | actual | SRC-v15-html | 5.03 ⚠️ |  |
| fcf_ttm | -$23.7B | legacy_unverified | actual | SRC-v15-html | -$23.7B |  |
| market_cap | $443.7B | legacy_unverified | actual | SRC-v15-html | $443.7B |  |
| net_borrowing_ttm | $40.2B | legacy_unverified | actual | SRC-v15-html | +$40.2B | 차환 제외 순증 |
| net_cash | -$135.5B | legacy_unverified | actual | SRC-v15-html | -$135.5B |  |
| nonop_share | -15% | legacy_unverified | actual | SRC-v15-html | -15% ᶜ |  |
| ntm_per | 19.1 | legacy_unverified | estimate | SRC-v15-html | 19.1 |  |
| offbalance_B | $250.0B | legacy_unverified | actual | SRC-v15-rule | 리스 $250B(15~20년) | 규칙 v1.5 ⑨ 게이트 4 적용표 |
| offbalance_note | 리스 $250B(15~20년) | legacy_unverified | text | SRC-v15-html | 리스 $250B(15~20년) | 부외 약정 원문(A/B/C 분류 전) |
| price | 154.04 | legacy_unverified | actual | SRC-v15-html | $154.04 |  |
| ps_ratio | 6.6 | legacy_unverified | actual | SRC-v15-html | 6.6 |  |
| quarter_note | Q4 FY26 (3~5월) \| $19.2B (+21%) · OCI $5.8B (+93%) \| 영업마진 33.2% \| TTM -$23.7B · 현금 $31.9B · 런웨이 1.3년 | legacy_unverified | text | SRC-v15-html |  | 최근 분기 실적 원문(③⑨ 참고). TTM 대체 금지 |
| runway_years | 1.3 | legacy_unverified | derived | SRC-v15-html | 1.3년 ⚠️ | 원본 계산값(현금 ÷ 연 소진) |
| ttm_per | 26.4 | legacy_unverified | actual | SRC-v15-html | 26.4 |  |

### OpenAI

| 지표 | 값 | 상태 | 종류 | 출처 | 원문 | 비고 |
| --- | --- | --- | --- | --- | --- | --- |
| arr | $40.0B | legacy_unverified | run_rate | SRC-v15-rule | 런레이트 $40B+(8/20) | 규칙 v1.5 ⑥ 비상장 절 |
| cash | — | not_disclosed | actual | SRC-v15-html | 미공시 |  |
| contracted_revenue | $40.0B | incompatible_basis | actual | SRC-v15-rule | ARR $40B — 계약 수입 아님(C-07) | 규칙 v1.5 ⑨ 게이트 4 적용표 |
| credit_rating | 비상장 | legacy_unverified | text | SRC-v15-html | 비상장 | 별표 J 교차검증 전용 — 점수 입력 아님 |
| cumulative_raised | $185.0B | legacy_unverified | actual | SRC-v15-rule | 약 $180~190B(중간값) | 규칙 v1.5 ⑥ 비상장 절 |
| debt_ebitda | — | not_disclosed | actual | SRC-v15-html | — |  |
| fcf_ttm | — | not_disclosed | actual | SRC-v15-html | 미공시 | 비상장 FCF 미공시 |
| net_cash | — | not_disclosed | actual | SRC-v15-html | — |  |
| offbalance_B | $338.0B | incompatible_basis | actual | SRC-v15-rule | 컴퓨트 약정 $338B+(연 ~$60B) (C-07) | 규칙 v1.5 ⑨ 게이트 4 적용표 |
| offbalance_note | 컴퓨트 $338B+ | legacy_unverified | text | SRC-v15-html | 컴퓨트 $338B+ | 부외 약정 원문(A/B/C 분류 전) |
| post_money_valuation | $852.0B | legacy_unverified | actual | SRC-v15-rule | $852B | 규칙 v1.5 ⑥ 비상장 절 |
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
| ⑧ 비대칭 의존 | score | -3 | — | carried | legacy:v1.5 2026-09-02 |  |
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
| anthropic | cash | not_disclosed | 미공시 |
| anthropic | fcf_ttm | not_disclosed | 비상장 FCF 미공시 |
| anthropic | runway_years | not_disclosed | FCF 미공시로 소진율을 만들 수 없음(원문 판정 불가) |
| anthropic | net_cash | not_disclosed | — |
| anthropic | debt_ebitda | not_disclosed | — |
| openai | cash | not_disclosed | 미공시 |
| openai | fcf_ttm | not_disclosed | 비상장 FCF 미공시 |
| openai | runway_years | not_disclosed | FCF 미공시로 소진율을 만들 수 없음(원문 판정 불가) |
| openai | net_cash | not_disclosed | — |
| openai | debt_ebitda | not_disclosed | — |
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

- legacy_unverified 관측 198건은 기준선 열람용이며 이번 실행에서 재검증되지 않았다.
- 미결 규칙 결정: C-03, C-05, C-06, C-13, C-16 (실행 선택: C-05=apply, C-06=proposed_v15_boundaries)
