---
name: score-update
description: 실적이 나온 회사만 다시 매기는 실적 반영 실행(규칙 v3.1)을 만들고 갱신 범위를 확정한다. /score-update <새 slug> --from-run <이전 slug> --update-companies a,b --update-reason "…" 처럼 사용한다.
---

# 실적 반영 실행 스킬

실적이 하나 나올 때마다 14개사를 전부 다시 매기지 않는다(2026-10-22 사용자 결정, `rules.md` 2.9). 실적을 낸 회사와 그 사건이 닿는 곳만 다시 매기고, 나머지는 이어받되 움직이지 않았음을 `diff` 로 증명한다.

## 절차

1. 이전 실행(`--from-run`)과 갱신 회사(`--update-companies`)를 정한다. 갱신 회사는 이전 실행 기준일 뒤 실적 공시(10-Q·10-K·20-F, 8-K Item 2.02)를 낸 회사다. 모르면 먼저 2단계까지 돌려 `scope` 가 알려 주는 대로 다시 만든다.
2. 실행을 만든다. 기준일은 이전 실행보다 뒤여야 하고, 가격 기준일·정보 컷오프는 새 기준일을 따른다.
   ```
   uv run --frozen python -X utf8 scripts/scorecard_cli.py init <새 slug> --from-run <이전 slug> --rule v3.1 --as-of <YYYY-MM-DD> --title "…" --request "…" --update-companies a,b --update-reason "<어떤 실적인지>"
   ```
   `--add-companies`·`--companies` 와 함께 쓰지 않는다. 이전 실행에 유효한 확인이 있으면 `--force` 로 덮어쓰지 않고 새 slug 로 만든다.
3. 공시 목록과 가격은 **모든 회사**를, 뉴스와 재무 사실은 갱신 회사만 모은다.
   ```
   uv run --frozen python -X utf8 scripts/scorecard_cli.py collect <slug> --kind filings
   uv run --frozen python -X utf8 scripts/scorecard_cli.py collect <slug> --kind prices
   uv run --frozen python -X utf8 scripts/scorecard_cli.py collect <slug> --company a,b --kind news
   uv run --frozen python -X utf8 scripts/scorecard_cli.py collect <slug> --company a,b --kind facts
   ```
   가격 종가가 아직 없는 날은 직전 종가를 쓰고 ADR 시가총액이 실패할 수 있다. 종가가 나온 뒤 `--kind prices` 를 다시 돌린다.
4. 범위를 확인한다. `[막힘]` 이 있으면 그 회사를 갱신 회사에 넣어 실행을 다시 만든다.
   ```
   uv run --frozen python -X utf8 scripts/scorecard_cli.py scope <slug>
   ```
   - 가격 기준일까지 실적 공시를 낸 회사가 갱신 회사가 아니면 막힌다. 6-K 만 내는 회사(TSMC·Alibaba)는 `[리뷰 확인]` 목록으로 나오므로 첨부를 열어 실적 공시인지 가른다.
   - 마지막 전체 갱신일(`run.json` 의 `refreshed_at`)에서 120일이 지난 회사는 갱신 회사여야 한다. 분기 실적이 없는 비상장사도 이 규칙으로 넉 달마다 다시 매긴다.
5. 갱신 회사의 공시 원문을 읽어 관측(9월 분기 TTM)·근거·이전 트리거 확인을 만든다(`score-collect`·`score-research` 스킬). 갱신 회사의 공시에서 다른 회사에 닿는 사실은 그 회사 ID 로 근거를 올린다. 확정하면 그 (회사, 항목)이 범위에 들어온다.
6. 판단 세션(Opus, 노력 high)은 갱신 회사의 정성 판단 전부와 범위에 든 항목을 ④ → ②③ → ① → ⑤ 순서로 다시 매긴다. 범위 밖 판단은 건드리지 않는다. `scope <slug>` 의 "다시 매기지 않은 범위 판단" 이 0건이 되면 끝이다.
7. `research → calculate → draft` 뒤에 `diff <slug> --against <이전 slug>` 로 범위 밖이 움직이지 않았음을 확인하고, 리뷰는 `score-review` 스킬의 「실적 반영 실행의 리뷰 범위」대로 한다. 리뷰가 경쟁사 항목을 범위에 넣으면 `scope <slug> --add 회사:항목 --reason "…"` 뒤 그 항목을 다시 매기고 research 부터 다시 돈다.
8. 확인 대기를 보고한다. 확인은 사람이 확인 페이지에서 한다.

## 제약

- 갱신 범위는 에이전트 재량이 아니라 기록(갱신 회사·새로 확정한 근거·발동한 트리거·`scope --add`)이 정한다. 범위 밖 판단을 고치면 `diff` 가 위반으로 잡는다.
- 가격은 모든 회사를 새로 받는다. 갱신 회사만 받지 않는다.
- 승계 판단 예외는 없다. 경쟁사와 잣대가 어긋나면 그 항목을 범위에 넣어 다시 매긴다.

## 완료 보고

실행 경로, 갱신 회사, `scope` 결과(범위 항목·막힘·리뷰 확인 공시), 다시 매긴 판단 수, `diff` 판정, 리뷰 상태, 확인 대기.
