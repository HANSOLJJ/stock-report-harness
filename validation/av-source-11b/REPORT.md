# Alpha Vantage EARNINGS_ESTIMATES 독립 조사 보고서 (AV-SOURCE-11B) 및 문서 정리 (RECORD-13)

- **조사일자**: 2026-09-10
- **조사주체**: C-13 독립 검증 세션 (worker 결과 미참조·독립 산출)
- **전제조건**: 산출물 사용 범위 **personal / internal only** (외부 대중 배포 없음) 확정
- **관련 커밋/브랜치**: `HANSOLJJ/C-13`
- **동반 실행 스크립트**: [verify_av_estimates.py](file:///C:/Users/noble/orca/workspaces/stock-report-harness/C-13/validation/av-source-11b/verify_av_estimates.py)
- **보존 원자료**: 
  - [av_earnings_estimates_ibm_demo.json](file:///C:/Users/noble/orca/workspaces/stock-report-harness/C-13/validation/av-source-11b/_raw/av_earnings_estimates_ibm_demo.json)
  - [alphavantage_terms_of_service.txt](file:///C:/Users/noble/orca/workspaces/stock-report-harness/C-13/validation/av-source-11b/_raw/alphavantage_terms_of_service.txt)

---

## 1. 종합 요약 (Executive Summary)

1. **전제 확정 (Personal / Internal Only)**:
   - 사용자가 리포트 산출물의 범위를 개인 및 내부 전용(personal / internal only)으로 확정함에 따라, 외부 재배포나 상용 라이선스 협상 이슈가 배제되었습니다.
2. **법적 / 약관 적격성 (Legal & ToS)**:
   - `alphavantage.co/robots.txt`는 HTTP 404 (Not Found)로 크롤링 차단 규칙이 존재하지 않습니다.
   - 이용약관(ToS) Section 2.a 및 2.a.i에 따르면, **개인의 사적 투자 분석, 연구, 모니터링 목적(private and individual in nature)의 플랫폼 접근 및 이용은 명시적으로 허용**됩니다. 
   - Section 5.b에 의해 사용자가 생성한 2차 가공물(F6 점수 등)의 지식재산권은 사용자에게 귀속됩니다.
   - 로컬 캐싱 및 데이터 보관에 대한 명시적 금지 조항은 없습니다.
3. **API 티어 및 요금제**:
   - `EARNINGS_ESTIMATES`는 프리미엄 전용 태그가 없으며, 무료 API 키(25 calls/day)로도 조회 가능한 기본/트렌딩 엔드포인트입니다.
   - 25회/일 초과 시 유료 플랜은 최저 $49.99/월(Plan 15, 75 req/min)부터 시작하며, 별도의 '개인 전용 할인 플랜'은 존재하지 않습니다.
4. **F6 1:1 기준 대조 평가 (기술적 적격성 결함)**:
   - 10개 평가 항목 중 **표본수(O)**, **min/max(O)** 2개 항목만 충족합니다.
   - **향후 분기 수가 2분기(2026-09-30, 2026-12-31)에 불과하여 F6의 4분기(NTM) 요구를 미달**합니다.
   - 회계분기 식별자(`fiscalQuarter`), 통화(`currency`), 주식기준(`share_basis`), 회계기준(`accounting`), 스냅샷 시점(`asOf`), 과거 시점 재현성(PIT) 등 **핵심 메타데이터 8개 항목이 부재(unknown)**합니다.
5. **최종 결론**:
   - 개인/내부용 전제에서 약관상 접근 가능성은 열려 있으나, **향후 4분기 미제공(2분기 한정) 및 메타데이터 결측이라는 본질적 기술 결함으로 인해 Alpha Vantage EARNINGS_ESTIMATES는 단독 F6/F6-H 공급원으로 채택 불가**합니다.

---

## 2. robots.txt 및 이용약관(ToS) 원문 인용 및 정밀 분석

### 2.1. robots.txt 확인 결과
- **조회 URL**: `https://www.alphavantage.co/robots.txt` 및 `https://alphavantage.co/robots.txt`
- **조회 결과**: **HTTP 404 (Not Found)**
- **해석**: Alpha Vantage 웹사이트는 별도의 `robots.txt` 파일을 서빙하지 않으며, 크롤러에 대한 엔드포인트 차단 규칙을 기술적으로 공시하지 않고 있습니다.

### 2.2. 이용약관(Terms of Service) 전문 검토
Alpha Vantage 이용약관(`https://www.alphavantage.co/terms_of_service/`, 4페이지 PDF 문서)을 추출·분석한 결과는 다음과 같습니다.

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
  - 상업적 사용(commercial use)의 배제 조건 중 2.a.i는 *"사적이고 개인적인 성격의 투자 분석, 연구, 테스팅, 모니터링(investment analysis, research, testing, monitoring, and any other activities that are private and individual in nature)"*을 명시하고 있습니다.
  - 사용자가 확정한 본 과제의 범위가 **"개인 연구 및 사적 투자 분석용(personal/internal only)"**이므로, 사용자가 개인(individual) 자격으로 수행하고 제3자 배포(2.a.iii)나 금융사 대리(2.a.iv)가 없는 한, **무료 또는 표준 라이선스 범위 내에서 완전하게 허용**됩니다.

#### (c) 2차 가공물 (Derivative Data Calculation)
> **Section 5. Intellectual Property Rights**  
> *"a. By Alpha Vantage. Alpha Vantage shall retain all right, title and interest to the intellectual property rights to the Alpha Vantage Platform, including, but not limited to, the HTML and DHTML files, Java Script files, UI elements, graphics files, visual comps, animation files, database and files, technology, scripts and programs (in both object and source code form), and any other Content developed by Alpha Vantage to facilitate the performance of its obligations under this Agreement.*  
> *b. By User. User shall retain all right, title and interest to the intellectual property rights to its data, and any other Content developed by User."*

- **해석**: Alpha Vantage로부터 수집한 수치를 바탕으로 F6 점수, 성장률, 팩터 스코어 등 2차 파생 데이터를 계산하고 산출물을 생성하는 것은 Section 5.b에 따라 **사용자가 해당 가공 콘텐츠의 지식재산권을 보유**합니다.

#### (d) 보관 / 캐싱 / 영구 보존 (Storage, Caching, Retention)
- **약관 명시 여부**: ToS 전문(Section 1 ~ 21)에 로컬 캐싱이나 데이터 영구 보존을 금지하는 별도 조항은 존재하지 않습니다.
- **해석**: 제3자에게 원천 데이터를 재배포(redistribution)하지 않고 개인 연구 목적으로 로컬 저장·캐싱하는 것은 약관상 위반되지 않습니다.

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
일일 25회 한도를 초과하거나 실시간 데이터 등이 필요할 경우의 유료 플랜 구조(`https://www.alphavantage.co/premium/`):

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

## 5. 1:1 F6 기준 정밀 대조 결과표 (10개 항목)

Alpha Vantage `function=EARNINGS_ESTIMATES`의 실제 데모 응답(`symbol=IBM`) 및 공식 API 문서를 바탕으로 F6 요구조건 10개 항목을 정밀 대조했습니다.

| 번호 | F6 요구 항목 | Alpha Vantage 응답 현황 | 판정 | 근거 및 상세 분석 |
|---|---|---|---|---|
| 1 | **12개사 커버리지** | 데모 키 환경에서는 `IBM`만 응답. 비데모 키 필요. SPCX(ETF) 결측 예상. | **unknown** | 데모 키로 타 종목 호출 시 안내 메시지만 반환됨. 개별 기업 11개사는 커버리지 지원 예상되나 실증 미확인, SPCX(ETF)는 실적 추정치가 원천적으로 없는 구조적 결측 예상. |
| 2 | **향후 분기 수 (4개 여부)** | 2026-09-10 기준 분기 전망치는 `2026-09-30`, `2026-12-31` **2개 분기만 존재**. | **불충족 (2개 / 4개 미달)** | 2027년 분기 추정치는 전혀 제공되지 않으며 2027-12-31 연간(fiscal year) 추정치만 제공됨. F6의 4분기 롤링(NTM) 요구 미달. |
| 3 | **회계분기 식별 필드** | `date` (종료일)와 `horizon` ("fiscal quarter")만 제공. | **unknown / 부재** | `fiscalQuarter`, `quarter` 등 명시적 분기 번호(Q1/Q2/Q3/Q4) 필드가 없음. 사용자가 일자를 바탕으로 역산해야 함. |
| 4 | **통화 (currency)** | 응답 내 통화 필드 일체 부재. | **unknown / 부재** | `currency`, `financialCurrency` 등이 전혀 제공되지 않아 암묵적 USD로 가정해야 하므로, TSM/BABA 등 해외 ADR 통화 불일치 검증 불가. |
| 5 | **주식 기준 (share_basis)** | EPS의 희석(Diluted) / 기본(Basic) 구분 없음. | **unknown / 부재** | `eps_estimate_average` 등 수치만 제공되며 주식수 기준 명시 없음. |
| 6 | **회계 기준 (accounting)** | GAAP / Non-GAAP(Adjusted) 구분 없음. | **unknown / 부재** | 컨센서스가 조정 EPS인지 GAAP EPS인지 명시적인 메타데이터 없음. |
| 7 | **asOf 스냅샷 시점** | 생성/스냅샷 타임스탬프 부재. | **unknown / 부재** | 루트 및 항목에 `asOf`, `last_updated` 필드 없음. 7일/30일/60일/90일 전 평균치만 제공. |
| 8 | **표본수 (sample size)** | 애널리스트 수 제공됨. | **제공 (충족)** | `eps_estimate_analyst_count` (예: 19.0000), `revenue_estimate_analyst_count` (예: 16.00) 제공. |
| 9 | **min / max** | 최소 및 최대 추정치 제공됨. | **제공 (충족)** | `eps_estimate_low`, `eps_estimate_high`, `revenue_estimate_low`, `revenue_estimate_high` 제공. |
| 10 | **과거 시점 재현성 (PIT)** | 엔드포인트 파라미터에 과거 시점(as_of) 쿼리 부재. | **unknown / 불가** | 임의의 과거 날짜 기준으로 당시 컨센서스를 재현하는 PIT 파라미터가 없으며, 확정 분기별 최종 추정치 고정 시계열만 반환. |

---

## 6. RECORD-13 문서 정리 내역

### 6.1. 나스닥 공식 서한 초안 폐기 표기 (`validation/nasdaq-license-c13-01/REPORT.md`)
- **수정 위치**: 제7절 ("공식 문의 서한 초안") 및 제9.2절 ("단기 실행 과제")
- **반영 내용**:
  1. **초안 폐기(Revoked) 경고 박스 추가**: 일자(2026-09-10)와 함께 공식 폐기 명시.
  2. **폐기 사유 2건 명시**:
     - 사유 1: 사용자가 산출물 범위를 'personal / internal only'로 최종 확정함에 따라 외부 재배포 라이선스 협상 자체가 불필요해짐.
     - 사유 2: 기존 초안에 실제 12개사 유니버스(`PLTR`, `SPCX`) 대신 잘못된 티커(`AVGO`, `AMD`)가 기재되어 있었음.
  3. **조건부 가격/보존 기간 재확인**: 나스닥 공식 답변이 없는 상태에서의 가격 정책 및 보존 기간은 잠정치임을 재강조.

### 6.2. 야후 탈락 사유 기술적 한계 우선 명시 (`validation/f6-h-sources-02/REPORT.md`)
- **수정 위치**: 제4절 (Stage 4 종합 판정) 및 제6.3절 (Yahoo 및 finnhub 탈락 원인)
- **반영 내용**:
  1. 야후의 탈락 사유는 단순히 'v1.6 allowlist 미등재'나 권리 라이선스 문제 이전에, **회계분기창 특정 불가(0/12) 및 2분기(0q, +1q) 한정이라는 본질적인 기술적·구조적 부적격성 때문**임을 최우선 사유로 명시.
  2. 사용자의 '개인/내부용' 전제 확정으로 인해 상용 라이선스 우려는 완화되었으나, **이러한 기술적 결함은 개인 사용 여부와 무관하게 동일하게 적용되므로 공급원 배제 결론은 불변**임을 명확히 기술.

---

## 7. 결론 및 종합 제언

1. **AV-SOURCE-11B 독립 조사 결과**:
   - Alpha Vantage는 개인/내부용 범위에서 이용약관상 합법적인 접근이 가능하지만, **F6-H의 필수 요건인 4분기 롤링 전망치를 충족하지 못하고(현재 시점 2분기만 제공)**, 통화·회계분기 식별자·asOf 등 메타데이터가 결측되어 있어 신뢰성 있는 F6 산출이 불가능합니다.
2. **RECORD-13 정리 완료**:
   - 나스닥 서한 초안 폐기 처리 및 야후 탈락의 기술적 원인 중심 서술 재정리가 완료되었습니다.
3. **독립성 유지**:
   - 본 조사는 worker의 진행 상황이나 결과를 일체 참조하지 않고 독자적인 웹 조사, 약관 추출, 데모 데이터 분석 및 자체 검증 스크립트 실행을 통해 도출되었습니다.
