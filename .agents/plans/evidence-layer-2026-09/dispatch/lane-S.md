# 레인 S — 단순 선행: 스킬 문구 이식, 종목 파일 삭제, 문서의 종목 서술 제거

에이전트: Claude Sonnet 5.5. 의존: 없음(0단계 완료). 공통 규약: `README.md` 를 먼저 읽는다.

## 목표 (Target · Change)

채점표(scorecard)만 남기고 종목 리포트(stock report) 전용 파일을 저장소에서 지운다. 지우기 전에 `stock-research` 스킬의 재사용 가능한 규칙 문구를 새 `score-collect` 스킬 초안으로 옮기고, `content-editor` 리뷰어를 `evidence-editor`(근거 불릿 리뷰어)로 바꾼다. 마지막으로 AGENTS·README·memory-system 문서에서 종목 서술을 제거한다.

세 커밋으로 나눈다. 순서가 중요하다. 문구 이식 → 파일 삭제 → 문서 정리.

## 소유 파일 (Ownership)

- `.claude/skills/**`, `.claude/commands/**`
- `.claude/agents/content-editor.md` (→ `evidence-editor.md`), `.codex/agents/content-editor.toml` (→ `evidence-editor.toml`)
- `.agents/skills/**`, `.codex/hooks/**`
- `output/*.html`, `output/assets/**` (`output/.gitkeep` 은 남긴다)
- `design/`, `sample/`, `sample.png`, `review.md`, `requirements.txt`
- `docs/stock-report-pipeline.md`, `docs/pedagogy.md`, `docs/visual-system.md`
- `AGENTS.md`, `README.md`, `docs/memory-system.md`

만지지 않는 것: `scripts/**`, `tests/**`, `.claude/hooks/**`, `.claude/settings.json`, `.codex/hooks.json`, `docs/scorecard/**`, `docs/finance-style-guide.md`(유지), `.claude/agents/fact-checker.md`·`report-designer.md`(4.5 에서 재작성), `docs/output-spec.md`(보호 훅이 삭제를 막는다. 조율자가 레인 C 병합 뒤 지운다).

## 1.1 문구 이식

커밋 메시지: `docs(skills): stock-research 규칙을 score-collect 초안으로, content-editor 를 evidence-editor 로`

1. `.claude/skills/stock-research/SKILL.md` 를 읽고 다음 규칙만 골라낸다. 1차 출처 우선. URL 조작 금지, 없는 URL 은 `url: null` 과 `url_is_fallback` 표시. 차단·실패 시 누락을 명시하고 조용히 다른 자료로 대체하지 않음. 사실과 추론의 분리.
2. `.claude/skills/score-collect/SKILL.md` 를 새로 쓴다. 형식은 `.claude/skills/score-research/SKILL.md` 를 따른다(frontmatter `name`·`description`, `# 제목`, `## 절차`, `## 제약`, `## 완료 보고`). 파일 머리에 `> 초안 — collect 명령은 3.4 에서 구현되고 이 스킬은 4.5 에서 완성한다.` 를 둔다.
   - 절차. (1) `output/<run_id>/run.json` 이 있는지 확인한다. (2) `uv run --frozen python -X utf8 scripts/scorecard_cli.py collect <run_id> [--company a,b] [--kind news|filings|prices|all] [--since YYYY-MM-DD]` 로 후보를 모아 `output/<run_id>/evidence/candidates.json` 을 만든다. (3) 후보를 읽고 factor 와 관련 있는 것만 `evidence/evidence.json` 에 `status: candidate` 로 선별한다. `excerpt` 는 원문 그대로 600자 이하, `relevance` 는 추론임을 표시한다. (4) 재채점 조건은 `triggers.json` 에 `status: watching` 으로 적는다. 미래 점수를 적지 않는다. (5) `uv run --frozen python -X utf8 scripts/scorecard_cli.py research <run_id>` 를 실행한다.
   - 제약. 사람이 `confirmed` 로 올리기 전까지 `status: new` 판단이 `candidate` 근거를 인용하지 않는다. `not_disclosed`(발행사가 공시하지 않음을 확인)와 `unverified`(우리가 못 찾음)를 구분한다. 기사 본문을 가져오지 않는다(제목·요약·URL 만). 다른 기업의 점수를 근거로 인용하지 않는다. 위 1번의 네 규칙을 여기 넣는다.
3. `.claude/skills/score-collect/agents/openai.yaml` 을 `score-research` 의 것과 같은 형식으로 만든다. `.claude/commands/score-collect.md` 를 기존 `.claude/commands/score-research.md` 형식으로 만든다.
4. `.claude/agents/content-editor.md` 를 `git mv` 로 `evidence-editor.md` 로 바꾸고 내용을 다시 쓴다. frontmatter `name: evidence-editor`, description 은 "채점표 근거 불릿(evidence.json 과 draft 의 근거 절)의 …" 로 시작한다. 검토 항목은 다음이다. 불릿 하나에 주장 하나와 `evidence_id`. 다른 기업의 점수 인용 금지. 낡은 최상급 표현 금지(C-19). 금지 투자 표현(매수·매도 지시, 수익 보장) 없음. `excerpt` 가 원문과 같음. `relevance` 가 추론으로 표시됨. `not_disclosed` 와 `unverified` 를 섞지 않음. `published_at_utc` 가 `run.info_cutoff` 이하. 마지막 문장은 기존처럼 pass 조건이다.
5. `.codex/agents/content-editor.toml` 도 `git mv` 로 `evidence-editor.toml` 로 바꾸고 같은 내용을 넣는다(`name`, `description`, `developer_instructions`). 기존 파일의 `\r` 은 따라 넣지 않는다.

## 1.2 종목 파일 삭제

커밋 메시지: `chore: 종목 리포트 전용 파일 제거 — 채점표만 남긴다`

`git rm` 대상은 전부 추적 파일이다. `git ls-files` 로 확인하고 지운다.

- `output/*.html` 4개, `output/assets/**` 전부
- `.claude/skills/stock-*/**` 7개 스킬, `.claude/commands/stock-*.md` 6개, `.agents/skills/stock-*/**` 7개 스킬
- `.codex/hooks/**` (sh 8개 + `lib/guardrail-common.sh`). 이 사본은 `.codex/hooks.json` 이 부르지 않는 죽은 파일이다.
- `design/toss_design.md`, `sample/skhynix.html`, `sample.png`, `review.md`, `requirements.txt`
- `docs/stock-report-pipeline.md`, `docs/pedagogy.md`, `docs/visual-system.md`

`docs/output-spec.md` 는 지우지 않는다.

커밋 메시지 본문에 사유를 적는다. 사용자 결정 2026-09-30, 종목 리포트 파이프라인 폐기, 채점표만 유지. 주석 처리 규칙은 살아 있는 기능의 계약 변경에만 적용되므로 삭제한다.

삭제 뒤 남은 참조를 `rg` 로 찾아 보고서에 적는다. 고치지 않는다. 검색어 `stock-research|stock-build|stock-plan|stock-draft|stock-review|stock-image|stock-goal|toss_design|pedagogy|visual-system|stock-report-pipeline|requirements\.txt|content-editor`, 대상 `scripts/ tests/ .claude/ docs/ README.md AGENTS.md package.json`. 이미 알려진 것은 `scripts/memory_context.py` 의 stock-* 명령 정규식(레인 C 가 처리), `scripts/build_report.py`·`validate_report_contract.py` 의 toss_design 주석(레인 A 가 처리), `tests/test_scorecard_f6_v17.py:580` 의 `stock-research` 는 규칙 v1.7 파일의 note 문자열을 읽는 것이라 영향 없음이다.

## 1.4 문서

커밋 메시지: `docs: AGENTS·README·memory-system 의 종목 리포트 서술 제거`

- `AGENTS.md`. `## 목적` 을 채점표 하네스로 두세 문장으로 다시 쓴다. 종목 절(`## 명령과 기본 순서`, `## Plan 계약`, `## Research 계약`, `## Draft 계약`, `## Image 계약`, `## Review 계약`, `## Build 계약`, `## 주요 산출물과 참조 문서`)과 `## 금지·주의` 의 종목 전용 줄(hero·yfinance 차트·`.ps1` 우선 등)을 지운다. 남기는 절은 `## AI Scorecard 계약`, `## 금지·주의` 의 일반 줄, `## Orca worktree 간 메시지와 작업 실행`, `## 원자료 조사 규율` 이다. AI Scorecard 절에서 "없으면 기존 stock_report 계약을 그대로 적용한다" 문장과 마지막 불릿 "구현은 scorecard 작업 브랜치에서 진행 중이며 … 계약 선언으로만 유효하다" 를 지운다(둘 다 낡았다). 그 절의 경로 문구(`plan/<slug>.md` 등)는 바꾸지 않는다. 4.6 이 한다.
- `README.md`, `docs/memory-system.md`. 종목 리포트 서술·명령·예시를 지우고 채점표 서술만 남긴다. 없는 파일을 가리키는 링크가 남지 않게 한다.

## 검증 (Observable acceptance)

- `git ls-files` 에 위 삭제 대상이 없다. `output/.gitkeep`, `docs/output-spec.md`, `docs/finance-style-guide.md` 는 남아 있다.
- `.claude/skills/score-collect/SKILL.md`, `.claude/skills/score-collect/agents/openai.yaml`, `.claude/commands/score-collect.md`, `.claude/agents/evidence-editor.md`, `.codex/agents/evidence-editor.toml` 이 있다. `content-editor.*` 는 없다.
- unittest 결과의 실패·오류 집합이 `baseline-failures.txt` 와 같다. pytest 도 같은 집합이다.
- `npm run check` 통과. `rg -n 'stock-' AGENTS.md README.md docs/memory-system.md` 가 0건.
- 보고서 `validation/lane-S-cleanup/REPORT.md`.
