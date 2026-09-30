---
name: score-draft
description: scorecard results.json 에서 Markdown 초안(output/<run_id>/draft.md)을 생성한다. /score-calculate 뒤 /score-draft <run_id> 로 사용한다.
---

# 채점 초안 스킬

## 절차

1. `uv run --frozen python -X utf8 scripts/scorecard_cli.py draft <run_id> [--take-lock]` 를 실행한다. 결과는 `output/<run_id>/draft.md` 이다.
2. 초안은 생성물이다. 손으로 문장을 넣지 않는다. 해석·설명을 추가하려면 렌더러(`scripts/scorecard/render_md.py`)를 고치거나 run 에 주석 필드를 두고 재생성한다.
3. 필수 섹션: `# 제목` 1개, `## 개요`, `## 종합 순위표`, `## 기업별 상세`, `## 지표 원자료`, `## 방법과 규칙`, `## References`.
4. `uv run --frozen python -X utf8 scripts/validate_report_contract.py <run_id>` 로 draft 결속(results_hash)을 확인한다. 리뷰 파일이 없으면 그 오류만 남는 것이 정상이다.

## 제약

- 다른 기업의 점수·순위를 문장으로 인용하지 않는다. 비교 문장은 결과에서 생성한다.
- 투자 권유·수익 보장 표현 금지. 통화는 $M/$B/$T.

## 완료 보고

draft 경로, 검증 결과, 다음 명령 `/score-review <run_id>`.
