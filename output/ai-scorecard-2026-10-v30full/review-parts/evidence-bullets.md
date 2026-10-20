---
reviewer_agent: evidence-editor
session: v30full-evidence-bullets
reviewed_at: 2026-10-20
---
검토자: evidence-editor(근거 불릿 — 9개사 판단 130개와 시범 바뀐 판단 셋의 판정·올릴·내릴 근거 줄, 줄이 가리키는 근거 743건의 형식)
결과: pass

점수·순위·체크리스트 판정을 바꾸는 발견은 없다(공통 지시서의 needs_fix 기준). 다만 아래 「다음 실행 과제」 1~7 은 draft.md·report.html 에 그대로 실리는 문장 결함이라, 다른 영역의 수정 묶음이 생기면 같이 고치길 권한다.

## 범위와 방법

- 대상. `judgments.json` 의 9개사 130개와 시범 셋(alphabet.F3.cloud·anthropic.F1.claude·anthropic.F5) 모두 133개. 판정 칸 전 문장, 올릴 541줄·내릴 570줄(합 1,111줄), 줄이 가리키는 근거 743건의 `relevance`·`published_at_utc`·`locator`·`excerpt`.
- 이미 보고된 것은 번호로만 참조하고 다시 적지 않았다(fact-sources-b F-02~F-08, fact-sources-c 1~14, rule-consistency F-1~F-5·과제 1~17). 같은 종류가 다른 판단에 더 있으면 그 판단만 더했다.
- 읽기. Amazon·Microsoft·Meta 는 줄과 표지 발췌를 나란히 읽었다. 나머지 여섯 회사와 시범 셋은 판정 칸과 올릴·내릴 줄 전체를 읽고 발췌는 의심 줄만 열었다. 줄의 숫자와 영문 고유명사가 발췌·제목·locator 에 있는지는 기계로도 걸렀다.
- 하지 않은 것. 발췌와 원문의 글자 일치는 사실·출처 영역 몫이다. Amazon·Microsoft·Meta 의 사실·출처 리뷰 파일이 아직 없어 그 세 회사의 원문 대조는 미검증이다(이 리뷰는 줄이 발췌를 넘는지만 봤다). 이해상충 표기는 보지 않았다.

기계 점검 결과.
- 올릴·내릴 1,111줄 모두 끝에 `[EV-…]` 표지가 있고 본문 가운데 표지가 낀 줄은 없다. 표지 근거는 모두 존재·`confirmed`·URL·`locator` 보유, `excerpt` 가 제목과 같은 것 없음, 600자 초과 없음. 후보(candidate) 인용 없음.
- 표지가 하나인 줄 930(83.7%), 둘 이상 181(둘 152·셋 19·넷 7·다섯 3). 다섯 개까지 가는 줄은 분기 합·런웨이처럼 여러 공시에서 숫자를 만든 줄이다.
- 세 칸. 판정 칸이 빈 판단 없음, 올릴·내릴이 모두 빈 판단 없음, `counter_evidence` 는 모두 비어 있다.
- 게시일. 컷오프(2026-10-14) 뒤 게시 근거 없음(날짜 단위 비교). 컷오프 당일 게시 10건(EV-anthropic-143 은 23:02Z, EV-openai-170 은 20:26Z). 게시일이 null 인 근거 7건 가운데 EV-amazon-001·002, EV-meta-001, EV-tesla-001 4건이 인용된다(제목에 제출일이 있고 모두 컷오프 이하).
- 금지 표현. 매수·매도 지시, 수익 보장, 목표가, 상승 여력, FOMO 표현 없음. 규칙 버전 표기·변경 표시 기호·취소선·FIX-류 작업 번호 없음(검증기와 일치). 기준일 뒤 사건을 이미 일어난 일로 쓴 줄 없음(2026-11-02·11-12·2027 일자는 모두 통지·계획이고 출처 게시일이 컷오프 이하).

## 발견 사항

점수·순위·체크리스트 판정을 바꾸는 발견 없음. 세 칸의 방향 배치, 표지-발췌 대응, 낡은 문장, 추론 표시의 결함은 모두 문장·표기 수준이라 아래 「다음 실행 과제」에 번호로 적었다.

한 가지만 점수와의 거리를 따로 적는다. 과제 7 의 nvidia.F8 D11 은 ⑧ 공급 축 −4 의 전제('가까운 대체 없음')를 받치는 줄이다. 줄이 단정하는 문장이 발췌와 어긋나므로 근거를 보강하거나 추론으로 표시해야 하지만, 칸 값은 입력이 정하므로 이 리뷰만으로 점수를 움직이지는 않는다.

## 체크리스트

| ID | 결과 | 근거 |
| --- | --- | --- |
| Q09 | not_applicable | 점수에 쓰인 입력이 아니라 줄 문장 수준의 관찰만 한다. 계획·발표 줄은 대부분 '점수에 넣지 않는다' 단서가 붙어 있다. 단서 없이 미래 일자 통지를 올릴 칸에 둔 줄은 openai.F7 U3·openai.F5.impl48 U5 둘이고, 계획을 현재형으로 쓴 줄은 이미 보고된 openai.F5.impl48 U1·oracle.F8 D9 다. 판정은 규칙 일관성 영역. |
| 그 밖 | not_applicable | Q01~Q08·Q10~Q25 는 규칙 일관성·재무 계산 영역이 판정한다. 이 리뷰는 줄의 분류·표지·문장만 본다. |

## 다음 실행 과제

점수·순위·체크리스트 판정을 바꾸지 않는다. 1~7 은 게시되는 문장이라 승인 전에 정정하길 권한다. 8~14 는 다음 실행의 작성·검증 규칙으로 올려도 된다.

1. 낡고 내부 보고 문장이 섞인 판정 문장 — alibaba.F3.cloud V6. [중]
   - 문장. "Alphabet 클라우드 층 ③ 은 연산을 사용량으로 빌려주는 전략(같은 방식)으로 매겨져 Gemma 무료 공개를 이 층의 전략으로 세지 않았다. 두 회사의 같은 구조가 다르게 매겨져 있다는 사실을 조율자에게 보고한다."
   - 현재 alphabet.F3.cloud V2 는 같은 Gemma 공개를 공짜 전략(별도 수익모델 4)으로 센다. 규칙 일관성 리뷰도 네 클라우드·칩의 개방형 모델 읽기가 일치한다고 판정했다. 이 두 문장은 현재 표와 반대이고, Q03 불일치가 아직 남은 것처럼 읽힌다. 게다가 조율자에게 보내는 말이다.
   - 고칠 방법. V6 의 둘째·셋째 문장을 지운다(문 닫힘 증거 없음 문장은 둔다).

2. 다른 판·트리거·작업 경위를 가리키는 표현이 판정 칸에 남았다(AGENTS 「금지·주의」). 검증기 `SELF_CONTAINED_BANNED` 에 '시범'·'TRG-'(트리거 문장에만 댄다)·'조율자'·'같은 실행'이 없어 통과했다. [중]
   - a. oracle.F5 V8 "시범 SpaceX ⑤ 가 …", V9 "Alphabet 시범도 …" 는 시범 실행(이전 판)을 가리킨다.
   - b. alibaba.F4 V3 "(TRG-340)", alibaba.F5 V8 "(TRG-079)" 는 트리거 번호다.
   - c. microsoft.F3.application V1 "모방 불가능성이 8 이 아니라 층 최고 15 관문과 …" 은 옛 값을 정정한 조각이 남아 읽히지 않는다. NVIDIA·Alphabet 층 ③ 의 V1 처럼 "모방 불가능성 관문(층 최고 15)과 문 닫힘 관문(층 최고 18)은 점수보다 높아 닿지 않는다" 로 쓴다.
   - d. tesla.F1.energy V1 "정의표를 만들지 않기로 한 사용자 결정(2026-10-19)에 따라" 는 결정 경위이고 날짜가 컷오프 뒤다. 같은 종류가 microsoft.F1.xbox V1 "(사용자 결정)", nvidia.F1.edge_computing V6 "사용자 결정으로", meta.F1.reality_labs V1 "사용자가 … 정해", alibaba.F1 일곱 사업(cn_ecom_cmr·cn_ecom_direct·cn_wholesale·intl_retail·intl_wholesale·all_others·quick_commerce) V1 "사용자가 미확인으로 정한 전자상거래" 다. Amazon 의 같은 시장 문장은 "정의표가 없어"로 사실만 적는다. 사실 문장으로 맞춘다.
   - e. alibaba.F9.obsreg25 V5 끝 문장 "비교 가능성은 예로 입력해 엔진이 결측 유형까지 내려가게 했다" 는 입력을 다룬 경위이고 '엔진'은 내부 구현이다. 지운다. 결정 번호 C-16(alibaba.F9 V5)·C-23(amazon.F9 V4)도 뜻을 풀어 쓰고 번호는 뺀다.
   - f. "같은 실행"·"이 실행" 11곳은 다음 실행으로 승계되면 틀린다. amazon.F2.user_platform V2, amazon.F5 V2·V3·V8, amazon.F7 V7, amazon.F8 V2, microsoft.F5 V3·V9, microsoft.F7 V11, microsoft.F8 V3, anthropic.F5 V11.

3. 다른 기업의 판정·점수를 이유로 인용한 판정 문장. [하]
   - 38개 판단의 61문장(기계 집계, 순수 사실 문장 몇 개 포함). 대부분 "같은 실행의 X 가 … 읽은 것과 같은 잣대다" 형태라 X 의 판단이 바뀌면 문장이 낡는다. 2026-10-09 지시가 요구하는 것은 읽기가 갈릴 때 갈리는 이유(관계의 종류)를 적는 것이지 다른 회사의 읽기를 근거로 대는 것이 아니다.
   - 다른 회사의 점수·칸·수치를 적은 곳(11). microsoft.F1.search_advertising V2("Google 검색은 6 을 받았다")·V4, microsoft.F2.cloud V3(1.82), microsoft.F2.user_platform V3(10배), microsoft.F3.user_platform V3("6 을 받았다"), microsoft.F8 V3(Alphabet 고객 축 비공개 −1), alibaba.F2.cloud V2(1.82배), alibaba.F3.user_platform V3·alibaba.F3.cloud V3("같은 칸(4)"), oracle.F7.fix52 V6(연 $40B·9.0%), amazon.F7 V7(20.1%).
   - 고칠 방법. 적용한 잣대를 그 문장 안에서 규칙 문언으로 쓰고 다른 회사 이름은 지운다. 읽기가 갈리는 곳(예 amazon.F5 V8, openai.F5.impl48 V10)만 이유를 남긴다. tesla.F8 V2 의 "Apple 과 같은 근거 등급"은 2026-10-09 지시가 요구하는 근거 등급 표시이므로 두되, 등급(2차 보도와 10-K 문언)을 문장에 직접 적는다.

4. 낡거나 단정적인 비교·최상급 문장(C-19). [중]
   - "Google 은 가장 성능이 좋은 개방형 모델 Gemma 4 를 …" 3줄(alphabet.F3.cloud U2, nvidia.F3.chip_design D1, alibaba.F3.cloud D1). 발췌(EV-alibaba-022)는 "our most capable open models" 로 Google 이 자기 오픈 모델 가운데 가장 강하다는 회사 홍보 문구다. 시장 전체 최고로 읽히게 옮겼고, 바로 이어지는 줄이 2.4T 매개변수 Qwen Max 가중치 공개(2026-08-12)라 줄끼리도 부딪친다. "Google 은 Gemma 4 를 Apache 2.0 라이선스로 냈다. 회사는 이를 자사에서 가장 강한 오픈 모델이라 부른다" 로 고친다.
   - "Bing 월간 사용자는 처음으로 10억 명에 이르렀다"(microsoft.F2.user_platform U4, microsoft.F1.search_advertising U1)는 2026-04-29 통화 값인데 날짜가 없다. Tesla 의 "사상 최대"(tesla.F2.device U2, tesla.F3.device U3)는 회사 발표인데 귀속 표시가 없다.
   - 날짜 없는 오래된 근거 32줄(인용 근거가 모두 2025-10-14 이전, 줄에 연·날짜 없음). 대표적으로 Phi-4(2024-12-12)를 현재형으로 쓴 6줄(alphabet.F3.cloud D4, microsoft.F3.cloud U1·U2, nvidia.F3.chip_design D3, alibaba.F3.cloud D3·D4), MTIA·Catalina·PyTorch(2022~2024)의 meta.F4 U7·U10·U11, Copilot Chat·Workspace Gemini(2025-01·2025-09) 줄들, Stargate(2025) 줄들, Oracle EV-oracle-040(2019) 줄들(fact-sources-b F-07 과 같은 묶음). 줄에 날짜를 적거나 최근 근거로 갈아 끼운다.
   - 같은 지표의 낡은 값이 최신 값과 한 리포트에 함께 실린다. ChatGPT 주간 사용자 "9억 명"(meta.F3.user_platform U5, openai.F7 U1, 2026-03-31)과 "12억 명"(openai.F1.chatgpt_api U1·openai.F4 U6, 2026-10-07). Meta AI 월간 사용자 "10억 명"(2025-10-29 통화)을 날짜 없이 쓴 7줄(meta.F2.user_platform U4, meta.F4 U16, amazon.F3.user_platform D3, microsoft.F3.user_platform D2, alibaba.F3.user_platform D3, openai.F3.model D2 와 meta.F4 V11).
   - Microsoft 의 공짜 전략(③ 클라우드)은 사용자 결정으로 들어간 읽기다. 다만 결정이 닿는 줄의 근거가 Microsoft 만 2024-12 Phi-4 이고 Alphabet·NVIDIA·Alibaba 는 2026 년 공개다. 결정을 바꾸자는 것이 아니라 어긋나는 자리를 적는다. 규칙 ③ 은 "지금" 쓰는 방식을 세는데 Microsoft 쪽 근거가 22개월 전 출시 하나다. 2026 년 Microsoft 오픈 모델 공개 근거를 더하거나 줄에 날짜를 적는다.

5. 줄이 표지 발췌를 넘는 곳(Amazon·Microsoft·Meta, 사실·출처 리뷰 파일 없음). 원문에는 사실이 있을 가능성이 크니 발췌·locator 를 넓히거나 줄을 줄인다. [중]
   - microsoft.F1.enterprise_partner_services U2·V2 "선수 매출에는 앞으로 수행할 컨설팅 서비스 대금도 들어 있다" — EV-microsoft-085 발췌는 앞 두 문장뿐이라 컨설팅이 없다.
   - microsoft.F1.linkedin D1 후반 "Talent·Sales Solutions 는 업무 솔루션 묶음으로 옮긴다" — EV-microsoft-084 발췌에 없다.
   - microsoft.F1.other D1·V1 "Other 의 일부를 Windows OEM and devices 로 옮긴다" — EV-microsoft-084 발췌에 'Other'·'Windows OEM' 이 없다.
   - microsoft.F3.application U1 "Word·Excel·PowerPoint·Outlook·OneNote 안에서" — EV-microsoft-100 발췌는 "a range of Office apps" 다.
   - microsoft.F4 U15 "NPU 로 기기 안 AI 를" — EV-microsoft-105 발췌에 NPU 가 없다(on-device AI 만).
   - amazon.F3.user_platform D2 "검색의 AI 답변을 검색 광고 위에 얹어 준다" — EV-alphabet-037 은 "AI answers atop Search" 이고 광고 언급이 없다. "검색 위쪽에 AI 답변을 둔다" 로.
   - amazon.F4 D3 "EC2 로만 수익화" — 이 내용은 EV-amazon-063 에 있고 줄이 인용한 EV-amazon-065 에는 없다. 표지에 063 을 더한다.
   - amazon.F5 U5 "(출하한 칩은 없다)" — 발췌는 팀 구성 확인만 말하고 부재 단정이 없다. "출하한 칩은 확정 근거에 없다" 로.
   - meta.F5 D10 — EV-meta-046 은 이란 인터넷 차단과 러시아 접근 제한을 함께 원인으로 적는데 줄은 러시아만 적는다(같은 근거를 쓴 meta.F8 D13 은 둘 다 적는다).

6. 숫자 오기. [하]
   - microsoft.F4 U1 "… 줄이 $202,298M 이다" — 나열한 일곱 줄 합은 $202,305M 이다(Other 를 더하면 $202,414M). 어느 값도 $202,298M 이 아니다. 판정 칸 V9 의 60.98%(202,348.6 ÷ 331,839)와 입력은 맞다. 숫자만 고친다. 이 줄은 합계를 여러 칸에서 직접 만들었는데 "(계산)" 표시가 없다.

7. 추론·부재를 사실처럼 쓴 줄. [하, nvidia.F8 D11 은 우선]
   - nvidia.F8 D11 "첨단 공정의 다른 파운드리는 아직 대량 공급 단계가 아니다." — 인용 발췌는 Samsung SF2 수율 약 60%(Chosun 인용 보도, EV-tsmc-032)와 Intel 10-Q(EV-tsmc-072)다. Intel 발췌 첫 문장은 18A 를 2026년 초 자사 제품에 대량 생산(high volume production)으로 적고 외부 고객용 18A-P 만 2026-06 위험 생산이라고 적는다. 첫 문장은 줄이 아니라 판단의 추론이다. "Intel 18A 는 자사 제품용으로 양산 중이고 외부 고객용 18A-P 는 위험 생산(2026-06), Samsung SF2 수율은 약 60% 로 보도됨" 으로 사실만 쓰고 결론은 판정 칸에서 추론으로 표시한다.
   - amazon.F9.obsreg25 U2 "설비투자는 줄일 수 있는 지출이다", U6 "…과소계상되고 … 과대계상되므로 커버리지는 보수적으로 낮게 나온다" 는 발췌에 없는 판단 문장이다. 판정 칸으로 옮기거나 (추론) 표시를 단다.
   - 위험 요인의 'could/may' 문장이 귀속 단서 없이 올릴·내릴 근거로 쓰였다. amazon.F8 D1, meta.F8 D7·D12, microsoft.F8 D13, palantir.F8 D3·D5, tesla.F8 D4, oracle.F5 D5, oracle.F8 D4·D12·D13. 같은 종류 문장을 쓴 nvidia.F4 D5·nvidia.F3.chip_design D4·oracle.F1.oci D4·palantir.F1.commercial D2 는 "회사가 적는다"를 붙였다. 맞춘다.

8. 근거 세 칸(guide 5.6) 분류가 어긋난 줄. fact-sources-c 4, rule-consistency 「판단 근거 세 칸」과 겹치지 않는 것만 적는다. [하]
   - 분류 판정 문장이 방향 칸에 실렸다. ④ 여덟 판단(amazon·microsoft·nvidia·oracle·alibaba·meta·tesla·palantir)의 U1 "…은 AI 무관 매출이다"와, 앞 다섯 판단의 D1 "…은 AI 수요로 세어 AI 무관 몫에서 빠진다". 관계 분류 문장 tesla.F5 U3·D9, tesla.F2.device D5, openai.F5.impl48 U2, anthropic.F5 U3, amazon.F2.cloud U4("…로 세지 않는다"). 모두 판정 칸 문장이다.
   - 판정이 점수에 쓰지 않는다고 적은 사실이 방향 칸에 있다. microsoft.F3.application D3(Zoom, "지금도 같은지는 미확인"), meta.F3.user_platform D7(Muse Glimmer, 판정 V5 는 세지 않는다), palantir.F5 D10(CBS 인터뷰, V11 은 긴장으로 세지 않는다), nvidia.F1.data_center D5·D6·D7(공급 제약·매출총이익률·가격 인상 모두 V3·V4 가 미확인으로 둔 항목), oracle.F8 U4(조달 자본이 줄어도 배수는 안 바뀐다고 V3 가 적음), tesla.F5 D7("그 뒤 결과는 확인되지 않는다", 미확인은 판정 칸).
   - 해당 칸의 점수 항목과 무관해 칸을 채우려고 둔 줄. amazon.F2.outside D1, tesla.F2.outside D1·D2, tesla.F3.outside D1, oracle.F2.outside U1(매출 증가율은 패러다임 적응 지표가 아니다), amazon.F1.other U1, microsoft.F1.other U1·D1. 규칙이 방향 칸을 둘 다 비우지 못하게 하는 탓이다. 억지로 채우기보다 가이드에 "해당 사실이 없으면 가장 가까운 사실을 판정 칸에 두고 방향 칸에 '없음'을 허용" 같은 길이 필요하다.
   - 앞 줄을 가리키는 줄. nvidia.F1.data_center U2 "같은 개발자 수는 2025 회계연도 590만 명을 넘었다"(기준값이라 올릴 근거도 아니다), meta.F9 U2 "같은 최근 1년 기간". 줄마다 자립하도록 고친다.
   - 같은 사실을 올림과 내림 양쪽에 쓴 amazon.F2.user_platform U1·D1(EV-amazon-088 '두 배 가까이'). D1 은 문턱 판정이라 판정 칸으로 옮긴다.

9. 근거 `relevance` 의 추론 표시와 낡은 판단 값. [하]
   - structure.md·score-collect 는 `relevance` 를 추론으로 표시하라고 한다. 이번 실행에서 더한 근거 160건 가운데 Meta 19건은 "추론:", OpenAI 12건은 "사실: … 추론: …" 로 나눠 썼지만 나머지 125건은 표시가 없다(Amazon 18 EV-amazon-088~105, Microsoft 30 EV-microsoft-077~106, Tesla 23 EV-tesla-076~098, Alibaba 16 EV-alibaba-098~113, Palantir 15 EV-palantir-052~066, Oracle 13 EV-oracle-062~074, NVIDIA 13 EV-nvidia-118~130). 예를 들어 EV-tesla-076 은 공시 사실 뒤에 "③ … 근거다" 라는 추론이 붙어 있다. 9개사 근거 937건 전체로는 474건이 표시 없이 시작한다(2026-10-07 표지 보강 배치 319건 포함).
   - 근거 `relevance`·`conditional_impact` 에 이전 척도의 판단 값이 현재형으로 남았다(83건). 예 EV-oracle-004 "지금 Oracle ⑧ 판단은 -4"(현재 −12), EV-microsoft-039~042 "⑤ 판단은 … 4점이다"(현재 11), EV-meta-052 "지금 판단은 동맹 +1, 적대 -1"(현재 10), EV-nvidia-107 "범위 하한인 −3"(현재 −12). 회사별 건수는 Alibaba 5, Amazon 8, Meta 7, Microsoft 7, NVIDIA 22, OpenAI 4, Oracle 8, Palantir 12, Tesla 10. fact-sources-b F-07 은 NVIDIA·Tesla 일부만 적었다. 이 문장들은 evidence.json 과 research.md 에 남는다. 확인한 문구(위 예시 네 가지)는 draft.md·report.html 에 나오지 않았다. 지우거나 현재 판단과 무관한 서술로 다시 쓴다.

10. 한 줄에 독립 주장 둘 이상을 묶은 곳. 줄마다 주장 하나와 표지를 맞추면 표지-발췌 대조가 쉬워진다. [하]
   - 같은 문장 4곳. "Meta AI 월간 사용자 10억 명을 넘었고 Meta 는 매출 거의 전부를 광고로 번다" [EV-meta-049, EV-meta-031] — amazon.F3.user_platform D3, microsoft.F3.user_platform D2, alibaba.F3.user_platform D3, openai.F3.model D2.
   - meta.F5 D2(뉴멕시코 평결·벌금 청구·2분기 소송 비용 셋), D3(48개 주 합의·플로리다 청구), D7(EU 임시 조치·타 국가 조사). microsoft.F5 D1·D2(제소와 병합), D7(독점 종료·Bedrock 탑재·FT 보도). amazon.F1.aws U2(5년 계약·임대료 인상 공개). nvidia.F5 D3·D6. anthropic.F5 D1·D12. palantir.F5 D10(의혹과 반박).
   - 표지가 둘 이상인 181줄 가운데 이 묶음이 아닌 것은 같은 숫자를 둘 이상 공시에서 만든 줄이라 그대로 둔다.

11. `not_disclosed`(공시하지 않음)와 `unverified`(우리가 못 찾음)의 혼용. 점수에는 닿지 않는다. [하]
   - 판정 칸 서술 52문장이 "…은 공시되지 않는다(미확인)" 형태다. 시범 셋의 alphabet.F3.cloud V6, anthropic.F1.claude V4 도 같은 문장이다. 규칙 2.6 은 "공시된 적 없음이 확인됨"을 발행사가 공시하지 않는다고 스스로 밝힌 경우와 비상장 재무제표로 한정하고 나머지는 "확인되지 않음"이라 한다. 구조 라벨이 아닌 서술이므로 하나로 정한다. "공시에서 찾지 못했다(미확인)" 로 쓰고 발행사가 밝힌 경우만 "공시하지 않는다고 밝혔다"로 쓴다.
   - ⑧ 고객 축 구조 라벨. Amazon·Tesla·Alibaba 는 `not_disclosed` 이고 그 근거가 "10-K·10-Q(20-F) 전문에서 찾지 못했다"인데, 같은 종류의 부재를 OpenAI·Anthropic 은 `not_found`(탐색 미완)로 적었고 Apple 은 "공개하지 않는 항목이라 비공개"로 적었다. fact-sources-b F-07(Tesla)·fact-sources-c 13(Alibaba)에 Amazon(`amazon.F8` inputs 와 V2)을 더한다. 점수는 정책 기본값 −1 로 같다.

12. 근거 등급 표시. [하]
   - 근거 채널이 `secondary` 인 73줄 가운데 54줄에 "(2차 보도)"·"보도" 표시가 없다. 지수 표(Artificial Analysis) 값을 쓰는 anthropic.F1.claude U6·D9~D11, openai.F2.model U1~U3·D1~D4 처럼 독립 측정을 옮긴 줄은 괜찮지만 기사·분석을 옮긴 줄은 표시한다(amazon.F5 D1·D5, microsoft.F5 D6, tesla.F5 D1·D4, meta.F3.device D1).
   - Qwen 최대 등급 가중치 공개(2026-08-12)는 2차 기사 하나(EV-alibaba-023)로 서 있고 "처음으로"를 4줄에서 단정한다(alibaba.F3.cloud U3, microsoft.F3.cloud D2, nvidia.F3.chip_design D2, alphabet.F3.cloud D2). 같은 입력의 다른 회사(Gemma 4·Nemotron·Phi-4)는 회사 1차 근거다. 2026-10-09 지시("같은 입력에는 같은 등급")에 따라 Qwen 공개의 회사 1차(Qwen 블로그·모델 저장소)를 확정 근거로 올리거나 줄에 "(2차 보도)"를 단다.

13. 상대 시간 표현이 날짜 없이 남았다. [하] anthropic.F1.claude D5 "Microsoft 의 올해 사내 Anthropic 지출", palantir.F5 D4 "내년 3월", oracle.F8 D3 "올해 1분기", openai.F4 V7·D2·D3 "올해 말까지·올해 안에", microsoft.F1.m365_consumer U4 "다음 분기 둔화를 지난해 가격 인상 효과", microsoft.F1.xbox V4 "다음 분기 매출 감소", amazon.F5 V3·U12·microsoft.F5 U5 "연말". 모두 연·분기를 적는다.

14. 같은 사실의 표현이 갈린 곳(정리 거리). [하]
   - OpenAI 의 다음 세대 모델 출시를 openai.F2.model V4·openai.F3.model V6 은 "멈췄다", openai.F2.model D5(WSJ "scrapping")는 "접었다"로 적는다. 발췌는 "scrapping" 이라 "접었다"가 맞다. openai.F3.model V6 첫 문장("멈춘 것은 매출 지표가 움직이지 않은 지연이 아니라 지연 조항(감속)을 적용하지 않았다")은 문장이 성립하지 않으니 다시 쓴다.
   - openai.F2.model D3 "28위"는 전체 모델 기준 순위이고 같은 판단 V2 는 회사별 최고 모델끼리의 순위(6위권)다. 줄에 "(전체 모델 기준)"을 적는다.
   - meta.F9 U2 의 최근 1년 잉여현금흐름(영업현금흐름 − 설비투자)과 D1 의 분기 잉여현금흐름(회사 정의, 금융리스 원금 상환 포함)은 정의가 다르다. 줄에 정의를 적는다.

15. 검증기·작성 규칙 제안. [하]
   - `SELF_CONTAINED_BANNED` 에 판정·올릴·내릴·`relevance` 문장용으로 '시범', '조율자', '같은 실행|이 실행', '사용자 결정', 컷오프 뒤 날짜(문장 안 `20\d\d-\d\d-\d\d` 가 `info_cutoff` 보다 늦고 계획 단서가 없는 것), `TRG-\d+` 를 더한다(과제 2).
   - `relevance` 가 '추론:'·'사실:' 로 시작하는지 검사한다(과제 9). 올릴·내릴 줄의 숫자가 표지 발췌에 있는지, 영문 고유명사가 발췌에 있는지 기계로 걸러 줄–발췌 간극(과제 5)을 막는다. 이번 리뷰의 간이 점검(숫자·영문 고유명사 포함 여부)은 과제 5 의 아홉 곳 가운데 네 곳(microsoft.F3.application U1, microsoft.F1.linkedin D1, microsoft.F1.other D1, amazon.F4 D3)과 과제 6 의 숫자 오기를 잡았다. 나머지 다섯 곳은 문장을 읽어서 찾았다.
   - 방향 칸 줄에서 '세지 않는다'·'넣지 않는다'·'(미확인)'이 계획·발표 단서 없이 나오면 경고한다(과제 8).
