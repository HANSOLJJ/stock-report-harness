---
name: score-collect
description: scorecard 실행의 근거 후보(뉴스·공시·가격)를 수집해 evidence.json 과 triggers.json 으로 선별한다. /score-collect <run_id> 로 사용하며 후보 수집과 선별만 하고 점수는 바꾸지 않는다.
---

# 채점 근거 수집 스킬

실행 하나의 근거 후보(뉴스·공시·가격)를 모으고, factor 와 관련 있는 것만 `evidence/evidence.json` 에 후보(`candidate`)로 올린다. 점수와 판단은 이 단계에서 바꾸지 않는다. 후보를 확정(`confirmed`)하는 것은 사람이며, 승인 페이지에서 한다.

```
collect → 후보 선별(evidence.json) → triggers.json → research
```

## 절차

1. `output/<run_id>/run.json` 이 있는지 확인한다. 없으면 중단하고 `/score-plan` 이나 `/score-extend` 로 실행 생성을 먼저 안내한다.
2. 후보를 수집한다. 결과는 `output/<run_id>/evidence/candidates.json` 에 쌓이고, 수집한 원문 캐시는 `data/<company_id>/`(gitignore)에 남는다.
   ```
   uv run --frozen python -X utf8 scripts/scorecard_cli.py collect <run_id> [--company a,b] [--kind news|filings|prices|all] [--since YYYY-MM-DD] [--forms 8-K,10-Q] [--locale en-US] [--from-file PATH] [--dry-run] [--take-lock]
   ```
   - `--company`: `run.companies` 가운데 일부만 수집한다(쉼표).
   - `--kind`: `news`, `filings`, `prices`, `all`. 공시는 형식 기본값이 `8-K,10-Q,10-K,20-F,6-K` 이고 `--forms` 로 바꾼다.
   - `--since`: 후보 창 시작일. 기본은 기준일(`as_of`)에서 180일 전이다.
   - `--from-file`: 네트워크 대신 파일을 읽는다. `--kind` 하나와 함께 쓴다.
   - `--dry-run`: 무엇을 가져올지만 확인한다.
   - 공시 수집(`--kind filings`)에는 환경변수 `SEC_UA`(이름과 연락처를 담은 식별 문자열)가 필요하다. 비어 있으면 그 기업의 공시는 건너뛰고 나머지는 계속 돈다. 값을 저장소나 문서에 적지 않는다.
   - `--kind prices` 는 yfinance 로 ⑥ `price`·`market_cap` 관측을 `observations.json` 에 넣는다. EPS·컨센서스는 받지 않는다. 조회일이 종가일과 하루 넘게 다르면 벤더 시가총액을 쓰지 않고, ADR 시가총액은 벤더 값만 쓴다.
3. `candidates.json` 을 읽고 factor 와 관련 있는 후보만 `evidence/evidence.json` 에 `status: candidate` 로 선별한다.
   - 필수 필드: `evidence_id`(`EV-<company_id>-NNN`), `company_id`, `factors`, `kind`(news|filing), `source_id`(sources.json 에 등록된 것), `published_at_utc`, `title`, `excerpt`, `relevance`, `channel`(disclosure|press|company_statement|secondary), `conditional_impact`, `horizon`, `counter_evidence`, `unverified`, `change_vs_previous`.
   - `excerpt` 는 원문 그대로 600자 이하로 옮긴다. 요약하거나 고쳐 쓰지 않는다.
   - `relevance` 는 추론이므로 추론임을 표시한다.
   - `conditional_impact` 에는 점수 이동(`-3→-4`, `+2점`)을 적지 않는다. 사건이 미치는 조건부 영향을 말로 쓴다.
   - `published_at_utc` 가 `run.info_cutoff` 보다 늦은 후보는 올리지 않는다.
4. 재채점 조건은 `output/<run_id>/triggers.json` 에 `status: watching` 으로 적는다. `condition`·`deadline`·`recheck` 를 채우고, 미래 점수를 저장하지 않는다(C-14).
5. 실행한다: `uv run --frozen python -X utf8 scripts/scorecard_cli.py research <run_id>`. 이 단계는 `/score-research` 가 이어받는다.

## 사람이 하는 일

선별한 근거는 후보 상태로 남는다. 사람이 `node server.js --approvals` 로 승인 페이지를 띄워 근거를 확정하거나 거부한다. 에이전트는 `confirm` 으로 근거를 확정하지 않는다. 사용자가 확정할 ID 를 지정해 지시한 경우에만 그 ID 로 실행한다. 확정하면 해시가 바뀌므로 `calculate`·`draft`·`review` 를 다시 돌린다.

## 제약

- 1차 출처를 우선한다. 기업 IR, 공식 뉴스룸, 공시, 거래소·중앙은행 데이터를 먼저 쓰고, 이벤트와 리스크는 공신력 있는 매체로 보완한다.
- URL 을 조작하지 않는다. URL 이 없으면 `url: null` 로 두고, 검색·제공자 폴백 URL 을 쓴 경우 `url_is_fallback: true` 를 표시한다.
- 수집이 차단되거나 실패하면 누락된 자료를 정확히 명시한다. 조용히 다른 자료·기간·지표로 대체하지 않는다.
- 사실과 추론을 분리한다. 원문에서 확인한 내용은 사실로, 우리가 해석한 내용은 추론으로 표시한다.
- 사람이 `confirmed` 로 올리기 전까지 `status: new` 판단이 `candidate` 근거를 인용하지 않는다.
- `not_disclosed`(발행사가 공시하지 않음을 확인)와 `unverified`(우리가 찾지 못함)를 구분한다. 어느 쪽인지 모르면 `unverified` 로 둔다.
- 기사 본문을 가져오지 않는다. 제목·요약·URL 만 다룬다.
- 다른 기업의 점수를 근거로 인용하지 않는다.

## 완료 보고

`candidates.json` 후보 수, `evidence.json` 에 올린 근거 수, `triggers.json` 항목 수, 수집 실패·누락 목록, 다음 명령 `/score-research <run_id>`.
