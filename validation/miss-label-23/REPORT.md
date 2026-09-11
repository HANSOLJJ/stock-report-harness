# MISS-LABEL-23 — 결측 라벨 분리와 F9 정합 검사

작성일 2026-09-11. 담당 worker(HANSOLJJ/worker). 요청 `msg_e7165378d135`. 근거 설계진행 `583af3f` `validation/missing-label-finding.md`.
**2026-09-11 보완 반영** — 검토 회신(`f9678ad` `validation/miss-label-23-review.md`) 보완 3건을 적용했다. 5 절·2.1.1·3 절이 바뀌었다.

## 결론

**세 과제 전부 완료했다. 핵심은 '우리가 안 찾은 것' 이 더는 C-16 에 닿지 않는 것이다.**

| | 결과 |
|---|---|
| 결측 유형 스키마 | **4종** — `unverified` · `not_disclosed_confirmed` · `not_applicable` · `indeterminate` |
| 재분류 | 25건. 한 라벨이 **4갈래**로 갈렸다 |
| **C-16 진입 대상** | **2개사 → 0개사.** 단 이 둘은 `coverage_comparable = yes` **가정하의 수**이고, 실제 도달 기업은 **변경 전에도 0개사**였다(3 절) |
| 라벨 소비 | `_g4` 와 **`_g2` 둘 다** `missing_type` 을 읽는다(5 절) |
| F9 정합 검사 | **v1.7 을 잡았다.** C-05·C-06 확정으로 재척도해 **해소** |
| 점수 | **14개사 전 factor 불변** · 승인 실행 재계산 **변동 0건** |
| 테스트 | 147 → **165건** · skip 0 (C-06 확정으로 F6 회귀 복귀) |

승인 대상 6종 전부 불변이다. 신규 네트워크 수집 없음. `offbalance_B` 실제 조사는 C-13·NTM 담당이라 라벨만 다뤘다.

## 1. 결측 유형 스키마

`status` 하나가 네 뜻을 담고 있었다. **값이 없는 이유를 라벨이 직접 말하게 한다.**

| `missing_type` | 뜻 | C-16 | 판단 기준 |
|---|---|---|---|
| `unverified` | **우리가 확인하지 않았다.** 찾으면 있을 수 있다 | ✗ | 애매하면 전부 여기 |
| `not_disclosed_confirmed` | **확인된 미공시.** 회사가 내지 않는다 | **○ 여기에만** | 구조적으로 확정될 때만 |
| `not_applicable` | 산식 적용 대상이 아니다. **개념상 정의되지 않는다** | ✗ | FCF 양수의 런웨이, 적자의 PER |
| `indeterminate` | 산출 대상이나 **선행 입력이 결측**이라 만들 수 없다 | ✗ | 비상장 런웨이 |

네 종으로 나눈 이유는 **뒤 둘이 서로 다르기 때문**이다. `not_applicable` 은 아무리 찾아도 값이 생기지 않는다(개념상 없다). `indeterminate` 는 선행 입력이 생기면 값이 생긴다. 둘을 합치면 "더 찾을 가치가 있는가" 를 못 가린다.

### 1.1 스키마 제약

- `missing_type` 은 **optional** 이다. 기존 관측에 없어도 로드된다 — 과거 실행이 계속 열려야 한다.
- **값이 있는데 `missing_type` 이 붙으면 거부**한다. 모순이다.
- 알 수 없는 값은 거부한다.

## 2. 재분류 25건

`reclassify.py` 가 낸 결과다. 전수는 `reclassify-output.txt` `[1]` 절, 제안은 `_derived/reclassification.json` 이다.

| 전 (status) | 후 (missing_type) |
|---|---|
| `not_disclosed` 24 · `parse_failed` 1 | `not_applicable` **10** · `not_disclosed_confirmed` **8** · `unverified` **5** · `indeterminate` **2** |

보완 전에는 `unverified` 9 · `not_disclosed_confirmed` 4 였다. 2.1.1 의 구조 기준을 명문화하면서 비상장 2사의 `net_cash`·`debt_ebitda` 4건이 올라갔다.

### 2.1 보수 원칙을 어떻게 적용했나

**`raw` 가 '미확인' 인 것을 '미공시' 로 승격하지 않았다.** 그리고 그보다 더 넓게 잡았다 — **뜻이 모호한 것도 전부 `unverified`** 로 뒀다.

| `raw` | 판정 | 사유 |
|---|---|---|
| `미확인` | `unverified` | 승격 금지 대상. alibaba·spacex-xai `offbalance_B` |
| `∞` | `not_applicable` | FCF 양수라 런웨이가 개념상 정의되지 않는다(설계 지침 6.2) |
| `적자` | `not_applicable` | 적자라 PER·영업외 비중이 정의되지 않는다 |
| `판정 불가` | `indeterminate` | 선행 입력(현금·FCF)이 결측 |
| **비상장 + 감사 재무제표 항목** | `not_disclosed_confirmed` | 공시 의무가 없다 — **구조적으로 확정**(2.1.1) |
| `—` · `없음` (그 외) | **`unverified`** | 미공시인지 미확인인지 **갈리지 않는다** |
| `parse_failed` | `unverified` | **파싱 실패는 확인이 아니다** |

**판정 순서가 중요하다.** ① 개념상 값이 없는 것(`∞`·`적자`·`판정 불가`)을 먼저 걷어내고 ② 구조 기준을 적용하고 ③ 남은 것은 `raw` 문구를 따른다. ①을 먼저 두는 이유는 2.1.1 마지막 문단에 적었다.

**틀리는 방향의 비용이 다르다.**

- `unverified` 로 잘못 두면 → 안 찾아도 될 것을 더 찾는다. **점수는 틀리지 않는다.**
- 미공시로 잘못 올리면 → **우리가 안 찾은 것이 그 기업의 위험으로 둔갑한다.**

그래서 뜻이 모호한 것은 전부 `unverified` 로 내렸다. 다만 **비상장 2사의 `net_cash`·`debt_ebitda` 는 예외**다 — 근거가 우리의 탐색량이 아니라 구조이기 때문이고, 그 논거를 2.1.1 에 규칙으로 적었다.

### 2.1.1 구조 기준 — 비상장에는 논거가 다르다 *(보완 반영)*

최초 보고에서는 `raw` 가 `—` 인 비상장 항목을 `unverified` 로 뒀다. **일관되지 않았다.** 같은 회사의 `cash`·`fcf_ttm` 은 `not_disclosed_confirmed` 였고 `net_cash`·`debt_ebitda` 는 `unverified` 였는데, 둘의 차이는 지표의 성격이 아니라 **`raw` 를 적은 사람이 `미공시` 라고 썼느냐 `—` 라고 썼느냐** 뿐이었다. 검토 회신의 지적대로 이는 기준이 아니라 표기 편차다.

확정 기준을 그대로 옮긴다.

> **공시 의무가 없는 기업의 지표가 감사 재무제표 항목이거나 그로부터만 도출되는 값이면 `not_disclosed_confirmed` 로 두고, 그 외에는 `raw` 문구를 따른다.**

**이것은 승격 금지 원칙과 충돌하지 않는다.** 승격 금지가 막는 것은 *우리가 안 찾은 것*을 위험으로 바꾸는 일이다. 여기서의 근거는 탐색량이 아니라 **구조**다 — 감사 재무제표를 제출할 의무가 없는 기업의 재무제표 항목은 **정의상 공개된 적이 없다.** '안 찾아서' 가 아니라 '있을 수 없어서' 없다.

`reclassify.py` 의 `AUDITED_STATEMENT_METRICS` 가 그 집합이다.

| 구분 | 지표 |
|---|---|
| 재무제표 본문 | `revenue_ttm` · `revenue_ttm_prior` · `operating_income_ttm` · `net_income_ttm` · `ocf_ttm` · `capex_ttm` · `cash` · `undrawn_credit` · `net_borrowing_ttm` |
| 본문에서만 도출 | `fcf_ttm` · `net_cash` · `debt_ebitda` · `operating_margin_ttm` · `nonop_share` · `runway_years` |
| 감사 재무제표 **주석** | `contracted_revenue`(ASC 606 잔여 수행의무) · `offbalance_B` |
| **제외** | `price` · `market_cap` · `ttm_per` · `ps_ratio` · `ntm_*` · `credit_rating` · `cds_5y_bp` · `post_money_valuation` · `arr` · `ttm_revenue_est` · `cumulative_raised` — 시장가·컨센서스·자금조달 발표가 섞여 **재무제표에서만 도출되지 않는다** |

**상장사에는 이 논거가 성립하지 않는다.** 정기보고서에 있을 수 있으므로 palantir `net_borrowing_ttm`(`raw` = `없음`)은 그대로 `unverified` 다. 같은 `없음` 이라도 비상장이면 구조로 확정되고 상장사면 확인 대상이다 — **이것이 표기 편차가 아니라 기준이다.**

**개념 분기가 구조 기준보다 먼저다.** `runway_years` 는 위 집합에 들어 있지만 비상장 2사의 값은 `indeterminate` 로 남는다. 구조 기준은 *미공시냐 미확인이냐* 를 가르는 규칙이지 *정의되지 않음*·*산출 불가* 를 미공시로 바꾸는 규칙이 아니기 때문이다. 이것을 뒤집으면 "선행 입력이 없어서 못 구했다" 가 "회사가 안 냈다" 로 둔갑한다.

### 2.2 amazon `contracted_revenue`

`raw` 가 `AWS 백로그(수백 $B급) — 숫자 미공시` 이고 `status` 는 `parse_failed` 다. 문면만 보면 "회사가 숫자를 안 낸다" 로 읽히지만 **확인된 바가 없어 `unverified` 로 뒀다.** 재파싱은 C-13 담당이라 건드리지 않았다.

### 2.3 세 관측은 잠정이다 (2026-09-11 지시)

`OFFB-24` 의 NTM 조사 결과가 **아직 미검증**이라 다음 셋을 **잠정**으로 표시했다. 설계진행 회신 전까지 확정하지 않는다.

| 회사 | metric | 잠정 분류 |
|---|---|---|
| spacex-xai | `offbalance_B` | `unverified` |
| alibaba | `offbalance_B` | `unverified` |
| amazon | `contracted_revenue` | `unverified` |

`_derived/reclassification.json` 의 각 항목에 `provisional: true` 와 사유를 넣었고 출력 `[3b]` 절에 따로 낸다. **조사에서 '확인했는데 없다' 가 나오면 `not_disclosed_confirmed` 로 올라가고, 그때 C-16 이 묻는 상황이 된다.** 지금 올리지 않는 이유는 2.1 의 보수 원칙 그대로다.

셋 다 현재 분류가 `unverified` 라 **C-16 진입은 어느 쪽으로든 0개사다**(3 절). 잠정이 확정으로 바뀌면 그때 다시 센다. 셋 중 둘(`offbalance_B`)은 2.1.1 의 집합에 들어 있지만 **세 회사 다 상장사**라 구조 기준이 닿지 않는다.

## 3. C-16 진입 대상 — 2개사 → 0개사 *(가정하의 수)*

**먼저 가정을 밝힌다. 아래 `2개사` 는 지금 실제로 C-16 에 닿는 기업 수가 아니다.**

> **가정: `coverage_comparable = yes`.** `_g4()` 는 이 검토 입력이 `yes` 가 아니면 **결측 유형을 보기도 전에** `undetermined` 로 빠져나간다. 아래 표는 그 관문을 통과했다고 놓았을 때의 수다.

이번 실행의 `coverage_comparable` 분포는 **`unknown` 11 · `no` 2 · `yes` 1** 이고, 유일한 `yes` 인 oracle 은 두 지표에 값이 다 있어 `computed` 로 끝난다. **따라서 이 변경 이전에도 C-16 에 실제로 도달하는 기업은 0개사였다.**

| 회사 | `coverage_comparable` | 가정하 전 | 가정하 후 | 근거 |
|---|---|---|---|---|
| **alibaba** | `unknown` | **진입** | **제외** | `offbalance_B`=미확인 · `contracted_revenue`=`—` |
| **spacex-xai** | `unknown` | **진입** | **제외** | `offbalance_B`=미확인 |
| amazon | `unknown` | 제외 | 제외 | `parse_failed` 라 원래 제외 |
| oracle | `yes` | — | — | 두 지표에 값이 있어 `computed`(커버리지 2.552) |
| **실제 도달** | | **0개사** | **0개사** | |

**그래서 `2 → 0` 은 '2개사가 빠졌다' 가 아니다.** *검토 입력이 채워졌을 때 들어갔을 2개사가 이제는 들어가지 않는다* 는 뜻이다. 그 둘 다 **'우리가 안 찾아서'** 들어가고 있었고, 설계 지침 6.4 가 금지하는 것이 정확히 그 일이다. `reclassify.py` `[3]` 절이 이 가정과 실제 도달 수를 같이 출력한다.

### 3.1 `_g4` 를 어떻게 고쳤나

`status == "not_disclosed"` 판별을 `missing_type == "not_disclosed_confirmed"` 로 바꿨다. 그리고 **미분류(`missing_type` 없음)도 C-16 에 보내지 않는다.**

> 확인된 미공시라는 **증거가 없으면** 보내지 않는다. 라벨이 없다는 것은 "모른다" 이지 "미공시" 가 아니다.

pending 사유에 `결측 유형이 분류되지 않아 확인된 미공시인지 판별 불가` 를 적어 **무엇을 해야 풀리는지**가 보이게 했다.

이 엄격화가 **지금 점수를 바꾸지 않는 이유**는 4.4 에 적었다.

## 4. F9 정책 ↔ range 정합 검사

F6 와 같은 형태로 **로드 시점**에 막는다. 점수를 만들어 내는 값만 검사하고 임계치(연 수·배수)는 제외한다.

### 4.1 검사가 잡은 것

```
v1.5  OK
v1.6  OK
v1.7  BLOCKED: rules.policies.f9: factors.F9.range [-4, 0] 를 벗어나는 점수 —
      floor=-5, g1_bep_retreat_score=-5, g1_bands_proposed[2].score=-5.
      밴드 재척도는 C-06 결정 사항이므로 임의로 고쳐 통과시키지 않는다
```

발견 문서가 예고한 **정확히 그 셋**이다.

**이것은 내 결함이다.** `F6-SPEC-18`(`0821c83`)에서 함정 재배분을 반영하며 `factors.F9.range` 를 `[-4,0]` 으로 바꿨는데 `policies.f9` 는 v1.6 에서 그대로 복사해 두었다. F6 에는 같은 검사를 넣어 놓고 F9 에는 안 넣어서 내 손으로 만든 불일치를 내가 못 잡았다.

### 4.2 그리고 C-05·C-06 확정으로 해소됐다 (2026-09-11, 진행 중 반영)

작업 중 **C-05 `apply`·C-06 재척도가 확정**됐다(설계진행 `19625ba`). "밴드를 고치지 말라" 던 제약이 해제돼 고칠 값이 정해졌고, **임의로 고친 것이 아니라 결정된 값을 반영했다.**

| 값 | v1.5 | **v1.7 확정** |
|---|---|---|
| `g1_bands_proposed` | −3 / −4 / −5 | **−2 / −3 / −4** |
| `floor` | −5 | **−4** |
| `g1_bep_retreat_score` | −5 | **−4** |
| `g1_buffer_erosion_min_score` | −4 | **−3** |
| `g1_direction_relief_cap` | −3 | **−2** |

**원칙은 "레벨은 올리고 스텝은 그대로" 다.** 점수 자리를 지정하는 값만 한 칸 올렸고, 몇 칸 내리는지를 지정하는 값(G2·G3·G4 감점폭, `relief_step`)은 건드리지 않았다. `rescale_note` 에 그 구분과 `buffer_erosion_min`·`relief_cap` 을 같이 올린 이유를 적었다.

**v1.7 이 다시 로드되고 F6 회귀 32건이 돌아왔다.** 테스트 164건, skip 0 이다. 차단을 고정하던 `TestV17BlockedByF9Range` 는 `TestV17F9Rescaled` 로 바꿔 **재척도가 유지되는지**를 고정한다 — 되돌리면 다시 걸리는 것까지 본다(`test_v17_would_be_blocked_if_rescale_reverted`).

**`v1.5` 는 재척도하지 않았다.** 승인 대상이다.

### 4.2.1 확정안의 점수 영향 — 독립 검산

결정문이 예측한 것(openai −5→−4, spacex-xai G4 대기)을 **실제 엔진으로 직접 돌려 확인했다**(`c05-c06-impact.txt`).

| 회사 | 현행 v1.5 | 확정 v1.7+결정 |
|---|---|---|
| **openai** | −5 / ok | **−4 / ok** |
| **spacex-xai** | None / `needs_rule_decision` | **None / `needs_judgment`** |
| 나머지 12개사 | | **불변** |

**예측과 정확히 일치한다.** spacex-xai 가 `needs_judgment` 인 것은 G4 가 `coverage_comparable` 검토 입력에서 멈추기 때문이고, 결정문의 "G4 대기" 와 같은 상태다.

이 영향은 **v1.7 을 쓰는 새 실행에서 나타난다.** 승인된 v1.5 실행의 점수는 그대로다(4.4).

### 4.3 v1.7 을 걸린 상태로 두려던 계획과 그 대가 *(해소됨 — 4.2 참조)*

**밴드를 고쳐 통과시키지 않았다.** 두 쪽 다 움직일 수 없다.

| 방향 | 왜 못 하나 |
|---|---|
| 밴드를 `[-4,0]` 에 맞춰 재척도 | **C-06 결정 사항**이고 사용자 확정 대기 중 |
| `factors.F9.range` 를 `[-5,0]` 으로 되돌림 | 함정 합이 −19 가 되어 **확정된 −18 보존이 깨진다** |

**아래는 C-05·C-06 확정 전의 상태다. 기록으로 남긴다.** 당시 대가는 v1.7 이 로드되지 않아 F6 회귀 32건이 skip 되는 것이었고, 숨기지 않고 두 가지로 드러냈다.

1. skip 사유에 차단 메시지 전문을 넣었다 — 테스트 출력에 이유가 보인다.
2. **`TestV17BlockedByF9Range` 로 "지금 막혀 있다" 를 회귀로 고정했다.** C-06 이 재척도하면 이 테스트가 실패하고 skip 도 자동으로 풀린다.

조용히 통과시키지도, 깨진 채 방치하지도 않는 형태다. **다만 C-06 이 정해질 때까지 F6 회귀 32건이 실제로 돌지 않는다는 점은 비용이다.** 검사를 로드 시점이 아니라 `validate.py` 쪽(`check_source_allowlist` 와 같은 자리)에 두면 v1.7 을 로드는 하되 검증에서 잡을 수 있다. **지시가 "F6 와 같은 형태" 였으므로 로드 시점으로 구현했고, 다른 배치를 원하면 옮기겠다.**

### 4.4 점수 불변 — 왜 안 바뀌나

`reclassify.py` `[4]` 절이 **실제 엔진(`compute_company`)** 으로 재분류 전후를 돌려 비교한다. 손으로 다시 계산하지 않는다.

```
14개사 전 factor 점수·상태 불변
```

이유는 **지금 `_g4` 의 C-16 분기에 도달하는 기업이 없기 때문**이다. 확인해 보니 G4 에 닿는 기업은 둘뿐이고 둘 다 그 분기 앞에서 멈춘다.

| 회사 | G4 결과 |
|---|---|
| oracle | `computed` — 커버리지 2.552 로 계산된다 |
| amazon | `coverage_comparable 미확인` 에서 멈춘다(판단 대기) |

alibaba·spacex-xai 는 **G4 이전 단계에서 이미 `pending_data`·`needs_rule_decision`** 이다. 그래서 C-16 진입 판별이 2→0 으로 바뀌어도 **현재 점수에는 나타나지 않는다**(3 절의 가정 참조).

`_g2` 마이그레이션(5 절)도 같은 이유로 점수를 바꾸지 않는다. 그 분기에 닿을 후보는 비상장 2사뿐인데 **둘 다 G2 이전에 멈춘다.**

| 회사 | G2 도달 여부 |
|---|---|
| anthropic | ✗ — G1 에서 `pending`(TTM 영업이익률 미확보, C-20) |
| openai | ✗ — G1 `fail` 로 `bep_retreat` −5 확정, G3/G4 건너뜀 |

승인 실행을 **실제 엔진으로 다시 계산해 `results.json` 과 대조**했고 **14개사 × 9 factor 변동 0건**이다.

**이것이 "지금은 안 중요하다" 는 뜻이 아니다.** C-05 `apply` 나 선행 게이트가 풀리는 순간 그 분기에 도달하고, 그때 라벨이 옳지 않으면 감점이 잘못 붙는다. **지금 고쳐야 그때 맞는다.**

## 5. `_g2` 도 `missing_type` 을 읽는다 *(보완 반영 — 완료)*

최초 보고에서는 이것을 **보고만 하고 고치지 않았다.** 과했다. 검토 회신의 판단이 맞다.

> 절반만 고친 상태가 가장 나쁩니다. 다음 사람이 `_g4` 에서는 `missing_type` 을, `_g2` 에서는 `status` 를 읽는 코드를 보게 됩니다.

내가 든 세 이유 중 둘은 성립하지 않았다. `F9-DECIDE-20` 과의 중복 우려는 **그쪽이 규칙 결정이고 이건 라벨 소비**라 겹치지 않는다. "점수가 바뀔 수 있다" 는 우려는 **확인하면 되는 것**이었고, 확인하는 것까지가 과제였다.

**전**

```python
if not company["listed"] and fcf_obs is not None and fcf_obs["status"] == "not_disclosed":
```

**후**

```python
if (not company["listed"] and fcf_obs is not None
        and fcf_obs.get("missing_type") == MISSING_TYPE_FOR_DISCLOSURE_POLICY):
```

`pending` 사유도 같이 옮겼다. 라벨이 없으면 `결측유형 미분류` 가 찍히고, 해소 힌트가 `status=not_disclosed 로 기록` 에서 `missing_type=not_disclosed_confirmed 로 기록` 으로 바뀐다 — **무엇을 해야 풀리는지가 새 계약을 가리킨다.**

### 5.1 점수가 바뀌지 않는 것을 확인했다

세 가지로 봤다.

1. **승인 실행 재계산** — `compute_company` 를 14개사에 돌려 `results.json` 과 대조. **변동 0건**(4.4).
2. **재분류 전후** — `reclassify.py` `[4]` 절. **14개사 전 factor 불변.**
3. **왜 안 바뀌나** — 이 분기의 후보인 비상장 2사가 **둘 다 G2 에 닿지 않는다**(4.4 표). 라벨이 붙든 안 붙든 지나가지 않는 길이다.

**"결과적으로 안 바뀐다" 와 "분기에 안 닿는다" 는 다르다.** 후자가 이유이고, 그래서 선행 게이트가 풀리는 순간 이 마이그레이션이 실제로 작동한다.

### 5.2 회귀로 고정했다

`tests/test_scorecard_calc.py::TestF9::test_g2_reads_missing_type_not_status` 가 셋을 본다.

| 입력 | 기대 |
|---|---|
| 비상장 · `status=not_disclosed` · **라벨 없음** | `pending_data` · 사유에 `결측유형 미분류` |
| 비상장 · `missing_type=unverified` | `pending_data` |
| **상장사** · `missing_type=not_disclosed_confirmed` | `pending_data` (애초에 이 분기 대상이 아니다) |

기존 `test_private_not_disclosed_dedupe` 와 `test_r04_absent_private_fcf_is_pending` 은 옛 계약(`status` 로 −2)을 고정하고 있어 **새 계약으로 갱신**했다. T-11 때와 같은 종류의 갱신이다.

## 6. 확인된 것과 미확인인 것

### 6.1 확인된 것

1. 값이 없는 관측은 **25건**이고 `status` 는 `not_disclosed` 24 · `parse_failed` 1 이다.
2. 그 25건이 **4갈래**로 갈린다 — `not_applicable` 10 · `unverified` 9 · `not_disclosed_confirmed` 4 · `indeterminate` 2.
3. **C-16 진입 대상이 2개사에서 0개사**가 된다(alibaba · spacex-xai). 단 이 `2` 는 **`coverage_comparable = yes` 가정하의 수**이고, 실제 도달 기업은 변경 전에도 0개사였다.
4. 재분류를 적용해도 **14개사 전 factor 점수·상태가 불변**이고, 승인 실행을 재계산해 `results.json` 과 대조한 결과도 **변동 0건**이다.
5. 지금 `_g4` 의 C-16 분기에 **도달하는 기업이 없다**(oracle 은 computed, amazon 은 판단 대기). `coverage_comparable` 은 `unknown` 11 · `no` 2 · `yes` 1 이다.
6. **`_g2` 도 `missing_type` 을 읽는다.** 비상장 2사가 **G2 에 닿지 않아** 점수가 바뀌지 않는다.
7. F9 정합 검사가 v1.7 의 **세 값**(`floor`·`g1_bep_retreat_score`·`g1_bands_proposed[2].score`)을 잡는다.
8. v1.5·v1.6 은 통과한다. **검사가 과거 규칙 파일을 깨지 않는다.**
9. 승인 대상 6종(`rules`·`observations`·`judgments`·`run`·`results`·`draft`)이 전부 불변이다.

### 6.2 미확인 — 추측하지 않고 남긴다

1. **palantir `net_borrowing_ttm`(`raw`=`없음`) 의 실제 성격.** 상장사라 구조 논거가 없어 `unverified` 로 남는다. **조사 대상이다.**
2. **`offbalance_B` 가 실제로 있는지.** C-13·NTM 담당이라 건드리지 않았다.
3. **amazon `contracted_revenue` 의 재파싱 결과.** C-13 담당.
4. **비상장 2사의 `net_cash`·`debt_ebitda` 실제 값.** 구조상 공개되지 않는다고 판정했을 뿐 값 자체는 모른다.
5. **C-06 재척도 후 v1.7 이 어떤 값을 가질지.** 결정 사항이다. *(4.2 에서 해소)*

## 7. 남은 결정

1. ~~**C-06 밴드 재척도.**~~ *2026-09-11 확정 — 4.2 참조.*
2. **F9 정합 검사의 배치** — 로드 시점(현재) vs 검증 시점(4.2).
3. **재분류 반영 시점.** 지금은 제안이다. `observations.json` 이 승인 해시 대상이라 반영은 새 실행과 승인을 거쳐야 하고 **그것은 사용자 결정**이다. 관측 등록·교체는 별건(`OBS-REG-25`)이라 이번에 하지 않았다.
4. ~~**`_g2` 마이그레이션.**~~ *보완에서 완료 — 5 절.*
5. **2.3 의 잠정 셋** — `OFFB-24` 회신에 따라 확정한다.

## 8. 재현 방법

```bash
cd worker/validation/miss-label-23
python reclassify.py                                  # reclassify-output.txt 와 같은 결과
cd ../.. && python -m unittest discover -s tests -q   # 165건 통과 · skip 0
```

**네트워크를 쓰지 않는다.**

| 파일 | 내용 |
|---|---|
| `scripts/scorecard/schema.py` | `MISSING_TYPES` · 관측 `missing_type` 검증 · `_validate_f9_policy` |
| `scripts/scorecard/calc_f9.py` | `_g4` 와 **`_g2`** 의 판별을 `missing_type` 으로 |
| `tests/test_scorecard_missing_type.py` | 신규 11건 |
| `tests/test_scorecard_f6_v17.py` | v1.7 재척도 고정 |
| `tests/test_scorecard_calc.py` | T-11·G2 를 새 계약으로 갱신 + `test_g2_reads_missing_type_not_status` |
| `reclassify.py` · `reclassify-output.txt` | 재분류와 점수 불변 확인 |
| `_derived/reclassification.json` | 25건 제안 |
