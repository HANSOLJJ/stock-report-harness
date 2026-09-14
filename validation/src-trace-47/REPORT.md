# SRC-TRACE-47 — 점수에 들어가는 legacy 25쌍의 상류 원천 추적

## 0. 답

**`없음`(세 목록 어디에도 없는 원천)이 확정인 것은 `11`건이다. 전부 `market_cap` 이고 상류는 `StockAnalysis` 다.**

| 등재 판정 | 건수 | 지표 |
|---|---:|---|
| **`없음`** | **11** | `market_cap` 11 — 상류 **StockAnalysis** |
| **혼합**(allowed + 없음이 한 문면에) | **3** | `net_cash` 2 · `offbalance_B` 1 |
| **귀속 불명** | **1** | `contracted_revenue` 1 |
| **판정 불가**(상류 미기재) | **10** | `arr` 2 · `arr_prior` 2 · `cumulative_raised` 2 · `post_money_valuation` 2 · `ps_ratio` 2 |
| 합 | **25** | |

**`없음` 을 넓게 세면 14건이다** — 확정 11 + 혼합 3(셋 다 `StockAnalysis` 또는 `셀사이드` 를 포함한다). **좁게 세면 11건이다.**

## 1. 대상 25쌍을 어떻게 확정했는가

`legacy_unverified` 전체가 아니라 **점수 경로에 실제로 들어가는 것**만이다. `results.json` 이 참조한 `observation_id` 와 9지표 `legacy_unverified` 의 교집합으로 뽑았다.

| 실행 | 교집합 |
|---|---|
| `ai-scorecard-2026-09-baseline` | 29건 — 지시서와 불일치 |
| **`ai-scorecard-2026-09-obsreg`** | **25건 — 지시서와 지표별 수까지 정확히 일치** |

**기준 실행은 `obsreg` 다.** `arr_prior` 2건은 `baseline` 에 아예 없고 `obsreg` 에만 있다(`PRIV-ARR-30B` 제안이 등록된 결과).

## 2. 추적표

| 지표 | 기업 | 원본 위치 | **상류 원천(문면 그대로)** | **등재** |
|---|---|---|---|---|
| `market_cap` | alphabet·amazon·apple·meta·microsoft·nvidia·oracle·palantir·tesla (9) | 채점표 **L794 절 제목** + L807~820 표 | `StockAnalysis` | **없음** |
| `market_cap` | **tsmc** | 채점표 L822 ✱ | 직접 계산 — 주가 입력은 같은 절(`StockAnalysis`) | **없음** |
| `market_cap` | **alibaba** | 채점표 L823 ✱ | 직접 계산 — 주가 입력은 같은 절(`StockAnalysis`) | **없음** |
| `net_cash` | apple·palantir | 채점표 **L848 절 제목** + 표 `순현금/순부채` 열 | `StockAnalysis 9/2 + 공시` | **혼합** |
| `offbalance_B` | oracle | 규칙 L543·L564·L579 · 상류는 HANDOVER **L44** | `10-K/10-Q 주석(리스 약정·구매 약정) · 셀사이드(Morgan Stanley)` | **혼합** |
| `contracted_revenue` | oracle | 채점표 L543 · 상류는 HANDOVER **L45** | `실적 발표` | **귀속 불명** |
| `arr` | anthropic·openai | 규칙 L664~667 · 채점표 L923~926 | **미기재** | 판정 불가 |
| `arr_prior` | anthropic·openai | 채점표 L341 · 규칙 L165·채점표 L745 | **미기재** | 판정 불가 |
| `cumulative_raised` | anthropic·openai | 규칙 L666~667 · 채점표 L925~926 | **미기재** | 판정 불가 |
| `post_money_valuation` | anthropic·openai | 채점표 L930~931 | **미기재** | 판정 불가 |
| `ps_ratio` | anthropic·openai | 규칙 L649~651 `TTM 매출 배수 추정` | **미기재**(유도값) | 판정 불가 |

전체는 `trace-25.json`.

## 3. 상류가 절 제목에 박혀 있었다

**값마다 출처를 적은 것이 아니라 절 제목에 한 번 적는 방식이었다.** 그래서 값만 보면 안 보인다.

```
채점표 L794   ### 3-1a. 가격 — ⑥ 원자료 (StockAnalysis · 2026-09-02 종가 · 단일 출처)
채점표 L848   ### 3-1a-3. 통합 재무 전수표 — ⑨ 게이트 원자료 (StockAnalysis 9/2 + 공시)
```

**L794 절의 표가 `주가·시총·NTM PER·TTM PER·영업외 비중·P/S` 여섯 열을 담는다.** `market_cap` 11건이 전부 여기서 나온다. **`단일 출처` 라고 못 박혀 있다.**

그리고 `HANDOVER` 에 **입력 데이터 레지스트리**(§2)가 따로 있어 지표별 상류를 표로 정리해 둔다. L35 가 그 이유를 적는다.

> 문서엔 `"StockAnalysis 9/2"` 처럼 **인라인으로만 적혀 있다.** 자동 수집용으로 정리:

| 입력 | 소스(HANDOVER 문면) |
|---|---|
| NTM PER | `StockAnalysis 종목 페이지` "Forward PE" |
| TTM PER · 영업외 비중 | `StockAnalysis` |
| **TTM FCF · 현금 · 순차입 · D/EBITDA** | **`StockAnalysis Financials`** — *"같은 날 같은 출처로 14사 일괄"* |
| 신용등급 · CDS | `S&P 공시 · 뉴스(Bloomberg/Seeking Alpha 인용)` |
| **부외 약정** | **`10-K/10-Q 주석 · 셀사이드(Morgan Stanley)`** |
| **RPO · 백로그** | **`실적 발표`** |

## 4. `net_cash` 2건 — 갈라 적으라고 하신 대로, 다만 예상과 다르다

**지시서 예상은 "상류가 SEC 일 것이므로 `없음` 이 아니라 `allowed 인데 검증 미완`" 이었다. 문면은 그렇게 적혀 있지 않다.**

`net_cash` 값(`+$62.2B`·`+$9.2B`)이 있는 표의 절 제목이 **`(StockAnalysis 9/2 + 공시)`** 다. 그리고 `HANDOVER` 레지스트리는 `현금·순차입` 을 **`StockAnalysis Financials`** 로 적고 *"같은 날 같은 출처로 14사 일괄"* 이라고 덧붙인다.

**즉 문면상 1차 상류는 `StockAnalysis` 이고 `+ 공시` 가 병기돼 있다.** 두 값 각각이 어느 쪽에서 왔는지는 **적혀 있지 않다.**

| 가능한 귀속 | 등재 |
|---|---|
| `StockAnalysis` | **없음** |
| `공시`(SEC 제출물) | **allowed** — 다만 검증 미완 |

**그래서 `allowed 검증 미완` 으로 단정할 수 없고 `없음` 으로도 단정할 수 없다. `혼합` 으로 적고 개별 귀속은 미기재로 남긴다.** 추정하지 말라고 하셨으므로 어느 쪽으로도 접지 않았다.

**참고로 이 두 값은 내가 `MCAP-36` 에서 SEC 원자료로 재현해 본 것들이다** — apple 은 `전체유가증권 − 차입 = 62,173M`(legacy 62.2B 대비 −0.043%), palantir 은 `9,197,699,000`(legacy 9.2B 대비 −0.025%)로 맞았다. **SEC 로 재현된다는 것이 SEC 에서 왔다는 뜻은 아니다.** 재현 가능성과 출처는 다른 문제이고, 문면은 여전히 `StockAnalysis + 공시` 다.

## 5. `offbalance_B` 와 `contracted_revenue`

- **`offbalance_B` oracle `리스 $250B`** — `HANDOVER` L44 가 `10-K/10-Q 주석 · 셀사이드(Morgan Stanley)` 로 적는다. **앞은 `allowed`(SEC), 뒤는 `없음`(Morgan Stanley 는 세 목록에 없다).** 이 값이 어느 쪽인지는 안 적혀 있다 → **혼합**.
- **`contracted_revenue` oracle `RPO $638B`** — `HANDOVER` L45 가 `실적 발표` 로 적는다. **실적 발표가 SEC 8-K 경유면 `allowed`, 회사 IR 사이트면 `없음` 이다.** 문면이 매체를 안 밝힌다 → **귀속 불명**.

**둘 다 `없음` 으로도 `allowed` 로도 세지 않았다.**

## 6. 비상장 10건은 상류 자체가 없다

`arr`·`arr_prior`·`cumulative_raised`·`post_money_valuation`·`ps_ratio` 10건은 **어느 절 제목에도 출처가 없다.** 비상장 ⑥ 절 머리는 이렇다.

```
채점표 L921  **비상장 ⑥** — ⚠️ **정밀도 열위**: ARR은 런레이트라 TTM보다 과대하므로 …
규칙  L655  **🔑 자본효율 — 비상장 ⑥의 보조 지표**
```

**정밀도 경고는 있는데 출처는 없다.** `post_money_valuation` 의 괄호(`2026/5 Series H $65B`·`2026/3 $122B 조달`)는 **라운드 설명이지 출처가 아니다.**

`ps_ratio` 2건은 한 겹 더 멀다 — `밸류÷ARR` 을 TTM 으로 보정한 **유도값**이라 그 자체의 상류가 없고, 재료인 `밸류`·`ARR` 의 상류도 미기재다.

→ **10건 전부 `미기재`.** 상류를 모르므로 **등재 여부를 판정할 수 없다.** 이것은 `없음` 과 다르다 — `없음` 은 "원천이 세 목록에 없다" 이고 `미기재` 는 "원천이 무엇인지 모른다" 다.

## 7. 그래서 무엇이 드러났는가

**`NTMPER-39 §5-3` 에서 연 것이 확인됐다.** `ntm_per` 12건만 상류가 적혀 있다고 봤는데, **실제로는 그것 말고도 적혀 있는 것이 있었다 — 절 제목과 HANDOVER 레지스트리에.** 다만 적혀 있는 것들이 가리키는 곳이 문제다.

| | 건수 |
|---|---:|
| 상류가 **적혀 있고** 그것이 세 목록에 **없는** 원천 | **11** (+혼합 3) |
| 상류가 **안 적혀** 있어 판정 자체가 안 되는 것 | **10** |
| 상류가 적혀 있고 `allowed` 만 가리키는 것 | **0** |

**25건 중 `allowed` 원천만으로 설명되는 것이 하나도 없다.**

그리고 **`market_cap` 11건이 `F6` 의 P1·P2 분자**다. `MCAP-36` 에서 실측 경로를 설계해 뒀으나 주가 원천이 막혀 완성하지 못했고, **현재 값은 `StockAnalysis` 에서 온 채로 점수를 만들고 있다.**

## 8. 조건 준수

| 조건 | 결과 |
|---|---|
| 외부 조회 | **0건.** v1.5 원본 세 문서와 worker 트리(읽기)만 |
| 규칙·관측 수정 | 없음 |
| 배제 원천 되살리기 제안 | 하지 않음 |
| 출처 미기재 시 추정 | **하지 않음.** 10건을 `미기재`·`판정 불가` 로 둠 |
| `net_cash` 2건을 `없음` 과 분리 | §4 — **혼합**으로 갈라 적음. 다만 지시서 예상(SEC)과 문면이 다르다는 것을 함께 보고 |

## 9. 산출물

| 파일 | 내용 |
|---|---|
| `collect25.py` | 점수 경로 참조 관측과의 교집합으로 25쌍 확정 |
| `targets-25.json` | 25쌍 원자료 |
| `trace.py` | 상류 추적과 등재 판정 |
| `trace-25.json` | **추적표 전문** |
