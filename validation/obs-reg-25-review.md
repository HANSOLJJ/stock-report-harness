# OBS-REG-25 재검토 — 관측 등록과 새 실행

- 검토일. 2026-09-11.
- 대상. worker `e3b79c7`.
- 판정. **`pass`.** 범위를 정확히 지켰고 **승인을 막는 문제를 숨기지 않고 드러냈다.** 내가 지시서에서 틀린 것 둘을 잡아 줬다.

## 재현

- `python -m unittest discover -s tests -q` **165건 통과**.
- `df17a08..e3b79c7` 에서 `rules/v1.5.json`·`runs/ai-scorecard-2026-09-baseline`·`output` diff **공집합**. 승인 실행이 손대지 않은 채로 있다.
- 새 실행 `ai-scorecard-2026-09-obsreg` 가 별도 디렉터리로 생겼다.
- **지시값 34건 대조 불일치 0건.**

---

## 가장 중요한 것 — 승인하면 순위가 사라진다

새 실행을 직접 돌려 확인했다.

```
ai-scorecard-2026-09-obsreg   (rule v1.7)
  F6 status  pending_data 12 · needs_rule_decision 2
  rank       14개사 전부 None
```

**`v1.7` 의 F6 파라미터 모드가 요구하는 관측 셋이 어느 실행에도 등록된 적이 없다.**

```
revenue_ttm            있으나 basis.period_basis 선언 없음 (승계 관측)
net_income_ttm         관측 없음 (v1.7 신설)
revenue_ttm_prior      관측 없음 (v1.7 신설)
```

**관측 등록 때문이 아니다.** 같은 관측으로 `v1.5` 를 돌리면 11개사가 완주한다. **규칙을 바꿨는데 그 규칙이 먹을 입력을 등록하지 않은 것**이고, **그 순서를 어긴 것은 나다.** 지시서에 `rule_version` 을 `v1.7` 로 두라고 적으면서 F6 입력이 비어 있다는 것을 안 봤다.

`F6-SPEC-18` 검토에서 내가 이렇게 적었다.

> **`_derived` 에만 두고 `observations.json` 에 넣지 않은 판단이 옳다.** 관측 등록은 승인 절차를 거친다. `v1.7` 이 `draft` 인 상태에서 등록하면 승인 없이 생산 입력이 생긴다.

**그 판단 자체는 맞았다. 다만 "그러면 언제 등록하는가" 를 과제로 남기지 않았다.** `F6-FIX-21` 에서 세운 규칙 — 소비자가 없는 선언은 `pending` 표식과 **그 값을 읽을 코드가 생기는 과제를 명시** — 의 거울상이다. **이번은 소비자(v1.7 F6)가 먼저 생겼고 공급(관측)이 안 왔다.**

### 선택 — **1번. F6 입력 등록 과제를 하나 더 배정한다**

worker 의견과 같다.

**2번(새 실행을 `v1.5` 로)은 안 된다.** `v1.5` 의 F6 는 NTM PER 이고 그것이 산출 불가라서 **사용자가 F6 를 4개 파라미터로 재정의했다.** `v1.5` 로 두면 그 결정 전체가 반영되지 않는다. 순위 11개사는 **옛 정의로 매긴 순위**다.

**3번(F6 미완료인 채 승인)은 논외다.**

**필요한 값은 이미 있다.** `f6-spec-18/collect_ttm.py` 가 보존된 `companyfacts` 로 12개사 TTM 을 재구성했고 `score_check.py` 가 실제 `compute_f6` 로 9/9 일치를 확인했다. **신규 수집이 없다.**

---

## 내가 틀린 것 둘

### 1. BABA 간편법은 Note 2(t) 가 아니라 **2(g)** 다

원문에서 확인했다.

```
(g) Revenue recognition  →  Practical expedients and exemptions  가 이 아래에 있다
(t) Equity securities and other investments   ← 무관
```

C-13 이 `Note 2(t)` 라고 적었고 **내가 `offb-24-review.md` 에 그대로 옮겨 적었다.** 문언은 F-21 에서 직접 확인했는데 **인용 위치는 확인하지 않았다.**

**오늘 두 번째다.** `G1-TTM-26` 에서도 C-13 의 `1,134억 위안` 을 값 확인 없이 통과시켰다. **패턴이 잡힌다 — 나는 값과 문언은 원자료로 대조하는데 출처 표기(연도 칸·주석 번호)는 대조하지 않는다.** 출처 표기가 틀리면 다음 사람이 그 자리를 열었을 때 아무것도 못 찾는다.

**앞으로 인용 위치도 대조 대상에 넣는다.**

### 2. AMZN `Other commitments` 각주(3)은 원문에 있다

내가 "각주 3의 내용을 확인하지 못했으므로 넣지 마십시오" 라고 적었는데 **확인 가능한 자료였다.** 읽었다.

> (3) Includes **asset retirement obligations**, the estimated timing and amounts of payments for **rent and tenant improvements associated with build-to-suit lease arrangements that are under construction**, and liabilities associated with **digital media content agreements with initial terms greater than one year**.

**결론은 그대로 제외이나 이유가 바뀐다.**

- **자산제거의무(ARO)는 이미 인식된 부채**다. 미개시 확정 약정이 아니고, G4 분모에 넣으면 재무제표에 이미 선 것을 다시 센다.
- **build-to-suit 임차료는 `Leases not yet commenced`(137,214) 와 겹칠 수 있다.**
- **디지털 콘텐츠 약정은 각주(2)의 `license digital media content` 와 겹칠 수 있다.**

설계 지침 6.4 가 **"B종과 리스 총액·구매 약정이 겹치지 않도록 계약 식별자를 남긴다"** 고 한다. **이 항목은 성격이 섞여 있고 공시가 분해를 주지 않는다.** 제외한다.

**영향을 계산해 뒀다.** 포함하면 분모가 `267,279 → 285,645` 이고 커버리지가 `1.856 → 1.736` 이다. **1 이상이라 판정은 안 갈린다.** 근거란에 이 수치를 남겨라.

---

## 찾아낸 결함 — `as_of` 가 기준일이 아니다

**중요하고, 이 프로젝트가 방금 세 라운드 동안 고친 것과 같은 종류다.**

`ObsLookup` 이 같은 지표의 관측이 여럿일 때 `(status 등급, as_of)` 로 최신을 고른다. **값이 있는 관측은 등급으로 승계를 이기지만, 값이 없는 교체 관측은 등급이 0 이라 `as_of` 로만 이긴다.** 그래서 `alibaba.contracted_revenue` 의 새 `missing_type` 이 `_g4` 에 닿지 못하고 `결측유형 미분류` 로 떨어졌다.

**`missing_type` 이 도입되면서 새로 생긴 함정**이라는 진단이 정확하다. **라벨만 바꾸는 교체**가 앞으로 계속 생긴다.

### 임시 해법은 받되 구조 문제로 남긴다

worker 가 `as_of` 를 **원문을 연 날**(2026-09-11)로 두고 공시 기준일을 `basis.measured_as_of` 에 넣었다. **동작은 한다. 자료도 안 사라진다.**

**그러나 이것은 `as_of` 한 필드가 두 뜻을 갖게 만든다** — 승계 관측에서는 기준선 날짜, 새 관측에서는 접근일. **`not_disclosed` 가 네 뜻을 갖던 것과 같은 형태다.** 그때 배운 것을 여기 그대로 적용해야 한다.

**구조 해법은 최신성 키를 `as_of` 에서 떼는 것이다.** `recorded_at` 이든 `supersedes` 든 이름은 worker 가 정한다. **다음 과제로 넘긴다.**

**이번 임시 해법에는 테스트를 건다** — 값 없는 교체 관측이 승계를 이기는지를 고정하라. 안 걸면 다음 사람이 `as_of` 를 "고쳐" 놓고 조용히 깨뜨린다.

---

## 잘한 것 셋

**1. SPCX 기준일 혼합을 지시한 형태보다 낫게 남겼다.**

```json
"mixed_as_of": true,
"as_of_span": {"earliest": "2025-12-31", "latest": "2026-06-30", "stale_component_share": 0.055}
```

**"합계만 남고 섞였다는 사실이 사라지는 형태는 안 된다" 고만 했는데 `stale_component_share` 까지 계산해 뒀다.** 엔진은 합계를 읽고 감사하는 쪽은 구성요소를 본다.

**2. BABA 통화를 외부 환율 없이 처리했다.** 스키마가 `unit` 을 `USD` 로 강제해 RMB 를 둘 자리가 없는데, **20-F 가 스스로 선언한 환율(RMB6.8980, 연준 H.10)** 로 환산하고 원 통화를 `basis` 에 남겼다. **환율 출처 문제를 새로 만들지 않았다** — 발행사가 그 문서에서 선언한 값이다.

**3. 예상이 맞았는데 원인을 바로잡았다.**

> 예상 셋 다 일치. 단 앞의 둘은 **원인이 C-06 재척도이지 관측이 아닙니다.**

`openai -5 → -4` 와 `spacex-xai` 해소는 밴드 재척도의 결과다. **맞은 예측을 자기 공으로 돌리지 않고 원인을 분리한 것이 정확하다.**

## F9 는 크게 풀렸다

```
              baseline                →  obsreg (v1.7)
alibaba       pending_data            →  needs_rule_decision (C-16)
spacex-xai    needs_rule_decision     →  ok  -3
amazon        needs_judgment          →  ok  -2
openai        ok -5                   →  ok  -4
anthropic     pending_data            →  pending_data
```

**F9 미완료가 4개사에서 1개사로 줄었다.** alibaba 는 `needs_rule_decision` 인데 그것이 **C-16** 이고, 오늘 조사가 좁혀 준 바로 그 자리다. anthropic 만 비상장 규칙(C-20)으로 남는다.

## 후속

| 건 | 처리 |
|---|---|
| **F6 입력 등록** | **worker 다음 과제.** `collect_ttm.py` 출력으로 12개사. 신규 수집 없음 |
| **`as_of` 최신성 키 분리** | worker — 구조 해법. 이번 임시 해법에는 테스트 고정 |
| **규약 2 재작성 세대 조건** | worker — `v1.7 ttm_window`. MSFT FY2016 을 `why` 에 |
| AMZN 18,366 | **제외 확정.** 사유와 `1.736` 을 근거란에 |
| BABA 주석 번호 | `2(t)` → **`2(g)`**. 내 `offb-24-review.md` 도 정정 |
| SPCX TTM | C-13 보완분이 오면 관측 교체 |
| **C-16** | **alibaba 단독. 결정 가능** |
| 비상장 F6 밴드(C-12) | anthropic·openai — 미정 |
