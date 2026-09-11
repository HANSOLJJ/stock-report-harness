# MCAP-36 — market_cap 조달 경로 설계 (중간 보고: SEC 주식수 완료, yfinance 대기)

## 0. 결론

**12개사 전부 발행주식수를 확보했다. 0건이던 회사가 하나도 남지 않았다.** 주가는 worker 의 yfinance 등재 확인 뒤에 호출하므로 `market_cap` 산출은 아직이다.

핵심 발견은 하나다. **`companyfacts` 는 차원(클래스별) 사실을 버린다.** `dei:EntityCommonStockSharesOutstanding` 이 0건으로 보이던 회사들은 값이 없는 것이 아니라 **클래스별 축(`CommonClassAMember` 등)에 붙어 있어 `companyfacts` 에서 탈락**한 것이다. 표지 렌더링(`R1.htm`)을 직접 읽으면 전부 나온다.

| 회사 | 주식수 | 기준일 | 경로 |
|---|---:|---|---|
| apple | 14,594,180,000 | 2026-07-17 | companyfacts `dei` |
| microsoft | 7,425,545,491 | 2026-07-23 | companyfacts `dei` |
| amazon | 10,786,313,572 | 2026-07-22 | companyfacts `dei` |
| nvidia | 24,100,000,000 | 2026-08-21 | companyfacts `dei` |
| tesla | 3,949,547,394 | 2026-07-16 | companyfacts `dei` |
| oracle | 2,880,471,000 | 2026-06-12 | companyfacts `dei` |
| **alphabet** | **12,230,000,000** | 2026-07-15 | **표지(차원)** — A 5,868M + C 5,527M + B 835M |
| **meta** | **2,547,506,225** | 2026-07-24 | **표지(차원)** — A 2,205,128,509 + B 342,377,716 |
| **palantir** | **2,403,058,480** | 2026-07-27 | **표지(차원)** — A 2,300,713,329 + B 101,340,151 + F 1,005,000 |
| **spacex-xai** | **13,181,779,945** | 2026-07-28 | **표지(차원)** — A 7,696,293,669 + B 5,485,486,276 |
| **tsmc** | **5,186,504,904** (ADS) | 2025-12-31 | 20-F 표지 원주 25,932,524,521 ÷ 5 |
| **alibaba** | **2,322,546,785** (ADS) | 2026-03-31 | 20-F 대차대조표 원주 18,580,374,278 ÷ 8 |

**지시서의 거친 집계와 다른 점이 하나 있다.** `PLTR`·`GOOGL` 은 `dei` 가 0건인 것은 맞으나 **`us-gaap:CommonStockSharesOutstanding` 이 무차원으로 존재한다**(각 48건·88건). 진짜로 아무 경로도 없던 것은 `META` 와 `SPCX` 둘뿐이었다.

## 1. `companyfacts` 가 차원 사실을 버린다 — 0건의 정체

`SPCX` 10-Q 의 XBRL 컨텍스트 머리가 이것을 직접 보여 준다.

```
0001181412 us-gaap:CommonClassAMember 2026-07-28
0001181412 us-gaap:CommonClassBMember 2026-07-28
```

표지의 `EntityCommonStockSharesOutstanding` 이 **클래스 축에 걸려 두 개로 쪼개져 있다.** `companyfacts` 는 무차원 사실만 싣기 때문에 이 둘이 모두 탈락하고 결과가 0건이 된다.

**그래서 0건은 "회사가 공시하지 않음" 이 아니라 "이 API 가 담지 않음" 이다.** 결측 유형으로는 **`api_scope`** 이고, 회사 미공시도 개념 부재도 아니다(§5).

검증도 됐다. 무차원 값이 있는 회사에서 **클래스 합이 무차원 값과 일치**한다.

| 회사 | 클래스 합 | 무차원 `us-gaap:CommonStockSharesOutstanding` | 차이 |
|---|---:|---:|---:|
| alphabet | 12,230,000,000 | 12,230,000,000 (2026-06-30) | **0** |
| palantir | 2,403,058,480 | 2,402,897,000 (2026-06-30) | 161,480 (0.007%, 기준일 27일 차) |

**무차원 값은 전 클래스 합이다.** 이것이 확인됐으므로 `GOOGL`·`PLTR` 은 어느 경로로 가도 같은 총수가 나온다.

## 2. 복수 클래스 처리 방법 (완료 조건 3)

### 2-1. 총수는 전 클래스 합이다

시가총액은 **회사 전체의 지분 가치**이므로 상장 클래스만 세면 안 된다. 비상장 클래스(GOOGL Class B, META Class B, PLTR Class B·F)도 포함한다.

### 2-2. 가격은 클래스마다 다를 수 있다 — GOOGL 만 실질 문제다

| 회사 | 상장 클래스 | 비상장 클래스 | 처리 |
|---|---|---|---|
| **alphabet** | **A(GOOGL) 5,868M · C(GOOG) 5,527M — 둘 다 상장** | B 835M | **A·C 각자 자기 주가로 곱하고, B 는 A 가격을 쓴다** |
| meta | A 2,205M | B 342M | 전량 A 가격 |
| palantir | A 2,301M | B 101M · F 1M | 전량 A 가격 |
| spacex-xai | A 7,696M | B 5,485M | 전량 A 가격 |

**비상장 클래스에 상장 클래스 가격을 쓰는 근거**는 전환권이다. 이들 B/F 주식은 의결권만 다르고 **경제적 권리가 같으며 1:1 로 보통주로 전환된다.** 전환 비율이 1:1 이 아니거나 경제적 권리가 다르면 이 가정이 깨지므로, **적용 전에 각 사 정관 조항으로 1:1 전환을 확인해야 한다** — 이번 라운드에서는 확인하지 못했고 미확인으로 남긴다.

**Alphabet 만 A 와 C 의 가격이 실제로 다르다.** 하나의 티커 가격으로 12,230M 전부를 곱하면 틀린다. `GOOGL`(Class A)과 `GOOG`(Class C) **두 티커의 주가가 모두 필요하다.** 이것이 yfinance 호출 계획에 영향을 주는 유일한 항목이다.

## 3. ADR 처리 방법 (완료 조건 3)

### 3-1. 약분되지 않는다 — 지적이 맞다

`F6-FX-16` 에서 정리한 "ADR 비율 자동 약분" 은 **분자와 분모가 둘 다 회사 단위일 때** 성립한다. `market_cap` **자체를 만들 때는 주가와 주식수의 단위를 한쪽으로 맞춰야** 하고 약분되지 않는다.

두 경로가 같은 값을 준다.

```
ADS 주가(USD) × ADS 수  =  ADS 주가(USD) × (원주 수 ÷ 비율)
원주 주가(현지) × 원주 수 → USD 환산 필요
```

**앞 경로를 쓴다.** yfinance 가 주는 것이 ADS 주가(USD)이고, 이 경로는 **환율이 아예 개입하지 않는다.** 뒤 경로는 원주 주가(TWD/CNY)와 기준일 환율이 둘 다 더 필요해 오차 원인이 둘 는다.

### 3-2. 통화 — 이 경로에는 환율이 없다

`market_cap` 이 USD 로 나온다. 주가가 USD 이고 ADS 수는 무차원이므로 **`F6-FX-16` 의 연도별 기말환율 함정이 이 계산에는 없다.** 다만 P2 의 `net_cash` 는 현지통화(TWD/CNY)로 공시되므로 **거기서 환율이 필요하다** — §6 에 적는다.

### 3-3. 비율은 원문으로 확인했다

| 회사 | 20-F 문언 | 비율 |
|---|---|---|
| tsmc | `each ADS represents five (5) common shares` | 5 |
| alibaba | `Each ADS represents eight ordinary shares.` · `ADSs, each representing eight ordinary shares, are listed on the NYSE.` | 8 |

지시서의 5:1·8:1 과 일치한다.

## 4. ★ BABA 의 `dei` 표지 값이 감사 대차대조표와 10배 어긋난다

**이번 조사에서 가장 위험한 발견이다.**

| 출처 | 값 | 기준일 |
|---|---:|---|
| `dei:EntityCommonStockSharesOutstanding` (companyfacts) | **1,858,037,427** | 2026-03-31 |
| 20-F FY2026 감사 대차대조표 | **18,580,374,278** | 2026-03-31 |
| `us-gaap:CommonStockSharesOutstanding` | 18,580,374,278 | 2026-03-31 |

**정확히 10배다.** 그리고 `1,858,037,427` 이라는 숫자는 **20-F 원문 어디에도 나오지 않는다**(전문 검색 확인). 대차대조표 문언은 이렇다.

> `18,474,235,708 and 18,580,374,278 shares issued and outstanding as of March 31, 2025 and 2026 respectively`

`dei` 이력을 보면 **FY2026 에서만 기준이 깨진다.**

```
2024-03-31   19,469,126,956   20-F 2024-05-23
2025-03-31   18,474,235,708   20-F 2025-06-26   ← 대차대조표와 일치
2026-03-31    1,858,037,427   20-F 2026-05-20   ← 10배 어긋남
```

**10 은 ADS 비율(8)도 아니고 알려진 주식분할도 아니다.** 태깅 척도 오류로 보이나 원문이 스스로 해소하지 않으므로 원인은 확정하지 않는다.

**영향이 크다.** `dei` 를 그대로 썼으면 BABA 시가총액이 **10배 작게** 나왔고, P1·P2 가 둘 다 `market_cap` 을 분자로 쓰므로 두 파라미터가 함께 틀렸을 것이다. 그리고 **값이 그럴듯한 자릿수라 눈으로는 안 걸린다.**

→ **BABA 는 `dei` 를 쓰지 않고 `us-gaap:CommonStockSharesOutstanding` 을 쓴다.** 감사 대차대조표 문언과 직접 대조해 확정했다.

반대로 **TSM 은 `dei` 가 20-F 표지와 글자 그대로 일치**한다.

> `As of December 31, 2025, 25,932,524,521 Common Shares, par value NT$10 each were outstanding.`

같은 개념이 한 회사에서는 맞고 다른 회사에서는 10배 틀렸다. **개념 이름이 같다고 기준이 같지 않다.**

## 5. 결측 유형 구분 (완료 조건 4)

| 값 | 판정 | 근거 |
|---|---|---|
| META·SPCX·GOOGL·PLTR 의 `dei` 0건 | **API 범위 밖(`api_scope`)** | 회사는 공시했고 개념도 존재한다. `companyfacts` 가 차원 사실을 싣지 않을 뿐이다. 표지 렌더링에서 전부 확보 |
| SPCX 의 `CommonStockSharesOutstanding` 부재 | **개념 부재(상환우선주 구조)** | 상장 전 지분이 `TemporaryEquitySharesOutstanding`·`PreferredStockSharesOutstanding` 에 있었다. 10-Q 표지가 상장 후 클래스별 수를 준다 |
| TSM 주식수의 최신 기준일이 2025-12-31 | **회사 미공시(FPI)** | 외국 사기업이라 분기 보고 의무가 없다. 기준일 대비 **8.1개월** 지연이며 `TSM-EDGAR-29B` 와 같은 사유다 |
| BABA `dei` 의 10배 차이 | **판별 불가(원인)** | 값은 대체 경로로 확정했으나 **왜 그렇게 태깅됐는지는 원문으로 못 가른다.** 미해결로 남긴다 |

## 6. `net_cash` — 정의와 태그 (완료 조건 5, 진행 중)

`F6` P2 가 `(market_cap − net_cash) ÷ revenue_ttm` 이므로 세트로 필요하다. 태그 존재 여부를 12개사에 전수 확인했다(`classes-netcash.json`).

**정의가 회사마다 갈릴 자리가 둘이다.**

1. **현금성자산에 단기투자를 넣는가** — `CashAndCashEquivalentsAtCarryingValue` 만 쓸지 `ShortTermInvestments`·`MarketableSecuritiesCurrent` 를 더할지. MSFT·TSLA 는 `ShortTermInvestments` 를, AAPL·AMZN·NVDA·META·GOOGL 은 `MarketableSecuritiesCurrent` 를 쓴다. **같은 뜻을 다른 개념으로 태깅하므로 기간별 Coalesce 가 필요하다**(`G1-FILL-27B` 규약 3 과 같은 형태).
2. **총차입금에 리스부채를 넣는가** — `OperatingLeaseLiabilityNoncurrent` 가 12사 중 10사에 있다. 리스를 차입으로 볼지가 정의 문제다.

**아직 정의를 확정하지 않았다.** 확정 전에 값을 만들면 `ttm_per`·`ps_ratio` 가 `legacy_unverified` 가 된 경로를 반복한다. 확정 후 산출한다.

이미 드러난 구조적 차이 둘을 적어 둔다.

- **TSM 은 IFRS 라 `LongTermDebt` 계열이 전무**하다. `ifrs-full:LeaseLiabilities` 15건은 있으나 `ifrs-full:Borrowings` 는 0건이라 **차입금이 다른 IFRS 개념에 있다.** 별도 특정이 필요하다.
- **ORACLE 은 `LongTermDebtNoncurrent`·`LongTermDebtCurrent` 가 둘 다 0건**이고 `DebtCurrent` 66건·`LongTermDebt` 1건이다. 개념 선택이 회사마다 갈린다.

그리고 **ADR 2사는 `net_cash` 가 현지통화(TWD·CNY)로 공시**되므로 `market_cap`(USD)에서 빼려면 **기준일 환율이 필요하다.** §3-2 대로 시총 계산에는 환율이 없었으나 **P2 에서는 들어온다.** 연준 H.10 이 allowlist 에 있고 `FX-SOURCE-19` 에서 TWD·CNY 수록을 확인해 뒀다.

## 7. 다음 단계 — yfinance (대기 중)

**worker 의 등재 완료 확인을 받은 뒤에 호출한다.** 그 전까지 호출하지 않았다.

준비된 계획은 이렇다.

- 티커 **13개** — 12개사인데 **`GOOGL` 과 `GOOG` 둘이 필요**하다(§2-2).
- 기준일 `2026-09-02`. **거래일 여부를 먼저 확인**하고 아니면 직전 거래일을 쓰되 그 사실과 실제 사용일을 값마다 남긴다.
- `run.json` 의 `price_as_of` 와 맞춘다.
- 종가 기준을 명시한다(조정종가 아님 — 시총은 실제 거래가 × 주식수다).

## 8. 조건 준수

| 조건 | 결과 |
|---|---|
| yfinance 호출 금지(등재 전) | **호출 0건.** SEC 와 표지 렌더링만 사용 |
| C-13 범위(cash·fcf_ttm) | 건드리지 않음. `net_cash` 는 내 범위 |
| C-13 산출물 | `_raw/` 의 **SEC 원본 스냅샷만** 읽음. 보고서·파생물은 열지 않음 |
| 등록 금지 | 관측 제안 아직 생성 안 함(주가 확보 후) |
| 점수·규칙·승인·원자료 | 변경 없음 |

**SEC 접근에 대한 기록 하나** — `www.sec.gov/Archives` 가 브라우저 User-Agent 에 **403** 을 준다. allowlist 등재 조건이 "User-Agent 표기" 이므로 신원을 밝힌 UA 로 바꿔 200 을 받았고, 요청 간 0.2초 간격을 뒀다. 기존 `fetchlib` 의 기본 UA 는 브라우저 UA 라 **SEC Archives 호출에는 맞지 않는다.** 다음 사람이 같은 403 을 만날 자리다.

## 9. 산출물

| 파일 | 내용 |
|---|---|
| `count_shares.py` | 주식수 후보 개념 전수 집계 |
| `adr_check.py` | ADR 단위 판정 — dei 와 원주 개념의 배수 |
| `fetch_covers.py` | 표지(R1) 조회 — **SEC 신원 UA 적용** |
| `classes_and_netcash.py` | 클래스별 주식수 + `net_cash` 태그 전수 |
| `shares_final.py` | **12개사 주식수 확정** |
| `shares-inventory.json` · `covers.json` · `classes-netcash.json` · `shares-final.json` | 산출 자료 |
| `raw/cover-*.htm` | 표지 원문 보존 |
