# PRIV-IMPL-31 — C-12·C-20 구현과 14/14 완주

작성일 2026-09-11. 담당 worker(HANSOLJJ/worker). 요청 `msg_73ec5d058e4c`.
선행 설계진행 `d57e70e` `validation/c12-c20-decision.md` (사용자 확정). 원본 `AI기업_채점규칙_v1.5.md`·`AI기업_채점표_v1.5.md`.
**2026-09-11 라운드2** — 검토 회신(`e291e21`) 보완 넷을 반영했다. **10~13절**이 새로 붙었다.

## 결론

**14/14 완주입니다. 미결 규칙 결정이 0건이 됐고 순위는 예상과 정확히 같습니다.**

| | 결과 |
|---|---|
| 완주 | **14/14개사** · `pending_rule_decisions` **없음** |
| 순위 | anthropic **5위 12점**(단독) · openai **13위 3점** · tsmc·spacex-xai **6위** · oracle **14위** — **예상과 일치** |
| C-12 | anthropic **F6 −3** · openai **F6 −4** |
| C-20 | anthropic **F9 −2**. 경로에 `판정 보류(통과 아님)` 가 남습니다 |
| 관측 | **19건** 등록 (`ps_ratio` 2 · `arr_prior` 2 · 결측 유형 10 · 영업손익 라벨 2 · 모순 기록 1 외) |
| 원본 대조 | **58건 · 불일치 0건.** v1.5 원본 sha256 이 `v1.5.json` 선언값과 일치 |
| **경고 1건** | **Series H 모순이 보정 임계 0.50 을 가로지릅니다.** 한 시나리오에서 anthropic F6 가 −4 가 됩니다 (5절) |
| 승인 실행 | **6종 해시 전부 불변** |
| 테스트 | 191 → **220건** · skip 0 (라운드2 +3) |
| 보완 넷 | 선언 정정 · 원천 정책 개정 · `source_violation` 동반 수정 · F8 근거란 교체 (10~13절) |

신규 네트워크 호출 없음. `v1.5`·승인 실행 파일 미변경. **승인은 하지 않았습니다.**

---

## 1. 값을 원본에서 다시 뽑았습니다

선행 조사 두 건(C-13 `03e1e57` · NTM `b0a2587`)이 준 값을 그대로 쓰지 않고 v1.5 원본 문장에서 다시 읽었습니다. `verify_private.py` 가 그 대조이고 **58건 중 불일치 0건**입니다.

먼저 **우리가 읽는 파일이 규칙이 선언한 그 파일인지**부터 확인했습니다.

```
규칙 원본 sha256 = 57beb84ad8c291f3…  ==  v1.5.json source.sha256   ✅
```

| 확인한 것 | 원문 |
|---|---|
| 비상장 구간표 | 609~616행 — `~20x` −2 · `20x대` −3 · `30x+` −4 · `100x+` −5, 0·−1 칸은 `—` ✅ |
| anthropic 배수 | `$965B ÷ ARR $65B(7월) = 14.8배` → `TTM으로 맞추면 약 30~39배(Q2 매출 $10.9B 역산)` ✅ |
| openai 배수 | `$852B ÷ ARR $40B = 21.3배 — TTM 보정 시 약 39배` ✅ |
| 자본효율 | anthropic `0.52`(65÷125) · openai `0.22`(40÷185) ✅ |
| ARR 직전값 | anthropic `$47B→$65B` · openai `$25B→$40B` ✅ |

숫자는 지시서와 전부 일치합니다.

---

## 2. C-12 — 비상장 F6

### 2.1 P2 분모는 `arr` 이 아닙니다

지시서가 짚어 주신 그 지점이 실제로 원문에 있습니다.

> 구간표 −2 칸 괄호: **ARR 배수 — TTM 보정 필수**
> 645~647행: **🔑 ARR은 TTM 매출보다 과대하다 — 반드시 보정한다** … 보정 없이 비교하면 비상장사가 부당하게 싸 보인다.

그래서 **`ps_ratio`(밸류 ÷ TTM 보정 매출)** 를 읽습니다. `arr` 을 분모로 쓰면 anthropic 이 14.8x 로 NVIDIA(17.9)보다 싸 보입니다 — 원문이 654행에서 직접 그렇게 경고합니다.

원본이 TTM 추정 배수를 직접 주므로 **그 값을 쓰되 어떻게 얻은 값인지**를 `basis` 에 남겼습니다 — `derivation`·`anchor`(Q2 매출 $10.9B 역산)·`why_not_arr`·`source_lines`.

### 2.2 `~30~39` 는 구간이라 값을 하나 고를 수 없습니다

낮은 끝 **30** 을 값으로 두고 `basis.estimate_range: [30, 39]` 를 함께 남겼습니다. 낮은 끝은 **기업에 가장 덜 불리한 쪽**이므로, 거기서도 `30x+`(−4)이면 판정이 견고하다는 뜻입니다.

그리고 계산기가 **양 끝이 같은 밴드에 드는지 확인합니다.**

```
anthropic  30.0 → 30x+   39.0 → 30x+   spans_bands=False   → 값을 쓴다
가상 사례   25.0 → 20x대  35.0 → 30x+   spans_bands=True    → pending_data, 값을 고르지 않는다
```

**범위가 밴드를 가르면 값을 고르지 않는다**는 것을 테스트로 고정했습니다.

### 2.3 보정 — 조건 둘이 **모두** 성립할 때만 한 칸

| | P2 배수 | P2 | P3 성장률 | P4 자본효율 | 보정 | **F6** |
|---|---|---|---|---|---|---|
| anthropic | 30~39 | −4 | **+38.30%** ✅ | **0.5200** ✅ | **+1** | **−3** |
| openai | 39 | −4 | **+60.00%** ✅ | 0.2162 ✗ | 0 | **−4** |

**조건 하나로 올리는 규칙이면 안 됩니다.** openai 의 성장률(+60.0%)이 anthropic(+38.3%)보다 **높습니다.** 어느 하나로 올리면 **성장률이 더 높고 자본효율이 나쁜 쪽이 보상받습니다.** 둘 다 요구해야 "빠르게 크면서 돈을 덜 태웠는가" 라는 한 문장이 됩니다. `require_all: true` 이고 이것을 테스트로 고정했습니다.

### 2.4 임계를 어디서 가져왔나 — 하나는 외부 기준, 하나는 새로 정했습니다

| 조건 | 임계 | 출처 |
|---|---|---|
| `arr_growth` | **0.30** | **상장 P3 의 최상단 밴드 경계를 그대로 재사용.** 통상 시장 기준에서 정했고 이 표본 둘에서 뽑지 않았습니다(`f6-band-decision.md`) |
| `capital_efficiency` | **0.50** | **이 선만 새로 정했습니다.** "조달한 돈의 절반 이상을 연매출 런레이트로 만들었다" 는 해석 가능한 값이고 표본 중간값이 아닙니다 |

두 임계 다 `threshold_source` 를 규칙 파일에 적었고, **비워 두면 스키마가 거부합니다.**

### 2.5 이 결정의 약점을 규칙 파일에 적었습니다

지시하신 대로입니다. `private_correction.weakness` 전문입니다.

> **이 보정의 결과가 v1.5 발표 점수 −3·−4 와 정확히 같다.** `f6-band-decision.md` 에서 상장 밴드를 정할 때 "경계를 정한 근거가 표본이면 그 점수는 표본 밖에서 의미가 없다" 고 적어 두었는데, **여기서는 답을 먼저 알고 보정 방향을 정했다.** 완화 요소는 둘이다 — P2 밴드는 v1.5 구간표라는 외부 기준을 그대로 쓰고 표본에서 뽑지 않았고, 상한 1칸 보정은 상장 P4 에서 이미 쓰는 장치라 새로 만든 것이 아니다. 그래도 보정이 어느 방향으로 갈지는 답을 보고 정한 셈이고 숨기지 않는다.

**이 문장이 비어 있으면 스키마가 규칙 파일 로드를 거부합니다.** 다음 사람이 이 보정을 볼 때 어디서 왔는지 모를 수 없게 만들었습니다. 기각된 안1 의 장점도 `rejected_alternative` 에 남겼습니다.

---

## 3. C-20 — G1 판정 보류 후 비상장 경로

```json
{"gate": "G1", "result": "undetermined",
 "reason": "비상장이라 TTM 영업손익이 구조적 미공시 — 판정 보류(통과 아님). 단일 분기 영업흑자를 통과 근거로 쓰지 않는다",
 "route": "G2 비상장 경로", "decision_id": "C-20"}
{"gate": "G2", "result": "not_disclosed", "score": -2, ...}
{"gate": "G3", "result": "skipped", "reason": "FCF 미공시라 소진율 없음"}
{"gate": "G4", "result": "incompatible", "dedupe": "anthropic.fcf_not_disclosed", ...}
```

**`pass` 가 아니라 `undetermined` 입니다.** "통과 아님" 을 사유 문장에 박아 두어 다음 사람이 경로만 보고 통과로 읽을 수 없게 했습니다. F9 = **−2**.

### 3.1 자료가 없다는 것만으로는 부족합니다

이 경로는 **`missing_type == not_disclosed_confirmed` 라벨이 관측에 있을 때만** 탑니다. 라벨이 없으면 예전처럼 `pending_data` 입니다. 상장사는 어떤 경우에도 이 경로를 타지 않고, 실행이 C-20 을 선택하지 않아도 타지 않습니다. 넷 다 테스트로 고정했습니다.

**우리가 안 찾은 것과 회사가 낼 의무가 없는 것을 가르는 장치**가 MISS-LABEL-23 에서 만든 그 라벨이고, 여기서 그것을 실제로 씁니다.

### 3.2 제 이전 과제의 미완이 여기서 막고 있었습니다

지시서가 짚으신 대로입니다. MISS-LABEL-23 에서 `_g2` 를 `missing_type` 으로 바꾸면서 **재분류는 제안으로만 내고 관측에 등록하지 않았습니다.** 그래서 `anthropic.fcf_ttm` 이 `결측유형 미분류` 로 떨어져 G1 을 넘겨도 G2 에서 멈췄습니다.

당시에는 "관측 등록과 교체는 별건" 이라는 지시가 있었고 그 판단 자체는 맞았지만, **등록을 언제 하는가를 과제로 남기지 않은 것**이 빠졌습니다. 이번에 anthropic·openai 의 `fcf_ttm`·`cash`·`net_cash`·`debt_ebitda` 8건과 `operating_margin_ttm` 2건을 등록했습니다. **값은 그대로 없고 라벨만 붙였습니다.**

---

## 4. 등록한 관측

| 지표 | anthropic | openai | 비고 |
|---|---|---|---|
| `ps_ratio` *(신설)* | 30.0 `[30, 39]` | 39.0 | P2 입력. **arr 아님** |
| `arr_prior` *(신설)* | 47B | 25B | P3 입력. `kind=run_rate` |
| `fcf_ttm`·`cash`·`net_cash`·`debt_ebitda` | 결측 유형 | 결측 유형 | 값 없음, 라벨만 |
| `operating_margin_ttm` *(신설)* | 결측 유형 | 결측 유형 | C-20 판정 근거 |
| `cumulative_raised` | 125B + 모순 기록 | — | 값 동일, 민감도 추가 |

`arr_prior` 의 시점 라벨은 **anthropic 이 null 입니다.** 원문이 "ARR이 $47B→$65B로 늘며" 라고만 적고 $47B 가 언제 기준인지 말하지 않습니다. **지어내지 않았습니다.** openai 는 "2~4월 정체 구간" 이 원문에 있습니다.

승계 관측은 지우지 않고 `[PRIV-IMPL-31 대체됨 → …]` 표시만 붙였습니다.

---

## 5. 모순 둘 — 그리고 하나는 판정을 가릅니다

### 5.1 anthropic Series H — **보정 임계를 가로지릅니다**

같은 문서 안에서 갈립니다.

| 위치 | 값 |
|---|---|
| `AI기업_채점표_v1.5.md` ⑨적자깊이 | "완충이 외부 조달뿐이다 … **Series H $30B**($965B 밸류)에 기댄다" |
| 같은 파일 비상장 ⑥ 표 | "$965B (2026/5 **Series H $65B**)" |

**값을 고르지 않았습니다.** 대신 이것이 어디까지 번지는지 계산했습니다 — `cumulative_raised` 가 P4 자본효율의 분모이기 때문입니다.

| 가정 | `cumulative_raised` | 자본효율 | 임계 0.50 | anthropic F6 |
|---|---|---|---|---|
| 원본 표기 그대로 | 125B | **0.5200** | 충족 | **−3** |
| 125B 가 Series H 를 65B 로 포함 → 30B 로 교체 | 90B | 0.7222 | 충족 | −3 |
| 125B 가 Series H 를 30B 로 포함 → 65B 로 교체 | 160B | **0.4063** | **미달** | **−4** |

> **구간 0.41~0.72 가 임계 0.50 을 가로지릅니다.** 세 시나리오 중 하나에서 보정이 사라지고 그때 anthropic F6 가 −3 이 아니라 **−4** 입니다. 총점은 12 에서 11 이 되어 tsmc·spacex-xai 와 공동 5위가 됩니다.

지시서는 "cumulative_raised 약 125B 에 대해 28% 영향이라 작지 않습니다" 라고만 하셨는데, **그 28% 가 밴드까지 넘어갑니다.** 판단이 필요한 자리로 올립니다.

제 의견은 **지금은 원본 표기(125B)를 그대로 두는 것**입니다. 원본이 자본효율 0.52 를 계산할 때 쓴 값이 125B 이고, 우리가 조정하면 원본 계산과 어긋나면서도 어느 쪽이 맞는지는 여전히 모릅니다. 다만 민감도를 관측 `basis` 와 테스트에 남겨 두었으니 Series H 가 확인되면 그 자리에서 바로 갈립니다.

한 가지 관찰을 덧붙이되 단정하지 않습니다 — **$65B 는 anthropic 의 ARR 값과 같습니다.** 표를 만들며 옮겨 적혔을 가능성이 있으나 그것도 추측이라 규칙·관측 어디에도 판정으로 적지 않았습니다.

### 5.2 openai `arr` 시점 — 값이 같아 영향이 없습니다

원문 안에서 "7월" 4회 · "8/20" 4회로 갈립니다. **금액 $40B 는 네 표기가 모두 같습니다.** P2·P3 에 영향이 없고, **영향이 없다는 사실까지** `basis.contradiction` 에 적었습니다.

---

## 6. 점수 영향

`compare_private.py` 가 세 열로 갈랐습니다 — A 승인 실행 · B C-12·C-20 이전 · C 새 실행.

### 6.1 B→C — **이번 과제의 몫**

| 기업 | 전 | 후 |
|---|---|---|
| anthropic F6 | `pending_data` | **−3** |
| anthropic F9 | `pending_data` | **−2** |
| openai F6 | `pending_data` | **−4** |

**정확히 셋입니다.** 다른 12개사는 한 칸도 움직이지 않습니다.

### 6.2 순위 — 예상과 대조

| | 승인 실행(v1.5) | 새 실행(v1.7) |
|---|---|---|
| 완주 | 9/14개사 | **14/14개사** |
| 미결 규칙 결정 | C-06·C-13 | **없음** |

| 순위 | 기업 | 과점 | 함정 | 조정 |
|---|---|---|---|---|
| 1 | Alphabet / Google · Amazon / AWS · Meta | 21·21·18 | −6·−6·−3 | **15** |
| 4 | Microsoft | 19 | −5 | 14 |
| **5** | **Anthropic** | 21 | −9 | **12** |
| 6 | SpaceX + xAI · TSMC | 18·18 | −7·−7 | 11 |
| 8 | NVIDIA · Apple | 16·15 | −8·−7 | 8 |
| 10 | Alibaba | 18 | −11 | 7 |
| 11 | Palantir | 13 | −7 | 6 |
| 12 | Tesla | 14 | −9 | 5 |
| **13** | **OpenAI** | 16 | −13 | **3** |
| 14 | Oracle | 14 | −13 | 1 |

| 예상 | 결과 |
|---|---|
| anthropic 총점 12 · 단독 5위 | ✅ **맞습니다** |
| openai 총점 3 · 13위 | ✅ **맞습니다** |
| tsmc·spacex-xai 6위로 밀림 | ✅ 맞습니다 (공동 6위) |
| oracle 14위 | ✅ 맞습니다 |
| 14/14 완주 | ✅ 맞습니다 |

**다섯 다 일치합니다.**

### 6.3 anthropic·openai 의 F6 는 숫자가 같고 근거가 바뀌었습니다

대조표에서 `−3c > −3` · `−4c > −4` 로 보입니다. `c` 는 승계(`carried_score`)입니다. **v1.5 발표 점수를 그대로 물려받던 것이 이제 관측에서 산출됩니다.** 숫자가 같다는 것이 2.5 의 약점이기도 합니다.

---

## 7. 반영 경로와 해시

**기존 실행 `ai-scorecard-2026-09-baseline` 의 파일은 하나도 고치지 않았습니다.**

| 대상 | 승인 baseline | 현재 baseline | 새 실행 |
|---|---|---|---|
| `rules` | `9231b3a05ba5c766…` | **동일** | `2cddd4948388fb4a…` (v1.7) |
| `observations` | `37435ae2989236f5…` | **동일** | `1a69763e1819e7b9…` |
| `judgments` | `685069767e0cf919…` | **동일** | `5dc79ac34c617267…` |
| `run` | `50b063a5a12e84a6…` | **동일** | `90b41988ef5282fc…` |
| `results` | `0942c342f010781e…` | **동일** | `d413fdbae633a762…` |
| `draft` | `574841bc7c26f225…` | **동일** | `24a31aad9feb9075…` |

`run.decisions` 는 **다섯**입니다 — C-05 `apply` · C-06 `proposed_v15_boundaries` · C-16 `downgrade` · C-12 `p2_with_capped_promotion` · C-20 `defer_to_private_g2`.

**승인은 하지 않았습니다.** 승인 전에 `reviews/ai-scorecard-2026-09-obsreg.md` 가 필요합니다(계약 검증이 요구). 검토 주체가 정해지면 `review-template` 로 생성하겠습니다.

---

## 8. 확인된 것과 미확인인 것

### 8.1 확인된 것

1. v1.5 원본 sha256 이 `v1.5.json` 선언값과 일치하고, 대조 **58건 불일치 0건**.
2. 비상장 구간표를 옮겨 적으며 바꾸지 않았다. 0·−1 칸이 없는 것은 **원본 표의 형태**다.
3. P2 분모가 `arr` 이 아니라 TTM 보정 매출이라는 근거가 원문에 명시돼 있다.
4. **openai 는 성장률이 더 높은데도 보정이 없다** — 조건 하나로 올리는 규칙이면 안 되는 이유가 표본에서 실제로 나타난다.
5. C-20 경로에 `판정 보류(통과 아님)` 가 남고 라벨 없이는 타지 않는다.
6. **14/14 완주 · 미결 규칙 결정 0건.** 순위 예상 다섯 항목 전부 일치.
7. 승인 대상 **6종 전부 보존**.

### 8.2 미확인 — 추측하지 않습니다

1. **Series H 가 $30B 인지 $65B 인지.** 같은 문서 안에서 갈리고 외부 확인이 범위 밖입니다. **이것이 anthropic F6 를 −3/−4 로 가릅니다**(5.1). 판단 요청 건입니다.
2. **anthropic `arr_prior` 의 시점.** 원문에 라벨이 없어 null 로 뒀습니다.
3. **`ps_ratio` 값 자체.** v1.5 가 준 추정 배수이고 `legacy_unverified` 입니다. 원자료에서 TTM 매출을 다시 뽑으면 확인됩니다.
4. **`arr` 은 ARR 이 아니라 런레이트입니다**(`kind=run_rate`). PRIV-ARR-17 에서 확인한 그대로이고 관측에 남아 있습니다.
5. **비상장 2사가 상장하면 룰이 바뀝니다.** v1.5 643행이 "상장 첫 분기부터 완전히 동일한 룰을 적용하고 비상장 구간표·정밀도 열위·자본효율 보조지표를 모두 폐기" 한다고 적습니다. anthropic 은 2026년 10월 IPO 예상입니다.

## 9. 재현 방법

```bash
python validation/priv-impl-31/verify_private.py       # 원본 대조 58건
python scripts/scorecard_cli.py init ai-scorecard-2026-09-obsreg --rule v1.7 ...
python validation/obs-reg-25/apply_registrations.py
python validation/f6-reg-28/apply_f6_inputs.py
python validation/priv-impl-31/apply_private_inputs.py
python scripts/scorecard_cli.py research  ai-scorecard-2026-09-obsreg
python scripts/scorecard_cli.py calculate ai-scorecard-2026-09-obsreg
python scripts/scorecard_cli.py draft     ai-scorecard-2026-09-obsreg
python validation/priv-impl-31/compare_private.py      # 3열 대조 · 순위 · 해시
python -m unittest discover -s tests                   # 217건
```

**네트워크를 쓰지 않습니다.**

| 파일 | 내용 |
|---|---|
| `verify_private.py` · `verify-output.txt` | 원본 대조 58건 |
| `apply_private_inputs.py` · `apply-output.txt` | 관측 19건 · 모순 기록 · C-12·C-20 결정 |
| `compare_private.py` · `compare-output.txt` | 3열 대조 · 산출 근거 · 순위 · 해시 |
| `scorecard/rules/v1.7.json` | `private_bands` · `private_correction` · `f9.g1_private_undisclosed_route` |
| `scripts/scorecard/calc_f6_params.py` | `compute_private` 재작성 |
| `scripts/scorecard/calc_f9.py` | `_private_undisclosed_operating` · G1 판정 보류 분기 |
| `scripts/scorecard/rules.py` · `schema.py` | 비상장 밴드 접근자 · 밴드·보정·천장 검증 |
| `tests/test_scorecard_private.py` | 신규 26건 |


---

# 라운드2 — 검토 보완 넷 (2026-09-11)

**점수 변동 0건. 순위 동일. 14/14 완주 유지.** 상태 변화가 딱 하나 있고 의도된 것이다(13.3).

원본 대조가 58 → **87건**으로 늘었고 불일치 0건이다.

## 10. ① `private_note`·`private_multiples` 를 지금 규칙과 맞췄습니다

지적하신 그대로였습니다. `private_note` 가 **"밴드는 미정이고 점수는 만들지 않는다"** 로 남아 있었는데 바로 옆 `private_bands` 가 점수를 만들고 있었습니다. **선언이 사실과 반대**였습니다.

고치되 **C-12 확정 전 서술이었다는 사실을 함께 남겼습니다.**

> 비상장 F6 는 **P2 가 점수를 내고 P3·P4 가 합쳐서 최대 한 칸 올린다**(C-12 확정, 2026-09-11, 사용자). … | C-12 확정 전(2026-09-11 이전) 서술은 '밴드는 미정이고 … 점수는 만들지 않는다' 였다. 확정 뒤에도 그 문장이 남아 있어 **선언이 사실과 반대**인 상태가 있었고 설계진행 검토에서 잡혔다. 오늘 `not_disclosed` 네 뜻과 `stale_asof` 미소비로 고친 것과 같은 종류다 — **선언은 코드가 하는 일과 같아야 하고, 다르면 다음 사람이 선언을 믿는다.**

`private_multiples` 도 넷으로 다시 적었습니다. 첫 항목이 `ps_ratio` 이고 **`arr` 이 아님을 명시**했으며, 버린 `post_money_valuation/arr` 은 **지우지 않고** "참고용. 점수에 쓰지 않는다" 로 남겼습니다.

## 11. ② 원천 정책 — 세 원천을 내렸습니다

`usage_scope` 를 단일값에서 **합집합**으로 바꿨습니다.

```json
"scopes": ["personal_internal_only", "corporate_internal_only"],
"evaluation_rule": "scopes 는 합집합이다. 어떤 원천이 적격이려면 그 라이선스가 scopes 의 모든
                    원소를 허용해야 한다. … 범위를 넓히는 것은 제약을 푸는 것이 아니라 조이는 것이다."
```

**그 결과 셋이 `allowed` 에서 내려갑니다.** 셋 다 라이선스가 법인 사용을 배제하는데, 합집합에 `corporate_internal_only` 가 남아 있어 **개인 사용을 더해도 배제가 철회되지 않습니다.**

| host | 배제 조항 | 재개 조건 |
|---|---|---|
| `www.alphavantage.co` | ToS 2.a.ii — 법인·법인 대리 사용은 commercial use | 개인 전용으로 좁히거나 상업 계약. **다만 전망 2개 분기라는 기술적 사유는 그대로 남습니다** |
| `financialmodelingprep.com` | §2.2.1 — "In no event may the Customer use this licence on behalf of a company" | 개인 전용으로 좁히거나 유료 등급 서면 조건 확인 |
| `finnhub.io` | "Personal plan can't be used by any business **even internally**" | **둘 다 필요** — 개인 전용으로 좁히고 **+ 파생 결과 공유 서면 승인** |

Finnhub 만 조건이 둘인 이유는 같은 절이 `"not redistribute or share access to data or **derived results** from the data … without written approval"` 로 **파생 결과의 공유까지** 제한하기 때문입니다. 우리 산출물이 파생 결과인 한 개인 범위로 좁히는 것만으로는 부족합니다. 그 사실을 `reopen_condition` 에 적었습니다.

**셋 다 실제로 쓰이지 않습니다** — F6·F9 는 SEC 만 씁니다. 그래서 점수 영향이 0입니다.

`not_adopted` 를 신설해 `denied` 와 갈랐습니다 — **`denied` 는 쓸 자격이 없는 것이고 `not_adopted` 는 자격은 있으나 안 쓰기로 한 것**입니다. `reopen_condition` 을 스키마 **필수**로 두어 "영구 배제" 와 "지금은 안 함" 이 섞이지 않게 했습니다.

**2026-09-10 의 "강등하지 마십시오" 와 판단이 바뀐 것**이라 그 사실을 `reason` 과 테스트 docstring 양쪽에 남겼습니다.

## 12. ③ `source_violation` 을 같이 고쳤습니다

지적하신 함정이 실재했습니다. 키만 바꾸고 코드를 안 고치면 `data.nasdaq.com` 이 **마지막 fallback** 으로 떨어집니다.

```
"data.nasdaq.com 는 원천 allowlist 에 없음 — 약관 확인 후 규칙에 등재하고 쓴다"
                                              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                                              우리가 막으려는 행동을 지시한다
```

`not_adopted` 를 **먼저** 읽게 하고 옛 블록은 지우지 않았습니다.

```
data.nasdaq.com 는 검토를 마치고 채택하지 않기로 결정된 원천 — 구독가 연 1,200 달러가
확인돼 사용자가 채택을 접었다 … (결정 2026-09-11, 사용자). 재조사 불필요.
재개 조건: 가격이 바뀌거나 사용자가 예산을 승인하면 …
```

| host | 판정 |
|---|---|
| `data.nasdaq.com` | **채택 안 함(비용)** · 재조사 불필요 |
| `finnhub.io`·`www.alphavantage.co`·`financialmodelingprep.com` | **채택 안 함(약관)** · 재개 조건 명시 |
| `api.nasdaq.com` | **생산 원천 영구 배제**(robots.txt 전면 Disallow) — 성격이 다르다 |
| `data.sec.gov` | 통과 |
| v1.6 으로 읽으면 | "미승인 후보 — 서면 확정 필요…" — **과거 규칙 파일이 안 깨진다** |

## 13. ④ anthropic F8 근거란을 1차 공시로 교체했습니다

### 13.1 무엇을 바꿨나

승계 근거란이 AWS 훈련 집중을 **증권사 2차 증언**으로 적고 있었는데, 실제로는 **Amazon 이 SEC Form 8-K 로 직접 공시한 사실**이었습니다. 네 건을 접수번호와 함께 등재했습니다.

| 접수번호 | 일자 | 핵심 |
|---|---|---|
| `0001018724-25-000002` | 2025-02-06 | Project Rainier — hundreds of thousands of Trainium2 |
| `0001018724-25-000121` | 2025-10-30 | nearly 500,000 Trainium2 |
| `0001018724-26-000002` | 2026-02-05 | **"which Anthropic is using to train its industry-leading AI model, Claude"** |
| `0001018724-26-000012` | 2026-04-29 | 최대 5GW Trainium — "train and power" |

**확인된 것과 확인되지 않은 것을 나눴습니다.**

- ✅ Project Rainier 의 실체·규모, Anthropic 이 그것으로 Claude 를 **훈련**한다는 Amazon 의 명시, 5GW 확보, AWS $100B/10년과 칩 성능 연계 의무.
- ❓ **Google 몫의 훈련/서빙 구분.** Alphabet 10-K·10-Q 본문에 `Anthropic` 이 **0건**입니다. 계약 존재·금액·기간·용도가 전부 회사 미공시입니다. AWS $100B+ 안의 훈련/서빙 금액 구분도 미공시입니다.

**점수는 −3 유지입니다.** 하향하지 않는 이유는 **Google 몫이 훈련이 아니라는 증거가 있는 것이 아니라 공시가 없을 뿐**이기 때문입니다. 미공시를 '아니다' 로 읽으면 우리가 못 찾은 것을 그 기업의 구조로 둔갑시킵니다 — MISS-LABEL-23 이 세운 원칙 그대로입니다.

**재판정 조건**을 근거란에 등재했습니다. 셋 중 하나라도 1차 자료로 확인되면 −4 를 재검토합니다 — (1) Alphabet 의 고객사별 분리 공시, (2) Anthropic 의 훈련 컴퓨트 구성 공시, (3) Google 몫이 **서빙 전용**임의 1차 확인.

`OpenAI 27%` 가 **Microsoft 의 OpenAI 지분율**이라는 것도 v1.5 원본 188·198·217·350행에서 확인해 근거란에 명시했습니다 — Anthropic 의 컴퓨트 배분이 아닙니다.

### 13.2 8-K 는 인용이고, 10-Q 한 줄은 직접 대조했습니다

8-K 네 건의 원문은 이 워크트리에 보존돼 있지 않아 **C-13 의 SEC 읽기를 인용**했고 그 사실을 적었습니다. 대신 보존된 AMZN 10-Q 에서 한 줄을 **직접 대조**했습니다.

> "In Q2 2026, AWS and Anthropic announced an expansion of the strategic collaboration and existing multi-year commitment by more than $100.0 billion over 10.0 years, which includes contractual obligations related to the performance of AWS chips." ✅

**그 과정에서 하나를 더 찾았습니다.** 같은 10-Q 가 **Anthropic Series H 를 직접 언급**합니다 — Amazon 이 Q2 2026 에 `Anthropic Series H nonvoting preferred stock` 에 **$5.0B** 를 투자했고, 별도로 최대 $20.0B 금융 약정(이 투자로 $15.0B 로 감액)을 맺었다고 공시합니다.

**이것은 5.1 의 Series H 모순(30B/65B)을 해소하지 못합니다** — 라운드 **총액**을 말하지 않기 때문입니다. 다만 **Series H 의 존재와 시점(2026 Q2)이 1차 자료로 확정**되고, Amazon 참여분이 $5.0B 라는 하한이 생깁니다. 30B 와 65B 어느 쪽도 이 사실과 모순되지 않습니다. 그래서 판정은 그대로 두되 **1차 자료 앵커가 하나 생겼다**는 것을 적어 둡니다.

### 13.3 상태 변화 하나 — 의도된 것입니다

```
anthropic F8  (-3, carried_score) → (-3, ok)
```

**점수는 그대로이고 상태만 바뀝니다.** 근거란을 우리 1차 자료로 다시 쓴 이상 이 판단은 더는 v1.5 기준선에서 **승계된 것이 아닙니다.** `carried` 로 두면 `carried_from: baseline:v1.5` 가 거짓이 됩니다. `status: new` 로 바꾸고 `previous_judgment_id` 로 이전 판단을 가리킵니다.

두 상태 다 `COMPLETE_STATUSES` 라 **총점·순위는 동일**합니다.

## 14. 라운드2 결과 확인

| 확인 | 결과 |
|---|---|
| 14개사 factor 변동 | **1건** — anthropic F8 상태만(`carried_score`→`ok`), 점수 −3 동일 |
| 순위 | **완전 동일** |
| 완주 | 14/14 · 미결 규칙 결정 없음 |
| 원천 하향의 점수 영향 | **0** — F6·F9 는 SEC 만 씁니다 |
| 원본 대조 | 58 → **87건 · 불일치 0건** |
| 테스트 | 217 → **220건** · skip 0 |
| 승인 대상 6종 | **전부 보존** |

`results_hash` 는 `d413fdba…` → `45f5bd8c…` 로 바뀝니다 — F8 근거란과 판단 id·상태가 결과에 들어가기 때문입니다.

### 14.1 갱신된 파일

| 파일 | 내용 |
|---|---|
| `scorecard/rules/v1.7.json` | `private_note`·`private_multiples` 정정 · `usage_scope.scopes` · `not_adopted` 4건 |
| `scripts/scorecard/schema.py` | `normalize_usage_scopes()` · `not_adopted` 검증(`reopen_condition` 필수) |
| `scripts/scorecard/rules.py` | `source_violation()` 이 `not_adopted` 를 먼저 읽음 |
| `validation/priv-impl-31/apply_followups.py` · `followup-output.txt` | F8 근거란 교체 |
| `validation/priv-impl-31/verify_private.py` | `[8]`·`[8b]` 절 추가 — 보완 넷 검사 29건 |
| `tests/test_scorecard_f6_v17.py` | 원천 정책 테스트를 새 결정으로 갱신 + 3건 추가 |
