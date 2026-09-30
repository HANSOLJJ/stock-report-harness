# 레인 G — 문서·스킬 반영: 스킬·리뷰어 개정(4.5), AGENTS·README·structure.md(4.6)

에이전트: Claude Sonnet 5.5. 의존: 레인 S·A·B·C·D·E·F 병합 완료. 공통 규약: `README.md` 를 먼저 읽는다. 계획 원문: `../plan.md` 4단계 "스킬·에이전트·문서" 절과 "다중 에이전트 운영" 절.

## 시작 시점 상태 (2026-09-30 조율자 기록)

지금 코드가 사실이다. 문서가 코드와 다르면 코드에 맞춘다. 각 명령은 `uv run --frozen python -X utf8 scripts/scorecard_cli.py <명령> --help` 로 실제 인자를 확인하고 적는다.

- 실행 묶음은 `output/<run_id>/` 한 폴더다. 파일은 `run.json observations.json judgments.json sources.json results.json approval.json plan.md research.md draft.md preview.md review.md review-parts/ evidence/{candidates.json,evidence.json} triggers.json report.html audit.md revocations.jsonl .lock`. 경로 도우미는 `scripts/scorecard/paths.py`. 옛 경로(`plan/<slug>.md`, `research/`, `drafts/`, `reviews/`, `scorecard/runs/`, `output/<slug>.html`)는 없다.
- 수집 데이터 캐시는 `data/<company_id>/`(gitignore, `SCORECARD_DATA_ROOT` 로 덮어씀).
- 단계 CLI: `init`(새 실행은 `--rule v1.8`), `collect <run_id> [--company] [--kind news|filings|prices|all] [--since] [--forms] [--locale] [--from-file] [--dry-run]`, `research [--no-register]`, `calculate`, `draft`, `review-template`, `summary --json`, `confirm --evidence … [--reject …]`, `approve --by … [--via browser|terminal]`(사람 셸에서만), `revoke --by … --note …`(사람 셸에서만), `status`, `diff`, `resolve-cik [--apply]`. 모든 단계는 실행 잠금(`.lock`)을 쓰고 `--take-lock` 으로 인수한다.
- 승인은 사람이 `node server.js --approvals` 로 띄운 승인 페이지에서 한다. 터미널에 6자리 일회용 코드가 나오고, 페이지 `http://127.0.0.1:3000/approve/<run_id>` 에서 근거 확정·승인·취소를 한다. 코드가 5번 틀리면 서버를 다시 띄워야 한다. 승인 성공 뒤 서버는 내려간다. **에이전트는 approve·revoke 를 실행하지 않는다.** 훅(`scripts/hooks/guard.py`)과 CLI(에이전트 세션 거부) 둘 다 막는다. 에이전트가 사람에게 말하는 것은 "승인 대기" 보고이고, 사람이 에이전트에게 하는 말은 "고쳐" 와 "빌드해" 다.
- 훅은 bash 스크립트가 아니라 `scripts/hooks/guard.py` 한 모듈이다. 배선은 `uv run --frozen … python -X utf8 scripts/hooks/guard.py <훅이름>` 한 줄(Claude `.claude/settings.json`, Codex `.codex/hooks.json`). 훅 목록과 한계는 `scripts/hooks/README.md` 에 있다. `enforce-citations` 는 없어졌다. `remind_review` 는 경고만 한다.
- 규칙 v1.8 은 원천 allowlist 가 없다(personal use, 사용자 결정 2026-09-30). 문서에 약관·robots 검토 절차를 새로 만들지 않는다.
- 근거: 후보(`candidate`) → 사람이 승인 페이지에서 확정(`confirmed`). `status: new` 판단은 confirmed 근거만 인용한다. 트리거는 미래 점수를 저장하지 않는다(C-14). `not_disclosed`(발행사 확인) ≠ `unverified`(우리가 못 찾음).
- 가격: `collect --kind prices` 가 yfinance 로 ⑥ `price`·`market_cap` 관측을 넣는다. EPS·컨센서스는 받지 않는다. 조회일이 종가일과 하루 넘게 다르면 벤더 시총을 쓰지 않는다. ADR 시총은 벤더 값만.

## 소유 파일 (Ownership)

- `.claude/skills/score-*/**`, `.claude/commands/score-*.md`, `.claude/agents/*.md`, `.codex/agents/*.toml`
- `AGENTS.md`, `README.md`, `docs/scorecard/structure.md`, `docs/memory-system.md`
- 코드 안의 **안내 문자열 두 곳만**: `scripts/scorecard/render_html.py` 의 `awaiting_user: 사용자 승인 없음 — …` 메시지, `scripts/scorecard/validate.py` 의 `사용자 승인 없음: awaiting_user (…)` 메시지. 터미널 승인 명령 대신 승인 페이지(`node server.js --approvals`)를 안내하도록 문자열만 바꾼다. 이 문자열을 검사하는 테스트가 있으면 함께 맞춘다.

만지지 않는 것: 그 밖의 `scripts/**`, `tests/**`(위 문자열 테스트 제외), `output/**`, `scorecard/**`, `server*`, `docs/scorecard/design-guideline.md`·`open-items.md`·`rules/`, `docs/finance-style-guide.md`, `.agents/**`.

## 4.5 스킬·에이전트

커밋 메시지: `docs(skills): score-collect 완성, score-approve 를 승인 페이지 안내로, score-* 경로·단계 개정, 리뷰어 에이전트 재작성`

- 모든 score-* 스킬과 명령: 옛 경로를 묶음 경로로, `python scripts/…` 를 `uv run --frozen python -X utf8 scripts/…` 로 바꾼다.
- `score-collect`: 초안 표시를 지우고 실제 CLI 인자로 완성한다. 수집 → 후보 선별(`evidence.json` 에 candidate) → `triggers.json` → `research`. 승인 페이지에서 사람이 확정한다는 흐름을 적는다.
- `score-research`: collect → 선별 → `research`(인용 출처 자동 등록, `--no-register` 설명) 순서. 새 판단은 confirmed 근거만 인용.
- `score-goal`: plan 뒤에 collect 를 넣는다. `awaiting_user` 에서 멈춘다(에이전트는 승인하지 않는다).
- `score-plan`: `init --rule v1.8`.
- `score-review`: 리뷰어 입력에 evidence·triggers·sources 를 더하고, 근거 불릿 검토는 `evidence-editor` 에이전트에 맡긴다. `review-parts/<영역>.md` frontmatter 에 `reviewer_agent`, `session`, `reviewed_at` 을 둔다.
- `score-approve`: 에이전트가 할 일은 "승인 대기" 를 보고하는 것뿐이다. 사람의 절차(서버 띄우기 → 페이지 확인 → 근거 확정 → 코드 입력 승인)와 확정 뒤 해시가 바뀌면 에이전트에게 calculate·draft·review 를 다시 시킨다는 것을 적는다. 에이전트가 approve 를 실행하라는 문구를 남기지 않는다.
- `score-build`: 포트 3000 이 쓰이고 있으면 기존 프로세스를 죽이지 않고 `PORT=<빈 포트>` 로 띄운다. URL 은 `http://localhost:3000/<run_id>/report.html`.
- `.claude/agents/fact-checker.md`: 채점표용으로 재작성. `source_ids ⊆ sources`, URL 이 실제로 열리는지(조작 URL 금지), `not_disclosed_confirmed` vs `unverified`, excerpt 원문 대조, `published_at_utc ≤ info_cutoff`, candidate 근거를 인용한 `status: new` 판단 없음.
- `.claude/agents/report-designer.md`: 채점표 HTML 용으로 재작성. `docs/scorecard/structure.md` 6절 대시보드 검사, 근거·트리거 절 가독성, audit 링크, 모바일 320px. 종목 리포트·토스 디자인 언급을 지운다.
- `.codex/agents/*.toml` 을 `.claude/agents/*.md` 와 같은 내용으로 맞춘다(`\r` 없이).

## 4.6 AGENTS·README·structure.md

커밋 메시지: `docs: AGENTS·README·structure.md 를 묶음 배치·근거 계층·승인 페이지·guard.py 에 맞춘다`

- `AGENTS.md`: AI Scorecard 절의 경로 문구를 묶음 경로로, 명령 목록에 `/score-collect` 를 더한다. 단계 순서 `plan → collect → research → calculate → draft → review → (사람) 승인 → build`. 레인 S 가 지운 일반 규칙("plan 없이 research 금지", "review 없이 build 금지")을 채점표 단계 이름으로 `## 금지·주의` 에 되살린다. 새 절 `## 통제의 위치` 에 세 가지를 적는다. (1) 어느 하네스로 돌리든 통제는 코드가 한다(해시 검증이 첫 방어선, 훅은 둘째). (2) 훅은 도구 호출 밖(사람 터미널, 훅 없는 에이전트)을 못 막는다. (3) 승인 서버가 떠 있는 동안 브라우저 도구를 가진 에이전트가 터미널의 코드를 읽으면 누를 수 있다. 코드는 파일에 쓰지 않고 서버는 승인 뒤 내려간다. 사용자가 알고 수용했다(2026-09-30). 테스트 명령을 `uv run --frozen python -X utf8 -m unittest discover -s tests -t .` 와 `npm run test:node` 로 적는다. `## Orca worktree 간 메시지와 작업 실행` 과 `## 원자료 조사 규율` 은 바꾸지 않는다.
- `README.md`: 훅 표를 `guard.py` 함수 이름으로 다시 쓴다(`scripts/hooks/README.md` 를 기준으로). 설치는 `uv sync --frozen`, 테스트 명령, 실행 흐름(collect 포함), 승인 페이지 사용법, `data/` 캐시, `SEC_UA` 환경변수(값은 저장소에 넣지 않는다)를 적는다. 없는 파일을 가리키는 링크가 남지 않게 한다.
- `docs/scorecard/structure.md`: 2·5·7절(배치, 흐름, 승인)을 묶음 배치·collect 단계·근거 계층·승인 페이지로 갱신한다. 다른 절은 경로 문구만.
- `docs/memory-system.md`: 훅 설명이 `inject-memory-context.sh`·`memory_context.py` 를 가리키면 `guard.py` 의 `inject_memory_context` 로 바꾼다.

## 검증 (Observable acceptance)

- 소유 파일에서 옛 경로 검색 0건: `plan/<slug>`, `research/<slug>`, `drafts/<slug>`, `reviews/<slug>`, `scorecard/runs`, `output/<slug>.html`, `enforce-citations`, `.claude/hooks`, `memory_context.py`, `stock-`. Grep 도구로 확인한다(셸 명령에 승인 명령 문자열을 넣으면 훅이 막는다).
- 소유 파일에서 에이전트에게 approve·revoke 실행을 시키는 문구 0건. 사람 셸 절차로 적는 것은 괜찮다.
- 문서에 적은 모든 CLI 인자가 `--help` 출력과 맞다.
- 테스트 기준(unittest 1085건 중 실패 1·오류 14, 전부 원자료 부재)에서 증가 없음. `npm run check`, `npm run test:node` 통과.
- 보고서 `validation/lane-G-docs/REPORT.md` 를 커밋에 포함한다. 통합 브랜치 merge 가 권한으로 거부되면 우회하지 말고 보고서에 적는다.

## 주의

- 이 워크트리의 훅은 새 `guard.py` 다. 셸 명령 문자열에 승인 명령(`scorecard_cli.py` 다음에 approve·revoke)이나 승인 파일 이름과 리다이렉션을 함께 넣으면 막힌다. 문서는 Write·Edit 도구로 쓴다.
