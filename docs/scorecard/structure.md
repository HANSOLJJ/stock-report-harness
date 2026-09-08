# AI 기업 분석 framework — 구조 확장 지침

- 작성일 2026-09-08. `design-guideline.md`(도메인 명세)의 짝이다. 이 문서는 요구 ID(D·F·Q·T·C)를 실제 모듈·파일·테스트에 연결한다.
- 기준 커밋 `0df7d6e`, 브랜치 `HANSOLJJ/worker`. 원본(`AI_company_analysis_factor/`)은 저장소 밖 읽기 전용이며 SHA-256 은 design-guideline 2.1절과 일치한다.

## 1. 유형 분기와 공통 진입점

| 항목 | stock_report (기존) | ai_scorecard (추가) |
|---|---|---|
| 판별 | `plan/<slug>.md` frontmatter `report_type` 없음 | `report_type: ai_scorecard`, slug 는 `ai-scorecard-` 접두 |
| 판별 코드 | `scripts/report_contract_lib.report_type_for()` — 알 수 없는 값은 ValueError 로 차단 | 동일 |
| 검증 | `validate_report_contract.validate_contract` 기존 로직 그대로 | 같은 함수가 `scorecard.validate.validate_scorecard` 로 위임 (`ValidationResult` 공유) |
| 빌드 | `build_report.build_report` 기존 로직 그대로 | 같은 함수가 `scorecard.render_html.build_scorecard` 로 위임. CLI `python scripts/build_report.py <slug>` 동일 |
| hero 이미지·뉴스 100건 | 필수 | 요구하지 않음 (`enforce-plan.sh` 가 plan 의 report_type 을 읽어 면제) |
| draft 숫자 마커 `[S1]` | 필수 (`enforce-citations.sh`) | 생성물이라 면제. 대신 draft frontmatter `results_hash` 가 results.json 과 결속되고 검증기가 순위표 행을 대조 |
| 투자 권유 표현 차단 | `forbid-financial-advice.sh` | 동일 적용 |
| 가격 공급 | yfinance | 실행 원자료(observations.json)만 사용. build 중 재수집 없음 (D-02, C-21) |

## 2. 파일 소유권과 저장 스키마

| 경로 | 소유 | 추적 | 내용 |
|---|---|---|---|
| `scorecard/rules/v1.5.json` | 규칙 담당 | git | factor 모드·범위, ⑥ 구간, ⑨ 게이트 정책, ③ 사다리, ⑤ 산식, ⑦ 매트릭스, 체크리스트 Q01~Q23, 결정 C-01~C-22 상태·선택지 |
| `scorecard/companies.json` | 통합 담당 | git | 안정 company_id, 표시명·별칭, 유형, 상장, 티커, share_basis, adr_ratio, 통화, 평가 범위 |
| `scorecard/baseline/v1.5/` | 이관 담당 | git | `scores.json`(점수·근거 불릿), `observations.json`, `triggers.json`, `import-report.md` |
| `scorecard/runs/<slug>/` | 실행 | git | `run.json`, `observations.json`, `judgments.json`, `sources.json`, `results.json`, `preview.md`, `approval.json` |
| `scorecard/history.csv` | 빌드 | git | 승인본 이력 (run_id, approval_id, 기업, F1~F9, 합계, 순위, 변동 원인) |
| `plan/ research/ drafts/ reviews/ output/` | 파이프라인 | ignore(기존 정책) | 생성물. 원본은 `scorecard/` 에만 둔다 (D-09) |

스키마는 `scripts/scorecard/schema.py` 가 엄격 파싱한다. 알 수 없는 키·범위 밖 점수·NaN/Infinity·빈 근거는 `SchemaError` 다.

| 객체 | 파일 | 필수 필드 |
|---|---|---|
| 관측 | observations.json items | observation_id, company_id, metric(카탈로그 `METRICS`), value, unit, as_of, kind, source_id, status(verified/legacy_unverified/not_disclosed/collection_failed/source_conflict/incompatible_basis/parse_failed), basis, raw, note |
| 판단 | judgments.json items | judgment_id, company_id, factor, kind(score/grade/criteria/matrix/paths/gate_inputs), score, inputs, evidence(비어 있으면 안 됨), reviewer, reviewed_at, status(new/carried), carried_from |
| 실행 | run.json | run_id(=slug), report_type, title, as_of, price_as_of, info_cutoff, rule_version, rule_hash, baseline_id, companies, decisions[{id, choice, rationale, decided_by, decided_at}], created_at, purpose, assumptions |
| 결과 | results.json | schema, run_id, input_hashes, decisions_applied, companies[{factors, moat, trap, total, complete, pending, rank}], ranking, population, pending_rule_decisions, results_hash |
| 승인 | approval.json | approval_id, approved_by, approved_at, hashes{rules, observations, judgments, run, results, draft} |

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
| 합산·동점 순위·미완료 제외 | `aggregate` | T-12 |
| 결정론·해시 | `engine.compute/load_results/recompute_matches` | validator "results deterministic recompute" |
| 기준선 이관 검산 (T-17) | `baseline_import` + `import-report.md` MD 대조 | 14사 match |
| 입력 검증 (T-03, T-05, T-06, R05, R06) | `schema.validate_*` | `TestReviewRegressions` |

`tests/test_scorecard_calc.py` 는 `python -m unittest discover -s tests -t .` 로 실행한다. 설계진행 검증 담당의 독립 재현 `validation/test_scorecard_review.py`(R01~R06, 10건)도 같은 코드로 통과해야 한다.

## 4. 미결 결정의 취급

`scorecard/rules/v1.5.json` 의 `decisions[].status == pending` 이고 `blocking: true` 인 항목(C-03, C-05, C-06, C-13, C-16)은 계산기가 해당 분기에서 `needs_rule_decision` 을 반환하고 기업을 공식 순위에서 제외한다. 실행 단위 `run.json.decisions` 에 `{id, choice, rationale, decided_by, decided_at}` 를 기록한 경우에만 그 실행에서 선택이 적용되며 results/preview/HTML 에 "실행 단위 결정"으로 표시된다. 규칙 파일의 status 를 `resolved` 로 바꾸는 것은 규칙 개정(새 버전)이다.

| ID | 계산기 동작 |
|---|---|
| C-03 | F2 paths 입력은 `activate_candidate_mapping` 선택 시에만 환산. 승계 score 는 경고와 함께 사용 |
| C-04 | G3 완충은 현금+확정 미인출 여신(기본 exclude). include_v15 도 숫자 관측만 산입 |
| C-05 | G1 실패 뒤 진단 점수가 다르면 대기. `diagnose_only`/`apply` 로 해소. 이미 하한 -5 면 불필요 |
| C-06 | 영업손실률 경계는 `proposed_v15_boundaries` 선택 시만 적용. BEP 후퇴 -5 는 원문 OR 조건 적용 + 경고 |
| C-13 | NTM proxy(`annual_weighted_proxy`)는 `accept_proxy_with_flag` 선택 시만 채점 |
| C-16 | G4 판정 불가(자료 없음·비교 가능성 미확인)는 `hold`/`downgrade` 선택 전까지 대기. 비상장 FCF 미공시 사유와는 중복 감점하지 않음 |
| C-20 | Anthropic 단일 분기 흑자는 TTM 부호로 쓰지 않음 → F9 pending_data |

## 5. 단계·상태·승인 흐름

```
init ──► plan/<slug>.md + scorecard/runs/<slug>/{run,observations,judgments,sources}.json
research ──► research/<slug>.md (observations_hash·judgments_hash 결속)
calculate ──► results.json(+results_hash) + preview.md ; 입력 해시가 바뀌면 이전 approval.json 자동 무효
draft ──► drafts/<slug>.md (results_hash 결속)
review-template ──► reviews/<slug>.md (4 영역 + Q01~Q23, status: needs_fix) → 리뷰어가 채움 → status: pass
approve --by <name> ──► approval.json (rules/observations/judgments/run/results/draft 해시 결합) — 사용자 행위
build_report.py ──► 승인 해시 == 현재 해시 검증 → output/<slug>.html → history.csv append(중복 방지) → 사후 검증
```

상태 이름: 자료 부족 `pending_data`, 판단 부족 `needs_judgment`, 규칙 미결 `needs_rule_decision`, 승인 필요 `awaiting_user`(빌더 메시지), 검토 미완 `needs_fix`(리뷰 frontmatter). 해시가 하나라도 바뀌면 검증기가 리뷰·승인을 무효로 판정한다(T-14). 같은 승인본 재빌드는 history.csv 에 행을 추가하지 않는다(T-15). 사전 검증 실패 시 HTML 을 쓰지 않으므로 최신 MD/HTML/CSV 가 갈라지지 않는다(T-16).

## 6. 산출물 렌더러

| 산출물 | 모듈 | 요구 |
|---|---|---|
| plan/research/draft/review 템플릿/preview | `render_md` | 9절 표. draft 필수 섹션 개요·종합 순위표·기업별 상세·지표 원자료·방법과 규칙·References |
| HTML 대시보드(단일 파일) | `render_html` | dashboard-design 스킬: 320px 리플로우, 표 모바일 패턴(합계 열만 + 첫 두 열 sticky + 행 탭→카드), 탭 대상 ≥24px, Pretendard 링크+폴백, 타입 스케일 토큰, 자체 팔레트(soft/line 짝), 인라인 style 없는 반응형, 산점도 결정론적 라벨 배치, aria-label |
| history.csv | `render_csv` | (run_id, approval_id, company_id) 중복 방지 |

HTML 검증(`scorecard.validate._validate_html`): generator 메타 `stock-report-harness scorecard-builder`, `results-hash` 메타, viewport, 면책 footer, 순위표 `data-company` 행, source marker 없음. Playwright 실측(2026-09-08): 320/768/769/1280 넘침 0건, 탭 대상 위반 0건, sticky 첫 열 유지, 행 탭 → 카드 열림.

## 7. 훅·명령·스킬

- 훅: `enforce-plan.sh`(scorecard 이미지 면제, review pass 는 유지), `enforce-citations.sh`(scorecard draft 건너뜀). 핵심 통제는 훅이 아니라 `scorecard_cli`·검증기·빌더가 직접 수행한다(설계 지침 4.3).
- 명령: `/score-plan`, `/score-research`, `/score-calculate`, `/score-draft`, `/score-review`, `/score-approve`, `/score-build`, `/score-goal` → `.claude/skills/score-*/SKILL.md`.
- Windows: `python` 실행 파일로 동작하며 `python3` 를 가정하지 않는다. 훅은 Git Bash + python3 별칭 환경에서 동작한다.

## 8. 회귀·수용 기준 매핑

| 검증 | 방법 |
|---|---|
| T-01~T-12 | `tests/test_scorecard_calc.py` |
| T-13 | 검증기: 체크리스트 23행·4 영역·검토자 없는 pass 차단 |
| T-14 | 검증기: review results_hash/draft_hash, approval hashes 비교 |
| T-15 | `render_csv.append_history` 중복 키 건너뜀 |
| T-16 | 빌더 사전 검증 실패 시 파일 미생성 |
| T-17 | `baseline/v1.5/import-report.md` 14사 match, 파싱 실패 목록 |
| T-18 | draft 순위표 ↔ results 대조, HTML `data-company` 대조 |
| T-19 | Playwright 실측 + `node --check` 상당(인라인 JS 는 정적 문자열) |
| T-20 | 기존 stock validator 경로 무변경 (report_type 없는 slug 는 기존 분기) |
