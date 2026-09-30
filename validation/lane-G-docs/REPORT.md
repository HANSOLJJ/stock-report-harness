# 레인 G 보고서 — 스킬·에이전트(4.5)와 AGENTS·README·structure.md(4.6)

브랜치 `HANSOLJJ/lane-G`. 지시서 `.agents/plans/evidence-layer-2026-09/dispatch/lane-G.md`. 지금 코드가 사실이라는 원칙으로, 문서를 코드와 `--help` 출력에 맞췄다.

## 한 일

### 커밋 1 (`20bf915`) 스킬·에이전트·안내 문자열

- `score-*` 스킬 12개와 명령 12개의 옛 경로를 `output/<run_id>/` 묶음 경로로 바꾸고 `python scripts/…` 를 `uv run --frozen python -X utf8 scripts/…` 로 바꿨다.
- `score-collect` 의 초안 표시를 지우고 실제 인자(`--company`, `--kind news|filings|prices|all`, `--since`, `--forms`, `--locale`, `--from-file`, `--dry-run`, `--take-lock`)로 완성했다. 수집 → 후보 선별 → `triggers.json` → `research`, 사람이 승인 페이지에서 확정하는 흐름, `SEC_UA`, 가격 관측 범위를 적었다.
- `score-research`: collect → 선별 → research 순서, `--no-register` 설명, 새 판단은 confirmed 근거만 인용.
- `score-plan`: `init --rule v1.8`. `score-extend`: 규칙 버전을 이어받는다는 점과 다음 명령 `/score-collect`.
- `score-goal`: plan 뒤에 collect 를 넣고 `awaiting_user` 에서 멈춘다.
- `score-review`: 리뷰어 입력에 evidence·triggers·sources 를 더하고 근거 불릿 검토를 `evidence-editor` 에 맡겼다. `review-parts/<영역>.md` 에 `reviewer_agent`, `session`, `reviewed_at` 을 둔다고 적었다.
- `score-approve`: 에이전트가 하는 일은 "승인 대기" 보고뿐이다. 사람의 절차(서버 띄우기, 페이지 확인, 근거 확정, 코드 입력 승인)와 확정 뒤 해시가 바뀌면 calculate·draft·review 를 다시 하는 흐름을 적었다. 에이전트에게 approve·revoke 를 실행하라는 문구는 없다.
- `score-build`: 포트 3000 이 쓰이면 기존 프로세스를 끄지 않고 `PORT=<빈 포트>` 를 쓴다. URL 은 `http://localhost:3000/<run_id>/report.html`.
- `fact-checker`·`report-designer` 를 채점표용으로 다시 썼다. 종목 리포트와 토스 디자인 언급을 지웠다. `.codex/agents/*.toml` 세 개를 `.claude/agents/*.md` 본문과 같게 맞췄고 `\r` 문자가 없다(tomllib 로 파싱해 본문 일치 확인).
- 코드 안내 문자열 두 곳(`render_html.py` 의 `awaiting_user`, `validate.py` 의 `사용자 승인 없음`)을 승인 페이지 안내로 바꿨다. 이 문자열을 검사하는 테스트는 없었다.

### 커밋 2 (이 보고서를 포함한 커밋) AGENTS·README·structure.md·memory-system.md

- `AGENTS.md`: 경로 문구와 명령 목록(`/score-collect` 추가), 단계 순서, 근거 계층 규칙, 승인 페이지 문단, 테스트 명령(`uv run` unittest 와 `npm run test:node`)을 고쳤다. `## 금지·주의` 에 채점표 단계 이름으로 일반 규칙(plan 없이 research 금지, review pass 없이 build 금지 등)을 되살렸다. 새 절 `## 통제의 위치` 에 (1) 통제는 코드가 한다, (2) 훅은 도구 호출 밖을 못 막는다, (3) 승인 서버가 떠 있는 동안의 틈과 사용자 수용(2026-09-30)을 적었다. `## Orca worktree 간 메시지와 작업 실행`, `## 원자료 조사 규율` 은 바꾸지 않았다.
- `README.md`: 흐름 표를 묶음 경로·collect·`uv run` 으로 다시 쓰고 근거 계층·승인 페이지 절을 넣었다. 훅 표를 `guard.py` 함수 이름 7개로 다시 썼다(`scripts/hooks/README.md` 기준). 설치·테스트 명령, `data/` 캐시, `SCORECARD_DATA_ROOT`, `SEC_UA`(값은 적지 않음)를 적었다.
- `docs/scorecard/structure.md`: 1절 표의 경로·훅 문구, 2절(배치 표, 실행 묶음 파일 표, 근거·트리거 스키마 행), 5절(흐름, 근거 계층, 승인), 6절 generator 표기, 7절(훅·명령·리뷰어·실행 방식)을 갱신했다.
- `docs/memory-system.md`: 훅 설명을 `guard.py` 의 `inject_memory_context` 로 바꾸고 `python3` 호출을 `uv run` 으로 바꿨다.

## 검증

| 항목 | 결과 |
| --- | --- |
| 소유 파일에서 옛 경로 검색(`plan/<slug>` `research/<slug>` `drafts/<slug>` `reviews/<slug>` `scorecard/runs` `output/<slug>.html` `enforce-citations` `.claude/hooks` `memory_context.py` `stock-`) | 0건 (Grep 도구) |
| 소유 파일에서 에이전트에게 approve·revoke 실행을 시키는 문구 | 0건. `approve`·`revoke` 단어는 "에이전트는 하지 않는다"와 사람 절차, 훅·CLI 설명에만 있다 |
| CLI 인자 대조 | `init` `collect` `research` `calculate` `draft` `review-template` `confirm` `summary` `status` `diff` `resolve-cik` `add-company` `import-baseline` 의 `--help` 를 열어 대조했다. `build_report.py` 와 `validate_report_contract.py` 는 훅이 `--help` 를 단계 위반으로 오인해 막아서 소스의 `argparse` 정의로 확인했다 |
| unittest | 1085건 실행, 실패 1·오류 14 (기준과 같음. 원자료 `validation/f6-avail-15/_raw` 부재) |
| pytest | 15 실패(=1+14), 1072 통과. 같은 집합 |
| `npm run check` | 통과 |
| `npm run test:node` | 10건 통과 |
| 통합 브랜치 merge | `git merge HANSOLJJ/revision_checker` 충돌 없음(`d7e2ebd`). merge 뒤 위 테스트 재실행, 결과 동일 |

## 판단과 지시서 대조

- 지시서는 `review-parts/<영역>.md` 의 frontmatter 에 `reviewer_agent`·`session`·`reviewed_at` 을 두라고 했다. 그러나 코드(`stages._part_field`)는 본문 첫머리의 `검토자:`·`결과:` 줄을 읽는다. 그래서 스킬에 frontmatter 를 두되 그 줄도 그대로 두라고 적었다. 코드는 바꾸지 않았다.
- `stock-` 검색 0건을 위해 명령 문서의 "stock-report-harness 의" 를 "이 저장소의" 로 바꿨고, generator 메타 표기는 `stock-report-harness scorecard-builder` 전문 대신 "`scorecard-builder` 표식"으로 적었다. 실제 메타 값은 코드 그대로다.
- `score-collect` 는 사용자가 확정할 ID 를 지정해 지시했을 때만 에이전트가 `confirm` 을 쓰도록 적었다. 훅은 `confirm` 을 막지 않지만 확정은 사람 몫이라는 지시서 흐름을 따랐다.
- `score-extend` 에는 `--rule` 을 넣지 않았다. 기업 추가 실행이 규칙을 바꾸면 `diff` 가 실패하고, 코드는 `--from-run` 에서 이전 규칙을 이어받는다.
- 커밋 사이에 통합 브랜치 merge 커밋(`d7e2ebd`)이 들어갔다. 지시서 "커밋 2개"는 내용 커밋 기준이다. 커밋 메시지에 공동 작성자 trailer 를 넣지 않았다.

## 소유 밖에서 발견한 문제

- `scripts/hooks/README.md` 의 "아직 하지 않은 것" 은 그대로 유효하다. 문서에서 인용만 했다.
- README 의 "지금 상태 (2026-09-21)" 표(테스트 797건, 규칙 v1.7, 재승인 대기)와 "다음에 정할 것" 목록은 날짜가 지난 기록이다. 지시서 범위 밖이라 고치지 않았다.
- README 브랜치 표의 `reviews/_parts/` 는 옛 폴더 이름이다. 다른 브랜치의 기록을 가리키는 문장이라 두었다.
- `hooks` 의 `_PROTECTED_FILES` 에 v1.8 이 없다는 점(첫 승인 뒤 추가)은 `scripts/hooks/README.md` 에 이미 적혀 있다.

## 남긴 것

- 승인 서버·코드 입력을 실제로 띄우는 종단 검증은 하지 않았다(에이전트 금지 범위).
- 최종 커밋 SHA 는 worker_done 본문에 적는다(보고서가 자기 SHA 를 담을 수 없다). 커밋 1 은 `20bf915`.
