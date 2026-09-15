# 리뷰 3차 B 재무 계산 — needs_fix, spacex-xai 미인출 여신 누락으로 F9 -4→-3

- 일시. 2026-09-15. codex gpt-5.6-sol 새 대화(C 뒤), part `review-obsreg` 커밋 `2c56e9f`. 기준 `04439f7`.
- 결과. needs_fix. **등록 관측·판단 고정 재계산에서 14개사 F6·F9 점수와 경계 플래그 일치.** 점수를 바꾸는 것은 새 관측 누락 하나.

## FC-01 high — spacex-xai 확정 미인출 여신 (점수 변경)

원문(보존 10-Q `3cf9799:validation/offb-24/_raw/spcx-20260630.htm`)에서 조율자 확인.
- `In May 2026, SpaceX amended the SpaceX Credit Facility to increase the borrowing capacity up to $ 5,000 million ("Amended SpaceX Credit Facility")` · 만기 2031-05-19
- `As of June 30, 2026, no amounts were outstanding under the SpaceX Credit Facility` · `As of June 30, 2026, the Company was in compliance with all covenants under the SpaceX Credit Facility`
- 신용장 `$ 645 million at June 30, 2026 … All of the outstanding letters of credit were collateralized by restricted cash.` 시설의 performance LC 한도 안에서 발행됐는지는 문면으로 확정 안 됨.

results 에서 현재 G3 는 `runway_years 2.8911`, step -1, 경계 거리 -3.63%(허용폭 밖) → G1 -3 에 더해 **-4**. 연 소진 = 93,522M / 2.8911 = 약 32,348M.

| 여신 | 런웨이 | G3 | F9 | 총점 |
|---|---|---|---|---|
| 없음(현재) | 2.891 | -1 | -4 | 10 |
| $4,355M (신용장 전액 차감) | 3.026 | 0 · 경계 true | -3 | 11 |
| $5,000M | 3.046 | 0 · 경계 true | -3 | 11 |

**신용장 차감 여부와 무관하게 결론이 같다.** 설계 지침 6.4 "조건이 확인된 확정 미인출 여신" 적용이고 alibaba(FIX-53 2단계)와 같은 기준이라 새 결정이 아니다. spacex-xai 총점 11 은 tsmc·anthropic(10)을 넘는다.

**같은 계열 여덟 번째 "이미 저장소 안에 있었다".** alibaba 누락을 고칠 때 14개사 전부의 확정 미인출 여신을 한 번 훑게 하지 않은 조율자 누락이다. FC-02 amazon 도 같다.

## 나머지

| # | 발견 | 성격 | 처리 안 |
|---|---|---|---|
| FC-02 medium | amazon 미인출 revolving $20B · delayed draw $17.5B 미등록. 넣으면 런웨이 9.95년, F9 -2 불변 | 새 관측 누락(이번 실행 G3 잣대) | **14개사 확정 미인출 여신 전수 조사**로 함께 |
| FC-03 medium | spacex-xai net_cash 가 운용리스 유동 344M 만 차감 — 비유동 부재를 0 으로 합산(`measure._lease` 의 `sum(v or 0)`) | 이번 실행 관측 · 점수 무영향(P2 없는 트랙) | verified 완전 합산 표기 정정, 결측을 0 으로 합산하지 않게 |
| FC-04 medium | tsmc P1 이 연결 전체 순이익, alibaba 는 모회사 귀속 순이익 — P1 소유 범위 불일치 | 이번 실행 P1 정의 · 점수 무영향(둘 다 P1 -1) | P1 분자를 모회사 귀속으로 정의·통일 |
| FC-05 low | apple TTM 관측 시작일 하루 중복(2025-06-28 → 06-29) | 메타데이터 | 정정 |
| FC-06 medium | TTM 성분 accession 을 basis 에 보존하라는 규칙(v1.7 736행)을 alphabet·meta 두 관측이 미충족 | 이번 실행 관측 계약 | 성분 accession 보존 전수 |
| FC-07 medium | oracle.F3 가속 판정도 같은 정의 비교 쌍이 없음 — TEN-RB-Q10 에 없음 | 승계 · 미등록 | TEN-RB-Q10 affected 에 oracle 추가 |
| FC-08 low | TEN-RB-Q10 셋은 승계 예외 적용 | 인정 | — |
