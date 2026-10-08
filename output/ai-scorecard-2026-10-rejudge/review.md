---
slug: ai-scorecard-2026-10-rejudge
report_type: ai_scorecard
status: pass
created_at: 2026-10-08
plan_source: output/ai-scorecard-2026-10-rejudge/plan.md
research_source: output/ai-scorecard-2026-10-rejudge/research.md
draft_source: output/ai-scorecard-2026-10-rejudge/draft.md
results_hash: b466a98c43bccef948b8f27ddf1027a1ec5499f71ea36dae715bb747dc2c09d4
draft_hash: 2ae12bf6ac545060e4b07c3dd6d8a31944b2600930b3efb483a1d40338d55b34
review_type: separate-session-4way
review_execution: separate_subagent_sessions
reviewers:
  - "fact-sources: fact-checker fs-a-rejudge-20261009-r1 · fs-b-rejudge-20261009-r1 → pass"
  - "financial-calc: general-purpose fc-rejudge-20261009-r1 → needs_fix → 수정 → pass"
  - "rule-consistency: general-purpose rc-rejudge-20261009-r1 → needs_fix → 수정 → pass"
  - "output-readability: report-designer or-rejudge-20261009-r1 → needs_fix → 수정 → pass"
  - "confirm: general-purpose cf-rejudge-20261009-r2 → pass"
---
# 리뷰 — 2026-10 전부 재판단(v2.0)

각 영역은 가능하면 독립 세션에서 검토하고 실제 수행자·결과를 남긴다. 수행하지 않은 검토를 pass 로 표시하지 않는다.

## 검토 영역

| 영역 | 검토 대상 | 검토자 | 결과 | 요약 |
| --- | --- | --- | --- | --- |
| 사실·출처 | 숫자·기업 귀속·기준 시점·공시·뉴스·부재 주장 | fact-checker ×2 (fs-a-rejudge-20261009-r1 · fs-b-rejudge-20261009-r1) + 확인 general-purpose (cf-rejudge-20261009-r2) | pass | 14사 판단 98건의 근거 줄 796개와 그 줄이 가리키는 근거 555건을 전수로 원문과 대조해 모두 발췌를 찾았고, 새 관측 108건이 원문으로 재현됐다. 점수를 바꾸는 발견은 없었고, 원문과 어긋난 문장(tsmc ⑤ Intel, anthropic ① 점유율 시점, alibaba ② ARC 순위표, amazon ⑤ $2.5B 등)과 locator 6건·발행일 1건을 수정 묶음에서 고쳤다. 확인 리뷰가 새 근거 EV-meta-056 과 고친 줄 전부를 다시 대조해 pass. |
| 재무 계산 | EPS·환율·ADR·TTM·FCF·런웨이·약정·단위·부호 | general-purpose (fc-rejudge-20261009-r1) + 확인 general-purpose (cf-rejudge-20261009-r2) | pass | ⑥ 상장 12사 시총·환율·P1~P4, ⑦ 14사 분자·분모·연간화, ⑨ 게이트, ③ 성장률 두 개, ⑧ 비율과 새 관측 108건의 단위·TTM·기준일이 맞고 결측을 0 으로 쓴 곳이 없다. needs_fix 1건(anthropic ③ 별도 수익모델이 총마진 전망치에 섬)은 입력을 partial 로 고쳐 해소했고(③ 2점 그대로), 엔진 재계산이 results_hash 를 그대로 낸다. |
| 규칙 일관성 | factor 정의·상하한·예외·중복 속성·정성 승계·전 기업 동일 기준 | general-purpose (rc-rejudge-20261009-r1) + 확인 general-purpose (cf-rejudge-20261009-r2) | pass | 판정 입력에서 점수로 가는 길을 ①②③⑤⑦ 70칸에서 따로 재현해 어긋남 0, 정성 판단 98건 모두 이 실행의 새 판단이고 승계 없음, open 쟁점 14건 가운데 13건이 재판단으로 닫힘. needs_fix 4건(⑦ 수치 임계·nvidia 큼으로 −2, meta ④ 칩 자리, alibaba 1260H 이중 계산, ⑤ 판매자 쪽 고객 잣대)을 고쳐 Q01·Q02·Q03·Q21 이 pass 로 바뀌었다. |
| 출력·가독성 | 표·카드·근거·차트·이력 일치, 낡은 비교 문장, 모바일·단일 HTML | report-designer (or-rejudge-20261009-r1) + 확인 general-purpose (cf-rejudge-20261009-r2) | pass | 초안 순위표·카드 126칸·KPI·원자료 점수와 메모리 렌더 HTML 이 results 와 어긋남 0, 320·768·1280px 가로 넘침 0, 요약 상자·①②③ 새 표시가 판단 입력과 같다. needs_fix 1건(트리거 문장이 지난 점수를 지금 판단처럼 적음)은 트리거 20건을 다시 써 해소했고, 기업 요약 14건을 새로 실었으며 요약 상자에 ⑨ 게이트 판정 입력 칸을 적었다. |
결과는 pass / needs_fix / blocked 중 하나. 네 영역이 모두 pass 이고 체크리스트에 fail 이 없을 때만 frontmatter `status: pass`.
**승계 판단 예외(AGENTS.md 리뷰 범위 · 기업 추가 실행에만, rules.md 2.9)** — 정기 실행에서는 체크리스트 fail 이 하나라도 있으면 `status: pass` 가 아니다. 기업 추가 실행에서는 체크리스트 fail 의 사유가 `carried_score` 로 승계한 판단의 기존 논리이고, 이번 실행이 그 판단에 쓰인 잣대를 바꾸지 않았으며, 규칙 파일 `open_tensions` 에 재검토 시점과 함께 등록됐다면 `status: pass` 를 막지 않는다. 이때 해당 fail 과 **긴장 번호**(예: `TEN-RC-02`)를 근거 칸에 그대로 적는다. 이번 실행이 바꾼 잣대가 닿는 승계 판단은 이 예외가 아니다 — 한 회사에 새 잣대를 댔으면 같은 잣대가 닿는 모든 회사에 대야 한다(Q03).

## 체크리스트

| ID | 검사 초점 | 결과 | 근거 |
| --- | --- | --- | --- |
| Q01 | 이 감점, 다른 칸에서 이미 셌나? | pass | 1차 fail 사유(1260H 를 ⑤·⑧ 이 함께 셈)가 해소됐다. alibaba.F5 는 1260H 를 ⑧ 지정학 축에서만 센다고 적고 적대 −1 을 EU 디지털서비스법 벌금으로 받치며, alibaba.F8 은 1260H 를 그대로 센다. 그 벌금 충당금이 ⑨ G1 영업이익률에도 들어 있는 것은 규제 적대(⑤)와 수익성(⑨)이라는 다른 속성이고 meta·spacex-xai 벌금과 같은 처리다. 대만 집중은 ⑧ 에서만, nvidia 고객 자체 칩·tesla NHTSA·palantir 정당성 공격은 ⑤ 에서만 센다 |
| Q02 | 이 지표가 이 칸의 정의에 맞나? | pass | 1차 fail 사유(⑦ 의 '절반' 수치 임계)가 해소됐다. ⑦ 14건이 "규칙 ⑦ 에 따라 큼·작음에 수치 임계를 두지 않는다" 는 같은 문장을 쓰고 '절반' 이 0번이다. anthropic ① 은 라우팅 서비스 토큰 점유율을 방증으로만 두고 정가 인하로 실패를 정한다(1차 L2 해소) |
| Q03 | 회사마다 같은 잣대인가? | pass | 1차 fail 사유 둘이 해소됐다. meta ④ 는 EV-nvidia-038 을 다른 다섯 판단처럼 'Meta 가 MTIA 를 운용한다' 로 읽고 1차 출처 EV-meta-056 으로 칩 자리를 센다(N2). ⑤ 는 유형 요소 없는 판매자 쪽 고객을 tsmc·spacex-xai·meta 에서 같은 문장으로 빼고 spacex-xai 의 해지 조항 사유가 빠졌다(N4). ① anthropic·openai 거래 채널 잣대, ⑦ 14건 둘째 줄, ⑤ 14건 첫머리 네 줄이 같은 문장이다. oracle.F5 의 'OCI 고객 수요' 문구(L3)는 +1 이 지분 동맹으로 서서 등급에 닿지 않는다 |
| Q04 | 시총 크기를 밸류에이션으로 착각했나? | pass | 정성 판단 98건과 기업 요약 14건에 시가총액 크기를 판정 재료로 쓴 문장이 없다. ⑥ 은 관측에서 프로그램이 계산한다 |
| Q05 | 출처가 이해당사자인가? | pass | 벤더 성능 발표는 방증으로만 쓴다. 새 근거 EV-meta-056 은 성능 수치가 아니라 Meta 가 자기 칩을 배치했다는 사실에 대한 회사 1차 발표이고, 외부 분석(EV-nvidia-038)이 함께 받친다. 이해상충 표기는 판정 사유로 보지 않았다 |
| Q06 | 볼륨인가 가치인가? | pass | anthropic·openai ① 이 토큰 점유율을 '매출 점유율이 아니며 라우팅 서비스는 전체 시장이 아니다' 로 한정하고 방증으로만 둔다. 토큰 볼륨은 ③ 가속도에 쓰이지 않는다 |
| Q07 | "안 만든 것"을 카운터 포지셔닝으로 셌나? | pass | 1차와 같다. amazon ③·palantir ② 가 모델을 안 만든 사실을 점수 근거로 쓰지 않는다 |
| Q08 | 적대세력을 수로 셌나, 성격으로 셌나? | pass | 14건 모두 '전선 수가 아니라 성격' 문장을 적는다. alibaba 는 EU 벌금으로 비용형 −1, anthropic 은 큰 고객이 경쟁사라 구조형 −2, openai 는 전선이 많아도 비용형 −1 이다 |
| Q09 | 미래 계획을 현재 점수에 넣었나? | pass | 1차 fail 사유(anthropic ③ 별도 수익모델이 2025년 매출총이익률 전망치에 섬)가 해소됐다. 입력이 partial 이고 올릴 근거가 "2025년 값은 전망치라 점수에 넣지 않는다" 를 적는다. ④ 는 양산 전 칩·인수 서명을 빼고(openai Jalapeño 배치 미확인, nvidia Hugging Face 종결 전), meta ④ 칩 자리는 배치·서빙 사실로 센다 |
| Q10 | 거리를 가속도로 착각했나? | pass | 1차와 같다. 지표가 있는 12건이 성장률 둘의 변화로 판정하고 anthropic ③ 은 절대 규모·증가 폭을 거리로 뺀다 |
| Q11 | 순적자를 실격 사유로 썼나? | pass | anthropic ③ 별도 수익모델은 적자가 아니라 단위경제 미확인으로 부분이고 '적자 규모는 이 기준의 판정 사유가 아니다(규칙 2.5)' 를 그대로 적는다. openai ③ 은 양의 총이익률로 통과다 |
| Q12 | ③ 세 기준을 동등하게 쟀나? | pass | 4점은 tsmc 하나이고 모방 불가능성이 완전 통과다. anthropic 은 통과점 0.5 로 2점이다 |
| Q13 | "공짜로 뿌린다"를 곧바로 카운터 포지셔닝으로 셌나? | pass | 1차와 같다. alibaba 오픈웨이트는 회수 장치가 없어 모방 불가능성 실패다 |
| Q14 | 아직 안 끝난 승부를 끝난 것처럼 쟀나? | pass | 14사 모두 문 닫힘 fail 이고 ③ 5점이 없다 |
| Q15 | ⑤에서 "공짜 사용자"를 아군으로 셌나? | pass | Qwen 파생 모델·오픈웨이트·Hugging Face 개발자를 세지 않는다 |
| Q16 | ①을 한 채널로만 쟀나? | pass | 14건 모두 가장 강한 채널 하나의 네 질문으로 판정하고, openai ① 은 거래 채널 정가 인하를 "보조 채널이라 판정에 넣지 않는다" 고 적는다. alphabet 기업 요약의 '세 채널' 문구(L6)는 판정이 아니라 요약 문장이다 |
| Q17 | ②를 "표준 없음"만으로 깎았나? | pass | 1차와 같다. 2점(apple·palantir)은 세 경로가 모두 막힌 경우다 |
| Q18 | ⑤에서 관계사를 독립 동맹으로 셌나? | pass | tesla↔spacex-xai 관계를 양쪽에서 뺀다 |
| Q19 | ⑤에서 "받은 투자"를 곧바로 동맹 +2로 셌나? | pass | anthropic·openai·spacex-xai 가 받은 투자를 동맹 등급에서 뺀다. nvidia·amazon 의 +2 는 자기가 넣은 지분이다 |
| Q20 | 조달을 동맹으로 셌나? | pass | apple 의 Gemini, anthropic 의 컴퓨트, openai 의 Oracle·Broadcom 을 조달로 뺀다. tsmc 고객은 이번 수정으로 판매로 빠져 동맹 등급에 들지 않는다 |
| Q21 | 동맹이자 의존인 관계를 한쪽에서만 셌나, 또는 같은 속성을 양쪽에서 셌나? | pass | 1차 fail 사유(1260H 같은 속성을 ⑤·⑧ 에서 셈)가 해소됐다. palantir·oracle·microsoft 는 같은 관계를 ⑤ 동맹과 ⑧ 의존으로 속성을 나눠 센다 |
| Q22 | 지분 평가이익을 ⑦ 순환금융 증거로 셌나? | pass | amazon·alphabet·nvidia ⑦ 이 지분 평가이익을 ⑥ 소관으로 밝히고 입력에서 뺀다 |
| Q23 | 벤치마크를 서로 다른 하네스끼리 비교했나? | pass | alibaba ② 가 ARC Prize 표준 하네스 행(Qwen3.8-27B XHigh 42.4%)으로 회사 기준 1·2위와 비교하고, 모델 비교는 같은 날 Artificial Analysis 표와 ARC 표준 하네스로 한다. spacex-xai ③ 의 다른 판 지수 인용은 1차 L8 그대로다 |
결과는 pass / fail / not_applicable. not_applicable 도 근거가 필요하다.

## 발견 사항

- (파일·섹션 단위로 기록)

## 판정

- results_hash `b466a98c43bccef9…` · draft_hash `2ae12bf6ac545060…` 기준 검토. 자료·규칙·판단·초안이 바뀌면 이 리뷰는 무효다(D-10).
- **두 해시의 뜻이 다르다.** `results_hash` 는 `results.json` 에서 `results_hash` 키를 뺀 내용의 정렬 JSON 해시이고(`engine.sha256_obj`) **파일 바이트 sha256 과 다르다.** `draft_hash` 는 초안 **파일 바이트 sha256** 이다. 대조할 때 섞지 않는다.

## 리뷰 경위

1차 리뷰는 네 영역을 독립 세션에서 2026-10-09 에 수행했다(`review-parts/rule-consistency.md`·`fact-sources-a.md`·`fact-sources-b.md`·`financial-calc.md`·`output-readability.md`). needs_fix 6건과 체크리스트 fail 5건(Q01·Q02·Q03·Q09·Q21)을 한 묶음으로 고쳤다 — 판단 제안 27건, 근거 추가 1건(EV-meta-056)·발췌·인용 위치 수정, 트리거 24건, 기업 요약 14건, 렌더러 2건. 점수 변화는 NVIDIA ⑦ −1 → −2(총점 10 → 9, TSMC 와 공동 4위)와 Meta ④ 3 → 4(③ 미확인으로 순위 밖 그대로)뿐이다. 확인 리뷰(`review-parts/confirm-r2.md`)는 수정이 지시대로 들어갔고 1차 fail 이 모두 해소됐으며 점수·순위·체크리스트를 바꾸는 발견이 남지 않았다고 판정했다(pass). 확인 리뷰가 점수 무관으로 남긴 발견 가운데 리포트에 실리는 문장(판단 문구 3건, 기업 요약 9건의 함정 구성 서술, 트리거 조건·재검토 칸 12건, 요약 상자 표기, 테스트 회귀)은 조율자가 같은 날 고치고 research → calculate → draft 를 다시 돌린 뒤 초안 순위표·카드 머리·기업 요약 14건을 results 와 스크립트로 대조(오류 0)하고 낡은 표현 검색(0건)으로 확인했다. 그래서 이 파일의 해시는 확인 리뷰 파일의 해시보다 뒤의 것이다. 남은 점수 무관 발견(evidence_ids 미갱신 등)은 `confirm-r2.md` 「다음 실행 과제」에 있다.
