# FMP analyst-estimates 직접 조사 — 실제 응답 검증

작성일 2026-09-09. 담당 worker(HANSOLJJ/worker). `../fincept-consensus-01/REPORT.md` 9절에서 분리한 후속 과제다.

사용자가 발급한 FMP 무료 등급 키로 실제 호출해 검증했다. **키는 환경변수와 스크래치 파일로만 다뤘고 이 보고서·커밋·Orca 메시지 어디에도 남기지 않았다.** 호출은 REST 4 회, MCP 6 회로 무료 한도(250 콜/일) 대비 미미하다.

## 1. 결론

**무료 등급으로는 Valley 를 대체할 수 없다.** `period=quarter` 가 유료 파라미터로 막혀 있어 회계분기 컨센서스를 받을 수 없고, 그것이 우리 F6 이 필요로 하는 유일한 형태다.

요청받은 다섯 항목의 답이다.

| # | 항목 | 결과 | 근거 |
|---|---|---|---|
| 1 | `period=quarter` 지원 | **무료 등급 차단.** FMP 자체는 지원 | REST HTTP 402, MCP ACCESS DENIED (2.1) |
| 2 | 표본 수 | **제공.** `numAnalystsEps` · `numAnalystsRevenue` | 실제 응답 (2.2) |
| 3 | min/max | **제공.** `epsLow` · `epsHigh` | 실제 응답 (2.2) |
| 4 | 무료 등급 접근성 | **annual 만 가능.** quarter 불가 | 2.1 |
| 5 | **미발표 4 개 분기 범위** | **무료 등급으로 충족 불가** | 1 번의 귀결 (2.4) |

구조 자체는 우리가 찾던 것과 맞다. 회계기간별로 최소·평균·최대와 표본 수를 주고 미래 기간을 포함한다. **막는 것은 데이터 구조가 아니라 요금제다.**

그리고 유료로 올리더라도 그대로 쓸 수는 없다. 실제 응답에서 **기준 불일치 한 건과 결측을 0 으로 채운 사례 한 건**을 확인했다(3절). 둘 다 우리 규칙이 금지하는 형태다.

## 2. 검증 결과

### 2.1 `period=quarter` 는 유료 파라미터다

두 개의 독립된 전송 경로가 같은 답을 준다.

**REST — HTTP 402**

```
GET https://financialmodelingprep.com/stable/analyst-estimates
      ?symbol=AAPL&period=quarter&limit=8&apikey=<free>

HTTP 402
Premium Query Parameter: 'Special Endpoint : This value set for 'period' is not
available under your current subscription please visit our subscription page to
upgrade your plan at https://financialmodelingprep.com/
```

**MCP — ACCESS DENIED**

`https://financialmodelingprep.com/mcp` 의 `analyst` 도구, `endpoint=financial-estimates`, `period=quarter`.

```
ACCESS DENIED: A parameter you passed to this tool ("analyst") requires a higher
plan. The user is currently on a lower-tier plan. … Do not retry this tool with
the same parameter value; the user may retry with values their plan allows.
```

**막힌 것은 endpoint 가 아니라 파라미터 값이다.** 같은 endpoint 에 `period=annual` 을 주면 HTTP 200 이다. 즉 무료 키로도 이 데이터셋에 접근은 하되 분기 해상도만 잘려 있다.

### 2.2 응답 구조 — 실제 필드 (annual, AAPL)

`GET /stable/analyst-estimates?symbol=AAPL&period=annual&limit=6` → HTTP 200, 6 행.

필드 22 개 전체다.

```
date, symbol,
revenueLow, revenueAvg, revenueHigh,
ebitdaLow, ebitdaAvg, ebitdaHigh,
ebitLow, ebitAvg, ebitHigh,
netIncomeLow, netIncomeAvg, netIncomeHigh,
sgaExpenseLow, sgaExpenseAvg, sgaExpenseHigh,
epsLow, epsAvg, epsHigh,
numAnalystsRevenue, numAnalystsEps
```

| date | epsAvg | epsLow | epsHigh | numAnalystsEps | numAnalystsRevenue |
|---|---|---|---|---|---|
| 2030-09-27 | 12.8 | 12.12038 | 14.13177 | 14 | 16 |
| 2029-09-27 | 12.34288 | 11.68753 | 13.62709 | 8 | 12 |
| 2028-09-27 | 10.6602 | 9.48543 | 11.44589 | 19 | 21 |
| 2027-09-27 | 9.57134 | 9.0396 | 10.18334 | 29 | 29 |
| 2026-09-27 | 8.82861 | 8.81863 | 8.85854 | 27 | 27 |
| 2025-09-27 | 7.38183 | 7.22157 | 7.43191 | 27 | 25 |

확인 사항 셋.

- **표본 수는 지표별로 다르다.** FY2025 는 EPS 27 명, 매출 25 명이다. 우리 스키마에서 표본 수를 지표에 종속시켜 저장해야 한다는 뜻이다. 기업 단위 커버 애널리스트 수와 같다고 가정하면 안 된다(공통 방법 문서와 일치).
- **회계연도 말이 라벨에 그대로 온다.** AAPL 은 09-27 이다. 3·6·9·12 월로 맞춰져 있지 않다. 이는 우리에게 유리하다.
- **미래 기간을 준다.** 기준일 2026-09 시점에 2030-09 까지 나온다.

### 2.3 목표주가 컨센서스는 무료 등급에서 열린다

`endpoint=price-target-consensus`, AAPL → HTTP 200.

```json
[{"symbol":"AAPL","targetHigh":400,"targetLow":245,"targetConsensus":339.35,"targetMedian":360}]
```

min/median/avg/max 구조가 맞지만 **대상이 목표주가다.** 우리 F6 은 EPS 를 요구하므로 채점 입력으로 쓸 수 없다. FinceptTerminal 이 화면에 그리던 게이지와 같은 성격의 데이터다.

### 2.4 미발표 4 개 분기 — 무료 등급으로는 판정 자체가 불가능

분기 응답을 못 받으므로 다음을 **하나도** 확인할 수 없다.

- 응답이 미래 분기를 몇 개나 주는지
- 그 분기가 각 기업의 다음 4 개 **미발표** 회계분기와 일치하는지
- 끝났지만 미발표인 분기가 포함되는지

연간 데이터로 대체할 수 없다. 연간 EPS 컨센서스를 4 분기 합 대신 쓰는 것은 우리 규칙에서 `annual_weighted_proxy` 이며 C-13 미결 사항이다. **이번 조사 결과는 12 개사 확보 수준을 0/4 에서 바꾸지 못한다.**

### 2.5 FinceptTerminal 이 부르던 v3 경로는 죽었다

이전 보고서(`fincept-consensus-01`)에서 확인한 `fmp_extra_data.py:36` 의 v3 호출을 실제로 시도했다.

```
GET https://financialmodelingprep.com/api/v3/analyst-estimates/AAPL?period=annual&apikey=<free>

HTTP 403
Legacy Endpoint : Due to Legacy endpoints being no longer supported - This endpoint
is only available for legacy users who have valid subscriptions prior August 31, 2025.
```

`period` 를 `quarter` 로 줘도 같은 403 이다. **FinceptTerminal 의 `estimates` 커넥터는 2025-08-31 이후 가입자에게는 동작하지 않는다.** 앞선 보고서에 이 사실을 추가로 남긴다. 우리가 채택한다면 `stable` 세대를 직접 불러야 한다는 판단이 실측으로 확인됐다.

## 3. 채택 전에 반드시 처리해야 할 두 가지

유료 등급으로 올려 분기 데이터를 받더라도 그대로 넣으면 안 된다. 무료 등급의 연간 응답만으로도 문제 두 개가 드러났다.

### 3.1 통화와 주식 단위가 섞여 있다 (TSMC·Alibaba)

`symbol=TSM`, annual, 2029-12-31 응답이다.

```
revenueAvg    = 11,654,173,860,000
netIncomeAvg  =  5,706,390,913,137
epsAvg        =  1100.3217
```

매출·순이익은 **TWD** 다(조 단위). 그런데 `epsAvg` 1100.32 는 보통주 기준일 수 없다. 역산하면 이렇다.

```
netIncomeAvg / epsAvg = 5,706,390,913,137 / 1100.3217 = 5,186,111,401 주
TSMC 보통주 약 25.93B → ADR 환산(1 ADR = 보통주 5주) = 5,186,000,000
보통주 기준이었다면 EPS 는 220.1 TWD 여야 한다
```

**단위가 정확히 ADR 수와 일치한다.** 즉 `epsAvg` 는 **TWD per ADR** 이고 매출·순이익은 TWD 다. 통화는 현지, 주식 단위는 예탁증권인 혼합 기준이다.

Alibaba 도 같다. `symbol=BABA`, 2030-03-31 에서 역산하면 2,404,375,001 단위로 ADS 수(보통주 ÷ 8)와 맞는다. 재무는 CNY 다.

우리 F6 은 주가 ÷ EPS 를 **같은 통화·같은 주식 기준**으로 요구한다(`calc_f6._basis_alignment`). TSM ADR 주가는 USD 다. 이 EPS 를 그대로 나누면 환율 배수만큼 틀린다. 우리 스키마는 이런 관측을 `incompatible_basis` 로 걸러야 하며, 자동으로 통과시키면 안 된다.

**FMP 응답에는 통화 필드가 없다.** 22 개 필드 어디에도 currency 표기가 없어서, 값만 보고는 TWD 인지 USD 인지 알 수 없다. 기업별로 별도 확인해 `basis` 를 우리가 채워야 한다.

### 3.2 결측을 0 으로 채운다

`symbol=BABA`, 2031-03-31 행이다.

```
epsAvg = 0    epsLow = 0    epsHigh = 0    numAnalystsEps = 10
netIncomeAvg = 0            revenueAvg = 1,829,876,520,503
```

**애널리스트 10 명이 있는데 EPS 가 0 이다.** 매출 추정은 정상적으로 들어 있다. 진짜 컨센서스가 0 일 리 없고 결측을 0 으로 인코딩한 것이다.

이는 우리가 명시적으로 금지한 형태다(`unknown ≠ 0`). 파서가 이 행을 그대로 받으면 EPS 0 이 4 분기 합에 섞여 PER 을 왜곡하거나 `pending_data` 로 가야 할 건을 `ok` 로 만든다. **`numAnalystsEps > 0` 인데 `epsAvg == epsLow == epsHigh == 0` 이면 결측으로 판정하는 규칙이 반드시 필요하다.**

같은 값이 진짜 0 인 경우와 구분되지 않는다는 점도 기록해 둔다. 우리 규칙은 EPS 0·음수를 유효 관측으로 보존하므로, 이 판정 규칙은 "세 통계가 동시에 0" 이라는 조건으로 좁혀야 오탐을 피한다.

## 4. 비용 판단 재료

무료 등급이 막혔으므로 유료 전환 여부가 결정 사항이 된다. 다만 **어느 등급부터 `period=quarter` 가 열리는지는 확인하지 못했다.**

공개 가격표 기준으로 Starter $29/월, Professional $69/월, Enterprise $139/월이며, Starter 소개 문구는 "annual fundamentals and ratios" 로 연간을 명시한다. 이 문구대로면 Starter 로도 분기 컨센서스가 안 열릴 수 있다.

**구매 전에 판매처에 분기 파라미터 해금 등급을 직접 확인할 것을 권한다.** 문서 문구만 보고 결제하면 이번 조사와 같은 결과가 반복될 수 있다. 가격 정보는 2 차 자료 기준이며 이번 조사에서 실측하지 않았다.

## 5. 권고

1. **무료 등급 FMP 는 Valley 대체재가 아니다.** 12 개사 확보 수준은 0/4 그대로다. 이 결과로 점수나 정책을 바꾸지 않는다.
2. **유료 전환은 분기 해금 등급을 확인한 뒤 결정한다.** 확인 없이 결제하지 않는다.
3. **채택하더라도 정규화는 우리 몫이다.** 응답에 통화 필드가 없고 EPS 주식 단위가 ADR/ADS 다. 기업별 `basis`(currency, share_basis)를 우리가 채우고 대조해야 한다.
4. **결측 0 판정 규칙을 먼저 만든다.** `numAnalystsEps > 0` 이고 `epsAvg == epsLow == epsHigh == 0` 이면 값이 아니라 결측으로 다룬다.
5. **다른 원천 조사를 병행한다.** FMP 유료화가 유일한 길이 아니다. Finnhub 실적 캘린더의 분기 EPS 추정치가 무료 등급에서 어디까지 열리는지 확인할 가치가 있다.

## 6. 재현 방법

키는 환경변수로만 다룬다. 보고서·메시지·git 에 남기지 않는다.

```bash
export FMP_API_KEY='...'

# 항목 1·4 — 분기 차단 확인 (HTTP 402)
curl -s -w "\nHTTP=%{http_code}\n" \
  "https://financialmodelingprep.com/stable/analyst-estimates?symbol=AAPL&period=quarter&limit=8&apikey=$FMP_API_KEY"

# 항목 2·3 — 연간 응답 구조 (HTTP 200)
curl -s "https://financialmodelingprep.com/stable/analyst-estimates?symbol=AAPL&period=annual&limit=6&apikey=$FMP_API_KEY" \
  | python -c "import json,sys; d=json.load(sys.stdin); print(sorted(d[0])); [print(r['date'],r['epsAvg'],r['epsLow'],r['epsHigh'],r['numAnalystsEps']) for r in d]"

# 2.5 — v3 레거시 폐지 확인 (HTTP 403)
curl -s "https://financialmodelingprep.com/api/v3/analyst-estimates/AAPL?period=annual&apikey=$FMP_API_KEY"

# 3.1 — 주식 단위 역산
curl -s "https://financialmodelingprep.com/stable/analyst-estimates?symbol=TSM&period=annual&limit=2&apikey=$FMP_API_KEY" \
  | python -c "import json,sys; [print(r['date'], r['netIncomeAvg']/r['epsAvg'] if r['epsAvg'] else 'eps=0') for r in json.load(sys.stdin)]"
#   → 5,186,111,401 ≈ TSMC 보통주 25.93B / 5 (ADR 단위)

# 3.2 — 결측 0 사례
curl -s "https://financialmodelingprep.com/stable/analyst-estimates?symbol=BABA&period=annual&limit=2&apikey=$FMP_API_KEY"
#   → 2031-03-31 행: epsAvg/Low/High 모두 0, numAnalystsEps 10
```

MCP 경로도 같은 결과를 준다. `https://financialmodelingprep.com/mcp?apikey=<key>` 에 JSON-RPC 로 `initialize` → `tools/call`(`analyst`, `endpoint=financial-estimates`)를 보내면 된다. 무료 등급에서 `period=quarter` 는 ACCESS DENIED 다.

## 7. 미확인으로 남긴 것

1. **분기 파라미터를 해금하는 최소 유료 등급.** 4 절 참조. 실측하지 않았다.
2. **유료 등급의 분기 응답이 미발표 4 개 분기를 덮는지.** 항목 5 는 여전히 미검증이다. 등급을 올려야만 확인된다.
3. **유료 등급 분기 응답의 통화·주식 단위.** 연간에서 확인한 혼합 기준이 분기에서도 같은지.
4. **12 개사 전수 확인.** 이번에는 AAPL·TSM·BABA 세 종목만 호출했다. 무료 등급으로는 연간만 나오므로 전수 호출의 실익이 없어 호출을 아꼈다.
5. **가격 정보.** 2 차 자료 기준이며 실측하지 않았다.
