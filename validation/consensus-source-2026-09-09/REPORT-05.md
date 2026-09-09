# NTM-SOURCE-05 — 담당 10개사 EPS 의 채점 기준 검증

- 지시 원문: `msg_98cbddbdac15` (run `run_1243c2a83479`)
- 선행 산출물: `a74c15e` (NTM-SOURCE-04, 4분기 원자료 확보)
- 기준일: 2026-09-09. 새 조회 시각은 `sec-05.json`·`raw-05/` 의 `fetched_at_utc` 참조
- 목표: 4/4 확보 반복이 아니라 **채점 보류 사유를 실제로 해소**하는 것

## 0. 결론

**보류 사유 7개 중 4개를 해소하고 1개를 부분 해소했다. 2개는 미확인으로 남는다.**

| 보류 사유 | NTM-SOURCE-04 | 지금 | 해소 근거 |
|---|---|---|---|
| 통화 | 미확인 | **해소** | SEC XBRL 단위 `USD/shares` (10/10) + StockAnalysis 선언 통화 `USD` |
| 보통주/ADR | 미확인 | **해소** | SEC 등록 법인·티커·거래소 + StockAnalysis `adrPriceDivisor` 미설정 (10/10) |
| 분할 조정 | 미확인 | **해소(관측 범위 내)** | SEC 에서 같은 분기 재보고값 불일치 0건 (10/10) |
| 회사 공식 회계분기·발표 창 | 미확인 | **해소** | SEC `fiscalYearEnd` + 분기 `start~end` + 10-Q/10-K 제출 이력 (10/10) |
| GAAP/조정 기준 | 미확인 | **부분 해소** | Nasdaq 이 GAAP 희석·기본 **아님**을 확정. 조정 규칙 자체는 미확인 |
| 추정치 스냅샷 시점 | 미확인 | **미확인 유지** | 4분기 원천 Nasdaq 은 미제공. StockAnalysis 는 제공하나 2/4 분기 |
| 주가·EPS 주식기준 일치 | 미확인 | **미확인 유지** | 공급사가 희석/기본을 밝히지 않음 |

**10개사 모두 여전히 자동 채점 불가**다. 다만 남은 사유가 7개에서 3개(부분 1 + 미확인 2)로 줄었고, 남은 항목은 조사로 더 좁힐 수 없는 **정책 결정 사항**이다. 필요한 최소 결정은 §5 에 있다.

`REPORT.md` §5.1 의 *"기간 일치이므로 조정 정의 차이"* 단정은 **철회**했다. 경위는 `CHANGELOG-05.md` R1 이다.

## 1. 방법

새 원천으로 **SEC EDGAR 공시**(`data.sec.gov`)를 사용했다. 회사 자신이 제출한 원문이므로 공급사 화면보다 상위 근거이며, 회사 IR 자료와 같은 계열이다. 수치 근접만으로 기준을 확정하지 않기 위해, 먼저 **공급사가 스스로 선언한 표기**(데이터 제공사, 통화, ADR 제수, 갱신시각)를 찾고, 그 다음 SEC 원문과 대조했다.

- `https://data.sec.gov/submissions/CIK{10자리}.json` — 법인명, 티커, 거래소, 회계연도 말, 10-Q/10-K 제출 이력
- `https://data.sec.gov/api/xbrl/companyconcept/CIK{10자리}/us-gaap/EarningsPerShareDiluted.json` (및 `...Basic`) — 분기별 GAAP EPS, 기간, 단위, 제출 양식·일자

CIK 는 StockAnalysis 스냅샷이 선언한 값을 사용했고, SEC 법인명으로 역확인했다.

## 2. 해소된 항목

### 2.1 공급사 표기: 추정치의 실제 제공사를 확인했다

StockAnalysis 는 `estimatesSource: "spg"` 와 함께 제공사를 명시한다(10/10 동일).

> Price targets, consensus ratings and financial forecasts are provided by **S&P Global Market Intelligence**. Individual analyst data is provided by TipRanks.

이는 NTM-SOURCE-04 가 추측을 피해 비워 둔 칸을 공급사 자신의 표기로 채운 것이다. **Nasdaq 쪽은 제공사 표기를 찾지 못했다.** NVDA 분기값이 Zacks 공개 표와 일치하는 것은 정황일 뿐 표기가 아니므로 제공사를 Zacks 로 확정하지 않는다.

### 2.2 통화

| 근거 | 값 |
|---|---|
| SEC XBRL `EarningsPerShareDiluted` 단위 | `USD/shares` (10/10) |
| StockAnalysis 선언 통화 `curr.financial` / `curr.price` | `USD` (10/10) |
| Nasdaq | **미표기** (종목정보 `currency` 필드 null) |

주가와 EPS 가 모두 USD 임을 두 상위 근거로 확인했다. Nasdaq 자체 표기는 없지만 미국 상장 법인의 USD 공시로 보완된다. 계약의 "통화 일치" 요건은 **충족**으로 본다.

### 2.3 보통주 / ADR

10개사 전부 SEC 등록 미국 법인의 보통주이고, StockAnalysis 의 `adrPriceDivisor` 가 **미설정**이다(ADR 환산 대상이 아님을 공급사가 표시). `exchangeRate` 도 미설정이다. ADR/ADS 환산 문제는 이 10개사에 **발생하지 않는다.**

| 기업 | SEC 법인명 | 회계연도 말 | 거래소 |
|---|---|---|---|
| Meta | Meta Platforms, Inc. | 12-31 | NASDAQ |
| NVIDIA | NVIDIA CORP | 01-31 | NASDAQ |
| Alphabet | Alphabet Inc. | 12-31 | NASDAQ |
| Microsoft | MICROSOFT CORP | 06-30 | NASDAQ |
| Amazon | AMAZON COM INC | 12-31 | NASDAQ |
| Apple | Apple Inc. | **09-26** | NASDAQ |
| Oracle | ORACLE CORP | 05-31 | NYSE |
| Palantir | Palantir Technologies Inc. | 12-31 | NASDAQ |
| Tesla | Tesla, Inc. | 12-31 | NASDAQ |
| SpaceX | **SPACE EXPLORATION TECHNOLOGIES CORP** | 12-31 | NASDAQ |

SpaceX 는 SEC 등록 법인으로 10-Q·10-K 를 제출하고 있음을 확인했다(CIK 0001181412). NTM-SOURCE-04 의 상장 확인이 공시 원문으로 보강됐다.

**Apple 의 회계연도 말은 09-26 이며 09-30 이 아니다.** 공급사의 월 라벨(`Sep 2026`)은 달력화된 표기이고 실제 분기말과 며칠 다르다. 이 차이는 기록했고, 분기 식별에는 영향이 없다.

### 2.4 분할 조정

SEC 공시에서 **같은 분기 기간이 서로 다른 값으로 재보고된 사례가 10개사 모두 0건**이다. 분할이 있었다면 후속 비교 공시에서 과거 EPS 가 소급 재작성된다. 조사 구간에 그런 흔적이 없고, 주가와 추정치가 모두 2026-09 시점이라 분할 기준이 어긋날 구간 자체가 없다. 요건은 **충족**이다. 다만 장래 발표될 분할까지 배제되지는 않는다.

### 2.5 회사 공식 회계분기와 발표 창

SEC 제출 이력으로 각 사의 마지막 발표 분기와 다음 미발표 분기 경계를 재확인했다. 공급사 표기와 **10/10 일치**한다.

| 기업 | 최근 10-Q/10-K 대상기간 | 제출일 | 첫 미발표 분기 | 다음 발표 예정 |
|---|---|---|---|---|
| Meta | 2026-06-30 | 2026-07-30 | Sep 2026 | 2026-10-28 |
| NVIDIA | 2026-07-26 | 2026-08-26 | Oct 2026 | 2026-11-25 |
| Alphabet | 2026-06-30 | 2026-07-23 | Sep 2026 | 2026-10-27 |
| Microsoft | 2026-06-30 | 2026-07-29 | Sep 2026 | 2026-10-27 |
| Amazon | 2026-06-30 | 2026-07-31 | Sep 2026 | 2026-10-22 |
| Apple | 2026-06-27 | 2026-07-31 | Sep 2026 | 2026-10-29 |
| Oracle | 2026-05-31 | 2026-06-22 | **Aug 2026** | **2026-09-10** |
| Palantir | 2026-06-30 | 2026-08-04 | Sep 2026 | 2026-11-09 |
| Tesla | 2026-06-30 | 2026-07-23 | Sep 2026 | 2026-10-28 |
| SpaceX | 2026-06-30 | 2026-08-04 | Sep 2026 | 2026-11-05 |

Oracle 의 Aug 2026 분기는 종료됐지만 미발표이며, 기준일 다음 날 발표 예정이다. 끝난 분기를 미발표 창에 포함한 NTM-SOURCE-04 의 판단이 공시 이력으로 확인됐다. **이 자료는 2026-09-10 발표 직후 곧바로 낡는다.**

## 3. 부분 해소: GAAP / 조정 기준

핵심 검증이다. 마지막 **확정 발표 분기**의 EPS 를 SEC 공시 GAAP 값과 대조했다. 확정값은 추정이 아니므로 기준 차이가 그대로 드러난다.

| 기업 | 확정 분기 | SEC GAAP 희석 | SEC GAAP 기본 | StockAnalysis `eps` 열 | Nasdaq 실적 | Nasdaq − GAAP희석 |
|---|---|---|---|---|---|---|
| Meta | 2026-04-01~06-30 | 6.18 | 6.23 | 6.18 ✓ | 6.18 | 0.00 |
| NVIDIA | 2026-04-27~07-26 | 2.46 | 2.47 | 2.46 ✓ | 2.22 | **−0.24** |
| Alphabet | 2026-04-01~06-30 | 9.11 | 9.23 | 9.11 ✓ | 9.11 | 0.00 |
| Microsoft | FY26 Q4 (유도) | 4.81 | – | 4.8094 ✓ | 4.74 | **−0.07** |
| Amazon | 2026-04-01~06-30 | 5.75 | 5.82 | 5.75 ✓ | 1.88 | **−3.87** |
| Apple | 2026-03-29~06-27 | 2.02 | 2.03 | 2.02 ✓ | 1.91 | **−0.11** |
| Oracle | FY26 Q4 (유도) | 1.45 | – | 1.4495 ✓ | 1.79 | **+0.34** |
| Palantir | 2026-04-01~06-30 | 0.41 | 0.44 | 0.41 ✓ | 0.31 | **−0.10** |
| Tesla | 2026-04-01~06-30 | 0.32 | 0.34 | 0.32 ✓ | 0.04 | **−0.28** |
| SpaceX | 2026-04-01~06-30 | −0.09 | −0.09 | −0.0923 ✓ | −0.09 | 0.00 |

Microsoft·Oracle 은 회계연도 말 분기라 SEC 가 분기를 별도 태그하지 않는다. `FY 희석 EPS − 같은 회계연도 9개월 누적`으로 유도했다(Microsoft 17.95 − 13.14 = 4.81, Oracle 5.83 − 4.38 = 1.45). 주식수 변동 때문에 단순차가 실제 분기 EPS 와 다를 수 있으므로 **유도값**으로 표시한다.

### 확정된 것

1. **StockAnalysis 의 `eps` 열은 SEC GAAP 희석 EPS 다.** 10/10 일치하며, 유도값을 쓴 Microsoft·Oracle 에서도 소수 넷째 자리까지 맞는다. 이 정도 일치는 우연으로 보기 어렵고, 공급사의 `non-GAAP adjusted` 각주는 `eps` 열이 아니라 별도 조정 열에 걸리는 표기로 읽힌다.
2. **Nasdaq 의 실적 열은 GAAP 희석도 GAAP 기본도 아니다.** 5개사에서 벗어나고, 편차가 한 방향이 아니다(Oracle +0.34, Amazon −3.87). 단일 부호였다면 특정 항목의 일괄 제외로 좁힐 수 있었겠지만 양방향이라 그렇게 좁혀지지 않는다.

### 확정되지 않은 것

- **Nasdaq 의 조정 규칙이 무엇인지 모른다.** `Consensus EPS*` 의 별표 정의를 찾지 못했다. 시도한 경로는 §4 에 있다. "조정 계열로 보인다"까지가 근거가 허용하는 한계이고, 무엇을 가감하는지는 미확인이다.
- **확정 실적 열의 기준을 추정 열이 그대로 쓰는지 모른다.** 같은 표에 병기된다는 점은 정황이지 증명이 아니다. 공급사가 두 열의 기준 동일성을 문서로 밝히지 않았다.

즉 **채점에 쓰는 4분기 값(Nasdaq)의 회계 기준은 여전히 확정할 수 없다.** 확정된 것은 그것이 GAAP 이 아니라는 사실뿐이다.

## 4. 미확인으로 남은 항목과 시도한 경로

### 4.1 추정치 스냅샷 시점

계약 5.1 (2) 가 요구하는 항목이다. **원천에 따라 갈린다.**

| 원천 | 스냅샷 시점 | 확보 분기 |
|---|---|---|
| Nasdaq (4분기 제공) | **미제공** — `asOf`=null, `/eps` 에도 필드 없음 | 4/4 |
| StockAnalysis (2분기 제공) | **제공** — `trust.lastUpdated` / `lastChecked` / `freshnessLag:"hours"` | 2/4 |

StockAnalysis 는 10/10 모두 시각을 명시한다. `a74c15e` 스냅샷에서 복원한 값이다.

| 기업 | lastUpdated (UTC) | lastChecked (UTC) |
|---|---|---|
| Meta | 2026-09-04T05:05:51Z | 2026-09-01T19:30:21Z |
| NVIDIA | 2026-09-04T08:45:32Z | 2026-09-04T12:40:35Z |
| Alphabet | 2026-09-08T00:00:00Z | 2026-09-08T10:50:43Z |
| Microsoft | 2026-09-08T00:00:00Z | 2026-09-08T10:50:27Z |
| Amazon | 2026-09-04T00:00:00Z | 2026-09-04T14:40:01Z |
| Apple | 2026-09-08T11:15:07Z | 2026-09-08T15:55:01Z |
| Oracle | 2026-09-08T10:35:42Z | 2026-09-08T13:50:01Z |
| Palantir | 2026-09-03T00:00:00Z | 2026-09-03T10:35:21Z |
| Tesla | 2026-09-08T09:21:03Z | 2026-09-08T09:50:19Z |
| SpaceX | 2026-09-08T10:30:06Z | 2026-09-08T12:45:02Z |

**시도한 경로와 결과**: Nasdaq `earnings-forecast` 의 `asOf`(null) / Nasdaq `/eps`(필드 없음) / Nasdaq 종목 earnings 페이지(클라이언트 렌더링, 각주 미노출) / Zacks 페이지 `last-modified` 메타(페이지 수정 시각이지 추정 갱신 시각이 아님) / StockAnalysis `trust` 블록(제공, 단 2분기).

**정확한 미확인 이유**: 4분기를 주는 원천이 시각을 안 주고, 시각을 주는 원천이 4분기를 안 준다. 두 원천을 이어 붙이면 계약 5.1 (3) 의 기준 일치를 깨므로 결합이 해법이 될 수 없다.

### 4.2 주가·EPS 의 주식 기준(희석/기본) 일치

주가는 시장 실거래가이고 EPS 는 Nasdaq 조정 기준이다. 공급사가 희석/기본을 밝히지 않아 두 값의 주식 기준이 같은지 확인할 수 없다. SEC 는 GAAP 희석·기본을 모두 제공하지만, 그것은 Nasdaq 값의 기준을 알려주지 않는다.

### 4.3 Nasdaq 별표 정의

**시도한 경로**: Nasdaq 용어사전(`/glossary/e/earnings-per-share`), 종목 earnings 페이지 HTML 전문 검색, `/market-activity/quotes/earnings-forecast`(404), `/data-disclaimers`(404), `/terms-and-conditions`(404), `api.nasdaq.com` 의 `earnings-forecast-disclaimer`·`estimates`·`earnings-date`(모두 404), 응답 JSON 의 `headers` 블록(라벨만 있고 정의 없음).

**정확한 미확인 이유**: 별표를 붙인 표는 있는데 별표를 푸는 각주가 공개 경로 어디에도 노출되지 않는다. 조사하지 않은 경로나 구독 문서에 있을 수 있으므로 **부재로 단정하지 않는다.**

## 5. 필요한 최소 결정사항

조사로는 더 좁힐 수 없고 정책으로 정해야 하는 것만 적는다. **여기서 결정하지 않는다.**

1. **추정 스냅샷 시점의 대체 허용 여부.** 조회 시각을 스냅샷 시점 대용으로 허용하면 Nasdaq 4/4 를 쓸 수 있다. 허용하지 않으면 스냅샷 시점이 명시된 원천만 쓸 수 있고, 그 경우 현재 확보는 2/4 라 4분기 합 자체가 불가능하다. **둘 중 하나를 고르면 나머지 검증은 자동으로 정해진다.**
2. **회계 기준 요건의 형태.** 채점이 "GAAP 희석"을 요구하면 Nasdaq 4분기 값은 기준 불일치로 배제되고, StockAnalysis `eps` 열(=GAAP 희석 확인됨)은 2분기뿐이라 역시 불가능하다. 채점이 "공급사 조정 기준의 일관 사용"을 허용하면 Nasdaq 4/4 를 쓸 수 있다.
3. **주식 기준 일치의 인정 근거.** 공급사가 밝히지 않는 상황에서 무엇을 근거로 "맞췄다"고 볼지 정해야 한다.

1과 2를 모두 엄격하게 잡으면 현재 공개 원천으로는 **어떤 기업도 채점 불가**다. 이는 자료 부족이 아니라 요건과 공개 자료의 구조적 불일치이므로, 요건 완화든 유료 원천 도입이든 정책 결정이 선행돼야 한다.

## 6. 계약 필드별 판정

전체는 `contract-fields-05.json` 에 있다. 10개사 모두 동일하게 12개 필드 중 9개 충족, 1개 부분 확인, 2개 미확인이다.

| 필드 | 판정 | 근거 요약 |
|---|---|---|
| 가격 유효 양수 | 충족 | Nasdaq 종목정보 종가 |
| 가격 시점 고정 | 충족 | 거래일 라벨 2026-09-08, 기준일 직전 거래일 |
| 4개 미발표 분기 확보 | 충족 | Nasdaq 단일 원천 4/4 |
| 분기 중복 없음·연속 | 충족 | 3개월 간격, 두 엔드포인트 일치 |
| 분기 기간 정의 | 충족 | SEC 회계연도 말·분기 기간과 대조 |
| 추정 스냅샷 시점 | **미확인** | Nasdaq 미제공 / StockAnalysis 제공(2분기) |
| 통화 일치 | 충족 | SEC `USD/shares` + 공급사 선언 USD |
| 보통주/ADR | 충족 | SEC 등록 보통주, ADR 제수 미설정 |
| 분할 조정 | 충족(관측 범위 내) | SEC 재보고 불일치 0건 |
| GAAP/조정 기준 | **부분 확인** | GAAP 아님은 확정, 조정 규칙 미확인 |
| 주가·EPS 주식기준 일치 | **미확인** | 공급사 미표기 |
| EPS 합 양수 | 충족 | 10/10 양수 |

**"모든 분기에 두 번째 공급사가 없다"는 사실은 새 필수요건으로 추가하지 않았다.** 계약 5.1 은 복수 공급사 교차검증을 요구하지 않는다. 해당 지표는 참고로만 남기고 충족 판정에 쓰지 않았다.

## 7. C-13 공유 사항 (Nasdaq 정의 근거)

- **Nasdaq 의 `Consensus EPS*` 별표 정의는 공개 경로에 없다.** §4.3 의 시도 경로를 그대로 재사용하면 중복 조사를 피할 수 있다. TSM/BABA 에서도 같은 결과일 가능성이 높다.
- **Nasdaq 값은 GAAP 이 아니다.** TSM/BABA 에서도 SEC(20-F) 또는 현지 공시와 대조해 같은 확인을 하는 것이 좋다. ADR 발행사는 20-F 를 제출하므로 `data.sec.gov` 의 `companyconcept` 가 그대로 동작할 수 있다.
- **StockAnalysis 는 ADR 판별에 바로 쓸 수 있는 필드를 준다.** `meta.adrPriceDivisor` 와 `meta.exchangeRate` 다. 이 10개사는 둘 다 미설정(=ADR 아님)이었으므로, TSM/BABA 에서 **값이 설정돼 있다면 그 제수가 곧 ADR 환산 비율**이다. 통화·ADS 비율 검증의 출발점으로 쓰면 된다.
- **StockAnalysis 는 추정 갱신시각과 제공사를 선언한다.** `trust.lastUpdated`·`lastChecked`·`freshnessLag`, `estimatesSource:"spg"`(S&P Global Market Intelligence). Nasdaq 에는 없는 정보다.
- 재현 스크립트: `collect_sec.py`(SEC), `extract_vendor_meta.py`(공급사 표기), `extract_freshness.py`(갱신시각), `verify_basis.py`(GAAP 대조). SEC 는 식별 가능한 User-Agent 를 요구하며 개인 연락처를 넣지 않았다.

## 8. 산출물

| 파일 | 내용 |
|---|---|
| `REPORT-05.md` | 이 보고서 |
| `CHANGELOG-05.md` | 수정 이력 (R1 단정 철회, R2 재분류, R3 요건 미추가) |
| `sec-05.json` | SEC 법인·회계연도·제출 이력·분기 GAAP EPS |
| `vendor-meta-05.json` | 공급사 표기(제공사·통화·CIK·ADR 제수) |
| `freshness-05.json` | 추정 갱신시각 10개사 |
| `basis-verification-05.json`, `.txt` | 공급사 EPS 대 SEC GAAP 대조 |
| `contract-fields-05.json` | 계약 5.1 필드별 충족/미확인 |
| `raw-05/` | 새 조회 원문 스냅샷 38건 (SEC 30건 = 기업당 submissions·희석·기본, 공급사 정의 탐색 8건) |
| `collect_sec.py`, `probe_definitions.py`, `extract_vendor_meta.py`, `extract_freshness.py`, `verify_basis.py`, `verify_contract_fields.py` | 수집·검증 스크립트 |

`a74c15e` 원자료(`raw/`, `collect-raw.json`, `collect-extra.json`, `evidence.json`, `tables.md`, `verify-output.txt`)는 **무변경**이다. `REPORT.md` 는 §5.1 만 개정했다.

## 9. 범위 밖으로 남긴 것

- 점수·채점 정책·경계값·worker 코드와 문서를 변경하지 않았다. `worker` 는 읽기 전용으로 읽었다.
- §5 의 결정사항을 여기서 결정하지 않았다.
- 새 필수요건을 추가하지 않았다.
- 2026-09-02 기준선에 이번 자료를 소급하지 않았다.
- 결제·가입·로그인이 필요한 경로는 보류했고, 조사하지 않은 경로를 부재로 단정하지 않았다.
