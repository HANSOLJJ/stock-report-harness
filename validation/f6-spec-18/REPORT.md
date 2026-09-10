# F6-SPEC-18 — F6 재정의 스펙 작성과 구현

작성일 2026-09-10. 담당 worker(HANSOLJJ/worker). 요청 `msg_d7ca2cdbcc40`.
선행 확정 문서: `f6-band-decision.md`(`a0c3c7e`) · `f6-status-2026-09-10.md`(`d663614`) · `priv-arr-17-review.md`(`bcafb42`) · `f6-fx-16-review.md`(`a0fa605`) · `f6-avail-15-review.md`(`ab02d77`).

## 결론

**다섯 작업 전부 완료했다. 검산 기준 9개 중 8개가 일치하고, 하나(oracle)는 산술이 아니라 TTM 창의 끝점 규약 차이다.**

| | 결과 |
|---|---|
| `v1.7.json` 신설 | 완료 · `status: draft` |
| 스키마 신규 metric **3종** | `net_income_ttm` · `revenue_ttm_prior` · `arr_prior` |
| `calc_f6.py` 개정 | 모드 분기 + `calc_f6_params.py` 신설 |
| SEC 수집기 | `collect_ttm.py` — **신규 네트워크 호출 없음**(F6-AVAIL-15 저장 원자료 재사용) |
| 테스트 | 113 → **137건** (신규 24건) |
| 검산 대조 | **8/9 일치** · oracle 1건 불일치(4 절) |

`v1.5`·승인 해시 6종·`results_hash 0942c342`·HTML 바이트 전부 불변이다. `api.nasdaq.com` 은 호출하지 않았고 환율 출처는 하드코딩하지 않고 자리만 만들었다.

## 1. `v1.7.json`

`v1.6` 을 바탕으로 F6 만 바꾸고 나머지는 그대로 뒀다. `sources` 정책(allowlist·`usage_scope`·`unlisted`)은 v1.6 에서 그대로 이어진다.

### 1.1 함정 배점 재배분 — 합 −18 보존

| factor | v1.5·v1.6 | **v1.7** |
|---|---|---|
| F6 가격 | −5 | **−7** |
| F7 순환금융 | −3 | **−2** |
| F8 비대칭 의존 | −5 | −5 유지 |
| F9 적자 깊이 | −5 | **−4** |
| **합** | **−18** | **−18** |

`trap_min_nominal` 의 `-20` 은 **건드리지 않았다.** 그것은 원문 개요가 네 factor 를 모두 −5 로 놓은 명목 설명이라(`design-guideline.md` 297행) 배분이 바뀌어도 그대로다. 대신 `trap_min_note` 에 v1.7 구성을 적었다.

### 1.2 파라미터

```
P1 PER          25 / 45        (-2 ~ 0)   upper 미만
P2 EV/Sales      8 / 20        (-2 ~ 0)   upper 미만
P3 성장률      30% / 15% / 5%  (-3 ~ 0)   lower 이상
P4 입력신뢰도   소계 한 칸 강등, 상한 1칸
경계 허용오차   ±3% 표시 전용
```

**규칙이 자기를 검산한다.** 스키마가 `파라미터 score_range 하한 합계 == factors.F6.range 하한` 을 강제한다. −2−2−3 = −7 이 아니면 규칙 파일이 로드되지 않는다. 배점을 손대면서 한쪽만 고치는 사고를 막는다.

### 1.3 트랙 넷

| 트랙 | 파라미터 | 하한 | 자동 P4 |
|---|---|---|---|
| `listed_ttm` 일반 상장 | P1·P2·P3 | −7 | — |
| `listed_annual` ADR/FPI | P1·P2·P3 | −7 | `period_basis_not_ttm` |
| `listed_newly` 신규 상장 | **P3 만** | **−3** | `short_history` |
| `private` 비상장 | P2·P3·P4 | **−5** | — |

비상장 밴드는 **`private_bands: null` · `private_score_mode: "pending_rule_decision"`** 로 자리만 만들었다. 배수는 계산하고 점수는 만들지 않는다.

환율은 `f6.fx.status = "pending_source_allowlist"` 이고 `rate_source_host` 는 `null` 이다. **하드코딩하지 않았다.**

## 2. 스키마

### 2.1 신규 metric은 3종뿐이다

`revenue_ttm` 과 `operating_income_ttm` 은 **이미 있어 새로 만들지 않았다.** F6-AVAIL-15 6절에서 확인한 대로 그 둘은 정의가 아니라 값을 채우는 문제였다.

셋 다 `PERIOD_REQUIRED_METRICS` 중 둘(`net_income_ttm`·`revenue_ttm_prior`)에 넣었다. TTM 흐름 지표는 기간 없이는 의미가 서지 않는다. `arr_prior` 는 비상장 런레이트라 기간 필수에서 뺐다 — 그 값 자체가 시점 기준이다.

### 2.2 F6 정책 검증을 모드별로 갈랐다

`v1.5`·`v1.6` 은 `bands`, `v1.7` 은 `parameters` 다. **과거 규칙 파일을 계속 읽을 수 있어야 하므로 한쪽을 지우지 않고 둘 다 검증한다.** 세 파일 모두 로드된다.

`parameters` 모드에서 새로 강제하는 것들.

| 검사 | 막는 사고 |
|---|---|
| 반개방 구간 정렬 (`upper` 오름차순 / `lower` 내림차순, 마지막 `null`) | 구간이 값을 못 덮는 상태 |
| bands 점수가 `score_range` 를 정확히 덮음 | 배점표와 선언이 어긋남 |
| `inputs` 의 metric 이 카탈로그에 존재 | 없는 metric 을 산식에 적어 영원히 pending |
| `p4.conditions[].id` 가 **구현된 id** | 선언만 있고 걸리지 않는 조건 |
| 트랙 `floor` 가 factor range 안 | 하한이 범위를 벗어남 |
| 파라미터 하한 합계 == factor range 하한 | 1.2 의 자기 검산 |

## 3. 계산기

`calc_f6.py` 는 `rules.f6_mode` 로 분기만 하고, 파라미터 경로는 `calc_f6_params.py` 로 뺐다. **v1.5·v1.6 경로는 한 줄도 바꾸지 않았다**(회귀 테스트로 고정, 6 절).

### 3.1 트랙은 선언된 기간 기준으로 정한다 — 설계 판단

**자료가 없다고 더 무른 트랙으로 내려보내지 않는다.**

처음에 "P1·P2 입력이 없으면 신규상장 트랙" 으로 잡으려다 멈췄다. 그러면 **일시적 자료 공백이 일반 상장사를 하한 −3 짜리 트랙으로 조용히 내려보내 점수를 후하게 만든다.** 부재가 감점을 지우는 구조는 위험하다.

그래서 트랙은 **관측이 선언한 `basis.period_basis`** 로 정한다.

| 선언 | 트랙 |
|---|---|
| `ttm` | `listed_ttm` |
| `annual` | `listed_annual` (ADR/FPI 는 `share_basis` 로도 판정) |
| `quarterly_yoy` | `listed_newly` |
| 없음 | **`pending_data`** — 트랙을 정하지 않는다 |

**티커로 분기하지 않는다.** SPCX 가 첫 10-K 를 내면 관측의 기준이 바뀌고 트랙도 따라 바뀐다. 하드코딩된 종목명이 없다.

그리고 **트랙이 기대하는 기준과 관측이 선언한 기준이 다르면 `pending_data`** 로 세운다. ADR 인데 관측이 `ttm` 이라고 하면 조용히 넘어가지 않는다.

### 3.2 이름이 아니라 선언을 읽는다 — PRIV-ARR-17 의 교훈 적용

`arr` 이 `kind=run_rate` 인데 이름만 ARR 이라 오독을 부른 일이 있었다. 그때 문제는 **표시가 없어서가 아니라 소비하는 쪽이 그 필드를 안 읽어서**였다.

같은 구조가 여기에도 있다. `revenue_ttm` 이라는 이름의 관측이 SPCX 에서는 분기 값이고 TSM·BABA 에서는 연간 값이다. 그래서 **소비하는 쪽이 `period_basis` 를 실제로 읽어 트랙을 정하고, 기대와 다르면 멈춘다.** 선언이 장식이 되지 않게 했다.

비상장 경로도 `arr` 관측의 `kind` 가 `run_rate` 면 `calc.kind_notes` 에 "ARR 이 아니라 런레이트" 를 남긴다.

### 3.3 P4 는 소계에 한 칸

조건이 여럿 걸려도 한 칸이다. 개별 파라미터가 아니라 **소계**에 건다 — 개별에 물리면 P1·P2 가 미산출인 트랙에서 적용 대상이 사라진다.

`nonop_share` 는 **원자료에서 재계산한다.** `net_income_ttm`·`operating_income_ttm` 이 있으면 `(NI − OI) / NI` 로 구하고, 저장된 완제품 `nonop_share` 관측과 1%p 넘게 다르면 **조용히 고르지 않고 경고로 남긴 뒤 재계산값을 쓴다.** 완제품만 들어와 재계산도 검증도 안 되던 상태를 반복하지 않는다.

## 4. 검산 대조 — 8/9 일치, oracle 한 건

`score_check.py` 는 **실제 계산기(`compute_f6`)를 그대로 태운다.** 손으로 다시 계산하지 않는다.

```
회사        트랙            P1        P2        P3      P4   F6  기준  판정
alphabet   listed_ttm    16.87(0)  8.97(-1)  20.1%(-1)  -1   -3   -3  일치
amazon     listed_ttm    20.33(0)  3.71(0)   15.8%(-1)  -1   -2   -2  일치
microsoft  listed_ttm    27.59(-1) 11.28(-1) 17.8%(-1)   0   -3   -3  일치
meta       listed_ttm    22.17(0)  6.71(0)   27.7%(-1)   0   -1   -1  일치
apple      listed_ttm    36.76(-1) 10.02(-1) 14.2%(-2)   0   -4   -4  일치
nvidia     listed_ttm    28.10(-1) 17.81(-1) 83.4%(0)    0   -2   -2  일치
palantir   listed_ttm   134.92(-2) 64.62(-2) 78.9%(0)    0   -4   -4  일치
tesla      listed_ttm   370.66(-2) 13.34(-1) 11.8%(-2)   0   -5   -5  일치
oracle     listed_ttm    25.97(-1)  8.60(-1) 17.3%(-1)   0   -3   -4  **불일치**
tsmc       listed_annual  1.86(0)   0.72(0)  33.9%(0)   -1   -1   기준 없음
alibaba    listed_annual  2.61(0)   0.25(0)   2.7%(-3)  -1   -4   기준 없음
spacex-xai listed_newly       -         -    91.9%(0)   -1   -1   기준 없음
anthropic  private            -         -        -       -  None  (밴드 미정)
openai     private            -         -        -       -  None  (밴드 미정)
```

설계 의도가 그대로 재현된다 — tesla −5(PER 370 에 성장 11.8%), palantir −4(PER 135 지만 성장 78.9% 라 P3 0), oracle 은 순차입 때문에 P/S 6.6 이 EV/Sales **8.60** 으로 올라가 P2 −1 이 된다.

### 4.1 oracle — 어느 쪽이 틀렸나

**산술이 아니라 TTM 창의 끝점 규약 차이다.** 성장률 자체가 갈린다.

| | 내 산출 | 검산 기준 |
|---|---|---|
| TTM 창 | **2025-06-01 ~ 2026-05-31** | TTM 26-02 |
| 성장률 | **+17.35%** → P3 −1 | +14.9% → P3 −2 |
| F6 | **−3** | −4 |

내 창의 구성은 이렇다.

```
2025-08-31  Q          14,926,000,000
2025-11-30  Q          16,058,000,000
2026-02-28  Q          17,190,000,000
2026-05-31  Q4_derived 19,183,000,000   ← FY 67,357 − (Q1+Q2+Q3) 48,174
합계                   67,357,000,000   ← FY2026 태깅값과 정확히 일치
직전 창                 57,399,000,000   ← FY2025 태깅값과 일치
```

**내 쪽이 맞다고 본다.** 근거 셋이다.

1. **oracle 의 TTM 은 FY2026 그 자체다.** 회계연도가 5월 말에 끝나고 FY2026 총액이 직접 태깅돼 있어, 내 4분기 합이 그 태깅값과 **정확히 일치**한다. 검산이 자명하다.
2. **확정 규칙이 `Q4 = FY − (Q1+Q2+Q3)` 복원을 명시한다.** 복원을 적용하면 oracle 의 Q4(2026년 3~5월)가 확보되므로, 그것을 빼고 2026-02-28 에서 끊으면 **이미 보고된 분기를 버리는 것**이 된다.
3. **다른 회사는 전부 최신 창을 쓴다.** 기준표의 meta·alphabet·amazon·tesla·palantir 는 TTM 26-06, nvidia 는 26-07 이다. oracle 만 26-02 인 것은 규약이 아니라 **복원 Q4 를 끝점으로 쓰지 않은 결과**로 보인다.

**같은 성질의 차이가 microsoft 에도 있다.** 내 창은 2025-07-01~2026-06-30(+17.79%), 기준은 TTM 26-03(+17.9%). 둘 다 15~30% 구간이라 **점수는 안 갈렸을 뿐**이다. 즉 이 규약 차이는 oracle 하나의 문제가 아니라 **회계 Q4 가 막 닫힌 두 회사(ORCL 5월·MSFT 6월)에 공통**이고, oracle 만 밴드 경계를 넘었다.

**결정이 필요하다.** "TTM 끝점 = 복원 Q4 를 포함한 최신 확보 분기" 인지 "직접 태깅된 최신 분기" 인지다. 내 구현은 전자다. 후자로 정하면 oracle −4 가 되고 microsoft 는 그대로다.

나머지 열 개사의 성장률은 **전부 0.11%p 이내**로 일치한다. 반올림 차이다.

## 5. SEC 수집기

`collect_ttm.py` 는 **F6-AVAIL-15 가 이미 받아 둔 `_raw/` 를 재사용한다. 신규 네트워크 호출이 없다.**

### 5.1 매출 태그 Coalesce — 그리고 그것이 필요했다

확정 규칙의 "매출 태그 Coalesce" 를 구현했다. **처음에 단일 개념만 골랐더니 alphabet 의 `revenue_ttm_prior` 가 나오지 않았다.** `Revenues` 계열에 2024년 4분기와 2024년 1분기가 비어 있어 직전 창이 연속하지 않았기 때문이다. 두 개념을 합치자 채워졌고 +20.05% 로 기준(+20.1%)과 맞았다.

혼합에는 F6-AVAIL-15 4.4 의 조건 둘을 그대로 달았다 — **혼합 사실을 기록하고, 겹치는 기간의 값을 검산한다.**

| 회사 | 겹침 불일치 | 2019년 이후 | 최대 상대오차 |
|---|---|---|---|
| oracle | 3 | **0** | 0.98% |
| tesla | 4 | **0** | 0.007% |
| 나머지 10사 | 0 | 0 | — |

**우리가 쓰는 구간(2019년 이후)은 불일치가 0건이다.** 불일치는 전부 ASC 606 전환기이고, 상대오차의 크기가 원인을 가른다(oracle 0.98% = 기준 차이, tesla 0.007% = 반올림). F6-AVAIL-15 에서 문서로만 적었던 검산이 **이제 파이프라인 안에서 돈다.**

### 5.2 현지통화

단위를 개념보다 **먼저** 고른다. TSM 은 TWD, BABA 는 CNY 다. 20-F 제출사는 현지통화와 USD 환산치를 함께 태깅하는데 각 연도가 그 해 기말환율로 환산되므로 공시 USD 로 성장률을 계산하면 왜곡된다(F6-FX-16). alibaba 가 그 사례다 — 현지통화 **+2.74%(−3)**, 공시 USD 로는 +8.1%(−2)로 **한 칸 갈린다.**

### 5.3 복원 근거를 함께 남긴다

`_derived/ttm_inputs.json` 에 TTM 값뿐 아니라 **구성 분기와 Q4 복원 근거(FY·Q1·Q2·Q3)** 를 담았다. 파생값을 완제품으로만 남기지 않는다.

## 6. 테스트 — 113 → 137건

신규 24건은 `tests/test_scorecard_f6_v17.py` 다.

| 묶음 | 고정하는 것 |
|---|---|
| `TestF6ParameterBands` | 반개방 경계(P1·P2 미만 / P3 이상), 파라미터 하한 합계 == −7, 함정 합 == −18 |
| `TestF6Tracks` | 트랙 선택, ADR 자동 P4, 기준 불일치 pending, **입력 부재가 트랙을 낮추지 않음** |
| `TestF6ParameterGuards` | 적자 시 pending(낮은 PER 대체 금지), EV 가 순현금을 뺌, 경계 표시가 점수를 안 바꿈 |
| `TestF6P4` | 재계산 우선·저장값 불일치 경고, 조건 여럿이어도 한 칸, 하한 절단(−7·−3) |
| `TestF6Private` | 점수 없음·배수 계산, `run_rate` 종류 노출 |
| `TestF6LegacyModeUnaffected` | **v1.5·v1.6 이 per_band 경로를 그대로 씀** |

가장 중요한 것은 `test_missing_input_does_not_demote_track` 이다. 3.1 의 설계 판단이 코드에서 유지되는지를 본다.

## 7. 불변 확인

| 대상 | 결과 |
|---|---|
| `v1.5.json` · `scorecard/runs/` · `output/` | `git diff` **공집합** |
| 승인 해시 `rules` | v1.5 해시 **일치** |
| `results_hash` | **`0942c342…`** 일치 |
| HTML | `e6cc960c1c50f412` · 213,851 B 불변 |
| `v1.7` status | `draft` |

`api.nasdaq.com` 미호출. 신규 네트워크 호출 없음.

## 8. 남은 결정

1. **oracle — TTM 창 끝점 규약**(4.1). 밴드 한 칸이 걸린다.
2. **비상장 밴드.** 지금은 `pending_rule_decision` 이라 anthropic·openai 가 점수를 받지 않는다.
3. **환율 출처 allowlist 등재.** `f6.fx` 가 `pending_source_allowlist` 다. TSM·BABA 의 P1·P2 는 **현지통화 그대로** 계산돼 있어 시총(USD)과 통화가 어긋난다 — 아래 4번과 함께 봐야 한다.
4. **TSM·BABA 의 P1·P2 가 지금은 의미가 없다.** 시총은 USD 인데 순이익·매출이 TWD·CNY 라 배수가 1.86·2.61 로 나온다. 환율이 붙기 전까지 **이 두 수치를 읽지 말아야 한다.** P3 는 현지통화끼리의 비율이라 영향이 없고 지금도 유효하다. 환율 등재 시 P1·P2 만 다시 계산하면 된다.
5. **관측 등록.** 이번 산출은 `_derived/` 에만 있고 `observations.json` 에 넣지 않았다. 등록은 별도 승인 절차다.

## 9. 재현 방법

```bash
cd worker/validation/f6-spec-18
python collect_ttm.py      # f6-avail-15/_raw 재사용 · 네트워크 없음
python score_check.py      # 실제 계산기로 F6 산출 후 검산 대조
cd ../.. && python -m unittest discover -s tests -q   # 137건
```

| 파일 | 커밋 | 내용 |
|---|---|---|
| `scorecard/rules/v1.7.json` | O | 신설 규칙 |
| `scripts/scorecard/calc_f6_params.py` | O | 파라미터 계산기 |
| `scripts/scorecard/calc_f6.py` · `schema.py` · `rules.py` | O | 모드 분기·metric 3종·검증·밴드 헬퍼 |
| `tests/test_scorecard_f6_v17.py` | O | 신규 24건 |
| `collect_ttm.py` · `score_check.py` | O | 수집기·대조기 |
| `collect-output.txt` · `score-check-output.txt` | O | 실행 결과 |
| `_derived/ttm_inputs.json` | O | TTM 과 복원 근거 |
| `_raw/` | **X** | 없음(F6-AVAIL-15 것을 재사용) |
