# TSM FY2025 EDGAR Form 20-F 원문 우회 실측 및 검산 보고서

## 1. 개요 및 과제 배경

### 1.1 과제 개요
- 과제 ID: `TSM-EDGAR-29`
- 대상 기업: Taiwan Semiconductor Manufacturing Company Limited (TSMC / TSM)
- CIK: `0001046179` (SIC: `3674`)
- 대상 제출물: Form 20-F (접수번호: `0001628280-26-025362`, 보고기간: `2025-12-31`, 제출일: `2026-04-16`)
- 핵심 목표: SEC EDGAR `companyfacts` 데이터셋의 결측으로 인해 발생한 TSM의 20개월 실적 시차(최신 연간 FY2024, 2024-12-31 기준)를 해소하기 위해, F6-FX-16에서 확립된 3대 조건에 따라 EDGAR Form 20-F 원문 HTML을 우회 실측하고 FY2024 교차 검증을 완료한다.

### 1.2 F6-FX-16 EDGAR 우회 3대 조건 준수 현황
1. **제1조건 (우회 사실 관측 기록)**.
   - 우회 사실 및 사유를 관측 제안(`obs.tsm.edgar_bypass.fy2025`)으로 명확히 정리하여 worker 등록용으로 제출한다.
2. **제2조건 (겹치는 연도 두 경로 선행 검산)**.
   - FY2024 실적에 대해 `companyfacts` 공시값(매출 2,894,307,700,000 TWD, 영업손익 1,322,053,000,000 TWD)과 20-F 원문 HTML 파싱값 간의 100% 일치(불일치 0건)를 먼저 검증한 후 FY2025 추출을 진행했다.
3. **제3조건 (companyfacts 정식 반영 시 복귀)**.
   - 향후 SEC가 `companyfacts` API 데이터셋에 accession `0001628280-26-025362`의 XBRL 팩트를 갱신 등재하면 표준 companyfacts 경로로 복귀하도록 롤백 조건을 명시한다.

---

## 2. 공시 없음 서술 규율 3대 구분

본 과제에서는 선행 과제들의 교훈을 엄격히 계승하여, 확인한 범위 내의 부재를 대상의 부재로 단정하지 않고 다음 3가지 영역을 엄밀히 분리하여 기술한다.

1. **회사 공시 여부**.
   - 회사는 FY2025 감사받은 IFRS 연결재무제표가 포함된 Form 20-F를 2026-04-16 정상 제출하였다. 따라서 "회사가 공시하지 않았다"는 성립하지 않는다.
2. **조사자 발견 여부**.
   - 조사자는 SEC EDGAR 공식 아카이브(`www.sec.gov`)에서 주 문서 `tsm-20251231.htm`을 온전히 확보하여 손익계산서 및 주석 3을 전수 확인하였다. 따라서 "우리가 못 찾았다"나 "불명"이 아니다.
3. **companyfacts API 결측 원인 규명**.
   - SEC EDGAR `companyfacts` API 데이터셋(`CIK0001046179_TSM.json`)에 해당 접수번호(`0001628280-26-025362`)로 등재된 팩트는 발행주식수(`dei`)와 자사주매입한도(`srt`) 2건뿐이며, `ifrs-full` 재무 팩트가 0건으로 누락된 기술적 집계 지연 상태임을 확인하였다.

---

## 3. FY2024 두 경로 선행 교차 검증 (제2조건 검증)

FY2025를 추출하기에 앞서, Form 20-F 원문 파싱 체계의 신뢰성을 입증하기 위해 companyfacts와 Form 20-F 원문 양쪽 모두에 존재하는 FY2024(2024-01-01 ~ 2024-12-31) 실적을 전수 대조하였다.

### 3.1 교차 검증 대조표 (단위: TWD)

| 항목 | 경로 1: companyfacts (`CIK0001046179_TSM.json`) | 경로 2: Form 20-F 원문 (`tsm-20251231.htm` p. F-6) | 괴리 (TWD) | 일치율 | 판정 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **매출 (Revenue)** | 2,894,307,700,000 TWD | 2,894,307.7백만 TWD (= 2,894,307,700,000 TWD) | 0 TWD | 100.0% | **일치 (PASS)** |
| **영업손익 (Operating Profit)** | 1,322,053,000,000 TWD | 1,322,053.0백만 TWD (= 1,322,053,000,000 TWD) | 0 TWD | 100.0% | **일치 (PASS)** |
| **영업이익률 (Operating Margin)** | 45.67769% (약 45.68%) | 45.67769% (약 45.68%) | 0.0000%p | 100.0% | **일치 (PASS)** |

### 3.2 경로별 상세 명세
- **경로 1 (companyfacts)**.
  - 접수번호: `0001193125-25-083423` (FY2024 Form 20-F)
  - 매출 태그: `ifrs-full:RevenueFromContractsWithCustomers` (TWD, end `2024-12-31`, val `2,894,307,700,000`)
  - 영업손익 태그: `ifrs-full:ProfitLossFromOperatingActivities` (TWD, end `2024-12-31`, val `1,322,053,000,000`)
- **경로 2 (Form 20-F 원문 HTML)**.
  - 문서 및 위치: `tsm-20251231.htm` Item 18, Page F-6
  - 표 제목: `CONSOLIDATED STATEMENTS OF PROFIT OR LOSS AND OTHER COMPREHENSIVE INCOME`
  - 열: `2024 NT$` (컨텍스트 `c-6`, Duration `2024-01-01` ~ `2024-12-31`, scale `6`)
  - 매출 줄: `NET REVENUE` -> 표 표기 `$2,894,307.7` 백만 NT$
  - 영업손익 줄: `INCOME FROM OPERATIONS` -> 표 표기 `1,322,053.0` 백만 NT$
- **검증 결론**.
  - 양 경로 간 오차 0건, 일치율 100%를 달성하여 원문 HTML 파싱 체계의 완전성이 검증되었다. 이에 따라 FY2025 추출을 정상 실행하였다.

---

## 4. FY2025 EDGAR 원문 실측 결과

### 4.1 핵심 실측 수치 및 회계기간
- **회계기간**: FY2025 (2025-01-01 ~ 2025-12-31, 12개월 연간)
- **제출 정보**: SEC Form 20-F (접수번호: `0001628280-26-025362`, 제출일: `2026-04-16`)
- **문서 내 위치**: Item 18 Financial Statements, Page F-6, `CONSOLIDATED STATEMENTS OF PROFIT OR LOSS AND OTHER COMPREHENSIVE INCOME`
- **보고 통화**: NT$ (신대만달러, TWD)

### 4.2 손익 항목별 실측 내역

| 재무제표 표기 줄 이름 (Line Item) | 참조 주석 | iXBRL 개념명 (Concept) | iXBRL 속성 | 원문 표 표기값 (백만 TWD) | 환산 실측값 (TWD) | 전년 대비 증감 (YoY) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **NET REVENUE** | Notes 6, 22, 34, 38 | `ifrs-full:RevenueFromContractsWithCustomers` / `Revenue` | context: `c-1`, unit: `twd`, scale: `6` | 3,809,054.3 | **3,809,054,300,000 TWD** | +31.61% |
| **COST OF REVENUE** | Notes 6, 13, 29, 34, 37 | `ifrs-full:CostOfSales` | context: `c-1`, unit: `twd`, scale: `6` | 1,527,760.3 | 1,527,760,300,000 TWD | +20.30% |
| **GROSS PROFIT** | - | `ifrs-full:GrossProfit` | context: `c-1`, unit: `twd`, scale: `6` | 2,281,294.0 | 2,281,294,000,000 TWD | +40.44% |
| **OPERATING EXPENSES** | Notes 6, 29, 34 | - | - | 345,649.6 | 345,649,600,000 TWD | +14.81% |
| **OTHER OPERATING INCOME/EXP** | Notes 15, 29, 37 | `tsm:OtherOperatingIncomeAndExpensesNet` | context: `c-1`, unit: `twd`, scale: `6` | 447.3 | 447,300,000 TWD | 흑자전환 |
| **INCOME FROM OPERATIONS** | Note 38 | `ifrs-full:ProfitLossFromOperatingActivities` | context: `c-1`, unit: `twd`, scale: `6` | 1,936,091.7 | **1,936,091,700,000 TWD** | +46.45% |

### 4.3 영업이익률 산출
- **산출 공식**: Operating Margin = INCOME FROM OPERATIONS / NET REVENUE.
- **현지통화 계산**.
  - 1,936,091,700,000 TWD / 3,809,054,300,000 TWD = 0.508286707... -> 50.83%.
- **수치 비교**.
  - FY2024: 45.68% (1,322,053.0백만 TWD / 2,894,307.7백만 TWD).
  - FY2025: 50.83% (1,936,091.7백만 TWD / 3,809,054.3백만 TWD).
  - 전년 대비 마진 개선폭: +5.15%p 대폭 확장.

---

## 5. 편의 환산 USD 정보 및 미사용 규율

### 5.1 편의 환산 수치 및 기준
- **재무제표 표기 위치**: Page F-6 우측 열 `2025 US$ (Note 3)`
- **편의 환산 매출**: $121,423.5백만 USD ($121,423,500,000)
- **편의 환산 영업손익**: $61,717.9백만 USD ($61,717,900,000)
- **적용 환율**: **NT$ 31.37 = US$ 1.00**
- **기준 일자**: 2025-12-31
- **환율 출처**: 미국 연방준비제도이사회(Federal Reserve Board) H.10 통계 발표(statistical release)

### 5.2 주석 및 서두 공시 내용
- **주석 3 전문 (Page F-13, "3. U.S. DOLLAR AMOUNTS")**.
  > "TSMC and its subsidiaries (collectively as the “Company”) maintain its accounts and express its consolidated financial statements in New Taiwan dollars. For convenience only, U.S. dollar amounts presented in the accompanying consolidated financial statements have been translated from New Taiwan dollars at the exchange rate as set forth in the statistical release of the Federal Reserve Board of the United States, which was NT$ 31.37 to US$1.00 as of December 31, 2025. The convenient translations should not be construed as representations that the New Taiwan dollar amounts have been, could have been, or could in the future be, converted into U.S. dollars at this or any other rate of exchange."
- **보고서 서두 환율 안내 공시**.
  > "Unless otherwise noted, all translations from NT dollars to U.S. dollars in this annual report were made at NT$ 31.37 to US$1.00, the exchange rate set forth in the H.10 statistical release of the Federal Reserve Board on December 31, 2025."

### 5.3 편의 환산 USD 수치 미사용 사유
- F6-FX-16 지침에 따라 각 연도의 기말 시점 환율에 따른 인위적 왜곡을 방지하기 위해, 모든 마진 및 재무 지표는 본원적 기능통화이자 보고통화인 TWD 기준으로만 확정하였다.
- 편의 환산 USD로 직접 마진을 계산하더라도 $61,717.9M / $121,423.5M = 50.83%로 동일 환율 단일 나눗셈에 의해 비율 자체는 보존되나, 원칙 준수를 위해 TWD 수치를 절대적 기준으로 삼는다.

---

## 6. 관측 제안 (Observation Proposal - Worker 소관)

F6-FX-16 제1조건에 따라 관측 제안을 정형화하여 worker 과제 등록용으로 제출한다 (실제 관측 등록은 worker 권한).

```json
{
  "proposal_id": "obs.tsm.edgar_bypass.fy2025",
  "target_ticker": "TSM",
  "target_company_id": "tsmc",
  "action": "bypass_to_edgar_form_20f",
  "rationale": "TSM FY2025 Form 20-F 제출(2026-04-16) 완료에도 불구하고 SEC companyfacts에 ifrs-full 재무 팩트가 미반영되어 20개월 관측 지연이 발생함. F6-FX-16 3조건(우회 관측 기록, FY2024 양 경로 100% 일치 검산 완료, 향후 companyfacts 반영 시 롤백)을 충족하여 Form 20-F 원문 실측치 적용을 제안함.",
  "metrics": {
    "period_basis": "annual",
    "fiscal_period": "FY2025",
    "period_start": "2025-01-01",
    "period_end": "2025-12-31",
    "currency": "TWD",
    "revenue": 3809054300000,
    "operating_income": 1936091700000,
    "operating_margin_pct": 50.83,
    "filing_accession": "0001628280-26-025362",
    "filing_form": "20-F",
    "filing_date": "2026-04-16",
    "document_name": "tsm-20251231.htm",
    "document_page": "F-6"
  },
  "convenience_usd": {
    "fx_rate": 31.37,
    "fx_date": "2025-12-31",
    "source": "Federal Reserve Board H.10",
    "revenue_usd": 121423500000,
    "operating_income_usd": 61717900000
  },
  "rollback_condition": "SEC EDGAR companyfacts API에 accession 0001628280-26-025362의 ifrs-full 팩트가 정식 반영되면 companyfacts 수치로 즉시 복귀함",
  "status": "proposal_submitted_to_worker"
}
```

---

## 7. F6 및 F9 영향 분석

### 7.1 F6 (자료 최신성 및 매출 규모) 영향
- **관측 시차 단축**.
  - 기존: FY2024(2024-12-31) 기준으로 기준일(2026-09-02) 대비 **20개월** 지연 상태.
  - 갱신: FY2025(2025-12-31) 기준으로 기준일 대비 **8개월** 지연 상태로 대폭 개선 (12개월 격차 해소).
- **매출 규모 갱신**.
  - 연간 매출이 NT$ 2,894.3B에서 NT$ 3,809.1B로 31.6% 상향 반영되어 최신 AI 반도체 파운드리 매출 급성장이 반영된다.

### 7.2 F9 (의사결정 매트릭스 및 G1 평가) 영향
- **G1 적격성 (영업이익률 판정)**.
  - 기존: FY2024 실적 기준 45.68%로 G1 통과 (ok).
  - 갱신: FY2025 실적 기준 50.83%로 G1 통과 (ok).
  - 마진이 5.15%p 추가 확대되어 G1 기준선을 더욱 여유 있게 상회한다.
- **점수 및 판정 불변**.
  - TSM은 기존 매트릭스에서도 G1 통과 및 안정적 FCF 창출로 0점(불변)을 유지하고 있었으며, 이번 실측치 갱신 후에도 '통과 (ok)' 판정이 확고히 유지된다. 점수, 규칙, 승인은 변경하지 않는다.

---

## 8. 검증기 수행 결과

자체 구축한 `verify_tsm_edgar.py` 검증기를 워크트리 루트 및 로컬 디렉터리 양쪽에서 수행하여 11건 전수 통과를 확인하였다.

```
...........
----------------------------------------------------------------------
Ran 11 tests in 0.025s

OK
```

- 메타데이터 및 원문 HTML 무결성 검증 통과.
- 공식 SEC 호스트(`www.sec.gov`) 다운로드 확인 통과.
- FY2024 양 경로(companyfacts vs Form 20-F 원문) 100% 일치(불일치 0건) 확인 통과.
- FY2025 매출, 영업손익, 영업이익률 및 iXBRL 태그 파싱 완전성 검증 통과.
- Note 3 편의 환산 환율 및 주석 위치 검증 통과.
- 관측 제안 구조 및 3대 공시 구분 검증 통과.
- F6/F9 영향 분석 일치 검증 통과.
