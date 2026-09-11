# F9-DECIDE-20 / 20B 2자 재검토 — F9 미결 5건

- 검토일. 2026-09-11.
- 대상. C-13 `3651c7b` · NTM `36cbca7`.
- 판정. **C-13 `needs_fix` · NTM `needs_fix`.** 둘 다 값진 것을 찾았고 **둘 다 핵심 결론이 틀렸다.**
- **정정.** 아래 "독립 시뮬레이터" 진단은 NTM 에만 맞다. C-13 의 시뮬레이터와 산출 JSON 은 엔진과 일치했고 **서술만 자기 산출물과 어긋났다.** `f9-decide-20-r2-review.md` 에서 정정했다.

## 재현 방법

두 보고서 중 어느 쪽도 정답으로 쓰지 않았다. **출하된 엔진(`calc_f9.py`)을 그대로 불러 16개 조합을 직접 돌렸다.** 기존 점수를 fixture 로 쓰지 않았고, 결정 오버라이드만 `run.decisions` 에 넣어 비교했다.

## 결론 — 지금 자료에서 점수를 움직이는 것은 **하나**다

| 조합 | 변동 기업 |
|---|---|
| C-06 + C-05 `diagnose_only` | **spacex-xai** `needs_rule_decision` → **−4 (ok)** |
| C-06 단독 | spacex-xai → `needs_judgment` (막힘이 옮겨갈 뿐 안 풀림) |
| C-05 `apply` | spacex-xai → `needs_judgment` |
| **C-16 `hold`·`downgrade`** | **0개사** |
| C-04 `include_v15` | 0개사 |
| C-07 | 이미 반영 |

나머지 13개사는 16개 조합 전부에서 값이 같다. amazon 은 어느 조합에서도 `needs_judgment`, alibaba·anthropic 은 어느 조합에서도 `pending_data` 다.

## C-16 은 지금 **아무도 도달하지 못한다** — 둘 다 놓쳤다

`_g4()` 의 분기 순서가 결정적이다.

```python
if comparable == "no":   → C-07 경로, 자료 대기
if comparable != "yes":  → needs_judgment. 주석에 "결측 정책(C-16)으로도 보내지 않는다 (R02)"
# comparable == "yes" 여야만 숫자를 보고, 그래야만 결측 유형 분기와 C-16 에 닿는다
```

**`coverage_comparable` 실측 분포는 `yes` 1 · `no` 2 · `unknown` 11 이다.**

| 값 | 기업 | G4 귀결 |
|---|---|---|
| `yes` | oracle | 숫자로 계산됨(커버리지 2.552) → C-16 불필요 |
| `no` | anthropic · openai | C-07 경로 → C-16 대상 아님 |
| `unknown` | 나머지 11개사 | **C-16 이전에 `needs_judgment` 로 멈춘다** |

그리고 `coverage_comparable` 은 **관측이 0건**이다. 판단 입력이라 `judgments.json` 에만 있고 14개사 전부 v1.5 승계값이다.

**따라서 C-16 을 오늘 `hold` 로 정하든 `downgrade` 로 정하든 점수는 한 칸도 안 바뀐다.** 막고 있는 것은 규칙 공백이 아니라 **`coverage_comparable` 이라는 검토 입력의 부재**다. C-13 은 C-16 이 alibaba 를 가른다고 했고 NTM 은 amazon 을 푼다고 했는데, **실행하면 둘 다 아니다.**

## C-13 — `needs_fix`

### 틀린 것 — alibaba 전제를 하나만 적었다

C-13 은 "alibaba 는 계약 수입·B종 약정이 모두 `not_disclosed` 이므로 C-16 이 −2 와 −3 을 가른다" 고 했고, 해소 경로로 `operating_result_reviewed = profit` **하나만** 들었다.

실행하면 이렇다.

```
alibaba + profit                      → needs_judgment (coverage_comparable 검토 입력 필요)
alibaba + profit + coverage=yes  hold → -2 (ok)
alibaba + profit + coverage=yes  down → -3 (ok)
```

**−2/−3 숫자는 정확하다. 다만 입력이 하나가 아니라 둘이다.** `coverage_comparable: unknown` 게이트를 건너뛰었다. 그 결과 "C-16 결정 시 즉시 완료" 로 읽히는데 실제로는 C-16 을 정해도 안 풀린다.

### 맞은 것 — amazon `parse_failed` 판정이 정확하다

**이번 라운드에서 가장 값진 발견이다.** C-13 은 amazon 의 `contracted_revenue` 가 `not_disclosed` 가 아니라 `parse_failed` 이므로 C-16 대상이 아니라고 했다. 원자료로 확인했다.

```
amazon      contracted_revenue = null / parse_failed     offbalance_B = 106,000,000,000
alibaba     contracted_revenue = null / not_disclosed    offbalance_B = null / not_disclosed
```

`coverage_comparable=yes` 를 넣어 강제로 G4 에 태워도 amazon 은 이렇게 나온다.

```
amazon + coverage=yes, C-16 어느 쪽이든 → pending_data
  "G4 자료 미수집/파싱 실패: contracted_revenue(parse_failed) — 수집 실패를 미공시 위험으로 둔갑시키지 않음"
```

설계 지침 6.4 마지막 문장 그대로다. **C-13 이 이 구분을 지켰고 NTM 은 못 지켰다.**

### 맞은 것 — spacex 경로가 정확하다

`apply` 에서 G4 판단 대기로 막히고, 판단이 `yes` 면 C-16 이 −4/−5 를 가른다는 서술이 실행과 일치한다.

```
spacex + coverage=yes  apply + hold      → -4 (ok)
spacex + coverage=yes  apply + downgrade → -5 (ok)
spacex + coverage=yes  diagnose_only     → -4 (ok)
```

C-04 의 런웨이 수치도 전부 맞다. amazon 10.6년(123/11.6) · oracle 1.35년(31.9/23.7) · spacex 3.08년(100/32.5).

## NTM — `needs_fix`

### 틀린 것 1 — amazon 을 C-16 으로 푼다고 했다

보고서 0절 첫 표의 핵심 결론이 **"C-16 `downgrade` → amazon `None` → −3, 푼다"** 인데 **거짓이다.** amazon 앞에는 관문이 둘 있고 C-16 은 그 뒤에 있다.

1. `coverage_comparable: unknown` → C-16 에 닿기 전에 `needs_judgment`
2. 그 관문을 넘겨도 `contracted_revenue` 가 `parse_failed` → `pending_data`

NTM 은 §9 에 "amazon 의 `unknown` 이 미공시인지 미확인인지 자료에 구분이 없다" 고 **스스로 적어 놓고** 결론에서는 C-16 대상으로 다뤘다. **자기가 찾은 단서를 자기 결론에 반영하지 않았다.**

### 틀린 것 2 — spacex `apply` 를 −5 로 계산했다

NTM 은 "G1 −4 → G2 FCF 음수 −2 → 누계 −5 → 하한" 이라고 썼다. **G1 실패 분기는 G2 를 다시 세지 않는다.** `calc_f9.py` 의 G1 실패 경로는 G2 를 건너뛰고 바로 G3·G4 진단으로 간다.

```
실제:  G1 -4 → G3 런웨이 3.08년 step 0 → diag -4 → G4 판단 대기
       apply → needs_judgment  (−5 아님)
```

### 틀린 것 3 — 얽힘 3 이 거꾸로다

"C-05=`apply` 면 spacex 가 G2 에서 하한에 닿아 C-16 이 무력화된다" 고 했는데 **반대다.** `diagnose_only` 면 G1 점수로 확정돼 C-16 이 안 걸리고, **`apply` 여야 C-16 이 spacex 에 닿는다.** 틀린 것 2 에서 파생된 오류다.

### 맞은 것 1 — 내 지시서 전제를 정정했다

**내가 틀렸다.** F9 점수가 `None` 인 기업은 3개가 아니라 **4개**다. amazon·alibaba·anthropic 에 **spacex-xai**(`needs_rule_decision`)가 빠져 있었다. 그리고 공교롭게 **이번 5건 중 유일하게 실제로 풀리는 기업**이 그 빠진 하나다. 지시서 전제를 그대로 받지 않고 실측해서 고친 것이 옳다.

### 맞은 것 2 — G1 입력 공백이 이 라운드의 최대 발견이다

전수 확인했다. **`operating_margin_ttm` 1/14 · `revenue_ttm` 0/14 · `operating_income_ttm` 0/14.**

손실률을 계산할 수도 유도할 수도 없다. **10개사가 G1 을 통과하는 근거는 수치가 아니라 검토 입력 `operating_result_reviewed=profit` 이고**, 엔진도 경고를 달고 있다("TTM 영업손익 수치 없이 검토된 부호로 통과").

**이것이 C-16 과 같은 성질의 문제다.** F9 는 규칙이 미결이라 막힌 것이 아니라 **입력이 없어서** 막혀 있다. 규칙 다섯을 다 정해도 자료가 그대로면 점수는 하나만 움직인다.

### 맞은 것 3 — C-06 다섯 공백 실측

전부 재현했다. 경계값 기업 0개 · `fcf_ttm == 0` 0개사 · `buffer_erosion` **14/14 `no`** · `bep_retreat=yes` **openai 1개사**. **다섯 중 지금 무언가를 바꾸는 것은 "밴드를 확정했는가" 하나뿐**이라는 정리가 맞다.

### 맞은 것 4 — R3 독해가 구현과 일치한다

NTM 이 타당성을 물은 "G3·G4 는 FCF 음수일 때만 도달한다" 는 **구현과 정확히 일치한다.** `fcf > 0` 이면 G2 에서 즉시 반환한다(안정 0 · 악화 −1 · 미확인 `needs_judgment`).

**다만 R3 은 결론을 가르지 않는다.** NTM 은 "다르게 읽으면 `coverage_comparable` 이 `unknown` 인 11개사가 C-16 영향권" 이라고 했는데, `unknown` 은 C-16 이전에 `needs_judgment` 로 멈추므로 어느 독해에서도 C-16 에 안 닿는다. 다르게 읽으면 그 11개사는 C-16 대상이 되는 게 아니라 **지금 `ok` 인 점수가 `needs_judgment` 로 후퇴한다.** R3 을 유지하는 것이 맞다.

## 두 보고서가 갈린 지점과 그 뜻

| | C-13 | NTM | 실행 결과 |
|---|---|---|---|
| C-16 이 움직이는 기업 | alibaba | amazon | **없음** |
| amazon 결측 유형 | `parse_failed` → 대상 아님 | 대상으로 다룸 | **C-13 이 맞다** |
| spacex `apply` | `needs_judgment` → −4/−5 | −5 즉시 | **C-13 이 맞다** |
| `None` 기업 수 | 3 (spacex 별도 취급) | **4** | **NTM 이 맞다** |
| G1 입력 공백 | 안 다룸 | **1/14 · 0/14 · 0/14** | **NTM 이 맞다** |

**둘이 반대로 틀렸기 때문에 2자 대조가 값을 했다.** 한쪽만 봤으면 alibaba 를 풀러 갔거나 amazon 을 −3 으로 확정했을 것이다. 다만 **둘 다 자기 시뮬레이터로 돌렸고 둘 다 출하 엔진과 어긋났다.** F6-SPEC-18 때 "두 쪽이 같은 전제를 쓰면 일치가 정답을 뜻하지 않는다" 를 배웠는데, 이번은 **서로 다른 전제를 써서 서로 다르게 틀린** 경우다. **독립 시뮬레이터는 규칙 해석을 검증하지만 구현과의 일치는 검증하지 않는다.** 다음 과제부터 "출하 엔진을 불러 같은 결론이 나오는지" 를 완료 조건에 넣는다.

## 그래서 결정할 것

**C-06 은 지금 정하는 것이 맞다.** 유일하게 기업을 푼다. `proposed_v15_boundaries` 로 spacex-xai 손실률 −14.9% 가 −4 구간에 확정된다.

**C-05 도 같이 정해야 한다.** C-06 만 정하면 spacex 는 `needs_rule_decision` 에서 `needs_judgment` 로 옮겨갈 뿐 안 풀린다. `diagnose_only` 여야 −4 로 완료된다.

**C-16 은 지금 정해도 효과가 없다.** 정하지 말자는 뜻이 아니라 **`coverage_comparable` 검토 입력을 채우기 전에는 어느 쪽을 골라도 같다**는 뜻이다. 입력을 채우고 나서 정하면 alibaba(−2/−3)와 spacex(`apply` 일 때 −4/−5)가 실제로 갈린다. **순서가 거꾸로 잡혀 있었다.**

**C-04 는 점수 영향 0 이다.** 다만 별표 J(신용등급의 점수 개입 금지)와 G3 의 충돌을 문서에서 해소하는 의미는 남는다. NTM 의 "점수 영향이 없다는 것이 결정이 불필요하다는 뜻은 아니다" 가 맞다.

**C-07 은 이미 반영돼 있다.** 문서 정리다.

## 후속

| 건 | 처리 |
|---|---|
| **C-06 · C-05** | **사용자 결정** — 이 둘만 spacex-xai 를 푼다 |
| **C-16** | **입력 확보 후로 미룬다** — 지금 정해도 0개사 |
| `coverage_comparable` 검토 입력 | 11개사 미확인. **F9 의 실제 병목** |
| `revenue_ttm` · `operating_income_ttm` | 0/14. **F6 수집이 이 둘을 채운다** — F9 G1 공백이 F6 작업으로 닫힌다 |
| amazon `contracted_revenue` | `parse_failed` 재수집 또는 "백로그가 미개시 리스를 명백히 상회" 정성 규칙 |
| C-13 보고 정정 | alibaba 해소에 `coverage_comparable` 도 필요하다는 점 추가 |
| NTM 보고 정정 | amazon 오귀속 · spacex `apply` 경로 · 얽힘 3 |
| 완료 조건 추가 | **규칙 영향 조사는 출하 엔진 호출 대조를 포함한다** |
