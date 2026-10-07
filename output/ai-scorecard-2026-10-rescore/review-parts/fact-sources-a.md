---
reviewer_agent: fact-checker
session: fc-opus55-20261007-rescore-r8a (원문 연결 세션·조율자와 다른 세션, a 묶음 전담)
reviewed_at: 2026-10-07
round: 8
---
# fact-sources-a — 사실·출처 (alibaba, alphabet, amazon, anthropic, apple)
검토자: Claude Opus 5.5 (claude-opus-5-5) · 사실·출처 독립 세션 a(이 실행을 만든 세션 아님) · 2026-10-07 · 원문 연결 뒤
결과: needs_fix
요약: 맡은 다섯 회사 판단의 올릴·내릴 근거 138줄과 그 줄이 가리키는 근거 211건(모두 confirmed, reviewer·reviewed_at 있음, sources.json 에 등록됨)을 전부 봤다. 211건 모두 출처 URL 원문에서 발췌를 찾았다. 정규화한 문자열이 그대로 맞은 것이 146건, 표 칸·문장부호만 다른 것이 50건, 받기가 막혀 Playwright 로 연 것이 14건, 사람이 읽어 확인한 것이 1건이다. 발행일은 모두 2026-10-06 이하이고, 발행일 칸이 빈 근거가 2건 있다. 줄의 숫자·날짜·주체는 138줄 가운데 137줄이 발췌와 맞는다. 최근 1년 합산(alphabet·amazon·apple·alibaba ⑨, amazon ⑦)은 발췌의 표 값으로 다시 계산해 모두 맞았다. needs_fix 는 1건이다. amazon.F2 올릴 근거가 "Trainium3(362 PFLOPS)" 라고 적는데, 인용한 원문(EV-amazon-034)에서 362 PFLOPS 는 칩 144개짜리 Trn3 UltraServer 의 합계다. 같은 공지는 칩 1개를 2.52 PFLOPS 로 적는다. 점수·순위에는 닿지 않는다. 다음 실행 과제는 9건이다.

검토 기준: results_hash `bacc7bc3e82a981d…`, draft_hash `0148fb46af32d9e8…`(review.md frontmatter 와 같음을 확인). 입력은 judgments.json·evidence/evidence.json·sources.json 의 현재 작업 트리(커밋 `7f684c6` 뒤)다. 대조 스크립트는 세션 스크래치 `fsa/fetch.py`·`fsa/match.py` 다.

## 확인 내용

### 범위와 기계 점검
- 대상 판단: 다섯 회사 판단의 evidence_up·evidence_down 138줄이다. 모든 줄에 표지 `[EV-…]` 가 있고, 표지 없는 줄은 0이다. 표지가 가리키는 근거는 211건이고 evidence.json 에 없는 ID 는 0이다. 211건 모두 `status: confirmed` 이며 reviewer·reviewed_at·locator·excerpt 가 차 있다. source_id 는 모두 sources.json 에 있다.
- 발행일: 211건 모두 2026-10-06 이하다. 가장 늦은 것은 EV-alphabet-050(Reuters, 2026-10-05T16:52Z)이다. EV-amazon-001(8-K 2026-06-10)과 EV-amazon-002(10-Q 2026-07-31)는 `published_at_utc` 가 null 이다. 출처 SRC-EDGAR-000110465926072140·SRC-EDGAR-000101872426000026 도 마찬가지다. 문서 자체의 날짜는 기준일 이전이다(다음 실행 과제 3).
- 원문 받기: 고유 URL 128개를 받았다. SEC 공시 24개는 `scorecard_cli.py sec-get` 으로 받았고(모두 캐시), 나머지는 urllib 로 받았다. 막힌 9개(Reuters 3, war.gov 2, WinBuzzer, TechXplore, Search Engine Land, MarketScreener)와 Google 뉴스 리다이렉트 8개는 Playwright 새 탭에서 열고 닫았다. Google 뉴스 리다이렉트 URL 을 쓴 출처 8개는 sources.json `note` 에 "url 은 Google 리다이렉트 링크다" 로 표시돼 있다. 그 가운데 5개는 locator 에 원문 주소를 적었고, 나머지 3개(NBC·Motley Fool·qz)는 리다이렉트가 기사 원문으로 풀렸다.

### 발췌 원문 대조(기계 대조와 사람 확인)
| 방법 | 건수 | 내용 |
| --- | --- | --- |
| 기계 · 정규화 문자열 일치 | 146 | 따옴표·대시·공백만 정규화했다. `…` 로 자른 발췌 4건은 조각이 모두 원문에 있다. |
| 기계 · 느슨한 일치(영문·숫자만 남김) | 50 | SEC 표 발췌(칸 구분 세로막대, `$`, 괄호 음수)와 iXBRL 줄바꿈 차이다. 숫자 열은 순서대로 이어져 일치한다. |
| Playwright · 화면 본문 대조 | 14 | Reuters 4건(EV-alphabet-042·050, EV-anthropic-045·046), war.gov 2건(EV-alphabet-044·048), EV-apple-010·025·028, EV-alibaba-058, EV-alphabet-005, EV-amazon-004·007·009 다. 12건은 그대로 있다. EV-alphabet-050 은 원문의 "Alphabet's (GOOGL.O) Google", EV-amazon-009 는 원문의 시세 위젯("$WMT +2.03%")을 발췌에서 뺐을 뿐이고 문장은 같다. |
| 사람 · 원문 읽기 | 1 | EV-alphabet-040(silicon.co.uk)은 두 문장 사이에 소제목 "Search monopoly" 가 끼어 있다. 두 문장은 글자 그대로 있고, locator 도 두 문단으로 적었다. |

- 인용 위치: SEC 공시의 쪽 번호가 적힌 곳은 발췌가 나오는 쪽을 기계로 찾아 대조했다. Apple 10-Q·10-K 8건(p.1·2·5·15·22·23·29·33)과 Alibaba 20-F 의 F-5·F-12·F-21·27쪽이 locator 와 맞다. 주석 번호(Amazon Note 1·2·4·5·8, Alphabet Note 2·3, Alibaba 주석 21·27)는 발췌 앞뒤 문단의 제목에서 맞음을 확인했다. EV-anthropic-033(SpaceX S-1/A)은 locator 대로 같은 문단이 두 번 나온다. 뉴스의 "N번째 문단" 은 Playwright 로 본 14건과 EV-alphabet-040 만 앞뒤 문맥으로 맞음을 확인했다. 나머지 기사 문단 번호는 세지 않았다.
- 라이브 페이지: Arena 텍스트 표(EV-alphabet-033)는 2026-10-07 에도 "Oct 2, 2026 · 8,626,731 votes" 판이다. 1위 gemini-4-argon-high(Preliminary)이고 2~7위는 모두 Anthropic 이며, 8위가 gemini-3.8-flash-high 다. 그래서 alphabet.F2 내릴 근거의 "Argon 을 빼면 최고 8위" 가 맞다. Text-to-Video 표(EV-alphabet-032, 2026-09-21 판)와 StatCounter 2026년 9월 표(EV-alphabet-031)도 발췌와 같다.

### 줄 사실 대조(사람이 138줄을 모두 읽음)
- 숫자 재계산: 아래 값을 발췌의 표 값으로 다시 계산했고 모두 맞는다.
  - alphabet ⑨: 최근 1년 매출 $445.9B·영업이익 $147.6B·33.1%, FCF $185.7B − $132.4B = +$53.3B, 2분기 FCF −$5.9B.
  - amazon ⑦⑨: 최근 1년 매출 $775.7B·영업이익 $93.7B·12.1%, 영업외 이익 $81.8B(세전이익의 46.6%), FCF −$11.6B. 여신 $15.0B + $5.0B + $17.5B = $37.5B, 약정 $137.2B + $130.1B = $267.3B.
  - apple ⑨: 최근 1년 매출 $466.8B·영업이익 $154.9B·33.2%, FCF +$136.7B. 6월 분기 설비투자 6,799 − 4,344 = $2.46B.
  - alibaba ⑨: 영업이익 RMB30,323M ÷ 매출 RMB1,044,971M = 2.90%, FCF RMB−76,579M ÷ 6.898 = US$−11,102M, 완충 US$24,048M·2.17년, 약정 RMB254,198M(US$36,851M).
  - anthropic ③⑥: 월 증가율 +58%·+57%, 밸류 ÷ ARR 14.8배.
  - alphabet ③: Gemini 월간 사용자 +20%·+5.6%.
- 날짜·요일: 아래 요일·날짜 환산은 모두 원문과 맞는다.
  - EV-alphabet-045·047 "Monday"(2026-04-29 기사) → 2026-04-27.
  - EV-anthropic-010 "Monday" → 2026-10-05.
  - EV-apple-011 "Monday" → 2026-09-14.
  - EV-amazon-043 은 운영 중단 2026년 1월, 공개 2025년 10월이다.
  - EV-amazon-046 재판일은 2027-03-29 다.
- 원문에 있고 발췌 밖인 사실: 아래 두 사실은 발췌에는 없지만 같은 원문에서 확인했다. 줄은 그대로 서고, 조치는 필요 없다.
  - alphabet.F5 의 "IL6·IL7" 은 war.gov 보도자료 둘째·셋째 문단에 있다.
  - alphabet.F2 의 "TPU 8t·8i" 는 Tom's Hardware 본문에 있다.
- 미확인 문장 위치: 판정 칸에 "원문을 찾지 못해" 로 옮긴 문장은 다섯 회사에 11개다. 방향 칸에 "확인하지 못했다" 류의 미확인 사실이 남은 줄은 없다. amazon.F2 내릴 근거의 "정식 출시는 아직 확인되지 않았다" 는 공지가 Azure 를 Preview 로 적은 사실을 옮긴 것이다.
- 금지 표현: 138줄과 발췌에 투자 조언·매매 지시·수익 보장·FOMO 표현은 없다.
- draft: 138줄 가운데 135줄은 표지를 뗀 문장이 draft.md 에 그대로 있다. 나머지 3줄은 anthropic.F6 이다. 비상장 ⑥ 판단 항목은 계산에 쓰이지 않아 카드로 렌더되지 않는다(설계대로다).

## 발견
| 등급 | 판단 ID · 칸 | 줄 앞부분 | 근거 ID | 발견 | 고칠 방향 | 점수 영향 |
| --- | --- | --- | --- | --- | --- | --- |
| needs_fix | amazon.F2 · evidence_up[1] | "첫 3nm 칩인 Trainium3(362 PFLOPS)는 …" | EV-amazon-034 (EV-amazon-033) | 발췌는 "Trn3 UltraServers can scale up to 144 Trainium3 chips (362 FP8 PFLOPs total)" 다. 362 PFLOPS 는 칩 144개짜리 UltraServer 의 FP8 합계인데, 줄은 칩 하나의 성능처럼 적는다. 같은 공지 앞 문장은 "Each AWS Trainium3 chip provides 2.52 petaflops (PFLOPs) of FP8 compute" 다. 원문과 주체가 다른 숫자다. draft.md 203행에도 그대로 실린다. | 괄호를 "(칩당 FP8 2.52 PFLOPS, 144칩 UltraServer 362 PFLOPS)" 로 고친다. 칩당 값을 쓰려면 같은 공지의 칩당 문장을 EV-amazon-034 의 발췌에 더하거나 새 근거로 단다. | 없음(② 판정 재료가 아님) |

## 체크리스트(a 묶음 해당 항목)
| ID | 결과(pass/fail/not_applicable) | 근거 |
| --- | --- | --- |
| Q05 | pass | 회사 자체 발표(anthropic.com, aboutamazon, blog.google, AWS)는 사실 확인용으로만 인용됐다. 벤치마크 우열은 AA·Arena 같은 제3자 값이다. 이해상충 표기는 AGENTS.md 에 따라 보지 않았다. |
| Q09 | pass | 계획을 점수에 넣지 않는다는 단서를 같은 줄에 단다. 해당 줄은 alibaba.F4 증자·자체 칩, apple.F4 Baltra, anthropic.F4·F8 자체 칩(양산 빨라야 2028~2030), alphabet.F2 Gemini 4 Argon(잠정 순위)이다. |
| Q23 | pass | anthropic.F2 의 AA Intelligence Index 는 같은 측정 주체의 값이다. Coding Agent Index 는 "참가자 전원이 자기 하네스로" 라고 밝힌다. ARC-AGI-3(anthropic.F2)와 HLE(alibaba.F2)는 하네스 불명이라 비교에서 뺐다고 적는다. Arena 는 참고로만 쓴다. |

## 다음 실행 과제
1. (low) anthropic.F6 판정 칸 "자본효율(ARR $65B ÷ 누적 조달 약 $125B = 0.52)은 ARR $65B 와 누적 조달 약 $125B 의 원문을 찾지 못해 확인하지 못했다." 가 같은 판단의 올릴 근거와 어긋난다. ARR $65B 는 그 올릴 근거가 EV-anthropic-040(CNBC 2026-08-17)으로 확인한 값이다. 미확인 대상을 "누적 조달 약 $125B" 로 좁혀 다시 쓴다. 누적 조달은 Anthropic 의 Series F·G·H 발표문으로 쉽게 맞출 수 있다. draft 의 ⑥ 비상장 표는 $125.0B·0.52 를 싣는다. 카드에는 렌더되지 않는다.
2. (low) alphabet.F9 evidence_up[2] 의 순현금 +$121.7B 를 발췌만으로는 다시 계산할 수 없다. EV-alphabet-029·030 은 현금·시장성 유가증권 $242.5B 와 장기차입 $98.2B·비유동 리스 $14.6B 만 보여 준다. 유동성 장기차입 $1,999M(10-Q Note 6 표)과 유동 리스부채가 빠져 있다. 값은 관측 `alphabet.net_cash.nc37`(정의: 현금 + 시장성 유가증권 − 총차입 − 리스부채)과 맞는다. Note 6 표의 "Less: current portion of long-term notes" 줄과 리스 주석 발췌를 근거로 더한다.
3. (low) EV-amazon-001·EV-amazon-002 와 출처 SRC-EDGAR-000110465926072140·SRC-EDGAR-000101872426000026 의 `published_at_utc` 를 채운다(2026-06-10, 2026-07-31).
4. (low) alibaba.F4 evidence_up[2]·alibaba.F9 evidence_up[2] 의 "2026-08-23 발표" 를 고친다. 배정계약일은 2026-08-23 이고, HKEX 공시 서명일과 Reuters 보도는 2026-08-24 다. "2026-08-23 계약·2026-08-24 공시" 로 쓴다.
5. (low) 오래된 근거로 현재 상태를 받치는 줄을 새 원문으로 바꿀지 본다.
   - alibaba.F1 evidence_down[0] 의 PDD·더우인 잠식은 Morningstar 2025-02-21(EV-alibaba-060)로 받친다.
   - amazon.F1 evidence_up[0] 의 Prime 2억 명은 2021 주주서한(EV-amazon-028)으로 받친다.
   - apple.F8 evidence_down[0] 의 "연 약 $20B" 는 2022년 지급분(EV-apple-027)으로 받친다.
6. (low) apple.F4 evidence_down[1] "Baltra 는 내부 전용이라 외부 판매 수익이 없고" 는 EV-apple-019·012 발췌에 없는 추론이다. 판정 칸으로 옮기거나 근거를 단다.
7. (low) 방향 칸에 남은 결론·저울질 문장을 판정 칸으로 옮길지 본다(guide.md 5.6). 해당 줄은 alibaba.F4 up[2]·up[3], apple.F4 up[1], anthropic.F2 up[2], anthropic.F8 up[0], alphabet.F2 up[3], alphabet.F7 down[1], amazon.F5 up[2] 다. 사실은 원문과 맞다.
8. (low) 발췌 표기를 다듬는다. EV-alphabet-050 은 원문의 "(GOOGL.O)", EV-amazon-009 는 시세 위젯을 뺐다. EV-alphabet-040 은 소제목을 건너뛴 두 문단이다. 발췌 안에 생략을 `…` 로 표시하면 글자 그대로 대조가 된다.
9. (low) 뉴스 기사의 "N번째 문단" locator 가운데 Playwright 로 보지 않은 것은 문단 번호를 세지 않았다. 다음 리뷰에서 기사 본문 단락을 세는 기계 점검을 붙인다.

## 열지 못한 근거
없음. 211건 모두 원문을 열어 발췌를 찾았다.

## 이전 리뷰 기록

이 파일은 round 8 에서 사실·출처 영역을 세 세션으로 나누며 새로 만들었다. 이 영역의 round 1~7 기록은 `review-parts/fact-sources.md` 에 있다(round 7 결과 pass, results_hash `59518fa18f928802…`).
