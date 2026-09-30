# financial-calc — 재무 계산
검토자: Claude Opus 5 (`claude-opus-5[1m]`) · NTM-전망치조사 워크트리에서 연 독립 리뷰 세션(이 실행을 만든 세션 아님) · 2026-09-17 · 기준 커밋 `f313060` · 같은 세션의 재판정 3회
결과: pass
요약: **직전 판정에서 낸 medium 둘이 실제로 닫혔다.** 고쳤다는 주장을 믿지 않고 규칙·코드·산출물을 내가 직접 다시 훑었고, 같은 계열이 남았는지 정규식 다섯 갈래로 산출물 10곳·코드 19파일·문서 전체를 독립 전수했다 — **살아 있는 잔존 0건**이다. 재계산도 14개사 전부 불일치 0 이고 새 `results_hash dda69e88…`·`draft_hash 9ac09ce3…` 를 직접 계산해 맞췄다. 점수 페이로드는 `96afd80` 과 **바이트 동일**이라 이번 반영이 문면만 건드렸다는 것도 기계로 확인했다. 새 발견은 low 하나다 — `bep_retreat` 가 미치는 범위를 문면이 실제보다 좁게 적는다(흑자 상장사도 하한으로 내려간다). 점수에 닿지 않고 그 자리의 판단은 이미 TEN-RA6-01 이 잡고 있어 영역을 막지 않는다.

## 재계산 대조표

엔진을 호출하지 않고 `observations.json`·`judgments.json`·`v1.7.json`·`run.json` 에서 직접 다시 계산했다(스크래치 파이썬, 저장소 미기록). 관측 선택은 `inputs.ObsLookup` 규약을, F9 는 C-20 탐지·C-16·C-05 분기를 규칙 선언과 실행 선택에서 다시 읽어 태웠다.

**먼저 입력이 안 움직였는지 기계로 확인했다.** `96afd80 → f313060` 에서 `observations.json`·`judgments.json` 이 **바이트 동일**이고, `results.json` 은 `companies`·`ranking` 의 정렬 JSON 해시가 **같다**(`833b99c2b79616a0`). 바뀐 최상위 키는 `input_hashes`(run·rules)와 `results_hash` 둘뿐이고 `warnings_count` 도 165 그대로다. 그래서 앞선 두 라운드에 보존 원자료로 세운 검산이 그대로 유효하고, 아래 원자료 절에서 다시 돌려 확인했다.

### F6 — P1~P4 · 14개사 (전 라운드와 동일)

| 기업 | 항목 | 엔진값 | 재계산값 | 일치 | 근거 |
|---|---|---|---|---|---|
| alphabet | P1/P2/P3 · P4 · F6 | 16.871071→0 / 8.967531→-1 / 0.200504→-1 · ns 0.506705 hit · **-3** | 동일 | ○ | `alphabet.market_cap.v15`·`net_cash.nc37`·`net_income_ttm.f6reg28`·`revenue_ttm(.prior).f6reg28`·`pretax_income_ttm.nonop44`·`operating_income_ttm.f6reg28` |
| amazon | P1/P2/P3 · P4 · F6 | 20.328058→0 / 3.699118→0 / 0.157666→-1 · ns 0.465925 hit · **-2** | 동일 | ○ | `amazon.*.f6reg28` · `amazon.net_cash.nc37` |
| meta | P1/P2/P3 · P4 · F6 | 22.173926→0 / 6.712281→0 / 0.276514→-1 · ns 0.006832 무 · **-1** | 동일 | ○ | `meta.*.f6reg28` · `meta.net_cash.nc37` |
| microsoft | P1/P2/P3 · P4 · F6 | 27.588991→-1 / 11.276462→-1 / 0.177887→-1 · 무 · **-3** | 동일 | ○ | `microsoft.*.f6reg28` · `microsoft.net_cash.nc37` |
| tsmc | P1/P2/P3 · P4 · F6 | 39.729819→-1 / 17.136514→-1 / 0.316050→0 · `period_basis_not_ttm` hit · **-3** | 동일 | ○ | `tsmc.*.f6reg28`(annual · 선언 환율 31.37) · `tsmc.net_cash.nc37` |
| alibaba | P1/P2/P3 · P4 · F6 | 17.978801→0 / 1.483557→0 / 0.027423→-3 · ns 0.612415 + `period_basis_not_ttm` hit · **-4** | 동일 | ○ | `alibaba.*.f6reg28`·`.obsreg25`(annual · 선언 환율 6.898) · `alibaba.net_cash.nc37` |
| anthropic | 비상장 P2 · 보정 · F6 | ps_ratio 30.0→-4 · 보정 0칸 · **-4** | 동일 | ○ | 구간 30~39 양 끝 모두 `30x+` · `arr`·`arr_prior` 가 `kind=run_rate` 라 `arr_growth` 불충족, `require_all` 이라 승격 0 |
| apple | P1/P2/P3 · P4 · F6 | 36.764136→-1 / 10.020500→-1 / 0.142424→-2 · 무 · **-4** | 동일 | ○ | `apple.*.f6reg28` · `apple.net_cash.nc37` |
| nvidia | P1/P2/P3 · P4 · F6 | 28.100519→-1 / 17.689841→-1 / 0.833759→0 · ns 0.140000 무 · **-2** | 동일 | ○ | `nvidia.*.f6reg28` · `nvidia.net_cash.nc37` |
| palantir | P1/P2/P3 · P4 · F6 | 134.915994→-2 / 64.620502→-2 / 0.789212→0 · 무 · **-4** | 동일 | ○ | `palantir.*.f6reg28` · `palantir.net_cash.nc37` |
| spacex-xai | P2/P3 · P4 · F6 | P1 미산출 / 80.268139→-2 / 0.919430→0 · `period_basis_not_ttm`+`short_history` hit · 하한 -3 · **-3** | 동일 | ○ | P2 분모가 `revenue_ttm_full.fix56` 23,044M · 세전 -7,623M 이라 ns 는 `incompatible_basis` |
| tesla | P1/P2/P3 · P4 · F6 | 370.662461→-2 / 13.342688→-1 / 0.117547→-2 · 무 · **-5** | 동일 | ○ | `tesla.*.f6reg28` · `tesla.net_cash.nc37` |
| oracle | P1/P2/P3 · P4 · F6 | 25.967109→-1 / 8.599522→-1 / 0.173487→-1 · ns -0.053800 무 · **-3** | 동일 | ○ | `oracle.*.f6reg28` · `oracle.net_cash.nc37` |
| openai | 비상장 P2 · 보정 · F6 | ps_ratio 39.0→-4 · 보정 0칸 · **-4** | 동일 | ○ | `capital_efficiency` 40,000/185,000=0.216216 < 0.50 |

### F9 — G1~G4 · 14개사

| 기업 | 항목 | 엔진값 | 재계산값 | 일치 | 근거 |
|---|---|---|---|---|---|
| alphabet | G1→G2 | 0.331104 통과 → FCF +53,273M 악화 → **-1** | 동일 | ○ | 147,628/445,866 |
| amazon | G1→G2→G3→G4 | 0.120813 → -11,625M → 런웨이 9.953806 step0 → 커버리지 1.855739 step0 → **-2** | 동일 | ○ | 완충 78,213+37,500=115,713 · 496,000/267,279 |
| meta | G1→G2 | 0.380842 → +40,976M 악화 → **-1** | 동일 | ○ | 86,926/228,247 |
| microsoft | G1→G2 | 0.467808 → +66,987M 안정 → **0** | 동일 | ○ | 155,237/331,839 |
| tsmc | G1→G2 | 0.508287(관측) → +31,959.3M 안정 → **0** | 동일 | ○ | `tsmc.operating_margin_ttm.f6reg28` |
| alibaba | G1→G2→G3→G4 | 0.048990(관측) → -7,226M → 런웨이 3.099640 step0 → C-16 확인된 미공시 step-1 → **-3** | 동일 | ○ | 완충 19,068+3,330=22,398 |
| anthropic | G1 보류→G2→G3→G4 | C-20 판정 보류 → 비상장 미공시 -2 → G3 생략 → G4 비교 불가 → **-2** | 동일 | ○ | 영업손익·FCF 둘 다 `not_disclosed_confirmed` · `coverage_comparable=no` |
| apple | G1→G2 | 0.331730 → +136,683M 안정 → **0** | 동일 | ○ | 154,859/466,823 |
| nvidia | G1→G2 | 0.652140 → +127,006M 안정 → **0** | 동일 | ○ | 197,579/302,970 |
| palantir | G1→G2 | 0.427985 → +3,358.272M 안정 → **0** | 동일 | ○ | 2,634,652/6,155,941(천) |
| spacex-xai | G1 실패→G3→G4 | -0.161951 → 밴드 -3 → 런웨이 3.025751 step0(경계 ⚠️) → 커버리지 1.604388 step0 → C-05 `apply` → **-3** | 동일 | ○ | 완충 93,522+4,355=97,877 · 소진 32,348 |
| tesla | G1→G2 | 0.042193 → +5,762M 악화 → **-1** | 동일 | ○ | 4,372/103,619 |
| oracle | G1→G2→G3→G4 | 0.305922 → -23,686M → 런웨이 1.320991 step-1 → 커버리지 2.552 step0 → **-3** | 동일 | ○ | 완충 31,289(여신 `not_disclosed`) |
| openai | G1 보류→G2→G3→G4 | C-20 판정 보류(BEP 후퇴 미적용) → 비상장 미공시 -2 → G3 생략 → G4 비교 불가 → **-2** | 동일 | ○ | 경로가 anthropic 과 문자 그대로 같고 다른 것은 `bep_retreat_not_applied` 기록과 C-29 경고 두 줄뿐이다 |

- **경계 전수.** P1~P3 · P4 · G3 합쳐 58칸을 `boundary_tolerance` 0.03 으로 재계산했고 **불일치 0**, 켜진 것은 `spacex-xai G3 +0.86%` 하나다.
- **총점·순위.** 9 factor 합을 14개사 다시 더했고 미산출 factor 가 없다. openai 4(단독 13위) · oracle 2(단독 14위)이고 나머지 12개사 불변이다.
- **테스트.** 직접 돌려 `677 tests OK (skipped=5)` 다.

### 원자료 재합산 — 보존 SEC 제출본·20-F (재확인)

| 기업 | 항목 | 등록값 | 원자료 재합산 | 일치 | 근거 |
|---|---|---|---|---|---|
| alphabet | net_cash | 121,683M | 55,911+186,563−(98,165+1,999)−(18,037+2,590) | ○ | `GOOGL.companyfacts.json` 2026-06-30. `CashCashEquivalentsAndShortTermInvestments` 242,474 가 앞 두 항의 합과 같아 교차 확인된다 |
| nvidia | net_cash | 60,509M | (22,443+34,143+42,783)−33,366−5,494 | ○ | `NVDA…` 2026-07-26. 시장성 지분증권 42,783 포함 · 비시장성 47,898 제외 · 만기 버킷 41,000 미사용 |
| oracle | net_cash | -135,538M | (31,289+605)−(130,105−564)−(30,190+7,701) | ○ | `ORCL…` 2026-05-31 |
| spacex-xai | net_cash | 60,301M | (93,522+6,487)−38,285−(1,079+344) | ○ | `SPCX…` 2026-06-30. 제한현금 830 · 암호자산 1,098 · 비시장성 237 제외 |
| tsmc | net_cash | US$69,224.9633M | (3,240,002.8−1,068,415.7)÷31.37 | ○ | `basis.rows` 15줄 직접 합산 |
| alibaba | net_cash | US$49,838.6489M | (625,509.0−281,722.0)÷6.898 | ○ | 보존 20-F `3cf9799:validation/offb-24/_raw/baba-20260331.htm` 여섯 줄 직접 확인. 주석 11 분할 **100,594+130,447+10,880+238,075=479,996** 이 대차대조표 합계와 정확히 맞는다 |
| alphabet | 매출·영업이익 TTM | 445,866M · 147,628M | 229,692+402,836−186,662 · 80,466+129,039−61,877 | ○ | 전기 누계가 두 제출본에 같은 값이라 재작성 세대 충돌이 없다 |
| oracle | 세전이익·nonop | 19,554M · -0.053800 | 8,693+10,861 = 17,087+2,467 · (19,554−20,606)/19,554 | ○ | 상대오차 0 |
| oracle | B종 대안 태그 | 할인차금 | 41,867−30,190=**11,677** · 11,460−7,701=**3,759** | ○ | `Excess` 오독 정정이 1차 자료에서 성립 |
| 8개사 | TTM FCF | 각 등록값 | OCF·CapEx 를 누계식으로 복원해 차를 검산 | ○ | 부호 규약이 8건 모두 같다 |
| 실행 전체 | results_hash · draft_hash | `dda69e88…b49c1ce` · `9ac09ce3…d55eb752` | 정렬 JSON sha256 · 파일 바이트 sha256 | ○ | 조율자가 준 값과 같다 |

**불일치 건수: 0.**

## 반영 확인 — 직전 판정의 지적 다섯

고쳤다는 주장은 믿지 않고 자리마다 직접 봤다.

| 지적 | 상태 | 내가 확인한 것 |
|---|---|---|
| **medium ①** C-06 `summary` 가 뒤집힌 우선순위를 반대로 적고 빌드 HTML 방법 표에 실린다 | **닫힘** | `v1.7.json:1571` 이 `C-20 비상장 경로가 먼저 서고, 상장사이거나 영업손익이 구조적 미공시가 아닌 경우에만 BEP 후퇴가 … 앞서` 로 바뀌었다. 이 조건문이 `_private_undisclosed_operating` 의 **정확한 부정**이다(C-20 은 `비상장 AND not_disclosed_confirmed AND C-20 선택` 일 때만 선다). `render_html.render_method` 가 싣는 blocking·pending 셋(C-05·C-06·C-16)을 다시 확인했고 이제 현재 동작과 같다 |
| **medium ②** `also_precedes_loss_band` 의 `순서가 관측되지 않는다` 가 사실이 아니고 테스트가 그것을 굳혔다 | **닫힘** | `v1.7.json:1252` 가 옛 문장을 `~~취소선~~` 으로 남기고 `이 닫음은 틀렸다` 로 정정했다. 내가 찾은 반례 수치와 같다(spacex-xai 밴드 -3 → BEP -4, `-30%` 초과일 때만 옛 주장이 성립). **테스트도 고쳤다** — `test_precedence_records_that_the_order_is_unobservable` 이 이름과 내용을 바꿔, 전제만 확인하고 결론을 주석으로 달았던 것을 docstring 으로 자인하고 `any(b["score"] > deepest)` 로 더 얕은 밴드의 존재를 건다. 그리고 `test_scorecard_fix63.py:112~125` 가 **엔진을 실제로 돌려** `(-3, proposed_v15_boundaries)` 대 `(-4, BEP 후퇴 → -4)` 를 확인한다 — 주장이 아니라 재현이다 |
| **리뷰어가 못 짚은 것 ①** C-07 `implementation_status.routes.openai` | **닫힘** | `v1.7.json:1606` 이 `G1 에서 BEP 후퇴로 실패해 하한 -4` 를 취소선 처리하고 현재 경로로 고쳤다. 덧붙인 `openai 가 이제 G4 에 닿아도 coverage_comparable=no 라 숫자를 읽기 전에 빠진다` 도 맞다 — `calc_f9._g4` 가 `comparable == "no"` 를 숫자 판독 앞에서 걸러 `incompatible` 을 돌려준다. C-07 `status` 는 `pending` 그대로다 |
| **리뷰어가 못 짚은 것 ②** `render_common.method_lines` | **닫힘** | `render_common.py:475~483` 에서 `두 경로가 만나도 결과는 같다` 가 빠지고 `그 자리에서는 순서가 결과를 가른다 … (TEN-RA6-01). 이번 실행에는 해당 기업이 없다` 로 바뀌었다. 초안 `1282행` 에 그 문장이 실려 있다 |
| **low** C-29 가 `reviewed_sign profit` 재배열을 안 적는다 | **닫힘** | `v1.7.json` C-29 `scope.what_changed` 가 `재배열이 문서보다 한 칸 더 갔다` 로 그 사실과 근거를 적었고, 판단 방향이 내가 적은 것과 같다(C-20 자신이 단일 분기 흑자를 통과 근거로 쓰지 말라고 하므로 새 순서가 맞다) |
| **low** 계획의 결정 표가 세 세대 전 문면 | **닫힘** | `plan/…:157` 이 규칙의 현재 C-06 문면과 같고, 계획 `rule_hash 21e120ae…` 가 실제 규칙 해시와 일치한다 — 해시만 손으로 다시 고정하던 것이 아니라 표를 실제로 다시 만들었다 |
| **low** 리뷰 템플릿 frontmatter 가 8차 해시 | **닫힘** | `results_hash dda69e88…` · `draft_hash 9ac09ce3…` 로 현재와 같고 `reviewers` 네 줄도 갱신됐다. rule-consistency·output-readability 가 FIX-61~63 의 변경을 아직 안 봤다는 사실까지 적어 둔 것은 정확한 기재다(내 영역 밖이라 판정하지 않는다) |

**내 독립 전수.** 반영 목록을 믿지 않고 직접 훑었다 — 산출물 10곳(규칙·run·results·judgments·observations·preview·초안·계획·리뷰템플릿·research), `scripts/scorecard/*.py` 19파일, `docs/scorecard/*.md` 전체에 정규식 다섯 갈래(옛 우선순위 주장 · 틀린 닫음 · openai F9 -4 주장 · 우선순위 미결 주장 · openai 총점 2)를 걸었다. **살아 있는 잔존 0건이다.** 걸린 것은 전부 (가) `superseded_record`·`what_it_said` 같은 취소선 보존, (나) `-4 → -2` 꼴의 전이 서술, (다) `470행을 살리면 다시 -4` 꼴의 반사실, (라) 고친 사실 자체의 기록이다. 해소된 `TEN-RA5-02` 의 `tension`·`why_carried_exception` 에 `[해소 전 기술]` 이라는 표시가 붙은 것도 확인했다.

**계약 검증도 직접 돌렸다.** `validate_contract` 오류가 **1건**이고 내용은 `review status 가 pass 가 아님: 'needs_fix'` 다 — 남은 하나가 이 영역 결과라는 조율자 설명과 같고, 그 밖에는 해시·체크리스트·절 구성이 모두 통과한다.

## 체크리스트

| ID | 결과 | 근거(파일:행) |
|---|---|---|
| Q04 | pass | 시총이 점수에 들어가는 자리는 비율의 분자뿐이다(`v1.7.json` P1·P2 `formula` · `calc_f6_params.py:280~285`). 규모를 재는 밴드가 F6·F9 어디에도 없고 결과가 그것을 보여 준다 — 최대 시총 nvidia(약 $5.42T)가 F6 -2 로 상위, 훨씬 작은 palantir 가 -4 · tesla 가 -5 다. 비상장도 `private_bands.input` 이 `ps_ratio` 다 |
| Q06 | pass | 관측 단위가 `USD`·`USD/share`·`ratio`·`text`·`years` 넷뿐이고 볼륨 지표가 363건 중 0건이다. P3 는 매출 성장률, G4 는 계약 수입 대 약정으로 둘 다 금액 기준이다. `private_correction.conditions[arr_growth].accepted_kinds:["actual"]` 가 런레이트를 ARR 로 세지 않아 anthropic 0.382979 · openai 0.600000 이 임계를 넘고도 불충족이다 |
| Q10 | pass | P3 는 `revenue_ttm / revenue_ttm_prior - 1` 로 변화율이고 누적이 아니다. G3 런웨이는 수준을 수준으로, G2 는 `fcf_trend` 로 방향만 받는다. 누적 성과를 성장률 자리에 넣은 곳을 F6·F9 에서 찾지 못했다. `arr_prior` 기간 미상은 `basis.period_unknown_blocks_growth` 에 적혀 있고 여전히 점수에 닿지 않는다 |
| Q11 | pass | **직전 판정에서 fail → pass 로 바꾼 것을 유지한다.** 근거 둘이 그대로 닫혀 있다 — C-28 `resolved` 로 순손실 상장사가 P2·P3 로 채점되고(합성 관측 재현: `score=-3 · status=ok` · `cause=requires_positive`), 수집 공백과 소유 범위 불일치는 여전히 `pending_data` 로 막힌다. C-29 로 openai 가 anthropic 과 같은 C-20 경로를 타 `g2_private_not_disclosed` -2 를 받고, 전망으로 하한을 주던 자리가 없다. 이번 실행에서 순적자 때문에 점수를 못 받거나 실격된 기업이 없다 — 유일한 순손실 상장사 spacex-xai 는 측정된 단위경제로만 채점된다(P2 80.27 · P3 +91.9% · G1 -16.195% · G3 3.03년 · G4 1.60) |

## 발견 사항

- **[severity: low · 새 발견]** `policies.f9.g1_bep_retreat_precedence.also_precedes_loss_band` · `decisions` C-06 `summary` · `render_common.py:478`(초안 1282행) · `TEN-RA6-01.also_covers_listed` — **`bep_retreat` 가 미치는 범위를 문면이 실제보다 좁게 적는다.** 네 자리가 모두 `손실률 밴드보다 앞선다` · `측정된 영업손실률 밴드를 전망이 덮어쓴다` 로 **적자 맥락에서만** 서술한다. 그런데 `calc_f9.compute_f9` 의 `g1_pass = (not bep_retreat) and (margin is None or margin > 0)` 은 **흑자 회사도 통과시키지 않는다** — `bep_retreat: yes` 면 영업이익률이 아무리 높아도 `else` 의 영업적자 구간으로 내려가 하한을 받는다. **시뮬레이션으로 확인했다**: microsoft(상장 · 측정 영업이익률 **+46.78%**)에 `bep_retreat` 만 `yes` 로 바꾸면 F9 가 **0 에서 -4 로** 떨어지고, 경로에 `result: "fail"` 이 **양수 마진과 함께** 기록된다(`{"result":"fail","operating_margin_ttm":0.4678…,"band":"BEP 후퇴 → -4"}`). 코드 주석이 그 블록을 `영업적자 구간` 이라 부르는데 흑자로도 들어온다. **동작 자체는 채점규칙 470행의 OR 조건 읽기와 어긋나지 않는다** — 이번에 새로 생긴 결함이 아니고 FIX-59 때부터 같은 식이다. 문제는 **이번 라운드가 `bep_retreat` 의 도달 범위를 설명하려고 쓴 문장들이 그 범위를 다 적지 않는다**는 것이고, 특히 이 질문을 넘겨받기로 한 `TEN-RA6-01.also_covers_listed` 가 손실 경우만 적어 **11월에 흑자 경우가 같이 판정되지 않을 수 있다.** 오늘 상장사 중 `bep_retreat: yes` 가 한 곳도 없어 **점수 영향은 0 이다.** 다음에 그 자리를 손댈 때 `손실률 밴드보다 앞선다` 를 `G1 통과와 손실률 밴드 둘 다보다 앞선다` 로 넓히고 TEN-RA6-01 의 범위에도 흑자 경우를 넣기를 권한다. 이번 실행을 막을 사유로 보지 않는다 — 문면이 좁을 뿐 틀리지 않았고, 근본 질문(전망이 측정된 실적을 덮어써도 되는가)은 이미 `open` 긴장으로 재검토 시점(2026-11)·비 Claude 재판정 확정과 함께 등록돼 있다.
- **[severity: low · 이월, 등록됨]** oracle F6 P1 = 25.967109 가 밴드 경계 25 에서 **+3.87%** 로 허용폭 3% 밖이라 경계 표시가 안 붙는다. 이 한 칸이 oracle 총점 2 와 3 을 가른다. C-27 에 alibaba G3(+3.32%)와 함께 표본 둘로 적혀 있다.
- **[severity: low · 이월, 등록됨]** `oracle.undrawn_credit.fix54` 가 null 인데 `calc_f9._runway` 의 `undrawn or 0.0` 이 0 으로 센다. C-04 가 완충을 `현금 + **확정** 미인출 여신` 으로 좁혀 설계대로이고, 뒤집히려면 39,769M 이상이 필요하다는 크기까지 관측 `basis.null_counts_as_zero` 에 적혀 있다. 보존 ORCL companyfacts 에 해당 태그 사실이 없어 `unverified` 라벨도 맞다.

## 확인 못 한 것

- **oracle B종 약정 250,000M 의 출처.** 보존 ORCL companyfacts 2026-05-31 시점 사실 전수에 대응 금액이 없다는 것까지만 확인했다. C-26 으로 등록돼 있고 커버리지 2.552 든 대안 47.937 이든 G4 step 0 이라 오늘 점수는 갈리지 않는다.
- **alibaba `nonop_share` 저장값 0.54 와 재계산 0.612415 의 차.** 규칙이 `가리지 못했다` 로 둔 자리이고 나도 가리지 못했다. 저장값에 `basis` 가 없어 어느 순이익·세전이익인지 복원할 수 없다. 둘 다 임계 0.30 위라 판정은 같다.
- **tsmc 20-F 원문 직접 대조.** `net_cash` 15줄은 관측 `basis.rows` 의 인용문과 US$ 칸 역검산(31.37)으로만 확인했고 보존 `tsm-20251231.htm` 를 열어 줄마다 맞추지는 않았다. alibaba 는 보존 20-F 를 실제로 열어 여섯 줄을 대조했다.
- **market_cap 12건·ntm_per 12건의 실측.** 전부 `legacy_unverified` 이고 원천 정책 밖 공급사 값이다. 엔진이 `unverified_inputs` 로 표시하고 점수를 깎지 않는 처리는 규칙대로이나 값 자체를 내가 확인한 것은 아니다.
- **비상장 두 곳의 `ps_ratio` 30.0·39.0.** v1.5 원문의 TTM 보정 추정치를 승계한 값이고 분기 매출 원자료가 없어 보정을 다시 하지 못했다. 구간 양 끝이 같은 밴드에 드는 것과 밴드 적용이 규칙대로인 것만 확인했다.
- **FIX-61~63 이 바꾼 규칙 문면의 규칙 일관성 검토.** 리뷰 템플릿이 적은 대로 그 영역은 8차 기록이고 이번 변경을 아직 보지 않았다. 나는 **재무 계산이 닿는 범위**(F9 우선순위 서술·C-06·C-07·C-29·TEN-RA6-01)만 확인했고 그 밖의 규칙 변경은 판정하지 않았다.
