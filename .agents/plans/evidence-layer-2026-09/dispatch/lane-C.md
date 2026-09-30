# 레인 C — 훅 통합: bash 훅 9개를 scripts/hooks/guard.py 하나로, 배선을 uv run 한 줄로

에이전트: Claude Sonnet 5.5. 의존: 없음(0단계 완료). 공통 규약: `README.md` 를 먼저 읽는다. 계획 원문: `../plan.md` 4단계 "훅을 Python 한 모듈 + uv run 한 줄로".

## 배경

`.claude/hooks/*.sh` 9개의 판단 논리는 전부 안쪽 `python3 - <<'PY'` 히어독에 있고 bash 는 stdin 을 넘기는 껍데기다. Windows 에서 겪은 문제(WSL bash 오인, CRLF, 로그인 셸 작업 디렉터리, cp949 출력 깨짐)는 전부 껍데기에서 났다. 껍데기를 없애고 논리를 Python 모듈 하나로 옮긴다. **논리는 그대로 이식한다.** 다만 경로는 새 묶음 배치(`output/<slug>/…`)로 바꾸고, 아래 표의 변경 세 가지만 더한다.

## 소유 파일 (Ownership)

- 새 파일: `scripts/hooks/guard.py`, `scripts/hooks/README.md`, `tests/test_hooks.py`
- 수정: `.claude/settings.json`, `.codex/hooks.json`
- 삭제: `.claude/hooks/**`(sh 9개와 `lib/`), `scripts/memory_context.py`(guard 에 흡수)

만지지 않는 것: `scripts/validate_memory.py`(guard 가 subprocess 로 부른다), `scripts/scorecard/**`, `scripts/build_report.py`, `tests/` 의 기존 파일, `.codex/hooks/**`(레인 S 가 지운다), `docs/**`, `AGENTS.md`, `package.json`.

## 새 배치 (레인 A 가 만든다. 훅은 이 경로를 기준으로 짠다)

```
output/<slug>/  run.json observations.json judgments.json sources.json results.json approval.json
                plan.md research.md draft.md preview.md review.md review-parts/**
                evidence/candidates.json evidence/evidence.json triggers.json
                report.html audit.md
```

slug 는 `output/` 바로 아래 폴더명이다. 파일명 stem 이 아니다. 옛 경로(`plan/`, `research/`, `drafts/`, `reviews/`, `output/<slug>.html`)는 더 이상 게이트 대상이 아니다.

## guard.py 설계

- 첫 줄 한국어 주석. 표준 라이브러리만. `main(argv)` 가 `<훅이름>` 하나를 받아 stdin JSON 을 읽고 해당 함수를 부른다.
- 함수 하나가 훅 하나다. 시그니처 `def <name>(payload: dict, *, root: Path) -> Decision`. `Decision` 은 `allow()`, `block(reason)`, `warn(message)`, `context(text)` 네 종류의 작은 데이터클래스다. **테스트는 이 함수를 dict 로 직접 부른다.** stdin 과 exit 처리는 `main` 만 한다. 훅 이름 → 함수 표는 `HOOKS` 모듈 상수.
- 출력 규약. `block` 은 stdout `{"decision": "block", "reason": "…"}` 과 exit 2(현재 sh 의 출력을 확인해 같은 형태를 유지한다). `warn` 은 PostToolUse 에서 exit 0 과 stdout `{"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": "…"}}`, Stop 에서 exit 0 과 `{"systemMessage": "…"}`. `context`(UserPromptSubmit)는 지금처럼 stdout 에 텍스트, exit 0. `allow` 는 출력 없이 exit 0. 이벤트 이름은 페이로드의 `hook_event_name` 으로 안다.
- 저장소 루트는 `git rev-parse --show-toplevel`(cwd 기준)로 찾는다. 실패하거나 그 루트에 `scripts/hooks/guard.py` 가 없으면 조용히 exit 0 이다. 무관한 폴더에서 불려도 무해해야 한다.
- **실패는 열어 둔다(fail-open).** 예기치 않은 예외는 stderr 에 한 줄 적고 exit 0. 훅 인프라 오류로 모든 도구가 막히는 일을 없앤다. 첫 방어선은 승인·해시 검증 코드이고 훅은 둘째다. 이 사실을 README 에 적는다.
- 도구 이름 별칭 표. `Bash`, `PowerShell` → 셸 명령 계열(`tool_input.command`). `Write`, `Edit`, `MultiEdit`, `NotebookEdit` → 파일 계열(`tool_input.file_path` 또는 `notebook_path`). 모르는 이름은 allow. 표는 모듈 상수로 두어 Antigravity·Muse 배선 때 채울 수 있게 한다.
- 공통 유틸(`extract_command`, `extract_paths`, `relpath`, `read_frontmatter`)은 같은 모듈 안에 둔다. `lib/guardrail-common.sh` 의 기능 중 Python 쪽이 쓰던 것만 옮긴다.

| 함수 | 원본 | 이식 규칙 |
|---|---|---|
| `block_dangerous_bash` | block-dangerous-bash.sh | 패턴과 메시지 그대로. PowerShell 명령에도 적용 |
| `protect_sensitive_files` | protect-sensitive-files.sh | 보호 목록에서 `docs/output-spec.md` **제거**(변경 1). 나머지 그대로. `approval.json`·규칙 파일·이동한 실행 폴더 보호는 **이 과제가 아니다.** 4.2 에서 한다. 지금 넣으면 레인 A 의 `git mv` 를 막는다 |
| `enforce_plan` | enforce-plan.sh | 새 배치로 매핑(변경 2). `plan.md` 는 자유. `research.md` 는 같은 폴더의 `plan.md` 필요. `draft.md` 는 `plan.md` 와 `research.md` 필요. `review.md` 는 `draft.md` 필요. `report.html`·`audit.md` 의 직접 Write/Edit 는 차단(빌드 명령으로만 생성). `review-parts/**`, `*.json`, `evidence/**`, `triggers.json`, `preview.md` 는 게이트 없음. Bash·PowerShell 의 빌드 명령은 정규식 `(?:uv\s+run\s+(?:--frozen\s+)?)?python3?(?:\s+-X\s+utf8)?\s+scripts/build_report\.py\s+(\S+)` 로 slug 를 잡고, `output/<slug>/review.md` 의 frontmatter 가 `status: pass`, `review_type: separate-session-4way`, `review_execution: separate_subagent_sessions` 일 때만 허용. 종목 시절의 hero·asset 접미사 표와 `plan_slugs` 추론은 지운다 |
| `forbid_financial_advice` | forbid-financial-advice.sh | 표현 목록 그대로. 대상 경로를 `output/*/draft.md`, `**/judgments.json`, `**/evidence/*.json` 으로 교체(옛 `drafts/*.md` 등은 제거) |
| `remind_review` | remind-review.sh | **차단 → 경고**(변경 3, 사용자 결정. 조율자·워커 구조에서 워커의 턴 종료를 잘못 막는다). PostToolUse: `output/<slug>/{draft.md, judgments.json, observations.json, evidence/*.json}` 이 바뀌면 "리뷰 해시가 무효화됨, `/score-review <slug>` 필요" 경고. Stop: `output/*/review.md` 중 frontmatter `results_hash` 가 같은 폴더 `results.json` 의 `results_hash` 와 다르거나 `draft_hash` 가 `draft.md` 의 sha256 과 다르면 같은 경고. 둘 다 exit 0 |
| `enforce_memory` | enforce-memory.sh | `memory/` 아래 쓰기 뒤 `[sys.executable, "-X", "utf8", "scripts/validate_memory.py"]` 를 subprocess 로 실행하고 실패면 block. 인코딩 `utf-8`, `errors="replace"` |
| `inject_memory_context` | inject-memory-context.sh + scripts/memory_context.py | `memory_context.py` 의 논리를 함수로 흡수하고 그 파일은 `git rm`. `/stock-*` 명령 정규식은 `/score-*` 로 바꾼다 |
| (없음) | enforce-citations.sh | **만들지 않는다.** 종목 리포트 전용이었다. 배선에서도 뺀다 |

## 배선

- `.claude/settings.json` 의 모든 명령을 아래 한 줄 형식으로 바꾼다.
  `uv run --frozen --directory "${CLAUDE_PROJECT_DIR:-.}" python -X utf8 scripts/hooks/guard.py <훅이름>`
  매처와 훅. PreToolUse `Bash|PowerShell` → block_dangerous_bash, protect_sensitive_files, enforce_plan. PreToolUse `Write|Edit|MultiEdit` → protect_sensitive_files, enforce_plan, forbid_financial_advice. PostToolUse `Write|Edit|MultiEdit` → forbid_financial_advice, remind_review, enforce_memory. PostToolUse `Bash|PowerShell` → forbid_financial_advice. UserPromptSubmit → inject_memory_context. Stop → remind_review. timeout 은 15 (첫 `uv run` 이 venv 를 만들 수 있다).
  **`PowerShell` 매처 추가가 핵심이다.** 지금은 PowerShell 도구가 모든 훅을 우회한다.
- `.codex/hooks.json`. 같은 훅 집합, 같은 이벤트. 명령은 `uv run --frozen python -X utf8 scripts/hooks/guard.py <훅이름>` 이다. Codex 는 Windows 에서 bash 를 거치지 않으므로 셸 변수 확장을 쓰지 않는다. cwd 가 세션 루트라는 가정을 README 에 적는다. Git Bash 절대경로는 없앤다. Codex 는 훅 파일이 바뀌면 신뢰 해시(`~/.codex/config.toml [hooks.state]`)를 다시 묻는다. 그 사실을 보고서에 적는다.
- `scripts/hooks/README.md`. 훅 목록·이벤트·출력 규약·fail-open·배선 가정, 그리고 Antigravity·Muse 배선은 확인 3건(차단 표현, 페이로드 필드 이름, 훅 프로세스의 작업 디렉터리) 뒤 별도 과제라는 것을 적는다.

## 테스트 `tests/test_hooks.py` (unittest, bash 불필요)

- 위험 명령(`rm -rf /`, `git push --force`, `curl … | sh`) 차단, 무해 명령 허용. Bash 와 PowerShell 페이로드 둘 다.
- 보호 경로(`.env`, `.github/workflows/x.yml`, `docs/finance-style-guide.md`) Write 차단. `docs/output-spec.md` 는 이제 허용.
- 단계 순서. 임시 루트에 `output/t/` 를 만들고 plan 없이 `research.md` Write → block, plan 있으면 allow. `report.html` 직접 Write → block. 빌드 명령은 review pass 없으면 block, 있으면 allow. `review-parts/x.md` 와 `evidence/candidates.json` 은 allow. 옛 경로 `research/t.md` 는 allow(게이트 없음).
- 금지 표현이 든 `output/t/draft.md` Write → block. `output/t/judgments.json` 도.
- remind_review 가 block 이 아니라 warn 을 돌려준다. Stop 에서 해시 불일치 → warn, 일치 → allow.
- enforce_memory 가 validator 실패 시 block(validator 경로를 실패하는 가짜 스크립트로 바꿔서).
- 무관한 폴더(루트에 `scripts/hooks/guard.py` 없음)에서 모든 함수가 allow.
- 예외를 던지는 가짜 훅이 `main` 을 통과할 때 exit 0 이다.
- 배선 정합. `.claude/settings.json` 과 `.codex/hooks.json` 이 이벤트별로 같은 훅 이름 집합을 갖고, 그 이름이 전부 `guard.HOOKS` 에 있고, `enforce_citations` 가 어디에도 없다.
- 배선 명령 스모크. 저장소 루트에서 `bash -c '<settings.json 의 명령 문자열>'` 에 `CLAUDE_PROJECT_DIR` 를 넣고 무해한 페이로드를 stdin 으로 줘 exit 0, 위험 명령 페이로드로 exit 2 가 나오는지. `shutil.which("bash")` 가 없으면 skip.

## 커밋

`refactor(hooks): bash 훅 9개를 scripts/hooks/guard.py 로 통합, 배선을 uv run 한 줄로(Claude·Codex), PowerShell 매처` 하나. 본문에 enforce-citations 제거 사유(종목 전용), remind-review 경고화 사유, output-spec 보호 해제 사유를 적는다.

## 주의

- 이 세션의 훅은 세션 시작 때 읽은 옛 배선으로 돈다. 새 배선은 다음 세션부터 적용된다. 그래서 스모크 테스트를 `bash -c` 로 직접 한다.
- `.claude/hooks/*.sh` 삭제는 커밋 직전 마지막 단계로 한다. 지우면 이 세션의 옛 훅이 "파일 없음" 오류를 낼 수 있다. exit 2 가 아니라 127 이라 차단은 아니다. 그 상태로 작업을 이어가되 보고서에 적는다.
- `scripts/build_report.py <slug>` 형태의 문자열을 테스트 밖 문서나 주석에 슬러그와 함께 적지 않는다. 옛 enforce-plan 이 명령 문자열을 훑는다.

## 검증 (Observable acceptance)

- `tests/test_hooks.py` 전부 통과. 기존 테스트의 실패·오류 집합이 `baseline-failures.txt` 와 같다. `npm run check` 통과.
- `git ls-files .claude/hooks` 가 비어 있다. `scripts/memory_context.py` 가 없다. `rg enforce-citations .claude .codex` 가 0건.
- 보고서 `validation/lane-C-hooks/REPORT.md` 에 스모크 테스트의 실제 명령과 exit code 를 붙인다.
