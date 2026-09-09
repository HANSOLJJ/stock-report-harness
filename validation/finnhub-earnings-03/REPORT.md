# Finnhub 실적 캘린더 분기 EPS 추정치 조사 — 실제 응답 검증

작성일 2026-09-09. 담당 worker(HANSOLJJ/worker). `../fmp-estimates-02/REPORT.md` 5절 권고 (5) 에서 이어진 과제다.

사용자가 발급한 Finnhub 무료 등급 키로 실제 호출해 검증했다. **키는 환경변수와 저장소 밖 스크래치 파일로만 다뤘고 이 보고서·커밋·Orca 메시지 어디에도 남기지 않았다.** 호출은 약 20 회이며 무료 등급 한도(분당 60 콜) 대비 미미하다.

## 1. 결론

**무료 등급에서 분기 EPS 추정치를 실제로 받을 수 있다.** FMP 와 달리 유료 벽에 막히지 않는다. 그러나 우리 F6 을 열지는 못한다. 이유가 세 가지이고, 분기 수 부족은 그중 가장 작은 문제다.

| 문제 | 내용 | 심각도 |
|---|---|---|
| 미래 분기 3 개 | 11 개 종목 중 10 개가 3 분기. 4 분기 요건에 하나 부족 | 보통 |
| **표본 수·최소최대 없음** | 응답은 점추정 `epsEstimate` 하나뿐 | 큼 |
| **통화·주식 단위 표기 없고 종목마다 다름** | `TSM` 은 대만 보통주, `BABA` 는 ADS 기준. 자동 판별 불가 | 가장 큼 |

확보 수준은 **2/4 에서 3/4 로 오른다.** 진전이지만 채점은 열리지 않는다. 그리고 세 번째 문제 때문에 이 값들은 그대로 관측으로 넣을 수 없고 기업별 기준 검증을 우리가 붙여야 한다.

## 2. 접근 범위 — 무엇이 무료이고 무엇이 막혔나

| endpoint | 결과 | 내용 |
|---|---|---|
| `calendar/earnings` | **HTTP 200** | 분기별 `epsEstimate`·`revenueEstimate`. 이번 조사의 대상 |
| `stock/recommendation` | HTTP 200 | 등급 카운트(strongBuy/buy/hold/sell/strongSell). EPS 아님 |
| `stock/profile2` | HTTP 200 | 통화·거래소·발행주식수. 3.3 절에서 기준 판정에 사용 |
| `stock/eps-estimate` | **HTTP 403** | `{"error":"You don't have access to this resource."}` |
| `stock/revenue-estimate` | **HTTP 403** | 동일 |
| `stock/price-target` | **HTTP 403** | 동일 |

**전용 컨센서스 endpoint 는 전부 유료다.** 표본 수와 최소·최대를 주는 것은 `stock/eps-estimate` 쪽이며 무료 등급에서 닫혀 있다. 무료로 열린 분기 EPS 경로는 실적 캘린더 하나뿐이다.

무인증 호출은 HTTP 401 `{"error":"Please use an API key."}`, 가짜 토큰은 401 `{"error":"Invalid API key."}` 다. 데모 경로는 없다.

## 3. 검증 결과

### 3.1 응답 구조 — 필드 9 개가 전부

`GET https://finnhub.io/api/v1/calendar/earnings?from=…&to=…&symbol=…&token=…`

```
date, symbol, year, quarter, epsEstimate, epsActual,
revenueEstimate, revenueActual, hour
```

**표본 수 필드가 없다. 최소·최대 필드도 없다.** `epsEstimate` 는 점추정 하나다.

Valley 화면이 주던 것과 비교하면 절반이 빠진다.

| Valley | Finnhub 무료 |
|---|---|
| 평균 2.47 | `epsEstimate` ✅ |
| 최소·최대 | ❌ 없음 |
| 표본 수 44 | ❌ 없음 |
| 회계분기 구분 | `year`·`quarter` ✅ |

공통 방법 문서는 "최소·최대·표본 수 미제공만으로 확보된 EPS 평균 자체를 폐기하지 않는다. 필수 채점 입력의 결측과 보조 정보의 결측을 분리한다" 고 정한다. 이 규정에 따르면 **평균은 살리고 보조통계는 결측으로 기록**하면 된다. 다만 그렇게 저장하더라도 3.3 의 기준 문제는 별개로 남는다.

### 3.2 미래 분기 수 — 11 개 종목 실측

조회 창을 2026-09-01 ~ 2029-12-31 로 넓게 잡아도 결과는 같다. 캘린더는 **일정이 잡힌 발표 건만** 돌려주므로 창을 넓힌다고 늘지 않는다.

| 종목 | 미래 분기 | 분기 라벨과 `epsEstimate` |
|---|---|---|
| META | 3 | FY2026Q3 6.6602 · FY2026Q4 8.4023 · FY2027Q1 7.8597 |
| NVDA | 3 | FY2027Q3 2.4659 · FY2027Q4 2.7718 · FY2028Q1 3.0781 |
| GOOGL | 3 | FY2026Q3 3.1057 · FY2026Q4 3.4401 · FY2027Q1 3.4358 |
| MSFT | 3 | FY2027Q1 4.8236 · FY2027Q2 4.9486 · FY2027Q3 4.9933 |
| AMZN | 3 | FY2026Q3 1.9928 · FY2026Q4 2.4901 · FY2027Q1 2.43 |
| AAPL | 3 | FY2026Q4 2.0202 · FY2027Q1 2.9585 · FY2027Q2 2.2512 |
| **ORCL** | **4** | FY2027Q1 1.7766 · FY2027Q2 1.9334 · FY2027Q3 2.0994 · FY2027Q4 2.4148 |
| PLTR | 3 | FY2026Q3 0.4277 · FY2026Q4 0.477 · FY2027Q1 0.4962 |
| TSLA | 3 | FY2026Q3 0.4451 · FY2026Q4 0.4755 · FY2027Q1 0.4499 |
| TSM | 3 | FY2026Q3 28.9619 · FY2026Q4 31.7014 · FY2027Q1 32.2501 |
| BABA | 3 | FY2027Q2 11.1893 · FY2027Q3 15.363 · FY2027Q4 11.7374 |

**회계연도 라벨이 기업별로 그대로 온다.** NVDA 는 FY2027Q3 부터, MSFT 는 FY2027Q1 부터, BABA 는 FY2027Q2 부터다. 3·6·9·12 월로 획일화돼 있지 않다. 이 점은 우리 요건에 부합한다.

**SpaceX+xAI 는 조회 대상에서 제외했다.** 공개 티커가 없어 이 endpoint 로 접근할 수 없다.

#### ORCL 의 4/4 는 오늘 하루짜리다

ORCL 만 4 분기가 나온다. 그런데 첫 행이 **2026-09-10, 즉 내일 발표**다. 발표되는 순간 `epsActual` 이 채워지면서 미래 분기는 3 개로 줄어든다.

즉 "오늘 ORCL 은 4/4" 라는 관측은 **하루 뒤 무효가 된다.** 이런 값을 근거로 채점 적격을 판정하면 다음 실행에서 재현되지 않는다. 재현 가능성이 없는 창은 채점 근거로 쓰지 않는다.

#### 3 분기를 4 분기로 늘려 쓸 수 없는 이유

세 경로 모두 막혀 있다.

1. **3 분기 합을 NTM 으로 쓰기.** EPS 가 약 25% 작아져 PER 이 약 33% 커진다. 구간 경계가 20·29·42·62·90 이므로 한두 구간을 통째로 건너뛴다. 점수가 바뀌는 크기다.
2. **×4/3 으로 스케일.** 구조적으로 `annual_weighted_proxy` 와 같은 근사이며 C-13 미결 사항이다. 게다가 분기는 균등하지 않다. 실측 데이터가 보여준다 — AAPL 은 FY2027Q1(연말 분기) 2.9585 가 FY2026Q4 2.0202 의 **1.46 배**이고, META 는 FY2026Q4 8.4023 이 FY2026Q3 6.6602 의 1.26 배다. 계절성이 큰 기업일수록 크게 틀린다.
3. **다른 공급사에서 한 분기 빌려오기.** 공통 방법 문서가 명시적으로 금지한다 — "서로 다른 공급사의 일부 분기를 이어 붙여 검증된 NTM 으로 만들지 않는다".

### 3.3 통화와 주식 단위 — 가장 큰 문제

**응답에 통화 필드도 주식 단위 필드도 없다.** 그리고 실측해 보니 기준이 종목마다 다르다.

`stock/profile2` 로 대조해 판정했다.

| 종목 | profile2 `ticker` | `currency` | `shareOutstanding`(백만) |
|---|---|---|---|
| AAPL | AAPL | USD | 14,687.36 |
| **TSM** | **2330.TW** | **TWD** | 25,932.37 |
| BABA | BABA | CNY | 19,063.63 |

#### TSM — 미국 ADR 티커가 대만 보통주로 해석된다

`symbol=TSM` 을 넣었는데 profile2 가 돌려주는 티커는 **`2330.TW`**, 거래소는 대만증권거래소다. 즉 Finnhub 은 미국 ADR 심볼을 조용히 **대만 상장 보통주**로 바꿔 해석한다.

그래서 값이 이렇게 나온다.

```
revenueEstimate FY2026Q3 = 1,479,386,868,558   → TWD 약 1.48 조. 분기 매출로 타당
epsEstimate     FY2026Q3 = 28.9619

보통주 기준 검산: 28.9619 × 25,932.37M주 = TWD 약 7,510 억 순이익
                 7,510 억 / 1.48 조 매출 = 순이익률 50.8%  → TSMC 수준으로 타당
ADR 기준 가정 시: 28.9619 × (25,932.37M / 5) = TWD 약 1,502 억 순이익
                 1,502 억 / 1.48 조 = 10.2%  → TSMC 순이익률과 맞지 않음
```

**결론: TSM 의 `epsEstimate` 는 TWD, 보통주 1 주 기준이다.**

이는 FMP 와 다르다. `fmp-estimates-02/REPORT.md` 3.1 절에서 FMP 의 TSM `epsAvg` 는 **TWD per ADR** 로 확인했다. 같은 `TSM` 심볼에 대해 **두 공급사가 같은 이름의 EPS 를 5 배 차이 나는 단위로 준다.** 이어 붙이기가 왜 금지되는지를 보여주는 구체적 사례다.

우리 F6 은 주가 ÷ EPS 를 같은 통화·같은 주식 기준으로 요구한다(`calc_f6._basis_alignment`). TSM ADR 주가는 USD 다. 이 EPS 를 그대로 나누면 통화와 주식 단위가 이중으로 어긋난다.

#### BABA — 같은 공급사 안에서 기준이 어긋난다

BABA 는 티커가 유지되고 거래소도 NYSE 인데 `currency` 는 CNY 다. 문제는 `shareOutstanding` 과 `epsActual` 의 기준이 서로 다르다는 것이다.

실제 발표된 분기(FY2027Q1, 2026-08-20 발표)로 검산했다.

```
revenueActual = 268,953,000,000  → CNY 약 2,690 억. 분기 매출로 타당
epsActual     = 8.52
shareOutstanding = 19,063.63M  (보통주)

보통주 기준 가정: 8.52 × 19,063.63M주 = CNY 약 1,624 억 순이익
                  1,624 억 / 2,690 억 매출 = 순이익률 60.4%  → 불가능
ADS 기준 가정:    8.52 × (19,063.63M / 8) = CNY 약 203 억 순이익
                  203 억 / 2,690 억 = 7.5%  → 타당
```

**결론: BABA 의 EPS 는 CNY, ADS 1 주 기준이다. 반면 같은 API 의 `shareOutstanding` 은 보통주 수다.**

즉 `epsEstimate × shareOutstanding` 을 하면 순이익이 8 배 부풀려진다. **한 공급사 안에서, 한 종목에 대해, 두 필드의 주식 기준이 다르다.** API 만 보고는 알 수 없고 순이익률 검산으로만 드러난다.

#### AAPL 대조군

```
epsEstimate FY2026Q4 = 2.0202,  shareOutstanding = 14,687.36M
2.0202 × 14,687.36M = USD 296.7 억 순이익
29.67B / 115.06B 매출 = 25.8%  → Apple 수준으로 타당
```

미국 기업은 일관된다. **문제는 ADR/ADS 종목에 한정되며, 정확히 우리가 TSMC·Alibaba 에서 다루기 어려웠던 그 지점이다.**

## 4. 우리 규칙에 비춘 판정

| 요건 | 충족 여부 |
|---|---|
| 미발표 4 개 연속 분기 | ❌ 10/11 종목이 3 개 |
| `YYYYQn` 식별 가능한 분기 라벨 | ✅ `year`·`quarter` 제공 |
| 회계연도 말 기업별 보존 | ✅ 획일화 없음 |
| 통화 명시 | ❌ 응답에 없음. profile2 로 별도 조회 필요 |
| 주식 기준(보통주/ADR/ADS) 명시 | ❌ 없고 종목마다 다름. 검산으로만 판정 |
| 표본 수 | ❌ 없음 |
| 최소·최대 | ❌ 없음 |
| 추정 시점 | ❌ 없음. `date` 는 발표 예정일이지 추정 갱신 시각이 아니다 |

**채점 입력으로 자동 승격할 수 없다.** 통화·주식 기준을 우리가 기업별로 붙이고 검산으로 확인해야만 관측이 된다.

## 5. 권고

1. **점수·정책은 바꾸지 않는다.** 이번 조사로 확보 수준이 2/4 → 3/4 로 오르지만 4 분기 요건 미충족이라 12 개사 채점 상태는 그대로다.
2. **확보한 3 분기는 보존한다.** 폐기하지 않는다. 공통 방법 문서대로 평균은 관측 후보로 남기고 표본 수·최소최대는 **결측**으로 기록한다. 한 분기만 더 확보되면 살아나는 자산이다.
3. **기준 검증 절차를 관측 등록의 전제 조건으로 둔다.** ADR/ADS 종목은 `순이익률 = epsEstimate × 주식수 ÷ revenueEstimate` 검산으로 주식 기준을 판정하고 그 근거를 `basis` 에 남긴다. TSM 은 TWD·보통주, BABA 는 CNY·ADS 로 이번에 판정했다.
4. **ORCL 의 4/4 는 채택하지 않는다.** 내일 발표로 소멸하는 창이라 재현되지 않는다.
5. **공급사 간 이어 붙이기 금지를 재확인한다.** FMP 와 Finnhub 이 같은 TSM 에 대해 5 배 다른 단위의 EPS 를 준다는 것이 실측으로 확인됐다.
6. **다음 후보.** 무료 등급에서 4 분기와 표본 수를 함께 주는 원천은 아직 못 찾았다. Finnhub 유료 `stock/eps-estimate` 가 표본 수를 주는지, 4 분기를 주는지는 등급을 올려야 확인된다. FMP 유료 분기와 함께 비용 대비 효용을 같이 검토하는 편이 낫다.

## 6. 재현 방법

키는 환경변수로만 다룬다. 보고서·메시지·git 에 남기지 않는다.

```bash
export FINNHUB_KEY='...'   # https://finnhub.io/register 무료 발급

# 3.1·3.2 — 분기 EPS 추정치와 미래 분기 수 (창을 넓혀도 3개)
curl -s "https://finnhub.io/api/v1/calendar/earnings?from=2026-09-01&to=2029-12-31&symbol=AAPL&token=$FINNHUB_KEY" -o aapl.json
python -c "import json;d=json.load(open('aapl.json'))['earningsCalendar'];print(sorted(d[0]));[print(r['date'],r['year'],r['quarter'],r['epsEstimate']) for r in sorted(d,key=lambda x:x['date'])]"

# 2 — 전용 컨센서스 endpoint 는 403
curl -s "https://finnhub.io/api/v1/stock/eps-estimate?symbol=AAPL&freq=quarterly&token=$FINNHUB_KEY"
#   → {"error":"You don't have access to this resource."}

# 3.3 — TSM 이 대만 보통주로 해석되는 것 확인
curl -s "https://finnhub.io/api/v1/stock/profile2?symbol=TSM&token=$FINNHUB_KEY" -o tsm.json
python -c "import json;d=json.load(open('tsm.json'));print(d['ticker'],d['currency'],d['shareOutstanding'])"
#   → 2330.TW TWD 25932.37

# 3.3 — BABA 주식 기준 검산 (실제 발표 분기 사용)
curl -s "https://finnhub.io/api/v1/calendar/earnings?from=2024-01-01&to=2027-12-31&symbol=BABA&token=$FINNHUB_KEY" -o baba.json
python -c "
import json
r=[x for x in json.load(open('baba.json'))['earningsCalendar'] if x['epsActual']][0]
sh=19063.63e6
print('보통주 기준 순이익률', r['epsActual']*sh/r['revenueActual'])
print('ADS 기준 순이익률', r['epsActual']*(sh/8)/r['revenueActual'])"
#   → 0.604 (불가능) / 0.075 (타당) → ADS 기준
```

## 7. 미확인으로 남긴 것

1. **유료 등급 `stock/eps-estimate` 의 응답.** 표본 수·최소최대·분기 수를 주는지. 403 이라 확인 불가.
2. **4 번째 분기가 시간이 지나면 채워지는지.** 캘린더는 일정이 확정된 발표만 준다. 다음 분기 일정이 공시되면 4 개가 될 가능성이 있으나 시점을 특정할 수 없다. 이번 조사 시점 기준으로는 3 개다.
3. **BABA 의 `marketCapitalization` 단위.** 277,916 은 CNY 로 보기엔 작고 USD 백만으로 보면 약 2,779 억 달러로 타당하다. `currency` 가 CNY 인데 시총만 USD 일 가능성이 있으나 이번 판정에 쓰지 않았으므로 확인하지 않았다.
4. **나머지 8 개 종목의 주식 기준.** 미국 상장 보통주라 AAPL 대조군과 같을 것으로 보이나 종목별 검산은 하지 않았다. ADR/ADS 인 TSM·BABA 만 검증했다.
5. **SpaceX+xAI.** 공개 티커가 없어 이 endpoint 로 조회할 수 없다.
