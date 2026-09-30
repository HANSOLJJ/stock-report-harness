# financial-calc — 재무 계산
검토자: Claude Opus 5 (1M context) · Claude Code 독립 세션(NTM-전망치조사 워크트리에서 실행, 읽기는 review-obsreg 절대경로, 쓰기는 이 파일 하나) · 2026-09-16
결과: needs_fix
요약: 14개사 F6 P1~P4 와 F9 G1~G4 를 규칙 JSON 만 보고 관측에서 다시 계산했고 **점수·소계·밴드·P4 조건·게이트 경로가 한 칸도 어긋나지 않았다.** 이번 라운드가 바꾼 spacex-xai P2 = 80.27 도 보존 S-1/A·10-Q 원문에서 성분까지 재현된다. 다만 그 변경이 만든 선언 하나가 결과와 반대로 남아 있고(발견 1), 점수를 가르는 두 자리에 위험 표시가 빠져 있어(발견 2·3) needs_fix 로 낸다. 산술 오류는 찾지 못했다.

## 재계산 대조표

엔진을 쓰지 않고 `observations.json` + `v1.7.json` 만으로 다시 계산한 값이다(스크래치 파이썬, 저장소에 남기지 않음). `results.json` 값과 부동소수 오차 1e-9 안에서 같으면 일치로 적는다.

### F6 — 파라미터·소계·점수

| 기업 | 항목 | 엔진값 | 재계산값 | 일치 | 근거 |
|---|---|---|---|---|---|
| alphabet | P1·P2·P3 / P4 / F6 | 16.8711(0) · 8.9675(-1) · 0.2005(-1) / nonop_share / -3 | 동일 | ✅ | results.json alphabet.F6.calc · 관측 market_cap.v15 · net_cash.nc37 · net_income_ttm.f6reg28 |
| amazon | P1·P2·P3 / P4 / F6 | 20.3281(0) · 3.6991(0) · 0.1577(-1) / nonop_share / -2 | 동일 | ✅ | amazon.F6.calc |
| meta | P1·P2·P3 / P4 / F6 | 22.1739(0) · 6.7123(0) · 0.2765(-1) / 없음 / -1 | 동일 | ✅ | meta.F6.calc |
| microsoft | P1·P2·P3 / P4 / F6 | 27.5890(-1) · 11.2765(-1) · 0.1779(-1) / 없음 / -3 | 동일 | ✅ | microsoft.F6.calc |
| tsmc | P1·P2·P3 / P4 / F6 | 39.7298(-1) · 17.1365(-1) · 0.3161(0) / period_basis_not_ttm / -3 | 동일 | ✅ | tsmc.F6.calc |
| alibaba | P1·P2·P3 / P4 / F6 | 17.9788(0) · 1.4836(0) · 0.0274(-3) / nonop_share·period_basis_not_ttm / -4 | 동일 | ✅ | alibaba.F6.calc |
| apple | P1·P2·P3 / P4 / F6 | 36.7641(-1) · 10.0205(-1) · 0.1424(-2) / 없음 / -4 | 동일 | ✅ | apple.F6.calc |
| nvidia | P1·P2·P3 / P4 / F6 | 28.1005(-1) · 17.8311(-1) · 0.8338(0) / 없음 / -2 | 동일 | ✅ | nvidia.F6.calc |
| palantir | P1·P2·P3 / P4 / F6 | 134.9160(-2) · 64.6205(-2) · 0.7892(0) / 없음 / -4 | 동일 | ✅ | palantir.F6.calc |
| spacex-xai | P2·P3 / P4 / F6 | 80.2681(-2) · 0.9194(0) / period_basis_not_ttm·short_history / -3 | 동일 | ✅ | spacex-xai.F6.calc · revenue_ttm_full.fix56 |
| tesla | P1·P2·P3 / P4 / F6 | 370.6625(-2) · 13.3427(-1) · 0.1175(-2) / 없음 / -5 | 동일 | ✅ | tesla.F6.calc |
| oracle | P1·P2·P3 / P4 / F6 | 25.9671(-1) · 8.5995(-1) · 0.1735(-1) / 없음 / -3 | 동일 | ✅ | oracle.F6.calc |
| anthropic | 비상장 P2 / 보정 / F6 | 30.0(-4) / +0 / -4 | 동일 | ✅ | anthropic.F6.calc.correction — arr_growth 0.3830 이 kind=run_rate 로 불인정, capital_efficiency 0.52 만 충족, require_all 이라 승격 없음 |
| openai | 비상장 P2 / 보정 / F6 | 39.0(-4) / +0 / -4 | 동일 | ✅ | openai.F6.calc.correction — arr_growth 0.60 kind 불인정 · capital_efficiency 0.2162 미달 |

### F6 — 트랙·P4 조건·경계

| 기업 | 항목 | 엔진값 | 재계산값 | 일치 | 근거 |
|---|---|---|---|---|---|
| 12개사 | 트랙 배정 | listed_ttm 9 · listed_annual 2(tsmc·alibaba) · listed_newly 1(spacex-xai) | 동일 | ✅ | `track_id_for` 를 규칙 tracks.select 대로 재현. spacex-xai 는 티커가 아니라 revenue_ttm.basis.period_basis=quarterly_yoy 로 갈린다 |
| 12개사 | stale_asof | 전원 미해당(경과 1~8개월, 임계 ttm/quarterly 6 · annual 16) | 동일 | ✅ | results F6.calc.p4.stale_asof. tsmc 8개월/16 · alibaba 5/16 · 나머지 1~3/6 |
| 11개사 | nonop_share | (세전−영업이익)÷세전 | 동일(최대 상대오차 1.2e-5) | ✅ | 아래 별표 참조 |
| spacex-xai | nonop_share | 산출 안 함(세전 -7,623M 음수) | 동일 | ✅ | `calc_f6_params._nonop_share` 의 pretax<0 분기. `short_history`·`period_basis_not_ttm` 가 이미 걸려 강등은 유지 |
| 12개사 | 밴드 경계 플래그 | 전원 false | 동일 | ✅ | 최근접은 oracle P1 +3.87%(임계 25), amazon P3 +5.11%(0.15), alibaba P1 -28.1% |
| spacex-xai | 하한 절단 | floor_applied 없음(-3 이 바닥과 같음) | 동일 | ✅ | 소계 -2 − P4 1 = -3, floor -3. C-25 미결 등재 확인 |

### F9 — 게이트 경로·점수

| 기업 | 항목 | 엔진값 | 재계산값 | 일치 | 근거 |
|---|---|---|---|---|---|
| alphabet | G1 통과(마진 0.3311 산출) → G2 흑자·추세 악화 | -1 | -1 | ✅ | operating_margin_ttm 관측 없음 → operating_income/revenue 로 산출. judgments alphabet.F9 fcf_trend=deteriorating |
| amazon | G1 통과 → G2 -2 → G3 런웨이 9.9538 step 0 → G4 커버리지 1.8557 step 0 | -2 | -2 | ✅ | (78,213+37,500)/11,625 · 496,000/267,279 |
| meta | G1 통과 → G2 흑자·악화 | -1 | -1 | ✅ | fcf 40,976 |
| microsoft | G1 통과 → G2 흑자·안정 | 0 | 0 | ✅ | fcf 66,987 |
| tsmc | G1 통과(0.5083) → G2 흑자·안정 | 0 | 0 | ✅ | fcf 31,959.3 |
| alibaba | G1 통과(0.04899) → G2 -2 → G3 런웨이 3.0996 step 0 → G4 확인된 미공시 C-16 downgrade -1 | -3 | -3 | ✅ | (19,068+3,330)/7,226 · contracted_revenue missing_type=not_disclosed_confirmed |
| anthropic | G1 판정 보류(C-20) → G2 비상장 미공시 -2 → G3 생략 → G4 비교 불가(추가 감점 없음) | -2 | -2 | ✅ | operating_margin_ttm·fcf_ttm 둘 다 not_disclosed_confirmed · coverage_comparable=no |
| apple | G1 통과 → G2 흑자·안정 | 0 | 0 | ✅ | fcf 136,683 |
| nvidia | G1 통과 → G2 흑자·안정 | 0 | 0 | ✅ | fcf 127,006 |
| palantir | G1 통과 → G2 흑자·안정 | 0 | 0 | ✅ | fcf 3,358.272 |
| spacex-xai | G1 실패(-0.161951 → 밴드 -3) → G3 진단 3.0258 step 0 → G4 진단 1.6044 step 0 → C-05 apply | -3 | -3 | ✅ | (93,522+4,355)/32,348 · 47,461/29,582 |
| tesla | G1 통과 → G2 흑자·악화 | -1 | -1 | ✅ | fcf 5,762. undrawn_credit 5,000 은 G3 가 안 돌아 점수에 닿지 않는다 |
| oracle | G1 통과(0.3059) → G2 -2 → G3 런웨이 1.3210 step -1 → G4 커버리지 2.552 step 0 | -3 | -3 | ✅ | 31,289/23,686 · 638,000/250,000 |
| openai | G1 BEP 후퇴 -4 → 하한이라 G3·G4 생략 | -4 | -4 | ✅ | judgments openai.F9 bep_retreat=yes · policies.f9.g1_bep_retreat_score -4 |

### 1차 자료 대조 (엔진값이 아니라 보존 원문에서 다시 읽음)

| 기업 | 항목 | 관측값 | 원문 | 일치 | 근거 |
|---|---|---|---|---|---|
| 9개 미국사 | revenue_ttm·revenue_ttm_prior·operating_income_ttm·net_income_ttm·pretax_income_ttm | 45건 | companyfacts 성분에서 전건 복원 | ✅ | `validation/f6-avail-15/_raw/*.companyfacts.json`. 직접 단일 12개월 사실이 있는 곳(microsoft·oracle·amazon NI)은 태그 그대로, 없는 곳은 네 분기 합 또는 `당기누계+전기연간−전기누계` 로 재현 |
| oracle | pretax_income_ttm 19,554 | 19,554 | Domestic 8,693 + Foreign 10,861 (accn 0001193125-26-277521) | ✅ | companyfacts `IncomeLossFromContinuingOperationsBeforeIncomeTaxesDomestic/Foreign` 2025-06-01~2026-05-31 |
| oracle | nonop_share 저장값 -0.15 대 엔진 -0.0538 | — | 채점표 3-1a 각주 ᶜ `세전($19.55B)이 영업이익($22.39B)보다 작다` (`AI기업_채점표_v1.5.md` 824행) | ✅ 설명됨 | GAAP 영업이익 20,606 + RestructuringCharges 1,779 = 22,385 ≈ $22.39B 를 companyfacts 에서 확인. 둘 다 \|값\|<0.30 이라 판정 동일 |
| — | nonop_share 산식 자체 | (세전−영업이익)÷세전 | `AI기업_채점표_v1.5.md` 804행 컬럼 설명 `(세전이익 − 영업이익) ÷ 세전이익. 30% 넘으면 TTM 무효` | ✅ | 엔진 산식이 원문 문면과 같다. 교차 확인 3건 — nvidia 각주 ᵃ `영업외 $32B` 대 엔진 229,743−197,579=32,164 · alphabet 89행 `세전 $299B 중 $152B` 대 299,269−147,628=151,641 · amazon 143행 `$81B` 대 175,466−93,712=81,754 |
| spacex-xai | revenue_ttm_full 23,044 | 18,674+12,508−8,138 | S-1/A 감사 손익계산서 F-5 `Revenue … $ 18,674` · 10-Q 태그 12,508·8,138 | ✅ | `3cf9799:validation/offb-24/_raw/spcx_s1a_20260603.htm` · SPCX.companyfacts. **세대 교차 확인** — S-1/A 가 주는 Q1'26 4,694·Q1'25 4,067 이 10-Q 의 반기−분기(12,508−7,814=4,694, 8,138−4,071=4,067)와 정확히 맞는다 |
| spacex-xai | net_cash 60,301 | 100,009 − 39,708 | 현금 93,522 + MarketableSecuritiesCurrent 6,487 − LongTermDebtAndCapitalLeaseObligationsIncludingCurrentMaturities 39,364 − OperatingLeaseLiabilityCurrent 344 | ✅ | SPCX.companyfacts 2026-06-30 전건. 제한현금 210+620·비상장지분 237·암호자산 1,098 제외가 `securities_scope` 와 맞는다 |
| spacex-xai | fcf_ttm -32,348 | OCF 9,900 − capex 42,248 | S-1/A `Net cash provided by operating activities … $ 6,785` · `Purchases of property, plant, and equipment … (20,737)` + 10-Q 반기 | ✅ | 보존 S-1/A 문면에서 직접 읽음 |
| alibaba | net_cash 49,838.6 | (625,509 − 281,722) RMB백만 ÷ 6.898 | 20-F 각 줄 합 재검산 | ✅ | 현금 131,530 + 단기투자 155,310 + 상장주식 100,594 + 기타 자금운용 238,075 = 625,509 · 차입 5행 259,996 + 리스 21,726 = 281,722. 지분법 206,803·비상장 130,447·제한현금 42,038·혼합줄 10,880 제외 |
| alibaba | 손익 5종 | CNY 원값 | 20-F companyfacts — 매출 1,023,670·전년 996,347·NI 103,592·OI 50,150·세전 129,387 | ✅ | accn 0001193125-26-231755. 전년 USD 는 공시 137,300 이 아니라 당해와 같은 6.898 로 환산(144,439.98)해 P3 가 현지통화 성장률 +2.742% 와 같다 |
| alibaba | capex 18,275 | — | 20-F 문면 `RMB126,063 million (US$18,275 million)` | ✅ | `3cf9799:validation/offb-24/_raw/baba-20260331.htm` |
| tsmc | 손익·현금흐름 7종 | NT$ 원값 ÷ 31.37 | 20-F 본문 — 매출 3,809,054 · 전년 2,894,308 · 모회사 귀속 NI 1,697,604 · 영업이익 1,936,091.7 · 세전 2,041,654.7 · OCF 2,274,975.6 · PP&E 취득 1,272,410.5 | ✅ | `f14a235:validation/tsm-edgar-29/_raw/tsm-20251231.htm`. 20-F `Total non-operating income and expenses 105,563.0` ÷ 2,041,654.7 = 0.05170 이 엔진 nonop_share 와 소수 다섯째 자리까지 같다 |
| tsmc | net_cash 69,224.96 | (3,240,002.8 − 1,068,415.7) ÷ 31.37 | 20-F 줄별 합 재검산 | ✅ | 현금 2,767,856.4 + 증권 4줄 471,146.4 = 3,240,002.8 · 차입 3행 1,032,987.7 + 리스 35,428.0 |
| alibaba·spacex-xai | 확정 미인출 여신 3,330 · 4,355 | — | 20-F 주석 21 `amended from US$ 6.5 billion to US$ 3.33 billion` · 10-Q Note 12 한도 5,000 − 신용장 645 | ✅ | 조건(미인출·약정 준수·만기)이 관측 basis 에 인용문으로 있다. spacex-xai 는 신용장 전액을 보수적으로 차감한 하한이고 5,000 이어도 step 0 으로 같다 |
| 14개사 | 총점 합산 | 9 factor 합 = total | 동일 | ✅ | alphabet·amazon·meta 15 · microsoft 14 · tsmc·anthropic 10 · spacex-xai·nvidia 9 · apple 8 · alibaba 7 · palantir 6 · tesla 5 · oracle·openai 2 — worker 보고와 같다 |
| 초안 | ⑥·⑨ 요약행 14×2 | — | 초안 문면 | ✅ | `drafts/ai-scorecard-2026-09-obsreg.md` 68·71·138·141·218·221·277·280·335·338·436·439·512·515·613·616·706·709·773·776·852·855·910·913·978·981·1089·1092행이 전부 results 값과 같다 |

## 체크리스트

| ID | 결과 | 근거(파일:행) |
|---|---|---|
| Q04 | pass | F6 세 파라미터가 전부 비율이고 시총 절대액이 점수 자리에 들어가지 않는다(`scorecard/rules/v1.7.json` policies.f6.parameters). 크기와 점수가 오히려 반대로 간다 — 시총 5.42조 달러인 nvidia 가 -2(P1 28.10·P2 17.83·P3 +83.4%)이고 4,070억 달러인 palantir 가 -4(P1 134.92·P2 64.62)다(`results.json` nvidia.F6.calc·palantir.F6.calc). 이번에 새로 계산한 spacex-xai P2 도 시총 1,910,000 에서 순현금 60,301 을 뺀 EV 를 12개월 매출 23,044 로 나눈 80.27 이지 시총 크기가 아니다(spacex-xai.F6.calc.parameters.P2). F9 도 마찬가지로 규모가 아니라 비율·기간을 본다 — G1 은 손실률, G3 은 런웨이 연수다(`scripts/scorecard/calc_f9.py:30·52`) |
| Q06 | pass | 내 영역 입력이 전부 금액이고 사용량이 아니다. P3 는 매출 증가율이다(policies.f6.parameters.P3.formula). 비상장 P2 는 ARR 이 아니라 TTM 보정 매출로 나눈 `ps_ratio` 를 읽고, 규칙이 그 이유를 `ARR 은 런레이트라 TTM 보다 과대` 로 적는다(policies.f6.private_bands.input_note · private_multiples 4번 항목). FIX-52 가 `arr_growth` 에 `accepted_kinds:["actual"]` 을 걸어 런레이트를 성장 증거로 쓰지 않는다 — anthropic 0.3830 이 임계 0.30 을 넘고도 불충족이다(`results.json` anthropic.F6.calc.correction.conditions.arr_growth). G4 도 계약 수입 금액 ÷ 약정 금액이다(`calc_f9.py:336`) |
| Q10 | pass | 내 영역에서 누적치를 변화율 자리에 쓴 곳을 찾지 못했다. P3 는 두 12개월 창의 비(policies.f6.parameters.P3), G1 은 TTM 손실률(`calc_f9.py:30`), G3 은 완충 ÷ 연 소진율로 차원이 시간(`calc_f9.py:37`)이다. spacex-xai 만 P3 를 분기 전년 동기로 재지만 이것도 1년 간격의 변화율이라 밴드와 단위가 같다(spacex-xai.revenue_ttm.f6reg28.basis.why_not_ttm). 다만 G4 는 기간이 다른 두 누적치의 비율이고 규칙이 기간 정합을 요구하지 않는다 — 아래 발견 사항 3·5 에 적는다. 체크리스트 case 가 가리키는 ③ 후발가속도는 내 담당 밖이고 TEN-RB-Q10·TEN-RC4-04 로 등재돼 있다 |
| Q11 | pass | 순적자가 실격 사유로 쓰이지 않는다. F9 G1 은 영업손실률로 판정하고 순손실을 읽지 않는다 — spacex-xai 는 operating_margin_ttm -16.195% 로 밴드 -3 을 받고 순손실 -8,218M 은 게이트 입력이 아니다(`results.json` spacex-xai.F9.calc.path[0] · `calc_f9.py:88~141`). F6 도 순손실 자체를 깎지 않는다. spacex-xai 는 P1 만 빠지고 그 사유를 `net_income_ttm 이 0 이하 — requires_positive 를 넘지 못한다` 로 따로 적으며(spacex-xai.F6.calc.parameters_not_in_track.P1), P2·P3 로 -3 을 받는다. `would_compute` 칸이 흑자 전환 시 트랙을 다시 볼 신호로 남아 있다. 구조적 한계 한 가지는 발견 사항 7 에 적는다 |

## 발견 사항

- [severity: medium] `observations.json` spacex-xai.market_cap.v15 `basis.on_score_path` — **선언이 이번 실행 결과와 반대다.** 그 칸은 `**점수 경로 밖.** spacex-xai 는 F6 listed_newly 트랙이라 P3 만 읽고 P1·P2 가 이 값을 쓰지 않는다. SRC-TRACE-47 의 점수 경로 11건에 안 들고 이 12번째 건이다` 라고 적는데, 같은 실행의 `results.json` spacex-xai.F6.calc 는 P2 inputs.market_cap = 1,910,000,000,000 을 쓰고 `calc.unverified_inputs` 가 `{"market_cap": ["P2"]}` 로, observation_ids 가 `spacex-xai.market_cap.v15` 로 정반대를 적는다. FIX-56 1단계가 트랙에 P2 를 넣으면서(C-24) 이 문장을 갱신하지 않았다. 값은 맞고 점수도 안 바뀌지만, 이 문장이 SRC-TRACE-47 의 `점수 경로 밖 12번째 건` 이라는 집계 근거이기도 해서 다음 사람이 실측 대상에서 빼기 쉽다. 같은 회사의 다른 문장은 갱신됐다 — net_cash.nc37 `basis.completeness.why_value_kept` 가 `[FIX-56 1단계 갱신] **이제 점수에 닿는다**` 로 고쳐져 있어, 한 관측만 빠진 것이 드러난다.
- [severity: medium] `scripts/scorecard/calc_f9.py:43~50` · `results.json` alibaba.F9.calc.path[2].boundary — **경계 표시 장치를 만들게 한 사례에서 그 장치가 켜지지 않는다.** `_runway_boundary` 의 도입 주석이 `alibaba 런웨이가 미인출 여신 등록으로 3년 임계 바로 위(+3.3%)가 되어 드러났다` 인데, 실제 distance_ratio 가 0.033213 이고 tolerance 가 0.03 이라 `flag: false` 다. 이 한 칸이 alibaba F9 -3 과 -4 를, 총점 7 과 6 을 가른다 — 확정 미인출 여신 3,330M 을 빼면 런웨이가 2.6388년이 되어 G3 step 이 -1 이 된다(alibaba.undrawn_credit.fix53.basis.runway_effect 가 그 수를 직접 적는다). 초안 776행이 `런웨이 3.10년(임계 3년 대비 +3.3%)` 으로 거리 자체는 보여 주므로 정보가 감춰진 것은 아니나, ⚠️ 표식이 붙는 자리와 실제로 아슬아슬한 자리가 어긋난다. 엔진은 선언된 3% 를 정확히 지키고 있으므로 고칠 곳은 코드가 아니라 tolerance 의 근거이거나 주석이다. 이 사안은 `open_tensions` 어디에도 등재돼 있지 않다.
- [severity: medium] `observations.json` oracle.contracted_revenue.v15 · oracle.offbalance_B.v15 — **G4 가 점수를 내는데 두 입력이 모두 `legacy_unverified` 이고 `basis` 가 null 이다.** 커버리지 638,000 ÷ 250,000 = 2.552 로 step 0 이고, 이 값이 oracle F9 -3(총점 2)을 -4(총점 1)와 가른다. 분자는 보존 자료에서 그대로 확인된다 — `validation/f6-avail-15/_raw/ORCL.companyfacts.json` 의 `us-gaap:RevenueRemainingPerformanceObligation` 2026-05-31 = 638,000,000,000(accn 0001193125-26-277521)이라 실측 등록이 가능한데 승계 라벨로 남아 있다. 분모 250,000M(`raw: 리스 $250B(15~20년)`)은 같은 자료의 어느 사실과도 맞지 않는다 — `LesseeOperatingLeaseLiabilityPaymentsDue` 41,867M, `UnrecordedUnconditionalPurchaseObligationBalanceSheetAmount` 13,309M 뿐이고 250,000 에 닿는 태그가 없다. 같은 라운드에서 amazon·spacex-xai·alibaba 의 offbalance_B 는 `미개시 리스 + 무조건 구매약정` 합으로 실측 교체됐는데(amazon.offbalance_B.obsreg25 = 137,214 + 130,065) oracle 만 리스 단독 표기라 **분모 정의도 다르다.** 구매약정이 빠진 분모면 커버리지가 관대한 쪽으로 기운다.
- [severity: low] `scorecard/rules/v1.7.json:771` · `:774` — FX 절이 근거로 드는 TSM P2 수치가 낡았다. 771행은 `TSM P2 는 32.79 로 23.485, 31.37 로 22.468 이고 **둘 다 -2** 다` 라고 적는데 이번 실행 P2 는 **17.1365 이고 밴드는 -1** 이다(`results.json` tsmc.F6.calc.parameters.P2). 옛 값은 FY2024 매출 92,263.55 와 legacy 순현금 77,000 으로 나온다 — (2,150,000 − 77,000) ÷ 92,263.55 = 22.468 로 재현된다. 774행의 `TWD 를 그대로 넣으면 … 23.485 대신 0.716` 도 같은 옛 입력이다. 결론(환율 선택이 밴드를 가르지 않는다)은 현재 값에서도 성립한다 — 31.37 로 17.137, 32.79 로 17.845 이고 둘 다 -1 이다. 고칠 것은 결론이 아니라 인용 숫자다.
- [severity: low] `observations.json` tsmc.revenue_ttm.f6reg28 `basis.band_sensitivity.used.value` = 17.072 가 실제 P2 17.1365 와 다르다. 17.072 는 legacy 순현금 77,000 기준이고(2,150,000 − 77,000) ÷ 121,423.47 = 17.072), 지금 엔진이 쓰는 검증 순현금은 69,224.96 이다. 밴드는 어느 쪽이든 -1 이라 점수에 닿지 않지만, 민감도 기록이 자기 실행의 입력과 다른 입력으로 계산돼 있다.
- [severity: low] `observations.json` spacex-xai.net_cash.nc37 · spacex-xai.market_cap.v15 — **P2 입력의 기준일이 갈리는데 그 사실을 적은 칸이 없다.** 시총은 2026-09-02, 순현금과 12개월 매출은 2026-06-30 이다. alibaba 는 똑같은 어긋남을 `alibaba.market_cap.v15.basis.p2_asof_mismatch` 에 민감도까지 붙여 적어 두었다(증자 $10.2B 반영 시 1.4836 → 1.4149, 밴드 불변). spacex-xai 는 이번 라운드에 P2 가 처음 계산됐는데 대응 기록이 없다. 밴드는 갈리지 않는다 — -1 이 되려면 순현금이 1,910,000 − 20 × 23,044 = 1,449,120M 을 넘어야 한다.
- [severity: low] `scripts/scorecard/calc_f6_params.py:355` · `:405` — 상장 TTM 트랙에서 **순손실이면 F6 이 통째로 `pending_data` 가 된다.** P1 의 `requires_positive` 를 넘지 못한 값이 `missing` 에 들어가고(355행), `missing` 이 하나라도 있으면 P2·P3 를 계산해 놓고도 점수를 만들지 않는다(405행). `listed_newly` 는 `optional_parameters` 로 이 경로를 피하지만 `listed_ttm`·`listed_annual` 에는 같은 장치가 없다. 오늘 해당 기업이 없어 점수를 가르지 않는다. Q11 이 경고하는 자리와 성격이 같아 적어 둔다 — 적자 기업이 낮은 점수를 받는 것이 아니라 아예 점수를 못 받는다.
- [severity: low] `scorecard/rules/v1.7.json` policies.f6.private_correction.conditions[1] — `capital_efficiency` 는 `accepted_kinds` 가 없어 여전히 `kind=run_rate` 인 arr 을 읽는다. 하필 anthropic 이 충족하는 조건이 이것이다(65,000 ÷ 125,000 = 0.52, `results.json` anthropic.F6.calc.correction.conditions.capital_efficiency.met=true). `require_all` 이라 오늘은 `arr_growth` 불충족만으로 승격이 막히지만, 두 조건이 같은 관측을 읽으면서 한쪽만 kind 를 검사한다. 규칙이 `not_changed` 로 사실은 적어 두었다(arr_growth.accepted_kinds_decision.not_changed).
- [severity: low] TTM 복원 방식이 한 실행 안에서 두 갈래다. 대부분은 네 분기 합(`component_accessions.arithmetic.formula: quarter + q4_derived + quarter + quarter`)이고, apple 의 revenue·operating_income·pretax 는 `curr_ytd + prior_fy − prior_ytd` 다(apple.revenue_ttm.f6reg28.basis.component_accessions.items 의 role 이 curr_ytd/prior_fy/prior_ytd). 발행사 자신의 누계와 분기 합이 어긋나는 곳이 있어 두 방식이 최대 $1M 갈린다 — meta.revenue_ttm_prior 는 분기 합 178,805 인데 누계식으로는 89,830 + 164,501 − 75,527 = 178,804 이고(2024 상반기 공시 누계 75,527 과 분기 합 36,455+39,071=75,526 이 다르다), nvidia.net_income_ttm 은 분기 합 192,879 인데 누계식으로는 192,880 이다. 발행사 반올림에서 오는 차이이고 밴드에 닿지 않지만, `policies.f6.ttm_window` 가 어느 쪽을 정본으로 할지 적지 않는다.
- [severity: low] alibaba `nonop_share` 가 환율이 섞인 USD 값 위에서 계산된다. 세전이익은 CNY 129,387 을 6.8980 으로 나눈 값이고, 영업이익은 20-F 공시 USD 7,270(내재 환율 6.8982, alibaba.operating_income_ttm.obsreg25.basis.implied_rate)을 그대로 쓴다. 비율이라 환율이 상쇄돼야 하는 자리인데 두 입력의 환율이 다르다 — 현지통화로는 (129,387 − 50,150) ÷ 129,387 = 0.612403 이고 엔진은 0.6124150 이다. 상대오차 2e-5 라 판정에 닿지 않는다.
- [severity: low] `scorecard/rules/v1.7.json` decisions C-24 `scope.score_impact` 가 `P4 short_history 한 칸` 이라고만 적는데 실제 걸린 조건은 `["period_basis_not_ttm", "short_history"]` 둘이다(`results.json` spacex-xai.F6.calc.p4.conditions_hit). 강등 칸 수는 하나라 점수는 같고, 둘이 걸려 `demotion_sole_cause` 가 null 인 것도 결과에 맞게 적혀 있다. 결정 기록의 문구만 한쪽을 빠뜨렸다.

## 확인 못 한 것

- **market_cap 12건 전부**. `legacy_unverified` 이고 상류가 StockAnalysis 인데 원천 장부에 `not_adopted · legacy_upstream` 으로만 올라 있다. P1 분자와 P2 분자가 전부 이 값 위에 서므로 상장 12개사 ⑥ 점수 전체가 미실측 입력 위에 있다. 저장소와 E: 원본 안에서 대조할 경로가 없다(외부 조회 금지). 결과가 `unverified_inputs` 로 그 사실을 표시하는 것은 확인했다.
- **apple·palantir 의 net_cash**. 검증 관측이 없어 legacy 62,200 · 9,200 이 P2 에 들어간다. 두 회사 다 리스부채가 기준일에 태깅되지 않아 재계산이 막힌다(`calc.unverified_blocked_by.net_cash` = `lease_liabilities = 아직 실측하지 못함`). 내가 companyfacts 에서 다시 합산해도 같은 공백에 걸린다.
- **oracle offbalance_B 250,000M 의 출처**. v1.5 문면 `리스 $250B(15~20년)` 뿐이고 보존 ORCL companyfacts 에 대응 사실이 없다. 미개시 리스 개념이 태깅돼 있지 않아 값이 맞는지, 무조건 구매약정이 빠졌는지 가리지 못했다(발견 3).
- **spacex-xai 운용리스 비유동분**. 기준일에 개념이 없어 net_cash 가 그만큼 과대라는 방향만 알고 크기를 모른다(net_cash.nc37.basis.completeness). 밴드는 어느 값이든 -2 로 같다는 것만 확인했다.
- **alibaba `Debt securities and loan investments` 10,880 RMB백만의 시장성 분해**. 20-F 가 채무증권과 대출을 나누지 않아 통째로 제외한 판단이 맞는지 가리지 못했다. 넣어도 P2 는 1.4836 → 1.4729 로 밴드 0 이 같다(순현금 49,838.65 + 10,880÷6.898 = 51,415.92).
- **G4 `coverage_comparable` 판단 자체**. amazon(가중평균 잔여 6.4년 계약 수입 대 Thereafter 까지의 약정)·oracle·alibaba·spacex-xai 에 대해 `yes`/`no` 를 정한 것은 판단 입력이고 내 재계산 대상이 아니다. 다만 규칙 `g4_coverage_keep: 1.0` 이 기간 정합을 요구하지 않아, 커버리지 1.0 이라는 선이 기간이 다른 두 누적치의 비 위에 선다는 사실은 적어 둔다.
- **Anthropic 점수에 닿는 판단**. 이해상충 지침에 따라 재판정하지 않았다. 재계산만 했고 anthropic F6 -4 · F9 -2 가 규칙대로 산출된다는 것까지만 확인했다.
