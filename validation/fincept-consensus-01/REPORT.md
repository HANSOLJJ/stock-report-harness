# Fincept-CONSENSUS-01 — FinceptTerminal 전망치 데이터 수집 방식 조사

작성일 2026-09-09. 담당 worker(HANSOLJJ/worker). 요청 메시지 `msg_592094eb970d`.

조사 대상은 <https://github.com/Fincept-Corporation/FinceptTerminal> 이다. 대상 저장소와 우리 저장소 모두 코드를 수정하지 않았다. 이 보고서만 추가한다.

## 1. 결론

**FinceptTerminal 공개 저장소에는 애널리스트별 EPS·매출 전망이나 컨센서스 범위를 수집하는 경로가 없다.** 저장소 전체에서 컨센서스 공급사(IBES·Refinitiv·FactSet·Visible Alpha·Capital IQ·Zacks·TipRanks·Benzinga·Estimize·FMP·Finnhub·Intrinio 등)를 실제로 호출하는 코드는 한 줄도 없다. `min/avg/median/max/count` 통계는 존재하지만 대상이 **동종업체(peer) 배수**이지 애널리스트 전망 표본이 아니다.

따라서 **Valley(`valley.town`)의 회계분기별 최소·평균·중간값·최대·전망치 수를 이 저장소로 대체할 수 없다.** 우리 F6 의 NTM EPS 4분기 요건을 채우는 데 직접 쓸 수 있는 부분은 없다.

부수적으로 확인한 두 가지가 더 중요할 수 있다. 첫째, 저장소가 **AGPL-3.0** 이라 코드 차용은 우리 저장소 전체에 전염될 위험이 있다. 둘째, 저장소 문서(`MARKET_DATA_SOURCES.md`)는 "Analyst estimates" 를 제공한다고 적어 두었지만 그 문서가 가리키는 모듈 8개가 저장소에 **하나도 존재하지 않는다.** 문서만 읽고 원천으로 채택했다면 우리가 이미 겪은 `vendor_forward_pe_verified_ntm` 명칭 오독과 같은 종류의 사고가 났을 것이다.

## 2. 조사 대상과 방법

| 항목 | 값 |
|---|---|
| 저장소 | `Fincept-Corporation/FinceptTerminal` |
| 조사 커밋 | `09b70f3bc5c751d0e9507cb877de0270445034fb` (2026-09-08T20:18:54+05:30) |
| 취득 방법 | `git clone --depth 1` (읽기 전용, 스크래치 디렉터리) |
| 조사 시각 | 2026-09-09 |
| 작업 트리 파일 수 | 563 (`fincept-qt/`, `docs/` 기준) |
| Python 파일 수 | 428 |
| 라이선스 | AGPL-3.0 (`LICENSE:1`), Copyright 2025-2026 Fincept Corporation (`LICENSE:4`) |

### 2.1 방법상 주의 — 한 번 잘못 잡을 뻔한 것

처음에 `git grep` 으로 공급사 이름을 훑었고 0 건이 나왔다. 그러나 이 클론은 인덱스가 비어 있어(`git ls-files` 가 0 을 반환) `git grep` 이 **탐색 대상 자체가 없어서** 0 을 돌려준 것이었다. 부재의 근거로 쓸 수 없는 결과다. 작업 트리를 직접 훑는 `grep -r` 로 전부 다시 수행했고, 이 보고서의 모든 부재 주장은 재수행 결과에 기반한다. 재현 명령은 8절에 있다.

두 번째 주의. 단어 경계 없는 정규식 `ibes` 는 문서의 `subscribes` 에 걸려 오탐을 만든다. 최종 스윕은 `\b` 경계를 붙였다.

## 3. 발견 — 데이터 원천과 endpoint

### 3.1 공개 저장소에 애플리케이션 C++ 소스가 없다

`fincept-qt/CMakeLists.txt` 는 `src/` 아래 C++ 소스를 나열하지만(첫 항목 `CMakeLists.txt:835` `src/core/actions/ActionRegistry.cpp`) 그 디렉터리는 저장소에 없다.

- CMakeLists 가 참조하는 `src/**/*.cpp|.c` 경로: **1717 개**
- 그중 작업 트리에 실제로 존재하는 파일: **0 개**
- `.gitignore` 에 `src/` 제외 규칙: 없음

즉 실제 배포되는 Qt 터미널의 데이터 계층은 공개 저장소에서 감사할 수 없다. 이 보고서의 범위는 **저장소에 실재하는 Python `fincept-qt/scripts/` 트리와 문서**로 한정된다. C++ 쪽에 컨센서스 수집기가 있는지 없는지는 이 조사로 판정하지 않는다(미확인이지 부재 아님).

### 3.2 실제로 호출하는 외부 원천

작업 트리의 코드·설정에서 확인되는 호스트는 다음이 전부다.

| 호스트 | 용도 | 근거 |
|---|---|---|
| `finance.yahoo.com` (yfinance 라이브러리) | 시세·기본 재무 | `Analytics/equityInvestment/base/data_providers.py:51,56` |
| `www.alphavantage.co/query` | `OVERVIEW`·`GLOBAL_QUOTE` | `data_providers.py:181,187,192,201,208,261` |
| `www.sec.gov` / `efts.sec.gov` / `data.sec.gov` | 10-K 등 공시 | `Analytics/corporateFinance/valuation/sec_data_adapter.py:7,40` |
| `api.fincept.in` | 자사 LLM·매크로 캘린더 | `scripts/agents/deepagents/orchestrator.py:25,26` |
| `api.stlouisfed.org`, `api.worldbank.org`, `www.imf.org`, `stats.oecd.org`, `kidb.adb.org` | 거시 통계 | `Analytics/economics/*` |
| `api.binance.com`, `data.alpaca.markets`, `lite-api.jup.ag` | 시세·체결·토큰 가격 | `Analytics/*`, `docs/DATAHUB_TOPICS.md:147` |
| LLM 공급사(`openrouter.ai`, `api.deepseek.com`, `api.mistral.ai`, `api.together.xyz`, `api.fireworks.ai`, `api.minimax.io`) | 에이전트 | `scripts/agents/**` |

**애널리스트 컨센서스 공급사는 이 목록에 없다.**

### 3.3 yfinance 를 쓰지만 전망치 API 는 쓰지 않는다

`import yfinance` 를 하는 파일은 28 개다. 그런데 yfinance 가 제공하는 애널리스트 전망 API(`Ticker.earnings_estimate`, `revenue_estimate`, `eps_trend`, `growth_estimates`, `analyst_price_targets`)는 **어디에서도 호출되지 않는다.**

전망 관련으로 쓰는 것은 `info` 딕셔너리의 스칼라 한 개뿐이다.

```
data_providers.py:93    'forward_pe': info.get('forwardPE', 0),
```

이 값은 우리가 이미 `period_unknown` · NTM 적격성 `unverified` 로 판정한 그 공급사 forward PE 와 같은 성격의 값이다. 분모의 기간 정의도, 표본 수도, 분기 분해도 없다. Fincept 는 이 값을 그대로 dict 에 담을 뿐 검증하지 않는다.

Alpha Vantage `OVERVIEW` 응답에는 `ForwardPE`·`AnalystTargetPrice`·`AnalystRatingStrongBuy` 같은 필드가 들어 있지만, Fincept 의 추출 코드(`data_providers.py:216-238`)는 이들을 **읽지 않는다.** 읽는 것은 `RevenueTTM`·`ProfitMargin`·`BookValue`·`EPS`(후행)·`PERatio`(후행) 등 실적 기반 항목이다.

### 3.4 min/avg/median/max/count 는 있으나 대상이 다르다

요청에서 지목한 통계 조합은 실재한다. 위치는 `Analytics/corporateFinance/valuation/trading_comps.py:144` 의 `calculate_statistics` 다.

```
trading_comps.py:153-161
    f'{name}_mean':   mean(clean_vals),
    f'{name}_median': median(clean_vals),
    f'{name}_min':    min(clean_vals),
    f'{name}_max':    max(clean_vals),
    f'{name}_std':    stdev(clean_vals) if len(clean_vals) > 1 else 0,
    f'{name}_count':  len(clean_vals),
    f'{name}_q1':     np.percentile(clean_vals, 25),
    f'{name}_q3':     np.percentile(clean_vals, 75)
```

**표본의 정체가 다르다.** 입력은 `find_comparables`(`trading_comps.py:131`)가 모은 **동종업체 티커 목록**이고, 각 티커에 대해 `yf.Ticker(ticker)`(`:63`)로 받은 EV/Revenue·EV/EBITDA·P/E·P/B·P/S 같은 **현재 배수**다. 즉 `count` 는 "이 지표를 낸 애널리스트 수" 가 아니라 "비교 대상 회사 수" 다. `median` 은 "애널리스트 전망의 중간값" 이 아니라 "동종업체 배수의 중간값" 이다.

`precedent_transactions.py:247` 의 `summary_statistics` 도 같은 구조이며 표본은 과거 M&A 거래다.

Valley 화면의 `평균 2.47 / 표본 44` 와 이름만 같고 의미가 완전히 다르다. 이 둘을 같은 칸에 넣으면 우리 관측 스키마가 오염된다.

### 3.5 집계 규칙이 우리 규칙과 정면으로 충돌한다

```
trading_comps.py:148
    clean_vals = [v for v in values if v > 0 and not np.isnan(v) and not np.isinf(v)]
```

**0 과 음수를 통계에서 제외한다.** 우리 공통 방법(`설계진행/validation/consensus-research-method.md`)은 "EPS 가 0 또는 음수여도 유효 관측으로 보존한다" 를 명시한다. 이 필터를 그대로 쓰면 적자 분기가 표본에서 조용히 사라지고 `count` 가 실제 표본 수와 달라진다. 결측과 제외를 구분하지도 않는다. 값이 하나도 없으면 통계 전부를 `0` 으로 채우는데(`:149-150`), 이는 우리가 금지한 "unknown 을 0 으로 치환" 그 자체다.

### 3.6 문서가 코드보다 앞서 있다 — 채택 전 반드시 확인할 것

`fincept-qt/scripts/MARKET_DATA_SOURCES.md` 는 공급사 8 개 표를 싣고, FMP 항목에 **"Analyst estimates"**(`:93`), NASDAQ 항목에 **"Analyst ratings"**(`:86`)를 적어 두었다. 표는 각 공급사의 구현 파일명을 지정한다(`:13-21`).

그 8 개 파일 중 저장소에 존재하는 것은 **0 개**다.

| 문서가 지정한 파일 | 저장소 존재 여부 |
|---|---|
| `yfinance_data.py` | 없음 |
| `alphavantage_data.py` | 없음 |
| `nasdaq_data.py` | 없음 |
| `fmp_data.py` | 없음 |
| `trading_economics_data.py` | 없음 |
| `coingecko.py` | 없음 |
| `cboe_data.py` | 없음 |
| `cftc_data.py` | 없음 |

문서 말미는 `Last Updated: 2025-01-29`(`:148`)로 저장소 HEAD(2026-09-08)보다 1 년 7 개월 앞선다. FMP 키 발급 안내(`:38`)도 실제 호출 코드 없이 남아 있다.

같은 종류의 잔재가 두 곳 더 있다.

- `Analytics/derivatives/market_data.py:53-60` 의 `DataProvider` enum 에 `REFINITIV = "refinitiv"`(`:56`)가 있으나 이 상수는 저장소 어디에서도 **참조되지 않는다.** 클라이언트도 endpoint 도 없다.
- `sec_data_adapter.py:391` 주석은 `# Try to get analyst growth estimates` 라고 적었지만 바로 다음 줄(`:392-393`)이 읽는 `info['revenueGrowth']` 는 **후행 매출 성장률**이지 애널리스트 전망이 아니다. 실패하면 하드코딩 5%(`:376` `default_growth: float = 0.05`)로 조용히 대체하고 2~30% 로 클램프한다.

세 사례 모두 **이름·주석·문서가 실제 데이터보다 강한 주장을 한다.** 우리가 `vendor_forward_pe_verified_ntm` 에서 겪은 것과 같은 함정이다.

### 3.7 인증·라이선스 요구

| 항목 | 내용 |
|---|---|
| 저장소 라이선스 | AGPL-3.0 (`LICENSE:1`) |
| yfinance 경로 | API 키 불필요. 비공식 API |
| Alpha Vantage | `apikey` 쿼리 파라미터 필수 (`data_providers.py:191`), 무료 500 콜/일로 문서 기재(`MARKET_DATA_SOURCES.md:130`) |
| SEC/edgartools | 키 불필요. SEC 는 User-Agent 정책 요구, 어댑터에 해당 설정 코드 없음 |
| FMP / Trading Economics | 키 필요하다고 문서에 기재되나 호출 코드 없음 |

AGPL-3.0 은 우리에게 실질적 제약이다. 이 저장소의 코드를 복사·개작해 우리 파이프라인에 넣으면 파생물 전체가 AGPL 적용 대상이 될 수 있다. **구조를 참고하는 것과 코드를 가져오는 것을 구분해야 하며, 이 보고서의 권고는 전자에 한정한다.**

### 3.8 캐시·스냅샷 구조

전망치용 캐시나 스냅샷은 없다.

- `Analytics/derivatives/market_data.py:222` 의 `self.data_cache = {}` 는 파생상품 가격계산 입력(spot·무위험이자율·배당률·변동성)을 담는 **프로세스 내 dict** 다. TTL 도, 디스크 영속화도, 조회 시각·원천 기록도 없다. 값은 호출자가 수동으로 넣는다(`:236,242,248,259`).
- SQLite 영속화는 에이전트 메모리 계층에만 있다(`scripts/agents/finagent_core/agentic/archival_memory.py` 등). 시장·전망 데이터용이 아니다.
- C++ 쪽 DataHub 는 토픽별 TTL 을 정의하지만(`docs/DATAHUB_TOPICS.md`) 시장 데이터 계열은 `market:quote`(TTL 5초, `:11`), `market:sparkline`(60초, `:12`), `market:history`(300초, `:13`) 뿐이다. **레지스트리 전체에 fundamentals·estimates·consensus 토픽 계열이 없다.**

따라서 "같은 분기 전망을 시점별로 스냅샷해 보존" 하는 우리 요구를 만족하는 구조는 이 저장소에 없다.

### 3.9 회계기간·통화·ADR/ADS 정규화

세 가지 모두 **없다.**

- **회계기간**: 전망치가 없으니 분기 라벨 정규화도 없다. `fiscal_year`·`fiscal_quarter` 컬럼은 M&A 딜 데이터베이스 스키마에만 있다(`Analytics/corporateFinance/deal_database/database_schema.py:93,94`). 기업별로 다른 회계연도 말을 맞추는 코드는 없다.
- **통화**: 기업별 보고통화 정규화가 없다. `financialCurrency` 를 읽는 코드가 없고, FX 는 파생상품 가격결정(`derivatives/forward_commitments.py:406`)과 거시 분석(`economics/capital_flows.py:581`)에만 등장한다. `trading_comps` 는 서로 다른 통화의 시총·EV 를 통화 확인 없이 같은 통계에 넣는다.
- **ADR/ADS**: 서술형 교육 콘텐츠로만 존재한다(`Analytics/equityInvestment/market_analysis/equity_securities.py:527,530,543,550,560`). ADR 비율 환산이나 보통주/ADS 기준 변환을 수행하는 코드는 없다.

## 4. 우리 scorecard framework 재사용 가능성

| 항목 | 판정 | 근거 |
|---|---|---|
| 컨센서스 수집 코드 | **재사용 불가** | 존재하지 않음 (3.1~3.3) |
| min/max/median/count 집계 코드 | **차용 금지** | 표본 정의가 다르고(3.4) 0·음수 제외가 우리 규칙과 충돌(3.5). AGPL 전염 위험(3.7) |
| SEC/edgartools 어댑터 | **참고 가치 있음, 차용 아님** | `sec_data_adapter.py:57-237` 의 10-K 태그 추출은 F9 의 현금·부채·capex 같은 **실적** 항목 교차검증에 쓸 접근법이다. 전망치와 무관 |
| 통계 함수 형태 | **개념만 참고** | `mean/median/min/max/std/count/q1/q3` 를 한 dict 로 묶는 형태는 우리 관측 스키마의 보조통계 필드 설계에 참고할 수 있다. 단 0·음수 보존과 결측·제외 구분을 우리 규칙대로 다시 써야 한다 |
| DataHub 토픽 TTL 설계 | **개념만 참고** | 토픽별 TTL·최소 갱신 간격 분리(`DATAHUB_TOPICS.md:11-13`)는 원천별 갱신 정책을 기록하는 방식으로 참고 가능 |

정리하면 **코드는 가져올 것이 없고, 가져와서도 안 된다.** 얻을 것은 두 가지 교훈이다. 하나는 보조통계를 한 묶음으로 저장하는 형태, 다른 하나는 "문서·필드명이 데이터의 성격을 과장할 수 있으니 실제 호출 지점까지 따라가 확인한다" 는 절차다.

## 5. Valley 대체 가능성

**대체 불가.** Valley 가 제공하는 것은 회계분기 × 지표별 최소·평균·중간값·최대·전망치 수다. FinceptTerminal 공개 저장소에는 그 네 축(회계분기 분해, 애널리스트 표본, 분포 통계, 표본 수) 중 **어느 하나도** 수집하는 경로가 없다.

FinceptTerminal 을 경유해 얻을 수 있는 가장 가까운 값은 `info['forwardPE']` 스칼라 하나(`data_providers.py:93`)이고, 이는 우리가 이미 확보했고 이미 `period_unknown` · `unverified` 로 판정한 값과 동일한 성격이다. 새 정보가 없다.

다만 **부재를 확정하지는 않는다.** C++ 소스 1717 개 파일이 공개 저장소에 없으므로(3.1) 배포판 터미널에 컨센서스 화면이 있을 가능성은 이 조사로 배제되지 않는다. 확인하려면 배포 바이너리나 비공개 소스가 필요하며, 그것은 이번 조사 범위 밖이다.

## 6. 14개사·비상장사 적용 한계

### 6.1 상장 12개사

- 어느 기업에도 4 분기 EPS 컨센서스를 줄 수 없다. 확보 수준은 12 개사 모두 **0/4** 로 변함이 없다.
- TSMC(ADR, 재무 TWD)·Alibaba(ADS, 재무 CNY)는 추가로 막힌다. 통화·예탁증권 환산 코드가 없어(3.9) 설령 값이 있어도 우리 `basis` 계약(`currency`·`share_basis` 일치)을 만족시킬 수 없다.
- `trading_comps` 를 억지로 쓰면 서로 다른 통화의 배수가 한 통계에 섞인다. 우리 Q03(전 기업 동일 잣대) 요건과 충돌한다.

### 6.2 비상장 2개사 (OpenAI, Anthropic)

- 전 경로가 티커 기반이다(`yf.Ticker(ticker)`, Alpha Vantage `symbol`, SEC `Company(ticker)`). 비상장사는 입력 자체가 성립하지 않는다.
- post-money 기업가치, ARR, 연율화 매출, 누적 조달액 같은 우리 비상장 F6 입력을 다루는 구조가 없다.
- 결론: 비상장사에 대해 이 저장소는 **해당 없음**이다. 억지로 상장사 경로를 태우지 않는다.

## 7. 정적 검증 결과

코드 변경이 없어 실행 테스트는 대상이 아니다. 우리 저장소 상태는 그대로임을 확인했다.

| 검증 | 결과 |
|---|---|
| `npm test` (54 건) | 통과 |
| `python scripts/validate_report_contract.py ai-scorecard-2026-09-baseline` | 8 개 항목 PASS |
| `results.json` sha256 | `4eb8c7d7…` (변경 없음) |
| 우리 저장소 코드·점수 입력·승인 | 변경 없음. 이 보고서 파일만 추가 |

## 8. 재현 방법

```bash
git clone --depth 1 https://github.com/Fincept-Corporation/FinceptTerminal.git
cd FinceptTerminal
git log -1 --format=%H          # 09b70f3bc5c751d0e9507cb877de0270445034fb

# 주의: 인덱스가 비어 있을 수 있으므로 git grep 이 아니라 작업 트리를 훑는다
git ls-files | wc -l            # 0 이면 git grep 결과는 부재의 근거가 못 된다

# 컨센서스 공급사 부재 (단어 경계 필수)
grep -rniE "\b(ibes|refinitiv|factset|visible alpha|capital iq|zacks|tipranks|benzinga|estimize|financialmodelingprep|finnhub|intrinio|quandl|simfin)\b" fincept-qt docs README.md

# yfinance 전망 API 부재
grep -rnE "analyst_price_targets|earnings_estimate|revenue_estimate|eps_trend|growth_estimates" fincept-qt/scripts

# C++ 소스 부재
grep -oE "src/[A-Za-z0-9_/.-]+\.(cpp|c)" fincept-qt/CMakeLists.txt | sort -u | wc -l   # 1717
grep -oE "src/[A-Za-z0-9_/.-]+\.(cpp|c)" fincept-qt/CMakeLists.txt | sort -u | while read f; do [ -f "fincept-qt/$f" ] && echo "$f"; done | wc -l   # 0

# 문서가 지정한 provider 모듈 부재
for f in yfinance_data.py alphavantage_data.py nasdaq_data.py fmp_data.py \
         trading_economics_data.py coingecko.py cboe_data.py cftc_data.py; do
  printf "%-28s %s\n" "$f" "$(find fincept-qt docs -name "$f" | head -1)"
done
```

## 9. 미확인으로 남긴 것

부재로 단정하지 않고 미확인으로 남긴다.

1. **배포판 Qt 터미널의 C++ 데이터 계층.** 공개 저장소에 소스가 없어 감사하지 못했다(3.1). 컨센서스 화면의 유무는 판정하지 않는다.
2. **`api.fincept.in` 의 비공개 endpoint 목록.** 코드에서 확인된 것은 LLM 연구용과 매크로 캘린더뿐이다. 다른 경로가 있는지는 서버 문서 없이 확인할 수 없다.
3. **저장소의 다른 브랜치·태그.** `--depth 1` 기본 브랜치만 조사했다.
4. **FMP·NASDAQ 자체의 컨센서스 제공 능력.** 이 조사는 "Fincept 가 그것을 호출하지 않는다" 만 확인했다. FMP 가 우리에게 유용한 분기 컨센서스를 주는지는 **별도 조사 대상**이며, 이번 결과로 배제해서는 안 된다.

4 번은 후속 제안으로 남긴다. Valley 대체 원천을 계속 찾는다면 FinceptTerminal 이 아니라 FMP·Finnhub 같은 공급사를 직접 조사하는 편이 빠르다.

## 10. 근거 파일 목록

| 파일 | 인용 줄 |
|---|---|
| `LICENSE` | 1, 4 |
| `fincept-qt/CMakeLists.txt` | 835 이하 소스 목록 |
| `fincept-qt/scripts/MARKET_DATA_SOURCES.md` | 13-21, 26, 38, 86, 93, 130, 132, 148 |
| `fincept-qt/docs/DATAHUB_TOPICS.md` | 11, 12, 13, 147 |
| `fincept-qt/scripts/Analytics/equityInvestment/base/data_providers.py` | 51, 56, 93, 181, 187, 191, 192, 201, 208, 216-238, 261, 475, 480 |
| `fincept-qt/scripts/Analytics/corporateFinance/valuation/trading_comps.py` | 14, 63, 131, 144, 148, 149-150, 153-161, 218, 221, 265, 269 |
| `fincept-qt/scripts/Analytics/corporateFinance/valuation/precedent_transactions.py` | 247 |
| `fincept-qt/scripts/Analytics/corporateFinance/valuation/valuation_summary.py` | 87, 89, 124, 126, 252 |
| `fincept-qt/scripts/Analytics/corporateFinance/valuation/sec_data_adapter.py` | 7, 40, 57-237, 376, 391, 392-393 |
| `fincept-qt/scripts/Analytics/corporateFinance/deal_database/database_schema.py` | 93, 94 |
| `fincept-qt/scripts/Analytics/derivatives/market_data.py` | 53-60, 56, 222, 236, 242, 248, 259 |
| `fincept-qt/scripts/Analytics/equityInvestment/market_analysis/equity_securities.py` | 527, 530, 543, 550, 560 |
| `fincept-qt/scripts/agents/deepagents/orchestrator.py` | 25, 26 |
