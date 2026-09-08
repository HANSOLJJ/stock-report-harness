# C13-DATA-01: TSMC·Alibaba NTM 원자료 확보 검증 보고서 (R7 최종 정정본)

- **문서 버전**: v3.0 (설계진행 R7 피드백 잔여 오류 정정본)
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
  - Orca 피드백 전문: `msg_bda33bc6cd31` (R1~R6), `msg_3d55133a9087` (R7 잔여 오류 정정)

---

## 1. 개요 및 R7 정정 목적

본 보고서는 C13-DATA-01 작업의 v2.0 보고서에 대해 설계진행 에이전트가 검토한 추가 지적사항(`msg_3d55133a9087`, R7)을 충실히 반영하여 잔여 오류를 바로잡고 검증 신뢰도를 완성한 최종본이다.

### R7 주요 정정 사항:
1. **[R7-1] 분기 충족표 동적 계산 및 오프라인 Fixture 검증**:
   - `fulfilled_count`, `missing_count`, `all_4q_fulfilled`의 리터럴 하드코딩을 제거하고, 관측 딕셔너리의 유효값(양수 숫자) 존재 여부를 평가하는 함수(`evaluate_quarterly_fulfillment`)로 동적 계산.
   - 0개 분기, 2개 분기, 4개 분기, None/비정상값 등 5종의 오프라인 fixture 단위 테스트를 작성·통과(`run_offline_fixture_tests`).
   - `target_quarters`에 현재 실행 시점의 기업별 회계연도 매핑 근거를 명시하여 재실행 시 라벨 고정 오류 방지.
2. **[R7-2] BABA 원문 행 오독 정정 및 단위 상태 격하**:
   - StockAnalysis BABA 재무표의 FY2026 62.98B 행 오독 정정: **62.98B는 Operating Income**이며, **Net Income은 103.59B**임(FY2027 Net Income은 85.76B).
   - 대략적 주식수와 추정 환율을 결합한 역산 비교는 엄밀한 수학적 증명이 아니므로, `source_conflict` 단정을 철회하고 **`currency_or_share_basis_unconfirmed` (통화 및 주식단위 미확인)**으로 격하.
   - `Financial currency is CNY` 각주는 원문 그대로 보존하되, EPS 필드의 개별 통화 확정과 구분.
3. **[R7-3] StockAnalysis Quarterly 유료벽 단정 정정**:
   - Quarterly 버튼 클릭 후 실제 차단 모달을 브라우저 세션으로 실사하지 않았으므로, '유료벽 차단 단정'을 **`browser_path_unverified` (브라우저 경로 미검증)**으로 정정. 유료 가입/결제는 수행하지 않음.
4. **[R7-4] Zacks F1과 Finviz의 엄밀한 구분 및 정의 미확보 표현 정정**:
   - Zacks F1은 **Current Fiscal Year (현재 진행 중인 2026 회계연도)** 기준이며, Finviz는 **Next Fiscal Year (차기 2027 회계연도)** 기준이므로 같은 차기 연도로 뭉뚱그리지 않고 분리.
   - '공급사 정의 미공개'라는 전칭 단정을 **`공급사 공식 산출 정의 문서 미확보 (unobtained_definition_document)`**로 정정.

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

## 3. 공급사별 원자료 조사 및 R7 정정 결과

### 3.1 Yahoo Finance (yfinance API 및 웹 실측)

- **조사 엔드포인트**: `https://finance.yahoo.com/quote/TSM/analysis/`, `https://finance.yahoo.com/quote/BABA/analysis/` 및 `yfinance` 모듈
- **조사 시각**: 2026-09-08 22:08 KST
- **동적 분기 충족 검증 (`evaluate_quarterly_fulfillment`)**:
  - 기대 기간키: `['0q', '+1q', '+2q', '+3q']`
  - 실제 수신 키: `['0q', '+1q', '0y', '+1y']`
  - 유효 분기 관측: `0q`, `+1q` (2개 분기)
  - 결측 분기: `+2q`, `+3q` (2개 분기 결측)
  - **동적 계산 결과**: `fulfilled_count: 2`, `missing_count: 2`, `all_4q_fulfilled: false`.
- **TSMC 세부 수치 대조**:
  - 현재 주가: **$428.91 USD**
  - `forwardPE`: **19.56251**
  - `forwardEps`: **$21.9251 USD**
  - `0q` (2026 Q3): 예상 EPS **$4.45297 USD**
  - `+1q` (2026 Q4): 예상 EPS **$4.95689 USD**
  - `+1y` (FY2027 연간): 예상 EPS **$21.86117 USD**
  - **산식 검산 및 한계**:
    * `Price / forwardEps` = $428.91 / $21.9251 = **19.56251**로 데이터 딕셔너리 내 항등식 일치 확인.
    * 그러나 `forwardEps`($21.9251)와 `+1y`($21.86117) 사이에 **$0.06393의 수치 차이**가 존재함.
    * Yahoo Finance 공식 문서에서 `forwardEps`의 기간 정의(롤링 12개월인지 연간인지)를 명시한 공식 문서는 무료 채널에서 확보되지 않음 (`unobtained_definition_document`).
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

### 3.2 StockAnalysis (R7-2, R7-3, R7-4 반영)

- **조사 엔드포인트**: `https://stockanalysis.com/stocks/baba/forecast/`, `https://stockanalysis.com/stocks/tsm/forecast/`
- **조사 시각**: 2026-09-08 21:53 KST
- **원문 테이블 수치 재확인 및 행 오독 정정 (R7-2 반영)**:
  - **원문 하단 각주**:
    > `<div class="mt-0.5 pl-px text-sm text-muted">EPS and Forward PE are based on non-GAAP adjusted numbers. Financial currency is CNY.</div>`
  - **원문 표 데이터(BABA)**:
    * 매출(Revenue): FY2026 1.02T, FY2027 1.12T (CNY)
    * **영업이익(Operating Income): FY2026 62.98B**, FY2027 89.75B (CNY) *(이전 보고서의 행 오독 정정: 62.98B는 Net Income이 아니라 Operating Income임)*
    * **당기순이익(Net Income): FY2026 103.59B**, FY2027 85.76B (CNY) *(정정 확인)*
    * 주당순이익(EPS): FY2026 3.35, FY2027 5.71
- **단위 상태 정정 (`currency_or_share_basis_unconfirmed`)**:
  - 하단 각주에는 `Financial currency is CNY`라고 기재되어 있으나, EPS 5.71 수치에 대해 보통주 주당순이익인지 ADS 주당순이익인지, 혹은 USD 환산값인지 개별 필드 단위가 원문에 명시되어 있지 않음.
  - GAAP vs Non-GAAP 조정 항목, 희석/가중평균주식수, 집계 표본의 일치 근거 없이 대략적인 주식수와 환율로 역산하여 충돌을 단정하는 것은 불완전하므로, `source_conflict` 단정을 철회하고 **`currency_or_share_basis_unconfirmed` (통화 및 주식단위 미확인)**으로 처리함.
- **Quarterly 토글 상태 정정 (R7-3 반영)**:
  - 정적 HTML 파싱만 수행하였으며, 웹 UI의 `Quarterly` 토글 버튼을 브라우저 세션에서 실제로 클릭하여 유료 결제 모달이 뜨는지 또는 동적 데이터가 렌더링되는지를 실사하지 않음.
  - 따라서 유료벽 차단 단정을 철회하고 **`browser_path_unverified` (브라우저 경로 미검증)**으로 정정함. (유료 결제/가입은 수행하지 않음).
- **공식 산출 정의 상태 (R7-4 반영)**:
  - StockAnalysis 공식 문서에서 `annual_weighted_proxy` 명칭이나 세부 알고리즘 문서를 확보하지 못하였으므로, **`unobtained_definition_document` (공급사 정의 문서 미확보)**로 표기함.

### 3.3 TipRanks (용어 및 미확인 필드 정정)

- **조사 엔드포인트**: `https://www.tipranks.com/stocks/tsm/earnings`, `https://www.tipranks.com/stocks/baba/earnings`
- **조사 시각**: 2026-09-08 21:58 KST
- **제공 분기 범위**:
  - **차기 1개 분기(upcoming 1 quarter) 및 과거 실적 분기**만 제공.
  - TSMC: 차기 1개 분기인 `2026 (Q3)`(예상 EPS $4.39)만 제공, 이후 3개 분기는 미제공.
  - Alibaba: 차기 1개 분기인 `FY2027 (Q2)`(예상 EPS $1.63)만 제공, 이후 3개 분기는 미제공.
- **미확인 필드 처리**:
  - GAAP vs Non-GAAP 여부 미기재: **`gaap_status: unconfirmed`**
  - 개별 추정치 집계 기준시각 미표시: **`estimate_as_of: unconfirmed`**

### 3.4 Zacks Investment Research (R7-4 반영: Current Fiscal Year F1 명시)

- **조사 엔드포인트**: `https://www.zacks.com/stock/quote/TSM/detailed-earning-estimates`
- **지표 명칭 및 성격**:
  - 지표명: **`P/E (F1)` = 25.97**
  - **성격**: F1은 **Current Fiscal Year (현재 진행 중인 2026 회계연도)** 연간 추정치($16.52) 기준임 (`$428.91 / $16.52 = 25.97`).
  - 차기 연도(Next Fiscal Year, 12/2027 F2)는 $21.09로 별도 분리되어 있음.
  - Zacks F1을 Finviz의 Next Fiscal Year와 동일한 차기 연도로 뭉뚱그리지 않으며, Current Fiscal Year 기준임을 명확히 구분함.
- **제공 분기**: `Current Qtr (09/2026)` $4.45, `Next Qtr (12/2026)` $4.68의 2개 분기만 제공, 차차기 2개 분기 결측.

### 3.5 Finviz (R7-4 반영: Next Fiscal Year 명시)

- **조사 엔드포인트**: `https://finviz.com/quote.ashx?t=TSM`
- **지표 명칭 및 성격**:
  - 지표명: **`Forward P/E` = 19.61**
  - **성격**: Finviz 공식 정의상 **Next Fiscal Year (차기 회계연도 연간 추정치)** 기준임. Current Fiscal Year를 기준으로 하는 Zacks F1과 대상 연도가 다름.

### 3.6 회사 공식 IR

- 과거 확정 실적 및 직전 다음 분기 경영진 가이던스(매출/마진)만 제공. 미래 연속 4분기 시장 EPS 컨센서스는 IR 공시 대상이 아님.

---

## 4. 4분기 충족표 (동적 계산 및 Fixture 검증 완료)

### 4.1 오프라인 Fixture 테스트 결과 (`run_offline_fixture_tests`)
`verify_ntm_data.py`에 내장된 오프라인 fixture 5종 검증 결과:
- **Fixture 1 (0개 분기)**: fulfilled=0, missing=4, all_4q_fulfilled=False -> **Pass**
- **Fixture 2 (키 존재하나 값 None)**: fulfilled=0, missing=4, all_4q_fulfilled=False -> **Pass**
- **Fixture 3 (2개 분기 실측 상황)**: fulfilled=2, missing=2, all_4q_fulfilled=False -> **Pass**
- **Fixture 4 (4개 분기 충족 상황)**: fulfilled=4, missing=0, all_4q_fulfilled=True -> **Pass**
- **Fixture 5 (0, 음수, 문자열 등 비정상값)**: 유효 양수 1개만 충족, 나머지 결측 판정 -> **Pass**

### 4.2 실제 관측 데이터 동적 평가 결과

#### TSMC (NYSE `TSM` ADR 기준, 결산월 12월)
- **매핑 근거**: 2026-06-30 종료 2Q 확정 후 미발표 4분기는 2026 Q3, 2026 Q4, 2027 Q1, 2027 Q2 로 매핑됨.
- **동적 충족 결과**:
  - `0q` (2026 Q3, 종료 2026-09-30): **$4.45** (Yahoo) / **$4.39** (TipRanks) / **$4.45** (Zacks) -> **충족**
  - `+1q` (2026 Q4, 종료 2026-12-31): **$4.96** (Yahoo) / **$4.68** (Zacks) -> **충족**
  - `+2q` (2027 Q1, 종료 2027-03-31): *조사 출처 내 미제공 (None)* -> **결측**
  - `+3q` (2027 Q2, 종료 2027-06-30): *조사 출처 내 미제공 (None)* -> **결측**
- **계산된 충족 수치**: `fulfilled_count: 2`, `missing_count: 2`, `all_4q_fulfilled: false` (동적 계산)

#### Alibaba (NYSE `BABA` ADS 기준, 결산월 3월)
- **매핑 근거**: 2026-06-30 종료 FY27 Q1 확정 후 미발표 4분기는 FY27 Q2, FY27 Q3, FY27 Q4, FY28 Q1 로 매핑됨.
- **동적 충족 결과**:
  - `0q` (FY27 Q2, 종료 2026-09-30): **10.98 CNY** (Yahoo) / **$1.63 USD** (TipRanks) -> **충족 (통화 상이)**
  - `+1q` (FY27 Q3, 종료 2026-12-31): **14.87 CNY** (Yahoo) -> **충족**
  - `+2q` (FY27 Q4, 종료 2027-03-31): *조사 출처 내 미제공 (None)* -> **결측**
  - `+3q` (FY28 Q1, 종료 2027-06-30): *조사 출처 내 미제공 (None)* -> **결측**
- **계산된 충족 수치**: `fulfilled_count: 2`, `missing_count: 2`, `all_4q_fulfilled: false` (동적 계산)

---

## 5. 과거 기준시점(2026-09-02) 재현성 분석

- **조사 출처의 특성**: 조사한 무료 공개 웹 공급사는 실시간 유동 스냅샷만 제공하여 과거 특정 시점(2026-09-02)의 컨센서스를 무료 채널에서 재현할 수 없음.
- **소급 적용 금지**: 현재 시점(2026-09-08)의 관측치를 과거 기준일로 소급 입력하는 것은 framework 계약(`D-08`, `C-17`)상 금지됨.
- **유료 DB 커버리지 유보**: 유료 기관용 데이터베이스(Bloomberg, FactSet, LSEG 등)의 과거 특정일 실제 커버리지는 직접 가입·실사하지 않았으므로 존재를 보장하지 않고 미확인 상태로 유지함.

---

## 6. 결론 및 C-13 정책 영향 분석

### 6.1 조사 범위 한정 결론
1. **조사 출처 내 미확보**: 조사 대상 6개 공개 출처(Yahoo Finance, StockAnalysis, TipRanks, Zacks, Finviz, 회사 IR) 범위 내에서 TSMC와 Alibaba의 **미발표 연속 4개 분기 EPS 컨센서스는 확보되지 않았다 (미확보/접근제한)**. 이는 해당 출처 내에서의 관측 결과이며, 시장 전체에 데이터가 존재하지 않는다는 전칭 주장이 아니다.
2. **공급사 PER 지표의 성격 분리**:
   - Zacks `P/E (F1)`은 **Current Fiscal Year** 기준임.
   - Finviz `Forward P/E`는 **Next Fiscal Year** 기준임.
   - Yahoo Finance와 StockAnalysis는 기간 정의 공식 문서가 미확보(`unobtained_definition_document`) 상태임.
3. **BABA 단위 상태**: StockAnalysis BABA의 경우 주석(CNY)과 EPS 수치(5.71) 간 개별 단위 표기 미비로 인해 **`currency_or_share_basis_unconfirmed`** 상태임.

### 6.2 C-13 규칙 결정 영향
- **`reject_proxy` 선택 시**: 조사 출처 내 연속 4분기 NTM 원자료가 미확보 상태이므로, `calc_f6.py` 계약에 따라 TSMC와 Alibaba의 F6는 **`pending_data` (자료 대기)**로 확정됨.
- **`accept_proxy_with_flag` 선택 시**: baseline에 기록된 `annual_weighted_proxy` 수치(TSMC 19.4, Alibaba 16.7)를 참고 정밀도 경고 플래그와 함께 채점에 사용할 수 있음. (단, TSMC는 20 경계선 3% 이내 주의 대상임).

*주의: 본 보고서는 순수 사실 증거만을 제공하며, worker 원본과 채점 규칙 및 정책 변경은 수행하지 않는다.*
