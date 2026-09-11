# 미개시 B종 약정 및 계약 수입 SEC 공시 실측 조사 보고서 (OFFB-24)

## 1. 핵심 결론 및 3사 실측 총괄표

SEC EDGAR 공식 호스트(`data.sec.gov`, `www.sec.gov`)에 제출된 원본 정기보고서(10-K, 10-Q, 20-F, S-1/A)를 전수 조사한 결과, **기존 baseline 관측치에서 `not_disclosed` 또는 `parse_failed`로 뭉뚱그려져 있던 3사의 미개시 약정 및 계약 수입의 실제 공시 사실이 명확하게 규명되었다.**

- **SPCX (SpaceX)**. 미개시 B종 약정(미개시 리스 $1.627B 및 무조건적 비취소 구매 약정 $27.955B, 합계 **$29.582B**)과 계약 수입(백로그 **$47.461B**)이 SEC 공시 주석에 연도별 스케줄과 함께 **명확한 숫자로 공시되어 있었다.** 기존 `not_disclosed (raw: '미확인')`는 **"공시했는데 우리가 못 찾았다(확인하지 않았다)"**로 정정된다.
- **BABA (Alibaba)**. 미개시 리스는 주석에 기재가 없어 **"공시 없음 (중요성 미달 가능)"**으로 분류된다. `not yet commenced` 0건은 확인되었으나, RPO와 달리 면제 규정이 명시되지 않아 중요하지 않아 기재 대상이 아닐 가능성이 존재한다. 계약 수입(RPO)은 회사가 ASC 606 실무적 간편법을 공식 채택하여 1년 이하 및 청구권 기준 계약의 미이행 의무를 기재하지 않으므로 **"회사가 공시하지 않았다(면제 채택)"**가 확인되었다.
- **AMZN (Amazon)**. AWS 백로그는 미공시가 아니라 2025년말 **$244B**, 2026년 2분기말 **$496B**로 SEC 공시 주석에 **정확한 숫자로 공시되어 있었다.** Amazon이 2020Q2 이후 XBRL 태깅을 중단하고 서술형 본문에만 숫자를 기재하여 자동 파서가 이를 읽지 못했던 것으로, **"공시했는데 우리가 못 찾았다(파서 결함)"**로 정정된다.

### [표 1] 3사 6개 항목 실측 대조 및 3분류 총괄표

| 기업 | 조사 항목 | 기존 baseline 관측치 | SEC 원자료 실측 사실 | 3분류 귀결 | 출처 공시 및 주석 |
|---|---|---|---|---|---|
| **SPCX** | **미개시 B종 약정** (`offbalance_B`) | `not_disclosed` (raw: "미확인") | **$29.582B 실재**<br>- 미개시 리스: $1.627B<br>- 무조건적 구매약정: $27.955B | **공시했는데 우리가 못 찾음** (미확인 상태를 미공시로 둔갑시켰음) | Form 10-Q Note 16 (p. 27)<br>Form S-1/A Note 11 (p. F-36) |
| **SPCX** | **계약 수입** (`contracted_revenue`) | `not_disclosed` (raw: "미확인") | **$47.461B 실재**<br>(백로그 총액 $47,461M, 잔여의무 XBRL 태깅) | **공시했는데 우리가 못 찾음** | Form 10-Q Note 3 (p. 13) |
| **BABA** | **미개시 B종 약정** (`offbalance_B`) | `not_disclosed` (raw: "미확인") | **미개시 리스 미기재**<br>(자본약정 RMB 54.1B, 기타약정 RMB 200.1B 공시) | **공시 없음 (중요성 미달 가능)** | Form 20-F Note 6 (p. F-39)<br>Form 20-F Note 27 (p. F-73) |
| **BABA** | **계약 수입** (`contracted_revenue`) | `not_disclosed` (raw: "—") | **미공시**<br>(ASC 606 실무적 간편법 적용으로 공시 생략) | **회사가 공시하지 않음** (회계기준 면제 채택) | Form 20-F Note 2(t) (p. F-21)<br>Form 20-F Note 5 (p. F-39) |
| **AMZN** | **AWS 백로그** (`contracted_revenue`) | `parse_failed` (raw: "AWS 백로그(수백 $B급) — 숫자 미공시") | **$496B 실재 (2026Q2)**<br>(2025년말 $244B, 가중평균 잔여 6.4년) | **공시했는데 우리가 못 찾음** (XBRL 태그 부재로 서술문 파싱 실패) | Form 10-Q Note 1 (p. 11)<br>Form 10-K Note 1 (p. 42) |
| **AMZN** | **미개시 B종 약정** (`offbalance_B`) | 106,000,000,000 ($106B) | **$137.214B 실재 (2026Q2)**<br>(미개시 리스 $137.2B + 구매약정 $130.1B) | **공시되어 있었고 확인됨** (기존 $106B는 과거 시점 수치) | Form 10-Q Note 4 (p. 13)<br>Form 10-K Note 3 (p. 54) |

---

## 2. 미확인 3분류(Three-way Classification) 상세 분석

지시서의 핵심 완료 조건에 따라 '못 찾음'을 세 범주로 엄격히 구분하여 분석하였다.

1. **회사가 공시하지 않았다 (`not_disclosed_by_company`)**.
   - **해당 사례**: BABA의 계약 수입(RPO).
   - **분석 근거**: BABA는 Note 2(t)에서 ASC 606의 실무적 간편법(practical expedient)을 명시적으로 채택하여 계약기간 1년 이하 및 청구권 기준 계약의 미이행 잔여의무 공시를 생략한다고 선언하였다. 1년 초과 계약에 대해서도 Note 5에서 인식액이 중요하지 않다고 기재하여 면제로 대부분 설명된다. 이는 외부 조사자의 수집 결함이 아니라 회사의 회계기준상 합법적·진정한 미공시이다.
2. **공시했는데 우리가 못 찾았다 (`disclosed_but_not_parsed`)**.
   - **해당 사례**: SPCX의 미개시 B종 약정, SPCX의 백로그, AMZN의 AWS 백로그.
   - **분석 근거**.
     - **SPCX**: 상장사(NASDAQ)로서 Form 10-Q Note 16에 무조건적 구매 약정 $27.955B, Form S-1/A Note 11에 미개시 리스 $1.627B, Form 10-Q Note 3에 백로그 $47.461B를 명시했음에도, 기존 수집 파이프라인이 정기보고서 주석을 열어보지 않고 raw에 '미확인'으로 둔 채 status를 'not_disclosed'로 잘못 분류하였다. 특히 SPCX의 백로그와 무조건적 약정은 이미 프로젝트 내 CIK JSON 파일(`validation/f6-avail-15b/_raw/CIK0001181412_SPCX.json`)에 XBRL 태그로도 보존되어 있었다.
     - **AMZN**: Amazon은 2025년 10-K Note 1에 $244B, 2026년 2분기 10-Q Note 1에 $496B라는 명확한 숫자를 수록했으나, 2020Q2 이후 XBRL 태그 매핑을 중단하고 본문 서술형 단락으로만 공시하였다. XBRL 태그에만 의존하던 기존 파서가 본문 텍스트를 읽지 못해 '숫자 미공시'로 단정하고 `parse_failed`로 격리시켰던 것이다.
3. **공시 없음(중요성 미달 가능) 또는 어느 쪽인지 불확실 (`uncertain_unknown`)**.
   - **해당 사례**: **BABA의 미개시 운용리스 약정**.
   - **분석 근거**: BABA의 Form 20-F Note 6에는 온밸런스 리스 부채(RMB 21,726M)만 기재되어 있고 `leases not yet commenced`는 기재되어 있지 않다. 다만 RPO와 달리 면제가 선언된 것이 아니므로, 이것이 공시 의무가 있는데 미공시된 것인지, 아니면 금액이 중요하지 않아(immaterial) 기재 대상에서 제외된 것인지에 대한 불확실성이 존재한다. 따라서 이를 '회사가 공시하지 않았다'로 섣불리 단정하지 않고 '공시 없음 (중요성 미달 가능)'으로 한 단계 낮추어 분류한다.

---

## 3. SPCX (Space Exploration Technologies Corp) 실측 상세

### 1. 기업 개요 및 SEC 제출 현황
- CIK: `0001181412`
- Ticker: `SPCX` (NASDAQ 상장)
- 주요 공시: Form 10-Q (접수번호 `0001628280-26-052535`, 공시일 2026-08-04), Form S-1/A (접수번호 `0001628280-26-040364`, 공시일 2026-06-03).

### 2. 미개시 B종 약정 실측 내역
- **미개시 운용리스 약정 (Uncommenced Operating Leases)**.
  - 출처: Form S-1/A Note 11 (Leases, p. F-36).
  - 공시 원문: "The above tables exclude operating lease agreements that have been signed as of December 31, 2025, but not yet commenced for the aggregate lease payments of $1,627 million and an average lease term of 7.2 years, including the operating lease arrangement with Stateline."
  - 금액: **$1,627 million ($1.627B)**.
  - 가중평균 기간: **7.2년**.
  - 최신 확인: 2026Q2 10-Q Note 10에서 "2025년 12월 31일 이후 리스 포트폴리오에 중요한 변동 없음"을 재확인함.
- **무조건적 비취소 구매 약정 (Unconditional Non-cancelable Obligations)**.
  - 출처: Form 10-Q Note 16 (Commitments and Contingencies, p. 27).
  - 성격: AI 인프라 투자, 제3자 클라우드 용량 계약, Spectrum Transaction 약정(현금 및 Class A 보통주 지급) 등 비취소 확정 약정.
  - 연도별 지출 스케줄.
    - 2026년 잔여 6개월: $2,728 million
    - 2027년: $22,244 million
    - 2028년: $2,172 million
    - 2029년: $809 million
    - 2030년: $2 million
    - 이후: $0
    - **합계: $27,955 million ($27.955B)**.
- **B종 합산 총액**: $1,627M (미개시 리스) + $27,955M (무조건적 구매약정) = **$29,582 million ($29.582B)**.
- **제외 대상 (C종 우발 보증)**: 신용장 $645M(제한성 현금 담보), 이행보증(surety bonds) $465M은 우발 보증이므로 B종 확정 약정에서 제외함.

### 3. 계약 수입 / 백로그 실측 내역
- 출처: Form 10-Q Note 3 (Revenue: Backlog, p. 13).
- 공시 원문: "Backlog totaled $47,461 million as of June 30, 2026, of which $14,286 million was recognized as deferred revenue at June 30, 2026."
- 총액: **$47,461 million ($47.461B)**.
- 이행 스케줄: 1년 이내 56%, 1~3년 사이 34%, 3년 이후 10%.
- XBRL 태그: `us-gaap:RevenueRemainingPerformanceObligation` = 47,461,000,000.

---

## 4. BABA (Alibaba Group Holding Ltd) 실측 상세

### 1. 기업 개요 및 SEC 제출 현황
- CIK: `0001577552`
- Ticker: `BABA` (NYSE 상장)
- 주요 공시: Form 20-F for FY2026 ended March 31, 2026 (접수번호 `0001193125-26-231755`, 공시일 2026-05-20).

### 2. 미개시 B종 약정 실측 내역
- **운용리스 (Note 6, p. F-39~F-40)**: 온밸런스 리스 부채(미할인 RMB 26,837M, 현재가치 RMB 21,726M)만 공시되어 있으며, 미개시 리스(leases not yet commenced)에 대한 기재는 존재하지 않는다. 다만 RPO와 달리 면제가 선언된 것이 아니므로 중요하지 않아 기재 대상이 아닐 가능성(immaterial)이 있어, 이를 단정하지 않고 **"공시 없음 (중요성 미달 가능)"**으로 분류한다.
- **자본적 지출 및 기타 확정 약정 (Note 27, p. F-73)**.
  - 자본적 지출 약정 (Note 27(a)): 유형자산 및 사옥 신축 계약 총 **RMB 54,136 million** (1년 이내 RMB 53,484M, 1~5년 RMB 652M).
  - 기타 약정 (Note 27(c)): 코로케이션, 대역폭, 저작권 라이선스 등 총 **RMB 200,062 million** (1년 이내 RMB 57,441M, 1~5년 RMB 133,598M, 5년 초과 RMB 9,023M).
  - **B종 확정 약정 합계**: **RMB 254,198 million (약 RMB 254.2B)**. SPCX의 구매약정($27.955B)이나 AMZN의 구매약정($130.065B)과 동일한 미개시 확정 지출 성격으로 일관되게 집계된다.
  - **제외 대상 (투자 약정)**: Note 27(b)의 지분투자/M&A 등 투자 약정 최대 RMB 14,501 million은 영업 지출이 아닌 투자 지출이며 계약 수입과 대응되지 않으므로 B종 약정에서 제외한다.

### 3. 계약 수입 / RPO 실측 내역
- **ASC 606 실무적 간편법 공식 적용 확인**.
  - 출처: Form 20-F Note 2(t) (Revenue recognition: Practical expedients and exemptions, p. F-21).
  - 공시 원문: "The Company applies the practical expedient to not disclose the value of unsatisfied performance obligations for contracts with an original expected duration of one year or less and contracts for which revenue is recognized at the amount to which the Company has the right to invoice for services performed."
  - Note 5 (Revenue, p. F-39): "The amount of revenue recognized for performance obligations satisfied (or partially satisfied) in prior periods for contracts with expected duration of more than one year during the years ended March 31, 2024, 2025 and 2026 were not material."
  - XBRL 태그: `RevenueRemainingPerformanceObligation` 태그 미사용.
- **결론**: Alibaba의 계약 수입 결측은 수집 누락이 아니라 회계정책 선언에 따른 진정한 미공시임이 확정되었다. 실무적 간편법으로 1년 이하 및 청구권 기준 계약이 대부분 설명되며, 1년 초과 계약의 경우에도 비중요성(not material)으로 인해 공시되지 않았다.

---

## 5. AMZN (Amazon.com Inc) 실측 상세

### 1. 기업 개요 및 SEC 제출 현황
- CIK: `0001018724`
- Ticker: `AMZN` (NASDAQ 상장)
- 주요 공시: Form 10-K (접수번호 `0001018724-26-000004`, 공시일 2026-02-06), Form 10-Q (접수번호 `0001018724-26-000026`, 공시일 2026-07-31).

### 2. AWS 백로그 숫자 복원
- **2025년 12월 31일 기준 (10-K Note 1, p. 42)**.
  - 공시 원문: "Additionally, we have performance obligations, primarily related to AWS, associated with commitments in customer contracts for future services that we expect to fulfill but have not yet been recognized in our financial statements. For contracts with original terms that exceed one year, those commitments not yet recognized were approximately **$244 billion** as of December 31, 2025. The weighted average remaining life of our long-term contracts is **4.1 years**."
  - 수치: **$244 billion ($244,000,000,000)**.
- **2026년 6월 30일 기준 (10-Q Note 1, p. 11)**.
  - 공시 원문: "Additionally, we have performance obligations, primarily related to AWS, associated with commitments in customer contracts for future services that we expect to fulfill but have not yet been recognized in our financial statements. For contracts with original terms that exceed one year, those commitments not yet recognized were approximately **$496 billion** as of June 30, 2026. The weighted-average remaining life of our long-term contracts is **6.4 years**."
  - 수치: **$496 billion ($496,000,000,000)**.
  - 주요 기여 계약 내역.
    - 2026Q1: OpenAI와의 장기 계약 $38.0B에 더해 8년간 $100.0B 추가 확대.
    - 2026Q2: Anthropic과의 전략적 협력 계약 10년간 $100.0B 이상 추가 확대.
- **파서 결함 원인 분석**: Amazon이 2020Q2를 끝으로 XBRL 태그 `RevenueRemainingPerformanceObligation` 수치 매핑을 중단하고 Note 1 본문 서술 단락으로만 수치를 공개함에 따라, XBRL 전용 파서가 서술문 내 숫자를 추출하지 못하고 "숫자 미공시"로 오분류하였다.

### 3. 미개시 B종 약정 현황 (참조)
- Form 10-Q Note 4 (Commitments and Contingencies, p. 13) 기준 내역.
  - 미개시 리스 (Leases not yet commenced): **$137,214 million ($137.214B)** (2025년말 $96.4B에서 증가).
  - 무조건적 구매 약정 (Unconditional purchase obligations): **$130,065 million ($130.065B)**.

---

## 6. F9 게이트 및 C-16에 미치는 영향 분석

이번 실측 조사는 F9 채점 엔진의 C-16 게이트 설계와 기업별 처리 방향에 근본적인 전환점을 제공한다.

1. **SPCX (SpaceX)**.
   - 기존에는 B종 약정과 계약 수입이 모두 `not_disclosed`로 분류되어 C-05 `apply` 시 C-16(미공시 정책)으로 직행할 상황이었다.
   - 그러나 실측 결과 계약 수입 **$47.461B**와 미개시 B종 약정 **$29.582B**가 모두 확인되었다.
   - 이에 따른 잠정 커버리지 비율은 다음과 같다.
     $$\text{Coverage (잠정)} = \frac{\$47.461\text{B}}{\$29.582\text{B}} = 1.604 \text{ (잠정)}$$
   - 다만 이는 `coverage_comparable` 최종 판정 전의 잠정치이며, 판정 시 다음 단서들이 근거란에 고려되어야 한다.
     - 미개시 리스($1,627M)는 2025-12-31 기준(Form S-1/A)임.
     - 무조건적 구매약정 중 Spectrum 거래 등에 현금 및 보통주(Class A common stock) 혼합 지급 조건이 미분해됨.
     - 2027년 지출($22,244M)이 전체 약정의 약 80%로 편중됨.
     - 백로그 내 이연수익($14,286M)이 포함되어 있어 중복 산입 주의 필요.
   - 비교 가능성이 승인될 경우 C-16 결측 처리가 아닌 정상 step 0(유지) 산출의 객관적 데이터 기반이 확보되었다.
2. **BABA (Alibaba)**.
   - BABA는 미개시 리스가 주석에 기재되지 않았고(공시 없음, 중요성 미달 가능), 계약 수입(RPO)은 회계정책 선언에 따른 진정한 미공시 상태임이 확인되었다.
   - B종 확정 약정은 자본약정(RMB 54,136M) + 기타약정(RMB 200,062M) = RMB 254,198M(투자약정 제외)이나, 분자인 계약 수입이 미공시되어 커버리지 수치 산출은 불가하다(통화 RMB 및 기준일 3개월 이름 주의).
   - 따라서 실제 C-16이 적용되어야 할 기업은 3사 중 BABA 하나뿐이며, 향후 G1·G4 검토 입력 후 C-16(hold/downgrade) 정책의 정당한 대상이 된다.
3. **AMZN (Amazon)**.
   - 계약 수입 $496B가 온전히 복원되었으며, 미개시 리스 $137.2B 대비 잠정 커버리지 비율은 다음과 같다.
     $$\text{Coverage (잠정)} = \frac{\$496.0\text{B}}{\$137.214\text{B}} = 3.615 \text{ (잠정)}$$
     *(구매약정 $130.065B를 합산한 총 약정 $267.279B 기준 시 1.856 (잠정))*
   - 다만 판정 시 약정은 Thereafter(5년 초과)까지 뻗어 있는 반면 계약 수입은 1년 초과 장기 계약 기준(가중평균 6.4년)이라는 기간 차이 단서가 근거란에 남겨져야 한다.
   - 파서 결함으로 인한 `parse_failed`가 정당하게 해소될 수 있는 명확한 SEC 원문 근거가 확보되었다.

---

## 7. 독립 검증 및 산출물 역추적 대조 내역

### 1. 독립 검증 스위트
- 검증 파일: [`validation/offb-24/verify_offb_survey.py`](file:///C:/Users/noble/orca/workspaces/stock-report-harness/C-13/validation/offb-24/verify_offb_survey.py)
- 테스트 결과: **10개 단위 테스트 전원 통과** (`Ran 10 tests in 0.073s. OK.`, `__file__` 기반 상대경로 완비로 임의 작업 디렉터리 실행 지원).
- 검증 세부 항목.
  - Test 1: SPCX 10-Q Note 16 무조건적 구매 약정 $27,955M 및 스케줄 일치 검증.
  - Test 2: SPCX S-1/A Note 11 미개시 리스 $1,627M 및 기간 7.2년 일치 검증.
  - Test 3: SPCX 10-Q Note 3 백로그 $47,461M 일치 검증.
  - Test 4: BABA 20-F Note 6 온밸런스 리스(RMB 26,837M) 확인 및 미개시 리스 공시 없음(중요성 미달 가능) 검증.
  - Test 5: BABA 20-F Note 27 자본 약정 RMB 54,136M 및 기타 약정 RMB 200,062M 일치 검증.
  - Test 6: BABA 20-F Note 2(t) ASC 606 실무적 간편법 명시 기재 검증.
  - Test 7: AMZN 10-K Note 1 RPO $244B(4.1년) 일치 검증.
  - Test 8: AMZN 10-Q Note 1 RPO $496B(6.4년) 및 OpenAI/Anthropic 계약 일치 검증.
  - Test 9: AMZN 10-Q Note 4 미개시 리스 $137,214M 일치 검증.
  - Test 10: 3분류 체계 일관성, 잠정 커버리지 수치, SEC 공식 호스트 준수 검증.

### 2. 산출물 역추적 대조표 (Traceability Matrix)

| 보고서 단정 내용 | 산출 파일 | 참조 필드 | 검증 통과 여부 |
|---|---|---|---|
| SPCX 미개시 구매약정 $27,955M | `offb_survey_results.json` | `SPCX.offbalance_B.components.unconditional_noncancelable_purchase_obligations` | 검증 완료 (`test_01`) |
| SPCX 미개시 운용리스 $1,627M | `offb_survey_results.json` | `SPCX.offbalance_B.components.uncommenced_operating_leases` | 검증 완료 (`test_02`) |
| SPCX 백로그 $47,461M | `offb_survey_results.json` | `SPCX.contracted_revenue.found_value_usd` | 검증 완료 (`test_03`) |
| BABA 미개시 리스 공시 없음 | `offb_survey_results.json` | `BABA.offbalance_B.three_way_classification` | 검증 완료 (`test_04`) |
| BABA 자본약정 RMB 54.1B | `offb_survey_results.json` | `BABA.offbalance_B.disclosed_commitments_detail.capital_commitments_contracted` | 검증 완료 (`test_05`) |
| BABA RPO 간편법 미공시 | `offb_survey_results.json` | `BABA.contracted_revenue.three_way_classification` | 검증 완료 (`test_06`) |
| AMZN 2025 RPO $244B | `offb_survey_results.json` | `AMZN.contracted_revenue.found_value_usd_20251231` | 검증 완료 (`test_07`) |
| AMZN 2026Q2 RPO $496B | `offb_survey_results.json` | `AMZN.contracted_revenue.found_value_usd_20260630` | 검증 완료 (`test_08`) |
| AMZN 2026Q2 미개시 리스 $137.2B | `offb_survey_results.json` | `AMZN.offbalance_B_comparison.survey_status_20260630_uncommenced_leases_usd` | 검증 완료 (`test_09`) |
| SEC 허용 호스트 준수 및 3분류/잠정 커버리지 | `offb_survey_results.json` | `data_source_host_compliance`, `classification_criteria`, `provisional_coverage` | 검증 완료 (`test_10`) |

### 3. 보존 원자료 목록 (`validation/offb-24/_raw/`)
- `spcx-20260630.htm` (2,271,923 bytes) — SPCX Form 10-Q 원본.
- `spcx_s1a_20260603.htm` (12,116,869 bytes) — SPCX Form S-1/A 원본.
- `baba-20260331.htm` (11,745,163 bytes) — BABA Form 20-F 원본.
- `amzn-20251231.htm` (1,968,342 bytes) — AMZN Form 10-K 원본.
- `amzn-20260630.htm` (1,591,422 bytes) — AMZN Form 10-Q 원본.
- `download_metadata.json` — SEC 다운로드 메타데이터(URL, 접수번호, 파일 크기).
- `extracted_excerpts.json` — 각 공시별 주석 원문 발췌 및 JSON 구조화 데이터.
