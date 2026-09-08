---
name: score-approve
description: 사용자가 검토한 scorecard 실행을 승인한다. 규칙·자료·판단·결과·초안 해시에 승인을 결합하며, 사용자가 /score-approve <slug> 를 직접 지시했을 때만 실행한다.
---

# 채점 승인 스킬

승인은 사용자 행위다. 에이전트가 스스로 승인하거나 `score-goal` 안에서 자동 실행하지 않는다.

## 절차

1. `reviews/<slug>.md` 가 `status: pass` 이고 `python scripts/validate_report_contract.py <slug>` 가 통과하는지 확인한다.
2. `scorecard/runs/<slug>/preview.md` 의 변경 요약(기존/제안 점수, 순위 영향, 변경 원인, 미결 항목)을 사용자에게 다시 보여준다.
3. 사용자가 승인을 지시하면 실행한다: `python scripts/scorecard_cli.py approve <slug> --by "<사용자 이름>" [--note "..."]`.
4. `approval.json` 의 approval_id 를 보고한다.

## 제약

- 승인 뒤 자료·규칙·판단·초안이 바뀌면 승인은 무효다. 다시 리뷰·승인한다.
- 미결 규칙 결정이 남아 있어도 승인할 수 있다(미완료 기업은 순위 제외로 표시됨). 단 사용자가 그 사실을 알고 있어야 한다.

## 완료 보고

approval_id, 승인자, 다음 명령 `/score-build <slug>`.
