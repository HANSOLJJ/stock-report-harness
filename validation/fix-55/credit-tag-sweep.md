# FIX-55 2단계 — 확정 미인출 여신 태그 광역 주사

`validation/f6-avail-15/_raw/*.companyfacts.json` 12개 파일(상장 12개사)을 정규식
`Unused|Undrawn|RemainingBorrowingCapacity|LineOfCreditFacility` 로 훑어 **시점형(instant) 사실이 있는 태그**를 전부 모았다.
FIX-54 S2 는 `LineOfCreditFacilityMaximumBorrowingCapacity` 계열 고정 후보만 봤고, 그래서 tesla 의
`DebtInstrumentUnusedBorrowingCapacityAmount` 를 놓쳤다(4차 리뷰 A 분담 high · AGENTS.md 117행).

| 티커 | 태그 수 | 가장 최신 사실 | 값 | 제출본 |
|---|---|---|---|---|
| AAPL | 0 | — | — | — |
| AMZN | 2 | `LineOfCreditFacilityFairValueOfAmountOutstanding` 2016-12-31 | 0 USD | 10-K 0001018724-17-000011 |
| BABA | 0 | — | — | — |
| GOOGL | 1 | `LineOfCreditFacilityMaximumBorrowingCapacity` 2015-09-30 | 3,000,000,000 USD | 10-Q 0001652044-15-000005 |
| META | 1 | `LineOfCreditFacilityAmountOutstanding` 2013-09-30 | 0 USD | 10-Q 0001326801-13-000031 |
| MSFT | 2 | `LineOfCreditFacilityMaximumBorrowingCapacity` 2014-09-30 | 5,000,000,000 USD | 10-Q 0001193125-14-380252 |
| NVDA | 1 | `LineOfCreditFacilityCurrentBorrowingCapacity` 2017-01-29 | 575,000,000 USD | 10-K 0001045810-17-000027 |
| ORCL | 0 | — | — | — |
| PLTR | 1 | `LineOfCreditFacilityMaximumBorrowingCapacity` 2021-12-31 | 400,000,000 USD | 10-K 0001193125-22-050913 |
| SPCX | 0 | — | — | — |
| TSLA | 3 | `DebtInstrumentUnusedBorrowingCapacityAmount` 2026-06-30 | 5,000,000,000 USD | 10-Q 0001628280-26-049270 |
| TSM | 0 | — | — | — |

**기준일(2026 회계 분기) 이후 값이 있는 회사는 TSLA 하나다.** 나머지는 최신 사실이 2013~2021년이고, AAPL·BABA·ORCL·SPCX·TSM 은
해당 태그 자체가 없다. **oracle 에는 없다** — G3 가 점수를 내는 유일한 미등록 기업이라 이 주사로도 값이 생기지 않았고 점수는 그대로다.

비상장 2사(anthropic·openai)는 companyfacts 가 없어 이 주사의 대상이 아니다. 관측을 만들지 않는 이유는 run.json 가정문에 있다.
다만 openai 보도자료(2026-03-31)에 `We have also expanded our existing revolving credit facility to approximately $4.7 billion` 이 있다 —
**시설 규모이고 미인출액이 아니며** 회사 자체 발표라 등록하지 않았다. G3 는 C-20 경로로 생략되어 점수에도 닿지 않는다.
