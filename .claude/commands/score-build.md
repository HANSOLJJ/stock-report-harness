---
description: 승인된 scorecard 실행을 대시보드 HTML 과 history.csv 로 빌드합니다.
argument-hint: "<slug>"
---

사용자가 stock-report-harness 의 AI 기업 9-factor 채점(ai_scorecard) build 단계를 요청했습니다.

**입력**: $ARGUMENTS

`.claude/skills/score-build/SKILL.md`를 읽고 그대로 수행하세요.
수동 HTML 작성 대신 `python scripts/build_report.py <slug>`를 실행하고, 완료 후 `python scripts/validate_report_contract.py <slug> --require-html` 결과를 보고하세요.
