---
slug: ai-scorecard-2026-10-v21
report_type: ai_scorecard
status: pass
created_at: 2026-10-12
plan_source: output/ai-scorecard-2026-10-v21/plan.md
research_source: output/ai-scorecard-2026-10-v21/research.md
draft_source: output/ai-scorecard-2026-10-v21/draft.md
results_hash: 7ebbb329bb1b7ffe2cd50fd6cfae599d9bb29ac8ad2f6b71798f4013a4d60eb4
draft_hash: a7e7ec8ca9ec9975246d99e50cacebb08cf86be9ca03c98562c15faefe6e6869
review_type: separate-session-4way
review_execution: separate_subagent_sessions
reviewers:
  - "fact-sources: fact-checker fs-a-v21-20261013-r1 → pass · fs-b-v21-20261013-r1 → needs_fix 3건(⑦ 세로축) → 수정 → pass · evidence-editor ev-v21-20261013-r1 → pass"
  - "financial-calc: general-purpose(Sonnet) fc-v21-20261013-r1 → pass"
  - "rule-consistency: general-purpose(Opus high) rc-v21-20261013-rule → needs_fix 1건(Palantir ④) → 수정 → pass"
  - "output-readability: report-designer or-v21-20261013-r1 → pass(트리거 점수 문장·렌더러 설명 수정)"
  - "confirm: general-purpose(Opus high) confirm-v21-20261013-r1 → pass"
  - "confirm: general-purpose(Opus high) confirm-v21-20261013-r2 → 막혔던 원문 재열람 뒤 변경분 확인 → pass"
  - "confirm: general-purpose(Opus high) confirm-v21-20261013-r3 → 승인 취소·Meta ③ 사용자 확정 뒤 변경분 확인"
---
# 리뷰 — 2026-10 규칙 v2.1 첫 실행(10월 사실)

각 영역은 가능하면 독립 세션에서 검토하고 실제 수행자·결과를 남긴다. 수행하지 않은 검토를 pass 로 표시하지 않는다.

## 검토 영역

| 영역 | 검토 대상 | 검토자 | 결과 | 요약 |
| --- | --- | --- | --- | --- |
| 사실·출처 | 숫자·기업 귀속·기준 시점·공시·뉴스·부재 주장 | fact-checker(1차·원문 다시 열기 대조) · Claude Opus 5.5 확인 리뷰 2차·3차 | pass | 이번 묶음은 새 근거가 없다. Meta ③ 판정 칸 0·4번 줄과 치환 6곳은 확정 근거의 사실(하한 두 시점, 2분기 콜까지 수치 없음)만 쓰고, 올릴·내릴 근거 표지 10개 모두 confirmed. 치환 6곳 new 1회·old 0회 |
| 재무 계산 | EPS·환율·ADR·TTM·FCF·런웨이·약정·단위·부호 | Claude Sonnet(1차) · Claude Opus 5.5 확인 리뷰 2차·3차 | pass | 바뀐 입력은 Meta ③ 가속도 하나. 통과점 1 → 2, Meta 과점 18·함정 −5·조정 13, 11개사 순위 +1. 결정론적 재계산·순위표 대조 통과, 요약 14건·draft 순위표·상세 머리를 기계 대조해 어긋남 0 |
| 규칙 일관성 | factor 정의·상하한·예외·중복 속성·정성 승계·전 기업 동일 기준 | Claude Opus 5.5(1차) · Claude Opus 5.5 확인 리뷰 2차·3차 | pass | 가속도 fail 은 사람이 승인 페이지에서 고친 값(guide 5.5 범위, 이력 완비)이라 뒤집지 않는다. 단계 e 는 Meta·Apple 둘 다 fail 로 같은 값이고 근거만 사용자 결정·지연 조항으로 갈린다. rules.md 178·198행 문언과의 거리는 사용자 결정으로 밝혀 두고 TODO 「나」 4번으로 넘어갔다. Q01~Q23 fail 없음 |
| 출력·가독성 | 표·카드·근거·차트·이력 일치, 낡은 비교 문장, 모바일·단일 HTML | report-designer(1차) · Claude Opus 5.5 확인 리뷰 2차·3차 | pass | 메모리 렌더에서 탭 일곱(국면 지표 자기 탭), 순위 열 없음, 설명 상자 두 곳, (가)·(나) 표지 속성 침범 0, Meta 가 순위표·산점도·막대·KPI 에 들어옴. Meta ③ 옛 서술 0건. 방법 절 "예외가 하나 있다" 는 점수 무관이라 다음 실행 과제 |

결과는 pass / needs_fix / blocked 중 하나. 네 영역이 모두 pass 이고 체크리스트에 fail 이 없을 때만 frontmatter `status: pass`.
**승계 판단 예외(AGENTS.md 리뷰 범위 · 기업 추가 실행에만, rules.md 2.9)** — 정기 실행에서는 체크리스트 fail 이 하나라도 있으면 `status: pass` 가 아니다. 기업 추가 실행에서는 체크리스트 fail 의 사유가 `carried_score` 로 승계한 판단의 기존 논리이고, 이번 실행이 그 판단에 쓰인 잣대를 바꾸지 않았으며, 규칙 파일 `open_tensions` 에 재검토 시점과 함께 등록됐다면 `status: pass` 를 막지 않는다. 이때 해당 fail 과 **긴장 번호**(예: `TEN-RC-02`)를 근거 칸에 그대로 적는다. 이번 실행이 바꾼 잣대가 닿는 승계 판단은 이 예외가 아니다 — 한 회사에 새 잣대를 댔으면 같은 잣대가 닿는 모든 회사에 대야 한다(Q03).

## 체크리스트

| ID | 검사 초점 | 결과 | 근거 |
| --- | --- | --- | --- |
| Q01 | 이 감점, 다른 칸에서 이미 셌나? | pass | Meta 가속도 fail 은 ③ 한 칸에서만 쓰이고, 제3자 Muse 순증 감소(EV-meta-057)는 ③ 반대 방향 방증으로만 남아 다른 칸 점수에 들어가지 않는다. ④ 보유표의 Meta 칸(칩·서버·플랫폼 자체 사용, 모델·응용 판매)은 ③ 에서 모방 불가능 자산 후보로만 읽혀 실패이고 ④ 점수와 겹쳐 세지 않는다. 2차 판정(Apple IDC·Alibaba 목록가·두 소송의 칸 구분)은 이번 묶음이 건드리지 않아 그대로다. |
| Q02 | 이 지표가 이 칸의 정의에 맞나? | pass | Meta ③ 가속도 판정은 AI 귀속 지표(Meta AI 월간 사용자, d 단계 후보)만 보고 광고 매출 성장을 쓰지 않는다(규칙 48행). 2차 판정(Oracle ④ 모델 칸 정의)과 1차 과제(Palantir ③ c 대리 지표)는 그대로다. |
| Q03 | 회사마다 같은 잣대인가? | pass | 지표 단계 e 는 Meta·Apple 둘뿐이고 둘 다 가속도 fail, ③ 2점이다. Apple 은 지연 조항, Meta 는 사용자 결정(2026-10-13, 정한솔, 승인 페이지 직접 수정)으로 서서 근거가 갈리지만 어느 잣대를 둘 다에 대도 값이 같아 한쪽만 엄격하거나 관대한 칸이 없다. b 수준값이 모자란 Amazon·Alibaba 는 c 로 내려갔고 Meta 는 내려갈 c 지표가 없다. 명시적 진술 대리 지표는 어느 회사에도 쓰이지 않았다. 사람의 결정이라 리뷰가 뒤집지 않으며, 단계 e 처리를 규칙 한 문장으로 정하는 일은 TODO.md 「나」 4번으로 넘어갔다. 2차의 표 넷(두 소송·타사 모델 판매·(나)·EU 지정)은 이번 묶음이 건드리지 않아 그대로다. |
| Q04 | 시총 크기를 밸류에이션으로 착각했나? | pass | ⑥ 변경 없음, 비율만 쓴다. |
| Q05 | 출처가 이해당사자인가? | pass | 결과 칸만 채운다. 이해상충 표기는 AGENTS.md 「금지·주의」에 따라 보지 않았다. |
| Q06 | 볼륨인가 가치인가? | pass | 변경 없음. Muse 주간 이용자 300만·하루 이용자 60% 증가는 ③ 에서 판정에 쓰지 않은 사용 지표로만 남고 가치로 읽히지 않는다. |
| Q07 | "안 만든 것"을 카운터 포지셔닝으로 셌나? | pass | 변경 없음. Meta ③ 의 별도 수익모델 통과는 광고 매출과 Muse 구독이라는 회수 장치에서 오고 "안 만든 것" 을 세지 않는다. |
| Q08 | 적대세력을 수로 셌나, 성격으로 셌나? | pass | 변경 없음. |
| Q09 | 미래 계획을 현재 점수에 넣었나? | pass | Meta ③ 은 앞으로 나올 같은 정의의 값을 점수에 넣지 않고 다시 판정할 조건으로만 적는다(판정 칸 4번 줄, TRG-011 재검토 2026-11-10). 트리거에 미래 점수가 없다. |
| Q10 | 거리를 가속도로 착각했나? | pass | Meta 가속도 판정에 누적 성과(36억 일간 사용자, Advantage+ 연환산 $75B, 300만 주간 이용자)를 쓰지 않는다. 한 시점 수치와 성장률 하나는 가속인지 가를 수 없다고 판정 칸이 밝힌다. |
| Q11 | 순적자를 실격 사유로 썼나? | pass | 변경 없음. |
| Q12 | ③ 세 기준을 동등하게 쟀나? | pass | Meta ③ 은 세 기준을 따로 판정하고(모방 불가능성 실패·별도 수익모델 통과·가속도 실패) 사다리가 통과점 1 → 2 로 환산한다. 4점 조건(모방 불가능성 완전 통과)에 닿지 않는다. |
| Q13 | "공짜로 뿌린다"를 곧바로 카운터 포지셔닝으로 셌나? | pass | Meta Muse 무료 이용은 월 $20·$100 구독과 광고라는 회수 장치와 함께 판정됐다. Muse Spark 1.2 오픈웨이트가 나오면 다시 보는 조건은 TRG-056 에 그대로 있다. |
| Q14 | 아직 안 끝난 승부를 끝난 것처럼 쟀나? | pass | Meta 문 닫힘은 실패이고 5점 관문에 닿지 않는다. |
| Q15 | ⑤에서 "공짜 사용자"를 아군으로 셌나? | pass | 변경 없음. |
| Q16 | ①을 한 채널로만 쟀나? | pass | 변경 없음. |
| Q17 | ②를 "표준 없음"만으로 깎았나? | pass | 변경 없음. |
| Q18 | ⑤에서 관계사를 독립 동맹으로 셌나? | pass | 변경 없음. |
| Q19 | ⑤에서 "받은 투자"를 곧바로 동맹 +2로 셌나? | pass | 변경 없음. |
| Q20 | 조달을 동맹으로 셌나? | pass | 변경 없음. |
| Q21 | 동맹이자 의존인 관계를 한쪽에서만 셌나, 또는 같은 속성을 양쪽에서 셌나? | pass | 변경 없음. |
| Q22 | 지분 평가이익을 ⑦ 순환금융 증거로 셌나? | pass | 변경 없음. |
| Q23 | 벤치마크를 서로 다른 하네스끼리 비교했나? | pass | 변경 없음. 1차 판정(코딩은 참가자 전원이 자기 제품 하네스로 잰 지표, 종합 지수 버전 표기는 과제 2)을 잇는다. |

결과는 pass / fail / not_applicable. not_applicable 도 근거가 필요하다.

## 발견 사항

- 1차 리뷰 여섯(`review-parts/rule-consistency.md`, `fact-sources-a.md`, `fact-sources-b.md`, `financial-calc.md`, `output-readability.md`, `evidence-bullets.md`)의
  needs_fix 는 넷이었다. Palantir ④ AI 무관 몫(규칙 일관성 N1), ⑦ 세로축 Palantir·Alibaba·OpenAI(사실·출처 b 1~3). 수정 한 묶음
  (`.agents/plans/v21-first-run-2026-10/FIX-INSTRUCTIONS.md`, `work/judge-fix1/`) 뒤 확인 리뷰 1차(`confirm-r1.md`)가 pass 했다.
- 점수에 닿지 않는 발견과 다음 실행 과제는 각 리뷰 파일의 「다음 실행 과제」 절에 있다. 리포트에 보이는 표시 결함 셋(TRG-023 의 Oracle ⑦ 옛 점수,
  ② 변경을 못 따라온 TRG-091·097)도 거기에 있다.

## 리뷰 경위

- 2026-10-13 1차 리뷰 여섯 세션(규칙 일관성·판단 검증은 Opus high, 사실·출처·재무·근거 불릿·출력은 Sonnet). 사실·출처 a 는 사용량 한도로 늦어져 같은 세션을 이어서 끝냈다.
- 수정 한 묶음: 판단 19건(점수가 바뀐 칸은 Palantir ④ 2→4.5·⑦ 0→−1, Alibaba ⑦ 0→−1. 나머지는 문장·근거 정정), 새 근거 16건(원문 대조 뒤 확정),
  새 트리거 2건, 트리거·근거 문장 치환 76항목, 기업 요약 4건. 조정 총점은 Palantir 5→6.5(10위→8위), Alibaba 7→6(8위→9위)이고 Tesla 는 9위→10위다.
- 사용자 지시(2026-10-13): CNBC 'Microsoft will mainly use its Maia chips for AI inference'(2026-10-12)를 추적한다. CNBC 본문은 접근 거부라 1차 발표인
  Microsoft 공식 블로그(2026-10-12)를 원문으로 근거 4건(EV-microsoft-070~073)과 트리거 TRG-121(Microsoft ④⑧)·TRG-122(NVIDIA ①⑧)를 두었다.
  2027년 다기가와트·주력 추론은 계획이라 점수에 넣지 않았다.
- Apple ④ 는 모델 칸의 유료 한도 확대가 계획이라 판매 칸이 없어 비교 그룹이 없다. 이 경우를 받도록 검증기·렌더러를 고쳤다(커밋 59d59e3).
- ② 는 정보 마감 당일 Artificial Analysis 의 Muse Wonder 평가를 2026-10-08 순위표에 더해 14개사를 같은 시점으로 비교한다(점수 불변).
- 경계 사례: Oracle ⑦ 의 TikTok 합작 연결은 추론으로 선 '돌아옴'(무거운 쪽)이다. 돌아오지 않음으로 읽으면 Oracle 은 −3→−2, 조정 8.5(7위)다.
- 사용자 결정(2026-10-13): 스크립트 요청이 403 이면 실제 브라우저로 다시 열고, 거기서도 막히면 우회하지 않는다(AGENTS.md 「원자료 조사 규율」). 이 규칙 이전에
  스크립트만 막혀 2차 기사로 대신했던 원문 아홉 건을 다시 열었다(`.agents/plans/v21-first-run-2026-10/work/reopen1/report.md`). 사용자가 USA TODAY 소장 PDF 와
  Seeking Alpha 본문을 직접 줬다. 원문 근거 12건을 확정하고 판단 9건의 문장·근거 표지와 근거 메모 16건을 고쳤다. 점수·순위는 바뀌지 않았다.
  확인 리뷰 2차(`confirm-r2.md`)가 이 변경분을 봤다.
- 2026-10-13 사용자가 승인한 뒤 승인을 취소하고, 승인 페이지에서 Meta ③ 의 후발 가속도를 unknown 에서 fail 로 직접 고쳤다(지표 단계 e, 사유 "일단 2점 확정 후 보기 위함").
  판정 칸 문장·기업 요약 12건·트리거와 근거의 옛 서술 6곳을 맞췄고, Meta 가 13점으로 Alphabet·Amazon 과 공동 1위가 되어 14개사가 모두 순위에 들었다.
  지표가 없는 회사의 가속도 처리는 TODO.md 「나-4」에서 규칙 문장으로 정한다. 확인 리뷰 3차(`confirm-r3.md`)가 이 변경분을 봤다.

## 판정

- results_hash `7ebbb329bb1b7ffe…` · draft_hash `a7e7ec8ca9ec9975…` 기준 검토. 자료·규칙·판단·초안이 바뀌면 이 리뷰는 무효다(D-10).
- **두 해시의 뜻이 다르다.** `results_hash` 는 `results.json` 에서 `results_hash` 키를 뺀 내용의 정렬 JSON 해시이고(`engine.sha256_obj`) **파일 바이트 sha256 과 다르다.** `draft_hash` 는 초안 **파일 바이트 sha256** 이다. 대조할 때 섞지 않는다.
