# F6-AVAIL-15 — SEC 태그 가용성 인벤토리 (F6 재정의 0단계)

작성일 2026-09-10. 담당 worker(HANSOLJJ/worker). 요청 `msg_66f1f0c1c78d`. 근거 결정문 설계진행 `a4ec258`.

**결론 먼저.** 태그는 다 있다. **막히는 것은 태그가 아니라 기간이다.**

| 확인 항목 | 결과 |
|---|---|
| 1 매출 개념 존재 | **12/12** — 다만 **현행 개념이 회사마다 다르고 대부분 2018 년에 한 번 바뀌었다** |
| 2 순이익 | **12/12** (`us-gaap:NetIncomeLoss` 11 · TSM 만 `ifrs-full:ProfitLoss`) |
| 3 영업이익 | **12/12** (`us-gaap:OperatingIncomeLoss` 11 · TSM 만 IFRS) |
| 4 전년 동기 같은 개념 | **9/12** — SPCX 1/2, TSM·BABA 분기 사실 0 |
| 4′ **최근 4 분기 연속 직접 태깅** | **0/12** — **회계 Q4 를 아무도 태깅하지 않는다** |
| 4″ 연간 −(Q1+Q2+Q3) 복원 | **9/12** — TTM 은 이 경로로만 만들어진다 |
| 5 비상장 2 사 전년 ARR | **0/2 · 출처 자체가 없다** |

`api.nasdaq.com` 은 호출하지 않았다. 점수·규칙·승인·원자료는 변경하지 않았다. C-13 에 1~4 가 독립 배정돼 있어 그쪽 산출을 참조하지 않고 `_raw/` 에서만 산출했다.

## 0. 방법과 범위

### 0.1 왜 `companyfacts` 인가

`companyconcept` 은 태그를 하나씩 찍어 보는 것이라 **후보 목록 밖의 개념을 놓친다.** 확인 항목 1 이 "회사별 실제 사용 개념" 이므로 보유 태그 전체를 봐야 한다. 실제로 그 선택이 갈랐다 — NVDA·GOOGL·TSLA·BABA 는 `Revenues` 를 쓰고 나머지 일곱은 `RevenueFromContractWithCustomerExcludingAssessedTax` 를 쓴다.

### 0.2 값을 대량 수집하지 않는다는 조건의 처리

`companyfacts` 는 요청 하나가 그 회사의 **모든 태그와 값**을 통째로 돌려준다. 과제가 이 endpoint 를 지정했으므로 endpoint 는 그대로 쓰되 **저장소에는 파생 인벤토리만 남겼다.**

- 응답 본문은 `_raw/` 에만 두고 `.gitignore` 로 커밋을 막았다.
- 커밋하는 것은 태그 이름·단위 키·기간 축 형태·건수뿐이다(`_derived/inventory.json`, 52 KB).
- 값(매출액·순이익 금액)은 파생물에 **한 건도 담지 않았다.**

### 0.3 SEC 접근

| 항목 | 값 |
|---|---|
| 요청 수 | **13 회** (티커 목록 1 + 12 개사) |
| 요청 간격 | **1.0 초** — SEC 권고 한도(10 req/s)의 10 분의 1 |
| User-Agent | `SEC_UA` 환경변수 우선, 미설정 시 `stock-report-harness F6-AVAIL-15 (contact: hansol.jung@digitalcoms.net)` |
| 결과 | **12/12 HTTP 200** |

User-Agent 의 연락처는 **이 저장소의 커밋 작성자 주소**를 썼다. SEC 공정접근 정책이 요청자 연락처를 요구하고, 그 주소는 이미 저장소 커밋 이력에 들어 있어 새로 노출되는 정보가 아니다. 다른 주소를 쓰기를 원하면 `SEC_UA` 로 덮으면 된다. **판단이 다르면 알려 달라.**

CIK 는 손으로 적지 않고 `www.sec.gov/files/company_tickers.json` 에서 해석했다. 12/12 해석됐고 `entityName` 까지 확인했다.

## 1. 매출 — 개념은 12/12, 그러나 회사마다 다르다

### 1.1 현행 개념

| 현행 개념 | 회사 |
|---|---|
| `us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax` | META · MSFT · AMZN · AAPL · ORCL · PLTR · SPCX (7) |
| `us-gaap:Revenues` | NVDA · GOOGL · TSLA · BABA (4) |
| `ifrs-full:Revenue` | TSM (1) |

**단일 개념으로 12 개사를 훑을 수 없다.** 회사별 매핑 표가 필요하다.

### 1.2 개념은 대부분 2018 년에 바뀌었다 — 항목 4 의 실질

ASC 606 시행에 맞춰 `SalesRevenueNet` 계열이 끊기고 `RevenueFromContractWithCustomer…` 로 넘어갔다. 끊긴 시점이 회사마다 다르다.

| 티커 | 폐기된 개념(마지막 분기) | 현행 개념(마지막 분기) |
|---|---|---|
| META | `Revenues` (2018-09-30) | `RFCWExcludingAssessedTax` (2026-06-30) |
| MSFT | `SalesRevenueNet`·`SalesRevenueGoodsNet` (2018-03-31), `Revenues` (2010-12-31) | `RFCWExcludingAssessedTax` (2026-03-31) |
| AMZN | `SalesRevenueNet`·`Goods`·`Services` (2018-06-30) | `RFCWExcludingAssessedTax` (2026-06-30) |
| AAPL | `SalesRevenueNet` (2018-06-30), `Revenues` (2018-09-29) | `RFCWExcludingAssessedTax` (2026-06-27) |
| ORCL | `SalesRevenue*` (2011~2018), **`Revenues` 분기 2022-05-31 에서 끊김** | `RFCWExcludingAssessedTax` (2026-02-28) |
| PLTR | `RFCWIncludingAssessedTax` (2020-09-30) | `RFCWExcludingAssessedTax` (2026-06-30) |
| TSLA | `SalesRevenueServicesNet` (2014), `SalesRevenueGoodsNet` (2018-06-30) | `Revenues` (2026-06-30) — `RFCWExcludingAssessedTax` 와 **병행 태깅** |
| NVDA · GOOGL | `RFCWExcludingAssessedTax` 가 오히려 먼저 끊김(2020·2025) | `Revenues` |

**전년 동기 대조에는 지장이 없다.** 전환이 2018 년이고 우리가 필요한 구간은 2025~2026 이라 **현행 개념 하나로 전년 동기까지 덮인다**(1.3). 다만 **과거로 더 거슬러 가는 백테스트를 하면 2018 경계에서 개념을 갈아타야 한다.**

### 1.3 ORCL 은 별도로 적는다 — 하마터면 틀릴 뻔한 자리

ORCL 의 `Revenues` 는 **연간이 2026-05-31 까지 최신**이다. 마지막 보고 시점으로 현행 개념을 고르면 이것이 뽑힌다. 그런데 **분기는 2022-05-31 에서 끊겼고**, 2019~2022 의 `Q` 항목은 회계 Q4(3~5 월)만 따로 태깅된 것이다. 현행 분기 계열은 `RFCWExcludingAssessedTax`(2026-02-28)다.

이 조사에서 **개념 선택 기준을 두 번 고쳤다.**

1. 처음에 **사실 개수**로 골랐더니 MSFT·AMZN·AAPL 이 2018 에 끝난 `SalesRevenueNet` 을 현행으로 집었다.
2. **마지막 보고 시점**으로 고쳤더니 ORCL 이 연간만 최신인 `Revenues` 를 집었다.
3. 항목 4 가 묻는 것이 분기 축이므로 **마지막 분기 종료일**을 1 순위로 두어 확정했다.

`inventory.py` 의 해당 주석과 `[4a]` 절 출력에 셋을 모두 남겼다.

### 1.4 후보 목록 밖 개념 — 놓친 것이 없는지 확인했다

후보 7 개 밖에서 이름에 `Revenue`/`Sales` 가 들어간 태그를 전 taxonomy 에서 훑어 `[1b]` 절에 출력했다. 나온 것은 전부 **최상단 매출이 아니다** — `BusinessAcquisitionsProFormaRevenue`(인수 프로포마), `SalesTypeLease*`(리스), `EquityMethodInvestment…Revenue`(지분법 피투자사), `AdvertisingRevenue`(부문), `RevenueFromDividends`·`RevenueFromInterest`(TSM 의 IFRS 금융수익) 등이다. **최상단 매출 개념을 놓치지 않았다.**

## 2·3. 순이익과 영업이익 — 12/12

| 티커 | 순이익 | 영업이익 |
|---|---|---|
| META·NVDA·GOOGL·MSFT·AMZN·AAPL·ORCL·PLTR·TSLA·SPCX | `us-gaap:NetIncomeLoss` [USD] | `us-gaap:OperatingIncomeLoss` [USD] |
| BABA | `us-gaap:NetIncomeLoss` [**CNY·USD**] | `us-gaap:OperatingIncomeLoss` [**CNY·USD**] |
| TSM | `ifrs-full:ProfitLoss` [**TWD·USD**] | `ifrs-full:ProfitLossFromOperatingActivities` [**TWD·USD**] |

**P4 의 `nonop_share` 재계산에 필요한 두 입력이 모두 있다.** 영업이익과 순이익이 같은 회사·같은 기간에 잡힌다. 다만 아래 5 절대로 **기간 축이 분기 단위로는 끊긴다.**

BABA·TSM 이 CNY/TWD 와 USD 두 단위를 함께 갖는다는 사실만 적는다. **어느 쪽이 convenience translation 인지, 환산 기준일이 무엇인지는 판정하지 않았다 — NTM-전망치조사 담당이다.**

## 4. 기간 — 여기가 실제 병목이다

### 4.1 전년 동기는 같은 개념으로 잡힌다 (9/12)

현행 개념 기준으로 최근 4 개 분기 각각에 대해 **1 년 전 같은 분기**가 같은 개념에 있는지 기계로 대조했다(허용 오차 ±10 일 — 52/53 주 회계연도 때문이다).

- **9 개사 4/4.** META·NVDA·GOOGL·MSFT·AMZN·AAPL·ORCL·PLTR·TSLA.
- **SPCX 1/2.** 분기 사실이 `2025-06-30`·`2026-06-30` 둘뿐이라 2025 분기의 전년(2024)이 없다. 상장 전이라 공시가 없었던 것으로 보이나 **단정하지 않는다.**
- **TSM·BABA 0/0.** 분기 기간 사실이 **한 건도 없다.** 20-F 제출사라 연간만 태깅된다.

허용 오차가 실제로 작동한 사례를 `[4b]` 절에 남겼다. NVDA `2025-07-27` ↔ `2024-07-28`(1 일), AAPL `2017-09-30` ↔ `2016-09-24`(6 일)처럼 **정확히 1 년 전 날짜가 아니다.** 날짜 일치로 검사했으면 실패로 잡혔을 자리다.

### 4.2 최근 4 분기 연속 직접 태깅 — **0/12**

**F6 재정의의 가장 큰 제약이다.** 미국 제출사는 **회계 Q4 를 분기로 태깅하지 않는다.** 10-K 에 연간만 싣기 때문이다.

```
META 분기 종료일  … 2024-09-30, [2024-12-31 없음], 2025-03-31, 2025-06-30,
                     2025-09-30, [2025-12-31 없음], 2026-03-31, 2026-06-30
MSFT 분기 종료일  … 2024-12-31, 2025-03-31, [2025-06-30 없음], 2025-09-30,
                     2025-12-31, 2026-03-31
```

MSFT 는 6 월 결산이라 **빠지는 자리가 6 월**이다. 회계 Q4 라는 점은 같다.

**따라서 `revenue_ttm` 을 4 개 분기 단순 합으로 만들 수 없다.** 이것은 F6H-BATCH-10 에서 이미 확인된 사실과 같은 성질이며, 이번에 **매출·순이익·영업이익 전부에 해당한다는 것**을 확인했다.

### 4.3 복원 경로 — 연간 −(Q1+Q2+Q3), 9/12

회계 Q4 = 연간 − (Q1+Q2+Q3) 로 복원한다. 최신 연간 구간 안에 분기 3 개가 있는지 세었다.

| 결과 | 회사 |
|---|---|
| 복원 가능 (연간 구간 안 분기 3 개) | META·NVDA·GOOGL·MSFT·AMZN·AAPL·ORCL·PLTR·TSLA (**9**) |
| 불가 | SPCX(연간 사실 없음) · TSM · BABA(분기 사실 없음) (**3**) |

**복원은 계산이지 조회가 아니다.** 스펙에 쓰려면 세 가지를 정해야 한다.

1. 연간과 분기가 **같은 개념**에서 나와야 한다 — ORCL 은 연간이 `Revenues`, 분기가 `RFCWExcludingAssessedTax` 로 갈릴 수 있다. 이번 조사에서는 현행 개념 기준으로 둘 다 확보됐지만 **개념 혼합 여부를 스펙이 명시해야 한다.**
2. 복원값은 **파생값**이므로 `ttm_per`·`ps_ratio`·`nonop_share` 가 지금 겪는 것과 같은 문제를 반복하지 않으려면 **원자료 3 개(연간·Q1·Q2·Q3)를 함께 저장**해야 한다.
3. 재작성(restatement)이 있으면 같은 기간에 값이 여러 개다. 이번 인벤토리는 `(start,end)` 마다 **가장 최근 `filed`** 하나만 남겼다. 스펙도 같은 규칙을 명시해야 한다.

## 5. 비상장 2 사 전년 ARR — 출처 자체가 없다

저장 자료만 확인했다(네트워크 미사용).

| 확인 | 결과 |
|---|---|
| `arr` 관측 | anthropic 65,000,000,000 USD · openai 40,000,000,000 USD (`as_of` 둘 다 2026-09-02) |
| `arr_prior` | **스키마에 metric 정의 자체가 없다** |
| `period` 필드 | 두 `arr` 관측 모두 `null` — **어느 기간의 값인지 자료에 없다** |
| 출처 | `SRC-v15-rule` — `AI기업_채점규칙_v1.5.md` 이며 **URL 이 없는 문서 인용**이다. 저장소의 3 개 source 전부 v1.5 문서이고 외부 피드가 없다 |

**전년 ARR 을 만들 근거가 저장소 안에 없다.** 억지로 만들지 않았다.

한 가지 더 적는다. `quarter_note` 원문이 anthropic `런레이트 $65B(7월)`, openai `런레이트 $40B+ (8/20)` 다. **지금 `arr` 로 들어 있는 값은 특정 시점의 런레이트이지 기간이 정의된 ARR 이 아니다.** P3 를 ARR 성장률로 두려면 **현재값 쪽의 기간 정의부터** 필요하다. 전년치만의 문제가 아니다.

## 6. 결정문 전제에 대한 정정 두 건

결정문 `a4ec258` 의 0 단계 표를 스키마에서 직접 확인했다. **두 칸이 사실과 다르다.**

| 결정문 서술 | 실제 | 근거 |
|---|---|---|
| `revenue_ttm` — 보유 0/14 | **맞다**(관측 0 개사). 다만 **스키마에는 metric 이 있다** | `schema.METRICS` 에 `revenue_ttm` 존재 |
| **비영업손익 원자료 — "스키마에 없다"** | **틀렸다.** `operating_income_ttm` 이 **스키마에 있다**(관측 0 개사) | `schema.METRICS` 에 존재 |
| `net_income_ttm` — 스키마에 없다 | **맞다** | 부재 확인 |
| `revenue_ttm_prior` — 스키마에 없다 | **맞다** | 부재 확인 |
| `arr_prior` — 스키마에 없다 | **맞다** | 부재 확인 |

**차이가 실무에 미치는 영향.** 신규 metric 정의가 **4 종이 아니라 3 종**이다(`net_income_ttm`·`revenue_ttm_prior`·`arr_prior`). `revenue_ttm`·`operating_income_ttm` 은 **정의가 아니라 값을 채우는 문제**다.

파생값 3 종이 원자료 없이 완제품으로만 있다는 서술은 **맞다.** 수치로 확인했다.

| 파생값 | 관측 | 그 분모·원자료 | 관측 |
|---|---|---|---|
| `ttm_per` | 11 개사 | `net_income_ttm` | **스키마에 없음** |
| `ps_ratio` | 12 개사 | `revenue_ttm` | **0 개사** |
| `nonop_share` | 11 개사 | `operating_income_ttm` | **0 개사** |

**재계산도 검증도 불가하다는 판단은 그대로 선다.**

## 7. 확인된 것과 미확인인 것

### 7.1 저장 자료로 확인된 것

1. 12 개사 `companyfacts` 가 **전부 HTTP 200** 으로 조회된다. TSM·BABA 도 포함이다.
2. 매출 개념이 **12/12** 있고 **현행 개념이 세 갈래**다(1.1).
3. 대부분 **2018 년 전후로 개념이 바뀌었다**. 2025~2026 구간은 현행 개념 하나로 덮인다(1.2).
4. ORCL 은 `Revenues` 의 **연간만 최신이고 분기는 2022 에서 끊긴다**(1.3).
5. 순이익·영업이익이 **12/12** 있다. TSM 만 IFRS 개념이다(2·3 절).
6. 전년 동기가 같은 개념으로 **9/12** 잡힌다(4.1).
7. **회계 Q4 를 직접 태깅하는 회사가 0/12** 다(4.2).
8. 연간 −(Q1+Q2+Q3) 복원이 **9/12** 가능하다(4.3).
9. TSM·BABA 는 **분기 기간 사실이 0 건**이다.
10. 비상장 2 사의 **전년 ARR 출처가 저장소에 없다**(5 절).
11. 결정문의 "비영업손익 원자료가 스키마에 없다" 는 **틀렸다**(6 절).

### 7.2 미확인 — 추측하지 않고 남긴다

1. **TSM·BABA 의 USD 단위가 convenience translation 인지.** NTM 담당이라 판정하지 않았다. 두 단위가 함께 존재한다는 사실만 적었다.
2. **TSM·BABA 의 분기 자료를 다른 경로로 얻을 수 있는지.** 6-K 본문이나 IR 자료는 이번 범위 밖이다. **`companyfacts` 에 없다는 것만 확인했다.**
3. **SPCX 의 전년 분기 부재 사유.** 상장 전이라 공시가 없었을 가능성이 크지만 **자료로 확인하지 않았다.**
4. **재작성(restatement) 빈도와 영향.** `(start,end)` 마다 최신 `filed` 하나만 남기는 규칙으로 처리했을 뿐 **재작성이 얼마나 잦은지는 세지 않았다.**
5. **값의 정확성.** 이번 조사는 **존재와 기간 축만** 본다. 값을 한 건도 검산하지 않았다.
6. **연간과 분기의 개념 혼합 허용 여부.** 스펙 결정 사항이다(4.3-1).
7. **`arr` 현재값의 기간 정의.** 런레이트인지 ARR 인지 자료가 말하지 않는다(5 절).

### 7.3 배분에 미치는 영향 — 잠정 배분은 유지 가능하다

과제가 준 판정 기준으로 답한다.

| 조건 | 결과 |
|---|---|
| 순이익이 없으면 **P1 불가** | 순이익 12/12 존재 → **P1 가능** |
| 매출 전년치가 없으면 **P3 불가** | 전년 동기 9/12, TTM 복원 9/12 → **상장 9 개사 P3 가능 · TSM·BABA·SPCX 는 별도 경로 필요** |
| 영업이익이 없으면 **P4 불가** | 영업이익 12/12 존재 → **P4 가능** |

**따라서 P1 −2 / P2 −2 / P3 −3 / P4 보정 배분을 자료 부재를 이유로 바꿀 필요는 없다.** 다만 셋을 스펙에서 정해야 한다.

1. **회계 Q4 복원 규칙** — TTM 전부가 여기에 걸린다(4.2·4.3).
2. **TSM·BABA 의 분기 경로** — 지금은 연간만 있다. 연간 기준 P3 를 허용할지, 아니면 두 회사를 P3 미산출로 둘지 정해야 한다.
3. **비상장 P3** — 전년 ARR 출처가 없으므로 **ARR 성장률은 지금 산출 불가**다. 현재값의 기간 정의부터 필요하다.

## 8. 재현 방법

```bash
cd worker/validation/f6-avail-15
export SEC_UA="your-app your@email"   # 선택
python collect_facts.py               # SEC 13회 호출 · _raw/ 에 저장(커밋 안 됨)
python inventory.py --json            # inventory-output.txt 와 같은 결과 · _derived/ 갱신
```

`inventory.py` 는 **네트워크를 쓰지 않는다.** `_raw/` 가 없으면 실행되지 않는다.

| 파일 | 커밋 | 내용 |
|---|---|---|
| `collect_facts.py` | O | 수집기. CIK 해석 + `companyfacts` 12 회 |
| `inventory.py` | O | 판정기. 태그 존재·기간 축·전년 동기·TTM 복원 |
| `inventory-output.txt` | O | 실행 결과 |
| `_derived/inventory.json` | O | 파생 인벤토리(52 KB). **값은 담지 않는다** |
| `_raw/**` | **X** | `companyfacts` 원문. `.gitignore` 로 막았다 |
