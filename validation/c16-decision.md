# C-16 확정 — `downgrade`

- 결정일. 2026-09-11.
- 결정자. 사용자.
- 선행. `offb-24-review.md`(`9c546e2`) · `missing-label-finding.md`(`583af3f`) · `miss-label-23-review.md`(`77d8c56`)

## 확정

**G4 산출 지표가 `not_disclosed_confirmed` 일 때 한 단계 하향한다(step −1).**

`v1.7` `run.decisions` 에 `{"id": "C-16", "choice": "downgrade"}` 를 넣는다.

## 적용 범위 — **`not_disclosed_confirmed` 하나뿐**

```
not_disclosed_confirmed  →  C-16 적용 (downgrade)
unverified               →  자료 대기
parse_failed             →  자료 대기
not_applicable           →  자료 대기
indeterminate            →  자료 대기
미분류(None)             →  자료 대기      ← 증거 없으면 안전한 쪽
```

**이 좁혀짐이 `downgrade` 를 고를 수 있게 한 전제다.** 좁혀지지 않았다면 `hold` 를 골랐을 것이다.

## 근거 셋

### 1. G2 선례와의 일관성

```
policies.f9.g2_private_not_disclosed = -2
anthropic·openai   "비상장 FCF 미공시 + 완충이 외부 조달뿐 → 보수적으로 -2"
```

**G2 는 이미 확인된 미공시에 −2 를 물린다.** v1.5 의 `미공시 보수 처리 원칙` 이다. **같은 성질의 결측을 G2 에서 벌하고 G4 에서 안 벌하면 규칙이 스스로 어긋난다.**

**중복 감점은 없다.** alibaba 의 G2 는 **공시된** FCF `−11.4B` 를 썼다. G4 의 `−1` 이 유일한 미공시 감점이고, 6.4 의 "동일한 미공시 사유를 G2·G4 에서 중복 감점" 에 해당하지 않는다.

### 2. `hold` 는 불투명을 보상한다

| 회사 | G4 | `hold` 일 때 |
|---|---|---|
| oracle | 공시 · 커버리지 2.552 | 0 |
| openai | 공시 · 커버리지 0.67 | **−1** |
| alibaba | 공시 안 함 | **0** |

**공시하고 커버리지가 나쁘면 깎이는데 아예 안 하면 안 깎인다.** 채점표가 "덮지 못하면 숨겨라" 라고 말하게 된다. **개별 판정이 아니라 규칙의 구조적 결함이다.**

### 3. 오늘 라벨을 고쳤기 때문에 안전해졌다

오늘 아침 상태로 `downgrade` 를 골랐다면 이렇게 됐다.

```
spacex-xai  offbalance_B        not_disclosed / raw "미확인"  →  감점
amazon      contracted_revenue  parse_failed                  →  감점
```

**둘 다 실제로는 공시돼 있었다.** `OFFB-24` 가 SEC 원문에서 찾았다. **우리가 안 찾은 것을 그 기업의 위험으로 둔갑시켰을 것**이고, 설계 지침 6.4 가 금지하는 바로 그 일이다.

**`MISS-LABEL-23` 이 `missing_type` 을 도입하고 `_g4()` 가 `not_disclosed_confirmed` 하나만 C-16 으로 보내게 되면서, 벌하는 대상이 "우리가 못 찾은 것" 에서 "회사가 공시하지 않겠다고 선언한 것" 으로 좁혀졌다.**

## 반대 논거와 그 한계

**`hold` 의 최선 논거** — BABA 는 합법적 회계정책(ASC 606 실무적 간편법, 20-F Note 2(g))을 택한 것이지 숨긴 것이 아니다. **타당하다.**

**다만 그 간편법은 1년 이하 계약과 청구권 기준 계약만 덮는다.** 그 밖에 중요한 장기 계약 수입이 있으면 면제로 가릴 수 없다. 면제를 택하고 아무것도 안 적은 것은 **비면제 부분이 크지 않다는 약한 신호**다.

**약한 신호라고 분명히 적는다.** Note 5 의 "중요하지 않다" 는 **과거 기간 인식액**에 관한 것이지 RPO 잔액 크기가 아니다. 설계진행이 한 번 그렇게 읽을 뻔했고 **틀린 독해다.** 뒷받침이지 근거가 아니다.

## 점수 영향

**오늘 기준 alibaba 한 기업이다.**

```
alibaba   G1 pass(profit, 영업이익률 +4.90%)
        → G2 FCF -11.4B 음수        -2
        → G3 런웨이 4.98년 step 0    -2
        → G4 not_disclosed_confirmed → downgrade  -1
        =  F9  -3
```

`hold` 였다면 `−2` 다. **한 칸.**

**적용 대상이 앞으로 늘어날 수 있다.** `coverage_comparable` 이 채워지고 결측 유형이 분류되면서 `not_disclosed_confirmed` 가 더 나올 수 있다. **그때마다 라벨이 실제로 "회사가 공시하지 않겠다고 선언했다" 를 뜻하는지 확인하는 것이 이 결정의 유지 조건이다.**

## 반영

`F6-REG-28` 에 이어지는 실행의 `run.decisions` 에 넣는다. **`v1.5` 는 불변이다.**
