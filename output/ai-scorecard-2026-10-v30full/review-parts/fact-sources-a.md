---
reviewer_agent: fact-checker
session: v30full-fact-a
reviewed_at: 2026-10-20
---
검토자: fact-checker(사실·출처 A — Amazon·Microsoft·Meta 의 이번 실행 추가 근거 67건과 세 회사 판단 53건의 올릴·내릴 근거 줄 417개)
결과: needs_fix

## 범위와 방법

- 대상은 EV-amazon-088~105(18건), EV-microsoft-077~106(30건), EV-meta-085~103(19건)과 `judgments.json` 의 `amazon.*`(18건)·`microsoft.*`(23건)·`meta.*`(12건)이다. 세 회사 판단이 어느 자리에서든 인용하는 근거는 331건이고 그중 66건이 이번 실행 추가분, 265건이 이어받은 근거다. EV-amazon-105 는 어떤 판단도 인용하지 않는다.
- 기계 점검. 판단 `source_ids`·근거 `source_id`·관측 `source_id` 가 모두 `sources.json` 에 있다(누락 0). 인용된 근거 331건이 전부 `confirmed` 이고 `reviewer`·`reviewed_at` 이 있다. `status: new` 판단이 `candidate` 를 인용한 곳은 없다. 올릴·내릴 근거 417줄은 전부 `[EV-…]` 표지가 있다. 추가 근거 67건의 `published_at_utc` 는 가장 늦은 것이 2026-10-08(EV-amazon-098)이라 정보 컷오프 2026-10-14 안이다. 관측의 `as_of` 는 컷오프 뒤가 없고 가격 관측의 가장 늦은 날은 2026-10-09(가격 기준일)다.
- 출처 열림. 추가 근거의 SEC 원문 8건은 `scorecard_cli.py sec-get` 으로 받았다(2026-10-07 캐시, 새 SEC 요청은 만들지 않았다). 그 밖의 27개 주소는 curl 로 22개가 200 이고, 403 이었던 Ars Technica·FTC 둘·Zoom IR·Microsoft Tech Community 는 앱 안 브라우저(내 탭)로 열어 본문을 읽었다. 봇 확인 화면(Reuters 빈 화면·Bloomberg "Are you a robot?"·CNBC "Access Denied")은 우회하지 않았다.
- 발췌 대조. 추가 근거 67건 전부 원문과 일치한다. 통짜 일치 26건, 공백 차이만 있는 3건(EV-amazon-102·EV-meta-093·EV-meta-101), 생략 부호(…)로 이은 조각이 각각 원문에 있고 순서가 맞는 33건(표 줄의 `|` 와 `$` 구분은 표 변환 표기로 보고 숫자·문언을 대조), 브라우저로 읽은 5건이다. Meta 녹취록 8건은 PDF 쪽수(1·2·3·4·5·12쪽)가 실제 쪽과 같고, SEC 주석 번호(Amazon Note 2, Microsoft Note 16·18, Meta Note 5)도 맞다. 발행일은 원문 날짜와 맞는다(예외는 다음 실행 과제 O-2).
- 줄 대조. 417줄을 그 줄이 가리키는 근거의 발췌와 하나씩 맞췄다. 분기 합·TTM·비율은 근거 숫자로 다시 계산했다(Amazon 매출 줄 일곱과 합 $775,680M·80.9%, 세그먼트 영업이익 6.22%, Microsoft 영업이익률 50.6%·FCF·분기 FCF 22%·23% 감소, Meta 광고 $55,024M·$59,363M·FCF $40.98B·약정 3.05배 등). 이어받은 근거 265건도 발췌가 줄의 사실을 받치는지 읽었고, 원문과의 글자 대조는 가능한 주소 전부에 했다. 못 연 것은 아래에 적었다.
- 시장 점유율 숫자(Amazon TV 시청 4.37%·3.60%, 클라우드 28%·30%·20%, Windows 69.81%·79.35%, Bing 4.73%·4.01%, Facebook 72%·73.3%, Instagram 7.13%·9.08%, LinkedIn 0.54%·0.65%)는 `observations.json` 의 `_market.*` 값과 같다.
- 판정 칸 "미확인" 가운데 원문이 열릴 수 있는 것을 찾아 열었다. Rivian(10-K FY2025 Item 7A 에만 있고 2026 Q1·Q2 10-Q 에는 없음, 확인됨), G42(FY2025~2026 10-K·10-Q 에 언급 없음, 확인됨), Meta 의 EssilorLuxottica 지분(10-K·10-Q 에 없음), Prime 회원 수(2026 공시·보도자료에 없음), Alexa+ 의 기기 안 처리(Alexa Tablet 발표문에 없음), 하원 법사위 민주당 간사의 자료 요청과 AWS 의 NDA 중단(GuruFocus·TechCrunch 를 열어 판정 칸 문장과 같음)은 판정대로 맞다. 열리는데 쓰지 않은 것은 F-1 하나다.
- 이해상충 표기는 보지 않았다. 실행 파일은 고치지 않았다.

## 발견 사항

- **F-1. amazon.F5 — 열리는 FDA 경고 서한 보도를 원문을 열지 않고 전선에서 뺐다(제목만 보고 미확인으로 돌리지 않는다는 규칙, 2026-10-12 지시).**
  근거 위치: `amazon.F5` 판정 칸 마지막 불릿("FDA 경고 서한 보도(2026-10-07)는 원문을 열지 않아 전선에 넣지 않았고…"). 후보는 "FDA Warns Amazon Over Herpes Treatments - MedPage Today"(중계 주소를 `resolve-urls` 로 풀면 https://www.medpagetoday.com/infectiousdisease/stds/123308)다.
  무엇이 틀렸나: 이 주소는 유료 장벽 없이 열린다. 본문은 FDA 약물평가연구센터가 2026-10-01 Andy Jassy 앞으로 보낸 경고 서한이고, Amazon 이 파는 미승인 헤르페스 치료 제품 아홉 종을 문제 삼으며 영업일 15일 안에 시정 조치를 서면으로 답하라고 요구한다. 열리는 기사를 열지 않고 "원문을 열지 않아"로 둔 것이라 규칙 위반이다.
  점수 영향: 없다. 규칙 ⑤ 비용형은 기본 −2, 구제 조치 진행 −2, 관할 3곳 이상 −2 가 이미 모두 서 있고 상한이 −6 이라 미국 전선이 하나 늘어도 −6 이다(판정 칸도 같은 말을 적었다). 체크리스트에서는 제목만 보고 미확인으로 돌린 것이라 이 항목이 fail 이다.
  고칠 방법: MedPage 기사를 읽고 판정 칸에 "원문 확인함, 규제기관 서한(미국 관할, 이미 센 관할)이라 비용형 전선 하나로 세어도 −6 이 같다"처럼 원문을 읽은 사실과 처리를 적는다. 전선으로 세면 올릴·내릴 칸에 줄을 달고 `confirm` 으로 근거를 확정해 표지를 단다. 고치면 판단 해시가 바뀌므로 research 부터 다시 돈다. 아래 F-2·F-3 도 같은 묶음에서 고친다.

- **F-2. microsoft.F4 — 올릴 근거 첫 줄의 금액이 근거 표와 $7M 다르다(점수 영향 없음).**
  근거 위치: `microsoft.F4` evidence_up 첫 줄("…Microsoft 365·XBOX·LinkedIn·Windows and Devices·Search advertising·Dynamics·Enterprise and partner services 줄이 $202,298M 이다. [EV-microsoft-064]")과 draft.md 1749행.
  무엇이 틀렸나: EV-microsoft-064 의 표(회계연도 2026)로 그 여덟 줄을 더하면 101,997 + 21,790 + 19,817 + 17,084 + 15,176 + 9,175 + 9,006 + 8,260 = $202,305M 이다. Other $109M 까지 넣으면 $202,414M 이다. 어느 쪽으로 읽어도 $202,298M 이 아니다.
  점수 영향: 없다. 같은 판단의 판정 칸 산식 (331,839 − 129,425 − 109 + 0.4 × 109) ÷ 331,839 = 60.98% 은 맞는 입력으로 계산돼 있고 ④ 다각화 6.10 은 그대로다.
  고칠 방법: 금액을 $202,305M 으로 고친다(Other 를 따로 두는 문장이면 $202,414M 에서 Other $109M 을 뺀 값이라고 적는다).

- **F-3. microsoft.F1.other — 내릴 근거 줄이 인용한 발췌에 그 문장이 없다(점수 영향 없음).**
  근거 위치: `microsoft.F1.other` evidence_down("8-K 재편은 Other 의 일부를 Windows OEM and devices 로 옮긴다. [EV-microsoft-084]").
  무엇이 틀렸나: EV-microsoft-084 의 `excerpt` 는 Azure 재편과 Search and advertising 설명 세 조각뿐이고 Other 를 옮긴다는 문장이 없다. 같은 8-K 원문에는 "Revenue previously reported in Other is now reported within Windows OEM and devices and Productivity and server licensing" 가 있어 줄의 사실 자체는 맞지만, 옮겨 가는 곳이 두 군데인데 줄은 한 군데만 적었다. 표지가 가리키는 근거의 본문 발췌가 줄의 사실을 받쳐야 한다는 5.7 기준을 못 채운다.
  고칠 방법: 위 문장을 EV-microsoft-084 `excerpt` 와 `locator` 에 더하고 줄을 "Windows OEM and devices 와 Productivity and server licensing 으로"로 고친다.

## 체크리스트

| ID | 결과 | 근거 |
| --- | --- | --- |
| Q05 | pass | 출처 이해당사자 표기는 보지 않는다(AGENTS.md 2026-10-02 지시). 발행사 자체 발표를 쓴 줄은 회사 1차 발표로 적혀 있고 2차 보도는 2차로 적혀 있다. |
| Q09 | pass | 사실 면에서 미래 계획을 현재 사실로 쓴 줄은 없다. Microsoft Maia 의 2027년 다기가와트 배치는 "계획이라 칸에 넣지 않는다"고 적었고, Alexa Tablet 은 "출하한다"로, Surface 는 2026-10-13 판매 시작으로 적었다. Alexa Tablet 출하일 2026-10-14 는 컷오프 당일이다(규칙 일관성 영역이 기기 칸을 따로 본다). |
| 그 밖 | not_applicable | Q01~Q04·Q06~Q08·Q10~Q25 는 규칙 일관성 영역이 판정한다. 이 리뷰는 사실·출처만 본다. |
| 제목만 보고 미확인 처리 금지(AGENTS.md 2026-10-12) | fail | F-1. |

## 다음 실행 과제

- **O-1. 같은 사건의 근거 둘이 어긋난다(점수 영향 없음).** EV-amazon-004(NBC 제목 "Meta's Muse blocked by Amazon and Walmart")는 Walmart 도 Muse 를 막았다고 하고, EV-amazon-048 은 Meta 가 Walmart 와 제휴했고 Amazon 만 막았다고 한다. TRG-006(철회)의 관찰 문장은 앞쪽을, `amazon.F1.online_store` 와 TRG-114 는 뒤쪽을 쓴다. 어느 쪽이 맞는지 정하거나 판정 칸에 갈린 사실을 적는다.
- **O-2. EV-amazon-092 의 날짜와 위치.** Ars Technica 페이지에는 "SEP 17, 2026 1:40 AM"으로 적혀 있는데 근거·출처의 게시일은 2026-09-16 이다(Google News RSS 시각). `locator` 의 "열째 문단"은 실제 일곱째 문단이다. 컷오프 안이라 판정은 같다.
- **O-3. 이어받은 근거 5건의 발췌가 표 머리글을 줄여 적었다.** EV-meta-001·020·035·037·038 은 "Three Months Ended… | Six Months Ended…"처럼 열 머리글을 합쳐 적어 원문 글자와 같지 않다. 숫자는 전부 원문에 있다. 다음에 고칠 때 머리글을 원문 그대로 옮긴다.
- **O-4. 못 연 주소.** CNBC 둘(EV-meta-051 Muse 구독 $20·$100, EV-amazon-053 2022 Prime 인상, 접근 거부 화면), Reuters 둘(EV-meta-052 Florida 소송은 이전 확인 기록이 있고 EV-meta-008 은 The Star 전재본으로 확인했다고 출처에 적혀 있다, 이번에는 빈 화면), Bloomberg(EV-microsoft-076, "Are you a robot?"), CNBC EV-microsoft-041(접근 거부) 은 봇 차단이라 이번에 본문을 다시 대조하지 못했다. EV-microsoft-076 과 EV-microsoft-041 의 사실은 열린 EV-amazon-008·EV-microsoft-042 의 본문이 함께 받친다. EV-meta-051 의 구독 가격은 같은 줄의 다른 근거(EV-meta-019·067)와 달리 이 근거 하나만 받친다. 사용자가 열어 줄 수 있다. 나머지 이어받은 근거(Yahoo 넷, OpenAI 일곱 쪽, war.gov, DCD, Ars, qz.com, GeekWire, Barchart, Axios, FTC, amazon.com)는 앱 안 브라우저로 열어 발췌와 같음을 확인했다.
- **O-5. 근거 하나가 어떤 판단에도 인용되지 않는다.** EV-amazon-105(10-K FY2025 Rivian 지분)는 `amazon.F5` 판정 칸의 Rivian 미확인 결론과 맞지만 표지로 달리지 않았다. 지분 동맹에서 뺀 이유를 받치는 근거라 필요하면 판정 칸에서 가리킨다.
- **O-6. 추가 근거의 출처 15곳은 `sha256` 이 null 이다**(SRC-WEB-microsoft-906~911, SRC-WEB-microsoft-001·002, SRC-WEB-meta-005, SEC 5곳 등). 원문 스냅샷이 없어 다음 사람이 같은 글을 못 받을 수 있다.
- **O-7. 이어받은 트리거의 확인 문장.** 세 회사의 이전 트리거 18건(carry, v2.1 실행에서 이어받음)은 이 영역의 지시 범위가 아니라 기계 점검(근거·출처 등록, 확정, 컷오프)만 했고 이상이 없다. 철회된 TRG-006(중복, TRG-114 에 조건 합침)과 TRG-056(③ 판단 근거가 v3.0 에 쓰이지 않음)의 사유는 근거와 어긋나지 않는다. 2026-10-12 Meta 가 Muse Wonder 모델군을 낸 일은 Meta 트리거에 없고 Anthropic·OpenAI 트리거와 EV-meta-082~084 에만 있다. Meta ②③ 는 모델 층 순위를 옮기지 않는다고 판정 칸에 적었으므로 점수 문제는 아니다.
