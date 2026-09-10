# Nasdaq 애널리스트 데이터 라이선스 및 배포 정책 조사 보고서 (NASDAQ-LICENSE-C13-01)

## 1. 개요 및 배경

본 보고서는 NASDAQ-LICENSE-C13-01 독립 작업 지침에 따라 `api.nasdaq.com`의 애널리스트 실적 전망치(analyst earnings-forecast) 데이터를 당사의 AI scorecard 및 리서치 리포트 생산 파이프라인에서 공식적으로 활용하고 공개 배포할 수 있는지 여부를 법적·계약적 관점에서 조사한 결과입니다.

기존 관측에서 `https://api.nasdaq.com/api/analyst/{TICKER}/earnings-forecast` 엔드포인트를 통해 10개 기업의 4분기 컨센서스를 성공적으로 수집한 바 있으나, 해당 엔드포인트의 상업적 이용 적격성, 라이선스 범위, 가공 데이터의 공개 배포 허용 여부에 대한 공식 검증이 선행되어야 합니다.

이에 따라 Nasdaq 공식 이용약관(Terms of Use), Nasdaq Global Data Agreement(GDA), Data Feed Request Form(DFRF), 그리고 공식 B2B 데이터 플랫폼인 Nasdaq Data Link(구 Quandl)의 정책 및 Zacks Investment Research 방법론을 분석하여 정리했습니다.

---

## 2. 핵심 라이선스 7대 차원 분석

### (1) 계약 유형 (Contract Type)

1. **`api.nasdaq.com` 엔드포인트의 법적 성격**:
   - `api.nasdaq.com`은 공식 배포용 공개 API가 아니며, Nasdaq 웹사이트 UI 렌더링을 지원하기 위한 내부 백엔드 서비스입니다.
   - Nasdaq 웹사이트 이용약관(Terms of Use) 제2조(Prohibited Uses)에 따르면, 자동화된 수단(로봇, 스파이더, 스크래퍼 등)을 통한 데이터 추출 및 상업적 목적의 재활용은 명시적으로 금지되어 있습니다.
   - 따라서 해당 무료 엔드포인트를 자동화 파이프라인의 정규 데이터 소스로 운영하는 것은 계약 위반 및 서비스 차단(IP 블록 등)의 위험이 있습니다.

2. **공식 계약 경로 구분**:
   - **경로 A: Nasdaq Data Link (클라우드 기반 REST API)**:
     - 과거 Quandl을 인수한 나스닥의 공식 금융 데이터 API 플랫폼입니다.
     - 구독형(Subscription) API 키 발급 방식으로 12개 종목과 같은 소규모 포트폴리오에 가장 적합한 현실적 계약 경로입니다.
   - **경로 B: Nasdaq Global Data Agreement (GDA) + Data Feed Request Form (DFRF)**:
     - 거래소 직접 피드(Direct Data Feed) 및 엔터프라이즈급 시장 데이터 분배를 위한 전통적 마스터 계약입니다.
     - 연간 비디스플레이(Non-Display Usage) 보고 의무 및 엄격한 준법 감사가 수반되는 고비용 기업용 계약입니다.

### (2) 회계 기준 및 원천 공급자 (GAAP/Non-GAAP & Source Provider)

1. **원천 데이터 공급자**:
   - Nasdaq 웹사이트 및 Nasdaq Data Link의 애널리스트 실적 전망치는 **Zacks Investment Research**에서 공급받아 제공됩니다.
2. **회계 기준 정의 (Zacks BNRI)**:
   - Zacks의 컨센서스 EPS는 **BNRI(Before Non-Recurring Items)** 기준을 엄격하게 적용합니다.
   - 일회성 손익(비경상적 항목, 구조조정 비용, 자산매각 손익 등)을 제외하고 정상 영업활동에서 발생한 이익만을 반영한 **Non-GAAP 조정 희석 EPS(Adjusted Diluted EPS)**입니다.
   - 주식보상비용(SBC)은 비용으로 포함되며, 주식분할(Stock Split) 및 무상증자 이벤트는 즉시 소급 조정됩니다.
   - 따라서 일반적인 GAAP EPS와는 일회성 항목 처리 방식에서 차이가 발생하며, 리포트 작성 시 "Zacks Consensus Non-GAAP (BNRI) Diluted EPS"임을 명시해야 합니다.

### (3) 시점 정보(asOf) 및 과거 시계열 제공 여부 (Point-in-Time Availability)

1. **`api.nasdaq.com`의 한계**:
   - 해당 엔드포인트의 JSON 응답 내 `asOf` 필드는 통상 `null`로 반환되며, 조회 시점의 최신 스냅샷 수치만 단독 노출됩니다.
   - 과거 특정 시점에 시장 컨센서스가 얼마였는지 추적하는 Point-in-Time 시계열 관측이 원천적으로 불가능합니다.
2. **Nasdaq Data Link 공식 테이블 (`ZACKS/EE`, `ZACKS/EEH`)**:
   - 공식 상업 데이터인 Zacks Earnings Estimates History(`ZACKS/EEH`) 테이블은 각 분기별 컨센서스의 개정 일자(Revision Date), 집계 시점(Calculation Timestamp), 개별 애널리스트 추정치 분포를 일자별로 보존하여 제공합니다.
   - 백테스팅 및 과거 시점 평가를 위해서는 공식 History 테이블 연동이 필수적입니다.

### (4) 12개사 분기별 사용 요금 및 요청 한도 (Pricing & Limits)

1. **요청 한도(Rate Limits)**:
   - Nasdaq Data Link의 표준 인증 사용자 한도는 **10초당 300건, 10분당 2,000건**입니다.
   - 당사 타깃 12개사(분기당 12~48회 호출 수준)의 사용량은 나스닥의 기술적 허용 한도 대비 0.01% 미만에 불과하므로, API 호출량에 따른 기술적 병목은 전혀 발생하지 않습니다.
2. **요금 체계**:
   - Nasdaq Data Link의 무료 티어(Free Tier)는 기본 거시경제 지표 및 일부 오픈 데이터셋에 한정되며, Zacks 컨센서스 데이터(`ZACKS/EE`)는 프리미엄(유료) 데이터셋으로 분류됩니다.
   - **내부 분석/연구용(Internal/Display Only)**: 개인 개발자 또는 소규모 팀 기준 월 $100~$300 수준의 구독료가 부과됩니다.
   - **외부 배포용(External Redistribution)**: 가공된 데이터라도 외부에 배포할 경우 별도의 Redistribution 라이선스 요금이 가산되며, 연간 수천 달러 이상의 맞춤형 B2B 계약이 요구됩니다.

### (5) 가공한 NTM EPS 및 HTML 리포트의 공개 배포 허용 여부 (Redistribution & Derived Data)

1. **파생 데이터(Derived Data) 요건**:
   - Nasdaq 및 거래소 라이선스 정책상, 원천 데이터(Zacks 개별 추정치 피드)를 직접 노출하지 않고 당사의 고유한 알고리즘(예: 분기 가중 합산 NTM EPS, 밸류에이션 점수, 종합 AI 스코어카드 랭킹)으로 가공한 결과물은 **파생 데이터(Derived Data)**로 분류될 수 있습니다.
   - 파생 데이터로 인정받기 위한 핵심 조건은 **"역산 불가능성(Non-Reversibility)"**입니다. 즉, 공개된 HTML 리포트의 지표만으로 원래의 Zacks 원천 컨센서스 피드를 재구성할 수 없어야 합니다.
2. **공개 배포 시 제약 사항**:
   - 파생 데이터라 하더라도 최종 HTML 리포트에 "Zacks 분기별 컨센서스 원수치($1.25, $1.40 등)"를 그대로 표기하여 대중에게 공개 배포할 경우, 이는 단순 파생이 아닌 원천 데이터의 '외부 재배포(Public External Distribution)'에 해당합니다.
   - 따라서 원천 수치를 그대로 담은 HTML 리포트를 외부에 무상/유상 공개 배포하려면 공식 재배포 권한(Redistribution Rights)이 계약에 포함되어야 합니다.
   - 원천 수치를 숨기고 오직 최종 산출 점수(스코어)와 가중 NTM 종합 수치만 노출하는 형태라면 파생 데이터 면제 또는 완화된 요율 적용 여부를 나스닥 영업팀과 협의할 수 있습니다.

### (6) 저장·캐싱 및 보존 조건 (Storage, Caching & Data Retention)

1. **임시 캐싱**:
   - AI scorecard 생성 및 리포트 빌드 파이프라인의 연산 성능 향상을 위한 로컬 메모리/데이터베이스 임시 캐싱은 유효한 계약 기간 동안 통상 허용됩니다.
2. **영구 보존 및 데이터 파기(Data Purge) 의무**:
   - 나스닥의 표준 계약 조건에 따르면, 구독 계약이 종료될 경우 원천 피드 데이터 및 로컬 저장된 스냅샷은 파기(Purge)하는 것이 원칙입니다.
   - 리포트 아카이빙 목적으로 과거 스냅샷 데이터를 영구 보유(Perpetual Rights)하고자 할 경우, 계약 체결 시 영구 보존 라이선스 조항을 명시적으로 포함해야 합니다.

### (7) 정식 계약 신청 시 필요 정보 및 사용 설명 (Corporate Requirements)

1. **법인 기본 정보**:
   - 회사 공식 법인명(Legal Entity Name) 및 설립 관할권(국가 및 주).
   - 사업자등록번호 및 본사 소재지 주소.
   - 계약 담당자(Business Contact), 기술 담당자(Technical Contact), 결제 담당자(Billing Contact) 정보.
   - 공식 웹사이트 URL.
2. **사용 용도 설명서(Description of Intended Use)**:
   - **데이터 수신 방식**: Nasdaq Data Link REST API를 통한 분기별 배치(Batch) 호출.
   - **대상 유니버스**: 글로벌 대형 기술주 및 반도체 12개사.
   - **처리 메커니즘**: 4개 분기 컨센서스 EPS를 수집하여 NTM(Next Twelve Months) 가중 지표 산출 및 당사 고유 밸류에이션 알고리즘을 통한 종합 투자 분석 스코어카드 연산.
   - **출력물 형태**: 웹 기반 정적 HTML 경제·기업 리포트.
   - **배포 대상**: 사내 연구용(내부) 또는 외부 일반 대중 공개(외부 배포 여부 명시).

---

## 3. 공식 규정 및 근거 출처

1. **Nasdaq Website Terms of Use**:
   - 제2조 'Prohibited Uses': "You agree not to use any robot, spider, other automatic device, or manual process to monitor or copy our web pages or the content contained herein without our prior written permission."
2. **Nasdaq Global Data Agreement (GDA) & Data Feed Request Form (DFRF)**:
   - 시장 데이터 비디스플레이 사용(Non-Display Use Policy) 및 파생 데이터(Derived Data Policy) 가이드라인.
3. **Nasdaq Data Link Documentation**:
   - Zacks Earnings Estimates (`ZACKS/EE`) 및 Zacks Estimates History (`ZACKS/EEH`) 데이터 사전 및 API 스펙.
4. **Zacks Investment Research Methodology**:
   - "BNRI (Before Non-Recurring Items) Diluted EPS Definition and Treatment of Extraordinary Items".

---

## 4. 미확인 사항 및 추가 확인 필요 항목

1. **소규모 유니버스(12개사) 전용 할인 또는 최소 과금 티어 부재**:
   - Nasdaq Data Link의 표준 유료 플랜은 전체 미국 상장사(전체 유니버스) 패키지로 가격이 책정되는 경우가 많아, 당사처럼 12개사만 선별 사용하는 경우에 대한 비례 과금 플랜이 존재하는지 영업팀 확인이 필요합니다.
2. **정적 리서치 리포트 내 컨센서스 인용의 공정 이용(Fair Use) 범위**:
   - 개별 분기 컨센서스 수치를 단순 출처 명시(Citation) 형태로 리포트 하단에 1~2개 인용하는 것이 외부 재배포 라이선스를 필수적으로 요구하는지, 아니면 비재배포성 파생 분석물로 인정되는지 공식 회답이 필요합니다.

---

## 5. 실제 문의 발송 가능 여부 점검 및 환경적 제약

지침에 따라 `datasales@nasdaq.com` 및 `DataOps@nasdaq.com` 공식 채널로의 실제 문의 발송 가능 여부를 환경적·기술적·법적 관점에서 점검했습니다.

1. **CLI 및 에이전트 환경의 기술적 제약**:
   - 현재 작업 환경(Windows PowerShell CLI) 내에는 인증된 SMTP 메일 전송 도구(MTA) 및 아웃바운드 메일 발송 클라이언트가 설치·구성되어 있지 않습니다.
   - 상용 클라우드/로컬 네트워크에서 포트 25, 465, 587을 통한 임의의 비인증 소켓 직접 발송은 보안 정책상 차단됩니다.
   - 가령 스크립트로 직접 발송을 시도하더라도 SPF(Sender Policy Framework), DKIM(DomainKeys Identified Mail), DMARC 인증 레코드가 없는 비공식 IP 발송물은 Nasdaq의 기업 보안 메일 게이트웨이(Proofpoint, Cisco IronPort 등)에서 즉시 스팸으로 분류되거나 거부(Bounce)됩니다.
2. **법인 대리권 및 보안 거버넌스 제약**:
   - 데이터 라이선스 및 지식재산권 계약 문의는 법적으로 권한 있는 대리인이 공식 기업 도메인 이메일을 통해 발송해야 공식 계약 절차로 접수됩니다.
   - 따라서 에이전트 환경에서의 임의 스크립트 발송은 불가능하며, 공식 대체 경로를 통한 접수가 필수적입니다.

---

## 6. 대체 공식 신청 경로 (Alternative Official Application Channels)

직접 이메일 발송의 환경적 제약을 해결하기 위한 공식 대체 신청 경로는 다음과 같습니다.

1. **경로 1: Nasdaq Data Link 공식 세일즈 웹 문의 폼 (Contact Sales Web Form)**:
   - **공식 URL**: `https://data.nasdaq.com/contact`
   - **접수 방식**: 웹 브라우저를 통해 법인명, 이메일, 관심 데이터셋(Zacks Earnings Estimates), 예상 사용 규모를 직접 입력하여 제출합니다.
   - **장점**: 제출 즉시 Nasdaq Data Sales CRM 티켓이 자동 생성되며, 담당 계정 관리자(Account Manager)가 지정되어 공식 안내를 받을 수 있습니다.
2. **경로 2: Nasdaq Global Data Products 공식 문의 포털**:
   - **공식 URL**: `https://www.nasdaq.com/solutions/global-data-products/contact-us`
   - **접수 방식**: 엔터프라이즈급 시장 데이터 피드 및 비디스플레이 라이선스 문의용 공식 웹 폼입니다.
   - **전화 문의 병행**: Nasdaq Global Data Products (+1 301 978 5307) 또는 Nasdaq Market Sales (+1 800 846 0477).
3. **경로 3: 공식 기업 이메일 클라이언트를 통한 직접 발송**:
   - 담당자가 기업 공식 메일(Google Workspace 또는 Microsoft 365)을 통해 본 보고서 7절에 수록된 완비된 영문 공문을 복사하여 `datasales@nasdaq.com` (참조: `DataOps@nasdaq.com`)으로 직접 발송합니다.

---

## 7. 공식 문의 필수 5대 핵심 요건 완비 내역 및 공문 초안 [폐기 (Revoked) - 2026-09-10]

> [!WARNING]
> **공문 초안 공식 폐기 공지 (Revocation Notice - 2026-09-10)**
> 본 공문 초안은 다음 두 가지 사유로 인해 **공식 폐기** 처리되었으며 실제 발송되지 않습니다 (기록 보존 목적으로 초안 원문은 삭제하지 않고 유지합니다).
> 1. **사용 범위 확정(personal/internal only)으로 인한 재배포 협상 전제 소멸**: 사용자가 프로젝트 산출물 사용 범위를 '개인 및 내부 연구용(personal / internal only)'으로 최종 확정함에 따라, 외부 일반 대중 배포를 전제로 한 재배포 라이선스(External Redistribution Agreement / Rider) 협상 전제가 소멸되었습니다.
> 2. **초안 내 유니버스 12개사 목록 기재 오류**: 초안 7절 2항 b)에 `AVGO`와 `AMD`가 포함되어 있으나, 당사 AI 스코어카드 실제 12개사 유니버스는 `PLTR`과 `SPCX`입니다. 본 초안을 그대로 발송했을 경우 신고 대상 종목 범위를 잘못 통보할 치명적 오류가 있었습니다.
>
> 아울러 본 보고서에 기술된 예상 요금 체계 및 원자료 보존/파기(Purge) 조건은 나스닥 세일즈/기술팀의 공식 서면 회신 전 수집된 **잠정 정보(Provisional Information)**임을 다시 명시합니다.

본 보고서에서 작성된 공식 문의서는 다음 5대 핵심 요건을 명시적으로 포함하여 구성되었습니다.

1. **데이터 수집 경로 및 원천**:
   - `api.nasdaq.com`의 무료 엔드포인트 프로그램 자동 수집 허용 여부 질의와 함께, 공식 상용 피드인 `Nasdaq Data Link ZACKS/EE` 및 `ZACKS/EEH`의 4개 분기 EPS 컨센서스 데이터 연동 방식을 명시했습니다.
2. **소규모 사용 규모**:
   - 당사 유니버스가 글로벌 기술주 12개사(AAPL, MSFT, NVDA, GOOGL, AMZN, META, TSLA, AVGO, ORCL, AMD, TSM, BABA)로 제한되며, 분기별/월별 배치 호출(월 100회 미만)의 극소량 볼륨임을 명시했습니다.
3. **내부 지표 가공 및 자체 스코어 계산 (Derived Computation)**:
   - 4개 분기 컨센서스를 가중 합산한 NTM(Next Twelve Months) EPS 지표 산출 및 당사의 독자적 AI 밸류에이션 스코어카드 연산에 활용됨을 명시했습니다.
4. **정적 HTML 리포트 외부 배포 (External Public Distribution)**:
   - 최종 결과물이 정적 HTML 경제·기업 리서치 리포트로 외부 일반 대중에게 배포되며, 연산된 종합 스코어 표기와 함께 원천 컨센서스 인용 범위에 따른 재배포 권한(Redistribution Rider) 필요 여부를 명시했습니다.
5. **원자료 보관 및 아카이빙 조건 (Data Retention)**:
   - 발행된 리포트의 과거 시점 검증 및 감사 추적(Audit Trail)을 위해 계산 시점의 스냅샷 데이터를 장기/영구 보관할 수 있는지 질의했습니다.

### [영문 공식 문의 공문 (Official Inquiry Draft)]

```text
To: datasales@nasdaq.com
Cc: DataOps@nasdaq.com
Subject: Commercial Licensing & Distribution Inquiry: Nasdaq Data Link (Zacks Estimates) for Educational AI Research Reports

Dear Nasdaq Data Sales Team,

We are submitting a formal licensing inquiry regarding consensus earnings estimates data from Nasdaq Data Link (specifically Zacks Earnings Estimates, ZACKS/EE and Estimates History, ZACKS/EEH) for our automated equity research and AI scorecard system.

1. Corporate Profile & System Overview:
- Company Name: [Company Name / Legal Entity]
- Corporate Website: [Website URL]
- Business Function: Automated equity research platform generating educational HTML scorecards for major equities.

2. Scope of Data & Technical Workflow (5 Core Requirements):
a) Data Source & Collection:
We seek official licensing for quarterly consensus EPS forecasts (upcoming 4 quarters). We request clarification on whether programmatic access is restricted strictly to Nasdaq Data Link (ZACKS/EE, ZACKS/EEH) or if any public programmatic interface is authorized.
b) Small-Scale Universe (12 Tickers):
Our target coverage is limited to approximately 12 global technology equities (e.g., AAPL, NVDA, MSFT, GOOGL, AMZN, META, TSLA, AVGO, ORCL, AMD, TSM, BABA). Query volume is extremely light (batch retrieval on a monthly/quarterly basis, well under 100 calls/month).
c) Derived Data & Metric Computation:
We do not redistribute raw analyst feeds. We aggregate the 4-quarter consensus EPS figures into a weighted Next Twelve Months (NTM) metric to calculate proprietary multi-factor valuation scores. The resulting output cannot be reverse-engineered to reconstruct the underlying raw Zacks feed.
d) External Public Distribution of Static HTML Reports:
Our deliverables are static HTML research reports distributed to end users. Does publishing these reports (displaying our proprietary scores alongside reference citation of the forward consensus figures) qualify as exempt Derived Data, or does it require an External Redistribution Agreement / Rider?
e) Data Retention & Archiving:
Are we authorized to retain historical calculation snapshots indefinitely for audit trails, compliance verification, and report recreation purposes?

3. Requested Information:
- Recommended agreement framework (Nasdaq Data Link Commercial Subscription vs. Nasdaq Global Data Agreement).
- Fee schedule for small-scale universe coverage (12 tickers) and applicable external redistribution riders.
- Standard data purge policies upon subscription expiration vs. perpetual audit rights.

Please provide the relevant contract documentation, pricing tiers, or application forms.

Sincerely,

[Authorized Representative Name]
[Title / Position]
[Company Legal Name]
[Corporate Email & Direct Contact]
```

---

## 8. 항목별 라이선스 확정 상태 및 증거 관리 매트릭스

나스닥의 공식 서면 회신을 접수하기 전까지 각 항목의 상태는 다음과 같이 관리됩니다.

| 검토 항목 | 현재 상태 | 상세 정책 근거 및 잠정 기준 | 증거 및 조치 계획 |
| :--- | :--- | :--- | :--- |
| **(1) 자동수집 허용** | **미확인 (보류)** | `api.nasdaq.com`은 웹사이트 이용약관 제2조상 자동화 스크래핑이 엄격히 금지됨. 정식 자동 수집은 Nasdaq Data Link API 키를 발급받아야 함. | 공식 회신 접수 시 계약 승인 번호 및 API 연동 증거 저장 예정. |
| **(2) 데이터 사용 범위** | **미확인 (보류)** | 12개사 소규모 사용에 대한 부분 라이선스 플랜 존재 여부 미확인. 표준 요금제는 전체 시장 단위로 부과될 가능성 높음. | 세일즈 견적서 접수 시 유니버스 범위 증빙 파일 보관. |
| **(3) Derived Data 계산** | **미확인 (보류)** | NTM 가중 합산 및 스코어 연산은 비역산성을 충족하여 파생 데이터로 해석될 소지가 크나, 나스닥의 공식 유권해석 필요. | 나스닥 법무/준법팀의 파생 데이터 인정 서면 회신 보관 예정. |
| **(4) 외부 배포 허용** | **미확인 (보류)** | HTML 리포트에 원천 컨센서스 수치를 인용 노출할 경우 External Redistribution 라이선스 필수 요구 가능성 높음. | 재배포 라이선스 계약서 및 공개 배포 승인 조항 증거 보관. |
| **(5) 원자료 보관 조건** | **미확인 (보류)** | 표준 약관상 계약 해지 시 원천 데이터 파기(Purge) 의무가 존재하며, 감사용 스냅샷 영구 보존 권한(Perpetual Rights) 승인 필요. | 데이터 보존 규정(Data Retention Schedule) 승인 문서 보관. |
| **(6) 가격 및 계약 조건** | **미확인 (보류)** | 클라우드 구독(Data Link) vs 거래소 직결(GDA/DFRF) 계약 유형 및 연간 라이선스 비용 확정 대기. | 체결된 정식 계약서 및 인보이스 사본을 증거로 저장. |

---

## 9. 결론 및 생산 점수 등록 보류 원칙 (Scoring Hold)

1. **생산 점수 등록 보류 원칙 엄격 준수**:
   - 나스닥 세일즈/기술팀의 공식 서면 답변이 접수되고 라이선스 계약이 체결되기 전까지, 수집된 Nasdaq 관측 데이터(10개사 4분기 등)는 **AI scorecard 생산 점수에 절대 등록하지 않습니다(Scoring Hold 엄격 유지)**.
   - 현재 워크스페이스의 6종 raw JSON, 점수 계산 로직, 그리고 12개 검증 테스트 상태를 완벽히 불변으로 유지합니다.
2. **공문 발송 불필요 및 라이선스 협상 종결**:
   - 사용자가 산출물의 범위를 '개인 및 내부 연구용(personal / internal only)'으로 최종 확정함에 따라, 외부 재배포를 전제로 했던 7절의 영문 공문 발송 권고는 **폐기**되었습니다.
   - 따라서 나스닥 재배포 라이선스 협상은 진행하지 않으며, `api.nasdaq.com` 생산 배제 정책은 변함없이 엄격히 유지됩니다.

