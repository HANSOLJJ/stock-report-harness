# 레인 N — 재검증 발견 수정: V2-1 · V2-2 · V2-3 · V2-4 (+ V2-5 의 코드 속 안내 문구)

에이전트: Claude Opus 5.5. 의존: 레인 V2 보고서 병합 완료. 공통 규약: `README.md` 를 먼저 읽는다. **발견의 재현 명령과 근거는 `validation/lane-V2-recheck/REPORT.md` 의 V2-1~V2-5 절에 있다. 먼저 읽고, 고치기 전에 사본에서 재현부터 한다.** 레인 P(Antigravity)가 동시에 문서의 V2-5 안내 문구를 고친다. 소유가 겹치지 않는다.

## 확정 계약 (레인 P 와 문서가 이 내용을 기준으로 쓴다. 바꾸려면 ask)

- 판단 수정·근거 확정 뒤 다시 돌릴 단계는 `research → calculate → draft → review` 다.
- 유효한 승인이 있는 실행의 입력·산출물을 바꾸는 단계는 에이전트 세션이면 거부한다(`init --force` 와 같은 규칙, 같은 판정 함수). 훅도 승인 파일이 **유효할 때만** 막는다(무효 승인은 사람이 판단을 고친 뒤의 정상 상태라 에이전트의 재계산을 막지 않는다). 유효성 판정이 실패하면 훅 함수 안에서 막는다(fail-closed). `init --force` 는 파일 존재 기준, `import-baseline` 은 훅이 항상 막는다. (2026-10-01 질문 회신)
- 보호 경로 대조는 대소문자를 구분하지 않는다. 승인 파일은 이름이 정확히 `approval.json` 일 때만 승인으로 읽는다.

## 소유 파일

`scripts/scorecard/stages.py`, `schema.py`, `engine.py`(필요 시), `scripts/scorecard_cli.py`, `scripts/hooks/guard.py`, `scripts/hooks/README.md`, `server/approvals.js`(823행 근처 안내 문구만), 관련 `tests/**`, 보고서. 만지지 않는 것: `README.md`·`AGENTS.md`·`docs/**`·`.claude/**`(레인 P), `output/ai-scorecard-2026-09-*`, 규칙 파일, `history.csv`.

## 고칠 것

1. **V2-1** 승인이 유효한 실행에 대해 입력·산출물을 바꾸는 단계 함수가 에이전트 세션이면 거부한다. 대상: `revise_judgment`(judge), `confirm`, `calculate`, `draft`, `research`, `review_template(force)`, 가격 `collect`, `import_baseline`(기준선을 소비하는 승인 실행이 있으면). 판정은 `init_run` 이 쓰는 함수 하나를 쓴다. 사람 세션은 허용하되 승인이 무효가 된다는 경고를 낸다. `calculate` 가 승인 파일을 지울 때는 그 사실을 출력하고 `revocations.jsonl` 에 남긴다(`revoked_by` 는 "calculate" 처럼 원인을 알 수 있게). 훅도 위 단계 명령이 승인 있는 실행 이름을 가리키면 막는다(맨 실행 이름을 폴더로 풀어 판정).
2. **V2-2** `init --from-run` 이 이전 실행의 판단이 인용한 근거(`evidence/evidence.json` 의 해당 항목)와 트리거(`triggers.json`)를 함께 옮긴다. 옮긴 뒤 교차 참조를 돌려, 맞지 않으면 `init` 에서 분명한 오류로 멈춘다. 근거를 인용한 판단이 있는 실행을 이어받아 research·calculate 까지 도는 테스트를 넣는다.
3. **V2-3** 훅의 보호 경로 대조를 대소문자 무시로 바꾼다(`approval.json`, `.env*`, 보호 트리 전부). 승인을 읽는 코드는 폴더 목록에서 이름이 정확히 `approval.json` 인지 확인한다. `validate_approval` 이 `approval_id` 를 다시 계산해 대조한다. 기존 두 실행의 `approval_id` 가 재계산과 같은지 먼저 확인하고, 다르면 고치지 말고 ask 한다.
4. **V2-4** 쓰기 명령(변경 동사·리다이렉션)이 하나라도 있는 명령에서, 변수 대입·명령 치환·따옴표 안 문자열에 보호 경로가 나오면 막는다. 중첩 셸(`bash -c`, `sh -c`, `powershell -Command`, `cmd /c`)과 `awk`·`dd` 는 인터프리터 규칙(보호 경로를 담기만 해도 차단)으로 묶는다. 읽기만 하는 명령은 지금처럼 통과한다(F-7 회귀 금지). V2 보고서의 옛 판정 대조 표 사례를 `tests/test_hooks_write_forms.py` 에 넣는다.
5. **V2-5 (코드 속 문구만)** `scorecard_cli.py` 의 confirm·judge 뒤 안내와 `server/approvals.js` 의 판단 수정 뒤 안내를 `research → calculate → draft → review` 로.

## 검증

- V2 보고서의 V2-1~V2-4 재현을 사본에서 다시 돌려 전후를 보고서에 붙인다.
- 두 기존 실행 `approval_valid: true`, `output/ai-scorecard-2026-09-*` 변경 0, `results_hash` 불변.
- F-7 회귀 없음: 읽기 명령(`cat`·`rg`·`git show`·`Get-Content` + 보호 경로)은 통과.
- 테스트 기준(unittest 1146건 OK, 건너뛰기 13)에서 실패 0 유지. `npm run check`, `npm run test:node` 통과.
- 보고서 `validation/lane-N-v2-fixes/REPORT.md`. 한국어 커밋, Co-Authored-By 금지, git push 금지, git stash 금지. 통합 브랜치 merge 가 거부되면 보고만.
- 셸 명령 문자열에 보호 경로·승인 명령이 들어가면 훅이 막는다. 필요하면 페이로드를 파일로 만들어 확인한다.
- 완료는 preamble 의 `worker_done`(--outcome 명시) 뒤 조율자 터미널 `term_be1eaaf8-815c-4231-a858-7229d925e5fe` 에 한 줄 안내.
