# 감사 기록 — 2026년 3분기 실적 반영 (2차) — ⑤ 받은 투자 규칙

이 파일은 **재현과 감사를 위한 기록**이다. 리포트 본문에서 뺀 해시·입력 지문·실행 단위 선택을 모은다.
리포트는 `output/ai-scorecard-2026-10-q3b/report.html` 이고 여기 값들이 그 리포트를 만든 입력이다.

## 규칙과 기준 시점

- 규칙 `v3.1` · 해시 `c24db4b239a69937222d10ff440448ffc6336e6c495e0bc84a97f7bedae6cf72`
- 원본 파일 `docs/scorecard/rules.md`
- 분석 기준일 `2026-10-23` · 가격 기준일 `2026-10-22` · 정보 컷오프 `2026-10-23`
- 이 실행은 일부 회사만 다시 매긴 실행이다(⑤ 받은 투자 절충안 적용 — 투자를 받은 비상장 모델사 둘의 판단을 다시 읽는다). Anthropic, OpenAI 의 판단은 전부 이 기준일에 다시 매겼고, 가격은 모든 회사가 가격 기준일 2026-10-22 의 종가이며, 나머지 회사의 판단은 각 회사 카드의 반영 기준일에 매긴 것을 이어받았다.
- 회사별 마지막 전체 갱신일: alibaba 2026-10-14, alphabet 2026-10-14, amazon 2026-10-14, anthropic 2026-10-23, apple 2026-10-14, meta 2026-10-22, microsoft 2026-10-14, nvidia 2026-10-14, openai 2026-10-23, oracle 2026-10-14, palantir 2026-10-14, spacex-xai 2026-10-22, tesla 2026-10-22, tsmc 2026-10-22

## 입력 해시

| 대상 | 해시 |
| --- | --- |
| observations | `ef0e653072ec311da7e94b8e3ae88b2b32a078298715d6c2de6c09b6eade5da8` |
| judgments | `debbf13c24d8edb8a7543b146bb9395d42cbd6f2c038206a5a92e5c40c7769ba` |
| results | `3063a73c56af7311e8a7cdc0f0ab58f2848ad88d3df6bc1f4014a5124779de64` |
| run | `c3900c2c9993958624c7ea8a2636ebe7e98c57a720ead91b7b8d54e30f4a4563` |
| draft | `c41adc70f02ad2dd5a12dc2d4b4ffb184d6bda62f9995ee11f4cfc0c4ba47d0f` |

## 확인

- 확인 `ee3d90f2d2e85613` · 정한솔 · 2026-10-23
- 확인 시점 입력과 현재 입력이 모두 같다.

## 실행 단위 결정

규칙이 미결로 둔 항목 중 이번 실행에서 고른 선택이다. **목록에 있다고 그 선택을 계산이 실제로 읽었다는 뜻은 아니다** — 소비 여부는 각 항목의 산식과 경고에서 확인한다.

| 결정 | 이번 실행 선택 |
| --- | --- |
| `C-05` | `apply` |
| `C-06` | `proposed_v15_boundaries` |
| `C-16` | `downgrade` |
| `C-20` | `defer_to_private_g2` |
| `C-03` | `paths_with_generation_gap_5` |
| `C-11` | `block_carryover` |
| `C-13` | `reject_proxy` |
| `C-24` | `compute_p2_when_inputs_exist` |
| `C-28` | `optional_parameters_for_all_listed_tracks` |
| `C-29` | `c20_private_route_first` |
| `C-12` | `growth_adjusted_ps` |

## 제3자 재검토 약속

  - anthropic ②5 재검토 — anthropic ②5 재검토가 C-13 에서 돌고 있다. **결과에 따라 anthropic F2 가 5→4 가 될 수 있다.** 시점 2026-11 재채점 (사용자 원본 채점표 · 인수인계 문서) · 발동 조건 `독립 기관의 에이전트 실무 축 측정 (인수인계 문서)` (C-03 이 재검토 대기로 걸어 둔 항목이다). 이번 실행은 이 판단을 재판정하지 않았다.

## 미결 규칙 결정

아직 확정되지 않은 규칙 항목이다. 걸린 항목은 점수를 만들지 않고 대기 상태로 남는다.

| 결정 | 요약 | 권고 | 이번 실행 |
| --- | --- | --- | --- |
| `C-05` | G1 실패 뒤 G3·G4 를 추가 감점하는지 진단만 하는지 원문이 혼재 | diagnose_only 또는 apply 를 결정. 결과가 달라지는 기업만 대기 처리 | apply |
| `C-06` | 손실률 -10%·-30% 경계 중첩, FCF/영업손익 0, 완충 잠식, G2 안정/악화의 기계 정의 부재. [FIX-63 정정 · obsreg 9차 재무 계산 재판정 2회(Claude 독립 세션) medium] **BEP 후퇴의 우선순위는 미결이 아니다.** 사용자 결정 2026-09-17(C-29)로 `policies.f9.g1_bep_retreat_precedence` 에 명문화했다 — **C-20 비상장 경로가 먼저 서고**, 상장사이거나 영업손익이 구조적 미공시가 아닌 경우에만 BEP 후퇴가 **G1 통과·손실률 밴드 둘 다보다 앞서** `g1_bep_retreat_score` 를 준다. 점수도 -5 가 아니라 **-4** 다(C-06 재척도). **그 자리에서는 순서가 결과를 가른다** — 손실률이 최심 밴드(-30% 초과)가 아니면 밴드 점수와 다른 값이 나오고, **영업흑자여도 통과하지 못하고 하한을 받는다**(TEN-RA6-01). 남은 미결은 FCF·영업손익 0 처리와 완충 잠식·G2 추세의 기계 정의다 | policies.f9.g1_bands_proposed 와 BEP 우선 규칙을 검토해 전 구간 명문화 | proposed_v15_boundaries |
| `C-16` | G4 판정 불가→하향 규칙과 Alibaba·SpaceX 보류 유지 사례가 다름 | 결측 유형·적용 대상·하향 중복 방지 규칙 확정 | downgrade |

## 검토 기록

검토 방식 `separate-session-4way` · 실행 `separate_subagent_sessions` · 검토한 초안 `c41adc70f02ad2dd5a12dc2d4b4ffb184d6bda62f9995ee11f4cfc0c4ba47d0f`

- fact-sources: fact-checker (claude-sonnet-5-5) → pass after fix batch, confirm reviews (Opus) pass
- financial-calc: separate session (claude-sonnet-5-5) pass
- rule-consistency: separate session (Claude Opus 5.5, high) → pass after fix batch, confirm reviews pass
- output-readability: report-designer (claude-sonnet-5-5) → pass after fix batch, confirm reviews pass

## 결정 기록

규칙 파일이 번호를 붙여 적어 둔 설계 결정이다. 리포트 본문은 번호 없이 **그 결정이 점수에 무엇을 했는지**만 말로 적고, 결정 자체의 기록은 여기 모은다.

| 결정 | 상태 | 무엇을 정했나 | 권고 | 이번 실행 선택 | 영향 항목 |
| --- | --- | --- | --- | --- | --- |
| `C-01` | 문서화 | 원본 AGENTS.md 의 체크리스트 17·게이트 2단계·별표 A~F·Meta 1위는 낡은 안내 | 새 안내는 활성 원본에서 생성 | — | — |
| `C-02` | 확정 | F6·F9 완전 자동(HANDOVER) vs 비상장 F6·F9 정성 수동(구현계획) | factor 내부를 입력→판정→환산 단계로 분리(설계 지침 4절). 본 규칙 파일의 mode 가 그 결과 | — | — |
| `C-03` | 확정 | F2 경로 수→점수 매핑(0→2, 1→3, 2→4, AA 1위→5)이 완결되지 않았고 NVIDIA·TSMC 5점을 재현하지 못함 | 기업 유형별 최고점 자격과 3경로 통과·0/1점 조건을 확정. 확정 전 신규 F2 는 승계 score 만 | 경로 수 매핑 + 세대 격차 최고점 (`paths_with_generation_gap_5`) | ② 게임체인저 |
| `C-04` | 미결 | 별표 J 는 신용등급의 점수 개입을 금지하나 G3 는 등급 기반 조달 여력을 완충에 넣음 | 확인 현금+확정 미인출 여신만 산입(기본 exclude). 등급은 교차검증. include_v15 선택 시 영향 검토 | — | ⑨ 적자 깊이 |
| `C-05` | 미결 | G1 실패 뒤 G3·G4 를 추가 감점하는지 진단만 하는지 원문이 혼재 | diagnose_only 또는 apply 를 결정. 결과가 달라지는 기업만 대기 처리 | 뒤 관문 값을 점수에 반영 (`apply`) | ⑨ 적자 깊이 |
| `C-06` | 미결 | 손실률 -10%·-30% 경계 중첩, FCF/영업손익 0, 완충 잠식, G2 안정/악화의 기계 정의 부재. [FIX-63 정정 · obsreg 9차 재무 계산 재판정 2회(Claude 독립 세션) medium] **BEP 후퇴의 우선순위는 미결이 아니다.** 사용자 결정 2026-09-17(C-29)로 `policies.f9.g1_bep_retreat_precedence` 에 명문화했다 — **C-20 비상장 경로가 먼저 서고**, 상장사이거나 영업손익이 구조적 미공시가 아닌 경우에만 BEP 후퇴가 **G1 통과·손실률 밴드 둘 다보다 앞서** `g1_bep_retreat_score` 를 준다. 점수도 -5 가 아니라 **-4** 다(C-06 재척도). **그 자리에서는 순서가 결과를 가른다** — 손실률이 최심 밴드(-30% 초과)가 아니면 밴드 점수와 다른 값이 나오고, **영업흑자여도 통과하지 못하고 하한을 받는다**(TEN-RA6-01). 남은 미결은 FCF·영업손익 0 처리와 완충 잠식·G2 추세의 기계 정의다 | policies.f9.g1_bands_proposed 와 BEP 우선 규칙을 검토해 전 구간 명문화 | 제안된 손실률 구간 적용 (`proposed_v15_boundaries`) | ⑨ 적자 깊이 |
| `C-07` | 미결 | G4 는 RPO/B종인데 Anthropic·OpenAI 는 ARR/연환산 약정으로 계산됨 | ARR 대체 금지. 동일 범위 계약 자료 미확보는 incompatible_basis 로 미완료 표시 | — | ⑨ 적자 깊이 |
| `C-08` | 미결 | 별표 H 이탈 가능성 본문과 Bedrock·광고주 예시가 다름. 3문/4문 참조 혼재. 원문 별표 G 는 OpenAI→Oracle $300B 를 동맹 근거로, 별표 H 는 조달로 적어 같은 관계를 다르게 분류함(Q20 긴장, 승계 A+2 는 다른 동맹 근거로 점수 무영향) | 계약상 가능성과 실질 대체·이탈 유인을 구분하는 정성 기준 필요 | — | ⑤ 아군 |
| `C-09` | 미결 | Anthropic·OpenAI F7 -1 의 매트릭스 입력(환류 여부)이 원문에 없음 | 두 축의 실제 입력 복원·검토. 기존 점수에 맞추려고 환류를 추정하지 않음. 승계 score 는 경고와 함께 허용 | — | ⑦ 순환금융 |
| `C-10` | 문서화 | 가격 설명·경계 트리거에 옛 경계 20·25·35·60·90 이 남음 | 활성 경계 20·29·42·62·90 에서 표시·트리거 생성 | — | — |
| `C-11` | 확정 | 영업외 비중을 F7 근거로 이월한다는 설명이 별표 I 와 충돌 | 손익의 질 참고로만 유지 | ⑦ 로 이월 금지 (`block_carryover`) | ⑦ 순환금융 |
| `C-12` | 미결 | 비상장 F6 가 배수만 vs TTM 보정·이익·자본효율로 점수를 가름이 공존 | 비상장 최종 점수는 정성 예외(manual_with_rationale) | growth_adjusted_ps (`growth_adjusted_ps`) | ⑥ 가격 |
| `C-13` | 확정 | TSMC·Alibaba 는 연간 EPS 가중 근사를 NTM 으로 사용. 신규 계약은 정확한 4분기만 허용 | 원본 방법 표시 보존. proxy 채점은 실행 단위 결정으로만 | 근사값 불인정 (`reject_proxy`) | ⑥ 가격 |
| `C-14` | 문서화 | 트리거에 낡은 기존/예상 점수(NVIDIA F7 -3→-4 등) 잔존 | 사건 확인 후 현재 규칙으로 재계산. 트리거는 미래 점수를 저장하지 않음 | — | — |
| `C-15` | 문서화 | Meta 리스 개시 후 연 소진 가산 트리거는 A종 이중 계상 금지와 충돌 | 개시 시 분류·원자료 갱신, FCF 반영 지출 재가산 금지 | — | — |
| `C-16` | 미결 | G4 판정 불가→하향 규칙과 Alibaba·SpaceX 보류 유지 사례가 다름 | 결측 유형·적용 대상·하향 중복 방지 규칙 확정 | 판정 불가면 한 칸 하향 (`downgrade`) | ⑨ 적자 깊이 |
| `C-17` | 문서화 | 기준일 9/2 인데 9/3~9/7 사건이 섞임 | price_as_of · 재무 기간 · info_cutoff 를 분리 기록 | — | — |
| `C-18` | 문서화 | 참조 기업(Moonshot) 포함 여부와 클라우드 표의 기간 불일치 | 모집단·기간을 실행별 고정 | — | — |
| `C-19` | 문서화 | 유일·최저 등 낡은 비교 문장 | 비교 문장은 결과에서 생성하고 통독 검토 | — | — |
| `C-20` | 미결 | Anthropic 단일 분기 영업흑자를 TTM 원칙과 달리 G1 통과 근거로 씀 | 연결 TTM 재확보. 단일 분기로 G1 통과를 자동 복원하지 않음 | 비상장 경로로 보냄 (`defer_to_private_g2`) | ⑨ 적자 깊이 |
| `C-21` | 문서화 | 가격 공급 정책(yfinance vs FMP)과 stock/scorecard 적용 범위 | docs/scorecard/structure.md 에 유형별 적용 범위 명시. 기존 stock 요건 보존 | — | — |
| `C-22` | 문서화 | 총점 설명이 음수 함정을 빼는 것처럼 읽히고 명목 -20 은 F7 하한 -3 과 다름 | 합산은 과점 + 음수 함정. 활성 범위는 규칙에서 도출(trap_min_active -18) | — | — |
| `C-23` | 미결 | 런웨이 분자의 확정 미인출 여신에 잔존 기간 요건이 없다 — amazon 37.5B 중 22.5B 이 기준일 4주 뒤 소멸·만기 | 이번 실행은 기준을 바꾸지 않는다(설계 지침 6.4 는 `조건이 확인된 확정 미인출 여신` 만 요구하고 잔존 기간 요건이 없다). 다음 라운드에서 요건을 정한다 — 정하기 전까지 관측 basis.sensitivity 로 영향을 남긴다. | — | ⑨ 적자 깊이 |
| `C-24` | 확정 | 신규 상장 트랙이 P2 를 만들지 않는데 P2 입력은 실행 안에 다 있다 — 계산할 것인가 | 계산한다. 상장사 열두 곳에 같은 잣대를 대는 쪽이다. | 입력이 있으면 계산 (`compute_p2_when_inputs_exist`) | ⑥ 가격 |
| `C-25` | 미결 | 신규 상장 트랙의 바닥 -3 이 P2 를 계산하게 된 뒤에도 맞는지 | 이번 실행은 바닥을 건드리지 않는다. 바닥 -3 은 P3 하나(범위 -3~0)로만 점수를 내던 트랙의 값인데, C-24 로 P2(-2~0)가 더해져 소계 범위가 -5 까지 넓어졌다. spacex-xai 는 소계 -2 에 P4 한 칸이라 -3 이고 **바닥에 정확히 닿지만 절단되지는 않는다**(floor_applied 없음). 다음 라운드에서 정한다. | — | ⑥ 가격 |
| `C-26` | 미결 | oracle B종 약정 250,000M 이 어느 공시 사실과도 맞지 않는다 — 출처와 범위를 정해야 한다 | 이번 실행은 값을 바꾸지 않는다. legacy 를 그대로 두고 `basis` 에 사실과 공시 대안을 남겼다. [FIX-58 1단계 정정 · obsreg 7차 리뷰 B(financial-calc, review-obsreg 4906a27) medium] 전에 B종 후보로 든 셋 중 둘이 후보가 아니다 — `LesseeOperatingLeaseLiabilityPaymentsDue` 41,867 은 **개시분**의 할인 전 지급총액이라 이미 대차대조표 리스부채 30,190 으로 인식돼 있고, `LesseeOperatingLeaseLiabilityUndiscountedExcessAmount` 11,677 은 그 둘의 차인 **내재이자(할인차금)** 다(금융리스도 11,460 − 7,701 = 3,759 로 같은 관계). **남는 B종 후보는 구매 약정 `UnrecordedUnconditionalPurchaseObligationBalanceSheetAmount` 13,309M 계열 하나다.** 다음 라운드에서 (1) legacy 를 유지할지, (2) 구매 약정만 세는 좁은 정의로 바꿀지, (3) B종을 oracle 에 대해 미확인으로 내릴지 정한다. **오늘은 어느 쪽이든 G4 step 0 이라 점수가 갈리지 않는다**(2.552 대 47.937, 임계 1.0). [FIX-59 · obsreg 8차 리뷰 B(financial-calc, review-obsreg e5a47d3) medium] **G4 의 분자와 분모는 기준일도 성질도 다르다** — 분자 RPO 638,000M 은 2026-05-31 공시 사실(`oracle.contracted_revenue.fix57`, verified)이고 분모 250,000M 은 기준일이 2026-09-02 로 적힌 legacy 승계값이며 어느 공시 사실과도 맞지 않는다. 커버리지 2.552 는 그 둘의 비다. 임계 1.0 에서 멀어 오늘 step 은 갈리지 않지만, **범위를 정할 때 기준일도 같이 정해야 한다.** | — | ⑨ 적자 깊이 |
| `C-27` | 미결 | 경계 표시 허용폭 3% 가 적정한지 — 도입 계기였던 alibaba 사례(+3.32%)가 폭 밖이라 표시되지 않는다 | 이번 실행은 폭을 바꾸지 않는다. **표시 폭은 점수와 무관하지만 기준을 손대면 같은 잣대 문제가 된다** — F6 P1~P4 와 F9 G3 가 같은 tolerance 를 쓰고 있어 한 자리만 넓힐 수 없다. 거리 자체는 초안이 늘 보여 주므로(`임계 3년 대비 +3.3%`) 읽는 사람이 놓치지 않는다. 다음 라운드에서 폭을 정한다. [FIX-61 · obsreg 9차 재무 계산 재판정(Claude 독립 세션) low] **표본이 둘이 됐다.** oracle F6 P1 = 25.967109 로 밴드 경계 25 에서 **+3.87%** 이고, 허용폭 3% 밖이라 경계 표시가 붙지 않는다. **이 한 칸이 oracle 총점 2 와 3 을 가른다** — P1 이 -1 대신 0 이면 F6 -3 → -2 이고 총점이 3 이 된다. alibaba G3(+3.32%)와 같은 성질이고 방향도 같다(둘 다 폭 바로 밖). 폭을 정할 때 이 둘을 함께 본다. | — | ⑥ 가격, ⑨ 적자 깊이 |
| `C-28` | 확정 | listed_ttm·listed_annual 에서 순손실 기업이 나오면 P2·P3 를 산출해 놓고도 F6 가 pending_data 가 된다 | `listed_ttm`·`listed_annual` 에도 `optional_parameters: ["P1"]` 을 두어 `listed_newly` 와 같은 경로로 만든다. 순이익이 음수여서 P1 이 성립하지 않으면 사유를 `calc.parameters_optional_unmet.P1` 에 적고 P2·P3 로 소계를 낸다. | 상장 트랙에 선택 파라미터 (`optional_parameters_for_all_listed_tracks`) | ⑥ 가격 |
| `C-29` | 확정 | BEP 목표 후퇴와 C-20 비상장 경로 중 무엇이 앞서는가 — 앞선 결정(BEP 우선)을 뒤집는다 | C-20 이 앞선다. 비상장이고 영업손익이 구조적 미공시면 BEP 후퇴가 기록돼 있어도 비상장 경로로 보낸다. | 비상장 경로 우선 (`c20_private_route_first`) | ⑨ 적자 깊이 |
| `C-30` | 확정 | 정기 실행 전부 재판단과 ① 구조화(2026-10-08) | 정기 실행은 정성 판단 전부를 다시 매기고 승계는 기업 추가 실행에만 남긴다. ① 은 네 질문 입력과 사다리 A 로 계산하며 부품 상한을 지속성 할인으로 바꾼다. ② 세대 격차는 시간(모델 6개월·하드웨어 12개월), ③ 가속도는 지표 단계 a~e. 돌아가며 재판단하는 안(rotate_factors_monthly)은 한 리포트 안에 판단 시점이 섞여 밀렸고, 승계 기본값 유지(keep_carried_default)는 9월 2일 판단 87칸이 네 실행 동안 재검토 없이 이어진 상태라 밀렸다. | — | ① 네트워크, ② 게임체인저, ③ 카운터포지셔닝, ⑦ 순환금융 |

## 기업·항목별 작업 이력

리포트 본문의 근거는 **무엇을 보고 그 점수를 주었는지**만 싣는다. 언제 어느 과제로 표기가 바뀌었는지는 근거가 아니라 이력이라 여기로 옮겼다. 본문 근거 문장 자체는 그대로 남아 있다.

| 기업 | 항목 | 작업 표기 |
| --- | --- | --- |
| `alibaba` | ① 네트워크 | 판단 기록 alibaba.F1.all_others |
| `alibaba` | ① 네트워크 | 판단 기록 alibaba.F1.cloud |
| `alibaba` | ① 네트워크 | 판단 기록 alibaba.F1.cn_ecom_cmr |
| `alibaba` | ① 네트워크 | 판단 기록 alibaba.F1.cn_ecom_direct |
| `alibaba` | ① 네트워크 | 판단 기록 alibaba.F1.cn_wholesale |
| `alibaba` | ① 네트워크 | 판단 기록 alibaba.F1.intl_retail |
| `alibaba` | ① 네트워크 | 판단 기록 alibaba.F1.intl_wholesale |
| `alibaba` | ① 네트워크 | 판단 기록 alibaba.F1.quick_commerce |
| `alibaba` | ② 게임체인저 | 판단 기록 alibaba.F2.cloud |
| `alibaba` | ② 게임체인저 | 판단 기록 alibaba.F2.user_platform |
| `alibaba` | ③ 카운터포지셔닝 | 판단 기록 alibaba.F3.cloud |
| `alibaba` | ③ 카운터포지셔닝 | 판단 기록 alibaba.F3.user_platform |
| `alibaba` | ④ 호황 이후 | 판단 기록 alibaba.F4 |
| `alibaba` | ⑤ 아군 | 판단 기록 alibaba.F5 |
| `alibaba` | ⑦ 순환금융 | 판단 기록 alibaba.F7 |
| `alibaba` | ⑧ 비대칭 의존 | 판단 기록 alibaba.F8 |
| `alibaba` | ⑨ 적자 깊이 | 판단 기록 alibaba.F9.obsreg25 |
| `alphabet` | ① 네트워크 | 판단 기록 alphabet.F1.consumer_subscriptions |
| `alphabet` | ① 네트워크 | 판단 기록 alphabet.F1.google_cloud |
| `alphabet` | ① 네트워크 | 판단 기록 alphabet.F1.network |
| `alphabet` | ① 네트워크 | 판단 기록 alphabet.F1.other_bets |
| `alphabet` | ① 네트워크 | 판단 기록 alphabet.F1.search |
| `alphabet` | ① 네트워크 | 판단 기록 alphabet.F1.youtube_ads |
| `alphabet` | ② 게임체인저 | 판단 기록 alphabet.F2.cloud |
| `alphabet` | ② 게임체인저 | 판단 기록 alphabet.F2.application |
| `alphabet` | ② 게임체인저 | 판단 기록 alphabet.F2.user_platform |
| `alphabet` | ③ 카운터포지셔닝 | 판단 기록 alphabet.F3.cloud |
| `alphabet` | ③ 카운터포지셔닝 | 판단 기록 alphabet.F3.application |
| `alphabet` | ③ 카운터포지셔닝 | 판단 기록 alphabet.F3.user_platform |
| `alphabet` | ④ 호황 이후 | 판단 기록 alphabet.F4 |
| `alphabet` | ⑤ 아군 | 판단 기록 alphabet.F5 |
| `alphabet` | ⑦ 순환금융 | 판단 기록 alphabet.F7 |
| `alphabet` | ⑧ 비대칭 의존 | 판단 기록 alphabet.F8 |
| `alphabet` | ⑨ 적자 깊이 | 판단 기록 alphabet.F9 |
| `amazon` | ① 네트워크 | 판단 기록 amazon.F1.advertising |
| `amazon` | ① 네트워크 | 판단 기록 amazon.F1.aws |
| `amazon` | ① 네트워크 | 판단 기록 amazon.F1.online_store |
| `amazon` | ① 네트워크 | 판단 기록 amazon.F1.other |
| `amazon` | ① 네트워크 | 판단 기록 amazon.F1.physical_stores |
| `amazon` | ① 네트워크 | 판단 기록 amazon.F1.subscriptions |
| `amazon` | ① 네트워크 | 판단 기록 amazon.F1.third_party_seller |
| `amazon` | ② 게임체인저 | 판단 기록 amazon.F2.cloud |
| `amazon` | ② 게임체인저 | 판단 기록 amazon.F2.user_platform |
| `amazon` | ② 게임체인저 | 판단 기록 amazon.F2.outside |
| `amazon` | ③ 카운터포지셔닝 | 판단 기록 amazon.F3.cloud |
| `amazon` | ③ 카운터포지셔닝 | 판단 기록 amazon.F3.user_platform |
| `amazon` | ③ 카운터포지셔닝 | 판단 기록 amazon.F3.outside |
| `amazon` | ④ 호황 이후 | 판단 기록 amazon.F4 |
| `amazon` | ⑤ 아군 | 판단 기록 amazon.F5 |
| `amazon` | ⑦ 순환금융 | 판단 기록 amazon.F7 |
| `amazon` | ⑧ 비대칭 의존 | 판단 기록 amazon.F8 |
| `amazon` | ⑨ 적자 깊이 | 판단 기록 amazon.F9.obsreg25 |
| `anthropic` | ① 네트워크 | 판단 기록 anthropic.F1.claude |
| `anthropic` | ② 게임체인저 | 판단 기록 anthropic.F2.model |
| `anthropic` | ③ 카운터포지셔닝 | 판단 기록 anthropic.F3.model |
| `anthropic` | ④ 호황 이후 | 판단 기록 anthropic.F4 |
| `anthropic` | ⑤ 아군 | 판단 기록 anthropic.F5 |
| `anthropic` | ⑦ 순환금융 | 판단 기록 anthropic.F7 |
| `anthropic` | ⑧ 비대칭 의존 | 판단 기록 anthropic.F8 |
| `anthropic` | ⑨ 적자 깊이 | 판단 기록 anthropic.F9 |
| `apple` | ① 네트워크 | 판단 기록 apple.F1.iphone_services |
| `apple` | ① 네트워크 | 판단 기록 apple.F1.mac |
| `apple` | ① 네트워크 | 판단 기록 apple.F1.wearables_home_accessories |
| `apple` | ② 게임체인저 | 판단 기록 apple.F2.user_platform |
| `apple` | ② 게임체인저 | 판단 기록 apple.F2.device |
| `apple` | ③ 카운터포지셔닝 | 판단 기록 apple.F3.user_platform |
| `apple` | ③ 카운터포지셔닝 | 판단 기록 apple.F3.device |
| `apple` | ④ 호황 이후 | 판단 기록 apple.F4 |
| `apple` | ⑤ 아군 | 판단 기록 apple.F5 |
| `apple` | ⑦ 순환금융 | 판단 기록 apple.F7 |
| `apple` | ⑧ 비대칭 의존 | 판단 기록 apple.F8 |
| `apple` | ⑨ 적자 깊이 | 판단 기록 apple.F9 |
| `meta` | ① 네트워크 | 판단 기록 meta.F1.advertising |
| `meta` | ① 네트워크 | 판단 기록 meta.F1.other_revenue |
| `meta` | ① 네트워크 | 판단 기록 meta.F1.reality_labs |
| `meta` | ② 게임체인저 | 판단 기록 meta.F2.user_platform |
| `meta` | ② 게임체인저 | 판단 기록 meta.F2.device |
| `meta` | ③ 카운터포지셔닝 | 판단 기록 meta.F3.user_platform |
| `meta` | ③ 카운터포지셔닝 | 판단 기록 meta.F3.device |
| `meta` | ④ 호황 이후 | 판단 기록 meta.F4 |
| `meta` | ⑤ 아군 | 판단 기록 meta.F5 |
| `meta` | ⑦ 순환금융 | 판단 기록 meta.F7 |
| `meta` | ⑧ 비대칭 의존 | 판단 기록 meta.F8 |
| `meta` | ⑨ 적자 깊이 | 판단 기록 meta.F9 |
| `microsoft` | ① 네트워크 | 판단 기록 microsoft.F1.dynamics |
| `microsoft` | ① 네트워크 | 판단 기록 microsoft.F1.enterprise_partner_services |
| `microsoft` | ① 네트워크 | 판단 기록 microsoft.F1.linkedin |
| `microsoft` | ① 네트워크 | 판단 기록 microsoft.F1.m365_commercial |
| `microsoft` | ① 네트워크 | 판단 기록 microsoft.F1.m365_consumer |
| `microsoft` | ① 네트워크 | 판단 기록 microsoft.F1.other |
| `microsoft` | ① 네트워크 | 판단 기록 microsoft.F1.search_advertising |
| `microsoft` | ① 네트워크 | 판단 기록 microsoft.F1.server_cloud |
| `microsoft` | ① 네트워크 | 판단 기록 microsoft.F1.windows_devices |
| `microsoft` | ① 네트워크 | 판단 기록 microsoft.F1.xbox |
| `microsoft` | ② 게임체인저 | 판단 기록 microsoft.F2.cloud |
| `microsoft` | ② 게임체인저 | 판단 기록 microsoft.F2.application |
| `microsoft` | ② 게임체인저 | 판단 기록 microsoft.F2.user_platform |
| `microsoft` | ② 게임체인저 | 판단 기록 microsoft.F2.outside |
| `microsoft` | ③ 카운터포지셔닝 | 판단 기록 microsoft.F3.cloud |
| `microsoft` | ③ 카운터포지셔닝 | 판단 기록 microsoft.F3.application |
| `microsoft` | ③ 카운터포지셔닝 | 판단 기록 microsoft.F3.user_platform |
| `microsoft` | ③ 카운터포지셔닝 | 판단 기록 microsoft.F3.outside |
| `microsoft` | ④ 호황 이후 | 판단 기록 microsoft.F4 |
| `microsoft` | ⑤ 아군 | 판단 기록 microsoft.F5 |
| `microsoft` | ⑦ 순환금융 | 판단 기록 microsoft.F7 |
| `microsoft` | ⑧ 비대칭 의존 | 판단 기록 microsoft.F8 |
| `microsoft` | ⑨ 적자 깊이 | 판단 기록 microsoft.F9 |
| `nvidia` | ① 네트워크 | 판단 기록 nvidia.F1.data_center |
| `nvidia` | ① 네트워크 | 판단 기록 nvidia.F1.edge_computing |
| `nvidia` | ② 게임체인저 | 판단 기록 nvidia.F2.chip_design |
| `nvidia` | ③ 카운터포지셔닝 | 판단 기록 nvidia.F3.chip_design |
| `nvidia` | ④ 호황 이후 | 판단 기록 nvidia.F4 |
| `nvidia` | ⑤ 아군 | 판단 기록 nvidia.F5 |
| `nvidia` | ⑦ 순환금융 | 판단 기록 nvidia.F7.fix52 |
| `nvidia` | ⑧ 비대칭 의존 | 판단 기록 nvidia.F8 |
| `nvidia` | ⑨ 적자 깊이 | 판단 기록 nvidia.F9 |
| `openai` | ① 네트워크 | 판단 기록 openai.F1.chatgpt_api |
| `openai` | ② 게임체인저 | 판단 기록 openai.F2.model |
| `openai` | ③ 카운터포지셔닝 | 판단 기록 openai.F3.model |
| `openai` | ④ 호황 이후 | 판단 기록 openai.F4 |
| `openai` | ⑤ 아군 | 판단 기록 openai.F5.impl48 |
| `openai` | ⑦ 순환금융 | 판단 기록 openai.F7 |
| `openai` | ⑧ 비대칭 의존 | 판단 기록 openai.F8 |
| `openai` | ⑨ 적자 깊이 | 판단 기록 openai.F9 |
| `oracle` | ① 네트워크 | 판단 기록 oracle.F1.cloud_applications |
| `oracle` | ① 네트워크 | 판단 기록 oracle.F1.hardware |
| `oracle` | ① 네트워크 | 판단 기록 oracle.F1.oci |
| `oracle` | ① 네트워크 | 판단 기록 oracle.F1.services |
| `oracle` | ① 네트워크 | 판단 기록 oracle.F1.software |
| `oracle` | ② 게임체인저 | 판단 기록 oracle.F2.cloud |
| `oracle` | ② 게임체인저 | 판단 기록 oracle.F2.data_platform |
| `oracle` | ② 게임체인저 | 판단 기록 oracle.F2.application |
| `oracle` | ② 게임체인저 | 판단 기록 oracle.F2.outside |
| `oracle` | ③ 카운터포지셔닝 | 판단 기록 oracle.F3.cloud |
| `oracle` | ③ 카운터포지셔닝 | 판단 기록 oracle.F3.data_platform |
| `oracle` | ③ 카운터포지셔닝 | 판단 기록 oracle.F3.application |
| `oracle` | ③ 카운터포지셔닝 | 판단 기록 oracle.F3.outside |
| `oracle` | ④ 호황 이후 | 판단 기록 oracle.F4 |
| `oracle` | ⑤ 아군 | 판단 기록 oracle.F5 |
| `oracle` | ⑦ 순환금융 | 판단 기록 oracle.F7.fix52 |
| `oracle` | ⑧ 비대칭 의존 | 판단 기록 oracle.F8 |
| `oracle` | ⑨ 적자 깊이 | 판단 기록 oracle.F9 |
| `palantir` | ① 네트워크 | 판단 기록 palantir.F1.commercial |
| `palantir` | ① 네트워크 | 판단 기록 palantir.F1.government |
| `palantir` | ② 게임체인저 | 판단 기록 palantir.F2.data_platform |
| `palantir` | ③ 카운터포지셔닝 | 판단 기록 palantir.F3.data_platform |
| `palantir` | ④ 호황 이후 | 판단 기록 palantir.F4 |
| `palantir` | ⑤ 아군 | 판단 기록 palantir.F5 |
| `palantir` | ⑦ 순환금융 | 판단 기록 palantir.F7 |
| `palantir` | ⑧ 비대칭 의존 | 판단 기록 palantir.F8 |
| `palantir` | ⑨ 적자 깊이 | 판단 기록 palantir.F9 |
| `spacex-xai` | ① 네트워크 | 판단 기록 spacex-xai.F1.ai_solutions_infrastructure |
| `spacex-xai` | ① 네트워크 | 판단 기록 spacex-xai.F1.starlink_consumer |
| `spacex-xai` | ① 네트워크 | 판단 기록 spacex-xai.F1.starlink_enterprise_government |
| `spacex-xai` | ① 네트워크 | 판단 기록 spacex-xai.F1.x_advertising |
| `spacex-xai` | ② 게임체인저 | 판단 기록 spacex-xai.F2.cloud |
| `spacex-xai` | ② 게임체인저 | 판단 기록 spacex-xai.F2.user_platform |
| `spacex-xai` | ② 게임체인저 | 판단 기록 spacex-xai.F2.outside |
| `spacex-xai` | ③ 카운터포지셔닝 | 판단 기록 spacex-xai.F3.cloud |
| `spacex-xai` | ③ 카운터포지셔닝 | 판단 기록 spacex-xai.F3.user_platform |
| `spacex-xai` | ③ 카운터포지셔닝 | 판단 기록 spacex-xai.F3.outside |
| `spacex-xai` | ④ 호황 이후 | 판단 기록 spacex-xai.F4 |
| `spacex-xai` | ⑤ 아군 | 판단 기록 spacex-xai.F5 |
| `spacex-xai` | ⑦ 순환금융 | 판단 기록 spacex-xai.F7 |
| `spacex-xai` | ⑧ 비대칭 의존 | 판단 기록 spacex-xai.F8 |
| `spacex-xai` | ⑨ 적자 깊이 | 판단 기록 spacex-xai.F9 |
| `tesla` | ① 네트워크 | 판단 기록 tesla.F1.energy |
| `tesla` | ① 네트워크 | 판단 기록 tesla.F1.regulatory_credits |
| `tesla` | ① 네트워크 | 판단 기록 tesla.F1.services_other |
| `tesla` | ① 네트워크 | 판단 기록 tesla.F1.vehicles |
| `tesla` | ② 게임체인저 | 판단 기록 tesla.F2.power |
| `tesla` | ② 게임체인저 | 판단 기록 tesla.F2.device |
| `tesla` | ② 게임체인저 | 판단 기록 tesla.F2.outside |
| `tesla` | ③ 카운터포지셔닝 | 판단 기록 tesla.F3.power |
| `tesla` | ③ 카운터포지셔닝 | 판단 기록 tesla.F3.device |
| `tesla` | ③ 카운터포지셔닝 | 판단 기록 tesla.F3.outside |
| `tesla` | ④ 호황 이후 | 판단 기록 tesla.F4 |
| `tesla` | ⑤ 아군 | 판단 기록 tesla.F5 |
| `tesla` | ⑦ 순환금융 | 판단 기록 tesla.F7 |
| `tesla` | ⑧ 비대칭 의존 | 판단 기록 tesla.F8 |
| `tesla` | ⑨ 적자 깊이 | 판단 기록 tesla.F9 |
| `tsmc` | ① 네트워크 | 판단 기록 tsmc.F1.automotive |
| `tsmc` | ① 네트워크 | 판단 기록 tsmc.F1.dce |
| `tsmc` | ① 네트워크 | 판단 기록 tsmc.F1.hpc |
| `tsmc` | ① 네트워크 | 판단 기록 tsmc.F1.iot |
| `tsmc` | ① 네트워크 | 판단 기록 tsmc.F1.others |
| `tsmc` | ① 네트워크 | 판단 기록 tsmc.F1.smartphone |
| `tsmc` | ② 게임체인저 | 판단 기록 tsmc.F2.foundry |
| `tsmc` | ③ 카운터포지셔닝 | 판단 기록 tsmc.F3.foundry |
| `tsmc` | ④ 호황 이후 | 판단 기록 tsmc.F4 |
| `tsmc` | ⑤ 아군 | 판단 기록 tsmc.F5 |
| `tsmc` | ⑦ 순환금융 | 판단 기록 tsmc.F7 |
| `tsmc` | ⑧ 비대칭 의존 | 판단 기록 tsmc.F8 |
| `tsmc` | ⑨ 적자 깊이 | 판단 기록 tsmc.F9 |

## 규칙 파일의 항목 메모

리포트 본문의 `무엇을 보고 매기는가` 는 ①~⑤ 는 규칙 값으로 쓴 판정 재료이고 나머지는 항목 설명 원문(`scorecard/factor-concepts.json`)에서 가져온다. 이 표는 규칙 JSON 의 `factors.*.note` 원문이며 **결정 번호와 작업 경위가 섞여 있어 본문에 싣지 않는다.** 규칙 파일과 대조할 때 쓴다.

| 항목 | `note` 원문 |
| --- | --- |
| `F1` ① 네트워크 | 사업 점수 = A + B + C + D + E (0~20). 층 점수 = 그 층 안 사업 점수의 매출 몫 평균. 회사 ① = 층 점수의 층 매출 몫 가중 평균 |
| `F2` ② 게임체인저 | 층 점수 = 성능 도약 0~10 + 패러다임 적응 0~5 + 표준 선점 0~5. 벤치마크가 없는 층은 (적응 + 표준) × 2 |
| `F3` ③ 카운터포지셔닝 | 층 점수 = 별도 수익모델 0~6 + 모방 불가능성 0~8 + 가속도 0~6, 관문 셋. 공짜 전략은 돈을 거둬들이는 판매 층에서 센다 |
| `F4` ④ 호황 이후 | ④ = 수직계열화 0~8 + 다각화 매출 몫 0~8 + 그 분야의 힘 0~4. 층 매출 몫(①②③ 의 무게)의 원천도 이 판단의 매출 줄이다 |
| `F5` ⑤ 아군 | ⑤ = 12(중립점) + 동맹 0~8 + 적대 −12~0. 금액은 쓰지 않는다. 한 관계는 한 부분에서만 센다 |
| `F6` ⑥ 가격 | v3.0: 이전 규칙 × 4 를 기준점으로 잇는 연속값(policies.f6 의 curve). 구간표는 같은 기준점을 4배 한 값으로 남는다 |

## 내부 표기

리포트 본문은 이름을 쓰고 번호는 쓰지 않는다. 코드·규칙 파일과 대조할 때 쓰는 표다.

| 번호 | 리포트 표기 |
| --- | --- |
| `P1` | PER |
| `P2` | EV/매출 |
| `P3` | 매출 성장 |
| `P4` | 입력 신뢰도 |
| `G1` | 본업 |
| `G2` | 현금 |
| `G3` | 런웨이 |
| `G4` | 약정 커버리지 |
