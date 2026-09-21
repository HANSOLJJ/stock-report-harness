# Alpha Vantage EARNINGS_ESTIMATES 독립 조사 보고서 (AV-SOURCE-11B) 및 문서 정리 (RECORD-13)

- **조사일자**: 2026-09-10
- **조사주체**: C-13 독립 검증 세션 (worker 결과 미참조·독립 산출)
- **전제조건**: 산출물 사용 범위 **personal / internal only** (외부 대중 배포 없음) 확정
- **관련 커밋/브랜치**: `HANSOLJJ/C-13`
- **동반 실행 스크립트**: [verify_av_estimates.py](file:///C:/Users/noble/orca/workspaces/stock-report-harness/C-13/validation/av-source-11b/verify_av_estimates.py)
- **보존 원자료**: 
  - [av_earnings_estimates_ibm_demo.json](file:///C:/Users/noble/orca/workspaces/stock-report-harness/C-13/validation/av-source-11b/_raw/av_earnings_estimates_ibm_demo.json) (IBM 데모 응답 41행 원문)
  - [alphavantage_terms_of_service.txt](file:///C:/Users/noble/orca/workspaces/stock-report-harness/C-13/validation/av-source-11b/_raw/alphavantage_terms_of_service.txt) (이용약관 PDF 추출 전문)
  - [alphavantage_robots_txt_probe.txt](file:///C:/Users/noble/orca/workspaces/stock-report-harness/C-13/validation/av-source-11b/_raw/alphavantage_robots_txt_probe.txt) (robots.txt HTTP 404 확인 기록)
  - [alphavantage_premium_pricing_page.html](file:///C:/Users/noble/orca/workspaces/stock-report-harness/C-13/validation/av-source-11b/_raw/alphavantage_premium_pricing_page.html) (프리미엄 요금제 웹페이지 원본)

---

## 1. 종합 요약 (Executive Summary)

1. **전제 확정 (Personal / Internal Only)**:
   - 사용자가 리포트 산출물의 범위를 개인 및 내부 전용(personal / internal only)으로 확정함에 따라, 외부 일반 대중 재배포 라이선스 협상 이슈는 해소되었습니다.
2. **법적 / 약관 적격성 및 사용자 확인 항목 (ToS 2.a vs 2.a.ii)**:
   - `alphavantage.co/robots.txt`는 HTTP 404 (Not Found)로 크롤링 차단 규칙이 존재하지 않습니다 (보존 파일 확인).
   - 이용약관(ToS) Section 2.a 및 2.a.i에 따르면, **개인의 사적 투자 분석, 연구, 모니터링 목적(private and individual in nature)의 플랫폼 접근 및 이용은 명시적으로 허용**됩니다.
   - 단, Section 2.a.ii에 따라 **법인 또는 단체를 대리한 사용(on behalf of a corporation)은 상업적 사용(commercial use)으로 분류**됩니다. 본 저장소 커밋 작성자 도메인(`hansol.jung@digitalcoms.net`) 등 법인 연관성이 존재할 경우, 에이전트가 자의로 판단할 수 없으므로 **사용자의 주체 확인이 필수적이며, 법인 내부 사용 시 `premium@alphavantage.co` 문의가 필요**합니다.
   - Section 5.b에 의해 사용자가 생성한 2차 가공물(F6 점수 등)의 지식재산권은 사용자에게 귀속되며, 로컬 캐싱에 대한 명시적 금지 조항은 없습니다.
3. **API 티어 및 요금제**:
   - `EARNINGS_ESTIMATES`는 프리미엄 전용 태그가 없으며, 무료 API 키(25 calls/day)로도 조회 가능한 기본/트렌딩 엔드포인트입니다.
   - 25회/일 초과 시 유료 플랜은 최저 $49.99/월(Plan 15, 75 req/min)부터 시작하며, 별도의 '개인 전용 할인 플랜'은 존재하지 않습니다 (원문 HTML 보존 확인).
4. **F6 1:1 기준 대조 평가 (기술적 적격성 및 한계)**:
   - **커버리지 (unknown)**: 데모 키는 IBM 1개 종목만 응답하며, SpaceX 보통주인 `SPCX`를 포함한 타 11개사는 실증 미확인 상태로 unknown으로 둡니다. 특정 종목의 구조적 결측을 임의로 단정하지 않습니다.
   - **향후 분기 수 (IBM 기준 2개, 일반화 미확인)**: IBM 실측 기준 2026-09-10 이후 분기 전망치는 `2026-09-30`, `2026-12-31` 2개 분기만 존재하여 4분기 롤링에 미달합니다. 단, 이것이 API의 구조적 속성인지 IBM의 커버리지 특성인지는 미확인이므로, **무료 키 발급 후 확인할 최우선(1순위) 과제**로 설정합니다.
   - **메타데이터 결측 (unknown)**: 회계분기 식별자(`fiscalQuarter`), 통화(`currency`), 주식기준(`share_basis`), 회계기준(`accounting`), 스냅샷 시점(`asOf`), 과거 시점 재현성(PIT) 등 6개 핵심 메타데이터가 부재합니다.
   - **단기 컨센서스 이동 데이터 (고유 강점)**: 전면 PIT는 아니나, `_N_days_ago`(7/30/60/90일 전 평균치) 및 `revision_trailing`(7/30일 리비전 수)을 제공하여 타 무료 원천(Finnhub, Yahoo, api.nasdaq) 대비 실질적인 90일 컨센서스 이동 및 모멘텀 추적이 가능합니다.
5. **최종 결론**:
   - Alpha Vantage는 단기 컨센서스 변동 추적이라는 강점을 보유하고 있으나, **IBM 기준 향후 2분기 한계(4분기 NTM 요건 미달) 및 통화·회계기준 등 메타데이터 결측이라는 본질적 기술 결함으로 인해 단독 F6/F6-H 공급원으로 채택 불가**합니다.

---

## 2. robots.txt 및 이용약관(ToS) 원문 인용 및 정밀 분석

### 2.1. robots.txt 확인 결과
- **조회 URL**: `https://www.alphavantage.co/robots.txt` 및 `https://alphavantage.co/robots.txt`
- **조회 결과**: **HTTP 404 (Not Found)**
- **보존 원자료**: [alphavantage_robots_txt_probe.txt](file:///C:/Users/noble/orca/workspaces/stock-report-harness/C-13/validation/av-source-11b/_raw/alphavantage_robots_txt_probe.txt)
- **해석**: Alpha Vantage 웹서버는 `robots.txt` 파일을 서빙하지 않으며(404), 크롤러 및 자동 수집에 대한 기술적 배제 규칙을 공시하지 않고 있습니다.

### 2.2. 이용약관(Terms of Service) 전문 검토
Alpha Vantage 이용약관(`https://www.alphavantage.co/terms_of_service/`, [alphavantage_terms_of_service.txt](file:///C:/Users/noble/orca/workspaces/stock-report-harness/C-13/validation/av-source-11b/_raw/alphavantage_terms_of_service.txt))을 추출·분석한 결과는 다음과 같습니다.

#### (a) 자동 수집 및 프로그래매틱 접근 (Automated Collection / API Access)
> **Section 3. End User License Agreement (“Agreement”)**  
> *"Alpha Vantage hereby grants User a non-exclusive, non-sublicensable, non-transferable, non-assignable, revocable license to access and utilize the Alpha Vantage Platform pursuant to the terms of this Agreement. Access and utilization and acceptance of the EULA is effective as of the date User clicks 'Get Free API Key' (the 'Effective Date')."*

> **Section 4. Use Restrictions**  
> *"You will not, directly or indirectly, reverse engineer, decompile, disassemble or otherwise attempt to discover the source code, object code or underlying structure, ideas, know-how or algorithms relevant to the Alpha Vantage Platform, Content or any software, documentation or data related to this Agreement, the Alpha Vantage Platform and developed Content. User shall only upload Content that they are authorized to share and upload onto the Alpha Vantage Platform."*

- **해석**: API 키 발급을 통해 공식 API 엔드포인트로 프로그래매틱 접근을 수행하는 것은 EULA에 의해 명시적으로 허가됩니다. 단, 플랫폼의 역공학이나 소스코드 추출은 금지됩니다.

#### (b) 개인 / 내부용 사용 범위 (Personal / Non-commercial Use)
> **Section 2. Grant of License**  
> *"a. Alpha Vantage grants the right to install, use, access, display and run the software on any computer or mobile device, where applicable, that you own or control, for personal, non-commercial use, unless you and Alpha Vantage have agreed otherwise in writing, and provided that you comply with all terms and conditions of the End User License Agreement (see below). Usage falls under “commercial use” if any of the following criteria apply to you:*  
> *i. You intend to use the Alpha Vantage Platform for any purpose that goes beyond investment analysis, research, testing, monitoring, and any other activities that are private and individual in nature*  
> *ii. You are using the Alpha Vantage Platform as or on behalf of a corporation, firm, partnership, trust or any other association and not as an individual.*  
> *iii. You plan to use or provide information accessed through the Alpha Vantage Platform as part of any type of commercial activity that allows individuals or entities other than User to access information directly or indirectly even if the scope of such activity falls outside of the securities industry.*  
> *iv. You are currently employed or have an active affiliation with a financial planning advisor, insurance company, investment advisor, investment bank, money manager, registered representative, securities broker-dealer, or any owner, partner, affiliate or associated person of the preceding.*  
> *If you are interested in using the Alpha Vantage Platform for commercial purposes, please contact us at: premium@alphavantage.co"*

- **해석**:
  - 이용약관 2.a는 **"개인적, 비상업적 사용(personal, non-commercial use)"**에 대한 명시적 라이선스를 부여합니다.
  - 상업적 사용(commercial use) 기준 4대 조항 중 2.a.i는 사적이고 개인적인 투자 분석/연구를 허용 범위로 정의합니다.
  - 그러나 **2.a.ii는 '법인, 회사, 파트너십, 신탁 또는 기타 단체로서 혹은 이를 대리하여 사용하는 경우(as or on behalf of a corporation... and not as an individual)'를 명시적으로 상업적 사용으로 규정**합니다.
  - 사용자가 확정한 "personal / internal only" 전제에서, **개인이 순수 사적 연구로 사용하는 "personal" 영역은 2.a에 부합하나, 법인의 조직적 "internal" 영역은 2.a.ii에 저촉될 위험**이 있습니다.

#### (c) 2차 가공물 (Derivative Data Calculation)
> **Section 5. Intellectual Property Rights**  
> *"a. By Alpha Vantage. Alpha Vantage shall retain all right, title and interest to the intellectual property rights to the Alpha Vantage Platform, including, but not limited to, the HTML and DHTML files, Java Script files, UI elements, graphics files, visual comps, animation files, database and files, technology, scripts and programs (in both object and source code form), and any other Content developed by Alpha Vantage to facilitate the performance of its obligations under this Agreement.*  
> *b. By User. User shall retain all right, title and interest to the intellectual property rights to its data, and any other Content developed by User."*

- **해석**: Alpha Vantage로부터 수집한 수치를 바탕으로 F6 점수, 성장률, 팩터 스코어 등 2차 파생 데이터를 계산하고 산출물을 생성하는 것은 Section 5.b에 따라 **사용자가 해당 가공 콘텐츠의 지식재산권을 보유**합니다.

#### (d) 보관 / 캐싱 / 영구 보존 (Storage, Caching, Retention)
- **약관 명시 여부**: ToS 전문(Section 1 ~ 21)에 로컬 캐싱이나 데이터 영구 보존을 금지하는 별도 조항은 존재하지 않습니다.
- **해석**: 제3자에게 원천 데이터를 재배포(redistribution)하지 않고 개인 연구 목적으로 로컬 저장·캐싱하는 것은 약관상 위반되지 않습니다.

### 2.3. [사용자 확인 필수 항목] 개인(Individual) 자격 vs 법인(Corporation) 내부 사용 구분 및 조치

- **쟁점 배경**: 사용자가 지정한 전제는 "personal / internal only"입니다. 여기서 "personal(개인)"과 "internal(내부)"은 약관상 법적 성격이 완전히 갈립니다.
  - **순수 개인 사용 (Individual Personal Use)**: 사용자가 개인 투자자/연구자 자격으로 사적 분석(2.a.i)을 수행하는 경우 → **Section 2.a에 따라 무료/표준 라이선스 완전 허용**.
  - **법인 내부 사용 (Corporate Internal Use)**: 사용자가 회사, 법인, 연구기관 등의 업무 또는 소속 조직의 내부 연구/모니터링을 위해 사용하는 경우 → **Section 2.a.ii에 따라 Commercial Use로 자동 분류**.
- **식별 정황**: 본 저장소의 git 커밋 author 메일 주소가 `hansol.jung@digitalcoms.net`으로 기업 법인 도메인입니다. 이 자체만으로 법인 대리 사용을 확정할 수는 없으나, 약관 2.a.ii 저촉 위험을 배제할 수 없습니다.
- **조치 요구**:
  1. 본 사용 주체의 법적 지위(순수 개인 자격 vs 법인/단체 대리 자격)는 AI 에이전트가 임의로 단정할 수 없으며, **사용자(오너)의 직접 확인이 필수적**입니다.
  2. 만약 **법인 또는 단체 명의의 내부 연구 목적에 해당할 경우**, 약관 Section 2 말미의 안내에 따라 **`premium@alphavantage.co`로 공식 상용 라이선스 문의 및 서면 합의(agreed otherwise in writing)를 진행해야 함**을 명시합니다.

---

## 3. 무료 vs 유료 티어 및 요금제 구조

### 3.1. 무료 티어 (Standard Free Tier)
- **기본 한도**: 일일 25회 API 요청 (`25 requests per day`), 분당 5회 (`5 requests per minute`).
- **EARNINGS_ESTIMATES 엔드포인트 포함 여부**:
  - 공식 문서(`https://www.alphavantage.co/documentation/#earnings-estimates`)에서 해당 엔드포인트는 `<span class="popular-label">Trending</span>`으로 분류되어 있습니다.
  - S&P 500 OHLC, Realtime Options 등 유료 전용 엔드포인트에 명시된 `<span class="premium-label">Premium</span>` 라벨이 없습니다.
  - 파라미터 안내에 *"Claim your free API key here"* 링크가 제공되므로, **무료 발급 키로 조회가 가능**합니다.
  - 단, 12개 종목 유니버스를 일괄 조회할 경우 일일 25회 한도 중 12회가 1회 실행으로 소진됩니다.

### 3.2. 프리미엄 요금제 (Premium Membership Plans)
일일 25회 한도를 초과하거나 실시간 데이터 등이 필요할 경우의 유료 플랜 구조(`https://www.alphavantage.co/premium/`, [alphavantage_premium_pricing_page.html](file:///C:/Users/noble/orca/workspaces/stock-report-harness/C-13/validation/av-source-11b/_raw/alphavantage_premium_pricing_page.html)):

| 플랜명 | 분당 요청 한도 | 미국 시장 데이터 | 옵션 데이터 | 월간 요금 | 연간 요금 (2개월 무료) |
|---|---|---|---|---|---|
| **Plan 15** | 75 req/min | 15분 지연 | End-of-day | $49.99 / 월 | $499 / 년 |
| **Plan 60** | 150 req/min | 실시간 (Realtime) | End-of-day | $99.99 / 월 | $999 / 년 |
| **Plan 120** | 300 req/min | 실시간 (Realtime) | End-of-day | $149.99 / 월 | $1,499 / 년 |
| **Plan 360** | 600 req/min | 실시간 (Realtime) | Realtime | $199.99 / 월 | $1,999 / 년 |
| **Plan 600** | 1200 req/min | 실시간 (Realtime) | Realtime | $249.99 / 월 | $2,499 / 년 |

- **개인 전용 할인 플랜**: 존재하지 않으며, Plan 15($49.99/월)가 최저 유료 플랜입니다. 일일 호출 25회 이내의 개인 사용자는 무료 티어가 기본 제공됩니다.

---

## 4. 무료 API 키 발급 절차 안내 (직접 발급 미수행)

본 조사는 지침에 따라 **직접 API 키를 신청·발급하지 않고 발급 절차 및 요구 항목만 정리**했습니다.

1. **신청 페이지 접속**: `https://www.alphavantage.co/support/#api-key`
2. **입력 요구 항목**:
   - `Which of the following best describes you?` (직업 선택 드롭다운):
     - 옵션: `Investor`, `Software Developer`, `Educator`, `Student`, `I am from the Trading Agents project on Github`, `Other`
   - `Organization (e.g. company, university, etc.)`: 소속 기관명 입력 (필수)
   - `Email`: 키를 수신할 이메일 주소 입력 (필수)
3. **제출 버튼**: `Get Free API Key` 클릭
4. **법적 효력**: 버튼 클릭 시 Alpha Vantage EULA 및 이용약관에 동의하는 것으로 간주됨 (ToS Section 3).
5. **발급 결과**: 화면 및 이메일로 고유 문자열 API 키 즉시 제공 (평생 무료 액세스, 25 calls/day).

---

## 5. 1:1 F6 기준 정밀 대조 결과표 (11개 항목)

Alpha Vantage `function=EARNINGS_ESTIMATES`의 실제 데모 응답(`symbol=IBM`, [av_earnings_estimates_ibm_demo.json](file:///C:/Users/noble/orca/workspaces/stock-report-harness/C-13/validation/av-source-11b/_raw/av_earnings_estimates_ibm_demo.json)) 및 공식 API 문서를 바탕으로 F6 요구조건을 정밀 대조했습니다.

| 번호 | F6 요구 항목 | Alpha Vantage 응답 현황 | 판정 | 근거 및 상세 분석 |
|---|---|---|---|---|
| 1 | **12개사 커버리지** | 데모 키 환경에서는 `IBM`만 응답. 타 11개사(SpaceX 보통주 `SPCX` 포함)는 실증 미확인. | **unknown** | 데모 키로 타 종목 호출 시 안내 메시지만 반환됨. 개별 기업 11개사는 일반적인 주식 기본 데이터 커버리지에 포함될 가능성이 있으나 현재 실증되지 않았으므로 단정하지 않고 unknown으로 분류. (SPCX는 NASDAQ 상장 SpaceX 보통주로 ETF가 아니며 타 원천에서 분기 실적/전망 존재 확인됨). |
| 2 | **향후 분기 수 (4개 여부)** | 2026-09-10 기준 IBM 분기 전망치는 `2026-09-30`, `2026-12-31` 2개 분기만 존재. 12개사 일반화는 미확인. | **IBM 1종목 기준 2개 (12개사 일반화 미확인, 키 발급 후 확인 1순위)** | IBM 데모 응답 기준 2026-09-10 이후 분기 전망치는 2개 분기만 제공되며 2027년은 연간(fiscal year) 행만 제공됨. 단, 이것이 API 전체의 구조적 분기 제한인지 IBM 단일 종목의 애널리스트 전망 특성인지는 1개 종목으로 단정할 수 없음. 12개사 전원에 대한 일반화 여부는 미확인이며, 향후 비데모 키 발급 시 확인할 최우선(1순위) 과제임. |
| 3 | **회계분기 식별 필드** | `date` (종료일)와 `horizon` ("fiscal quarter")만 제공. | **unknown / 부재** | `fiscalQuarter`, `quarter` 등 명시적 분기 번호(Q1/Q2/Q3/Q4) 필드가 없음. 사용자가 일자를 바탕으로 역산해야 함. |
| 4 | **통화 (currency)** | 응답 내 통화 필드 일체 부재. | **unknown / 부재** | `currency`, `financialCurrency` 등이 전혀 제공되지 않아 암묵적 USD로 가정해야 하므로, TSM/BABA 등 해외 ADR 통화 불일치 검증 불가. |
| 5 | **주식 기준 (share_basis)** | EPS의 희석(Diluted) / 기본(Basic) 구분 없음. | **unknown / 부재** | `eps_estimate_average` 등 수치만 제공되며 주식수 기준 명시 없음. |
| 6 | **회계 기준 (accounting)** | GAAP / Non-GAAP(Adjusted) 구분 없음. | **unknown / 부재** | 컨센서스가 조정 EPS인지 GAAP EPS인지 명시적인 메타데이터 없음. |
| 7 | **asOf 스냅샷 시점** | 생성/스냅샷 타임스탬프 부재. | **unknown / 부재** | 루트 및 항목에 `asOf`, `last_updated` 필드 없음. (단, 90일 구간의 컨센서스 이동 데이터는 11번 항목 참조). |
| 8 | **표본수 (sample size)** | 애널리스트 수 제공됨. | **제공 (충족)** | `eps_estimate_analyst_count` (예: 19.0000), `revenue_estimate_analyst_count` (예: 16.00) 제공. |
| 9 | **min / max** | 최소 및 최대 추정치 제공됨. | **제공 (충족)** | `eps_estimate_low`, `eps_estimate_high`, `revenue_estimate_low`, `revenue_estimate_high` 제공. |
| 10 | **과거 시점 재현성 (PIT)** | 엔드포인트 파라미터에 과거 시점(as_of) 쿼리 부재. | **unknown / 불가** | 임의의 과거 날짜 기준으로 당시 컨센서스를 재현하는 PIT 파라미터가 없으며, 확정 분기별 최종 추정치 고정 시계열만 반환. |
| 11 | **단기 컨센서스 변동 추적 (`_N_days_ago`, `revision`)** | 7/30/60/90일 전 평균치 및 7/30일 상향/하향 리비전 건수 전 분기 제공. | **제공됨 (고유 강점 / 긍정 항목)** | 전면 PIT는 아니나, `eps_estimate_average_7/30/60/90_days_ago`와 `eps_estimate_revision_up/down_trailing_7/30_days`를 통해 90일 구간의 컨센서스 이동 및 모멘텀 추적 가능. Finnhub, Yahoo, 무료 api.nasdaq(asOf 전체 null) 등 타 무료 공급원에서 전혀 제공되지 않은 실질적 변동 데이터임. |

---

## 6. RECORD-13 문서 정리 내역

### 6.1. 나스닥 공식 서한 초안 폐기 표기 (`validation/nasdaq-license-c13-01/REPORT.md`)
- **수정 위치**: 제7절 ("공식 문의 서한 초안") 및 제9.2절 ("단기 실행 과제")
- **반영 내용**:
  1. **초안 폐기(Revoked) 경고 박스 추가**: 일자(2026-09-10)와 함께 공식 폐기 명시.
  2. **폐기 사유 2건 명시**:
     - 사유 1: 사용자가 산출물 범위를 'personal / internal only'로 최종 확정함에 따라 외부 재배포 라이선스 협상 자체가 불필요해짐.
     - 사유 2: 기존 초안에 실제 12개사 유니버스(`PLTR`, `SPCX` - SpaceX 보통주) 대신 잘못된 티커(`AVGO`, `AMD`)가 기재되어 있었음.
  3. **조건부 가격/보존 기간 재확인**: 나스닥 공식 답변이 없는 상태에서의 가격 정책 및 보존 기간은 잠정치임을 재강조.

### 6.2. 야후 탈락 사유 기술적 한계 우선 명시 (`validation/f6-h-sources-02/REPORT.md`)
- **수정 위치**: 제4절 (Stage 4 종합 판정) 및 제6.3절 (Yahoo 및 finnhub 탈락 원인)
- **반영 내용**:
  1. 야후의 탈락 사유는 단순히 'v1.6 allowlist 미등재'나 권리 라이선스 문제 이전에, **회계분기창 특정 불가(0/12) 및 2분기(0q, +1q) 한정이라는 본질적인 기술적·구조적 부적격성 때문**임을 최우선 사유로 명시.
  2. 사용자의 '개인/내부용' 전제 확정으로 인해 상용 라이선스 우려는 완화되었으나, **이러한 기술적 결함은 개인 사용 여부와 무관하게 동일하게 적용되므로 공급원 배제 결론은 불변**임을 명확히 기술.

---

## 7. 결론 및 종합 제언

1. **AV-SOURCE-11B 독립 조사 결과**:
   - Alpha Vantage는 `_N_days_ago` 및 `revision_trailing` 필드를 통해 **90일 단기 컨센서스 이동과 모멘텀을 추적할 수 있다는 뚜렷한 고유 강점**을 보유하고 있습니다.
   - 그러나 IBM 실측 기준 **향후 분기 전망이 2분기에 불과하여 F6의 4분기 롤링(NTM) 요구에 미달**하며(12개사 일반화 여부는 키 발급 후 확인 1순위 과제), 통화·회계분기 식별자·asOf 등 메타데이터가 결측되어 있어 현재 상태에서 **단독 F6/F6-H 공급원 채택은 불가**합니다.
2. **사용자 확인 필수 사항 (ToS 2.a.ii)**:
   - 사용자가 개인 자격으로 연구하는 경우 약관상 허용되나, 법인/기업 명의의 내부 연구인 경우 상업적 사용으로 분류될 수 있으므로, 사용자의 주체 확인 및 필요 시 `premium@alphavantage.co` 문의가 필요합니다.
3. **근거 자료 4종 완비**:
   - 이용약관 전문, robots.txt 404 확인 기록, 프리미엄 요금제 웹페이지, IBM 데모 응답 원본 등 4종의 근거 원자료를 모두 `_raw` 디렉토리에 보존하여 검증 가능성을 확보했습니다.
4. **RECORD-13 정리 완결**:
   - 나스닥 서한 초안 폐기 처리 및 야후 탈락의 기술적 원인 중심 서술 재정리가 완료되었습니다.
5. **독립성 유지**:
   - 본 조사는 worker의 진행 상황이나 결과를 일체 참조하지 않고 독자적인 자료 수집, 약관 분석, 데모 데이터 파싱 및 검증 스크립트 실행을 통해 산출되었습니다.
