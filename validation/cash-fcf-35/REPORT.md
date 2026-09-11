# CASH-FCF-35 — `cash`·`fcf_ttm` 12개사 등록 + SCOPE-34 후속 셋

작성일 2026-09-11. 담당 worker(HANSOLJJ/worker). 요청 `msg_27db905c1662`.
원자료 C-13 `4074894` `validation/cash-fcf-35/`.

## 결론

**예상과 정확히 같습니다. alibaba·spacex-xai 의 F9 가 −3 에서 −4 로 내려가고 나머지는 불변입니다.**

| | 결과 |
|---|---|
| 관측 | **24건** 등록 (12개사 × `cash`·`fcf_ttm`) |
| `cash` 정의 | **순수 현금.** 유동성 버퍼·총계·제한현금은 `basis` 에 보존 |
| 점수 변동 | **2건** — alibaba F9 −3→−4(런웨이 2.64년) · spacex-xai −3→−4(2.89년). **예상과 일치** |
| 순위 | spacex-xai 6→7위 · alibaba 10위 유지(7→6점) · palantir 11→10위 |
| **발견** | **legacy `cash` 의 정의가 세 갈래였습니다** — 7개사만 버퍼 (2절) |
| SCOPE-34 후속 | yahoo 두 host **`denied`** 이전 · `market_cap` 미검증 노출 (5·6절) |
| 원문 대조 | **46건 · 불일치 0건** |
| 승인 실행 | **6종 해시 전부 불변** · 14/14 완주 유지 |
| 테스트 | 222 → **223건** · skip 0 |

신규 네트워크 호출 없음. `v1.5`·승인 실행 파일 미변경. **승인은 하지 않았습니다.**

---

## 1. `cash` 를 순수 현금으로 등록했습니다

설계 지침 6.4 가 **사용 가능한 현금 및 현금성자산만** 포함하고, 단기 투자자산을 넣으려면 **환금성 기준을 먼저 정하라**고 합니다. **그 기준이 아직 없습니다.**

```
cash = us-gaap:CashAndCashEquivalentsAtCarryingValue  (ifrs-full:CashAndCashEquivalents)
```

**버리지 않았습니다.** 유동성 버퍼·총계·제한현금·구성요소를 전부 `basis.preserved_wider_definitions` 에 남겼습니다. 환금성 기준이 정해지면 그 자리에서 바로 쓸 수 있습니다.

| 회사 | 순수 현금 | 유동성 버퍼 | `fcf_ttm` |
|---|---|---|---|
| apple | 39,544 | 62,399 | +136,683 |
| microsoft | 20,935 | 76,843 | +66,987 |
| amazon | 78,213 | 122,988 | **−11,625** |
| nvidia | 22,443 | 56,586 | +127,006 |
| tesla | 15,219 | 43,524 | +5,762 |
| palantir | 2,030 | 9,409 | +3,358 |
| meta | 15,462 | 90,260 | +40,976 |
| oracle | 31,289 | 31,894 | **−23,686** |
| alphabet | 55,911 | 242,474 | +53,273 |
| spacex-xai | 93,522 | 93,522 | **−32,348** |
| tsmc | 88,233 | 99,720 | +31,959 |
| alibaba | 19,068 | 41,583 | **−7,226** |

(백만 USD)

---

## 2. 발견 — `legacy cash` 의 정의가 **세 갈래**였습니다

설계진행이 "12개사 중 7개사에서 legacy cash 가 버퍼 값과 소수점까지 같다" 고 하셨고 **그것은 맞습니다.** 나머지 5개사가 무엇이었는지를 마저 확인했습니다.

| `legacy cash` 가 같았던 것 | 개사 | 기업 |
|---|---|---|
| **유동성 버퍼**(현금 + 단기투자) | **7** | alphabet · amazon · meta · microsoft · oracle · palantir · tesla |
| **총계**(비유동 증권까지 포함) | **3** | apple · tsmc · alibaba |
| **어느 쪽도 아님** | **2** | nvidia(1.5% 차) · spacex-xai(6% 차) |

- **apple** — legacy 146,500 이 버퍼 62,399 가 아니라 총계 146,517 입니다. **버퍼의 2.3배**입니다.
- **spacex-xai** — legacy 100,000 인데 순수 93,522 · 버퍼 93,522 · 총계 94,352 입니다. v1.5 서술이 `현금 $100B(IPO)` 라 **반올림된 서술값**으로 보입니다.
- **nvidia** — legacy 62,500, 총계 63,443 로 1.5% 차입니다.

**`legacy cash` 가 단일 정의가 아니었습니다.** "사실상 유동성 버퍼였다" 는 진단은 7개사에 맞고 나머지 5개사에는 다른 값이 들어 있었습니다. 이것이 **순수 현금으로 통일해야 할 이유를 하나 더** 만듭니다 — 지금까지는 회사마다 다른 잣대로 완충을 재고 있었습니다.

각 관측의 `basis.legacy_comparison.legacy_equaled` 에 회사별로 무엇과 같았는지 적었습니다.

---

## 3. 점수 영향 — 3년 경계

```
alibaba     런웨이  2.64년  step -1   **3년 미만**   F9 -3 → -4
spacex-xai  런웨이  2.89년  step -1   **3년 미만**   F9 -3 → -4
oracle      런웨이  1.32년  step -1   3년 미만       F9 -3 (legacy 로도 이미 미만이라 불변)
amazon      런웨이  6.73년  step  0                  F9 -2 (불변)
```

**예상과 정확히 같습니다.** 둘 다 3년 경계를 가로질렀고 나머지는 불변입니다. 14개사 × 9 factor 중 **변동 2건**입니다.

### 3.1 alibaba 는 capex 가 둘인데 판정은 안 갈립니다

20-F 가 토지사용권을 포함한 capex 와 제외한 non-GAAP 을 둘 다 줍니다.

| | capex | fcf_ttm | 런웨이 |
|---|---|---|---|
| **GAAP**(토지사용권 포함) — **등록** | 18,275 | **−7,226** | **2.64년** |
| non-GAAP | 17,689 | −6,757 | 2.82년 |

**GAAP 쪽을 등록했습니다** — 현금이 실제로 나간 금액입니다. **둘 다 3년 미만이라 G3 판정은 갈리지 않습니다.** non-GAAP 변형을 `basis.non_gaap_variant` 에 보존했습니다.

### 3.2 순수 현금 대신 버퍼를 썼다면

alibaba 는 버퍼(41,583)로 계산하면 런웨이가 **5.75년**이 되어 step 이 0 입니다. **즉 이 판정은 `cash` 정의에 직접 걸려 있습니다.** 환금성 기준이 정해져 버퍼를 쓰게 되면 alibaba F9 가 −4 에서 −3 으로 돌아옵니다. 그 사실을 관측 `basis` 에 남겼습니다.

spacex-xai 는 순수 현금과 버퍼가 같아(단기투자 0) 정의가 바뀌어도 2.89년 그대로입니다.

---

## 4. 현지통화 환산 — 우리가 다시 계산했습니다

C-13 값을 그대로 쓰지 않고 **20-F 선언 환율로 재환산해 대조**했습니다.

| | 현지통화 | 환율 | 재계산 | C-13 보고 | 상대오차 |
|---|---|---|---|---|---|
| alibaba 현금 | ¥131,530 | **6.8980** | 19,068 | 19,068 | 0.0008% |
| tsmc 현금 | NT$2,767,856 | **31.37** | 88,233 | 88,233 | 0.0000% |

**환율 하나를 정정했습니다.** C-13 은 alibaba 에 `6.8979` 를 썼는데 20-F 문면은 `RMB6.8980 to US$1.00` 입니다. 0.0015% 차이라 백만 단위 반올림 결과가 같지만, **F6-REG-28 에서 등록한 환율과 통일**하는 편이 맞아 6.8980 으로 계산했습니다. 그 사실을 `basis.fx_note` 에 적었습니다.

---

## 5. SCOPE-34 후속 ① — yahoo 두 host 를 `denied` 로

지시대로 옮겼습니다. **사유를 둘 다** 적었습니다 — 하나만 적으면 나머지가 해소됐을 때 오독됩니다.

1. **robots.txt 전면 Disallow** — `User-agent: *` + `Disallow: /`, 26바이트, 예외 0건.
2. **이용약관** — `for any purpose` 로 목적 불문 자동 수집 금지. 개인 사용 예외 없음.

`query2` 도 **별도 항목**입니다. note 로만 적으면 `source_violation()` 이 못 잡고 마지막 fallback 으로 샙니다.

### 5.1 모순을 note 에 남겼습니다

> **기존 stock 파이프라인은 yfinance 를 쓴다** — `stock-research`·`stock-build`·`stock-plan`·`stock-goal` 스킬이 일봉을 거기서 받는다. **정책은 금지하는데 프로젝트는 이미 쓰고 있다.** 이 모순을 어떻게 할지는 사용자 사안이고 이 정책은 `sources.json` 에 등재되는 생산 원천만 규율한다. 다음 사람이 '왜 stock 은 쓰는데 scorecard 는 안 쓰나' 를 되묻지 않도록 여기 남긴다.

알려 주신 **`ClaudeBot`·`Claude-Web`·`anthropic-ai` 가 `Disallow: /` 목록에 있다**는 것도 직접 확인해 note 에 넣었습니다. API host 의 전면 금지와 별개로 **우리 계열 에이전트를 이름으로 지목한 금지**가 같은 사이트에 있습니다.

---

## 6. SCOPE-34 후속 ② — `market_cap` 미검증을 산출물에 드러냈습니다

### 6.1 제안 — 조건으로 걸지 않고 표시만 합니다

물으신 것에 답합니다. **P4 조건으로 걸어 점수를 깎지 않는 쪽을 제안하고 그대로 구현했습니다.**

`market_cap` 이 `legacy_unverified` 인 것은 **우리가 아직 실측하지 못한 것**이지 그 기업의 성질이 아닙니다. 조건으로 걸면 **우리 수집 공백을 기업 위험으로 둔갑시키는** 것이고, 그것이 MISS-LABEL-23 에서 세운 원칙이 막는 바로 그 동작입니다. 짚어 주신 그대로입니다.

### 6.2 구현 — `calc` 와 경고 양쪽에

```json
"unverified_inputs": {"market_cap": ["P1", "P2"], "net_cash": ["P2"]},
"unverified_inputs_note": "이 파라미터들은 status=legacy_unverified 관측 위에 서 있다.
                           **점수를 깎지 않는다** — 자료를 아직 실측하지 못한 것이지 그 기업의
                           성질이 아니다. 실측으로 교체되면 이 표시가 사라진다."
```

경고에도 나옵니다 — `미검증 입력 ⚠️ market_cap 이 legacy_unverified 인데 P1, P2 가 그 위에 선다 — 점수는 그대로`.

**F6 가 산출된 상장 11개사 전부에 붙습니다.** spacex-xai 는 `listed_newly` 라 P1·P2 를 안 써서 빠집니다.

### 6.3 덤으로 하나 더 잡혔습니다

`market_cap` 만 볼 줄 알았는데 **`net_cash` 도 `legacy_unverified`** 라 P2 가 미검증 입력 **둘** 위에 서 있습니다. 검사를 지표 이름으로 하드코딩하지 않고 관측 `status` 를 읽게 만들어서 잡혔습니다. `net_cash` 는 이번 실측 범위 밖이라 그대로 두고 표시만 했습니다.

### 6.4 EntityPublicFloat 확인 결과 받았습니다

`dei:EntityPublicFloat` 가 대체물이 못 된다는 것 — 내부자 보유분 제외, 기준일이 2025-03~2026-05 로 흩어짐, TSM·BABA·SPCX 는 부재 — 받아들입니다. 별도로 조사하지 않았습니다.

---

## 7. 14개사 전 factor 대조 (승인 실행 → 새 실행)

```
회사                 F1     F2     F3     F4     F5        F6     F7       F8       F9
alphabet            +5c    +4c    +3c    +5c    +4c     -1>-3    -1c      -1c       -1
amazon              +5c    +4c    +3c    +5c    +4c     -1>-2    -1c      -1c  judg>-2
meta                +5c    +4c    +3c    +3c    +3c     +0>-1    +0c      -1c       -1
microsoft           +5c    +3c    +3c    +4c    +4c     -1>-3    -1c      -1c       +0
tsmc                +2c    +5c    +3c    +4c    +4c   rule>-3    +0c      -4c       +0
alibaba             +4c    +4c    +3c    +4c    +3c   rule>-4    +0c      -4c  pend>-4
anthropic           +4c    +5c    +3c    +4c    +5c    -3c>-3    -1c   -3c>-3  pend>-2
apple               +5c    +2c    +2c    +3c    +3c     -2>-4    +0c      -3c       +0
nvidia              +2c    +5c    +2c    +5c    +2c     +0>-2    -3c      -3c       +0
palantir            +2c    +3c    +3c    +3c    +2c        -4    +0c      -3c       +0
spacex-xai          +3c    +4c    +3c    +5c    +3c     -5>-1    +0c      -3c  rule>-4
tesla               +2c    +3c    +3c    +4c    +2c        -5    -1c      -2c       -1
oracle              +3c    +2c    +3c    +3c    +3c     +0>-3    -3c      -4c       -3
openai              +4c    +4c    +2c    +4c    +2c    -4c>-4    -1c      -4c    -5>-4
```

`c` 는 승계(`carried_score`)입니다. **이번 과제가 움직인 것은 alibaba·spacex-xai 의 F9 둘뿐**이고 나머지 차이는 앞선 과제들의 누적입니다.

### 7.1 순위

| 순위 | 기업 | 과점 | 함정 | 조정 | 직전 대비 |
|---|---|---|---|---|---|
| 1 | Alphabet / Google · Amazon / AWS · Meta | 21·21·18 | −6·−6·−3 | **15** | |
| 4 | Microsoft | 19 | −5 | 14 | |
| 5 | Anthropic | 21 | −9 | 12 | |
| 6 | TSMC | 18 | −7 | 11 | 공동 6 → **단독 6** |
| 7 | SpaceX + xAI | 18 | −8 | 10 | 6 → **7위** (11→10점) |
| 8 | NVIDIA · Apple | 16·15 | −8·−7 | 8 | |
| 10 | Alibaba · Palantir | 18·13 | −12·−7 | 6 | alibaba 7→6점 · palantir 11→**10위** |
| 12 | Tesla | 14 | −9 | 5 | |
| 13 | OpenAI | 16 | −13 | 3 | |
| 14 | Oracle | 14 | −13 | 1 | |

**14/14 완주 유지 · 미결 규칙 결정 0건.**

---

## 8. 승인 대상 해시

| 대상 | 승인 baseline | 현재 baseline | 새 실행 |
|---|---|---|---|
| `rules`·`observations`·`judgments`·`run`·`results`·`draft` | — | **여섯 칸 전부 동일** | 전부 변경 |

`ai-scorecard-2026-09-baseline` 파일은 하나도 고치지 않았습니다. **승인은 하지 않았습니다.**

---

## 9. 확인된 것과 미확인인 것

### 9.1 확인된 것

1. `cash` 12건이 전부 **순수 현금**이고 버퍼·총계·제한현금이 `basis` 에 보존됐다.
2. **`legacy cash` 의 정의가 세 갈래였다** — 7개사 버퍼 · 3개사 총계 · 2개사 어느 쪽도 아님.
3. alibaba 2.64년 · spacex-xai 2.89년으로 **3년 경계를 가로지른다.** F9 둘 다 −4.
4. alibaba 의 GAAP/non-GAAP capex 차이는 **판정을 가르지 않는다**(둘 다 3년 미만).
5. 현지통화 환산이 20-F 선언 환율로 재계산했을 때 상대오차 0.001% 이내로 맞는다.
6. 미검증 입력이 **11개사 F6 에 표시되고 점수는 안 바뀐다.** `net_cash` 도 같이 잡혔다.
7. yahoo 두 host 가 `denied` 에 있고 `source_violation` 이 배제로 잡는다.

### 9.2 미확인 — 추측하지 않습니다

1. **환금성 기준.** 아직 없습니다. 정해지면 alibaba F9 가 −4 에서 −3 으로 돌아갑니다(3.2).
2. **`net_cash` 실측.** 이번 범위 밖이라 legacy 그대로이고 표시만 했습니다.
3. **`market_cap` 실측 경로.** `EntityPublicFloat` 는 대체물이 아니라고 확인받았고 다른 원천은 찾지 않았습니다.
4. **정책과 stock 파이프라인의 모순.** 사용자 사안이라 note 에만 남겼습니다.

## 10. 재현 방법

```bash
python validation/cash-fcf-35/verify_cash_fcf.py    # 원문 대조 46건
python validation/cash-fcf-35/apply_cash_fcf.py     # 관측 24건 등록
python scripts/scorecard_cli.py calculate ai-scorecard-2026-09-obsreg
python -m unittest discover -s tests                # 223건
```

**네트워크를 쓰지 않습니다.**

| 파일 | 내용 |
|---|---|
| `apply_cash_fcf.py` · `apply-output.txt` | 관측 24건 · legacy 정의 대조표 |
| `verify_cash_fcf.py` · `verify-output.txt` | 원문 대조 46건 |
| `scorecard/rules/v1.7.json` | yahoo 두 host `denied` 이전 |
| `scripts/scorecard/calc_f6_params.py` | `unverified_inputs` 노출 (점수 미개입) |
| `tests/test_scorecard_f6_v17.py` | yahoo `denied` 계약 · 모순 기록 고정 |
