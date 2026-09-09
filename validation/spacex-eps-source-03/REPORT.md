# SPACEX-EPS-SOURCE-03 — SPCX 분기 EPS 컨센서스 신규 원천 조사

작성일 2026-09-09. 담당 worker(HANSOLJJ/worker). 요청 메시지 `msg_11803f6a94d1`.

Finnhub SPCX 0 건(`../spacex-f6-recheck-01/REPORT.md`)과 무료 FMP 분기 차단(`../fmp-estimates-02/REPORT.md`)을 전제로 독립 원천을 조사했다. **코드·점수·승인은 변경하지 않았다.** 보고서 한 건만 추가한다.

API 키는 환경변수와 저장소 밖 스크래치 파일로만 다뤘고 이 보고서·커밋·Orca 메시지 어디에도 남기지 않았다.

## 1. 결론

**미발표 4 개 분기를 모두 주는 원천을 찾았다. Nasdaq 자체 API 다.**

```
GET https://api.nasdaq.com/api/analyst/SPCX/earnings-forecast
```

무료·무키로 접근되며 회계분기별 **컨센서스·최고·최저·추정치 수**를 준다. 우리가 필요한 4 개 분기(2026 Sep·Dec, 2027 Mar·Jun)가 전부 들어 있다.

동시에 **앞선 보고서의 판정 하나를 정정한다.** `spacex-f6-recheck-01` 9.5 절에서 "Finnhub 이 SPCX 를 커버하지 않는다" 고 했는데 **틀렸다.** `calendar/earnings` 에만 없을 뿐 `stock/earnings` 와 `stock/recommendation` 은 SPCX 를 정상 반환한다. 애널리스트 43 명이 등급을 내고 있다(8 절).

다만 **자료가 갖춰졌다고 채점이 열리는 것은 아니다.** GAAP/비GAAP 기준, 추정 시점, 접근 약관 세 가지가 미확인이다(9 절). 이번 작업은 원천 조사이며 **점수를 만들지 않았다.**

## 2. 조사 방법

후보를 공개 규제기관 → 거래소 → 무료 공급사 → 유료 공급사 순으로 실제 호출해 확인했다. 문서만 읽고 판단하지 않았다.

| 후보 | 접근 | 키 |
|---|---|---|
| SEC EDGAR (submissions·XBRL companyconcept) | 공개 | 불요 |
| Nasdaq `api.nasdaq.com` | 공개 | 불요 |
| Yahoo Finance (yfinance) | 공개 | 불요 |
| StockAnalysis | 공개 | 불요 |
| Finnhub | 무료 등급 | 사용 |
| FMP | 무료 등급 | 사용 |

## 3. 회계 캘린더와 필요한 창 — SEC 로 확정

`https://data.sec.gov/submissions/CIK0001181412.json`

| 항목 | 값 |
|---|---|
| CIK | 1181412 |
| 등록명 | SPACE EXPLORATION TECHNOLOGIES CORP |
| 티커·거래소 | SPCX · Nasdaq |
| **`fiscalYearEnd`** | **1231 (역년 회계연도)** |
| 최근 정기보고 | **10-Q, filed 2026-08-04, reportDate 2026-06-30** |
| 최근 8-K | 2026-08-14 (Cursor 인수 완료일과 일치) |

SPCX 는 **역년 회계연도**다. TSMC·MSFT 처럼 어긋난 회계연도가 아니다. 따라서 2026-09-09 기준 **다음 4 개 미발표 회계분기**는 확정적으로 다음과 같다.

| # | 회계분기 | 분기 종료일 | 상태 |
|---|---|---|---|
| 1 | 2026 Q3 | 2026-09-30 | 미종료·미발표 |
| 2 | 2026 Q4 | 2026-12-31 | 미발표 |
| 3 | 2027 Q1 | 2027-03-31 | 미발표 |
| 4 | 2027 Q2 | 2027-06-30 | 미발표 |

Yahoo 가 다음 발표일을 **2026-11-03** 로 준다. 9/30 종료 분기의 발표 시점으로 정합적이다.

## 4. basis 확정 — SEC XBRL 이 권위 있는 근거다

`https://data.sec.gov/api/xbrl/companyconcept/CIK0001181412/us-gaap/EarningsPerShareDiluted.json`

```
units: ["USD/shares"]
  2026-04-01 ~ 2026-06-30  val = -0.09   form=10-Q  fy=2026 fp=Q2
  2026-01-01 ~ 2026-06-30  val = -1.12   form=10-Q
  2025-04-01 ~ 2025-06-30  val = -0.34   form=10-Q  (전년 대비 표시)
  2025-01-01 ~ 2025-06-30  val = -0.53   form=10-Q
```

`EarningsPerShareBasic` 도 동일한 값이다(적자라 희석 효과 없음).

| 기준 | 값 | 근거 |
|---|---|---|
| 통화 | **USD** | SEC XBRL 단위 `USD/shares`, Yahoo `financialCurrency: USD` |
| 주식 단위 | **보통주** | 미국 직상장. ADR/ADS 아님. Yahoo `quoteType: EQUITY`, `fullExchangeName: NasdaqGS` |
| 회계 기준 | **US-GAAP** (실적 한정) | `us-gaap` 택소노미 |

**교차 검증이 두 겹으로 맞는다.** SEC 의 Q2 2026 희석 EPS `-0.09` 는 우리 기준선 `quarter_note` 의 "-$0.09" 와 일치하고, 같은 분기 매출 `$7,814M` 은 기준선의 "$7.8B (+92%)" 와 일치한다(전년 동기 $4,071M 대비 +91.9%). 기준선 값이 독립 원천으로 확인된 셈이다.

## 5. 후보별 결과

| 원천 | 미래 분기 | 표본 수 | 최소·최대 | 통화 표기 | 접근 | 판정 |
|---|---|---|---|---|---|---|
| **Nasdaq** | **5 개 (필요 4 개 전부)** | ✅ `noOfEstimates` | ✅ | ❌ 없음 | 무료·무키 | **유일한 4/4 원천** |
| Yahoo (yfinance) | 2 개 | ✅ `numberOfAnalysts` | ✅ | ✅ `currency: USD` | 무료·무키 | 통계 완비, 분기 부족 |
| Finnhub 무료 | 0 개 | ❌ | ❌ | ❌ | 키 필요 | `calendar` 에 SPCX 없음 |
| FMP 무료 | 0 개 | — | — | — | 키 필요 | **심볼 자체가 유료** |
| SEC EDGAR | 해당 없음 | — | — | ✅ | 무료·무키 | 컨센서스 없음. **창·basis·실적 확정에 필수** |
| StockAnalysis | 페이지 존재 | 미확인 | 미확인 | 미확인 | 무료·무키 | **비GAAP 명시**. 8.3 참조 |

### 5.1 Nasdaq — 4/4 충족

`quarterlyForecast.rows` 5 건이다. 필요한 4 개에 표시했다.

| fiscalEnd | consensusEPSForecast | highEPSForecast | lowEPSForecast | noOfEstimates | 필요 |
|---|---|---|---|---|---|
| Sep 2026 | 0.09 | 0.26 | -0.03 | 11 | ✅ |
| Dec 2026 | 0.29 | 0.62 | 0.00 | 11 | ✅ |
| Mar 2027 | 0.37 | 0.73 | 0.00 | 7 | ✅ |
| Jun 2027 | 0.41 | 0.93 | 0.02 | 7 | ✅ |
| Sep 2027 | 0.40 | 0.90 | -0.01 | 7 | (여분) |

`yearlyForecast` 도 함께 온다(Dec 2026 -0.15, Dec 2027 1.63, Dec 2028 4.16, Dec 2029 5.92).

**분기 라벨이 SEC 회계 캘린더와 정확히 맞는다.** 역년 회계연도이므로 Sep/Dec/Mar/Jun 종료월이 곧 Q3/Q4/Q1/Q2 다. 3 절의 창과 일대일 대응한다.

**표본 수가 분기마다 다르다.** 가까운 두 분기는 11 명, 먼 두 분기는 7 명이다. 우리 스키마에서 표본 수를 분기에 종속시켜 저장해야 한다는 뜻이다.

### 5.2 Yahoo — 통계는 완비되나 2 분기뿐

`yfinance` `Ticker("SPCX").earnings_estimate`

| period | avg | low | high | numberOfAnalysts | currency |
|---|---|---|---|---|---|
| 0q | 0.14582 | -0.11 | 0.28833 | 12 | USD |
| +1q | 0.44758 | -0.14 | 0.80000 | 14 | USD |
| 0y | 0.11869 | -1.52 | 1.00000 | 17 | USD |
| +1y | 1.74665 | -0.68 | 3.19000 | 18 | USD |

`calendar` 의 다음 발표일 2026-11-03 으로 `0q = 2026 Q3`, `+1q = 2026 Q4` 로 확정된다.

**Yahoo 의 구조적 한계는 4 개 기간뿐**이라는 점이다(`0q`, `+1q`, `0y`, `+1y`). 분기는 최대 2 개다. `eps_trend` 도 같은 4 기간만 준다. 늘릴 방법이 없다.

**장점은 통화를 명시한다는 것이다.** Nasdaq 에 없는 `currency: USD` 필드가 있다. 기준 대조용으로 가치가 있다.

### 5.3 Finnhub — 커버는 하되 미래 분기가 없다

`calendar/earnings` 는 여전히 0 건이다. 그러나 다른 두 endpoint 는 SPCX 를 정상 반환한다.

```
GET /stock/earnings?symbol=SPCX
[{"symbol":"SPCX","estimate":-0.2635,"actual":-0.09,"period":"2026-06-30",
  "surprise":0.1735,"surprisePercent":65.8444,"year":2026,"quarter":2}]

GET /stock/recommendation?symbol=SPCX
[{"period":"2026-09-01","strongBuy":13,"buy":21,"hold":7,"sell":1,"strongSell":1}, …]
```

- `stock/earnings` 의 `estimate: -0.2635` 는 **발표 직전 컨센서스**다. 기준선 `quarter_note` 의 "컨센 -0.26" 과 일치하고 `actual: -0.09` 는 SEC 값과 일치한다.
- `stock/recommendation` 은 2026-09-01 기준 **43 명**(13+21+7+1+1)이 등급을 내고 있음을 보여준다.

**즉 애널리스트 커버리지는 충분히 형성돼 있다.** 8 절에서 앞선 판정을 정정한다.

`stock/eps-estimate`(미래 분기 컨센서스)는 무료 등급에서 HTTP 403 이다.

### 5.4 FMP — SPCX 는 심볼 자체가 유료다

무료 키로 SPCX 를 호출하면 `period` 가 아니라 **`symbol`** 이 막힌다.

```
GET /stable/analyst-estimates?symbol=SPCX&period=annual
HTTP 402
Premium Query Parameter: 'Special Endpoint : This value set for 'symbol' is not
available under your current subscription …
```

`price-target-consensus`·`ratings-snapshot` 도 같은 402 다. `grades-summary` 는 빈 배열에 404 다. **AAPL 로는 annual 이 열렸는데 SPCX 는 심볼 단위로 차단된다.** 무료 등급으로 SPCX 를 볼 방법이 없다.

## 6. 참고 산식 — 점수가 아니다

> ⚠️ **아래는 원천 평가용 예시 계산이며 채점값이 아니다.** 관측 등록·`calculate`·`review`·`approve` 를 거치지 않았다. 현행 승인 실행의 F6 는 그대로다.

Nasdaq 4 개 분기 컨센서스 합:

```
0.09 + 0.29 + 0.37 + 0.41 = 1.16 USD
주가 153.47 (Finnhub quote, 2026-09-08 20:00 UTC)
153.47 / 1.16 = 132.3
```

기준선의 승계 관측 `ntm_per 111.0`(주가 140.71 기준, 함의 NTM EPS 1.268)과 같은 자릿수이나 다른 값이다. **둘을 섞거나 어느 하나로 다른 하나를 검증했다고 하지 않는다.** 기준선 값은 `legacy_unverified` 이고 이번 값은 미등록 후보다.

## 7. 공급사 간 불일치 — 채택 전 반드시 인지할 것

같은 종목·같은 시점인데 공급사마다 값이 크게 다르다.

### 7.1 forward PE — 7.4 배 차이

| 원천 | forward PE | 함의 forward EPS |
|---|---|---|
| Yahoo `info.forwardPE` | 96.84 | 1.585 (`forwardEps`) |
| 기준선 StockAnalysis (2026-09-02) | 111.0 | 1.268 |
| Finnhub `stock/metric.forwardPE` | **718.07** | 0.214 |

세 값이 96.8 / 111 / 718 로 흩어진다. **공급사 forward PE 를 NTM 으로 신뢰할 수 없다**는 우리 기존 판정(`period_unknown` · `unverified`)을 실물로 뒷받침한다.

### 7.2 같은 분기 컨센서스 — 최대 54% 차이

| 분기 | Nasdaq | Yahoo | 차이 |
|---|---|---|---|
| 2026 Q3 (Sep) | 0.09 (n=11) | 0.14582 (n=12) | +62% |
| 2026 Q4 (Dec) | 0.29 (n=11) | 0.44758 (n=14) | +54% |

표본 수가 비슷한데 값이 이만큼 다르다. **패널 구성이 다르거나 GAAP/비GAAP 기준이 다르다.** 어느 쪽이든 **공급사를 섞으면 안 된다**는 규정의 근거가 된다. 어느 공급사를 고르냐가 NTM EPS 를 절반 가까이 바꾼다.

### 7.3 발행주식수도 갈린다

| 원천 | shares |
|---|---|
| Finnhub `profile2.shareOutstanding` | 13,159.2 M |
| Yahoo `info.sharesOutstanding` | 7,696.3 M |

1.7 배 차이다. 시가총액이 그만큼 달라진다(153.47 기준 2.02 조 대 1.18 조, 기준선은 1.91 조). SpaceX 가 복수 주식 종류를 두었을 가능성이 있으나 **이번 조사에서 확인하지 않았다.** F6 자체에는 개입하지 않지만 시총·P/S 를 쓸 때 문제가 된다.

## 8. 앞선 보고서 정정

### 8.1 "Finnhub 이 SPCX 를 커버하지 않는다" 는 틀렸다

`../spacex-f6-recheck-01/REPORT.md` 9.5 절에서 나는 이렇게 썼다.

> "**판정: Finnhub 가 SPCX 를 커버하지 않는다.** 시간이 지나도 채워질 것으로 기대하기 어렵다."

**틀렸다.** `stock/earnings` 와 `stock/recommendation` 이 SPCX 를 정상 반환한다(5.3). 애널리스트 43 명이 커버 중이다.

정확한 판정은 이렇다. **Finnhub 은 SPCX 를 커버하되 `calendar/earnings` 에 이 종목의 행이 없다.** 같은 공급사 안에서 endpoint 별로 수록 범위가 다르다. 원인은 확인하지 못했다.

**교훈: 한 endpoint 의 빈 응답을 공급사 전체의 미커버로 일반화하면 안 된다.** 이번 조사에서만 두 번째로 같은 종류의 실수다(첫 번째는 불완전 체크아웃을 근거로 한 부재 판정, `../fincept-consensus-01/REPORT.md` 2.2).

### 8.2 "다른 원천을 찾는 편이 낫다" 는 결과적으로 맞았다

권고 자체는 유효했다. Nasdaq 이라는 더 나은 원천을 찾았다.

### 8.3 StockAnalysis 의 비GAAP 표기

기준선 `ntm_per 111.0` 의 출처는 `StockAnalysis Forward PE (2026-09-02)` 다. 이번에 해당 페이지를 조회하니 본문에 **"EPS and Forward PE are based on non-GAAP adjusted numbers"** 가 명시돼 있다.

즉 기준선의 NTM PER 은 **비GAAP 조정 EPS 기반**일 가능성이 높다. SEC 의 GAAP 실적(-0.09)과 기준이 다르다. 이 역시 `legacy_unverified` 로 남겨야 할 이유다.

## 9. F6 적용 가능성 판정

| 요건 | 상태 |
|---|---|
| 미발표 4 개 연속 분기 | ✅ **4/4** (Nasdaq, 3 절 창과 일치) |
| 분기 라벨 식별 | ✅ 종료월 표기, 역년 회계연도라 `YYYYQn` 환산 명확 |
| 표본 수 | ✅ 분기별 `noOfEstimates` (11·11·7·7) |
| 최소·최대 | ✅ `highEPSForecast`·`lowEPSForecast` |
| 통화 | ⚠️ **응답에 없음.** SEC·Yahoo 교차로 USD 확정 가능하나 원천 자체는 미표기 |
| 주식 단위 | ⚠️ 동일. 미국 직상장이라 위험은 낮으나 원천이 명시하지 않음 |
| **GAAP/비GAAP** | ❌ **미확인.** 헤더가 `Consensus EPS*` 로 별표를 달았으나 각주 본문이 API 응답에 없다 |
| **추정 시점** | ❌ **미확인.** `asOf` 가 `null` 이다 |
| **접근 약관·한도** | ❌ **미확인.** 문서화되지 않은 endpoint 이며 브라우저 UA 를 요구한다 |

**판정: 자료는 4/4 를 충족하나 채택 조건은 미충족이다.** 위 세 개의 ❌ 가 해소되기 전에는 관측으로 등록하지 않는다.

특히 GAAP/비GAAP 이 중요하다. 우리 F6 은 주가 ÷ EPS 이고 SEC 실적은 GAAP 다. 컨센서스가 비GAAP 조정치라면 **실적과 추정이 다른 잣대**가 되어 시계열이 어긋난다. 8.3 에서 StockAnalysis 가 비GAAP 을 명시한 것을 보면 이 업계에서 컨센서스는 비GAAP 이 기본일 가능성이 높다. 확인이 필요하다.

## 10. 다른 11 개사로의 확장 리드

SPCX 조사 중 확인한 부수 사실이다. **이번 과제 범위 밖이므로 리드로만 남긴다.**

Nasdaq 은 같은 endpoint 로 다른 종목도 5 개 분기를 준다.

| 종목 | Sep 2026 | Dec 2026 | Mar 2027 | Jun 2027 |
|---|---|---|---|---|
| AAPL | 1.98 (n=7) | 2.91 (n=7) | 2.16 (n=7) | 2.09 (n=7) |
| TSM | 4.45 (n=6) | 4.68 (n=5) | 4.64 (n=4) | 5.10 (n=4) |
| BABA | 1.42 (n=3) | 1.89 (n=3) | 1.81 (n=3) | 2.45 (n=2) |

**TSM 값이 특히 주목할 만하다.** 4.45 는 USD 로 환산한 ADR 당 값으로 보인다. Finnhub 은 같은 TSM 을 TWD 보통주 기준 28.96 으로, FMP 는 TWD ADR 기준으로 준다(`../finnhub-earnings-03/REPORT.md` 3.3). **Nasdaq 은 미국 상장 증권의 통화·단위로 정규화하는 것으로 보이며**, 그렇다면 우리가 TSMC·Alibaba 에서 겪던 기준 불일치가 완화된다.

다만 이는 **세 종목만 본 추정이며 확정이 아니다.** 12 개사 전수 확인과 통화·단위 명시적 검증이 필요하다. 별도 과제로 제안한다.

## 11. 미확인 사항

부재나 확정으로 단정하지 않고 남긴다.

1. **Nasdaq 컨센서스의 GAAP/비GAAP 기준.** 헤더 별표의 각주가 API 응답에 없다. 웹 페이지나 약관에서 확인해야 한다.
2. **Nasdaq 의 추정 갱신 시각.** `asOf` 가 null 이라 우리 공통 방법이 요구하는 "공급사의 갱신/추정 기준 시각" 을 채울 수 없다. 미표시이므로 미확인으로 기록해야 한다.
3. **Nasdaq API 의 이용 약관·요청 한도.** 문서화된 공개 API 가 아니며 브라우저 UA 를 요구한다. 반복 자동 수집의 허용 여부가 불명확하다. **약관 확인 없이 대량 수집하지 않는다.**
4. **합병 전 기간의 소급 연결 여부.** 10-Q 가 2025 년 비교치를 제시하지만(Q2 2025 EPS -0.34, 매출 $4,071M) xAI 를 소급 연결했는지는 **기본 표시 주석(basis of presentation)을 읽어야** 알 수 있다. 이번에 읽지 않았다. 이는 `../spacex-f6-recheck-01/REPORT.md` 9.3 의 TTM 창 문제를 해소할 열쇠이며 자료는 공개돼 있다.
5. **발행주식수 불일치의 원인.** Finnhub 13.16B 대 Yahoo 7.70B(7.3). 복수 주식 종류 가능성을 확인하지 않았다.
6. **Nasdaq 의 12 개사 전수 커버리지와 기준.** 3 종목만 확인했다(10 절).
7. **StockAnalysis 의 분기 컨센서스 제공 여부.** 페이지는 열리나 분기 표를 파싱하지 않았다. 비GAAP 명시만 확인했다.
8. **유료 공급사.** Finnhub `stock/eps-estimate`(403)와 FMP 유료 등급은 결제 없이 확인할 수 없다. Nasdaq 무료 경로가 4/4 를 주므로 우선순위가 낮아졌다.

## 12. 재현 방법

```bash
# 3 — 회계 캘린더와 창 (키 불요, User-Agent 필수)
UA="your-app research contact:you@example.com"
curl -s -A "$UA" "https://data.sec.gov/submissions/CIK0001181412.json" -o sub.json
python -c "import json;d=json.load(open('sub.json'));print(d['fiscalYearEnd'],d['tickers'],d['exchanges'])"
#   → 1231 ['SPCX'] ['Nasdaq']

# 4 — basis (USD/shares) 와 실적 대조
curl -s -A "$UA" "https://data.sec.gov/api/xbrl/companyconcept/CIK0001181412/us-gaap/EarningsPerShareDiluted.json" -o eps.json
python -c "
import json;d=json.load(open('eps.json'))
print(list(d['units']))
[print(r['start'],r['end'],r['val'],r['form']) for r in d['units']['USD/shares']]"
#   → USD/shares · 2026-04-01~2026-06-30 -0.09 10-Q

# 5.1 — Nasdaq 4/4 (키 불요, 브라우저 UA 필요)
curl -s -A "Mozilla/5.0" "https://api.nasdaq.com/api/analyst/SPCX/earnings-forecast" -o nq.json
python -c "
import json;d=json.load(open('nq.json'))
[print(r['fiscalEnd'],r['consensusEPSForecast'],r['lowEPSForecast'],r['highEPSForecast'],r['noOfEstimates'])
 for r in d['data']['quarterlyForecast']['rows']]"

# 5.2 — Yahoo 2 분기 + 통화
python -c "
import yfinance as yf
t=yf.Ticker('SPCX')
print(t.earnings_estimate.to_string()); print(t.calendar)"

# 5.3 — Finnhub 은 커버하되 calendar 에만 없다
curl -s "https://finnhub.io/api/v1/stock/earnings?symbol=SPCX&token=$FINNHUB_KEY"
curl -s "https://finnhub.io/api/v1/stock/recommendation?symbol=SPCX&token=$FINNHUB_KEY"
curl -s "https://finnhub.io/api/v1/calendar/earnings?from=2024-01-01&to=2029-12-31&symbol=SPCX&token=$FINNHUB_KEY"
#   → 앞의 둘은 200, 마지막은 {"earningsCalendar":[]}

# 5.4 — FMP 는 심볼 자체가 유료
curl -s "https://financialmodelingprep.com/stable/analyst-estimates?symbol=SPCX&period=annual&apikey=$FMP_API_KEY"
#   → HTTP 402, "This value set for 'symbol' is not available…"
```

## 13. 권고

1. **점수·정책은 바꾸지 않는다.** 이번 조사로 자료 후보가 생겼을 뿐이며 현행 승인 실행의 F6 는 그대로다.
2. **Nasdaq 을 1 순위 후보로 두되 11 절의 1~3 을 먼저 해소한다.** GAAP 기준, 추정 시점, 이용 약관이다. 특히 약관 확인 전 반복 수집을 하지 않는다.
3. **공급사를 섞지 않는다.** 7.2 에서 같은 분기가 54% 까지 벌어졌다. Nasdaq 으로 4 분기를 채우기로 했다면 4 분기 모두 Nasdaq 이어야 한다.
4. **통화·주식 단위는 우리가 붙인다.** Nasdaq 응답에 표기가 없으므로 SEC(`USD/shares`)와 Yahoo(`financialCurrency`)를 교차 근거로 `basis` 를 채운다.
5. **10-Q 의 기본 표시 주석을 읽어 소급 연결 여부를 확정한다.** 공개 자료이고 `spacex-f6-recheck-01` 9.3 의 미해결 항목을 닫을 수 있다.
6. **Nasdaq 의 12 개사 확장 조사를 별도 과제로 제안한다.** 성립한다면 4 분기 요건 자체가 12 개사 전부에서 풀릴 수 있다(10 절).
