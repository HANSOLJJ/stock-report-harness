---
reviewer_agent: fact-checker
session: v30full-fact-sources-b
reviewed_at: 2026-10-20
---
검토자: fact-checker(사실·출처 — NVIDIA·Oracle·Tesla 세 회사의 근거·판단·트리거·시장 관측 전수)
결과: needs_fix

## 범위와 방법

- 대상은 이번 실행에서 더한 근거 EV-nvidia-118~130, EV-oracle-062~074, EV-tesla-076~098(49건) 전부와, 세 회사 판단(`nvidia.*`·`oracle.*`·`tesla.*` 42개)의 올릴·내릴 근거 줄이 인용한 근거 전부(옛 실행에서 이어받은 것 포함, 서로 다른 근거 306건), 세 회사 트리거 28건, 시장 관측(ev_bev·semiconductors)이다.
- 등록·확정 점검은 기계로 전수했다. 세 회사 판단의 `source_ids`, 근거의 `source_id`, 관측의 `source_id`, 트리거의 `evidence_ids`·`source_ids` 가 모두 `sources.json`·`evidence.json` 에 있다(누락 0). 세 회사 근거 291건은 모두 `confirmed` 이고 판단이 인용한 근거 306건 가운데 `reviewer`·`reviewed_at` 이 없는 것은 없다. `published_at_utc` 는 전부 정보 컷오프(2026-10-14) 이하다. EV-oracle-071(NetSuite, 2026-10-14T13:16Z)은 컷오프 당일이고 코드의 비교가 일 단위(`[:10]`)라 통과다.
- 원문 대조는 SEC 공시를 `scorecard_cli.py sec-get` 으로만 받아(캐시 sha256 이 등록 값과 같은 것은 일치 확인) 글자 대조했다. 새 근거 중 SEC 36건은 모두 발췌가 원문과 글자 그대로 같다. 인용된 SEC 근거 전체 179건(옛 근거 포함)도 같은 방식으로 대조해 172건이 일치했고, 나머지 7건은 아래 F-08 이다. 비SEC 새 근거 13건은 원문 페이지를 열어 대조했다. 스크립트 요청이 403 인 NetSuite·WhichCar·Gartner·Marvell·OpenAI·Axios·The Hill 은 앱 안 브라우저로 열었다(봇 확인 화면 없음). heise 는 본문 전체를 읽었다.
- 판단 줄 전수: 올릴·내릴 근거 줄마다 표지가 가리키는 근거의 발췌가 그 줄의 사실을 받치는지 줄 단위로 읽었다. 숫자(매출 줄 합, 비율, 날짜)는 원문 값으로 다시 계산했다.
- 시장 관측: Gartner 보도자료 Table 1 의 열 개 업체와 Total Market 의 2024·2025 값이 관측과 모두 같다(NVIDIA 125,703/793,449, 76,692/655,882 등). Counterpoint 영문 표는 'Tesla' 행이 Q2 2026 13%·Q2 2025 18%, 'BYD Auto' 행이 12%·12% 이고, 같은 페이지 독일어 표는 행 순서가 반대(BYD Auto 18% , Tesla 12% — Q2 2025)이며 본문이 BYD 를 'clear lead', Tesla 를 'second-largest, nearly 12%, sales +25%' 로 적는다. 정의표 note 의 ①②를 원문에서 확인했고 ③④(TrendForce 2Q25 BYD 18.3%, 2Q26 BYD 1위·Tesla 2위 +25%)는 검색으로 같은 내용을 확인했다. 행 이름을 바로잡아 읽은 값은 원문으로 뒷받침된다. 가격 기준일은 관측의 최신 가격 행이 2026-10-09 로 실행 설정(price_as_of)과 같다.
- 이해상충 표기는 보지 않았다. 투자 조언·매매 지시·수익 보장·FOMO 표현은 draft·근거·판단·트리거에서 찾지 못했다(검색어 일치는 '사 오는'·'목표가가 밀렸다' 같은 일반 문장뿐).

## 발견 사항

### needs_fix (점수에 닿음)

**F-01. Oracle ② 층 밖 사업의 패러다임 적응 `none`(0)이 찾지 못함에서 왔는데 열리는 회사 발표가 있다.**
- 위치: `judgments.json` `oracle.F2.outside` inputs `adaptation: none`, 판정 칸 둘째 줄("…두 사업 설명과 2026-04-17~10-14 Oracle 뉴스 후보 제목에서 찾지 못했다").
- 문제: 0 의 근거가 10-Q 주석 9 사업 설명과 뉴스 후보 *제목* 검색 실패다. 규칙 2.6(사다리 점수 부분은 미확인이면 40%, 0 처럼 나쁜 값으로 바꾸지 않는다)과 v3.0 미확인 처리 점검 대상이다. 열리는 반증이 있다. Oracle 보도자료(2026-03-24, `oracle.com/news/announcement/oracle-unveils-ai-database-agentic-innovations-for-business-data-2026-03-24`, 열림·200)는 "customers running on Oracle Exadata further benefit from Exadata Powered AI Search, which enables agentic AI at the highest scale" 라고 적는다. Exadata 는 하드웨어 사업(Engineered Systems)의 대표 제품이다. 같은 상황의 Amazon 층 밖 사업(`amazon.F2.outside`)은 "출시와 채택 지표를 확정 근거로 가르지 못했다" 며 `unknown` 으로 뒀다. Oracle 만 같은 상황에서 0 이라 Q03(같은 잣대) 문제이기도 하다.
- 점수·순위: 층 밖 가중치 0.1253 이 매출 줄(하드웨어·서비스 합 12.53%) 몫이다. `unknown`(2 → (2+0)×2 = 4)이면 ② 가 0.3085×10 + 0.3395×4 + 0.2267×4 + 0.1253×4 = 5.85 로 현재 5.35 보다 높아 정수 반올림 ② 5→6, Oracle 총점 5→6 이다. 순위는 10위 그대로(위 Alibaba·Palantir 9, 아래 SpaceX −1).
- 고칠 방법: `oracle.F2.outside` adaptation 을 `unknown` 으로 바꾸거나(Exadata 보도자료를 확정 근거로 올려 채택 지표 없음 → 4 가 아니라 미확인), 0 을 지키려면 "새 판용 제품이 없다"를 구조적 이유로 세우고 판정 칸에서 검색 실패 문장을 뺀다. 고친 뒤 research→calculate→draft→review 재실행. 규칙 일관성 리뷰의 Q03 표와 맞춰 한 번에 반영할 것.

### 근거 공백·표지 불일치 (점수 영향 없음 — 다음 실행 과제와 같은 묶음으로 고칠 것)

**F-02. 표지가 가리키는 발췌가 줄의 사실을 담지 않는다(9줄).** 원문에는 사실이 있는 경우가 대부분이라 발췌·locator 를 넓히면 된다. 점수는 이 줄들이 아닌 다른 근거로 정해졌다.
1. EV-oracle-073 발췌(첫 문단 셋째·넷째 문장)에는 "하드웨어 매출 15%·서비스 매출 5% 증가"가 없다. 원문 같은 문단 다섯째 문장("Services revenues were $1.4 billion, up 5%, and Hardware revenues were $0.8 billion, up 15%.")에 있다. 해당 줄: `oracle.F2.outside`·`oracle.F3.outside`·`oracle.F1.hardware`·`oracle.F1.services` 올릴 근거.
2. EV-openai-132(Stargate UAE) — `oracle.F5` 올릴 근거 "Stargate UAE 는 G42 가 짓고 OpenAI 와 Oracle 이 운영한다"(판정 칸 같은 문장 포함)는 발췌에도, 열어 본 OpenAI 페이지 전문에도 없다. 페이지는 파트너 G42·Oracle·NVIDIA·Cisco·SoftBank 와 '1GW, 2026 200MW 가동 예정'만 적고 누가 짓고 운영하는지는 적지 않는다. 사실이면 그것을 적은 다른 근거를 인용하고, 아니면 문장을 줄인다. OpenAI 상업 동맹은 EV-openai-028·082 로 서므로 점수는 같다.
3. EV-oracle-070 발췌(첫 문단)에는 Gemini·OpenAI 가 없다. 원문 뒷 문단 "powered by industry-leading frontier models including Gemini and OpenAI" 에 있다. 해당 줄: `oracle.F8` 내릴 근거.
4. EV-oracle-069 — `oracle.F8` 내릴 근거와 판정 칸이 "Gemini 를 Fusion 애플리케이션·NetSuite 에 넣고 … 제공한다"로 현재형으로 적었다. 원문은 "is planned to make Gemini models available in Oracle AI Agent Studio for Fusion Applications", "Oracle plans to use Gemini models for embedded AI use cases in Oracle Fusion Applications and Oracle NetSuite" 라는 계획이고, 지금 되는 것은 OCI Enterprise AI 접근뿐이다. 판정 칸이 이 경로로 칸을 내리지 않는다고 적어 점수는 같지만 계획을 현재 사실로 쓴 문장은 고친다(Q09).
5. EV-tesla-095 발췌에는 '연방법원'·'1만 명'이 없다(다음 문장 "Federal Court judge Tom Thawley … a lawyer representing 10,000 Australian Tesla drivers" 에 있다). 해당 줄: `tesla.F5` 내릴 근거.
6. EV-anthropic-064(Axios) — `oracle.F7` 내릴 근거와 판정 칸 "OpenAI 가 투자자에게 알린 연환산 매출은 $700억보다 $200억 적다"는 원문과 거꾸로다. 원문은 OpenAI 연환산 매출이 $500억이고 보도된 $700억은 투자자 비교용으로 부풀린(gross-up) 값이라고 적는다. 발췌에는 '$200억 적다'도 없다(제목과 첫 문단에만). ⑦ 가로축 '큼'은 연 $600억 ÷ 매출 83.6% 로 정해져 점수는 같다.

**F-03. 새 근거의 locator·제목 오기.** EV-nvidia-118 은 제목·locator 가 "Note 16 Segment Information" 이라고 적지만 2025-10-26 10-Q 의 Segment Information 은 Note 13 이다(Note 16 은 FY2026 10-K 번호). EV-nvidia-123 locator "넷째·다섯째 문장"은 실제 둘째·셋째 문장이다. EV-oracle-064 locator 의 절 제목은 'Enterprise Ontologies' 가 아니라 'Enterprise Ontology' 다. 값·문언은 맞다.

**F-04. 열리는데 판단이 쓰지 않은 보도(규칙 2026-10-12 위반, 점수 영향 없음).**
- Tesla ⑤ 판정 칸: "스웨덴 IF Metall 의 쟁의가 2026-08 끝났다는 보도와 NHTSA 가 Robotaxi 의 학교 구역 감속을 조사한다는 2026-10 보도는 원문을 근거로 확정하지 않았다". 둘 다 열린다. IF Metall 은 2026-08-19 쟁의 중단(basenor.com, 2026-08-13·18 갱신, 열림)이고 끝난 사건이라 세지 않는 것이 맞다. NHTSA 는 2026-10-09 결함 청원 파일 DP26010 을 열었다(`electrek.co/2026/10/12/nhtsa-tesla-robotaxi-school-zone-speeding-petition/`, 열림). 정식 조사가 아니라 청원 판단이고 미국 관할이라 관할 수는 그대로 3 이다. 같은 기사는 Cybercab 인증을 둘러싼 NHTSA 질의·특별 명령도 적는다(역시 미국, 점수 같음). 근거로 확정하거나 사유를 바꿔 적을 것.
- Oracle ⑤ 판정 칸: 개인정보 집단소송 합의 지급(2026-09-21~12-07, The Hill 열림 — 사실 일치), 2025 의료 침해 사고, Project Jupiter 가스관 경로 거부·불가항력 통보, 위스콘신 전력 승인 대기를 "확정 근거로 확인하지 못해" 세지 않는다고 적었다. 모두 후보 제목 수준이고 확정 근거가 없다. 판정 칸은 "⑧·⑨ 의 데이터센터 일정에서 본다"고 하지만 `oracle.F8`·`oracle.F9` 판단에는 이 사건 언급이 없다(트리거 TRG-022 에만 있다). 문장을 맞출 것.
- NVIDIA ② 판정 칸: "MLPerf 결과표 원본에서 벤치마크마다 가속기당 1위를 직접 대조하지는 못했다(미확인)". 결과표는 공개돼 있다(`github.com/mlcommons/inference_results_v6.1` summary.csv). closed·available·datacenter 를 가속기당 처리량으로 직접 대조했다. VLM·DeepSeek-R1(Offline)·GPT-OSS-120B·Llama2-70B·Llama3.1-8B·Whisper 모두 NVIDIA(GB300·B300)가 1위이고 DLRM-v3 는 AMD MI355X 가 유일한 제출이다. GPT-OSS-120B 에서 8-GPU MI355X 15,227 이 8-GPU B300 14,321·B200 11,436 보다 높다는 AMD 주장도 표로 확인되지만 GB300 16,635 가 1위다. 판단의 '1위이고 3개월 안(6)'은 표로 뒷받침되고 '미확인' 문장은 불필요하다. 점수 영향 없음.

**F-05. 판정 칸 사실에 확정 근거가 없다.**
- Oracle `oracle.F5` 지분 동맹·`oracle.F7` 세로축: "합작법인(TikTok USDS Joint Venture)은 Oracle 이 용량을 늘려 맞추는 OCI 대형 계약 고객이다"를 받치는 확정 근거가 없다. EV-oracle-030 은 'TikTok' 이라고만 적고 EV-oracle-009 는 JV 지분 15%·비시장성 투자만 적는다. 공개 보도(The Register 2026-01-23, DCD 등)는 Oracle 이 JV 의 미국 사용자 데이터를 자기 클라우드에 호스팅한다고 적어 사실로는 서지만 근거로 올라 있지 않다. 근거를 확정해 인용하면 점수는 그대로다. 못 하면 ⑤ 지분 동맹 2 가 빠져 ⑤ 9→7, ⑦ 세로축이 흔들려 −12→−8 쪽이다.
- Oracle `oracle.F2.cloud`: "OCP 작업반(2026-10-13 발표)은 Marvell·Microsoft 와 함께 만든 중립 기구 작업이고 채택한 주요 회사가 아직 없다" — 원문(Marvell 보도자료, 앱 안 브라우저로 열림)과 일치하나 근거 장부에 없다. 서버 내장 HSM 규격이라 시스템·칩 층 소관이고 Oracle 가중치가 0 이라 점수 영향도 없다.
- NVIDIA `nvidia.F5` 판정 칸의 "NVIDIA 가 지분을 넣은 … Intel", "Intel 지분과 공동 개발"은 근거 장부에 없다. 세지 않는 쪽으로 쓰여 점수 영향은 없다.

**F-06. Tesla ⑧ 공급 −4 의 전제(결정 유지, 어긋나는 자리만 적는다).** heise 원문은 2025-07-28 게시이고 "Samsung is currently producing the AI4 … with 4-nanometer technology", AI5 는 "TSMC for the time being" 이라고 적는다(발췌와 글자 일치, 판단이 2025-07·2차 보도로 날짜를 적은 것도 맞다). 기사에는 "Samsung 한 곳"도 "모든 차량"도 없다. 판단의 "모든 차량에 넣는 AI4 를 Samsung 한 곳이 만든다"에서 '모든 차량'·'한 곳'은 판단의 추론이다. EV-tesla-064(AI3 하드웨어 고객 차량에 FSD v14 lite 배포)는 AI3 차량이 현장에 남아 있음을 보이고, EV-tesla-034(AI5 두 변형, 파운드리마다 하나)는 `evidence_up` 에 이미 들어 있다. Apple 과 같은 근거 등급이라는 결정과는 어긋나지 않는다. 위치: `tesla.F8` inputs.supply.note·판정 칸 첫 두 줄·TRG-301 observation.

**F-07. 낡은 문장·경위가 현재처럼 읽힘.**
- 근거 `relevance` 에 이전 실행 점수가 "지금 … 점이다"로 남았다: EV-nvidia-004·008·083("지금 NVIDIA ④ 판단은 3점", "② 판단은 4점"), EV-tesla-004("⑤ … 2점이다"), EV-tesla-007·008·057("③ 3점", "④ 4.5점"), EV-tesla-050("이어받은 ① 판단은 2점"). 현재 값은 NVIDIA ④ 10·② 12, Tesla ⑤ 7·③ 4·④ 12·① 7.0 등이다. `research.md` 에 7줄로 실리고 draft·report.html 에는 없다.
- TRG-303 observation 의 호주 집단소송 상태("2026-07-31 까지 증거 개시를 끝내라는 명령을 받은 단계")는 5월 기사 시점이다. 기한이 지났고 2026-09-01 심리(Reuters, 판사가 독립 전문가 접근 명령 가능성 언급)에서 사건이 이어지는 것을 확인했다. 호주 전선 '진행 중'은 맞다(Tesla ⑤ 관할 3 곳 유지).
- EV-oracle-040 은 2019-10-15 AWS 블로그다. `oracle.F1.software`·`F3.data_platform` 이 날짜 없이 현재 대체재 출하의 근거로 쓴다(F3 모방 수는 10-K 경쟁사 목록 EV-oracle-024 로도 같다).
- Tesla ⑧ 고객 축 `not_disclosed` 는 10-K·10-Q 본문 검색 실패에 서 있다(10-Q 2026-06-30 도 매출채권 10% 이상 없음만 적는다). ⑧ 점수는 공급 축 −4 가 정해 영향 없다.

**F-08. 근거 대조에서 걸린 7건.** EV-nvidia-024·054·055·056·064·065 는 값·행 이름이 모두 일치하고 머리글 행의 글자 구성만 원문과 다르다(표 머리글 합성). EV-tesla-008 은 등록 URL 이 8-K 표지(`tsla-20261002.htm`)인데 발췌는 첨부 Exhibit 99.1(`exhibit991111111.htm`, sec-get 으로 받아 발췌 일치 확인)에 있다. EV-tesla-001·003·008 은 `published_at_utc` 가 null 이다(제출일 2026-07-23·2026-09-29·2026-10-02 로 컷오프 이하).

### 확인된 것(요약)

- 새 근거 49건과 세 회사 판단 줄 대부분은 출처 등록·발췌 일치·날짜·확정 상태를 만족한다. 새 근거의 URL 은 모두 열렸다(SEC 는 sec-get 캐시, 비SEC 는 직접).
- 숫자: Tesla 매출 줄 6개 합 $103,619M, Oracle 6개 합 $71,776M, NVIDIA 두 줄 합 $302,969M(관측 revenue_ttm 302,970 과 $1M 차, 반올림), 가속도 배수(Tesla 1.506→1.558, NVIDIA 1.9239→2.1662, Oracle 클라우드 1.932→2.207·데이터 0.979→0.970·응용 1.103→1.099), NVIDIA ⑧ 1.19배·$199B/0.66배, Oracle ⑧ 4.49배·⑨ 2.06배·1.61년, Oracle ⑦ 연 $60B/83.6%, Tesla 중국 매출 22.1%·17.5%, 상하이 설치 능력 40% 모두 원문 값으로 재계산해 맞다.
- 부재 주장: Tesla 10-K·10-Q 에 매출 기준 10% 이상 고객 문구 없음, 2026-06-30 10-Q 에 미개시 리스 없음, Oracle 10-Q 에 회전여신 변경 기재 없음은 본문 검색으로 확인했다.
- 트리거 28건(NVIDIA 11·Oracle 8·Tesla 9)은 모두 `watching`, 기한이 2026-11-15 이후이고 근거·출처가 등록돼 있다. `carry` 확인 문장(19건, 나머지 9건은 이번 실행 신규)은 기준일까지 조건 사건이 없다는 판단이 후보·근거와 맞는다. `research.md` 의 '이전 트리거 처리' 표는 pilot10 43건만 싣고 v21 에서 옮긴 이 19건의 확인은 `triggers.json` carry 에만 있다. 발동 트리거 재검토 표에는 세 회사 행이 없다.

## 체크리스트 (사실·출처 영역이 판정할 수 있는 항목)

| ID | 결과 | 근거 |
| --- | --- | --- |
| Q03 | fail | F-01. 같은 상황(층 밖 사업의 새 판용 제품을 못 찾음)을 Amazon 은 unknown, Oracle 은 0 으로 매겼다. 규칙 일관성 리뷰와 맞춰 결정. |
| Q05 | pass | 이해상충 표기는 보지 않는다(2026-10-02 지시). 출처가 이해당사자라는 이유로 점수를 가른 칸은 없다. |
| Q09 | pass | 계획을 현재 점수에 넣은 칸은 없다. 다만 Oracle ⑧ 줄이 Gemini 탑재 계획을 현재형으로 적었다(F-02-4, 점수에 안 씀). |
| Q24 | pass | Tesla IF Metall 쟁의 종료, Oracle $115M 합의 지급 단계는 끝난 사건으로 세지 않았고 사실이 맞다. |
| 그 밖 | not_applicable | Q01·Q02·Q04·Q06~Q08·Q10~Q23·Q25 는 규칙 일관성 영역이 판정한다. 재무 항목은 재무 계산 리뷰가 본다. |

## 다음 실행 과제

1. F-02·F-03·F-08 은 근거 발췌·locator·등록 URL(EV-tesla-008)·제목을 고쳐 줄이 받치는 사실과 일치시킨다. EV-openai-132 줄은 근거를 바꾸거나 문장을 줄인다.
2. F-04·F-05 의 보도·사실(Exadata Powered AI Search, TikTok JV 호스팅, OCP 작업반, DP26010, 합의 지급)은 열어서 확정 근거로 올리거나 사유를 바꿔 적는다. 후보 제목 수준의 문장을 판정 칸에 두지 않는다.
3. 근거 `relevance` 의 이전 실행 점수(F-07)는 현재 판단과 어긋나므로 재생성하거나 지운다. 새 근거를 올릴 때 `published_at_utc` 를 비워 두지 않는다.
4. 점수·결정에 닿는 2차 보도(Tesla 공급 −4 의 AI4 제조사, OpenAI $300B 약정)는 날짜와 근거 등급을 판정 칸에 계속 적는다. 1차 자료(Tesla·Samsung 공시, Oracle 10-Q RPO 고객 구성)가 나오면 먼저 갈아 끼운다.
