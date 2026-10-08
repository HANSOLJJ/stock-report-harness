---
slug: ai-scorecard-2026-10-rejudge
report_type: ai_scorecard
status: needs_fix
created_at: 2026-10-08
plan_source: output/ai-scorecard-2026-10-rejudge/plan.md
research_source: output/ai-scorecard-2026-10-rejudge/research.md
draft_source: output/ai-scorecard-2026-10-rejudge/draft.md
results_hash: ca52264b918d32d524e00ed10cf7adb2a0d8e874045df2ff196ee053e38f2a5b
draft_hash: 5c0003f9c5615e0cb8989115a7d8c43aec9d3a04cff71380e1b5a15f9dcfd646
review_type: separate-session-4way
review_execution: separate_subagent_sessions
reviewers:
  - "fact-sources: pending"
  - "financial-calc: pending"
  - "rule-consistency: pending"
  - "output-readability: pending"
---
# 리뷰 — 2026-10 전부 재판단(v2.0)

각 영역은 가능하면 독립 세션에서 검토하고 실제 수행자·결과를 남긴다. 수행하지 않은 검토를 pass 로 표시하지 않는다.

## 검토 영역

| 영역 | 검토 대상 | 검토자 | 결과 | 요약 |
| --- | --- | --- | --- | --- |
| 사실·출처 | 숫자·기업 귀속·기준 시점·공시·뉴스·부재 주장 |  | pending |  |
| 재무 계산 | EPS·환율·ADR·TTM·FCF·런웨이·약정·단위·부호 |  | pending |  |
| 규칙 일관성 | factor 정의·상하한·예외·중복 속성·정성 승계·전 기업 동일 기준 |  | pending |  |
| 출력·가독성 | 표·카드·근거·차트·이력 일치, 낡은 비교 문장, 모바일·단일 HTML |  | pending |  |

결과는 pass / needs_fix / blocked 중 하나. 네 영역이 모두 pass 이고 체크리스트에 fail 이 없을 때만 frontmatter `status: pass`.
**승계 판단 예외(AGENTS.md 리뷰 범위 · 기업 추가 실행에만, rules.md 2.9)** — 정기 실행에서는 체크리스트 fail 이 하나라도 있으면 `status: pass` 가 아니다. 기업 추가 실행에서는 체크리스트 fail 의 사유가 `carried_score` 로 승계한 판단의 기존 논리이고, 이번 실행이 그 판단에 쓰인 잣대를 바꾸지 않았으며, 규칙 파일 `open_tensions` 에 재검토 시점과 함께 등록됐다면 `status: pass` 를 막지 않는다. 이때 해당 fail 과 **긴장 번호**(예: `TEN-RC-02`)를 근거 칸에 그대로 적는다. 이번 실행이 바꾼 잣대가 닿는 승계 판단은 이 예외가 아니다 — 한 회사에 새 잣대를 댔으면 같은 잣대가 닿는 모든 회사에 대야 한다(Q03).

## 체크리스트

| ID | 검사 초점 | 결과 | 근거 |
| --- | --- | --- | --- |
| Q01 | 이 감점, 다른 칸에서 이미 셌나? | pending |  |
| Q02 | 이 지표가 이 칸의 정의에 맞나? | pending |  |
| Q03 | 회사마다 같은 잣대인가? | pending |  |
| Q04 | 시총 크기를 밸류에이션으로 착각했나? | pending |  |
| Q05 | 출처가 이해당사자인가? | pending |  |
| Q06 | 볼륨인가 가치인가? | pending |  |
| Q07 | "안 만든 것"을 카운터 포지셔닝으로 셌나? | pending |  |
| Q08 | 적대세력을 수로 셌나, 성격으로 셌나? | pending |  |
| Q09 | 미래 계획을 현재 점수에 넣었나? | pending |  |
| Q10 | 거리를 가속도로 착각했나? | pending |  |
| Q11 | 순적자를 실격 사유로 썼나? | pending |  |
| Q12 | ③ 세 기준을 동등하게 쟀나? | pending |  |
| Q13 | "공짜로 뿌린다"를 곧바로 카운터 포지셔닝으로 셌나? | pending |  |
| Q14 | 아직 안 끝난 승부를 끝난 것처럼 쟀나? | pending |  |
| Q15 | ⑤에서 "공짜 사용자"를 아군으로 셌나? | pending |  |
| Q16 | ①을 한 채널로만 쟀나? | pending |  |
| Q17 | ②를 "표준 없음"만으로 깎았나? | pending |  |
| Q18 | ⑤에서 관계사를 독립 동맹으로 셌나? | pending |  |
| Q19 | ⑤에서 "받은 투자"를 곧바로 동맹 +2로 셌나? | pending |  |
| Q20 | 조달을 동맹으로 셌나? | pending |  |
| Q21 | 동맹이자 의존인 관계를 한쪽에서만 셌나, 또는 같은 속성을 양쪽에서 셌나? | pending |  |
| Q22 | 지분 평가이익을 ⑦ 순환금융 증거로 셌나? | pending |  |
| Q23 | 벤치마크를 서로 다른 하네스끼리 비교했나? | pending |  |

결과는 pass / fail / not_applicable. not_applicable 도 근거가 필요하다.

## 발견 사항

- (파일·섹션 단위로 기록)

## 판정

- results_hash `ca52264b918d32d5…` · draft_hash `5c0003f9c5615e0c…` 기준 검토. 자료·규칙·판단·초안이 바뀌면 이 리뷰는 무효다(D-10).
- **두 해시의 뜻이 다르다.** `results_hash` 는 `results.json` 에서 `results_hash` 키를 뺀 내용의 정렬 JSON 해시이고(`engine.sha256_obj`) **파일 바이트 sha256 과 다르다.** `draft_hash` 는 초안 **파일 바이트 sha256** 이다. 대조할 때 섞지 않는다.
