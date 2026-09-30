# 가드레일 훅 (scripts/hooks/guard.py)

훅 판단 논리는 전부 `guard.py` 한 모듈에 있다. 훅 하나가 함수 하나이고, 배선은 `uv run` 한 줄이다. 예전에는 `.claude/hooks/*.sh` 9개가 bash 껍데기로 Python 을 감쌌으나, Windows 에서 WSL bash 오인·CRLF·로그인 셸 작업 디렉터리·cp949 출력 깨짐이 모두 껍데기에서 났으므로 껍데기를 없앴다.

## 훅 목록

| 이름 | 이벤트 | 하는 일 | 결과 |
|---|---|---|---|
| `block_dangerous_bash` | PreToolUse 셸 | `rm -rf /`, `sudo`, 원격 스크립트 파이프 실행, 강제 push 차단 | block |
| `protect_sensitive_files` | PreToolUse 셸·파일 | 보호 경로(아래 절) 수정 차단, 승인·취소 명령 차단 | block |
| `enforce_plan` | PreToolUse 셸·파일 | `output/<slug>/` 단계 순서 강제, `report.html`·`audit.md` 직접 쓰기 차단, 빌드 명령은 리뷰 pass 필요, 다른 소유자의 실행 잠금이 있는 묶음 쓰기 차단 | block |
| `forbid_financial_advice` | Pre·PostToolUse | `output/*/draft.md`, `**/judgments.json`, `**/evidence/*.json` 의 투자 권유·수익 보장 표현 차단 | block |
| `remind_review` | PostToolUse 파일, Stop | 리뷰 입력이 바뀌었거나 리뷰 해시가 현재 산출물과 다르면 경고 | warn |
| `enforce_memory` | PostToolUse 파일 | `memory/_daily/`·`memory/topics/` 변경 뒤 `scripts/validate_memory.py` 실행, 실패하면 차단 | block |
| `inject_memory_context` | UserPromptSubmit | 프롬프트에 맞는 `memory/topics/*.md` 를 문맥으로 주입 | context |

`enforce-citations` 는 종목 리포트 전용이라 만들지 않았고 배선에서도 뺐다.

## 보호 경로와 승인 명령 (`protect_sensitive_files`)

파일 도구 경로는 아래에 해당하면 막는다. 셸 명령은 같은 경로를 언급하면서 파일을 바꾸는 것처럼 보일 때(변경 명령·리다이렉션)만 막는다. 셸 명령의 `\` 는 `/` 로 바꿔 대조한다.

- `.env*`, `.git/`, `.github/workflows/`, `docs/finance-style-guide.md`
- 어느 폴더에 있든 `approval.json` (2026-09-30 레인 F)
- 승인된 실행이 쓰는 규칙 `scorecard/rules/v1.5.json`, `v1.6.json`, `v1.7.json`. **v1.8 은 아직 승인된 실행이 없어 넣지 않았다. 첫 실행이 v1.8 로 승인되면 `_PROTECTED_FILES` 에 더한다.**
- 이동한 기존 실행 두 폴더 `output/ai-scorecard-2026-09-baseline/`, `output/ai-scorecard-2026-09-obsreg/`
- `scorecard/history.csv`

셸 명령에 `scorecard_cli.py approve`, `scorecard_cli.py revoke`, `stages.approve`, `stages.revoke` 가 있으면 변경 기호와 무관하게 막는다. 승인·취소는 사람이 `node server.js --approvals` 승인 페이지에서 한다. `confirm` 은 막지 않는다. 근거 확정은 승인이 아니고, 확정하면 해시가 바뀌어 사람이 다시 승인해야 하기 때문이다. 훅은 둘째 방어선이고, 첫째는 CLI 가 에이전트 세션의 `approve`·`revoke` 를 거부하는 것이다(`scorecard.stages.agent_session_markers`).

## 실행 잠금 (`enforce_plan`)

`output/<slug>/.lock`(gitignore)에 `{owner, started_utc, stage}` 가 있고 그 소유자가 훅 프로세스의 소유자와 다르면 그 묶음에 대한 Write/Edit 를 막는다. 잠금 파일이 없으면 통과하고, 읽을 수 없는 잠금은 소유자를 모르는 잠금으로 보아 막는다. 소유자는 `SCORECARD_AGENT`, 없으면 `ORCA_TERMINAL_HANDLE`, 없으면 OS 사용자명이다(`guard.lock_owner` 와 `scorecard.stages.lock_owner` 가 같은 규칙). 잠금은 CLI 의 `init`·`collect`·`research`·`calculate`·`draft`·`review-template` 과 에이전트 세션의 `confirm` 이 쓰고, 인수는 그 단계들의 `--take-lock` 이다.

## 단계 순서 (`enforce_plan`)

`output/<slug>/` 의 slug 는 폴더 이름이다.

- `plan.md` 는 자유. `research.md` 는 `plan.md` 가 있어야 한다. `draft.md` 는 `plan.md`·`research.md`, `review.md` 는 여기에 `draft.md` 까지 있어야 한다.
- `report.html`, `audit.md` 는 Write/Edit 로 쓸 수 없다. 빌드 명령으로만 만든다.
- 빌드 명령(Bash·PowerShell)은 `output/<slug>/review.md` frontmatter 가 `status: pass`, `review_type: separate-session-4way`, `review_execution: separate_subagent_sessions` 일 때만 통과한다.
- `review-parts/**`, `*.json`, `evidence/**`, `triggers.json`, `preview.md` 에는 게이트가 없다. 옛 경로(`plan/`, `research/`, `drafts/`, `reviews/`, `output/<slug>.html`)도 게이트 대상이 아니다.

## 출력 규약

`main` 이 이벤트에 맞춰 출력하고 exit code 를 정한다. 이벤트 이름은 페이로드의 `hook_event_name` 이고, 없으면 `tool_name` 유무로 추정한다.

| 결정 | 출력 | exit |
|---|---|---|
| allow | 없음 | 0 |
| block | stdout `{"decision": "block", "reason": "…"}` 과 같은 이유를 stderr 에도 | 2 |
| warn (PostToolUse) | `{"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": "…"}}` | 0 |
| warn (Stop) | `{"systemMessage": "…"}` | 0 |
| context (UserPromptSubmit) | `{"hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": "…"}}` | 0 |

`remind_review` 는 예전에 Stop 을 차단했으나 경고로 바꿨다. 조율자와 워커 구조에서 워커의 턴 종료를 잘못 막았기 때문이다.

## 실패는 열어 둔다 (fail-open)

- 훅 함수가 예외를 던지면 stderr 에 한 줄 남기고 exit 0 이다.
- 저장소 루트는 cwd 기준 `git rev-parse --show-toplevel` 로 찾는다. 실패하거나 그 루트에 `scripts/hooks/guard.py` 가 없으면 조용히 exit 0 이다. 무관한 폴더에서 불려도 무해하다.
- 모르는 훅 이름과 모르는 도구 이름도 통과한다.

훅 인프라 오류로 모든 도구가 막히는 일을 없애려는 선택이다. 첫 방어선은 승인·해시 검증 코드(`scorecard_cli.py`, 빌더)이고 훅은 둘째 방어선이다. 훅이 통과시켰다고 검증이 끝난 것이 아니다.

## 도구 이름 별칭

`guard.py` 의 `SHELL_TOOLS`(`Bash`, `PowerShell`)와 `FILE_TOOLS`(`Write`, `Edit`, `MultiEdit`, `NotebookEdit`)가 표다. 다른 에이전트의 도구 이름은 이 상수에 채운다.

## 배선

- Claude Code: `.claude/settings.json`. 명령은 `uv run --frozen --directory "${CLAUDE_PROJECT_DIR:-.}" python -X utf8 scripts/hooks/guard.py <훅이름>` 이다. 매처는 셸 계열 `Bash|PowerShell`, 파일 계열 `Write|Edit|MultiEdit` 이다.
- Codex: `.codex/hooks.json`. 명령은 `uv run --frozen python -X utf8 scripts/hooks/guard.py <훅이름>` 이다. Codex 는 Windows 에서 bash 를 거치지 않으므로 셸 변수 확장을 쓰지 않는다. **훅 프로세스의 cwd 가 세션 루트라고 가정한다.** 그 가정이 깨지면 `uv` 가 프로젝트를 못 찾거나 `find_root` 가 None 을 돌려주어 훅이 조용히 통과한다. 훅 파일이 바뀌면 Codex 가 신뢰 해시(`~/.codex/config.toml [hooks.state]`)를 다시 묻는다.
- timeout 은 15초다. 첫 `uv run` 이 `.venv` 를 만들 수 있다.

## 테스트

`uv run --frozen python -X utf8 -m unittest tests.test_hooks`. 훅 함수를 dict 로 직접 부르므로 bash 가 필요 없다. 배선 스모크 두 건만 `bash` 와 `uv` 가 있을 때 실행한다.

## 아직 하지 않은 것

- Antigravity·Muse 배선은 확인 세 건(차단 표현, 페이로드 필드 이름, 훅 프로세스의 작업 디렉터리)이 끝난 뒤 별도 과제로 한다.
- `protect_sensitive_files` 의 셸 변경 감지 정규식은 bash 명령 기준이다. PowerShell 의 `Set-Content`, `Remove-Item` 같은 cmdlet 은 아직 변경 명령으로 보지 않는다(리다이렉션 `>` 는 잡는다).
