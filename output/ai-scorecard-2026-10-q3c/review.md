---
slug: ai-scorecard-2026-10-q3c
report_type: ai_scorecard
status: pass
created_at: 2026-10-27
plan_source: output/ai-scorecard-2026-10-q3c/plan.md
research_source: output/ai-scorecard-2026-10-q3c/research.md
draft_source: output/ai-scorecard-2026-10-q3c/draft.md
results_hash: 71225356f89c3f3189e40f127626f1d57694660536061e95261a33af64b42a92
draft_hash: 419fd88090370c9e4ae1df9a23427281727af980e14912cdd4d42aee3c4835a3
review_type: separate-session-4way
review_execution: separate_subagent_sessions
reviewers:
  - "fact-sources: fact-checker (claude-q3c-review-2026-10-27) (pass)"
  - "financial-calc: general-purpose (재무 계산 영역, 별도 세션) (pass)"
  - "rule-consistency: Claude(general-purpose, Opus) 규칙 일관성 리뷰어. 판단 세션과 별개 세션이다. (pass)"
  - "output-readability: report-designer (claude-q3c-review-2026-10-27) (pass)"
---
# 리뷰 — 2026-10 실적 반영 실행 (Anthropic S-1 공개 제출)

각 영역은 가능하면 독립 세션에서 검토하고 실제 수행자·결과를 남긴다. 수행하지 않은 검토를 pass 로 표시하지 않는다.

## 검토 영역

| 영역 | 검토 대상 | 검토자 | 결과 | 요약 |
| --- | --- | --- | --- | --- |
| 사실·출처 | 숫자·기업 귀속·기준 시점·공시·뉴스·부재 주장 | fact-checker (claude-q3c-review-2026-10-27) | pass | 결과는 pass 이다. 이번 실행에서 새로 확정한 근거 63건(anthropic 173~229, alphabet 126·127, amazon 108·109, microsoft 108, spacex-xai 140), 새 관측 22건, anthropic 판단 아홉 항목과 타사 10건의 새 근거 인용 줄, 트리거(anthropic 이월 16건·새 6건)를 점검했다. 점수·순위·체크리스트 판정을 바꾸는 발견은 없다. 아래 발견 10건은 모두 낮음이며 확인을 막지 않고 「다음 실행 과제」로 넘긴다. |
| 재무 계산 | EPS·환율·ADR·TTM·FCF·런웨이·약정·단위·부호 | general-purpose (재무 계산 영역, 별도 세션) | pass | 결과는 pass 다. Anthropic 새 관측 22건의 숫자·단위·부호·기간은 S-1 재무제표 원문과 전부 일치하고, ⑥ −11(곡선값 −10.988)·⑧ −12·⑨ −16 의 계산 경로를 규칙 JSON(`scorecard/rules/v3.1.json`)의 곡선과 `scripts/scorecard/calc_f6_params.py`·`calc_f9.py` 에서 손으로 다시 따라가 같은 값을 얻었다. 14개사 가격은 기준일·통화·주식 기준이 맞고, 타사 ⑦ 판단의 비율 네 개(Alphabet 3.5%, Amazon 1.4%, Microsoft 2.1%, SpaceX 116%)도 관측값으로 다시 계산해 같았다. |
| 규칙 일관성 | factor 정의·상하한·예외·중복 속성·정성 승계·전 기업 동일 기준 | Claude(general-purpose, Opus) 규칙 일관성 리뷰어. 판단 세션과 별개 세션이다. | pass | 범위: 갱신 회사 Anthropic 의 ①~⑨(층·사업 판단 포함)와 범위에 든 타사 10건(alphabet ⑤⑦⑧, amazon ⑤⑦⑧, microsoft ⑤⑧, spacex-xai ⑦⑧). 범위 밖은 `diff`(1층·2층 통과)로 갈음했고 다시 읽지 않았다. 수정 묶음 반영 뒤 확인 리뷰(Claude(general-purpose, Opus) 확인 리뷰어. 1차 리뷰 네 영역과 판단 세션과는 다른 세션이다.)가 pass 로 확인했다. |
| 출력·가독성 | 표·카드·근거·차트·이력 일치, 낡은 비교 문장, 모바일·단일 HTML | report-designer (claude-q3c-review-2026-10-27) | pass | 결과는 pass 다. 점수·순위·체크리스트 판정을 바꾸는 발견은 없다. 다만 점수에 닿지 않는 내용 모순이 셋 있다(F1~F3, 트리거 문장). 확인 전에 트리거를 고칠 수 있으면 고치고, 아니면 다음 실행 과제로 넘긴다. |

결과는 pass / needs_fix / blocked 중 하나. 네 영역이 모두 pass 이고 체크리스트에 fail 이 없을 때만 frontmatter `status: pass`.
**승계 판단 예외(AGENTS.md 리뷰 범위 · 기업 추가 실행에만, rules.md 2.9)** — 정기 실행에서는 체크리스트 fail 이 하나라도 있으면 `status: pass` 가 아니다. 기업 추가 실행에서는 체크리스트 fail 의 사유가 `carried_score` 로 승계한 판단의 기존 논리이고, 이번 실행이 그 판단에 쓰인 잣대를 바꾸지 않았으며, 규칙 파일 `open_tensions` 에 재검토 시점과 함께 등록됐다면 `status: pass` 를 막지 않는다. 이때 해당 fail 과 **긴장 번호**(예: `TEN-RC-02`)를 근거 칸에 그대로 적는다. 이번 실행이 바꾼 잣대가 닿는 승계 판단은 이 예외가 아니다 — 한 회사에 새 잣대를 댔으면 같은 잣대가 닿는 모든 회사에 대야 한다(Q03).

## 체크리스트

| ID | 검사 초점 | 결과 | 근거 |
| --- | --- | --- | --- |
| Q01 | 이 감점, 다른 칸에서 이미 셌나? | pass | 수정은 칸 사이 이동이 없다. 국방부 전선은 ⑤ 에만, 해외 매출·대만 집중은 ⑧ 지정학에만, Broadcom 리스는 ⑧ 약정에만 있다. |
| Q02 | 이 지표가 이 칸의 정의에 맞나? | pass | 규칙 리뷰의 fail 이 풀렸다. ⑥ 이 C-12 성장 조정 경로(실측 보정 매출과 공시 합계로 가둔 전년값)를 탔다. P/S 와 성장의 창이 다르지만 어느 창으로 맞춰도 −8 이라 판정이 바뀌지 않는다(발견 1). 다른 항목의 지표 정의는 1차 리뷰대로 맞다. |
| Q03 | 회사마다 같은 잣대인가? | pass | 사건 교차표의 갈린 줄은 관계 종류 차이이고, Cursor 전선과 ⑥ 성장 경로는 자료 유무 차이지만 미확인 쪽(OpenAI)이 감점 쪽으로 해소됐다(규칙 리뷰 긴장 절, 발견 6). OpenAI ⑤⑦ 문장은 범위에 넣어 현재 상태로 다시 썼다. Amazon 7.9% 수정은 판정(작음)을 바꾸지 않는다. |
| Q04 | 시총 크기를 밸류에이션으로 착각했나? | pass | ⑥ 은 P/S 와 성장으로 쟀고 시가총액 크기를 쓰지 않았다. |
| Q05 | 출처가 이해당사자인가? | pass | 결정적 사실은 S-1 공시와 상대방 제출본이다. 출처의 이해상충 표기는 보지 않았다(AGENTS.md). |
| Q06 | 볼륨인가 가치인가? | pass | 수정이 볼륨 지표를 가치로 읽은 줄을 만들지 않았다. |
| Q07 | "안 만든 것"을 카운터 포지셔닝으로 셌나? | pass | Anthropic ③ 수익 모델 0 그대로다. |
| Q08 | 적대세력을 수로 셌나, 성격으로 셌나? | pass | 국방부 전선의 비용형 근거가 금액에서 관계의 종류로 바뀌어 성격으로 세는 원칙에 더 맞다. |
| Q09 | 미래 계획을 현재 점수에 넣었나? | pass | FTC 임원 증언 요구는 처분이 아니라 구제 조치로 세지 않았고, 3분기·공모 조건 빈칸은 값으로 쓰지 않았다. |
| Q10 | 거리를 가속도로 착각했나? | pass | ③ 가속도는 1년 전 대비 비(0.828)로 쟀다. ⑥ 성장은 가속도가 아니라 성장률이다. |
| Q11 | 순적자를 실격 사유로 썼나? | pass | ⑨ −16 은 손실 곡선 결과이고 실격이 아니다. |
| Q12 | ③ 세 기준을 동등하게 쟀나? | pass | Anthropic ③ 0 이다. |
| Q13 | "공짜로 뿌린다"를 곧바로 카운터 포지셔닝으로 셌나? | pass | 공짜 배포 전략 점수가 없다. |
| Q14 | 아직 안 끝난 승부를 끝난 것처럼 쟀나? | pass | 문 닫힘 판정이 없다. |
| Q15 | ⑤에서 "공짜 사용자"를 아군으로 셌나? | pass | ⑤ A 는 Amazon·Google 지분 동맹만 셌다. |
| Q16 | ①을 사업마다, ②③을 층마다 나눠 쟀나? | pass | ① 사업 단위, ②③ 층 단위가 그대로다. |
| Q17 | ②를 "표준 없음"만으로 깎았나? | pass | ② 세 경로 판정이 그대로다. |
| Q18 | ⑤에서 관계사를 독립 동맹으로 셌나? | pass | 관계사를 동맹으로 센 칸이 없다. |
| Q19 | ⑤에서 "받은 투자"를 곧바로 지분 동맹으로 셌나? | pass | 받은 투자는 묶임 증거가 있는 Amazon·Google 만 셌다. |
| Q20 | 조달을 동맹으로 셌나? | pass | 조달을 동맹으로 센 칸이 없다. |
| Q21 | 동맹이자 의존인 관계를 한쪽에서만 셌나, 또는 같은 속성을 양쪽에서 셌나? | pass | Amazon·Google 은 ⑤ 와 ⑧ 에서 다른 속성으로 세졌다. |
| Q22 | 지분 평가이익을 ⑦ 순환금융 증거로 셌나? | pass | ⑦ 은 지분 평가이익이 아니라 매출 몫으로 쟀다. |
| Q23 | 벤치마크를 서로 다른 하네스끼리 비교했나? | pass | 벤치마크 판 교차 비교가 점수에 닿지 않는다. |
| Q24 | 끝난 싸움을 ② 표준 선점·③·⑤ 적대에 셌나? | pass | FTC 조사는 증언 요구 단계로 진행 중이고, 끝난 사건을 센 칸이 없다. |
| Q25 | 매출 몫이 없는 층의 강점을 옮겨 셀 때 원칙을 지켰나? | pass | 모델 순위를 다른 층으로 옮기지 않았다. |

결과는 pass / fail / not_applicable. not_applicable 도 근거가 필요하다.

## 발견 사항

- 1차 리뷰 네 영역의 발견과 수정 묶음, 확인 리뷰 결과는 `review-parts/` 의 다섯 파일에 있다. 결론은 pass 다. 수정 묶음의 항목이 모두 실제 입력 파일(observations·evidence·triggers·judgments)과 산출물(results·draft·preview)에 반영됐다. 점수·순위·체크리스트 판정을 바꾸는 발견은 남지 않았다. 규칙 리뷰의 Q02 fail 은 풀렸다.

- 확인 리뷰(pass) 뒤 조율자가 점수와 무관한 문장 셋을 고치고 기계로 대조했다. `anthropic.ps_ratio.2026-09-30.q3c` 관측의 성장 보정 설명, TRG-036 carry 의 Reuters 원문 표기(EV-anthropic-228 로 확정), OpenAI ⑦ 판정 칸의 기준일(2026-10-27). 그 뒤 research → calculate → draft 를 다시 돌렸고 점수·순위는 확인 리뷰 때와 같으며 `diff --against ai-scorecard-2026-10-q3b` 1층·2층 통과다.
- 사용자 결정 안건(확인 전에 볼 것): ⑤⑦ 의 Cursor 전선을 Anthropic 공개 제출본으로 풀고 OpenAI 는 미확인에 둔 읽기(AGENTS.md 2026-10-09 문장과의 긴장, Q03 pass 근거는 review-parts/rules.md), ③ 가속도의 1년 전 대비 기준과 2차 보도 3분기 값 사용(공시값만 쓰면 ③ 6), ⑥ 성장 보정 입력의 범위 추정(공시 합계로 가둔 2024년 3분기), ③ '자료 없음 2.4 대 측정 감속 0' 역전.

## 판정

- results_hash `71225356f89c3f31…` · draft_hash `419fd88090370c9e…` 기준 검토. 자료·규칙·판단·초안이 바뀌면 이 리뷰는 무효다(D-10).
- **두 해시의 뜻이 다르다.** `results_hash` 는 `results.json` 에서 `results_hash` 키를 뺀 내용의 정렬 JSON 해시이고(`engine.sha256_obj`) **파일 바이트 sha256 과 다르다.** `draft_hash` 는 초안 **파일 바이트 sha256** 이다. 대조할 때 섞지 않는다.
