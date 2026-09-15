# 리뷰 3차 A 사실·출처 — needs_fix, 두 세션 분담

- 일시. 2026-09-15. 기준 `04439f7`. part `review-obsreg` 커밋 `2088a21`.
- **분담.** qwen 이 오래 걸려 사용자 요청으로 조율자가 두 항목(부재 주장 전수 재검색 · Q23 이해상충)을 codex 새 대화에 나눴다. qwen 에게는 진행 중 범위 조정을 보냈다. 두 세션은 서로의 산출을 보지 않았다.
  - qwen → `reviews/_parts/.../fact-sources.md` (verified 관측 103건 전수, legacy 공급사 표시 25쌍, 판단 근거란 인용, Q05·Q09·Q14)
  - codex → `validation/fact-sources-split/codex.md` (부재 주장 전수 · Q23 · Q09 부재 부분)
- 합칠 때 fact-sources part 에 codex 분담 절을 붙이고 검토자 줄에 두 세션을 적는다.

## 결과 요지

- **verified 103건 값·단위·기준일·귀속 전부 일치**(qwen). legacy 공급사 표시, 판단 근거란 행 번호, FIX-53 정정도 원문과 맞다.
- Q23 pass, 이해상충 고지 반영 확인(codex).

## 조율자 확인과 처리 안

| 발견 | 세션 | 확인 | 성격 | 처리 안 |
|---|---|---|---|---|
| **openai.F4 = 4 의 1차 근거가 OpenAI 공개 InferenceX 벤치마크**(이해당사자 발표), 배치 계획이 상향 근거에 섞임. 저장소 방증 0건 | qwen · medium | **사실.** 활성 근거 첫 줄. 채점규칙 382행 | 승계 · 미등록 · nvidia.F2(TEN-RA-02)와 같은 성격 | 긴장 등록(하향 가능 3, openai 총점 2→1 시 oracle 과 13위 동률 갈림) |
| spacex-xai offbalance_B note `Spectrum 거래분 … 분해가 미공시다` | codex · high | **틀린 note.** 10-Q: `approximately $19.6 billion, consisting of (i) approximately $11.1 billion in equity … 261.8 million shares … $42.40 per share, and (ii) up to $8.5 billion related to the payoff of designated EchoStar debt, with any shortfall below $8.5 billion to be paid in cash`. Note 16 약정표 `includes the Company's commitments under the Spectrum Transaction, which are payable in cash and in the Company's Class A common stock` | 이번 실행 관측 · **B종에 주식 지급분이 들어가는지 정의 문제** | note 정정. B종 정의(현금 부담인지)를 규칙에서 확인하고, 주식분 제외 민감도(약정표 안 Spectrum 비중이 문면으로 정해지는 만큼)를 기록. spacex-xai G4 는 G1 fail 경로의 진단이라 점수 경로 확인 |
| 비상장 priv31 `not_disclosed_confirmed` 10건 — 공시 의무 없음이라는 지위가 실제 미공개의 증거는 아님 | codex · medium | 라벨 기준은 MISS-LABEL-23 구조 기준이고 **C-20 사용자 확정(2026-09-11)** 의 탐지 조건이다 | 결정된 기준 · 근거 기록 부족 | **기준 유지.** 각 관측 basis 에 검색 범위(v1.5 원문 `미공시`, 보존 조달 발표에 수치 없음)를 적고 라벨 뜻을 "구조적 미공시"로 한정 |
| apple·palantir lease_liabilities `not_disclosed_confirmed` — companyfacts 표준 태그 부재를 발행사 미공시로 승격 | codex · medium | 사실. 10-Q 전문 미보존·미검색 | 이번 실행 라벨 | 자료 범위에 맞는 라벨로. 점수 경로 소비 여부 확인 |
| alibaba contracted_revenue `basis.limit` 이 Note 5 `중요하지 않다` 를 잔여 의무 부재로 읽음 | codex · medium | 원문은 과거 이행 의무의 당기 인식 매출이 중요하지 않다는 뜻 | 이번 실행 설명 | 문장 정정. 전문 검색 RPO 부재 판정은 유지 |
| 승계 v15 null 관측의 `not_disclosed` 라벨(spacex ttm_per 적자, 비상장 runway 입력 부재, palantir net_borrowing 없음 등) | codex · medium | 사실 — 산출 불가·해당 없음과 미공시 구별 안 됨 | 라벨 위생 | MISS-LABEL-23 분류대로 재라벨. 점수 경로 확인 |
| anthropic·openai F7 note `원문 없음` 포괄 표현 | codex · low | FIX-54 S6 에 이미 있음 | — | — |
| alibaba net_cash `채무증권과 대출을 나누지 않는다` | codex · low | Note 11 에 일부 구분 있음 | 설명 | 한계 문장 좁히기 |
| tsmc revenue_ttm_prior `FY2024 20-F 의 공시 USD 70,598.8` 은 FY2023 값, 예시 성장률도 한 해 앞 쌍 | qwen · low | 사실(companyfacts 2023 = 70,598.8M) | 설명 | 정정 |
| spacex-xai revenue_ttm_prior 도 단일 분기인데 period_label 없음 | qwen · low | 사실 | 명명 | 3단계 revenue_ttm 과 같게 |
| apple lease `값이 붙은 일자는 전부 회계연도 말` 과잉 | qwen · low | 2020-06-27 까지 분기말 fact 있음 | 설명 | 정정 |

## 두 세션의 겹침

apple·palantir 리스 부재를 qwen 은 "companyfacts 와 일치" 로, codex 는 "라벨이 자료 범위를 넘는다" 로 적었다. 모순이 아니다 — 자료 부재는 맞고 라벨의 뜻이 넓다.

## 수렴 문제 (3차 누계)

3차에서 새로 나온 **미등록 승계 판단 문제**: C 넷(anthropic F7 · palantir/oracle F1 · tesla F5/F8 · alibaba F3), B 하나(oracle F3), A 하나(openai F4). 2차 누계 넷. 새 세션마다 v1.5 원문의 다른 모순을 찾는다.
