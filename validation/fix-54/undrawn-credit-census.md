# FIX-54 1단계 S2 — 확정 미인출 여신 14개사 전수

보존 원문만 봤다(3cf9799 offb-24 · f14a235 tsm-edgar-29 · validation/f6-avail-15 companyfacts). 새로 받지 않았다.
런웨이는 G3 가 계산되는 FCF 음수 회사만 의미가 있다(나머지는 G2 에서 끝남).

| 회사 | 보존 원문 | 시설 · 한도 | 미인출(기준일) | 조건 확인 | 등록 | 런웨이(년) 전 → 후 | F9 |
|---|---|---|---|---|---|---|---|
| spacex-xai | 10-Q 2026-06-30 | Amended SpaceX Credit Facility 5,000M (2031-05-19) · 신용장 645M(제한현금 담보, 시설 안 발행 여부 미확정) · X Corp 회전여신 한도 0(2025-02 감액) | 전액 미인출 | 미인출 · 약정 준수 · 만기 | **verified 4,355M**(확인 하한, 5,000M 이면 3.046) | 2.891 → **3.026** (경계 true +0.86%) | **-4 → -3** |
| amazon | 10-Q 2026-06-30 | 회전 15.0B(2028-11) · 364일 5.0B(2026-10) · 지연인출 17.5B(2026-09-30 까지 단일 인출) · CP 프로그램 30.0B(약정 아님, 제외) | 전액 미인출 | 미인출 · 만기 · covenant 문장 없음 | **verified 37,500M** | 6.728 → 9.954 (15.0B 만이면 8.02) | -2 불변 |
| alibaba | 20-F 2026-03-31 | 회전 3.33B(2028-09) · 3.17B 시설 미사용 약정 approximately 2.6B | 3.33B 미인출 | 미인출 · 약정 준수 | verified 3,330M(FIX-53) · 2.6B incompatible_basis | 2.639 → 3.100 (FIX-53) | -3 (FIX-53) |
| oracle | **본문 없음** | companyfacts 최근 여신 태그 없음 | — | — | not_disclosed · unverified | 1.321 그대로 | -3 · **G3 가 점수에 닿는 회사**. step 0 이 되려면 약 39,770M 이상 필요 — 확인 못 함 |
| tsmc | 20-F 2025-12-31 | 전문 검색 `credit facilit`·`unused credit`·`lines of credit`·`unutilized` 0건 | — | — | not_disclosed · unverified | FCF 양수 — G3 없음 | 0 |
| apple | 본문 없음 | companyfacts CommercialPaper 1,997M 만 | — | — | not_disclosed · unverified | FCF 양수 | 0 |
| microsoft | 본문 없음 | 여신 태그 최신 2014-09-30 | — | — | not_disclosed · unverified | FCF 양수 | 0 |
| nvidia | 본문 없음 | 여신 태그 최신 2017-01-29 | — | — | not_disclosed · unverified | FCF 양수 | 0 |
| alphabet | 본문 없음 | 여신 한도 태그 최신 2015-09-30 | — | — | not_disclosed · unverified | FCF 양수 | -1 |
| meta | 본문 없음 | 여신 태그 최신 2013-09-30 | — | — | not_disclosed · unverified | FCF 양수 | -1 |
| palantir | 본문 없음 | 여신 한도 태그 최신 2021-12-31 | — | — | not_disclosed · unverified | FCF 양수 | 0 |
| tesla | 본문 없음 | 여신 한도 태그 최신 2016-12-31 · 신용장 556M(2025-12-31) | — | — | not_disclosed · unverified | FCF 양수 | -1 |
| anthropic | 비상장 · 원문 없음 | — | — | — | **관측 등록 안 함**(인용할 source_id 가 없다) | G3 건너뜀(FCF 미공시) | -2 |
| openai | 비상장 · 원문 없음 | — | — | — | **관측 등록 안 함** | G3 건너뜀(FCF 미공시) | -4 |

점수가 바뀐 회사는 spacex-xai 하나다(S1). oracle 은 원문 부재로 판정할 수 없어 점수 변화가 생기지 않았다 — 원문이 보존되면 다시 볼 대상이다.
