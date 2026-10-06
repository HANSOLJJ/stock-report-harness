---
reviewer_agent: fact-checker
session: fc-opus55-20261001-b (3차 확인 같은 세션)
reviewed_at: 2026-10-01
---
# fact-sources — 사실·출처
검토자: Claude Opus 5.5 (claude-opus-5-5) · fact-checker 독립 세션(2차 재리뷰 + 3차 확인, 이 실행을 만든 세션 아님) · 2026-10-01
결과: pass
요약: 3차 확인에서 2차 medium 세 건(발견 1~3)이 모두 닫혔다. 이해상충 기준에 nvidia(Anthropic 투자자)와 spacex-xai(경쟁사·컴퓨트 공급자)가 들어갔다. 출처 19건이 채워져 표기 출처는 69/129건이 됐고, 지적한 4건도 모두 표기됐다. PRP-006·007 로 Oracle ⑨ 게이트 1(영업이익 $20.61B ÷ 매출 $67.36B = 30.6%)과 아마존 순부채(-$119.3B)가 verified 관측과 맞게 고쳐졌다. 점수·순위는 바뀌지 않았다. 참조 무결성, excerpt·출처·후보 일치, 인용 근거 표 38건을 다시 확인했고 새 문제는 없다. 남은 것은 low 뿐이고 다음 실행 과제로 넘긴다(조정자 지시).

검토 기준: results_hash `d82fcfa1fa3148ce…` · draft_hash `30135ffb15ac1be6…` 시점의 묶음(3차). 2차 판정은 results_hash `f4158bfdb450c1a3…` · draft_hash `3d6ae00bf9a0ab8c…` 기준이었다. 관측 387·판단 114·근거 91·트리거 40·출처 129건이다.

## 1차 발견 재확인

- [1차 medium · 닫힘] 아마존 ⑨ 런웨이 10.6년. `judgments.json` `amazon.F9.obsreg25` 의 현재 evidence 는 "런웨이 9.95년 — 완충 $115.7B(현금 $78.2B + 확정 미인출 여신 $37.5B…) ÷ 연 소진 $11.6B" 와 "현금만으로도 … 6.7년" 이다. 관측으로 다시 계산했다. 78,213 + 37,500 = 115,713, 115,713 ÷ 11,625 = 9.954, 78,213 ÷ 11,625 = 6.728 이고 `results.json` amazon F9 G3(buffer 115,713,000,000 · runway 9.9538)와 같다. TRG-005 observation, EV-amazon-001·002 relevance·conditional_impact 도 9.95년으로 고쳐졌다. 10.6 이 남은 곳은 `draft.md` 190행 취소선 "(대체됨)", `research.md` 84행 legacy 관측 행, `proposals.json`·revision_history 의 이력 문면뿐이다. 모두 옛 값으로 표시돼 있다.
- [1차 medium · 닫힘] Anthropic ⑤ 낡은 상태. EV-anthropic-002·006 relevance 는 "선별 당시 … 적대 등급 0(최소)으로 4점이었고, … PRP-001 반영으로 적대 등급 -1(비용형), 3점이 됐다" 로 고쳐졌다. TRG-037 도 같은 시점 구분으로 고쳐졌다. `results.json` anthropic F5 = A 1, H -1, 3점과 맞는다. `research.md` 737·741행도 같은 문장이다. "적대 0" 이 현재형으로 남은 곳은 없다. `judgments.json` 1534행 부근의 "H 0 = 4" 는 revision_history 의 이전 값이다.
- [1차 medium · 일부 남음] Q05 이해상충. 출처 129건 가운데 50건에 표기가 생겼고 draft 1206행의 "이해상충이 표기된 출처가 50건" 과 맞는다. company_statement 근거 13건은 모두 "발행사(또는 거래 상대) 자체 발표 — 이해당사자" 로 표기됐다. alphabet·amazon·microsoft·openai·anthropic 출처도 모두 표기됐다. 남은 곳은 아래 발견 1 이다.
- [1차 medium · 닫힘] 트리거 출처. 트리거 40건 모두 `source_ids` 가 비어 있지 않다. 트리거만 가리키는 출처 24건이 sources.json 에 있고 id 가 전부 등록돼 있다. 제목은 candidates.json 과 글자 단위로 같고 url·company_id·published_at_utc 도 같다. 발행 시각은 모두 2026-10-01 이하다. 1차가 지적한 사건마다 제목이 관측 문장과 맞는지 대조했다.
  - TRG-007 은 crn "Usage-Based Billing By Default for Copilot Business" 로 맞는다.
  - TRG-013 은 Reuters "China weighs allowing ByteDance, Alibaba…" 와 Politico "Lawmakers plan to cut off China…" 로 맞는다. "국방수권법" 은 제목에 없는 본문 수준 세부다.
  - TRG-016 은 Reuters Texas 로 맞는다.
  - TRG-017 은 simplywall.st "Starts Commercial 2 Nm Production" 과 TradingView "Q3 results Oct. 15" 로 맞는다.
  - TRG-019 은 Bloomberg 스마트홈 기사로 맞는다.
  - TRG-020 은 Stocktwits 메모리 칩 기사로 맞는다.
  - TRG-022 는 CNBC force majeure 와 Investing.com "unconfirmed report… Wisconsin" 으로 맞는다.
  - TRG-025 는 Reuters "new chip, bigger model" 과 Yahoo "20GW … by 2032" 로 맞는다.
  - TRG-026 은 Reuters 기사로 맞는다.
  - TRG-027 은 Lingxi $2B·Bloomberg 유럽·중동·Euronews 리전 기사로 맞는다.
  - TRG-028 은 Guardian 44,000건과 Middle East Eye 기사로 맞는다.
  - TRG-030 은 Moomoo 5,000대 기사로 맞는다.
  - TRG-031 은 독일 12월 표결·Reuters 안전단체·Reuters 크로아티아 기사로 맞는다.
  - TRG-034 는 $100B 발사장·Google 궤도 시험·Starship Flight 14 기사로 맞는다. "처음 궤도" 는 제목에 없지만 CNN·Space.com 보도로 사실임을 확인했다.
  - TRG-035 는 Bloomberg/Yahoo 4단계 요금제 기사로 맞는다.
  - TRG-036 은 Fortune·Reuters·Motley Fool "Possible November IPO" 기사로 맞는다.
  - TRG-037 은 Reuters 항소심과 CBS 만찬 기사로 맞는다.
  - TRG-039 는 Axios $70B·Bloomberg $1.4T/$30B·FT 상장 연기 기사로 맞고, 둘 다 2026-09-29 라 "같은 날" 이 맞다.
- [1차 low · 남음] `sources.json` `SRC-SEC-FACTS-F6` url 은 여전히 `https://data.sec.gov/api/xbrl/companyfacts/` 이다. 이번에는 SEC 에 요청하지 않았고, 1차의 404 판정을 그대로 둔다.
- [1차 low · 남음] filing 근거 18건과 filing 출처 18건의 `published_at_utc` 가 null 이다. candidates.json `filed_at` 으로 다시 대조하면 모두 2026-10-01 이하다.
- [1차 low · 닫힘] 함정 최심 동점. `draft.md` 26행이 "-11점 — Alibaba · OpenAI · Oracle — 공동" 으로 고쳐졌다.
- [1차 low · 남음] EV-anthropic-007 의 unverified·conditional_impact("Q2 다음 분기라면")가 갱신되지 않았다.
- [1차 low · 남음] EV-anthropic-002 unverified "배제 시작 시점이 기준선 판단일 이전인지 미확인" 이 그대로다.
- [1차 low · 남음] `anthropic.F5.impl48` 의 `source_ids` 는 여전히 `SRC-v15-rule` 하나다. note 도 여전히 "A +2→+1, F5 5→4" 이고 PRP-001(4→3)이 빠져 있다. evidence 의 "FTC 가 제품 안전 조사를 시작했다" 도 그대로이며 `draft.md` 408행에 실려 있다.
- [1차 low · 남음] `SRC-YF-2026-09-30` note 에 주식 수 수집일(10-01)이 적혀 있지 않다.
- [1차 low · 남음] 투자 의견성 원제목이 남아 있다. EV-alphabet-004 는 "Could Be 28% Undervalued" 이고 draft 인용 근거 표에 실려 있다. EV-meta-003 은 "Poised to Be Big Winners" 이다.
- [1차 low · 남음] `SRC-OPENAI-FUNDING-2026` 은 아무 항목도 가리키지 않는다(승계).
- [1차 low · 남음] `status: not_disclosed` 인데 `missing_type` 이 없는 승계 관측 9건이 그대로다. 대체 관측이 엔진 입력이라 점수에는 닿지 않는다.

## 발견 사항(2차 재리뷰 — 3차 확인 결과를 각 항목 앞에 적음)

1. [3차 · 닫힘] [심각도 medium] Q05 이해상충 표기가 일부 출처에 없다. `scripts/scorecard/stages.py` 의 `ANTHROPIC_RELATION` 은 출처를 고른 피드의 company_id 로만 표기한다. 그래서 다음 출처가 빠졌다.
   - (a) NVIDIA 출처 10건(news 6·filing 3·company_statement 1, 마지막 1건은 "자체 발표" 만 표기)에 Anthropic 관계 표기가 없다. NVIDIA 는 2025-11-18 Microsoft 와 함께 Anthropic 에 최대 $10B 투자를 발표했다(CNBC 2025-11-18 보도로 확인). Microsoft 가 "Anthropic 투자자" 로 표기되는 근거와 같은 사건이다.
   - (b) SpaceX-xAI 출처 11건에 Anthropic 관계 표기가 없다. xAI(Grok)는 Anthropic 의 직접 경쟁사다. SpaceX 는 Anthropic 의 컴퓨트 공급자이기도 하다(EV-spacex-xai-008: 최대 $84.5B, The Information·Reuters 보도로 존재 확인).
   - (c) 다른 기업 피드로 들어온 Anthropic·OpenAI·Google 기사도 표기가 없다. EV-spacex-xai-008(`SRC-NEWS-spacex-xai-20260930-855edb41`, Anthropic 계약), EV-spacex-xai-001(`SRC-NEWS-spacex-xai-20260605-203712fc`, Google 이 거래 상대), EV-nvidia-004(`SRC-NEWS-nvidia-20260928-596760c7`, OpenAI 투자 제안), 트리거 출처 `SRC-NEWS-spacex-xai-20260925-e95e4ee1`(Google 궤도 시험)이다.
   - 고칠 방향은 둘이다. 관계 표에 nvidia("Anthropic 투자자")와 spacex-xai("직접 경쟁사 · Anthropic 컴퓨트 공급자")를 더하거나, 규칙 문서 별표 G 가 이 관계를 적지 않는 이유를 긴장 목록에 남긴다. (c) 의 4건은 기사 대상 기준으로 표기를 더한다. 관계 표 변경은 실행 묶음 밖 코드라 만든 세션이 결정한다.
2. [3차 · 닫힘] [심각도 medium] `judgments.json` `oracle.F9` 가 PRP-003 으로 status new(noble, 2026-10-01)가 됐다. 그런데 손대지 않은 v1.5 문장 "게이트 1 ✅ 영업흑자(영업이익 $22.39B, 마진 33.2%)" 가 라벨 없이 남아 있고 `draft.md` 1047행에 실린다. verified 관측은 `oracle.operating_income_ttm.f6reg28` 20,606M ÷ `oracle.revenue_ttm.f6reg28` 67,357M = 30.6% 이다(엔진 G1 operating_margin_ttm 0.3059). 33.2% 는 legacy `quarter_note` 의 Q4 FY26 분기 마진이다(`research.md` 445행). $22.39B 는 관측·research 어디에서도 추적되지 않는다. 같은 판단의 "OCF $31.98B, capex -$55.66B", "이자보상 4.87", "Altman Z 2.18", "2026년 $45~50B 추가 조달 예정" 도 관측이나 등록 출처로 추적되지 않는다. 판단의 `source_ids` 는 `SRC-v15-html` 하나다. G1 결론(통과)은 같다.
   - 고칠 방향은 둘 중 하나다. `scorecard_cli.py judge` 로 G1 문장을 "영업이익 $20.61B, 마진 30.6%(TTM, 2026-05-31 관측)" 로 고친다. 또는 G1 줄과 위 수치 줄에 `(v1.5 인용, 이번 실행 미검증)` 라벨을 단다. 현금·소진 수치를 인용하므로 `source_ids` 에 `SRC-SEC-FACTS-F6` 도 더한다.
3. [3차 · 닫힘] [심각도 medium] `judgments.json` `amazon.F9.obsreg25`(status new)의 "순부채 -$128.7B…" 는 legacy `amazon.net_cash.v15` 값이고 `draft.md` 182행에 실린다. 같은 초안의 ⑨ 원자료 표(1100행)는 verified `amazon.net_cash.nc37` -$119.3B 를 싣는다. 한 카드 안에서 같은 지표가 두 값으로 나온다. ⑨ 엔진은 순부채를 쓰지 않아 점수에는 닿지 않는다. 1차 리뷰가 놓친 것이다.
   - 고칠 방향은 다음과 같다. judge 로 "-$119.3B(2026-06-30 관측)" 으로 고치거나 `(v1.5 인용)` 라벨을 단다.
4. [3차 · 남음, 다음 실행] [심각도 low] EV-amazon-001 conditional_impact 의 "런웨이가 이미 9.95년이라 확정 미인출 여신이 더해져도 게이트 3 판정은 그대로다" 는 이중 계산으로 읽힐 수 있다. 9.95년은 이미 확정 미인출 여신 37,500M 을 포함한다. 2026-06-10 8-K(Items 1.01·2.03)는 `amazon.undrawn_credit.fix54` 구성요소의 Term Loan $17.5B 일 가능성이 있다. 또 그 관측 basis 에 따르면 Term Loan 미인출분은 2026-09-30 에 자동 소멸하고 364일 여신 $5B 는 2026-10 만기다. 둘을 빼도 (78,213 + 15,000) ÷ 11,625 = 8.0년이라 결론은 같다. TRG-005 가 3분기 10-Q 에서 다시 보도록 걸려 있다.
   - 고칠 방향은 다음과 같다. 문장을 "이미 완충에 포함됐을 수 있다 — 본문으로 확인" 으로 고친다.

## 3차 확인(2026-10-01)
- 발견 1(Q05)은 닫혔다. 바뀐 `scripts/scorecard/stages.py` 기준으로 sources.json 의 nvidia 10건과 spacex-xai 11건이 모두 표기됐다. 회사별 null 은 이제 alibaba·apple·meta·tesla 와, 관계 표에 없는 oracle·palantir·tsmc 의 일반 보도뿐이다. 지적한 4건의 표기는 다음과 같다.
  - `SRC-NEWS-spacex-xai-20260930-855edb41`(EV-spacex-xai-008), `SRC-NEWS-spacex-xai-20260605-203712fc`(EV-spacex-xai-001), `SRC-NEWS-spacex-xai-20260925-e95e4ee1` 은 "이 기업은 Anthropic 경쟁사(xAI)이자 컴퓨트 공급자다" 로 표기됐다.
  - `SRC-NEWS-nvidia-20260928-596760c7`(EV-nvidia-004)은 "이 기업은 Anthropic 투자자(2025-11 발표)다" 로 표기됐다.
  - 제목에 Anthropic·Claude·OpenAI·ChatGPT·Google·Alphabet·Gemini·Altman·Amodei 가 들어간 출처 가운데 표기가 null 인 것은 0건이다.
  - 기존 표기 50건의 기업별 분포는 2차와 같다(alphabet 7·amazon 7·anthropic 10·microsoft 4·openai 10 등).
  - draft 1208행의 "이해상충이 표기된 출처가 69건" 은 sources.json 의 null 이 아닌 69건과 맞다.
- 발견 2(Oracle ⑨)는 닫혔다. `oracle.F9` 게이트 1 은 "최근 1년 영업이익 $20.61B ÷ 매출 $67.36B, 마진 30.6% — 2026-05-31 관측" 이다(`draft.md` 1048행). 이 값은 `oracle.operating_income_ttm.f6reg28` 20,606M, `oracle.revenue_ttm.f6reg28` 67,357M, 엔진 G1 0.3059 와 맞는다. 옛 문장은 1058행에 취소선 "(대체됨)" 으로만 남았고 revision_history 에 PRP-006 이 있다.
- 발견 3(아마존 순부채)은 닫혔다. `amazon.F9.obsreg25` 는 "순부채 -$119.3B(2026-06-30 관측)" 이고 `amazon.net_cash.nc37` -119,332M, draft ⑨ 원자료 표와 맞는다. 옛 -$128.7B 는 `draft.md` 192행 취소선에만 있고 revision_history 에 PRP-007 이 있다.
- 점수는 바뀌지 않았다. `results.json` 순위·총점 14행(alphabet 1·15 … oracle 14·3)이 2차와 같다. amazon F9 -2(G3 9.954년)와 oracle F9 -3(G3 1.321년)도 그대로다.
- 재확인한 결과 새 문제는 없다.
  - 참조 무결성 위반 0건이다. 근거 status 는 모두 confirmed 이고, new 판단이 candidate 근거를 인용한 경우는 없다.
  - 출처 제목·url 과 후보의 불일치, excerpt 와 후보 제목의 불일치는 모두 0건이다.
  - 인용 근거 표는 본문 38건과 표 38행이 같다.
  - draft 에서 "10.6년" 은 취소선 1곳에만 있고, Anthropic "적대 0·4점" 의 현재형은 없다.
- 남은 low 는 아래 "다음 실행 과제" 절에 모았다. `oracle.F9`·`amazon.F9.obsreg25` 의 `source_ids` 가 아직 `SRC-v15-html` 하나뿐이다. 그래서 새로 넣은 SEC 관측 수치(현금·영업이익·순부채)가 판단 단위의 source_ids 로는 이어지지 않는다. 관측 id 로는 추적된다. Oracle ⑨ 의 라벨 없는 v1.5 수치(OCF·capex·이자보상·Altman Z·추가 조달 예정)는 그대로다. 위 4번과 1차 low 들도 그대로 남았다.

## 다음 실행 과제
아래는 모두 점수·순위·체크리스트 판정에 닿지 않는 문장·표기 문제라 이번 결과(pass)를 막지 않는다(2026-10-01 사용자 결정). 다음 실행에서 처리한다.
1. `sources.json` `SRC-SEC-FACTS-F6` 의 url `https://data.sec.gov/api/xbrl/companyfacts/` 는 404 다(1차 확인, 이번에는 SEC 미요청). url 을 null 로 두고, 회사별 `companyfacts/CIK##########.json` 을 `publisher_url` 에 적는다.
2. filing 근거 18건과 filing 출처 18건의 `published_at_utc` 가 null 이다. 수집기가 `filed_at` 을 `published_at_utc` 로 옮겨 적게 한다.
3. EV-anthropic-007 의 unverified·conditional_impact 를 갱신한다. $11.6B 는 Q2 잠정 매출 보도로 보여 "Q2 다음 분기라면" 분기는 해당하지 않을 가능성이 크다.
4. EV-anthropic-002 unverified "배제 시작 시점 미확인" 을 원 기사 본문으로 확인한다. 2026-02 시작 보도가 있다.
5. `anthropic.F5.impl48` 을 세 군데 고친다. `source_ids` 에 SRC-NEWS-anthropic-20260925-86310879·SRC-NEWS-anthropic-20260930-a02b29dc 를 더한다. note "A +2→+1, F5 5→4" 에 PRP-001(4→3)을 덧붙인다. "FTC 가 제품 안전 조사를 시작했다" 는 "조사하고 있다(Bloomberg 2026-09-30 보도)" 로 고친다(`draft.md` 408행 부근).
6. `SRC-YF-2026-09-30` note 에 "주식 수는 수집일(2026-10-01) 기준" 을 적는다.
7. 투자 의견성 원제목 근거 두 건(EV-alphabet-004 "Could Be 28% Undervalued", EV-meta-003 "Poised to Be Big Winners")을 같은 사실의 1차 보도로 바꾼다.
8. `SRC-OPENAI-FUNDING-2026` 은 어떤 항목도 가리키지 않는 출처다(승계). 정리할지 정한다.
9. `status: not_disclosed` 인데 `missing_type` 이 없는 승계 관측 9건(anthropic/openai `*.v15` 8건, `alibaba.contracted_revenue.v15`)에 missing_type 을 채운다.
10. EV-amazon-001 conditional_impact 의 "확정 미인출 여신이 더해져도" 는 이중 계산으로 읽힐 수 있다. 9.95년은 이미 37,500M 을 포함하고, 2026-06-10 8-K 는 Term Loan $17.5B 일 가능성이 있다. 또 `amazon.undrawn_credit.fix54` 의 Term Loan 미인출분은 2026-09-30 에 자동 소멸하고 364일 여신 $5B 는 2026-10 만기라, 3분기 10-Q(TRG-005)에서 완충을 다시 잰다. 둘을 빼도 8.0년이라 결론은 같다.
11. `oracle.F9` 와 `amazon.F9.obsreg25` 의 `source_ids` 가 `SRC-v15-html` 하나다. 새로 인용한 SEC 관측 수치(현금·영업이익·매출·순부채)의 출처 `SRC-SEC-FACTS-F6` 을 더한다.
12. `oracle.F9` 의 라벨 없는 v1.5 수치(OCF $31.98B·capex -$55.66B, 이자보상 4.87, Altman Z 2.18, "2026년 $45~50B 추가 조달 예정")는 관측·등록 출처로 추적되지 않는다. 검증 관측으로 바꾸거나 `(v1.5 인용, 이번 실행 미검증)` 라벨을 단다. 아마존 ⑨ 의 "TTM capex $173B, 순차입 +$75.2B" 도 legacy 값이라 같은 처리를 한다.
13. TRG-013 의 "국방수권법", TRG-025 의 "10조 파라미터", TRG-034 의 "처음 궤도" 는 등록 출처의 제목에 없는 본문 수준 세부다. "처음 궤도" 는 웹 보도로 사실임을 확인했고, 나머지 둘은 본문을 열어 확인한다.
14. Google News 리다이렉트 URL(뉴스 출처 전부)은 기사 착지 URL 을 확인하지 못했다. 가능하면 최종 기사 URL 을 함께 적는다.

## 수행한 확인과 결과
- 참조 무결성은 통과했다. 관측 387건의 source_id, 판단 114건의 source_ids·evidence_ids, 근거 91건의 source_id, 트리거 40건의 evidence_ids·source_ids 가 전부 sources.json·evidence.json 에 있다. 트리거 근거의 company_id 는 트리거 기업과 같고, 트리거에 점수 키는 없다(C-14).
- 근거 상태는 통과했다. 91건 모두 `confirmed` 이고 reviewer·reviewed_at 이 있다. status new 판단이 candidate 근거를 인용한 경우는 없다.
- excerpt 일치는 통과했다. 근거 91건의 excerpt·title 이 candidates.json 후보 title 과 글자 단위로 같고 published_at_utc 도 같다. 원문은 기사 제목이고 본문은 대조하지 않았다.
- 정보 마감도 통과했다. run.info_cutoff 2026-10-01, price_as_of 2026-09-30 이다. 근거·출처의 published_at_utc 는 모두 마감 이하이고, filing 은 filed_at 기준으로 마감 이하다.
- 반영 판단 숫자는 통과했다.
  - Oracle 은 완충 $31.29B = `oracle.cash.cashfcf35` 31,289M 이고, 연 소진 $23.69B = `oracle.fcf_ttm.cashfcf35` -23,686M 이다. 31,289 ÷ 23,686 = 1.321년이라 results G3 1.3210 과 같다. 신용등급 논리는 제거됐고, 옛 문장은 draft 에 취소선으로만 남았다.
  - 아마존은 위 1차 재확인 첫 항목과 같다.
  - 아마존 ⑤ 의 새 문장 "이번 실행에서 적대 등급 0 인 기업은 없다" 는 results 의 F5 H 값 14개사(-1·-2·-3 뿐)로 맞다. 낡은 예시는 draft 162행에 취소선으로 남았다.
  - 단, 같은 두 ⑨ 카드의 다른 줄에 옛 수치가 남았다(발견 2·3).
- 초안 인용 근거 표는 통과했다. 인용 근거 절과 References 를 뺀 본문의 EV id 38개와 표의 38행이 정확히 같다. 각 행의 제목·url·발행일·상태("확정")를 evidence.json·sources.json 과 대조해 불일치 0건이었다.
- URL 실재는 표본으로 확인했다. 새 트리거 출처 24건은 모두 Google News 리다이렉트(302 → 200)이고 기사 착지는 확인하지 못했다. sources note 의 "url 은 Google 리다이렉트 링크다" 표기로 폴백 요건은 충족한다. 원 기사 존재는 웹 검색으로 4건 확인했다. CBS "Trump had private dinner with Anthropic CEO Dario Amodei", Axios "Scoop: OpenAI's annual recurring revenue nears $70B"(2026-09-29), Anthropic–SpaceX $84.5B(The Information·Reuters 인용 보도), Starship Flight 14 첫 궤도 도달(CNN·Space.com, 2026-09-28)이다. 기사 본문은 열지 않았다. SEC 에는 요청하지 않았다.
- 미공시 표기는 통과했다. `not_disclosed_confirmed` 13건, `unverified` 15건, `indeterminate` 2건이 분리돼 있다. Oracle ⑨ 의 "확정 미인출 여신 관측 없음" 은 `oracle.undrawn_credit.fix54`(missing_type unverified)와 맞고, 미공시로 승격하지 않았다.
- 투자 조언은 통과했다. draft 에 매매 권유·수익 보장·FOMO 문구가 없다. 의견성 원제목 2건은 위 low 로 남았다.

## 체크리스트 기여
- Q05(출처가 이해당사자인가): pass(3차). 자체 발표 13건, Anthropic 당사자·경쟁사(OpenAI·xAI)·투자자(Alphabet·Amazon·Microsoft·NVIDIA) 출처, 다른 피드의 Anthropic·OpenAI·Google 기사가 모두 출처 단위로 표기됐다. 2차의 fail 사유(발견 1)는 해소됐다.
- Q09(미래 계획을 현재 점수에 넣었나): pass(사실·출처 범위). 트리거 40건에 점수 키가 없다. 계획·검토 단계 사건(TRG-007·019·025·027·034·035 등)은 observation 에 계획·검토로 분리돼 있다. PRP-003~005 도 계획을 점수 재료로 쓰지 않는다. Oracle ⑨ 의 "$45~50B 추가 조달 예정" 은 서술일 뿐 게이트 입력이 아니다.
- Q23(벤치마크를 다른 하네스끼리 비교했나): pass(사실·출처 범위). 1차 이후 ② 판단과 모델 발표 근거는 바뀌지 않았다.
