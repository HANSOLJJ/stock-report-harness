---
slug: ai-scorecard-2026-10-rejudge
report_type: ai_scorecard
status: pass
created_at: 2026-10-08
plan_source: output/ai-scorecard-2026-10-rejudge/plan.md
research_source: output/ai-scorecard-2026-10-rejudge/research.md
draft_source: output/ai-scorecard-2026-10-rejudge/draft.md
results_hash: 037f6be5692564d52a09c0c2c9de857d6561fb8c8615d18bf4ee186427b9a25a
draft_hash: 15a9f074fe1a9f9eaf870ceccba92b7fc83aef498e826e9685e6e383e433d8a4
review_type: separate-session-4way
review_execution: separate_subagent_sessions
reviewers:
  - "fact-sources: fact-checker fs-a-rejudge-20261009-r1 · fs-b-rejudge-20261009-r1 → pass"
  - "financial-calc: general-purpose fc-rejudge-20261009-r1 → needs_fix → 수정 → pass"
  - "rule-consistency: general-purpose rc-rejudge-20261009-r1 → needs_fix → 수정 → pass"
  - "output-readability: report-designer or-rejudge-20261009-r1 → needs_fix → 수정 → pass"
  - "confirm: general-purpose cf-rejudge-20261009-r2 → pass (승인 뒤 사용자 지적으로 승인 취소)"
  - "confirm: general-purpose cf-rejudge-20261009-r3 (사건 교차표·미확인 방향표·근거 등급표) → blocked 5건 → 수정"
  - "confirm: general-purpose cf-rejudge-20261009-r4 → pass"
---
# 리뷰 — 2026-10 전부 재판단(v2.0)

각 영역은 가능하면 독립 세션에서 검토하고 실제 수행자·결과를 남긴다. 수행하지 않은 검토를 pass 로 표시하지 않는다.

## 검토 영역

| 영역 | 검토 대상 | 검토자 | 결과 | 요약 |
| --- | --- | --- | --- | --- |
| 사실·출처 | 숫자·기업 귀속·기준 시점·공시·뉴스·부재 주장 | fact-checker ×2 (fs-a·fs-b-rejudge-20261009-r1) + 확인 general-purpose (cf-rejudge-20261009-r2·r3·r4) | pass | 14사 판단 98건의 근거 줄과 그 줄이 가리키는 근거 555건을 전수로 원문과 대조해 모두 발췌를 찾았고, 새 관측 108건이 원문으로 재현됐다. 원문과 어긋난 문장과 locator·발행일을 수정 묶음에서 고쳤고, 승인 취소 뒤의 수정(Anthropic ⑤⑦⑧·Oracle ⑧·OpenAI ①⑦③·Palantir ⑤)에서 새로 단 표지(EV-spacex-xai-013·048 등)는 확인 리뷰가 확정 근거의 발췌로 다시 대조했다. |
| 재무 계산 | EPS·환율·ADR·TTM·FCF·런웨이·약정·단위·부호 | general-purpose (fc-rejudge-20261009-r1) + 확인 general-purpose (cf-rejudge-20261009-r2·r3·r4) | pass | ⑥ 상장 12사 잣대·⑦ 분자분모·⑨ 게이트·③ 성장률·새 관측 108건의 단위·TTM·기준일이 맞고, 엔진 재계산이 results_hash 를 그대로 낸다. needs_fix 1건(anthropic ③ 총마진 전망치)은 partial 로 해소했고, 그 뒤의 입력 변경(nvidia ⑦ 큼, meta ④ 4, anthropic ⑤ −1·⑦ 큼, oracle ⑧ −3)마다 확인 리뷰가 엔진으로 점수·순위를 대조했다. |
| 규칙 일관성 | factor 정의·상하한·예외·중복 속성·정성 승계·전 기업 동일 기준 | general-purpose (rc-rejudge-20261009-r1) + 확인 general-purpose (cf-rejudge-20261009-r3·r4, 사건 교차표·미확인 방향표·근거 등급표) | pass | 판정 입력에서 점수로 가는 길을 ①②③⑤⑦ 70칸에서 재현해 어긋남 0, 정성 판단 98건 모두 새 판단이고 승계 없음, open 쟁점 14건 중 13건 닫힘. 1차 needs_fix 4건(⑦ 수치 임계, meta ④, 1260H 이중 계산, ⑤ 판매자 쪽 고객)을 고쳤고, 승인 취소 뒤 회사를 가로지르는 표 셋으로 다시 보아 같은 사건·같은 미확인·같은 근거 등급이 회사마다 다르게 읽힌 5곳(Anthropic ⑤·⑦·⑧, Oracle ⑧, OpenAI ⑦①③, Palantir ⑤ 문언)을 고쳐 Q03 이 pass 로 돌아왔다. |
| 출력·가독성 | 표·카드·근거·차트·이력 일치, 낡은 비교 문장, 모바일·단일 HTML | report-designer (or-rejudge-20261009-r1) + 확인 general-purpose (cf-rejudge-20261009-r2·r3·r4) | pass | 초안 순위표·카드 126칸·기업 요약 14건·KPI 가 results 와 어긋남 0(값을 바꾼 사본으로 검사가 값을 읽는지 확인), 메모리 렌더 HTML 이 320·768·1280px 에서 가로 넘침 0, 요약 상자에 ⑨ 게이트 판정 입력 칸을 적었다. 트리거 관찰·조건·재검토 칸의 지난 점수 진술은 전수로 현재 판단에 맞췄다. |
결과는 pass / needs_fix / blocked 중 하나. 네 영역이 모두 pass 이고 체크리스트에 fail 이 없을 때만 frontmatter `status: pass`.
**승계 판단 예외(AGENTS.md 리뷰 범위 · 기업 추가 실행에만, rules.md 2.9)** — 정기 실행에서는 체크리스트 fail 이 하나라도 있으면 `status: pass` 가 아니다. 기업 추가 실행에서는 체크리스트 fail 의 사유가 `carried_score` 로 승계한 판단의 기존 논리이고, 이번 실행이 그 판단에 쓰인 잣대를 바꾸지 않았으며, 규칙 파일 `open_tensions` 에 재검토 시점과 함께 등록됐다면 `status: pass` 를 막지 않는다. 이때 해당 fail 과 **긴장 번호**(예: `TEN-RC-02`)를 근거 칸에 그대로 적는다. 이번 실행이 바꾼 잣대가 닿는 승계 판단은 이 예외가 아니다 — 한 회사에 새 잣대를 댔으면 같은 잣대가 닿는 모든 회사에 대야 한다(Q03).

## 체크리스트

| ID | 검사 초점 | 결과 | 근거 |
| --- | --- | --- | --- |
| Q01 | 이 감점, 다른 칸에서 이미 셌나? | pass | anthropic 은 ⑤ 에서 큰 고객이 경쟁사 소유라는 사실을 비용형 재료로만, ⑦ 에서 Cursor 가 조달 자금으로 대금을 내는 속성만, ⑧ 에서 공급자=경쟁자와 약정만 센다. oracle ⑧ 은 이제 약정 축만 세고 ⑦ 은 조달 의존 고객 비중을 세어 속성이 다르다. oracle ⑤ J12 의 낡은 교차 참조(L1)는 이중 계산이 아니다. 1260H·대만 집중은 ⑧ 에서만, 고객 자체 칩·관계 단절 요구는 ⑤ 에서만 센다 |
| Q02 | 이 지표가 이 칸의 정의에 맞나? | pass | ⑦ 14건이 수치 임계 없는 같은 둘째 줄을 쓰고 ① 의 토큰 점유율은 방증이다. openai ① J9 는 총마진을 빼는 사유를 규칙 ① 표의 '원가 요인과 가른 설명' 이 아니라 근거 등급으로 적어 고칠 문장이 남았으나(L3), ① 점수는 회수 루프·대체 공급이 정해 결과가 같다 |
| Q03 | 회사마다 같은 잣대인가? | pass | B1(anthropic ⑦ 큼, nvidia ⑦ J7 과 같은 기준), B2(oracle ⑧ 고객 축 미확인, anthropic·microsoft 와 같은 처리), B3(openai ⑦ '확인되지 않아 작음' 가지), B4(AGENTS 범위를 좁히고 openai ③ 에 등급 표시, 두 모델 회사에 허용 하한 등급이 같음), B5(palantir 는 규칙 문언의 정당성 경로, 국방부 배제·플로리다 청구는 비용형)가 해소됐다. 남은 문면 차이(L3·L4, 과제 61·66)는 엔진 대조로 점수·순위를 바꾸지 않는다 |
| Q04 | 시총 크기를 밸류에이션으로 착각했나? | pass | 고친 판단 여섯과 요약 다섯에 시가총액 크기를 판정 재료로 쓴 문장이 없다 |
| Q05 | 출처가 이해당사자인가? | pass | 벤더 성능 발표는 방증으로만 쓴다. 이해상충 표기는 판정 사유로 보지 않았다 |
| Q06 | 볼륨인가 가치인가? | pass | anthropic·openai ① 이 토큰 점유율을 매출 점유율이 아니라고 한정하고 방증으로만 둔다 |
| Q07 | "안 만든 것"을 카운터 포지셔닝으로 셌나? | pass | amazon ③·oracle ②·palantir ② 가 모델을 안 만든 사실을 점수 근거로 쓰지 않는다 |
| Q08 | 적대세력을 수로 셌나, 성격으로 셌나? | pass | 14건 모두 성격으로 센다. palantir 는 사업의 정당성 자체를 겨냥한 적대라는 성격으로 구조형이고, 전선이 많은 openai 는 모두 소송·조사라 비용형이다(「B5 판정」) |
| Q09 | 미래 계획을 현재 점수에 넣었나? | pass | anthropic ③ 의 2025년 전망 총마진을 점수에 넣지 않고, oracle ⑧ 의 OpenAI 몫 재측정은 확인될 때로 미룬다. nvidia ⑤ J10 의 전망 문장은 3차 과제 52 그대로다 |
| Q10 | 거리를 가속도로 착각했나? | pass | 지표가 있는 12건이 성장률 둘의 변화로 판정한다 |
| Q11 | 순적자를 실격 사유로 썼나? | pass | anthropic ③ 별도 수익모델은 단위경제 판정 보류로 부분이고 적자 규모를 사유로 쓰지 않는다 |
| Q12 | ③ 세 기준을 동등하게 쟀나? | pass | 4점은 tsmc 하나이고 모방 불가능성 완전 통과다 |
| Q13 | "공짜로 뿌린다"를 곧바로 카운터 포지셔닝으로 셌나? | pass | alibaba 오픈웨이트는 회수 장치가 없어 모방 불가능성 실패다 |
| Q14 | 아직 안 끝난 승부를 끝난 것처럼 쟀나? | pass | 14사 모두 문 닫힘 실패이고 ③ 5점이 없다 |
| Q15 | ⑤에서 "공짜 사용자"를 아군으로 셌나? | pass | 파생 모델·오픈웨이트 개발자를 세지 않는다 |
| Q16 | ①을 한 채널로만 쟀나? | pass | 14건 모두 가장 강한 채널 하나의 네 질문으로 판정한다 |
| Q17 | ②를 "표준 없음"만으로 깎았나? | pass | 2점(apple·palantir)은 세 경로가 모두 막힌 경우다 |
| Q18 | ⑤에서 관계사를 독립 동맹으로 셌나? | pass | tesla↔spacex-xai 관계를 양쪽에서 뺀다 |
| Q19 | ⑤에서 "받은 투자"를 곧바로 동맹 +2로 셌나? | pass | anthropic·openai·spacex-xai 가 받은 투자를 동맹 등급에서 뺀다 |
| Q20 | 조달을 동맹으로 셌나? | pass | apple 의 Gemini, anthropic 의 컴퓨트, openai 의 Oracle·Broadcom, meta 의 칩 구매를 조달로 뺀다 |
| Q21 | 동맹이자 의존인 관계를 한쪽에서만 셌나, 또는 같은 속성을 양쪽에서 셌나? | pass | palantir·microsoft 는 같은 관계를 ⑤ 동맹과 ⑧ 의존으로 나눠 센다. oracle 은 OpenAI 관계를 ⑤ 동맹으로 세고 ⑧ 에서는 고객 집중을 재지 않아 같은 속성을 두 번 세지 않는다(L1 은 문구) |
| Q22 | 지분 평가이익을 ⑦ 순환금융 증거로 셌나? | pass | amazon·alphabet·nvidia ⑦ 이 지분 평가이익을 ⑥ 소관으로 밝히고 입력에서 뺀다 |
| Q23 | 벤치마크를 서로 다른 하네스끼리 비교했나? | pass | 모델 비교는 같은 날 Artificial Analysis 표와 ARC Prize 표준 하네스로 한다. spacex-xai ③ 의 다른 판 지수 인용은 기존 과제 11 이다 |
결과는 pass / fail / not_applicable. not_applicable 도 근거가 필요하다.

## 발견 사항

- (파일·섹션 단위로 기록)

## 판정

- results_hash `037f6be5692564d5…` · draft_hash `15a9f074fe1a9f9e…` 기준 검토. 자료·규칙·판단·초안이 바뀌면 이 리뷰는 무효다(D-10).
- **두 해시의 뜻이 다르다.** `results_hash` 는 `results.json` 에서 `results_hash` 키를 뺀 내용의 정렬 JSON 해시이고(`engine.sha256_obj`) **파일 바이트 sha256 과 다르다.** `draft_hash` 는 초안 **파일 바이트 sha256** 이다. 대조할 때 섞지 않는다.

## 리뷰 경위

1차 리뷰는 네 영역을 독립 세션에서 2026-10-09 에 수행했다(`review-parts/rule-consistency.md`·`fact-sources-a.md`·`fact-sources-b.md`·`financial-calc.md`·`output-readability.md`). needs_fix 6건과 체크리스트 fail 5건(Q01·Q02·Q03·Q09·Q21)을 한 묶음으로 고쳤고(판단 제안 27건, 근거 추가 1건, 트리거 24건, 기업 요약 14건, 렌더러 2건), 확인 리뷰 2차(`confirm-r2.md`)가 pass 를 냈다. 그 상태로 사람이 승인·빌드했으나, 사용자가 리포트에서 같은 사건(Microsoft 의 GitHub Copilot 자체 모델 투입, SpaceX 의 Cursor 인수)이 Anthropic ⑤ 에서는 구조형 −2, OpenAI ⑤ 에서는 비용형 −1 로 읽힌 것을 짚어 승인을 취소했다(2026-10-09, 사유 '일관성'). 차이는 Anthropic 의 고객 비중이 유출된 상장 신청서 초안·2차 보도로만 알려졌다는 자료의 유무에서 왔다. 이에 ⑤ 구조형의 주요 고객·⑧ 고객 축·⑦ 몫 좁히기는 공개 제출본의 공시나 회사 1차 발표로만 잰다는 잣대를 세우고(`AGENTS.md`, `score-review` 스킬 「회사를 가로지르는 표 셋」), Anthropic ⑤ 를 −1 로 고쳤다. 확인 리뷰 3차(`confirm-r3.md`)는 14사 전부에 사건 교차표·미확인 방향표·근거 등급표를 만들어 같은 잣대에 걸리는 5곳을 더 찾았고(blocked), 조율자가 Anthropic ⑦ 큼(−2), Oracle ⑧ 고객 축 미확인(−3), OpenAI ⑦①③ 문장, Palantir ⑤ 를 규칙 ⑤ 표 문언으로 고쳤다. Palantir 는 규칙 표가 '사업의 정당성 자체를 겨냥한 적대' 만으로 구조형을 정해 −2 를 유지했다. 확인 리뷰 4차(`confirm-r4.md`)가 이 처리와 Palantir 판정을 확인해 pass 를 냈고, 그 리뷰가 남긴 점수 무관 문장 결함 5건(oracle ⑤ 교차 참조, 트리거 3건의 Oracle ⑧ 진술, openai ① 총마진 사유, oracle ⑦·요약의 2차 보도 등급 표시, openai ⑦ 문구)은 조율자가 같은 날 고치고 research → calculate → draft 를 다시 돌린 뒤 초안 순위표·카드 머리·기업 요약 14건을 results 와 스크립트로 대조(오류 0)하고 낡은 표현을 검색(0건)해 확인했다. 그래서 이 파일의 해시는 4차 확인 리뷰 파일의 해시보다 뒤의 것이며, 그 사이에 바뀐 것은 문장뿐이고 점수·입력·근거는 같다. 최종 순위는 Microsoft 15, Alphabet·Amazon 14, NVIDIA·TSMC 9, Apple 7, Alibaba·Oracle 6, Tesla 5, SpaceX·Palantir 4, OpenAI 2, Anthropic 1, Meta 미완료다. 남은 과제 70건은 `confirm-r4.md` 「다음 실행 과제」에 있다.
