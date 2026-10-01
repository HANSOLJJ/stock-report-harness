# 레인 M — 실제 수집 시험, SEC 실응답 픽스처, 에이전트 환경변수 조사

에이전트: Muse. 의존: 통합 브랜치 현재 상태. 공통 규약: `README.md` 를 먼저 읽는다. 레인 H(Opus)가 동시에 `guard.py`·`stages.py`·`scorecard_cli.py`·`render_md.py` 를 고친다. **그 파일들은 건드리지 않는다.**

## 목적

수집기는 지금까지 픽스처로만 시험했다. 실제 응답에서 생기는 문제(날짜 형식, 빈 결과, 비상장사, 조회 한도, 통화, ADR)를 다음 정기 재채점 전에 드러낸다. 그리고 SEC 합성 픽스처 두 개를 실제 응답으로 바꾼다.

## 시작 시점 상태

- `SEC_UA` 는 사용자가 원본 폴더 루트의 로컬 설정 파일에 두었다. 코드(`evidence_lib.sec_user_agent()`)가 워크트리 루트 → 원본 루트 순서로 읽는다. **값을 출력·로그·보고서·커밋에 적지 않는다.** 확인이 필요하면 "있음/없음" 과 길이만 적는다.
- 에이전트의 그 설정 파일 쓰기는 보호 훅이 막는다. 만들거나 고치지 않는다.
- 수집기 정중한 기본값: 구글 질의당 하루 4회, SEC 요청 사이 1초, 기사 본문 미수집. 이 상수를 바꾸지 않는다.

## 소유 파일 (Ownership)

- `tests/fixtures/edgar_submissions.CIK0001045810.sample.json`, `tests/fixtures/company_tickers.sample.json`, `tests/fixtures/README.md`
- 이 두 픽스처를 쓰는 테스트 `tests/test_collect_filings.py`, `tests/test_resolve_cik.py`(픽스처 교체로 바뀌는 기대값만)
- 보고서 `validation/lane-M-live-collection/REPORT.md`

만지지 않는 것: `scripts/**`(버그를 찾으면 고치지 말고 보고), `scorecard/companies.json`(CIK 를 기입하지 않는다. `--apply` 금지), 그 밖의 `tests/**`, 문서 전부, `output/ai-scorecard-2026-09-*`.

## 할 일

1. **임시 실행으로 실제 수집.** `uv run --frozen python -X utf8 scripts/scorecard_cli.py init ai-scorecard-livecheck-2026-10 …` 으로 14개사 임시 실행을 만든다(규칙 v1.8, as_of 는 오늘). 이 실행 폴더와 `data/` 는 **커밋하지 않는다.** 먼저 `collect … --dry-run` 으로 URL 을 확인하고, 그다음 `--kind news` 와 `--kind prices` 를 한 번씩 실제로 돌린다. 기업별 결과(후보 수, 창 밖으로 버린 수, 날짜 없는 항목, 실패와 오류 문구, 가격의 close_date·통화·시총 방식·ADR 처리)를 표로 남긴다. 결과가 이상하면 원인을 코드에서 찾아 위치(`파일:줄`)와 고치는 방향을 적는다.
2. **SEC 실조회.** `resolve-cik --json`(apply 없이)으로 12개 상장사 CIK 를 실제 조회한다. 결과 표(티커, CIK, status). SPCX 가 목록에 있는지, 없으면 그 사실을 적는다(사용자 확인 후보는 1181412). 그다음 CIK 가 확인된 회사 가운데 NVDA·TSM·SPCX(목록에 없으면 후보 CIK 로)의 submissions 를 각각 한 번 조회해 `parse_submissions` 결과(최근 form 몇 건)를 적는다. 요청 사이 1초를 지킨다.
3. **픽스처 교체.** 2번의 실제 응답으로 `company_tickers.sample.json`(12개사 + 테스트에 필요한 행만 남겨 줄인다)과 `edgar_submissions.CIK0001045810.sample.json`(`filings.recent` 20건 이내로 줄인다)을 바꾼다. 줄일 때 키 구조는 그대로 둔다. `tests/fixtures/README.md` 의 "합성" 표시를 "실응답(조회일, 줄인 방식)" 으로 바꾼다. 바뀐 기대값만 테스트에서 고치고, 테스트가 검사하는 성질(SPCX 미등재 경로 등)이 실제 응답으로 성립하지 않으면 그 테스트를 약하게 만들지 말고 보고서에 적어 조율자에게 `ask` 한다.
4. **에이전트 환경변수 조사.** 이 Muse 세션의 환경변수 **이름** 목록을 뽑아, `validation/lane-F-approval/REPORT.md` 의 표(Claude Code 세션 기준, 거부 표지 `CLAUDECODE`·`CLAUDE_CODE_ENTRYPOINT`·`ORCA_AGENT_LAUNCH_TOKEN`·`AI_AGENT`)와 비교한다. Muse 세션에 그 넷 중 무엇이 있는지, Muse 세션만의 표지 후보가 무엇인지 표로 적는다. 값은 적지 않는다. 코드는 고치지 않는다(레인 H 뒤 조율자가 반영한다).

## 검증 (Observable acceptance)

- 픽스처 교체 뒤 `tests/test_collect_filings.py`·`tests/test_resolve_cik.py` 통과. 전체 테스트 기준(unittest 1094건 안팎 중 실패 1·오류 14, 전부 원자료 부재)에서 증가 없음.
- `git status` 에 임시 실행 폴더와 `data/` 가 커밋되지 않았다. 커밋은 픽스처·테스트·보고서뿐이다.
- 보고서에 `SEC_UA` 값이 없다.
- 보고서 `validation/lane-M-live-collection/REPORT.md` 를 커밋에 포함한다. 통합 브랜치 merge 가 거부되면 보고만.
