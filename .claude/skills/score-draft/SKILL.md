---
name: score-draft
description: scorecard results.json 에서 Markdown 초안(output/<run_id>/draft.md)을 생성한다. /score-calculate 뒤 /score-draft <run_id> 로 사용한다.
---

# 채점 초안 스킬

## 절차

1. **규칙 v3.0 이상 실행은 draft 전에 모든 회사의 한 줄 요약을 쓴다(2026-10-24 사용자 지적).** 요약은 이 실행의 점수를 인용하므로 init 이 옮기지 않고, 정기·기업 추가·실적 반영 실행 모두 14개사 전부를 다시 쓴다(실적 반영 실행도 가격이 모든 회사를 바꾼다). 없으면 계약 검증이 회사 이름을 대며 막는다. 규칙 v3.0 시범 실행부터 q3b 까지 요약 없이 나갔다.
   - 회사마다 `uv run --frozen python -X utf8 scripts/scorecard_cli.py propose <run_id> --company <id> --factor SUMMARY --evidence "…" --reason "…"` 로 쓰고, `results.json` 의 점수와 대조한 뒤 `proposal` 로 반영한다.
   - 한 문단으로 쓴다. 과점을 쌓은 항목과 그 사실, 함정을 만든 항목과 그 사실, 조정 점수와 순위를 이 실행의 점수로 적는다. 그 회사의 전략이 무엇으로 돈을 버는지가 한 번 읽어 보이게 쓴다.
   - 판단 근거와 같은 완결 문장 규칙을 따른다(AGENTS.md 「금지·주의」). 다른 회사의 점수·순위를 인용하지 않는다.
2. `uv run --frozen python -X utf8 scripts/scorecard_cli.py draft <run_id> [--take-lock]` 를 실행한다. 결과는 `output/<run_id>/draft.md` 이다.
3. 초안은 생성물이다. 손으로 문장을 넣지 않는다. 해석·설명을 추가하려면 렌더러(`scripts/scorecard/render_md.py`)를 고치거나 run 에 주석 필드를 두고 재생성한다.
4. 필수 섹션: `# 제목` 1개, `## 개요`, `## 종합 순위표`, `## 기업별 상세`, `## 지표 원자료`, `## 방법과 규칙`, `## References`.
5. `uv run --frozen python -X utf8 scripts/validate_report_contract.py <run_id>` 로 draft 결속(results_hash)을 확인한다. 리뷰 파일이 없으면 그 오류만 남는 것이 정상이다.

## 제약

- 다른 기업의 점수·순위를 문장으로 인용하지 않는다. 비교 문장은 결과에서 생성한다.
- 투자 권유·수익 보장 표현 금지. 통화는 $M/$B/$T.

## 완료 보고

draft 경로, 검증 결과, 다음 명령 `/score-review <run_id>`.
