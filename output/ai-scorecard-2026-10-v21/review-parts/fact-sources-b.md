---
reviewer_agent: fact-checker
session: fs-b-v21-20261013-r1
reviewed_at: 2026-10-13
round: 1
---
# fact-sources-b — 사실·출처 (oracle, palantir, anthropic, openai, alibaba, tesla, spacex-xai)
검토자: Claude Sonnet 5.5 (claude-sonnet-5-5) · fact-checker · 사실·출처 독립 세션 b(이 실행을 만든 세션도 판단 세션도 아님) · 2026-10-13 · 1차
결과: needs_fix
요약: 맡은 일곱 회사의 정성 판단 49건(①②③④⑤⑦⑧, 모두 `status: new`)의 올릴·내릴 근거 513줄과, 표지·층별 보유표·AI 수익화 근거가 가리키는 근거 448건을 전수로 봤다. 근거는 모두 `confirmed` 이고 출처 등록·발췌·기준일이 맞으며 발췌는 원문에서 찾았다(SEC 183건은 캐시 원문, 웹 265건은 원문·브라우저·PDF 텍스트, 글자 그대로 못 맞춘 EV-palantir-028 과 라이브 순위 페이지는 아래에 적었다). 이번에 새로 들어온 관측 7건(Alibaba 법인세·영업현금흐름·설비투자, SpaceX 영업현금흐름·설비투자, Tesla 지분 평가이익, 시장 토큰 가격 지수)은 값·기간·환율·성분이 원문과 맞는다. 점수를 바꾸는 발견은 셋이고 모두 ⑦ 세로축(내 돈이 돌아옴)이다. (1) Palantir 는 10-K·10-Q 위험 요인이 투자 대상과 맺은 'Strategic Commercial Contracts'(누적 매출 $325M)를 공시하는데 판정은 '확정 근거에 없어 돌아오지 않음'이다(⑦ 0 → −1, 조정 5 → 4, 10위 → 11위). (2) Alibaba 는 20-F 가 투자 대상과의 클라우드 계약 매출 RMB9,415M 을 공시하는데 판정은 '확인하지 못했다(미확인)'이다(⑦ 0 → −1, 조정 7 → 6, 8위 유지). (3) OpenAI(조건부)는 'Startup Fund 구조 미확인'으로 푼 자리에 열리는 보도(Cursor 시드 주도, YC 토큰-지분 교환)가 있다('돌아옴'으로 읽으면 ⑦ −2 → −3, 조정 1.5 → 0.5, 공동 12위 → 13위). 이 밖에 미확인으로 뺀 보도가 열리는데 판단이 쓰지 않은 두 건(Palantir ①, SpaceX ①)과 점수에 닿지 않는 지적이 있다.
검토 기준: results_hash `55d4a0cc8452c05d…`, draft_hash `21a0850e0a1f9bb5…`(review.md frontmatter 값과 같다. `engine.compute(engine.load_context(slug))` 가 같은 results_hash 를 다시 냈고 draft.md 바이트 sha256 이 같음을 확인했다).

## RESULT

needs_fix — 맡은 일곱 회사의 사실 가운데 출처까지 거슬러 안 닿는 것은 없지만, 판정 칸이 '확인하지 못했다'고 적은 사실이 같은 실행의 확정 근거 문서(Palantir 10-K·10-Q, Alibaba 20-F)나 열리는 원문에 있는 경우가 둘 있고 하나는 판독이 갈린다. 세 건 모두 규칙 v2.1 ⑦ 매트릭스(큼·돌아옴 −3 복원)와 작음·돌아옴 −1 칸에서 점수를 가른다. 나머지 지적은 점수·순위·체크리스트 판정에 닿지 않는다.

## 확인한 것

### 범위와 기계 점검
- 판단 49건(일곱 회사 × ①②③④⑤⑦⑧), 올릴·내릴 근거 513줄(회사별 oracle 65, palantir 62, anthropic 93, openai 94, alibaba 59, tesla 65, spacex-xai 75)을 봤다. 모든 줄 끝에 `[EV-…]` 가 있다.
- 줄 표지·`evidence_ids`·④ `layer_evidence`·① `ai_separate_billing_evidence` 가 가리키는 근거는 중복을 빼고 448건이다(맡은 회사 근거 427건, 다른 회사 근거 21건). 448건 모두 evidence.json 에 있고 `confirmed` 이며 reviewer·reviewed_at·locator 를 갖췄다. 발췌는 제목과 다르다. `source_id` 는 모두 sources.json 에 있고 URL 이 있다. 판단의 `source_ids`·`evidence_ids` 는 모두 sources·evidence 에 있고, 후보(candidate) 근거를 인용한 새 판단은 없다.
- 다른 회사 근거 21건(alphabet 7·amazon 7·nvidia 4·microsoft 2·apple 1)은 맡은 회사의 사실을 받치는 데 쓰였다(예: Amazon 10-Q 의 OpenAI·Anthropic 약정, Alphabet 의 Anthropic 투자). 다른 회사 점수를 근거로 인용한 줄은 없다.
- `published_at_utc` 는 447건이 정보 마감(2026-10-12) 이하이고 EV-tesla-008 만 비어 있다. 관측 `as_of`·`observed_at` 은 모두 2026-10-12 이하이고, 상장사 다섯(alibaba·oracle·palantir·spacex-xai·tesla)의 가격 기준일은 2026-10-09 로 실행 설정(`price_as_of`)과 같다. 맡은 회사 관측의 출처 ID 는 모두 sources 에 있다.
- ⑥·⑨ 판단 9건(carried 6, new 3: alibaba·spacex-xai `F9.obsreg25`, oracle `F9`)이 인용한 근거 40건도 모두 `confirmed` 다. 이 가운데 SEC 문서에서 따온 34건의 발췌는 같은 방법으로 대조했고(표 형식 3건 EV-palantir-014·016, EV-spacex-xai-055 는 값이 원문에 있다) 웹 6건은 범위 밖이라 대조하지 않았다(⑥·⑨ 계산은 재무 계산 영역).
- 트리거: 맡은 회사 45건 모두 `watching`, `evidence_ids`·`source_ids` 가 모두 등록돼 있고 확정 근거만 인용한다. 이전 트리거 42건의 carry 는 모두 '계속 관찰'이고 사유는 '이전 실행과 기준일·정보 마감(2026-10-12)이 같아 새 창이 없다'이다. 맡은 회사 트리거의 기한은 가장 이른 것이 2026-11-15 라 기한이 지난 `watching` 은 없다. 발동 트리거 재검토 표는 이 실행에 없다.

### 원문 받기
- SEC: 근거·관측이 가리키는 SEC 주소 41개는 모두 `data/_sec/docs/index.json` 캐시에서 읽었다. 새 SEC 요청은 보내지 않았고 `SEC_UA` 와 `.env` 는 읽지 않았다.
- 웹: 비SEC 226개 주소를 식별용 일반 요청 머리글(`fact-check-review/0.1`)로 받았다. 181개가 열렸고 45개(403 36, 401 5, 시간 초과 3, 429 1)는 열리지 않았다. 열리지 않은 주소는 머리글을 바꿔 우회하지 않고 Playwright 브라우저로 열었다. 일부 페이지는 본문을 브라우저 텍스트와 페이지 `og:description` 으로 대조했다.
- 막힌 주소 가운데 Reuters 두 건은 열리지 않았다. EV-anthropic-046 은 같은 Reuters 기사를 전재한 The Star(EV-anthropic-002 의 문서)에 발췌가 글자 그대로 있다('The 2-1 decision by the US Court of Appeals…'). EV-anthropic-045 는 열지 못했고 판단 줄이 인용하지 않는다(`evidence_ids` 에만 있다).
- FT 네 건: 부제 세 건(EV-openai-010, EV-palantir-004·011)은 페이지 `og:description` 에서 발췌와 글자 그대로 같은 문장을 찾았다. EV-palantir-028 의 본문 인용(MHCLG 대변인)은 구독 장벽에 막혀 다시 확인하지 못했다.
- PDF 두 건: EV-openai-044(JPML 이송 결정)는 PDF 텍스트에서 사건명·뉴스 사건·중앙집중 문장을 찾았다. EV-tesla-048(NHTSA ODI Resume)은 글자 매핑표(ToUnicode)로 텍스트를 복원해 'EA26002', 'Date Opened: 03/18/2026', 'Population: 3,203,754 (Estimated)' 를 확인했다.
- Google 뉴스 중계 주소 하나(SpaceXAI 요금 보도)를 `scorecard_cli.py resolve-urls --url` 로 풀었다(발견 5).
- 대조에 쓴 임시 파일과 도우미 스크립트는 스크래치패드 `rv-fact-b/` 아래에만 있다. 실행 폴더에는 이 파일 하나만 썼고 `scorecard_cli.py` 의 쓰는 명령은 부르지 않았다.

### 발췌·위치 대조 결과(448건)
- SEC 183건: 정규화 문자열이 그대로 맞은 것 137건, 공백·구두점 차이만 있는 것 40건, 표 형식 차이 6건이다. 표 형식 5건(EV-palantir-012·015, EV-spacex-xai-011·024·050)은 표의 값을 원문 표에서 모두 찾았다. 나머지 1건 EV-tesla-008 은 발견 7 이다.
- 웹 265건: 그대로 164건, 공백·구두점 차이 39건, 형식 차이 9건, 막힌 주소 51건, PDF 2건이다. 막힌 주소 51건 가운데 브라우저·PDF·og:description·전재본으로 대조한 것이 49건이다. EV-anthropic-045 와 EV-palantir-028 은 위에 적은 대로 대조하지 못했다.
- 줄이 인용하는 근거 가운데 글자 그대로 대조하지 못한 것은 EV-palantir-028 과 라이브 순위 페이지 네 건(EV-anthropic-049·051·052·057)이다. EV-anthropic-049·052 의 값(58/53/53/53/52/48/46, 68/66/64/63/62/62/56/54)은 열린 페이지와 같고 라벨과 값이 따로 실려 짝지어 옮겼다는 단서가 근거에 있다. EV-anthropic-051 의 1위 행(Claude Opus 5.5 1866)은 같고 다른 행의 Elo 는 2026-10-08 뒤 다시 계산돼 조금 다르다(13위 Muse Spark 1684 → 1681, 14위 Qwen3.8 Max 1671 → 1667). 순위 순서는 같다. EV-anthropic-057 은 열린 페이지가 2026-10-05 주 자료로 갱신돼 9월 28일 주 스냅숏(Anthropic 2.5%·7위)을 다시 볼 수 없다. 이 줄은 방증이라 판정에 닿지 않는다.
- `evidence_ids` 에만 있고 줄이 인용하지 않는 EV-amazon-051(arena.ai 순위), EV-anthropic-055(가격 문서 표), EV-openai-051(openai.com 요금 페이지 탭)도 같은 이유로 글자 그대로 대조하지 못했다.
- 인용 위치: 쪽 번호가 적힌 SEC locator 78건 가운데 41건은 문서 쪽 머리글('N Table of Contents')로 쪽이 맞음을 확인했고 1건(EV-alibaba-074)은 어긋난다(발견 6). 나머지 36건은 표·전문 형식이거나 쪽 머리글이 없는 문서(6-K·8-K 보도자료, Tesla 10-K)라 기계 대조가 안 돼 소제목·문장 위치만 봤다.

### 이번 실행에서 새로 들어온 관측(원문 값·기간·환율·성분 대조)
- alibaba `income_tax_ttm` 2026-06-30: 20-F 연결손익계산서 FY2026 법인세 RMB30,045M(열 순서 FY2024 22,529·FY2025 35,445·FY2026 30,045·US$ 4,356), 2025년 4~6월 RMB8,865M(2025 6-K 본문), 2026년 4~6월 RMB12,798M(2026 6-K 본문). 30,045 − 8,865 + 12,798 = 33,978, ÷ 6.8980 = $4,925.78M 으로 관측값 4,925,775,587 과 맞는다. 세전이익 교차식 순이익 70,189 + 법인세 33,978 − 지분법 2,706 = 101,461 도 맞는다.
- alibaba `ocf_ttm`: 20-F 영업현금흐름 FY2026 RMB76,213M, 6-K 분기 RMB20,672M·RMB22,945M. 76,213 − 20,672 + 22,945 = 78,486, ÷ 6.8980 = $11,378.08M. 네 분기 합 10,099 + 36,032 + 9,410 + 22,945 = 78,486 도 닫힌다.
- alibaba `capex_ttm`: 20-F 본문과 현금흐름표 'Land use rights, property and equipment (126,063)', 6-K 본문 설비투자 RMB38,676M(2025년 4~6월)·RMB67,678M(2026년 4~6월). 126,063 − 38,676 + 67,678 = 155,065, ÷ 6.8980 = $22,479.7M. 20-F 현금흐름표는 같은 칸 아래 무형자산 취득 874 를 따로 적고 관측은 그것을 넣지 않았다.
- spacex-xai `ocf_ttm`: 10-Q 현금흐름표 반기 $3,466M·$351M, S-1/A 2025년 연간 $6,785M. 3,466 + 6,785 − 351 = 9,900. `capex_ttm`: 10-Q 반기 $28,476M·$6,965M, S-1/A 2025년 연간 $20,737M. 28,476 + 20,737 − 6,965 = 42,248.
- tesla `equity_investment_gains_ttm`: 2026년 상반기 영업활동 현금흐름표 'SpaceX equity investment unrealized gain (1,005)' 와 투자활동 'Purchase of SpaceX equity investment (2,002)'(Q1 10-Q 현금흐름표에도 2,002). Q1 10-Q 공정가치표의 SpaceX 지분 2,002 는 취득원가와 같아 1분기 이익이 없다는 설명이 맞고, 2분기 값이 1,005 다.
- `_market` `token_price_index` 2026-10-10: Silicon Data 페이지에 'As of Oct 10, 2026 · 0.97 USD / M tokens · 1.7% (7D)' 가 있다. 같은 페이지 차트 설명문의 'frontier segment' 표기를 관측 설명이 스스로 밝히고 broad 로 적은 근거도 페이지의 'broad-market' 문장과 맞다.

### 회사별 줄 사실과 계산
- 판정 칸 숫자를 기계로 근거 발췌·관측과 맞춰 봤다. 발췌나 관측에 없는 숫자는 모두 계산값이었고 다시 계산해 맞았다.
- **oracle**: 최근 1년 매출 67,357 − 14,926 + 19,345 = 71,776. AI 무관 몫 (71,776 − 22,142) ÷ 71,776 = 69.15%(OCI 최근 1년 18,101 − 3,347 + 7,388 = 22,142). (288 + 34.15) ÷ 71.776 = 4.49배. 2027 회계연도 잔여·2028 회계연도 지급 5,449 + 6,176 = 11,625(16%). 소프트웨어 라이선스 655 + 지원 4,895 = 5,550. 60 ÷ 71.776 = 83.6%. 10-K 'No single customer accounted for 10% or more of our total revenues in fiscal 2026, 2025 or 2024' 를 찾았다. 10-K·10-Q 에 'OpenAI'·'Stargate' 문자열이 없다는 서술도 맞다.
- **palantir**: 최근 1년 매출 4,475,446 + 3,568,047 − 1,887,552 = 6,155,941. 정부 3,210,783(2,402,287 + 1,848,442 − 1,039,946), 상업 2,945,158. 정부 몫 52.2%, 미국 정부 809 ÷ 1,935.46 = 41.8%. 약정 5.6 ÷ 6.156 = 0.91배, 연 최소 $268M~$979M 은 매출의 4~16%. RPO $4.9B 중 43%, '12개월 미만 통지 해지' 문장이 10-Q 에 있다.
- **anthropic**: ARR $9B → $30B(96일) 월 복리 46.5%, $30B → $65B(116일) 22.5%, 2월 12일을 끼우면 36.7%·54.9%. 100 + 30 + 19 + 11.6 + 44.6 + 21 = 226.2, ÷ 65 = 3.48배, Nscale 을 빼면 2.79배. OpenRouter 관측 점유율 0.1169 → 0.0389, 평균 단가 1.2393 → 1.0178, OpenAI 0.3604 가 관측과 같다. 각 약정(Amazon 10-Q '$100.0 billion over 10.0 years', Azure $30B, TeraWulf 약 $19B, Akamai 약 $11.6B, Nscale 최대 약 $44.6B, Broadcom $10B + $11B)의 문장이 발췌에 있다.
- **openai**: 50 ÷ 900 = 5.6%. ③ (50/25)^(1/5.03) − 1 = 14.8%, (50/24)^(1/6.03) − 1 = 13.0%. ⑧ 138 + 250 + 18.4 + 219.5 = 625.9, ÷ 50 = 12.5배(CoreWeave 를 빼면 12.15배, Oracle $300B 를 더하면 18.5배, ÷ 70 이면 8.9배). SB Energy 수주잔고 $439B 가운데 PORTS-Pike 가 '상당한 대부분'이라는 문장(EV-openai-113)이 있고 절반 하한은 판정이 밝힌 가정이다. 광고 $1B ÷ $40B = 2.5%, ÷ $50B = 2.0%. OpenAI 가 발표한 ARC-AGI-3 99.9%(openai.com GPT-6 Astra 페이지 'saturates ARC-AGI-3 with a 99.9% score')가 판정 칸의 숫자와 맞는다.
- **alibaba**: 매출 유형별 AI 무관 (1,023,670 − 112,077 − 36,427) ÷ 1,023,670 = 85.49%, 6-K 세그먼트 (268,953 − 51,775) ÷ 268,953 = 80.76%. AI 관련 제품 12,376 ÷ 8,971 = +38%, ÷ 48,437 = 25.6%. ⑦ 클라우드 158,132 ÷ 1,023,670 = 15.4%. ⑧ 최근 1년 매출 1,023,670 − 247,652 + 268,953 = 1,044,971, 약정 54,136 + 200,062 = 254,198(0.24배), 1년 안 몫 110,925(10.6%), 주요 VIE 119,561(11.7%)·연결 VIE 156,369(15.3%), Ant Group 클라우드 매출 19,134(1.9%). 20-F 에 최대 고객·10% 이상 고객 문장이 없다는 `not_disclosed` 표기는 전문 검색으로 맞다(주석 (f) 는 금융상품 신용위험만 적는다).
- **tesla**: FSD 1.28 ÷ 1.10 = 16.4%, 1.48 ÷ 1.28 = 15.6%, 누적 인도 9.7M 으로 1.48 ÷ 9.7 = 15.3%. 최근 1년 매출 28,095 + 24,901 + 22,387 + 28,236 = 103,619 와 줄별 합(72,588 + 1,485 + 1,575 + 12,799 + 15,172). BYD 762,478 − 486,532 = 275,946(56.72%). SpaceX Megapack 405 × 2 ÷ 103.6B = 0.78%, 318 × 4 → 1.2%, SpaceX 최근 1년 영업손실 2,589 + 2,086 − 943 = 3,732. 중국 매출 20,962 ÷ 94,827 = 22.1%, 8,859 ÷ 50,623 = 17.5%. 설치 능력 합 2,375k 에서 상하이 950k 는 40%. 10-K·10-Q 는 매출채권 기준 10% 이상 거래 상대만 적고 매출 기준 문장이 없다(`not_disclosed` 맞음).
- **spacex-xai**: 최근 1년 매출 18,674 + 12,508 − 8,138 = 23,044. AI 무관 (4,056 + 13,873 + 1,684) ÷ 23,044 = 85.1%(Connectivity 11,387 + 7,548 − 5,062). 1.25B × 12 = $15B, ÷ 23.044 = 65.1%, Reflection 1.8B 을 더하면 72.9%, 3.75 ÷ 23.044 = 16.3%. 해지할 수 없는 무조건 약정 27,955(2,728 + 22,244 + 2,172 + 809 + 2) + 미개시 리스 1,627 = 29,582, ÷ 23,044 = 1.28배, 18개월 몫 24,972 = 1.08배. 10-Q 고객 A 17.9%·고객 B 19.5%, 2025년 미국 발생 매출 69.4%.

### 미확인으로 뺀 보도·사실 점검
- 판정 칸의 '미확인·확인하지 못했다·열지 못했다' 문장 가운데 특정 보도·서한·녹취를 가리킨 것을 모두 모아 원문을 직접 열어 봤다. 열리는데 판단이 쓰지 않은 것이 다섯이다(발견 1~5). 나머지는 원문이 닫혀 있거나(Anthropic·OpenAI 의 유출 초안 인용 보도, 유료 Bloomberg·WSJ·The Information 원문) 수치가 공시에 없다는 서술이고, 같은 문서에서 다시 찾아 맞았다.
- 부재 주장: Anthropic·OpenAI 가 EDGAR 에 공개 제출본이 없다는 것은 캐시한 EDGAR 전문 검색(2026-10-12)에서 'Anthropic PBC' 결과가 Nscale·SpaceX·Amazon 등 다른 회사 제출본뿐이고 'OpenAI Group PBC' 는 SB Energy·Praetorian 제출본뿐이라는 것으로 맞다. Palantir 10% 이상 고객 없음(10-Q), Oracle 10% 이상 고객 없음(10-K Note 1), Tesla 매출채권 10% 이상 없음(10-K Note 2)도 원문과 맞다.
- 미확인과 확인된 미공시의 구분: `not_disclosed`(Oracle·Alibaba·Tesla 고객 축)는 같은 원문에서 그 문장이 없음을 찾았고, `not_found`(Anthropic·OpenAI 고객 축)는 우리가 못 찾은 쪽으로 적혀 있다. 섞인 자리는 찾지 못했다.

### 기준 시점·귀속·초안
- 기준일 뒤 사실을 점수에 넣은 줄은 없다(Cursor 차단 2026-11-12, Tesla 3분기 Update 10-21, Jalapeño·Optimus·Terafab·궤도 컴퓨트는 계획으로 표시돼 점수에 안 들어갔다).
- 회사 귀속: SpaceX 가 Anthropic 에 컴퓨트를 파는 계약은 SpaceX ⑦·⑧ 에서는 고객 집중으로, Anthropic ⑧ 에서는 해지 가능 계약이라 약정 축에서 빠졌다. 같은 계약을 관계에 따라 다른 축으로 읽는다고 판정 칸에 적었고 계약 금액은 두 쪽이 같다.
- `company_summaries` 일곱 건의 점수·순위(Oracle 7.5·7위, Alibaba 7·8위, Tesla 5.5·9위, Palantir 5·10위, SpaceX 4.5·11위, Anthropic·OpenAI 1.5·공동 12위)는 results.json `ranking` 과 같다.
- draft.md 에 매수·매도 권유, 목표 주가, 수익 보장, 조급함을 부추기는 표현은 없고 끝에 투자 자문이 아니라는 고지가 있다. 'price target'·'Outperformed' 는 출처 목록에 실린 기사 제목이다.

## FINDINGS

### 점수·순위를 바꾸는 발견(needs_fix)

1. **palantir.F7 — 세로축 '돌아오지 않음'이 Palantir 자신의 공시와 어긋난다(점수 변경).**
   - 위치: judgments.json `palantir.F7` 입력 `own_money_returns: no` 와 판정 칸 마지막 줄 'Palantir 가 고객에 투자·대출·보증한 돈이 매출로 돌아오는 계약·공시는 이 실행의 확정 근거에 없어 세로축은 돌아오지 않음이다.'
   - 원문: Palantir 10-Q(2026-06-30) Part II Item 1A 위험 요인(이 판단이 이미 EV-palantir-013·019·020 등으로 인용하는 같은 문서, https://www.sec.gov/Archives/edgar/data/1321655/000132165526000041/pltr-20260630.htm). 'we have made, and may continue to make, strategic investments pursuant to certain approved agreements (“Investment Agreements”) to purchase, or commit to purchase, shares of various entities, including special purpose acquisition companies and/or other privately-held or publicly-traded entities (each, an “Investee”…)' 와 'in connection with approving and signing the Investment Agreements, we and each Investee or an associated entity entered into a commercial contract for access to our products and services (collectively, the “Strategic Commercial Contracts”). The total value of Strategic Commercial Contracts … was $326 million … the cumulative amount of revenue recognized from Strategic Commercial Contracts was $325 million, of which $3 million was recognized by us during the six months ended June 30, 2026.' 같은 문단이 10-K(2025) Item 1A 에도 있다(total value $326.1 million, 2025-12-31). 'some of our early-stage Investee customers filed for bankruptcy or terminated their contracts with us' 도 적혀 있다.
   - 왜 점수에 닿나: 판정 칸이 적은 세로축 정의는 '내가 투자·대출·보증으로 고객에 넣은 돈이 있고 그 고객이 내게 대금을 내는 구조가 실행된 계약이나 공시로 확인될 때 돌아옴'이다. 투자와 투자 대상의 상업 계약이 한 묶음으로 체결되고 그 계약에서 누적 매출 $325M 이 인식됐다는 공시는 이 문장을 그대로 채운다. Tesla ⑦(SpaceX 에 투자한 $2.00B, SpaceX 가 Megapack 대금을 냄)을 '예'로 읽은 잣대와 같다. 이 판정은 공시에 있는 사실을 '확정 근거에 없다'는 이유로 감점 완화 쪽(돌아오지 않음)으로 풀었다. 규칙 2.1 은 감점을 덜어 주는 장치에 가점과 같은 엄격함을 요구한다.
   - 고칠 것: `own_money_returns: yes` 로 바꾸고 판정 칸 마지막 줄을 위 공시로 다시 쓴다. 올릴·내릴 근거 칸에 이 위험 요인 문단을 근거로 등록·확정해 표지를 단다. 현재 확정 근거 가운데 이 문단을 담은 것은 없다. 'Strategic Commercial Contracts' 규모(누적 $325M, 2026년 상반기 $3M)는 작음·돌아옴 칸(−1)이라는 판정과 충돌하지 않는다.
   - 바뀌는 점수(엔진 모의, 이 한 칸만): Palantir ⑦ 0 → −1, 함정 −7 → −8, 조정 5 → 4, 순위 10위 → 11위(SpaceX 가 10위). 다른 기업은 그대로다.

2. **alibaba.F7 — 투자 대상 가운데 클라우드 고객이 '확인하지 못했다'고 적었지만 20-F 가 공시한다(점수 변경).**
   - 위치: `alibaba.F7` 입력 `own_money_returns: no` 와 판정 칸 '알리바바의 지분 투자 대상 가운데 Alibaba Cloud 고객이 있는지는 이 실행에서 확인하지 못했다(미확인).' 및 '세로축은 돌아오지 않음이다.'
   - 원문: Alibaba 20-F(FY2026) Item 7.B Related Party Transactions(p.173, https://www.sec.gov/Archives/edgar/data/1577552/000119312526231755/baba-20260331.htm). 'We have also entered into commercial arrangements with certain of our investees related to cloud services. In fiscal years 2024, 2025 and 2026, we recognized revenue of RMB984 million, RMB4,507 million and RMB9,415 million (US$1,365 million), respectively, for these cloud services. In fiscal year 2026, this revenue accounted for 0.9% of our revenue.' 이 문장은 확정 근거 EV-alibaba-089 의 발췌에 이미 들어 있고(제목도 '투자 회사 클라우드 매출 RMB9,415M') 같은 판단의 ⑧ 올릴 근거 줄이 EV-alibaba-089 를 인용한다. ⑦ 은 이 근거를 읽지 않았다. 20-F 는 같은 절에서 물류 서비스도 투자 대상과의 상업 계약으로 적는다(FY2026 RMB3,301M).
   - 왜 점수에 닿나: 알리바바가 지분을 투자한 회사들이 알리바바 클라우드에 대금을 내는 구조가 공시로 확인된다. 매출 몫이 0.9% 로 작아 가로축 작음에는 변화가 없고, 세로축만 '돌아옴'이 된다(작음·돌아옴 −1). Ant Group(33% 지분, SAPA 로 받은 지분) 클라우드 매출 RMB19,134M 은 받은 지분이라 이 판단의 근거로 쓰지 않았다. 판정은 이 자리를 미확인으로 두고 점수를 가볍게 하는 쪽(돌아오지 않음)으로 풀었다.
   - 고칠 것: `own_money_returns: yes`, 판정 칸을 EV-alibaba-089 의 투자 대상 문장으로 다시 쓰고 올릴·내릴 근거 칸에 표지를 단다. 'investees' 가 알리바바가 현금을 넣은 지분인지(Ant Group 같은 받은 지분 제외) 한 번 더 가르려면 20-F 지분투자 주석에서 투자 대상 명단을 본다.
   - 바뀌는 점수(엔진 모의): Alibaba ⑦ 0 → −1, 함정 −10 → −11, 조정 7 → 6, 순위는 8위 그대로(Tesla 5.5 가 9위). 다른 기업 불변.

3. **openai.F7 — 'Startup Fund 구조는 원문을 찾지 못해 미확인'으로 푼 자리에 열리는 원문이 있다(조건부, 판독에 따라 점수 변경).**
   - 위치: `openai.F7` 입력 `own_money_returns: no` 와 판정 칸 'OpenAI Startup Fund 가 API 고객에 투자하는 구조는 원문을 찾지 못해 미확인이다.'
   - 열리는 원문 둘. (가) TechCrunch 2023-10-11 'Anysphere raises $8M from OpenAI to build an AI-powered IDE': Cursor(Anysphere)의 시드를 OpenAI Startup Fund 가 이끌었다('raised $8 million in seed funding led by OpenAI’s Startup Fund', https://techcrunch.com/2023/10/11/anysphere-raises-8m-from-openai-to-build-an-ai-powered-ide, 브라우저로 열어 확인). Cursor 는 이 판단이 '기준일에 OpenAI 의 고객'이라 적은 조달 의존 고객이고(EV-spacex-xai-049: OpenAI 모델이 Cursor 이용 트래픽의 약 5%) 이전 실행 사실·출처 b 리뷰가 다음 실행 과제 3 으로 이미 적었다. (나) The Daily Star 2026-05-24(TechCrunch·The Verge·The Information 인용, https://www.thedailystar.net/news/tech-startup/news/altman-offers-2-million-ai-credits-y-combinator-startups-equity-4183461)와 KuCoin 2026-05-21: Altman 이 YC 배치 스타트업(약 169곳)마다 OpenAI API 토큰 $2M 을 미래 지분(uncapped SAFE)과 바꾸겠다고 제안했고 YC 의 Friedman 이 구조를 확인했다.
   - 왜 점수에 닿나: 규칙 v2.1 은 큼·돌아옴을 −3 으로 복원했다(이전 규칙은 큼·돌아옴과 큼·돌아오지 않음이 같은 칸이라 점수를 안 갈랐다). OpenAI ⑦ 은 큼·돌아오지 않음 −2 라 세로축이 이제 −1 을 가른다. 판정은 미확인을 감점 완화 쪽(돌아오지 않음)으로 풀었다.
   - 판독이 갈리는 점: (가)는 OpenAI Startup Fund 가 OpenAI 자신의 돈인지(출자자 구성)를 한 번 더 확인해야 하고, (나)는 현금이 아니라 토큰 크레딧이며 SAFE 체결·소진이 공시나 1차 발표로 확인되지 않는다. Anthropic ⑦ 은 스타트업 크레딧을 현금이 아니라 할인으로 읽어 세로축에 넣지 않았다. Anthropic Anthology Fund 의 자본은 Menlo Ventures 라 같은 구조가 아니다(검색 결과). 둘 중 어느 쪽으로 읽든 판정 칸이 이 구조들을 다루고 이유를 적어야 한다.
   - 고칠 것: 판정 칸의 '미확인'을 위 두 사실과 읽기(돌아옴으로 읽으면 근거 표지와 `yes`, 아니면 '내 돈이 아님·체결 미확인' 같은 이유)로 다시 쓴다. 어느 쪽이든 근거 등록과 확정이 필요하다.
   - 바뀌는 점수(엔진 모의, 돌아옴으로 읽을 때): OpenAI ⑦ −2 → −3, 함정 −11 → −12, 조정 1.5 → 0.5, 순위 공동 12위 → 13위(Anthropic 이 12위). 돌아오지 않음을 유지하면 점수는 그대로다.
   - 세 건을 모두 적용하면(엔진 모의) Palantir 4(11위), Alibaba 6(8위), OpenAI 0.5(13위)이고 SpaceX 는 4.5 로 10위다.

### 점수에 닿지 않는 발견

4. **fail(점수 불변) — palantir.F1 판정 칸.** '실적 통화 녹취와 CEO 서한은 열지 못해 회사가 그 자리에서 AIP 몫을 밝혔는지는 미확인이다.' 라고 적었는데 둘 다 열린다. 2026 Q2 통화 전사본(https://transcripts.platformaeronaut.com/transcripts/PLTR-2Q26-transcript, 제3자 전사본)과 CEO 서한(https://www.palantir.com/q2-2026-letter/en/)이다. 통화는 AIP 에 따로 돈을 내는 고객 수·매출 몫과 AIP 가격 인상을 말하지 않고, 서한은 AIP 를 앞선 면책 문구 말고 쓰지 않는다. ① AI 수익화는 부분 그대로다. '열지 못해'를 '열어 보니 AIP 몫·가격 인상 서술이 없다'로 고친다.

5. **fail(점수 불변) — spacex-xai.F1 판정 칸.** 'Grok·X 요금 체계를 바꾸는 안을 검토한다는 보도는 원문을 확인하지 못해 쓰지 않는다.' 라고 적었다. 그 보도(Bloomberg 인용, Yahoo Finance 2026-10-01 'SpaceXAI considers four-tier pricing model for Grok and X users')는 `resolve-urls` 로 풀면 https://finance.yahoo.com/technology/ai/articles/spacexai-considers-four-tier-pricing-181516980.html 이고 본문이 열린다. 내부 문서를 인용한 계획(무료·월 $8 Lite·월 $100 Ultra 네 단계)이라 회사 1차 발표도 아니고 실행된 인상도 아니다. ① AI 수익화 '예'는 회사 공시나 1차 발표를 요구하므로 점수는 안 바뀐다. 문장을 '열어 보니 계획 단계의 2차 보도라 쓰지 않는다'로 고친다.

6. **fail(점수 불변) — EV-alibaba-074 locator.** '20-F Item 4.B … T-Head 소제목 단락(p.88)' 이라 적었는데 그 단락(발췌 'T-Head, our chip design subsidiary, has brought its proprietary GPU into production at scale…')은 20-F 81쪽이다(같은 20-F 에서 EV-alibaba-076 PAI·EV-alibaba-083 Qwen 앱의 88쪽, EV-alibaba-077 Apsara 의 91쪽, EV-alibaba-089 의 173쪽은 맞다). locator 를 81쪽으로 고친다.

7. **EV-tesla-008 출처 URL·날짜.** 발췌('In the third quarter, we produced over 464,000 vehicles, delivered over 486,000 vehicles and deployed 13.7 GWh…')는 인용한 URL(8-K 본문 `tsla-20261002.htm`, 표지와 Item 2.02·9.01 만 있다)에 없다. 같은 제출본(accession 0001628280-26-064366)의 Exhibit 99.1 `exhibit991111111.htm` 에 글자 그대로 있고 locator 도 그 첨부를 가리킨다. 출처 URL 을 Exhibit 99.1 로 옮기고 `published_at_utc`(비어 있음)에 2026-10-02 를 넣는다. 이 근거의 `unverified` 는 '같은 날 보도 제목에서 옮겼고 공시 본문과 대조하지 않았다'고 적는데 지금은 대조됐다.

8. **oracle.F4 서버·네트워크 칸 '자체 사용'의 근거.** 올릴 근거 줄('OCI Zettascale10 클러스터는 Oracle 이 자체 설계한 Acceleron RoCE 네트워킹으로 NVIDIA GPU 수십만 개를 잇는다', EV-oracle-056)은 2025-10-14 발표문이고 그 문서는 'Built on next-generation Oracle Acceleron RoCE networking architecture'·'OCI is now taking orders …, which will be available in the second half of next calendar year' 를 적는다. 자체 설계('designed')라는 말은 발표문에 없고, 지금 가동 중이라는 말도 없다. 줄은 이를 현재 사실로 적었다. 칸 값 합이 상한 2.5 에 걸려(엔진 모의: 서버·네트워크를 '없음'으로 바꿔도 ④ 4.5 그대로) 점수는 같다. 줄을 '발표와 주문 접수 단계'로 고치고 '자체 설계'는 추론으로 표시한다. 같은 기준을 Tesla ④ 에 대면 '자체 설계 장비 미확인'이라 서버 없음이고, Tesla 서버·네트워크를 자체 사용으로 읽으면 ④ 4.5 → 5(엔진 모의, 순위 불변)이므로 두 회사에 같은 잣대를 댔는지 규칙 일관성 영역이 함께 본다.

9. **낡은 `unverified` 문구 20건.** 아래 근거는 `confirmed` 이고 발췌가 본문에 있는데 `unverified` 에 '제목만 보고 판정함'·'본문 미열람'이 남아 있다. 근거 문장과 원문이 맞아 점수에는 닿지 않지만, 승인 페이지에서 제목만 보고 확정한 것으로 읽힌다. 지운다. EV-alphabet-006, EV-anthropic-010, EV-openai-001·003·009·010, EV-oracle-004·005·008, EV-palantir-004·005·007·008·010·011, EV-spacex-xai-001·008·009, EV-tesla-007 열아홉 건에 EV-tesla-008(발견 7)을 더해 스무 건이다. 이 가운데 EV-openai-010·EV-palantir-004·011 은 FT 부제만 따서 '제목만'이 아니라 '부제만'이라고 고친다.

10. **유출 초안 인용 보도가 방향 칸에 있다.** 판정 칸은 유출 초안 수치를 등급을 가르는 값으로 쓰지 않는다고 밝히지만(Anthropic ⑤·⑧, SpaceX ⑦), 방향 칸에는 그 수치를 단 줄이 있다. anthropic.F5 올릴 근거 'Anthropic 매출의 약 47% 가 … Amazon·Google 을 거쳤다(유출된 상장 신청서를 인용한 2차 보도)' [EV-alphabet-006]와 내릴 근거 'Cursor 와 GitHub Copilot 이 4분의 1 가까이를 낸다' [EV-anthropic-048], anthropic.F7 내릴 근거 [EV-anthropic-048, EV-anthropic-060], spacex-xai.F7 내릴 근거 '지출이 최대 $84.5B'·'순손실 $42B, $518B' [EV-spacex-xai-008·043]다. 줄마다 '보도가 있다'로만 쓰였고 점수 입력은 이 수치에 기대지 않는다(가로축은 S-1/A 의 월 $1.25B 로 선다). 같은 방향 칸에 두면 점수를 가르는 근거로 읽히니, 판정 칸에 두거나 방향 칸에서 '점수에 넣지 않는다'를 줄마다 단다(규칙 일관성 영역 Q03 과 함께).

11. **oracle.F7 '돌아옴' 연결(경계).** 세로축은 'TikTok USDS Joint Venture LLC 지분 15%(10-Q)'와 'TikTok 은 OCI 의 최대 계약 고객 가운데 하나(회사 1차 발표, EV-oracle-030)'를 한 구조로 묶는다. 인용한 문서 어느 것도 합작법인 자신이 Oracle 에 대금을 낸다고 적지 않는다(10-K·10-Q 는 합작법인을 비시장성 투자 문단에서만 언급한다). 규칙 정의에 '(또는 고객을 위한 합작법인)'이 있어 읽기는 설 수 있으나 연결은 추론이다. 판정 칸에 '추론'을 표시하거나 합작법인이 OCI 고객이라는 1차 문장을 찾는다. 엔진 모의로 '돌아오지 않음'이면 Oracle ⑦ −3 → −2, 조정 7.5 → 8.5, 순위 7위 → 6위(NVIDIA 가 7위)다.

12. **openai.F8 의 교차 참조.** F8 판정 칸은 'Cerebras 에 준 $10억 대출은 ⑦ 에서 센다'고 적는데 F7 판정 칸에는 그 문장이 없다. Cerebras 는 OpenAI 의 공급자(컴퓨트를 파는 쪽)라 세로축(고객이 대금을 냄)에 맞지 않으므로 F8 쪽 문장이 어긋난다. 점수에는 닿지 않는다.

## 체크리스트 (사실·출처 영역이 닿는 항목)

| ID | 결과 | 근거 |
| --- | --- | --- |
| Q05 | pass | 맡은 회사 근거마다 출처 등급(공시·회사 1차 발표·독립 측정·2차 보도·유출 초안)이 줄이나 판정 칸에 적혀 있다. 이해상충 표기는 점검 대상이 아니다(AGENTS.md 「금지·주의」). |
| Q09 | pass | Cursor 차단(11-12), Tesla 3분기 Update, Jalapeño 배치, Optimus, Terafab, 궤도 컴퓨트는 계획이라 점수에서 뺐다. 단 Oracle ④ 서버 칸의 Zettascale10 줄은 발표 단계를 현재 사실처럼 적었고 점수는 같다(발견 8). |
| Q23 | pass | ARC-AGI-3 Provider Adapter 값과 OpenAI 발표 99.9% 는 표준 하네스와 견주지 않았다. Alibaba HLE 기사 값도 하네스가 달라 비교에서 뺐다. |
| 그 밖 | not_applicable | 판정표 대조·사건 교차표·미확인 방향표는 규칙 일관성 영역이 본다. 이 영역은 미확인이 감점 완화 쪽으로 풀린 사실 근거(발견 1~3)와 유출 초안 수치의 위치(발견 10)를 알렸다. |

## 다음 실행 과제

1. EV-alibaba-074 의 locator 를 81쪽으로, EV-tesla-008 의 출처를 Exhibit 99.1 로 옮기고 `published_at_utc` 를 채운다(발견 6·7).
2. 낡은 `unverified` 문구 20건을 지운다(발견 9). 근거를 확정할 때 `unverified` 를 새로 쓰는 단계가 필요하다.
3. 출처 ID 이름이 회사와 어긋난 것을 바로잡는다. `SRC-SEC-anthropic-000101872426000002`·`SRC-SEC-anthropic-000101872426000026` 은 Amazon(CIK 1018724) 8-K·10-Q 이고, `SRC-SEC-anthropic-000162828026040364` 는 SpaceX(CIK 1181412) S-1/A 이며 같은 문서가 `SRC-SEC-spacex-xai-000162828026040364` 로도 등록돼 있다(`SRC-SEC-SPCX-S1A-2026` 은 폴더 주소다). `SRC-WEB-amazon-010`(anthropic.com 글)·`SRC-WEB-anthropic-030`(biggo.com)·`SRC-WEB-spacex-xai-010`(wccftech)·`SRC-WEB-openai-901`(The Next Web) 처럼 처음 인용한 회사 이름이 붙은 공용 출처도 있다. 공시 출처는 제출 회사 slug 로, 여러 회사가 같이 쓰는 웹 출처는 회사 없는 이름으로 옮긴다.
4. 라이브 순위 페이지 근거(EV-anthropic-049·051·052·057, EV-amazon-051, EV-anthropic-055, EV-openai-051)는 스냅숏 텍스트를 저장해 다음 리뷰가 같은 값을 다시 볼 수 있게 한다. EV-anthropic-049·052 의 라벨-값 짝짓기는 렌더링한 텍스트를 함께 둔다.
5. EV-palantir-028(FT 본문)은 구독 장벽으로 본문을 다시 확인하지 못했다. 같은 기사의 `og:description` 은 Homes for Ukraine 계약 연장 기사임을 보여 준다. 열리는 전재본을 찾거나 본문을 저장한다.
6. 사실·출처 영역이 보는 미확인 문장 점검을 근거 확정 단계에 넣는다. 판정 칸의 '찾지 못했다'가 같은 실행의 확정 근거 문서(10-K·10-Q·20-F 위험 요인·관련 당사자 절)에 있는지 한 번 더 검색하는 절차가 있었다면 발견 1·2 는 이 단계에서 잡혔다. 같은 질문('투자한 곳이 고객인가')을 열네 회사 모두에 같은 키워드('investee', 'strategic investment', 'commercial contract' 등)로 묻는 점검을 만든다. 이번에는 맡은 일곱 회사만 검색했고 Oracle·Tesla·SpaceX 는 해당 문장이 없었다.
7. OpenAI ⑦ 세로축을 판단 세션이 다시 매길 때 OpenAI Startup Fund 의 출자자 구성과 YC 토큰-지분 교환의 체결 여부(SAFE 서명·토큰 소진)를 1차 자료로 확인한다(발견 3).
8. 맡은 회사 판정 칸 곳곳에 수치가 근거 표지 없이 섞여 있다. Tesla ③ 'FSD 월 구독 연환산 매출 약 $7.9억으로 보도'는 EV-tesla-043(2차 매체의 666,000명 × $99 × 12 계산)에서 왔고, Anthropic ⑦ '$1,000 크레딧'은 EV-anthropic-061 에서 왔지만 판정 칸이 근거를 밝히지 않는다. 표지 없는 사실은 판정 칸에서 어떤 근거가 받치는지 문장으로 적는다.

## 열지 못했거나 글자 그대로 대조하지 못한 원문

- EV-palantir-028 FT 본문: 구독 장벽(부제 `og:description` 만 확인). Palantir ①③⑤ 줄이 인용한다.
- EV-anthropic-045 Reuters: 401. 판단 줄이 인용하지 않는다.
- 라이브 순위·가격 페이지 일곱 건: 위 '발췌·위치 대조 결과' 참고.
- Axios·WSJ·Reuters·Bloomberg·FT 등 구독 사이트 가운데 브라우저로 열린 것은 화면 본문을, 그렇지 않은 것은 전재본이나 부제로 대조했고 각 근거의 `unverified` 가 그 한계를 적는다.
