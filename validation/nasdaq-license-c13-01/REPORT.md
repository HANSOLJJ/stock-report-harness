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

## 5. 공식 문의 채널 및 영문 문의 초안

공식 라이선스 계약 및 배포 승인을 진행하기 위한 담당 채널은 다음과 같습니다. 지침에 따라 실제 이메일 발송은 수행하지 않았으며, 사용자 승인 후 발송할 수 있도록 완성도 높은 문의 초안을 작성했습니다.

- **상업 라이선스, 계약 및 견적 문의**: `datasales@nasdaq.com`
- **기술 데이터 연동 및 피드 문의**: `DataOps@nasdaq.com`

### [문의 발송 전 사용자 필수 입력 사항]
- `[Company Name]`: 정식 영문 법인명
- `[Website URL]`: 서비스 또는 법인 웹사이트
- `[Contact Person]`: 담당자 영문 성명 및 직책
- `[Target Distribution]`: 순수 사내 연구용 vs 웹사이트를 통한 대중 공개 배포 여부 선택

### [영문 공식 문의문 초안 (Draft)]

```text
To: datasales@nasdaq.com
Cc: DataOps@nasdaq.com
Subject: Licensing Inquiry: Nasdaq Data Link (Zacks Consensus Data) for Educational AI Scorecard & Research Reports

Dear Nasdaq Data Sales Team,

We are reaching out to inquire about the appropriate licensing structure and pricing for utilizing consensus earnings estimates data from Nasdaq Data Link (specifically Zacks Earnings Estimates, ZACKS/EE / ZACKS/EEH).

1. About Us & Use Case Overview:
- Company Name: [Company Name]
- Website: [Website URL]
- Application: We develop an automated financial analysis and educational reporting system that produces periodic HTML equity research scorecards for a focused universe of approximately 12 global technology companies.

2. Data Requirements & Pipeline Workflow:
- Dataset: Zacks Consensus Earnings Estimates (4 upcoming forward quarters).
- Universe Size: Approximately 12 tickers (e.g., AAPL, NVDA, MSFT, TSMC, etc.).
- Request Frequency: Batch retrieval on a quarterly / monthly basis (very low volume, under 100 API calls per month).
- Processing: We aggregate the 4-quarter consensus EPS figures into a weighted Next Twelve Months (NTM) metric to feed our proprietary financial scoring algorithm.

3. Licensing Questions & Clarifications Needed:
a) Derived Data & Public Report Distribution:
Our final deliverables are static HTML research reports containing valuation metrics and overall company scores. Does publishing these reports (where our calculated score is displayed, alongside reference citation of the forward consensus figures) classify as "Derived Data", and what level of external redistribution rights/rider is required?
b) Tier & Pricing for Focused Universe:
Do you offer tiered subscription options tailored for small-scale universe needs (12 tickers) rather than an enterprise-wide full-market subscription?
c) Data Retention & Archiving:
Are we permitted to archive point-in-time calculation snapshots strictly for historical report verification and audit trails after publication?

Please advise on the suitable agreement type (Nasdaq Data Link Commercial Subscription vs. Nasdaq Global Data Agreement) and provide the relevant fee schedule or application forms.

Thank you for your time and assistance.

Sincerely,

[Contact Person]
[Title / Role]
[Company Name]
[Contact Email / Phone]
```

---

## 6. 결론 및 권고사항

1. **단기적 조치**:
   - `api.nasdaq.com`을 통한 자동화 스크래핑 파이프라인 운영은 이용약관 위반 위험이 있으므로 정규 배포 환경의 자동 호출 소스로 승격하지 않고, 관측 참조 데이터로만 보존합니다.
   - 현재 생성된 12개사 관측 데이터는 연구 및 계약 검토용 스냅샷으로 유지합니다.
2. **중장기적 조치**:
   - 정식 서비스 및 공개 배포 리포트 상용화를 위해서는 작성된 문의 초안을 바탕으로 Nasdaq Data Sales(`datasales@nasdaq.com`)와 정식 상담을 진행하여, 12개 종목 규모에 대한 최소 요금제 및 파생 데이터(Derived Data) 재배포 권한 조건을 확정해야 합니다.
   - 법인 정보가 확정되면 본 보고서의 문의 초안에 입력값을 채워 공식 승인을 거쳐 발송할 것을 권고합니다.
