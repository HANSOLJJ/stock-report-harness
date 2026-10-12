---
reviewer_agent: fact-checker
session: fs-b-recheck-20261012-r1
reviewed_at: 2026-10-12
round: 1
---
# fact-sources-b — 사실·출처 (oracle, palantir, anthropic, openai, alibaba, tesla, spacex-xai)
검토자: Claude Opus 5.5 (claude-opus-5-5) · 사실·출처 독립 세션 b(이 실행을 만든 세션 아님) · 2026-10-12
결과: pass
요약: 맡은 일곱 회사의 정성 판단 49건(①②③④⑤⑦⑧, 모두 `status: new`)에서 올릴·내릴 근거 453줄을 전부 봤다. 이 가운데 116줄이 이전 실행(ai-scorecard-2026-10-rejudge)에 없던 줄이다. 줄마다 표지가 있고, 표지가 가리키는 근거 312건은 모두 evidence.json 에 있다. 312건 모두 `confirmed` 이고 reviewer·reviewed_at·locator 를 갖췄다. 발췌는 모두 제목과 다르고 600자 이하이며, 출처는 sources.json 에 등록돼 있고 URL 이 http(s) 다. 근거 312건 가운데 새 근거는 30건, 발췌·인용 위치·URL 이 바뀐 근거는 38건이다. 이 68건은 원문을 열어 모두 대조했다. 나머지 244건은 이전 실행과 글자가 같고, 이번에 원문을 다시 받아 기계로 대조했다. 원문에서 발췌를 찾지 못한 근거는 없다. 다만 EV-palantir-028(FT 본문)은 오늘 구독 장벽에 막혀 다시 확인하지 못했다. 새 사실(OpenAI 연환산 매출 두 정의, 월 매출 $2B, Cursor 계약 정리, 비상장 재무 관측 10건, Anthropic 2분기 영업이익 전환, Palantir ⑤ 새 근거, Tesla 신용한도 8-K)은 값·문언·인용 위치가 원문과 맞는다. 줄에 적힌 계산도 모두 재현된다. 판정 칸이 미확인으로 둔 보도 한 건(palantir.F5 프랑스·독일 계약 중단)은 이미 확정한 근거의 원문 안에 실려 있다. 판단이 이를 쓰지 않았으므로 이 항목은 fail 이다. 다만 다발형은 최대 파트너와의 긴장을 따로 요구하므로 이 보도를 써도 점수는 바뀌지 않는다. 점수·순위·체크리스트 판정을 바꾸는 발견은 없다. 다음 실행 과제는 9건이다.

검토 기준: results_hash `5d0c5181750beeea…`, draft_hash `35c6a4c454044ca4…`(review.md frontmatter 값).

## RESULT

pass — 맡은 일곱 회사의 핵심 사실은 모두 출처까지 거슬러 확인된다. fail 한 건(아래 FINDINGS 1)과 다음 실행 과제 9건은 모두 점수·순위·체크리스트 판정에 닿지 않는다.

## 확인한 것

### 범위와 기계 점검
- 판단 49건, 올릴·내릴 근거 453줄을 봤다. 모든 줄 끝에 `[EV-…]` 가 있고, 표지는 모두 그 판단의 `evidence_ids` 에 들어 있다. `counter_evidence` 는 49건 모두 비어 있다.
- 근거 312건은 모두 confirmed 이고 reviewer·reviewed_at·locator 를 갖췄다. excerpt 는 제목과 다르고 600자 이하다. source_id 는 모두 sources.json 에 있고 URL 은 http(s) 다(`source_ids ⊆ sources`).
- `published_at_utc` 는 311건이 정보 마감(2026-10-12) 이하다. EV-tesla-008 은 비어 있다(이전 실행부터 이어진 상태, 다음 실행 과제 1).
- 트리거: 맡은 회사의 트리거 42건(이어받은 36건, 새로 만든 6건 TRG-107~112)은 모두 `watching` 이다. `evidence_ids`·`source_ids` 는 모두 등록돼 있다. 기한이 지난 `watching` 은 없다. 이전 트리거 36건의 carry finding 이 적은 사건을 근거·원문과 맞춰 봤다. 조건이 섰는데 `fired` 로 처리하지 않은 트리거는 없다. 예를 들어 TRG-031 의 EU 표결은 10-06 에 열리지 않았고(EV-tesla-060), TRG-036 은 EDGAR 에 공개 S-1 이 없으며, TRG-039 의 라운드는 아직 마감되지 않았다(Bloomberg 10-09). 일곱 트리거(TRG-022·025·029·031·036·037·038)는 인용한 근거의 출처가 트리거 자신의 `source_ids` 에 빠져 있다. 그 출처도 sources.json 에는 등록돼 있다(다음 실행 과제 5).
- 원문 받기
  - SEC: 근거·관측이 가리키는 SEC 주소 102건은 모두 `data/_sec/docs/` 캐시에서 읽었다. 새 SEC 요청은 보내지 않았다. SEC 요청이나 User-Agent 는 직접 만들지 않았다.
  - 웹: 일반 브라우저 헤더로 받았다. 막힌 23개 주소(Reuters·Axios·WSJ·FT·Bloomberg·openai.com·help.openai.com·Security Boulevard·Business Wire·war.gov·AT&T·ai.google.dev)는 Playwright 로 열었다.
  - PDF 두 건(JPML 이송 결정, NHTSA ODI Resume)은 pdftotext 로 대조했다.
  - Axios 세 건(EV-anthropic-064·069, EV-openai-002)은 본문 일부가 화면 텍스트에서 가려진다. 'By the numbers'·'State of play'·'Yes, but' 문단은 접근성 스냅숏에서 찾았다.
  - FT 부제 세 건(EV-openai-010, EV-palantir-004·011)은 페이지 `og:description` 에서 글자 그대로 찾았다.
  - Google 뉴스 중계 주소는 `resolve-urls --url` 로 세 건을 풀었다. Bloomberg 10-09 'Black Box', FXLeaders 10-10, Memeburn 10-06 이다.
- 발췌 대조 결과(312건)
  - 정규화 문자열이 그대로 맞은 것: 207건.
  - 나머지 105건은 형식 차이로 조각 단위로 대조했다. SEC 표 칸, 문단 사이 줄바꿈, Reuters 전재본의 보이지 않는 문자, '(NASDAQ: AMZN)' 의 띄어쓰기, 페이지 안 JSON(EV-openai-051) 같은 차이다. 표 발췌 14건은 칸 순서대로 다시 찾았다. EV-spacex-xai-024·050 은 같은 10-Q 의 MD&A AI·Connectivity 표에서, EV-tesla-008 은 같은 제출본의 Exhibit 99.1 에서 찾았다.
  - 자바스크립트로 그리는 차트 근거 8건(EV-anthropic-049·050·051·052·053·055·057, EV-amazon-051)은 평문 받기로는 조각만 맞았다. 발췌·locator·URL 이 이전 실행과 같고, 2026-10-09 리뷰가 Playwright 렌더링으로 대조한 근거라 이번에는 다시 렌더링하지 않았다(열지 못한 원문 목록에 적음).
- 원장·초안: draft.md 「종합 순위표」의 일곱 회사 점수·순위는 results.json `ranking` 과 같다. Oracle 7위 6, Alibaba·Tesla 8위 5, SpaceX + xAI·Palantir 10위 4, Anthropic 12위 1, OpenAI 13위 0 이다. draft 에는 매수·매도 권유, 목표 주가, 수익 보장, 조급함을 부추기는 표현이 없고, 끝에 투자 자문이 아니라는 고지가 있다. 'BNP Paribas maintains a $420 price target' 은 알파벳 출처 목록에 실린 기사 제목이고 맡은 회사가 아니다.

### 이번 실행에서 새로 들어온 사실
- **OpenAI 연환산 매출의 정의**
  - Axios 09-29(EV-openai-002)는 '$70B 근접'과 '3분기 초 대비 70% 초과'를 적었다.
  - TechCrunch 10-08(EV-openai-064, FT 인용)은 회사가 투자자에게 알린 값을 'approaching $50 billion' 으로 적었다. 같은 기사는 $70B 가 투자자들이 Anthropic 과 바로 견주려고 만든 값이고, Anthropic 은 클라우드 파트너 판매를 매출에 넣는다고 적었다.
  - Axios 10-08(EV-anthropic-064)은 OpenAI 가 'records only its share of certain partner sales' 라고 적었다.
  - Bloomberg 10-09 전재본(EV-openai-065)은 9월 말 약 $50B 를 적었다.
  - 판단 문장과 `openai.arr.2026-09-30.recheck` 의 정의 메모는 이 원문들과 맞는다. FXLeaders 제목의 'OpenAI Clarifies' 는 본문을 보면 FT 보도다. 회사 1차 성명이 아니므로 2차 보도 등급은 맞다.
- **OpenAI 월 매출 $2B(EV-openai-071)**: 조달 발표문 본문에서 'We are now generating $2B in revenue per month.' 를 글자 그대로 찾았다. 같은 문단에서 'By the end of 2024 we were generating $1B per quarter.' 도 확인했다. 연환산 $24B 는 ×12 계산이다.
- **OpenAI 의 Cursor 계약 정리(EV-openai-070)**: wccftech 본문에 OpenAI 블로그 인용 블록이 글자 그대로 있다('proposed shutoff date of November 12, 2026', 'maximum notice provided by our contract'). 같은 날 CNBC(EV-spacex-xai-049)는 Cursor CEO 의 '약 5%' 발언을 전한다. 2026-08-29 이후 원문 창 안에 차단이 앞당겨지거나 철회됐다는 보도는 없다. 차단은 기준일 뒤의 일이라 점수에 넣지 않은 처리(규칙 2.1)도 원문과 맞는다.
- **비상장 재무 관측 10건**(as_of 가 가장 늦은 verified 값)은 raw 문장을 모두 원문에서 찾았다.
  - Anthropic 기업가치 $965B·직전 런레이트 $47B: Series H 발표문, 회사 1차 발표.
  - OpenAI 기업가치 $852B·직전 값 $24B: 조달 발표문, 회사 1차 발표.
  - Anthropic 연환산 $65B: CNBC 08-17, 관계자 셋, 2차 보도.
  - OpenAI 연환산 $50B: Bloomberg 10-09, 2차 보도.
  - 누적 조달 $144B·$185B: Pinggy 집계 'Total raised: ~$144 billion'·'~$180-190 billion', 2차.
  - ps_ratio 두 건의 입력도 원문에서 찾았다. 1분기 매출 $4.8B(Investing.com 전재 WSJ), 2분기 $11.6B·$11.5B·$6.7B·$5.7B(The Next Web·The Decoder), 2025년 하반기 범위(Series F 발표문 '2025년 초 약 $1B, 8월 $5B 초과', Series G 발표문 '$14 billion')다.
  - 산식을 다시 계산했다. 965/23.40 = 41.24, 965/18.47 = 52.25(관측 52.26 은 18.467 기준 반올림), 852/24.4 = 34.92, 852/14.4 = 59.17.
  - 유출 문서 수치(2025년 매출 $4.6B·$13B)는 `not_used` 로 빠져 있다.
  - Anthropic 7월 말 $65B 가 2026-10-12 까지 가장 최근 값이라는 메모는 Bloomberg 10-09 'Black Box' 기사 본문('Anthropic, meanwhile, hit $65 billion in annualized revenue in July')과 맞는다.
- **Anthropic 2분기 영업이익 전환(EV-anthropic-065)**: The Next Web 이 WSJ 를 인용해 'Anthropic also swung to a small operating profit' 과 '조정 이익 산정 불분명·주식보상비 제외 전력' 을 적었다. Axios 10-08 도 FT 를 인용해 주식보상비를 뺀 영업이익이라고 적어 정황이 맞는다. 판단은 이를 2차 보도로 적었고, 유출 초안 수치는 쓰지 않았다.
- **Palantir ⑤ 새 근거**: Mopac 의 계약 차단과 Palantir 의 소송(BBC 10-10, EV-palantir-035), 버넘 총리 압박·£330m·£427m(Guardian 10-09, EV-palantir-039), ICE VSPTS 의 Foundry 전환(Biometric Update, EV-palantir-036), WIRED 의 ELITE 보도(EV-palantir-034), CBS 녹취록 두 건(EV-palantir-037·038)은 모두 발췌가 원문에 있다. 줄의 숫자·날짜·주체도 맞는다(£427m×1.33 ÷ $4,475M ≈ 12.7%).
- **Tesla 신용한도 8-K(2026-09-29)**: 캐시 원문에서 확인했다. 세 한도 $20.0B·$8.0B·$2.0B, 2026-09-29 인출 잔액 0, 지연인출 대출의 1주년 $10.0B·15개월 $5.0B 감액과 18개월 소멸, 연결 유동성 $5.0B 유지 약정, Item 1.02 기존 회전여신 종료가 모두 관측 note 그대로다.

### 회사별 줄 사실과 계산
- 회사별 근거 수의 합(353)은 여러 회사가 같은 근거를 함께 인용해 고유 근거 312건보다 크다.
- **openai(판단 7건, 74줄, 근거 69건)**
  - ③ 월 복리 성장률을 다시 계산했다. (50/25)^(30.44/153) − 1 = 14.8%, (50/24)^(30.44/183) − 1 = 13.0%, (40/25)^(30.44/107) − 1 = 14.3%, (50/40)^(30.44/46) − 1 = 15.9%, 6.7/5.7 = 17.5%(보도 '18 percent')다.
  - ⑧: 1.4T/50B = 28배, 1.4T/70B = 20배, (38+100)/50 = 2.76배, (38+100+300)/50 = 8.76배.
  - ⑤: AT&T(Playwright), USA TODAY 제소 $250M 초과(RuntimeWire), Microsoft-Decision-1 의 Qwen3.5-9B 후학습(The New Stack), FTC 정식 자료 요구 준비(Bloomberg Law)가 원문과 맞는다.
  - ① Plus 월 $20 은 Help Center 셋째 문단에서 찾았다.
- **anthropic(판단 7건, 84줄, 근거 66건)**
  - ③: (30/9)^(30.44/96) − 1 = 46.5%, (65/30)^(30.44/116) − 1 = 22.5%, 2월 12일 $14B 를 끼우면 36.7%·54.9%, 5월 중순을 끼우면 42%·13.7%, 30→47 은 57%, 47→65 는 38%.
  - ⑧: 공시·회사 1차 약정 $130B 초과 ÷ $65B 는 2배 초과, Google 을 더하면 330/65 = 5.1배, $60B 를 더하면 6.0배, 유출 수치 679.2/65 = 10.4배, 분모 절반이면 330/32.5 = 10.2배.
  - ① Sonnet 5.5 캐시 읽기 $0.20 → $0.10(mixed-news, 릴리스 노트 인용)과 SpaceX 컴퓨트 계약의 90일 해지 조항(S-1/A)이 원문과 맞는다.
  - 유출 초안 수치(47%, 4분의 1, $518B·$161.2B·$42B)는 모두 '보도가 있다' 로만 쓰였다. 등급을 가르는 값으로는 쓰이지 않았다.
- **oracle(판단 7건, 58줄, 근거 39건)**: 최근 1년 매출 67,357 − 14,926 + 19,345 = 71,776, (288 + 34.15)/71.776 = 4.49배, 60/71.776 = 83.6%, 300/664 = 45.2%. 새 근거인 Project Jupiter 가스관(Quartz, EV-oracle-045)과 Apollo·Goldman 칩 금융 협의(Yahoo Finance, EV-oracle-044)도 원문에 있다.
- **palantir(판단 7건, 56줄, 근거 33건)**: 미 정부 매출 1.9/4.475 = 42.5%, 687/1,632.6 = 42.1%, 최근 1년 매출 $6.16B. 새 근거는 위와 같다.
- **alibaba(판단 7건, 50줄, 근거 46건)**: ARC Prize 의 Qwen3.8-27B(XHigh) ARC-AGI-2 42.4% 는 EV-anthropic-053 발췌의 행과 맞는다. 판정 칸의 Cloudflare Clef-flash 는 EV-alibaba-073 과 같은 기사 본문('cloudflare built clef-flash on the same qwen3.5-9b base')에 있다. 이전 실행이 남긴 'ARC 에 알리바바 제품 없음' 서술은 고쳐졌다.
- **tesla(판단 7건, 57줄, 근거 48건)**
  - FSD 1.28/1.10 = 16.4%, 1.48/1.28 = 15.6%. SpaceX 최근 1년 영업손실 2,589 + 2,086 − 943 = 3,732. Tesla 최근 1년 매출 94,827 + 50,623 − 41,831 = 103,619. 0.81/103.6 = 0.8%, 1.272/103.6 = 1.2%.
  - 중국 9월 64,837대 대 71,525대(−9.4%, Benzinga), Cybercab 300대 초과와 텍사스 밖 미출하(Drive Tesla Canada), 독일 교통장관 발언(TechCrunch), EU 표결 미개최·8개국(Electrek), 부당 사망 소송(Stocktwits)이 원문과 맞는다.
- **spacex-xai(판단 7건, 74줄, 근거 52건)**: 최근 1년 매출 18,674 + 12,508 − 8,138 = 23,044, 15/23.044 = 65.1%, 16.8/23.044 = 72.9%, 3.75/23.044 = 16.3%, 11.04/23.044 = 47.9%, 27,955/23,044 = 1.21배. Reflection 의 GB300 임차($6.3B·월 $150M·2029년, SiliconANGLE 의 FT 인용)와 멤피스 가동 중단 보도(Gadget Review)는 원문에 있다. 멤피스 보도는 원 보도와 날짜를 확인하지 못했다는 단서를 줄에 달았다.

### 기준 시점·귀속·부재 주장
- 기준일 뒤 사실을 점수에 넣은 줄은 없다. 해당하는 것은 Cursor 차단 11-12, Tesla Q3 Update 10-21, Zhenwu V900 양산 2027년, Optimus 라인, Broadcom 의 OpenAI 칩 금융 협의, Oracle 칩 금융 협의이고, 모두 계획이나 미래로 표시돼 있다.
- 회사 귀속도 맞다. Microsoft 사내 Claude 축소는 Anthropic ①②⑤⑦ 에, Grok Bot 의 Claude 사용은 Anthropic 쪽 사실로 들어갔다. Starlink V5 는 관계사 자산이라 Tesla ③ 에서 빠졌다.
- 부재 주장도 원문으로 받쳐진다. Anthropic·OpenAI 의 공개 S-1 이 없다는 것은 EDGAR 전문 검색으로(관측 gross_margin_ttm note, TRG-036), Palantir 10% 이상 고객이 없다는 것은 10-Q 로, Oracle FY2024~FY2026 10% 이상 고객이 없다는 것은 10-K Note 1 로 확인된다.
- `not_disclosed`(구조적 미공시)와 미확인이 섞인 자리는 맡은 회사에서 찾지 못했다.

## FINDINGS

1. **fail(점수 불변) — palantir.F5 판정 칸.** '프랑스·독일 정부가 Palantir 계약을 끊었다는 사실은 확정 근거에 없어 미확인이다' 라고 적혀 있다. 그런데 확정 근거 EV-palantir-009 의 원문(SFG Media 2026-10-01, FT 인용)에 다음 문장이 있다. 'in recent months, france and germany have dropped some contracts with palantir or restricted the use of its products in their armed forces and intelligence services'. 원문이 열리는데 판단이 쓰지 않았다. 계약 이름과 시점이 없는 2차 보도이므로, 내릴 근거 칸에 그 등급과 단서를 달아 올려야 한다(같은 근거에 이 문장을 덧붙여 발췌하면 된다). 이 보도를 써도 Palantir ⑤ 는 −2(구조형)에 머문다. 다발형은 최대 파트너인 미 정부와의 긴장을 따로 요구하고, 판단은 그 긴장이 없다고 근거를 들어 적었기 때문이다(ICE VSPTS 의 Foundry 전환, 미 정부 매출 증가). ①·⑧ 판정도 바뀌지 않는다.
2. 그 밖에 점수·순위·체크리스트 판정을 바꾸는 발견은 없다.

## CHECKLIST (사실·출처 영역이 닿는 항목)

| ID | 결과 | 근거 |
| --- | --- | --- |
| Q05 | pass | 맡은 회사 근거의 출처 등급을 줄마다 적었다(회사 1차·공시·2차 보도·유출 초안). 이해상충 표기는 점검 대상이 아니다(AGENTS.md 「금지·주의」). |
| Q09 | pass | Cursor 차단(11-12), Zhenwu V900, Optimus, Terafab, Jalapeño 배치, 칩 금융 협의는 모두 계획이나 기준일 뒤로 표시돼 점수에 들어가지 않았다. |
| Q23 | pass | ARC-AGI-3 Provider Adapter 값과 OpenAI 발표 99.9% 는 표준 하네스와 견주지 않았다. Alibaba HLE 기사 값도 하네스가 달라 빠졌다. |
| 그 밖 | not_applicable | 판정표 대조와 회사를 가로지르는 표 셋은 규칙 일관성 영역이 본다. 이 영역에서는 유출 초안 수치가 등급을 가르는 값으로 쓰이지 않았다는 것만 확인했다(Anthropic ①⑤⑦⑧, OpenAI ⑤⑧). |

## 다음 실행 과제

1. EV-tesla-008 의 `published_at_utc` 가 비어 있다. 8-K 제출일 2026-10-02 를 넣는다(이전 실행부터 이어진 상태).
2. EV-palantir-028(FT 본문, MHCLG 대변인 인용 문단)은 오늘 구독 장벽에 막혀 본문을 다시 확인하지 못했다. 같은 기사의 `og:description` 은 Homes for Ukraine 계약 연장 기사임을 확인해 준다. 열리는 전재본을 찾아 출처를 옮기거나, 본문을 저장해 둔다.
3. **OpenAI ⑦ 세로축.** 판정 칸은 'OpenAI Startup Fund 가 API 고객에 투자하는 구조는 원문을 찾지 못해 미확인' 이라고 적는다. 그런데 TechCrunch 2023-10-11 'Anysphere raises $8M from OpenAI to build an AI-powered IDE' 는 OpenAI Startup Fund 가 Cursor(Anysphere) 시드를 이끌었고 Cursor 가 OpenAI 모델을 쓴다고 적는다. SpaceX 인수 뒤 지분이 어떻게 됐는지 함께 확인해 근거로 올린다. 가로축이 '큼' 이라 세로축은 점수를 가르지 않는다(Oracle ⑦ 판정 문장과 같은 구조).
4. openai.F5 의 Microsoft-Decision-1 줄은 'OpenAI 모델이 아니라 Qwen' 만 적는다. 같은 발췌에 있는 'plans to rebase it soon on its own MAI models as well as OpenAI's' 는 올릴 근거 칸에도 둔다. Microsoft 를 동맹에서 뺀 판정은 Copilot 근거로 따로 서므로 점수는 바뀌지 않는다.
5. 트리거 일곱 건(TRG-022·025·029·031·036·037·038)의 `source_ids` 에 인용 근거의 현재 출처가 빠져 있다. 이번 실행에서 근거의 출처를 원문 주소로 옮긴 결과이고, 해당 출처는 sources.json 에 있다. 트리거의 `source_ids` 를 근거 출처와 맞춘다.
6. EV-openai-070 은 OpenAI 블로그를 인용한 wccftech 기사다. 판단 문장은 회사 성명으로 읽힌다. OpenAI 블로그 원문 주소를 찾아 출처를 회사 1차로 옮긴다.
7. TRG-030 의 carry finding 은 Barron's 10-08 Optimus 기사를 '유료라 제목만 확인' 으로 적는다. 트리거 맥락이라 판단 인용은 아니지만, 열리는 전재본이 있는지 다음 창에서 본다.
8. 자바스크립트 차트 근거 8건(EV-anthropic-049·050·051·052·053·055·057, EV-amazon-051)은 평문 받기로는 조각만 맞는다. 렌더링한 본문 텍스트를 저장해 다음 리뷰가 Playwright 없이도 대조할 수 있게 한다.
9. 이번 창의 Google 뉴스 후보 가운데 Bloomberg 10-09 'Black Box' 기사(Anthropic 7월 $65B 가 최신이라는 서술)는 `anthropic.arr.2026-07-31.recheck` 의 '더 늦은 값 없음' 메모를 받치는 원문이다. 출처로 등록해 메모의 근거를 남긴다.

## 열지 못했거나 다시 렌더링하지 않은 원문

- EV-palantir-028 FT 본문: 구독 장벽(부제·제목만 열림).
- EV-openai-010, EV-palantir-004·011 FT 본문: 구독 장벽. 근거가 부제만 땄고, 부제는 `og:description` 에서 확인했다.
- 자바스크립트 차트 8건: 위 과제 8. 이전 리뷰(2026-10-09)가 Playwright 로 대조했고 이번에는 평문 조각 대조만 했다.
