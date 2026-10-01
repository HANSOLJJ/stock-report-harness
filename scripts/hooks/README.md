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

파일 도구 경로는 아래에 해당하면 막는다.

- `.env*`, `.git/`, `.github/workflows/`, `docs/finance-style-guide.md`
- 어느 폴더에 있든 `approval.json` (2026-09-30 레인 F)
- 승인된 실행이 쓰는 규칙 `scorecard/rules/v1.5.json`, `v1.6.json`, `v1.7.json`. **v1.8 은 아직 승인된 실행이 없어 넣지 않았다. 첫 실행이 v1.8 로 승인되면 `_PROTECTED_FILES` 에 더한다.**
- 이동한 기존 실행 두 폴더 `output/ai-scorecard-2026-09-baseline/`, `output/ai-scorecard-2026-09-obsreg/`
- `scorecard/history.csv`
- `scorecard/baseline/**` (2026-10-01 레인 H). 기준선 트리거는 승인 해시 밖의 재빌드 입력이다. 실행 묶음에 `triggers.json` 이 없으면 렌더러가 기준선 트리거를 그리므로, 바꾸면 승인이 유효한 채 재빌드 리포트가 바뀐다.

보호 경로 대조는 대소문자를 가리지 않는다(2026-10-01 레인 N, V2-3). Windows 파일 시스템은 `Approval.json`·`approval.JSON`·`.ENV` 를 `approval.json`·`.env` 와 같은 파일로 열기 때문이다. 파일 도구 경로, 셸 명령의 쓰기 대상, 글롭, 승인 파일을 품은 상위 폴더 판정이 모두 같다. 읽는 쪽도 맞춘다. `scorecard.schema.load_json_strict` 는 폴더 목록에 이름이 정확히 `approval.json` 인 항목이 있을 때만 승인 파일을 읽고, `validate_approval` 은 `approval_id` 를 실행·결과·초안 해시로 다시 계산해 대조한다. 대소문자만 바꾼 파일이나 손으로 쓴 임의 `approval_id` 는 승인으로 읽히지 않는다.

셸 명령은 같은 경로가 **쓰기 대상** 일 때만 막는다(2026-10-01 레인 H). 명령을 따옴표를 지켜 토큰으로 나누고(`shlex`) `;`·`&&`·`||`·`|`·`&`·괄호·줄바꿈마다 끊어 명령 하나씩 본다. `\` 는 `/` 로 바꿔 대조한다.

| 명령 | 판정 |
|---|---|
| 리다이렉션 `>`·`>>` 의 대상 | 보호 경로면 막는다 |
| 변경 동사 `rm`·`mv`·`tee`·`touch`·`truncate`·`chmod`·`chown`, `sed -i`, `perl -pi`, `git checkout`·`git restore`·`git reset` 의 인자 | 보호 경로면 막는다 |
| PowerShell `Set-Content`·`Add-Content`·`Out-File`·`Remove-Item`·`Move-Item`·`Copy-Item`·`New-Item`·`Rename-Item`·`Clear-Content` 와 기본 별칭(`sc`·`ac`·`ri`·`del`·`erase`·`rd`·`mi`·`move`·`cpi`·`copy`·`ni`·`rni`·`ren`·`clc`)의 경로 인자(`-Path x`, `-Path:x`, 위치 인자) | 보호 경로면 막는다(2026-10-01 레인 J) |
| 복사 `cp`·`install`·`Copy-Item` | **목적지**(`-Destination`·`-t`·마지막 위치 인자)만 쓰기 대상이다. 보호 경로에서 복사해 나오는 것은 읽기라 통과한다(레인 J) |
| 지우기 `rm`·`rmdir`·`Remove-Item` 계열, 옮기기 `mv`·`Move-Item`·`Rename-Item` 계열의 원본 | 보호 경로를 품은 상위 폴더(`rm -rf output`, `rm -rf .`, 승인 파일이 든 실행 폴더)도 막는다(레인 J) |
| `find … -delete`, `find … -exec <변경 동사>` | 시작 경로가 보호 경로이거나 보호 경로를 품으면 막는다. 경로 없는 `find . …` 는 저장소 전체라 막는다(레인 J) |
| `… \| xargs <변경 동사>` | 대상이 앞 명령의 출력이라 알 수 없다. 명령 전체에 보호 경로가 나오거나, 같은 명령의 다른 명령이 받은 경로(find·ls·git ls-files 등)가 보호 경로를 품으면 막는다(레인 J) |
| 글롭(`*`·`?`·`[`)이 든 쓰기 대상 | 보호 경로(아직 없는 파일 포함)와 맞거나 파일 시스템에서 전개한 결과가 보호 경로면 막는다. `*` 는 `/` 를 넘지 않는다(`rm *.md` 는 `docs/` 아래와 맞지 않는다)(레인 J) |
| 인터프리터 `python`·`python3`·`py`·`node`, `uv run …`, `uvx` | 보호 경로 문자열을 담기만 해도 막는다. 스크립트 안의 쓰기를 셸에서 가릴 수 없다 |
| 읽기 명령 `cat`·`rg`·`grep`·`ls`·`head`·`git show`·`git diff`·`Get-Content`·`Select-String` 등 | 경로를 언급해도 통과한다 |

- 앞에 붙은 `VAR=값`, `env`(옵션·`-u NAME` 포함), `command`·`exec`·`nohup`·`time` 은 건너뛰고 그 뒤의 동사를 본다.
- `cd`·`pushd`·`Set-Location` 뒤의 상대 경로는 바뀐 폴더 기준으로 푼다(`cd output/<보호 실행> && rm draft.md` 도 막는다). `git -C <폴더>` 도 같다.
- 따옴표가 맞지 않아 나눌 수 없는 명령은 쓰기 대상을 가릴 수 없으므로 보호 경로를 언급하기만 해도 막는다.

셸 명령에 `scorecard_cli.py approve`, `scorecard_cli.py revoke`, `stages.approve`, `stages.revoke` 가 있으면 변경 기호와 무관하게 막는다. 승인·취소는 사람이 `node server.js --approvals` 승인 페이지에서 한다. `confirm` 은 막지 않는다. 근거 확정은 승인이 아니고, 확정하면 해시가 바뀌어 사람이 다시 승인해야 하기 때문이다. 훅은 둘째 방어선이고, 첫째는 `scorecard.stages.approve`·`revoke` **함수 본체** 가 에이전트 세션을 거부하는 것이다(2026-10-01 레인 H). CLI 든 import 든 같은 판정(`scorecard.stages.agent_session_markers`)을 거친다. 테스트만 키워드 인자 `allow_agent_session=True` 로 이 거부를 끈다.

`scorecard_cli.py init <slug> … --force` 는 `output/<slug>/approval.json` 이 있으면 막는다(2026-10-01 레인 H). 덮어쓰면 승인 기록이 지워지기 때문이다. 슬러그가 맨 이름이든 `output/<slug>` 경로든 마지막 경로 조각을 실행 폴더로 보고, argparse 의 줄임(`--fo`)도 `--force` 로 본다. `stages.init_run` 도 같은 경우 에이전트 세션을 거부하고, 사람 세션에서는 CLI 가 승인 기록이 지워졌다고 경고한다.

## 실행 잠금 (`enforce_plan`)

`output/<slug>/.lock`(gitignore)에 `{owner, started_utc, stage}` 가 있고 그 소유자가 훅 프로세스의 소유자와 다르면 그 묶음에 대한 Write/Edit 를 막는다. 잠금 파일이 없으면 통과하고, 읽을 수 없는 잠금은 소유자를 모르는 잠금으로 보아 막는다. 소유자는 `SCORECARD_AGENT`, 없으면 `ORCA_TERMINAL_HANDLE`, 없으면 OS 사용자명이다(`guard.lock_owner` 와 `scorecard.stages.lock_owner` 가 같은 규칙). 잠금은 CLI 의 `init`·`collect`·`research`·`calculate`·`draft`·`review-template` 과 에이전트 세션의 `confirm`·`judge`(2026-10-01 레인 J) 가 쓰고, 인수는 그 단계들의 `--take-lock` 이다.

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

훅 인프라 오류로 모든 도구가 막히는 일을 없애려는 선택이다. 첫 방어선은 승인·해시 검증 코드(`scorecard.stages` 의 승인 함수, 빌더)이고 훅은 둘째 방어선이다. 훅이 통과시켰다고 검증이 끝난 것이 아니다.

## 도구 이름 별칭

`guard.py` 의 `SHELL_TOOLS`(`Bash`, `PowerShell`)와 `FILE_TOOLS`(`Write`, `Edit`, `MultiEdit`, `NotebookEdit`)가 표다. 다른 에이전트의 도구 이름은 이 상수에 채운다.

## 배선

- Claude Code: `.claude/settings.json`. 명령은 `uv run --frozen --directory "${CLAUDE_PROJECT_DIR:-.}" python -X utf8 scripts/hooks/guard.py <훅이름>` 이다. 매처는 셸 계열 `Bash|PowerShell`, 파일 계열 `Write|Edit|MultiEdit` 이다.
- Codex: `.codex/hooks.json`. 명령은 `uv run --frozen python -X utf8 scripts/hooks/guard.py <훅이름>` 이다. Codex 는 Windows 에서 bash 를 거치지 않으므로 셸 변수 확장을 쓰지 않는다. **훅 프로세스의 cwd 가 세션 루트라고 가정한다.** 그 가정이 깨지면 `uv` 가 프로젝트를 못 찾거나 `find_root` 가 None 을 돌려주어 훅이 조용히 통과한다. 훅 파일이 바뀌면 Codex 가 신뢰 해시(`~/.codex/config.toml [hooks.state]`)를 다시 묻는다.
- timeout 은 15초다. 첫 `uv run` 이 `.venv` 를 만들 수 있다.

## 테스트

`uv run --frozen python -X utf8 -m unittest tests.test_hooks tests.test_lane_v_fixes tests.test_hooks_write_forms`. 훅 함수를 dict 로 직접 부르므로 bash 가 필요 없다. 배선 스모크 두 건만 `bash` 와 `uv` 가 있을 때 실행한다.

## 아직 하지 않은 것

- Antigravity·Muse 배선은 확인 세 건(차단 표현, 페이로드 필드 이름, 훅 프로세스의 작업 디렉터리)이 끝난 뒤 별도 과제로 한다.
- `protect_sensitive_files` 는 셸 문자열만 본다. PowerShell 변수(`$p = 'output/…'; Remove-Item $p`)·`Invoke-Expression`·스크립트 블록처럼 경로가 실행 중에 정해지는 쓰기는 가릴 수 없다. 첫 방어선(승인 해시 검증)과 git 이력 확인이 이 틈을 덮는다.
- `xargs` 판정은 보수적이다. 대상 목록을 파일에서 읽는 `cat list.txt | xargs rm` 은 목록 안의 보호 경로를 볼 수 없어 통과한다.
