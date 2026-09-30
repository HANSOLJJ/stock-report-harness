# rule-consistency — 규칙 일관성
검토자: Gemini 3.8 Flash (High) · 독립 세션 · 2026-09-17 09:31
결과: pass
요약: 14개 기업의 모든 factor 점수가 `v1.7.json`의 정의 구간 안에 정확히 부합하며, F2 `[2,5]`와 F3 `[1,5]`의 구간 근거가 명문화되어 있습니다. run.json의 결정 사항(C-03·C-05·C-06·C-11·C-12·C-13·C-16·C-20·C-24)은 코드 분기와 결과에 실질적으로 반영되었거나 유효하게 격리되어 있으며, 이번 실행이 변경한 잣대(F5 A-STRICT-54 TSMC 재판정, F6 순현금 및 P2 securities_scope 전사 통일, C-24 신규 상장 트랙 P2 산출)는 14개사에 차별 없이 일관되게 적용되었습니다. 체크리스트 담당 15개 항목 중 나타난 fail은 모두 v1.5 승계 판단 논리에 기인한 것이며 `open_tensions`에 재검토 시점과 함께 정식 등록되어 있어 AGENTS.md의 승계 판단 예외 규정에 따라 pass를 차단하지 않습니다.

## 결정 반영 대조
| 결정 | rules status | run.json | 코드 분기 | 결과 반영 | 판정 |
|---|---|---|---|---|---|
| C-01 | documented | 미등록 | 없음 (안내 문서 성격) | 낡은 안내 정리 완료 (`scorecard/rules/v1.7.json:decisions[0]`) | pass |
| C-02 | resolved | 미등록 | `scripts/scorecard/calc_f6.py:273` | 상장사 완전 자동(parameters), 비상장사 파라미터 산출 및 정성 예외 분기 반영 | pass |
| C-03 | resolved | `paths_with_generation_gap_5` | `scripts/scorecard/calc_qual.py:39` | 14개사 F2가 kind="score"이므로 warning 문구에 반영되고 승계 점수 유지. 세대 격차는 판단 입력으로 분리 (`judgments.json:items`) | pass |
| C-04 | pending | 미등록 (규칙 기본값 `exclude` 적용) | `scripts/scorecard/calc_f9.py:294` | include/exclude 산식이 `현금 + undrawn_credit`로 동일하여 점수 변동 없음, 경고 문구 분기 반영 | pass |
| C-05 | pending | `apply` | `scripts/scorecard/calc_f9.py:191`, `213` | G1 실패 뒤 G3/G4 진단 결과를 실제 점수에 감점 반영 (spacex-xai G1 -3 확정, `results.json`) | pass |
| C-06 | pending | `proposed_v15_boundaries` | `scripts/scorecard/calc_f9.py:158` | 영업손실률 밴드 -2/-3/-4 재척도 적용 (spacex-xai G1 -3 확정, `results.json`) | pass |
| C-07 | pending | 미등록 | `scripts/scorecard/calc_f9.py:348` | `coverage_comparable: no`일 때 약정 비교 불가(`incompatible`) 대기 처리 (anthropic G4 반영) | pass |
| C-08 | pending | 미등록 | 직접 호출 코드 없음 | Q19와 결합하여 OpenAI F5 A=+1 갱신에 기여, 별표 H 이탈 조건 모순은 `TEN-RC-03` 긴장 등록 | pass |
| C-09 | pending | 미등록 | `scripts/scorecard/calc_qual.py:158` | 환류 매트릭스 입력 미복원으로 anthropic·openai F7 -1 승계 유지, `TEN-RC3-01` 긴장 등록 | pass |
| C-10 | documented | 미등록 | 없음 (문서성) | 가격 설명 및 경계 트리거 옛 수치 정리 완료 | pass |
| C-11 | resolved | `block_carryover` | 없음 (F7 엔진에 이월 경로 원천 부재) | 영업외 비중을 F6 P4 전용으로 한정하고 F7 이월 차단 (`scripts/scorecard/calc_qual.py:150`) | pass |
| C-12 | pending | `p2_with_capped_promotion` | `scripts/scorecard/calc_f6_params.py:486` | 비상장사 P2(PS 배수) 구간 채점 및 P3·P4 조건부 한 칸 보정 적용 (anthropic·openai F6=-4 반영) | pass |
| C-13 | resolved | `reject_proxy` | `scripts/scorecard/calc_f6.py:202` | v1.7은 parameters 모드라 bands 모드 전용인 이 분기는 실행되지 않고 점수 불개입 (`calc_f6.py:200`) | pass |
| C-14 | documented | 미등록 | `scripts/scorecard/render_common.py:158` | 트리거 예상 점수 문언 정리 완료 | pass |
| C-15 | documented | 미등록 | 없음 | Meta 리스 개시 후 연 소진 이중 계상 방지 정리 완료 | pass |
| C-16 | pending | `downgrade` | `scripts/scorecard/calc_f9.py:386` | 확인된 미공시(`not_disclosed_confirmed`) 시 G4에서 -1 감점 적용 (alibaba G4 -1 반영, F9=-3) | pass |
| C-17 | documented | 미등록 | `scripts/scorecard/render_html.py:556` | 기준 시점(as_of, price_as_of, info_cutoff) 3자 분리 기록 적용 | pass |
| C-18 | documented | 미등록 | 없음 | 참조 기업 범위 및 클라우드 표 기간 정리 완료 | pass |
| C-19 | documented | 미등록 | 없음 | 유일·최저 등 낡은 비교 문장 정리 완료 | pass |
| C-20 | pending | `defer_to_private_g2` | `scripts/scorecard/calc_f9.py:332` | 비상장 TTM 영업손익 미공시 시 G1 보류 후 G2 비상장 경로 분기 (anthropic G2로 이동하여 -2 감점) | pass |
| C-21 | documented | 미등록 | 없음 | 가격 공급 정책(yfinance/FMP) 및 적용 범위 정리 완료 | pass |
| C-22 | documented | 미등록 | 없음 | 총점 음수 함정 명목(-20 vs F7 -2) 설명 정리 완료 | pass |
| C-23 | pending | 미등록 | 없음 | 확정 미인출 여신 잔존 기간 요건 미결 (amazon 37.5B 전액 산입 유지, pending_recheck) | pass |
| C-24 | resolved | `compute_p2_when_inputs_exist` | `scripts/scorecard/calc_f6_params.py:345` | 신규 상장 트랙(spacex-xai)에 P2 계산(80.27, -2점) 및 F6=-3 반영 완료 | pass |
| C-25~C-28 | pending | 미등록 | 각 해당 엔진 파일 참조 | 미결 상태 유지 (C-25 바닥, C-26 oracle B종, C-27 경계 3%, C-28 순손실 P2) | pass |

## 체크리스트
| ID | 결과 | 근거(파일:행) · fail 이면 회사 |
|---|---|---|
| Q01 | fail (승계 예외) | nvidia: F5 H=-2(고객이 경쟁자)와 F8=-3(고객 40% 자체 칩 개발) 중복 (`scorecard/rules/v1.7.json:open_tensions`, `TEN-RC-05`). tesla: F5 H=-1과 F8=-2에 NHTSA 조사 중복 (`TEN-RC3-04`). v1.5 승계 논리이며 2026-11 재검토 등록되어 pass 유지. |
| Q02 | fail (승계 예외) | anthropic: F1 주채널 업무 지정 후 개인 사용자 수 열세로 차단 (`TEN-RC-02`). palantir vs oracle: 업무 전환비용 상반 취급 (`TEN-RC3-03`). alibaba: 경쟁사 오픈웨이트 배포 상황에서 F3 모방불가 partial (`TEN-RC3-05`). openai: F1 소비자 주채널 분류 후 거래 채널로 차단 (`TEN-RC4-02`). anthropic·openai: F7 매트릭스 입력 미복원 (`TEN-RC3-01`). 모두 v1.5 승계 예외. |
| Q03 | fail (승계 예외) | 이번 실행이 바꾼 잣대(F5 A-STRICT-54 TSMC 재판정, F6 순현금 securities_scope 전사 통일, C-24 신규 상장 트랙 P2)는 14개사 전사에 동일하게 적용됨 (`scorecard/runs/ai-scorecard-2026-09-obsreg/judgments.json:tsmc.F5.strict54`, `scripts/scorecard/calc_f6_params.py:345`). v1.5 승계 판단의 전사 불일치는 `TEN-RC-03`(별표 H 이탈 조건), `TEN-RC3-01`(F7 매트릭스), `TEN-RC3-03`(F1 전환비용), `TEN-RC4-03`(F5 H=-1 수 비교)으로 등록된 승계 예외. |
| Q07 | pass | 14개사 전수 조사 결과 "안 만든 것" 자체를 카운터 포지셔닝으로 인정한 회사 없음. Amazon은 Bedrock 매대 전략의 모방불가 fail (`judgments.json:amazon.F3`), Apple은 디바이스 ① 중복으로 모방불가 fail (`judgments.json:apple.F3`)로 엄격 판정. |
| Q08 | fail (승계 예외) | spacex-xai: F5 H=-1 근거가 적대의 종류가 아닌 "동맹이 적보다 확실히 많지 않음"이라는 수 비교 (`scorecard/rules/v1.7.json:open_tensions`, `TEN-RC4-03`). Apple(비용형 -1), NVIDIA(구조형 -2), Palantir(구조형 -2), OpenAI(다발형 -3) 등 타사는 성격으로 분류됨. |
| Q12 | fail (승계 예외) | F3 사다리는 모방불가 pass 없이 4점 이상 진입 불가 (`scorecard/rules/v1.7.json:factors.F3.ladder[3].requires_imitation_pass`). 전원 3점 이하 절단 확인. 단 meta·anthropic·spacex-xai의 imitation partial 근거 불충분 긴장이 `TEN-RC4-01`로 등록됨. |
| Q13 | fail (승계 예외) | 오픈웨이트 무료 배포를 곧바로 카운터 포지셔닝으로 인정하지 않고 회수 장치 부재를 엄격 지적 (`judgments.json:alibaba.F3`). 단 오픈웨이트 배포 기업들의 imitation partial 부여 논리가 승계 예외 `TEN-RC4-01`, `TEN-RC3-05`에 등록됨. |
| Q15 | pass | Meta 광고주 생태계(유료 광고주), NVIDIA Nemotron 상업 연합(CUDA 무료 개발자는 불인정). 14개사 전원에서 공짜 사용자를 동맹으로 산입한 사례 없음 (`E:/sourcecode/.../AI기업_채점규칙_v1.5.md:198, 226행`). |
| Q16 | fail (승계 예외) | anthropic: 주채널을 업무로 적고도 개인 채널로 차단 (`TEN-RC-02`). openai: 주채널을 소비자라 적고 거래 채널로 차단 (`TEN-RC4-02`). v1.5 승계 예외. |
| Q17 | pass | F2는 세 경로(성능 도약, 패러다임 적응, 표준 선점) 통과 수로 매핑 (`scorecard/rules/v1.7.json:factors.F2`). "표준 없음" 단독으로 감점된 회사 없음. |
| Q18 | pass | Tesla F5에서 관계사 SpaceX는 동맹 산입 제외(A=0 적용, `judgments.json:tesla.F5`). SpaceX+xAI에서도 NASA/DoD 등 외부 동맹만 산입 확인. |
| Q19 | pass | 피투자 관계를 동맹 +2로 센 v1.5 오류를 시정하여 Anthropic(A=+1), OpenAI(A=+1) 갱신 완료 (`judgments.json:anthropic.F5`, `openai.F5`). 동일한 잣대로 TSMC도 지분 동맹 0건 및 자신 경쟁사 편입 부재로 A=+1 재판정 (`judgments.json:tsmc.F5.strict54`). Alphabet, Amazon, Microsoft는 +2 요건 충족 유지 확인. 전사 일관 통과. |
| Q20 | fail (승계 예외) | Apple(칩 구매, Gemini 라이선스), Tesla(Starlink 조달), OpenAI(Oracle 클라우드 구매) 등 조달 관계는 동맹에서 제외됨. 다만 별표 H 3문(상대 이탈 가능성)과 관련해 NVIDIA는 불인정하고 타사는 인정한 이탈 기준 불일치가 승계 예외 `TEN-RC-03`으로 등록됨. |
| Q21 | fail (승계 예외) | nvidia: F5 H=-2와 F8=-3의 자체 칩 이탈 중복 (`TEN-RC-05`). tesla: F5 H=-1과 F8=-2의 NHTSA 중복 (`TEN-RC3-04`). v1.5 승계 예외. |
| Q22 | pass | `scripts/scorecard/calc_qual.py:150-166` `compute_f7`은 오직 `funding_dependent_share`와 `own_money_returns` 두 축만 읽음. 지분 평가이익은 F6 P4 전용으로 F7로 이월되지 않음 (`scorecard/rules/v1.7.json:decisions` C-11 block_carryover 확인). |

## 발견 사항
- [severity: low] `scripts/scorecard/calc_qual.py:39` (C-03) — C-03 choice(`paths_with_generation_gap_5`)를 읽어 경고 문구 분기에만 반영하고, 14개사의 judgment가 모두 `kind: "score"`여서 실제 경로 계산 분기(`_f2_generation_gap`)로는 진입하지 않음 — 이는 run.json.decisions의 rationale("14개사 F2는 승계 score 판단이라 세대 격차는 판단 입력이라 경로 판정이 들어올 때 compute_f2가 이 선택으로 산출한다")에 부합하는 설계된 동작임.
- [severity: low] `scripts/scorecard/calc_f6.py:202` (C-13) — run.json에 C-13(`reject_proxy`)이 등록되어 있고 코드에도 분기가 있으나, v1.7은 F6가 `parameters` 모드이므로 상위에서 `calc_f6_params.py`로 분기하여 `calc_f6.py:202`의 `bands` 전용 NTM proxy 거절 코드는 실행되지 않음 — rules.decisions C-13 implementation_status 및 FIX-56 주석에 명시된 정상 상태임.
- [severity: low] `scripts/scorecard/rules.py` 및 run.json (C-11) — run.json에 C-11(`block_carryover`)이 등록되어 있으나, 이를 읽는 `decision_choice` 코드 호출이 없음 — F7 계산 엔진(`calc_qual.py:compute_f7`) 자체가 nonop_share를 읽지 않고 두 축(고객 의존도, 자기자금 환류)만 읽으므로 이월 경로가 구조적으로 차단되어 있어 기능상 무결함.
- [severity: low] `scripts/scorecard/calc_f9.py:294` (C-04) — run.json에 미등록 상태이며 규칙 정책 기본값("exclude")이 적용됨. `include_v15`를 선택하더라도 산식(`현금 + undrawn_credit`)이 동일하여 점수 변동이 없는 상태임 (`calc_f9.py:291-294`).
- [severity: low] `scripts/scorecard/schema.py:741-824` — 메모리 상 변조 검증 결과, `scope_separation` 제거, `two_axes` 제거, 금지어(`환금성`) 임의 삽입, `banned_word` 블록 누락 시 스키마 유효성 검사가 즉시 `SchemaError`를 발생시키며 철저하게 강제됨을 입증함.

## 확인 못 한 것
- 외부 실시간 웹/API 조회 (외부 조회 금지 및 오프라인 규칙 준수). 단, 로컬 저장소 내부 SEC JSON 사실자료(`validation/f6-avail-15/_raw/`) 및 v1.5 보존 원문(`E:/sourcecode/.../AI기업_채점규칙_v1.5.md`)은 전수 대조 확인 완료함.
