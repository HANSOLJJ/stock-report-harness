---
reviewer_agent: fact-checker
session: fc-opus55-20261007-rescore-r8c (원문 연결 세션·조율자와 다른 세션, c 묶음 전담)
reviewed_at: 2026-10-07
round: 8
---
# fact-sources-c — 사실·출처 (palantir, spacex-xai, tesla, tsmc)
검토자: Claude Opus 5.5 (claude-opus-5-5) · 사실·출처 독립 세션 c(이 실행을 만든 세션 아님) · 2026-10-07 · 원문 연결 뒤
결과: needs_fix
요약: 맡은 네 회사 판단 32개의 올릴·내릴 근거 103줄을 모두 봤다. 그 줄의 표지 233개가 가리키는 근거는 176건이다. 176건 모두 confirmed 이고 reviewer·reviewed_at·locator·excerpt 가 차 있으며, 출처는 모두 sources.json 에 등록돼 있다. 175건은 출처 원문에서 발췌를 찾았다. 1건(EV-spacex-xai-007, Investor's Business Daily)은 유료벽이라 확인하지 못했다. 그 근거가 받치는 두 줄에는 같은 사실을 받치는 확정 근거(EV-spacex-xai-022)가 함께 붙어 있다. 발행일이 2026-10-06 을 넘는 근거는 없다. 발행일 칸이 비어 있는 근거는 2건이다(EV-tesla-001·008, 문서 날짜는 기준일 이전). 줄의 숫자·날짜·주체는 102줄이 발췌와 맞는다. 최근 1년 합산(tsmc ②③⑨, palantir ③⑨, tesla ⑨, spacex-xai ⑨)은 발췌의 표 값으로 모두 다시 계산했고 판단 값과 같다. needs_fix 는 1건이다. spacex-xai.F2 올릴 근거 넷째 줄(Starship 첫 궤도 비행)이 EV-spacex-xai-009 를 표지로 다는데, 그 발췌는 Google 의 월 $920M 컴퓨트 계약 이야기라 줄의 사실을 받치지 않는다. 점수·순위에는 닿지 않는다. 다음 실행 과제는 10건이다.

검토 기준: results_hash `bacc7bc3e82a981d…`, draft_hash `0148fb46af32d9e8…`(review.md frontmatter 와 같음을 확인했고, draft.md sha256 도 같다). 입력은 judgments.json·evidence/evidence.json·sources.json 의 현재 작업 트리(커밋 `7f684c6` 뒤)다. 대조 스크립트는 세션 스크래치 `fsc/dump.py`·`fsc/match.py`·`fsc/rows.py`·`fsc/loc.py` 다.

## 확인 내용

### 범위와 기계 점검
- **대상 판단**: palantir 8, spacex-xai 8, tesla 8, tsmc 8 이다. 올릴 근거 59줄, 내릴 근거 44줄, 판정 칸 131줄이다. 방향 칸 103줄에는 모두 표지 `[EV-…]` 가 있다. 판정 칸에 표지가 남은 줄은 0이다. 표지가 다른 회사의 근거를 가리키는 줄도 0이다. 판단 `source_ids` 도 모두 sources.json 안에 있다.
- **근거 상태**: 176건 모두 `status: confirmed` 이고 reviewer·reviewed_at 이 있다. 새 판단(`status: new`) tsmc.F5.strict54·tsmc.F9·tesla.F4·spacex-xai.F9.obsreg25 가 인용한 근거도 모두 confirmed 다.
- **발행일**: 174건이 2026-10-06 이하다. 가장 늦은 것은 EV-palantir-022(healthcare-management.uk, 2026-10-06)다. EV-tesla-001(10-Q, 2026-07-23 접수)과 EV-tesla-008(8-K, 2026-10-02 접수)은 `published_at_utc` 가 null 이다. 두 문서의 접수일은 기준일 이전이다(다음 실행 과제 1).
- **원문 받기**: 고유 출처는 85개다. SEC 공시 20개는 `scorecard_cli.py sec-get` 으로 받았다(17개 캐시, 3개 새로 받음). 테슬라 8-K(0001628280-26-064366)는 색인(index.json)과 Exhibit 99.1(`exhibit991111111.htm`)도 sec-get 으로 받았다. 나머지는 urllib 로 받았다. 막힌 3개(businesswire, war.gov, TSMC 4Q25 녹취록 PDF)는 Playwright 새 페이지로 열거나 다시 받았다. Google 뉴스 리다이렉트 13개도 Playwright 새 페이지로 열었다. 연 페이지는 스크립트 끝에서 닫았다. Google 뉴스 리다이렉트 URL 을 쓴 출처 13개는 모두 sources.json `note` 에 "url 은 Google 리다이렉트 링크다" 로 표시돼 있다. 13개 모두 리다이렉트가 기사 원문(simplywall.st, digitimes, FT 둘, Yahoo 둘, Common Dreams, Guardian, WIRED, investors.com, CNBC 둘, TradingKey)으로 풀렸다. TSMC 녹취록 두 PDF 의 sha256 은 sources.json 값과 같다.

### 발췌 원문 대조(기계 대조와 사람 확인)
| 방법 | 건수 | 내용 |
| --- | --- | --- |
| 기계 · 정규화 문자열 일치 | 143 | 따옴표·대시·공백만 정규화했다. 111건은 그대로, 24건은 공백·문장부호만 다르고, 8건은 `…`·`...` 로 자른 조각이 모두 원문에 있다. EV-tesla-008 은 출처 URL(8-K 표지)이 아니라 같은 접수의 Exhibit 99.1 에서 찾았다(다음 실행 과제 2). |
| 기계 · 표 행 대조 | 16 | SEC 표 발췌(칸 구분 세로막대, `$`, 괄호 음수, 점 리더)를 행 이름 + 숫자 열로 나눠 원문 행과 대조했다. palantir 012·014·015·016·017, spacex-xai 010·011·024·033·045·050·053·054·056·058·059 다. 모든 행의 숫자 열이 순서대로 원문 행과 같다. palantir 012·014·015·016 은 사이 행을 건너뛰면서 생략 표시를 달지 않았다(다음 실행 과제 3). |
| Playwright · 화면 본문 대조 | 15 | Google 뉴스 리다이렉트 13건과 EV-palantir-023(businesswire), EV-spacex-xai-036(war.gov)이다. 14건은 원문에 그대로 있다. EV-palantir-004·011(FT)은 부제(standfirst)라 유료벽 앞 화면에서 찾았다. EV-spacex-xai-007(investors.com)은 유료벽 뒤라 본문 3번째 문단을 볼 수 없었다. 서버 HTML 에도 그 문장이 없다. |
| 사람 · 원문 읽기 | 2 | EV-spacex-xai-043(CNBC)은 원문의 "infrastructure" 와 "obligations" 사이에 보이지 않는 낱말 결합 문자(U+2060)가 끼어 있을 뿐 글자는 같다. EV-spacex-xai-055(10-Q)는 "Backlog totaled" 와 "$ 47,461 million" 사이에 쪽 꼬리표 "13 Table of Contents" 가 끼어 있다. locator 도 "p.13 끝~p.14 첫 줄" 로 적었다. |

- **인용 위치**: 쪽 번호가 적힌 근거 39건은 발췌가 나오는 쪽을 기계로 찾아 대조했다. TSMC 녹취록 10건(3·4·5·6·7·14·20쪽), SpaceX 10-Q·S-1/A 25건, NHTSA 조사 문서 1건이 locator 와 맞다. EV-spacex-xai-042 의 S-1/A 문단은 p.14(요약)와 p.147(Business)에 두 번 나오고, locator 는 p.147 이다. 표 발췌 EV-spacex-xai-011·024·050·059 는 표 머리글로 찾았고 각각 p.111·44·43·108 이 맞다. SpaceX 8-K Exhibit 99.1(EV-spacex-xai-019·023·035)은 쪽 꼬리표가 없어 쪽 번호를 대조하지 못했다. 발췌는 원문에 있다. 쪽 번호 없는 SEC locator(항목·주석 이름)와 기사의 "N번째 문단" 은 발췌가 원문에 있는지만 봤다. 문단 순서는 세지 않았다.
- **원문 값 정정**: link/final 의 corrections 30건(palantir 3, spacex-xai 9, tesla 7, tsmc 11) 가운데 줄에 남은 고친 값은 모두 발췌와 맞는다. 예를 들어 palantir.F8 미 정부 매출 $1.9B, spacex-xai.F4 IPO 순조달 약 $85.7B, tsmc.F4 애리조나 $265B(팹 10·첨단 패키징 2), tsmc.F9 가이던스 $52~56B → $60~64B, tesla.F3 Waymo 오스틴 300대 이상·전체 약 4,000대, tesla.F5 NHTSA EA26002 3,203,754대가 그렇다.

### 줄의 사실과 발췌(사람이 읽어 확인)
103줄 모두 줄의 사실과 발췌를 나란히 읽었다. 102줄은 숫자·날짜·주체가 발췌와 맞는다. 다시 계산한 합산은 다음과 같다(단위는 각 공시 표 단위).
- **TSMC**: 최근 1년 매출 NT$4,440,492,429천, 영업이익 NT$2,491,156,024천으로 영업이익률 56.1% 다. 그 전 1년 매출 NT$3,401,198,854천 대비 성장률은 30.6% 다. 영업현금흐름 NT$2,634,679,110천 − 유형자산 취득 NT$1,491,122,744천 = NT$1,143,556,366천이고, 20-F 편의환산율 31.37 로 나누면 $36.45B → +$36.5B 다. 2분기 매출총이익률 67.7%·영업이익률 60.3% 는 6-K 실적 발표문(EV-tsmc-011) 끝 문장에 있다. HPC 밖 34% 는 100 − 66 이다. NVIDIA 19%·Apple 17%·상위 둘 36% 는 20-F(EV-tsmc-040)와 TechPowerUp(EV-tsmc-039)이 같다.
- **Palantir**: 2분기 매출 성장 1,935,464/1,003,697 = +92.8% 다. 최근 1년 매출 $6,155,941천, 그 전 1년 $3,440,587천으로 +78.9% 다. 최근 1년 영업이익 $2,634,652천으로 42.8% 다. 영업현금흐름 $3,400,291천 − 설비투자 $42,019천 = 잉여현금흐름 $3,358,272천이다.
- **Tesla**: 최근 1년 매출 103,619, 영업이익 4,372(4.22%)다. 영업현금흐름 18,685 − 설비투자 12,923 = 5,762 다. 상반기 FCF 352·810, 2분기 FCF −1,092, 영업이익률 1.4% 다. Cortex 205MW 는 >90 + >115 다.
- **SpaceX**: 최근 1년 매출 23,044, 영업손실 3,732(−16.195%), 순손실 8,218 이다. 영업현금흐름 9,900 − 설비투자 42,248 = −32,348 이다. 완충 93,522 + (5,000 − 645) = 97,877 이고, 런웨이는 97,877/32,348 = 3.03년이다. 커버리지는 47,461/(1,627 + 27,955) = 1.604 다. Starlink 영업마진은 2025년 4,423/11,387 = 38.8%, 2026년 2분기 1,656/4,291 = 38.6% 다. 현금 + 시장성 증권은 93,522 + 6,487 = 100,009 다.

맞지 않는 1줄은 아래 발견 1 이다. 받침이 약하거나 분류가 갈릴 수 있는 줄은 「다음 실행 과제」 에 적었다.

### 판정 칸으로 옮긴 "원문을 찾지 못해" 문장
네 회사에 다섯 곳이 있다. tesla.F1 의 전환비용·스노우볼, tesla.F5 의 EU 승인 거부 영향·악동 이미지, tsmc.F8 의 take-or-pay, spacex-xai.F9 의 흑자 전환 목표 후퇴·완충 잠식이다. 이 가운데 spacex-xai.F9 의 '완충 잠식 없음' 은 같은 판단 올릴 근거가 이미 인용한 EV-spacex-xai-033(현금 2025-12-31 US$24,747M → 2026-06-30 US$93,522M)으로 바로 받쳐진다(다음 실행 과제 5). 나머지는 판단 문장이거나, 공시에서 찾을 곳이 마땅치 않다.

### 금지 표현·draft 반영
- 네 회사 판단 문장 234줄(판정 131 + 방향 103)에 매수·매도·목표주가·수익 보장 표현은 0건이다.
- 234줄은 표지를 뗀 문장 그대로 draft.md 에 모두 있다.

## 발견
| 등급 | 위치 | 발견 | 고칠 방향 | 점수 영향 |
| --- | --- | --- | --- | --- |
| needs_fix | judgments.json spacex-xai.F2 · evidence_up[3] "2026-09-28 Starship 이 처음 궤도에 올라 Starlink 위성을 배치했지만, 궤도 데이터센터가 …" · 표지 EV-spacex-xai-009 | EV-spacex-xai-009 의 발췌는 "A June agreement with Alphabet calls for SpaceX to supply AI computing services at about $920 million a month for 32 months …" 다. 줄의 사실(Starship 첫 궤도 비행·Starlink 배치, 궤도 데이터센터 미실현)과 무관하다. 근거의 relevance 와 factors(F7·F8)도 ⑦⑧ 용 근거라고 적는다. 줄의 주된 사실은 같은 줄의 EV-spacex-xai-022 가 받친다. | 표지에서 EV-spacex-xai-009 를 뺀다: `[EV-spacex-xai-022, EV-spacex-xai-007]`. | 없음 |

## 열지 못한 근거
| 근거 | 출처 | 이유 | 같은 줄의 다른 근거 |
| --- | --- | --- | --- |
| EV-spacex-xai-007 | SRC-NEWS-spacex-xai-20260928-504eea45 (investors.com, 리다이렉트 해소됨) | 유료벽이라 화면에는 첫 문단만 나온다. 서버 HTML 에도 발췌 문장이 없다. | spacex-xai.F2 up[3]·F4 up[1] 모두 EV-spacex-xai-022(Satellite Today, 원문 일치)가 같은 사실(26기 Starlink V3 배치, 엔진 문제로 조기 종료)을 받친다. |

## 체크리스트
| ID | 결과(pass/fail/not_applicable) | 근거 |
| --- | --- | --- |
| Q05 | pass | 이해당사자 발표(테슬라 Q2 Update, SpaceX 실적 발표, xAI Colossus 페이지)는 줄에서 회사 발표로 읽히게 적혀 있다. 공시가 아닌 보도는 '보도가 있다'·'보도됐다' 로 적는다(tsmc.F2·F5, tesla.F3·F4, spacex-xai.F4). 이해상충 표기는 AGENTS.md 에 따라 보지 않았다. |
| Q09 | pass | 계획은 같은 줄에 계획이라고 적는다. tsmc.F2 CoWoS 14배 레티클 '(계획)', tsmc.F9 설비투자 가이던스 '계획이라 … 쓰지 않는다', tesla.F2 AI5·Optimus·Terafab '점수에 넣지 않는다', spacex-xai.F2 Colossus 100만 개 '목표라 점수에 넣지 않는다' 가 그렇다. |
| Q14 | pass | 진행 중인 사건은 미완으로 적는다. Starship 14차 '시험 비행 성격', Cybercab '첫 달이 순탄치 않았다', 테슬라 Apple 청구 '자진 취하를 신청했다', EC 벌금 'challenge remains pending' 이 그렇다. |
| Q23 | pass | spacex-xai.F2 Grok 4.6 의 Artificial Analysis Index 61 은 공개 시점(2026-08)과 비교 대상을 원문대로 적었다. 하네스가 다른 수치를 비교한 줄은 없다. |

## 다음 실행 과제
1. (low) EV-tesla-001·EV-tesla-008 과 출처 SRC-EDGAR-000162828026049270·SRC-EDGAR-000162828026064366 의 `published_at_utc` 를 접수일(2026-07-23·2026-10-02)로 채운다. EV-tesla-001 의 `unverified`("원문 미열람", "본문 수치 미확인")는 발췌가 본문 표로 바뀐 지금과 맞지 않으니 비운다.
2. (low) EV-tesla-008 의 발췌는 8-K 표지(`tsla-20261002.htm`)가 아니라 같은 접수의 Exhibit 99.1(`https://www.sec.gov/Archives/edgar/data/1318605/000162828026064366/exhibit991111111.htm`)에 있다. Exhibit 을 출처로 등록하거나 출처 URL 을 바꾼다. 출처 sha256 셋(SRC-SEC-TSM-20F-FY2025, SRC-EDGAR-000162828026049270·064366)은 sec-get 으로 받은 파일의 해시와 다르다. 다시 받은 해시로 맞추거나, 다른 사본의 해시라는 사실을 note 에 적는다(본문은 같다).
3. (low) 표 발췌의 사이 행 생략 표기를 통일한다. palantir 012·014·015·016 은 건너뛴 행 사이에 생략 표시가 없다. spacex-xai 쪽은 `...` 를 단다.
4. (low) 표지 근거의 `factors` 가 인용한 판단 factor 와 다른 곳이 여덟 곳 있다. EV-tsmc-009(tsmc.F5), EV-tsmc-004(tsmc.F8), EV-spacex-xai-007(F2), EV-spacex-xai-009(F2, 발견 1), EV-spacex-xai-013(F4), EV-spacex-xai-040(F5), EV-spacex-xai-011(F9), EV-tesla-007(F4)이다. 근거 메타데이터만 맞추면 된다.
5. (low, 규칙 일관성 영역과 함께) spacex-xai.F9 판정 칸의 "흑자 전환 목표 후퇴와 완충 잠식이 없다는 사실은 … 원문을 찾지 못해 확인하지 못했다" 는 입력(`bep_retreat`·`buffer_erosion` = no)과 결이 다르다. 미확인이면 unknown, 확인이면 no 여야 한다. '완충 잠식 없음' 은 EV-spacex-xai-033(현금 US$24,747M → US$93,522M)으로 받쳐진다. 같은 입력을 tesla.F9 는 "없음이다" 로 적는다. 문장을 근거와 함께 다시 쓴다.
6. (low) tesla.F1 판정 칸의 "차량 소유자에게 전환비용이 있다는 사실은 원문을 찾지 못해" 는 link 출력에서 `score_bearing: true` 로 표시됐다. 같은 판단 올릴 근거의 S&P Global Mobility 충성도 상(EV-tesla-049)은 재구매율이지 전환비용이 아니다. 다음 실행에서 원문을 더 찾거나, ① 2점이 이 사실 없이도 서는지 판정 칸에 적는다.
7. (low, Q03) spacex-xai.F1 up[3] 은 "2026-07-20 부터 Starlink V5 가 Tesla Cybercab 에 공장에서 통합되는" 이라고 적는다(EV-spacex-xai-014, techeblog "factory-installed"). tesla.F3 은 같은 사건을 Electrek(EV-tesla-037) 따라 "양산 사양인지 설계 단계인지는 밝히지 않았다" 로 고쳤다. 두 회사 문장을 같은 사실로 맞춘다. 점수에는 넣지 않는 줄이다.
8. (low) spacex-xai.F8 down[0] 의 '공모 후 합산 의결권 84.4%' 는 S-1/A 주요 주주표의 '옵션 미행사' 칸 값이다. 같은 S-1/A 요약은 82.4%(옵션 전량 행사 시 82.3%, Class B 5,219,053,075주)로 적고, 8-K(EV-spacex-xai-030)는 옵션 전량 행사를 공시했다. 문서 안에서 값이 갈린다는 사실과 고른 칸을 줄이나 판정 칸에 적는다. ⑧ −3 에는 닿지 않는다.
9. (low, 분류) 받침이 약한 방향 칸 줄이다. spacex-xai.F1 up[1] "X 는 페이스북형 네트워크다"(EV-spacex-xai-012 는 경쟁 SNS 목록), spacex-xai.F1 down[0] "Starlink 에는 사용자끼리 연결되는 구조가 없다"(부재 주장, EV-spacex-xai-015 는 서비스 회선 정의), tesla.F3 up[1] "차량 판매 이익이 AI 를 대고 있다"(EV-tesla-029 는 영업이익 감소 서술)다. 판정 칸으로 옮기거나 발췌를 바꾼다.
10. (low) round 6·7 과제 1(palantir.F5 판정 칸 '구조형 적대로 인한' 삭제)이 남아 있다. 지금은 판정 칸 여섯째 줄에 있다.
