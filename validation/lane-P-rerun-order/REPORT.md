# 레인 P: 재검증 발견 V2-5 문서 속 재실행 순서 안내 수정 보고서 (2026-10-01)

에이전트: Antigravity. 지시서: `.agents/plans/evidence-layer-2026-09/dispatch/lane-P.md`. 공통 규약: `.agents/plans/evidence-layer-2026-09/dispatch/README.md`.
참조: `validation/lane-V2-recheck/REPORT.md` V2-5 절.

## 1. 개요 및 한 일

판단 수정 또는 근거 확정 뒤 안내대로 `calculate → draft → review`만 다시 돌리면, `research.md`의 머리글에 결속된 입력 해시(`judgments_hash`, `evidence_hash` 등)가 갱신되지 않아 승인 전 계약 검증(`validate_report_contract.py`) 및 승인 단계에서 거부되는 결함(V2-5)이 있었습니다.

소유 파일 내에서 판단 수정·근거 확정 및 관측 갱신 후 재실행 순서 안내를 모두 `research → calculate → draft → review`로 일관되게 수정했습니다. 또한 명령/스킬에서 다시 도는 시작 단계를 가리키던 `/score-calculate` 안내를 `/score-research`로 수정했습니다.

코드(`scripts/**`, `server/**`, `tests/**`)는 레인 N 소유이므로 일절 수정하지 않았으며, 처음 채점의 정상 파이프라인 순서 안내(`plan → collect → research → calculate ...`)는 유지했습니다.

---

## 2. 고친 위치별 전후 대조표

| 파일 | 위치 | 변경 전 | 변경 후 |
|---|---|---|---|
| `AGENTS.md` | 19행 | `calculate`·`draft`·`review` 를 다시 돌린 뒤 사람이 승인한다. | `research → calculate → draft → review` 를 다시 돌린 뒤 사람이 승인한다. |
| `README.md` | 78행 | 에이전트에게 `calculate`·`draft`·`review` 를 다시 시킨 뒤 승인합니다. | 에이전트에게 `research → calculate → draft → review` 를 다시 시킨 뒤 승인합니다. |
| `README.md` | 86행 | 3. 해시가 바뀌었다는 안내가 나오면 에이전트에게 `calculate`·`draft`·`review` 를 다시 시킵니다. | 3. 해시가 바뀌었다는 안내가 나오면 에이전트에게 `research → calculate → draft → review` 를 다시 시킵니다. |
| `.claude/skills/score-approve/SKILL.md` | 32행 | 에이전트가 `calculate` → `draft` → `review` 를 다시 수행하고 "승인 대기" 를 보고한다. | 에이전트가 `research → calculate → draft → review` 를 다시 수행하고 "승인 대기" 를 보고한다. |
| `.claude/skills/score-approve/SKILL.md` | 36행 | 에이전트가 `calculate` → `draft` → `review` 를 다시 수행하고, 다시 "승인 대기" 를 보고한다. | 에이전트가 `research → calculate → draft → review` 를 다시 수행하고, 다시 "승인 대기" 를 보고한다. |
| `.claude/skills/score-review/SKILL.md` | 37행 | `calculate` → `draft` → `review-template --force` 부터 다시 돌리고 | `research → calculate → draft → review-template --force` 부터 다시 돌리고 |
| `.claude/skills/score-collect/SKILL.md` | 43행 | 확정하면 해시가 바뀌므로 `calculate`·`draft`·`review` 를 다시 돌린다. | 확정하면 해시가 바뀌므로 `research → calculate → draft → review` 를 다시 돌린다. |
| `docs/scorecard/structure.md` | 62행 | 관측을 새로 넣고 `calculate → draft → review` 를 다시 돌린 뒤 사람이 다시 승인해야 한다. | 관측을 새로 넣고 `research → calculate → draft → review` 를 다시 돌린 뒤 사람이 다시 승인해야 한다. |
| `docs/scorecard/structure.md` | 137행 | 근거를 확정하면 판단·결과·초안 해시가 바뀌어 리뷰가 무효가 되므로 `calculate`·`draft`·`review` 를 다시 돌린다. | 근거를 확정하면 판단·결과·초안 해시가 바뀌어 리뷰가 무효가 되므로 `research → calculate → draft → review` 를 다시 돌린다. |
| `docs/scorecard/structure.md` | 143행 | 판단 해시가 바뀌므로 `calculate`·`draft`·`review` 를 다시 돌린 뒤 사람이 승인한다. | 판단 해시가 바뀌므로 `research → calculate → draft → review` 를 다시 돌린 뒤 사람이 승인한다. |
| `.claude/commands/score-research.md` | 12행 | 고친 뒤에는 `/score-calculate <run_id>` 부터 다시 돕니다. | 고친 뒤에는 `/score-research <run_id>` 부터 다시 돕니다. |
| `.claude/skills/score-research/SKILL.md` | 18행 | 고친 뒤에는 `/score-calculate <run_id>` 부터 다시 돈다. | 고친 뒤에는 `/score-research <run_id>` 부터 다시 돈다. |

---

## 3. 남은 것이 없음을 확인한 Grep 검증

### (1) `calculate.*draft.*review` 패턴 검색

```bash
rg -n "calculate.*draft.*review" AGENTS.md README.md docs/ .claude/
```

출력 결과:
- `AGENTS.md:19`: `research → calculate → draft → review` (수정 완료)
- `README.md:36`: `plan → collect → research → calculate → draft → review → (사람) 승인 → build` (정상 파이프라인 전체 순서, 유지)
- `README.md:78`: `research → calculate → draft → review` (수정 완료)
- `README.md:86`: `research → calculate → draft → review` (수정 완료)
- `docs/scorecard/structure.md:62`: `research → calculate → draft → review` (수정 완료)
- `docs/scorecard/structure.md:124`: `collect·research(신규만) ──► diff ... ──► calculate ──► ... ──► draft ──► review` (정상 파이프라인 전체 흐름 다이어그램, 유지)
- `docs/scorecard/structure.md:127`: 모든 단계 목록 (`init`·`collect`·`research`·`calculate`·`draft`·`review-template`) (유지)
- `docs/scorecard/structure.md:137`: `research → calculate → draft → review` (수정 완료)
- `docs/scorecard/structure.md:143`: `research → calculate → draft → review` (수정 완료)
- `docs/scorecard/structure.md:166`: 명령 목록 (유지)
- `docs/scorecard/open-items.md:54`: 소유 밖 파일 (아래 4절 참조)
- `docs/memory-system.md:91`: 단계 순서 설명 (소유 밖 파일 및 정상 순서)
- `docs/scorecard/design-guideline.md:353`: 정상 파이프라인 순서 (소유 밖 파일)
- `.claude/skills/score-collect/SKILL.md:43`: `research → calculate → draft → review` (수정 완료)
- `.claude/skills/score-approve/SKILL.md:32`: `research → calculate → draft → review` (수정 완료)
- `.claude/skills/score-approve/SKILL.md:36`: `research → calculate → draft → review` (수정 완료)
- `.claude/skills/score-review/SKILL.md:21`: 상위 단계 목록 `(collect/research/calculate/draft/렌더러)` (유지)
- `.claude/skills/score-review/SKILL.md:37`: `research → calculate → draft → review-template --force` (수정 완료)
- `.claude/skills/score-goal/SKILL.md:3, 9` 및 `.claude/commands/score-goal.md:2`: 정상 파이프라인 순서 (유지)

소유 파일 내에서 `research`가 누락된 재실행 순서 안내는 0건입니다.

---

## 4. 소유 밖 파일에서 발견한 문제

- `docs/scorecard/open-items.md` 54행:
  "조사 결과를 실제 점수에 넣으려면 나머지 2분기와 통화·주식단위 기준 검증을 확보해 관측을 새로 넣고 `calculate → draft → review → approve` 를 다시 밟아야 한다."
  - 상태: 지시서 소유 파일 목록(`AGENTS.md`, `README.md`, `docs/scorecard/structure.md`, `.claude/skills/score-*/SKILL.md`, `.claude/commands/score-*.md`, 보고서)에 포함되지 않으므로 공통 규약에 따라 수정하지 않고 기록만 남깁니다.

---

## 5. 검증 러너 결과

| 러너 | 결과 | 비고 |
|---|---|---|
| `npm run check` | 통과 | node --check server.js && compileall scripts |
| `uv run --frozen python -X utf8 -m unittest discover -s tests -t .` | 1146건 중 2 failed, 13 skipped | 작업 전 기준선과 동일 (WiringSmokeTest 2건: Windows Git bash PATH uv 부재 환경 이슈, 13건: 원자료 부재 건너뛰기) |
| `uv run --frozen pytest -q` | 2 failed, 1131 passed, 13 skipped, 2139 subtests passed | 작업 전 기준선과 동일 (신규 실패 0건) |

내 변경으로 인한 실패 집합 증가 없음(신규 실패 0건).

---

## 6. 소유 파일 및 변경 통계

`git diff --stat HANSOLJJ/revision_checker...HEAD` 결과:

```
 .claude/commands/score-research.md      |   2 +-
 .claude/skills/score-approve/SKILL.md   |   4 +-
 .claude/skills/score-collect/SKILL.md   |   2 +-
 .claude/skills/score-research/SKILL.md  |   2 +-
 .claude/skills/score-review/SKILL.md    |   2 +-
 AGENTS.md                               |   2 +-
 README.md                               |   4 +-
 docs/scorecard/structure.md             |   6 +-
 validation/lane-P-rerun-order/REPORT.md | 112 ++++++++++++++++++++++++++++++++
 9 files changed, 124 insertions(+), 12 deletions(-)
```

소유 파일 이외의 파일은 전혀 변경되지 않았습니다.

---

## 7. 최종 커밋 정보

- 커밋 메시지: `docs: 판단 수정·근거 확정 뒤 재실행 순서 안내에 research 추가(V2-5)`
- 최종 커밋 SHA: `ec083c3`

