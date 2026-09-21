# F6-H 사이트별 독립 공급원 비교 조사 보고서 (R3 보완: 통화 충돌·financialCurrency·전 행 분기창·동적notes 반영)

## 0. 철회 및 정정 공지 (Retraction & Correction Notice)

본 보고서는 `msg_609ace096b37`, `msg_8fd06ac3ff02`, `msg_734e6968ba5f` 지침에 따라 이전 커밋들의 오류를 전면 정정하고 공식 철회 표식을 남깁니다.

1. **R2-01~04 통과 확인 및 R3 보완**:
   - R2-01(원자료 거래통화 분리), R2-02(단계 간 판정 변수 연결 및 요약-상세 일치), R2-03(유한수치 검증 및 음수 EPS 보존), R2-04(철회 수치 배제 및 보고서 정정) 4건은 독립 재현 검증을 거쳐 통과 확정되었습니다.
   - R3-01(trade_currency_status의 Stage 3·4 반영), R3-02(회계기간 전 행 검증), R3-03(basis.financialCurrency 파싱 및 TSM 불일치 반영), R3-04(2A 통화미표기 분리 및 estimate_currency_match 명시), R3-05(Stage 2 동적 notes 생성)를 추가 반영했습니다.
2. **하드코딩 판정 및 '전 공급원 기술적 불가능' 단정 철회**:
   - 이전 `run_source_comparison.py`가 실제 저장 응답을 파싱하지 않고 코드 분기문(basis/cid)으로 `has_2a`, `has_2e`, `unit_ok` 및 `single_source_f6h_viable=False`를 하드코딩했던 방식을 **공식 철회**합니다.
   - 실제 저장 원자료 분석에 입각한 4단계 정밀 분리 검증 체계로 전환했습니다.
3. **기존 생성자료의 증거 수준 명시**:
   - 기존 [raw_source_comparison.json](file:///C:/Users/noble/orca/workspaces/stock-report-harness/C-13/validation/f6-h-sources-02/raw_source_comparison.json)은 실제 API 원응답이 아니라 스크립트가 임의 생성한 시뮬레이션 판정 데이터(증거 수준: 하위 시뮬레이션 / 철회됨)였음을 명시합니다.
4. **철회된 수치(Nasdaq 9/12·통화 10/12, StockAnalysis 0/12)의 완전 배제**:
   - 독립 근거가 없는 이전 시뮬레이션 수치(Nasdaq 9/12, 통화 10/12, StockAnalysis 0/12)를 공식 철회 및 미검증으로 처리합니다. 비생산 참고 표시는 증거를 복구하지 않으므로 본 보고서의 비교표에서 해당 수치를 전면 배제합니다.
5. **새 계산의 입력 경로 및 무결성 해시**:
   - 새 계산은 peer worktree(worker)가 실제 수집·저장한 원자료(`worker/validation/f6h-source-batch-10/_raw/yahoo/*.json`, 12건)를 직접 읽어 수행했습니다.
   - worker 원본 파일 덮어쓰기는 일체 없으며, 12개 입력 파일의 SHA-256 해시를 [yahoo_evidence_verification.json](file:///C:/Users/noble/orca/workspaces/stock-report-harness/C-13/validation/f6-h-sources-02/yahoo_evidence_verification.json)에 기록했습니다.
6. **Yahoo 전면 401 차단 단정 철회 및 Valley와 완전 분리**:
   - Yahoo를 "전면 401 차단, 0/12"로 단정했던 것은 사실과 달라 철회합니다. worker 실제 저장 응답 확인 결과 Yahoo는 1단계 값 존재 기준 11/12(유한 수치 충족)이며, SPCX는 저장자료 내 1A / 2E 관측입니다.
   - Valley와 Yahoo를 별도 원천으로 분리합니다 (Valley는 v1.5의 동결된 정적 baseline 테이블, Yahoo는 yfinance 저장 응답).
7. **단일 공급원의 다중 엔드포인트 허용 및 캘린더 참조 구분**:
   - 동일 공급사가 제공하는 서로 다른 엔드포인트(예: Yahoo의 `earnings_estimate` + `earnings_dates`) 조회를 결합하는 것은 허용됩니다.
   - 회계기간 확인을 위한 공식 캘린더 참조는 서로 다른 브로커 컨센서스를 혼합하는 EPS 공급원 혼합과는 구별됩니다.
8. **SPCX, BABA, TSM 판정 정밀화**:
   - SPCX의 확정 실적 1건은 제공된 저장자료 내 관측 결과로 한정하며, 상장으로 인한 인과 단정을 배제합니다.
   - BABA는 1단계 값 존재(24A / 2E)는 통과하며, 3단계 전망 통화 불일치(CNY vs USD) 및 재무통화 불일치(CNY vs USD)로 인해 기준 검증에서 미달함을 분리합니다.
   - TSM은 1단계 값 존재(24A / 2E)는 통과하나, `basis.financialCurrency`가 본사 통화인 TWD로 거래통화 USD와 상이하며 페이로드 내 환산 근거가 부재하여 통화 일치에서 제외(10/12)합니다.
9. **Yahoo allowlist 미등재 및 권리 검토 명확화**:
   - Yahoo의 v1.6 allowlist 미등재 사실과 개인 사용 시 필요한 권리 검토를 명확히 구분합니다. 본 검토가 상업적 배포를 전제하거나 새로운 법적 금지를 확정한 것은 아닙니다.
10. **정책 준수 및 증거 채택**:
    - worker가 Finnhub 분기창을 담당하므로 C-13은 중복 조사하지 않고 Yahoo 전담 검증을 수행합니다.
    - `api.nasdaq.com` 생산 배제를 유지하며 신규 API/네트워크 호출은 일체 없습니다.
    - 기존 채점 규칙(`v1.5.json`), 승인 결과 해시(`4eb8c7d7`)는 100% 불변 보존합니다.
    - 본 작업의 증거로 관계없는 `verify_sources.py`를 사용하지 않고, [verify_yahoo_evidence.py](file:///C:/Users/noble/orca/workspaces/stock-report-harness/C-13/validation/f6-h-sources-02/verify_yahoo_evidence.py)의 7대 직접 검증 테스트를 증거로 채택합니다.

---

## 1. 개요 및 '종목별 사이트 혼합 배제' 원칙

본 보고서는 제안된 **F6-H(하이브리드 F6, 2A+2E)** 모드의 정식 도입 가능성을 **사이트별 공급원 단위**로 독립 검증한 결과입니다.

기존 관측 과정에서 특정 종목은 나스닥, 다른 종목은 핀허브나 FMP에서 취사선택하는 방식(체리피킹)은 공급사 간 집계 기준·통화 단위·회계 조정 방식의 불일치로 인해 공통 방법 문서에서 엄격히 금지되었습니다. 이에 따라 본 조사는 **"하나의 후보 공급원 경로로 12개 상장사 전체를 일괄 조회하여 2A+2E를 온전히 확보할 수 있는가"**를 단일 기준으로 평가했습니다.

---

## 2. 공급원 개요 및 수집 경로

1. **Yahoo (yfinance 저장 응답) [검증 대상 / allowlist 미등재]**:
   - 원천 공급자: LSEG / Refinitiv (I/B/E/S) 기반 Yahoo Finance 엔드포인트.
   - 상태: **v1.6 allowlist 미등재** (상류 API personal use 및 상용 권리 검토 선행 필요).
   - 수집 경로: `earnings_estimate` (2E: 0q, +1q) + `earnings_dates` (2A: Reported EPS).
   - 원자료 근거: `worker/validation/f6h-source-batch-10/_raw/yahoo/*.json` (12건).
2. **Finnhub (`finnhub.io`) [worker 전담 영역]**:
   - 원천 공급자: Finnhub 자체 브로커 집계.
   - 상태: v1.6 allowlist 등재.
   - 수집 경로: `stock/earnings`(2A) + `calendar/earnings`(2E).
   - 현황: 값 존재 11/12 (SPCX 결측), 단 분기창 및 4대 기준 검증은 worker가 전담.
3. **Nasdaq (`api.nasdaq.com` / Zacks Consensus) [생산 배제 / 수치 철회]**:
   - 상태: **생산 원천 배제 (Denied / 수치 철회)**.
   - robots.txt 및 웹사이트 약관(제2조)에 따라 생산 입력 전면 배제. 기존 시뮬레이션 수치는 독립 근거 부재로 철회되었으며 추가 조회가 없습니다.
4. **StockAnalysis (`stockanalysis.com`) [미검증 후보 / 수치 철회]**:
   - 원천 공급자: S&P Global Market Intelligence (`spg`) + TipRanks.
   - 이전 0/12 판정은 시뮬레이션 수치로 철회되었으며 현재 미검증 상태입니다.
5. **Financial Modeling Prep (FMP)**:
   - 상태: 무료 등급에서 `period=quarter` 호출 시 전 종목 HTTP 402 발생. 유료 등급은 미검증.
6. **TradingView (`tradingview.com`) [미검증 후보]**:
   - 원천 공급자: FactSet / TradingView Fundamentals. 미검증 상태.
7. **Valley (Legacy Static Baseline)**:
   - 원천 공급자: 레거시 고정 테이블 (NVDA 44 등 v1.5 동결 기준선 전용).
   - Yahoo와 분리된 내부 기준선 원천.

---

## 3. 12개 상장사 공급원별 비교 매트릭스

### (1) 공급원별 12개사 종합 비교 매트릭스

| 공급원 | 원천 정책 상태 | 값 존재 (2A/2E) | 분기창 특정 | 통화 일치 | 표본/MinMax | 최종 채점 적격 | 비고 및 주요 판정 |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Yahoo (yfinance 저장)** | **미등재** | **11/12 (유한수치)** | **0/12 (원자료단독 불가)** | **10/12 (TSM·BABA 불일치)** | **제공 (n:O, mm:O)** | **0/12 (미적격)** | **저장자료 실측**. 값 존재 11/12(SPCX 1A/2E 관측), 전 행 발표일 한계, TSM/BABA 통화 불일치, allowlist 미등재. |
| **Finnhub** | 등재 (후보) | **11/12** | worker 전담 | 미검증 | **미제공 (0개, 403)** | **보류** | worker 전담 조사. 4대 기준(회계기준, endpoint 일치, 통화·주식, asOf) 선결 필요. |
| **Nasdaq (api.nasdaq.com)** | **배제 (Denied)** | **철회 (독립근거 부재)** | 미검증 | **철회 (미검증)** | **철회 (미검증)** | **0/12 (배제)** | **생산 원천 배제**. 약관상 자동 수집 금지. 기존 9/12·10/12 수치는 독립 근거 부재로 철회함. |
| **StockAnalysis** | 미검증 | **미검증 (수치 철회)** | 미검증 | 미검증 | 미검증 | **0/12 (미검증)** | 미검증 후보. 이전 0/12 시뮬레이션 수치 철회. 다중 페이지 크롤링 여부 미검증. |
| **FMP (무료)** | 등재 (후보) | 0/12 (402 차단) | 해당없음 | 해당없음 | 미제공 (연간 한정) | **0/12 (무료불가)** | 무료 등급 `period=quarter` 전 종목 HTTP 402 발생. 유료 등급은 미검증. |
| **TradingView** | 미검증 | 미검증 | 미검증 | 미검증 | 미검증 | **0/12 (미검증)** | 2A 구성 및 과거 시계열 제공 여부 미검증. |
| **Valley** | 기준선 전용 | 해당없음 (정적) | 해당없음 | USD | 제공 (NVDA 44) | **0/12 (기준선)** | v1.5 레거시 정적 동결 baseline (Yahoo와 분리). |

---

### (2) 12개사 종목별 Yahoo 실측 및 타 공급원 비교표

| 종목코드 | 기업명 | 시장/단위 | Yahoo (저장 실측) | Finnhub (worker) | Nasdaq (생산배제/수치철회) | FMP (무료) |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: |
| **AAPL** | Apple | US 보통주 (USD) | **1단계 통과 (24A / 2E)** | 값 충족 (4A / 3E) | 철회 / 미검증 | 402 차단 |
| **MSFT** | Microsoft | US 보통주 (USD) | **1단계 통과 (24A / 2E)** | 값 충족 (4A / 3E) | 철회 / 미검증 | 402 차단 |
| **GOOGL** | Alphabet | US 보통주 (USD) | **1단계 통과 (24A / 2E)** | 값 충족 (4A / 3E) | 철회 / 미검증 | 402 차단 |
| **AMZN** | Amazon | US 보통주 (USD) | **1단계 통과 (24A / 2E)** | 값 충족 (4A / 3E) | 철회 / 미검증 | 402 차단 |
| **META** | Meta | US 보통주 (USD) | **1단계 통과 (24A / 2E)** | 값 충족 (4A / 3E) | 철회 / 미검증 | 402 차단 |
| **NVDA** | NVIDIA | US 보통주 (USD) | **1단계 통과 (24A / 2E)** | 값 충족 (4A / 3E) | 철회 / 미검증 | 402 차단 |
| **TSLA** | Tesla | US 보통주 (USD) | **1단계 통과 (24A / 2E)** | 값 충족 (4A / 3E) | 철회 / 미검증 | 402 차단 |
| **ORCL** | Oracle | US 보통주 (USD) | **1단계 통과 (24A / 2E)** | 값 충족 (4A / 4E) | 철회 / 미검증 | 402 차단 |
| **PLTR** | Palantir | US 보통주 (USD) | **1단계 통과 (24A / 2E)** | 값 충족 (4A / 3E) | 철회 / 미검증 | 402 차단 |
| **SPCX** | SpaceX | US 보통주 (저장자료 관측) | **1단계 미달 (1A / 2E 관측)** | FAIL (1A / 0E) | 철회 / 미검증 | 402 차단 |
| **TSM** | TSMC | TW ADR (5:1) | **1단계 통과 [단 3단계 재무통화 TWD 불일치]** | 값 충족 (TWD 보통주) | 철회 / 미검증 | 402 차단 |
| **BABA** | Alibaba | CN ADS (8:1) | **1단계 통과 [단 3단계 전망통화 CNY 불일치]** | 값 충족 (CNY ADS) | 철회 / 미검증 | 402 차단 |

---

## 4. Yahoo 저장 원자료의 4단계 정밀 분리 검증 (C-13 전담)

C-13은 peer worktree(worker)의 실제 저장 응답(`worker/validation/f6h-source-batch-10/_raw/yahoo/*.json`, 12건)을 직접 파싱하여 4단계 정밀 분리 검증을 수행했습니다 (스크립트: [verify_yahoo_evidence.py](file:///C:/Users/noble/orca/workspaces/stock-report-harness/C-13/validation/f6-h-sources-02/verify_yahoo_evidence.py), 데이터: [yahoo_evidence_verification.json](file:///C:/Users/noble/orca/workspaces/stock-report-harness/C-13/validation/f6-h-sources-02/yahoo_evidence_verification.json)).

### 1단계: 원자료 값 존재 검증 (Raw Value Existence: 11/12 통과)
- **11개사 충족**: META, NVDA, GOOGL, MSFT, AMZN, AAPL, ORCL, PLTR, TSLA, TSM, BABA는 `earnings_dates` 내에 2개 이상의 확정 실적(Reported EPS 24건)과 `earnings_estimate` 내 2개의 분기 전망(0q, +1q)을 모두 보유하고 있으며 유한 수치 검증을 통과했습니다.
- **이력 내 확정 분기 존재와 연속 분기창의 구분 (R3-04)**: 1단계의 `has_2a`는 전체 이력 데이터 내에 유효한 확정 실적 분기가 2개 이상 존재하는지를 평가하며, 최근 연속 2개 분기의 특정 여부는 2단계 회계분기창의 검증 대상입니다.
- **BABA 1단계 통과**: BABA는 값 존재 단계(1단계)에서 24개의 확정 실적 행과 2개의 유효한 분기 전망 행을 온전히 보유하고 있어 1단계를 정상 통과합니다.
- **SPCX (미달)**: SPCX는 제공된 저장자료 내에서 확정 실적이 1건(`2026-08-04`, Reported EPS -0.09, 유효 음수 실적) 관측되며, 11월 발표 예정 행(`2026-11-03`, EPS Estimate 0.15)은 실적이 아직 발표되지 않아 Reported EPS가 `null`입니다. 따라서 저장자료 내 확정 실적 행이 1개(중복 제거 후에도 1개 분기)뿐이므로 2A 최소 요건에 미달합니다 (1A + 2E). 본 판정은 상장으로 인한 인과 단정을 배제하고 저장자료 관측 결과로 한정합니다.

### 2단계: 회계분기창 특정 검증 (Quarter Window Specificity: 0/12 특정 불가, R3-02 & R3-05)
- **전 행 교차 검증 원칙**: 회계기간 검증은 단일 행에만 의존하지 않고, 2A 확정 실적 행 전체(Reported EPS가 유효한 행들)와 2E 전망 행(0q, +1q) 전체를 교차 검증합니다.
- **미발표 예정행 배제 및 conflict 감지**: 실적이 아직 발표되지 않은 예정 행(Reported EPS null)에만 기간 정보가 있거나, 일부 행에만 기간 정보가 있고 타 행에 누락된 경우 통과가 아닌 `conflict` 상태를 부여하고 기각합니다.
- **상대 오프셋 키의 한계**: `earnings_estimate`의 키는 `0q`, `+1q`라는 상대적 오프셋일 뿐, 실제 어느 회계연도 어느 분기인지 특정하는 필드가 없습니다.
- **동적 notes 연동 (R3-05)**: Stage 2의 notes는 고정 문자열이 아니며, 입력 자료의 실제 상태(missing, conflict, insufficient_rows 등)에 따라 동적으로 생성됩니다.
- **외부 캘린더 참조와의 구별**: 회계기간 확인을 위해 회사의 공식 실적 발표 캘린더나 공시 일정을 참조하는 것은 허용되며, 이는 서로 다른 브로커 컨센서스를 혼합하는 EPS 공급원 혼합과는 명확히 구별됩니다.

### 3단계: 기준 검증 (Basis & Metadata Alignment: 0/12 전원 미달, R3-01, R3-03, R3-04)
- **원자료 거래통화 충돌 시 엄격한 탈락 (R3-01)**: `trade_currency_status`가 참조 통화(USD)와 충돌(conflict)하거나 누락(missing)된 경우, `currency_match=False` 및 `stage3_pass=False`가 도출됩니다. 원자료 거래통화와 전망 통화가 동시에 임의 통화(예: KRW)로 일치하더라도 참조 통화와의 conflict 상태로 인해 검사를 통과할 수 없습니다.
- **본사 재무통화(financialCurrency) 파싱 및 TSM 불일치 (R3-03)**: `basis.financialCurrency`를 함께 파싱하여 거래통화와의 정합성을 검증합니다. TSM의 경우 `basis.currency=USD`, `0q.currency=USD`이지만 `basis.financialCurrency=TWD`입니다. 페이로드 내에 TWD와 USD 간 환산 공식이나 ADR 5:1 반영 근거가 부재하므로, TSM은 통화 일치에서 제외(불일치) 처리되며 이에 따라 종합 통화 일치는 10/12가 됩니다.
- **BABA 통화 불일치**: Alibaba(BABA)는 전망 통화(`CNY`) 및 재무통화(`CNY`)가 거래통화(`USD`)와 모두 불일치하여 통화 검증에서 탈락합니다.
- **2A Reported EPS 통화 필드 부재 명시 (R3-04)**: `earnings_dates`의 Reported EPS에는 통화 필드가 전혀 표기되어 있지 않음을 `actual_currency_status: unspecified_in_payload`로 명시하고, 전망치 통화 일치(`estimate_currency_match`)와 구분하여 다룹니다.
- **회계 기준 및 asOf 시점 부재**: GAAP/Non-GAAP 명시 부재 및 Point-in-Time 시계열 검증용 `asOf` 타임스탬프 부재로 12개사 전원 3단계 미달입니다.

### 4단계: 최종 채점 가능 상태 (Scoring Eligibility: 0/12 전원 불가)
- **근본적 기술 부적격 (Technical Ineligibility: 회계분기창 0/12 및 전망 2분기 한계)**:
  - Yahoo의 공식 F6 원천 부적격 사유는 allowlist 미등재나 약관 이전의 **근본적인 기술적 제약**입니다.
  - 첫째, `earnings_dates`가 실적 발표일일 뿐 대상 회계기간 종료일이 없고 `0q`/`+1q`가 상대 오프셋에 불과하여 **원자료 단독 회계분기창 특정 불가(0/12)**입니다.
  - 둘째, 전망치가 `0q`와 `+1q`로 **최대 2개 분기만 제공**되므로, 4개 분기 연속 컨센서스를 요구하는 F6 요건을 구조적으로 충족하지 못합니다.
  - 사용자가 프로젝트 범위를 'personal / internal only'로 확정하여 약관상 외부 배포 부담이 소멸되었더라도, 이러한 데이터 스키마의 기술적 한계로 인해 Yahoo가 F6 채점 원천으로 부적격하다는 판정은 변함없이 유지됩니다.
- **v1.6 allowlist 및 권리 상태**: Yahoo는 현재 생산 allowlist에 미등재 상태이나, 이는 상기 기술적 부적격에 부차적인 요인입니다.
- **종합 판정**: 값 행수는 11/12개사에서 확보되지만, 회계분기창 특정 불가(0/12), 전망 분기 2개 한계, TSM/BABA 통화 불일치, SPCX 1A 미달 등 기술적 결격 사유로 인해 F6 공식 채점에 부적격(0/12)입니다.

---

## 5. 타 공급원 현황 및 역할 분담 요약

1. **Finnhub (worker 전담 영역)**:
   - worker 조사 결과 값 행수는 11/12 확보(SPCX 결측).
   - 단, 회계기준, `stock/earnings`와 `calendar/earnings`의 기준 일치, 통화·주식 기준, `asOf` 시점 4가지가 선결 과제로 남아 있습니다. worker가 분기창 검증을 전담하고 있으므로 본 보고서에서는 중복 조사를 배제합니다.
2. **Nasdaq (api.nasdaq.com)**:
   - 생산 원천 배제(Denied) 정책을 엄격히 유지하며, 신규 API 호출을 일체 수행하지 않습니다. 이전 시뮬레이션 수치는 철회되었습니다.
3. **FMP 및 미검증 원천**:
   - FMP 무료 등급은 `period=quarter`가 유료 파라미터라 HTTP 402로 전 종목 불가하지만, 유료 등급이나 타 미확인 원천은 '미검증' 상태이지 기술적 원천 불가가 아닙니다.

---

## 6. 종합 결론

1. **공급원별 값 존재는 최고 11/12 수준 (Finnhub 11/12, Yahoo 11/12)**:
   - 이전 보고서의 "최고 75%(9/12) 한계" 단정을 공식 철회하며, 실제 저장 원자료 기준으로 11개사에서 2A+2E 유한 수치 행수가 확보됨을 확인했습니다.
   - 막히는 종목은 공통적으로 SPCX(저장자료 관측상 확정 실적 1건으로 2A 미달)입니다.
2. **값 존재와 분기창·기준 검증의 명확한 분리**:
   - 값 행수가 존재하더라도, 원자료 단독 회계분기창 특정 한계, 회계기준 미표기, `asOf` 시점 부재, 통화 불일치(BABA CNY, TSM TWD 불일치)가 해소되지 않으면 F6-H 자동 채점으로 연결할 수 없습니다.
3. **Yahoo 채점 채택 불가 (기술적 사유 우선)**:
   - Yahoo는 allowlist나 약관 이전의 근본적 기술 제약, 즉 **회계분기창 특정 불가(0/12)**와 **전망치 2분기(`0q`, `+1q`) 한계**로 인해 공식 채점 후보에서 원천 배제됩니다. 사용자의 personal/internal 범위 확정으로도 이 기술적 배제 결론은 불변합니다.
4. **운영 권고**:
   - F6-H는 단일 공급원 확보 및 선결 기준(회계기준, 통화/주식 단위, asOf, 분기창)이 공식 확정될 때까지 **`pending_data`를 엄격히 유지**합니다.
   - 기존 점수, 채점 규칙(`v1.5.json`), 승인 결과 해시(`4eb8c7d7`)는 100% 불변으로 보존되었습니다.

---

## 7. 재현 방법 및 직접 검증 테스트

본 보고서의 Yahoo 4단계 검증은 네트워크 호출 없이 저장 원자료를 직접 파싱하는 스크립트로 100% 재현 가능합니다. 스크립트는 상대경로 기본값을 사용하므로 임시 경로에서도 안전하게 실행할 수 있습니다.

```bash
# Yahoo 저장 원자료 4단계 분리 검증 및 7대 자체 검증 테스트 실행
python validation/f6-h-sources-02/verify_yahoo_evidence.py

# 피어 워크트리(설계진행) 독립 재검증 스크립트 실행 (동일 재현)
python ../설계진행/validation/recheck_f6h_sources02_r2.py validation/f6-h-sources-02 --raw ../worker/validation/f6h-source-batch-10/_raw/yahoo
```

### 7대 직접 검증 테스트 통과 결과:
- **Test 1 PASS**: 12개사 전체 원자료 파일 존재 및 SHA-256 해시 대조 확인 완료.
- **Test 2 PASS**: 동일 입력 반복 2회 실행 결과 및 일관성(결정론적 재현) 확인 완료.
- **Test 3 PASS (R2-01 & R3-01)**: 통화 변경/누락 및 거래·전망 동시 변이(KRW) 시 conflict 감지 및 match=False 검증 완료.
- **Test 4 PASS (R2-03)**: 비수치 문자열('NOT_A_NUMBER'), bool(True), NaN 기각 및 음수 EPS(-0.09) 정상 유효 수치 보존 확인 완료.
- **Test 5 PASS (R2-02)**: 중복 실적 행 삽입 시 행수(actual_count)와 중복제거 분기수(unique_actual_quarters) 구분 및 요약-상세 일치 확인 완료.
- **Test 6 PASS (R3-02 & R3-05)**: 회계기간 필드 부분 부여(P7/P8) 입력 변이 대응, conflict 판정 및 입력 상태에 따른 동적 notes 변경 확인 완료.
- **Test 7 PASS (R3-03, R3-04 & R2-04)**: TSM financialCurrency(TWD) 불일치 판정, 2A 통화미표기 분리, BABA 분리 및 10/12 실측 검증 완료.
- **산출물**: `validation/f6-h-sources-02/yahoo_evidence_verification.json` (입력 파일 경로, SHA-256, 4단계 검증 결과 수록).



