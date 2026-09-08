---
description: 사용자가 검토한 scorecard 실행을 승인하고 해시를 결합합니다. 사용자의 명시적 지시로만 실행합니다.
argument-hint: "<slug> [--by 이름]"
---

사용자가 stock-report-harness 의 AI 기업 9-factor 채점(ai_scorecard) approve 단계를 요청했습니다.

**입력**: $ARGUMENTS

`.claude/skills/score-approve/SKILL.md`를 읽고 그대로 수행하세요.
승인은 사용자 행위이므로 사용자가 이 명령을 직접 내렸을 때만 `approve`를 실행하고, 완료 후 `/score-build <slug>`를 안내하세요.
