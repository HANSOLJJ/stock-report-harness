# Fincept-CONSENSUS-01 — FinceptTerminal 전망치 데이터 수집 방식 조사

작성일 2026-09-09. 담당 worker(HANSOLJJ/worker). 요청 메시지 `msg_592094eb970d`.

조사 대상은 <https://github.com/Fincept-Corporation/FinceptTerminal> 이다. 대상 저장소와 우리 저장소 모두 코드를 수정하지 않았다.

> **정정 고지.** 이 문서는 같은 제목의 초판(커밋 `9a42121`)을 전면 대체한다. 초판은 **불완전한 체크아웃을 근거로 잘못된 결론**을 냈다. 무엇이 왜 틀렸는지는 2.2 절에 남긴다. 초판의 핵심 주장("전망치 수집 경로가 없다")은 **사실이 아니다.**

## 1. 결론

FinceptTerminal 은 애널리스트 데이터를 수집한다. 경로는 두 갈래이고, 우리 목적에 대한 유용성이 서로 다르다.

| 경로 | 무엇을 주나 | 우리 F6 에 쓸 수 있나 |
|---|---|---|
| yfinance `info` 목표주가 블록 | 목표주가 **high/low/mean + 애널리스트 수** | 아니오. EPS 가 아니라 목표주가다 |
| FMP `/api/v3/analyst-estimates/{symbol}` | EPS·매출 컨센서스, `period` 파라미터 있음 | **후보. 단 저장소만으로는 검증 불가** |

핵심은 이렇다. **`min/avg/max/count` 구조는 실재하지만 그 대상이 목표주가다.** EPS 컨센서스로 가는 유일한 문은 FMP `analyst-estimates` 하나이고, FinceptTerminal 은 그 응답을 **가공 없이 그대로 통과시킨다.** 즉 이 저장소는 컨센서스를 *계산하지* 않는다. 집계는 전적으로 공급사가 한다.

따라서 **Valley 대체 후보는 FinceptTerminal 이 아니라 그 뒤에 있는 FMP 다.** FinceptTerminal 은 "FMP 의 analyst-estimates 를 쓰면 된다" 는 사실을 알려주는 이정표이지, 그 자체가 원천이 아니다. FMP 가 분기 단위로 무엇을 주는지, 무료 등급에서 열리는지, 표본 수를 함께 주는지는 **FMP 를 직접 조사해야** 한다(9절 후속 제안).

부수 확인 두 가지는 그대로 유효하다. 저장소는 **AGPL-3.0** 이라 코드 차용에 전염 위험이 있다. 그리고 **회계기간·통화·ADR/ADS 정규화가 사실상 없다** — 이 저장소를 경유해도 우리 `basis` 계약은 우리가 직접 채워야 한다.

## 2. 조사 대상과 방법

| 항목 | 값 |
|---|---|
| 저장소 | `Fincept-Corporation/FinceptTerminal` |
| 조사 커밋 | `09b70f3bc5c751d0e9507cb877de0270445034fb` (2026-09-08T20:18:54+05:30) |
| HEAD 트리 파일 수 | **3597** (`git ls-tree -r HEAD` 기준) |
| C++ 소스 | `fincept-qt/src/` 아래 **2013** 개 |
| 최상위 provider 스크립트 | `fincept-qt/scripts/*.py` **320** 개 |
| 등록된 데이터 커넥터 | **190** (`src/mcp/tools/DataConnectorManifest.inc`) |
| 라이선스 | AGPL-3.0 (`LICENSE:1`), Copyright 2025-2026 Fincept Corporation (`LICENSE:4`) |

### 2.1 취득 방법

Windows 에서 기본 `git clone` 은 **실패한다.** 저장소에 `MAX_PATH` 를 넘는 경로가 있어 체크아웃이 중간에 끊긴다.

```
error: unable to create file fincept-qt/scripts/agents/hedgeFundAgents/
  renaissance_technologies_hedge_fund_agent/agents/compliance_officer.py: Filename too long
fatal: cannot create directory at '.../agents/tools': Filename too long
```

성공하는 명령은 이것이다.

```bash
git clone --depth 1 -c core.longpaths=true \
  https://github.com/Fincept-Corporation/FinceptTerminal.git /e/tmp/ft
cd /e/tmp/ft && git ls-files | wc -l    # 3597 이어야 한다
```

### 2.2 초판이 틀린 이유 — 같은 실수를 반복하지 않기 위해

초판은 위 실패한 클론의 잔해를 조사했다. 증상과 오판의 연쇄는 이랬다.

1. `git clone` 이 **exit code 0 을 반환**했다. 긴 경로 오류는 stderr 로만 나갔고 종료 코드에 반영되지 않았다.
2. 체크아웃이 중단되면서 작업 트리에는 **563 개**만 남았다(전체 3597 개 중). 인덱스는 비었다.
3. `git ls-files` 가 0 을 반환했다. 나는 이것을 "인덱스가 깨졌다" 로만 해석하고 **작업 트리는 온전하다고 가정**했다. 틀린 가정이었다. 작업 트리야말로 반쪽이었다.
4. 그 반쪽 트리에 `grep -r` 을 돌려 "`src/` 가 없다", "provider 모듈 8 개가 없다", "컨센서스 공급사 호출이 없다" 는 **부재 결론 세 개**를 냈다. 전부 사실이 아니다.

교훈은 하나다. **부재를 주장하기 전에 탐색 대상의 완전성을 먼저 증명한다.** 이 경우 필요한 확인은 `git ls-tree -r HEAD --name-only | wc -l` 과 작업 트리 파일 수의 대조 한 줄이었다. 종료 코드 0 은 체크아웃 완전성의 근거가 아니다.

초판이 맞게 본 것도 있다. 라이선스(AGPL-3.0), 정규화 부재, `trading_comps` 의 통계가 애널리스트 표본이 아니라는 점은 재조사 후에도 유지된다.

## 3. 발견 — 애널리스트 데이터 경로

### 3.1 경로 A. yfinance 목표주가 — min/avg/max/count 구조의 실체

Python 수집기가 `Ticker.info` 에서 목표주가 블록을 뽑는다.

```
fincept-qt/scripts/yfinance_data.py:236-241
    "target_high_price":            info.get('targetHighPrice'),
    "target_low_price":             info.get('targetLowPrice'),
    "target_mean_price":            info.get('targetMeanPrice'),
    "recommendation_mean":          info.get('recommendationMean'),
    "recommendation_key":           info.get('recommendationKey'),
    "number_of_analyst_opinions":   info.get('numberOfAnalystOpinions'),
```

C++ 서비스가 이를 모델에 싣는다.

```
fincept-qt/src/services/equity/EquityResearchService.cpp:724   s.target_high    = o["target_high_price"].toDouble();
fincept-qt/src/services/equity/EquityResearchService.cpp:729   s.analyst_count  = o["number_of_analyst_opinions"].toInt();
```

모델 정의는 `src/services/equity/EquityResearchModels.h:95-101` 의 `target_high` · `target_low` · `target_mean` · `recommendation_mean` · `recommendation_key` · `analyst_count` 이고, 같은 구조체 `:51` 에 `forward_pe` 가 있다.

화면은 이 값을 게이지로 그린다. `src/screens/equity_research/EquityAnalysisTab.cpp:409` 가 `gauge_->set_data(info.target_low, info.target_mean, info.target_high, …)` 를 호출하고, `:455` 가 `"%n analyst(s)"` 로 표본 수를 표시한다. 커버리지가 없으면 `"No analyst coverage"` 로 떨어진다(`EquityAnalysisTab.h:104`).

같은 값이 관계도 화면에도 쓰인다(`scripts/relationship_map.py:98,102`, `src/services/relationship_map/RelationshipMapService.cpp:121,125`). 관계도 쪽은 추가로 yfinance 의 `analyst_price_targets` · `recommendations_summary` · `upgrades_downgrades` 를 직접 읽는다(`relationship_map.py:177,192,209`).

**우리 용도로는 쓸 수 없다.** high/low/mean/count 가 붙는 대상이 **목표주가**다. 회계분기별 EPS 가 아니다. Valley 화면의 "FY2027Q3 일반 EPS 평균 2.47, 표본 44" 와는 축이 다르다.

### 3.2 경로 B. FMP analyst-estimates — 유일한 EPS 컨센서스 문

최상위 provider 스크립트 320 개 전체에서 애널리스트 **전망치** endpoint 는 하나뿐이다.

```
fincept-qt/scripts/fmp_extra_data.py:35-36
def get_analyst_estimates(symbol: str, period: str = "annual", limit: int = 10) -> Any:
    return _make_request(f"analyst-estimates/{symbol}",
                         {"apikey": API_KEY, "period": period, "limit": limit})
```

- BASE_URL 은 `https://financialmodelingprep.com/api/v3` (`fmp_extra_data.py:12`)
- 인증은 `FMP_API_KEY` 환경변수 (`:11`)
- CLI 서브커맨드 `estimates <symbol> [period] [limit]` 로 노출 (`:66-69`)
- 앱에는 MCP 데이터 커넥터 `data_fmp_extra` 의 `estimates` 명령으로 등록 (`src/mcp/tools/DataConnectorManifest.inc:59`)

**`period` 가 호출자에게 열려 있다.** 기본값은 `"annual"` 이지만 그대로 통과시키므로 `"quarter"` 를 넘길 수 있다. 우리가 필요한 분기 단위 조회의 입구가 여기다.

동시에 한계가 분명하다. `_make_request`(`:20-30`)는 응답 JSON 을 **그대로 반환**한다. 파싱도, 검증도, 필드 재명명도, 회계기간 대조도 없다. 오류는 `{"error": …}` dict 로 뭉개진다. 즉 **FinceptTerminal 은 컨센서스를 계산하지 않는다.** min/avg/max 와 표본 수가 응답에 들어 있다면 그것은 FMP 가 계산한 값이며, 이 저장소는 배달만 한다.

> 응답 필드의 실제 이름과 분기 지원 여부는 **이 저장소로 검증할 수 없다.** 코드에 응답 스키마가 없기 때문이다. FMP 문서·실제 호출로 따로 확인해야 한다(9절). 초판에서 한 번 데인 만큼, 여기서 추측으로 필드명을 적지 않는다.

### 3.3 그 밖의 전망 인접 데이터

| 원천 | 무엇 | 근거 |
|---|---|---|
| Finnhub `calendar/earnings` | 실적 발표 일정(공급사가 EPS 추정치를 함께 주는 endpoint) | `scripts/finnhub_data.py:53-58`, BASE `https://finnhub.io/api/v1` (`:13`) |
| FMP `discounted-cash-flow/{symbol}` | FMP 산출 DCF 밸류 | `fmp_extra_data.py:33` |
| Intrinio | `search`·`prices`·`news`·`economic`·`tags`·`fundamentals` — 전망치 명령 없음 | `DataConnectorManifest.inc:91` |
| SimFin | `income`·`balance`·`cashflow`·`companies`·`prices`·`ratios` — 전망치 명령 없음 | `DataConnectorManifest.inc:152` |
| Nasdaq Data Link (구 Quandl) | 데이터셋 조회 | `scripts/quandl_nasdaq_data.py` |
| Alpha Vantage | `OVERVIEW`·`GLOBAL_QUOTE` 등. `AnalystTargetPrice` 필드는 **읽지 않는다** | `Analytics/equityInvestment/base/data_providers.py:201,208,216-238` |

Finnhub 실적 캘린더는 분기 EPS 추정치의 또 다른 후보지만, 이 저장소의 호출은 날짜 구간 조회일 뿐이고 응답을 가공하지 않는다.

### 3.4 저장소가 직접 계산하는 통계는 전망치가 아니다

`Analytics/corporateFinance/valuation/trading_comps.py:144` 의 `calculate_statistics` 는 `mean`·`median`·`min`·`max`·`std`·`count`·`q1`·`q3` 를 한 dict 로 만든다(`:153-161`). 이름만 보면 우리가 찾던 것 같지만 **표본이 동종업체다.** 입력은 `find_comparables`(`:131`)가 모은 peer 티커 목록이고, 각 티커의 EV/Revenue·EV/EBITDA·P/E 같은 **현재 배수**를 `yf.Ticker(ticker)`(`:63`)로 받아 쓴다. `count` 는 "애널리스트 수" 가 아니라 "비교 회사 수" 다. `precedent_transactions.py:247` 도 같은 구조이며 표본은 과거 M&A 거래다.

집계 규칙도 우리와 충돌한다.

```
trading_comps.py:148
    clean_vals = [v for v in values if v > 0 and not np.isnan(v) and not np.isinf(v)]
```

**0 과 음수를 버린다.** 우리 공통 방법(`설계진행/validation/consensus-research-method.md`)은 "EPS 가 0 또는 음수여도 유효 관측으로 보존한다" 를 명시한다. 표본이 하나도 없으면 통계 전부를 `0` 으로 채우는데(`:149-150`), 이는 우리가 금지한 unknown→0 치환이다. 이 함수는 우리 목적에 그대로 쓸 수 없다.

### 3.5 캐시·스냅샷 구조

실재한다. 초판의 "없다" 는 틀렸다.

- `CacheManager` 는 **SQLite 백엔드**다. 헤더 주석이 명시한다 — `src/storage/cache/CacheManager.h:10` "SQLite-backed cache. All reads and writes go directly to CacheDatabase (cache.db)".
- API 는 `put(key, value, ttl_seconds = 300, category = "general")` (`CacheManager.h:17`).
- 주식 조회는 키를 계층화해 넣는다. `equity:quote:<symbol>`(`EquityResearchService.cpp:202,217`), `equity:info:<symbol>`(`:227,242`), `equity:candles:<symbol>:<period>`(`:252`).
- TTL 은 시세 30 초, 기업정보 300 초다(`EquityResearchService.h:92,93`).

**우리 요구와는 다르다.** 이 캐시는 "최근 값을 잠깐 재사용" 하는 성능 캐시다. 같은 분기 전망을 **추정 시점별로 여러 벌 보존**하는 스냅샷 구조가 아니다. 키에 조회 시각도, 공급사 갱신 시각도 들어가지 않는다. TTL 이 지나면 덮어쓴다. 우리가 필요한 "기업 × 회계분기 × 지표 × 원천 × 추정 시점" 5 축 보존은 이 구조로 안 된다.

### 3.6 회계기간·통화·ADR/ADS 정규화

전체 트리를 다시 훑어도 셋 다 **없다.**

- **회계기간**: 기업별 회계연도 말을 맞추거나 분기 라벨을 정규화하는 코드가 없다. `fiscal_year`·`fiscal_quarter` 컬럼은 M&A 딜 DB 스키마에만 있다(`Analytics/corporateFinance/deal_database/database_schema.py:93,94`).
- **통화**: 기업 보고통화 정규화가 없다. `financialCurrency` 를 읽는 코드가 없고, 통화 변환은 재무제표 처리기의 `convert_currency`(`Analytics/finanicalanalysis/core/data_processor.py:532`) 한 곳뿐이며 전망치 경로와 무관하다.
- **ADR/ADS**: 서술형 교육 콘텐츠로만 존재한다(`Analytics/equityInvestment/market_analysis/equity_securities.py:527,530,543,550,560`). ADR 비율 환산 코드는 없다.

TSMC(ADR·재무 TWD)와 Alibaba(ADS·재무 CNY)에 대해 이 저장소를 경유해 값을 얻더라도, 우리 `basis` 계약(`currency`·`share_basis` 일치)은 **우리가 직접 채워야 한다.**

### 3.7 인증·라이선스

| 항목 | 내용 |
|---|---|
| 저장소 라이선스 | **AGPL-3.0** (`LICENSE:1`) |
| FMP (전망치 경로) | `FMP_API_KEY` 필수 (`fmp_extra_data.py:11`). 문서상 무료 250 콜/일 (`scripts/MARKET_DATA_SOURCES.md:132`) |
| yfinance (목표주가 경로) | 키 불필요. 비공식 API |
| Finnhub / Intrinio / SimFin | 각각 `FINNHUB_API_KEY` 등 환경변수 필요 (`DataConnectorManifest.inc:56,91,152`) |
| Alpha Vantage | `apikey` 쿼리 파라미터 필수 (`data_providers.py:191`) |

AGPL-3.0 은 실질적 제약이다. 이 저장소의 코드를 복사·개작해 우리 파이프라인에 넣으면 파생물 전체가 AGPL 적용 대상이 될 수 있다. **"어떤 endpoint 를 쓰는지 배우는 것" 과 "코드를 가져오는 것" 은 다르다.** 아래 권고는 전자에 한정한다.

## 4. 우리 scorecard framework 재사용 가능성

| 항목 | 판정 | 근거 |
|---|---|---|
| FMP `analyst-estimates` **endpoint 선택** | **채택 검토 대상** | 3.2. 단 FMP 직접 검증이 선행 조건 |
| FMP 호출 코드 자체 | 차용 불필요 | 5 줄짜리 GET 이다. AGPL 위험을 감수할 이유가 없다 |
| yfinance 목표주가 블록 | **우리 F6 에 무용** | 3.1. EPS 가 아니다 |
| `trading_comps.calculate_statistics` | **차용 금지** | 표본이 peer 이고 0·음수를 버린다 (3.4) |
| SQLite 캐시 구조 | **개념만 참고** | 키 계층 + 카테고리 + TTL 형태는 참고할 만하나, 우리는 덮어쓰기가 아니라 시점별 누적 보존이 필요하다 (3.5) |
| 정규화 계층 | **참고 대상 없음** | 없다 (3.6) |

정리하면 **가져올 코드는 없고, 얻을 정보는 하나다** — "FMP 에 `analyst-estimates` 라는 분기 파라미터를 받는 endpoint 가 있고, 실제 제품이 그것을 EPS 컨센서스 용도로 쓴다".

## 5. Valley 대체 가능성

**FinceptTerminal 자체는 대체재가 아니다.** 컨센서스를 계산하지 않고 공급사 응답을 통과시킬 뿐이다(3.2).

**FMP 는 대체 후보다.** 다만 다음 네 가지가 확인되기 전에는 후보 이상으로 취급하지 않는다.

1. `period=quarter` 가 실제로 회계분기 단위 EPS 컨센서스를 돌려주는가
2. 응답에 **표본 수**(전망치 수)가 포함되는가 — Valley 의 `44` 에 해당하는 값
3. 최소·최대가 포함되는가, 아니면 평균만 오는가
4. 무료 등급에서 이 endpoint 가 열리는가, 그리고 우리가 필요한 **미발표 4 개 분기**를 덮는가

이 넷은 저장소로 알 수 없다. FMP 를 직접 호출해 확인해야 한다.

확인되더라도 우리 규칙상 남는 제약이 있다. 회계기간 라벨은 공급사 라벨로 보존하고 회사 공식 회계기간과 별도 대조해야 하며, 서로 다른 공급사의 분기를 이어 붙여 검증된 NTM 으로 만들지 않는다.

## 6. 14개사·비상장사 적용 한계

### 6.1 상장 12개사

- 이 저장소를 경유한다고 확보 수준이 바뀌지 않는다. 실제 값은 FMP 에서 오고, 그 검증은 아직 안 됐다. 현재 **0/4 유지**다.
- TSMC·Alibaba 는 추가로 막힌다. 통화·예탁증권 환산이 없어(3.6) 값이 있어도 우리 `basis` 요건을 저장소 쪽에서 만족시킬 수 없다.
- 목표주가 경로(3.1)는 12 개사 전부에 적용 가능하지만 **F6 입력이 아니다.** 우리 규칙상 목표주가는 채점 입력이 아니며, 참고 지표로도 도입하려면 별도 결정이 필요하다.

### 6.2 비상장 2개사 (OpenAI, Anthropic)

- 모든 경로가 티커 기반이다(`analyst-estimates/{symbol}`, `yf.Ticker`, Finnhub `symbol`). 비상장사는 입력이 성립하지 않는다.
- post-money 기업가치·ARR·연율화 매출·누적 조달액을 다루는 구조가 없다.
- 결론: **해당 없음.** 상장사 경로를 억지로 태우지 않는다.

## 7. 정적 검증 결과

우리 저장소는 읽기만 했다. 상태 불변을 확인했다.

| 검증 | 결과 |
|---|---|
| `npm test` (54 건) | 통과 |
| `python scripts/validate_report_contract.py ai-scorecard-2026-09-baseline` | 8 개 항목 PASS |
| `results.json` sha256 | `4eb8c7d7…` (변경 없음) |
| 우리 코드·점수 입력·승인 | 변경 없음. 이 보고서 파일만 추가·수정 |

## 8. 재현 방법

```bash
# 1) 반드시 longpaths + 짧은 경로. 기본 clone 은 Windows 에서 조용히 반쪽만 받는다.
git clone --depth 1 -c core.longpaths=true \
  https://github.com/Fincept-Corporation/FinceptTerminal.git /e/tmp/ft
cd /e/tmp/ft

# 2) 완전성 먼저 증명한다. 이 두 값이 같아야 이후 grep 결과를 신뢰할 수 있다.
git ls-tree -r HEAD --name-only | wc -l   # 3597
git ls-files | wc -l                      # 3597

# 3) 전망치 endpoint — 최상위 provider 320개 중 이것 하나
grep -nE "(_make_request|requests\.get)[^\n]*\b(estimate|consensus|analyst)" fincept-qt/scripts/*.py
#   → fmp_extra_data.py:36  analyst-estimates/{symbol}

# 4) 목표주가 min/avg/max/count 경로
grep -rn "targetHighPrice\|numberOfAnalystOpinions" fincept-qt/scripts
grep -rn "target_high\|analyst_count" fincept-qt/src/services/equity/

# 5) yfinance 분기 EPS 컨센서스 API 미사용 확인
grep -rnE "\.(earnings_estimate|revenue_estimate|eps_trend|growth_estimates)\b" fincept-qt/src fincept-qt/scripts

# 6) 캐시 구조
grep -n "SQLite-backed" fincept-qt/src/storage/cache/CacheManager.h
grep -n "kQuoteTtlSec\|kInfoTtlSec" fincept-qt/src/services/equity/EquityResearchService.h
```

## 9. 미확인으로 남긴 것과 후속 제안

1. **FMP `analyst-estimates` 의 실제 응답.** 분기 지원, 표본 수, 최소·최대 포함 여부, 무료 등급 접근성. 저장소에 응답 스키마가 없어 확인 불가. **→ 이것이 다음 조사 대상이다.** Valley 대체를 계속 찾는다면 FinceptTerminal 이 아니라 FMP 를 직접 조사하는 편이 빠르다.
2. **Finnhub `calendar/earnings` 의 EPS 추정치.** 분기 단위 후보이나 이 저장소는 날짜 구간 조회만 한다. 별도 확인 필요.
3. **저장소의 다른 브랜치·태그.** `--depth 1` 기본 브랜치만 조사했다.
4. **190 개 커넥터 전수 조사.** 이번에는 endpoint 문자열 패턴으로 훑었다. 명령 이름이 전망치를 암시하지 않는 커넥터에 관련 기능이 숨어 있을 가능성은 배제하지 않는다.

## 10. 근거 파일 목록

| 파일 | 인용 줄 |
|---|---|
| `LICENSE` | 1, 4 |
| `fincept-qt/scripts/fmp_extra_data.py` | 11, 12, 20-30, 33, 35-36, 66-69 |
| `fincept-qt/scripts/yfinance_data.py` | 236-241 |
| `fincept-qt/scripts/relationship_map.py` | 98, 102, 177, 192, 209 |
| `fincept-qt/scripts/finnhub_data.py` | 13, 53-58 |
| `fincept-qt/scripts/MARKET_DATA_SOURCES.md` | 132 |
| `fincept-qt/src/mcp/tools/DataConnectorManifest.inc` | 56, 59, 91, 152 |
| `fincept-qt/src/services/equity/EquityResearchModels.h` | 51, 95-101 |
| `fincept-qt/src/services/equity/EquityResearchService.cpp` | 202, 217, 227, 242, 252, 724, 729 |
| `fincept-qt/src/services/equity/EquityResearchService.h` | 92, 93 |
| `fincept-qt/src/services/relationship_map/RelationshipMapService.cpp` | 121, 125 |
| `fincept-qt/src/screens/equity_research/EquityAnalysisTab.cpp` | 390, 409, 455 |
| `fincept-qt/src/screens/equity_research/EquityAnalysisTab.h` | 103, 104 |
| `fincept-qt/src/storage/cache/CacheManager.h` | 10, 17 |
| `fincept-qt/scripts/Analytics/corporateFinance/valuation/trading_comps.py` | 63, 131, 144, 148, 149-150, 153-161 |
| `fincept-qt/scripts/Analytics/corporateFinance/valuation/precedent_transactions.py` | 247 |
| `fincept-qt/scripts/Analytics/equityInvestment/base/data_providers.py` | 191, 201, 208, 216-238 |
| `fincept-qt/scripts/Analytics/finanicalanalysis/core/data_processor.py` | 532 |
| `fincept-qt/scripts/Analytics/corporateFinance/deal_database/database_schema.py` | 93, 94 |
| `fincept-qt/scripts/Analytics/equityInvestment/market_analysis/equity_securities.py` | 527, 530, 543, 550, 560 |
