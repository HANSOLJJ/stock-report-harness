# 채점표 하네스 구조

이 문서는 코드 구조, 저장 스키마, 요구 ID(D·T)를 실제 모듈·파일·테스트에 연결한다. 채점 규칙은 `rules.md`, 실행 순서와 승인 페이지 사용법은 `guide.md`, 훅의 동작과 한계는 `scripts/hooks/README.md` 에 있다. 남은 작업은 루트 `TODO.md` 에 모은다.

## 1. 설계 원칙과 진입점

| 요구 ID | 원칙 | 구현이 만족해야 할 결과 |
|---|---|---|
| D-01 | 원자료·판단·규칙이 입력이고 점수는 결과다 | 자동 산출 factor 점수를 직접 수정할 수 없다. 입력 또는 규칙 변경으로 재계산한다 |
| D-02 | 같은 입력과 같은 규칙은 같은 결과다 | 실행 중 재수집하지 않으며 표시 반올림이 판정에 개입하지 않는다 |
| D-03 | 정성 판정과 산술 자동화를 분리한다 | 사람이 등급·경로·분류를 결정하면 산식·사다리·구간 적용은 프로그램이 한다 |
| D-04 | 모르는 값과 0은 다르다 | 누락을 0점, 위험 없음, 경로 실패 또는 정상으로 자동 치환하지 않는다 |
| D-05 | 같은 속성의 중복 계상을 금지한다 | 동일 관계도 확산 이익과 대체 불가 위험처럼 다른 속성이면 별도 평가할 수 있다 |
| D-06 | 회사별 예외로 원하는 순위를 만들지 않는다 | 동일 적용 범위의 기업에는 동일 구간·분모·기간을 적용한다 |
| D-07 | 실현된 성과와 미래 계획을 구분한다 | 가점은 출하·매출·채택 등 확인된 성과로 판단한다. 계획은 트리거로 남긴다 |
| D-08 | 과거 기록은 보존한다 | 원본 이관 중 불일치를 고쳐 과거 점수를 새로 만들지 않는다 |
| D-09 | 출력은 한 실행의 결과를 공유한다 | 순위표·카드·MD·HTML·CSV·차트·이력을 따로 편집하지 않는다 |
| D-10 | 검토·승인은 검토받은 내용에 연결한다 | 규칙·자료·판단·보고 내용 변경 시 해당 검토와 승인이 유효한지 다시 검사한다 |

진입점은 다음과 같다.

- 실행 판별: `output/<run_id>/plan.md` frontmatter `report_type: ai_scorecard`, run_id 는 `ai-scorecard-` 접두. `report_type` 필드는 `scripts/report_contract_lib.py` 의 frontmatter 키 목록에 있다.
- 검증: `scripts/validate_report_contract.py` 의 `validate_contract` 가 `scorecard.validate.validate_scorecard` 로 위임한다(`ValidationResult` 공유).
- 빌드: `scripts/build_report.py` 가 `scorecard.render_html.build_scorecard` 로 위임한다.
- 초안의 숫자는 생성물이라 출처 표식(`[S1]`)을 요구하지 않는다. 대신 draft frontmatter `results_hash` 가 results.json 과 결속되고 검증기가 순위표 행을 대조한다.
- 투자 권유 표현 차단은 `guard.py` 의 `forbid_financial_advice` 가 `draft.md`·`judgments.json`·`evidence/evidence.json` 에 적용한다.
- 가격은 `collect --kind prices` 가 실행 원자료(observations.json)에 넣는다. build 중에는 다시 수집하지 않는다(D-02).

## 2. 파일 소유권과 저장 스키마

| 경로 | 누가 쓰나 | 추적 | 내용 |
|---|---|---|---|
| `scorecard/rules/v1.5.json` ~ `vN.json` | 규칙 개정 때 새 버전을 더한다 | git | factor 모드·범위, ⑥ 잣대·트랙, ⑨ 게이트 정책, ③ 사다리, ⑤ 산식, ⑦ 매트릭스, 체크리스트 Q01~Q23, 결정(C-xx) 상태·선택지, 긴장 목록. 새 실행은 현행 버전(`rules.md` 머리말)을 쓴다. 승인 해시에 파일 바이트 해시가 들어가므로 이미 쓰인 파일은 고치지 않는다. 사람용 설명은 `rules.md` |
| `scorecard/companies.json` | `add-company`, `resolve-cik --apply` | git | 안정 company_id, 표시명·별칭, 유형, 상장, 티커, share_basis, adr_ratio, 통화, 평가 범위, `news_queries`, `cik` |
| `scorecard/baseline/v1.5/` | 이관(끝남). 보호 경로 | git | `scores.json`(점수·근거 불릿), `observations.json`, `triggers.json`, `import-report.md` |
| `output/<run_id>/` | 각 단계 | git(입력·결과·승인), 일부 gitignore(`.lock`) | 실행 묶음 한 폴더. 아래 표 |
| `data/<company_id>/` | `collect` | gitignore | 수집한 원문 캐시. `SCORECARD_DATA_ROOT` 로 위치를 바꾼다 |
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

상태 이름의 뜻은 다음과 같다. 이름은 바꿀 수 있어도 뜻을 합치지 않는다. `unknown` 은 `not_applicable` 이 아니며, 적용 제외에도 이유가 있어야 한다.

| 구분 | 상태 | 처리 |
|---|---|---|
| 관측 `status` | `verified` | 계산 입력 가능 |
| | `legacy_unverified` | 기준선에서 이관한 값. 계산에 쓰이면 결과에 미검증 입력으로 표시하되 점수는 깎지 않는다 |
| | `not_disclosed` | 값이 없다. 결측 유형(`missing_type`)으로 어느 쪽인지 가른다 |
| | `collection_failed` · `parse_failed` | 다시 수집하거나 사람이 넣을 대상. 자동 감점 금지 |
| | `source_conflict` | 값을 고른 근거가 필요하다 |
| | `incompatible_basis` | 정의·기간이 맞지 않아 비교·합산을 막는다 |
| | `not_applicable` | 개념상 해당 없음 |
| 관측 `missing_type` | `not_disclosed_confirmed` | 공시된 적 없음이 확인됨. 점수에 닿는 유일한 결측 유형이다(`rules.md` 2.6) |
| | `unverified` · `indeterminate` · `not_applicable` | 점수에 닿지 않는다(자료 대기 또는 해당 없음) |
| factor 결과 `status` | `ok` · `carried_score` | 점수가 있다. `carried_score` 는 이전 실행에서 이어받은 판단으로 낸 점수 |
| | `pending_data` | 자료 대기 |
| | `needs_judgment` | 판단 입력 대기. 필요한 질문을 `pending` 에 적는다 |
| | `needs_rule_decision` | 규칙 미결. 해당 계산 분기를 활성화하지 않는다 |
| | `error` · `unavailable` | 입력이 규칙과 모순되거나 산출할 수 없다 |

`data_availability.json` 은 채점 입력이 아니라 표시용 기록이다. 승인 해시 6종(rules·observations·judgments·run·results·draft)에 들어가지 않으므로 이 파일을 추가하거나 고쳐도 기존 승인은 무효가 되지 않는다. 대신 점수에도 개입하지 않는다. 렌더러는 이 파일이 있으면 「자료 확보 현황」 섹션을 만들고, 각 기업의 `ntm_per` 관측 기준일이 `surveyed_at` 보다 앞서면 그 조사가 점수에 반영되지 않았다고 표시한다. 조사 결과를 실제 점수에 넣으려면 관측을 새로 넣고 `research → calculate → draft → review` 를 다시 돌린 뒤 사람이 다시 승인해야 한다.

화면에 노출되는 `C-NN` 은 렌더러가 후처리로 `#dec-C-NN` 앵커 링크로 바꾸고, 「C-번호 사전」 항목을 규칙 파일의 `decisions` 에서 생성한다. 치환은 태그 사이 텍스트에만 적용하고 속성·`<style>`·`<script>`·경로 문자열(`C-13/...`)은 건드리지 않는다.

## 3. 계산 모듈과 요구 ID

| 요구 | 모듈 | 테스트 |
|---|---|---|
| F1·F4·F8 정성 (부품 상한 2) | `calc_qual.compute_manual` | `test_f1_component_cap` |
| F2 경로 환산 (C-03 확정: 경로 수 0·1·2 → 2·3·4, 세대 격차 → 5. 경로 입력이 없으면 승계 score) | `calc_qual.compute_f2`, `_f2_generation_gap` | `tests/test_scorecard_c03.py`, `test_f2_requires_decision_and_carried_allowed` |
| F3 사다리 + 모방불가 상한 + 문 닫힘 | `calc_qual.compute_f3`, `rules.f3_ladder` | T-04 `test_t04_f3_all_combinations` |
| F5 `3 + A + H` | `calc_qual.compute_f5`, `rules.f5_formula` | T-05 |
| F7 2×2 (v1.7 이후 −2~0, `large\|yes` −2. v1.5 규칙은 −3) | `calc_qual.compute_f7`, `rules.f7_matrix`, schema | T-06, `tests/test_scorecard_fix52_schema.py` |
| F6 상장 네 잣대·트랙·P4·경계 표시 (`parameters` 모드, v1.7 이후 정본) | `calc_f6_params.compute_listed`, `rules.f6_parameter_band/f6_parameter_boundary_flag` | `tests/test_scorecard_f6_v17.py` |
| F6 비상장 밸류÷보정 매출 + 보정 한 칸 (C-12) | `calc_f6_params.compute_private` | `tests/test_scorecard_f6_v17.py` `TestF6Private` |
| F6 NTM PER 구간표 (`bands` 모드, v1.5·v1.6 실행 재현용) | `calc_f6._listed`, `rules.f6_band/f6_boundary_flag` | T-01~T-03(구버전), R01 |
| F9 G1~G4, 정책·결정 오버라이드 | `calc_f9.compute_f9`, `_g4` | T-07(`baseline_import.standard_fcf`), T-09~T-11, R02~R04, `TestV17F9Rescaled` |
| 관측 상태 의미(적용 제외 ≠ 미공시), 흐름 지표 period, 승인자 문자열 | `schema.validate_observations`, `validate_approval` | `TestReviewRegressions` |
| 합산·동점 순위·미완료 제외 | `aggregate` | T-12 |
| 결정론·해시 | `engine.compute/load_results/recompute_matches` | validator "results deterministic recompute" |
| 기준선 이관 검산 (T-17) | `baseline_import` + `import-report.md` MD 대조 | 14사 match |
| 입력 검증 (T-03, T-05, T-06, R05, R06) | `schema.validate_*` | `TestReviewRegressions` |

테스트는 `uv run --frozen python -X utf8 -m unittest discover -s tests -t .` 로 실행한다. `tests/test_scorecard_calc.py` 는 v1.5 규칙으로 검사한다(T-01~T-12 의 원래 정의). 현행 규칙의 ⑥ 은 `test_scorecard_f6_v17.py`, ⑦ 재척도는 `test_scorecard_fix52_schema.py`, v1.8 로드와 재계산은 `test_rules_v18.py`, v1.9 의 트랙 판정은 `test_rules_v19.py` 가 본다. 독립 리뷰가 찾은 회귀 R01~R06 은 `test_scorecard_calc.py` 의 `TestReviewRegressions` 가 고정한다.

## 4. 미결 결정의 취급

결정을 내린 뒤에도 남는 대기와, 결정 자체가 미결인 대기를 구분한다. 실행 단위 선택이 "적용하지 않는다"(예: C-13 `reject_proxy`, C-16 `hold`)로 끝나면 그 factor 는 `needs_rule_decision` 이 아니라 자료·판단 대기로 표시되고 `pending_rule_decisions` 에서 빠진다. 결정을 내렸는데 산출물이 계속 결정을 요구하면 안 된다.

규칙 파일은 실행에 `rule_hash` 로 고정된다. 문구만 고쳐도 진행 중인 실행이 무효가 되므로, 결정의 운영 해석은 이 문서에 적고 규칙 파일은 규칙 개정(새 버전) 때만 손댄다.

결정(C-xx)의 **상태·선택지는 실행이 쓰는 규칙 파일의 `decisions` 가 원본**이다. 사람용 미결 목록은 `rules.md` 8절에 있다.

규칙 파일에서 아직 확정되지 않은 결정이 걸린 분기는 계산기가 `needs_rule_decision` 을 반환하고 그 기업을 공식 순위에서 제외한다. 실행 단위 `run.json.decisions` 에 `{id, choice, rationale, decided_by, decided_at}` 를 기록한 경우에만 그 실행에서 선택이 적용되며 results/preview/HTML 에 "실행 단위 결정"으로 표시된다. 규칙 파일의 status 를 `resolved` 로 바꾸는 것은 규칙 개정(새 버전)이다. 결정을 읽는 코드 분기는 각 `calc_*.py` 의 `decision_choice(run, rules, "C-xx")` 호출이다.

## 5. 단계·상태·승인 흐름

아래 경로는 모두 `output/<run_id>/` 기준이다. 모든 명령은 `uv run --frozen python -X utf8 scripts/…` 로 실행한다.

```
init --rule vN ──► plan.md + run.json·observations.json·judgments.json·sources.json
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

수집 세부(가격의 NaN 종가 처리, `SEC_UA`, 뉴스 질의)는 `score-collect` 스킬과 `guide.md` 에 있다. 레지스트리의 `news_queries` 와 `cik` 는 수집기만 읽는다.

### 판단 수정

정성 판단의 입력을 고치는 코드 경로는 `stages.revise_judgment` 하나다. 사람이 직접 고치는 것(`judge`)과 에이전트 제안(`propose`)을 반영하는 것(`proposal --accept`, 2026-10-07 부터 에이전트도 한다)이 모두 이 경로를 지난다. 점수 칸은 고치지 않는다. F1·F4·F8 은 `score`, F3 `criteria`·F5 `grade`·F7 `matrix`·F9 `gate_inputs` 는 판정 재료 키만 받고(허용값은 `schema.JUDGMENT_INPUT_CHOICES`), F2·F6 은 대상이 아니다. 고치면 이전 값이 항목 안 `revision_history` 에 쌓이고, 교차 참조가 깨지면 쓰기 전 상태로 되돌린다. 승인 페이지에서 고치는 법은 `guide.md` 에 있다.

### 승인

승인과 취소는 사람 행위다. 막는 장치는 둘이다. 첫 방어선은 `scorecard.stages` 의 `approve`·`revoke` 함수 본체가 에이전트 세션(`agent_session_markers`)을 거부하는 것과 해시 검증이고, 둘째 방어선은 훅이다. 승인 있는 실행에 대한 `init --force` 도 에이전트 세션이면 `init_run` 이 거부한다. 승인 페이지 사용법은 `guide.md`, 남은 틈(승인 서버가 떠 있는 동안의 일회용 코드)은 AGENTS.md 「통제의 위치」에 있다.

상태 이름: 자료 부족 `pending_data`, 판단 부족 `needs_judgment`, 규칙 미결 `needs_rule_decision`, 승인 필요 `awaiting_user`(빌더 메시지), 검토 미완 `needs_fix`(리뷰 frontmatter). 해시가 하나라도 바뀌면 검증기가 리뷰·승인을 무효로 판정한다(T-14). 같은 승인본 재빌드는 history.csv 에 행을 추가하지 않는다(T-15). 사전 검증 실패 시 HTML 을 쓰지 않으므로 최신 MD/HTML/CSV 가 갈라지지 않는다(T-16).

> **해시는 파일 바이트에 걸린다(`sha256_file` = `read_bytes`).** 줄끝(LF/CRLF)이 바뀌면 내용이 같아도 `rule_hash` 와 승인 해시 6종이 갈린다. 그래서 `.gitattributes` 가 해시 대상 파일의 줄끝을 고정한다(승인된 baseline·v1.5 규칙은 CRLF, 나머지는 LF). 해시 함수를 줄끝 정규화 기반으로 바꾸면 기존 승인 해시가 모두 달라지므로 바꾸지 않는다.

## 6. 산출물 렌더러

| 산출물 | 모듈 | 요구 |
|---|---|---|
| plan/research/draft/review 템플릿/preview | `render_md` | 9절 표. draft 필수 섹션 개요·종합 순위표·기업별 상세·지표 원자료·방법과 규칙·References |
| HTML 대시보드(단일 파일) | `render_html` | dashboard-design 스킬: 320px 리플로우, 표 모바일 패턴(합계 열만 + 첫 두 열 sticky + 행 탭→카드), 탭 대상 ≥24px, Pretendard 링크+폴백, 타입 스케일 토큰, 자체 팔레트(soft/line 짝), 인라인 style 없는 반응형, 산점도 결정론적 라벨 배치, aria-label |
| history.csv | `render_csv` | (run_id, approval_id, company_id) 중복 방지 |

HTML 검증(`scorecard.validate._validate_html`)은 generator 메타(`scorecard-builder` 표식), `results-hash` 메타, viewport, 면책 footer, 순위표 `data-company` 행, source marker 없음을 본다. 화면 검증은 Playwright 로 320·768·1280px 에서 가로 넘침, 탭 대상 크기, 첫 열 고정, 행 탭으로 카드가 열리는지를 실측한다.

## 7. 훅·명령·스킬

- 훅: `scripts/hooks/guard.py` 한 모듈이고 훅은 다섯 개다(`block_dangerous_bash`, `protect_sensitive_files`, `enforce_plan`, `forbid_financial_advice`, `remind_review`). 동작·보호 경로·한계는 `scripts/hooks/README.md` 가 원본이다. 핵심 통제는 `scorecard.stages` 의 승인 함수·검증기·빌더가 직접 하고 훅은 둘째 방어선이다.
- 명령: `.claude/skills/score-*/SKILL.md` 12개가 곧 `/score-*` 명령이다(Claude Code 가 스킬 폴더 이름을 명령으로 올린다). `/score-approve` 는 승인을 실행하지 않고 "승인 대기" 보고와 승인 페이지 안내만 한다. Codex 는 같은 내용의 사본을 `.agents/skills/` 에서 읽으므로 스킬을 고치면 사본도 맞춘다.
- 리뷰어 에이전트: `.claude/agents/`(`fact-checker`, `evidence-editor`, `report-designer`)와 같은 내용의 `.codex/agents/*.toml`.
- 실행은 `uv run --frozen python -X utf8 scripts/…` 이다. 시스템 `python`·`python3` 를 직접 부르지 않는다. 훅 배선도 `uv run` 한 줄이라 bash 를 거치지 않는다.

## 8. 회귀·수용 기준 매핑

T 번호는 설계 시점(2026-09-08)에 v1.5 규칙을 기준으로 정의됐다. 규칙이 바뀐 항목은 "현행" 열에 지금 무엇을 검사하는지 적는다.

| ID | 입력·상황 | 기대 결과 | 현행 | 검증 위치 |
|---|---|---|---|---|
| T-01 | ⑥ 구간 경계의 직전·정확값·직후 | 정해진 반개방 구간 적용. 표시 반올림 영향 없음 | 구버전 정의는 NTM PER 경계 20·29·42·62·90. 현행은 P1 25·45, P2 8·20, P3 30%·15%·5% | 구버전 `test_scorecard_calc.py` `TestF6`, 현행 `test_scorecard_f6_v17.py` `TestF6ParameterBands` |
| T-02 | ⑥ 경계 거리 정확히 3%, 그 안과 밖 | 표시만 달라지고 점수는 그대로 | 같음. 현행은 잣대마다 자기 경계에 대해 계산 | `test_t02_boundary_flag_only_warns`, `test_boundary_flag_is_display_only` |
| T-03 | ⑥ 입력 누락·0·음수·중복 기간·소유 범위 불일치 | 자동 채점 차단, 구체적 자료 사유 표시 | 구버전 정의는 NTM EPS 네 분기. 현행은 P1~P3 입력 결측·소유 범위·순손실 처리 | 구버전 `test_t03_missing_or_bad_eps_blocks`, 현행 `TestF6ParameterGuards` |
| T-04 | ③ 세 기준의 27개 조합과 문 닫힘 입력 | 사다리와 모방불가 상한 준수. unknown 은 별도 대기 | 같음 | `test_t04_f3_all_combinations` |
| T-05 | ⑤ A·H 의 12개 허용 조합과 잘못된 입력 | 정확한 합산, 허용 범위 밖 입력 거부 | 같음 | `test_t05_f5_grades` |
| T-06 | ⑦ 네 조합, unknown, 범위 밖 직접 입력 | 네 점수만 허용. 미확인·범위 밖 값 거부 | 구버전 `large\|yes` −3. 현행 −2, 범위 −2~0 | 구버전 `test_t06_f7_matrix`, 현행 `test_scorecard_fix52_schema.py` |
| T-07 | 영업현금흐름 100, 설비투자 120 과 원출처의 음수 지출 표현 | 정규화 후 FCF −20. 부호 역전·이중 차감 없음 | 같음 | `test_t07_fcf_sign_normalization` |
| T-08 | 누적·분기 혼재, 정정 공시, 연결·세그먼트 범위 혼재 | 검증된 변환만 허용하고 중복 TTM 차단 | **미구현.** 재무 관측을 직접 수집하기 전에 채운다(TODO.md) | — |
| T-09 | 런웨이 1·3년 직전·정확·직후, 제한 현금·중복 여신·예상 조달 | 경계 정확 적용, 쓸 수 없는 완충 제외 | 같음 | `test_t09_runway_boundaries` |
| T-10 | ⑨ 손실률 경계·BEP·방향 완화·FCF 0·G1 후속 게이트 | 결정 선택(C-05·C-06)과 일치. 하한 준수 | 구버전 하한 −5·밴드 −3/−4/−5. 현행 하한 −4·밴드 −2/−3/−4 | 구버전 `test_scorecard_calc.py` `TestF9`, 현행 `TestV17F9Rescaled` |
| T-11 | RPO 와 B종의 기간 차이, ARR 대체, B종 0·미확인, 미공시 중복 | 유효한 비교만 수행. 정책 미결 분기는 완료 처리하지 않음 | 같음 | `test_scorecard_calc.py` `TestF9`, `test_scorecard_missing_type.py` |
| T-12 | 규칙이 다른 두 실행, 미완료 기업, 동점 셋 | 추세로 섞지 않음. 미완료는 공식 순위 제외, 1·2·2·2·5 방식 | 같음 | `test_scorecard_calc.py` `TestAggregate` |
| T-13 | 체크리스트 누락, 근거 없는 적용 제외, 미수행 검토, 정성 판단 미입력 | 확정되지 않는다 | 같음 | 검증기: 체크리스트 23행·4 영역·검토자 없는 pass 차단 |
| T-14 | 승인 뒤 자료·규칙·판단·보고 내용 변경 | 승인과 리뷰가 무효가 된다 | 같음 | 검증기: review results_hash·draft_hash, approval hashes 비교 |
| T-15 | 같은 승인본 반복 실행 | 같은 점수·순위·출력, 이력 중복 없음 | 같음 | `render_csv.append_history` 중복 키 건너뜀 |
| T-16 | 확정 중 실패 | 최신 MD·HTML·CSV 가 서로 다른 실행을 가리키지 않는다 | 같음 | 빌더 사전 검증 실패 시 파일 미생성 |
| T-17 | 기준선 14사 이관 | 개별 점수와 합계 보존, 불일치·누락 원본 표시 | 이관 끝남 | `scorecard/baseline/v1.5/import-report.md` |
| T-18 | MD·HTML·CSV·카드·원자료·트리거·차트 | 숫자·단위·현재 기업 참조가 일치 | 같음 | draft 순위표 ↔ results 대조, HTML `data-company` 대조 |
| T-19 | HTML 스크립트와 실제 데스크톱·모바일 화면 | 표 잘림·빈 차트·산점도 겹침·근거 불릿 확인 | 같음 | Playwright 실측 |
| T-20 | 일반 종목 리포트 요건 유지 | 다른 미완료 실행이 간섭하지 않는다 | 종목 리포트 기능은 2026-09-30 에 지웠다. 실행 간 간섭 부분만 남는다(실행 잠금) | `tests/test_run_lock.py` |

## 9. 알려진 한계

코드를 고치거나 결과를 해석할 때 지금도 맞는 주의 사항이다.

| ID | 언제 | 내용 |
|---|---|---|
| RC3-06 | `decisions_applied` 를 근거로 무엇을 주장할 때 | **소비 증명이 아니다.** `results.decisions_applied` 는 run.json `decisions` 를 `id:choice` 로 옮긴 목록일 뿐이다(engine.py). 선택을 읽는 분기가 없거나(C-11) 현재 모드에서 효력이 없는(C-13 은 bands 모드 전용) 선택도 들어 있다. 적용 여부는 factor 산식·경고에서 확인한다. 소비 추적(선택마다 읽은 factor 기록)은 구현하지 않았다 |
| RC3-08 | 관측 kind·metric 의미를 스키마로 막으려 할 때 | **단어 의미는 스키마가 아니라 소비 코드가 막는다.** `metric=arr` 에 `kind=run_rate` 를 `actual` 로 바꿔도 스키마는 통과한다. 비상장 P2 보정의 `arr_growth` 는 `accepted_kinds: ["actual"]` 을 calc_f6_params 가 읽어 run_rate 를 거부한다. kind 를 새로 쓰는 소비자를 만들면 그 코드에 같은 거부를 넣는다 |
| 재빌드 | 승인 뒤 리뷰 파일을 고쳤을 때 | 승인 해시 여섯 가지에 `review.md` 는 들지 않아 승인은 유효하지만, HTML References 의 검토자·리뷰 유형은 빌드 시점의 리뷰 파일에서 읽는다. 리뷰 파일을 고쳤으면 빌드를 다시 돌린다. 같은 승인본이면 `history.csv` 에 행이 추가되지 않는다 |
