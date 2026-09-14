# stock-report-harness 운영 지침

## 목적
이 저장소는 주식·ETF·섹터 요청을 `plan → research → draft → image → review → build` 파일 계약으로 처리해 검증 가능한 HTML 경제리포트를 만든다.
`plan/<slug>.md`는 후속 단계의 단일 기준 문서이며, 모든 산출물은 같은 `slug`의 선행 산출물을 참조한다.

## 명령과 기본 순서
- 명령: `/stock-plan <요청>`, `/stock-research <slug>`, `/stock-draft <slug>`, `/stock-image <slug>`, `/stock-review <slug>`, `/stock-build <slug>`.
- 기본 순서: `plan → research → draft → hero 이미지 3개 생성/선택 → review → build`.
- 특정 단계만 요청받아도 필요한 선행 산출물이 없으면 먼저 만든다.
- review/build에서 문제가 발견되면 같은 slug의 선행 단계로 돌아가 수정 후 재실행한다.

## Plan 계약
- `/stock-plan`은 반드시 `plan/<slug>.md`를 작성한다.
- frontmatter 필수: `slug`, `topic`, `request`, `output_type`, `audience`, `ticker`, `period_start`, `period_end`, `chart_required`, `price_data_source`, `price_data_interval`, `created_at`, `assumptions`.
- 본문 필수: 요청 해석, 이해 목표, 리서치 범위, 데이터 확인 항목, 리포트 구조, 차트 요구, Hero 이미지 방향, 리뷰 기준, 완료/차단 조건.
- 사용자가 기간을 말하지 않으면 기본값은 최근 6개월이며 `assumptions`에 기록한다.

## Research 계약
- `/stock-research`는 `plan/<slug>.md`의 research questions와 data requirements를 따른다.
- `ticker`, `period_start`, `period_end`를 확인하고, 가격 데이터 요구는 `yfinance` 일봉(`interval=1d`)으로 둔다.
- 관련 종목(개별주/ETF/섹터 proxy)이 있으면 종목별 최신 뉴스 최소 100건을 수집·분류·분석한다.
- `research/<slug>.md`에는 100건 뉴스의 날짜, 매체, 제목, 핵심 이슈, 가격/수급/리스크 해석을 표로 남긴다.
- 뉴스 원자료 JSON에는 가능한 항목별 원문 URL을 저장한다. URL이 없으면 원문 URL을 조작하지 말고 fallback과 `url_is_fallback`을 명시한다.
- 한국 상장 종목은 가능하면 토스증권 종목 뉴스와 투자자별 매매 동향을 참고하고, 사용 URL/API를 `sources`와 원자료 JSON에 남긴다.

## Draft 계약
- `/stock-draft`는 `plan/<slug>.md`의 outline을 따르고 반드시 `research/<slug>.md`를 근거로 작성한다.
- frontmatter 필수: `ticker`, `period_start`, `period_end`, `plan_source`, `research_source`.
- 필수 섹션: H1 정확히 1개, `## 개요`, `## 배경`, `## 메커니즘`, `## 영향과 적용`, `## References`.
- 가격 차트는 직접 데이터 배열을 쓰지 말고 `price-chart` 블록으로 선언한다.
- 뉴스 100건이 있으면 `## 최신 뉴스 5건 요약`을 넣고 날짜·매체·제목 링크·1~2문장 요약·가격/수급 해석을 포함한다.
- 숫자·가격·수급·뉴스 해석에는 근거를 두고, draft/research에는 검증용 출처 표식을 유지한다.
- 투자 권유, 수익 보장, 매매 지시처럼 읽히는 표현은 금지한다.

## Image 계약
- `/stock-image`는 plan, research, draft 전체 메시지와 결론 톤을 반영해 hero 후보 3개를 만든다.
- 이미지 생성은 `python3 scripts/run_stock_image_codex.py <slug>`로 Codex CLI를 열어 `imagegen` skill / built-in `image_gen`이 수행하게 한다.
- 로컬/Pillow/SVG/빈 placeholder를 실제 hero 이미지로 대체하지 않는다.
- 이미지에는 텍스트, 숫자, 티커, 로고, 워터마크, UI 스크린샷을 넣지 않는다.
- 필수 산출물: `output/assets/<slug>-hero-v1~v3.prompt.txt`, `hero-v1~v3.png`, `hero-v1~v3.score.json`, `image-manifest.json`, `selected-image.json`.
- `image-manifest.json`은 `status: complete`, `generation_method: codex-cli-imagegen`, `generated_with`를 가져야 하며, procedural/Pillow/SVG/placeholder 방식은 실패로 본다.
- `selected-image.json`은 최소 `slug`, `selected_candidate`, `image_path` 또는 `selected_image`, `reason`, `generated_with`를 포함하고, 경로는 `assets/<file>.png` 또는 `output/assets/<file>.png`처럼 검증기가 찾을 수 있는 값으로 쓴다.
<!-- 2026-09-07 hero 선택 사항 변경 전: - 최종 HTML에는 선택된 hero 이미지 1장이 반드시 있어야 하며, 없으면 build를 성공 처리하지 않는다. -->
- hero 이미지는 선택 사항이다. Codex CLI를 쓸 수 있으면 위 절차로 반드시 생성하고, 쓸 수 없으면 래퍼가 남긴 `status: blocked` 매니페스트와 프롬프트 파일만 유지한 채 review/build를 hero 카드 없이 진행한다.
- 다른 도구나 수동으로 만든 이미지에 `codex-cli-imagegen` 출처를 붙여 통과시키지 않는다. 매니페스트가 `complete`이면 선택된 PNG가 실제로 존재해야 하며, 없으면 build를 실패로 본다.

## Review 계약
- `reviews/<slug>.md` frontmatter에는 `status: pass | needs_fix | blocked`, `plan_source`, `research_source`, `draft_source`, `review_type: separate-session-4way`, `review_execution: separate_subagent_sessions`를 둔다.
- 리뷰 작성 후 `python3 scripts/validate_report_contract.py <slug>`를 반드시 실행하고, 실패하면 `needs_fix`로 되돌린다.
- `needs_fix`이면 generator 단계로 돌아가 수정 후 다시 review한다. 같은 차단 이슈가 3회 반복되거나 외부 데이터/권한 때문에 해결 불가할 때만 `blocked`로 둔다.

## Build 계약
<!-- 2026-09-07 hero 선택 사항 변경 전: - `/stock-build`는 `plan`, `research`, `draft`, `reviews`, 선택된 hero 이미지가 모두 유효할 때만 `output/<slug>.html`을 만든다. -->
- `/stock-build`는 `plan`, `research`, `draft`, `reviews`가 모두 유효할 때만 `output/<slug>.html`을 만든다. 선택된 hero 이미지가 있으면 삽입하고, 없으면 hero 카드 없이 렌더링한다.
- build는 수동 작성이 아니라 `python3 scripts/build_report.py <slug>`로 수행한다.
- build는 `python3 scripts/validate_report_contract.py <slug> --require-html --require-price-chart`로 pass review, 4-way review metadata, frontmatter 정합성, ticker·기간 일치, 필수 섹션, References, selected image(있을 때), yfinance price chart를 검증한다.
- 가격 차트는 요청 기간 전체의 실제 yfinance 일봉으로 만들고, 366일 이내·`YYYY-MM-DD` 오름차순 라벨·`ariaLabel`을 만족해야 한다.
- 최종 HTML 본문에는 `[S1]`, `[N1]` 같은 인라인 참조 표식을 노출하지 말고 References만 남긴다.
- 최종 HTML에는 투자 유의 문구를 하단 footer note로 포함하고, build 단계에서 새 주장을 추가하지 않는다.

## AI Scorecard 계약 (report_type: ai_scorecard)
- 목적: AI 기업 9-factor 채점표를 같은 하네스 안에서 재현 가능하게 계산한다. 도메인 명세는 `docs/scorecard/design-guideline.md`, 구조 지침은 `docs/scorecard/structure.md`.
- 판별: `plan/<slug>.md` frontmatter `report_type: ai_scorecard`, slug 는 `ai-scorecard-` 접두. 없으면 기존 stock_report 계약을 그대로 적용한다.
- 명령: `/score-plan`, `/score-research`, `/score-calculate`, `/score-draft`, `/score-review`, `/score-approve`, `/score-build`, `/score-goal`. 실행기는 `python scripts/scorecard_cli.py <stage> <slug>`, 빌드는 `python scripts/build_report.py <slug>`.
- 단일 진실은 `scorecard/`(rules, companies, baseline, runs/<slug>, history.csv)에 두고 추적한다. plan/research/drafts/reviews/output 은 생성물이며 손으로 고치지 않는다.
- 원자료·판단·규칙이 입력이고 점수는 결과다. 자동 산출 점수를 직접 수정하지 않는다. 모르는 값은 0으로 치환하지 않는다(unknown ≠ 0).
- 정성 판정(③ criteria, ⑤ A/H, ⑦ 매트릭스, ⑨ gate_inputs, ①④⑧ score)은 근거·검토자·검토일이 있어야 하고, 산식·사다리·구간 적용은 프로그램이 한다.
- 미결 규칙 결정(C-03, C-05, C-06, C-13, C-16)은 `run.json.decisions` 로만 실행 단위에서 선택한다. 기본값을 조용히 채택하지 않으며 해당 기업은 순위에서 제외된다.
- 리뷰는 4 영역(사실·출처 / 재무 계산 / 규칙 일관성 / 출력·가독성) + 체크리스트 Q01~Q23. hero 이미지·뉴스 100건 요건은 적용하지 않는다.
- 승인(`approve`)은 사용자 행위다. 승인 해시(rules/observations/judgments/run/results/draft)가 현재와 다르면 build 는 `awaiting_user` 로 멈춘다.
- 새 실행에서 상장사 ⑥은 NTM PER(4개 연속 미발표 분기 YYYYQn, 통화·주식 기준 일치)만 채점하고 근사치는 대기한다. ⑨ G4 는 `coverage_comparable: yes` 일 때만 계산한다.
- 테스트: `python -X utf8 -m unittest discover -s tests -t .`(T-01~T-12, R01~R06). 코드 변경 후 반드시 실행한다.
- 구현은 scorecard 작업 브랜치에서 진행 중이며 `scorecard/`·`scripts/scorecard_cli.py`·`docs/scorecard/`는 그 브랜치가 머지될 때 들어온다. 이 절은 그때까지 계약 선언으로만 유효하다.

## 금지·주의
- plan 없이 research/draft/build 산출물을 만들지 않는다.
- research 없이 draft를 만들지 않고, review 없이 build하지 않는다.
- 임의 가격 데이터, 샘플링 차트, 조작한 기사 URL을 넣지 않는다.
- `browser-use`와 직접 LLM API 키 호출은 사용하지 않는다.
- 가격 데이터는 `yfinance`를 사용하고, 웹 리서치는 검증 가능한 출처나 Playwright MCP를 우선한다.
- macOS/Linux는 `.sh`, Windows는 `.ps1` 스크립트를 우선 사용한다.

## 주요 산출물과 참조 문서
- 산출물: `plan/<slug>.md`, `research/<slug>.md`, `drafts/<slug>.md`, `reviews/<slug>.md`, `output/<slug>.html`, `output/assets/<slug>-selected-image.json`, `output/assets/<slug>-price-chart-v1.json`.
- 참조: `docs/pedagogy.md`, `docs/visual-system.md`, `docs/finance-style-guide.md`, `docs/output-spec.md`, `docs/image-generation-spec.md`, `docs/templates/*.md`.

## Orca worktree 간 메시지와 작업 실행
- 이 규칙은 프로젝트의 모든 worktree와 에이전트에 적용한다. 새 worktree 생성 또는 기존 worktree 작업 시작 시 이 절이 있는지 확인하고, 오래된 분기에서 누락됐으면 원본 저장소의 공통 규칙을 반영한다. 실행 중인 에이전트에는 갱신된 AGENTS.md를 읽도록 터미널로 안내한다.
- 다른 worktree에 신규 작업·보완·재검증 등 추가 실행을 요청할 때는 **메시지 발송과 터미널 실행 안내를 반드시 함께 수행한다.** `orca orchestration send/reply`로 수신함에 저장한 것만으로 요청 처리를 끝내지 않는다.
- 메시지 발송 후 수신 에이전트의 현재 terminal handle과 입력 상태를 확인하고, `orca terminal send --terminal <handle> --text "<메시지 ID와 수신함 확인·작업 실행 안내>" --enter --json`으로 실행 안내를 제출한다. 기존 입력이나 진행 중인 작업을 지우거나 중단하지 않는다.
- 실행 안내에는 확인할 메시지 ID, 해야 할 작업, 수신 확인 및 완료 회신 방법을 포함한다. 최초 제출이 처리됐는지 확인하고, 이미 처리 중인 동일 요청은 중복 제출하지 않는다.
- **발송 성공·수신 확인·작업 착수·완료는 별개 상태다.** 도구의 `accepted: true`만으로 수신·착수·완료를 주장하지 않는다. 수신 확인 회신이 오면 사용자에게 알린다.
- 상대 CLI가 실행 승인이나 인증을 기다리면 해당 상태와 필요한 조치를 사용자에게 알린다. 메시지를 보냈다는 이유로 실행 중이라고 보고하지 않는다.
- **완료 보고 뒤 수신자의 검토·재검증·통합·다음 작업이 필요하면 완료 회신도 추가 실행 요청이다.** 발신자는 완료 메시지에 다음 담당자와 할 일을 적고, 해당 담당자의 현재 터미널에 메시지 ID와 실행 안내를 반드시 제출한다. 수신함 알림만으로 다음 담당자가 자동 실행된다고 가정하지 않는다.
- **작업을 요청하는 쪽이 지시서 끝에 자기 회신용 terminal handle을 적는다.** 받는 쪽이 `orca terminal list`로 찾게 하지 않는다. 한 worktree에 터미널이 둘 이상(예: claude와 codex)이면 어느 쪽이 담당자인지 목록만으로는 가릴 수 없고, 못 찾으면 터미널 안내가 조용히 생략된다. 2026-09-14에 완료 회신 네 건이 수신함에만 남아 조율자가 모른 채 워커가 놀았고, 원인이 그것이었다.
- **한 과제의 끝은 세 단계다** — 커밋 → `orca orchestration send`(본문) → `orca terminal send`(한두 줄 안내). 둘째까지만 하면 상대가 모른다. 터미널 안내 본문은 짧게 쓰고 전문은 수신함에 둔다.
- **AGENTS.md는 `main`에서만 고친다.** 각 worktree는 `git merge main`으로 받아온다. worktree마다 같은 수정을 따로 적용하지 않는다 — 그렇게 하면 같은 커밋이 브랜치 수만큼 다른 SHA로 생기고 파일이 갈라진다. 2026-09-11에 `docs: Review 계약 제목 오타 복구` 한 줄이 다섯 브랜치에 따로 존재하고 AGENTS.md가 세 버전으로 갈라진 것이 확인됐다.
- 작업 시작 전 `git log --oneline <branch>..main`으로 뒤처진 커밋이 있는지 확인한다. 있으면 머지부터 한다. 규칙만이 아니라 버그 수정도 거기 있다.
- `main` 머지 후 실행 중인 에이전트에는 메시지와 터미널 안내로 AGENTS.md 재읽기를 요청한다. 재읽기 확인 회신을 받아야 적용 확인으로 처리한다. 재시작은 필요하지 않으며 기존 작업과 입력을 보존한다.
- 단순 수신 확인이나 후속 작업이 전혀 없는 결과 공유만 터미널 실행 안내 대상에서 제외한다. 재읽기 확인 회신에는 다시 실행 안내를 보내지 않아 알림 순환을 방지한다.

## 원자료 조사 규율

모든 worktree의 조사·검증 작업에 적용한다. 지시서에 매번 적지 않아도 기본값이다.

- **밖에서 찾기 전에 저장소 안을 먼저 본다.** 보존된 원자료·이전 과제의 `_raw`·프로젝트 내 원본 문서를 먼저 연다. 2026-09-11에 "없다"고 적힌 값이 이미 저장소 안에 있던 사례가 세 번 나왔다.
- **출처가 여러 파일이면 전부 연다.** 값과 그 값을 소비하는 규칙이 다른 파일에 있을 수 있다.
- **값·문언·인용 위치를 셋 다 확인한다.** 연도 칸, 주석 번호, 페이지를 원문에서 그 번호로 실제 찾아지는지 본다. 값이 맞아도 위치가 틀리면 다음 사람이 그 자리에서 아무것도 못 찾는다.
- **재무표는 열 머리글에서 축을 먼저 확정한다.** 최신이 맨 왼쪽이라고 가정하지 않는다. 오름차순 표가 흔하다.
- **같은 제출본 안에서 수치가 갈리면 감사 재무제표 본문을 우선한다.** MD&A·서술부는 반올림하거나 다른 기준을 쓸 수 있다.
- **발행사가 준 두 번째 칸을 체크섬으로 쓴다.** 20-F의 편의환산 USD 칸처럼 같은 값의 다른 표현이 있으면 선언 환율로 역검산한다. 줄을 놓치면 합계가 안 맞아 드러난다.
- **없는 것은 세 갈래로 구분한다.** 회사가 공시하지 않았다 / 우리가 못 찾았다 / 어느 쪽인지 모르겠다. 마지막을 첫째로 승격하지 않는다.
- **값이 없으면 같은 원문에서 "왜 없는지"를 한 번 더 검색한다.** 회계정책 면제 선언 같은 근거가 같은 문서에 있을 수 있다.
- **0이 나오면 부재인지 탐색 실패인지 가른다.** 고정 후보 목록으로 태그를 찾으면 체계가 다른 발행사가 0으로 나온다.
- **결측을 0으로 반환하지 않는다.** 0은 유효한 값처럼 보여 결측이라는 사실이 사라진다.
- **기존 점수·파생값을 정답 fixture로 쓰지 않는다.** 어긋나면 어긋난 대로 보고한다.
- **범위를 한 값으로 좁히거나 갈린 것을 고를 때는 좁혔다는 사실과 근거를 함께 남긴다.**
- **보고서의 모든 단정을 자기 산출물과 역추적 대조한다.** 산출은 맞는데 요약이 그것과 어긋나는 일이 있다.
- **한 곳에서 확정한 정의를 같은 이름이라는 이유로 다른 소비자에 옮기지 않는다.** 같은 단어가 자리마다 다른 것을 가리킬 수 있다.

## Memory System
- 반복 실패 방지를 위해 `docs/memory-system.md` 규칙을 따른다.
- 실패/재시도 비용이 큰 관측은 `memory/_daily/YYYY-MM-DD.md`에 append한다.
- 같은 패턴 3회 이상 또는 재발 비용이 큰 실패는 `memory/topics/{slug}.md`로 추출한다.
- memory 변경 후 `python3 scripts/validate_memory.py`를 실행한다.
- 작업 시작 시 관련 topic만 읽는다: 시간/yfinance=`time-sync`, 외부 API=`external-api`, 이미지=`image-workflow`, 단계 순서=`pipeline-order`, 빌드=`build-errors`, git=`git-workflow`, hook/validator=`guardrails`.
