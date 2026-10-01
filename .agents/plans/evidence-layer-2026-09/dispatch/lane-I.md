# 레인 I — 독립 검증 발견 수정: F-5(locale) · F-6(문서 불일치)

에이전트: Claude Sonnet 5.5. 의존: 레인 V 보고서 병합 완료. 공통 규약: `README.md` 를 먼저 읽는다. **발견 근거는 `validation/lane-V-independent-review/REPORT.md` 의 F-5·F-6 절이다. 먼저 읽는다.** 레인 H(Opus)가 동시에 F-1·F-2·F-3·F-4·F-7 을 고친다. 소유가 겹치지 않는다.

## 레인 H 가 확정한 계약 (README 훅 표는 이 내용으로 쓴다)

- 보호 목록: `.env*`, `.git/`, `.github/workflows/`, `docs/finance-style-guide.md`, `**/approval.json`, `scorecard/rules/v1.5~v1.7.json`, `scorecard/history.csv`, `scorecard/baseline/**`(레인 H 가 추가), `output/ai-scorecard-2026-09-baseline/`, `output/ai-scorecard-2026-09-obsreg/`.
- 셸 명령은 보호 경로가 쓰기 대상(리다이렉션 대상, 변경 동사 인자)일 때만 막고, 읽기 명령의 언급은 통과한다. 인터프리터(`python`·`node`·`uv run python`)가 보호 경로를 담으면 막는다.
- `scorecard_cli.py init … --force` 는 승인 있는 실행이면 훅이 막는다.
- 승인·취소 명령은 셸에서 막고, 에이전트 거부는 `stages.approve`·`stages.revoke` 함수 안에 있다.
- 첫 방어선의 한계: 임의 Python 을 실행할 수 있는 에이전트가 작정하면 우회할 수 있다. 최종 보증은 사람이 git 이력에서 승인 파일의 변경을 확인하는 것이다.

## 소유 파일 (Ownership)

- `scripts/scorecard/collect_news.py`, `tests/test_collect_news.py`
- `README.md`, `AGENTS.md`, `docs/scorecard/open-items.md`, `docs/scorecard/structure.md`, `docs/scorecard/design-guideline.md`(353행 옛 단계명 `finalize` 한 곳만), `docs/memory-system.md`

만지지 않는 것: `scripts/hooks/**`, `scripts/scorecard/stages.py`·`render_md.py`, `scripts/scorecard_cli.py`, 그 밖의 `tests/**`, `output/**`, `scorecard/**`, `.claude/**`, `.codex/**`.

## F-5 locale

- `collect_news.build_query_url`(또는 locale 을 나누는 곳): 하이픈 없는 언어 코드면 작은 표로 국가를 정한다. `en→US`, `ko→KR`, `ja→JP`, `zh→CN`, `de→DE`, `fr→FR`. 표에 없으면 `ValueError("locale 은 xx-YY 형식으로 준다")`. `xx-YY` 는 지금처럼 그대로. `ceid` 는 `<국가>:<언어>`.
- 테스트: `ko` → `gl=KR`, `ceid=KR:ko`. `en-US` 는 기존과 같은 URL. 모르는 언어는 예외. 커밋 `fix(collect): 언어만 준 locale 의 국가 코드 매핑`.

## F-6 문서

레인 V 보고서 F-6 의 네 항목을 고친다. 커밋 `docs: 독립 검증 F-6 — 옛 경로·훅 표·memory topic 목록·원본 폴더 서술 정정`.

- `docs/scorecard/open-items.md` 의 옛 경로(`scorecard/runs/`, `reviews/<slug>.md`), uv 없는 `python`, "훅이 python3 별칭을 요구" 전제를 지금 배치·배선으로 고친다. 항목의 의미(열린 문제)는 바꾸지 않는다.
- `README.md` 훅 표를 위 계약대로 다시 쓴다. `forbid_financial_advice` 의 셸 PostToolUse 배선, `enforce_memory` 범위(`memory/_daily/`·`memory/topics/`)를 정확히 적는다. 기준은 `scripts/hooks/guard.py` 의 실제 코드와 `.claude/settings.json` 이다(레인 H 가 바꾸는 부분은 위 계약을 따른다).
- `docs/scorecard/structure.md:4`, `design-guideline.md:30` 의 `AI_company_analysis_factor/` 서술을 사실대로 고친다(git 이 그 안 6개 파일을 추적한다). `design-guideline.md:353` 의 `finalize` 를 지금 단계명으로.
- `AGENTS.md`·`docs/memory-system.md` 의 memory topic 목록: 지금 실재하는 파일은 `memory/topics/guardrails.md` 하나다. 목록은 "주입 훅이 찾는 topic 이름" 으로 두되, 없는 파일은 관측이 생길 때 만든다는 것을 적는다.
- `AGENTS.md` 의 통제 절에 위 계약의 "첫 방어선의 한계" 한 줄을 더한다.

## 검증 (Observable acceptance)

- `tests/test_collect_news.py` 통과. 테스트 기준(unittest 1090건 중 실패 1·오류 14)에서 증가 없음. `npm run check` 통과.
- 레인 V 보고서 F-6 의 각 위치를 Grep 도구로 다시 찾아 고쳐졌는지 보고서에 적는다.
- 보고서 `validation/lane-I-review-fixes/REPORT.md` 를 커밋에 포함한다. 통합 브랜치 merge 가 거부되면 보고만.
- 셸 명령에 보호 경로 문자열(`.env` 등)이나 승인 명령을 넣으면 훅이 막는다. 문서는 Write·Edit 도구로 고친다.
