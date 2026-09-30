---
description: AI 기업 9-factor 채점 실행을 생성합니다(plan + run 입력 승계). 예: /score-plan 2026-09 기준선 재계산
argument-hint: "자연어 요청 (기준일·제목 포함)"
---

사용자가 이 저장소의 AI 기업 9-factor 채점(ai_scorecard) plan 단계를 요청했습니다.

**입력**: $ARGUMENTS

`.claude/skills/score-plan/SKILL.md`를 읽고 그대로 수행하세요.
완료 후 생성된 `output/<run_id>/plan.md`와 실행 묶음 폴더, 다음 단계 `/score-collect <run_id>`를 알려주세요.
