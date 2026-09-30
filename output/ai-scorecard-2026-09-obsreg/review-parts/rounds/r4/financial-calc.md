# financial-calc — 재무 계산
검토자: Claude Opus 5 (1M context) · Claude Code 독립 리뷰 세션(조율자·worker 와 다른 세션) · 2026-09-16 · 검토 기준 `results_hash 66493509c00acf01…`(저장값과 재계산 해시 일치 확인) · 트리 HEAD `b7debcd` 이나 `git diff ab5a053 HEAD -- scorecard scripts docs drafts` 가 빈 결과라 기준 커밋 `ab5a053` 과 산출물이 동일함
결과: needs_fix
요약: F6 P1~P4 와 F9 G1~G4 의 값·밴드·경계·소계·하한을 14개사 전부 관측에서 독립 재계산했고 엔진 결과와 한 건도 어긋나지 않았으며, 보존 companyfacts 12건과 보존 20-F·10-Q 원문(TSM·BABA·AMZN·SPCX)으로 TTM 복원·환산·순현금·런웨이 성분까지 1차 자료 대조를 마쳤습니다. 다만 규칙이 선언한 P4 조건 `period_basis_not_ttm` 을 읽는 코드가 없어 spacex-xai 의 `demotion_sole_cause` 가 사실과 다르게 기록되고, alibaba 관측 하나가 같은 실행의 G3 결과와 정반대로 서술되며, 순적자 상장사가 ⑥ 전체를 미산출로 만들어 순위에서 빠지는 경로가 남아 있어 needs_fix 로 판정합니다. 세 건 모두 이번 실행의 점수는 바꾸지 않습니다.

## 재계산 대조표

재계산 방법은 다음과 같습니다. `observations.json` 에서 `ObsLookup` 과 같은 선택 규칙(verified 우선, 그다음 `observed_at` 또는 `as_of` 최신)으로 관측을 고르고, `v1.7.json` 의 밴드·임계·하한만 읽어 파이썬 스크래치로 값을 다시 만든 뒤 `results.json` 과 대조했습니다. 엔진 코드는 산식 확인에만 쓰고 계산에는 쓰지 않았습니다.

### F6 파라미터 모드(상장 12개사)

| 기업 | 항목 | 엔진값 | 재계산값 | 일치 | 근거 |
|---|---|---|---|---|---|
| alphabet | P1·P2·P3 / 소계 / P4 / 점수 | 16.8711·8.9675·0.20050 / -2 / nonop_share / -3 | 동일 | 예 | 관측 alphabet.market_cap.v15 · net_income_ttm.f6reg28 · net_cash.nc37 · revenue_ttm.f6reg28 · revenue_ttm_prior.f6reg28 |
| amazon | P1·P2·P3 / 소계 / P4 / 점수 | 20.3281·3.6991·0.15767 / -1 / nonop_share / -2 | 동일 | 예 | 관측 amazon.\*.f6reg28 · nc37 |
| meta | P1·P2·P3 / 소계 / P4 / 점수 | 22.1739·6.7123·0.27651 / -1 / 없음 / -1 | 동일 | 예 | 관측 meta.\*.f6reg28 · nc37 |
| microsoft | P1·P2·P3 / 소계 / P4 / 점수 | 27.5890·11.2765·0.17789 / -3 / 없음 / -3 | 동일 | 예 | 관측 microsoft.\*.f6reg28 · nc37 |
| tsmc | P1·P2·P3 / 소계 / P4 / 점수 | 39.7298·17.1365·0.31605 / -2 / period_basis_not_ttm / -3 | 동일 | 예 | 관측 tsmc.\*.f6reg28 · nc37, 트랙 `listed_annual` |
| alibaba | P1·P2·P3 / 소계 / P4 / 점수 | 17.9788·1.4836·0.027423 / -3 / nonop_share + period_basis_not_ttm / -4 | 동일 | 예 | 관측 alibaba.\*.f6reg28 · obsreg25 · nc37 |
| apple | P1·P2·P3 / 소계 / P4 / 점수 | 36.7641·10.0205·0.142424 / -4 / 없음 / -4 | 동일 | 예 | net_cash 는 legacy 62,200(apple.net_cash.v15)이고 `calc.unverified_blocked_by` 에 사유가 기록돼 있습니다 |
| nvidia | P1·P2·P3 / 소계 / P4 / 점수 | 28.1005·17.8311·0.83376 / -2 / 없음 / -2 | 동일 | 예 | 관측 nvidia.\*.f6reg28 · nc37 |
| palantir | P1·P2·P3 / 소계 / P4 / 점수 | 134.9160·64.6205·0.78921 / -4 / 없음 / -4 | 동일 | 예 | net_cash 는 legacy 9,200(palantir.net_cash.v15) |
| spacex-xai | P3 / 소계 / P4 / 점수 | 0.91943 / 0 / short_history / -1 | 동일 | 예 | 트랙 `listed_newly` 라 P1·P2 미산출입니다. 발견 1 참조 |
| tesla | P1·P2·P3 / 소계 / P4 / 점수 | 370.6625·13.3427·0.117547 / -5 / 없음 / -5 | 동일 | 예 | 관측 tesla.\*.f6reg28 · nc37 |
| oracle | P1·P2·P3 / 소계 / P4 / 점수 | 25.9671·8.5995·0.173487 / -3 / 없음 / -3 | 동일 | 예 | 관측 oracle.\*.f6reg28 · nc37 |

### F6 경계 표시와 하한

| 기업 | 항목 | 엔진값 | 재계산값 | 일치 | 근거 |
|---|---|---|---|---|---|
| 12개사 전부 | P1·P2·P3 `boundary.flag`·`nearest_boundary`·`distance_ratio` | results.json 기록값 | 동일(상대거리 최소 경계 선택, 12자리 반올림 후 0.03 이하 비교) | 예 | `scripts/scorecard/rules.py:160-170` |
| oracle | P1 경계(가장 아슬아슬한 사례) | flag=false, 25 선 대비 +3.868% | 동일 | 예 | 임계 3% 를 0.868%p 넘어 표시되지 않습니다 |
| amazon | P3 경계 | flag=false, 0.15 선 대비 +5.110% | 동일 | 예 | |
| 12개사 전부 | P4 `nonop_share_boundary` | results.json 기록값 | 동일(`abs(value)` 를 0.30 과 비교) | 예 | `scripts/scorecard/rules.py:175-187` |
| 12개사 전부 | 트랙 하한 절단 | 적용 0건 | 동일(최저 tesla -5 가 하한 -7 위, spacex-xai -1 이 -3 위) | 예 | `scorecard/rules/v1.7.json:673-686` |

### F6 비상장 2개사

| 기업 | 항목 | 엔진값 | 재계산값 | 일치 | 근거 |
|---|---|---|---|---|---|
| anthropic | P2 ps_ratio / 보정 / 점수 | 30.0 → -4 / 승격 0칸 / -4 | 동일 | 예 | anthropic.ps_ratio.priv31 의 구간 30~39 가 양 끝 모두 `30x+` 이고, arr·arr_prior 가 `kind=run_rate` 라 `accepted_kinds:["actual"]` 를 못 넘습니다 |
| openai | P2 ps_ratio / 보정 / 점수 | 39.0 → -4 / 승격 0칸 / -4 | 동일 | 예 | capital_efficiency 0.21622 가 0.50 미만이라 `require_all` 을 못 넘습니다 |

### F9 게이트

| 기업 | 항목 | 엔진값 | 재계산값 | 일치 | 근거 |
|---|---|---|---|---|---|
| alphabet | G1 pass(마진 0.33110) → G2 흑자·악화 | -1 | 동일 | 예 | fcf_ttm 53,273 = OCF 185,675 − CapEx 132,402 |
| meta | G1 pass → G2 흑자·악화 | -1 | 동일 | 예 | fcf_ttm 40,976 |
| tesla | G1 pass(0.042193) → G2 흑자·악화 | -1 | 동일 | 예 | fcf_ttm 5,762 |
| microsoft·apple·nvidia·palantir·tsmc | G1 pass → G2 흑자·안정 | 0 | 동일 | 예 | fcf_ttm 66,987 / 136,683 / 127,006 / 3,358.272 / 31,959.3 |
| amazon | G2 -2 → G3 런웨이 9.9538년(step 0) → G4 커버리지 1.85574(step 0) | -2 | 동일 | 예 | 완충 78,213 + 37,500 = 115,713, 연 소진 11,625 |
| alibaba | G2 -2 → G3 런웨이 3.09964년(step 0) → G4 C-16 강등(step -1) | -3 | 동일 | 예 | 완충 19,068 + 3,330 = 22,398, 연 소진 7,226. 경계 flag=false(+3.321%) |
| oracle | G2 -2 → G3 런웨이 1.32099년(step -1) → G4 커버리지 2.552(step 0) | -3 | 동일 | 예 | 완충 31,289(미인출 여신 0), 연 소진 23,686 |
| spacex-xai | G1 fail 손실률 -0.161951 → 밴드 -3 → G3 3.02575년(step 0, 경계 flag=true) → G4 1.60439(step 0), C-05 apply | -3 | 동일 | 예 | 완충 93,522 + 4,355 = 97,877, 연 소진 32,348 |
| openai | G1 BEP 후퇴 -4 → 하한이라 G3·G4 생략 | -4 | 동일 | 예 | `scripts/scorecard/calc_f9.py:130-156`, 판단 입력 `bep_retreat=yes` |
| anthropic | C-20 판정 보류 → G2 비상장 미공시 -2 → G3 생략 → G4 중복 감점 없음 | -2 | 규칙 `policies.f9.g1_private_undisclosed_route.result` 와 동일 | 예 | 점수 판단은 재판정하지 않고 경로만 대조했습니다 |

### 산식·정의 1차 자료 대조

| 기업 | 항목 | 엔진값 | 재계산값 | 일치 | 근거 |
|---|---|---|---|---|---|
| oracle | nonop_share `(세전−영업이익)/세전` | -0.053800 | -0.053800 = (19,554 − 20,606) / 19,554 | 예 | 세전은 companyfacts 의 Domestic 8,693 + Foreign 10,861(`validation/f6-avail-15/_raw/ORCL.companyfacts.json`, 10-K 0001193125-26-277521). 채점표 3-1a 각주 ᶜ 의 $22.39B 는 GAAP 20,606 + 구조조정비 1,779 = 22,385 로 재현되고, 그 값으로 계산하면 -0.14478 이라 저장값 -0.15 과 맞습니다 |
| alibaba | nonop_share | 0.612415 | 0.612415 = (18,757.176 − 7,270) / 18,757.176 | 예 | 보존 20-F 의 `Income before income tax and share of results of equity method investees 129,387 18,757` 과 `Income from operations 50,150 7,270`(3cf9799:validation/offb-24/_raw/baba-20260331.htm). 저장값 0.54 와의 차이는 규칙에 미해소로 등록돼 있습니다 |
| tsmc | nonop_share | 0.051705 | 0.051705 = 105,563.0 / 2,041,654.7 | 예 | 보존 20-F F-6 의 `Total non-operating income and expenses 105,563.0`·`INCOME BEFORE INCOME TAX 2,041,654.7`·`INCOME FROM OPERATIONS 1,936,091.7`. 분자가 손익계산서의 영업외 합계 줄과 정확히 같습니다 |
| spacex-xai | nonop_share 음수 분모 처리 | 미산출(`incompatible_basis`) | 동일. 세전 -7,623 이 음수라 산출하지 않는 것이 규칙과 일치합니다 | 예 | `scripts/scorecard/calc_f6_params.py:74-82`. P4 는 `short_history` 로 이미 한 칸이라 점수가 바뀌지 않습니다 |
| tsmc | P1 분자의 소유 범위 | 54,115.524386(모회사 귀속) | 동일 | 예 | 보존 20-F F-6 의 `Shareholders of the parent 1,697,604.0 54,115.5`·`Non-controlling interests (2,479.1) (79.0)`·`NET INCOME 1,695,124.9 54,036.5`. 연결 전체가 아니라 모회사 귀속분을 썼습니다 |
| tsmc | FX 환산(당해·전년 동일 환율) | 3,809,054.3 / 31.37 = 121,423.471 과 2,894,307.7 / 31.37 = 92,263.554 | 동일 | 예 | 선언 환율 31.37 을 두 해에 같이 적용해 P3 가 현지통화 성장률 +31.605% 와 일치합니다 |
| alibaba | FX 환산 | 996,347 / 6.898 = 144,439.983 | 동일 | 예 | 당해는 20-F 공시 USD 148,401 을 그대로 쓰고 전년만 6.898 로 환산했습니다. 두 해를 같은 환율로 통일해 계산해도 성장률이 2.74233% 로 같아 밴드가 갈리지 않습니다 |
| tsmc | net_cash | 69,224.963 US$M | 2,171,587.1 / 31.37 = 69,224.963. 성분 합도 일치합니다(현금·유가증권 3,240,002.8, 제외 22,632.0, 차입 1,032,987.7, 리스 35,428.0) | 예 | 보존 20-F 대차대조표의 15개 줄을 전부 문면에서 확인했습니다. 리스 총계는 주석 16 의 `Current portion 3,833.0 / Noncurrent 31,595.0 / 35,428.0` |
| alibaba | net_cash | 49,838.649 US$M | 625,509.0 − 281,722.0 = 343,787.0 이고 6.898 로 나누면 49,838.649 | 예 | 보존 20-F 에서 현금 131,530·단기투자 155,310·상장주식 100,594·기타 자금운용 238,075, 차입 5줄 합계 259,996, 리스 총계 21,726(주석 19)을 확인했습니다. 지분법 206,803·비상장 130,447·제한현금 42,038·혼합 줄 10,880 은 제외돼 있습니다 |
| alphabet·amazon·meta·microsoft·nvidia·oracle·tesla·spacex-xai | net_cash 성분 | results.json 기록값 | 보존 companyfacts 에서 태그별로 전수 일치 | 예 | `validation/f6-avail-15/_raw/*.companyfacts.json`. microsoft 는 합계 태그 `OperatingLeaseLiability 21,925` 와 `FinanceLeaseLiability 66,594` 로 확인했습니다 |
| 상장 9개사 | revenue_ttm·revenue_ttm_prior TTM 복원 | results.json 기록값 | 성분 18건이 전부 companyfacts 에 존재하고 복원 Q4 산술과 합계가 일치 | 예 | 각 관측의 `basis.component_accessions.items` 를 대조했습니다 |
| 상장 9개사 | 재작성 세대 충돌 | 없음 | 없음. 복원에 쓰인 모든 기간에서 `Revenues` 와 `RevenueFromContractWithCustomerExcludingAssessedTax` 가 다른 값을 주는 사례가 0건입니다 | 예 | 세 매출 개념을 기간별로 교차 조회했습니다 |
| 상장 9개사 | operating_income_ttm·pretax_income_ttm 복원 | results.json 기록값 | 전부 일치. 예를 들어 alphabet 세전은 216,165 + 158,826 − 75,722 = 299,269 | 예 | companyfacts 성분 대조 |
| 관측 360건 | 단위·부호 | USD·ratio 선언 | 이상 0건. 금액 지표에 백만·십억 단위 혼입이 없고 양수여야 하는 12개 지표에 음수가 없습니다 | 예 | 전수 점검 |

## 체크리스트

| ID | 결과 | 근거(파일:행) |
|---|---|---|
| Q04 | pass | ⑥ 정본이 `parameters` 모드라 시총이 절대액으로 점수에 들어가는 자리가 없습니다. P1 은 `market_cap / net_income_ttm`, P2 는 `(market_cap − net_cash) / revenue_ttm` 로 둘 다 비율이고 P3 는 시총을 읽지 않습니다(`scorecard/rules/v1.7.json` policies.f6.parameters, `scripts/scorecard/calc_f6_params.py:213-218`). 결과로도 시총 최대인 nvidia($5.42T)가 -2 이고 시총 최소인 alibaba($0.27T)가 -4, tesla($1.41T)가 최저 -5 입니다. 시총 순서와 F6 순서가 같은 쌍 22건 대 역전 쌍 33건으로 단조 관계가 없습니다 |
| Q06 | pass | 비상장 ⑥ 의 분모가 런레이트가 아니라 TTM 보정 매출입니다(`scorecard/rules/v1.7.json` policies.f6.private_bands.input `ps_ratio` 와 input_note). anthropic 을 ARR 로 재면 14.85배지만 등록값은 30배이고 openai 도 21.3배가 아니라 39배입니다(results.json 의 `calc.multiples.post_money_over_arr` 대 `parameters.P2.value`). FIX-52 로 `arr_growth` 가 `accepted_kinds:["actual"]` 을 요구해 런레이트 입력을 거부합니다(`scorecard/rules/v1.7.json:832-847`). F9 G4 도 계약 수입과 B종 약정이라는 두 금액을 나누며, 사용자 수나 토큰량 같은 볼륨 지표는 어느 계산에도 들어가지 않습니다 |
| Q10 | pass | 재무 계산 쪽 지표가 전부 차원이 맞습니다. P3 는 누적 매출이 아니라 증가율이고(`scorecard/rules/v1.7.json` P3.formula), G1 은 적자 절대액이 아니라 손실률이며, G3 는 잔고를 연 소진율로 나눠 연수를 내고(`scripts/scorecard/calc_f9.py:39-59`), G4 는 금액 대 금액입니다. 다만 비상장 보정의 `capital_efficiency = arr / cumulative_raised` 는 연율을 누적 잔고로 나눠 차원이 섞이며 이는 v1.5 정의를 그대로 이어받은 것입니다(발견 7). 이번 실행에서 이 조건이 점수를 만든 기업은 없습니다 |
| Q11 | pass | 순적자를 실격 사유로 쓴 기업이 이번 실행에 없습니다. ⑨ G1 은 순이익이 아니라 TTM 영업손실률로 판정하고(`scripts/scorecard/calc_f9.py:87-97,140`), spacex-xai 는 -16.195% 로 밴드 -3, openai 는 BEP 후퇴 판단으로 -4 입니다. 비상장 미공시는 적자라고 단정하는 대신 C-20 판정 보류 경로로 보냅니다(`scripts/scorecard/calc_f9.py:105-112`). 다만 상장 `listed_ttm` 트랙에 순적자 기업이 들어오면 ⑥ 전체가 미산출이 되어 순위에서 빠지는 경로가 남아 있습니다(발견 3). 이번 실행의 `listed_ttm` 11개사 순이익이 모두 양수라 발동하지 않았습니다 |

## 발견 사항

- [severity: medium] `scorecard/rules/v1.7.json:623-625` · `scripts/scorecard/calc_f6_params.py:161-178` — **P4 조건 `period_basis_not_ttm` 을 관측에서 판정하는 코드가 없습니다.** 규칙은 이 조건을 "기간 단위가 TTM 이 아님(연간 대체 등). 관측 basis.period_basis 로 판정한다" 고 선언하지만 `_p4()` 는 `nonop_share` 와 `stale_asof` 만 관측에서 계산하고 이 조건은 트랙의 `auto_p4_conditions` 목록으로만 붙입니다. `listed_annual` 은 그 목록에 이 조건이 있어 tsmc·alibaba 가 걸리지만(`scorecard/rules/v1.7.json:673-674`), `listed_newly` 는 `short_history` 만 선언해(`scorecard/rules/v1.7.json:684-685`) spacex-xai 가 빠집니다. spacex-xai 의 `revenue_ttm` 관측은 `period_basis: quarterly_yoy` 이고 관측 자신이 "분기값(2026Q2) — TTM 아님" 이라고 적습니다(관측 `spacex-xai.revenue_ttm.f6reg28`). 선언대로라면 조건이 걸려야 합니다. 점수는 바뀌지 않습니다. P4 는 한 칸 상한이고 `short_history` 가 이미 걸려 있기 때문입니다. 그러나 `calc.p4.demotion_sole_cause` 가 `short_history` 로 기록돼(results.json 의 spacex-xai) 조건 하나가 강등을 혼자 정했다고 말하는데, 선언을 따르면 조건이 둘이라 이 칸은 `null` 이어야 합니다. 같은 형태의 결함, 곧 선언은 있는데 읽는 코드가 없는 상태가 `stale_asof` 에서 이미 한 번 잡혀 고쳐졌고(`scripts/scorecard/calc_f6_params.py:112-118`), 규칙 스스로도 `stale_asof.why_not_single_threshold` 에서 이 조건이 관측 기준으로 평가되는 것을 전제합니다(`scorecard/rules/v1.7.json:645`).
- [severity: medium] 관측 `alibaba.fcf_ttm.cashfcf35`(`scorecard/runs/ai-scorecard-2026-09-obsreg/observations.json:10973`) — **같은 실행 안의 두 관측이 alibaba 런웨이를 서로 반대로 적습니다.** `non_gaap_variant.note` 가 "non-GAAP 을 쓰면 런웨이가 2.64년에서 2.82년이 되나 둘 다 3년 미만이라 G3 판정은 갈리지 않는다" 라고 적는데, FIX-53 2단계가 미인출 여신 3,330 을 등록한 뒤의 실제 런웨이는 3.09964년이고 엔진의 G3 step 은 0 입니다(results.json 의 alibaba F9 path). 미인출 여신을 등록한 관측 자신은 "런웨이 (19,068 + 3,330) / 7,226 = 3.0996년(등록 전 2.6388년). G3 step -1 → 0" 이라고 바르게 적습니다(관측 `alibaba.undrawn_credit.fix53`). 즉 fcf 관측의 서술만 갱신되지 않은 채 남아 "3년 미만" 이라는 틀린 사실과 step -1 을 함의하는 근거를 제시합니다. 결론 문장인 "G3 판정은 갈리지 않는다" 는 우연히 여전히 맞습니다. non-GAAP 값으로 계산해도 (19,068 + 3,330) / 6,757 = 3.3147년이라 3년을 넘기 때문이며 이는 제가 직접 계산했습니다. alibaba 는 완충 22,398 을 3으로 나눈 7,466 이 소진율 상한이라 지금의 7,226 에서 3.32% 만 커져도 G3 가 -1 이 되고 총점이 7 에서 6 으로 내려가는 자리입니다. 그 자리의 근거란에 틀린 수치가 남아 있으면 다음 사람이 잘못된 여유를 읽습니다.
- [severity: medium] `scripts/scorecard/calc_f6_params.py:210-212,336-339` · `scripts/scorecard/aggregate.py:12` — **순적자 상장사는 ⑥ 전체가 미산출이 되어 순위에서 빠집니다.** P1 은 `requires_positive: ["net_income_ttm"]` 이라 순이익이 0 이하면 값을 만들지 않고 사유를 `missing` 에 넣습니다. `compute_listed` 는 `missing` 이 하나라도 있으면 P2·P3 를 이미 계산해 놓고도 factor 를 `pending_data`(score `None`)로 돌려주고, `summarize_company` 는 그 기업을 `complete: false` 로 만들어 `rank_companies` 가 공식 순위에서 제외합니다. 트랙은 수익성이 아니라 매출 관측의 `period_basis` 로 정해지므로(`scripts/scorecard/calc_f6_params.py:40-47`) 정상적으로 분기 보고를 하는 순적자 상장사는 `listed_ttm` 에 그대로 남습니다. 이번 실행에서는 `listed_ttm` 11개사 순이익이 모두 양수라 발동하지 않았지만, 구조는 체크리스트 Q11 이 이름 붙인 실패형, 곧 순적자가 실격으로 작동하는 모양과 같습니다. 판정이 아니라 등록으로 적습니다. P1 만 미산출로 두고 P2·P3 로 소계를 낼지, 아니면 별도 트랙을 둘지는 규칙 결정 사항입니다.
- [severity: low] 관측 `oracle.undrawn_credit.fix54`(`scorecard/runs/ai-scorecard-2026-09-obsreg/observations.json:13009`) — **확정 미인출 여신이 점수를 가르는 유일한 기업에만 공백이 남았습니다.** 상장 12개사 중 amazon·alibaba·spacex-xai 셋만 금액이 등록됐고 나머지 아홉은 `missing_type: unverified` 입니다. 잣대 자체는 같습니다. 보존 원문이 있으면 읽고 외부 조회는 금지이기 때문입니다. 다만 oracle 은 FCF 가 음수라 G3 가 점수를 내는 유일한 미등록 기업이고, 관측 스스로 "런웨이 3년(step 0)에 닿으려면 현금 31,289M 에 약 39,770M 이상의 확정 미인출 여신이 더해져야 한다" 고 적습니다. 결측이 어느 방향으로 작용하는지를 관측이 밝혀 둔 점은 적절합니다. 원문이 보존되면 이 한 건을 먼저 채우는 편이 좋겠습니다.
- [severity: low] 관측 `amazon.undrawn_credit.fix54`(`scorecard/runs/ai-scorecard-2026-09-obsreg/observations.json:12832`) — **미인출 여신 37.5B 중 22.5B 이 실행 기준일로부터 4주 안에 소멸하거나 만기가 됩니다.** 보존 10-Q(3cf9799:validation/offb-24/_raw/amzn-20260630.htm) 문면을 직접 확인했습니다. 364일 여신 5.0B 은 2026-10 만기이고 지연인출 약정 17.5B 은 "on or prior to September 30, 2026, after which any undrawn commitments will automatically terminate" 입니다. 실행 기준일은 2026-09-02 입니다. 설계 지침 6.4 는 "조건이 확인된 확정 미인출 여신" 만 요구하고 잔존 기간 요건을 두지 않으므로 규칙 위반은 아니며, 관측이 15·37.5·0 세 경우 모두 step 0 이라는 민감도를 남겼습니다. 그래도 9.95년 런웨이의 분자에 4주 뒤 소멸하는 약정이 들어간다는 사실은 기록해 둘 만합니다. 런웨이 분자에 잔존 기간 요건을 둘지가 미결입니다.
- [severity: low] 관측 `tsmc.pretax_income_ttm.nonop44`(`scorecard/runs/ai-scorecard-2026-09-obsreg/observations.json:12658`) — **`cross_check_ni_plus_tax` 가 등록된 `net_income_ttm` 과 다른 순이익으로 계산됐습니다.** 그 필드의 note 는 "세전 = 순이익 + 법인세" 이고 다른 회사는 등록된 모회사 귀속 순이익으로 계산돼 amazon 은 -0.003248, palantir 는 -0.004566 처럼 어긋남의 크기가 남습니다. tsmc 만 `relative_gap` 이 2.258e-12 인데, 등록값 54,115.524386 으로 계산하면 (54,115.524386 + 11,046.534906 − 65,083.031559) / 65,083.031559 = +0.001214 입니다. 20-F 의 연결 `NET INCOME 54,036.5` 를 쓴 것으로 보이며 그 값이면 정확히 0 이 됩니다. 점수에는 닿지 않습니다. `nonop_share` 가 세전이익과 영업이익만 읽기 때문입니다. 같은 이름의 검산 칸이 회사마다 다른 순이익을 가리키면 교차 확인의 뜻이 흐려집니다.
- [severity: low] `scorecard/rules/v1.7.json:845,849-856` — **비상장 보정의 두 조건이 같은 관측에 다른 잣대를 댑니다.** `arr_growth` 는 `accepted_kinds:["actual"]` 로 `kind=run_rate` 인 arr 을 거부하는데 `capital_efficiency` 는 같은 arr 을 그대로 읽습니다. 규칙이 `not_changed` 에 그 사실과 사유, 곧 사용자 결정 범위가 `arr_growth` 였다는 점을 적어 두었고 `require_all` 이라 지금은 점수가 바뀌지 않습니다. 더해서 `arr / cumulative_raised` 는 연율을 누적 잔고로 나눈 값이라 차원이 섞이며 0.50 이라는 임계도 무차원처럼 다뤄집니다. v1.5 정의 승계이고 이번 실행이 만든 문제는 아닙니다.
- [severity: low] `scorecard/rules/v1.7.json:935` · 관측 `palantir.net_cash.v15` 대 `spacex-xai.net_cash.nc37` — **같은 결함에 두 회사가 다른 처리를 받았습니다.** 기준일에 리스 구성요소 하나가 없다는 같은 사정에서 palantir 는 관측을 등록하지 않아 P2 가 legacy 9,200 위에 서고, spacex-xai 는 부분 합 기준으로 verified 등록됐습니다. 규칙이 `partial_lease_basis` 에 이 사실을 적어 두었습니다. 점수는 바뀌지 않습니다. palantir P2 는 legacy 9,200 이든 규칙이 근거로만 쓴 실측 9,198 이든 64.62 로 같은 `20+` 밴드이고, spacex-xai 는 `listed_newly` 라 P2 를 계산하지 않습니다.
- [severity: low] 관측 `anthropic.undrawn_credit` 과 `openai.undrawn_credit` 의 부재 — **확정 미인출 여신 조사가 14개사 전수가 아니라 12개사입니다.** worker 보고는 "14개사 전수 조사와 등록" 이지만 관측 층에서 확인되는 것은 상장 12개사뿐이고 비상장 둘에는 이 지표의 관측이 아예 없습니다. 두 회사는 C-20 경로라 G3 가 생략되므로 점수에 닿지 않습니다. 다만 다른 미확인 기업에 `missing_type: unverified` 관측을 남긴 것과는 처리가 다릅니다.
- [severity: low] 관측 `oracle.contracted_revenue.v15` 와 `oracle.offbalance_B.v15` — **oracle 의 G4 만 legacy 값 두 개 위에 섭니다.** 638B 와 250B 이 모두 `legacy_unverified` 이고 반올림된 수치인데 `coverage_comparable: yes` 로 커버리지 2.552 가 계산됩니다. amazon·spacex-xai·alibaba 는 같은 게이트를 verified SEC 관측으로 통과합니다. 점수는 안정적입니다. step 이 -1 이 되려면 B종 약정이 638B 를 넘어야 하기 때문입니다.

## 확인 못 한 것

- **market_cap 12건이 전부 `legacy_unverified` 이고 저는 그 상류를 다시 재지 않았습니다.** P1·P2 가 전부 이 값 위에 서지만 v1.5 채점표의 주가와 주식 수 자체를 검증하는 것은 사실·출처 영역입니다. 엔진은 `calc.unverified_inputs` 로 이 사실을 드러내며 점수를 깎지 않습니다. ADR 산술만 확인했습니다. tsmc 는 5.19B ADR 곱하기 $415.50 이 $2,156.4B 인데 $2.15T 로 적었고, alibaba 는 2.42B ADS 곱하기 $111.76 이 $270.5B 인데 $270B 로 적었습니다. 표기 반올림 폭 0.2~0.3% 로는 P1·P2 밴드가 갈리지 않습니다(tsmc P1 39.73 대 39.85, P2 17.14 대 17.19, alibaba P1 17.98 대 18.01).
- **oracle·microsoft·tesla 를 비롯한 아홉 곳의 확정 미인출 여신 실제 금액을 확인하지 못했습니다.** 보존 10-K·10-Q 본문이 이 트리에 없고 외부 조회가 금지입니다. 그중 oracle 한 곳만 점수에 닿습니다(발견 4).
- **spacex-xai 순현금의 비유동 운용리스 금액을 확인하지 못했습니다.** 기준일 2026-06-30 에 `OperatingLeaseLiabilityNoncurrent` 태그가 companyfacts 에 없고 10-Q 가 기타 비유동부채를 나누지 않습니다. 관측이 `completeness` 에 이 한계와 방향, 곧 순현금이 과대라는 점을 적어 두었습니다. `listed_newly` 트랙이라 P2 를 계산하지 않아 점수에는 닿지 않습니다.
- **apple 의 리스부채를 확인하지 못했습니다.** 10-K 에만 태깅되고 기준일 2026-06-27 의 10-Q 에는 없어 net_cash 실측이 성립하지 않으며 P2 는 legacy 62,200 위에 섭니다. 관측 `apple.lease_liabilities.nc37` 과 `calc.unverified_blocked_by` 가 사유를 밝힙니다.
- **`nonop_share` 저장값과 재계산값의 alibaba 차이(0.54 대 0.6124)를 가르지 못했습니다.** 규칙이 미해소로 등록해 두었고 지금은 hit 판정이 양쪽 다 임계 위라 점수가 갈리지 않습니다.
- **anthropic 점수에 닿는 판단은 재판정하지 않았습니다.** F6 -4 와 F9 -2 는 각각 C-12 보정 규칙과 C-20 경로를 그대로 적용한 결과인지만 대조했고 판단 자체의 타당성은 다루지 않았습니다. 이해상충 고지에 따른 것입니다.
- **빌드된 HTML 과 초안의 표시값은 보지 않았습니다.** 출력·가독성 영역이며 저는 `results.json` 까지만 대조했습니다.
