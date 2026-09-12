# NTMPER-39 — NTM PER 이 허용 원천으로 구성 가능한가

## 0. 결론 넷

1. **`ntm_per` 12건의 출처는 v1.5 채점표 HTML(`SRC-v15-html`)이고, 산출 방법이 원문에 문언으로 적혀 있다.** 10사는 벤더 Forward PE 인용, **tsmc·alibaba 2사만 직접 계산**이며 산식이 통째로 공개돼 있다.
2. **허용 원천 셋만으로는 구성할 수 없다. 없다.** 미발표 분기의 애널리스트 컨센서스는 발행사 제출물이 아니므로 SEC 에 존재하지 않는다. **따라서 AGENTS.md 72행은 현재 원천 정책 아래에서 지킬 수 없는 계약이다.**
3. **`연간 EPS 가중 근사` 는 "현 회계연도 남은 개월수 : 차기 회계연도 개월수" 로 연간 EPS 둘을 선형 안분한 것이다.** tsmc 19.40(원문 19.4)·alibaba 16.74(원문 16.7)로 **둘 다 재현된다.**
4. **`reject_proxy` 를 권한다. 다만 어느 쪽을 골라도 점수는 바뀌지 않는다** — 이것이 이번 조사의 핵심 발견이다(§4).

## 1. `ntm_per` 12건의 출처와 산출 방법

### 1-1. 관측 자체가 방법을 들고 있다

12건 전부 `source_id: SRC-v15-html`, `status: legacy_unverified`, `kind: estimate` 이고 **`basis` 에 방법이 기록돼 있다.**

| method | 회사 | 수 |
|---|---|---|
| `vendor_forward_pe_verified_ntm` | meta 17.9 · nvidia 18.0 · alphabet 25.3 · microsoft 25.4 · amazon 27.5 · apple 35.5 · oracle 19.1 · palantir 89.0 · spacex-xai 111.0 · tesla 187.5 | **10** |
| `annual_weighted_proxy` | **tsmc 19.4 ✱ · alibaba 16.7 ✱** | **2** |

벤더는 전부 `StockAnalysis Forward PE (2026-09-02)` 다. `raw` 의 `✱` 가 직접 계산 표식이다.

### 1-2. 원문 문언 — 규칙 md L629

> **NTM PER 정의**: 주가 ÷ 향후 4개 분기 애널리스트 컨센서스 EPS 합. 출처는 StockAnalysis "Forward PE"(역산으로 NTM임을 확인 — 회계연도 마감이 달라도 창이 동일). **데이터가 꼬인 곳(Alibaba, CNY/USD 혼재)은 현 FY·차기 FY EPS를 남은 개월수로 가중해 직접 계산한다.**

파일: `AI기업_채점규칙_v1.5.md` L629 (sha256 `57beb84a…`, `SRC-POLICY-32` 에서 검증).

### 1-3. 2사의 산식이 통째로 적혀 있다 — 채점표 md L822·L823

> ✱ **TSMC는 전부 직접 계산** — ADR 1주 = 보통주 5주, 재무는 TWD. StockAnalysis가 시총 $1.95T·PER 27.9 등 환산이 섞여 있어 ADR 5.19B주 × $415.5 = $2.15T, **NTM EPS = (FY26 107.64×5)×4/12 + (FY27 142.13×5)×8/12 = 653 TWD ÷ 30.5 = $21.4 → 19.4.** TWD 환율 하나로 20선을 넘을 수 있다.

> ✱ **Alibaba NTM은 직접 계산** — StockAnalysis가 CNY/USD를 섞어 forward PE 13.92(FY28 EPS 그대로)를 표시. **FY27 $5.71 × 7/12 + FY28 $8.03 × 5/12 = NTM EPS $6.68 → 16.7.** 시총은 8/26 증자(710M주) 완료 반영, ADS 24.2억 주.

**출처 불명이 아니다.** 값·방법·산식·사유가 모두 원문에 있다. `legacy_unverified` 인 것은 검증 이력이 없다는 뜻이지 유래를 모른다는 뜻이 아니었다.

## 2. 허용 원천만으로 NTM PER 을 구성할 수 있는가 — **없다**

### 2-1. 계약이 요구하는 것

AGENTS.md L72:

> 새 실행에서 상장사 ⑥은 **NTM PER(4개 연속 미발표 분기 YYYYQn, 통화·주식 기준 일치)** 만 채점하고 근사치는 대기한다.

즉 **미발표 4개 분기 각각의 애널리스트 합의 추정치**가 필요하다.

### 2-2. SEC 에 그런 자료가 없다 — 실증

"없다" 를 이름만으로 단정하지 않고 12개사 `companyfacts` 전체에서 미래·추정 어휘(`forecast|estimat|guidance|projec|outlook|consensus|analyst|expected|future`)를 담은 개념을 전수 탐색했다(`verify.py`).

나온 것은 전부 **회계 추정**이었다.

- `RestructuringAndRelatedCostExpectedCost` — 구조조정 예상 비용
- `ShareBasedCompensationArrangement…FairValue…` — 주식보상 공정가치 가정
- `SignificantChangeInUnrecognizedTaxBenefitsIsReasonablyPossibleEstimate…` — 세무 불확실성 추정
- `…FutureMinimumPaymentsRemainderOfFiscalYear` — 약정 최소지급액 스케줄

**애널리스트 합의 추정치는 하나도 없다.** 당연한 결과다 — **컨센서스는 발행사가 만들지 않는다.** 증권사 애널리스트의 예측을 제3자가 집계한 것이고, SEC 제출물은 발행사가 제출하는 문서다. 구조적으로 SEC 에 있을 수 없는 자료다.

`www.federalreserve.gov` 는 H.10 환율이라 해당 없다.

### 2-3. 그래서 AGENTS.md 72행은 지킬 수 없는 계약이다

| 조건 | 상태 |
|---|---|
| 미발표 4개 분기 컨센서스 | **허용 원천에 없음** |
| 그 자료를 주던 원천 | `api.nasdaq.com`·`data.nasdaq.com`·`alphavantage`·`FMP`·`finnhub`·`yfinance` — **전부 닫힘** |
| 계약이 요구하는 채점 | `consensus_4q_sum` |
| 현재 가능한 것 | **없음** |

**배제된 원천을 되살리자는 제안은 하지 않는다.** 그 근거는 `SRC-POLICY-32`·`FX-SOURCE-19`·`DATALINK-14` 에서 내가 직접 세웠고 다시 열 이유가 없다.

**결론: 계약을 지킬 자료가 손에 들어오지 않는다. 이것이 답이다.**

## 3. `연간 EPS 가중 근사` 의 정체와 재현

### 3-1. 가중은 **달력 개월수**에 대한 가중이다

기준일 `2026-09-02` 에서 **현 회계연도의 남은 개월수 : 차기 회계연도에서 끌어오는 개월수**로 연간 EPS 둘을 선형 안분한다. 가중치 합은 항상 12/12 다.

| 회사 | 결산월 | 기준일 기준 남은 개월 | 가중 |
|---|---|---|---|
| TSMC | 12월 | FY2026 의 9·10·11·12 = **4개월** | FY26 × 4/12 + FY27 × 8/12 |
| Alibaba | 3월 | FY2027(2026-04~2027-03)의 9월~익3월 = **7개월** | FY27 × 7/12 + FY28 × 5/12 |

### 3-2. 재현 — 둘 다 재현된다

```
[TSMC]
  FY26 107.64×5 = 538.20 × 4/12 = 179.4000
  FY27 142.13×5 = 710.65 × 8/12 = 473.7667
  NTM EPS = 653.1667 TWD ÷ 30.5 = $21.4153
  PER = 415.50 ÷ 21.4153 = 19.4020      원문 19.4 대비 +0.0020 (+0.01%)  → 재현됨

[Alibaba]
  FY27 $5.71 × 7/12 = 3.3308
  FY28 $8.03 × 5/12 = 3.3458
  NTM EPS = $6.6767
  PER = 111.76 ÷ 6.6767 = 16.7389       원문 16.7 대비 +0.0389 (+0.23%)  → 재현됨
```

**proxy 의 성질이 확정됐다.** 이것은 **연간 추정치 둘의 가중평균**이지 분기 컨센서스가 아니다. 차이는 정밀도가 아니라 **종류**다.

### 3-3. 근사가 실제로 무엇을 놓치는가

- **분기 계절성이 사라진다.** 선형 안분은 연내 분기별 이익 분포를 균등으로 가정한다. TSMC·Alibaba 둘 다 분기 편차가 큰 사업이다.
- **환율이 한 겹 더 들어간다.** TSMC 는 TWD EPS 를 `30.5` 로 나눈다. 원문 스스로 *"TWD 환율 하나로 20선을 넘을 수 있다"* 고 적었고, 실제로 채점표 L239 가 **"20선 −3%, 경계 ⚠️"** 로 표시한다. **환율 가정 하나가 밴드를 가른다.**
- **벤더 값이 있어도 못 쓴 이유가 통화 혼재였다.** 원문이 StockAnalysis 의 TSMC PER 27.9·Alibaba forward PE 13.92 를 **환산이 섞였다는 이유로 기각**했다. 근사는 그 기각의 대체물이다.

## 4. `accept_proxy_with_flag` vs `reject_proxy` — **reject 를 권한다. 다만 점수는 안 바뀐다**

### 4-1. ★ 두 선택지가 같은 결과를 낸다

`worker/scripts/scorecard/calc_f6.py` L199~213 을 읽었다. **두 분기가 모두 `score=None`, `status="pending_data"` 를 돌려준다.**

```python
if choice == "accept_proxy_with_flag":
    # 승인된 F6 정책: 근사 방법은 정식 점수를 만들지 않는다.
    return factor_result(FACTOR, score=None, status="pending_data", ...)
elif choice == "reject_proxy":
    return factor_result(FACTOR, score=None, status="pending_data", ...)
else:
    return factor_result(FACTOR, score=None, status="needs_rule_decision", ..., "C-13")
```

**C-13 이 바꾸는 것은 점수가 아니라 상태 라벨뿐이다** — `needs_rule_decision`(규칙 공백) → `pending_data`(자료 공백). 분류가 옮겨질 뿐 값은 `None` 으로 같다.

`accept_proxy_with_flag` 라는 이름이 "받아들여 채점한다" 로 읽히지만 **구현은 받아들이지 않는다.** 주석이 그 이유를 적는다 — *"승인된 F6 정책: 근사 방법은 정식 점수를 만들지 않는다."*

### 4-2. ★ 그리고 v1.7 에서는 C-13 이 아예 호출되지 않는다

지시서의 `tsmc F6 −3, alibaba F6 −4` 는 **C-13 과 무관한 경로에서 나온 값**이다.

| 실행 | 엔진 | tsmc F6 | alibaba F6 | C-13 관여 |
|---|---|---|---|---|
| `ai-scorecard-2026-09-baseline` | `calc_f6.py` (bands) | `None` / `needs_rule_decision` | `None` / `needs_rule_decision` | **예** |
| `ai-scorecard-2026-09-obsreg` | `calc_f6_params.py` (parameters) | **−3** / `ok` | **−4** / `ok` | **아니오** |

v1.7 은 `mode: parameters` 이고 **`proxy_methods`·`accepted_ntm_methods` 키가 아예 없다.** P1 이 `market_cap / net_income_ttm` 즉 **TTM PER** 이라 `ntm_per` 을 읽지 않는다. track 은 `listed_annual`("ADR/FPI 연간")이다.

**따라서 현행 v1.7 실행에서 C-13 은 이미 무의미하다.** 어느 쪽을 골라도 −3·−4 는 그대로다.

### 4-3. 한 가지 정정

지시서에 `ntm_per` 관측이 *"아무도 안 읽는다"* 고 적혀 있는데 **정확하지 않다.** `calc_f6.py` L155·L200·L222 가 읽는다. 정확한 진술은 **"읽는 쪽이 구버전 엔진(bands 모드)이고, 현행 v1.7 parameters 모드가 읽지 않는다"** 이다. 두 엔진이 공존하며 `schema.py` 가 그것을 명시한다 — *"F6 는 두 모드가 공존한다. v1.5·v1.6 은 NTM PER 단일 구간표(bands), v1.7 은 네 파라미터(parameters)"*.

### 4-4. 그래서 권고

**`reject_proxy`.**

이유는 셋이다.

1. **종류가 다른 값이다**(§3-2). 연간 둘의 선형 안분을 `ntm_per` 이라는 이름으로 저장하면 `arr`/`run_rate`·`net_cash`/`cash` 와 같은 병이 하나 더 생긴다. 이름과 내용이 어긋난 값이 쌓인 자리마다 나중에 사고가 났다.
2. **`accept` 를 골라도 채점되지 않는다**(§4-1). 이름만 수용이고 실제로는 대기다. 고르면 **문서와 동작이 어긋난 상태가 하나 더 는다.**
3. **환율 하나로 밴드가 갈린다**(§3-3). 원문 스스로 경계 ⚠️ 를 달았다.

### 4-5. 그 결과 — 무엇이 어떻게 되는가

| 항목 | reject_proxy 선택 시 |
|---|---|
| v1.7 실행(현행) | **변화 없음.** tsmc −3, alibaba −4 유지. C-13 을 읽지 않는다 |
| baseline 실행(bands) | F6 `None` 유지. 상태가 `needs_rule_decision` → `pending_data` 로 이동 |
| 미결 건수 | blocking 규칙 미결 **1건 감소**. 대신 자료 대기 2건이 명시적으로 남는다 |
| TSMC·Alibaba 의 ⑥ | **bands 모드에서는 영구 미완료.** §2 대로 `consensus_4q_sum` 을 줄 원천이 없기 때문이다 |
| 총점 | tsmc 11, alibaba 6 **그대로**(v1.7 기준) |

**"영구 미완료" 가 옳은 상태라고 본다.** 자료가 없는 것을 근사로 메우면 없다는 사실이 장부에서 사라진다. `pending_data` 로 남아 있어야 원천 정책이 바뀌거나 새 원천이 열릴 때 다시 걸린다.

## 5. C-13 을 확정하려면 무엇이 더 필요한가

**자료는 더 필요하지 않다. 필요한 것은 질문을 바꾸는 것이다.**

C-13 은 *"근사를 채점에 쓸 것인가"* 를 묻는데, §4-1·§4-2 가 보이듯 **어느 답도 점수를 바꾸지 않고 현행 엔진은 그 결정을 읽지도 않는다.** 그러므로 C-13 은 지금 상태로는 확정해도 얻는 것이 상태 라벨 하나뿐이다.

**실제로 막고 있는 것은 그 아래 세 가지이고, 셋 다 사용자·설계 결정이지 조사로 풀리지 않는다.**

1. **AGENTS.md 72행을 어떻게 할 것인가.** §2 대로 지킬 자료가 없다. 세 갈래다 — (a) 계약을 현실에 맞게 고친다(v1.7 이 이미 하는 TTM PER 기반 P1 을 명문화), (b) 계약을 유지하고 상장사 ⑥을 전부 미완료로 둔다, (c) 원천 정책을 바꾼다. **(c)는 내가 제안하지 않는다.**
2. **두 F6 엔진 중 무엇이 정본인가.** bands 와 parameters 가 같은 회사에 대해 `None` 과 `−3` 을 동시에 내고 있다. 정본이 정해지지 않으면 C-13 의 유효 범위도 정해지지 않는다.
3. **`ntm_per` 관측 12건을 어떻게 할 것인가.** 10사는 벤더 인용인데 **그 벤더(StockAnalysis)가 현재 allowlist 에 없다.** 근사 2사만 문제라고 보고 있었으나 실제로는 **12건 전부가 닫힌 원천에서 온 값**이다. 이것이 이번 조사에서 예상 밖으로 나온 사실이고, C-13 보다 범위가 넓다.

**세 번째를 강조한다.** C-13 은 2사의 근사를 묻는 결정인데, 조사해 보니 **나머지 10사도 출처 원천이 닫혀 있어 재확보 경로가 없다.** 근사냐 아니냐 이전에 **12건 전부가 갱신 불가능한 값**이다.

## 6. 산출물

| 파일 | 내용 |
|---|---|
| `verify.py` | SEC 미래·추정 개념 전수 탐색 + 가중 근사 재현 계산 |
| `verify-output.json` | 탐색 결과와 재현 값 |

## 7. 조건 준수

| 조건 | 결과 |
|---|---|
| 규칙·관측·점수·승인 변경 금지 | 변경 없음. 읽기만 함 |
| worker `scorecard/` 읽기 전용 | 읽기만 함 |
| 배제 원천 부활 제안 금지 | 하지 않음. §2-3 에 명시 |
| 값이 없으면 없다고 | §2 — "없다" 로 단정 |
| 재현 안 되면 안 된다고 | §3-2 — **재현됨**(둘 다) |
