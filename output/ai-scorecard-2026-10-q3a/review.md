---
slug: ai-scorecard-2026-10-q3a
report_type: ai_scorecard
status: pass
created_at: 2026-10-23
plan_source: output/ai-scorecard-2026-10-q3a/plan.md
research_source: output/ai-scorecard-2026-10-q3a/research.md
draft_source: output/ai-scorecard-2026-10-q3a/draft.md
results_hash: 5dc69c33544c686ef9e9097f1ea68beaf8a3781dc6aac1feff1fa2a2c18eb637
draft_hash: 711fd46db1ecc0a5ed497cb0399366f6910cfd2c3b14fbc08d4d02d06cfc87c1
review_type: separate-session-4way
review_execution: separate_subagent_sessions
reviewers:
  - "fact-sources: fact-checker (claude-sonnet-5-5) → pass after fix batch, confirm review (Opus) pass"
  - "financial-calc: separate session (claude-sonnet-5-5) pass"
  - "rule-consistency: separate session (Claude Opus 5.5, high) → pass after fix batch, confirm review pass"
  - "output-readability: report-designer (claude-sonnet-5-5) → pass after fix batch, confirm review pass"
---
# 리뷰 — 2026년 3분기 실적 반영 (1차)

각 영역은 가능하면 독립 세션에서 검토하고 실제 수행자·결과를 남긴다. 수행하지 않은 검토를 pass 로 표시하지 않는다.

## 검토 영역

| 영역 | 검토 대상 | 검토자 | 결과 | 요약 |
| --- | --- | --- | --- | --- |
| 사실·출처 | 숫자·기업 귀속·기준 시점·공시·뉴스·부재 주장 | fact-checker(claude-sonnet-5-5, 별도 세션) + 확인 리뷰(Opus) | pass | 1차 needs_fix(⑤ Unity 운영 여부, Meta–Apple Muse Spark, DMV·DSA 구제 조치) → 수정 뒤 확인 리뷰에서 닫힘. 새 근거 142건 원문 대조·가격 24건·TTM 성분 accession 일치. review-parts/facts.md·confirm.md |
| 재무 계산 | EPS·환율·ADR·TTM·FCF·런웨이·약정·단위·부호 | 별도 세션(claude-sonnet-5-5) | pass | 새 관측 TTM 복원·환율 31.37·⑥⑨ 재계산 일치, 10-22 가격·시가총액 일치. ⑨ 문장 어긋남은 수정 묶음에서 닫힘. review-parts/finance.md |
| 규칙 일관성 | factor 정의·상하한·예외·중복 속성·정성 승계·전 기업 동일 기준 | 별도 세션(Claude Opus 5.5, high) + 확인 리뷰 | pass | 1차 needs_fix(갱신 회사 ⑨ 미재판단, TSMC 판정 대기 문장) → 닫힘. 사건 교차표·미확인 방향표·근거 등급표 모두 일치, 같은 층 경쟁사 잣대 비교 통과. review-parts/rules.md·confirm.md |
| 출력·가독성 | 표·카드·근거·차트·이력 일치, 낡은 비교 문장, 모바일·단일 HTML | report-designer(claude-sonnet-5-5) + 확인 리뷰 | pass | 순위표·카드 머리·반영 기준일 일치, 낡은 표기 없음. ⑨ 문장 어긋남 닫힘. HTML 은 확인 뒤 빌드 때 --require-html 로 본다. review-parts/output.md·confirm.md |

결과는 pass / needs_fix / blocked 중 하나. 네 영역이 모두 pass 이고 체크리스트에 fail 이 없을 때만 frontmatter `status: pass`.
**승계 판단 예외(AGENTS.md 리뷰 범위 · 기업 추가 실행에만, rules.md 2.9)** — 정기 실행에서는 체크리스트 fail 이 하나라도 있으면 `status: pass` 가 아니다. 기업 추가 실행에서는 체크리스트 fail 의 사유가 `carried_score` 로 승계한 판단의 기존 논리이고, 이번 실행이 그 판단에 쓰인 잣대를 바꾸지 않았으며, 규칙 파일 `open_tensions` 에 재검토 시점과 함께 등록됐다면 `status: pass` 를 막지 않는다. 이때 해당 fail 과 **긴장 번호**(예: `TEN-RC-02`)를 근거 칸에 그대로 적는다. 이번 실행이 바꾼 잣대가 닿는 승계 판단은 이 예외가 아니다 — 한 회사에 새 잣대를 댔으면 같은 잣대가 닿는 모든 회사에 대야 한다(Q03).

## 체크리스트

| ID | 검사 초점 | 결과 | 근거 |
| --- | --- | --- | --- |
| Q01 | 이 감점, 다른 칸에서 이미 셌나? | pass | Tesla 의 SpaceX 지분은 ⑤ 에서 관계사로 빼고 ⑦ 에서 환류로 센다. 공급자가 곧 경쟁자인 위험은 ⑧ 에서만 센다. ⑥ 은 가격 배수, ⑨ 는 영업손익·FCF·런웨이로 입력이 겹치지 않는다. SpaceX–Anthropic 계약은 ⑦ 조달 의존 몫과 ⑧ 고객 집중으로 속성을 나눠 적었다(사실·재무·규칙) |
| Q02 | 이 지표가 이 칸의 정의에 맞나? | pass | ① D·E 는 정의표 시장으로, ③ 가속도는 AI 귀속 지표(Tesla 활성 FSD 구독, TSMC HPC 대리 지표 c)로 쟀고 Starlink 가입자는 층 밖 사업 ② 의 채택 지표로만 쓴다. TSMC ③ 을 b 단계가 아니라 c 단계로 둔 이유가 판정 칸에 있다(규칙) |
| Q03 | 회사마다 같은 잣대인가? | pass | 사건 교차표·미확인 방향표·근거 등급표·같은 층 경쟁사 교차표에서 자료의 유무로 갈린 줄이 없다(규칙). 수정 뒤에도 Meta–Apple Muse Spark Open 은 두 회사에 같은 이유로 동맹 아님, DMV·DSA 구제 조치는 Apple·Meta·Alphabet·Amazon 의 같은 성격 전선과 같은 잣대(명령을 따르며 다투면 진행 중)다. Meta 평가손익 미조정(재무 F-07)은 부등식으로 점수 불변을 확인했다 |
| Q04 | 시총 크기를 밸류에이션으로 착각했나? | pass | 시총은 PER·EV/매출의 분자로만 쓰였고 14개사 가격·시총이 10-22 종가·벤더 시총으로 맞다(사실·재무·규칙) |
| Q05 | 출처가 이해당사자인가? | pass | 결과 칸만 채운다(표기 점검 제외, AGENTS.md). 회사 발표·CEO 발언에는 근거 등급이 붙어 있고 유출 초안은 등급을 가르는 수치로 쓰이지 않았다(사실) |
| Q06 | 볼륨인가 가치인가? | pass | Starlink 가입자는 회선 수, ARPU 는 소비자 서비스 매출, TSMC 3분기 플랫폼 값은 비중·성장률 범위로 구분되고, 소셜 유입 점유율은 간접 자료 50% 로 썼다(사실·규칙) |
| Q07 | "안 만든 것"을 카운터 포지셔닝으로 셌나? | pass | TSMC 의 고객과 경쟁하지 않는 전용 파운드리 구조를 ③ 으로 세지 않았다(규칙, 수정 뒤 `tsmc.F3.foundry` 에서 다시 확인) |
| Q08 | 적대세력을 수로 셌나, 성격으로 셌나? | pass | Tesla 열 전선·Meta 열셋 전선은 성격(비용형)·관할·구제 조치로 띠를 정했다. Tesla ⑤ 의 변화(7→6)도 전선 수가 아니라 구제 조치 판정에서 왔다 |
| Q09 | 미래 계획을 현재 점수에 넣었나? | pass | Unity Spark(연내 출시 예정), Apple Home Collection(12월 판매), Terafab, 설비투자 전망, N2 용량 계획, A14 일정은 "계획이라 점수에 넣지 않는다"로 처리됐다. 트리거에 미래 점수가 없다(재무·규칙·출력) |
| Q10 | 거리를 가속도로 착각했나? | pass | ③ 가속도는 두 기간 배수의 비(Tesla 1.074, SpaceX 클라우드 2.77 → c 상한, TSMC 1.22)다(규칙, TSMC 비는 다시 계산해 확인) |
| Q11 | 순적자를 실격 사유로 썼나? | pass | SpaceX ⑨ 는 TTM 영업손실률로 게이트 1 을 걸었고 순손실은 쓰지 않았으며, 3분기 단일 분기 흑자로 TTM 적자를 지우지 않았다(재무·규칙) |
| Q12 | ③ 세 기준을 동등하게 쟀나? | pass | 범위 안 ③ 층 점수 최고는 6.4 이고 관문이 걸린 층은 관문대로 적었다(규칙) |
| Q13 | "공짜로 뿌린다"를 곧바로 카운터 포지셔닝으로 셌나? | pass | Muse Spark Open 은 회수 장치가 없어 세지 않았고 Grok 무료 등급은 회수 장치가 있어 4 다(규칙) |
| Q14 | 아직 안 끝난 승부를 끝난 것처럼 쟀나? | pass | 문 닫힘 증거로 20 을 받은 층이 없다(규칙) |
| Q15 | ⑤에서 "공짜 사용자"를 아군으로 셌나? | pass | 공개 가중치를 받는 개발자, Grok 파트너 네트워크 참여사, Muse Spark Open 을 Mac 에서 돌리는 쪽을 동맹으로 세지 않았다(규칙, 수정 뒤 Meta·Apple ⑤ 에서 다시 확인) |
| Q16 | ①을 사업마다, ②③을 층마다 나눠 쟀나? | pass | 매출 줄을 가장 잘게 나눈 공시 표에 통째로 붙였고 TSMC 는 금액이 공시된 최근 4개 분기 줄을 쓴다(규칙 2.10, 사용자 결정) |
| Q17 | ②를 "표준 없음"만으로 깎았나? | pass | 표준 0 인 층도 적응 경로로 매겼다(규칙) |
| Q18 | ⑤에서 관계사를 독립 동맹으로 셌나? | pass | Tesla–SpaceX 거래·지분·Grok·Terafab·결합 검토 특별위원회를 양쪽 모두 관계사로 빼고 동맹으로 세지 않았다(규칙) |
| Q19 | ⑤에서 "받은 투자"를 곧바로 지분 동맹으로 셌나? | pass | SpaceX 가 받은 Alphabet·Tesla 지분, TSMC 의 JASM·ESMC 소수 지분은 지분 동맹에서 뺐다(규칙) |
| Q20 | 조달을 동맹으로 셌나? | pass | Samsung·Intel 위탁 제조, Samsung Electro-Mechanics, OCI 용량, Apple 쪽 Gemini 구매, Google 의 SpaceX 컴퓨트 구매를 조달로 읽었다(규칙) |
| Q21 | 동맹이자 의존인 관계를 한쪽에서만 셌나, 또는 같은 속성을 양쪽에서 셌나? | pass | SpaceX–Anthropic 계약은 SpaceX ⑧ 고객 축과 Anthropic ⑧ 약정·공급 축에서 방향대로 한 번씩 센다. Alphabet–Apple 제휴는 Alphabet ⑤ 상업 동맹, Apple ⑧ 공급 축으로 방향에 따라 다르게 센다(규칙, 수정 뒤 Apple ⑤ 문장에서 다시 확인) |
| Q22 | 지분 평가이익을 ⑦ 순환금융 증거로 셌나? | pass | Tesla ⑦ 의 SpaceX 지분 공정가치는 방증으로만 적고 입력은 실행된 투자 사실이다. 평가이익은 ⑥ P1 조정에서만 쓰였다(규칙·재무) |
| Q23 | 벤치마크를 서로 다른 하네스끼리 비교했나? | pass | TSMC ② 밀도 비교는 독립 분석(SemiAnalysis) 하나이고 Tesla AI5 성능 발언은 쓰지 않았다(규칙) |
| Q24 | 끝난 싸움을 ② 표준 선점·③·⑤ 적대에 셌나? | pass | Marlin ITC 종료·IF Metall 쟁의 종료·X 의 Apple 청구 취하는 세지 않았다. DMV 사건은 Tesla 의 결정 취소 소송이 끝났다는 근거가 없어 진행 중으로 두었다(C-5 에 위험을 적었다) |
| Q25 | 매출 몫이 없는 층의 강점을 옮겨 셀 때 원칙을 지켰나? | pass | Grok·Muse 모델 순위와 AI5 성능을 사용자 플랫폼·기기 층의 도약으로 옮기지 않았다(규칙) |

결과는 pass / fail / not_applicable. not_applicable 도 근거가 필요하다.

## 발견 사항

- 1차 리뷰 발견과 수정(한 묶음): 갱신 회사 넷의 ⑨ 판단을 9월 분기 숫자로 다시 매김(범위 검사가 ⑥⑨ 를 건너뛰던 코드 수정 b18e75c) · TSMC ①②③④ 아홉 건의 '판정 대기' 문장을 6월 분기 줄 금액 유지(규칙 2.10, 2026-10-23 사용자 결정)로 고침 · ⑤ 다섯 건(Alphabet Unity 운영 중으로 읽되 동맹 아님, Meta·Apple Muse Spark 협업은 같은 이유로 동맹 아님 — Apple ⑤ 는 scope --add 로 범위에 넣음, Tesla DMV 구제 조치 진행 중 yes 로 ⑤ 7→6, SpaceX DSA 시정 진행 중) · 새 근거 5건 확정 · 14개사 가격을 10-22 종가·벤더 시가총액으로 다시 받음.
- 확인 리뷰(review-parts/confirm.md) 결과 pass. 점수·순위·체크리스트 판정을 바꾸는 발견 없음. 낮은 심각도 C-1~C-9 와 네 영역의 다음 실행 과제 33건은 confirm.md 「다음 실행 과제」에 있다(openai ⑦ 문장, TSMC P1 세금 창 짝, SpaceX 현금 정의·완충 잠식 C-06, DMV 구제 조치 '끝남' 읽기, 개요의 범위 항목 문장, EV-alphabet-072 옛 척도 문장, 발췌 형식 등).
- diff(ai-scorecard-2026-10-v30full 대비) 1층·2층 통과: 범위 밖은 ⑥(가격)만 움직였다. 갱신 범위: 갱신 회사 spacex-xai·meta·tesla·tsmc 전부 + alphabet ⑤⑧·anthropic ⑤⑦⑧·apple ⑤(선언)⑧·nvidia ⑧.

## 판정

- results_hash `5dc69c33544c686e…` · draft_hash `711fd46db1ecc0a5…` 기준 검토. 자료·규칙·판단·초안이 바뀌면 이 리뷰는 무효다(D-10).
- **두 해시의 뜻이 다르다.** `results_hash` 는 `results.json` 에서 `results_hash` 키를 뺀 내용의 정렬 JSON 해시이고(`engine.sha256_obj`) **파일 바이트 sha256 과 다르다.** `draft_hash` 는 초안 **파일 바이트 sha256** 이다. 대조할 때 섞지 않는다.
