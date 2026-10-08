# 회사 묶음 작업 지시서 (2026-10 v2.0 재실행, 수집·트리거·관측)

실행 `ai-scorecard-2026-10-rejudge`(기준일 2026-10-08, 정보 마감 2026-10-08, 가격 2026-10-07)에서 맡은 회사들에 대해 세 가지를 한다. (1) 새 근거 후보 선별과 원문 확인, (2) 이전 실행의 관찰 중 트리거 처리, (3) ① 네 질문·③ 지표 단계에 쓸 새 관측 수집. **실행 폴더 `output/ai-scorecard-2026-10-rejudge/` 의 파일은 읽기만 하고 쓰지 않는다.** 산출물은 `.agents/plans/rejudge-all-2026-11/work/out-<묶음>.json` 하나에 모은다. 조율자가 `merge_group_outputs.py` 로 합치고 검증한다. `confirm`·`judge`·`propose` CLI 를 부르지 않는다(실행 잠금이 충돌한다). `sec-get` 은 써도 된다(캐시에만 쓴다).

## 읽을 것

- `AGENTS.md` 「원자료 조사 규율」·「금지·주의」, `.claude/skills/score-collect/SKILL.md`(선별 기준과 문장 규칙), `docs/scorecard/rules.md` 3절 ①②③(무엇이 근거가 되는지), `.agents/plans/rejudge-all-2026-11/F1-INSTRUCTIONS.md`·`F2-INSTRUCTIONS.md`·`F3-INSTRUCTIONS.md`(판단 세션이 어떤 근거를 필요로 하는지), `OBS-INSTRUCTIONS.md`(관측 지표와 규율).
- 실행 파일: `evidence/candidates.json`(5,427건. 맡은 회사이고 `published_at_utc` 2026-10-06 이후 또는 `filed_at` 2026-09-02 이후인 것이 새 후보), `evidence/evidence.json`(이어받은 확정 근거 603건 — 같은 사건을 다시 올리지 않는다), `output/ai-scorecard-2026-10-rescore/triggers.json`(이전 실행의 트리거. `status: watching` 인 것 가운데 맡은 회사 것이 처리 대상), `observations.json`(지금 관측. 이미 있는 값을 다시 넣지 않는다), `sources.json`, `judgments.json`(옛 판단. 어떤 근거가 비어 있는지 보는 용도).

## 1. 근거

- 새 후보를 제목으로 훑어 ①~⑨ 와 닿는 것만 고른다. 2026-10-06~10-08 이틀치라 대부분 중복·잡음이다. 회사당 보통 0~8건이다. 많이 고르는 것이 목표가 아니다.
- **판단 세션이 인용할 근거는 원문 본문을 열어 발췌한다.** `excerpt` 는 본문 그대로 600자 이하, 제목과 달라야 하고, `locator` 에 자리(공시는 항목·주석·표, 기사는 문단)를 적는다. 본문을 연 근거는 `"verified_original": true` 로 표시한다(조율자가 그 ID 를 `confirm` 한다). 제목만 본 근거는 `false` 이고 `unverified` 에 "제목만 보고 판정함"을 적는다.
- ① 네 질문에 쓸 근거를 **일부러 찾는다.** 새 후보에 없으면 확정 근거 603건 안에서 이미 있는지 보고, 그래도 없으면 공시·IR·독립 측정 페이지를 직접 열어 근거로 올린다(이때 출처는 `sources` 에 `SRC-WEB-<company>-NNN` 으로 새로 등록. `url`·`accessed_at`·`publisher` 필수). 회사마다 최소한 다음이 있어야 판단 세션이 일할 수 있다.
  - 가격 실측: 정가 인상·유지와 그 뒤 고객 유지(좌석·구독자·광고 단가), 또는 총마진 추세의 원인 설명(10-K MD&A 의 마진 변동 사유 문단).
  - 전환비용: 대체재가 있는데도 남았다는 사실(갱신·유지율) 또는 이탈 사례.
  - 대체 공급: 경쟁 제품 출하 실적(경쟁사 공시·독립 벤치마크).
  - 회수 루프: 개발자·사용자 수 시계열(두 시점 이상)과 보완재 수.
  - 지속성 할인: 10-K 고객 집중 공시 문단(있으면).
- ② 는 독립 측정 순위표(AA Intelligence Index·ARC-AGI·SWE-bench 류)의 **같은 날짜 한 장**을 모델 기업 공통 근거로 올린다(묶음 D 가 올리고 다른 묶음은 중복으로 올리지 않는다). 칩·파운드리는 MLPerf·독립 분석(묶음 A).
- ③ 가속도는 같은 정의의 성장률 두 개가 나오는 자료(실적 발표 두 분기, 10-Q 세그먼트 표)를 올린다.
- 필수 키: `company_id`, `factors`, `kind`(news|filing), `source_id`(후보의 `source_id` 그대로. 직접 연 페이지는 새 `SRC-WEB-…`), `published_at_utc`, `title`, `excerpt`, `relevance`(추론임을 표시), `channel`, `conditional_impact`("지금은 유지:" 또는 "재검토:"로 시작), `horizon`, `counter_evidence`, `unverified`, `change_vs_previous`, 선택 `locator`. `evidence_id` 는 적지 않는다(조율자가 부여).

## 2. 트리거

- `output/ai-scorecard-2026-10-rescore/triggers.json` 에서 맡은 회사의 `status: watching` 항목마다 `triggers` 에 한 줄을 쓴다. `trigger_id` 는 그대로, `status`(watching·fired·expired·withdrawn), `deadline`, `finding`(2026-10-06~10-08 후보에서 무엇을 봤는지. 검색 범위를 적는다), 발동이면 `evidence_ids`(이번 산출물의 근거는 ID 가 아직 없으니 `source_ids` 로 가리킨다). 하나도 빠뜨리지 않는다. 기한이 기준일(2026-10-08)을 지났는데 관찰 유지면 `deadline` 을 늦추고 `note` 에 이유를 적는다.
- 새 트리거는 `new_triggers` 에 전체 키(`company_id`, `factors`, `observation`, `condition`, `deadline`, `source_ids`, `status`, `recheck{factors, what}`)로. 미래 점수를 적지 않는다.

## 3. 관측

`OBS-INSTRUCTIONS.md` 의 지표를 맡은 회사에 대해 읽는다. `observations` 항목은 `company_id`, `metric`, `value`, `unit`, `as_of`, `kind: actual`, `source_id`, `status: verified`, `raw`(원문 발췌), `note`(페이지·표 이름), 필요하면 `period`. 추세용 지표(`mau`·`token_share`·`gross_margin_ttm`+`gross_margin_ttm_prior`)는 두 시점 이상. 공시 없음이 확인되면 `value: null`, `status: not_disclosed`, `missing_type: not_disclosed_confirmed`, `note` 에 그 문면과 자리. 못 찾은 것은 등록하지 않고 보고에 적는다. 값·문언·인용 위치를 셋 다 확인한다. 10-K·10-Q 는 `data/_sec/docs/` 캐시를 먼저 보고 없으면 `uv run --frozen python -X utf8 scripts/scorecard_cli.py sec-get <SEC 주소>` 로 받는다.

## 출력

`work/out-<묶음>.json` 에 `{"group", "sources", "evidence", "triggers", "new_triggers", "observations"}`. 마지막 답변에는 회사별로 올린 근거 수(본문 확인 수), 트리거 처리 결과(관찰·발동·만료·철회 수), 등록한 관측과 공시 없음·못 찾음 목록, 그리고 판단 세션에 알려야 할 것(예: "Palantir 는 NRR 공개", "Meta AI 월간 사용자는 2026-07 실적 콜에 10억")을 적는다. 문장은 완결된 현재 상태 문장으로 쓰고 규칙 버전·작업 번호·이전 판 참조를 쓰지 않는다.
