# 막혔던 원문 다시 열기 결과 (2026-10-13, 실행 ai-scorecard-2026-10-v21)

브라우저 세션(fact-checker)이 앱 안 브라우저를 먼저 쓰고, 막히면 Playwright 로 한 번 더 열었다. User-Agent 는 바꾸지 않았고 CAPTCHA·"Press & Hold" 는 풀지 않았다.
새 근거 후보는 `items-reopen1.json`(9건)과 조율자가 만든 `items-lawsuit.json`(1건, EV-openai-160 으로 확정)에 있다. 하위 세션이 보고서 파일을 쓸 수 없어 조율자가 답변 본문을 옮겼다.

| 건 | 지금 근거 | 연 원문 | 결과 | 지금 근거·판단과 다른 점 | 새 근거 key |
|---|---|---|---|---|---|
| 1 | EV-openai-055 | OpenAI DevDay 2026 Recap | 열림 | 같은 사실(주간 12억 명). 원문에 발언자·무대 그래픽 서술 없음 | ev-devday-1p2b |
| 2 | EV-anthropic-098 | claude.com Marketplace 공식 글·페이지 | 열림 | 수수료 면제 문장이 공식 자료에 없음 | ev-mkt-sep23 |
| 3 | EV-openai-068 | USA TODAY 소장(사용자 제공 PDF, CourtListener 사본) | 조율자 처리 | 청구 취지 4항의 모델·학습 데이터셋 폐기 청구가 2차 기사에 없음, 피고에 Microsoft 없음 | (EV-openai-160 확정) |
| 4 | EV-apple-043 | IDC 보도자료 원문 | 열림(Seeking Alpha 는 봇 확인·구독 장벽, 사용자가 본문 제공) | 숫자 같음, IDC 는 Apple 가격 인상 효과를 말하지 않음 | ev-idc-shipments, ev-idc-drivers |
| 5 | EV-apple-045 | Top Class Actions 등 | Top Class Actions 접근 거부(Cloudflare 1009 국가 차단), Fox 칼럼 열림 | 예비 승인 2026-07-17, 최종 심리 2027-02-24 가 새 사실 | ev-siri-status |
| 6 | EV-microsoft-040 | Bloomberg 원문 | 열림(앞 두 문단만) | 같은 사실, Google Cloud 대우 문장은 확인 못 함 | ev-bloomberg-eu |
| 7 | EV-oracle-052 | OCI 가격표 | 열림(스크립트 페이지, 마감 전 스냅숏) | 과금 방식 확인, 매출은 여전히 없음 | ev-oci-pricing |
| 8 | EV-alibaba-091 | aliyun 공지 상세표 | 열림(이미지 표) | 범위 같고 규격별 차등·'목록가' 기준이 새 사실 | ev-aliyun-gpu-table, ev-aliyun-cpfs-table |
| 9 | 근거 없음($518B) | Reuters·CNBC·Tribune | 유출 초안 보도 | CNBC 전재본이 이미 EV-spacex-xai-043. 다섯 판단 모두 "보도가 있다" 줄로만 써 규칙 위반 없음(조율자 점검) | 없음 |

## 1. EV-openai-055 → OpenAI DevDay 공식 자료
- https://openai.com/index/devday-2026-recap/ (2026-09-29) 열림. "…launch new native experiences to our collective 1.2B weekly users."(도입부 셋째 문단).
- 같은 사실이다. 055 는 Engadget 의 "Altman is reiterating…", "A graphic behind Altman…" 에 근거하는데 공식 글에는 발언자·그래픽 서술이 없고 회사 문장으로만 나온다.
- openai ② 의 "DevDay 에서 Altman 은 … 말했다 [EV-openai-055]" 의 발언 주체는 공식 글에서 확인되지 않는다. ①③④ 에서 055 는 reconfirmed 목록에만 있다.
- 같은 페이지가 이미 SRC-WEB-openai-934(EV-openai-094·095)로 등록돼 있어 새 출처를 만들지 않았다.

## 2. EV-anthropic-098 → Anthropic Marketplace 원 발표문
- 열린 곳: https://claude.com/resources/articles/claude-marketplace (2026-09-23 공식 글), https://claude.com/marketplace/agents-products (현재 제품 17개와 FAQ), Internet Archive 2026-03-11 스냅숏(claude.com/platform/marketplace). anthropic.com/news/claude-marketplace 는 404.
- 9월 글 "Use a portion of your committed Anthropic spend on Claude-powered software from companies like CrowdStrike, Cursor, Harvey, Legora, Lovable, and Snowflake." 3월 스냅숏 "Use your existing Anthropic commitment to pay for Claude-powered solutions from our customers. Now in limited preview." 현재 FAQ 는 약정 사용이 "in limited preview".
- TNW 의 "without Anthropic taking a commission" 은 세 공식 자료에 없다(commission·take rate·revenue share 검색 일치 없음). OpenAI Marketplace 공식 글에도 수수료 문장이 없다. 판단 중 098 을 인용하는 곳은 없다.

## 3. EV-openai-068 → 소장 원문(조율자)
- 사용자가 준 소장 PDF 와 같은 CourtListener 문서 1 사본으로 EV-openai-160 을 확정했다. 5쪽 13항(배상 $250M 초과, 기사 수십만 건 복제), 78쪽 청구 취지 3항(영구 금지명령)·4항(원고 콘텐츠가 들어간 모든 GPT·LLM 모델과 학습 데이터셋 폐기, 17 U.S.C. § 503(b)). 피고는 OpenAI 법인 일곱 곳이고 Microsoft 는 없다. MDL 3143 관련 사건 신청.

## 4. EV-apple-043 → IDC 발표 원문
- https://www.idc.com/resource-center/press-releases/idc-pc-tracker-3q26/ (2026-10-08T17:08Z) 열림. 출하 −20.1%, 6,270만 대. Apple 행 5.9, 9.5%, 6.7, 8.5%, −11.3%. 하락 원인은 연초 재고 선매입 되돌림, 공급 제약, AI 데이터센터 구축이 끌어올린 높은 가격. 가격은 전년보다 높게 유지된다는 문장.
- 숫자는 apple ① 문장과 같다. 다만 043 의 relevance 는 "Apple 은 메모리 가격 급등으로 Mac·iPad 가격을 올렸고 …", "인상 뒤 고객이 남았는가에 쓰는 방증" 이라고 읽는데 IDC 원문에는 Apple 의 가격 인상도, Apple 이 덜 줄어든 이유도 없다.
- 사용자가 붙여 준 Seeking Alpha 본문도 같은 숫자다(Apple 590만 대, 전년 670만 대, 점유율 8.5%→9.5%).

## 5. EV-apple-045 → Siri 합의 안내
- Top Class Actions 는 두 브라우저 모두 Cloudflare 1009(접속 국가 차단), 공식 합의 사이트 smartphoneaisettlement.com 은 Cloudflare 봇 확인이라 풀지 않았다.
- Fox News 소비자 칼럼(https://www.foxnews.com/tech/apple-250m-siri-settlement-claim-95, 2026-09-29): Landsheft 외 대 Apple(캘리포니아 북부 연방법원), 2026-07-17 예비 승인, 최종 승인 심리 2027-02-24, 청구 접수 2026-09-21 개시. Apple 은 혐의를 부인. 2차 칼럼이다.
- $250M·잘못 불인정은 같다. apple ⑤ 의 "판사 승인이 남았다" 와 모순 없음(최종 승인이 남음). 합의 체결일(2026-05-05)은 045 만 근거다.

## 6. EV-microsoft-040 → Bloomberg
- https://www.bloomberg.com/news/articles/2026-10-02/microsoft-amazon-cloud-arms-set-to-face-deeper-scrutiny-under-eu-s-tech-rules (2026-10-02T11:16Z) 앞 두 문단만 보임. "Azure and Amazon Web Services are set to be designated…", 결정은 11월 예정이지만 초안이고 늦춰질 수 있다(익명 소식통).
- 040 의 둘째 발췌(Google Cloud 가 같은 심사를 받지 않는 점)는 열린 부분에 없다. microsoft ⑤ 의 "결정은 11월" 은 맞다.

## 7. EV-oracle-052 → OCI Generative AI 가격 페이지
- 정보 마감 전 상태는 Internet Archive 스냅숏 web.archive.org/web/20261006035648/https://www.oracle.com/cloud/price-list/ 로 읽었다. 정적 HTML 에 모델 행·단위·설명 문단이 있고 가격 숫자는 없다(스크립트가 채움).
- 공급자 Cohere·Meta·xAI·Google·OpenAI. 단위는 100만 토큰(xAI·Google·OpenAI), 1만 거래(Cohere·Meta), 전용 클러스터 AI unit 시간. on-demand 종량과 전용 AI 클러스터 호스팅·미세조정. 자체 모델 행 없음('Custom Model' 은 Model Import).
- 052 가 확인하지 못한 호스팅 모델의 과금 방식(사용량 종량과 클러스터 시간)이 확인된다. 매출은 없다. oracle ④ layers.model 은 "none"(layer_evidence.model = EV-oracle-035·052).

## 8. EV-alibaba-091 → 공지 상세표
- https://www.aliyun.com/notice/118086 의 "详细列表见：GPU、CPFS" 두 링크는 이미지(img.alicdn.com). 텍스트 계층이 없어 셀을 눈으로 옮겼다.
- GPU 표 열 머리글 "…规格/规格族 目录价涨幅". ECS ecs.gn8v 계열 5%, 灵骏 efg2.nvgh8bn 21%, efg2.p16en 25%–34%, ACS H2* 5%, PPU810E 25%–34%. 위쪽 행은 중국·국제 사이트, 규제 클라우드, 전 리전.
- CPFS 표는 智算版 CPFS 세 항목 모두 30%.
- 새로 확인: 열 이름이 '목록가 인상 폭' 이라 인상 방향과 목록가 기준이 공지 표로 확인되고, 규격별로 5%·21%·25%–34% 로 갈린다. 091 은 alibaba ① reconfirmed 에서만 인용된다.

## 열람 중 사고와 참고
- 브라우저 세션이 Reuters 기사 안의 소장 링크(tmsnrt.rs → fingfx.thomsonreuters.com PDF)를 앱 안 브라우저로 열었다가 사용자 화면에 저장 대화상자가 떴다. 다운로드하지 않았고 다시 열지 않았다.
- Playwright 에서는 Reuters 두 기사와 CNBC 전재본이 본문 전체로 열렸고, 앱 안 브라우저에서는 Reuters 가 DataDome 봇 확인, CNBC 가 Akamai 접근 거부였다. 유출 초안 보도라 근거로 더하지 않았다.
