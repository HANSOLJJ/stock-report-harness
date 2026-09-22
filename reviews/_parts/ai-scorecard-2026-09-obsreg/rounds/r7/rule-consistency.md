# rule-consistency — 규칙 일관성
검토자: Gemini 3.8 Flash · 세션 49475e60-f29b-4a83-ab54-22fc6d4cf615 · 2026-09-16T18:56:00+09:00
결과: pass
요약: 14개사 모든 factor 점수(F1~F9)가 규칙 허용 범위에 부합하고, `working_definition` 스키마 강제 검증을 통과했습니다. 체크리스트 상의 일부 fail 항목은 모두 `open_tensions`에 등록된 승계 판단 예외 규정을 충족하여 최종 pass로 판정합니다.

## 결정 반영 대조
| 결정 | rules status | run.json | 코드 분기 | 결과 반영 | 판정 |
|---|---|---|---|---|---|
| C-01 | documented | 미등재 | 없음 | 문서화 전용(설계 지침 4절) | pass |
| C-02 | resolved | 미등재 | factor별 mode 분기 구조(`scripts/scorecard/rules.py:120`) | 입력→판정→환산 분리 적용 | pass |
| C-03 | resolved | `paths_with_generation_gap_5` | `scripts/scorecard/calc_qual.py:39` `decision_choice(...)` | 14개사 F2가 전부 carried_score라 `_f2_generation_gap` 분기를 타지 않고 승계 점수 반환(점수 불변) | pass |
| C-04 | pending | 미등재 | `scripts/scorecard/calc_f9.py:273` | run 미등재로 `policies.f9.g3_rating_capacity` 기본값(exclude) 적용 | pass |
| C-05 | pending | `apply` | `scripts/scorecard/calc_f9.py:175, 192` `decision_choice(...)` | G1 실패 기업(SpaceX-xAI, Anthropic, OpenAI)에 G3/G4 진단 및 점수 반영 | pass |
| C-06 | pending | `proposed_v15_boundaries` | `scripts/scorecard/calc_f9.py:142` `decision_choice(...)` | G1 밴드 재척도(-2/-3/-4) 및 floor -4, relief_cap -2 적용 | pass |
| C-07 | pending | 미등재 | `scripts/scorecard/calc_f9.py:350` | 범위 불일치는 자료 대기로 분기(Anthropic G4) | pass |
| C-08 | pending | 미등재 | 없음 | Q19 체크리스트와 조합되어 OpenAI/Anthropic F5 A=+1 재판정에 실질 반영 | pass |
| C-09 | pending | 미등재 | `scripts/scorecard/calc_qual.py:157` | 매트릭스 입력 복원 전까지 승계 점수 -1 유지(`TEN-RC3-01`) | pass |
| C-10 | documented | 미등재 | 없음 | 문서화 전용 | pass |
| C-11 | resolved | `block_carryover` | 없음(`scripts/scorecard/rules.py` 내 `decision_choice` 호출 0건) | 선언만 있고 소비자가 없는 형태(`declared_without_consumer`). F7 계산기가 원래 영업외 비중을 안 읽어 점수 왜곡 없음 | pass |
| C-12 | pending | `p2_with_capped_promotion` | `scripts/scorecard/calc_f6_params.py:477` `decision_choice(...)` | 비상장 2사 F6 P2 배수 계산 및 P3/P4 조건 검증 반영(배수 -4, 보정 미충족으로 F6=-4) | pass |
| C-13 | resolved | `reject_proxy` | `scripts/scorecard/calc_f6.py:202`(bands 모드 전용) | v1.7 parameters 모드에서는 NTM PER을 쓰지 않아 무소비(`run.json:82`) | pass |
| C-14 | documented | 미등재 | 없음 | 문서화 전용 | pass |
| C-15 | documented | 미등재 | 없음 | 문서화 전용 | pass |
| C-16 | pending | `downgrade` | `scripts/scorecard/calc_f9.py:365` `decision_choice(...)` | G4 미공시(`not_disclosed_confirmed`) 시 1칸 강등 분기(실행 내 대상사 없음) | pass |
| C-17 | documented | 미등재 | 메타데이터 검증 | 기준 시점 분리(price_as_of, info_cutoff) 반영 | pass |
| C-18 | documented | 미등재 | 없음 | 문서화 전용 | pass |
| C-19 | documented | 미등재 | 없음 | 문서화 전용 | pass |
| C-20 | pending | `defer_to_private_g2` | `scripts/scorecard/calc_f9.py:311` `decision_choice(...)` | 비상장 2사 G1 보류 후 G2 비상장 경로로 직행 | pass |
| C-21 | documented | 미등재 | 없음 | 문서화 전용 | pass |
| C-22 | documented | 미등재 | 없음 | 문서화 전용 | pass |
| C-23 | pending | 미등재 | 없음 | 미결 유지 | pass |
| C-24 | resolved | `compute_p2_when_inputs_exist` | `scripts/scorecard/calc_f6_params.py:343` | `track["optional_parameters"]` 규칙 설정을 통해 spacex-xai P2 계산(80.27, -2) 반영 | pass |
| C-25 | pending | 미등재 | 없음 | 미결 등재 | pass |
| C-26 | pending | 미등재 | 없음 | 미결 등재 | pass |
| C-27 | pending | 미등재 | 없음 | 미결 등재 | pass |
| C-28 | pending | 미등재 | 없음 | 미결 등재 | pass |

## 체크리스트
| ID | 결과 | 근거(파일:행) · fail 이면 회사 |
|---|---|---|
| Q01 | fail | nvidia (`scorecard/runs/ai-scorecard-2026-09-obsreg/judgments.json` nvidia.F5 vs nvidia.F8 하이퍼스케일러 40% 이탈 중복 계상, `TEN-RC-05` 승계 예외), tesla (`judgments.json` tesla.F5 vs tesla.F8 NHTSA 조사 중복 계상, `TEN-RC3-04` 승계 예외). |
| Q02 | pass | `scripts/scorecard/calc_f6_params.py:50~100`(nonop_share 세전 기준), `calc_f6_params.py:364~378`(net_cash 정의 분리), `calc_f9.py:39~42`(런웨이 cash 분리), `run.json:116, 119`에 따라 각 지표가 정의에 맞게 엄격 분리됨. |
| Q03 | pass | F6 parameters 상장 12개사 동일 산식 및 C-24 신규 상장 트랙 P2 적용(`calc_f6_params.py:343`), TSM/Alibaba 환율 환산 3조건 일관 적용(`run.json:105`). 단, 승계 판단 긴장 `TEN-RC-03`(F5 별표 H 이탈 기준), `TEN-RC3-03`(palantir/oracle F1 락인 기준), `TEN-RA4-01`(F2 하네스 미표기)은 승계 예외 인정. |
| Q07 | pass | Amazon·Apple 모두 모델을 안 만든 것 자체를 카운터 포지셔닝으로 인정하지 않고 `imitation=fail` 판정(`judgments.json` amazon.F3, apple.F3). |
| Q08 | fail | spacex-xai (`judgments.json` spacex-xai.F5 H=-1 근거가 적대의 성격이 아닌 "동맹이 적보다 확실히 많지 않음" 수 비교, `scorecard/rules/v1.7.json` `TEN-RC4-03` 승계 예외). |
| Q12 | pass | `scripts/scorecard/calc_qual.py:128` 및 `scorecard/rules/v1.7.json` factors.F3.ladder에 `requires_imitation_pass`가 설정되어 모방불가 미충족 시 4점 진입이 원천 차단됨(Alibaba, SpaceX-xAI 등 통과점 2.5를 3점으로 상한). |
| Q13 | pass | Alibaba F3에서 오픈웨이트 무료 배포의 회수 장치 부재를 지적해 partial로 제한하고(`judgments.json` alibaba.F3), Meta F3에서는 광고 기반 저가 API를 회수 장치로 구분함. |
| Q15 | pass | NVIDIA 개발자 1,800만, Alibaba 파생모델 15만, Meta Glimmer 개발자를 공짜 사용자로 배제하고 상업적 약속만 아군으로 인정(`judgments.json` nvidia.F5, alibaba.F5, meta.F5). |
| Q16 | fail | anthropic (`judgments.json` anthropic.F1 주채널 업무 선정 후 소비자 수 열세로 5점 제한, `TEN-RC-02` 승계 예외), openai (`judgments.json` openai.F1 주채널 소비자 선정 후 거래 채널 근거로 4점 제한, `TEN-RC4-02` 승계 예외). |
| Q17 | pass | Oracle F2(세 경로 전부 미통과), Alibaba F2(프론티어 미달 복합) 등 "표준 없음" 단일 사유로 감점한 기업 없음(`judgments.json` F2 항목 전수). |
| Q18 | pass | Tesla F5에서 관계사 SpaceX를 동맹에서 배제(A=0), SpaceX-xAI F5에서도 Tesla를 관계사로 배제하여 관계사를 독립 동맹으로 센 기업 0건(`judgments.json` tesla.F5, spacex-xai.F5). |
| Q19 | pass | OpenAI F5(F5-IMPL-48)에서 피투자 관계(Amazon, SoftBank, MS 27%, NVIDIA)를 전부 배제하고 Stargate 지분 등 능동 동맹만 인정하여 A=+1 강등, 14개사 전수에서 피투자를 동맹으로 인정한 사례 없음(`judgments.json` F5 항목 전수). |
| Q20 | pass | Apple Gemini 라이선스, Meta 멀티벤더 구매, OpenAI→Oracle $300B 컴퓨트 계약을 모두 조달로 배제(`judgments.json` apple.F5, meta.F5, openai.F5). 단, Bedrock 입점사 및 광고주 동맹 인정 긴장은 `TEN-RC-03` 승계 예외. |
| Q21 | fail | nvidia (`judgments.json` nvidia.F5 H=-2와 nvidia.F8 -3에 "고객 40% 자체 칩 개발 이탈" 동일 속성 중복 계상, `TEN-RC-05` 승계 예외), tesla (`judgments.json` tesla.F5 H=-1과 tesla.F8 -2에 NHTSA 조사 동일 속성 중복 계상, `TEN-RC3-04` 승계 예외). |
| Q22 | pass | `scripts/scorecard/calc_qual.py:159~167` F7 엔진은 두 축만 읽고 영업외 비중을 점수에 산입하지 않음. Alphabet·Amazon·NVIDIA 근거란에 ⑥ 소관 및 방증 언급만 유지하여 C-11 및 별표 I 원칙 준수(`judgments.json` F7 항목 전수). |

## 발견 사항
- [severity: medium] `scripts/scorecard/calc_f6_params.py:343` — C-24 결정이 `decision_choice(run, rules, "C-24")` 분기를 거치지 않고 규칙 파일의 `track["optional_parameters"]` 사전 설정만 읽어 동작함 — `run.json.decisions`에서 선택지를 변경하더라도 코드가 감지하지 못하므로, 향후 `decision_choice`를 통한 런타임 결정 검증 분기로 정합성을 보완할 필요가 있음.
- [severity: medium] `scorecard/rules/v1.7.json` factors.F5 및 `judgments.json` — Anthropic, OpenAI에 이어 TSMC까지 [A-STRICT-54]로 A=+2에서 A=+1(F5: 3점)로 하향된 상태에서, Alphabet·Amazon·Microsoft 3사의 A=+2 유지 적격성을 별표 G A 기준표(채점규칙 192~193행)와 대조함 — Alphabet은 Meta에 TPU 판매(경쟁사 공정 편입), Amazon은 Bedrock 100+ 모델(경쟁사 매대 편입), Microsoft는 OpenAI 지분 27% 및 다수 모델 Azure 편입으로 +2 요건을 충족하여 전사 동일 잣대가 유지됨을 확인했음.
- [severity: low] `scripts/scorecard/calc_qual.py:150` 및 `scorecard/rules/v1.7.json:C-11` — C-11(`block_carryover`)은 규칙과 `run.json`에 등재되었으나 코드가 이를 읽는 분기(`decision_choice`)가 전혀 없는 무소비자 상태(`declared_without_consumer`)임 — F7 계산기가 원래 두 축만 읽어 점수 왜곡은 없으나, 향후 입력 확장 시 코드 검증 분기 추가가 필요함.
- [severity: low] `scripts/scorecard/calc_f6_params.py` 및 `scorecard/rules/v1.7.json:C-13` — C-13(`reject_proxy`)은 `calc_f6.py`(구 bands 모드)에만 존재하고 v1.7 정본인 `calc_f6_params.py`에는 호출이 없음 — parameters 모드는 NTM PER을 사용하지 않으므로 점수 영향은 없으나, decisions 항목의 소비 범위가 모드에 종속됨을 유의해야 함.
- [severity: low] `scripts/scorecard/schema.py:741~823` — 인메모리 변조 테스트를 통해 `working_definition` 상태에서 `scope_separation`, `two_axes`, `banned_word`('환금성') 검사가 `SchemaError`를 정상 발생시키며 스키마 차원에서 엄격히 강제됨을 입증했음.

## 확인 못 한 것
- 비상장 2사(Anthropic, OpenAI)의 미공시 재무제표 원문 — 구조적 미공시(`not_disclosed_confirmed`) 라벨에 따라 점수 경로에서 제외되었으며 외부 비공개 자료이므로 직접 열람하여 대조하지 못함.
- 2026-11 재검토 예정으로 등록된 긴장(`open_tensions`) 대상 6개사 12개 judgment의 실측치 갱신 결과 — 현 실행에서는 승계 판단 예외 규정에 따라 기존 점수를 보존한 채 검토를 통과시킴.
- 기타 미결 결정 5건(C-23, C-25, C-26, C-27, C-28)의 최종 사용자 결정 — 현 실행 기준에서는 `run.json`에 미반영된 상태로 유지됨.
