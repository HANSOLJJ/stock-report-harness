---
description: scorecard 실행의 승인 대기 상태를 점검하고 사람이 승인 페이지에서 승인하도록 안내합니다. 에이전트는 승인하지 않습니다.
argument-hint: "<run_id>"
---

사용자가 이 저장소의 AI 기업 9-factor 채점(ai_scorecard) 승인 단계를 요청했습니다.

**입력**: $ARGUMENTS

`.claude/skills/score-approve/SKILL.md`를 읽고 그대로 수행하세요.
승인과 취소는 사람이 승인 페이지(`node server.js --approvals`)에서 합니다. 에이전트는 "승인 대기" 를 보고하고 절차를 안내한 뒤 멈추며, 승인된 뒤의 다음 단계 `/score-build <run_id>`를 알려주세요.
