---
reviewer_agent: confirmation(opus)
session: v30full-confirmation
reviewed_at: 2026-10-20
---
검토자: confirmation(opus)(확인 리뷰 — 1차 리뷰 일곱의 needs_fix 해소, 수정 묶음 PRP-133~202 와 새 근거 22건·새 관측 1건, 회사를 가로지른 새 어긋남, 화면 문장 결함, 320·375px 표시, 체크리스트 Q01~Q25 최종 판정)
결과: pass

검토 기준. `results.json` results_hash `b8299899bf24b5ec62f89fc45160fa9af96d04af01590ebf0c692b7b149c90e7`, `draft.md` 파일 sha256 `1c3cdcef52cfd314e17bdca0b79a9b23e416cf79dc715ddd97828280faf81c02`. 확인용 HTML(`scratchpad/full/render/report.html`)의 `results-hash` 메타가 같은 값이고, 그 폴더의 `draft.md`·`preview.md` 는 실행 폴더 것과 바이트가 같다. `review.md` frontmatter 의 두 해시는 수정 전 값(2ecccf10…·2efc197d…)이라 `validate_report_contract.py` 가 리뷰 무효 오류 둘과 상태 오류 하나를 낸다. 나머지 검사(스키마·자기완결 문장·세 칸·방향 줄 표지·재판단 정책·결정적 재계산·초안 순위표·리뷰 구조)는 모두 ok 다. `review.md` 는 이 해시로 다시 만든 뒤 채운다.

## 범위와 방법

- 1차 리뷰 일곱(rule-consistency, fact-sources-a·b·c, financial-calc, evidence-bullets, output-readability)과 수정 지시(`full-fixbatch.md`), 조율 메모 「E9 리뷰」 절을 읽었다.
- needs_fix 아홉 건(규칙 F-1~F-5, 사실 a F-1~F-3, 사실 b F-01, 사실 c 발견 1, 재무 발견 1)은 `judgments.json` 의 판정·올릴·내릴 칸과 inputs, `results.json` 의 calc 로 하나씩 확인했다. 수정 묶음 제안 PRP-133~202 70건은 모두 `accepted` 다.
- 새 근거 22건은 원문을 다시 열어 발췌 조각을 기계로 대조했다. SEC 넷(EV-microsoft-107, EV-alibaba-114·115, EV-nvidia-131)은 `scorecard_cli.py sec-get` 캐시로, 비SEC 열넷은 스크립트로 받은 본문으로, 403 이 난 넷(MedPage Today, CourtListener 사건 기록 셋)과 본문이 스크립트로 렌더되는 Meta 블로그는 앱 안 브라우저의 내 탭에서 본문을 읽었다. 법원 PDF 셋(Dkt. 580·602·606)은 받은 파일을 텍스트로 바꿔 줄 번호를 빼고 대조했다. 봇 확인 화면은 만나지 않았다.
- 새 관측 `alibaba.equity_investment_gains_ttm.2026-06-30` 은 6-K(2026-08-20) 비 GAAP 조정표의 13,128·5,364 를 캐시 원문에서 찾았고, 20-F 의 74,416 은 재무 리뷰가 원문으로 확인한 값과 같다. 다른 회사 같은 관측의 정의·기간·부호와 견줬다.
- 기계 점검: 판단이 가리키는 근거 전부 존재·`confirmed`·출처 등록·게시일 컷오프 이하, 판단·트리거·관측의 `source_id` 누락 0, 관측 `as_of` 컷오프 이하. 게시일이 null 인 근거는 EV-amazon-001·002, EV-meta-001, EV-microsoft-004 넷이 남았다(Tesla 셋은 채워짐).
- 회사를 가로지른 점검은 ④ 기기 칸 열네 회사, ③ 가속도 입력 서른여덟 층 전부, ⑤ 소송·운동 전선의 성격을 표로 놓고 봤다.
- 화면: 확인용 HTML 을 로컬 서버(127.0.0.1)로 띄워 Playwright 에서 320·375px 로 쟀다. 앱 안 브라우저와 Playwright 모두 `file://` 주소를 열지 못해 이 방법을 썼다.
- 이해상충 표기는 보지 않았다. 실행 파일은 고치지 않았다.

## 발견 사항

점수·순위·체크리스트 판정을 바꾸는 발견은 없다.

### 1. needs_fix 해소 확인

| 1차 발견 | 확인한 상태 | 판정 |
|---|---|---|
| 규칙 F-1 amazon.F4·meta.F4 기기 AI 사슬 | 둘 다 '예' 유지. Amazon 은 EV-amazon-106(About Amazon 2025-09-30: AI 가속기를 담은 AZ3 칩으로 판매 중인 Echo Dot Max 가 대화 감지), Meta 는 EV-meta-104(Meta 블로그: Ray-Ban Display 와 함께 파는 Neural Band 가 근전도 원신호를 기기 안 기계학습으로 처리, 2025-09-30 미국 판매). 두 판정 칸은 "생성형 응답이 기기 안에서 도는지는 미확인"을 따로 적었다. Alphabet 도 EV-alphabet-122(Pixel 10 Tensor G5 가 Gemini Nano 를 완전히 기기 안에서 돌림)로 받쳤다 | 해소. 규칙 2.10 기기 조건은 "기기 안에서 AI 가 돌아가는 제품이 출하될 때"이고, 생성형만을 요구하지 않는다. 같은 잣대(출하 제품 안의 기계학습 추론)를 Microsoft Surface(기기 안 AI), Alibaba Qwen Glasses(Himax 기기 안 시각 추론), NVIDIA DGX Spark(로컬 AI), Tesla 차량 칩, Apple 에 똑같이 댔다. Amazon 근거는 "AI edge models of the future" 라는 미래 표현이 섞여 확신이 가장 낮지만, 같은 원문에 "Echo Studio … include the more advanced AZ3 Pro … adding support for state-of-the-art language models and vision transformers" 와 "The Echo Dot Max and Echo Studio are now available for purchase" 가 있어 출하 제품의 기기 안 AI 는 원문으로 선다(과제 9) |
| 규칙 F-2 alibaba.F1.cloud B | pricing `unknown`, `pricing_growth_quarters 1`, B 1.6. 판정 칸이 3월 분기는 인상 전이라 세지 않는다고 적음. Alibaba ① 9 → 8 | 해소. AWS·Apple Mac 과 같은 잣대 |
| 규칙 F-3·사실 b F-01 oracle.F2.outside | adaptation `unknown`(2), Exadata Powered AI Search(EV-oracle-076)를 올릴 근거로, 채택 지표 없음을 미확인 이유로 적음. Oracle ② 5 → 6 | 해소. Amazon 층 밖·Oracle 데이터·응용과 같은 '출시했으나 채택 지표 없음 → 미확인 2' |
| 규칙 F-4 oracle.F3 데이터·응용, palantir.F3.data_platform | 세 층 모두 tier `e`, 가속도 2.4. 판정 칸이 "④ 에서 AI 무관 매출로 센 줄이라 가속도 지표로 쓰지 않는다"를 적음. Oracle ③ 4 → 3, Palantir ③ 3 → 2 | 해소 |
| 규칙 F-5 nvidia.F2.chip_design | standards `[]`, 표준 선점 0, AWS·d-Matrix 줄에 "설계 단계·계획이라 점수에 넣지 않는다" 단서. NVIDIA ② 12 → 11 | 해소. ⑤ 의 같은 사실 읽기(설계 단계)와 맞음 |
| 사실 a F-1 amazon.F5 FDA 경고 서한 | EV-amazon-107 로 확정(앱 안 브라우저로 원문 대조, 2026-10-07 게시, 2026-10-01 Jassy 앞 서한·영업일 15일 회신 요구 일치). 비용형 전선(미국)으로 넣고 법적 구속력 있는 명령이 아니라 시정 요구라 구제 조치로 세지 않음. ⑤ 11 그대로 | 해소. 비용형 상한 −6 이 이미 서 있어 점수 같음 |
| 사실 a F-2 microsoft.F4 금액 | 올릴 1 이 $202,305M(계산) | 해소 |
| 사실 a F-3 microsoft.F1.other | 내릴 1 이 EV-microsoft-107(8-K Ex.99.1 "Revenue previously reported in Other is now reported within Windows OEM and devices and Productivity and server licensing", 캐시 원문 일치)을 가리키고 옮겨 가는 곳 둘을 적음 | 해소 |
| 사실 c 발견 1 openai.F5.impl48 Musk 소송 | 판정 칸이 평결(2026-05-18)·채택(05-20)·남은 청구 서면 일정(06-10)·조정인 임명(07-01)·반소 답변(08-10)·항소 공언을 EV-openai-175~179 로 적고, 영리 전환 청구를 `structural_unknown`, 같은 사건의 반독점 청구와 X.AI 영업비밀 항소(26-4486, EV-openai-180·181)를 비용형으로 넣음. ⑤ 8 → 6. TRG-062 갱신, TRG-366·367 새로 | 해소. 아래 3절에서 잣대를 따로 봤다 |
| 재무 발견 1 Alibaba ⑥ | 관측 등록(RMB66,652M ÷ 6.8980 = US$9,662.5M, 세전, 이익 양수, 최근 1년). P1 조정 적용, P4 영업외 비중은 "P1 이 평가손익을 조정했다 — 보지 않는다"로 건너뜀(Q01). ⑥ −14 → −12, Alibaba 9 → 10 | 해소. 정의 폭은 과제 5 |

수정 뒤 결과는 Alphabet 43 · Meta 41 · Amazon 32 · TSMC 31 · Microsoft 24 · Apple 24(공동 5위) · NVIDIA 19 · Alibaba 10 · Palantir 8 · Oracle 5 · SpaceX + xAI −1 · Tesla −1(공동 11위) · OpenAI −6 · Anthropic −13 이고, draft 카드 머리·순위표·preview 가 이 값과 같다. 시범 다섯 회사의 바뀐 판단 셋(alphabet.F4·F3.cloud, anthropic.F5)은 문장만 바뀌어 점수가 같다.

### 2. 새 근거·새 관측

- 22건 모두 출처가 `sources.json` 에 있고 `confirmed` 이며 게시일이 2026-10-14 이하다(가장 늦은 것 EV-tesla-100 2026-10-14T21:33Z, 날짜 단위 비교로 통과).
- 발췌 대조: EV-amazon-106·107, EV-meta-104, EV-alphabet-122, EV-microsoft-107, EV-alibaba-114·115, EV-oracle-075·076, EV-nvidia-131, EV-tesla-099~103, EV-openai-175~181 전부 원문에 있다. 기계 대조에서 걸린 조각은 모두 표 칸 구분, 링크 앞 공백, 단어 결합 문자(⁠), 법원 문서 줄 번호 때문이었고 문언은 같다. CourtListener 기록은 2026-10-19 갱신본에서 Dkt. 572·602·606·609 가 있고 2026-09-29(Dkt. 615, 변호인 철회) 뒤 최종 판결이 없음을, 항소 26-4486 은 2026-08-25 항소인 서면 접수 뒤 진행 중임을 확인했다.
- 인용 줄과의 대응: 새 근거를 가리키는 줄(amazon.F4 U13, amazon.F5 D6, meta.F4 U18, microsoft.F1.linkedin D2·other D1, alibaba.F1.cn_ecom_direct D1·all_others D1, oracle.F5 U3, oracle.F7.fix52 D11, oracle.F2.outside U1, tesla.F5 D8, openai.F5.impl48 U6·D14~D16, alphabet.F4 U16, TRG-151·302·303·366·367)은 모두 발췌 범위 안이다. EV-nvidia-131 은 nvidia.F5 의 `evidence_ids` 에만, EV-tesla-101·103 은 tesla.F5 판정 칸 서술(표지 없음)에만 쓰인다. 판정 칸은 표지를 요구하지 않아 결함이 아니다.
- 새 관측: 정의(지분증권 평가·처분 손익, 세전, 지분법 손익 제외)·기간(2025-07-01~2026-06-30)·부호(이익 양수)·환율(alibaba.*.rs1006 과 같은 6.8980)이 다른 회사 관측과 같다. 다만 쓰인 줄이 비 GAAP 조정표 줄이라 지분법 피투자사의 간주 처분과 자회사 처분 이익이 섞일 수 있음을 `basis.not_separable` 에 적었고, 연간 현금흐름표로 좁힌 지분증권 순이익 58,365 도 P1 바닥(재무 리뷰가 잰 문턱 약 RMB 293억)을 넘어 점수가 같다.

### 3. 회사를 가로지른 새 어긋남

- **④ 기기 칸 AI 사슬.** 판매 칸이 있는 아홉 회사(Alphabet·Apple·Amazon·Meta·Microsoft·Alibaba·NVIDIA·Tesla)가 모두 '출하 제품 안에서 AI 추론이 돈다'는 회사 1차 근거로 '예'를 받친다. 근거 깊이는 생성형 모델(Apple·Alphabet)에서 신호 처리 기계학습(Meta Neural Band·Amazon AZ3)까지 갈리지만 규칙 문언이 생성형을 요구하지 않아 같은 잣대 안이다. 판매가 없거나 준비 중인 다섯 곳은 해당 없음. 어긋남 없음.
- **③ 가속도와 규칙 2.4.** 서른여덟 층의 가속도 입력을 전부 봤다. 단계 c 대리 지표는 Google Cloud·AWS·Azure·OCI·Alibaba 클라우드·xAI AI Solutions·TSMC HPC 로, 모두 ④ 가 AI 수요로 센 줄이다. ④ 가 AI 무관으로 센 줄(Oracle 라이선스·지원, Oracle 클라우드 응용, Palantir 두 줄, 각 회사 사용자 플랫폼)을 대리 지표로 쓴 층은 남지 않았다. 어긋남 없음.
- **⑤ 소송·운동의 구조형 판단.** Palantir 정부 계약 반대 운동은 사업 자체를 끝내라는 요구라 구조형(이미 정해진 결정), OpenAI Musk 영리 전환 청구는 영리 운영의 정당성을 다투지만 구한 구제가 자선 부문 배상과 이사 해임이라 판매를 멈추게 하지 않아 둘로 가를 수 없어 `structural_unknown` 이고, 판정 칸이 Palantir 잣대와 견준 이유를 적었다. 같은 사건의 반독점 청구, X.AI 영업비밀 항소, NYT·USA TODAY 저작권 소송(Microsoft·OpenAI 같은 값), 주 법무장관 소송, Meta·Tesla·Amazon 의 규제·소송은 모두 비용형이다. 규칙 ⑤ 의 "구조형이 아닌 쪽으로 끝까지 풀지 않는다(2026-10-19)" 대로 가르지 못한 성격을 나쁜 쪽에서 40% 로 풀었고, 엔진 계산(구조형 둘이면 −11.2, 빼면 −4, 40% 지점 −8.32)이 Anthropic(−8.32)·NVIDIA(−9.12)와 같은 식이다. 평결이 채택됐어도 최종 판결 전이라 항소가 남아 규칙 2.11 의 '끝난 사건'이 서지 않는다는 판단도 법원 기록과 맞다. 어긋남 없음.
- **Oracle TikTok 합작법인.** EV-oracle-075(합작법인 설립 발표, Silver Lake 게재: 미국 사용자 데이터와 추천 알고리즘을 Oracle 미국 클라우드 환경에, Oracle 은 15% 관리 투자자)가 ⑤ 지분 동맹 2 와 ⑦ 세로축 '돌아옴'을 받친다. 규제 준수 구조상 데이터를 Oracle 클라우드에 두는 합작법인이라 네 질문의 '상대가 떠날 수 있나'도 서고, 1차 리뷰가 걱정한 ⑤ 9 → 7·⑦ −12 → −8 은 일어나지 않는다.
- **Microsoft 노동 인증 정지를 구제 조치로 읽은 것.** 규칙 예시의 '승인 거부'와 같은 성격(정부 프로그램 참여 정지가 효력 중)이고 점수를 깎는 쪽으로 읽어 미확인을 유리하게 푼 것이 아니다. 같은 실행의 Anthropic 국방부 배제·Alibaba 조달 금지도 구제로 읽었다. 경계 문장은 과제 11.

### 4. 화면에 실리는 문장 결함(근거 불릿 리뷰 1~7)

- 고쳐진 것: alibaba.F3.cloud V6(낡은 문장·"조율자" 삭제), oracle.F5 V8·V9 의 "시범", alibaba.F4·F5 의 "(TRG-…)", microsoft.F3.application V1 의 정정 흔적, 아홉 회사 판단의 "사용자 결정(날짜)"·"사용자가 … 정해"(정의표가 없다는 사실 문장으로 바뀜), alibaba.F9 의 "엔진이"·결정 번호, Amazon·Microsoft 의 "같은 실행·이 실행" 열 곳, 줄이 발췌를 넘던 아홉 곳(EV-microsoft-085 발췌 넓힘·EV-microsoft-107 새로·"NPU" 삭제·"검색 위쪽에 AI 답변"·"출하한 칩은 확정 근거에 없다"·meta.F5 D10 이란 포함 등), microsoft.F4 금액, nvidia.F8 D11(사실만 쓰고 결론은 판정 칸에 추론 표시), Gemma 4 최상급 세 줄(자사 개방형 모델 가운데 가장 성능이 좋은), anthropic.F5 의 Meta 지수 줄(Muse Spark 1.3 가격으로 교체).
- 남은 것(draft 에 실림, 점수·체크리스트 무관, 과제 1): anthropic.F5 V11 "이 실행의 다른 회사도"(draft 4360행). 시범 승인본에서 그대로 이어진 alphabet.F1.other_bets V3 "이 실행에 없다"(190행), alphabet.F2.cloud V2 "같은 실행에서"(246행), alphabet.F2.chip_design·systems·model 의 "이 실행의 확정 근거", spacex-xai.F4 V1 "이 실행의 시장 정의표"(3520행). 계산 코드가 만드는 참고 줄 두 곳: SpaceX "이 실행에 그 시장의 정의표가 없어"(3550행), OpenAI "비상장사용 경로가 먼저다(사용자 결정 2026-09-17)"(4214행). 그 밖에 alibaba.F9.obsreg25 V5 "실행 결정에 따라", Qwen 최대 모델 공개 "처음으로" 줄 가운데 alphabet.F3.cloud D2·microsoft.F3.cloud D2 에 "(2차 보도)" 표시가 없고, Bing "처음으로 10억 명" 두 줄에 날짜가 없다.

### 5. 출력(B-1·B-2)

- CSS 가 들어갔다: `.uname{…min-width:0;overflow-wrap:anywhere}`, `.trig td.text{vertical-align:top;overflow-wrap:anywhere}`.
- 320px: 회사 카드 14장 모두 `scrollWidth == clientWidth`(271), 카드 안 요약 줄 넘침 0, Microsoft 의 `LinkedIn(Talent·Marketing·Premium·Sales Solutions)`·`Search advertising(…)` 이름 칸이 168px 안에 접혀 요약 줄 221px 안에 든다. 트리거 표 폭 271 = 래퍼 271(행 130), 페이지 가로 넘침 0.
- 375px: 카드 넘침 0, 요약 줄 넘침 0, 트리거 표 326 = 래퍼 326, 페이지 가로 넘침 0.
- B-3(순위 열)은 2026-10-13 사용자 지시(순위 열을 뺌)와 어긋나 받지 않았다는 조율자 판단을 그대로 둔다. 공동 순위는 카드 머리(`5위(완료 14개사 기준)`)와 draft 순위표에 보인다.

## 체크리스트 (최종 상태)

| ID | 결과 | 근거 |
|---|---|---|
| Q01 | pass | 같은 속성을 두 번 센 곳 없음. Alibaba ⑥ 은 P1 에서 평가손익을 조정하고 P4 영업외 비중을 건너뛰었다. 수출 통제(NVIDIA ⑤·Alibaba ⑧), 고객 자체 칩(⑤ 만), Palantir 정부 집중(⑧ 만)은 1차 판정과 같다 |
| Q02 | pass | 1차 fail 사유 셋 해소: 기기 AI 사슬은 회사 1차 근거로 받침(F-1), 인상 전 분기를 B 에서 뺌(F-2), AI 무관 줄 성장을 가속도에서 뺌(F-4). 시장 평균 단가·시장 성장률을 ① 에 넣은 곳 없음 |
| Q03 | pass | 1차 fail 사유(규칙 F-1~F-5, 사실 b F-01, 재무 발견 1) 모두 해소. 사건 교차표에 Musk 소송·TikTok 합작법인·FDA 서한을 더해도 자료 유무로 읽기가 갈린 곳 없음. Palantir 의 `equity_investment_gains_ttm` 은 아직 없으나, 원문으로 확인되는 하한(상장 지분증권 순이익 약 $41M 과 비상장 상향 조정)이 ⑥ 을 움직이는 문턱(세전 약 $98M)에 못 미치고 나머지(2026년 상반기 비상장 실현이익)는 금액이 공시되지 않아 지금 점수가 확인된 자료로 정해진다(과제 10) |
| Q04 | pass | ⑥ 은 비율 파라미터·성장 조정으로만 계산, 시총 크기를 근거로 쓴 판단 없음 |
| Q05 | pass | 새 근거는 법원 기록·공시·회사 1차 발표·보도이고 등급을 줄에 적었다. 이해상충 표기는 보지 않는다 |
| Q06 | pass | 1차 판정과 같음(토큰·트래픽 점유율은 부분 반영으로만) |
| Q07 | pass | 1차 판정과 같음 |
| Q08 | pass | 사실 c 의 보류 사유(Musk 사건 전제)가 법원 기록으로 고쳐졌다. OpenAI 전선은 성격(비용형 열다섯·구조형 미확인 둘)과 관할 수로 정했다 |
| Q09 | pass | 1차 fail 사유(NVLink Fusion 설계 단계를 표준으로 셈) 해소. Oracle ⑧ Gemini 탑재는 "넣을 계획이다", SB OAI Japan 은 "팔 예정"으로 고쳐졌고 지분 동맹은 맺은 지분으로 센다고 적었다. TRG-303 재검토 칸에 미래 점수가 없다 |
| Q10 | pass | 가속도는 모두 같은 정의 두 배수의 비, 누적값을 쓴 곳 없음 |
| Q11 | pass | 적자는 ⑨ 에서만 감점 |
| Q12 | pass | 모방 불가능성 8 없이 16 이상인 층 없음 |
| Q13 | pass | 공짜 전략은 거둘 장치가 있는 곳만(이미 정해진 결정) |
| Q14 | pass | 문 닫힘 증거로 20 을 받은 층 없음 |
| Q15 | pass | 파생 모델·개발자·NACS 채택사를 동맹으로 세지 않음 |
| Q16 | pass | 층 배정·사업 나누기는 1차 판정과 같고 수정 묶음이 바꾸지 않았다 |
| Q17 | pass | 벤치마크 없는 층은 (적응 + 표준) × 2. Oracle 층 밖은 적응 미확인 2 로 고쳐졌다 |
| Q18 | pass | Tesla–SpaceX 관계사 제외 유지. 합병 보도는 트리거로만(TRG-151·302) |
| Q19 | pass | 받은 투자 제외 유지. TikTok 합작법인은 Oracle 이 맺은 지분이다 |
| Q20 | pass | 조달 제외 유지 |
| Q21 | pass | ⑤ '상대가 떠날 수 있나'와 ⑧ '내가 떠날 수 있나'를 섞은 곳 없음 |
| Q22 | pass | 지분 평가이익은 ⑥ 에서만, ⑦ 입력에 없음 |
| Q23 | pass | 같은 하네스 안 순위만 비교 |
| Q24 | pass | 끝나지 않은 Musk v. Altman 과 X.AI 항소를 전선으로 고쳐 넣었고, 끝난 사건(IF Metall 쟁의 중단, Oracle 개인정보 합의 지급, Palantir Mopac)은 빼 둔다 |
| Q25 | pass | 모델 순위를 다른 층으로 옮긴 곳 없음, 공짜 전략은 거두는 층에서 셈 |
| 제목만 보고 확정·미확인 처리 금지(AGENTS 2026-10-12) | pass | 1차 fail(FDA 서한)이 원문 확정으로 풀렸다. Tesla 의 IF Metall·NHTSA DP26010 도 원문을 열어 확정했다(EV-tesla-101·103) |

## 다음 실행 과제

1. 4절의 남은 문장(anthropic.F5 V11, 시범에서 이어진 alphabet·spacex-xai 의 "이 실행" 문장, 계산 코드 참고 줄의 "이 실행"·"사용자 결정 2026-09-17", alibaba.F9 "실행 결정", Qwen "처음으로" 줄의 2차 보도 표시, Bing 날짜)을 완결된 현재 상태 문장으로 고친다. 검증기 `SELF_CONTAINED_BANNED` 에 '이 실행|같은 실행'·'사용자 결정'을 더하고, 계산 코드가 만드는 참고 줄도 같은 검사를 받게 한다.
2. 근거 `relevance` 에 낡은 서술이 남은 곳: EV-microsoft-105 relevance 의 "NPU 로"(발췌에 없음). 1차 근거 불릿 과제 9 의 이전 점수 문장과 함께 정리한다.
3. 새 트리거 TRG-366·367 의 `source_ids` 가 비었다(근거의 출처는 등록돼 있음). TRG-062 carry finding 의 "같은 날 … 더했고 따로 트리거를 단다"는 작업 경위라 현재 상태 문장으로 바꾼다.
4. 새 출처 대부분(SRC-WEB-amazon-021, SRC-WEB-meta-916, SRC-WEB-alphabet-913, SRC-WEB-oracle-921·922, SRC-WEB-tesla-020~024, SRC-WEB4-openai-008~014, SEC 넷)의 `sha256` 이 null 이다.
5. Alibaba 관측 raw 문자열의 "US$9,662.7M" 은 값(9,662.5)과 0.2 어긋난다. 정의 폭(비 GAAP 조정표 줄에 지분법 간주 처분·자회사 처분이 섞일 수 있음)은 재무 리뷰 발견 3(지분법 처분·희석 이익을 ⑥ 에 넣을지, TSMC 는 넣고 Microsoft 는 뺌)과 함께 규칙 문언으로 정한다.
6. oracle.F3.data_platform U1(멀티클라우드 AI Database 404%)은 판정 칸이 가속도에 쓰지 않는데 단서 없이 올릴 칸에 있다(1차 규칙 리뷰 「세 칸」과 같은 종류).
7. amazon.F4·meta.F4·alphabet.F4 의 기기 칸 판정 문장은 근거 깊이가 다르다(생성형 대 신호 처리 기계학습). 규칙 2.10 기기 조건에 "기기 안 기계학습 추론이면 생성형이 아니어도 인정"을 적어 두면 다음 실행에서 같은 질문이 반복되지 않는다.
8. ⑤ 구조형 기준에 '사업의 형태(영리 전환·지배구조)를 다투는 소송'을 어디에 두는지 한 줄 적는다(지금은 OpenAI 판정 칸의 추론으로 `structural_unknown`).
9. EV-amazon-106 발췌에 같은 원문의 AZ3 Pro 문장("adding support for state-of-the-art language models and vision transformers")과 Echo Studio 판매 문장을 더하면 '미래 모델용 가속기'라는 표현에 기대지 않고 기기 칸이 선다.
10. Palantir `equity_investment_gains_ttm` 을 등록한다(재무 리뷰 발견 2). 세전 약 $98M 이상이 확인되면 Palantir ⑥ −12 → −13, 조정총점 8 → 7 이다.
11. Microsoft ⑤ 노동 인증 정지를 구제 조치로 본 경계와 microsoft.F1.linkedin 참여자 효과 6(회원 수만으로)의 근거는 1차 규칙 리뷰 과제 11·1 그대로 남는다(둘 다 정수 영향 없음 또는 감점 쪽).
12. `review.md` 를 현재 해시(results_hash b8299899…, draft_hash 1c3cdcef…)로 다시 만들고 이 확인 리뷰와 1차 리뷰 일곱의 결과를 채운 뒤 `validate_report_contract.py` 를 다시 돌린다.
