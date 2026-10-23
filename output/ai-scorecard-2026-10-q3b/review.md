---
slug: ai-scorecard-2026-10-q3b
report_type: ai_scorecard
status: pass
created_at: 2026-10-23
plan_source: output/ai-scorecard-2026-10-q3b/plan.md
research_source: output/ai-scorecard-2026-10-q3b/research.md
draft_source: output/ai-scorecard-2026-10-q3b/draft.md
results_hash: 7a150813fbb1d0f9a2756c147764ff804ffc02ab80bc456139407dfea3d89294
draft_hash: 6f2db50f5972fc7cb0b3b8bab6812f1ceb3300835e9af23efd4039363599a3a0
review_type: separate-session-4way
review_execution: separate_subagent_sessions
reviewers:
  - "fact-sources: fact-checker (claude-sonnet-5-5) → pass after fix batch, confirm review (Opus) pass"
  - "financial-calc: separate session (claude-sonnet-5-5) pass"
  - "rule-consistency: separate session (Claude Opus 5.5, high) → pass after fix batch, confirm review pass"
  - "output-readability: report-designer (claude-sonnet-5-5) → pass after fix batch, confirm review pass"
---
# 리뷰 — 2026년 3분기 실적 반영 (2차) — ⑤ 받은 투자 규칙

각 영역은 가능하면 독립 세션에서 검토하고 실제 수행자·결과를 남긴다. 수행하지 않은 검토를 pass 로 표시하지 않는다.

## 검토 영역

| 영역 | 검토 대상 | 검토자 | 결과 | 요약 |
| --- | --- | --- | --- | --- |
| 사실·출처 | 숫자·기업 귀속·기준 시점·공시·뉴스·부재 주장 | fact-checker(claude-sonnet-5-5, 별도 세션) + 확인 리뷰(Opus) | pass | 1차 needs_fix(OpenAI ⑤ Microsoft 헤지 읽기) → 수정 뒤 확인 리뷰에서 닫힘. 새 근거 16+1+3건 원문 대조, 트리거 29건 확인 전수. review-parts/facts.md·confirm.md |
| 재무 계산 | EPS·환율·ADR·TTM·FCF·런웨이·약정·단위·부호 | 별도 세션(claude-sonnet-5-5) | pass | Anthropic ⑤ 7·OpenAI ⑤·TSMC ⑤ 계산 경로 일치, 관측 변화 없음(가격은 10-22 종가 그대로). TRG-163 문장 어긋남은 수정 묶음에서 닫힘. review-parts/finance.md |
| 규칙 일관성 | factor 정의·상하한·예외·중복 속성·정성 승계·전 기업 동일 기준 | 별도 세션(Claude Opus 5.5, high) + 확인 리뷰 | pass | 1차 needs_fix(OpenAI ⑤ 넓은 읽기 잔재, Microsoft–OpenAI 긴장 불일치, TSMC·SpaceX ⑤ 옛 문장) → scope --add 와 재판단으로 닫힘. 합작법인 원칙 통일, 투자자별 교차표 일치. review-parts/rules.md·confirm.md |
| 출력·가독성 | 표·카드·근거·차트·이력 일치, 낡은 비교 문장, 모바일·단일 HTML | report-designer(claude-sonnet-5-5) + 확인 리뷰 | pass | 순위표·카드·반영 기준일 일치. 개요 문구(실적 단정, 가격 새로 받음)는 렌더러 수정으로 닫힘. HTML 은 확인 뒤 --require-html 로 본다. review-parts/output.md·confirm.md |

결과는 pass / needs_fix / blocked 중 하나. 네 영역이 모두 pass 이고 체크리스트에 fail 이 없을 때만 frontmatter `status: pass`.
**승계 판단 예외(AGENTS.md 리뷰 범위 · 기업 추가 실행에만, rules.md 2.9)** — 정기 실행에서는 체크리스트 fail 이 하나라도 있으면 `status: pass` 가 아니다. 기업 추가 실행에서는 체크리스트 fail 의 사유가 `carried_score` 로 승계한 판단의 기존 논리이고, 이번 실행이 그 판단에 쓰인 잣대를 바꾸지 않았으며, 규칙 파일 `open_tensions` 에 재검토 시점과 함께 등록됐다면 `status: pass` 를 막지 않는다. 이때 해당 fail 과 **긴장 번호**(예: `TEN-RC-02`)를 근거 칸에 그대로 적는다. 이번 실행이 바꾼 잣대가 닿는 승계 판단은 이 예외가 아니다 — 한 회사에 새 잣대를 댔으면 같은 잣대가 닿는 모든 회사에 대야 한다(Q03).

## 체크리스트

| ID | 검사 초점 | 결과 | 근거 |
| --- | --- | --- | --- |
| Q01 | 이 감점, 다른 칸에서 이미 셌나? | pass | Anthropic·OpenAI 의 공급자 경쟁 위험은 ⑧ 공급 축에서만 센다. 국방부 지정은 ⑤ 에서만 센다. TSMC 는 관세를 ⑤ 비용형으로, 대만 집중·장비 의존을 ⑧ 에서 센다. 같은 감점을 두 칸에서 세지 않았다 |
| Q02 | 이 지표가 이 칸의 정의에 맞나? | pass | 받은 투자는 규칙의 묶임 증거 셋(독점·우선, 주력 편입, 조건부 추가 출자)으로만 셌다. TSMC 지분 동맹은 관계기업·보유 지분이라 칸 정의(맺은 출자)에 맞다. 금액은 어느 계산에도 들어가지 않았다(`amounts_used: false`) |
| Q03 | 회사마다 같은 잣대인가? | pass | 갱신 범위 안의 어긋남 셋이 닫혔다. 첫째, Copilot 의 Claude·OpenAI 병행을 두 회사 모두 '나란히 올림'으로 읽는다. 둘째, Microsoft–OpenAI 긴장을 두 회사 모두 '있음'으로 읽는다. 셋째, 받은 투자 규칙을 SpaceX·TSMC 에도 댔고 합작법인 원칙이 OpenAI·Oracle·TSMC 에서 같다. 범위 밖에서 이어받은 Palantir·NVIDIA 의 맺은 출자 읽기는 C-1 에 적었다(Palantir 는 순위에 닿을 수 있음) |
| Q04 | 시총 크기를 밸류에이션으로 착각했나? | pass | ⑥ 는 14개사 모두 q3a 와 점수가 같다(가격은 사용자 결정으로 10-22 종가를 이어받음). 상장사 ⑥ 는 성장 조정 PER·EV/매출·성장으로 재고, 시총 크기를 점수에 쓰지 않는다. 비상장 두 곳은 포스트머니 ÷ 런레이트다 |
| Q05 | 출처가 이해당사자인가? | pass | 출처 이해관계는 결과 칸만 채운다. 표기 누락을 판정 사유로 삼지 않았다 |
| Q06 | 볼륨인가 가치인가? | not_applicable | 두 갱신 회사 ① 의 판정 재료는 q3a 와 같다. 이번 수정은 ⑤ 에 한정된다 |
| Q07 | "안 만든 것"을 카운터 포지셔닝으로 셌나? | not_applicable | ③ 재료 불변. '안 만든 것'을 ③ 으로 세지 않은 판정은 이어받았다 |
| Q08 | 적대세력을 수로 셌나, 성격으로 셌나? | pass | 적대를 성격으로 센다. Anthropic 의 Reservoir 전선을 더해도 관할 수(미국·EU)만 보고 띠를 올리지 않았다. OpenAI 비용형 열다섯도 관할 셋으로만 더 깎는다 |
| Q09 | 미래 계획을 현재 점수에 넣었나? | pass | Sony 이미지 센서 합작(종결 전), Terafab, Synopsys 공동 개발, Workday 연동, UAE 라운드는 점수에 넣지 않았다. Google·Amazon 조건부 약정은 지금 맺어진 약정이다 |
| Q10 | 거리를 가속도로 착각했나? | not_applicable | ③ 가속도 재료 불변 |
| Q11 | 순적자를 실격 사유로 썼나? | pass | 두 비상장사 ⑨ 는 G1 판정 보류·G2 비상장 미공시 −8 이고 적자를 실격 사유로 쓰지 않았다 |
| Q12 | ③ 세 기준을 동등하게 쟀나? | pass | 갱신 회사 ③ 은 0·8 이라 모방 불가능성 8 관문에 닿지 않는다 |
| Q13 | "공짜로 뿌린다"를 곧바로 카운터 포지셔닝으로 셌나? | pass | OpenAI ③ 의 무료·Go 요금제는 광고 회수 장치와 함께 셌다(재료 불변) |
| Q14 | 아직 안 끝난 승부를 끝난 것처럼 쟀나? | pass | 두 회사 ②③ 어느 층도 20 이 아니고 문 닫힘 날짜가 없다 |
| Q15 | ⑤에서 "공짜 사용자"를 아군으로 셌나? | pass | 오픈웨이트·개발자 수·Grok 파트너 네트워크 참여 수를 ⑤ 동맹으로 세지 않았다 |
| Q16 | ①을 사업마다, ②③을 층마다 나눠 쟀나? | not_applicable | 두 갱신 회사는 사업 하나·판매 층 하나이고 재료 불변이다 |
| Q17 | ②를 "표준 없음"만으로 깎았나? | not_applicable | ② 표준 재료 불변 |
| Q18 | ⑤에서 관계사를 독립 동맹으로 셌나? | pass | Tesla–SpaceX 는 양쪽 모두 관계사로 뺐다. TSMC 가 지배하는 JASM·ESMC 는 관계사라 동맹이 아니다. SSMC·GUC·Xintec·VIS 는 TSMC 가 연결하지 않는 회사다 |
| Q19 | ⑤에서 "받은 투자"를 곧바로 지분 동맹으로 셌나? | pass | 받은 투자를 곧바로 세지 않았다. Anthropic 의 Amazon·Google 은 묶임 증거가 원문으로 확인돼 셌다. OpenAI 의 Microsoft·Amazon·NVIDIA, TSMC 의 JASM·ESMC 소수 주주 여섯 곳, SpaceX 의 Alphabet·NVIDIA 는 묶임 증거가 없어 뺐다. Amazon·Google 은 지분 동맹 한 부분에만 넣었다 |
| Q20 | 조달을 동맹으로 셌나? | pass | GlobalFoundries 인터포저, 웨이퍼 매매, 두 모델사의 클라우드·칩 구매, AMD 워런트·CoreWeave 주식은 조달로 뺐다. 범위 밖 Apple 의 Globalstar SPE 지분 읽기는 C-2 에 적었다 |
| Q21 | 동맹이자 의존인 관계를 한쪽에서만 셌나, 또는 같은 속성을 양쪽에서 셌나? | pass | 받은 투자(Anthropic ⑤, 투자자가 떠나기 어려움)와 맺은 출자(Amazon·Alphabet ⑤, Anthropic 이 떠나기 어려움)는 방향이 다른 속성이고, 회사 안의 ⑤ 와 ⑧ 은 규칙이 허용한 짝이다. TSMC 의 지분 동맹 상대와 상업 동맹 상대는 겹치지 않는다 |
| Q22 | 지분 평가이익을 ⑦ 순환금융 증거로 셌나? | pass | Microsoft 의 Anthropic 평가이익, TSMC 의 VIS 처분 이익은 ⑦ 입력이 아니다 |
| Q23 | 벤치마크를 서로 다른 하네스끼리 비교했나? | not_applicable | ② 성능 도약 재료 불변 |
| Q24 | 끝난 싸움을 ② 표준 선점·③·⑤ 적대에 셌나? | pass | Marlin ITC 조사(2026-08-06 종료)와 Anthropic 작가 집단소송 합의는 세지 않았다. X.AI 영업비밀 항소·Musk v. Altman 은 진행 중으로 셌다 |
| Q25 | 매출 몫이 없는 층의 강점을 옮겨 셀 때 원칙을 지켰나? | not_applicable | 두 갱신 회사는 판매 층이 하나이고, TSMC 도 반도체 제조 한 층이라 다른 층으로 옮겨 센 강점이 없다 |

결과는 pass / fail / not_applicable. not_applicable 도 근거가 필요하다.

## 발견 사항

- 실행 이유: ⑤ 받은 투자 절충안과 좁은 헤지 읽기(2026-10-23 사용자 결정, rules.md ⑤). 갱신 회사 anthropic·openai 전 항목 재판단, scope --add 로 tsmc·spacex-xai ⑤ 추가.
- 1차 리뷰 발견과 수정(한 묶음): OpenAI ⑤ 를 좁은 읽기로 다시 씀(Microsoft 는 주력 편입의 '바꾸기 어려움'이 1차 근거로 서지 않아 제외, 긴장 '있음'을 Microsoft 쪽과 맞춤, 6→5) · TSMC ⑤ 에 빠져 있던 관계기업 지분(SSMC·GUC·Xintec·VIS, 새 근거 EV-tsmc-130~132)을 맺은 출자로 세어 12→15 · 합작법인 원칙 통일(지배하면 관계사, 아니면 맺은 출자) · SpaceX ⑤ 문장 갱신(5 그대로) · TRG-163, EV-anthropic-172·165·169, EV-tsmc-102 문장 · 개요 렌더러 문구 · 가격 기준일을 10-22(이어받은 종가)로 두고 가정에 기록.
- 확인 리뷰(review-parts/confirm.md) pass. 점수·순위·체크리스트 판정을 바꾸는 발견 없음. 범위 밖 판단 가운데 다시 매기면 순위가 바뀔 수 있는 것 둘(Palantir ⑤ 지분증권 보유 → 8위 가능, Apple ⑤ Globalstar SPE 20% → 5·6위 교체 가능)은 사람이 확인 전에 알고 정한다(C-1·C-2). 다음 실행 과제 16건은 confirm.md 에 있다.
- diff(ai-scorecard-2026-10-q3a 대비) 통과: 범위 안 변화 Anthropic ⑤ 4→7, OpenAI ⑤ 6→5, TSMC ⑤ 12→15, 나머지 불변.

## 판정

- results_hash `7a150813fbb1d0f9…` · draft_hash `6f2db50f5972fc7c…` 기준 검토. 자료·규칙·판단·초안이 바뀌면 이 리뷰는 무효다(D-10).
- **두 해시의 뜻이 다르다.** `results_hash` 는 `results.json` 에서 `results_hash` 키를 뺀 내용의 정렬 JSON 해시이고(`engine.sha256_obj`) **파일 바이트 sha256 과 다르다.** `draft_hash` 는 초안 **파일 바이트 sha256** 이다. 대조할 때 섞지 않는다.
