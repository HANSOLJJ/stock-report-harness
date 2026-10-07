# 근거 사슬(원문 연결) 뒤 4영역 리뷰 지시서 (2026-10-07, round 8)

실행: `output/ai-scorecard-2026-10-rescore/`. 리뷰 기준 해시는 results_hash `bacc7bc3e82a981d…`, draft_hash `0148fb46af32d9e8…` 다(`review.md` frontmatter 와 같은지 먼저 확인).

## 무엇이 바뀌었나

1. **올릴·내릴 근거의 모든 줄 끝에 원문 근거 표지 `[EV-…]` 를 달았다**(`docs/scorecard/guide.md` 5.7). 근거는 72건에서 600건이 됐고 새 528건은 모두 출처 URL·본문 발췌(`excerpt`)·인용 위치(`locator`)를 갖는다. 기존 72건 가운데 일부도 본문 발췌로 바꿨다. 검증기(`validate.citation_violations`)는 위반 0 이다.
2. **원문을 찾지 못한 사실은 방향 칸에서 판정 칸으로 옮겨 "원문을 찾지 못해 확인하지 못했다"로 적었다.** 원문 값이 달랐던 줄은 원문 값으로 고쳤다. 기업별 경위는 `.agents/plans/evidence-chain-2026-10/link/final/<company_id>.output.json` 의 `unfound`·`corrections` 와 `link/retry-*.output.json` 의 `results` 에 있다. 바뀌기 전 문장은 각 판단의 `revision_history[-1].previous` 에 있다.
3. **판정 정정**(조율자 결정, 근거는 `context-notes.md`):
   - anthropic.F2·meta.F2: 점수는 그대로이고, "세대 격차 미판정" 문장을 "세대 격차 판단에서 나온 승계 점수, 축 수는 규칙 미결"로 고쳤다(v1.5 원 규칙이 Anthropic ②5·Meta ②4 를 예시로 든다).
   - TEN-RC-05(nvidia F5·F8)·TEN-RC3-04(tesla F5·F8): 고객 자체 칩·NHTSA 조사는 ⑤ 적대 등급에서만 세고 ⑧ 에서 뺐다(규칙 2.2). ⑧ 점수는 −3·−2 그대로.
   - oracle.F7: 세로축 '돌아옴'의 근거를 미확인 Stargate 출자에서 TikTok 미국 합작법인(지분법 투자 + OCI 고객)으로 바꿨다.
   - alphabet.F7·microsoft.F7: 조달 의존 비중 '작음'을 유지하고 근거 숫자(Anthropic 약정 $200B·백로그 40% 초과, OpenAI 매출 $24.1B·약 7%)를 적었다.
4. 관측 `oracle.offbalance_B.link26`(verified): 10-Q 미개시 리스 $288B + 10-K 구매 약정 $13.309B. 승계 값 $250B 를 대신한다(아마존 B종과 같은 범위, 기준일 섞임은 레코드에 적음).
5. TRG-005(아마존 ⑨): 기준일 현재 여신 상태와 민감도(8.4·8.0·6.7년)를 앞에 두고 9.95년은 6월 공시 기준 값이라 밝혔다.
6. 렌더: 카드의 표지는 작은 글씨, 「출처」 탭 인용 근거 표에 "본문 발췌 · 위치" 칸, 리드에 factor 별 범위와 ⑥ 설명.
7. **14개사 총점·순위·factor 점수는 그대로다**(조율자 대조).

## 원칙

- 한 번에 끝낸다. 맡은 범위를 표본이 아니라 전부 본다.
- needs_fix 는 이번 실행의 목적을 해치는 발견에 쓴다: 발췌가 원문 그 자리에 없음, 표지 근거가 그 줄의 사실을 받치지 않음, 원문과 다른 숫자, 원문을 찾지 못한 사실이 방향 칸에 남음, 점수·순위·체크리스트 판정을 바꾸는 발견. 표현·분류가 갈릴 수 있는 것은 「다음 실행 과제」.
- 함정 항목(⑥⑦⑧⑨)에서 올릴 근거는 함정이 얕다는 사실, 내릴 근거는 깊다는 사실이다.
- 이해상충 표기는 보지 않는다(AGENTS.md). 저장소에서 고치는 파일은 자기 영역 파일 하나뿐이다. 단계 명령(research·calculate·draft 등)을 실행하지 않는다. 저장소 밖으로 cd 하지 않는다.
- 웹 검색 도구(`WebSearch`)는 세션 한도가 소진됐을 수 있다. 원문은 근거의 URL 을 `WebFetch`·Playwright 로 직접 열고, SEC 공시는 `uv run --frozen python -X utf8 scripts/scorecard_cli.py sec-get <주소>` 로 받는다(`data/_sec/docs/` 에 캐시가 있다). 여러 URL 을 표준 라이브러리(`urllib`) 스크립트로 받아 발췌를 대조해도 된다(외부 패키지 설치 금지). 열리지 않는 페이지(유료벽·자바스크립트)는 Playwright 로 연다.

## 영역별

- **사실·출처** — 세션 셋이 기업을 나눠 맡는다. 결과는 `review-parts/fact-sources-<a|b|c>.md` 에 쓴다(조율자가 `fact-sources.md` 로 합친다).
  - a: alibaba, alphabet, amazon, anthropic, apple · b: meta, microsoft, nvidia, openai, oracle · c: palantir, spacex-xai, tesla, tsmc
  - 맡은 기업 판단의 올릴·내릴 근거 줄마다: (1) 표지가 가리키는 근거의 `excerpt` 가 출처 URL 원문에 그대로 있고 `locator` 자리에서 찾아지는지, (2) 그 발췌가 줄의 사실(숫자·날짜·주체)을 받치는지, (3) 발행일이 2026-10-06 이하인지. 판정 칸에 "원문을 찾지 못해"로 옮긴 사실 가운데 쉽게 찾아지는 원문이 있으면 적는다(다음 실행 과제).
  - 기계 대조가 된 것과 사람이 읽어 확인한 것을 나눠 적는다. 열지 못한 근거는 이유와 함께 목록으로 남긴다.
- **재무 계산** (`financial-calc.md`): 고친 재무 숫자(link `corrections` 의 재무 항목), `oracle.offbalance_B.link26` 의 범위·합계와 G4 커버리지, TRG-005 의 8.4·8.0·6.7년(실제 계산 코드 `scripts/scorecard/calc_f9.py` 를 메모리 사본으로 불러 대조), results 의 점수·순위가 이전 승인본(git `a576ee3` 의 results.json)과 같은지.
- **규칙 일관성** (`rule-consistency.md`): 3번 판정 정정 다섯 건이 규칙과 맞는지, 같은 잣대가 다른 회사에도 닿는지(Q03: 같은 속성 이중 계산이 다른 회사 ⑤·⑧ 에 남아 있는지, ⑦ 가로축 '작음·큼'을 회사마다 같은 기준으로 댔는지). 원문 정정으로 판정 재료가 흔들린 판단(apple.F2·F3·F5, amazon.F2, tesla.F1, openai.F1·F5, anthropic.F3·F6, alphabet.F2·F7, spacex-xai.F3·F8)의 점수가 여전히 서는지. 체크리스트 Q01~Q23 을 다시 채운다(round 7 판정을 출발점으로).
- **출력·가독성** (`output-readability.md`): 메모리 렌더 HTML(아래 코드)로 카드 표지 표시, 인용 근거 표의 발췌·위치 칸, 리드 범위 문장, 판정 칸에 늘어난 "확인하지 못했다" 문장의 가독성, 리포트 크기. Playwright 로 320·768·1280px 가로 넘침 0(특히 인용 근거 표), 표지 링크 → 출처 탭 이동, 탭 전환. 리포트 본문에 `원검토|이전 실행에서|다시 매김|앞서 매긴` 0건.

메모리 렌더(빌드하지 않는다):
```python
import sys; sys.path.insert(0, 'scripts')
from tests.test_report_tabs import render
open('.playwright-mcp/review.html', 'w', encoding='utf-8').write(render('ai-scorecard-2026-10-rescore'))
```
`python -m http.server 3942 --bind 127.0.0.1 --directory .playwright-mcp` 로 띄워 연다.

## 출력

자기 영역 파일을 이번 리뷰판으로 고친다(사실·출처 세션은 새 파일). frontmatter `round: 8`, `reviewed_at: 2026-10-07`, 「검토자:」 줄 끝에 "· 원문 연결 뒤", `결과:`·`요약:`·`검토 기준:`(새 해시)을 새로 쓰고, 이전 내용은 「## 이전 리뷰 기록」 으로 옮긴다. 「## 발견」 에는 판단 ID·칸·줄 앞부분·근거 ID·고칠 방향을 적어 조율자가 그대로 제안으로 옮길 수 있게 한다. 마지막 답변에는 결과, needs_fix 발견 수와 목록, 다음 실행 과제 수만 짧게 적는다.
