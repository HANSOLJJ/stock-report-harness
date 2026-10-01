# 레인 N: 재검증 발견 V2-1~V2-4 수정과 V2-5 코드 속 안내 문구 (2026-10-01)

에이전트: Claude Opus 5.5. 지시서는 `.agents/plans/evidence-layer-2026-09/dispatch/lane-N.md`, 발견은 `validation/lane-V2-recheck/REPORT.md` 의 V2-1~V2-5 절이다. 고치기 전에 `git archive HEAD`(`ef361a3`) 사본에서 V2-1~V2-4 를 먼저 재현했고, 고친 뒤 병합 커밋 `6126a63` 의 사본에서 같은 스크립트를 다시 돌려 전후를 비교했다. 재현 스크립트와 사본은 세션 임시 폴더에만 두었고 저장소에는 남기지 않았다. 승인·취소 명령은 실행하지 않았다.

## 요약

다섯 건을 고쳤다. 유효한 승인이 있는 실행의 입력·산출물을 바꾸는 단계는 이제 한 함수(`stages.protect_approved_run`)가 판정해 에이전트 세션이면 거부하고, 훅도 같은 판정으로 막는다(V2-1). `init --from-run` 은 인용 근거와 트리거를 함께 옮기고 교차 참조가 맞지 않으면 아무것도 쓰지 않고 멈춘다(V2-2). 보호 경로 대조는 대소문자를 가리지 않고, 승인 파일은 이름이 정확히 `approval.json` 이고 `approval_id` 가 재계산과 같을 때만 승인이다(V2-3). 쓰기가 있는 명령에서는 변수·명령 치환·따옴표 안의 보호 경로도 막고, 중첩 셸·`awk`·`dd` 는 인터프리터 규칙으로 묶었다(V2-4). 읽기 명령은 그대로 통과한다(F-7 회귀 없음). 기존 두 실행은 바이트 변경이 없고 `approval_valid: true` 이다.

## 계약 해석 (조율자 회신, 2026-10-01)

확정 계약은 CLI 를 "유효한 승인이 있는 실행", 훅을 "승인 있는 실행 이름을 가리키면" 으로 적었다. 그런데 사람이 승인 페이지에서 판단을 고치면 `approval.json` 은 남고(무효) 페이지 안내가 "에이전트에게 다시 돌리게 한다" 이다. 훅이 파일 존재만으로 막으면 이 정상 흐름이 막히므로 `ask` 로 확인했고, 다음으로 회신받아 그대로 구현했다.

- 훅도 승인 파일이 **유효할 때만** 막는다. 유효성은 훅이 다시 계산하지 않고 `scorecard.stages.approval_is_valid` 를 불러 판정한다. 판정은 명령이 단계 명령이고 실행 이름(또는 경로)을 가리킬 때만 한다.
- 유효성 판정이 실패하면 훅 함수 안에서 예외를 잡아 막는다(fail-closed). `guard.main` 은 예외를 통과시키는 구조라 함수 밖으로 올리지 않는다. 테스트로 고정했다(`HookStageCommandTest.test_undecidable_validity_blocks_inside_the_hook`, `test_main_returns_block_exit_code_when_validity_fails`).
- `init --force` 는 지금처럼 파일 존재 기준이다(무효 승인까지 지우므로 더 엄격하게 둔다).
- `import-baseline` 은 보호 트리 `scorecard/baseline/` 를 다시 쓰므로 훅이 항상 막고, CLI 는 `v1.5` 를 쓰는 유효 승인 실행이 있으면 에이전트를 거부한다.
- 사람이 판단을 고친 뒤 에이전트의 `calculate` 가 무효 승인 파일을 지울 때도 `revocations.jsonl` 에 원인(무효 승인 정리)을 남긴다.

조율자가 지시서에 같은 내용을 반영했다(`8204577`, 병합으로 받음). 기존 두 실행의 `approval_id` 는 재계산 값과 같았다(`43f6583db9108858`, `776a511bf0a9028f`). 그래서 이 항목은 `ask` 하지 않았다.

## 한 일

| 발견 | 커밋 | 바꾼 것 |
| --- | --- | --- |
| V2-3 | `3fe738c` | `guard.py` 보호 경로 대조(파일 도구·쓰기 대상·글롭·상위 폴더) 대소문자 무시. `schema.approval_file_present`·`load_json_strict` 가 폴더 목록에서 이름이 정확히 `approval.json` 일 때만 승인 파일을 읽는다(소유 밖 `build`·`validate`·`compare` 도 이 함수를 지나므로 함께 막힌다). `schema.approval_id_for` 한 곳에서 id 를 만들고 `validate_approval` 이 다시 계산해 대조한다. `stages.status`·`summary` 의 유효 판정도 `approval_is_valid`(형식+해시)로 바꿨다 |
| V2-4 | `ae905d5` | `_shell_violations` 가 쓰기(변경 동사, `/dev/null`·`$null`·`&1` 이 아닌 리다이렉션, `xargs <변경 동사>`, `git checkout` 계열)를 하나라도 보면 따옴표 안·`$(…)`·백틱·변수 대입값(`NAME=`, `export NAME=`, `$name =`, `$env:NAME =`)을 훑는다. `bash`·`sh`·`zsh`·`powershell`·`pwsh`·`cmd`·`awk`·`dd` 등은 인터프리터 규칙(보호 경로를 담기만 해도 차단) |
| V2-1 | `08f2c13` | `stages.protect_approved_run(slug, action, any_approval=False)`. 판정은 `agent_session_markers` 한 곳. `revise_judgment`·`confirm`·`calculate`·`draft`·`research`·`review_template(force)`·가격 `collect`(dry-run 제외)·`init_run(force, any_approval=True)` 가 부른다. 에이전트는 거부, 사람은 경고 뒤 진행. `calculate` 가 승인 파일을 지우면 `[알림]` 을 출력하고 `revocations.jsonl` 에 `revoked_by: "calculate"` 와 원인(`유효했던 승인을 …` 또는 `무효 승인 정리: …`)을 남긴다. `stages.protect_baseline_consumers` 를 CLI `import-baseline` 앞에서 부른다. 훅 `_stage_on_approved` 는 맨 이름·`output/<이름>` 을 폴더로 풀어 유효 승인이면 막고, `import-baseline` 은 항상 막는다 |
| V2-2 | `4f7b8ad` | `_inputs_from_run` 이 대상 기업의 트리거와, 판단·트리거가 인용한 근거 항목을 확정 상태 그대로 옮긴다(인용되지 않은 근거는 옮기지 않는다). `_check_carried_refs` 가 쓰기 전에 출처·근거·트리거·판단 교차 참조를 돌려, 맞지 않으면 폴더를 만들지 않고 멈춘다 |
| V2-5 | `351c58c` | `scorecard_cli.py` confirm·judge 뒤 안내와 다음 명령, judge 도움말, `server/approvals.js` 판단 수정 뒤 안내를 `research → calculate → draft → review` 로. stages 주석 두 곳도 맞췄다 |

테스트는 `tests/test_lane_n_fixes.py`(새 파일, 16건)와 `tests/test_hooks_write_forms.py`(6건: 대소문자 4, 옛 쓰기 형태·읽기 통과 2)에 더했다. 판단 수정·근거 확정을 승인된 샌드박스 실행에서 부르던 기존 테스트 두 건(`test_approval_commands.ApproveRevokeTest.test_end_to_end`, `test_judge.HistoryAndHashTest.test_only_judgments_hash_moves_and_approval_becomes_invalid`)은 승인 페이지(사람 세션) 흐름이라 그 호출만 `human_env()` 로 감쌌다. `approval_id` 에 임의 값 `"x"` 를 쓰던 형식 테스트 두 건은 `approval_id_for` 값으로 바꿨다. 옛 안내 문구를 단언하던 두 건은 새 문구로 바꿨다.

## 재현 전후 (사본, 에이전트 표지 `CLAUDECODE=1`)

### V2-1 단계 명령

| 장면 | 수정 전 (`ef361a3`) | 수정 후 (`6126a63`) |
| --- | --- | --- |
| obsreg `judge` | exit 0, `valid=False`, judgments `2403fb37…→a42fad70…` | exit 1 `[FAIL] 에이전트 세션(CLAUDECODE)에서는 승인이 유효한 실행 … 에서 판단 수정(judge)할 수 없다`, judgments 그대로, `valid=True` |
| obsreg 이어서 `calculate` | exit 0, 승인 파일 삭제, 출력·기록 없음 | exit 1 거부, 승인 유효 |
| baseline `calculate` | exit 0, `results.json 4eb8c7d7…→20d7d87c…`, 승인 삭제, 기록 없음 | exit 1 거부, `results.json 4eb8c7d7…` 그대로, 승인 유효 |
| obsreg `research`·`draft`·`review-template --force`·`collect --kind prices` | 모두 exit 0, 바뀐 파일 `research.md`·`draft.md`·`review.md`, `valid=False` | 모두 exit 1 거부, 바뀐 파일 없음, `valid=True` |
| `import-baseline`(에이전트) | exit 0, `import-report.md 0a879ebc…→ae35ea0f…` | exit 1 `기준선 v1.5 를 다시 이관할 수 없다 … ['ai-scorecard-2026-09-baseline', 'ai-scorecard-2026-09-obsreg']`, 파일 그대로 |
| 사람 `judge` → 에이전트 `research`·`calculate` | 셋 다 exit 0, 승인 파일 삭제, `revocations=[]` | judge 는 `[경고]` 뒤 exit 0(`valid=False`), research·calculate 는 exit 0(무효 승인이라 막지 않음), calculate 가 `[알림] … approval.json 을 지웠다(무효 승인 정리: …)` 출력, `revocations=['calculate']` |
| 사람 baseline `calculate` | exit 0, 승인 삭제, 출력·기록 없음 | `[경고]` 뒤 exit 0, 승인 삭제, `revocations=['calculate']`(원인 "유효했던 승인을 재계산 결과가 바꿔 지웠다") |

`confirm` 은 obsreg 에 근거 파일이 없어 수정 전후 모두 `근거 파일이 없다` 로 멈췄다. 유효 승인 실행에서의 거부는 샌드박스 테스트(`ApprovedRunStageTest`)로 확인했다.

### V2-1 훅 (실제 보호 실행, Bash·PowerShell 같음)

| 명령 (`uv run … scorecard_cli.py` 생략) | 수정 전 | 수정 후 |
| --- | --- | --- |
| `judge <obsreg> …`, `calculate <baseline>`, `draft <obsreg>`, `research <baseline>`, `review-template <obsreg> --force`, `confirm <obsreg> …`, `collect <obsreg> [--kind prices]` | allow | block |
| `import-baseline` | allow | block |
| `collect <obsreg> --kind news`, `status`, `summary --json`, `diff`, 없는 실행의 `calculate` | allow | allow |

훅 프로세스로 잰 판정 시간은 단계 명령 약 0.21초, 그 밖의 명령 약 0.14초다.

### V2-3

| 장면 | 수정 전 | 수정 후 |
| --- | --- | --- |
| Write `…/Approval.json`·`…/approval.JSON`·`.ENV`·`.Env.local`, `echo x > .ENV` | allow | block |
| obsreg 사본에 `Approval.json`(summary 해시, id `0000…`) 을 써 넣음 | `approval=True valid=True`, `build_report` exit 0, `report.html` 생성 | `approval=False`, `build_report` exit 1(`승인 파일은 이름이 정확히 approval.json 이어야 한다 … ['Approval.json']`), `report.html` 없음 |
| 같은 파일을 `approval.json` 으로 바꿈(id 임의) | `valid=True`, build exit 0 | `valid=False`, build exit 1(`approval_id '0000000000000000' 가 … 다시 계산한 값 '776a511bf0a9028f' 와 다름`) |

### V2-4 (옛 판정 대조 표의 사례, `<P>` = 보호 실행 폴더)

`RUN=<P>; sed -i …`, `RUN=<P> && rm -rf "$RUN"`, `export RUN=<P>; echo x > $RUN/draft.md`, `RUN=<P>; mv …`, `RUN=<P>; cp /tmp/x $RUN/draft.md`, `RUN=<P>; truncate …`, `rm $(echo <P>/draft.md)`, `sh -c "echo x > <P>/draft.md"`, `bash -c …`, `awk 'BEGIN{print "x" > "<P>/draft.md"}'`, `echo x | dd of=<P>/draft.md`, `$run = '<P>'; 'x' > "$run/draft.md"`, `powershell -Command "Set-Content <P>/draft.md x"`, `cmd /c "del <P>\draft.md"` 가 수정 전에는 모두 allow, 수정 후에는 모두 block 이다(백틱 `rm \`echo …\`` 는 수정 전에도 block). 같은 사례를 `tests/test_hooks_write_forms.py::WriteFormsTest.test_old_blocked_forms_blocked_again` 에 넣었다.

### F-7 회귀 확인 (수정 전후 모두 allow)

`cat <P>/approval.json; echo done`, `head -5 <P>/results.json`, `rg -n "approval_id" <P>`, `git show HEAD:<P>/approval.json`, `git diff HEAD -- <P>`, `Get-Content <P>/approval.json`, `cp -r <P> /tmp/obsreg-copy`, `rg -n "approval.json" scripts 2>/dev/null`, `cat <P>/results.json > /tmp/x.json`, `Copy-Item -Path <P>/approval.json -Destination C:/tmp/a.txt`, `git log --oneline -- "<P>"`, `git commit -m "approval.json 처리 수정"`. `rm <P>/approval.json` 은 전후 모두 block.

### V2-2

| 장면 | 수정 전 | 수정 후 |
| --- | --- | --- |
| 근거를 인용한 판단(nvidia F1, `EV-nvidia-001` 확정)이 있는 실행을 `init --from-run` | 성공, 새 실행에 `evidence/`·`triggers.json` 없음 | 성공, 반환 키에 `evidence`·`triggers`, 두 파일 생성 |
| 새 실행 `research` | `SchemaError: 교차 참조: nvidia.F1 의 evidence_ids ['EV-nvidia-001'] 가 evidence.json 에 없음` | 성공 |
| 새 실행 `calculate` | (research 없음으로 멈춤) | 성공, nvidia F1 점수 1 |
| 이전 실행의 근거를 비운 뒤 `init --from-run` | 성공(폴더 생김) | `SchemaError: init --from-run …: 이어받은 입력의 교차 참조가 맞지 않아 실행을 만들지 않았다 — triggers[0]: evidence.json 에 없는 evidence_ids ['EV-nvidia-001']`, 폴더 없음 |

## 검증 명령과 결과 (병합 `6126a63` 뒤, 이 워크트리)

| 명령 | 결과 |
| --- | --- |
| `uv run --frozen python -X utf8 -m unittest discover -s tests -t .` | 1168건 · OK · 건너뜀 13 (기준 1146건 OK · 건너뜀 13 에서 새 테스트 22건이 늘었고 실패·오류 0) |
| `uv run --frozen pytest -q` | 1155 passed · 13 skipped · 2281 subtests passed |
| `npm run check` | 통과 |
| `npm run test:node` | tests 15 · pass 15 · fail 0 |
| `scorecard_cli.py status ai-scorecard-2026-09-baseline` / `…-obsreg` | 둘 다 `approval: true`, `approval_valid: true` |
| `git diff --quiet HANSOLJJ/revision_checker -- output scorecard/history.csv scorecard/rules` | 변경 0 |
| `results_hash` (저장 값, 통합 브랜치와 대조) | baseline `0942c342f010…` · obsreg `4a3f6c05b206…` 같음 |
| `git diff --stat HANSOLJJ/revision_checker...HEAD` | 소유 파일 12개만(`scripts/hooks/{guard.py,README.md}`, `scripts/scorecard/{schema.py,stages.py}`, `scripts/scorecard_cli.py`, `server/approvals.js`, `tests/` 6개) |

통합 브랜치 merge 는 충돌 없이 됐다(`6126a63`, 레인 P 문서와 조율자 계약 정정을 받음).

## 소유 밖에서 발견한 것 (고치지 않음)

1. `scripts/build_report.py`·`scorecard/render_html.py` 는 승인 파일 이름이 틀리거나 `approval_id` 가 다르면 `SchemaError` 를 잡지 않아 추적 출력으로 끝난다(exit 1 이라 빌드는 막힌다). `awaiting_user` 처럼 한 줄로 알리면 읽기 쉽다.
2. `scorecard/baseline_import.import_baseline` 함수 본체에는 승인 실행 검사가 없다. 판정은 CLI(`cmd_import_baseline`)와 훅(명령 차단)에만 있어, import 로 함수를 직접 부르면 지나간다. 본체에 `stages.protect_baseline_consumers` 를 부르려면 `baseline_import.py` 소유가 필요하다.
3. `scorecard/compare.approval_state`(`diff` 의 덤 항목)는 `validate_approval` 을 그대로 부르므로, 실행 폴더에 손으로 쓴 승인(임의 `approval_id`)이 있으면 `diff` 전체가 `[FAIL]` 로 멈춘다. 무효로 표시하는 편이 낫다.
4. `init --force` 가 승인 파일을 지울 때는 `revocations.jsonl` 에 남기지 않는다(지시서 범위가 `calculate` 뿐이었다). 같은 `_append_revocation` 으로 남길 수 있다.

## 남긴 것

- 훅은 경로를 조각내 이어 붙이는 쓰기(`D=scorecard/rules; rm $D/v1.7.json`, `Join-Path`)와 `Invoke-Expression`·스크립트 블록은 가리지 못한다. `scripts/hooks/README.md` 의 "아직 하지 않은 것" 에 적었다.
- 쓰기가 있는 명령은 따옴표 안의 보호 경로를 읽기 인자로 써도 막는다(`grep "approval.json" -r . > /tmp/out`). README 에 적었다.
- 훅은 유효성 판정을 위해 단계 명령일 때만 `scorecard` 를 가져온다. 다른 명령에서는 가져오지 않는다.
- 문서(`README.md`·`AGENTS.md`·`docs/**`·`.claude/**`)는 고치지 않았다(레인 P).

## 최종 커밋

이 보고서 커밋 직전 HEAD 는 병합 커밋 `6126a63` 이다. 보고서를 담은 최종 커밋 SHA 는 `worker_done` 과 조율자 터미널 안내에 적는다.
