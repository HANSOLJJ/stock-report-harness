# 레인 C 보고서 — 훅 통합 (bash 9개 → scripts/hooks/guard.py)

브랜치 `HANSOLJJ/lane-C`, 작업일 2026-09-30. 커밋 SHA 는 이 보고서를 담은 커밋이다(`git log -1 -- validation/lane-C-hooks/REPORT.md`).

## 한 일

- `scripts/hooks/guard.py` 신설. 훅 함수 7개와 `Decision`(allow·block·warn·context), `HOOKS` 표, `main`(fail-open)을 담았다. 함수 7개인 이유는 `enforce-citations` 를 만들지 않았고, `inject-memory-context.sh` 와 `memory_context.py` 가 함수 하나로 합쳐졌기 때문이다.
- 변경 세 가지를 반영했다. `docs/output-spec.md` 보호 해제, `remind_review` 차단→경고, `enforce_plan` 의 `output/<slug>/` 묶음 배치 매핑.
- `.claude/settings.json`, `.codex/hooks.json` 을 `uv run` 한 줄 형식으로 재작성했다. 셸 계열 매처를 `Bash|PowerShell` 로 넓혔다. `enforce_citations` 는 배선에서 뺐다.
- `tests/test_hooks.py`(43건), `scripts/hooks/README.md` 추가. `.claude/hooks/**` 9개(lib 포함)와 `scripts/memory_context.py` 는 `git rm` 했다.

## 검증

| 항목 | 결과 |
|---|---|
| `python -X utf8 -m unittest tests.test_hooks` | 43건 OK |
| `pytest -q tests/test_hooks.py` | 43 passed |
| unittest 전체(`discover -s tests -t .`) | 800건, 실패 7·오류 30·skip 5. 기준선(757건, 7·30)에 새 43건이 더해졌고 실패·오류 37줄이 `baseline-failures.txt` 와 diff 결과 동일 |
| `pytest -q` 전체 | 28 failed, 109 errors. 기준선 문서에 pytest 집합이 없어 직접 비교하지 못했다. 실패에 `test_hooks` 는 없다. 내가 추가한 것은 새 테스트 파일뿐이다 |
| `npm run check` | 통과 |
| `git ls-files .claude/hooks` | 0줄 |
| `scripts/memory_context.py` | 없음 |
| `rg enforce-citations .claude .codex` | 0건 |

### 배선 명령 스모크 (실제 실행)

저장소 루트에서 Git Bash(`C:\Program Files\Git\usr\bin\bash.EXE`)로, `CLAUDE_PROJECT_DIR` 에 저장소 루트를 넣어 `settings.json` 의 명령을 그대로 실행했다.

명령 문자열은 `uv run --frozen --directory "${CLAUDE_PROJECT_DIR:-.}" python -X utf8 scripts/hooks/guard.py block_dangerous_bash` 이다.

| 도구 | 페이로드 명령 | exit |
|---|---|---|
| Bash | `git status` | 0 |
| PowerShell | `git status` | 0 |
| Bash | `git push --force origin main` | 2 (stdout `{"decision": "block", …}`) |
| PowerShell | `git push --force origin main` | 2 |

## 지시서와 다르게 한 것, 그 밖의 판단

1. **`inject_memory_context` 출력 형태.** 지시서는 "지금처럼 stdout 에 텍스트" 라고 했으나, 옛 `memory_context.py` 가 실제로 내던 것은 `{"hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": …}}` JSON 이다. 실제 동작을 유지했다.
2. **block 이유를 stderr 에도 쓴다.** exit 2 에서 Claude Code 가 모델에게 전달하는 것은 stderr 다. 옛 훅은 stdout JSON 만 냈다. stdout 형태는 그대로 두고 stderr 를 더했다.
3. **`remind_review` 의 상태 파일 폐기.** 옛 `.claude/state/touched-drafts.txt` 로 "만진 draft" 를 기억하던 방식을 없앴다. Stop 은 `output/*/review.md` 의 해시를 산출물과 직접 대조한다. PostToolUse 경고는 리뷰 입력 파일이 바뀔 때마다 나온다(리뷰가 아직 없어도 나온다. 지시서 그대로다).
4. **`enforce_memory` 대상은 옛 그대로** `memory/_daily/`, `memory/topics/` 만이다. 지시서의 "memory/ 아래" 를 옛 논리 이식 원칙에 맞춰 좁게 읽었다.
5. **`forbid_financial_advice` 는 `report.html` 을 더 이상 훑지 않는다.** 지시서가 대상 경로를 교체하라고 했다. 셸 명령 뒤에는 세 대상 글롭을 전부 훑는다. 그래서 대상 파일에 금지 표현이 이미 있으면 그 뒤 셸 호출이 모두 차단된다. 옛 동작과 같은 구조다.
6. **통합 브랜치 병합을 하지 못했다.** `git merge HANSOLJJ/revision_checker` 가 권한 분류기(Modify Shared Resources)에 거부되어 우회하지 않았다. 통합 브랜치에서 이 브랜치로 들어올 커밋은 `039657c`(`checklist.md` 만 변경) 하나라 내 파일과 겹치지 않는다. 병합은 조율자가 하거나, 허용해 주면 내가 한다.
7. 테스트 스모크에서 `subprocess.run(["bash", …])` 는 Windows 에서 WSL 의 `System32\bash.exe` 를 잡는다. 테스트는 `shutil.which("bash")` 경로를 쓴다.

## 이 세션의 옛 훅

세션 시작 때 읽은 옛 배선이 계속 돌았다. 스모크 중 명령 문자열에 `git push --force` 가 들어가 옛 훅이 차단했다(정상 동작). `.sh` 삭제는 마지막 단계에서 했으므로 이후 이 세션에서 옛 훅은 "파일 없음"(127)을 낼 수 있으나 차단은 아니다.

## Codex 신뢰 해시

`.codex/hooks.json` 이 바뀌었으므로 Codex 는 `~/.codex/config.toml [hooks.state]` 의 신뢰 해시를 다시 묻는다. 사용자가 한 번 승인해야 새 배선이 돈다. 그 전에는 신뢰되지 않은 훅으로 다뤄질 수 있다.

## 소유 밖에서 발견한 것 (고치지 않음)

- `.codex/hooks/**` 는 `.sh` 9개가 그대로 남아 있다. 레인 S 가 지운다. 새 `hooks.json` 은 이 파일들을 더 이상 부르지 않는다.
- `README.md` 76~84줄과 `docs/memory-system.md` 99~113줄이 `.claude/hooks/*.sh`, `scripts/memory_context.py`, `enforce-citations.sh` 를 여전히 설명한다. 레인 S 의 문서 정리 대상이다.
- `scripts/report_contract_lib.py:31` 주석이 `enforce-citations.sh` 를 언급한다(역사적 주석).
- `validation/**` 옛 보고서들이 옛 훅 경로를 인용한다. 기록이므로 그대로 둔다.
- `protect_sensitive_files` 의 셸 변경 감지가 bash 명령 기준이라 PowerShell cmdlet(`Set-Content`, `Remove-Item` 등)은 변경으로 보지 않는다. 논리 이식 원칙에 따라 그대로 두었다(README 에 적음).
- 작업 트리의 `settings.json`·`hooks.json` 은 LF 로 저장했다. 저장소 인덱스가 LF 이므로 diff 잡음이 없다.

## 남긴 것

- Antigravity·Muse 배선(확인 3건 뒤 별도 과제).
- `approval.json`·규칙 파일·이동한 실행 폴더 보호(4.2).
- 통합 브랜치 병합과 병합 뒤 테스트 재실행(위 6번).
