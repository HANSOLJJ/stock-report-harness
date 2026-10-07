---
reviewer_agent: general-purpose (규칙 일관성)
session: rc-rescore-20261007-r7
reviewed_at: 2026-10-07
round: 7
---
# rule-consistency — 규칙 일관성
검토자: Claude Opus 5.5 · 규칙 일관성 독립 세션(이 실행을 만든 세션 아님) · 2026-10-07 · 완결된 문장 재작성 뒤 1차 · 확인 리뷰 · 좁은 확인 · 근거 세 칸 재분류 뒤 · 확인 리뷰
결과: pass
요약: 1차(round 6) needs_fix 두 건이 모두 닫혔다.<br>• **N1 tsmc.F9:** 설비투자 가이던스 상향이 내릴 근거로 옮겨졌고, "가이던스는 계획이라 추세 판정의 근거로 쓰지 않는다" 단서가 같은 줄에 붙었다. microsoft.F9 의 계획 하향 줄과 같은 잣대다. FCF 흑자는 올릴 근거 둘째 줄(+$36.5B)에 남아 사실이 빠지지 않았다.<br>• **N2 신용 지표 줄:** oracle.F8·openai.F7 의 신용 교차검증 줄이 판정 칸으로 갔다. oracle.F9 는 추가 조달 예고(계획, 올릴 근거)와 신용등급 조달 여력(판정 칸)으로 나뉘었다. 이제 신용 지표 문장은 세 판단 모두 판정 칸에 있어 amazon.F9 와 같은 칸이고, 규칙 2.8 과 맞다.<br>• **수정이 만든 새 문제:** 없다. 수정 묶음이 고친 판단은 다섯 개(tsmc.F9·oracle.F8·oracle.F9·openai.F7·alphabet.F5)이고, 다섯 모두 kind·score·inputs 가 수정 전과 같다. 판정 칸이 빈 판단과 두 방향 칸이 함께 빈 판단은 0이다. alphabet.F5 는 직원 반발 사실을 내릴 근거에 두고 "내부 갈등이지 시장의 적대가 아니다" 는 결론을 판정 칸에 두었다. guide 5.6 「판정 + 이유」 분리와 amazon.F1 처리 방식에 맞다.<br>• **결과:** 점수·순위는 round 6 과 같고, 체크리스트 판정도 바뀌지 않았다. 다음 실행 과제 34건은 그대로 남는다.

검토 기준: results_hash `59518fa18f928802…`, draft_hash `cb819da1aab10ac6…`. review.md frontmatter 와 같은 값이다. results_hash 는 results.json 에서, 초안 sha256 은 파일에서 이 세션이 다시 계산했다.

확인한 것:
- 수정 다섯 판단의 세 칸 전 줄과 수정 이력(PRP-259~263). 각 이력의 `previous` 와 kind·score·inputs 를 대조했다.
- 수정 묶음 밖 판단이 움직이지 않았다는 것. 2026-10-07 세 칸 분할 뒤 새 이력이 붙은 판단은 위 다섯뿐이다.
- 114개 형식: 판정 칸이 빈 판단 0, 두 방향 칸이 함께 빈 판단 0.
- results 순위: alphabet·amazon 15 공동 1위, meta·microsoft 13 공동 3위, tsmc 11, anthropic·nvidia·spacex-xai 9 공동 6위, apple 8, palantir 6, alibaba 5, oracle·tesla 4 공동 12위, openai 3 14위. round 6 과 같다.

## 발견
1차 needs_fix 의 처리:

| 1차 발견 | 상태 | 확인 내용 |
| --- | --- | --- |
| medium · N1 tsmc.F9 가이던스 상향이 올릴 근거에 있음 | **닫힘** | 올릴 근거는 영업이익률 56.1%·FCF +$36.5B 두 줄이다. 내릴 근거는 "2026년 설비투자 가이던스를 $60~64B 로 약 $10B 올렸다. 가이던스는 계획이라 추세 판정의 근거로 쓰지 않는다." 한 줄이다. 계획 단서가 같은 줄에 있어 guide 5.6 계획 행대로이고, microsoft.F9 올릴 근거 셋째 줄과 같은 잣대다. 판정(추세 안정, 0점)은 그대로다 |
| medium · N2 신용 지표 줄이 방향 칸에 있음(oracle.F8·openai.F7·oracle.F9) | **닫힘** | • oracle.F8: 신용 교차검증 줄이 판정 둘째 줄이 됐다. 내릴 근거 3줄과 올릴 근거 1줄이 남는다.<br>• openai.F7: S&P 강등 줄이 판정 다섯째 줄이 됐다. 올릴·내릴 근거가 각 1줄 남는다.<br>• oracle.F9: 올릴 근거 둘째 줄은 "회사는 2026년 $45~50B 추가 조달을 예고했으나, 계획이라 완충에 넣지 않는다." 이고 alibaba.F9 증자 줄과 같은 배치다. 판정 일곱째 줄은 "신용등급(BBB-)으로 추정한 조달 여력은 완충에 넣지 않는다." 이고 amazon.F9 판정 넷째 줄과 같은 칸이다.<br>• 방향 칸에 신용등급·CDS 가 남은 판단은 없다 |

수정 묶음에서 새로 본 것:

| 등급 | 위치 | 확인 | 점수 영향 |
| --- | --- | --- | --- |
| — | alphabet.F5 내릴 근거 첫째 줄 · 판정 넷째 줄 | 이 판단은 사실·출처 영역의 지적으로 고쳐졌다. 직원 반발 사실은 적대 쪽(H)을 깊게 보이게 하는 사실이라 내릴 근거가 맞다. 그것을 시장의 적대로 세지 않는다는 결론은 판정 칸에 있다. 규칙 ⑤ "적대는 성격으로 본다" 와 맞고, H −1 은 그대로다. 반발 대상 셋이 원문과 맞는지는 사실·출처 영역 몫이다 | 없음 |

새 needs_fix 는 없다.

## 체크리스트
round 6 표를 이어 싣는다. 판정 재료는 그대로이고, 수정 묶음은 근거 칸 배치만 바꿨다. 「세 칸」 문장 가운데 N1·N2 에 걸린 곳은 닫혔다고 고쳐 적었다.

| ID | 결과 | 근거 |
| --- | --- | --- |
| Q01 | fail | **승계 판단 예외 — TEN-RC-05 · TEN-RC3-04** |
| Q02 | fail | **승계 판단 예외 — TEN-RC-02 · TEN-RC3-01 · TEN-RC3-03 · TEN-RC3-05 · TEN-RC4-02**<br>• 세 칸: N2 의 신용 지표 줄 셋이 판정 칸으로 옮겨져 규칙 2.8 과 맞다(닫힘).<br>• 세 칸: spacex-xai.F4 올릴 근거의 상장 조달액·현금은 ④ 지표가 아니다(다음 실행 과제) |
| Q03 | fail | **승계 판단 예외 — TEN-RC-03(nvidia.F5 포함) · TEN-RC4-03.** 예외 없는 fail 은 없다. 이번 실행이 새로 댄 잣대 셋이 닿는 회사는 모두 다시 판정됐다.<br>• ④ 출하만: tesla·openai.<br>• FCF 추세: microsoft 를 다시 판정했다. apple·nvidia·palantir·tsmc 는 실측으로 재도 안정이다.<br>• ⑥ 트랙: tsmc·alibaba.<br>• oracle.F5 는 기존 +2 조건을 확인된 사실에 대 +1 이다.<br>• 세 칸: 설비투자 계획(tsmc ↔ microsoft)과 신용 지표(oracle·openai ↔ amazon)는 같은 칸으로 맞춰졌다(N1·N2 닫힘). 점수에 닿지 않는 갈림(⑤ 공짜 사용자·조달 제외 줄, ⑦ 비고객 평가이익)은 다음 실행 과제다 |
| Q04 | pass | ⑥ 은 비율 잣대이고 변경이 없다 |
| Q05 | fail | **승계 판단 예외 — TEN-RA-02(nvidia F2).** openai.F4 는 이해당사자 발표를 점수 근거에서 뺐다. 이해상충 표기는 판정에 넣지 않았다 |
| Q06 | pass | 볼륨 지표가 점수 재료로 든 곳이 없다 |
| Q07 | pass | amazon.F3 문장 그대로다. 세 칸에서도 "모델을 직접 만들지 않은 것 자체는 카운터 포지셔닝이 아니다" 가 판정 칸에 있다 |
| Q08 | fail | **승계 판단 예외 — TEN-RC4-03.** alphabet.F5 의 직원 반발은 수로 세지 않고 성격(내부 갈등)으로 판정 칸에서 거른다 |
| Q09 | fail | **승계 판단 예외 — TEN-RA-02 · TEN-RA6-01.**<br>• openai.F4·tesla.F4·microsoft.F9 는 계획을 점수 근거에서 뺐다.<br>• spacex-xai.F4 의 Terafab 과 tsmc.F4 의 로드맵·투자액 서술은 점수를 정하지 않아 low 로 적었다.<br>• 세 칸: tsmc.F9 가이던스 상향은 내릴 근거로 옮겨지고 단서가 붙었다(N1 닫힘). 단서가 다른 줄에 있거나 없는 계획 줄(tesla.F2, meta.F9, tsmc.F2·F3, spacex-xai.F3)은 점수를 정하지 않아 다음 실행 과제다 |
| Q10 | fail | **승계 판단 예외 — TEN-RB-Q10 · TEN-RC4-04.** 세 칸: alphabet.F3 의 "2년 만에 격차 회수" 와 anthropic.F3 의 "$9B → $65B" 는 거리라서 가속도 근거에서 뺀다는 문장으로 남았다 |
| Q11 | pass | ⑨ 게이트 경로로 계산하고, 순적자 실격은 없다 |
| Q12 | fail | **승계 판단 예외 — TEN-RC4-01 · TEN-RC3-05.** nvidia.F3 은 규칙 정의(직전 분기 대비)로 잰다. 세 칸에서 직전 분기 대비 감속은 내릴 근거, 전년 대비 가속은 올릴 근거로 갈렸고, 판정 칸이 고른 지표를 적는다 |
| Q13 | fail | **승계 판단 예외 — TEN-RC3-05** |
| Q14 | pass | 14사 door_closed 가 전부 fail 이다 |
| Q15 | pass | 공짜 사용자를 동맹으로 세지 않는다. 세 칸: 제외 문장의 칸이 alibaba.F5(내릴 근거)와 meta.F5·nvidia.F5(판정)로 갈린다(다음 실행 과제) |
| Q16 | fail | **승계 판단 예외 — TEN-RC-02 · TEN-RC4-02** |
| Q17 | pass | 변경 없음 |
| Q18 | pass | 관계사 처리가 같다. tesla.F4 는 관계사 합작 Terafab 을 배치 전이라 뺐다 |
| Q19 | fail | **승계 판단 예외 — TEN-RC-03(nvidia.F5).** 받은 투자를 A 에서 빼는 처리는 일관된다. 준 지분 투자를 동맹으로 셀지는 이탈 조건 통일(C-08)과 함께 2026-11 에 재검토한다 |
| Q20 | fail | **승계 판단 예외 — TEN-RC-03(C-08)** |
| Q21 | fail | **승계 판단 예외 — TEN-RC-05 · TEN-RC3-04** |
| Q22 | pass | ⑦ 입력에 평가이익이 없다. 세 칸: amazon·nvidia F7 은 고객사 출처 평가이익을 "입력에 넣지 않는다" 단서와 함께 내릴 근거에 방증으로 두어 규칙 ⑦ 문언대로다. alphabet.F7 의 비고객(SpaceX) 평가이익 줄은 올릴 근거에 있어 판정 칸으로 옮기는 것이 맞다(다음 실행 과제) |
| Q23 | fail | **승계 판단 예외 — TEN-RA4-01** |

fail 14건(Q01·02·03·05·08·09·10·12·13·16·19·20·21·23)은 모두 승계 판단 예외다. 인용한 긴장 15개(TEN-RC-02·RC-03·RC-05·RB-Q10·RA-02·RC3-01·RC3-03·RC3-04·RC3-05·RC4-01·RC4-02·RC4-03·RC4-04·RA4-01·RA6-01)는 규칙 v1.9 에서 모두 `status: open`, `recheck_at: 2026-11` 이다. 수정 묶음은 규칙 파일을 건드리지 않았다. TEN-RA3-01 은 닫을 대상으로 남는다.

## 다음 실행 과제
round 6 의 34건을 그대로 이어받는다. 수정 묶음은 이 과제들을 다루지 않았고, 새로 더할 것도 없다. 목록은 아래 「round 6」 기록의 다음 실행 과제 절에 있다(세 칸 분류 6건, round 5 에서 넘어온 6건, 확인 리뷰에서 넘어온 22건).

## 이전 리뷰 기록

### 근거 세 칸 재분류 뒤 1차(round 6) · rule-consistency — 규칙 일관성
round 6 검토자: Claude Opus 5.5 · 규칙 일관성 독립 세션(이 실행을 만든 세션 아님) · 2026-10-07 · 완결된 문장 재작성 뒤 1차 · 확인 리뷰 · 좁은 확인 · 근거 세 칸 재분류 뒤
round 6 결과: needs_fix
round 6 요약: 판단 114개의 판정·올릴 근거·내릴 근거를 전부 읽었다. 문장마다 판정 재료(③ 세 기준·⑤ A·H·⑦ 두 축·⑨ gate_inputs·①②④⑥⑧ 점수)와 규칙 문언에 대 방향을 확인했다. 판정 재료·점수·순위는 하나도 바뀌지 않았다. 114개 모두 kind·score·inputs 가 `revision_history[-1].previous` 와 같다.<br>• **needs_fix 두 건(줄 넷).** 둘 다 점수를 바꾸지 않는다. 다만 카드에서 독자가 "이 사실이 점수를 올리나 내리나" 로 읽는 자리에 틀린 방향이나 판정 문장이 놓였다.<br>• **(N1) tsmc.F9:** 올릴 근거 셋째 줄이 설비투자 가이던스 상향과 FCF 흑자를 한 줄로 묶었다. 가이던스 상향은 FCF 추세를 악화 쪽으로 미는 계획이다. microsoft.F9 는 같은 유형인 설비투자 계획 하향을 올릴 근거에 두고 "계획은 추세 판정에 쓰지 않는다" 를 같은 줄에 단다. 따라서 tsmc 의 상향은 내릴 근거로 가야 한다.<br>• **(N2) 신용 지표 줄:** 규칙 2.8 은 신용등급·CDS 를 어느 항목의 입력으로도 쓰지 않고 함정 총점의 교차검증에만 쓴다. 그런데 oracle.F8 은 S&P 강등·CDS 확대를 "깊은 감점과 방향이 맞다" 는 검증 결론과 함께 내릴 근거에 두었다. openai.F7 도 같은 S&P 강등을 내릴 근거에 두었다. oracle.F9 올릴 근거 둘째 줄의 "신용등급으로 추정한 조달 여력" 도 같은 유형인데, amazon.F9 는 같은 문장을 판정 칸에 둔다.<br>• **지목된 메모 일곱 줄:** tsmc.F9 는 N1, oracle.F8·oracle.F9 는 N2 다. anthropic·openai F6 의 밸류÷ARR 배수는 규칙이 "근거로만 남긴다" 고 정한 값이라, 단서와 함께 올릴 근거에 두는 지금 배치가 방향에 맞고 두 회사가 같다. amazon.F9 여신 구성 줄은 완충을 줄이는 제약이라 내릴 근거가 맞다. alphabet.F7 SpaceX 평가이익 줄과 tesla.F2 계획 줄은 방향이 틀리지 않아 다음 실행 과제로 적었다.<br>• **체크리스트:** 판정 재료가 그대로라 round 5 판정을 이어받는다. fail 14건은 모두 승계 판단 예외이고, 인용한 긴장 15개는 모두 open·2026-11 이다. 세 칸 분류로 드러난 것은 Q02·Q03·Q09·Q15·Q22 근거 칸에 덧붙였고, 판정을 바꾸는 것은 없다.

round 6 검토 기준: results_hash `07814146bc1e8401…`, draft_hash `9461bade7e987939…`. review.md frontmatter 와 같은 값이다. results_hash 는 results.json 에서, 초안 sha256 은 파일에서 이 세션이 다시 계산했다.

확인한 것:
- `judgments.json` 114개의 세 칸 전 줄. 점수가 자동 산출인 판단은 results 의 factor 점수·calc 와 맞춰 읽었다.
- 형식 대조(스크립트): kind·score·inputs 변경 0, 판정 칸이 빈 판단 0, 두 방향 칸이 함께 빈 판단 0, counter_evidence 가 남은 판단 0. 방향 칸의 점수 표기는 지시서가 허용한 meta.F2 AA 지수 점수 세 줄뿐이다.
- 지목된 메모 일곱 줄은 `previous.evidence` 원문과 대조했다.
- 같은 유형 사실의 칸 배치를 회사 사이로 대 보았다. 대상은 ⑨ 설비투자 계획, 신용 지표, ⑦ 지분 평가이익, 규칙상 세지 않는 사실(공짜 사용자·조달·계획·미측정 발표), ⑥ 밸류÷ARR 이다.
- results 순위: alphabet·amazon 15 공동 1위, meta·microsoft 13 공동 3위, tsmc 11, anthropic·nvidia·spacex-xai 9 공동 6위, apple 8, palantir 6, alibaba 5, oracle·tesla 4 공동 12위, openai 3 14위. round 5 와 같다.
- 규칙 v1.9 `open_tensions` 에서 인용 긴장 15개와 TEN-RA3-01 의 상태·재검토 시점.

#### 발견
needs_fix(이번 실행의 목적인 근거 분류를 해치는 것):

| 등급 | 판단 · 칸 | 문장 앞부분 | 문제 | 고칠 방향 |
| --- | --- | --- | --- | --- |
| **medium · needs_fix (N1)** | tsmc.F9 · 올릴 근거 3번째 줄 | "2026년 설비투자 가이던스를 $60~64B 로 약 $10B 올렸는데도 FCF 는 흑자다." | **방향이 섞였다.** 한 줄에 반대 방향 사실 둘이 묶였다(guide 5.6 「한 사실이 양쪽으로 읽힘」).<br>• 설비투자 가이던스 상향은 FCF 추세를 악화 쪽으로 미는 계획이라 내릴 근거다.<br>• 앞부분 "FCF 흑자" 는 올릴 근거 둘째 줄(+$36.5B)과 같은 사실이다.<br>• microsoft.F9 는 설비투자 계획 하향을 올릴 근거에 두고 "계획은 … 추세 판정의 근거로 쓰지 않는다" 를 같은 줄에 단다. 같은 유형을 같은 잣대로 두어야 한다(Q03 원칙) | 이 줄을 올릴 근거에서 빼고 내릴 근거에 "2026년 설비투자 가이던스를 $60~64B 로 약 $10B 올렸다. 가이던스는 계획이라 추세 판정의 근거로 쓰지 않는다." 로 넣는다. FCF 흑자는 올릴 근거 둘째 줄에 이미 있어 사실이 빠지지 않는다. 판정(추세 안정, 0점)은 그대로다 |
| **medium · needs_fix (N2)** | oracle.F8 · 내릴 근거 4번째 줄<br>openai.F7 · 내릴 근거 2번째 줄<br>oracle.F9 · 올릴 근거 2번째 줄 뒷부분 | "신용 지표는 점수 입력이 아니라 교차검증에만 쓰는데(규칙 2.8), S&P 가 2026-07-09 …"<br>"신용 교차검증으로는 S&P 가 7/9 Oracle 을 …"<br>"… 신용등급(BBB-)으로 추정한 조달 여력도 있으나 …" | **판정 칸 문장이 방향 칸에 있다.** 규칙 2.8 은 신용등급·CDS 를 어느 항목의 입력으로도 쓰지 않고 함정 총점의 교차검증에만 쓴다.<br>• guide 5.6 의 물음("이 사실 하나로 점수가 오르나 내리나")에 규칙이 "어느 쪽도 아니다" 로 답하므로 판정 칸이다.<br>• oracle.F8 줄은 끝이 "깊은 감점과 방향이 맞다" 는 검증 결론이다.<br>• ⑨ 의 신용등급 조달 여력은 규칙 ⑨ 「쓰지 말 것」 항목이다. amazon.F9 는 같은 문장("신용등급으로 추정한 조달 여력은 완충에 넣지 않는다")을 판정 칸에 둔다 | • oracle.F8·openai.F7 의 두 줄은 문장 그대로 판정 칸 끝으로 옮긴다.<br>• oracle.F9 올릴 근거 둘째 줄은 둘로 나눈다. 올릴 근거에는 "회사는 2026년 $45~50B 추가 조달을 예고했으나, 계획이라 완충에 넣지 않는다." 를 남긴다(alibaba.F9 의 $10.2B 증자 줄과 같은 배치). 판정 칸에는 "신용등급(BBB-)으로 추정한 조달 여력은 완충에 넣지 않는다." 를 더한다.<br>• 옮긴 뒤에도 세 판단 모두 방향 칸이 남는다(oracle.F8 내릴 근거 3줄, openai.F7 올릴·내릴 근거 각 1줄, oracle.F9 올릴 근거 3줄) |

지목된 판단 메모 일곱 줄의 판정:

| 메모 | 판정 | 이유 |
| --- | --- | --- |
| tsmc.F9 넷째 줄(가이던스 상향 + FCF 흑자) | needs_fix (N1) | 위 표 |
| oracle.F8 신용 지표 줄 | needs_fix (N2) | 위 표 |
| anthropic.F6 · openai.F6 밸류÷ARR 배수 | 현행 유지 | • 규칙 ⑥ 비상장은 "밸류 ÷ ARR 은 근거로만 남긴다" 고 정한다.<br>• 이 배수(14.8배·21.3배)는 점수 배수(약 30~39배·약 39배)보다 싸 보이게 하는 사실이라, 단서와 함께 올릴 근거에 두는 배치가 방향에 맞다. 두 회사가 같은 칸이다.<br>• 자본효율도 값대로 갈렸다(anthropic 0.52 올릴 근거, openai 0.22 내릴 근거).<br>• 판단 항목은 계산에 쓰이지 않고 점수(둘 다 −4)는 프로그램 값이다 |
| alphabet.F7 SpaceX 지분 평가이익 | 다음 실행 과제 | • 방향이 뒤집히지는 않았다. 큰 평가이익이 고객사에서 오지 않았다는 사실은 함정을 깊게 하지 않는다.<br>• 다만 규칙 ⑦ 은 평가이익을 출처가 고객사일 때만 근거란에 방증으로 적는다. 고객사 출처인 amazon.F7·nvidia.F7 은 내릴 근거에 방증으로 둔다. 고객사가 아닌 영업외 비중을 적은 tsmc·apple·alibaba F7 은 판정 칸에 둔다.<br>• alphabet 의 SpaceX 줄은 뒤쪽 유형이라 판정 칸 넷째 줄 옆이 맞다 |
| amazon.F9 여신 구성 줄 | 현행 유지 | • 364일 리볼빙 연장의 대주단 승인 요건과 지연인출 약정의 자동 소멸은 완충을 줄이는 쪽의 사실이라 내릴 근거가 맞다. 셋째 줄(시한 종료)과 같은 방향이다.<br>• 여신을 모두 빼도 런웨이 6.7년이라 게이트 3 결론은 같고, 판정 칸 다섯째 줄이 그렇게 적는다 |
| oracle.F9 추가 조달 계획 줄 | 계획 부분 현행 유지 · 신용등급 부분 needs_fix (N2) | $45~50B 예고는 완충을 늘리는 쪽의 계획이고, "완충에 넣지 않는다" 단서가 같은 줄에 있어 guide 5.6 계획 행대로다. alibaba.F9 의 증자 줄과 같은 배치다 |
| tesla.F2 계획 줄 | 다음 실행 과제 | • AI5·Optimus·Terafab 은 ② 를 올리는 쪽 사실이라 올릴 근거가 맞다.<br>• 그러나 "계획이라 점수에 넣지 않는다" 단서가 같은 줄이 아니라 판정 넷째 줄에 있다. 카드의 올릴 근거 상자만 읽으면 점수 근거처럼 보인다. guide 5.6 계획 행은 단서를 같은 줄에 둔다 |

판단 114개에서 방향이 뒤집힌 줄은 N1 하나다. 함정 항목(⑥⑦⑧⑨)은 올릴 근거가 함정이 얕다는 사실, 내릴 근거가 깊다는 사실인지 먼저 보았고, N1·N2 밖에서는 어긋난 곳이 없다. 원문에 없던 사실이나 판정을 바꾸는 사실 배치도 찾지 못했다. 점수에 닿지 않고 분류가 갈릴 수 있는 줄은 다음 실행 과제에 적었다.

#### 체크리스트
승계 판단 예외는 round 5 와 같은 조건(fail 사유가 승계 판단의 기존 논리, 이번 실행이 그 잣대를 바꾸지 않음, `open_tensions` 에 recheck_at 2026-11 로 등록)에서 적었다. 이번 실행이 새로 댄 잣대는 ⑥ 트랙·최근 1년 창·여신, ④ 출하·실제 배포만, 분기 실측 FCF 추세다. 세 칸 분류는 판정 재료를 바꾸지 않아 결과를 이어받는다. 세 칸 분류로 드러난 것은 근거 칸 끝에 「세 칸」 으로 시작하는 문장으로 덧붙였다.

| ID | 결과 | 근거 |
| --- | --- | --- |
| Q01 | fail | **승계 판단 예외 — TEN-RC-05 · TEN-RC3-04** |
| Q02 | fail | **승계 판단 예외 — TEN-RC-02 · TEN-RC3-01 · TEN-RC3-03 · TEN-RC3-05 · TEN-RC4-02**<br>• 세 칸: N2 의 신용 지표 줄 셋은 규칙 2.8 상 어느 항목의 지표도 아닌데 방향 칸에 놓였다. 점수 입력은 아니다(oracle ⑧ −4·openai ⑦ −1 은 사람 점수이고 oracle ⑨ 완충에 들지 않는다). 판정은 바뀌지 않고 N2 를 고치면 해소된다.<br>• 세 칸: spacex-xai.F4 올릴 근거의 상장 조달액·현금은 ④ 지표가 아니다(다음 실행 과제) |
| Q03 | fail | **승계 판단 예외 — TEN-RC-03(nvidia.F5 포함) · TEN-RC4-03.** 예외 없는 fail 은 없다. 이번 실행이 새로 댄 잣대 셋이 닿는 회사는 모두 다시 판정됐다.<br>• ④ 출하만: tesla·openai.<br>• FCF 추세: microsoft 를 다시 판정했다. apple·nvidia·palantir·tsmc 는 실측으로 재도 안정이다.<br>• ⑥ 트랙: tsmc·alibaba.<br>• oracle.F5 는 기존 +2 조건을 확인된 사실에 대 +1 이다.<br>• 세 칸: 같은 유형 사실의 칸이 회사마다 갈린 곳은 N1(설비투자 계획, tsmc ↔ microsoft)과 N2(신용 지표, oracle·openai ↔ amazon)다. 점수에 닿지 않는 갈림(⑤ 공짜 사용자·조달 제외 줄, ⑦ 비고객 평가이익)은 다음 실행 과제다 |
| Q04 | pass | ⑥ 은 비율 잣대이고 변경이 없다 |
| Q05 | fail | **승계 판단 예외 — TEN-RA-02(nvidia F2).** openai.F4 는 이해당사자 발표를 점수 근거에서 뺐다. 이해상충 표기는 판정에 넣지 않았다 |
| Q06 | pass | 볼륨 지표가 점수 재료로 든 곳이 없다 |
| Q07 | pass | amazon.F3 문장 그대로다. 세 칸에서도 "모델을 직접 만들지 않은 것 자체는 카운터 포지셔닝이 아니다" 가 판정 칸에 있다 |
| Q08 | fail | **승계 판단 예외 — TEN-RC4-03** |
| Q09 | fail | **승계 판단 예외 — TEN-RA-02 · TEN-RA6-01.**<br>• openai.F4·tesla.F4·microsoft.F9 는 계획을 점수 근거에서 뺐다.<br>• spacex-xai.F4 의 Terafab 과 tsmc.F4 의 로드맵·투자액 서술은 점수를 정하지 않아 low 로 적었다.<br>• 세 칸: 계획 줄 대부분은 "점수에 넣지 않는다" 단서를 같은 줄에 단다. tsmc.F9 가이던스 상향은 방향이 틀려 N1 이다. 단서가 다른 줄에 있거나 없는 계획 줄(tesla.F2, meta.F9, tsmc.F2·F3, spacex-xai.F3)은 점수를 정하지 않아 다음 실행 과제다 |
| Q10 | fail | **승계 판단 예외 — TEN-RB-Q10 · TEN-RC4-04.** 세 칸: alphabet.F3 의 "2년 만에 격차 회수" 와 anthropic.F3 의 "$9B → $65B" 는 거리라서 가속도 근거에서 뺀다는 문장으로 남았다 |
| Q11 | pass | ⑨ 게이트 경로로 계산하고, 순적자 실격은 없다 |
| Q12 | fail | **승계 판단 예외 — TEN-RC4-01 · TEN-RC3-05.** nvidia.F3 은 규칙 정의(직전 분기 대비)로 잰다. 세 칸에서 직전 분기 대비 감속은 내릴 근거, 전년 대비 가속은 올릴 근거로 갈렸고 판정 칸이 고른 지표를 적는다(guide 5.6 「지표끼리 결론이 갈림」) |
| Q13 | fail | **승계 판단 예외 — TEN-RC3-05** |
| Q14 | pass | 14사 door_closed 가 전부 fail 이다 |
| Q15 | pass | 공짜 사용자를 동맹으로 세지 않는다. 세 칸: 제외 문장의 칸이 alibaba.F5(내릴 근거)와 meta.F5·nvidia.F5(판정)로 갈린다(다음 실행 과제) |
| Q16 | fail | **승계 판단 예외 — TEN-RC-02 · TEN-RC4-02** |
| Q17 | pass | 변경 없음 |
| Q18 | pass | 관계사 처리가 같다. tesla.F4 는 관계사 합작 Terafab 을 배치 전이라 뺐다 |
| Q19 | fail | **승계 판단 예외 — TEN-RC-03(nvidia.F5).** 받은 투자를 A 에서 빼는 처리는 일관된다. 준 지분 투자를 동맹으로 셀지는 이탈 조건 통일(C-08)과 함께 2026-11 에 재검토한다 |
| Q20 | fail | **승계 판단 예외 — TEN-RC-03(C-08)** |
| Q21 | fail | **승계 판단 예외 — TEN-RC-05 · TEN-RC3-04** |
| Q22 | pass | ⑦ 입력에 평가이익이 없다. 세 칸: amazon·nvidia F7 은 고객사 출처 평가이익을 "입력에 넣지 않는다" 단서와 함께 내릴 근거에 방증으로 두어 규칙 ⑦ 문언대로다. alphabet.F7 의 비고객(SpaceX) 평가이익 줄은 올릴 근거에 있어 판정 칸으로 옮기는 것이 맞다(다음 실행 과제) |
| Q23 | fail | **승계 판단 예외 — TEN-RA4-01** |

fail 14건(Q01·02·03·05·08·09·10·12·13·16·19·20·21·23)은 모두 승계 판단 예외다. 인용한 긴장 15개(TEN-RC-02·RC-03·RC-05·RB-Q10·RA-02·RC3-01·RC3-03·RC3-04·RC3-05·RC4-01·RC4-02·RC4-03·RC4-04·RA4-01·RA6-01)는 규칙 v1.9 에서 모두 `status: open`, `recheck_at: 2026-11` 이다(이 세션이 다시 확인). TEN-RA3-01 은 아직 open 이라 닫을 대상으로 남는다. needs_fix 두 건은 체크리스트 판정을 바꾸지 않는다.

#### 다음 실행 과제
이번에 새로 본 것(세 칸 분류, 6건):
- alphabet.F7 올릴 근거 둘째 줄(SpaceX 평가이익)을 판정 칸 넷째 줄 옆으로 옮긴다. tsmc·apple·alibaba F7 의 비고객 영업외 비중과 같은 칸이다.
- 계획 줄에 단서를 같은 줄로 단다. tesla.F2 는 판정 넷째 줄의 단서를 올릴 근거 둘째 줄로 옮긴다. meta.F9 내릴 근거(연간 설비투자 계획 $130~145B), tsmc.F2 올릴 근거 첫째 줄(하반기 증산 계획), tsmc.F3 올릴 근거 둘째 줄(매출 성장 가이던스 상향), spacex-xai.F3 올릴 근거 둘째 줄(10월부터 램프하는 $6.7B 계약)에는 "계획이라 점수에 넣지 않는다" 류 단서를 단다. tsmc.F4 는 넘어온 과제다.
- ⑤ 에서 공짜 사용자·수출통제로 세지 않는 관계의 칸을 맞춘다. alibaba.F5 내릴 근거 첫째·둘째 줄을 meta.F5·nvidia.F5 처럼 판정 칸으로 옮긴다. 옮겨도 내릴 근거에 셋째 줄(증류 주장)이 남는다.
- alphabet.F2 올릴 근거 셋째 줄(Gemini 3.8 Flash)을 나눈다. 속도·가격 경쟁력은 올릴 근거, 프론티어 순위 불변은 내릴 근거다. 규칙 ② 는 성능이 프론티어를 넘지 못하고 가격만 싼 모델을 게임체인저로 보지 않는다.
- spacex-xai.F4 올릴 근거 셋째 줄(상장 조달액·현금)은 ④ 기준(다각화·변신·속도·수직계열화)의 지표가 아니어서 판정 칸으로 옮기거나 근거에서 뺀다. Terafab 과제와 함께 처리한다.
- anthropic.F9 올릴 근거 둘째 줄 "흑자 전환 목표 후퇴와 완충 잠식은 확인되지 않았다" 를 판정 입력(bep_retreat·buffer_erosion = no)에 맞춰 spacex-xai·tesla F9 처럼 "없음이다" 로 쓴다. 지금 문면은 미확인으로 읽혀 guide 5.6 의 "미확인은 판정 칸" 과 부딪친다.

round 5 에서 넘어온 것(6건):
- Stargate 출자 사실을 한쪽으로 정해 oracle.F7.fix52 내릴 근거 둘째 줄과 openai.F5.impl48 문장을 oracle.F5 내릴 근거 둘째 줄과 맞춘다(점수는 −2 그대로).
- TEN-RC-03 재검토 때 NVIDIA 의 자체 칩 없는 지분 투자처(CoreWeave·Nebius·Reflection AI)를 네 질문으로 함께 판정하고, affected 의 nvidia 사유에 적는다.
- EV-nvidia-013 conditional_impact 의 "⑤ 에서는 공동개발 관계만 센다" 를 규칙 2.2 에 맞게 고친다.
- spacex-xai.F4 부문 목록에서 Terafab 을 뺀다.
- tsmc.F4 올릴 근거 첫째·둘째 줄에서 계획(로드맵·투자액·건설 중 거점)과 배포 사실을 갈라 적는다.
- 규칙 파일에서 TEN-RA3-01 을 해소로 닫는다(openai.F4 재판정 반영).

확인 리뷰에서 넘어온 것(22건):
- anthropic·openai F3 별도 수익모델 사유. openai.F3 내릴 근거는 의견 한 줄("퍼스트무버 함정에 머물러 있다고 본다")뿐이다.
- tesla.F7 환류 고리.
- microsoft.F5 +2 근거(Anthropic 지분).
- palantir.F3 사유.
- apple·nvidia·palantir·tsmc F9 '안정' 근거를 실측 FCF 로 바꾸기.
- rules.md ③ 직전 분기 대비·전년 대비 우선순위.
- 새 사유 승계 판단의 판단일 표시.
- counter_evidence 옛 문서 표기(세 건은 이번에 비웠다. 규칙·문서 쪽 표기만 남는다).
- judgments note.
- TRG-057·080.
- 방법 절 ⑨ 신용등급 문장(사용자 판단 대기).
- alibaba 여신 `mixed_as_of`.
- oracle G4 분모 C-26.
- net_cash 지분증권 우선순위.
- tsmc·oracle F9 스톡 지표.
- EV-amazon-008.
- EV-microsoft-004.
- Alibaba 9월 분기 트리거.
- rules.md 8절 C-09·C-26.
- CDAO "4사 공통".
- 비상장 보정 ARR kind.
- research 발동 트리거 표 문구.

### 근거 세 칸 재분류 전 좁은 확인(round 5) · rule-consistency — 규칙 일관성
round 5 검토자: Claude Opus 5.5 · 규칙 일관성 독립 세션(이 실행을 만든 세션 아님) · 2026-10-07 · 완결된 문장 재작성 뒤 1차 · 확인 리뷰 · 좁은 확인
round 5 결과: pass
round 5 요약: 확인 리뷰의 needs_fix 두 건은 닫혔다.<br>• **openai.F4:** 출하 실적이 없는 Jalapeño 를 근거에서 빼고 배포된 ChatGPT·API 로 3점을 매겼다. tesla.F4 와 같은 '출하·실제 배포만' 잣대다.<br>• **nvidia.F5:** 승계 판단 예외(TEN-RC-03)로 본다. oracle.F5 는 +2 에서 +1 로 돌아갔다. 근거는 확인된 지분 동맹이 TikTok USDS 15% 하나뿐이고 Stargate 출자가 10-Q·10-K 에 없다는 것이다. 따라서 이번 실행에서 '지분 동맹 복수 → +2' 를 새로 받은 회사가 없다. Oracle 에 대한 판정은 기존 A 기준표 문언을 확인된 사실에 댄 것이지 새 읽기가 아니다. 남은 쟁점은 NVIDIA 지분 투자처(CoreWeave·Nebius·Reflection)를 동맹으로 셀지인데, 이는 네 질문 3번(상대가 떠날 수 있나)의 통일 기준에 달려 있다. TEN-RC-03 이 바로 그 긴장을 nvidia.F5 를 대상으로 2026-11 재검토에 올려 두었다. 그래서 AGENTS.md 승계 판단 예외의 세 조건(기존 논리, 이번 실행이 잣대를 바꾸지 않음, 재검토 시점과 함께 등록)이 선다.<br>• **'출하·실제 배포만' 잣대:** ④ 를 받는 나머지 회사에 마지막으로 대 보았다. 미배치 사업 줄이나 출하 전 제품이 점수를 정하는 곳은 없다. anthropic.F4 는 자체 칩을 이미 빼고 Claude Code·에이전틱 워크플로로 4점을 매긴다. spacex-xai.F4 의 Terafab 과 tsmc.F4 의 로드맵·투자액 서술은 점수를 정하지 않아 다음 실행 과제다.<br>• **결론:** 예외 없는 fail 이 남지 않았다. 점수 결과는 openai 14위, oracle·tesla 공동 12위이고 results 와 맞다.

round 5 검토 기준: results_hash `e279d193d30137ee…`, draft_hash `1bbf20715c81cc01…`. review.md frontmatter 와 같은 값이고, results_hash 는 results.json 에서, 초안 sha256 은 파일에서 이 세션이 다시 계산했다.

확인한 것:
- oracle.F5·openai.F4 의 새 문장과 판정 재료, oracle.F7.fix52·openai.F5.impl48 의 Stargate 서술.
- nvidia.F5 와 EV-nvidia-013, 규칙 TEN-RC-03 의 판단 목록·사유·재검토 시점.
- 14개사 ④ 판단 문장.
- 기업 요약 여섯 개의 점수·순위 서술(사실 대조는 사실·출처 영역).

#### 발견
확인 리뷰 needs_fix 의 처리:

| 확인 리뷰 발견 | 상태 | 확인 내용 |
| --- | --- | --- |
| high · nvidia.F5 지분 동맹 복수 잣대 미판정(Q03·Q19) | **닫힘 — 승계 판단 예외 TEN-RC-03** | 이 발견의 전제는 "이번 실행이 oracle 에 '준 지분 투자 복수 → +2' 를 새로 댔다" 였다. PRP-142 로 oracle.F5 는 +1 이 됐고, 그 문장은 기존 A 기준표의 +2 조건을 확인된 사실에 대 "지분 동맹이 둘 이상이라는 +2 조건이 서지 않는다" 고 판정한다. 이번 실행에서 +2 를 새로 받은 회사는 없고, A 기준표 문언과 Microsoft 에 쓴 읽기(2026-09-15 A+2 재판정)도 바뀌지 않았다. nvidia.F5 의 남은 쟁점(투자처를 동맹으로 셀지)은 네 질문 3번의 기준 통일 문제이고, TEN-RC-03 이 nvidia.F5 를 judgment_ids 에 넣어 "투자처·하이퍼스케일러가 … 떠날 수 있어 불인정" 사유로 2026-11 재검토에 올려 두었다. 방향은 "A 가 오르거나 내릴 수 있다" 다. 다만 TEN-RC-03 의 nvidia 사유는 자체 칩으로 떠날 수 있는 투자처만 적고, 자체 칩이 없는 CoreWeave·Nebius·Reflection 은 적지 않는다. 재검토 때 함께 대도록 다음 실행 과제에 적는다 |
| medium · openai.F4 배치 전 ASIC 이 ④ 4점 근거(Q03·Q09) | **닫힘** | 4→3 이다. 문장이 배포된 사업(ChatGPT·API)과 진행 중인 확장(광고·디바이스)을 가르고, Jalapeño 는 "출하가 확인될 때까지 점수 근거로 쓰지 않는다" 고 적는다. tesla.F4 와 같은 잣대다. 이해당사자 발표 근거(TEN-RA3-01 의 사유)도 점수 근거에서 빠졌다. 총점 3, 14위가 results 와 맞다 |

이번 확인에서 본 것(모두 점수·순위·체크리스트 판정을 바꾸지 않는다):

| 등급 | 위치 | 발견 | 점수 영향 |
| --- | --- | --- | --- |
| medium | `judgments.json` oracle.F7.fix52 ↔ oracle.F5 · openai.F5.impl48 | **Stargate 출자 서술이 판단끼리 어긋난다.** oracle.F5 는 "10-Q 와 2026 회계연도 10-K 에는 Stargate 지분 출자가 나오지 않는다" 고 적는다. 그런데 oracle.F7.fix52 는 "Oracle 은 Stargate LLC 에 $7B 를 지분 출자했고 … 세로축은 '내 돈이 돌아옴'" 으로 세로축 입력을 받친다. openai.F5.impl48 도 "Oracle 의 Stargate $7B 지분은 동맹으로 남는다" 고 적는다. 같은 사실을 한 판단은 공시로 확인되지 않는다고, 다른 판단은 실측처럼 쓴다 | 없음. ⑦ 은 '조달 의존 비중 큼' 이라 세로축과 상관없이 −2 이고, openai A +1 은 Stargate 를 OpenAI 자신의 지분으로 센다. 사실 확정은 사실·출처 영역 몫 |
| low | `evidence.json` EV-nvidia-013 conditional_impact | **⑤·⑦ 중복에 대한 잣대가 반대다.** "NVIDIA 가 Reflection 에 넣은 돈은 ⑦ 의 환류 근거와 겹치지 않도록 ⑤ 에서는 공동개발 관계만 센다" 는 규칙 2.2("같은 관계를 ⑤ 와 ⑧·⑦ 에 한 번씩 넣는 것은 정상, 금지선은 같은 속성")와 microsoft(OpenAI 지분을 ⑤·⑦ 에 함께 사용)와 반대다 | 없음(근거 문장) |
| low | `judgments.json` spacex-xai.F4 | **배치 전 사업이 부문 목록에 있다.** '출하·실제 배포만' 잣대로 보면 Terafab(건설·장비 조달 단계)은 부문 목록에서 빠져야 한다 | 없음. Starlink·Starship·xAI·X·Cursor 다섯 배포 부문으로 5 |
| low | `judgments.json` tsmc.F4 | **계획과 배포가 섞여 있다.** 근거에 계획 성격(A16·A14 로드맵 "일정대로", 애리조나 $165B 투자액, 드레스덴)과 배포 사실(해외 거점, CoWoS 캐파 증설, 비HPC 매출 34%, 2023년 하강기 생존)이 함께 있다. 미배치 사업 줄을 폭에 넣지는 않아 tesla·openai 와 같은 경우는 아니다. 다만 계획 서술을 점수 근거와 갈라 적어야 한다 | 없음(판정 기준) |

#### 체크리스트
승계 판단 예외는 fail 사유가 승계 판단의 기존 논리이고, 이번 실행이 그 잣대를 바꾸지 않았으며, `open_tensions` 에 recheck_at 2026-11 로 등록된 경우에 적었다. 이번 실행이 새로 댄 잣대는 ⑥ 트랙·최근 1년 창·여신, ④ 출하·실제 배포만, 분기 실측 FCF 추세다. 이 잣대가 닿는 판단은 tesla·openai F4, microsoft F9 처럼 모두 다시 판정됐다.

| ID | 결과 | 근거 |
| --- | --- | --- |
| Q01 | fail | **승계 판단 예외 — TEN-RC-05 · TEN-RC3-04** |
| Q02 | fail | **승계 판단 예외 — TEN-RC-02 · TEN-RC3-01 · TEN-RC3-03 · TEN-RC3-05 · TEN-RC4-02** |
| Q03 | fail | **승계 판단 예외 — TEN-RC-03(nvidia.F5 포함) · TEN-RC4-03.** 예외 없는 fail 은 없다. 이번 실행이 새로 댄 잣대 셋이 닿는 회사는 모두 다시 판정됐다.<br>• ④ 출하만: tesla·openai.<br>• FCF 추세: microsoft 를 다시 판정했다. apple·nvidia·palantir·tsmc 는 실측으로 재도 안정이다.<br>• ⑥ 트랙: tsmc·alibaba.<br>• oracle.F5 는 기존 +2 조건을 확인된 사실에 대 +1 이다 |
| Q04 | pass | ⑥ 은 비율 잣대이고 변경이 없다 |
| Q05 | fail | **승계 판단 예외 — TEN-RA-02(nvidia F2).** openai.F4 는 이해당사자 발표를 점수 근거에서 뺐다. 이해상충 표기는 판정에 넣지 않았다 |
| Q06 | pass | 볼륨 지표가 점수 재료로 든 곳이 없다 |
| Q07 | pass | amazon.F3 문장 그대로다 |
| Q08 | fail | **승계 판단 예외 — TEN-RC4-03** |
| Q09 | fail | **승계 판단 예외 — TEN-RA-02 · TEN-RA6-01.**<br>• openai.F4·tesla.F4·microsoft.F9 는 계획을 점수 근거에서 뺐다.<br>• spacex-xai.F4 의 Terafab 과 tsmc.F4 의 로드맵·투자액 서술은 점수를 정하지 않아 low 로 적었다 |
| Q10 | fail | **승계 판단 예외 — TEN-RB-Q10 · TEN-RC4-04** |
| Q11 | pass | ⑨ 게이트 경로로 계산하고, 순적자 실격은 없다 |
| Q12 | fail | **승계 판단 예외 — TEN-RC4-01 · TEN-RC3-05.** nvidia.F3 은 규칙 정의(직전 분기 대비)로 잰다 |
| Q13 | fail | **승계 판단 예외 — TEN-RC3-05** |
| Q14 | pass | 14사 door_closed 가 전부 fail 이다 |
| Q15 | pass | 공짜 사용자를 동맹으로 세지 않는다 |
| Q16 | fail | **승계 판단 예외 — TEN-RC-02 · TEN-RC4-02** |
| Q17 | pass | 변경 없음 |
| Q18 | pass | 관계사 처리가 같다. tesla.F4 는 관계사 합작 Terafab 을 배치 전이라 뺐다 |
| Q19 | fail | **승계 판단 예외 — TEN-RC-03(nvidia.F5).** 받은 투자를 A 에서 빼는 처리는 일관된다. 준 지분 투자를 동맹으로 셀지는 이탈 조건 통일(C-08)과 함께 2026-11 에 재검토한다 |
| Q20 | fail | **승계 판단 예외 — TEN-RC-03(C-08)** |
| Q21 | fail | **승계 판단 예외 — TEN-RC-05 · TEN-RC3-04** |
| Q22 | pass | ⑦ 입력에 평가이익이 없다 |
| Q23 | fail | **승계 판단 예외 — TEN-RA4-01** |

fail 14건(Q01·02·03·05·08·09·10·12·13·16·19·20·21·23)은 모두 승계 판단 예외다. 인용한 긴장 15개(TEN-RC-02·RC-03·RC-05·RB-Q10·RA-02·RC3-01·RC3-03·RC3-04·RC3-05·RC4-01·RC4-02·RC4-03·RC4-04·RA4-01·RA6-01)는 모두 `status: open`, `recheck_at: 2026-11` 이다. TEN-RA3-01(openai.F4)은 이번 재판정으로 사유가 해소됐으므로 규칙 파일에서 닫을 대상이다.

#### 다음 실행 과제
이번에 새로 본 것:
- Stargate 출자 사실을 한쪽으로 정해 oracle.F7.fix52(세로축 근거)와 openai.F5.impl48 문장을 oracle.F5 와 맞춘다. 공시로 확인되지 않으면 ⑦ 세로축 근거를 다른 사실로 바꾸거나 '모름' 으로 둔다(점수는 −2 그대로).
- TEN-RC-03 재검토 때 NVIDIA 의 자체 칩 없는 지분 투자처(CoreWeave·Nebius·Reflection AI)를 네 질문으로 함께 판정하고, affected 의 nvidia 사유에 적는다.
- EV-nvidia-013 conditional_impact 의 "⑤ 에서는 공동개발 관계만 센다" 를 규칙 2.2 에 맞게 고친다.
- spacex-xai.F4 부문 목록에서 Terafab 을 뺀다.
- tsmc.F4 근거에서 계획(로드맵·투자액·건설 중 거점)과 배포 사실을 갈라 적는다.
- 규칙 파일에서 TEN-RA3-01 을 해소로 닫는다(openai.F4 재판정 반영).

확인 리뷰에서 넘어온 것:
- anthropic·openai F3 별도 수익모델 사유.
- tesla.F7 환류 고리.
- microsoft.F5 +2 근거(Anthropic 지분).
- palantir.F3 사유.
- apple·nvidia·palantir·tsmc F9 '안정' 근거를 실측 FCF 로 바꾸기.
- rules.md ③ 직전 분기 대비·전년 대비 우선순위.
- 새 사유 승계 판단의 판단일 표시.
- counter_evidence 옛 문서 표기.
- judgments note.
- TRG-057·080.
- 방법 절 ⑨ 신용등급 문장(사용자 판단 대기).
- alibaba 여신 `mixed_as_of`.
- oracle G4 분모 C-26.
- net_cash 지분증권 우선순위.
- tsmc·oracle F9 스톡 지표.
- EV-amazon-008.
- EV-microsoft-004.
- Alibaba 9월 분기 트리거.
- rules.md 8절 C-09·C-26.
- CDAO "4사 공통".
- 비상장 보정 ARR kind.
- research 발동 트리거 표 문구.

### 확인 리뷰(round 4) · rule-consistency — 규칙 일관성
round 4 검토자: Claude Opus 5.5 · 규칙 일관성 독립 세션(이 실행을 만든 세션 아님) · 2026-10-06 · 완결된 문장 재작성 뒤 1차 · 확인 리뷰
round 4 결과: needs_fix
round 4 요약: 1차 needs_fix 네 건(nvidia.F3, oracle.F5, tesla.F4, microsoft.F9)은 모두 닫혔다.<br>• NVIDIA ③ 의 후발 가속도 실패는 직전 분기 대비 감속(+21%→+18%)으로 판정했고, 규칙 문언에 맞다. rules.md ③ 지침은 "직전 분기 대비 성장률이 오르면 가속 … 내리면 감속" 을 가속도의 정의로 먼저 적고, 전년 대비 비교는 자료 요건으로 덧붙인다. 두 지표가 갈린 이유(전년 1분기 중국향 Hopper $4.6B 의 기저)와 고른 근거도 문장에 남겼다. 1차에서 이 리뷰가 낸 전년 대비 통과 제안은 철회한다.<br>• Microsoft 분기 FCF 여덟 분기는 companyfacts 에서 다시 계산해 문장과 맞췄다.<br>그러나 이번에 새로 댄 잣대 셋을 같은 잣대가 닿는 회사에 대 보니, 두 회사가 남았다(Q03).<br>• **(나) 준 지분 투자로 이룬 지분 동맹 복수 → +2:** A +1 가운데 NVIDIA 만 실행 안에 고객 지분 투자가 여럿 있다. CoreWeave $2B·Nebius $2B 와 Nemotron 연합 회원 Reflection AI 투자가 그것인데, nvidia.F5 는 이 조항을 판정하지 않았다. EV-nvidia-013 은 오히려 "⑦ 과 겹치지 않도록 ⑤ 에서는 공동개발만 센다" 고 적어, Oracle·Microsoft 처럼 같은 지분을 ⑤ 와 ⑦ 에 함께 쓰는 잣대와 반대다.<br>• **(다) ④ 의 배치 전 사업 제외:** openai.F4 4점의 근거는 출하 실적이 저장소에 없는 자체 ASIC Jalapeño 다. 이 사정은 TEN-RA3-01 로 등록돼 있지만, 이번 실행이 같은 잣대를 Tesla 에 대 4→3 으로 내렸으므로 승계 판단 예외가 아니다(AGENTS.md 「리뷰 범위 — 승계 판단 예외」).<br>• **(가) 분기 실측 현금흐름으로 재는 FCF 추세:** 모든 FCF 흑자 기업에 대 보니 판정이 그대로다. 문장의 근거만 손볼 곳이 있다(low).<br>두 건 모두 점수와 순위를 움직일 수 있다.

round 4 검토 기준: results_hash `c11f5cc6b5eb3bf7…`, draft_hash `d522699cf7916b1d…`. review.md frontmatter 와 같은 값이고, results_hash 는 results.json 에서, 초안 sha256 은 파일에서 이 세션이 다시 계산했다.

확인한 것:
- 네 판단의 새 문장과 판정 재료·개정 이력, proposals PRP-134~137.
- results 의 순위: Microsoft 13 공동 3위, Oracle 5 공동 11위, Tesla 4 공동 13위.
- 분기 FCF 복원: `validation/f6-avail-15/_raw/{MSFT,AAPL,PLTR}.companyfacts.json` 의 누계 차로 구했다(스크래치 `review/qfcf.py`). TSMC 는 tsmc.fcf_ttm.rs1006 basis 의 6-K 반기 성분으로 구했다.
- A +1 인 9개사(meta·tsmc·alibaba·anthropic·apple·nvidia·palantir·spacex-xai·openai)의 판단·근거에서 지분·투자·출자 서술을 전수 검색했다.
- 14개사 ④ 판단에서 계획·서명·미배치 서술을 전수로 읽었다.

#### 발견
1차 발견의 처리:

| 1차 발견 | 상태 | 확인 내용 |
| --- | --- | --- |
| high · nvidia.F3 가속도 사유가 비기준(퍼스트무버) | **닫힘** | 판정 재료는 그대로(acceleration fail, imitation fail)이고 사유를 규칙 기준으로 다시 썼다.<br>• **가속도:** 데이터센터 매출의 직전 분기 대비 성장률이 +21%($75.2B)에서 +18%($89.0B)로 내렸다. 규칙 ③ 지침 문언 "직전 분기 대비 성장률이 오르면 가속, 유지면 등속, 내리면 감속" 에 그대로 맞고, 수준값 3개 분기 요건도 선다(직전 분기 대비 +21% 가 전 분기 수준을 전제).<br>• **두 지표가 갈림:** 전년 대비는 +92%→+117% 로 올라 두 지표가 갈렸다. 규칙은 직전 분기 대비를 정의로 두고 전년 대비를 비교 요건으로 덧붙일 뿐 우선순위를 따로 정하지 않는다. 갈린 이유(전년 1분기 중국향 Hopper $4.6B 기저, 추론 표시)와 고른 근거를 문장에 남겼다. 가점은 실측이 분명할 때만 준다는 2.1 의 방향과도 맞다.<br>• **1차 제안 철회:** 1차에서 이 리뷰가 낸 "전년 대비 가속으로 통과" 제안은 규칙의 첫 정의를 건너뛴 것이라 철회한다.<br>• **모방 불가능성:** CUDA 생태계를 ① 의 설치기반이라 쓰지 않는 처리는 alphabet·microsoft·apple 의 "① 재탕 → 실패" 와 같은 잣대다 |
| high · oracle.F5 동맹 +2 조항 미판정 | **닫힘** | A +1→+2 다. 지분 동맹 둘은 Stargate LLC $7B 출자와 TikTok USDS 15% 이고, 네 질문 1·2번(지분·연동)을 문장에 적었다. 같은 지분을 ⑦ 세로축과 ⑤ 에 함께 쓰는 것은 microsoft(OpenAI 27%)와 같은 처리다. Stargate 를 합작 법인 하나로 센 것도 openai.F5 와 같다. ⑤ 4, 총점 5, 공동 11위가 results 와 맞다 |
| medium · tesla.F4 배치 전 사업 포함 | **닫힘** | 4→3 이다. Optimus·Terafab 을 폭에서 빼고 차량·에너지 저장·소규모 로보택시로 매겼다. ④ 판정 지침("출하·실제 배포와 계획 … 을 나눈다. 양산 계획은 0점")에 맞다. 총점 4, 공동 13위다 |
| medium · microsoft.F9 추세를 계획으로 판정 | **닫힘** | fcf_trend 를 deteriorating 으로 바꿨다. 분기 FCF 를 다시 계산하면 2026년 1~3월 15,803M(전년 20,299M, −22%), 4~6월 19,639M(전년 25,568M, −23%)이다. 4~6월 설비투자는 35,802M(전년 17,079M)이고, 회계연도 FCF 는 71,611M→66,987M 이다. 문장 숫자와 같다. 설비투자 계획 하향을 근거에서 뺐다고 명시한다. ⑨ −1, 총점 13 이 results 와 맞다 |
| medium · anthropic.F3·openai.F3 별도 수익모델 사유 | 남음(다음 실행 과제) | 문장 불변이다 |
| medium · tesla.F7 환류 고리 | 남음(다음 실행 과제) | 문장 불변이다 |
| medium · microsoft.F5 +2 근거(Anthropic 지분 투자) | 남음(다음 실행 과제) | 문장 불변이다. 이번에 oracle 이 "준 지분 = 지분 동맹" 으로 +2 가 되면서 이 빈칸이 더 눈에 띈다 |
| medium · palantir.F3 별도 수익모델 사유 | 남음(다음 실행 과제) | 불변이다(점수 영향 없음) |
| low 다섯 건(counter_evidence 옛 문서 표기, spacex-xai.F4 Terafab, judgments note, 아마존 여신 각주, TRG-057·080) | 아마존 여신 각주 닫힘 · 나머지 남음 | 렌더러가 "런웨이는 <관측일> 공시 기준 약정으로 계산했다" 로 바꿨다(출력 영역이 문면 확인). spacex-xai.F4 의 Terafab 은 아래 (다) 로 다시 적는다 |

이번 확인에서 본 것:

| 등급 | 위치 | 발견 | 점수 영향 |
| --- | --- | --- | --- |
| **high · needs_fix** | `judgments.json` nvidia.F5(승계, A +1) · `evidence.json` EV-nvidia-013 · 참조 nvidia.F7.fix52·oracle.F5·microsoft.F5 | **(나) 지분 동맹 복수 잣대가 NVIDIA 에 닿는데 판정하지 않았다(Q03·Q19).**<br>• 이번 실행은 oracle.F5 에 "준 지분 투자 둘 → 지분 동맹 복수 → +2" 를 댔다. microsoft.F5 +2 도 같은 잣대다(A+2 재판정 b1f32f0).<br>• A +1 아홉 회사 가운데 실행 안 사실로 고객 지분 투자가 여럿인 곳은 NVIDIA 뿐이다. nvidia.F7.fix52 에 CoreWeave $2B·Nebius $2B 와 OpenAI·Anthropic·xAI 지분이 있고, EV-nvidia-013 에는 "NVIDIA 가 투자한 Reflection AI(Nemotron 연합 회원)" 가 있다.<br>• 이탈 가능성(네 질문 3번)도 따져야 한다. OpenAI·Anthropic 은 자체 칩으로 떠날 수 있어 빠질 수 있다(TEN-RC-03 의 nvidia 항목 사유). 그러나 CoreWeave·Nebius·Reflection 은 nvidia.F5 자신이 연합사에 적은 대로 "자체 칩을 개발할 자본이 없어 NVIDIA GPU 를 빌려 쓰므로 … 끊으면 양쪽이 아프다" 쪽이다.<br>• nvidia.F5 문장은 +2 조항을 판정하지 않는다. EV-nvidia-013 conditional_impact 는 "NVIDIA 가 Reflection 에 넣은 돈은 ⑦ 의 환류 근거와 겹치지 않도록 ⑤ 에서는 공동개발 관계만 센다" 고 적어, oracle(Stargate 를 ⑦ 세로축과 ⑤ +2 에 함께 사용)·microsoft 와 반대 잣대다.<br>• TEN-RC-03 은 이탈 조건 통일(C-08) 긴장이다. 이번 실행이 바꾼 잣대(지분 동맹 복수)가 닿는 판단이므로 승계 판단 예외가 아니다 | **있음.** A +2 이면 ⑤ 3, nvidia 총점 9→10 으로 단독 6위가 되고 anthropic·spacex-xai 는 7위 |
| **medium · needs_fix** | `judgments.json` openai.F4(승계, 4점) · 규칙 `open_tensions` TEN-RA3-01 | **(다) ④ 배치 전 사업 제외 잣대가 OpenAI 에 닿는다(Q03·Q09).** 4점의 근거는 자체 추론 ASIC Jalapeño 다. 그러나 문장 스스로 "출하 실적이나 독립 측정은 저장소에 없다", "Broadcom 과의 배치 계획은 2026년 0.1GW 미만 … 계획이라 점수에 넣지 않는다" 고 적는다. 이 사정은 TEN-RA3-01(하향 가능 4→3, 2026-11)로 등록돼 있다. 하지만 이번 실행이 같은 ④ 잣대(출하·실제 배포만)를 tesla.F4 에 대 4→3 으로 내렸으므로, AGENTS.md 「승계 판단 예외」의 "이번 실행이 바꾼 잣대가 닿는 승계 판단은 이 예외가 아니다" 에 걸린다. 출하가 1차 자료로 확인되면 4 가 서고, 아니면 Stargate Abilene(운영은 Oracle·SoftBank)·광고·디바이스로 다시 매겨야 한다 | **있음(가능).** 3 이면 openai 총점 4→3 으로 단독 14위, tesla 단독 13위 |
| low | `judgments.json` spacex-xai.F4 | **(다)의 잔여.** 사업 부문 목록에 Terafab(건설·장비 조달 단계)이 남았다. Tesla 는 같은 Terafab 을 폭에서 뺐다 | 없음. 나머지 다섯 부문으로 5 그대로 |
| low | `judgments.json` apple.F9·nvidia.F9·palantir.F9·tsmc.F9 | **(가)는 판정은 맞고 문장 근거만 다르다.** 네 회사의 "안정" 근거가 매출 흐름이거나 사유가 없다.<br>• 분기 실측 FCF 로 다시 재면 모두 안정 이상이다. apple 은 2026년 1~3월 26,731M(전년 20,881M), 4~6월 31,914M(24,405M)이다. palantir 는 892M(304M), 1,202M(532M)이다. tsmc 는 상반기 NT$635.6B(전년 494.6B, +28.5%)다. nvidia 는 조율자 계산으로 +86%·+59% 다.<br>• alphabet·meta·tesla 의 악화는 실측 분기 FCF 로 이미 판정돼 있다 | 없음 |
| low | `judgments.json` nvidia.F3 상태 | **새 사유인데 원래 판단일이 표시된다.** 사유를 새로 판정했는데 상태가 `carried`, 검토자 `legacy:v1.5`·2026-09-02 그대로다. 근거 문장만 바꾸는 수정은 상태를 건드리지 않는 설계(5a284f5)라 규칙 위반은 아니다. 다만 화면 머리줄 판단일이 사유를 쓴 날과 다르다 | 없음 |
| low | rules.md 3절 ③ 판정 지침 | **우선순위 규정이 없다.** 직전 분기 대비와 전년 대비 성장률이 갈릴 때 무엇을 앞세울지 정하지 않는다. NVIDIA 는 직전 분기 대비를 골라 근거를 남겼다. 다른 회사(alibaba·oracle·tsmc)는 전년 대비 자료만 있어 전년 대비로 쟀다. 같은 회사에 두 자료가 생기면(예: microsoft Azure 분기 공시) 같은 순서를 대도록 규칙에 적어 두는 것이 좋다 | 없음 |

#### 체크리스트
승계 판단 예외는 fail 사유가 승계 판단의 기존 논리이고, 이번 실행이 그 잣대를 바꾸지 않았으며, `open_tensions` 에 recheck_at 2026-11 로 등록된 경우에만 적었다. 이번 실행이 새로 댄 잣대는 ⑥ 트랙·최근 1년 창·여신, 지분 동맹 복수 → +2, ④ 배치 전 제외, 분기 실측 FCF 추세다. 이 잣대가 닿는 판단은 등록돼 있어도 예외로 적지 않았다.

| ID | 결과 | 근거 |
| --- | --- | --- |
| Q01 | fail | **승계 판단 예외 — TEN-RC-05 · TEN-RC3-04.** oracle 의 Stargate 를 ⑤(동맹)와 ⑦(환류)에 함께 쓰는 것은 속성이 달라(2.2 "같은 관계를 두 칸에 한 번씩은 정상") 중복이 아니다 |
| Q02 | fail | **승계 판단 예외 — TEN-RC-02 · TEN-RC3-01 · TEN-RC3-03 · TEN-RC3-05 · TEN-RC4-02.** 1차의 예외 없는 fail(nvidia.F3)은 닫혔다. 가속도를 규칙 정의(직전 분기 대비)로 쟀다 |
| Q03 | fail | **예외 없는 fail — nvidia.F5((나) 잣대 미적용) · openai.F4((다) 잣대 미적용).**<br>• 1차의 oracle.F5·nvidia.F3·microsoft.F9 는 닫혔다.<br>• (가) FCF 추세 잣대는 FCF 흑자 8개사 모두 판정이 그대로다.<br>• 승계 판단 예외도 있다: TEN-RC-03 · TEN-RC4-03 |
| Q04 | pass | ⑥ 은 비율 잣대이고 변경이 없다 |
| Q05 | fail | **승계 판단 예외 — TEN-RA-02(nvidia F2).**<br>• openai.F4 의 이해당사자 발표 근거(TEN-RA3-01)는 (다) 잣대에 닿아 Q03·Q09 의 예외 없는 fail 로 옮겼다.<br>• 이해상충 표기는 판정에 넣지 않았다 |
| Q06 | pass | 볼륨 지표가 점수 재료로 든 곳이 없다 |
| Q07 | pass | amazon.F3 문장 그대로다 |
| Q08 | fail | **승계 판단 예외 — TEN-RC4-03.** 변경분에 H 변화가 없다 |
| Q09 | fail | **예외 없는 fail — openai.F4.** 출하 미확인 ASIC 이 ④ 4점의 근거다.<br>• 1차의 tesla.F4·microsoft.F9 는 닫혔다.<br>• 승계 판단 예외도 있다: TEN-RA-02 · TEN-RA6-01 |
| Q10 | fail | **승계 판단 예외 — TEN-RB-Q10 · TEN-RC4-04.** nvidia.F3 은 거리(누적 매출 규모)가 아니라 성장률의 변화로 쟀다 |
| Q11 | pass | ⑨ 게이트 경로로 계산하고, 순적자 실격은 없다 |
| Q12 | fail | **승계 판단 예외 — TEN-RC4-01 · TEN-RC3-05.** 1차의 예외 없는 fail(nvidia.F3)은 닫혔다. 세 기준 모두 규칙 정의로 사유를 댄다 |
| Q13 | fail | **승계 판단 예외 — TEN-RC3-05** |
| Q14 | pass | 14사 door_closed 가 전부 fail 이다 |
| Q15 | pass | 공짜 사용자를 동맹으로 세지 않는다. 변경 없음 |
| Q16 | fail | **승계 판단 예외 — TEN-RC-02 · TEN-RC4-02** |
| Q17 | pass | 변경 없음 |
| Q18 | pass | tesla·spacex-xai 관계사 처리가 같다. tesla.F4 도 관계사 합작 Terafab 을 배치 전이라 뺐다 |
| Q19 | fail | **예외 없는 fail(같은 원인 Q03) — nvidia.F5.** 받은 투자를 빼는 처리는 일관된다. 그러나 준 지분 투자를 지분 동맹으로 세는 잣대를 oracle·microsoft 에는 대고 nvidia 에는 대지 않았다 |
| Q20 | fail | **승계 판단 예외 — TEN-RC-03(C-08).** oracle 의 두 지분 동맹은 조달이 아니라고 문장이 적는다 |
| Q21 | fail | **승계 판단 예외 — TEN-RC-05 · TEN-RC3-04** |
| Q22 | pass | ⑦ 입력에 평가이익이 없다. oracle ⑦ 세로축은 출자금의 환류이지 평가이익이 아니다 |
| Q23 | fail | **승계 판단 예외 — TEN-RA4-01** |

예외 없는 fail 은 Q03·Q09·Q19 이고, 원인 판단은 nvidia.F5 와 openai.F4 둘이다.

**닫는 길(둘 공통, 하나를 고른다).**
- (가) 사람이 승인 페이지에서 판정 재료를 규칙대로 다시 매긴다.
  - nvidia.F5 A: CoreWeave·Nebius·Reflection 지분 동맹을 네 질문으로 판정하고, EV-nvidia-013 의 "⑤ 에서는 공동개발만" 문장을 같이 맞춘다.
  - openai.F4 score: Jalapeño 출하를 1차 자료로 확인하거나 출하분을 빼고 다시 매긴다.
- (나) 같은 잣대를 대고도 지금 값이 선다는 판정을 문장으로 남긴다. 예를 들어 NVIDIA 지분 투자처가 왜 동맹이 아닌지, Jalapeño 출하의 1차 자료가 무엇인지 적는다.

이번 실행이 그 잣대를 바꿨으므로 긴장 등록만으로는 닫히지 않는다. 고친 뒤 research → calculate → draft → 확인을 거친다. score-review 절차상 확인 리뷰는 이번이 한 번이라, 남으면 `blocked` 로 사람에게 올린다.

#### 다음 실행 과제
- anthropic.F3·openai.F3 의 별도 수익모델 사유를 규칙 기준(비모델 매출 또는 양의 단위경제)으로 다시 쓴다.
- tesla.F7 '내 돈이 돌아옴' 의 고리를 사람이 판정해 문장에 넣는다. 고리는 xAI 투자 → SpaceX 의 Megapack 구매다.
- microsoft.F5 +2 근거에 Microsoft 의 Anthropic 지분 투자를 넣는다. oracle.F5 와 같은 서술 방식으로 맞춘다.
- palantir.F3 별도 수익모델 '부분' 사유를 채운다.
- spacex-xai.F4 부문 목록에서 Terafab 을 배치 전 사업으로 뺀다(tesla.F4 와 같은 처리).
- apple·nvidia·palantir·tsmc F9 의 '안정' 근거를 분기 실측 FCF 로 다시 쓴다(위 계산값).
- rules.md ③ 지침에 직전 분기 대비·전년 대비 성장률이 갈릴 때의 우선순위를 적는다.
- nvidia.F3 처럼 사유를 새로 판정한 승계 판단의 판단일 표시를 정한다(상태·검토자 갱신 여부).
- tsmc·anthropic·openai F5 의 `counter_evidence` 에서 옛 문서 행 번호 표기를 지운다.
- judgments.json 최상위 note 를 지금 상태로 고친다.
- TRG-057 condition 을 fired 에 맞게 고치고, TRG-080 source_ids 를 채운다.
- 방법 절 ⑨ 의 "조달 여력은 신용등급으로" 고정 문장(`factor-concepts.json`, 사용자 원본)은 사용자 판단 대기다.
- 이전 리뷰에서 넘어온 것(관측·규칙 불변이라 유지):
  - alibaba 여신 `mixed_as_of`.
  - oracle G4 분모 C-26($288B).
  - net_cash 상장 지분증권·전략적 지분투자 우선순위(TSMC VIS).
  - tsmc·oracle F9 의 스톡 지표.
  - EV-amazon-008 microsoft 배정.
  - EV-microsoft-004 AI 귀속 단서.
  - Alibaba 9월 분기 트리거.
  - rules.md 8절 C-09·C-26.
  - CDAO "4사 공통" 서술.
  - 비상장 보정 ARR kind 기준.
  - research 발동 트리거 표의 "수정함" 문구.

#### 이전 리뷰 기록

##### 재작성 뒤 1차(round 3) · rule-consistency — 규칙 일관성
round 3 검토자: Claude Opus 5.5 · 규칙 일관성 독립 세션(이 실행을 만든 세션 아님) · 2026-10-06 · 완결된 문장 재작성 뒤 1차
round 3 결과: needs_fix
round 3 요약: 판단 114개의 새 문장을 판정 재료(③ 세 기준·⑤ A·H·⑦ 두 축·⑨ gate_inputs·①②④⑧ 점수)와 하나씩 대조했다. 문장과 판정 재료가 어긋나는 승계 판단은 대부분 이미 `open_tensions` 에 재검토 시점(2026-11)과 함께 등록돼 있어 승계 판단 예외에 든다. 예를 들면 tsmc.F3 후발 가속도(TEN-RC4-04), anthropic·openai F7(TEN-RC3-01), anthropic.F2 의 5점(TEN-RA4-01·C-03 pending_recheck), spacex-xai·tesla·microsoft·amazon·palantir F3 가속도(TEN-RB-Q10)가 그렇다. 그런데 문장을 완결된 현재 상태로 다시 쓰면서 **등록되지 않은 긴장 네 건**이 드러났다. 넷 모두 점수를 움직일 수 있어 체크리스트 Q02·Q03·Q09·Q12 를 예외 없는 fail 로 만든다.<br>(1) nvidia.F3 은 후발 가속도를 실패로 두는데, 사유가 규칙 기준(AI 귀속 지표의 성장률이 오르는가)이 아니라 "시장을 연 퍼스트무버" 다. 같은 실행 안의 데이터센터 매출 성장률은 직전 분기 +92% 에서 +117% 로 올랐다.<br>(2) oracle.F5 는 동맹 등급 +2 의 "지분이 걸린 동맹 복수" 조항을 판정하지 않았다. 실행 안에는 Stargate LLC $7B 지분 출자와 TikTok USDS 합작사 15% 지분이 있고, microsoft.F5 +2 는 준 투자를 능동 지분 동맹으로 세는 잣대를 썼다.<br>(3) tesla.F4 는 배치 전인 Optimus·Terafab 을 사업 폭에 넣었다고 스스로 적는다.<br>(4) microsoft.F9 는 FCF 추세 "안정" 을 설비투자 계획 하향 하나로 판정했다.<br>넷 다 승계 판단이고, 고치는 길은 둘이다. 사람이 판정 재료를 규칙대로 다시 매기거나(propose→승인 페이지), 규칙 파일 `open_tensions` 에 재검토 시점과 함께 등록해 승계 판단 예외로 돌리는 것이다. 점수·순위는 1차·확인 리뷰와 같고, 검증기의 화면 문장 검사(`self_contained`)는 통과한다.

round 3 검토 기준: results_hash `975fbe139afc3c37…`, draft_hash `7f21d3d4b2577789…`. review.md frontmatter 와 같은 값이고, results_hash 는 results.json 에서, 초안 sha256 은 파일에서 이 세션이 다시 계산했다.

확인한 것:
- `judgments.json` 114개: 지금 evidence 를 판정 재료·점수와 전부 대조했다. 문장이 판정 재료와 어긋나 보인 판단 12개는 `revision_history[-1].previous.evidence` 와도 맞춰, 재작성이 만든 것인지 원래 있던 것인지 갈랐다(모두 원래 있던 논리였다).
- `company_summaries` 14개의 점수·순위 서술을 results 와 대조했다.
- 규칙 v1.9 의 `open_tensions` 18개를 판단 ID·사유 문자열로 전수 대조했다. A+2 재판정 기록(`validation/a2-strict-54-verdict.md`, 커밋 b1f32f0)도 봤다.
- results 의 점수 14개사가 이전 리뷰와 같다. 입력 해시 가운데 observations 는 원본 표기 문구 한 줄만 바뀌었다.
- `validate_report_contract.py`: display text self-contained ok, 결정론적 재계산 ok. 실패는 review 상태·승인·HTML 해시뿐이다.

###### 발견
| 등급 | 위치 | 발견 | 점수 영향 |
| --- | --- | --- | --- |
| **high · needs_fix** | `judgments.json` nvidia.F3(승계, `acceleration: fail`, `imitation: fail`) | **후발 가속도를 규칙 기준이 아닌 사유로 실패시켰다(Q02·Q03·Q12).**<br>• 문장: "후발 가속도는 실패로 판정돼 있으며, 이는 NVIDIA 가 후발 진입자가 아니라 시장을 연 쪽이라는 데서 나온 판정으로 읽힌다(추론)". 이전 문장도 "시장 개척자이자 현 지배자 = 퍼스트무버" 하나다.<br>• 규칙 ③ 의 후발 가속도는 "AI 귀속 지표의 성장률이 오르는가(2차 도함수)" 이고, 선두 기업을 빼는 조항이 없다.<br>• 같은 실행의 다른 선두 기업은 성장률로 판정했다. tsmc.F3 은 매출 성장률, microsoft.F3 은 Copilot 시트 증가율, amazon.F3 은 통과로 판정됐다.<br>• NVIDIA 의 AI 귀속 지표인 데이터센터 매출 성장률은 직전 판단 문장의 FY27 1분기 +92% 에서 지금 nvidia.F9 문장의 2분기 +117% 로 올랐다.<br>• 모방 불가능성 실패 사유("추격당하는 쪽")도 기준(구조적 자산 + 실제로 앞섬)과 다르다. 같은 판단에 점유율 70~75% 가 적혀 있다.<br>• `open_tensions` 에 이 판단이 없다. | **있음.** 가속도 통과 시 통과점 2 → ③ 3. nvidia 총점 9→10, 공동 6위 → 단독 6위가 되고 anthropic·spacex-xai 는 7위 |
| **high · needs_fix** | `judgments.json` oracle.F5(승계, A +1) · 참조 microsoft.F5 · oracle.F7.fix52 · observations oracle.net_cash.rs1006 | **동맹 등급 +2 조항을 Oracle 에만 판정하지 않았다(Q03·Q19).**<br>• 문장은 동맹을 "OpenAI 대형 클라우드 계약, NVIDIA, TikTok 미국 법인, 정부 클라우드" 로 열거하고 +1 을 준다. +2 의 두 조항(지분 동맹 복수 / 경쟁사 편입)이 왜 안 서는지는 적지 않는다.<br>• 실행 안에는 Oracle 의 지분 동맹 후보 둘이 있다. 하나는 Stargate LLC 에 $7B 지분 출자(oracle.F7.fix52, openai.F5.impl48 은 이를 Oracle 의 지분 동맹으로 셈)다. 다른 하나는 TikTok USDS 합작사 지분 15%(oracle.net_cash.rs1006 basis, 10-Q 주석 1, 지분법)다.<br>• microsoft.F5 +2 는 A+2 재판정(b1f32f0)에서 "준 투자 = 능동 지분 동맹" 으로 OpenAI 27% 와 Anthropic 투자를 합쳐 복수로 셌다. 같은 잣대를 대면 Oracle 도 +2 가 될 수 있다. 그 재판정은 Oracle 을 "불변" 으로 적었지만 TikTok 지분을 다룬 기록은 없다.<br>• Stargate 를 하나로 셀지는 TEN-RC-03 note 에 별건으로 적혀 있으나, oracle.F5 는 그 긴장의 judgment_ids 에 없다. | **있음.** A +2 이면 ⑤ 4, oracle 총점 4→5. 13위 → alibaba·tesla 와 공동 11위 |
| **medium · needs_fix** | `judgments.json` tesla.F4(승계, 4점) | **배치 전 사업을 지금 점수에 넣었다고 문장이 스스로 밝힌다(Q09).** 문장: "Optimus 와 Terafab 도 폭에 넣었으나, Optimus 는 아직 배치되지 않았고 Terafab 은 건설·장비 조달 단계다. 배치 전 사업을 폭에 넣은 점은 미해결 쟁점으로 남아 있고". 규칙 ④ 는 "양산 계획은 0점", 2.1 은 "계획·발표·포지션은 0점" 이다. 이전 문장의 "운영이력 긴장 #6" 은 v1.9 `open_tensions` 에 없다. | **있음(가능).** 두 사업을 빼면 사업 폭은 차량·에너지 저장·오스틴 로보택시다. 4 가 서는지 사람이 다시 판정해야 한다. 3 이면 tesla 총점 5→4 |
| **medium · needs_fix** | `judgments.json` microsoft.F9(승계, `fcf_trend: stable`) | **FCF 추세 판정 근거가 계획 하나다(Q09·Q03).** 문장: "2026 역년 설비투자 계획을 $190B 에서 $175B 로 낮춰 현금 유출이 커지는 방향이 아니므로, 우리는 추세를 '안정'으로 판정했다". 추세는 게이트 2 에서 0 과 −1 을 가른다. 다른 FCF 흑자 기업은 실측 현금흐름으로 판정했다. alphabet·meta·tesla 는 분기 FCF 감소·마이너스로 악화, apple·nvidia 는 분기 실적으로 안정이다. 계획으로 감점을 피하는 것은 규칙 2.1("감점을 덜어 주는 장치는 가점과 같은 엄격한 기준")과 맞지 않는다. 등록된 긴장이 없다. | **있음(가능).** 악화이면 ⑨ −1, microsoft 총점 14→13 으로 meta 와 공동 3위 |
| medium | `judgments.json` anthropic.F3(`revenue_model: pass`)·openai.F3(`revenue_model: fail`) | **별도 수익모델 사유가 규칙 기준과 다르다(Q02·Q12).** 기준은 "그 전략을 먹여 살리는 비(非)모델 매출 또는 양의 단위경제" 다.<br>• anthropic 은 "소비자가 아니라 기업·코딩을 축으로 잡아 선두와 다른 자리를 팠다"(포지셔닝)로 통과다.<br>• openai 는 "퍼스트무버 함정" 으로 실패다.<br>두 사유 모두 원래 문장의 논리다. 다만 실행 안의 사실이 지금 입력을 받칠 수 있다. anthropic 은 2분기 첫 영업흑자 $559M(anthropic.F9)으로 양의 단위경제 쪽, openai 는 2026년 GAAP 손실 약 $60B 전망과 비모델 매출 부재 쪽이다. 그래서 점수 변화로 보지 않는다 | 없음(사유를 기준대로 다시 쓰면 같은 입력이 선다고 봄) |
| medium | `judgments.json` tesla.F7(`own_money_returns: yes`) | **문장이 판정 재료를 스스로 뒷받침하지 못한다.**<br>• 문장: "규칙은 관계사 거래라는 사실만으로 환류를 인정하지 않으며, 테슬라 돈이 관계사를 거쳐 테슬라 매출로 돌아오는 금액은 근거에 적혀 있지 않다".<br>• 실행 안에는 받칠 사실이 있다. 테슬라의 xAI 투자(같은 문장)와 SpaceX 의 Tesla Megapack 구매 3개월 $295M·6개월 $329M(spacex-xai.F7)이다. 이 고리를 문장에 적으면 '예' 가 선다.<br>• 이 고리를 환류로 인정하지 않으면 ⑦ 0, 총점 6 이 된다. 사람이 고리를 판정해 문장에 넣어야 한다 | 없음(지금 사실로 '예' 가 설 수 있음). 고리 불인정 시 있음 |
| medium | `judgments.json` microsoft.F5(A +2) | **+2 의 근거 문장이 빠졌다.** 문장의 근거는 "OpenAI 지분 27% 와 Anthropic 의 Azure $30B 약정" 이다. A+2 재판정이 +2 를 유지한 근거인 "Microsoft 의 Anthropic 지분 투자(준 투자 = 능동 지분 동맹)" 가 없다. Azure 약정은 Anthropic 이 사는 계약이라 지분 동맹이 아니다 | 없음(재판정 기록의 사실을 문장에 넣으면 선다) |
| medium | `judgments.json` palantir.F3(`revenue_model: partial`) | **사유가 없다.** 문장이 "부분으로 본 사유를 따로 적지 않아 다음 재검토에서 사유를 채울 대상" 이라고 적는다. `open_tensions` 에 없다 | 없음. pass·partial·fail 어느 쪽이든 통과점 1.5~2.5, 모방 불가능성 partial 이라 ③ 3 그대로다 |
| low | `judgments.json` tsmc.F5.strict54·anthropic.F5.impl48·openai.F5.impl48 의 `counter_evidence` | **옛 문서를 가리키는 표현이 남았다.** "원문 별표 G 판정표 218행", "채점표_v1.5.md 243행", "옛 근거 첫 줄", "worker 관찰" 등이 그대로다. 화면에는 나오지 않지만(검증기 통과) 판단 레코드의 완결된 문장 원칙과 어긋난다 | 없음 |
| low | `judgments.json` spacex-xai.F4 | **배치 전 사업이 부문 목록에 있다.** Terafab(건설·장비 조달 단계)이 사업 부문 목록에 든다 | 없음(나머지 다섯 부문만으로 5) |
| low | `judgments.json` 최상위 `note` | **note 가 실제와 어긋난다.** "항목은 한 글자도 바꾸지 않았다" 그대로다. 지금은 판단 114개 전부의 문장을 다시 썼다(PRP-006~119) | 없음 |
| low | 초안 1081행 | **소멸한 여신을 "기준일 현재 유효" 로 적는다.** "런웨이는 기준일 현재 유효한 약정으로 계산했다" 가 남아 있다. amazon.F9 문장은 이제 Term Loan 소멸과 C-23 을 바르게 적는다(문장은 고쳐짐, 고정 각주는 남음) | 없음(6.7년 이상) |
| low | `triggers.json` TRG-057 condition · TRG-080 source_ids | **확인 리뷰 low 가 남았다.** TRG-057 condition 의 "사건이 지나 기한이 끝났다" 가 그대로이고, TRG-080 의 `source_ids` 는 비어 있다 | 없음 |

###### 체크리스트
승계 판단 예외는 fail 사유가 승계 판단의 기존 논리이고, 이번 실행이 그 잣대를 바꾸지 않았으며, `open_tensions` 에 recheck_at 2026-11 로 등록된 경우에만 적었다. 이번 재작성은 문장만 바꿨고 판정 재료·점수를 바꾸지 않았으므로 앞의 두 조건은 모든 승계 판단에 선다. 셋째 조건(등록)이 없는 fail 은 예외로 적지 않았다.

| ID | 결과 | 근거 |
| --- | --- | --- |
| Q01 | fail | **승계 판단 예외 — TEN-RC-05 · TEN-RC3-04.** 새 문장들은 같은 속성을 두 칸에서 세지 않는다고 명시한다. alibaba 지정학은 ⑧ 에서만, palantir 정부 관계는 ⑤ 성격·⑧ 의존으로 한 번씩, oracle 선투자 위험은 ⑧·⑨ 에서 센다. 승계 fail 은 nvidia F5·F8 의 고객 자체 칩 이탈, tesla F5·F8 의 NHTSA 이고, 두 문장 모두 긴장 등록 사실을 적는다 |
| Q02 | fail | **예외 없는 fail — nvidia.F3.** 후발 가속도를 "퍼스트무버" 라는 비기준 사유로 실패시켰고 미등록이다.<br>• 그 밖은 승계 판단 예외다: TEN-RC-02(anthropic F1), TEN-RC3-01(anthropic·openai F7, 문장이 판정표상 0 임을 스스로 적음), TEN-RC3-03(palantir·oracle F1), TEN-RC3-05(alibaba F3), TEN-RC4-02(openai F1).<br>• 사유만 기준과 다른 anthropic·openai F3 별도 수익모델, tesla.F7 은 실행 안 사실로 같은 입력이 설 수 있어 medium 으로 따로 적었다 |
| Q03 | fail | **예외 없는 fail — oracle.F5 · nvidia.F3 · microsoft.F9.**<br>• Oracle 에는 microsoft 가 받은 "준 투자 = 능동 지분 동맹" 잣대를 대지 않았다.<br>• NVIDIA 는 다른 선두 기업과 달리 가속도를 성장률로 재지 않았다.<br>• Microsoft 만 FCF 추세를 계획으로 판정했다.<br>• 승계 판단 예외도 있다: TEN-RC-03(C-08 이탈 조건), TEN-RC4-03(spacex-xai H 수 비교).<br>• 이번 실행이 새로 댄 잣대(⑥ 트랙·최근 1년 창·여신)는 1차에서 확인한 대로 닿는 회사에 모두 닿았다 |
| Q04 | pass | 상장 12사 ⑥ 은 비율 잣대이고 시총 절대액을 쓰지 않는다. 기업 요약도 ⑥ 을 배수·성장률·영업외 비중으로 설명한다 |
| Q05 | fail | **승계 판단 예외 — TEN-RA-02 · TEN-RA3-01.** nvidia.F2 문장이 "벤더 발표이고 독립 측정이 아니다", openai.F4 가 "이해당사자인 OpenAI 의 발표라 1차 근거가 아니다" 라고 스스로 적는다. 이해상충 표기는 판정에 넣지 않았다 |
| Q06 | pass | ① 가격 결정력은 매출 점유율·$/M 로 잰다. alibaba.F1 은 OpenRouter 단가를 플랫폼 기업에 쓰지 않는다고 적고, anthropic·openai F1 은 "토큰 점유율은 매출 점유율이 아니다" 를 적는다 |
| Q07 | pass | amazon.F3 이 "모델을 직접 만들지 않은 것 자체는 카운터 포지셔닝이 아니다" 를 적는다 |
| Q08 | fail | **승계 판단 예외 — TEN-RC4-03.** spacex-xai.F5 문장이 등록 사실을 적는다. 다른 13사 H 는 종류(비용형·구조형·다발형)로 사유를 댄다 |
| Q09 | fail | **예외 없는 fail — tesla.F4 · microsoft.F9.**<br>• tesla.F4: 배치 전 Optimus·Terafab 을 폭에 넣었다.<br>• microsoft.F9: 설비투자 계획 하향으로 FCF 추세 안정을 판정했다.<br>• 승계 판단 예외도 있다: TEN-RA-02 · TEN-RA3-01 · TEN-RA6-01.<br>• 나머지 판단은 계획을 명시적으로 뺀다. nvidia Hugging Face 인수, apple Baltra, anthropic 자체 칩, alibaba 증자, meta 기업용 AI, oracle 추가 조달이 그렇다 |
| Q10 | fail | **승계 판단 예외 — TEN-RB-Q10 · TEN-RC4-04.** 거리를 가속도에서 뺀 문장이 있다: alphabet "2년 만의 격차 회수", anthropic "$9B→$65B 는 이동 거리". tsmc.F3 문장은 "반기 창으로 본 가속은 아직 뚜렷하지 않다(추론)" 를 덧붙였고, 이는 등록된 긴장의 내용과 같다 |
| Q11 | pass | ⑨ 는 게이트 경로로 계산하고, 순적자 실격은 없다. spacex-xai 손실률 구간, 비상장 2사 미공시 경로를 문장이 그대로 설명한다 |
| Q12 | fail | **예외 없는 fail — nvidia.F3.** 세 기준 가운데 가속도·모방 불가능성을 기준 아닌 사유로 쟀다.<br>• 승계 판단 예외도 있다: TEN-RC4-01(meta·anthropic·spacex-xai imitation partial), TEN-RC3-05(alibaba).<br>• palantir.F3 별도 수익모델 사유 부재는 점수에 닿지 않아 medium 으로 따로 적었다 |
| Q13 | fail | **승계 판단 예외 — TEN-RC3-05.** alibaba.F3 문장이 회수 장치 부재와 등록 사실을 적는다 |
| Q14 | pass | 14사 door_closed 가 전부 fail 이다 |
| Q15 | pass | 공짜 사용자를 동맹으로 세지 않는다: meta(Glimmer 개발자), alibaba(파생모델 15만), nvidia(HF 개발자 1,800만) |
| Q16 | fail | **승계 판단 예외 — TEN-RC-02 · TEN-RC4-02.** anthropic.F1(5점 불가 사유를 소비자 채널로 댐)과 openai.F1(주채널 소비자, 4점 사유는 거래 채널)이다. 다른 판단은 가장 강한 채널로 점수를 정한다 |
| Q17 | pass | ② 가 낮은 apple·oracle 은 세 경로를 각각 판정한 문장이 있고, "표준 없음" 하나로 깎지 않는다 |
| Q18 | pass | tesla.F5(SpaceX 관계사 제외)·spacex-xai.F5(Tesla 관계사 제외)가 같은 잣대이고, tesla.F3 은 관계사 자산(Starlink V5)을 자기 자산으로 세지 않는다 |
| Q19 | fail | **예외 없는 fail(같은 원인 Q03) — oracle.F5.** 받은 투자를 빼는 쪽은 anthropic·openai 가 일관된다. 그러나 "준 투자 = 능동 지분 동맹" 잣대는 microsoft 에만 댔고 oracle(Stargate·TikTok USDS 지분)에는 판정하지 않았다 |
| Q20 | fail | **승계 판단 예외 — TEN-RC-03(C-08).** 조달은 동맹에서 뺐다: apple 의 Gemini 구매, openai 의 Oracle $300B, anthropic 의 컴퓨트 구매, meta 의 칩 구매 |
| Q21 | fail | **승계 판단 예외 — TEN-RC-05 · TEN-RC3-04.** anthropic.F5 가 같은 3사 관계를 ⑤ 연동·⑧ 대체 불가에 한 번씩 세는 것을 명시한다 |
| Q22 | pass | alphabet.F7(SpaceX 지분 평가이익은 ⑥ 소관), amazon·tsmc·alibaba·apple·nvidia F7 이 영업외 이익을 ⑦ 입력에서 뺀다고 적는다 |
| Q23 | fail | **승계 판단 예외 — TEN-RA4-01.** meta.F2·alibaba.F2·anthropic.F2·openai.F2 문장이 하네스 미표기 수치를 비교 근거에서 뺀다고 적는다. openai.F2 는 자사 어댑터 하네스 99.9% 를 배제한다 |

예외 없는 fail 은 Q02·Q03·Q09·Q12·Q19 다. 원인 판단은 넷이다(nvidia.F3 · oracle.F5 · tesla.F4 · microsoft.F9). 승계 판단 예외로 적은 긴장 16개(TEN-RC-02·RC-03·RC-05·RB-Q10·RA-02·RC3-01·RC3-03·RC3-04·RC3-05·RA3-01·RC4-01·RC4-02·RC4-03·RC4-04·RA4-01·RA6-01)는 모두 `status: open`, `recheck_at: 2026-11` 이다.

**needs_fix 를 닫는 길(네 판단 공통, 하나를 고른다).**
- (가) 사람이 승인 페이지에서 판정 재료를 규칙대로 다시 매긴다. 고칠 대상은 nvidia.F3 의 acceleration·imitation, oracle.F5 의 A, tesla.F4 의 score, microsoft.F9 의 fcf_trend 다. 에이전트는 `propose` 로 근거를 붙여 올린다.
- (나) 규칙 파일 `open_tensions` 에 네 건을 recheck_at 과 함께 등록해 승계 판단 예외로 돌린다. 규칙 해시가 바뀌므로 calculate·draft 를 다시 돌린다.

어느 쪽이든 research → calculate → draft → 확인 리뷰를 거친다.

###### 다음 실행 과제
- anthropic.F3·openai.F3 별도 수익모델 사유를 규칙 기준(비모델 매출 또는 양의 단위경제)으로 다시 쓴다.
- tesla.F7 '내 돈이 돌아옴' 의 고리를 사람이 판정해 문장에 넣는다. 고리는 xAI 투자 → SpaceX 의 Megapack 구매 $329M/6개월이다.
- microsoft.F5 +2 근거에 Microsoft 의 Anthropic 지분 투자를 넣는다.
- palantir.F3 별도 수익모델 '부분' 사유를 채우거나 긴장으로 등록한다.
- tsmc·anthropic·openai F5 의 `counter_evidence` 를 완결된 현재 상태 문장으로 다시 쓴다(옛 문서 행 번호 삭제).
- spacex-xai.F4 부문 목록에서 Terafab 을 배치 전 사업으로 갈라 적는다.
- judgments.json 최상위 note 를 지금 상태로 고친다.
- 초안 고정 각주 "기준일 현재 유효한 약정" 을 관측 기준일 기준으로 고친다(amazon 여신). 또는 C-23 을 결정한다.
- TRG-057 condition 을 fired 상태에 맞게 고치고, TRG-080 source_ids 를 채운다.
- 이전 리뷰에서 넘어온 것(관측·규칙 불변이라 그대로 유지):
  - alibaba 여신 `mixed_as_of`·runway_effect 갱신.
  - oracle G4 분모를 C-26 과 함께 정리($288B).
  - net_cash 상장 지분증권·전략적 지분투자 우선순위(TSMC VIS).
  - tsmc·oracle F9 의 스톡 지표.
  - EV-amazon-008 microsoft 배정.
  - EV-microsoft-004 AI 귀속 단서.
  - Alibaba 9월 분기 트리거.
  - rules.md 8절 C-09·C-26.
  - CDAO "4사 공통" 서술(지금 문장도 "4사가 같이 받아" 로 남음).
  - 비상장 보정 ARR kind 기준.
  - research 발동 트리거 표의 `이번 실행에서 수정함`: 이제 문장 재작성만으로 TRG-080 ② 행도 "수정함" 이 돼, 판정 재료 변경과 문장 변경을 가르지 못한다. EV-oracle-003 문구는 고쳐져 닫혔다.

###### 이전 리뷰 기록

##### 확인 리뷰(2차) · rule-consistency — 규칙 일관성
2차 검토자: Claude Opus 5.5 · 규칙 일관성 독립 세션(이 실행을 만든 세션 아님) · 2026-10-06 · 확인 리뷰(2차)
2차 결과: pass
2차 요약: 1차 medium 두 건은 모두 닫혔다. 첫째, TRG-017 은 v1.9 일반 트랙과 P3 30.56%(30% 경계 바로 위)로 고쳐졌다. 둘째, preview 원인 분류는 렌더러 수정으로 바뀌었다. TSMC·Alibaba ⑥ 은 `📐 규칙(트랙 listed_annual→listed_ttm)·📊 관측`, Alibaba ⑨ 는 `📊 관측` 으로 나온다. 발동으로 바꾼 두 트리거의 판정은 규칙과 맞는다. TRG-057 은 ⑦ 판정표의 "큼 쪽에서는 세로축이 점수를 가르지 않는다" 와 ⑧ 근거 갱신 공시가 없다는 점을 근거로 유지했다. TRG-080 은 2.4 비AI 귀속(로켓·위성은 ①·③ 별도 수익모델·④ 에서만)에 따라 Starship 을 ② 가 아니라 ④ 로 보고, ④ 가 범위 맨 위라 유지했다. spacex-xai.F2 근거도 이미 "재사용 로켓·Starship 은 AI 게임체인저가 아니다" 로 같은 잣대다. research.md 「발동 트리거 재검토 대상」 표는 fired 2건 4행으로 trigger 상태와 맞는다. 다만 ⑦ 행의 `이번 실행에서 수정함` 은 근거 문장만 고친 것이라 오해 소지가 있다(low). 고친 숫자(런웨이 1.61년, 커버리지 2.66배, FCF −287억 달러, ⑥ 22.8·7.86·21.6%)는 관측·results 와 맞다. 점수·순위는 1차와 같다(results 의 입력 해시 가운데 evidence·triggers·sources 만 바뀜). 점수·순위·체크리스트 판정을 바꾸는 발견은 없다. 체크리스트 fail 13건은 1차와 같고 모두 승계 판단 예외다.

2차 검토 기준: results_hash `34248db45321ea0b…`, draft_hash `2af65e2f45bb0e34…`. review.md frontmatter 와 같은 값이고, results_hash 는 results.json 에서, 초안 sha256 은 파일에서 이 세션이 다시 계산했다.

확인한 것:
- `git diff cf958b4 HEAD`(08bfc90·6ae2ac9·96d522f): results.json 은 입력 해시 세 줄만 바뀌었다(점수 불변).
- 렌더러 diff 를 읽었고 `tests/test_preview_causes.py` 를 돌렸다(4 tests OK).
- triggers.json 80건을 봤다. 상태는 watching 56 · withdrawn 22 · fired 2 다. TRG-005·017·022·057·070·078·080 은 전문을 읽었다.
- evidence EV-oracle-003·004·006·007 의 숫자를 관측과 대조했다.
- judgments alibaba.F9.obsreg25(PRP-005)와 proposals 5건을 봤다.
- research.md 1014행 표.
- `validate_report_contract.py`: review 상태 외 전부 ok, 결정론적 재계산 ok.

###### 1차 발견 처리
| 1차 발견 | 상태 | 확인 내용 |
| --- | --- | --- |
| medium · TRG-017 연간 트랙 문장 | **닫힘** | observation 은 "규칙 v1.9 에서 TSMC ⑥ 은 6-K 반기 재무제표로 복원한 최근 1년(2025-07-01~2026-06-30, 대만 IFRS) … 일반 트랙이고, P3 는 30.56% 로 30% 경계 바로 위" 로 바뀌었다. recheck 는 "3분기 6-K 가 나오면 최근 1년 매출·순이익이 바뀐다 … 다음 실행에서 밴드가 바뀔 수 있다" 로 바뀌었다. results tsmc F6 `track: listed_ttm`, P3 0.3056(경계 표시 +1.9%)과 맞는다. 초안·research 표도 같은 문면이다 |
| medium · preview 변동 원인 분류 | **닫힘** | 원인별 결과:<br>• TSMC·Alibaba ⑥: `📐 규칙(트랙 listed_annual→listed_ttm)·📊 관측`.<br>• Alibaba ⑨: `📊 관측(가격·재무)`.<br>• Oracle ⑥: `📊 관측`(트랙 불변).<br>• Palantir·Tesla: 순위만 이동한 행이 추가됐다.<br>렌더러는 이번 실행 개정 가운데 previous.inputs/score 가 현재와 다른 것만 `판단 수정` 으로 본다. 테스트 4건이 통과한다. 규칙 5절(원인을 나눠 적고, 함께 작동하면 모두 적는다)과 맞는다 |
| low · alibaba 여신 `mixed_as_of` 미기록 | 다음 실행 과제 유지 | 관측 불변(basis.mixed_as_of 없음, runway_effect 3.0996 그대로) |
| low · oracle G4 분모 날짜(C-26) | 다음 실행 과제 유지 | 관측 불변 |
| low · net_cash 규칙 문면 충돌(VIS) | 다음 실행 과제 유지 | 규칙 불변 |
| low · ⑨ 근거의 스톡 지표(tsmc·oracle) | 다음 실행 과제 유지 | 판단 불변 |
| low · amazon 소멸 여신 "기준일 현재 유효" | 다음 실행 과제 유지 | 초안 1123행 그대로다. TRG-005 에 £4.25B 사채 발행 완료(현금 기준일 뒤)가 더해졌다. 이는 완충 정의(실제 들어온 현금만, 관측 기준일 기준)와 맞는다 |
| low · EV-amazon-008 Microsoft 미배정 | 다음 실행 과제 유지 | 불변 |
| low · EV-microsoft-004 AI 귀속 단서 | 다음 실행 과제 유지 | 불변 |
| low · Alibaba 다음 분기 트리거 없음 | 다음 실행 과제 유지 | 새 트리거는 TRG-080 하나다 |
| low · EV-oracle-006·007·TRG-022 낡은 숫자 | **닫힘** | 셋 다 "1.61년·2.66배(2026-08-31 관측)" 다. results oracle F9 G3 1.6145·G4 2.656 과 맞는다. EV-oracle-003·004 도 같고, FCF "약 −287억 달러" 는 fcf_ttm −28,720M 과 맞는다 |
| low · judgments note·source_ids·판정 주체 줄 | 다음 실행 과제 유지 | note "한 글자도 바꾸지 않았다" 그대로다(이제 이번 실행 반영 5건). F9 3건의 source_ids 는 `SRC-v15-html` 만 있다 |
| low · rules.md 8절 C-09·C-26 누락 | 다음 실행 과제 유지 | 문서 불변 |
| low · CDAO "4사 공통" 서술 | 다음 실행 과제 유지 | 불변 |
| info · 비상장 보정의 ARR kind 기준 | 다음 실행 과제 유지 | 불변 |

###### 바뀐 항목 확인
| 항목 | 판정 | 확인 내용 |
| --- | --- | --- |
| 렌더러 미리보기 원인 분류(08bfc90) | 맞음 | `판단 수정` 은 판정 재료가 바뀐 개정만 센다. ⑥ 트랙 변화는 규칙 원인으로 함께 적는다. 순위만 바뀐 기업도 행에 넣는다. 규칙 5절과 맞고, 테스트로 고정됐다 |
| TRG-057 expired → fired(Oracle ⑦·⑧ 유지) | 맞음 | **⑦ 유지:** 판정표에서 "조달 의존 고객 비중 큼" 이면 세로축이 점수를 가르지 않고 −2 가 범위 최저다. 10-Q 에 고객 집중 서술이 없어 두 축을 바꿀 새 사실이 없다. PRP-002 는 근거 숫자만 바꿨다(inputs 불변 확인).<br>**⑧ 유지:** "단일 고객이 백로그의 절반" 을 반박·갱신할 공시가 10-Q 에 없다(본문 'OpenAI' 0건). 집중도만으로 점수를 정하지 않는다는 ⑧ 지침과도 어긋나지 않는다.<br>**발동 판정 숫자:** ⑥ −2→−1(PER 22.83·EV/매출 7.858·성장 21.6%), ⑨ −3(런웨이 1.61년)이 results 와 맞는다. 미래 점수를 저장하지 않는다. |
| TRG-080 신설(SpaceX ②·④ 유지) · TRG-078 테슬라 몫만 철회 | 맞음 | **② 유지:** 2.4 "로켓·위성 통신 … 은 ①·③ 별도 수익모델·④ 에서만 센다. ② 는 AI 에 귀속되는 부분만" 을 그대로 댔다. 승계 spacex-xai.F2 근거도 "재사용 로켓·Starship 은 AI 게임체인저가 아니다 — 궤도 데이터센터가 실현되기 전까지는 ④ 에서만 센다" 라 같은 잣대다. 궤도 데이터센터(AI 컴퓨트)의 실제 제공·매출만 ② 재검토 조건으로 TRG-034 에 둔 것도 2.1(실측만)과 맞다.<br>**④ 유지:** spacex-xai.F4 = 5(범위 맨 위)이고, Starship 은 이미 부문으로 세고 있다.<br>**근거:** EV-spacex-xai-007 은 confirmed·F4 배정이다.<br>**TRG-078:** 테슬라 부분(Optimus 생산 미확인)은 TRG-030 으로 이었다. 중복 잇기 방침과 맞다. |
| research.md 「발동 트리거 재검토 대상」 | 맞음(문구 low) | fired 2건(TRG-057 ⑦·⑧, TRG-080 ②·④) 4행으로 triggers.json 과 같다.<br>"수정하지 않음" 3행은 oracle.F8·spacex-xai.F2·F4 가 carried 이고 개정 이력이 없는 것과 맞다.<br>⑦ 행 `이번 실행에서 수정함` 은 oracle.F7.fix52 개정(PRP-002)이 근거 숫자만 바꾼 것이라 사실이다. 그러나 트리거 finding 의 "⑦ 유지" 와 나란히 읽으면 판정이 바뀐 것으로 오해할 수 있다 |
| TRG-017·022·005·070 문면 | 맞음 | **TRG-017:** 위 처리와 같다.<br>**TRG-022:** 9/14 8-K 를 엘리슨 10b5-1 계획 취소로 보고 "일정·약정 변경 아님" 으로 판정했다. condition(일정·인식 시점·계약 조정) 문언과 맞다.<br>**TRG-005:** 사채 발행 완료분을 관측 기준일 뒤라 완충에 넣지 않았다. 계획 단계 $42B 는 넣지 않았다. ⑨ G3 완충 정의와 맞다.<br>**TRG-070:** Cursor 인수·협업 4건을 "Claude 사용 축소 아님" 으로 보고 관찰을 유지했다. condition 문언과 맞다. |
| evidence EV-oracle-003·004·006·007 | 맞음 | 숫자가 관측과 맞다. EV-oracle-004 의 "⑦ 판정표에 따라 이 선투자 위험은 ⑦ 이 아니라 ⑧·⑨" 는 ⑦ 지침(세로축은 고객에게 준 돈이지 내 설비에 태운 돈이 아니다)과 맞다 |
| judgments alibaba.F9.obsreg25 (PRP-005) | 맞음 | 취소선 줄이 "현재 점수와 경로는 다음 줄에 있다" 로 바뀌었다. inputs 불변(개정 이력 previous 와 같음)이고 점수 −4 그대로다 |

###### 체크리스트
2차 기준으로 다시 봤다. 이번 수정은 트리거·근거 문장·렌더러뿐이고 판정 재료·점수는 그대로라, 판정은 1차와 같다. 승계 판단 예외의 조건(fail 사유가 승계 판단의 기존 논리, 이번 실행이 그 잣대를 바꾸지 않음, `open_tensions` 에 recheck_at 2026-11 로 등록)은 그대로 선다.

| ID | 결과 | 근거 |
| --- | --- | --- |
| Q01 | fail | **승계 판단 예외 — TEN-RC-05 · TEN-RC3-04.**<br>• 변경분 통과. TRG-057 은 Oracle 선투자 위험을 ⑦ 이 아니라 ⑧·⑨ 에 두고, EV-oracle-004 와 같은 자리를 지킨다. TRG-080 은 Starship 을 ④ 한 곳에만 둔다.<br>• 승계 fail: nvidia F5·F8 의 고객 자체 칩 이탈, tesla F5·F8 의 NHTSA |
| Q02 | fail | **승계 판단 예외 — TEN-RC-02 · TEN-RC3-01 · TEN-RC3-03 · TEN-RC3-05 · TEN-RC4-02.**<br>• 변경분 통과. 비AI 사업(로켓)을 ② 지표로 쓰지 않는다(TRG-080). 완충에 넣는 것은 실현 현금뿐이다(TRG-005).<br>• 저심각 관찰(tsmc/oracle F9 의 스톡 지표, EV-microsoft-004)은 다음 실행 과제로 남는다 |
| Q03 | fail | **승계 판단 예외 — TEN-RC-03 · TEN-RC4-03.**<br>• 1차 Q03 결론(⑥ 트랙은 예탁증서 2사에만, 최근 1년 창은 전 기업 최신, 여신 기준 동일)은 그대로다. 이번 수정은 TSMC 트리거의 트랙 서술을 다른 기업과 같은 v1.9 기준으로 맞췄다.<br>• 비AI 귀속 잣대는 TRG-080 과 spacex-xai.F2 근거가 같고, tesla(④ 에서 에너지 저장)와도 같다.<br>• 승계 fail: C-08 이탈 조건 미통일, spacex-xai H 수 비교 |
| Q04 | pass | 상장 12사 ⑥ 은 비율 잣대(시총 ÷ 모회사 귀속 순이익, (시총−순현금) ÷ 매출)다. 시총 절대액을 쓰지 않는다. 변경 없음 |
| Q05 | fail | **승계 판단 예외 — TEN-RA-02 · TEN-RA3-01.** 변경분은 통과다. TRG-057 은 법정 제출본(10-Q), TRG-080 은 2차 매체를 확정 근거로 써서 판단을 바꾸지 않았다. 이해상충 표기는 판정에 넣지 않았다 |
| Q06 | pass | 볼륨 지표가 점수 재료로 든 곳이 없다. 변경 없음 |
| Q07 | pass | amazon.F3 의 "안 만든 것 자체는 카운터 포지셔닝이 아니다". 변경 없음 |
| Q08 | fail | **승계 판단 예외 — TEN-RC4-03.** 변경분에 ⑤ 판정이 없다 |
| Q09 | fail | **승계 판단 예외 — TEN-RA-02 · TEN-RA3-01 · TEN-RA6-01.**<br>• 변경분 통과. TRG-080 은 실현된 페이로드 배치(실측)만 봤다. 궤도 데이터센터는 실현 전이라 ② 에 넣지 않았다. TRG-005 는 계획 단계 사채·칩 매각을 근거·완충에서 뺐다.<br>• 트리거 80건에 점수 키·예상 점수가 없다(C-14) |
| Q10 | fail | **승계 판단 예외 — TEN-RB-Q10 · TEN-RC4-04.** ③ 변경 없음 |
| Q11 | pass | ⑨ 는 게이트 경로로 계산된다. 순적자 실격은 없다. 변경 없음 |
| Q12 | fail | **승계 판단 예외 — TEN-RC4-01 · TEN-RC3-05.** ③ 변경 없음 |
| Q13 | fail | **승계 판단 예외 — TEN-RC3-05.** 변경 없음 |
| Q14 | pass | 14사 door_closed 가 전부 fail 이다 |
| Q15 | pass | 공짜 사용자를 아군으로 세지 않는다. 변경 없음 |
| Q16 | fail | **승계 판단 예외 — TEN-RC-02 · TEN-RC4-02.** ① 변경 없음 |
| Q17 | pass | ② 를 "표준 없음" 하나로 깎지 않는다. spacex-xai.F2 는 성능·적응 두 경로 통과, 표준 실패로 4점이다(TRG-080 확인) |
| Q18 | pass | tesla·spacex-xai 상호 관계사 처리가 같은 잣대다. 변경 없음 |
| Q19 | pass | 받은 투자를 A 에 넣은 곳이 없다. 변경 없음 |
| Q20 | fail | **승계 판단 예외 — TEN-RC-03(C-08).** 변경분에 ⑤ 판정이 없다 |
| Q21 | fail | **승계 판단 예외 — TEN-RC-05 · TEN-RC3-04.** 변경분에 같은 속성을 양쪽에서 센 곳이 없다 |
| Q22 | pass | ⑦ 입력에 평가이익이 없다. TRG-057 의 ⑦ 판정도 두 축으로만 한다 |
| Q23 | fail | **승계 판단 예외 — TEN-RA4-01.** ② 변경 없음. TRG-080 은 벤치마크를 쓰지 않는다 |

fail 13건(Q01·02·03·05·08·09·10·12·13·16·20·21·23)이 인용한 긴장 16개(TEN-RC-02·RC-03·RC-05·RB-Q10·RA-02·RC3-01·RC3-03·RC3-04·RC3-05·RA3-01·RC4-01·RC4-02·RC4-03·RC4-04·RA4-01·RA6-01)는 모두 `status: open`, `recheck_at: 2026-11` 이다. 이번 실행이 고친 판단 5건(tsmc.F9·oracle.F9·oracle.F7.fix52·alibaba.F9.obsreg25, PRP-005 포함)은 어느 긴장의 대상에도 없다.

###### 다음 실행 과제
1차에서 유지된 것:
- alibaba.undrawn_credit.fix53 에 Oracle 과 같은 `mixed_as_of`(3-31 값 / 6-30 소비, 6월 분기 6-K 여신 언급 검색)를 남긴다. `runway_effect`·`score_dependence` 를 현재 값(여신 제외 1.87년·포함 2.17년, 점수 비의존)으로 고친다.
- oracle G4 분모를 C-26 결정과 함께 정리한다(10-Q 미개시 리스 $288B, 2026-08-31).
- `policies.f6.net_cash` 의 "상장 지분증권(include)" 과 "전략적 지분투자(excluded)" 우선순위를 정하거나, TSMC VIS 사례를 open_questions 에 등록한다.
- tsmc.F9·oracle.F9 근거의 스톡 지표(순현금·순부채·Debt/EBITDA·이자보상·Altman Z)를 빼거나 "교차검증용(2.8)" 으로 표시한다. oracle 의 옛 기간 값은 갱신하거나 지운다.
- amazon 여신: C-23 을 결정하거나, 초안 1123행 "런웨이는 기준일 현재 유효한 약정으로 계산했다" 를 관측 기준일(2026-06-30) 기준이라고 바로잡는다(Term Loan 미인출분은 2026-09-30 소멸).
- EV-amazon-008 을 microsoft ⑤ 에도 배정하거나 microsoft 근거에 같은 사건을 적는다.
- EV-microsoft-004 conditional_impact 에 TRG-053 과 같은 AI 귀속 단서를 넣는다.
- Alibaba 9월 분기 6-K 트리거를 만든다. 감시 대상은 ⑥ P1 경계 +3.4%, ⑨ 런웨이 2.17년, 여신 6월 말 값이다.
- judgments.json 을 정리한다.
  - 최상위 note 를 "승계 + 2026-10-01 반영 7건 + 2026-10-06 반영 5건(PRP-001~005)" 으로 고친다.
  - tsmc/oracle/alibaba F9 source_ids 에 6-K·10-Q 출처를 더한다.
  - alibaba.F9.obsreg25 "판정 주체" 줄을 정리한다.
- rules.md 8절 표에 C-09·C-26 을 더한다.
- CDAO "4사 공통" 서술 4곳을 Anthropic 배제 집행(EV-anthropic-010) 뒤 사실로 고친다.
- 비상장 ⑥ 보정의 `capital_efficiency` ARR kind 기준을 `arr_growth` 와 같게 할지 규칙에서 정한다.

2차에서 새로 본 것(모두 low, 점수 영향 없음):
- research.md 「발동 트리거 재검토 대상」 ⑦ 행의 `이번 실행에서 수정함` 을 "근거 문장 수정(판정 재료·점수 유지)" 처럼 갈라 적는다. 렌더러가 개정 이력 유무로 고르는 같은 문제가 이 표에 남아 있다.
- TRG-057 condition 의 "사건이 지나 기한이 끝났다" 는 expired 시절 문구다. fired 상태에 맞게 "실적·10-Q 공시로 충족됐다" 로 맞춘다.
- TRG-080 의 `source_ids` 가 비어 있다. EV-spacex-xai-007 의 출처를 트리거에도 적는다.
- EV-oracle-003 conditional_impact 의 "계산 입력이 2026-05-31 기준이라 … 갱신하고" 는 선별 당시 문장이다. 이번 실행에서 이미 갱신됐다는 사실을 덧붙인다.

###### 1차 리뷰 기록

##### 1차 · rule-consistency — 규칙 일관성
1차 검토자: Claude Opus 5.5 · 규칙 일관성 독립 세션(이 실행을 만든 세션 아님) · 2026-10-06 · 1차
1차 결과: pass
1차 요약: 14개사 판단 114건, 근거 72건 가운데 새 근거 34건 전부, 트리거 79건을 보고 규칙 v1.9 와 대조했다. 점수·순위·체크리스트 판정을 바꾸는 발견은 없다. 이번 실행이 새로 댄 잣대 셋은 모두 닿아야 할 회사에 닿았다. 첫째, ⑥ 트랙을 관측 기간으로 정하는 v1.9 규칙은 예탁증서 상장사 두 곳(TSMC `adr`, Alibaba `ads`)에만 해당하고, 둘 다 `listed_ttm` 이 됐다. 둘째, 분기 자료로 최근 1년을 복원하는 방식은 세 회사에 댔다. 나머지 11개사의 ⑥·⑨ 관측 창은 이미 기준일 시점의 최신 분기(2026-06-27/06-30/07-26)에서 끝나고, SpaceX 는 H1'24 자료가 없어 신규 상장 트랙에 남는 것이 맞다. 셋째, 미인출 여신과 순현금의 날짜 섞임은 점수에 닿지 않지만 회사마다 기록 방식이 다르다. Oracle 은 `mixed_as_of` 와 변동 검색을 남겼고, Alibaba 여신에는 그 기록이 없다(low). ③·⑤·⑦·⑥·⑨ 의 환산은 전 기업을 손으로 다시 계산해 엔진 결과와 맞췄다. 미결 결정 가운데 차단형(C-05·C-06·C-16)은 모두 run.json 에서 골랐다. 트리거 철회 22건의 사유는 규칙과 맞고, 미래 점수를 저장한 트리거는 없다. 체크리스트 fail 13건은 모두 승계 판단의 기존 논리에서 나왔다. 이번 실행은 그 잣대를 바꾸지 않았고, 모두 `open_tensions` 에 재검토 시점 2026-11 로 등록돼 있다(승계 판단 예외). medium 두 건이 있다. TRG-017 은 v1.9 와 반대로 "TSMC ⑥ 은 연간 트랙이라 분기 실적으로 P3 가 바뀌지 않는다" 고 적는데, 실제로는 P3 가 경계 +1.9% 에 있다. preview 의 변동 원인 분류도 규칙 5절과 어긋난다. 둘 다 점수에 닿지 않으므로 「다음 실행 과제」로 둔다.

1차 검토 기준: results_hash `1101644bc117e2a2…`, draft_hash `1168a515ee524414…`. review.md frontmatter 와 같은 값이고, draft.md 파일 sha256 은 이 세션에서 다시 계산해 확인했다.

검토 범위(전수):
- `judgments.json` 114건(승계 102 · new 12)을 표로 뽑아 전부 봤다. 종류, 입력, 상태, 검토자·검토일, 대체 기록, 개정 이력을 확인했다.
- 환산을 손으로 다시 계산했다.
  - ③: 14개사 통과점 → 사다리 결과.
  - ⑤: 3 + A + H.
  - ⑦: 판정표 4칸.
  - ⑥: P1·P2·P3 밴드 + P4 → 바닥 적용(상장 12사), 비상장 C-12 보정 2사.
  - ⑨: G1~G4 경로(14사).
  - 결과는 모두 results.json 과 같다.
- 관측 창: 14개사 ⑥·⑨ 입력 관측 160줄의 기준일·`period_basis`·`mixed_as_of` 를 확인했다. 미인출 여신 4건(amazon·spacex-xai·alibaba·oracle)은 basis 를 전문으로 읽었다.
- `scorecard/companies.json` 의 `share_basis` 로 예탁증서 상장사를 전수 확인했다.
- 근거 34건(reviewed_at 2026-10-06)은 relevance·conditional_impact 를 전부 읽었다.
- 트리거 79건을 전부 봤다. 미래 점수 키·문구를 검색했고, 철회 22건의 사유를 전부 읽었다.
- 그 밖에 본 것:
  - `proposals.json` 4건: 입력 불변 여부를 개정 이력의 previous 와 대조했다.
  - 규칙 `decisions` 29건과 `open_tensions` 18건.
  - `scorecard_cli.py diff`: 1층 위반은 판단 4건 수정·관측 53건 추가, 2층 위반은 3개사로, 재조사 사례라 예상된 결과다.
  - `validate_report_contract.py`: review 상태 외 전부 ok, 결정론적 재계산 ok.
  - 초안의 승계 표시 112줄 ↔ 판단 상태 대조: 불일치 0.

###### 1차 · 발견
| 등급 | 위치 | 발견 | 점수 영향 |
| --- | --- | --- | --- |
| medium | `triggers.json` TRG-017 observation·recheck(초안 1239행, research.md 882·949행) | **v1.9 와 반대되는 트랙 서술.**<br>• 트리거 문구: "TSMC ⑥ 은 20-F 연간 수치로 계산하는 트랙이다", "⑥ 매출 성장 잣대(P3)는 연간 트랙이라 분기 실적으로 입력이 바뀌지 않으므로, 분기 성장률은 2026 연간 20-F 가 들어올 때까지 참고로만 남긴다".<br>• 실제: v1.9 `track_by_period_basis` 로 TSMC 는 `listed_ttm` 이고, 6-K 반기·분기 자료로 최근 1년을 복원한다. 3분기 실적(2026-10-15) 6-K 가 나오면 P1·P2·P3 입력이 모두 바뀐다.<br>• 특히 P3 는 30.56% 로 경계 30% 에서 +1.9% 다(경계 표시 걸림). 이 트리거가 정확히 지켜봐야 할 곳을 "안 바뀐다" 고 막고 있다. | 없음(트리거는 점수를 저장하지 않는다). 다음 재채점의 감시 방향을 그르친다 |
| medium | `preview.md` 「이전 실행 대비」·「변동 원인 분류」 | **원인 분류가 규칙 5절과 어긋난다.** 5절은 "실적·사실 변화, 규칙 변경 … 서로 다른 원인이다. 여러 원인이 함께 작동하면 모두 적는다" 이다.<br>• TSMC ⑥ −3→−2 와 Alibaba ⑥ −4→−5 는 v1.9 트랙 변경(규칙 변경)과 관측 갱신이 함께 낸 결과다. 그런데 `📊 관측(가격·재무)` 하나로만 적혔다. 지시서도 TSMC 가 가격만 갱신했다면 −5 였다고 적는다.<br>• Alibaba ⑨ −3→−4 는 `✍️ 판단 수정` 으로 분류됐다. 그러나 PRP-003 은 근거 문장만 바꿨고, 게이트 입력은 개정 이력 previous 와 같다. 실제 원인은 관측 갱신이다(최근 1년 FCF −7,226M→−11,102M, 런웨이 3.10→2.17년). | 없음. 승인자가 읽는 원인 설명이 틀린다(출력 영역과 겹친다) |
| low | `observations.json` alibaba.undrawn_credit.fix53 ↔ oracle.undrawn_credit.rs1006 | **날짜 섞임을 회사마다 다르게 기록한다(Q03).**<br>• Oracle: 10-K(2026-05-31) 여신을 8-31 현금과 섞으면서 `mixed_as_of`(value/consumer 기준일, 10-Q 의 `revolv`·`credit facilit` 0건 검색, 재무활동 차입 유입 없음)를 남겼다.<br>• Alibaba: 3-31 여신 US$3,330M 을 6-30 현금과 섞었는데 관측에 `mixed_as_of` 가 없다. 6월 분기 6-K 에서 해지·인출 여부를 찾은 기록도 없다. 판단 문장에만 "(2026-03-31, 6월 말 값은 보도자료에 없음)" 이 있다.<br>• 같은 관측 basis 의 `runway_effect`(3.0996년)·`score_dependence`("총점 7 이 이 관측 하나에 달려 있다")도 낡았다. | 없음. 여신을 빼도 20,718 ÷ 11,102 = 1.87년으로 같은 1~3년 구간이다 |
| low | `observations.json` oracle.offbalance_B.v15 · results oracle F9 G4 | **G4 분자와 분모의 날짜가 다르다.**<br>• 분자 RPO 는 2026-08-31 값($664B)으로 갱신했다. 분모 B종 약정은 v1.5 legacy $250B(C-26 미결) 그대로이고, `coverage_comparable: yes` 다.<br>• 판단 문장이 적듯 같은 10-Q 가 미개시 리스 약정 $288B 를 공시한다. | 없음. 664 ÷ 288 = 2.31배로 1배 이상이다 |
| low | `observations.json` tsmc.net_cash.rs1006 `vis_remaining_stake` · 규칙 `policies.f6.net_cash` | **VIS 잔여 19% 를 넣으면서 규칙 문면 안의 충돌이 드러났다.**<br>• 규칙 `securities_scope.include` 의 "상장 지분증권" 과 `components.excluded` 의 "전략적 지분투자(환금 목적이 아닌 보유)" 가 부딪힌다. 주석 8 은 FVOCI 를 "held for medium to long-term purposes" 로 적는다.<br>• 포함 자체는 다른 회사 처리와 같은 잣대다. nvidia 의 시장성 지분증권(EquitySecuritiesFvNi)과 alibaba 상장주식을 넣는다. 그래서 회사 간 불일치는 아니다. | 없음. 빼면 순현금 $84.1B, P2 17.19 → 약 17.21 로 같은 −1 밴드다 |
| low | `judgments.json` tsmc.F9(PRP-004)·oracle.F9(PRP-001) evidence | **⑨ 근거에 스톡 지표가 남았다.** ⑨ 「쓰지 말 것」(순부채 잔고)과 `net_cash.scope_separation`(P2 순현금을 ⑨ 로 옮기지 말 것)에 걸린다.<br>• tsmc.F9 는 P2 정의의 "순현금 $86.5B(VIS 잔여 지분 포함 — 빼면 $84.1B)" 를 적는다.<br>• oracle.F9 는 "순부채 −$132.07B" 를 갱신했다. 그러나 Debt/EBITDA 5.03 · 이자보상 4.87 · Altman Z 2.18 은 옛 기간 값 그대로다.<br>• 이전 실행 low 와 같은 모양이고 엔진 입력이 아니다. | 없음 |
| low | 초안 1123행 · `observations.json` amazon.undrawn_credit.fix54 | **소멸한 여신을 "기준일 현재 유효" 로 적는다.**<br>• 지연인출 Term Loan $17.5B 의 미인출분은 2026-09-30 에 소멸했다(기준일 −6일). 364일 여신 $5.0B 는 2026-10 만기다.<br>• 그런데 초안은 "런웨이는 기준일 현재 유효한 약정으로 계산했다" 고 적는다. 엔진은 6-30 관측 37.5B 를 그대로 쓴다. C-23(잔존 기간)은 미결이다.<br>• 이전 실행 low 의 연장이고, 기준일이 늦어져 더 어긋났다. | 없음. 여신 0 이어도 6.7년이다 |
| low | `evidence.json` EV-amazon-008 | **같은 사건을 한 회사에만 배정했다(Q03).** EU 가 AWS 와 Azure 를 함께 DMA 심사 대상으로 본다는 보도를 Amazon ⑤ 에만 배정했다. microsoft ⑤(H −1 비용형)에는 배정하지 않았다. | 없음. 두 회사 모두 비용형 그대로다 |
| low | `evidence.json` EV-microsoft-004 conditional_impact | **AI 귀속분 없이 ③ 가속도를 재려 한다.** "같은 정의의 Azure 수준값이 세 분기 이상 모이면 ③ 후발 가속도를 정량으로 다시 판정한다" 고 적는다. 그러나 Azure 에는 비AI 매출이 섞여 있다. ③ 판정 지침("플랫폼 전체 성장률이 아니라 AI 에 귀속되는 부분만")과 2.4("비AI 매출의 성장은 ③ 가속도가 아니다")에 비추면 단서가 필요하다. TRG-053 recheck 에는 그 단서가 있다. | 없음 |
| low | `triggers.json` 전체 | **Alibaba 다음 분기 감시 트리거가 없다(Q03).** v1.9 로 Alibaba ⑥·⑨ 도 분기 6-K 로 갱신되는 회사가 됐다. 그런데 9월 분기 실적(11월 예상) 트리거가 없다. 미국 상장사는 3분기 10-Q 트리거가 있다(TRG-005·010·024·032·055). 지금 Alibaba 값은 P1 25.85(경계 +3.4%)와 런웨이 2.17년이다. | 없음 |
| low | `evidence.json` EV-oracle-006·007 relevance, `triggers.json` TRG-022 observation | **낡은 숫자.** "버티는 기간 약 1.3년 · 약정 커버리지 약 2.6배" 라고 적는다. 지금은 1.61년 · 2.66배다. | 없음 |
| low | `judgments.json` 최상위 note · tsmc/oracle/alibaba F9 source_ids · alibaba.F9.obsreg25 마지막 줄 | **기록이 실제와 어긋난다.**<br>• note: "항목은 한 글자도 바꾸지 않았다" 그대로다. 실제로는 이번 실행에서 4건(PRP-001~004)을 고쳤고, 이전 실행에서 7건을 고쳤다.<br>• source_ids: 새 숫자는 6-K·10-Q 출처에서 왔는데 `SRC-v15-html` 만 남아 있다.<br>• alibaba.F9.obsreg25: "판정 주체 설계진행(2026-09-11…)" 인데 검토자는 noble 2026-10-06 이다. | 없음 |
| low | `docs/scorecard/rules.md` 8절 | **사람용 문서에서 미결 결정 둘이 빠졌다.** v1.9.json 에서 pending 인 C-09(anthropic·openai ⑦ 매트릭스 입력)와 C-26(oracle B종 $250B 출처)이 「규칙에도 실행에도 답이 없는 것」 표에 없다. C-26 은 이번 실행 oracle G4 분모와 닿는다. JSON 이 기준이고 문서를 고쳐야 한다. | 없음 |
| low | `judgments.json` alphabet.F5·openai.F5.impl48·spacex-xai.F5·anthropic.F5.impl48 | **국방부 계약 서술이 낡았다.** "국방부 CDAO 계약 4사 공통이라 변별력 없음" 이 그대로다. 그런데 EV-anthropic-010(국방부가 Anthropic 도구 사용 중단)으로 실질은 3사가 됐다. 이전 실행 low 의 연장이다. | 없음. 어느 회사의 A 도 이 계약에 기대지 않는다 |
| info | results anthropic F6 `calc.correction` | **비상장 보정 두 조건이 런레이트를 다르게 다룬다.**<br>• `arr_growth` 는 run_rate kind 를 거부하는데, `capital_efficiency` 는 같은 run_rate ARR 로 0.52 를 계산해 met=true 다. 규칙 문면은 런레이트 배제를 성장률에만 명시한다.<br>• anthropic P2 는 30.0 으로 경계 정확히 위(30배 이상 −4)다. 비상장은 경계 표시를 하지 않는다. | 없음. require_all 이라 성장률 불인정으로 보정이 서지 않는다. 승계 입력이다 |

###### 1차 · 체크리스트
| ID | 결과 | 근거 |
| --- | --- | --- |
| Q01 | fail | **승계 판단 예외 — TEN-RC-05 · TEN-RC3-04.**<br>• 이번 변경분은 통과다. 같은 위험을 두 칸에서 센 곳이 없다.<br>&nbsp;&nbsp;– Alibaba ⑥ 은 P3 성장 −3 과 P4 영업외 비중 0.70, ⑨ 는 런웨이 2.17년과 G4 확인된 미공시다. 서로 다른 속성이다.<br>&nbsp;&nbsp;– Oracle ⑨ 런웨이 하향과 ⑧ −4(단일 고객 의존)도 다른 속성이다.<br>&nbsp;&nbsp;– 새 근거 EV-spacex-xai-009 는 ⑦(진위)·⑧(취약성) 양쪽 배정이 이중 계상이 아님을 스스로 적는다.<br>• 승계 fail: nvidia F5·F8 의 고객 자체 칩 이탈(TEN-RC-05), tesla F5·F8 의 NHTSA(TEN-RC3-04). 이번 실행은 두 판단의 잣대를 바꾸지 않았다. 둘 다 2026-11 재검토로 등록돼 있다 |
| Q02 | fail | **승계 판단 예외 — TEN-RC-02 · TEN-RC3-01 · TEN-RC3-03 · TEN-RC3-05 · TEN-RC4-02.**<br>• 변경분은 통과다.<br>&nbsp;&nbsp;– PRP-001~004 는 판정 재료를 그대로 두고 숫자만 최근 1년 관측으로 바꿨다(개정 이력 previous.inputs 와 현재 inputs 동일).<br>&nbsp;&nbsp;– ⑨ 완충은 현금 + 조건 확인된 확정 여신이다. Oracle 의 ATM 발행분은 8-31 현금에 이미 든 실현 현금이라 "예상 증자" 가 아니다.<br>&nbsp;&nbsp;– 새 근거 34건의 factor 배정은 칸 정의에 맞는다. 소송·규제는 ⑤ H, 고객 이탈은 ① 전환비용, 에너지 저장 배치는 비AI 사업이라 ④, 인도 대수는 현금이 아니라 ⑨ 유지로 배정됐다.<br>• 저심각 관찰(위 발견): tsmc/oracle F9 근거의 스톡 지표, EV-microsoft-004 의 Azure 전체 성장. 둘 다 점수 입력이 아니다 |
| Q03 | fail | **승계 판단 예외 — TEN-RC-03 · TEN-RC4-03.** 이번 실행이 새로 댄 잣대는 모두 닿아야 할 회사에 닿았다.<br>(1) **⑥ 트랙.** companies.json 의 예탁증서 상장사는 tsmc(adr)·alibaba(ads) 둘뿐이고 둘 다 `listed_ttm`·P4 기간 조건 미적용이 됐다. 나머지는 보통주다. spacex-xai 는 H1'24 사실이 어느 문서에도 없어 전년 TTM 이 복원되지 않는다(관측 basis.why_not_ttm). 그래서 `listed_newly` 에 남는다. 규칙 문면(전년 1년치를 복원할 기간 자료가 없음)과 맞는다.<br>(2) **최근 1년 복원.** 나머지 11개사의 ⑥·⑨ 관측 창은 이미 기준일 시점의 최신 확보 분기에서 끝난다.<br>&nbsp;&nbsp;– 대부분 2026-06-30, apple 06-27, nvidia 07-26 이다. 9월 분기 실적은 기준일까지 나오지 않았다.<br>&nbsp;&nbsp;– 새 분기가 있던 회사는 Oracle(8-31)뿐이고 갱신됐다.<br>&nbsp;&nbsp;– P4 자료 오래됨은 14사 모두 걸리지 않는다(경과 1~3개월).<br>(3) **미인출 여신.** Oracle 에도 amazon·spacex-xai·alibaba 와 같은 기준(감사 주석 1차·MD&A 교차·약정 준수·만기)으로 여신을 등록했다. FCF 음수 기업 4곳 모두 여신 관측이 있다. 날짜 섞임 기록 방식은 다르다(alibaba 기록 없음, low). 순현금 날짜 섞임은 alibaba 만 있고 `mixed_as_of: true` 로 기록됐다.<br>(4) **VIS 포함.** nvidia·alibaba 의 상장 지분증권 포함과 같은 잣대다.<br>• 승계 fail: C-08 별표 H 이탈 조건 전사 미통일(TEN-RC-03), spacex-xai H 수 비교(TEN-RC4-03). 이번 실행은 ⑤ 잣대를 바꾸지 않았다. 새 ⑤ 근거는 기존 H 정의(종류)를 댄 것이고 등급은 그대로다 |
| Q04 | pass | 상장 12사 ⑥ 은 parameters 모드다. P1 은 시총 ÷ 모회사 귀속 순이익, P2 는 (시총−순현금) ÷ 매출이고, 시총 절대액을 쓰지 않는다. 트랙이 바뀐 TSMC·Alibaba 도 같은 비율 잣대다. 세 회사의 순이익 관측은 모두 모회사 귀속분이다(alibaba "attributable to Alibaba Group Holding Limited", tsmc "Shareholders of the parent", oracle `NetIncomeLoss`). 비상장 2사는 밸류 ÷ 보정 매출 배수다 |
| Q05 | fail | **승계 판단 예외 — TEN-RA-02 · TEN-RA3-01.**<br>• 변경분은 통과다. 회사 성명 근거(EV-palantir-008 Armada 제휴, EV-oracle-006 홍수 성명)는 conditional_impact 가 "지금은 유지" 로 막아 두었고 점수 재료로 쓰지 않았다. 재무 갱신의 1차 근거는 10-Q·10-K·6-K 법정 제출본이다.<br>• 승계 fail: nvidia F2 5점의 벤더 발표 성능 근거(TEN-RA-02), openai F4 3→4 의 이해당사자 발표(TEN-RA3-01).<br>• 출처 장부의 이해상충 표기는 이 판정에 넣지 않았다(AGENTS.md 「금지·주의」) |
| Q06 | pass | ① 가격 결정력 근거는 매출 점유율·$/M 이다. 새 근거에 볼륨 지표가 점수 재료로 든 곳은 없다. EV-amazon-009 의 챗봇 추천 비중은 Prime·트래픽 실측이 아니라서 유지로 처리됐다. ⑥ P3 와 ⑨ 는 금액 기준이다 |
| Q07 | pass | amazon.F3 이 "모델을 안 만든 것 자체는 카운터 포지셔닝이 아니다" 라고 명시한다. 이번 실행은 ③ 을 바꾸지 않았다 |
| Q08 | fail | **승계 판단 예외 — TEN-RC4-03.**<br>• 변경분은 통과다. 새 ⑤ 근거 21건은 적대를 종류로 분류했다.<br>&nbsp;&nbsp;– 비용형: 손해배상·규제 조사·시장 일부 차단.<br>&nbsp;&nbsp;– 구조형: 팔란티어 정당성 겨냥.<br>&nbsp;&nbsp;– 다발형 요건: "최대 파트너와도 긴장" 을 따로 확인한다(EV-palantir-009·010).<br>• 승계 fail: spacex-xai.F5 "동맹이 적보다 확실히 많지 않음"(수 비교) |
| Q09 | fail | **승계 판단 예외 — TEN-RA-02 · TEN-RA3-01 · TEN-RA6-01.**<br>• 변경분은 통과다.<br>&nbsp;&nbsp;– 계획·예정 근거는 모두 "지금은 유지" 로 처리됐다: 노르웨이 판매 금지 계획, Hugging Face 인수 서명, Armada 제휴 발표, Broadcom 대출 보도.<br>&nbsp;&nbsp;– oracle.F9 의 "2026년 $45~50B 추가 조달 예정" 과 tsmc.F9 의 capex 가이던스는 엔진 입력이 아닌 서술이다.<br>&nbsp;&nbsp;– Alibaba 8월 증자는 현금 관측 기준일 뒤라 완충에 넣지 않았다.<br>&nbsp;&nbsp;– 트리거 79건에 점수 키·예상 점수 문구가 없다. TRG-041 은 "옛 척도의 예상 점수 문장은 옮기지 않았다" 고 적는다(C-14).<br>• 승계 fail: 위 세 긴장 |
| Q10 | fail | **승계 판단 예외 — TEN-RB-Q10 · TEN-RC4-04.** 이번 실행은 ③ 을 바꾸지 않았다. 새 ③ 근거 EV-microsoft-004·EV-tesla-007 은 "유지" 다(EV-microsoft-004 의 AI 귀속 단서는 위 low) |
| Q11 | pass | ⑨ 는 게이트 경로로 계산된다.<br>• spacex-xai: 손실률 −16.2% 구간 −3.<br>• amazon·oracle·alibaba: FCF 음수 −2 에서 런웨이 사다리.<br>• anthropic·openai: 비상장 미공시 경로 −2.<br>순적자만으로 실격시킨 판단은 없다. spacex-xai 는 순손실이라 P1 을 만들지 않았고 감점하지도 않았다 |
| Q12 | fail | **승계 판단 예외 — TEN-RC4-01 · TEN-RC3-05.** ③ 사다리는 엔진이 적용한다. 14사 통과점 → 점수를 다시 계산해 모두 맞았다. 모방 불가능성이 pass 가 아닌 2.5점 두 곳(alibaba·spacex-xai)은 3으로 상한이 걸렸다 |
| Q13 | fail | **승계 판단 예외 — TEN-RC3-05.** alibaba.F3 이 회수 장치 없는 오픈웨이트를 imitation=partial 로 둔 것이다(긴장의 두 번째 사유). 이번 실행은 바꾸지 않았다 |
| Q14 | pass | 14사 F3 의 door_closed 가 전부 fail 이라 5점이 없다 |
| Q15 | pass | 공짜 사용자를 아군으로 세지 않는다는 잣대가 같다. nvidia.F5 는 개발자 1,800만을, alibaba.F5 는 파생모델 15만을 불인정했고, meta.F5 는 Glimmer 개발자를 무효로 봤다. 새 근거 EV-nvidia-013(Reflection)은 Nemotron 공동개발 관계로만 세고 사용자 수를 쓰지 않는다 |
| Q16 | fail | **승계 판단 예외 — TEN-RC-02 · TEN-RC4-02.** 이번 실행은 ① 을 바꾸지 않았다. 새 ① 근거 넷은 각 회사의 실질 채널로 배정됐다. EV-anthropic-011 은 업무 채널, EV-palantir-011 은 업무 전환비용, EV-amazon-009 는 소비자, EV-nvidia-009 는 부품 상한이다 |
| Q17 | pass | ② 가 낮은 apple(2)·oracle(2)도 세 경로 판정 근거가 있고, "표준 없음" 하나로 깎지 않았다. 이번 실행은 ② 를 바꾸지 않았다 |
| Q18 | pass | 관계사를 동맹으로 세지 않는다. tesla.F5 는 유일한 아군이 관계사 SpaceX 라 A=0 이고, spacex-xai.F5 는 Tesla 를 동맹에서 뺐다 |
| Q19 | pass | anthropic.F5.impl48·openai.F5.impl48 이 받은 투자를 A 에서 뺐다. 새 근거 가운데 받은 투자를 A 로 올린 것은 없다. EV-nvidia-013 은 NVIDIA 가 준 투자이고, ⑦ 환류와 겹치지 않게 ⑤ 에서는 공동개발만 센다 |
| Q20 | fail | **승계 판단 예외 — TEN-RC-03(C-08).**<br>• 변경분은 통과다.<br>&nbsp;&nbsp;– EV-anthropic-009(Broadcom 칩 임차 대출)는 "조달(돈 주고 사 오는 관계)" 로 분류돼 ⑤ 가 아니라 ⑧·⑨ 로 갔다.<br>&nbsp;&nbsp;– EV-palantir-008(Armada 공동 제공)은 네 질문 1·2번(재판매·연동)으로 동맹 후보다. +2 조건 불성립도 확인했다.<br>• 승계 fail: 별표 H 이탈 조건 전사 미통일. 이번 실행은 이 잣대를 바꾸지 않았다 |
| Q21 | fail | **승계 판단 예외 — TEN-RC-05 · TEN-RC3-04.**<br>• 변경분은 통과다. EV-spacex-xai-009 는 ⑦(진위)·⑧(취약성)의 독립을 적는다. EV-anthropic-011 은 Microsoft 를 ⑤ 동맹(유통)과 이탈 가능성(3문) 양쪽에서 보되 ⑧ 로 같은 속성을 다시 세지 않는다.<br>• 승계 fail: 위 두 긴장 |
| Q22 | pass | ⑦ 14건 모두 관측 입력이 없고, 두 축이거나 승계 점수다. oracle.F7(PRP-002)의 갱신은 RPO·매출 숫자뿐이다. TRG-003 은 "평가이익은 ⑦ 의 증거가 아니다(⑥ 소관)" 로 처리했다. 영업외 비중은 ⑥ P4 에만 쓰인다(C-11 block_carryover) |
| Q23 | fail | **승계 판단 예외 — TEN-RA4-01.** 이번 실행은 ② 를 바꾸지 않았다. 새 근거에 하네스 간 비교로 점수를 움직인 것은 없다. TRG-001 은 벤더 발표 벤치마크를 방증으로만 보고 독립 측정을 기다린다 |

승계 판단 예외의 공통 조건을 확인했다.
- fail 사유가 모두 `carried_score`(또는 그 기존 논리)다.
- 이번 실행은 ⑥ 트랙과 ⑥·⑨ 관측 창만 바꿨다. 위 fail 의 잣대(①②③⑤⑦⑧ 정성 기준)는 건드리지 않았다.
- fail 13건(Q01·02·03·05·08·09·10·12·13·16·20·21·23)이 인용한 긴장 16개(TEN-RC-02·RC-03·RC-05·RB-Q10·RA-02·RC3-01·RC3-03·RC3-04·RC3-05·RA3-01·RC4-01·RC4-02·RC4-03·RC4-04·RA4-01·RA6-01)는 모두 `status: open`, `recheck_at: 2026-11` 이다.
- 이번에 고친 판단 4건(tsmc.F9·oracle.F9·oracle.F7.fix52·alibaba.F9.obsreg25)은 어느 긴장의 대상에도 없다.

###### 1차 · 다음 실행 과제
- TRG-017 을 v1.9 에 맞게 고친다. "TSMC ⑥ 은 `listed_ttm`(6-K 로 최근 1년 복원)이고, 3분기 6-K 가 P1·P2·P3 입력을 바꾼다. P3 30.56% 는 경계 +1.9%" 로 적고, ⑥ 재계산을 recheck 에 넣는다. 승인 전에 고쳐도 비용이 작다(트리거 문장만).
- preview 의 변동 원인 분류를 규칙 5절에 맞춘다.
  - TSMC·Alibaba ⑥ 에는 "규칙 변경(v1.9 트랙) + 관측 갱신" 을 함께 적는다.
  - Alibaba ⑨ 는 "관측 갱신(최근 1년 FCF·현금)" 으로 적는다. 판단 수정이 아니다.
  - 렌더러가 개정 이력 유무만으로 `판단 수정` 을 고르지 않게, 입력이 바뀌었는지를 본다.
- alibaba.undrawn_credit.fix53 에 Oracle 과 같은 모양의 `mixed_as_of`(value 3-31 / consumer 6-30, 6월 분기 6-K 의 여신 언급·재무활동 차입 유입 검색 결과)를 남긴다. `runway_effect`·`score_dependence` 도 지금 값(1.87/2.17년, 점수 비의존)으로 고친다.
- oracle G4 분모를 C-26 결정과 함께 정리한다. 10-Q 의 미개시 리스 $288B(2026-08-31)를 같은 날짜 분모 후보로 등록하고, `coverage_comparable` 판정 근거에 날짜를 적는다.
- 규칙 파일 `policies.f6.net_cash` 에서 "상장 지분증권(include)" 과 "전략적 지분투자(excluded)" 의 우선순위를 정한다. 그 전까지는 open_questions 나 긴장에 TSMC VIS 사례를 등록한다.
- tsmc.F9·oracle.F9 근거의 스톡 지표(순현금·순부채·Debt/EBITDA·이자보상·Altman Z)를 ⑨ 근거에서 빼거나 "교차검증용(2.8)" 으로 표시한다. oracle 의 Debt/EBITDA 등은 옛 기간 값이라 갱신하거나 지운다.
- amazon 여신: C-23 을 결정하거나, 초안 각주 "런웨이는 기준일 현재 유효한 약정으로 계산했다" 를 "관측 기준일(2026-06-30) 약정으로 계산했다. Term Loan 미인출분은 기준일 전 소멸" 로 바로잡는다.
- EV-amazon-008 을 microsoft ⑤ 에도 배정하거나, microsoft 쪽 근거에 같은 사건을 적는다.
- EV-microsoft-004 conditional_impact 에 TRG-053 과 같은 AI 귀속 단서를 넣는다.
- Alibaba 9월 분기 실적(6-K) 트리거를 만든다. 감시 대상은 ⑥ P1 경계 +3.4%, ⑨ 런웨이 2.17년, 여신 6월 말 값 확인이다.
- 낡은 숫자를 고친다. EV-oracle-006·007 relevance 와 TRG-022 observation 의 "1.3년·2.6배" 를 "1.61년·2.66배" 로 바꾼다.
- judgments.json 을 정리한다.
  - 최상위 note 를 "승계 + 2026-10-01 반영 7건 + 2026-10-06 반영 4건(PRP-001~004)" 으로 고친다.
  - tsmc/oracle/alibaba F9 source_ids 에 새 6-K·10-Q 출처를 더한다.
  - alibaba.F9.obsreg25 의 "판정 주체" 줄을 정리한다.
- rules.md 8절 「규칙에도 실행에도 답이 없는 것」 표에 C-09·C-26 을 더한다(v1.9.json 과 맞춘다).
- CDAO "4사 공통" 서술 4곳을 Anthropic 배제 집행(EV-anthropic-010) 뒤 사실로 고친다.
- 비상장 ⑥ 보정에서 `capital_efficiency` 의 ARR kind 기준을 `arr_growth` 와 같게 할지 규칙에서 정한다.
