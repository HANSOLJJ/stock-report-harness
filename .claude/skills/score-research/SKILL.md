---
name: score-research
description: scorecard 실행의 원자료(observations)·판단(judgments)·출처를 엄격 검증하고 research/<slug>.md 를 생성한다. /score-plan 뒤 /score-research <slug> 로 사용한다.
---

# 채점 리서치 스킬

실행 입력을 검증하고 `research/<slug>.md` 를 만든다. 새 자료를 넣는 단계이기도 하다.

## 절차

1. `plan/<slug>.md` 와 `scorecard/runs/<slug>/` 가 있는지 확인한다.
2. 새 원자료가 있으면 `observations.json` 에 추가한다. 필수: `metric`(카탈로그), `value`, `unit`, `as_of`, `kind`, `source_id`(sources.json 에 등록), `status`(새 자료는 `verified`), `basis`(주가·EPS 는 `currency`·`share_basis`, NTM EPS 는 `quarters` 4개 YYYYQn).
   - 수집 실패는 `collection_failed`, 확인된 비공개는 `not_disclosed`, 기간·범위가 다르면 `incompatible_basis`. 다른 기간·지표로 조용히 대체하지 않는다.
   - 출처 없는 URL 을 만들지 않는다. URL 이 없으면 `url: null`.
3. 새 정성 판정이 있으면 `judgments.json` 에 `status: new` 로 교체한다. 근거(`evidence`)·검토자·검토일 필수. F3 는 criteria, F5 는 grade, F7 은 matrix, F9 는 gate_inputs 로 입력하고 점수는 비운다.
4. 실행한다: `python scripts/scorecard_cli.py research <slug>`.
   스키마 오류(`[FAIL]`)가 나면 입력을 고친다. 임의 해석으로 통과시키지 않는다.
5. `research/<slug>.md` 의 "미결 항목" 을 읽고 unknown 입력·자료 대기·규칙 결정을 보고한다.

## 제약

- 승계(carried) 판단을 새로 검증된 것처럼 바꾸지 않는다. 재검토했으면 `status: new`, `reviewed_at` 갱신.
- LLM 이 제안한 판정은 사람이 확인하기 전까지 `status: new` 로 확정하지 않는다(evidence 에 "후보" 표시).

## 완료 보고

research 경로, 관측·판단 건수, 미결 항목, 다음 명령 `/score-calculate <slug>`.
