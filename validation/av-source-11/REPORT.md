# AV-SOURCE-11 — Alpha Vantage `EARNINGS_ESTIMATES` 조사

작성일 2026-09-10. 담당 worker(HANSOLJJ/worker). 요청 `msg_bf7185886336`.

> ## 사용 범위 변경에 따른 정정 (2026-09-10, `POLICY-12` 후속)
>
> 이 문서는 사용 범위가 **personal/internal only** 라는 전제 위에서 썼다. **그 전제가 바뀌었다.** 산출물이 사용자가 대표로 있는 회사의 업무에 쓰이고, 약관상 분류는 신고가 아니라 실제 사용을 따르므로 **법인 내부 사용**이 구속 기준이다(`scorecard/rules/v1.6.json` `sources.usage_scope` = `corporate_internal_only`).
>
> **결과. 무료 티어 적격이 사라진다.** §2.a 의 무료 라이선스는 "for personal, non-commercial use" 이고, 같은 조항 **ii** 가 법인 명의·법인 대리 사용을 `commercial use` 로 분류한다. 기준 넷 중 **하나만 해당해도** 상업 사용이므로 ii 하나로 결정된다. 쓰려면 `premium@alphavantage.co` 상업 계약 경로다.
>
> 3.1 이 ii 를 "사용자 사실관계라 unknown" 으로 남겼던 것은 **이제 해소됐다 — 해당한다.** 3 절 (b) 판정과 7.2-5 도 그에 맞춰 고쳤다.
>
> **채택 결론은 바뀌지 않는다.** 향후 분기 전망 2 개와 basis 4 필드 부재로 이미 F6 부적격이었다(4 절). 실질 손실이 없다는 뜻이며, 약관 경로가 하나 닫혔다는 사실만 추가된다.

**결론 먼저.** 약관은 개인·비상업 사용을 명시적으로 허가하지만 **우리는 그 범위 밖이다**(위 정정). 자동 수집·robots 금지는 없다. 그리고 **F6 관문도 통과하지 못한다.** 분기 전망이 4 개가 아니라 **2 개**이고, basis 4 필드(`currency`·`share_basis`·`accounting`·`asOf`)가 응답에 **전부 없다**. Yahoo 와 같은 이유(전망 2 분기)로 막히되, 회계분기 식별은 Yahoo 보다 낫다(절대 날짜).

**무료 키를 발급하지 않았다.** 발급 절차만 5 절에 정리했다. `api.nasdaq.com` 은 호출하지 않았다.

C-13 에 같은 과제가 독립 배정됐다. 이 문서는 C-13 산출을 참조하지 않고 `_raw/` 원자료에서만 산출했다.

## 0. 조사 순서와 범위

요청대로 **약관 확인을 수집보다 먼저** 했다.

| # | 행위 | 시각(UTC) | 결과 |
|---|---|---|---|
| 1 | `www.alphavantage.co/robots.txt` | 02:50:35 | **HTTP 404** |
| 2 | `alphavantage.co/robots.txt` | 02:50:42 | HTTP 301 → www |
| 3 | `/terms_of_service/` | 02:50:47 | HTTP 200 · `application/pdf` 4 쪽 |
| 4 | `/documentation/` | 02:51:48 | HTTP 200 |
| 5 | `/premium/` · `/support/` | 02:51:5x | HTTP 200 |
| 6 | 문서 공개 예시 `EARNINGS_ESTIMATES&symbol=IBM&apikey=demo` | 02:53:23 | HTTP 200 · 실제 자료 |
| 7 | 같은 함수 `symbol=NVDA&apikey=demo` | 02:53:3x | HTTP 200 · **안내문만** |

6·7 은 문서가 "click for JSON output" 으로 게시한 **예시 URL 그대로**이며 스키마 확인 목적의 2 회 요청이다. **12 개사 수집은 하지 않았다.** 키가 필요하고, 키 발급은 사용자 결정 사항이다(5 절).

원자료·지문·재현 스크립트는 `_raw/`, `analyze_demo.py`, `analysis-output.txt` 다. 분석 스크립트는 네트워크를 쓰지 않는다.

## 1. robots.txt — 존재하지 않는다

```
$ curl -D - https://www.alphavantage.co/robots.txt
HTTP/1.1 404 Not Found
Content-Type: text/html; charset=utf-8
...
<h1>Not Found</h1><p>The requested resource was not found on this server.</p>
```

`_raw/robots.txt` · `_raw/robots.headers.txt` 에 원문을 보존했다. apex 도메인은 301 로 `www` 에 넘긴다.

**robots.txt 가 없다는 것은 크롤러 지시가 없다는 뜻이다.** `api.nasdaq.com` 을 배제한 근거(전면 `Disallow` + `automated or manual process` 금지)가 여기에는 **존재하지 않는다.** 다만 **부재는 허가가 아니다.** 권한의 근거는 아래 약관이다.

## 2. 이용약관 — 원문 인용

전문은 `_raw/terms_of_service.pdf`(4 쪽, 개행 정규화 sha256:56c3a9eaa55baa7b)와 추출본 `_raw/terms_of_service.txt`(9,945 자) 다.

### 2.1 §2.a Grant of License — 개인·비상업 사용은 명시적 허가다

> Alpha Vantage grants the right to install, use, access, display and run the software on any computer or mobile device, where applicable, that you own or control, **for personal, non-commercial use**, unless you and Alpha Vantage have agreed otherwise in writing, and provided that you comply with all terms and conditions of the End User License Agreement (see below). **Usage falls under "commercial use" if any of the following criteria apply to you:**
>
> i. You intend to use the Alpha Vantage Platform for any purpose that goes beyond **investment analysis, research, testing, monitoring, and any other activities that are private and individual in nature**
>
> ii. You are using the Alpha Vantage Platform **as or on behalf of a corporation, firm, partnership, trust or any other association and not as an individual.**
>
> iii. You plan to use or provide information accessed through the Alpha Vantage Platform as part of any type of commercial activity **that allows individuals or entities other than User to access information** directly or indirectly even if the scope of such activity falls outside of the securities industry.
>
> iv. You are currently employed or have an active affiliation with a financial planning advisor, insurance company, investment advisor, investment bank, money manager, registered representative, securities broker-dealer, or any owner, partner, affiliate or associated person of the preceding.
>
> If you are interested in using the Alpha Vantage Platform for commercial purposes, please contact us at: premium@alphavantage.co

### 2.2 §3 EULA — 키를 받는 행위가 계약 체결이다

> Alpha Vantage hereby grants User a non-exclusive, non-sublicensable, non-transferable, non-assignable, **revocable** license to access and utilize the Alpha Vantage Platform pursuant to the terms of this Agreement. Access and utilization and acceptance of the EULA is effective as of the date **User clicks "Get Free API Key"** (the "Effective Date").

### 2.3 §4 Use Restrictions — 금지 대상은 역공학이다

> You will not, directly or indirectly, **reverse engineer, decompile, disassemble or otherwise attempt to discover the source code, object code or underlying structure, ideas, know-how or algorithms** relevant to the Alpha Vantage Platform, Content or any software, documentation or data related to this Agreement…

### 2.4 §5 Intellectual Property Rights

> a. **By Alpha Vantage.** Alpha Vantage shall retain all right, title and interest to the intellectual property rights to the Alpha Vantage Platform, including… **any other Content developed by Alpha Vantage**…
>
> b. **By User** User shall retain all right, title and interest to the intellectual property rights to **its data, and any other Content developed by User**.

## 3. 요청하신 네 항목 판정

**부재 주장을 근거로 쓰기 전에 검색 공간의 완전성을 먼저 확인했다.** 약관 4 쪽 전문을 텍스트로 추출해(9,945 자) 키워드를 기계로 셌다. 결과는 아래 괄호 안 숫자다.

**다만 검색 공간 자체가 좁다는 점을 먼저 적는다. 약관 전문이 4 쪽 9,945 자로 짧다.** 조항이 없는 것과 문서가 얇은 것은 다르다. 아래 (c)·(d) 의 `unknown` 은 **"이 문서에 없다"** 는 뜻이지 **"어디에도 허용·금지 조건이 없다"** 는 뜻이 아니다. 별도 EULA·프리미엄 약관·Privacy Policy 에 조항이 따로 있을 수 있고, 이번 범위는 robots.txt 와 이 ToS 였다(7.2-7). 채택 판단은 그 확인 뒤에 한다.

| # | 항목 | 판정 | 근거 |
|---|---|---|---|
| **(a)** | 프로그램 자동 수집 | **허용** (금지 조항 없음) | `scrap`(0) `crawl`(0) `robot`(0) `spider`(0) `automat`(1). 유일한 `automat` 은 §6 의 "**automatically renewed**" 로 갱신 조항이다. 애초에 **API 제공이 제품**이고 문서가 Python·NodeJS·PHP·C# 호출 예제를 게시한다. §4 의 금지는 역공학이지 조회가 아니다 |
| **(b)** | 개인·내부 사용 범위 | **개인은 명시적 허가. 그러나 우리 사용은 그 밖이다** | §2.a 가 "for personal, non-commercial use" 를 직접 부여한다. **다만 우리 사용은 법인 내부 사용이라 기준 ii(법인 명의·법인 대리)에 해당해 `commercial use` 로 분류된다.** 기준 넷 중 하나만 해당해도 상업 사용이므로 ii 하나로 결정된다(3.1) |
| **(c)** | 파생 데이터 계산 | **unknown — 조항 자체가 없다** | `derivative`(0) `derived`(0) `redistribut`(0) `resell`(0) `distribut`(0). 허가도 금지도 없다. 가장 가까운 것이 §5.b "User shall retain all right… to its data, and any other Content **developed by User**" 이고, 우리 점수는 사용자가 만든 파생물에 해당할 여지가 있으나 **원 Content 로부터의 파생을 명시적으로 다룬 문장이 아니다** |
| **(d)** | 저장·캐싱·보존 | **unknown — 조항 자체가 없다** | `cache`(0) `cach`(0) `store`(0) `storage`(0) `retention`(0). `retain`(2)은 둘 다 §5 의 지식재산권 귀속이지 데이터 보존이 아니다 |

키워드 계수는 `analysis-output.txt` 와 무관하게 재현 가능하다. `_raw/terms_of_service.txt` 를 직접 세면 된다.

### 3.1 기준 ii 는 해소됐다 — 해당한다

**초판은 여기를 "사용자 사실관계라 unknown" 으로 남겼다. 사용자 확인으로 해소됐다.**

산출물이 사용자가 대표로 있는 회사의 업무에 쓰인다. 개인 투자 참고 열람이 병행되지만 **약관상 분류는 신고가 아니라 실제 사용을 따른다.** 따라서 기준 **ii**("as or on behalf of a corporation … and not as an individual")에 **해당한다.**

§2.a 는 "**if any of the following criteria apply**" 다. **하나만 해당해도 상업 사용이므로 ii 하나로 결정된다.** 나머지는 굳이 가릴 필요가 없다.

| 기준 | 상태 | 비고 |
|---|---|---|
| i (private and individual in nature 를 넘어서는 목적) | 다투지 않는다 | ii 로 이미 결정됐다 |
| **ii (법인 명의·법인 대리)** | **해당** | **이것으로 결정된다** |
| iii (User 외의 개인·법인이 정보에 접근) | 다투지 않는다 | 외부 배포는 여전히 없다 |
| iv (금융업 종사·제휴) | unknown | 사용자 사실관계. **moot** — ii 로 이미 결정됐다 |

**결과는 무료 티어 적격 상실이다.** 무료 라이선스가 personal, non-commercial 에 걸려 있으므로 상업 사용은 그 밖이다. 경로는 `premium@alphavantage.co` 다.

무료 키 발급 양식이 **Organization 을 필수 입력**으로 받는다는 관측(5 절)은 이 판정과 같은 방향이다. 공급사 자신이 가입자를 조직 단위로 식별한다. **다만 이것은 관측이지 판정 근거가 아니다.** 판정 근거는 §2.a.ii 조문과 사용자가 확인해 준 실제 사용이다.

**채택 결론은 바뀌지 않는다.** 아래 4 절대로 **약관이 해소됐어도 F6 관문은 통과하지 못했다.** 향후 분기 2 개와 basis 4 필드 부재가 그대로다. 약관 경로가 하나 닫혔다는 사실만 추가되고 **실질 손실은 없다.**

### 3.2 무료 응답은 허가가 아니다 — 이 원칙이 여기서 어떻게 적용되나

`v1.6.json` 의 `policy_note` 원칙을 그대로 적용했다. 이번 판정의 근거는 **HTTP 200 이 아니라 §2.a 의 명시적 라이선스 문장**이다. 실제로 이 조사에서 HTTP 200 이 자료를 뜻하지 않는 사례가 나왔다. `symbol=NVDA&apikey=demo` 는 **HTTP 200** 을 내면서 본문은 안내문뿐이다.

```json
{"Information": "The **demo** API key is for demo purposes only. Please claim your free API key at (https://www.alphavantage.co/support/#api-key) to explore our full API offerings. It takes fewer than 20 seconds."}
```

## 4. F6 관문 1:1 대조

기준일 2026-09-10. 근거는 문서 예시 심볼 IBM 의 실제 응답(`_raw/EARNINGS_ESTIMATES.IBM.demo.json`, sha256:3491498f5fad6083, `estimates` 41 행)이다.

| F6 관문 항목 | Alpha Vantage | 근거 |
|---|---|---|
| **12 개사 커버리지** | **unknown** | demo 키가 문서 예시 심볼(IBM) 외에는 응답하지 않는다. 무료 키가 있어야 확인 가능 |
| **향후 분기 수 (4 개인가)** | **2 개 — 미달** | 기준일 이후 `fiscal quarter` 행이 `2026-09-30`·`2026-12-31` 둘뿐. 같은 응답의 `fiscal year` 는 `2026-12-31`·`2027-12-31` 둘이다 |
| **회계분기 식별 필드** | **절대 날짜 있음 · 의미는 unknown** | `horizon`("fiscal quarter"/"fiscal year") + `date`(YYYY-MM-DD). **Yahoo 식 상대 오프셋이 아니다.** 다만 IBM 은 달력연도 결산사라 회계분기말·달력분기말 두 가설이 갈리지 않는다 |
| **currency** | **unknown** | 응답 18 필드에 키 없음 |
| **share_basis** (ADR/ADS) | **unknown** | 응답 18 필드에 키 없음 |
| **accounting** (GAAP/Non-GAAP) | **unknown** | 응답 18 필드에 키 없음 |
| **asOf** | **unknown** | 응답 18 필드에 키 없음 |
| **표본수** | **있음** | `eps_estimate_analyst_count`(IBM 2026Q3 = 20), `revenue_estimate_analyst_count` |
| **min/max** | **있음** | `eps_estimate_low` / `eps_estimate_high` |
| **과거 시점 재현** | **부분적** | 평균만 `_7/30/60/90_days_ago` 로 4 점. low/high/표본수의 과거 값은 없고 임의 시점 파라미터도 문서에 없다 |

### 4.1 응답 필드 전체 (18 개)

```
date  horizon
eps_estimate_average  eps_estimate_high  eps_estimate_low  eps_estimate_analyst_count
eps_estimate_average_7_days_ago   eps_estimate_average_30_days_ago
eps_estimate_average_60_days_ago  eps_estimate_average_90_days_ago
eps_estimate_revision_up_trailing_7_days    eps_estimate_revision_down_trailing_7_days
eps_estimate_revision_up_trailing_30_days   eps_estimate_revision_down_trailing_30_days
revenue_estimate_average  revenue_estimate_high  revenue_estimate_low
revenue_estimate_analyst_count
```

**basis 4 필드는 키 자체가 없다.** Finnhub 과 같은 상태다(값이 빈 것이 아니라 키가 없다). 추측으로 채우지 않았다.

### 4.2 회계분기 식별 — 진전은 있으나 확정은 아니다

`horizon: "fiscal quarter"` 라는 **명시 라벨**과 절대 종료일을 함께 준다. Yahoo(`0q`/`+1q` 상대 오프셋)보다 낫고, Finnhub(`period` 가 회계종료일이 아님이 F6H-BATCH-10-R1 §3 에서 확인됨)보다도 낫다.

**그러나 "fiscal quarter" 라는 라벨이 곧 회계분기 종료일임을 이 자료로 확정할 수 없다.** IBM 의 분기 종료 월 집합이 `{03, 06, 09, 12}` 라 달력분기와 완전히 겹친다. 두 가설을 가르려면 NVDA(1 월)·MSFT(6 월)·AAPL(9 월)·ORCL(5 월) 같은 **비달력 결산사**가 필요한데 demo 키가 응답하지 않는다. **판정은 unknown 이고, 무료 키 1 개면 즉시 해소된다.**

### 4.3 향후 분기 2 개 — Yahoo 와 같은 벽이다

```
기준일 2026-09-10 이후 fiscal quarter 행
  2026-09-30  avg 2.8881  n 20  low 2.7800  high 3.1200
  2026-12-31  avg 4.6017  n 19  low 4.4100  high 4.7680
기준일 이후 fiscal year 행
  2026-12-31, 2027-12-31
```

F6 는 미발표 4 개 분기를 요구한다. **2 개는 절반이다.** F6-H(2 실적 + 2 전망)에는 형식상 맞지만, F6-H 자체가 아직 승인되지 않았고 basis 가 unknown 이라 어느 쪽으로도 채점에 못 쓴다.

주의할 점 하나. 연간은 2 개가 나오는데 분기는 2 개까지만 나온다. **자료가 없는 것이 아니라 분기 지평이 짧은 것이다.** 이것이 IBM 한 종목의 특성인지 함수 전체의 성질인지는 **다른 종목으로만 확인되고, 그러려면 키가 필요하다**(unknown).

## 5. 무료 키 — 발급 절차만 보고한다. 발급하지 않았다

발급 위치는 `https://www.alphavantage.co/support/#api-key` 이고, 양식이 요구하는 것은 셋이다.

| 입력 | 필수 | 선택지 / 형식 |
|---|---|---|
| "Which of the following best describes you?" | 선택 | Investor / Software Developer / Educator / Student / *I am from the Trading Agents project on Github* / Other |
| **Organization** (e.g. company, university, etc.) | **필수** | 자유 입력 |
| **Email** | **필수** | 자유 입력(최대 254 자) |

버튼은 `Get Free API Key` 다. 페이지 원문은 이렇게 적는다.

> We highly recommend that you use a legitimate email address… **By acquiring and using an Alpha Vantage API key, you agree to our Terms of Service and Privacy Policy.**

**이것이 발급을 사용자에게 넘기는 이유다.** §2.2 인용대로 **"Get Free API Key" 클릭 시점이 EULA 의 Effective Date** 다. 즉 키 발급은 조회 편의가 아니라 **법적 구속력 있는 계약의 체결**이고, 개인 이메일과 Organization 을 제출하는 행위다. 대리 수행할 성질이 아니다. 게다가 Organization 입력은 3.1 의 기준 ii 판단과 직접 맞물린다.

### 5.1 무료 티어 한도와 유료 플랜

`EARNINGS_ESTIMATES` 는 **premium 함수가 아니다.** 문서 마크업이 근거다.

```html
<h4 id="earnings-estimates">Earnings Estimates <span class="popular-label">Trending</span></h4>
```

같은 문서에서 premium 함수는 `<span class="premium-label">Premium</span>` 이 붙는다(Realtime Bulk Quotes, FX Intraday, VWAP 등). 이 함수에는 없다.

무료 한도는 `/support/` 와 `/premium/` 이 같은 수치를 적는다.

> We are pleased to provide free stock API service covering the majority of our datasets for **25 API requests per day** and unlimited API requests for **verified open-source or educational projects**.

**12 개사 × 1 회 = 12 회로 하루 25 회 안에 들어간다.** 재조회 여유까지 있다. 호출량은 우리 규모에서 문제가 되지 않는다.

**다만 한도 안에 든다는 것과 무료 티어를 쓸 자격이 있다는 것은 다르다.** 법인 내부 사용이라 §2.a.ii 로 상업 사용이고, 무료 라이선스는 personal, non-commercial 에 걸려 있다(3.1). **우리에게 유료 전환이 필요한 이유는 호출량이 아니라 사용 주체다.**

유료 플랜(참고, 개인/상업 구분 없이 분당 호출 수로만 나뉜다).

| 월간 | 연간 |
|---|---|
| 75 req/min $49.99/월 | 75 req/min $499/년 |
| 150 req/min $99.99/월 | 150 req/min $999/년 |
| 300 req/min $149.99/월 | 300 req/min $1499/년 |
| 600 req/min $199.99/월 | 600 req/min $1999/년 |
| 1200 req/min $249.99/월 | 1200 req/min $2499/년 |

**가격표에 개인 전용 티어가 따로 없다.** 개인 경로는 무료 티어인데 **우리는 거기 해당하지 않는다.** 상업 사용은 §2.a 말미대로 `premium@alphavantage.co` 문의이며, 위 가격표가 그 경로인지 별도 상업 계약인지는 확인하지 않았다.

## 6. 다른 공급원과의 비교

| 항목 | Alpha Vantage | Finnhub | Yahoo | api.nasdaq.com |
|---|---|---|---|---|
| robots.txt 제약 | **없음**(404) | — | — | **전면 Disallow** |
| 약관상 개인 사용 | **명시 허가**(§2.a) | 미확인 | personal use only(상류) | 자동·수동 모두 금지 |
| **우리(법인 내부) 사용 적격** | **아니오** — §2.a.ii 로 상업 사용 | 미확인 | **아니오** — 상류가 personal use only | 아니오 |
| 향후 분기 수 | **2** | 3 | 2 | 4 |
| 회계분기 식별 | **절대 날짜 + "fiscal quarter" 라벨** (의미 unknown) | `period` — 회계종료일 아님이 확인됨 | 상대 오프셋 — 특정 0/12 | `fiscalEnd` |
| currency | unknown | unknown | 있음 | 있음 |
| share_basis | unknown | unknown | unknown | unknown |
| accounting | unknown | unknown | unknown | unknown |
| asOf | unknown | unknown | unknown | unknown |
| 표본수 | **있음** | 없음 | 있음 | 있음 |
| min/max | **있음** | 없음 | 있음 | 있음 |
| 채택 가능 | **아니오 — 분기 2 개, basis 4 필드 부재** | 아니오 | 아니오 | 아니오(정책 배제) |

**Alpha Vantage 는 지금까지 조사한 무료 원천 중 `robots.txt` 지위가 가장 깨끗하다**(404 · 지시 자체가 없다). 배제의 **결정적 사유도 여전히 자료 부족**이다 — 향후 분기 2 개와 basis 4 필드 부재는 약관과 무관하다.

**약관 지위는 깨끗하지 않다.** 법인 내부 사용이 §2.a.ii 로 상업 사용이라 무료 티어 적격이 없다(3.1). 이 점에서 Yahoo 와 같은 자리에 선다 — 둘 다 개인 사용 조항 위에 서 있고 우리는 그 조항 밖이다. **초판이 '약관 지위가 가장 깨끗하다' 고 적은 것은 personal 전제에서였고, 그 전제가 바뀌었다.**

**두 축을 분리해 읽어야 한다.** `robots.txt` 지위는 사용 주체와 무관하게 깨끗하고(404), **약관 지위는 우리 사용 범위에서 깨끗하지 않다.** 앞 문단이 `robots.txt` 만 말한다고 해서 약관 쪽이 중립이라는 뜻이 아니다.

## 7. 확인된 것과 미확인인 것

### 7.1 저장 자료로 확인된 것

1. `www.alphavantage.co/robots.txt` 는 **404** 다. 크롤러 지시가 없다.
2. 약관 §2.a 가 **개인·비상업 사용을 명시적으로 부여**한다. 상업 사용 판정 기준 4 개를 함께 정의한다.
3. 약관 전문(4 쪽)에 자동 수집·스크래핑·크롤링 금지 문구가 **없다**(키워드 계수 0).
4. 약관 전문에 **파생 데이터·재배포·캐싱·보존 조항이 없다**(키워드 계수 0). 허가도 금지도 아니다.
5. 키 발급 클릭이 **EULA 의 Effective Date** 다(§3).
6. `EARNINGS_ESTIMATES` 는 **premium 함수가 아니다**(문서 마크업에 `premium-label` 부재).
7. 무료 한도는 **하루 25 회**다. 12 개사 조회에 충분하다.
8. 응답은 `horizon` + 절대 `date` 로 분기를 식별한다. **상대 오프셋이 아니다.**
9. 응답 18 필드에 `currency`·`share_basis`·`accounting`·`asOf` **키가 없다.**
10. 표본수와 low/high 는 **있다.**
11. 기준일 이후 분기 행이 **2 개**다(IBM). 같은 응답의 연간 행은 2 개다.
12. `demo` 키는 문서 예시 심볼에만 응답한다. **HTTP 200 이 커버리지 증거가 아니다.**
13. **우리 사용은 §2.a 의 무료 라이선스 범위 밖이다.** 법인 내부 사용이 기준 ii 에 해당해 `commercial use` 로 분류된다(3.1, 2026-09-10 사용자 확인).

### 7.2 미확인 — 추측하지 않고 남긴다

1. **12 개사 커버리지.** 무료 키 필요.
2. **"fiscal quarter" 의 `date` 가 회계분기 종료일인지.** 비달력 결산사(NVDA·MSFT·AAPL·ORCL)로만 갈린다. 무료 키 필요.
3. **분기 전망 2 개가 함수 전체의 성질인지 IBM 한 종목의 특성인지.** 무료 키 필요.
4. **currency·share_basis·accounting·asOf.** 응답에 없다. 공급사 문의 사항이며 Finnhub 과 같은 상태다.
5. ~~**약관 기준 ii(법인 명의·대리 여부)와 iv(금융업 종사·제휴).** 사용자 사실관계다.~~ **→ 해소(2026-09-10).** 기준 **ii 는 해당한다**(법인 내부 사용). 하나만 해당해도 상업 사용이므로 **iv 는 moot** 다. 결과는 무료 티어 적격 상실이며 3.1 에 적었다.
6. **파생 데이터와 저장·보존.** 이 약관이 침묵한다. 전문이 9,945 자로 짧아 별도 EULA·프리미엄 약관에 조항이 따로 있을 수 있다. **"이 문서에는 없다" 이지 "허용 조건이 없다" 가 아니다.** 채택하려면 서면 확인이 필요하다.
7. **Privacy Policy 본문.** 이번 범위는 robots.txt 와 ToS 였다. 읽지 않았다.
8. **TSM·BABA 같은 ADR/ADS 종목의 단위.** `share_basis` 가 없으므로 다른 원천과 같은 미해결 상태다.

### 7.3 권고

**지금 채택하지 않는다.** 사유가 둘로 늘었고, **결정적인 것은 여전히 자료다.**

1. **분기 전망 2 개** — F6(4 분기)에 미달. F6-H(2+2)에는 형식상 맞으나 F6-H 자체가 미승인이다.
2. **basis 4 필드 전무** — F6 의 실제 병목이다. 이 원천도 병목을 풀지 못한다.
3. **무료 티어 적격 상실** — 법인 내부 사용이라 §2.a.ii 로 상업 사용이다(3.1). 1·2 로 이미 부적격이었으므로 **실질 손실은 없다.**

**무료 키 발급 권고는 철회한다.** 초판은 "무료 키 1 개면 7.2 의 1·2·3 이 한 번에 해소된다" 며 사용자 결정으로 올렸다. 법인 내부 사용이 확정된 지금 **무료 키를 받는 것 자체가 §2.a 범위 밖**이다. 7.2 의 1·2·3 은 미확인으로 남기고, 이 원천을 다시 볼 일이 생기면 상업 계약 경로부터 본다. 그때 확인 순서는 이렇다.

1. 12 개사 응답 여부 (12 회)
2. NVDA·MSFT·AAPL·ORCL 의 `date` 가 각 사 회계분기 말과 맞는지 — 저장된 SEC 근거(`../f6h-source-batch-10/_derived/sec_quarter_ends.json`)와 대조하면 **추가 호출 없이** 판정된다
3. 12 개사 각각의 기준일 이후 분기 행 수

3.1 의 확인은 끝났다. **조직 내부 사용이라 상업 사용이고 경로는 `premium@alphavantage.co` 다.** 다만 향후 분기 2 개라는 사실이 그대로여서 그 문의를 낼 이유가 지금은 없다.

## 8. 재현 방법

```bash
cd worker/validation/av-source-11
python analyze_demo.py        # analysis-output.txt 와 같은 결과
```

**네트워크를 쓰지 않는다.** 읽는 것은 `_raw/` 뿐이다.

| 파일 | 내용 |
|---|---|
| `_raw/robots.txt` · `robots.headers.txt` | 404 응답 원문과 헤더 |
| `_raw/terms_of_service.pdf` · `.txt` | 약관 원본(4 쪽)과 추출본 |
| `_raw/documentation.html` | API 문서 전체 |
| `_raw/premium.html` · `support.html` | 가격표·무료 한도·키 발급 양식 |
| `_raw/EARNINGS_ESTIMATES.IBM.demo.json` | 문서 예시 응답(41 행) |
| `_raw/EARNINGS_ESTIMATES.NVDA.demo.json` | demo 키 제한 안내문 |
| `analyze_demo.py` · `analysis-output.txt` | 판정 스크립트와 결과 |

각 파일의 크기와 sha256 앞 16 자는 `analysis-output.txt` `[0]` 절에 있다. **크기·해시 모두 개행 정규화(CRLF→LF) 기준이다.** 파일 바이트를 그대로 재면 체크아웃마다 값이 갈린다 — `documentation.html` 이 작업 트리 1,059,116 B, 커밋 트리 1,079,968 B 로 갈렸다. 같은 내용이다. 승인 해시에 파일 바이트를 쓰지 않는 것과 같은 이유다(`../policy-12/REPORT.md` 5.1).
