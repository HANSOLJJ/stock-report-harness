---
name: score-plan
description: AI 기업 9-factor 채점(ai_scorecard) 실행을 생성한다. /score-plan "2026-09 기준선 재계산" 처럼 사용하며 output/<run_id>/ 묶음에 plan.md 와 입력(기준선 승계)을 만든다.
---

# 채점 실행 생성 스킬

`output/<run_id>/plan.md` 와 `output/<run_id>/{run,observations,judgments,sources}.json` 을 생성한다. 이후 단계의 단일 기준이다. 실행 하나의 산출물은 전부 `output/<run_id>/` 한 폴더에 모인다.

## 절차

1. 요청을 파싱한다. 제목, 분석 기준일(`as_of`, 없으면 기준선 날짜 2026-09-02), 대상 기업(없으면 기준선 14개사), 실행 단위 규칙 결정(사용자가 명시한 C-xx 선택만).
2. run_id(=slug)는 `ai-scorecard-<YYYY-MM>-<label>` 형식으로 정한다 (예: `ai-scorecard-2026-09-baseline`).
3. 기준선이 없으면 먼저 `uv run --frozen python -X utf8 scripts/scorecard_cli.py import-baseline` 을 실행한다 (원본 HTML/MD 경로가 다르면 `--html`, `--md`).
4. 실행한다. 새 실행은 규칙 v1.8 을 쓴다.
   ```
   uv run --frozen python -X utf8 scripts/scorecard_cli.py init <run_id> --rule v1.8 --as-of <YYYY-MM-DD> --title "<제목>" --request "<요청 원문>" [--purpose "..."] [--companies a,b] [--decision C-16=hold --rationale "..." --by <이름>]
   ```
   `--decision` 은 사용자가 근거와 함께 명시적으로 지시했을 때만 넣는다. 기본은 미결(needs_rule_decision).
5. 이 스킬은 collect/research/calculate 로 진행하지 않는다. `score-goal` 에서 호출된 경우에만 즉시 다음 단계(`collect`)로 간다.

## 제약

- plan 을 손으로 쓰지 않는다. `init` 이 생성한 파일만 쓴다.
- 다른 소유자의 실행 잠금(`output/<run_id>/.lock`)이 있으면 명령이 거부한다. 잠금을 넘겨받아야 할 때만 `--take-lock` 을 쓴다.
- 기업 ID 는 `scorecard/companies.json` 에 있는 것만 쓴다. 새 기업은 레지스트리에 먼저 `/score-add-company` 로 등록한다(안정 ID, 상장 여부, share_basis, 통화).
- 투자 권유·수익 보장 표현을 쓰지 않는다.

## 완료 보고

plan 경로(`output/<run_id>/plan.md`), 실행 묶음 폴더, 기준일, 기업 수, 규칙 버전, 적용한 결정 목록, 다음 명령 `/score-collect <run_id>`.
