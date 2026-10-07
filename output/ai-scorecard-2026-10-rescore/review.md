---
slug: ai-scorecard-2026-10-rescore
report_type: ai_scorecard
status: pass
created_at: 2026-10-06
plan_source: output/ai-scorecard-2026-10-rescore/plan.md
research_source: output/ai-scorecard-2026-10-rescore/research.md
draft_source: output/ai-scorecard-2026-10-rescore/draft.md
results_hash: 59518fa18f928802828905ce4844947b8a6c3d5a83d7b6062366532dab7e59ce
draft_hash: cb819da1aab10ac67a0286100b6387811d4a08a5f4aa14f6c4bfb57c27a90716
review_type: separate-session-4way
review_execution: separate_subagent_sessions
reviewers:
  - "fact-sources: Claude Opus 5.5 fact-checker 독립 세션 fc-opus55-20261007-rescore-r6 · round 7 pass"
  - "financial-calc: Claude Opus 5.5 general-purpose 독립 세션 rescore-1007-financial-calc-r7 · round 7 pass"
  - "rule-consistency: Claude Opus 5.5 general-purpose 독립 세션 rc-rescore-20261007-r7 · round 7 pass"
  - "output-readability: Claude Opus 5.5 report-designer 독립 세션 rd-opus55-20261007-rescore-r7 · round 7 pass"
---
# 리뷰 — 2026-10 정기 재채점

각 영역은 가능하면 독립 세션에서 검토하고 실제 수행자·결과를 남긴다. 수행하지 않은 검토를 pass 로 표시하지 않는다.

## 검토 영역

| 영역 | 검토 대상 | 검토자 | 결과 | 요약 |
| --- | --- | --- | --- | --- |
| 사실·출처 | 숫자·기업 귀속·기준 시점·공시·뉴스·부재 주장 | Claude Opus 5.5 fact-checker 독립 세션(`review-parts/fact-sources.md`) | pass | 판단 114개의 세 칸 합을 나누기 전 문장과 대조해 새 사실·빠진 사실이 없다. 1차에서 alphabet.F5 의 결론 문장과 좁혀진 반발 대상을 잡았고 수정으로 닫혔다. 렌더러가 `AA-LCR` 을 자르던 결함도 닫혔다 |
| 재무 계산 | EPS·환율·ADR·TTM·FCF·런웨이·약정·단위·부호 | Claude Opus 5.5 독립 세션(`review-parts/financial-calc.md`) | pass | 세 칸 문장의 숫자·영문 토큰이 원문과 같고 점수·순위·factor 점수가 그대로다. 1차에서 tsmc.F9 설비투자 가이던스 상향이 올릴 근거에 있던 것을 잡았고 내릴 근거로 옮겨 닫혔다 |
| 규칙 일관성 | factor 정의·상하한·예외·중복 속성·정성 승계·전 기업 동일 기준 | Claude Opus 5.5 독립 세션(`review-parts/rule-consistency.md`) | pass | 판단 114개의 분류와 방향을 전부 봤다. 1차 needs_fix 둘(tsmc.F9, 신용 지표 줄은 판정 칸 — 규칙 2.8)이 닫혔다. 판정 재료는 그대로이고 체크리스트는 round 5 판정을 이어받았다 |
| 출력·가독성 | 표·카드·근거·차트·이력 일치, 낡은 비교 문장, 모바일·단일 HTML | Claude Opus 5.5 report-designer 독립 세션(`review-parts/output-readability.md`) | pass | 카드의 올릴·내릴 근거 상자, 초안 소제목, 트리거 표 두 덩어리, 탭 여섯 개를 메모리 렌더로 확인했다. 320·768·1280px 가로 넘침 0, 24px 미만 탭 대상 0, 탭 사이 앵커 이동이 동작한다. 1차의 320px 탭 표시·초안 ⑥ 머리줄·'앞서 매긴' 이 닫혔다 |

결과는 pass / needs_fix / blocked 중 하나. 네 영역이 모두 pass 이고 체크리스트에 fail 이 없을 때만 frontmatter `status: pass`.
**승계 판단 예외(AGENTS.md 리뷰 범위)** — 체크리스트 fail 의 사유가 `carried_score` 로 승계한 판단의 기존 논리이고, 이번 실행이 그 판단에 쓰인 잣대를 바꾸지 않았으며, 규칙 파일 `open_tensions` 에 재검토 시점과 함께 등록됐다면 `status: pass` 를 막지 않는다. 이때 해당 fail 과 **긴장 번호**(예: `TEN-RC-02`)를 근거 칸에 그대로 적는다. 이번 실행이 바꾼 잣대가 닿는 승계 판단은 이 예외가 아니다 — 한 회사에 새 잣대를 댔으면 같은 잣대가 닿는 모든 회사에 대야 한다(Q03).

## 체크리스트

| ID | 검사 초점 | 결과 | 근거 |
| --- | --- | --- | --- |
| Q01 | 이 감점, 다른 칸에서 이미 셌나? | fail | **승계 판단 예외 — TEN-RC-05 · TEN-RC3-04** |
| Q02 | 이 지표가 이 칸의 정의에 맞나? | fail | **승계 판단 예외 — TEN-RC-02 · TEN-RC3-01 · TEN-RC3-03 · TEN-RC3-05 · TEN-RC4-02**<br>• 세 칸: N2 의 신용 지표 줄 셋이 판정 칸으로 옮겨져 규칙 2.8 과 맞다(닫힘).<br>• 세 칸: spacex-xai.F4 올릴 근거의 상장 조달액·현금은 ④ 지표가 아니다(다음 실행 과제) |
| Q03 | 회사마다 같은 잣대인가? | fail | **승계 판단 예외 — TEN-RC-03(nvidia.F5 포함) · TEN-RC4-03.** 예외 없는 fail 은 없다. 이번 실행이 새로 댄 잣대 셋이 닿는 회사는 모두 다시 판정됐다.<br>• ④ 출하만: tesla·openai.<br>• FCF 추세: microsoft 를 다시 판정했다. apple·nvidia·palantir·tsmc 는 실측으로 재도 안정이다.<br>• ⑥ 트랙: tsmc·alibaba.<br>• oracle.F5 는 기존 +2 조건을 확인된 사실에 대 +1 이다.<br>• 세 칸: 설비투자 계획(tsmc ↔ microsoft)과 신용 지표(oracle·openai ↔ amazon)는 같은 칸으로 맞춰졌다(N1·N2 닫힘). 점수에 닿지 않는 갈림(⑤ 공짜 사용자·조달 제외 줄, ⑦ 비고객 평가이익)은 다음 실행 과제다 |
| Q04 | 시총 크기를 밸류에이션으로 착각했나? | pass | ⑥ 은 비율 잣대이고 변경이 없다 |
| Q05 | 출처가 이해당사자인가? | fail | **승계 판단 예외 — TEN-RA-02(nvidia F2).** openai.F4 는 이해당사자 발표를 점수 근거에서 뺐다. 이해상충 표기는 판정에 넣지 않았다 |
| Q06 | 볼륨인가 가치인가? | pass | 볼륨 지표가 점수 재료로 든 곳이 없다 |
| Q07 | "안 만든 것"을 카운터 포지셔닝으로 셌나? | pass | amazon.F3 문장 그대로다. 세 칸에서도 "모델을 직접 만들지 않은 것 자체는 카운터 포지셔닝이 아니다" 가 판정 칸에 있다 |
| Q08 | 적대세력을 수로 셌나, 성격으로 셌나? | fail | **승계 판단 예외 — TEN-RC4-03.** alphabet.F5 의 직원 반발은 수로 세지 않고 성격(내부 갈등)으로 판정 칸에서 거른다 |
| Q09 | 미래 계획을 현재 점수에 넣었나? | fail | **승계 판단 예외 — TEN-RA-02 · TEN-RA6-01.**<br>• openai.F4·tesla.F4·microsoft.F9 는 계획을 점수 근거에서 뺐다.<br>• spacex-xai.F4 의 Terafab 과 tsmc.F4 의 로드맵·투자액 서술은 점수를 정하지 않아 low 로 적었다.<br>• 세 칸: tsmc.F9 가이던스 상향은 내릴 근거로 옮겨지고 단서가 붙었다(N1 닫힘). 단서가 다른 줄에 있거나 없는 계획 줄(tesla.F2, meta.F9, tsmc.F2·F3, spacex-xai.F3)은 점수를 정하지 않아 다음 실행 과제다 |
| Q10 | 거리를 가속도로 착각했나? | fail | **승계 판단 예외 — TEN-RB-Q10 · TEN-RC4-04.** 세 칸: alphabet.F3 의 "2년 만에 격차 회수" 와 anthropic.F3 의 "$9B → $65B" 는 거리라서 가속도 근거에서 뺀다는 문장으로 남았다 |
| Q11 | 순적자를 실격 사유로 썼나? | pass | ⑨ 게이트 경로로 계산하고, 순적자 실격은 없다 |
| Q12 | ③ 세 기준을 동등하게 쟀나? | fail | **승계 판단 예외 — TEN-RC4-01 · TEN-RC3-05.** nvidia.F3 은 규칙 정의(직전 분기 대비)로 잰다. 세 칸에서 직전 분기 대비 감속은 내릴 근거, 전년 대비 가속은 올릴 근거로 갈렸고, 판정 칸이 고른 지표를 적는다 |
| Q13 | "공짜로 뿌린다"를 곧바로 카운터 포지셔닝으로 셌나? | fail | **승계 판단 예외 — TEN-RC3-05** |
| Q14 | 아직 안 끝난 승부를 끝난 것처럼 쟀나? | pass | 14사 door_closed 가 전부 fail 이다 |
| Q15 | ⑤에서 "공짜 사용자"를 아군으로 셌나? | pass | 공짜 사용자를 동맹으로 세지 않는다. 세 칸: 제외 문장의 칸이 alibaba.F5(내릴 근거)와 meta.F5·nvidia.F5(판정)로 갈린다(다음 실행 과제) |
| Q16 | ①을 한 채널로만 쟀나? | fail | **승계 판단 예외 — TEN-RC-02 · TEN-RC4-02** |
| Q17 | ②를 "표준 없음"만으로 깎았나? | pass | 변경 없음 |
| Q18 | ⑤에서 관계사를 독립 동맹으로 셌나? | pass | 관계사 처리가 같다. tesla.F4 는 관계사 합작 Terafab 을 배치 전이라 뺐다 |
| Q19 | ⑤에서 "받은 투자"를 곧바로 동맹 +2로 셌나? | fail | **승계 판단 예외 — TEN-RC-03(nvidia.F5).** 받은 투자를 A 에서 빼는 처리는 일관된다. 준 지분 투자를 동맹으로 셀지는 이탈 조건 통일(C-08)과 함께 2026-11 에 재검토한다 |
| Q20 | 조달을 동맹으로 셌나? | fail | **승계 판단 예외 — TEN-RC-03(C-08)** |
| Q21 | 동맹이자 의존인 관계를 한쪽에서만 셌나, 또는 같은 속성을 양쪽에서 셌나? | fail | **승계 판단 예외 — TEN-RC-05 · TEN-RC3-04** |
| Q22 | 지분 평가이익을 ⑦ 순환금융 증거로 셌나? | pass | ⑦ 입력에 평가이익이 없다. 세 칸: amazon·nvidia F7 은 고객사 출처 평가이익을 "입력에 넣지 않는다" 단서와 함께 내릴 근거에 방증으로 두어 규칙 ⑦ 문언대로다. alphabet.F7 의 비고객(SpaceX) 평가이익 줄은 올릴 근거에 있어 판정 칸으로 옮기는 것이 맞다(다음 실행 과제) |
| Q23 | 벤치마크를 서로 다른 하네스끼리 비교했나? | fail | **승계 판단 예외 — TEN-RA4-01** |

결과는 pass / fail / not_applicable. not_applicable 도 근거가 필요하다.

## 발견 사항

리뷰는 1차(round 6) → 수정 한 묶음 → 확인 리뷰(round 7) 순서로 끝났다. 영역별 발견 전체는 `review-parts/` 네 파일에 있다.

- **이번 실행에서 바뀐 것**: 판단 114개의 근거를 판정·올릴 근거·내릴 근거 세 칸으로 나눴다(2026-10-07 사용자 지시, `docs/scorecard/guide.md` 5.6). 사실·숫자는 그대로이고 점수·순위·판정 재료도 그대로다. 리포트에 근거 세 칸, 트리거 표 두 덩어리, 상단 탭 여섯 개를 넣었다.
- **1차 needs_fix(모두 닫힘)**: tsmc.F9 설비투자 가이던스 상향이 올릴 근거에 있었다 → 내릴 근거로 옮기고 계획 단서. oracle.F8·openai.F7·oracle.F9 의 신용 지표 줄 → 판정 칸(규칙 2.8). alphabet.F5 결론 문장이 내릴 근거에 있었고 반발 대상이 좁혀졌다 → 사실과 결론으로 나누고 대상 셋 복원. 렌더러: `AA-LCR` 절단, 320px 탭 표시, 초안 ⑥ 머리줄, 고정 문장 '앞서 매긴'.
- **다음 실행 과제(점수에 닿지 않음)**: 회사마다 같은 유형의 사실이 다른 칸에 간 줄 맞추기(⑨ 현금 잔고, 런웨이 민감도, ⑦ 영업외 이익, '흑자 전환 후퇴·완충 잠식 없음'), 칸을 건너간 지시어 7곳, palantir.F5 인과 수식어, anthropic.F5 조달 논리 한 줄, 320px 순위표 조정총점 열, oracle.F7·openai.F5 의 Stargate $7B 서술 등. 영역 파일의 「다음 실행 과제」 에 전부 있다.

## 판정

- **status: pass.** 네 영역이 pass 이고, 체크리스트 fail 14건(Q01·02·03·05·08·09·10·12·13·16·19·20·21·23)은 모두 승계 판단 예외다. 인용한 긴장 15개는 근거 칸에 그대로 적었고 모두 `status: open`·`recheck_at: 2026-11` 이다.
- results_hash `59518fa18f928802…` · draft_hash `cb819da1aab10ac6…` 기준 검토. 자료·규칙·판단·초안이 바뀌면 이 리뷰는 무효다(D-10).
- **두 해시의 뜻이 다르다.** `results_hash` 는 `results.json` 에서 `results_hash` 키를 뺀 내용의 정렬 JSON 해시이고(`engine.sha256_obj`) **파일 바이트 sha256 과 다르다.** `draft_hash` 는 초안 **파일 바이트 sha256** 이다. 대조할 때 섞지 않는다.
