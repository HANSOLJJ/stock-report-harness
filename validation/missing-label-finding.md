# `not_disclosed` 가 네 가지 뜻으로 쓰이고 있다

- 발견일. 2026-09-11.
- 발견 경위. 사용자가 **"일단 그 데이터가 없는 게 맞아?"** 라고 물어 원자료를 열었다.
- 영향. **C-16 을 현재 상태로는 결정할 수 없다.**

## 발단

`spacex-xai` 가 C-05 `apply` 에서 G4 에 막힌다. 무엇이 있으면 풀리는지 확인하려고 관측을 열었다.

```json
{ "observation_id": "spacex-xai.offbalance_B.v15",
  "value": null,
  "status": "not_disclosed",
  "raw": "미확인" }
```

**`status` 는 "회사가 공시하지 않았다" 라고 말하고 `raw` 는 "우리가 확인하지 않았다" 라고 말한다.** 둘은 다른 사실이다.

그리고 **SPCX 는 NASDAQ 상장사다**(`listed: true`, `exchange: NASDAQ`). 미개시 리스·구매 약정은 정기보고서 주석 항목이므로 **찾으면 있을 수도 있다.** 없다고 확인된 적이 없다.

## 전수 확인 — 한 라벨에 네 뜻

`status` 가 `not_disclosed` 인 관측을 전부 뽑아 `raw` 와 대조했다.

| 뜻 | raw | 사례 |
|---|---|---|
| **미확인 — 우리가 안 봤다** | `"미확인"` | **spacex-xai·alibaba `offbalance_B`** |
| **미공시 — 회사가 안 낸다** | `"미공시"` | anthropic·openai `cash`·`fcf_ttm` (비상장) |
| **계산 대상 아님** | `"∞"` | `runway_years` 8개사 (FCF 양수) |
| **없음 / 미상** | `"없음"`·`"—"` | palantir `net_borrowing_ttm` · alibaba `contracted_revenue` |

`amazon.contracted_revenue` 만 `parse_failed` 로 **정직하게** 적혀 있다(`raw: "AWS 백로그(수백 $B급) — 숫자 미공시"`). C-13 이 F9-DECIDE-20 에서 잡아낸 그 항목이다.

**같은 상황(확인 안 됨)이 amazon 은 `parse_failed`, spacex·alibaba 는 `not_disclosed` 로 갈려 있다.** 라벨이 일관되지 않다.

## 왜 치명적인가

`calc_f9._g4()` 는 이렇게 판별한다.

```python
if any(st != "not_disclosed" for st in statuses):
    → pending_data  "수집 실패를 미공시 위험으로 둔갑시키지 않음"
else:
    → C-16 (hold / downgrade)
```

**설계 지침 6.4 의 마지막 문장을 코드가 구현하고 있는데, 입력 라벨이 그 구분을 담고 있지 않다.** `raw` 가 "미확인" 인 관측이 `not_disclosed` 라는 이유로 C-16 경로에 들어가면, **우리가 안 찾은 것이 그 기업의 미공시 위험으로 둔갑한다.** 지침이 금지한 바로 그 일이다.

`runway_years` 8건은 F9 계산이 읽지 않아(엔진이 현금÷소진으로 재계산) 점수에는 영향이 없다. 그래도 지침 6.2 의 "FCF 양수의 런웨이는 **계산 대상 아님**으로 표시" 와 다른 라벨이다.

## 결정 순서가 바뀐다

**C-16 을 정하기 전에 `offbalance_B` 를 실제로 찾아야 한다.**

| 조사 결과 | 귀결 |
|---|---|
| 숫자가 있다 | G4 가 커버리지로 계산된다. **C-16 이 필요 없어진다** |
| 확인했는데 정말 없다 | 그때 비로소 `not_disclosed` 가 맞고 **C-16 이 묻는 상황이 된다** |

지금 C-16 을 정하면 **찾아보지도 않고 감점하거나 봐주는 것**이 된다.

## 부수 발견 — v1.7 F9 하한이 어긋나 있다

```
v1.7  factors.F9.range        [-4, 0]
v1.7  policies.f9.floor        -5          ← 범위 밖
      g1_bands_proposed 셋째   -5          ← 범위 밖
      g1_bep_retreat_score     -5          ← 범위 밖
```

확정된 함정 재배분(F6 −7 · F7 −2 · F8 −5 · **F9 −4** = −18)과 충돌한다. **F6 에는 정책과 range 를 로드 시점에 맞추는 검사가 있는데 F9 에는 없어 아무도 안 잡는다.** `F6-SPEC-18` 에서 그 검사를 넣은 이유가 "조용히 틀리는 종류라 로드 시점 차단" 이었는데, 같은 결함이 F9 에 남아 있다.

## 후속

| 건 | 배정 |
|---|---|
| **`offbalance_B` 실제 조사** (SPCX·BABA) + amazon `contracted_revenue` 재파싱 | C-13 · NTM 병렬 독립 |
| **결측 라벨 분리** — 스키마·재분류·C-16 게이트 연결 | worker |
| **F9 정책↔range 정합 검사** | worker (F6 와 같은 형태) |
| C-16 | **조사 결과 후로 연기** |
| C-05 `apply` · C-06 재척도 | 사용자 확정 대기 |
