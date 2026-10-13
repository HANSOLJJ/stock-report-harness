# 다시 연 원문으로 판단 고치기 지시서 (2026-10 규칙 v2.1 첫 실행, 2026-10-13 사용자 지시)

실행 `ai-scorecard-2026-10-v21`(정보 마감 2026-10-12)에서 스크립트 요청이 막혀 2차 기사로 대신했던 원문을 실제 브라우저로 다시 열었다.
결과는 `.agents/plans/v21-first-run-2026-10/work/reopen1/report.md` 에 있고, 원문 근거 10건을 확정했다. 이 근거로 인용 판단을 고친다.
공통 절차와 파일 모양은 `FIX-INSTRUCTIONS.md`(같은 폴더)와 그 지시서가 가리키는 `JUDGE-INSTRUCTIONS.md`·`REJUDGE-INSTRUCTIONS.md` 를 그대로 따른다.

## 새로 확정한 원문 근거

| 근거 | 원문 | 대신했던 근거 | 닿는 판단 |
|---|---|---|---|
| EV-openai-161 | OpenAI DevDay 2026 Recap(회사 글, 주간 12억 명) | EV-openai-055(Engadget) | openai ②(본문 줄), ①③④(reconfirmed) |
| EV-anthropic-141 | claude.com Marketplace 공식 글(2026-09-23) | EV-anthropic-098(TNW, 인용 없음) | anthropic ④ 와 openai ④ 의 플랫폼 칸 대조 |
| EV-openai-160 | USA TODAY 소장(청구 취지에 모델·학습 데이터셋 폐기, 피고에 Microsoft 없음) | EV-openai-068(RuntimeWire) | openai ⑤ |
| EV-apple-065·066 | IDC 3분기 PC 출하 발표 원문 | EV-apple-043(9to5Mac) | apple ① |
| EV-apple-067 | Fox News 칼럼(Siri 합의 2026-07-17 예비 승인, 최종 심리 2027-02-24, 2차) | EV-apple-045 | apple ②⑤ |
| EV-microsoft-076 | Bloomberg 원문(앞 두 문단) | EV-microsoft-040 | microsoft ⑤ |
| EV-oracle-061 | OCI 가격표(2026-10-06 아카이브, 타사 모델 종량·전용 클러스터 시간) | EV-oracle-052 | oracle ④ |
| EV-alibaba-094·095 | Alibaba Cloud 가격 인상 공지 상세표(목록가 인상 폭, 규격별 5%·21%·25%–34%, CPFS 30%) | EV-alibaba-091 | alibaba ① |

## 맡을 일

1. 위 판단마다 원문이 2차 기사와 **같은 사실인지, 다른 숫자·조건인지, 새 사실을 더하는지** 보고 판단 문장을 원문 기준으로 다시 쓴다. 같은 사실이면 원문 근거 표지를 줄에 더하거나 바꾸고, 2차 기사에만 있던 서술(발언자, 해석)은 원문이 받치지 않으면 뺀다.
   - openai ②: "DevDay 에서 Altman 은 … 말했다 [EV-openai-055]" 의 발언 주체는 공식 글에 없다. 회사 문장으로 고친다.
   - openai ⑤: 소장의 청구 취지(영구 금지명령, 원고 콘텐츠가 들어간 GPT·LLM 모델과 학습 데이터셋 폐기)를 정확히 적고, 지금의 비용형 읽기가 같은 청구를 담은 언론사 병합 소송(MDL 3143, EV-openai-044~046)과 같은 잣대인지 확인한다. 판결 전 청구는 사업 구조를 바꾼 사실이 아니라는 기존 원칙을 따르되, 그 이유를 판정 칸에 적는다.
   - apple ①: IDC 원문은 Apple 의 가격 인상도, Apple 이 덜 줄어든 이유도 말하지 않는다. EV-apple-043 의 relevance 가 "Apple 은 메모리 가격 급등으로 Mac·iPad 가격을 올렸고 … 인상 뒤 고객이 남았는가에 쓰는 방증" 이라고 읽는데, 9to5Mac 발췌가 그 사실을 받치는지 보고 apple ① 의 가격 실측 재료가 이 해석에 기대는지 확인한다.
   - apple ②⑤: Siri 합의의 법원 단계(예비 승인, 최종 심리일)를 현재 상태로 적는다. 칼럼은 2차라 등급을 적는다.
   - microsoft ⑤: Bloomberg 열린 부분은 Azure·AWS 지정 예정과 11월 결정(초안, 늦춰질 수 있음)까지다. Google Cloud 대우 문장은 원문에서 확인되지 않았다.
   - oracle ④: OCI 는 타사 모델(Cohere·Meta·xAI·Google·OpenAI)을 토큰·문자 종량과 전용 클러스터 시간으로 판다. 이 사실을 어느 층의 판매로 읽을지 정한다. **Amazon Bedrock·Microsoft Foundry·Google Vertex 처럼 타사 모델을 파는 다른 회사의 ④ 칸 읽기와 같은 잣대**를 댄다(층 정의는 rules.md ④ 절: 모델 층은 모델 사용 자체에 돈을 내는 것).
   - alibaba ①: 공지 상세표는 목록가 인상과 규격별 차등을 보여 준다. 표 아래쪽 행에는 PAI·RDS·PolarDB 같은 다른 제품과 대형 모델 플랫폼 百炼(MU 단위)도 같은 인상 폭으로 있다(이미지 https://img.alicdn.com/imgextra/i1/O1CN01THZxty1PNH8XYiEmW_!!6000000001828-2-tps-2466-3634.png, 필요하면 Playwright 로 연다). 이 사실이 alibaba ① 의 가격 실측(인상 뒤 고객이 남았나는 별개의 실측이 필요)과 AI 수익화 (나)(AI 가 가격·단가를 올렸나)에 어떻게 닿는지, Microsoft ① (나)(AI 포함 정가 인상)에 댄 잣대와 같게 정한다.
   - anthropic ④·openai ④: Marketplace 공식 글은 두 회사 모두 수수료를 밝히지 않는다(Anthropic 의 '수수료 면제' 는 언론 보도뿐). 두 회사의 플랫폼 칸 읽기가 이 사실에서 갈리지 않는지 확인한다. 고칠 것이 없으면 파일을 만들지 않는다.
2. **낡아진 메모를 고친다.** 원문을 열었으므로 대신했던 근거의 `unverified`·`relevance` 에 남은 "원문을 열지 못했다", "확인하지 못했다" 같은 문장이 현재 상태와 어긋난다(EV-openai-055·068, EV-anthropic-098, EV-apple-043·045, EV-microsoft-040, EV-oracle-052, EV-alibaba-091). 트리거(`triggers.json`)에 같은 사실을 적은 문장이 있으면 그것도 본다. 이 문장 고침은 판단이 아니라 치환 목록으로 쓴다.
3. 점수가 바뀌는 칸이 생기면 같은 잣대가 닿는 다른 회사도 함께 본다(체크리스트 Q03).

## 출력

- 판단 파일: `.agents/plans/v21-first-run-2026-10/work/reopen1/<F>-<company_id>.json`(모양은 지금까지와 같다. `reason` 에 "다시 연 원문" 과 근거 ID 를 적는다).
- 치환 목록: `work/reopen1/subst-reopen1.json`(모양은 `SUBST-INSTRUCTIONS.md` 「출력」과 같다. `old` 는 그 칸의 지금 값 안에 정확히 한 번 나와야 하고, python 으로 확인한 뒤 쓴다).
- 새 근거가 더 필요하면 `work/reopen1/items-reopen2.json`(모양은 `work/add_fix_items.py` 머리말)에 쓰고 판단에서는 `[NEW:<key>]` 로 가리킨다.
- 상태를 바꾸는 CLI 는 부르지 않는다. SEC 는 `scorecard_cli.py sec-get` 으로만 받는다. 막힌 페이지는 우회하지 않는다(AGENTS.md 「원자료 조사 규율」 403 항목). 큰 JSON 은 필요한 부분만 읽는다. Bash 에서 `&&`·`;` 로 명령을 잇지 않는다.
- 마지막 답변(한국어, 짧게): 바뀐 판단 표(회사·항목·바뀐 입력·계산될 점수 가늠·이유), 고치지 않은 항목과 이유, 치환 항목 수, 같은 잣대 대조(oracle ④ 의 타사 모델 판매 읽기, alibaba ① 과 microsoft ① 의 (나)).
- 판단 문장은 완결된 현재 상태 문장으로 쓴다. 규칙 버전·변경 표시·작업 번호·이전 판 참조("2차 기사로는", "다시 열어 보니")를 쓰지 않는다. 이해상충을 이유로 멈추거나 되묻지 않는다.
