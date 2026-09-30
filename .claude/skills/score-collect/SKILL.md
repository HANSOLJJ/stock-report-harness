---
name: score-collect
description: scorecard 실행의 근거 후보(뉴스·공시·가격)를 수집해 evidence.json 과 triggers.json 으로 선별한다. /score-collect <run_id> 로 사용하며 후보 수집과 선별만 하고 점수는 바꾸지 않는다.
---

> 초안 — collect 명령은 3.4 에서 구현되고 이 스킬은 4.5 에서 완성한다.

# 채점 근거 수집 스킬

실행 단위의 근거 후보를 모으고, factor 와 관련 있는 것만 `evidence/evidence.json` 에 후보로 올린다. 점수와 판단은 이 단계에서 바꾸지 않는다.

## 절차

1. `output/<run_id>/run.json` 이 있는지 확인한다. 없으면 중단하고 실행 생성을 먼저 안내한다.
2. 후보를 수집한다. `output/<run_id>/evidence/candidates.json` 이 만들어진다.
   `uv run --frozen python -X utf8 scripts/scorecard_cli.py collect <run_id> [--company a,b] [--kind news|filings|prices|all] [--since YYYY-MM-DD]`
3. `candidates.json` 을 읽고 factor 와 관련 있는 후보만 `evidence/evidence.json` 에 `status: candidate` 로 선별한다.
   - `excerpt` 는 원문 그대로 600자 이하로 옮긴다. 요약하거나 고쳐 쓰지 않는다.
   - `relevance` 는 추론이므로 추론임을 표시한다.
4. 재채점 조건은 `triggers.json` 에 `status: watching` 으로 적는다. 미래 점수를 적지 않는다.
5. 실행한다: `uv run --frozen python -X utf8 scripts/scorecard_cli.py research <run_id>`.

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
