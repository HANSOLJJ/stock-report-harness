# F6-H 사이트별 독립 공급원 비교 조사 보고서 (R1 보완: 하드코딩 판정 철회 및 Yahoo 증거 검증)

## 0. 철회 및 정정 공지 (Retraction & Correction Notice)

본 보고서는 `msg_609ace096b37` 지침에 따라 이전 커밋(`2bc6274`, `da571bc`)의 오류를 전면 정정하고 공식 철회 표식을 남깁니다.

1. **하드코딩 판정 및 '전 공급원 기술적 불가능' 단정 철회**:
   - 이전 `run_source_comparison.py`가 실제 저장 응답을 파싱하지 않고 코드 분기문(basis/cid)으로 `has_2a`, `has_2e`, `unit_ok` 및 `single_source_f6h_viable=False`를 하드코딩했던 방식을 **공식 철회**합니다.
   - 이에 따라 이전 보고서의 "6개 공급원 전원 불합격 / 최고 75% 기술적 한계"라는 섣부른 일반화 단정을 철회하고, 실제 저장 원자료 분석에 입각한 4단계 분리 검증 체계로 전환합니다.
2. **기존 생성자료의 증거 수준 명시**:
   - 기존 [raw_source_comparison.json](file:///C:/Users/noble/orca/workspaces/stock-report-harness/C-13/validation/f6-h-sources-02/raw_source_comparison.json)은 실제 API 원응답이 아니라 스크립트가 임의 생성한 시뮬레이션 판정 데이터(증거 수준: 하위 시뮬레이션 / 철회됨)였음을 명시합니다.
3. **새 계산의 입력 경로 및 무결성 해시**:
   - 새 계산은 peer worktree(worker)가 실제 수집·저장한 원자료(`worker/validation/f6h-source-batch-10/_raw/yahoo/*.json`, 12건)를 직접 읽어 수행했습니다.
   - worker 원본 파일 덮어쓰기는 일체 없으며, 12개 입력 파일의 SHA-256 해시를 [yahoo_evidence_verification.json](file:///C:/Users/noble/orca/workspaces/stock-report-harness/C-13/validation/f6-h-sources-02/yahoo_evidence_verification.json)에 기록했습니다.
4. **Yahoo 전면 401 차단 단정 철회 및 Valley와 완전 분리**:
   - Yahoo를 "전면 401 차단, 0/12"로 단정했던 것은 사실과 달라 철회합니다. worker 실제 저장 응답 확인 결과 Yahoo는 11/12(값 존재 기준)이며, SPCX는 actual 1건 / estimate 2건입니다.
   - Valley와 Yahoo를 별도 원천으로 분리합니다 (Valley는 v1.5의 동결된 정적 baseline 테이블, Yahoo는 yfinance 저장 응답).
5. **단일 공급원의 다중 엔드포인트 허용**:
   - 단일 공급원 원칙은 '단일 URL 엔드포인트'로 제한하는 것이 아닙니다. 동일 공급사가 제공하는 서로 다른 엔드포인트(예: Finnhub의 `stock/earnings` + `calendar/earnings`, Yahoo의 `earnings_estimate` + `earnings_dates`) 조회를 결합하는 것은 허용됩니다.
6. **일반주 및 ADR/IPO 관련 과도한 단정 철회**:
   - 일반주에 대해 `unit_ok=True`를 자동 지정했던 것을 철회합니다 (발행주식수 및 통화 매핑 미확인 상태로 분리).
   - ADR 통화변환 가능성은 근거 미확인으로 분리합니다.
   - IPO 때문에 상장 전 실적이 없다는 단정, 유료 B2B만 가능하다는 단정을 철회합니다 (미확인 원천은 미검증이지 0/12 불가 판정이 아님).
7. **역할 분담 및 정책 준수**:
   - worker가 Finnhub 분기창을 담당하므로 C-13은 중복 조사하지 않고 Yahoo 전담 검증을 수행합니다.
   - `api.nasdaq.com` 생산 배제 유지 (신규 API/네트워크 호출 일체 없음).
   - 기존 채점 규칙(`v1.5.json`), 승인 결과 해시(`4eb8c7d7`) 100% 불변 보존.
   - 본 작업의 증거로 관계없는 `verify_sources.py`를 사용하지 않고, [verify_yahoo_evidence.py](file:///C:/Users/noble/orca/workspaces/stock-report-harness/C-13/validation/f6-h-sources-02/verify_yahoo_evidence.py)의 5대 직접 검증 테스트를 증거로 채택합니다.

---

## 1. 개요 및 '종목별 사이트 혼합 배제' 원칙

본 보고서는 제안된 **F6-H(하이브리드 F6, 2A+2E)** 모드의 정식 도입 가능성을 **사이트별 공급원 단위**로 독립 검증한 결과입니다.

기존 관측 과정에서 특정 종목은 나스닥, 다른 종목은 핀허브나 FMP에서 취사선택하는 방식(체리피킹)은 공급사 간 집계 기준·통화 단위·회계 조정 방식의 불일치로 인해 공통 방법 문서에서 엄격히 금지되었습니다. 이에 따라 본 조사는 **"하나의 후보 공급원 경로로 12개 상장사 전체를 일괄 조회하여 2A+2E를 온전히 확보할 수 있는가"**를 단일 기준으로 평가했습니다.

---

## 2. 공급원 개요 및 수집 경로

1. **Yahoo (yfinance 저장 응답) [검증 대상 / allowlist 미등재]**:
   - 원천 공급자: LSEG / Refinitiv (I/B/E/S) 기반 Yahoo Finance 엔드포인트.
   - 상태: **v1.6 allowlist 미등재** (상류 API personal use only, 상용 약관 선행 검토 미완료로 채택 후보 아님).
   - 수집 경로: `earnings_estimate` (2E: 0q, +1q) + `earnings_dates` (2A: Reported EPS).
   - 원자료 근거: `worker/validation/f6h-source-batch-10/_raw/yahoo/*.json` (12건).
2. **Finnhub (`finnhub.io`) [worker 전담 영역]**:
   - 원천 공급자: Finnhub 자체 브로커 집계.
   - 상태: v1.6 allowlist 등재.
   - 수집 경로: `stock/earnings`(2A) + `calendar/earnings`(2E).
   - 현황: 값 존재 11/12 (SPCX 결측), 단 분기창 및 4대 기준 검증은 worker가 전담.
3. **Nasdaq (`api.nasdaq.com` / Zacks Consensus) [생산 배제 - 비생산 참고용]**:
   - 상태: **생산 원천 배제 (Denied / Non-production Reference Only)**.
   - robots.txt 및 웹사이트 약관(제2조)에 따라 생산 입력, 관측 등록, F6 점수 계산 사용 전면 배제. 추가 조회 없음.
4. **StockAnalysis (`stockanalysis.com` via `__data.json`) [미검증 후보]**:
   - 원천 공급자: S&P Global Market Intelligence (`spg`) + TipRanks.
   - 수집 경로: `https://stockanalysis.com/stocks/{ticker}/forecast/__data.json`.
5. **Financial Modeling Prep (FMP)**:
   - 상태: 무료 등급에서 `period=quarter` 호출 시 전 종목 HTTP 402 발생. 유료 등급은 미검증.
6. **TradingView (`tradingview.com`) [미검증 후보]**:
   - 원천 공급자: FactSet / TradingView Fundamentals.
7. **Valley (Legacy Static Baseline)**:
   - 원천 공급자: 레거시 고정 테이블 (NVDA 44 등 v1.5 동결 기준선 전용).
   - Yahoo와 분리된 내부 기준선 원천.

---

## 3. 12개 상장사 공급원별 비교 매트릭스

### (1) 공급원별 12개사 종합 비교 매트릭스

| 공급원 | 원천 정책 상태 | 값 존재 (2A/2E) | 분기창 특정 | 통화 일치 | 표본/MinMax | 최종 채점 적격 | 비고 및 주요 판정 |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Yahoo (yfinance 저장)** | **미등재** | **11/12** | **0/12 (특정불가)** | 11/12 | **제공 (n:O, mm:O)** | **0/12 (불가)** | **저장자료 실측**. 값 존재 11/12(SPCX 1A/2E), 분기창 발표일 한계, BABA 통화 불일치, allowlist 미등재. |
| **Finnhub** | 등재 (후보) | **11/12** | worker 전담 | 미검증 | **미제공 (0개, 403)** | **보류** | worker 전담 조사. 값 존재 11/12(SPCX 결측), 4대 기준(회계기준, endpoint 일치, 통화·주식, asOf) 선결 필요. |
| **Nasdaq (api.nasdaq.com)** | **배제 (Denied)** | 9/12 (참고용) | 미검증 | 10/12 | **제공 (애널리스트수)** | **0/12 (배제)** | **생산 원천 배제**. robots.txt 및 약관상 자동 수집 금지. 비생산 참고용으로만 보존. 추가 조회 없음. |
| **StockAnalysis** | 미검증 | 0/12 (2A 부재) | 미검증 | 미검증 | **제공 (S&P Global)** | **0/12 (미검증)** | forecast 엔드포인트 2A 부재. 다중 페이지 크롤링 필요. |
| **FMP (무료)** | 등재 (후보) | 0/12 (402 차단) | 해당없음 | 해당없음 | **제공 (연간 한정)** | **0/12 (무료불가)** | 무료 등급 `period=quarter` 전 종목 HTTP 402 발생. 유료 등급은 미검증. |
| **TradingView** | 미검증 | 0/12 (1Q만) | 미검증 | 미검증 | **미제공** | **0/12 (미검증)** | 최근 1개 분기(fq)만 제공되어 2A 구성 불가. |
| **Valley** | 기준선 전용 | 0/12 (정적) | 해당없음 | USD | **제공 (NVDA 44)** | **0/12 (기준선)** | v1.5 레거시 정적 동결 baseline (Yahoo와 분리). |

---

### (2) 12개사 종목별 Yahoo 실측 및 타 공급원 비교표

| 종목코드 | 기업명 | 시장/단위 | Yahoo (저장 실측) | Finnhub (worker) | Nasdaq (비생산참고) | FMP (무료) |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: |
| **AAPL** | Apple | US 보통주 (USD) | **값 충족 (24A / 2E)** | 값 충족 (4A / 3E) | 참고용 9/12 | 402 차단 |
| **MSFT** | Microsoft | US 보통주 (USD) | **값 충족 (24A / 2E)** | 값 충족 (4A / 3E) | 참고용 9/12 | 402 차단 |
| **GOOGL** | Alphabet | US 보통주 (USD) | **값 충족 (24A / 2E)** | 값 충족 (4A / 3E) | 참고용 9/12 | 402 차단 |
| **AMZN** | Amazon | US 보통주 (USD) | **값 충족 (24A / 2E)** | 값 충족 (4A / 3E) | 참고용 9/12 | 402 차단 |
| **META** | Meta | US 보통주 (USD) | **값 충족 (24A / 2E)** | 값 충족 (4A / 3E) | 참고용 9/12 | 402 차단 |
| **NVDA** | NVIDIA | US 보통주 (USD) | **값 충족 (24A / 2E)** | 값 충족 (4A / 3E) | 참고용 9/12 | 402 차단 |
| **TSLA** | Tesla | US 보통주 (USD) | **값 충족 (24A / 2E)** | 값 충족 (4A / 3E) | 참고용 9/12 | 402 차단 |
| **ORCL** | Oracle | US 보통주 (USD) | **값 충족 (24A / 2E)** | 값 충족 (4A / 4E) | 참고용 9/12 | 402 차단 |
| **PLTR** | Palantir | US 보통주 (USD) | **값 충족 (24A / 2E)** | 값 충족 (4A / 3E) | 참고용 9/12 | 402 차단 |
| **SPCX** | SpaceX | US 보통주 (신규) | **FAIL (실적 1A 부족, 1A/2E)** | **FAIL (1A / 0E)** | 참고용 결측 | 402 차단 |
| **TSM** | TSMC | TW ADR (5:1) | **값 충족 (24A / 2E, USD)** | 값 충족 (TWD 보통주) | 참고용 불일치 | 402 차단 |
| **BABA** | Alibaba | CN ADS (8:1) | **FAIL (전망 통화 CNY ≠ 매매 USD)**| 값 충족 (CNY ADS) | 참고용 불일치 | 402 차단 |

---

## 4. Yahoo 저장 원자료의 4단계 정밀 분리 검증 (C-13 전담)

C-13은 peer worktree(worker)의 실제 저장 응답(`worker/validation/f6h-source-batch-10/_raw/yahoo/*.json`, 12건)을 직접 파싱하여 4단계 정밀 분리 검증을 수행했습니다 (스크립트: [verify_yahoo_evidence.py](file:///C:/Users/noble/orca/workspaces/stock-report-harness/C-13/validation/f6-h-sources-02/verify_yahoo_evidence.py), 데이터: [yahoo_evidence_verification.json](file:///C:/Users/noble/orca/workspaces/stock-report-harness/C-13/validation/f6-h-sources-02/yahoo_evidence_verification.json)).

### 1단계: 원자료 값 존재 검증 (Raw Value Existence: 11/12 통과)
- **11개사 충족**: META, NVDA, GOOGL, MSFT, AMZN, AAPL, ORCL, PLTR, TSLA, TSM, BABA는 `earnings_dates` 내에 2개 이상의 확정 실적(Reported EPS 24건)과 `earnings_estimate` 내 2개의 분기 전망(0q, +1q)을 모두 보유하고 있습니다.
- **SPCX (미달)**: SpaceX는 2026-06-12 상장으로 인해 확정 실적이 1건(`2026-08-04`, Reported EPS -0.09)뿐이며, 11월 발표 예정일(`2026-11-03`, EPS Estimate 0.15)은 아직 실적이 발표되지 않아 Reported EPS가 `null`입니다. 따라서 실제 실적 행수가 1개뿐이므로 2A 요건(최근 확정 2개 분기)을 충족하지 못합니다 (1A + 2E).

### 2단계: 회계분기창 특정 검증 (Quarter Window Specificity: 0/12 특정 불가)
- **발표일과 회계기간의 근본적 괴리**: `earnings_dates`의 일자는 실적 발표일(`Earnings Date`, announcement date)일 뿐, 대상 회계기간의 종료일(Period End Date)이나 분기 레이블(예: 2026Q2, 2026Q3)이 명시되어 있지 않습니다.
- **상대 오프셋 키의 한계**: `earnings_estimate`의 키는 `0q`, `+1q`라는 상대적 오프셋일 뿐, 실제 어느 회계연도 어느 분기인지(예: FY2026 Q3, FY2026 Q4) 특정하는 필드가 없습니다.
- **기업별 결산월 차이**: Apple(9월 결산), Microsoft(6월 결산), Oracle(5월 결산), NVIDIA(1월 결산) 등 기업마다 결산월이 상이하므로, 외부 결산 캘린더 매핑 없이 Yahoo 응답 단독으로는 회계분기창을 객관적으로 특정할 수 없습니다 (0q/+1q만으로 날짜를 임의 추정 확정하지 않음).

### 3단계: 기준 검증 (Basis & Metadata Alignment: 조건부 / 미달)
- **회계 기준 미표기**: Yahoo는 `earnings_estimate` 및 `earnings_dates` 어디에도 GAAP인지 Non-GAAP인지 회계 기준을 명시하지 않습니다.
- **asOf 시점 부재**: 과거 시점별 컨센서스 변경 일자(`asOf` timestamp)가 없어 Point-in-Time 시계열 검증이 불가능합니다.
- **BABA 통화 불일치 (결정적 결격)**: Alibaba(BABA)의 전망 EPS 통화는 `CNY`인 반면 미국 주식 매매 통화는 `USD`입니다. 환율 변환 공식이나 ADR(8:1) 반영 근거가 페이로드에 없어 주가와 직결할 수 없습니다.
- **TSM ADR 통화**: TSM은 전망 통화와 매매 통화가 USD로 표면상 일치하나, ADR 5:1 보통주 변환 기준에 대한 설명이 없습니다.
- **일반주 주식 기준**: 일반주라 하더라도 `unit_ok=True`를 자동 지정하지 않고, 발행주식수 기준이 페이로드에 명시되지 않았음을 비고에 분리 기록했습니다.
- **표본 수 및 Min/Max**: `0q`와 `+1q`에 대해 애널리스트 수(`numberOfAnalysts`), 최저치(`low`), 최고치(`high`)는 12개사 전원에 충실히 제공됩니다.

### 4단계: 최종 채점 가능 상태 (Scoring Eligibility: 0/12 전원 불가)
- **v1.6 allowlist 미등재**: Yahoo는 상류 API의 Personal Use Only 제약 및 상용 약관 선행 검토 미완료로 인해 현재 생산 allowlist에 등재되지 않았습니다.
- **종합 판정**: 값 행수는 11/12개사에서 확보되지만, allowlist 미등재, 회계기준 미표기, 회계분기창 특정 불가, BABA 통화 불일치, SPCX 1A 결측으로 인해 현재 상태에서는 **채점 가능 0/12 (보류/불가)**입니다.

---

## 5. 타 공급원 현황 및 역할 분담 요약

1. **Finnhub (worker 전담 영역)**:
   - worker 조사 결과 값 행수는 11/12 확보(SPCX 결측).
   - 단, 회계기준, `stock/earnings`와 `calendar/earnings`의 기준 일치, 통화·주식 기준, `asOf` 시점 4가지가 모두 비어 있어 선결 과제로 남아 있습니다. worker가 분기창 검증을 전담하고 있으므로 본 보고서에서는 중복 조사를 배제합니다.
2. **Nasdaq (api.nasdaq.com)**:
   - 생산 원천 배제(Denied) 정책을 엄격히 유지하며, 신규 API 호출을 일체 수행하지 않습니다.
3. **FMP 및 미검증 원천**:
   - FMP 무료 등급은 `period=quarter`가 유료 파라미터라 HTTP 402로 전 종목 불가하지만, 유료 등급이나 타 미확인 원천은 '미검증' 상태이지 기술적 원천 불가가 아닙니다.

---

## 6. 종합 결론

1. **공급원별 값 존재는 최고 11/12 수준 (Finnhub 11/12, Yahoo 11/12)**:
   - 이전 보고서의 "최고 75%(9/12) 한계" 단정을 공식 철회하며, 실제 저장 원자료 기준으로 11개사에서 2A+2E 값 행수가 확보됨을 확인했습니다.
   - 막히는 종목은 공통적으로 신규 상장사 SPCX(2026-06-12 상장, 확정 실적 1건으로 2A 미달)입니다.
2. **값 존재와 분기창·기준 검증의 명확한 분리**:
   - 값 행수가 존재하더라도, 회계분기창 특정(발표일 vs 회계기간), 회계기준 명시, `asOf` 시점, 통화 일치(BABA CNY 불일치)가 해소되지 않으면 F6-H 자동 채점으로 연결할 수 없습니다.
3. **Yahoo 채점 채택 불가**:
   - Yahoo는 allowlist 미등재, 약관 검토 선행 필요, 회계기준 및 회계분기 미특정, BABA 통화 불일치로 인해 공식 채점 후보에서 제외됩니다.
4. **운영 권고**:
   - F6-H는 단일 공급원 확보 및 선결 기준(회계기준, 통화/주식 단위, asOf, 분기창)이 공식 확정될 때까지 **`pending_data`를 엄격히 유지**합니다.
   - 기존 점수, 채점 규칙(`v1.5.json`), 승인 결과 해시(`4eb8c7d7`)는 100% 불변으로 보존되었습니다.

---

## 7. 재현 방법 및 직접 검증 테스트

본 보고서의 Yahoo 4단계 검증은 네트워크 호출 없이 저장 원자료를 직접 파싱하는 스크립트로 100% 재현 가능합니다.
(지침에 따라 관계없는 `verify_sources.py` 대신 직접 관련 검증 스크립트를 증거로 사용합니다.)

```bash
# Yahoo 저장 원자료 4단계 분리 검증 및 5대 자체 검증 테스트 실행
python validation/f6-h-sources-02/verify_yahoo_evidence.py
```

### 5대 직접 검증 테스트 통과 결과:
- **Test 1 PASS**: 12개사 전체 원자료 파일 존재 및 SHA-256 해시 기록 확인 완료.
- **Test 2 PASS**: Stage 1 값 존재 11/12 통과 및 SPCX actual 1 / estimate 2 검증 완료.
- **Test 3 PASS**: Stage 2 발표일 vs 회계분기 미구분 및 상대키(0q/+1q) 한계 0/12 분리 검증 완료.
- **Test 4 PASS**: Stage 3 BABA 통화 불일치(CNY vs USD) 및 메타데이터 정합성 검증 완료.
- **Test 5 PASS**: Stage 4 Yahoo allowlist 미등재 및 채점 가능 0/12 확인 완료.
- **산출물**: `validation/f6-h-sources-02/yahoo_evidence_verification.json` (입력 파일 경로, SHA-256, 4단계 검증 결과 수록).

