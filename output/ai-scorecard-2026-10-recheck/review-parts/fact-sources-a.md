---
reviewer_agent: fact-checker
session: fs-a-recheck-20261012-r1
reviewed_at: 2026-10-12
round: 1
---
# fact-sources-a — 사실·출처 (nvidia, tsmc, apple, alphabet, amazon, microsoft, meta)
검토자: Claude Opus 5.5 (claude-opus-5-5) · 사실·출처 독립 세션 a(이 실행을 만든 세션 아님) · 2026-10-12
결과: needs_fix
요약: 맡은 일곱 회사의 정성 판단 49건, 올릴·내릴 근거 468줄과 그 줄이 가리키는 근거 328건(모두 confirmed, reviewer·reviewed_at·locator·본문 발췌·출처 URL 을 갖춤)을 전부 봤다. 출처 219곳(SEC 51, 웹 168) 가운데 SEC 51곳은 `data/_sec/docs/` 캐시로, 웹 168곳은 직접 받기 154곳과 Playwright 14곳으로 모두 열었고 328건 모두 발췌가 원문에 있다. 다만 Arena 순위표 두 건은 페이지가 10-08 판으로 바뀌어 10-02 판 값을 재현하지 못했다. 점수·순위를 바꾸는 발견은 셋이다. ① alphabet ⑧ 약정 축이 같은 10-Q 의 해지 불가 약정 총액 $811.0B 대신 1년 넘는 계약만 담은 주석 값 $707.0B 를 써 1.79배(−2)로 나왔다. Microsoft·Meta 와 같은 범위로 재면 2.02배(−3)다. ② microsoft ⑦ 은 OpenAI 의 Azure 추가 약정을 "원문을 갖추지 못해 미확인"으로 뺐지만, 회사 1차 발표(2025-10-28 블로그의 $250B)와 이미 등록된 FY26 2분기 실적 콜("commercial RPO 의 약 45% 가 OpenAI")이 열린다. 넣으면 가로축이 큼이 되어 −1 이 −2 로 바뀐다. ③ microsoft ⑧ 고객 축도 같은 45% 를 미확인으로 두었다. 넣으면 −2 나 −3 이 된다. 이 밖에 원문과 다른 기록 넷과 위치·표현 문제는 「다음 실행 과제」에 적었다.

검토 기준: review.md frontmatter results_hash `5d0c5181750b…`, draft_hash `35c6a4c45404…`. draft.md 「종합 순위표」의 일곱 회사 점수(Microsoft 14·Amazon 14·Alphabet 13·NVIDIA 9·TSMC 9·Apple 7, Meta ③ 대기)는 results.json 과 같다.

## RESULT

needs_fix. 고칠 것은 아래 FINDINGS F1~F3 이고, 셋 다 판단 입력을 고쳐 `research → calculate → draft → review` 를 다시 돌려야 한다. F1 은 재무 계산 영역(financial-calc.md ⑧ 절)이, F2 는 규칙 일관성 영역(rule-consistency.md N1)이 같은 결론을 냈다.

## 확인한 것

### 범위와 기계 점검
- 대상은 맡은 일곱 회사의 ①②③④⑤⑦⑧ 판단 49건이다(tsmc.F5.strict54, nvidia.F7.fix52 포함). 모두 `status: new` 이고 승계 판단은 없다. 올릴·내릴 근거 468줄(nvidia 91, alphabet 72, microsoft 69, apple 60, amazon 59, tsmc 59, meta 58)은 모두 끝에 표지 `[EV-…]` 가 있다. 표지가 가리키는 근거 328건(다른 회사 번호 16건 포함: anthropic 8, openai 6, spacex-xai 1, oracle 1)은 모두 evidence.json 에 있고 `status: confirmed`·reviewer·reviewed_at·locator 를 갖췄다. excerpt 는 제목과 다르고 600자 이하다. source_id 는 모두 sources.json 에 있고 URL 이 `http(s)://` 이며, Google News 중계 주소로 남은 것은 없다.
- 판단의 `source_ids`(SRC-v15-html 등), 판단의 `evidence_ids`, 맡은 회사 관측 294건의 source_id, 트리거 36건의 evidence_ids·source_ids 가 모두 sources.json·evidence.json 에 등록돼 있다. 새 판단이 후보 근거를 인용한 곳은 없다.
- 발행일: 328건 모두 `run.info_cutoff`(2026-10-12) 이하다. 가장 늦은 것은 EV-nvidia-082·083(2026-10-11)이다. 맡은 회사 관측의 as_of 도 모두 기준일 이하다.
- 원문 받기: SEC 문서 51곳은 모두 `data/_sec/docs/index.json` 캐시에 있어 새로 요청하지 않았다. `sec-get` 을 부를 일이 없었고, SEC 요청이나 User-Agent 를 직접 만들지 않았다. 웹 168곳은 직접 받기로 154곳을 열었다. 막힌 14곳(Reuters 5, war.gov 2, MarketScreener, ftc.gov(직접 받기는 404), ai.meta.com 2, Search Engine Land, TechXplore, TSMC IR PDF)과 스크립트로 그리는 페이지(Artificial Analysis 2, Arena, Barchart, Futu)는 Playwright 로 열었다. TSMC IR PDF 는 Referer 를 붙여 받았다. Playwright 창은 다른 리뷰어와 함께 쓰여 같은 탭이 다른 페이지로 바뀌는 일이 있었다. 그래서 대조는 모두 새 탭을 열어 그 안에서 했다.
- 이번 실행에서 새로 들어오거나 바뀐 근거는 60건이다(새 근거 28, 발췌·위치·주소가 바뀐 근거 32). 이어받은 제목뿐 근거를 원문 발췌로 바꾼 것은 nvidia(004·010·011·012·013·014), alphabet(004·007·009·010), amazon-008, anthropic-011(microsoft 인용), meta(002·004·006·007)다. 모두 바뀐 주소의 원문에서 발췌를 찾았다.

### 발췌 원문 대조(328건)
- 정규화 문자열 일치 175건, 문장부호·표 칸만 다른 일치 49건, "…" 로 나눈 조각이 모두 원문에 있는 것 79건이다.
- 사람이 원문을 보고 맞춘 것은 11건이다.
  - 소제목이나 광고가 사이에 낀 것: EV-alphabet-040(소제목 "Search monopoly"), EV-meta-057("Ad"·소제목 "Usage Climbs, Slowly").
  - 쪽 번호가 문장 가운데 낀 것: EV-tsmc-065(20-F 31쪽 경계).
  - 표 줄이 원문 그대로이고 열 머리글 배치만 다른 것: EV-meta-020, EV-nvidia-054.
  - 차트 값의 순서가 같은 것: EV-anthropic-049 는 58·53·53·53·52·48·46, EV-anthropic-052 는 68·66·64·63·62·62·56·54 이다. 2026-10-12 브라우저로 연 차트에서 같은 순서로 나오고, v4.3.2·Haiku 5.5 변경 기록도 같다.
  - Playwright 본문에서 찾은 것: EV-meta-009(Barchart), EV-nvidia-066(Futu), EV-tsmc-066(1Q26 경영 보고서 2쪽, 둘째 쪽 읽기 순서 텍스트로 대조).
- Playwright 로 연 14건은 모두 찾았다. EV-alphabet-050·meta-008 의 Reuters 원문은 종목 표기 "(GOOGL.O) , opens new tab" 만 빠진 차이다.
- 재현하지 못한 것은 둘이다. EV-amazon-051·EV-microsoft-009(arena.ai/leaderboard/text, 2026-10-02 판)는 페이지가 지금 10-08 판(8,734,330표·414개 모델)이다. 그 판에서 Amazon Nova 최고 순위는 116위(26-02-10, 1426), phi-4 는 318위다. 10-02 판(117위·317위)은 아카이브 사본이 없어 대조하지 못했다. 점수에는 닿지 않는다(다음 실행 과제 6).

### 인용 위치
- 새로 들어오거나 바뀐 근거 60건은 기사 본문 `<p>` 순서로 세어 locator 와 견줬다. 머리 안내·사진 설명 줄을 빼고 세면 문단 번호가 맞는다(예: EV-openai-066 1·3번째, EV-microsoft-040 2·22번째, EV-nvidia-082 5·7번째, EV-alphabet-009 1·2·8번째). EV-nvidia-079 는 "둘째 문단 셋째 문장과 열아홉째 문단" 인데 두 조각의 세는 기준이 한 칸 다르다(점수 무관).
- 공시 근거: EV-alphabet-073 은 Note 10 Commitments, EV-alphabet-074 는 Note 4 Leases(뒤가 Note 5) 자리다. EV-meta-058 은 Note 9 Leases and Contractual Commitments 다. EV-microsoft-044 의 $329.1B 는 Note 13 Leases 마지막 문단(뒤가 NOTE 14)에, 건설·구매 약정은 Item 7 계약상 의무 표(2027·Thereafter·Total 세 열)에 있다. EV-tsmc-073 은 2026-10-08 6-K 다. 모두 locator 와 같다.
- 이어받은 근거 268건은 발췌·위치·주소가 2026-10-09 rejudge 판과 같다. 이번에는 발췌가 원문에 있는지를 다시 확인했고, 문단 번호는 rejudge 리뷰의 대조를 따랐다.

### 줄 사실(468줄)
- 숫자 기계 대조로 줄의 숫자가 발췌에 없는 82줄을 뽑았고, 모두 사람이 원문과 맞췄다. 대부분은 단위 환산(억·만), 날짜 표기, 계산 표시가 붙은 값이다. 새로 쓰인 109줄은 발췌와 한 줄씩 읽었다.
- 다시 계산한 값은 다음과 같다.
  - alphabet ③: Gemini 앱 월간 사용자 6.5억(2025-10-29) → 7.5억(2026-02-04) → 9억(2026-05-19) → 9.5억(2026-07-22). 월 복리로 4.4%·5.3%·2.6% 이고, 줄이 적은 약 4.5%·5.5%·2.6% 와 반올림 범위에서 맞는다. 구간 성장률은 20%·5.6% 다.
  - ⑧ 약정 배수:
    - alphabet (707.0 + 85.2 + 5.8) ÷ 445.866 = 1.790
    - microsoft (329.1 + 194.060 + 34.566) ÷ 331.839 = 1.681, 2027 회계연도 몫을 빼면 1.081
    - meta (278.99 + 349.31) ÷ 228.247 = 2.753, 2026·2027년 몫 135.17 을 빼면 2.16, 7월 리스 $68B 를 더하면 3.05
    - amazon 267.279 ÷ 775.680 = 0.345
  - ⑧ 분모: alphabet 매출 402,836 − 186,662 + 229,692 = 445,866 이다. meta 매출 228,247 은 상반기 89,830·117,111 을 8-K 에서 확인했다. microsoft 10-K Total revenue 는 331,839 다.
  - 요일: Google–국방부 계약 개정 "Monday" = 2026-04-27, Brinkema 판결 "Wednesday" = 2026-09-02, Apple Siri 합의 "Tuesday" = 2026-05-05, 노동부 정지 "Thursday" = 2026-10-08 이다. 기사 발행일과 맞는다.
  - TSMC 9월 매출 NT$511.86B(+54.6%), 1~9월 누계 NT$3,898.73B, 3분기 합 약 NT$1조 4,942억(TRG-017)이 맞다.
- 원문과 다른 줄·판정 문장은 FINDINGS F1~F3 과 다음 실행 과제 1·2·3 에 적었다.

### 새로 들어온 사실
- ⑧ 약정 축 공시 근거 넷(EV-alphabet-073·074, EV-microsoft-044, EV-meta-058)의 금액과 위치는 원문과 같다. 매출 분모(최근 1년)도 공시와 맞는다. 다만 alphabet 은 분자의 범위가 다른 두 회사와 다르다(F1).
- TSMC·Alibaba 2026-10-09 시가총액 관측을 2026-10-12 yfinance 로 다시 받았다. TSM 종가 453.31 × ADR 환산 주식 수 5,186,474,013 = $2,351,080,522,171, BABA 종가 111.37 × ADS 환산 주식 수 2,487,744,939 = $277,060,160,689 로 관측값과 같다. 10-05·10-07 종가(485.80·472.20, 110.80·107.00)도 같다. results.json 은 열한 상장사 모두 2026-10-09 시총 관측을 쓰고, 이는 `run.price_as_of` 와 맞는다.

### 부재 주장과 결측 라벨
- 맡은 회사 관측에 `not_disclosed_confirmed` 는 없다. `not_disclosed` 9건은 모두 `missing_type: unverified` 이고 note 가 "우리가 확인하지 않았다/못했다" 로 적혀 있어 미공시와 섞이지 않는다. 최대 고객 비중 `not_applicable` 네 건은 발행사 문장 위치나(alphabet·microsoft·meta) 공시 의무에서 나온 추론(apple)을 적었다.
- 판정 칸의 "미확인" 문장 64개 가운데 열 수 있는 원문을 판단이 쓰지 않은 것이 넷이다(F2·F3, 다음 실행 과제 2·4). 나머지는 공시 부재 주장(Prime 회원 수, Alexa+ 유료 이용자, 대만 밖 생산 비중 등)이거나 시계열 부재여서 같은 원문 범위에서 반대 사실을 찾지 못했다. "제목만" 을 사유로 쓴 판정 문장은 없다.

### 트리거
- 맡은 일곱 회사 트리거는 36건이다(이어받은 31, 새 트리거 5: TRG-102~106). 이어받은 31건 모두 carry(ref, checked_at 2026-10-12, finding)가 있다. 기한이 기준일 이전인 watching·withdrawn 은 없다. 직전 실행에서 발동(TRG-001·004·014·043·053)하거나 철회(TRG-051)된 트리거는 닫혀 이어받지 않았다.
- research.md 「이전 트리거 처리」 표의 맡은 회사 31행은 발동 1(TRG-002)과 계속 관찰 30이다. TRG-002 의 finding(Brinkema 판사 2026-09-02 AdX 매각 거부·행위 처분, 폴란드 UOKiK 조사, 영국 경쟁항소법원 2026-10-06 개시, 핀란드 공사 중지)은 원문과 같다. 「발동 트리거 재검토 대상」 표의 맡은 회사 행은 TRG-002 하나이고 "이번 실행에서 수정함" 이다.
- 관찰 30행의 finding 가운데 TRG-007·008·009·013·015·017·020·081·082·083·086·087·091 을 원문과 견줬다. 조건의 사건(TSMC 3분기 실적 10-15, Microsoft FY27 1분기 10-28, Alphabet·Apple 3분기 실적, NVIDIA 10-Q 11월)은 모두 정보 마감 뒤라, 사건이 있었는데 관찰로 남긴 경우는 찾지 못했다. TRG-013 의 체포(10-01)와 유죄 인정(10-09)은 제3자 사건이라 조건(중국 당국의 구매 허용·의회 조항 확정)에 닿지 않는다.

### 초안과 금지 표현
- draft.md 와 맡은 회사 근거의 relevance·conditional_impact·excerpt 에 매수·매도 권유, 목표 주가, 수익 보장, 조급함을 부추기는 표현이 없다. draft 끝에 투자 자문이 아니라는 고지가 있다. 이해상충 표기는 점검하지 않았다(AGENTS.md 「금지·주의」).

## FINDINGS

### F1 · needs_fix · alphabet ⑧ 약정 축의 분자 범위(−2 → −3)
- **판단 문장.** alphabet.F8 판정 칸은 "같은 10-Q 경영진 논의의 구매 약정 총액 $811.0B 는 1년 안에 끝나는 $200.7B(주문서 포함)까지 더한 값이고, 같은 제출본 안에서 값이 갈리면 재무제표 주석을 앞세우므로 주석 값으로 잰다" 고 적는다.
- **원문(goog-20260630 10-Q).**
  - Note 10 의 $707.0B 는 "contracts with remaining terms greater than one year" 의 고정·보장 약정이다.
  - MD&A 의 $811.0B 는 장기 공급 계약과 open purchase orders 를 담은 "material purchase commitments and other contractual obligations" 이고, 그 가운데 $200.7B 가 short-term 이다. 같은 절(54쪽)은 "For agreements with variable terms, we do not estimate the non-cancelable obligation beyond any minimum quantities" 라고 적어, 이 총액이 해지할 수 없는 의무의 합계임을 밝힌다.
  - 두 값은 같은 양을 다르게 적은 것이 아니라 범위가 다르다. 그러니 "감사 재무제표 본문 우선" 규율이 적용되는 자리가 아니다. "$200.7B 가 1년 안에 끝나는 계약" 이라는 표현도 원문과 다르다. 원문의 short-term 은 1년 안에 갚을 몫이고, 총액에서 주석 값을 뺀 몫은 $104.0B 다.
- **다른 회사와의 대조.** Meta 는 "non-cancelable contractual commitments, comprising both short-term and long-term arrangements" $349.31B 전부를 분자에 넣었다. Microsoft 는 "open purchase orders and take-or-pay contracts" 를 담은 구매 약정 $194.06B 전부를 넣었다. 같은 범위(1년 이하 계약과 구매 주문 포함)로 알파벳을 재면 (811.0 + 85.2 + 5.8) ÷ 445.866 = 2.023배로 "2배 이상 20배 미만" 의 −3 이다. Microsoft 는 어느 범위로 재도 −2, Meta 는 어느 범위로 재도 −3 이라, 범위 선택이 점수를 가르는 회사는 알파벳 하나다.
- **고칠 것.** alphabet.F8 의 약정 축 분자를 MD&A 총액 $811.0B 로 바꾸고 내릴 근거 첫 줄과 판정 문장을 다시 쓴다. MD&A 의 $811.0B 문장과 54쪽 해지 불가 문장을 발췌한 새 근거를 확정해 인용한다. 그러면 ⑧ 이 −3, 알파벳 조정총점이 13 → 12 다. 재무 계산 영역(financial-calc.md)이 같은 계산을 냈다. 규칙 일관성 영역은 세 회사에 같은 범위를 댔는지 확인해 주기 바란다.

### F2 · needs_fix · microsoft ⑦ 가로축(작음 → 큼, −1 → −2)
- **판단 문장.** microsoft.F7 판정 칸은 "OpenAI 가 Azure 를 추가로 사기로 한 약정의 금액·기간은 원문을 이 실행의 확정 근거로 갖추지 못해 분자에 넣지 않았다(미확인)" 고 적고, 실제 매출 7.3% 와 Anthropic $30B 상한 16.3% 로 가로축을 작음으로 둔다.
- **열리는 원문은 둘이다.**
  - 회사 1차 발표. `https://blogs.microsoft.com/blog/2025/10/28/the-next-chapter-of-the-microsoft-openai-partnership/` 가 2026-10-12 열리고 "OpenAI has committed to purchase an additional $250 billion in Azure services" 가 있다. 기간은 적혀 있지 않다.
  - 이미 등록된 출처. EV-microsoft-031 의 출처(FY26 2분기 실적 콜, microsoft.com investor)에 "Approximately 45% of our commercial RPO balance is from OpenAI" 와 "previously announced large Azure commitment from OpenAI that reflects multi-year demand needs" 가 있다. 당시 commercial RPO 는 $625B 이고 가중평균 잔여 기간은 약 2.5년이다.
  - EV-microsoft-005·010 의 출처(FY26 4분기 콜)는 6-30 RPO $678B, 가중평균 2.3년, "RPO increased 25% when excluding OpenAI" 를 적는다.
- **점수 영향.** 이 실행이 Anthropic $30B 와 Amazon 의 OpenAI $38B 에 댄 "기간이 적히지 않은 약정은 한 해에 다 넣은 상한" 을 그대로 대면 (24.1 + 30 + 250) ÷ 331.8 = 92% 다. RPO 몫을 잔여 기간으로 나눠 연환산하는 보수적 읽기로도 약 $281B ÷ 2.3년 ≈ $122B, 매출의 37% 다. 어느 쪽이든 "확인된 몫이 매출에 견줘 작다" 고 할 수 없다. 가로축이 큼이면 ⑦ 매트릭스 large|yes = −2 로 Microsoft 조정총점이 14 → 13 이 되고 단독 1위가 Amazon 으로 바뀐다. 규칙 일관성 영역(rule-consistency.md N1)이 같은 결론을 냈다.
- **고칠 것.** 위 두 원문의 문장을 발췌한 근거를 확정해 microsoft.F7 내릴 근거에 더하고, 판정 칸의 미확인 문장을 지우고 가로축을 다시 판정한다.

### F3 · needs_fix · microsoft ⑧ 고객 축(−2 유지 또는 −3)
- **판단 문장.** microsoft.F8 판정 칸은 "OpenAI 가 상업 RPO $678B 에서 차지하는 비중은 확정 근거로 확인하지 못했다(미확인). 그 몫의 연환산이 매출의 10% 를 넘는 것으로 확인되면 고객 축을 다시 잰다" 고 적는다.
- **원문.** 같은 회사 1차 발표(FY26 2분기 콜, 이미 등록된 출처)에 2025-12-31 기준 OpenAI 비중 약 45%(약 $281B)가 있다. FY26 4분기 콜은 그 뒤 RPO 증가가 모두 프론티어 모델 회사 밖에서 왔다고 적어, 6-30 의 OpenAI 몫이 그 수준을 넘지 않음을 보여 준다.
- **점수 영향.** 연환산하면 잔여 기간 2.3년 기준 약 37%, "12개월 안에 30% 인식" 비율 기준 약 25% 로 둘 다 10% 를 넘는다. 고객 축은 −2(10~30%)나 −3(30% 이상)이다. ⑧ 이 지금 −2 라 −3 이면 점수가 바뀐다. 사다리는 "한 고객의 연환산 계약액 ÷ 최근 1년 매출" 을 요구하고, 기간이 없는 계약을 어떻게 연환산할지는 규칙 일관성 영역이 정한다.
- **고칠 것.** 판정 칸의 미확인 문장을 원문 수치로 바꾸고, 고객 축을 재어 ⑧ 을 다시 판정한다.

## 다음 실행 과제

1. meta.F5 내릴 근거 "뉴멕시코 배심원은 2026-03-24 Meta 에 민사벌금 $375M 을 명령했고, 주 정부는 $35~40B 의 벌금을 판사에게 요구했으며 … [EV-meta-027, EV-meta-009, EV-meta-026]" 는 두 금액을 한 사건처럼 잇는다. 10-Q(EV-meta-027)의 $375M 은 미성년자 관련 소송의 배심 평결이다. Barchart(EV-meta-009) 원문은 $35~40B 요구가 2021년 제기된 Cambridge Analytica 계열 소비자보호(데이터 프라이버시 진술) 사건의 평결 뒤라고 적는다. 두 사건을 나누어 쓰거나, 원문끼리 엇갈린다는 사실을 판정 칸에 적는다. 두 사건 모두 비용형이라 점수는 그대로다.
2. microsoft.F5 판정 칸 "마이크로소프트의 Anthropic 지분 투자는 확정 근거로 확인하지 못했다(미확인)" 는 열리는 원문과 다르다. 같은 실행의 확정 근거 EV-microsoft-015 의 출처(2025-11-18 블로그)는 "NVIDIA and Microsoft are committing to invest up to $10 billion and up to $5 billion respectively in Anthropic" 이라 적는다. EV-microsoft-005·010 의 출처(FY26 4분기 콜)는 "$3.2 billion gain from our investment in Anthropic" 을 적는다. 판정 칸을 원문대로 고친다. 동맹 등급은 이미 경쟁사 편입 조항으로 +2 라 점수는 그대로다(규칙 일관성 영역 미확인 방향표와 같은 결론). 이 항목은 미확인 처리 규율의 fail 이다.
3. alphabet.F8 판정 칸의 "$811.0B 는 1년 안에 끝나는 $200.7B(주문서 포함)까지 더한 값" 은 F1 을 고치면서 원문 표현("of which $200.7 billion was short-term", 총액과 주석 값의 차이 $104.0B)으로 다시 쓴다.
4. nvidia.F5 판정 칸 "Anthropic 은 NVIDIA 와 직접 맺은 다년 약정이 확정 근거로 확인되지 않고" 는 원문과 엇갈릴 여지가 있다. 2025-11-18 3사 발표(EV-microsoft-015·EV-anthropic-030 출처)는 NVIDIA 가 Anthropic 에 최대 $10B 를 투자하기로 했고, Anthropic 의 컴퓨트 약정이 처음에는 NVIDIA Grace Blackwell·Vera Rubin 시스템 최대 1GW 라고 적는다. 다만 그 약정이 Azure 를 거치는지 NVIDIA 와 직접 맺은 것인지는 문안에 없다. 판정 칸에 이 발표를 적고 "직접 약정인지 미확인" 으로 좁힌다. 동맹 등급은 CoreWeave·Nebius 로 이미 +2 라 점수는 그대로다.
5. NVIDIA 10-Q Note 10 에는 약정 표($366B) 밖에 "Additional Commitments" 표(AI 클라우드 계약 $36B, 제3자용 미개시 데이터센터 리스 $20B, 합계 $56B)가 따로 있다. nvidia.F8 약정 축은 $366B 만 세어 1.2배다. $56B 를 더하면 422 ÷ 303.0 = 1.39배로 같은 −2 이고, ⑧ 은 다른 축의 −4 가 정한다. 넣을지 뺄지와 그 이유를 판정 칸에 적는다.
6. EV-amazon-051·EV-microsoft-009 는 Arena 순위표의 2026-10-02 판을 인용한다. 같은 주소가 지금은 10-08 판(Amazon Nova 최고 116위, phi-4 318위)이라 인용한 값을 다시 볼 수 없다. 다음 실행부터는 정보 마감에 가장 가까운 판을 쓰고 열람 시각을 적거나, 열람한 판을 보존본으로 남긴다.
7. EV-nvidia-079 locator 의 두 조각("둘째 문단 셋째 문장", "열아홉째 문단")은 세는 기준이 한 칸 다르다. 같은 기준(머리 안내 제외)으로 맞춘다.
8. meta.F3 올릴 근거 "Muse 는 미국 출시 3주 만에 주간 이용자 300만 명을 넘었다" 는 원문(EV-meta-004)의 "주 1회 이상 프롬프트를 보내는 사람 300만 명 이상, 어떤 식으로든 쓰는 사람 400만 명 이상" 가운데 앞의 정의다. "주간 프롬프트 사용자" 로 맞춘다.
9. TRG-015 finding 은 SiliconANGLE 을 인용해 Hugging Face 인수 합의일을 "9-03" 으로 적었다. NVIDIA 8-K(EV-nvidia-009)는 2026-09-02 다. 공시 날짜로 맞춘다.

## CHECKLIST

사실·출처에 닿는 Q 만 적는다. 나머지는 규칙 일관성 영역이 채운다.

| ID | 결과 | 근거 |
| --- | --- | --- |
| Q02 | pass | 맡은 회사의 ① 가격 실측 지표(alphabet CPC·유료 클릭, amazon Prime 정가·구독 매출, microsoft 정가 인상·좌석, meta 광고당 가격, tsmc 선수금·총마진 사유)와 ③ 가속도 지표(alphabet d Gemini 앱 월간 사용자, microsoft b Copilot 좌석, tsmc b HPC, meta e)가 근거 원문의 정의와 맞는다. 성장률을 원문 값으로 다시 계산했다. |
| Q03 | fail | 사실·출처에서 본 같은 잣대 문제는 둘이다. ⑧ 약정 축 분자의 범위가 alphabet(1년 넘는 계약만)과 microsoft·meta(구매 주문·단기 포함)에서 다르다(F1). 기간이 적히지 않은 OpenAI 약정을 amazon ⑦ 은 한 해 상한으로 넣고 microsoft ⑦ 은 원문이 열리는데 넣지 않았다(F2). |
| Q05 | pass | 결과 칸만 채운다. 판단의 결정적 사실은 공시·회사 1차 발표가 중심이고, 공매도 측 자료(EV-meta-057)와 유출 신청서 보도(EV-spacex-xai-043)는 줄에 그 성격을 적고 판정에 쓰지 않았다. 이해상충 표기는 점검 대상이 아니다. |
| Q09 | pass | 계획·발표(Baltra 2027 배치, Hugging Face 인수 종결 전, AMD MI450 대량 출하 2027, Meta Enterprise Platform 출범, Amazon 칩 매각·재임차 추진)는 줄마다 "계획이라 점수에 넣지 않는다" 를 달았고 원문의 단계와 맞는다. |

## 열지 못한 원문

- 없다. 모든 출처 주소를 열었다. 다만 Arena 순위표(EV-amazon-051·EV-microsoft-009)는 인용한 2026-10-02 판을 지금 페이지에서 볼 수 없어 그 판의 값은 대조하지 못했다(다음 실행 과제 6).
