# 레인 E — 근거 계층 연결 보고서 (2026-09-30)

지시서 `.agents/plans/evidence-layer-2026-09/dispatch/lane-E.md` 의 3.1(스키마 확대)과 3.4(collect 단계·research 등록·해시 결속·가격 시점 결함)를 수행했다.

## 커밋

| SHA | 내용 |
| --- | --- |
| `9654b1c` | feat(schema): sources·evidence·triggers 검증, companies cik·news_queries |
| `b7df762` | feat(stages): collect 단계, research 근거 등록·렌더링, 해시 결속 |
| `57be181` | 통합 브랜치 `HANSOLJJ/revision_checker`(`9833b77`, 문서 한 줄) 병합. 충돌 없음 |
| (이 보고서 커밋) | docs(validation) |

## 시작 기준값 (변경 전)

- baseline: approval_valid True, recompute False (저장 `0942c342…`, 재계산 `200d7b01…`)
- obsreg: approval_valid True, recompute True (`4a3f6c05…`)
- 두 실행 sources.json 최상위 `{schema, run_id, items}`, 항목 8키만. 관측·판단의 source_id 는 모두 장부에 있다. 그래서 교차 검사를 완화 없이 전 실행에 적용했다.
- 두 실행 approval.hashes 6키, results.input_hashes 5키(run·observations·judgments·sources·rules).
- 테스트: unittest 974건 중 실패 1·오류 14.

## 계약 변경 (조율자 허가)

- 소유 밖 `render_html.py` build_scorecard(1719행)와 `compare.py` approval_state 가 승인 해시를 dict 등호로 비교했다. `current_hashes` 에 sources 를 더하면 기존 실행(승인 6키)이 깨지므로 `ask` 로 요청했고 허가받았다. 비교 규칙을 `stages.approval_mismatches` 한 곳으로 모으고 두 호출부를 각 1~3줄 바꿨다. render_html 882행 stale 계산은 승인 키만 돌므로 그대로 뒀다.
- 허가 조건 두 가지를 테스트로 넣었다. (1) `tests/test_hash_binding.py::NoDirectComparisonTest` 는 scripts/ 에서 `approval["hashes"]`·`current_hashes` 를 `==`/`!=` 로 직접 비교하는 줄이 0건임을 고정한다(패턴이 옛 세 형태를 잡는지도 따로 확인). (2) `ExistingRunsBuildTest` 는 기존 두 실행의 임시 사본으로 build_scorecard 를 돌린다. `ExistingRunsTest` 는 compare.approval_state 가 두 실행 모두 유효임을 확인한다.

## 한 일

### 3.1 스키마 확대

- `COMPANY_OPTIONAL_KEYS` 에 `cik`(양의 정수|null)·`news_queries`(비어 있지 않은 문자열 배열). obsreg 사본에 두 키를 넣어도 results_hash 가 같음을 테스트로 고정했다.
- `registry.set_company_field(company_id, key, value, *, path)`: 허용 키 두 개만, 대상 한 줄만 바꾸고(쉼표 보존) 사후 검증이 실패하면 원문으로 되돌린다.
- `scorecard_cli.py resolve-cik [--company] [--from-file] [--apply]`: 표를 내고 `--apply` 는 `resolved` 이면서 값이 다른 것만 쓴다. **실제 `companies.json` 에는 돌리지 않았다**(테스트는 임시 사본, `companies.json` 에 `"cik"` 가 없음을 테스트로 확인).
- `validate_sources`·`validate_evidence`·`validate_triggers`·`validate_cross_refs`, judgments 선택 키 `evidence_ids`.
- `engine.load_context`: sources 는 항상, evidence·triggers 는 파일이 있을 때 검증하고 교차 대조. `RunContext.evidence`·`triggers`(없으면 None).

### 3.4

- `stages.collect` 와 CLI `collect`. 후보 창은 `since`(기본 as_of−180일) ≤ 발행일 ≤ `info_cutoff`. `evidence/candidates.json` 은 `sort_keys` 와 `(company_id, kind, candidate_id)` 정렬로 쓴다.
- 뉴스·공시는 sources.json 을 건드리지 않는다. `--kind prices` 만 observations 와 `SRC-YF-<price_as_of>` 를 등록하고, 같은 `(company, metric, as_of)` 나 같은 observation_id 가 있으면 아무것도 쓰지 않고 멈춘다. 비상장은 `skipped_unlisted`. `SEC_UA` 가 없으면 공시는 `skipped_no_user_agent` 로 두고 나머지를 계속한다.
- collect_prices 결함 수정. `fetch_quote` 가 `fetched_at`(UTC 날짜)을 반환한다. 조회일이 종가일과 0~1일 차이일 때만 `vendor_market_cap`, 그 밖에는 `price_x_shares` 에 `shares_as_of`·`shares_timing: "current_at_fetch"`. ADR·ADS 는 `vendor_market_cap` 만 쓰고 못 쓰면 `collection_failed` 와 사유 note. `price_observations` 의 `price_as_of` 인자를 뺐다. 단위(`USD`, 달러 금액)는 그대로다.
- `stages.research(register=True)`: evidence.json 이 인용한 후보의 출처를 `source_entry`·`upsert_sources` 로 추가만 한다(`--no-register` 로 끔). raw 파일이 캐시에 있으면 sha256 을 센다. research.md 에 `## 근거 자료`(기업별 표, relevance 앞에 `(추론)`)와 `## 트리거(활성)`(triggers.json 이 있으면 watching 항목, 없으면 기준선 트리거를 초안과 같은 모양으로) 절을 더했다. frontmatter `evidence_hash`·`triggers_hash` 는 파일이 있을 때만 쓰고 validate.py 도 그렇게 대조한다.
- 해시 결속. `input_hashes` 는 evidence·triggers 를 파일이 있을 때만 더한다. `current_hashes` = 6키 + sources + evidence·triggers(있을 때). `validate_approval` 은 세 키를 선택으로 받는다. `approval_mismatches` 는 승인에 있는 키만 대조하고, 근거·트리거가 지금 있는데 승인에 없으면 무효, 필수 6키가 승인에 없어도 무효다.
- `collect_news` 에 `locale` 연결(기본 `en-US` 의 URL 은 전과 같다).

## 좁히거나 고른 것 (근거와 함께)

- `conditional_impact` 의 "숫자 금지(C-14)" 를 **점수 이동 표현 금지**로 읽었다. 숫자 타입과 `-3→-4`·`-2점` 꼴을 거부하고, "매출 20% 감소 시" 같은 조건 서술의 숫자는 허용한다. 계획서 136행이 "숫자 점수 금지" 라고 적었기 때문이다.
- 트리거의 미래 점수 필드는 키 이름 정규식 `score|점수|rating|points|delta|expected|target` 로 중첩까지 거부한다.
- `confirmed` 근거는 `reviewer`·`reviewed_at` 를 요구한다(지시서에는 없던 조건이다). 판단과 같은 규칙이고, 사람이 확인하지 않은 근거를 확정으로 올리는 길을 막는다. evidence `status` 가 없으면 `candidate` 로 본다.
- 후보 항목에 `source_id` 를 더했다. evidence 의 source_id 로 후보를 찾아 출처를 등록하려면 필요하다. 공시 후보는 제출일만 있으므로 `published_at_utc: null` 에 `filed_at`·`form` 을 두었다(시각을 지어내지 않는다).
- 발행일이 없는 기사는 창을 판정할 수 없어 후보에서 뺀다.
- 건너뜀 상태(`skipped_*`)는 candidates.json 에 넣지 않고 collect 반환값과 CLI 출력에만 둔다. 후보 파일을 캐시만의 함수로 두어야 결정론이 선다.
- `--from-file` 은 `--kind` 하나와 함께만 받는다(종류마다 파일 형식이 다르다).
- `stages.collect` 에 테스트용 `now` 인자를 두었다(CLI 에는 없음).
- `SRC-YF-<날짜>` 가 이미 있으면 upsert 가 기존 항목을 둔다. 같은 기준일에 기업을 나눠 수집하면 첫 수집의 url 만 남는다.
- research 의 `## 트리거(활성)` 은 `watching` 만 표로 싣고 나머지 상태는 건수만 적는다.
- CLI `init` 의 다음 단계 안내를 `collect → 후보 선별 → research` 로 바꿨다.

## 검증

| 명령 | 결과 |
| --- | --- |
| `uv run --frozen python -X utf8 -m unittest discover -s tests -t .` | 1030건, 실패 1·오류 14. 실패·오류 목록이 시작 기준(974건)과 **같다**. 늘어난 56건은 모두 새 테스트이고 통과 |
| `uv run --frozen pytest -q` | 15 failed, 1017 passed. 실패 테스트 이름 목록이 3.1 직후 실행과 같고, unittest 기준 13개 메서드와 같다(unittest 는 하위 테스트 2건을 따로 센다) |
| `npm run check` | 통과 |
| `npm run test:node` | 9건 통과 |
| 기존 두 실행 status·recompute | baseline approval_valid True, recompute (False, `0942c342…`, `200d7b01…`) 불변. obsreg approval_valid True, recompute True(`4a3f6c05…`) |
| `git diff --stat HANSOLJJ/revision_checker HEAD -- output/ scorecard/ scripts/hooks server.js server docs .claude AGENTS.md README.md` | 빈 출력 |

새 테스트 파일과 지시서 검증 항목의 대응.

- `tests/test_evidence_schema.py`(23건): 각 검증기의 필수 키 누락·형식 위반·교차 참조 위반·트리거 점수 필드 거부, 기존 두 실행 통과, set_company_field 한 줄 변경, resolve-cik 표·`--apply`, results_hash 불변.
- `tests/test_collect_stage.py`(13건): 창(C-17), 후보 필드에 시각 없음, 뉴스·공시가 sources 불변, SEC_UA 없는 공시, dry-run 무기록, 결정론(같은 입력 두 번·기업 순서 뒤집기·캐시 항목 순서 섞기 모두 같은 바이트), 가격 관측·출처 등록, 중복 관측 거부(파일 불변).
- `tests/test_collect_prices.py` 추가분: 과거 기준일 조회는 `vendor_market_cap` 을 쓰지 않는다, ADR 은 `price_x_shares` 를 쓰지 않는다, `fetch_quote` 가 조회일을 남긴다.
- `tests/test_hash_binding.py`(13건): 기존 실행 승인·재계산 불변, 대조 규칙, grep 고정, 기존 실행 빌드.
- `tests/test_evidence_e2e.py`(2건): 임시 OUTPUT_DIR·DATA_ROOT·companies 사본에서 CLI 로 `init --rule v1.8`(nvidia·openai) → `collect --kind news --from-file RSS` → `collect --kind prices --from-file yfinance` → `collect --kind filings`(SEC_UA 없음) → 테스트가 evidence·triggers 작성 → `research` → candidate 근거를 인용한 새 판단으로 `calculate` 거부 → confirmed 로 바꾸면 `research`·`calculate`·`draft`·`review-template` 통과 → evidence 수정 시 current_hashes 에서 evidence 만 바뀌고 validate 가 research 의 evidence_hash 를 낡았다고 잡는다. `--no-register` 는 sources 를 건드리지 않고 엄격 검증에서 막힌다.

음성 대조: `approval_mismatches` 대신 옛 dict 등호였다면 obsreg 빌드가 sources 키 때문에 awaiting_user 로 멈춘다. `test_obsreg_builds` 가 그 경로를 지난다.

## 소유 밖에서 발견한 것 (고치지 않음)

- **baseline 실행은 재빌드할 수 없다.** `build_scorecard` 사전 검사가 "재계산 결과가 저장된 results.json 과 다름" 한 건으로 멈춘다. 레인 E 이전부터의 상태(recompute False)이고 awaiting_user 가 아니다. 승인 검사는 통과한다. 체크리스트의 "감사 링크 재빌드" 후속 항목에 영향이 있다. `ExistingRunsBuildTest.test_baseline_stops_only_on_its_known_recompute_mismatch` 가 이 상태를 고정한다.
- 초안(`render_draft`)의 `## 트리거` 절은 여전히 기준선 트리거를 그린다. 지시서는 research 만 요구했고, 계획서 137행은 "렌더러는 이 파일이 있으면 legacy 39건 대신 그린다" 라고 적었다. HTML 도 같다.
- `init --from-run` 은 evidence·triggers 를 이어받지 않고, 이전 실행 승인 무효 판정(`_inputs_from_run`)은 5키만 본다.
- `render_html.py` 882행 stale 표는 승인 키만 돌므로, 승인 뒤 새로 생긴 evidence 는 무효 사유 표에 나오지 않는다(승인 무효 판정 자체는 build 게이트가 한다).

## 남긴 것

- 실제 SEC 조회(SEC_UA 필요), 실제 yfinance 조회. 테스트는 픽스처만 썼다. 픽스처 `yfinance_quotes.sample.json` 에는 `fetched_at` 이 없어 이 경로로는 벤더 시총을 쓰지 않는다(파일은 고치지 않았다).
- `companies.json` 의 cik 기입(`resolve-cik --apply`)과 SPCX CIK 확인은 사용자 몫이다.
- 뉴스 raw 파일명에 수집 시각이 들어가므로, 다른 시각에 같은 RSS 를 다시 수집하면 후보의 `raw_ref` 만 바뀐다. 캐시(입력)에서 온 값이라 규약 안이지만 한계로 적는다.
- `summary --json`·`confirm` 명령과 초안·HTML 의 근거 절은 4단계 몫이다.
