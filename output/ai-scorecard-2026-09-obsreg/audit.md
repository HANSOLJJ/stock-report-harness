# 감사 기록 — AI 기업 9-factor 채점표 — SEC 실측 관측 반영(v1.7)

이 파일은 **재현과 감사를 위한 기록**이다. 리포트 본문에서 뺀 해시·입력 지문·실행 단위 선택을 모은다.
리포트는 `output/ai-scorecard-2026-09-obsreg.html` 이고 여기 값들이 그 리포트를 만든 입력이다.

## 규칙과 기준 시점

- 규칙 `v1.7` · 해시 `345c3353372d0f95d98eef5ed918c31e7a3f7878185a24f1e4edfa9870d58d21`
- 원본 파일 `AI기업_채점규칙_v1.5.md`
- 분석 기준일 · 가격 기준일 · 정보 컷오프가 모두 `2026-09-02` 로 같다
- 승계 근거와 트리거에는 컷오프 이후 사건이 원문 그대로 남아 있고 이번 실행에서 재검증하지 않았다.

## 입력 해시

| 대상 | 해시 |
| --- | --- |
| observations | `02dcd2ab605542d8bb2b14a2f956eb4d38d4e764df409087bec2c67409f53b05` |
| judgments | `2403fb3748edd85310c299ef3022ae756a6a25f2f5664db1f05ab767ebf325d6` |
| results | `4a3f6c05b206ef81f370ac7765a1a948fe1e9cf6d1999c142bac4f124e04910b` |
| run | `71a83f40e92ea8969da919e9a07ff9561cd60b72e6b934a1d2678367922129be` |
| draft | `94215e94def972072ea280547adfcb3acbf11241fcfb2d2a1e1e69c64ad64dfb` |

## 승인

- 승인 `776a511bf0a9028f` · 사용자 · 2026-09-21
- 승인 시점 입력과 현재 입력이 모두 같다.

## 실행 단위 결정

규칙이 미결로 둔 항목 중 이번 실행에서 고른 선택이다. **목록에 있다고 그 선택을 계산이 실제로 읽었다는 뜻은 아니다** — 소비 여부는 각 항목의 산식과 경고에서 확인한다.

| 결정 | 이번 실행 선택 |
| --- | --- |
| `C-05` | `apply` |
| `C-06` | `proposed_v15_boundaries` |
| `C-16` | `downgrade` |
| `C-12` | `p2_with_capped_promotion` |
| `C-20` | `defer_to_private_g2` |
| `C-03` | `paths_with_generation_gap_5` |
| `C-11` | `block_carryover` |
| `C-13` | `reject_proxy` |
| `C-24` | `compute_p2_when_inputs_exist` |
| `C-28` | `optional_parameters_for_all_listed_tracks` |
| `C-29` | `c20_private_route_first` |

## 미결 규칙 결정

아직 확정되지 않은 규칙 항목이다. 걸린 항목은 점수를 만들지 않고 대기 상태로 남는다.

| 결정 | 요약 | 권고 | 이번 실행 |
| --- | --- | --- | --- |
| `C-05` | G1 실패 뒤 G3·G4 를 추가 감점하는지 진단만 하는지 원문이 혼재 | diagnose_only 또는 apply 를 결정. 결과가 달라지는 기업만 대기 처리 | apply |
| `C-06` | 손실률 -10%·-30% 경계 중첩, FCF/영업손익 0, 완충 잠식, G2 안정/악화의 기계 정의 부재. [FIX-63 정정 · obsreg 9차 재무 계산 재판정 2회(Claude 독립 세션) medium] **BEP 후퇴의 우선순위는 미결이 아니다.** 사용자 결정 2026-09-17(C-29)로 `policies.f9.g1_bep_retreat_precedence` 에 명문화했다 — **C-20 비상장 경로가 먼저 서고**, 상장사이거나 영업손익이 구조적 미공시가 아닌 경우에만 BEP 후퇴가 **G1 통과·손실률 밴드 둘 다보다 앞서** `g1_bep_retreat_score` 를 준다. 점수도 -5 가 아니라 **-4** 다(C-06 재척도). **그 자리에서는 순서가 결과를 가른다** — 손실률이 최심 밴드(-30% 초과)가 아니면 밴드 점수와 다른 값이 나오고, **영업흑자여도 통과하지 못하고 하한을 받는다**(TEN-RA6-01). 남은 미결은 FCF·영업손익 0 처리와 완충 잠식·G2 추세의 기계 정의다 | policies.f9.g1_bands_proposed 와 BEP 우선 규칙을 검토해 전 구간 명문화 | proposed_v15_boundaries |
| `C-16` | G4 판정 불가→하향 규칙과 Alibaba·SpaceX 보류 유지 사례가 다름 | 결측 유형·적용 대상·하향 중복 방지 규칙 확정 | downgrade |

## 검토 기록

검토 방식 `separate-session-4way` · 실행 `separate_subagent_sessions` · 검토한 초안 `94215e94def972072ea280547adfcb3acbf11241fcfb2d2a1e1e69c64ad64dfb`

- fact-sources: pass (8차 · Gemini 독립 세션)
- financial-calc: pass (9차 · Claude 독립 세션 · 재판정 3회 · 최종 기준 커밋 f313060) — 8차 needs_fix 에서 FIX-59·61·63 반영을 거쳐 pass. 잔존 전수 0건 · 재계산 14개사 불일치 0 · 점수 페이로드 96afd80 과 바이트 동일
- rule-consistency: pass (8차 · Gemini 독립 세션 — FIX-61~64 의 규칙 문면 변경은 미검토)
- output-readability: pass (8차 · Gemini 독립 세션, low 둘 반영 — HTML 은 build 에서 재생성)

## 정정 이력

본문은 정정된 현재 내용만 싣는다. 언제 어느 과제로 고쳤는지는 여기 원문으로 남긴다.

- [정정 2026-09-15 FIX-53]
- [FIX-53 3단계 라벨 정정: 10-Q Note 1 문면은 `expansion of … existing multi-year commitment by more than $100.0 billion over 10.0 years` — 기존 다년 약정 **위의 증액**이고 `more than` 이라 **하한**이다. $100B/10년은 약정 총액이 아니다. $300B 합계는 v1.5 기준선 값(HANDOVER 51행). `연 ~$50B`·`ARR $65B의 77%`·`커버리지 1.3배` 는 약정 하한 기준 환산 — 약정이 더 크면 커버리지는 1.3배보다 낮다]

## 다시 볼 것(긴장)

| 번호 | 무엇 | 걸린 판단 | 다시 볼 때 | 상태 |
| --- | --- | --- | --- | --- |
| `TEN-RA-02` | nvidia F2 5점의 성능 근거가 벤더 발표이고 같은 실행 안에서 시점이 반증된다 | nvidia.F2 | 2026-11 | 대기 |
| `TEN-RA3-01` | openai F4 4점의 3→4 상향 근거가 이해당사자 발표이고 배치 계획이 섞였다 | openai.F4 | 2026-11 | 대기 |
| `TEN-RA4-01` | F2 근거란이 모델 간 성능을 비교하면서 어느 하네스로 잰 값인지 적지 않는다 — 채점규칙 22행 `비교는 같은 하네스끼리만` 을 확인할 수 없다 | anthropic.F2, meta.F2, alibaba.F2, openai.F2 | 2026-11 | 대기 |
| `TEN-RA5-01` | anthropic.F8 이 -4 로 내려가지 않는 유일한 근거(`Alphabet 제출본에 Anthropic 0건`)를 확인할 수 없다 | anthropic.F8 | 2026-11 | 대기 |
| `TEN-RA5-02` | BEP 후퇴가 C-20 비상장 판정보다 앞서는 것이 맞는지 — v1.5 안에서 두 문면이 충돌한다 | openai.F9 | 2026-11 | 해소 2026-09-17 |
| `TEN-RA6-01` | 채점규칙 470행(BEP 목표 후퇴 = 독립 감점 조건)과 별표 D 388~390행(계획·발표·포지션은 0점)이 v1.5 안에서 충돌한다 | openai.F9 | 2026-11 | 대기 |
| `TEN-RB-Q10` | F3 가속도가 단일 성장률 하나로 pass — 성장률의 변화(가속)를 재현할 수 없다 | microsoft.F3, spacex-xai.F3, tesla.F3, amazon.F3, palantir.F3 | 2026-11 | 대기 |
| `TEN-RC-02` | anthropic F1 — 주채널을 업무로 적고도 개인 사용자 절대수 열세로 5점을 막는다 | anthropic.F1 | 2026-11 | 대기 |
| `TEN-RC-03` | C-08 — 별표 H 이탈 조건의 허용·제외 기준이 F5 전사에 통일되지 않았다 | nvidia.F5, openai.F5.impl48, amazon.F5, meta.F5, anthropic.F5.impl48 | 2026-11 | 대기 |
| `TEN-RC-05` | nvidia F5·F8 — 고객 40% 자체 칩 이탈이라는 같은 속성이 F5 H -2 와 F8 -3 에 반복된다 | nvidia.F5, nvidia.F8 | 2026-11 | 대기 |
| `TEN-RC3-01` | anthropic·openai F7 — 매트릭스 입력 없이 -1 을 승계했고 v1.5 매트릭스와 판정표가 서로 어긋난다 | anthropic.F7, openai.F7 | 2026-11 | 대기 |
| `TEN-RC3-03` | palantir·oracle F1 — 업무 채널 전환비용을 한쪽은 가짜 해자로 빼고 한쪽은 락인으로 인정한다 | palantir.F1, oracle.F1 | 2026-11 | 대기 |
| `TEN-RC3-04` | tesla F5·F8 — NHTSA 조사라는 같은 속성이 F5 H -1 과 F8 -2 에 반복된다 | tesla.F5, tesla.F8 | 2026-11 | 대기 |
| `TEN-RC3-05` | alibaba F3 — 경쟁사 두 곳이 이미 오픈웨이트를 내는데 모방 불가능성이 partial 이다 | alibaba.F3 | 2026-11 | 대기 |
| `TEN-RC4-01` | meta·anthropic·spacex-xai 의 F3 `imitation=partial` 이 partial 의 정의를 채우지 못한다 | meta.F3, anthropic.F3, spacex-xai.F3 | 2026-11 | 대기 |
| `TEN-RC4-02` | openai F1 — 주채널은 소비자라고 적고 4점을 막는 근거는 거래 채널이다 | openai.F1 | 2026-11 | 대기 |
| `TEN-RC4-03` | spacex-xai F5 H=-1 의 근거가 적대의 종류가 아니라 수 비교다 | spacex-xai.F5 | 2026-11 | 대기 |
| `TEN-RC4-04` | tsmc F3 가속도 pass 의 근거가 가이던스(계획)다 | tsmc.F3 | 2026-11 | 대기 |

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
| `C-12` | 미결 | 비상장 F6 가 배수만 vs TTM 보정·이익·자본효율로 점수를 가름이 공존 | 비상장 최종 점수는 정성 예외(manual_with_rationale) | 배수 구간표 + 한 칸 상한 보정 (`p2_with_capped_promotion`) | ⑥ 가격 |
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

## 기업·항목별 작업 이력

리포트 본문의 근거는 **무엇을 보고 그 점수를 주었는지**만 싣는다. 언제 어느 과제로 표기가 바뀌었는지는 근거가 아니라 이력이라 여기로 옮겼다. 본문 근거 문장 자체는 그대로 남아 있다.

| 기업 | 항목 | 작업 표기 |
| --- | --- | --- |
| `alibaba` | ① 네트워크 | 판단 기록 alibaba.F1 |
| `alibaba` | ② 게임체인저 | 판단 기록 alibaba.F2 |
| `alibaba` | ② 게임체인저 | [FIX-56 2단계] |
| `alibaba` | ② 게임체인저 | 채점표 375행 |
| `alibaba` | ② 게임체인저 | 채점표 943행 |
| `alibaba` | ② 게임체인저 | 채점규칙 22행 |
| `alibaba` | ② 게임체인저 | anthropic.F2 |
| `alibaba` | ② 게임체인저 | 5차 리뷰 A |
| `alibaba` | ③ Last Mover | 판단 기록 alibaba.F3 |
| `alibaba` | ④ 호황 이후 | 판단 기록 alibaba.F4 |
| `alibaba` | ⑤ 아군 | 판단 기록 alibaba.F5 |
| `alibaba` | ⑥ 가격 | v1.5 참고 문면: **이번 실행 점수는 -4 이고 입력에서 자동 산출한 값이다**(위 산식 참조). 아래는 기준선 v1.5 문면이라 다른 수가 섞여 있을 수 있다 — 점수 근거가 아니다. |
| `alibaba` | ⑥ 가격 | v1.5 참고 문면: NTM PER 16.7(상장 12사 최저 — SA 데이터 CNY/USD 혼재라 FY27 $5.71·FY28 $8.03을 7:5 가중 직접 계산) |
| `alibaba` | ⑥ 가격 | v1.5 참고 문면: 증자 후 시총 $270B |
| `alibaba` | ⑥ 가격 | v1.5 참고 문면: TTM 25.8은 영업외 54%로 무효 |
| `alibaba` | ⑥ 가격 | v1.5 참고 문면: P/S 1.8 참고 |
| `alibaba` | ⑥ 가격 | v1.5 참고 문면: 팔란티어 시총($407B)이 알리바바보다 50% 크다 |
| `alibaba` | ⑦ 순환금융 | 판단 기록 alibaba.F7 |
| `alibaba` | ⑧ 비대칭 의존 | 판단 기록 alibaba.F8 |
| `alibaba` | ⑨ 적자 깊이 | 판단 기록 alibaba.F9.obsreg25 |
| `alibaba` | ⑨ 적자 깊이 | [FIX-54 1단계] |
| `alibaba` | ⑨ 적자 깊이 | [FIX-54 2단계] |
| `alibaba` | ⑨ 적자 깊이 | OBS-REG-25 지시서 G1-TTM-26 |
| `alibaba` | ⑨ 적자 깊이 | alibaba.fcf_ttm.cashfcf35 |
| `alibaba` | ⑨ 적자 깊이 | alibaba.cash.cashfcf35 |
| `alibaba` | ⑨ 적자 깊이 | alibaba.undrawn_credit.fix53 |
| `alphabet` | ① 네트워크 | 판단 기록 alphabet.F1 |
| `alphabet` | ② 게임체인저 | 판단 기록 alphabet.F2 |
| `alphabet` | ③ Last Mover | 판단 기록 alphabet.F3 |
| `alphabet` | ④ 호황 이후 | 판단 기록 alphabet.F4 |
| `alphabet` | ⑤ 아군 | 판단 기록 alphabet.F5 |
| `alphabet` | ⑥ 가격 | v1.5 참고 문면: **이번 실행 점수는 -3 이고 입력에서 자동 산출한 값이다**(위 산식 참조). 아래는 기준선 v1.5 문면이라 다른 수가 섞여 있을 수 있다 — 점수 근거가 아니다. |
| `alphabet` | ⑥ 가격 | v1.5 참고 문면: (v1.5: 구간 재설계 — 20~29) NTM PER 25.3 — 20~29 구간, 경계에서 벗어남(29선까지 12.8%) |
| `alphabet` | ⑥ 가격 | v1.5 참고 문면: TTM 16.9는 영업외 비중 51%로 무효 |
| `alphabet` | ⑥ 가격 | v1.5 참고 문면: P/S 9.3 참고 |
| `alphabet` | ⑦ 순환금융 | 판단 기록 alphabet.F7 |
| `alphabet` | ⑧ 비대칭 의존 | 판단 기록 alphabet.F8 |
| `alphabet` | ⑨ 적자 깊이 | 판단 기록 alphabet.F9 |
| `amazon` | ① 네트워크 | 판단 기록 amazon.F1 |
| `amazon` | ② 게임체인저 | 판단 기록 amazon.F2 |
| `amazon` | ③ Last Mover | 판단 기록 amazon.F3 |
| `amazon` | ④ 호황 이후 | 판단 기록 amazon.F4 |
| `amazon` | ⑤ 아군 | 판단 기록 amazon.F5 |
| `amazon` | ⑥ 가격 | v1.5 참고 문면: **이번 실행 점수는 -2 이고 입력에서 자동 산출한 값이다**(위 산식 참조). 아래는 기준선 v1.5 문면이라 다른 수가 섞여 있을 수 있다 — 점수 근거가 아니다. |
| `amazon` | ⑥ 가격 | v1.5 참고 문면: (v1.5: 구간 재설계 — 20~29) NTM PER 27.5 — 29선까지 5.2% |
| `amazon` | ⑥ 가격 | v1.5 참고 문면: TTM 20.5는 영업외 46%로 무효 |
| `amazon` | ⑥ 가격 | v1.5 참고 문면: P/S 3.6(빅테크 최저) 참고 |
| `amazon` | ⑦ 순환금융 | 판단 기록 amazon.F7 |
| `amazon` | ⑧ 비대칭 의존 | 판단 기록 amazon.F8 |
| `amazon` | ⑨ 적자 깊이 | 판단 기록 amazon.F9.obsreg25 |
| `amazon` | ⑨ 적자 깊이 | OBS-REG-25 지시서 |
| `amazon` | ⑨ 적자 깊이 | amazon.offbalance_B.obsreg25 |
| `anthropic` | ① 네트워크 | 판단 기록 anthropic.F1 |
| `anthropic` | ② 게임체인저 | 판단 기록 anthropic.F2 |
| `anthropic` | ② 게임체인저 | [FIX-53 3단계] |
| `anthropic` | ② 게임체인저 | [FIX-55 2단계] [FIX-56 2단계] |
| `anthropic` | ② 게임체인저 | 채점규칙 22행 |
| `anthropic` | ② 게임체인저 | openai.F2 |
| `anthropic` | ② 게임체인저 | TEN-RA4-01 |
| `anthropic` | ② 게임체인저 | meta.F2 |
| `anthropic` | ② 게임체인저 | alibaba.F2 |
| `anthropic` | ③ Last Mover | 판단 기록 anthropic.F3 |
| `anthropic` | ④ 호황 이후 | 판단 기록 anthropic.F4 |
| `anthropic` | ⑤ 아군 | 판단 기록 anthropic.F5.impl48 |
| `anthropic` | ⑤ 아군 | [F5-IMPL-48 재판정 2026-09-14] |
| `anthropic` | ⑤ 아군 | 채점규칙 727행 |
| `anthropic` | ⑤ 아군 | 별표 H 288행 |
| `anthropic` | ⑤ 아군 | anthropic.F5 |
| `anthropic` | ⑤ 아군 | a01f127 |
| `anthropic` | ⑤ 아군 | 1aab1f2 |
| `anthropic` | ⑥ 가격 | v1.5 참고 문면: **이번 실행 점수는 -4 이고 입력에서 자동 산출한 값이다**(위 산식 참조). 아래는 기준선 v1.5 문면이라 다른 수가 섞여 있을 수 있다 — 점수 근거가 아니다. |
| `anthropic` | ⑥ 가격 | v1.5 참고 문면: -3 (v1.5: ARR 보정 + 자본효율 반영) |
| `anthropic` | ⑥ 가격 | v1.5 참고 문면: post-money $965B ÷ ARR $65B(7월) = 14.8배 — 그러나 ARR은 런레이트라 TTM 매출보다 과대하다. 분모를 TTM으로 맞추면 약 30~39배(Q2 매출 $10.9B 역산) = Palantir(TTM P/S 66.2, ⑥-4)의 절반 수준 |
| `anthropic` | ⑥ 가격 | v1.5 참고 문면: (참고) 이익 기준 $965B ÷ 연환산 영업이익 약 $2.2B = 약 440배, Palantir NTM PER 89의 5배 |
| `anthropic` | ⑥ 가격 | v1.5 참고 문면: 자본효율 0.52(ARR $65B ÷ 누적 조달 약 $125B) — 비상장 3사 중 최선 |
| `anthropic` | ⑥ 가격 | v1.5 참고 문면: 주의 — 정밀도 열위, 10월 IPO 예상 시 상장사 룰로 자동 전환 |
| `anthropic` | ⑥ 가격 | anthropic.post_money_valuation.v15 |
| `anthropic` | ⑥ 가격 | anthropic.arr.v15 |
| `anthropic` | ⑥ 가격 | anthropic.arr_prior.priv31 |
| `anthropic` | ⑥ 가격 | anthropic.cumulative_raised.priv31 |
| `anthropic` | ⑥ 가격 | anthropic.ps_ratio.priv31 |
| `anthropic` | ⑦ 순환금융 | 판단 기록 anthropic.F7 |
| `anthropic` | ⑧ 비대칭 의존 | 판단 기록 anthropic.F8.f8anth33 |
| `anthropic` | ⑧ 비대칭 의존 | [FIX-58 2단계] [FIX-59 정정] |
| `anthropic` | ⑧ 비대칭 의존 | FIX-53 |
| `anthropic` | ⑧ 비대칭 의존 | [FIX-53 3단계 라벨 정정: 10-Q Note 1 문면은 `expansion of … existing multi-year commitment by more than $100.0 billion over 10.0 years` — 기존 다년 약정 **위의 증액**이고 `more than` 이라 **하한**이다. $100B/10년은 약정 총액이 아니다. $300B 합계는 v1.5 기준선 값(HANDOVER 51행). `(연 ~$10B)` 는 이 라벨에서 나온 **약정 하한 기준 환산**이다] |
| `anthropic` | ⑧ 비대칭 의존 | F8-ANTH-33 |
| `anthropic` | ⑧ 비대칭 의존 | [FIX-58 2단계] |
| `anthropic` | ⑧ 비대칭 의존 | ff75add:validation/mcap-36-2026-09-11/raw/cover-alphabet-R1.htm.htm |
| `anthropic` | ⑧ 비대칭 의존 | 7차 리뷰 A |
| `anthropic` | ⑧ 비대칭 의존 | TEN-RA5-01 |
| `anthropic` | ⑧ 비대칭 의존 | 채점표_v1.5.md 188·198·350행 |
| `anthropic` | ⑧ 비대칭 의존 | 3cf9799:validation/offb-24/_raw/amzn-20260630.htm |
| `anthropic` | ⑧ 비대칭 의존 | 8ddb0ae |
| `anthropic` | ⑧ 비대칭 의존 | 3cf9799:validation/offb-24/_raw/spcx_s1a_20260603.htm |
| `anthropic` | ⑨ 적자 깊이 | 판단 기록 anthropic.F9 |
| `anthropic` | ⑨ 적자 깊이 | [FIX-53 3단계 라벨 정정: 10-Q Note 1 문면은 `expansion of … existing multi-year commitment by more than $100.0 billion over 10.0 years` — 기존 다년 약정 **위의 증액**이고 `more than` 이라 **하한**이다. $100B/10년은 약정 총액이 아니다. $300B 합계는 v1.5 기준선 값(HANDOVER 51행). `연 환산 약 $50B`·`ARR $65B 의 77%`·`커버리지 1.3배` 는 이 라벨에서 나온 **약정 하한 기준 환산**이다 — 약정이 더 크면 연 환산은 $50B 보다 크고 커버리지는 1.3배보다 낮다. 게이트 4 판정은 승계 그대로다] |
| `apple` | ① 네트워크 | 판단 기록 apple.F1 |
| `apple` | ② 게임체인저 | 판단 기록 apple.F2 |
| `apple` | ③ Last Mover | 판단 기록 apple.F3 |
| `apple` | ④ 호황 이후 | 판단 기록 apple.F4 |
| `apple` | ⑤ 아군 | 판단 기록 apple.F5 |
| `apple` | ⑥ 가격 | v1.5 참고 문면: **이번 실행 점수는 -4 이고 입력에서 자동 산출한 값이다**(위 산식 참조). 아래는 기준선 v1.5 문면이라 다른 수가 섞여 있을 수 있다 — 점수 근거가 아니다. |
| `apple` | ⑥ 가격 | v1.5 참고 문면: (v1.5: 구간 재설계 — 29~42) NTM PER 35.5 — 29~42 구간, 경계에서 벗어남(42선까지 15.5%) |
| `apple` | ⑥ 가격 | v1.5 참고 문면: TTM 37.3 |
| `apple` | ⑥ 가격 | v1.5 참고 문면: PEG 3.36, 상장 12사 최악 |
| `apple` | ⑥ 가격 | v1.5 참고 문면: AI 실행력은 하위인데 밸류는 역사적 최상단 |
| `apple` | ⑦ 순환금융 | 판단 기록 apple.F7 |
| `apple` | ⑧ 비대칭 의존 | 판단 기록 apple.F8 |
| `apple` | ⑨ 적자 깊이 | 판단 기록 apple.F9 |
| `meta` | ① 네트워크 | 판단 기록 meta.F1 |
| `meta` | ② 게임체인저 | 판단 기록 meta.F2 |
| `meta` | ② 게임체인저 | [FIX-56 2단계] [FIX-52 2026-09-15] |
| `meta` | ② 게임체인저 | [FIX-52 2026-09-15] |
| `meta` | ② 게임체인저 | 채점표 264행 |
| `meta` | ② 게임체인저 | 채점규칙 22행 |
| `meta` | ② 게임체인저 | anthropic.F2 |
| `meta` | ② 게임체인저 | 5차 리뷰 A |
| `meta` | ③ Last Mover | 판단 기록 meta.F3 |
| `meta` | ④ 호황 이후 | 판단 기록 meta.F4 |
| `meta` | ⑤ 아군 | 판단 기록 meta.F5 |
| `meta` | ⑥ 가격 | v1.5 참고 문면: **이번 실행 점수는 -1 이고 입력에서 자동 산출한 값이다**(위 산식 참조). 아래는 기준선 v1.5 문면이라 다른 수가 섞여 있을 수 있다 — 점수 근거가 아니다. |
| `meta` | ⑥ 가격 | v1.5 참고 문면: NTM PER 17.9 — Alibaba(16.7) 다음으로 낮음 |
| `meta` | ⑥ 가격 | v1.5 참고 문면: TTM 21.8, 영업외 비중 1% — Apple과 함께 상장 12사 중 평가이익 없는 깨끗한 배수 |
| `meta` | ⑥ 가격 | v1.5 참고 문면: PEG 0.92 |
| `meta` | ⑥ 가격 | v1.5 참고 문면: P/S 6.6 참고 |
| `meta` | ⑦ 순환금융 | 판단 기록 meta.F7 |
| `meta` | ⑧ 비대칭 의존 | 판단 기록 meta.F8 |
| `meta` | ⑨ 적자 깊이 | 판단 기록 meta.F9 |
| `microsoft` | ① 네트워크 | 판단 기록 microsoft.F1 |
| `microsoft` | ② 게임체인저 | 판단 기록 microsoft.F2 |
| `microsoft` | ③ Last Mover | 판단 기록 microsoft.F3 |
| `microsoft` | ④ 호황 이후 | 판단 기록 microsoft.F4 |
| `microsoft` | ⑤ 아군 | 판단 기록 microsoft.F5 |
| `microsoft` | ⑥ 가격 | v1.5 참고 문면: **이번 실행 점수는 -3 이고 입력에서 자동 산출한 값이다**(위 산식 참조). 아래는 기준선 v1.5 문면이라 다른 수가 섞여 있을 수 있다 — 점수 근거가 아니다. |
| `microsoft` | ⑥ 가격 | v1.5 참고 문면: (v1.5: 구간 재설계 — 20~29) NTM PER 25.4 — v1.4의 25선은 배율이 좁아(×1.25) 실제 분포와 안 맞았다 |
| `microsoft` | ⑥ 가격 | v1.5 참고 문면: TTM 27.9, 영업외 6%(정상) |
| `microsoft` | ⑥ 가격 | v1.5 참고 문면: P/S 11.1 참고 |
| `microsoft` | ⑦ 순환금융 | 판단 기록 microsoft.F7 |
| `microsoft` | ⑧ 비대칭 의존 | 판단 기록 microsoft.F8 |
| `microsoft` | ⑨ 적자 깊이 | 판단 기록 microsoft.F9 |
| `nvidia` | ① 네트워크 | 판단 기록 nvidia.F1 |
| `nvidia` | ② 게임체인저 | 판단 기록 nvidia.F2 |
| `nvidia` | ③ Last Mover | 판단 기록 nvidia.F3 |
| `nvidia` | ④ 호황 이후 | 판단 기록 nvidia.F4 |
| `nvidia` | ⑤ 아군 | 판단 기록 nvidia.F5 |
| `nvidia` | ⑥ 가격 | v1.5 참고 문면: **이번 실행 점수는 -2 이고 입력에서 자동 산출한 값이다**(위 산식 참조). 아래는 기준선 v1.5 문면이라 다른 수가 섞여 있을 수 있다 — 점수 근거가 아니다. |
| `nvidia` | ⑥ 가격 | v1.5 참고 문면: (v1.5: NTM 18.0 → 20 미만 · P/S 예외 삭제 — 규칙이 아니라 직관이었음) NTM PER 18.0 (Q2 실적 후 이익 급증) |
| `nvidia` | ⑥ 가격 | v1.5 참고 문면: PEG 0.36 |
| `nvidia` | ⑥ 가격 | v1.5 참고 문면: TTM 27.5는 영업외 14%($32B 랩 지분 평가익) 포함 |
| `nvidia` | ⑥ 가격 | v1.5 참고 문면: P/S 17.9는 참고만 — PER이 낮으면 낮은 것이 정보다 |
| `nvidia` | ⑦ 순환금융 | 판단 기록 nvidia.F7.fix52 |
| `nvidia` | ⑦ 순환금융 | [FIX-52 재척도 2026-09-15] |
| `nvidia` | ⑦ 순환금융 | FIX-52 |
| `nvidia` | ⑦ 순환금융 | nvidia.F7 |
| `nvidia` | ⑧ 비대칭 의존 | 판단 기록 nvidia.F8 |
| `nvidia` | ⑨ 적자 깊이 | 판단 기록 nvidia.F9 |
| `openai` | ① 네트워크 | 판단 기록 openai.F1 |
| `openai` | ② 게임체인저 | 판단 기록 openai.F2 |
| `openai` | ② 게임체인저 | [FIX-56 2단계] |
| `openai` | ② 게임체인저 | [FIX-52 2026-09-15] |
| `openai` | ② 게임체인저 | A-LCR |
| `openai` | ② 게임체인저 | 채점표 732행 |
| `openai` | ② 게임체인저 | 채점규칙 22행 |
| `openai` | ② 게임체인저 | anthropic.F2 |
| `openai` | ② 게임체인저 | 5차 리뷰 A |
| `openai` | ③ Last Mover | 판단 기록 openai.F3 |
| `openai` | ④ 호황 이후 | 판단 기록 openai.F4 |
| `openai` | ④ 호황 이후 | [FIX-54 2단계] |
| `openai` | ④ 호황 이후 | 채점규칙 382행 |
| `openai` | ④ 호황 이후 | TEN-RA3-01 |
| `openai` | ⑤ 아군 | 판단 기록 openai.F5.impl48 |
| `openai` | ⑤ 아군 | [F5-IMPL-48 재판정 2026-09-14] |
| `openai` | ⑤ 아군 | 채점규칙 727행 |
| `openai` | ⑤ 아군 | 채점표 759행 |
| `openai` | ⑤ 아군 | 별표 H 276행 |
| `openai` | ⑤ 아군 | openai.F5 |
| `openai` | ⑤ 아군 | a01f127 |
| `openai` | ⑤ 아군 | 1aab1f2 |
| `openai` | ⑥ 가격 | v1.5 참고 문면: **이번 실행 점수는 -4 이고 입력에서 자동 산출한 값이다**(위 산식 참조). 아래는 기준선 v1.5 문면이라 다른 수가 섞여 있을 수 있다 — 점수 근거가 아니다. |
| `openai` | ⑥ 가격 | v1.5 참고 문면: -4 (v1.5: ARR 보정 + 적자 + 자본효율) |
| `openai` | ⑥ 가격 | v1.5 참고 문면: post-money $852B ÷ ARR $40B = 21.3배 — TTM 보정 시 약 39배 |
| `openai` | ⑥ 가격 | v1.5 참고 문면: 이익 배수 산출 불가 — 적자(2026 GAAP 손실 약 $60B 전망, BEP 2030) |
| `openai` | ⑥ 가격 | v1.5 참고 문면: 자본효율 0.22(ARR $40B ÷ 누적 조달 약 $180~190B) — Anthropic(0.52)의 절반 이하. 1.5배 많은 돈을 태우고 더 낮은 밸류($852B < $965B)에 있다 |
| `openai` | ⑥ 가격 | v1.5 참고 문면: 주의 — 정밀도 열위 |
| `openai` | ⑥ 가격 | v1.5 참고 문면: IPO는 2027로 밀림 |
| `openai` | ⑥ 가격 | openai.post_money_valuation.v15 |
| `openai` | ⑥ 가격 | openai.arr.v15 |
| `openai` | ⑥ 가격 | openai.arr_prior.priv31 |
| `openai` | ⑥ 가격 | openai.cumulative_raised.v15 |
| `openai` | ⑥ 가격 | openai.ps_ratio.priv31 |
| `openai` | ⑦ 순환금융 | 판단 기록 openai.F7 |
| `openai` | ⑧ 비대칭 의존 | 판단 기록 openai.F8 |
| `openai` | ⑨ 적자 깊이 | 판단 기록 openai.F9 |
| `openai` | ⑨ 적자 깊이 | [FIX-56 1단계 재척도 표시 2026-09-16] [FIX-62 2026-09-17] |
| `openai` | ⑨ 적자 깊이 | [FIX-56 1단계] |
| `openai` | ⑨ 적자 깊이 | 별표 D 388~390행 |
| `openai` | ⑨ 적자 깊이 | 5차 리뷰 B |
| `openai` | ⑨ 적자 깊이 | 8b98b56 |
| `oracle` | ① 네트워크 | 판단 기록 oracle.F1 |
| `oracle` | ② 게임체인저 | 판단 기록 oracle.F2 |
| `oracle` | ③ Last Mover | 판단 기록 oracle.F3 |
| `oracle` | ③ Last Mover | oracle.contracted_revenue.fix57 |
| `oracle` | ④ 호황 이후 | 판단 기록 oracle.F4 |
| `oracle` | ⑤ 아군 | 판단 기록 oracle.F5 |
| `oracle` | ⑥ 가격 | v1.5 참고 문면: **이번 실행 점수는 -3 이고 입력에서 자동 산출한 값이다**(위 산식 참조). 아래는 기준선 v1.5 문면이라 다른 수가 섞여 있을 수 있다 — 점수 근거가 아니다. |
| `oracle` | ⑥ 가격 | v1.5 참고 문면: NTM PER 19.10 — 20선 밖(-4.5%) |
| `oracle` | ⑥ 가격 | v1.5 참고 문면: TTM 26.42 |
| `oracle` | ⑥ 가격 | v1.5 참고 문면: P/S 6.6 |
| `oracle` | ⑥ 가격 | v1.5 참고 문면: 주가 52주 -31.6%로 시장이 이미 크게 깎았다 |
| `oracle` | ⑥ 가격 | v1.5 참고 문면: PEG 0.65 |
| `oracle` | ⑥ 가격 | v1.5 참고 문면: 주의 — 단 EV/Sales 8.60(P/S 6.59보다 높다) — 부채 $167B가 시총에 안 잡힌다 |
| `oracle` | ⑦ 순환금융 | 판단 기록 oracle.F7.fix52 |
| `oracle` | ⑦ 순환금융 | [FIX-52 재척도 2026-09-15] |
| `oracle` | ⑦ 순환금융 | FIX-52 |
| `oracle` | ⑦ 순환금융 | oracle.contracted_revenue.fix57 |
| `oracle` | ⑦ 순환금융 | oracle.F7 |
| `oracle` | ⑧ 비대칭 의존 | 판단 기록 oracle.F8 |
| `oracle` | ⑨ 적자 깊이 | 판단 기록 oracle.F9 |
| `oracle` | ⑨ 적자 깊이 | oracle.contracted_revenue.fix57 |
| `oracle` | ⑨ 적자 깊이 | oracle.offbalance_B.v15 |
| `palantir` | ① 네트워크 | 판단 기록 palantir.F1 |
| `palantir` | ② 게임체인저 | 판단 기록 palantir.F2 |
| `palantir` | ③ Last Mover | 판단 기록 palantir.F3 |
| `palantir` | ④ 호황 이후 | 판단 기록 palantir.F4 |
| `palantir` | ⑤ 아군 | 판단 기록 palantir.F5 |
| `palantir` | ⑥ 가격 | v1.5 참고 문면: **이번 실행 점수는 -4 이고 입력에서 자동 산출한 값이다**(위 산식 참조). 아래는 기준선 v1.5 문면이라 다른 수가 섞여 있을 수 있다 — 점수 근거가 아니다. |
| `palantir` | ⑥ 가격 | v1.5 참고 문면: (v1.5: 9/2 NTM 89.0 — 90선 아래 1.1%, 📏경계) NTM PER 89.0 |
| `palantir` | ⑥ 가격 | v1.5 참고 문면: 9/2 하루 -5.8%로 선 아래로 |
| `palantir` | ⑥ 가격 | v1.5 참고 문면: TTM 144.9 |
| `palantir` | ⑥ 가격 | v1.5 참고 문면: P/S 66, 상장사 중 SpaceX(83) 다음(참고) |
| `palantir` | ⑥ 가격 | v1.5 참고 문면: 시총 $407B |
| `palantir` | ⑦ 순환금융 | 판단 기록 palantir.F7 |
| `palantir` | ⑧ 비대칭 의존 | 판단 기록 palantir.F8 |
| `palantir` | ⑨ 적자 깊이 | 판단 기록 palantir.F9 |
| `spacex-xai` | ① 네트워크 | 판단 기록 spacex-xai.F1 |
| `spacex-xai` | ② 게임체인저 | 판단 기록 spacex-xai.F2 |
| `spacex-xai` | ③ Last Mover | 판단 기록 spacex-xai.F3 |
| `spacex-xai` | ④ 호황 이후 | 판단 기록 spacex-xai.F4 |
| `spacex-xai` | ⑤ 아군 | 판단 기록 spacex-xai.F5 |
| `spacex-xai` | ⑥ 가격 | v1.5 참고 문면: **이번 실행 점수는 -3 이고 입력에서 자동 산출한 값이다**(위 산식 참조). 아래는 기준선 v1.5 문면이라 다른 수가 섞여 있을 수 있다 — 점수 근거가 아니다. |
| `spacex-xai` | ⑥ 가격 | v1.5 참고 문면: NTM PER 111(SA fwd 111.46) |
| `spacex-xai` | ⑥ 가격 | v1.5 참고 문면: P/S 83 |
| `spacex-xai` | ⑥ 가격 | v1.5 참고 문면: 시총 $1.91T — Tesla보다 크다 |
| `spacex-xai` | ⑥ 가격 | v1.5 참고 문면: 주식 수 YoY +41.8%(IPO + xAI $250B + Cursor $60B 전량 주식교환) |
| `spacex-xai` | ⑦ 순환금융 | 판단 기록 spacex-xai.F7 |
| `spacex-xai` | ⑦ 순환금융 | [FIX-59 정정 · obsreg 8차 리뷰 A 분담(Claude 독립 세션, review-obsreg e5a47d3) medium] FIX-58 |
| `spacex-xai` | ⑦ 순환금융 | 8차 리뷰 A |
| `spacex-xai` | ⑦ 순환금융 | e5a47d3 |
| `spacex-xai` | ⑦ 순환금융 | 3cf9799:validation/offb-24/_raw/spcx_s1a_20260603.htm |
| `spacex-xai` | ⑦ 순환금융 | 3cf9799:validation/offb-24/_raw/spcx-20260630.htm |
| `spacex-xai` | ⑧ 비대칭 의존 | 판단 기록 spacex-xai.F8 |
| `spacex-xai` | ⑨ 적자 깊이 | 판단 기록 spacex-xai.F9.obsreg25 |
| `spacex-xai` | ⑨ 적자 깊이 | [FIX-52 2026-09-15 · 값 갱신 FIX-55 1단계] [FIX-55 1단계] FIX-54 |
| `spacex-xai` | ⑨ 적자 깊이 | [FIX-54 2단계] |
| `spacex-xai` | ⑨ 적자 깊이 | OBS-REG-25 지시서 |
| `spacex-xai` | ⑨ 적자 깊이 | spacex-xai.undrawn_credit.fix54 |
| `spacex-xai` | ⑨ 적자 깊이 | spacex-xai.operating_margin_ttm.f6reg28 |
| `spacex-xai` | ⑨ 적자 깊이 | spacex-xai.contracted_revenue.obsreg25 |
| `spacex-xai` | ⑨ 적자 깊이 | spacex-xai.offbalance_B.obsreg25 |
| `spacex-xai` | ⑨ 적자 깊이 | 채점표_v1.5.md 671·673행 |
| `spacex-xai` | ⑨ 적자 깊이 | 채점표_v1.5.md 672행 |
| `spacex-xai` | ⑨ 적자 깊이 | 채점표_v1.5.md 674행 |
| `tesla` | ① 네트워크 | 판단 기록 tesla.F1 |
| `tesla` | ② 게임체인저 | 판단 기록 tesla.F2 |
| `tesla` | ③ Last Mover | 판단 기록 tesla.F3 |
| `tesla` | ④ 호황 이후 | 판단 기록 tesla.F4 |
| `tesla` | ⑤ 아군 | 판단 기록 tesla.F5 |
| `tesla` | ⑥ 가격 | v1.5 참고 문면: **이번 실행 점수는 -5 이고 입력에서 자동 산출한 값이다**(위 산식 참조). 아래는 기준선 v1.5 문면이라 다른 수가 섞여 있을 수 있다 — 점수 근거가 아니다. |
| `tesla` | ⑥ 가격 | v1.5 참고 문면: NTM PER 187.5 / TTM 370.5 / P/S 13.6 |
| `tesla` | ⑥ 가격 | v1.5 참고 문면: 시총 $1.41T |
| `tesla` | ⑦ 순환금융 | 판단 기록 tesla.F7 |
| `tesla` | ⑧ 비대칭 의존 | 판단 기록 tesla.F8 |
| `tesla` | ⑨ 적자 깊이 | 판단 기록 tesla.F9 |
| `tsmc` | ① 네트워크 | 판단 기록 tsmc.F1 |
| `tsmc` | ② 게임체인저 | 판단 기록 tsmc.F2 |
| `tsmc` | ③ Last Mover | 판단 기록 tsmc.F3 |
| `tsmc` | ④ 호황 이후 | 판단 기록 tsmc.F4 |
| `tsmc` | ⑤ 아군 | 판단 기록 tsmc.F5.strict54 |
| `tsmc` | ⑤ 아군 | [A-STRICT-54 재판정 2026-09-15] |
| `tsmc` | ⑤ 아군 | 채점규칙 192·193행 |
| `tsmc` | ⑤ 아군 | 체크리스트 Q03 |
| `tsmc` | ⑤ 아군 | 2차 리뷰 C RC-04 |
| `tsmc` | ⑤ 아군 | 채점표_v1.5.md 243행 |
| `tsmc` | ⑤ 아군 | 채점규칙 218행 |
| `tsmc` | ⑤ 아군 | 채점규칙 289행 |
| `tsmc` | ⑤ 아군 | tsmc.F5 |
| `tsmc` | ⑤ 아군 | AGENTS.md 리뷰 범위 |
| `tsmc` | ⑥ 가격 | v1.5 참고 문면: **이번 실행 점수는 -3 이고 입력에서 자동 산출한 값이다**(위 산식 참조). 아래는 기준선 v1.5 문면이라 다른 수가 섞여 있을 수 있다 — 점수 근거가 아니다. |
| `tsmc` | ⑥ 가격 | v1.5 참고 문면: NTM PER 19.4(직접 계산 ✱ — StockAnalysis가 TWD/USD 혼재) — 20선 -3%, 경계 주의 — . TWD 환율 하나로 -1 가능 |
| `tsmc` | ⑥ 가격 | v1.5 참고 문면: TTM 30.9 |
| `tsmc` | ⑥ 가격 | v1.5 참고 문면: 영업외 7%(깨끗) |
| `tsmc` | ⑥ 가격 | v1.5 참고 문면: P/S 15.4 참고 |
| `tsmc` | ⑥ 가격 | v1.5 참고 문면: 시총 $2.15T(ADR 5.19B주 × $415.5) |
| `tsmc` | ⑦ 순환금융 | 판단 기록 tsmc.F7 |
| `tsmc` | ⑧ 비대칭 의존 | 판단 기록 tsmc.F8 |
| `tsmc` | ⑨ 적자 깊이 | 판단 기록 tsmc.F9 |

## 규칙 파일의 항목 메모

리포트 본문의 `무엇을 보고 매기는가` 는 채점규칙 별표에서 가져온다. 이 표는 규칙 JSON 의 `factors.*.note` 원문이며 **결정 번호와 작업 경위가 섞여 있어 본문에 싣지 않는다.** 규칙 파일과 대조할 때 쓴다.

| 항목 | `note` 원문 |
| --- | --- |
| `F1` ① 네트워크 | 모든 실질 채널을 보고 가장 강한 락인으로 채점(별표 A). 소비자·업무 채널이 없는 부품형은 상한 2 |
| `F2` ② 게임체인저 | 세 경로(성능 도약·패러다임 적응·표준 선점) 통과 수 → 0개 2 · 1개 3 · 2개 4, **단 성능 도약이 '세대 격차' 수준이면 5**(C-03 확정, 2026-09-14). 5점 칸은 `AA 종합 1위` 가 아니다 — HANDOVER 사다리가 판단을 조회로 바꾸면서 nvidia·tsmc 를 놓쳤다. **F2 는 여전히 carried_score 다** — 이 결정은 규칙 확정이고 자동 산출 전환은 별건이다. 세대 격차가 세 축 중 몇 개에서 서야 하는지는 원문 미규정이다(decisions C-03). |
| `F4` ④ 호황 이후 | 출하·실제 배포만 인정, 계획·발표·포지션은 0(별표 D) |
| `F6` ⑥ 가격 | 상장: P1 PER + P2 EV/Sales + P3 매출성장률 합계에 P4 입력신뢰도 보정(한 칸) 후 트랙 하한으로 절단. 비상장: 배수는 자동 계산, 밴드 미정이라 점수는 pending_rule_decision. C-13(근사 NTM)은 v1.7 F6 가 NTM 을 쓰지 않아 F6 와 무관해졌다(결정 자체는 유지). |

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
