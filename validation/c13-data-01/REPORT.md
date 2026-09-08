# C13-DATA-01: TSMC·Alibaba NTM 원자료 확보 검증 보고서

- **작성일자**: 2026-09-08
- **작업 ID**: `C13-DATA-01`
- **검증 대상 기업**: 
  - **TSMC** (티커: NYSE `TSM`, 대만 TWSE `2330.TW`)
  - **Alibaba** (티커: NYSE `BABA`, 홍콩 HKEX `9988.HK`)
- **수행 주체**: C-13 worktree Antigravity 담당
- **참조 문서**:
  - `docs/scorecard/design-guideline.md` (C-13, D-01~D-10, F6 계약)
  - `docs/scorecard/open-items.md` (C-13 결정 대기 및 경계 3% 위험)
  - `scripts/scorecard/calc_f6.py` (F6 계산 로직 및 4분기 연속성/기준 일치 검증기)
  - `scorecard/baseline/v1.5/observations.json` (기존 baseline 이관 관측치)

---

## 1. 검증 배경 및 목표

규칙 C-13의 사용자 결정(`accept_proxy_with_flag` vs `reject_proxy`)을 내리기 전에, **공개된 데이터 공급사로부터 TSMC 및 Alibaba의 실제 향후 4분기(NTM) EPS 컨센서스 또는 독립적으로 검증 가능한 공급사 NTM PER을 확보할 수 있는지**를 원문과 정의 문서를 대조하여 철저히 조사하는 것이 본 작업의 목표다.

기존 worker의 산출물은 과거 HTML에 기재된 수치를 이관한 것(`legacy_unverified`)에 불과하며, 신규 EPS를 실사 수집하지 않았다. 또한 타 기업에 부여된 `vendor_forward_pe_verified_ntm` 명칭 역시 원문 텍스트 설명을 단순 승계한 라벨일 뿐 기계적 검증 증거가 아니다. 본 검증은 유료 가입이나 계정 변경 없이 순수 공개 접근 가능한 채널을 통해 원자료 실체와 정의를 규명했다.

---

## 2. 핵심 결론 요약 (Executive Summary)

1. **향후 4분기(NTM) 연속 분기 EPS 컨센서스 확보: 불가 (Unobtainable)**
   - 공개 무료 데이터 공급사(Yahoo Finance/yfinance, StockAnalysis, TipRanks, Zacks, Finviz) 어디에서도 **미발표 4개 분기 연속 EPS 컨센서스**를 완전히 제공하지 않는다.
   - Yahoo Finance와 Zacks는 **최대 2개 분기(`0q`, `+1q`)**만 제공하며 차차기 이후 2개 분기(`+2q`, `+3q`)는 결측이다. TipRanks는 **직전 1개 분기**만 제공한다.
2. **공급사 `Forward P/E` 지표의 실체: NTM이 아닌 차기 회계연도(FY1/FY2) 또는 연간 근사치**
   - 공급사들이 제공하는 Forward P/E는 롤링 12개월(NTM) 합산이 아니라, **차기 회계연도(Next Fiscal Year, FY+1) 연간 EPS 추정치**를 분모로 한 배수(`P/E (F1)`)이거나 연간 추정치를 역산한 근사치다.
   - 주가와 EPS 역산 결과, Yahoo Finance의 `forwardPE`는 `price / +1y_eps`와 정확히 일치하여 NTM이 아님이 수학적으로 입증되었다.
   - Finviz와 Zacks 공식 정의 문서 역시 Forward P/E를 "Next Fiscal Year EPS 기준" 또는 "P/E (F1)"로 명시하고 있다.
3. **StockAnalysis 공개 접근의 제약**
   - 무료 공개 페이지에서는 연간(FY) 추정치만 노출되며, 분기별 세부 추정치 및 차차기 연도 추정치는 **"Stock Analysis Pro" 유료 결제벽** 뒤에 잠겨 있다.
4. **2026-09-02 기준시점 재현 불가 (No Point-in-Time History)**
   - 공개 무료 웹 공급사는 모두 현재 조회 시점(2026-09-08)의 실시간 유동 스냅샷만 제공하며, 과거 특정일(2026-09-02) 시점의 컨센서스 스냅샷을 무료로 재현할 수 있는 공개 API나 아카이브는 존재하지 않는다. 오늘 수집한 값을 과거 기준일로 소급 적용하는 것은 계약상 금지된다.
5. **C-13 규칙 결정에 미치는 영향**
   - **`reject_proxy` 선택 시**: 검증 가능한 4분기 NTM 원자료가 공개 공급사에 부재하므로, TSMC와 Alibaba의 F6는 자동 채점되지 않고 **`pending_data` (자료 대기)** 상태로 확정된다.
   - **`accept_proxy_with_flag` 선택 시**: 기존 baseline의 `annual_weighted_proxy` 수치(TSMC 19.4, Alibaba 16.7)를 참고 정밀도 플래그와 함께 수용하여 채점을 진행할 수 있다.

---

## 3. 대상 기업 프로필 및 주식·통화 기준

F6 자동 채점 계약(`calc_f6.py`)은 주가와 EPS 간 **통화 일치**, **보통주/ADR/ADS 기준 일치**, **회계연도 분기 연속성**을 필수 조건으로 요구한다.

| 항목 | TSMC | Alibaba |
|---|---|---|
| **미국 상장 티커 / 거래소** | `TSM` / NYSE | `BABA` / NYSE |
| **본국 상장 티커 / 거래소** | `2330` / 대만 증권거래소(TWSE) | `9988` / 홍콩 거래소(HKEX) |
| **주식 기준 (Share Basis)** | ADR (American Depositary Receipt) | ADS (American Depositary Share) |
| **보통주 대 ADR/ADS 비율** | **1 ADR = 보통주 5주** | **1 ADS = 보통주 8주** |
| **회사 공식 보고 통화** | 신대만달러 (**TWD**) | 위안화 (**CNY / RMB**) |
| **미국 시장 거래 주가 통화** | 미국 달러 (**USD**) | 미국 달러 (**USD**) |
| **회계연도 결산월** | 12월 31일 (Dec) | 3월 31일 (Mar) |
| **기준 통화/단위 불일치 위험** | 대만 원주는 TWD, ADR은 USD. 환율 및 5:1 배율 환산 필요 | 중국 본토/홍콩은 CNY/HKD, ADS는 USD. 8:1 배율 환산 필요 |

---

## 4. 공급사별 원자료 조사 및 기술적 검증 결과

### 4.1 Yahoo Finance / yfinance

- **조사 엔드포인트**: `https://finance.yahoo.com/quote/TSM/analysis/`, `https://finance.yahoo.com/quote/BABA/analysis/`, Python `yfinance` 모듈
- **수집 시각**: 2026-09-08 21:55 KST
- **제공 분기 범위**:
  - `earnings_estimate`의 기간 키는 `['0q', '+1q', '0y', '+1y']` 4개만 존재.
  - 분기(Quarterly) 추정치는 당분기(`0q`)와 차기 분기(`+1q`)의 **단 2개 분기만 제공**됨.
  - 향후 제3분기(`+2q`), 제4분기(`+3q`) 추정치는 데이터 자체가 없음.
- **TSMC 세부 관측치**:
  - 현재 주가(`regularMarketPrice`): **$428.91 USD**
  - `0q` (2026 Q3, 기간종료 2026-09-30): 예상 EPS **$4.45 USD** (애널리스트 9명, Low $4.26, High $4.72)
  - `+1q` (2026 Q4, 기간종료 2026-12-31): 예상 EPS **$4.96 USD** (애널리스트 9명, Low $4.76, High $5.29)
  - `0y` (FY2026 연간): 예상 EPS **$16.91 USD**
  - `+1y` (FY2027 연간): 예상 EPS **$21.86 USD**
  - `forwardEps`: **$21.9251 USD**
  - `forwardPE`: **19.5625**
  - **역산 검증**: $428.91 / $21.9251 = **19.5625** (소수점 4자리까지 일치). `forwardEps`($21.925)는 FY2027 연간 추정치($21.86)에 대응하며, 향후 4분기 롤링 합산($4.45 + $4.96 + 미상 + 미상)이 아니다.
- **Alibaba 세부 관측치**:
  - 현재 주가(`regularMarketPrice`): **$113.24 USD**
  - `0q` (FY27 Q2 / 2026-09-30): 예상 EPS **10.98 CNY** (애널리스트 17명)
  - `+1q` (FY27 Q3 / 2026-12-31): 예상 EPS **14.87 CNY** (애널리스트 15명)
  - `0y` (FY2027 연간, 종료 2027-03-31): 예상 EPS **44.50 CNY**
  - `+1y` (FY2028 연간, 종료 2028-03-31): 예상 EPS **62.73 CNY**
  - `forwardEps`: **$9.2848 USD** (FY2028 연간 EPS 62.73 CNY를 환율 ~6.756으로 환산한 USD 추정치)
  - `forwardPE`: **12.1962**
  - **역산 검증**: $113.24 / $9.2848 = **12.1962** (일치). 이 역시 FY2028 연간 추정치 기반이며 4분기 롤링 NTM이 아니다. 또한 분기 EPS는 CNY로 제시되고 주가는 USD로 제시되어 통화 혼재가 발생한다.

### 4.2 StockAnalysis

- **조사 엔드포인트**: `https://stockanalysis.com/stocks/tsm/forecast/`, `https://stockanalysis.com/stocks/baba/forecast/`, `/statistics/`
- **수집 시각**: 2026-09-08 21:53 KST
- **접근 제약**:
  - 무료 공개 페이지에는 **연간 실적 및 1개년 전망(FY2026/FY2027)**만 테이블로 노출됨.
  - 분기별 세부 컨센서스 테이블 및 2년 이상 미래 연도 전망은 **"Stock Analysis Pro" 유료 결제**를 요구함.
- **TSMC 세부 관측치**:
  - 통화: 재무제표 기준 통화인 **TWD**로 표시됨.
  - FY2026 예상 연간 EPS: 평균 **107.64 TWD** (Low 98.40, High 113.38).
  - Statistics 페이지 `Forward PE`: **19.81** (S&P Global 컨센서스 피드).
- **Alibaba 세부 관측치**:
  - 통화: ADS 기준 통화인 **USD**로 표시됨.
  - FY2027 예상 연간 EPS: 평균 **$5.71 USD** (Low $4.95, High $7.41).
  - Statistics 페이지 `Forward PE`: **12.5~16.7** (시점 및 공급사 기준에 따라 상이).
- **공급사 정의 확인**:
  - StockAnalysis의 공식 용어 설명 및 도움말 확인 결과, Forward P/E는 "Estimated EPS for the next fiscal year or upcoming period"로 정의되며 4분기 롤링 NTM을 보장하지 않는다. ADR/ADS 종목의 경우 원주의 회계연도 연간 추정치를 환율/배율로 환산한 가중치 근사치(`annual_weighted_proxy`)를 사용한다.

### 4.3 TipRanks

- **조사 엔드포인트**: `https://www.tipranks.com/stocks/tsm/earnings`, `https://www.tipranks.com/stocks/baba/earnings`
- **접근성**: 브라우저 User-Agent 필요 (일반 curl/스크래퍼는 Cloudflare 403 차단).
- **수집 시각**: 2026-09-08 21:58 KST
- **제공 분기 범위**:
  - **향후 단 1개 분기만 제공**.
  - TSMC: 2026년 10월 15일 발표 예정인 `2026 (Q3)`에 대해서만 예상 EPS **$4.39 USD** 제공.
  - Alibaba: 2026년 12월 1일 발표 예정인 `2027 (Q2)`에 대해서만 예상 EPS **$1.63 USD** 제공.
  - 그 외 과거 4~8분기 실적(Reported vs Forecast)만 나열되어 있으며, 연속 4개 분기 미래 전망은 전혀 제공하지 않음.

### 4.4 Zacks Investment Research

- **조사 엔드포인트**: `https://www.zacks.com/stock/quote/TSM/detailed-earning-estimates`, `quote/BABA/`
- **수집 시각**: 2026-09-08 21:59 KST
- **지표 명칭 및 정의**:
  - Zacks는 Forward P/E를 **`P/E (F1)`**으로 명시한다.
  - 정의: `Current Stock Price / Zacks Consensus EPS Estimate for Fiscal Year 1 (F1)`.
- **제공 분기 범위**:
  - TSMC: `Current Qtr (9/2026)` 예상 $4.45, `Next Qtr (12/2026)` 예상 $4.68의 **2개 분기만 제공**.
  - `Current Year (12/2026)` 예상 $16.52, `Next Year (12/2027)` 예상 $21.09 제공.
  - `P/E (F1)`: $428.91 / $16.52 = **25.97**. (Zacks 테이블 표기와 정확히 일치).
  - 차차기 2개 분기(`1Q27`, `2Q27`)는 무료 상세 페이지에서 제공되지 않음.

### 4.5 Finviz

- **조사 엔드포인트**: `https://finviz.com/quote.ashx?t=TSM`, `quote.ashx?t=BABA`
- **지표 명칭 및 정의**:
  - `Forward P/E`로 표기.
  - Finviz 공식 도움말/정의: "Forward Price-to-Earnings measures share price relative to its forecasted earnings per share (EPS) for the next fiscal year."
  - TSMC Forward P/E: 19.61. 이는 FY2027 연간 추정치 기준 배수이며 NTM이 아님.

### 4.6 회사 공식 IR 및 규제 공시 (TWSE MOPS, HKEX, SEC 20-F)

- TSMC IR (`investor.tsmc.com`) 및 MOPS:
  - 과거 확정 분기 실적(2026 Q2 등) 및 직전 다음 분기(Q3 2026)에 대한 경영진 가이던스(매출 미화 환산 범위, 총마진율, 영업마진율)만 발표.
  - 향후 4분기 주당순이익(EPS) 컨센서스나 시장 전망치는 회사 IR의 공시 범위가 아님.
- Alibaba IR (`alibabagroup.com/en-US/ir`):
  - 직전 분기 실적(FY27 Q1) 및 연차보고서(Form 20-F)만 제공. 미래 4분기 EPS 컨센서스 공시 부재.

---

## 5. 4분기 충족표 (Quarterly Fulfillment Matrix)

`calc_f6.py`가 요구하는 미발표 4개 분기 연속 EPS 컨센서스 확보 가능 여부를 대조한 결과는 다음과 같다.

### 5.1 TSMC (TSM, NYSE ADR 기준)

| 분기 순번 | 대상 분기 | 기간종료일 | 예상 EPS | 통화 | 주식기준 | 회계기준 | 데이터 공급사 | 확보 상태 |
|---|---|---|---|---|---|---|---|---|
| **Q1 (차기 1Q)** | 2026 Q3 | 2026-09-30 | **$4.45** | USD | ADR (1:5) | 조정(Non-GAAP) | Yahoo / Zacks | **확보** |
| **Q2 (차기 2Q)** | 2026 Q4 | 2026-12-31 | **$4.96** (Yahoo) / **$4.68** (Zacks) | USD | ADR (1:5) | 조정(Non-GAAP) | Yahoo / Zacks | **확보 (편차 존재)** |
| **Q3 (차기 3Q)** | 2027 Q1 | 2027-03-31 | *미제공* | - | - | - | 없음 (결측) | **미확보 (결측)** |
| **Q4 (차기 4Q)** | 2027 Q2 | 2027-06-30 | *미제공* | - | - | - | 없음 (결측) | **미확보 (결측)** |

- **4분기 연속 충족 여부**: **불충족 (2/4분기만 확보, 50% 결측)**
- **합산 NTM EPS 산출 가능 여부**: **불가능**

### 5.2 Alibaba (BABA, NYSE ADS 기준)

| 분기 순번 | 대상 분기 | 기간종료일 | 예상 EPS | 통화 | 주식기준 | 회계기준 | 데이터 공급사 | 확보 상태 |
|---|---|---|---|---|---|---|---|---|
| **Q1 (차기 1Q)** | FY27 Q2 | 2026-09-30 | **10.98** (CNY) / **$1.63** (USD) | CNY/USD 혼재 | ADS (1:8) | 조정(Non-GAAP) | Yahoo / TipRanks | **확보 (통화 불일치)** |
| **Q2 (차기 2Q)** | FY27 Q3 | 2026-12-31 | **14.87** (CNY) | CNY | ADS (1:8) | 조정(Non-GAAP) | Yahoo | **확보** |
| **Q3 (차기 3Q)** | FY27 Q4 | 2027-03-31 | *미제공* | - | - | - | 없음 (결측) | **미확보 (결측)** |
| **Q4 (차기 4Q)** | FY28 Q1 | 2027-06-30 | *미제공* | - | - | - | 없음 (결측) | **미확보 (결측)** |

- **4분기 연속 충족 여부**: **불충족 (2/4분기만 확보, 50% 결측)**
- **합산 NTM EPS 산출 가능 여부**: **불가능**

---

## 6. 공급사 Forward P/E의 정의 원문 대조 및 NTM 증명 여부

규칙 지침은 **"주가/EPS 역산 일치만으로 NTM을 증명하지 말 것"**을 명시하고 있다. 본 검증에서 역산 검증을 수행한 결과, 오히려 공급사의 지표가 NTM이 아님을 증명하는 결과가 도출되었다.

1. **역산 일치의 진실**:
   - Yahoo Finance의 TSM Forward P/E (19.56)는 주가($428.91)를 NTM 합산으로 나눈 것이 아니라, **차기 연간 EPS 추정치(+1y = $21.925)**로 정확히 나눈 값이다.
   - 즉, `Forward P/E = Price / FY+1 Annual EPS`이며, 롤링 12개월(NTM)이 아니라 **차기 회계연도(Fiscal Year) Forward P/E**다.
2. **공급사 공식 명칭 및 문서상의 정의**:
   - Zacks: 공식 컬럼명이 **`P/E (F1)`**으로, 1차 회계연도 기준임을 직접 명시.
   - Finviz: 공식 용어집에서 "estimated earnings per share (EPS) for the next fiscal year"로 정의.
   - StockAnalysis: S&P Global의 컨센서스를 인용하며 해외 ADR의 경우 연간 가중치 근사치(`annual_weighted_proxy`)를 사용.
3. **`vendor_forward_pe_verified_ntm` 라벨의 허구성**:
   - baseline `observations.json`에서 Meta, NVIDIA, Alphabet 등에 부여된 `vendor_forward_pe_verified_ntm`은 이전 HTML 작성자의 주관적 설명을 구조화하면서 승계된 라벨일 뿐이다.
   - 미국 12월 결산 기업의 경우 하반기로 갈수록 차기 회계연도(FY1)가 NTM과 기간상 유사해지는 착시가 있으나, 방법론적으로는 4분기 롤링 컨센서스 합산(`consensus_4q_sum`)이 아니다.

---

## 7. 과거 기준시점(2026-09-02) 재현 가능성 검증

지침은 **"현재 확보 자료와 2026-09-02 과거 기준시점 재현 가능 여부를 분리하고 오늘 값을 과거로 소급하지 말 것"**을 지시하고 있다.

1. **Point-in-Time(시계열 스냅샷) 데이터 부재**:
   - 무료 공개 웹 인터페이스(Yahoo Finance, StockAnalysis, Zacks, Finviz, TipRanks)는 실시간 데이터 서비스로서, 항상 **현재 조회 당일(2026-09-08)의 최신 스냅샷만 반환**한다.
   - 2026-09-02 당시의 컨센서스 수치를 조회할 수 있는 공개 무료 API나 과거 이력 조회 파라미터는 제공되지 않는다.
2. **소급 적용 금지 원칙 준수**:
   - 2026-09-08에 수집된 주가($428.91 / $113.24)와 컨센서스를 2026-09-02 기준선으로 소급 입력하는 것은 `D-08`(과거 기록 보존) 및 `C-17`(기준일 분리) 원칙 위반이다.
3. **기관용 데이터베이스와의 비교**:
   - Bloomberg (기능: `TSM US Equity EE <GO>`), FactSet, LSEG Workspace(구 Refinitiv I/B/E/S) 등 유료 기관용 단말기에서만 과거 특정일(Point-in-Time) 기준의 4분기 컨센서스 스냅샷을 정확히 조회할 수 있으며, 무료 공개 웹 채널에서는 물리적으로 불가능하다.

---

## 8. 자동 수집 가능성 및 파이프라인 제언

1. **무료 공개 자동 수집 파이프라인의 한계**:
   - yfinance: 안정적으로 수집 가능하나 제공 분기가 2개 분기에 불과해 4분기 NTM 합산 불가능.
   - StockAnalysis: 분기 컨센서스가 유료(Pro)로 차단되어 무료 자동 수집 불가.
   - TipRanks / Zacks: Cloudflare 봇 방어 및 스크래핑 차단 정책이 적용되어 헤드리스 환경에서 지속적이고 안정적인 자동화 곤란.
2. **파이프라인 구축 방향 제언**:
   - 정량적 4분기 NTM 합산(`consensus_4q_sum`)을 고수할 경우, 공개 웹 스크래핑 대신 합법적인 라이선스를 가진 유료 재무 데이터 API(FMP 유료 플랜, LSEG, FactSet 등)를 공식 연동해야 한다.
   - 공개 무료 데이터만을 활용하는 오픈소스 하네스 환경에서는 "4분기 롤링 컨센서스 합산"을 상장사 F6의 절대적 단일 기준으로 강제하는 데 구조적 한계가 존재한다.

---

## 9. C-13 규칙 결정에 미치는 영향 및 권고

`open-items.md`에서 지적된 바와 같이, TSMC의 기존 근사치(19.4)는 F6 점수 구간 경계인 **20**에 불과 3% 이내로 근접해 있어 산출 방식 변경에 매우 민감하다.

| 선택지 | 동작 및 결과 | 영향 분석 |
|---|---|---|
| **`reject_proxy`**<br>(근사치 거부, 엄격한 NTM 요구) | TSMC·Alibaba 모두 F6를 **`pending_data` (자료 대기)**로 확정.<br>공식 점수 산출에서 제외됨. | - 공개 출처에서 4분기 NTM이 실제로 부재하므로 논리적으로 가장 무결함.<br>- 그러나 유료 API 도입 전까지 두 대형 기업이 영구히 순위에서 배제되는 운영상 결손 발생. |
| **`accept_proxy_with_flag`**<br>(근사치 조건부 수용) | 기존 baseline의 `annual_weighted_proxy` 수치(TSMC 19.4 → 0점, Alibaba 16.7 → 0점)를 **참고 정밀도 경고 플래그와 함께 채점에 사용**. | - TSMC의 F6가 0점으로 산출되어 종합 조정점수 14점으로 완료 가능.<br>(단 Alibaba는 ⑨ 적자깊이 G1 자료 대기로 여전히 순위 외)<br>- 경계값 20 근접 경고(⚠️ 3% 이내)를 병기하여 데이터의 근사 한계를 투명하게 공개함. |

*주의: 본 보고서는 작업자로서 C-13 결정을 임의로 확정하거나 규칙을 변경하지 않으며, 순수 사실 증거만을 제공하여 사용자의 정책 결정을 지원한다.*

---

## 10. 산출물 및 생성 파일 안내

- **검증 스크립트**: `validation/c13-data-01/verify_ntm_data.py` (한국어 첫 줄 주석 준수, 자체 실행 및 테스트 완료)
- **원자료 증거 데이터**: `validation/c13-data-01/evidence.json` (공급사별 필드, 4분기 충족표, 재현성 분석 구조화 JSON)
- **종합 보고서**: `validation/c13-data-01/REPORT.md` (본 문서)
