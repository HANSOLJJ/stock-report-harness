---
reviewer_agent: general-purpose (재무 계산 재리뷰)
session: fc-rr2-5335307c
reviewed_at: 2026-10-01
round: 3
---
# financial-calc — 재무 계산
검토자: Claude Opus 5.5 · 재무 계산 독립 세션(이 실행을 만든 세션 아님) · 2026-10-01 · 2차, 3차 확인
결과: pass
요약: 1차 medium 두 건은 둘 다 닫혔다. TSMC 환율 민감도를 관측 원값(NT$)과 새 시가총액으로 다시 계산하니 P1 43.7216/45.7007, 손익분기 환율 32.2872, P2 18.9156/19.7976 이 나와 기록과 맞는다. 아마존 ⑨ 런웨이는 9.9538년(115,713M ÷ 11,625M), 현금만 6.728년이고, Oracle ⑨ 는 1.3210년(31,289M ÷ 23,686M)이다. 판단 문장, 초안, 트리거 TRG-005 에 같은 값이 적혀 있다. 14개사 9-factor 점수와 순위는 1차와 같다. obsreg 대비 바뀐 칸은 meta ⑥, oracle ⑥, anthropic ⑤ 세 칸뿐이다. ⑥ 은 관측에서 다시 계산해 P1·P2·P3 값, 밴드, 소계, P4, 최종 점수가 14개사 모두 맞는다. preview 의 이전 실행 대비 표 세 행과 원인 분류도 맞다. 남은 것은 점수에 닿지 않는 low 두 건이다(셋째는 3차에서 닫혔다). Alibaba 민감도 기록은 숫자가 옛 입력 기준으로 남았고, † 각주 마지막 문장은 apple·palantir 순현금 † 를 빠뜨렸고, 새로 매긴 ⑨ 판단 문장에 legacy 재무 수치 두 개가 남았다.

검토 기준: results_hash `d82fcfa1fa3148ce…`, draft_hash `30135ffb15ac1be6…`. review.md frontmatter 와 같고, 이 세션에서 다시 계산해 확인했다. **3차 확인(같은 날)**: 2차 기준(`f4158bfd…`/`3d6ae00b…`) 뒤에 바뀐 입력은 셋이다. PRP-006(oracle.F9 게이트 1 문장), PRP-007(amazon.F9 순부채 문장), sources.json 이해상충 칸 19건이다. 다시 확인한 결과 판단 두 건의 판정 재료 7키는 revision_history previous 와 같다. 14개사 9-factor 점수는 obsreg 대비 차이가 2차와 같은 세 칸(meta F6, anthropic F5, oracle F6)이고, ⑥ 재계산 불일치 0, 과점·함정·총점·순위도 2차와 같다. 새 문장의 숫자도 관측과 맞는다. oracle 은 operating_income_ttm.f6reg28 20,606M ÷ revenue_ttm.f6reg28 67,357M = 30.59% → "$20.61B ÷ $67.36B, 마진 30.6%"(draft 1048행)이다. amazon 은 net_cash.nc37 −119,332M → "순부채 −$119.3B"(draft 182행)이다. 옛 값은 취소선(192·1058행)으로만 남았다. 재계산 스크립트는 세션 스크래치(`scratchpad/rr2/fx.py`, `scores.py`)에만 두었다. 저장소 파일은 이 파일 말고 고치지 않았다.

## 1차 발견 처리

| 1차 등급 | 발견 | 상태 | 확인 내용 |
| --- | --- | --- | --- |
| medium | TSMC 환율 민감도가 옛 시가총액 2.15T 기준으로 남아 있었다 | **닫힘** | `tsmc.net_income_ttm.f6reg28` 은 used 43.722(−1), alt 45.701(−2), `band_differs: true`, 손익분기 32.287 이다. `tsmc.revenue_ttm.f6reg28` 은 used 18.9156(−1), alt 19.798(−1), `band_differs: false` 이다. 두 기록 모두 `market_cap_basis` 로 새 시총 기준임을 적었다. 아래 재계산값과 소수 셋째 자리까지 맞는다. Alibaba 는 이번에 다시 계산하지 않았다. 아래 low 1 에서 다룬다 |
| medium | 아마존 ⑨ 근거와 TRG-005 에 런웨이 10.6년(legacy 현금 $123B 기준)이 남아 있었다 | **닫힘** | 판단 `amazon.F9.obsreg25` evidence 는 "런웨이 9.95년 — 완충 $115.7B(현금 $78.2B + 확정 미인출 여신 $37.5B) ÷ 연 소진 $11.6B"와 "현금만으로도 6.7년"이다. draft 132·179·180행, TRG-005(triggers.json·draft 1221행·research 836행)도 9.95년이다. draft 의 10.6년은 190행 "과거 기록(대체됨)" 취소선 한 곳에만 남았다. research 84행 `runway_years 10.6` 은 legacy 관측 목록이고 엔진은 쓰지 않는다. 판정 재료 7키는 revision_history 의 previous 와 같다 |
| low | draft † 각주가 시총 12건 모두 미실측인 것처럼 읽혔다 | **대부분 닫힘 — 일부 남음(low 2)** | 시총 문장이 "이번 실행의 ⑥ 은 직접 받은 시가총액(verified)으로 계산했다"로 바뀌어 지금 상태와 맞는다. 다만 이어지는 "† 는 참고 열(NTM PER 등)에만 남는다"가 apple·palantir 순현금 † 를 빠뜨렸다 |
| low | preview 원인 분류가 고정 문장("기준선 이관 재계산이라 📐규칙")이었다 | **닫힘** | "이전 실행 대비" 표가 생겼다. Meta ⑥ 은 📊 관측(가격·재무), Anthropic ⑤ 는 ✍️ 판단 수정, Oracle ⑥ 은 📊 관측(가격·재무)으로 나뉜다. 아래에서 원인을 입력 단위로 확인했다 |
| info | meta·oracle 경계 민감도 | 유지 | 값이 1차와 같다. meta P2 8.1905(+2.4%), oracle P1 24.3592(−2.6%)·P2 8.1916(+2.4%), ⚠️ 표시가 유지된다 |
| info | alibaba ADS 수 2.7% 차이 | 유지 | 확인하지 않았다. 밴드에서 멀어(P1 17.8, P2 1.47) 점수 영향은 없다 |

## 재계산 대조표

엔진값은 results.json `factors.*.calc` 에서 읽었다. 재계산값은 observations.json 의 값과 원값(`basis.original_value`, `basis.components`)에서 직접 계산했다. 밴드는 `scorecard/rules/v1.8.json` `policies.f6.parameters`·`private_bands` 에서 읽었다.

| 기업 | 항목 | 엔진·기록값 | 재계산값 | 일치 | 근거 관측 |
| --- | --- | --- | --- | --- | --- |
| tsmc | P1 @31.37 / @32.79 | 43.722(−1) / 45.701(−2) | 43.7216 / 45.7007 | O | market_cap.2026-09-30 = 2,366,017.59M · net_income_ttm.f6reg28 원값 NT$1,697,604.0M |
| tsmc | P1 = 45 손익분기 환율 | 32.287 | 45 × 1,697,604.0M ÷ 2,366,017.59M = 32.2872 | O | 선언 환율 31.37 에서 +2.9% 이면 밴드가 바뀐다 |
| tsmc | P2 @31.37 / @32.79 | 18.9156(−1) / 19.798(−1) | 18.9156 / 19.7976 | O | revenue_ttm.f6reg28 NT$3,809,054.3M · net_cash.nc37 NT$2,171,587.1M, 매출과 순현금을 같은 환율로 환산했다 |
| tsmc | P2 = 20 손익분기 환율 | (기록 없음) | 33.1158. 32.79 에서 20 선까지 −1.0% | — | 참고. 32.79 에서도 −1 밴드다 |
| alibaba | P1 @6.898 / @7.2567 | 기록 17.979 / 18.914 | **17.8046 / 18.7305** | △ | 기록은 legacy 시총 270B 기준이다(270B ÷ 15,017.7M = 17.979). 밴드는 둘 다 0이라 결론은 같다 |
| alibaba | P2 @6.898 / @7.2567 | 기록 1.701 / 1.79 | **1.4659 / 1.5596** | △ | 기록은 legacy 시총 270B 와 legacy 순현금 17.5B 기준이다((270 − 17.5) ÷ 148.401 = 1.7015). 밴드는 둘 다 0 |
| amazon | ⑨ G3 런웨이 | 9.953806 | 115,713M ÷ 11,625M = 9.9538. 현금만 78,213M ÷ 11,625M = 6.7280 | O | cash.cashfcf35 78,213M + undrawn_credit.fix54 37,500M · fcf_ttm.cashfcf35 −11,625M. 임계 3년 대비 +231.8%로 draft 132행과 같다 |
| oracle | ⑨ G3 런웨이 | 1.320991, step −1 | 31,289M ÷ 23,686M = 1.3210 | O | cash.cashfcf35 31,289M. undrawn_credit.fix54 는 값이 없어 분자에 들어가지 않는다. fcf_ttm.cashfcf35 −23,686M. 1~3년 구간에서 한 단계 하향하고, 임계 1년 대비 +32.1%다 |
| oracle | ⑨ G4 | 2.552 | 638,000M ÷ 250,000M = 2.552 | O | contracted_revenue.fix57 · offbalance_B.v15(legacy) |
| 14개사 | 9-factor 점수 | results.json | obsreg results.json 과 126칸을 비교했다. 차이는 meta F6 −1→−3, anthropic F5 4→3, oracle F6 −3→−2 셋뿐이다 | O | 1차가 확인한 세 칸과 같다. 판단 문장만 바뀌었고 점수는 바뀌지 않았다 |
| 14개사 | ⑥ P1·P2·P3·소계·P4·최종 | results.json | 1차 대조표 값과 소수 넷째 자리까지 같다. 밴드, 소계, P4 한 칸, 하한도 모두 맞다(불일치 0) | O | 12개 상장사 모두 `*.market_cap.2026-09-30`(verified)을 쓴다. spacex-xai P1 은 순손실이라 만들지 않았다(`parameters_optional_unmet`). 비상장 2사는 ps_ratio 30.0·39.0 → −4 |
| 14개사 | 과점·함정·총점·순위 | ranking | ①~⑤ 합, ⑥~⑨ 합, 둘의 합, 경쟁 순위(1 + 더 높은 총점 수)가 모두 맞다 | O | 1위 alphabet·amazon 15, 3위 microsoft 14, 4위 meta 13, 5위 tsmc 10, 6위 anthropic·spacex-xai·nvidia 9, … 14위 oracle 3. 1차와 같다 |
| meta | 이전 대비 ⑥ 원인 | 📊 관측(가격·재무) | obsreg 와 비교해 바뀐 입력은 market_cap 하나다(v15 1,510.0B → 2026-09-30 1,847.4B). P1 22.17→27.13, P2 6.71→8.19, P3 와 P4 는 같다 | O | 원인은 가격이다. 재무 관측은 바뀌지 않았다 |
| oracle | 이전 대비 ⑥ 원인 | 📊 관측(가격·재무) | 바뀐 입력은 market_cap 하나다(443.7B → 416.2B). P1 25.97(−1) → 24.36(0), P2 8.60 → 8.19 로 둘 다 −1 | O | 원인은 가격이다 |
| anthropic | 이전 대비 ⑤ 원인 | ✍️ 판단 수정 | judgment `anthropic.F5.impl48` inputs H 0 → −1(PRP-001, revision_history 1건). 3 + 1 − 1 = 3 | O | — |
| preview | 이전 실행 대비 표 | Meta 15/1→13/4 · Anthropic 10/5→9/6 · Oracle 2/14→3/14 | obsreg ranking 과 이번 ranking 에서 같은 값이 나온다 | O | 순위만 바뀐 microsoft 4→3, nvidia·spacex-xai 7→6 은 표에 없다. 표가 "바뀐 factor" 기준이라 의도된 범위다(info) |
| preview | 기준선 대비 표 14행 | — | 이번 조정·순위가 ranking 과 같다 | O | — |
| draft.md | 종합 순위표 14행 | — | 순위·9칸·과점·함정·총점 13열이 results 와 모두 같다 | O | 프로그램으로 대조했다 |
| draft.md | ⑨ 원자료 표 런웨이 열 | — | amazon 10.0(9.95 반올림) · alibaba 3.1 · spacex-xai 3.0 · oracle 1.3 이 엔진 G3 와 같다 | O | 소수 한 자리 반올림이다 |

## 발견 사항

- [low] `observations.json` `alibaba.net_income_ttm.f6reg28`·`alibaba.revenue_ttm.obsreg25` 의 basis.band_sensitivity: 숫자가 legacy 입력 기준으로 남아 있다. P1 17.979/18.914 는 legacy 시총 270B 기준이고, P2 1.701/1.79 는 legacy 시총 270B 와 legacy 순현금 17.5B 기준이다. 이번 실행 입력(시총 267,384.05M, 순현금 nc37 49,838.65M)으로 다시 계산하면 P1 17.8046/18.7305, P2 1.4659/1.5596 이다. 엔진 P1·P2 와 used 칸이 다르다. 밴드는 넷 다 0이라 `band_differs: false` 결론은 맞고 점수 영향도 없다. TSMC 기록에는 이번에 `market_cap_basis` 를 붙였고 Alibaba 기록에는 붙이지 않았다. 그래서 같은 이름의 필드가 회사마다 다른 시점 입력을 가리킨다. — 고칠 방향: Alibaba 두 기록도 새 시총과 nc37 순현금으로 다시 계산하고 `market_cap_basis` 를 남긴다. 1차에서 권고한 대로, 다른 입력이 바뀔 때마다 낡는 파생값은 관측 basis 에 저장하지 말고 calculate 에서 계산하는 것을 검토한다.
- [low] `draft.md` 1084행 † 각주의 마지막 문장: "† 는 참고 열(NTM PER 등)에만 남는다"라고 적었다. 그런데 같은 초안의 ⑨ 원자료 표(1106·1108행)에서 apple $62.2B†, palantir $9.2B† 순현금에도 † 가 붙는다. 이 둘(`*.net_cash.v15`)은 엔진이 ⑥ P2 입력으로 실제로 고른 관측이다. 그러니 † 는 참고 열에만 남은 것이 아니다. 각주가 세는 "net_cash 2건"이 바로 이 둘이다. 밴드에서 멀어 점수 영향은 없다(apple P2 10.28, palantir 71.52). 시총 문장 자체("직접 받은 시가총액(verified)으로 계산했다")는 지금 상태와 맞는다. — 고칠 방향: 마지막 문장을 "† 는 참고 열(NTM PER)과 apple·palantir 순현금(⑥ P2 입력)에 남는다"처럼 엔진이 고른 † 관측을 기준으로 만든다. 출력·가독성 영역에 넘긴다.
- [low → 3차에서 닫힘: PRP-006·PRP-007 로 두 문장의 수치를 관측에 맞췄다. 위 검토 기준 참조] 이번 실행에서 다시 매긴 ⑨ 판단 두 건(status `new`, reviewed 2026-10-01)의 문장에 legacy 재무 수치가 남아 있다. 같은 실행의 verified 관측과 다르다. ① `oracle.F9` "게이트 1 ✅ 영업흑자(영업이익 $22.39B, 마진 33.2%)"(draft 1047행): 엔진 G1 은 `oracle.operating_income_ttm.f6reg28` 20,606M ÷ 67,357M = **30.6%** 다. 22.39B 는 규칙 p4 메모가 말하는 구조조정비를 뺀 조정 영업이익으로 보인다. PRP-003 으로 status 가 carried → new 로 바뀌면서 이 문장도 이번 실행의 주장이 됐다. ② `amazon.F9.obsreg25` "순부채 −$128.7B"(draft 182행): `amazon.net_cash.v15`(legacy)이고, 이 관측은 `amazon.net_cash.nc37` **−$119.3B**(verified)로 대체됐다. 같은 초안 ⑨ 표 순현금 열은 −$119.3B 다. 두 건 모두 G1 통과와 ⑨ 점수에는 영향이 없다. — 고칠 방향: 사람이 `scorecard_cli.py judge` 로 문장의 수치를 관측에 맞춘다(oracle 마진 30.6%, 조정 기준을 남기려면 정의를 함께 적는다. amazon 순부채 −$119.3B). 문장을 고치면 판단 해시가 바뀌므로 research → calculate → draft → review 를 다시 돌린다. 급하지 않으면 다음 실행으로 넘겨도 된다.
- [info] `scorecard/rules/v1.8.json` `policies.f6.fx.why_issuer_declared_first[3]`: 공유 규칙 파일이 시총 2,150,000M 기준 TSMC P2 17.14/17.94 로 "환율 선택이 밴드를 가르지 않는다"고 결론짓는다. P2 만 놓고 보면 새 시총(18.92/19.80)에서도 맞다. 다만 이번 실행에서는 **P1 이 환율로 갈린다**(43.72 → 45.70). 이 문장을 "환율이 점수를 가르지 않는다"는 일반 결론으로 읽으면 안 된다. 실행 단위 기록(`tsmc.net_income_ttm.f6reg28`)은 이미 맞게 적혀 있다. 규칙 문구를 고칠지는 rule-consistency 영역에 넘긴다.
- [info] `oracle.undrawn_credit.fix54` 는 status 가 `not_disclosed` 인데 note 는 "확정 미인출 여신 미확인(우리가 확인하지 않았다)"이다. AGENTS.md 의 not_disclosed / unverified 구분과 어긋난다. 엔진은 값이 없으면 분자에 넣지 않으므로 런웨이 1.32년과 ⑨ −3 은 그대로다. 이번 실행 이전부터 있던 표기다. 사실·출처 영역에 넘긴다.
- [info] 경계 민감도는 1차와 같다. TSMC P1 은 선언 환율에서 45 선까지 −2.8%이고, 환율이 32.287 을 넘으면 −2 밴드가 된다. 규칙상 선언 환율이 우선이라 엔진 점수 −3 이 옳다.

## 체크리스트 기여
- Q04(시총 크기를 밸류에이션으로 착각했나): pass — ⑥ 은 시총을 분자로 쓰는 비율(시총 ÷ 모회사 귀속 순이익, (시총 − 순현금) ÷ 매출)로만 점수를 낸다. meta ⑥ −1→−3 과 oracle ⑥ −3→−2 는 이번 재계산에서도 시총 변화가 같은 이익·매출 대비 배수를 25·8 선 너머로 옮긴 결과다. 시총 절대 크기는 어떤 밴드에도 들어가지 않는다.
- Q06(볼륨인가 가치인가): pass — 이 세션이 다시 계산한 범위는 ⑥ 과 ⑨ 다. ⑥ P3 는 매출 금액 성장률이고, ⑨ G3 는 $ 완충 ÷ $ 소진, G4 는 계약 매출 $ ÷ 약정 $ 다. 사용자 수나 토큰 같은 볼륨 지표는 계산 경로에 없다. ①⑤ 같은 정성 판단 안의 Q06 은 보지 않았다.
- Q11(순적자를 실격 사유로 썼나): pass — spacex-xai 는 순손실이라 P1 을 만들지 않았고(`parameters_optional_unmet.P1`, 감점 아님) P2·P3 로 소계를 냈다. 비상장 2사 ⑨ 는 비상장 경로로 −2 이고 실격 처리는 없다. FCF 음수 기업(amazon·oracle·alibaba·spacex-xai)은 런웨이 사다리로만 깎였다.
- Q22(지분 평가이익을 ⑦ 증거로 셌나): pass — ⑦ 14건 모두 observation_ids 가 비어 있다. calc 키는 `funding_dependent_share`·`own_money_returns` 두 축이거나 비어 있다. 영업외 비중은 ⑥ P4 에만 쓰인다.
