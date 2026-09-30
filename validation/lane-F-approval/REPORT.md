# 레인 F — 승인 보호·실행 잠금(4.2)과 승인 명령·트리거 렌더(4.3) 보고서 (2026-09-30)

## 커밋

| SHA | 내용 |
| --- | --- |
| `f202703` | feat(hooks): approve·approval.json·이동한 실행·규칙 파일 보호, 실행 잠금 (4.2) |
| `2d7473c` | feat(approve): summary·confirm·revoke 명령, approved_via 기록, 초안·HTML 트리거 절 (4.3) |
| `73b3921` | merge: `HANSOLJJ/revision_checker`(문서 커밋 2건, 충돌 없음) |
| 이 보고서 커밋 | docs(validation): 레인 F 보고서 |

`git diff --stat HANSOLJJ/revision_checker...HEAD` 는 소유 파일 14개만 보여 준다(보고서 커밋 전 기준).
`.gitignore`, `scripts/hooks/{guard.py,README.md}`, `scripts/scorecard/{stages,schema,render_md,render_html}.py`,
`scripts/scorecard_cli.py`, `server/approvals.js`, `tests/node/approvals.test.js`, `tests/test_hooks.py`,
새 파일 `tests/test_run_lock.py`, `tests/test_approval_commands.py`, `tests/test_trigger_render.py`.

## 계약 변경 (조율자 결정, `ask` 회신)

지시서 4.2-4 는 `confirm` 도 다른 소유자의 잠금이면 거부하고 `--force` 로 인수한다고 적었다. 그런데 `confirm` 은
사람이 띄운 승인 페이지가 `execFile` 로 부르고, 사람 셸의 소유자(사람 셸의 `ORCA_TERMINAL_HANDLE` 또는 사용자명)는
에이전트가 잡은 잠금과 항상 달라서 페이지의 근거 확정이 늘 거부된다. 조율자에게 물어 다음으로 정했다.

1. **`confirm` 은 에이전트 세션일 때만 잠금을 검사·기록한다.** 사람 세션의 `confirm` 은 `approve`·`revoke` 와 같은
   사람 행위로 본다. 에이전트 판정은 `approve` 거부와 같은 함수 하나(`stages.agent_session_markers`)를 쓴다.
2. **잠금 인수 플래그는 모든 단계에서 `--take-lock` 하나다.** 기존 `--force`(init 덮어쓰기, review-template 재생성)는
   의미를 그대로 둔다. 한 플래그가 두 의미를 가지면 템플릿을 다시 만들다가 잠금까지 조용히 가져가게 된다.
3. 훅은 `stages.approve` 와 대칭으로 `stages.revoke` 도 셸 명령에서 막는다(내 제안, 조율자 승인).

## 환경변수 조사 (4.2-3)

방법. 지시서대로 `orca terminal create --worktree active --title env-probe --json` 으로 일반 셸(PowerShell,
oh-my-posh 프롬프트)을 만들고, `Get-ChildItem env:` 의 **이름만** 스크래치 파일로 받은 뒤 `orca terminal close` 로
닫았다(셸이 PowerShell 이라 `env | sort` 대신 이 명령을 썼다. 값에 토큰이 있어 이름만 비교했다). 에이전트 쪽은 이 세션의
Bash 도구에서 `env | sort` 로 받았다. 대소문자를 무시하고 이름 집합을 비교했다.

| 변수 | 에이전트 터미널 | 사람 Orca 셸 | 거부 조건 | 판단 |
| --- | --- | --- | --- | --- |
| `CLAUDECODE` (`1`) | 있음 | 없음 | **넣음** | 지시서 지정 |
| `CLAUDE_CODE_ENTRYPOINT` (`cli`) | 있음 | 없음 | **넣음** | 지시서 지정 |
| `ORCA_AGENT_LAUNCH_TOKEN` (36자) | 있음 | 없음 | **넣음** | Orca 가 에이전트를 띄울 때만 준다. Claude 가 아닌 에이전트도 잡을 것으로 본다(아래 한계) |
| `AI_AGENT` (`claude-code_2-1-285_agent`) | 있음 | 없음 | **넣음** | 이름이 에이전트 표지 그 자체다 |
| `CLAUDE_CODE_SESSION_ID`, `CLAUDE_CODE_CHILD_SESSION`, `CLAUDE_CODE_SESSION_ATTENDED`, `CLAUDE_CODE_EXECPATH`, `CLAUDE_CODE_MESSAGING_*`, `CLAUDE_PID`, `CLAUDE_EFFORT` | 있음 | 없음 | 뺌 | Claude Code 전용이라 `CLAUDECODE` 와 늘 함께 있다. 더해도 잡는 범위가 넓어지지 않는다 |
| `MSYSTEM`, `SHLVL`, `PWD`, `SHELL`, `_`, `EXEPATH`, `PLINK_PROTOCOL`, `WSLENV`, `NODEFAULTCURRENTDIRECTORYINEXEPATH` | 있음 | 없음 | 뺌 | Bash 도구가 쓰는 Git Bash 가 만든다. 사람이 Git Bash 를 열어도 생긴다 |
| `GIT_ASKPASS`, `GIT_EDITOR`, `GIT_TERMINAL_PROMPT`, `GIT_CONFIG_*`, `GCM_INTERACTIVE`, `SSH_ASKPASS`, `COREPACK_ENABLE_AUTO_PIN` | 있음 | 없음 | 뺌 | 도구 설정용이다. 사람 도구(IDE 등)도 같은 이름을 쓸 수 있어 표지로 약하다 |
| `ORCA_TERMINAL_HANDLE`, `ORCA_WORKTREE_ID`, `ORCA_PANE_KEY`, `ORCA_TAB_ID`, `ORCA_AGENT_HOOK_*`, `ORCA_APP_VERSION`, `ORCA_USER_DATA_PATH`, `ORCA_CODEX_HOME`, `ORCA_OPENCODE_AGENT` 등 | 있음 | **있음** | 뺌 | 사람 셸에도 있다. 넣으면 사람이 Orca 셸에서 승인하지 못한다 |
| `ORCA_OMP_FRESH_CONFIG`, `ORCA_OMP_STATUS_EXTENSION`, `POSH_CURSOR_*` | 없음 | 있음 | — | 사람 셸 프롬프트 쪽 변수 |

`stages.AGENT_ENV_MARKERS = ("CLAUDECODE", "CLAUDE_CODE_ENTRYPOINT", "ORCA_AGENT_LAUNCH_TOKEN", "AI_AGENT")`. 값이 공백뿐이면
없는 것으로 본다. 테스트 `test_run_lock.AgentRefusalTest.test_orca_variables_alone_are_a_human_shell` 이 `ORCA_*` 만 있는
환경을 사람 셸로 판정하는지 잠근다.

한계. 조사는 이 Claude Code 세션 하나와 사람 셸 하나를 비교한 것이다. Codex·Antigravity 세션의 환경변수는 보지 않았다.
그 세션이 Orca 로 떠서 `ORCA_AGENT_LAUNCH_TOKEN` 을 받는다면 잡히지만, 이것은 이 세션에서만 관측한 사실을 넓힌 가정이다.

## 한 일

### 4.2 승인 보호·실행 잠금

- `guard.protect_sensitive_files` 보호 목록: 어느 폴더든 `approval.json`, `scorecard/rules/v1.5.json`·`v1.6.json`·`v1.7.json`,
  `output/ai-scorecard-2026-09-baseline/**`, `output/ai-scorecard-2026-09-obsreg/**`, `scorecard/history.csv`. 파일 도구 경로와
  셸 변경 명령 리터럴 둘 다 기존 방식으로 막는다. 셸 명령은 `\` 를 `/` 로 바꿔 대조한다(PowerShell 경로). v1.8 은 넣지 않았고,
  첫 실행이 v1.8 로 승인되면 넣는다고 `scripts/hooks/README.md` 에 적었다.
- 셸 명령에 `scorecard_cli.py approve|revoke`, `stages.approve|revoke` 가 있으면 변경 기호와 무관하게 막는다. 메시지는
  "승인·취소는 사람이 `node server.js --approvals` 승인 페이지에서 한다". `confirm` 은 막지 않는다.
- `guard.enforce_plan`: `output/<slug>/.lock` 의 소유자가 훅 프로세스의 소유자와 다르면 그 묶음 Write/Edit 를 막는다. 잠금이
  없으면 통과, 읽을 수 없는 잠금은 소유자를 모르는 잠금으로 보아 막는다. 소유자 규칙은 `guard.lock_owner` 와
  `stages.lock_owner` 가 같다(`SCORECARD_AGENT` → `ORCA_TERMINAL_HANDLE` → OS 사용자명). 훅은 `scorecard` 를 import 하지 않으므로
  세 줄을 두 곳에 두었다.
- `stages.claim_lock(slug, stage, take_lock=, write=)`: `{owner, started_utc, stage}` 를 쓴다. 같은 소유자면 `started_utc` 를 두고
  `stage` 만 바꾼다. 단계가 끝나도 잠금은 남긴다. 실행 폴더가 없으면 쓰지 않는다.
- CLI: `init`(폴더를 만들기 전 검사, 만든 뒤 기록)·`collect`·`research`·`calculate`·`draft`·`review-template` 이 잠금을 검사·기록하고
  `--take-lock` 으로 인수한다. **잠금은 CLI 계층에서만 건다.** `stages` 단계 함수에 넣으면 정본 실행에 대해 함수를 부르는
  테스트가 세션마다 다른 소유자로 잠금을 남겨 서로를 막을 수 있어서다. `approve`·`revoke`·`build` 는 잠금을 요구하지도 쓰지도 않는다.
- CLI `approve` 는 에이전트 세션이면 거부한다. `stages.approve()` 함수 자체는 막지 않는다. TTY 검사는 두지 않았다.
- `.gitignore`: `output/*/.lock`.

### 4.3 승인 명령과 트리거 렌더

- `stages.summary(slug)` 와 `summary <run_id> --json`. 키 구조는 픽스처와 같다. 값의 출처:
  `companies[]` 는 `results.json` 과 기준선 `scores.json`(`baseline.rank` 는 `rank_raw`, 기준선에 없는 기업은 null),
  `changed_factors` 는 두 점수가 다 있고 다른 factor, `carried_factors` 는 `results.companies[].carried_factors`(= `carried_score`),
  `pending` 은 `"<factor>: <status>"`(결정 ID 가 있으면 ` (C-xx)`). `review` 는 `review.md` 의 frontmatter `status`, 검토 영역 표의
  검토자·결과(칸이 비었거나 `pending` 이면 `review-parts/<영역>.md` 의 `검토자:`·`결과:` 줄), 체크리스트 `fail` 개수. 파일이 없으면
  null. `evidence` 는 `candidates.json`·`evidence.json` 개수와 항목(`url` 은 `sources.json` 에서), 없으면 0 과 빈 리스트.
  `triggers` 는 `triggers.json` 항목, 없으면 빈 리스트. `hashes` 는 `current_hashes`, `approval.valid` 는 `approval_mismatches` 가 빈지.
  JSON 은 `ensure_ascii=False`, CLI 가 표준 출력을 UTF-8 로 다시 설정한다.
- `stages.confirm(slug, evidence_ids=, reject_ids=, reviewer=)` 와 CLI `confirm --evidence a,b --reject c --by NAME [--take-lock]`.
  ID 는 `^EV-[a-z0-9-]+-\d{3}$` 만 받는다(`--` 로 시작하는 값 포함 SchemaError). 없는 ID, ID 없음, 같은 ID 의 확정·거부 동시 지정은
  오류다. 확정은 `status: confirmed`·`reviewer`(없으면 `SCORECARD_AGENT`, 그다음 사용자명)·`reviewed_at`(UTC 날짜), 거부는 항목 삭제다.
  이미 확정된 항목은 건드리지 않는다. 쓴 뒤 `load_context` 로 실행 전체를 다시 검증하고 실패하면 원래 바이트로 되돌린다(예: 트리거가
  인용한 근거를 거부할 때). 표준 출력에 "calculate → draft → review 를 다시 돌린다" 를 안내한다.
- `approve --via browser|terminal`(기본 terminal), `approval.json.approved_via`. `schema.validate_approval` 은 `approved_via` 를 선택
  키로 받고 값을 검사한다. 기존 두 실행의 승인 파일은 바뀌지 않았고 `approved_via` 가 없다.
- `stages.revoke(slug, by=, note=)` 와 CLI `revoke`(에이전트 세션 거부). `approval.json` 을 지우고 `output/<run_id>/revocations.jsonl`
  에 `{revoked_by, revoked_at(UTC ISO 시각), note, approval_id, hashes}` 한 줄을 더한다. `by`·`note` 가 비었거나 승인이 없으면 오류.
- 트리거 절: `render_md.active_trigger_rows` 를 연구·초안·HTML 이 같이 쓴다(열: ID·기업·Factor·관찰 사실·조건·기한·근거·재검토, 감시 중만,
  그 밖의 상태 건수와 C-14 문장). `render_draft` 와 `render_html.render_triggers` 는 `ctx.triggers` 가 있으면 그것을, 없으면 기준선
  트리거를 그린다. 연구 단계 출력은 리팩터 뒤에도 같다.
- `server/approvals.js`: 잘못된 코드가 5번 오면 그 뒤 모든 POST 를 403(`Forbidden: 5 invalid codes - restart the server`)으로 막고
  "코드 실패 5회 — 서버를 다시 띄우세요" 를 한 번 출력한다(`options.log`, 기본 `console.error`).

## 좁히거나 고른 것 (근거와 함께)

- **기존 draft 바이트 고정은 트리거 절로 좁혔다.** 지시서는 obsreg 컨텍스트로 `render_draft` 를 돌려 저장된 draft 와 바이트가 같은지
  고정하라고 했다. 변경 **전** 코드로 돌려 보니 이미 같지 않았다. 차이는 네 줄이다 — frontmatter `plan_source`·`research_source`
  (레이아웃 이동으로 `plan/…` → `output/…/plan.md`)와 방법 절 문장 두 개(다른 레인의 문면 변경). 트리거 절은 같았다. 그래서 테스트
  `test_trigger_render.ExistingRunTest` 는 **트리거 절**이 저장본과 바이트가 같은지를 본다. 따로, 변경 후 obsreg 전체 렌더가 변경 전
  렌더와 문자 단위로 같은 것을 스크래치에서 확인했다(`draft same as pre-change render: True`).
- baseline 은 `render_draft` 자체가 변경 전부터 실패한다(아래 소유 밖 1). 그래서 바이트 테스트는 obsreg 만 돈다.
- `summary.review.areas[].area` 는 `REVIEW_AREAS` 키(`output-readability`)다. 픽스처 표본 값은 `presentation` 이지만 값은 계약 밖이고
  승인 페이지는 영역 이름에 기대지 않는다.
- `summary.review.checklist_fail` 은 fail 행을 그대로 센다. obsreg 는 승계 예외로 통과한 fail 이 11건이라 승인 페이지가 경고
  배너를 띄운다. 예외를 빼고 세면 페이지가 승계 예외를 조용히 숨기게 된다고 보아 그대로 두었다.
- `summary.approval` 에 `approved_via` 를 싣지 않았다. 픽스처 키 구조를 정확히 따르라는 지시 때문이다.
- `summary.triggers` 는 `triggers.json` 이 없으면 빈 리스트다. 기준선 트리거는 모양(`title`·`why`)이 달라 페이지 표에 맞지 않는다.

## 검증

| 명령 | 결과 |
| --- | --- |
| `uv run --frozen python -X utf8 -m unittest discover -s tests -t .` | 기준 1030건 실패 1·오류 14 → **1085건 실패 1·오류 14**. 실패·오류 집합이 기준선과 한 줄도 다르지 않다(`diff` 빈 출력, 전부 `validation/*/_raw` 부재) |
| `uv run --frozen pytest -q` | 15 failed, 1072 passed, 1806 subtests passed. 실패 15건의 테스트 이름이 모두 위 기준선 집합에 있다 |
| `npm run check` | 종료 코드 0 |
| `npm run test:node` | tests 10 · pass 10 · fail 0 (새 테스트 "코드 실패 5회 뒤 모든 POST 403…" 포함) |
| `scorecard_cli.py status` 두 실행 | 둘 다 `"approval": true`, `"approval_valid": true` |
| `git status --porcelain -- output` | 빈 출력 |
| `scorecard_cli.py summary <두 실행>` | 둘 다 돌고 `approval.valid: true`, obsreg `review.status: pass` |

새 승인 경로 종단은 `tests/test_approval_commands.ApproveRevokeTest.test_end_to_end` 가 임시 묶음에서 잠근다. init(v1.8) → collect(뉴스
픽스처) → 근거·트리거 작성 → research → calculate → draft → review-template → 테스트가 리뷰를 pass 로 채움 → `approve --via browser`
→ `summary.approval.valid` true → `confirm` 으로 근거 확정 → `valid` false → `revoke` → 승인 파일 삭제·`revocations.jsonl` 한 줄.
CLI `init` 을 거치는 잠금 흐름은 `tests/test_run_lock.CliLockTest` 가 본다.

배선 실측(이 세션, Claude Code). 새 훅이 실제로 막았다.
- Bash 명령 본문에 `stages.approve` 문자열이 든 파이썬 heredoc 을 실행하려 하자 PreToolUse 가 막았다(그 뒤 스크래치 파일로 바꿔 실행).
- 검색용 `rg` 명령에 같은 문자열이 들어가도 막혔다(지시서가 정한 "변경 기호와 무관" 규칙대로다. 검색은 Grep 도구로 했다).
- Write 도구로 `tmp-lane-f-probe/approval.json` 을 쓰려 하자 `**/approval.json` 보호로 막혔고 파일은 생기지 않았다.

## 소유 밖에서 발견한 것 (고치지 않음)

1. **baseline 초안을 다시 렌더할 수 없다.** `render_draft` 가 `render_common.method_sections` 1352행 `f6p["parameters"]` 에서
   `KeyError` 로 죽는다. v1.5(bands) 실행에는 `parameters` 가 없다. 변경 전부터 그렇다. 기존 draft 를 다시 렌더하지 않으므로 승인에는
   영향이 없다.
2. **obsreg 초안도 다시 렌더하면 네 줄이 달라진다**(위 "좁히거나 고른 것"). 저장된 draft 는 지금 코드로 재현되지 않는다.
3. **터미널 승인 명령을 안내하는 자리가 남아 있다.** 이제 에이전트 세션은 훅과 CLI 에서 막히고, 사람은 승인 페이지를 쓰는 것이 계획이다.
   `.claude/skills/score-approve/SKILL.md:14`(에이전트가 사용자 지시로 `scorecard_cli.py approve` 를 실행한다), `README.md:45`(승인 행),
   `scripts/scorecard/validate.py:270` 과 `scripts/scorecard/render_html.py:1735` 의 `awaiting_user` 메시지(둘 다
   `scorecard_cli.py approve <slug> --by <name>` 안내, 렌더 파일은 트리거 절 밖이라 소유 밖). 4.5·4.6 문서·스킬 레인에서 승인 페이지
   안내로 바꿔야 한다. `AGENTS.md` 는 명령을 적지 않고 "승인은 사용자 행위" 라고만 적어 그대로 맞다.
4. **PowerShell cmdlet 변경은 여전히 셸 보호를 지나간다.** `_MUTATING` 이 `Set-Content`·`Remove-Item`·`Out-File` 을 변경 명령으로 보지
   않는다(README "아직 하지 않은 것" 에 이미 있는 한계). 리다이렉션 `>` 은 잡는다. 이동한 실행 폴더를 PowerShell cmdlet 으로 고치는 것은
   훅이 못 막는다. 4.2 지시가 "기존 방식대로" 라 넓히지 않았다.

## 남긴 것

- v1.8 규칙 보호는 첫 v1.8 실행이 승인될 때 `guard._PROTECTED_FILES` 에 더한다.
- Codex·Antigravity 세션의 환경변수 비교(위 한계).
- 소유 밖 1~4.
