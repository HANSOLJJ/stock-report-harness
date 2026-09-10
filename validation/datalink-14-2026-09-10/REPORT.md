# DATALINK-14 — Nasdaq Data Link 셀프서비스 구독 조건 확인

- 지시 원문: `msg_c1e19a31751a` (run `run_1243c2a83479`)
- 기준일: 2026-09-10. 조회 시각은 `probe-log.txt` 와 `raw/` 스냅샷 참조
- 대상 호스트: `data.nasdaq.com` (무료 `api.nasdaq.com` 과 **별도 상품·별도 약관**. 이번 조사에서 `api.nasdaq.com` 은 한 번도 호출하지 않았다)

## 0. 결론 — 세 질문에 대한 답

**셀프서비스로 가능한가: 확인하지 못했다. 확인하려면 계정 생성이 필요한데 그것이 금지 행위라 여기서 멈춘다.** 다만 방향을 가르는 신호는 양쪽으로 갈린다. 상품 페이지에는 Contact Sales 버튼이 없고 "Log in with your Nasdaq Data Link account to view pricing information" 과 Login/Sign Up 버튼만 있다. 즉 **가격이 영업 문의가 아니라 무료 계정 뒤에 있다.** 반대로 실제 계약서인 Data License Terms and Conditions 는 **§1.1 에서 "mutual executed order form" 으로 라이선스를 부여**하고, §4.1 요금도 Order Form 에 적히며, §6.1 기본 기간은 **1년 자동갱신에 해지 90일 전 통지**, §8 은 Nasdaq 이 **연 1회 고객 사업장·컴퓨터·인력에 접근하는 감사권**을 갖는다. 이건 클릭 동의형이 아니라 계약형 문구다. 로그인 후 화면이 자동 결제로 이어지는지 영업으로 넘기는지는 **공개 경로에서 판별 불가**다.

**얼마인가: unknown.** `data.nasdaq.com` 어디에도 표시된 가격이 없다. ZEE·ZEEH 는 물론 대조군으로 확인한 Sharadar 번들(SFA)까지 동일하게 "로그인하면 가격을 볼 수 있다" 문구만 나온다. **개인·내부 티어의 존재 여부, 무료 티어 포함 여부, 12종목 소규모 비례 과금 여부도 전부 unknown 이다.** 추정치를 넣지 않았고, 기존 보고서의 월 100~300 달러는 근거로 쓰지 않았다.

**ZACKS/EEH 가 asOf 를 주는가: 그렇다.** `obs_date` 컬럼이 있고, 정의는 **"Observation date (YYYY-MM-DD) corresponding to the date on which contributed estimates were changed and the consensus was revised"** 이며 **필터 가능하고 기본키**다. 이력은 **1979년 1월부터**, 미래 기간은 **today 기준 최대 4년**, 리포팅 지연 1일이다. 무료 `api.nasdaq.com` 이 12개사 전부 `asOf`=null 이라 불가능했던 과거 시점 재현이 **EEH 에서는 구조적으로 가능하다.**

덧붙여 예상 밖의 수확이 둘 있다. 첫째, **F6 이 요구하는 회계·주식 기준이 문서로 명시돼 있다** — BNRI 는 "diluted Earnings Per Share before non-recurring items and including employee stock options expenses". NTM-SOURCE-05 가 무료 경로에서 끝내 확정하지 못한 두 필드가 유료 상품 문서에는 그냥 적혀 있다. 둘째, **ZACKS/LTG 에 `eps_mean_est_fwd12m` 이 있고 정의가 "This is the sum of the individual mean estimates for the next four quarters"** 다. F6 의 NTM EPS 를 공급사가 이미 계산해 제공한다.

## 1. robots.txt 원문 보존

`https://data.nasdaq.com/robots.txt` (2026-09-10 조회). 전문이다.

```
user-agent: *
sitemap: https://data.nasdaq.com/sitemap.xml.gz
allow: /search/$
disallow: /search/
disallow: /api/*.csv*
disallow: /api/*.xml*
disallow: /api/*.xls*
disallow: /api/*.json*
disallow: /api/v3/databases/*/data
disallow: /api/v3/databases/*/codes
disallow: ?anchor=
disallow: ?sortDirection=desc
disallow: ?sortProperty=date
allow: /*sitemap.xml*
```

**해석과 준수.** `disallow` 목록이 데이터 API 경로를 정확히 겨냥한다. `/api/*.json*` 과 `/api/v3/databases/*/data`·`/codes` 는 이번 조사에서 **한 번도 호출하지 않았다.** 상품 문서 페이지가 안내하는 `https://data.nasdaq.com/api/v3/datatables/{Table_Code}?api_key=...` 형태의 샘플 데이터 호출도 하지 않았다. API 키가 없기도 하지만, 애초에 "무료로 응답한다는 사실은 이용 허가가 아니다" 원칙을 적용해 데이터 경로 자체를 건드리지 않았다. 조회한 것은 공개 상품 설명 페이지와 약관 페이지뿐이다.

명시적으로 `allow` 된 `sitemap.xml.gz` 는 시도했으나 **404** 였다. robots.txt 가 가리키는 사이트맵이 실재하지 않는다.

## 2. 이용약관 원문 보존과 4개 항목

전문은 `raw/dl-terms-rendered.txt` (32,827자). 출처는 푸터 "DATA LICENSE TERMS AND CONDITIONS" 링크인 `https://data.nasdaq.com/terms` 다.

> 초판에는 `dl-terms-clean.txt` 가 함께 있었으나 `dl-terms-rendered.txt` 와 **바이트 단위로 동일**했다(md5 `de6e912f5dfe00f3a7a6ea1b42bf59d9`). 원본이 이미 실제 개행을 담고 있어 정규화 처리가 무효과였던 탓이다. 같은 파일 2부를 남길 이유가 없어 `dl-terms-clean.txt` 를 삭제하고 조회 원문 그대로인 `dl-terms-rendered.txt` 만 남겼다.

**페이지 최상단 고지 (원문)**

> "Nasdaq is updating the Terms and Conditions to align terminology and improve clarity based on client feedback. As of November 1, 2026, the updated Terms and Conditions posted here will apply. Unless otherwise agreed to a written agreement with Nasdaq, your continued use of the Data / Nasdaq Information after such date will constitute acceptance of the updated terms."

**2026-11-01 자로 약관이 바뀐다.** 지금 확인한 내용은 그 이전 판이다.

### 2.1 라이선스 부여 방식 (§1.1 원문)

> "Licensor grants to the Client or Client business **as detailed in a mutual executed order form (“Order Form”)**, a limited, non-exclusive, non-transferable non-sublicenseable, license to receive, use, process and store within the Territory the Data each of which shall be detailed in the applicable Order Form. Such usage shall be **for internal business purposes only** unless otherwise detailed in the applicable Order Form."

핵심은 **게시된 약관 자체가 라이선스를 주지 않는다**는 점이다. 라이선스는 Order Form 이 준다. 게시된 약관은 Order Form 과 합쳐져야 "Agreement" 가 된다.

### 2.2 개인·내부 사용의 정확한 정의 — **정의되어 있지 않다**

- `"internal business purposes"` 는 문서 전체에서 **§1.1 에 단 한 번** 나오고 **정의 조항이 없다.**
- `"Territory"` 도 §1.1 에 한 번 나오고 **정의되지 않는다.** Order Form 에서 정해진다.
- `"personal"` 은 개인 사용 개념으로는 **전혀 등장하지 않는다.** 두 번 나오는데 둘 다 기밀정보 조항의 "non-public personal or financial information" 과 대명사 해석 조항이다.
- `Display` / `Non-Display` 티어 구분 문구는 **0건**이다. "Display Only" 같은 티어는 이 약관에 없다.

즉 **"산출물을 나만 본다"가 약관상 어디까지 허용되는지는 게시된 약관으로 확인할 수 없다.** 그 범위는 Order Form 에 적힌다. 다만 §1.4(e) 가 관련된다.

> "(e) use the Data in any time sharing service bureau, software-as-a-service, **cloud** or other technology service"

이건 금지 항목이다. 개인 사용이라도 데이터를 클라우드 서비스에 태우는 형태는 걸릴 수 있다. 이 하네스의 실행 환경이 로컬인지 클라우드인지에 따라 판단이 갈리므로 결정 전에 확인이 필요하다.

### 2.3 Derived Data — 조건부 허용 (§1.2 원문)

> "Client may create derived data (“Derived Data”) provided that: (a) such Derived Data cannot be reversed engineered or decompiled to arrive at the underlying Data; and/or (b) the Derived Data cannot be a substitute for a service provided by Licensor containing the Data. Notwithstanding the foregoing, Client shall be prohibited from creating any Derived Data from any Data for which a **Third Party Provider has prohibited** the creation and of which the Client has been notified. Client shall exclusively own all rights and title in the Derived Data; provided such Derived Data **cannot be distributed outside of Client** except as otherwise detailed in the Order Form or without Licensor's prior written approval."

4분기 합산 NTM EPS 산출은 §1.2 의 Derived Data 에 해당하고, 문언상 **허용 방향**이다. 산출물이 개인·내부용이면 "distributed outside of Client" 문제도 발생하지 않는다. 다만 두 가지가 남는다.

- **Zacks 가 derived data 생성을 금지했는지 확인하지 못했다.** §1.3 이 준수를 요구하는 third party provider 약관 문서(`nasdaqtrader.com` 의 Third-Party Data License Terms and Conditions v1.8, 13페이지)를 받아 전문을 검색했으나 **"Zacks" 는 0건**이다. 이 문서는 Bloomberg·OTC·RepRisk 등 다른 공급사만 다룬다. Zacks 조항은 Order Form 또는 별도 스케줄에 있을 것으로 보이나 **공개 경로에서는 unknown** 이다.
- (b) 조항의 "substitute for a service provided by Licensor" 해석이 남는다. NTM EPS 는 ZACKS/LTG 의 `eps_mean_est_fwd12m` 과 사실상 같은 값이라, 그 필드를 사지 않고 EE 에서 직접 합산하는 것이 "대체물" 로 읽힐 여지가 있다. 판단이 필요한 지점이다.

### 2.4 자동 수집 — 명시 조항 없음

약관에 `automated`, `scrape`, `crawl` 이라는 단어가 **0건**이다. 접근 방법은 §1.5 가 정한다.

> "Client will be provided access to the Data through the Nasdaq Data Link website, Licensor applicable program interface (API), or other tools that may be made available by Licensor **as more explicitly detailed in the applicable Order Form**."

API 접근은 전제돼 있으나 범위는 다시 Order Form 이다. robots.txt 가 데이터 API 경로를 disallow 하는 것은 **비인증 크롤러 기준**이며, API 키를 가진 정당한 구독자의 호출과는 별개 문제다. 다만 구독 전 현재 상태에서는 그 경로를 쓸 근거가 없다.

### 2.5 저장·캐싱·보존

- §1.1 라이선스에 **"receive, use, process and store within the Territory"** 가 포함된다. 저장 자체는 라이선스 범위 안이다.
- §6.3 원문: "Upon termination or expiration of any applicable Order Form for any reason whatsoever, all rights granted to Client hereunder or thereunder to use the applicable Data shall terminate. Client shall immediately cease using all Data, and (b) **delete or purge any Data** provided by Licensor. Upon Licensor's request, Client shall **certify** that all such deletions, purges and cessation of use has occurred. Notwithstanding the above, Client may retain copies of the Data where legally compelled by government regulation, or as necessary for audit purposes."
- 즉 **구독을 끊으면 받아둔 원자료를 지워야 한다.** 백테스트용으로 EEH 이력을 쌓아 두어도 계약 종료 시 삭제 대상이다. 자체 산출한 Derived Data 는 §1.2 에 따라 Client 소유이므로 이와 구분된다. 이 구분이 이 프로젝트에는 실질적으로 중요하다.
- §8 감사: "Licensor or its designee, upon thirty (30) days advance written request, shall have the right to audit use of the Data by Client. Client shall allow Licensor or its designee access to any of the premises, computers ... and personnel of Client at reasonable times ... Such audit request shall not occur more than once per year."

## 3. ZACKS/EE 와 ZACKS/EEH 상품 확인

지시서의 `ZACKS/EE`·`ZACKS/EEH` 는 **테이블 코드**이고, 상품(데이터베이스) 코드는 각각 **ZEE**·**ZEEH** 다. 현재 카탈로그에서 Zacks 퍼블리셔로 15개 상품이 노출된다.

| 항목 | ZEE (North American Earnings Estimates) | ZEEH (North American Consensus Earnings Estimate History) |
|---|---|---|
| URL | `data.nasdaq.com/databases/ZEE` | `data.nasdaq.com/databases/ZEEH` |
| Availability | **Premium** | **Premium** |
| 셀프서비스 구독 | 페이지에 구매 버튼 없음. "Log in ... to view pricing information" | 동일 |
| Contact Sales 버튼 | **없음** | **없음** |
| 표시 가격 | **없음 (unknown)** | **없음 (unknown)** |
| 무료 티어 포함 | **아님** (Premium 표기) | **아님** (Premium 표기) |
| 12종목 비례 과금 | **unknown** — 페이지에 과금 단위 정보 없음 | **unknown** |
| 샘플 데이터 | 있음. 30개 티커(AAPL·MSFT 포함), API 키 필요 | 있음. 같은 30개 티커, `obs_date` 2018년분 |
| Delivery | Daily. EE 테이블 10:30 UTC, MT 15:00 UTC | Daily. EEH 테이블 10:00 UTC(전일자), MT 15:00 UTC |
| History | 표기 "-" | **Jan 1979** |
| Reporting Lag | 표기 "-" | **1 day** |
| Coverage | 5,000+ 미국·캐나다 상장사 | 23,000+ 미국·캐나다 상장·상장폐지사 |
| 미래 기간 | 분기·연간 | **today 기준 최대 4년** |

12종목 소규모 비례 과금 여부는 **어떤 공개 페이지에도 단서가 없다.** 전체 유니버스 패키지뿐인지도 확인되지 않는다. 둘 다 unknown 으로 남긴다.

## 4. 데이터 사전과 F6 관문 1:1 대조

F6(설계 5.1)이 요구하는 항목별로 맞췄다. 출처는 `raw/dl-ZEE-rendered.txt`, `raw/dl-ZEEH-rendered.txt` 다.

| F6 요구 항목 | ZACKS/EE | ZACKS/EEH | 판정 |
|---|---|---|---|
| 향후 4개 분기 제공 | `per_type`="Q" + `per_end_date` 로 분기 행 제공 | 미래 기간 **최대 4년**분 제공 | **충족** |
| 회계분기 종료일 | `per_end_date` (Date, 필터·PK) | `per_end_date` (Date, 필터·PK) | **충족** |
| **회계분기 vs 역분기 분리** | `per_fisc_year`/`per_fisc_qtr` 와 `per_cal_year`/`per_cal_qtr` 를 **별도 컬럼으로 동시 제공** | **동일 4필드가 EEH 테이블 자체에 존재.** 원문 정의: `per_fisc_qtr` = "The fiscal quarter to which this estimate applies", `per_cal_qtr` = "The calendar quarter to which this estimate applies" | **충족 — Finnhub `period` 문제의 해답** (§4.2) |
| currency | `currency_code` (ZACKS/EE 테이블) | **`currency_code` 가 ZACKS/EEH 테이블 컬럼 목록 안에 직접 존재** (MT 를 조인하지 않아도 됨). 원문: `currency_code String Currency code` | **충족 — 백테스트에서도 통화 유지** (§4.3) |
| share_basis | 방법론에 **diluted** 명시 | 동일 | **충족** |
| ADR/ADS 구분 | ZACKS/MT `asset_type` (ADR/CDN/COM/CEF/ETF/MLP) | 동일 MT 테이블 포함 | **충족** |
| accounting | **BNRI** 문서화 | **BNRI** 문서화 | **충족** |
| **asOf / revision date** | **없음.** 테이블 일일 갱신 시각(10:30 UTC)만 존재 | **`obs_date`** (필터·PK) | **EEH 만 충족** |
| 표본수 | `eps_cnt_est` | `eps_cnt_est` + `eps_cnt_est_rev_up`/`_down` | **충족** |
| min / max | `eps_low_est` / `eps_high_est` | `eps_low_est` / `eps_high_est` | **충족** |
| median | `eps_median_est` | `eps_median_est` | **충족** (무료 경로에 없던 항목) |
| 분산 | `eps_std_dev_est` | `eps_std_dev_est` | 추가 확보 |
| 분할 | ZACKS/MT `mr_split_date`, `mr_split_factor` | 동일 | **충족** |
| SEC 대조 키 | ZACKS/MT `comp_cik` | 동일 | 추가 확보 |
| 회계연도 말 월 | ZACKS/MT `per_end_month_nbr` | 동일 | 추가 확보 |

### 4.1 accounting 원문 (ZEEH Methodology)

> "Zacks offers two methods for computing EPS estimates: the Street method and Zacks' proprietary method. The earnings estimates published on Nasdaq Data Link use Zacks' proprietary **BNRI** accounting methodology, which defines the EPS used in the consensus estimates as **diluted Earnings Per Share before non-recurring items and including employee stock options expenses, denominated in U.S. and/or Canadian dollars**, across the board for all stocks in the Zacks universe."

FAQ 보충 원문이다.

> "In 1980, Zacks identified a set of non-recurring items(NRIs) that should be excluded from operating earnings ... (Note: starting as of 2008, Zacks has treated **stock-based compensation as a recurring item to be included** in operating earnings and does not exclude it as an NRI when calculating EPS BNRI.)"

이 한 문장이 NTM-SOURCE-05 의 미확인 두 필드(GAAP/조정 기준, 주가·EPS 주식기준)를 **문서 근거로 해소한다.** 무료 `api.nasdaq.com` 의 `Consensus EPS*` 별표 정의를 못 찾아 "GAAP 이 아니라는 것만 확정" 상태로 남겼던 항목이다. 다만 **무료 API 값이 이 BNRI 와 같은 계산이라는 증명은 아니다.** 두 상품은 별개이고, 무료 API 에는 여전히 공급사 표기가 없다. 유료 상품을 도입해야 이 문서가 우리 데이터에 적용된다.

또 Zacks 는 **Street 방법론 상품을 따로 판다**(ZSEE North American Street Earnings Estimates, ZSES Street Earnings Surprises). 즉 조정 기준이 상품 선택 사항이다.

### 4.2 회계분기와 역분기의 분리 — Finnhub `period` 문제의 해답

ZACKS/EEH 는 같은 행에 네 개의 기간 식별자를 동시에 준다.

| 컬럼 | 원문 정의 |
|---|---|
| `per_fisc_year` | "The fiscal year to which this estimate applies." |
| `per_fisc_qtr` | "The fiscal quarter to which this estimate applies." |
| `per_cal_year` | "The calendar year to which this estimate applies." |
| `per_cal_qtr` | "The calendar quarter to which this estimate applies." |

여기에 `per_end_date`(Date, 필터·PK)와 `per_type`("Q"/"A")가 더해진다.

**이것이 그동안 막혀 있던 지점을 푼다.** 기존 조사에서 Finnhub 의 `period` 필드가 회계분기인지 역분기인지 끝내 확정하지 못했고, 무료 `api.nasdaq.com` 은 `Oct 2026` 같은 **월 라벨 하나만** 줘서 NTM-SOURCE-05 에서 "공급사 라벨은 달력화돼 있어 Apple 처럼 실제 분기말(09-26)과 며칠 어긋날 수 있다" 는 단서를 달아야 했다. EEH 는 회계 기준과 역년 기준을 **추론이 아니라 별도 컬럼으로 구분해 주므로** 그 애매함이 사라진다. Apple(회계연도 말 09-26)이나 NVIDIA(01-31), Oracle(05-31)처럼 역년과 어긋나는 기업에서 특히 값이 크다.

### 4.3 EEH 의 통화 필드 — 백테스트 경로에서도 유지된다

과거 시점 재현은 EE 가 아니라 **EEH** 로 하므로, EEH 쪽에 통화 필드가 없으면 백테스트에서 통화가 다시 미확인이 된다. 원문을 다시 확인한 결과 `currency_code`(String, "Currency code")는 **ZACKS/EEH 테이블의 컬럼 목록 안에 직접 들어 있다.** ZACKS/MT 를 조인해야만 얻는 값이 아니다. 방법론의 "denominated in U.S. and/or Canadian dollars" 표기와 함께 보면, 행 단위 통화 식별과 상품 단위 통화 범위가 모두 확보된다.

근거 위치는 `raw/dl-ZEEH-rendered.txt` 의 `EARNINGS ESTIMATES HISTORY (ZACKS/EEH)` 블록(문자 오프셋 3101~5232, `MASTER TABLE (ZACKS/MT)` 블록 시작 전)이며, 그 구간 안에서 `currency_code` 가 1회 출현한다.

### 4.4 NTM EPS 를 공급사가 이미 계산해 준다 (ZACKS/LTG)

> `eps_mean_est_fwd12m` — "Earnings per share (EPS) mean estimate for the next 12 months. **This is the sum of the individual mean estimates for the next four quarters.**"
> `eps_high_est_fwd12m`, `eps_low_est_fwd12m` — 동일 방식의 high/low 합

F6 의 `NTM EPS = 네 분기 EPS 합` 과 정의가 일치한다. LTG 는 ZEE 상품에 포함된 세 테이블 중 하나다. 다만 커버리지가 2,000+ 사로 EE(5,000+)보다 좁으므로 담당 12종목 전부가 들어가는지는 별도 확인이 필요하다. 그리고 이 필드를 쓰면 §1.2(b) 의 "substitute for a service" 논점이 오히려 사라진다.

## 5. 확인한 것과 확인하지 못한 것

**확인한 것**

- robots.txt 전문과 disallow 대상 경로
- Data License Terms and Conditions 전문, 2026-11-01 개정 예고
- 라이선스가 Order Form 으로 부여된다는 점, 기본 1년 자동갱신·90일 통지, 연 1회 감사권
- Derived Data 조건부 허용과 외부 배포 금지
- 종료 시 원자료 삭제·증명 의무
- "internal business purposes" 와 "Territory" 가 **정의되지 않음**, 개인 사용 개념 부재
- ZEE·ZEEH 가 모두 Premium, 구매 버튼·Contact Sales 버튼 모두 없고 가격은 로그인 뒤
- 두 상품의 전체 컬럼 정의와 F6 관문 대조
- **EEH 의 `obs_date` 로 과거 시점 재현 가능**
- BNRI = diluted, before NRI, ESO 포함, USD/CAD 표기
- ZACKS/LTG 의 `eps_mean_est_fwd12m` = 향후 4분기 평균의 합

**확인하지 못한 것 (전부 unknown, 추측하지 않음)**

- 실제 가격. 어떤 통화·주기·단위인지도 모름
- 셀프서비스 결제 완결 가능 여부. 로그인 후 화면이 결제인지 영업 연결인지
- 개인·내부 티어의 존재 여부와 이름
- 12종목 비례 과금 여부, 종목 단위 과금의 존재 여부
- 무료 트라이얼의 조건과 기간
- Zacks 가 derived data 를 금지했는지 (참조된 third party 약관 문서에 Zacks 없음)
- ZACKS/LTG 커버리지에 담당 12종목이 모두 들어가는지
- 무료 `api.nasdaq.com` 값이 BNRI 와 같은 계산인지 (별개 상품이므로 이번 조사 범위 밖)

## 6. 멈춘 지점과 다음 결정

지시서는 "영업 문의를 거쳐야만 하는 경로로 밝혀지면 보고하고 멈추라"고 했다. **영업 문의 전용 경로임이 밝혀진 것은 아니다.** 상품 페이지에 Contact Sales 버튼이 없다는 점은 오히려 반대 신호다. 그러나 다음 단계가 **계정 생성**이고 그것이 금지 행위라 여기서 멈춘다. 메일도 보내지 않았다.

사용자 결정이 필요한 것은 셋이다.

1. **무료 계정을 만들어 가격을 확인할지.** 결제 없이 가격만 보는 것도 가입이라 이번 지시의 금지 범위에 걸린다. 가입 자체를 허용할지 사용자가 정해야 한다. 가격을 알 수 있는 다른 공개 경로는 확인되지 않았다.
2. **§1.1 의 Order Form 구조를 감수할지.** 셀프서비스 결제가 가능하더라도 그 결제가 Order Form 을 생성하는 형태라면, 1년 자동갱신·90일 해지 통지·연 1회 감사권이 따라온다. "계약 협상 과정을 피하고 싶다" 는 요구와 이 구조가 양립하는지는 사용자 판단이다.
3. **실행 환경이 §1.4(e) 에 걸리는지.** 클라우드·SaaS 사용 금지 조항이 있으므로 하네스를 어디서 돌리는지에 따라 판단이 달라진다.

## 7. 산출물

| 파일 | 내용 |
|---|---|
| `REPORT.md` | 이 보고서 |
| `raw/dl-robots.txt` | robots.txt 원문 |
| `raw/dl-terms-rendered.txt` | 약관 전문 (32,827자) |
| `raw/dl-ZEE-rendered.txt` | ZEE 상품 페이지 전문 (데이터 사전 포함) |
| `raw/dl-ZEEH-rendered.txt` | ZEEH 상품 페이지 전문 (데이터 사전·방법론 포함) |
| `raw/third-party-terms.pdf`, `.txt` | §1.3 이 참조하는 third party 약관 v1.8 (Zacks 미포함 확인용) |
| `raw/dl-*-err.txt` | 404 응답 보존 |
| `probe_datalink.py`, `probe_sitemap.py` | 정적 조회 스크립트 |
| `probe-log.txt` | 조회 시각과 응답 상태 |

## 8. 지키지 않은 것이 없음을 확인

- 결제·가입·구독 신청 **하지 않음**
- 메일 발송 **하지 않음** (약관 페이지의 `dataops@nasdaq.com` 안내도 사용하지 않음)
- `api.nasdaq.com` 호출 **0건**
- `data.nasdaq.com` 의 robots.txt disallow 경로 호출 **0건** (데이터 API 경로 포함)
- 점수·규칙·승인·원자료 변경 **없음**. 기존 `validation/consensus-source-2026-09-09/` 는 읽기 전용으로 `fetchlib.py` 만 재사용
- 요금 추정치 **기재하지 않음**. 기존 월 100~300 달러 수치 **근거로 쓰지 않음**
