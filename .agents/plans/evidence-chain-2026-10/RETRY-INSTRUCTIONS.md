# 원문 연결 2차 탐색 지시서 (2026-10-07)

1차 원문 연결(`LINK-INSTRUCTIONS.md`)에서 찾지 못한 줄을 다시 찾는다. 1차 때 세션 공용 웹 검색 한도(200회)가 바닥나 상당수는 원문이 없어서가 아니라 검색을 못 해서 남았다. **`WebSearch` 는 쓰지 않는다**(한도 소진). 대신 Playwright 로 검색 엔진 결과 페이지(`https://www.bing.com/search?q=…`, `https://duckduckgo.com/html/?q=…`)를 열어 찾고, 찾은 페이지는 `WebFetch` 나 Playwright 로 직접 연다. SEC 공시는 `uv run --frozen python -X utf8 scripts/scorecard_cli.py sec-get <주소>` 로만 받는다. 저장소 밖으로 cd 하지 않는다. `output/` 과 저장소 파일은 고치지 않고 커밋하지 않는다. 1차 지시서의 원칙(원문 직접 열기, 본문 발췌 600자 이하·원문 언어 그대로, `locator`, 발행일 2026-10-06 이하, URL 지어내지 않기)은 그대로다.

## 입력
`link/retry.input.json` 의 `items` 가 대상 줄이다. 각 항목은 `company_id`, `judgment_id`, `column`(up|down, both_empty 항목은 null), `score_bearing`, `line`(원래 줄), `searched`(1차에서 찾아본 곳)를 가진다. 맡은 기업의 항목만 처리한다. `next_numbers` 의 `<company_id>` 값부터 새 근거 번호를 매긴다.

## 순서
1. **`score_bearing: true` 항목을 먼저** 처리한다.
2. **두 방향 칸이 모두 빈 판단**(`line` 이 빈 항목: `alibaba.F7`, `anthropic.F6`)은 그 판단의 점수 방향을 받치는 원문 사실을 한두 개 찾아 새 줄로 만든다. 판단 전체는 `link/<company_id>.output.json` 의 `judgments` 에서 본다. 예: alibaba ⑦ 은 매출이 어떤 고객에게서 나오는지(20-F 부문 매출), anthropic ⑥ 은 기업가치와 매출 규모(회사 발표의 Series H post-money 와 run-rate 매출).
3. 나머지 사실 항목을 처리한다. 원래 줄이 사실이 아니라 분석·부재 주장이면(예: "자체 모델이 없다", "…은 없음이다", "…라고 판단했다") 찾지 말고 `status: "is_analysis"` 로 둔다.

## 출력 (`link/retry-<묶음 이름>.output.json`)
```json
{
  "sources": [ {1차 형식과 같다. source_id 는 SRC-WEB2-<company_id>-NNN(001 부터) 또는 SRC-SEC-<company_id>-<accession>} ],
  "evidence": [ {1차 형식과 같다. evidence_id 는 next_numbers 부터, status confirmed, reviewer "agent-link-retry", reviewed_at "2026-10-07"} ],
  "results": [
    {"judgment_id": "…", "line": "<원래 줄 그대로>", "status": "found|partial|not_found|is_analysis",
     "column": "up|down", "new_line": "<원문에 맞춘 줄 + 끝에 [EV-…]>", "dropped": "<partial 이면 못 찾은 부분>",
     "note": "<찾아본 곳·원문 값이 달랐으면 그 값>"}
  ]
}
```
- `found`·`partial` 이면 `new_line` 을 준다. 원문 값이 원래 줄과 다르면 원문 값으로 고치고 `note` 에 적는다.
- both_empty 판단의 새 줄은 `line` 을 빈 문자열로 두고 `column` 과 `new_line` 을 준다.
- `not_found` 는 찾아본 곳을 `note` 에 적는다.

## 끝나면
마지막 답변에 항목 수, found·partial·not_found·is_analysis 수, score_bearing 항목 각각의 결과, 원문 값이 달랐던 것을 짧게 적는다.
