# C13-DATA-01: TSMC·Alibaba NTM 원자료 확보 검증 보고서 (R1~R6 보완본)

- **문서 버전**: v2.0 (피드백 R1~R6 보완 반영)
- **작성일자**: 2026-09-08
- **작업 ID**: `C13-DATA-01`
- **조사 대상 기업**:
  - **TSMC** (티커: NYSE `TSM`, 대만 TWSE `2330.TW`)
  - **Alibaba** (티커: NYSE `BABA`, 홍콩 HKEX `9988.HK`)
- **수행 주체**: C-13 worktree Antigravity 담당
- **참조 문서**:
  - `docs/scorecard/design-guideline.md` (C-13, D-01~D-10, F6 계약)
  - `docs/scorecard/open-items.md` (C-13 결정 대기 및 경계 3% 위험)
  - `scripts/scorecard/calc_f6.py` (F6 자동 산출 계약, 4분기 연속성 검증기)
  - `scorecard/baseline/v1.5/observations.json` (기존 baseline 이관 관측치)
  - Orca 피드백 전문 `msg_bda33bc6cd31` (R1~R6 요구사항)

---

## 1. 개요 및 보완 목적

본 보고서는 AI Scorecard framework의 F6(가격) factor와 관련하여, 규칙 결정 C-13(`accept_proxy_with_flag` vs `reject_proxy`)의 정책 판단 근거를 마련하기 위해 **공개 데이터 공급사로부터 TSMC 및 Alibaba의 향후 4분기(NTM) EPS 컨센서스 또는 검증 가능한 공급사 NTM PER 원자료를 확보할 수 있는지**를 조사·검증한 결과를 담는다.

초기 보고서 제출 후 접수된 설계진행 검토 피드백(`msg_bda33bc6cd31`, R1~R6)에 따라 다음 사항을 전면 보완·수정하였다:
1. **[R1] 역산에 의한 기간 단정 제거**: `Price / forwardEps = forwardPE`는 데이터 제공사의 단순 항등식 확인일 뿐이며, FY1 또는 비NTM의 독립적 증명이 될 수 없음을 명시하고 기간 정의 공식 근거가 없는 경우 `unknown`으로 정정. TSM의 `forwardEps`(21.9251)와 `+1y`(21.86117) 수치 간 불일치(차이 0.06393) 명시. BABA 환율 추정에 의한 FY2028 단정 제거.
2. **[R2] StockAnalysis BABA 통화·단위 실사 및 `source_conflict` 처리**: 웹페이지 원문의 `Financial currency is CNY` 주석과 EPS 5.71 수치 간 통화·주식단위 불일치를 독립 근거로 대조하여 공급사 내부 충돌(`source_conflict`)로 규명.
3. **[R3] StockAnalysis 공식 정의 분리**: `annual_weighted_proxy`는 baseline 하네스의 이관 라벨일 뿐 StockAnalysis 공식 명칭이 아니므로 공식 산출 방식을 `unknown`으로 정정.
4. **[R4] 자동 관측과 수동 관측의 분리**: `verify_ntm_data.py`에서 고정된 하드코딩을 제거하고, API/웹 응답의 실제 관측 데이터로부터 결측 분기와 충족 여부를 동적으로 판정하도록 개선.
5. **[R5] 전칭 명제 제거 및 조사 범위 한정**: "전원 부재", "영구 배제" 등의 과도한 일반화를 배제하고, "조사 대상 6개 출처 내 미확보, 접근 제한, 기간 정의 미확인"으로 서술 범위를 엄격히 한정. 4분기 미확보(수집 실패)와 시장 전체 부재를 구분.
6. **[R6] TipRanks 용어 정정 및 미확인 필드 명시**: TipRanks의 제공 범위를 "차기 1개 분기(upcoming 1 quarter) 및 과거 실적 분기"로 명확히 정정하고, GAAP 여부 및 추정치 기준시각 미기재 항목을 `unconfirmed / unknown`으로 처리.

---

## 2. 조사 대상 기업 프로필 및 주식·통화 기준

| 항목 | TSMC | Alibaba |
|---|---|---|
| **미국 상장 티커 / 거래소** | `TSM` / NYSE | `BABA` / NYSE |
| **본국 상장 티커 / 거래소** | `2330` / 대만 증권거래소(TWSE) | `9988` / 홍콩 거래소(HKEX) |
| **주식 기준 (Share Basis)** | ADR (American Depositary Receipt) | ADS (American Depositary Share) |
| **보통주 대 ADR/ADS 비율** | **1 ADR = 보통주 5주** | **1 ADS = 보통주 8주** |
| **회사 공식 보고 통화** | 신대만달러 (**TWD**) | 위안화 (**CNY / RMB**) |
| **미국 거래 주가 통화** | 미국 달러 (**USD**) | 미국 달러 (**USD**) |
| **회계연도 결산월** | 12월 31일 | 3월 31일 |
| **기준 통화/단위 불일치 위험** | 대만 원주(TWD)와 ADR(USD) 간 환율 및 5:1 배율 환산 필요 | 중국 본토/홍콩(CNY/HKD)과 ADS(USD) 간 환율 및 8:1 배율 환산 필요 |

---

## 3. 공급사별 원자료 조사 및 기술적 검증 결과

### 3.1 Yahoo Finance (yfinance API 및 웹페이지)

- **조사 엔드포인트**: `https://finance.yahoo.com/quote/TSM/analysis/`, `https://finance.yahoo.com/quote/BABA/analysis/` 및 Python `yfinance`
- **조사 시각**: 2026-09-08 22:08 KST
- **제공 분기 관측 결과**:
  - `earnings_estimate` 기간 키: `['0q', '+1q', '0y', '+1y']`만 수신됨.
  - 분기(Quarterly) 추정치는 당분기(`0q`)와 차기 분기(`+1q`) **2개 분기만 제공**되며, 차차기 이후(`+2q`, `+3q`)는 결측(`missing_quarters: ['+2q', '+3q']`).
- **TSMC 세부 수치 대조 (R1 반영)**:
  - 현재 주가(`regularMarketPrice`): **$428.91 USD**
  - `forwardPE`: **19.56251**
  - `forwardEps`: **$21.9251 USD**
  - `0q` (2026 Q3): 예상 EPS **$4.45297 USD** (애널리스트 9명)
  - `+1q` (2026 Q4): 예상 EPS **$4.95689 USD** (애널리스트 9명)
  - `0y` (FY2026 연간): 예상 EPS **$16.91131 USD**
  - `+1y` (FY2027 연간): 예상 EPS **$21.86117 USD**
  - **수치 비교 및 산식 검산**:
    * `Price / forwardEps` = $428.91 / $21.9251 = **19.56251**로 항등식 일치 확인.
    * 그러나 `forwardEps`($21.9251)와 `+1y` 연간 평균($21.86117)은 **$0.06393 차이**가 있어 완전히 동일한 숫자가 아님.
    * Yahoo Finance 공식 문서에서 `forwardEps`가 롤링 NTM인지, FY+1 조정치인지 명시한 원문 정의 문서는 무료 채널에서 제공되지 않음.
    * 따라서 공급사 공식 정의 근거 부재로 인해 대상 기간은 **`unknown (공급사 기간 정의 공식 근거 미확보)`**으로 판정함 (R1 준수).
- **Alibaba 세부 수치 대조 (R1 반영)**:
  - 현재 주가(`regularMarketPrice`): **$113.24 USD**
  - `forwardPE`: **12.196245**
  - `forwardEps`: **$9.284824 USD**
  - `0q` (FY27 Q2): 예상 EPS **10.98 CNY** (통화: CNY)
  - `+1q` (FY27 Q3): 예상 EPS **14.87 CNY** (통화: CNY)
  - `0y` (FY2027 연간): 예상 EPS **44.50 CNY**
  - `+1y` (FY2028 연간): 예상 EPS **62.73 CNY**
  - **수치 비교 및 산식 검산**:
    * `Price / forwardEps` = $113.24 / $9.284824 = **12.19625**로 항등식 일치 확인.
    * `earnings_estimate`의 분기 및 연간 수치는 통화가 **CNY**로 기재되어 있는 반면, 주가와 `forwardEps`는 **USD**로 표시됨.
    * 62.73 CNY를 9.2848 USD로 나눈 값(~6.756)이 위안화 환율과 유사하다는 추론만으로 FY2028이라고 단정할 수 없으며, Yahoo의 환산 공식과 기간 정의가 명시된 공식 원문이 없으므로 대상 기간은 **`unknown`**으로 처리함 (R1 준수).

### 3.2 StockAnalysis (R2, R3 반영)

- **조사 엔드포인트**: `https://stockanalysis.com/stocks/baba/forecast/`, `https://stockanalysis.com/stocks/tsm/forecast/`
- **조사 시각**: 2026-09-08 21:53 KST
- **BABA 통화 및 단위 실사 (R2 반영)**:
  - **원문 주석(Footer Note)**:
    > `<div class="mt-0.5 pl-px text-sm text-muted">EPS and Forward PE are based on non-GAAP adjusted numbers. Financial currency is CNY.</div>`
  - **표 내 수치**:
    * 매출(Revenue): FY2026 1.02T, FY2027 1.12T (CNY)
    * 순이익(Net Income): FY2026 62.98B, FY2027 85.76B (CNY)
    * 주당순이익(EPS): FY2026 3.35, FY2027 5.71
    * Forward PE: FY2027 133.10 (표 내) vs 12.5~16.7 (통계 페이지)
  - **`source_conflict` (공급사 내부 불일치) 규명**:
    * 표 하단에는 `Financial currency is CNY`라고 명시되어 있음.
    * 알리바바의 발행주식수는 보통주 약 193억 주, ADS(1:8) 환산 시 약 24.1억 주임.
    * FY27 예상 순이익 85.76B CNY를 보통주로 나누면 약 **4.44 CNY/보통주**, ADS로 환산하면 약 **35.5 CNY/ADS**가 됨. 이를 미화 환율(~7.1)로 환산하면 약 **$5.0 USD/ADS** 수준임.
    * 표에 적힌 `5.71`이라는 숫자가 CNY 기준 보통주 EPS인지, USD 기준 ADS EPS인지, 혹은 다른 조정 기준인지에 대한 주석이 없으며, "Financial currency is CNY" 주석과 EPS 5.71 수치 표기 간에 명백한 **공급사 내부 모순(`source_conflict`)**이 존재함.
- **공식 산출 정의 검증 (R3 반영)**:
  - baseline의 `annual_weighted_proxy` 명칭은 이전 하네스 작성자가 부여한 라벨일 뿐이며, StockAnalysis 공식 문서에는 해당 용어나 산출식에 대한 설명이 전혀 존재하지 않음.
  - StockAnalysis는 S&P Global 컨센서스 피드를 인용한다고만 밝히고 세부 산출 알고리즘을 공개하지 않으므로, 공급사의 공식 산출 방식은 **`unknown (공식 문서 미확인)`**으로 정정함.
- **접근 제약**:
  - 분기별 세부 컨센서스는 "Stock Analysis Pro" 유료 결제벽으로 차단되어 무료 공개 접근 불가.

### 3.3 TipRanks (R6 반영)

- **조사 엔드포인트**: `https://www.tipranks.com/stocks/tsm/earnings`, `https://www.tipranks.com/stocks/baba/earnings`
- **조사 시각**: 2026-09-08 21:58 KST
- **제공 분기 범위 정정 (R6 반영)**:
  - 이전 보고서의 "직전 1개 분기"라는 혼동을 주는 표현을 **"차기 1개 분기(upcoming 1 quarter) 및 과거 실적 분기"**로 바로잡음.
  - **TSMC**: 2026년 10월 15일 발표 예정인 **차기 1개 분기(2026 Q3, 예상 EPS $4.39)**만 제공하며, 이후 3개 분기(2026 Q4, 2027 Q1, 2027 Q2)는 미제공.
  - **Alibaba**: 2026년 12월 1일 발표 예정인 **차기 1개 분기(FY2027 Q2, 예상 EPS $1.63)**만 제공하며, 이후 3개 분기는 미제공.
  - 테이블의 나머지 행들은 모두 이미 발표된 과거 실적(Reported EPS vs Forecast)임.
- **회계 기준 및 추정치 시각 미확인 (R6 반영)**:
  - TipRanks 표에는 GAAP/Non-GAAP 조정 여부가 명시되어 있지 않으므로 **`gaap_status: unconfirmed`**로 처리함.
  - 개별 애널리스트 추정치가 집계된 기준 시각(as-of date)도 표시되지 않아 **`estimate_as_of: unconfirmed`**로 처리함.

### 3.4 Zacks Investment Research

- **조사 엔드포인트**: `https://www.zacks.com/stock/quote/TSM/detailed-earning-estimates`
- **조사 시각**: 2026-09-08 21:59 KST
- **제공 분기 및 연도 범위**:
  - 분기: `Current Qtr (09/2026)` 예상 $4.45, `Next Qtr (12/2026)` 예상 $4.68의 **2개 분기만 제공**.
  - 연도: `Current Year (12/2026, F1)` 예상 $16.52, `Next Year (12/2027, F2)` 예상 $21.09 제공.
- **지표 명칭 및 정의**:
  - Forward P/E를 **`P/E (F1)`**으로 명시하며, 주가($428.91)를 Fiscal Year 1 연간 추정치($16.52)로 나눈 25.97로 산출함.
  - 향후 4분기 롤링 NTM이 아님이 공급사 표기로 확인됨.

### 3.5 Finviz

- **조사 엔드포인트**: `https://finviz.com/quote.ashx?t=TSM`
- **지표 정의 원문 확인**:
  - Finviz 용어집: "Forward P/E is a valuation metric that measures a company's current share price relative to its forecasted earnings for the next fiscal year."
  - 공식적으로 차기 회계연도(Next Fiscal Year) 기준임을 명시하고 있어 NTM과 다름.

### 3.6 회사 공식 IR 및 규제 공시 (TWSE MOPS, HKEX, SEC)

- **TSMC IR** (`investor.tsmc.com`) 및 **MOPS**: 과거 확정 실적과 직전 다음 분기 경영진 가이던스(매출/마진율)만 공시하며, 4분기 연속 EPS 시장 컨센서스는 공시 대상이 아님.
- **Alibaba IR** (`alibabagroup.com/ir`): 과거 실적 및 연차보고서만 제공, 미래 4분기 EPS 컨센서스 미공시.

---

## 4. 4분기 충족표 (Quarterly Fulfillment Matrix)

`calc_f6.py` 계약(`basis.quarters` 4개 연속 YYYYQn)에 따른 출처별 실측 충족 현황이다.

### 4.1 TSMC (NYSE `TSM` ADR 기준, 통화 USD)

| 분기 | 대상 분기 | 기간종료일 | Yahoo 관측치 | TipRanks 관측치 | Zacks 관측치 | GAAP/조정 | 추정기준시각 | 확보 상태 |
|---|---|---|---|---|---|---|---|---|
| **1Q** | 2026 Q3 | 2026-09-30 | **$4.45** | **$4.39** | **$4.45** | unconfirmed | unconfirmed | **확보** |
| **2Q** | 2026 Q4 | 2026-12-31 | **$4.96** | *미제공* | **$4.68** | unconfirmed | unconfirmed | **확보 (출처간 편차)** |
| **3Q** | 2027 Q1 | 2027-03-31 | *미제공* | *미제공* | *미제공* | - | - | **조사 출처 내 미확보 (결측)** |
| **4Q** | 2027 Q2 | 2027-06-30 | *미제공* | *미제공* | *미제공* | - | - | **조사 출처 내 미확보 (결측)** |

- **4분기 연속 충족률**: **50% (2개 분기 관측, 2개 분기 결측)**
- **NTM 합산 산출 가능 여부**: **불가능** (`calc_f6.py` R01 연속성 검증 통과 불가)

### 4.2 Alibaba (NYSE `BABA` ADS 기준)

| 분기 | 대상 분기 | 기간종료일 | Yahoo 관측치 | TipRanks 관측치 | StockAnalysis 관측치 | 통화/단위 상태 | 확보 상태 |
|---|---|---|---|---|---|---|---|
| **1Q** | FY27 Q2 | 2026-09-30 | **10.98 CNY** | **$1.63 USD** | *미제공 (연간만)* | 통화 불일치 | **확보 (통화 상이)** |
| **2Q** | FY27 Q3 | 2026-12-31 | **14.87 CNY** | *미제공* | *미제공 (연간만)* | CNY | **확보** |
| **3Q** | FY27 Q4 | 2027-03-31 | *미제공* | *미제공* | *미제공 (연간만)* | - | **조사 출처 내 미확보 (결측)** |
| **4Q** | FY28 Q1 | 2027-06-30 | *미제공* | *미제공* | *미제공 (연간만)* | - | **조사 출처 내 미확보 (결측)** |

- **4분기 연속 충족률**: **50% (2개 분기 관측, 2개 분기 결측)**
- **StockAnalysis BABA**: 주석(CNY)과 EPS 수치(5.71) 간 모순으로 **`source_conflict`** 판정.
- **NTM 합산 산출 가능 여부**: **불가능**

---

## 5. 과거 기준시점(2026-09-02) 재현 가능성 분석

- **Point-in-Time 스냅샷 기능 부재**:
  조사한 5개 무료 공개 웹 공급사(Yahoo Finance, StockAnalysis, TipRanks, Zacks, Finviz)는 모두 **현재 조회 시점의 유동(floating) 실시간 스냅샷만 반환**한다.
- **소급 적용 금지 (`D-08`, `C-17`)**:
  2026-09-08에 수집된 현재 주가나 컨센서스 수치를 2026-09-02 시점으로 소급 입력하는 것은 framework 계약상 엄격히 금지된다.
- **유료 기관용 DB 커버리지 유보 (R5 반영)**:
  FactSet, Bloomberg, LSEG I/B/E/S 등 기관용 유료 서비스의 경우 과거 특정일(Point-in-Time) 컨센서스 시계열을 제공하는 기능이 통상 존재하지만, TSMC 및 Alibaba의 2026-09-02 당시 4분기 커버리지를 직접 실사하지 않았으므로 데이터 존재를 확정적으로 단정하지 않고 **미확인 상태**로 둔다.

---

## 6. 조사 범위 한정 결론 및 C-13 정책 영향 (R5 반영)

### 6.1 조사 범위 한정 결론
1. **조사 출처 내 미확보**: 본 조사가 확인한 6개 공개 출처(Yahoo Finance, StockAnalysis, TipRanks, Zacks, Finviz, 회사 IR) 범위 내에서 TSMC와 Alibaba의 **미발표 4분기 연속 EPS 컨센서스는 확보되지 않았다 (미확보/접근제한)**. 이는 해당 출처 내에서의 관측 실패 및 접근 제약을 의미하며, 금융 시장 전체에 데이터가 부재하다는 전칭 주장이 아니다.
2. **공급사 PER 지표의 성격**: Zacks와 Finviz는 공식 정의상 차기 회계연도(FY1) 기준이며, Yahoo Finance와 StockAnalysis는 기간 정의 공식 문서가 미확인(`unknown`) 상태이므로, 공급사 Forward P/E 필드명만으로 NTM 적격성을 입증할 수 없다.
3. **BABA 통화 충돌**: StockAnalysis BABA의 경우 주석과 수치 간 충돌로 인해 `source_conflict` 상태이다.

### 6.2 C-13 규칙 결정 영향 분석
| 선택지 | 산출기(`calc_f6.py`) 동작 | 정책적 의미 및 영향 |
|---|---|---|
| **`reject_proxy`**<br>(근사치 거부) | TSMC·Alibaba 모두 4분기 연속 컨센서스 부재로 인해 F6가 **`pending_data` (자료 대기)**로 확정됨. | 엄격한 4분기 NTM 계약을 관철하여 데이터 무결성을 유지하나, 공개 출처 기반 실행에서는 두 기업이 순위에 편입되지 못함. |
| **`accept_proxy_with_flag`**<br>(근사치 조건부 수용) | baseline에 기록된 `annual_weighted_proxy` 수치(TSMC 19.4 → 0점, Alibaba 16.7 → 0점)를 **참고 정밀도 경고 플래그와 함께 채점에 사용**. | TSMC(조정총점 14)의 채점이 완료될 수 있음 (Alibaba는 ⑨ G1 자료 대기로 여전히 미완료). 단, TSMC 19.4는 구간 경계(20) 대비 3% 이내 주의 대상임. |

*주의: 본 보고서는 사실 검증 증거만을 제공하며, C-13 선택지 확정이나 기업 순위 편입은 사용자의 정책 결정 영역으로 남겨둔다.*
