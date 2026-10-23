---
reviewer_agent: fact-checker
session: claude-q3b-facts-2026-10-23
reviewed_at: 2026-10-23
area: facts
---
검토자: fact-checker (claude-q3b-facts-2026-10-23)
결과: needs_fix

## RESULT

- 새 근거 16건(EV-anthropic-164~172, EV-openai-182~188)은 전부 URL 이 열리고 발췌가 원문과 글자 그대로 같다. 발행시각은 모두 정보 컷오프(2026-10-23) 이하이고 출처는 모두 `sources.json` 에 있으며 `confirmed` 근거에는 검토자·검토일이 있다.
- Anthropic ⑤ 가 묶임 증거로 쓴 Amazon 10-Q 금융 한도(EV-amazon-086·078·087)는 원문 같은 문단에 있고 "컴퓨트 인도 이정표" 조건과 잔액 $15.0B 를 받친다. Google 조건부 $300억(EV-anthropic-172)은 Bloomberg Law 전재본 첫 화면 본문에 있고 "성과 목표" 조건을 받친다.
- 판단 18건(anthropic 9, openai 9)의 올릴·내릴 근거 265줄은 전부 `[EV-…]` 표지로 끝나고, 표지가 가리키는 근거는 모두 존재·`confirmed`·출처 등록이다. 이전 트리거 29건의 carry 는 새 후보 107건 전수 대조와 일치한다. 새 트리거 4건의 근거는 모두 confirmed 다.
- 그러나 OpenAI ⑤ 가 Microsoft 를 "헤지 확인"으로 읽은 근거가 규칙 문언("내렸거나 그 자리에 경쟁 모델·제품을 올린 것이 확인될 때")을 받치지 못한다(F-1). 이 읽기가 OpenAI ⑤ 동맹 2 와 3 을 가르므로 점수에 닿는다.

## FINDINGS

### F-1 (높음, 점수에 닿음) OpenAI ⑤ — Microsoft "헤지 확인"의 근거가 "그 자리에 올림"을 받치지 못한다

- 파일·항목: `judgments.json` `openai.F5.impl48` 의 `evidence` 넷째 문단(Microsoft)과 `evidence_down` 의 EV-microsoft-010·EV-microsoft-015·EV-alibaba-073·EV-microsoft-074 줄.
- 무엇이: 판정 칸이 "Microsoft 는 GitHub Copilot 에 자체 모델 MAI-Code-1-Flash 를 넣어 … 헤지도 Microsoft 1차 발표로 확인된다", "Copilot 이 OpenAI 모델을 내리지 않았어도 헤지가 확인된 Microsoft 는 주력 편입이 있어도 세지 않는다"고 쓴다. 주력 편입은 같은 문단이 확인했다고 적는다(EV-openai-122, EV-microsoft-071).
- 근거(원문 대조):
  - EV-microsoft-010(Microsoft FY26 4분기 통화록, 원문 일치)은 MAI-Code-1-Flash 를 GitHub Copilot 에서 쓴다고 하면서 같은 문장에서 "while still having access to frontier capabilities from OpenAI and Anthropic" 이라고 적는다. OpenAI 모델을 내렸다는 말도, 그 자리를 MAI 가 대신했다는 말도 없다. 판정 칸 스스로 "OpenAI 모델을 내리지 않았어도"라고 인정한다.
  - EV-microsoft-015(Claude 를 Copilot 제품군에서 계속 제공)와 EV-microsoft-074(Anthropic 지분 평가이익)는 다른 회사 모델을 나란히 쓰거나 다른 회사에 출자했다는 사실이다. 규칙 3절 ⑤ 는 이것만으로는 묶임이 풀리지 않는다고 적는다.
  - 규칙 문언에 가장 가까운 사실은 EV-alibaba-073(The New Stack, 발췌 일치)이다. Microsoft 가 Foundry 의 결정 모델을 OpenAI 것 대신 Alibaba Qwen 후학습으로 만들었다는 보도인데, 같은 발췌가 "plans to rebase it soon on its own MAI models as well as OpenAI's" 라고 적어 OpenAI 모델도 계속 쓸 계획이다. 이 사실은 Copilot 이 아니라 Foundry 의 한 모델이고, 판정 칸은 이것을 헤지의 직접 근거로 따로 세우지 않았다.
- 점수에 닿는 이유: Microsoft 가 지분 동맹으로 세어지면 OpenAI ⑤ 동맹이 2 에서 3 이 되어 12+3−8.32=6.68 로 7 이 된다(현재 6).
- 고치는 법: 둘 중 하나로 한다.
  - (a) Microsoft 를 헤지로 읽으려면 판정 칸에서 "Copilot 이 OpenAI 모델을 내리지 않았어도" 문장을 지우고, 헤지의 근거를 "OpenAI 의 자리에 경쟁 모델을 올린 확인된 사건"(EV-alibaba-073)으로 명시한다. 그 사건이 Microsoft 의 주력(Copilot)에 닿는지, OpenAI 모델도 계속 쓴다는 같은 발췌의 문장까지 판정 칸에 적는다. EV-microsoft-010 은 "자체 모델 보유·공존"의 근거로만 쓰고 헤지 근거에서 뺀다.
  - (b) 그 근거로 헤지를 확정할 수 없으면 주력 편입이 확인된 Microsoft 를 지분 동맹으로 세고 헤지 확인 문장을 미확인으로 바꾼다.
  - 어느 쪽이 규칙 문언에 맞는지는 규칙 일관성 영역이 가른다. 사실 영역의 판정은 "EV-microsoft-010 은 '그 자리에 올림'을 받치지 않는다"이다.

### F-2 (중간, Q03 소관·사실 영역 관찰) OpenAI ⑤ 판정 칸이 "헤지가 확인된다"고 쓴 Amazon 근거가 같은 실행의 Anthropic ⑤ 에서는 "헤지 아님"으로 읽힌 사실과 같다

- 파일·항목: `openai.F5.impl48` `evidence` 다섯째 문단(Amazon)과 열째 문단 가까이의 Bedrock·Azure 되팔기 단락, `anthropic.F5` `evidence` 셋째 문단(Amazon).
- 무엇이: OpenAI 쪽은 "Bedrock 은 자체 Nova 를 비롯한 여러 회사 모델을 바꿔 쓰게 하고 Amazon 은 Anthropic 에도 출자했으며 … 헤지가 확인된다"고 쓴다. Anthropic 쪽은 같은 사실(Nova, OpenAI 협력 계약, OpenAI 출자)을 보고도 "Bedrock 에서 Claude 를 내리거나 자리를 바꿨다는 확정 근거는 없어 좁은 읽기로 헤지가 아니다"라고 쓴다.
- 근거: Amazon 을 OpenAI 에서 세지 않는 실제 이유는 남은 추가 출자 약정 없음(EV-amazon-019·020. Amazon 10-Q 원문의 OpenAI 문단에 "milestone" 문구가 없고 남은 $21.3B 는 6-30 뒤 모두 집행됐음을 확인했다)과 주력 편입 미확인이다. 이 결론은 사실로 받쳐진다. 문제는 "헤지가 확인된다"는 문장이 규칙의 좁은 읽기와 어긋난다는 점이다.
- 고치는 법: OpenAI 판정 칸의 Amazon·Bedrock·Azure 단락에서 "헤지가 확인된다" 표현을 빼고 묶임 증거가 없다는 이유만 남긴다. 점수는 바뀌지 않는다. F-1 과 함께 고치면 된다.

### F-3 (낮음, 점수 불변) Anthropic ⑤ 의 "다른 음악 출판사 소송은 확정 근거에 없다(미확인)" 문장이 인용한 Billboard 기사와 어긋난다

- 파일·항목: `anthropic.F5` `evidence` 열넷째 문단, EV-anthropic-164.
- 무엇이: Billboard 기사(EV-anthropic-164 원문 본문 여덟째 문단)는 "Anthropic … has faced numerous such lawsuits across industries, including ongoing cases from music firms" 라고 적는다. 발췌에는 없지만 근거가 가리키는 같은 원문에 음악 회사의 진행 중 소송이 있다. 판정 칸은 "확정 근거에 없다"고 쓴다.
- 점수에 닿지 않는 이유: 비용형 전선의 관할 수(미국·EU)는 같은 미국 전선이 하나 더 늘어도 변하지 않는다. 구제 조치 진행 여부는 기사에 없다.
- 고치는 법: "Billboard 는 음악 회사들의 진행 중 소송이 더 있다고 적지만 사건·청구·구제 내용은 없다(미확인)"로 바꾼다. EV-anthropic-164 의 `unverified` 칸에도 같은 문장을 더한다.

### F-4 (낮음, 점수 불변) 인용·표기 정밀도

- EV-alphabet-018(Fortune)은 "commitments of up to $30 billion more" 라고만 적고 성과 조건을 적지 않는다. Google 이 묶였다는 조건 부분은 EV-anthropic-172 만 받친다. 그 등급이 회사 발표를 전한 2차 보도라는 점은 판정 칸이 이미 적고 있다. Alphabet 2026-06-30 10-Q 본문에는 "Anthropic" 이 한 번도 나오지 않아 공시로 올릴 수는 없다. 수정 불필요, 확인용 기록이다.
- `openai.F5.impl48` 판정 칸의 "NVIDIA 는 2026-03 라운드를 이끈 투자자이고 OpenAI 에 $300억을 넣었다고 보도됐다"에서 $300억은 EV-nvidia-043(원문 발췌 "$30 billion check")이 받치지만 이 판단은 그 근거를 인용하지 않았고 "라운드를 이끈"은 확인하지 못했다. 근거 ID 를 달거나 "이끈"을 뺀다.
- TRG-036 carry 의 "EDGAR 회사명 검색에서 Anthropic 이름의 제출인이 나오지 않아"는 부정확하다. 같은 검색(2026-10-23 05:20 UTC 재현, 35건)에는 'Anthropic …' 이름의 투자 SPV 펀드 35곳만 나오고 Anthropic PBC 본인은 없다. 결론(공개 제출본 없음)은 맞다. "Anthropic PBC 의 제출인은 나오지 않아"로 고친다.
- TRG-380 조건의 "금융 한도가 줄거나 끝나면"은 Series H 처럼 한도 아래 출자를 집행하면 한도 잔액이 줄어드는 구조(10-Q: $20.0B → $15.0B)와 겹쳐 뜻이 모호하다. "집행으로 줄어드는 것은 제외, 만료·철회·감액이 공시되면"으로 다시 쓴다.

## 검증 요약

### 새 근거 16건 원문 대조

방법: 일반 매체는 curl(기본 User-Agent)로 받아 발췌 문장을 글자 그대로 대조했다. 403 이 난 곳은 앱 안 브라우저·Playwright 로 열어 대조했다. 앱 안 브라우저에서 접근 거부가 난 CNBC 는 우회하지 않고 Playwright 에서 열린 페이지만 읽었다. 발췌의 `…` 는 문단 사이 생략이고 각 구간을 따로 대조했다.

| 근거 | 열림 | 발췌 | locator | 비고 |
| --- | --- | --- | --- | --- |
| EV-anthropic-164 Billboard | curl 200 | 일치 | 일치(본문 3·6번째 문단) | 같은 기사 8번째 문단은 F-3 |
| EV-anthropic-165 Google Cloud 블로그 | curl 200 | 일치 | 일치 | |
| EV-anthropic-166 PYMNTS | curl 200 | 일치 | 일치 | |
| EV-anthropic-167 Motley Fool | curl 200 | 일치 | 일치 | 유출 S-1 수치를 옮긴 보도, 판단에 인용 안 됨 |
| EV-anthropic-168 Crunchbase News | curl 200 | 일치 | 일치 | 유출 S-1 수치, 판단에 인용 안 됨 |
| EV-anthropic-169 Newcomer | curl 200 | 일치 | 일치 | |
| EV-anthropic-170 Morningstar | curl 403, 앱 안 브라우저 열림 | 일치 | 셋째 문단 일치 | |
| EV-anthropic-171 Motley Fool | curl 200 | 일치 | 일치 | 발췌의 수익성 문장은 유출 수치를 옮긴 것이며 판단에 쓰이지 않음 |
| EV-anthropic-172 Bloomberg Law | curl 200 | 일치 | 일치 | 유료 벽 앞 첫 화면 본문, 발행일 2026-04-24(금) 일치 |
| EV-openai-182 CNBC | curl 403, 앱 안 브라우저 접근 거부, Playwright 열림 | 일치 | 일치 | 서명 목표 "다음 주 말"이 같은 기사에 있고 TRG-379 의 10-30 전후가 이를 옮김 |
| EV-openai-183 Bloomberg | curl 403, Playwright 열림 | 일치 | 일치 | 게시 2026-10-23 08:31 GMT+9 = 22:31Z, 근거 시각과 일치 |
| EV-openai-184 SiliconANGLE | curl 200 | 일치 | 일치 | |
| EV-openai-185 TNGlobal | curl 403, Playwright 열림 | 일치 | 일치 | |
| EV-openai-186 OpenAI(Uber) | curl 403, Playwright 열림 | 일치 | 일치 | |
| EV-openai-187 Key Context | curl 200 | 일치 | 일치 | |
| EV-openai-188 The New Stack | curl 200 | 일치 | 일치 | Anthropic·Google 이 지원 목록에 없다는 TRG-364 문장도 같은 기사에서 확인 |

### Amazon 10-Q·Google·Microsoft 근거

- EV-amazon-086·078·087: `sec-get` 로 받은 10-Q(2026-06-30) 원문의 Note 2 Anthropic 항목 한 문단(여섯 문장)에서 발췌가 글자 그대로 같다. locator 의 문장 순서(넷째·다섯째, 셋째·마지막, 마지막)가 맞고 문단은 Series H 문장으로 끝난다. "expire 30 months after an Anthropic liquidity event", "delivery milestones of compute capacity", 잔액 $15.0B 가 모두 있다. 판단의 "이정표 조건부 추가 출자 약정" 읽기는 원문을 받친다.
- EV-amazon-039(Anthropic 발표): curl 로 발췌 일치. 10-Q 의 Series G $5.0B + 한도 $20.0B 와 맞는다.
- EV-alphabet-018(Fortune): Playwright 로 일곱째 문단 발췌 일치(조건 표현의 한계는 F-4).
- EV-microsoft-010·015: curl 로 발췌 일치. EV-microsoft-014(10-K)는 `sec-get` 원문에서 "$13.0 billion … $11.9 billion funded" 가 일치하고 남은 몫의 조건을 적지 않는다는 서술도 원문과 맞다. OpenAI ⑤ 의 "미확인"은 `unverified` 로 쓰였고 확인된 미공시와 섞이지 않았다.
- OpenAI ⑤ 의 부정 주장 두 건을 원문으로 재현했다. Amazon 10-Q 의 OpenAI 항목에는 이정표 문구가 없고 남은 $21.3B 는 6-30 뒤 모두 집행됐다. NVIDIA 2026-04-26·2026-07-26 10-Q 본문에서 OpenAI 가 나오는 곳은 PORTS-Pike 보증 문장뿐이고 출자 약정 문장은 없다.
- Anthropic ⑤ 의 AMD 미계상 근거: AMD 보도자료 원문(curl 200)에 "committed to make a strategic equity investment of up to $5 billion … in the future" 외에 시기·조건·이정표·독점 문구가 없다. EV-anthropic-119 발췌와 일치한다.

### 판단 18건 표지 전수

- 대상: anthropic.F1.claude·F2.model·F3.model·F4·F5·F6·F7·F8·F9 와 openai.F1.chatgpt_api·F2.model·F3.model·F4·F5.impl48·F6·F7·F8·F9. 전부 `status: new`, `reviewer`·`reviewed_at` 있음.
- `evidence_up`·`evidence_down` 합계 265줄 모두 줄 끝이 `[EV-…]` 표지다. 표지·본문·`inputs` 가 가리키는 모든 EV ID 가 `evidence.json` 에 있고 전부 `confirmed`(전체 1,679건 `confirmed`, 검토자·검토일 결손 0)다. `source_ids` 는 전부 `sources.json` 에 있다. 후보(`candidate`) 인용 0건.
- 표지와 줄 내용의 대응은 숫자 대조로 훑었다. 44줄이 불일치로 걸렸으나 억·B 단위 변환, 날짜 표기, 계산값이 원인이다. 사실 오류로 확인된 줄은 없다. 이 대조는 숫자 기준이라 서술 의미까지 전수로 읽은 것은 아니다. 새 근거를 인용하는 줄과 OpenAI ⑤ Microsoft·Amazon 줄은 원문으로 따로 읽었다.
- 새 근거를 인용하는 판단은 anthropic.F5 하나뿐이다(EV-164·165·169·170·172). openai 판단은 EV-openai-182~188 을 인용하지 않는다(트리거와 carry 문장에서만 쓰였다).

### 전수 기계 점검

- `sources.json` 미등록 참조: 관측 0, 판단 0, 근거 0, 트리거 0. 컷오프 초과 발행시각 0건(발행시각이 없는 4건 EV-amazon-001·002, EV-meta-001, EV-microsoft-004 은 이어받은 항목이다).
- draft.md 와 evidence.json 에서 투자 조언·매매 지시·수익 보장·FOMO 표현 없음(검색에 걸린 "매도 제한"·"공매도"는 사실 서술이다).

### 이전 트리거 29건 carry 전수

- `research.md` 「이전 트리거 처리」 29행과 `triggers.json` 의 `ref` 가 q3a 인 29건은 결론이 모두 `watching`(계속 관찰)이고 확인일은 2026-10-23 이다. 발동·철회 전이는 없다.
- `finding` 이 말한 "새 후보 107건"은 `candidates.json` 에서 anthropic·openai 뉴스 중 발행시각이 2026-10-22 이후인 후보 수와 같다(107). 107건 제목을 전수로 훑어 29건 각각의 발동 조건과 맞춰 봤고, 조건에 해당하는데 놓친 후보는 없었다. 구체 대조는 다음과 같다.
  - TRG-036: PYMNTS(10-23 공개 제출 가능성), Motley Fool(10-25 시한), Morningstar, 유출 초안 보도 구분이 원문과 맞다. EDGAR 재조회에도 Anthropic PBC 제출인이 없다(표현 보정은 F-4).
  - TRG-039: CNBC·Bloomberg 원문과 일치(라운드 미마감, 가치 $1.4조에서 $1.25조). TRG-062 소송 계열은 판결·합의 후보가 없다.
  - TRG-110: The Verge 로비 보도 원문에 백악관 AI 태스크포스 언급만 있고 사고 통보 의무 집행 서술은 없다.
  - TRG-163: Google Cloud 블로그·TNGlobal 원문과 일치한다(같은 가격·같은 청구, 같은 주 OpenAI 모델 입점).
  - TRG-364: The New Stack 원문에서 Anthropic·Google 이 지원 목록에 없다는 문장을 확인했다. TRG-095: GPT-6.1 Sol 은 이미 기존 근거에 있고 GPT-6.1 Astra 출시·독립 측정 등재는 후보에 없다. TRG-119: Key Context 인터뷰는 배치 규모를 적지 않는다.
  - 나머지(037·038·070·071·092·093·094·096·097·108·112·160·161·162·360~363·365~367)는 해당 후보가 없거나 유출 수치·연환산 반복이라는 `finding` 서술이 후보 제목과 맞다.
- 이 29건 밖의 이전 트리거(v30full·v21 계열의 watching·fired·withdrawn)는 q3a 에서 이어받은 상태 그대로이고 이번 실행의 갱신 범위(Anthropic·OpenAI) 밖이다. fired 로 처리해야 했는데 놓친 사건은 29건 안에서 발견되지 않았다.
- 「발동 트리거 재검토 대상」 표의 "수정하지 않음" 행(TRG-107 Palantir, TRG-113 Alphabet)은 갱신 범위 밖 항목이고 q3a 에서 이어받았다. 이번 실행의 입력이 바뀌지 않았다.

### 새 트리거 TRG-378~381

- 근거: TRG-378(EV-anthropic-164), TRG-379(EV-openai-182·184), TRG-380(EV-amazon-086·078·087·039), TRG-381(EV-anthropic-172·EV-alphabet-018·EV-anthropic-165). 전부 confirmed 이고 원문과 일치한다.
- 코디네이터가 알린 TRG-163 observation 과 EV-anthropic-172·165·169 의 `relevance`·`conditional_impact` 수정은 현재 파일 기준으로 읽었다. 발췌·출처·locator 는 그대로이고 새 문구가 원문·판단과 어긋나지 않는다.
- TRG-380·381 의 `source_ids` 는 빈 배열이다. 같은 모양의 트리거가 31건 있어 새 결함이 아니고 `evidence_ids ⊆ evidence` 는 성립한다.

## CHECKLIST

| ID | 결과 | 근거 |
| --- | --- | --- |
| Q05 | pass | 출처 이해당사자 표기는 점검하지 않는다(AGENTS.md). 결과 칸만 채운다. |
| Q09 | pass | 새 근거 중 계획·예고(10-25 S-1 시한, UAE 컴퓨트 계약 협상, Google 조건부 출자)는 트리거로만 쓰였다. Google 조건부 약정은 규칙이 이정표 조건부 추가 출자를 묶임 증거로 인정하므로 현재 사실로 쓰였다. |
| Q19 | pass | 받은 투자를 곧바로 지분 동맹으로 세지 않았다. Amazon·Google 은 묶임 증거(10-Q 이정표 한도, 성과 목표 조건부 약정)가 원문으로 확인됐고, Microsoft·AMD·NVIDIA 는 묶임 증거 미확인으로 뺐다. 단 OpenAI ⑤ Microsoft 의 헤지 읽기는 F-1, Amazon 문구는 F-2 에 적었고 일관성 판정은 규칙 일관성 영역(Q03)이 한다. |

## 다음 실행 과제

1. EV-anthropic-172 의 1차 원문(Anthropic 발표)을 찾아 등급을 올린다. 지금은 Bloomberg 전재본 하나가 "성과 목표" 조건을 받친다.
2. 후보 107건 중 근거·트리거·판단 어디에도 없는 두 건을 다음 실행에서 가린다. Anthropic 의 Claude Duet 출시(2026-10-22, 여러 매체)가 ④ 응용 칸·① 가격에 닿는지, OpenAI 에이전트 감시 시스템 오작동 보고서와 외부 평가자 지적(CNBC·Reuters, 2026-10-22)이 OpenAI ⑤ 전선(규제기관 조사)에 닿는지 본다. 이번 리뷰에서는 점수에 닿는다는 근거를 찾지 못해 발견으로 적지 않는다.
3. 가격 관측은 이번 리뷰 범위가 아니다. run.json 의 `price_as_of` 는 2026-10-23 이지만 가격 관측은 10-22 종가이므로 10-23 종가를 받아 research·calculate·draft 를 다시 돌린 뒤 확인 리뷰가 본다(지시서에 적힌 대로).
4. EV-anthropic-167·168·171 처럼 유출 상장 신청서 수치를 옮긴 근거는 확정은 됐으나 판단에서 쓰이지 않는다. 공개 S-1 이 나오면 공시 값으로 대체한다.
