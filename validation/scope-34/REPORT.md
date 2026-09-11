# SCOPE-34 — `usage_scope` 확정과 yfinance 등재 시도

작성일 2026-09-11. 담당 worker(HANSOLJJ/worker). 요청 `msg_bde0a0dea4c7`.
선행 설계진행 `6ca810f` `validation/scope-final-decision.md` (사용자 확정).

## 결론

**과제 하나는 끝냈고, 과제 둘은 지시하신 보고 조건에 걸렸습니다.**

| | 결과 |
|---|---|
| ① `usage_scope` | **`personal_internal_only` 단독으로 확정.** `supersedes` 로 09-10 정정과 오늘 합집합을 이었습니다 |
| ① `not_adopted` 넷 | 그대로 유지. **약관 사유 해소를 반영하고 남은 사유를 정확히** 했습니다 |
| ② yfinance 등재 | **올리지 못했습니다.** robots.txt 전면 금지 + 약관이 `for any purpose` 로 개인 사용까지 배제 |
| 점수 | **14개사 전 factor 변동 0건 · 순위 동일 · 14/14 완주 유지** |
| v1.5·v1.6 | **로드 정상.** 테스트로 고정 |
| 승인 실행 | **6종 해시 전부 불변** |
| 테스트 | 220 → **222건** · skip 0 |

---

## 1. ② 를 먼저 보고합니다 — 개인 사용조차 막습니다

지시는 **"개인 사용조차 막는 조항이 나올 때만 보고하십시오"** 였습니다. **그 조건에 해당합니다.**

### 1.1 robots.txt — 전면 금지

확인 목적으로 조회하고 응답 본문을 그대로 보존했습니다(`_raw/`, sha256 은 `fetch-meta.json`).

```
$ query1.finance.yahoo.com/robots.txt   (200, 26 bytes)
User-agent: *
Disallow: /

$ query2.finance.yahoo.com/robots.txt   (200, 26 bytes)
User-agent: *
Disallow: /
```

**26바이트, 예외 한 줄도 없습니다.** 비교를 위해 같이 받은 `finance.yahoo.com/robots.txt` 는 2,539바이트에 `Allow:` 가 섞인 선택적 목록입니다 — **API host 두 개만 전면 금지**입니다.

이 형태는 우리가 이미 `denied` 로 보낸 것과 같습니다.

> `api.nasdaq.com` — "생산 원천 영구 배제. robots.txt 가 `User-agent *` 에 `Disallow /` 이고 이용약관이 automated or manual process 로 데이터를 캡처하는 것을 금지한다"

그리고 우리 `policy_note` 가 이미 규정합니다.

> **"법인이든 개인이든 robots.txt 의 전면 Disallow 를 무르지 않는다 — `denied` 의 `api.nasdaq.com` 을 보라."**

### 1.2 이용약관 — `for any purpose`

Yahoo Terms of Service 원문입니다(보존 `_raw/yahoo_tos.html`, 167,945바이트).

> "access or collect data, or attempt to access or collect data, from our Services using any automated means, devices, programs, algorithms or methodologies, including but not limited to robots, spiders, scrapers, data mining tools, or data gathering or extraction tools, **for any purpose** without our express, prior permission."

**`for any purpose` 라 개인 사용 예외가 없습니다.** Finnhub·FMP 처럼 "법인은 안 되고 개인은 된다" 는 형태가 아니라 **목적을 가리지 않습니다.** `usage_scope` 를 `personal_internal_only` 로 좁힌 것이 이 조항을 해소하지 못합니다.

ToS 본문에서 `personal` 은 15회 나오는데 전부 소프트웨어 라이선스 문구(`we grant you a personal, royalty-free … license`)나 개인정보 맥락이고, **자동 수집을 개인에게 허용하는 조항은 없습니다.**

### 1.3 그래서 `allowed` 로 올리지 않았습니다

지시서가 이 함정을 먼저 짚어 주셨습니다.

> "지금 note 가 약관 미검토라고 적고 있어서 그대로 올리면 finnhub 과 똑같이 약관 안 읽고 allowed 에 올린 상태가 됩니다. 오늘 그것을 고쳤으니 반복하지 마십시오."

**읽었고, 읽은 결과가 안 됨이었습니다.**

### 1.4 대신 사유를 정정했습니다 — 지적하신 소멸은 맞습니다

기존 `unlisted` 사유가 틀렸다는 판단은 **정확합니다.** 그대로 두지 않고 교체했습니다.

| | |
|---|---|
| **소멸한 사유** | "회계분기 창 특정 0/12 이고 향후 전망이 2개 분기뿐" — **NTM PER 컨센서스 용도 판정**이었습니다. F6 가 v1.7 에서 네 파라미터로 재정의돼 컨센서스를 안 쓰므로 사라집니다. **주가는 애초에 그 판정 대상이 아니었습니다.** |
| **새 사유** | robots.txt 전면 금지 + 약관 `for any purpose` (1.1·1.2) |

`reason_type` 을 `technical` 에서 **`both`** 로 바꿨습니다. 소멸한 사유와 새 사유를 같은 칸에 나란히 적어, 다음 사람이 **어느 사유가 살아 있는지** 헷갈리지 않게 했습니다.

### 1.5 `query2` 도 같이 처리했습니다 — 별도 항목으로

같은 서비스이고 robots.txt 도 같습니다(직접 조회로 확인). **note 로만 적지 않고 별도 항목으로 넣었습니다** — note 는 `source_violation()` 이 못 읽어 `query2` 가 안내 없이 빠져나갑니다. yfinance 는 두 host 를 번갈아 쓰므로 한쪽만 등재하면 나머지가 샙니다.

### 1.6 기존 관행은 사실이고, 이 정책은 그것을 판정하지 않습니다

말씀대로 **가격 용도 yfinance 는 이 프로젝트의 관행입니다** — `stock-research`·`stock-build`·`stock-plan`·`stock-goal` 스킬이 일봉을 거기서 받습니다(확인했습니다).

다만 이 정책은 `sources.json` 에 등재되는 **생산 원천**을 대상으로 하고, **기존 관행을 여기서 승인하거나 금지하는 것이 아닙니다.** 그 관행을 어떻게 할지는 별건이고 제가 정할 일이 아닙니다. 그 구분을 `unlisted` note 에 적었습니다.

### 1.7 남는 문제 — 가격 원천이 없습니다

**F6 의 P1·P2 분자(`market_cap`)를 만들 가격 원천이 allowlist 에 여전히 없습니다.**

```
allowed = data.sec.gov · www.sec.gov · www.federalreserve.gov
```

SEC 는 주가를 내지 않고 연준 H.10 은 환율뿐입니다. **현재 `market_cap` 12건은 전부 `legacy_unverified`** 이고, 이번 과제는 등재까지라 그대로 뒀습니다. **가격 원천 없이는 다음 과제(market_cap 실측)가 성립하지 않습니다.** 숨기지 않고 테스트로도 고정했습니다(`test_no_price_source_in_allowlist`).

---

## 2. ① `usage_scope` 확정

```json
"scope": "personal_internal_only",
"evaluation_rule": "단일 범위다. … 개인 사용조차 막는 조항이나 robots.txt 전면 Disallow 가 있으면
                    부적격이고, 그때만 사용자에게 보고한다. 개인 사용이 허용되면 되묻지 않고 등재한다."
```

**`supersedes` 로 대체 관계를 이었습니다.**

> 2026-09-11 SCOPE-34 사용자 확정. **이 결정이 앞선 둘을 모두 대체한다.** (1) 2026-09-10 의 `corporate_internal_only` 정정, (2) 2026-09-11 오전의 personal+corporate 합집합(SRC-POLICY-32). 세션 초반 사용자 진술이 personal use only 였고 그것이 최종 확정과 같다 — **같은 건을 세 번 되물은 것이고 다시 올리지 않는다.**

`note` 에 경위를 남겼습니다. 앞으로 이 건을 사용자 결정으로 올리지 않고, **개인 사용조차 막는 원천이 나올 때만 보고**한다는 규칙도 같이 적었습니다. 이번이 그 첫 사례입니다.

### 2.1 `not_adopted` 넷 — 되살아나는 원천이 없습니다

확인하신 대로입니다. **약관 사유 해소를 반영하고 남은 사유를 정확히 했습니다.** `reason_type` 도 남은 사유의 종류에 맞게 고쳤습니다.

| host | `reason_type` | 약관 사유 | **남은 사유** |
|---|---|---|---|
| `www.alphavantage.co` | terms → **technical** | 해소 | **향후 분기 전망 2개** — F6 의 4개 분기를 못 만듭니다 |
| `financialmodelingprep.com` | terms → **technical** | 해소 | **무료 등급이 `period=quarter` 차단**(HTTP 402). `annual` 만 200 |
| `finnhub.io` | terms (유지) | **일부만 해소** | **파생 결과 공유 서면 승인** — 넷 중 약관 사유가 남는 유일한 원천 |
| `data.nasdaq.com` | cost (유지) | 무관 | 연 1,200달러 비용 결정 |

남는 사유는 **우리 보고서에서 검증**했습니다 — AV 는 `validation/av-source-11/REPORT.md` 4.3("향후 분기 2 개와 basis 4 필드 부재가 그대로다"), FMP 는 `validation/fmp-estimates-02/REPORT.md` 2.1·2.4(`period=quarter` 가 유료 파라미터).

`reason_type` 이 바뀐 둘은 note 앞에 `[SCOPE-34 2026-09-11] reason_type 을 terms 에서 technical 로 바꿨다 — 약관 사유가 해소되고 남은 사유의 종류가 달라졌다` 를 붙여 **판단이 바뀐 것을 지우지 않았습니다.**

Finnhub 의 남은 조항에 대해 한 줄 덧붙였습니다 — "산출물을 공유하지 않고 혼자 열람만 한다면 '공유' 에 해당하지 않는다는 해석이 가능하나, **그 해석을 우리가 단정하지 않는다** — 서면으로 확인해야 한다."

---

## 3. 곁가지로 고친 것 — 같은 함정을 두 번 겪지 않으려고

`query1` 을 `unlisted` 에 둔 채 돌려 보니 이렇게 나왔습니다.

```
query1.finance.yahoo.com 는 원천 allowlist 에 없음 — 약관 확인 후 규칙에 등재하고 쓴다
                                                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                                                    방금 확인해서 막은 host 에 재조사를 지시한다
```

**오늘 보완 ③에서 `data.nasdaq.com` 으로 고친 것과 똑같은 함정입니다.** `unlisted` 는 `source_violation()` 이 안 읽는다는 계약이었기 때문입니다.

같은 방향으로 고쳤습니다 — `source_violation()` 이 `unlisted` 도 읽어 **기록된 사유를 돌려줍니다.**

```
query1.finance.yahoo.com 는 검토를 마치고 등재하지 않은 host — [SCOPE-34 … 사유 교체] …
(검토 2026-09-11). 재조사 전에 이 사유부터 본다.
```

**판정은 그대로 위반이고 안내만 달라집니다.** 이전 계약을 고정하던 테스트 셋은 **지우지 않고** "무엇을 지키려던 검사였는지" 를 docstring 에 남기고 새 계약으로 갱신했습니다 — 목적은 **"unlisted 가 허용으로 바뀌지 않는다"** 였고 그 불변식은 지금도 유효합니다. `denied`·`not_adopted`·`allowed` 판정이 가려지지 않는 것까지 같이 고정했습니다.

이것은 지시받지 않은 변경이라 **되돌리기 쉽게** 한 군데(`source_violation` 의 블록 하나)에 모아 두었고 `policy_note` 에 변경 사실과 이유를 적었습니다.

---

## 4. 완료 조건 확인

| 조건 | 결과 |
|---|---|
| 점수가 안 바뀌는가 | **14개사 × 9 factor 변동 0건.** 순위 동일. 14/14 완주 유지 |
| `market_cap` | 12건 전부 `legacy_unverified` 그대로 — 이번 과제는 등재까지 |
| v1.5·v1.6 로드 | **정상.** `v1.5` `9231b3a0…` · `v1.6` `a86d048f…` 로드 확인, 테스트로 고정 |
| 승인 대상 6종 | 승인 baseline 과 현재 baseline 이 **여섯 칸 다 동일** |
| 기존 실행 | `ai-scorecard-2026-09-baseline` 파일 **미변경** |

`results_hash` 는 `45f5bd8c…` → `4320682e…` 로 바뀝니다 — 규칙 파일이 바뀌어 `rule_hash` 가 결과에 들어가기 때문이고, **점수는 한 칸도 안 움직입니다.**

---

## 5. 확인된 것과 미확인인 것

### 5.1 확인된 것

1. `query1`·`query2`.finance.yahoo.com 의 robots.txt 는 **`User-agent: *` + `Disallow: /` 전면 금지**(각 26바이트, 직접 조회·보존).
2. Yahoo ToS 가 자동 수집을 **`for any purpose`** 로 금지한다 — 개인 사용 예외 없음.
3. 기존 `unlisted` 기술 사유는 **소멸했다**. NTM PER 용도 판정이었고 F6 재정의로 무관해졌다.
4. 가격 용도 yfinance 는 **이 프로젝트의 기존 관행이다**(스킬 4개에서 확인).
5. `not_adopted` 넷 중 **좁혀서 되살아나는 원천이 없다**. 남는 사유를 우리 보고서로 검증했다.
6. **가격 원천이 allowlist 에 없다.** F6 P1·P2 분자를 만들 경로가 없다.
7. 점수 변동 0건 · 승인 대상 6종 보존.

### 5.2 미확인 — 추측하지 않습니다

1. **Yahoo 의 `express, prior permission` 을 받는 경로.** 조회하지 않았습니다. 개인 사용자에게 그 경로가 열려 있는지 모릅니다.
2. **finance.yahoo.com(HTML 사이트) 경유가 대안인지.** robots.txt 가 선택적이지만 같은 ToS 가 적용되고, HTML 스크래핑이 `automated means` 에 걸리지 않는다고 볼 근거가 없습니다. **더 나은 길로 보이지 않아 파고들지 않았습니다.**
3. **기존 스킬 관행을 어떻게 할지.** 이 정책의 대상이 아니고 제가 정할 일이 아닙니다.
4. **대체 가격 원천.** 이번 과제 범위 밖이라 조사하지 않았습니다.

## 6. 다음으로 필요한 결정

**가격 원천을 어떻게 할지가 다음 과제의 선행 조건입니다.** 제가 판단할 것이 아니라 갈래만 적습니다.

| 갈래 | 내용 |
|---|---|
| A | **Yahoo 에 `prior permission` 을 문의한다.** 받으면 등재 근거가 생깁니다 |
| B | **다른 가격 원천을 조사한다.** 약관이 개인 사용을 허용하는 곳 |
| C | **`market_cap` 을 legacy 로 둔 채 간다.** F6 P1·P2 가 legacy 입력 위에 서 있다는 사실을 근거란에 남기고 진행 |
| D | **`denied` 로 옮긴다.** `api.nasdaq.com` 과 형태가 같아 일관성으로는 이쪽인데, 지시가 `allowed` 로 올리는 것이었으므로 제가 정하지 않았습니다 |

## 7. 재현 방법

```bash
python validation/scope-34/verify_scope.py          # robots·약관 대조와 정책 반영 확인
python -m unittest discover -s tests                # 222건
```

**네트워크는 확인 목적 조회 4건만 썼습니다**(robots.txt 3 + ToS 1). 응답 본문을 `_raw/` 에 그대로 보존했고 sha256·상태코드·조회 시각을 `_raw/fetch-meta.json` 에 남겼습니다. 재현 시에는 보존본을 읽고 새로 호출하지 않습니다.

| 파일 | 내용 |
|---|---|
| `_raw/query1_robots.txt` · `query2_robots.txt` · `finance_robots.txt` | robots.txt 원문 |
| `_raw/yahoo_tos.html` | 이용약관 원문 167,945바이트 |
| `_raw/fetch-meta.json` | url·상태·바이트·sha256·조회 시각 |
| `verify_scope.py` · `verify-output.txt` | 원문 대조와 정책 반영 확인 |
| `scorecard/rules/v1.7.json` | `usage_scope` 확정 · `not_adopted` 갱신 · `unlisted` 사유 교체 |
| `scripts/scorecard/rules.py` | `source_violation()` 이 `unlisted` 를 읽음 |
| `scripts/scorecard/schema.py` | `usage_scope.supersedes` 허용 |
