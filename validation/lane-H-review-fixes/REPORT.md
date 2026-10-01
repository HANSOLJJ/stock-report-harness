# 레인 H — 독립 검증 발견 수정 F-1·F-2·F-3·F-4·F-7 (2026-10-01)

에이전트: Claude Opus 5.5. 지시서: `.agents/plans/evidence-layer-2026-09/dispatch/lane-H.md`. 근거: `validation/lane-V-independent-review/REPORT.md` 의 F-1·F-2·F-3·F-4·F-7 절.

## 요약

수정 전에 `git archive HEAD` 로 푼 사본에서 레인 V 의 재현을 다시 돌려 다섯 발견 중 넷(F-1·F-2·F-3·F-7)이 그대로 재현되는 것을 확인했다. 그 뒤 승인·취소의 에이전트 거부를 `stages.approve`·`stages.revoke` 본체로 옮기고(F-2), `init --force` 의 승인 파괴를 stage 와 훅 양쪽에서 막았으며(F-1), 보호 훅을 "쓰기 대상" 판정으로 바꾸면서 `scorecard/baseline/**` 를 보호 목록에 넣었다(F-3·F-7). CLI 안내와 plan 템플릿 흐름도 고쳤다(F-4). 수정 후 사본에서 같은 재현을 돌리면 네 발견이 모두 막히고, 기존 두 실행은 `approval_valid: true` 그대로다. 테스트 실패·오류 집합은 늘지 않았다.

## 한 일

| 발견 | 파일 | 변경 |
| --- | --- | --- |
| F-2 | `scripts/scorecard/stages.py` | `refuse_agent_session(action, *, allow_agent_session=False)` 를 새로 두고 `approve`·`revoke` 첫 줄에서 부른다. 두 함수에 키워드 인자 `allow_agent_session: bool = False` 를 더했다. 판정 함수 `agent_session_markers` 는 그대로다. |
| F-2 | `scripts/scorecard_cli.py` | `_refuse_agent_session` 을 지웠다. `cmd_approve`·`cmd_revoke` 는 stage 함수만 부른다. CLI 는 `allow_agent_session` 을 노출하지 않는다. |
| F-2 | `tests/test_approval_commands.py` | `stages.approve`·`stages.revoke` 직접 호출 9곳에 `allow_agent_session=True` 를 명시했다. 다른 테스트 파일에는 직접 호출이 없다(`rg` 로 확인). |
| F-1 | `scripts/scorecard/stages.py` | `init_run` 이 `force` 이고 `approval.json` 이 있으면 에이전트 세션에서 `SchemaError("…승인 기록이 지워진다…")` 로 거부한다. |
| F-1 | `scripts/scorecard_cli.py` | 사람 세션이 승인된 실행을 덮어쓰면 `[경고] 승인된 실행을 --force 로 덮어써 승인 기록이 지워졌다(approval.json 삭제)…` 를 출력한다. |
| F-1 | `scripts/hooks/guard.py` | `_init_force_approved`: `scorecard_cli.py init … --force`(줄임 `--fo` 포함)가 `output/<이름>/approval.json` 이 있는 실행을 가리키면 막는다. 맨 슬러그와 `output/<slug>` 경로 모두 마지막 경로 조각으로 푼다. |
| F-3 | `scripts/hooks/guard.py` | `_PROTECTED_TREES = [두 실행 폴더, "scorecard/baseline"]`. 파일 도구 경로와 셸 쓰기 대상 양쪽에 적용된다. |
| F-7 | `scripts/hooks/guard.py` | `_MUTATING`·`_REDIRECT` 정규식을 지우고, `shlex` 로 토큰화해 제어 연산자마다 명령을 나눈 뒤 쓰기 대상만 대조한다(아래 표). |
| F-4 (a) | `scripts/scorecard_cli.py` | draft 뒤 안내: `… review-template <slug> → 4-way 리뷰 → 승인 대기 보고(사람이 승인 페이지에서 승인한다)`. |
| F-4 (b) | `scripts/scorecard/render_md.py` | plan 템플릿 흐름: `plan → collect → research → calculate → draft → review → awaiting_user → build`. 기존 두 실행의 plan.md 는 다시 렌더하지 않았다. |
| F-4 (c) | `scripts/scorecard_cli.py` | 모듈 docstring usage 와 모든 "다음:" 안내(confirm 의 재계산 안내 포함)를 `uv run --frozen python -X utf8 scripts/…` 로 바꿨다. |
| 문서 | `scripts/hooks/README.md` | 보호 목록에 baseline, 셸 쓰기 대상 판정 표, `init --force` 차단, 첫 방어선 위치(stage 함수 본체), 남은 틈. |
| 테스트 | `tests/test_lane_v_fixes.py` (새 파일, 21건) | 훅 사례 표(Bash·PowerShell), init --force 훅, stage 거부, init_run 거부·경고, 안내 문구. |

### 셸 쓰기 대상 판정 (F-7, 계약대로)

| 명령 | 판정 |
| --- | --- |
| 리다이렉션 `>`·`>>` 의 대상 | 보호 경로면 차단 |
| `rm`·`mv`·`cp`·`tee`·`touch`·`truncate`·`install`·`chmod`·`chown`, `sed -i`, `perl -pi`, `git checkout`·`restore`·`reset` 의 인자 | 보호 경로면 차단 |
| `python`·`python3`·`py`·`node`, `uv run …`, `uvx` | 보호 경로 문자열을 담기만 해도 차단 |
| 그 밖(`cat`·`rg`·`grep`·`ls`·`head`·`git show`·`git diff` 등) | 통과 |

보조 규칙은 세 가지다. 앞에 붙은 `VAR=값`·`env -u X`·`command`·`exec`·`nohup`·`time` 은 건너뛰고 뒤의 동사를 본다. `cd`·`pushd`·`Set-Location`·`git -C` 뒤의 상대 경로는 바뀐 폴더 기준으로 푼다(이전 구현은 `cd 보호폴더 && rm draft.md` 를 동사+리터럴로 막았으므로, 이 규칙이 없으면 그 사례가 새로 뚫린다). 따옴표가 맞지 않아 토큰화가 실패하면 보호 경로를 언급하기만 해도 막는다(fail-closed).

## 재현 전후 비교 (사본에서)

재현 스크립트는 시스템 임시 폴더에 두었고 저장소에 넣지 않았다. 사본은 `git archive 971b1ae` 로 풀었고, 수정 후 사본은 같은 사본에 바뀐 네 소스 파일을 덮어썼다. 두 경우 모두 에이전트 표지 네 개(`CLAUDECODE`, `CLAUDE_CODE_ENTRYPOINT`, `ORCA_AGENT_LAUNCH_TOKEN`, `AI_AGENT`)가 있는 프로세스에서 돌렸다.

| 사례 | 수정 전 | 수정 후 |
| --- | --- | --- |
| 사전: 두 실행 approval_valid | True · True | True · True |
| F-1 훅 `uv run … scorecard_cli.py init <obsreg> --force …` (Bash·PowerShell, 맨 슬러그·`output/` 경로) | protect=allow ×4 | protect=**block** ×4 |
| F-1 훅 같은 명령, 승인 없는 새 슬러그 | allow | allow |
| F-1 실행 CLI `init <obsreg> --force` | exit 0, 뒤에 `approval.json 없음` | exit 1 `[FAIL] 에이전트 세션(…)에서는 승인된 실행 output/ai-scorecard-2026-09-obsreg 를 --force 로 덮어쓸 수 없다…`, 뒤에도 `approval_valid=True` |
| F-2 실행 `stages.approve(obsreg)` 직접 호출(approval.json·report.html 을 치운 뒤) | 승인 생성, `approval_valid=True` | `SchemaError: 에이전트 세션(…)에서는 승인할 수 없다…`, `approval.json 없음` |
| F-2 훅 `uv run python -c "from scorecard.stages import approve; approve('<obsreg>', …)"` | allow | allow (아래 "남긴 것" 참고. 이 호출은 이제 함수 본체가 거부한다) |
| F-3 Write `scorecard/baseline/v1.5/triggers.json` | allow | **block** |
| F-3 `echo x > …/triggers.json`, `sed -i … …/triggers.json` (Bash·PowerShell) | allow ×4 | **block** ×4 |
| F-3 `cat …/triggers.json` | allow | allow |
| F-7 `cat output/<obsreg>/approval.json; echo done` (Bash·PowerShell) | **block** ×2 (오탐) | allow ×2 |
| F-7 `rg`·`git show HEAD:…approval.json` | allow | allow |
| F-7 `rm output/<obsreg>/approval.json` | block | block |

F-4 는 문면 결함이라 재현 대신 `GuidanceTest` 3건으로 잠갔다. 수정 전 사본에서 이 테스트 파일을 돌리면 21건 중 20건이 실패(하위 사례 83건 실패·오류 1건)하고, 남은 1건(`test_cli_still_refuses_through_the_stage`)은 수정 전에도 CLI 가 거부했으므로 통과가 맞다. 즉 새 테스트는 고친 동작에 실제로 걸려 있다.

이 워크트리의 훅이 지금의 `guard.py` 라서, 수정 뒤 이 세션에서 `head -c 120 output/<obsreg>/approval.json; echo; echo done` 을 실제로 실행해 훅이 읽기를 통과시키는 것도 확인했다.

## 검증 명령과 결과

| 명령 | merge 전 | merge 후 (`184c3e0`) |
| --- | --- | --- |
| `uv run --frozen python -X utf8 -m unittest discover -s tests -t .` | 1111건 · 실패 1 · 오류 14 | 1115건 · 실패 1 · 오류 14 |
| `uv run --frozen pytest -q` | 15 failed · 1098 passed · 2024 subtests passed | 15 failed · 1102 passed · 2024 subtests passed |
| `npm run check` | 통과 | 통과 |
| `npm run test:node` | tests 10 · pass 10 · fail 0 | tests 10 · pass 10 · fail 0 |
| `uv run … scorecard_cli.py summary ai-scorecard-2026-09-baseline` / `…-obsreg` | — | 둘 다 `승인: 있음 · 유효` |
| `git diff --name-only HANSOLJJ/revision_checker HEAD -- output/ scorecard/` | — | 빈 출력(변경 0) |

- 기준선은 지시서의 1090건 중 실패 1·오류 14다. 늘어난 25건(1115−1090)은 새 테스트 21건과 레인 I 가 merge 로 더한 4건이다.
- 실패·오류 집합은 merge 전후 줄 단위로 같다(`diff` 출력 없음). 모듈은 `test_scorecard_fix54_obs`·`fix55_stage2`·`fix57_stage1`·`fix58_stage1`·`fix58_stage2`·`obs_recency` 이고 전부 원자료(`validation/*/_raw` 등) 부재다.
- 수정 전 사본(`git archive`, git 저장소 밖)에서 같은 러너를 돌리면 실패 2·오류 31 이 나온다. 늘어난 것은 git 이력을 읽는 테스트(`fix59`·`fix64`·`WiringSmokeTest` 등)가 저장소 밖이라 실패한 것이고, 수정 후 집합은 그 집합의 부분집합이다(새 실패 0).

## 소유 밖에서 발견한 문제 (고치지 않음)

1. **문서의 첫 방어선 위치가 낡았다.** `AGENTS.md:39`, `README.md:112`, `docs/scorecard/structure.md:143·161` 이 첫 방어선을 "CLI 의 거부" 로 적는다. 이제 거부는 `scorecard.stages.approve`·`revoke` 본체에 있다(CLI 는 그 함수를 부를 뿐이다). 레인 I 의 README 훅 표(103행)는 확정 계약과 일치한다.
2. **`scripts/scorecard/render_md.py:130`** 의 plan 템플릿 리뷰 기준에 uv 없는 `python scripts/validate_report_contract.py` 가 남아 있다. 지시서가 이 파일의 소유를 "plan 템플릿 흐름 문구만" 으로 한정해 고치지 않았다.
3. **`validation/recheck_worker_final.py:66`** 이 `stages.approve` 를 인자 없이 부른다. 에이전트 세션에서 다시 돌리면 이제 거부된다. 지난 검증 스크립트라 고치지 않았다.

## 남긴 것

- 훅이 잡지 않는 쓰기 형태: PowerShell cmdlet(`Set-Content`·`Remove-Item` 등, 별칭 `rm`·`cp`·`mv` 는 잡는다), `find … -delete`, `xargs rm`, 글롭(`rm output/ai-*`), 보호 폴더의 상위 폴더 삭제(`rm -rf output`), `dd of=`·`ln` 같은 계약 밖 동사. 모두 수정 전에도 통과하던 형태이고, 계약의 동사 목록을 README 표와 맞추려고 넓히지 않았다. `scripts/hooks/README.md` 의 "아직 하지 않은 것" 에 적었다.
- `from scorecard.stages import approve` 처럼 함수 이름을 리터럴 `stages.approve` 없이 부르는 명령은 훅이 여전히 통과시킨다. 이 경로는 이제 함수 본체가 거부하므로 훅을 넓히지 않았다. 표지 변수를 지운 셸에서 import 로 부르는 경로는 여전히 열려 있다(레인 V·AGENTS.md 가 적은 "임의 Python 을 실행할 수 있는 에이전트" 한계).
- `init_run` 에는 `allow_agent_session` 인자를 두지 않았다. 사람 세션 경로는 `human_env` 로 시험한다.
- `init --force` 가 지운 승인은 `revocations.jsonl` 에 남지 않는다(F-1 범위 밖, 지금도 사람 세션에서만 일어난다).

## 커밋

- `e236b52` fix(scorecard): 승인 거부를 stage 함수 본체로 옮기고 init --force 승인 파괴를 막는다 (F-1·F-2·F-4)
- `45d7488` fix(hooks): 보호 훅을 쓰기 대상 판정으로 바꾸고 기준선과 init --force 를 보호한다 (F-1·F-3·F-7, 새 테스트)
- `184c3e0` 통합 브랜치 `HANSOLJJ/revision_checker` merge (충돌 없음)
- 이 보고서 커밋 (`docs(validation)`) 이 최종 커밋이다.

소유 파일만 바뀌었다(`git diff --stat HANSOLJJ/revision_checker...HEAD`: `scripts/hooks/README.md`, `scripts/hooks/guard.py`, `scripts/scorecard/render_md.py`, `scripts/scorecard/stages.py`, `scripts/scorecard_cli.py`, `tests/test_approval_commands.py`, `tests/test_lane_v_fixes.py`, 그리고 이 보고서).
