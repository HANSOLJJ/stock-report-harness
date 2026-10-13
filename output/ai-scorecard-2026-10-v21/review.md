---
slug: ai-scorecard-2026-10-v21
report_type: ai_scorecard
status: pass
created_at: 2026-10-12
plan_source: output/ai-scorecard-2026-10-v21/plan.md
research_source: output/ai-scorecard-2026-10-v21/research.md
draft_source: output/ai-scorecard-2026-10-v21/draft.md
results_hash: 0a4d9739e259929974f5bf091e811bd5faa1e990572e58795fa0158a3aa08662
draft_hash: c856687f8df67598bff4c3a15379695d7ede780ab23253bb285a95ac36903002
review_type: separate-session-4way
review_execution: separate_subagent_sessions
reviewers:
  - "fact-sources: fact-checker fs-a-v21-20261013-r1 → pass · fs-b-v21-20261013-r1 → needs_fix 3건(⑦ 세로축) → 수정 → pass · evidence-editor ev-v21-20261013-r1 → pass"
  - "financial-calc: general-purpose(Sonnet) fc-v21-20261013-r1 → pass"
  - "rule-consistency: general-purpose(Opus high) rc-v21-20261013-rule → needs_fix 1건(Palantir ④) → 수정 → pass"
  - "output-readability: report-designer or-v21-20261013-r1 → pass(트리거 점수 문장·렌더러 설명 수정)"
  - "confirm: general-purpose(Opus high) confirm-v21-20261013-r1 → pass"
---
# 리뷰 — 2026-10 규칙 v2.1 첫 실행(10월 사실)

각 영역은 가능하면 독립 세션에서 검토하고 실제 수행자·결과를 남긴다. 수행하지 않은 검토를 pass 로 표시하지 않는다.

## 검토 영역

| 영역 | 검토 대상 | 검토자 | 결과 | 요약 |
| --- | --- | --- | --- | --- |
| 사실·출처 | 숫자·기업 귀속·기준 시점·공시·뉴스·부재 주장 | fact-checker(a·b, 1차) · Claude Opus 5.5 확인 리뷰 | pass | 1차 a pass·b needs_fix 3건(⑦ 세로축 Palantir·Alibaba·OpenAI)은 공시·1차 근거 신설(EV-palantir-051, EV-alibaba-092·093, EV-openai-157~159)로 풀렸고 a 의 F1~F4 문장도 고쳐졌다. 새 근거 16건 확정·출처 등록·발행일 정보 마감 이하, 마감 뒤 근거 0건, 트리거 근거 전부 확정. 근거 relevance 의 옛 점수 24건은 표시 문장이라 다음 실행 과제 |
| 재무 계산 | EPS·환율·ADR·TTM·FCF·런웨이·약정·단위·부호 | Claude Sonnet(1차) · Claude Opus 5.5 확인 리뷰 | pass | 1차 pass. 바뀐 칸을 다시 셈 — Palantir AI 무관 $6,155,941천 = 최근 1년 매출, ④ 2 + 2.5 = 4.5, Alibaba 투자 대상 클라우드 매출 9,415 ÷ 1,023,670 = 0.92%, Palantir 상반기 $3M. 결정론적 재계산·순위표 대조가 검증기에서 통과하고 TRG-017 의 성장 조정 PER 1.08 이 results 와 같다 |
| 규칙 일관성 | factor 정의·상하한·예외·중복 속성·정성 승계·전 기업 동일 기준 | Claude Opus 5.5(1차) · Claude Opus 5.5 확인 리뷰 | pass | N1 풀림(Palantir ④ 4.5). ⑦ 세로축 14개사·② 같은 시점 순위표·Maia 사건·Apple ①④⑧ 계획 읽기·Meta⑧↔NVIDIA 분기 뒤 처리를 교차표로 다시 놓아 같은 구조에 같은 칸임을 확인했다. Oracle TikTok 합작 연결(추론, 무거운 쪽)은 1차 리뷰의 다음 실행 과제 그대로. Q01~Q23 fail 없음 |
| 출력·가독성 | 표·카드·근거·차트·이력 일치, 낡은 비교 문장, 모바일·단일 HTML | report-designer(1차) · Claude Opus 5.5 확인 리뷰 | pass | B1 12건·TRG-025·027·017 과 렌더러 문장 반영 확인, Apple ④ '비교 그룹 없음' 이 draft·HTML(메모리 렌더) 모두 맞다. 남은 표시 결함 — TRG-023 의 Oracle ⑦ −2, ② 변경을 못 따라온 TRG-091·097 — 은 점수 무관이라 다음 실행 과제 |

결과는 pass / needs_fix / blocked 중 하나. 네 영역이 모두 pass 이고 체크리스트에 fail 이 없을 때만 frontmatter `status: pass`.
**승계 판단 예외(AGENTS.md 리뷰 범위 · 기업 추가 실행에만, rules.md 2.9)** — 정기 실행에서는 체크리스트 fail 이 하나라도 있으면 `status: pass` 가 아니다. 기업 추가 실행에서는 체크리스트 fail 의 사유가 `carried_score` 로 승계한 판단의 기존 논리이고, 이번 실행이 그 판단에 쓰인 잣대를 바꾸지 않았으며, 규칙 파일 `open_tensions` 에 재검토 시점과 함께 등록됐다면 `status: pass` 를 막지 않는다. 이때 해당 fail 과 **긴장 번호**(예: `TEN-RC-02`)를 근거 칸에 그대로 적는다. 이번 실행이 바꾼 잣대가 닿는 승계 판단은 이 예외가 아니다 — 한 회사에 새 잣대를 댔으면 같은 잣대가 닿는 모든 회사에 대야 한다(Q03).

## 체크리스트

| ID | 검사 초점 | 결과 | 근거 |
| --- | --- | --- | --- |
| Q01 | 이 감점, 다른 칸에서 이미 셌나? | pass | ⑦ 돌아옴(Palantir·Alibaba 투자 대상 매출)은 ⑦ 에서만 세고 ⑧ 의 EV-alibaba-089 인용은 함정을 얕게 하는 쪽이다. Maia 는 NVIDIA ① 대체 공급(락인 강도)과 ⑤ 구조형(적대의 성격)에서 다른 질문으로 읽히고 ⑧ 은 '⑤ 소관' 이라 고객 축에 넣지 않는다. Microsoft 의 Anthropic 투자 이익은 ⑤ 지분 동맹 근거로만 쓰였다. 우발 보증은 ⑧ 약정에서 빼고 ⑦ 에서만 본다(Meta·NVIDIA 같음). |
| Q02 | 이 지표가 이 칸의 정의에 맞나? | pass | Palantir ④ 다각화가 수요 분류 정의(기업용 소프트웨어 줄은 AI 무관)로 돌아왔다. Palantir ③ c 단계(미국 상업 매출 대리)는 ④ 가 AI 무관으로 센 줄을 ③ 의 AI 대리 지표로 쓰는 것이나, ③ c 는 '섞인 대리 지표, 최대 부분' 이라 정의에 맞는다(과제 6). |
| Q03 | 회사마다 같은 잣대인가? | pass | ⑦ 세로축 14개사 표, ② 같은 시점 순위표(공동 1위 읽기를 Anthropic·Meta 에 같게), Maia 와 TPU·Trainium·MTIA 의 칩 칸·대체 공급 읽기, Apple ①④⑧ 의 iCloud+ 계획 읽기, Meta ⑧ 체결 리스 ↔ NVIDIA 우발 보증(rules.md 393행)이 모두 같은 잣대다. 자료의 유무로 갈린 줄은 없다. Oracle ⑦ 의 추론 연결은 1차 리뷰가 넘긴 다음 실행 과제로 이번 묶음이 잣대를 바꾸지 않았다. |
| Q04 | 시총 크기를 밸류에이션으로 착각했나? | pass | ⑥ 은 비율만 쓴다(이번 묶음 변경 없음). |
| Q05 | 출처가 이해당사자인가? | pass | 결과 칸만 채운다. 이해상충 표기는 AGENTS.md 「금지·주의」에 따라 보지 않았다. |
| Q06 | 볼륨인가 가치인가? | pass | 변경 없음. 토큰 점유율은 방증으로만 쓴다. |
| Q07 | "안 만든 것"을 카운터 포지셔닝으로 셌나? | pass | 변경 없음. 모델 없는 회사의 ③ 통과 없음. |
| Q08 | 적대세력을 수로 셌나, 성격으로 셌나? | pass | Microsoft ⑤ H −1 은 성격(비용형)으로, 지분 동맹 추가는 상한 +2 로 결과 불변. |
| Q09 | 미래 계획을 현재 점수에 넣었나? | pass | Maia 2027 다기가와트·주력 추론, Apple 유료 한도 확대, OpenAI YC 교환(제안 단계), Cursor 차단(기준일 뒤)을 모두 점수 밖에 두었다. 트리거 TRG-121·122 에 미래 점수 없음. |
| Q10 | 거리를 가속도로 착각했나? | pass | 변경 없음. ③ 가속도는 성장률 둘로 판정. |
| Q11 | 순적자를 실격 사유로 썼나? | pass | 변경 없음. |
| Q12 | ③ 세 기준을 동등하게 쟀나? | pass | 변경 없음. ③ 4점은 TSMC 하나. |
| Q13 | "공짜로 뿌린다"를 곧바로 카운터 포지셔닝으로 셌나? | pass | 변경 없음. |
| Q14 | 아직 안 끝난 승부를 끝난 것처럼 쟀나? | pass | 변경 없음. ③ 5점 없음. |
| Q15 | ⑤에서 "공짜 사용자"를 아군으로 셌나? | pass | 변경 없음. |
| Q16 | ①을 한 채널로만 쟀나? | pass | Apple ① 은 소비자 채널 하나로 판정하고 iCloud+ 계획을 그 채널의 AI 수익화에서 계획으로 뺐다. |
| Q17 | ②를 "표준 없음"만으로 깎았나? | pass | ② 2점(Apple·Palantir)은 세 경로를 모두 보고 나왔다. Alphabet·SpaceX 의 성능 도약 실패는 점수를 바꾸지 않는다. |
| Q18 | ⑤에서 관계사를 독립 동맹으로 셌나? | pass | Tesla–SpaceX 는 ⑤ 에서 빼고 ⑦ 에서는 실행된 투자 사실로만 돌아옴을 세웠다(관계사라는 사실로 세지 않음). |
| Q19 | ⑤에서 "받은 투자"를 곧바로 동맹 +2로 셌나? | pass | Microsoft·NVIDIA 의 Anthropic 투자는 Anthropic ⑤ A 에 세지 않는다(변경 없음). |
| Q20 | 조달을 동맹으로 셌나? | pass | 변경 없음. |
| Q21 | 동맹이자 의존인 관계를 한쪽에서만 셌나, 또는 같은 속성을 양쪽에서 셌나? | pass | 변경 없음. Microsoft–Anthropic 은 ⑤ 동맹(경쟁사 편입·지분)과 ⑧ 고객 분산을 따로 센다. |
| Q22 | 지분 평가이익을 ⑦ 순환금융 증거로 셌나? | pass | Microsoft 의 Anthropic 투자 이익 $3.2B 는 ⑤ 근거이고 ⑦ 입력이 아니다. Palantir·Alibaba ⑦ 은 평가이익이 아니라 매출 계약으로 섰다. |
| Q23 | 벤치마크를 서로 다른 하네스끼리 비교했나? | pass | 코딩은 참가자 전원이 각자 제품 하네스로 잰 지표(Muse Code 포함)다. 종합 지수 'v4.3'(2026-10-12 글)과 'v4.3.2'(2026-10-08 홈페이지) 표기 차이로 Meta 종합 지수 회사 기준 2위만 두 출처의 절대값을 잇지만, 판정을 가르는 비교(Anthropic GDPval 1위·코딩 공동 1위, Meta 코딩 공동 1위)는 한 글 안의 순위로 서고 대조 값이 2026-10-08 표와 같다(과제 2). |

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
- 경계 사례: Oracle ⑦ 의 TikTok 합작 연결은 추론으로 선 '돌아옴'(무거운 쪽)이다. 돌아오지 않음으로 읽으면 Oracle 은 −3→−2, 조정 8.5(6위)다.

## 판정

- results_hash `0a4d9739e2599299…` · draft_hash `c856687f8df67598…` 기준 검토. 자료·규칙·판단·초안이 바뀌면 이 리뷰는 무효다(D-10).
- **두 해시의 뜻이 다르다.** `results_hash` 는 `results.json` 에서 `results_hash` 키를 뺀 내용의 정렬 JSON 해시이고(`engine.sha256_obj`) **파일 바이트 sha256 과 다르다.** `draft_hash` 는 초안 **파일 바이트 sha256** 이다. 대조할 때 섞지 않는다.
