---
description: scorecard 실행의 원자료·판단 입력을 검증하고 research 문서를 생성합니다.
argument-hint: "<slug>"
---

사용자가 이 저장소의 AI 기업 9-factor 채점(ai_scorecard) research 단계를 요청했습니다.

**입력**: $ARGUMENTS

`.claude/skills/score-research/SKILL.md`를 읽고 그대로 수행하세요.
완료 후 `output/<run_id>/research.md`와 미결 항목, 다음 단계 `/score-calculate <run_id>`를 보고하세요.
정성 판단 입력을 고쳐야 하면 점수를 직접 고치지 말고 `scorecard_cli.py judge` 로 판단 입력을 고치세요(인자는 `--help`, 사용법은 `.claude/skills/score-review/SKILL.md` 의 "판단 수정을 제안할 때"). 고친 뒤에는 `/score-calculate <run_id>` 부터 다시 돕니다.
