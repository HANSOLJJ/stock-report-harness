---
slug: ai-scorecard-2026-10-rescore
report_type: ai_scorecard
status: pass
created_at: 2026-10-06
plan_source: output/ai-scorecard-2026-10-rescore/plan.md
research_source: output/ai-scorecard-2026-10-rescore/research.md
draft_source: output/ai-scorecard-2026-10-rescore/draft.md
results_hash: e279d193d30137ee25dcd9b90a11196dcca280e803db718c371760376420bee0
draft_hash: 1bbf20715c81cc0138286c8d7a66f7d8c6a776b652da5b0a65bdb0b63e2fcca2
review_type: separate-session-4way
review_execution: separate_subagent_sessions
reviewers:
  - "fact-sources: Claude Opus 5.5 fact-checker 독립 세션 fc-opus55-20261006-rescore-r1 · round 5 pass"
  - "financial-calc: Claude Opus 5.5 general-purpose 독립 세션 rescore-1007-financial-calc-r5 · round 5 pass"
  - "rule-consistency: Claude Opus 5.5 general-purpose 독립 세션 rc-rescore-20261007-r5 · round 5 pass"
  - "output-readability: Claude Opus 5.5 report-designer 독립 세션 rd-opus55-20261007-rescore-r5 · round 5 pass"
---
# 리뷰 — 2026-10 정기 재채점

각 영역은 가능하면 독립 세션에서 검토하고 실제 수행자·결과를 남긴다. 수행하지 않은 검토를 pass 로 표시하지 않는다.

## 검토 영역

| 영역 | 검토 대상 | 검토자 | 결과 | 요약 |
| --- | --- | --- | --- | --- |
| 사실·출처 | 숫자·기업 귀속·기준 시점·공시·뉴스·부재 주장 | Claude Opus 5.5 fact-checker 독립 세션(`review-parts/fact-sources.md`) | pass | 재작성 판단 114개·요약 14개를 문장 단위로 대조했다. 확인 리뷰에서 Oracle ⑤ 의 'Stargate $7B 출자'가 10-Q·10-K 에 없음을 잡았고, PRP-142 로 +1 로 되돌린 문장이 원문과 맞는다. 요약 14개의 숫자·순위가 results 와 맞다 |
| 재무 계산 | EPS·환율·ADR·TTM·FCF·런웨이·약정·단위·부호 | Claude Opus 5.5 독립 세션(`review-parts/financial-calc.md`) | pass | 14개사 ⑥·⑨ 재계산이 results 와 14/14 일치한다. Microsoft 분기 FCF 여덟 분기를 companyfacts 로 다시 계산해 판단 문장과 맞다. 아마존 여신 메모가 계산(2026-06-30 공시 $37.5B)과 맞다 |
| 규칙 일관성 | factor 정의·상하한·예외·중복 속성·정성 승계·전 기업 동일 기준 | Claude Opus 5.5 독립 세션(`review-parts/rule-consistency.md`) | pass | 1차 needs_fix 네 건(nvidia.F3·oracle.F5·tesla.F4·microsoft.F9)과 확인 리뷰 needs_fix 두 건(nvidia.F5·openai.F4)이 닫혔다. 이번 실행이 새로 댄 잣대(⑥ 트랙·최근 1년 창·여신, ④ 출하·실제 배포만, 분기 실측 FCF 추세)는 닿는 회사에 모두 닿았다. nvidia.F5 는 승계 판단 예외 TEN-RC-03 이다 |
| 출력·가독성 | 표·카드·근거·차트·이력 일치, 낡은 비교 문장, 모바일·단일 HTML | Claude Opus 5.5 report-designer 독립 세션(`review-parts/output-readability.md`) | pass | 초안·메모리 렌더 HTML 에 옛 판 표기·이전 판 꼬리표가 0건이다. 카드 요약·머리줄·순위표가 서로 맞다. 320·768·1280px 가로 넘침 0(round 3 실측, 이후 배치 코드 변경 없음) |

결과는 pass / needs_fix / blocked 중 하나. 네 영역이 모두 pass 이고 체크리스트에 fail 이 없을 때만 frontmatter `status: pass`.
**승계 판단 예외(AGENTS.md 리뷰 범위)** — 체크리스트 fail 의 사유가 `carried_score` 로 승계한 판단의 기존 논리이고, 이번 실행이 그 판단에 쓰인 잣대를 바꾸지 않았으며, 규칙 파일 `open_tensions` 에 재검토 시점과 함께 등록됐다면 `status: pass` 를 막지 않는다. 이때 해당 fail 과 **긴장 번호**(예: `TEN-RC-02`)를 근거 칸에 그대로 적는다. 이번 실행이 바꾼 잣대가 닿는 승계 판단은 이 예외가 아니다 — 한 회사에 새 잣대를 댔으면 같은 잣대가 닿는 모든 회사에 대야 한다(Q03).

## 체크리스트

| ID | 검사 초점 | 결과 | 근거 |
| --- | --- | --- | --- |
| Q01 | 이 감점, 다른 칸에서 이미 셌나? | fail | **승계 판단 예외 — TEN-RC-05 · TEN-RC3-04** |
| Q02 | 이 지표가 이 칸의 정의에 맞나? | fail | **승계 판단 예외 — TEN-RC-02 · TEN-RC3-01 · TEN-RC3-03 · TEN-RC3-05 · TEN-RC4-02** |
| Q03 | 회사마다 같은 잣대인가? | fail | **승계 판단 예외 — TEN-RC-03(nvidia.F5 포함) · TEN-RC4-03.** 예외 없는 fail 은 없다. 이번 실행이 새로 댄 잣대 셋이 닿는 회사는 모두 다시 판정됐다.<br>• ④ 출하만: tesla·openai.<br>• FCF 추세: microsoft 를 다시 판정했다. apple·nvidia·palantir·tsmc 는 실측으로 재도 안정이다.<br>• ⑥ 트랙: tsmc·alibaba.<br>• oracle.F5 는 기존 +2 조건을 확인된 사실에 대 +1 이다 |
| Q04 | 시총 크기를 밸류에이션으로 착각했나? | pass | ⑥ 은 비율 잣대이고 변경이 없다 |
| Q05 | 출처가 이해당사자인가? | fail | **승계 판단 예외 — TEN-RA-02(nvidia F2).** openai.F4 는 이해당사자 발표를 점수 근거에서 뺐다. 이해상충 표기는 판정에 넣지 않았다 |
| Q06 | 볼륨인가 가치인가? | pass | 볼륨 지표가 점수 재료로 든 곳이 없다 |
| Q07 | "안 만든 것"을 카운터 포지셔닝으로 셌나? | pass | amazon.F3 문장 그대로다 |
| Q08 | 적대세력을 수로 셌나, 성격으로 셌나? | fail | **승계 판단 예외 — TEN-RC4-03** |
| Q09 | 미래 계획을 현재 점수에 넣었나? | fail | **승계 판단 예외 — TEN-RA-02 · TEN-RA6-01.**<br>• openai.F4·tesla.F4·microsoft.F9 는 계획을 점수 근거에서 뺐다.<br>• spacex-xai.F4 의 Terafab 과 tsmc.F4 의 로드맵·투자액 서술은 점수를 정하지 않아 low 로 적었다 |
| Q10 | 거리를 가속도로 착각했나? | fail | **승계 판단 예외 — TEN-RB-Q10 · TEN-RC4-04** |
| Q11 | 순적자를 실격 사유로 썼나? | pass | ⑨ 게이트 경로로 계산하고, 순적자 실격은 없다 |
| Q12 | ③ 세 기준을 동등하게 쟀나? | fail | **승계 판단 예외 — TEN-RC4-01 · TEN-RC3-05.** nvidia.F3 은 규칙 정의(직전 분기 대비)로 잰다 |
| Q13 | "공짜로 뿌린다"를 곧바로 카운터 포지셔닝으로 셌나? | fail | **승계 판단 예외 — TEN-RC3-05** |
| Q14 | 아직 안 끝난 승부를 끝난 것처럼 쟀나? | pass | 14사 door_closed 가 전부 fail 이다 |
| Q15 | ⑤에서 "공짜 사용자"를 아군으로 셌나? | pass | 공짜 사용자를 동맹으로 세지 않는다 |
| Q16 | ①을 한 채널로만 쟀나? | fail | **승계 판단 예외 — TEN-RC-02 · TEN-RC4-02** |
| Q17 | ②를 "표준 없음"만으로 깎았나? | pass | 변경 없음 |
| Q18 | ⑤에서 관계사를 독립 동맹으로 셌나? | pass | 관계사 처리가 같다. tesla.F4 는 관계사 합작 Terafab 을 배치 전이라 뺐다 |
| Q19 | ⑤에서 "받은 투자"를 곧바로 동맹 +2로 셌나? | fail | **승계 판단 예외 — TEN-RC-03(nvidia.F5).** 받은 투자를 A 에서 빼는 처리는 일관된다. 준 지분 투자를 동맹으로 셀지는 이탈 조건 통일(C-08)과 함께 2026-11 에 재검토한다 |
| Q20 | 조달을 동맹으로 셌나? | fail | **승계 판단 예외 — TEN-RC-03(C-08)** |
| Q21 | 동맹이자 의존인 관계를 한쪽에서만 셌나, 또는 같은 속성을 양쪽에서 셌나? | fail | **승계 판단 예외 — TEN-RC-05 · TEN-RC3-04** |
| Q22 | 지분 평가이익을 ⑦ 순환금융 증거로 셌나? | pass | ⑦ 입력에 평가이익이 없다 |
| Q23 | 벤치마크를 서로 다른 하네스끼리 비교했나? | fail | **승계 판단 예외 — TEN-RA4-01** |

결과는 pass / fail / not_applicable. not_applicable 도 근거가 필요하다.

## 발견 사항

리뷰는 1차 → 수정 한 묶음 → 확인 리뷰 → (사용자 결정 "한 묶음 더 고치고 좁은 확인") 수정 한 묶음 → 좁은 확인 순서로 끝났다. 영역별 경위와 발견 전체는 `review-parts/` 네 파일에 있다.

- **1차 리뷰(round 3, 완결된 문장 재작성 뒤)**: 규칙 일관성 needs_fix 4건. nvidia.F3 가속도 사유가 규칙 기준이 아님, oracle.F5 지분 동맹 +2 조항 미판정, tesla.F4 배치 전 사업을 폭에 넣음, microsoft.F9 FCF 추세를 계획으로 판정. → 제안 PRP-134~137.
  - nvidia.F3 은 10-Q 두 건에서 데이터센터 직전 분기 대비 성장률이 +21%→+18%(감속)라 실패를 유지하고 사유만 규칙 기준으로 다시 썼다(점수 불변).
- **확인 리뷰(round 4)**: needs_fix 는 셋이다. 기업 요약 넷이 옛 점수, oracle.F5 의 둘째 지분 동맹 'Stargate $7B 출자'가 10-Q·10-K 에 없음, tesla.F4 에 댄 잣대가 openai.F4 에 닿지 않음. → PRP-142(oracle.F5 +1 로 되돌림)·143(openai.F4 3)·요약 제안.
- **좁은 확인(round 5)**: 네 영역 pass. nvidia.F5 는 승계 판단 예외 TEN-RC-03(이번 실행이 '지분 동맹 복수 → +2' 를 새로 댄 회사가 없고, 투자처 이탈 조건을 2026-11 에 재검토).
- **이번 실행 점수 변화(시험 실행 대비)**: TSMC ⑥ −3→−2, Oracle ⑥ −2→−1, Alibaba ⑥ −4→−5·⑨ −3→−4, Microsoft ⑨ 0→−1, Tesla ④ 4→3, OpenAI ④ 4→3.
- **다음 실행 과제(점수에 닿지 않음)**: oracle.F7·openai.F5 에 남은 'Oracle 의 Stargate $7B 지분' 서술, Apple·NVIDIA·Palantir·TSMC ⑨ 문장의 추세 근거를 실측 FCF 로, NVIDIA ③ 인용 10-Q 의 출처 등록과 판단 단위 출처 연결, 방법 절 ⑨ '조달 여력은 신용등급으로'(사용자 원본 문장), 발동 트리거 2건 표시, TEN-RA3-01 닫기, NVIDIA 지분 투자처(CoreWeave·Nebius·Reflection) 판정 등. 영역 파일의 「다음 실행 과제」에 전부 있다.

## 판정

- **status: pass.** 네 영역이 pass 이고, 체크리스트 fail 14건(Q01·02·03·05·08·09·10·12·13·16·19·20·21·23)은 모두 승계 판단 예외다. 인용한 긴장 15개는 근거 칸에 그대로 적었고 모두 `status: open`·`recheck_at: 2026-11` 이다.
- results_hash `e279d193d30137ee…` · draft_hash `1bbf20715c81cc01…` 기준 검토. 자료·규칙·판단·초안이 바뀌면 이 리뷰는 무효다(D-10).
- **두 해시의 뜻이 다르다.** `results_hash` 는 `results.json` 에서 `results_hash` 키를 뺀 내용의 정렬 JSON 해시이고(`engine.sha256_obj`) **파일 바이트 sha256 과 다르다.** `draft_hash` 는 초안 **파일 바이트 sha256** 이다. 대조할 때 섞지 않는다.
