# FX-SOURCE-19 — 환율 출처 조사 및 allowlist 등재 후보

- 지시 원문: `msg_389e8d20889b` (run `run_1243c2a83479`)
- 배경: `F6-FX-16` 에서 P1·P2 환율 기준을 **C안(시총 기준일 현물환율)** 으로 확정
- 기준일: 2026-09-10. 조회 시각은 `robots-log.txt`·`terms-log.txt` 참조
- 필요 통화: **TWD·CNY 둘뿐**. 필요 기능: 과거 일자 조회
- 범위: 환율 출처 조사만. worker `F6-SPEC-18`·C-13 `F6-VERIFY-18B` 범위는 건드리지 않음

## 0. 결론

**권고 출처는 연준 H.10 (`www.federalreserve.gov`)이다.** TWD·CNY 를 모두 제공하고, 과거 일자 조회가 되며, TSM·BABA 두 발행사가 20-F 에서 실제로 인용하는 바로 그 출처다. 우리가 임의로 고르는 것이 아니라 공시 관행을 따르는 것이 된다.

**TWD·CNY 과거 일자 조회는 된다. 원문에서 직접 확인했다.** 현재 릴리스(2026-09-08)에 `TAIWAN DOLLAR 31.6700 31.6600 31.7300 31.7800 31.6300` 과 `CHINA, P.R. YUAN 6.7197 6.7202 6.7190 6.7181 6.7108` 이 일별 5개 열로 실려 있다. 과거는 `Release Dates` 아카이브와 Data Download Program(`/datadownload/choose.aspx?rel=h10`, 200 응답 확인)으로 접근한다.

**약관상 쓸 수 있는가 — 금지는 없으나 명시 허가도 못 찾았다.** `www.federalreserve.gov` 는 **`robots.txt` 가 404** 로 존재하지 않아 크롤러 제한이 게시돼 있지 않다. 다만 확인한 경로(`/legal.htm`, `/website-terms-of-use.htm`, `/privacy-program.htm` 모두 404, `/website-linking-policies.htm` 은 200)에서 **Board 자체 콘텐츠의 재사용을 명시적으로 허가하는 문구는 찾지 못했다.** 그 페이지의 저작권 언급은 외부 링크 사이트에 관한 것이다. 따라서 **"금지 없음"이지 "명시 허가"가 아니다.** 등재 시 이 상태를 note 에 그대로 적기를 권한다. 미국 연방정부 저작물의 일반 원칙(17 U.S.C. §105)이 있으나 이번 조사에서 사이트 문서로 확인한 사실이 아니므로 근거로 내세우지 않는다.

**부수적으로 더 중요한 것을 찾았다. 이미 `allowed` 인 `financialmodelingprep.com` 의 무료·개인 라이선스가 2026-09-10 자로 바뀐 `usage_scope: corporate_internal_only` 와 정면으로 충돌한다.** 그리고 **`finnhub.io` 는 자기 `robots.txt` 가 이용약관 페이지를 `Disallow` 해서 규정대로는 약관을 확인할 수 없다.** 둘 다 내 과제 범위 밖이라 고치지 않았고 §4 에 보고만 한다.

## 1. 후보별 조사 결과

`robots.txt` 를 먼저 받고, 그 다음 약관·정책 문서만 받았다. 데이터·내용 페이지는 약관 확인 뒤에만 열었다(PRIV-ARR-17).

| 후보 | robots.txt | 약관 | TWD | CNY | 과거 조회 | 키/요금 | 판정 |
|---|---|---|---|---|---|---|---|
| **연준 H.10** `www.federalreserve.gov` | **404 (없음)** | 명시 허가 문구 미발견, 금지도 없음 | **○ 확인** | **○ 확인** | ○ 아카이브·DDP | 불필요 | **권고** |
| FRED `fred.stlouisfed.org` / `api.stlouisfed.org` | 둘 다 전체 허용 (`Disallow:` 공란, crawl-delay 1~2) | **확인 실패 — 반복 타임아웃** | 미확인 | 미확인 | 미확인 | 무료 키 필요 | 보류 |
| BIS `www.bis.org` | 표준 Drupal, 콘텐츠 허용 | **비상업 한정** | 미확인 | 미확인 | 미확인 | 불필요 | **부적격** |
| exchangerate.host (apilayer) | 전체 허용 | **최종사용자 개인 사용 한정** | 미확인 | 미확인 | 미확인 | 키 필요 | **부적격 추정** |
| `financialmodelingprep.com` (기등재) | 전체 허용 | **무료=개인·비영리 한정** | 미확인 | 미확인 | 미확인 | 무료 250콜/일 | **범위 충돌** |
| `finnhub.io` (기등재) | **`/terms-of-service` Disallow** | **확인 불가(위 사유)** | 미확인 | 미확인 | 미확인 | 무료 60콜/분 | **약관 미확인** |
| 대만 중앙은행 `www.cbc.gov.tw` | **접근 실패** | 미확인 | – | – | – | – | 조사 불가 |
| 중국 SAFE `www.safe.gov.cn` | **접근 실패** | 미확인 | – | – | – | – | 조사 불가 |
| `chinamoney.com.cn` | 404 | 미조사 | – | – | – | – | 미조사 |

TWD·CNY 열의 "미확인" 은 **약관이 부적격이거나 확인되지 않아 데이터 페이지를 열지 않았다**는 뜻이다. 없다는 뜻이 아니다.

### 1.1 연준 H.10 — 권고안

**게시 방식과 기준 시각을 원문에서 확인했다.**

> "The H.10 weekly release contains **daily rates of exchange** of major currencies against the U.S. dollar. The data are **noon buying rates in New York for cable transfers** payable in the listed currencies. The rates have been **certified by the Federal Reserve Bank of New York for customs purposes** as required by section 522 of the amended Tariff Act of 1930. **Release Dates provides an archive of historical H.10 releases.** The H.10 release contains daily bilateral exchange rates and nominal dollar indexes **from the previous week**."

정리하면 이렇다.

- **기준 시각**: 뉴욕 정오 매입률(noon buying rate). 시각 정의가 문서로 확정돼 있다.
- **주기**: 값은 **일별**, 게시는 **주간**이며 **전주 분**을 싣는다.
- **결측 표기**: `ND = No data for this date` 로 명시한다. 휴일 처리에 그대로 쓸 수 있다.
- **과거**: `Release Dates` 아카이브 + Data Download Program.
- **통화**: `TAIWAN DOLLAR`, `CHINA, P.R. YUAN` 둘 다 수록. **우리가 필요한 둘이 정확히 있다.**
- **키·요금**: 불필요.

**주의할 제약이 하나 있다. 게시가 주간이라 오늘 날짜 환율이 아직 안 나와 있을 수 있다.** C안이 "시총 기준일 환율" 이므로 이 지연이 직접 걸린다. §2 의 규칙이 이걸 흡수한다.

### 1.2 FRED — 보류

`fred.stlouisfed.org` 와 `api.stlouisfed.org` 의 `robots.txt` 는 둘 다 전체 허용이다(`User-agent: *`, `Disallow:` 공란, crawl-delay 1과 2). 접근 제한은 없다.

그러나 **이용약관 페이지를 받지 못했다.** `/docs/api/terms_of_use.html` 과 `/legal/` 을 45초·90초 타임아웃으로 각각 재시도했고 `api.stlouisfed.org` 루트도 시도했으나 **모두 read timeout** 이었다. 약관을 확인하지 못했으므로 **데이터 페이지나 시리즈 페이지는 열지 않았다.** TWD·CNY 시리즈 존재 여부를 확인하지 않은 것은 그 때문이며, 없다고 판단한 것이 아니다.

FRED API 는 **무료 API 키 발급이 필요**하다. 금지 사항에 따라 **발급하지 않았다.** 절차만 적으면, FRED 계정 생성 후 `My Account → API Keys` 에서 무료 키를 신청하는 방식으로 알려져 있으나 **이 절차 자체도 이번에 페이지로 확인하지 못했으므로 미확인으로 둔다.**

FRED 는 H.10 과 같은 연준 계통이고 일별 환율 시리즈를 다루므로 **차선 후보로서 가치가 있다.** 약관 확인이 되면 재검토를 권한다.

### 1.3 BIS — 부적격

> "Users may download, display, print out, photocopy or redistribute any BIS Material **for non-commercial purposes**."

`usage_scope` 가 `corporate_internal_only` 이므로 비상업 한정 조건을 만족하지 못한다. 또한 같은 문서가 **BIS Data Portal 의 통계는 무료 발췌 허용 범위에서 제외**한다고 별도로 적고 있어, 우리가 쓰려는 바로 그 부분이 더 좁다. **부적격으로 판정하고 데이터 페이지를 열지 않았다.**

### 1.4 exchangerate.host — 부적격 추정

> "...provided such end users use exchangeratehost API Data & Services **strictly for their own personal use**..."

apilayer 계열이고 최종사용자 개인 사용 한정 문언이 있다. 유료 등급의 별도 조건이 있을 수 있으나 **결제·가입 금지 조건상 확인 대상이 아니다.** 부적격 추정으로 두고 데이터 페이지를 열지 않았다.

### 1.5 대만·중국 공적 기관 — 조사 불가

`www.cbc.gov.tw`(대만 중앙은행)와 `www.safe.gov.cn`(중국 외환관리국) 은 **TLS 인증서 검증 실패**로 `robots.txt` 조차 받지 못했다(`CERTIFICATE_VERIFY_FAILED: self-signed certificate in certificate chain`). **인증서 검증을 끄지 않았다.** 검증을 우회하면 그 응답이 진짜 그 기관의 것이라고 보증할 수 없고, 환율처럼 값 자체가 근거가 되는 자료에서는 특히 받아들일 수 없다. 조사 불가로 남긴다.

원본 통화 발행국의 중앙은행이라는 점에서 원천으로서의 가치는 높으므로, 네트워크·인증서 문제가 해결되면 재조사를 권한다. 다만 **두 기관은 각각 자국 통화만 다루므로 채택 시 출처가 둘로 나뉜다.** H.10 은 하나로 둘 다 덮는다.

## 2. 기준일 정의 (조사 항목 2)

C안은 "시총 기준일의 현물환율" 인데, 그대로는 실행할 수 없다. 휴일과 게시 지연 때문이다. 아래 규칙을 권고한다.

### 2.1 규칙 초안

| 항목 | 규칙 | 근거 |
|---|---|---|
| **기준 시각** | 뉴욕 정오 매입률 | H.10 정의. 우리가 고르는 것이 없다 |
| **목표 일자** | `fx_target_date` = 시총 기준일(`price_date`) | C안 정의 |
| **휴일·결측** | 해당 일자에 값이 없거나 `ND` 이면 **그 이전 가장 가까운 값이 있는 영업일**로 후퇴 | H.10 이 `ND = No data for this date` 를 명시하므로 결측 판별이 결정적 |
| **후퇴 한도** | 최대 7 일. 초과하면 산출하지 않고 보류 | 주간 게시 주기의 1배. 그 이상 벌어지면 자료 문제로 본다 |
| **미게시** | 게시 지연으로 목표 일자 값이 아직 없으면 같은 후퇴 규칙 적용 | 주간 게시라 T일 값이 없을 수 있다 |
| **기록** | `fx_rate_date`, `fx_rate`, `fx_source`, `fx_backfill_days`(= `price_date` − `fx_rate_date`), `fx_release_date` 를 관측에 저장 | 재현성. 나중에 같은 규칙으로 같은 값이 나와야 한다 |

**핵심은 `price_date` 와 `fx_rate_date` 를 같다고 가정하지 않고 둘 다 저장하는 것이다.** 게시 지연 때문에 둘이 다른 것이 정상이고, 그 차이를 숨기면 나중에 재현이 안 된다. `fx_backfill_days` 가 0 이 아닌 관측은 화면에서 그 사실을 볼 수 있어야 한다.

### 2.2 왜 "직전 영업일 후퇴" 인가

미래 값을 쓰면 기준 시점에 존재하지 않던 정보를 쓰는 것이 된다. F6 는 특정 시점의 평가라 그 오염을 피해야 한다. 후퇴는 항상 "그 시점에 이미 존재하던 값" 만 쓰므로 안전하다. 이 방향은 AGENTS.md 의 휴장일 처리(직전 거래일 종가)와도 같은 성격이다.

### 2.3 남는 판단 사항

**후퇴 한도 7일은 제안이지 확정이 아니다.** 주간 게시 주기에 맞춘 값인데, 게시 지연이 길어지는 시기에는 부족할 수 있다. 실제 게시 이력을 보고 정하는 편이 낫고 그건 별도 확인이 필요하다.

## 3. allowlist 등재 권고안 (조사 항목 3)

`v1.6` 의 `sources.allowed` 형식에 맞춘 초안이다. **제안이며 내가 파일을 고치지 않았다.**

```json
{
  "host": "www.federalreserve.gov",
  "note": "연준 H.10 Foreign Exchange Rates. P1·P2 의 USD 환산 환율 출처. 일별 뉴욕 정오 매입률이며 TAIWAN DOLLAR·CHINA P.R. YUAN 을 모두 수록한다(2026-09-10 현재 릴리스에서 확인). 과거는 Release Dates 아카이브와 Data Download Program(/datadownload/choose.aspx?rel=h10)으로 조회한다. API 키 불필요. robots.txt 가 404 로 존재하지 않아 크롤러 제한이 게시돼 있지 않다. 다만 Board 자체 콘텐츠의 재사용을 명시적으로 허가하는 문구는 확인한 경로(/legal.htm·/website-terms-of-use.htm·/privacy-program.htm 은 404, /website-linking-policies.htm 은 200)에서 찾지 못했다. 즉 '금지 없음'이지 '명시 허가'가 아니다. 미국 연방정부 저작물 원칙(17 U.S.C. §105)은 사이트 문서로 확인한 사실이 아니므로 등재 근거로 쓰지 않는다. TSM·BABA 20-F 가 convenience translation 환율의 출처로 H.10 을 명시하므로 발행사 공시 관행과 같은 기준을 쓰게 된다. 값을 대량 수집하지 않고 필요한 일자만 조회하며 요청 간격을 둔다.",
  "decided_at": "2026-09-10",
  "scope": "F6 P1·P2 의 TWD·CNY → USD 환산 환율에 한정",
  "evidence": "validation/fx-source-19-2026-09-10/REPORT.md"
}
```

**FRED 는 지금 등재하지 않기를 권한다.** 약관을 확인하지 못했고, `policy_note` 가 "robots.txt 와 이용약관을 확인하고 등재한 뒤에 수집한다" 를 요구하기 때문이다. 다만 `unlisted` 에도 넣지 않기를 권한다. `unlisted` 는 "검토를 마치고 안 넣기로 한 host" 만 담는다는 규정이라, 약관 확인이 안 된 FRED 는 **미검토** 에 해당한다.

**BIS 는 `unlisted` 등재를 권한다.** 검토를 마쳤고 비상업 한정이라 안 넣기로 판정했으므로 규정상 `unlisted` 의 정의에 맞는다. 초안이다.

```json
{
  "host": "www.bis.org",
  "reason_type": "license",
  "reason": "이용약관이 BIS Material 의 무료 이용을 non-commercial purposes 로 한정한다. usage_scope 가 corporate_internal_only 이므로 충족하지 못한다. 같은 약관이 BIS Data Portal 의 통계를 무료 발췌 허용 범위에서 별도로 제외하므로 우리가 쓰려는 부분은 더 좁다.",
  "decided_at": "2026-09-10",
  "evidence": "validation/fx-source-19-2026-09-10/raw/doc-bis-terms.txt"
}
```

## 4. 범위 밖이지만 보고해야 하는 것 둘

내 과제는 환율 출처지만, 조사 중 **이미 `allowed` 인 두 host 에서 문제를 발견했다.** 고치지 않았고 보고만 한다. `F6-SPEC-18` 과 겹칠 수 있으니 처리 주체는 설계진행이 정해 주기 바란다.

### 4.1 `financialmodelingprep.com` — `corporate_internal_only` 와 충돌

약관 §2.2.1 원문이다.

> "**Personal Use**: This license may only be used by a Customer who is **an individual**, and strictly for their own **personal, non-business and non-commercial** purposes. **In no event may the Customer use this licence on behalf of a company, partnership, organization, group, entity or any other third party.** ... Without limiting the foregoing, Customer may not use the Data or Services for any Commercial Use. For the purposes of these terms of service **Commercial Use** refers to, but is not limited to, the following activities: **Association with Business or Commercial Entities**: Any association with a company, organization, or non-personal domain, including but not limited to being an employee, contractor, representative... **Data Collection and Analysis for Commercial Purposes**: Collecting, aggregating, or analyzing data using FMP Services or Data for commercial purposes or to support commercial activities, including market research, business intelligence, or **data-driven decision-making**."

현재 `v1.6` 의 등재 note 는 `"API 키 발급 기반. 무료 등급 250콜/일"` 로 **무료 등급을 전제**한다. 그런데 무료 등급은 §2.2.1 의 개인 라이선스이고, 그 문언은 법인 대리 사용을 명시적으로 배제한다. `usage_scope` 가 2026-09-10 에 `personal_internal_only` 에서 `corporate_internal_only` 로 바뀌면서 **Alpha Vantage 와 정확히 같은 구조의 문제가 FMP 에도 생긴 것으로 보인다.** `usage_scope.note` 가 이미 "원천을 새로 검토할 때는 '개인 사용 허용' 조항이 우리에게 적용되지 않는다는 점부터 확인한다" 고 적고 있는데, 기등재 host 에 대한 소급 점검은 아직 안 된 듯하다.

§2.2 본문이 "Order Form 또는 계정에 명시된" 라이선스를 말하므로 **유료 등급은 다른 조건일 수 있다.** 즉 FMP 자체가 부적격이라는 뜻이 아니라 **무료 등급 전제가 깨진다**는 뜻이다.

### 4.2 `finnhub.io` — 약관을 규정대로 확인할 수 없다

`finnhub.io/robots.txt` 전문이다.

```
User-agent: *
Disallow: /terms-of-service
Disallow: /faq
Allow: /
```

**공급사가 자기 이용약관 페이지를 크롤러에 대해 `Disallow` 하고 있다.** 우리 정책은 "robots.txt 와 이용약관을 확인하고 등재한 뒤에 수집한다" 인데, 이 host 는 그 확인을 robots.txt 가 막는 구조다. **`/terms-of-service` 를 조회하지 않았다.** PRIV-ARR-17 이 약관 문서 조회를 허용하지만, 그 host 의 robots.txt 가 그 경로를 명시적으로 금지하는 경우까지 덮는지는 내가 판단할 사항이 아니라고 봤다.

현재 `finnhub.io` 는 `allowed` 에 등재돼 있으나 note 가 `"API 키 발급 기반. 무료 등급 분당 60콜"` 로 **약관 검토 근거를 담고 있지 않다.** 어떻게 확인하고 등재했는지 기록이 필요하다.

## 5. 확인한 것과 확인하지 않은 것

**확인한 것**
- 후보 11개 host 의 `robots.txt` 응답(원문 보존)
- H.10 이 TWD·CNY 를 모두 수록한다는 사실을 현재 릴리스 본문에서 직접 확인
- H.10 의 기준 시각(뉴욕 정오 매입률), 일별 값·주간 게시·전주 수록, `ND` 결측 표기, 과거 아카이브 존재
- H.10 Data Download Program 이 응답한다는 것(200)
- `www.federalreserve.gov` 에 `robots.txt` 가 없다는 것과, 확인한 경로에 재사용 명시 허가가 없다는 것
- BIS·exchangerate.host·FMP 의 약관 제한 문구(원문 인용)
- `finnhub.io` 가 자기 약관 페이지를 robots 로 막는다는 것

**확인하지 않은 것 (추측하지 않음)**
- FRED 의 이용약관. 반복 타임아웃으로 실패했고, 그래서 FRED 의 TWD·CNY 시리즈 존재 여부도 열지 않았다
- FRED 무료 키 발급 절차의 정확한 단계. 페이지로 확인하지 못했다
- BIS·exchangerate.host 의 TWD·CNY 제공 여부. 약관이 부적격이라 데이터 페이지를 열지 않았다
- Finnhub·FMP 의 환율 기능. 약관 문제가 선행이라 열지 않았다
- 대만 중앙은행·중국 SAFE. TLS 검증 실패로 접근 불가
- H.10 의 실제 게시 지연 분포. §2.3 의 후퇴 한도 7일을 확정하려면 필요하다
- `www.federalreserve.gov` 의 요청 한도 정책. 명시 문서를 찾지 못했다

## 6. 산출물

| 파일 | 내용 |
|---|---|
| `REPORT.md` | 이 보고서 |
| `robots-log.txt`, `raw/robots-*.txt` | 후보 11개 host 의 robots.txt 원문 |
| `terms-log.txt`, `raw/doc-*.txt`, `raw/doc-*.html` | 약관·정책 문서 원문 |
| `raw/doc-frb-h10-current.*` | H.10 현재 릴리스 원문 (TWD·CNY 확인 근거) |
| `raw/doc-frb-h10-about.*` | H.10 기준 시각·주기 정의 원문 |
| `raw/doc-fmp-terms.*` | FMP 약관 원문 (§2.2.1 근거) |
| `raw/doc-bis-terms.*` | BIS 약관 원문 |
| `probe_robots.py`, `probe_terms.py` | 조회 스크립트 |

## 7. 조건 준수

- **`robots.txt` 를 먼저 받고 그 다음 약관만 받았다.** 데이터·내용 페이지는 약관 확인 뒤에만 열었고, 약관이 부적격이거나 미확인인 host 의 데이터 페이지는 열지 않았다
- **결제·가입·API 키 발급 없음.** FRED 무료 키도 발급하지 않고 절차만 적었다(그 절차도 미확인으로 표시)
- **값을 대량 수집하지 않았다.** H.10 은 현재 릴리스 1건만 받아 통화 수록 여부를 확인했다
- **환율을 임의로 정해 넣지 않았다.** 인용한 수치는 전부 H.10 원문 값이고 계산에 쓰지 않았다
- **TLS 인증서 검증을 끄지 않았다.** 검증 실패 host 는 조사 불가로 남겼다
- 근거는 응답 본문 자체를 보존했다
- `api.nasdaq.com` 호출 0건. 점수·규칙·승인·원자료 변경 없음. `v1.6` 파일을 고치지 않고 초안만 제시했다
- worker `F6-SPEC-18`·C-13 `F6-VERIFY-18B` 범위를 건드리지 않았다
