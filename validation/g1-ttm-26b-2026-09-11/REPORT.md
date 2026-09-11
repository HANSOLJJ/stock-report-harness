# G1-TTM-26B — alibaba FY2026 영업손익·매출 SEC 복원

- 지시 원문: `msg_e4f299aaf6b8` (run `run_1243c2a83479`)
- 조사일: 2026-09-11. 원천은 `data.sec.gov`·`www.sec.gov` 만
- C-13 에 독립 배정됨. **상대 결과를 참조하거나 기다리지 않았다**
- **신규 네트워크 수집 0건.** 이미 보존된 스냅샷만 사용했다(§5)

## 0. 결론

**셋 다 찾았다. 그리고 alibaba 는 FY2026 에 영업흑자다.**

| 항목 | CNY (보고통화) | USD (편의 환산) | 기간 |
|---|---:|---:|---|
| **매출** `us-gaap:Revenues` | **1,023,670,000,000** | 148,401,000,000 | 2025-04-01 ~ 2026-03-31 (364일) |
| **영업손익** `us-gaap:OperatingIncomeLoss` | **+50,150,000,000** | +7,270,000,000 | 동일 |
| **영업이익률** | **+0.04899 (+4.899%)** | +0.048989 | 동일 |

출처는 전부 **20-F, accession `0001193125-26-231755`, 제출 2026-05-20** 이다.

**G1 에 주는 답이 명확하다. `operating_result_reviewed` 는 `unknown` 이 아니라 `profit` 이다.** 영업손익이 양수(+RMB 50,150M, +4.899%)이므로 **G1 은 통과**하고 손실률 밴드(C-06)의 적용 대상이 아니다. alibaba 가 `pending_data` 였던 이유는 값이 없어서가 아니라 **관측에 등록되지 않았기 때문**이다.

**TTM 은 복원할 수 없다. 연간으로 가야 한다.** 분기 행이 **전 개념 전수에서 0건**이고, 그 부재를 회사가 20-F 에서 직접 설명한다(§2). 따라서 `period_basis = annual` 로 선언한다.

**통화 주의사항을 확인했다.** 영업이익률은 분자·분모가 같은 기간·같은 통화라 환율이 약분된다. 두 통화 값의 차이 `0.0000015` 는 **공시 USD 의 백만 단위 반올림 때문**이며 환산 자체의 문제가 아니다(§3.2 실증).

## 1. taxonomy 와 개념 이름 — 전제하지 않고 직접 확인

지시대로 F6-FX-16 의 확인값을 전제하지 않고 다시 셌다.

| taxonomy | 개념 수 | 단위 분포 |
|---|---:|---|
| **`us-gaap`** | **358** | CNY 317 · USD 138 · USD/shares 10 · shares 19 · CNY/shares 2 · pure 8 · 기타 |
| `dei` | 2 | shares 1 · pure 1 |
| `ifrs-full` | **0 (없음)** | — |

**BABA 는 `us-gaap` 이다.** `ifrs-full` 은 존재하지 않는다. (TSM 과 반대다 — F6-FX-16 에서 TSM 이 `ifrs-full` 임을 확인했다.)

**F9 G1 에 필요한 개념 이름**

| 용도 | 개념 | 단위 |
|---|---|---|
| 매출 | `us-gaap:Revenues` | CNY, USD |
| 영업손익 | `us-gaap:OperatingIncomeLoss` | CNY, USD |
| (참고) 매출원가 | `us-gaap:CostOfRevenue` | CNY, USD |
| 매출총이익 | `us-gaap:GrossProfit` — **없음** | — |

`GrossProfit` 은 태깅되지 않는다. 필요하면 `Revenues − CostOfRevenue` 로 유도해야 하며 그것은 유도값이다. 이번 과제에 필요하지 않아 계산하지 않았다.

## 2. 분기 행 부재 — 확인했고, 이유까지 찾았다

지시대로 "기억이지 확정 사실이 아니다" 를 전제하지 않고 직접 셌다.

### 2.1 전 개념 전수 집계

`us-gaap` 358개 + `dei` 2개 전체의 모든 관측을 기간 길이로 분류했다.

| 기간 길이 | 건수 |
|---|---:|
| 0~29일 | 8 |
| **80~100일 (분기)** | **0** |
| 180~209일 (반기) | 219 |
| 360~389일 (연간) | 5,333 |

**분기 관측이 단 1건도 없다.** 특정 개념의 문제가 아니라 파일 전체에 없다.

### 2.2 제출 이력이 같은 말을 한다

| 양식 | 건수 |
|---|---:|
| **10-Q** | **0** |
| 20-F | 12 |
| 6-K | 349 |

### 2.3 부재의 이유 — 회사가 직접 설명한다

**값 이름으로 0건을 확인하고 끝내지 않고, 부재를 설명하는 표현으로 다시 찾았다.** 20-F 원문에 있다.

> "We are also **not required under the U.S. Exchange Act to file periodic reports and financial statements with the SEC as frequently or as promptly as domestic U.S. companies**... For example, in addition to annual reports with audited financial statements, **domestic U.S. companies are required to file with the SEC quarterly reports that include interim financial statements** reviewed by an independent registered public accounting firm and certified by the companies' principal executive and financial officers. **By contrast, as a foreign private issuer, we are not re[quired]**..."

따라서 이 부재는 **`회사가 공시하지 않는다` 이고, 근거는 추정이 아니라 회사의 명시적 서술**이다. foreign private issuer 지위에서 나오는 구조적 면제이므로 **지속적**이다. 다만 "영구적" 이라고 단정하지는 않는다 — 지위가 바뀌면 달라진다.

### 2.4 반기 행이 있으나 TTM 에 쓸 수 없다

"연간만 있다" 는 정확하지 않다. **반기 관측이 219건 있다.** 다만 `Revenues`·`OperatingIncomeLoss` 기준으로 보면 쓸 수 없다.

| 개념 | 기간 | 값(CNY) | 출처 |
|---|---|---:|---|
| Revenues | 2019-04-01 ~ 2019-09-30 | 233,941,000,000 | 6-K, filed **2021-02-02** |
| Revenues | 2020-04-01 ~ 2020-09-30 | 308,810,000,000 | 6-K, filed **2021-02-02** |
| OperatingIncomeLoss | 2019-04-01 ~ 2019-09-30 | 44,739,000,000 | 6-K, filed 2021-02-02 |
| OperatingIncomeLoss | 2020-04-01 ~ 2020-09-30 | 48,339,000,000 | 6-K, filed 2021-02-02 |

**2019·2020 두 시점뿐이고 전부 2021-02-02 제출 6-K 하나에서 왔다.** 유지되는 시계열이 아니다. FY2026 근처에는 반기 행이 없으므로 **반기를 이어 붙인 TTM 복원도 불가능하다.**

## 3. FY2026 값과 영업이익률

### 3.1 원값

| 개념 | 단위 | 기간 | 값 | form | filed | accession |
|---|---|---|---:|---|---|---|
| `Revenues` | CNY | 2025-04-01~2026-03-31 (364일) | 1,023,670,000,000 | 20-F | 2026-05-20 | 0001193125-26-231755 |
| `Revenues` | USD | 동일 | 148,401,000,000 | 20-F | 2026-05-20 | 동일 |
| `OperatingIncomeLoss` | CNY | 동일 | **50,150,000,000** | 20-F | 2026-05-20 | 동일 |
| `OperatingIncomeLoss` | USD | 동일 | 7,270,000,000 | 20-F | 2026-05-20 | 동일 |

기간이 364일이다. BABA 회계연도는 3월 말 종료이고 FY2026 은 2025-04-01 부터다.

### 3.2 영업이익률과 환율 약분 실증

```
CNY  50,150,000,000 / 1,023,670,000,000 = 0.0489903973  (4.8990%)
USD   7,270,000,000 /   148,401,000,000 = 0.0489888882  (4.8989%)
차이                                    = 0.0000015091  (0.000151%p)
```

**차이의 원인은 환산이 아니라 공시 USD 의 반올림이다.** 내재환율 6.8980(F6-FX-16 에서 확인한 convenience translation 환율)으로 역산하면 이렇다.

```
매출   1,023,670 / 6.8980 = 148,400.986 백만  → 공시 148,401 (반올림)
영업익    50,150 / 6.8980 =   7,270.223 백만  → 공시   7,270 (반올림)

반올림 전 값으로 계산한 영업이익률 = 0.0489903973
                        CNY 영업이익률 = 0.0489903973   → 소수 12자리까지 일치
```

**즉 환율은 완전히 약분된다.** 지시하신 "분자와 분모가 같은 통화이므로 환율이 약분되지만 그 사실을 근거란에 적으라" 를 실측으로 채웠다.

**그러므로 영업이익률은 CNY 값 `0.04899` 를 쓴다.** 공시 USD 로 계산하면 반올림 오차가 섞인다. F6-FX-16 에서 확인한 "연도별 환율이 다르므로 공시 USD 로 성장률을 계산하면 왜곡된다" 는 **비율(같은 기간 내 나눗셈)에는 해당하지 않지만**, 반올림 때문에 굳이 USD 를 쓸 이유가 없다.

## 4. 찾은 것과 못 찾은 것

| 항목 | 판정 | 근거 |
|---|---|---|
| FY2026 연간 영업손익 | **찾았다** | `us-gaap:OperatingIncomeLoss` CNY 50,150,000,000 |
| FY2026 연간 매출 | **찾았다** | `us-gaap:Revenues` CNY 1,023,670,000,000 |
| FY2026 영업이익률 | **찾았다(계산)** | 0.0489903973, 두 통화 교차 검증 |
| taxonomy·개념 이름 | **찾았다** | `us-gaap`, 358 개념, `ifrs-full` 0 |
| 통화 | **찾았다** | 보고통화 CNY, 편의환산 USD, 내재환율 6.8980 |
| **분기 행 / TTM** | **① 회사가 공시하지 않는다 (확정)** | 전 개념 0건 + 10-Q 0건 + **20-F 원문의 foreign private issuer 면제 서술** |
| `GrossProfit` | **① 회사가 이 개념으로 태깅하지 않는다** | 개념 자체 부재. `Revenues − CostOfRevenue` 유도는 가능하나 유도값 |
| FY2026 이후 반기 데이터 | **② 우리가 못 찾았다 / ③ 모르겠다** | 반기 관측은 2019·2020 뿐. 6-K 349건 중 최근분 미확인 |

**③ 을 ① 로 승격하지 않았다.** 분기 부재만 ① 로 확정했고 그 근거는 회사의 명시적 서술이다.

## 5. 신규 수집을 하지 않은 이유

지시서가 "밖에서 찾기 전에 보존된 파일부터 열라" 고 했고, 그대로 했다. **네트워크 호출 0건이다.**

| 사용한 파일 | 출처 과제 |
|---|---|
| `validation/f6-fx-16-2026-09-10/raw/sec-BABA-companyfacts.json` | F6-FX-16 (내 워크트리) |
| `validation/f6-fx-16-2026-09-10/raw/20F-BABA-FY2026.txt` | F6-FX-16 (내 워크트리) |
| `validation/offb-24b-2026-09-11/raw/sec-BABA-submissions.json` | OFFB-24B (내 워크트리) |

C-13 의 `f6-avail-15b/_raw/CIK0001577552_BABA.json` 은 **열지 않았다.** 내 워크트리에 같은 성격의 스냅샷이 이미 있었고, 상대 산출물을 참조하지 말라는 조건과 겹치지 않게 하기 위해서다. 필요하면 교차 검증용으로 열 수 있다.

## 6. 관측 등록 제안 (등록하지 않았음)

점수·원자료 변경 금지 조건에 따라 **제안만 한다.**

```
alibaba.operating_income_ttm  → value 50150000000  unit CNY  period_basis annual
                                period 2025-04-01~2026-03-31  status ok
                                source 20-F 0001193125-26-231755 (filed 2026-05-20)
alibaba.revenue_ttm           → value 1023670000000  unit CNY  period_basis annual
                                (동일 기간·출처)
alibaba.operating_margin_ttm  → value 0.0489903973  unit pure  period_basis annual
                                note "CNY 기준. 분자·분모 동일 기간·동일 통화로 환율 약분.
                                      공시 USD 로 계산하면 반올림 오차 1.5e-6 발생"
```

**`period_basis` 를 반드시 `annual` 로 남겨야 한다.** 지표명이 `_ttm` 인데 실제로는 연간이므로, 이름만 보고 TTM 으로 오인할 위험이 있다. 다른 10개사는 TTM 트랙이라 **같은 필드에 다른 기간 정의가 섞인다.**

`operating_result_reviewed` 는 검토 입력이므로 내가 정하지 않는다. 다만 **영업손익이 양수라는 사실은 확정**이다.

## 7. 역추적 대조

보고서의 단정을 내 산출물과 대조했다.

| 단정 | 대조 |
|---|---|
| 매출 CNY 1,023,670,000,000 | `baba-g1-extract.json` → `fy2026.Revenues.CNY.val` |
| 영업손익 CNY 50,150,000,000 | 동 `fy2026.OperatingIncomeLoss.CNY.val` |
| 영업이익률 0.0489903973 | 동 `margins.CNY.operating_margin` |
| 분기 0건 | `verify_no_quarterly.py` A절 히스토그램 |
| 10-Q 0건 | 동 B절, `sec-BABA-submissions.json` 기준 |
| 면제 서술 | 동 C절, 20-F 원문 인용 |
| taxonomy us-gaap 358 | `extract_baba_g1.py` A절 |
| 내재환율 6.8980 | `extract_baba_g1.py` D절 |

## 8. 산출물과 조건 준수

| 파일 | 내용 |
|---|---|
| `REPORT.md` | 이 보고서 |
| `extract_baba_g1.py`, `baba-g1-extract.json` | taxonomy·FY2026 값·영업이익률 |
| `verify_no_quarterly.py` | 분기 부재 전수 확인 + 부재 이유 원문 검색 |

- 원천은 `data.sec.gov`·`www.sec.gov` 만. **이번 과제에서 신규 호출 0건**
- 분기 부재와 taxonomy 를 전제하지 않고 직접 확인했다
- **통화를 남겼다.** 보고통화 CNY, 편의환산 USD, 내재환율, 반올림 영향까지 기록
- 못 찾은 것은 ①②③ 으로 구분했고 ③ 을 ① 로 승격하지 않았다
- **값이 없을 때 값 이름 검색으로 끝내지 않고 부재 설명 표현으로 재검색**해 회사의 면제 서술을 찾았다
- 기존 F9 점수·`v1.5` 표를 정답 fixture 로 쓰지 않았다
- 점수·규칙·승인·원자료 변경 없음. 관측 등록은 제안만 했다
- 다른 워크트리 산출물은 읽기 전용. C-13 결과를 참조하거나 기다리지 않았다
- anthropic 은 범위에서 제외했다
