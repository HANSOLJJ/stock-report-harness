# AI 기업 분석 framework — 구조 확장 지침

- 작성일 2026-09-08. `design-guideline.md`(도메인 명세)의 짝이다. 남은 작업은 루트 `TODO.md` 에 모은다. 이 문서는 요구 ID(D·F·Q·T·C)를 실제 모듈·파일·테스트에 연결한다.
- 기준 커밋 `0df7d6e`, 브랜치 `HANSOLJJ/worker`. 원본 규칙·계획 문서는 읽기 전용 참고 자료이고, git 이 6개 파일을 추적한다. 2026-10-01 에 옛 `AI_company_analysis_factor/` 에서 규칙 문서 둘은 `docs/scorecard/rules/`, 원천 자료 넷은 `docs/scorecard/source/` 로 옮겼다(바이트 그대로). SHA-256 은 design-guideline 2.1절과 일치한다.

## 1. 유형 분기와 공통 진입점

| 항목 | stock_report (기존) | ai_scorecard (추가) |
|---|---|---|
| 판별 | `output/<run_id>/plan.md` frontmatter `report_type` 없음 | `report_type: ai_scorecard`, run_id 는 `ai-scorecard-` 접두 |
| 판별 코드 | 판별 함수 `report_type_for()` 는 제거됐다. `report_type` 필드는 `scripts/report_contract_lib.py` 의 frontmatter 키 목록에만 남아 있다 | 동일 |
| 검증 | `validate_report_contract.validate_contract` 기존 로직 그대로 | 같은 함수가 `scorecard.validate.validate_scorecard` 로 위임 (`ValidationResult` 공유) |
| 빌드 | `build_report.build_report` 기존 로직 그대로 | 같은 함수가 `scorecard.render_html.build_scorecard` 로 위임. CLI `uv run --frozen python -X utf8 scripts/build_report.py <run_id>` 동일 |
| hero 이미지·뉴스 100건 | 필수 | 요구하지 않음 |
| draft 숫자 마커 `[S1]` | 필수 | 생성물이라 면제. 대신 draft frontmatter `results_hash` 가 results.json 과 결속되고 검증기가 순위표 행을 대조 |
| 투자 권유 표현 차단 | `guard.py` 의 `forbid_financial_advice` | 동일 적용 (`draft.md`·`judgments.json`·`evidence/*.json`) |
| 가격 공급 | yfinance | `collect --kind prices` 가 실행 원자료(observations.json)에 넣는다. build 중 재수집 없음 (D-02, C-21) |

## 2. 파일 소유권과 저장 스키마

| 경로 | 소유 | 추적 | 내용 |
|---|---|---|---|
| `scorecard/rules/v1.5.json` | 규칙 담당 | git | factor 모드·범위, ⑥ 구간, ⑨ 게이트 정책, ③ 사다리, ⑤ 산식, ⑦ 매트릭스, 체크리스트 Q01~Q23, 결정 C-01~C-22 상태·선택지 |
| `scorecard/companies.json` | 통합 담당 | git | 안정 company_id, 표시명·별칭, 유형, 상장, 티커, share_basis, adr_ratio, 통화, 평가 범위 |
| `scorecard/baseline/v1.5/` | 이관 담당 | git | `scores.json`(점수·근거 불릿), `observations.json`, `triggers.json`, `import-report.md` |
| `scorecard/rules/v1.8.json` | 규칙 담당 | git | 새 실행이 쓰는 규칙. 원천 allowlist 가 없다(personal use, 사용자 결정 2026-09-30) |
| `output/<run_id>/` | 실행 | git(입력·결과·승인), 일부 gitignore(`.lock`) | 실행 묶음 한 폴더. 아래 표 |
| `data/<company_id>/` | 수집 | gitignore | `collect` 가 받은 원문 캐시. `SCORECARD_DATA_ROOT` 로 위치를 바꾼다 |
| `scorecard/history.csv` | 빌드 | git | 승인본 이력 (run_id, approval_id, 기업, F1~F9, 합계, 순위, 변동 원인) |

실행 묶음 `output/<run_id>/` 의 파일은 `scripts/scorecard/paths.py` 의 `run_paths()` 가 돌려준다. 단계별로 흩어진 옛 폴더는 없다.

| 파일 | 만드는 단계 | 내용 |
|---|---|---|
| `run.json` `observations.json` `judgments.json` `sources.json` | `init` | 실행 설정과 입력(원자료·판단·출처) |
| `plan.md` | `init` | 실행 계획 (생성물) |
| `evidence/candidates.json` | `collect` | 수집한 근거 후보 (뉴스·공시) |
| `evidence/evidence.json` | 에이전트 선별 → 사람 확정 | 근거. `status: candidate` 로 올라오고 사람이 `confirmed` 로 바꾼다 |
| `triggers.json` | 에이전트 선별 | 재채점 조건. 미래 점수를 저장하지 않는다(C-14) |
| `research.md` | `research` | 입력 검증 결과와 미결 항목 |
| `results.json` `preview.md` | `calculate` | 점수와 기준선 대비 미리보기 |
| `draft.md` | `draft` | Markdown 초안 |
| `review.md` `review-parts/` | `review-template` 과 리뷰어 | 4 영역 리뷰. 영역별 결과는 `review-parts/<영역>.md` |
| `approval.json` `revocations.jsonl` | 승인 페이지 | 승인 해시와 취소 기록. 사람이 만든다 |
| `report.html` `audit.md` | 빌드 | 대시보드와 감사 문서 |
| `data_availability.json` | 수동(선택) | 자료 확보 현황 표시용 기록. 아래 설명 |
| `.lock` | 각 단계 | 실행 잠금(`{owner, started_utc, stage}`). 다른 소유자의 잠금은 `--take-lock` 으로 넘겨받는다 |

스키마는 `scripts/scorecard/schema.py` 가 엄격 파싱한다. 알 수 없는 키·범위 밖 점수·NaN/Infinity·빈 근거는 `SchemaError` 다.

| 객체 | 파일 | 필수 필드 |
|---|---|---|
| 관측 | observations.json items | observation_id, company_id, metric(카탈로그 `METRICS`), value, unit, as_of, kind, source_id, status(verified / legacy_unverified / not_applicable / not_disclosed / collection_failed / source_conflict / incompatible_basis / parse_failed), basis, raw, note |
| 판단 | judgments.json items | judgment_id, company_id, factor, kind(score/grade/criteria/matrix/paths/gate_inputs), score, inputs, evidence(비어 있으면 안 됨), reviewer, reviewed_at, status(new/carried), carried_from, revision_history(선택: `judge` 가 쌓는 `{revised_at, revised_by, reason, previous}`) |
| 실행 | run.json | run_id(=slug), report_type, title, as_of, price_as_of, info_cutoff, rule_version, rule_hash, baseline_id, companies, decisions[{id, choice, rationale, decided_by, decided_at}], created_at, purpose, assumptions, continued_from(선택: 이어받은 실행이 무엇에서 왔는지 기록) |
| 결과 | results.json | schema, run_id, input_hashes, decisions_applied, companies[{factors, moat, trap, total, complete, pending, rank}], ranking, population, pending_rule_decisions, results_hash |
| 승인 | approval.json | approval_id, approved_by, approved_at, hashes{rules, observations, judgments, run, results, draft} |
| 근거 | evidence/evidence.json items | evidence_id(`EV-<company_id>-NNN`), company_id, factors, kind(news / filing), source_id, published_at_utc, title, excerpt(600자 이하), relevance(추론), channel(disclosure / press / company_statement / secondary), conditional_impact(점수 이동 금지), horizon, counter_evidence, unverified, change_vs_previous, status(candidate / confirmed), reviewer·reviewed_at(confirmed 는 필수) |
| 트리거 | triggers.json items | trigger_id(`TRG-NNN`), company_id, factors, observation, condition, deadline, evidence_ids, source_ids, status(watching / fired / expired / withdrawn), recheck{factors, what}. 점수처럼 보이는 키는 거부한다(C-14) |
| 자료 확보 현황 | data_availability.json (선택) | schema, surveyed_at, scope, required_quarters, companies_with_full_quarters, headline, score_effect, not_re_surveyed, collection_note, materials[], companies[{company_id, quarter_ends, secured_quarters, missing, survey}], surveys{}, sources[], cautions[], references[] |

`data_availability.json` 은 채점 입력이 아니라 표시용 기록이다. 승인 해시 6종(rules·observations·judgments·run·results·draft)에 들어가지 않으므로 이 파일을 추가하거나 고쳐도 기존 승인은 무효가 되지 않는다. 대신 점수에도 개입하지 않는다. 렌더러는 이 파일이 있으면 「자료 확보 현황」 섹션을 만들고, 각 기업의 `ntm_per` 관측 기준일이 `surveyed_at` 보다 앞서면 그 조사가 점수에 반영되지 않았다고 표시한다. 조사 결과를 실제 점수에 넣으려면 관측을 새로 넣고 `research → calculate → draft → review` 를 다시 돌린 뒤 사람이 다시 승인해야 한다.

화면에 노출되는 `C-NN` 은 렌더러가 후처리로 `#dec-C-NN` 앵커 링크로 바꾸고, 「C-번호 사전」 항목을 규칙 파일의 `decisions` 에서 생성한다. 치환은 태그 사이 텍스트에만 적용하고 속성·`<style>`·`<script>`·경로 문자열(`C-13/...`)은 건드리지 않는다.

## 3. 계산 모듈과 요구 ID

| 요구 | 모듈 | 테스트 |
|---|---|---|
| F1·F4·F8 정성 (부품 상한 2) | `calc_qual.compute_manual` | `test_f1_component_cap` |
| F2 경로 매핑 (C-03 미결, 승계 score 허용) | `calc_qual.compute_f2` | `test_f2_requires_decision_and_carried_allowed` |
| F3 사다리 + 모방불가 상한 + 문 닫힘 | `calc_qual.compute_f3`, `rules.f3_ladder` | T-04 `test_t04_f3_all_combinations` |
| F5 `3 + A + H` | `calc_qual.compute_f5`, `rules.f5_formula` | T-05 |
| F7 2×2 (하한 -3, -4 불허) | `calc_qual.compute_f7`, `rules.f7_matrix`, schema | T-06 |
| F6 상장 구간·경계·EPS 4분기·기준 정합 | `calc_f6._listed`, `rules.f6_band/f6_boundary_flag` | T-01, T-02, T-03, R01 |
| F6 비상장 배수·정성 점수 | `calc_f6._private` | `test_private_multiples_and_manual_score` |
| F9 G1~G4, 정책·결정 오버라이드 | `calc_f9.compute_f9`, `_g4` | T-07(`baseline_import.standard_fcf`), T-09, T-10, T-11, R02~R04 |
| 관측 상태 의미(적용 제외 ≠ 미공시), 흐름 지표 period, 승인자 문자열 | `schema.validate_observations`, `validate_approval` | `TestReviewRegressions` |
| 합산·동점 순위·미완료 제외 | `aggregate` | T-12 |
| 결정론·해시 | `engine.compute/load_results/recompute_matches` | validator "results deterministic recompute" |
| 기준선 이관 검산 (T-17) | `baseline_import` + `import-report.md` MD 대조 | 14사 match |
| 입력 검증 (T-03, T-05, T-06, R05, R06) | `schema.validate_*` | `TestReviewRegressions` |

`tests/test_scorecard_calc.py` 는 `uv run --frozen python -X utf8 -m unittest discover -s tests -t .` 로 실행한다. 설계진행 검증 담당의 독립 재현 `validation/test_scorecard_review.py`(R01~R06, 10건)도 같은 코드로 통과해야 한다.

## 4. 미결 결정의 취급

결정을 내린 뒤에도 남는 대기와, 결정 자체가 미결인 대기를 구분한다. 실행 단위 선택이 "적용하지 않는다"(예: C-13 `reject_proxy`, C-16 `hold`)로 끝나면 그 factor 는 `needs_rule_decision` 이 아니라 자료·판단 대기로 표시되고 `pending_rule_decisions` 에서 빠진다. 결정을 내렸는데 산출물이 계속 결정을 요구하면 안 된다.

규칙 파일은 실행에 `rule_hash` 로 고정된다. 문구만 고쳐도 진행 중인 실행이 무효가 되므로, 결정의 운영 해석은 이 문서에 적고 규칙 파일은 규칙 개정(새 버전) 때만 손댄다.

결정 C-01~C-22 의 **활성 요약·선택지·상태는 `scorecard/rules/v1.5.json` 의 `decisions` 가 원본**이다. `design-guideline.md` 11절은 설계 시점의 발견 기록이며, 이후 보충된 문구(C-06 의 BEP OR 분기 활성, C-08 의 별표 G/H 분류 긴장 등)는 규칙 파일에만 반영한다.

`scorecard/rules/v1.5.json` 의 `decisions[].status == pending` 이고 `blocking: true` 인 항목(C-03, C-05, C-06, C-13, C-16)은 계산기가 해당 분기에서 `needs_rule_decision` 을 반환하고 기업을 공식 순위에서 제외한다. 실행 단위 `run.json.decisions` 에 `{id, choice, rationale, decided_by, decided_at}` 를 기록한 경우에만 그 실행에서 선택이 적용되며 results/preview/HTML 에 "실행 단위 결정"으로 표시된다. 규칙 파일의 status 를 `resolved` 로 바꾸는 것은 규칙 개정(새 버전)이다.

| ID | 계산기 동작 |
|---|---|
| C-03 | F2 paths 입력은 `activate_candidate_mapping` 선택 시에만 환산. 승계 score 는 경고와 함께 사용 |
| C-04 | G3 완충은 현금+확정 미인출 여신(기본 exclude). include_v15 도 숫자 관측만 산입 |
| C-05 | G1 실패 뒤 진단 점수가 다르면 대기. `diagnose_only`/`apply` 로 해소. 이미 하한 -5 면 불필요 |
| C-06 | 영업손실률 경계는 `proposed_v15_boundaries` 선택 시만 적용. BEP 후퇴 -5 는 원문 OR 조건 적용 + 경고 |
| C-13 | NTM proxy(`annual_weighted_proxy`)는 `accept_proxy_with_flag` 선택 시만 채점. `reject_proxy` 는 내려진 결정이므로 규칙 미결이 아니라 `pending_data`(정확한 4분기 컨센서스 확보 필요)로 남고 미결 목록에서 빠진다 |
| C-16 | G4 판정 불가(자료 없음·비교 가능성 미확인)는 `hold`/`downgrade` 선택 전까지 대기. 비상장 FCF 미공시 사유와는 중복 감점하지 않음 |
| C-20 | Anthropic 단일 분기 흑자는 TTM 부호로 쓰지 않음 → F9 pending_data |

## 5. 단계·상태·승인 흐름

아래 경로는 모두 `output/<run_id>/` 기준이다. 모든 명령은 `uv run --frozen python -X utf8 scripts/…` 로 실행한다.

```
init --rule v1.8 ──► plan.md + run.json·observations.json·judgments.json·sources.json
collect ──► evidence/candidates.json (뉴스·공시 후보) ; --kind prices 는 observations.json 에 ⑥ price·market_cap 관측을 넣는다
  └─ 에이전트가 후보를 골라 evidence/evidence.json(candidate)·triggers.json 작성
research ──► research.md (observations_hash·judgments_hash 결속) ; 인용한 근거의 출처를 sources.json 에 등록(--no-register 로 끔)
calculate ──► results.json(+results_hash) + preview.md ; 입력 해시가 바뀌면 이전 approval.json 자동 무효
draft ──► draft.md (results_hash 결속)
review-template ──► review.md (4 영역 + Q01~Q23, status: needs_fix) → 리뷰어가 review-parts/ 를 채움 → status: pass
[사람] 승인 페이지 ──► 근거 확정(candidate → confirmed) · 판단 수정(judge) · 승인 · 취소 → approval.json (rules/observations/judgments/run/results/draft 해시 결합)
build_report.py ──► 승인 해시 == 현재 해시 검증 → report.html·audit.md → history.csv append(중복 방지) → 사후 검증

[기업 추가 갈래]
add-company ──► scorecard/companies.json 등록
init --from-run ──► 이전 실행 계승 + plan + 입력 생성 (continued_from 기록)
collect·research(신규만) ──► diff (1층: 기존 기업 불변 검증) ──► calculate ──► diff (2층: 점수 투영 불변 검증) ──► draft ──► review ──► (사람) 승인 ──► build
```

모든 단계(`init`·`collect`·`research`·`calculate`·`draft`·`review-template`)와 에이전트 세션의 `confirm`·`judge` 는 실행 잠금 `.lock` 을 검사하고 기록한다. 다른 소유자의 잠금이면 거부하고 `--take-lock` 으로 넘겨받는다.

### 근거 계층

`collect` 는 후보(`candidate`)만 만든다. 후보를 확정(`confirmed`)하는 것은 사람이고 승인 페이지에서 한다. 규칙은 셋이다.

- `status: new` 판단은 `confirmed` 근거만 인용한다. 후보를 인용하면 교차 참조 검증이 실패한다(`schema.validate_cross_refs`).
- `confirmed` 근거에는 `reviewer`·`reviewed_at` 이 있어야 한다.
- 트리거는 재채점 조건만 저장하고 미래 점수를 저장하지 않는다(C-14).

`not_disclosed`(발행사가 공시하지 않음을 확인)와 `unverified`(우리가 찾지 못함)는 다르다. 근거를 확정하면 판단·결과·초안 해시가 바뀌어 리뷰가 무효가 되므로 `research → calculate → draft → review` 를 다시 돌린다.

가격은 `collect --kind prices` 가 yfinance 로 ⑥ `price`·`market_cap` 관측을 넣는다. EPS·컨센서스는 받지 않는다. 조회일이 종가일과 하루 넘게 다르면 벤더 시가총액을 쓰지 않고, ADR 시가총액은 벤더 값만 쓴다. 종가가 NaN 인 날은 건너뛰고 기준일 이하의 직전 확정 종가와 그 날짜를 쓰며(건너뛴 날짜는 `skipped_nonfinite_close` 로 요약에 남는다), 전부 NaN 이면 오류다. 가격 실패는 회사 단위라 한 회사가 실패해도(중복 관측 포함) 나머지는 기록된다. 공시 수집에는 `SEC_UA` 가 필요하다(루트 `.env` 의 `SEC_UA=이름 이메일`, 또는 같은 이름의 환경변수). 영문으로 적는다(HTTP 머리글 제약). 뉴스 질의는 레지스트리의 `news_queries`(없으면 표시명·티커)를 쓰고, 상장 12개사의 `cik` 는 `resolve-cik --apply` 로 기입돼 있다. 두 키는 수집기만 읽는다.

### 판단 수정 (사람 행위, 승인 페이지 8절)

정성 판단의 입력을 고치는 길은 `scorecard_cli.py judge` 하나이고 승인 페이지 8절이 그 앞단이다. 점수 칸은 고치지 않는다. F1·F4·F8 은 `score`, F3 `criteria`·F5 `grade`·F7 `matrix`·F9 `gate_inputs` 는 판정 재료 키만 받고, F2·F6 은 대상이 아니다. 근거 문장(`evidence`)은 판정 재료와 어긋나지 않게 함께 고칠 수 있다. 고치면 `status: new`·검토자·검토일이 갱신되고 이전 값은 항목 안 `revision_history` 에 쌓인다. 새 판단은 확정된 근거만 인용하므로 교차 참조가 깨지면 쓰기 전 상태로 되돌린다. 판단 해시가 바뀌므로 `research → calculate → draft → review` 를 다시 돌린 뒤 사람이 승인한다. 승인 페이지는 factor 를 고르면 그 factor 의 모든 기업 판단을 나란히 보이므로(Q03) 같은 잣대가 닿는 다른 기업 판단을 함께 본다. 쓰는 요청은 일회용 코드가 있어야 한다.

### 승인 (사람 행위)

승인과 취소는 사람이 `node server.js --approvals` 로 띄운 승인 페이지(`http://127.0.0.1:3000/approve/<run_id>`)에서 한다. 터미널에 6자리 일회용 코드가 나오고, 페이지에서 근거 확정·승인·취소를 한다. 코드를 5번 틀리면 서버를 다시 띄워야 하고, 승인이 성공하면 서버는 내려간다. 에이전트는 `approve`·`revoke` 를 실행하지 않는다. 훅(`guard.py`)과 `scorecard.stages` 의 `approve`·`revoke` 함수 본체(에이전트 세션 거부, CLI 든 import 든 같은 판정) 둘 다 막고, 첫 방어선은 그 함수 본체와 해시 검증이다. 승인 있는 실행에 대한 `init --force` 도 에이전트 세션이면 `init_run` 이 거부하고 훅이 막는다. 승인 서버가 떠 있는 동안 브라우저 도구를 가진 에이전트가 터미널의 코드를 읽으면 누를 수 있는 틈이 있다. 코드는 파일에 쓰이지 않고 서버는 승인 뒤 내려가며, 사용자가 이를 알고 수용했다(2026-09-30). 에이전트가 사람에게 하는 말은 "승인 대기" 보고이고, 사람이 에이전트에게 하는 말은 "고쳐" 와 "빌드해" 이다.

상태 이름: 자료 부족 `pending_data`, 판단 부족 `needs_judgment`, 규칙 미결 `needs_rule_decision`, 승인 필요 `awaiting_user`(빌더 메시지), 검토 미완 `needs_fix`(리뷰 frontmatter). 해시가 하나라도 바뀌면 검증기가 리뷰·승인을 무효로 판정한다(T-14). 같은 승인본 재빌드는 history.csv 에 행을 추가하지 않는다(T-15). 사전 검증 실패 시 HTML 을 쓰지 않으므로 최신 MD/HTML/CSV 가 갈라지지 않는다(T-16).

> **해시는 파일 바이트에 걸린다(`sha256_file` = `read_bytes`).** 이 저장소는 `.gitattributes` 가 없고 `core.autocrlf=true`(Git for Windows 시스템 설정)라 checkout·재기록 때 LF/CRLF 가 바뀌면 **내용이 같아도** `rule_hash` 와 승인 해시 6종이 갈린다. 2026-09-14 bfb4fbd 가 LF 바이트로 `rule_hash` 를 고정해 CRLF 작업 트리에서 research·calculate 가 멈췄고 5209311 에서 재고정했다. **[해소 2026-09-15 FIX-53]** 이제 `.gitattributes` 가 scorecard 해시 대상 파일의 줄끝을 고정한다(승인된 baseline·v1.5 규칙은 CRLF, 나머지는 LF). 해시 함수를 줄끝 정규화 기반으로 바꾸는 안은 기존 승인 해시가 모두 달라져 적용하지 않았다.

## 6. 산출물 렌더러

| 산출물 | 모듈 | 요구 |
|---|---|---|
| plan/research/draft/review 템플릿/preview | `render_md` | 9절 표. draft 필수 섹션 개요·종합 순위표·기업별 상세·지표 원자료·방법과 규칙·References |
| HTML 대시보드(단일 파일) | `render_html` | dashboard-design 스킬: 320px 리플로우, 표 모바일 패턴(합계 열만 + 첫 두 열 sticky + 행 탭→카드), 탭 대상 ≥24px, Pretendard 링크+폴백, 타입 스케일 토큰, 자체 팔레트(soft/line 짝), 인라인 style 없는 반응형, 산점도 결정론적 라벨 배치, aria-label |
| history.csv | `render_csv` | (run_id, approval_id, company_id) 중복 방지 |

HTML 검증(`scorecard.validate._validate_html`): generator 메타(`scorecard-builder` 표식), `results-hash` 메타, viewport, 면책 footer, 순위표 `data-company` 행, source marker 없음. Playwright 실측(2026-09-08): 320/768/769/1280 넘침 0건, 탭 대상 위반 0건, sticky 첫 열 유지, 행 탭 → 카드 열림.

## 7. 훅·명령·스킬

- 훅: `scripts/hooks/guard.py` 한 모듈이다. `block_dangerous_bash`, `protect_sensitive_files`(보호 경로 `scorecard/baseline/**` 포함, 쓰기 대상일 때만 막고 읽기는 통과, PowerShell cmdlet·`find -delete`·`xargs`·글롭 판정, 승인·취소 명령과 승인 있는 실행의 `init --force` 차단), `enforce_plan`(`output/<run_id>/` 단계 순서·실행 잠금), `forbid_financial_advice`, `remind_review`(경고만), `enforce_memory`, `inject_memory_context`. 목록과 한계는 `scripts/hooks/README.md`. 핵심 통제는 훅이 아니라 `scorecard.stages` 의 승인 함수·검증기·빌더가 직접 수행하고(설계 지침 4.3), 훅은 둘째 방어선이다. 훅은 도구 호출 밖(사람 터미널, 훅이 배선되지 않은 에이전트)을 막지 못한다.
- 명령: `/score-plan`, `/score-add-company`, `/score-extend`, `/score-diff`, `/score-collect`, `/score-research`, `/score-calculate`, `/score-draft`, `/score-review`, `/score-approve`, `/score-build`, `/score-goal` → `.claude/skills/score-*/SKILL.md`. `/score-approve` 는 승인을 실행하지 않고 "승인 대기" 보고와 승인 페이지 안내만 한다.
- 리뷰어 에이전트: `.claude/agents/`(`fact-checker`, `evidence-editor`, `report-designer`)와 같은 내용의 `.codex/agents/*.toml`.
- 실행은 `uv run --frozen python -X utf8 scripts/…` 이다. 시스템 `python`·`python3` 를 직접 부르지 않는다. 훅 배선도 `uv run` 한 줄이라 bash 를 거치지 않는다.

## 8. 회귀·수용 기준 매핑

| 검증 | 방법 |
|---|---|
| T-01~T-07, T-09~T-12 | `tests/test_scorecard_calc.py` (35건) |
| T-08 (YTD·분기 혼재, 정정 공시, 연결/세그먼트 범위) | **미구현.** 이관 자료에 해당 사례가 없어 아직 테스트가 없다. 신규 재무 관측을 직접 수집하기 전에 채운다 |
| T-13 | 검증기: 체크리스트 23행·4 영역·검토자 없는 pass 차단 |
| T-14 | 검증기: review results_hash/draft_hash, approval hashes 비교 |
| T-15 | `render_csv.append_history` 중복 키 건너뜀 |
| T-16 | 빌더 사전 검증 실패 시 파일 미생성 |
| T-17 | `baseline/v1.5/import-report.md` 14사 match, 파싱 실패 목록 |
| T-18 | draft 순위표 ↔ results 대조, HTML `data-company` 대조 |
| T-19 | Playwright 실측 + `node --check` 상당(인라인 JS 는 정적 문자열) |
| T-20 | 기존 stock validator 경로 무변경 (report_type 없는 slug 는 기존 분기) |

## 9. 알려진 한계

2026-10-02 `open-items.md` 를 정리하며 지금도 맞는 주의 사항만 옮겼다.

| ID | 언제 | 내용 |
|---|---|---|
| RC3-06 | `decisions_applied` 를 근거로 무엇을 주장할 때 | **소비 증명이 아니다.** `results.decisions_applied` 는 run.json `decisions` 를 `id:choice` 로 옮긴 목록일 뿐이다(engine.py). 선택을 읽는 분기가 없거나(C-11) 현재 모드에서 효력이 없는(C-13 은 bands 모드 전용) 선택도 들어 있다. 적용 여부는 factor 산식·경고에서 확인한다. 소비 추적(선택마다 읽은 factor 기록)은 구현하지 않았다 |
| RC3-08 | 관측 kind·metric 의미를 스키마로 막으려 할 때 | **단어 의미는 스키마가 아니라 소비 코드가 막는다.** `metric=arr` 에 `kind=run_rate` 를 `actual` 로 바꿔도 스키마는 통과한다. 비상장 P2 보정의 `arr_growth` 는 `accepted_kinds: ["actual"]` 을 calc_f6_params 가 읽어 run_rate 를 거부한다. kind 를 새로 쓰는 소비자를 만들면 그 코드에 같은 거부를 넣는다 |
| 재빌드 | 승인 뒤 리뷰 파일을 고쳤을 때 | 승인 해시 여섯 가지에 `review.md` 는 들지 않아 승인은 유효하지만, HTML References 의 검토자·리뷰 유형은 빌드 시점의 리뷰 파일에서 읽는다. 리뷰 파일을 고쳤으면 빌드를 다시 돌린다. 같은 승인본이면 `history.csv` 에 행이 추가되지 않는다 |
