# 판단 세션 지시서 (2026-10 규칙 v2.1 첫 실행)

실행 `ai-scorecard-2026-10-v21`(기준일·정보 마감 2026-10-12, 규칙 v2.1)은 직전 실행 `ai-scorecard-2026-10-recheck` 와 사실이 같고 규칙만 v2.1 로 바뀌었다. 정기 실행이라 ①②③④⑤⑦⑧ 판단을 14개사 전부 이 실행에서 다시 매긴다(`docs/scorecard/rules.md` 2.9). 한 세션이 맡은 항목을 14개사 전부 맡는다.

공통 절차는 `.agents/plans/rejudge-all-2026-11/REJUDGE-INSTRUCTIONS.md` 를 그대로 따른다(세 칸 문장, `[EV-…]` 표지, 사건 교차표 5-1, 근거 등급 5-2, 미확인 처리, 완결된 현재 상태 문장, 하지 않는 것). 항목별 기준은 `docs/scorecard/rules.md` 3·4절이 원본이다. 아래는 이 실행에서 달라진 점이다.

## 달라진 점

1. **출발점.** `output/ai-scorecard-2026-10-v21/judgments.json` 의 판단은 직전 실행이 같은 날 같은 근거로 매긴 것이다. ①④⑧ 은 규칙이 바뀌어 판정 재료부터 새로 정해야 하고(④⑧ 은 형식이 점수에서 판정 입력으로 바뀐다), ②③⑤⑦ 은 규칙 문언이 닿는 자리만 다시 본다. 입력이 같으면 `changes` 를 비우고 `reconfirm` 에 다시 읽은 근거 ID 를 적는다. 그때도 세 칸 문장은 지금 규칙·지금 근거에서 그대로 맞는지 읽고, 맞으면 그대로 옮겨도 된다. 이 실행에서 바꾼 잣대(⑦ 큼·돌아옴 −3, ③ 보유표의 판매·자체 사용 칸을 모방 불가능 자산 후보로 읽기, ① AI 수익화 '예' 의 두 조건)가 닿는 문장은 다시 쓴다.
2. **새 근거.** 회사 묶음 다섯이 ①④⑧ 재료를 원문에서 확인해 근거로 올렸고 조율자가 확정했다. 묶음의 사실 정리는 `.agents/plans/v21-first-run-2026-10/work/out-<A~E>.json` 의 `layer_map`·`notes` 에 있다(근거 ID 는 `evidence.json` 에서 제목으로 찾는다). 확정 근거만 인용한다. 꼭 필요한데 후보이거나 없는 근거는 마지막 답변에 적는다.
3. **CLI 를 부르지 않는다.** 출력 파일만 쓴다. `sec-get`·`resolve-urls --url` 로 원문을 다시 여는 것은 된다.

## 항목별 판정 재료 (`changes` 에 넣는 키)

- **① (J1)** lockin 입력 전부: `channel_consumer`·`channel_work`·`channel_trade`(채널, `yes`·`no`), `loop`·`switching`·`substitutes`·`pricing`(회수 루프·전환비용·대체 공급·가격 실측. `pass`·`partial`·`fail`·`unknown`), `pricing_sustained_quarters`(가격 실측 통과면 필수), `durability_discount`(`yes`·`no`·`unknown`), `ai_monetized_in_channel`(`yes`·`partial`·`no`·`unknown`). **`yes` 는 두 조건이 함께 설 때만이고, 그때 재료 여섯이 필수다:** `ai_monetized_channel`(`consumer`·`work`·`trade`, 가장 강한 채널이고 그 채널 키가 `yes`), `ai_monetized_measure`(`customers`·`seats`·`revenue`), `ai_monetized_share`(0~1, 과반이면 0.5 초과), `ai_monetized_period`(분자·분모 기간 문자열), `ai_separate_billing_evidence`·`ai_price_uplift_evidence`(확정 근거 ID 목록). 재료가 모자라면 `partial` 이하다. 빅테크(alphabet·amazon·apple·meta·microsoft·oracle)는 ① 마다 공동화 트리거를 하나씩 둔다(아래 트리거). 키 이름과 허용값은 `scripts/scorecard/schema.py` 의 lockin 검사가 원본이다.
- **④ (J2)** survival 입력 전부: `layers`(여섯 칸 `chip`·`server`·`platform`·`cloud`·`model`·`app` 각각 `sold`·`self`·`none`·`preparing`), `layer_evidence`(칸마다 확정 근거 ID 목록. `none` 이 아닌 칸은 반드시), `layer_triggers`(준비 중 칸마다 트리거 ID), `primary_layer`(판매 칸 가운데 외부 매출이 가장 큰 층), `non_ai_revenue_share`(0~1), `non_ai_share_basis`(어느 세그먼트를 AI 무관으로 셌는지와 계산), `non_ai_share_evidence`(근거 ID). 같은 층에 같은 사실이면 회사마다 같은 칸 값을 준다(체크리스트 Q03). 판단 칸에 칸별 이유를 적는다.
- **⑧ (J3, J2 뒤)** axes 입력 전부: `customer`·`commitment`·`supply`·`geopolitics` 각각 `{"status": confirmed|absent_disclosed|not_applicable|not_disclosed|not_found, …}`. 고객 `recognized_share`·`contract_share`·`dedicated_assets`, 약정 `multiple`·`payment_years`·`near_term_burden`, 공급 `rung`(0~−5)·`supplier_is_competitor`, 지정학 `rung`. 확인됨이면 그 축의 숫자나 칸이 필수다. J2 의 보유표에서 칩이나 클라우드가 `none` 인 회사는 공급 축을 0 으로 적을 수 없다(`work/judge/F4-<회사>.json` 을 읽는다). 비공개(발행사가 공개하지 않음)와 탐색 미완(우리가 못 찾음)을 섞지 않는다.
- **②③ (J4)** paths 입력 전부와 criteria 입력 전부(지난 판단과 같으면 비우고 reconfirm).
- **⑤⑦ (J5)** `A`·`H`, `funding_dependent_share`·`own_money_returns`(지난 판단과 같으면 비우고 reconfirm).

## 트리거

공동화 트리거(①)와 준비 중 칸의 트리거(④)는 새로 쓴다. 먼저 `triggers.json` 에 같은 조건의 관찰 중 트리거가 있는지 보고, 있으면 그 ID 를 쓴다. 없으면 `work/judge/triggers-<항목>.json` 에 `{"group": "J1", "new_triggers": [{"key": "<짧은 영문 키>", "company_id", "factors", "observation", "condition", "deadline", "source_ids": [], "evidence_ids": [], "status": "watching", "recheck": {"factors": [...], "what": "..."}}]}` 로 쓰고, 판단의 `layer_triggers` 에는 `"NEW:<key>"` 를 적는다. 조율자가 ID 를 붙여 바꾼다. 미래 점수를 적지 않는다.

## 출력

- 파일: `.agents/plans/v21-first-run-2026-10/work/judge/<F>-<company_id>.json`(모양은 REJUDGE-INSTRUCTIONS 5번). `cite` 에는 올릴·내릴 근거의 표지와 판정 재료(`layer_evidence`·`ai_*_evidence`·`non_ai_share_evidence`)가 가리키는 근거 ID 를 빠짐없이 적는다.
- 마지막 답변: 회사별 입력 요약표(입력과 계산될 점수 가늠, 직전 판단과 달라진 칸과 이유), 사건 교차표, 미확인으로 남긴 것, 경계 사례, 조율자가 더 확정해야 할 근거. ① 은 네 빅테크(alphabet·amazon·meta·microsoft)의 AI 수익화 몫 교차표, ④ 는 층마다 회사별 칸 값 교차표를 함께 싣는다.
- 판단 문장은 완결된 현재 상태 문장으로 쓴다. 규칙 버전·변경 표시·작업 번호·이전 판 참조("직전 실행에서는")를 쓰지 않는다. 이해상충을 이유로 멈추거나 되묻지 않는다. 투자 권유 표현을 쓰지 않는다.
