# F6-H 사이트별 독립 공급원 비교 조사 보고서

## 1. 개요 및 '종목별 사이트 혼합 배제' 원칙

본 보고서는 `msg_9c9b44bc73ee` 지침에 따라 제안된 **F6-H(하이브리드 F6, 2A+2E)** 모드의 정식 도입 가능성을 **사이트별 공급원 단위**로 독립 검증한 결과입니다.

기존 관측 과정에서 특정 종목은 나스닥, 다른 종목은 핀허브나 FMP에서 취사선택하는 방식(체리피킹)은 공급사 간 집계 기준·통화 단위·회계 조정 방식의 불일치로 인해 공통 방법 문서에서 엄격히 금지되었습니다. 이에 따라 본 조사는 **"하나의 후보 공급원 경로로 12개 상장사 전체를 일괄 조회하여 2A+2E를 온전히 확보할 수 있는가"**를 단일 기준으로 평가했습니다.

본 조사는 프로덕션 채점 코드나 기존 점수(v1.5)를 일체 변경하지 않고, 독립적인 분석 스크립트([run_source_comparison.py](file:///C:/Users/noble/orca/workspaces/stock-report-harness/C-13/validation/f6-h-sources-02/run_source_comparison.py))와 시뮬레이션 원자료([raw_source_comparison.json](file:///C:/Users/noble/orca/workspaces/stock-report-harness/C-13/validation/f6-h-sources-02/raw_source_comparison.json))를 기반으로 정량 검증을 수행했습니다.

---

## 2. 6대 후보 공급원 개요 및 수집 경로

조사 대상 6대 공급원과 데이터 수집 경로는 다음과 같습니다.

1. **Nasdaq (`api.nasdaq.com` / Zacks Consensus) [생산 배제 - 비생산 참고용 검증 증거]**:
   - 생산 원천 상태: **생산 원천 배제 (Denied / Non-production Reference Only)**.
   - 배제 사유: robots.txt(Disallow: /) 및 웹사이트 약관(제2조 자동 수집 금지)에 따라 생산 입력, 관측 등록, F6 점수 계산, HTML 리포트 근거 사용 전면 배제.
   - 취급 기준: 기존 수집 표본은 규격·포맷 비교를 위한 '비생산 참고용 검증 증거(non-production reference)'로만 보존되며, 배제 결정 이후 api.nasdaq.com 추가 조회를 일체 수행하지 않음.
   - 원천 공급자: Zacks Investment Research.
   - 회계 기준: Zacks BNRI (Non-GAAP 조정 희석 EPS, 비반복 손익 제외, 스톡옵션 비용 포함).
   - 과거 샘플 경로: `https://api.nasdaq.com/api/analyst/{TICKER}/earnings-forecast` (2E) 및 `.../quote/{TICKER}/eps` (2A).
2. **StockAnalysis (`stockanalysis.com` via `__data.json`)**:
   - 원천 공급자: S&P Global Market Intelligence (`spg`) + TipRanks.
   - 회계 기준: S&P Global Normalized Non-GAAP Diluted EPS.
   - 수집 경로: `https://stockanalysis.com/stocks/{ticker}/forecast/__data.json`.
3. **Finnhub (`finnhub.io`)**:
   - 원천 공급자: Finnhub 자체 브로커 집계.
   - 회계 기준: 미확정 (GAAP/Non-GAAP 미표기, 종목별 혼재).
   - 수집 경로: `https://finnhub.io/api/v1/calendar/earnings?symbol={TICKER}`.
4. **Financial Modeling Prep (FMP)**:
   - 원천 공급자: FMP Fundamental Data.
   - 회계 기준: 미확정 (Annual 기준 제공).
   - 수집 경로: `https://financialmodelingprep.com/stable/analyst-estimates?symbol={TICKER}&period=quarter`.
5. **TradingView (`tradingview.com`)**:
   - 원천 공급자: FactSet / TradingView Fundamentals.
   - 회계 기준: Normalized Diluted EPS.
   - 수집 경로: `https://scanner.tradingview.com/symbol?symbol={TICKER}` (Fundamental Quote JSON).
6. **Valley / Yahoo Finance (Legacy Baseline)**:
   - 원천 공급자: LSEG / Refinitiv (I/B/E/S) 또는 레거시 Valley 고정 테이블.
   - 회계 기준: Refinitiv Non-GAAP / 정적 Forward P/E.
   - 수집 경로: Yahoo Finance `quoteSummary` (401 차단) / v1.5 레거시 정적 보존 데이터.

---

## 3. 12개 상장사 일괄 확보율 및 Coverage Matrix

### (1) 공급원별 12개사 종합 비교 매트릭스

| 후보 공급원 | 생산 정책 상태 | F6-H 적격수 (기술/참고) | 적격률 (%) | 2A 확보수 | 2E 확보수 | 단위 정합수 | 표본수 제공 | asOf 시계열 | 약관 및 생산 후보 적격성 |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Nasdaq (api.nasdaq.com)** | **배제 (Denied)** | 9/12 (비생산 참고용) | 75.0% | 9/12 | 12/12 | 10/12 | **제공 (애널리스트수)** | 미제공 (asOf null) | **생산 원천 배제 (비인가 엔드포인트)**. 약관상 자동 수집 금지, 생산 후보 제외. |
| **Finnhub** | 후보 유지 (불합격) | **9/12** | **75.0%** | 11/12 | 11/12 | 9/12 | **미제공 (0개, 403)** | 미제공 (발표일만 존재) | 무료 분당 60콜 허용, 단 전용 컨센서스는 403 차단. |
| **StockAnalysis** | 후보 유지 (불합격) | **0/12** | **0.0%** | 0/12 | 9/12 | 0/12 | **제공 (S&P Global)** | 미제공 (스냅샷만 존재) | 스크래핑 금지, S&P Global 재배포 엄격 금지. |
| **FMP** | 후보 유지 (불합격) | **0/12** | **0.0%** | 0/12 | 0/12 | 0/12 | **제공 (연간에 한함)** | 미제공 | **무료 등급 period=quarter 전면 차단 (HTTP 402)**. |
| **TradingView** | 후보 유지 (불합격) | **0/12** | **0.0%** | 0/12 | 9/12 | 0/12 | **미제공 (Quote 부재)** | 미제공 | 웹 내부 엔드포인트 무단 스크래핑 금지. |
| **Valley / Yahoo** | 기준선 (불합격) | **0/12** | **0.0%** | 0/12 | 0/12 | 0/12 | **제공 (NVDA 44)** | 미제공 | **Yahoo API 401 차단, yfinance 금지, Valley 정적 보존**. |

> **판정 결과 및 생산 후보 정정**:
> - 6개 후보 공급원 중 **12개 상장사 전원(100%)을 일괄 확보할 수 있는 단일 생산 공급원은 전무**합니다.
> - **Nasdaq 9/12 수치 정정**: Nasdaq의 9/12 수치는 채택 후보가 아니며, 비인가 공개 엔드포인트(`api.nasdaq.com`) 정책상 **생산 후보에서 전면 제외(Denied)**되었습니다. 해당 수치는 비생산 참고용 검증 증거(non-production reference)로만 취급됩니다.
> - 따라서 기술적으로 9/12에 도달한 Finnhub 역시 단위 왜곡(TSMC 5배, BABA 8배) 및 SPCX 결측, 403 차단으로 인해 생산 채택 불가(FAIL)입니다.

---

### (2) 공급원별 12개사 종목별 세부 판정표

| 종목코드 | 기업명 | 시장/단위 | Nasdaq | Finnhub | StockAnalysis | FMP | TradingView | Yahoo/Valley |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **AAPL** | Apple | US 보통주 (USD) | **PASS** | **PASS** | 2A 부재 | 402 차단 | 2A 부족(1Q만) | 401 차단 |
| **MSFT** | Microsoft | US 보통주 (USD) | **PASS** | **PASS** | 2A 부재 | 402 차단 | 2A 부족(1Q만) | 401 차단 |
| **GOOGL** | Alphabet | US 보통주 (USD) | **PASS** | **PASS** | 2A 부재 | 402 차단 | 2A 부족(1Q만) | 401 차단 |
| **AMZN** | Amazon | US 보통주 (USD) | **PASS** | **PASS** | 2A 부재 | 402 차단 | 2A 부족(1Q만) | 401 차단 |
| **META** | Meta | US 보통주 (USD) | **PASS** | **PASS** | 2A 부재 | 402 차단 | 2A 부족(1Q만) | 401 차단 |
| **NVDA** | NVIDIA | US 보통주 (USD) | **PASS** | **PASS** | 2A 부재 | 402 차단 | 2A 부족(1Q만) | 401 차단 |
| **TSLA** | Tesla | US 보통주 (USD) | **PASS** | **PASS** | 2A 부재 | 402 차단 | 2A 부족(1Q만) | 401 차단 |
| **ORCL** | Oracle | US 보통주 (USD) | **PASS** | **PASS** | 2A 부재 | 402 차단 | 2A 부족(1Q만) | 401 차단 |
| **PLTR** | Palantir | US 보통주 (USD) | **PASS** | **PASS** | 2A 부재 | 402 차단 | 2A 부족(1Q만) | 401 차단 |
| **SPCX** | SpaceX | US 보통주 (신규) | **FAIL (2A 결측)** | **FAIL (티커 부재)** | **FAIL (결측)** | 402 차단 | **FAIL (결측)** | 401 차단 |
| **TSM** | TSMC | TW ADR (5:1) | **FAIL (단위 불일치)**| **FAIL (TWD 보통주)**| 2A 부재 | 402 차단 | 단위 불일치 | 401 차단 |
| **BABA** | Alibaba | CN ADS (8:1) | **FAIL (단위 불일치)**| **FAIL (ADS/CNY 왜곡)**| 2A 부재 | 402 차단 | 단위 불일치 | 401 차단 |

---

## 4. 회계 기준, 통화 및 ADR/ADS 단위 정합성 심층 분석

단일 공급원으로 12개사를 채우지 못하는 본질적인 구조적 병목은 다음 세 가지입니다.

### 1. ADR/ADS 외환 및 주식 단위의 치명적 괴리
- **TSMC (TSM)**:
  - 본사 공시 통화는 신대만달러(TWD)이며 보통주 5주당 1 ADR(미국 주가 $439.00)로 거래됩니다.
  - **Nasdaq**: 2E 컨센서스는 USD per ADR($18.87)로 제공되나, 과거 실적(2A)은 본사 재무제표(TWD 보통주)를 참조해야 하므로 동일 단일 엔드포인트에서 2A와 2E의 통화/주식 단위가 일치하지 않습니다.
  - **Finnhub**: 2E 및 2A가 대만 보통주(2330.TW, TWD) 기준으로 반환되어 미국 주가($439.00)와 5배 및 환율(약 32:1) 차이가 발생합니다.
- **Alibaba (BABA)**:
  - 본사 공시 통화는 위안화(CNY)이며 보통주 8주당 1 ADS로 거래됩니다.
  - **Finnhub**: 실제 실적 `epsActual`은 CNY per ADS인 반면, 발행주식수(`shareOutstanding`)는 보통주 수로 반환되어 순이익 산출 시 8배 부풀려지는 심각한 결함이 실측되었습니다.

### 2. 신규 상장사 (SpaceX / SPCX)의 실적 이력 부재
- SpaceX는 2026-06-12에 상장되었으므로, 상장 후 정식 10-Q 확정 실적이 누적되지 않았습니다.
- **Nasdaq**: 과거 분기 실적이 `0.00` 또는 음수로 기록되어 정상적인 2A 합산이 불가능합니다.
- **Finnhub**: 캘린더 데이터베이스에 SPCX 티커 자체가 등록되어 있지 않아 100% 결측됩니다.

### 3. 단일 엔드포인트 내 2A+2E 결합 구조의 부재
- **StockAnalysis**: `forecast/__data.json`은 미래 전망치만 다루며 과거 2개 분기 실적(2A)을 포함하지 않아 단일 호출 일괄 조회가 불가능합니다(재무제표 페이지 별도 크롤링 강제).
- **TradingView**: Fundamental Quote에서 최근 확정 실적이 1개 분기(`fq`)만 제공되어 2A(2개 분기) 요건을 구조적으로 충족하지 못합니다.
- **FMP**: 무료 등급에서 분기 파라미터(`period=quarter`)를 호출하면 즉시 **HTTP 402 Payment Required**가 발생하여 0개 분기 확보에 그칩니다.

---

## 5. 부가 메타데이터 및 약관·재배포 제약 비교

1. **asOf 및 Point-in-Time 시계열 부재**:
   - 6개 공급원 전체에서 무료/공개 엔드포인트는 과거 특정 시점의 컨센서스 개정일자(asOf timestamp)를 제공하지 않습니다.
   - `api.nasdaq.com`의 `asOf`는 `null`이며, 실적 발표 시점의 스냅샷 수치만 박제되어 있어 진정한 의미의 Point-in-Time 백테스트가 불가능합니다(Zacks History 유료 테이블 필수).
2. **표본 수 및 보조 통계 제공 여부**:
   - **Nasdaq (Zacks)**: 분기별 애널리스트 수(`noOfEstimates`), 최고치(`highEPSForecast`), 최저치(`lowEPSForecast`), 상향/하향 개정 건수를 충실히 제공합니다.
   - **Finnhub**: 무료 캘린더는 점추정치(`epsEstimate`) 1개만 반환하며, 표본 수와 min/max가 **완전히 결측**됩니다.
3. **약관 및 재배포 라이선스 제약**:
   - **Nasdaq, StockAnalysis, TradingView**: 이용약관상 자동화된 스크래퍼 호출이 명시적으로 금지되어 있어 상용 프로덕션 환경의 안정적 운영이 불가합니다.
   - 정식 HTML 리포트에 분기별 컨센서스를 표기하여 외부에 공개 배포하려면 공식 재배포 권한(Redistribution Rider) 계약이 필수적입니다.

---

## 6. 종합 결론 및 F6-H 채택 적격성 판정

1. **'종목별 사이트 혼합 배제' 및 생산 배제 원칙 하에서의 판정: `전원 불합격 (FAIL)`**:
   - 종목별 체리피킹을 배제하고 단일 공급원 일괄 조회 원칙을 엄격히 적용했을 때, **12개 상장사 전원을 충족하는 생산 공급원은 존재하지 않습니다**.
   - **Nasdaq 공개 샘플의 비생산 참고용 정정**:
     - 기존 조사에 포함된 Nasdaq 9/12 수치는 채택 후보가 아니며, `api.nasdaq.com` 생산 배제 정책에 따라 **공식 생산 후보에서 완전히 제외(Denied)**되었습니다.
     - 기존 Nasdaq 샘플은 기술적 포맷·데이터 구조 비교를 위한 **'비생산 참고용 검증 증거(non-production reference)'**로만 보존되며, 생산 입력·관측 등록·점수 계산에 일체 사용되지 않습니다.
     - 배제 결정 이후 `api.nasdaq.com`에 대한 추가 조회를 일체 수행하지 않습니다.
   - 생산 후보 중 기술적 조회가 가능한 Finnhub 역시 9/12(75.0%)에 그치며, TSMC·Alibaba의 ADR 단위 왜곡 및 SpaceX의 상장 초기 실적 부재로 인해 단일 통일 모드로 채택할 수 없습니다.
2. **F6-H 통일 모드 전환 불가**:
   - F6-N(순수 4E)의 대안으로 F6-H(2A+2E)를 도입하더라도, ADR 및 신규 상장사 문제는 여전히 해결되지 않으며 오히려 2A와 2E 간의 이종 통화/회계 결합 위험만 가중됩니다.
3. **향후 운영 권고**:
   - 무료 웹 엔드포인트를 통한 F6-H 자동 수집 및 채점 승격 시도를 전면 중단합니다.
   - F6 항목은 공식 B2B 유료 데이터 라이선스(Nasdaq Data Link 또는 S&P Global) 체결 및 ADR 단위 변환 게이트가 완비될 때까지 **`pending_data` 원칙을 엄격히 유지**해야 합니다.
4. **불변 원칙 준수**:
   - 본 조사는 독립 분석 스크립트([run_source_comparison.py](file:///C:/Users/noble/orca/workspaces/stock-report-harness/C-13/validation/f6-h-sources-02/run_source_comparison.py)) 및 원자료([raw_source_comparison.json](file:///C:/Users/noble/orca/workspaces/stock-report-harness/C-13/validation/f6-h-sources-02/raw_source_comparison.json))를 통해 완벽히 재현 가능합니다.
   - 프로덕션 채점 코드, 승인 해시 및 12개 검증 테스트는 100% 불변으로 유지되었습니다.
