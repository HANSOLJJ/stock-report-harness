# 레인 S 보고서: 스킬 문구 이식, 종목 파일 삭제, 문서 정리

최종 커밋 SHA: `ccb186f` (브랜치 `HANSOLJJ/lane-S`, 기준 `46da56c`)

## 한 일

| 커밋 | 내용 |
| --- | --- |
| `5453f8c` | `score-collect` 스킬 초안(SKILL.md, agents/openai.yaml)과 `/score-collect` 커맨드를 만들었다. `content-editor` 를 `git mv` 로 `evidence-editor` 로 바꾸고(.md, .toml) 내용을 다시 썼다. |
| `378e621` | 종목 전용 추적 파일 130개 가까이 `git rm`. output/*.html 4개와 output/assets, stock-* 스킬(.claude 7, .agents 7)과 커맨드 6, `.codex/hooks/**`, design/, sample/, sample.png, review.md, requirements.txt, 문서 3종. |
| `ccb186f` | AGENTS.md, README.md, docs/memory-system.md 의 종목 서술을 제거했다. |

문서 정리에서 지시서 밖으로 판단한 부분은 다음과 같다.

- AGENTS.md 제목이 `stock-report-harness 운영 지침` 이어서 검증(`rg 'stock-'` 0건)을 위해 `채점표 하네스 운영 지침` 으로 바꿨다.
- AGENTS.md `## 금지·주의` 에서 지운 줄은 plan/research/draft/build 순서 줄 둘과 `.ps1` 우선 줄이다. "임의 가격 데이터, 샘플링 차트, 조작한 기사 URL" 줄과 yfinance 줄은 일반 규칙으로 보아 남겼다.
- README 의 설치 안내를 `pip install -r requirements.txt` 에서 `uv sync --frozen` 으로 바꿨다(requirements.txt 삭제, pyproject.toml 이 기준).
- memory-system.md 의 순서 행은 `/score-*` 단계 순서로 바꾸고 수동 테스트 예시 블록은 지웠다.

## 검증

- 삭제 대상은 `git ls-files` 에 없다. `output/.gitkeep`, `docs/output-spec.md`, `docs/finance-style-guide.md` 는 남아 있다. 신규 5개 파일이 있고 `content-editor.*` 는 없다.
- unittest: 757건 실행, 실패 7 · 오류 30 · skipped 5. 실패·오류 집합이 `baseline-failures.txt` 와 동일(diff 결과 SAME).
- pytest: 28 failed · 109 errors (클래스 단위 오류를 테스트별로 집계). 기준 커밋 `46da56c` 를 `git archive` 로 임시 경로에 풀어 같은 명령으로 돌린 결과(45 failed · 109 errors)와 비교하면 현재 집합이 부분집합이며 새로 늘어난 항목은 없다. 줄어든 9건은 기준 추출본에만 있던 항목이다.
- `npm run check` 통과.
- `rg -n 'stock-' AGENTS.md README.md docs/memory-system.md` 0건.

## 삭제 뒤 남은 참조 (고치지 않음)

- `scripts/memory_context.py:13,59` stock-* 명령 정규식 (레인 C)
- `scripts/build_report.py:131,463`, `scripts/validate_report_contract.py:405,409` requirements.txt·toss_design 문구 (레인 A)
- `tests/test_scorecard_f6_v17.py:580` 규칙 note 문자열 (영향 없음)
- `.claude/agents/report-designer.md:16,24,26` toss_design·stock-build (4.5 에서 재작성)
- `.claude/hooks/remind-review.sh:84` `/stock-review` 안내 문구 (소유 밖)
- 소유 파일 중 남긴 것: AGENTS.md 16행의 "hero 이미지·뉴스 100건 요건은 적용하지 않는다"(AI Scorecard 절), 같은 절의 경로 문구, memory-system.md 의 `image-workflow` 행과 AGENTS.md 메모리 절의 `image-workflow`·`pipeline-order` 토픽 목록. 모두 지시서가 바꾸지 말라고 한 절이거나 `stock-` 문자열이 없다.

## 소유 밖 문제와 남은 일

- **통합 브랜치 병합을 하지 못했다.** `git merge HANSOLJJ/revision_checker` 와 `git rev-list` 비교가 권한 분류기에서 거부되어 실행하지 못했다. 이 브랜치는 `46da56c` 위에 있으므로 조율자가 병합하거나 병합 권한을 준 뒤 다시 지시해 주기 바란다. 병합 뒤 테스트 재실행은 하지 않았다.
- 이 보고서는 커밋 3개 제한에 맞추어 커밋하지 않은 파일이다.
- `docs/output-spec.md` 삭제는 지시서대로 조율자가 레인 C 병합 뒤 한다.
