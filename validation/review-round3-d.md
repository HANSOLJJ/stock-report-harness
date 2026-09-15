# 리뷰 3차 D 출력·가독성 — needs_fix, HTML 렌더러가 v1.7 을 따라가지 못함

- 일시. 2026-09-15. Gemini 3.8 Flash(C-13 창) 새 대화, **D 첫 실행.** part `review-obsreg` 커밋 `08dddd7`. 기준 `04439f7`.
- 결과. needs_fix. 순위표 숫자는 results 와 일치, 출력 스펙 pass.

## 조율자 확인

| 발견 | 확인 | 성격 |
|---|---|---|
| high · HTML 카드 근거가 기준선 evidence 만 읽음(`render_html.py:467` `b.get("evidence")`), 활성 판단·superseded 가 HTML 에 없음. 817행 안내문도 "기준선 원문을 옮긴 과거 기록" | **사실.** `render_cards` 가 judgments 를 받지 않는다 | **조율자 누락.** FIX-53 1단계 RC-06 지시를 `render_md.py` 에만 적었다. 최종 산출물은 HTML 이다 |
| high · HTML `factor_calc_text` F6 이 `ntm_per`·`valuation_over_arr` 만 처리, v1.7 정본 `parameters`(P1~P4) 분기 없음. 경계 열 항상 `—`. 582·603행에 v1.5 NTM PER 구간 문구 하드코딩 | **사실.** 520·532·538행 분기, 582·603행 문구 | 렌더러 결함(이번 실행이 바꾼 F6 모드) |
| high · 초안 anthropic·openai F6 가 자동 산출(-4, judgment_id 없음)인데 `render_md.py:324` 가 (회사, factor) 쌍만으로 옛 판단을 찾아 `승계 판단 anthropic.F6` 헤더와 `-3 (v1.5: …)` 불릿을 찍음 | **사실.** 초안 379~380행 | 렌더러 결함 — factor 결과의 `judgment_id` 로 찾아야 한다 |
| medium · alibaba ⑨ 활성 판단 `alibaba.F9.obsreg25` 근거에 `그러나 -2 유지` (v1.5 점수) 잔존, 현재 -3 | **사실.** 초안 823행(리뷰의 762행은 행 번호 틀림) | 이번 실행 판단 근거란 — 점수가 바뀐 판단 |
| medium · `vendor_not_in_source_policy: true` 관측 26건이 초안·HTML 에 노출 안 됨 | **사실.** 초안·렌더러 0건 | 불확실성 노출 |
| medium · `stored_vs_recomputed`, net_cash `open_questions` 가 한 줄 경고로만 | 부분 사실 — 경고는 있음 | 노출 수준 판단 |
| low · HTML G3 boundary 표시 누락 | render_md 에만 있음 | HTML 렌더러 |
| low · HTML 580행 "모든 값은 기준선 승계 관측" | **사실** | HTML 낡은 문구 |

## 메모

- HTML 쪽이 통째로 뒤처져 있다. 1·2차 리뷰가 D 를 건너뛴 사이 초안 렌더러만 고쳐 왔다. 반영 과제에서 **초안에서 고친 표시 전부(RC-06 활성 근거, superseded, 대체 수치 ⚠️, 부외 칸 B종, G3 경계, 관측 상태 캡션, source_text_corrections)를 HTML 에 같은 규칙으로** 대게 한다. 가능하면 두 렌더러가 같은 함수를 쓰게.
- C-13 창의 완결성. 발견은 구체적이고 코드 행이 맞았다. 행 번호 하나(762→823)가 틀렸다. 확인 못 한 것은 브라우저 렌더링 하나로 적었다.
