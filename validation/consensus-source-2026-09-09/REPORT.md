# NTM-SOURCE-04 — 담당 10개사 전망치 원천 조사

- 지시 원문: `msg_f849c3f1fb00` (run `run_1243c2a83479`)
- 적용 방법: `설계진행/validation/consensus-research-method.md`
- 기준일: 2026-09-09 (조회 시각은 `evidence.json` 의 각 `fetched_at_utc` 참조)
- 담당: Meta, NVIDIA, Alphabet, Microsoft, Amazon, Apple, Oracle, Palantir, Tesla, SpaceX
- 산출물 경로: `NTM-전망치조사/validation/consensus-source-2026-09-09/`
- 대상 worktree(`worker`, `scarpper`, `C-13`, `설계진행`)는 읽기 전용으로만 다뤘고 이 폴더에만 기록했다.

## 0. 결론

**담당 10개사 전부 다음 4개 미발표 회계분기 EPS 컨센서스를 4/4 확보했다.** 평균·최소·최대·전망치 수를 한 원천(Nasdaq 공개 API)에서 분기를 섞지 않고 통째로 얻었다. 2026-09-08 조사에서 10개사 전부 2/4 였던 결측이 해소됐다.

동시에 **10개사 전부 채점 적격성은 여전히 미검증(unverified)이다.** 확보와 적격성은 별개이며, 아래 미검증 사유는 자료 부재가 아니라 기준 확인이 남았다는 뜻이다.

핵심 사실 네 가지다.

1. **새 원천을 찾았다.** `https://api.nasdaq.com/api/analyst/{TICKER}/earnings-forecast` 는 로그인·구독 없이 분기별 **평균·최대·최소·전망치 수·최근 4주 상하향 수정 건수**를 5개 분기까지 준다. 2026-09-08 조사가 "Nasdaq 정적 수집 실패"로 남긴 경로는 HTML 스크래핑이었고, JSON API 경로는 열려 있었다.
2. **미발표 분기 경계를 공급사 표기로 확정했다.** `https://api.nasdaq.com/api/quote/{TICKER}/eps` 가 분기를 `PreviousQuarter`(발표)와 `UpcomingQuarter`(미발표)로 명시 구분하며, 10개사 모두 `UpcomingQuarter` 가 정확히 4개다. StockAnalysis 의 회계분기 종료일·마지막 발표 분기 인덱스와 대조해 일치를 확인했다.
3. **중간값은 어느 공개 원천에서도 얻지 못했다.** Valley 화면에는 있으나 로그인 없이는 표를 얻지 못했다. 중간값은 보조 정보 결측으로 기록했고, 이 때문에 확보한 평균을 폐기하지 않았다.
4. **공급사 간 회계 기준이 실제로 다르다는 증거를 잡았다.** 같은 기업·같은 **확정 발표 분기**의 실적 EPS 가 원천마다 다르다(Amazon 1.88 vs 5.75, Tesla 0.04 vs 0.33). 기간은 일치하므로 기간 오정렬이 아니라 조정(adjusted) 정의 차이다. 따라서 원천 간 EPS 대체나 분기 이어붙이기는 이 10개사에서 실제로 위험하며, 방법 문서의 금지 규칙이 관측으로 뒷받침된다.

Valley 참고 사례(NVIDIA)와의 대조는 §4 에 있다. Valley 표시 평균 2.47/2.74/3.20/3.67(표본 44/42/40/40) 과 이번 Nasdaq 값 2.47/2.72/3.17/3.60(표본 12/11/10/10) 은 서로 다른 공급사 값이며 나란히 보존한다.

## 1. 미발표 분기 창 확정 방법

기준시각의 직전 발표 실적을 확인해 다음 4개 미발표 회계분기를 정했다. 모든 기업을 3·6·9·12월로 맞추지 않았다.

- NVIDIA 는 1월 결산이라 창이 Oct 2026 / Jan 2027 / Apr 2027 / Jul 2027 이다.
- Oracle 은 5월 결산이라 창이 Aug 2026 / Nov 2026 / Feb 2027 / May 2027 이다. **Aug 2026 분기는 이미 종료됐지만 실적 미발표라 창에 포함된다.** 공급사도 이 분기를 `UpcomingQuarter` 로 표시한다.
- 나머지 8개사는 12월 결산 계열로 Sep 2026 / Dec 2026 / Mar 2027 / Jun 2027 이다. Microsoft(6월 결산)·Apple(9월 결산)도 이번 창은 같은 월에 걸린다.

SpaceX 는 기준시점에 **NASDAQ-GS 상장·거래 중**임을 공급사 종목 정보로 확인했다(`Space Exploration Technologies Corp. Class A Common Stock`, SPCX, 2026-09-08 종가 $153.47). 2026-09-08 조사가 남긴 `registry_defect`(레지스트리 ticker=null) 는 레지스트리 쪽 결함이고, 티커 자체는 유효하다. 다만 사내 식별자 `spacex-xai` 가 SpaceX 와 xAI 를 한 항목으로 묶고 있는데, 공급사 종목은 SpaceX 단일 법인으로 표기된다. 이 불일치는 정책 사안이라 여기서 결정하지 않고 기록만 한다.

## 2. 확보 결과

표 전체는 `tables.md` 에 있다. 아래는 요약이다.

### 2.1 담당 10개사 4분기 EPS 컨센서스 (Nasdaq API 단일 원천, USD 추정·공급사 미표기)

| 기업 | 티커 | 4개 미발표 분기 | 평균 EPS | 전망치 수 | 평균 합 |
|---|---|---|---|---|---|
| Meta | META | Sep26/Dec26/Mar27/Jun27 | 6.33 / 8.01 / 7.76 / 8.08 | 13/12/6/6 | 30.18 |
| NVIDIA | NVDA | Oct26/Jan27/Apr27/Jul27 | 2.47 / 2.72 / 3.17 / 3.60 | 12/11/10/10 | 11.96 |
| Alphabet | GOOGL | Sep26/Dec26/Mar27/Jun27 | 2.93 / 3.21 / 3.30 / 3.47 | 14/12/7/7 | 12.91 |
| Microsoft | MSFT | Sep26/Dec26/Mar27/Jun27 | 4.67 / 4.81 / 4.84 / 5.13 | 13/13/12/12 | 19.45 |
| Amazon | AMZN | Sep26/Dec26/Mar27/Jun27 | 2.03 / 2.56 / 2.37 / 2.64 | 14/12/8/8 | 9.60 |
| Apple | AAPL | Sep26/Dec26/Mar27/Jun27 | 1.98 / 2.91 / 2.16 / 2.09 | 7/7/7/7 | 9.14 |
| Oracle | ORCL | Aug26/Nov26/Feb27/May27 | 1.40 / 1.53 / 1.66 / 1.92 | 10/11/10/10 | 6.51 |
| Palantir | PLTR | Sep26/Dec26/Mar27/Jun27 | 0.33 / 0.37 / 0.36 / 0.42 | 10/9/7/7 | 1.48 |
| Tesla | TSLA | Sep26/Dec26/Mar27/Jun27 | 0.26 / 0.30 / 0.21 / 0.30 | 11/11/6/6 | 1.07 |
| SpaceX | SPCX | Sep26/Dec26/Mar27/Jun27 | 0.09 / 0.29 / 0.37 / 0.41 | 11/11/7/7 | 1.16 |

최소·최대는 표 A 에 분기별로 있다. **최소·최대는 관측된 전망 범위이며 확률 구간이나 실적 보장 범위가 아니다.** 평균 합은 같은 원천 4분기 평균의 단순 합이고, 전망치 수로 재가중하지 않았다. 10개사 모두 합이 양수라 합계 0 이하로 인한 채점 보류 사유는 이번에 발생하지 않았다. SpaceX 의 Sep 2026 최소값 -0.03 처럼 음수 관측도 유효 관측으로 보존했다.

### 2.2 확보 수준 요약

| 항목 | 결과 |
|---|---|
| 4개 미발표 분기 EPS 평균 | **10개사 전부 4/4** (전 분기 단일 원천 Nasdaq) |
| 최소·최대·전망치 수 | 10개사 전부 4/4 |
| 중간값 | **10개사 전부 0/4** (공개 원천 미제공, 보조 정보 결측) |
| 회계분기 종료일 대조 | 10개사 전부 4/4 (StockAnalysis 종료일과 월 일치) |
| 2원천이 같은 분기를 커버 | 10개사 전부 2/4 (3·4분기는 유료·로그인 구간) |
| 2원천 값이 5% 이내 합치 | Meta 1/4, Amazon 1/4, NVIDIA·Alphabet·Microsoft·Apple 2/4, **Oracle·Palantir·Tesla·SpaceX 0/4** |
| 채점 자동 사용 | 10개사 전부 불가(미검증) |

## 3. 원천별 조사 결과

| 원천 | 접근 조건 | 제공 통계 | 확보 분기 | 성공/실패 |
|---|---|---|---|---|
| `api.nasdaq.com/api/analyst/{T}/earnings-forecast` | 공개 JSON GET | 평균·최소·최대·전망치 수·4주 수정 건수 | **4/4 (10개사)** | 성공 |
| `api.nasdaq.com/api/quote/{T}/eps` | 공개 JSON GET | 발표/미발표 구분, 평균, 직전 분기 실적 | 4/4 경계 확정 | 성공 |
| StockAnalysis `__data.json` | 공개, 3분기째부터 `[PRO]` | 평균(조정·GAAP 열), 전망치 수, **회계분기 종료일**, 마지막 발표 분기 인덱스 | 2/4 | 부분 성공 |
| TradingView 스캐너 | 공개 JSON GET | 다음 1분기 평균, 직전 분기 실적·컨센서스, 다음 발표일 | 1/4 | 부분 성공 |
| Zacks 종목 페이지 | 공개 | 평균(현재·다음 분기), 30/60/90일 전 추이 | 2/4 | 부분 성공 |
| Yahoo Finance | 공개, 무료 2분기 | 평균 | 2/4 (재수집 안 함) | 기존 기록 재사용 |
| Valley `valley.town` | **로그인 필요** | 최소·평균·중간값·최대·전망치 수 | 0/4 | 미로그인 접근으로 표 미확보 |
| Investing.com, GuruFocus, Fintel, SimplyWallSt, AlphaSpread, StockTwits | 공개 페이지이나 봇 차단(403) | 미확인 | 0/4 | 보류 |
| FMP, MarketWatch, WSJ, Yahoo `quoteSummary` | 키·구독·인증 필요(401) | 미확인 | 0/4 | 결제·가입 없이 보류 |
| SeekingAlpha, TipRanks API | 404 | 미확인 | 0/4 | 보류 |

차단·인증 실패 경로는 **미조사**로 남긴다. 자료가 없다는 뜻도, 유료면 가능하다는 뜻도 아니다. 결제·가입은 하지 않았다.

### 3.1 새 원천의 재현 방법

```
GET https://api.nasdaq.com/api/analyst/NVDA/earnings-forecast
Referer: https://www.nasdaq.com/market-activity/stocks/nvda/earnings
User-Agent: (일반 브라우저 UA)
```

응답 `data.quarterlyForecast.rows[]` 각 항목이 `fiscalEnd`, `consensusEPSForecast`, `highEPSForecast`, `lowEPSForecast`, `noOfEstimates`, `up`, `down` 이다. `data.yearlyForecast` 는 연간 표다. 수집기는 `collect_consensus.py`, 재현 스크립트 전체가 이 폴더에 있다.

**공급사 식별**: NVIDIA 로 대조한 결과 Nasdaq 분기 평균(2.47 / 2.72)이 Zacks 종목 페이지의 Zacks Consensus Estimate(2.47 / 2.72)와 같다. Nasdaq 분기 추정치는 Zacks 계열로 보이나, 공급사 표기가 페이지에 없어 단정하지 않는다.

## 4. Valley 참고 사례와의 대조 (NVIDIA)

| 항목 | Valley (지시 메시지 인용) | Nasdaq (이번 조사) | StockAnalysis | Yahoo(09-08) | TradingView |
|---|---|---|---|---|---|
| FY2027Q3 (Oct 2026) | 2.47 | 2.47 | 2.46983 | 2.47 | 2.469278 |
| FY2027Q4 (Jan 2027) | 2.74 | 2.72 | 2.74567 | 2.75 | 미제공 |
| FY2028Q1 (Apr 2027) | 3.20 | 3.17 | `[PRO]` | 미제공 | 미제공 |
| FY2028Q2 (Jul 2027) | 3.67 | 3.60 | `[PRO]` | 미제공 | 미제공 |
| 전망치 수 | 44/42/40/40 | 12/11/10/10 | 40/38/`[PRO]`/`[PRO]` | 미제공 | 미제공 |
| 4분기 합 | 12.08 | 11.96 | 계산 불가 | 계산 불가 | 계산 불가 |

값은 가깝지만 **표본 수가 크게 다르다**(44 vs 12 vs 40). 전망치 수는 해당 지표·분기의 표본 수이며 전체 커버 애널리스트 수와 같다고 보지 않는다. 서로 다른 공급사의 값이므로 나란히 보존하고 섞지 않는다. Valley 의 실제 공급사와 집계·제외 규칙은 여전히 미확인이며 추측하지 않는다.

## 5. 검증 결과

`verify.py` 실행 결과는 `verify-output.txt` 에 있다. **FAIL 0건, 진단성 WARN 10건.**

기업별로 통과한 검사다.

- evidence.json 의 4분기 값이 원문 스냅샷과 일치 (10/10)
- 두 Nasdaq 엔드포인트의 미발표 4분기 라벨·평균 일치 (10/10)
- 모든 분기에서 최소 ≤ 평균 ≤ 최대 (10/10)
- 모든 분기 전망치 수 > 0 (10/10)
- 4개 분기 라벨 중복 없음, 3개월 간격 연속 (10/10)
- 첫 미발표 분기가 StockAnalysis 의 다음 미발표 분기 종료월과 일치 (10/10)
- 마지막 발표 분기의 **기간**이 세 원천에서 일치 (10/10)
- 독립 원천 기준 다음 실적 발표일이 기준일 이후 (10/10)
- 4분기 평균 합 재계산 일치 (10/10)
- 기준시점 상장·거래 확인 (10/10)

### 5.1 진단: 같은 확정 분기인데 실적 EPS 가 원천마다 다르다

> **2026-09-09 개정 (NTM-SOURCE-05).** 초판의 *"기간은 일치하므로 기간 오정렬이 아니라 조정(adjusted) 정의 차이다"* 단정을 **철회한다.** 기간 일치는 기간 불일치 가설 하나만 배제할 뿐, 주식 기준·통화·분할·갱신 시점 등 다른 원인을 배제하지 않는다. 개정 경위와 후속 검증은 `REPORT-05.md` 와 `CHANGELOG-05.md` 를 참조한다.

기간은 일치하는데 값이 다른 기업이 5개다.

| 기업 | 확정 분기 | Nasdaq | TradingView | StockAnalysis 조정열 | 격차 |
|---|---|---|---|---|---|
| Amazon | Jun 2026 | 1.88 | 5.75 | 5.75 | **3.87** |
| Oracle | May 2026 | 1.79 | 2.11 | 2.11 | 0.32 |
| Tesla | Jun 2026 | 0.04 | 0.33 | 0.33 | 0.29 |
| Apple | Jun 2026 | 1.91 | 2.02 | 2.02 | 0.11 |
| Palantir | Jun 2026 | 0.31 | 0.41 | 0.41 | 0.10 |

**원인은 이 표만으로 확정되지 않는다.** NTM-SOURCE-05 에서 SEC 공시와 대조한 결과 다음까지만 말할 수 있다.

- StockAnalysis 의 `eps` 열은 SEC 공시 **GAAP 희석 EPS 와 10개사 전부 일치**한다(Microsoft·Oracle 은 FY 말 분기라 FY − 9개월 누적으로 유도).
- Nasdaq 의 확정 실적 열은 **SEC GAAP 희석도 GAAP 기본도 아니다.** 차이는 한 방향이 아니라 양방향이다(Oracle +0.34, Amazon −3.87).
- Nasdaq 이 무엇을 가감하는지, 즉 **조정 규칙의 공식 정의는 여전히 미확인**이다. `Consensus EPS*` 의 별표 정의 문서를 공개 경로에서 찾지 못했다.
- 확정 실적 열의 기준을 **추정 열이 그대로 쓰는지도 공급사 문서로 확인되지 않았다.** 같은 표에 병기된다는 점은 정황이지 증명이 아니다.

초판이 "NVIDIA 는 원천 간 일치한다"고 적은 것도 정정한다. NVIDIA 의 Nasdaq 값 2.22 는 StockAnalysis 의 **조정열**과 일치할 뿐이고 GAAP 희석(2.46)과는 다르다. 원천 간 일치 여부는 어느 열과 비교하느냐에 따라 달라진다.

**이것은 이번 수집의 오류가 아니라 원천 간 기준 차이의 관측이다.** 확정된 과거 실적조차 갈리므로 전망치도 원천 간 대체·혼합이 불가능하다. 미발표 첫 분기 평균에서도 같은 패턴이 나온다: Tesla 76.9%, SpaceX 55.6%, Palantir 25.6%, Oracle 24.3% 의 상대격차다.

이 진단의 실무적 결론은 하나다. **3·4번째 분기를 Nasdaq 에서만 얻은 현재 상태에서, 1·2분기를 다른 공급사 값으로 바꿔 끼우면 안 된다.** 4분기 묶음은 Nasdaq 원천 그대로만 유효하다.

## 6. 미확보·미검증 항목

| 항목 | 상태 | 비고 |
|---|---|---|
| 중간값 | 미확보 (10개사 0/4) | 보조 정보. 이 결측으로 평균을 폐기하지 않았다 |
| 공급사 추정치 갱신 시각 | 미확인 | Nasdaq `asOf` = null. 조회 시각은 갱신 시각의 증명이 아니다 |
| 회계 기준(별표 정의) | 미확인 | `Consensus EPS*` 의 별표 정의 문서를 공개 경로에서 찾지 못함 |
| 주식 기준(희석/기본) | 미확인 | 공급사 명시 없음 |
| 통화 | 미표기 | 미국 상장 종목이나 공급사 통화 필드가 null |
| 3·4번째 분기 교차검증 | 없음 | 단일 원천. 다른 무료 원천은 2분기까지만 노출 |
| 회사 공식 회계기간 대조 | 미완 | 공급사 월 라벨 기준. Apple 실제 분기말은 9월 말 근처로 월 라벨과 어긋날 수 있다 |
| Valley 공급사·집계 규칙 | 미확인 | 로그인 없이 표 미확보 |
| 차단·인증 원천 | 미조사 | 부재나 불가능으로 단정하지 않음 |

## 7. 계산 후보 (검증 대기)

같은 공급사 화면의 주가와 4분기 평균 합으로 만든 참고 계산이다. 표 F 에 전체가 있다. 회계·주식 기준이 미확인이라 **채점 입력이 아니며, 2026-09-02 기준선에 소급 적용하지 않는다.** 2026-09-08 종가 기준이고 기준선 시점 값이 아니다.

| 기업 | 주가(09-08 종가) | 4분기 평균 EPS 합 | 주가÷EPS합 |
|---|---|---|---|
| Meta | 613.48 | 30.18 | 20.33 |
| NVIDIA | 225.73 | 11.96 | 18.87 |
| Alphabet | 338.36 | 12.91 | 26.21 |
| Microsoft | 493.95 | 19.45 | 25.40 |
| Amazon | 256.97 | 9.60 | 26.77 |
| Apple | 316.22 | 9.14 | 34.60 |
| Oracle | 162.52 | 6.51 | 24.96 |
| Palantir | 170.30 | 1.48 | 115.07 |
| Tesla | 368.16 | 1.07 | 344.07 |
| SpaceX | 153.47 | 1.16 | 132.30 |

Tesla 와 SpaceX 의 값이 특히 큰 이유는 Nasdaq 의 조정 기준이 다른 공급사보다 훨씬 보수적인 EPS 를 쓰기 때문이다(§5.1). 다른 공급사 기준이었다면 분모가 달라진다. 이 표를 공급사 Forward PE 나 기존 기준선 점수와 같은 것으로 취급하면 안 된다.

## 8. C-13 과 공유할 사항

담당 밖이지만 TSMC·Alibaba 에도 같은 경로가 열려 있을 가능성이 높다.

- `https://api.nasdaq.com/api/analyst/TSM/earnings-forecast`, `https://api.nasdaq.com/api/analyst/BABA/earnings-forecast` 를 위 헤더로 시도할 것.
- ADR 종목은 **공급사 EPS 가 ADR 주당인지 보통주 주당인지 공급사가 표기하지 않을 수 있다.** 이번 10개사에서도 주식 기준이 미표기였다. TSM/BABA 는 여기에 통화(TWD/CNY vs USD)까지 겹치므로 표기 없는 값을 USD·ADR 기준으로 가정하지 말 것.
- `https://api.nasdaq.com/api/quote/{T}/eps` 로 발표/미발표 경계를 먼저 확정하고, `https://stockanalysis.com/stocks/{slug}/forecast/__data.json` 의 `dates`·`lastDate` 로 회계분기 종료일을 대조할 것. 대만·홍콩 상장분(2330, 9988)은 Nasdaq API 대상이 아니므로 ADR 티커로만 접근된다.
- §5.1 의 회계 기준 차이가 TSM/BABA 에서도 나타나는지 반드시 같은 방식으로 확인할 것. 확정 분기 실적을 원천 간 대조하면 드러난다.
- 재현 스크립트는 이 폴더의 `fetchlib.py`, `collect_consensus.py`, `collect_extra.py`, `devalue.py` 를 그대로 쓸 수 있다. `devalue.py` 는 StockAnalysis 의 SvelteKit 평탄화 JSON 복원용이다.

## 9. 산출물

| 파일 | 내용 |
|---|---|
| `REPORT.md` | 이 보고서 |
| `evidence.json` | 기업×분기×지표×원천 관측, 검증 항목, 확보 수준, 채점 적격성 |
| `tables.md` | 표 A~F 전체 |
| `verify-output.txt` | 검증 실행 결과 (FAIL 0 / WARN 10) |
| `collect-raw.json`, `collect-extra.json` | 수집 원본 정규화 결과 |
| `raw/` | 원문 스냅샷 74건 (Nasdaq JSON 40건 = 기업당 forecast·eps·info·summary, StockAnalysis 10건, TradingView 10건, 원천 탐색 응답 등) |
| `probe_sources.py` | 원천 후보 18건 탐색 |
| `fetchlib.py`, `devalue.py` | 공개 GET 헬퍼, SvelteKit 평탄화 JSON 복원 |
| `collect_consensus.py`, `collect_extra.py` | 10개사 수집기 |
| `consolidate.py`, `verify.py`, `make_table.py` | 정규화·검증·표 생성 |

## 10. 범위 밖으로 남긴 것

- 채점 정책·점수·승인·규칙은 손대지 않았다. `worker` 를 포함한 다른 worktree 는 읽기 전용으로만 다뤘다.
- 기존 보고서·원문을 덮어쓰거나 지우지 않았다. 2026-09-08 Yahoo 관측은 재수집 없이 원문 그대로 인용했다.
- 철회된 N-04·N-06·N-07 추론은 재사용하지 않았다.
- 현재 수집값을 2026-09-02 기준선에 소급하지 않았다.
- 로그인 정보·세션 토큰은 저장하지 않았다. 결제·가입이 필요한 경로는 보류했다.
