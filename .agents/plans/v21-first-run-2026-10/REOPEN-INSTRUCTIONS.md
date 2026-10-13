# 막혔던 원문 다시 열기 지시서 (2026-10 규칙 v2.1 첫 실행, 2026-10-13 사용자 지시)

실행 `ai-scorecard-2026-10-v21`(정보 마감 2026-10-12)의 근거 가운데 **스크립트 요청이 막혀 원문 대신 다른 기사로 확인한 것**을 실제 브라우저로 다시 연다.
규칙은 AGENTS.md 「원자료 조사 규율」의 403 항목이다. 앱 안 브라우저(`mcp__Claude_Browser__*`)나 Playwright(`mcp__playwright__*`)로 연다.
실제 브라우저에서도 접근 거부·봇 확인 화면(CAPTCHA 등)·구독 장벽이 뜨면 우회하지 않고(User-Agent 를 바꿔 다시 받지 않는다) 막혔다고 적는다.

## 대상

| 지금 근거 | 다시 열 원문 | 판단이 인용하는 칸 |
|---|---|---|
| EV-openai-055 (Engadget 실시간 기사) | OpenAI DevDay 2026 공식 자료(openai.com 의 발표 글·요약) | openai ①②③④ |
| EV-anthropic-098 (The Next Web) | Anthropic Marketplace 원 발표문(anthropic.com) | 인용 없음 |
| EV-openai-068 (RuntimeWire) | Forbes·Reuters 의 USA TODAY Co. 대 OpenAI 소송 기사, 가능하면 소장 원문 | openai ⑤ |
| EV-apple-043 (9to5Mac) | Seeking Alpha 의 IDC Mac 출하 기사, 가능하면 IDC 발표 원문 | apple ① |
| EV-apple-045 (Yahoo 전재 Reuters) | Top Class Actions 의 Siri 합의 안내(2026-10-08) | apple ②⑤ |
| EV-microsoft-040 (CloudComputing News) | Bloomberg 의 EU 게이트키퍼(AWS·Azure) 기사 | microsoft ⑤ |
| EV-oracle-052 (Oracle 안내 페이지) | OCI Generative AI 가격 페이지(스크립트로 그려지는 페이지) — 호스팅 모델의 과금 방식 | oracle ④ |
| EV-alibaba-091 (중신경위 기사) | Alibaba Cloud 가격 인상 공지의 상세표(GPU·CPFS 목록, 2026-04-18 시행) | alibaba ① |
| 근거 없음 | Reuters·CNBC·Tribune 의 "5,180억 달러" 기사. 무엇에 관한 기사인지는 `.agents/plans/v21-first-run-2026-10/work/out-D.json` 의 notes 와 OpenAI 판단에서 먼저 확인한다 | 해당 판단 |

지금 근거의 본문·출처·후보 주소는 `output/ai-scorecard-2026-10-v21/evidence/evidence.json`·`sources.json` 에서 그 ID 로 꺼내 읽는다(python 한 줄). 후보로 수집된 원문 주소가 Google News 중계 주소면 `uv run --frozen python -X utf8 scripts/scorecard_cli.py resolve-urls --url <주소>` 로 푼다.

## 건마다 할 일

1. 원문을 실제 브라우저로 연다. 열리면 본문에서 판단에 쓰이는 문장을 **글자 그대로** 옮기고 위치(문단·표·절)를 적는다. 발행일이 2026-10-12 이하인지 본다. 정보 마감 뒤에 고쳐진 페이지(가격표 등)는 2026-10-12 이전 상태를 확인할 수 있을 때만 쓴다(아카이브 스냅숏 등). 확인할 수 없으면 그 사실을 적는다.
2. 원문이 지금 근거·판단 문장과 **같은 사실을 말하는지, 다른 숫자·조건을 말하는지, 새 사실을 더하는지** 가른다. 판단 문장은 `judgments.json` 에서 그 근거 ID 를 인용한 줄을 찾아 읽는다.
3. 열린 원문은 새 근거 후보로 만든다. 모양은 `work/add_fix_items.py` 머리말과 `work/items-maia.json` 예시와 같다(`sources`·`evidence`, 항목마다 `key`). `excerpt` 는 600자 이하, " … " 로 이은 조각은 원문에 그 순서로 있어야 한다. `channel` 은 `disclosure`·`press`·`company_statement`·`secondary` 가운데 하나다(회사 페이지는 company_statement, 언론 원보도는 press, 전재·인용 보도는 secondary). `conditional_impact` 에 점수나 점수 이동을 적지 않는다.

## 규칙

- 파일은 `.agents/plans/v21-first-run-2026-10/work/reopen1/items-reopen1.json` 과 `work/reopen1/report.md` 둘만 쓴다. 실행 폴더 파일은 고치지 않고, 상태를 바꾸는 CLI(confirm·propose·research 등)는 부르지 않는다.
- SEC 문서는 `scorecard_cli.py sec-get <주소>` 로만 받는다.
- 큰 JSON 은 python 한 줄이나 grep 으로 필요한 부분만 읽는다. Bash 에서 `&&`·`;` 로 명령을 잇지 않는다.
- report.md 에는 건마다 연 주소, 결과(열림·구독 장벽·접근 거부·봇 확인·없음), 원문이 말하는 것, 지금 근거·판단과 다른 점, 새 근거 key 를 적는다. 판단을 어떻게 고칠지는 정하지 않는다(판단 세션이 정한다).
