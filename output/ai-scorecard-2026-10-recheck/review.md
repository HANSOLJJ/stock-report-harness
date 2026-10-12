---
slug: ai-scorecard-2026-10-recheck
report_type: ai_scorecard
status: pass
created_at: 2026-10-12
plan_source: output/ai-scorecard-2026-10-recheck/plan.md
research_source: output/ai-scorecard-2026-10-recheck/research.md
draft_source: output/ai-scorecard-2026-10-recheck/draft.md
results_hash: 0b3fe1402a8a0c2872a268c62b312e6e8d63f16c0f072d20414231786fb55576
draft_hash: b035c8d023f0bfc8b13eb1d35180e19c9ed497493e5bae52fb4aad724bbeaffd
review_type: separate-session-4way
review_execution: separate_subagent_sessions
reviewers:
  - "fact-sources: fact-checker fs-a-recheck-20261012-r1 → needs_fix → 수정 → pass · fs-b-recheck-20261012-r1 → pass"
  - "financial-calc: general-purpose fc-recheck-20261012-r1 → needs_fix → 수정 → pass"
  - "rule-consistency: general-purpose rc-recheck-20261012-rule → needs_fix → 수정 → pass"
  - "output-readability: report-designer or-recheck-20261012-r1 → pass(빌드 전 문장 9곳 수정)"
  - "confirm: general-purpose confirm-r2 → blocked 1건(Microsoft ⑧ 고객 축) → 수정"
  - "confirm: general-purpose confirm-r3 → pass"
  - "confirm: general-purpose confirm-r4 → pass(⑧ 약정 축 3배 경계 반영 확인)"
---
# 리뷰 — AI 기업 9-factor 채점표 2026-10 정기 재실행

각 영역은 가능하면 독립 세션에서 검토하고 실제 수행자·결과를 남긴다. 수행하지 않은 검토를 pass 로 표시하지 않는다.

## 검토 영역

| 영역 | 검토 대상 | 검토자 | 결과 | 요약 |
| --- | --- | --- | --- | --- |
| 사실·출처 | 숫자·기업 귀속·기준 시점·공시·뉴스·부재 주장 | fact-checker ×2 (fs-a·fs-b-recheck-20261012-r1) + 확인 general-purpose (confirm-r2·r3·r4) | pass | 14사 판단 98건의 올릴·내릴 근거 921줄과 그 줄이 가리키는 근거 640건을 전수로 원문과 대조해 발췌를 모두 찾았다. 이어받은 제목뿐 근거 30건은 원문 발췌로 바뀌었고, 판정 칸의 '제목만' 사유는 0건이다. 1차 needs_fix(Alphabet ⑧ 약정 범위, Microsoft ⑦·⑧ 의 OpenAI 약정)는 회사 1차 발표와 공시를 근거로 등록해 고쳤고(EV-microsoft-045~048, EV-alphabet-075), Palantir ⑤ 의 프랑스·독일 문장은 원문 본문대로 고쳤다. |
| 재무 계산 | EPS·환율·ADR·TTM·FCF·런웨이·약정·단위·부호 | general-purpose (fc-recheck-20261012-r1) + 확인 general-purpose (confirm-r2·r3·r4) | pass | ⑥ 상장 12사·비상장 P/S·⑨ 게이트·③ 성장률·⑧ 약정 배수를 원값으로 다시 계산해 맞았고, 엔진 재계산이 results_hash 를 그대로 낸다. Alibaba ⑥ −5 는 2026-10-09 종가로 PER 이 25배를 넘은 결과다. needs_fix 1건(⑧ 약정 분자 정의가 회사마다 다름)은 공유 정의대로 OpenAI −3(구속력 확인 몫 7.8~13.8배)·Alphabet 총액 2.02배로 맞췄고, 사용자가 정한 3배 경계에서 Alphabet ⑧ 은 −2 다(확인 4차 재계산 일치). |
| 규칙 일관성 | factor 정의·상하한·예외·중복 속성·정성 승계·전 기업 동일 기준 | general-purpose (rc-recheck-20261012-rule) + 확인 general-purpose (confirm-r2·r3·r4, 사건 교차표·미확인 방향표·근거 등급표) | pass | 98칸 판정 입력이 규칙 판정표와 맞고 모두 새 판단이다. 회사를 가로지르는 표 셋과 경쟁사 쌍 비교를 만들었다. 1차 Q03 fail(Microsoft ⑦ 이 회사 1차 발표인 OpenAI Azure $250B 를 빼고 작음)과 확인 2차 C1(Microsoft ⑧ 고객 축을 다른 판단에 없는 방식으로 폄)을 공유 문장대로 고쳐 Q02·Q03 이 pass 로 돌아왔다. ⑦·⑧ 의 OpenAI 계약 사용은 규칙 ⑦ 의 '서로 독립' 대로 다른 속성이다. |
| 출력·가독성 | 표·카드·근거·차트·이력 일치, 낡은 비교 문장, 모바일·단일 HTML | report-designer (or-recheck-20261012-r1) + 확인 general-purpose (confirm-r2·r3·r4) | pass | 초안 순위표·카드·요약 상자·요약 속 숫자를 results 와 스크립트로 대조해 어긋남 0 이고, 값을 바꾼 사본으로 검사가 값을 읽는지 확인했다. 트리거·판단·요약의 낡은 기준일·옛 점수·'제목 기준' 표현 10곳을 고쳤다. HTML 은 승인 뒤 빌드에서 확인한다. |

결과는 pass / needs_fix / blocked 중 하나. 네 영역이 모두 pass 이고 체크리스트에 fail 이 없을 때만 frontmatter `status: pass`.
**승계 판단 예외(AGENTS.md 리뷰 범위 · 기업 추가 실행에만, rules.md 2.9)** — 정기 실행에서는 체크리스트 fail 이 하나라도 있으면 `status: pass` 가 아니다. 기업 추가 실행에서는 체크리스트 fail 의 사유가 `carried_score` 로 승계한 판단의 기존 논리이고, 이번 실행이 그 판단에 쓰인 잣대를 바꾸지 않았으며, 규칙 파일 `open_tensions` 에 재검토 시점과 함께 등록됐다면 `status: pass` 를 막지 않는다. 이때 해당 fail 과 **긴장 번호**(예: `TEN-RC-02`)를 근거 칸에 그대로 적는다. 이번 실행이 바꾼 잣대가 닿는 승계 판단은 이 예외가 아니다 — 한 회사에 새 잣대를 댔으면 같은 잣대가 닿는 모든 회사에 대야 한다(Q03).

## 체크리스트

| ID | 검사 초점 | 결과 | 근거 |
| --- | --- | --- | --- |
| Q01 | 이 감점, 다른 칸에서 이미 셌나? | pass | OpenAI 계약은 microsoft ⑦(대금 원천)·⑧(고객 집중)에서 규칙 ⑦ 의 '서로 독립' 대로 다른 속성을 센다(SpaceX + xAI 의 Anthropic 계약과 같은 처리). 1260H·대만 집중은 ⑧ 에서만, 고객 자체 칩·정당성 공격은 ⑤ 에서만 센다 |
| Q02 | 이 지표가 이 칸의 정의에 맞나? | pass | microsoft ⑧ 고객 축이 공유 J2 의 '한 고객의 연환산 계약액 ÷ 최근 1년 매출' 로 돌아왔다(C1 해소). ⑧ 약정 축 분자는 아홉 회사가 같은 정의이고 Microsoft 열린 구매 주문·NVIDIA 지분 투자 약정은 정의보다 넓으나 구간이 같다 |
| Q03 | 회사마다 같은 잣대인가? | pass | ⑧ 고객 축은 공시·회사 1차만 재고, 30% 이상이면 재배정 경로가 있어도 −3 이며, 기간 미공시는 감점 완화 쪽으로 풀지 않는다는 잣대가 Microsoft·SpaceX·Palantir·Amazon·Oracle·Alphabet 에 같다. microsoft ⑦ 과 ⑧ 이 같은 한 해 상한 줄을 따른다. amazon ⑧ 의 $38B 누락은 넣어도 점수가 같다(N2) |
| Q04 | 시총 크기를 밸류에이션으로 착각했나? | pass | 바뀐 판단에 시가총액 크기를 재료로 쓴 문장이 없다. 1차 판정 그대로 |
| Q05 | 출처가 이해당사자인가? | pass | 새 근거는 10-K 공시와 회사 1차(실적 콜)이고 줄마다 등급을 적었다. 이해상충 표기는 판정 사유로 보지 않았다 |
| Q06 | 볼륨인가 가치인가? | pass | 1차 판정 그대로. 토큰 점유율을 매출 점유율로 읽은 문장이 없다 |
| Q07 | "안 만든 것"을 카운터 포지셔닝으로 셌나? | pass | 1차 판정 그대로 |
| Q08 | 적대세력을 수로 셌나, 성격으로 셌나? | pass | 공유 다섯째 줄대로 성격으로 센다. palantir ⑤ 는 다발형 요건으로 성격을 갈랐다 |
| Q09 | 미래 계획을 현재 점수에 넣었나? | pass | Broadcom 칩 조달 협의(TRG-092)는 논의 단계라 점수 밖이고, OpenAI $1.4T 의 구속력 미확인 몫도 넣지 않았다 |
| Q10 | 거리를 가속도로 착각했나? | pass | 1차 판정 그대로 |
| Q11 | 순적자를 실격 사유로 썼나? | pass | 1차 판정 그대로 |
| Q12 | ③ 세 기준을 동등하게 쟀나? | pass | 1차 판정 그대로. 4점은 TSMC 하나이고 모방 불가능성 완전 통과다 |
| Q13 | "공짜로 뿌린다"를 곧바로 카운터 포지셔닝으로 셌나? | pass | 1차 판정 그대로 |
| Q14 | 아직 안 끝난 승부를 끝난 것처럼 쟀나? | pass | 1차 판정 그대로. ③ 5점 없음 |
| Q15 | ⑤에서 "공짜 사용자"를 아군으로 셌나? | pass | 1차 판정 그대로 |
| Q16 | ①을 한 채널로만 쟀나? | pass | 1차 판정 그대로 |
| Q17 | ②를 "표준 없음"만으로 깎았나? | pass | 1차 판정 그대로 |
| Q18 | ⑤에서 관계사를 독립 동맹으로 셌나? | pass | 1차 판정 그대로. Tesla↔SpaceX + xAI 를 양쪽에서 뺀다 |
| Q19 | ⑤에서 "받은 투자"를 곧바로 동맹 +2로 셌나? | pass | 1차 판정 그대로 |
| Q20 | 조달을 동맹으로 셌나? | pass | 1차 판정 그대로 |
| Q21 | 동맹이자 의존인 관계를 한쪽에서만 셌나, 또는 같은 속성을 양쪽에서 셌나? | pass | microsoft(OpenAI)는 ⑤ 동맹·⑦ 대금 원천·⑧ 고객 집중을 나눠 세고, ⑧ 판정 칸은 조달 여부를, ⑦ 판정 칸은 집중 크기를 쓰지 않는다 |
| Q22 | 지분 평가이익을 ⑦ 순환금융 증거로 셌나? | pass | 1차 판정 그대로 |
| Q23 | 벤치마크를 서로 다른 하네스끼리 비교했나? | pass | 1차 판정 그대로 |

결과는 pass / fail / not_applicable. not_applicable 도 근거가 필요하다.

## 발견 사항

- 1차 리뷰 다섯(`review-parts/rule-consistency.md`, `fact-sources-a.md`, `fact-sources-b.md`, `financial-calc.md`, `output-readability.md`)의 needs_fix 는
  Microsoft ⑦(OpenAI Azure $250B), ⑧ 약정 분자 정의(OpenAI·Alphabet), Microsoft ⑧ 고객 축이었다. 수정 한 묶음(`.agents/plans/oct-recheck-2026-10/work/make_fix1.py`)
  뒤 확인 리뷰 2차(`confirm-r2.md`)가 Microsoft ⑧ 고객 축의 연환산 방식을 C1 으로 막았고, 공유 지표대로 고친 뒤(`make_fix2.py`) 확인 리뷰 3차(`confirm-r3.md`)가 pass 했다.
- 점수에 닿지 않는 발견과 다음 실행 과제는 각 리뷰 파일의 「다음 실행 과제」 절에 있다.

## 리뷰 경위

- 2026-10-12 1차 4영역 리뷰 다섯 세션. 사실·출처 A·B 는 사용량 한도로 중간에 끊겼다가 같은 세션을 이어서 끝냈다.
- 수정 한 묶음: 근거 3건 추가, 판단 8건(Microsoft ⑦ −2, OpenAI ⑧ −3, Alphabet ⑧ −3, Microsoft ⑧ 고객 축, 문장 4건), 트리거 9건, 기업 요약 6건.
- 확인 리뷰 2차 blocked 1건(C1) → 근거 2건 추가, Microsoft ⑧ −3, 문장·위치 결함 7건 수정, 기업 요약 3건.
- 확인 리뷰 3차 pass. ⑧ 의 '몇 배(−3)'와 '1배 안팎(−2)'을 가르는 경계가 판단 문장의 2배 해석이었고 rules.md 에 없었다.
- 사용자 결정(2026-10-12): ⑧ 약정 축 경계를 20배 이상 −4 · 3배 이상 −3 · 0.5배 이상 −2 · 그 아래 0 으로 정했다. 14건의 공유 경계 줄을 바꿨고
  (`make_fix3.py`) Alphabet ⑧ 이 −2(2.02배)가 됐다. Meta 는 2026-07 추가 리스로 3.05배라 −3 이다.
- 확인 리뷰 4차(`confirm-r4.md`) pass. 경계 줄 14건이 글자 그대로 같고, 3차 대비 바뀐 칸은 Alphabet ⑧·함정·조정과 Microsoft 순위뿐이며, 엔진 재계산이
  저장된 results_hash 와 같다. 민감도: Meta ⑧ 3.05배는 3배 경계 바로 위(미완료라 순위 무관), 2위 Alphabet 13 과 3위 Microsoft 12 는 Microsoft ⑧ 고객 축
  34~37%(기간 미공시 계약을 보수적으로 편 값, 하한 아님)에 걸려 있다.
- 사용자 결정(2026-10-12): 이 실행은 승인하지 않는다. 규칙 v2.1 개정(①④⑥⑦⑧)으로 11월 정기 실행이 14사를 다시 매기며, 그 실행이 이 실행을
  `init --from-run` 으로 이어받는다. 승인된 10월 기록은 `ai-scorecard-2026-10-rejudge` 다.

## 판정

- results_hash `0b3fe1402a8a0c28…` · draft_hash `b035c8d023f0bfc8…` 기준 검토. 자료·규칙·판단·초안이 바뀌면 이 리뷰는 무효다(D-10).
- **두 해시의 뜻이 다르다.** `results_hash` 는 `results.json` 에서 `results_hash` 키를 뺀 내용의 정렬 JSON 해시이고(`engine.sha256_obj`) **파일 바이트 sha256 과 다르다.** `draft_hash` 는 초안 **파일 바이트 sha256** 이다. 대조할 때 섞지 않는다.
