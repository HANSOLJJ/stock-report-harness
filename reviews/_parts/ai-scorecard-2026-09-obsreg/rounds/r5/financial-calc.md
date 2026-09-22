# financial-calc — 재무 계산
검토자: Claude Opus 5 (1M context) · financial-calc 독립 리뷰어 세션 · 2026-09-16 (기준 커밋 4f6288c)
결과: needs_fix
요약: F6 P1~P4 와 F9 G1~G4 를 14개사 전부 관측값에서 직접 재계산했고 엔진값과 한 칸도 어긋나지 않았으며, 밴드 경계·`boundary` 플래그·P4 강등 조건·런웨이·환율·순현금까지 원자료로 대조해 모두 재현됐습니다. 다만 spacex-xai 는 P2 입력 세 개가 이 실행 안에 모두 갖춰져 있는데도 트랙 선택 때문에 P2 가 산출되지 않아 EV/Sales 80배가 점수에 닿지 않으며, 이것이 needs_fix 의 주된 사유입니다.

## 재계산 대조표

재계산은 엔진 코드를 호출하지 않고 `scorecard/rules/v1.7.json` 의 `policies.f6`·`policies.f9` 선언만 읽어 별도 스크래치 스크립트로 수행했습니다. 관측 선택 규칙(verified 우선, 그다음 `observed_at` 최신)도 직접 구현했습니다.

| 기업 | 항목 | 엔진값 | 재계산값 | 일치 | 근거 |
|---|---|---|---|---|---|
| alphabet | F6 P1·P2·P3·P4 → 소계 | 16.8711(0) · 8.9675(-1) · 0.20050(-1) · nonop 0.5067 hit → **-3** | 동일 | ✅ | `alphabet.market_cap.v15` · `alphabet.net_cash.nc37` · `alphabet.revenue_ttm.f6reg28` · `alphabet.pretax_income_ttm.nonop44` |
| alphabet | TTM 창 복원 | 229,692 + (402,836 − 186,662) = 445,866 | 동일 | ✅ | GOOGL companyfacts `Revenues` FY2025 402,836 · H1'25 186,662 · H1'26 229,692 (`validation/f6-avail-15/_raw/GOOGL.companyfacts.json`) |
| alphabet | F9 G1·G2 | 0.331104 통과 → FCF +53,273 악화 → **-1** | 동일 | ✅ | `alphabet.fcf_ttm.cashfcf35` · G1 은 `operating_income_ttm/revenue_ttm` 으로 산출 |
| amazon | F6 소계 | 20.3281(0) · 3.6991(0) · 0.15767(-1) · nonop 0.46593 hit → **-2** | 동일 | ✅ | `amazon.pretax_income_ttm.nonop44` 175,466 = 120,691 + 97,311 − 42,536, AMZN companyfacts 3건 전부 대조 |
| amazon | F9 G2·G3·G4 | -11,625 → -2 · 런웨이 9.9538 step 0 · 커버리지 1.85574 step 0 → **-2** | 동일 | ✅ | 현금 78,213(AMZN companyfacts 2026-06-30) + 미인출 37,500 = 115,713 ÷ 11,625 |
| meta | F6 소계 | 22.1739(0) · 6.7123(0) · 0.27651(-1) · nonop 0.00683 → **-1** | 동일 | ✅ | `meta.*.f6reg28` · `meta.net_cash.nc37` |
| meta | F9 G1·G2 | 0.380842 통과 → FCF +40,976 악화 → **-1** | 동일 | ✅ | `meta.fcf_ttm.cashfcf35` |
| microsoft | F6 소계 | 27.5890(-1) · 11.2765(-1) · 0.17789(-1) · nonop 0.06447 → **-3** | 동일 | ✅ | TTM 은 `direct_fy_is_ttm`(FY2026 = 2025-07-01~2026-06-30), 4분기 합 일치 선언 확인 |
| microsoft | F9 G1·G2 | 0.467808 통과 → FCF +66,987 안정 → **0** | 동일 | ✅ | `microsoft.fcf_ttm.cashfcf35` |
| tsmc | F6 소계 | 39.7298(-1) · 17.1365(-1) · 0.31605(0) · P4 `period_basis_not_ttm` → **-3** | 동일 | ✅ | 트랙 `listed_annual`(share_basis adr) |
| tsmc | 환율 환산 | 매출 3,809,054.3 ÷ 31.37 = 121,423.47 · 순이익 1,697,604.0 ÷ 31.37 = 54,115.52 | 동일 | ✅ | 보존 20-F `f14a235:validation/tsm-edgar-29/_raw/tsm-20251231.htm` 선언 환율 NT$31.37, 전년도 2,894,307.7 도 같은 환율 적용 확인 |
| tsmc | P3 환율 불변성 | USD 0.31605 = TWD 3,809,054.3/2,894,307.7 − 1 | 동일 | ✅ | 당해·전년 같은 환율이라 상쇄됨을 직접 검산 |
| tsmc | 모회사 귀속 범위 | 순이익 1,697,604.0(귀속) · 연결 1,695,124.9 · 비지배 −2,479.1 | 동일 | ✅ | `basis.ownership_correction` 인용문과 P1 39.7298 일치 |
| tsmc | F9 G1·G2 | 0.508287 통과 → FCF +31,959.3 안정 → **0** | 동일 | ✅ | `tsmc.operating_margin_ttm.f6reg28` |
| alibaba | F6 소계 | 17.9788(0) · 1.4836(0) · 0.027423(-3) · nonop 0.61242 + `period_basis_not_ttm` → **-4** | 동일 | ✅ | `alibaba.*.obsreg25`·`.f6reg28`·`.nonop44` |
| alibaba | 환율 환산 | 매출 1,023,670 ÷ 6.898 = 148,401.0 · 전년 996,347 ÷ 6.898 = 144,440.0 | 동일 | ✅ | 보존 20-F `3cf9799:validation/offb-24/_raw/baba-20260331.htm` 손익계산서, 전년에 같은 환율 적용 확인 |
| alibaba | 세전이익 | 129,387 RMB백만 ÷ 6.898 = 18,757.18 | 동일 | ✅ | 같은 20-F `INCOME BEFORE INCOME TAX` 행(변환 텍스트 6773행) |
| alibaba | net_cash 재합산 | 625,509 − 281,722 = 343,787 RMB백만 ÷ 6.898 = 49,838.65 | 동일 | ✅ | 20-F 대차대조표 차입 5행(28,224·47,450·117,485·55,861·10,976) · 주석 11 증권 분할(100,594 + 238,075 시장성, 130,447 + 10,880 제외) · 주석 6 리스 21,726 을 전부 문면에서 확인 |
| alibaba | 지분법·비상장·제한현금 제외 | 206,803 · 130,447 · 42,038 제외 | 동일 | ✅ | 대차대조표·주석 11·주석 10 에서 각 값 확인, 제외 합 390,168 검산 |
| alibaba | F9 G2·G3·G4 | -7,226 → -2 · 런웨이 3.09964 step 0(경계 +3.32%, 허용폭 밖) · G4 C-16 강등 -1 → **-3** | 동일 | ✅ | 현금 19,068 + 미인출 3,330 = 22,398 ÷ 7,226 · 미인출 여신은 20-F 주석 21 원문(raw 25431행)에서 `US$ 6.5 billion to US$ 3.33 billion … not yet been drawn` 확인 |
| anthropic | F6 비상장 | ps_ratio 30.0 → -4 · arr_growth 는 kind 불인정 · capital_efficiency 0.52 충족 · require_all 미달 → **-4** | 동일 | ✅ | `anthropic.ps_ratio.priv31` 구간 30~39 양 끝 같은 밴드 · `anthropic.arr.v15` kind=run_rate |
| anthropic | F9 C-20 경로 | G1 판정 보류 → G2 -2 → G3 생략 → G4 추가 감점 없음 → **-2** | 동일 | ✅ | `anthropic.operating_margin_ttm.priv31` missing_type=not_disclosed_confirmed · `anthropic.fcf_ttm.priv31` 동일 라벨 |
| apple | F6 소계 | 36.7641(-1) · 10.0205(-1) · 0.14242(-2) · nonop 0.00672 → **-4** | 동일 | ✅ | P2 는 legacy `apple.net_cash.v15` 62,200 위에 서고 `unverified_inputs` 에 표시됨 |
| apple | TTM 창 복원 | 364,357 + (416,161 − 313,695) = 466,823 | 동일 | ✅ | AAPL companyfacts 세 값 모두 대조, 회계연도 9월 종료 반영 |
| apple | F9 G1·G2 | 0.331730 통과 → FCF +136,683 안정 → **0** | 동일 | ✅ | `apple.fcf_ttm.cashfcf35` |
| nvidia | F6 소계 | 28.1005(-1) · 17.8311(-1) · 0.83376(0) · nonop 0.140000 → **-2** | 동일 | ✅ | 세전 229,743 = 141,410 + 141,450 − 53,117, NVDA companyfacts 3건 대조 |
| nvidia | F9 G1·G2 | 0.652140 통과 → FCF +127,006 안정 → **0** | 동일 | ✅ | `nvidia.fcf_ttm.cashfcf35` |
| palantir | F6 소계 | 134.9160(-2) · 64.6205(-2) · 0.78921(0) · nonop 0.14232 → **-4** | 동일 | ✅ | P2 는 legacy `palantir.net_cash.v15` 9,200 위에 서고 `unverified_inputs` 에 표시됨 |
| palantir | F9 G1·G2 | 0.427985 통과 → FCF +3,358.272 안정 → **0** | 동일 | ✅ | `palantir.fcf_ttm.cashfcf35` |
| spacex-xai | F6 소계 | P3 0.91943(0) · P4 `period_basis_not_ttm` + `short_history` → **-1** | 동일 | ✅ | 트랙 `listed_newly`, P1·P2 미산출. 미산출 자체는 아래 발견 사항 1번 |
| spacex-xai | TTM 손익 복원 | 영업 -2,589 + (-2,086) − (-943) = -3,732 · 순이익 -4,937 + (-4,817) − (-1,536) = -8,218 · 세전 -4,219 + (-4,788) − (-1,384) = -7,623 | 동일 | ✅ | FY2025 세 값을 보존 S-1/A `3cf9799:validation/offb-24/_raw/spcx_s1a_20260603.htm`(변환 텍스트 1716·1730·1737·6083행)에서, 반기 값을 SPCX companyfacts 에서 확인 |
| spacex-xai | 세전 음수 처리 | 세전 -7,623 이므로 nonop_share 산출 안 함(`incompatible_basis`) | 동일 | ✅ | `calc_f6_params._nonop_share` 의 `pretax < 0` 분기와 규칙 `negative_denominator` 선언 일치 |
| spacex-xai | net_cash 재합산 | 93,522 + 6,487 − (39,364 + 344) = 60,301 | 동일 | ✅ | SPCX companyfacts 2026-06-30 태그 전부 대조. 총액 태그가 금융리스 1,079 를 이미 포함하는 것도 `39,364 − 38,285 = 1,079` 로 재현 |
| spacex-xai | F9 G1·G3·G4 | -0.161951 → -3 · 런웨이 3.02575 step 0(경계 +0.86% ⚠️) · 커버리지 1.60439 step 0 → **-3** | 동일 | ✅ | 현금 93,522 + 미인출 4,355 = 97,877 ÷ 32,348. 미인출은 한도 5,000 − 미결제 신용장 645(companyfacts `LettersOfCreditOutstandingAmount`)로 재현 |
| spacex-xai | FCF | 9,900 − 42,248 = -32,348 | 동일 | ✅ | FY2025 OCF 6,785 · capex 20,737 을 보존 S-1/A(7405·14838행)에서, 반기 값을 companyfacts 에서 확인 |
| tesla | F6 소계 | 370.6625(-2) · 13.3427(-1) · 0.11755(-2) · nonop 0.16197 → **-5** | 동일 | ✅ | `tesla.net_cash.nc37` 27,444 |
| tesla | F9 G1·G2 | 0.042193 통과 → FCF +5,762 악화 → **-1** | 동일 | ✅ | FCF 양수라 G3 미진입, 신규 등록 미인출 여신 5,000 은 점수에 닿지 않음 |
| oracle | F6 소계 | 25.9671(-1) · 8.5995(-1) · 0.17349(-1) · nonop -0.05380 → **-3** | 동일 | ✅ | 세전 19,554 = 국내 8,693 + 해외 10,861(ORCL companyfacts 10-K 2026FY) |
| oracle | 채점표 각주 ᶜ 대조 | 세전 19,554(원문 $19.55B 일치) · 영업이익 20,606(GAAP) 대 원문 22,390(구조조정비 1,779 환입) | 동일 | ✅ | 엔진은 GAAP 유지, 저장값 -0.15 와 재계산 -0.0538 의 차이가 영업이익 정의 차이라는 규칙 설명이 산술로 재현됨(20,606 + 1,779 = 22,385) |
| oracle | TTM 창 | FY2026 67,357 직접 공시, 전년 57,399 | 동일 | ✅ | ORCL companyfacts, `direct_fy_is_ttm` 경로 확인 |
| oracle | F9 G2·G3·G4 | -23,686 → -2 · 런웨이 1.32099 step -1 · 커버리지 2.552 step 0 → **-3** | 동일 | ✅ | OCF 31,977 − capex 55,663 · 현금 31,289 모두 ORCL companyfacts 2026-05-31 |
| openai | F6 비상장 | ps_ratio 39.0 → -4 · 보정 두 조건 모두 미충족 → **-4** | 동일 | ✅ | capital_efficiency 40,000/185,000 = 0.216 |
| openai | F9 G1 | bep_retreat → -4(하한) · G3·G4 생략 → **-4** | 동일 | ✅ | `policies.f9.g1_bep_retreat_score` = -4 를 읽는 경로 확인 |
| 전사 | 시총 교차검증 | 등록 시총 12건 | 주가 × 발행주식수와 대조 | ✅ | 미국 8사 오차 0.2% 이내, tsmc 는 ADR 5.19억 주 × 5 = 25.95억 보통주 대 companyfacts 25.93억, alibaba 는 18.58억 보통주 + 증자 0.71억 = 19.29억 ÷ 8 × $111.76 = $269.5B 대 등록 $270B |
| 전사 | 단위·부호 | 30개 지표 361건 | 지표별 단위 단일(USD·ratio·years·USD/share), 음수여서는 안 되는 지표에 음수 0건, 백만·십억 혼입 0건 | ✅ | `observations.json` 전수 주사 |
| 전사 | 소계 합산 | 14개사 factor 합 = total | 동일 | ✅ | 9개 factor 점수 합이 `total` 과 전부 일치, 결측 factor 0건 |

밴드 경계와 `boundary` 플래그도 전수 재계산했습니다. `boundary_tolerance` 0.03 기준으로 F6 P1~P3 36칸 가운데 플래그가 서는 칸은 없고(가장 가까운 것이 oracle P1 의 +3.87%), P4 `nonop_share` 임계 0.30 에 대해서도 플래그가 없으며, F9 G3 에서는 spacex-xai 의 +0.86% 한 건만 플래그가 섭니다. 엔진 출력과 전부 같습니다.

## 체크리스트

| ID | 결과 | 근거(파일:행) |
|---|---|---|
| Q04 | pass | v1.7 `parameters` 모드에서 시총 크기를 그대로 읽는 점수 경로가 없습니다. P1 은 `market_cap / net_income_ttm`, P2 는 `(market_cap − net_cash) / revenue_ttm` 이라 둘 다 배수이고(`scorecard/rules/v1.7.json` policies.f6.parameters.P1·P2), 예시 사례인 nvidia 는 시총 $5.42T 로 표 최대인데 F6 -2 라서 tesla(-5)·apple(-4)·palantir(-4)보다 높습니다(`results.json` nvidia F6 calc). 시총 자체의 신뢰성도 12건 전부 주가 × 발행주식수로 대조해 확인했습니다. 반대 방향의 오류는 발견 사항 1번에 적었습니다. |
| Q06 | pass | 비상장 P2 의 입력이 `ps_ratio`(밸류 ÷ TTM 보정 매출)이고 `post_money_valuation ÷ arr` 은 참고용으로만 두며 점수에 쓰지 않습니다(`scorecard/rules/v1.7.json` policies.f6.private_multiples · private_bands.input_note). 런레이트를 그대로 나눈 14.85배를 쓰면 anthropic 이 nvidia 보다 싸 보인다는 이유까지 규칙에 적혀 있고 엔진도 `compute_private` 에서 `ps_ratio` 만 읽습니다(`scripts/scorecard/calc_f6_params.py:410` 부근). F6 P3 는 매출 성장률이고 F9 G4 는 계약 수입 대 약정 금액이라 양쪽 다 가치 지표입니다. 남은 한 자리는 발견 사항 5번에 적었습니다. |
| Q10 | fail | F6·F9 안에서는 거리를 가속도로 세운 자리가 없습니다. P3 는 성장률 자체이고 가속을 주장하지 않습니다. 다만 F3 `acceleration=pass` 9건 가운데 microsoft·spacex-xai·tesla·oracle 은 TEN-RB-Q10, tsmc 는 TEN-RC4-04 로 등록돼 있어 승계 판단 예외에 해당하지만(`scorecard/rules/v1.7.json` open_tensions), **amazon 과 palantir 는 어느 긴장에도 등록되지 않았습니다.** 두 건은 발견 사항 2번입니다. |
| Q11 | pass | F9 G1 은 순손실이 아니라 영업손실률로 칸을 나눕니다(`scorecard/rules/v1.7.json` policies.f9.g1_bands_proposed). F6 P1 은 `requires_positive: net_income_ttm` 이라 적자면 산출하지 않을 뿐 감점하지 않습니다(`scripts/scorecard/calc_f6_params.py:229` 부근). openai 의 -4 는 순적자가 아니라 BEP 목표 2030년 후퇴가 사유이고(`judgments.json` openai.F9 inputs.bep_retreat), -4 는 F9 하한이지 실격이 아닙니다. 적자이면서 고성장인 spacex-xai 가 총점 11 로 5위인 것이 1999년 아마존 시험을 통과한다는 방증입니다. |

## 발견 사항

- [severity: high] `scorecard/runs/ai-scorecard-2026-09-obsreg/results.json` spacex-xai F6 · `scorecard/rules/v1.7.json` policies.f6.tracks.listed_newly — **P2 입력 세 개가 이 실행 안에 전부 갖춰져 있는데 트랙 선택 때문에 P2 가 산출되지 않습니다.** 트랙은 `revenue_ttm` 관측의 `period_basis` 하나로 정해지는데(`scripts/scorecard/calc_f6_params.py:40`·`276`), spacex-xai 의 `revenue_ttm` 은 P3 의 전년 대조를 세우려고 분기값(2026Q2 7,814)으로 등록돼 있어 트랙이 `listed_newly` 가 되고 그 트랙의 `parameters` 가 P3 하나뿐이라 P1·P2 가 아예 만들어지지 않습니다. 그런데 P2 의 세 입력은 모두 있습니다. 시총 1,910,000(`spacex-xai.market_cap.v15`), 순현금 60,301(`spacex-xai.net_cash.nc37`, verified), TTM 매출 23,044 입니다. TTM 매출은 같은 실행의 `spacex-xai.operating_margin_ttm.f6reg28` 의 `basis.denominator` 이고 `spacex-xai.revenue_ttm.f6reg28` 의 `basis.ttm_is_constructible.value` 로도 선언돼 있으며, 저 자신이 보존 S-1/A 의 FY2025 매출 18,674 와 companyfacts 의 반기 12,508·8,138 으로 재현했습니다. 이 값으로 계산하면 EV/Sales = (1,910,000 − 60,301) ÷ 23,044 = **80.27** 이라 P2 밴드 -2 입니다. 같은 실행의 legacy 관측 `spacex-xai.ps_ratio.v15` 82.9 가 1,910,000 ÷ 23,044 = 82.88 과 0.02% 차이로 맞아 분모가 옳다는 것을 독립적으로 받칩니다. P2 를 넣으면 소계 -2, P4 강등 한 칸을 더해 트랙 하한 -3 에 걸려 F6 는 -1 이 아니라 **-3** 이고 총점은 11 에서 9 로, 순위는 5위에서 nvidia 와 같은 자리로 내려갑니다. 세 가지가 이것을 단순한 설계 선택이 아니라 결함으로 만듭니다. (1) 규칙의 `listed_newly.select` 문면이 `연간 기간 사실이 없어 P1·P2 입력이 성립하지 않는 기업` 인데 P2 는 성립합니다(성립하지 않는 것은 순이익이 음수인 P1 뿐입니다). (2) 같은 회사의 `operating_income_ttm`·`net_income_ttm`·`pretax_income_ttm` 은 모두 같은 TTM 창(2025-07-01~2026-06-30)으로 등록돼 있어, 매출만 분기 기준인 것은 자료의 한계가 아니라 등록 선택입니다. (3) 잣대가 갈립니다. palantir 는 EV/Sales 64.62 로 P2 -2 를 받는데, 표에서 가장 비싼 80.27 은 가격 파라미터가 아예 없습니다. 어느 긴장에도 등록돼 있지 않고, FIX-55 1단계가 바로 이 `period_basis` 판정 경로를 바꿨으므로 승계 판단 예외에도 해당하지 않습니다. 참고로 `spacex-xai.market_cap.v15` 의 `basis.on_score_path` 는 이 값이 점수 경로 밖이라고 적고 있어, 실행 자신도 상태는 알고 있으나 그것이 옳은지는 묻지 않았습니다.
- [severity: medium] `scorecard/runs/ai-scorecard-2026-09-obsreg/judgments.json` amazon.F3 · palantir.F3 (체크리스트 Q10) — **`acceleration=pass` 인데 성장률의 변화를 재현할 근거가 판단 기록에 없고 긴장에도 등록되지 않았습니다.** amazon 근거란은 `✅후발 가속도` 한 줄뿐이고 성장률 수치가 하나도 없습니다. palantir 근거란에는 가속도를 말하는 줄 자체가 없고 두 줄 모두 모방 불가능성 이야기입니다. 채점규칙 145·153행이 요구하는 것은 실측 성장률의 변화이고, 같은 성질의 문제로 microsoft·spacex-xai·tesla·oracle 은 TEN-RB-Q10 에, tsmc 는 TEN-RC4-04 에 등록돼 있는데 이 둘만 빠져 있습니다. 비교 대상으로 alibaba 는 `클라우드 +34→36→38→45%` 라는 성장률의 열을, openai 는 `2~4월 $25B 정체 → 7월 $40B, MoM +20% 복귀` 라는 변화를 적어 두어 같은 잣대에서 갈립니다. `acceleration` 만 fail 로 읽으면 통과점이 2.0 에서 1.0 이 되어 `rules.f3_ladder` 상 F3 는 3 에서 2 로 내려가고(`scripts/scorecard/rules.py:311`), amazon 총점은 15 에서 14 가 되어 alphabet·meta 와의 공동 1위가 갈리며 palantir 는 6 에서 5 가 됩니다. 저는 재판정하지 않고 등록 누락을 보고합니다.
- [severity: medium] `scripts/scorecard/calc_f6_params.py:69`·`84` — **P4 `nonop_share` 의 입력 관측 id 가 F6 결과의 `observation_ids` 에 남지 않습니다.** `_nonop_share` 는 `obs.number(cid, "pretax_income_ttm")` 과 `operating_income_ttm` 을 읽으면서 `obs_ids` 에 넣지 않아, `results.json` 의 F6 `observation_ids` 에는 market_cap·net_cash·net_income_ttm·revenue_ttm 계열만 들어 있습니다(14개사 전부 확인). 이 조건은 alphabet 을 -2 에서 -3 으로, amazon 을 -1 에서 -2 로 혼자 끌어내리는 자리라(`calc.p4.demotion_sole_cause` 가 `nonop_share`) 점수를 만드는 입력인데 감사 경로에서 빠져 있습니다. `calc.p4.nonop_share_inputs` 에 값은 남지만 어느 관측에서 왔는지는 남지 않아, 관측이 교체되면 무엇이 다시 계산돼야 하는지 결과만 보고는 알 수 없습니다.
- [severity: low] `observations.json` spacex-xai.net_cash.nc37 — 시장성 판정에서 `us-gaap:CryptoAssetFairValueNoncurrent` 1,098(2026-06-30)이 포함 목록에도 제외 목록에도 없습니다. 대차대조표 줄이고 거래 시장이 있는 자산이라 `securities_scope` 의 판단 대상인데 `excluded_nonmarketable_present` 에 비상장 지분 237 과 제한현금만 적혀 있습니다. 넣으면 61,399 가 되어 legacy 60,300 과의 일치가 깨지므로 지금의 제외가 결과적으로는 맞다고 보이지만, 판단한 기록이 없습니다. spacex-xai 는 P2 를 계산하지 않아 오늘의 점수에는 닿지 않습니다. 관측 자신도 `excluded_completeness` 에서 전수 목록이 아니라고 한정하고 있습니다.
- [severity: low] `scorecard/rules/v1.7.json` policies.f6.private_correction.conditions[1] — `capital_efficiency` 에는 `accepted_kinds` 가 없어 같은 `run_rate` 관측이 `arr_growth` 에서는 불인정되고 여기서는 인정됩니다. anthropic 은 0.52 로 이 조건을 충족한 것으로 기록되고(`results.json` anthropic F6 calc.correction), `require_all` 때문에 오늘은 승격이 막혀 점수가 갈리지 않습니다. 규칙 `accepted_kinds_decision.not_changed` 가 사용자 결정 범위 밖이라 두었다고 선언하고 있으므로 미등록 문제는 아닙니다. Anthropic 점수에 닿는 자리라 재판정하지 않고 상태만 적습니다.
- [severity: low] `observations.json` alibaba.net_cash.nc37 · alibaba.market_cap.v15 — P2 안에서 기준일이 어긋납니다. 시총은 2026-09-02 기준이고 8월 증자(보통주 710M)를 반영하는데(제가 19.29억 보통주 ÷ 8 × $111.76 = $269.5B 로 재현했습니다), 순현금은 2026-03-31 기준이라 그 조달 대금 약 $10.2B 가 들어 있지 않습니다. EV 가 그만큼 과대이나 EV/Sales 는 1.4836 에서 1.4149 로 움직일 뿐이라 밴드 0 이 그대로입니다.
- [severity: low] `observations.json` alibaba.net_cash.nc37 basis.components — 리스 21,726 만 `rows` 에 줄과 인용문이 없습니다. 차입 5행은 전부 `line` 을 달고 있어 같은 기준이 적용되지 않았습니다. 값 자체는 제가 보존 20-F 주석 6 `Total operating lease liabilities (Note 19) 21,726` 과 주석 19 의 유동 4,318 + 비유동 17,408 로 확인했습니다.
- [severity: low] `judgments.json` openai.F9 근거란 — `BEP 후퇴만으로 -5`·`이미 -5(바닥)` 라는 문구가 C-06 재척도 이전의 척도입니다. 엔진은 `g1_bep_retreat_score` -4 를 읽고 경로에도 -4 가 남으므로 점수는 맞습니다. 근거란만 옛 척도라 다음 사람이 -5 를 찾게 됩니다.
- [severity: low] `observations.json` amazon.undrawn_credit.fix54 — 37,500 안에 2026-10 만기 364일 시설 5,000 이 들어 있고 연장은 대주 승인 조건입니다. 기준일에서 두 달 뒤 만기인 시설을 다년 런웨이 분자에 넣는 것은 다툼의 여지가 있으나, 미인출 여신을 전부 빼도 런웨이가 6.73년이라 step 0 이 바뀌지 않습니다.

## 확인 못 한 것

- **legacy net_cash 4건의 불일치 원인.** amazon·nvidia·tsmc·alibaba 에서 실측값과 v1.5 legacy 가 갈리는 이유는 규칙 `policies.f6.net_cash.evidence.differs` 에 미해결로 적혀 있고 이번에도 가리지 못했습니다. 다만 P2 는 verified 실측값을 쓰므로 점수에는 legacy 가 들어가지 않습니다. apple 과 palantir 두 곳만 verified 대체가 없어 legacy 를 그대로 씁니다.
- **spacex-xai 비유동 운용리스.** 기준일에 개념 자체가 없어 순현금이 그만큼 과대이고 크기를 확인하지 못했습니다(관측 `basis.completeness` 에 선언돼 있음). 발견 사항 1번대로 P2 를 계산하면 이 결측이 점수 경로로 들어오므로 그때는 크기를 확인해야 합니다.
- **oracle 확정 미인출 여신.** 보존 companyfacts 12개 파일에 `Unused|Undrawn|RemainingBorrowingCapacity|LineOfCredit|BorrowingCapacity|CreditFacility|Revolving` 광역 정규식을 제가 직접 다시 돌렸고, 기준일에 가까운 값이 있는 것은 tesla(`DebtInstrumentUnusedBorrowingCapacityAmount` 2026-06-30 5,000M) 한 곳뿐이라는 실행의 주장을 재현했습니다. oracle 은 해당 사실이 2011년치뿐이라 확인하지 못했고, 런웨이 1.32년(step -1)이라 미등록 아홉 곳 중 유일하게 점수에 닿는 자리입니다. 외부 조회 금지라 이번에 채우지 않았습니다.
- **F9 판단 입력.** `fcf_trend`(stable·deteriorating)·`bep_retreat`·`buffer_erosion`·`coverage_comparable` 은 사람의 검토 입력이라 산술만 검증했고 판정 자체는 제 영역이 아닙니다.
- **TSMC 20-F 우회.** SEC companyfacts 에 해당 접수번호의 ifrs-full 사실이 없어 보존 20-F 문면을 원천으로 쓰는 우회가 걸려 있습니다. 저는 20-F 안의 값과 환산만 대조했고, companyfacts 대조는 자료가 없어 못 했습니다. 다만 FY2024 두 경로 일치(2,894,307.7 / 1,322,053.0)는 관측이 기록한 대로 성립합니다.
- **F6 P4 `nonop_share` 저장값과 재계산값의 남은 차이.** alibaba(0.54 대 0.6124)와 oracle(-0.15 대 -0.0538)의 차이는 규칙에 각각 미해결·해결로 기재돼 있고, 두 경우 모두 hit 여부가 바뀌지 않는다는 점만 확인했습니다. 저장값 쪽 정의를 새로 가리지는 않았습니다.
