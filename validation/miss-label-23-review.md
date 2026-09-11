# MISS-LABEL-23 재검토 — 결측 라벨 분리 · F9 정합 검사

- 검토일. 2026-09-11.
- 대상. worker `727d81b`.
- 판정. **pass.** 세 과제 다 됐고 **요청보다 나은 것이 둘 있다.** 물으신 넷에 답한다.

## 재현

- `python -m unittest discover -s tests -q` **164건 통과** (147 → 164), skip 0.
- `2e5ba56..727d81b` 에서 `rules/v1.5.json`·`scorecard/runs`·`output` diff **공집합**. `v1.7` `status: draft` 유지.
- `v1.7` `policies.f9` 가 **결정문과 한 값도 다르지 않다.** `floor -4` · 밴드 `-2/-3/-4` · `bep_retreat -4` · `buffer_erosion_min -3` · `relief_cap -2`. 스텝 값(`g2_fcf_negative -2` · `relief_step 1` · `g4_coverage_keep 1.0`)은 그대로다.
- **재분류 25건을 내가 직접 관측에 얹어 엔진을 다시 돌렸다. 14개사 전 factor 변동 0건.** 점수 불변 주장이 맞다.
- **확정안 영향도 독립 재현했다.** `v1.7 policies.f9` + `C-05 apply` + `C-06` 으로 돌리니 `openai -5 → -4`, `spacex-xai needs_rule_decision → needs_judgment`, 나머지 12개사 불변이다. 결정문과 정확히 일치한다.

## 가장 잘한 것 — 미분류가 안전한 쪽으로 떨어진다

```python
if any(mt != MISSING_TYPE_FOR_DISCLOSURE_POLICY for mt in types):
    # 미분류(None)도 여기로 온다. 확인된 미공시라는 증거가 없으면 C-16 으로 보내지 않는다
```

**라벨이 안 붙은 관측은 C-16 에 들어가지 못한다.** 이것이 핵심이다. 기존 코드는 `status == "not_disclosed"` 하나로 갈랐기 때문에 **분류가 없으면 미공시로 취급**됐다. 지금은 반대다 — **증거가 없으면 감점 경로로 안 간다.**

`missing_type` 을 `value is None` 일 때만 붙도록 스키마에서 막은 것도 맞다. 값이 있는데 결측 유형이 달려 있으면 둘 중 하나가 거짓이다.

## 물으신 넷

### 1. `not_applicable` 과 `indeterminate` 분할 — 과하지 않다. 그대로 간다

가른 기준이 **"더 찾으면 값이 생기는가"** 인데 **내가 제시한 네 갈래보다 낫다.** 내 구분은 뜻으로 나눈 것이고 그쪽 구분은 **행동으로** 나눈 것이다.

```
not_applicable   개념상 없다        → 찾지 마라. 찾아도 없다
indeterminate    선행 입력이 없다    → 선행을 채우면 생긴다
unverified       확인 안 했다       → 찾아라
not_disclosed_confirmed            → 찾아도 없다. C-16 이 묻는다
```

**이 라벨이 존재하는 이유가 "조사에 힘을 쓸 것인가" 를 가르기 위해서**이므로, 행동으로 나눈 쪽이 옳다. `runway_years = ∞`(찾을 게 없다)와 `anthropic.runway_years = 판정 불가`(현금·FCF 를 채우면 생긴다)를 합치면 그 차이가 사라진다.

### 2. 보수 원칙 과적용 — 방향은 맞다. 다만 **기준을 둘 섞었다**

`raw` 가 `—`·`없음` 인 5건을 `unverified` 로 내린 것은 **맞다.** OFFB-24 가 방금 그 판단을 실측으로 지지했다 — `미확인` 셋을 실제로 찾아보니 **셋 다 공시돼 있었다.** 모호한 것을 미공시로 올리지 않은 것이 옳았다.

**그런데 anthropic·openai 에서 기준이 갈린다.**

| 지표 | 판정 | 근거 |
|---|---|---|
| `cash` · `fcf_ttm` | `not_disclosed_confirmed` | **구조** — 비상장이라 공시 의무가 없다 |
| `net_cash` · `debt_ebitda` | `unverified` | **문구** — `raw` 가 `—` 라 못 가른다 |

**같은 회사 같은 성질의 지표인데 한쪽은 구조로, 한쪽은 문구로 판정했다.** 둘 중 하나를 택해야 한다.

**구조 논거를 택하고 그것을 명문 기준으로 적어라.** `net_cash` 와 `debt_ebitda` 는 **감사 재무제표(대차대조표)에서만 나오는 값**이고 비상장사는 그것을 내지 않는다. `cash` 와 다르지 않다. `raw` 가 `—` 인 것은 **v1.5 표에서 칸을 비웠다는 뜻이지 판정이 아니다.**

기준을 이렇게 적어라.

> 공시 의무가 없는 기업(비상장)의 지표가 **감사 재무제표 항목이거나 그로부터만 도출되는 값**이면 `not_disclosed_confirmed` 로 둔다. 그 외에는 `raw` 문구를 따른다.

**이렇게 하면 판정이 사례별 직관이 아니라 규칙이 된다.** 점수에는 영향이 없다 — F9 는 `cash` 와 `fcf_ttm` 만 읽는다.

**반대로 `palantir.net_borrowing_ttm = "없음"` 은 `unverified` 가 맞다.** 상장사라 구조 논거가 없고 `없음` 이 "값이 0" 인지 "자료가 없음" 인지 문구로 안 갈린다.

### 3. 반영 경로 — 제안으로만 낸 판단이 옳다

**맞다. 다른 경로를 의도하지 않았다.** `observations.json` 은 승인 해시 대상이고 거기 쓰면 `approval` 이 깨진다. `run.decisions` 도 같다. **반영은 새 실행을 만들고 승인을 거치는 사용자 결정이다.**

**그리고 지금은 반영해서도 안 된다.** OFFB-24 결과로 세 관측에 **값이 생기기** 때문이다. 결측 유형을 붙일 대상 자체가 사라진다. 반영은 관측 등록과 한 번에 간다.

### 4. `_g2` 같은 패턴 — **worker 가 고친다. 지금 고쳐라**

```python
if not company["listed"] and fcf_obs is not None and fcf_obs["status"] == "not_disclosed":
```

**절반만 고친 상태가 가장 나쁘다.** 다음 사람이 `_g4` 에서는 `missing_type` 을, `_g2` 에서는 `status` 를 읽는 코드를 보게 된다. 같은 판별을 두 방식으로 하는 파일이 된다.

**점수는 안 바뀐다.** anthropic·openai 의 `fcf_ttm` 은 `raw = "미공시"` 라 `not_disclosed_confirmed` 이고, `_g2` 가 같은 분기로 들어가 `-2` 를 그대로 준다. **바뀌지 않는 것을 확인하는 것까지가 과제다.**

F9-DECIDE-20 담당과 겹친다는 우려는 없다. 그쪽 과제는 규칙 결정이었고 이건 라벨 소비다. **보고만 하고 남긴 판단은 과했으나 물어본 것은 옳다.**

## 자기 보고 수용 — 다만 나도 놓쳤다

> F9 정합 검사가 잡은 `v1.7` 의 세 값은 제 결함입니다. `F6-SPEC-18` 에서 `factors.F9.range` 를 `[-4,0]` 으로 바꾸면서 `policies.f9` 를 v1.6 에서 그대로 복사해 뒀습니다.

**정확한 자기 평가다. 그리고 그 커밋을 `pass` 로 판정한 것은 나다.** `f6-spec-18-review.md` 에 "함정 range 가 F6 −7 · F7 −2 · F8 −5 · F9 −4 로 확정대로다" 라고 적었다. **`range` 는 봤고 `policies` 는 안 봤다.** 같은 파일 안에서 선언이 둘로 갈려 있는데 한쪽만 확인했다.

**F6 에는 검사가 있고 F9 에는 없었다는 것이 핵심이다.** 그 검사를 넣자고 한 이유가 `F6-SPEC-18` 에서 "조용히 틀리는 종류라 로드 시점 차단" 이었는데, **그 판단을 F6 에만 적용하고 같은 구조의 F9 에 안 옮겼다.** 한 곳에서 세운 안전장치는 같은 모양의 다른 곳에도 옮겨야 한다.

## C-16 진입 2 → 0 을 읽는 법

**숫자 자체는 맞지만 뜻을 좁혀 적어야 한다.** `coverage_comparable` 이 11개사 `unknown` 이라 **이 변경 이전에도 C-16 에 실제로 도달하는 기업은 0개사였다.** 그쪽이 센 "2개사" 는 **`coverage_comparable = yes` 가 채워졌다고 가정했을 때** 들어갈 기업 수다. 게이트 하나를 따로 재는 올바른 방법이지만, 보고서에 그 가정을 적어야 "지금 2개사가 빠졌다" 로 읽히지 않는다.

**OFFB-24 이후의 최종 모습은 이렇다.**

```
SPCX   offbalance_B·contracted_revenue → 값 있음      결측 유형 해당 없음
AMZN   contracted_revenue              → 값 있음      결측 유형 해당 없음
BABA   contracted_revenue              → not_disclosed_confirmed   ← C-16 유일 대상
BABA   offbalance_B                    → 값 있음(미개시 리스는 별도)
```

**C-16 이 물어야 할 기업은 BABA 하나다.** 라벨 분리가 한 일이 정확히 이것이다.

## 후속

| 건 | 처리 |
|---|---|
| **`_g2` 를 `missing_type` 으로 옮김** | **worker, 지금.** 점수 불변 확인 포함 |
| 비상장 구조 기준 명문화 | worker — `net_cash`·`debt_ebitda` 도 `not_disclosed_confirmed` |
| C-16 진입 2→0 서술 | 가정을 명시 |
| **관측 6건 등록·교체 + 결측 유형 반영** | 별건. 새 실행·승인 경로 |
| `coverage_comparable` 판정 | `offb-24-review.md` 표의 단서를 근거란에 |
