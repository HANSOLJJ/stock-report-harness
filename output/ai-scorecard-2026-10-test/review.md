---
slug: ai-scorecard-2026-10-test
report_type: ai_scorecard
status: pass
created_at: 2026-10-01
plan_source: output/ai-scorecard-2026-10-test/plan.md
research_source: output/ai-scorecard-2026-10-test/research.md
draft_source: output/ai-scorecard-2026-10-test/draft.md
results_hash: d82fcfa1fa3148cec2e6df63765ab0c7fb724fd8f12095fc5fd1a00de8d69bd2
draft_hash: 30135ffb15ac1be66339eb55f6242883e9dc2e8bfc7ac3dad560727914fed8a7
review_type: separate-session-4way
review_execution: separate_subagent_sessions
reviewers:
  - "fact-sources: pass (Claude Opus 5.5 (claude-opus-5-5) · fact-checker 독립 세션(2차 재리뷰 + 3차 확인, 이 실행을 만든 세션 아님) · 2026-10-01)"
  - "financial-calc: pass (Claude Opus 5.5 · 재무 계산 독립 세션(이 실행을 만든 세션 아님) · 2026-10-01 · 2차, 3차 확인)"
  - "rule-consistency: pass (Claude Opus 5.5 · 규칙 일관성 독립 세션 · 2026-10-01 · 2차(재리뷰) + 3차 기준 갱신 확인. 이 실행을 만든 세션이 아니다)"
  - "output-readability: pass (Claude Opus 5.5 · report-designer 독립 세션(3차 확인, 이 실행을 만든 세션 아님) · 2026-10-01)"
---
# 리뷰 — v1.8 근거 계층 시험 실행

각 영역은 가능하면 독립 세션에서 검토하고 실제 수행자·결과를 남긴다. 수행하지 않은 검토를 pass 로 표시하지 않는다.

## 검토 영역

| 영역 | 검토 대상 | 검토자 | 결과 | 요약 |
| --- | --- | --- | --- | --- |
| 사실·출처 | 숫자·기업 귀속·기준 시점·공시·뉴스·부재 주장·이해상충 | Claude Opus 5.5 (claude-opus-5-5) · fact-checker 독립 세션(2차 재리뷰 + 3차 확인, 이 실행을 만든 세션 아님) · 2026-10-01 | pass | 3차 확인에서 2차 medium 세 건(발견 1~3)이 모두 닫혔다. 이해상충 기준에 nvidia(Anthropic 투자자)와 spacex-xai(경쟁사·컴퓨트 공급자)가 들어갔다. 출처 19건이 채워져 표기 출처는 69/129건이 됐고, 지적한 4건도 모두 표기됐다. PRP-006·007 로 Oracle ⑨ 게이트 1(영업이익 $20.61B ÷ 매출 $67.36B = 30.6%)과 아마존 순부채(-$119.3B)가 verified 관측과 맞게 고쳐졌다. 점수·순위는 바뀌지 않았다. 참조 무결성, excerpt·출처·후보 일치, 인용 근거 표 38건을 다시 확인했고 새 문제는 없다. 남은 것은 low 뿐이고 다음 실행 과제로 넘긴다(조정자 지시). 상세: `review-parts/fact-sources.md` |
| 재무 계산 | EPS·환율·ADR·TTM·FCF·런웨이·약정·단위·부호 | Claude Opus 5.5 · 재무 계산 독립 세션(이 실행을 만든 세션 아님) · 2026-10-01 · 2차, 3차 확인 | pass | 1차 medium 두 건은 둘 다 닫혔다. TSMC 환율 민감도를 관측 원값(NT$)과 새 시가총액으로 다시 계산하니 P1 43.7216/45.7007, 손익분기 환율 32.2872, P2 18.9156/19.7976 이 나와 기록과 맞는다. 아마존 ⑨ 런웨이는 9.9538년(115,713M ÷ 11,625M), 현금만 6.728년이고, Oracle ⑨ 는 1.3210년(31,289M ÷ 23,686M)이다. 판단 문장, 초안, 트리거 TRG-005 에 같은 값이 적혀 있다. 14개사 9-factor 점수와 순위는 1차와 같다. obsreg 대비 바뀐 칸은 meta ⑥, oracle ⑥, anthropic ⑤ 세 칸뿐이다. ⑥ 은 관측에서 다시 계산해 P1·P2·P3 값, 밴드, 소계, P4, 최종 점수가 14개사 모두 맞는다. preview 의 이전 실행 대비 표 세 행과 원인 분류도 맞다. 남은 것은 점수에 닿지 않는 low 두 건이다(셋째는 3차에서 닫혔다). Alibaba 민감도 기록은 숫자가 옛 입력 기준으로 남았고, † 각주 마지막 문장은 apple·palantir 순현금 † 를 빠뜨렸고, 새로 매긴 ⑨ 판단 문장에 legacy 재무 수치 두 개가 남았다. 상세: `review-parts/financial-calc.md` |
| 규칙 일관성 | factor 정의·상하한·예외·중복 속성·정성 승계·전 기업 동일 기준 | Claude Opus 5.5 · 규칙 일관성 독립 세션 · 2026-10-01 · 2차(재리뷰) + 3차 기준 갱신 확인. 이 실행을 만든 세션이 아니다 | pass | 1차 Q03 fail 의 원인이던 oracle.F9 의 `BBB-라 조달 여력을 온전히 인정받지 못한다(A- 이상만 무제한)` 는 PRP-003 으로 지워졌다. 그 자리는 이제 v1.7 완충 정의(현금과 확정 미인출 여신만)로 하향을 설명한다. 14개사 F9 를 전수로 다시 봤고, 신용등급으로 조달 여력을 인정하거나 부정하는 문장은 판단에 남아 있지 않다. 남은 신용등급 언급은 oracle.F8·openai.F7 의 `(교차검증·별표 J)` 두 줄뿐이고 점수 사유가 아니다. 1차 medium 두 건은 닫혔다. amazon.F9 런웨이 숫자는 PRP-004 로 엔진 값(9.95년, 현금만 6.7년)과 맞춰졌다. 남은 fail 은 모두 승계 판단 예외이고, 긴장 번호 16개가 v1.8.json open_tensions 에 2026-11 재검토로 등록돼 있다. 남은 발견은 low 여섯 건과 info 세 건이고 어느 것도 점수를 바꾸지 않는다. 3차에 low 한 건이 늘었다. 이해상충 기준을 넓힌 뒤에도 같은 기준이 닿는 SEC 제출본 출처 3건에 표기가 없다(Q05, 아래 발견). 체크리스트 결과 칸은 검증기 형식에 맞춰 `fail` 로 적고, 승계 예외와 긴장 번호는 근거 칸에 둔다. 상세: `review-parts/rule-consistency.md` |
| 출력·가독성 | 표·카드·근거·차트·이력 일치, 낡은 비교 문장, 모바일·단일 HTML | Claude Opus 5.5 · report-designer 독립 세션(3차 확인, 이 실행을 만든 세션 아님) · 2026-10-01 | pass | 1차 high 두 건(함정 최심 동점, TRG-037 의 옛 적대 등급 0)과 medium 여섯 건이 닫혔다. 2차에서 남았던 M1(HTML 근거 ID 대응)은 ab896b9 로 닫혔다. "이번 실행에서 다시 매김" 은 이번 실행에서 고친 판단 네 개(anthropic ⑤, amazon ⑤, amazon ⑨, oracle ⑨)에만 붙는다. 이 네 개는 proposals.json 의 accepted 일곱 건(PRP-001~007)과 맞는다. amazon ⑨ 는 PRP-002·004·007, oracle ⑨ 는 PRP-003·006 이다. 3차 입력 변경(PRP-006·007 숫자 반영, 출처 이해상충 보강) 뒤에도 순위표 14행, 카드 머리줄 14개, 카드 factor 126칸, 미리보기 14행이 results.json 과 모두 같고, 순위·점수는 2차와 같다. 남은 것은 low 뿐이다. report.html 은 아직 없다. HTML 시각 검증은 빌드 뒤 `uv run --frozen python -X utf8 scripts/validate_report_contract.py ai-scorecard-2026-10-test --require-html` 와 Playwright 실측으로 미룬다. 상세: `review-parts/output-readability.md` |

결과는 pass / needs_fix / blocked 중 하나. 네 영역이 모두 pass 이고 체크리스트에 fail 이 없을 때만 frontmatter `status: pass`.
**승계 판단 예외(AGENTS.md 리뷰 범위)** — 체크리스트 fail 의 사유가 `carried_score` 로 승계한 판단의 기존 논리이고, 이번 실행이 그 판단에 쓰인 잣대를 바꾸지 않았으며, 규칙 파일 `open_tensions` 에 재검토 시점과 함께 등록됐다면 `status: pass` 를 막지 않는다. 이때 해당 fail 과 **긴장 번호**(예: `TEN-RC-02`)를 근거 칸에 그대로 적는다. 이번 실행이 바꾼 잣대가 닿는 승계 판단은 이 예외가 아니다 — 한 회사에 새 잣대를 댔으면 같은 잣대가 닿는 모든 회사에 대야 한다(Q03).

## 체크리스트

| ID | 검사 초점 | 결과 | 근거 |
| --- | --- | --- | --- |
| Q01 | 이 감점, 다른 칸에서 이미 셌나? | fail | 규칙 일관성: 승계 예외 — **이번 변경분은 통과다.** anthropic.F5 H 근거(국방부 배제 유지·FTC 제품 안전 조사)는 다른 칸에서 세지 않는다. anthropic.F8 의 `FTC 가 계약 배타성 검토` 는 다른 사안이고, 이번 실행 판단으로 대체돼 초안에서도 취소선이다. 승계 fail 은 nvidia F5·F8 의 자체 칩 이탈(TEN-RC-05)과 tesla F5·F8 의 NHTSA(TEN-RC3-04)다. 이번 실행은 두 판단의 잣대를 바꾸지 않았고 둘 다 2026-11 재검토로 등록돼 있다 |
| Q02 | 이 지표가 이 칸의 정의에 맞나? | fail | 규칙 일관성: 승계 예외 — 변경 일곱 건(PRP-001~007)의 지표는 칸 정의에 맞는다. ⑤ H 에는 규제·시장 차단을 썼고, ⑨ 완충은 현금과 확정 여신이다. 승계 fail 은 TEN-RC-02(anthropic F1)·TEN-RC3-01(anthropic·openai F7)·TEN-RC3-03(palantir·oracle F1)·TEN-RC3-05(alibaba F3)·TEN-RC4-02(openai F1)이고 모두 등록돼 있다. 저심각 관찰 하나가 남았다. 이번 실행이 고친 amazon.F9·oracle.F9 두 판단에 순부채 줄이 남아 있다(oracle 은 Debt/EBITDA·이자보상·Altman Z 도). 이는 ⑨ `쓰지 않는 것`(857행 `순부채 잔고 … 레버리지는 별표 J`)에 해당한다. 엔진 입력이 아니라 점수에 닿지 않고, 두 회사에 같은 모양으로 남아 있어 회사 간 잣대 차이는 아니다. 3차: PRP-007 은 amazon 순부채 숫자만 검증 관측(-$119.3B, 2026-06-30)으로 바꿨고, 줄은 그대로라 관찰도 그대로다. PRP-006 은 oracle 게이트 1 의 영업이익·마진을 검증 관측(20,606M ÷ 67,357M = 30.6%)으로 바꿨다. operating_result_reviewed=profit 은 그대로이고 G1 정의(영업이익)에도 맞는다 |
| Q03 | 회사마다 같은 잣대인가? | fail | 규칙 일관성: 승계 예외 — **1차 fail 은 닫혔다.** (1) oracle.F9 의 신용등급 기반 조달 여력 문장은 PRP-003 으로 `완충은 현금과 확정 미인출 여신만 센다(v1.7 ⑨ 게이트 3) — 신용등급(BBB-)으로 조달 여력을 가감하지 않는다` 로 바뀌었다(초안 1049행). 런웨이 1.32년, 1~3년 구간 한 칸 하향은 엔진(완충 31,289M ÷ 23,686M)과 같다. (2) 14사 F9 를 전수로 다시 봤다. alphabet `순현금·현금으로 완충 최상위급`, amazon(현금+확정 여신), alibaba(현금+확정 여신, 8월 증자는 관측일 뒤라 제외), spacex-xai(v1.5 인용 라벨 + verified 현금+여신)는 모두 v1.7 정의 안에 있다. meta·microsoft·tsmc·apple·nvidia·palantir·tesla 는 FCF 흑자라 G3 대상이 아니다. openai 에는 완충 서술이 없다. 신용등급으로 조달 여력을 인정하거나 부정하는 문장은 남아 있지 않다. anthropic.F9 의 `완충이 외부 조달뿐` 은 경계 사례로 보고 low 로 따로 적었다(아래 발견). (3) 적대 0 잣대도 통과다. PRP-005 이후 amazon.F5 는 `이번 실행에서 적대 등급 0 인 기업은 없다` 라고 적는데, 14사 H 를 대조한 결과(최고 -1)와 맞는다. 같은 FTC 조사가 걸린 openai 는 H -3, NYC 조사가 걸린 spacex-xai 는 -1 이라 이미 비용형 이하다. 승계 fail 은 TEN-RC-03(C-08, 별표 H 이탈 조건)·TEN-RC4-03(spacex-xai H 수 비교)이다. TEN-RC-03 에는 이번 실행이 고친 amazon.F5·anthropic.F5.impl48 이 들어 있다. 그러나 이번 변경은 H 와 만점 예시 문장만 건드렸고 A 등급을 가르는 별표 H 이탈 잣대는 바꾸지 않았으므로 예외 조건이 선다. TEN-RC4-03 도 같다. 이번 실행은 기존 별표 G 의 H 정의를 새 근거에 댔을 뿐 새 잣대를 만들지 않았고, spacex-xai 는 종류로 다시 대도 비용형 -1 이다(EV-spacex-xai-006 conditional_impact) |
| Q04 | 시총 크기를 밸류에이션으로 착각했나? | pass | 규칙 일관성: 상장사 ⑥ 은 parameters 모드(P1 TTM PER·P2 (시총−순현금)/매출)로 계산됐고 시총 절대액을 쓰지 않는다. 이번 변경은 ⑥ 과 무관하다 / 재무 계산: pass — ⑥ 은 시총을 분자로 쓰는 비율(시총 ÷ 모회사 귀속 순이익, (시총 − 순현금) ÷ 매출)로만 점수를 낸다. meta ⑥ −1→−3 과 oracle ⑥ −3→−2 는 이번 재계산에서도 시총 변화가 같은 이익·매출 대비 배수를 25·8 선 너머로 옮긴 결과다. 시총 절대 크기는 어떤 밴드에도 들어가지 않는다. |
| Q05 | 출처가 이해당사자인가? | fail | 규칙 일관성: 승계 예외 — 변경분은 통과다. anthropic H 근거는 Reuters·Bloomberg 보도다. 제안자가 Anthropic 모델이라는 이해상충과 방향(Anthropic 에 불리)이 제안 사유와 근거 relevance 에 적혀 있다. 벤더 발표 근거는 conditional_impact 가 `회사 발표만으로는 바꾸지 않는다` 로 막아 두었다. 승계 fail 은 TEN-RA-02(nvidia F2)·TEN-RA3-01(openai F4)이고 등록돼 있다. **3차 확인**: 이해상충 기준에 nvidia·spacex-xai 와 Anthropic·Claude 를 다루는 기사가 더해졌다. 그 결과 출처 129건 가운데 69건에 표기가 있고 60건이 비어 있다. 빈 60건 가운데 news 는 alibaba·apple·meta·oracle·palantir·tesla·tsmc 피드이고, 제목에 Anthropic·Claude 를 다루는 기사는 남아 있지 않다. 다만 같은 기준이 닿는 출처 3건(SRC-SEC-AMZN-10Q-2026Q2, SRC-SEC-SPCX-10Q-2026Q2, SRC-SEC-SPCX-S1A-2026)은 아직 비어 있다. 같은 발행사의 SRC-EDGAR-* 제출본에는 표기가 붙어 있다. 이 출처들은 법정 제출본이라 벤더 발표가 아니다. 그리고 표기가 빠진 것은 선별·판정자(Claude) 쪽 이해상충이지 출처를 1차 근거로 쓴 방식의 문제가 아니다. 그래서 이 칸의 새 fail 사유로 세지 않고 low 로 적는다(아래 발견) / 사실·출처: pass — Q09(미래 계획을 현재 점수에 넣었나): pass(사실·출처 범위). 트리거 40건에 점수 키가 없다. 계획·검토 단계 사건(TRG-007·019·025·027·034·035 등)은 observation 에 계획·검토로 분리돼 있다. PRP-003~005 도 계획을 점수 재료로 쓰지 않는다. Oracle ⑨ 의 "$45~50B 추가 조달 예정" 은 서술일 뿐 게이트 입력이 아니다. / 출력·가독성: pass — Q09 미래 계획을 현재 점수에 넣었나: 이 영역에서 판정하지 않음. 출력 측면에서는 트리거가 미래 점수를 저장하지 않는다는 것만 확인했다. 점수 반영 여부는 규칙 일관성 영역이 본다. |
| Q06 | 볼륨인가 가치인가? | pass | 규칙 일관성: ① 가격 결정력 근거는 토큰 점유율이 아니라 매출 점유율과 $/M 이다. 새 근거로 볼륨 지표가 점수에 들어간 곳은 없다 / 재무 계산: pass — 이 세션이 다시 계산한 범위는 ⑥ 과 ⑨ 다. ⑥ P3 는 매출 금액 성장률이고, ⑨ G3 는 $ 완충 ÷ $ 소진, G4 는 계약 매출 $ ÷ 약정 $ 다. 사용자 수나 토큰 같은 볼륨 지표는 계산 경로에 없다. ①⑤ 같은 정성 판단 안의 Q06 은 보지 않았다. |
| Q07 | "안 만든 것"을 카운터 포지셔닝으로 셌나? | pass | 규칙 일관성: amazon.F3 이 `모델을 안 만든 것 자체는 카운터 포지셔닝이 아니다` 라고 명시한다. 이번 실행에서 바뀐 것은 없다 |
| Q08 | 적대세력을 수로 셌나, 성격으로 셌나? | fail | 규칙 일관성: 승계 예외 — **변경분은 통과다.** anthropic.F5 H=-1 은 적대의 종류로 매겼다. `시장 일부 차단과 규제 조사이고 사업 구조 자체를 겨냥하지 않아 -2 구조형은 아니다` 는 규칙 286~287행 문언과 맞는다. 승계 fail 은 spacex-xai.F5 `동맹이 적보다 확실히 많지 않음 → 3`(수 비교)이고 TEN-RC4-03 으로 등록돼 있다 |
| Q09 | 미래 계획을 현재 점수에 넣었나? | fail | 규칙 일관성: 승계 예외 — 변경 일곱 건은 이미 일어난 사건(항소심 유지·조사 개시)과 실측 현금·확정 여신만 쓴다. 이번에 고친 oracle.F9 에 남은 `2026년 $45~50B 추가 조달 예정` 은 엔진 입력이 아닌 위험 서술이다. 규칙 706행도 같은 사례를 `빚으로 산 런웨이는 공짜가 아니다` 로 적는다. 런웨이를 늘리는 데 쓰이지 않았다. 승계 fail 은 TEN-RA-02·TEN-RA3-01·TEN-RA6-01 이고 등록돼 있다 |
| Q10 | 거리를 가속도로 착각했나? | fail | 규칙 일관성: 승계 예외 — 이번 실행은 ③ 을 바꾸지 않았다. 승계 fail 은 TEN-RB-Q10·TEN-RC4-04 이고 등록돼 있다 |
| Q11 | 순적자를 실격 사유로 썼나? | pass | 규칙 일관성: ⑨ 는 게이트 경로(G1·G2·G3·G4)로 계산된다. 순적자만으로 실격시킨 판단은 없다. spacex-xai 는 손실률 -16.2% 구간, anthropic·openai 는 비상장 미공시 경로다 / 재무 계산: pass — spacex-xai 는 순손실이라 P1 을 만들지 않았고(`parameters_optional_unmet.P1`, 감점 아님) P2·P3 로 소계를 냈다. 비상장 2사 ⑨ 는 비상장 경로로 −2 이고 실격 처리는 없다. FCF 음수 기업(amazon·oracle·alibaba·spacex-xai)은 런웨이 사다리로만 깎였다. |
| Q12 | ③ 세 기준을 동등하게 쟀나? | fail | 규칙 일관성: 승계 예외 — ③ 사다리는 엔진이 적용한다. 승계 fail 은 TEN-RC4-01·TEN-RC3-05 이고 등록돼 있다 |
| Q13 | "공짜로 뿌린다"를 곧바로 카운터 포지셔닝으로 셌나? | fail | 규칙 일관성: 승계 예외 — alibaba.F3 의 오픈웨이트(회수 장치 없음)를 imitation=partial 로 둔 것이다. TEN-RC3-05 의 두 번째 사유로 등록돼 있다 |
| Q14 | 아직 안 끝난 승부를 끝난 것처럼 쟀나? | pass | 규칙 일관성: 14사 F3 의 door_closed 가 전부 fail 이라 사다리 상한이 걸린다 |
| Q15 | ⑤에서 "공짜 사용자"를 아군으로 셌나? | pass | 규칙 일관성: nvidia.F5(개발자 1,800만 불인정)·alibaba.F5(파생모델 15만 불인정)·meta.F5(Glimmer 개발자 무효)가 같은 잣대다 |
| Q16 | ①을 한 채널로만 쟀나? | fail | 규칙 일관성: 승계 예외 — 승계 fail 은 TEN-RC-02(anthropic F1)·TEN-RC4-02(openai F1)이고 등록돼 있다. 이번 실행은 ① 을 바꾸지 않았다 |
| Q17 | ②를 "표준 없음"만으로 깎았나? | pass | 규칙 일관성: ② 가 낮은 기업은 세 경로를 모두 판정했고 `표준 없음` 하나로 깎지 않았다 |
| Q18 | ⑤에서 관계사를 독립 동맹으로 셌나? | pass | 규칙 일관성: tesla.F5 A=0(유일한 아군이 관계사 SpaceX), spacex-xai.F5 는 Tesla 를 동맹에서 뺐다. 양쪽이 같은 잣대다 |
| Q19 | ⑤에서 "받은 투자"를 곧바로 동맹 +2로 셌나? | pass | 규칙 일관성: anthropic.F5·openai.F5 가 받은 투자를 A 에서 뺐다. 이번 변경은 H 만 건드렸고 A=+1 은 그대로다 |
| Q20 | 조달을 동맹으로 셌나? | fail | 규칙 일관성: 승계 예외 — 변경분은 통과다. anthropic A 는 3사 유통으로 서고, 컴퓨트 구매는 `조달 ≠ 동맹` 으로 뺐다. 승계 fail 은 별표 H 이탈 조건의 전사 미통일이고 TEN-RC-03(C-08)으로 등록돼 있다. 이번 실행은 이 잣대를 바꾸지 않았다(Q03 칸 참조) |
| Q21 | 동맹이자 의존인 관계를 한쪽에서만 셌나, 또는 같은 속성을 양쪽에서 셌나? | fail | 규칙 일관성: 승계 예외 — 변경분은 통과다. anthropic 의 같은 3사 관계를 ⑤ 연동과 ⑧ 대체 불가에 한 번씩 센다(규칙 266행 허용). 승계 fail 은 TEN-RC-05·TEN-RC3-04 이다. EV-nvidia-007 conditional_impact 의 이중 계상 서술은 그대로 남아 있다(아래 low). 근거 문장이고 판단은 바뀌지 않았다 |
| Q22 | 지분 평가이익을 ⑦ 순환금융 증거로 셌나? | pass | 규칙 일관성: alphabet.F7 이 평가익을 ⑥ 소관으로 뺐다. amazon.F7·nvidia.F7 의 영업외 이익은 방증으로만 쓴다 / 재무 계산: pass — ⑦ 14건 모두 observation_ids 가 비어 있다. calc 키는 `funding_dependent_share`·`own_money_returns` 두 축이거나 비어 있다. 영업외 비중은 ⑥ P4 에만 쓰인다. |
| Q23 | 벤치마크를 서로 다른 하네스끼리 비교했나? | fail | 규칙 일관성: 승계 예외 — 이번 실행은 ② 를 바꾸지 않았다. 승계 판단 anthropic·meta·alibaba·openai F2 의 하네스 미표기는 TEN-RA4-01 로 등록돼 있다 |

결과는 pass / fail / not_applicable. not_applicable 도 근거가 필요하다.

## 발견 사항

- 영역별 발견과 1차 발견의 닫힘 여부는 각 `review-parts/<영역>.md` 에 있다. 2차 리뷰에서 남은 high·medium 은 없고, low 는 다음 실행 과제로 넘긴다.

## 판정

- results_hash `d82fcfa1fa3148ce…` · draft_hash `30135ffb15ac1be6…` 기준 검토. 자료·규칙·판단·초안이 바뀌면 이 리뷰는 무효다(D-10).
- **두 해시의 뜻이 다르다.** `results_hash` 는 `results.json` 에서 `results_hash` 키를 뺀 내용의 정렬 JSON 해시이고(`engine.sha256_obj`) **파일 바이트 sha256 과 다르다.** `draft_hash` 는 초안 **파일 바이트 sha256** 이다. 대조할 때 섞지 않는다.
