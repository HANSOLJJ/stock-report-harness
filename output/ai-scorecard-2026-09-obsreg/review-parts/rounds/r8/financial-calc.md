# financial-calc — 재무 계산
검토자: Claude Opus 5 (1M context) · 8차 독립 리뷰어 세션(NTM-전망치조사 워크트리에서 실행, 읽기는 review-obsreg 절대경로 전용) · 2026-09-17
결과: needs_fix
요약: F6 P1~P4 와 F9 G1~G4 를 엔진 없이 관측·규칙·보존 원자료에서 다시 계산했더니 14개사 전부에서 값·밴드·경계 플래그·강등 칸수·소계·하한 절단·합계·순위가 한 칸도 어긋나지 않았습니다. 다만 F9 G1 에서 openai 가 C-20 의 탐지 조건을 문면 그대로 충족하는데도 비상장 경로로 가지 않고 BEP 후퇴 경로로 하한 −4 를 받으며, 두 경로의 차이가 F9 −4 대 −2(총점 2 대 4)를 가르는데 그 우선순위가 규칙 어디에도 적혀 있지 않아 needs_fix 로 냅니다.

## 재계산 대조표

**검토 기준 확인.** `results.json` 에서 `results_hash` 키를 뺀 정렬 JSON 의 sha256 을 직접 계산해 `d41598800167ccd61b915b486535f3abb2d4bdc0af04305acf0c54fa8c4572be` 를 재현했고, 리뷰 템플릿 frontmatter `results_hash`(`reviews/ai-scorecard-2026-09-obsreg.md:8`)와 같습니다. `input_hashes` 다섯 건(run·observations·judgments·sources·rules)도 해당 파일의 바이트 sha256 과 전부 일치해 결과가 이 파일들에서 나온 것이 맞습니다. 기준 커밋 `3eb0b77` 과 현재 HEAD `1d2bdf9` 의 차이는 다른 리뷰어의 part 파일 한 개뿐이라 제가 읽은 `scorecard/`·`scripts/`·`validation/` 는 기준 커밋과 동일합니다.

**재계산 방법.** 엔진 모듈(`scripts/scorecard/calc_f6_params.py`·`calc_f9.py`)을 불러오지 않고 제 스크래치 파이썬에서 `scorecard/rules/v1.7.json` 의 밴드·임계·하한 선언과 `observations.json` 의 값만으로 다시 계산했습니다. 밴드 판정은 `policies.f6.parameters` 의 `comparison`(P1·P2 `upper_exclusive`, P3 `lower_inclusive`)을 직접 구현했고, 경계는 `boundary_tolerance` 0.03 에 대해 상대거리 `(값 − 가까운 경계) ÷ 가까운 경계` 로 다시 냈습니다. 코드는 저장소에 남기지 않았습니다.

### F6 — 상장·비상장 14개사

| 기업 | 항목 | 엔진값 | 재계산값 | 일치 | 근거 |
|---|---|---|---|---|---|
| alphabet | P1 PER | 16.8711 / 0 | 16.8711 / 0 | 일치 | alphabet.market_cap.v15 ÷ alphabet.net_income_ttm.f6reg28 |
| alphabet | P2 EV/Sales | 8.9675 / -1 | 8.9675 / -1 | 일치 | alphabet.net_cash.nc37 · alphabet.revenue_ttm.f6reg28 |
| alphabet | P3 매출성장 | 0.2005 / -1 | 0.2005 / -1 | 일치 | alphabet.revenue_ttm.f6reg28 ÷ alphabet.revenue_ttm_prior.f6reg28 |
| alphabet | P4 nonop_share | 0.5067 / hit=True | 0.5067 / hit=True | 일치 | alphabet.pretax_income_ttm.nonop44 · alphabet.operating_income_ttm.f6reg28 |
| alphabet | P4 조건·강등 | nonop_share / 1칸 | nonop_share / 1칸 | 일치 | basis.period_basis=ttm · stale 2/6개월 |
| alphabet | F6 소계→점수 | -2 → -3 (하한 -7) | -2 → -3 | 일치 |  |
| amazon | P1 PER | 20.3281 / 0 | 20.3281 / 0 | 일치 | amazon.market_cap.v15 ÷ amazon.net_income_ttm.f6reg28 |
| amazon | P2 EV/Sales | 3.6991 / 0 | 3.6991 / 0 | 일치 | amazon.net_cash.nc37 · amazon.revenue_ttm.f6reg28 |
| amazon | P3 매출성장 | 0.1577 / -1 | 0.1577 / -1 | 일치 | amazon.revenue_ttm.f6reg28 ÷ amazon.revenue_ttm_prior.f6reg28 |
| amazon | P4 nonop_share | 0.4659 / hit=True | 0.4659 / hit=True | 일치 | amazon.pretax_income_ttm.nonop44 · amazon.operating_income_ttm.f6reg28 |
| amazon | P4 조건·강등 | nonop_share / 1칸 | nonop_share / 1칸 | 일치 | basis.period_basis=ttm · stale 2/6개월 |
| amazon | F6 소계→점수 | -1 → -2 (하한 -7) | -1 → -2 | 일치 |  |
| meta | P1 PER | 22.1739 / 0 | 22.1739 / 0 | 일치 | meta.market_cap.v15 ÷ meta.net_income_ttm.f6reg28 |
| meta | P2 EV/Sales | 6.7123 / 0 | 6.7123 / 0 | 일치 | meta.net_cash.nc37 · meta.revenue_ttm.f6reg28 |
| meta | P3 매출성장 | 0.2765 / -1 | 0.2765 / -1 | 일치 | meta.revenue_ttm.f6reg28 ÷ meta.revenue_ttm_prior.f6reg28 |
| meta | P4 nonop_share | 0.0068 / hit=False | 0.0068 / hit=False | 일치 | meta.pretax_income_ttm.nonop44 · meta.operating_income_ttm.f6reg28 |
| meta | P4 조건·강등 | 없음 / 0칸 | 없음 / 0칸 | 일치 | basis.period_basis=ttm · stale 2/6개월 |
| meta | F6 소계→점수 | -1 → -1 (하한 -7) | -1 → -1 | 일치 |  |
| microsoft | P1 PER | 27.5890 / -1 | 27.5890 / -1 | 일치 | microsoft.market_cap.v15 ÷ microsoft.net_income_ttm.f6reg28 |
| microsoft | P2 EV/Sales | 11.2765 / -1 | 11.2765 / -1 | 일치 | microsoft.net_cash.nc37 · microsoft.revenue_ttm.f6reg28 |
| microsoft | P3 매출성장 | 0.1779 / -1 | 0.1779 / -1 | 일치 | microsoft.revenue_ttm.f6reg28 ÷ microsoft.revenue_ttm_prior.f6reg28 |
| microsoft | P4 nonop_share | 0.0645 / hit=False | 0.0645 / hit=False | 일치 | microsoft.pretax_income_ttm.nonop44 · microsoft.operating_income_ttm.f6reg28 |
| microsoft | P4 조건·강등 | 없음 / 0칸 | 없음 / 0칸 | 일치 | basis.period_basis=ttm · stale 2/6개월 |
| microsoft | F6 소계→점수 | -3 → -3 (하한 -7) | -3 → -3 | 일치 |  |
| tsmc | P1 PER | 39.7298 / -1 | 39.7298 / -1 | 일치 | tsmc.market_cap.v15 ÷ tsmc.net_income_ttm.f6reg28 |
| tsmc | P2 EV/Sales | 17.1365 / -1 | 17.1365 / -1 | 일치 | tsmc.net_cash.nc37 · tsmc.revenue_ttm.f6reg28 |
| tsmc | P3 매출성장 | 0.3161 / 0 | 0.3161 / 0 | 일치 | tsmc.revenue_ttm.f6reg28 ÷ tsmc.revenue_ttm_prior.f6reg28 |
| tsmc | P4 nonop_share | 0.0517 / hit=False | 0.0517 / hit=False | 일치 | tsmc.pretax_income_ttm.nonop44 · tsmc.operating_income_ttm.f6reg28 |
| tsmc | P4 조건·강등 | period_basis_not_ttm / 1칸 | period_basis_not_ttm / 1칸 | 일치 | basis.period_basis=annual · stale 8/16개월 |
| tsmc | F6 소계→점수 | -2 → -3 (하한 -7) | -2 → -3 | 일치 |  |
| alibaba | P1 PER | 17.9788 / 0 | 17.9788 / 0 | 일치 | alibaba.market_cap.v15 ÷ alibaba.net_income_ttm.f6reg28 |
| alibaba | P2 EV/Sales | 1.4836 / 0 | 1.4836 / 0 | 일치 | alibaba.net_cash.nc37 · alibaba.revenue_ttm.obsreg25 |
| alibaba | P3 매출성장 | 0.0274 / -3 | 0.0274 / -3 | 일치 | alibaba.revenue_ttm.obsreg25 ÷ alibaba.revenue_ttm_prior.f6reg28 |
| alibaba | P4 nonop_share | 0.6124 / hit=True | 0.6124 / hit=True | 일치 | alibaba.pretax_income_ttm.nonop44 · alibaba.operating_income_ttm.obsreg25 |
| alibaba | P4 조건·강등 | nonop_share,period_basis_not_ttm / 1칸 | nonop_share,period_basis_not_ttm / 1칸 | 일치 | basis.period_basis=annual · stale 5/16개월 |
| alibaba | F6 소계→점수 | -3 → -4 (하한 -7) | -3 → -4 | 일치 |  |
| anthropic | P2 (ps_ratio) | 30.0000 / -4 | 30.0000 / -4 | 일치 | anthropic.ps_ratio.priv31 |
| anthropic | 보정 arr_growth | 0.3830 / met=False | 0.3830 / met=False(kind=run_rate) | 일치 | anthropic.arr.v15 · anthropic.arr_prior.priv31 |
| anthropic | 보정 capital_eff | 0.5200 / met=True | 0.5200 / met=True | 일치 | anthropic.arr.v15 · anthropic.cumulative_raised.priv31 |
| anthropic | F6 점수 | -4 | -4 | 일치 | private floor -5 · ceiling -2 |
| apple | P1 PER | 36.7641 / -1 | 36.7641 / -1 | 일치 | apple.market_cap.v15 ÷ apple.net_income_ttm.f6reg28 |
| apple | P2 EV/Sales | 10.0205 / -1 | 10.0205 / -1 | 일치 | apple.net_cash.v15 · apple.revenue_ttm.f6reg28 |
| apple | P3 매출성장 | 0.1424 / -2 | 0.1424 / -2 | 일치 | apple.revenue_ttm.f6reg28 ÷ apple.revenue_ttm_prior.f6reg28 |
| apple | P4 nonop_share | 0.0067 / hit=False | 0.0067 / hit=False | 일치 | apple.pretax_income_ttm.nonop44 · apple.operating_income_ttm.f6reg28 |
| apple | P4 조건·강등 | 없음 / 0칸 | 없음 / 0칸 | 일치 | basis.period_basis=ttm · stale 2/6개월 |
| apple | F6 소계→점수 | -4 → -4 (하한 -7) | -4 → -4 | 일치 |  |
| nvidia | P1 PER | 28.1005 / -1 | 28.1005 / -1 | 일치 | nvidia.market_cap.v15 ÷ nvidia.net_income_ttm.f6reg28 |
| nvidia | P2 EV/Sales | 17.6898 / -1 | 17.6898 / -1 | 일치 | nvidia.net_cash.nc37 · nvidia.revenue_ttm.f6reg28 |
| nvidia | P3 매출성장 | 0.8338 / 0 | 0.8338 / 0 | 일치 | nvidia.revenue_ttm.f6reg28 ÷ nvidia.revenue_ttm_prior.f6reg28 |
| nvidia | P4 nonop_share | 0.1400 / hit=False | 0.1400 / hit=False | 일치 | nvidia.pretax_income_ttm.nonop44 · nvidia.operating_income_ttm.f6reg28 |
| nvidia | P4 조건·강등 | 없음 / 0칸 | 없음 / 0칸 | 일치 | basis.period_basis=ttm · stale 1/6개월 |
| nvidia | F6 소계→점수 | -2 → -2 (하한 -7) | -2 → -2 | 일치 |  |
| palantir | P1 PER | 134.9160 / -2 | 134.9160 / -2 | 일치 | palantir.market_cap.v15 ÷ palantir.net_income_ttm.f6reg28 |
| palantir | P2 EV/Sales | 64.6205 / -2 | 64.6205 / -2 | 일치 | palantir.net_cash.v15 · palantir.revenue_ttm.f6reg28 |
| palantir | P3 매출성장 | 0.7892 / 0 | 0.7892 / 0 | 일치 | palantir.revenue_ttm.f6reg28 ÷ palantir.revenue_ttm_prior.f6reg28 |
| palantir | P4 nonop_share | 0.1423 / hit=False | 0.1423 / hit=False | 일치 | palantir.pretax_income_ttm.nonop44 · palantir.operating_income_ttm.f6reg28 |
| palantir | P4 조건·강등 | 없음 / 0칸 | 없음 / 0칸 | 일치 | basis.period_basis=ttm · stale 2/6개월 |
| palantir | F6 소계→점수 | -4 → -4 (하한 -7) | -4 → -4 | 일치 |  |
| spacex-xai | P1 PER | 미산출(트랙 제외) | 미산출 — 순이익 -8,218,000,000 < 0 | 일치 | spacex-xai.net_income_ttm.f6reg28 |
| spacex-xai | P2 EV/Sales | 80.2681 / -2 | 80.2681 / -2 | 일치 | spacex-xai.net_cash.nc37 · spacex-xai.revenue_ttm_full.fix56 |
| spacex-xai | P3 매출성장 | 0.9194 / 0 | 0.9194 / 0 | 일치 | spacex-xai.revenue_ttm.f6reg28 ÷ spacex-xai.revenue_ttm_prior.f6reg28 |
| spacex-xai | P4 nonop_share | 미산출(incompatible_basis) | 미산출(세전 -7,623,000,000 < 0) | 일치 | spacex-xai.pretax_income_ttm.fix53 · spacex-xai.operating_income_ttm.f6reg28 |
| spacex-xai | P4 조건·강등 | period_basis_not_ttm,short_history / 1칸 | period_basis_not_ttm,short_history / 1칸 | 일치 | basis.period_basis=quarterly_yoy · stale 2/6개월 |
| spacex-xai | F6 소계→점수 | -2 → -3 (하한 -3) | -2 → -3 | 일치 |  |
| tesla | P1 PER | 370.6625 / -2 | 370.6625 / -2 | 일치 | tesla.market_cap.v15 ÷ tesla.net_income_ttm.f6reg28 |
| tesla | P2 EV/Sales | 13.3427 / -1 | 13.3427 / -1 | 일치 | tesla.net_cash.nc37 · tesla.revenue_ttm.f6reg28 |
| tesla | P3 매출성장 | 0.1175 / -2 | 0.1175 / -2 | 일치 | tesla.revenue_ttm.f6reg28 ÷ tesla.revenue_ttm_prior.f6reg28 |
| tesla | P4 nonop_share | 0.1620 / hit=False | 0.1620 / hit=False | 일치 | tesla.pretax_income_ttm.nonop44 · tesla.operating_income_ttm.f6reg28 |
| tesla | P4 조건·강등 | 없음 / 0칸 | 없음 / 0칸 | 일치 | basis.period_basis=ttm · stale 2/6개월 |
| tesla | F6 소계→점수 | -5 → -5 (하한 -7) | -5 → -5 | 일치 |  |
| oracle | P1 PER | 25.9671 / -1 | 25.9671 / -1 | 일치 | oracle.market_cap.v15 ÷ oracle.net_income_ttm.f6reg28 |
| oracle | P2 EV/Sales | 8.5995 / -1 | 8.5995 / -1 | 일치 | oracle.net_cash.nc37 · oracle.revenue_ttm.f6reg28 |
| oracle | P3 매출성장 | 0.1735 / -1 | 0.1735 / -1 | 일치 | oracle.revenue_ttm.f6reg28 ÷ oracle.revenue_ttm_prior.f6reg28 |
| oracle | P4 nonop_share | -0.0538 / hit=False | -0.0538 / hit=False | 일치 | oracle.pretax_income_ttm.nonop44 · oracle.operating_income_ttm.f6reg28 |
| oracle | P4 조건·강등 | 없음 / 0칸 | 없음 / 0칸 | 일치 | basis.period_basis=ttm · stale 3/6개월 |
| oracle | F6 소계→점수 | -3 → -3 (하한 -7) | -3 → -3 | 일치 |  |
| openai | P2 (ps_ratio) | 39.0000 / -4 | 39.0000 / -4 | 일치 | openai.ps_ratio.priv31 |
| openai | 보정 arr_growth | 0.6000 / met=False | 0.6000 / met=False(kind=run_rate) | 일치 | openai.arr.v15 · openai.arr_prior.priv31 |
| openai | 보정 capital_eff | 0.2162 / met=False | 0.2162 / met=False | 일치 | openai.arr.v15 · openai.cumulative_raised.v15 |
| openai | F6 점수 | -4 | -4 | 일치 | private floor -5 · ceiling -2 |

### F9 — 게이트 경로

| 기업 | 항목 | 엔진값 | 재계산값 | 일치 | 근거 |
|---|---|---|---|---|---|
| alphabet | G1 영업이익률 | 0.331104 / pass | 0.331104 | 일치 | alphabet.operating_income_ttm.f6reg28 ÷ alphabet.revenue_ttm.f6reg28 |
| alphabet | G2 FCF | 53,273,000,000 / positive_deteriorating / -1 | 53,273,000,000 | 일치 | alphabet.fcf_ttm.cashfcf35 |
| alphabet | F9 점수 | -1 | -1 | 일치 | 경로 G1:pass → G2:positive_deteriorating |
| amazon | G1 영업이익률 | 0.120813 / pass | 0.120813 | 일치 | amazon.operating_income_ttm.f6reg28 ÷ amazon.revenue_ttm.f6reg28 |
| amazon | G2 FCF | -11,625,000,000 / negative / -2 | -11,625,000,000 | 일치 | amazon.fcf_ttm.cashfcf35 |
| amazon | G3 런웨이 | 9.9538 / step 0 | 9.9538 (완충 115,713,000,000 ÷ 소진 11,625,000,000) | 일치 | amazon.cash.cashfcf35 + amazon.undrawn_credit.fix54 |
| amazon | G4 커버리지 | 1.8557 / step 0 | 1.8557 | 일치 | amazon.contracted_revenue.obsreg25 ÷ amazon.offbalance_B.obsreg25 |
| amazon | F9 점수 | -2 | -2 | 일치 | 경로 G1:pass → G2:negative → G3: → G4:computed |
| meta | G1 영업이익률 | 0.380842 / pass | 0.380842 | 일치 | meta.operating_income_ttm.f6reg28 ÷ meta.revenue_ttm.f6reg28 |
| meta | G2 FCF | 40,976,000,000 / positive_deteriorating / -1 | 40,976,000,000 | 일치 | meta.fcf_ttm.cashfcf35 |
| meta | F9 점수 | -1 | -1 | 일치 | 경로 G1:pass → G2:positive_deteriorating |
| microsoft | G1 영업이익률 | 0.467808 / pass | 0.467808 | 일치 | microsoft.operating_income_ttm.f6reg28 ÷ microsoft.revenue_ttm.f6reg28 |
| microsoft | G2 FCF | 66,987,000,000 / positive_stable / 0 | 66,987,000,000 | 일치 | microsoft.fcf_ttm.cashfcf35 |
| microsoft | F9 점수 | 0 | 0 | 일치 | 경로 G1:pass → G2:positive_stable |
| tsmc | G1 영업이익률 | 0.508287 / pass | 0.508287 | 일치 | tsmc.operating_margin_ttm.f6reg28 |
| tsmc | G2 FCF | 31,959,300,000 / positive_stable / 0 | 31,959,300,000 | 일치 | tsmc.fcf_ttm.cashfcf35 |
| tsmc | F9 점수 | 0 | 0 | 일치 | 경로 G1:pass → G2:positive_stable |
| alibaba | G1 영업이익률 | 0.048990 / pass | 0.048990 | 일치 | alibaba.operating_margin_ttm.obsreg25 |
| alibaba | G2 FCF | -7,226,000,000 / negative / -2 | -7,226,000,000 | 일치 | alibaba.fcf_ttm.cashfcf35 |
| alibaba | G3 런웨이 | 3.0996 / step 0 | 3.0996 (완충 22,398,000,000 ÷ 소진 7,226,000,000) | 일치 | alibaba.cash.cashfcf35 + alibaba.undrawn_credit.fix53 |
| alibaba | F9 점수 | -3 | -3 | 일치 | 경로 G1:pass → G2:negative → G3: → G4:undetermined |
| anthropic | G1 영업이익률 | None / undetermined | None | 일치 | anthropic.operating_margin_ttm.priv31 missing_type=not_disclosed_confirmed |
| anthropic | G2 FCF | 미공시 / not_disclosed / -2 | 미공시 | 일치 | anthropic.fcf_ttm.priv31 |
| anthropic | F9 점수 | -2 | -2 | 일치 | 경로 G1:undetermined → G2:not_disclosed → G3:skipped → G4:incompatible |
| apple | G1 영업이익률 | 0.331730 / pass | 0.331730 | 일치 | apple.operating_income_ttm.f6reg28 ÷ apple.revenue_ttm.f6reg28 |
| apple | G2 FCF | 136,683,000,000 / positive_stable / 0 | 136,683,000,000 | 일치 | apple.fcf_ttm.cashfcf35 |
| apple | F9 점수 | 0 | 0 | 일치 | 경로 G1:pass → G2:positive_stable |
| nvidia | G1 영업이익률 | 0.652140 / pass | 0.652140 | 일치 | nvidia.operating_income_ttm.f6reg28 ÷ nvidia.revenue_ttm.f6reg28 |
| nvidia | G2 FCF | 127,006,000,000 / positive_stable / 0 | 127,006,000,000 | 일치 | nvidia.fcf_ttm.cashfcf35 |
| nvidia | F9 점수 | 0 | 0 | 일치 | 경로 G1:pass → G2:positive_stable |
| palantir | G1 영업이익률 | 0.427985 / pass | 0.427985 | 일치 | palantir.operating_income_ttm.f6reg28 ÷ palantir.revenue_ttm.f6reg28 |
| palantir | G2 FCF | 3,358,272,000 / positive_stable / 0 | 3,358,272,000 | 일치 | palantir.fcf_ttm.cashfcf35 |
| palantir | F9 점수 | 0 | 0 | 일치 | 경로 G1:pass → G2:positive_stable |
| spacex-xai | G1 영업이익률 | -0.161951 / fail | -0.161951 | 일치 | spacex-xai.operating_margin_ttm.f6reg28 |
| spacex-xai | G3 런웨이 | 3.0258 / step 0 | 3.0258 (완충 97,877,000,000 ÷ 소진 32,348,000,000) | 일치 | spacex-xai.cash.cashfcf35 + spacex-xai.undrawn_credit.fix54 |
| spacex-xai | G4 커버리지 | 1.6044 / step 0 | 1.6044 | 일치 | spacex-xai.contracted_revenue.obsreg25 ÷ spacex-xai.offbalance_B.obsreg25 |
| spacex-xai | F9 점수 | -3 | -3 | 일치 | 경로 G1:fail → G1:방향 완화 판정 불가 → 유지 → G3:diagnostic → G4:computed → G1-after: |
| tesla | G1 영업이익률 | 0.042193 / pass | 0.042193 | 일치 | tesla.operating_income_ttm.f6reg28 ÷ tesla.revenue_ttm.f6reg28 |
| tesla | G2 FCF | 5,762,000,000 / positive_deteriorating / -1 | 5,762,000,000 | 일치 | tesla.fcf_ttm.cashfcf35 |
| tesla | F9 점수 | -1 | -1 | 일치 | 경로 G1:pass → G2:positive_deteriorating |
| oracle | G1 영업이익률 | 0.305922 / pass | 0.305922 | 일치 | oracle.operating_income_ttm.f6reg28 ÷ oracle.revenue_ttm.f6reg28 |
| oracle | G2 FCF | -23,686,000,000 / negative / -2 | -23,686,000,000 | 일치 | oracle.fcf_ttm.cashfcf35 |
| oracle | G3 런웨이 | 1.3210 / step -1 | 1.3210 (완충 31,289,000,000 ÷ 소진 23,686,000,000) | 일치 | oracle.cash.cashfcf35 (미인출 여신 미공시) |
| oracle | G4 커버리지 | 2.5520 / step 0 | 2.5520 | 일치 | oracle.contracted_revenue.fix57 ÷ oracle.offbalance_B.v15 |
| oracle | F9 점수 | -3 | -3 | 일치 | 경로 G1:pass → G2:negative → G3: → G4:computed |
| openai | G1 영업이익률 | None / fail | None | 값은 일치 · **경로는 이견** | `openai.operating_margin_ttm.priv31` missing_type=not_disclosed_confirmed. anthropic 과 같은 라벨인데 결과가 `fail` 과 `undetermined` 로 갈립니다 — 발견 1 |
| openai | F9 점수 | -4 | **−4 또는 −2** | **불일치 가능** | 현행 경로 `G1:fail(BEP 후퇴) → G3/G4 생략` 은 −4, C-20 문면대로 비상장 경로면 −2. 우선순위 미명시 — 발견 1 |

### 순현금 — 보존 companyfacts·20-F 에서 재합산

| 기업 | 항목 | 엔진값 | 재계산값 | 일치 | 근거 |
|---|---|---|---|---|---|
| alphabet | 현금+시장성증권 − 차입 − 리스 | 121,683 | 55,911 + 186,563 − (98,165+1,999+0) − (18,037+2,590) = 121,683 | 일치 | GOOGL.companyfacts 2026-06-30 · `CashCashEquivalentsAndShortTermInvestments` 242,474 로 교차 확인 |
| amazon | 같음 | −119,332 | 78,213 + 44,775 − (132,549) − (96,320+13,451) = −119,332 | 일치 | AMZN.companyfacts 2026-06-30 |
| meta | 같음 | −22,058 | 15,462 + 74,798 − 83,664 − 28,654 = −22,058 | 일치 | META.companyfacts 2026-06-30 |
| microsoft | 같음 | −51,970 | 20,935 + 55,908 − (31,067+9,227) − (21,925+66,594) = −51,970 | 일치 | MSFT.companyfacts 2026-06-30 |
| nvidia | 같음 | 60,509 | 22,443 + 34,143 + 42,783 − (32,366+1,000) − 5,494 = 60,509 | 일치 | NVDA.companyfacts 2026-07-26 |
| oracle | 같음 | −135,538 | 31,289 + 605 − 129,541 − (30,190+7,701) = −135,538 | 일치 | ORCL.companyfacts 2026-05-31 |
| tesla | 같음 | 27,444 | 15,219 + 28,305 − 9,061 − (6,738+281) = 27,444 | 일치 | TSLA.companyfacts 2026-06-30 · 암호자산 674 제외 확인 |
| spacex-xai | 같음 | 60,301 | 93,522 + 6,487 − 39,364 − 344 = 60,301 | 일치 | SPCX.companyfacts 2026-06-30 · 제한현금 830·암호자산 1,098 제외 확인 |
| tsmc | 현지통화 합산 후 환산 | 69,224.96 (US$백만) | (3,240,002.8 − 1,032,987.7 − 35,428.0) = 2,171,587.1 NT$백만 ÷ 31.37 = 69,224.96 | 일치 | `tsmc.net_cash.nc37` rows 6+3+2행 · 보존 20-F `f14a235:validation/tsm-edgar-29/_raw/tsm-20251231.htm` |
| alibaba | 같음 | 49,838.65 (US$백만) | (625,509 − 259,996 − 21,726) = 343,787 RMB백만 ÷ 6.898 = 49,838.65 | 일치 | `alibaba.net_cash.nc37` rows · 지분법 206,803·비상장 130,447·제한현금 42,038 제외 확인 |
| apple · palantir | — | legacy 62,200 · 9,200 | **재계산 불가** | 판정 보류 | 리스부채 실측 결측(`apple.lease_liabilities.nc37`·`palantir.lease_liabilities.nc37`). 엔진이 `calc.unverified_blocked_by` 로 드러냅니다 |

### 환율·ADR — 발행사 선언 편의환산 환율

| 기업 | 항목 | 엔진값 | 재계산값 | 일치 | 근거 |
|---|---|---|---|---|---|
| tsmc | 선언 환율 | 31.37 | 보존 20-F 본문 `NT$31.37 to US$1.00, the exchange rate set forth in the H.10 statistical release of the Federal Reserve Board on December 31, 2025` | 일치 | `f14a235:validation/tsm-edgar-29/_raw/tsm-20251231.htm` |
| tsmc | 매출 FY2025 | 121,423.47 | `NET REVENUE` 행 2023·2024·2025 오름차순 중 셋째 열 3,809,054.3 ÷ 31.37 = 121,423.47 (공시 US$ 칸 121,423.5) | 일치 | 같은 원문 손익계산서 |
| tsmc | 모회사 귀속 순이익 | 54,115.52 | `Shareholders of the parent` 1,697,604.0 ÷ 31.37 = 54,115.52 (공시 54,115.5). 연결 순이익 1,695,124.9 가 아닙니다 | 일치 | 같은 원문 · P1 `input_scope` 모회사 귀속 요건 충족 |
| tsmc | 세전이익 | 65,083.03 | `INCOME BEFORE INCOME TAX` 2,041,654.7 ÷ 31.37 = 65,083.03 (공시 65,083.0) | 일치 | 같은 원문 |
| tsmc | P3 환율 불변성 | 0.316050 | 현지통화 3,809,054.3 ÷ 2,894,307.7 − 1 = 0.3160502 | 일치 | 당해·전년 같은 환율이라 상쇄됩니다 |
| alibaba | P3 환율 불변성 | 0.027423 | 현지통화 1,023,670 ÷ 996,347 − 1 = 0.0274232 | 일치 | `alibaba.revenue_ttm.obsreg25` · `alibaba.revenue_ttm_prior.f6reg28` 둘 다 6.898 |
| alibaba | 시총(ADS) | 270,000 | 24.2억 ADS × $111.76 = $270.5B → 표기 $270B | 일치 | `alibaba.market_cap.v15` basis. status 는 legacy_unverified |
| tsmc | 시총(ADR) | 2,150,000 | 51.9억 ADR × $415.50 = $2,156.4B → 표기 $2.15T | 일치 | `tsmc.market_cap.v15` basis. status 는 legacy_unverified |

### TTM 창·복원 Q4 — 보존 companyfacts 에서 직접 조립

| 기업 | 항목 | 엔진값 | 재계산값 | 일치 | 근거 |
|---|---|---|---|---|---|
| alphabet | revenue_ttm 2025-07-01~2026-06-30 | 445,866 | 229,692(2026 상반기 누계) + 402,836(FY2025) − 186,662(2025 상반기 누계) = 445,866 | 일치 | GOOGL.companyfacts `Revenues` |
| alphabet | revenue_ttm_prior | 371,399 | 186,662 + 350,018(FY2024) − 165,281 = 371,399 | 일치 | 같음. FY2024 350,018 이 두 태그·두 accession 에서 같아 재작성 세대가 섞이지 않았습니다 |
| nvidia | revenue_ttm 2025-07-28~2026-07-26 | 302,970 | 177,837 + 215,938(FY2026) − 90,805 = 302,970 | 일치 | NVDA.companyfacts `Revenues` |
| nvidia | revenue_ttm_prior | 165,218 | 90,805 + 130,497(FY2025) − 56,084 = 165,218 | 일치 | 같음. FY2025 130,497 이 두 accession 에서 동일 |
| oracle | revenue_ttm FY2026 | 67,357 | `2025-06-01..2026-05-31` 단일 연간 공시 67,357 — 복원이 아니라 공시값 자체 | 일치 | ORCL.companyfacts. `ttm_window.anchor` 의 복원 Q4 포함 규칙대로 최신 FY 를 끝점으로 씁니다 |
| oracle | 세전이익 | 19,554 | 국내 8,693 + 국외 10,861 = 19,554 | 일치 | ORCL.companyfacts `IncomeLossFromContinuingOperationsBeforeIncomeTaxes{Domestic,Foreign}` |

### 합계·밴드 경계·순위

- 14개사 전부에서 `moat`(F1~F5 합)·`trap`(F6~F9 합)·`total` 을 다시 더해 저장값과 일치했습니다. worker 보고 총점(alphabet·amazon·meta 15 · microsoft 14 · tsmc·anthropic 10 · spacex-xai·nvidia 9 · apple 8 · alibaba 7 · palantir 6 · tesla 5 · openai·oracle 2)과도 같습니다. 다만 이 일치는 **엔진이 실제로 탄 경로를 기준으로 한 것**이고, 발견 1 의 openai F9 경로가 C-20 문면대로 바뀌면 openai 총점만 2 에서 4 로 움직입니다(나머지 13개사와 anthropic 순위는 불변).
- 순위를 `1 + (조정총점이 더 높은 완료 기업 수)` 로 다시 매겨 14건 전부 저장값과 일치했습니다(동점 공동 순위 포함).
- 경계 플래그(`boundary.flag`)는 P1·P2·P3·nonop_share 전 항목에서 `false` 이고 제 재계산도 같습니다. 유일한 `true` 는 F9 G3 spacex-xai 런웨이 3.0258년(임계 3년 대비 +0.86%)이고, 다음으로 가까웠던 alibaba 3.0996년은 +3.32% 로 허용폭 ±3% 를 넘어 `false` 가 맞습니다.
- P4 `stale_asof` 는 관측 `period.end` 에서 실행 기준일 2026-09-02 까지의 개월 수로 다시 셌습니다 — nvidia 1 · alphabet·amazon·meta·microsoft·apple·palantir·tesla·spacex-xai 2 · oracle 3 · alibaba 5 · tsmc 8. 임계는 ttm·quarterly 6, annual 16 이라 한 건도 걸리지 않고 엔진과 같습니다.

### FIX-58 이 바꿨다고 한 범위 — 제 손으로 다시 확인한 것

- **nvidia 시장성 지분증권 42,783.** `NVDA.companyfacts` 2026-07-26 에 `EquitySecuritiesFvNi` 42,783 이 실재하고 비시장성 `EquitySecuritiesWithoutReadilyDeterminableFairValueAmount` 47,898 과 별개 태그입니다. P2 는 (5,420,000 − 60,509) ÷ 302,970 = 17.6898 이고 밴드 `8~20`(−1)로 이전 17.8311 과 같은 칸입니다. **점수 불변이 맞습니다.**
- **meta 를 더하지 않은 판단이 옳습니다.** `DebtSecuritiesAvailableForSaleExcludingAccruedInterest` 71,255 + `EquitySecuritiesFvNi` 3,543 = 74,798 이 `MarketableSecuritiesCurrent` 74,798 과 정확히 같아, 더하면 이중 계상입니다. 규칙 파일의 `meta_note` 가 맞습니다.
- **`LesseeOperatingLeaseLiabilityUndiscountedExcessAmount` 는 할인차금입니다.** 세 회사에서 관계가 성립합니다 — oracle 41,867 − 30,190 = 11,677, nvidia 7,207 − 5,494 = 1,713, alphabet 21,333 − 18,037 = 3,296. 금융리스도 oracle 11,460 − 7,701 = 3,759 로 같습니다. 미개시 약정 후보가 아니라는 정정이 맞습니다.
- **F9 G1 의 기간 기준.** spacex-xai 영업이익률 −0.161951 은 영업손익 −3,732(TTM) ÷ **`revenue_ttm_full` 23,044**(TTM)입니다. 같은 회사의 `revenue_ttm` 7,814 는 분기(quarterly_yoy)라 그것으로 나눴다면 −0.4776 이 되어 밴드가 −3 이 아니라 **−4** 가 됩니다. 기간을 맞춘 것이 한 칸을 지켰습니다.
- **oracle 각주 ᶜ 대조.** 세전 19,554 · GAAP 영업이익 20,606 · 구조조정비 1,779 를 companyfacts 에서 직접 읽었고 20,606 + 1,779 = 22,385 ≈ 원문 $22.39B 입니다. 엔진이 GAAP 영업이익을 유지해 `nonop_share` −0.0538 이고 |값| < 0.30 이라 판정도 같습니다.

### 단위·부호 전수

점수 경로에 실제로 쓰인 관측 143건의 단위를 훑었습니다. 금액은 전부 `USD` 이고 절대 달러 단위로 저장돼 백만·십억이 섞인 곳이 없습니다. 비율은 전부 `ratio` 입니다. 음수 13건은 전부 뜻이 맞습니다 — 순차입인 net_cash 넷(amazon·meta·microsoft·oracle), 소진인 fcf_ttm 넷(alibaba·amazon·oracle·spacex-xai), 적자인 spacex-xai 의 순이익·영업이익·세전이익·영업이익률, 영업외가 음수인 oracle 저장 nonop_share. 부호가 뒤집힌 항목은 없습니다. `ntm_per`·`ttm_per` 관측은 존재하지만 어느 factor 의 `observation_ids` 에도 없어 점수 경로 밖입니다.

## 체크리스트

| ID | 결과 | 근거(파일:행) |
|---|---|---|
| Q04 | pass | F6 는 시총을 크기로 읽지 않고 비율의 분자로만 씁니다 — P1 `market_cap / net_income_ttm`, P2 `(market_cap − net_cash) / revenue_ttm`(`scorecard/rules/v1.7.json` `policies.f6.parameters.P1.formula`·`P2.formula`). 결과가 크기와 반대로도 움직입니다 — 시총 1위 nvidia($5.42T)가 F6 −2 인데 시총 최하위 alibaba($270B)와 palantir($407B)는 −4 입니다(`results.json` 각사 `factors.F6.score`). 옛 단일지표 `ntm_per`·`ttm_per` 관측은 점수 경로에 없습니다(어느 factor 의 `observation_ids` 에도 미등장). |
| Q06 | pass | 점수를 내는 입력이 전부 가치 단위입니다 — P3 는 매출 성장률, G4 는 계약 수입 ÷ B종 약정(둘 다 USD), 비상장 P2 는 `ps_ratio`(밸류 ÷ TTM 보정 매출)입니다. 런레이트 배수 `post_money_over_arr` 는 `calc.multiples` 에 계산만 되고 점수에 쓰이지 않습니다 — anthropic 14.846·openai 21.3 이 있는데 P2 는 30.0·39.0 을 씁니다(`results.json` anthropic/openai `factors.F6.calc`). 규칙도 그 이유를 `policies.f6.private_multiples` 에 적습니다. 사용자 수·토큰 같은 볼륨 지표는 F6·F9 입력에 한 건도 없습니다(점수 경로 관측 143건 전수). |
| Q10 | fail (승계 예외 · TEN-RB-Q10 · TEN-RC4-04) | 제 영역인 F6·F9 에서는 새 사례를 찾지 못했습니다 — P3 는 성장률, G2 `fcf_trend` 는 방향, G3 런웨이는 잔고 ÷ 소진속도로 전부 축이 맞습니다. 다만 같은 체크리스트 항목의 기존 fail 이 살아 있습니다. `TEN-RB-Q10`(microsoft·spacex-xai·tesla·amazon·palantir·oracle F3 가속도가 성장률 하나로 pass)과 `TEN-RC4-04`(tsmc F3 가속도 근거가 가이던스)이고 둘 다 `status: open`·`recheck_at: 2026-11` 입니다(`scorecard/rules/v1.7.json` `open_tensions`). 이번 실행에서 14개사 F3 는 전부 `carried_score` 라(`results.json` 각사 `factors.F3.status`) 잣대가 바뀌지 않았고, 승계 판단 예외에 해당해 pass 를 막는 사유로 세지 않습니다. |
| Q11 | fail (예외 아님 — 아래 발견 1) | 대부분의 자리는 순적자를 실격으로 쓰지 않습니다 — spacex-xai 는 순이익이 음수라 P1 을 못 만들지만 `parameters_not_in_track.P1` 로 사유를 적고 트랙 하한도 −7 이 아니라 −3 이며, F9 G1 은 순손실이 아니라 영업이익률(−16.195%)로 밴드를 고릅니다. 반면 **openai 는 F9 하한 −4 를 단위경제 측정 없이 받습니다** — `results.json` openai `factors.F9.calc.path[0]` 이 `operating_margin_ttm: null` 인 채 `band: "BEP 후퇴 → -4"` 이고, 같은 회사의 `openai.operating_margin_ttm.priv31` 은 `missing_type: not_disclosed_confirmed` 에 basis 가 `openai 2026 GAAP 손실 약 $60B 전망 · BEP 2030 — 전망이지 실적이 아니다` 라고 적습니다. 실적이 아닌 손실 전망으로 가장 깊은 칸을 주고, 규칙이 그것을 막으려고 둔 C-20 경로는 우회됩니다. |

## 발견 사항

- **[severity: high] `scripts/scorecard/calc_f9.py:122` · `scorecard/rules/v1.7.json` `policies.f9.g1_private_undisclosed_route`(C-20) — openai 가 C-20 탐지 조건을 문면 그대로 충족하는데 비상장 경로로 가지 않는다. 규칙에 그 우선순위가 없고, 갈림이 2점을 정한다.**
  C-20 의 `detection` 은 `company.listed 가 false 이고 operating_margin_ttm 또는 operating_income_ttm 관측의 missing_type 이 not_disclosed_confirmed 일 때` 입니다. openai 는 `results.json` 에서 `listed: false` 이고 `openai.operating_margin_ttm.priv31` 의 `missing_type` 이 `not_disclosed_confirmed` 라 두 조건을 다 채웁니다. 그런데 `scripts/scorecard/calc_f9.py:122` 의 분기가 `if margin is None and not bep_retreat:` 이고 C-20 판정 함수 호출이 그 블록 안 `calc_f9.py:127` 한 곳뿐이라, `bep_retreat == "yes"` 인 openai 는 C-20 판정에 닿지도 못한 채 영업적자 경로로 내려가 `calc_f9.py:153` 에서 `g1_bep_retreat_score` −4 를 받습니다. **`bep_retreat` 가 C-20 보다 앞선다는 문장은 규칙 파일 어디에도 없습니다.** C-06 결정문이 적은 미결 우선순위는 `BEP 후퇴 ↔ 손실률 경계` 사이의 것이고(`decisions` C-06 `summary`) C-20 과의 순서는 언급되지 않습니다. `open_tensions` 16건 어디에도 C-20·F9·bep 문자열이 없어 등록된 긴장도 아닙니다.
  같은 조건의 anthropic 은 C-20 경로로 가 G1 `undetermined` → G2 `not_disclosed` −2 를 받습니다. 두 비상장사가 같은 결측 라벨을 달고 갈립니다. 유일한 분기점은 승계 판단 입력 `bep_retreat`(`judgments.json` `openai.F9`, `reviewer: legacy:v1.5`, `status: carried`) 하나입니다.
  점수 영향 — 현행 openai F9 −4, 총점 2, 공동 13위. C-20 경로였다면 F9 −2, 총점 4, 단독 13위이고 oracle 이 14위가 됩니다. anthropic 점수와 순위(10점·5위)는 어느 쪽이든 바뀌지 않습니다.
  **어느 쪽이 옳은지는 제가 정하지 않습니다.** 다만 C-20 이 세 선택지 중 `assume_loss` 를 버리고 `defer_to_private_g2` 를 고른 결정이고(`run.json` decisions C-20), 그 이유가 `TTM 영업손익을 모르는데 적자라고 단정하는 것이다`(`why_not_assume_loss`)인데, 현행 경로는 TTM 영업손익을 모르는 회사에 손실 경로의 하한을 주고 있습니다. 규칙 문면과 엔진 동작이 갈리고 그 갈림이 점수를 정하므로 문면을 고치든 코드를 고치든 한쪽을 명시해야 합니다.
  승계 예외에 해당하지 않는 이유 — `bep_retreat` 자체는 v1.5 승계 논리가 맞지만, **이 실행이 새로 댄 잣대(C-20, 2026-09-11 사용자 확정)가 닿는 자리**이고 등록된 긴장도 없습니다.

- **[severity: low] `scorecard/rules/v1.7.json` `policies.f6.net_cash.securities_scope.how_to_measure` — `대차대조표 줄만 쓴다` 는 한정과 nvidia 에 주석 태그를 넣은 이번 정정이 서로 다른 방향으로 작동한다. 점수는 안 움직인다.**
  `how_to_measure` 는 합계 줄과 주석 버킷을 쓰지 말라고 합니다. 그 결과 시장성이 확인되는 금액이 남습니다 — nvidia 는 AFS 채무증권 총계 46,900 중 대차대조표 줄 `DebtSecuritiesCurrent` 가 34,143 이고 만기 1년 내 버킷과의 차 6,857 은 현금성자산 안(정정 기록대로), 남는 **만기 1~5년 5,900 은 어느 줄에도 없습니다**. alphabet 은 `OtherLongTermInvestments` 131,461 에서 비시장성 124,259 를 뺀 7,202, microsoft 는 `LongTermInvestments` 36,348 에서 지분법 12,000·비시장성 12,400 을 뺀 11,948, oracle 은 `Investments` 24,126 이 같은 사유로 통째로 빠집니다.
  한편 nvidia 의 `EquitySecuritiesFvNi` 42,783 은 대차대조표 줄이 아니라 주석 태그인데 `주석이 둘을 갈라 준다` 를 근거로 넣었습니다(`nvidia.net_cash.nc37` basis `marketable_equity_added`). 같은 근거를 대면 위 잔여분도 후보가 되고, `how_to_measure` 를 그대로 읽으면 nvidia 의 42,783 도 후보가 아닙니다. 둘 중 하나로 문장을 좁히는 편이 낫습니다.
  민감도 — 잔여분을 전부 더해도 밴드가 움직이지 않습니다. alphabet P2 8.9675 → 8.9514, microsoft 11.2765 → 11.2405, nvidia 17.6898 → 17.6704, oracle 8.5995 → 8.2413 으로 네 곳 다 같은 칸입니다. **오늘 점수는 안 갈립니다.**

- **[severity: low] `results.json` oracle `factors.F9.calc.path[3]` — G4 커버리지의 분자와 분모가 다른 기준일이고 분모가 legacy 다.**
  분자 `oracle.contracted_revenue.fix57` 638,000 은 `measured_as_of: 2026-05-31`(FY2026 10-K)인데 분모 `oracle.offbalance_B.v15` 250,000 은 `status: legacy_unverified` 이고 `as_of` 가 실행 기준일 2026-09-02 이며 `measured_as_of` 가 없습니다. 커버리지 2.552 는 638,000 ÷ 250,000 으로 두 자리 다 반올림된 legacy 자릿수입니다. 엔진이 경고를 남기고는 있습니다(`factors.F9.warnings`).
  민감도 — G4 임계가 1.0 이라 분모가 638,000 을 넘어야 판정이 바뀌는데 지금의 2.55배에서 그만큼 움직일 근거가 없습니다. **점수 불변입니다.** 규칙 파일도 같은 자리를 이미 `다음 라운드에서 정한다` 로 적어 두었습니다.

- **[severity: low] `scorecard/rules/v1.7.json` `policies.f6.private_correction.conditions` — `arr` 의 kind 제한이 두 조건 중 하나에만 걸려 있다. anthropic 점수에 닿으므로 재판정하지 않고 사실만 적는다.**
  `arr_growth` 는 `accepted_kinds: ["actual"]` 로 `kind=run_rate` 입력을 거부하는데, 같은 `anthropic.arr.v15`(kind `run_rate`)를 읽는 `capital_efficiency` 에는 같은 제한이 없어 0.52 로 충족 처리됩니다(`results.json` anthropic `calc.correction.conditions`). 규칙 파일이 이 비대칭을 `accepted_kinds_decision.not_changed` 에 사유(사용자 결정 범위)와 함께 이미 적어 두었고, `require_all` 때문에 오늘은 승격이 어차피 막혀 F6 −4 로 같습니다. 진짜 ARR(kind `actual`)이 들어오면 이 비대칭이 점수를 가를 수 있다는 것도 규칙이 적습니다. **제 판정이 아니라 확인 결과만 남깁니다.**

## 확인 못 한 것

- **nvidia 의 만기 1~5년 AFS 채무증권 5,900 이 대차대조표 어느 줄에 있는지.** companyfacts 2026-07-26 에 비유동 투자 줄 태그가 없고(`Investments` 계열 0건, `OtherAssetsNoncurrent` 15,746 만 있음) 해당 10-Q 원문이 저장소에 보존돼 있지 않아 확인하지 못했습니다. 위 발견의 민감도는 5,900 을 전액 시장성으로 가정한 상한값입니다.
- **oracle `Investments` 24,126 이 대차대조표 줄인지 주석 합계인지.** 같은 이유로 가르지 못했습니다.
- **alibaba `nonop_share` 저장값 0.54 와 재계산 0.6124 의 차이 원인.** 규칙 파일이 `unresolved: 가리지 못했다` 로 적어 둔 그대로이고 저도 가리지 못했습니다. |값| 이 임계 0.30 의 두 배라 어느 값이든 조건이 걸려 점수는 갈리지 않습니다.
- **apple·palantir 의 순현금 실측.** 리스부채가 표준 태그로 잡히지 않아 `net_cash` 가 legacy 값(62,200·9,200) 위에 서 있고, 제 재합산으로 대조할 방법이 없습니다. 엔진이 `unverified_blocked_by` 로 사유까지 드러내고 있어 은폐는 아닙니다.
- **12개사 시총 전부.** `market_cap` 관측 12건이 모두 `legacy_unverified` 이고 저장소에 대조할 주가·주식수 실측이 없습니다. P1·P2 가 그 위에 서지만 규칙대로 점수를 깎지는 않고 `calc.unverified_inputs` 로 표시됩니다.
- **G2 `fcf_trend`(안정/악화) 판단 입력.** alphabet·meta·tesla 의 `deteriorating` 근거가 분기 수치(meta `분기 FCF +$780M로 -91% 급감` 등)인데 이 실행의 관측은 TTM 만 등록돼 있어 재현하지 못했습니다. 승계 판단이라 재계산 대상은 아니지만 대조도 못 했다는 뜻입니다.
- **anthropic 의 F6·F9 판단 자체.** 이해상충 고지에 따라 anthropic 점수에 닿는 판단은 재판정하지 않았습니다. 산술(ps_ratio 30.0 → 밴드 `30x+` −4, 보정 0칸, F6 −4 · G1 보류 → G2 −2)만 대조했고 전부 일치합니다.
