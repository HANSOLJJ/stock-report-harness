# 레인 F — 승인 보호·실행 잠금(4.2) → 승인 명령 summary·confirm·approve --via·revoke 와 트리거 렌더(4.3)

에이전트: Claude Opus 5.5. 의존: 레인 A·B·C·D·E 병합 완료(통합 브랜치 기준). 공통 규약: `README.md` 를 먼저 읽는다. 계획 원문: `../plan.md` 4단계 "훅을 Python 한 모듈…" 표의 `protect_sensitive_files`·`scorecard_cli.py approve` 행, "다중 에이전트 운영" 의 실행 잠금·승인 거부 확대, "승인 페이지 (방식 2)" 의 Python 쪽 새 명령, 그리고 "디스패치 전에 고정하는 계약" 의 `summary --json`.

## 시작 시점 상태 (2026-09-30 조율자 기록)

- 실행 묶음 `output/<run_id>/`, 경로는 `scripts/scorecard/paths.py` 의 `run_paths`. 기존 실행 2개는 `approval_valid: true`.
- 승인 해시 비교는 `stages.approval_mismatches(approved, current)` 한 곳이다(레인 E). 새 승인은 `current_hashes` 전체(6키 + sources + 있을 때 evidence·triggers)를 담는다.
- 훅은 `scripts/hooks/guard.py`(레인 C). 도구 이름 별칭은 `SHELL_TOOLS`·`FILE_TOOLS`. 차단은 `block(reason)`, 테스트는 `tests/test_hooks.py` 가 함수를 dict 로 직접 부른다.
- 승인 페이지는 `server/approvals.js`(레인 D). Python 명령 `summary <run_id> --json`, `confirm <run_id> --evidence … [--reject …]`, `approve <run_id> --by … [--note …] --via browser`, `revoke <run_id> --by … --note …` 를 `execFile` 로 부른다. 계약 픽스처는 `tests/node/fixtures/summary.sample.json` 이다. **이 형태를 그대로 낸다.**
- 연구 단계는 `triggers.json` 을 그린다. 초안(`render_md.render_draft`)과 HTML(`render_html`)의 트리거 절은 아직 기준선 트리거를 그린다.
- 테스트 기준: unittest 1030건 중 실패 1·오류 14(전부 `validation/*/_raw` 원자료 부재). 이 집합이 늘면 안 된다.
- baseline 실행은 원래 있던 재계산 불일치로 `build_scorecard` 가 멈춘다(승인 검사는 통과). 이 상태를 바꾸지 않는다.
- 이 세션에서 확인한 환경변수. 에이전트 세션에는 `CLAUDECODE`, `CLAUDE_CODE_ENTRYPOINT`, `CLAUDE_CODE_SESSION_ID`, `ORCA_AGENT_LAUNCH_TOKEN` 등이 있다. Orca 터미널 식별자는 `ORCA_TERMINAL_HANDLE` 이다(계획서의 `ORCA_TERMINAL_ID` 가 아니다). **`ORCA_*` 는 사람이 여는 일반 Orca 셸에도 있을 수 있다.** 사람이 Orca 셸에서 `node server.js --approvals` 를 띄워도 승인이 되어야 한다.

## 소유 파일 (Ownership)

- `scripts/hooks/guard.py`, `tests/test_hooks.py`, `scripts/hooks/README.md`
- `scripts/scorecard/stages.py`, `scripts/scorecard_cli.py`, `scripts/scorecard/schema.py`(approval 에 `approved_via` 선택 키), `scripts/scorecard/render_md.py`, `scripts/scorecard/render_html.py`(트리거 절만)
- `server/approvals.js`(코드 시도 제한만), `tests/node/approvals.test.js`(해당 테스트 추가)
- `.gitignore`(`output/*/.lock` 한 줄)
- 새 테스트 `tests/test_approval_commands.py`, `tests/test_run_lock.py`, `tests/test_trigger_render.py`

만지지 않는 것: `output/ai-scorecard-2026-09-*/**`(내용 변경 금지. 보호 대상을 추가할 뿐이다), `scorecard/rules/*.json`, `scorecard/companies.json`, `scorecard/history.csv`, `.claude/**`, `.codex/**`, `docs/**`, `AGENTS.md`, `README.md`, `server.js`.

## 4.2 승인 보호·실행 잠금

커밋 메시지: `feat(hooks): approve·approval.json·이동한 실행·규칙 파일 보호, 실행 잠금`

1. `guard.protect_sensitive_files` 보호 목록에 더한다. (a) `(^|/)approval\.json$`. (b) `scorecard/rules/v1.5.json`, `v1.6.json`, `v1.7.json`(v1.8 은 아직 쓰는 실행이 없어 넣지 않는다. 첫 실행이 v1.8 로 승인되면 넣는다고 README 에 적는다). (c) 이동한 실행 두 폴더 `output/ai-scorecard-2026-09-baseline/**`, `output/ai-scorecard-2026-09-obsreg/**`. (d) `scorecard/history.csv`. 파일 도구 경로와 셸 명령 리터럴 둘 다 기존 방식대로 막는다.
2. 셸 명령에 `scorecard_cli\.py\s+approve\b`, `scorecard_cli\.py\s+revoke\b`, `stages\.approve\b` 가 있으면 변경 기호 여부와 무관하게 막는다. 메시지는 "승인·취소는 사람이 `node server.js --approvals` 승인 페이지에서 한다" 로 한다. `confirm` 은 막지 않는다. 근거 확정은 승인이 아니고, 확정하면 해시가 바뀌어 사람이 다시 승인해야 하기 때문이다.
3. `scorecard_cli.py` 의 `approve`·`revoke` 는 CLI 계층에서 에이전트 세션을 거부한다. 거부 조건은 `CLAUDECODE` 또는 `CLAUDE_CODE_ENTRYPOINT` 가 있을 때, 그리고 **에이전트 터미널에만 있고 사람 셸에는 없는 것을 직접 확인한** 변수다. 확인 방법: 자기 워크트리에 `orca terminal create --worktree active --title env-probe --json` 로 일반 셸을 하나 만들고 `orca terminal send` 로 `env | sort` 를 실행해 읽은 뒤 `orca terminal close` 로 닫는다. 자기 세션의 `env` 와 비교해 에이전트에만 있는 변수를 고른다. 결과는 보고서에 표로 남긴다. 일반 셸에도 있는 `ORCA_*` 는 거부 조건에 넣지 않는다. `stages.approve()` 함수 자체는 막지 않는다(테스트가 부른다). TTY 검사는 두지 않는다.
4. 실행 잠금. `output/<run_id>/.lock`(gitignore)에 `{owner, started_utc, stage}` 를 쓴다. 소유자는 `SCORECARD_AGENT`, 없으면 `ORCA_TERMINAL_HANDLE`, 없으면 OS 사용자명. `research`·`calculate`·`draft`·`review-template`·`collect`·`confirm` 단계는 다른 소유자의 잠금이 있으면 거부하고 `--force` 로 인수한다. 단계가 끝나도 잠금은 남긴다(한 에이전트가 실행을 끝까지 맡는다). `approve`·`revoke`·`build` 는 잠금을 요구하지도 쓰지도 않는다(사람 행위). `init` 은 잠금을 만든다.
5. `guard.enforce_plan` 은 Write/Edit 대상 묶음에 다른 소유자의 잠금이 있으면 막는다. 훅 프로세스의 소유자 판정도 같은 규칙(환경변수)으로 한다. 잠금 파일이 없으면 통과한다.
6. 테스트 `tests/test_hooks.py` 와 `tests/test_run_lock.py`. approve·revoke 명령 차단(Bash·PowerShell), `approval.json` Write 차단, 이동한 실행 파일 Write·셸 변경 차단, 규칙 v1.7 차단·v1.8 허용, history.csv 차단, 잠금 충돌·`--force` 인수·잠금 없는 통과, CLI approve 의 에이전트 환경 거부(환경변수를 patch 해서).

## 4.3 승인 명령과 트리거 렌더

커밋 메시지: `feat(approve): summary·confirm·revoke 명령, approved_via 기록, 초안·HTML 트리거 절`

1. `stages.summary(slug) -> dict` 와 CLI `summary <run_id> --json`. `tests/node/fixtures/summary.sample.json` 의 키 구조를 정확히 따른다. 값은 `status`·`render_md` 가 이미 계산하는 데이터를 재사용한다. `companies[].baseline`·`current` 는 `{total, rank}`, `changed_factors` 는 기준선 대비 점수가 바뀐 factor, `carried_factors` 는 `status: carried` 판단의 factor, `pending` 은 미결 사유 문자열. `review` 는 `review.md` frontmatter 와 `review-parts/` 에서, 없으면 null. `evidence` 는 `candidates.json`·`evidence.json` 에서 개수와 항목, 파일이 없으면 0 과 빈 리스트. `hashes` 는 `current_hashes`. `approval` 은 `{exists, valid, approved_by, approved_at}`, valid 는 `approval_mismatches` 가 비었는지. JSON 은 `ensure_ascii=False`, 표준 출력 UTF-8.
2. `stages.confirm(slug, *, evidence_ids, reject_ids=())` 와 CLI `confirm`. 근거 ID 는 `^EV-[a-z0-9-]+-\d{3}$` 만 받는다(형식이 틀리면 SchemaError, 인자가 `--` 로 시작하는 값 포함). `evidence.json` 에 없는 ID 는 오류. 확정은 `status: confirmed` 와 `reviewer`(CLI `--by`, 없으면 `SCORECARD_AGENT` 또는 사용자명), `reviewed_at`(UTC 날짜)을 쓴다. 거부는 항목을 지운다. 쓴 뒤 스키마 검증. 해시가 바뀌므로 표준 출력에 "calculate → draft → review 를 다시 돌린다" 를 안내한다.
3. `approve` 에 `--via browser|terminal`(기본 terminal)을 더하고 `approval.json` 에 `approved_via` 를 쓴다. `schema.validate_approval` 은 `approved_via` 를 선택 키로 받는다. 기존 두 실행의 승인 파일은 바뀌지 않고 유효해야 한다.
4. `stages.revoke(slug, *, by, note)` 와 CLI `revoke`. `approval.json` 을 지우고 `output/<run_id>/revocations.jsonl` 에 `{revoked_by, revoked_at, note, approval_id, hashes}` 한 줄을 더한다. `note` 는 비어 있으면 안 된다. 승인이 없으면 오류.
5. 초안과 HTML 의 트리거 절. `render_draft` 와 `render_html` 은 `ctx.triggers`(레인 E 가 `RunContext` 에 넣었다)가 있으면 그것을 그리고, 없으면 지금처럼 기준선 트리거를 그린다. 연구 단계의 `## 트리거(활성)` 표와 같은 열을 쓴다. 미래 점수는 싣지 않는다(C-14). **기존 두 실행의 draft 는 다시 렌더하지 않는다.** 그 실행들에는 `triggers.json` 이 없으므로 출력이 같아야 하고, 이것을 테스트로 고정한다(obsreg 컨텍스트로 `render_draft` 를 돌려 저장된 draft 와 바이트가 같은지. 이미 그런 테스트가 있으면 그것이 통과하는지만 확인).
6. `server/approvals.js` 에 코드 실패 제한. 같은 서버에서 잘못된 코드가 5번 오면 그 뒤 모든 POST 를 403 으로 막고 터미널에 "코드 실패 5회 — 서버를 다시 띄우세요" 를 출력한다. `tests/node/approvals.test.js` 에 테스트 하나. `npm run test:node` 로 확인한다.
7. 테스트 `tests/test_approval_commands.py`: summary 키 구조가 픽스처와 같은지(키 집합 재귀 비교, 값은 제외), 기존 obsreg 로 summary 가 돌고 `approval.valid` 가 true 인지, confirm 형식 거부·없는 ID 거부·확정 뒤 current_hashes 의 evidence 변경, approve `--via browser` 기록, revoke 기록과 승인 파일 삭제(임시 묶음에서), 기존 실행 승인 파일 불변. `tests/test_trigger_render.py`: triggers.json 이 있으면 초안·HTML 에 그 트리거가 나오고, 없으면 기준선 트리거가 나온다.

## 검증 (Observable acceptance)

- 두 실행 `status` 의 `approval_valid: true`, `output/ai-scorecard-2026-09-*` 아래 `git diff` 0.
- 새 승인 경로 종단(임시 묶음): init → … → review-template → (테스트가 review 를 pass 로) → `approve --via browser` → `summary` 의 `approval.valid` true → `confirm` 으로 근거 변경 → `approval.valid` false → `revoke`. 
- 테스트 기준(1030건 중 실패 1·오류 14)에서 증가 없음. `npm run check`, `npm run test:node` 통과.
- 환경변수 조사 결과 표가 보고서에 있다.
- 보고서 `validation/lane-F-approval/REPORT.md` 를 커밋에 포함한다. 통합 브랜치 merge 가 권한으로 거부되면 우회하지 말고 보고서에 적는다.
