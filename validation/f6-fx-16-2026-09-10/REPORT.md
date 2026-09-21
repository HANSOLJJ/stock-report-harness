# F6-FX-16 — TSM·BABA 통화 축

- 지시 원문: `msg_e63354d329b7` (run `run_1243c2a83479`)
- 배경: 설계진행 `a4ec258` 의 `validation/f6-redefine-decision.md`
- 기준일: 2026-09-10. 조회 시각은 `sec-fx-16.json` 의 `fetched_at_utc` 참조
- 범위: TSM·BABA 두 종목의 통화 문제만. worker·C-13 의 12개사 태그 인벤토리와 겹치지 않음
- 사용 호스트: `data.sec.gov`, `www.sec.gov` 만. User-Agent `stock-report-harness F6-FX validation (contact via repository issues)`, 요청 간 0.7초 이상 간격

## 0. 결론

**convenience translation 이 있는가: 두 회사 모두 있다. 그리고 XBRL 로 태그돼 있어 기계 판독이 된다.** 20-F 원문을 직접 열어 확인했다. TSM 은 FY2025 20-F 에서 `NT$31.37 = US$1.00`(H.10 연준 고시, 2025-12-31 기준), BABA 는 FY2026 20-F 에서 `RMB6.8980 = US$1.00`(H.10 연준 고시, 2026-03-31 기준)이다. 둘 다 **기말 현물환율**이고 출처가 같다. 매출·순이익·영업이익·매출총이익이 모두 USD 로 태그돼 있어 우리가 환율을 고를 필요가 없다.

**다만 결정적인 단서가 하나 있다. 각 20-F 는 자기 회계연도 한 해만 환산하고, 그 해의 기말 환율을 쓴다.** 그래서 `companyfacts` 에 쌓인 연도별 USD 값은 **연도마다 다른 환율로 환산된 값**이다. 내재 환율을 역산해 확인했다 — TWD 는 27.74~32.79, CNY 는 6.1985~7.2569 범위로 매년 다르고, 각 값의 출처 accession 이 그 해의 20-F 다.

**없다면 환율 기준을 무엇으로 권하는가: 있으므로 원칙적으로 불필요하다.** 다만 폴백이 필요한 구간이 실재한다(§3). 폴백을 쓸 때는 **발행사 자신이 쓰는 기준인 연준 H.10 기말 현물환율**을 권한다. 근거는 두 회사가 독립적으로 같은 출처·같은 기준을 쓴다는 점이다. TSM 은 그 환율 자체를 `ifrs-full:ClosingForeignExchangeRate` 로 태그하므로 SEC 안에서 끝난다. **다만 기간값(매출)과 시점값(시총)의 정합은 판단 사항이라 §4 에 선택지와 권고를 제시하되 확정하지 않는다.**

**P3 는 환산이 필요한가: 필요 없다. 현지통화로 계산해야 한다.** "성장률은 환율이 약분된다" 는 전제는 **두 시점에 같은 환율을 적용할 때만** 성립한다. 공시된 USD 값을 그대로 쓰면 약분되지 않고 환율 변동이 섞인다. 실제 값으로 확인했다.

| | 현지통화 성장률 | 공시 USD 성장률 | 차이 |
|---|---|---|---|
| BABA FY2025→FY2026 | **+2.742%** | +8.085% | **+5.34%p** |
| TSM FY2023→FY2024 | **+33.888%** | +25.028% | **−8.86%p** |

두 해를 **같은 환율**로 환산하면 현지통화 성장률과 소수점까지 정확히 일치한다(검증 완료). 즉 환산은 무의미한 왕복이므로 **P3 는 현지통화로 계산하고 환산 단계를 두지 않는다.** P3 는 −3 으로 F6 하위 최대 배점인데 BABA 는 2.7% 와 8.1% 가 밴드를 가를 수 있는 차이다.

## 1. 택소노미와 개념 이름 (확인 항목 1)

**BABA 는 `ifrs-full` 이 아니라 `us-gaap` 이다.** 지시서의 예상과 다르다. TSM 만 IFRS 다.

| | TSM | BABA |
|---|---|---|
| CIK | `0001046179` | `0001577552` |
| SEC 등록명 | Taiwan Semiconductor Manufacturing Company Limited | Alibaba Group Holding Limited |
| **택소노미** | **`ifrs-full`** (334개 개념) + `dei`, `srt` | **`us-gaap`** (358개 개념) + `dei` |
| 보고통화 단위 | TWD 313 · **USD 142** · TWD/shares 5 · USD/shares 3 | CNY 317 · **USD 138** · CNY/shares 2 · USD/shares 10 |
| 회계연도 말 | 12-31 | 03-31 |

CIK 는 추측하지 않고 `https://www.sec.gov/files/company_tickers.json` 공식 매핑으로 해석했다.

### F6 파라미터별 개념 이름

| F6 입력 | TSM (`ifrs-full`) | BABA (`us-gaap`) |
|---|---|---|
| 매출 (P2·P3) | **`Revenue`** — TWD, USD | **`Revenues`** — CNY, USD |
| 순이익 (P1) | **`ProfitLoss`** — TWD, USD<br>`ProfitLossAttributableToOwnersOfParent` — TWD, USD | **`NetIncomeLoss`** — CNY, USD<br>`ProfitLoss` — CNY, USD |
| 영업이익 (P4 분모) | **`ProfitLossFromOperatingActivities`** — TWD, USD | **`OperatingIncomeLoss`** — CNY, USD |
| 매출총이익 | `GrossProfit` — TWD, USD | (별도 확인 필요, 이번 범위 밖) |

P1 은 지배주주 귀속(`ProfitLossAttributableToOwnersOfParent` / `NetIncomeLossAvailableToCommonStockholdersBasic`)을 쓸지 총이익(`ProfitLoss`)을 쓸지 정해야 한다. 시총이 지배주주 지분의 가치이므로 지배주주 귀속이 정합적이지만, **12개사 전체에 같은 규칙을 적용하는 문제라 worker·C-13 의 인벤토리 결과와 함께 정하는 것이 맞다.** 여기서 정하지 않는다.

## 2. convenience translation 원문 대조 (확인 항목 2)

인용에 그치지 않고 20-F 원문을 받아 직접 열어 확인했다. 스냅샷은 `raw/20F-TSM-FY2025.html`(10.4MB)·`raw/20F-BABA-FY2026.html`(11.7MB)과 텍스트 추출본이다.

### 2.1 TSM — FY2025 20-F (2026-04-16 제출, 기간 2025-12-31)

**환율 고지 (원문)**

> "This annual report contains translations of certain NT dollar amounts into U.S. dollars at specified rates solely for the convenience of the reader. Unless otherwise noted, all translations from NT dollars to U.S. dollars in this annual report were made at **NT$ 31.37 to US$1.00**, the exchange rate set forth in the **H.10 statistical release of the Federal Reserve Board on December 31, 2025**."

**재무제표 주석 3 (원문)**

> "3. U.S. DOLLAR AMOUNTS — TSMC and its subsidiaries ... maintain its accounts and express its consolidated financial statements in New Taiwan dollars. For convenience only, U.S. dollar amounts presented in the accompanying consolidated financial statements have been translated from New Taiwan dollars at the exchange rate as set forth in the statistical release of the Federal Reserve Board of the United States, which was **NT$ 31.37 to US$1.00 as of December 31, 2025**."

**감사 범위 (원문) — 이 부분이 중요하다**

> "Our audits also comprehended the translation of New Taiwan dollar amounts into U.S. dollar amounts and, in our opinion, **such translation has been made in conformity with the basis stated in Note 3** to the consolidated financial statements."

즉 TSM 의 환산치는 **감사인이 명시적으로 감사 범위에 포함시킨 값**이다. 우리가 환율을 고를 필요가 없다는 판단의 근거가 여기 있다.

**단서.** 같은 20-F 안에서도 항목에 따라 다른 환율을 쓴다. 자본적지출 서술은 **가중평균환율 NT$31.11** 을 쓴다고 명시한다("US$ 40,895 million, translated from a weighted average exchange rate of NT$ 31.11 to US$1.00"). 따라서 "20-F 의 USD 는 전부 31.37" 이 아니다. **재무제표 본문의 USD 열이 31.37 기준**이고, 서술 부분의 일부 수치는 다른 기준일 수 있다.

### 2.2 BABA — FY2026 20-F (2026-05-20 제출, 기간 2026-03-31)

**환율 고지 (원문)**

> "Our reporting currency is the Renminbi. This annual report contains translations of Renminbi and Hong Kong dollar amounts into U.S. dollars at specific rates solely for the convenience of the reader. Unless otherwise stated, all translations ... were made at a rate of **RMB6.8980 to US$1.00** and HK$7.8400 to US$1.00, the respective exchange rates on **March 31, 2026** set forth in the **H.10 statistical release of the Federal Reserve Board**."

**재무제표 주석 (원문) — 환산 범위가 여기 명시된다**

> "Translations of balances in the **consolidated balance sheet, consolidated income statement, consolidated statement of comprehensive income and consolidated statement of cash flows** from RMB into the US$ **as of and for the year ended March 31, 2026** are solely for the convenience of the readers and are calculated at the rate of **US$1.00=RMB 6.8980**, representing the exchange rate set forth in the H.10 statistical release of the Federal Reserve Board on March 31, 2026."

범위가 4대 재무제표 전체로 **매출만이 아니다.** 다만 기간이 **"as of and for the year ended March 31, 2026"**, 즉 **최신 1개 연도로 한정**된다.

**감사 범위 — TSM 과 다르다.** BABA 20-F 전문에서 `comprehended the translation` 문구는 **0건**이다. 환산은 감사받은 재무제표의 주석 안에 있지만, TSM 처럼 감사인이 환산을 감사 범위에 포함한다고 별도로 진술한 문장은 **없다.** 두 회사를 똑같이 "감사받은 환산치" 라고 부르면 과장이므로 구분해 적는다.

### 2.3 연도마다 환율이 다르다 — 가장 중요한 관측

`companyfacts` 에는 여러 해의 USD 값이 쌓여 있는데, **각 값은 그 해의 20-F 에서 온 것이고 그 해의 기말 환율로 환산돼 있다.** 값과 출처 accession 을 대조해 확인했다(`implied-rates.json`).

| 회계연도 | TSM 내재환율 (TWD/USD) | 출처 제출일 | | 회계연도 | BABA 내재환율 (CNY/USD) | 출처 제출일 |
|---|---|---|---|---|---|---|
| 2017 | 29.6400 | 2018-04-19 | | FY2022 | 6.3393 | 2022-07-26 |
| 2018 | 30.6100 | 2019-04-17 | | FY2023 | 6.8676 | 2023-07-21 |
| 2019 | 29.9100 | 2020-04-15 | | FY2024 | 7.2203 | 2024-05-23 |
| 2020 | 28.0800 | 2021-04-16 | | FY2025 | 7.2567 | 2025-06-26 |
| 2021 | 27.7400 | 2022-04-14 | | FY2026 | **6.8980** | 2026-05-20 |
| 2022 | 30.7300 | 2023-04-20 | | | | |
| 2023 | 30.6200 | 2024-04-18 | | | | |
| 2024 | **32.7900** | 2025-04-17 | | | | |

BABA FY2026 의 내재환율 6.8980 은 20-F 고지 환율과 **정확히 일치**한다. TSM 도 각 해 20-F 의 고지 환율과 일치하며, TSM 은 그 환율을 아예 `ifrs-full:ClosingForeignExchangeRate` 로 태그한다(2022-12-31 30.73 / 2023-12-31 30.62 / 2024-12-31 32.79).

**따라서 서로 다른 해의 공시 USD 값을 비율로 쓰면 안 된다.** 이것이 §5 의 P3 결론으로 이어진다.

## 3. 가용성 공백 — TSM 최신 연도가 API 에 없다

**TSM 의 FY2025(2025-12-31)는 `companyfacts` 에 없다.** 20-F 는 2026-04-16 에 제출됐고 원문에는 환율 31.37 과 재무수치가 다 있는데, XBRL API 의 연간 관측은 **TWD·USD 모두 2024-12-31 이 최신**이다. BABA 는 FY2026(2026-03-31)이 정상적으로 들어 있다.

실무적 함의는 이렇다. **오늘 기준으로 `companyfacts` 만 쓰면 TSM 은 FY2024, BABA 는 FY2026 이 최신이 되어 두 회사의 기준 시점이 어긋난다.** P1·P2·P3 를 같은 기준일로 맞추려면 TSM 은 20-F 원문(또는 재무제표 XBRL 첨부)에서 FY2025 를 별도로 가져와야 한다. 원인이 SEC 인덱싱 지연인지 TSMC 의 태그 방식인지는 이번 범위에서 확인하지 않았고 **추측하지 않는다.**

## 4. 환율 출처와 기준일 (확인 항목 3) — 권고안, 확정 아님

convenience translation 이 있으므로 원칙적으로 환율을 고를 필요가 없다. 폴백이 필요한 경우는 셋이다 — TSM FY2025 처럼 API 에 최신 연도가 없을 때, TTM 이 회계연도와 어긋날 때, 그리고 시총 기준일과 환산 기준일을 맞추고 싶을 때다.

### 4.1 출처 후보

| 후보 | 근거 | 접근 |
|---|---|---|
| **연준 H.10 (권고)** | **두 발행사가 독립적으로 같은 출처·같은 기준을 쓴다.** 우리가 임의로 고르는 것이 아니라 공시 관행을 따르는 것이 된다 | `federalreserve.gov`. **v1.6 allowed 목록에 있는지 확인 필요.** 이번 조사에서 호출하지 않았다 |
| **SEC 태그된 환율** | TSM 은 `ifrs-full:ClosingForeignExchangeRate` 로 환율 자체를 태그한다. SEC 안에서 끝나고 별도 호스트가 불필요 | `data.sec.gov`. 이미 allowed |
| **공시 값에서 역산** | 같은 개념의 현지통화 값 ÷ USD 값. BABA 는 환율을 태그하지 않으므로 이 방법이 필요하다. FY2026 역산값 6.8980 이 고지값과 일치함을 확인했다 | `data.sec.gov`. 이미 allowed |
| 상용 FX API | — | 유료·가입 필요. 이번 금지 범위 |

**BABA 는 환율을 태그하지 않는다.** 따라서 BABA 는 역산 또는 20-F 본문 파싱이 필요하다. 역산이 고지값과 일치함을 확인했으므로 역산 경로가 실용적이다.

### 4.2 기준일 — 기간값 대 시점값

매출은 기간 값이고 시총은 시점 값이라는 지적이 정확하다. 선택지는 셋이고 각각 값이 달라진다.

| 안 | 방식 | 장점 | 단점 |
|---|---|---|---|
| **A. 공시 환산 그대로** | 20-F 의 USD 매출을 그대로 사용(그 회계연도 기말 환율) | 재현성이 최고. TSM 은 감사 범위 안. 우리가 고르는 것이 없음 | 환율 기준일이 회계연도 말이라 시총 기준일과 최대 1년 어긋남. BABA FY2026 은 2026-03-31 기준 |
| **B. 기간 평균환율** | 매출 기간의 평균환율로 환산 | 유량(flow)에 대해 경제적으로 가장 타당 | 공시값과 불일치. 외부 FX 출처 필요. 평균의 정의(일평균·월평균)를 또 골라야 함 |
| **C. 시총 기준일 현물환율** | 시총과 같은 날짜의 환율로 매출을 환산 | 분자·분모의 환율 기준일이 완전히 일치. "오늘 시장이 매출 1달러당 얼마를 매기는가" 라는 물음에 정합 | 과거 매출을 오늘 환율로 재평가. 공시값과 불일치. 외부 FX 출처 필요 |

**권고는 A 를 기본으로 하고 C 를 대안으로 둔다.** 근거는 이렇다. F6 는 12개사를 **한 규칙으로 줄세우는** 것이 목적이라 개별 정밀도보다 **일관성과 재현성**이 중요하다. A 는 우리가 고르는 파라미터가 0개이고 TSM 은 감사 범위 안이며 SEC 안에서 완결된다. B·C 는 외부 FX 호스트가 allowed 여야 하고 평균의 정의나 기준일을 또 정해야 해서 자의성이 늘어난다.

다만 **A 의 약점은 실제로 존재한다.** BABA 의 환산 기준일은 2026-03-31 인데 시총은 오늘 기준이다. 그 사이 CNY 가 크게 움직이면 EV/Sales 가 왜곡된다. 시총 기준일과의 정합을 더 중시한다면 C 가 맞다.

**어느 쪽이든 TSM 과 BABA 에 동일하게 적용해야 하고, 선택한 기준을 산출물에 명시해야 한다.** 이 선택은 설계진행·사용자 판단 사항이라 여기서 확정하지 않는다.

## 5. P3 성장률 (확인 항목 4) — 환산 불필요

지시서의 가설은 **조건부로만 맞다.** 같은 환율을 두 시점에 적용하면 약분되지만, **공시된 USD 값은 연도마다 다른 환율로 환산돼 있어 약분되지 않는다.**

`p3-fx-check.txt` 의 실측이다.

```
TSM/Revenue   2023 -> 2024
  현지통화 성장률             33.888 %   (환율 무관)
  USD 성장률 (공시값 그대로)   25.028 %   환율 30.6200 -> 32.7900
  차이(=환율 기여분)           -8.861 %p
  USD 성장률 (두 해 모두 32.7900 로 환산)   33.888 %   현지통화와 일치: 예

BABA/Revenues   FY2025 -> FY2026
  현지통화 성장률              2.742 %   (환율 무관)
  USD 성장률 (공시값 그대로)    8.085 %   환율 7.2567 -> 6.8980
  차이(=환율 기여분)            5.343 %p
  USD 성장률 (두 해 모두 6.8980 로 환산)    2.742 %   현지통화와 일치: 예
```

**같은 환율을 적용하면 현지통화 성장률과 소수점까지 정확히 일치한다.** 즉 환산은 곱했다 나누는 왕복이고 결과를 바꾸지 않는다.

**따라서 P3 는 현지통화(TWD·CNY)로 계산하고 환산 단계를 두지 않는다.** 환산을 넣으면 이득이 없고, 공시 USD 를 그대로 쓰는 실수를 할 여지만 생긴다.

**이 실수의 크기가 작지 않다.** BABA 는 실제 매출성장 2.7% 인데 공시 USD 로 계산하면 8.1% 가 되어 세 배로 부풀고, TSM 은 33.9% 가 25.0% 로 축소된다. P3 는 −3 으로 F6 하위 최대 배점이라 밴드가 갈릴 수 있다. 방향도 반대다 — 현지통화가 절상되면 성장이 부풀고(BABA), 절하되면 깎인다(TSM).

부수적으로, **현지통화로 가면 §3 의 TSM FY2025 공백과 §4 의 기준일 선택이 P3 에는 아예 영향을 주지 않는다.** P3 는 환율 문제에서 완전히 분리된다.

## 6. 정리 — 파라미터별 통화 처리

| 파라미터 | 산식 | 통화 처리 | 근거 |
|---|---|---|---|
| **P1 PER** | `시총 ÷ 순이익` | 순이익을 USD 로 환산 필요 | 시총이 USD. 공시 USD 순이익이 태그돼 있음 |
| **P2 EV/Sales** | `(시총 − 순현금) ÷ 매출` | 매출·순현금을 USD 로 환산 필요 | 위와 동일. §4 의 기준일 선택이 여기 적용됨 |
| **P3 성장률** | `매출 ÷ 전년매출 − 1` | **환산 불필요. 현지통화로 계산** | 환율이 약분됨(§5 실측 검증) |
| **P4 품질보정** | `영업외 비중` = 비율 | **환산 불필요.** 분자·분모가 같은 통화·같은 기간이라 약분 | P3 와 같은 논리 |

**환산이 실제로 필요한 것은 P1 과 P2 뿐이다.** ADR 배수는 회사 단위 계산에서 약분되므로 네 파라미터 모두 무관하다.

## 7. 확인한 것과 확인하지 않은 것

**확인한 것**
- 두 회사의 CIK(공식 매핑), 택소노미, F6 입력별 개념 이름과 단위
- BABA 가 `us-gaap` 이라는 사실 (지시서 예상과 다름)
- 두 20-F 의 convenience translation 문구·환율·기준일·범위를 원문에서 직접 대조
- TSM 은 감사인이 환산을 감사 범위에 포함한다고 명시, BABA 는 해당 문구 없음
- 각 20-F 가 자기 연도만 그 해 기말 환율로 환산한다는 것, 그리고 그것이 `companyfacts` 의 연도별 USD 로 쌓인다는 것
- TSM 이 환율 자체를 `ClosingForeignExchangeRate` 로 태그, BABA 는 미태그
- P3 에서 환율이 약분되는 조건과 공시 USD 사용 시 오차 크기(실측)
- TSM FY2025 가 `companyfacts` 에 부재

**확인하지 않은 것 (추측하지 않음)**
- TSM FY2025 가 API 에 없는 원인
- BABA 의 `GrossProfit` 대응 개념
- 순현금(P2 분모 조정)에 해당하는 개념 이름과 그 USD 태그 여부 — 이번 범위 밖
- P1 에 지배주주 귀속을 쓸지 총이익을 쓸지 — 12개사 공통 규칙 문제라 보류
- 연준 H.10 호스트가 v1.6 allowed 인지 — **호출하지 않았다**
- TTM(분기 누적) 경로의 통화 처리 — 이번은 연간 기준으로만 확인

## 8. 산출물

| 파일 | 내용 |
|---|---|
| `REPORT.md` | 이 보고서 |
| `sec-fx-16.json` | CIK 해석, 택소노미 요약, 개념 목록, 20-F 위치 |
| `usd-coverage.json` | 개념별 USD/현지통화 연간 관측 범위 |
| `implied-rates.json` | 연도별 내재환율과 출처 accession |
| `p3-fx-check.json`, `.txt` | P3 환율 약분 검증 실측 |
| `raw/20F-TSM-FY2025.html`, `.txt` | TSM FY2025 20-F 원문 스냅샷 (10.4MB) |
| `raw/20F-BABA-FY2026.html`, `.txt` | BABA FY2026 20-F 원문 스냅샷 (11.7MB) |
| `raw/sec-*-companyfacts.json`, `sec-*-submissions.json` | SEC API 원문 |
| `raw/sec-company_tickers.json` | CIK 공식 매핑 |
| `collect_sec_fx.py`, `inspect_usd.py`, `implied_rates.py`, `fetch_20f.py`, `p3_fx_check.py` | 수집·검증 스크립트 |

## 9. 조건 준수

- `data.sec.gov`·`www.sec.gov` 만 사용. 식별 가능한 User-Agent 표기, 요청 간 0.7초 이상 간격
- 결제·가입·메일 발송 **없음**. `api.nasdaq.com` 호출 **0건**
- **값 대량 수집 없음.** 개념 목록과 경로 확인, 검증에 필요한 최소 관측만 조회
- **환율을 임의로 정해 넣지 않았다.** 모든 환율은 20-F 원문 고지값이거나 공시값에서 역산한 것이며 출처를 표기했다
- 없는 것은 없다고 적었다 (TSM FY2025 부재, BABA 환율 미태그, BABA 감사 문구 부재)
- 1차 자료를 인용에 그치지 않고 20-F 원문을 직접 받아 열어 대조했다
- 점수·규칙·승인·원자료 변경 **없음**
