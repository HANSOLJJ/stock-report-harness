# AI 기업 채점표: 근거 수집 계층 도입 + 종목 잔재 정리 + 실행 묶음 배치

작업 위치: `C:\Users\noble\orca\workspaces\stock-report-harness\revision_checker` (브랜치 `HANSOLJJ/revision_checker`, `main` 과 같은 커밋 b07334a). 종목 리포트는 폐기하고 채점표만 대상으로 한다. 커밋 메시지에 Co-Authored-By 를 넣지 않는다.

## Context

- 채점표(`scripts/scorecard/`)는 실행 묶음, 입력 해시, 사람 승인(`approve --by`, 6종 해시), 관측 상태 라벨, 4영역 리뷰, 테스트 866건을 이미 갖추고 있다. 개선점.md 제안의 대부분이 구현돼 있다.
- 빠진 것은 **근거를 자동으로 모으는 층**이다. 판단 114건은 전부 `reviewer: legacy:v1.5`·`status: carried`, 출처는 `SRC-v15-html` 하나, 트리거 39건은 `status: legacy` 문장이다. 뉴스·공시 수집 코드는 `scripts/` 에 없다. 2026년 11월 재채점에서 14개사 근거와 트리거를 갱신하려면 이 층이 필요하다(open-items P2·P6·P7).
- 실행 하나의 산출물이 여덟 곳(`scorecard/runs/`, `plan/`, `research/`, `drafts/`, `reviews/`, `reviews/_parts/`, `output/`, `validation/`)에 흩어져 있고, plan·draft·HTML 은 gitignore 라 승인 해시가 가리키는 draft 가 git 에 없다.
- 종목 리포트 전용 파일(스킬·명령·`output/` 산출물 70개·디자인 문서)과 공유 스크립트 안의 종목 코드 약 1,200줄이 채점표와 섞여 있다.
- `python`/`python3` 혼용, pyproject 없음. `scripts/validate_memory.py` 가 오류 3건으로 실패해 `npm test` 가 멈추고 memory 쓰기 훅이 막힌다.

## 확정된 결정 (사용자, 2026-09-30)

| 항목 | 결정 |
|---|---|
| 대상·위치 | 채점표만. 이 워크트리에서 작업, 완료 후 `main` 으로 합침 |
| Python 환경 | uv (`pyproject.toml` + `uv.lock`), pytest 는 dev 의존성. 훅은 표준 라이브러리 `python3` 유지 |
| 첫 원천 | Google News RSS + SEC EDGAR 공시 목록 + **yfinance 가격**(⑥ 의 `price`·`market_cap` 관측 전용. EPS 컨센서스 확대 금지, AGENTS.md 수집 절, 옛 handoff 정책 4. 종목 리포트의 차트용 yfinance 코드는 삭제) |
| 원천 정책 | **allowlist 폐지**(사용자 결정 2026-09-30, personal use). 규칙 v1.8 은 v1.7 에서 `sources` 블록(allowed·denied·not_adopted·unlisted·usage_scope)을 제거한다. 이로써 nasdaq.com·Yahoo 배제도 규칙에서 사라진다. 수집기는 정중한 기본 동작(식별 UA, 낮은 빈도, 본문 미수집)만 유지 |
| 수집 키 | `company_id`. 티커·별칭·CIK 는 `companies.json` 속성 |
| 실행 묶음 | `output/<run_id>/` 한 폴더. 기존 실행 2개도 같은 양식으로 이동해 과거 이력으로 보존 |
| 수집 데이터 | `data/<company_id>/` 공유, gitignore |
| git 추적 | 묶음의 텍스트·JSON·HTML(`report.html`, `audit.md`) 모두 추적 |
| 종목 코드 | 파일·코드 모두 삭제. 사유는 커밋 메시지와 context-notes 에. 9월 7일 "주석 처리" 규칙은 살아 있는 기능의 계약 변경에만 적용한다고 메모리에 보완 |
| 스킬·에이전트 | `stock-research` 문구 → `score-collect`, `fact-checker`·`report-designer` 재작성, `content-editor` → `evidence-editor` 로 전환해 score-review 연결 |
| 승인 | 기존 `approve` 유지 + 훅으로 에이전트 도구 호출 차단(방식 A) |
| 승인 UX | **브라우저 승인 페이지**(사용자 결정 2026-09-30). `node server.js --approvals` 로 사람이 띄운 서버만 `/approve/<run_id>` 를 제공하고 터미널에 일회용 코드를 찍는다. 페이지에서 근거 확정 체크·승인·취소. Node 는 화면만, 검증·지문·기록은 Python CLI(`summary --json`, `confirm`, `approve`, `revoke`)가 한다. 에이전트와 대화로 승인하지 않는다 |
| 훅 실행기 | bash 훅 9개를 `scripts/hooks/guard.py` 한 모듈로 통합. 모든 배선(Claude·Codex·Antigravity·Muse)은 `uv run --frozen python -X utf8 scripts/hooks/guard.py <훅이름>` 한 줄. 시스템 python3·bash 의존 제거, 인코딩 문제 해소 |
| Codex | 계속 사용. `.codex/hooks.json`·`.codex/agents/*.toml` 은 함께 갱신. `.codex/hooks/*.sh` 9개는 `hooks.json` 이 이미 `.claude/hooks/*.sh` 를 부르므로 죽은 사본이라 삭제 |

## 최종 배치

```
.claude/  scripts/  tests/  docs/  memory/  AI_company_analysis_factor/  validation/   ← 유지
scorecard/                 공유 정의만: companies.json, rules/(v1.5~v1.8), baseline/, history.csv
data/<company_id>/         (새로, ignore) news/google/{raw/, normalized.json, state.json}, filings/{raw/, index.json, state.json}
data/_sec/                 company_tickers 캐시
output/<run_id>/           실행 묶음 = 최종 결과
  run.json  observations.json  judgments.json  sources.json  results.json  approval.json
  plan.md  research.md  draft.md  preview.md  review.md  review-parts/
  evidence/{candidates.json, evidence.json}  triggers.json
  report.html  audit.md
```

`plan/ research/ drafts/ reviews/ scorecard/runs/ design/ sample/` 은 비워져 사라진다. `validation/` 934개는 이력 보관소로 그대로 둔다.

## 단계 개요

```
0  환경·위생      uv, pytest, memory validator 수정, .agents/plans 3종
1  정리·재활용    종목 파일 삭제 → 종목 코드 삭제 → 스킬·에이전트 문구 이식
2  묶음 배치      경로 도우미 하나로 통일, 기존 실행 2개 이동(해시 보존), 훅·서버·테스트 경로
3  근거 계층      companies cik·news_queries, 수집기 2종, evidence/triggers 스키마, sources 검증, 해시 결속, 규칙 v1.8
4  훅·스킬        승인 보호, PowerShell 매처, score-collect 신설과 score-* 개정, 문서
5  (개요) 캐시·증분·평가 표본·지표
```

각 단계 커밋마다 `uv run pytest -q` 와 `npm test` 통과가 게이트다.

## 0단계: 환경·위생

1. `pyproject.toml`: `requires-python = ">=3.12"`, `dependencies = ["pyyaml>=6", "yfinance>=1.7"]`(PyYAML 은 frontmatter 파싱 `report_contract_lib.py:173`, yfinance 는 3단계 가격 수집기용. 이 머신의 1.7.0 으로 lock), `[dependency-groups] dev = ["pytest>=8"]`, `[tool.pytest.ini_options] testpaths = ["tests"]`. `.python-version` = 3.12. `uv lock` → `uv.lock` 커밋.
2. `package.json`: `check` → `uv run python -m compileall -q scripts`; `validate:memory`·`validate:report`·`build:report`·`scorecard`·`test:scorecard` 전부 `uv run --frozen python -X utf8 …`. unittest discover 는 그대로 두고 pytest 를 추가 러너로. `inject-memory-context.sh` 와 `enforce-memory.sh` 안의 `python3` 호출도 같은 명령으로 바꿔 memory 안내의 한글 깨짐(cp949 출력)을 즉시 해소한다. 4단계에서 이 두 훅도 `guard.py` 로 흡수된다.
3. memory validator 수정(내용은 보존, 형식만): `memory/_daily/2026-09-11.md` 첫 줄 `# 2026-09-11`, 헤더 3개를 `## Entry: 2026-09-11 — <제목>` 으로, 각 entry 아래 `- **상황**/**증상**/**원인**/**해결**/**검증**` 5개 불릿을 기존 문장으로 채움. `memory/topics/guardrails.md` ENTRY-002/003/004 헤더를 `## ENTRY-00N: ` 로, `###` 소제목 2개를 굵은 단락으로, 각 ENTRY 를 `**상황**…**일자**` 6개 절로 재배열. `python3 scripts/validate_memory.py` 통과 확인.
4. `.agents/plans/evidence-layer-2026-09/{plan.md, checklist.md, context-notes.md}` 생성(글로벌 규칙 7, 로컬 전용).

## 1단계: 종목 잔재 정리 + 재활용

순서가 중요하다. 문구 이식 → 파일 삭제 → 코드 삭제.

1. 이식: `stock-research/SKILL.md` 의 규칙 문구(1차 출처 우선, URL 조작 금지·fallback 표시, 차단 시 누락 명시, 사실·추론 분리)를 `.claude/skills/score-collect/SKILL.md` 초안으로. `content-editor.md` → `evidence-editor.md`(근거 불릿 검사: 다른 기업 점수 인용 금지, 낡은 최상급 C-19, 금지 투자 표현, 불릿당 주장 하나와 `evidence_id`). `fact-checker.md`, `report-designer.md` 는 4단계에서 재작성.
2. `git rm`(한 커밋): `output/*.html` 4 + `output/assets/**` 65, `.claude/skills/stock-*` 7, `.claude/commands/stock-*` 6, `.agents/skills/stock-*` 14, `.codex/hooks/*.sh` 9, `.claude/hooks/enforce-citations.sh` + `settings.json` 배선 2곳 + `.codex/hooks.json` 배선, `design/toss_design.md`, `sample/skhynix.html`, `sample.png`, `docs/{stock-report-pipeline,pedagogy,visual-system,output-spec}.md`, `review.md`, `requirements.txt`. `protect-sensitive-files.sh` 보호 목록에서 `docs/output-spec.md` 를 같은 커밋에서 빼야 `rm` 이 막히지 않는다. `docs/finance-style-guide.md` 는 유지.
3. 코드 삭제(한 커밋, 테스트 게이트). 채점표 코드·테스트가 공유 스크립트에서 쓰는 이름은 `rel`, `read_markdown`, `ROOT`, `artifact_paths`, `frontmatter_value`, 디렉터리 상수 5개, `has_source_markers`(report_contract_lib), `validate_contract`·`ValidationResult`·`print_result`(validate_report_contract) 뿐이다.
   - `build_report.py` 911 → 약 40줄: `main` 만 남기고 `scorecard.render_html.build_scorecard(slug)` 호출 + 경로·미리보기 URL 출력. `--reuse-existing-price-chart`, `report_type_for` 분기, 종목 함수 33개 삭제. 파일은 진입점으로 유지(스킬·문서·훅 정규식이 가리킴).
   - `validate_report_contract.py` 505 → 약 80줄: `ValidationResult`, `print_result`, `validate_contract(slug, *, require_html, check_html_if_present)` → `validate_scorecard` 위임, `main`. `require_price_chart`·`check_price_chart_if_present` 인자 제거와 함께 `stages.approve` 호출부 수정. 토스 HTML 정규식·`_validate_*` 6개·보조 함수 4개 삭제. `scorecard/validate.py` 가 보조 함수를 import 하지 않는지 grep 확인.
   - `report_contract_lib.py` 350 → 약 150줄: 남김 = `ROOT`·`OUTPUT_DIR`(디렉터리 상수 4개는 2단계 `paths.py` 뒤 제거), frontmatter 파서 일체, `SOURCE_MARKER_RE`·`has_source_markers`, `ArtifactPaths`·`artifact_paths`(plan·research·draft·review·html 만), `rel`, `REQUIRED_SCORECARD_PLAN_FRONTMATTER`. 지움 = `ASSET_DIR`, `PRICE_CHART_FENCE_RE`·`price_chart_blocks`·`parse_key_value_block`, `strip_source_markers`, 이미지 키 상수 3개, `iter_json_strings`·`prohibited_image_generation_hits`·`selected_image_path`·`hero_image_status`, `REQUIRED_PLAN_FRONTMATTER`·`REQUIRED_DRAFT_SECTIONS`, `REPORT_TYPES`·`DEFAULT_REPORT_TYPE`·`report_type_for`. `heading_titles`·`has_required_section`·`count_h1`·`load_json`·`html_attr`·`html_text` 는 채점표 쪽 사용 grep 뒤 미사용이면 삭제.
   - 훅은 이 단계에서 건드리지 않는다. hero·자산 접미사 로직은 4단계 `guard.py` 재작성에서 함께 사라진다.
   - 검증: `compileall`, 테스트 866건, 옮긴 실행 obsreg 로 `validate_report_contract.py <slug>` 와 `build_report.py <slug>` 결과가 삭제 전과 같은지.
4. 문서: `AGENTS.md` 종목 계약 절 제거, `README.md`·`docs/memory-system.md` 종목 서술 정리.

## 2단계: 묶음 배치

### 경로 도우미 하나 (`scripts/scorecard/paths.py`, 새 파일)

```python
@dataclass(frozen=True)
class RunPaths:
    slug: str; run_dir: Path
    plan: Path; research: Path; draft: Path; review: Path; review_parts: Path
    html: Path; audit: Path; evidence_dir: Path; evidence: Path; candidates: Path; triggers: Path
    def rel(self, name: str) -> str        # ROOT 기준 POSIX 문자열. 렌더러와 검증기가 같은 함수를 쓴다
def run_paths(slug: str) -> RunPaths       # 항상 OUTPUT_DIR/slug 아래
```

- `engine.py`: `RUNS_DIR` 를 `OUTPUT_DIR` 로, `run_dir(slug) = OUTPUT_DIR/slug`. `compare.py` 는 `run_dir` 를 쓰므로 자동 반영.
- `stages.py`: `PLAN_DIR` 등 모듈 전역 import 제거, 모든 단계가 `run_paths(slug)` 사용. `init_run` 은 `output/<slug>/` 에 생성.
- `render_md.py` L145·L219·L431 frontmatter 경로 문자열과 L93·L121·L478 본문 문자열 → `paths.rel(...)`. `validate.py` L131·L166·L185 비교도 `paths.rel(...)`.
- **이동한 실행 호환**: 기존 실행의 research·draft·review frontmatter 는 `plan/<slug>.md` 같은 옛 문자열을 갖고 있고 draft 는 해시 대상이라 고칠 수 없다. `validate.py` 가 `plan_source` 등에 대해 현재 문자열 **또는** 옛 문자열(`plan/<slug>.md`, `research/<slug>.md`, `drafts/<slug>.md`)을 허용하는 `LEGACY_SOURCE_STRINGS` 규칙을 둔다. 새 실행은 묶음 문자열만 나온다.
- `render_html.py`: HTML 과 audit 를 `paths.html`·`paths.audit` 에, 상대 링크는 `paths.audit.name`. `server.js`: `output/*/report.html` 한 단계 재귀, `.md` MIME, 디렉터리 요청 시 `report.html`.
- `report_contract_lib.artifact_paths` 는 묶음 경로만 반환(종목 분기 제거 뒤).

### 기존 실행 2개 이동 (한 커밋, 바이트 보존)

- `git mv scorecard/runs/<id>/* output/<id>/`, `research/<id>.md → output/<id>/research.md`, `reviews/<id>.md → output/<id>/review.md`, `reviews/_parts/<id>/ → output/<id>/review-parts/`.
- 원본 폴더(`E:\sourcecode\01_side_project\stock-report-harness`)에서 gitignore 라 git 에 없던 `plan/<id>.md`, `drafts/<id>.md`, `output/<id>.html`, `output/<id>-audit.md` 를 `output/<id>/{plan.md, draft.md, report.html, audit.md}` 로 복사해 추적 시작. 승인 해시가 가리키는 draft 가 처음으로 git 에 들어간다.
- `.gitattributes`: `scorecard/runs/ai-scorecard-2026-09-baseline/**` CRLF 고정과 `drafts/ai-scorecard-2026-09-baseline.md` CRLF 고정을 `output/ai-scorecard-2026-09-baseline/**`(json·md) 와 `output/ai-scorecard-2026-09-baseline/draft.md` 로 같은 커밋에서 옮긴다. `output/**/*.{json,md,html} text eol=lf` 를 기본으로 두고 baseline 예외를 뒤에 둔다. `tests/fixtures/** -text`.
- `.gitignore`: `output/` 제외 삭제, `data/` 추가, `plan/*`·`drafts/*` 줄 삭제, `.agents/`·`.codex/` 는 추적 파일 정리 뒤 유지.
- 검증: `uv run python -X utf8 scripts/scorecard_cli.py status <id>` 가 두 실행 모두 `approval_valid: true`(이 워크트리에서는 draft 가 없어 지금은 false 이므로, 이동 뒤 true 가 되면 해시 보존이 증명된다). `results` 재계산 일치.

### 훅·테스트

- `enforce-plan.sh` 매핑: `output/<slug>/plan.md` 자유, `research.md` 는 plan, `draft.md` 는 +research, `review.md` 는 +draft, `report.html` 은 +review pass(`output/<slug>/review.md`), `review-parts/**`·`*.json`·`evidence/**` 는 게이트 없음. slug 는 파일명 stem 이 아니라 `output/` 다음 폴더명. 빌드 정규식 `(?:uv\s+run\s+)?python3?(?:\s+-X\s+utf8)?\s+scripts/build_report\.py\s+(slug)`.
- `remind-review.sh`: 대상 `output/<slug>/{draft.md, judgments.json, observations.json, evidence/*.json}`; Stop 검사는 리뷰 frontmatter `results_hash`·`draft_hash` 와 현재 해시 비교; 안내 `/score-review`. `forbid-financial-advice.sh`: 대상에 `output/*/draft.md`, `**/judgments.json`, `**/evidence/*.json` 추가.
- 테스트: 49개 파일의 `ROOT / "scorecard" / "runs" / <slug>` 를 `ROOT / "output" / <slug>` 로, `plan/`·`drafts/`·`output/<slug>.html`·`reviews/` 참조를 묶음 경로로 기계적 치환. `test_scorecard_continue_run.py` 샌드박스는 `engine.OUTPUT_DIR` 를 patch. 새 `tests/test_layout_paths.py`: `run_paths` 문자열, 이동한 실행의 frontmatter 옛 문자열 허용, `init_run` 이 묶음을 만드는지. `sync_outputs.py` 삭제(묶음이 추적되므로 불필요).

## 3단계: 근거 수집 계층

### 입력 정의

- `companies.json` 선택 키 `cik: int|null`, `news_queries: list[str]`. `schema.validate_companies` optional 확대(`aggregate`·calc 는 이 키를 읽지 않아 `results_hash` 불변). 한 줄 형식 유지(`registry.render_company_line`).
- `scorecard_cli.py resolve-cik [--company id] [--apply]`: `https://www.sec.gov/files/company_tickers.json`(허용 host, `SEC_UA` 환경변수, 초당 1회)으로 티커 → CIK. `registry.set_company_field()` 신설. SPCX 는 목록에 없을 수 있어 `validation/f6h-source-batch-10/collect.py` 의 1181412 를 사용자 확인 뒤 수동 설정. 비상장 2사는 null.

### 수집기 (표준 라이브러리만)

- `scripts/scorecard/evidence_lib.py`: `fetch_bytes(url, *, user_agent, timeout, retries=2)` 가 유일한 네트워크 지점. `sha256_bytes`, `parse_rfc2822`, `load_state/save_state(keep_runs=20)`, `merge_items(existing, incoming, key)`, `source_id_for_article`("SRC-NEWS-<cid>-<yyyymmdd>-<hash8>"), `source_id_for_filing`("SRC-EDGAR-<accession>"), `source_entry(item, kind, raw_sha256, accessed_at)`, `upsert_sources`(추가만, 기존 id 불변), `DATA_ROOT`(테스트가 덮어씀).
- `collect_news.py`: `build_query_url(query, hl, gl, ceid)`, `parse_rss(xml)`, `normalize_article(...)`, `collect_company_news(company, *, fetch, from_file, dry_run)`. 레코드: `article_id="google:"+guid`(순번 id 금지), provider, company_id, query, title, summary(HTML 제거), source{name,url}, published_at_utc(RFC 2822 → UTC, 없으면 null 로 두고 unverified 표시), first_seen_utc, updated_utc|null, url(실제 조회한 Google 리다이렉트), url_kind, url_is_fallback, content_hash, raw_ref. `revisions[]`·`published_at_local` 은 두지 않는다(표시 시 +09:00 고정 변환).
- `collect_filings.py`: `SUBMISSIONS="https://data.sec.gov/submissions/CIK{cik:010d}.json"`, 기본 form `{8-K,10-Q,10-K,20-F,6-K}`, `SLEEP_S=1.0`, `require_user_agent()`, `resolve_cik`, `parse_submissions(payload, forms, since)`, `normalize_filing`. 레코드: `filing_id="edgar:"+accession_nodash`, company_id, cik, form, filed_at, report_period, accession, primary_document, primary_doc_url(`www.sec.gov/Archives/...`), items, first_seen_utc, raw_ref.
- `collect_prices.py`(yfinance, 가격 전용): `fetch_quote(ticker, price_as_of) -> {close, close_date, market_cap, shares_outstanding, currency}` 하나가 유일한 yfinance 호출. `price_observations(company, quote, *, price_as_of, source_id) -> list[dict]` 가 상장 12개사에 대해 `price`(`USD/share`, basis `{currency, share_basis, adr_ratio}`)와 `market_cap`(`USD`, basis `{method: "vendor_market_cap" | "price_x_shares", shares_outstanding}`) 관측을 `status: verified`, `kind: actual`, `as_of = 실제 거래일`(휴장일이면 직전 거래일, 규칙 5.1)로 만든다. 출처 `SRC-YF-<price_as_of>` 를 `sources.json` 에 등록(`url: https://finance.yahoo.com/quote/<ticker>`, `accessed_at`). 비상장 2사는 건너뛴다. EPS·컨센서스는 받지 않는다(AGENTS.md 수집 절, 옛 handoff 정책 4). 테스트는 저장된 응답 픽스처(`tests/fixtures/yfinance_quotes.sample.json`)로.
- CLI `scorecard_cli.py collect <run_id> [--company a,b] [--kind news|filings|prices|all] [--since YYYY-MM-DD] [--forms …] [--locale en-US] [--from-file PATH] [--dry-run]` → `stages.collect`: `run.companies` 순회, 캐시 갱신, 후보 창 `since`(기본 `as_of − 180일`) ≤ published ≤ `run.info_cutoff`(C-17), `evidence/candidates.json` 을 결정론적으로 기록. 뉴스·공시는 `sources.json` 을 건드리지 않는다(선별 전 항목으로 해시가 흔들리지 않게). **`--kind prices` 만 예외**로 `observations.json` 에 관측을 넣고 `sources.json` 에 출처를 등록한다. 가격은 선별 대상이 아니라 계산 입력이기 때문이다. 같은 `(company, metric, as_of)` 관측이 이미 있으면 덮어쓰지 않고 오류로 멈춘다(스키마의 중복 규칙). research 단계 앞에서만 실행하고 build 는 재수집하지 않는다(D-02).
- `stages.research`: `evidence.json` 이 있으면 인용된 후보의 `source_entry` 를 `sources.json` 에 upsert(`--no-register` 로 끔) → 엄격 검증 → 렌더(새 절 `## 근거 자료`, `## 트리거(활성)`).

### 스키마 (`schema.py`)

- `validate_sources(payload, run_id)`: 최상위 `{schema, run_id, items}`, 항목 필수 8키(`source_id, title, publisher, url, accessed_at, sha256, conflict_of_interest, note`; 기존 두 실행이 정확히 이 형태), 선택 `kind, company_id, published_at_utc, publisher_url, raw_ref`. 중복 id 오류.
- `validate_evidence(payload, companies, source_ids, run_id)`: 항목 `evidence_id("EV-<cid>-<NNN>"), company_id, factors[F1..F9], kind(news|filing), source_id ∈ sources, published_at_utc, title, excerpt(원문 그대로 ≤600자), relevance(추론, 표시), channel(disclosure|press|company_statement|secondary), conditional_impact(str|null, 숫자 점수 금지 C-14), horizon, counter_evidence[], unverified[], change_vs_previous(new|updated|unchanged|null), previous_evidence_id?, reviewer, reviewed_at, status(candidate|confirmed)`.
- `validate_triggers(payload, companies, evidence_ids, source_ids, run_id)`: `scorecard.triggers/2`. 항목 `trigger_id("TRG-<NNN>"), company_id, factors[], observation, condition, deadline, evidence_ids ⊆ evidence, source_ids ⊆ sources, status(watching|fired|expired|withdrawn), recheck{factors, what}, legacy_ref?, note?`. 미래 점수 필드는 거부(design-guideline L272). 렌더러는 이 파일이 있으면 legacy 39건 대신 그린다.
- `validate_cross_refs(observations, judgments, evidence, sources)`: `obs.source_id ∈ S`, `jud.source_ids ⊆ S`, `ev.source_id ∈ S`, `status: new` 판단의 `evidence_ids`(judgment 선택 키 신설)는 모두 `confirmed`. 기존 두 실행이 이미 만족하므로 전 실행에 엄격 적용.
- `engine.load_context`: `validate_sources` 항상, evidence·triggers 는 파일이 있을 때 검증, 교차 검사. `RunContext` 에 `evidence`, `triggers`.

### 해시 결속

- `engine.input_hashes`: `evidence`·`triggers` 키를 **파일이 있을 때만** 추가. 기존 실행의 `results.input_hashes`(정확히 run·observations·judgments·sources·rules)와 재계산 비교가 그대로 통과한다. 근거를 고치면 calculate → draft → review 를 다시 밟게 된다(의도).
- `stages.current_hashes`: 6키 + `sources` + evidence·triggers(있을 때). `approve`·`validate.py:258`·`render_html:1721` 이 이 함수 하나를 쓰므로 분기 없음. `validate_approval` 은 `hashes` 에 6키 필수, `sources/evidence/triggers` 선택.
- `render_research` frontmatter 에 `evidence_hash`·`triggers_hash` 를 있을 때만 쓰고 `validate.py:133` 도 있을 때만 검사.

### 규칙 v1.8

- `scorecard/rules/v1.8.json` = v1.7 복사에서 `sources` 블록 전체를 제거하고 `rule_version: "v1.8"`, `note` 에 "원천 allowlist 폐지. 개인 사용 목적이라 host 등재 절차를 두지 않는다(사용자 결정 2026-09-30). 2026-09-30 구글 뉴스 robots·약관 검토 결과(robots 는 /rss 차단, 일반 약관은 robots 위반 자동 접근을 남용으로 정의, 뉴스 약관은 개인 피드 리더 용도 허용)를 알고 내린 결정" 을 적는다.
- 검증기는 `rules.source_policy` 가 없으면 allowlist 검사를 건너뛴다(v1.5 와 같은 경로). `rules.source_violation`·`validate.check_source_allowlist` 코드는 v1.7 로 고정된 기존 실행을 위해 그대로 둔다.
- 새 실행은 `init --rule v1.8`. v1.5·v1.7 파일은 건드리지 않아 기존 실행 해시 불변. `tests/test_rules_v18.py`: v1.7 과의 차이가 정확히 `sources` 삭제·`rule_version`·`note` 인지, v1.8 컨텍스트에서 allowlist 검사가 호출되지 않는지, 기존 두 실행 `recompute_matches`.
- 수집기의 정중한 기본 동작은 정책이 아니라 코드 상수다. User-Agent 에 도구 이름과 `SEC_UA` 연락처, 구글 피드는 검색어당 하루 4회 이하, 기사 본문 미조회, SEC 는 초당 1회.

## 4단계: 훅 통합·승인 보호·스킬

### 훅을 Python 한 모듈 + `uv run` 한 줄로

지금 9개 `.sh` 의 판단 논리는 전부 안쪽 `python3 - <<'PY'` 히어독에 있고 bash 는 표준 입력을 넘기는 껍데기다. Windows 에서 겪은 문제(WSL bash 오인, `.sh` CRLF, 로그인 셸 작업 디렉터리, cp949 출력 깨짐)는 전부 이 껍데기에서 났다. 껍데기를 없앤다.

- 새 파일 `scripts/hooks/guard.py`: 훅 하나가 함수 하나. `main(argv)` 가 `<훅이름>` 을 받아 표준 입력 JSON 을 읽고, 판단 후 허용이면 조용히 0, 차단이면 `{"decision":"block","reason":…}` 출력 + 종료 코드 2. 저장소 루트는 `git rev-parse --show-toplevel` 로 찾고, `.claude/hooks` 대신 `scripts/hooks/` 가 없으면 조용히 0(무관한 폴더에서 불려도 무해). 함수 목록: `block_dangerous_bash`, `protect_sensitive_files`, `enforce_plan`, `forbid_financial_advice`, `remind_review`(경고만), `enforce_memory`, `inject_memory_context`(`memory_context.py` 흡수). `enforce_citations` 는 만들지 않는다.
- 공통 유틸(`extract_bash_command`, `extract_tool_paths`, 도구 이름 별칭 표)은 같은 모듈 안. 도구 이름 별칭 표는 `Bash`·`PowerShell`·Codex·Antigravity·Muse 가 보내는 이름을 우리 분기 이름으로 바꾼다(실제 이름은 배선 시 페이로드를 캡처해 채운다).
- 모든 배선의 명령은 하나: `uv run --frozen --directory <루트> python -X utf8 scripts/hooks/guard.py <훅이름>`. Claude 는 `<루트>` 에 `%CLAUDE_PROJECT_DIR%`, 다른 도구는 세션 폴더. timeout 은 첫 `uv run` 이 venv 를 만들 수 있으므로 10초.
- `.claude/hooks/*.sh`, `.claude/hooks/lib/` 삭제. `.gitattributes` 의 `*.sh eol=lf` 는 남겨도 무해.
- 테스트 `tests/test_hooks.py`: bash 없이 `guard.<함수>(payload_dict)` 를 직접 호출해 차단·허용을 확인. 위험 명령, 보호 경로, 단계 순서 위반, approve 명령, `approval.json` 쓰기, PowerShell 페이로드, 금지 표현.

| 훅(함수) | 처리 |
|---|---|
| `block_dangerous_bash` | 논리 그대로 이식 |
| `protect_sensitive_files` | 보호 목록: `docs/output-spec.md` 제거; **추가** `(^|/)approval\.json$`, `scorecard/rules/v1.5.json|v1.6.json|v1.7.json`, 이동한 실행 2개 폴더 `output/ai-scorecard-2026-09-{baseline,obsreg}/**`, `scorecard/history.csv`. 명령에 `scorecard_cli\.py\s+approve\b` 또는 `stages\.approve\b` 가 있으면 변경 여부와 무관하게 차단, `approval.json` 문자열 + 변경 명령이면 차단 |
| `enforce_plan` | 2단계 표의 묶음 경로 매핑, 빌드 정규식 완화, `review-parts/` slug 추출 수정, 잠금 파일 검사 |
| `forbid_financial_advice` | 대상에 `output/*/draft.md`, `**/judgments.json`, `**/evidence/*.json` 추가 |
| `remind_review` | 차단 → 경고. 리뷰 frontmatter 해시와 현재 해시 비교 |
| `enforce_memory`, `inject_memory_context` | 논리 그대로, `-X utf8` 로 출력 깨짐 해소 |
| 배선 `.claude/settings.json` | 9개 명령을 `guard.py` 호출로 교체. **PowerShell 매처 추가**(PreToolUse `PowerShell` → block_dangerous_bash, protect_sensitive_files, enforce_plan). 지금은 PowerShell 도구가 모든 훅을 우회한다 |
| 배선 `.codex/hooks.json`, `.codex/agents/*.toml` | 같은 `uv run` 명령으로 교체(Git Bash 경로 불필요). 훅 변경 시 Codex 가 신뢰 해시를 다시 물음. 배선 파일 간 차이를 잡는 테스트 하나 |
| `scorecard_cli.py approve` | CLI 계층에서 에이전트 환경변수(`CLAUDECODE`, `CLAUDE_CODE_ENTRYPOINT`, Codex·Orca 변수)가 있으면 "approve 는 사용자 터미널에서 실행한다" 로 거부. `stages.approve()` 는 영향 없음. TTY 검사는 두지 않는다 |
| 한계(AGENTS.md 에 명시) | 도구 호출 밖(사람 터미널, 훅 없는 에이전트)은 못 막는다. 첫 방어선은 해시 검증 코드, 훅은 두 번째 |

### 다중 에이전트 운영 (Orca 조율자·워커, 독립 세션 리뷰어, 예약 갱신)

- **훅 한 벌, 하네스별 배선**: 논리는 `scripts/hooks/guard.py` 하나, 배선은 도구별 파일에 같은 `uv run` 명령 한 줄. Codex 는 `.codex/hooks.json`(프로젝트 단위, 이미 있음). Antigravity 는 `~/.gemini/config/hooks.json` 에 Orca 의 `orca-status` 와 별개 프로필로 추가하되 전역 파일이므로 `guard.py` 가 저장소 밖에서는 조용히 0 으로 끝나는 성질에 의존한다. Muse 는 Claude 와 같은 형식의 훅 JSON 을 하나 더 두고 설정에서 가리킨다. Gemini CLI 는 대상에서 제외. 훅이 없는 CLI(qwen)는 `scorecard_cli`·검증기·빌더의 코드 거부에 맡긴다. `AGENTS.md` 에 "어느 하네스로 돌리든 통제는 코드가 한다" 를 적는다.
- **Antigravity·Muse 배선 전 확인 3건**(이 확인이 끝나기 전에는 배선에 의존하지 않는다): (1) 차단 표현. Orca 훅 본체가 `{"decision":"ask"}`·`{"decision":""}` 를 쓰므로 `block` + 종료 코드 2 를 차단으로 해석하는지 무해한 시험 명령으로 확인. (2) 표준 입력 JSON 의 필드·도구 이름(`tool_name`, `tool_input.command`) 캡처 후 `guard.py` 별칭 표에 등록. (3) 훅 프로세스의 작업 디렉터리가 세션 폴더인지, `uv run --directory` 로 루트가 맞게 잡히는지 로그로 확인. Orca 가 `orca agent hooks on/off` 로 파일을 다시 쓸 때 다른 프로필을 보존하는지도 본다.
- **첫 실행 지연**: 새 워크트리에서 첫 `uv run` 은 venv 생성으로 수 초가 걸릴 수 있다. Orca 워크트리 setup 에 `uv sync --frozen` 을 넣고 훅 timeout 은 10초.
- **공유 수집 캐시**: `evidence_lib.DATA_ROOT` 를 환경변수 `SCORECARD_DATA_ROOT` 로 덮어쓸 수 있게 해 워크트리가 여럿이어도 `data/` 를 한 곳에 둔다. 없으면 `ROOT/data`.
- **실행 잠금**: `output/<run_id>/.lock`(gitignore) 에 `{owner, started_utc, stage}` 를 쓴다. 소유자는 `SCORECARD_AGENT`(없으면 `ORCA_TERMINAL_ID`, 없으면 사용자명). CLI 단계는 다른 소유자의 잠금이 있으면 거부(`--force` 로 인수). `enforce-plan.sh` 는 잠긴 묶음에 대한 Write/Edit 를 같은 규칙으로 막는다. 승인·빌드는 잠금을 요구하지 않는다(사람 행위).
- **승인 거부 확대**: `cmd_approve` 의 에이전트 환경 검사에 `CLAUDECODE`, `CLAUDE_CODE_ENTRYPOINT` 외에 `CODEX_*`, `ORCA_TERMINAL_ID` 등 Orca 가 워커 터미널에 넣는 변수를 포함한다(구현 시 실제 변수명 확인).
- **리뷰어 추적**: `output/<run_id>/review-parts/<영역>.md` frontmatter 에 `reviewer_agent`, `session`, `reviewed_at` 을 두고 `review.md` 의 `reviewers` 에 모은다. 검증기는 `pass` 영역에 수행자가 비어 있으면 거부(지금 규칙 유지).
- **Stop 훅은 경고로**: `remind-review.sh` 는 조율자·워커 구조에서 워커의 턴 종료를 잘못 막는다(리뷰는 다른 세션이 한다). 채점표에서는 차단 대신 "판단·근거 변경으로 리뷰 해시가 무효화됨, `/score-review` 필요" 경고만 출력한다. 강제는 approve·build 시점의 해시 검증 코드가 맡는다. 서브에이전트 도구 호출도 같은 하네스의 훅을 지나므로 Claude 리뷰어는 별도 조치 없이 보호된다.
- 조율 규칙(회신 먼저, 핸들 반환, 3단계 완료)은 훅이 아니라 스킬·메모리 문서에 둔다.

### 승인 페이지 (방식 2)

- **Python 쪽 새 명령** (`scorecard_cli.py`, 논리는 `stages.py`):
  - `summary <run_id> --json`: preview 표 데이터(기업별 기준선/이번 점수·순위·변경 factor), 리뷰 4영역 결과와 체크리스트 fail 수, 근거 후보(`evidence/candidates.json`)와 선별·확정 상태, 활성 트리거, 미결 규칙 결정, 승인 대상 지문. `status`·`render_md` 의 기존 데이터 함수를 재사용한다.
  - `confirm <run_id> --evidence EV-…,EV-… [--reject EV-…]`: `evidence.json` 의 `status` 를 `confirmed` 로(또는 항목 제거). 지문이 바뀌므로 이후 calculate 부터 다시.
  - `approve <run_id> --by <이름> [--note] [--via browser|terminal]`: 기존 논리 + `approved_via` 기록.
  - `revoke <run_id> --by <이름> --note <이유>`: `approval.json` 삭제와 `output/<run_id>/revocations.jsonl` 에 이유 기록.
- **`server.js` 확장**: `--approvals` 플래그일 때만 `GET /approve/<run_id>` (페이지), `POST /approve/<run_id>/confirm|approve|revoke` 를 열고 시작 시 6자리 일회용 코드를 터미널에 출력한다. 요청은 127.0.0.1 만, POST 는 코드가 맞아야 처리, 승인 성공 후 서버는 종료한다. 데이터는 `uv run python scripts/scorecard_cli.py summary <run_id> --json` 을 자식 프로세스로 받아 렌더하고, 버튼은 해당 CLI 를 자식 프로세스로 실행한 뒤 stdout 을 그대로 보여 준다. 화면은 dashboard-design 규칙(320px 리플로우, 표 모바일 패턴)을 따른다.
- **사람의 흐름**: 에이전트가 "승인 대기" 를 보고하면 → 사람이 `node server.js --approvals` → 브라우저에서 페이지 확인 → 근거 체크 후 "근거 확정" (지문이 바뀌면 에이전트에게 calculate·draft·review 재실행을 시키고 페이지 새로고침) → 이름·코드 입력 후 "승인" → 에이전트에게 "빌드해". 에이전트에게 말하는 것은 "고쳐" 와 "빌드해" 만이다.
- **한계**(AGENTS.md 에 명시): 승인 모드 서버가 떠 있는 동안 브라우저 도구를 가진 에이전트가 터미널의 코드를 읽으면 누를 수 있다. 코드는 파일에 쓰지 않고, 서버는 승인 뒤 스스로 내려간다. 첫 방어선은 여전히 지문 검증이다.
- 테스트: `summary`·`confirm`·`revoke` 는 Python 단위 테스트, 서버 라우트는 `node --test` 로 코드 불일치·비로컬 요청 거부·`--approvals` 없을 때 404 를 확인.

스킬·에이전트·문서:
- 신설 `score-collect` SKILL + command: collect → 후보 선별(`status: candidate`) → `evidence.json`·`triggers.json` → `research`. 사람이 `confirmed` 로 올린다(judgments 와 같은 규칙). `not_disclosed`(발행사 확인) ≠ `unverified`(우리가 못 찾음) 명시.
- `score-research`: collect → 선별 → 자동 등록 → `research` 순서, 새 판단은 `confirmed` 근거만 인용. `score-goal`: plan 뒤 collect 삽입, `awaiting_user` 정지 유지. `score-review`: 리뷰어 입력에 evidence·triggers·sources 추가, evidence-editor 연결. `score-build`: 포트 규칙 이식(3000 사용 중이면 죽이지 않고 `PORT=<빈포트>`), URL `http://localhost:3000/<slug>/report.html`. `score-plan`: `--rule v1.8`. 나머지 score-* 는 경로 문구.
- `fact-checker.md`: source_ids ∈ sources, URL 이 실제로 열리는지(조작 URL 금지), `not_disclosed_confirmed` vs `unverified`, excerpt 원문 대조, `published_at_utc ≤ info_cutoff`, candidate 근거를 인용한 `status: new` 판단 없음. `report-designer.md`: structure.md 6절 대시보드 검사, 근거·트리거 절 가독성, audit 링크. `evidence-editor.md`: 1단계 초안 완성.
- `AGENTS.md` 채점표 전용으로 재작성, `README.md`, `docs/scorecard/structure.md` 2·5·7절 갱신.

## 5단계 (개요, 새 실행 두 개가 쌓인 뒤)

- 사건별 분석 캐시(키: 근거 content_hash + company_id + 기간 + 프롬프트/스키마 버전), 정기 갱신 시 신규·수정 근거만 재검토 표시, `data/` 정리와 `--since` 커서.
- `tests/fixtures/evidence/` 평가 표본(사람 라벨), 입력 순서 불변·정정 반영·무변경 재실행 테스트.
- `docs/scorecard/evidence-eval.md`: 실행별 선별 근거의 정확도를 리뷰어 판정과 대조.

## 구현 분할 (Orca 다중 에이전트)

통합 브랜치는 이 워크트리의 `HANSOLJJ/revision_checker`. 조율자와 최종 검증은 이 세션(Fable). Codex 는 토큰 소진으로 쓰지 않는다. 워커 워크트리는 `orca worktree create --name <레인> --base-branch HANSOLJJ/revision_checker --setup run --json`(setup 에서 `uv sync --frozen`) 뒤 `orca terminal create --worktree name:<레인> --command "<에이전트 명령>"`.

**에이전트 배정 기준(사용자, 2026-09-30):** 복잡·판단 필요 = `claude --model claude-opus-5-5`, 단순·기계적 = `claude --model claude-sonnet-5-5`, 중간 = `antigravity` 또는 `muse`, 최종 검증 = Fable(이 세션). Antigravity 에는 판단 과제를 주지 않는다.

**선행(조율자 직접):** 0단계 전부. 통합 브랜치에 커밋된 뒤 워커 디스패치.

**병렬 레인(파일 소유권으로 분리):**

| 레인 | 작업 | 소유 파일 | 의존 | 에이전트 |
|---|---|---|---|---|
| S 단순 선행 | 1.1 스킬 문구 이식(score-collect 초안, evidence-editor), 1.2 종목 파일 `git rm`(훅 파일 제외), 1.4 AGENTS·README·memory-system 종목 서술 제거 | `.claude/skills/*`, `.claude/agents/*`, `docs/*`, `README.md`, `AGENTS.md`, `output/` 종목 산출물, `design/`, `sample/`, `review.md`, `requirements.txt` | 0 | Sonnet 5.5 |
| A 핵심 경로 | 1.3 공유 스크립트 축소 → 2.1 `paths.py` → 2.2 기존 실행 이동(해시 보존) → 2.3 테스트 49개 경로·서버 경로 함수 → 2.4 | `scripts/*.py`, `scripts/scorecard/{engine,stages,render_md,render_html,validate,compare}.py`, `tests/` 기존 파일, `.gitattributes`, `.gitignore`, `server.js` 경로 함수 | 0, S 의 1.2 병합 뒤 | Opus 5.5 |
| B 수집기 | 3.3 `evidence_lib`·`collect_news`·`collect_filings`·`collect_prices`(yfinance)·`resolve-cik`·픽스처·테스트, 3.2 규칙 v1.8 | 새 파일만 + `scorecard/rules/v1.8.json` | 0 | Muse |
| C 훅 | 4.1 `scripts/hooks/guard.py`(9개 히어독 이식), `tests/test_hooks.py`, `.claude/settings.json`, `.codex/hooks.json` 배선, `enforce-citations` 배선 제거, `protect-sensitive-files` 보호 목록에서 output-spec 제거 | 새 파일 + `.claude/hooks/**`, `.codex/hooks.json`, `.claude/settings.json` | 0 (묶음 경로 이름은 계획에 고정) | Sonnet 5.5 (사양이 고정된 기계적 이식) |
| D 승인 페이지 | 4.4 `server.js` `--approvals` 라우트·페이지·`node --test` | `server.js` 라우트 영역(A 와 함수 단위로 분리) | `summary --json` 계약(아래) | Antigravity |

**후속(직렬, A·B 병합 뒤):** 3.1 스키마 확대 → 3.4 `stages.collect`·research 등록·해시 결속 → 4.2 승인 보호·잠금 → 4.3 `summary·confirm·approve·revoke` 는 Opus 5.5. 4.5·4.6 문서·스킬은 Sonnet 5.5. `engine.load_context`·`stages.py` 를 A 도 만지므로 병렬 금지.

**검증:** 레인마다 구현자가 아닌 에이전트가 재현한다. A 의 해시 보존과 3.4 의 교차 검사, 최종 통합은 Fable(이 세션)이 직접 재현. 나머지 레인의 1차 재현은 Sonnet 5.5, 그 결과를 Fable 이 대조.

**디스패치 전에 고정하는 계약:** `paths.py` 이름과 묶음 경로(2단계), `candidates.json`·`evidence.json`·`triggers.json` 스키마(3단계), `guard.py` 훅 이름·입출력(4단계), 그리고 `summary --json`:
```
{ "run_id", "as_of", "rule_version",
  "companies": [{company_id, display_name, baseline: {total, rank}, current: {total, rank}, changed_factors: [{factor, from, to}], carried_factors: [..], pending: [..]}],
  "review": {status, areas: [{area, reviewer, result}], checklist_fail: int},
  "evidence": {candidates: int, selected: int, confirmed: int, items: [{evidence_id, company_id, factors, kind, title, url, published_at_utc, excerpt, status}]},
  "triggers": [{trigger_id, company_id, factors, condition, deadline, status}],
  "pending_rule_decisions": [..],
  "hashes": {rules, observations, judgments, run, results, draft, sources?, evidence?, triggers?},
  "approval": {exists, valid, approved_by?, approved_at?} }
```

**규칙:** 소유 밖 파일을 고쳐야 하면 조율자에게 계약 변경 요청 → 조율자가 계획 갱신 → 양쪽 반영. 워커는 완료 전 통합 브랜치 rebase + 테스트 재실행 → 커밋 → 회신 → 조율자 터미널 착수 안내(3단계 완료). 조율자는 보고를 믿지 않고 재현(테스트, `status`, `git diff --stat` 로 소유권 밖 변경 확인) 후 병합. 검증 기록은 `validation/<과제>/REPORT.md`. 지시서 끝에는 조율자 터미널 handle 을 적어 완료 회신이 조율자를 깨우게 한다(메모리: return-handle-in-dispatch). 1.2 의 훅 파일 삭제·배선 수정은 S 가 아니라 C 가 한다(`.claude/settings.json` 충돌 방지).

## 검증

- 단계마다 `uv run pytest -q`, `npm test`.
- 2단계: 이동한 실행 2개 `status` 가 `approval_valid: true`, `recompute_matches` 통과, `git diff --stat` 에 내용 변경 0(rename 만).
- 3단계: 수집기는 픽스처(`tests/fixtures/google_news_rss.sample.xml`, `edgar_submissions.CIK0001045810.sample.json`, `company_tickers.sample.json`, `yfinance_quotes.sample.json`)로 단위 테스트, `fetch_bytes` 가 유일한 urllib 사용자이고 `fetch_quote` 가 유일한 yfinance 호출자임을 grep 테스트로 고정. `--dry-run` 으로 URL 확인 뒤 SEC·Google·yfinance 각 1회 실조회. 가격 관측은 스키마(`unit`, basis, 중복 규칙)를 통과하고 ⑥ 계산이 `pending_data` 없이 산출되는지 확인.
- 종단: `init --rule v1.8` → `collect --from-file` → 선별 → `research` → `calculate` → `draft` → `review-template` 를 임시 묶음에서 자동 테스트, 실제 실행은 사람이 `node server.js --approvals` 로 페이지를 열어 근거 확정·승인 → 에이전트가 `build_report.py` → `output/<run_id>/report.html`. 승인 페이지 없이 `approve` 를 에이전트가 호출하면 훅·환경변수 검사에 막히는지 확인.
- 훅: `tests/test_hooks.py` 가 `guard.py` 함수를 페이로드 dict 로 직접 호출(bash 불필요). approve 명령, `approval.json` 쓰기, PowerShell 페이로드, 잠금 파일, 무관한 폴더에서의 무해 종료. 배선은 각 도구 세션에서 시험 명령 1회로 실제 차단 확인.

## 위험

- 기존 실행 이동에서 `.gitattributes` 를 같은 커밋에 옮기지 않으면 checkout 줄끝이 바뀌어 승인 해시가 깨진다. 이동 커밋 직후 `status` 로 확인한다.
- 규칙 파일 수정은 `rule_hash` 를 바꾼다. v1.8 신설로만 대응한다.
- 원천 allowlist 를 없앴으므로 수집기의 빈도 상한과 UA 표기가 유일한 자제 장치다. 상한을 코드 상수로 두고 테스트로 고정한다.
- 두 경로 문자열(옛/새) 허용 규칙은 이동한 실행 2개에만 필요하다. 새 실행에 옛 문자열이 나오면 오류로 잡는 테스트를 둔다.
- `enforce-plan.sh` 는 명령 문자열을 훑으므로 테스트·문서 인용문에 `scripts/build_report.py <slug>` 를 넣지 않는다.
- Windows 콘솔 cp949: CLI 는 `-X utf8`.

## 사용자 준비 항목 (구현 중 필요)

1. `SEC_UA` 환경변수 값(이름과 연락처, SEC 요구). 저장소에 넣지 않는다.
2. SPCX CIK 확인(1181412 후보).

## 커밋 순서

0.1 `build: uv 전환(pyproject·uv.lock·package.json)` · 0.2 `docs(memory): 2026-09-11 일지·guardrails 를 스키마에 맞춘다`
1.1 `docs(skills): stock-research 규칙을 score-collect 초안으로, content-editor 를 evidence-editor 로` · 1.2 `chore: 주식 리포트 HTML·에셋·스킬·명령·Codex 훅 사본·enforce-citations 제거` · 1.3 `refactor: 빌더·검증기·계약 라이브러리를 scorecard 전용으로 축소` · 1.4 `docs: AGENTS·README·memory-system 종목 서술 제거`
2.1 `feat(layout): paths.run_paths 로 경로 통일, output/<run_id>/ 묶음` · 2.2 `chore(layout): 기존 실행 2개를 output/ 묶음으로 이동(해시 보존)` · 2.3 `chore(hooks,server,tests): 묶음 경로 반영` · 2.4 `chore: sync_outputs.py 제거`
3.1 `feat(schema): sources·evidence·triggers 검증, companies cik·news_queries` · 3.2 `feat(rules): v1.8 — 원천 allowlist 블록 제거(personal use)` · 3.3 `feat(collect): evidence_lib·Google News RSS·EDGAR·yfinance 가격 수집기·resolve-cik` · 3.4 `feat(stages): collect 단계, research 근거 등록·렌더링, 해시 결속`
4.1 `refactor(hooks): bash 훅 9개를 scripts/hooks/guard.py 로 통합, 배선을 uv run 한 줄로(Claude·Codex), PowerShell 매처` · 4.2 `feat(hooks): approve·approval.json·이동한 실행·규칙 파일 보호, remind-review 경고화, 잠금 검사` · 4.3 `feat(approve): summary·confirm·revoke 명령, approved_via 기록` · 4.4 `feat(server): --approvals 승인 페이지와 일회용 코드` · 4.5 `docs(skills): score-collect 완성, score-approve 를 페이지 안내로 개정, score-* 개정, 리뷰어 에이전트 재작성` · 4.6 `docs: AGENTS·README·structure.md 반영` · (운영 단계) Antigravity·Muse 배선은 확인 3건 뒤 별도 커밋
