# financial-calc — 재무 계산
검토자: Claude Opus 5 (`claude-opus-5[1m]`) · NTM-전망치조사 워크트리에서 연 독립 리뷰 세션(이 실행을 만든 세션 아님) · 2026-09-17 · 기준 커밋 `8445619`
결과: needs_fix
요약: F6 P1~P4 와 F9 G1~G4 를 14개사 전부 관측값에서 다시 계산했고 **엔진과의 불일치는 0** 이다(밴드·경계 플래그·강등·하한·총점·`results_hash` 포함). 8차 지적 다섯 건은 보존 원자료로 대조해 전부 닫힌 것을 확인했다. 다만 **FIX-59 가 스스로 만든 모순 하나**가 남는다 — `policies.f9.g1_bep_retreat_precedence` 로 우선순위를 확정해 놓고, 그 확정이 아직 안 됐다고 적는 문장 셋이 코드·규칙·초안에 그대로 있다. 점수는 한 칸도 닿지 않지만 초안 문면에 거짓 문장이 실려 나가므로 `pass` 로 올리지 않는다.

## 재계산 대조표

재계산은 엔진을 호출하지 않고 `observations.json`·`judgments.json`·`v1.7.json` 에서 직접 했다(스크래치 파이썬, 저장소 미기록). 관측 선택은 `inputs.ObsLookup` 규약(verified 우선 → `observed_at`/`as_of` 최신)을 같은 방식으로 다시 구현했다.

### F6 — P1~P4 · 14개사

| 기업 | 항목 | 엔진값 | 재계산값 | 일치 | 근거 |
|---|---|---|---|---|---|
| alphabet | P1/P2/P3 · P4 · F6 | 16.871071→0 / 8.967531→-1 / 0.200504→-1 · ns 0.506705 hit · **-3** | 동일 | ○ | `alphabet.market_cap.v15`·`net_cash.nc37`·`net_income_ttm.f6reg28`·`revenue_ttm.f6reg28`·`revenue_ttm_prior.f6reg28`·`pretax_income_ttm.nonop44`·`operating_income_ttm.f6reg28` |
| amazon | P1/P2/P3 · P4 · F6 | 20.328058→0 / 3.699118→0 / 0.157666→-1 · ns 0.465925 hit · **-2** | 동일 | ○ | `amazon.*.f6reg28` · `amazon.net_cash.nc37` |
| meta | P1/P2/P3 · P4 · F6 | 22.173926→0 / 6.712281→0 / 0.276514→-1 · ns 0.006832 무 · **-1** | 동일 | ○ | `meta.*.f6reg28` · `meta.net_cash.nc37` |
| microsoft | P1/P2/P3 · P4 · F6 | 27.588991→-1 / 11.276462→-1 / 0.177887→-1 · 무 · **-3** | 동일 | ○ | `microsoft.*.f6reg28` · `microsoft.net_cash.nc37` |
| tsmc | P1/P2/P3 · P4 · F6 | 39.729819→-1 / 17.136514→-1 / 0.316050→0 · `period_basis_not_ttm` hit · **-3** | 동일 | ○ | `tsmc.*.f6reg28`(annual·FX 31.37) · `tsmc.net_cash.nc37` |
| alibaba | P1/P2/P3 · P4 · F6 | 17.978801→0 / 1.483557→0 / 0.027423→-3 · ns 0.612415 + `period_basis_not_ttm` hit · **-4** | 동일 | ○ | `alibaba.*.f6reg28`·`.obsreg25`(annual·FX 6.898) · `alibaba.net_cash.nc37` |
| anthropic | 비상장 P2 · 보정 · F6 | ps_ratio 30.0→-4 · 보정 0칸 · **-4** | 동일 | ○ | `anthropic.ps_ratio.priv31`(구간 30~39 양 끝 모두 `30x+`) · `arr.v15`·`arr_prior.priv31` 둘 다 `kind=run_rate` 라 `arr_growth` 불충족(`accepted_kinds:["actual"]`), `require_all` 이라 승격 0 |
| apple | P1/P2/P3 · P4 · F6 | 36.764136→-1 / 10.020500→-1 / 0.142424→-2 · 무 · **-4** | 동일 | ○ | `apple.*.f6reg28` · `apple.net_cash.nc37` |
| nvidia | P1/P2/P3 · P4 · F6 | 28.100519→-1 / 17.689841→-1 / 0.833759→0 · ns 0.140000 무 · **-2** | 동일 | ○ | `nvidia.*.f6reg28` · `nvidia.net_cash.nc37` |
| palantir | P1/P2/P3 · P4 · F6 | 134.915994→-2 / 64.620502→-2 / 0.789212→0 · 무 · **-4** | 동일 | ○ | `palantir.*.f6reg28` · `palantir.net_cash.nc37` |
| spacex-xai | P2/P3 · P4 · F6 | P1 미산출 / 80.268139→-2 / 0.919430→0 · `period_basis_not_ttm`+`short_history` hit · 하한 -3 · **-3** | 동일 | ○ | P2 분모가 `revenue_ttm_full.fix56` 23,044M 인 것 확인(`input_alternatives`). P1 은 트랙 외이고 `parameters_not_in_track.P1.would_compute=false`(순이익 -8,218M) |
| tesla | P1/P2/P3 · P4 · F6 | 370.662461→-2 / 13.342688→-1 / 0.117547→-2 · 무 · **-5** | 동일 | ○ | `tesla.*.f6reg28` · `tesla.net_cash.nc37` |
| oracle | P1/P2/P3 · P4 · F6 | 25.967109→-1 / 8.599522→-1 / 0.173487→-1 · ns -0.053800 무 · **-3** | 동일 | ○ | `oracle.*.f6reg28` · `oracle.net_cash.nc37` |
| openai | 비상장 P2 · 보정 · F6 | ps_ratio 39.0→-4 · 보정 0칸 · **-4** | 동일 | ○ | `openai.ps_ratio.priv31` · `arr_growth` kind 불충족 · `capital_efficiency` 40,000/185,000=0.216216 < 0.50 |

- **`nonop_share` 산식 확인.** `calc_f6_params._nonop_share`(`scripts/scorecard/calc_f6_params.py:50~108`)가 실제로 `(pretax_income_ttm − operating_income_ttm) / pretax_income_ttm` 을 돌고 규칙 `policies.f6.p4.conditions[nonop_share].formula` 와 같다. 11개사 값이 내 재계산과 소수 이하 전부 일치한다.
- **음수 분모 처리.** spacex-xai 는 세전이익 -7,623M 이라 `calc_f6_params.py:83~89` 가 `incompatible_basis` 로 산출을 막는다. 내가 그대로 나누면 +0.510429 가 나와 임계를 넘지만 **흑자 기업의 같은 값과 뜻이 다르므로 만들지 않는 것이 맞다.** 결과가 바뀌지 않는 이유도 확인했다 — `conditions_hit` 이 `period_basis_not_ttm`·`short_history` 둘이라 강등 한 칸은 그대로이고 `demotion_sole_cause` 는 null 이다.
- **oracle 대조.** 채점표 3-1a 각주 ᶜ 의 세전 $19.55B·영업이익 $22.39B 를 `AI기업_채점표_v1.5.md:824` 에서 직접 읽었다. 보존 ORCL companyfacts 로 세전 8,693(국내)+10,861(국외)=**19,554** 이고 `순이익 17,087 + 법인세 2,467 = 19,554` 로 상대오차 0 이다. 각주의 22.39B 는 GAAP 영업이익 20,606 + `RestructuringCharges` **1,779** = 22,385 로 재현된다. 엔진이 GAAP 20,606 을 유지해 -0.053800 이 나오는 것은 규칙대로이고, |값| 이 임계 0.30 에서 -82.07% 라 판정도 갈리지 않는다.
- **P4 나머지 조건 전수.** `period_basis` 는 14개사 모두 `revenue_ttm` 관측의 `basis.period_basis` 와 일치한다(ttm 9 · annual 2 · quarterly_yoy 1 · 비상장 2). `stale_asof` 는 `_months_elapsed`(완결 개월 수)를 다시 구현해 대조했고 14개사 전부 임계 미만이다 — 최대가 tsmc 8개월(annual 임계 16), 다음이 alibaba 5개월, oracle 3개월이다. **한 곳도 걸리지 않는다.**
- **밴드·경계 전수.** P1·P2 는 `upper_exclusive`, P3 는 `lower_inclusive`, 비상장은 `lower_inclusive` 로 각각 다시 매겼고 전부 같다. 경계 플래그는 P1~P3 42칸 · P4 12칸 · G3 4칸을 `boundary_tolerance` 0.03 으로 재계산해 **불일치 0** 이다. 켜진 것은 spacex-xai G3 하나뿐이다(+0.86%).
- **소계·강등·하한.** 트랙별 `floor` 적용까지 다시 계산했다. 하한이 실제로 무는 곳은 spacex-xai 하나다(소계 -2 −1 = -3, `listed_newly` floor -3).

### F9 — G1~G4 · 14개사

| 기업 | 항목 | 엔진값 | 재계산값 | 일치 | 근거 |
|---|---|---|---|---|---|
| alphabet | G1→G2 · F9 | 0.331104 통과 → FCF +53,273M 악화 → **-1** | 동일 | ○ | `alphabet.operating_income_ttm`/`revenue_ttm.f6reg28` · `fcf_ttm.cashfcf35` · 판단 `fcf_trend=deteriorating` |
| amazon | G1→G2→G3→G4 · F9 | 0.120813 → -11,625M → 런웨이 9.953806 step0 → 커버리지 1.855739 step0 → **-2** | 동일 | ○ | 완충 78,213+37,500=115,713(`amazon.undrawn_credit.fix54`) · 496,000/267,279 |
| meta | G1→G2 · F9 | 0.380842 → +40,976M 악화 → **-1** | 동일 | ○ | `meta.fcf_ttm.cashfcf35` |
| microsoft | G1→G2 · F9 | 0.467808 → +66,987M 안정 → **0** | 동일 | ○ | `microsoft.fcf_ttm.cashfcf35` |
| tsmc | G1→G2 · F9 | 0.508287 → +31,959.3M 안정 → **0** | 동일 | ○ | `tsmc.operating_margin_ttm.f6reg28` 관측 직접 사용 |
| alibaba | G1→G2→G3→G4 · F9 | 0.048990 → -7,226M → 런웨이 3.099640 step0 → G4 미공시 확정 C-16 step-1 → **-3** | 동일 | ○ | 완충 19,068+3,330=22,398(`alibaba.undrawn_credit.fix53`) · `contracted_revenue.obsreg25` 가 `not_disclosed_confirmed` |
| anthropic | G1 보류→G2→G3→G4 · F9 | C-20 판정 보류 → 비상장 미공시 -2 → G3 생략 → G4 비교 불가·추가 감점 없음 → **-2** | 동일 | ○ | `anthropic.operating_margin_ttm.priv31`·`fcf_ttm.priv31` 둘 다 `not_disclosed_confirmed` · `coverage_comparable=no` |
| apple | G1→G2 · F9 | 0.331730 → +136,683M 안정 → **0** | 동일 | ○ | `apple.fcf_ttm.cashfcf35` |
| nvidia | G1→G2 · F9 | 0.652140 → +127,006M 안정 → **0** | 동일 | ○ | `nvidia.fcf_ttm.cashfcf35` |
| palantir | G1→G2 · F9 | 0.427985 → +3,358.272M 안정 → **0** | 동일 | ○ | `palantir.fcf_ttm.cashfcf35` |
| spacex-xai | G1 실패→G3→G4 · F9 | -0.161951 → 밴드 -3 → 런웨이 3.025751 step0(경계 ⚠️) → 커버리지 1.604388 step0 → C-05 `apply` → **-3** | 동일 | ○ | 완충 93,522+4,355=97,877 · 소진 32,348 · 47,461/29,582 |
| tesla | G1→G2 · F9 | 0.042193 → +5,762M 악화 → **-1** | 동일 | ○ | `tesla.fcf_ttm.cashfcf35` |
| oracle | G1→G2→G3→G4 · F9 | 0.305922 → -23,686M → 런웨이 1.320991 step-1 → 커버리지 2.552 step0 → **-3** | 동일 | ○ | 완충 31,289(미인출 여신 `not_disclosed`) · 638,000/250,000 |
| openai | G1 실패 · F9 | `bep_retreat=yes` → -4(하한) → G3/G4 생략 → **-4** | 동일 | ○ | `openai.F9.inputs.bep_retreat=yes` · `policies.f9.g1_bep_retreat_score=-4` · `calc_f9.py:126` |

- **G1 손실률 밴드.** `g1_bands_proposed` 를 그대로 다시 적용했다. spacex-xai -0.161951 은 `-0.30 ≤ m < -0.10` 이라 -3 이고, `buffer_erosion=no`·`direction_*=unknown` 이라 조정이 없다. G1 이 밴드로 내려간 유일한 회사다.
- **G1 대체 산출의 기간 기준 검사.** `operating_margin_ttm` 관측이 없는 8개사는 `operating_income_ttm / revenue_ttm` 으로 내려가는데, `calc_f9.py:106~115` 가 두 관측의 `period_basis` 가 다르면 비율을 만들지 않는다. 8개사 전부 `ttm/ttm` 으로 같아 실제로 산출된다. spacex-xai 는 관측 `operating_margin_ttm.f6reg28` -0.161951 이 직접 있고, 그 값이 `-3,732 / 23,044`(TTM 매출 전량)와 맞는 것도 확인했다 — 12개월 손익을 한 분기 매출로 나눈 값이 아니다.
- **런웨이 산식·단위.** `(cash + undrawn) / burn` 을 네 곳 전부 다시 계산했고 단위는 모두 USD, 부호는 `burn = -fcf` 로 양수다. 완충에 `net_cash` 가 섞이지 않은 것도 확인했다 — alphabet 을 예로 들면 `cash` 55,911M 과 `net_cash` 121,683M 이 갈려 있고, 규칙 `net_cash.scope_separation`(즉시성 대 시장성) 대로 G3 는 `cash` 만 읽는다.
- **G4 커버리지.** `contracted_revenue / offbalance_B` 를 네 곳 다시 계산했다(1.855739 · 1.604388 · 2.552 · alibaba 는 분자 미공시 확정). `g4_coverage_keep=1.0` 이라 네 곳 다 step 0 이거나 C-16 step -1 이다. alibaba 의 분모 36,851M 이 `RMB254,198M ÷ 6.898` 인 것도 검산했다(36,850.97).
- **amazon 완충의 만기 민감도.** 완충 37,500M 중 22,500M(364일 회전 5,000 + 지연인출 17,500)이 기준일 직후 소멸·만기다. 빼고 계산하면 런웨이 9.95년 → **8.02년**으로 여전히 임계 3년 위라 step 0 이 안 바뀐다. 초안이 이 사실을 각주로 적고 있다.

### 원자료 재합산 — 보존 SEC 제출본·20-F

| 기업 | 항목 | 등록값 | 원자료 재합산 | 일치 | 근거 |
|---|---|---|---|---|---|
| alphabet | net_cash | 121,683M | 55,911 + 186,563 − (98,165+1,999) − (18,037+2,590) = 121,683 | ○ | `validation/f6-avail-15/_raw/GOOGL.companyfacts.json` 2026-06-30 시점 사실(10-Q `0001652044-26-000071`). `CashCashEquivalentsAndShortTermInvestments` 242,474 가 앞 두 항의 합과 같아 교차 확인된다 |
| nvidia | net_cash | 60,509M | (22,443 + 34,143 + 42,783) − 33,366 − 5,494 = 60,509 | ○ | `NVDA.companyfacts.json` 2026-07-26. 시장성 지분증권 `EquitySecuritiesFvNi` 42,783 포함, 비시장성 47,898 제외, 만기 버킷 41,000 미사용 — 규칙 `securities_scope` 대로다 |
| oracle | net_cash | -135,538M | (31,289+605) − (130,105−564) − (30,190+7,701) = -135,538 | ○ | `ORCL.companyfacts.json` 2026-05-31(10-K `0001193125-26-277521`) |
| spacex-xai | net_cash | 60,301M | (93,522 + 6,487) − 38,285 − (1,079+344) = 60,301 | ○ | `SPCX.companyfacts.json` 2026-06-30. 제한현금 830(=94,352−93,522)·암호자산 1,098·비시장성 지분 237 제외 확인 |
| tsmc | net_cash | US$69,224,963,341 | NT$백만 3,240,002.8 − 1,068,415.7 = 2,171,587.1 ÷ 31.37 | ○ | 관측 `basis.rows` 15줄을 직접 더해 세 소계가 모두 맞는다. FX 31.37 은 FY2025 20-F Note 3 선언 환율 |
| alibaba | net_cash | US$49,838,648,884 | RMB백만 625,509.0 − 281,722.0 = 343,787.0 ÷ 6.898 | ○ | 보존 20-F `3cf9799:validation/offb-24/_raw/baba-20260331.htm` 에서 `Listed equity securities … 100,594`·`Investments in privately held companies … 130,447`·`Other treasury investments … 238,075`·`Total operating lease liabilities (Note 19) 21,726`·`Non-current exchangeable bonds 24 — 10,976 1,591` 을 직접 읽어 대조했다. 주석 11 분할이 **100,594 + 130,447 + 10,880 + 238,075 = 479,996** 으로 대차대조표 합계와 정확히 맞아, 시장성·비시장성 구분이 빠짐도 겹침도 없다 |
| alphabet | 매출 TTM | 445,866M | 229,692 + 402,836 − 186,662 | ○ | GOOGL companyfacts 기간 사실 3건. 전기 누계 186,662 가 2025·2026 두 제출본에 같은 값으로 실려 재작성 세대 충돌이 없다 |
| alphabet | 영업이익 TTM | 147,628M | 80,466 + 129,039 − 61,877 | ○ | 위와 같은 3건 |
| oracle | 매출·영업이익 TTM | 67,357M · 20,606M | FY2026(2025-06-01~2026-05-31) 단일 공시값 | ○ | `direct_fy_is_ttm`. 규칙 `ttm_window.verification` 대로 FY 태깅값 자체다 |
| oracle | B종 대안 태그 | 할인차금 정정 | 41,867 − 30,190 = **11,677** · 11,460 − 7,701 = **3,759** | ○ | ORCL companyfacts. FIX-58·FIX-59 의 `Excess` 오독 정정이 1차 자료에서 그대로 성립한다. 남는 B종 후보 `UnrecordedUnconditionalPurchaseObligationBalanceSheetAmount` 13,309M 도 확인 |
| 8개사 | TTM FCF | 각 등록값 | `당기 누계 + 전기 FY − 전기 동일 누계` 로 OCF·CapEx 를 각각 복원해 차를 검산 | ○ | alphabet 185,675−132,402 · meta 130,301−89,325 · tesla 18,685−12,923 · nvidia 134,360−7,354 · apple 146,724−10,041 · palantir 3,400.291−42.019 · spacex-xai 9,900−42,248 · amazon 은 직접 공시 TTM 161,403−173,028 이 복원값과 같다. **부호 규약(capex 를 양수 유출로 빼는 것)이 8건 모두 같다** |
| tsmc | P3 통화 | 0.316050 | NT$3,809,054.3 / NT$2,894,307.7 − 1 | ○ | 당해·전년을 **같은 선언 환율 31.37** 로 환산해 성장률이 현지통화와 같다. 규칙 `fx.same_rate_for_both_periods` 충족 |
| alibaba | P3 통화 | 0.027423 | RMB1,023,670 / RMB996,347 − 1 | ○ | 같은 환율 6.898. 두 해가 서로 다른 20-F 환율로 섞이지 않았다 |
| 12개사 | P1 귀속 범위 | parent_attributable | `net_income_ttm` 12건 전부 `basis.ownership_scope=parent_attributable` | ○ | 규칙 `P1.input_scope` 와 일치. tsmc 는 연결 1,695,124.9 에 비지배 −2,479.1 을 조정한 1,697,604.0 이다 |
| 실행 전체 | results_hash | `a5b80e71…f284d46` | `results_hash` 키를 뺀 정렬 JSON 의 sha256 을 다시 계산 | ○ | 리뷰 템플릿 frontmatter 와 같다. `draft_hash 1bf14082…6f30c5e` 도 초안 파일 바이트 sha256 과 같다 |
| 14개사 | 총점 | 15·15·15·14·10·10·9·9·8·7·6·5·2·2 | 9 factor 합을 다시 더함 | ○ | 지시서의 총점과 전부 같고 미산출 factor 는 한 곳도 없다 |

**불일치 건수: 0.** 점수·소계·밴드·경계·게이트 경로 어느 칸도 어긋나지 않는다.

## 체크리스트

| ID | 결과 | 근거(파일:행) |
|---|---|---|
| Q04 | pass | 시총이 점수에 들어가는 자리는 비율의 분자뿐이다 — `scorecard/rules/v1.7.json` P1 `market_cap / net_income_ttm`·P2 `(market_cap - net_cash) / revenue_ttm`, 구현은 `scripts/scorecard/calc_f6_params.py:267~269`. 규모 자체를 재는 밴드는 F6·F9 어디에도 없다. 결과가 그것을 보여 준다 — **표 전체 최대 시총인 nvidia(약 $5.42T = 28.100519 × 192,879M)가 F6 -2 로 상위**이고, 시총이 훨씬 작은 palantir 가 -4, tesla 가 -5 다. 비상장도 `private_bands.input` 이 `ps_ratio` 라 밸류 절대액이 아니다 |
| Q06 | pass | 관측 단위가 `USD`·`USD/share`·`ratio`·`text`·`years` 넷뿐이고 토큰 수·사용자 수 같은 볼륨 지표는 한 건도 없다(`observations.json` 363건 전수). P3 는 매출 성장률, G4 는 계약 수입 대 약정으로 둘 다 금액 기준이다. 볼륨과 가치를 가르는 장치도 실제로 문다 — `policies.f6.private_correction.conditions[arr_growth].accepted_kinds:["actual"]` 가 런레이트를 ARR 로 세지 않아 anthropic·openai 의 `arr_growth` 가 값으로는 0.382979·0.600000 으로 임계를 넘는데도 불충족이다(`results.json` 두 회사 `correction.conditions.arr_growth.met=false`) |
| Q10 | pass | 거리(수준)와 가속(변화율)을 쓰는 자리가 갈려 있다. P3 는 `revenue_ttm / revenue_ttm_prior - 1` 로 변화율이고 누적 매출이 아니다(`v1.7.json` P3 `formula`). G3 런웨이는 수준을 수준으로 쓰는 자리이고, G2 는 `fcf_trend` 로 방향만 받는다. F6·F9 안에서 누적 성과를 성장률 자리에 넣은 곳을 찾지 못했다. 다만 아래 발견 사항의 `arr_prior` 시점 결측을 함께 본다 — 점수에는 닿지 않는다 |
| Q11 | **fail** | 두 자리에서 걸린다. **(1)** `listed_ttm`·`listed_annual` 에서 순손실이면 P1 이 `requires_positive` 를 못 넘어 `missing` 에 들어가고, `calc_f6_params.py:414~418` 이 **이미 산출한 P2·P3 를 버리고 F6 전체를 `pending_data` 로 돌려준다.** 스크래치에서 tesla 의 `net_income_ttm` 만 음수로 뒤집어 `compute_listed` 를 직접 호출해 재현했다 — `score=None · status=pending_data` 인데 같은 호출의 P2 13.342688, P3 0.117547 은 정상 산출돼 있었다(대조군은 원값으로 -5 를 그대로 재현). Q11 이 든 1999년 아마존이 이 트랙에 들어오면 ⑥ 이 아예 없다. 등록은 `v1.7.json:1952` **C-28**(pending · trigger·when 2026-11 있음)이고 그 `implementation_status.evidence` 가 내 재현과 같다. **(2)** openai F9 -4 는 하한이고, 그 근거는 측정된 손실률이 아니라 `bep_retreat=yes` 라는 전망 한 칸이다(`calc_f9.py:126`·`156~160`). openai 의 TTM 영업손익은 `not_disclosed_confirmed` 라 단위경제가 아예 측정돼 있지 않다. 규칙 자신이 이 충돌을 적는다 — `v1.7.json:2605` TEN-RA5-02 가 별표 D 388~390행(`계획·발표·포지션은 0점`)과 C-20 의 `why_not_assume_loss` 를 근거로 `전망·목표로 손실을 단정하는 것` 이라고 쓴다. **오늘 점수에 닿는 것은 (2)뿐이고 (1)은 잠재다** — 이번 실행의 상장사 12곳은 전부 `net_income_ttm > 0` 이라 (1)이 발동한 회사가 없다. 유일한 순손실 상장사 spacex-xai 는 `listed_newly` 라 P1 을 트랙에서 빼고 P2·P3 로 -3 을 받는다 |

### Q11 승계 예외가 서는지 — 서지 않는다

`AGENTS.md:71` 의 세 요건을 근거 (2) 에 하나씩 대면 이렇다.

1. **`carried_score` 로 승계한 판단인가 — 아니다.** `results.json` 의 openai F9 는 `status: ok · basis: computed` 다. 판단 기록 `openai.F9` 자체는 `status: carried`(`carried_from: baseline:v1.5`)이지만 그것이 주는 것은 게이트 입력이고, **점수 -4 는 이번 실행의 엔진과 이번 실행의 정책값(`g1_bep_retreat_score`)이 만든다.** 조항이 가리키는 `carried_score` 상태가 아니다.
2. **이번 실행이 그 잣대를 바꾸지 않았는가 — 바꿨다.** 엔진 동작은 그대로다(커밋 `0ab6ffe` 의 `calc_f9.py` diff 는 주석 네 줄뿐이고 `if margin is None and not bep_retreat:` 는 이전부터 있었다). 그러나 규칙 문면은 달라졌다 — FIX-59 가 `policies.f9.g1_bep_retreat_precedence`(`v1.7.json:1224`, `decided_at 2026-09-17`, `decided_by 사용자`)를 **신설**해, 선언이 없고 경고가 `결정 대기` 라고 적던 자리를 확정된 우선순위로 바꿨다. **규칙 파일이 이 점을 스스로 인정한다** — TEN-RA5-02 의 `why_carried_exception` 이 `이번 실행이 이 자리의 잣대를 문면으로 확정했다 … 그래서 예외로 넘기지 않고 정식 긴장으로 둔다` 로 적혀 있다(`v1.7.json:2609`).
3. **긴장 목록에 재검토 시점과 함께 등록됐는가 — 근거 (2) 는 됐다.** TEN-RA5-02 · `recheck_at 2026-11` · `third_party_recheck: committed`(비 Claude 세션). 근거 (1) 은 `open_tensions` 가 아니라 `decisions` 의 C-28 이라 조항 문면이 요구하는 자리가 아니다.

요건 1·2 가 안 서고, 근거 (1) 은 3 도 안 선다. **Q11 fail 은 승계 예외로 덮이지 않는다.** 8차 리뷰어의 `예외 아님` 과 같은 결론이고, 나는 원문과 규칙을 다시 보고 독립적으로 이 결론에 왔다.

**이해상충 고지.** 나는 여기서 openai F9 를 재판정하지 않았다. `C-20 우선`(openai -2 · 총점 4)과 `bep_retreat 우선`(현행 -4 · 총점 2) 중 어느 쪽이 옳은지는 TEN-RA5-02 가 비 Claude 세션에 맡긴 문제이고, openai 는 Anthropic 경쟁사라 내가 판정할 자리가 아니다. 위 판정은 **체크리스트 항목이 통과했는지와 예외 조항이 서는지**에만 닿고 점수는 한 칸도 건드리지 않는다.

## 발견 사항

- **[severity: medium]** `scripts/scorecard/calc_f9.py:160` · `scripts/scorecard/render_common.py:473` · `scorecard/rules/v1.7.json:1541`(decisions C-06 `summary`) — **FIX-59 가 확정한 것을 아직 미결이라고 적는 문장 셋이 남아 있다.** FIX-59 는 `policies.f9.g1_bep_retreat_precedence` 를 신설해 우선순위를 사용자 결정으로 확정했는데(`v1.7.json:1224`), 세 자리는 그대로 `우선순위 명문화는 결정 대기` · `손실률 경계·우선순위 명문화만 미결이다` 라고 말한다. 이 문장은 산출물까지 흘러간다 — `results.json` 의 openai F9 `warnings[0]` 이 그 문자열이고, 초안 `drafts/ai-scorecard-2026-09-obsreg.md:1092` 와 `:1281` 에 그대로 실려 있다. 같은 C-06 `summary` 는 `BEP 후퇴→-5` 라고도 적어 C-06 재척도(-4) 와도 어긋난다. **점수는 한 칸도 닿지 않고 고칠 것은 문자열 셋이다.** 다만 셋 다 해시에 묶인 산출물을 거치므로 계산·초안 재생성과 새 `results_hash`·`draft_hash` 가 따라온다 — 조율자가 비용을 알고 판단할 자리다. 이 항목은 어느 미결·긴장에도 등록돼 있지 않다.
- **[severity: low]** `scripts/scorecard/calc_f6_params.py:414~418` — Q11 근거 (1) 의 자리. 순손실 상장사가 `listed_ttm`·`listed_annual` 에 들어오면 산출된 P2·P3 를 버리고 F6 가 `pending_data` 가 된다. `listed_newly` 만 `optional_parameters` 로 이 경로를 피해, **같은 순손실이라는 조건이 트랙에 따라 다르게 처리된다.** 재현은 위 Q11 칸에 적었다. **C-28 로 등록돼 있고**(pending · trigger `listed_ttm·listed_annual 트랙에 순손실 기업이 들어올 때` · when 2026-11) 이번 실행 점수 영향은 0 이다.
- **[severity: low]** `observations.json` `anthropic.arr_prior.priv31` — `basis.period_label` 이 null 이라 `arr_growth 0.382979` 가 **얼마의 기간에 걸친 증가인지 모르는 비율**이다. 지어내지 않고 null 로 둔 것은 옳은 처리이고, `accepted_kinds:["actual"]` 때문에 조건이 어차피 불충족이라 점수에 닿지 않는다. 다만 `kind` 제한이 풀리면 이 비율이 바로 보정 임계와 겨루게 되므로 그때 기간을 먼저 정해야 한다. `capital_efficiency`(65,000/125,000=0.52)는 수준 대 수준이라 이 문제가 없다.
- **[severity: low]** `results.json` oracle F6 P1 = 25.967109 — 밴드 경계 25 에서 **+3.87%** 다. 플래그가 안 붙은 것 중에서는 alibaba G3(+3.32%) 다음으로 경계에 가깝고, **이 한 칸이 oracle F6 -3 → -2 · 총점 2 → 3 을 가른다.** 허용폭 0.03 은 C-27 로 등록돼 있고 초안이 거리 자체는 늘 보여 주므로 새 조치는 필요 없다. **다음 라운드에서 폭을 정할 때 alibaba G3 와 함께 볼 표본으로 적어 둔다.**
- **[severity: low]** `observations.json` `oracle.undrawn_credit.fix54` = null(`missing_type: unverified`) 인데 `calc_f9.py:303` 의 `undrawn or 0.0` 이 그것을 0 으로 세어 런웨이 1.320991 → step -1 을 만든다. 실측 못 한 값을 0 으로 쓰는 형태지만, 규칙 C-04 가 완충을 `현금 + **확정** 미인출 여신` 으로 좁히므로 미확정분이 0 으로 들어가는 것은 설계대로다. **뒤집히려면 미인출 여신이 약 39.8B 이상이어야 하고**, 보존 ORCL companyfacts 에는 `DebtInstrumentUnusedBorrowingCapacityAmount`·`LineOfCreditFacility*` 계열 사실이 한 건도 없어 `unverified` 라벨 자체는 맞다(같은 검색에서 tesla 는 5,000M 이 잡힌다). 민감도가 어디에도 안 적혀 있다는 것만 남긴다.

## 확인 못 한 것

- **oracle B종 약정 250,000M 의 출처.** 보존 ORCL companyfacts 2026-05-31 시점 사실을 전수로 훑어 대응하는 리스·약정 금액이 없다는 것까지는 확인했으나, **그 값이 어디서 온 것인지는 가리지 못했다.** C-26 으로 등록돼 있고 커버리지 2.552 든 대안 47.937 이든 G4 step 0 이라 오늘 점수는 갈리지 않는다.
- **alibaba `nonop_share` 저장값 0.54 와 재계산 0.612415 의 차.** 규칙이 `가리지 못했다` 로 적어 둔 자리인데 나도 가리지 못했다. 지분법 손익·비지배지분이 세전이익 아래에 오는 구조까지는 확인했으나 저장값이 어느 순이익·어느 세전이익을 썼는지는 `basis` 가 없어 복원할 수 없다. |0.612415| 든 |0.54| 든 임계 0.30 위라 판정은 같다.
- **tsmc 20-F 원문 직접 대조.** `net_cash` 15줄은 관측 `basis.rows` 의 인용문과 US$ 칸 역검산(31.37)으로만 확인했고 `f14a235:validation/tsm-edgar-29/_raw/tsm-20251231.htm` 를 열어 줄마다 맞춰 보지는 않았다. alibaba 쪽은 보존 20-F 를 실제로 열어 여섯 줄을 대조했다.
- **market_cap 12건·ntm_per 12건의 실측.** 전부 `legacy_unverified` 이고 원천 정책 밖 공급사 값이라 이번 실행에서도 재측정되지 않았다. P1·P2 가 그 위에 서는데 **엔진이 `unverified_inputs` 로 표시하고 점수는 깎지 않는다** — 처리는 규칙대로이나 값 자체를 내가 확인한 것은 아니다.
- **비상장 두 곳의 `ps_ratio` 30.0·39.0.** v1.5 원문이 준 TTM 보정 추정치를 그대로 승계한 값이고, 그 보정을 내가 다시 하지는 못했다(분기 매출 원자료가 없다). 구간 양 끝이 같은 밴드에 드는 것과 밴드 적용이 규칙대로인 것만 확인했다.
