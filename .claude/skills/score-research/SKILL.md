---
name: score-research
description: scorecard 실행의 원자료(observations)·판단(judgments)·출처를 엄격 검증하고 output/<run_id>/research.md 를 생성한다. /score-collect 뒤 /score-research <run_id> 로 사용한다.
---

# 채점 리서치 스킬

실행 입력을 검증하고 `output/<run_id>/research.md` 를 만든다. 새 자료를 넣는 단계이기도 하다. 순서는 `collect` → 후보 선별 → `research` 이다.

## 절차

1. `output/<run_id>/plan.md` 와 `output/<run_id>/run.json` 이 있는지 확인한다. 근거 후보가 필요하면 `/score-collect <run_id>` 를 먼저 수행했는지 확인한다.
2. 새 원자료가 있으면 `output/<run_id>/observations.json` 에 추가한다. 필수: `metric`(카탈로그), `value`, `unit`, `as_of`, `kind`, `source_id`(sources.json 에 등록), `status`(새 자료는 `verified`), `basis`(주가·EPS 는 `currency`·`share_basis`, NTM EPS 는 `quarters` 4개 YYYYQn).
   - 수집 실패는 `collection_failed`, 확인된 비공개는 `not_disclosed`, 기간·범위가 다르면 `incompatible_basis`. 다른 기간·지표로 조용히 대체하지 않는다.
   - 출처 없는 URL 을 만들지 않는다. URL 이 없으면 `url: null`.
3. 새 정성 판정이 있으면 `judgments.json` 을 손으로 고치지 말고 `judge` 명령으로 판단 입력을 고친다. 명령이 형식을 검증하고, `status: new`·검토자·검토일을 쓰고, 이전 값을 `revision_history` 에 남긴다. F1·F4·F8 은 점수와 근거, F3 는 criteria, F5 는 grade, F7 은 matrix, F9 는 gate_inputs 를 고친다. F3·F5·F7·F9 의 점수 칸은 규칙이 계산하므로 고칠 수 없다.
   `uv run --frozen python -X utf8 scripts/scorecard_cli.py judge <run_id> --company <id> --factor F1..F9 (--set key=value … | --evidence "문장" … | --json 파일) --reason "…" --by <이름> [--take-lock]`
   - 인자는 `--help` 로 확인한다. 고친 뒤에는 `/score-calculate <run_id>` 부터 다시 돈다. 사람이 승인 페이지에서 판단을 고친 경우도 같다.
   - `status: new` 판단은 `evidence_ids` 로 **confirmed 근거만** 인용한다. candidate 근거를 인용하면 교차 참조 검증이 실패한다. 아직 확정되지 않은 후보는 인용하지 말고, 사람이 승인 페이지에서 확정한 뒤 인용한다.
4. 실행한다: `uv run --frozen python -X utf8 scripts/scorecard_cli.py research <run_id> [--no-register] [--take-lock]`.
   - 기본 동작은 `evidence.json` 이 인용한 후보의 출처를 `sources.json` 에 자동 등록하는 것이다. `--no-register` 는 이 등록을 하지 않는다. 등록 없이 검증만 보고 싶을 때만 쓴다.
   - 스키마 오류(`[FAIL]`)가 나면 입력을 고친다. 임의 해석으로 통과시키지 않는다.
5. `output/<run_id>/research.md` 의 "미결 항목" 을 읽고 unknown 입력·자료 대기·규칙 결정을 보고한다.

## 제약

- 승계(carried) 판단을 새로 검증된 것처럼 바꾸지 않는다. 재검토했으면 `status: new`, `reviewed_at` 갱신.
- LLM 이 제안한 판정은 사람이 확인하기 전까지 `status: new` 로 확정하지 않는다(evidence 에 "후보" 표시).
- `not_disclosed`(발행사가 공시하지 않음을 확인)와 `unverified`(우리가 찾지 못함)를 구분한다. 어느 쪽인지 모르면 `unverified` 로 둔다.

## 완료 보고

research 경로, 관측·판단 건수, 미결 항목, 다음 명령 `/score-calculate <run_id>`.
