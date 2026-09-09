# C13-SOURCE-03: 컨센서스 기준 검증 및 비상장사 근거 보완 보고서 (v4.2 R2 재검토 반영본)

- **문서 버전**: v4.2 (설계진행 R2 독립 재검토 `c13-source03-r2-review.md` 잔여 이슈 4종 전면 반영본)
- **작업 ID**: `C13-SOURCE-03` (선행: `C13-SOURCE-02`)
- **작성일자**: 2026-09-09
- **수행 주체**: C-13 worktree Antigravity 담당
- **참조 문서**:
  - `설계진행` R2 재검토 통보: `msg_260dee949d61` 및 `validation/c13-source03-r2-review.md`
  - `validation/consensus-source-2026-09-09/verify_sources.py` (12개 단위 테스트 검증기)
  - `validation/consensus-source-2026-09-09/evidence.json` (기계 판독용 정합성 데이터)

---

## 1. 개요 및 R2 재검토 보완 핵심

본 보고서는 설계진행의 R2 독립 재검토(`c13-source03-r2-review.md`) 지적사항에 따라, **공식 원문 직접 발췌(Verbatim Quotes)**와 **작성자 분석 요약 및 미확인 2차 보도 메모**를 명확히 분리하고, 직접 근거가 없는 홈페이지 루트 링크 철회 및 비상장 미확인 수치의 관측 배제를 완결한 최종 보고서이다.

### 1.1 R2 재검토 4개 잔여 이슈 조치 내역

1. **Anthropic 스냅샷 원문 발췌와 요약 분리 (`snapshots/anthropic_2026_05_28_series_h.md`)**:
   - 공식 발표문 본문의 실제 영문 원문 발췌문(사후가치 $965B, 조달액 $65B, 기존 약정 $15B 포함 문구, annualized run-rate revenue $47B)을 1절에 직접 인용으로 분리 기록함.
   - $50B 산술 추론, ARR 산식 미공개, 실현 매출 미확보 등의 해설은 2절 작성자 분석/요약으로 분리함.
2. **Anthropic Series A/B/C 홈페이지 루트 링크 철회 및 미확인 정정**:
   - 단순 홈페이지 루트(`anthropic.com`) 링크는 개별 근거로 부적합하므로 철회하고, 개별 공식 릴리스 직접 URL 부재에 따라 과거 라운드를 모두 **미확인 (`unconfirmed / unobtained`)**으로 낮춤.
3. **OpenAI 스냅샷 미확인 2차 보도 메모 완전 격리 (`snapshots/openai_2026_03_31_accelerating_next_phase.md`)**:
   - 직접 기사 URL이 없는 $12B 및 인프라 약정 비중 보도를 "검증에 사용하지 않는 미확인 참고 메모"로 완전히 격리하고 공식 관측치에서 배제함 (`unverified_article_url`).
4. **REPORT.md 원문 발췌와 작성자 요약의 엄격한 분리**:
   - 본문 서술 및 요약표에서 실제 공식 발표문 직접 발췌 수치와 관측 배제 미확인 메모를 분리 표기함.

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

### 3.1 OpenAI 지표 체계 (원문 발췌 vs 미확인 메모 분리)

| 지표 항목 | 값 및 통화 | 분류 상태 | 기준 시점 및 근거 원천 | 검증 및 분리 비고 |
|---|---|---|---|---|
| **사후 기업가치** | **$852.0B USD** | `confirmed` | 2026-03-31<br>[OpenAI 공식 발표](https://openai.com/index/accelerating-the-next-phase-ai/) | **공식 발표문 영문 원문 발췌 확인** |
| **약정 자본 총액** | **$122.0B USD** | `confirmed` | 2026-03-31<br>[OpenAI 공식 발표](https://openai.com/index/accelerating-the-next-phase-ai/) | **공식 본문 약정 자본 확인 (단정 배제)** |
| *과거 기업가치* | *$157.0B USD* | `confirmed` | 2024-10-02<br>[OpenAI 공식 발표](https://openai.com/index/scale-next-frontier/) | Thrive Capital 주도 라운드 이력 보존 |
| **누적 투자유치액** | **$17.9B USD** | `confirmed` | 2024-10-02<br>[Crunchbase](https://www.crunchbase.com) | 2024년 10월 라운드 완료 기준 |
| **ARR (연율화 런레이트)** | **$40.0B USD** | `unverified_article_url` | 2026-08-31<br>Bloomberg 보도 | **직접 URL 부재로 관측치에서 완전 배제** |
| **과거 연간 실매출** | **$3.7B USD** | `unverified_article_url` | FY2024<br>The Information 보도 | **직접 URL 부재로 관측치에서 완전 배제** |
| **장기 매출 목표** | **$100.0B USD** | `unverified_article_url` | 2029년 목표<br>New York Times 보도 | **직접 URL 부재로 관측치에서 완전 배제** |

### 3.2 Anthropic 지표 체계 (원문 발췌 vs 미확인 메모 분리)

| 지표 항목 | 값 및 통화 | 분류 상태 | 기준 시점 및 근거 원천 | 검증 및 분리 비고 |
|---|---|---|---|---|
| **사후 기업가치** | **$965.0B USD** | `confirmed` | 2026-05-28<br>[Anthropic 공식 발표](https://www.anthropic.com/news/series-h) | **공식 발표문 영문 원문 발췌 확인** |
| **Series H 조달액** | **$65.0B USD** | `confirmed` | 2026-05-28<br>[Anthropic 공식 발표](https://www.anthropic.com/news/series-h) | **원문: $15B 기존 약정 포함 명시 ($50B는 산술 추론)** |
| **Run-rate revenue** | **>$47.0B USD** | `confirmed` | 2026-05-28<br>[Anthropic 공식 발표](https://www.anthropic.com/news/series-h) | **원문 표기 'annualized run-rate revenue' (산식 미공개)** |
| **과거 Series A~G** | **개별 미상세** | `unconfirmed` | 과거 라운드 | **개별 직접 URL 부재로 미확인 처리 (홈페이지 링크 철회)** |
| **잠정 IPO 목표 시총** | **$2,000.0B USD** | `unverified_article_url` | 2026-09<br>Reuters 보도 | **직접 URL 부재로 관측치에서 배제 (매출전망 아님)** |
| **실제 연간 매출** | **미확보 (`None`)** | `unobtained` | unconfirmed | 당사 조사 범위 내 결산 감사보고서 미공개 |
| **미래 매출 전망치** | **미확보 (`None`)** | `unobtained` | unconfirmed | 당사 조사 범위 내 미래 공식 가이던스 부재 |
| **누적 조달액 합계** | **`unconfirmed_ledger`** | `unconfirmed_ledger` | 2026-05-28 | **과거 라운드 직접 URL 미비 및 전환사채 중복으로 미확인 유지** |

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
