---
reviewer_agent: fact-checker
session: fc-opus55-20261006-rescore-r1
reviewed_at: 2026-10-06
round: 1
---
# fact-sources — 사실·출처
검토자: Claude Opus 5.5 (claude-opus-5-5) · 사실·출처 독립 세션(이 실행을 만든 세션 아님, evidence-editor 관점 포함) · 2026-10-06 · 1차
결과: pass
요약: 점수·순위·체크리스트 판정을 바꾸는 발견은 없다. 확인한 것은 다음과 같다. 참조 무결성(관측 525·판단 183·근거 72·트리거 183 참조가 모두 출처 207건 안에 있다), 근거 72건 전부 confirmed·검토자·검토일 있음, excerpt 71/72건이 후보 제목과 글자 그대로 같다, 기준일 뒤 자료 없음. 새 재무 관측 29건의 성분 값은 SEC 원문 캐시와 20-F 보존본에서 전부 찾았고, 산술·환율·인용문·쪽 위치도 재현했다(예외 1건). 부재 주장(알리바바 계약수입 확인된 미공시, TSMC 미인출 여신 unverified)도 원문으로 재현했다. PRP-001~004 판단 문장의 숫자는 확정 관측과 맞다. 트리거 79건의 carry 표는 triggers.json 과 79/79 일치하고, 인용한 매체·날짜·숫자는 후보 제목과 맞는다. medium 네 건이 남았다. 사건이 일어났는데 fired 로 처리하지 않은 트리거 두 건(TRG-057, TRG-078 의 SpaceX 몫), 부재 주장이 틀린 트리거 한 건(TRG-070 'Cursor 0건' — 실제로는 4건), 판단 단위 source_ids 에 새 SEC 출처가 빠진 것 한 건이다. 넷 다 점수에는 닿지 않아 결과를 막지 않는다. 다만 셋은 승인 전에 고칠 만하다(아래 「다음 실행 과제」 1~3).

검토 기준: results_hash `1101644bc117e2a2…`, draft_hash `1168a515ee524414…`(review.md frontmatter 와 같음을 확인). 관측 440·판단 114(new 12)·근거 72·트리거 79·출처 207·후보 4,507건.

## 수행한 검토 (전수, 스크립트는 스크래치 `review/fs_*.py`)

- **참조 무결성**: 관측·판단·근거·트리거·제안의 `source_id`/`source_ids`/`evidence_ids` 를 재귀로 전부 모아 대조했다. 빠진 것 0건. draft.md 의 SRC 207·EV 56 참조도 모두 있다. research.md 에서는 EV 두 개가 이번 장부에 없다(발견 9).
- **근거 72건**: 38건은 이전 실행 근거와 모든 칸이 같고(reviewed_at 2026-10-01), 34건은 이번에 확정했다(noble, 2026-10-06). 상태는 전부 confirmed 다. `status: new` 판단 가운데 EV 를 인용한 것은 anthropic.F5.impl48(EV-anthropic-002·006, confirmed) 하나다. excerpt = 후보 제목인 것이 71건이고, 예외는 EV-anthropic-010 이다(발견 7). 가장 늦은 발행시각은 2026-10-05T23:09:19Z 다. 공시 9건은 published_at_utc 가 null 이고 filed_at 은 2026-06-10~10-02 이다. 후보 창은 2026-04-09~10-06 이다.
- **새 재무 관측 29건**: 성분 값을 원문에서 찾았다. Oracle 은 companyfacts(start·end·accn 까지 일치)와 10-Q·10-K 본문, TSMC 는 6-K 연간·반기 연결재무제표 4건, 알리바바는 20-F(`validation/offb-24/_raw`, sha256 은 CRLF 를 정규화하면 출처 장부와 같음)와 6-K 보도자료 2건이다. 알리바바 차입금 266,530 은 5개 행의 합이고, TSMC 상장주식 유동분 2,500,625 는 B/S 193,182,690 − 채무증권 190,682,065 로 나온다. 모두 재현했다. 성분 합계와 원통화÷환율도 29건 모두 관측값과 같다(TSMC 는 천 단위). 인용문은 Oracle RPO·제한현금·회전여신 주석 6·MD&A·약정 준수·CP, TSMC VIS 처분·주석 32·33g·33h, 알리바바 474,505 문단을 원문과 대조했다. 쪽 위치는 10-K p.53·65·68·85·86, 10-Q p.1·2·5·6·7·33, 20-F F-5·F-12 를 재현했다(10-Q p.13 은 예외, 발견 10). 환율은 TSMC 31.37 을 `git show f14a235:validation/tsm-edgar-29/_raw/tsm-20251231.htm` 에서(sha256 이 출처 장부와 같음), 알리바바 6.8980 을 20-F 에서 확인했다.
- **부재 주장**: alibaba.contracted_revenue.obsreg25(not_disclosed_confirmed)는 20-F F-21 'Practical expedients and exemptions' 문장이 있고 'remaining performance obligation' 은 0건이다. 2026 6월 분기 6-K 에도 RPO·backlog 는 0건이다. 이것이 알리바바 ⑨ −4 의 G4 근거다. tsmc.undrawn_credit.rs1006 은 missing_type=unverified 이고, 2026H1·2025H1 6-K 검색 건수 13개가 basis 와 정확히 같다. oracle.F7 의 '8월 말 OpenAI 몫 미공시'는 10-Q 본문에서 'OpenAI' 0건으로 확인했다.
- **판단 근거 숫자(14개사)**: 판단 근거 문장의 달러 금액을 모든 관측값과 대조해, 대체된 관측 값과 같고 현재 값과는 다른 것을 찾았다. FCF·순현금·현금·매출·영업이익·RPO·순이익 키워드 숫자도 results 가 쓴 관측과 대조했다(오차 3%). 걸린 것은 분기·부문 값이거나 v1.5 표시가 붙은 승계 문면뿐이고, 발견 5·6·16 만 남는다. PRP 네 판단은 다시 계산했다. Oracle 은 23,057/71,776=32.1%, 영업현금흐름 46,940, 설비투자 75,660, 런웨이 (36,369+10,000)/28,720=1.61년과 1.27년, 664/250=2.66, 332/71.78=4.6년, 선수금 제외 −40.08B 다. 알리바바는 30,323/1,044,971=2.90%, 24,048/11,102=2.17년, 254,198/6.898=36,851, 67,678/38,676=+75% 다. TSMC 는 FCF 36.45, 순현금 86.51(VIS 제외 84.06), 마진 56.1% 다. 모두 맞다.
- **다른 기업 점수 인용**: 판단 근거에서 다른 기업의 factor 점수를 인용한 것은 승계 판단 4줄뿐이다(microsoft.F3→애플 ③2, apple.F5→NVIDIA ⑤2, openai.F4→Anthropic ④4). 모두 잣대 비교이고 현재 results 값과 같다.
- **트리거 79건**: research.md 「이전 트리거 처리」 79행의 결론·확인 내용이 triggers.json 과 전부 같다. finding 이 인용한 매체+날짜 쌍을 후보 제목과 대조해 모두 찾았다(표기 차이 1건, 날짜 차이 1건은 발견 13). 숫자(464,391대·486,532대·13.7GWh·$518B·$664B·$42B·$8B·$30B·$84.5B·$920M·19개 중 13개·$100B/$2T mezha)도 후보 제목에 있다. 기업별 공시 목록(2026-09-02~10-06)도 각 finding 의 서술과 맞다. 0건 주장은 OpenRouter·Baltra·iOS 27·new Siri·SDLLMTK·CDS·credit default·interconnect 를 재현했고 Cursor 는 틀렸다(발견 3). finding 이 '본문 미열람'이라 적은 8-K 4건은 `sec-get` 으로 받아 확인했다. NVIDIA 2026-09-03 은 Hugging Face 확정 계약($11.9B, 2027 상반기 종결)이라 finding 의 추정과 맞다. Microsoft 2026-09-02 는 FY27 부문 변경이라 맞다. Oracle 2026-09-14 는 Ellison 의 10b5-1 매도 계획 취소라 TRG-022 조건과 무관하다. Amazon 2026-09-14 는 파운드화 회사채 발행 완료다(발견 8).
- **URL**: Google News 출처 163건은 수집 원문 RSS(raw_ref)에 URL 이 그대로 있다. EDGAR 공시 출처 26건은 원문 submissions JSON 에서 접수번호와 주문서명이 모두 확인된다. 새 SEC 출처 8건은 `data/_sec/docs` 캐시의 sha256 이 출처 장부와 같다. Oracle 10-K(SRC-SEC-ORCL-10K-FY2026)는 캐시 index 에 항목이 없어 오늘 `scorecard_cli.py sec-get` 으로 다시 받았고, sha256 517287f8… 이 장부와 같다(발견 12). url=null 은 6건이고 내부 기준선 4건과 재수집 금지 보도자료 2건이다. note 에 사유가 있다. SEC 요청은 sec-get 으로만 했다(5회). User-Agent 는 직접 만들지 않았다.
- **기준 시점**: 관측 as_of 와 observed_at, 출처 accessed_at 이 모두 기준일(2026-10-06) 이하다. 가격·시총 관측 24건은 2026-10-05(SRC-YF-2026-10-05)로 run.json price_as_of 와 같다.
- **근거 불릿(evidence-editor)**: relevance 는 '추론:' 이나 '사실:/추론:' 표시가 72건 모두 있다. 뉴스 63건은 모두 '제목만' 단서가 있다. conditional_impact·horizon·counter_evidence·unverified·channel 은 빈 칸이 없다. 매수·매도·목표주가·수익 보장·FOMO 같은 금지 표현은 근거와 draft 모두에서 0건이다(draft 1557행은 면책 문구다).

## 발견
| 등급 | 위치 | 발견 | 점수 영향 |
| --- | --- | --- | --- |
| medium | triggers.json TRG-057 (baseline/v1.5:TRIG-011) | 사건(Oracle 2026-09-10 실적 8-K, 2026-09-11 10-Q)이 일어났고 수집됐다. 이 10-Q 로 관측을 갱신해 Oracle ⑥ 이 −2→−1 로 움직였다. 그런데 status 가 `expired` 다. guide.md 4.1 과 score-collect 규칙은 "사건이 일어났으면 fired" 이고 expired 는 "기한이 지나 의미가 없어졌다"는 뜻이다. 그래서 research.md 에 「발동 트리거 재검토 대상」 행(Oracle ⑦·⑧)이 없다. ⑦ 문장은 PRP-002 로 이미 고쳐졌고 ⑧ 은 10-Q 에 OpenAI 몫이 없어 유지 이유가 finding 에 있다. | 없음(점수는 관측에서 산출, ⑦⑧ 판정 재료 불변) |
| medium | triggers.json TRG-078 (baseline/v1.5:TRIG-029) | 기준선 항목은 'Optimus 생산 개시 · Starship 페이로드' 둘이다. SpaceX 몫(Starship 페이로드 실측, Flight 14 Starlink 배치, EV-spacex-xai-007)은 사건이 일어났다고 finding 이 스스로 적었다. 그런데 항목 전체를 `withdrawn`(이어받음)으로 닫았다. SpaceX 몫은 fired 로 두고 재검토 표에 "수정하지 않음 — ④ 이미 범위 맨 위, ② 는 비AI 귀속 원칙상 근거 아님" 을 적는 것이 규칙에 맞다(기업별 항목 분리는 guide.md 4.1 이 허용). | 없음 |
| medium | triggers.json TRG-070 (baseline/v1.5:TRIG-027) carry.finding · research.md 999행 | "전 기업 뉴스 후보 2026-04-09~10-06 제목 검색 'Cursor'·'Anysphere' 0건" 이 사실과 다르다. spacex-xai 후보에 4건이 있다. Reuters·CNBC 2026-06-16 'SpaceX locks in $60 billion Cursor deal'·'SpaceX to acquire … Cursor for $60 billion', Reuters 2026-07-07 'SpaceXAI plans to launch new model with Cursor', a16z 2026-08-14 이다. 제목만으로는 '기본 모델 Grok 전환·Claude 비중 축소'가 확인되지 않아 watching 결론 자체는 지킬 수 있다. 다만 부재 주장이 틀렸고 가장 가까운 사건이 빠졌다. | 없음(조건 미충족이면 판단 불변) |
| medium | judgments.json oracle.F9 · oracle.F7.fix52 · alibaba.F9.obsreg25 · tsmc.F9 (PRP-001~004) | 근거 문장을 새 SEC 원문 기반 숫자(2026-08-31·2026-06-30)로 바꿨다. 그런데 `source_ids` 는 [SRC-v15-html(·rule·md)] 그대로이고 새 출처 8건(SRC-SEC-FACTS-ORCL-20261006, SRC-SEC-ORCL-10K-FY2026, SRC-SEC-TSM-6K-*, SRC-SEC-BABA-6K-*)이 판단 단위에서 이어지지 않는다. 숫자 자체는 관측(rs1006)과 맞아 관측 경유로는 추적된다. alibaba 문장만 관측 ID 를 적는다. | 없음 |
| low | judgments.json alibaba.F9.obsreg25 · draft.md 802행 | 취소선 줄의 "(superseded … 이번 실행 점수는 -3)" 이 낡았다. 이번 실행 알리바바 ⑨ 는 −4 다(같은 판단 다음 줄과 results). | 없음 |
| low | judgments.json amazon.F9.obsreg25 (status new) | "게이트 4 ✅ 미개시 리스 $106B(매출 0.14배)" 는 v1.5 값이다. 같은 판단의 "미개시 리스만 쓰면 3.615"(496,000/3.615 ≈ $137B)와 B종 $267.3B 와 어긋난다. draft 는 '주의 — 원문 $106B 는 …$267.3B' 로 표시했다. | 없음 |
| low | evidence.json EV-anthropic-010 | title·excerpt 가 "… BBC told - bbc.com" 이다. 후보(raw_ref `data/anthropic/news/google/raw/20261006T054442Z-d3679f8b.xml`)와 출처 장부 제목은 "… BBC told - BBC" 다. excerpt 는 더 이른 수집본(043405Z·043614Z)의 표기와 같다. 본문 문언은 같고 매체 꼬리표만 다르다. | 없음 |
| low | triggers.json TRG-005 carry.finding | 2026-09-14 아마존 8-K 를 '본문 미열람' 으로 두고 회사채 발행을 '계획 단계' 로만 적었다. sec-get 으로 확인해 보니 Item 8.01 은 £4.25B 회사채 발행 완료(순조달 약 £4.235B)다. 조건(3분기 10-Q)과 ⑨ G3 통과(런웨이 9.95년)에는 영향이 없다. | 없음 |
| low | evidence.json EV-apple-005 relevance · TRG-057 finding | 이전 실행 근거 EV-apple-003·EV-oracle-002 를 인용한다. 이번 evidence.json 에는 없다(이전 확정 91건 중 38건만 이어받음). TRG-055·079 note 는 같은 사정을 밝혔고 EV-apple-005 는 밝히지 않았다. | 없음 |
| low | observations.json oracle.net_cash.rs1006 성분 operating_lease·finance_lease location | "10-Q 주석 6 p.13 `Total operating lease liabilities` (유동 4,027 + 비유동 30,594)" 로 적었는데, 그 줄은 p.12 보조 재무상태표에 있다. p.13 에 있는 것은 만기표의 `Total lease liability $34,621 $9,185` 다. 값은 같다. | 없음 |
| low | observations.json oracle.undrawn_credit.rs1006 basis.search.hit_counts_10k | 'revolv' 26건이라 적었으나 재현하면 35건이다(나머지 키워드 건수는 일치). 결론(약정 1건 $10.0B)은 같다. | 없음 |
| low | data/_sec/docs/index.json | SRC-SEC-ORCL-10K-FY2026 캐시 파일은 있는데 index 에 항목이 없었다(동시 기록 경합으로 보임). 오늘 sec-get 으로 다시 받아 항목이 생겼고 sha256 이 장부와 같다. | 없음 |
| low | triggers.json TRG-006 · TRG-010·011·012·056 | TRG-006 "qz 2026-10-06" 은 후보 발행이 2026-10-05T19:35Z 다. 메타 항목들의 "메타 뉴스 2026-09-03~10-06 303건" 은 후보 news 307건이다. | 없음 |
| low | preview.md 「이전 실행 대비」 | 알리바바 ⑨ −3→−4 의 원인이 "✍️ 판단 수정" 으로 적혀 있다. PRP-003 은 근거 문장만 바꿨고 gate_inputs 는 그대로다. 실제 원인은 관측 갱신(FCF·현금)이다. | 없음 |
| low | judgments.json oracle.F7.fix52 · oracle.F9 | 갱신된 2026-08-31 숫자 옆에 v1.5 값이 표시 없이 남아 있다. oracle.F7 의 '자체 부채 $167B'(현재 차입 $125.3B + 리스 $43.8B), oracle.F9 의 'Debt/EBITDA 5.03·이자보상 4.87·Altman Z 2.18' 이다. 게이트 입력은 아니다. | 없음 |

## 체크리스트
| ID | 결과(pass/fail/not_applicable) | 근거 |
| --- | --- | --- |
| Q05 | pass | 이해당사자 출처를 확정 사실로 쓰지 않았다. 벤더 발표 벤치마크(Gemini 4 Argon '19개 중 13개', NVIDIA 블로그의 Astra 가속, Microsoft 음성 모델)는 TRG-001·009·040·066 에서 방증으로만 다뤘다. 회사 주장('중국에서 가장 강력한')은 EV-alibaba-007 counter_evidence 에 적혔다. 출처 장부의 `conflict_of_interest` 표기는 AGENTS.md 「금지·주의」(2026-10-02)에 따라 점검하지 않았다. |
| Q09 | pass | 계획·발표는 점수 입력에 없다. 아마존 $42B 회사채 추진·$8B 칩 매각 추진(TRG-005), 알리바바 8월 증자(완충 제외, alibaba.F9), Anthropic 상장 목표(TRG-036), 테슬라 Optimus 계획(TRG-030)이 그렇다. 기준일 뒤 사건은 관측에 없다. Oracle 미인출 여신은 10-K 기준일 값이고 mixed_as_of 로 표시했다. 승계 문면의 계획 문장(oracle.F9 '$45~50B 추가 조달 예정', tsmc.F9 capex 가이던스)은 gate_inputs 에 닿지 않는다. |
| Q14 | pass | 진행 중인 사건은 끝난 것으로 세지 않았다. Anthropic S-1·상장, Hugging Face 종결(8-K 원문은 2027 상반기 종결 예정), OpenAI $30B 라운드, EU 표결, 영국 Palantir 계약은 모두 watching 이다. 알리바바 G4 는 '모름' 이 아니라 원문으로 확인한 미공시만 C-16 으로 보냈다. |
| Q23 | pass | 사실·출처 관점에서 서로 다른 하네스의 벤치마크 비교를 근거로 쓴 곳이 없다. TRG-040 은 같은 하네스 독립 측정을 조건으로 두고, 벤더 수치는 조건 미충족으로 처리했다. |

## 다음 실행 과제
1. (medium, 승인 전 고칠 만함) TRG-057 을 `fired` 로 바꾸고 「발동 트리거 재검토 대상」에 Oracle ⑦(PRP-002 로 근거 문장만 갱신)과 ⑧(10-Q 에 OpenAI 몫·고객 집중 서술 0건이라 수정하지 않음) 행을 넣는다.
2. (medium, 승인 전 고칠 만함) TRG-078 을 기업별로 나눈다. SpaceX 몫(Starship 페이로드 실측)은 `fired` + "수정하지 않음" 사유로 두고, 테슬라 몫(Optimus)은 TRG-030 으로 철회한다.
3. (medium, 승인 전 고칠 만함) TRG-070 finding 의 'Cursor 0건' 을 고친다. 2026-06-16 SpaceX 의 Cursor 인수($60B), 2026-07-07 'SpaceXAI·Cursor 새 모델 출시' 보도를 적고, 제목으로는 기본 모델 전환·Claude 비중 축소가 확인되지 않아 watching 을 유지한다고 적는다. 가능하면 Reuters 07-07 본문을 열어 전환 여부를 확인한다.
4. (medium) PRP 판단 네 건의 `source_ids` 에 새 SEC 출처를 더하는 판단 변경 제안을 올린다(사람 반영 필요). Oracle·TSMC 문장에 쓴 관측 ID(rs1006)를 alibaba 처럼 적는다.
5. (low) alibaba.F9.obsreg25 취소선 줄의 "이번 실행 점수는 -3" 과 amazon.F9.obsreg25 의 "미개시 리스 $106B" 를 현재 값과 맞추거나 v1.5 문면으로 표시한다. oracle.F7·F9 의 v1.5 수치($167B, Debt/EBITDA 등)에도 표시를 붙인다.
6. (low) EV-anthropic-010 의 title·excerpt 를 raw_ref 원문 표기("- BBC")로 맞춘다. 다음 선별부터 excerpt 를 raw_ref 의 제목에서 기계로 복사한다.
7. (low) '본문 미열람' 공시는 sec-get 으로 열어 finding 에 적는다. 이번에 열어 본 결과는 Amazon 09-14(파운드화 회사채 발행 완료), NVIDIA 09-03(HF 확정 계약), Microsoft 09-02(부문 변경), Oracle 09-14(Ellison 매도 계획 취소)다. TRG-005 finding 에 회사채 발행 완료 사실을 더한다.
8. (low) 이어받지 않은 이전 근거(EV-apple-003·EV-oracle-002 등)를 인용하는 문장은 출처 ID 로 바꾸거나 그 사실을 적는다.
9. (low) oracle.net_cash.rs1006 리스 성분 위치를 p.12 로 고치고, oracle.undrawn_credit 의 'revolv' 건수(26→35)를 다시 센다. sec-get 캐시 index 의 동시 기록 경합을 막는다(index 에 빠진 파일이 있었다).
10. (low) preview 의 변동 원인 분류가 '판단 수정' 을 gate_inputs·score 변경으로만 세게 한다. 근거 문장만 바꾼 제안은 원인으로 세지 않는다.
11. (low) 트리거 finding 의 날짜·건수 표기(TRG-006 qz 날짜, 메타 303건)를 후보 기준으로 맞춘다.
