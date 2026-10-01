# 레인 J — 승인 페이지의 판단 수정 기능, 수집기 실측 결함 수정, 남은 정리

에이전트: Claude Opus 5.5. 의존: 레인 H·I·M 병합 완료. 공통 규약: `README.md` 를 먼저 읽는다. 근거 문서: `../context-notes.md` 의 "승인 페이지에서 사람이 정성 판단을 고친다" 결정, `validation/lane-M-live-collection/REPORT.md`(F-M-1~3), `validation/lane-H-review-fixes/REPORT.md` 의 "남은 것". 이 레인이 끝나면 문서는 레인 K(Sonnet)가 맡는다. **문서(README·AGENTS·docs)는 고치지 않는다.**

## A. 판단 수정 기능 (사용자 결정 2026-10-01)

원칙. 사람은 승인 페이지에서 정성 판단을 고친다. **점수가 아니라 판단 입력을 고친다.** `results.json` 의 점수를 덮어쓰지 않는다. 수정 제출과 승인은 다른 단계다. 수정하면 해시가 바뀌어 calculate·draft·review 를 다시 거친 뒤에 승인한다.

1. Python. `stages.revise_judgment(slug, *, company_id, factor, changes, reason, by)` 와 CLI `judge <run_id> --company <id> --factor F1..F9 --set key=value … --reason "…" --by <이름>`(또는 `--json <파일>`). 대상은 `judgments.json` 의 해당 항목이다.
   - F1·F4·F8: `score` 와 근거(`evidence` 문장)를 고친다.
   - F3: `criteria`, F5: `grade`, F7: `matrix`, F9: `gate_inputs` 의 판정 재료를 고친다. 이 factor 들의 점수 칸은 고치게 하지 않는다(규칙이 계산한다).
   - 쓴 뒤 `status: new`, `reviewer: <by>`, `reviewed_at: 오늘(UTC)`, 수정 사유를 남긴다. 이전 값은 항목 안에 `revision_history`(이전 값·사유·누가·언제) 로 보존한다. 스키마(`validate_judgments`)가 이 키를 받도록 확장한다.
   - 값의 형식은 스키마가 검증한다. 형식이 틀리면 아무것도 쓰지 않는다.
   - 에이전트 세션도 이 명령을 쓸 수 있다(에이전트가 판단을 제안하는 것은 정상 흐름). 다만 `reviewer` 는 `--by` 로 받은 이름이다. 승인 페이지는 사람 이름을 넣는다.
   - 실행 잠금 규칙은 `confirm` 과 같다(에이전트 세션일 때만 잠금 검사).
2. `summary --json` 에 판단 목록을 더한다. 기업×factor 별 현재 판단 입력, 판정 종류, status, reviewer, reviewed_at, 근거. 승인 페이지 계약 픽스처 `tests/node/fixtures/summary.sample.json` 에 이 키를 추가하고 Python 쪽 키 구조 테스트를 맞춘다.
3. 승인 페이지(`server/approvals.js`). "판단 수정" 절을 더한다. factor 를 고르면 그 factor 의 **모든 기업 판단을 나란히** 보여 주고(잣대 비교, Q03), 한 기업을 골라 판정 종류에 맞는 입력란(점수 또는 criteria·등급·매트릭스·gate 값)과 사유 입력을 낸다. 제출은 `POST /approve/<run_id>/judge`, 일회용 코드 필수, CLI `judge` 를 `execFile` 로 부른다. 제출 뒤 "해시가 바뀌었다 — 에이전트에게 다시 계산·리뷰를 시킨 뒤 새로고침해 승인" 안내를 보인다. 기존 보안 규칙(루프백, 코드 실패 5회 제한, 이스케이프, run_id 정규식)을 그대로 따른다.
4. 테스트. Python: 각 판정 종류의 수정과 거부(점수 칸 직접 수정 거부, 형식 오류 시 무변경), `revision_history` 보존, 수정 뒤 `current_hashes` 의 judgments 변경과 승인 무효, 수정한 판단으로 calculate 가 새 점수를 내는지(임시 묶음). node: 판단 수정 POST 의 코드 검사·인자 생성·CLI 미호출(코드 불일치).

## B. 수집기 실측 결함 (레인 M F-M-1~3, 조율자 재시도 결과)

1. **NaN 종가.** 야후는 가장 최근 거래일 일봉의 종가를 몇 시간 동안 비워 둔다(2026-09-30 실측, 12개사 모두). `fetch_quote` 는 종가가 유한하지 않은 행을 건너뛰고 기준일 이하의 마지막 유한 종가를 쓰며, `close_date` 도 그 날짜로 한다. 건너뛴 사실을 반환값에 남긴다.
2. **회사별 실패.** `collect --kind prices` 는 한 회사의 실패가 전체를 막지 않게 한다. 회사별로 관측을 만들고 검증해서, 실패한 회사는 요약에 failed 로 남기고 나머지는 기록한다. 검증 실패도 회사 단위로 잡는다.
3. **`resolve-cik --json`.** CLI 에 `--json` 을 더한다(모듈에는 이미 있다).
4. **`SEC_UA` 사전 검사.** 영문 범위(ASCII) 밖 글자가 있으면 네트워크 요청 전에 "SEC_UA 는 영문으로 적는다(HTTP 머리글 제약)" 오류를 낸다. 뉴스 UA 도 같은 값을 쓰므로 같은 검사를 거친다. 값은 오류 메시지에 넣지 않는다.
5. **일반 단어 회사의 뉴스 질의.** `scorecard/companies.json` 의 `news_queries` 에 회사명이 일반 단어인 곳의 질의를 넣는다. 최소 meta(`"Meta Platforms"`, `"META stock"`), oracle(`"Oracle Corporation"`, `"ORCL"`), apple(`"Apple Inc"`, `"AAPL"`). `registry.set_company_field` 로 쓰고 다른 줄 바이트는 그대로 둔다. 기존 두 실행의 `results_hash` 가 바뀌지 않는지 확인한다.
6. **CIK 기입.** `resolve-cik --apply` 를 실제로 한 번 돌려 상장 12개사의 `cik` 를 `companies.json` 에 넣는다. SEC 실응답이 SPCX 를 1181412 로 확인했다(사용자 후보와 일치). `SEC_UA` 는 원본 폴더 루트 설정 파일에서 읽히고, 이제 영문이다. 값을 출력하지 않는다.

## C. 남은 정리

1. **보호 훅 쓰기 형태.** PowerShell cmdlet(`Set-Content`, `Add-Content`, `Out-File`, `Remove-Item`, `Move-Item`, `Copy-Item`, `New-Item`, `Rename-Item`, `Clear-Content`)의 경로 인자, `find … -delete`, `xargs` 로 이어지는 변경, 글롭이 보호 경로와 맞는 경우를 쓰기 대상으로 판정한다. 레인 H 의 "쓰기 대상일 때만 막고 읽기는 통과" 규칙을 유지한다.
2. `render_md.py` 130행 근처의 `uv` 없는 `python` 안내를 `uv run --frozen python -X utf8` 로.
3. 에이전트 표지에 `MUSE_TOOL_USE_ID` 를 더한다(도구 호출 때만 생기는 값, 레인 M 조사). `MUSE_RELEASE_INFO` 는 사람 셸 비교가 없어 넣지 않는다.
4. `validation/recheck_worker_final.py` 는 옛 검증 기록이다. 고치지 않고, 이 스크립트가 지금 에이전트 세션에서는 거부된다는 사실만 보고서에 적는다.

## 소유 파일

`scripts/scorecard/stages.py`·`schema.py`·`collect_prices.py`·`evidence_lib.py`·`collect_news.py`(UA 검사만)·`render_md.py`(130행)·`registry.py`(필요 시), `scripts/scorecard_cli.py`, `scripts/hooks/guard.py`·`README.md`, `server/approvals.js`, `scorecard/companies.json`(B-5·B-6 만), `tests/**`(관련 테스트·픽스처), 보고서. 만지지 않는 것: `output/ai-scorecard-2026-09-*`, 규칙 파일, `history.csv`, 루트 문서(`README.md`·`AGENTS.md`·`docs/**`), `server.js`.

## 검증

- 두 기존 실행 `approval_valid: true`, `output/ai-scorecard-2026-09-*` 변경 0, `results_hash` 불변(companies.json 변경 뒤에도).
- 실제 조회 확인(각 1회): 가격은 가장 최근 거래일 기준으로 조회해 NaN 행이면 직전 종가로 기록되는지, 뉴스는 질의를 바꾼 3개사, CIK 기입 결과 표.
- 승인 페이지 수동 확인: 가짜 CLI 로 서버를 띄워 판단 수정 양식을 열고 코드 입력까지(레인 D 보고서 방식).
- 테스트 기준(unittest 1115건 중 실패 1·오류 14, 전부 원자료 부재)에서 증가 없음. `npm run check`, `npm run test:node` 통과.
- 보고서 `validation/lane-J-judgment-edit/REPORT.md`. 통합 브랜치 merge 가 거부되면 보고만.
- 셸 명령 문자열에 보호 경로·승인 명령을 넣으면 훅이 막는다. 필요하면 페이로드를 파일로 만들어 확인한다.
