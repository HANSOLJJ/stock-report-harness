# 레인 V — 통합 브랜치 독립 검증 보고서 (2026-10-01)

에이전트: Claude Fable 5.1. 대상: 통합 브랜치 `HANSOLJJ/revision_checker`(main 대비 58커밋). 읽고 재현만 했고 코드·문서·기존 실행 파일은 고치지 않았다. 임시 스크립트는 시스템 임시 폴더에 두었고 저장소에 남기지 않았다. 네트워크는 쓰지 않았으며 모든 수집 재현은 `tests/fixtures/` 와 주입한 fetch 로 했다. 승인 명령은 실제 두 실행에 대고 돌리지 않았고, 재현은 전부 `git checkout-index` 와 `git archive` 로 푼 사본에서 했다.

## 요약

일곱 축을 실제 명령으로 재현했다. 승인 바이트 무결성·근거 계층 정합·잠금 판정·수집기 시점 처리는 설계대로 동작했다. 이음매에서 새로 찾은 결함은 일곱 건이고, 이 가운데 병합을 하드 블록할 것은 없다고 판단한다. 다만 승인된 실행을 파괴하거나 승인 첫 방어선을 우회하는 경로 두 건(F-1·F-2)은 병합 전에 손보기를 권한다.

## 테스트 러너 결과 (새 워크트리, 변경 없음)

| 러너 | 결과 |
| --- | --- |
| `uv run --frozen python -X utf8 -m unittest discover -s tests -t .` | 1085건 · 실패 1 · 오류 14 |
| `uv run --frozen pytest -q` | 15 failed · 1072 passed · 1806 subtests passed |
| `npm run check` | 통과 (node --check + compileall) |
| `npm run test:node` | tests 10 · pass 10 · fail 0 |

실패·오류 집합은 전부 `tests/test_scorecard_obs_recency.py` 와 `validation/*/_raw` 원자료 부재로, 알려진 기준선과 같다. 내 검증으로 이 집합이 늘지 않았다.

---

## 새로 찾은 결함

### F-1 [medium] `init --force` 가 승인된 실행을 훅·CLI 제지 없이 덮어쓰고 승인을 지운다

- 위치: `scripts/scorecard/stages.py:282`(init 이 `approval.json`·`results.json`·`preview.md` 를 unlink), `scripts/hooks/guard.py:186`(`_MUTATING`), `scripts/scorecard_cli.py:127`(cmd_init, 에이전트 거부 없음).
- 재현: obsreg 사본에서 CLI `init ai-scorecard-2026-09-obsreg --force --as-of 2026-09-17 --title x --request y --rule v1.7` 를 실행했다.

```
init --force 전: approval.json 있음 · approved_by='사용자' · approval_valid=True
CLI init --force → exit 0: plan: output/ai-scorecard-2026-09-obsreg/plan.md
run.json 바뀜 = True · results.json 있음 = False · .lock 있음 = True
init --force 뒤: approval.json 없음
```

- 훅 판정(실제 보호 실행 슬러그로 두 훅을 직접 호출):

```
protect=allow enforce_plan=allow | init --force 바 슬러그
protect=allow enforce_plan=allow | init --force output/ 경로
```

- 왜 결함인가. `protect_sensitive_files` 는 승인된 두 실행 묶음을 지키려고 만든 훅인데, 셸 명령은 변경 동사(`_MUTATING`: cat>, python, rm, mv 등)나 리다이렉션이 먼저 잡혀야 경로 리터럴을 검사한다. `uv run … scripts/scorecard_cli.py init <슬러그> --force` 는 `uv` 로 시작해 `python\b` 앵커에 걸리지 않고 `init` 은 변경 동사 목록에 없어, 경로 리터럴 검사 자체가 돌지 않는다. 게다가 명령이 쓰는 것은 맨 슬러그(`ai-scorecard-2026-09-obsreg`)라 보호 리터럴(`output/ai-scorecard-2026-09-obsreg`)과도 어긋난다. CLI 의 `init` 에는 에이전트 세션 거부가 없다. 결과적으로 에이전트가 승인된 실행의 관측·판단·run 입력을 덮어쓰고 승인 기록을 지울 수 있다.
- 고치는 방향. `init` 이 이미 존재하는 실행을 `--force` 로 덮어쓸 때, 그 실행에 `approval.json` 이 있으면 에이전트 세션에서 거부하거나(`agent_session_markers` 재사용), 훅이 `scorecard_cli.py init … --force <보호 슬러그>` 를 보호 대상으로 인식하게 한다. git 이 이력을 보존하므로 복구는 가능하지만 승인 산출물 보호라는 훅의 목적이 이 경로로 비어 있다.

### F-2 [medium] 승인 첫 방어선(에이전트 거부)이 CLI 명령 계층에만 있어 stage 함수 import 로 우회된다

- 위치: `scripts/scorecard_cli.py:242`(에이전트 거부는 `cmd_approve`·`cmd_revoke` 에만 있음), `scripts/scorecard/stages.py:674`(`approve` 함수 자체에는 거부 없음), `scripts/hooks/guard.py:193`(`_APPROVAL_CMD` 는 리터럴 `scorecard_cli.py approve`·`stages.approve` 만 매칭).
- 재현: 에이전트 표지 네 개(`CLAUDECODE` 등)가 모두 있는 이 세션 프로세스에서 `stages.approve` 를 직접 불렀다.

```
에이전트 표지 ['CLAUDECODE', 'CLAUDE_CODE_ENTRYPOINT', 'ORCA_AGENT_LAUNCH_TOKEN', 'AI_AGENT'] 인 프로세스에서 stages.approve() 직접 호출 → approval.json 생성 · approval_valid=True
```

- 훅을 지나는 명령 형태(실제 보호 슬러그로 두 훅 호출):

```
protect=allow enforce_plan=allow | stages 승인함수 from-import
protect=allow enforce_plan=allow | CLI 서브커맨드 셸 변수 분할
```

- 보강: 표지가 있는 채로 CLI `approve` 는 `exit 1` 로 거부됐고(첫 방어선 동작), `env -u CLAUDECODE -u … approve` 명령은 훅이 리터럴 `approve` 로 막는다. 그러나 표지를 지운 셸에서 CLI `approve` 는 승인을 기록했다(`approved_by='agent-session'`). 표지 제거와 `from scorecard.stages import approve` 를 함께 쓰면 첫 방어선(거부는 `cmd_approve` 에만 있음)과 둘째 방어선(리터럴 매칭)을 모두 지난다.
- 왜 결함인가. 설계는 "훅은 도구 호출 밖을 막지 못한다, 첫 방어선은 CLI 거부" 라고 적는데, 그 거부가 argparse 명령 함수에만 있고 `stages.approve`·`stages.revoke` 본체에는 없다. import 경로 호출자는 첫 방어선을 통째로 건너뛴다.
- 고치는 방향. `agent_session_markers()` 거부를 `stages.approve`·`stages.revoke` 본체로 옮긴다. 테스트는 환경변수나 인자로 opt-in 하게 해 import 경로 호출자도 거부 대상에 넣는다. 훅의 리터럴 매칭은 보완이지 방어선이 아니다.

### F-3 [medium] `scorecard/baseline/` 가 승인 해시와 보호 훅 밖의 재빌드 입력이다

- 위치: `scripts/hooks/guard.py:166-168`(보호 목록에 baseline 없음), `scripts/scorecard/stages.py:640`(`current_hashes` 가 baseline 을 해시하지 않음), `scripts/scorecard/render_html.py:1746`(build 가 `load_baseline` 으로 트리거를 읽음).
- 재현: obsreg 사본에서 `baseline/v1.5/triggers.json` 첫 항목 문자열에 표지를 붙이고 다시 빌드해 원본 빌드와 줄 단위로 비교했다.

```
[baseline_triggers] approval_valid = True
[baseline_triggers] build = 성공
[baseline_triggers] report.html 달라진 줄 2개
   …TAMPERED 🆕 NVIDIA–Hugging Face 클로징 … (트리거 표에 표지가 실림)
```

- 왜 결함인가. obsreg 는 실행 묶음에 `triggers.json` 이 없어 렌더러가 기준선 트리거를 그린다. 그 바이트는 승인 해시(6키)에도 없고 보호 훅의 `_PROTECTED_RUN_DIRS`·`_PROTECTED_FILES`(규칙 v1.5~v1.7·history.csv)에도 없다. 그래서 공유·추적 상태인 baseline 트리거를 바꾸면 승인이 유효로 남은 채 재빌드 리포트 본문이 바뀐다. 같은 조건에서 `baseline/v1.5/scores.json` 변경은 obsreg HTML·audit 에 0줄 변화였다(그 실행 화면에는 점수 델타가 표시되지 않음).
- 고치는 방향. `scorecard/baseline/**` 를 보호 훅에 넣거나, baseline 을 소비하는 실행의 입력 해시에 baseline subtree 해시를 포함시킨다. baseline 은 안정적이고 변경이 git 에 보이므로 위험은 제한되지만, 두 방어선이 모두 이 입력을 덮지 않는다.

### F-4 [low→medium] 실시간 CLI 안내와 생성된 plan.md 가 금지·낡은 단계를 가리킨다

- 위치: `scripts/scorecard_cli.py:226`(cmd_draft 의 "다음" 안내), `scripts/scorecard/render_md.py:97`(plan 템플릿 흐름), `scripts/scorecard_cli.py:168·191·200·217·226·274`·`scripts/scorecard/render_md.py:130`(uv 없는 `python` 안내).
- 재현·근거:
  - cmd_draft 가 찍는 다음 안내가 `review-template → 4-way 리뷰 → approve` 다. draft 를 돌린 에이전트에게 다음 단계로 `approve` 를 읽게 하는데, 승인은 사람 행위다.
  - plan.md 템플릿 흐름이 `plan → research → calculate → draft → review → awaiting_user → build` 로 `collect` 가 빠졌다. `design-guideline.md:353` 에도 `finalize` 라는 옛 단계명이 남아 있다.
  - 모든 "다음" 안내와 `--help` usage 본문이 `python scripts/…` 형식이라 `structure.md:164` 의 "시스템 python 직접 호출 금지" 와 어긋난다.
- 왜 결함인가. 에이전트가 안내를 문면 그대로 따르면 금지된 승인을 시도하거나 uv 밖 인터프리터를 부른다.
- 고치는 방향. draft 안내를 "승인 대기 보고(사람이 승인 페이지)" 로, 템플릿 흐름에 `collect` 를 넣고, 안내 접두를 `uv run --frozen python -X utf8` 로 맞춘다.

### F-5 [low] `--locale` 가 언어만 오면 Google `gl`·`ceid` 를 틀리게 만든다

- 위치: `scripts/scorecard/collect_news.py:115` `region = region or lang.upper()`.
- 재현:

```
locale 'ko' 이면 gl='KO' ceid='KO:ko' (Google 은 gl=KR 을 기대)
locale 'en-US' → …&hl=en-US&gl=US&ceid=US%3Aen (정상)
```

- 왜 결함인가. 하이픈 없는 로케일은 국가 코드 자리에 언어 코드를 넣어 잘못된 질의 URL 을 만든다. 기본값 `en-US` 는 정상이라 픽스처·기본 경로는 영향이 없고, 비US 실시간 수집에서 맨 언어 로케일을 줄 때만 드러난다.
- 고치는 방향. 언어→국가 매핑을 두거나 완전한 `xx-YY` 로케일을 요구한다.

### F-6 [low] 문서와 코드 불일치 (명령·경로·훅 표)

`--help` 전 서브커맨드 출력과 문서를 전수 대조했다. argparse 플래그 이름은 문서와 전부 일치한다(인자 불일치 없음). 남은 것은 다음이다.

- `docs/scorecard/open-items.md:26·54·68·103` — 옛 경로 `scorecard/runs/`·`reviews/<slug>.md`, uv 없는 `python`, "훅이 python3 별칭을 요구" 전제가 남아 있다. 지금은 `output/<run_id>/`, `uv run` 배선이다.
- `README.md:103·105·107` — protect 표가 `.github/workflows/`·`docs/finance-style-guide.md` 를 빠뜨리고, forbid_financial_advice 의 셸 PostToolUse 배선을 빼며, enforce_memory 범위를 `memory/` 전체로 넓게 적는다(실제는 `memory/_daily/`·`memory/topics/`).
- `docs/scorecard/structure.md:4`·`design-guideline.md:30` — `AI_company_analysis_factor/` 를 "저장소 밖 읽기 전용" 이라 하지만 git 이 그 안 6개 파일을 추적한다.
- `AGENTS.md:82`·`docs/memory-system.md:84-92` — memory topic 7개를 적지만 실재 파일은 `memory/topics/guardrails.md` 하나다(주입 훅은 없는 topic 을 "(없음)" 으로 보고해 동작은 무해).
- 고치는 방향. 위 문서를 현재 경로·배선·파일 목록으로 갱신한다. 코드 동작에는 영향이 없다.

### F-7 [low] 보호 훅이 읽기 전용 명령을 오탐으로 막는다

- 위치: `scripts/hooks/guard.py:186-217`.
- 재현: `cat output/ai-scorecard-2026-09-obsreg/approval.json; echo done` → `protect=block`. 이 검증 중에 두 번 걸렸다.
- 왜 결함인가. `_MUTATING` 이 `echo` 를 잡은 뒤 경로 리터럴을 발견해 막는데, 실제로 쓰는 것은 없다. 안전 방향의 오탐이라 위험은 없으나 승인 파일을 읽기만 하려는 정상 작업을 막는다.
- 고치는 방향. 경로를 리다이렉션·변경 동사의 대상일 때만 쓰기로 보고, 단순 언급은 통과시킨다.

---

## 발견이 없는 축 — 확인한 명령과 결과

### 축 1 승인 해시 무결성 (결함 없음, F-3 은 별건)

- 세 방식으로 푼 트리에서 두 실행 모두 `approval_valid: true` 를 재현했다. 워크트리, `git checkout-index -a --prefix=<스크래치>/`, `git archive HEAD | tar -x` 셋이 같은 바이트를 냈다.

```
== ai-scorecard-2026-09-baseline  approval_mismatches=[] approval_valid=True
   observations crlf=3258  draft crlf=1195  v1.5.json crlf=596   (승인 해시와 전부 일치)
   recompute_matches=(False, '0942c342…', '200d7b01…')   ← 알려진 기존 불일치
== ai-scorecard-2026-09-obsreg    approval_mismatches=[] approval_valid=True
   observations crlf=0  draft crlf=0                     (LF 바이트, 승인 해시 일치)
   recompute_matches=(True, '4a3f6c05…', '4a3f6c05…')
```

- `.gitattributes` 의 baseline CRLF 예외와 obsreg LF 규칙이 실제로 승인 바이트를 재현한다. baseline recompute 불일치는 알려진 기존 상태이고 approval_valid 는 저장 바이트 기준이라 유효하다.
- `approval_mismatches` 규칙 재현: obsreg 승인 해시 밖 입력(`sources.json` url, research 본문, `companies.json` scope, review 검토자 칸)을 바꿔도 `approval_valid=True` 로 남는다. 이는 의도된 계약이다. 다만 review 검토자 문자열 변경은 재빌드 시 HTML References 판정 줄과 audit 에 실린다. 이는 `docs/scorecard/open-items.md:103` 에 "리뷰 파일은 승인 해시 밖, 고치면 재빌드" 로 이미 기록된 설계다.

### 축 5 잠금과 다중 에이전트 (결함 없음)

- CLI `claim_lock` 과 훅 `enforce_plan` 이 같은 소유자 규칙을 쓴다.

```
env={} → stages='noble' guard='noble' 같음=True
env={'ORCA_TERMINAL_HANDLE':'term_x'} → 둘 다 'term_x'
env={'SCORECARD_AGENT':'A', 'ORCA_TERMINAL_HANDLE':'term_x'} → 둘 다 'A'
CLI: A 가 init(OK) → B 가 calculate(거부) → B 가 --take-lock(OK) → 사람 셸이 draft(거부)
훅: 잠금 owner=B 일 때 A 의 Write 차단, 손상된 잠금은 '알 수 없음' 소유자로 보아 차단, --take-lock 으로 인수
approve 단계는 잠금 대상이 아니다(사람 행위)
```

- 참고(low): 잠금·보호 검사는 파일 도구(Write/Edit/MultiEdit) 호출에만 걸린다. 잠긴(비보호) 실행 파일에 Bash `sed -i` 로 쓰면 잠금 검사를 지난다. 보호 실행은 `sed -i` 가 `_MUTATING` 에 잡혀 별도로 막힌다. 잠금은 조율용 표지라 영향은 낮다.

### 축 4 수집기 정확성 (결함 없음, F-5 는 별건)

- 시총 시점: 조회일이 종가일과 0~1일 이내면 `vendor_market_cap`, 그 밖이면 `price_x_shares`(발행주식수가 조회 시점 값임을 basis 에 표기), ADR 은 vendor 만 쓰고 못 쓰면 `collection_failed`.

```
NVDA 조회일=종가일     → vendor_market_cap
NVDA 조회일=종가일+2   → price_x_shares (shares_timing=current_at_fetch)
TSM(ADR) 조회일=종가일 → vendor_market_cap
TSM(ADR) 조회일+3      → collection_failed
TWD 통화               → ValueError(USD만 관측)
```

- 날짜 창(C-17): `since ≤ 발행일 ≤ info_cutoff`. `info_cutoff=2026-09-15` 로 두니 픽스처의 09-28·09-29·09-30 기사가 전부 제외됐다.
- `SEC_UA` 없는 공시: `require_user_agent` 가 fetch 전에 예외를 올리고 `stages.collect` 는 `skipped_no_user_agent`(cik 없으면 `skipped_no_cik`)로 나머지를 계속한다.
- `fetch_bytes` 가 유일한 urllib 지점, `fetch_quote` 가 유일한 yfinance 지점임을 `rg` 로 확인했다.
- 속도 제한: 질의당 하루 4회 뒤 `skipped_rate_limit`. 재수집 시 같은 `(기업, 지표, 기준일)` 가격 관측은 덮어쓰지 않고 `SchemaError` 로 멈춘다. `candidates.json` 은 같은 캐시에서 다른 시각에 두 번 써도 바이트가 같다(결정론).

### 축 3 근거 계층 정합 (결함 없음)

- 임시 `OUTPUT_DIR`·`DATA_ROOT`·`companies` 사본에서 CLI 로 `resolve-cik --apply` → `init --rule v1.8` → `collect`(news·filings·prices 픽스처) → 근거·트리거 작성 → `research` → `calculate` → `draft` → `review-template` → `approve` → `build` 를 끝까지 돌렸다.
- candidate 근거를 인용한 `status: new` 판단은 `calculate` 에서 거부된다("확정되지 않은 근거 … confirmed 근거만 인용한다"). `confirm` 뒤에는 통과한다.
- 승인 뒤 evidence `horizon` 을 바꾸면 `approval_valid=False`, mismatches `['evidence']`. `triggers.json` 삭제 시 mismatches `['triggers']`. 되돌리면 유효로 복귀. `candidates.json` 을 비워도 승인은 유효(후보 파일은 해시 밖).
- 트리거가 인용하는 근거를 `confirm --reject` 하면 실행 전체 재검증이 실패해 evidence 파일이 원상 복구된다(항목 수 불변). 근거 확정은 승인을 무효로 만들고 이후 `build` 는 사전 검증에서 멈춘다.

### 축 2 승인 우회 (F-1·F-2 외 확인한 것)

- 표지가 있는 세션에서 CLI `approve`·`revoke` 는 `exit 1` 로 거부된다.
- 이미 빌드된 obsreg 에서 사람 셸(표지 제거)로 `revoke` 뒤 `approve` 를 시도하면, `report.html` 이 남아 있는 동안은 `awaiting_user` 로 거부되고 html 을 지운 뒤에만 승인된다.
- 훅 명령 형태 표: 리터럴 `approve`·리다이렉션 `> approval.json`·`python -c` 로 draft 덮어쓰기(python 이 맨 앞)는 block, `Set-Content`(PowerShell cmdlet, 알려진 통과)·`uv run` 안의 approval.json 쓰기는 allow.

### 축 6·7 문서와 삭제 부작용

- 지운 이름(`report_type_for`·`price_chart_blocks`·`hero_image_status`·`ASSET_DIR`·`sync_outputs`·`memory_context`·`enforce-citations`·`stock-*`)을 `rg` 로 전수 검색했다. 살아 있는 코드 참조는 없다. 남은 언급은 `scripts/report_contract_lib.py:25`·`scripts/hooks/README.md:17`(둘 다 "예전에는" 역사 서술), `tests/test_scorecard_f6_v17.py:580`·`tests/test_scorecard_fix64.py:101`(옛 커밋·문자열을 일부러 참조하는 테스트)뿐이다. `report_type_for` 는 `structure.md:11` 이 가리키지만 실제 함수는 없다(문서 잔재, F-6 에 포함).
- 문서 불일치는 F-6 에 모았다.

---

## main 병합을 막아야 할 발견

정상적인 도구 호출 경로에서 승인된 산출물이 조용히 오염되거나 미승인 빌드가 나가는 결함은 없었다. 승인 해시·CLI·훅 사슬은 도구 호출 경로에서 유지된다. 따라서 하드 블록 항목은 없다고 판단한다.

병합 전에 손보기를 권하는 두 건은 다음이다. 둘 다 설계가 "훅은 둘째 방어선" 이라 문서화한 범위 밖에서 에이전트가 의도적으로 움직여야 성립한다.

1. **F-1** — `init --force` 가 승인된 실행의 입력과 승인을 훅·CLI 제지 없이 파괴한다. 보호 훅의 목적이 이 경로로 비어 있으므로 승인 산출물 보호를 완성하려면 닫는 편이 낫다.
2. **F-2** — 승인 첫 방어선(에이전트 거부)이 `stages.approve` 본체에 없어 import 로 우회된다. 거부를 stage 함수로 내리면 첫 방어선이 실제로 첫 방어선이 된다.

F-3(baseline 이 해시·보호 밖)은 재빌드가 필요하고 변경이 git 에 보이므로 병합 차단은 아니나 같은 결로 함께 고려할 수 있다.

## 최종 커밋 SHA

이 보고서 커밋(아래 `docs(validation)`)이 유일한 변경이다. 소유 밖 파일은 건드리지 않았다.
