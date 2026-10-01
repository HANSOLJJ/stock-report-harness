# 레인 H — 독립 검증 발견 수정: F-1·F-2·F-3·F-4·F-7

에이전트: Claude Opus 5.5. 의존: 레인 V 보고서 병합 완료. 공통 규약: `README.md` 를 먼저 읽는다. **발견의 재현 명령과 근거는 `validation/lane-V-independent-review/REPORT.md` 에 있다. 먼저 그 보고서의 F-1·F-2·F-3·F-4·F-7 절을 읽고, 수정 전에 재현부터 한다.** 레인 I(Sonnet)가 동시에 F-5·F-6 을 고친다. 소유가 겹치지 않는다.

## 확정 계약 (레인 I 가 README 훅 표를 이 내용으로 쓴다. 바꾸려면 ask)

- 보호 목록에 `scorecard/baseline/**` 를 더한다(F-3).
- 셸 명령의 보호 경로 검사는 "쓰기 대상" 일 때만 막는다(F-7). 쓰기 대상이란 리다이렉션(`>`, `>>`)의 대상, 또는 변경 동사(`rm`, `mv`, `cp`, `tee`, `touch`, `truncate`, `sed -i`, `perl -pi`, `install`, `chmod`, `chown`, `git checkout`·`git restore`·`git reset` 의 경로 인자)의 인자다. `cat`·`rg`·`grep`·`ls`·`head`·`git show`·`git diff` 처럼 읽기만 하는 명령의 경로 언급은 통과한다. **`python`·`node`·`uv run python` 처럼 인터프리터가 보호 경로 문자열을 담은 명령은 지금처럼 막는다**(스크립트 안의 쓰기를 셸에서 가릴 수 없다).
- `scorecard_cli.py init <slug> … --force` 는 `output/<slug>/` 에 승인 파일이 있으면 훅이 막는다(F-1). 슬러그가 맨 이름이어도 대상 폴더로 해석한다.
- 승인·취소의 에이전트 거부는 `stages.approve`·`stages.revoke` 함수 안에서 한다(F-2).

## 소유 파일 (Ownership)

- `scripts/hooks/guard.py`, `scripts/hooks/README.md`, `tests/test_hooks.py`
- `scripts/scorecard/stages.py`, `scripts/scorecard_cli.py`, `scripts/scorecard/render_md.py`(plan 템플릿 흐름 문구만)
- 승인 함수를 직접 부르는 기존 테스트(`tests/test_approval_commands.py`, `tests/test_run_lock.py`, `tests/test_evidence_e2e.py` 등 grep 으로 찾는다)와 새 테스트 `tests/test_lane_v_fixes.py`

만지지 않는 것: `scripts/scorecard/collect_news.py`(레인 I), `README.md`·`AGENTS.md`·`docs/**`(레인 I), `output/ai-scorecard-2026-09-*/**`, `scorecard/**`, `server*`, `.claude/**`, `.codex/**`.

## 고칠 것

1. **F-1** `stages.init_run`(또는 `cmd_init`)이 기존 실행을 `--force` 로 덮어쓸 때, 그 실행에 승인 파일이 있고 에이전트 세션이면 `SchemaError` 로 거부한다. 사람 세션은 지금처럼 허용하되 표준 출력에 "승인 기록이 지워진다" 를 경고한다. 훅도 위 계약대로 막는다.
2. **F-2** 에이전트 판정(`agent_session_markers` 등 레인 F 가 만든 함수)을 `stages.approve`·`stages.revoke` 본체로 옮긴다. CLI 의 거부는 그 함수를 부르는 것으로 바꿔 판정이 한 곳에만 있게 한다. 테스트가 쓸 수 있도록 키워드 인자 `allow_agent_session: bool = False` 를 두고, CLI 는 이 인자를 노출하지 않는다. 승인 함수를 부르는 기존 테스트는 이 인자를 명시한다.
3. **F-3** 보호 목록에 `scorecard/baseline/**` 를 넣는다. 파일 도구 경로와 셸 쓰기 대상 둘 다.
4. **F-4** (a) `draft` 뒤 "다음" 안내를 `review-template → 4-way 리뷰 → 승인 대기 보고(사람이 승인 페이지에서 승인)` 로 바꾼다. 에이전트가 읽는 안내에 approve 실행을 넣지 않는다. (b) `render_md` 의 plan 템플릿 흐름에 `collect` 를 넣는다(`plan → collect → research → calculate → draft → review → awaiting_user → build`). 기존 두 실행의 plan.md 는 다시 렌더하지 않는다. (c) `scorecard_cli.py` 의 모든 "다음:" 안내와 모듈 docstring usage 를 `uv run --frozen python -X utf8 scripts/…` 형식으로 바꾼다.
5. **F-7** 위 계약의 "쓰기 대상" 판정으로 바꾼다. 기존 `tests/test_hooks.py` 의 차단 사례는 모두 그대로 막혀야 한다.

## 검증 (Observable acceptance)

- 레인 V 보고서의 F-1·F-2·F-3·F-7 재현 명령을 **사본에서** 다시 돌려 이제 막히는지 보고서에 전후를 붙인다. F-2 는 에이전트 표지가 있는 프로세스에서 `stages.approve` 직접 호출이 거부되는지.
- 훅 사례 표 테스트: 읽기(`cat`·`rg`·`git show` + 보호 경로) 통과, 쓰기(`>`·`>>`·`rm`·`cp`·`mv`·`sed -i`·`tee`) 차단, 인터프리터(`python -c`·`uv run python`) + 보호 경로 차단, `init … --force <승인 있는 슬러그>` 차단, 승인 없는 슬러그 `init --force` 통과, `scorecard/baseline/v1.5/triggers.json` 쓰기 차단. Bash 와 PowerShell 페이로드 둘 다.
- 두 기존 실행 `approval_valid: true`, `output/ai-scorecard-2026-09-*` 변경 0.
- 테스트 기준(unittest 1090건 중 실패 1·오류 14, 전부 원자료 부재)에서 증가 없음. `npm run check`, `npm run test:node` 통과.
- 보고서 `validation/lane-H-review-fixes/REPORT.md` 를 커밋에 포함한다. 커밋은 발견별로 나눠도 되고 2~3개로 묶어도 된다. 통합 브랜치 merge 가 거부되면 보고만.
- 이 워크트리의 훅은 지금의 `guard.py` 다. 재현 명령 문자열이 훅에 걸리면 페이로드를 파일로 만들어 `guard.py` 에 stdin 으로 넣는 방식으로 확인한다.
