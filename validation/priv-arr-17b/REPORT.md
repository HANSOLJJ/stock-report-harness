# PRIV-ARR-17B: 비상장 2사(Anthropic·OpenAI) ARR 정의 및 기간 가용성 독립 조사 보고서

## 핵심 결론

현재 스코어카드 기준선(`v1.5`)에 등록된 비상장 2사의 `arr` 관측치(Anthropic $65B, OpenAI $40B)는 회계상 ARR(Annual Recurring Revenue)이나 GAAP 확정매출이 아니며, 각각 2026년 7월 말 및 2026년 8월 20일 시점의 단일 월 매출 페이스를 12개월로 단순 연율화한 언론 보도 기준의 **추정 런레이트(Annualized Revenue Run-Rate)**이다. 두 비상장사 모두 감사(Audited)를 거쳐 대외 공시된 분기·반기·연간 GAAP 기간 매출은 전무하며, 특히 Anthropic `quarter_note`의 `Q2 | $10.9B`는 실제 공시된 확정 분기 매출이 아니라 2026년 5월 Series H 유치 당시 투자자 IR 덱에 포함되었던 분기 목표 전망치(Projected Q2 Guidance)가 언론에 유출된 수치이다. 따라서 1년 전 동기(2025년 7~8월)의 공식 런레이트 발표치가 부재하고, 유출된 과거 분기 매출($787M 등)은 런레이트와 지표 정의 및 산정 성격이 완전히 달라 수학적·회계학적으로 **전년 동기 비교 불가(Non-comparable)**로 판정한다.

---

## 1. 조사 배경 및 문제의 본질

F6 재정의 작업(`f6-status-2026-09-10.md`)에서 상장 11개사는 P1(PER), P2(EV/Sales), P3(매출 성장률), P4(입력 신뢰도)의 네 파라미터가 모두 정상 산출되는 반면, 비상장 2사(Anthropic, OpenAI)는 채점 근거의 핵심 분모가 흔들리는 결함이 확인되었다.

비상장 트랙 설계안은 P2 지표에 `post_money_valuation ÷ ARR`을 대응시키고, P4 지표에 `ARR ÷ cumulative_raised`를 대응시키고자 했다. 그러나 관측치 데이터베이스(`observations.json`) 실사 결과, 비상장 2사의 `arr` 항목은 두 회사 모두 `period`가 `null`로 비어 있었고, `quarter_note` 원문에는 각각 "런레이트 $65B(7월)", "런레이트 $40B+ (8/20)"로 기록되어 있었다.

런레이트(단일 기간 매출 × 12)와 ARR(계약 기반 연간 반복 매출)은 본질적으로 다른 개념이다. 런레이트는 일시적 토큰 사용량 급증이나 프로모션 등이 12배로 증폭되어 변동성이 극심하며, 계약 잔여 가치나 이탈률을 반영하지 않는다. 더욱이 현재 등록된 값은 공식 감사를 거친 GAAP 기간 매출도 아니다. 분모의 실체적 정의와 기간이 확인되지 않으면 P2 배수와 P4 자본효율이 모두 허상 위에 놓이게 된다. 이에 본 조사는 비상장 2사의 수치 실체와 출처 위계를 5대 항목으로 분해 실사하였다.

---

## 2. 5대 조사 항목별 상세 분석

### 2.1 항목 1: 현재 `arr` 값의 정체, 기준 시점, 원 출처

| 기업명 | 관측치 값 | 관측치 원문(`raw`) | 실제 지표 성격 | 기준 시점 | 원천 출처 및 위계 |
|---|---|---|---|---|---|
| **Anthropic** | $65.0B | `ARR $65B(7월 런레이트)` | 연율화 런레이트 (Run-rate) | 2026년 7월 말 | **Tier 3 (언론 보도 / 유출)**<br>공식 보도자료는 5월의 `$47B`(Tier 1)이며, $65B는 블룸버그/인포메이션 단독 보도 |
| **OpenAI** | $40.0B | `런레이트 $40B+(8/20)` | 연율화 런레이트 (Run-rate) | 2026-08-20 | **Tier 3 (언론 단독 보도)**<br>블룸버그 2026-08-20/31 보도 (공식 발표문에는 매출/ARR 일체 없음) |

#### (1) Anthropic 상세 실사
- **지표의 실체**: 관측치 `raw` 자체가 `ARR $65B(7월 런레이트)`로 괄호 안에 "7월 런레이트"임을 밝히고 있다. 이는 회계적 ARR이나 확정 매출이 아니라 2026년 7월 한 달 동안 발생한 추정 매출을 연간화(x12)한 수치이다.
- **원 출처**: Anthropic의 최신 공식 1차 발표문인 2026-05-28 Series H 보도자료(`https://www.anthropic.com/news/series-h`)의 원문은 `"Since our Series G in February, adoption has continued to grow across global enterprise customers, and our run-rate revenue crossed $47 billion earlier this month."`이다. 즉, 회사 공식 발표치(Tier 1)는 **2026년 5월 기준 런레이트 $47B**이다.
- **$65B의 출처**: 2026년 7월 말~8월 초 The Information, Bloomberg, GraniteShares 등의 언론 보도(Tier 3)를 통해 "7월 말 기준 런레이트가 $65B에 도달했다"는 내용이 전해졌으며, 이것이 기준선 관측치로 유입되었다.

#### (2) OpenAI 상세 실사
- **지표의 실체**: 관측치 `raw`는 `런레이트 $40B+(8/20)`이다. 2026년 8월 20일경 집계된 월 매출 페이스(월 약 $3.3B)를 12개월로 연율화한 수치이다.
- **원 출처**: OpenAI의 최신 공식 펀딩 발표문인 2026-03-31 "Accelerating the next phase of AI"(`https://openai.com/index/accelerating-the-next-phase-ai/`)에는 기업가치($852B)와 약정 자본($122B)만 명시되어 있으며, 매출·ARR·런레이트 수치는 일체 공개되지 않았다.
- **$40B+의 출처**: 2026-08-20 블룸버그 단독 보도(Tier 3)에서 처음 언급되었으며, 선행 조사(`consensus-source-2026-09-09`)에서도 1차 URL이 부재한 `unverified_article_url`로 분류되어 공식 관측치에서 배제된 바 있다.

---

### 2.2 항목 2: 기간 정의 확인 가능 수치 및 Anthropic `Q2 | $10.9B` 실체 규명

#### (1) Anthropic `Q2 | $10.9B`의 성격 규명
- **결론: "Q2 | $10.9B"는 사후 공시된 확정 분기 매출이 아니라, 2026년 5월 투자자 IR 덱에 수록된 '분기 목표 가이던스(Projected Guidance)'이다.**
- **근거 및 맥락**:
  1. Anthropic은 비상장 PBC(Public Benefit Corporation)로서 SEC에 분기보고서(Form 10-Q)를 제출하지 않는다.
  2. 2026년 5월 Series H 펀딩 라운드 진행 당시, 경영진이 투자자들에게 공유한 재무 모델에서 "2026 Q2 매출 $10.9B, 영업이익 $559M(첫 영업흑자, 영업이익률 약 5%)"을 달성할 것이라는 전망치를 제시했다.
  3. 이 수치가 금융 언론(The Information 등)을 통해 외부에 유출되었고, 스코어카드 작성 과정에서 `quarter_note`에 사실상 분기 실적처럼 요약 등재되었다.
  4. 이후 2026년 8월 언론 보도에서는 실제 Q2 잠정(preliminary) 매출이 이 전망치를 상회하여 $11.5B 이상을 기록했다는 후속 보도가 나왔다.
  5. 따라서 $10.9B는 감사된 확정 분기 매출(Audited Realized Revenue)이 아니며, `observations.json`에서도 공식 정량 metric(`revenue_q`)이 아닌 메모성 텍스트(`quarter_note`)로 격리되어 있고 `period`는 `null`이다.

#### (2) OpenAI 기간 매출 가용성
- OpenAI의 `quarter_note` 원문은 `"— | 런레이트 $40B+ (8/20) | 2026 GAAP 손실 ~$60B 전망 | BEP 2030"`이다. 첫 칸이 대시(`—`)로 표기되어 있어 분기 실적 수치가 아예 존재하지 않는다.
- 언론 유출 문건에서 2025년 연간 매출($13.07B), 2026 Q1($5.7B), 2026 Q2($6.7B) 등이 보도된 바 있으나, 회사가 공식 발표한 분기 기간 매출은 0건이다.

---

### 2.3 항목 3: 전년 동기 해당 값 유무 및 YoY 비교 가능성

**판정: 전년 동기 비교 불가 (Non-comparable).**

1. **지표 성격의 불일치**:
   - 현재 시점의 `arr` 관측치는 특정 월의 매출 속도를 연간화한 '런레이트'이다.
   - 1년 전 시점(2025년 중반)에 대해 언론에 단편적으로 언급된 과거 수치는 특정 분기 매출(예: Anthropic 2025 Q2 $787M)이거나, 과거 라운드 추정치(OpenAI 2024년 $3.7B)이다.
   - 런레이트와 분기 기간매출은 산정 공식과 단위가 완전히 달라 직접 비교(YoY)할 수 없다.

2. **동일 기준 1차 공식 발표치의 부재**:
   - Anthropic: 2025년 7월 시점의 공식 런레이트 발표문이 존재하지 않는다. 당시 언론에 오르내리던 수치는 약 $850M~$1B 수준(Tier 3/4)의 불확실한 추정치뿐이다.
   - OpenAI: 2025년 8월 시점의 공식 발표치가 없으며, 당시 런레이트 추정치(약 $10B~$13B) 역시 비공식 보도마다 범위가 상이하다.
   - 따라서 회계적·통계적 엄밀성을 충족하는 동일 기준의 1년 전 수치는 존재하지 않으므로 전년 동기 비교는 불가하다.

---

### 2.4 항목 4: `post_money_valuation` 및 `cumulative_raised`의 기준일 명시 여부

**판정: `observations.json` 내부에는 사건 기준일(Transaction Date)이 명시되어 있지 않으며(`period: null`), 스코어카드 실행일(`as_of: "2026-09-02"`)로 일괄 덮여 있다.**

| 기업명 | 지표명 | 수치 | `observations.json` 기록일 | 실제 사건 기준일 (실사 결과) | 상태 및 결함 |
|---|---|---|---|---|---|
| **Anthropic** | `post_money_valuation` | $965B | `as_of: 2026-09-02` (period: null) | **2026-05-28** (Series H 발표일) | 사건 발생일 누락 |
| **Anthropic** | `cumulative_raised` | $125B | `as_of: 2026-09-02` (period: null) | 시작일 "2021년~"만 존재 | 컷오프 기준일 부재, 미확인 원장 합산 |
| **OpenAI** | `post_money_valuation` | $852B | `as_of: 2026-09-02` (period: null) | **2026-03-31** (공식 펀딩 발표일) | 사건 발생일 누락 |
| **OpenAI** | `cumulative_raised` | $185B | `as_of: 2026-09-02` (period: null) | 특정 일자 부재 ("약 $180~190B 중간값") | 기준일 부재, 추정 범위 중간값 대입 |

- 두 회사 모두 펀딩 라운드가 성사된 실제 시점(Anthropic 2026년 5월, OpenAI 2026년 3월)과 관측치 기록 시점(2026년 9월 2일) 사이에 수개월의 시차가 존재한다.
- 누적 조달액(`cumulative_raised`)은 과거 라운드의 전환사채 전환 여부, 실제 현금 납입액 대 컴퓨팅 크레딧 약정액의 분리가 검증되지 않은 채 언론 추정치 또는 범위 중간값을 기계적으로 대입한 상태이다.

---

### 2.5 항목 5: 출처 등급 분류 체계 (Source Hierarchy)

엄격한 4단계 출처 위계에 따른 비상장 2사의 수치 분류는 다음과 같다.

```
[Tier 1: 회사 공식 발표]  ──▶ 공식 보도자료, 뉴스룸 공식 릴리스 (검증 가능 직접 URL)
         │
[Tier 2: 임원 공개 발언]  ──▶ CEO/CFO 등 핵심 임원의 공개 컨퍼런스, 인터뷰 육성
         │
[Tier 3: 언론 단독 보도]  ──▶ 내부 문건, IR 덱 유출, 관계자 인용 취재 보도 (Bloomberg 등)
         │
[Tier 4: 2차 인용 / 루머] ──▶ 취재원 없는 재인용 블로그, 집계 사이트, 커뮤니티 추정
```

#### 출처 등급별 매핑 표

| 등급 | 정의 및 요건 | Anthropic 해당 항목 | OpenAI 해당 항목 |
|---|---|---|---|
| **Tier 1<br>(회사 공식 발표)** | 회사 공식 도메인의 뉴스룸/보도자료에 직접 게재된 수치 | • Series H 기업가치: **$965B** (2026-05-28)<br>• Series H 조달액: **$65B** (약정 $15B 포함)<br>• **공식 run-rate revenue: >$47B** (2026-05-28) | • 펀딩 기업가치: **$852B** (2026-03-31)<br>• 약정 자본 총액: **$122B** (2026-03-31)<br>• 과거 Thrive 가치: **$157B** (2024-10-02)<br>*(공식 매출/ARR/런레이트 발표는 전무)* |
| **Tier 2<br>(임원 공개 발언)** | CEO·CFO 등 임원의 콘퍼런스, 팟캐스트, 공개 포럼 발언 | • 다리오 아모데이 CEO 공개 인터뷰 발언 (연간 수십억 달러 단위 성장 추세 언급 등) | • 샘 알트만 CEO 공개 인터뷰 및 X 게시글 (ChatGPT WAU 9억/MAU 10억 사용자 언급 등) |
| **Tier 3<br>(언론 단독 보도)** | 신뢰도 높은 금융 언론의 내부 문건 실사, IR 덱 유출, 취재원 인용 보도 | • **7월 런레이트 $65B** (2026-07/08 블룸버그 등)<br>• **Q2 재무 전망 매출 $10.9B / 영업익 $559M** (2026-05 IR 유출)<br>• Q2 잠정 실적 >$11.5B (2026-08 언론 보도)<br>• 목표 IPO 시총 $2T (2026-09 로이터) | • **8/20 런레이트 $40B+** (2026-08-20 블룸버그)<br>• 2025년 GAAP 매출 $13.07B / 손실 $20.92B<br>• 2026년 GAAP 손실 ~$60B 전망<br>• 2026 Q1 $5.7B / Q2 $6.7B 매출 유출<br>• 손익분기 목표 2030년 후퇴 (2026-08 보도) |
| **Tier 4<br>(2차 인용 / 루머)** | 1차 출처나 취재원 없이 Tier 3를 단순 재인용한 집계치 및 파생 배수 | • 누적 조달액 "약 $125B(2021년~)"<br>• 비공식 P/S(30~39배) 역산치 | • 누적 조달액 "약 $180~190B(중간값)"<br>• 2029년 장기 목표 매출 $100B 보도 |

---

## 3. 원자료 수집 및 `_raw` 보존 현황

본 조사는 `robots.txt`와 이용약관을 사전에 확인하였으며, 사후 전사가 아닌 실제 HTTP 응답 및 baseline 슬라이스를 `validation/priv-arr-17b/_raw/`에 영구 보존하였다.

1. **`anthropic_robots.txt` / `openai_robots.txt`**: 두 공식 사이트 모두 루트 경로 크롤링을 허용하고 있음을 확인하였다.
2. **`anthropic_commercial_terms.html` / `openai_terms_of_use.html`**: 상업 및 소비자 약관 원문을 보존하였다.
3. **`anthropic_series_h_official_2026-05-28.html`**: Anthropic의 2026-05-28 Series H 공식 보도자료 전문(148,593 바이트)을 보존하였다.
4. **`openai_accelerating_official_2026-03-31.html`**: OpenAI의 2026-03-31 공식 발표문 전문(367,661 바이트)을 보존하였다.
5. **`baseline_v15_unlisted_observations.json`**: 기준선 `v1.5`의 Anthropic 및 OpenAI 관측치 항목 26건 전체 슬라이스를 보존하였다.
6. **`baseline_v15_unlisted_scores.json`**: 기준선 `v1.5`의 비상장 2사 점수 및 근거 서술 원문을 보존하였다.
7. **`external_reporting_raw.json`**: 위계화된 금융 언론 보도 이벤트 원문 데이터를 구조화하여 보존하였다.

---

## 4. 단위 테스트 검증 결과 (`verify_arr_definitions.py`)

`validation/priv-arr-17b/verify_arr_definitions.py`를 통해 총 12개의 검증 테스트를 실행하였으며 전원 통과하였다.

| 번호 | 테스트 명칭 및 대상 | 검증 내용 | 결과 |
|---|---|---|---|
| **Test 1** | `test_01_baseline_items_present` | 기준선 관측치 슬라이스 내 비상장 2사 존재 확인 | **PASS** |
| **Test 2** | `test_02_anthropic_arr_nature` | Anthropic `arr`이 런레이트이며 `period=null`임을 확인 | **PASS** |
| **Test 3** | `test_03_openai_arr_nature` | OpenAI `arr`이 8/20 런레이트이며 `period=null`임을 확인 | **PASS** |
| **Test 4** | `test_04_anthropic_quarter_note_definition` | Anthropic `quarter_note`에 $10.9B가 있으나 정량 매출 metric 부재 확인 | **PASS** |
| **Test 5** | `test_05_openai_quarter_note_definition` | OpenAI `quarter_note` 분기 매출란이 대시(`—`) 결측 상태임을 확인 | **PASS** |
| **Test 6** | `test_06_post_money_and_cumulative_raised_as_of_dates` | 기업가치·누적조달액이 사건일이 아닌 실행일(2026-09-02)로 등록됨을 확인 | **PASS** |
| **Test 7** | `test_07_source_tier_classification` | Tier 1(공식)과 Tier 3(언론 유출)의 엄격한 분리 위계 검증 | **PASS** |
| **Test 8** | `test_08_positive_control_audited_revenue` | **양성 대조군**: 정식 10-Q 기간매출(Tier 1, period 명시)의 적격 승격 검증 | **PASS** |
| **Test 9** | `test_09_negative_mutation_control_arr_as_gaap` | **음성 변이 1**: 런레이트를 기간 없는 GAAP 매출로 왜곡 시 차단 예외 발생 | **PASS** |
| **Test 10** | `test_10_negative_mutation_control_yoy_mismatch` | **음성 변이 2**: 런레이트와 분기매출 간 YoY 계산 시도 시 타입 불일치 차단 | **PASS** |
| **Test 11** | `test_11_negative_mutation_control_unverified_tier_elevation` | **음성 변이 3**: 1차 URL 없는 언론 보도를 Tier 1으로 승격 시 assertion 차단 | **PASS** |
| **Test 12** | `test_12_raw_files_preservation` | `_raw/` 디렉터리 내 9개 필수 원자료 파일 존재 및 용량 검증 | **PASS** |

---

## 5. F6 재정의 작업에 대한 권고안

1. **지표 명칭의 회계적 정정**:
   - `arr`이라는 명칭 대신 `annualized_run_rate` 또는 `run_rate_revenue`로 분리 표기해야 한다.
   - 계약 잔여액이나 갱신율이 통제되지 않는 런레이트를 정통 SaaS ARR로 취급해서는 안 된다.
2. **P2(EV/Sales) 및 P4(신뢰도) 적용 시 주의사항**:
   - `post_money_valuation ÷ ARR` 계산 시, 분모가 실제 연간 매출(TTM)이 아닌 런레이트이므로 밸류에이션 배수가 2~3배가량 과소평가(착시 현상)된다.
   - 따라서 비상장 트랙은 상장사와 동일한 배수 잣대를 기계 적용하지 말고, P4 신뢰도 항목에서 "기간 단위가 TTM 아님(런레이트 대체)" 및 "비공식 유출치 의존"에 따른 감점을 적용해야 한다.
3. **P3(매출 성장률) 산출 불가 인정**:
   - 전년 동기의 동일 기준 공식 런레이트가 존재하지 않으므로, 무리하게 왜곡된 YoY 성장률을 산출하지 말고 "성장률 비교 불가(산출 제외)"로 처리하는 것이 원칙에 부합한다.
