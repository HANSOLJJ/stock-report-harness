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
   - Zacks 유료 구독($1,200) 철회 및 NTM PER 대체 결정([validation/f6-redefine-decision.md](file:///C:/Users/noble/orca/workspaces/stock-report-harness/%EC%84%A4%EA%B3%84%EC%A7%84%ED%96%89/validation/f6-redefine-decision.md))에 따라, F6를 4개 파라미터(**P1 PER**, **P2 EV/Sales**, **P3 매출성장률**, **P4 품질보정**)로 재정의하기 위한 0단계 원천 가용성을 SEC EDGAR `companyfacts`에서 직접 확인했습니다.
2. **핵심 확인 결과 (4대 질문 및 TTM 조립성)**:
   - **1) 매출 태그 존재 및 실제 사용 개념**:
     - US-GAAP 보고 11개사 전원 매출 데이터가 실재합니다.
     - 단, **회사마다 실제 사용하는 개념이 세 갈래로 분기**됩니다:
       - `RevenueFromContractWithCustomerExcludingAssessedTax` (6개사): `META`, `MSFT`, `AMZN`, `AAPL`, `PLTR`, `SPCX`. (특히 `AMZN`, `PLTR`, `SPCX` 3개사는 `Revenues` 태그가 택소노미에 아예 부재합니다.)
       - `Revenues` (3개사): `NVDA`, `GOOGL`, `BABA`.
       - 둘 다 최신 분기에 동일 수치로 병행 공시 (2개사): `ORCL`, `TSLA`.
     - 따라서 단일 태그 쿼리 시 결측이 발생하므로, 회사별 지정 또는 우선순위 Coalesce (`RevenueFromContractWithCustomerExcludingAssessedTax` 우선, 없으면 `Revenues`) 처리가 필수적입니다.
   - **2) 순이익 (`NetIncomeLoss`) 존재 여부**:
     - US-GAAP 보고 11개사 전원(**11/11**)에서 `NetIncomeLoss`가 100% 실재하며 최신 분기까지 완비되어 있습니다 (P1 분모 확보).
   - **3) 영업이익 (`OperatingIncomeLoss`) 존재 여부**:
     - US-GAAP 보고 11개사 전원(**11/11**)에서 `OperatingIncomeLoss`가 100% 실재하며 최신 분기까지 완비되어 있습니다 (P4 `nonop_share` 산출 가능).
   - **4) 전년 동기 동일 개념 추출 가능 여부 및 TTM 조립 가능성**:
     - **Filing 내 전년 동기 비교치 (11/11 가능)**: 11개사 전원 최근 분기/연간 공시(10-Q/10-K)에서 당기 수치와 **전년 동기 비교 수치(Comparative Prior Period)가 동일한 파일 내에서 동일한 개념 태그로 동시 공시**되어 있습니다 (`has_prior_year_in_same_filing: True`).
     - **최신 연도 Q4 직접 태깅 (0/12, 전 종목 부재)**: 그러나 이것이 4개 연속 분기 단순 합산을 뜻하지는 않습니다. 미국 Form 10-K는 연간(FY) 총계만 싣고 4분기를 독립 분기 행으로 직접 태깅하지 않으므로, 최신 연도 기준 Q4 직접 태깅은 **0/12**입니다 (과거 태깅 이력이 있던 NVDA·TSLA는 2020년, ORCL은 2022년경 중단).
     - **TTM 복원 경로 `FY - (Q1+Q2+Q3)` (9/12 가능)**: 따라서 TTM은 연간(12개월)에서 1~3분기 단순 합을 차감하는 복원 경로로만 생성 가능하며, 이 경로가 확보되는 곳은 일반 미국 상장사 **9/12**입니다 (`META`, `NVDA`, `GOOGL`, `MSFT`, `AMZN`, `AAPL`, `ORCL`, `PLTR`, `TSLA`).
     - **막힌 3개사의 기간 단위 차이**:
       - `SPCX`: Form 10-K 제출 이력 없음(연간 FY 0행). 최초 10-Q(2026Q2)만 존재하여 차감 복원 불가. 따라서 P1·P2 TTM 산출 불가. (단, 2026Q2 vs 2025Q2 분기 YoY 성장률인 P3는 완전 산출 가능).
       - `TSM`: 외국 사기업(FPI)으로 Form 20-F 연간 공시만 수행(분기 0행), US-GAAP 부재 (`ifrs-full` 334개). 연간 대체 필요.
       - `BABA`: FPI로 Form 20-F 연간 공시만 수행(분기 0행). US-GAAP 공시이나 연간 데이터만 존재. 연간 대체 필요.
     - 종전 보고의 "100% 추출 가능"은 단순 filing 내 비교치 존재를 과하게 서술한 것이었으며, 실질적 TTM 조립 가능성은 **9/12**로 정정합니다.
3. **특이 종목 요약 (TSM, BABA, SPCX)**:
   - **TSM**: `us-gaap` 택소노미가 전혀 없으며(0개), `ifrs-full` 택소노미(334개)로만 공시됩니다 (NTM-전망치조사 담당 영역).
   - **BABA**: 케이맨 제도 설립 FPI이나 20-F 제출 시 `us-gaap` 택소노미(358개)를 사용하여 `Revenues`, `NetIncomeLoss`, `OperatingIncomeLoss`가 모두 정상 수집됩니다 (단위: CNY 및 USD, 연간 기준).
   - **SPCX (SpaceX)**: 2026-06-12 IPO 이후 2026-08-04 최초 10-Q(2026Q2) 제출. 연간 실적이 없어 TTM(P1, P2)은 현시점 불가하나, 분기 YoY 성장률(+91.94%, P3)과 품질보정(P4)은 정상 산출 가능합니다.

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

| 티커 | 기업명 | CIK | 택소노미 | 1. 주 사용 매출 개념 (최근 2024~2026 공시) | 2. NetIncomeLoss | 3. OperatingIncomeLoss | 4. YoY 비교치 (Filing내) | 5. Q4 직접태깅 | 6. TTM 복원 (FY-3Q) | 비고 |
|---|---|---|---|---|---|---|---|---|---|---|
| **META** | Meta Platforms, Inc. | 0001326801 | us-gaap (458) | `RevenueFromContractWithCustomerExcludingAssessedTax` | O (194건) | O (186건) | **O** | **X (0/12)** | **가능 (O)** | `Revenues`는 2018 이전 유물, 연간 2025 내 분기 3개로 Q4 복원 |
| **NVDA** | NVIDIA CORP | 0001045810 | us-gaap (627) | `Revenues` | O (314건) | O (225건) | **O** | **X (0/12)** | **가능 (O)** | `RevenueFromContract...`는 2022 이전 과거, Q4는 2020년 끊김 |
| **GOOGL** | Alphabet Inc. | 0001652044 | us-gaap (543) | `Revenues` | O (152건) | O (146건) | **O** | **X (0/12)** | **가능 (O)** | 주개념 `Revenues`, 연간 2025 내 분기 3개로 Q4 복원 |
| **MSFT** | MICROSOFT CORPORATION | 0000789019 | us-gaap (562) | `RevenueFromContractWithCustomerExcludingAssessedTax` | O (340건) | O (278건) | **O** | **X (0/12)** | **가능 (O)** | `Revenues`는 2010 유물, 6월 결산(Q4 6월 부재), 연간-3Q 복원 |
| **AMZN** | AMAZON COM INC | 0001018724 | us-gaap (545) | `RevenueFromContractWithCustomerExcludingAssessedTax` | O (422건) | O (289건) | **O** | **X (0/12)** | **가능 (O)** | **`Revenues` 태그 부재 (3사 중 1)**, 연간 2025 내 3Q로 Q4 복원 |
| **AAPL** | Apple Inc. | 0000320193 | us-gaap (503) | `RevenueFromContractWithCustomerExcludingAssessedTax` | O (338건) | O (234건) | **O** | **X (0/12)** | **가능 (O)** | `Revenues` 2018 유물, 52/53주 회계(날짜 오차 허용 필요) |
| **ORCL** | Oracle Corporation | 0001341439 | us-gaap (535) | `RevenueFromContract...` (분기최신) / `Revenues` (연간) | O (188건) | O (221건) | **O** | **X (0/12)** | **가능 (O)** | `Revenues` 분기 2022 끊김(연간만 최신), 계약매출 분기로 복원 |
| **PLTR** | Palantir Technologies Inc. | 0001321655 | us-gaap (356) | `RevenueFromContractWithCustomerExcludingAssessedTax` | O (83건) | O (78건) | **O** | **X (0/12)** | **가능 (O)** | **`Revenues` 태그 부재 (3사 중 1)**, 단일 계약매출로 Q4 복원 |
| **TSLA** | Tesla, Inc. | 0001318605 | us-gaap (643) | `Revenues` / `RevenueFromContract...` (병행) | O (285건) | O (202건) | **O** | **X (0/12)** | **가능 (O)** | 두 태그 동일 수치 병행, Q4 직접태깅 2020 끊김, 연간-3Q 복원 |
| **SPCX** | Space Exploration Technologies Corp. | 0001181412 | us-gaap (174) | `RevenueFromContractWithCustomerExcludingAssessedTax` | O (4건) | O (4건) | **O** | **X (0/12)** | **불가 (X)** | **`Revenues` 태그 부재 (3사 중 1)**, 10-K(연간) 부재로 TTM 불가, 분기 YoY만 가능 |
| **TSM** | Taiwan Semiconductor Mfg. Co. | 0001046179 | ifrs-full (334) | **us-gaap 없음 (IFRS 전용, 20-F 연간만)** | X (0건) | X (0건) | **X** | **X (0/12)** | **불가 (X)** | FPI로 10-Q 의무 없음, 분기 사실 전무(0건), 연간 대체 필요 |
| **BABA** | Alibaba Group Holding Ltd. | 0001577552 | us-gaap (358) | `Revenues` (20-F 연간만) | O (47건) | O (47건) | **O (연간)** | **X (0/12)** | **불가 (X)** | FPI로 10-Q 의무 없음, 분기 사실 전무(0건), 연간 대체 필요 |

---

## 5. 4대 질문별 심층 분석

### 5.1. 질문 1: 매출 태그 존재와 회사별 실제 사용 개념
- **핵심 발견**: 단일 공통 태그는 존재하지 않으며, 실질 사용은 세 갈래로 분기됩니다.
  1. **`RevenueFromContractWithCustomerExcludingAssessedTax` 주 사용 (6개사)**:
     - `META`, `MSFT`, `AMZN`, `AAPL`, `PLTR`, `SPCX`
     - **`Revenues` 태그 완전 부재 (3개사)**: `AMZN`, `PLTR`, `SPCX` 3개사는 `us-gaap` 택소노미 내에 `Revenues` 태그 자체가 아예 존재하지 않습니다.
     - `MSFT`(2010년 마지막), `AAPL`(2018년 마지막), `META`(2018년 마지막)는 과거 유물 데이터에만 `Revenues`가 있고 현행 공시에는 계약매출 태그만 들어옵니다.
  2. **`Revenues` 주 사용 (3개사)**:
     - `NVDA`, `GOOGL`, `BABA`
     - `NVDA`는 2022년 이후 계약매출 태그를 쓰지 않고 `Revenues`만 최신 10-Q(2026-07-26)까지 보고합니다.
     - `GOOGL`은 `Revenues`가 최신 10-Q(2026-06-30)까지 이어지며, 계약매출 태그는 2025Q1에 멈춰 있습니다.
     - `BABA`는 20-F에서 `Revenues` 단일 태그(CNY/USD)를 사용합니다.
  3. **양쪽 태그 병행 보고 (2개사)**:
     - `ORCL`, `TSLA`: 최신 공시에서 두 개념이 모두 존재합니다.
     - 특히 `TSLA`는 동일 기간에 두 태그가 100% 일치하며 함께 공시됩니다.
     - `ORCL`의 경우 `Revenues`는 연간만 최신(2026-05-31)이고 분기는 2022-05-31에서 끊겼으므로, 현행 분기 계열은 `RevenueFromContractWithCustomerExcludingAssessedTax`입니다.
- **수집 파이프라인 설계 권고사항**:
  - `Revenues` 태그 하나만 조회하면 `AMZN`, `PLTR`, `SPCX` 등 **3개사에서 즉시 결측**이 발생하고, `MSFT`, `AAPL`, `META`는 과거 2010~2018년 유물 데이터가 집계됩니다.
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

### 5.4. 질문 4: 전년 동기를 같은 개념으로 뽑을 수 있는가 및 TTM 조립 가능성 (핵심 보완)

- **층위의 구분: "Filing 내 비교치 존재" vs "TTM 조립 가능성"**:
  - 종전 보고에서 "전년 동기 비교치가 동일 태그로 수록되어 100% 추출 가능"이라고 서술한 것은 **단순 Filing 내 비교치 존재**에 국한된 과한 표현이었으며, 실질적인 **TTM(Trailing Twelve Months) 조립 가능성**과는 명확히 구분되어야 합니다.

1. **Filing 내 전년 동기 비교치 존재 (11/11 가능)**:
   - 미국 SEC 규정(Regulation S-X)에 따라 10-Q 및 10-K 공시 본문에는 당기 실적과 직전 전년 동기 비교 실적이 동일한 파일 내 동일 태그로 병기됩니다 (`has_prior_year_in_same_filing: True`).
   - 2018년 ASC 606 전환 이후 최근 3개년(2023~2026) 동안 개념 변경 없이 일관성이 유지되고 있습니다.
   - 52/53주 회계연도를 채택하는 기업의 경우 NVDA(1일 차이: 2025-07-27 ↔ 2024-07-28), AAPL(6일 차이: 2017-09-30 ↔ 2016-09-24)처럼 전년 동기 일자가 정확히 365일이 아니므로, 기계 대조 시 **±10일 허용 오차** 적용이 필수적입니다 (실측 최대 편차 6일에 여유 버퍼 4일 감안).

2. **최신 회계연도 4분기(Q4) 직접 태깅 부재 (0/12, 전 종목 불가)**:
   - 미국 상장사는 Form 10-K 제출 시 **12개월 연간(FY) 총계만 공시**하며, 4분기(3개월) 실적을 독립된 분기 행으로 직접 태깅하지 않습니다.
   - 과거에 Q4를 태깅하던 기업들도 NVDA·TSLA는 2020년경, ORCL은 2022년경에 모두 직접 태깅이 중단되었습니다.
   - 따라서 12개사 전원 최신 회계연도에서 **4개 분기 연속 단순 합산으로 TTM을 직접 조립하는 것은 0/12로 전면 불가**합니다.

3. **TTM 복원 경로: `연간(FY) - (Q1 + Q2 + Q3) = Q4` (9/12 가능)**:
   - Q4가 직접 태깅되지 않으므로, 유일한 TTM 산출 경로는 연간 12개월 실적에서 1~3분기 단순 합을 차감하여 Q4를 복원하는 방식입니다.
   - 최신 연간 구간 내에 3개 분기(Q1, Q2, Q3)가 온전히 존재하는 곳은 미국 일반 상장사 **9/12**입니다:
     - `META`, `NVDA`, `GOOGL`, `MSFT`, `AMZN`, `AAPL`, `ORCL`, `PLTR`, `TSLA` (9개사 완비).
   - **막힌 3개사의 기간 단위 차이**:
     - `SPCX`: 2026-06-12 상장 후 최초 10-Q(2026Q2)만 제출되어 **Form 10-K(연간 FY)가 0행**입니다. 차감 대상인 연간 총액이 없으므로 TTM 복원 불가(P1, P2 불가). 단, 2026Q2 vs 2025Q2 분기 YoY 성장률(P3)은 완전 산출 가능.
     - `TSM`: 외국 사기업(FPI)으로 Form 20-F 연간 공시만 수행하며, **분기 사실이 0행**입니다. 또한 US-GAAP이 부재하므로 TTM 조립 불가(연간 대체 필요).
     - `BABA`: FPI로 Form 20-F 연간 공시만 수행하며, **분기 사실이 0행**입니다. US-GAAP 공시이나 분기 데이터가 없어 TTM 조립 불가(연간 대체 필요).
   - **파이프라인 구현 주의점**: 복원은 조회가 아니라 계산(파생값)이므로, 분모/분자 불투명성을 방지하기 위해 복원 시 사용된 4개 원자료(FY, Q1, Q2, Q3)를 함께 저장해야 합니다.

---

## 6. 특이 종목 정밀 분석 (TSM, BABA, SPCX)

### 6.1. TSM (Taiwan Semiconductor Manufacturing Co., Ltd.)
- **택소노미**: `ifrs-full` (334개 개념), `us-gaap` 0개.
- **판정**: 미국 일반 상장사와 동일한 US-GAAP 경로로는 매출·순이익 조회가 불가능합니다.
- **기간 단위**: Form 20-F 연간 공시만 수행(분기 0건)하므로 TTM 산출은 불가하며, 연간 단위 지표 대체가 요구됩니다.
- **후속 처리**: 본 과제 분담 정책에 따라 TSM의 IFRS 매출 태그(`Revenue` 등) 및 20-F 환율/편의환산(convenience translation)은 NTM-전망치조사 트랙에서 처리합니다.

### 6.2. BABA (Alibaba Group Holding Limited)
- **택소노미**: `us-gaap` (358개 개념).
- **판정**: 해외 기업(FPI)이지만 20-F 공시에서 US-GAAP 택소노미를 채택하고 있습니다.
- **기간 단위**: Form 20-F 연간 공시만 수행(분기 0건)하므로 TTM 산출은 불가하며, 연간 단위 지표 대체가 요구됩니다.
- **매출/손익**: `Revenues`, `NetIncomeLoss`, `OperatingIncomeLoss`가 모두 실재하며, 통화 단위는 기본 CNY와 편의환산 USD가 병기되어 있습니다.

### 6.3. SPCX (Space Exploration Technologies Corp. - SpaceX)
- **신분**: 2026-06-12 NASDAQ 상장 보통주 (단일 법인 기업).
- **공시 현황**: 2026-08-04 제출된 최초 분기보고서(Form 10-Q, 2026Q2) 확인. Form 10-K(연간)는 아직 제출 이력 없음.
- **실측 수치**:
  - `RevenueFromContractWithCustomerExcludingAssessedTax`:
    - 2026Q2 (3개월): **$7,814,000,000** (CY2026Q2)
    - 2025Q2 (3개월 전년동기): **$4,071,000,000** (CY2025Q2) → **YoY 성장률 +91.94%**
    - 2026년 상반기 (6개월): $12,508,000,000
    - 2025년 상반기 (6개월): $8,138,000,000
  - `NetIncomeLoss` 및 `OperatingIncomeLoss`: 2026Q2 및 2025Q2 모두 존재.
  - `Revenues` 태그: 부재 (`AMZN`, `PLTR`과 함께 택소노미 내 미제공).
- **정정된 결론**:
  - SPCX는 연간 Form 10-K가 없으므로 `FY - (Q1+Q2+Q3)` 복원 경로를 쓸 수 없어 **P1 PER 및 P2 EV/Sales의 TTM 산출은 현시점 불가**합니다.
  - 그러나 2026Q2와 전년 동기 2025Q2가 완비되어 있으므로 **P3 매출성장률(분기 YoY +91.94%)과 P4 품질보정(`nonop_share`)은 완전 산출 가능**합니다.
  - 이는 구조적 불가가 아니며, 향후 첫 번째 10-K 보고서 제출 시 시간이 해결하는 일시적 제약입니다.

---

## 7. 검증 스크립트 실행 및 결론

### 7.1. 검증 스크립트 실행 결과 ([verify_sec_tags.py](file:///C:/Users/noble/orca/workspaces/stock-report-harness/C-13/validation/f6-avail-15b/verify_sec_tags.py))
- **Test 1 (실측 원자료 전수 검증)**:
  - 12개사 원자료 JSON 파일 전수 로드 및 4대 지표 판별.
  - 11개사 US-GAAP 존재, NetIncomeLoss 완비, OperatingIncomeLoss 완비, YoY 동일 개념 추출 가능 단언 통과.
  - **Q4 직접 연속 태깅 0/12 단언 통과** (12개사 전원 최신 연도 Q4 직접 태깅 부재).
  - **TTM 복원 경로(`FY - 3Q`) 9/12 단언 통과** (SPCX, TSM, BABA 제외 9개사 정확히 일치).
  - **US-GAAP 기업 중 Revenues 태그 부재 3개사(`AMZN`, `PLTR`, `SPCX`) 단언 통과**.
  - TSM의 IFRS 택소노미 및 US-GAAP 부재 단언 통과.
  - 회사별 주 사용 매출 개념 매핑 단언 전원 일치 통과.
- **Test 2 (양성 대조)**:
  - 연간(FY) 및 3개 분기(Q1, Q2, Q3)가 완비된 합성 데이터에서 TTM 복원(`fy_minus_3q`), YoY 비교치, 전 태그가 모두 True를 반환함을 입증.
- **Test 3 (음성 변이 대조)**:
  - 연간/분기 제거, NetIncomeLoss/OperatingIncomeLoss/Revenues 제거 변이 데이터에서 결측 및 TTM 복원 불가 판정이 동적으로 작동함을 입증.
- **종합 판정**: **3개 동적 테스트 ALL PASS**.

---

## 8. 결정문 정정 사항 독립 교차 확인 (`f6-redefine-decision.md`)

- **확인 대상**: `설계진행` 워크트리의 `validation/f6-redefine-decision.md` 87행 "비영업손익 원자료가 스키마에 없다" 기술.
- **독립 교차 확인 결과**:
  - `worker/scripts/scorecard/schema.py` 확인 결과, `operating_income_ttm`은 이미 지표 카탈로그 `schema.METRICS`(65행) 및 `PERIOD_REQUIRED_METRICS`(28행)에 정의되어 있습니다:
    ```python
    "operating_income_ttm": {"unit": "USD", "type": "number"}
    ```
  - 또한 `revenue_ttm` 역시 `schema.METRICS`(64행)에 이미 정의되어 있습니다.
  - 종전 결정문에서 "스키마에 없다"고 한 것은 사실과 다르며, **스키마에는 필드가 실재하나 수집된 관측치가 0개사였던 것**입니다.
  - 따라서 신규 정의가 필요한 지표(metric)는 4종이 아니라 **3종**입니다:
    1. `net_income_ttm` (신규 정의 필요)
    2. `revenue_ttm_prior` (신규 정의 필요)
    3. `arr_prior` (신규 정의 필요)
  - `revenue_ttm`과 `operating_income_ttm`은 스키마 정의 변경이 아니라 **값을 채우는 수집의 문제**임을 C-13 세션에서도 공식 확인합니다.
