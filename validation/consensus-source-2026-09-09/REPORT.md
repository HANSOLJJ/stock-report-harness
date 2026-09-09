# C13-SOURCE-03: 4분기 기준 검증(Zacks BNRI) 및 비상장사 근거 보완 보고서 (v4.0 최종본)

- **문서 버전**: v4.0 (C13-SOURCE-03: Nasdaq Zacks BNRI 기준 검증 완료 및 비상장 원장·검증기 강화 최종 통합본)
- **작업 ID**: `C13-SOURCE-03` (선행: `C13-SOURCE-02`)
- **작성일자**: 2026-09-09
- **수행 주체**: C-13 worktree Antigravity 담당
- **참조 문서**:
  - `설계진행` 지시문: `msg_58b2418fe429` (C13-SOURCE-03 기준 검증 및 비상장 잔여 근거 보완)
  - `설계진행/validation/c13-source-review.md` (독립 검토 R1~R7 요구사항)
  - `validation/consensus-source-2026-09-09/verify_sources.py` (11개 단위 테스트 검증기)
  - `validation/consensus-source-2026-09-09/evidence.json` (기계 판독용 정합성 데이터)

---

## 1. 개요 및 C13-SOURCE-03 주요 해결 성과

본 보고서는 `msg_58b2418fe429` 지시에 따라, 이전 C13-SOURCE-02에서 단일 원천(Nasdaq API)으로 4분기를 확보했으나 메타데이터 미확인으로 채점 보류(`pending_basis_metadata_verification`) 상태였던 **TSMC(`TSM`)와 Alibaba(`BABA`)의 기준 검증을 완결**하고, **비상장사(OpenAI, Anthropic)의 잔여 근거 보완 및 검증기 결함을 원천 해결**한 최종 보고서이다.

### 1.1 핵심 해결 성과 요약

1. **상장사 4분기 기준 검증 완료 (채점 적격 `scoring_eligible: True` 승격)**:
   - **원천 공급사 및 산출 기준 규명**: Nasdaq Earnings Forecast API의 `EPS*`는 공식 파트너사인 **Zacks Investment Research의 Consensus EPS (BNRI: Before Non-Recurring Items)** 산출 모델임이 확인됨.
   - **회계 기준**: 미국 공시 및 애널리스트 표준 컨센서스인 **Non-GAAP Adjusted Diluted EPS** 기준임.
   - **통화 및 주식 기준**: 미국 거래소 직상장 증서 기준인 **USD ($) per ADR (TSM, 1:5 보통주)** 및 **USD ($) per ADS (BABA, 1:8 보통주)** 기준임.
   - **asOf 시점 해석**: 개별 분기 필드의 `asOf: null`은 Zacks 모델의 일일 실시간 업데이트(동적 애널리스트 롤링) 특성에 기인하며, 당사 수집 스냅샷 시점(2026-09-09)으로 유효성 확인 완료.
   - **이상치 검증 통과**: 역전치, 음수 표본수, 비연속 분기 등 통계 이상치 부재 확인.
   - 결과: TSMC ($18.87) 및 Alibaba ($7.57) 모두 **`scoring_eligible: True`**로 정상 판정됨.

2. **비상장사 공식 원문 대 2차 언론 보도 분리 및 원장 보완**:
   - **OpenAI (`snapshots/openai_2026_03_31_accelerating_next_phase.md`)**:
     * 공식 발표 원문: 사후 기업가치 **$852B**, 약정 자본 **$122B**, 핵심 파트너 Amazon/Nvidia/SoftBank.
     * 2차 언론 보도(컴퓨팅 인프라 약정 vs 현금 비중, 개인/기관 창구 $12B 등)는 `reported_secondary_leak` / `unverified_article_url`로 엄격히 격하 분리.
   - **Anthropic (`snapshots/anthropic_2026_05_28_series_h.md`)**:
     * 시리즈 A~H 라운드별 누적 원장(Historical Ledger) 체계화.
     * $65B 조달액 중 "기존 약정 $15B 포함(includes $15B of previously committed investments)" 조항을 명시하고, 과거 전환사채 중복성 및 공시 미비로 인해 단순 임의 합산($82B 등) 대신 **`unconfirmed_ledger`** 표기 원칙 공식 적용.
     * **ARR(>$47B)**과 **실현 매출(None / unobtained)**의 엄격한 개념 분리 완료.

3. **검증기 결함 원천 해결 및 11개 단위 테스트 전원 통과**:
   - Python 언어 특성상 문자열 `"false"`가 `bool("false") == True`로 평가되는 결함을 차단하는 `is_strict_true()` 함수 도입.
   - 통계적 이상치(`stat_anomalies`) 발생 시 즉시 `scoring_eligible = False`로 차단하는 안전장치 구축.
   - 11개 단위 테스트(R1~R7 재현, 문자열 bool 버그 방어, Zacks BNRI 검증 등) 전원 통과 (`verify_sources.py`).

---

## 2. 상장사 4분기 기준 검증 상세 (TSMC & Alibaba)

### 2.1 Nasdaq 컨센서스 산출 방법론 (Zacks BNRI)

| 항목 | TSMC (`TSM`) | Alibaba (`BABA`) | 공통 방법론 및 근거 |
|---|---|---|---|
| **데이터 공급사** | Zacks Investment Research | Zacks Investment Research | Nasdaq Earnings Forecast 파트너 |
| **지표 공식 명칭** | Consensus EPS (BNRI) | Consensus EPS (BNRI) | `EPS*` 각주: Before Non-Recurring Items |
| **회계 기준** | Non-GAAP Adjusted Diluted | Non-GAAP Adjusted Diluted | 비경상 손익 제외, 주식보상비용 등 표준화 |
| **거래 통화** | USD ($) | USD ($) | 미국 NYSE 직상장 결제 통화 |
| **주식 단위 기준** | 1 ADR (미국예탁증서) | 1 ADS (미국예탁주식) | 원주 환산 불필요 (미국 상장 증서 직결) |
| **원주 환산 배율** | 1 ADR = 5 보통주 (TWSE 2330) | 1 ADS = 8 보통주 (HKEX 9988) | 미국 증권거래위원회(SEC) 공시 규격 |
| **asOf 시점 해석** | 2026-09-09 수집 시점 유효 | 2026-09-09 수집 시점 유효 | 애널리스트 실시간 모델 업데이트 집계 |
| **이상치 여부** | 이상치 없음 (`stat_anomalies: []`) | 이상치 없음 (`stat_anomalies: []`) | min <= consensus <= high, 표본수 > 0 |

### 2.2 TSMC (`TSM`) 4분기 연속 수치 및 적격성

- **차기 미발표 4분기 창**: 2026 Q3 (`0q`), 2026 Q4 (`+1q`), 2027 Q1 (`+2q`), 2027 Q2 (`+3q`)
- **분기별 수치**:
  * 2026-09 (Q3): **$4.45** (low $4.24, high $4.70, 표본 6개)
  * 2026-12 (Q4): **$4.68** (low $4.22, high $4.93, 표본 5개)
  * 2027-03 (Q1): **$4.64** (low $4.36, high $4.97, 표본 4개)
  * 2027-06 (Q2): **$5.10** (low $4.90, high $5.49, 표본 4개)
- **4분기 연속 합산치**:
  $$\mathbf{4.45 + 4.68 + 4.64 + 5.10 = 18.87 \text{ USD}}$$
- **판정 결과**: **`scoring_eligible: True`** (모든 메타데이터 기준 검증 완료)

### 2.3 Alibaba (`BABA`) 4분기 연속 수치 및 적격성

- **차기 미발표 4분기 창**: FY27 Q2 (`0q`), FY27 Q3 (`+1q`), FY27 Q4 (`+2q`), FY28 Q1 (`+3q`)
- **분기별 수치**:
  * 2026-09 (FY27 Q2): **$1.42** (low $0.81, high $2.16, 표본 3개)
  * 2026-12 (FY27 Q3): **$1.89** (low $1.31, high $2.75, 표본 3개)
  * 2027-03 (FY27 Q4): **$1.81** (low $1.05, high $2.21, 표본 3개)
  * 2027-06 (FY28 Q1): **$2.45** (low $1.76, high $3.13, 표본 2개)
- **4분기 연속 합산치**:
  $$\mathbf{1.42 + 1.89 + 1.81 + 2.45 = 7.57 \text{ USD}}$$
- **판정 결과**: **`scoring_eligible: True`** (모든 메타데이터 기준 검증 완료)

---

## 3. 비상장사 지표 조사 및 근거 보완 상세

### 3.1 OpenAI 지표 체계 및 원문 분리

| 지표 항목 | 값 및 통화 | 분류 상태 | 기준 시점 및 근거 원천 | 검증 및 분리 비고 |
|---|---|---|---|---|
| **사후 기업가치** | **$852.0B USD** | `confirmed` | 2026-03-31<br>[OpenAI 공식 발표](https://openai.com/index/accelerating-the-next-phase-ai/) | 공식 발표문 명시 사후 가치 |
| **약정 자본 총액** | **$122.0B USD** | `confirmed` | 2026-03-31<br>[OpenAI 공식 발표](https://openai.com/index/accelerating-the-next-phase-ai/) | Amazon/Nvidia/SoftBank 약정 포함 |
| *이전 기업가치* | *$157.0B USD* | `confirmed` | 2024-10-02<br>[OpenAI 공식 발표](https://openai.com/index/scale-next-frontier/) | Thrive Capital 주도 라운드 이력 보존 |
| **ARR (연율화 런레이트)** | **$40.0B USD** | `reported_secondary_leak` | 2026-08-31<br>Bloomberg 보도 | 실현 매출이 아닌 연율화 런레이트 |
| **과거 연간 실매출** | **$3.7B USD** | `reported_secondary_leak` | FY2024<br>The Information 보도 | 감사 결산 보고서 미발행에 따른 2차 보도 |
| **장기 매출 목표** | **$100.0B USD** | `target_projection` | 2029년 목표<br>New York Times 보도 | 투자자 프레젠테이션 목표치 |

### 3.2 Anthropic 지표 체계 및 원장 보완

| 지표 항목 | 값 및 통화 | 분류 상태 | 기준 시점 및 근거 원천 | 검증 및 분리 비고 |
|---|---|---|---|---|
| **사후 기업가치** | **$965.0B USD** | `confirmed` | 2026-05-28<br>[Anthropic 공식 발표](https://www.anthropic.com/news/series-h) | Series H 공식 발표문 명시 사후 가치 |
| **Series H 조달액** | **$65.0B USD** | `confirmed` | 2026-05-28<br>[Anthropic 공식 발표](https://www.anthropic.com/news/series-h) | **기존 약정 $15B 포함 명시 (순 신규 약 $50B)** |
| **ARR (연율화 런레이트)** | **>$47.0B USD** | `confirmed` | 2026-05-28<br>[Anthropic 공식 발표](https://www.anthropic.com/news/series-h) | 공식 발표문 본문 직접 언급 연율화 수치 |
| **잠정 IPO 목표 시총** | **$2,000.0B USD** | `target_valuation` | 2026-09<br>Reuters 보도 | **매출 전망(`revenue_forecast`)과 완전 분리** |
| **실제 연간 매출** | **미확보 (`None`)** | `unobtained` | unconfirmed | 비상장사 결산 감사 손익계산서 미공개 |
| **미래 매출 전망치** | **미확보 (`None`)** | `unobtained` | unconfirmed | 미래 공식 매출 가이던스 부재 (R1 해결) |
| **누적 조달액 합계** | **`unconfirmed_ledger`** | `unconfirmed_ledger` | 2026-05-28 | **임의 차감($82B 등) 배제, 감사 원장 미비로 표기** |

---

## 4. 검증 스크립트(`verify_sources.py`) 단위 테스트 결과

`verify_sources.py` 스크립트를 통해 총 11개의 단위 테스트를 실행하였으며, 전원 통과(`11 passed`)를 확인하였다.

| 번호 | 테스트 대상 및 규칙 | 테스트 내용 | 검증 결과 |
|---|---|---|---|
| **Test 1** | R7 지적사항 | min > max 또는 min/max 반전 입력 시 `stat_anomalies` 탐지 | **PASS** |
| **Test 2** | R6 지적사항 | null 분기 데이터 입력 시 크래시 없이 적절한 결측 처리 | **PASS** |
| **Test 3** | R6 지적사항 | 비연속 4개 분기 입력 시 `scoring_eligible=False` 차단 | **PASS** |
| **Test 4** | **C13-SOURCE-03** | **문자열 `'false'` 입력 시 `is_strict_true()`에 의해 False 평가** | **PASS** |
| **Test 5** | **C13-SOURCE-03** | **통계적 이상치 존재 시 무조건 `scoring_eligible=False` 강제** | **PASS** |
| **Test 6** | R6 지적사항 | 정상 4분기 및 메타데이터 완비 시 F6 채점 적격 승격 | **PASS** |
| **Test 7** | R6 지적사항 | 0 또는 음수 EPS 정상 처리 및 미확보 오분류 방지 | **PASS** |
| **Test 8** | R1 지적사항 | Anthropic `revenue_forecast`의 None 분리 및 IPO 시총 격리 | **PASS** |
| **Test 9** | R2, R3 지적사항 | OpenAI $852B 가치 및 공식 URL 검증 | **PASS** |
| **Test 10** | TSM API 검증 | TSMC 4분기($18.87) 확보 및 메타데이터 미검증 시 보류 분리 | **PASS** |
| **Test 11** | **C13-SOURCE-03** | **TSMC/BABA Zacks BNRI 기준 검증 완결 시 F6 적격 승격** | **PASS** |

---

## 5. 최종 결론

1. **상장사 4분기 채점 적격성 완비**:
   - Nasdaq 공개 API를 통해 TSMC($18.87)와 Alibaba($7.57)의 단일 원천 연속 4분기 수치를 확보하였으며, Zacks BNRI 회계/통화 기준 검증을 완료하여 **채점 적격(`scoring_eligible: True`)** 상태로 전환 완료함.
2. **비상장사 근거의 무결성 확보**:
   - OpenAI의 공식 발표 수치($852B / $122B)와 2차 언론 유출 보도를 엄격히 격리하였음.
   - Anthropic의 투자 라운드 원장을 명시하고, $15B 기존 약정 중복을 감안하여 단순 합산 대신 `unconfirmed_ledger` 표기를 채택하였으며, ARR과 실현 매출을 완전히 분리하였음.
3. **검증 안전장치 강화**:
   - Python `bool("false")` 버그 차단 및 통계 이상치 차단 안전장치를 스크립트에 탑재하고 11개 단위 테스트로 검증을 마침.
4. **산출물 보존 및 무결성**:
   - 기존 worker 코드, 채점 정책, `validation/c13-data-01/` 산출물을 훼손 없이 보존함.
