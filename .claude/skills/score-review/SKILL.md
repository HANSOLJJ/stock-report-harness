---
name: score-review
description: scorecard 4-way 리뷰 게이트. 사실·출처 / 재무 계산 / 규칙 일관성 / 출력·가독성 네 영역과 체크리스트 Q01~Q23 을 별도 세션 리뷰어로 수행하고 output/<run_id>/review.md 를 pass|needs_fix|blocked 로 기록한다.
---

# 채점 리뷰 스킬

## 한 번에 끝낸다

리뷰 → 수정 → 재리뷰를 되풀이하지 않는다(2026-10-01 시험 실행에서 세 바퀴 돌았다).

- 리뷰어에게 표본 대조를 시키지 않는다. 이어받은 판단까지 전부 보게 하고, 발견을 한 번에 다 적게 한다. "바뀐 것 위주" 로 범위를 좁히지 않는다.
- `needs_fix` 는 점수·순위·체크리스트 판정을 바꾸는 발견에만 쓴다. 나머지는 영역 파일의 "다음 실행 과제" 절에 적고 승인을 막지 않는다.
- 고친 문장의 숫자는 사람에게 올리기 전에 확정 관측값과 대조한다. 고치면서 새 결함을 만들지 않는다.
- 판단을 고치는 제안은 옛 문장 옆에 정정을 덧붙이지 않고 문장 전체를 현재 상태로 다시 쓴다. 버전 표기·변경 표시·작업 번호·다른 판을 가리키는 표현이 리포트에 남으면 출력·가독성 발견이다(2026-10-06 사용자 지시, AGENTS.md 「금지·주의」).

## 절차

1. `uv run --frozen python -X utf8 scripts/scorecard_cli.py review-template <run_id> [--force] [--take-lock]` 로 `output/<run_id>/review.md` 뼈대를 만든다(이미 있으면 `--force` 는 리뷰를 새로 시작할 때만).
2. 네 영역을 가급적 별도 Task/서브에이전트 세션에서 수행한다. 각 리뷰어에게 읽을 파일과 출력 형식(RESULT / FINDINGS / CHECKLIST)을 지정한다. 각 리뷰어가 쓴 결과는 `output/<run_id>/review-parts/<영역>.md` 에 둔다.
   - 리뷰어 입력: `output/<run_id>/` 의 `draft.md`, `research.md`, `results.json`, `observations.json`, `judgments.json`, `sources.json`, `evidence/evidence.json`, `triggers.json`, `preview.md`(HTML 이 있으면 `report.html`). 근거·트리거·출처를 읽지 않은 리뷰는 사실·출처 영역을 pass 로 쓰지 않는다.
   - 리뷰어 프롬프트에 "SEC 공시 원문은 `scorecard_cli.py sec-get <SEC 주소>` 로만 받고 SEC 요청이나 User-Agent 를 직접 만들지 않는다" 를 넣는다(2026-10-01 사고).
   - 리뷰어 프롬프트에 "큰 파일은 grep/sed 로 필요한 부분만 읽으라"를 넣는다. 네 개를 동시에 띄우면 세션 사용량 한도(HTTP 429)로 전부 중단되는 일이 있었다(2026-09-08). 한도가 걱정되면 2개씩 나눠 띄우고, 중단된 리뷰어는 같은 agent 에 이어서 진행을 요청한다.
   - 사실·출처: `fact-checker` — 숫자·기업 귀속·기준 시점·출처·부재 주장, 근거의 `source_ids ⊆ sources`, URL, excerpt 원문 대조. 올릴·내릴 근거 줄마다 표지 `[EV-…]` 가 가리키는 근거의 본문 발췌가 원문 그 위치(`locator`)에 실제로 있고 그 줄의 사실을 받치는지 전수로 본다(2026-10-07, `guide.md` 5.7). 이해상충 표기는 보지 않는다(2026-10-02, AGENTS.md 「금지·주의」).
   - 근거 불릿: `evidence-editor` — `evidence.json` 과 draft 근거 절의 주장·출처 대응, 추론 표시, 금지 표현. 근거 불릿 검토는 이 에이전트에 맡기고 사실·출처 영역의 근거로 인용한다.
   - 재무 계산: EPS·환율·ADR·TTM·FCF·런웨이·약정·단위·부호. results.json 의 calc.path 대조.
   - 규칙 일관성: 판정 입력↔규칙 판정표, 승계 표시(기업 추가 실행에만. 규칙 v2.0 이상 정기 실행은 승계 판단이 없어야 한다, `rules.md` 2.9), 미결 결정 처리, 체크리스트 Q01~Q23 전체. **회사별 사다리 적용 표만으로는 부족하다** — 아래 「회사를 가로지르는 표 셋」을 반드시 만든다(2026-10-09).
   - 출력·가독성: `report-designer` — draft·HTML(있으면) 숫자 일치, 낡은 비교 문장(C-19), 근거·트리거 절 가독성, dashboard-design 기준.
   - 각 `review-parts/<영역>.md` 는 frontmatter 에 `reviewer_agent`(예: `fact-checker`), `session`(리뷰 세션 식별자), `reviewed_at`(YYYY-MM-DD)을 둔다. 본문 첫머리의 `검토자:`·`결과:` 줄은 승인 페이지 요약이 읽으므로 그대로 둔다.
3. 리뷰 파일의 "검토 영역" 표에 검토자·결과·요약을, "체크리스트" 표에 Q01~Q23 결과와 근거를 채운다. not_applicable 도 사유를 쓴다. 수행하지 않은 검토를 pass 로 쓰지 않는다.
4. 네 영역 모두 pass 이고 fail 항목이 없을 때만 frontmatter `status: pass`. 하나라도 needs_fix 면 `needs_fix` 로 두고 상위 단계(collect/research/calculate/draft/렌더러)로 돌아가 발견을 한 묶음으로 고친 뒤 재생성하고 **확인 리뷰를 한 번** 한다. 확인 리뷰에서도 점수·순위·체크리스트 판정을 바꾸는 발견이 남으면 `blocked` 로 사람에게 보고한다(2026-10-06). 자료·규칙·판단·초안이 바뀌면 리뷰는 무효이므로 템플릿의 `results_hash`·`draft_hash` 를 갱신한다(`review-template --force` 후 다시 채움).
5. `uv run --frozen python -X utf8 scripts/validate_report_contract.py <run_id>` 를 실행해 통과를 확인한다.

## 회사를 가로지르는 표 셋 (규칙 일관성 리뷰어 필수)

2026-10-09 재실행 리뷰가 Q03 을 pass 로 두고도 OpenAI–Anthropic ⑤ 의 어긋남을 놓쳤다. 리뷰어는 "회사마다 사다리를 맞게 적용했나" 표만 만들었고, 같은 사건을 회사를 가로질러 나란히 놓지 않았다. Microsoft 가 GitHub Copilot 에 자체 모델을 넣은 한 사건이 Anthropic ⑤ 에서는 구조형 −2, OpenAI ⑤ 에서는 비용형 −1 로 읽혔고, 그 차이는 경제적 차이가 아니라 "Anthropic 의 고객 비중은 유출 초안으로 알려졌고 OpenAI 는 공개하지 않았다" 는 정보 차이에서 왔다. 규칙 일관성 리뷰어는 다음 세 표를 리뷰 파일에 싣고, 어긋난 줄은 Q03 fail 로 적는다.

1. **사건 교차표.** 한 상대의 한 행동(예: Microsoft 의 자체 모델 투입, SpaceX 의 Cursor 인수, 미국의 수출 통제, Anthropic 의 Google 약정)을 행으로, 그 사건이 등장하는 모든 회사의 판단(회사·항목·읽은 성격·점수 방향)을 열로 놓는다. 같은 사건이 회사마다 다른 성격(동맹/조달/적대, 비용형/구조형, 계획/실측)으로 읽혔으면 그 이유가 **관계의 종류 차이**인지 **자료의 유무 차이**인지 적는다. 자료의 유무 차이면 Q03 fail 이다.
2. **미확인 방향표.** 판정 칸의 "미확인·확인하지 못했다·확인되지 않는다" 문장마다 그 미확인이 점수를 **올리는 쪽**으로 해소됐는지 **내리는 쪽**으로 해소됐는지 적는다(예: 조달 의존 몫 미확인 → 큼(내림), 구조형 전선 미확인 → 비용형(올림)). 같은 종류의 미확인이 회사마다 다른 방향으로 해소됐으면 fail 이고, 가점이나 감점 완화 쪽으로 해소된 미확인은 규칙 2.1 의 "감점을 덜어 주는 장치는 가점과 같은 엄격함" 에 비춰 사유를 요구한다.
3. **결정적 사실의 근거 등급표.** 등급·통과·큼/작음을 가른 사실마다 근거의 등급을 적는다 — 공시(10-K·20-F·S-1 공개 제출본), 회사 1차 발표, 독립 측정, 2차 보도, 유출 문서·초안. 같은 입력(예: ⑤ 구조형의 '주요 고객', ⑧ 고객 축의 집중)에 회사마다 다른 등급의 근거를 썼으면 fail 이다. 유출 문서·초안은 "보도가 있다" 는 사실로만 쓰고 등급을 가르는 수치로 쓰지 않는다.

직접 경쟁사 쌍(OpenAI–Anthropic, Alphabet–Microsoft–Amazon, NVIDIA–AMD 류, TSMC–Intel·Samsung)은 항목별로 나란히 놓고 점수가 다른 칸마다 차이의 이유를 한 줄로 쓴다. 이유를 한 줄로 못 쓰면 그 칸이 발견이다.

## 판단 수정을 제안할 때

리뷰에서 정성 판단(F1·F3·F4·F5·F7·F8·F9)의 입력이 틀렸다고 보면, 점수나 `draft.md` 를 고치지 않고 판단 입력을 고친다. 에이전트는 판단 변경 제안을 쓰고, 근거를 원문과 대조한 뒤 `proposal` 로 반영하거나 거부한다(2026-10-07 사용자 지시: 사람은 최종 승인만 한다). 사람은 9절 「전체 판단 표」에서 직접 고칠 수도 있다. 제안은 리뷰가 끝난 뒤 한 묶음으로 올린다. 규칙 일관성 리뷰는 근거 세 칸의 분류(판정·올릴 근거·내릴 근거, `guide.md` 5.6)가 판정 재료와 맞는지와 방향이 뒤바뀐 줄이 없는지도 본다(2026-10-07).

```
uv run --frozen python -X utf8 scripts/scorecard_cli.py propose <run_id> --company <id> --factor F1..F9 (--set key=value … | --evidence "문장" … | --json 파일) --reason "…" [--cite EV-…]
```

사람이 바꿀 값을 정확히 지시한 경우에만 같은 인자로 `judge` 를 써서 바로 기록한다(`--by` 에 지시한 사람의 이름).

- F1·F4·F8 은 `--set score=N`, F3 은 `--set imitation=pass` 같은 `criteria` 키, F5 는 `A`·`H`, F7 은 `funding_dependent_share`·`own_money_returns`, F9 는 `gate_inputs` 키를 준다. F3·F5·F7·F9 에 `score` 를 주면 거부된다. F2·F6 은 대상이 아니다.
- `--evidence` 는 여러 번 주면 그 목록으로 근거를 통째로 바꾼다. 판정 재료를 바꿨다면 근거 문장도 함께 맞춘다.
- `--reason` 에 사유를, `--by` 에 수정을 정한 사람의 이름을 적는다. 이전 값은 `revision_history` 에 남는다.
- 새 판단은 확정된 근거만 인용한다. 후보 근거를 인용하는 수정은 거부된다.
- 같은 factor 의 다른 기업 판단을 함께 보고 같은 잣대를 대는지 확인한다(Q03).
- 고친 뒤에는 판단 해시가 바뀌므로 리뷰가 무효다. `research → calculate → draft → review-template --force` 부터 다시 돌리고 "승인 대기" 를 보고한다.

## 상태

- `pass`: 승인 요청 가능.
- `needs_fix`: 생성 단계에서 고칠 수 있는 문제.
- `blocked`: 확인 리뷰 뒤에도 점수·순위·체크리스트 판정을 바꾸는 발견이 남았거나, 외부 자료·권한 한계.

## 완료 보고

리뷰 상태, 영역별 결과, 수정 목록. pass 이면 "승인 대기" 를 보고하고, 사람이 승인 페이지에서 승인하도록 안내한다(`/score-approve <run_id>` 는 그 안내를 보여 준다). 에이전트는 승인하지 않는다.
