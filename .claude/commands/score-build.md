---
description: 승인된 scorecard 실행을 대시보드 HTML 과 history.csv 로 빌드합니다.
argument-hint: "<slug>"
---

사용자가 이 저장소의 AI 기업 9-factor 채점(ai_scorecard) build 단계를 요청했습니다.

**입력**: $ARGUMENTS

`.claude/skills/score-build/SKILL.md`를 읽고 그대로 수행하세요.
수동 HTML 작성 대신 `uv run --frozen python -X utf8 scripts/build_report.py <run_id>`를 실행하고, 완료 후 `uv run --frozen python -X utf8 scripts/validate_report_contract.py <run_id> --require-html` 결과를 보고하세요.
