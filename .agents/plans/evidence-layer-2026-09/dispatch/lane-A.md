# 레인 A — 핵심 경로: 공유 스크립트 축소 → paths.py → 기존 실행 이동(해시 보존) → 테스트·서버 경로

에이전트: Claude Opus 5.5. 의존: 레인 S 의 1.2(종목 파일 삭제)가 통합 브랜치에 병합된 뒤 시작한다. 공통 규약: `README.md` 를 먼저 읽는다. 계획 원문: `../plan.md` 1.3 과 2단계 전체.

## 시작 시점 상태 (2026-09-30 조율자 기록)

- 레인 S(종목 파일 삭제)와 레인 C(훅 통합)가 통합 브랜치에 병합됐다. `docs/output-spec.md` 도 지워졌다.
- 이 워크트리의 훅은 새 `scripts/hooks/guard.py` 다. `enforce_plan` 은 `output/<slug>/report.html`·`audit.md` 를 **Write/Edit 도구로 쓰는 것을 막는다.** 2.2 의 복사는 Bash 의 `cp` 나 `uv run --frozen python -X utf8 -c "import shutil; …"` 로 한다. `git mv` 도 Bash 로 하므로 막히지 않는다.
- `enforce_plan` 은 `output/<slug>/research.md` 를 Write 로 만들 때 같은 폴더의 `plan.md` 를 요구한다. 테스트 픽스처를 Write 로 만들 일이 있으면 순서를 지킨다.
- `forbid_financial_advice` 는 Bash 뒤마다 `output/*/draft.md` 와 `judgments.json` 을 훑는다. 옮길 두 실행의 draft·judgments 에는 걸리는 표현이 없음을 조율자가 확인했다.
- `validate.py` 의 `check_source_allowlist` 는 v1.7 실행 때문에 그대로 둔다. 레인 B 의 규칙 v1.8 은 아직 병합 전일 수 있다.

## 목표 (Target · Change)

종목 리포트 코드를 공유 스크립트에서 지우고, 실행 산출물을 `output/<run_id>/` 한 폴더로 모으는 경로 도우미를 만들고, 기존 실행 2개를 그 양식으로 옮기되 승인 해시가 깨지지 않게 한다. 네 커밋이다.

## 소유 파일 (Ownership)

- `scripts/build_report.py`, `scripts/validate_report_contract.py`, `scripts/report_contract_lib.py`, `scripts/sync_outputs.py`(삭제)
- `scripts/scorecard/paths.py`(새), `engine.py`, `stages.py`, `render_md.py`, `render_html.py`, `validate.py`, `compare.py`(필요 시)
- `tests/` 의 기존 파일 전부와 새 `tests/test_layout_paths.py`
- `.gitattributes`, `.gitignore`
- `server.js` 의 경로 함수(`ROOT` 아래 탐색: `findHtmlReports`, `normalizeRequestedReport`, `reportUrl`, 디렉터리 요청 처리, MIME 표). **argv 파싱·핸들러 첫 줄·listen 콜백은 레인 D 가 고친다. 건드리지 않는다.**
- `scorecard/runs/**`, `research/ai-scorecard-*`, `reviews/**`, `plan/.gitkeep`, `drafts/.gitkeep`, `research/.gitkeep`, `reviews/.gitkeep`. `git mv` 와 `git rm` 만 한다. 내용 변경 금지.
- `output/<run_id>/**` 새 위치.

만지지 않는 것: `scripts/scorecard/schema.py`(3.1), `scripts/hooks/**`(레인 C), `.claude/**`, `.codex/**`, `docs/**`, `AGENTS.md`, 레인 B 의 새 수집기 파일, `scorecard/rules/*`, `scorecard/companies.json`, `scorecard/history.csv`.

## 1.3 공유 스크립트 축소

커밋 메시지: `refactor: 빌더·검증기·계약 라이브러리를 scorecard 전용으로 축소`

채점표 코드·테스트가 세 파일에서 쓰는 이름은 `rel`, `read_markdown`, `ROOT`, `artifact_paths`, `frontmatter_value`, 디렉터리 상수, `has_source_markers`(report_contract_lib), `validate_contract`·`ValidationResult`·`print_result`(validate_report_contract) 다. 시작 전에 `rg` 로 다시 확인한다.

- `build_report.py` 911줄 → 약 40줄. `main` 만 남기고 `scorecard.render_html.build_scorecard(slug)` 호출과 경로·미리보기 URL 출력. `--reuse-existing-price-chart`, `report_type_for` 분기, 종목 함수 전부 삭제. 파일은 진입점으로 유지한다(스킬·문서·훅이 가리킨다).
- `validate_report_contract.py` 505줄 → 약 80줄. `ValidationResult`, `print_result`, `validate_contract(slug, *, require_html, check_html_if_present)` → `scorecard.validate.validate_scorecard` 위임, `main`. `require_price_chart`·`check_price_chart_if_present` 인자를 없애고 `stages.approve` 호출부를 맞춘다. 토스 HTML 정규식·`_validate_*`·보조 함수 삭제. `scorecard/validate.py` 가 지운 함수를 import 하지 않는지 확인한다.
- `report_contract_lib.py` 350줄 → 약 150줄. 남기는 것은 `ROOT`·`OUTPUT_DIR`(다른 디렉터리 상수는 2.1 뒤 제거), frontmatter 파서, `SOURCE_MARKER_RE`·`has_source_markers`, `ArtifactPaths`·`artifact_paths`(plan·research·draft·review·html 만), `rel`, `REQUIRED_SCORECARD_PLAN_FRONTMATTER`. 지우는 것은 `ASSET_DIR`, `PRICE_CHART_FENCE_RE`·`price_chart_blocks`·`parse_key_value_block`, `strip_source_markers`, 이미지 키 상수, `iter_json_strings`·`prohibited_image_generation_hits`·`selected_image_path`·`hero_image_status`, `REQUIRED_PLAN_FRONTMATTER`·`REQUIRED_DRAFT_SECTIONS`, `REPORT_TYPES`·`DEFAULT_REPORT_TYPE`·`report_type_for`. `heading_titles`·`has_required_section`·`count_h1`·`load_json`·`html_attr`·`html_text` 는 사용처 grep 뒤 미사용이면 삭제.
- 검증. compileall, 테스트, 그리고 실행 obsreg 에 대해 삭제 전·후 `validate_report_contract.py` 출력이 같은지. 이 워크트리에는 `plan/`·`drafts/` 파일이 없으므로 원본 폴더 `E:/sourcecode/01_side_project/stock-report-harness` 의 `plan/ai-scorecard-2026-09-obsreg.md`, `drafts/ai-scorecard-2026-09-obsreg.md` 를 이 워크트리의 같은 경로(gitignore)로 복사해 비교하고, 2.2 에서 그 파일을 묶음으로 옮긴다.

## 2.1 경로 도우미

커밋 메시지: `feat(layout): paths.run_paths 로 경로 통일, output/<run_id>/ 묶음`

- 새 `scripts/scorecard/paths.py`.

  ```python
  @dataclass(frozen=True)
  class RunPaths:
      slug: str
      run_dir: Path
      plan: Path; research: Path; draft: Path; preview: Path; review: Path; review_parts: Path
      html: Path; audit: Path
      evidence_dir: Path; evidence: Path; candidates: Path; triggers: Path
      def rel(self, p: Path) -> str: ...   # ROOT 기준 POSIX 문자열. 렌더러와 검증기가 같은 함수를 쓴다

  def run_paths(slug: str) -> RunPaths: ...  # 항상 OUTPUT_DIR / slug 아래
  ```

  파일명은 `plan.md`, `research.md`, `draft.md`, `preview.md`, `review.md`, `review-parts/`, `report.html`, `audit.md`, `evidence/`, `evidence/evidence.json`, `evidence/candidates.json`, `triggers.json` 이다. 레인 C 의 훅이 이 이름을 그대로 쓴다. 바꾸지 않는다.
- `engine.py`. `RUNS_DIR` → `OUTPUT_DIR`, `run_dir(slug) = OUTPUT_DIR / slug`. `compare.py` 는 `run_dir` 를 쓰므로 따라온다.
- `stages.py`. `PLAN_DIR` 등 전역 import 를 없애고 모든 단계가 `run_paths(slug)` 를 쓴다. `init_run` 은 `output/<slug>/` 에 만든다.
- `render_md.py` 의 frontmatter·본문 경로 문자열 → `paths.rel(...)`. `validate.py` 의 비교도 같은 함수.
- **이동한 실행 호환.** 기존 실행의 research·draft·review frontmatter 는 `plan/<slug>.md` 같은 옛 문자열을 갖고 있고 draft 는 해시 대상이라 고칠 수 없다. `validate.py` 에 `LEGACY_SOURCE_STRINGS` 를 두어 `plan_source`·`research_source`·`draft_source` 비교에서 현재 문자열 **또는** 옛 문자열(`plan/<slug>.md`, `research/<slug>.md`, `drafts/<slug>.md`)을 허용한다. 이 허용은 `LEGACY_RUNS = {"ai-scorecard-2026-09-baseline", "ai-scorecard-2026-09-obsreg"}` 에만 적용하고, 다른 실행에 옛 문자열이 나오면 오류다.
- `render_html.py`. HTML 과 audit 를 `paths.html`·`paths.audit` 에 쓰고, 상대 링크는 `paths.audit.name`. `report_contract_lib.artifact_paths` 는 묶음 경로만 반환한다.
- `server.js` 경로 함수. `output/*/report.html` 을 한 단계 재귀로 목록에 올리고, `.md` MIME 을 추가하고, 디렉터리 요청에 `report.html` 이 있으면 그것을 낸다.

## 2.2 기존 실행 2개 이동 (한 커밋, 바이트 보존)

커밋 메시지: `chore(layout): 기존 실행 2개를 output/ 묶음으로 이동(해시 보존)`

- `git mv scorecard/runs/<id>/* output/<id>/`, `git mv research/<id>.md output/<id>/research.md`, `git mv reviews/<id>.md output/<id>/review.md`, `git mv reviews/_parts/<id>/ output/<id>/review-parts/`(obsreg 만 있다).
- 원본 폴더에서 gitignore 라 git 에 없던 `plan/<id>.md`, `drafts/<id>.md`, `output/<id>.html`, `output/<id>-audit.md` 를 `output/<id>/{plan.md, draft.md, report.html, audit.md}` 로 **바이트 그대로** 복사해 추적을 시작한다. `shutil.copyfile` 이나 `cp` 로 하고 편집기로 열지 않는다. 복사 전후 sha256 을 보고서에 적는다.
- **줄끝을 먼저 판정한다.** 두 실행의 `draft.md` 원본 바이트에 `\r\n` 이 있는지 보고 `approval.json` 의 draft 해시와 대조한다. baseline 은 CRLF 로 승인됐음이 알려져 있다. obsreg 도 CRLF 라면 그 파일에 `eol=crlf` 예외를 둔다. 승인 해시와 일치하는 바이트가 checkout 뒤에도 그대로 나오게 하는 것이 목표다.
- `.gitattributes` 를 같은 커밋에서 바꾼다. `output/**/*.json text eol=lf`, `output/**/*.md text eol=lf`, `output/**/*.html text eol=lf` 를 기본으로 두고, 그 뒤에 예외 `output/ai-scorecard-2026-09-baseline/** text eol=crlf` 와 `output/ai-scorecard-2026-09-baseline/data_availability.json text eol=lf` 를 둔다(뒤 줄이 이긴다). 옛 `scorecard/runs/…`, `research/ai-scorecard-*.md`, `drafts/…`, `reviews/…` 줄은 지운다. `scorecard/**/*.json`·`*.md` 줄은 남는 공유 정의(rules·baseline·companies)를 위해 유지한다. `scorecard/rules/v1.5.json text eol=crlf` 도 유지.
- `.gitignore`. `output/` 줄 삭제, `plan/*`·`!plan/.gitkeep`·`drafts/*`·`!drafts/.gitkeep` 삭제. `data/`·`node_modules/`·`.agents/plans` 관련 줄은 이미 있다.
- `plan/.gitkeep`, `drafts/.gitkeep`, `research/.gitkeep`, `reviews/.gitkeep`, `reviews/_parts/**/.gitkeep` 을 `git rm` 해 빈 폴더가 사라지게 한다.
- **검증이 핵심이다.** 커밋 직후 `uv run --frozen python -X utf8 scripts/scorecard_cli.py status <id>` 가 두 실행 모두 `approval_valid: true` 여야 한다. 지금 이 워크트리에서는 draft 부재로 false 다. 이동 뒤 true 가 되면 해시 보존이 증명된다. `engine.recompute_matches` 참. `git show --stat HEAD` 에 rename 과 새 추적 파일만 있고 기존 파일의 내용 변경(`M`)이 없다.

## 2.3 · 2.4 테스트와 정리

커밋 메시지: `chore(server,tests): 묶음 경로 반영` 과 `chore: sync_outputs.py 제거`

- 테스트 약 49개 파일의 `ROOT / "scorecard" / "runs" / <slug>` → `ROOT / "output" / <slug>`, `plan/`·`drafts/`·`output/<slug>.html`·`reviews/` 참조 → 묶음 경로. 기계적 치환 뒤 전체 실행. `test_scorecard_continue_run.py` 의 샌드박스는 `engine.OUTPUT_DIR` 를 patch 한다.
- 새 `tests/test_layout_paths.py`. `run_paths` 문자열, 이동한 실행의 frontmatter 옛 문자열 허용(그리고 다른 slug 에서는 거부), `init_run` 이 묶음을 만드는지.
- `scripts/sync_outputs.py` 삭제. 묶음이 추적되므로 불필요하다.
- 훅 매핑은 레인 C 가 새 배치 기준으로 짠다. 여기서는 건드리지 않는다.

## 검증 (Observable acceptance)

- **테스트 전부 통과.** 기준선의 실패 7·오류 30 은 draft·plan 부재가 원인이었고 2.2 가 해소한다. 이 워크트리에서 처음으로 866건 전부 통과가 목표다. 남는 실패가 있으면 원인을 보고서에 적는다.
- `status` 가 두 실행 모두 `approval_valid: true`.
- `git diff --stat HANSOLJJ/revision_checker...HEAD` 가 소유 파일만 보인다.
- 보고서 `validation/lane-A-layout/REPORT.md` 에 sha256 전후, `status` 출력, 테스트 요약을 적는다.
