---
slug: ai-scorecard-2026-10-rescore
report_type: ai_scorecard
status: pass
created_at: 2026-10-06
plan_source: output/ai-scorecard-2026-10-rescore/plan.md
research_source: output/ai-scorecard-2026-10-rescore/research.md
draft_source: output/ai-scorecard-2026-10-rescore/draft.md
results_hash: 462585f940bfc201daf798e03879dd97f3e4dbf6c1d7e4f7a35b23d69cee861c
draft_hash: ece5fa5f37d75c5c87f558a403bd660a073c22e64d3bf687fe980b783c605af3
review_type: separate-session-4way
review_execution: separate_subagent_sessions
reviewers:
  - "fact-sources: Claude Opus 5.5 fact-checker 독립 세션 · round 8 세 묶음(a·b·c) + round 9 확인 pass"
  - "financial-calc: Claude Opus 5.5 general-purpose 독립 세션 · round 9 pass"
  - "rule-consistency: Claude Opus 5.5 general-purpose 독립 세션 · round 9 pass"
  - "output-readability: Claude Opus 5.5 report-designer 독립 세션 · round 9 pass"
---
# 리뷰 — 2026-10 정기 재채점

각 영역은 가능하면 독립 세션에서 검토하고 실제 수행자·결과를 남긴다. 수행하지 않은 검토를 pass 로 표시하지 않는다.

## 검토 영역

| 영역 | 검토 대상 | 검토자 | 결과 | 요약 |
| --- | --- | --- | --- | --- |
| 사실·출처 | 숫자·기업 귀속·기준 시점·공시·뉴스·부재 주장 | Claude Opus 5.5 fact-checker 독립 세션 넷(round 8 세 묶음 `review-parts/fact-sources-a·b·c.md`, round 9 확인 `fact-sources.md`) | pass | 올릴·내릴 근거 376줄의 표지가 가리키는 근거 566건을 전부 원문과 대조했다(원문에서 발췌를 못 찾은 근거 0). 1차 needs_fix 4건(amazon.F2 수치 주체, spacex-xai.F2 오표지, nvidia.F7 약정·담보 전제)과 확인 리뷰의 oracle.F2 '자체 모델 대신' 1건이 닫혔다 |
| 재무 계산 | EPS·환율·ADR·TTM·FCF·런웨이·약정·단위·부호 | Claude Opus 5.5 독립 세션(`review-parts/financial-calc.md`) | pass | 엔진 메모리 재계산이 results 와 같다. oracle.offbalance_B.link26(10-Q 미개시 리스 $288B + 구매 약정 $34.15B)과 G4 커버리지 2.06배, TRG-005 의 8.4·8.0·6.7년을 실제 계산 코드로 대조했다. 1차 needs_fix 5건이 닫혔다 |
| 규칙 일관성 | factor 정의·상하한·예외·중복 속성·정성 승계·전 기업 동일 기준 | Claude Opus 5.5 독립 세션(`review-parts/rule-consistency.md`) | pass | 판정 정정 다섯 건이 규칙과 맞다. ⑦ 가로축 잣대(연간 약정 ÷ 최근 1년 매출)를 14개사 모두에 대 같은 결론을 확인했다(작음 0.6~9.0%, 큼 65~92%). 1차 needs_fix 5건(N1 spacex-xai ⑦, N2 palantir ⑧, N3 amazon ②, N4 amazon ⑦, N5 oracle ②)이 닫혔다 |
| 출력·가독성 | 표·카드·근거·차트·이력 일치, 낡은 비교 문장, 모바일·단일 HTML | Claude Opus 5.5 report-designer 독립 세션(`review-parts/output-readability.md`) | pass | 카드 근거 표지(근거 ID 760개)가 320·768·1280px 에서 잘림·겹침 0 이다. SpaceX 9위·Apple 8위가 순위표·카드·요약에서 results 와 같고 금지어 0건이다. 해시를 달고 처음 열 때 탭이 걸리지 않던 결함도 고쳤다 |

결과는 pass / needs_fix / blocked 중 하나. 네 영역이 모두 pass 이고 체크리스트에 fail 이 없을 때만 frontmatter `status: pass`.
**승계 판단 예외(AGENTS.md 리뷰 범위)** — 체크리스트 fail 의 사유가 `carried_score` 로 승계한 판단의 기존 논리이고, 이번 실행이 그 판단에 쓰인 잣대를 바꾸지 않았으며, 규칙 파일 `open_tensions` 에 재검토 시점과 함께 등록됐다면 `status: pass` 를 막지 않는다. 이때 해당 fail 과 **긴장 번호**(예: `TEN-RC-02`)를 근거 칸에 그대로 적는다. 이번 실행이 바꾼 잣대가 닿는 승계 판단은 이 예외가 아니다 — 한 회사에 새 잣대를 댔으면 같은 잣대가 닿는 모든 회사에 대야 한다(Q03).

## 체크리스트

| ID | 검사 초점 | 결과 | 근거 |
| --- | --- | --- | --- |
| Q01 | 이 감점, 다른 칸에서 이미 셌나? | pass | palantir.F8 이 ICE 논란을 ⑤ 에만 둔다(N2 닫힘). nvidia·tesla 도 속성을 갈랐다. spacex-xai 고객 집중의 ⑦·⑧ 은 다른 속성이다 |
| Q02 | 이 지표가 이 칸의 정의에 맞나? | fail | **승계 판단 예외 — TEN-RC-02 · TEN-RC3-01 · TEN-RC3-03 · TEN-RC3-05 · TEN-RC4-02.** spacex-xai.F4 올릴 근거의 상장 조달액·현금과 nvidia.F8 의 중국 우회 조사는 그 칸의 지표가 아니지만 점수를 정하지 않는다(다음 실행 과제) |
| Q03 | 회사마다 같은 잣대인가? | fail | **승계 판단 예외 — TEN-RC-03(nvidia.F5 포함) · TEN-RC4-03.** 예외 없는 fail 은 없다. ⑦ 가로축 잣대는 14개사 모두 같은 결론이다(N1 닫힘, 위 표). ⑤·⑧ 속성 분리는 nvidia·tesla·palantir 에 같게 댔다(N2 닫힘). 'Anthropic 매출 미미' 는 alphabet·amazon 모두 판정 칸 미확인이다(N4 닫힘) |
| Q04 | 시총 크기를 밸류에이션으로 착각했나? | pass | ⑥ 은 비율 잣대이고 변경이 없다 |
| Q05 | 출처가 이해당사자인가? | fail | **승계 판단 예외 — TEN-RA-02(nvidia F2).** 이해상충 표기는 판정에 넣지 않았다 |
| Q06 | 볼륨인가 가치인가? | pass | 볼륨 지표가 점수 재료로 든 곳이 없다 |
| Q07 | "안 만든 것"을 카운터 포지셔닝으로 셌나? | pass | amazon.F3 판정 넷째 줄 그대로다. oracle.F2 의 '고객이 고른 LLM' 은 ③ 이 아니라 ② 성능 도약 실패의 근거로 쓰였다 |
| Q08 | 적대세력을 수로 셌나, 성격으로 셌나? | fail | **승계 판단 예외 — TEN-RC4-03.** alphabet.F5 직원 반발은 성격(내부 갈등)으로 판정 칸에서 거른다 |
| Q09 | 미래 계획을 현재 점수에 넣었나? | fail | **승계 판단 예외 — TEN-RA-02 · TEN-RA6-01.** amazon.F2 는 실측 근거(Anthropic 의 Trainium2 학습)를 판정 칸에 적어 예외 없는 fail 이 닫혔다(N3). '다년 채택' 을 실측이라 부른 문구와 단서 없는 계획 줄(tesla.F2, meta.F9, tsmc.F2·F3, spacex-xai.F3)은 점수를 정하지 않아 다음 실행 과제다. spacex-xai.F7 의 Anthropic 계약은 구속력 있는 약정을 감점에 쓴 것이라 규칙 2.1 과 맞다 |
| Q10 | 거리를 가속도로 착각했나? | fail | **승계 판단 예외 — TEN-RB-Q10 · TEN-RC4-04** |
| Q11 | 순적자를 실격 사유로 썼나? | pass | ⑨ 게이트 경로로 계산하고, 순적자 실격은 없다 |
| Q12 | ③ 세 기준을 동등하게 쟀나? | fail | **승계 판단 예외 — TEN-RC4-01 · TEN-RC3-05** |
| Q13 | "공짜로 뿌린다"를 곧바로 카운터 포지셔닝으로 셌나? | fail | **승계 판단 예외 — TEN-RC3-05** |
| Q14 | 아직 안 끝난 승부를 끝난 것처럼 쟀나? | pass | 14사 door_closed 가 전부 fail 이다(스크립트) |
| Q15 | ⑤에서 "공짜 사용자"를 아군으로 셌나? | pass | 공짜 사용자를 동맹으로 세지 않는다 |
| Q16 | ①을 한 채널로만 쟀나? | fail | **승계 판단 예외 — TEN-RC-02 · TEN-RC4-02** |
| Q17 | ②를 "표준 없음"만으로 깎았나? | pass | oracle.F2 가 세 경로를 따로 판정하고, 성능 도약 실패를 10-K 문장(EV-oracle-035)으로 받친다(N5 닫힘) |
| Q18 | ⑤에서 관계사를 독립 동맹으로 셌나? | pass | 관계사 처리가 같다(tesla.F5 판정 둘째 줄, spacex-xai.F5 판정 셋째 줄). tesla.F7 의 SpaceX Megapack 구매도 관계사 거래라는 사실만으로 환류를 인정하지 않는다 |
| Q19 | ⑤에서 "받은 투자"를 곧바로 동맹 +2로 셌나? | fail | **승계 판단 예외 — TEN-RC-03(nvidia.F5).** 받은 투자를 A 에서 빼는 처리는 일관된다 |
| Q20 | 조달을 동맹으로 셌나? | fail | **승계 판단 예외 — TEN-RC-03(C-08)** |
| Q21 | 동맹이자 의존인 관계를 한쪽에서만 셌나, 또는 같은 속성을 양쪽에서 셌나? | pass | palantir.F8 의 같은 속성 이중 계산이 닫혔다(N2). 동맹이자 의존인 관계는 ⑤·⑧ 에 한 번씩 센다 |
| Q22 | 지분 평가이익을 ⑦ 순환금융 증거로 셌나? | pass | ⑦ 입력에 평가이익이 없다. spacex-xai.F7 재판정은 연간 약정과 고객 집중으로 했다. alphabet.F7 의 SpaceX 평가이익 줄은 넘어온 과제다 |
| Q23 | 벤치마크를 서로 다른 하네스끼리 비교했나? | fail | **승계 판단 예외 — TEN-RA4-01** |

결과는 pass / fail / not_applicable. not_applicable 도 근거가 필요하다.

## 발견 사항

리뷰는 1차(round 8, 사실·출처 세 묶음 + 세 영역) → 수정 한 묶음 → 확인 리뷰(round 9) 순서로 끝났다. 확인 리뷰에서 나온 사실·출처 1건은 고친 뒤 같은 리뷰어가 다시 확인했다. 영역별 발견 전체는 `review-parts/` 에 있다.

- **이번 실행에서 바뀐 것**: 올릴·내릴 근거의 모든 줄 끝에 원문 근거 표지를 달았다(2026-10-07 사용자 지시, `docs/scorecard/guide.md` 5.7). 근거는 72건에서 603건이 됐고, 판단이 인용하는 근거는 모두 출처 URL·본문 발췌·인용 위치를 갖는다. 원문을 찾지 못한 사실은 판정 칸에 미확인으로 옮겼고, 원문 값이 다른 줄은 원문대로 고쳤다.
- **판정 정정**: anthropic·meta ② 문장, TEN-RC-05·TEN-RC3-04 속성 분리(nvidia·tesla ⑧ 에서 ⑤ 속성 제거, palantir ⑧ 도 같은 원칙), oracle ⑦ 세로축 근거, ⑦ 가로축 잣대 통일.
- **점수 변화**: spacex-xai ⑦ 0 → −2(조달 의존 고객 비중 큼: Anthropic 계약 연 약 $15B ÷ 최근 1년 매출 $23.0B ≈ 65%). 총점 9 → 7, 순위 6위 → 9위. apple 은 9위 → 8위. 나머지 12개사 총점·순위·factor 점수는 그대로다.
- **다음 실행 과제(점수에 닿지 않음)**: 영역 파일의 「다음 실행 과제」 에 전부 있다. 큰 것은 원문을 끝내 찾지 못한 점수 근거 두 줄(openai ① OpenRouter 단가·점유율, anthropic ⑥ 누적 조달), anthropic ⑥ 매출 역산을 실적으로 다시 할지, ⑦ 큼·작음 경계를 규칙 긴장으로 올릴지, 리포트 크기(약 1.1MB)와 320px 인용 근거 표다.

## 판정

- **status: pass.** 네 영역이 pass 이고, 체크리스트 fail 12건(Q02·Q03·Q05·Q08·Q09·Q10·Q12·Q13·Q16·Q19·Q20·Q23)은 모두 승계 판단 예외다. 인용한 긴장은 규칙 v1.9 에서 모두 `status: open`·`recheck_at: 2026-11` 이다.
- results_hash `462585f940bfc201…` · draft_hash `ece5fa5f37d75c5c…` 기준 검토. 자료·규칙·판단·초안이 바뀌면 이 리뷰는 무효다(D-10).
- **두 해시의 뜻이 다르다.** `results_hash` 는 `results.json` 에서 `results_hash` 키를 뺀 내용의 정렬 JSON 해시이고(`engine.sha256_obj`) **파일 바이트 sha256 과 다르다.** `draft_hash` 는 초안 **파일 바이트 sha256** 이다. 대조할 때 섞지 않는다.
