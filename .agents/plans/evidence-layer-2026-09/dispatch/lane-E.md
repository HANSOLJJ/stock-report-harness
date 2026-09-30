# 레인 E — 근거 계층 연결: 스키마 확대(3.1) → collect 단계·research 등록·해시 결속(3.4)

에이전트: Claude Opus 5.5. 의존: 레인 A·B 병합 완료(통합 브랜치 기준). 공통 규약: `README.md` 를 먼저 읽는다. 계획 원문: `../plan.md` 3단계의 "입력 정의", "스키마", "해시 결속", 수집기 절의 CLI·`stages.collect` 부분.

## 시작 시점 상태 (2026-09-30 조율자 기록)

- 실행 묶음은 `output/<run_id>/` 이고 경로는 `scripts/scorecard/paths.py` 의 `run_paths(slug)` 로만 만든다. 기존 실행 2개(`ai-scorecard-2026-09-baseline`, `…-obsreg`)는 이미 옮겨졌고 두 실행 모두 `status` 의 `approval_valid: true` 다.
- 수집기 모듈은 모두 있다. `scripts/scorecard/evidence_lib.py`(유일한 urllib 지점 `fetch_bytes`, `DATA_ROOT`, `source_entry`, `upsert_sources`, `merge_items`), `collect_news.py`, `collect_filings.py`, `collect_prices.py`(유일한 yfinance 지점 `fetch_quote`), `resolve_cik.py`(모듈만, `--apply` 없음). 규칙 `scorecard/rules/v1.8.json` 도 있다(allowlist 없음).
- `engine.input_hashes` 는 지금 `run·observations·judgments·sources(있을 때)` 를 담고 `load_context` 가 `rules` 를 더한다. `stages.current_hashes` 는 6키(rules·observations·judgments·run·results·draft)다.
- 훅은 `scripts/hooks/guard.py` 다. `output/<slug>/evidence/**`·`*.json` 쓰기는 게이트가 없다. `output/<slug>/research.md` 를 Write 도구로 쓰면 같은 폴더 `plan.md` 가 필요하다.
- 테스트 기준: unittest 974건 중 실패 1·오류 14. 전부 `validation/*/_raw` 원자료가 워크트리에 없어서 난다. 이 집합이 늘면 안 된다.
- `baseline` 실행의 `engine.recompute_matches` 는 원래부터 False(저장 `0942c342…`, 재계산 `200d7b01…`)다. 이 값이 바뀌지 않아야 한다. `obsreg` 는 True 를 유지해야 한다.

## 소유 파일 (Ownership)

- `scripts/scorecard/schema.py`, `engine.py`, `stages.py`, `render_md.py`, `validate.py`, `registry.py`
- `scripts/scorecard/collect_prices.py`(아래 결함 수정), `collect_news.py`·`collect_filings.py`·`evidence_lib.py`·`resolve_cik.py`(연결에 필요한 최소 수정)
- `scripts/scorecard_cli.py`
- `tests/` 의 기존 파일(필요한 수정)과 새 테스트 `tests/test_evidence_schema.py`, `tests/test_collect_stage.py`, `tests/test_hash_binding.py`, `tests/test_evidence_e2e.py`, 새 픽스처 `tests/fixtures/evidence/**`

만지지 않는 것: `output/ai-scorecard-2026-09-*/**` 의 모든 파일(내용 변경 금지), `scorecard/rules/*.json`, `scorecard/companies.json`(아래 설명), `scorecard/history.csv`, `scripts/hooks/**`, `server.js`, `server/**`, `.claude/**`, `docs/**`, `AGENTS.md`, `README.md`.

## 3.1 스키마 확대

커밋 메시지: `feat(schema): sources·evidence·triggers 검증, companies cik·news_queries`

1. `validate_companies`. `COMPANY_OPTIONAL_KEYS` 에 `cik`(int 또는 null), `news_queries`(비어 있지 않은 문자열 리스트)를 더한다. `aggregate`·calc 가 이 키를 읽지 않으므로 `results_hash` 는 불변이어야 한다(테스트로 고정).
2. `registry.set_company_field(company_id, key, value, *, path=COMPANIES_PATH)`. 한 줄 형식(`render_company_line`)을 유지하며 허용 키(`cik`, `news_queries`)만 바꾼다. 다른 줄의 바이트는 그대로다.
3. `scorecard_cli.py resolve-cik [--company id] [--from-file PATH] [--apply]`. `resolve_cik` 모듈을 부르고 결과를 표로 낸다. `--apply` 는 `resolved` 인 것만 `set_company_field` 로 쓴다. **이 과제에서 `--apply` 를 실제 `companies.json` 에 실행하지 않는다.** `SEC_UA` 가 없고 픽스처는 합성이다. 테스트는 임시 사본으로 한다. SPCX 는 사용자가 CIK 를 확인한 뒤 따로 넣는다.
4. `validate_sources(payload, run_id)`. 최상위 `{schema, run_id, items}`(기존 두 실행의 실제 최상위 키를 먼저 확인하고 그대로 허용한다). 항목 필수 8키 `source_id, title, publisher, url, accessed_at, sha256, conflict_of_interest, note`, 선택 `kind, company_id, published_at_utc, publisher_url, raw_ref`. 중복 `source_id` 는 오류.
5. `validate_evidence(payload, companies, source_ids, run_id)`. 최상위 `{schema: "scorecard.evidence/1", run_id, items}`. 항목 키는 `evidence_id`(`^EV-<company_id>-\d{3}$`), `company_id`, `factors`(F1~F9 부분집합, 비어 있지 않음), `kind`(news|filing), `source_id ∈ source_ids`, `published_at_utc`(ISO Z 또는 null), `title`, `excerpt`(≤600자), `relevance`(문자열), `channel`(disclosure|press|company_statement|secondary), `conditional_impact`(문자열 또는 null, 숫자 금지 C-14), `horizon`, `counter_evidence`(리스트), `unverified`(리스트), `change_vs_previous`(new|updated|unchanged|null), 선택 `previous_evidence_id`, `reviewer`, `reviewed_at`, `status`(candidate|confirmed).
6. `validate_triggers(payload, companies, evidence_ids, source_ids, run_id)`. `{schema: "scorecard.triggers/2", run_id, items}`. 항목 `trigger_id`(`^TRG-\d{3}$`), `company_id`, `factors`, `observation`, `condition`, `deadline`(날짜), `evidence_ids ⊆ evidence`, `source_ids ⊆ sources`, `status`(watching|fired|expired|withdrawn), `recheck{factors, what}`, 선택 `legacy_ref`, `note`. 미래 점수 필드(`score`, `expected_score`, `target_score` 등 점수처럼 보이는 키)는 거부한다.
7. `validate_judgments` 에 선택 키 `evidence_ids` 를 허용한다.
8. `validate_cross_refs(observations, judgments, evidence, sources)`. `obs.source_id ∈ S`, `jud.source_ids ⊆ S`, `ev.source_id ∈ S`, `status: new` 판단의 `evidence_ids` 는 모두 `confirmed`. **기존 두 실행이 이 검사를 통과하는지 먼저 확인한다.** 통과하지 않으면 검사를 완화하지 말고 `ask` 로 조율자에게 보고한다.
9. `engine.load_context`. `validate_sources` 는 항상, evidence·triggers 는 파일이 있을 때만 검증하고 교차 검사를 돈다. `RunContext` 에 `evidence`, `triggers`(없으면 None)를 더한다.

## 3.4 collect 단계·research 등록·해시 결속

커밋 메시지: `feat(stages): collect 단계, research 근거 등록·렌더링, 해시 결속`

### collect

- `stages.collect(slug, *, companies=None, kinds=("news","filings","prices"), since=None, forms=None, locale="en-US", from_file=None, dry_run=False)` 와 CLI `scorecard_cli.py collect <run_id> [--company a,b] [--kind news|filings|prices|all] [--since YYYY-MM-DD] [--forms …] [--locale en-US] [--from-file PATH] [--dry-run]`.
- `run.companies` 를 순회해 수집 캐시(`DATA_ROOT/<company_id>/…`)를 갱신한다. 후보 창은 `since`(기본 `run.as_of − 180일`) ≤ published ≤ `run.info_cutoff`(C-17, 없으면 `as_of`). 창 밖은 버린다.
- `output/<run_id>/evidence/candidates.json` 을 결정론적으로 쓴다. 같은 입력이면 같은 바이트(정렬 키 고정, `accessed_at` 같은 시각 필드는 후보 파일에 넣지 않거나 입력에서 온 값만). 스키마 `scorecard.candidates/1`, 항목은 `candidate_id`(뉴스 `article_id`, 공시 `filing_id`), `company_id`, `kind`, `title`, `url`, `published_at_utc`, `source{name,url}` 또는 `form`, `raw_ref`, `content_hash`.
- 뉴스·공시는 `sources.json` 을 **건드리지 않는다**(선별 전 항목으로 해시가 흔들리지 않게).
- **`--kind prices` 만 예외**로 `observations.json` 에 가격·시총 관측을 넣고 `sources.json` 에 `SRC-YF-<날짜>` 를 등록한다. 같은 `(company, metric, as_of)` 관측이 이미 있으면 덮어쓰지 않고 오류로 멈춘다. 비상장 2사는 건너뛴다.
- `SEC_UA` 가 없으면 filings 는 `skipped_no_user_agent` 로 기록하고 나머지는 진행한다(전체를 실패시키지 않는다).
- research 단계 앞에서만 실행한다. build 는 재수집하지 않는다(D-02).

### collect_prices 결함 수정 (레인 B 병합 때 조율자가 발견)

- 지금 `fetch_quote` 는 yfinance 의 `fast_info.market_cap`·`shares` 를 쓰는데, 이 값은 **조회 시점** 값이다. 그런데 관측의 `as_of` 는 과거 종가 날짜가 된다. 과거 기준일로 조회하면 날짜와 값이 어긋난다.
- 고치는 방향. (1) 조회일(UTC 날짜)이 `close_date` 와 같거나 하루 이내일 때만 `vendor_market_cap` 을 쓴다. (2) 그 밖에는 `price_x_shares` 로 계산하되, 발행주식수가 조회 시점 값이라는 사실을 `basis.shares_as_of`(조회일)와 `basis.shares_timing: "current_at_fetch"` 로 남긴다. (3) ADR(`share_basis` adr·ads)은 `price` 가 ADR 1주 가격이고 `shares_outstanding` 이 무엇을 세는지(보통주인지 ADR 인지) yfinance 가 보장하지 않는다. ADR 의 시총은 `vendor_market_cap` 만 쓰고, 그것도 없으면 `status: collection_failed` 로 둔다. 추정으로 채우지 않는다. (4) 쓰지 않는 인자 `price_as_of` 를 정리한다.
- 기존 관측 형식(`nvidia.market_cap.v15` 등, unit `USD`, 값은 달러 금액)과 같은 단위를 유지한다.

### research 등록·렌더

- `stages.research`: `evidence/evidence.json` 이 있으면 인용된 후보의 `source_entry` 를 `sources.json` 에 `upsert_sources` 로 추가한다(추가만, 기존 id 불변). `--no-register` 로 끈다. 그 뒤 엄격 검증 → 렌더.
- `render_md` 의 research 에 새 절 `## 근거 자료`(기업별 표: evidence_id·factor·kind·제목 링크·발행시각·status·relevance 는 추론 표시)와 `## 트리거(활성)`(`triggers.json` 이 있으면 그것, 없으면 기존 legacy 트리거 서술을 그대로)를 더한다. **기존 두 실행의 research.md 는 다시 렌더하지 않는다.**
- research frontmatter 에 `evidence_hash`·`triggers_hash` 를 파일이 있을 때만 쓰고, `validate.py` 도 있을 때만 대조한다.

### 해시 결속

- `engine.input_hashes`: `evidence`·`triggers` 키를 **파일이 있을 때만** 추가한다. 기존 실행의 `results.input_hashes` 와 재계산 비교가 그대로 통과해야 한다.
- `stages.current_hashes`: 6키 + `sources` + `evidence`·`triggers`(있을 때). `approve`·`validate.py`·`render_html` 이 이 함수 하나를 쓰는지 확인한다.
- `schema.validate_approval`: `hashes` 에 6키 필수, `sources`·`evidence`·`triggers` 는 선택. **기존 두 실행의 `approval.json` 은 6키만 있다. 이들의 `approval_valid` 가 true 로 남아야 한다.** 비교는 "승인에 있는 키만 현재와 대조하되, 현재에 evidence·triggers 파일이 있는데 승인에 그 키가 없으면 무효" 로 한다. sources 는 기존 승인에 없으므로, sources 키가 승인에 없을 때는 대조하지 않는다(기존 실행 호환). 새 승인은 sources 를 반드시 담는다.

## 검증 (Observable acceptance)

- 기존 두 실행: `status` 가 두 실행 모두 `approval_valid: true`. `recompute_matches` 가 obsreg True, baseline 은 전과 같은 False 와 같은 두 해시. `output/ai-scorecard-2026-09-*` 아래 `git diff` 가 비어 있다.
- 종단 테스트 `tests/test_evidence_e2e.py`: 임시 `OUTPUT_DIR`·`DATA_ROOT` 에서 `init --rule v1.8`(가능한 최소 기업 수) → `collect --from-file`(뉴스는 기존 RSS 픽스처, 가격은 yfinance 픽스처, 공시는 SEC_UA 없는 경로) → 테스트 코드가 evidence.json 을 candidate 로 작성 → `research` → `calculate` → `draft` → `review-template` 까지 오류 없이 돈다. candidate 근거를 인용한 `status: new` 판단은 거부되고, confirmed 로 바꾸면 통과한다. evidence 를 고치면 `current_hashes` 가 바뀐다.
- 스키마 단위 테스트: 각 검증기의 필수 키 누락, 형식 위반, 교차 참조 위반, 트리거의 점수 필드 거부.
- `collect` 결정론: 같은 입력으로 두 번 돌리면 `candidates.json` 바이트가 같다. 입력 순서를 섞어도 같다.
- 가격 결함 수정 테스트: 과거 기준일 조회는 `vendor_market_cap` 을 쓰지 않는다. ADR 은 `price_x_shares` 를 쓰지 않는다.
- 테스트 집합: 기준(974건 중 실패 1·오류 14)에서 늘지 않는다. `npm run check`, `npm run test:node` 통과.
- 보고서 `validation/lane-E-evidence-wiring/REPORT.md` 를 커밋에 포함한다. 통합 브랜치 merge 가 권한으로 거부되면 우회하지 말고 보고서에 적는다(조율자가 병합한다).
