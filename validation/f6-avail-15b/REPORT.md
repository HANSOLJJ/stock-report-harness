# 상장 12개사 SEC companyfacts 태그 가용성 독립 재확인 보고서 (F6-AVAIL-15B)

- **조사일자**: 2026-09-10
- **조사주체**: C-13 독립 검증 세션 (worker 코드 및 결과 미참조·독립 직접 수집)
- **대상**: 상장 12개사 (`META`, `NVDA`, `GOOGL`, `MSFT`, `AMZN`, `AAPL`, `ORCL`, `PLTR`, `TSLA`, `SPCX`, `TSM`, `BABA`)
- **관련 커밋/브랜치**: `HANSOLJJ/C-13`
- **동반 실행 스크립트**: [verify_sec_tags.py](file:///C:/Users/noble/orca/workspaces/stock-report-harness/C-13/validation/f6-avail-15b/verify_sec_tags.py)
- **보존 원자료 13종**: [validation/f6-avail-15b/_raw/](file:///C:/Users/noble/orca/workspaces/stock-report-harness/C-13/validation/f6-avail-15b/_raw/)
  - 12개사 SEC `companyfacts` 응답 본문 원본 JSON 전수
  - [http_metadata.json](file:///C:/Users/noble/orca/workspaces/stock-report-harness/C-13/validation/f6-avail-15b/_raw/http_metadata.json) (HTTP 200 응답 메타데이터, 타임스탬프, 바이트 수)

---

## 1. 종합 요약 (Executive Summary)

1. **조사 목적**:
   - Zacks 유료 구독($1,200) 접회 및 NTM PER 대체 결정([validation/f6-redefine-decision.md](file:///C:/Users/noble/orca/workspaces/stock-report-harness/%EC%84%A4%EA%B3%84%EC%A7%84%ED%96%89/validation/f6-redefine-decision.md))에 따라, F6를 4개 파라미터(**P1 PER**, **P2 EV/Sales**, **P3 매출성장률**, **P4 품질보정**)로 재정의하기 위한 0단계 원천 가용성을 SEC EDGAR `companyfacts`에서 직접 확인했습니다.
2. **핵심 확인 결과 (4대 질문)**:
   - **1) 매출 태그 존재 및 실제 사용 개념**:
     - US-GAAP 보고 11개사 전원 매출 데이터가 실재합니다.
     - 단, **회사마다 실제 사용하는 개념이 분기**됩니다:
       - `RevenueFromContractWithCustomerExcludingAssessedTax` (6개사): `META`, `MSFT`, `AMZN`, `AAPL`, `PLTR`, `SPCX`.
       - `Revenues` (3개사): `NVDA`, `GOOGL`, `BABA`.
       - 둘 다 최신 분기에 동일 수치로 병행 공시 (2개사): `ORCL`, `TSLA`.
     - 따라서 단일 태그 쿼리 시 결측이 발생하므로, 회사별 지정 또는 우선순위 Coalesce (`RevenueFromContractWithCustomerExcludingAssessedTax` 우선, 없으면 `Revenues`) 처리가 필수적입니다.
   - **2) 순이익 (`NetIncomeLoss`) 존재 여부**:
     - US-GAAP 보고 11개사 전원(**11/11**)에서 `NetIncomeLoss`가 100% 실재하며 최신 분기까지 완비되어 있습니다 (P1 산출 가능).
   - **3) 영업이익 (`OperatingIncomeLoss`) 존재 여부**:
     - US-GAAP 보고 11개사 전원(**11/11**)에서 `OperatingIncomeLoss`가 100% 실재하며 최신 분기까지 완비되어 있습니다 (P4 `nonop_share` 산출 가능).
   - **4) 전년 동기 동일 개념 추출 가능 여부 (YoY)**:
     - 11개사 전원 최근 분기/연간 공시(10-Q/10-K)에서 당기 수치와 **전년 동기 비교 수치(Comparative Prior Period)가 동일한 파일 내에서 동일한 개념 태그로 동시 공시**되어 있습니다 (`has_prior_year_in_same_filing: True`).
     - 최근 3개년(2023~2026) 구간에서 개념 전환 없이 100% 일관되게 전년 동기 매출 추출이 가능합니다 (P3 산출 가능).
3. **특이 종목 (TSM, BABA, SPCX)**:
   - **TSM**: `us-gaap` 택소노미가 전혀 없으며(0개), `ifrs-full` 택소노미(334개)로만 공시됩니다 (NTM-전망치조사 담당 영역).
   - **BABA**: 케이맨 제도 설립 FPI이나 20-F 제출 시 `us-gaap` 택소노미(358개)를 사용하여 `Revenues`, `NetIncomeLoss`, `OperatingIncomeLoss`가 모두 정상 수집됩니다 (단위: CNY 및 USD).
   - **SPCX (SpaceX)**: 2026-06-12 IPO 이후 2026-08-04 제출된 최초 10-Q(2026Q2)에 2026Q2($7,814M) 및 전년 동기 2025Q2($4,071M) 매출이 `RevenueFromContractWithCustomerExcludingAssessedTax`로 완비되어 있으며, 순이익/영업이익도 모두 존재합니다.

---

## 2. 조사 배경 및 필요성

1. **기존 저장 자료의 한계**:
   - 기존 워크스페이스에 저장된 10개 SEC 파일은 `EarningsPerShareDiluted` 단일 태그의 `companyconcept` 응답뿐이어서, 매출·순이익·영업이익 원자료가 전혀 포함되어 있지 않았습니다.
   - 기존 점수표의 `ttm_per`, `ps_ratio`, `nonop_share`는 분모/분자 원자료 없이 완제품 파생값으로만 존재하여 검증 및 재계산이 불가능했습니다.
2. **0단계 가용성 조사의 원칙**:
   - 본 조사는 스펙 작성 전 "필요한 원자료 태그가 실제로 존재하는가"를 검증하는 단계입니다.
   - 대량의 시계열 값을 스크래핑하는 것이 아니라, **태그 존재 여부, 회사별 개념 식별자, 기간축 형태, 전년 동기 비교 일관성**을 확인하는 데 집중했습니다.
3. **독립성 유지**:
   - worker 코드를 일체 참조하지 않고, C-13 독립 세션에서 `data.sec.gov` REST API를 직접 호출하여 원자료 응답 본문 12종을 수집·보존하고 독자적인 분석 및 검증 스크립트를 작성했습니다.

---

## 3. SEC EDGAR API 조회 환경 및 원자료 보존 내역

- **조회 엔드포인트**: `https://data.sec.gov/api/xbrl/companyfacts/CIK{10자리}.json`
- **준수 규정**:
  - `User-Agent`: `StockReportHarness/1.0 (hansol.jung@digitalcoms.net)` (SEC 필수 규격 준수).
  - 요청 간격: `time.sleep(0.3)`으로 초당 10회 제한 규정(SEC Fair Access Rule) 엄격 준수.
- **보존 원자료 (응답 본문 자체 보존)**:
  - 사후 전사나 발췌가 아닌, SEC 서버로부터 수신한 `companyfacts` JSON 응답 본문 전체(총 34.4 MB)를 [validation/f6-avail-15b/_raw/](file:///C:/Users/noble/orca/workspaces/stock-report-harness/C-13/validation/f6-avail-15b/_raw/)에 영구 보존했습니다.
  - 전 통신 내역의 HTTP 상태 코드, Content-Type, Content-Encoding, 압축/해제 바이트 수, 타임스탬프를 [http_metadata.json](file:///C:/Users/noble/orca/workspaces/stock-report-harness/C-13/validation/f6-avail-15b/_raw/http_metadata.json)에 기록했습니다 (12/12 전원 HTTP 200 OK).

---

## 4. 상장 12개사 SEC companyfacts 태그 인벤토리 종합 표

| 티커 | 기업명 | CIK | 택소노미 | 1. 주 사용 매출 개념 (최근 2024~2026 공시) | 2. NetIncomeLoss (건수/최신일) | 3. OperatingIncomeLoss (건수/최신일) | 4. YoY 전년동기 동일개념 추출 | 비고 |
|---|---|---|---|---|---|---|---|---|
| **META** | Meta Platforms, Inc. | 0001326801 | us-gaap (458) | `RevenueFromContractWithCustomerExcludingAssessedTax` | O (194건 / 2026-06-30) | O (186건 / 2026-06-30) | **가능 (O)** | `Revenues`는 2018Q3 이전 과거 데이터에만 존재 |
| **NVDA** | NVIDIA CORP | 0001045810 | us-gaap (627) | `Revenues` | O (314건 / 2026-07-26) | O (225건 / 2026-07-26) | **가능 (O)** | `RevenueFromContract...`는 2022 이전 과거에만 존재 |
| **GOOGL** | Alphabet Inc. | 0001652044 | us-gaap (543) | `Revenues` | O (152건 / 2026-06-30) | O (146건 / 2026-06-30) | **가능 (O)** | 포괄손익계산서 주개념 `Revenues` (주석에 계약매출 병행) |
| **MSFT** | MICROSOFT CORPORATION | 0000789019 | us-gaap (562) | `RevenueFromContractWithCustomerExcludingAssessedTax` | O (340건 / 2026-06-30) | O (278건 / 2026-06-30) | **가능 (O)** | 과거 `SalesRevenueNet`에서 2018년 전환 완료 |
| **AMZN** | AMAZON COM INC | 0001018724 | us-gaap (545) | `RevenueFromContractWithCustomerExcludingAssessedTax` | O (422건 / 2026-06-30) | O (289건 / 2026-06-30) | **가능 (O)** | `Revenues` 태그 부재. 과거 `SalesRevenueNet`에서 2018년 전환 |
| **AAPL** | Apple Inc. | 0000320193 | us-gaap (503) | `RevenueFromContractWithCustomerExcludingAssessedTax` | O (338건 / 2026-06-27) | O (234건 / 2026-06-27) | **가능 (O)** | 과거 `SalesRevenueNet`에서 2018년 전환 완료 |
| **ORCL** | Oracle Corporation | 0001341439 | us-gaap (535) | `Revenues` / `RevenueFromContract...` (둘 다 최신 수치 일치) | O (188건 / 2026-05-31) | O (221건 / 2026-05-31) | **가능 (O)** | 10-K 본문에 두 태그 동일 수치($67,357M) 병행 보고 |
| **PLTR** | Palantir Technologies Inc. | 0001321655 | us-gaap (356) | `RevenueFromContractWithCustomerExcludingAssessedTax` | O (83건 / 2026-06-30) | O (78건 / 2026-06-30) | **가능 (O)** | `Revenues` 태그 부재. 단일 계약매출 개념 사용 |
| **TSLA** | Tesla, Inc. | 0001318605 | us-gaap (643) | `Revenues` / `RevenueFromContract...` (둘 다 최신 수치 일치) | O (285건 / 2026-06-30) | O (202건 / 2026-06-30) | **가능 (O)** | 10-Q 본문에 두 태그 동일 수치($28,236M Q2) 병행 보고 |
| **SPCX** | Space Exploration Technologies Corp. | 0001181412 | us-gaap (174) | `RevenueFromContractWithCustomerExcludingAssessedTax` | O (4건 / 2026-06-30) | O (4건 / 2026-06-30) | **가능 (O)** | 2026-06-12 IPO 보통주. 최초 10-Q에 2026Q2 및 전년동기 2025Q2 완비 |
| **TSM** | Taiwan Semiconductor Mfg. Co. | 0001046179 | ifrs-full (334) | **us-gaap 없음 (IFRS 전용)** | X (us-gaap 0건) | X (us-gaap 0건) | **불가 (us-gaap 기준)** | us-gaap 미보고 FPI (ifrs-full 경로 전용, NTM 담당) |
| **BABA** | Alibaba Group Holding Ltd. | 0001577552 | us-gaap (358) | `Revenues` | O (47건 / 2026-03-31) | O (47건 / 2026-03-31) | **가능 (O)** | 20-F us-gaap 공시 (단위: CNY 및 USD 병기) |

---

## 5. 4대 질문별 심층 분석

### 5.1. 질문 1: 매출 태그 존재와 회사별 실제 사용 개념
- **핵심 발견**: 단일 공통 태그는 존재하지 않습니다.
  1. **`RevenueFromContractWithCustomerExcludingAssessedTax` 주 사용 (6개사)**:
     - `META`, `MSFT`, `AMZN`, `AAPL`, `PLTR`, `SPCX`
     - 이들 기업 중 `AMZN`과 `PLTR`은 `Revenues` 태그가 택소노미에 아예 존재하지 않습니다.
     - `MSFT`, `AAPL`, `META`는 과거 2018년 이전 데이터에만 `Revenues` 또는 `SalesRevenueNet`이 있고 최근 공시에는 `RevenueFromContractWithCustomerExcludingAssessedTax`만 단독으로 들어옵니다.
  2. **`Revenues` 주 사용 (3개사)**:
     - `NVDA`, `GOOGL`, `BABA`
     - `NVDA`는 2022년 이후 계약매출 태그를 쓰지 않고 `Revenues`만 최신 10-Q(2026-07-26)까지 보고합니다.
     - `GOOGL`은 `Revenues`가 최신 10-Q(2026-06-30)까지 이어지며, 계약매출 태그는 2025Q1에 멈춰 있습니다.
     - `BABA`는 20-F에서 `Revenues` 단일 태그를 사용합니다.
  3. **양쪽 태그 병행 보고 (2개사)**:
     - `ORCL`, `TSLA`: 최신 분기/연간 공시에서 `Revenues`와 `RevenueFromContractWithCustomerExcludingAssessedTax`에 정확히 동일한 매출 총액이 매핑되어 있습니다.
- **수집 파이프라인 설계 권고사항**:
  - `Revenues` 태그 하나만 조회하면 `AMZN`, `PLTR`, `MSFT`, `AAPL`, `META`, `SPCX` 등 **6개사에서 매출이 즉시 결측**됩니다.
  - 반대로 `RevenueFromContractWithCustomerExcludingAssessedTax`만 조회하면 `NVDA`에서 결측이 발생합니다.
  - 따라서 파이프라인은 반드시 **종목별 우선순위 매핑** 또는 **`Coalesce(RevenueFromContractWithCustomerExcludingAssessedTax, Revenues)` 폴백 로직**을 탑재해야 합니다.

### 5.2. 질문 2: 순이익 (`NetIncomeLoss`) 존재 여부
- **가용성**: US-GAAP 11개사 전원 완비.
- **의미**: 
  - `P1 PER = market_cap ÷ net_income_ttm`의 분모인 직전 4분기 순이익 합산(`net_income_ttm`)을 SEC 원자료에서 100% 직접 추출할 수 있습니다.
  - 적자 기업의 경우 `NetIncomeLoss`에 음수 값이 정상 반영되어 있으므로, F9 적자 로직과의 정합성도 완전히 유지됩니다.

### 5.3. 질문 3: 영업이익 (`OperatingIncomeLoss`) 존재 여부
- **가용성**: US-GAAP 11개사 전원 완비.
- **의미**:
  - `P4 품질보정`의 핵심 지표인 `nonop_share` 산출식:
    $$\text{nonop\_share} = \frac{\text{NetIncomeLoss} - \text{OperatingIncomeLoss}}{\text{NetIncomeLoss}}$$
  - 분자와 분모에 필요한 `NetIncomeLoss`와 `OperatingIncomeLoss`가 모두 SEC 원자료에 직접 존재하므로, 기존에 완제품 파생값으로만 들어와 있던 `nonop_share`를 100% 투명하게 재계산 및 역검증할 수 있습니다.

### 5.4. 질문 4: 전년 동기를 같은 개념으로 뽑을 수 있는가
- **결과**: **최근 3개년(2023~2026) 기준 100% 가능**.
- **근거**:
  - 미국 SEC 공시 규정(Regulation S-X)에 따라 10-Q 및 10-K는 당기 실적 공시 시 반드시 **비교 대상 전년 동기 실적(Comparative Prior Period)**을 동일한 XBRL 태그로 본문에 병기해야 합니다.
  - 11개사 전원의 최신 10-Q/10-K 공시 파일(단일 `accessionNumber`)을 파싱한 결과, 당기 종료일(예: 2026-06-30)과 전년 동기 종료일(예: 2025-06-30) 데이터가 **동일한 매출 태그 아래에 동시 수록**되어 있음을 확인했습니다 (`has_prior_year_in_same_filing: True`).
- **개념 전환 이력**:
  - 2018년 ASC 606(고객과의 계약에서 생기는 수익) 회계기준 개정 당시 `SalesRevenueNet`에서 `RevenueFromContractWithCustomerExcludingAssessedTax`로 전환된 이력이 있습니다 (`AAPL`, `MSFT`, `AMZN`, `META`).
  - 그러나 전환 시점(2018년) 이후 현재까지 최소 6년 이상 단일 개념이 안정적으로 유지되고 있으므로, **F6 측정 대상인 최근 1~2개년 전년 동기 매출(`revenue_ttm_prior`) 및 성장률(`P3`)을 동일 개념으로 추출하는 데 아무런 장애가 없습니다**.

---

## 6. 특이 종목 정밀 분석 (TSM, BABA, SPCX)

### 6.1. TSM (Taiwan Semiconductor Manufacturing Co., Ltd.)
- **택소노미**: `ifrs-full` (334개 개념), `us-gaap` 0개.
- **판정**: 미국 일반 상장사와 동일한 US-GAAP 경로로는 매출·순이익 조회가 불가능합니다.
- **후속 처리**: 본 과제 분담 정책에 따라 TSM의 IFRS 매출 태그(`Revenue` 등) 및 20-F 환율/편의환산(convenience translation)은 NTM-전망치조사 트랙에서 처리합니다.

### 6.2. BABA (Alibaba Group Holding Limited)
- **택소노미**: `us-gaap` (358개 개념).
- **판정**: 해외 기업(FPI)이지만 20-F 공시에서 US-GAAP 택소노미를 채택하고 있습니다.
- **매출/손익**: `Revenues`, `NetIncomeLoss`, `OperatingIncomeLoss`가 모두 실재하며, 통화 단위는 기본 CNY와 편의환산 USD가 병기되어 있습니다.

### 6.3. SPCX (Space Exploration Technologies Corp. - SpaceX)
- **신분**: 2026-06-12 NASDAQ 상장 보통주 (단일 법인 기업).
- **공시 현황**: 2026-08-04 제출된 최초 분기보고서(Form 10-Q, 2026Q2) 확인.
- **실측 수치**:
  - `RevenueFromContractWithCustomerExcludingAssessedTax`:
    - 2026Q2 (3개월): **$7,814,000,000** (CY2026Q2)
    - 2025Q2 (3개월 전년동기): **$4,071,000,000** (CY2025Q2) → **YoY 성장률 +91.94%**
    - 2026년 상반기 (6개월): $12,508,000,000
    - 2025년 상반기 (6개월): $8,138,000,000
  - `NetIncomeLoss` 및 `OperatingIncomeLoss`: 2026Q2 및 2025Q2 모두 존재.
- **결론**: SPCX는 F6 재정의 4대 파라미터(P1, P2, P3, P4)를 SEC 원자료에서 직접 도출할 수 있는 완전한 적격 상태입니다.

---

## 7. 검증 스크립트 실행 및 결론

### 7.1. 검증 스크립트 실행 결과 ([verify_sec_tags.py](file:///C:/Users/noble/orca/workspaces/stock-report-harness/C-13/validation/f6-avail-15b/verify_sec_tags.py))
- **Test 1 (실측 원자료 전수 검증)**:
  - 12개사 원자료 JSON 파일 전수 로드 및 4대 지표 판별.
  - 11개사 US-GAAP 존재, NetIncomeLoss 완비, OperatingIncomeLoss 완비, YoY 동일 개념 추출 가능 단언 통과.
  - TSM의 IFRS 택소노미 및 US-GAAP 부재 단언 통과.
  - 회사별 주 사용 매출 개념 매핑 단언 전원 일치 통과.
- **Test 2 (양성 대조)**:
  - 전 태그 완비 및 YoY 2개 기간을 포함한 합성 데이터에서 모든 판정 변수가 True를 반환함을 입증.
- **Test 3 (음성 변이 대조)**:
  - NetIncomeLoss, OperatingIncomeLoss 제거 및 단일 기간만 남긴 변이 데이터에서 결측 및 YoY 불가 판정이 동적으로 작동함을 입증.
- **종합 판정**: **3개 동적 테스트 ALL PASS**.

### 7.2. F6 재정의 프레임워크에 대한 시사점
1. **0단계 가용성 조사 통과**:
   - 상장사에 대해 F6를 P1(PER), P2(EV/Sales), P3(매출성장률), P4(품질보정)로 분해하는 데 필요한 모든 핵심 회계 입력(`net_income_ttm`, `revenue_ttm`, `revenue_ttm_prior`, `OperatingIncomeLoss`)이 SEC EDGAR `companyfacts` 원천에 실재함을 확정했습니다.
2. **파이프라인 필수 구현 사항**:
   - 매출 수집 시 단일 태그 하드코딩을 금지하고, `RevenueFromContractWithCustomerExcludingAssessedTax`와 `Revenues`의 2-way Coalesce 매핑 규칙을 적용해야 합니다.
   - TSM은 IFRS 트랙(NTM 담당), BABA는 US-GAAP 20-F 트랙으로 처리하면 12개 상장사 전원에 대한 F6 평가가 기술적으로 완벽히 가능합니다.
