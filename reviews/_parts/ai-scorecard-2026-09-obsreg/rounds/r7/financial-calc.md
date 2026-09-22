# financial-calc — 재무 계산
검토자: Claude Opus 5 (1M) · 독립 리뷰어 세션(NTM-전망치조사 워크트리에서 실행, 쓰기는 이 파일뿐) · 2026-09-16
결과: needs_fix
요약: 14개사 F6 P1~P4 와 F9 G1~G4 를 엔진을 쓰지 않고 규칙 선언(v1.7.json)과 관측값만으로 재계산했고 점수·소계·밴드·경계 플래그·게이트 경로가 한 칸도 어긋나지 않았으며, TTM·복원 Q4·FCF·net_cash·환율 산술도 보존 원자료에서 전부 재현됐다. 다만 net_cash 의 시장성 유가증권 범위가 회사마다 다르게 적용된 곳이 셋이고, FIX-57 이 이번에 등재한 oracle 부외 약정 대안 하나가 XBRL 개념을 잘못 읽었으며, F9 G1 에 기간 기준을 섞을 수 있는 무방비 나눗셈이 남아 있다.

## 재계산 대조표

### F6 — 파라미터·소계·P4·최종 (전 14개사, 엔진값 = 재계산값)

| 기업 | 항목 | 엔진값 | 재계산값 | 일치 | 근거 |
|---|---|---|---|---|---|
| alphabet | P1 / P2 / P3 | 16.8711(0) / 8.9675(−1) / 0.2005(−1) | 동일 | ✅ | `market_cap.v15` 4,120,000M ÷ `net_income_ttm.f6reg28` 244,205M 등 · v1.7.json `policies.f6.parameters` |
| alphabet | 소계·P4·F6 | −2 / nonop 0.5067 hit / −3 | 동일 | ✅ | `results.json` alphabet.F6.calc.p4 · `demotion_sole_cause=nonop_share` |
| amazon | P1 / P2 / P3 | 20.3281(0) / 3.6991(0) / 0.1577(−1) | 동일 | ✅ | `amazon.net_cash.nc37` −119,332M(음수 순현금이 EV 를 키우는 방향) |
| amazon | 소계·P4·F6 | −1 / nonop 0.4659 hit / −2 | 동일 | ✅ | 임계 0.30 대비 +55.3% — 경계 플래그 false |
| meta | P1 / P2 / P3 | 22.1739(0) / 6.7123(0) / 0.2765(−1) | 동일 | ✅ | nonop 0.0068 로 미해당 |
| meta | 소계·F6 | −1 / −1 | 동일 | ✅ | P4 조건 0건 |
| microsoft | P1 / P2 / P3 | 27.5890(−1) / 11.2765(−1) / 0.1779(−1) | 동일 | ✅ | `microsoft.net_cash.nc37` −51,970M |
| microsoft | 소계·F6 | −3 / −3 | 동일 | ✅ | P4 조건 0건 |
| tsmc | P1 / P2 / P3 | 39.7298(−1) / 17.1365(−1) / 0.3161(0) | 동일 | ✅ | NT$ ÷ 31.37 (FY2025 20-F Note 3 선언 환율) |
| tsmc | 소계·P4·F6 | −2 / period_basis_not_ttm / −3 | 동일 | ✅ | `stale_asof` 8개월 < 연간 임계 16개월 → 미해당 |
| alibaba | P1 / P2 / P3 | 17.9788(0) / 1.4836(0) / 0.0274(−3) | 동일 | ✅ | CNY ÷ 6.898 · 당해·전년 같은 환율 |
| alibaba | 소계·P4·F6 | −3 / nonop 0.6124 + period_basis / −4 | 동일 | ✅ | 조건 둘이라 `demotion_sole_cause=null` |
| anthropic | 비상장 P2·보정·F6 | ps 30.0 → −4 / 승격 0 / −4 | 동일 | ✅ | `arr_growth` 0.3830 은 임계 위이나 `kind=run_rate` 로 불인정(FIX-52) · `capital_efficiency` 0.52 만 충족 · `require_all` |
| apple | P1 / P2 / P3 | 36.7641(−1) / 10.0205(−1) / 0.1424(−2) | 동일 | ✅ | P2 는 `apple.net_cash.v15`(legacy) 위에 선다 — `unverified_inputs` 에 표시됨 |
| apple | 소계·F6 | −4 / −4 | 동일 | ✅ | P4 조건 0건 |
| nvidia | P1 / P2 / P3 | 28.1005(−1) / 17.8311(−1) / 0.8338(0) | 동일 | ✅ | nonop 0.1400 미해당 |
| nvidia | 소계·F6 | −2 / −2 | 동일 | ✅ | 시총 5.42T 이 P1·P2 를 악화시키지 않는다(Q04) |
| palantir | P1 / P2 / P3 | 134.9160(−2) / 64.6205(−2) / 0.7892(0) | 동일 | ✅ | net_cash 는 legacy(`palantir.net_cash.v15`) |
| palantir | 소계·F6 | −4 / −4 | 동일 | ✅ | |
| spacex-xai | P2 / P3 | 80.2681(−2) / 0.9194(0) | 동일 | ✅ | P2 가 `revenue_ttm_full.fix56` 23,044M 을 먼저 읽음(`input_alternatives`) |
| spacex-xai | P1 제외 사유 | `would_compute=false`(순이익 −8,218M) | 동일 | ✅ | 적자가 감점이 아니라 미산출로 처리됨(Q11) |
| spacex-xai | 소계·P4·F6 | −2 / period_basis+short_history / −3 | 동일 | ✅ | 세전 −7,623M 이라 nonop 산출 안 함 |
| tesla | P1 / P2 / P3 | 370.6625(−2) / 13.3427(−1) / 0.1175(−2) | 동일 | ✅ | 소계 −5 가 트랙 하한 −7 위라 절단 없음 |
| oracle | P1 / P2 / P3 | 25.9671(−1) / 8.5995(−1) / 0.1735(−1) | 동일 | ✅ | P1 이 임계 25 에서 +3.87% — 허용폭 3% 밖이라 플래그 없음 |
| oracle | P4 nonop | −0.0538 (미해당) | 동일 | ✅ | 채점표 3-1a 각주 ᶜ 의 (19.55−22.39)/19.55 = −0.1448 과 다르나 둘 다 \|값\|<0.30 → 판정 같음 |
| openai | 비상장 P2·보정·F6 | ps 39.0 → −4 / 승격 0 / −4 | 동일 | ✅ | `capital_efficiency` 0.2162 미충족 |
| 전 14개사 | F6 총계 | −3·−2·−1·−3·−3·−4·−4·−4·−2·−4·−3·−5·−3·−4 | 동일 | ✅ | 불일치 0건. 비상장 밴드 라벨만 표기 차이(엔진 `30x+` = 선언 `label`, 정상) |

### F9 — 게이트 경로·런웨이·커버리지 (전 14개사, 엔진값 = 재계산값)

| 기업 | 항목 | 엔진값 | 재계산값 | 일치 | 근거 |
|---|---|---|---|---|---|
| alphabet | G1 영업이익률 → G2 | 0.331104 통과 → FCF +53,273M 악화 −1 | 동일 | ✅ | `alphabet.fcf_ttm.cashfcf35` |
| amazon | G3 런웨이 / G4 커버리지 | 9.9538(step 0) / 1.8557(step 0) → −2 | 동일 | ✅ | 완충 78,213+37,500=115,713M ÷ 소진 11,625M · 496,000M ÷ 267,279M |
| meta | G2 | FCF +40,976M 악화 → −1 | 동일 | ✅ | |
| microsoft | G2 | FCF +66,987M 안정 → 0 | 동일 | ✅ | |
| tsmc | G1 → G2 | 0.508287 → FCF +31,959M 안정 → 0 | 동일 | ✅ | `tsmc.operating_margin_ttm.f6reg28` |
| alibaba | G3 런웨이 | 3.099640, step 0, 경계 +3.3213%(flag false) | 동일 | ✅ | (19,068+3,330)÷7,226 · FIX-57 이 적은 +3.3213% 와 소수 넷째 자리까지 일치 |
| alibaba | G4 → F9 | 미공시 → C-16 downgrade −1 → −3 | 동일 | ✅ | `contracted_revenue.obsreg25` missing_type=not_disclosed_confirmed |
| anthropic | G1·G2 경로 | C-20 판정 보류 → 비상장 미공시 −2 → −2 | 동일 | ✅ | G4 는 C-07 비교 불가로 추가 감점 없음 |
| apple / nvidia / palantir | G2 | FCF +136,683 / +127,006 / +3,358M 안정 → 0 | 동일 | ✅ | |
| spacex-xai | G1 밴드 | −0.161951 → −3 (−30%≤m<−10%) | 동일 | ✅ | 영업이익률이지 순이익률이 아님(Q11) |
| spacex-xai | G3·G4 진단 → 적용 | 3.0258(step 0, 경계 flag **true**) · 1.6044(step 0) · C-05 apply → −3 | 동일 | ✅ | (93,522+4,355)÷32,348 · 경고 문구 출력 확인 |
| tesla | G2 | FCF +5,762M 악화 → −1 | 동일 | ✅ | G3 미도달이라 `undrawn_credit.fix55` 5,000M 은 점수에 안 닿음 |
| oracle | G3 런웨이 / G4 | 1.320991(step −1) / 2.552(step 0) → −3 | 동일 | ✅ | 31,289÷23,686 · 638,000÷250,000 |
| openai | G1 | bep_retreat → −4 (하한, G3·G4 생략) | 동일 | ✅ | `g1_bep_retreat_score` −4 |
| 전 14개사 | F9 총계·상태 | −1·−2·−1·0·0·−3·−2·0·0·0·−3·−1·−3·−4 (전부 ok) | 동일 | ✅ | 불일치 0건 |

### 원자료 검산 (보존 companyfacts·20-F·S-1/A 대조)

| 대상 | 항목 | 엔진값 | 재계산값 | 일치 | 근거 |
|---|---|---|---|---|---|
| TTM 관측 45건 | 태그·기간·접수번호·산술 | 각 관측 `basis.component_accessions.arithmetic.sum` | 보존 companyfacts 에서 성분별 재조회 | ✅ 0건 불일치 | `validation/f6-avail-15/_raw/*.companyfacts.json` |
| 복원 Q4 18건 | FY − 3분기 누계 | 각 `q4_derived.val` | 전부 재현(예: alphabet 132,170−97,715=34,455) | ✅ | 성분이 전부 **한 개념**에서 옴 → 재작성 세대 혼합 없음 |
| MSFT FY2016 | 재작성 세대 반례 | 91,154(ASC606) 대 85,320(ASC605), 9M 64,706 | 전부 재현, 차 5,834(6.84%)·Q4 오차 28.3% | ✅ | `ttm_window.restatement_generation.why` 가 근거로 쓴 사례 |
| 세대 검사 소비자 | 선언→코드 | `rules.f6_q4_restatement_check` | `validation/f6-spec-18/collect_ttm.py:199` 에서 호출, 테스트 6건 | ✅ | 선언만 있고 안 읽는 상태가 아님 |
| TTM 창 끝점 | `anchor` 준수 | 12개사 창 종료일 | 보존 원자료에 **더 늦은 매출 사실 0건** | ✅ | oracle 2026-05-31(FY)이 최신 태깅 분기 2026-02-28 보다 뒤 — 규약대로 |
| FCF 10건 | OCF − CapEx | `fcf_ttm.cashfcf35` | 성분 전부 재현 | ✅ | amazon 은 `PaymentsToAcquireProductiveAssets` 사용(경쟁 태그 0건 확인) |
| spacex FCF | S-1/A 성분 | OCF FY2025 6,785 · CapEx FY2025 20,737 | 보존 S-1/A 연결현금흐름표에서 확인 | ✅ | 20,737 은 `Purchases of property, plant, and equipment` 본문 줄 — 별도 표가 아님 |
| net_cash 10건 | 현금+증권−차입−리스 | alphabet 121,683 … oracle −135,538 | 전 성분을 태그로 대조, 합계 전부 재현 | ✅ | alibaba 625,509−281,722=343,787 RMB백만 ÷6.898 · spacex 100,009−39,708 |
| 환율 | 선언 환율·동일 환율 원칙 | alibaba 6.898 · tsmc 31.37 | 상대오차 10⁻¹² 수준으로 재현 | ✅ | 20-F 공시 USD 와 교차 검산됨 |
| 환율 민감도 | tsmc P2 대체 환율 | 31.37→17.1365 · 32.79→17.9380, 둘 다 −1 | 17.938025 재현 | ✅ | FIX-57 이 갱신한 인용값이 맞음 |
| oracle RPO | 638,000M | `contracted_revenue.fix57` verified | 10-K 0001193125-26-277521 `RevenueRemainingPerformanceObligation` 2026-05-31 | ✅ | 시계열 455,300→523,300→552,600→638,000 도 일치 |
| oracle 부외 250,000M | 대응 사실 존재 여부 | 「없음」 주장 | 230~270B 구간 USD 사실은 `Assets`·`LiabilitiesAndStockholdersEquity` 261,759 둘뿐 | ✅ 주장 확인 | 리스·약정 계열에 250,000M 없음 |
| amazon G4 분모 | 267,279M | 미개시 리스 137,214 + 무조건 구매 130,065 | 보존 10-Q Commitments 표에서 전부 확인(총계 650,034) | ✅ | 나머지 행(장기차입·개시 리스·금융약정)은 전부 재무상태표 계상분이라 제외가 옳음 |
| 미인출 여신 태그 | FIX-55 주사 완전성 | tesla 하나만 기준일 값 존재 | 12개 파일 재주사 — tesla 5,000M 외 0건, oracle 0건 | ✅ | oracle 민감도 「약 39,770M 이상 필요」도 39,769M 로 재현 |
| 단위·부호 | 전수 | — | 단위 위반 0 · 부호 위반 0 · 자릿수 이상 0 | ✅ | 음수 22건 전부 순차입·현금소진·적자로 의미가 맞음 |
| results_hash | frontmatter 기준 | `e075d236…` | `sha256_obj` 재계산 일치 | ✅ | 파일 바이트 해시와 섞지 않음 |
| 총점·순위 | 14개사 | results.total = factor 합 = worker 보고 | 전부 일치 | ✅ | 미산출 factor 0건 |

## 체크리스트

| ID | 결과 | 근거(파일:행) |
|---|---|---|
| Q04 | pass | 시총은 **비율의 분자로만** 쓰인다 — `scorecard/rules/v1.7.json` `policies.f6.parameters.P1.formula`(`market_cap / net_income_ttm`)·`P2.formula`(`(market_cap - net_cash) / revenue_ttm`). 시총 수준을 읽는 factor 는 없다. 실행 증거: apple 시총 4.74T 인데 P1 −1, alphabet 4.12T 인데 P1 0 — 큰 쪽이 더 좋은 점수다(`results.json` apple/alphabet F6.calc.parameters.P1). 가장 작은 palantir(407B)가 P1 −2·P2 −2 로 가장 나쁘다. 주가·EPS·ADR 비율을 쓰는 per_band 경로는 `scripts/scorecard/calc_f6.py:273` 의 분기에서 실행되지 않는다(`f6_mode == parameters`). |
| Q06 | pass | 내 영역의 점수 경로 입력은 전부 금액 또는 비율이고 물량 대리지표가 없다(`observations.json` 의 F6·F9 소비 지표 전수 확인). 볼륨이 값으로 새어 들어올 유일한 자리인 비상장 P2 가 ARR 런레이트가 아니라 `ps_ratio`(밸류÷TTM 보정 매출)를 읽고, 근거를 `policies.f6.private_bands.input_note` 가 적는다 — v1.5 원본 `AI기업_채점규칙_v1.5.md` 645~654행("ARR은 특정 시점 월매출 × 12(런레이트)… 보정 없이 비교하면 비상장사가 부당하게 싸 보인다")에서 직접 확인했다. 나아가 `private_correction.conditions.arr_growth.accepted_kinds:["actual"]`(FIX-52)이 런레이트를 **능동적으로 기각**하며, 두 비상장사 결과에 `input_kinds: run_rate` 와 불인정 사유가 남아 있다. |
| Q10 | pass | 거리와 가속도가 갈려 있다. P3 은 증가율(`revenue_ttm / revenue_ttm_prior - 1`), G3 은 연수라는 거리(`(cash+undrawn)/burn`, `scripts/scorecard/calc_f9.py:38`), G4 는 **누적 대 누적**(계약 잔량 ÷ 약정 잔량)이라 잔량을 유량에 대는 자리가 없다. 비상장 보정은 증가율(arr_growth)과 수준비(capital_efficiency)를 **둘 다** 요구하고 이유를 `private_correction.why_require_all` 이 적는다. 기간 축 비대칭도 아는 범위에서 기록돼 있다 — `amazon.contracted_revenue.obsreg25` 는 가중평균 잔여 6.4년, `amazon.offbalance_B.obsreg25.scope` 는 Thereafter 포함으로 분모 과대 방향임을 명시한다. (oracle 쪽 잔여 기간은 확인 못 함 — 아래 참조.) |
| Q11 | pass | 순적자가 실격 사유로 쓰이지 않는다. F9 G1 은 **영업**이익률로 판정하고(`calc_f9.py` G1 절, spacex-xai −0.161951 → 밴드 −3), F6 P1 은 `requires_positive: net_income_ttm` 에 걸리면 나쁜 밴드를 주는 대신 **산출하지 않는다** — spacex-xai 순이익 −8,218M 이 `results.json` spacex-xai.F6.calc.parameters_not_in_track.P1.would_compute=false 로 남는다. P4 `nonop_share` 도 세전이익이 음수면 조건을 걸지 않고 산출을 포기한다(`calc_f6_params._nonop_share`, FIX-53 3단계). openai −4 는 순적자가 아니라 `bep_retreat`(영업 BEP 후퇴)에서 나오고 그 −4 는 F9 하한이지 탈락이 아니다. 적자 기업이 순위에서 빠진 경우도 없다(`results.json` population.scored=14, incomplete=[]). |

## 발견 사항

- [severity: medium] `observations.json` `oracle.offbalance_B.v15` · `basis.disclosed_alternatives[1]` — `us-gaap:LesseeOperatingLeaseLiabilityUndiscountedExcessAmount` 11,677M 을 「**미개시** 리스 약정. B종(미개시 약정)의 성격에 가장 가깝다」고 적었으나 이 개념은 **미개시 약정이 아니라 이미 인식된 운용리스부채의 내재이자(할인차금)** 다. 보존 ORCL companyfacts 에서 `LesseeOperatingLeaseLiabilityPaymentsDue` 41,867 − `OperatingLeaseLiability` 30,190 = **11,677 로 정확히 일치**하고, 금융리스 쪽도 11,460 − 7,701 = 3,759(`FinanceLeaseLiabilityUndiscountedExcessAmount`)로 같은 구조다. 세 대안의 합 66,853M 을 나중에 C-26 에서 B종 값으로 채택하면 **같은 basis 가 41,867 에 대해 경고한 이중 계상**(「개시분이라 이미 FCF·대차대조표에 있고」)을 11,677 에서 똑같이 저지르게 된다. 보존 companyfacts 에 `…NotYetCommenced` 계열 태그는 0건이라 oracle 의 미개시 리스는 XBRL 로는 복원되지 않는다. **오늘 점수는 안 갈린다** — 250,000 이든 66,853 이든 66,853−11,677=55,176 이든 커버리지가 1 을 넘어 G4 step 0 이다. 이 블록은 FIX-57 이 `recorded_at: 2026-09-16` 으로 이번 라운드에 새로 넣은 것이다.
- [severity: medium] `observations.json` `nvidia.net_cash.nc37` · `meta.net_cash.nc37` · `oracle.net_cash.nc37` · `components` — **상장 지분증권이 포함 목록에도 제외 목록에도 없다.** 규칙 `policies.f6.net_cash.securities_scope.include` 는 「상장 지분증권」을 명시적으로 **포함** 대상으로 적고, alibaba 는 실제로 `Listed equity securities 100,594` 를 시장성으로 넣었다. 그런데 보존 companyfacts 의 `us-gaap:EquitySecuritiesFvNi`(공정가치 변동을 손익으로 인식하는 **시장가 확인 가능한** 지분증권)가 nvidia 42,783M(2026-07-26)·meta 3,543M(2026-06-30) 으로 있고, oracle 은 혼합 개념 `EquitySecuritiesFvNiAndWithoutReadilyDeterminableFairValue` 2,300M(2026-05-31)이 있는데 세 관측 모두 `cash_and_marketable_securities_concepts` 와 `excluded_nonmarketable_present` 어느 쪽에도 이 개념을 적지 않았다. 「포함·제외 어느 목록에도 없었다」는 것은 5차 리뷰가 spacex-xai 암호자산에서 잡아 FIX-56 이 고친 것과 **같은 유형**이고, 같은 기준이 다른 회사에 안 닿은 상태다. **밴드는 안 갈린다** — 전액을 넣으면 nvidia P2 17.8311→17.6898(둘 다 −1), meta 6.7123→6.6968(둘 다 0), oracle 8.5995→8.5654(둘 다 −1)로 셋 다 같은 구간이다. 제외가 맞다면 (혼합 줄이라서인지, 대차대조표 줄이 아니라서인지) 사유를 적어야 하고, 포함이 맞다면 값을 고쳐야 한다.
- [severity: medium] `scripts/scorecard/calc_f9.py` G1 절(영업이익률 대체 산출) — `operating_income_ttm` 을 `revenue_ttm` 으로 나누면서 **두 관측의 `basis.period_basis` 를 확인하지 않고 `revenue_ttm_full` 대체 지표도 읽지 않는다.** spacex-xai 는 바로 이 회사에서 두 지표의 창이 다르다 — `operating_income_ttm.f6reg28` 은 12개월(2025-07-01~2026-06-30) −3,732M 인데 `revenue_ttm.f6reg28` 은 **한 분기**(2026-04-01~2026-06-30) 7,814M 이다. 오늘은 `operating_margin_ttm.f6reg28` −0.161951 이 등록돼 있어 대체 경로가 타지 않지만, 그 관측이 빠지면 엔진이 −3,732÷7,814 = **−0.4776** 을 만들어 G1 밴드가 −3 에서 −4 로 내려가고 F9 −3→−4, 총점 9→8 이 된다. FIX-56 이 F6 P2 에 대해 「지표 이름 하나에 두 뜻을 담지 않는다」며 `input_alternatives` 로 고친 바로 그 문제인데 F9 쪽은 손대지 않았다. `revenue_ttm_full` 의 소비자는 현재 `policies.f6.parameters.P2.input_alternatives` 하나뿐이다(저장소 전수 확인).
- [severity: low] `scorecard/rules/v1.7.json` `policies.f6.p4.conditions[nonop_share].stored_vs_recomputed.which_is_used` — 현재형으로 「원자료(`net_income_ttm`·`operating_income_ttm`)에서 다시 계산할 수 있고 … 두 값이 **0.01** 넘게 다르면 경고를 남긴다(`calc_f6_params._nonop_share`)」고 적지만, 그 함수는 `pretax_income_ttm` 을 읽고 임계는 **0.02** 다(`scripts/scorecard/calc_f6_params.py:97`). 형제 키 `recomputed_formula` 도 옛 산식 `(net_income_ttm − operating_income_ttm) / net_income_ttm` 그대로라 같은 조건의 `formula` 키(`(pretax_income_ttm - operating_income_ttm) / pretax_income_ttm`)와 정면으로 어긋난다. 같은 블록의 `note` 는 옛 산식을 취소선으로 표시해 뒀는데 이 둘만 남았다.
- [severity: low] 같은 블록의 두 현재형 서술이 이번 실행 결과와 다르다. (1) `where_it_does_decide` 가 「alibaba 와 spacex-xai 도 걸리지만」이라고 하는데 spacex-xai 는 FIX-53 3단계 이후 세전이익이 음수라 **조건에 걸리는 것이 아니라 산출 자체를 안 한다**(`results.json` spacex-xai.F6.calc.p4.nonop_share=null). (2) `remaining_mismatch['spacex-xai'].score_impact` 가 「정정 후 `demotion_sole_cause` 가 `short_history` 가 된다」고 하는데 실제 값은 **null** 이다 — FIX-55 로 `period_basis_not_ttm` 이 관측에서 판정되면서 조건이 둘이 됐기 때문이다(`conditions_hit: ["period_basis_not_ttm","short_history"]`). 점수는 어느 쪽도 안 바뀐다.
- [severity: low] `scorecard/rules/v1.7.json` `policies.f6.revenue_coalesce.priority` 에 **행동을 바꾸는 소비자가 없다.** 실제 수집기 `validation/f6-spec-18/collect_ttm.py:52` 는 같은 네 태그를 `REVENUE_TAGS` 상수로 **따로 적어** 쓰고 규칙을 읽지 않으며, 유일한 테스트(`tests/test_scorecard_f6_v17.py:438`)는 선언 자체만 검사한다. 지금 두 목록이 같아 값이 갈리지는 않지만 규칙의 우선순위를 바꿔도 수집 결과가 안 바뀌고 테스트는 계속 통과한다. 같은 블록의 `record_provenance`·`overlap_check` 는 수집기가 실제로 지킨다(`coalesce`·`overlap_conflicts` 기록 확인).
- [severity: low] 같은 조건 블록 안에서 alibaba 의 재계산 `nonop_share` 가 세 값으로 나온다 — `table` 0.5159(옛 산식), `hypothesis_test.unmatched_B` 0.6247, `remaining_mismatch` 0.6124. 엔진이 내는 값은 0.6124150 이다. `table` 열 이름이 「재계산값」이라 현행 산식 결과로 읽히기 쉽다(실제로는 정정 전 값들의 기록이다). 세 값 모두 \|값\|≥0.30 이라 판정은 같다.
- [severity: low] `observations.json` `spacex-xai.net_cash.nc37.components` — 합계는 맞지만 분해 라벨이 틀렸다. `debt_ex_lease: 39,364` 는 `LongTermDebtAndCapitalLeaseObligationsIncludingCurrentMaturities` 라 금융리스 1,079 를 **이미 포함**하고(39,364 − `LongTermDebt` 38,285 = 1,079 확인), `lease_total: 344` 는 운용리스 유동분만이다. 따라서 이름과 달리 「차입금(리스 제외)」도 「리스 합계」도 아니다. 합 39,708 과 최종 60,301 은 정확하다.
- [severity: low] `scripts/scorecard/calc_f9.py` 진단 경로 — G1 실패 뒤의 G3 기록에는 본경로에 있는 `buffer`·`annual_burn` 이 없고, G4 기록은 `step` 을 떼고 저장한다(`{k: v for k, v in g4.items() if k != "step"}`). spacex-xai 처럼 C-05 `apply` 로 진단값이 실제 점수가 되는 회사에서 **각 게이트가 몇 칸을 냈는지 경로만 보고는 읽을 수 없다**(G1-after 의 최종 점수에서 역산해야 한다). 점수는 맞다.

## 확인 못 한 것

- **점수 경로 시총 12건이 전부 `legacy_unverified`** 라 검증할 방법이 이 트리 안에 없다. `alibaba.market_cap.v15` 270,000M 이 ADS 만인지 홍콩 상장분을 합친 전체인지, `tsmc.market_cap.v15` 2,150,000M 이 TWSE+ADR 전체인지 `basis` 가 비어 있어(전부 null) 가릴 수 없다. ADR 두 회사에서 이 구분이 틀리면 P1·P2 가 통째로 움직인다. FIX-57 이 이 사실을 기록한 것은 확인했고, 값 자체의 검증은 못 했다.
- **oracle 계약 수입 638,000M 의 잔여 인식 기간.** amazon 은 가중평균 6.4년이 문면에 있어 분모(Thereafter 포함)와의 축 비대칭 방향을 적을 수 있었는데, oracle 은 보존 companyfacts 에 `RevenueRemainingPerformanceObligationExpectedTimingOfSatisfaction…` 계열 사실이 0건이고 10-K 본문이 보존돼 있지 않아 잔여 기간을 알 수 없다. 분모 쪽 legacy 서술은 「리스 $250B(**15~20년**)」이므로 두 축의 기간이 맞는지 판정 불가다. `coverage_comparable=yes`(`oracle.F9` 판단 입력)의 근거를 재확인하지 못했다.
- **oracle `Investments` 24,126M(2026-05-31) 의 성격.** net_cash 는 시장성 증권으로 `AvailableForSaleSecuritiesDebtSecuritiesCurrent` 605M 만 세는데 companyfacts 에 이 값이 따로 있다(`InvestmentsFairValueDisclosure` 24,162M 과 짝). 대차대조표 줄인지 공정가치 주석 합계인지 원문이 보존되지 않아 가리지 못했다. 시장성 대차대조표 줄이라면 net_cash 가 24,126M 만큼 과소이나, 그 경우에도 P2 는 8.5995→8.2413 으로 같은 −1 밴드다(임계 8 대비 +3.017%, 허용폭 3% 를 아슬아슬하게 넘어 경계 표시도 안 붙는다).
- **apple·palantir 의 `net_cash` 실측.** 둘 다 `lease_liabilities` 미확보로 legacy 값 위에 P2 가 선다(`unverified_blocked_by` 에 사유 기록됨). 보존 companyfacts 로 리스 태그를 대신 세워 보지 않았다 — 결측 사유가 「표준 태그 결측, 10-Q 전문 필요」로 적혀 있어 이 트리 자료로는 같은 벽에 막힌다고 판단했다.
- **spacex-xai 비유동 운용리스.** 관측이 스스로 「부분 합이라 순현금이 과대」라고 적고 크기를 모른다고 한다. 보존 10-Q 에 `OperatingLeaseLiabilityNoncurrent` 가 없는 것은 확인했고(같은 기준일 태그 0건), 크기는 나도 못 구했다. 밴드가 갈리려면 순현금이 1,449,120M 이상이어야 해 실질 위험은 없다는 관측의 판단에는 동의한다.
- **Anthropic 점수에 닿는 재판정은 하지 않았다.** anthropic F6 −4·F9 −2 는 규칙 선언대로 재계산해 엔진과 일치함을 확인했을 뿐이고, `arr` 의 kind 처리(FIX-52 사용자 결정)나 C-20 경로의 타당성은 판정하지 않았다.
