# 보강 세션 지시서 (2026-10 규칙 v2.1 첫 실행)

실행 `ai-scorecard-2026-10-v21`(기준일·정보 마감 2026-10-12)에 관측과 근거를 보강한다. **실행 폴더 파일은 읽기만 한다.** 산출물은 `.agents/plans/v21-first-run-2026-10/work/out-S.json` 하나이고 모양은 `GROUP-INSTRUCTIONS.md` 의 「출력」과 같다(`sources`·`evidence`·`observations`·`notes`). 여기에 `observation_fixes`(이미 실행에 있는 관측을 고치거나 뺄 것: `{"observation_id", "action": "replace"|"remove", "replacement": {...}, "reason"}`)를 더한다. CLI 는 `sec-get`·`resolve-urls --url` 만 쓴다. 공통 규율(원문 확인, 발췌·locator, 0 으로 채우지 않기, 접근이 막힌 페이지를 User-Agent 를 바꿔 우회하지 않기)은 `GROUP-INSTRUCTIONS.md` 와 같다.

## 1. 지분 평가손익 `equity_investment_gains_ttm` — 모든 USD 보고 상장사에 같은 정의

**정의(고정):** ASC 321 지분증권(시장성 지분증권의 공정가치 평가, 비시장성 지분증권의 측정대안 상향·하향 조정과 손상)의 평가·처분 손익 **순액**, 세전, 최근 1년(네 분기). **빼는 것:** 지분법(ASC 323) 투자의 지분 손익과 그 처분 손익, 채무증권(매도가능 채무증권 재분류 포함), 워런트·파생상품. Alphabet 의 `us-gaap:EquitySecuritiesFvNiGainLoss` 가 이 범위다.

- 회사: nvidia, oracle, tesla, meta, microsoft, apple, palantir, amazon, alphabet. 10-Q·10-K 의 '기타 영업외 손익(Other income (expense), net)' 주석 표나 투자 주석에서 줄을 찾고, 분기별 값을 네 분기 합한다. 태그가 정의와 같으면 태그 값을 써도 되고, 주석 표와 대조한 사실을 `basis.reconciliation` 에 적는다. `basis.components` 에는 서로 겹치지 않는 구성(줄 이름이나 태그, 분기별 값, accession)을 적는다.
- 이미 실행에 있는 관측도 이 정의로 다시 본다. `alphabet.equity_investment_gains_ttm…`(148,982M), `amazon…`(78,850M: 시장성 지분 평가 1,619 + 비상장 지분 상향 70,437 + 매도가능 채무증권 재분류 6,794 — 채무증권 줄은 정의 밖이다. 하향 조정·손상 줄이 따로 있으면 넣어 순액으로), `microsoft…`(4,364M), `alibaba…`(9.66B: 'Gain on deemed disposals/disposals/revaluation of investments' 줄 — 지분법 투자의 간주 처분 이익이 섞였는지, 투자 손상을 뗄 수 있는지 20-F·6-K 주석에서 본다). 정의와 다르면 `observation_fixes` 로 고친 값을 내고, 정의에 맞게 가를 수 없으면 `remove` 로 내고 이유를 적는다(맞지 않는 값을 같은 이름으로 두지 않는다).
- 해당 손익이 최근 1년에 없으면 등록하지 않고 `notes` 에 찾아본 범위를 적는다(0 으로 등록하지 않는다).
- 관측 키는 `GROUP-INSTRUCTIONS.md` 「관측」과 같고, `period{start,end}` 가 필수다. 출처는 SEC 주소로 등록한다.

## 2. Alibaba 법인세 `income_tax_ttm`

기존 `alibaba.pretax_income_ttm.rs1006` 과 **같은 조립**(20-F 회계연도 값 − 전년 같은 분기 + 올해 같은 분기, 위안, 환율 6.8980, 연결 범위)으로 법인세 비용을 만든다. 성분 셋의 줄 이름·값·accession·위치를 `basis.component_accessions` 에 적는다. `basis.ownership_scope` 는 세전이익 관측과 같은 값을 쓴다(세전이익 관측의 basis 를 먼저 읽는다).

## 3. 근거 보강 (판단 세션 요청)

각 문단을 원문에서 발췌해 새 근거로 낸다(필수 키는 score-collect 스킬).
- NVIDIA 8-K(2026-08-17) Item 1.01 'Residual Value Guaranties' 둘째·셋째 문단(리스 개시 때 발효, 지급 사유, OpenAI 의 보상·면책, DSX 플랫폼 배치).
- NVIDIA 10-Q(2026-07-26 분기) Note 10 Guarantees 의 SB Energy 문단("on behalf of a customer, an affiliate of OpenAI", 첫 발효 회계 2029, 세입자 채무불이행 때 지급).
- Amazon 10-Q(2026-06-30) Note 2 의 Anthropic 금융 한도 문단(컴퓨트 인도 이정표마다 열림, 시리즈 H $5.0B 투자).
- Alphabet 10-Q(2026-06-30) Note 3·5: 금융보증 $7.6B·신용 파생 $43.8B·추가 보증 $24.1B·조건부 출자 $20.0B 의 상대가 밝혀져 있으면 그 문단. 밝혀져 있지 않으면 `notes` 에 그 사실.
- NVIDIA 10-K(2026-01-25 회계연도) Item 1 Competition 목록의 첫째 항목(AMD·Huawei·Intel)과 다섯째 항목(네트워킹 경쟁사), 넷째 항목 뒷부분(Tesla 자체 SoC 팀). 원문 캐시 `data/_sec/docs/f516b383fa894681-nvda-20260125.htm`. 기존 EV-nvidia-102 와 겹치지 않는 부분만.

마지막 답변: 회사별 지분 평가손익(값과 구성, 정의에 맞는지), 고친·뺀 관측과 이유, Alibaba 법인세, 보강 근거 목록, 못 찾은 것. 문장은 완결된 현재 상태 문장으로 쓴다.
