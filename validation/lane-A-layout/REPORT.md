# 레인 A 보고서: 공유 스크립트 축소, 실행 묶음 배치, 기존 실행 이동

## 한 일

| 커밋 | 단계 | 내용 |
|---|---|---|
| `52eef7a` | 1.3 | `refactor: 빌더·검증기·계약 라이브러리를 scorecard 전용으로 축소`. `build_report.py` 911→32줄, `validate_report_contract.py` 505→65줄, `report_contract_lib.py` 350→171줄(2.1 에서 디렉터리 상수를 지워 165줄). 종목 코드는 주석 처리하지 않고 지웠다. `stages.approve` 와 테스트 3개의 `validate_contract` 호출에서 가격 차트 인자를 뺐다. |
| `8449ba5` | 2.1 | `feat(layout): paths.run_paths 로 경로 통일, output/<run_id>/ 묶음`. 새 `scripts/scorecard/paths.py`, `engine`·`stages`·`render_md`·`render_html`·`validate`·`report_contract_lib`, `server.js` 경로 함수. |
| `f477856` | 2.2 | `chore(layout): 기존 실행 2개를 output/ 묶음으로 이동(해시 보존)`. rename 62건(전부 R100), 새 추적 7건, `.gitkeep` 삭제 5건, `.gitattributes`·`.gitignore` 수정. 기존 파일 내용 변경(`M`)은 이 두 설정 파일뿐이다. |
| `22ca671` | 2.3 | `chore(tests): 묶음 경로 반영`. 테스트 49개 파일 기계 치환, continue_run 샌드박스, company_invariance, 새 `tests/test_layout_paths.py`(6건). |
| `e11b953` | 2.4 | `chore: sync_outputs.py 제거`. |
| `6fb3c77` | 병합 | `HANSOLJJ/revision_checker`(레인 B·D 병합분) merge. 충돌 없음. |
| `2f7a0ef` | 병합 후속 | `test: yfinance 호출 지점 고정을 collect_prices.py 하나로`. 조율자 승인(아래 "지시서와 다른 점"). |

### 1.3 세부

- `build_report.py` 는 `main` 만 남았다. `scorecard.render_html.build_scorecard(slug)` 를 호출하고 HTML 경로, 생성 파일, 미리보기 URL(`OUTPUT_DIR` 기준 상대 경로)을 출력한다.
- `validate_report_contract.py` 는 `ValidationResult`·`print_result`·`validate_contract(slug, *, require_html, check_html_if_present)`·`main` 이다. `validate_contract` 는 `scorecard.validate.validate_scorecard` 에 위임한다. plan 이 없거나 `report_type` 이 다르면 `validate_scorecard` 가 오류를 낸다.
- `report_contract_lib.py` 에 남긴 것은 `ROOT`·`OUTPUT_DIR`, frontmatter 파서 일체, `H1_RE`·`H2_RE`·`heading_titles`·`has_required_section`·`count_h1`(scorecard.validate 가 사용), `SOURCE_MARKER_RE`·`has_source_markers`, `ArtifactPaths`·`artifact_paths`, `rel`, `REQUIRED_SCORECARD_PLAN_FRONTMATTER` 다. `load_json`·`html_attr`·`html_text` 는 사용처가 없어 지웠다.
- 삭제 전후 비교. 원본 폴더의 plan·draft 를 이 워크트리의 `plan/`·`drafts/`(gitignore)에 복사한 상태에서 두 실행의 `validate_report_contract.py <slug>` 출력을 저장하고, 삭제 뒤 `diff` 로 비교했다. 두 실행 모두 출력이 **같았다**(obsreg PASS, baseline 은 삭제 전부터 recompute 불일치로 FAIL). 비교에 쓴 임시 사본은 2.2 에서 원본 폴더로부터 다시 바이트 복사한 뒤 지웠다.

### 2.1 세부

- `RunPaths` 필드는 지시서 그대로다. 파일명 `plan.md`·`research.md`·`draft.md`·`preview.md`·`review.md`·`review-parts/`·`report.html`·`audit.md`·`evidence/`·`evidence/evidence.json`·`evidence/candidates.json`·`triggers.json` 은 `scripts/hooks/guard.py` 가 쓰는 이름과 대조했다.
- `run_paths` 는 `engine.run_dir(slug)`(= `engine.OUTPUT_DIR / slug`)를 거친다. 테스트가 `engine.OUTPUT_DIR` 하나만 바꾸면 모든 경로가 따라온다.
- `RunPaths.rel(p)` 은 `OUTPUT_DIR` 의 부모 기준 POSIX 문자열이다. 실제로는 ROOT 와 같고, 샌드박스에서도 frontmatter 가 `output/<slug>/…` 로 같게 나온다. 렌더러(`render_md`)와 검증기(`validate`)가 이 함수를 같이 쓴다.
- `validate.py` 에 `LEGACY_RUNS = {baseline, obsreg}` 와 `LEGACY_SOURCE_STRINGS`(`plan/<slug>.md`·`research/<slug>.md`·`drafts/<slug>.md`)를 두고 `source_matches(paths, kind, actual)` 로 비교한다. 옛 문자열은 두 실행에서만 통과한다. 이 판정이 허용 집합을 실제로 읽는지 변이로 확인했다(다른 slug 를 집합에 넣으면 True 로 바뀌고, 집합을 비우면 obsreg 도 False 로 바뀐다).
- `render_html.py` 는 `report.html`·`audit.md` 를 묶음에 쓰고, HTML 안의 감사 기록 링크는 `audit.md`(= `paths.audit.name`)다. `AUDIT_SUFFIX` 는 지웠다.
- `server.js`. `findHtmlReports` 는 `output/*/report.html` 을 한 단계만 찾고 `name` 을 run_id 로 둔다. `normalizeRequestedReport` 는 `run_id`, `output/<run_id>/`, `output/<run_id>/report.html`, `<run_id>.html` 을 모두 run_id 로 맞춘다. 디렉터리 요청은 끝 슬래시가 없으면 301 로 붙이고(상대 링크 `audit.md` 보호), `index.html` 이 없으면 `report.html` 을 낸다. `.md` 는 `text/plain; charset=utf-8` 이다. `text/markdown` 은 내려받기로 처리하는 브라우저가 있어 이렇게 정했다. argv 파싱, 핸들러 첫 줄, listen 콜백(`printReportLinks`)은 건드리지 않았다.

### 2.2 세부: 줄끝 판정

Git Bash 의 `grep -c $'\r$'` 는 LF 파일에도 줄 수를 세어 틀린 값을 냈다. 그래서 Python 으로 원본 바이트의 `\r\n` 개수를 다시 셌다.

| 파일 | baseline | obsreg |
|---|---|---|
| plan | CRLF | LF |
| draft | CRLF, sha256 `574841…` = 승인 해시 | LF, sha256 `94215e…` = 승인 해시 |
| report.html | CRLF | CRLF |
| audit | 원본 폴더에 없음 | LF |
| research·review(기존 추적) | LF | LF |

- obsreg draft 는 LF 로 승인됐으므로 `eol=crlf` 예외를 두지 않았다. 기본 `output/**/*.md text eol=lf` 가 적용된다.
- `.gitattributes` 는 `output/**/*.{json,md,html} text eol=lf` 를 기본으로 두고, 뒤에 `output/ai-scorecard-2026-09-baseline/** text eol=crlf` 와 `data_availability.json text eol=lf` 를 두었다. 지시서에 더해 예외 셋을 넣었다. baseline 의 `research.md`·`review.md` 는 원래 LF 로 추적·checkout 되던 파일이라 LF 를 유지하게 했고, obsreg `report.html` 은 원본 바이트(CRLF)를 유지하게 했다. 옛 `scorecard/runs/…`·`research/…`·`drafts/…`·`reviews/…` 줄은 지웠고 `scorecard/**` 두 줄과 `scorecard/rules/v1.5.json text eol=crlf` 는 남겼다.
- 새 checkout 재현. 커밋 뒤 `git checkout-index --prefix=<스크래치>/` 로 `output/` 을 새로 풀어 대조했다. 두 실행의 draft·observations·judgments·run 이 승인 해시와 전부 일치했고, plan·report.html·audit.md·research.md·review.md 는 작업 트리 바이트와 같았다(불일치 0).
- review-parts 43개는 옛 위치에서 속성이 없어 작업 트리가 CRLF(autocrlf)였다. 이제 `output/**/*.md text eol=lf` 가 적용되므로 새 checkout 에서는 LF 로 나온다. 인덱스 blob 은 그대로이고(R100) 해시 대상이 아니다.

### 2.2 세부: sha256 전후 대조

작업 트리 바이트 기준이다. 원본 폴더에서 복사한 파일은 원본 바이트와 비교했다.

| 원래 위치 | 새 위치 | 이동 전 sha256 | 이동 후 sha256 | 결과 |
|---|---|---|---|---|
| `scorecard/runs/ai-scorecard-2026-09-baseline/approval.json` | `output/ai-scorecard-2026-09-baseline/approval.json` | `d1d95f3159872461` | `d1d95f3159872461` | 같음 |
| `scorecard/runs/ai-scorecard-2026-09-baseline/data_availability.json` | `output/ai-scorecard-2026-09-baseline/data_availability.json` | `531e5f22329dedb1` | `531e5f22329dedb1` | 같음 |
| `scorecard/runs/ai-scorecard-2026-09-baseline/judgments.json` | `output/ai-scorecard-2026-09-baseline/judgments.json` | `685069767e0cf919` | `685069767e0cf919` | 같음 |
| `scorecard/runs/ai-scorecard-2026-09-baseline/observations.json` | `output/ai-scorecard-2026-09-baseline/observations.json` | `37435ae2989236f5` | `37435ae2989236f5` | 같음 |
| `scorecard/runs/ai-scorecard-2026-09-baseline/preview.md` | `output/ai-scorecard-2026-09-baseline/preview.md` | `7a36b08cb20c2e4e` | `7a36b08cb20c2e4e` | 같음 |
| `scorecard/runs/ai-scorecard-2026-09-baseline/results.json` | `output/ai-scorecard-2026-09-baseline/results.json` | `4eb8c7d77b73dd3e` | `4eb8c7d77b73dd3e` | 같음 |
| `scorecard/runs/ai-scorecard-2026-09-baseline/run.json` | `output/ai-scorecard-2026-09-baseline/run.json` | `50b063a5a12e84a6` | `50b063a5a12e84a6` | 같음 |
| `scorecard/runs/ai-scorecard-2026-09-baseline/sources.json` | `output/ai-scorecard-2026-09-baseline/sources.json` | `18f7b6571fc66d21` | `18f7b6571fc66d21` | 같음 |
| `research/ai-scorecard-2026-09-baseline.md` | `output/ai-scorecard-2026-09-baseline/research.md` | `69b04a0e467ffb01` | `69b04a0e467ffb01` | 같음 |
| `reviews/ai-scorecard-2026-09-baseline.md` | `output/ai-scorecard-2026-09-baseline/review.md` | `1c3d4a3800f4eaf5` | `1c3d4a3800f4eaf5` | 같음 |
| `scorecard/runs/ai-scorecard-2026-09-obsreg/approval.json` | `output/ai-scorecard-2026-09-obsreg/approval.json` | `c40afa3bccea3fb3` | `c40afa3bccea3fb3` | 같음 |
| `scorecard/runs/ai-scorecard-2026-09-obsreg/judgments.json` | `output/ai-scorecard-2026-09-obsreg/judgments.json` | `2403fb3748edd853` | `2403fb3748edd853` | 같음 |
| `scorecard/runs/ai-scorecard-2026-09-obsreg/observations.json` | `output/ai-scorecard-2026-09-obsreg/observations.json` | `02dcd2ab605542d8` | `02dcd2ab605542d8` | 같음 |
| `scorecard/runs/ai-scorecard-2026-09-obsreg/preview.md` | `output/ai-scorecard-2026-09-obsreg/preview.md` | `3449ce654a0973a3` | `3449ce654a0973a3` | 같음 |
| `scorecard/runs/ai-scorecard-2026-09-obsreg/results.json` | `output/ai-scorecard-2026-09-obsreg/results.json` | `d3f99cb5243bd521` | `d3f99cb5243bd521` | 같음 |
| `scorecard/runs/ai-scorecard-2026-09-obsreg/run.json` | `output/ai-scorecard-2026-09-obsreg/run.json` | `71a83f40e92ea896` | `71a83f40e92ea896` | 같음 |
| `scorecard/runs/ai-scorecard-2026-09-obsreg/sources.json` | `output/ai-scorecard-2026-09-obsreg/sources.json` | `14ec0e8083d82e53` | `14ec0e8083d82e53` | 같음 |
| `research/ai-scorecard-2026-09-obsreg.md` | `output/ai-scorecard-2026-09-obsreg/research.md` | `aadfb4db60208258` | `aadfb4db60208258` | 같음 |
| `reviews/ai-scorecard-2026-09-obsreg.md` | `output/ai-scorecard-2026-09-obsreg/review.md` | `ef2c4c6c64d8e213` | `ef2c4c6c64d8e213` | 같음 |
| `원본:plan/ai-scorecard-2026-09-baseline.md` | `output/ai-scorecard-2026-09-baseline/plan.md` | `24a7de5d68a87c22` | `24a7de5d68a87c22` | 같음 |
| `원본:drafts/ai-scorecard-2026-09-baseline.md` | `output/ai-scorecard-2026-09-baseline/draft.md` | `574841bc7c26f225` | `574841bc7c26f225` | 같음 |
| `원본:output/ai-scorecard-2026-09-baseline.html` | `output/ai-scorecard-2026-09-baseline/report.html` | `e6cc960c1c50f412` | `e6cc960c1c50f412` | 같음 |
| `원본:plan/ai-scorecard-2026-09-obsreg.md` | `output/ai-scorecard-2026-09-obsreg/plan.md` | `6d41e429bf40ddce` | `6d41e429bf40ddce` | 같음 |
| `원본:drafts/ai-scorecard-2026-09-obsreg.md` | `output/ai-scorecard-2026-09-obsreg/draft.md` | `94215e94def97207` | `94215e94def97207` | 같음 |
| `원본:output/ai-scorecard-2026-09-obsreg.html` | `output/ai-scorecard-2026-09-obsreg/report.html` | `57013f0c858c6223` | `57013f0c858c6223` | 같음 |
| `원본:output/ai-scorecard-2026-09-obsreg-audit.md` | `output/ai-scorecard-2026-09-obsreg/audit.md` | `cf4f765707177e05` | `cf4f765707177e05` | 같음 |

전체 69개 중 69개가 같고 다른 것은 0개다. review-parts 43개는 모두 같아서 표에서 생략했다. 복사는 `shutil.copyfile` 로 했고, 편집기나 Write 도구로 열지 않았다.

## 검증 명령과 출력 요약

### status 와 recompute (이동 전·후)

`uv run --frozen python -X utf8 -c "… recompute_matches(s); status(s)"` 출력이다. 이동 전 값은 1.3 커밋 뒤, plan·draft 임시 사본이 있는 상태에서 쟀다.

| 실행 | 시점 | recompute_matches | approval_valid | html |
|---|---|---|---|---|
| baseline | 이동 전 | `False`, 저장 `0942c342f010781e…`, 재계산 `200d7b01afc3cf39…` | true | false |
| baseline | 이동 후 | `False`, 저장 `0942c342f010781e…`, 재계산 `200d7b01afc3cf39…` | true | true |
| obsreg | 이동 전 | `True`, `4a3f6c05b206ef81…` 양쪽 동일 | true | false |
| obsreg | 이동 후 | `True`, `4a3f6c05b206ef81…` 양쪽 동일 | true | true |

두 실행 모두 `approval_valid: true` 다. baseline 의 recompute 는 이동 전후가 같은 `False` 이며, 조율자 메시지 `msg_2161aab10d56` 에 따라 기존 상태로 판정한다(승인 뒤 엔진이 바뀌어 amazon·oracle·openai 의 F9 calc 경로 기록만 달라졌다). 나머지 status 필드(`pending_rule_decisions`·`scored`·`incomplete`·`review_status`)도 전후가 같다. `html` 만 false 에서 true 로 바뀌었다.

`validate_report_contract.py <slug> --require-html`:

- obsreg: `[PASS]`. plan·schema·allowlist·research·recompute·순위표·리뷰·승인 해시·HTML·history.csv 전부 ok. 옛 frontmatter 문자열로 인한 불일치 오류는 없다.
- baseline: `[FAIL]`. 오류는 `재계산 결과가 저장된 results.json 과 다름` 하나이고, 삭제 전부터 있던 것이다. 승인 해시·HTML·history.csv 검사는 ok 다.

### 테스트 (merge 뒤 최종)

- `uv run --frozen python -X utf8 -m unittest discover -s tests -t .` → `Ran 974 tests`, `FAILED (failures=1, errors=14)`.
- `uv run --frozen pytest -q` → `15 failed, 961 passed, 1664 subtests passed`.
- `npm run check` → 통과(`node --check server.js` + `compileall -q scripts`).
- `npm run test:node`(레인 D) → 9 pass, 0 fail.
- server.js 스모크. 임시 포트로 띄워 `/` 200, `/ai-scorecard-2026-09-obsreg` 301 → `/ai-scorecard-2026-09-obsreg/`, 디렉터리 요청 200(report.html), `audit.md` 200 `text/plain`, 시작 로그에 두 실행의 `…/report.html` URL 이 나왔다.

기준선(`dispatch/baseline-failures.txt`, 실패 7·오류 30 = 37줄)과 비교하면 **새로 생긴 실패는 0건이고 22줄이 해소됐다.** 남은 15줄(unittest 기준)은 전부 기준선 목록에 있다.

남은 실패의 원인은 한 가지다. `test_scorecard_fix54_obs`·`fix55_stage2`·`fix57_stage1`·`fix58_stage1`·`fix58_stage2`·`obs_recency` 가 `validation/f6-avail-15/_raw/*.companyfacts.json` 등 SEC 원자료를 읽는다. 이 파일들은 `validation/f6-avail-15/.gitignore`(`_raw/`)로 추적되지 않고, 원본 폴더에는 있다(`AAPL…GOOGL.companyfacts.json` 확인). 13건은 `FileNotFoundError`, 1건은 원자료가 없어 `None` 을 받은 `AttributeError`, 1건(`test_broad_tag_sweep_finds_only_tesla`)은 훑을 파일이 없어 `[] != ['TSLA']` 다. 레인 A 소유 밖이라 복사하지 않았다.

### 소유 범위

`git diff --name-only HANSOLJJ/revision_checker...HEAD` 는 `.gitattributes`, `.gitignore`, 옛 `plan/`·`drafts/`·`research/`·`reviews/` 의 `.gitkeep` 5개, `output/ai-scorecard-2026-09-{baseline,obsreg}/**`, `scripts/{build_report,report_contract_lib,validate_report_contract,sync_outputs}.py`, `scripts/scorecard/{paths,engine,render_html,render_md,stages,validate}.py`, `server.js`, `tests/**` 만 보인다. `schema.py`, `scripts/hooks/**`, 규칙 파일, `companies.json`, `history.csv` 는 바꾸지 않았다.

## 지시서와 다른 점

- **server.js 를 2.1 커밋에 넣었다.** 지시서는 2.1 절에 server.js 경로 함수를 적고 2.3 커밋 메시지를 `chore(server,tests)` 로 적었다. 경로 함수는 2.1 의 한 단위라 `8449ba5` 에 넣었고, 2.3 커밋은 `chore(tests): 묶음 경로 반영` 으로 했다.
- **2.1 은 2.2 이동을 작업 트리에 먼저 적용해 검증한 뒤 경로 지정 커밋(`git commit -- <files>`)으로 분리했다.** 2.1 만으로는 실행 파일이 옛 위치에 있어 검증할 수 없기 때문이다. 결과적으로 커밋 순서는 지시서와 같다.
- **`.gitattributes` 에 예외 셋을 더했다.** baseline `research.md`·`review.md` 는 LF, obsreg `report.html` 은 CRLF 다. 이유는 위 "줄끝 판정" 절에 적었다.
- **`test_scorecard_company_invariance` 가 draft 해시도 본다.** 기존 docstring 은 "초안은 git 이 추적하지 않으므로 검사하지 않는다" 였는데 이번 변경으로 그 전제가 사라졌다. 테스트 이름을 `test_prior_approval_matches_all_six_hashes` 로 바꿨다.
- **레인 B 테스트 수정(`2f7a0ef`).** merge 뒤 `tests/test_collect_prices.py` 의 `test_yfinance_importing_files_are_pinned` 가 실패했다. 기대 집합에 `scripts/build_report.py` 가 있었는데, 1.3 이 계획대로 그 파일의 종목 차트 yfinance 코드를 지웠기 때문이다. 조율자에게 `ask` 로 물었고 "레인 A 가 고친다" 는 답을 받아 기대 집합을 `{scripts/scorecard/collect_prices.py}` 하나로 줄이고 docstring 의 예외 문구를 지웠다. 검사 범위는 이미 `scripts/` 전체(`rglob`)다. 조율자는 "1.3 커밋에 함께" 넣으라고 했으나, 1.3 은 이미 merge 아래에 있어 이력을 다시 써야 하므로 별도 커밋으로 넣었다.
- **merge 커밋 메시지**는 `git merge --no-edit` 기본값(`Merge branch 'HANSOLJJ/revision_checker' into HANSOLJJ/lane-A`)이다. 통합 브랜치의 `merge: …` 형식과 다르다.

## 소유 밖에서 발견한 문제 (고치지 않음)

1. **옛 obsreg `report.html` 의 감사 기록 링크가 묶음에서 깨진다.** 본문에 `href="ai-scorecard-2026-09-obsreg-audit.md"` 가 2개 있는데, 묶음 안 파일 이름은 `audit.md` 다. 기존 바이트를 바꾸지 않는다는 조건 때문에 그대로 두었다. 다음 빌드(`build_report.py`)부터는 `href="audit.md"` 로 나온다. baseline `report.html` 에는 감사 링크가 없다.
2. **baseline 묶음에는 `audit.md` 가 없다.** 원본 폴더에도 `output/ai-scorecard-2026-09-baseline-audit.md` 가 없다. 감사 기록 기능(FIX-67)이 baseline 빌드 뒤에 생겼기 때문으로 보인다.
3. **`scripts/scorecard_cli.py` 문서 문자열**(16행)이 "build 는 … `build_report.py <slug>` 가 report_type 으로 분기한다" 고 적는다. 분기는 1.3 에서 사라졌다. 180행 안내도 `validate_report_contract.py` 를 가리키며, 이것은 여전히 맞다.
4. **server.js `printReportLinks`**(레인 D 소유)의 안내 문구가 아직 `Build a report into output/*.html` 이다. 동작은 새 `findHtmlReports` 와 맞게 돈다(스모크 확인).
5. **스킬·명령 문서**(`.claude/skills/score-*`, `.claude/commands/score-build.md`)와 `AGENTS.md` 가 `plan/<slug>.md`·`reviews/<slug>.md`·`drafts/` 경로를 말한다. 4단계 문서 작업 대상이다.
6. **`guard.py` 의 빌드 명령 정규식**이 `build_report.py` 뒤의 어떤 인자든 slug 로 본다. `build_report.py --help` 도 `output/--help/review.md` 리뷰가 필요하다는 이유로 막힌다. 해가 크지 않아 기록만 한다.
7. **사용자 메모리의 `sync_outputs.py` 언급**(저장소 밖 `worktrees-consolidated` 메모)이 이제 낡았다.
8. **`scorecard.validate` 의 `input_hashes` import** 는 이번 변경 전부터 쓰이지 않는다. 고치지 않았다.

## 남긴 것

- `validation/*/_raw/` 원자료 부재로 남는 테스트 15줄(위 원인). 원본 폴더에서 복사하거나 픽스처로 바꾸는 것은 다른 과제다.
- baseline recompute 불일치(기존 상태, 조율자 판정).
- 옛 `report.html` 감사 링크(위 1).

## 최종 커밋

이 보고서를 담은 커밋이 레인 A 의 마지막 커밋이다. SHA 는 `worker_done` 본문과 조율자 터미널 안내에 적는다. 보고서 직전 HEAD 는 `2f7a0ef` 다.
