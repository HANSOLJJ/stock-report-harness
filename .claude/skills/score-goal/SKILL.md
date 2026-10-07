---
name: score-goal
description: 종단 간 scorecard 파이프라인. 자연어 요청 하나로 plan → collect → research → calculate → draft → review 를 한 턴에 실행하고 승인 대기(awaiting_user)에서 멈춘다. 승인은 사람이 승인 페이지에서 하고, 빌드는 그 뒤 /score-build 로 진행한다.
---

# 채점 목표 스킬

```
plan → collect → research → calculate → draft → review → (사람) 승인 → build
```

모든 산출물은 `output/<run_id>/` 한 폴더에 쌓인다.

## 규칙

1. review 까지는 한 턴에서 연속 실행한다. 중간 보고로 턴을 끊지 않는다.
2. `Skill` 도구로 하위 스킬을 호출하지 않는다. 각 `score-*` SKILL.md 의 절차를 인라인으로 수행한다.
3. 규칙 결정(C-xx)이 필요하면 사용자에게 묻지 말고 미결 상태 그대로 계산한다. 미완료 기업은 순위에서 제외되며 preview.md 에 필요한 결정이 남는다.
4. collect 가 만든 근거는 후보 상태로 남는다. 에이전트가 원문을 확인하고 `confirm` 으로 확정하기 전까지 `status: new` 판단은 그 근거를 인용하지 않는다(2026-10-07 사용자 지시: 사람은 최종 승인만 한다).
5. review 가 needs_fix 면 발견을 한 묶음으로 고치고 확인 리뷰를 **한 번** 한다. 확인 리뷰에서도 점수·순위·체크리스트 판정을 바꾸는 발견이 남으면 더 돌지 않고 blocked 로 보고한다(2026-10-06, 리뷰는 1차 리뷰·수정 한 묶음·확인 리뷰 1회로 끝낸다).
   - needs_fix 의 원인이 정성 판단 입력이면 에이전트는 고칠 수 없다. 제안(`propose`)을 한 묶음으로 올리고 **"제안 반영 대기"에서 멈춘다.** 사람이 승인 페이지에서 반영한 뒤 `research → calculate → draft → 확인 리뷰` 를 한 번 돌린다.
6. review pass 뒤 **`awaiting_user` 에서 멈춘다**. 승인은 사람 행위이고 에이전트는 승인하지 않는다. build 도 자동 실행하지 않는다.

## 완료 보고 (review 후 한 번)

- 산출물 목록(`output/<run_id>/` 의 plan, run 입력, evidence·triggers, research, results/preview, draft, review)
- 순위 요약과 미완료 기업·사유
- 필요한 규칙 결정 목록(C-xx, 선택지, 영향 기업)
- 후보 상태로 남은 근거 수
- 다음 행동: "승인 대기" 를 보고한다. 사람이 `node server.js --approvals` 로 승인 페이지(`http://127.0.0.1:3000/approve/<run_id>`)를 열어 근거를 확정하고 승인한 뒤, `/score-build <run_id>` 로 빌드한다.
