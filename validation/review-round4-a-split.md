# 리뷰 4차 A 분담(부재 주장 전수·Q23) — needs_fix

- 일시. 2026-09-16. NTM-전망치조사 워크트리의 Claude 독립 세션. part `review-obsreg` `validation/fact-sources-split/ntm.md`(커밋 `0752b05`). 기준 `ab5a053`.
- 세션 선택. codex 주간 한도가 10% 아래로 떨어져 사용자가 NTM Claude 세션을 지정했다. 이해상충 때문에 Anthropic 점수에 닿는 판단은 재판정하지 말고 발견으로만 적으라고 명시했고, 리뷰어가 그대로 지켰다.
- 범위. 부재 주장 관측 52건·판단 9건 재검색, Q23, Q09 중 부재 주장 부분.

## 조율자 확인

| 발견 | 확인 | 처리 |
|---|---|---|
| **high · `tesla.undrawn_credit.fix54` 가 `미확인` 인데 보존 companyfacts 에 기준일 값이 있다** — us-gaap `DebtInstrumentUnusedBorrowingCapacityAmount` 2026-06-30 = 5,000,000,000(10-Q accn 0001628280-26-049270) | **사실.** 조율자가 보존 companyfacts 14개를 `Unused\|Undrawn\|RemainingBorrowingCapacity\|LineOfCreditFacility` 정규식으로 다시 훑었다. **기준일 이후 값이 있는 회사는 TSLA 하나뿐이고 oracle 에는 없다.** tesla 는 FCF 양수라 G3 미계산 → **점수 불변** | 등록·census 문구 정정. 원인은 고정 태그 후보만 훑은 것(AGENTS.md 117행이 경고한 함정) |
| medium · run.json 111·115행이 apple·palantir 리스 라벨을 아직 `not_disclosed_confirmed` 로 적음 | 사실 — FIX-54 2단계에서 관측은 `unverified` 로 바뀌었다 | 가정문 정정 |
| medium · `palantir.offbalance_note.v15` 만 `없음`, 다른 회사는 `미확인` | 사실. 보존 PLTR companyfacts 에 기준일 부외 태그 없음 | `미확인` 계열로 |
| medium · 비상장 2사 보도자료가 `sources.json` 에 없고 관측 source_id 는 `SRC-v15-md` | 사실 | 출처 등재 + `conflict_of_interest` 기재. 초안·HTML 참고문헌에 노출 |
| **medium · Q23 fail — `anthropic.F2` 5점 근거에 하네스 표기가 없다** | 사실. openai.F2 는 `표준 하네스 62.7%` 로 명시하고 어댑터 99.9% 배제 이유까지 적는데, anthropic.F2 의 `ARC-AGI-3 30.2%` 는 하네스 미표기이고 저장소에 받치는 자료가 없다. 재검토 약속은 `decisions.C-03.pending_recheck` 에 있으나 `open_tensions` 에는 없다 | **긴장 등록**(점수 5 유지, 방향 하향 가능, 비 Claude 재판정, 발동 조건은 독립 기관의 같은 하네스 측정) |
| low 넷 | tsmc 여신 관측의 기간 불일치 · amazon RPO 표현 · openai checked_scope 범위 서술 · 한계 절에 이해상충 없음 | 정정 |

## 리뷰어가 물은 것 — 조율자 판정

`spacex-xai.undrawn_credit.fix54` 가 신용장 645M 을 전액 차감했는데 그 신용장이 제한현금 담보라, 같은 제한현금이 현금 93,522M 에 들어 있으면 이중 계산이라는 물음. **이중 계산이 아니다.** 등록 현금은 `CashAndCashEquivalentsAtCarryingValue` 순수 현금이고 제한현금 830M 은 basis 의 별도 칸이다. 신용장 전액 차감은 보수적 하한일 뿐이다. 관측 basis 에 이 사실을 적게 해 같은 물음이 반복되지 않게 한다.

## Q09 부재 주장 부분

리뷰어가 `nvidia.F2`(TEN-RA-02)·`openai.F4`(TEN-RA3-01)를 승계 예외로 인정하고 pass 차단 사유에서 제외했다. 승계 예외가 설계대로 작동한 첫 사례다.
