---
reviewer_agent: fact-checker
session: fs-a-v21-20261013-r1
reviewed_at: 2026-10-13
round: 1
---
# fact-sources-a — 사실·출처 (nvidia, tsmc, apple, alphabet, amazon, microsoft, meta)
검토자: Claude Sonnet 5.5 (claude-sonnet-5-5) · 사실·출처 독립 세션 a(이 실행을 만든 세션 아님) · 2026-10-13
결과: pass
요약: 맡은 일곱 회사의 정성 판단 49건(①②③④⑤⑦⑧, 모두 `status: new`)과 올릴·내릴 근거 573줄, 그 줄과 ④ `layer_evidence`·`non_ai_share_evidence`·① `ai_*_evidence`·`evidence_ids` 가 가리키는 근거 457건을 전수로 봤다. 457건 모두 confirmed 이고 reviewer·reviewed_at·locator·원문 발췌·등록된 출처 URL 을 갖췄으며 발행일이 정보 마감(2026-10-12) 이하다. 발췌는 432건을 원문과 기계 대조했고 10건은 브라우저로, 2건은 원문 텍스트로 직접 맞췄으며 13건은 이번에 열리지 않았지만 직전 실행과 발췌·위치·주소가 같다. 이번에 새로 들어온 관측(지분 평가손익 4건, 세 항목 TTM, 클라우드 세그먼트 분기 값, NVIDIA 공급자 지원 둘, Meta 잔존가치 보증)은 원문 숫자와 모두 맞는다. 점수·순위를 바꾸는 발견은 없다. 다만 Microsoft ⑤ 판정 칸의 "Anthropic 지분 투자 미확인" 한 문장은 같은 실행의 확정 근거 출처에 반대 사실이 있어 미확인 규율 fail 이다(점수 불변). 수정 묶음이 생기면 그때 함께 고친다.

검토 기준: review.md frontmatter results_hash `55d4a0cc8452c05d…`, draft_hash `21a0850e0a1f9bb5…`. results.json 의 `results_hash` 와 draft.md 파일 sha256 이 둘 다 이 값과 같다. draft.md 「종합 순위표」의 일곱 회사 행(Alphabet 13·Amazon 13·Microsoft 10.5·Apple 10·TSMC 9·NVIDIA 8, Meta ③ 대기)은 results.json 과 같고, 판단 파일의 기업 요약 일곱 건의 점수·함정 합도 순위표와 같다.

## RESULT

pass. 점수·순위·체크리스트 판정을 바꾸는 발견이 없다. 아래 FINDINGS 의 F1 은 미확인 규율 fail(점수 불변), F2~F4 는 다른 영역이 볼 경계다. 나머지는 「다음 실행 과제」에 적었다.

## 확인한 것

### 범위와 기계 점검
- 대상 49건(nvidia.F7.fix52·tsmc.F5.strict54 포함)은 전부 새 판단이고 승계가 없다. 올릴·내릴 근거는 573줄(nvidia 105, alphabet 92, microsoft 92, meta 78, apple 71, amazon 70, tsmc 65)이고 줄마다 끝에 `[EV-…]` 표지가 있다. 표지가 가리키는 근거 가운데 다른 회사 번호는 anthropic 9, openai 9, tesla 2, oracle 1, spacex-xai 1이다.
- 가리킨 근거 457건(줄 표지 403 + `evidence_ids`·입력 54)은 모두 evidence.json 에 있고 `status: confirmed`, reviewer·reviewed_at·locator 가 있으며 excerpt 는 제목과 다르다. source_id 는 모두 sources.json 에 있고 URL 은 `http(s)://` 이다. Google News 중계 주소로 남은 것은 없다(google.com 도메인 3건은 Google Cloud·Workspace 1차 블로그다). 후보(candidate) 근거를 인용한 판단은 없다. 발행일 최대는 2026-10-11 이고 관측 as_of 도 모두 2026-10-12 이하다.
- 직전 실행(recheck)과 견주면 345건은 발췌·위치·출처·제목·발행일이 같고 112건이 새 근거다. 새 근거가 닿는 줄은 136줄이다. 바뀐 근거는 없다.
- 판단 `source_ids`(SRC-v15-html 등), 관측 source_id, 트리거 85건의 evidence_ids·source_ids 가 모두 등록돼 있다.
- 부재 라벨: 맡은 일곱 회사 관측의 `not_disclosed` 9건은 모두 `missing_type: unverified` 이고 note 가 "확인하지 않았다/못했다" 로 적혀 있어 확인된 미공시와 섞이지 않는다. `not_disclosed_confirmed` 는 없다. ⑧ 고객 축 `not_disclosed`(Alphabet·Amazon·Apple)와 `absent_disclosed`(Meta)는 판정 칸에 검색 범위나 10-K 문장을 적었다.

### 원문 받기와 발췌 대조(457건)
- SEC 문서 54곳은 `data/_sec/docs/` 캐시에서 읽었다(색인 sha256 과 파일이 모두 맞는다). `sec-get` 을 부를 일이 없었고 SEC 요청이나 User-Agent 를 직접 만들지 않았다. 웹 180곳은 일반 직접 받기로 받았고, 막힌 곳은 브라우저 창에서 열었다. 막힌 페이지를 User-Agent 로 우회하지 않았다.
- 기계 대조 432건: 정규화 문자열 일치 233, 문장부호·표 칸만 다른 일치 70, "…" 로 나눈 조각이 모두 원문에 있는 것 124, 표 줄 일치(머리글 줄만 서식 차이) 5. 표 발췌(EV-nvidia-024·054·055·056, EV-meta-020)는 머리글 줄만 서식이 달랐고 숫자 줄은 모두 원문과 같다.
- 브라우저로 직접 열어 맞춘 것 10건: marketscreener(EV-alphabet-005), war.gov(EV-alphabet-044·048), cloudcomputing-news(EV-amazon-008·EV-microsoft-040, 같은 문서), ai.meta.com(EV-meta-054·056), ftc.gov(EV-amazon-055), Benzinga(EV-meta-057), Futu(EV-nvidia-066). 광고·소제목이 끼어 기계 대조가 어긋난 EV-alphabet-040(소제목 "Search monopoly")과 쪽 번호가 문장 가운데 낀 EV-tsmc-065(20-F 31쪽 경계)는 원문 텍스트에서 앞뒤 조각이 모두 있다.
- 이번에 다시 열지 못한 13건은 모두 직전 실행과 발췌·위치·주소가 같다. Reuters 5건(EV-alphabet-042·050, EV-meta-008·052, EV-nvidia-010)은 직접 받기가 401 이고 브라우저 창도 접근을 거부했다. techxplore(EV-apple-025)와 Search Engine Land(EV-apple-028)는 봇 확인 화면이 떠서 기다려도 열리지 않았고 우회하지 않았다. Barchart(EV-meta-009)는 빈 페이지가 왔다. Arena(EV-amazon-051·EV-microsoft-009)는 직전 리뷰가 10-08 판으로 바뀐 것을 확인했고 점수에 닿지 않는다. Artificial Analysis 세부 페이지(EV-anthropic-051·052)는 다시 열지 않았다.
- 같은 열기: EV-anthropic-049(Artificial Analysis 홈페이지)는 2026-10-13 에 연 페이지가 이미 바뀌어 있다(F4).

### 줄 사실(573줄)과 판정 칸 숫자
- 줄의 숫자를 발췌와 기계로 견줘 발췌에 없는 172줄을 뽑아 모두 원문과 맞췄다. 대부분은 단위 환산(억·만·B), 날짜, 계산 표시가 붙은 값이다. 새 근거가 닿는 136줄은 발췌와 한 줄씩 읽었다.
- 판정 칸 문장의 숫자를 근거 발췌·입력·관측과 기계로 견줘 어느 것에도 없는 39문장을 뽑고 직접 다시 계산했다. 다시 계산해 맞은 것은 다음과 같다.
  - ⑧ 약정 배수: alphabet (811.0 + 85.2 + 5.8) ÷ 445.866 = 2.02, amazon (137.214 + 130.065) ÷ 775.680 = 0.345, microsoft (329.1 + 194.060 + 34.566) ÷ 331.839 = 1.68, meta (278.99 + 349.31 + 68) ÷ 228.247 = 3.05(2026-07 리스 $68B 를 빼면 2.75), nvidia (366 − 25 + 20) ÷ 302.97 = 1.19(82% 가 2029 회계연도 말 안, 18개월 몫 $199B = 0.66배), apple 86.8 ÷ 466.823 = 0.19, tsmc 1,534,575 ÷ 4,440,492 = 0.35.
  - ④ AI 무관 몫: alphabet 82.6%(네 분기 합 모두 맞음), amazon 80.9%, microsoft 61.0%, meta 98.7%, nvidia 7.7%, tsmc 40.0%(HPC 최근 12개월 NT$2,663,665,463천 ÷ 4,440,492,429천), apple 100%(최근 1년 매출 $466,823M).
  - ⑦: nvidia 조달 의존 몫 상한 41.9%·40.8%, 보증 $105B ÷ $303.0B = 34.7%, RPO $3.2B ÷ $303.0B = 1.1%. amazon (22.5 + 38.0) ÷ 775.7 = 7.8%, 두 회사 약정 $238B 가 1년 초과 미인식 약정 $496B 의 48%($496B 는 10-Q 본문에서 확인). microsoft $24.1B ÷ $331.8B = 7.3%, RPO 45% ÷ 2.5년 = 연 $112.5B = 33.9%, (250 + 30) ÷ 331.8 = 84.4%.
  - ③: Alphabet Gemini 앱 월 복리 성장률 4.5%·5.5%·2.6%(6.5억→7.5억 98일, →9억 104일, →9.5억 64일), microsoft Copilot 좌석 +33%→+50%, tsmc HPC +20%→+20%, nvidia 데이터센터 +21%→+18%, amazon AWS +24%→+28%→+37%.
- 요일·날짜: Brinkema 판결 2026-09-02, Apple Siri 합의 2026-05-05, 노동부 정지 2026-10-08, 뉴멕시코 평결 2026-03-24, Taction 평결·SB Energy 8-K 2026-08-17 이 원문과 맞는다.

### 새로 들어온 관측(원문 대조)
- 지분 평가손익 `equity_investment_gains_ttm`: Alphabet $148,982M(= 2025 연간 24,080 − 2025 상반기 11,044 + 2026 상반기 135,946, 10-Q·10-K Note 3 줄과 같음), Amazon $72,056M(시장성 지분 1,439 + 430 − 250 = 1,619, 비상장 상향 7,709 + 62,814 − 86 = 70,437), Microsoft $4,364M(10-K Note 3 합계), NVIDIA $30,552M(8,918 − 2,073 + 23,707). 기간(최근 1년)·성분 제외(지분법·채무증권·워런트)가 basis 와 note 에 적혀 있고 원문 줄과 같다.
- `income_tax_ttm`·`ocf_ttm`·`capex_ttm`: Alphabet 55,064·185,675·132,402, Amazon 39,615·161,403·173,028, Meta 19,426·130,301·89,325, Microsoft 32,185·182,935·115,948, Apple 26,976·146,724·10,041, NVIDIA 36,863·134,360·7,354(백만 달러)를 10-K 연간 − 전년 같은 반기(9개월) + 올해 값으로 모두 다시 만들어 같았다. Meta 세금은 10-Q 가 적은 상반기 감소 $6.05B 로 맞췄다. TSMC OCF NT$2,634,679,110천 ÷ 31.37 = $83.99B 도 6-K 연간·반기 값과 같다. Amazon 의 capex 는 총 구매액 $173,028M 이고(순액 $169,007M 아님) ocf − capex = −$11.6B 가 ⑨ 의 값과 같다.
- 클라우드 세그먼트 분기 값: Alphabet Google Cloud 매출·영업이익 15,157·3,594 / 17,664·5,313 / 20,028·6,598 / 24,768·8,814, Amazon AWS 33,006·11,434 / 35,579·12,465 / 37,587·14,161 / 42,232·16,621, Microsoft Intelligent Cloud 30,897·13,391 / 32,907·13,873 / 34,681·13,753 / 39,306·15,955(네 분기 합이 FY2026 합계 137,791·56,972 와 같다)가 8-K·10-Q 표와 같다.
- NVIDIA `supplier_guarantees`($3.5B)와 `supplier_capacity_buyback`($36B)는 10-Q Note 10 과 같다. 분기 뒤 서명한 SB Energy 보증 $105B 는 `basis.subsequent_event` 로 두었고 8-K(2026-08-17)의 상한·발효 조건·OpenAI 보상 문장과 같다. Meta `residual_value_guarantee`($28B)는 10-Q Note 5 의 "aggregate threshold of approximately $28 billion" 이고, 합작 최대 손실 노출 $46.03B 와 El Paso 보증 약 $13B(2026-07, 분기 뒤)는 값에서 빠져 있다.

### 부재 주장과 미확인 문장
- 판정 칸의 "미확인·확인하지 못했다·찾지 못했다" 계열 문장 122개를 모두 훑었다. 열리는 원문이 있는데 판단이 쓰지 않은 것은 F1 하나다. Meta ③ 의 "Meta AI 월간 사용자 뒤 수치 없음"은 2026년 1·2분기 실적 콜 전문에서 월간 수치를 찾지 못해 맞다. Amazon·Apple ⑧ 의 "10% 이상 고객 문장 없음"도 10-K·10-Q 전문에서 고객 문장을 찾지 못해 맞다(Amazon 10-K 의 10% 문장은 공급자 쪽이다). Microsoft ① 의 "가장 최근 분기의 상업용 유료 좌석 절댓값 없음"도 FY26 4분기 콜과 FY27 투자자 지표에서 증가율만 나와 맞다.
- "제목만" 을 사유로 쓴 판정 문장은 없다.

### 트리거
- 맡은 일곱 회사 트리거는 40건(이어받은 35, 새로 TRG-113~117)이다. 모두 `watching` 이고 기한이 정보 마감 이전인 것이 없다. 이어받은 35건의 carry finding 은 "이전 실행과 기준일·정보 마감이 같아 새로 볼 창이 없다" 로 같은 문장이고, 이전 실행이 같은 날 확인한 상태이므로 맞다. 새 트리거 다섯의 근거는 모두 확정이고, 맡은 회사 쪽 관측 문장(검색 점유율 89.94%, UBS 분석·Amazon 의 Muse 차단, Microsoft 365 좌석 4.5억·6%, Meta 광고 노출·가격)은 근거 발췌와 같다. OpenAI·Oracle 쪽 문장은 b 묶음이 본다.

### 초안과 금지 표현
- 맡은 회사 근거의 relevance·conditional_impact 와 draft 에 매수·매도 권유, 목표 주가, 수익 보장, 조급함을 부추기는 표현이 없다. 이해상충 표기는 점검하지 않았다(AGENTS.md 「금지·주의」).

## FINDINGS

### F1 · fail(미확인 규율, 점수 불변) · microsoft ⑤ 판정 칸의 Anthropic 지분 투자
- **판단 문장.** microsoft.F5 판정 칸 V8 은 "지분 동맹 조항은 확정 근거로 확인된 것이 OpenAI 하나라 서지 않는다. 마이크로소프트의 Anthropic 지분 투자는 확정 근거로 확인하지 못했다(미확인)" 고 적는다.
- **원문.** 이 실행이 이미 등록한 출처 둘에 있다. FY26 4분기 실적 콜(SRC-WEB-microsoft-001, EV-microsoft-005·010·048 의 출처)에 "These include a $3.2 billion gain from our investment in Anthropic" 와 "other income and expense was $2.8 billion driven by the gain on investment in Anthropic" 가 있다(2026-07-29 열기로 확인). 2025-11-18 3사 발표(EV-microsoft-015 의 출처)는 NVIDIA 와 Microsoft 가 Anthropic 에 각각 최대 $10B·$5B 를 투자하기로 했다고 적는다(직전 리뷰가 같은 문장을 확인했다).
- **점수 영향.** 없다. ⑤ 동맹 등급 +2 는 이미 경쟁사 편입 조항(Anthropic 의 Azure $30B 약정)으로 서고, 지분 동맹이 둘이 되어도 상한 +2 라 같다. 판정 문장만 원문과 어긋난다.
- **고칠 것.** V8 을 "Anthropic 투자 이익 $3.2B 가 실적 콜에 있어 지분 투자는 확인되지만 동맹 등급은 이미 +2 라 결과를 바꾸지 않는다" 꼴로 다시 쓰고 EV-microsoft-005·015 를 인용한다. 직전 실행 리뷰의 다음 과제 2 와 같은 문장이 그대로 이어졌다.

### F2 · 규칙 일관성 영역 확인 요청 · Meta ⑧ 약정 축의 분기 뒤 리스(−3 ↔ −2)
- 사실은 맞다. 10-Q 가 2026-07 체결 리스 약 $68B(2027·2028 개시, 18~20년)를 적었고, 포함하면 (278.99 + 349.31 + 68) ÷ 228.247 = 3.05배(−3), 빼면 2.75배(−2)다. 판정 칸이 이 경계를 적고 "이미 체결해 10-Q 에 공시된 리스라 넣는 것이 규칙이다" 로 정했다.
- 같은 실행에서 분기 뒤 사건의 다룸이 갈린다. NVIDIA 의 분기 뒤 SB Energy 보증 $105B 는 관측 값에서 빼고 `subsequent_event` 로 두었지만(⑦ 서술에서는 세로축 근거로 인용), Meta 의 분기 뒤 리스는 ⑧ 값에 넣어 구간을 가른다. 보증(우발 의무)과 리스(약정)는 성격이 달라 같은 잣대를 대지 않았을 수 있다. 점수 영향은 Meta 함정 −5 → −4 이고 Meta 는 ③ 대기라 순위는 그대로다. Q03 판정은 규칙 일관성 영역이 낸다.

### F3 · 규칙 일관성 영역 확인 요청 · Apple ④ 모델 칸 '판매' 와 ① 의 계획 처리
- Apple ④ 는 모델 칸을 판매로 적고 근거를 WWDC 세션의 "users can upgrade to iCloud+ to get higher limits"(EV-apple-051) 한 문장에 둔다. 같은 실행의 EV-apple-037(2026-09-09 보도자료 각주)은 "Expanded access to such features will be available for a fee in the future" 라 유료 확대가 앞으로의 일이라고 적고, Apple ① 판정 칸은 이 각주를 "계획이라 점수에 넣지 않는다" 로 처리한다. 같은 사실을 ① 은 계획으로, ④ 는 판매로 읽었다.
- 점수 영향은 없다. 모델 칸을 자체 사용으로 읽어도 수직계열화는 칸 값 합 2.5 로 같다. 다만 판매 칸이 하나도 없어져 주 레이어 검증이 막힌다(판단 세션이 스스로 적은 규칙 빈틈). 판단 세션이 근거가 얇다고 판정 칸에 남겼다.

### F4 · 판정 문장의 낡은 서술(점수 불변) · Meta 의 Artificial Analysis 최고 모델
- Alphabet ②·Meta ② 판정 칸 V2 는 "판단 세션이 2026-10-12 다시 연 Artificial Analysis 에서도 회사별 최고 모델 순서(Meta 48 …)가 같고, 2026-10-08 뒤의 새 평가가 회사별 최고 모델을 바꾸지 않았다" 고 적는다. 2026-10-13 에 연 홈페이지는 종합 지수 차트에 Muse Wonder(max) 52 를 올렸고 변경 기록에 12 Oct "Muse Wonder and Muse Wonder Full: a material jump in intelligence over previous Meta models" 가 있다. 그러면 Meta 의 회사별 최고 모델은 12일에 Muse Spark 1.3(48)에서 바뀌었을 수 있다.
- 점수 영향은 없다. ② 성능 도약의 통과는 두 축 이상 1위일 때만 세는데(`compute_f2` 는 `pass` 만 센다) Muse Wonder 52 는 종합 지수에서 Anthropic 58·OpenAI·Google 53 보다 낮아 Meta 가 어느 회사 기준에서도 1위가 아니다. 정보 마감 이하의 사실이 판정 문장에서 빠진 것이라 다음 실행에서 열람 시각과 함께 고쳐 적는다.

## 다음 실행 과제

1. microsoft.F5 V8 은 F1 대로 고친다(직전 실행 리뷰 과제 2 가 반영되지 않았다).
2. meta.F5 내릴 근거 "뉴멕시코 배심원은 2026-03-24 Meta 에 민사벌금 $375M 을 명령했고, 주 정부는 $35~40B 의 벌금을 판사에게 요구했으며 …" [EV-meta-027, EV-meta-009, EV-meta-026] 는 두 금액을 한 사건처럼 잇는다. 10-Q(EV-meta-027)의 $375M 은 청소년 관련 소송의 평결이고, Barchart(EV-meta-009)는 $35~40B 요구가 데이터 프라이버시 진술을 어겼다는 평결 뒤라고 적는다. 두 사건이면 나누어 쓰고, 한 사건이면 원문끼리 어긋난다는 사실을 적는다. 둘 다 비용형이라 점수는 그대로다(직전 실행 리뷰 과제 1 과 같다).
3. nvidia.F5 V6 "Anthropic 은 NVIDIA 와 직접 맺은 다년 약정이 확정 근거로 확인되지 않고" 는 2025-11-18 3사 발표(최대 1GW 컴퓨트, NVIDIA 시스템)와 엇갈릴 여지가 있다. 그 약정이 Azure 를 거치는지 직접 약정인지 문안에 없다고 좁혀 쓴다. 동맹 등급은 CoreWeave·Nebius 로 이미 +2 라 점수는 그대로다(직전 과제 4 와 같다).
4. 판정 칸에 숫자나 사실이 있지만 인용 근거 발췌에 없는 것을 근거 줄로 올리거나 지운다. 점수에는 닿지 않는다.
   - tsmc.F2 V6 "TSMC 가 2022년 내놓은 3D 칩 설계 언어 3Dblox" 는 evidence.json 어디에도 근거가 없다.
   - alphabet.F2 V5 "Arena 텍스트 부문에서 Gemini 4 Argon 이 표본 4,932표의 잠정 1위", alphabet·meta ② V2 "Alibaba 45" 는 인용 근거가 없다. Arena 페이지는 같은 주소에서 판이 바뀌어 다시 볼 수 없다(직전 과제 6).
   - nvidia.F4 non_ai_share_basis "Edge Computing 최근 12개월 $25,172M(8.3%)" 은 근거 표지가 없다. 10-K 연간 표는 구분이 달라 이 값을 만들 수 없다. 민감도 서술이라 구간은 같다.
   - nvidia.F1 V7 의 Hopper $18B·Vera Rubin $40B/GW 는 실적 콜 전문(EV-nvidia-041 의 출처)에 있고 줄로 인용되지 않았다.
5. Apple ① V6·⑧ V4·입력 note 의 매출채권 집중 "한 고객 12%, 이동통신사 34%" 는 2025-09-27 10-K 값이다. 2026-06-27 10-Q 는 한 고객 18%, 이동통신사 27% 를 적는다(같은 문장 구조). 최신 값으로 고친다. ⑧ 고객 축은 `not_disclosed` 정책 기본값이라 점수는 그대로다.
6. microsoft.F8 V4 "구매 약정을 모두 빼도 약 0.99배" 는 건설 약정 $34.566B 가 남으면 (329.1 + 34.566) ÷ 331.839 = 1.10배다. 0.99배는 리스만 남긴 값이다. 둘 다 같은 구간(0.5배 이상 3배 미만)이라 점수는 그대로다.
7. microsoft.F1 근거 "2026년 1월 상업용 유료 좌석은 4.5억 개를 넘었다" [EV-microsoft-031] 는 2025-12-31 분기 말 값을 2026-01-28 통화에서 밝힌 것이다. 같은 판단의 입력과 판정 칸은 2025-12-31 로 적었다. 줄을 "2025-12-31 현재(2026-01-28 통화)" 로 맞춘다.
8. meta.F3 올릴 근거 "Muse 는 미국 출시 3주 만에 주간 이용자 300만 명을 넘었다" [EV-meta-004] 는 원문의 "주 1회 이상 프롬프트를 보내는 사람 300만 명 이상, 어떤 식으로든 쓰는 사람 400만 명 이상" 가운데 앞의 정의다. "주간 프롬프트 사용자" 로 맞춘다(직전 과제 8 과 같다).
9. EV-nvidia-079 locator 의 두 조각은 세는 기준이 한 칸 다르다. EV-tsmc-079 로 인용한 tsmc.F8 "최대 고객 비중은 2023년 25%, 2024년 22%, 2025년 19%" 는 표의 Customer A·B 를 연도별로 합쳐 읽어야 나온다. 같은 문장이 있는 EV-tsmc-040 도 함께 인용한다.
10. 막힌 페이지(Reuters 5, techxplore, Search Engine Land, Barchart)는 다음 실행에서 열람 방법과 결과를 근거 비고에 남긴다.

## CHECKLIST

사실·출처에 닿는 Q 만 적는다. 나머지는 규칙 일관성 영역이 채운다.

| ID | 결과 | 근거 |
| --- | --- | --- |
| Q02 | pass | ① 가격 실측 지표(alphabet CPC·유료 클릭, amazon Prime 정가·구독 매출, microsoft 정가 인상·좌석, meta 광고당 가격, tsmc 선수금·총마진 사유)와 ③ 가속도 지표(alphabet d Gemini 앱 월간 사용자, microsoft b Copilot 좌석, tsmc b HPC, nvidia b 데이터센터 직전 분기 대비, amazon c AWS)가 근거 원문의 정의와 맞고 성장률을 원문 값으로 다시 계산해 같았다. |
| Q03 | pass(사실 수준, 확인 요청) | 같은 사건의 사실 귀속은 일관된다(Anthropic 약정·OpenAI 약정을 amazon·microsoft·alphabet ⑦ 이 같은 방식으로 연환산, 지분 평가이익을 ⑦ 에서 모두 제외). 분기 뒤 사건의 다룸(F2)은 규칙 일관성 영역이 가른다. |
| Q05 | pass | 결과 칸만 채운다. 결정적 사실은 공시·회사 1차 발표가 중심이고, 공매도 측 자료(EV-meta-057)와 유출 신청서 보도(EV-spacex-xai-043)는 줄에 등급을 적고 보도 사실로만 인용했다. |
| Q09 | pass(사실 수준, 확인 요청) | nvidia·amazon·alphabet ② ⑤ 의 약정·칩 계획은 줄에 "점수에 넣지 않는다" 로 적혀 있다. Apple 은 ① 과 ④ 의 읽기가 갈린다(F3). |
| Q22 | pass | alphabet(SpaceX·Anthropic)·amazon(Anthropic)·nvidia 의 지분 평가이익은 ⑦ 판정 칸에서 "⑥ 의 영업외 비중에서 다루고 ⑦ 의 입력으로 쓰지 않는다" 로 명시했고, 숫자도 ⑥ 관측으로만 쓴다. |
