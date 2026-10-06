---
reviewer_agent: general-purpose (규칙 일관성)
session: rc-rescore-20261006-r1
reviewed_at: 2026-10-06
round: 1
---
# rule-consistency — 규칙 일관성
검토자: Claude Opus 5.5 · 규칙 일관성 독립 세션(이 실행을 만든 세션 아님) · 2026-10-06 · 1차
결과: pass
요약: 14개사 판단 114건, 근거 72건 가운데 새 근거 34건 전부, 트리거 79건을 보고 규칙 v1.9 와 대조했다. 점수·순위·체크리스트 판정을 바꾸는 발견은 없다. 이번 실행이 새로 댄 잣대 셋은 모두 닿아야 할 회사에 닿았다. 첫째, ⑥ 트랙을 관측 기간으로 정하는 v1.9 규칙은 예탁증서 상장사 두 곳(TSMC `adr`, Alibaba `ads`)에만 해당하고, 둘 다 `listed_ttm` 이 됐다. 둘째, 분기 자료로 최근 1년을 복원하는 방식은 세 회사에 댔다. 나머지 11개사의 ⑥·⑨ 관측 창은 이미 기준일 시점의 최신 분기(2026-06-27/06-30/07-26)에서 끝나고, SpaceX 는 H1'24 자료가 없어 신규 상장 트랙에 남는 것이 맞다. 셋째, 미인출 여신과 순현금의 날짜 섞임은 점수에 닿지 않지만 회사마다 기록 방식이 다르다. Oracle 은 `mixed_as_of` 와 변동 검색을 남겼고, Alibaba 여신에는 그 기록이 없다(low). ③·⑤·⑦·⑥·⑨ 의 환산은 전 기업을 손으로 다시 계산해 엔진 결과와 맞췄다. 미결 결정 가운데 차단형(C-05·C-06·C-16)은 모두 run.json 에서 골랐다. 트리거 철회 22건의 사유는 규칙과 맞고, 미래 점수를 저장한 트리거는 없다. 체크리스트 fail 13건은 모두 승계 판단의 기존 논리에서 나왔다. 이번 실행은 그 잣대를 바꾸지 않았고, 모두 `open_tensions` 에 재검토 시점 2026-11 로 등록돼 있다(승계 판단 예외). medium 두 건이 있다. TRG-017 은 v1.9 와 반대로 "TSMC ⑥ 은 연간 트랙이라 분기 실적으로 P3 가 바뀌지 않는다" 고 적는데, 실제로는 P3 가 경계 +1.9% 에 있다. preview 의 변동 원인 분류도 규칙 5절과 어긋난다. 둘 다 점수에 닿지 않으므로 「다음 실행 과제」로 둔다.

검토 기준: results_hash `1101644bc117e2a2…`, draft_hash `1168a515ee524414…`. review.md frontmatter 와 같은 값이고, draft.md 파일 sha256 은 이 세션에서 다시 계산해 확인했다.

검토 범위(전수):
- `judgments.json` 114건(승계 102 · new 12)을 표로 뽑아 전부 봤다. 종류, 입력, 상태, 검토자·검토일, 대체 기록, 개정 이력을 확인했다.
- 환산을 손으로 다시 계산했다.
  - ③: 14개사 통과점 → 사다리 결과.
  - ⑤: 3 + A + H.
  - ⑦: 판정표 4칸.
  - ⑥: P1·P2·P3 밴드 + P4 → 바닥 적용(상장 12사), 비상장 C-12 보정 2사.
  - ⑨: G1~G4 경로(14사).
  - 결과는 모두 results.json 과 같다.
- 관측 창: 14개사 ⑥·⑨ 입력 관측 160줄의 기준일·`period_basis`·`mixed_as_of` 를 확인했다. 미인출 여신 4건(amazon·spacex-xai·alibaba·oracle)은 basis 를 전문으로 읽었다.
- `scorecard/companies.json` 의 `share_basis` 로 예탁증서 상장사를 전수 확인했다.
- 근거 34건(reviewed_at 2026-10-06)은 relevance·conditional_impact 를 전부 읽었다.
- 트리거 79건을 전부 봤다. 미래 점수 키·문구를 검색했고, 철회 22건의 사유를 전부 읽었다.
- 그 밖에 본 것:
  - `proposals.json` 4건: 입력 불변 여부를 개정 이력의 previous 와 대조했다.
  - 규칙 `decisions` 29건과 `open_tensions` 18건.
  - `scorecard_cli.py diff`: 1층 위반은 판단 4건 수정·관측 53건 추가, 2층 위반은 3개사로, 재조사 사례라 예상된 결과다.
  - `validate_report_contract.py`: review 상태 외 전부 ok, 결정론적 재계산 ok.
  - 초안의 승계 표시 112줄 ↔ 판단 상태 대조: 불일치 0.

## 발견
| 등급 | 위치 | 발견 | 점수 영향 |
| --- | --- | --- | --- |
| medium | `triggers.json` TRG-017 observation·recheck(초안 1239행, research.md 882·949행) | **v1.9 와 반대되는 트랙 서술.**<br>• 트리거 문구: "TSMC ⑥ 은 20-F 연간 수치로 계산하는 트랙이다", "⑥ 매출 성장 잣대(P3)는 연간 트랙이라 분기 실적으로 입력이 바뀌지 않으므로, 분기 성장률은 2026 연간 20-F 가 들어올 때까지 참고로만 남긴다".<br>• 실제: v1.9 `track_by_period_basis` 로 TSMC 는 `listed_ttm` 이고, 6-K 반기·분기 자료로 최근 1년을 복원한다. 3분기 실적(2026-10-15) 6-K 가 나오면 P1·P2·P3 입력이 모두 바뀐다.<br>• 특히 P3 는 30.56% 로 경계 30% 에서 +1.9% 다(경계 표시 걸림). 이 트리거가 정확히 지켜봐야 할 곳을 "안 바뀐다" 고 막고 있다. | 없음(트리거는 점수를 저장하지 않는다). 다음 재채점의 감시 방향을 그르친다 |
| medium | `preview.md` 「이전 실행 대비」·「변동 원인 분류」 | **원인 분류가 규칙 5절과 어긋난다.** 5절은 "실적·사실 변화, 규칙 변경 … 서로 다른 원인이다. 여러 원인이 함께 작동하면 모두 적는다" 이다.<br>• TSMC ⑥ −3→−2 와 Alibaba ⑥ −4→−5 는 v1.9 트랙 변경(규칙 변경)과 관측 갱신이 함께 낸 결과다. 그런데 `📊 관측(가격·재무)` 하나로만 적혔다. 지시서도 TSMC 가 가격만 갱신했다면 −5 였다고 적는다.<br>• Alibaba ⑨ −3→−4 는 `✍️ 판단 수정` 으로 분류됐다. 그러나 PRP-003 은 근거 문장만 바꿨고, 게이트 입력은 개정 이력 previous 와 같다. 실제 원인은 관측 갱신이다(최근 1년 FCF −7,226M→−11,102M, 런웨이 3.10→2.17년). | 없음. 승인자가 읽는 원인 설명이 틀린다(출력 영역과 겹친다) |
| low | `observations.json` alibaba.undrawn_credit.fix53 ↔ oracle.undrawn_credit.rs1006 | **날짜 섞임을 회사마다 다르게 기록한다(Q03).**<br>• Oracle: 10-K(2026-05-31) 여신을 8-31 현금과 섞으면서 `mixed_as_of`(value/consumer 기준일, 10-Q 의 `revolv`·`credit facilit` 0건 검색, 재무활동 차입 유입 없음)를 남겼다.<br>• Alibaba: 3-31 여신 US$3,330M 을 6-30 현금과 섞었는데 관측에 `mixed_as_of` 가 없다. 6월 분기 6-K 에서 해지·인출 여부를 찾은 기록도 없다. 판단 문장에만 "(2026-03-31, 6월 말 값은 보도자료에 없음)" 이 있다.<br>• 같은 관측 basis 의 `runway_effect`(3.0996년)·`score_dependence`("총점 7 이 이 관측 하나에 달려 있다")도 낡았다. | 없음. 여신을 빼도 20,718 ÷ 11,102 = 1.87년으로 같은 1~3년 구간이다 |
| low | `observations.json` oracle.offbalance_B.v15 · results oracle F9 G4 | **G4 분자와 분모의 날짜가 다르다.**<br>• 분자 RPO 는 2026-08-31 값($664B)으로 갱신했다. 분모 B종 약정은 v1.5 legacy $250B(C-26 미결) 그대로이고, `coverage_comparable: yes` 다.<br>• 판단 문장이 적듯 같은 10-Q 가 미개시 리스 약정 $288B 를 공시한다. | 없음. 664 ÷ 288 = 2.31배로 1배 이상이다 |
| low | `observations.json` tsmc.net_cash.rs1006 `vis_remaining_stake` · 규칙 `policies.f6.net_cash` | **VIS 잔여 19% 를 넣으면서 규칙 문면 안의 충돌이 드러났다.**<br>• 규칙 `securities_scope.include` 의 "상장 지분증권" 과 `components.excluded` 의 "전략적 지분투자(환금 목적이 아닌 보유)" 가 부딪힌다. 주석 8 은 FVOCI 를 "held for medium to long-term purposes" 로 적는다.<br>• 포함 자체는 다른 회사 처리와 같은 잣대다. nvidia 의 시장성 지분증권(EquitySecuritiesFvNi)과 alibaba 상장주식을 넣는다. 그래서 회사 간 불일치는 아니다. | 없음. 빼면 순현금 $84.1B, P2 17.19 → 약 17.21 로 같은 −1 밴드다 |
| low | `judgments.json` tsmc.F9(PRP-004)·oracle.F9(PRP-001) evidence | **⑨ 근거에 스톡 지표가 남았다.** ⑨ 「쓰지 말 것」(순부채 잔고)과 `net_cash.scope_separation`(P2 순현금을 ⑨ 로 옮기지 말 것)에 걸린다.<br>• tsmc.F9 는 P2 정의의 "순현금 $86.5B(VIS 잔여 지분 포함 — 빼면 $84.1B)" 를 적는다.<br>• oracle.F9 는 "순부채 −$132.07B" 를 갱신했다. 그러나 Debt/EBITDA 5.03 · 이자보상 4.87 · Altman Z 2.18 은 옛 기간 값 그대로다.<br>• 이전 실행 low 와 같은 모양이고 엔진 입력이 아니다. | 없음 |
| low | 초안 1123행 · `observations.json` amazon.undrawn_credit.fix54 | **소멸한 여신을 "기준일 현재 유효" 로 적는다.**<br>• 지연인출 Term Loan $17.5B 의 미인출분은 2026-09-30 에 소멸했다(기준일 −6일). 364일 여신 $5.0B 는 2026-10 만기다.<br>• 그런데 초안은 "런웨이는 기준일 현재 유효한 약정으로 계산했다" 고 적는다. 엔진은 6-30 관측 37.5B 를 그대로 쓴다. C-23(잔존 기간)은 미결이다.<br>• 이전 실행 low 의 연장이고, 기준일이 늦어져 더 어긋났다. | 없음. 여신 0 이어도 6.7년이다 |
| low | `evidence.json` EV-amazon-008 | **같은 사건을 한 회사에만 배정했다(Q03).** EU 가 AWS 와 Azure 를 함께 DMA 심사 대상으로 본다는 보도를 Amazon ⑤ 에만 배정했다. microsoft ⑤(H −1 비용형)에는 배정하지 않았다. | 없음. 두 회사 모두 비용형 그대로다 |
| low | `evidence.json` EV-microsoft-004 conditional_impact | **AI 귀속분 없이 ③ 가속도를 재려 한다.** "같은 정의의 Azure 수준값이 세 분기 이상 모이면 ③ 후발 가속도를 정량으로 다시 판정한다" 고 적는다. 그러나 Azure 에는 비AI 매출이 섞여 있다. ③ 판정 지침("플랫폼 전체 성장률이 아니라 AI 에 귀속되는 부분만")과 2.4("비AI 매출의 성장은 ③ 가속도가 아니다")에 비추면 단서가 필요하다. TRG-053 recheck 에는 그 단서가 있다. | 없음 |
| low | `triggers.json` 전체 | **Alibaba 다음 분기 감시 트리거가 없다(Q03).** v1.9 로 Alibaba ⑥·⑨ 도 분기 6-K 로 갱신되는 회사가 됐다. 그런데 9월 분기 실적(11월 예상) 트리거가 없다. 미국 상장사는 3분기 10-Q 트리거가 있다(TRG-005·010·024·032·055). 지금 Alibaba 값은 P1 25.85(경계 +3.4%)와 런웨이 2.17년이다. | 없음 |
| low | `evidence.json` EV-oracle-006·007 relevance, `triggers.json` TRG-022 observation | **낡은 숫자.** "버티는 기간 약 1.3년 · 약정 커버리지 약 2.6배" 라고 적는다. 지금은 1.61년 · 2.66배다. | 없음 |
| low | `judgments.json` 최상위 note · tsmc/oracle/alibaba F9 source_ids · alibaba.F9.obsreg25 마지막 줄 | **기록이 실제와 어긋난다.**<br>• note: "항목은 한 글자도 바꾸지 않았다" 그대로다. 실제로는 이번 실행에서 4건(PRP-001~004)을 고쳤고, 이전 실행에서 7건을 고쳤다.<br>• source_ids: 새 숫자는 6-K·10-Q 출처에서 왔는데 `SRC-v15-html` 만 남아 있다.<br>• alibaba.F9.obsreg25: "판정 주체 설계진행(2026-09-11…)" 인데 검토자는 noble 2026-10-06 이다. | 없음 |
| low | `docs/scorecard/rules.md` 8절 | **사람용 문서에서 미결 결정 둘이 빠졌다.** v1.9.json 에서 pending 인 C-09(anthropic·openai ⑦ 매트릭스 입력)와 C-26(oracle B종 $250B 출처)이 「규칙에도 실행에도 답이 없는 것」 표에 없다. C-26 은 이번 실행 oracle G4 분모와 닿는다. JSON 이 기준이고 문서를 고쳐야 한다. | 없음 |
| low | `judgments.json` alphabet.F5·openai.F5.impl48·spacex-xai.F5·anthropic.F5.impl48 | **국방부 계약 서술이 낡았다.** "국방부 CDAO 계약 4사 공통이라 변별력 없음" 이 그대로다. 그런데 EV-anthropic-010(국방부가 Anthropic 도구 사용 중단)으로 실질은 3사가 됐다. 이전 실행 low 의 연장이다. | 없음. 어느 회사의 A 도 이 계약에 기대지 않는다 |
| info | results anthropic F6 `calc.correction` | **비상장 보정 두 조건이 런레이트를 다르게 다룬다.**<br>• `arr_growth` 는 run_rate kind 를 거부하는데, `capital_efficiency` 는 같은 run_rate ARR 로 0.52 를 계산해 met=true 다. 규칙 문면은 런레이트 배제를 성장률에만 명시한다.<br>• anthropic P2 는 30.0 으로 경계 정확히 위(30배 이상 −4)다. 비상장은 경계 표시를 하지 않는다. | 없음. require_all 이라 성장률 불인정으로 보정이 서지 않는다. 승계 입력이다 |

## 체크리스트
| ID | 결과 | 근거 |
| --- | --- | --- |
| Q01 | fail | **승계 판단 예외 — TEN-RC-05 · TEN-RC3-04.**<br>• 이번 변경분은 통과다. 같은 위험을 두 칸에서 센 곳이 없다.<br>&nbsp;&nbsp;– Alibaba ⑥ 은 P3 성장 −3 과 P4 영업외 비중 0.70, ⑨ 는 런웨이 2.17년과 G4 확인된 미공시다. 서로 다른 속성이다.<br>&nbsp;&nbsp;– Oracle ⑨ 런웨이 하향과 ⑧ −4(단일 고객 의존)도 다른 속성이다.<br>&nbsp;&nbsp;– 새 근거 EV-spacex-xai-009 는 ⑦(진위)·⑧(취약성) 양쪽 배정이 이중 계상이 아님을 스스로 적는다.<br>• 승계 fail: nvidia F5·F8 의 고객 자체 칩 이탈(TEN-RC-05), tesla F5·F8 의 NHTSA(TEN-RC3-04). 이번 실행은 두 판단의 잣대를 바꾸지 않았다. 둘 다 2026-11 재검토로 등록돼 있다 |
| Q02 | fail | **승계 판단 예외 — TEN-RC-02 · TEN-RC3-01 · TEN-RC3-03 · TEN-RC3-05 · TEN-RC4-02.**<br>• 변경분은 통과다.<br>&nbsp;&nbsp;– PRP-001~004 는 판정 재료를 그대로 두고 숫자만 최근 1년 관측으로 바꿨다(개정 이력 previous.inputs 와 현재 inputs 동일).<br>&nbsp;&nbsp;– ⑨ 완충은 현금 + 조건 확인된 확정 여신이다. Oracle 의 ATM 발행분은 8-31 현금에 이미 든 실현 현금이라 "예상 증자" 가 아니다.<br>&nbsp;&nbsp;– 새 근거 34건의 factor 배정은 칸 정의에 맞는다. 소송·규제는 ⑤ H, 고객 이탈은 ① 전환비용, 에너지 저장 배치는 비AI 사업이라 ④, 인도 대수는 현금이 아니라 ⑨ 유지로 배정됐다.<br>• 저심각 관찰(위 발견): tsmc/oracle F9 근거의 스톡 지표, EV-microsoft-004 의 Azure 전체 성장. 둘 다 점수 입력이 아니다 |
| Q03 | fail | **승계 판단 예외 — TEN-RC-03 · TEN-RC4-03.** 이번 실행이 새로 댄 잣대는 모두 닿아야 할 회사에 닿았다.<br>(1) **⑥ 트랙.** companies.json 의 예탁증서 상장사는 tsmc(adr)·alibaba(ads) 둘뿐이고 둘 다 `listed_ttm`·P4 기간 조건 미적용이 됐다. 나머지는 보통주다. spacex-xai 는 H1'24 사실이 어느 문서에도 없어 전년 TTM 이 복원되지 않는다(관측 basis.why_not_ttm). 그래서 `listed_newly` 에 남는다. 규칙 문면(전년 1년치를 복원할 기간 자료가 없음)과 맞는다.<br>(2) **최근 1년 복원.** 나머지 11개사의 ⑥·⑨ 관측 창은 이미 기준일 시점의 최신 확보 분기에서 끝난다.<br>&nbsp;&nbsp;– 대부분 2026-06-30, apple 06-27, nvidia 07-26 이다. 9월 분기 실적은 기준일까지 나오지 않았다.<br>&nbsp;&nbsp;– 새 분기가 있던 회사는 Oracle(8-31)뿐이고 갱신됐다.<br>&nbsp;&nbsp;– P4 자료 오래됨은 14사 모두 걸리지 않는다(경과 1~3개월).<br>(3) **미인출 여신.** Oracle 에도 amazon·spacex-xai·alibaba 와 같은 기준(감사 주석 1차·MD&A 교차·약정 준수·만기)으로 여신을 등록했다. FCF 음수 기업 4곳 모두 여신 관측이 있다. 날짜 섞임 기록 방식은 다르다(alibaba 기록 없음, low). 순현금 날짜 섞임은 alibaba 만 있고 `mixed_as_of: true` 로 기록됐다.<br>(4) **VIS 포함.** nvidia·alibaba 의 상장 지분증권 포함과 같은 잣대다.<br>• 승계 fail: C-08 별표 H 이탈 조건 전사 미통일(TEN-RC-03), spacex-xai H 수 비교(TEN-RC4-03). 이번 실행은 ⑤ 잣대를 바꾸지 않았다. 새 ⑤ 근거는 기존 H 정의(종류)를 댄 것이고 등급은 그대로다 |
| Q04 | pass | 상장 12사 ⑥ 은 parameters 모드다. P1 은 시총 ÷ 모회사 귀속 순이익, P2 는 (시총−순현금) ÷ 매출이고, 시총 절대액을 쓰지 않는다. 트랙이 바뀐 TSMC·Alibaba 도 같은 비율 잣대다. 세 회사의 순이익 관측은 모두 모회사 귀속분이다(alibaba "attributable to Alibaba Group Holding Limited", tsmc "Shareholders of the parent", oracle `NetIncomeLoss`). 비상장 2사는 밸류 ÷ 보정 매출 배수다 |
| Q05 | fail | **승계 판단 예외 — TEN-RA-02 · TEN-RA3-01.**<br>• 변경분은 통과다. 회사 성명 근거(EV-palantir-008 Armada 제휴, EV-oracle-006 홍수 성명)는 conditional_impact 가 "지금은 유지" 로 막아 두었고 점수 재료로 쓰지 않았다. 재무 갱신의 1차 근거는 10-Q·10-K·6-K 법정 제출본이다.<br>• 승계 fail: nvidia F2 5점의 벤더 발표 성능 근거(TEN-RA-02), openai F4 3→4 의 이해당사자 발표(TEN-RA3-01).<br>• 출처 장부의 이해상충 표기는 이 판정에 넣지 않았다(AGENTS.md 「금지·주의」) |
| Q06 | pass | ① 가격 결정력 근거는 매출 점유율·$/M 이다. 새 근거에 볼륨 지표가 점수 재료로 든 곳은 없다. EV-amazon-009 의 챗봇 추천 비중은 Prime·트래픽 실측이 아니라서 유지로 처리됐다. ⑥ P3 와 ⑨ 는 금액 기준이다 |
| Q07 | pass | amazon.F3 이 "모델을 안 만든 것 자체는 카운터 포지셔닝이 아니다" 라고 명시한다. 이번 실행은 ③ 을 바꾸지 않았다 |
| Q08 | fail | **승계 판단 예외 — TEN-RC4-03.**<br>• 변경분은 통과다. 새 ⑤ 근거 21건은 적대를 종류로 분류했다.<br>&nbsp;&nbsp;– 비용형: 손해배상·규제 조사·시장 일부 차단.<br>&nbsp;&nbsp;– 구조형: 팔란티어 정당성 겨냥.<br>&nbsp;&nbsp;– 다발형 요건: "최대 파트너와도 긴장" 을 따로 확인한다(EV-palantir-009·010).<br>• 승계 fail: spacex-xai.F5 "동맹이 적보다 확실히 많지 않음"(수 비교) |
| Q09 | fail | **승계 판단 예외 — TEN-RA-02 · TEN-RA3-01 · TEN-RA6-01.**<br>• 변경분은 통과다.<br>&nbsp;&nbsp;– 계획·예정 근거는 모두 "지금은 유지" 로 처리됐다: 노르웨이 판매 금지 계획, Hugging Face 인수 서명, Armada 제휴 발표, Broadcom 대출 보도.<br>&nbsp;&nbsp;– oracle.F9 의 "2026년 $45~50B 추가 조달 예정" 과 tsmc.F9 의 capex 가이던스는 엔진 입력이 아닌 서술이다.<br>&nbsp;&nbsp;– Alibaba 8월 증자는 현금 관측 기준일 뒤라 완충에 넣지 않았다.<br>&nbsp;&nbsp;– 트리거 79건에 점수 키·예상 점수 문구가 없다. TRG-041 은 "옛 척도의 예상 점수 문장은 옮기지 않았다" 고 적는다(C-14).<br>• 승계 fail: 위 세 긴장 |
| Q10 | fail | **승계 판단 예외 — TEN-RB-Q10 · TEN-RC4-04.** 이번 실행은 ③ 을 바꾸지 않았다. 새 ③ 근거 EV-microsoft-004·EV-tesla-007 은 "유지" 다(EV-microsoft-004 의 AI 귀속 단서는 위 low) |
| Q11 | pass | ⑨ 는 게이트 경로로 계산된다.<br>• spacex-xai: 손실률 −16.2% 구간 −3.<br>• amazon·oracle·alibaba: FCF 음수 −2 에서 런웨이 사다리.<br>• anthropic·openai: 비상장 미공시 경로 −2.<br>순적자만으로 실격시킨 판단은 없다. spacex-xai 는 순손실이라 P1 을 만들지 않았고 감점하지도 않았다 |
| Q12 | fail | **승계 판단 예외 — TEN-RC4-01 · TEN-RC3-05.** ③ 사다리는 엔진이 적용한다. 14사 통과점 → 점수를 다시 계산해 모두 맞았다. 모방 불가능성이 pass 가 아닌 2.5점 두 곳(alibaba·spacex-xai)은 3으로 상한이 걸렸다 |
| Q13 | fail | **승계 판단 예외 — TEN-RC3-05.** alibaba.F3 이 회수 장치 없는 오픈웨이트를 imitation=partial 로 둔 것이다(긴장의 두 번째 사유). 이번 실행은 바꾸지 않았다 |
| Q14 | pass | 14사 F3 의 door_closed 가 전부 fail 이라 5점이 없다 |
| Q15 | pass | 공짜 사용자를 아군으로 세지 않는다는 잣대가 같다. nvidia.F5 는 개발자 1,800만을, alibaba.F5 는 파생모델 15만을 불인정했고, meta.F5 는 Glimmer 개발자를 무효로 봤다. 새 근거 EV-nvidia-013(Reflection)은 Nemotron 공동개발 관계로만 세고 사용자 수를 쓰지 않는다 |
| Q16 | fail | **승계 판단 예외 — TEN-RC-02 · TEN-RC4-02.** 이번 실행은 ① 을 바꾸지 않았다. 새 ① 근거 넷은 각 회사의 실질 채널로 배정됐다. EV-anthropic-011 은 업무 채널, EV-palantir-011 은 업무 전환비용, EV-amazon-009 는 소비자, EV-nvidia-009 는 부품 상한이다 |
| Q17 | pass | ② 가 낮은 apple(2)·oracle(2)도 세 경로 판정 근거가 있고, "표준 없음" 하나로 깎지 않았다. 이번 실행은 ② 를 바꾸지 않았다 |
| Q18 | pass | 관계사를 동맹으로 세지 않는다. tesla.F5 는 유일한 아군이 관계사 SpaceX 라 A=0 이고, spacex-xai.F5 는 Tesla 를 동맹에서 뺐다 |
| Q19 | pass | anthropic.F5.impl48·openai.F5.impl48 이 받은 투자를 A 에서 뺐다. 새 근거 가운데 받은 투자를 A 로 올린 것은 없다. EV-nvidia-013 은 NVIDIA 가 준 투자이고, ⑦ 환류와 겹치지 않게 ⑤ 에서는 공동개발만 센다 |
| Q20 | fail | **승계 판단 예외 — TEN-RC-03(C-08).**<br>• 변경분은 통과다.<br>&nbsp;&nbsp;– EV-anthropic-009(Broadcom 칩 임차 대출)는 "조달(돈 주고 사 오는 관계)" 로 분류돼 ⑤ 가 아니라 ⑧·⑨ 로 갔다.<br>&nbsp;&nbsp;– EV-palantir-008(Armada 공동 제공)은 네 질문 1·2번(재판매·연동)으로 동맹 후보다. +2 조건 불성립도 확인했다.<br>• 승계 fail: 별표 H 이탈 조건 전사 미통일. 이번 실행은 이 잣대를 바꾸지 않았다 |
| Q21 | fail | **승계 판단 예외 — TEN-RC-05 · TEN-RC3-04.**<br>• 변경분은 통과다. EV-spacex-xai-009 는 ⑦(진위)·⑧(취약성)의 독립을 적는다. EV-anthropic-011 은 Microsoft 를 ⑤ 동맹(유통)과 이탈 가능성(3문) 양쪽에서 보되 ⑧ 로 같은 속성을 다시 세지 않는다.<br>• 승계 fail: 위 두 긴장 |
| Q22 | pass | ⑦ 14건 모두 관측 입력이 없고, 두 축이거나 승계 점수다. oracle.F7(PRP-002)의 갱신은 RPO·매출 숫자뿐이다. TRG-003 은 "평가이익은 ⑦ 의 증거가 아니다(⑥ 소관)" 로 처리했다. 영업외 비중은 ⑥ P4 에만 쓰인다(C-11 block_carryover) |
| Q23 | fail | **승계 판단 예외 — TEN-RA4-01.** 이번 실행은 ② 를 바꾸지 않았다. 새 근거에 하네스 간 비교로 점수를 움직인 것은 없다. TRG-001 은 벤더 발표 벤치마크를 방증으로만 보고 독립 측정을 기다린다 |

승계 판단 예외의 공통 조건을 확인했다.
- fail 사유가 모두 `carried_score`(또는 그 기존 논리)다.
- 이번 실행은 ⑥ 트랙과 ⑥·⑨ 관측 창만 바꿨다. 위 fail 의 잣대(①②③⑤⑦⑧ 정성 기준)는 건드리지 않았다.
- fail 13건(Q01·02·03·05·08·09·10·12·13·16·20·21·23)이 인용한 긴장 16개(TEN-RC-02·RC-03·RC-05·RB-Q10·RA-02·RC3-01·RC3-03·RC3-04·RC3-05·RA3-01·RC4-01·RC4-02·RC4-03·RC4-04·RA4-01·RA6-01)는 모두 `status: open`, `recheck_at: 2026-11` 이다.
- 이번에 고친 판단 4건(tsmc.F9·oracle.F9·oracle.F7.fix52·alibaba.F9.obsreg25)은 어느 긴장의 대상에도 없다.

## 다음 실행 과제
- TRG-017 을 v1.9 에 맞게 고친다. "TSMC ⑥ 은 `listed_ttm`(6-K 로 최근 1년 복원)이고, 3분기 6-K 가 P1·P2·P3 입력을 바꾼다. P3 30.56% 는 경계 +1.9%" 로 적고, ⑥ 재계산을 recheck 에 넣는다. 승인 전에 고쳐도 비용이 작다(트리거 문장만).
- preview 의 변동 원인 분류를 규칙 5절에 맞춘다.
  - TSMC·Alibaba ⑥ 에는 "규칙 변경(v1.9 트랙) + 관측 갱신" 을 함께 적는다.
  - Alibaba ⑨ 는 "관측 갱신(최근 1년 FCF·현금)" 으로 적는다. 판단 수정이 아니다.
  - 렌더러가 개정 이력 유무만으로 `판단 수정` 을 고르지 않게, 입력이 바뀌었는지를 본다.
- alibaba.undrawn_credit.fix53 에 Oracle 과 같은 모양의 `mixed_as_of`(value 3-31 / consumer 6-30, 6월 분기 6-K 의 여신 언급·재무활동 차입 유입 검색 결과)를 남긴다. `runway_effect`·`score_dependence` 도 지금 값(1.87/2.17년, 점수 비의존)으로 고친다.
- oracle G4 분모를 C-26 결정과 함께 정리한다. 10-Q 의 미개시 리스 $288B(2026-08-31)를 같은 날짜 분모 후보로 등록하고, `coverage_comparable` 판정 근거에 날짜를 적는다.
- 규칙 파일 `policies.f6.net_cash` 에서 "상장 지분증권(include)" 과 "전략적 지분투자(excluded)" 의 우선순위를 정한다. 그 전까지는 open_questions 나 긴장에 TSMC VIS 사례를 등록한다.
- tsmc.F9·oracle.F9 근거의 스톡 지표(순현금·순부채·Debt/EBITDA·이자보상·Altman Z)를 ⑨ 근거에서 빼거나 "교차검증용(2.8)" 으로 표시한다. oracle 의 Debt/EBITDA 등은 옛 기간 값이라 갱신하거나 지운다.
- amazon 여신: C-23 을 결정하거나, 초안 각주 "런웨이는 기준일 현재 유효한 약정으로 계산했다" 를 "관측 기준일(2026-06-30) 약정으로 계산했다. Term Loan 미인출분은 기준일 전 소멸" 로 바로잡는다.
- EV-amazon-008 을 microsoft ⑤ 에도 배정하거나, microsoft 쪽 근거에 같은 사건을 적는다.
- EV-microsoft-004 conditional_impact 에 TRG-053 과 같은 AI 귀속 단서를 넣는다.
- Alibaba 9월 분기 실적(6-K) 트리거를 만든다. 감시 대상은 ⑥ P1 경계 +3.4%, ⑨ 런웨이 2.17년, 여신 6월 말 값 확인이다.
- 낡은 숫자를 고친다. EV-oracle-006·007 relevance 와 TRG-022 observation 의 "1.3년·2.6배" 를 "1.61년·2.66배" 로 바꾼다.
- judgments.json 을 정리한다.
  - 최상위 note 를 "승계 + 2026-10-01 반영 7건 + 2026-10-06 반영 4건(PRP-001~004)" 으로 고친다.
  - tsmc/oracle/alibaba F9 source_ids 에 새 6-K·10-Q 출처를 더한다.
  - alibaba.F9.obsreg25 의 "판정 주체" 줄을 정리한다.
- rules.md 8절 「규칙에도 실행에도 답이 없는 것」 표에 C-09·C-26 을 더한다(v1.9.json 과 맞춘다).
- CDAO "4사 공통" 서술 4곳을 Anthropic 배제 집행(EV-anthropic-010) 뒤 사실로 고친다.
- 비상장 ⑥ 보정에서 `capital_efficiency` 의 ARR kind 기준을 `arr_growth` 와 같게 할지 규칙에서 정한다.
