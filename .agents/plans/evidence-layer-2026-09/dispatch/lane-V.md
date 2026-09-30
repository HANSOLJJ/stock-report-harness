# 레인 V — 독립 검증: 통합 브랜치 전체를 적대적으로 검토한다

에이전트: Claude Fable 5.1. **읽고 재현만 한다. 코드·문서를 고치지 않는다.** 공통 규약 `README.md` 의 커밋·금지 규칙은 따른다(보고서만 커밋).

## 배경

`HANSOLJJ/revision_checker` 는 `main` 대비 커밋 58개 앞서 있다. 레인 S·A·B·C·D·E·F·G 여덟 워커가 나눠 구현했고, 조율자가 레인마다 재현 뒤 병합했다. 계획은 `../plan.md`, 결정은 `../context-notes.md`, 진행과 알려진 후속 항목은 `../checklist.md`, 레인별 지시서는 이 폴더의 `lane-*.md`, 레인별 보고서는 `validation/lane-*/REPORT.md` 다.

조율자의 재현은 레인 단위였다. 너의 일은 **레인 사이의 이음매와 전체 흐름**에서 조율자가 놓친 결함을 찾는 것이다. 보고서를 믿지 말고 코드와 실행 결과로 판단한다.

## 이미 알려진 것 (다시 보고하지 않는다. 틀렸다고 판단하면 그 근거만 적는다)

- unittest 1085건 중 실패 1·오류 14, pytest 실패 15 는 `validation/*/_raw` 원자료가 워크트리에 없어서 난다.
- baseline 실행은 승인 뒤 엔진이 바뀌어 recompute 가 원래부터 불일치(저장 `0942c342…`, 재계산 `200d7b01…`)이고 재빌드가 멈춘다. 초안 재렌더도 KeyError.
- 옛 obsreg `report.html` 의 감사 링크가 묶음에서 깨진다(재빌드로 해결 예정).
- PowerShell cmdlet(`Set-Content` 등) 변경은 보호 훅을 지나간다.
- SEC 픽스처 2개는 합성이다. 에이전트 표지 환경변수는 Claude Code 세션 하나만 조사했다.

## 검토 축 (각 축마다 실제로 명령을 돌려 확인한다)

1. **승인 해시 무결성.** 두 기존 실행이 새 checkout 에서도 `approval_valid: true` 인가(`git worktree` 가 아니라 `git checkout-index --prefix=<스크래치>/` 나 `git archive` 로 풀어서 `.gitattributes` 줄끝 규칙이 실제로 승인 바이트를 재현하는지). `approval_mismatches` 의 규칙에 승인을 무효로 만들어야 하는데 유효로 두는 경우가 있는가(예: sources 가 바뀌었는데 기존 승인에 sources 키가 없어 대조하지 않는 경우의 영향 범위).
2. **승인 우회 경로.** 에이전트가 승인 없이 build 까지 가거나 승인 파일을 만들 수 있는 길. 훅(`scripts/hooks/guard.py`), CLI 에이전트 거부, 승인 페이지(`server/approvals.js`) 각각의 우회. 예: `python -c "from scorecard.stages import approve …"` 류, 다른 파일명·경로 표기(역슬래시, 대소문자, 상대경로 `./`), `uv run` 없이 직접 호출, 셸 변수로 명령을 쪼개기. 훅은 둘째 방어선이라는 설계를 전제로, **첫째 방어선(해시 검증·CLI)** 이 뚫리는지를 중심으로 본다.
3. **근거 계층 정합.** `collect → evidence → research → calculate → draft → review → approve → build` 를 임시 `OUTPUT_DIR`·`DATA_ROOT` 에서 픽스처로 끝까지 돌려 본다(`tests/test_evidence_e2e.py` 를 참고하되 그대로 믿지 말고 CLI 로 직접). candidate 근거를 인용한 새 판단이 어디서든 통과하는가. 근거·트리거를 바꾼 뒤 승인이 무효가 되는가. `candidates.json` 결정론.
4. **수집기 정확성.** `collect_prices` 의 시총 시점·ADR 처리, `collect_news` 의 날짜 창(C-17 `info_cutoff`), `collect_filings` 의 `SEC_UA` 없는 경로, `fetch_bytes` 가 유일한 네트워크 지점인지. 네트워크는 쓰지 않는다(픽스처와 주입된 fetch 로).
5. **잠금과 다중 에이전트.** `.lock` 의 소유자 판정, `--take-lock`, `confirm` 의 사람/에이전트 구분, 훅의 잠금 검사가 CLI 와 같은 판정을 쓰는지.
6. **문서와 코드의 일치.** AGENTS.md·README.md·`docs/scorecard/structure.md`·score-* 스킬에 적힌 명령과 인자가 실제 `--help` 와 맞는가. 에이전트에게 승인을 시키는 문구가 남았는가.
7. **삭제의 부작용.** 종목 코드 삭제(레인 S·A)로 채점표가 쓰던 것이 끊겼는가. `rg` 로 지운 이름(`report_type_for`, `price_chart_blocks`, `hero_image_status`, `ASSET_DIR`, `sync_outputs`, `memory_context`, `enforce-citations` 등)의 남은 참조.

## 산출물

- 보고서 `validation/lane-V-independent-review/REPORT.md`. 발견마다 다음을 적는다. 심각도(high·medium·low), 위치(`파일:줄`), 재현 명령과 실제 출력, 왜 결함인지, 고치는 방향(한두 문장, 직접 고치지 않는다). 발견이 없는 축은 "확인한 것" 을 명령과 함께 적는다. 마지막에 "main 병합을 막아야 할 발견" 을 따로 모은다.
- 보고서만 한 커밋. `docs(validation): 통합 브랜치 독립 검증 보고서`.
- 코드·테스트·문서·기존 실행 파일을 고치지 않는다. 임시 파일은 시스템 임시 폴더에 두고 저장소에 남기지 않는다. `git stash` 금지. 승인 명령을 실제 두 실행에 대고 돌리지 않는다.
- 완료는 preamble 의 `worker_done`(발견 수와 병합 차단 여부를 세 문장 요약에) 뒤 조율자 터미널 `term_be1eaaf8-815c-4231-a858-7229d925e5fe` 에 한 줄 안내.
