---
name: score-calculate
description: scorecard 9개 factor 를 규칙·입력에서 결정론적으로 계산해 results.json 과 기준선 대비 preview.md 를 만든다. /score-research 뒤 /score-calculate <slug> 로 사용한다.
---

# 채점 계산 스킬

## 절차

1. `python scripts/scorecard_cli.py calculate <slug>` 를 실행한다.
2. 출력의 순위·미완료 기업·미결 결정(C-xx)을 읽는다. `scorecard/runs/<slug>/preview.md` 의 "필요한 규칙 결정" 을 사용자에게 그대로 전달한다.
3. 사용자가 결정을 내리면 `run.json` 의 `decisions` 에 `{id, choice, rationale, decided_by, decided_at}` 를 추가하고 다시 `calculate` 한다. 결정 없이 기본값을 채택하지 않는다.
4. 계산 후 `research` 가 오래됐다는 검증 오류가 나면 `research` 를 다시 생성한다(입력 해시 결속).
5. 기업을 더한 실행이면 `python scripts/scorecard_cli.py diff <slug> --against <이전 slug>` 로 기존 기업이 움직이지 않았는지 확인한다. 1층(입력 가법성)·2층(점수 투영 불변) 위반이 하나라도 있으면 사용자에게 그대로 보고한다.

## 제약

- 자동 산출 점수(results.json)를 손으로 고치지 않는다. 입력이나 규칙을 고쳐 재계산한다.
- 규칙 파일(`scorecard/rules/*.json`)을 이 단계에서 바꾸지 않는다. 규칙 변경은 새 버전과 사용자 승인이 필요하다.
- `diff` 의 판정에 subtree 해시를 쓰지 않는다. subtree 해시 차이는 실패 조건이 아니다 — `as_of` 만 바꿔도 달라진다(`factors.F6.calc.p4.stale_asof.as_of`). 불변은 점수 투영으로 판정한다.

## 완료 보고

순위표 요약, 미완료 기업과 사유, 필요한 결정, 다음 명령 `/score-draft <slug>`.
