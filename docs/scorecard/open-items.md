# AI Scorecard — 남은 작업

작성일 2026-09-08. 기준 커밋 `7a05b3d`, 브랜치 `HANSOLJJ/worker`.

이 문서는 **처리하지 않고 남겨둔 항목**만 모은다. 처리한 항목은 커밋 메시지와 `reviews/<slug>.md` 에 있고, 설계·구조 계약은 `design-guideline.md` 와 `structure.md` 에 있다.

## ID 주의

설계 지침의 설계 원칙 **D-01~D-10** 과 아래 검증 담당 보고서의 항목 번호 **D-01~D-13** 은 **서로 다른 체계인데 번호가 겹친다.** 이 문서에서는 출처를 앞에 붙여 `REVIEW-03/D-06` 처럼 쓴다. 설계 원칙을 가리킬 때는 접두 없이 `D-06` 으로 쓴다.

## 출처

검증 담당(설계진행 Codex)의 보고서 원문은 이 저장소가 아니라 다른 worktree 에 있다.

| 보고 | 원문 | 재현 스크립트 |
|---|---|---|
| SCORECARD-REVIEW-02 | `설계진행/validation/qwen-recheck.md` | `recheck_qwen.py` |
| SCORECARD-REVIEW-03 | `설계진행/validation/cli-doc-recheck.md` | `recheck_cli_doc.py` |
| SCORECARD-REVIEW-01 | Orca 스레드 `msg_32b69fde6c6f` | `설계진행/validation/test_scorecard_review.py` |

## 1. 사용자 결정 대기 — 규칙

계산기가 막고 있는 항목이다. `scorecard/runs/<slug>/run.json` 의 `decisions` 에 `{id, choice, rationale, decided_by, decided_at}` 를 넣어야 그 실행에서 적용된다.

| ID | 선택지 | 정하면 달라지는 것 |
|---|---|---|
| C-06 | `proposed_v15_boundaries` | SpaceX 영업손실률 -14.9% 가 -4 로 확정(기준선 재현). 단독으로는 SpaceX 를 순위에 넣지 못하고 C-05 가 함께 필요 |
| C-13 | `accept_proxy_with_flag` / `reject_proxy` | 수용하면 TSMC 가 조정 14 로 순위 편입, 거절하면 TSMC·Alibaba 가격이 자료 대기로 확정 |
| C-05 | `diagnose_only` / `apply` | C-06 과 함께 정하면 SpaceX 완료(조정 6) |
| C-16 | `hold` / `downgrade` | 확인된 미공시의 약정 커버리지 처리. 현재 실행에는 걸리는 기업 없음 |
| C-03 | `activate_candidate_mapping` | F2 경로 수→점수 환산. 현재 14사 전부 승계 점수라 안 걸림 |

비차단 결정 7건은 `scorecard/rules/v1.5.json` 의 `decisions` 참조: C-04, C-07, C-08, C-09, C-11, C-12, C-20.

### 결정 전에 같이 볼 것

- **경계값 방향이 factor 마다 반대다.** ⑥ 은 정확히 20 인 값을 더 나쁜 칸(-1)에 붙이고, ⑨ 제안 경계는 정확히 -10% 인 값을 덜 나쁜 칸(-3)에 붙인다. 실무에서 걸릴 확률은 낮지만 같은 잣대 원칙(Q03)에 어긋난다.
- **C-06 은 다섯 항목의 묶음이다.** `proposed_v15_boundaries` 를 골라도 손실률 경계 하나만 정해진다. FCF 0, 영업손익 0, 완충 잠식 정의, G2 안정·악화 정의는 남는다. 이번 실행에 해당 기업이 없어 드러나지 않을 뿐이다. 결정을 쪼갤지 판단이 필요하다.
- **TSMC 근사값 19.4 는 구간 경계 20 에서 3% 안쪽이다.** 산출 방법이 바뀌면 0 과 -1 이 뒤집힌다. 근사 수용은 기준선 재현에는 맞지만 신규 채점에는 위험하다.

## 2. 자료·판단 대기 — 규칙이 아님

| 기업 | 막힌 것 | 필요한 것 |
|---|---|---|
| Amazon | ⑨ 약정 커버리지 | AWS 백로그와 미개시 리스 $106B 가 같은 범위·기간인지 사람의 판정(`coverage_comparable`) |
| Alibaba | ⑨ G1 | TTM 영업손익 관측. 원문은 단일 분기 흑자 전환뿐이라 C-20 잣대로 부호 미확인 |
| Anthropic | ⑨ G1 | 위와 같음 |

## 3. 문서 보완 — REVIEW-03

| ID | 내용 |
|---|---|
| REVIEW-03/D-03 | `init --help` 에 이미 있는 `--price-as-of`·`--info-cutoff`·`--baseline`·`--rule` 의 의미와 기본값을 README·`score-plan` 스킬에 설명. 기능 부재가 아니라 설명 부재 |
| REVIEW-03/D-06 | npm 스크립트가 `python3` 와 `python` 을 혼용한다. 훅은 `python3` 별칭을 요구하므로 그 전제를 README 에 명시. 전역 일괄 치환은 하지 않는다 |
| REVIEW-03/D-07 | Python CLI 의 `--by` 는 필수인데 slash command hint 는 선택처럼 보인다. `/score-approve` 안내에 실제 승인자 확보 절차를 적는다 |
| REVIEW-03/D-08 | 기본 이관 원본 경로가 특정 머신의 `E:` 경로다. `--html`·`--md` 로 바꿀 수 있고 기준선이 커밋돼 있어 최초 실행에 재이관이 필수가 아니라는 두 사실을 README 에 명시 |
| REVIEW-03/D-09 | `status` 명령을 README 사용 흐름에 추가. 단 `approval_valid` 는 해시 일치만 보므로 전체 계약 검증의 대체가 아님을 함께 적는다 |
| REVIEW-03/D-10 | 빌더가 `run.change_type` 을 읽지만 run 스키마가 그 키를 거부해 이력 사유가 `baseline-recompute` 로 고정된다. 이번 기준선에는 맞지만 **다음 재채점 전에 계약을 보완해야 한다** |

`REVIEW-03/D-11`(AGENTS 제목 손상)은 base `0df7d6e` 부터 있던 stock 쪽 문제라 이번 범위에서 제외했다. `REVIEW-03/D-12`(plan 부재 시 init 안내)는 선택 사항이다. `REVIEW-03/D-13`(C-20 을 실행 선택지로 만들자)은 기각했다. C-20 은 선택지가 아니라 TTM 자료를 확보할 문제다.

## 4. 기능 활성화 전 계약 요구 — REVIEW-02

지금 결함이 아니라, 해당 기능을 켤 때 채워야 하는 것이다.

| ID | 언제 | 내용 |
|---|---|---|
| REVIEW-02/P2 | 트리거를 원문 보존용에서 활성 트리거로 전환할 때 | 트리거마다 대상 기업·factor·조건·출처를 구조화한다. 현재 39건은 `status=legacy` 로 원문 문장만 보존하며 표에 과거 기록으로 표시된다 |
| REVIEW-02/P6 | 재현성을 더 올릴 때 | 관측별 원문 행·열 위치(locator)를 구조화한다. 현재도 출처 ID·문서 제목·해시는 있어 추적이 끊기지는 않는다 |
| REVIEW-02/P7 | F2 를 신규 판정할 때 | 설계 지침 4.3 의 평가기관·평가일·모델/제품 버전·지수 버전·하네스·모집단·순위·측정값을 관측으로 받는다. 현재 F2 는 전부 승계 점수이고 신규 경로 매핑은 C-03 미결로 차단돼 있다 |

## 5. 테스트 미구현

| ID | 내용 |
|---|---|
| T-08 | YTD·분기 혼재, 정정 공시, 연결/세그먼트 범위 혼재 검증. 이관 자료에 해당 사례가 없어 아직 없다. 신규 재무 관측을 직접 수집하기 전에 채운다 |

## 6. 승인된 실행의 취급

`ai-scorecard-2026-09-baseline` 은 승인·빌드가 끝난 스냅샷이다. 이후의 이관기·스키마 수정은 **다음 `init` 부터** 반영되며 이 실행을 재계산하지 않는다. 승인은 규칙·자료·판단·결과·초안 해시에 결합돼 있고, 스키마 변경은 기존 데이터와 호환되게 만들어(상태 추가는 허용 집합 확대, `period` 필수는 `verified` 에만) 검증기가 계속 통과한다.

이 실행에 반영하려면 새 실행을 만들어야 한다. 그 경우 리뷰와 승인을 다시 받는다.
