# 레인 M — 실제 수집 시험, SEC 실응답 픽스처, 에이전트 환경변수 조사 보고서 (2026-10-01)

임시 실행 `ai-scorecard-livecheck-2026-10`(규칙 v1.8, as_of 2026-10-01)으로 14개사
뉴스·가격 실수집을 돌리고, SEC 실조회로 픽스처 두 개를 실응답으로 교체했다.
실수집에서 버그 3건을 찾았다. scripts/** 는 소유 밖이라 고치지 않고 위치와
고치는 방향만 적는다. `SEC_UA` 값은 어디에도 적지 않는다(있음, 길이 23).

## 커밋

| SHA | 내용 |
| --- | --- |
| `7e96302` | test: SEC 합성 픽스처 두 개를 실응답으로 교체하고 기대값 갱신(픽스처 3·테스트 3) |
| `f05476b` | merge: `HANSOLJJ/revision_checker`(레인 H, fast-forward, 충돌 없음) |
| 이 보고서 커밋 | docs(validation): 레인 M 보고서 |

## 1. 임시 실행 실제 수집

`init ai-scorecard-livecheck-2026-10 --rule v1.8 --as-of 2026-10-01` 로 생성.
이 실행 폴더와 `data/` 는 커밋하지 않는다(검증 절 참조).

### 1.1 뉴스 (`collect --kind news`, dry-run 뒤 실수집 1회)

dry-run URL 정상(기업별 display_name·ticker 2질의, anthropic·openai는 1질의).
실수집 결과: **14개사 전부 failed**,
`error='latin-1' codec can't encode characters in position 36-38` (F-M-1).

| 기업 | 질의 | 결과 |
| --- | --- | --- |
| 14개사 전부 | display_name·ticker(비상장 2개사는 이름만) | failed, 위 오류 문구 동일 |

원인. `scripts/scorecard/evidence_lib.py:85-91` `user_agent_for("news")` 가
`SEC_UA` 값을 그대로 UA에 끼워 넣는다. 이 환경의 `SEC_UA` 첫 글자가
latin-1 범위 밖이라 `urllib` 헤더 인코딩에서 터진다(접두 35자는 ASCII,
36번째부터 연락처). 같은 이유로 SEC 조회(`resolve-cik`, submissions)도
`position 0-2` 에서 터진다(§2). 즉 뉴스 수집기는 한 번도 실제 응답을 받지
못했다. 수집 상수(질의당 하루 4회)는 건드리지 않았다.

고치는 방향(레인 H·조율자용). 뉴스 UA에는 `SEC_UA` 원문을 통째로 넣지 말고
ASCII로 살균한 연락처(또는 고정 식별자)를 쓴다. SEC 조회 UA도 마찬가지다
(SEC는 ASCII UA를 기대한다).

진단(코드 미수정, 메모리 내 1회). ASCII UA로 `NVDA` 1질의를 직접 조회하자
정상 응답했다. item 100건, `pubDate` 없는 항목 0건,
첫 항목 `published_at_utc` 정상(RFC 2822 → UTC 파싱 동작).
즉 파이프라인(`parse_rss`·`normalize_article`)은 멀쩡하고 UA 헤더 하나가
전부를 막고 있다. 창 밖 제외·날짜 없음 통계는 후보가 0건이라 표로 남길
값이 없다.

### 1.2 가격 (`collect --kind prices` 1회)

결과: **종료 코드 1, `[FAIL] observations[227]: price 값은 숫자 또는 null`**.
어떤 기업도 기록되지 않았다(검증이 쓰기보다 먼저라 전량 롤백, §1.3).

티커별 실측(`fetch_quote(t, '2026-10-01')` 직접 조회, 통화·시총 방식 확인용):

| 티커 | close | close_date | currency | market_cap | shares | 비고 |
| --- | --- | --- | --- | --- | --- | --- |
| GOOGL·AMZN·MSFT·META·TSM·BABA·AAPL·NVDA·PLTR·SPCX·TSLA·ORCL 전부 | NaN | 2026-09-30 | USD | 값 있음 | 값 있음 | F-M-2 |

원인. Yahoo가 2026-09-30 행을 내놓되 `Close`를 NaN으로 주었다
(OHLC·Volume은 있음. NVDA tail 실측 확인).
`scripts/scorecard/collect_prices.py:22` 가 마지막 행의 종가를
유한성 검사 없이 그대로 쓴다 → `price_observations` 가 NaN을 관측값에
넣는다 → `scripts/scorecard/schema.py:184-187` `_is_number`
(`math.isfinite`)가 거부한다(메시지 `schema.py:958`).
`stages.py:370` 의 기업별 try/except는 `fetch`·`price_observations`
예외만 잡고, 검증(`stages.py:389` `validate_observations`)은 전량 합친 뒤라
한 기업의 NaN이 12개사 전체를 실패시킨다.

고치는 방향(레인 H·조율자용). `fetch_quote` 에서 NaN 종가를 건너뛰고
직전 유한 종가를 쓰거나(권장, close_date도 그 날짜로), NaN이면 그 기업의
관측을 `collection_failed` 로 기록하고 나머지는 살린다. 후자를 택하면
검증 실패가 아니라 기업별 failed 행이 된다.

참고 — ADR 경로 실측(정상 동작 확인).
`price_as_of=2026-09-29` 로 TSM·BABA를 조회하자 종가는 유한하고
`_vendor_cap_is_fresh` 가 거짓(조회일 10-01, gap 2일)이라
`market_cap=collection_failed` + ADR 안내 note가 붙었다. 레인 E 설계대로다.
SPCX도 yfinance에서 정상 조회된다(시장가·발행주식 값 있음).
TSM·BABA의 yfinance 통화는 USD(뉴욕 ADR 티커)라 통화 거부는 없었다.

### 1.3 수집 실패의 기록 방식

뉴스 실패는 기업별 failed 행으로 남아 `candidates.json` 까지 간다(전량 실패라
후보 0건). 가격 실패는 예외가 아니라 검증 실패라 행 자체가 남지 않고
명령이 종료 코드 1로 끝난다. 둘의 가시성이 다르다는 점을 적어 둔다.

## 2. SEC 실조회

`resolve-cik --json` 은 CLI가 `--json` 을 안 받는다
(`scripts/scorecard_cli.py:529-533` 에 플래그 없음. 모듈
`scripts/scorecard/resolve_cik.py:60` 에는 있음. F-M-3).
`--apply` 없이 표 출력으로 조회하려 했으나 F-M-1 때문에 CLI가 통째로
실패한다. 그래서 scripts 미수정 진단 스크립트로 SEC_UA의 ASCII 잔여분만을
UA로 써서 조회했다(값 출력·저장 없음, 요청 사이 1초 준수).

### 2.1 resolve 결과 (실응답 `company_tickers.json` 10431행)

| 티커 | CIK | status |
| --- | --- | --- |
| GOOGL | 1652044 | resolved |
| AMZN | 1018724 | resolved |
| MSFT | 789019 | resolved |
| META | 1326801 | resolved |
| TSM | 1046179 | resolved |
| BABA | 1577552 | resolved |
| AAPL | 320193 | resolved |
| NVDA | 1045810 | resolved |
| PLTR | 1321655 | resolved |
| SPCX | 1181412 | resolved |
| TSLA | 1318605 | resolved |
| ORCL | 1341439 | resolved |
| anthropic·openai | — | unlisted |

SPCX는 목록에 있다. CIK 1181412는 사용자 확인 후보와 일치하고 역조회도
`1181412 → SPCX` 다. `companies.json` 에는 쓰지 않았다(`--apply` 금지 준수).

### 2.2 submissions 조회 (`parse_submissions` 결과)

| 기업 | CIK | 응답 바이트 | DEFAULT_FORMS 파싱 | 최근 5건 |
| --- | --- | --- | --- | --- |
| NVDA | 1045810 | 159785 | 85건 | 8-K 2026-09-03, 10-Q 2026-08-26, 8-K 2026-08-26, 8-K 2026-08-17, 8-K 2026-07-02 |
| TSM | 1046179 | 162649 | 677건(6-K 대다수) | 6-K 2026-09-24, 6-K 2026-09-10, 6-K 2026-09-01, 6-K 2026-08-25, 6-K 2026-08-14 |
| SPCX | 1181412 | 14922 | 9건 | 8-K 2026-08-14, 10-Q 2026-08-04, 8-K 2026-08-04, 8-K 2026-06-26, 8-K 2026-06-23 |

NVDA `filings.recent` 는 1000건(구분 `4` 557·`144` 247·`8-K` 61·`10-Q` 18 등).
SPCX는 상장 초기라 9건뿐이다.

## 3. 픽스처 교체

- `tests/fixtures/company_tickers.sample.json`. 실응답 10431행 중 12개사 행만
  남겨 줄임(키 구조 `{"N": {cik_str, ticker, title}}` 그대로, 0~11 재배번).
  조회일 2026-10-01. SPCX 행 포함.
- `tests/fixtures/edgar_submissions.CIK0001045810.sample.json`. 실응답의
  `filings.recent` 병렬 배열 1000건을 앞 20건으로 자름(그 밖의 키·`files`
  그대로). 앞 20건은 `4`·`144`·`3`·`N-PX` 뿐이라 파싱 결과 2건
  (8-K 2026-09-03 items `8.01`, 10-Q 2026-08-26)이다.
  종전 픽스처의 S-8 1건은 앞 20건에 없어 거름망 검사는 `4`·`144`·`3`·`N-PX`
  제외로 바뀐다(성질은 유지).
- `tests/fixtures/README.md`. "합성" 표시를 "실응답(조회일, 줄인 방식)" 으로 바꿈.

테스트 변경(바뀐 기대값만).

- `tests/test_collect_filings.py`. 파싱 9→2, since 7→2, 첫 행
  `edgar:000104581026000078`·items `["8.01"]`·`nvda-20260902.htm`,
  수집 9→2.
- `tests/test_resolve_cik.py`. 매핑 11→12. SPCX는 `resolved` + CIK 1181412
  단언으로 바꾼다(조율자 결정: 실측이 사용자 후보와 일치한다는 결과가
  테스트에 남는다). `not_found` 경로는 픽스처에 없는 가짜 티커(`ZZZZ`,
  테스트용 `ghost` 기업 dict)로 검사하고 픽스처에 가짜 행은 넣지 않는다.
  `unlisted` 검사는 그대로 둔다.
- `tests/test_evidence_schema.py`(소유 밖, 조율자 결정의 동일 성질이라 최소
  한으로 손댐. 아래 소유 밖 5). SPCX 행 기대를 `not_found`→`resolved`
  1181412로, `--apply` 뒤 `cik` 미기록 3사에서 spacex-xai를 빼고
  `cik == 1181412` 단언을 더한다.

## 4. 에이전트 환경변수 조사

이 Muse 세션의 환경변수 이름 목록과 `validation/lane-F-approval/REPORT.md`
표(Claude Code 세션 기준)를 비교했다. 값은 적지 않는다.

| 변수 | Claude Code 세션 | 이 Muse 세션 | 비고 |
| --- | --- | --- | --- |
| `CLAUDECODE` | 있음 | 없음 | 거부 표지 1 |
| `CLAUDE_CODE_ENTRYPOINT` | 있음 | 없음 | 거부 표지 2 |
| `ORCA_AGENT_LAUNCH_TOKEN` | 있음 | 있음 | 거부 표지 3. Muse 세션에도 있다 |
| `AI_AGENT` | 있음 | 없음 | 거부 표지 4 |
| `MUSE_RELEASE_INFO` | (미관측) | 있음 | Muse 표지 후보 1 |
| `MUSE_TOOL_USE_ID` | (미관측) | 있음 | Muse 표지 후보 2 |
| `CLAUDE_CODE_TOOL_USE_ID` | (미관측) | 있음 | Muse 세션에 있으나 Claude Code 전용인지는 미확인 |
| `ORCA_OPENCODE_AGENT`·`ORCA_CODEX_HOME`·`CODEX_HOME`·`ORCA_PI_SOURCE_AGENT_DIR` 등 | 사람 셸에도 있는 것은 제외(레인 F) | 있음 | 사람 Orca 셸과의 비교가 없어 표지 판단 불가 |

판단. 현행 `AGENT_ENV_MARKERS` 4개 중 Muse 세션에 잡히는 것은
`ORCA_AGENT_LAUNCH_TOKEN` 하나뿐이다. `CLAUDECODE`·`CLAUDE_CODE_ENTRYPOINT`·
`AI_AGENT` 가 없어 Muse 세션의 `approve`·`revoke` 거부가 동작하지 않을
가능성이 크다(레인 H가 고치는 영역이라 코드는 손대지 않았다).
Muse 표지 후보는 `MUSE_RELEASE_INFO`·`MUSE_TOOL_USE_ID` 다.
다만 사람 셸(레인 F 방식의 PowerShell 대조)을 이번 레인에서 띄우지 않아
"사람 셸에는 없음" 쪽 확인은 못 했다. `ORCA_*` 단독 환경의 사람 셸 판정
테스트는 그대로 유효하다.

## 소유 밖에서 발견한 문제 (고치지 않음)

- F-M-1. `evidence_lib.py:85-91` 뉴스·SEC UA에 `SEC_UA` 원문 삽입 →
  비ASCII 연락처에서 전량 실패. §1.1 방향 참조.
- F-M-2. `collect_prices.py:22` NaN 종가 무검사 + `stages.py:383`
  일괄 검증 → 한 기업 NaN에 전체 실패·무기록. §1.2 방향 참조.
- F-M-3. `scorecard_cli.py:529-533` `resolve-cik` 에 `--json` 미배선
  (모듈에는 있음). 지시서의 `resolve-cik --json` 그대로는 실행 불가.
  레인 H 병합 뒤에도 같다.
- 5. **`tests/test_evidence_schema.py` 를 소유 밖인데 고쳤다.**
  같은 픽스처를 쓰는 `ResolveCikCliTest` 2건이 SPCX 등재로 깨졌고, 두지
  않으면 수락 기준(실패 증가 없음)을 어긴다. 조율자 `ask` 답변이 SPCX
  성질을 정했으므로 그 결정의 동일 성질을 최소 3행으로 반영했다. 계약
  변경 요청을 별도 `ask` 로 올리지 않은 것은 같은 성질의 중복 질의를
  피하기 위해서다. 조율자가 되돌리라면 되돌린다.

## 검증

| 명령 | 결과 |
| --- | --- |
| `uv run … -m unittest tests.test_collect_filings tests.test_resolve_cik tests.test_evidence_schema` | 38건 전부 통과 |
| `uv run … -m unittest discover -s tests -t .` (병합 후) | 1115건 실패 3·오류 14. 실패=훅 배선 2(환경, `/bin/bash`에 `uv` 없음, repo 코드와 무관)+`broad_tag_sweep` 1(원자료 부재). 오류 14건 전부 원자료 부재(`_raw` FileNotFound 13+`load_facts` None 1). 내 변경으로 늘어난 집합은 없다 |
| `uv run --frozen pytest -q` (병합 후) | 17 failed, 1100 passed. 실패 집합이 위와 같은 분류(훅 2+원자료 부재 15, subtest 분리 표기) |
| `npm run check` | 종료 코드 0 |
| `npm run test:node` | tests 10·pass 10·fail 0 |
| `git status --short` (정리 뒤) | 픽스처·테스트·보고서만. 임시 실행 폴더·`tmp-lane-m/` 삭제, `data/` 는 생기지 않음 |
| `git diff --stat HANSOLJJ/revision_checker...HEAD` | 소유 파일+보고서+`test_evidence_schema.py`(위 소유 밖 5)만 |
| 보고서 `SEC_UA` 값 | 없음(있음·길이 23만 기록) |
| 통합 병합 `git merge HANSOLJJ/revision_checker` | fast-forward `f05476b` 성공, 충돌 없음. 병합 뒤 테스트 다시 돌림(위 수치) |

## 남긴 것

- F-M-1~F-M-3 수정(레인 H 소유 파일).
- 훅 배선 2건의 환경 실패(`/bin/bash`에 `uv` 없음). 이 Windows 워크트리에서만
  난다. 코드와 무관하며 메커니즘(127, 실행 전 실패)이 자명해 별도 base
  실행은 하지 않았다.
- 임시 실행 폴더·`tmp-lane-m/` 은 삭제했고 커밋에 없다.
