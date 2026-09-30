# rule-consistency — 규칙 일관성
검토자: Gemini 3.8 Flash (High) · 독립 리뷰 세션 (rule-consistency) · 2026-09-16
결과: pass
요약: 14개사의 9개 factor 점수가 v1.7.json의 range 내에 완전 일치하며, FIX-56에 따른 C-24 반영(spacex-xai P2 계산 및 F6 -3, 총점 9)과 F5 전사 엄격 잣대(Anthropic·OpenAI·TSMC A+1 재판정)가 규칙과 정합합니다. 담당 체크리스트 15개 항목은 모두 pass이며(승계 판단에 기인한 기존 fail은 open_tensions에 등록되어 승계 판단 예외 규정에 따라 pass를 저해하지 않음), scope_separation·two_axes·banned_word 스키마 강제가 메모리 변조 검증을 통해 실증되었습니다.

## 결정 반영 대조
| 결정 | rules status | run.json | 코드 분기 | 결과 반영 | 판정 |
|---|---|---|---|---|---|
| C-01 | documented | 없음 | 없음 | 지침 문서화 기록용 | 적정 |
| C-02 | resolved | 없음 | 없음 | 수동 vs 자동 경계 문서화 기록용 | 적정 |
| C-03 | resolved (paths_with_generation_gap_5) | paths_with_generation_gap_5 | calc_qual.py:39 | carried_score 보존 및 warnings 기록 | 적정 |
| C-04 | pending | 없음 | calc_f9.py:267 | 미지정 시 정책 기본값(include_v15) 사용, 점수 영향 없음 | 적정 |
| C-05 | pending | apply | calc_f9.py:169, 186 | G1 실패 후 G3·G4 감점 적용에 반영 | 적정 |
| C-06 | pending | proposed_v15_boundaries | calc_f9.py:136 | G1 영업손실률 밴드 경계(-10%·-30%) 및 바닥 -4 적용 | 적정 |
| C-07 | pending | 없음 | 없음 (주석 참조) | ARR 대체 금지 자료 대기 판정 유지 | 적정 |
| C-08 | pending | 없음 | 없음 | 별표 H 이탈 조건 미결 유지 (TEN-RC-03 긴장 등록) | 적정 |
| C-09 | pending | 없음 | calc_qual.py:158 | 매트릭스 입력 부재로 승계 점수 기준선 표시 (TEN-RC3-01 긴장 등록) | 적정 |
| C-10 | documented | 없음 | 없음 | 가격 경계 트리거 문서화 | 적정 |
| C-11 | resolved (block_carryover) | block_carryover | 없음 (F7 엔진 원래 분기 없음) | nonop_share의 F7 이월 차단 | 적정 |
| C-12 | pending | p2_with_capped_promotion | calc_f6_params.py:477 | 비상장 F6 P2 배수 및 P3·P4 보정 경로 반영 | 적정 |
| C-13 | resolved (reject_proxy) | reject_proxy | calc_f6.py:202 | parameters 모드로 구동되어 bands 전용인 C-13 미실행(점수 무영향) | 적정 |
| C-14 | documented | 없음 | 없음 | 낡은 점수 잔존 문서화 | 적정 |
| C-15 | documented | 없음 | 없음 | A종 이중 계상 충돌 문서화 | 적정 |
| C-16 | pending | downgrade | calc_f9.py:359 | 확인된 미공시로 G4 판정 불가 시 1칸 하향 적용 | 적정 |
| C-17 | documented | 없음 | 없음 | 기준 시점 분리 기록 문서화 | 적정 |
| C-18 | documented | 없음 | 없음 | 참조 기업 범위 문서화 | 적정 |
| C-19 | documented | 없음 | 없음 | 낡은 비교 문장 정정 문서화 | 적정 |
| C-20 | pending | defer_to_private_g2 | calc_f9.py:305 | 비상장 TTM 구조적 미공시 시 G1 보류 후 G2 경로 분기 반영 | 적정 |
| C-21 | documented | 없음 | 없음 | 가격 공급 정책 문서화 | 적정 |
| C-22 | documented | 없음 | 없음 | 총점 음수 설명 문서화 | 적정 |
| C-23 | pending | 없음 | 없음 | 런웨이 미인출 여신 잔존기간 요건 미결 유지 | 적정 |
| C-24 | resolved (compute_p2_when_inputs_exist) | compute_p2_when_inputs_exist | rules 정책(listed_newly parameters)으로 반영 | spacex-xai P2(80.27) 산출되어 F6 -1에서 -3으로 반영 | 적정 |
| C-25 | pending | 없음 | 없음 | 신규 상장 트랙 바닥 -3 적정성 미결 등록 | 적정 |

## 체크리스트
| ID | 결과 | 근거(파일:행) · fail 이면 회사 |
|---|---|---|
| Q01 | pass | `scorecard/rules/v1.7.json:44`, `scorecard/runs/ai-scorecard-2026-09-obsreg/judgments.json`. 동일 감점 속성의 다중 계상 없음. (승계 판단 예외: fail 2건 — TEN-RC-05 nvidia F5/F8, TEN-RC3-04 tesla F5/F8. 모두 open_tensions 등록) |
| Q02 | pass | `scorecard/rules/v1.7.json:37-210`, `scripts/scorecard/calc_f6_params.py:218-330`, `scripts/scorecard/calc_f9.py:90-370`. 각 factor 정의에 부합하는 지표만 투입됨. (승계 판단 예외: fail 5건 — TEN-RC-02 anthropic F1, TEN-RC3-01 anthropic·openai F7, TEN-RC3-03 palantir·oracle F1, TEN-RC3-05 alibaba F3, TEN-RC4-02 openai F1) |
| Q03 | pass | `scorecard/rules/v1.7.json:188-210`, `judgments.json` F5 전사 엄격 잣대(Anthropic·OpenAI·TSMC A+1, Alphabet·Amazon·Microsoft A+2) 일관 적용, FIX-56 C-24 spacex-xai P2 계산 적용. (승계 판단 예외: fail 4건 — TEN-RC-03 별표 H 이탈 조건, TEN-RC3-01 F7 매트릭스 입력, TEN-RC3-03 F1 업무 채널 잣대, TEN-RC4-03 spacex-xai F5) |
| Q07 | pass | `scorecard/runs/ai-scorecard-2026-09-obsreg/judgments.json` amazon.F3, apple.F3 evidence. 모델을 안 만든 것 자체를 카운터 포지셔닝으로 인정한 회사 없음. |
| Q08 | pass | `AI기업_채점규칙_v1.5.md:171-179`, `judgments.json` apple.F5(비용형 H=-1), nvidia.F5(구조형/존립위협 H=-2). 적대세력의 수가 아닌 성격으로 판정. (승계 판단 예외: TEN-RC4-03 spacex-xai F5) |
| Q12 | pass | `scorecard/rules/v1.7.json:101-105`, `scripts/scorecard/calc_qual.py:125-145`, `judgments.json` tesla.F3, spacex-xai.F3. 모방 불가능성 게이트(requires_imitation_pass)를 4점 이상에 필수 적용. (승계 판단 예외: TEN-RC4-01 meta·anthropic·spacex-xai F3 imitation=partial 정의 미충족) |
| Q13 | pass | `AI기업_채점규칙_v1.5.md:별표 B`, `judgments.json` alibaba.F3(회수 장치 부재로 불인정), meta.F3(광고 기반 회수 장치 인정). 공짜 배포를 곧바로 카운터 포지셔닝으로 인정하지 않음. (승계 판단 예외: TEN-RC4-01 meta) |
| Q15 | pass | `AI기업_채점규칙_v1.5.md:198`, `judgments.json` nvidia.F5(CUDA 개발자 1,800만 제외), alibaba.F5(파생모델 15만 제외), meta.F5(오픈웨이트 개발자 제외). 공짜 사용자를 아군으로 계상한 사례 없음. |
| Q16 | pass | `scorecard/rules/v1.7.json:46`, `AI기업_채점규칙_v1.5.md:별표 A`, `judgments.json` F1 항목들. 모든 실질 채널을 보고 가장 강한 락인으로 평가. (승계 판단 예외: fail 2건 — TEN-RC-02 anthropic F1, TEN-RC4-02 openai F1) |
| Q17 | pass | `scorecard/rules/v1.7.json:59`, `scripts/scorecard/calc_qual.py:30-115`. 게임체인저 세 경로(성능 도약, 패러다임 적응, 표준 선점) 중 하나라도 충족 시 인정하며 표준 부재만으로 깎지 않음. |
| Q18 | pass | `AI기업_채점규칙_v1.5.md:199`, `judgments.json` tesla.F5(SpaceX 제외 A=0), spacex-xai.F5(Tesla 제외). 관계사를 독립 동맹으로 센 사례 없음. |
| Q19 | pass | `scorecard/rules/v1.7.json:188-195`, `judgments.json` anthropic.F5, openai.F5, tsmc.F5. F5-IMPL-48 및 A-STRICT-54에 따라 피투자 관계 전면 배제 및 A+1 재판정 적용 완료. 받은 투자를 동맹 +2로 센 회사 없음. |
| Q20 | pass | `AI기업_채점규칙_v1.5.md:197, 233-240`, `judgments.json` apple.F5(Gemini 조달 배제), meta.F5(칩 조달 배제), openai.F5(Oracle $300B 조달 배제). 단순 조달을 동맹으로 계상하지 않음. (승계 판단 예외: TEN-RC-03) |
| Q21 | pass | `AI기업_채점규칙_v1.5.md:253-268`, `judgments.json` anthropic(⑤ 유통 동맹 vs ⑧ 의존 위험 분리), openai(⑤ 동맹 vs ⑧ 의존 위험 분리). 동일 관계라도 속성이 다르면 양쪽에 각각 반영. (승계 판단 예외: fail 2건 — TEN-RC-05 nvidia, TEN-RC3-04 tesla) |
| Q22 | pass | `scorecard/rules/v1.7.json:165-184`, `judgments.json` F7 전 항목. 지분 평가이익을 ⑦ 순환금융 점수 계산 매트릭스에 반영하지 않고 두 축(조달 의존 고객 비중, 환류 여부)으로만 산출함. |

## 발견 사항
- [severity: low] `scorecard/rules/v1.7.json:decisions.C-24` 및 `scripts/scorecard/calc_f6_params.py:341-350` — C-24(신규 상장 트랙 P2 계산)가 run.json.decisions에 등록되고 results.json.decisions_applied에 기록되었으나, 코드 내 decision_choice(run, rules, "C-24") 호출 분기는 없습니다. 대신 v1.7.json의 f6.tracks.listed_newly 정책(parameters에 P2 추가, optional_parameters에 P2 지정)을 엔진이 직접 읽어 계산에 반영했습니다. run.json의 선택지(p3_only_v17 등) 변경 시 코드 분기가 작동하지 않는 한계가 있으나 현재 계산 결과 자체는 정합합니다.
- [severity: low] `scorecard/rules/v1.7.json:decisions.C-13` 및 `scripts/scorecard/calc_f6.py:202` — C-13(근사 NTM PER 배제)은 run.json.decisions에 포함되어 있으나, 현 실행은 v1.7 parameters 모드(calc_f6_params.py)로 구동되어 calc_f6.py의 decision_choice("C-13") 분기가 실제로 실행되지 않습니다. run.json의 rationale에도 명시되어 점수 영향은 없습니다.
- [severity: low] `scorecard/rules/v1.7.json:decisions.C-11` — C-11(nonop_share의 F7 이월 차단)은 run.json.decisions에 포함되어 있으나 코드 분기가 없습니다. F7 엔진이 원래 nonop_share를 읽지 않으므로 계산상 안전합니다.
- [severity: medium] `scorecard/rules/v1.7.json:decisions.C-25` 및 `scorecard/rules/v1.7.json:policies.f6.tracks.listed_newly.floor` — C-24 적용으로 spacex-xai의 P2(80.27, 밴드 -2)가 계산되면서 F6가 -3이 되었고, 트랙 바닥(floor: -3)에 도달했습니다. 일반 상장 트랙의 floor가 -7인 것에 비해 신규 상장 트랙의 바닥이 -3으로 고정되어 있어 추가 감점 요인 발생 시 비대칭이 발생할 수 있습니다(미결 C-25 등록).

## 확인 못 한 것
- SEC 제출물 원문 원천의 회계 수치(10-K, 10-Q 원문)의 산술적 진위는 재무 계산 및 사실·출처 영역의 분담이므로 규칙 일관성 검토에서는 규칙 및 관측 간 매핑과 논리적 범위 정합성만 검증하고 외부 원문을 독립 재검토하지 않았습니다.
- 비상장 2사(Anthropic, OpenAI)의 미공시 재무 추정치(내부 ARR, 밸류에이션 등)의 원천 진위는 주어진 관측과 v1.5 원본 문언 범위 내에서만 일관성을 대조했습니다.
