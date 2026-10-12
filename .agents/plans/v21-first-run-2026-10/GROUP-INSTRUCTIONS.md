# 회사 묶음 작업 지시서 (2026-10 규칙 v2.1 첫 실행)

실행 `ai-scorecard-2026-10-v21`(기준일·정보 마감 2026-10-12, 가격 2026-10-09 종가, 규칙 v2.1)은 직전 실행 `ai-scorecard-2026-10-recheck` 와 사실이 같고 규칙만 v2.1 로 바뀐 실행이다. v2.1 은 ①·④·⑧ 의 판정 재료를 새로 요구한다. 이 묶음은 맡은 회사에 대해 **판정에 쓸 사실을 원문에서 확인해 근거와 관측으로 낸다. 판정(칸 값·등급·점수)은 하지 않는다** — 판단 세션이 한다.

**실행 폴더 `output/ai-scorecard-2026-10-v21/` 의 파일은 읽기만 하고 쓰지 않는다.** 산출물은 `.agents/plans/v21-first-run-2026-10/work/out-<묶음>.json` 하나다. `confirm`·`judge`·`propose`·`research`·`collect` CLI 를 부르지 않는다(실행 잠금이 충돌한다). `sec-get` 과 `resolve-urls --url` 은 써도 된다.

## 읽을 것

- `AGENTS.md` 「원자료 조사 규율」·「금지·주의」, `.claude/skills/score-collect/SKILL.md`(근거 필수 키, 문장 작성 규칙, 국면 지표 수동 관측), `docs/scorecard/rules.md` ①(AI 수익화 '예' 의 두 조건), ④(층 여섯의 정의, 칸 값, AI 무관 매출 몫), ⑧(네 축과 칸 정하는 법), 2.6·2.7(모르는 값·출처 등급).
- 실행 파일: `evidence/evidence.json`(확정 근거 817건 — **이미 있는 사실을 다시 올리지 않는다.** 같은 사실이 있으면 그 ID 를 보고에 적는다), `judgments.json`(직전 판단 문장. ①④⑧ 은 이전 규칙 형식이라 어떤 사실을 썼는지만 참고한다), `observations.json`, `sources.json`.
- 정보 마감은 2026-10-12 이다. 그 뒤 자료는 쓰지 않는다.

## 원문 확인

- 공시는 `uv run --frozen python -X utf8 scripts/scorecard_cli.py sec-get <SEC 주소>` 로 받는다. SEC 요청이나 User-Agent 를 직접 만들지 않는다. 받은 파일은 `data/_sec/docs/` 에 있다.
- 뉴스 근거의 URL 이 Google News 중계 주소면 `scorecard_cli.py resolve-urls --url "<주소>"` 로 원문 주소를 얻어 연다. 유료 기사로 막히면 같은 사실을 전한 열리는 기사나 회사 발표를 찾는다. 제목만 본 사실은 근거로 내지 않는다.
- 근거 항목의 `excerpt` 는 본문 그대로 600자 이하이고 제목과 달라야 하며, `locator`(공시는 항목·주석 번호·표 이름, 기사는 몇째 문단)를 적는다. 본문을 연 근거만 `"verified_original": true` 다.

## 해야 할 일 (맡은 회사마다)

1. **④ 층별 보유표의 칸 근거.** 여섯 층(칩 · 서버·네트워크 · 소프트웨어 플랫폼 · 클라우드 · 모델 · 응용)마다 이 회사가 그 층을 **남에게 팔아 돈을 버는지(판매), 대규모로 자기만 쓰는지(자체 사용), 남에게 사 오는지(없음), 돈이 나간 실행된 투자인데 매출이 0 인지(준비 중)** 를 가를 사실을 찾는다. 출하·실제 배포·매출 공시가 근거이고, 계획·발표는 근거가 아니다(준비 중은 확정 계약·건설 착수·인수 종결까지). 모델 층과 응용 층은 고객이 무엇에 돈을 내는지로 가른다(모델 = API 토큰·범용 비서 구독, 응용 = 특정 일을 끝내 주는 제품). 층마다 기존 근거가 있으면 그 ID 를, 없으면 새 근거를 낸다. 특히 **서버·네트워크와 소프트웨어 플랫폼 두 층은 기존 근거가 거의 없다.**
2. **④ AI 무관 매출 몫.** 세그먼트 공시(10-K·20-F 세그먼트 주석, 비상장은 회사 발표·2차 보도)에서 AI 와 무관한 최종 수요(광고, 소비자 기기·구독, 리테일, 자동차, 발사 등)에서 나오는 매출과 회사 전체 매출을 기간과 함께 찾는다. AI 설비투자(칩·AI 컴퓨트)와 AI 서비스(모델 API·AI 구독)는 AI 수요다. 어느 세그먼트를 AI 무관으로 볼지는 판단 세션이 정하므로 세그먼트별 숫자를 빠짐없이 낸다. **주 레이어**(판매 칸 가운데 외부 매출이 가장 큰 층)를 가를 세그먼트 매출도 함께 낸다.
3. **① AI 수익화 재료.** 이 회사의 가장 강한 채널(직전 ① 판단 문장 참고)에서 (가) 고객·좌석·매출 가운데 AI 에 따로 돈을 내는 몫을 잴 **공시 숫자**(분자·분모·기간. 예: Copilot 유료 좌석 ÷ 상업용 좌석)와 (나) AI 로 그 채널의 가격·단가를 올렸다는 **공시나 회사 1차 발표**(정가 인상 공지 등)를 찾는다. 없으면 없다는 사실과 찾아본 범위를 보고에 적는다(미확인과 회사 미공시를 가른다).
4. **⑧ 네 축 재료.** 고객 축: 10-K 의 10% 이상 고객 비중(인식 매출), 계약액이 인식 매출보다 큰 고객이면 그 고객의 연환산 계약액. 약정 축: 아직 개시되지 않은 리스 + 해지할 수 없거나 고정·보장된 구매 약정의 합(공시 주석의 표와 쪽), 지급 기간, 가까운 12~24개월 부담. 보증·조건부 구매·MOU 는 따로 적는다(⑦ 소관). 공급 축: 컴퓨트·칩·공정·OS·모델 공급자와 그 약정, 공급자가 곧 경쟁자인가. 지정학 축: 한 나라나 정부에 걸린 위험(대만 생산 집중, 수출 통제). 고객 집중은 공개 제출본 공시나 회사 1차 발표로만 낸다. 유출 문서·초안의 수치는 "보도가 있다" 는 사실로만 적는다.

## 관측 (묶음별)

관측 항목은 `company_id`, `metric`, `value`, `unit`, `as_of`, `kind`, `source_id`, `status: verified`, `raw`(원문 발췌), `note`(자리), 흐름 지표는 `period{start,end}`, 필요하면 `basis`. 출처는 `sources` 에 넣는다(공시는 SEC 주소). 값이 없으면 등록하지 않고 보고에 이유를 적는다(0 으로 채우지 않는다).

- **A (nvidia·tsmc·apple):** NVIDIA 공급자 지원 셋 — `supplier_guarantees`(고객의 설비·임차·차입에 대한 보증 한도), `supplier_customer_investments`(고객 회사에 대한 출자 잔액), `supplier_capacity_buyback`(고객의 클라우드 용량을 되사는 다년 사용 약정 잔액). 기준일 전 마지막 10-Q(회계 2027 2분기, 2026-07-26 끝)의 주석에서 그 분기 말 `as_of` 로 적는다. 셋 중 못 찾은 것은 비워 둔다. TSMC `ocf_ttm`: 기존 `tsmc.fcf_ttm` 관측과 같은 출처·기간·환산으로(같은 basis 의 영업현금흐름 값) 등록한다.
- **B (alphabet·amazon·microsoft):** `equity_investment_gains_ttm`(지분증권 평가·처분 손익, 최근 1년, 세전) — Alphabet 은 `us-gaap:EquitySecuritiesFvNiGainLoss` 네 분기 합, Amazon 은 10-Q '기타 영업외 손익' 주석 표의 지분 관련 줄(시장성 지분증권 평가, 비상장 지분 상향 조정 등)을 네 분기 합으로. `basis.components` 에 서로 겹치지 않는 구성(태그나 표 줄 이름, 분기별 값, accession)을 적고, 합계를 주석 표와 대조한 사실을 `basis.reconciliation` 에 적는다. Microsoft 는 해당 줄이 없으면 등록하지 않는다. 클라우드 세그먼트 분기 매출·영업이익 — `cloud_segment_revenue_quarterly`·`cloud_segment_operating_income_quarterly` 를 Amazon `AWS`, Alphabet `Google Cloud`, Microsoft `Intelligent Cloud` 로 2025년 3분기~2026년 2분기(Microsoft 는 그에 해당하는 회계 분기) 넷씩, `period` 와 `basis.segment`(이 이름 그대로)를 붙여 낸다.
- **C (meta·oracle·palantir):** Meta 장부 밖 설비 잔존가치 보증 `residual_value_guarantee`(특수목적법인 데이터센터의 최대 노출, 10-Q 주석). Oracle·Palantir 는 해당이 있으면.
- **D (anthropic·openai):** 비상장 보정 매출 `revenue_ttm`·`revenue_ttm_prior`(실측 최근 1년 매출과 그 직전 1년. ARR·런레이트가 아니다). 두 회사에 **같은 등급의 근거**를 쓰고 `note` 에 등급(회사 1차 발표 > 독립 집계 > 2차 보도)을 적는다. 같은 정의로 두 값을 맞출 수 없으면 등록하지 말고 후보 값과 이유를 보고한다. 토큰 단가 지수 — Silicon Data LLM Token Expenditure Index 공개 페이지(https://www.silicondata.com/products/silicon-index/llm-token-expenditure-index)의 값과 날짜를 `company_id: "_market"`, `metric: token_price_index`, `unit: USD` 로. `basis.segment` 는 페이지가 밝힌 구간(broad·frontier·open)만 쓰고, 밝히지 않으면 등록하지 말고 그 사실을 보고한다.
- **E (alibaba·tesla·spacex-xai):** Alibaba `equity_investment_gains_ttm`(20-F·6-K 주석, 다른 Alibaba 관측과 같은 USD 환산과 기간)과 `ocf_ttm`(기존 `alibaba.fcf_ttm` 관측과 같은 출처·기간·환산). SpaceX `ocf_ttm`(기존 `spacex-xai.fcf_ttm` 관측 basis 의 성분과 같은 출처로).

## 출력

`work/out-<묶음>.json` 에 `{"group", "sources", "evidence", "observations", "layer_map", "notes"}`.
- `evidence`: 새 근거(필수 키는 score-collect 스킬. `factors` 는 실제로 쓸 항목만, `conditional_impact` 는 "지금은 유지:" 나 "재검토:" 로 시작, `evidence_id` 는 적지 않는다).
- `layer_map`: 회사마다 `{"company_id", "layers": {"chip": {"facts": "그 층에 대해 확인한 사실 한두 문장", "evidence": ["EV-…" 기존 ID 나 "new:<새 근거 제목>"]}, …여섯 층}, "segments": [{"name", "revenue", "period", "source"}], "monetization": {...}, "f8": {...}}`. 판정을 적지 않고 사실과 근거 위치만 적는다.
- `notes`: 못 찾은 것과 찾아본 범위, 판단 세션에 알려야 할 사실.

마지막 답변에는 회사별로 올린 새 근거 수, 층마다 근거가 있는지(없으면 찾아본 범위), 등록한 관측과 못 찾은 것을 적는다. 문장은 완결된 현재 상태 문장으로 쓰고 규칙 버전·작업 번호·이전 판 참조를 쓰지 않는다. 이해상충을 이유로 멈추거나 되묻지 않는다. 투자 권유 표현(매수·매도 등)을 쓰지 않는다.
