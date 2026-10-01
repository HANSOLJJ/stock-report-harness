---
name: score-collect
description: scorecard 실행의 근거 후보(뉴스·공시·가격)를 수집해 evidence.json 과 triggers.json 으로 선별한다. /score-collect <run_id> 로 사용하며 후보 수집과 선별만 하고 점수는 바꾸지 않는다.
---

# 채점 근거 수집 스킬

실행 하나의 근거 후보(뉴스·공시·가격)를 모으고, factor 와 관련 있는 것만 `evidence/evidence.json` 에 후보(`candidate`)로 올린다. 점수와 판단은 이 단계에서 바꾸지 않는다. 후보를 확정(`confirmed`)하는 것은 사람이며, 승인 페이지에서 한다.

```
collect → 후보 선별(evidence.json) → triggers.json → research
```

## 절차

1. `output/<run_id>/run.json` 이 있는지 확인한다. 없으면 중단하고 `/score-plan` 이나 `/score-extend` 로 실행 생성을 먼저 안내한다.
2. 후보를 수집한다. 결과는 `output/<run_id>/evidence/candidates.json` 에 쌓이고, 수집한 원문 캐시는 `data/<company_id>/`(gitignore)에 남는다.
   ```
   uv run --frozen python -X utf8 scripts/scorecard_cli.py collect <run_id> [--company a,b] [--kind news|filings|prices|all] [--since YYYY-MM-DD] [--forms 8-K,10-Q] [--locale en-US] [--from-file PATH] [--dry-run] [--take-lock]
   ```
   - `--company`: `run.companies` 가운데 일부만 수집한다(쉼표).
   - `--kind`: `news`, `filings`, `prices`, `all`. 공시는 형식 기본값이 `8-K,10-Q,10-K,20-F,6-K` 이고 `--forms` 로 바꾼다.
   - `--since`: 후보 창 시작일. 기본은 기준일(`as_of`)에서 180일 전이다.
   - `--from-file`: 네트워크 대신 파일을 읽는다. `--kind` 하나와 함께 쓴다.
   - `--dry-run`: 무엇을 가져올지만 확인한다.
   - 공시 수집(`--kind filings`)에는 `SEC_UA`(이름과 연락처를 담은 식별 문자열)가 필요하다. 사용자가 루트 `.env` 에 적거나 환경변수로 둔다. **영문으로 적어야 한다**(HTTP 머리글 제약이라 영문 밖 글자가 있으면 값을 보이지 않고 "SEC_UA 는 영문으로 적는다" 오류를 낸다). 뉴스 수집의 요청 식별자도 같은 검사를 거친다. 에이전트는 `.env` 를 만들거나 고치지 않는다. 비어 있거나 영문이 아니면 그 기업의 공시는 `failed` 로 남기고 나머지는 계속 돈다. 값을 저장소나 문서에 적지 않는다.
   - `--kind prices` 는 yfinance 로 ⑥ `price`·`market_cap` 관측을 `observations.json` 에 넣는다. EPS·컨센서스는 받지 않는다. 조회일이 종가일과 하루 넘게 다르면 벤더 시가총액을 쓰지 않고, ADR 시가총액은 벤더 값만 쓴다.
   - 종가가 NaN 인 날은 건너뛰고 기준일 이하의 **직전 확정 종가**와 그 날짜를 기록한다. 건너뛴 날짜는 수집 요약의 `skipped_nonfinite_close` 에 있으므로 보고에 옮긴다. 종가가 전부 NaN 이면 그 회사는 오류다.
   - 가격 실패는 **회사 단위**다. 조회·관측 생성·중복(같은 기업·지표·기준일)·검증이 한 회사에서 실패하면 그 회사만 `failed` 로 남고 나머지는 기록된다. 부분 실패 뒤 다시 돌리면 빠진 회사만 들어가고, 이미 기록된 회사는 `skipped_existing` 으로 표시되며 출처 항목에 새 티커 주소가 덧붙는다. 실패 회사를 조용히 다른 값으로 채우지 않는다.
   - 뉴스 질의는 `scorecard/companies.json` 의 `news_queries`(없으면 표시명과 티커)를 쓴다. `Meta`·`Oracle`·`Apple` 처럼 일반 단어와 겹치는 이름은 이 키로 질의를 좁혀 둔다(meta·oracle·apple 에 이미 있다). 질의가 넓어 엉뚱한 기사가 많으면 사용자에게 `news_queries` 를 좁히자고 제안한다.
   - 상장 12개사의 SEC CIK(`cik`)는 `companies.json` 에 기입돼 있다. 티커로 다시 확인하려면 `uv run --frozen python -X utf8 scripts/scorecard_cli.py resolve-cik [--company id] [--json]` 를 쓴다(`--apply` 는 레지스트리를 고치므로 사용자가 요청할 때만).
3. `candidates.json` 을 읽고 factor 와 관련 있는 후보만 `evidence/evidence.json` 에 `status: candidate` 로 선별한다.
   - 필수 필드: `evidence_id`(`EV-<company_id>-NNN`), `company_id`, `factors`, `kind`(news|filing), `source_id`(sources.json 에 등록된 것), `published_at_utc`, `title`, `excerpt`, `relevance`, `channel`(disclosure|press|company_statement|secondary), `conditional_impact`, `horizon`, `counter_evidence`, `unverified`, `change_vs_previous`.
   - `excerpt` 는 원문 그대로 600자 이하로 옮긴다. 요약하거나 고쳐 쓰지 않는다.
   - `relevance` 는 추론이므로 추론임을 표시한다.
   - `conditional_impact` 에는 점수 이동(`-3→-4`, `+2점`)을 적지 않는다. 사건이 미치는 조건부 영향을 말로 쓴다.
   - `published_at_utc` 가 `run.info_cutoff` 보다 늦은 후보는 올리지 않는다.
   - **factor 배정 기준.** 정의는 `docs/scorecard/rules/AI기업_채점규칙_v1.7.md` 의 표와 별표에 있다. 2026-10-01 평가 표본에서 실제로 틀렸던 자리를 먼저 본다(예시는 `tests/fixtures/evidence/labeling-2026-10.csv`).
     - 조달은 ⑤ 동맹이 아니다. 칩·설계 도구·전력·컴퓨트를 사는 계약은 별표 H 의 조달이다. 같은 계약을 파는 쪽에서 보면, 고객이 조달한 돈으로 내는 매출이라 ⑦ 순환금융, 고객 집중이 크면 ⑧ 의 재료가 된다.
     - 규제 조사·소송·평결은 ⑤ 적대 등급의 재료다(별표 C·G). 사업 구조를 건드리지 않으면 비용형이고, 판매 금지처럼 구조를 건드려야 구조형이다.
     - 계획·발표·예정·인사·조직 개편은 별표 D 에 따라 점수 근거가 아니다. 출하·매출·채택처럼 지금 측정되는 것만 근거로 올리고, 계획은 필요하면 트리거로 적는다.
     - 신모델·신제품의 벤더 발표는 ② 를 다시 볼 계기일 뿐이다. 벤더 발표 벤치마크는 방증이고 독립 측정(AA·ARC-AGI 등)이 1차다. 이런 근거의 확신을 '높음' 으로 두지 않는다.
     - ① 은 회사의 모든 채널 중 가장 강한 락인으로 매긴다(별표 A). 이미 강한 채널이 있는 회사의 작은 신규 앱 지표는 ① 을 움직이지 못한다. 후발 서비스가 선두보다 빨리 크는 소식은 ② 패러다임 적응이나 ③ 후발 가속도의 재료일 수 있다. 내려받기 수는 사용량이 아니라는 한계를 `unverified` 에 적는다.
     - ④ 는 출하와 사업 부문만 센다. 자체 칩은 출하가 확인될 때, 비AI 사업은 매출이나 배치가 생길 때 근거가 된다. 기존 제품군 안의 기능 추가나 매각설 부인은 ④ 를 바꾸지 않는다.
     - 흑자 기업의 매출 공시는 ⑨ 보다 ⑥ 매출 성장의 입력이다. 비상장사의 ARR 보도는 ⑥ 매출 분모의 근거로만 쓴다. 확정 미인출 여신은 ⑨ 완충의 직접 입력이다.
     - 이번 점수를 바꾸지 못하는 근거라도 factor 배정이 맞으면 올린다(사용자 결정 2026-10-01). 점수가 그대로라는 판단은 `conditional_impact` 에 말로 적는다.
     - 올리지 않는 것: 시세·옵션·지분 매입 자동 생성 페이지, 경영진 개인 일화, 다른 회사를 잘못 귀속한 기사(티커 혼동), 회사 이름을 도용한 제3자 사건. 질의 오염이 반복되면 `news_queries` 를 좁히자고 제안한다.
     - 합병·분할처럼 채점 단위(scope)를 바꾸는 사건은 factor 근거가 아니다. 완료 보고에 따로 적어 사용자가 기업 등록부를 다시 보게 한다.
     - 제목과 요약만 보고 판정했으면 그 사실을 `unverified` 에 적고, 원문에 따라 갈릴 수 있는 건은 확신을 낮춘다.
   - **문장 작성 규칙.** `relevance`·`conditional_impact`·`counter_evidence`·트리거 문장은 사람이 승인 페이지에서 규칙 문서를 열지 않고 읽어 확정 여부를 가를 수 있게 쓴다(사용자 요청 2026-10-01).
     - 규칙 용어를 코드로만 쓰지 않는다. 별표(A~J), ⑥ 의 잣대(P1 PER·P2 EV/매출·P3 매출 성장·P4 입력 신뢰도), ⑨ 의 게이트(게이트 1 본업 이익·게이트 2 최근 1년 현금흐름·게이트 3 버티는 기간·게이트 4 약정 커버리지), 체크리스트 번호, 긴장 번호는 처음 쓸 때 뜻을 괄호로 붙인다. 예: "⑨ 게이트 2(최근 1년 잉여현금흐름이 마이너스인가)", "별표 H(돈 주고 사는 관계는 동맹이 아니다)".
     - 판단 ID(`alibaba.F9`)를 쓰지 않고 "알리바바 ⑨ 판단" 처럼 쓴다. 그 판단의 지금 값도 말로 적는다. 예: "알리바바 ⑤ 판단은 적대 등급 -1(비용형)이다".
     - `conditional_impact` 는 판단 단위의 결론으로 시작한다. **"지금은 유지:"**(이 근거로는 어느 판단도 바꾸지 않음, 근거 문장만 보강) 또는 **"재검토:"**(어느 factor 의 어떤 입력을 어떤 방향으로 다시 볼지)로 시작하고, 그 뒤에 조건을 쓴다. "~의 재료다", "~와 닿는다" 로 끝내지 않는다.
     - `factors` 에는 이 근거로 실제로 다시 보거나 근거 문장을 보강할 factor 만 넣는다. 관련이 "닿을 수 있다" 수준인 factor 는 넣지 않고, 이중 계상이 걱정되면 어느 factor 에만 쓰는지 정해서 그 하나만 넣는다.
4. 재채점 조건은 `output/<run_id>/triggers.json` 에 `status: watching` 으로 적는다. `condition`·`deadline`·`recheck` 를 채우고, 미래 점수를 저장하지 않는다(C-14).
5. 실행한다: `uv run --frozen python -X utf8 scripts/scorecard_cli.py research <run_id>`. 이 단계는 `/score-research` 가 이어받는다.

## 사람이 하는 일

선별한 근거는 후보 상태로 남는다. 사람이 `node server.js --approvals` 로 승인 페이지를 띄워 근거를 확정하거나 거부한다. 에이전트는 `confirm` 으로 근거를 확정하지 않는다. 사용자가 확정할 ID 를 지정해 지시한 경우에만 그 ID 로 실행한다. 확정하면 해시가 바뀌므로 `research → calculate → draft → review` 를 다시 돌린다.

## 제약

- 1차 출처를 우선한다. 기업 IR, 공식 뉴스룸, 공시, 거래소·중앙은행 데이터를 먼저 쓰고, 이벤트와 리스크는 공신력 있는 매체로 보완한다.
- URL 을 조작하지 않는다. URL 이 없으면 `url: null` 로 두고, 검색·제공자 폴백 URL 을 쓴 경우 `url_is_fallback: true` 를 표시한다.
- 수집이 차단되거나 실패하면 누락된 자료를 정확히 명시한다. 조용히 다른 자료·기간·지표로 대체하지 않는다.
- 사실과 추론을 분리한다. 원문에서 확인한 내용은 사실로, 우리가 해석한 내용은 추론으로 표시한다.
- 사람이 `confirmed` 로 올리기 전까지 `status: new` 판단이 `candidate` 근거를 인용하지 않는다.
- `not_disclosed`(발행사가 공시하지 않음을 확인)와 `unverified`(우리가 찾지 못함)를 구분한다. 어느 쪽인지 모르면 `unverified` 로 둔다.
- 기사 본문을 가져오지 않는다. 제목·요약·URL 만 다룬다.
- 다른 기업의 점수를 근거로 인용하지 않는다.

## 완료 보고

`candidates.json` 후보 수, `evidence.json` 에 올린 근거 수, `triggers.json` 항목 수, 수집 실패·누락 목록, 다음 명령 `/score-research <run_id>`.
