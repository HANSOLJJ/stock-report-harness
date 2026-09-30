# financial-calc — 재무 계산
검토자: Claude Opus 5 (`claude-opus-5[1m]`) · NTM-전망치조사 워크트리에서 연 독립 리뷰 세션(이 실행을 만든 세션 아님) · 2026-09-17 · 기준 커밋 `96afd80` · 9차 판정을 낸 것과 같은 세션의 재판정
결과: needs_fix
요약: **Q11 은 pass 로 바뀐다.** 근거 둘이 실제로 닫혔다 — C-28 로 순손실 상장사가 P2·P3 로 채점되는 것을 합성 관측으로 재현했고(가드 둘도 그대로), C-29 로 openai 가 anthropic 과 같은 C-20 경로를 타 전망으로 하한을 받는 자리가 사라졌다. 재계산도 14개사 전부 불일치 0 이고 새 `results_hash`·`draft_hash` 를 직접 계산해 맞췄다. **영역은 그래도 needs_fix 다** — FIX-61·FIX-62 가 9차 지적을 고치면서 규칙 파일에 **새 모순 둘**을 남겼다. 하나는 C-06 `summary` 가 뒤집힌 우선순위를 그대로 반대로 적고 **빌드된 HTML 방법 표에 그 문장이 실린다**. 다른 하나는 `also_precedes_loss_band` 의 `순서가 관측되지 않는다` 가 **사실이 아니고**, 그 주장을 테스트가 함께 굳혀 놓았다. 둘 다 점수에 닿지 않는다.

## 재계산 대조표

엔진을 호출하지 않고 `observations.json`·`judgments.json`·`v1.7.json`·`run.json` 에서 직접 다시 계산했다(스크래치 파이썬, 저장소 미기록). 관측 선택은 `inputs.ObsLookup` 규약을 같은 방식으로 다시 구현했고, F9 는 C-20 탐지·C-16·C-05 분기를 규칙 선언과 실행 선택에서 다시 읽어 태웠다.

**입력이 9차와 같은지 먼저 확인했다.** `8445619 → 96afd80` 에서 `observations.json` 은 363건 그대로이고, **값·`status`·`missing_type` 이 바뀐 관측이 한 건도 없다**(사라진 관측도 없다). 바뀐 것은 `basis` 주석 둘뿐이고 둘 다 9차에서 내가 낸 low 를 받아 적은 것이다. 그래서 9차에 보존 원자료로 세운 검산이 그대로 유효하고, 아래 원자료 절에서 다시 돌려 확인했다.

### F6 — P1~P4 · 14개사 (9차와 동일, 전부 불변)

| 기업 | 항목 | 엔진값 | 재계산값 | 일치 | 근거 |
|---|---|---|---|---|---|
| alphabet | P1/P2/P3 · P4 · F6 | 16.871071→0 / 8.967531→-1 / 0.200504→-1 · ns 0.506705 hit · **-3** | 동일 | ○ | `alphabet.market_cap.v15`·`net_cash.nc37`·`net_income_ttm.f6reg28`·`revenue_ttm(.prior).f6reg28`·`pretax_income_ttm.nonop44`·`operating_income_ttm.f6reg28` |
| amazon | P1/P2/P3 · P4 · F6 | 20.328058→0 / 3.699118→0 / 0.157666→-1 · ns 0.465925 hit · **-2** | 동일 | ○ | `amazon.*.f6reg28` · `amazon.net_cash.nc37` |
| meta | P1/P2/P3 · P4 · F6 | 22.173926→0 / 6.712281→0 / 0.276514→-1 · ns 0.006832 무 · **-1** | 동일 | ○ | `meta.*.f6reg28` · `meta.net_cash.nc37` |
| microsoft | P1/P2/P3 · P4 · F6 | 27.588991→-1 / 11.276462→-1 / 0.177887→-1 · 무 · **-3** | 동일 | ○ | `microsoft.*.f6reg28` · `microsoft.net_cash.nc37` |
| tsmc | P1/P2/P3 · P4 · F6 | 39.729819→-1 / 17.136514→-1 / 0.316050→0 · `period_basis_not_ttm` hit · **-3** | 동일 | ○ | `tsmc.*.f6reg28`(annual · 선언 환율 31.37) · `tsmc.net_cash.nc37` |
| alibaba | P1/P2/P3 · P4 · F6 | 17.978801→0 / 1.483557→0 / 0.027423→-3 · ns 0.612415 + `period_basis_not_ttm` hit · **-4** | 동일 | ○ | `alibaba.*.f6reg28`·`.obsreg25`(annual · 선언 환율 6.898) · `alibaba.net_cash.nc37` |
| anthropic | 비상장 P2 · 보정 · F6 | ps_ratio 30.0→-4 · 보정 0칸 · **-4** | 동일 | ○ | `anthropic.ps_ratio.priv31`(구간 30~39 양 끝 모두 `30x+`) · `arr`·`arr_prior` 둘 다 `kind=run_rate` 라 `arr_growth` 불충족, `require_all` 이라 승격 0 |
| apple | P1/P2/P3 · P4 · F6 | 36.764136→-1 / 10.020500→-1 / 0.142424→-2 · 무 · **-4** | 동일 | ○ | `apple.*.f6reg28` · `apple.net_cash.nc37` |
| nvidia | P1/P2/P3 · P4 · F6 | 28.100519→-1 / 17.689841→-1 / 0.833759→0 · ns 0.140000 무 · **-2** | 동일 | ○ | `nvidia.*.f6reg28` · `nvidia.net_cash.nc37` |
| palantir | P1/P2/P3 · P4 · F6 | 134.915994→-2 / 64.620502→-2 / 0.789212→0 · 무 · **-4** | 동일 | ○ | `palantir.*.f6reg28` · `palantir.net_cash.nc37` |
| spacex-xai | P2/P3 · P4 · F6 | P1 미산출 / 80.268139→-2 / 0.919430→0 · `period_basis_not_ttm`+`short_history` hit · 하한 -3 · **-3** | 동일 | ○ | P2 분모가 `revenue_ttm_full.fix56` 23,044M(`input_alternatives`). 세전 -7,623M 이라 `nonop_share` 는 `incompatible_basis` |
| tesla | P1/P2/P3 · P4 · F6 | 370.662461→-2 / 13.342688→-1 / 0.117547→-2 · 무 · **-5** | 동일 | ○ | `tesla.*.f6reg28` · `tesla.net_cash.nc37` |
| oracle | P1/P2/P3 · P4 · F6 | 25.967109→-1 / 8.599522→-1 / 0.173487→-1 · ns -0.053800 무 · **-3** | 동일 | ○ | `oracle.*.f6reg28` · `oracle.net_cash.nc37` |
| openai | 비상장 P2 · 보정 · F6 | ps_ratio 39.0→-4 · 보정 0칸 · **-4** | 동일 | ○ | `openai.ps_ratio.priv31` · `capital_efficiency` 40,000/185,000=0.216216 < 0.50 |

- **FIX-61 이 P1 을 선택 파라미터로 넓혔는데 12개 상장사의 점수·상태가 한 칸도 안 바뀌었다.** 전부 `net_income_ttm > 0` 이라 `requires_positive` 를 넘고, `parameters_optional_unmet` 이 비어 있다. C-24 분기가 `listed_newly` 의 P2 로만 한정된 것도 확인했다(`calc_f6_params.py:362~370`) — `listed_ttm` 의 P1 을 끄지 않는다.
- **P4 조건 전수.** `period_basis` 는 14개사 모두 `revenue_ttm` 관측의 `basis.period_basis` 와 일치한다. `stale_asof` 는 완결 개월 수를 다시 구현해 대조했고 한 곳도 걸리지 않는다(최대 tsmc 8개월 · 임계 16). `nonop_share` 는 `(세전 − 영업이익) / 세전` 으로 11개사 전부 소수 이하까지 같다.
- **경계 전수.** P1~P3 · P4 · G3 합쳐 58칸을 `boundary_tolerance` 0.03 으로 재계산했고 **불일치 0**, 켜진 것은 `spacex-xai G3 +0.86%` 하나다.

### F9 — G1~G4 · 14개사 (openai 만 변경)

| 기업 | 항목 | 엔진값 | 재계산값 | 일치 | 근거 |
|---|---|---|---|---|---|
| alphabet | G1→G2 | 0.331104 통과 → FCF +53,273M 악화 → **-1** | 동일 | ○ | 147,628/445,866 · `fcf_ttm.cashfcf35` |
| amazon | G1→G2→G3→G4 | 0.120813 → -11,625M → 런웨이 9.953806 step0 → 커버리지 1.855739 step0 → **-2** | 동일 | ○ | 완충 78,213+37,500=115,713 · 496,000/267,279 |
| meta | G1→G2 | 0.380842 → +40,976M 악화 → **-1** | 동일 | ○ | 86,926/228,247 |
| microsoft | G1→G2 | 0.467808 → +66,987M 안정 → **0** | 동일 | ○ | 155,237/331,839 |
| tsmc | G1→G2 | 0.508287(관측) → +31,959.3M 안정 → **0** | 동일 | ○ | `tsmc.operating_margin_ttm.f6reg28` |
| alibaba | G1→G2→G3→G4 | 0.048990(관측) → -7,226M → 런웨이 3.099640 step0 → C-16 확인된 미공시 step-1 → **-3** | 동일 | ○ | 완충 19,068+3,330=22,398 · `contracted_revenue.obsreg25` 가 `not_disclosed_confirmed` |
| anthropic | G1 보류→G2→G3→G4 | C-20 판정 보류 → 비상장 미공시 -2 → G3 생략 → G4 비교 불가·추가 감점 없음 → **-2** | 동일 | ○ | `operating_margin_ttm.priv31`·`fcf_ttm.priv31` 둘 다 `not_disclosed_confirmed` · `coverage_comparable=no` |
| apple | G1→G2 | 0.331730 → +136,683M 안정 → **0** | 동일 | ○ | 154,859/466,823 |
| nvidia | G1→G2 | 0.652140 → +127,006M 안정 → **0** | 동일 | ○ | 197,579/302,970 |
| palantir | G1→G2 | 0.427985 → +3,358.272M 안정 → **0** | 동일 | ○ | 2,634,652/6,155,941(천) |
| spacex-xai | G1 실패→G3→G4 | -0.161951 → 밴드 -3 → 런웨이 3.025751 step0(경계 ⚠️) → 커버리지 1.604388 step0 → C-05 `apply` → **-3** | 동일 | ○ | 완충 93,522+4,355=97,877 · 소진 32,348 · 47,461/29,582 |
| tesla | G1→G2 | 0.042193 → +5,762M 악화 → **-1** | 동일 | ○ | 4,372/103,619 |
| oracle | G1→G2→G3→G4 | 0.305922 → -23,686M → 런웨이 1.320991 step-1 → 커버리지 2.552 step0 → **-3** | 동일 | ○ | 완충 31,289(여신 `not_disclosed`) · 638,000/250,000 |
| **openai** | G1 보류→G2→G3→G4 | **C-20 판정 보류(BEP 후퇴 미적용) → 비상장 미공시 -2 → G3 생략 → G4 비교 불가 → -2** | 동일 | ○ | **9차의 -4 에서 바뀐 유일한 칸.** 경로가 anthropic 과 문자 그대로 같고, 다른 것은 `bep_retreat_not_applied` 기록과 C-29 경고 두 줄뿐이다 |

- **C-20 탐지를 규칙에서 다시 읽어 태웠다.** `company.listed=false` · `run.decisions[C-20].choice == g1_private_undisclosed_route.choice_required` · 영업손익 관측의 `missing_type == not_disclosed_confirmed` 셋을 내가 직접 확인했고, openai·anthropic 둘만 충족한다. 그래서 openai 의 -2 는 `g2_private_not_disclosed` 에서 나오고 BEP 입력은 경로를 가르지 않는다.
- **분기 재배열에 회귀가 없는지 네 경우로 확인했다**(`calc_f9.py:130~152`). ① 비상장·미공시 → C-20(anthropic·openai) ② 비상장 아님·`bep_retreat=no`·`reviewed=profit` → G1 통과 ③ 같은 조건에 `reviewed≠profit` → `pending_data` ④ 비상장 아님·`bep_retreat=yes`·margin 없음 → 예전처럼 -4. 넷 다 FIX-59 때와 같은 결과다. **다만 ①이 `reviewed_sign == "profit"` 보다도 앞으로 옮겨졌다** — 아래 발견 사항에 적는다.
- **런웨이·커버리지 산식·단위·부호** 를 네 곳씩 다시 계산했다. 단위는 전부 USD, `burn = -fcf` 로 양수, 완충에 `net_cash` 가 섞이지 않는다(alphabet `cash` 55,911M 대 `net_cash` 121,683M 이 갈려 있고 G3 는 `cash` 만 읽는다).
- **총점·순위.** 9 factor 합을 14개사 다시 더했고 미산출 factor 는 한 곳도 없다. **openai 4(단독 13위) · oracle 2(단독 14위)** 이고 나머지 12개사는 9차와 같다.

### 원자료 재합산 — 보존 SEC 제출본·20-F (9차 검산 재확인)

| 기업 | 항목 | 등록값 | 원자료 재합산 | 일치 | 근거 |
|---|---|---|---|---|---|
| alphabet | net_cash | 121,683M | 55,911 + 186,563 − (98,165+1,999) − (18,037+2,590) | ○ | `validation/f6-avail-15/_raw/GOOGL.companyfacts.json` 2026-06-30(10-Q `0001652044-26-000071`). `CashCashEquivalentsAndShortTermInvestments` 242,474 가 앞 두 항의 합과 같아 교차 확인된다 |
| nvidia | net_cash | 60,509M | (22,443 + 34,143 + 42,783) − 33,366 − 5,494 | ○ | `NVDA…` 2026-07-26. 시장성 지분증권 42,783 포함 · 비시장성 47,898 제외 · 만기 버킷 41,000 미사용 |
| oracle | net_cash | -135,538M | (31,289+605) − (130,105−564) − (30,190+7,701) | ○ | `ORCL…` 2026-05-31(10-K `0001193125-26-277521`) |
| spacex-xai | net_cash | 60,301M | (93,522 + 6,487) − 38,285 − (1,079+344) | ○ | `SPCX…` 2026-06-30. 제한현금 830 · 암호자산 1,098 · 비시장성 237 제외 확인 |
| tsmc | net_cash | US$69,224.9633M | (3,240,002.8 − 1,068,415.7) NT$백만 ÷ 31.37 | ○ | 관측 `basis.rows` 15줄을 직접 더해 세 소계가 맞는다 |
| alibaba | net_cash | US$49,838.6489M | (625,509.0 − 281,722.0) RMB백만 ÷ 6.898 | ○ | 보존 20-F `3cf9799:validation/offb-24/_raw/baba-20260331.htm` 에서 여섯 줄 직접 확인. 주석 11 분할이 **100,594 + 130,447 + 10,880 + 238,075 = 479,996** 으로 대차대조표 합계와 정확히 맞아 시장성·비시장성 구분에 빠짐도 겹침도 없다 |
| alphabet | 매출·영업이익 TTM | 445,866M · 147,628M | 229,692+402,836−186,662 · 80,466+129,039−61,877 | ○ | 전기 누계 186,662·61,877 이 두 제출본에 같은 값으로 실려 재작성 세대 충돌이 없다 |
| oracle | 세전이익 | 19,554M | 국내 8,693 + 국외 10,861 = 순이익 17,087 + 법인세 2,467 | ○ | 상대오차 0. `nonop_share` -0.053800 = (19,554−20,606)/19,554 |
| oracle | B종 대안 태그 | 할인차금 | 41,867 − 30,190 = **11,677** · 11,460 − 7,701 = **3,759** | ○ | `Excess` 오독 정정이 1차 자료에서 그대로 성립. 남는 B종 후보 `UnrecordedUnconditionalPurchaseObligationBalanceSheetAmount` 13,309M |
| 8개사 | TTM FCF | 각 등록값 | OCF·CapEx 를 각각 누계식으로 복원해 차를 검산 | ○ | 부호 규약(capex 를 양수 유출로 뺌)이 8건 모두 같다 |
| tsmc·alibaba | P3 통화 | 0.316050 · 0.027423 | 현지통화 원값 비로 같은 값 | ○ | 당해·전년을 같은 선언 환율로 환산해 환율이 상쇄된다(`fx.same_rate_for_both_periods`) |
| 12개사 | P1 귀속 범위 | parent_attributable | `net_income_ttm` 12건 전부 선언 일치 | ○ | 규칙 `P1.input_scope` |
| 실행 전체 | results_hash | `bffb6f75…b195ade` | `results_hash` 키를 뺀 정렬 JSON 의 sha256 | ○ | 조율자가 준 값과 같다 |
| 실행 전체 | draft_hash | `ac4b3831…4daae98` | 초안 파일 바이트 sha256 | ○ | 조율자가 준 값과 같다 |

**불일치 건수: 0.** 점수·소계·밴드·경계·게이트 경로·총점·해시 어느 칸도 어긋나지 않는다. 프로젝트 테스트도 직접 돌렸다 — `662 tests OK (skipped=5)`.

## 체크리스트

| ID | 결과 | 근거(파일:행) |
|---|---|---|
| Q04 | pass | 시총이 점수에 들어가는 자리는 비율의 분자뿐이다(`v1.7.json` P1·P2 `formula`, `calc_f6_params.py:280~285`). 규모 자체를 재는 밴드가 F6·F9 어디에도 없고 결과가 그것을 보여 준다 — 표 전체 최대 시총인 nvidia(약 $5.42T)가 F6 -2 로 상위이고, 훨씬 작은 palantir 가 -4 · tesla 가 -5 다. 비상장도 `private_bands.input` 이 `ps_ratio` 라 밸류 절대액이 아니다 |
| Q06 | pass | 관측 단위가 `USD`·`USD/share`·`ratio`·`text`·`years` 넷뿐이고 토큰 수·사용자 수 같은 볼륨 지표가 363건 중 한 건도 없다. P3 는 매출 성장률, G4 는 계약 수입 대 약정으로 둘 다 금액 기준이다. 볼륨과 가치를 가르는 장치도 실제로 문다 — `private_correction.conditions[arr_growth].accepted_kinds:["actual"]` 가 런레이트를 ARR 로 세지 않아 anthropic 0.382979 · openai 0.600000 이 임계를 넘고도 불충족이다 |
| Q10 | pass | 거리(수준)와 가속(변화율)을 쓰는 자리가 갈려 있다. P3 는 `revenue_ttm / revenue_ttm_prior - 1` 로 변화율이고 누적 매출이 아니다. G3 런웨이는 수준을 수준으로, G2 는 `fcf_trend` 로 방향만 받는다. F6·F9 안에서 누적 성과를 성장률 자리에 넣은 곳을 찾지 못했다. 9차에 든 `arr_prior` 기간 미상은 FIX-61 이 `basis.period_unknown_blocks_growth` 로 적었고 여전히 점수에 닿지 않는다 |
| **Q11** | **pass** (9차 fail 에서 바뀜) | **근거 둘이 다 닫혔다.** **(1)** C-28 이 `resolved`(`chosen: optional_parameters_for_all_listed_tracks`, `v1.7.json:1981`)이고 세 트랙이 `optional_parameters: [P1]` · `optional_parameters_causes: {P1:[requires_positive]}` 를 갖는다. **합성 관측으로 직접 재현했다** — tesla 의 `net_income_ttm` 만 음수로 뒤집으면 이제 `score=-3 · status=ok`(P2 -1 + P3 -2)이고 `parameters_optional_unmet.P1.cause=requires_positive` 다. 9차에는 같은 입력이 `score=None · pending_data` 였다. alibaba(`listed_annual`)로도 같게 나온다(-4). **가드 둘도 그대로다**: 순이익 관측이 아예 없으면 여전히 `pending_data`(수집 공백을 조용히 넘기지 않는다), 소유 범위가 어긋나도 여전히 `pending_data`(FC-04). 대조군은 원값 -5·-4 를 정확히 재현했다. **1999년 아마존이 이제 ⑥ 을 받는다.** **(2)** C-29(`v1.7.json:2012`, 사용자 결정 2026-09-17, 앞선 결정 뒤집음)로 openai 가 C-20 경로를 타고 F9 -2 를 받는다. 그 -2 는 `g2_private_not_disclosed` 즉 **공시 여부**에서 나오지 순적자에서 나오지 않고, `bep_retreat: no` 인 anthropic 이 같은 -2 를 받아 **두 비상장사의 처리가 같다.** 전망(BEP 2030 후퇴)으로 가장 깊은 칸을 주던 자리가 사라졌다. **이번 실행에서 순적자 때문에 점수를 못 받거나 실격된 기업이 없다** — 유일한 순손실 상장사 spacex-xai 는 측정된 단위경제로만 채점된다(P2 80.27 · P3 +91.9% · G1 손실률 -16.195% · G3 런웨이 3.03년 · G4 커버리지 1.60). 남는 잠재는 아래 발견 사항에 적었고 TEN-RA6-01 로 등록돼 있다 |

**Q11 을 pass 로 읽는 범위.** 실현된 노출이 없어졌다는 뜻이고 조항이 가리키는 자리가 전부 사라졌다는 뜻은 아니다. 상장사에 `bep_retreat: yes` 가 들어오면 측정된 손실률 밴드를 전망이 덮어쓰는 경로가 남아 있다(아래 medium 둘째). 오늘 그런 회사가 없고, 조항 충돌 자체는 **TEN-RA6-01**(open · `recheck_at 2026-11` · 비 Claude 재판정 확정)로 등록돼 있다.

**이해상충 고지.** openai F9 의 경로를 내가 고른 것이 아니다. 나는 9차에 체크리스트 Q11 을 fail 로 보고 승계 예외가 안 선다고만 적었고 점수는 건드리지 않았다. 이번에도 엔진이 사용자 결정(C-29)을 제대로 수행했는지만 확인했다. 결과가 Anthropic 경쟁사의 총점을 올리는 방향(2 → 4)이라는 점도 판정에 넣지 않았다.

## 발견 사항

- **[severity: medium]** `scorecard/rules/v1.7.json:1570`(decisions C-06 `summary`) — **뒤집힌 우선순위를 그대로 반대로 적는다.** FIX-61 이 이 문장을 `BEP 후퇴가 기록되면 손실률 밴드·**C-20 비상장 경로보다 앞서** g1_bep_retreat_score 를 준다` 로 고쳐 넣었는데, 같은 날 FIX-62 가 그 순서를 뒤집었다(C-29 · `c20_private_route_first`). 규칙 파일이 **스스로 모순된다** — `policies.f9.g1_bep_retreat_precedence.what_is_true_now` 는 `C-20 이 앞선다` 이고 C-06 `summary` 는 그 반대다. FIX-62 가 `precedence` 블록과 `render_common.py` 는 고치면서 이 한 줄을 안 따라갔다. **그리고 이 문자열은 빌드 산출물에 실린다** — `render_html.render_method`(`scripts/scorecard/render_html.py:553`)가 blocking·pending 결정(`C-05`·**`C-06`**·`C-16`)의 `summary` 를 방법 표에 그대로 찍는다. 점수는 한 칸도 닿지 않지만, 최종 HTML 을 읽는 사람이 현재 엔진과 반대인 규칙을 배우게 된다. 9차에 내가 낸 medium 과 같은 계열이 같은 날 되살아난 것이다.
- **[severity: medium]** `scorecard/rules/v1.7.json:1252`(`policies.f9.g1_bep_retreat_precedence.also_precedes_loss_band`) 와 `tests/test_scorecard_fix61.py:81~91` — **`순서가 관측되지 않는다` 는 주장이 사실이 아니다.** 문면은 `g1_bep_retreat_score -4 가 이미 floor 이고 g1_bands_proposed 의 가장 깊은 칸도 -4 라 어느 쪽을 먼저 보든 점수가 -4 다` 라고 적는다. 그러나 `calc_f9.py:166` 의 `if bep_retreat:` 는 **밴드를 아예 보지 않고 단락시킨다** — 손실률이 가장 깊은 칸(-30% 초과)이 아니면 두 순서의 결과가 다르다. **시뮬레이션으로 확인했다**: spacex-xai(상장 · 측정 손실률 -0.161951 · 밴드 -3)에 `bep_retreat` 만 `yes` 로 바꾸면 F9 가 **-3 에서 -4 로 내려간다**(경로 기록도 `band: "proposed_v15_boundaries", score: -3` 에서 `band: "BEP 후퇴 → -4", score: -4` 로 바뀐다). 주장이 성립하는 것은 손실률이 이미 최심 밴드일 때뿐이다. 이 문면의 선언된 목적이 `다음 사람이 이것을 열린 문제로 다시 들지 않게` 하는 것이라 **틀린 닫음은 안 적은 것보다 나쁘다.** 테스트도 같은 오추론을 굳혀 놓았다 — `test_precedence_records_that_the_order_is_unobservable` 은 `g1_bep_retreat_score == 최심 밴드 == floor` 라는 **전제만** 확인하고 `그래서 순서가 관측되지 않는다` 를 주석으로 단다. 두 순서가 실제로 같은 점수를 내는지는 아무 테스트도 대지 않는다. 오늘 상장사 중 `bep_retreat: yes` 가 없어 점수 영향은 0 이다.
- **[severity: low]** `scripts/scorecard/calc_f9.py:130~152` — **FIX-62 의 재배열이 커밋 메시지가 적은 것보다 한 칸 더 갔다.** 메시지와 C-29 `scope.what_changed` 는 `C-20 탐지를 bep_retreat 보다 앞에 둔다` 로만 적는데, 옛 코드는 `reviewed_sign == "profit"` 을 C-20 보다 먼저 봤고 새 코드는 **C-20 을 그것보다도 앞에 둔다.** 비상장·구조적 미공시이면서 `operating_result_reviewed: profit` 인 회사가 옛 코드에서는 G1 통과, 새 코드에서는 C-20 판정 보류로 갈린다. **새 순서가 더 맞다** — C-20 자신이 `단일 분기 영업흑자를 G1 통과 근거로 쓰지 않는다` 고 적고, 그런 회사는 TTM 영업손익이 `not_disclosed_confirmed` 라 `profit` 이라는 부호가 TTM 밖에서 왔을 수밖에 없다. 오늘 해당 회사가 없다(anthropic `unknown` · openai `loss`). **바뀐 것이 옳아도 안 적힌 것은 안 적힌 것이라** 기록만 남긴다.
- **[severity: low]** `plan/ai-scorecard-2026-09-obsreg.md:149` — 계획의 결정 표가 C-06 을 **세 세대 전 문면**으로 적는다(`BEP 후퇴→-5 … 손실률 경계와의 우선순위 명문화만 미결`). -5 는 C-06 재척도 전 값이고 `명문화만 미결` 은 FIX-59·FIX-61·FIX-62 를 거치며 세 번 달라졌다. 이 표는 `render_md.render_plan`(`scripts/scorecard/render_md.py:82`)이 `rules.pending_decisions()` 의 `summary` 로 만드는데, 계획을 다시 만들지 않고 머리말 `rule_hash` 만 손으로 다시 고정해 왔다 — **계획은 현재 규칙 해시 `d60d72aa…`(실제 규칙 해시와 일치 확인)를 주장하면서 옛 규칙 문면을 보여 준다.** 계획 파일 자신이 `rule_hash 는 다시 고정했으나 계획 파일은 따라오지 않았다`(24행)고 적어 알고는 있다.
- **[severity: low]** `reviews/ai-scorecard-2026-09-obsreg.md` frontmatter — `results_hash`·`draft_hash` 가 아직 8차 값(`a5b80e71…`·`1bf14082…`)이고 `reviewers` 네 줄도 8차 기록이다. 지시서가 이 frontmatter 를 검토 기준으로 삼으라고 했으나 **현재 실행(`bffb6f75…`·`ac4b3831…`)과 다르다.** 나는 트리 `96afd80` 의 실제 산출물을 기준으로 검토했고 그 둘은 조율자가 준 값과 같다. 템플릿 재생성이 이 라운드에 남아 있다는 뜻으로만 적는다.

## 확인 못 한 것

- **oracle B종 약정 250,000M 의 출처.** 보존 ORCL companyfacts 2026-05-31 시점 사실 전수에 대응 금액이 없다는 것까지만 확인했다. C-26 으로 등록돼 있고 커버리지 2.552 든 대안 47.937 이든 G4 step 0 이라 오늘 점수는 갈리지 않는다.
- **alibaba `nonop_share` 저장값 0.54 와 재계산 0.612415 의 차.** 규칙이 `가리지 못했다` 로 둔 자리이고 나도 가리지 못했다. 저장값에 `basis` 가 없어 어느 순이익·세전이익인지 복원할 수 없다. 둘 다 임계 0.30 위라 판정은 같다.
- **tsmc 20-F 원문 직접 대조.** `net_cash` 15줄은 관측 `basis.rows` 의 인용문과 US$ 칸 역검산(31.37)으로만 확인했고 `f14a235:validation/tsm-edgar-29/_raw/tsm-20251231.htm` 를 열어 줄마다 맞추지는 않았다. alibaba 는 보존 20-F 를 실제로 열어 여섯 줄을 대조했다.
- **market_cap 12건·ntm_per 12건의 실측.** 전부 `legacy_unverified` 이고 원천 정책 밖 공급사 값이다. 엔진이 `unverified_inputs` 로 표시하고 점수를 깎지 않는 처리는 규칙대로이나, 값 자체를 내가 확인한 것은 아니다.
- **비상장 두 곳의 `ps_ratio` 30.0·39.0.** v1.5 원문의 TTM 보정 추정치를 승계한 값이고 분기 매출 원자료가 없어 보정을 다시 하지 못했다. 구간 양 끝이 같은 밴드에 드는 것과 밴드 적용이 규칙대로인 것만 확인했다.
- **openai `operating_result_reviewed: loss` 의 근거.** C-29 가 `그 근거도 전망이다` 라고 적는데, 이 입력은 이제 경로를 가르지 않으므로(C-20 이 먼저 선다) 더 파지 않았다. 상장사였다면 이 한 칸이 밴드를 정했을 자리다.
