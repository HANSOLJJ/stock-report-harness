---
reviewer_agent: rule-consistency(opus)
session: v30full-rule
reviewed_at: 2026-10-20
---
검토자: rule-consistency(opus)(규칙 일관성 — 14개사 가로질러 체크리스트 Q01~Q25, 회사를 가로지르는 표 셋, 직접 겨루는 쌍, v3.0 판정 재료, 근거 세 칸, 재판단 정책)
결과: needs_fix

## 범위와 방법

- 9개사(Amazon·Microsoft·Meta·NVIDIA·Oracle·Tesla·Palantir·Alibaba·OpenAI) 판단 130건을 판정·올릴·내릴 칸과 inputs 까지 전부 읽었다. 시범 5개사는 바뀐 판단 셋(alphabet.F3.cloud·anthropic.F1.claude·anthropic.F5)을 전부 읽고, 나머지는 9개사와 잣대를 견줄 자리(①A~C·② 적응·③ 수익모델과 가속도·④ 칸·⑤ 구조형 기준·⑦ 가로축·⑧ 칸)만 골라 읽었다. revision_history 는 보지 않았다.
- 대조 자료: `docs/scorecard/rules.md`(v3.0, 1~8절), `guide.md` 5.6·5.7, `results.json` 의 층·사업 calc(점수 영향은 이 calc 로 어림했고 확정값은 재계산으로 정한다), `evidence/evidence.json`(결정 근거의 발췌 확인), 공통 지시서의 이미 정해진 결정, 시범 pilot8 규칙 일관성 리뷰와 pilot10 판정.
- 원문을 새로 열지 않았다. 판단 문장의 숫자와 원문의 일치는 사실·출처·재무 계산 리뷰어 몫이다.
- 이미 정해진 결정(③ 공짜 전략, 시장 정의, 부분 반영, 40% 규칙, AIP 문언, 모방 회사 수, MAI 읽기, Palantir 구조형, AWS Interconnect, 클라우드 적응 지표, Tesla ⑧ 공급)은 다시 올리지 않았다.

## 발견 사항 (점수·순위·체크리스트 판정을 바꾸는 것)

- **F-1. amazon.F4·meta.F4 — 기기 칸의 AI 사슬 '예'가 미확인을 올리는 쪽으로 푼 것이다(규칙 2.10·2.1·2.6, Q02·Q03).**
  무엇이 틀렸나: 규칙의 기기 조건은 "기기 안에서 AI 가 돌아가는 제품이 출하될 때"다. 두 판단은 스스로 "Alexa+ 가 기기 안에서 도는지는 확정 근거에 없다(미확인)", "안경의 모델이 기기 안에서 도는지 서버에서 도는지는 확정 근거에 없다(미확인)"라고 적고 Alphabet Pixel 칸에 맞춰 '예'로 세었다. 수직계열화는 가점이고 2.1 은 가점에 실측만 인정한다. AGENTS.md(2026-10-09)도 미확인을 가점 쪽으로 풀지 않는다고 한다. 같은 실행의 Microsoft(Surface NPU 기기 안 AI, EV-microsoft-105)·Alibaba(Himax 기기 안 시각 추론, EV-alibaba-105)·Apple·Tesla·NVIDIA 는 기기 안 AI 근거를 대고 '예'로 적었다. Alphabet 의 같은 처리는 시범 리뷰가 다음 실행 과제 11 로 적었고 상한 8 에 걸려 점수가 같았지만, Amazon·Meta 에서는 점수가 움직인다.
  점수 영향: Amazon 수직계열화 8 → 7, ④ 16.62 → 15.62(17 → 16), 조정총점 32 → 31(TSMC 와 공동 3위). Meta 수직계열화 5.5 → 4.5, ④ 17.31 → 16.31(17 → 16), 조정총점 41 → 40(순위 같음).
  고칠 방향: 두 기기의 기기 안 AI 근거(예: Echo·Fire TV 의 자체 신경망 처리, Meta 안경의 기기 안 처리)를 확정 근거로 찾아 대거나, 못 찾으면 AI 사슬을 '아니오'로 적는다. Alphabet Pixel 칸도 같은 잣대로 고친다(점수 같음).

- **F-2. alibaba.F1.cloud — 가격 인상 전 분기를 '인상·유지 뒤 2개 분기'로 셌다(① B, Q02·Q03).**
  무엇이 틀렸나: B 3 의 근거는 2026-04-18 목록가 인상(EV-alibaba-090·091·095)과 '2026년 3월 분기·6월 분기 매출 증가'다. 3월 분기는 인상 전이고, 6월 분기도 공지대로 기존 주문은 다음 갱신 주기까지 옛 값이라 인상 뒤 매출이 한 분기에도 다 실리지 않았다. 판단은 "인상 전까지는 값을 유지했다"로 3월 분기를 '유지 뒤'로 읽었다. 같은 실행에서 Amazon AWS 는 2026-10-02 AI 칩 임대료 인상 뒤 분기가 없어 B 미확인이고, 시범 Apple Mac·웨어러블은 분기 끝 이틀 전 인상이라 "인상 뒤 매출을 가르지 못한다"로 미확인이다. TSMC·iPhone 은 인상 뒤 두 분기를 모두 썼다. Alibaba 만 인상 전 분기를 넣었다.
  점수 영향: B 3 → 미확인 1.6, 클라우드 사업 7.4 → 6.0. Alibaba ① 8.65 → 8.45(9 → 8), 조정총점 9 → 8. Palantir 와 공동 8위에서 9위로 내려간다(F-4 와 함께면 Palantir 와 다시 공동 8위).
  고칠 방향: Apple Mac 과 같은 잣대로 미확인(1.6)으로 두고, 인상 뒤 두 분기가 나오면 다시 잰다는 트리거를 단다. '인상 전 유지'를 3 의 근거로 인정하려면 AWS(인상 전 유지)에도 같은 잣대를 대야 하며, 그 경우 Amazon ① 은 9.80 → 10.07 로 정수가 같다.

- **F-3. oracle.F2.outside — 찾지 못한 것을 '없음'(0)으로 적었다(② 패러다임 적응, 2.6, Q03).**
  무엇이 틀렸나: 하드웨어·서비스 층 밖 사업의 패러다임 적응을 "10-Q 주석·경영진 논의의 두 사업 설명과 뉴스 후보 제목에서 찾지 못했다"는 이유로 0 으로 적었다. 2.6 은 "우리가 못 찾았다"를 확인되지 않음(만점의 40%)으로 두고 공시되지 않았음이 확인된 경우와 가른다. 같은 실행의 Amazon 층 밖 사업(실물 매장·기타)은 같은 상태를 미확인 2 로, 시범 Alphabet 데이터 플랫폼·기기와 Apple 두 층도 미확인 2 로 적었다. Tesla 층 밖(규제 크레딧)의 0 은 사업이 정부 규제가 만든 거래라 새 판 제품이 성립하지 않는다는 판정이라 경우가 다르다.
  점수 영향: 층 밖 ② 0 → (2 + 0) × 2 = 4, 무게 12.5%. Oracle ② 5.35 → 5.85(5 → 6), 조정총점 +1(F-4 와 함께면 Oracle 은 5 그대로).
  고칠 방향: 패러다임 적응을 미확인으로 적는다. 0 으로 두려면 두 사업에 새 판용 제품이 없다는 발행사 문언을 대야 한다.

- **F-4. oracle.F3.data_platform·oracle.F3.application·palantir.F3.data_platform — AI 무관 매출 줄의 성장을 가속도 단계 c 로 썼다(③ 가속도, 2.4, Q02·Q03).**
  무엇이 틀렸나: 2.4 는 "③ 의 가속도는 AI 귀속 지표로만 잰다. 비AI 매출의 성장은 ③ 가속도가 아니다"라고 하고, 가속도 절은 "플랫폼 전체 성장률이 아니라 AI 에 귀속되는 부분만 본다. 섞으면 레거시 모멘텀 때문에 AI 가 정체해도 가속으로 보인다"고 한다. Oracle 은 소프트웨어 라이선스·지원 매출(2.72)과 클라우드 애플리케이션 매출(2.89)을, Palantir 는 회사 전체 매출(3)을 단계 c 대리 지표로 썼는데, 같은 실행의 ④ 판단이 세 줄을 모두 AI 무관 매출로 적었고 세 판단 스스로 AI 기능에 귀속되는 매출·사용량이 공시되지 않는다(미확인)고 적는다. 단계 c 의 예인 클라우드 전체 매출은 ④ 가 AI 수요로 센 줄이다. 같은 실행의 다른 회사는 AI 기능이 섞인 비AI 줄을 대리 지표로 쓰지 않고 자료 없음(2.4)으로 두었다: Tesla 전력("AI 데이터센터와 무관한 수요가 대부분이라 AI 귀속 지표가 아니다(규칙 2.4)"), Amazon·Meta·Microsoft·Alibaba 사용자 플랫폼, Microsoft·Amazon·Oracle 층 밖, Apple·Meta 기기.
  점수 영향: Oracle 데이터 플랫폼 ③ 2.72 → 2.4, 응용 ③ 6.89 → 6.4, Oracle ③ 3.71 → 3.49(4 → 3), 조정총점 −1. Palantir ③ 3 → 2.4(3 → 2), 조정총점 9 → 8(Alibaba 와 순위가 바뀐다).
  고칠 방향: 세 층의 가속도를 자료 없음(2.4)으로 둔다. AIP·AI 에이전트처럼 줄 안에 AI 제품이 섞인 비AI 줄을 대리 지표로 인정하려면 규칙에 그 기준을 적고 Amazon·Meta·Alibaba 사용자 플랫폼에도 같은 잣대를 댄다.

- **F-5. nvidia.F2.chip_design — 설계 단계 발표를 표준 지원으로 셌다(② 표준 선점, 2.1, Q09·Q03).**
  무엇이 틀렸나: NVLink Fusion 의 '한두 곳 지원'(1) 근거는 AWS 가 Trainium4 를 이 규격에 묶도록 "설계 중"이라는 것(EV-nvidia-128 "teased its Trainium4 accelerators, which will be among the first", EV-nvidia-036 "AWS, which is designing Trainium4 to integrate")과 d-Matrix 의 채택 발표(EV-nvidia-037 "plans to integrate")다. 2.1 은 계획·발표를 0점으로 둔다. 같은 판단 묶음의 nvidia.F5 는 같은 AWS 사실을 "설계 단계"라 경쟁사 편입이 아니라고 읽어, 한 사실이 ② 에서는 지금의 지원, ⑤ 에서는 계획으로 갈렸다. 시범 Anthropic MCP 는 ChatGPT·Gemini·Copilot 이 실제로 지원하는 제품이라 경우가 다르고, OpenAI API 규격도 Google·DeepSeek·Anthropic 이 지금 지원한다.
  점수 영향: 표준 선점 1 → 0, NVIDIA ② 12 → 11, 조정총점 20 → 19(순위 같음).
  고칠 방향: 출하된 제품의 지원이 확인될 때까지 표준 선점을 0 으로 두고 트리거로 지켜본다.

- 발견을 모두 반영한 어림: Alphabet 43 · Meta 40 · Amazon 31 · TSMC 31 · Microsoft 24 · Apple 24 · NVIDIA 19 · Palantir 8 · Alibaba 8 · Oracle 5 · SpaceX + xAI −1 · Tesla −1 · OpenAI −4 · Anthropic −13. Amazon·TSMC 공동 3위, Palantir·Alibaba 공동 8위로 순위가 바뀐다.

## 다음 실행 과제 (점수·순위에 닿지 않는 것)

1. microsoft.F1.linkedin 의 참여자 효과 6 은 회원 13억 명과 5년 연속 회원 증가에 기댄다. 규칙 ① 은 고객 수와 성장률만으로 6 을 주지 않는다. 같은 칸 6 의 Meta·Windows·Amazon 제3자 판매는 일간 활성·광고 노출·활성 기기·판매 몫 같은 이용 수치를 댔다. 4 로 두면 Microsoft ① 8.93 → 8.81 로 정수가 같다.
2. Tesla 의 B 가 평균 판매가 변화를 가격 행동으로 읽는다. 에너지는 평균 판매가 하락(정가 인하인지 구성 변화인지 10-Q 가 가르지 않음)을 '가격 인하' 0 으로, 서비스·기타는 중고차 평균 판매가 상승을 3 으로 셌다. NVIDIA 는 제품 구성에 따른 이익률 변화를 B 미확인으로, 시범 TSMC 는 공정 구성에 따른 ASP 상승이 아니라 인상 보도로 B 를 정했다. 두 줄을 미확인으로 두면 Tesla ① 7.21 → 7.20 이다.
3. oracle.F1.software 의 C 1 근거는 Amazon 이 일부 제3자 응용을 옮기지 못했다는 사례다. 옮기기 어려운 것은 A 의 전환비용이 센 속성이고 격차를 잰 측정이 아니다(시범 F-5 와 같은 원칙). 미확인 0.8 이면 Oracle ① 7.06 → 6.99 다.
4. 데이터 플랫폼 칸의 AI 사슬 근거가 회사마다 깊이가 다르다. Microsoft(Fabric 으로 에이전트에 데이터를 대는 고객 1만 7천 곳)·Palantir(부트캠프에서 실제 고객 데이터)는 쓰임을 보였고, Alphabet·Amazon·Oracle·Alibaba 는 기능 설명이다. Oracle ④ 는 멀티클라우드 AI Database 404% 를 근거로 들지만 같은 회사 ② 는 그 값을 AI 기능 채택 지표가 아니라고 뺐다. 규칙의 "실제로 쓰일 때"에 필요한 근거를 정한다(엄격히 대면 Amazon·Oracle·Alibaba ④ 가 1씩 내려갈 수 있다).
5. '자체 사용'(자기가 설계한 것을 대규모로 자기만 쓴다) 칸에 남에게 공짜로 주는 것이 들어간다. Meta 개발 플랫폼(재단에 넘긴 PyTorch), NVIDIA 모델(공개한 Nemotron), 시범 Apple 개발 플랫폼(Foundation Models 프레임워크). Meta 는 Apple 잣대를 따랐다고 적지만 Apple 의 프레임워크는 Apple 기기 안에서만 쓰여 경우가 다르다. Meta·NVIDIA 는 정수가 같고, 엄격히 대면 Apple ④ 14.82 → 14.32 다.
6. '무료 AI 를 주고 다른 데서 거둠' 같은 방식 회사 목록이 회사마다 다르다. Meta 는 Alphabet·OpenAI·SpaceX 셋, Amazon·Microsoft·Alibaba 는 넷을 세며, Amazon 과 Microsoft 는 어느 회사 목록에도 없다(두 회사 스스로는 그 방식으로 매겨졌다). 모두 두 곳 이상이라 점수는 같다.
7. 규칙 8절이 기기 층의 AI 귀속 지표를 정하지 않았는데 Tesla 기기 ③ 은 활성 FSD 구독을 단계 d 로 썼다(Apple·Meta 기기는 자료 없음). 단계표와는 맞지만 규칙으로 정해 둔다(Tesla ③ 은 4.04 ↔ 2.4 에 따라 4 ↔ 2).
8. openai.F2.model 의 성능 도약 '2위권'(4)은 종합 지수 공동 3위·GDPval 6위권·코딩 4위에 기대고, 근거로 2026-09-09~22 의 지난 공동 1위를 든다. 사다리에 3위 이하 칸이 없어 같은 처지의 Alphabet 은 '미확인'(4)으로 적었다. 점수는 같지만 칸 이름과 지난 순위 인용(2.11 '과거 실적')을 정리하고, 동률·3위 이하 처리를 규칙에 적는다(시범 과제 13 과 같은 빈칸).
9. ⑤ 구조형 기준 문장이 갈린다. Amazon·Microsoft 는 "고객이 컴퓨트를 만들어 팔지 않는다"(남에게 파는지)로, NVIDIA(Maia·MTIA·Jalapeño)·Anthropic(Cursor 자체 모델)은 자기 사용 대체품으로 전선을 세었다. 규칙 ⑧ 은 "고객이 자체 대체재를 만든다는 것"을 ⑤ 로 보낸다. OpenAI·Anthropic 은 자기 소유 컴퓨트가 없어(OpenAI ④ 시스템·클라우드 없음, Stargate 하드웨어는 Oracle·SoftBank 소유) 결과는 같다. 문장을 '자체 대체품 출하(자기 사용 포함)'로 맞춘다.
10. 정부 매출 집중을 재는 축이 다르다. Palantir 는 미국 정부 기관 합계 약 42% 를 지정학 축(−3)에서, 시범 SpaceX 는 미국 연방정부 약 20% 를 고객 축(10~30%)에서 잰다. 칸 값은 어느 축이든 같다.
11. ⑤ 구제 조치의 경계: Microsoft 의 노동부 영주권 노동 인증 정지를 구제 조치(−2)로, Meta 의 러시아 WhatsApp 접근 제한은 구제 조치가 아닌 시장 일부 차단으로 읽었다. 규칙 예시(매각·판매 금지·승인 거부·구제 명령)에 비춰 경계를 적어 둔다(Microsoft ⑤ 는 아니면 11 → 13).
12. meta.F8 공급 축은 운영체제별 매출 몫이 30% 이상인지 미확인인데 −2 로 두었다(감점 완화 쪽). 약정 축 −3 이 칸을 정해 점수는 같다.
13. Amazon 온라인 스토어와 구독(Prime 배송 혜택) 사이의 연결을 묶기 검토에서 다루지 않았다(시범 F-6 의 묶기 원칙).
14. 간접 자료와 덮는 비율을 함께 거는 경우가 갈린다. Amazon 구독·LinkedIn 은 둘을 곱했고, Meta 광고는 표에 없는 Messenger·제3자 앱 광고가 줄에 섞였는데 YouTube·X 선례대로 간접 50% 만 걸었다. 기준을 적는다(Meta ① 14.27 → 14.07 로 정수 같음).
15. 규칙 ① 의 "한쪽만 미확인이면 아는 쪽"이 아는 쪽 0 일 때 A 0 을 만든다(Amazon 실물 매장, Tesla 에너지·서비스·기타). 문언대로라 모든 회사에 같게 닿았지만, 미확인 전환비용을 0 으로 푸는 효과라 규칙 검토 대상으로 적는다.
16. Oracle ⑤ 미 전쟁부 ESI IDIQ 는 Oracle 제품 조달 수단이고 같은 프로그램이 다른 소프트웨어 회사에도 있다. '경쟁사도 함께 받은 계약'인지 적어 둔다(OpenAI 만으로도 1 이라 점수 같음).
17. 근거 세 칸의 작은 정리(아래 「판단 근거 세 칸」).

## 회사를 가로지르는 표 셋

### 1. 사건 교차표

| 사건(상대의 행동) | 판단(회사·항목·읽은 성격·점수 방향) | 갈린 이유 | 판정 |
|---|---|---|---|
| Microsoft 의 자체 모델(MAI) 투입 | Anthropic ⑤ GitHub Copilot 구조형 미확인 전선(내림) · OpenAI ⑤ 전선 아님 · Microsoft ⑤ 미산입 · OpenAI ⑧ 공급자=경쟁자(−3) · Microsoft ⑧ 공급 축 대체 경로(올림) | 관계의 종류(Anthropic 에게 유료 고객, OpenAI 에게 공급자·투자자·IP 라이선스 보유자, Microsoft 는 사는 쪽). 이미 정해진 결정 | 일치 |
| SpaceX 의 Cursor 인수 | Anthropic ⑤·OpenAI ⑤ 구조형 미확인 전선 · Anthropic ⑦·OpenAI ⑦ Cursor 를 조달 의존 고객으로(큼) · SpaceX ⑧ 공급 축 | 두 모델 회사에 같은 성격·같은 등급(매출 몫 미공시) | 일치 |
| Meta 의 자체 모델(Muse)과 사내 Claude 축소 | Anthropic ⑤ 구조형 미확인 전선(이 실행에서 더함) · Meta ⑤·⑧ 사는 쪽 조달 변화 · OpenAI 는 Meta 고객 관계 근거 없음 | 관계의 종류 | 일치 |
| OpenAI 의 Azure $250B 추가 구매 | Microsoft ⑦ 큼(기간 미공시 상한 84%) · Microsoft ⑧ 고객 −3(RPO 몫 1차 발표) · Microsoft ⑤ 지분 동맹·경쟁사 편입 · OpenAI ⑧ 약정 합계에 넣음 | 관계의 종류(공급자에게 매출 의존, 고객에게 약정). 계약 구속력은 같게 읽음 | 일치 |
| OpenAI·Anthropic 의 AWS 확장 약정 | Amazon ⑦ 작음(연환산 2.9%, 장기계약 상한 10%) · Amazon ⑧ 고객 −1 정책값(연환산 1.6%·1.3%) · Amazon ⑤ 지분 동맹·경쟁사 편입 · OpenAI ⑧ 약정 합계 | 관계의 종류. ⑦ 가로축은 Microsoft(33.9%)·Alphabet(9.0%)과 같은 연환산 잣대 | 일치 |
| Anthropic 의 Google TPU·Cloud 약정과 Alphabet 지분 | Alphabet ⑤ 경쟁사 편입 · Alphabet ⑦ 돌아옴 · Amazon·Microsoft ⑤ 가 같은 잣대(대체품 미출하라 못 떠남)를 인용 | 같은 관계를 세 클라우드가 같은 조건으로 읽음 | 일치 |
| OpenAI–Oracle Stargate 협력 | Oracle ⑤ 상업 동맹(공동 구축·운영) · Oracle ⑦ 큼(2차 보도 $300B, 넓히는 쪽) · Oracle ⑧ 고객 축에 안 씀(지급 의무 미기재) · OpenAI ⑤ 조달 · OpenAI ⑧ 약정 합계에 안 넣음 | 관계의 방향. ⑧ 두 회사에 같은 성격(지급 의무 없음) | 일치 |
| xAI(SpaceX)의 OCI 구매와 자체 클라우드 판매 | Oracle ⑤ 구조형 미확인 전선 · 시범 SpaceX ⑤ 의 Google 컴퓨트 구매와 대칭 | 같은 잣대 | 일치 |
| 하이퍼스케일 고객의 자체 칩(TPU·Trainium·Maia·MTIA)과 OpenAI Jalapeño | NVIDIA ⑤ 구조형 미확인 전선 다섯 · Amazon ⑤·Microsoft ⑤ 는 OpenAI 를 못 떠나는 상대로(배치 전·묶인 약정) · NVIDIA ⑤ 는 OpenAI 를 떠날 수 있는 상대로(묶인 약정 없음) | 무엇을 대신하나(칩 대 클라우드)와 묶인 약정 유무, 관계의 종류. 기준 문장 차이는 과제 9 | 일치 |
| 미국의 첨단 칩 수출 통제·중국의 구매 억제 | NVIDIA ⑤ 비용형(파는 시장 차단) · Alibaba ⑧ 지정학 −2(사는 공급 차단) · Microsoft·Oracle ⑧ 지정학 서술 | 관계의 종류(파는 쪽·사는 쪽) | 일치 |
| 미 국방부의 군 계약 배제·목록 등재 | Anthropic ⑤ 비용형·구제 진행(판매 금지) · Alibaba ⑤ 비용형·구제 진행(조달 금지) | 같은 성격 | 일치 |
| Palantir 정부 계약 반대 운동 | Palantir ⑤ 구조형 둘 · Anthropic 국방부 배제는 비용형 | 사업의 정당성을 겨냥(운동) 대 시장 일부 차단(정부 조치). 이미 정해진 결정 | 일치 |
| EU 디지털시장법 클라우드 게이트키퍼 절차 | Amazon ⑤·Microsoft ⑤ 비용형·구제 없음 | 같은 값 | 일치 |
| NYT 등 언론사 저작권 소송(MDL 3143) | Microsoft ⑤·OpenAI ⑤ 비용형·구제 없음 | 같은 값 | 일치 |
| FTC·EU AI Office 조사 | OpenAI ⑤·Anthropic ⑤ 비용형·구제 없음 | 같은 값 | 일치 |
| 영국 장터 판매자 제한 집단소송 | Amazon ⑤·시범 Apple ⑤ 비용형 | 같은 값 | 일치 |
| Amazon 의 Meta Muse 쇼핑 에이전트 차단 | Amazon ⑤ 자기 조치라 적대 아님 · Meta ⑤ 경쟁 행위라 적대 아님 · Amazon ② 규격 아님 | 같은 성격 | 일치 |
| 개방형 모델 무료 공개 | NVIDIA 칩·Alphabet·Microsoft·Alibaba 클라우드 ③ 공짜 전략(수익모델 4, 같은 셋을 서로 셈) · Meta 는 거둘 장치 없어 안 셈 · ④ 칸은 NVIDIA 모델 자체 사용, Meta 모델 판매(Muse API) | 거둘 장치 유무. 이미 정해진 결정. ④ '자체 사용' 정의는 과제 5 | 일치 |
| Alibaba Qwen 의 중국 Apple Intelligence 탑재 | Alibaba ⑤ 상업 동맹 · Apple ⑤ 조달(시범) | 관계의 방향(Alphabet–Apple Gemini 와 같은 잣대) | 일치 |
| Microsoft 의 Qwen 후학습(Decision-1)·Bedrock 의 Qwen 입점 | Alibaba ⑤·⑦·⑧ 대가 없는 사용·떠날 수 있는 입점 · Microsoft ⑤ 동맹도 적대도 아님 | 같은 성격 | 일치 |
| Tesla–SpaceX(xAI) 투자·Megapack 판매 | Tesla ⑤ 관계사라 제외 · Tesla ⑦ 실행된 투자가 고객에 들어가 돌아옴 · Tesla ④ 전력 AI 사슬 예(SpaceX S-1/A) · 시범 SpaceX ⑤ 관계사 거래 | ⑤ 는 관계사 규칙, ⑦ 은 실행된 투자 사실로 판정. 규칙 문언대로 | 일치 |
| AWS Interconnect 채택 | Amazon ② 표준에 세지 않음 · Microsoft ② 언급 없음 | 이미 정해진 결정 | 일치 |
| AWS 의 NVLink Fusion 채택 발표 | NVIDIA ② 표준 지원으로 셈 · NVIDIA ⑤ 설계 단계라 경쟁사 편입 아님 | 같은 회사 안에서 같은 사실을 지금(②)과 계획(⑤)으로 갈라 읽음 | **F-5** |

자료의 유무 차이로 같은 사건이 회사마다 다른 성격으로 읽힌 곳은 찾지 못했다.

### 2. 미확인 방향표

| 판단 | 미확인 | 해소 방향 | 판정 |
|---|---|---|---|
| amazon.F4 · meta.F4 | 기기 안에서 AI 가 도는지 | AI 사슬 예 — 올림 | **F-1** |
| alibaba.F1.cloud | 인상 뒤 2개 분기 매출(인상 뒤 분기가 하나뿐) | B 3 — 올림 | **F-2**(AWS·Apple Mac 은 미확인) |
| oracle.F2.outside | 새 판 제품 유무(찾지 못함) | 0 — 내림 | **F-3**(Amazon 층 밖은 미확인 2) |
| oracle.F3 데이터·응용 · palantir.F3 | AI 귀속 지표 | AI 무관 줄 성장으로 단계 c — 올림 | **F-4** |
| nvidia.F2 | 표준 지원 대부분이 설계 단계 | 지원 1 — 올림 | **F-5** |
| tesla.F5 | 캘리포니아 DMV 명령의 구제 진행 | 40% 규칙(−1.2) | 맞음(2.6) |
| nvidia.F5 · oracle.F5 · openai.F5 · anthropic.F5 | 경쟁사(소유) 고객이 주요 고객인지 | 구조형 미확인 40% 규칙 | 맞음(2.6, 2026-10-19) |
| nvidia.F5 · anthropic.F5 | 최대 파트너 긴장(구조형 둘 이상) | −12 와 −10 사이 40% | 맞음 |
| amazon.F5 · meta.F5 · tesla.F5 · alibaba.F5 · oracle.F5 · openai.F5 | 최대 파트너 긴장(구조형 둘 미만) | 점수 영향 없음 | 맞음 |
| microsoft.F7 | Azure $250B 의 기간 | 한 해 상한(큼) — 내림 | 맞음 |
| microsoft.F8 | OpenAI RPO 몫의 기간 | 전체 평균 기간(−3) — 내림 | 맞음 |
| nvidia.F7 | ACIE 안 조달 의존 몫 | 상한 41.9%(큼) — 내림 | 맞음(2.1) |
| openai.F7 | Cursor 매출 몫 | 큼 — 내림 | 맞음(Anthropic ⑦ 과 같음) |
| amazon.F7 · alibaba.F7 | 조달 의존 고객 몫 | 공시 상한(10%·15.4%)으로 작음 | 맞음(Alphabet 20.1% 와 같은 잣대) |
| amazon.F8 · oracle.F8 · tesla.F8 · alibaba.F8 | 계약 기준 최대 고객 | 비공개 정책값 −1 | 맞음 |
| openai.F8 | 최대 고객(비상장, 제출본 없음) | 탐색 미완 정책값 −1 | 맞음(Anthropic 과 같음) |
| amazon.F8 · meta.F8 | 중국 판매자·광고주 몫 | −1 유지(10% 이상 공시되면 −2) | 맞음(두 회사 같은 잣대) |
| meta.F8 | 운영체제별 매출 30% 이상 여부 | −2 — 감점 완화 | 점수 무관(과제 12) |
| openai.F8 | Cerebras 금액 | 합계에서 뺌(배수를 키우는 쪽의 미확인) | 구간 같음 |
| nvidia.F4 | 2027 회계연도 Edge 구성 | AI 무관(옛 구분 게임 64~74%), 40% 로 둬도 정수 같음 | 맞음 |
| meta.F4 | 기타 매출 안 AI 서비스 금액 | AI 무관(주 구성 기준), 다각화 상한이라 영향 없음 | 맞음 |
| amazon.F1.physical_stores · tesla.F1.energy · tesla.F1.services_other | 전환비용(참여자 효과 0) | A 0 — 내림 | 규칙 문언대로(과제 15) |
| tesla.F1.energy | 평균 판매가 하락 원인 | B 0 — 내림 | 점수 무관(과제 2) |
| oracle.F1.software | 대체재와의 격차 | 사례로 C 1 — 올림 | 점수 무관(과제 3) |
| amazon.F2.user_platform · microsoft.F2.user_platform | '두 배 가까이'·'3배 가까이' | 4·5(하한을 문면대로) | 맞음(같은 읽기) |
| alibaba.F2.user_platform | 누적값의 1년 배수 | 4 | 맞음 |
| oracle.F2 데이터·응용 · palantir.F2 · tesla.F2.power · amazon.F2.outside | 채택 지표 | 미확인 2 | 맞음 |
| 9개사 ③ 사용자 플랫폼·기기 | 가속도 두 기간 값 | 자료 없음 2.4 | 맞음 |

### 3. 결정적 사실의 근거 등급표

| 입력 | 회사별 근거 | 판정 |
|---|---|---|
| ⑤ 구조형의 '주요 고객' | NVIDIA(고객 이름 미공시, 2차 비중 미사용)·Oracle(xAI 몫 미공시)·OpenAI(Cursor 몫 미공시)·Anthropic(2차·유출 미사용)·시범 SpaceX(Google 2차 미사용) 모두 미확인으로 40% 규칙 | 같은 등급 요구, 유출·2차 수치 미사용 |
| ⑧ 고객 축 집중 | Microsoft OpenAI RPO 몫(회사 1차)·NVIDIA 10% 고객(10-K)·SpaceX(S-1/A)·TSMC(20-F) 확인 · Meta·Palantir 부재 공시 · Alphabet·Oracle 2차 미사용(비공개) · Amazon·Tesla·Alibaba 문구 없음(비공개) · OpenAI·Anthropic 탐색 미완 | 일치 |
| ⑦ 조달 의존 몫 | 좁히는 쪽 공시·1차(Amazon 10-Q 상한·Alphabet 매출 상한·Alibaba 부문 매출) · 넓히는 쪽 2차 허용(Oracle $300B) · Microsoft 1차 RPO 몫 | 일치 |
| ⑧ 공급 −4(단일 파운드리) | Apple(TSMC, 2차 + 10-K 단일 공급원) · Tesla(Samsung AI4, heise 2차 + 10-K 단일 공급원) · NVIDIA(10-K TSMC·삼성, TSMC 의존 2차) | 일치(이미 정해진 결정) |
| ③ 수익모델 6(회수 매출 확인) | Alphabet(AI 기능이 검색 질의를 이끈다는 회사 발표) · Amazon(Rufus 추가 판매 연 $120억, Prime 가입률 회사 발표) · OpenAI(광고 연환산 $10억 회사 발표) · Microsoft·Meta·Alibaba·SpaceX 는 회사 귀속 발표가 없어 4 | 일치 |
| ② 패러다임 적응 배수 | AWS AI 사업 런레이트·Microsoft Foundry·Alibaba Model Studio·Meta·Microsoft Copilot·Tesla FSD 구독·OpenAI Codex(회사 1차) · Oracle OCI·NVIDIA 데이터센터(10-Q) · Alphabet Google Cloud(10-Q) | 일치 |
| ② 성능 도약 | 모델: Artificial Analysis(독립) · 칩: MLPerf 를 전한 2차 보도와 벤더 격차 수치(NVIDIA, 원표 미대조) · 파운드리(시범): 공시 + 독립 분석(2차 전달) | 일치(독립 측정의 2차 전달은 시범과 같은 등급) |
| ② 표준 선점 | Anthropic MCP·OpenAI API 규격은 지원 제품 출하 · NVIDIA NVLink Fusion 은 설계 단계 발표 | **F-5** |
| ① A 6(수치로 확인) | Meta(10-Q 일간 활성·노출)·Amazon 제3자(회사 판매 몫)·Alibaba(QuestMobile·회사)·Palantir(10-Q 기존 고객 매출, 2차 NRR 보조)·Windows(회사 활성 기기) · LinkedIn(회원 수만) | 과제 1 |
| ① B 가격 | Amazon 수수료 인상·Microsoft 365 인상(회사)·Alibaba 목록가(회사 공지)·Oracle 지원 요율(재판매사 2차, 2024) · Meta 광고당 가격(10-Q) | 등급은 일치, 시점은 **F-2** |
| ⑤ 상업 동맹의 네 질문 | Oracle–OpenAI·NVIDIA–Mistral·NAVER·Palantir–미국 정부(회사 1차) · Alibaba–Apple(회사 1차 + 2차) · Meta–EssilorLuxottica(공동 출시 1차, 연장 계약 2차) | 일치(가점 근거라 1차 근거 보강이 낫다) |
| ④ 매출 줄 | 상장사 공시 · OpenAI·Anthropic 투자자 수치 2차(같은 등급) | 일치 |

## 직접 겨루는 쌍

### 모델 — OpenAI · Anthropic · xAI(SpaceX)

| 항목 | OpenAI · Anthropic · SpaceX | 차이의 이유 |
|---|---|---|
| ① | 6 · 4 · 7 | OpenAI·Anthropic 은 A 2·B 0·C 0 이 같고, 같은 ai_models_api(25% 반영)에서 OpenAI 3위·+2.2%p 대 Anthropic 상위 밖·점유율 하락. SpaceX 는 사업 구성이 다르다(Starlink 73%) |
| ② | 12 · 15 · 10 | 성능 도약 2위권 4 대 두 축 1위 6(과제 8). 표준은 회사가 쥔 API 규격 셋 지원 3 대 중립 기구 MCP 4. SpaceX 는 모델 층 무게 0, 클라우드·층 밖 적응 5 |
| ③ | 8 · 0 · 3 | OpenAI 는 광고가 받치는 무료 요금제로 회수 매출 확인(6), Anthropic 은 같은 방식(0)에 가속도 감속(0). SpaceX 는 클라우드 같은 방식·층 밖 자료 없음 |
| ④ | 4 · 3 · 14 | OpenAI 사용자 플랫폼 판매(광고) 칸 하나 더. SpaceX 는 비AI 다각화 8 |
| ⑤ | 8 · 4 · 5 | OpenAI 지분 동맹 하나(SB OAI Japan) + 구조형 미확인 하나(Cursor), Anthropic 동맹 없음 + 구조형 미확인 셋(Cursor·Copilot·Meta)과 구제 진행(국방부). 관계의 종류로 Microsoft 는 OpenAI 전선 아님 |
| ⑦ · ⑧ · ⑨ | −8·−8·−8 / −12·−12·−12 / −8·−8·−12 | ⑦ 세 회사 모두 큼·안 돌아옴. ⑧ OpenAI·Anthropic 약정·공급 −3, SpaceX 고객 −3. ⑨ 비상장 경로 대 상장 경로 |

### 클라우드 — Microsoft · Amazon · Alphabet · Oracle · Alibaba (+SpaceX)

| 항목 | Azure · AWS · Google Cloud · OCI · Alibaba · xAI | 차이의 이유 |
|---|---|---|
| ① 클라우드 사업 | 6.64 · 6.7 · 7.2 · 5.2 · 7.4 · 6.0 | A 2·C 0 모두 같음. B 는 Alibaba 만 3(**F-2**). D: 2위(78.8% 반영) · 1위이나 2배 미만(50%) · 3위(50%) · 상위 밖(100%, 줄이 순수 OCI라 0) · 상위 밖(50%) · 상위 밖(50%). E: 0%p · −2%p · +2%p · 미확인 · 미확인 · 미확인 |
| ② 클라우드 | 10 · 10 · 8 · 10 · 10 · 10 | 새 판 제품만의 1년 배수가 있으면 그것(Foundry >2배·AI 사업 런레이트 세 자릿수·Model Studio 고객 8배), 없으면 줄 전체(Google 1.82배 → 4, OCI 2.21배·xAI 7.05배 → 5). 이미 정해진 결정 |
| ③ 클라우드 | 7 · 3 · 7 · 3 · 7 · 3 | 개방형 모델 무료 공개 + 거둘 장치(Phi·Gemma·Qwen)면 공짜 전략 4, 없으면 같은 방식 0. 가속도는 모두 단계 c 최고 3 |
| ⑤ | 11 · 11 · 12 · 9 · 10 | Alphabet 은 상업 동맹(Apple) 하나 더. Oracle 은 지분 1곳 + 구조형 미확인(xAI). Alibaba 는 지분 2곳 + 상업 1 |
| ⑦ | −12 · −4 · −4 · −12 · −4 | 조달 의존 고객 약정의 연환산 몫: Microsoft 33.9%(1차)·상한 84% / Amazon 2.9%(상한 10%) / Alphabet 9.0%(상한 20.1%) / Oracle 83.6%(2차, 넓히는 쪽) / Alibaba 확인 고객 없음(상한 15.4%) |
| ⑧ | −12 · −4 · −8 · −12 · −8 | 고객 −3(OpenAI RPO) / 모두 −1 / 약정 2.02배 / 약정 4.49배 / 지정학 VIE 11.7~15.3% |

### 칩·파운드리 — NVIDIA · TSMC

| 항목 | NVIDIA · TSMC | 차이의 이유 |
|---|---|---|
| ① 주력 사업 | 데이터센터 12.0 · HPC 14.0 | A 4(CUDA 참여자·남는다는 근거) 대 2(설계 기간만 묶임). B 미확인 대 3(첨단 공정 인상 보도 뒤 두 분기). D·E 는 반도체 순위 58% 반영(1위, 2위의 1.73배) 대 파운드리 1위 50% 초과 100% 반영 |
| ② | 12 · 12 | 성능 도약 1위 3개월 미만 6 대 3개월 이상 8. 적응 데이터센터 2.17배 5 대 HPC 1.45배 4. 표준 1 대 0(NVIDIA 1 은 **F-5**) |
| ③ | 10 · 3 | 개방형 모델 무료 공개 공짜 전략 4(결정) + 가속도 단계 b 6 대 같은 방식 + 단계 c |
| ④ | 10 · 9 | NVIDIA 칸 다섯 판매 + 모델 자체 사용(5.5), 다각화 0.83 · TSMC 칸 하나, 다각화 3.88 |
| ⑤ | 7 · 12 | NVIDIA 지분 둘·상업 둘이나 고객 자체 칩 구조형 미확인 다섯(−9.12) · TSMC 상업 EDA 셋, 비용형 관세 하나 |
| ⑦ | −12 · 0 | ACIE 상한을 좁히지 못해 큼 + 보증·되사기로 돌아옴 · TSMC 작음·안 돌아옴 |
| ⑧ | −16 · −16 | NVIDIA 공급(TSMC)·지정학 −4 · TSMC 지정학 −4. 같은 관계를 NVIDIA 공급 −4, TSMC 고객 −2 로 읽음(대체 가능성의 비대칭) |

### 광고·소셜 — Meta · Alphabet · SpaceX(X)

| 항목 | Meta · Alphabet · SpaceX | 차이의 이유 |
|---|---|---|
| ① 광고 사업 | 광고 14.4 · 검색 14.84·YouTube 11·Network 6 · X 광고 9.21 | A 6(일간 활성·노출) 대 검색 6·YouTube 4·Network 2(이탈) 대 X 4(전환비용 0). B 4(10-Q 가 구성 요인을 따로 적음) 대 검색 3(클릭당 비용을 구성·환율로 설명) 대 미확인. E: 소셜 −3.25%p 대 검색 방향 |
| ② 사용자 플랫폼 | 10 · 10 · 8 | 1년 2배 이상 지표(미디어 생성 일간 3배·AI Mode 10배) 대 1년 배수 없음 |
| ③ 사용자 플랫폼 | 6.4 · 9.93 · 6.4 | 회수 매출 회사 귀속 발표 유무(4 대 6). 가속도 자료 없음 대 Gemini 앱 d 단계 |
| ④ | 17 · 20 · 14 | 수직계열화 5.5(**F-1** 반영 시 4.5) 대 8 대 4 |
| ⑤ | 10 · 12 · 5 | 지분 둘 + 상업 하나 대 편입 + 지분 + 상업, SpaceX 구조형 미확인(Google) |
| ⑧ | −12 · −8 · −12 | 약정 3.05배 대 2.02배 대 고객 −3 |

### 업무 소프트웨어·데이터 플랫폼 — Microsoft · Oracle · Palantir

| 항목 | Microsoft · Oracle · Palantir | 차이의 이유 |
|---|---|---|
| ① | M365 상업 11·Dynamics 7.6 · 클라우드 앱 7.6·소프트웨어 8.2 · 정부·상업 각 11.6 | A: 정가 인상 뒤 좌석 증가 4·계약 기간 2 / 계약 2·지원 갱신 진술 4 / 기존 고객 매출 증가 공시 6. B: 2022 인상 유지 뒤 3 / 지원 요율 인상 뒤 감소 0 / 미확인 |
| ② 응용 | 10 · 4 | Copilot 좌석 순증 3.5배 대 채택 지표 없음 |
| ② 데이터 플랫폼 | — · 4 · 4 | 둘 다 채택 지표 없음 |
| ③ 응용 | 10 · 6.89 | 같은 공짜 전략·모방 0. 가속도: 유료 Copilot 좌석 단계 b 6 대 AI 무관 클라우드 앱 매출 단계 c(**F-4**) |
| ③ 데이터 플랫폼 | — · 2.72 · 3 | 둘 다 AI 무관 매출 줄을 단계 c 로 씀(**F-4**) |
| ④ | 18 · 15 · 15 | 수직계열화 8 대 4.5 대 3, 다각화 6.10 대 6.92 대 8 |
| ⑤ | 11 · 9 · 3 | 편입 + 지분 대 지분 + 상업·구조형 미확인 대 상업 하나·구조형 둘(결정) |

### 기기 층 — Apple · Tesla · Meta · Alibaba

| 항목 | Apple · Tesla · Meta · Alibaba | 차이의 이유 |
|---|---|---|
| ① 기기 사업 | iPhone 묶음 15.8(iPad 16)·Mac 9.3·웨어러블 11 · 차량 7.8 · Reality Labs 8 · (매출 줄 없음) | A 6·4 대 4(충성도 수상, 미국) 대 미확인. B 3(iPhone 인상 뒤) 대 0(중국 할인·호주 인하) 대 미확인. D·E 는 스마트폰·태블릿·PC·웨어러블 대 BEV 2위 대 미확인(결정) |
| ② 기기 | 4 · 8 · 10 · 무게 0 | 채택 지표 없음 대 FSD 구독 1.56배 대 안경 판매 3배 |
| ③ 기기 | 2.4 · 4.04 · 2.4 · 무게 0 | 같은 방식·모방 0 은 같음. 가속도는 FSD 구독 d 단계(과제 7) 대 자료 없음 |
| ④ 기기 칸 AI 사슬 | 예(기기 안 처리) · 예(차량 칩) · 예(미확인, **F-1**) · 예(Himax 기기 안 추론) | Meta 만 근거 없이 예 |

## v3.0 판정 재료

- **④ 보유표.** 14개사 칸과 AI 사슬 표시(예·no 는 판정 재료값)다.

| 회사 | 전력 | 반도체 제조 | 칩 설계 | 시스템 | 클라우드 | 개발 | 데이터 | 모델 | 응용 | 사용자 플랫폼 | 기기 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Alphabet | 준비 | 없음 | 판매 | 판매 | 판매 | 판매 | 판매·예 | 판매 | 판매 | 판매·예 | 판매·예(미확인) |
| Apple | 없음 | 없음 | 자체 | 자체 | 없음 | 자체 | 없음 | 자체 | 자체 | 판매·아니오 | 판매·예 |
| TSMC | 없음 | 판매 | 없음 | 없음 | 없음 | 없음 | 없음 | 없음 | 없음 | 없음 | 없음 |
| SpaceX | 없음 | 없음 | 없음 | 없음 | 판매 | 없음 | 없음 | 판매 | 판매 | 판매·예 | 없음 |
| Anthropic | 없음 | 없음 | 없음 | 없음 | 없음 | 판매 | 없음 | 판매 | 판매 | 없음 | 없음 |
| Amazon | 없음 | 없음 | 자체 | 자체 | 판매 | 판매 | 판매·예 | 판매 | 판매 | 판매·예 | 판매·예(미확인, **F-1**) |
| Microsoft | 없음 | 없음 | 자체 | 자체 | 판매 | 판매 | 판매·예 | 판매 | 판매 | 판매·예 | 판매·예 |
| Meta | 없음 | 없음 | 자체 | 자체 | 없음 | 자체(과제 5) | 없음 | 판매 | 판매 | 판매·예 | 판매·예(미확인, **F-1**) |
| NVIDIA | 없음 | 없음 | 판매 | 판매 | 없음 | 판매 | 없음 | 자체(과제 5) | 판매 | 없음 | 판매·예 |
| Oracle | 없음 | 없음 | 없음 | 자체 | 판매 | 판매 | 판매·예 | 없음 | 판매 | 없음 | 없음 |
| Tesla | 판매·예 | 준비 | 자체 | 없음 | 없음 | 없음 | 없음 | 자체 | 판매 | 없음 | 판매·예 |
| Palantir | 없음 | 없음 | 없음 | 없음 | 없음 | 판매 | 판매·예 | 없음 | 판매 | 없음 | 없음 |
| Alibaba | 없음 | 없음 | 자체 | 자체 | 판매 | 판매 | 판매·예 | 판매 | 판매 | 판매·예 | 판매·예 |
| OpenAI | 없음 | 없음 | 준비 | 없음 | 없음 | 판매 | 없음 | 판매 | 판매 | 판매·예 | 준비 |

  자기 클라우드로만 빌려주는 칩(Trainium·Maia·Zhenwu)은 모두 자체 사용, 준비 중 칸(Tesla 반도체 공장·OpenAI 칩·기기·Alphabet 전력)은 모두 트리거를 달았다. 매출 줄 층 배정은 공시 줄을 가장 많이 속한 층에 통째로 붙이고 구성 미공시면 사업 설명으로 고르고 미확인을 적는 방식으로 14개사가 같다(Amazon 온라인 스토어의 기기, Oracle 라이선스·지원, Palantir 두 줄, Alibaba 그 밖 사업, OpenAI 회사 한 줄). AI 무관 판정은 AIP 문언(결정)과 40% 규칙(Microsoft Other)대로 쓰였다. 칩·클라우드가 없는 회사의 ⑧ 공급 축은 모두 0 이 아니다. 데이터 플랫폼 AI 사슬 근거 깊이는 과제 4.
- **① 나누기·묶기·AI 수익화·부분 반영.** 9개사 모두 공시 줄 단위로 나누고 고객 유형을 누가 돈을 내나로 적었다. 새 묶음은 Oracle 라이선스·지원 하나이고 묶은 근거(지원이 라이선스의 부속 계약)를 적었다. AI 수익화 '예'는 14개사에 없다(Microsoft 365 상업·소비자는 가격 조건만 서서 부분). 부분 반영은 덮는 비율(AWS·Alibaba 50%, Azure 78.8%, LinkedIn 48.7%, Windows·Bing 50%, NVIDIA 58%)과 간접 자료(소셜·TV 시청·OpenRouter 50%)가 결정과 규칙대로 쓰였고 OCI·Tesla 차량은 100% 다. 상한 밖 목록(Synergy 상위 3)은 D 0·E 미확인으로 같게 적었다. 기준 문제는 과제 14.
- **② 벤치마크 없는 층.** 9개사 층은 모델(OpenAI)·칩(NVIDIA)만 성능 도약을 쓰고 나머지는 (적응 + 표준) × 2 로 매겼다. 모델 순위를 사용자 플랫폼으로 옮긴 판단은 없다(Meta 가 명시). 표준은 OpenAI API 규격(2025-03 최근 지원, 회사 보유 3)·NVLink Fusion(**F-5**)뿐이다.
- **③ 상대의 현존·모방 회사 수·가속도 환산.** 상대가 없다고 적은 층은 Microsoft·Tesla 층 밖뿐이고 둘 다 수익모델·모방 0, 가속도 2.4 다. 모방 회사 수는 같은 방식 두 곳 이상이면 0 으로 모두 같게 셌다(목록 차이는 과제 6). 20% 안 길이 환산은 Microsoft 응용(90일·91일)이 규칙대로 썼다. 단계는 클라우드 c, NVIDIA b, Microsoft 응용 b, Tesla 기기 d 이고 AI 무관 줄을 c 로 쓴 세 층이 **F-4** 다.
- **⑤ 세 부분과 전선 성격.** 한 관계 한 부분(Amazon·Microsoft 의 OpenAI·Anthropic 배정), 받은 투자 제외(OpenAI·Anthropic 의 투자자), 관계사 제외(Tesla–SpaceX, Alibaba–Brooklyn Nets), 경쟁사도 함께 받은 정부 계약 제외(기밀망 협약·CDAO), 현재 보유가 확인되지 않은 지분 제외(Microsoft G42, Amazon Rivian), 끝난 사건 제외(Palantir Mopac, Oracle 합의, OpenAI 영리 전환 소송)가 같게 쓰였다. 관할은 나라와 EU 를 따로 셌다(Microsoft 이탈리아, Meta 여섯).
- **⑦·⑧.** ⑦ 가로축 문장과 잣대(좁히는 사실은 공시·1차, 넓히는 쪽은 2차 허용, 연환산)가 9개사 모두 같고 결과도 시범과 이어진다. ⑧ 은 '지금의 생산이 멈추나'(−4) 대 '증설만 막히나'(−1)가 공급·지정학 축에서 같게 쓰였고, 약정 축은 체결 리스(기간 뒤 Meta 2026-07 리스 포함)와 우발 의무(⑦ 로)를 같게 갈랐다.

## 판단 근거 세 칸

9개사 판단의 올릴·내릴 줄을 전부 읽었다. 점수와 반대 방향 사실이 그 점수를 받치는 칸에 섞인 줄은 아래 하나다. 결론·저울질·미확인은 판정 칸에 있다.

- 방향이 뒤바뀐 줄: microsoft.F8 내릴 근거의 "Maia 를 자사 주력 추론 시스템으로 삼는 다기가와트 배치는 2027년에 시작하는 계획이다" 는 그 사실만 보면 공급 의존을 줄이는 쪽(올림)이다. 계획 단서는 붙어 있다.
- 판단이 쓰지 않는다고 판정 칸에 적은 사실이 단서 없이 올릴 칸에 있다: oracle.F2.data_platform·oracle.F3.data_platform 의 멀티클라우드 AI Database 404%, palantir.F2.data_platform 의 미국 상업 매출·고객 수, openai.F3.model 의 2분기 매출 18% 증가. 같은 줄에 '채택 지표로 쓰지 않는다'·'가속도에 쓰지 않는다' 단서를 붙인다(guide 5.6 '품질이 약한 사실').
- 한 사실이 양쪽으로 읽히는 줄은 Amazon·Microsoft ⑤ 의 Jalapeño(출하 대 배치 전)처럼 둘로 쪼개져 있다.

## 정기 실행 재판단 정책(rules.md 2.9)

9개사의 ①②③④⑤⑦⑧ 판단 120건은 모두 `status: new`, 검토일 2026-10-20 이고 ④⑤⑦⑧ 은 모두 `reconfirmed` 에 이 실행의 날짜·근거를 남겼다. `carried` 는 ⑥(Anthropic·OpenAI)과 ⑨(Apple·NVIDIA·Palantir·Tesla·OpenAI) 일곱 건으로 2.9 의 대상 밖이다. 시범 5개사의 판단은 바뀐 셋을 빼고 승인된 pilot10 과 같다. 이 실행은 기업 추가 실행이지만 규칙이 바뀌어 전체 리뷰를 했고 승계 판단 예외는 쓰지 않았다.

## 체크리스트

| ID | 결과 | 근거 |
|---|---|---|
| Q01 | pass | 같은 속성을 두 번 센 곳 없음. 수출 통제는 NVIDIA ⑤·Alibaba ⑧ 에 한 번씩(관계의 종류), Palantir 미국 정부 집중은 ⑧ 지정학에서만, 활동가 운동은 ⑤ 에서만, 고객 자체 칩은 ⑤ 에서만(NVIDIA ① C 는 MLPerf 격차로 정함), 지분 평가이익은 ⑥ 에만. Oracle C 가 A 의 속성을 다시 쓴 점은 점수 무관(과제 3) |
| Q02 | fail | F-1(기기 AI 사슬 근거 없이 예), F-2(인상 전 분기로 B), F-4(AI 무관 줄을 가속도로). 시장 평균 단가·시장 성장률을 ① 에 넣은 곳 없음 |
| Q03 | fail | F-1~F-5. 사건 교차표·근거 등급표에서 자료의 유무로 읽기가 갈린 곳은 없고, 미확인 해소 방향(F-1·F-3)·B 시점(F-2)·가속도 지표(F-4)·계획의 표준 산입(F-5)이 같은 실행의 다른 회사와 달랐다 |
| Q04 | pass | ⑥ 은 비율 파라미터·비상장 P/S 성장 조정으로 계산되고 판단이 시총 크기를 밸류에이션 근거로 쓴 곳 없음 |
| Q05 | pass | 결정 근거는 공시·회사 1차·독립 측정(Synergy·StatCounter·Nielsen·Gartner·Counterpoint·OpenRouter·MLPerf·Artificial Analysis·QuestMobile·S&P Global Mobility)이다. 표기 누락은 사유로 삼지 않는다 |
| Q06 | pass | 토큰 점유율은 부분 반영으로만(결정), 소셜·TV 시청은 간접 자료 50%, 사용량을 매출 점유율로 쓴 곳 없음 |
| Q07 | pass | '모델을 안 만든 것'을 ③ 으로 센 판단 없음(Oracle·Palantir 는 같은 방식) |
| Q08 | pass | 적대는 성격과 관할 수로 정했다. 전선을 상대·사건마다 따로 적은 방식(Palantir 둘, Anthropic 셋, Meta 열둘)이 같고, 띠는 구조형 여부와 관할 조건으로 갈렸다 |
| Q09 | fail | F-5(NVLink Fusion 설계 단계 발표를 표준 지원으로). 그 밖의 계획(Microsoft Maia 2027, Alibaba V900, OpenAI 기기·Jalapeño 배치, Synopsys·Workday 협력, Oracle AI Data Platform, Tesla Terafab·Optimus)은 점수 밖이고 준비 중 칸에 트리거를 달았다 |
| Q10 | pass | ③ 가속도는 모두 두 기간 배수의 비이고 누적 성과(누적 AI 쇼핑 2.5억·누적 Codex)를 가속도로 쓴 곳 없음 |
| Q11 | pass | OpenAI·Anthropic·SpaceX 적자는 ⑨ 에서만 감점 |
| Q12 | pass | 모방 불가능성 8 없이 16 이상 받은 층 없음(최고 Microsoft 응용·NVIDIA 칩 10) |
| Q13 | pass | 공짜 전략은 거둘 장치가 있는 곳만 세었고(결정), 거둘 장치 없는 Meta 오픈웨이트·CUDA 무료 제공은 세지 않았다 |
| Q14 | pass | 문 닫힘 증거로 20 을 받은 층 없음 |
| Q15 | pass | Qwen 파생 모델·오픈웨이트 개발자·광고주·NACS 채택사를 동맹으로 세지 않았다 |
| Q16 | pass | ① 은 공시 줄과 고객 유형으로 사업마다, ②③ 은 매출 줄이 붙은 층마다 매겼고 무게 0 층 판단을 새로 만들지 않았다. 층 배정 기준이 14개사 같다. 묶기 검토 누락은 과제 13 |
| Q17 | pass | 벤치마크 없는 층은 (적응 + 표준) × 2, '표준 없음'만으로 깎은 곳 없음 |
| Q18 | pass | Tesla–SpaceX(같은 경영자), Alibaba–Brooklyn Nets 제외. Ant Group 은 지배 관계가 과거형이라 지분 동맹 |
| Q19 | pass | 받은 투자(OpenAI·Anthropic·xAI 의 투자자 지분, Tesla 의 xAI 투자는 SpaceX 쪽 받은 투자)를 동맹에서 뺐고, 한 관계를 두 부분에 넣은 곳 없음 |
| Q20 | pass | Meta 의 TPU 임차·AMD, Oracle 의 모델 탑재, Palantir 의 모델·Nemotron, Amazon 의 NVIDIA·전력, OpenAI 의 Oracle·CoreWeave·Cerebras, Apple 의 Qwen 은 조달로 제외 |
| Q21 | pass | '상대가 떠날 수 있나'(⑤)와 '내가 떠날 수 있나'(⑧)를 섞은 곳 없음. 같은 계약을 공급자 ⑧ 고객 축·고객 ⑧ 약정 축으로 나눠 읽고 구속력은 같게 읽음(Azure $250B, Oracle 협력) |
| Q22 | pass | Amazon $53.4B·Microsoft $3.2B·Alphabet·NVIDIA 평가이익을 ⑦ 입력에서 뺐다 |
| Q23 | pass | Artificial Analysis 는 같은 하니스, Coding Agent Index 는 참가자 전원 자기 하니스, MLPerf 는 같은 규칙 제출본이고 미리보기 등급은 1위 판정에서 뺐다 |
| Q24 | pass | 끝난 사건(Palantir Mopac, Oracle 개인정보 합의, Musk 영리 전환 소송) 제외, 굳은 규격(Windows·CUDA)은 ① 에서만, 표준은 2년 창 안. OpenAI 성능 도약이 지난 공동 1위를 근거로 든 점은 과제 8 |
| Q25 | pass | 모델 순위를 다른 층으로 옮긴 곳 없음, 공짜 전략은 거두는 층(NVIDIA 칩, 세 클라우드, OpenAI 는 광고가 든 회사 한 줄의 모델 층)에서 셈, 자체 사용 기술은 따로 점수 없음, 무게 0 층 판단 없음 |
