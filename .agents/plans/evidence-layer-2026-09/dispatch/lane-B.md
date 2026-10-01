# 레인 B — 근거 수집기: evidence_lib · Google News RSS · SEC EDGAR · yfinance 가격 · resolve_cik · 규칙 v1.8

에이전트: Muse. 의존: 없음(0단계 완료). 공통 규약: `README.md` 를 먼저 읽는다. 계획 원문: `../plan.md` 의 "3단계 근거 수집 계층" 중 수집기와 규칙 v1.8 절.

## 목표 (Target · Change)

채점표 실행에 근거를 자동으로 모으는 수집기 네 개와 공용 라이브러리를 **새 파일로만** 만든다. 기존 `stages.py`·`schema.py`·`scorecard_cli.py` 는 건드리지 않는다. 그 연결(`collect` 단계, CLI 서브커맨드, 스키마 확대, `companies.json` 의 `cik`·`news_queries` 키)은 후속 과제 3.1·3.4 가 한다. 규칙 v1.8 도 여기서 만든다. 두 커밋이다.

## 소유 파일 (Ownership, 모두 새 파일)

- `scripts/scorecard/evidence_lib.py`, `collect_news.py`, `collect_filings.py`, `collect_prices.py`, `resolve_cik.py`
- `scorecard/rules/v1.8.json`
- `tests/fixtures/README.md`, `tests/fixtures/google_news_rss.sample.xml`, `tests/fixtures/edgar_submissions.CIK0001045810.sample.json`, `tests/fixtures/company_tickers.sample.json`, `tests/fixtures/yfinance_quotes.sample.json`
- `tests/test_evidence_lib.py`, `tests/test_collect_news.py`, `tests/test_collect_filings.py`, `tests/test_collect_prices.py`, `tests/test_resolve_cik.py`, `tests/test_rules_v18.py`

만지지 않는 것: 그 밖의 모든 기존 파일. 특히 `scorecard/companies.json`, `scorecard/rules/v1.5.json`·`v1.6.json`·`v1.7.json`, `scripts/scorecard/schema.py`·`stages.py`·`engine.py`·`rules.py`, `scripts/scorecard_cli.py`, `.gitattributes`(`tests/fixtures/** -text` 는 조율자가 이미 넣었다), `.gitignore`(`data/` 는 이미 무시된다).

## 먼저 읽을 것

- `scripts/scorecard/schema.py`. `METRICS` 카탈로그에서 `price`·`market_cap` 의 unit·kind·basis 요건, `OBSERVATION_STATUSES`, `validate_observations` 의 시그니처. 가격 관측은 이 검증기를 통과해야 한다.
- `scripts/scorecard/engine.py` 와 `render_common.py`. `ROOT`, `load_companies`, sha256 도우미가 어디 있는지.
- `scripts/scorecard/rules.py`. `load_rules(version)` 과 allowlist 정책(`source_policy` 또는 그에 해당하는 속성)이 어떻게 노출되는지. `scripts/scorecard/validate.py` 의 `check_source_allowlist` 가 언제 호출되는지.
- `scorecard/runs/ai-scorecard-2026-09-obsreg/sources.json`. 출처 항목의 정확한 8키.
- `scorecard/companies.json`. 기업 항목 키(`company_id`, `display_name`, `ticker`, `listed`, `share_basis`, `adr_ratio`, `reporting_currency`).
- `tests/test_scorecard_fix64.py` 머리. 테스트의 import 방식(`sys.path.insert(0, ROOT / "scripts")`, `from scorecard import …`, unittest).

## 3.3 수집기

커밋 메시지: `feat(collect): evidence_lib·Google News RSS·EDGAR·yfinance 가격 수집기·resolve_cik`

### evidence_lib.py (표준 라이브러리만)

- `DATA_ROOT`. 환경변수 `SCORECARD_DATA_ROOT` 가 있으면 그 경로, 없으면 `ROOT / "data"`. 테스트가 덮어쓸 수 있게 모듈 변수로 둔다.
- `fetch_bytes(url, *, user_agent, timeout=20, retries=2) -> bytes`. **저장소에서 유일한 urllib 사용 지점이다.** 재시도 사이 1초 대기. 실패는 예외로 올린다. 빈 바이트를 돌려주지 않는다.
- `sha256_bytes(b)`, `parse_rfc2822(text) -> str | None`(UTC ISO 8601 `YYYY-MM-DDTHH:MM:SSZ`, 파싱 실패는 None), `utc_now_iso()`.
- `load_state(path)` / `save_state(path, state, keep_runs=20)`. `state.json` 에 조회 이력(`runs[]` 최근 20건)과 날짜별 카운터.
- `merge_items(existing, incoming, key) -> list`. key 기준 upsert. 기존 항목의 `first_seen_utc` 를 보존하고, 내용이 바뀌면 `updated_utc` 를 갱신하고, 결과는 key 로 정렬한다(결정론).
- `source_id_for_article(company_id, published_at_utc, content_hash)` → `SRC-NEWS-<cid>-<yyyymmdd>-<hash8>`. published 가 None 이면 `first_seen` 날짜를 쓰고 note 에 표시한다.
- `source_id_for_filing(accession_nodash)` → `SRC-EDGAR-<accession_nodash>`.
- `source_entry(item, *, kind, raw_sha256, accessed_at) -> dict`. 필수 8키 `source_id, title, publisher, url, accessed_at, sha256, conflict_of_interest(None), note` 와 선택 `kind, company_id, published_at_utc, publisher_url, raw_ref`.
- `upsert_sources(sources_payload, entries) -> dict`. 추가만 한다. 같은 `source_id` 가 있으면 기존 항목을 바꾸지 않는다.
- 정중한 기본 동작을 **코드 상수**로 둔다. `TOOL_NAME = "stock-report-harness-scorecard"`. `user_agent_for(kind)` 는 SEC 는 `SEC_UA` 환경변수 값을 그대로, 그 밖은 `f"{TOOL_NAME}/0.1 ({SEC_UA 값 또는 'contact unset'})"`. `GOOGLE_MAX_FETCH_PER_QUERY_PER_DAY = 4`, `SEC_SLEEP_S = 1.0`. 기사 본문 조회 함수는 두지 않는다.

### collect_news.py (Google News RSS, 표준 라이브러리만)

- `build_query_url(query, *, hl="en-US", gl="US", ceid="US:en") -> str`. `https://news.google.com/rss/search?q=<urlencoded>&hl=…&gl=…&ceid=…`.
- `parse_rss(xml_bytes) -> list[dict]`. `xml.etree` 로 item 의 title, link, guid, pubDate, description, source(텍스트와 `url` 속성)를 뽑는다.
- `normalize_article(raw_item, *, company_id, query, fetched_at, raw_ref) -> dict`. 필드는 `article_id = "google:" + guid`(순번 id 금지), `provider = "google_news_rss"`, `company_id`, `query`, `title`, `summary`(HTML 태그 제거), `source{name, url}`, `published_at_utc`(RFC 2822 → UTC, 실패 시 None 이고 `unverified: ["published_at"]`), `first_seen_utc`, `updated_utc: None`, `url`(link 그대로, 구글 리다이렉트 주소), `url_kind: "google_redirect"`, `url_is_fallback: False`, `content_hash`(title + summary + source.url 의 sha256), `raw_ref`. `revisions[]` 와 `published_at_local` 은 두지 않는다.
- `collect_company_news(company, *, fetch=fetch_bytes, from_file=None, dry_run=False, now=None) -> dict`. `company.get("news_queries")` 가 없으면 `display_name` 과 `ticker` 로 기본 질의를 만든다. 질의마다 URL 을 만들고, `dry_run` 이면 URL 목록만 돌려준다. `from_file` 이 있으면 네트워크 대신 그 파일을 읽는다. 하루 한도(`state.json` 의 `YYYY-MM-DD` 카운터)를 넘으면 조회하지 않고 `skipped_rate_limit` 를 기록한다. raw 는 `DATA_ROOT/<company_id>/news/google/raw/<yyyymmddTHHMMSSZ>-<hash8>.xml`, 정규화 결과는 `news/google/normalized.json` 에 merge 한다.

### collect_filings.py (SEC EDGAR submissions, 표준 라이브러리만)

- `SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik:010d}.json"`, `DEFAULT_FORMS = {"8-K", "10-Q", "10-K", "20-F", "6-K"}`, `ARCHIVE_BASE = "https://www.sec.gov/Archives/edgar/data/{cik}/{accession_nodash}/{primary_document}"`.
- `require_user_agent() -> str`. `SEC_UA` 가 없으면 명확한 메시지의 예외를 낸다("SEC_UA 환경변수가 필요하다 — 이름과 연락처"). **SEC 조회는 이 값 없이 절대 하지 않는다.**
- `parse_submissions(payload, *, forms, since) -> list[dict]`. `filings.recent` 의 병렬 배열(accessionNumber, filingDate, reportDate, form, primaryDocument, items)을 행으로 묶고 form 과 since 로 거른다.
- `normalize_filing(row, *, company_id, cik, raw_ref) -> dict`. `filing_id = "edgar:" + accession_nodash`, `company_id`, `cik`, `form`, `filed_at`, `report_period`, `accession`, `primary_document`, `primary_doc_url`, `items`(8-K 항목 문자열을 리스트로), `first_seen_utc`, `raw_ref`.
- `collect_company_filings(company, *, fetch=fetch_bytes, from_file=None, dry_run=False, since=None, forms=DEFAULT_FORMS, sleep=time.sleep) -> dict`. `company.get("cik")` 가 없으면 `skipped_no_cik`. 조회 사이 `SEC_SLEEP_S` 대기. raw 는 `DATA_ROOT/<company_id>/filings/raw/`, 색인은 `filings/index.json`.

### collect_prices.py (yfinance, 가격 전용)

- `fetch_quote(ticker, price_as_of) -> dict`. **저장소에서 유일한 yfinance 호출 지점이다.** `import yfinance` 는 이 함수 안에서 한다(모듈 import 시점에 네트워크나 의존을 요구하지 않는다). 반환은 `{close, close_date, market_cap, shares_outstanding, currency}`. `close_date` 는 `price_as_of` 이하의 마지막 거래일(휴장일이면 직전 거래일, 규칙 5.1). `market_cap` 은 벤더 값이 있으면 그것, 없으면 None.
- `price_observations(company, quote, *, price_as_of, source_id) -> list[dict]`. 상장사에 대해 관측 두 개를 만든다. `price`(unit `USD/share`, basis `{currency, share_basis, adr_ratio}`)와 `market_cap`(unit `USD`, basis `{method: "vendor_market_cap" | "price_x_shares", shares_outstanding}`). 공통은 `status: "verified"`, `kind: "actual"`, `as_of = quote["close_date"]`, `source_id`. 비상장(`listed: false`)은 빈 리스트. 통화가 USD 가 아니면 예외(ADR 은 USD 로 거래되므로 정상 경로에서는 나지 않는다). **스키마 `METRICS` 카탈로그가 요구하는 키와 형식을 정확히 맞춘다.** EPS·컨센서스 관련 필드는 어떤 형태로도 받지 않는다(AGENTS.md 수집 절, 옛 handoff 정책 4).
- `price_source_entry(price_as_of, *, tickers, accessed_at) -> dict`. `source_id = "SRC-YF-<price_as_of>"`, `url = "https://finance.yahoo.com/quote/<첫 티커>"`, 여러 티커면 `publisher_url` 에 목록, `publisher = "Yahoo Finance via yfinance"`, `sha256 = None`, `note` 에 "가격·시총 관측 전용, EPS·컨센서스 미수집".

### resolve_cik.py

- `COMPANY_TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"`. `SEC_UA` 필수.
- `load_ticker_map(payload) -> dict[str, int]`(대문자 티커 → cik). `resolve(companies, ticker_map) -> list[dict]`. 기업마다 `{company_id, ticker, cik | None, status: resolved | not_found | unlisted}`.
- `main(argv)`. `--from-file PATH`(캐시나 픽스처), `--company id` 필터, `--json`. 결과를 표준 출력에 낸다. **`companies.json` 에 쓰는 `--apply` 는 만들지 않는다.** 3.1 이 스키마와 함께 넣는다. 캐시는 `DATA_ROOT/_sec/company_tickers.json`.
- SPCX 가 목록에 없으면 `not_found` 로 두고 보고서에 적는다. 사용자가 CIK 1181412 후보를 확인할 예정이다.

### 픽스처

- `google_news_rss.sample.xml`. 실제 조회 1회(질의 `NVIDIA`) 결과를 그대로 저장한다. 크면 item 을 5개 이내로 줄인다.
- `edgar_submissions.CIK0001045810.sample.json`. **`SEC_UA` 가 환경에 있을 때만** 실제 조회한다. 없으면 SEC 문서의 submissions 형식대로 합성 픽스처를 만들고 `tests/fixtures/README.md` 에 "합성, 실제 응답으로 교체 필요" 라고 적는다. 실제 조회했으면 `filings.recent` 를 20건 이내로 줄인다.
- `company_tickers.sample.json`. 같은 조건. 합성이면 상장 12개사 티커를 넣고 SPCX 는 빼서 `not_found` 경로를 검사할 수 있게 한다.
- `yfinance_quotes.sample.json`. `fetch_quote` 의 반환 형식으로 상장 12개사 값. 실제 호출 1회(NVDA) 결과를 포함한다. 네트워크가 막히면 합성으로 하고 README 에 적는다.

### 테스트 (unittest 형식, 네트워크 금지)

- 각 모듈의 파서·정규화·id 생성·merge 결정론(같은 입력 두 번 → 같은 출력, 입력 순서 무관).
- `fetch` 를 주입해 raw 저장 경로와 `state.json` 카운터를 확인한다. 일일 한도 초과 시 조회하지 않는다.
- `require_user_agent` 가 `SEC_UA` 없이 예외를 내고, `collect_company_filings` 가 `SEC_UA` 없이는 주입된 fetch 를 한 번도 부르지 않는다.
- `price_observations` 출력이 `schema.validate_observations` 를 통과한다(검증기 시그니처에 맞는 최소 페이로드로). 비상장 2사는 빈 리스트. 출력 어디에도 EPS 키가 없다.
- **grep 고정 테스트.** `scripts/` 아래에서 `urllib` 를 import 하는 파일이 `evidence_lib.py` 하나다(기존 파일에 이미 있으면 그 목록을 허용 목록으로 고정하고 보고서에 적는다). `yfinance` 를 import 하는 곳이 `collect_prices.fetch_quote` 함수 안 하나다.
- `DATA_ROOT` 를 `tempfile` 로 바꿔 실제 `data/` 에 쓰지 않는다.

## 3.2 규칙 v1.8

커밋 메시지: `feat(rules): v1.8 — 원천 allowlist 블록 제거(personal use)`

- `scorecard/rules/v1.7.json` 을 복사해 `v1.8.json` 을 만든다. 바꾸는 것은 셋뿐이다. (1) 최상위 `sources` 블록 삭제. (2) `rule_version: "v1.8"`. (3) `note` 끝에 다음을 덧붙인다. ` | v1.8: 원천 allowlist 폐지. 개인 사용 목적이라 host 등재 절차를 두지 않는다(사용자 결정 2026-09-30). 2026-09-30 구글 뉴스 robots·약관 검토 결과(robots 는 /rss 차단, 일반 약관은 robots 위반 자동 접근을 남용으로 정의, 뉴스 약관은 개인 피드 리더 용도 허용)를 알고 내린 결정이다. 수집기의 자제(식별 UA·낮은 빈도·본문 미수집)는 코드 상수로 지킨다. 프로즈 참조는 docs/scorecard/rules/AI기업_채점규칙_v1.7.md 를 계속 쓴다.`
- 다른 키·순서·들여쓰기는 그대로 둔다. 먼저 `json.load` 뒤 `json.dump(indent=2, ensure_ascii=False)` 로 v1.7 을 임시 파일에 다시 써서 원본과 바이트가 같은지 확인한다. 같으면 그 방식으로 v1.8 을 쓴다. 다르면 텍스트 편집으로 블록만 지운다.
- `tests/test_rules_v18.py`. (a) v1.7 과 v1.8 을 dict 로 읽어 차이가 정확히 `sources` 부재·`rule_version`·`note` 셋인지. (b) `load_rules("v1.8")` 이 성공하고 allowlist 정책이 비어 있어 `validate.check_source_allowlist` 가 호출되지 않는지(mock 이나 결과로 확인). (c) 기존 두 실행 `engine.recompute_matches` 가 그대로 참인지(v1.7 고정이라 영향이 없어야 한다). (d) `scorecard/rules/v1.7.json` 의 sha256 이 이 과제 시작 시점과 같은지 고정한다(값을 테스트에 적는다).

## 실제 조회 확인 (각 1회, 보고서에 결과만 적는다)

- Google. `collect_company_news(nvidia, dry_run=True)` 로 URL 을 확인한 뒤 1회 실조회.
- SEC. `SEC_UA` 가 없으면 조회하지 않고 "미확인, SEC_UA 필요" 라고 적는다.
- yfinance. NVDA 1회.

## 검증 (Observable acceptance)

- 새 테스트 전부 통과. 기존 테스트의 실패·오류 집합이 `baseline-failures.txt` 와 같다.
- `git diff --stat HANSOLJJ/revision_checker...HEAD` 에 소유 밖 파일이 없다. 특히 `scorecard/rules/v1.7.json` 이 없다.
- `data/` 에 파일이 남았다면 실조회 확인에서 생긴 것이고 gitignore 라 커밋에 들어가지 않는다. `git status --short` 에 보이지 않아야 한다.
- 보고서 `validation/lane-B-collectors/REPORT.md`.
