# 레인 V2: 통합 브랜치 독립 재검증 보고서 (2026-10-01)

에이전트: Claude Fable 5.1. 대상: 첫 검증 기준점 `51873f8` 뒤에 통합 브랜치 `HANSOLJJ/revision_checker` 에 병합된 변경 전체(레인 H·I·M·J·K·T·L 과 조율자 커밋, `51873f8..52347a2`). 지시서는 `.agents/plans/evidence-layer-2026-09/dispatch/lane-V2.md` 다.

읽고 재현만 했다. 코드·테스트·문서·기존 실행 파일은 고치지 않았고, 이 보고서가 유일한 변경이다. 재현은 `git archive HEAD` 로 시스템 임시 폴더에 푼 사본에서 했고, 재현 스크립트도 그 임시 폴더에 두었다. 네트워크는 쓰지 않았다(시세는 주입한 가짜 `yfinance`, 요청은 호출되면 예외를 내는 주입 `urlopen`, 그 밖은 `tests/fixtures/`). 승인·취소 명령은 저장소의 두 실행에 돌리지 않았고 사본에서만 돌렸다. `SEC_UA` 값은 읽은 뒤 "있음·영문 여부" 만 확인했고 출력하지 않았다. 훅 판정은 지금의 `scripts/hooks/guard.py` 함수에 페이로드를 직접 넣어 얻었다(그 명령들을 실제로 실행하지 않았다).

## 요약

일곱 축을 실제 명령으로 재현했다. 첫 검증의 F-1~F-7 은 지목된 경로에서는 모두 닫혔다. 판단 수정 기능은 형식 오류에 아무것도 쓰지 않고, 점수 칸 직접 수정을 막고, 수정하면 승인이 반드시 무효가 되며, 승인 페이지의 POST 는 코드·루프백·인자 생성이 설계대로 동작했다. 승인 함수의 에이전트 거부, 수집기의 NaN 건너뛰기·회사별 실패·`SEC_UA` 영문 검사, 레지스트리 변경 뒤 두 실행의 해시 불변도 확인했다.

새로 찾은 발견은 13건이다(medium 4 · low 9). 정상적인 명령 경로에서 미승인 빌드가 나가거나, 승인이 유효한 채 채점 결과가 바뀌는 결함은 없었다. 하드 블록으로 볼 발견은 없다고 판단한다. 다만 승인된 실행을 평범한 단계 명령이 파괴하는 경로(V2-1), 근거를 인용한 판단이 있는 실행을 다음 실행이 이어받지 못하는 결함(V2-2), 보호 훅을 다시 쓰면서 새로 통과하게 된 쓰기 형태(V2-4)는 병합 전에 손보기를 권한다.

## 테스트 러너 결과 (이 워크트리, 변경 없음)

| 러너 | 결과 |
| --- | --- |
| `uv run --frozen python -X utf8 -m unittest discover -s tests -t .` | 1146건 · OK · 건너뜀 13 |
| `uv run --frozen pytest -q` | 1133 passed · 13 skipped · 2139 subtests passed |
| `npm run check` | 통과 |
| `npm run test:node` | tests 15 · pass 15 · fail 0 |

건너뛴 13건은 전부 레인 T 의 `require_raw` 가 원자료 부재로 건너뛴 것이다. 레인 T 보고서가 적은 `WiringSmokeTest` 2건 실패는 이 환경에서 나지 않았다.

## 레인 V 발견 F-1~F-7 해소 표

| 발견 | 판정 | 재현 결과 |
| --- | --- | --- |
| F-1 `init --force` 승인 파괴 | 해소 | 에이전트 세션 CLI 가 `exit 1` 로 거부하고(`--fo` 줄임 포함) 승인이 유효로 남는다. 훅은 맨 슬러그·`output/` 경로·`--fo` 를 Bash·PowerShell 모두 `block` 한다. 사람 세션은 통과하고 경고를 낸다. 같은 피해를 내는 다른 단계 명령은 V2-1 로 따로 적었다. |
| F-2 stage 함수 import 우회 | 해소 | 표지가 있는 프로세스에서 `approve()`·`revoke()` 를 import 로 부르면 `SchemaError` 로 거부된다. `MUSE_TOOL_USE_ID` 하나만 있어도 거부된다. CLI·승인 페이지 소스에 `allow_agent_session` 은 없다. |
| F-3 기준선이 해시·훅 밖 | 일부 | 파일 도구와 셸 쓰기(`>`·`sed -i`·`Set-Content`)는 `block`, 읽기는 `allow` 다. 그러나 `scorecard_cli.py import-baseline` 은 훅도 CLI 도 막지 않고 `scorecard/baseline/v1.5/` 를 다시 쓴다(V2-1). 승인 해시는 여전히 기준선을 담지 않는다(훅 보호를 택한 결정대로다). |
| F-4 안내 문구 | 해소 | draft 뒤 안내가 "승인 대기 보고" 로, plan 템플릿 흐름에 `collect` 가, 모든 "다음" 안내에 `uv run --frozen python -X utf8` 접두가 들어갔다. 문서에서 uv 없는 `python scripts/` 호출은 0건이다. 판단 수정 뒤 안내에 새 누락이 있다(V2-5). |
| F-5 locale | 해소 | `ko` → `gl=KR&ceid=KR:ko`, `xx`·빈 값·`-US` 는 `ValueError`. `ko-` 처럼 끝이 `-` 인 값은 통과해 `hl=ko-` 가 된다(영향이 작은 잔여). |
| F-6 문서 불일치 | 해소 | 옛 경로(`scorecard/runs/`, `reviews/<slug>.md`), "저장소 밖 읽기 전용" 서술, memory topic 목록, README 훅 표가 지금 상태로 바뀌었다. |
| F-7 읽기 명령 오탐 | 해소 | `cat …/approval.json; echo done`, `head`, `rg`, `git show`, `git diff`, `Get-Content`, 보호 실행을 밖으로 복사하는 `cp -r` 가 `allow` 다. `rm …/approval.json` 은 `block` 이다. 이 수정이 쓰기 형태 일부도 함께 통과시키게 됐다(V2-4). |

F-1·F-2 재현 출력(사본, 에이전트 표지 네 개가 있는 프로세스)은 다음과 같다.

```
에이전트 CLI init --force → exit 1: [FAIL] 에이전트 세션(CLAUDECODE, CLAUDE_CODE_ENTRYPOINT, ORCA_AGENT_LAUNCH_TOKEN, AI_AGENT)에서는 승인된 실행 output/ai-scorecard-2026-09-obsreg 를 --force 로 덮어쓸 수 없다. …
사후: approval=True valid=True results=True html=True
사람 CLI init --force → exit 0: … [경고] 승인된 실행을 --force 로 덮어써 승인 기록이 지워졌다(approval.json 삭제). …
표지 있는 프로세스 approve() import 호출 → exit 1 (stages.py:715 SchemaError) · 사후: approval=False
표지 있는 프로세스 revoke() import 호출 → exit 1 (stages.py:748 SchemaError) · 사후: approval=True valid=True
MUSE 표지만 있는 프로세스 revoke() → exit 1 · 사후: approval=True valid=True
```

---

## 새로 찾은 발견

### V2-1 [medium] 승인된 실행을 가리키는 단계 명령이 훅·CLI 제지 없이 승인을 무효로 만들거나 지운다

- 위치: `scripts/scorecard/stages.py:559-563`(`calculate` 가 결과 해시가 다르면 `approval.json` 을 unlink), `scripts/scorecard_cli.py:280`(`cmd_judge`)·`:200`(`cmd_calculate`)·`:103`(`cmd_import_baseline`, 승인·세션 검사 없음), `scripts/hooks/guard.py:435-436`(`uv run` 명령은 보호 경로 **문자열** 이 있을 때만 막음)·`:467-483`(실행 폴더를 슬러그로 푸는 판정은 `init --force` 하나뿐).
- 재현(사본 루트에서 에이전트 표지가 있는 프로세스로 `python -X utf8 scripts/scorecard_cli.py <아래 인자>`).

```
== 승인·빌드된 obsreg 사본: judge → calculate
사전: approval=True valid=True · .lock 없음
judge ai-scorecard-2026-09-obsreg --company nvidia --factor F1 --set score=1 --reason 재현 --by 사용자 → exit 0
사후: approval=True valid=False · judgments 2403fb37… → a42fad70… · .lock 생김
calculate ai-scorecard-2026-09-obsreg → exit 0 (승인 삭제를 알리는 출력 없음)
calculate 뒤: approval=False · approval.json 없음 · revocations.jsonl 없음

== baseline 사본: calculate 하나만
사전: approval=True valid=True · results.json 4eb8c7d7…
calculate ai-scorecard-2026-09-baseline → exit 0: results … (hash 200d7b01afc3cf39…)
사후: approval=False · approval.json 없음 · results.json 20d7d87c… · revocations.jsonl 없음

== obsreg 사본: research · draft · review-template --force (입력 무변경)
세 명령 모두 exit 0 · 바뀐 파일 ['draft.md', 'research.md', 'review.md'] · approval=True valid=False

== 기준선: import-baseline --html <고친 사본>
exit 0 · 바뀐 파일 ['import-report.md', 'scores.json'] · obsreg 승인은 valid=True 그대로
```

- 훅 판정(실제 보호 슬러그로 `protect_sensitive_files`·`enforce_plan` 호출, Bash·PowerShell 같음).

```
protect=allow plan=allow | uv run … scorecard_cli.py judge ai-scorecard-2026-09-obsreg --company nvidia --factor F1 --set score=5 …
protect=allow plan=allow | uv run … scorecard_cli.py calculate ai-scorecard-2026-09-baseline
protect=allow plan=allow | … draft · research · review-template --force · confirm · collect --kind prices (두 실행 모두)
protect=allow plan=allow | uv run … scorecard_cli.py import-baseline [--html … --md …]
```

- 왜 결함인가. 레인 H 는 "승인 파괴는 사람만 한다" 를 `init --force` 에만 넣었다. 단계 명령은 맨 슬러그를 받으므로 보호 경로 문자열이 명령에 없고, 훅은 통과시킨다. 그 결과 에이전트 세션이 평범한 명령 한 줄로 승인된 실행을 망가뜨린다. 특히 baseline 은 저장 결과와 재계산 결과가 다르다는 것이 알려진 상태(`context-notes.md` 의 "그대로 둔다" 결정)라서, `calculate` 한 번이 `results.json` 을 덮어쓰고 승인 파일을 지운다. 레인 J 의 `judge` 는 이 틈을 판단 파일까지 넓혔다. 이전에는 보호 실행의 `judgments.json` 을 고치려면 파일 도구(훅이 막음)나 임의 Python 이 필요했다. 지워진 승인은 `revocations.jsonl` 에 남지 않고 `calculate` 출력에도 나오지 않는다. 승인이 무효·부재가 되므로 미승인 빌드는 나가지 않고(`build_report` 가 `exit 1`), 파일은 git 이 추적하므로 복구할 수 있다. `calculate` 의 삭제 동작은 `main` 에도 이미 있다(`main:scripts/scorecard/stages.py:304-308`).
- 고치는 방향. 유효한 승인이 있는 실행의 입력·산출물을 바꾸는 단계 함수(`revise_judgment`·`confirm`·`calculate`·`draft`·`research`·`review_template(force)`·가격 `collect`)와 `import_baseline` 이 에이전트 세션이면 `init_run` 과 같은 규칙으로 거부하게 한다. `calculate` 가 승인 파일을 지울 때는 그 사실을 출력하고 `revocations.jsonl` 에 남긴다.

### V2-2 [medium] 근거를 인용한 판단이 있는 실행은 `init --from-run` 으로 이어받으면 다음 실행이 research 부터 멈춘다

- 위치: `scripts/scorecard/stages.py:133-141`(`_inputs_from_run` 이 판단은 한 글자도 바꾸지 않고, 출처는 통째로 옮기지만 `evidence/evidence.json`·`triggers.json` 은 옮기지 않음), `scripts/scorecard/schema.py:1364-1367`(판단의 `evidence_ids` 가 근거 파일에 없으면 교차 참조 실패).
- 재현(사본의 테스트 샌드박스 `FlowBase` 로 근거·트리거가 있는 v1.8 실행을 만든 뒤).

```
confirm EV-nvidia-001 → nvidia F1 에 evidence_ids 를 달고 judge(score=1)
이전 실행 nvidia F1: {'score': 1, 'status': 'new', 'evidence_ids': ['EV-nvidia-001'], 'reviewer': '사용자'}
이전 실행 load_context → 성공
init --from-run → 성공 ['judgments', 'observations', 'plan', 'run', 'sources']
새 실행 파일: ['judgments.json', 'observations.json', 'plan.md', 'run.json', 'sources.json'] | evidence 폴더: False | triggers: False
새 실행 nvidia F1: {'score': 1, 'status': 'new', 'evidence_ids': ['EV-nvidia-001']} | 이력 1
근거 출처가 새 실행 장부에 있음: True
새 실행 research → SchemaError: 교차 참조: nvidia.F1 의 evidence_ids ['EV-nvidia-001'] 가 evidence.json 에 없음
새 실행 judge(다른 판단) → SchemaError: 교차 참조: nvidia.F1 의 evidence_ids ['EV-nvidia-001'] 가 evidence.json 에 없음
```

- 왜 결함인가. 지시서의 물음("다음 실행이 수정된 판단을 출처와 함께 이어받는가")에 대한 답이 갈린다. 근거를 인용하지 않은 판단(기존 obsreg)은 이어받기가 된다. obsreg 사본에서 `judge` 뒤 `init --from-run` 을 돌리면 판단 114건·출처 13건·`revision_history` 가 그대로 옮겨지고, `run.assumptions` 에 "이전 실행의 승인이 무효다(달라진 것: judgments)" 가 적히며, research·calculate 가 돈다. 그러나 새 판단이 확정 근거를 인용하는 것이 근거 계층의 정상 사용이고, 그 경우 `init` 은 조용히 성공한 뒤 다음 실행의 모든 단계(research·calculate·judge)가 교차 참조에서 멈춘다. 출처 장부에는 근거의 출처가 있는데 근거 항목만 없다. 트리거도 옮겨지지 않는다. 이어받기와 근거를 함께 쓰는 테스트는 없다(`tests/test_scorecard_continue_run.py` 만 이어받기를 다룬다).
- 고치는 방향. `_inputs_from_run` 이 판단이 인용한 근거 항목(과 트리거)을 함께 옮기거나, 옮기지 않기로 한다면 `init` 에서 교차 참조를 돌려 그 자리에서 분명한 오류로 멈춘다.

### V2-3 [medium] 승인 파일·`.env` 보호가 대소문자를 구분해, Windows 에서 파일 도구만으로 승인 파일을 만들 수 있다

- 위치: `scripts/hooks/guard.py:178-191`(`_APPROVAL_FILE`·`_is_protected` 가 소문자 `approval.json`·`.env` 만 대조), `scripts/scorecard/schema.py:1430-1446`(`validate_approval` 이 `approval_id` 를 검산하지 않음). 읽는 쪽은 `approval.json` 으로 열고, Windows 파일 시스템은 대소문자를 가리지 않는다.
- 재현.

```
훅 Write output/ai-scorecard-new/approval.json: protect=block
훅 Write output/ai-scorecard-new/Approval.json: protect=allow
훅 Write output/ai-scorecard-new/approval.JSON: protect=allow
훅 Write .ENV: protect=allow · Write .Env.local: protect=allow · echo x > .ENV: protect=allow

== obsreg 사본에서 승인 파일·report.html·audit.md 를 지운 뒤
build_report(승인 없음) → exit 1: awaiting_user: 사용자 승인 없음 …
`summary --json` 의 hashes 를 담아 `Approval.json` 을 직접 씀(approval_id 는 임의 값 0000000000000000)
써 넣은 뒤: approval=True valid=True
build_report → exit 0: … [PASS] report contract: ai-scorecard-2026-09-obsreg · report.html 생성: True
```

- 왜 결함인가. `**/approval.json` 은 에이전트가 파일 도구로 승인 파일을 쓰지 못하게 하는 둘째 방어선이다. 승인 파일이 아직 없는 실행에서는 이름의 대소문자만 바꾸면 훅이 통과시키고, 승인 검증은 그 파일을 유효한 승인으로 읽는다. 필요한 해시는 `summary --json` 이 그대로 내주고 `approval_id` 는 검산되지 않으므로 Python 없이 Write 도구 한 번으로 성립한다. 첫 방어선(승인 함수의 거부)은 파일을 직접 쓰는 경로에 닿지 않는다. 문서가 최종 보증으로 든 "git 이력에서 승인 파일 변경 확인" 도 `approval.json` 으로 찾으면 `Approval.json` 을 놓친다. 승인 파일이 이미 있으면 경로가 실제 이름으로 풀려 세 표기 모두 `block` 이고, 보호 실행 두 폴더는 폴더째 보호라 막힌다(둘 다 확인했다). 이 틈은 `51873f8` 이전부터 있었고 첫 검증이 잡지 못했다. 에이전트가 의도적으로 움직여야 성립한다.
- 고치는 방향. 훅의 보호 경로 대조를 대소문자 무시로 바꾸고(`approval.json`·`.env*`·보호 트리 전부), 승인을 읽는 코드는 폴더 목록에서 이름이 정확히 `approval.json` 인지 확인한다. `approval_id` 를 검증에서 다시 계산해 대조하면 임의 값도 걸러진다.

### V2-4 [medium] 보호 훅을 쓰기 대상 판정으로 바꾸면서, 이전에는 막히던 쓰기 형태가 통과하게 됐다

- 위치: `scripts/hooks/guard.py:405-464`(`_shell_violations` 가 토큰으로 나눈 쓰기 대상만 대조), `:218-223`(대조는 리터럴 경로). 이전 구현은 `51873f8:scripts/hooks/guard.py` 의 `_MUTATING`·`_REDIRECT` 정규식이다.
- 재현. `git show 51873f8:scripts/hooks/guard.py` 를 임시 폴더에 풀어 같은 페이로드를 옛 함수와 지금 함수에 넣었다(`<P>` 는 `output/ai-scorecard-2026-09-obsreg`, Bash·PowerShell 같음).

```
옛=block 지금=allow | RUN=<P>; sed -i s/a/b/ $RUN/draft.md
옛=block 지금=allow | RUN=<P> && rm -rf "$RUN"
옛=block 지금=allow | export RUN=<P>; echo x > $RUN/draft.md
옛=block 지금=allow | RUN=<P>; mv $RUN/draft.md $RUN/draft.bak
옛=block 지금=allow | RUN=<P>; cp /tmp/x $RUN/draft.md
옛=block 지금=allow | RUN=<P>; truncate -s 0 $RUN/results.json
옛=block 지금=allow | rm $(echo <P>/draft.md)
옛=block 지금=allow | sh -c "echo x > <P>/draft.md" · bash -c "echo x > <P>/draft.md"
옛=block 지금=allow | awk 'BEGIN{print "x" > "<P>/draft.md"}'
옛=block 지금=allow | echo x | dd of=<P>/draft.md
옛=block 지금=allow | $run = '<P>'; 'x' > "$run/draft.md"
```

- 왜 결함인가. 이전 구현은 "변경 동사나 리다이렉션이 있고 보호 경로 문자열이 명령 어디에든 있으면 막는다" 였다. 그래서 읽기 명령까지 막았고(F-7), 레인 H 가 "쓰기 대상일 때만 막는다" 로 바꿨다. 그 과정에서 경로가 변수·명령 치환·따옴표 안에 있는 쓰기는 보호 경로 문자열이 명령에 그대로 있어도 통과하게 됐다. 실행 폴더를 변수에 담아 쓰는 것(`RUN=<실행 폴더>; … $RUN/draft.md`)은 에이전트가 흔히 쓰는 꼴이라, 의도하지 않은 수정도 이 경로로 훅을 지난다. 레인 H 보고서는 남긴 형태가 "모두 수정 전에도 통과하던 형태" 라고 적었는데, 위 형태들은 수정 전에는 막혔다. `scripts/hooks/README.md` 의 한계 목록은 PowerShell 변수만 적고 있다. 승인 해시(첫 방어선)는 유지되므로 고친 뒤에는 승인이 무효가 된다.
- 고치는 방향. 쓰기 명령(변경 동사·리다이렉션)이 하나라도 있는 명령에서 변수 대입·명령 치환·따옴표 안 문자열에 보호 경로가 나오면 이전처럼 막는다(읽기만 하는 명령은 지금처럼 통과). 중첩 셸(`bash -c`·`sh -c`·`powershell -Command`·`cmd /c`)과 `awk`·`dd` 는 인터프리터 규칙(보호 경로를 담기만 해도 차단)으로 묶는다. `tests/test_hooks_write_forms.py` 에 옛 판정과의 대조 사례를 더한다.

### V2-5 [low] 판단을 고치거나 근거를 확정한 뒤 안내대로 `calculate → draft → review` 만 돌리면 승인이 거부된다

- 위치: `scripts/scorecard_cli.py:270-271`(confirm 안내)·`:308-309`(judge 안내), `server/approvals.js:823`(승인 페이지 안내), `AGENTS.md:19`, `README.md:78·86`, `.claude/skills/score-approve/SKILL.md:32·36`, `.claude/skills/score-review/SKILL.md:37`, `.claude/skills/score-collect/SKILL.md:43`, `docs/scorecard/structure.md:137`. 검증은 `scripts/scorecard/validate.py:145-150` 이 한다.
- 재현(샌드박스, 리뷰 pass·승인 상태에서 시작).

```
== 판단 수정 뒤
CLI 안내: judgments 해시가 바뀌었다(…). 점수는 아직 그대로다 — calculate → draft → review 를 다시 돌린 뒤 승인한다: …
안내대로 calculate → draft → review 뒤 승인: 거부 — 승인 전 계약 검증 실패: …/research.md 가 현재 입력 해시와 다름 — research 를 다시 생성
research 를 다시 돌린 뒤 승인(리뷰는 그대로): 승인됨 | valid=True
== 근거 확정 뒤
안내대로 calculate → draft → review 뒤 승인: 거부 — …/research.md evidence_hash 가 현재 evidence 와 다름 — research 를 다시 생성
research 를 다시 돌린 뒤 승인(리뷰는 그대로): 승인됨 | valid=True
```

- 왜 결함인가. `research.md` 는 입력 해시를 머리에 담고 승인 전 계약 검증이 그것을 대조한다. 안내 문구 세 곳과 문서 여덟 곳이 `research` 를 빼고 적어서, 문면대로 따르면 사람이 승인 페이지에서 승인을 누르는 단계에서 거부를 본다. 리뷰 스킬 5단계(`validate_report_contract.py`)를 돌리는 에이전트는 그 전에 같은 오류를 보므로 실제 피해는 한 번 되돌아가는 정도다.
- 고치는 방향. 안내와 문서를 `research → calculate → draft → review` 로 맞춘다.

### V2-6 [low] NaN 종가를 건너뛴 날에 조회하면 시총 관측이 조회 시점의 벤더 값으로 `verified` 기록되고, 관측에 건너뛴 사실이 남지 않는다

- 위치: `scripts/scorecard/collect_prices.py:32-33·65-66`(건너뛴 날짜는 반환값에만 남음), `:70-76`(조회일과 종가일이 하루 이내면 벤더 시총을 그날 값으로 봄), `:112-114`.
- 재현(가짜 `yfinance`: 어제 종가 101.0, 오늘 행은 NaN, 벤더 시총 4.0e12, 조회일은 오늘).

```
price_as_of(run)=2026-10-01 close_date=2026-09-30 fetched_at=2026-10-01 skipped=['2026-10-01']
price 관측 as_of=2026-09-30 value=101.0
market_cap 관측 as_of=2026-09-30 value=4.000e+12 basis={'method': 'vendor_market_cap', 'shares_outstanding': 24000000000, 'fetched_at': '2026-10-01'}
관측에 건너뛴 날짜 기록: False
ADR(tsmc) market_cap status=verified method=vendor_market_cap
```

- 왜 결함인가. 종가가 비어 있는 행이 있다는 것은 그 거래일의 일봉이 이미 생겼다는 뜻이므로, 그때의 벤더 시총은 건너뛴 날의 가격을 반영한 값이라고 보는 것이 맞다(이 부분은 추론이다. 실데이터로 대조하지 못했다). 그러면 종가는 하루 앞 날짜인데 시총은 건너뛴 날 값이 같은 `as_of` 로 `verified` 기록된다. ADR 도 `collection_failed` 가 아니라 `verified` 가 된다. 건너뛴 날짜는 수집 요약 행(표준 출력)에만 있고 `observations.json` 에는 없어, 나중에 이 어긋남을 알 길이 없다. 레인 M 이 실측한 경우(다음 날 조회, 간격 2일)는 `price_x_shares` 로 떨어져 영향이 없다. 건너뛰기 자체는 지시서대로 동작한다.
- 고치는 방향. `skipped_nonfinite_close` 가 있으면 벤더 시총을 그날 값으로 보지 않고(보통주는 `price_x_shares`, ADR 은 `collection_failed`), 건너뛴 날짜를 관측 `basis` 에 남긴다.

### V2-7 [low] 부분 실패 뒤 다시 수집한 회사의 가격 관측이 가리키는 출처 항목에 그 회사가 없다

- 위치: `scripts/scorecard/stages.py:403`(`SRC-YF-<기준일>` 을 이번에 기록한 티커로 만듦), `scripts/scorecard/evidence_lib.py:213-220`(`upsert_sources` 는 같은 id 가 있으면 바꾸지 않음).
- 재현(샌드박스, 1차는 TSM 시세가 비정상인 파일, 2차는 정상 픽스처).

```
1차: nvidia collected · tsmc failed(observations[47]: 값이 null 이면 status 는 verified 일 수 없음) · openai skipped_unlisted
1차 뒤 출처: https://finance.yahoo.com/quote/NVDA None
2차: nvidia failed(같은 (기업, 지표, 기준일) 관측이 이미 있다 …) · tsmc collected
2차 뒤 가격 관측: nvidia.market_cap/price.2026-09-29, tsmc.market_cap/price.2026-09-29
2차 뒤 출처: https://finance.yahoo.com/quote/NVDA None | accessed_at 2026-09-30T00:00:00Z
```

- 왜 결함인가. 회사별 실패(레인 J)는 지시서대로 동작한다. 한 회사의 실패가 나머지를 막지 않고, 다시 돌리면 빠진 회사만 들어간다. 그러나 2차에 들어간 tsmc 관측은 `url` 이 NVDA 시세 페이지이고 `publisher_url` 목록이 없으며 조회 시각이 1차 시각인 출처를 가리킨다. 한 번에 전부 성공했을 때는 모든 티커가 `publisher_url` 에 실린다(`collect_prices.py:157-158`). 또 이미 기록된 회사가 2차에서 `failed` 로 표시돼 실패와 중복을 구분하기 어렵다.
- 고치는 방향. 같은 `SRC-YF` 항목이 있으면 `publisher_url` 에 새 티커를 더한다. 이미 기록된 회사는 `failed` 가 아닌 별도 상태(예: `skipped_existing`)로 낸다.

### V2-8 [low] 테스트 파일을 직접 실행하면 사용자의 실제 설정 파일을 읽고 SEC 요청을 시도한다

- 위치: `tests/__init__.py:6`(`SCORECARD_DOTENV=""` 는 `tests` 패키지가 임포트될 때만 설정됨), `tests/test_collect_stage.py:58`(샌드박스는 환경변수 `SEC_UA` 만 지움).
- 재현(이 워크트리에서 읽기만, 요청은 주입한 예외로 차단).

```
tests 패키지 임포트 뒤: SCORECARD_DOTENV = ''          (unittest discover · pytest 는 이 경로)
수집기를 쓰면서 tests 패키지를 임포트하지 않는 테스트 파일: ['test_collect_filings.py', 'test_collect_news.py', 'test_collect_prices.py', 'test_collect_stage.py', 'test_evidence_lib.py', 'test_resolve_cik.py']
test_collect_stage.py 를 파일로 직접 불러온 뒤 SCORECARD_DOTENV = None
그때 후보 경로: ['…\\lane-V2\\.env', 'E:\\sourcecode\\01_side_project\\stock-report-harness\\.env']
직접 실행 조건에서 test_filings_without_user_agent 의 수집 결과: {'nvidia': 'failed', 'tsmc': 'skipped_no_cik', 'openai': 'skipped_no_cik'} (테스트 기대값: nvidia=skipped_no_user_agent)
nvidia 오류 종류: 요청하면 안 된다   ← 주입한 예외. 주입이 없었다면 실제 요청이 나갔다
```

- 왜 결함인가. 문서가 정한 두 러너는 실제 설정 파일을 읽지 않는다. 그러나 `python tests/test_collect_stage.py` 처럼 파일을 직접 실행하면 `tests/__init__.py` 가 돌지 않아, 원본 체크아웃의 설정 파일에서 `SEC_UA` 를 읽고 "UA 가 없으면 건너뛴다" 를 보는 테스트가 SEC 로 실제 요청을 보낸다. 여섯 파일이 이 조건에 해당하고 모두 `if __name__ == "__main__"` 진입점이 있다.
- 고치는 방향. 샌드박스(`Sandbox.__init__`)가 `SCORECARD_DOTENV` 를 직접 비우거나 여섯 파일이 `tests` 패키지를 임포트하게 한다.

### V2-9 [low] 그 밖에 보호 훅이 통과시키는 쓰기 형태 (이전에도 통과하던 것)

- 위치: `scripts/hooks/guard.py:197-211`(동사 목록), `:218-223`(경로 앞에 `/` 가 붙으면 보호 경로로 보지 않는 대조), `:453-462`(git 은 `checkout`·`restore`·`reset` 의 정확한 경로 인자만 봄).
- 재현. 레인 J 가 막았다고 한 형태는 전부 `block` 이었다(`Set-Content`·`Remove-Item`·`Out-File`·`find -delete`·`xargs rm`·글롭·`rm -rf output`·`rm -rf .`·`mv output`·보호 경로로의 `cp`·`cd` 뒤 상대 경로·대소문자만 다른 기존 경로). 아래는 옛 훅과 지금 훅 모두 `allow` 인 형태다(`<P>` 는 보호 실행 폴더).

| 갈래 | `allow` 로 나온 명령 |
| --- | --- |
| 레인 H 가 남긴 것 | `dd if=/tmp/x of=<P>/draft.md`, `ln -sf /tmp/x <P>/draft.md` |
| 평범한 `rm` 인데 경로 표기가 다른 것 | `rm $PWD/<P>/draft.md`, `rm "$(pwd)/<P>/draft.md"`, `rm ${PWD}/<P>/draft.md`, `rm output/ai-scorecard-2026-09-{obsreg,baseline}/draft.md` |
| 중첩 셸·다른 인터프리터 | `bash -c 'rm …'`, `powershell -Command "Remove-Item …"`, `pwsh -c …`, `cmd /c del …`, `eval "rm …"`, `perl -e 'unlink …'`, `ruby -e …` |
| git 의 다른 쓰기 | `git rm -f <P>/approval.json`, `git rm -r output`, `git mv`, `git clean -fdx output`, `git checkout HEAD~5 -- output`, `git checkout HEAD~5 -- .`, `git restore --source HEAD~5 output`, `git reset --hard HEAD~5`, `git stash push -- <P>`, `git apply` |
| PowerShell 의 다른 쓰기 | `Tee-Object -FilePath`, `[IO.File]::WriteAllText(…)`, `[System.IO.File]::Delete(…)`, `Export-Csv -Path`, `Invoke-WebRequest -OutFile`, `Expand-Archive -DestinationPath`, `$p = '…'; Remove-Item $p` |
| 그 밖 | `robocopy`, `curl -o`, `tar -xf x.tar -C <P>`, `patch <P>/draft.md` |

- 왜 결함인가. 문서가 적은 "훅은 둘째 방어선" 범위이고 의도적인 동작이 있어야 한다. 그래도 `rm $PWD/output/<보호 실행>/draft.md` 와 중괄호 전개는 보호 경로 문자열이 변경 동사의 인자로 그대로 있는데 통과한다는 점에서 README 의 "변경 동사의 인자가 보호 경로면 막는다" 와 어긋난다. `git checkout <옛 커밋> -- output` 은 보호 실행을 옛 판으로 되돌린다. `.env` 는 쓰기만 보호되고 읽기(`cat .env`·`Get-Content .env`·Read 도구)는 어떤 훅도 막지 않는다.
- 고치는 방향. 보호 경로 대조에서 `$PWD/`·`$(pwd)/`·`${PWD}/` 접두와 중괄호 전개를 풀고, git 판정에 `rm`·`mv`·`clean`·`stash`·`apply` 와 상위 폴더 인자를 더한다. 남기는 것은 `scripts/hooks/README.md` 의 한계 목록에 적는다.

### V2-10 [low] `judge`·`confirm` 의 되돌리기가 `SchemaError` 만 잡고, `--json` 의 중첩 값은 추적 출력으로 끝난다

- 위치: `scripts/scorecard/stages.py:875-880`(`revise_judgment`), `:805-810`(`confirm`), `scripts/scorecard/schema.py:1031`(`inputs[key] in TRI` 가 해시할 수 없는 값에서 `TypeError`).
- 재현.

```
== 쓴 뒤 검증이 SchemaError 가 아닌 예외를 내면(load_context 에 KeyError 주입)
judge → KeyError: '주입한 예외' · 파일 원상 복구: False
== judge --json {"imitation": {"x": 1}}
exit 1 파일 무변경 | TypeError: unhashable type: 'dict'   (Python 추적 출력, [FAIL] 형식 아님)
```

- 왜 결함인가. 쓰기 전 형식 검증은 잘못된 입력에 아무것도 쓰지 않는다(25가지 모두 `exit 1`·파일 무변경). 그러나 파일을 쓴 뒤 도는 전체 검증이 `SchemaError` 가 아닌 예외(파일 잠김, 다른 파일의 형식 밖 값 등)를 내면 고친 `judgments.json` 이 검증되지 않은 채 남는다. 실제로 그런 예외가 나는 조건은 재현하지 못했고 주입으로만 확인했다. `--json` 의 중첩 값은 쓰기 전에 걸러지지만 `[FAIL]` 대신 추적 출력이 나온다.
- 고치는 방향. 되돌리기를 `except Exception` 으로 넓히고 다시 올린다. `_validate_judgment_inputs` 는 값이 문자열·정수인지 먼저 본다.

### V2-11 [low] 수정자 이름은 검증되지 않고 수정 이력에 세션 종류가 남지 않는다. 거부된 `judge` 도 잠금 파일을 남긴다

- 위치: `scripts/scorecard/stages.py:868-870`(`reviewer`·`revised_by` 는 받은 `--by` 그대로), `scripts/scorecard_cli.py:284-285`(잠금 기록이 검증보다 먼저).
- 재현(obsreg 사본, 에이전트 표지가 있는 프로세스).

```
judge … --factor F8 --set score=0 --reason r --by 사용자 → exit 0
기록: {'reviewer': '사용자', 'reviewed_at': '2026-10-01', 'status': 'new'} | 이력 키 ['previous', 'reason', 'revised_at', 'revised_by']
judge … --factor F3 --set score=3 (거부) → exit 1 파일 무변경 | .lock 생김 = True
```

- 왜 결함인가. 승인 페이지는 판단마다 "검토자 · 검토일" 을 보여 주고 사람은 그것을 보고 승인한다. 에이전트 세션이 사람 이름으로 판단을 고쳐도 기록에는 차이가 없다. 설계가 "승인이 아니므로 에이전트도 부를 수 있다" 고 정한 것은 맞지만, 사람 세션과 에이전트 세션 가운데 어느 쪽이 고쳤는지는 이력에서 가려낼 수 없다. 또 에이전트 세션의 `judge` 는 거부돼도 실행 폴더에 `.lock` 을 만든다(보호 실행에도 생긴다. gitignore 대상이다).
- 고치는 방향. 수정 이력 항목에 세션 종류(`agent_session_markers()` 유무)를 남기고 승인 페이지 표에 보인다. 잠금 기록은 수정이 성공한 뒤에 한다.

### V2-12 [low] `require_raw` 는 원자료가 일부만 있을 때 "전 회사 훑기" 단언을 훑지 않은 채 통과시키고, 건너뛴 테스트에는 원자료와 무관한 단언이 섞여 있다

- 위치: `tests/test_scorecard_fix55_stage2.py:65-76`(TSLA 파일 하나만 요구하고 `RAW.glob("*.companyfacts.json")` 전체를 훑음), `tests/test_scorecard_fix58_stage1.py:54-67` 등.
- 재현(사본에 원본 폴더의 원자료 14개를 복사했다. 원본 폴더에는 쓰지 않았다).

```
== 원자료 없음: Ran 13 tests · OK (skipped=13)
== 원자료 전부 있음: Ran 13 tests · OK (13건 모두 ok)
== TSLA 원자료만 있음: OK (skipped=10)
   test_broad_tag_sweep_finds_only_tesla … ok   ← 다른 11개사 파일 없이 "값이 있는 회사는 tesla 하나" 가 통과
```

- 왜 결함인가. 지시서의 두 물음에 대한 답은 다음과 같다. 원자료가 있으면 13건이 실제로 실행되고 통과한다(레인 T 는 가짜 파일 하나로만 확인했다). 건너뛰기 조건은 파일 존재뿐이라 원자료와 무관한 실패를 새로 숨기지는 않는다. 다만 두 가지가 남는다. 첫째, 위 테스트는 원자료가 일부만 있으면 훑지 않은 회사를 "없음" 으로 센 채 통과한다. 둘째, 건너뛴 13건 가운데 여럿은 원자료 단언과 실행 파일 단언을 함께 가진다(예: `test_nvidia_marketable_equity_added` 는 원자료 단언 1개와 `observations.json`·`results.json` 단언 9개). 워크트리에서는 뒤의 단언도 함께 건너뛴다. 대상 파일이 승인 해시와 보호 훅 아래에 있어 영향은 작다.
- 고치는 방향. 전 회사를 훑는 테스트는 훑을 파일 전부를 `require_raw` 에 적는다. 섞인 테스트는 원자료 단언만 건너뛰게 나눈다.

### V2-13 [low] `createApprovals` 를 코드 없이 켜면 코드 검사가 비어 통과한다

- 위치: `server/approvals.js:648`(`code` 기본값 빈 문자열), `:752`(제출 코드와 문자열 비교).
- 재현: `createApprovals({enabled: true, runCli})` 에 코드 없는 `POST /approve/<run_id>/approve` 를 보냈다.

```
code 옵션 없이 만든 라우트에 코드 없는 POST approve: 200 | CLI 호출 ["approve ai-scorecard-2026-09-obsreg --by x --via browser", "summary … --json"]
```

- 왜 결함인가. `server.js` 는 승인 모드에서 항상 6자리 코드를 만들어 넘기므로 지금 배선에서는 일어나지 않는다. 모듈의 기본값이 "검사 없음" 이라, 다른 진입점이 코드를 빼먹으면 조용히 열린다.
- 고치는 방향. `enabled` 인데 코드가 6자리 숫자가 아니면 생성 시점에 예외를 낸다.

---

## 발견이 없는 항목: 확인한 명령과 결과

### 축 2 판단 수정 기능의 안전성

- **고치면 승인이 무효가 된다.** 샌드박스에서 리뷰 pass → 승인 → `judge` 뒤 바뀐 해시 키는 `['judgments']` 하나이고 승인은 `valid: False` 다. obsreg 사본에서도 같다. 값을 원래대로 되돌리는 `judge` 를 한 번 더 해도 이력이 쌓여 바이트가 달라지므로 `valid=False` 로 남는다(이력 3건). 판단을 고쳐도 승인 해시가 그대로인 경로는 찾지 못했다.
- **고친 직후에는 승인할 수 없다.** 사람 세션 사본에서 `judge` 직후 `approve` 는 `exit 1`("results.json 의 input_hashes 가 현재 입력과 다름 — calculate 를 다시 실행")이고, `calculate` 뒤·`draft` 뒤에도 리뷰 해시 불일치로 거부된다. `judge` 뒤 `build_report` 는 `exit 1` 이다.
- **점수 칸 직접 수정은 막힌다.** F3·F5·F7·F9 에 `--set score=N`, `--json {"score": 3}`, `--json {"kind","status","inputs"}` 모두 `exit 1`·파일 무변경이다. F2·F6 은 "고치지 않는다" 로 거부된다. 승인 페이지 POST 에 `factor=F3&score=5` 를 넣어도 CLI 가 거부한다.
- **형식 오류에 아무것도 쓰지 않는다.** 범위 밖 점수, 정수 아닌 점수, 빈 값, 모르는 키, 허용 밖 값, `--set` 형식 오류, 빈 근거, 같은 값, 빈 사유, 빈 수정자, 없는 기업을 포함한 25가지 모두 `exit 1`·`judgments.json` 해시 불변이다.
- **`revision_history` 가 이전 값을 보존한다.** 두 번 고친 뒤 첫 이력의 `previous` 는 원래 7키와 같고, 둘째 이력의 `previous` 는 첫 수정 결과(`status: new`, `reviewer: 갑`)다. `carried_from`·`source_ids` 는 남는다. 승계 점수형 F7(anthropic)은 키 하나나 근거만 주면 거부되고, 두 키를 주면 `matrix`·`score: null` 로 바뀌며 이전 `kind: score`·`-1` 이 이력에 남는다.
- **후보 근거를 인용한 판단의 수정은 되돌려진다.** "새 판단 … 확정되지 않은 근거 … 를 인용" 으로 거부되고 파일이 원상 복구된다.
- **승인 페이지 POST.** 사본의 실제 CLI 에 물려 호출했다. 틀린 코드·코드 없음 403, `company=--json`·`factor=F1 --take-lock` 400, `in_--by` 같은 키는 무시, `score=1 --by evil`·`in_imitation=pass --take-lock` 은 한 인자로 넘어가 스키마가 거부, 근거 `--reason=evil`·사유 `--by=evil`·이름 `--take-lock` 은 글자 그대로 저장됐다. `<b>` 는 이스케이프된다. 틀린 코드 5회 뒤 맞는 코드도 403, 루프백이 아닌 주소 403, `..` 경로와 대문자 run_id 400 이다. 에이전트 표지가 있는 환경에서 띄운 서버의 승인·취소 POST 는 stage 함수가 거부한다.

### 축 3 승인 첫 방어선 (V2-3 은 별건)

- 표지가 있는 프로세스의 직접 호출은 거부된다(위 F-2 출력). `approve --help` 옵션은 `--by --note --via`, `revoke --help` 는 `--by --note` 이고, `server.js`·`server/approvals.js`·`scorecard_cli.py`·`build_report.py` 소스에 `allow_agent_session` 이 없다.
- 문서가 적은 한계는 그대로 열려 있다. 프로세스 안에서 표지 변수를 지우고 `from scorecard.stages import approve as a` 로 부르면 승인이 기록되고(`approved_by='agent-x'`), `allow_agent_session=True` 를 import 로 넘겨도 같다. 두 명령 형태 모두 훅은 `allow` 다. `AGENTS.md:42` 가 "임의 Python 을 실행할 수 있는 에이전트가 작정하면 우회할 수 있다" 로 적은 범위다. 표지 변수 값이 공백뿐이면 사람 세션으로 본다.

### 축 4 수집기 실측 수정 (V2-6·V2-7 은 별건)

- NaN 건너뛰기: 마지막 행 NaN → `close=101.0 close_date=2026-09-29 skipped=['2026-09-30']`, 연속 NaN → 그 앞 유한 종가와 건너뛴 두 날짜, inf 도 건너뜀, 기준일 뒤 행은 무시, 전부 NaN → `ValueError: … 종가 없음(유한하지 않은 종가 2행 건너뜀: …)`.
- 회사별 실패: 위 V2-7 출력의 1차·2차. NaN 이 든 시세 파일은 그 회사만 `failed` 이고 `observations.json` 은 바뀌지 않는다.
- `SEC_UA` 영문 검사: 비영문 값이면 뉴스 3행·공시 1행이 `failed`("SEC_UA 는 영문으로 적는다…"), 주입한 `urlopen` 은 한 번도 불리지 않았고, 오류 문자열·`require_user_agent`·`user_agent_for("news")`·설정 파일 경로·`resolve-cik` CLI 어디에도 값이 실리지 않는다.
- 레지스트리 변경 전후: 지금의 `companies.json` 과 `51873f8` 의 것으로 각각 사본에서 재계산했다. 두 경우 모두 baseline `approval_valid True · stored 0942c342f010 · fresh 200d7b01afc3`, obsreg `approval_valid True · stored 4a3f6c05b206 · fresh 4a3f6c05b206` 이다.
- `resolve-cik --json --from-file <픽스처>` 는 `{rows 14, applied []}` 한 줄이고 상태는 `resolved`·`unlisted` 뿐이다. 뉴스 질의는 meta·apple·oracle 만 `news_queries` 를 쓴다.
- `SEC_UA` 값(전체 문자열과 이메일 부분)은 추적 파일 0곳, `51873f8..HEAD` 커밋 diff 0곳에 나온다(개수만 확인했다).

### 축 5 로컬 설정 파일 읽기 (V2-8 은 별건)

- 이 워크트리에서 후보 경로는 `…\lane-V2\.env`(없음)와 `E:\sourcecode\01_side_project\stock-report-harness\.env`(있음) 순서다. `.git` 파일의 `gitdir` 이 원본의 `.git/worktrees/lane-V2` 를 가리킨다.
- `.git` 파일 모양별 판정(임시 폴더): 절대·상대·끝 슬래시·CRLF 는 원본 루트를 찾는다. 서브모듈(`.git/modules/…`), bare 저장소의 워크트리, BOM, 형식 아님, 빈 파일, `.git` 이 폴더인 일반 체크아웃은 `None` 이다. 엉뚱한 폴더를 읽으려면 `.git` 파일을 고쳐야 하는데 훅이 `.git` 쓰기를 막는다.
- 참고(결함으로 올리지 않음): `.env` 의 `export SEC_UA=…` 줄은 읽지 않고, 값 뒤의 `# 주석` 은 값에 포함된다. 워크트리 `.env` 에 다른 키만 있으면 원본 `.env` 로 넘어간다.

### 축 6 원자료 건너뛰기 (V2-12 참조)

- 원자료가 있을 때 13건이 실행되고 통과하며, 없을 때 사유와 함께 건너뛴다(위 출력).

### 축 7 문서와 코드 일치 (V2-5 는 별건)

- 문서 43개(README·AGENTS·`docs/**`·`.claude/**`·`scripts/hooks/README.md` 등)에서 `scorecard_cli.py <서브커맨드> …` 언급 36건을 뽑아 각 서브커맨드의 `--help` 와 기계로 대조했다. 모르는 서브커맨드 0건, 없는 옵션 0건이다. uv 없는 `python scripts/` 호출은 0건이다. `/score-*` 스킬 12개와 명령 12개의 이름이 같다.
- 스킬·명령·에이전트 정의에서 `approve`·`revoke`·"승인" 이 든 줄을 전부 읽었다. 에이전트에게 승인·취소를 시키는 문구는 없다. 모두 "승인 대기를 보고하고 멈춘다" 로 적혀 있다.
- 남은 문면(코드 동작과 무관): `docs/scorecard/design-guideline.md:353` 의 흐름이 `plan → research → … → awaiting_user → approve → build` 로 `collect` 없이 적혀 있고, `docs/scorecard/open-items.md:54` 가 "`calculate → draft → review → approve` 를 다시 밟아야" 로 적는다. `scripts/hooks/guard.py:1` 주석은 "훅 9개" 인데 실제는 7개다.
- 레인 L 표본: `labeling-2026-10.json` 38건과 `.csv` 38행의 `sample_id` 가 순서까지 같고 유일하며, 라벨 칸은 비어 있다(라벨 대기 상태와 일치).

---

## main 병합을 막아야 할 발견

정상적인 명령 경로에서 미승인 빌드가 나가는 결함과, 승인이 유효한 채 채점 결과가 바뀌는 새 경로는 찾지 못했다. 승인 해시·stage 함수의 거부·계약 검증은 판단 수정 기능을 더한 뒤에도 유지된다. 에이전트가 의도적으로 승인 파일을 만들어 넣는 경로는 V2-3 과 문서가 적은 "임의 Python" 한계로 남아 있다. 따라서 **하드 블록 항목은 없다** 고 판단한다.

병합 전에 손보기를 권하는 것은 다음이다.

1. **V2-1**: 에이전트 세션의 평범한 단계 명령(`calculate <baseline>`, `judge`+`calculate`, `draft`, `import-baseline`)이 승인된 실행의 승인을 지우거나 무효로 만든다. 레인 H 가 `init --force` 로 닫으려던 것과 같은 피해이고, `--force` 같은 표시 없이 일어나며 삭제 기록도 남지 않는다. `calculate` 의 삭제 동작은 `main` 에도 이미 있으므로 병합이 새로 들이는 것은 `judge` 경로다.
2. **V2-4**: 보호 훅이 이전에는 막던 쓰기 형태(실행 폴더를 변수에 담은 `sed -i`·`rm`·`>` 등)를 통과시킨다. 이 브랜치의 변경(레인 H)이 만든 후퇴이고, 에이전트가 의도 없이도 쓰는 꼴이다.
3. **V2-2**: 근거를 인용한 판단이 있는 실행을 이어받으면 다음 실행이 멈춘다. 기존 두 실행에는 영향이 없지만, v1.8 첫 실행 다음에 `init --from-run` 을 쓰는 순간 드러난다. 그 전에 고치면 된다.

V2-3(대소문자 변형 승인 파일)은 의도적인 에이전트 동작이 있어야 성립하고 문서가 적은 한계와 같은 결이어서 병합 차단으로 보지 않는다. 다만 파일 도구 한 번으로 성립하므로 V2-1·V2-4 를 고칠 때 함께 닫기를 권한다. 나머지 low 9건은 병합 뒤에 다뤄도 된다.

## 재현 환경과 최종 커밋

- 사본: `git archive HEAD`(`52347a2`) 를 시스템 임시 폴더에 풀고, 재현마다 새 복사본에서 돌렸다. 사본에서 두 실행은 `approval=True valid=True` 로 시작했다.
- 실행 형식: 워크트리에서 `uv run --frozen python -X utf8 <임시 폴더의 재현 스크립트>`. 스크립트가 사본의 `scripts/scorecard_cli.py`·`scripts/build_report.py` 를 하위 프로세스로 부르거나(에이전트 표지 유지 또는 제거), 사본의 `tests` 샌드박스를 임포트해 돌렸다. 설정 파일은 `SCORECARD_DOTENV=""` 로 읽지 않게 했다(축 5 의 경로 확인과 V2-8 재현만 예외이고, 그때도 값은 출력하지 않았다).
- 통합 브랜치와의 차이: 작업 시작 때 `git log HEAD..HANSOLJJ/revision_checker` 가 비어 있어 merge 할 것이 없었다.
- 이 보고서 커밋(`docs(validation)`)이 유일한 변경이다. 저장소에 임시 파일을 남기지 않았다.
