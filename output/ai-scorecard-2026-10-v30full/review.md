---
slug: ai-scorecard-2026-10-v30full
report_type: ai_scorecard
status: pass
created_at: 2026-10-19
plan_source: output/ai-scorecard-2026-10-v30full/plan.md
research_source: output/ai-scorecard-2026-10-v30full/research.md
draft_source: output/ai-scorecard-2026-10-v30full/draft.md
results_hash: b8299899bf24b5ec62f89fc45160fa9af96d04af01590ebf0c692b7b149c90e7
draft_hash: 1c3cdcef52cfd314e17bdca0b79a9b23e416cf79dc715ddd97828280faf81c02
review_type: separate-session-4way
review_execution: separate_subagent_sessions
reviewers:
  - "fact-sources: fact-checker ×3(a·b·c) + evidence-editor → confirmation(opus)"
  - "financial-calc: financial-calc(sonnet) → confirmation(opus)"
  - "rule-consistency: rule-consistency(opus) → confirmation(opus)"
  - "output-readability: report-designer → confirmation(opus)"
---
# 리뷰 — 규칙 v3.0 14개사 채점(2026-10)

각 영역은 가능하면 독립 세션에서 검토하고 실제 수행자·결과를 남긴다. 수행하지 않은 검토를 pass 로 표시하지 않는다.

## 검토 영역

| 영역 | 검토 대상 | 검토자 | 결과 | 요약 |
| --- | --- | --- | --- | --- |
| 사실·출처 | 숫자·기업 귀속·기준 시점·공시·뉴스·부재 주장 | fact-checker(a·b·c)·evidence-editor → confirmation(opus) | pass | 1차 사실·출처 리뷰 셋이 needs_fix 를 냈다(Amazon FDA 경고 서한을 제목만 보고 미확인으로 둠, Microsoft ④ 금액과 Other 줄의 옮겨 가는 곳, Oracle 층 밖 적응을 '없음'으로 둠과 TikTok 합작법인의 근거, OpenAI Musk 소송을 끝난 사건으로 씀). 근거 불릿 리뷰는 pass 였다. 수정 묶음(PRP-133~202)과 새 근거 22건을 넣은 뒤 확인 리뷰가 22건 모두를 원문과 대조했다. 발췌는 원문 그 위치에 있고, 인용하는 줄은 발췌 범위 안이며, 끊긴 참조와 기준일을 넘긴 근거는 없다. 기록은 `review-parts/fact-sources-a.md`·`fact-sources-b.md`·`fact-sources-c.md`·`evidence-bullets.md`·`confirmation.md` 에 있다 |
| 재무 계산 | EPS·환율·ADR·TTM·FCF·런웨이·약정·단위·부호 | financial-calc(sonnet) → confirmation(opus) | pass | 1차 발견 1(Alibaba 지분증권 평가손익 관측이 빠짐)을 20-F·6-K 원문으로 등록했다(RMB66,652M ÷ 6.8980 = US$9,662.5M, 세전, 최근 1년). Alibaba ⑥ 은 −14 에서 −12 가 됐다. 정의·기간·부호·환율이 다른 회사 관측과 같고, 현금흐름표 기준으로 좁혀도 P1 바닥을 넘어 점수가 같다. 재계산 결정성 검사를 통과했다. 기록은 `financial-calc.md`·`confirmation.md` 에 있다 |
| 규칙 일관성 | factor 정의·상하한·예외·중복 속성·정성 승계·전 기업 동일 기준 | rule-consistency(opus) → confirmation(opus) | pass | 1차 F-1~F-5(기기 칸 AI 사슬의 근거, Alibaba 클라우드 가격에 인상 전 분기를 넣음, Oracle 층 밖 적응, Oracle·Palantir 가속도에 AI 무관 매출을 씀, NVIDIA 표준 선점에 설계 단계 발표를 셈)가 모두 풀렸다. 확인 리뷰가 ④ 기기 칸 열네 회사, ③ 가속도 서른여덟 층, ⑤ 소송·운동 전선의 성격을 표로 놓고 회사를 가로지른 새 어긋남이 없음을 확인했다. 기록은 `rule-consistency.md`·`confirmation.md` 에 있다 |
| 출력·가독성 | 표·카드·근거·차트·이력 일치, 낡은 비교 문장, 모바일·단일 HTML | report-designer → confirmation(opus) | pass | B-1·B-2(긴 사업 이름과 트리거 문장이 좁은 화면에서 넘침)를 렌더러 CSS 로 고쳤다(9b829f1). 320·375px 에서 회사 카드 14장, 트리거 표, 페이지의 가로 넘침이 모두 0 이다. B-3(순위 열 추가)은 2026-10-13 사용자 지시(순위 열을 뺌)와 어긋나 받지 않았다. draft 에 남은 내부 표현 몇 줄은 점수에 닿지 않아 다음 실행 과제로 둔다. 기록은 `output-readability.md`·`confirmation.md` 에 있다 |

결과는 pass / needs_fix / blocked 중 하나. 네 영역이 모두 pass 이고 체크리스트에 fail 이 없을 때만 frontmatter `status: pass`.
**승계 판단 예외(AGENTS.md 리뷰 범위 · 기업 추가 실행에만, rules.md 2.9)** — 정기 실행에서는 체크리스트 fail 이 하나라도 있으면 `status: pass` 가 아니다. 기업 추가 실행에서는 체크리스트 fail 의 사유가 `carried_score` 로 승계한 판단의 기존 논리이고, 이번 실행이 그 판단에 쓰인 잣대를 바꾸지 않았으며, 규칙 파일 `open_tensions` 에 재검토 시점과 함께 등록됐다면 `status: pass` 를 막지 않는다. 이때 해당 fail 과 **긴장 번호**(예: `TEN-RC-02`)를 근거 칸에 그대로 적는다. 이번 실행이 바꾼 잣대가 닿는 승계 판단은 이 예외가 아니다 — 한 회사에 새 잣대를 댔으면 같은 잣대가 닿는 모든 회사에 대야 한다(Q03).

## 체크리스트

| ID | 검사 초점 | 결과 | 근거 |
| --- | --- | --- | --- |
| Q01 | 이 감점, 다른 칸에서 이미 셌나? | pass | 같은 속성을 두 번 센 곳이 없다. Alibaba ⑥ 은 P1 에서 평가손익을 조정하고 P4 영업외 비중을 건너뛰었다. 수출 통제(NVIDIA ⑤·Alibaba ⑧), 고객 자체 칩(⑤ 만), Palantir 정부 집중(⑧ 만)은 1차 판정과 같다 |
| Q02 | 이 지표가 이 칸의 정의에 맞나? | pass | 1차 fail 사유 셋이 풀렸다. 기기 칸 AI 사슬은 회사 1차 근거로 받쳤고(규칙 F-1), 인상 전 분기를 클라우드 가격 B 에서 뺐으며(F-2), AI 무관 줄의 성장을 가속도에서 뺐다(F-4). 시장 평균 단가와 시장 성장률을 ① 에 넣은 곳이 없다 |
| Q03 | 회사마다 같은 잣대인가? | pass | 1차 fail 사유(규칙 F-1~F-5, 사실 b F-01, 재무 발견 1)가 모두 풀렸다. 사건 교차표에 Musk 소송·TikTok 합작법인·FDA 서한을 더해도 자료 유무 때문에 읽기가 갈린 곳이 없다. Palantir 지분증권 손익 관측은 아직 없지만, 원문으로 확인되는 하한이 ⑥ 을 움직이는 문턱(세전 약 $98M)에 못 미치고 나머지는 금액이 공시되지 않아 지금 점수는 확인된 자료로 정해진다(다음 실행 과제 10) |
| Q04 | 시총 크기를 밸류에이션으로 착각했나? | pass | ⑥ 은 비율 파라미터와 성장 조정으로만 계산했고, 시총 크기를 근거로 쓴 판단이 없다 |
| Q05 | 출처가 이해당사자인가? | pass | 새 근거는 법원 기록·공시·회사 1차 발표·보도이고 등급을 줄에 적었다. 이해상충 표기는 점검하지 않는다(AGENTS.md 「금지·주의」) |
| Q06 | 볼륨인가 가치인가? | pass | 토큰·트래픽 점유율은 부분 반영으로만 썼다. 1차 판정과 같다 |
| Q07 | "안 만든 것"을 카운터 포지셔닝으로 셌나? | pass | 만들지 않은 제품을 카운터 포지셔닝으로 센 곳이 없다. 1차 판정과 같다 |
| Q08 | 적대세력을 수로 셌나, 성격으로 셌나? | pass | 사실 c 의 보류 사유(Musk 사건의 전제)가 법원 기록으로 고쳐졌다. OpenAI 전선은 성격(비용형 열다섯, 구조형 미확인 둘)과 관할 수로 정했다 |
| Q09 | 미래 계획을 현재 점수에 넣었나? | pass | 1차 fail 사유(NVLink Fusion 설계 단계 발표를 표준으로 셈)가 풀렸다. Oracle ⑧ 의 Gemini 탑재는 계획으로, SB OAI Japan 은 판매 예정으로 고쳐 썼고, 지분 동맹은 맺은 지분으로 센다. TRG-303 재검토 칸에 미래 점수가 없다 |
| Q10 | 거리를 가속도로 착각했나? | pass | 가속도는 모두 같은 정의의 두 배수를 나눈 값이고 누적값을 쓴 곳이 없다 |
| Q11 | 순적자를 실격 사유로 썼나? | pass | 적자는 ⑨ 에서만 감점했다 |
| Q12 | ③ 세 기준을 동등하게 쟀나? | pass | 모방 불가능성 8 없이 16 이상을 받은 층이 없다 |
| Q13 | "공짜로 뿌린다"를 곧바로 카운터 포지셔닝으로 셌나? | pass | 공짜 전략은 거둘 장치가 있는 곳만 셌다(사용자 결정: 거둘 장치가 있으면 공짜 전략으로 ③ 을 재고, 거둔 매출이 확인되지 않으면 수익모델 4) |
| Q14 | 아직 안 끝난 승부를 끝난 것처럼 쟀나? | pass | 문 닫힘 증거로 20 을 받은 층이 없다 |
| Q15 | ⑤에서 "공짜 사용자"를 아군으로 셌나? | pass | 파생 모델·개발자·NACS 채택사를 동맹으로 세지 않았다 |
| Q16 | ①을 사업마다, ②③을 층마다 나눠 쟀나? | pass | ① 은 사업마다, ②③ 은 층마다 쟀다. 층 배정과 사업 나누기는 1차 판정과 같고 수정 묶음이 바꾸지 않았다 |
| Q17 | ②를 "표준 없음"만으로 깎았나? | pass | 벤치마크가 없는 층은 (적응 + 표준) × 2 로 쟀다. Oracle 층 밖은 적응 미확인 2 로 고쳤다 |
| Q18 | ⑤에서 관계사를 독립 동맹으로 셌나? | pass | Tesla–SpaceX 관계사 제외를 유지했다. 합병 보도는 트리거로만 둔다(TRG-151·302) |
| Q19 | ⑤에서 "받은 투자"를 곧바로 지분 동맹으로 셌나? | pass | 받은 투자는 동맹에서 뺐다. TikTok 합작법인은 Oracle 이 맺은 지분이다 |
| Q20 | 조달을 동맹으로 셌나? | pass | 조달은 동맹에서 뺐다 |
| Q21 | 동맹이자 의존인 관계를 한쪽에서만 셌나, 또는 같은 속성을 양쪽에서 셌나? | pass | ⑤ '상대가 떠날 수 있나'와 ⑧ '내가 떠날 수 있나'를 섞은 곳이 없다 |
| Q22 | 지분 평가이익을 ⑦ 순환금융 증거로 셌나? | pass | 지분 평가이익은 ⑥ 에서만 다루고 ⑦ 입력에 없다 |
| Q23 | 벤치마크를 서로 다른 하네스끼리 비교했나? | pass | 같은 하네스 안의 순위만 비교했다 |
| Q24 | 끝난 싸움을 ② 표준 선점·③·⑤ 적대에 셌나? | pass | 끝나지 않은 Musk v. Altman 과 X.AI 항소를 전선으로 넣었고, 끝난 사건(IF Metall 쟁의 중단, Oracle 개인정보 합의 지급, Palantir Mopac)은 뺐다 |
| Q25 | 매출 몫이 없는 층의 강점을 옮겨 셀 때 원칙을 지켰나? | pass | 모델 순위를 다른 층으로 옮긴 곳이 없고, 공짜 전략은 거두는 층에서 셌다 |

결과는 pass / fail / not_applicable. not_applicable 도 근거가 필요하다.

## 발견 사항

- **1차 리뷰.** 일곱 갈래 가운데 사실·출처 a·b·c, 재무 계산, 규칙 일관성이 needs_fix 를 냈고, 근거 불릿과 출력·가독성은 pass 였다. 점수에 닿은 발견은 아홉 건이다.
  - 규칙 F-1: Amazon·Meta ④ 기기 칸 AI 사슬을 미확인인데 '예'로 셈. 두 회사 모두 회사 1차 근거(EV-amazon-106, EV-meta-104)를 세워 '예'를 유지했고, Alphabet 도 EV-alphabet-122 로 받쳤다.
  - 규칙 F-2: Alibaba ① 클라우드 가격 실측에 인상 전 분기를 넣음. 미확인으로 고쳐 Alibaba ① 이 9 에서 8 이 됐다.
  - 규칙 F-3·사실 b F-01: Oracle ② 층 밖 적응을 '없음'으로 둠. 미확인 2 로 고쳐 Oracle ② 가 5 에서 6 이 됐다.
  - 규칙 F-4: Oracle·Palantir ③ 가속도에 ④ 가 AI 무관으로 센 매출 줄의 성장을 씀. 자료 없음으로 고쳐 Oracle ③ 은 4 에서 3, Palantir ③ 은 3 에서 2 가 됐다.
  - 규칙 F-5: NVIDIA ② 표준 선점에 설계 단계 발표를 셈. 0 으로 고쳐 NVIDIA ② 가 12 에서 11 이 됐다.
  - 사실 a F-1: Amazon ⑤ FDA 경고 서한을 제목만 보고 미확인으로 둠. 원문으로 확정해 비용형 전선에 넣었고, 비용형 상한이 이미 서 있어 점수는 같다.
  - 사실 a F-2·F-3: Microsoft ④ 금액($202,305M)과 ① Other 줄의 옮겨 가는 곳(8-K Ex.99.1)을 고쳤다. 점수는 같다.
  - 사실 c 발견 1: OpenAI ⑤ Musk 소송을 끝난 사건으로 씀. 법원 기록으로 최종 판결 전임을 확인해, 영리 전환 청구는 structural_unknown, 반독점 청구와 X.AI 영업비밀 항소는 비용형 전선으로 넣었다. OpenAI ⑤ 가 8 에서 6 이 됐다.
  - 재무 발견 1: Alibaba 지분증권 평가손익 관측이 빠짐. 등록해 Alibaba ⑥ 이 −14 에서 −12 가 됐다.
- **수정 묶음.** 원 판단 세션 아홉이 차례로 PRP-133~199 를 반영했고, 조율자가 PRP-200~202(Alphabet ④ 기기 근거, Alphabet 클라우드 ③ Gemma 문장, Anthropic ⑤ Meta 지수 줄)를 반영했다. 제안 70건은 모두 accepted 다. 새 근거는 22건, 새 관측은 1건이다.
- **수정 뒤 결과.** Alphabet 43 · Meta 41 · Amazon 32 · TSMC 31 · Microsoft 24 · Apple 24(공동 5위) · NVIDIA 19 · Alibaba 10 · Palantir 8 · Oracle 5 · SpaceX + xAI −1 · Tesla −1(공동 11위) · OpenAI −6 · Anthropic −13. 순위에서 빠진 회사는 없다.
- **받지 않은 지적.** 출력 리뷰 B-3(순위 열 추가)은 2026-10-13 사용자 지시(순위 열을 뺌, 가로 스크롤 금지)와 어긋나 받지 않았다.
- **확인 리뷰.** 1차 needs_fix 아홉 건이 모두 풀렸고, 회사를 가로지른 새 어긋남이 없으며, 체크리스트 Q01~Q25 와 제목만 보고 확정·미확인 처리 금지 항목(AGENTS.md 2026-10-12)이 모두 pass 다(`review-parts/confirmation.md`).
- **리뷰어 절차 위반 한 건.** 사실·출처 c 리뷰어가 SEC 주소 하나를 `sec-get` 이 아닌 curl 로 요청했다(403, 받은 것 없음). 같은 주소를 `sec-get` 으로 다시 받아 대조했다.
- **다음 실행 과제(점수에 닿을 수 있는 것).** Palantir `equity_investment_gains_ttm` 을 등록해 세전 약 $98M 이상이 확인되면 Palantir ⑥ 은 −12 에서 −13, 총점은 8 에서 7 이 된다. 지분법 처분·희석 이익을 ⑥ 에 넣을지는 규칙 문언으로 정해야 한다(TSMC 는 넣고 Microsoft 는 뺌, 재무 리뷰 발견 3).
- **다음 실행 과제(점수에 닿지 않는 것).** draft 에 남은 내부 표현(anthropic.F5 의 "이 실행의 다른 회사도", 시범 승인본에서 이어진 alphabet·spacex-xai 의 "이 실행" 문장, 계산 코드가 만드는 참고 줄의 "이 실행"·"사용자 결정 2026-09-17", alibaba.F9 의 "실행 결정에 따라", Qwen "처음으로" 두 줄의 2차 보도 표시, Bing "처음으로 10억 명" 줄의 날짜)을 고치고 검증기 금지 표현에 더한다. TRG-366·367 의 `source_ids`, 새 출처의 `sha256`, EV-microsoft-105 relevance, EV-amazon-106 발췌 보강, 규칙 2.10 기기 조건과 ⑤ 구조형 기준의 문언 보강은 `confirmation.md` 다음 실행 과제 1~11 과 1차 리뷰 파일의 다음 실행 과제 절에 있다.

## 판정

- results_hash `b8299899bf24b5ec…` · draft_hash `1c3cdcef52cfd314…` 기준 검토. 자료·규칙·판단·초안이 바뀌면 이 리뷰는 무효다(D-10).
- **두 해시의 뜻이 다르다.** `results_hash` 는 `results.json` 에서 `results_hash` 키를 뺀 내용의 정렬 JSON 해시이고(`engine.sha256_obj`) **파일 바이트 sha256 과 다르다.** `draft_hash` 는 초안 **파일 바이트 sha256** 이다. 대조할 때 섞지 않는다.
