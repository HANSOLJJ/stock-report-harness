# 원문 연결 지시서 (2026-10-07)

실행 `ai-scorecard-2026-10-rescore`(기준일 2026-10-06, 정보 마감 2026-10-06)의 판단 문장을 원문과 잇는다. 맡은 기업마다 입력 파일 `link/<company_id>.input.json` 을 읽고 결과를 `link/<company_id>.output.json` 하나로 쓴다. **실행 폴더(`output/`)와 그 밖의 저장소 파일은 고치지 않는다.** 조율자가 결과를 검사한 뒤 반영한다.

## 왜
판단 문장의 사실은 URL 없는 내부 문서에서 왔다. 이제 올릴 근거·내릴 근거의 모든 줄은 끝에 원문 근거 표지 `[EV-…]` 를 달아야 하고, 그 근거는 출처 URL·본문 발췌·인용 위치를 갖춰야 한다(`docs/scorecard/guide.md` 5.6·5.7 을 먼저 읽는다).

## 할 일 (판단마다, `evidence_up`·`evidence_down` 의 줄마다)
1. 그 줄의 사실을 받치는 **원문**을 찾는다. 우선순위는 이렇다.
   - SEC 공시: `uv run --frozen python -X utf8 scripts/scorecard_cli.py sec-get <SEC 주소>` 로만 받는다. `data/<company_id>/filings/` 에 받아 둔 공시가 있으면 먼저 본다.
   - 회사 1차 발표(IR 보도자료, 공식 블로그, 실적 발표문).
   - 신뢰할 수 있는 언론 보도, 벤치마크 원 사이트(artificialanalysis.ai, lmarena.ai 등).
   - 웹 도구는 `ToolSearch` 로 `WebSearch`·`WebFetch` 또는 Playwright 도구를 불러 쓴다.
2. 원문을 **직접 열어** 그 사실이 적힌 문장·표 줄을 그대로 옮긴다(`excerpt`, 600자 이하, 원문 언어 그대로, 요약·번역 금지). 제목과 같으면 안 된다.
3. 그 자리를 `locator` 에 적는다. 공시는 `10-Q (2026-06-30) Note 7 Debt — Credit Facilities 표`, 기사는 `기사 4번째 문단` 처럼 다음 사람이 그 자리를 찾을 수 있게 쓴다.
4. 원문 발행일이 **2026-10-06 이하**여야 한다. 그 뒤 자료만 있으면 못 찾은 것으로 친다.
5. 줄 끝에 표지를 붙인다. `… 미인출 상태다. [EV-amazon-014]`, 근거가 둘이면 `[EV-amazon-014, EV-amazon-015]`. 문장 내용은 바꾸지 않는다.
6. 원문 값이 문장과 다르면 원문에 맞게 문장을 고치고 `corrections` 에 적는다. 고친 줄도 표지를 단다.
7. 원문을 찾지 못하면 그 줄을 방향 칸에서 빼고, 판정 칸(`evidence_after`) 끝에 완결된 문장으로 옮긴다. 예: `"Stargate LLC 에 $7B 를 지분 출자했다는 사실은 원문을 찾지 못해 확인하지 못했다."` 그리고 `unfound` 에 적는다. 그 사실이 점수를 받치는 핵심이면 `score_bearing: true`.
8. 두 방향 칸이 모두 비게 되면 그대로 두지 말고 `unfound` 에 `"both_empty": true` 로 알린다.

판정 칸의 기존 줄은 그대로 둔다(7번에서 덧붙이는 것만 허용).

## 근거 ID 와 출처 ID
- 새 근거 ID 는 입력 파일의 `next_evidence_number` 부터 `EV-<company_id>-NNN`(세 자리)로 차례로 쓴다. 근거의 `company_id` 는 **판단의 기업**이다(다른 회사 기사여도).
- 같은 원문·같은 자리로 여러 줄을 받치면 근거 하나를 여러 줄에서 인용한다.
- `existing_evidence` 의 근거가 그 줄을 받치면 새로 만들지 말고 그 ID 를 쓰되, 원문을 열어 `evidence_updates` 에 본문 `excerpt` 와 `locator` 를 준다.
- 새 출처 ID: SEC 공시는 `SRC-SEC-<company_id>-<accession 숫자만>`, 그 밖은 `SRC-WEB-<company_id>-NNN`(001 부터). 같은 URL 은 출처 하나.

## 출력 형식 (`link/<company_id>.output.json`, UTF-8)
```json
{
  "company_id": "amazon",
  "sources": [
    {"source_id": "SRC-SEC-amazon-000101872426000026", "title": "Amazon 10-Q (2026-06-30)", "publisher": "SEC EDGAR",
     "url": "https://www.sec.gov/Archives/edgar/data/1018724/000101872426000026/amzn-20260630.htm",
     "accessed_at": "2026-10-07", "sha256": null, "conflict_of_interest": null, "note": null,
     "kind": "filing", "company_id": "amazon", "published_at_utc": "2026-07-31T00:00:00Z"}
  ],
  "evidence": [
    {"evidence_id": "EV-amazon-014", "company_id": "amazon", "factors": ["F9"], "kind": "filing",
     "source_id": "SRC-SEC-amazon-000101872426000026", "published_at_utc": "2026-07-31T00:00:00Z",
     "title": "Amazon 10-Q (2026-06-30)", "excerpt": "<원문 그대로>", "locator": "10-Q Note 7 Debt — Credit Facilities",
     "relevance": "아마존 ⑨ 의 완충에 들어가는 미인출 여신의 구성과 만기다.", "channel": "disclosure",
     "conditional_impact": null, "horizon": "현재", "counter_evidence": [], "unverified": [],
     "change_vs_previous": "new", "status": "confirmed", "reviewer": "agent-link", "reviewed_at": "2026-10-07"}
  ],
  "evidence_updates": [{"evidence_id": "EV-amazon-003", "excerpt": "<본문 원문>", "locator": "기사 2번째 문단"}],
  "judgments": [
    {"judgment_id": "amazon.F9.fix54", "evidence_after": ["<판정 칸 전체>"],
     "evidence_up_after": ["<표지 붙은 줄>"], "evidence_down_after": ["<표지 붙은 줄>"]}
  ],
  "unfound": [{"judgment_id": "…", "column": "up|down", "line": "<원래 줄>", "searched": "<찾아본 곳>", "score_bearing": false}],
  "corrections": [{"judgment_id": "…", "before": "<원래 줄>", "after": "<고친 줄>", "why": "<원문 값>", "evidence_id": "EV-…"}]
}
```
- `judgments` 에는 맡은 기업의 **모든 판단**을 싣는다. 세 칸은 각각 반영 뒤 전체 목록이다.
- `kind`: SEC 공시는 `filing`, 나머지는 `news`. `channel`: SEC `disclosure`, 회사 발표 `company_statement`, 언론 `press`, 벤치마크·집계 사이트 `secondary`. 출처 `kind` 는 `filing` 또는 `news`.
- 날짜: `published_at_utc` 는 `YYYY-MM-DDTHH:MM:SSZ`(시각을 모르면 `T00:00:00Z`), `accessed_at` 은 `YYYY-MM-DD`.

## 금지
- URL 을 만들어 내지 않는다. 직접 열어 본 페이지의 URL 과 그 페이지에서 본 문장만 쓴다.
- 문장에 없는 새 사실을 더하지 않는다. 문장을 쪼개거나 합치지 않는다(6·7번 예외).
- `relevance`·문장에 규칙 버전 표기(v1.x), 변경 표시, 작업 번호, "기준선"·"이전 실행에서"·"위 줄" 같은 다른 판 참조를 쓰지 않는다. `conditional_impact` 는 `null`.
- 출처의 이해관계를 이유로 일을 멈추지 않는다.

## 끝나면
마지막 답변에 기업별로 줄 수, 연결한 줄 수, 새 근거 수, `unfound`(그중 `score_bearing`), `corrections` 수, `both_empty` 판단을 짧게 적는다.
