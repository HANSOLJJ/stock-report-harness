---
reviewer_agent: fact-checker
session: fc-opus55-20261007-rescore-r8b (원문 연결 서브에이전트·조율자와 다른 세션, b 묶음 전담)
reviewed_at: 2026-10-07
round: 8
---
# fact-sources-b — 사실·출처 (meta, microsoft, nvidia, openai, oracle)
검토자: Claude Opus 5.5 (claude-opus-5-5) · 사실·출처 독립 세션(이 실행을 만든 세션 아님) · 2026-10-07 · 원문 연결 뒤
결과: needs_fix
요약: 다섯 회사의 판단 41개에서 올릴·내릴 근거 135줄과 거기 달린 표지 근거 179건을 전부 봤다. 출처 URL 97개도 모두 열었다. 179건의 발췌 모두 원문에서 찾았고, 원문에 없는 발췌는 0건이다. 발행일은 176건이 2026-10-06 이하이고, 나머지 3건은 발행일이 비어 있다. 이 3건은 공시라서 제출일(07-30·09-03·09-11)로 확인하면 마감 전이다. 줄과 원문 사이에 숫자가 어긋난 곳은 없다. 최근 1년 합산값·비율(5절 목록)을 원문 표에서 모두 다시 계산했는데 모두 맞았다. 원문을 찾지 못한 사실이 방향 칸에 남은 경우도 없다. needs_fix 는 2건이고 둘 다 nvidia.F7.fix52 의 내릴 근거다. 표지가 가리키는 원문에 그 줄의 일부 사실이 없다. 하나는 CNBC 기사를 근거로 단 줄로, Anthropic Series G(최대 $10B)·xAI Series E 는 기사에 없다. 기사가 '약정(commitments)' 이라고 쓴 $40B 를 줄은 '넣었고(실측)' 라고 적었다. 다른 하나는 잔존가치 보증 담보가 Grace Blackwell 이라는 전제인데, 이를 받치는 원문이 없다. ⑦ 은 판정표 입력으로 점수가 정해지므로 두 건 모두 점수·순위에는 닿지 않는다. 다음 실행 과제는 14건이다.

검토 기준: results_hash `bacc7bc3e82a981d…`, draft_hash `0148fb46af32d9e8…`(review.md frontmatter 와 같음을 확인했다). 대조 기준은 `.agents/plans/evidence-chain-2026-10/link/final/{meta,microsoft,nvidia,openai,oracle}.output.json` 과 `link/retry-{a,b}.output.json` 이다. 스크립트는 세션 스크래치 `fsb/`(fetch.py·match.py·insp.py·ctx.py·loc.py)에 있다. Playwright 대조 코드는 `.playwright-mcp/fsb-b/pw_code.js` 에 있다(gitignore 대상).

## 확인 내용

### 1. 등록·상태(기계 점검)
- b 묶음의 판단 41개, 관측 150개, 트리거 34개를 봤다. 여기에 나오는 `source_ids`·`source_id`·`evidence_ids` 는 모두 `sources.json`·`evidence.json` 에 등록돼 있다. 근거 196건의 `source_id` 도 모두 등록돼 있다. 미등록은 0건이다.
- 방향 칸 135줄은 모두 줄 끝에 `[EV-…]` 표지가 있다. 표지가 가리키는 근거 179건은 모두 `confirmed` 이고 `reviewer`·`reviewed_at`·`locator` 가 있다. 다른 회사 ID 를 단 표지는 0건이다.
- `status: new` 판단 7개(microsoft.F9, nvidia.F7.fix52, oracle.F5, oracle.F7.fix52, oracle.F9, openai.F4, openai.F5.impl48)도 confirmed 근거만 인용한다.
- 현재 judgments 의 세 칸은 `link/final/<cid>.output.json` 의 `*_after` 와 41개 판단 모두 같다.
- 1차 `unfound` 21줄 가운데 방향 칸에 다시 들어간 것은 openai.F6(누적 조달 $185B, Pinggy)과 openai.F9(FutureSearch $62B) 2줄이다. 둘 다 2차 탐색(retry-b)에서 `found` 로 원문을 찾아 표지를 달고 되돌린 줄이다. 나머지는 판정 칸에 있다.
- 판정 칸의 표지 3건(EV-microsoft-021·022, EV-oracle-034)도 원문에서 글자 그대로 찾았다.
- 근거 196건의 `relevance`·`title` 과 판단 세 칸에서 투자 권유·매매 지시·수익 보장·FOMO 표현을 찾아봤다. 버전·작업 번호·옛 판을 가리키는 표기도 함께 찾았다. 모두 0건이다.

### 2. 발췌 원문 대조(기계 대조 → 사람 확인)
| 단계 | URL | 근거 | 결과 |
| --- | --- | --- | --- |
| SEC 공시를 `sec-get` 으로 받음(전부 캐시 적중) | 18 | 70 | 공백·따옴표 정규화 뒤 엄격 일치 41 · 문자만 비교해 일치 18(XBRL 꼬리표·'$ 24.1'식 띄어쓰기·글머리표) · 표 행 재구성 발췌 11(행마다 칸 값이 순서대로 원문 표에 있는지 확인. 기계가 BAD 로 본 행 3개(Meta 8-K 표 머리 2, NVIDIA 약정 표의 '—' 칸 행 1)는 원문 표를 직접 보고 맞다고 확인) |
| 일반 웹을 urllib 로 받음 | 52 | 76 | 엄격 일치 60 · 느슨 일치 13(문단 안 링크 공백, 특수 하이픈, 굽은 따옴표) · 사람이 확인한 MISS 3건(arcprize 각주 툴팁 끼어듦, JPML PDF 제목 줄바꿈, futunn 자바스크립트 렌더 → Playwright 로 일치) |
| Playwright 로 연 페이지(새 페이지를 열어 대조하고 닫음) | 27 | 33 | Google News 리다이렉트 13개는 모두 발행사 원문으로 풀어서 열었다. openai.com 은 urllib 에 403 을 내 8개를 이 방법으로 열었고, x.com 3, DCD·GeekWire 403, FT 유료벽도 여기서 열었다. 엄격 일치 26 · 느슨 일치 2 · 사람이 확인 5건: Reuters 3건은 본문 티커 링크 '(META.O)'·'(0700.HK)'·'(ORCL.N)' 만 빠졌다. EV-nvidia-010 은 발췌의 'a25%' 가 원문 'a 25%' 와 띄어쓰기만 다르다. Barchart 는 늦게 불러오는 본문이 일치했다. FT(EV-openai-010)는 본문이 유료벽이라 부제를 og:description 에서 글자 그대로 확인했다. |

**결과: 179/179 발췌가 원문에 있다.** 열지 못한 근거는 없다. 원문을 전재본(Yahoo·The Star)으로 확인했다고 적힌 근거도 발행사 원문(Barchart·Reuters)을 직접 열어 대조했다.

### 3. 인용 위치
- SEC 근거 70건은 발췌 앞쪽에서 가장 가까운 Note·Item 머리글을 뽑아 `locator` 와 나란히 봤다. 사람 눈으로는 다음 위치를 직접 확인했다.
  - Oracle 10-Q RPO 문단: (2026-02-28) Note 1, (2026-08-31) Note 1. MD&A 의 비슷한 문장('$552.6B and $130.2B')이 아니라 locator 가 적은 Note 1 문장과 일치한다.
  - Oracle 미개시 리스 $288B 문단: Note 6 리스 만기표 바로 다음.
  - NVIDIA 10-Q Note 10 약정 표와 그 아래 Supply and capacity 문단, Note 13 Revenue by Market Platform 표.
  - Microsoft 10-K Note 1 Investments 의 OpenAI 문단.
  - Meta 8-K Ex.99.1 'Segment Results' 표.
- 웹 근거는 일치한 자리의 앞뒤 문맥(문단·절 제목)으로 locator 의 문단 번호와 절 이름을 확인했다. 틀린 위치는 찾지 못했다.

### 4. 발행일
- `published_at_utc` 가 2026-10-06 을 넘는 근거는 0건이다. 마감에 가장 가까운 것은 EV-meta-009·008·029·010, EV-oracle-008(Bloomberg 2026-10-06 08:09 KST = 10-05 23:09 UTC), EV-openai-009, EV-openai-026(Epoch 디렉터리, 2026-10-05 갱신)이다.
- 발행일이 비어 있는 근거는 EV-meta-001, EV-nvidia-009, EV-oracle-003 이다. 출처 `note` 에 적힌 제출일은 각각 2026-07-30·2026-09-03·2026-09-11 이다(다음 실행 과제 8).
- thenewstack(EV-nvidia-020, 2026-08-27)은 NVIDIA 의 인수 서명(2026-09-02)보다 먼저 나온 기사다. 'reported $12.9B acquisition' 보도를 다룬 글이라 날짜는 맞다.

### 5. 줄 ↔ 발췌 대조(사람이 읽음, 135줄 전부)
재계산한 합산값(원문 표 → 줄)은 이렇다.
- meta.F9: 최근 1년 매출 $228.25B·영업이익 $86.93B·38.1%, 영업현금흐름 $130.30B − 설비투자 $89.33B = +$40.98B. 분기 잉여현금흐름 $0.78B(전년 동기 대비 −90.8%). 설비투자(금융리스 원금 포함) $31.08B·$17.01B(1.83배).
- meta.F4: 광고 비중 59,363/60,801 = 97.6%.
- microsoft.F7·F9: OpenAI $24.1B/$331.8B = 7.3%, 46.8%, +$66.99B. 분기 잉여현금흐름 $15.80B·$19.64B(전년 같은 분기 $20.30B·$25.57B, −22%·−23%), 분기 설비투자 $35.80B·$17.08B, 2025 회계연도 잉여현금흐름 $71.61B.
- microsoft.F1: Copilot 유료 시트 2,000만 → 3,000만(+50%).
- nvidia.F9: 최근 1년 매출 $302.97B·영업이익 $197.58B·65.2%, 잉여현금흐름 $127.0B.
- nvidia.F7: 영업외이익 $32.16B / 세전이익 $229.74B = 14.0%.
- nvidia.F5·F8: 하이퍼스케일 48,710/96,221 = 50.6%.
- oracle.F9: 최근 1년 매출 $71.78B·영업이익 $23.06B·32.1%. 영업현금흐름 $46.94B − 설비투자 $75.66B = −$28.72B, 선수금 $11.36B 를 빼면 −$40.08B. 완충 $46.37B. RPO ÷ 미개시 리스 = 2.31배.
- oracle.F3·F7·F8: RPO 증가 +$85.4B·+$26B, Tencent $7B/RPO $664B = 1.05%, RPO 절반/매출 = 4.63년치.
- openai.F6·F8: $852B/$40B = 21.3배, $40B/$185B = 0.22, $1.4T/$40B = 35배, $1.4T − $338B = $1.06T.

모두 줄의 숫자와 같다. 2차 탐색에서 고친 줄도 원문 값과 맞는다. 대상은 openai.F5 소송 묶음(Apple 영업비밀 2026-07-10, X Corp·SpaceXAI 의 Apple 취하 2026-09-14, 지역신문 약 400곳 2026-06-24 제소 뒤 MDL 병합), openai.F9 FutureSearch $62B·7월 $33B·Oracle 연 $60B, nvidia.F7 SemiAnalysis LTV 70~80% 이다.

Oracle 판정 칸의 부재 주장 두 개도 같은 원문에서 확인했다.
- "Stargate 지분 출자가 10-Q·10-K 에 나오지 않는다": 10-K(FY2026)와 10-Q(2026-08-31) 본문에 'Stargate' 가 0회 나온다.
- "회전여신이 10-Q 에 변동 기재 없음": 10-Q 본문에 'Revolving Credit'·'revolving credit' 이 0회 나온다.

### 6. 판정 칸 "원문을 찾지 못해" 줄
b 묶음에는 10줄이 있다. 쉽게 찾아지는 원문은 찾지 못했다. microsoft.F1 의 Copilot 월간 사용자 4.2억 명은 1차 자료에 없다. 가장 최근 1차 값은 FY26 1분기의 '1.5억 명 초과'로, retry-a 가 확인한 것과 같다. openai.F1 OpenRouter 단가·점유율, openai.F4 의 '2026년 0.1GW 미만', openai.F6 의 39배 분모, nvidia.F2 의 70~75%, nvidia.F4 의 '10개 영역' 도 이번에 찾아보지 않았거나 원문을 찾지 못했다. 이번 세션은 WebSearch 를 쓰지 않고, 연결된 URL 만 직접 열었다.

## 발견
| 등급 | 판단·칸 | 줄 앞부분 | 근거 ID | 발견 | 고칠 방향 | 점수 영향 |
| --- | --- | --- | --- | --- | --- | --- |
| needs_fix | nvidia.F7.fix52 · evidence_down[1] | "NVIDIA 는 2026년 다섯 달 동안 AI 기업 지분에 $40B 넘게 넣었고(실측), 여기에는 OpenAI $30B, Anthropic Series G(최대 $10B), xAI Series E, …" | EV-nvidia-042·043·044·045 | CNBC(2026-05-09) 원문은 "Nvidia already topping $40 billion in commitments" 다. IREN·Corning 은 "right to invest up to"·"allowing it to invest up to" 로 적혀 있다. Anthropic·xAI 는 "participated in massive funding rounds for Anthropic and Elon Musk's xAI" 뿐이다. 'Series G', '$10 billion', 'Series E' 는 기사 어디에도 없다(Playwright 로 본문 전체를 검색해 0회). | '넣었고(실측)' 를 원문대로 '약정했고' 로 고친다. IREN·Corning 은 '최대 … 투자 권리' 로 적는다. 'Anthropic Series G(최대 $10B), xAI Series E' 는 'Anthropic·xAI 펀딩 라운드 참여' 로 원문에 맞춘다. 아니면 그 금액을 받치는 원문을 새 근거로 단다. NVIDIA 의 Anthropic '최대 $10B' 약정은 2025-11-18 발표(blogs.microsoft.com, EV-microsoft-015 와 같은 출처)라서 '2026년 다섯 달' 에 넣을 수 없다는 점도 함께 확인한다. 금액을 확인하지 못하면 판정 칸에 "원문을 찾지 못해 확인하지 못했다" 로 옮긴다. | 없음(⑦ 은 판정표 입력으로 −2 가 정해지고, OpenAI $30B 등 나머지 근거는 선다) |
| needs_fix | nvidia.F7.fix52 · evidence_down[3] | "잔존가치를 보증한 담보(Grace Blackwell)의 가치를 깎는 것이 NVIDIA 자신의 신제품 Vera Rubin 이라는 자기모순도 있다." | EV-nvidia-052 | 발췌(2분기 실적 콜)가 받치는 것은 Vera Rubin 이 Grace Blackwell Ultra 대비 30배 처리량·35분의 1 토큰 비용이라는 사실뿐이다. '잔존가치를 보증한 담보가 Grace Blackwell' 이라는 전제는 이 근거에도, 같은 판단에 달린 다른 근거에도 없다. SB Energy 잔존가치 보증(EV-nvidia-047)은 데이터센터 리스(IT 부하 4.25GW)에 대한 것이다. Reuters 25% 보증(EV-nvidia-010)은 GPU 세대를 적지 않는다. | 담보 세대를 받치는 원문을 새 근거로 단다. futunn/SemiAnalysis 기사(EV-nvidia-066 의 출처)에 NVIDIA 신용 지원 사례로 Sharon AI 의 GB300 40,000개 배치 문장이 있다. 다만 이 문장이 잔존가치 보증 대상이라는 점까지 받치는지 원문에서 확인해야 한다. 받칠 원문이 없으면 '담보(Grace Blackwell)' 를 빼고 사실 부분(Vera Rubin 이 Grace Blackwell Ultra 대비 30배·35분의 1)만 남긴다. 자기모순 해석은 판정 칸에 (추론)으로 둔다. | 없음 |

## 체크리스트
| ID | 결과(pass/fail/not_applicable) | 근거 |
| --- | --- | --- |
| Q05 | pass | b 묶음에서 이해당사자 수치는 벤더 발표라고 줄 안에 밝혔다(nvidia.F2 Rubin 성능 "벤더 발표이고 독립 측정이 아니다", openai.F4 Jalapeño "이해당사자인 OpenAI 의 발표"). 이해상충 표기는 AGENTS.md 에 따라 보지 않았다. |
| Q09 | pass | 계획·서명 단계 사실은 점수 근거에서 빼고 같은 줄에 그 사실을 밝혔다. 대상은 oracle.F9 $45~50B 조달 계획, nvidia.F1·F4 Hugging Face 인수(종결 2027 상반기), openai.F4 Broadcom 배치 계획, meta.F4 기업용 AI 출범, microsoft.F9 설비투자 예상치(판정 칸)이다. 원문으로도 모두 계획·예정 표현임을 확인했다. |
| Q14 | pass | 사실 쪽만 봤다. nvidia.F2 5점의 성능 근거가 벤더 발표에 기댄다는 점은 판정 칸에 (추론)으로 적혀 있고, 출하는 10-Q 로 확인된다. 점수 판단은 규칙 일관성 영역이 본다. |
| Q23 | pass | openai.F2 는 ARC-AGI-3 표준 하네스 62.7% 만 쓰고 Provider Adapter 99.9%·96% 는 뺀다(arcprize 원문으로 하네스 구분을 확인했다). FrontierMath 는 하네스 미표기라 비교에서 뺐다. meta.F2 Tau3-Bench 도 같은 이유로 뺐다. 다만 같은 줄의 'ExploitBench 100%' 는 OpenAI 자체 발표다(다음 실행 과제 14). |

## 다음 실행 과제
1. (low) openai.F4 evidence_up[1]: EV-openai-024 발췌는 범위 문장('1.5 to 1.9 times … than the comparison systems')뿐이라 줄의 'GB300 대비 DeepSeek R1 1.7배·Kimi K2.5 1.5배' 가 발췌에 없다. 같은 페이지 부록에 'Higher peak mixed TPS / kW ≈1.7× 19,641 vs. 11,781 … GB300 1,400 W' 와 Kimi 'approximately 1.5 times higher peak performance per watt' 가 있으니 발췌를 바꾼다.
2. (low) nvidia.F5 evidence_up[0]: 연합사별 역할(멀티모달·에이전트·코딩 평가 데이터)은 같은 보도자료의 'Expected contributions span multimodal capabilities from Black Forest Labs, … evaluation datasets from Cursor, … AI agents … from LangChain' 문장에 있다. EV-nvidia-033 발췌에 이 문장을 더한다.
3. (low) microsoft.F4 evidence_up[0]: "Azure 매출을 처음으로 달러로 공시" 가 EV-microsoft-012(8-K 2026-09-02)에 없다. 'first time' 은 0회다. Microsoft 는 2025-07 실적에서 Azure 연매출 $75B 초과를 이미 밝혔다. '분기별 달러 값을 처음 공시' 로 좁히고 근거를 달거나 '처음으로' 를 뺀다.
4. (low) openai.F8 evidence_down[1]: 나머지 약 $1.06T 의 'NVIDIA·AMD' 발표분을 받치는 근거가 없다(표지는 Oracle·AWS·Broadcom 만 받친다). OpenAI–NVIDIA(2025-09), OpenAI–AMD(2025-10) 발표를 근거로 단다.
5. (low) openai.F5.impl48 evidence_down[0]: FT 는 본문이 유료벽이다. 제목과 부제('Cyber security incidents … vulnerable to wave of lawsuits')만 확인되고 줄의 '여러 관할에서' 는 확인되지 않는다. 그 구절을 뺀다.
6. (low) nvidia.F5 evidence_up[1]: "연합사는 자체 칩을 개발할 자본이 없어 NVIDIA GPU 를 빌려 쓰므로 …" 는 발췌(공동개발 문장)가 받치지 않는 추론이다. (추론)을 붙이거나 그 부분을 판정 칸으로 옮긴다.
7. (low) openai.F7 evidence_up[0]: 뒷절 "공급자와 투자자 사이를 도는 자금은 매출이 아니라 비용 쪽으로 나간다" 는 발췌가 받치지 않는다. (추론)을 붙이거나 판정 칸으로 옮긴다.
8. (low) 근거 EV-meta-001·EV-nvidia-009·EV-oracle-003 과 그 출처(SRC-EDGAR-000162828026050705·…000104581026000078·…000119312526389274)의 `published_at_utc` 가 비어 있다. 제출일(2026-07-30·2026-09-03·2026-09-11)로 채운다.
9. (low) Google News 리다이렉트 URL 을 쓴 출처가 b 묶음에 13개 있다. 이번에 모두 발행사 원문으로 풀어서 열었다(예: EV-oracle-005 → reuters.com/world/china/chinas-tencent-leases-100000-chips-oracle-…-2026-10-01/). 출처에 발행사 URL 을 적고, '전재본으로 확인' locator(EV-meta-008·009, EV-nvidia-010)는 발행사 원문 기준으로 바꾼다. EV-nvidia-010 발췌의 'a25%' 는 원문대로 'a 25%' 로 고친다.
10. (low) openai.F6 판정 칸의 "2026년 GAAP 손실이 약 $60B" 를 openai.F9 에서 원문(FutureSearch)에 맞춰 고친 $62B 와 맞춘다. openai.F6 방향 칸 2줄과 표지(EV-openai-034·049)는 draft.md 에 실리지 않는다(비상장 ⑥ 판단은 계산에 쓰이지 않는 항목). 의도한 것인지 출력 영역에서 확인한다.
11. (low) 계속 바뀌는 페이지에서 가져온 근거가 있다. EV-openai-026(Epoch 디렉터리, 2026-10-05 갱신)과 EV-microsoft-009(Arena 순위표, 2026-10-02)다. 2026-10-07 에 열었을 때 발췌는 그대로였지만 기준일 시점 사본이 없다. 다음 실행부터 수집 때 `sha256` 이나 사본을 남긴다.
12. (low) meta.F3 evidence_up[2]: '(The Information 단독, 2026-09-30)' 의 날짜가 근거 기사(TNW 2026-10-02)에 없다. 날짜를 빼거나 원 보도를 단다.
13. (low) nvidia.F2 evidence_up[0]: '2026-03-16 GTC 재공개' 와 'R100' 이 표지 근거(2026-01-05 보도자료·기술 블로그)에 없다.
14. (low, 규칙 일관성 영역과 함께) openai.F2 evidence_up[0] 은 하네스 미표기·자사 발표 점수(FrontierMath·99.9%)를 빼면서, 같은 OpenAI 자체 발표인 'ExploitBench 100%' 는 성능 도약 근거로 둔다. 같은 잣대로 둘지 다시 본다.

## 이전 리뷰 기록
이 파일은 round 8 에서 b 묶음 전용으로 새로 만들었다. round 7 까지의 사실·출처 리뷰는 `review-parts/fact-sources.md` 에 있다. 조율자가 a·b·c 묶음을 그 파일로 합친다.
