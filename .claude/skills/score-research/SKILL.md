---
name: score-research
description: scorecard 실행의 원자료(observations)·판단(judgments)·출처를 엄격 검증하고 output/<run_id>/research.md 를 생성한다. /score-collect 뒤 /score-research <run_id> 로 사용한다.
---

# 채점 리서치 스킬

실행 입력을 검증하고 `output/<run_id>/research.md` 를 만든다. 새 자료를 넣는 단계이기도 하다. 순서는 `collect` → 후보 선별 → `research` 이다.

## 절차

1. `output/<run_id>/plan.md` 와 `output/<run_id>/run.json` 이 있는지 확인한다. 근거 후보가 필요하면 `/score-collect <run_id>` 를 먼저 수행했는지 확인한다.
2. 새 원자료가 있으면 `output/<run_id>/observations.json` 에 추가한다. 필수: `metric`(카탈로그), `value`, `unit`, `as_of`, `kind`, `source_id`(sources.json 에 등록), `status`(새 자료는 `verified`), `basis`(주가는 `currency`·`share_basis`, 매출·이익 같은 기간 지표는 `period_basis`. ⑥ 의 트랙이 이 값으로 정해진다).
   - 수집 실패는 `collection_failed`, 확인된 비공개는 `not_disclosed`, 기간·범위가 다르면 `incompatible_basis`. 다른 기간·지표로 조용히 대체하지 않는다.
   - 출처 없는 URL 을 만들지 않는다. URL 이 없으면 `url: null`.
3. 새 정성 판정이 있으면 `judgments.json` 을 손으로 고치지 않는다. **에이전트는 `propose` 로 판단 변경 제안을 쓰고**, 근거를 원문과 대조한 뒤 `proposal` 로 반영·거부한다(2026-10-01, 2026-10-07 부터 에이전트가 반영한다). 제안은 확정 근거만 `--cite` 로 인용하고, 근거는 세 칸으로 준다(2026-10-07, `guide.md` 5.6). 판정은 `--evidence`, 올릴 근거는 `--up`, 내릴 근거는 `--down` 이고 각각 반영 뒤 전체 목록이다. 규칙 v1.9 이상 실행은 세 칸이 아니면 반영이 막힌다. 올릴·내릴 근거의 줄마다 끝에 원문 근거 표지 `[EV-…]` 를 달고, 그 근거는 확정·URL·본문 발췌·`locator` 를 갖춘다. 원문을 못 찾은 사실은 판정 칸에 "미확인"으로 둔다(2026-10-07, `guide.md` 5.7). `uv run --frozen python -X utf8 scripts/scorecard_cli.py propose <run_id> --company <id> --factor F1..F9 (--set key=value … | --evidence "판정" … --up "올릴 근거" … --down "내릴 근거" … | --json 파일) --reason "…" --cite EV-…`. 사람이 직접 고칠 때는 `judge` 명령을 쓴다. 명령이 형식을 검증하고, `status: new`·검토자·검토일을 쓰고, 이전 값을 `revision_history` 에 남긴다. F3 는 criteria, F5 는 grade, F7 은 matrix, F9 는 gate_inputs 를 고친다. F1 은 규칙 v2.0 이상 실행에서 lockin(채널·네 질문·지속성 할인·AI 수익화), v1.9 이하 실행에서 점수와 근거를, F2 는 규칙 v2.0 이상 실행에서 paths(세 경로·세대 격차 개월 수·독립 측정)를 고친다(2026-10-08). F4·F8 은 규칙 v2.0 이하 실행에서 점수와 근거, 규칙 v2.1 실행에서 판정 재료를 고친다. 점수 칸은 규칙이 계산하므로 고칠 수 없다.
   `uv run --frozen python -X utf8 scripts/scorecard_cli.py judge <run_id> --company <id> --factor F1..F9 (--set key=value … | --evidence "문장" … | --json 파일) --reason "…" --by <이름> [--take-lock]`
   - 인자는 `--help` 로 확인한다. 고친 뒤에는 `/score-research <run_id>` 부터 다시 돈다. 사람이 승인 페이지에서 판단을 고친 경우도 같다.
   - `status: new` 판단은 `evidence_ids` 로 **confirmed 근거만** 인용한다. candidate 근거를 인용하면 교차 참조 검증이 실패한다. 아직 확정되지 않은 후보는 인용하지 말고, 원문을 확인해 `confirm` 으로 확정한 뒤 인용한다.
   - **제목만 보고 넘기지 않는다(2026-10-12 사용자 지시).** 후보와 수집 뉴스의 URL 은 Google News 중계 주소라 그대로 열면 원문으로 넘어가지 않는다. `scorecard_cli.py resolve-urls --url <중계 주소>` 로 원문 주소를 얻어 본문을 읽고 발췌·`locator` 를 채운다. 근거 출처를 한꺼번에 고칠 때는 `resolve-urls <run_id>` 를 쓴다. "제목만 확인"은 미확인 사유가 아니다. 유료 기사라 본문이 막혔을 때만 그 사실을 판정 칸에 적고 미확인으로 둔다. 규칙 v2.0 이상 실행은 발췌가 제목뿐이거나 출처가 중계 주소인 근거를 `confirm` 이 받지 않고, 이어받은 것까지 `research` 가 막으며, '제목만' 사유를 쓴 판단 문장은 `judge`·`proposal` 이 받지 않는다. 10월 재실행에서 이전 실행에 제목만으로 확정된 근거 29건이 이어졌고, OpenAI ③ 이 연환산 매출 $70B 기사를 "제목만 확인"으로 빼 두었다.
   - **규칙 v2.1 판정 재료(2026-10-12).** 중첩 입력이라 승인 페이지 입력란이 없고 `judge --json`·`propose --json` 으로만 준다.
     - ① AI 수익화 '예' 는 `ai_monetized_channel`(consumer·work·trade, 실질 채널)·`ai_monetized_measure`(customers·seats·revenue)·`ai_monetized_share`(0~1, 과반 > 0.5)·`ai_monetized_period`·`ai_separate_billing_evidence`·`ai_price_uplift_evidence`(확정 EV 목록)를 모두 적어야 한다. 몫은 공시 숫자로 재고(예: Copilot 유료 좌석 ÷ 상업용 유료 좌석), 일부면 '부분' 이다. 광고 효율·내부 비용 절감은 별도 과금이 아니다.
     - ④ `survival`: `layers`(chip·server·platform·cloud·model·app 각각 sold·self·none·preparing·unknown), `primary_layer`(판매 칸 중 외부 매출 최대), `non_ai_revenue_share`(AI 와 무관한 최종 수요의 매출 몫, 세그먼트 공시로), 선택으로 `layer_triggers`(준비 중 칸은 필수, TRG-NNN)·`layer_evidence`(칸별 EV 목록)·`non_ai_share_basis`·`non_ai_share_evidence`. 모델 층은 모델 사용 자체(API·범용 비서 구독), 응용 층은 특정 일을 끝내 주는 제품이다. 칩 칸은 설계이고 파운드리 의존은 ⑧ 에서 본다.
     - ⑧ `axes`: `customer`·`commitment`·`supply`·`geopolitics` 네 축마다 `status`(confirmed·absent_disclosed·not_applicable·not_disclosed·not_found)와, 확인됨이면 고객 `recognized_share`·`contract_share`·`dedicated_assets`, 약정 `multiple`(선택 `payment_years`·`near_term_burden`), 공급 `rung`(0~−5)·`supplier_is_competitor`, 지정학 `rung`. 부재 확인은 "10% 이상 고객 없음"처럼 그 조건이 없다고 공시한 경우이고, 공개하지 않은 것(비공개)·못 찾은 것(탐색 미완)과 섞지 않는다. ④ 보유표에서 칩·클라우드가 '없음'이면 공급 축을 0 으로 적을 수 없다.
     - 판단 세션은 Opus(노력 high)로 띄운다(AGENTS.md 「서브에이전트 모델」).
   - **규칙 v3.0 판단 세션(2026-10-14).** ①②③ 은 층·사업마다, ④⑤ 는 회사마다 한 건이다. ①②③ 의 무게와 ① 사업의 매출 몫이 ④ 매출 줄에서 나오므로 **④ → ②③ → ① → ⑤** 순서로 매긴다. 모두 `judge --json`·`propose --json` 으로 주고, ①②③ 은 `--business`·`--layer` 로 판단을 가리킨다(없으면 새로 만든다). 입력 모양은 `structure.md` 2절 「판단 입력(규칙 v3.0)」, 기준은 `rules.md` 2.10·2.11·3절이다.
     1. ④ `holdings`: 열한 층 칸(판매·자체 사용·없음·준비 중·미확인)과 칸별 근거. AI 사슬 조건 층(전력·데이터 플랫폼·사용자 플랫폼·기기)의 판매·자체 사용 칸은 `ai_chain`, 준비 중 칸은 트리거를 단다. 매출 줄은 공시된 가장 잘게 나눈 매출 표(최근 4개 분기 합)를 그 매출이 가장 많이 속한 층에 통째로 붙이고 어림으로 쪼개지 않는다. 구성 금액이 공시되지 않아 어느 층이 가장 많은지 확인할 수 없으면 사업 설명으로 고르고 판정 칸에 미확인으로 적는다. 열한 층에 들지 않는 사업은 `outside`, 로켓 발사는 `rocket_launch` 다. 줄마다 AI 무관 여부(`non_ai`)를 누가 왜 돈을 내는지로 가른다. 기업용 소프트웨어는 AI 무관이고, 전력 층 매출은 AI 데이터센터가 그 줄 고객의 과반일 때만 AI 수요다. AI 무관 부문 이익률을 공시하지 않으면 회사 전체 영업이익률을 쓰고 `non_ai_margin_source: company` 로 적는다.
     2. ②③ `layer_paths`·`layer_cp`: 매출 줄이 붙은 판매 층마다 한 건이다. 매출 몫 0 판매 층은 매기지 않는다(2026-10-15 사용자 결정, ④ 보유표로만 센다). ② 는 벤치마크가 없는 층(규칙 JSON `no_benchmark_layers`, 개발 플랫폼 포함)에 `leap` 을 적지 않고, 표준은 그 규격을 지원하는 주요 제품이 속한 층에서 세며(2026-10-15 사용자 결정, 예: MCP 는 모델 층), 규격마다 가장 최근에 새로 지원한 주요 회사와 그 날짜를 적는다(2년 창은 프로그램이 가른다). 출시했지만 채택 지표가 없으면 패러다임 적응은 `unknown` 이다. ③ 의 상대는 층을 가리지 않는다. 상대가 돈을 받는 것을 내가 공짜나 헐값으로 주면 상대다. 승부가 끝났거나 처음부터 그런 상대가 없어 지금 시장에 없으면 `counterparty_present: no` 다(상대 이름을 지어 넣고 same·copied 로 적지 않는다). 모방 불가능성은 나 말고 같은 방식을 이미 쓰는 회사 수를 `imitators` 에 적는다. 1 곳(양분)이면 최고 conflict_pending(5), 2 곳 이상이면 copied(0)이고, 상대와 경쟁사를 가르지 않는다(2026-10-15 사용자 결정, 스키마가 막는다). 가속도는 같은 정의의 두 기간 성장 배수(기본 1년 전 대비, 없으면 같은 길이로 이어진 두 기간)를 적고, 회사가 공시로 밝힌 일회성만 뺀다. 두 기간의 길이 차이가 20% 안이면 같은 길이로 보고 지난 배수를 이번 기간 길이로 환산한다(지난 배수^(이번 일수 ÷ 지난 일수)). 두 기간의 날짜와 일수를 판정 칸에 적는다.
     3. ① `business`: 공시 매출 줄을 사업으로 나눈다. 같은 층이라도 고객 유형(소비자·업무·거래)이 다르면 나누고, 하나를 떠나면 다른 서비스의 편익도 잃는다는 근거가 있을 때만 묶는다(`bundle_reason`). 판매 층의 매출 줄은 빠짐없이 한 사업에만 붙는다. A~C 는 규칙 사다리 칸 이름으로 적고, 매출 10% 이상 고객의 자체 대체품도 C 의 대체재로 센다. B 가격 실측은 가격 인상·유지 뒤 최근 2개 분기 매출이 모두 1년 전 같은 분기보다 늘었는지를 `pricing_growth_quarters`·`pricing_explained` 로 받친다(2026-10-15 사용자 결정, 최근 분기 보고서 둘이면 잰다).
     4. ⑤ `alliance`: 관계마다 채우는 부분(`qualifies`)을 적으면 어느 부분에 넣을지는 프로그램이 정한다. 정부 계약은 그 회사만 받은 계약만 상업 동맹으로 적고, 같은 사업에서 경쟁사도 함께 받은 계약은 적지 않는다(2026-10-15 사용자 결정). 적대는 전선 목록(비용형·구조형, 진행 중·끝남)으로 적고, 금액은 쓰지 않는다.
     5. ⑦⑧ 은 판정 재료를 다시 읽어 재확인하고, 판정 칸에 옛 점수 척도(×4 전) 문장이 남았으면 v3.0 점수로 문장 전체를 다시 쓴다. 준비 중 칸의 트리거는 `triggers.json` 에 직접 쓴다(collect 다음 단계 안내와 같은 경로).
     - 확인하지 못한 점수 부분은 `unknown` 으로 적는다. 프로그램이 만점의 40% 와 미확인 표시를 준다. 0 이나 낮은 칸으로 적어 대신하지 않고, 확인할 수 있는 것을 `unknown` 으로 두지 않는다. 매출 금액·보유표 칸처럼 무게를 내는 재료가 `unknown` 이면 판정 대기가 된다.
     - 같은 층의 경쟁사는 같은 잣대로 나란히 매긴다. 판단 전에 사건 교차표를 만든다(AGENTS.md 「금지·주의」).
4. 실행한다: `uv run --frozen python -X utf8 scripts/scorecard_cli.py research <run_id> [--no-register] [--take-lock]`.
   - 기본 동작은 `evidence.json` 이 인용한 후보의 출처를 `sources.json` 에 자동 등록하는 것이다. `--no-register` 는 이 등록을 하지 않는다. 등록 없이 검증만 보고 싶을 때만 쓴다.
   - 스키마 오류(`[FAIL]`)가 나면 입력을 고친다. 임의 해석으로 통과시키지 않는다.
5. `output/<run_id>/research.md` 의 "미결 항목" 을 읽고 unknown 입력·자료 대기·규칙 결정을 보고한다.

## 제약

- 승계(carried) 판단을 새로 검증된 것처럼 바꾸지 않는다. 재검토했으면 `status: new`, `reviewed_at` 갱신.
- 규칙 v2.0 이상 정기 실행에는 승계 판단이 없다. 정성 판단 일곱 항목(①②③④⑤⑦⑧)을 모든 기업에 대해 이번 실행의 근거로 새로 매기고, 점수가 같으면 다시 읽은 근거를 `reconfirmed` 에 남긴다. 승계는 기업 추가 실행의 기존 기업에만 쓴다(2026-10-08, `rules.md` 2.9).
- LLM 이 제안한 판정은 사람이 확인하기 전까지 `status: new` 로 확정하지 않는다(evidence 에 "후보" 표시).
- `not_disclosed`(발행사가 공시하지 않음을 확인)와 `unverified`(우리가 찾지 못함)를 구분한다. 어느 쪽인지 모르면 `unverified` 로 둔다.

## 완료 보고

research 경로, 관측·판단 건수, 미결 항목, 다음 명령 `/score-calculate <run_id>`.
