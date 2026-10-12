# 회사 묶음 작업 지시서 (2026-10 정기 재실행 recheck)

실행 `ai-scorecard-2026-10-recheck`(기준일 2026-10-12, 정보 마감 2026-10-12, 가격 2026-10-09 종가, 규칙 v2.0)에서 맡은 회사에 대해 네 가지를 한다. (1) 이어받은 제목뿐 근거의 원문 다시 읽기, (2) 새 근거 후보 선별과 원문 확인, (3) 이전 실행의 관찰 중 트리거 처리, (4) 관측 갱신. **실행 폴더 `output/ai-scorecard-2026-10-recheck/` 의 파일은 읽기만 하고 쓰지 않는다.** 산출물은 `.agents/plans/oct-recheck-2026-10/work/out-<묶음>.json` 하나다. 조율자가 합치고 검증한다. `confirm`·`judge`·`propose`·`research` CLI 를 부르지 않는다(실행 잠금이 충돌한다). `sec-get` 과 `resolve-urls --url` 은 써도 된다.

## 이 실행의 배경 (반드시 읽는다)

- 직전 실행은 Google News 중계 주소 때문에 본문을 못 연 기사를 "제목만 확인"이라며 판단에서 뺐다. 그 안에 OpenAI 연환산 매출 기사 같은 결정적 사실이 있었다(2026-10-12 사용자 지시). **이번에는 제목만 보고 넘기지 않는다.**
- 후보의 `url` 은 Google News 중계 주소다. 원문 주소는 이렇게 얻는다.
  `uv run --frozen python -X utf8 scripts/scorecard_cli.py resolve-urls --url "<중계 주소>"`
  그 주소를 WebFetch 로 연다. 유료 기사(FT·Bloomberg·WSJ·The Information 등)로 막히면 같은 사실을 전한 열리는 기사(Reuters·CNBC·TechCrunch·Yahoo Finance 전재·회사 발표)를 찾아 그 기사로 근거를 올린다. 그래도 없을 때만 "유료 기사라 본문 미확인"으로 보고한다.

## 읽을 것

- `AGENTS.md` 「원자료 조사 규율」·「금지·주의」, `.claude/skills/score-collect/SKILL.md`, `docs/scorecard/rules.md` 3·4절, `.agents/plans/rejudge-all-2026-11/F1-INSTRUCTIONS.md`·`F2-INSTRUCTIONS.md`·`F3-INSTRUCTIONS.md`·`OBS-INSTRUCTIONS.md`(판단 세션이 쓰는 근거·관측의 종류).
- 실행 파일: `evidence/candidates.json`(3,076건, 창 2026-10-06~10-12. 맡은 회사이고 `published_at_utc` 2026-10-08 이후 또는 공시 `filed_at` 2026-10-07 이후인 것이 새 후보), `evidence/evidence.json`(이어받은 확정 근거 756건 — 같은 사건을 다시 올리지 않는다), `observations.json`, `sources.json`(근거 출처는 이미 원문 주소로 바뀌어 있다), `judgments.json`(직전 판단. 어떤 근거가 비었는지 보는 용도), `output/ai-scorecard-2026-10-rejudge/triggers.json`(이전 실행 트리거).
- `.agents/plans/oct-recheck-2026-10/work/title-only-evidence.json`: 이어받은 근거 중 발췌가 제목뿐인 30건(회사별, 원문 URL 포함).

## 1. 이어받은 제목뿐 근거 고치기

- `title-only-evidence.json` 에서 맡은 회사 항목을 전부 연다. 본문에서 그 근거의 사실을 받치는 문장을 600자 이하로 그대로 발췌하고, `locator` 에 자리(기사 몇째 문단, 공시 항목·표)를 적는다.
- 산출물 `evidence_fixes` 에 `{"evidence_id", "excerpt", "locator"}` 를 쓴다. 원문이 유료라 같은 사실을 전한 다른 열리는 기사로 바꾸면 `sources` 에 새 출처를 넣고(`source_id` 는 `SRC-WEB-<company>-9NN`, 901 부터. `url`·`title`·`publisher`·`accessed_at`·`company_id`·`kind: news`·`published_at_utc` 필수) `evidence_fixes` 항목에 `"source_id"` 와 새 `"title"`·`"published_at_utc"` 를 함께 적는다.
- 끝내 본문을 못 읽으면 `evidence_unreadable` 에 `{"evidence_id", "reason"}`(어디서 왜 막혔는지)을 쓴다. 조율자가 후보로 되돌린다.

## 2. 새 근거

- 새 후보를 제목으로 훑어 ①~⑨ 와 닿는 것을 고른다. 고른 것은 **반드시 원문 본문을 열어** 발췌한다. `excerpt` 는 본문 그대로 600자 이하이고 제목과 달라야 하며, `locator` 를 적는다. 본문을 연 근거만 `"verified_original": true` 로 낸다. 제목만 본 근거는 내지 않는다.
- 직전 판단이 "제목만 확인"으로 뺀 보도는 이번에 원문을 열어 근거로 올린다(묶음별 목록은 아래 「묶음별 필수」).
- 필수 키: `company_id`, `factors`, `kind`(news|filing), `source_id`(후보의 `source_id` 그대로. 직접 연 페이지는 `sources` 에 새 출처 `SRC-WEB-<company>-9NN`), `published_at_utc`, `title`, `excerpt`, `locator`, `relevance`(추론임을 표시), `channel`(disclosure|press|company_statement|secondary), `conditional_impact`("지금은 유지:" 또는 "재검토:"로 시작), `horizon`, `counter_evidence`(빈 목록), `unverified`, `change_vs_previous`. `evidence_id` 는 적지 않는다.
- 정보 마감은 2026-10-12 이다. 그 뒤에 나온 기사는 쓰지 않는다.

## 3. 트리거

- `output/ai-scorecard-2026-10-rejudge/triggers.json` 에서 맡은 회사의 `status: watching` 항목마다 `triggers` 에 한 줄을 쓴다. `trigger_id` 그대로, `status`(watching·fired·expired·withdrawn), `deadline`, `finding`(2026-10-08~10-12 후보와 원문에서 무엇을 봤는지, 검색 범위 포함), 발동이면 근거를 `source_ids` 로 가리킨다. 하나도 빠뜨리지 않는다. 기한이 2026-10-12 이전인데 관찰을 유지하면 `deadline` 을 늦추고 `note` 에 이유를 적는다.
- 새 트리거는 `new_triggers` 에 전체 키(`company_id`, `factors`, `observation`, `condition`, `deadline`, `source_ids`, `status`, `recheck{factors, what}`)로 쓴다. 미래 점수를 적지 않는다.

## 4. 관측

- `OBS-INSTRUCTIONS.md` 의 규율대로 이번 창에 새로 나온 값만 등록한다(이미 있는 값을 다시 넣지 않는다). 항목은 `company_id`, `metric`, `value`, `unit`, `as_of`, `kind`, `source_id`, `status: verified`, `raw`(원문 발췌), `note`(자리), 필요하면 `period`·`basis`. 엔진은 같은 지표가 여럿이면 verified 이면서 최신인 것을 쓴다.

## 묶음별 필수

- **A (nvidia·tsmc·apple):** TSMC 2026-10-08 6-K(9월 매출)를 열어 월매출 관측과 ③ 근거로 올린다. 직전 nvidia ⑤ 가 제목만 보고 뺀 "중국 칩 밀수"·"Groq 거래 소송" 보도를 원문으로 연다.
- **B (alphabet·amazon·microsoft):** 직전 ⑤ 가 제목만 보고 뺀 보도를 연다. alphabet 은 폴란드 조사·영국 앱 장터 소송(Reuters·FT), amazon·microsoft 는 EU 가 AWS·Azure 를 디지털시장법 규율 대상으로 들여다본다는 보도.
- **C (meta·oracle·palantir):** palantir ⑤ 가 제목만 보고 뺀 "앤디 버넘이 영국 안의 Palantir 대체 업체를 찾는다" 보도를 연다.
- **D (anthropic·openai):** (1) OpenAI 연환산 매출: Axios 2026-09-29($70B 근접, 3분기 초 대비 70% 이상)와 2026-10-08 FT 보도(투자자에게 "$50B 에 가까움", $70B 는 투자자가 Anthropic 기준으로 환산한 값, Anthropic 은 클라우드 파트너 판매를 매출에 넣고 OpenAI 는 넣지 않음. 열리는 전재: TechCrunch 2026-10-08)를 근거로 올린다. (2) **비상장 재무 관측 갱신(필수):** 두 회사의 `post_money_valuation`(가장 최근 확정 라운드), `arr`(연환산 매출, `kind: run_rate`, 회사 기준 정의를 `note` 에), `arr_prior`(같은 정의의 직전 값), `cumulative_raised`, 그리고 `ps_ratio`(기업가치 ÷ 최근 1년 실매출 추정, `kind: estimate`, `basis` 에 `formula`·`derivation`·`estimate_range`). 지금 값은 9월 2일 기준선의 `legacy_unverified` 다. 근거 등급을 `note` 에 적는다(회사 1차 발표 > 독립 집계 > 2차 보도). **유출 문서·초안의 수치는 등급을 가르는 값으로 쓰지 않는다(AGENTS.md).** 최근 1년 실매출을 받칠 공시·1차·2차 보도가 없으면 `ps_ratio` 를 등록하지 말고 그 사실과 후보 값을 보고에 적는다. 두 회사에 같은 등급의 근거를 쓴다. (3) ② 모델 기업 공통 근거로 Artificial Analysis·ARC Prize 같은 날짜 순위표가 10-08 이후 바뀌었으면 새 날짜로 올린다.
- **E (alibaba·tesla·spacex-xai):** spacex-xai 는 상장사라 ⑥ 은 가격 관측을 쓴다. xAI 의 연환산 매출·Grok 사용량처럼 ③ 지표가 이번 창에 나왔으면 올린다. alibaba 2026-10-07 6-K 를 연다.

## 출력

`work/out-<묶음>.json` 에 `{"group", "sources", "evidence", "evidence_fixes", "evidence_unreadable", "triggers", "new_triggers", "observations"}`. 마지막 답변에는 회사별로 고친 제목뿐 근거 수와 못 읽은 것, 올린 새 근거 수, 트리거 처리 결과(관찰·발동·만료·철회 수), 등록한 관측과 못 찾은 것, 판단 세션에 알려야 할 사실을 적는다. 문장은 완결된 현재 상태 문장으로 쓰고 규칙 버전·작업 번호·이전 판 참조를 쓰지 않는다. 이해상충을 이유로 멈추거나 되묻지 않는다.
