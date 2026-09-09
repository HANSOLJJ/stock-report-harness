# C13-SOURCE-03: 컨센서스 기준 검증 및 비상장사 근거 보완 보고서 (v4.1 독립 재검토 반영본)

- **문서 버전**: v4.1 (설계진행 독립 재검토 `c13-source03-review.md` S03-01~05 요구사항 전면 반영본)
- **작업 ID**: `C13-SOURCE-03` (선행: `C13-SOURCE-02`)
- **작성일자**: 2026-09-09
- **수행 주체**: C-13 worktree Antigravity 담당
- **참조 문서**:
  - `설계진행` 재검토 통보: `msg_cf996e830c0f` 및 `validation/c13-source03-review.md` (커밋 `48984c8`)
  - `설계진행` 12개사 원자료 검증: `validation/recheck_nasdaq_12.py`
  - `validation/consensus-source-2026-09-09/verify_sources.py` (12개 단위 테스트 검증기)
  - `validation/consensus-source-2026-09-09/evidence.json` (기계 판독용 정합성 데이터)

---

## 1. 개요 및 S03-01~05 재검토 보완 핵심

본 보고서는 설계진행의 독립 재검토(`c13-source03-review.md`) 지적사항(S03-01~05)에 따라, 연구자의 주관적 추정이나 과도한 단정을 배제하고 **자료 확보(Data Fulfillment: 4/4 완료)**와 **메타데이터 검증(Metadata Verification: 미확인)**을 명확히 분리하여, **TSMC와 Alibaba의 채점 적격성을 보류(`scoring_eligible: False`)로 유지**하며 **비상장사(Anthropic, OpenAI)의 원문 명칭 및 출처 범위를 원칙에 맞게 정정한 최종 보고서**이다.

### 1.1 S03-01~05 조치 내역 요약

1. **S03-01: Zacks 계열(BNRI vs Street) 및 회계 기준 추정 단정 철회**:
   - Zacks 공식 FAQ(`https://zacksdata.com/consensus/faq/`)에 따르면 Zacks는 BNRI(Before Non-Recurring Items)와 Street 두 계열의 컨센서스를 모두 제공함.
   - Nasdaq Earnings Forecast API 응답상 `EPS*` 필드가 BNRI인지 Street인지, 희석 여부 및 세부 조정 항목이 무엇인지 직결하는 원문 URL이나 각주 보존본이 부재함.
   - 따라서 추측으로 BNRI 또는 Street로 단정하지 않고 **회계 기준 미확인(`unconfirmed_series / unconfirmed_standard`)**으로 명시함.
2. **S03-02: `asOf: null` 일일 동적갱신 단정 철회 및 시점 분리**:
   - Nasdaq JSON의 `asOf: null` 발생 원인을 일일 동적 갱신으로 단정하던 서술을 철회하고 **원인 미확인(`unknown`)**으로 기록함.
   - 공급사 기준시각(`unknown`), 당사 수집시각(`2026-09-09T02:11:00Z`), 파일 생성시각을 엄격히 분리함.
3. **S03-03: 주가 통화 기반 EPS 단위 확정 철회 및 채점 보류 유지**:
   - 미국 거래소 직상장 증서(ADR/ADS) 및 주가 거래 통화(USD)가 확인되었으나, 이것만으로 EPS 필드 자체의 통화와 분모 단위(주당)까지 입증되지 않음을 인정함.
   - 직접적인 필드 메타데이터 부재에 따라 `currency_confirmed=False`, `share_basis_confirmed=False`로 정정함.
   - 이에 따라 TSMC ($18.87) 및 Alibaba ($7.57) 모두 **채점 보류 (`scoring_eligible: False`, `scoring_status: "pending_basis_metadata_verification"`)를 확고히 유지함.**
4. **S03-04: Anthropic 공식 표현 'run-rate revenue' 보존 및 임의 산식 삭제**:
   - 공식 발표문 본문의 지표명은 **"run-rate revenue"** (> $47B in May)이며, SaaS 연간반복매출(ARR)로 단정하지 않음.
   - 기존의 "주간/월간 매출에 12를 곱한다"는 임의 산식 설명을 전면 삭제하고, **"연율화 산식 미공개 (`unspecified_formula` / `unknown`)"**로 명시함.
   - 연간 실현 매출, TTM, 미래 매출 전망과 엄격히 분리하며, 조사 범위 내 미확보(`None / unobtained`)로 기록함.
5. **S03-05: Anthropic 원장 미완성 범위 명시, SEC draft S-1 실사 철회, 2차 보도 관측 배제**:
   - Anthropic 자금조달 원장 중 세부 중간 라운드(Series D~G 등)의 개별 공식 출처 부재 및 미상세 공시 범위를 명시함.
   - 확인된 주요 라운드(A, B, C, H)만 개별 출처와 함께 표기하고, 누적 합계는 **`unconfirmed_ledger`** 유지.
   - 이전 작성본의 "SEC draft S-1 공시 대조 실사" 표기는 직접 accession/URL 부재로 공식 철회 및 삭제함.
   - Series H $65B 중 기존 약정 $15B 차감액 $50B는 본문 문구에 기반한 **"단순 산술 추론(arithmetic deduction)"**이며 현금 납입액 검증과 구별함.
   - 직접 기사 URL이 없는 수치(OpenAI $40B, $3.7B, $100B, Anthropic IPO 목표 시총 $2.0T)는 공식 검증된 관측치로 사용하지 않음(`unverified_article_url`).
   - 실현 매출 및 전망치 미확보는 당사 조사 범위 내에서의 확인 결과이며, 전 세계적 자료 부재로 확대 단정하지 않음.

---

## 2. 상장사 4분기 관측치 및 메타데이터 검증 상세 (TSMC & Alibaba)

### 2.1 Nasdaq 컨센서스 메타데이터 실사 결과

| 항목 | TSMC (`TSM`) | Alibaba (`BABA`) | 실사 판정 및 비고 |
|---|---|---|---|
| **원천 공급사** | Zacks Investment Research | Zacks Investment Research | Nasdaq 제휴 공급사 확인 |
| **컨센서스 계열** | **미확인 (`unconfirmed_series`)** | **미확인 (`unconfirmed_series`)** | Zacks 공식상 BNRI/Street 존재하나 필드 직결 각주 부재 |
| **회계 기준** | **미확인 (`unconfirmed_standard`)** | **미확인 (`unconfirmed_standard`)** | Non-GAAP 조정 여부 직접 필드 메타데이터 부재 |
| **EPS 통화** | **미확인 (`unconfirmed_currency`)** | **미확인 (`unconfirmed_currency`)** | 주가 통화(USD)와 별개로 EPS 필드 통화코드 부재 |
| **주식 분모 단위** | **미확인 (`unconfirmed_share_basis`)** | **미확인 (`unconfirmed_share_basis`)** | 상장 증서(ADR/ADS)와 별개로 EPS 분모 직결 근거 미확보 |
| **공급사 기준일 (`asOf`)** | **미확인 (`unknown`)** | **미확인 (`unknown`)** | JSON상 `asOf: null`이며 원인 단정 철회 |
| **당사 수집 시각** | 2026-09-09T02:11:00Z | 2026-09-09T02:11:00Z | 파일 수집 시각 (기준일과 분리) |
| **4분기 연속 수치 확보** | **4/4 확보 완료** | **4/4 확보 완료** | 단일 원천 내 연속 4개 분기 관측치 존재 |
| **채점 적격성 판정** | **`scoring_eligible: False`** | **`scoring_eligible: False`** | **채점 보류 (`pending_basis_metadata_verification`) 유지** |

### 2.2 TSMC (`TSM`) 4분기 관측치 요약

- **차기 미발표 4분기 창**: 2026 Q3 (`0q`), 2026 Q4 (`+1q`), 2027 Q1 (`+2q`), 2027 Q2 (`+3q`)
- **분기별 관측치**:
  * 2026-09 (Q3): **$4.45** (low $4.24, high $4.70, 표본 6개)
  * 2026-12 (Q4): **$4.68** (low $4.22, high $4.93, 표본 5개)
  * 2027-03 (Q1): **$4.64** (low $4.36, high $4.97, 표본 4개)
  * 2027-06 (Q2): **$5.10** (low $4.90, high $5.49, 표본 4개)
- **4분기 연속 산술 합산치**:
  $$\mathbf{4.45 + 4.68 + 4.64 + 5.10 = 18.87}$$
- **채점 상태**: `pending_basis_metadata_verification` (수치는 4/4 완비되었으나 메타데이터 미확인으로 채점 보류).

### 2.3 Alibaba (`BABA`) 4분기 관측치 요약

- **차기 미발표 4분기 창**: FY27 Q2 (`0q`), FY27 Q3 (`+1q`), FY27 Q4 (`+2q`), FY28 Q1 (`+3q`)
- **분기별 관측치**:
  * 2026-09 (FY27 Q2): **$1.42** (low $0.81, high $2.16, 표본 3개)
  * 2026-12 (FY27 Q3): **$1.89** (low $1.31, high $2.75, 표본 3개)
  * 2027-03 (FY27 Q4): **$1.81** (low $1.05, high $2.21, 표본 3개)
  * 2027-06 (FY28 Q1): **$2.45** (low $1.76, high $3.13, 표본 2개)
- **4분기 연속 산술 합산치**:
  $$\mathbf{1.42 + 1.89 + 1.81 + 2.45 = 7.57}$$
- **채점 상태**: `pending_basis_metadata_verification` (수치는 4/4 완비되었으나 메타데이터 미확인으로 채점 보류).

---

## 3. 비상장사 지표 조사 및 근거 범위 상세

### 3.1 OpenAI 지표 체계 및 분류 상태

| 지표 항목 | 값 및 통화 | 분류 상태 | 기준 시점 및 근거 원천 | 검증 비고 |
|---|---|---|---|---|
| **사후 기업가치** | **$852.0B USD** | `confirmed` | 2026-03-31<br>[OpenAI 공식 발표](https://openai.com/index/accelerating-the-next-phase-ai/) | 공식 발표문 본문 직접 확인 |
| **약정 자본 총액** | **$122.0B USD** | `confirmed` | 2026-03-31<br>[OpenAI 공식 발표](https://openai.com/index/accelerating-the-next-phase-ai/) | 공식 본문 약정 자본 (전액 현금/컴퓨팅 단정 배제) |
| *과거 기업가치* | *$157.0B USD* | `confirmed` | 2024-10-02<br>[OpenAI 공식 발표](https://openai.com/index/scale-next-frontier/) | Thrive Capital 주도 라운드 이력 보존 |
| **누적 투자유치액** | **$17.9B USD** | `confirmed` | 2024-10-02<br>[Crunchbase](https://www.crunchbase.com) | 2024년 10월 라운드 완료 기준 |
| **ARR (연율화 런레이트)** | **$40.0B USD** | `unverified_article_url` | 2026-08-31<br>Bloomberg 보도 | **직접 URL 부재로 검증된 관측치로 미사용** |
| **과거 연간 실매출** | **$3.7B USD** | `unverified_article_url` | FY2024<br>The Information 보도 | **직접 URL 부재로 검증된 관측치로 미사용** |
| **장기 매출 목표** | **$100.0B USD** | `unverified_article_url` | 2029년 목표<br>New York Times 보도 | **직접 URL 부재로 검증된 관측치로 미사용** |

### 3.2 Anthropic 지표 체계 및 원장 범위

| 지표 항목 | 값 및 통화 | 분류 상태 | 기준 시점 및 근거 원천 | 검증 비고 |
|---|---|---|---|---|
| **사후 기업가치** | **$965.0B USD** | `confirmed` | 2026-05-28<br>[Anthropic 공식 발표](https://www.anthropic.com/news/series-h) | Series H 공식 발표문 본문 직접 확인 |
| **Series H 조달액** | **$65.0B USD** | `confirmed` | 2026-05-28<br>[Anthropic 공식 발표](https://www.anthropic.com/news/series-h) | **기존 약정 $15B 포함 명시 (산술 추론 순신규 약 $50B)** |
| **Run-rate revenue** | **>$47.0B USD** | `confirmed` | 2026-05-28<br>[Anthropic 공식 발표](https://www.anthropic.com/news/series-h) | **공식 표현 run-rate revenue 보존 (산식 미공개)** |
| **잠정 IPO 목표 시총** | **$2,000.0B USD** | `unverified_article_url` | 2026-09<br>Reuters 보도 | **직접 URL 부재로 검증된 관측치로 미사용 (매출전망 아님)** |
| **실제 연간 매출** | **미확보 (`None`)** | `unobtained` | unconfirmed | 당사 조사 범위 내 결산 감사보고서 미공개 |
| **미래 매출 전망치** | **미확보 (`None`)** | `unobtained` | unconfirmed | 당사 조사 범위 내 미래 공식 가이던스 부재 |
| **누적 조달액 합계** | **`unconfirmed_ledger`** | `unconfirmed_ledger` | 2026-05-28 | **D~G 라운드 출처 미비 및 전환사채 중복으로 미확인 유지** |

---

## 4. 검증 스크립트(`verify_sources.py`) 단위 테스트 결과

`verify_sources.py` 스크립트를 통해 총 12개의 단위 테스트를 실행하였으며, 전원 통과(`12 passed`)를 확인하였다.

| 번호 | 테스트 대상 및 규칙 | 테스트 내용 | 검증 결과 |
|---|---|---|---|
| **Test 1** | R7 지적사항 | min > max 또는 min/max 반전 입력 시 `stat_anomalies` 탐지 | **PASS** |
| **Test 2** | R6 지적사항 | null 분기 데이터 입력 시 크래시 없이 적절한 결측 처리 | **PASS** |
| **Test 3** | R6 지적사항 | 비연속 4개 분기 입력 시 `scoring_eligible=False` 차단 | **PASS** |
| **Test 4** | C13-SOURCE-03 | 문자열 `'false'` 입력 시 `is_strict_true()`에 의해 False 평가 | **PASS** |
| **Test 5** | C13-SOURCE-03 | 통계적 이상치 존재 시 무조건 `scoring_eligible=False` 강제 | **PASS** |
| **Test 6** | R6 지적사항 | 정상 4분기 및 메타데이터 완비 시 F6 채점 적격 승격 | **PASS** |
| **Test 7** | R6 지적사항 | 0 또는 음수 EPS 정상 처리 및 미확보 오분류 방지 | **PASS** |
| **Test 8** | R1 지적사항 | Anthropic `revenue_forecast`의 None 분리 및 IPO 시총 격리 | **PASS** |
| **Test 9** | R2, R3 지적사항 | OpenAI $852B 가치 및 공식 URL 검증 | **PASS** |
| **Test 10** | TSM API 검증 | TSMC 4분기($18.87) 확보 및 단위 미확인 채점 보류 분리 | **PASS** |
| **Test 11** | 모의 로직 검사 | 모의 메타데이터 True 주입 시 F6 적격 로직 동작 (외부 입증 아님) | **PASS** |
| **Test 12** | **S03-01~03 검증** | **실제 메타데이터 미확인(False) 시 scoring_eligible=False(채점 보류) 유지** | **PASS** |

---

## 5. 최종 결론

1. **상장사 채점 보류 유지 및 엄격한 메타데이터 분리**:
   - Nasdaq 공개 API를 통해 TSMC($18.87)와 Alibaba($7.57)의 단일 원천 연속 4분기 수치를 완비하였음.
   - 단, Zacks 계열(BNRI vs Street) 및 EPS 필드 통화/분모/기준일 직접 메타데이터가 미확인되었으므로, 채점 적격성을 승격하지 않고 **`scoring_eligible: False` (채점 보류: `pending_basis_metadata_verification`)를 엄격히 유지함.**
2. **비상장사 지표의 원문성 보존 및 2차 보도 배제**:
   - OpenAI의 공식 발표 수치($852B / $122B)와 직접 URL이 없는 2차 언론 보도를 엄격히 격리하였음.
   - Anthropic의 공식 지표명 **'run-rate revenue'**를 원문 그대로 보존하고 임의 연율화 산식(주간/월간 x12)을 전면 삭제하였으며, 자금조달 원장의 D~G 미완성 범위를 명시하고 SEC draft S-1 실사 표기를 철회함.
3. **원칙 및 산출물 보존**:
   - 기존 worker 코드, 채점 정책, raw JSON 6개, `validation/c13-data-01/` 산출물을 일체 훼손 없이 100% 보존함.
