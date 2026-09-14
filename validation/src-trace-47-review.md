# SRC-TRACE-47 검토 — 점수에 들어가는 legacy 25쌍의 상류

- 검토일. 2026-09-14. 대상 NTM `496350a`. 판정 **pass.**

## 결과 — 독립 집계와 일치

```
없음 확정   11   market_cap 전부 — 상류 StockAnalysis (채점표 L794 절 제목)
혼합         3   net_cash 2 (StockAnalysis 9/2 + 공시, L848) · offbalance_B 1 (10-K 주석 + Morgan Stanley)
귀속 불명    1   contracted_revenue (실적 발표)
판정 불가   10   arr·arr_prior·cumulative_raised·post_money_valuation·ps_ratio 각 2 — 상류 미기재
합          25   **allowed 만으로 설명되는 것 0건**
```

내 집계 25쌍·9지표·market_cap 11 과 정확히 맞는다. 25행 전부 원본 행 번호 첨부. 794·848·HANDOVER 33~41행 문면 일치.

## 핵심 — 상류는 값이 아니라 절 제목에 있었다

```
L794  ### 3-1a. 가격 — ⑥ 원자료 (StockAnalysis · 2026-09-02 종가 · 단일 출처)
L848  ### 3-1a-3. 통합 재무 전수표 — ⑨ 게이트 원자료 (StockAnalysis 9/2 + 공시)
HANDOVER L35  "문서엔 'StockAnalysis 9/2'처럼 인라인으로만 적혀 있다. 자동 수집용으로 정리:"
HANDOVER L41  | TTM FCF · 현금 · 순차입 · D/EBITDA | StockAnalysis Financials | ...
```

**작성자가 스스로 "인라인으로만 적혀 있다" 고 썼다.** 이관할 때 절 제목을 관측 `basis` 로 옮기지 않아 242건이 null 이 됐다. `nonop_share` 정의가 범례에 있던 것과 같은 사고 — **문서의 구조 정보(제목·범례·레지스트리)를 값과 함께 옮기지 않았다.**

## net_cash 혼합은 관대한 쪽

HANDOVER L41 레지스트리는 현금·순차입을 StockAnalysis 로 등재한다. L848 문면이 "+ 공시" 라 어느 값이 어느 쪽인지 안 갈려 혼합 유지. 내 지시서 예상(SEC)이 틀렸고 NTM 이 문면대로 갈랐다.

## 미기재 10건을 없음과 합산하지 않았다

모르는 것을 나쁜 쪽으로 승격하지 않았다. 규율대로.

## 조치

`SRC-FLAG-49` → worker. market_cap 11건 `vendor_not_in_source_policy` 표시, `stockanalysis.com` 을 `not_adopted`(legacy 상류·재조회 안 함)로 등재, net_cash 2건 혼합 표시, `source_id` 가 원천 검사 밖이라는 note. **되살리기 아님. 장부에 이름을 올리는 것.**
