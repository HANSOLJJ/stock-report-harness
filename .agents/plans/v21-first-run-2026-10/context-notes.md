# 결정 메모 — 규칙 v2.1 첫 실행

- (2026-10-12) 사용자 "실행 — 서브에이전트 룰 참고". 3분기 실적 전이므로 이 실행은 다리 첫 단계(recheck 와 같은 사실, 규칙만 v2.1)로 정했다. 기준일·가격·정보 마감을 recheck 와 같게 두어 점수 차이를 규칙 변경 몫으로 읽을 수 있게 한다.
- recheck 의 ④⑧ 판단은 점수(score) 형식이다. v2.1 은 ④ survival·⑧ axes 만 받으므로 init 뒤 그 둘은 판단 대기로 나오고, 판단 세션 제안이 형식을 바꾼다(judgment_edit_kind 가 규칙의 첫 판단 종류를 쓴다).
- 이전 트리거는 정보 마감이 같아 새로 볼 창이 없다. carry 의 finding 에 그 사실을 적고 상태를 유지한다.
- init 이 v2.1 로 이어받을 때 ④⑧ score 형식과 ① AI 수익화 '예'(재료 없음) 판단이 v2.1 검증에 걸려 load_context 부터 막혔다. init 이 새 규칙에 걸리는
  새 판단만 carried 로 넘기게 고쳤다(커밋 62eb459·e988202, 35건: ④⑧ 28 + ① 7).
- 재판단 검사는 '검토일이 이전 실행 기준일보다 뒤' 를 요구해 같은 기준일 실행이 통과할 수 없었다. 이 실행에서 수정 이력이 늘어난 판단은 다시 매긴 것으로
  보게 넓혔다(02a5538). 그래서 ②③⑤⑦ 도 입력이 같으면 reconfirm 제안을 반영해야 한다(제안 반영이 수정 이력 한 줄을 더한다).
- 규칙 파일 문구를 고쳐 실행을 네 번 다시 만들었다. 같은 일을 `work/reinit.py` 로 묶었다(init·표시 이름·facts·트리거 carry).
- 묶음 A 의 NVIDIA 공급자 지원 관측을 조정했다. 보증 한도는 분기 말(2026-07-26) 유효분 $3.5B 만 값으로 쓰고, 분기 뒤 2026-08-17 서명한 SB Energy 보증
  $105B 는 basis.subsequent_event 로 둔다(다음 분기 관측). 고객 출자는 고객만의 잔액이 공시되지 않아 등록하지 않았다(생태계 지분 전체 $98.9B 는 정의가
  달라 같은 이름으로 넣지 않음). 그래서 공급자 지원 비중의 합은 미확인이다.
- 묶음 B 의 지분 평가손익 정의를 그대로 둔다. Amazon 78,850M 은 워런트 평가 줄을 뺐다(워런트는 지분증권이 아니라 파생상품). Microsoft 4,364M 은
  OpenAI 지분법 이익을 뺐다(Alphabet 태그도 지분법을 빼는 정의라 같은 잣대).
- Microsoft 는 회계연도 2027 부터 Intelligent Cloud 를 없앤 두 부문으로 보고한다. 규칙 v2.1 margins.cloud_segments 의 Microsoft 정의는 다음 실행에서
  다시 정해야 한다(이번 실행 자료는 2026-06-30 까지라 Intelligent Cloud 로 충분).
- 판단 세션에 넘길 것: ④ 칩 칸(Alphabet TPU 시스템 직접 판매 매출 인식 시작 / Amazon EC2 로만 수익화 / Microsoft Maia 자체 사용)을 같은 잣대로 읽기,
  ⑧ 고객 집중 근거 등급(Alphabet 의 Anthropic 몫은 2차 보도, Amazon 은 10-Q, Microsoft OpenAI RPO 몫은 1차 발표).
- 묶음 A 가 TSMC 투자자 페이지의 403 을 브라우저형 User-Agent·Referer 로 다시 받았다. 접근 차단 우회에 가까워 사용자에게 알리고, 이후 세션은 막힌 페이지를
  다른 열리는 출처로 대신하거나 미확인으로 둔다.
- J5(⑤⑦) 끝: 14개사 판정 입력 그대로(reconfirm). ⑦ Microsoft·NVIDIA·Oracle −2 → −3(규칙 v2.1 큼·돌아옴). 보강 요청 근거: NVIDIA 8-K(2026-08-17) Item 1.01 잔존가치
  보증 문단, NVIDIA 10-Q Note 10 SB Energy 문단, Amazon 10-Q Note 2 금융 한도 문단, Alphabet 10-Q Note 3·5 보증 상대. 판단 세션 요청을 모아 한 번에 보강한다.
- 리뷰가 볼 경계: TSMC ⑤ 비용형 −1 의 유일한 재료가 미국 관세(관세를 ⑧ 지정학으로 보면 ⑤ 4점).
- J4(②③) 끝: 28건 판정 입력 그대로(reconfirm). ③ 은 v2.1 읽기로 14개사 문장을 다시 썼고 통과는 TSMC 하나. SpaceX ③ 의 'Grok 공동 3위' 문장을 지수에 맞게
  고쳤다(회사 기준 다섯째). 리뷰가 볼 경계: Alphabet ③ Waymo(TSMC 의 '같은 수준 복제 못 함' 잣대를 대면 모방 불가능성 통과 → ③ 2→3), ② 성능 도약 '부분'
  정의가 기존 판단에서 지시서보다 넓게 읽힘(점수 영향 없음). 보강 요청 근거: NVIDIA 10-K Item 1 Competition 목록의 첫째·다섯째 항목과 넷째 항목 뒷부분
  (원문 data/_sec/docs/f516b383fa894681-nvda-20260125.htm). J2 결과가 나오면 ③ 문장의 칸 서술과 대조한다.
- 묶음 E 를 합쳤다(근거 +43 확정, 관측 +5: Alibaba 지분 평가손익·OCF·설비투자, SpaceX OCF·설비투자). Alibaba·SpaceX 설비투자는 ⑨ FCF 관측과 성분이 같다.
- ⑥ 이익 조정의 일관성: 오늘 받은 companyfacts 로 훑으니 지분 평가손익이 NVIDIA 순이익의 약 15.8%(GainLossOnInvestments 305억), Oracle 약 17%(29억),
  Tesla SpaceX 지분 평가이익 10억(순이익의 약 26%), Meta 평가손실 −15억이다. Alphabet·Amazon 에만 조정을 대면 Q03 위반이라 보강 세션(SUPPLEMENT-INSTRUCTIONS)이
  모든 USD 보고 상장사에 같은 정의로 등록한다. 정의는 Alphabet 태그 범위로 고정: ASC 321 지분증권의 평가·손상·처분 손익 순액, 지분법(ASC 323)·채무증권·워런트 제외.
  그래서 Amazon 의 매도가능 채무증권 재분류 6,794 는 정의 밖이고, Oracle 의 Ampere(지분법) 처분 이익도 빠진다. 같은 세션이 Alibaba 법인세와 판단 세션의 근거 보강도 한다.
- 보강 세션 결과를 합쳤다(근거 +13 확정, 관측 +3, 고침 1·뺌 1). 지분 평가손익: Alphabet 148,982M·Microsoft 4,364M 유지, Amazon 78,850 → 72,056M
  (매도가능 채무증권 재분류 6,794 는 정의 밖), NVIDIA 30,552M 새로(워런트 섞임 가능성은 공시 없음, basis 에 한계 표시), Tesla 1,005M 새로(공정가치 옵션
  지분법 투자라 ASC 321 문언 밖이지만 같은 SpaceX 주식을 Alphabet 쪽은 넣으므로 같은 사건 같은 성격으로 넣음 — 조율자 결정), Alibaba 는 지분법 처분·종속기업
  처분이 섞여 정의대로 가를 수 없어 뺐다. Meta·Oracle·Palantir·Apple 은 정의에 맞는 값이 없어 미등록(빠진 크기는 세전이익의 2% 안팎 이하). Alibaba 법인세는
  등록했지만 평가손익이 없어 조정은 돌지 않는다.
- ⑥ 미리보기: 이익 조정이 Alphabet·Amazon·NVIDIA·Tesla 에 적용되고(NVIDIA 조정 순이익 1,672억), 이 실행 자료로는 ⑥ 점수 칸이 바뀌는 회사가 없다.
- 묶음 D 를 합쳤다(근거 +156 확정, 출처 +107, 관측 +1). 토큰 단가 지수는 0.97(2026-10-10) broad 로 둔다 — 페이지가 SDLLMTK 를 broad-market 벤치마크로 적고
  머리 값이 그 탭이다. 비상장 보정 매출 revenue_ttm·revenue_ttm_prior 는 등록하지 않는다 — 직전 1년 값이 유출 초안·런레이트 추정에만 있고 규칙(실측, 같은 등급)을
  못 맞춘다. 그래서 OpenAI·Anthropic ⑥ 은 P/S 구간표(−4)다. 후보 값으로는 두 회사 모두 성장 조정 배수가 1 미만(천장 −2)이라 민감도가 크다 → 리포트 한계·최종 보고에 적는다.
- J1(①)·J2(④) 를 띄웠다. J3(⑧)은 J2 의 F4 파일을 읽어야 해서 그 뒤에 띄운다.
- J1(①) 끝(2026-10-13, 사용량 한도로 한 번 멈췄다가 이어서 끝냄): 14개사 모두 AI 수익화 '예' 아님 → 5점 없음. Alphabet·Amazon·Meta·Microsoft 는 사다리 합 5 라도
  상한 4. Microsoft 는 (나) 2026-07-01 AI 포함 정가 인상이 서지만 (가) 좌석 약 6.7% 라 부분. 리뷰가 볼 경계: OpenAI 가장 강한 채널(회사 1차 '기업 40% 초과' 로 소비자 유지
  → 0점, 거래로 보면 Anthropic 과 같은 잣대 1점). 공동화 트리거 6건(triggers-F1.json, 판단 파일은 참조하지 않음). EV-amazon-082·083 의 source_id 가 'SRC-SEC-anthropic-…'
  이름이라 이름만 어긋남(리뷰 과제).
- ①②③⑤⑦ 제안 70건을 반영했다. 한꺼번에 반영하던 중 proposals.json 쓰기가 Windows Errno 22(다른 프로세스가 파일을 잡음으로 보임)로 실패해, PRP-049(Microsoft ⑤)가
  판단에는 반영되고 장부에는 대기로 남았다. 장부의 그 건을 반영 함수가 남기는 모양(applied.previous·after, decided_*)으로 맞춘 뒤 남은 21건을 반영했다.
- J2(④) 끝: Apple 3→5, Oracle 2→4.5, NVIDIA 4→3, Meta 4→5, Microsoft 5→4.5, Tesla·SpaceX 4→4.5, Anthropic·OpenAI 2→2.5, Palantir 1→2 (나머지 그대로).
  잣대: 칩은 하드웨어로 팔아 매출 인식하면 판매(Alphabet TPU 시스템), 자기 클라우드·제품 안에서만 수익화하면 자체 사용(Trainium·Zhenwu·Maia·MTIA·기기 칩).
  돈을 받지 않는 자기 층은 자체 사용. 클라우드 인프라 매출 줄은 전체를 AI 수요로 센다(범용·AI 비율 공시가 없음). 리뷰가 볼 경계: Apple 의 유일한 판매 칸(모델)의
  근거가 얇다(빠지면 판매 칸이 없어 검증기가 primary_layer 로 막는다 — 규칙 빈틈, 다음 실행 과제), Google Cloud(Workspace 포함)와 M365 상업용의 비대칭,
  Palantir AI 무관 몫 0(정부 부문을 AI 무관으로 보면 52%), Tesla 서버(자체 사용이면 5.0).
- 트리거 8건 번호 붙임(TRG-113~118 공동화, 119 OpenAI Jalapeño, 120 SpaceX Cursor 매출). TRG-111 recheck 문구를 v2.1 ④ 에 맞게 고쳤다(주파수는 통신 사업이라
  보유표가 아니라 다각화 몫에 닿는다).
- J3(⑧) 끝·반영: 바뀐 칸은 Alibaba −3→−2(VIE 경유 매출 11.7~15.3% 로 '대부분' 아님), Tesla −2→−3(상하이 설치 능력 약 40%·CATL). 리뷰가 볼 경계: Meta 약정
  3.05배(2026-07 리스 $68B 빼면 2.75배 −2), Palantir 미국 정부 집중을 고객 축이 아니라 지정학 축(−3)에 둠, Microsoft 고객 33.9% 는 RPO 평균 기간을 빌린 추론,
  Alphabet·Oracle 은 고객별 RPO 비공개라 기본값 −1(공개한 Microsoft 는 −3).
- research 통과, calculate: Alphabet·Amazon 13 공동 1위, Microsoft 10.5, Apple 10, TSMC 9, NVIDIA 8, Oracle 7.5, Alibaba 7, Tesla 5.5, Palantir 5,
  SpaceX 4.5, Anthropic·OpenAI 1.5, Meta 미완료(③ 가속도 자료 없음). 규칙 변경 몫: ① 상한으로 빅테크 넷 −1, ⑦ 큼·돌아옴 −3 으로 Microsoft·NVIDIA·Oracle −1,
  ④ 형식 변경으로 Apple +2·Oracle +2.5·Meta +1·NVIDIA −1, ⑥ 성장 조정으로 Alphabet·Meta·Microsoft·Apple·NVIDIA·Alibaba·Tesla +1(Meta +2).
- 1차 리뷰 규칙 일관성(Opus): needs_fix 1건 — N1 Palantir ④ AI 무관 몫 0 은 14개사 공통 잣대(기업용 소프트웨어 줄은 AI 무관)와 어긋난다. 공통 잣대대로면 1.0 →
  ④ 2→4.5, 총점 5→7.5(Oracle 과 공동 7위). 고칠 입력·문안은 review-parts/rule-consistency.md 에 있다. 경계 사례 나머지는 통과. 점수 무관 L1~L10 은 다음 실행 과제.
- 1차 리뷰 재무 계산(Sonnet): pass. 출력·가독성(report-designer): pass, 빌드 전 권고 — 트리거 12건(TRG-006·007·012·015·019·021·026·030·034·058·071·102)이
  v2.0 점수를 지금 점수로 적음, 렌더러 설명이 v2.1 이전 내용(⑥ 방법·① AI 수익화·⑥ 카드 'PER'·HTML 방식 설명). 렌더러는 고쳐 커밋했다(9a32236, 774bd3a).
  트리거 12건과 TRG-017(옛 P3 경계)은 데이터 수정 묶음에 넣는다. 모양 문제(320px 순위표 잘림, 국면 지표가 순위표를 밀어냄, 새 표 sticky 열, 출처 표시)는
  다음 실행 과제.
- 근거 불릿(evidence-editor): pass. 이번 묶음에 고칠 근거 문장 12건(사실 오류 7: EV-tsmc-086·anthropic-076·tesla-063·openai-114·nvidia-112·openai-149·microsoft-058,
  낡은 점수 5: EV-alibaba-007·meta-002·meta-004·nvidia-004·nvidia-083). 점수 무관 243건은 다음 실행 과제.
- 수정 묶음 준비: Palantir ④(work/judge-fix1/F4-palantir.json, EV-palantir-042·019 원문 대조 끝). 트리거 14건(B1 12 + TRG-025·027 '다섯 자리' 표현 + TRG-017)과
  근거 12건은 정확한 치환 목록을 Sonnet 에게 만들게 해 적용한다(사실·출처 리뷰 결과 합친 뒤).
- 사실·출처 b(fact-checker): needs_fix 3건, 모두 ⑦ 세로축. Palantir(Strategic Commercial Contracts 누적 $325M, 10-K·10-Q 공시 → 돌아옴이면 0→−1),
  Alibaba(투자 대상과의 클라우드 계약 매출 RMB9,415M 이 EV-alibaba-089 발췌에 이미 있는데 미확인을 유리하게 풀었음 → 0→−1),
  OpenAI(Startup Fund 의 Cursor 시드·YC 토큰 지분 교환 보도 — 기금 돈이 OpenAI 자신의 돈인지에 따라 −2→−3). 점수 무관: 열리는 원문을 '열지 못해' 로 둔 두 건
  (Palantir ① 통화 전사본·CEO 서한, SpaceX ① Yahoo 전재), EV-alibaba-074 locator 쪽수, EV-tesla-008 발췌·날짜, 낡은 unverified 20건, Oracle ⑦ TikTok 연결 추론.
  → ⑦ 셋은 Opus 수정 판단 세션이 다른 회사의 투자 조직 읽기와 맞춰 판정한다(사실·출처 a 결과 합친 뒤).
- 사실·출처 a(fact-checker): pass, 점수 불변. 고칠 문장 넷 — F1 Microsoft ⑤ 판정 칸 "Anthropic 지분 투자 미확인" 은 틀림(FY26 4분기 콜 $3.2B 이익),
  F2 Meta ⑧ 분기 뒤 리스 $68B 포함(3.05배) ↔ NVIDIA 분기 뒤 SB Energy 보증 제외의 잣대 확인, F3 Apple ④ 모델 '판매' 근거(iCloud+ 한도)와 ① 의 계획 처리가 갈림,
  F4 Alphabet·Meta ② 판정 칸의 Artificial Analysis 최고 모델 서술이 12 Oct Muse Wonder(52)와 어긋남. 다음 실행 과제 10건은 리뷰 파일에.
- 사용자 지시(2026-10-13): CNBC 'Microsoft will mainly use its Maia chips for AI inference'(2026-10-12)를 추적한다. CNBC 는 WebFetch 403·앱 브라우저 Akamai 접근
  거부라 우회하지 않고, 1차 발표인 Microsoft 공식 블로그(Scott Guthrie, 2026-10-12T13:01:29Z, 정보 마감 안)를 원문으로 근거 4건 확정(EV-microsoft-070~073,
  출처 SRC-WEB-microsoft-904). 2027년 다기가와트·주력 추론은 계획이라 점수에 넣지 않고 트리거로 지켜본다. 판단 반영과 트리거 문구는 수정 판단 세션이 정한다.
- merge_group_outputs.py 는 트리거를 이전 실행의 관찰 항목으로 다시 만들어 이 실행의 TRG-113~120 을 지운다 → 수정 묶음은 덧붙이기 전용 add_fix_items.py 를 쓴다.
  문장 치환은 apply_subst.py(old 가 정확히 한 번 나와야 적용, 실패하면 되돌림).
- Apple ④ 에서 판매 칸이 하나도 남지 않으면 primary_layer 를 null 로 두고 "비교 그룹 없음" 으로 다룬다(규칙의 비교 그룹 정의가 판매 칸에서 출발하므로 판매 칸이
  없으면 그룹도 없다). 그렇게 판정될 때만 검증기·렌더러를 고친다.
- 수정 묶음 띄움: 수정 판단 세션(Opus high, FIX-INSTRUCTIONS.md — ⑦ 셋·Microsoft ⑤·Meta ⑧·Apple ④·Alphabet·Meta ②·Maia 반영과 트리거)과
  문장 치환 목록 세션(Sonnet, SUBST-INSTRUCTIONS.md — 트리거 15건·근거 12건). 치환 목록 가운데 다시 세우는 칸의 점수를 적는 항목은 depends_on 으로 표시해
  판단 반영 뒤 다시 맞춘다.
- 치환 목록 1(Sonnet, 49건) 검증·적용: 44건 적용, TRG-019·021 다섯 건은 Apple ④ 판정 뒤에 적용. TRG-017 의 산식 표현("÷ 성장률 × 100" 은 곱하기로 읽힘)을
  렌더러 표기("PER 33.0 ÷ 성장 30.6")로 고쳐 적용했다. P1′ 경계는 upper_exclusive 라 "1 미만이면 0" 이 맞다. 같은 B 부류(근거 relevance 의 낡은 자기 회사 점수)를
  리뷰가 10건 더 놓쳐 둘째 목록(subst-fix2.json)으로 함께 고친다. EV-meta-002 의 "FT" 표기는 실제 출처(Reuters 전재)와 어긋나 같이 고친다.
- 치환 목록 2(21건) 검증·적용: 19건 적용, EV-microsoft-002 두 건은 Microsoft ② 판정 뒤. 판정 재료를 풀어 쓴 문장(TSMC·Microsoft·NVIDIA ② 경로, Palantir ① 전환비용,
  Tesla·SpaceX ④ 칸)은 results calc 와 대조해 맞았다. 확정 근거에 남은 "제목·매체·날짜만 보고 판정함" unverified 문장은 사실·출처 b 가 다음 실행 과제로 적은 낡은 unverified 와 같은 부류라 이번에 손대지 않는다.
- 수정 판단 세션 결과: 점수가 바뀌는 칸은 Palantir ⑦(돌아옴, 0→−1)·Alibaba ⑦(돌아옴, 0→−1). OpenAI ⑦ 은 Startup Fund 가 "OpenAI itself is not an investor"
  (openai.fund, 2026-09-15 아카이브로 마감 전 확인)이고 YC 토큰은 체결 미확인 크레딧이라 돌아오지 않음 유지. Microsoft ⑤ 문장 정정(Anthropic 투자 이익 $3.2B), Meta ⑧ 은
  "체결 리스는 기간 뒤 것도 넣고 우발 의무는 ⑦" 이라 같은 잣대로 구분 문장만. Apple ④ 모델 칸 판매→자체 사용(①과 같은 계획 읽기), primary_layer null.
  ② 는 정보 마감 당일 Artificial Analysis 평가(Muse Wonder)를 넣으며 회사 간 상대 순위가 바뀌어 Meta·Alphabet·SpaceX 성능 도약 경로와 Anthropic·OpenAI·Alibaba
  문장을 함께 고쳤다(점수 불변). 확인 리뷰가 ② 의 같은 날 스냅숏 원칙과 맞는지 본다. Maia 트리거 TRG-121(Microsoft ④⑧)·122(NVIDIA ①⑧).
- add_fix_items 첫 실행이 발췌 600자 초과(Palantir 936·OpenAI 614)와 channel 'news'(허용 밖) 로 두 번 되돌려졌다. 발췌는 원문 문장을 바꾸지 않고 판정에 쓰는 문장만
  " … " 로 남겼고, channel 은 기존 관례(TechCrunch press, Artificial Analysis secondary, 2차 인용 보도 secondary)로 맞췄다. 새 근거 12건은 fact-checker 원문 대조 뒤 확정한다.
- 판매 칸이 없을 때 primary_layer null 을 허용하는 코드(schema·stages·render·rules.md·테스트) 커밋 59d59e3. 전체 테스트 1611·node 24 통과.
- 치환 목록의 판정 의존 7건(Apple ④ 5건은 '모델은 판매' 를 '다섯 칸 자체 사용, 판매 칸 없음' 으로 고쳐, EV-microsoft-002 2건은 그대로) 적용 → 치환 70건 모두 반영.
