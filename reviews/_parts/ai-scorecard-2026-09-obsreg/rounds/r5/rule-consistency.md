# rule-consistency — 규칙 일관성
검토자: Gemini 3.8 Flash (High) · session 4f1c7d16 · 2026-09-16 15:00 KST
결과: pass
요약: factor 정의 및 상하한 범위, 스키마 강제성, 결정 반영 여부를 전수 검증했습니다. 체크리스트 8건의 fail은 모두 v1.5 승계 판단 논리에 기인하고 open_tensions에 등록되어 재검토 시점이 명시되어 있으므로 AGENTS.md 승계 판단 예외 규정에 따라 본 영역은 pass입니다.

## 결정 반영 대조
| 결정 | rules status | run.json | 코드 분기 | 결과 반영 | 판정 |
|---|---|---|---|---|---|
| C-01 | documented | 미등재 | 없음 | 낡은 안내 정리 문서화 완료 | pass (문서화) |
| C-02 | resolved | 미등재 | `rules.factors.*.mode` | factor 내부 입력·판정·환산 분리 완료 | pass (아키텍처 확정) |
| C-03 | resolved | `paths_with_generation_gap_5` | `calc_qual.py:39` | `results.json` decisions_applied 등재. 14개사 F2는 `kind="score"` 승계 점수라 사유 문구에 반영되고 점수는 승계값 보존 | pass (규칙 확정 및 점수 승계 보존) |
| C-04 | pending | 미등재 (기본 exclude) | `calc_f9.py:261` | `include_v15`와 기본 분기의 완충 산출식이 동일하여 읽지만 계산 미사용. run.json 미등재로 점수 영향 없음 | needs_attention (잠재 결함) |
| C-05 | pending | `apply` | `calc_f9.py:169, 186` | G1 실패 기업(alibaba, oracle, openai)의 G3·G4 진단 감점을 실제 점수에 적용 | pass (실제 반영) |
| C-06 | pending | `proposed_v15_boundaries` | `calc_f9.py:136` | G1 손실률 밴드 재척도 및 BEP 후퇴 감점(-4)에 실제 적용 | pass (실제 반영) |
| C-07 | pending | 미등재 | `calc_f9.py:315, 343` | ARR의 약정 대체 금지 및 incompatible_basis 차단 로직(double block) 유지 | pass (차단 반영) |
| C-08 | pending | 미등재 | 없음 | 코드가 읽지 않음. TEN-RC-03 긴장 등록 후 2026-11 재검토 이관 | pass (승계 긴장 예외) |
| C-09 | pending | 미등재 | 없음 | 코드가 읽지 않음. TEN-RC3-01 긴장 등록 후 2026-11 재검토 이관 | pass (승계 긴장 예외) |
| C-10 | documented | 미등재 | 없음 | 가격 설명 낡은 경계 정리 문서화 완료 | pass (문서화) |
| C-11 | resolved | `block_carryover` | 없음 | F7 엔진에 이월 경로가 없어 점수 무영향. Q22에 따라 방증 문구만 허용되고 산술 차단됨. 선언은 있으나 읽는 코드 부재 | pass (차단 유효, 코드 미호출) |
| C-12 | pending | `p2_with_capped_promotion` | `calc_f6_params.py:416` | 비상장 2사(anthropic, openai)의 P2 배수 및 보정 계산에 실제 적용 | pass (실제 반영) |
| C-13 | resolved | `reject_proxy` | `calc_f6.py:199` | 코드가 있으나 v1.7 parameters 모드에서는 calc_f6_params.py를 사용하여 미호출 경로. 점수 무영향 | pass (bands 모드 전용) |
| C-14 | documented | 미등재 | 없음 | 낡은 미래 점수 정리 문서화 완료 | pass (문서화) |
| C-15 | documented | 미등재 | 없음 | Meta 리스 개시 이중 계상 방지 문서화 완료 | pass (문서화) |
| C-16 | pending | `downgrade` | `calc_f9.py:353` | G4 확인된 미공시(not_disclosed_confirmed) 시 한 칸 하향(-1) 적용 | pass (실제 반영) |
| C-17 | documented | 미등재 | 없음 | 기준일·재무기간·컷오프 분리 문서화 완료 | pass (문서화) |
| C-18 | documented | 미등재 | 없음 | 참조 기업 분리 문서화 완료 | pass (문서화) |
| C-19 | documented | 미등재 | 없음 | 비교 문언 정리 문서화 완료 | pass (문서화) |
| C-20 | pending | `defer_to_private_g2` | `calc_f9.py:299` | 비상장 구조적 미공시 시 G1 보류 후 G2 비상장 경로 전송 | pass (실제 반영) |
| C-21 | documented | 미등재 | 없음 | 가격 공급 정책 문서화 완료 | pass (문서화) |
| C-22 | documented | 미등재 | 없음 | 총점 산식 음수 함정 명문화 완료 | pass (문서화) |
| C-23 | pending | 미등재 | 없음 | 미인출 여신 만기 요건 미결, 점수 무영향(amazon 런웨이 여유) | pass (점수 무영향) |

## 체크리스트
| ID | 결과 | 근거(파일:행) · fail 이면 회사 |
|---|---|---|
| Q01 | fail | nvidia, tesla. nvidia는 F5 H-2(고객 40% 자체 칩)와 F8 -3(고객 40% 집중 및 자체 칩)에서 동일 속성이 중복 감점되었고(`judgments.json:nvidia.F5`, `judgments.json:nvidia.F8`), tesla는 F5 H-1(NHTSA 조사)과 F8 -2(NHTSA 조사)에서 동일 규제 위험이 중복 감점되었습니다(`judgments.json:tesla.F5`, `judgments.json:tesla.F8`). 두 건 모두 승계 판단 예외 규정(TEN-RC-05, TEN-RC3-04)에 해당합니다. |
| Q02 | fail | anthropic, openai, palantir, oracle, alibaba. anthropic.F1은 주채널을 업무로 적고도 개인 사용자 열세로 감점(`v1.7.json:1788`), openai.F1은 소비자 주채널에 거래 채널 지표로 감점(`v1.7.json:2081`), palantir·oracle은 업무 채널 전환비용을 비대칭 인정(`v1.7.json:1960`), alibaba.F3은 경쟁사 2곳 오픈웨이트에도 모방불가 partial 부여(`v1.7.json:2008`). 전부 승계 판단 예외 규정(TEN-RC-02, TEN-RC4-02, TEN-RC3-03, TEN-RC3-05)에 해당합니다. |
| Q03 | fail | nvidia, amazon, meta, spacex-xai, anthropic, openai, palantir, oracle. F5 별표 H 이탈 조건 불통일(`v1.7.json:1812`), spacex-xai.F5 H의 단순 수 비교(`v1.7.json:2104`), anthropic·openai F7 매트릭스 입력 누락(`v1.7.json:1938`), palantir·oracle F1 전환비용 불일치(`v1.7.json:1960`). 전부 승계 판단 예외 규정(TEN-RC-03, TEN-RC4-03, TEN-RC3-01, TEN-RC3-03)에 해당합니다. |
| Q07 | pass | `judgments.json` 전사 F3 검토. amazon은 매대 수수료 모델, apple은 자사 칩 및 온디바이스 에코시스템으로 검토하여 모델 미개발 자체를 카운터 포지셔닝으로 인정한 기업이 없습니다. |
| Q08 | fail | spacex-xai. spacex-xai.F5의 H=-1 판정 근거에 '동맹이 적보다 확실히 많지 않음'이라는 단순 수 비교 문언이 기재되어 있습니다(`judgments.json:spacex-xai.F5`, `v1.7.json:2104`). 승계 판단 예외 규정(TEN-RC4-03)에 해당합니다. |
| Q12 | pass | `v1.7.json:103` 및 `scripts/scorecard/calc_qual.py:compute_f3`. 모방 불가능성 완전 pass(requires_imitation_pass)가 없는 경우 상한 3점 규칙이 14개사 전원에 철저히 적용되어 F3 4점 이상을 받은 기업이 전무합니다(전원 2점 또는 3점). |
| Q13 | fail | alibaba, meta. alibaba.F3 근거란에 오픈웨이트 회수 장치 부재를 자인하고도 partial을 부여했고(`v1.7.json:2008`), meta.F3도 무료 배포 Llama의 복제 가능성에도 partial을 부여했습니다(`v1.7.json:2055`). 승계 판단 예외 규정(TEN-RC3-05, TEN-RC4-01)에 해당합니다. |
| Q15 | pass | `judgments.json` alibaba.F5(파생모델 15만 개 불인정), nvidia.F5(개발자 1,800만 명 불인정), meta.F5(Glimmer 개발자 불인정). 14개사 전사에서 공짜 사용자를 상업 동맹으로 인정한 사례가 없습니다. |
| Q16 | fail | anthropic, openai. anthropic.F1은 업무 주채널을 소비자 지표로 깎았고(`v1.7.json:1788`), openai.F1은 소비자 주채널을 거래 채널 지표로 깎았습니다(`v1.7.json:2081`). 승계 판단 예외 규정(TEN-RC-02, TEN-RC4-02)에 해당합니다. |
| Q17 | pass | `judgments.json` 전사 F2 검토. 세 경로 중 하나(성능 도약 세대 격차 등)만 충족해도 점수가 부여되었으며(nvidia 5, anthropic 5), 표준 부재만으로 감점된 기업이 없습니다. |
| Q18 | pass | `judgments.json:tesla.F5` 및 `judgments.json:spacex-xai.F5`. Tesla와 SpaceX는 동일 지배주주 아래 관계사이므로 상호 독립 동맹에서 제외하여 Tesla A=0, SpaceX에서도 Tesla를 동맹에서 배제했습니다. |
| Q19 | pass | `judgments.json:anthropic.F5.impl48` 및 `judgments.json:openai.F5.impl48`. FIX-53/F5-IMPL-48 재판정을 통해 피투자 관계(Amazon/Google/MS 투자)와 조달 관계(Oracle $300B)를 배제하고 능동적 상업 제휴만 인정하여 두 회사 모두 A를 +2에서 +1로 정상 정정했습니다. |
| Q20 | fail | nvidia, amazon, meta. 별표 H 3문(상대가 떠날 수 있으면 동맹 제외) 원칙과 달리 Amazon Bedrock 입점사 및 Meta 광고주는 동맹으로 가점하고 NVIDIA 하이퍼스케일러는 제외하는 등 조달과 동맹의 이탈 기준이 전사에 통일되지 않았습니다(`v1.7.json:1812`). 승계 판단 예외 규정(TEN-RC-03)에 해당합니다. |
| Q21 | fail | nvidia, tesla. nvidia는 F5 H-2와 F8 -3에서 '고객 40% 자체 칩 이탈' 속성이 중복되었고(`v1.7.json:1868`), tesla는 F5 H-1과 F8 -2에서 'NHTSA 조사' 규제 속성이 중복되었습니다(`v1.7.json:1985`). 승계 판단 예외 규정(TEN-RC-05, TEN-RC3-04)에 해당합니다. |
| Q22 | pass | `v1.7.json:1482` 및 `scripts/scorecard/calc_qual.py`. C-11 block_carryover 및 carryover_scope 명문화에 따라 지분 평가이익은 F7의 두 축 입력 및 점수 산술에서 완전 배제되었으며, 고객사 관련 일부 서술란에 방증 문구로만 기재되었습니다. |

## 발견 사항
- [severity: medium] `scripts/scorecard/calc_f9.py:261` — C-04 결정 읽지만 계산 미사용 결함 — `calc_f9.py:261-266`에서 `decision_choice(run, rules, "C-04")`를 읽어 `capacity_choice == "include_v15"` 분기로 갈라지지만, 양쪽 분기 모두 완충 계산식이 `runway = _runway(cash, undrawn or 0.0, -fcf)`로 동일하여 점수에 영향이 없고 경고 문자열만 다릅니다. 규칙 파일 `v1.7.json:1356`에서도 스스로 인정한 결함이며, 이번 실행은 `run.json`에 C-04가 등재되지 않아 기본값(exclude)으로 작동하므로 점수 왜곡은 없습니다.
- [severity: low] `scorecard/runs/ai-scorecard-2026-09-obsreg/run.json:73` — C-11 결정 선언되었으나 읽는 코드 부재 — `run.json.decisions`에 `C-11: block_carryover`가 명시되어 있으나 코드베이스 전체에 `decision_choice(run, rules, "C-11")` 호출이 없습니다. F7 계산기는 원래 2축 매트릭스만 읽어 이월 경로 자체가 없으므로 점수 왜곡은 없으나, 실행 단위 결정에 선언된 항목을 코드가 소비하지 않는 불일치가 있습니다.
- [severity: low] `scripts/scorecard/calc_f6.py:199` — C-13 결정 코드 존재하나 v1.7 parameters 모드에서는 미호출 경로 — `run.json.decisions`에 `C-13: reject_proxy`가 있고 `calc_f6.py:199`에 분기 코드가 존재하지만, v1.7 정본 실행은 `calc_f6_params.py`를 사용하므로 bands 모드 전용인 `calc_f6.py`는 호출되지 않습니다. 점수에는 영향이 없습니다.
- [severity: low] `scorecard/rules/v1.7.json:66` — F3 factor range 하한(1)과 사다리 최저 실측(2) 간의 불일치 잔존 — F2는 C-03 확정으로 사다리 바닥인 2에 맞춰 `range: [2, 5]`로 정정되었으나, F3는 정의상 1점 칸(points 0 -> 1)이 있으나 14개사 실측 최저가 2점이라 1점 칸을 쓰지 못하는 미정리 상태가 유지되고 있습니다.

## 확인 못 한 것
- 비상장 2사(Anthropic, OpenAI)의 F7에 v1.5에서 두 축 입력 없이 승계된 -1 점수의 원문 상류(실제 환류 루프 존재 여부)는 외부 조회 금지 규칙 및 저장소 내 원문 미기재로 인해 독립 확인하지 못했습니다(TEN-RC3-01 소관).
- NVIDIA와 Tesla의 F5/F8 중복 계상(TEN-RC-05, TEN-RC3-04)에서 해당 속성이 각각 몇 점의 감점을 만들어냈는지 수동 판단 분해가 없어 중복 감점 폭을 독립 확인하지 못했습니다.
