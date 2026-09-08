# C13-DATA-01: TSMC·Alibaba NTM 원자료 확보 검증 보고서 (R8 최종 정정본)

- **문서 버전**: v4.0 (설계진행 R8 피드백: 자료확보 vs 채점적격성 분리 및 회귀검증 반영본)
- **작성일자**: 2026-09-08
- **작업 ID**: `C13-DATA-01`
- **조사 대상 기업**:
  - **TSMC** (티커: NYSE `TSM`, 대만 TWSE `2330.TW`)
  - **Alibaba** (티커: NYSE `BABA`, 홍콩 HKEX `9988.HK`)
- **수행 주체**: C-13 worktree Antigravity 담당
- **참조 문서**:
  - `docs/scorecard/design-guideline.md` (C-13, D-01~D-10, F6 계약)
  - `docs/scorecard/open-items.md` (C-13 결정 대기 및 경계 3% 위험)
  - `scripts/scorecard/calc_f6.py` (F6 자동 산출 계약, 4분기 연속성 검증기)
  - `scorecard/baseline/v1.5/observations.json` (기존 baseline 이관 관측치)
  - Orca 피드백 전문:
    * `msg_bda33bc6cd31` (R1~R6: 역산 단정 금지, BABA 단위/통화 검증, 정의 미확보 표현, 미확보 vs 부재 구분)
    * `msg_3d55133a9087` (R7: BABA Net Income 103.59B 정정, Zacks F1 vs Finviz 구분, 브라우저 미검증)
    * `msg_04fffe9ba299` (R8: 4분기 자료확보와 EPS합 채점적격성 분리, bool/Inf 배제, expected_quarters 검증)

---

## 1. 개요 및 R8 정정 목적

본 보고서는 C13-DATA-01 작업에 대해 설계진행 에이전트가 검토·재현한 지적사항(`msg_04fffe9ba299`, R8)을 충실히 반영하여, **원자료 확보 여부**와 **EPS 합산에 따른 F6 채점 적격성**을 엄격히 분리하고 비정상 입력 배제 및 회귀 검증 체계를 확립한 최종 보고서이다.

### R8 핵심 정정 사항:
1. **[R8-1] 원자료 확보와 F6 채점 적격성의 엄격한 분리**:
   - **원자료 확보 판정**: 개별 분기 컨센서스 EPS가 `0`이거나 음수(`< 0`)인 경우도 시장 관측치로서 유효한 자료 확보로 인정하고 값을 보존함. 0이나 음수라는 이유로 자료 미확보(`None` 또는 결측)로 처리하던 기존 판정 오류를 정정함.
   - **F6 채점 적격성 판정**: `calc_f6.py` 산출 계약에 따라, 4개 분기 자료가 모두 확보되었더라도 **4개 분기 EPS의 합이 0 이하(`sum_4q_eps <= 0`)인 경우**에는 정상적인 PER 배수 산출이 불가능하므로 F6 채점 보류(`pending_data_eps_sum_non_positive`)로 판정함.
2. **[R8-2] 엄격한 비숫자(bool, Infinity, NaN) 배제 로직 (`is_finite_number`)**:
   - Python에서 `isinstance(True, int)`가 `True`로 평가되는 취약점을 차단하기 위해 `isinstance(val, bool)`를 명시적으로 거부.
   - `math.isfinite()`를 통해 `float('inf')`, `float('-inf')`, `float('nan')` 및 문자열 등의 입력을 엄격히 배제함.
3. **[R8-3] `expected_quarters` 입력 검증 강화**:
   - `expected_quarters`가 빈 목록(`[]`), 4개 미만, 또는 중복 분기를 포함할 경우 `all_4q_fulfilled=False` 및 명시적 에러를 반환하도록 안전장치 구현.
4. **[R8-4] 오프라인 Fixture 회귀 검증 7종 전원 통과**:
   - 설계진행이 직접 재현한 3대 오류 사례(`[-1, 0, 2, 3]`, `[True, inf, 2, 3]`, `expected_quarters=[]`) 및 합 0/음수, NaN/-Inf, 실측 2분기, 정상 4분기 양수 케이스를 포함한 7종 fixture 테스트를 구현하고 전원 통과를 확인.

---

## 2. 대상 기업 프로필 및 회계연도 매핑 근거

| 항목 | TSMC | Alibaba |
|---|---|---|
| **미국 상장 티커 / 거래소** | `TSM` / NYSE | `BABA` / NYSE |
| **본국 상장 티커 / 거래소** | `2330` / 대만 증권거래소(TWSE) | `9988` / 홍콩 거래소(HKEX) |
| **주식 기준 (Share Basis)** | ADR (1 ADR = 보통주 5주) | ADS (1 ADS = 보통주 8주) |
| **회사 공식 보고 통화** | 신대만달러 (**TWD**) | 위안화 (**CNY / RMB**) |
| **미국 거래 주가 통화** | 미국 달러 (**USD**) | 미국 달러 (**USD**) |
| **회계연도 결산월** | 12월 31일 | 3월 31일 |
| **직전 확정 실적 분기** | 2026 Q2 (2026-06-30 종료) | FY2027 Q1 (2026-06-30 종료) |
| **차기 미발표 4분기 매핑 근거** | 회계연도 12월 종료 기준, 차기 4분기는 **2026 Q3(`0q`), 2026 Q4(`+1q`), 2027 Q1(`+2q`), 2027 Q2(`+3q`)**에 대응됨. | 회계연도 3월 종료 기준, 차기 4분기는 **FY27 Q2(`0q`), FY27 Q3(`+1q`), FY27 Q4(`+2q`), FY28 Q1(`+3q`)**에 대응됨. |

---

## 3. 공급사별 원자료 조사 결과 (R7/R8 검증 종합)

### 3.1 Yahoo Finance (yfinance API 및 웹 실측)

- **조사 엔드포인트**: `https://finance.yahoo.com/quote/TSM/analysis/`, `https://finance.yahoo.com/quote/BABA/analysis/` 및 `yfinance` 모듈
- **조사 시각**: 2026-09-08 22:08 KST
- **동적 분기 충족 검증 (`evaluate_quarterly_fulfillment`)**:
  - 기대 기간키: `['0q', '+1q', '+2q', '+3q']`
  - 실제 수신 키: `['0q', '+1q', '0y', '+1y']`
  - 유효 분기 관측: `0q`, `+1q` (2개 분기)
  - 결측 분기: `+2q`, `+3q` (2개 분기 결측)
  - **동적 계산 결과**: `fulfilled_count: 2`, `missing_count: 2`, `all_4q_fulfilled: false`, `scoring_status: pending_data_missing_quarters`.
- **TSMC 세부 수치 대조**:
  - 현재 주가: **$428.91 USD**
  - `forwardPE`: **19.56251**
  - `forwardEps`: **$21.9251 USD**
  - `0q` (2026 Q3): 예상 EPS **$4.45297 USD**
  - `+1q` (2026 Q4): 예상 EPS **$4.95689 USD**
  - `+1y` (FY2027 연간): 예상 EPS **$21.86117 USD**
  - **산식 검산 및 한계**:
    * `Price / forwardEps` = $428.91 / $21.9251 = **19.56251**로 데이터 딕셔너리 내 항등식 일치 확인.
    * 그러나 `forwardEps`($21.9251)와 `+1y`($21.86117) 사이에 **$0.06393의 차이**가 존재함.
    * Yahoo Finance 공식 문서에서 `forwardEps`의 대상 기간 정의를 명시한 공식 문서는 무료 채널에서 확보되지 않음 (`unobtained_definition_document`).
- **Alibaba 세부 수치 대조**:
  - 현재 주가: **$113.24 USD**
  - `forwardPE`: **12.196245**
  - `forwardEps`: **$9.284824 USD**
  - `0q` (FY27 Q2): 예상 EPS **10.98 CNY** (통화: CNY)
  - `+1q` (FY27 Q3): 예상 EPS **14.87 CNY** (통화: CNY)
  - `+1y` (FY2028 연간): 예상 EPS **62.73 CNY**
  - **산식 검산 및 한계**:
    * `Price / forwardEps` = $113.24 / $9.284824 = **12.19625**로 항등식 일치 확인.
    * 분기 수치는 CNY이며 주가 및 forwardEps는 USD로 표시됨. Yahoo 내부의 통화 환산 및 기간 산출 공식에 대한 공식 정의 문서는 미확보(`unobtained_definition_document`) 상태임.

### 3.2 StockAnalysis (R7 정정사항 유지 및 재확인)

- **조사 엔드포인트**: `https://stockanalysis.com/stocks/baba/forecast/`, `https://stockanalysis.com/stocks/tsm/forecast/`
- **원문 테이블 수치 (BABA)**:
  - **하단 각주**: `<div class="mt-0.5 pl-px text-sm text-muted">EPS and Forward PE are based on non-GAAP adjusted numbers. Financial currency is CNY.</div>`
  - 매출(Revenue): FY2026 1.02T, FY2027 1.12T (CNY)
  - **영업이익(Operating Income): FY2026 62.98B**, FY2027 89.75B (CNY) *(62.98B는 Operating Income임)*
  - **당기순이익(Net Income): FY2026 103.59B**, FY2027 85.76B (CNY) *(순이익 수치 정정 완료)*
  - 주당순이익(EPS): FY2026 3.35, FY2027 5.71
- **단위 상태 (`currency_or_share_basis_unconfirmed`)**:
  - 각주에 `Financial currency is CNY`로 기재되어 있으나, EPS 5.71이 보통주 기준인지 ADS 기준인지, 혹은 USD 환산치인지 개별 필드 단위가 원문에 명시되지 않음.
  - GAAP vs non-GAAP 조정, 주식수, 집계 표본 일치 근거 없이 역산하여 충돌을 단정하지 않고 **`currency_or_share_basis_unconfirmed` (통화 및 주식단위 미확인)**으로 유지함.
- **Quarterly 토글 상태 (`browser_path_unverified`)**:
  - 정적 파싱만 수행하였으며 브라우저 세션에서 Quarterly 토글 후 실제 데이터 렌더링/차단 모달 여부를 실사하지 않았으므로 **`browser_path_unverified`**로 유지함 (유료 결제는 수행하지 않음).
- **공식 산출 정의 상태 (`unobtained_definition_document`)**:
  - 공급사 공식 산출 정의 문서는 조사 범위 내에서 미확보 상태임.

### 3.3 TipRanks

- **조사 엔드포인트**: `https://www.tipranks.com/stocks/tsm/earnings`, `https://www.tipranks.com/stocks/baba/earnings`
- **제공 분기 범위**: 차기 1개 분기(TSMC 2026 Q3 $4.39, Alibaba FY27 Q2 $1.63) 및 과거 실적만 제공, 이후 3개 분기 미제공.
- **미확인 필드**: `gaap_status: unconfirmed`, `estimate_as_of: unconfirmed`.

### 3.4 Zacks Investment Research (Current Fiscal Year F1 명시)

- **조사 엔드포인트**: `https://www.zacks.com/stock/quote/TSM/detailed-earning-estimates`
- **지표 성격**: `P/E (F1)` = 25.97은 **Current Fiscal Year (진행 중인 2026 회계연도 연간 추정치 $16.52)** 기준임. 차기 연도(12/2027 F2, $21.09)와 분리되어 있음.
- **제공 분기**: `Current Qtr (09/2026)` $4.45, `Next Qtr (12/2026)` $4.68의 2개 분기만 제공, 차차기 2개 분기 결측.

### 3.5 Finviz (Next Fiscal Year 명시)

- **조사 엔드포인트**: `https://finviz.com/quote.ashx?t=TSM`
- **지표 성격**: `Forward P/E` = 19.61은 **Next Fiscal Year (차기 회계연도 연간 추정치)** 기준임. Current Fiscal Year를 기준으로 하는 Zacks F1과 대상 기간이 명확히 다름.

### 3.6 회사 공식 IR

- 과거 확정 실적 및 직전 다음 분기 경영진 가이던스만 제공하며, 미래 연속 4분기 시장 EPS 컨센서스는 IR 공시 대상이 아님.

---

## 4. 4분기 충족표 및 회귀 Fixture 검증

### 4.1 오프라인 Fixture 7종 회귀 검증 결과 (`run_offline_fixture_tests`)

`verify_ntm_data.py`에 구현된 7종 오프라인 fixture 테스트를 통해 지적된 3대 오류의 완전한 해결을 검증함:

| Fixture ID | 테스트 시나리오 | 입력값 명세 | 자료 확보 결과 | 채점 적격성 결과 | 검증 결과 |
|---|---|---|---|---|---|
| **Fixture 1** | 0과 음수 EPS 보존 (설계진행 재현 1) | `{"0q": -1.0, "+1q": 0.0, "+2q": 2.0, "+3q": 3.0}` | 4건 모두 정상 확보 (`all_4q_fulfilled=True`) | `sum_4q_eps=4.0 > 0` -> **채점 적격 (`eligible_for_f6_scoring`)** | **PASS** |
| **Fixture 2** | bool 및 Infinity 배제 (설계진행 재현 2) | `{"0q": True, "+1q": inf, "+2q": 2.0, "+3q": 3.0}` | `0q`, `+1q` 결측 처리, 2건만 확보 (`all_4q_fulfilled=False`) | `scoring_eligible=False` (`pending_data_missing_quarters`) | **PASS** |
| **Fixture 3** | 빈 목록/중복/불완전 분기키 (설계진행 재현 3) | `expected_quarters=[]`, `["0q", "0q", ...]` | 0건 확보 (`all_4q_fulfilled=False`), 에러 메시지 반환 | `scoring_eligible=False` (`ineligible_quarters_spec`) | **PASS** |
| **Fixture 4** | 자료 확보 완료 vs 합 $\le 0$ 채점 보류 분리 | 합 = 0.0 (`[-2, -1, 1, 2]`) 및 합 = -3.0 (`[-3, -2, 1, 1]`) | 4건 모두 정상 확보 (`all_4q_fulfilled=True`) | `sum_4q_eps <= 0` -> **F6 채점 보류 (`pending_data_eps_sum_non_positive`)** | **PASS** |
| **Fixture 5** | NaN, -Infinity, 문자열 배제 | `{"0q": nan, "+1q": -inf, "+2q": "invalid", "+3q": None}` | 0건 확보, 4건 결측 (`all_4q_fulfilled=False`) | `scoring_eligible=False` | **PASS** |
| **Fixture 6** | Yahoo Finance 실제 수신 데이터 모사 | `{"0q": 4.45297, "+1q": 4.95689, "+2q": None, "+3q": None}` | 2건 확보, 2건 결측 (`all_4q_fulfilled=False`) | `scoring_eligible=False` (`pending_data_missing_quarters`) | **PASS** |
| **Fixture 7** | 정상 4분기 양수 관측치 | `{"0q": 4.45, "+1q": 4.96, "+2q": 5.10, "+3q": 5.30}` | 4건 모두 정상 확보 (`all_4q_fulfilled=True`) | `sum_4q_eps=19.81 > 0` -> **채점 적격 (`eligible_for_f6_scoring`)** | **PASS** |

### 4.2 실제 관측 데이터 동적 평가 결과

#### TSMC (NYSE `TSM` ADR 기준, 결산월 12월)
- **매핑 근거**: 2026-06-30 종료 2Q 확정 후 미발표 차기 4분기는 `2026 Q3`, `2026 Q4`, `2027 Q1`, `2027 Q2`로 매핑됨.
- **동적 충족 결과**:
  - `0q` (2026 Q3, 종료 2026-09-30): **$4.45** (Yahoo) / **$4.39** (TipRanks) / **$4.45** (Zacks) -> **확보**
  - `+1q` (2026 Q4, 종료 2026-12-31): **$4.96** (Yahoo) / **$4.68** (Zacks) -> **확보**
  - `+2q` (2027 Q1, 종료 2027-03-31): *조사 출처 내 미제공 (None)* -> **결측**
  - `+3q` (2027 Q2, 종료 2027-06-30): *조사 출처 내 미제공 (None)* -> **결측**
- **평가 지표**:
  - `fulfilled_count`: **2**, `missing_count`: **2**
  - `all_4q_fulfilled`: **false**
  - `scoring_eligible`: **false**
  - `scoring_status`: **`pending_data_missing_quarters`**
  - `status`: **`unobtained_in_investigated_sources`**

#### Alibaba (NYSE `BABA` ADS 기준, 결산월 3월)
- **매핑 근거**: 2026-06-30 종료 FY27 Q1 확정 후 미발표 차기 4분기는 `FY27 Q2`, `FY27 Q3`, `FY27 Q4`, `FY28 Q1`로 매핑됨.
- **동적 충족 결과**:
  - `0q` (FY27 Q2, 종료 2026-09-30): **10.98 CNY** (Yahoo) / **$1.63 USD** (TipRanks) -> **확보 (통화 상이)**
  - `+1q` (FY27 Q3, 종료 2026-12-31): **14.87 CNY** (Yahoo) -> **확보**
  - `+2q` (FY27 Q4, 종료 2027-03-31): *조사 출처 내 미제공 (None)* -> **결측**
  - `+3q` (FY28 Q1, 종료 2027-06-30): *조사 출처 내 미제공 (None)* -> **결측**
- **평가 지표**:
  - `fulfilled_count`: **2**, `missing_count`: **2**
  - `all_4q_fulfilled`: **false**
  - `scoring_eligible`: **false**
  - `scoring_status`: **`pending_data_missing_quarters`**
  - `status`: **`unobtained_in_investigated_sources`**

---

## 5. 과거 기준시점(2026-09-02) 재현성 분석

- **조사 출처의 특성**: 조사한 무료 공개 웹 공급사는 실시간 유동 스냅샷만 제공하여 과거 특정 시점(2026-09-02)의 컨센서스를 무료 채널에서 재현할 수 없음.
- **소급 적용 금지**: 현재 시점(2026-09-08)의 관측치를 과거 기준일로 소급 입력하는 것은 framework 계약(`D-08`, `C-17`)상 금지됨.
- **유료 DB 커버리지 유보**: 유료 기관용 데이터베이스(Bloomberg, FactSet, LSEG 등)의 과거 특정일 실제 커버리지 여부는 직접 가입·실사하지 않았으므로 존재를 보장하지 않고 미확인 상태로 유지함.

---

## 6. 결론 및 C-13 정책 영향 분석

### 6.1 조사 범위 한정 결론
1. **조사 출처 내 미확보 (미확보 vs 부재 구분)**:
   - 조사 대상 6개 공개 출처 범위 내에서 TSMC와 Alibaba의 **미발표 연속 4개 분기 EPS 컨센서스는 확보되지 않았다 (`unobtained_in_investigated_sources`)**.
   - 이는 해당 6개 출처 내에서의 관측 결과이며, 시장 전체에 데이터가 부재하다는 전칭 주장이 아님. 유료 기관용 DB 등 미조사 영역은 미확인 상태로 둠.
2. **자료 확보와 채점 적격성의 분리 확립**:
   - 0 및 음수 EPS는 정상 자료 확보로 판정하고 유효 숫자로 보존함.
   - 4개 분기 합 $\le 0$인 경우 F6 채점 보류(`pending_data_eps_sum_non_positive`)로 연결하는 F6 계약과의 연계를 명확히 분리함.
3. **공급사 PER 지표의 성격 분리**:
   - Zacks `P/E (F1)`은 **Current Fiscal Year** 기준임.
   - Finviz `Forward P/E`는 **Next Fiscal Year** 기준임.
   - Yahoo Finance와 StockAnalysis는 기간 정의 공식 문서가 미확보(`unobtained_definition_document`) 상태임.
4. **BABA 단위 상태**:
   - StockAnalysis BABA의 경우 주석(CNY)과 EPS 수치(5.71) 간 개별 단위 표기 미비로 인해 **`currency_or_share_basis_unconfirmed`** 상태임.

### 6.2 C-13 정책 영향
- **`reject_proxy` 선택 시**: 조사 출처 내 연속 4분기 NTM 원자료가 미확보 상태이므로, `calc_f6.py` 계약에 따라 TSMC와 Alibaba의 F6는 **`pending_data` (자료 대기)**로 확정됨.
- **`accept_proxy_with_flag` 선택 시**: baseline에 기록된 `annual_weighted_proxy` 수치(TSMC 19.4, Alibaba 16.7)를 참고 정밀도 경고 플래그와 함께 채점에 사용할 수 있음 (단, TSMC는 20 경계선 3% 이내 주의 대상임).

---

*주의: 본 보고서는 순수 사실 증거만을 제공하며, worker 원본 파일, 채점 규칙 및 framework 정책 변경은 수행하지 않는다.*
