# Alibaba (BABA) FY2026 연간 영업손익 및 매출 SEC 원자료 실측 복원 보고서 (G1-TTM-26)

## 1. 핵심 결론 및 3대 실측 복원 수치 요약

SEC EDGAR 공식 호스트(`data.sec.gov`, `www.sec.gov`)의 원본 정기보고서(Form 20-F) 및 보존된 CIK XBRL facts(`validation/f6-avail-15b/_raw/CIK0001577552_BABA.json`)를 전수 조사하여, Alibaba Group Holding Limited(NYSE: BABA, CIK: 0001577552)의 FY2026 연간 영업손익, 매출 및 영업이익률을 완벽하게 복원하였다.

1. **FY2026 연간 영업손익 (Operating Income/Loss)**.
   - **RMB 기준**: **RMB 50,150 million (RMB 50,150,000,000 / 약 RMB 50.150B)**.
   - **USD 편의 환산**: **US$ 7,270 million ($7,270,000,000 / 약 $7.270B)**.
   - **적용 Taxonomy 및 개념명**: `us-gaap:OperatingIncomeLoss` (손익계산서 표기: `Income from operations`).
   - **손익 판정**: 양수(흑자)로서 F9 G1 게이트에서 **`operating_result_reviewed = profit`**으로 확정된다.
2. **FY2026 연간 매출 (Revenues)**.
   - **RMB 기준**: **RMB 1,023,670 million (RMB 1,023,670,000,000 / 약 RMB 1,023.670B)**.
   - **USD 편의 환산**: **US$ 148,401 million ($148,401,000,000 / 약 $148.401B)**.
   - **적용 Taxonomy 및 개념명**: `us-gaap:Revenues` (손익계산서 표기: `Revenue`).
3. **FY2026 연간 영업이익률 (Operating Margin)**.
   - **RMB 기준 산출**.
     $$\text{Operating Margin}_{\text{RMB}} = \frac{\text{RMB } 50,150\text{M}}{\text{RMB } 1,023,670\text{M}} = 4.898998...\% \approx \mathbf{4.90\%}$$
   - **USD 기준 산출**.
     $$\text{Operating Margin}_{\text{USD}} = \frac{\text{US\$ } 7,270\text{M}}{\text{US\$ } 148,401\text{M}} = 4.898888...\% \approx \mathbf{4.90\%}$$
   - **환율 왜곡 상쇄 확인**: 분자와 분모가 동일한 편의 환산 환율(US$1.00 = RMB 6.8980)로 변환되었으므로 환율 효과가 약분되어 양 통화 기준 비율이 4.90%로 일치한다.

---

## 2. 20-F 대 10-Q 구조적 제약 검증 및 period_basis 확정

지시서에서 요구한 'BABA가 20-F만 내서 분기 행이 0건인지' 여부를 CIK XBRL facts(`CIK0001577552_BABA.json`) 전수 조사를 통해 실측 검증하였다.

1. **Foreign Private Issuer(FPI) 보고 제도 실측**.
   - BABA는 미국 증권거래위원회(SEC)에 등록된 외국 민간 발행인(Foreign Private Issuer)이다.
   - SEC 규정상 FPI는 미국 국내 상장사와 달리 분기보고서인 Form 10-Q 제출 의무가 면제되며, 연차보고서(Form 20-F)와 수시공시(Form 6-K)만 제출한다.
2. **SEC XBRL 데이터 전수 조사 결과**.
   - CIK `0001577552`의 358개 us-gaap 개념 전체에서 Form 10-Q 제출 건수는 **0건(전무)**이다.
   - `us-gaap:OperatingIncomeLoss` 및 `us-gaap:Revenues`의 모든 회계연도 정기 보고 행은 예외 없이 `form: 20-F`, `fp: FY`로만 구성되어 있다.
   - 최근 3개년(FY2024, FY2025, FY2026) 중 정기 분기(`fp: Q1`, `fp: Q2`, `fp: Q3`) XBRL 데이터는 **0건**이다.
3. **결론 및 period_basis 선언**.
   - 따라서 4개 분기를 합산하여 TTM(Trailing Twelve Months)을 조립하는 것은 외부 수집의 문제가 아니라 공시 체계상 영구적·구조적으로 불가능하다.
   - 이에 따라 BABA의 실적 관측 기준은 TTM 대신 연간 실적을 사용하는 **`period_basis: annual`**로 공식 선언하며, 최신 감사 완료 회계연도인 FY2026(2025-04-01 ~ 2026-03-31) 수치를 확정값으로 적용한다.

---

## 3. Taxonomy 및 개념명 특정

F6-AVAIL-15B 및 F6-FX-16의 선행 조사 결과와 부합하게, BABA의 공시 Taxonomy와 회계기준을 다음과 같이 확정하였다.

- **적용 Taxonomy**: **`us-gaap`** (`ifrs-full`이 아님).
  - TSM(TSMC)이 `ifrs-full` 334개 개념을 사용하는 것과 달리, BABA는 미국 GAAP 기준(`us-gaap` 358개 개념)으로 재무제표를 작성 및 공시한다.
- **영업손익 개념명**: **`us-gaap:OperatingIncomeLoss`**.
  - 20-F 연결손익계산서(Consolidated Income Statements, p. F-6) 상의 `Income from operations` 행에 1:1로 매핑된다.
- **매출 개념명**: **`us-gaap:Revenues`**.
  - 연결손익계산서 상의 `Revenue` 행에 1:1로 매핑된다.

---

## 4. 통화(RMB vs USD) 및 편의 환산 왜곡 분석

BABA의 재무제표 통화 및 환산 정책을 Form 20-F Note 2(a) 및 Note 2(f)를 통해 실측 분석하였다.

### 1. 기능통화 및 보고통화
- **기능통화(Functional Currency)**: Alibaba Group Holding Limited 본사의 기능통화는 US$이며, 중국 본토 내 주요 자회사들의 기능통화는 RMB이다 (Note 2(f)).
- **보고통화(Reporting Currency)**: 주요 영업 활동이 중국 내에서 이루어지므로 연결 재무제표의 공식 보고통화는 **RMB(인민비/위안)**이다.

### 2. 편의 환산(Convenience Translation) 기준 및 환율
- 출처: Form 20-F Note 2(a) Basis of presentation (p. F-15).
- 공시 원문.
  > "Translations of balances in the consolidated balance sheet, consolidated income statement, consolidated statement of comprehensive income and consolidated statement of cash flows from RMB into the US$ as of and for the year ended March 31, 2026 are solely for the convenience of the readers and are calculated at the rate of **US$1.00=RMB 6.8980**, representing the exchange rate set forth in the H.10 statistical release of the Federal Reserve Board on March 31, 2026."
- 적용 환율: **1 USD = 6.8980 RMB** (2026년 3월 31일 미국 연방준비제도 H.10 고시환율).

### 3. 환율 왜곡과 영업이익률의 수학적 불변성
- **다년도 비교 시의 왜곡**.
  - 각 회계연도 20-F의 USD 편의 환산은 해당 연도 기말환율(FY2024 약 7.2282, FY2025 약 7.2552, FY2026 6.8980)을 각각 일괄 적용한다.
  - 따라서 서로 다른 연도의 공시 USD 수치로 성장률을 계산할 경우, 실제 영업 성장이 아닌 위안화 환율 변동 효과가 혼입되어 심각한 왜곡이 발생한다.
- **단일 회계연도 영업이익률의 불변성**.
  - 그러나 단일 회계연도(FY2026)의 영업이익률 계산에서는 분자(영업이익)와 분모(매출)에 정확히 동일한 환율(6.8980)이 곱해져 변환된다.
  - 수학적으로 환율 항이 분자·분모에서 완전 상쇄(약분)된다.
    $$\text{Operating Margin}_{\text{USD}} = \frac{\text{Operating Income}_{\text{RMB}} / 6.8980}{\text{Revenue}_{\text{RMB}} / 6.8980} = \frac{\text{Operating Income}_{\text{RMB}}}{\text{Revenue}_{\text{RMB}}} = \text{Operating Margin}_{\text{RMB}}$$
  - 실제 계산 결과.
    - RMB 기준: $50,150 / 1,023,670 = 0.04898998...$ ($4.90\%$)
    - USD 기준: $7,270 / 148,401 = 0.04898888...$ ($4.90\%$)
  - 백만 단위 정수 반올림 표기에 따른 0.0001%p 미만의 미세 차이를 제외하면 양 통화의 영업이익률은 완전히 일치하며, 환율 왜곡이 발생하지 않는다.

---

## 5. 미확인 3분류 및 F9 G1 영향 분석

### 1. 3분류 체계에 따른 항목별 판정
- **FY2026 연간 영업손익**: **공시되어 있었고 확인됨 (`disclosed_and_found`)**.
  - 원문 20-F 및 CIK facts에서 RMB 50,150M 및 US$ 7,270M이 명확히 추출되었다.
- **FY2026 연간 매출**: **공시되어 있었고 확인됨 (`disclosed_and_found`)**.
  - 원문 20-F 및 CIK facts에서 RMB 1,023,670M 및 US$ 148,401M이 명확히 추출되었다.
- **분기별 4분기 TTM 조립 데이터**: **회사가 공시하지 않았다 (`not_disclosed_by_company`)**.
  - FPI 제도에 따라 회사가 10-Q를 제출하지 않고 20-F 연차보고서만 공시하는 합법적·구조적 공시 형태이다.

### 2. F9 G1 게이트 및 pending_data 해소
- **기존 상태**: `operating_result_reviewed`가 `unknown`으로 남아 있어 alibaba가 `pending_data`로 차단되어 있었다.
- **실측 결과**: FY2026 연간 영업손익이 **RMB 50,150 million (US$ 7,270 million)**으로 **0을 크게 상회하는 흑자(profit)**임이 명백한 공시 원문으로 확인되었다.
- **판정 귀결**: 따라서 `operating_result_reviewed = profit`으로 확정되며, alibaba의 G1 미결 상태가 완전히 해소된다.

---

## 6. 독립 검증 및 산출물 역추적 대조 내역

### 1. 독립 검증 스위트
- 검증 파일: [`validation/g1-ttm-26/verify_baba_g1.py`](file:///C:/Users/noble/orca/workspaces/stock-report-harness/C-13/validation/g1-ttm-26/verify_baba_g1.py)
- 테스트 결과: **10개 단위 테스트 전원 통과** (`Ran 10 tests in 0.036s. OK.`, `__file__` 기반 상대경로 완비로 임의 작업 디렉터리 실행 지원).
- 검증 세부 항목.
  - Test 1: Operating Income RMB 50,150M 및 US$ 7,270M, us-gaap:OperatingIncomeLoss 개념 일치 검증.
  - Test 2: Revenues RMB 1,023,670M 및 US$ 148,401M, us-gaap:Revenues 개념 일치 검증.
  - Test 3: 영업이익률 4.90% 일치 및 양 통화 약분 논리 검증.
  - Test 4: 20-F HTML 손익계산서 표(p. F-6) 원문 대조 검증.
  - Test 5: Note 2(a) 편의 환산 환율 6.8980 RMB/USD 일치 검증.
  - Test 6: CIK XBRL facts 내 Form 10-Q 부재 및 최근 3개년 분기 행 0건 실측 검증.
  - Test 7: period_basis: annual 선언 및 구조적 사유 검증.
  - Test 8: us-gaap taxonomy 적용 검증.
  - Test 9: F9 G1 영향 operating_result_reviewed = profit 검증.
  - Test 10: SEC 공식 호스트(data.sec.gov, www.sec.gov) 전용 준수 검증.

### 2. 산출물 역추적 대조표 (Traceability Matrix)

| 보고서 단정 내용 | 산출 파일 | 참조 필드 | 검증 통과 여부 |
|---|---|---|---|
| 영업손익 RMB 50,150M / $7,270M | `baba_g1_results.json` | `survey_findings.operating_income.amount_rmb`, `amount_usd_convenience` | 검증 완료 (`test_01`) |
| 매출 RMB 1,023,670M / $148,401M | `baba_g1_results.json` | `survey_findings.revenue.amount_rmb`, `amount_usd_convenience` | 검증 완료 (`test_02`) |
| 영업이익률 4.90% 및 환율 약분 | `baba_g1_results.json` | `survey_findings.operating_margin.formatted`, `exchange_rate_cancellation` | 검증 완료 (`test_03`) |
| 20-F HTML 손익계산서 원문 일치 | `baba-20260331.htm` | `ALIBABA GROUP HOLDING LIMITED CONSOLIDATED INCOME STATEMENTS (p. F-6)` | 검증 완료 (`test_04`) |
| Note 2(a) 편의환산율 6.8980 | `baba_g1_results.json` | `convenience_translation_basis.rate_usd_to_rmb` | 검증 완료 (`test_05`) |
| 10-Q 부재 및 분기 행 0건 | `CIK0001577552_BABA.json` | `facts.us-gaap.OperatingIncomeLoss`, `Revenues` | 검증 완료 (`test_06`) |
| period_basis: annual 선언 | `baba_g1_results.json` | `period_basis.declared_basis` | 검증 완료 (`test_07`) |
| us-gaap taxonomy 채택 | `baba_g1_results.json` | `taxonomy.used` | 검증 완료 (`test_08`) |
| G1 게이트 profit 확정 | `baba_g1_results.json` | `f9_g1_impact.operating_result_reviewed` | 검증 완료 (`test_09`) |
| SEC 허용 호스트 준수 | `baba_g1_results.json` | `data_source_host_compliance` | 검증 완료 (`test_10`) |

### 3. 보존 원자료 목록
- `validation/f6-avail-15b/_raw/CIK0001577552_BABA.json` (1,397,371 bytes) — BABA SEC XBRL facts 원본.
- `validation/offb-24/_raw/baba-20260331.htm` (11,745,163 bytes) — BABA Form 20-F HTML 전문.
- `validation/g1-ttm-26/_raw/extracted_baba_ttm.json` (4,395 bytes) — 손익계산서 및 주석 구조화 발췌 데이터.
