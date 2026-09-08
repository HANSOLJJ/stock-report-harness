---
name: score-goal
description: 종단 간 scorecard 파이프라인. 자연어 요청 하나로 plan → research → calculate → draft → review 를 한 턴에 실행하고 사용자 승인(awaiting_user)에서 멈춘다. 승인과 빌드는 사용자 결정 뒤 /score-approve, /score-build 로 진행한다.
---

# 채점 목표 스킬

```
plan → research → calculate → draft → review → (awaiting_user) → approve → build
```

## 규칙

1. review 까지는 한 턴에서 연속 실행한다. 중간 보고로 턴을 끊지 않는다.
2. `Skill` 도구로 하위 스킬을 호출하지 않는다. 각 `score-*` SKILL.md 의 절차를 인라인으로 수행한다.
3. 규칙 결정(C-xx)이 필요하면 사용자에게 묻지 말고 미결 상태 그대로 계산한다. 미완료 기업은 순위에서 제외되며 preview.md 에 필요한 결정이 남는다.
4. review 가 needs_fix 면 해당 단계로 돌아가 최대 3회 수정·재리뷰한다. 같은 차단 이슈가 3회면 blocked 로 보고한다.
5. review pass 뒤 **멈춘다**. 승인은 사용자 행위다. approve/build 를 자동 실행하지 않는다.

## 완료 보고 (review 후 한 번)

- 산출물 목록(plan, run 입력, research, results/preview, draft, review)
- 순위 요약과 미완료 기업·사유
- 필요한 규칙 결정 목록(C-xx, 선택지, 영향 기업)
- 다음 행동: 사용자 승인 `/score-approve <slug>` → `/score-build <slug>`
