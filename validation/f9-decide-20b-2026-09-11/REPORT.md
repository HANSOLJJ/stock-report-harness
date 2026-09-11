# F9-DECIDE-20B — F9 미결 규칙 5건 독립 조사

- 지시 원문: `msg_b5b20b9979f1` (run `run_1243c2a83479`)
- 조사일: 2026-09-11
- **결정하지 않았다.** 선택지별 영향을 실측으로만 보인다
- 대상 자료: `worker/scorecard/runs/ai-scorecard-2026-09-baseline/` (읽기 전용)
- C-13 에 같은 과제가 독립 배정됐다. **상대 결과를 참조하지 않고 각자 산출했다**

> **2026-09-11 개정 (R1).** 설계진행 재검토(`f2a92a1`, `needs_fix`)를 반영했다. 초판의 0절 표·3절·7절 세 곳이 **틀렸다.** 원인은 자체 시뮬레이터가 출하 엔진과 어긋난 것이다. **이번 개정은 자체 시뮬레이터를 쓰지 않고 출하 엔진 `scripts/scorecard/calc_f9.py` 의 `compute_f9()` 를 직접 호출해 16개 조합을 돌린 결과다**(`engine_matrix.py`, `engine-matrix-output.txt`). 개정 내역은 §12 에 있다.

## 0. 결론 — 무엇이 점수를 움직이고 누가 풀리는가

**다섯 중 점수를 움직이는 것은 둘뿐이고, 기업을 푸는 것은 하나뿐이다.**

| 결정 | 점수 변동 | 미완료를 푸는가 | 영향 기업 (출하 엔진 실측) |
|---|---|---|---|
| **C-06** 밴드 확정 | **있음** | **푼다** | **spacex-xai** `None(needs_rule_decision)` → **−4** |
| **C-05** `diagnose_only`→`apply` | **있음** | **되레 막는다** | **spacex-xai** −4 → **`None(needs_judgment)`** |
| **C-16** `hold`→`downgrade` | **없음** | 못 푼다 | **0개사** |
| **C-04** `exclude`→`include_v15` | **없음** | 못 푼다 | **0개사** |
| **C-07** `ARR 대체 금지` 확정 | 없음 | 못 푼다 | 이미 `incompatible_basis` 반영됨 |

**지금 자료에서 미완료를 푸는 조합은 `C-06 확정 + C-05 diagnose_only` 하나뿐이고, 그때 풀리는 기업은 spacex-xai 하나다.**

**amazon·alibaba·anthropic 은 16개 조합 전부에서 풀리지 않는다.** 엔진을 16회 돌려 확인했다(`never resolved: amazon, alibaba, anthropic`).

- alibaba·anthropic: G1 에서 `operating_result_reviewed: unknown` → `pending_data`
- **amazon: 관문이 둘이다.** `coverage_comparable: unknown` 이라 C-16 에 닿기 전에 `needs_judgment` 로 멈추고, 그 관문을 `yes` 로 강제로 넘겨도 **`contracted_revenue` 의 status 가 `parse_failed`** 라 `pending_data` 로 빠진다. **C-16 은 amazon 을 풀지 못한다** (엔진으로 양쪽 다 확인).

**지시서의 전제 하나를 정정한다.** "미완료 5개사 중 3개가 F9 에서 막혀 있고 amazon 은 needs_judgment, alibaba·anthropic 은 pending" 이라고 하셨는데, 실측하면 **F9 점수가 `None` 인 기업은 4개**다. amazon(`needs_judgment`), alibaba·anthropic(`pending_data`), 그리고 **spacex-xai(`needs_rule_decision`, 사유가 바로 C-06)** 이다. spacex-xai 가 누락돼 있었고, 공교롭게 **이번 결정으로 가장 확실히 풀리는 기업**이다.

**가장 큰 발견은 따로 있다. F9 의 진입 게이트 G1 이 요구하는 입력이 사실상 없다.** `operating_margin_ttm` 1/14, `revenue_ttm` **0/14**, `operating_income_ttm` **0/14** 다. 손실률을 계산할 수도, 유도할 수도 없다. 지금 10개사가 G1 을 통과하는 근거는 수치가 아니라 **검토 입력 `operating_result_reviewed=profit`** 이고, 엔진도 경고를 달고 있다("TTM 영업손익 수치 없이 검토된 부호로 통과"). **C-06 의 다섯 공백 중 넷은 현재 자료에서 아무 기업도 건드리지 못한다.** 규칙이 없어서가 아니라 판정할 입력이 없어서다.

## 1. 계산 규약 — 스스로 세우고 근거를 적는다

직전 라운드에서 두 워크트리가 같은 규약을 써서 12/12 일치했는데 둘 다 틀렸다고 하셨다. **일치를 정답의 근거로 쓰지 않기 위해 규약을 명시적으로 정의하고 그 선택 이유를 적는다.** 기존 F9 점수는 정답 fixture 로 쓰지 않았다.

| 규약 | 내용 | 근거 |
|---|---|---|
| R1 | 게이트 순서·동작은 `design-guideline.md` 6.2 표를 따른다 | 계약 문서가 유일한 규범 원천 |
| R2 | G1 진입은 `operating_result_reviewed`. profit=통과, loss=밴드, unknown=pending | 6.1 "단일 분기 흑자를 TTM 영업흑자로 대체하지 않는다" |
| R3 | **G3·G4 는 FCF 음수일 때만 도달한다** | 6.2 가 G2 에서 "FCF 음수는 기본 −2 에서 G3 진행" 이라고만 적고 양수 경로의 후속 진행을 규정하지 않는다 |
| R4 | 하한 −5 | `policies.f9.floor` |
| R5 | `direction_A`·`B` 가 모두 unknown 이면 방향 완화 미적용 | 6.3 "자료 부족으로 완화 요건을 입증하지 못한 경우 완화를 적용하지 않는다" |
| R6 | 값이 없으면 추정하지 않고 pending | 지시 조건 |

**R3 은 출하 엔진 구현과 정확히 일치한다**(설계진행 재검토 확인). `fcf > 0` 이면 G2 에서 즉시 반환하고 G3·G4 로 가지 않는다.

> **R1 정정.** 초판은 여기에 "다르게 읽으면 C-16 영향 범위가 10개사로 늘어난다" 고 적었는데 틀렸다. `_g4()` 는 `coverage_comparable == "yes"` 여야만 결측 유형 분기(C-16)에 닿는다. 그 11개사는 전부 `unknown` 이라 **어느 독해에서도 C-16 에 닿지 않는다.** R3 을 다르게 읽으면 그 기업들이 C-16 영향권에 들어오는 것이 아니라, 지금 `ok` 인 점수가 `needs_judgment` 로 후퇴할 뿐이다. **R3 은 결론을 가르지 않는다.**

## 2. C-06 다섯 공백의 실측

| 공백 | 실측 | 지금 점수를 움직이는가 |
|---|---|---|
| 손실률 −10%·−30% 경계 중첩 | **정확히 경계값인 기업 0개.** 손실률 보유 자체가 1/14(spacex-xai −0.149) | **아니오** (단, 밴드가 `proposed` 라 spacex-xai 가 보류 중) |
| FCF·영업손익 0 | `fcf_ttm == 0` **0개사**. `operating_income_ttm` 지표 자체가 **0/14** | **아니오** |
| 완충 잠식 | `buffer_erosion` 이 **14/14 전부 `no`**. 엔진이 읽는 `undrawn_credit` 관측 **0건** | **아니오** |
| G2 안정/악화 기계 정의 | `fcf_ttm` 이 기업당 **1개 시점뿐**이라 전기 대비도 추세도 계산 불가 | **아니오** (현재 값은 검토 입력이지 계산 결과가 아님) |
| BEP 후퇴 × 손실률 우선순위 | `bep_retreat=yes` 는 **openai 1개사뿐**이고, 그 openai 는 손실률 수치가 **없다** | **아니오** — 충돌이 실제로 발생하는 기업 **0개** |

**다섯 중 지금 점수를 움직이는 것은 "밴드를 확정했는가" 하나뿐이다.** 경계 귀속·0 처리·완충 잠식·G2 기계 정의·BEP 우선순위는 전부 **명문화는 필요하지만 현재 자료로는 아무 기업도 바꾸지 않는다.**

### 2.1 경계 귀속은 두 해석이 한 칸 갈린다

`v1.5` 의 `g1_bands_proposed` 배열과 `g1_bands_status` 문자열을 두 가지로 읽을 수 있다.

| m | 해석A (포함, status 문자열 `-10% <= m < 0 → -3`) | 해석B (배제, 경계를 나쁜 쪽에 귀속) |
|---|---|---|
| 정확히 −0.10 | **−3** | **−4** |
| 정확히 −0.30 | **−4** | **−5** |

경계 바깥은 두 해석이 일치한다(−0.0999999→−3, −0.3000001→−5 확인). **해당 기업이 0개라 지금은 무해하지만, 새 기업이 경계에 앉으면 한 칸이 갈린다.**

### 2.2 G2 안정/악화는 자료가 없어서 기계화할 수 없다

이것이 "판정에 필요한 입력이 자료에 없으면 그 사실이 결론" 에 해당하는 항목이다. 현재 `fcf_trend` 분포는 `stable 5 / deteriorating 3 / unknown 6` 인데, **이 값들은 계산된 것이 아니라 사람이 넣은 검토 입력이다.** 관측에는 기업당 `fcf_ttm` 이 한 시점만 있어 전기 대비 비교 자체가 불가능하다.

기계로 가르려면 최소한 **직전 기간의 같은 정의 TTM FCF** 가 필요하다. 6.3 이 방향 완화 A 에 "통상 8개 분기 자료 또는 검증된 네 개의 YoY 비교 쌍" 을 요구하는 것과 같은 성격의 요구다. **지금 정의를 확정해도 적용할 수치가 없다.**

## 3. C-05 — `diagnose_only` 대 `apply`

**점수가 달라지는 기업은 spacex-xai 하나다.**

| 기업 | G1 | `diagnose_only` | `apply` |
|---|---|---|---|
| **spacex-xai** | fail (m=−0.149 → −4) | **−4** | **`None` (needs_judgment)** |
| openai | fail (BEP 후퇴 → −5) | −5 | −5 (이미 하한, G3/G4 skip) |
| alibaba·anthropic | pending (입력 없음) | `pending_data` | `pending_data` |
| 나머지 10개사 | pass (profit) | 해당 없음 | 해당 없음 |

**G1 이 실패하는 기업 자체가 2개뿐이고, 그중 openai 는 이미 하한 −5 라 추가 감점이 불가능하다**(엔진이 `G3/G4 skipped: G1 점수가 이미 하한(-5)이라 추가 감점 불가` 를 남긴다). 그래서 C-05 의 실질 영향은 spacex-xai 하나다.

**`apply` 경로의 실제 동작 (출하 엔진 기준).** 초판은 여기서 틀렸다. **G1 실패 분기는 G2 를 다시 세지 않는다.** 엔진은 G1 실패 시 G2 를 건너뛰고 곧바로 G3·G4 **진단**으로 간다.

```
G1  m=-0.149 → proposed 밴드 → -4
G3  진단: runway = 100B / 32.5B = 3.0769년 ≥ 3 → step 0 → -4 유지
G4  진단: coverage_comparable=unknown → step=None, pending(judgment)
C-05=apply  → g4_pending 이 있으므로 done(None, needs_judgment)
```

즉 **`apply` 는 spacex-xai 를 −5 로 만들지 않는다. `None(needs_judgment)` 로 되돌린다.** 초판이 적은 "G2 −2 를 더해 −5" 는 엔진에 없는 경로였다.

**이 점이 결정에 중요하다.** `apply` 는 "적자 기업을 현금·약정으로 차등한다" 는 취지인데, 지금 자료에서는 **차등을 만들기는커녕 이미 풀려 있던 기업을 다시 미완료로 되돌린다.** G4 판정 입력(`coverage_comparable`)이 없기 때문이다.

**조건부로는 차등이 생긴다.** `coverage_comparable` 을 `yes` 로 가정하고 엔진을 돌리면 이렇게 갈린다.

| spacex-xai (`coverage_comparable=yes` 가정) | C-16=`hold` | C-16=`downgrade` |
|---|---|---|
| C-05=`diagnose_only` | −4 | −4 |
| C-05=`apply` | −4 | **−5** |

**`apply` × `downgrade` 조합에서만 −5 가 된다.** 다만 이것은 현재 자료에 없는 입력을 가정한 결과이므로 **지금 점수가 아니라 조건부 전망**이다.

## 4. C-16 — `hold` 대 `downgrade`

**점수가 달라지는 기업이 0개다.** 초판은 amazon 이 풀린다고 적었으나 틀렸다.

이유는 엔진의 `_g4()` 가 **C-16 에 닿기 전에 관문을 둘 두기 때문이다.**

1. `coverage_comparable != "yes"` 이면 곧바로 `undetermined` + `pending(judgment)` 로 반환한다. 코드 주석이 명시한다 — *"숫자가 있어도 확정하지 않고, **결측 정책(C-16)으로도 보내지 않는다**"*.
2. `yes` 를 통과해도, 값이 비었을 때 **status 가 `not_disclosed` 인 경우에만** C-16 분기에 닿는다. `parse_failed`·수집 실패·관측 부재는 `pending(data)` 다. 주석이 *"수집 실패를 미공시 위험으로 둔갑시키지 않음"* 이라고 적는다.

| 기업 | `coverage_comparable` | 값 상태 | C-16 에 닿는가 | `hold` | `downgrade` |
|---|---|---|---|---|---|
| **amazon** | `unknown` | `contracted_revenue` = **`parse_failed`** | **아니오 (관문 2개 다 막힘)** | `None` | `None` |
| oracle | `yes` | 양쪽 값 있음 (coverage 2.552) | 아니오 (계산됨) | −3 | −3 |
| spacex-xai | `unknown` | `offbalance_B` = `not_disclosed` | 아니오 (관문 1 에서 막힘) | 해당 없음 | 해당 없음 |
| anthropic·openai | `no` | `incompatible_basis` | 아니오 (C-07 경로) | 해당 없음 | 해당 없음 |

**amazon 을 엔진으로 직접 확인했다.** `coverage_comparable` 을 `yes` 로 강제해도 `contracted_revenue` 가 `parse_failed` 라 `hold`·`downgrade` 양쪽 모두 `None(pending_data)` 다. **C-16 은 어느 쪽을 골라도 amazon 을 풀지 못한다.**

**즉 C-16 은 지금 자료에서 적용 대상이 0개다.** 규칙이 나쁜 것이 아니라 **엔진이 이미 결측 유형을 구분하고 있어서** `not_disclosed` 가 아닌 결측은 C-16 으로 가지 않는다. 초판이 우려한 "자료 수집 실패를 미공시 위험으로 둔갑" 문제는 **엔진이 이미 막아 두었다.**

다만 §9 에 적었던 관찰은 유효하다. amazon 의 `coverage_comparable` 이 `unknown` 인 이유가 미공시인지 미확인인지 자료에 구분이 없다. **초판의 잘못은 이 단서를 §9 에 적어 놓고 0절 결론에서는 amazon 을 C-16 대상으로 다룬 것이다.** 자기가 찾은 단서를 자기 결론에 반영하지 않았다.

## 5. C-04 — 영향 0

**`exclude` 와 `include_v15` 사이에 점수가 달라지는 기업이 0개다.**

이유는 규칙이 아니라 자료다. `include_v15` 는 신용등급 기반 조달 여력을 완충에 넣는 선택인데, **그 여력을 수치로 넣을 관측이 없다.** `credit_rating` 은 14/14 있지만 등급→금액 환산 규칙도, `undrawn_credit_facility` 관측도 없다(**0/14**). 완충에 더할 숫자가 없으므로 어느 쪽을 골라도 G3 런웨이가 그대로다.

G3 에 실제로 도달하는 기업은 FCF 음수인 amazon·alibaba·spacex-xai·oracle 4개사인데, 넷 다 완충이 `cash` 단독으로 계산된다.

**따라서 C-04 는 지금 "어느 쪽을 골라도 같다".** 다만 별표 J(신용등급의 점수 개입 금지)와 G3 의 충돌을 문서에서 해소하는 의미는 남는다. 점수 영향이 없다는 것이 곧 결정이 불필요하다는 뜻은 아니다.

## 6. C-07 — 이미 반영돼 있다

`ARR 대체 금지` 를 확정해도 **새로 미완료가 되는 기업은 없다.** anthropic·openai 의 `contracted_revenue` 가 이미 `incompatible_basis` 로 처리돼 있고, 두 기업은 그보다 앞선 G1 에서 이미 막혀 있다(anthropic `pending_data`, openai 는 BEP 후퇴로 −5 확정).

`arr` 관측은 anthropic·openai 2개사뿐이고, 6.4 가 "ARR/연환산 약정은 G4 커버리지가 아니다" 라고 이미 명시한다. **확정은 문서 정리이지 점수 변경이 아니다.**

## 7. 다섯이 얽히는 지점

지시서가 짚은 대로 **C-05 와 C-06 은 따로 정하면 어긋난다.** 실측으로 확인한 얽힘은 셋이다.

**얽힘 1 — C-06 × C-05 가 같은 기업(spacex-xai)에 순차로 걸린다.** C-06 이 밴드를 확정해야 G1 이 −4 를 내고, 그 다음에야 C-05 가 −4 로 멈출지 −5 로 갈지를 정한다. **C-06 을 안 정하면 C-05 는 적용 대상이 아예 없다.** 순서가 있다.

| C-06 | C-05 | spacex-xai |
|---|---|---|
| 미확정 | (무관) | `None` needs_rule_decision |
| 확정 | `diagnose_only` | **−4** |
| 확정 | `apply` | **−5** |

**얽힘 2 — BEP 우선순위는 C-05 요약과 C-06 다섯째가 같은 사안이다.** 두 곳에 나뉘어 적혀 있는데 실제로는 하나의 규칙이다. 다행히 **현재 충돌 기업이 0개**라 지금 어긋나도 점수는 안 갈린다. 그러나 `design-guideline.md` 의 T-10 이 "C-05/C-06 결정표와 일치" 를 요구하므로, **두 곳에 따로 쓰면 T-10 이 깨진다.** 한 곳에 쓰고 다른 곳이 참조하는 형태를 권한다.

**얽힘 3 — 방향이 반대다. `apply` 라야 C-16 이 spacex-xai 에 닿는다.** 초판은 "`apply` 가 C-16 을 무력화한다" 고 적었는데 정반대였다.

`diagnose_only` 면 엔진이 G1 점수 −4 로 확정하고 G3·G4 는 진단 기록만 남긴다(`G1-after applied=False`). **G4 결과가 점수에 반영되지 않으므로 C-16 선택이 아예 걸리지 않는다.** `apply` 를 골라야 G4 가 점수 경로에 들어오고, 그래야 C-16 이 의미를 갖는다.

`coverage_comparable=yes` 를 가정한 엔진 실행이 이를 보인다 — `apply`+`downgrade` 에서만 −5 가 되고 나머지 셋은 −4 다(§3 표).

**따라서 C-05 와 C-16 의 선후는 이렇다.** C-06 이 밴드를 확정해야 C-05 가 대상을 갖고, C-05 가 `apply` 여야 C-16 이 대상을 갖는다. **셋이 순차 의존이다.** 다만 현재 자료에서는 `coverage_comparable` 이 없어 `apply` 가 차등이 아니라 `needs_judgment` 를 낳으므로, **세 번째 고리는 아직 작동하지 않는다.**

## 8. 검증

`verify-output.txt` 전문이다. **FAIL 0건.**

**통과 방향 양성 대조** — 밴드 함수가 각 구간에서 실제로 그 값을 내는지 확인했다. m=−0.05→−3, −0.20→−4, −0.50→−5, spacex-xai 실측 −0.149→−4 전부 통과. 경계 바깥 −0.0999999→−3, −0.3000001→−5, 0.0→`not_loss` 통과.

**입력 변경 테스트** — 입력을 바꾸면 점수가 기대 방향으로 움직이는지 확인했다.

| 변경 | 결과 |
|---|---|
| spacex-xai 손실률 −0.149 → −0.05 (완화) | −4 → **−3** |
| spacex-xai 손실률 −0.149 → −0.40 (악화) | −4 → **−5** |
| spacex-xai `buffer_erosion` no → yes | 하한 −4 적용 확인 |
| oracle 현금 31.9B → 200B (완충 증가) | −3 → **−2** (런웨이 상승으로 G3 감점 해소) |

**경계 귀속은 pass/fail 이 아니라 두 해석 대조로 남겼다.** 초판에서 이걸 FAIL 2건으로 처리했는데, 내 테스트 기대값이 해석B 를 인코딩한 것이라 구현 오류가 아니라 **모호성 자체의 발현**이었다. §2.1 의 표가 그 결과다.

## 9. 확인하지 않은 것

- **다른 factor 로의 파급.** F9 점수 변동이 종합 순위를 어떻게 바꾸는지 계산하지 않았다. 이번 과제 범위 밖이고 `results_hash` 불변 조건도 있다
- **alibaba·anthropic 의 TTM 영업손익을 어디서 구할 수 있는지.** 규칙 조사 범위 밖이다. 다만 alibaba 는 `us-gaap:OperatingIncomeLoss` 가 SEC 에 있으므로(F6-FX-16 에서 확인) 수집 경로 자체는 존재한다
- **`coverage_comparable: unknown` 11개사 중 amazon 외 10개사.** R3 에 따라 G4 에 도달하지 않아 계산하지 않았다. **R3 을 다르게 읽으면 이 10개사가 C-16 영향권에 들어온다**
- **amazon 의 `unknown` 이 미공시인지 미확인인지.** 자료에 사유가 구분돼 있지 않다
- 신규 네트워크 수집은 하지 않았다. 필요 없었다

## 10. 산출물

| 파일 | 내용 |
|---|---|
| `REPORT.md` | 이 보고서 |
| `extract_f9_inputs.py`, `f9-input-inventory.json` | F9 필수 입력 보유 현황 (G1 입력 부재의 근거) |
| `extract_f9_state.py`, `f9-current-state.json` | 현재 게이트 경로·보류 사유 (정답이 아니라 상태로만 사용) |
| `simulate_f9.py`, `f9-simulation.json` | 초판 자체 시뮬레이션. **구현과 어긋나 R1 에서 대체됨. 이력 보존용이며 결론 근거가 아니다** |
| `verify_and_c06.py`, `verify-output.txt` | 양성 대조·입력 변경 테스트·C-06 다섯 공백 실측 |
| **`engine_matrix.py`, `engine-matrix.json`, `engine-matrix-output.txt`** | **R1 정정 근거 — 출하 엔진 `compute_f9()` 직접 호출 16조합** |

## 11. 조건 준수

- **결정하지 않았다.** 선택지별 영향만 실측으로 제시했다
- **기존 F9 점수를 정답 fixture 로 쓰지 않았다.** `f9-current-state.json` 은 보류 사유와 검토 입력을 읽는 데만 썼고, 시뮬레이터는 계약 문서(6.1~6.4)와 `policies.f9` 에서 독립적으로 구성했다. S-HAND 검산 사례(Oracle −3, SpaceX −4, OpenAI −5, Amazon −2)를 기준으로 삼지 않았다
- 판정 변수를 계산해 놓고 출력에 안 쓰지 않았다. 한 행·한 필드 표본으로 전체를 판정하지 않았고 14개사 전수로 집계했다
- 없는 것은 없다고 적었다. `revenue_ttm` 0/14, `operating_income_ttm` 0/14, `undrawn_credit_facility` 0/14 가 결론의 일부다
- 입력 변경 테스트와 통과 방향 양성 대조를 남겼다
- **점수·규칙·승인·원자료를 변경하지 않았다.** `worker/` 는 읽기 전용으로만 읽었고 `v1.5`·`v1.7.json`·`scripts/scorecard/` 를 건드리지 않았다
- `api.nasdaq.com` 호출 0건. 신규 네트워크 수집 0건
- C-13 의 결과를 참조하거나 기다리지 않았다
- **R1 에서 worker 의 `scripts/scorecard/` 를 `import` 로 읽기만 했고 수정하지 않았다.** `v1.5`·`v1.7.json`·승인 해시·`results_hash` 불변

## 12. 수정 이력 (R1, 2026-09-11)

설계진행 재검토 `f2a92a1` 의 `needs_fix` 3건을 반영했다. **판정 근거는 자체 시뮬레이터가 아니라 출하 엔진 직접 호출이다.**

| # | 초판 | 정정 | 근거 |
|---|---|---|---|
| 1 | 0절·4절: C-16 `downgrade` 가 amazon 을 −3 으로 푼다 | **C-16 은 0개사.** amazon 은 `coverage_comparable=unknown` 에서 먼저 막히고, `yes` 로 강제해도 `contracted_revenue=parse_failed` 라 `pending_data` | 엔진 16조합 + `yes` 강제 실행 |
| 2 | 3절: `apply` 시 spacex-xai 가 G2 −2 를 더해 −5 | **G1 실패 분기는 G2 를 다시 세지 않는다.** G3 런웨이 3.0769년 step 0 → −4 유지, G4 pending → **`None(needs_judgment)`** | `calc_f9.py` G1 실패 분기 + 엔진 실행 |
| 3 | 7절 얽힘 3: `apply` 가 C-16 을 무력화 | **반대다.** `diagnose_only` 면 G4 가 점수에 안 들어와 C-16 이 안 걸린다. `apply` 라야 C-16 이 닿는다 | 엔진 `G1-after applied=False` 경로 |

**근본 원인.** 초판은 계약 문서에서 자체 시뮬레이터를 구성했는데, 그것이 구현과 어긋났다. 특히 (a) G1 실패 뒤 G2 재계산 여부, (b) `_g4()` 의 결측 유형 분기를 잘못 모델링했다. **독립 시뮬레이터는 규칙 해석을 검증하지만 구현과의 일치는 검증하지 않는다.**

보조 원인이 하나 더 있다. `extract_f9_inputs.py` 가 관측의 `value` 만 읽고 **`status` 를 버렸다.** 그래서 amazon 의 `contracted_revenue` 가 `parse_failed` 인 것을 초판이 `-`(없음)로만 보았다. §9 에 "미공시인지 미확인인지 구분이 없다" 고 적어 놓고 결론에 반영하지 못한 것도 같은 뿌리다.

**초판에서 유지되는 것** — 지시서 전제 정정(F9 `None` 4개사, spacex-xai 누락), G1 입력 공백 발견(`operating_margin_ttm` 1/14, `revenue_ttm` 0/14, `operating_income_ttm` 0/14), C-06 다섯 공백 실측, 규약 R3. 설계진행이 전수 재현해 확인했고 R3 은 구현과 정확히 일치한다고 확인받았다.

**작은 정정 둘.** 초판이 적은 지표명 `undrawn_credit_facility` 는 엔진이 실제로 읽는 이름이 **`undrawn_credit`** 이다. 이름과 무관하게 관측은 **0건**이므로 C-04 = 0개사 결론은 유지된다. 그리고 §4 표의 spacex-xai 행이 "하한 도달" 이라 적었던 것은 정정 2에 따라 "관문 1(`coverage_comparable`)에서 막힘" 이 맞다.
