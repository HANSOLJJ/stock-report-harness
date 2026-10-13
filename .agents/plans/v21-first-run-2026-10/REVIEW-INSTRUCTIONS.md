# 리뷰 세션 공통 지시서 (2026-10 규칙 v2.1 첫 실행)

실행 `ai-scorecard-2026-10-v21`(기준일·정보 마감 2026-10-12, 규칙 v2.1)의 1차 리뷰다. 절차는 `.claude/skills/score-review/SKILL.md` 가 원본이다(한 번에 끝낸다, 표본 대조 금지, 회사를 가로지르는 표 셋). 이 실행은 직전 실행 `ai-scorecard-2026-10-recheck` 와 사실이 같고 규칙만 v2.1 로 바뀌었다. 판단 98칸(①②③④⑤⑦⑧ × 14)은 모두 이 실행에서 다시 매겼다. 결정과 경계 사례는 `.agents/plans/v21-first-run-2026-10/context-notes.md` 에 있다.

## 읽을 것

`output/ai-scorecard-2026-10-v21/` 의 `draft.md`, `research.md`, `results.json`, `observations.json`, `judgments.json`, `sources.json`, `evidence/evidence.json`, `triggers.json`, `preview.md`, `run.json`. 규칙은 `scorecard/rules/v2.1.json` 과 `docs/scorecard/rules.md`. 큰 파일은 grep·rg·Python 으로 필요한 부분만 읽는다.

## 지킬 것

- 실행 폴더에는 자기 영역 파일 `review-parts/<영역>.md` 하나만 쓴다. `scorecard_cli.py` 의 쓰는 명령(`propose`·`judge`·`confirm`·`research`·`calculate`·`draft`·`review-template`)은 부르지 않는다. 엔진 대조는 메모리에서 한다(`engine.compute(engine.load_context(slug))`).
- SEC 공시 원문은 `uv run --frozen python -X utf8 scripts/scorecard_cli.py sec-get <SEC 주소>` 로만 받는다. SEC 요청이나 User-Agent 를 직접 만들지 않는다. `.env` 는 읽거나 고치지 않는다. 접근이 막힌 페이지를 User-Agent 를 바꿔 우회하지 않는다. Google News 중계 주소는 `scorecard_cli.py resolve-urls --url <주소>` 로 푼다.
- `needs_fix` 는 점수·순위·체크리스트 판정을 바꾸는 발견에만 쓴다. 그 밖의 지적은 영역 파일의 「다음 실행 과제」 절에 적는다. 발견마다 바뀌는 점수를 엔진 모의 계산으로 적는다.
- 이해상충 표기는 보지 않는다(AGENTS.md). 문장은 완결된 현재 상태 문장으로 쓴다.
- 스크래치 파일은 `C:\Users\noble\AppData\Local\Temp\claude\E--sourcecode-01-side-project-stock-report-harness\3f23ec5b-078b-4f45-a195-366647b227cf\scratchpad\rv-<영역>\` 아래에만 둔다. 셸 명령은 한 번에 하나씩 실행하고 `&&`·`;` 로 잇지 않는다.

## 영역 파일 형식

`output/ai-scorecard-2026-10-recheck/review-parts/rule-consistency.md` 와 같은 모양이다. frontmatter(`reviewer_agent`, `session`, `reviewed_at: 2026-10-13`, `round: 1`), 제목 줄, 본문 첫머리의 `검토자:`·`결과:`(pass|needs_fix|blocked)·`요약:`·`검토 기준:`(review.md frontmatter 의 results_hash·draft_hash 와 같은지) 줄, 그 뒤에 확인한 범위, 발견(FINDINGS, 발견마다 회사·항목·근거·바뀌는 점수), 체크리스트(맡은 Q 번호의 결과와 근거), 「다음 실행 과제」.

## v2.1 에서 새로 볼 것

- ① AI 수익화 '예' 의 두 조건과 상한 4, 공동화 트리거(TRG-113~118).
- ④ 층별 보유표(14사 × 6층, 칸마다 `layer_evidence`), AI 무관 매출 몫, 주 레이어, 준비 중 칸의 트리거(TRG-119·120).
- ⑥ 성장 조정 P1′, 지분 평가손익 이익 조정(Alphabet·Amazon·Microsoft·NVIDIA·Tesla), 비상장 P/S 구간표 복귀(OpenAI·Anthropic 보정 매출 미등록).
- ⑦ 큼·돌아옴 −3, ⑧ 네 축과 공급 축 안전장치·정책 기본값 −1.
- 점수 밖: 현금 연결표, 국면 지표(설비투자 가속도·공급자 지원 비중·마진 두 수열·SDLLMTK).
