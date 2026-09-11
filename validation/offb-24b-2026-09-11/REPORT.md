# OFFB-24B — SPCX·BABA 미개시 B종 약정과 AMZN AWS 백로그 실제 조사

- 지시 원문: `msg_dd6df1cddcf5` (run `run_1243c2a83479`)
- 배경: 설계진행 `583af3f` 의 `validation/missing-label-finding.md`
- 조사일: 2026-09-11. 원천은 `data.sec.gov`·`www.sec.gov` 만
- C-13 에 독립 배정됨. **상대 결과를 참조하거나 기다리지 않았다**

## 0. 결론

**셋 다 공시돼 있다. 찾았다.** `not_disclosed`·`parse_failed` 세 라벨이 전부 사실과 다르다.

| 대상 | 기존 라벨 | 실제 | 출처 |
|---|---|---|---|
| **SPCX** `offbalance_B` | `not_disclosed` / raw `"미확인"` | **총 $27,955M** (연도별 명세 있음) | 10-Q 2026-06-30 Note 16 |
| **BABA** `offbalance_B` | `not_disclosed` / raw `"미확인"` | **RMB 54,136M (US$7,848M)** 자본약정 + 기타약정 RMB 200,062M | 20-F FY2026 Note 27 |
| **AMZN** `contracted_revenue` | `parse_failed` / raw `"숫자 미공시"` | **약 $496 billion** (가중평균 잔여 6.4년) | 10-Q 2026-06-30 |

**따라서 `missing-label-finding.md` 의 결정 순서가 옳았다.** 찾아보니 있었고, C-16 을 먼저 정했더라면 **공시된 자료를 못 찾은 채 감점하거나 봐주는 일**이 실제로 벌어졌을 것이다.

**다만 찾았다고 바로 나눌 수는 없다.** 기간·범위·지급수단이 셋 다 다르다(§4). 특히 AMZN 의 $496B 는 **가중평균 6.4년**짜리 수입이고 약정표는 `Thereafter` 까지 뻗는다. 그대로 나누면 설계 지침 6.4 가 금지한 "기간·대상 자산·사업 범위가 다른 총액을 바로 나누는" 일이 된다.

**못 찾은 것이 하나 있다. BABA 의 계약 수입(RPO/백로그)이다.** 20-F 전문에서 `remaining performance obligation` 0건, `backlog` 0건이다. 이것은 **"이 문서에 없다"** 이지 **"회사가 어디에도 공시하지 않는다"** 가 아니다(§3.3).

## 1. SPCX — 찾았다

**출처.** 10-Q, 기간 2026-06-30, 제출 2026-08-04, accession `0001628280-26-052535`, `spcx-20260630.htm`.

**SPCX 는 10-K 가 아직 없다.** 정기보고서는 이 10-Q 하나뿐이고 나머지는 8-K 다(2026년 6월 상장). 지시서가 말한 "분기 이력이 짧다" 가 맞다.

### 1.1 B종 후보 — Note 16 Unconditional Obligations

> "The Company's unconditional obligations are **non-cancelable contractual commitments** primarily related to the Company's investments in **AI infrastructure and third-party cloud capacity arrangements** and other service arrangements. It also includes the Company's commitments under the **Spectrum Transaction, which are payable in cash and in the Company's Class A common stock.**"

**연도별 명세 (백만 달러, 2026-06-30 기준)**

| 기간 | 금액 |
|---|---:|
| 2026 (잔여 6개월) | 2,728 |
| 2027 | 22,244 |
| 2028 | 2,172 |
| 2029 | 809 |
| 2030 | 2 |
| Thereafter | (표기 없음) |
| **Total** | **27,955** |

**취소 조건**: `non-cancelable` 로 명시된다.
**대응 수입**: 이 표 자체에는 없다. 아래 백로그가 별도 항목이다.

**중요한 단서 둘.**
1. **전액이 현금 지출이 아니다.** Spectrum Transaction 분은 "payable in cash **and in the Company's Class A common stock**" 이다. 현금 소진 대비 커버리지에 쓰려면 현금 지급분만 분리해야 하는데 **그 분해는 이 주석에 없다.**
2. **2027년에 22,244 가 몰려 있다.** 총액의 80%다. 총액만 보면 이 편중이 사라진다.

### 1.2 계약 수입 — 백로그 공시됨

> "Backlog totaled **$ 47,461 million as of June 30, 2026**, of which **$ 14,286 million was recognized as deferred revenue** at June 30, 2026. Approximately **56 %** is expected to be recognized **within one year**."

정의도 함께 적혀 있다 — "transaction price of performance obligations to customers for which work remains to be performed", "Contracts are included in backlog when an **enforceable agreement** has been reached", 그리고 billed-and-delivered 분·옵션 구매·제약된 변동대가는 **제외**된다.

**이연수익 $14,286M 이 백로그 안에 포함돼 있다.** 둘을 더하면 중복이다.

### 1.3 C종(우발) — 참고

letters of credit $645M(전액 제한현금으로 담보), surety bonds $465M. 설계 지침 6.4 의 C종이므로 **현재 확정 현금 지출로 세지 않는다.**

## 2. BABA — 찾았다

**출처.** 20-F FY2026, 기간 2026-03-31, 제출 2026-05-20, `baba-20260331.htm`. **F6-FX-16 에서 이미 받아 둔 원문 스냅샷을 재사용했고 새로 받지 않았다.**

### 2.1 B종 후보 — Note 27 Commitments

**(a) Capital commitments — "contracted but not provided for"**

| 기간 | 2025-03-31 | **2026-03-31** |
|---|---:|---:|
| No later than 1 year | 44,067 | **53,484** |
| Later than 1 year and no later than 5 years | 1,254 | **652** |
| **합계 (RMB 백만)** | 45,321 | **54,136** |

본문이 USD 환산도 함께 준다 — **US$7,848 million**. `54,136 ÷ 7,848 = 6.898` 로 **F6-FX-16 에서 확인한 convenience translation 환율 RMB6.8980 과 일치**한다.

용도는 "capital expenditures contracted for purchase of property and equipment, including **the cloud infrastructure** and construction of corporate campuses" 다.

**(c) Other commitments** — co-location·bandwidth fees, licensed copyrights, marketing expenses

| 기간 | 2025-03-31 | **2026-03-31** |
|---|---:|---:|
| No later than 1 year | 32,364 | **57,441** |
| 1–5 years | 46,768 | **133,598** |
| More than 5 years | 5,094 | **9,023** |
| **합계 (RMB 백만)** | 84,226 | **200,062** |

**(b) Investment commitments** — RMB 14,501M (2026-03-31). "business combinations and equity investments", 주로 투자펀드 약정자본이다. **성격이 달라 B종에 넣을지는 판단 사항이다.** 영업용 미개시 약정이 아니라 투자 약정이다.

**B종을 무엇으로 잡느냐에 따라 총액이 크게 달라진다.**

| 조합 | RMB 백만 | 비고 |
|---|---:|---|
| (a) 자본약정만 | 54,136 | 가장 좁은 해석 |
| (a) + (c) 기타약정 | **254,198** | 영업 관련 미개시 확정 약정 |
| (a) + (b) + (c) | 268,699 | 투자 약정까지 포함 |

**여기서 정하지 않는다.** 어느 범위를 B종으로 볼지는 규칙 결정이다.

### 2.2 계약 수입 — 이 문서에서는 못 찾았다

20-F 전문(1,360,400자) 검색 결과다.

| 검색어 | 건수 |
|---|---:|
| `remaining performance obligation` | **0** |
| `backlog` | **0** |
| `purchase obligation` | 0 |
| `not yet commenced` | 0 |

§3.3 에서 이 결측을 분류한다.

## 3. AMZN — 찾았다

**출처.** 10-Q, 기간 2026-06-30, 제출 2026-07-31, accession `0001018724-26-000026`, `amzn-20260630.htm`.

### 3.1 계약 수입 — 숫자가 공시돼 있다

> "Additionally, we have performance obligations, **primarily related to AWS**, associated with commitments in customer contracts for future services that we expect to fulfill but have not yet been recognized in our financial statements. For contracts with **original terms that exceed one year**, those commitments not yet recognized were **approximately $496 billion as of June 30, 2026**. The **weighted-average remaining life of our long-term contracts is 6.4 years.**"

**기존 관측의 raw `"AWS 백로그(수백 $B급) — 숫자 미공시"` 는 사실과 다르다.** 숫자가 있다.

범위 단서 둘을 반드시 함께 기록해야 한다. **(가) 원계약 1년 초과분만이다.** 1년 이하 계약은 빠져 있다. **(나) 가중평균 잔여 6.4년이다.** 연도별 배분은 공시되지 않는다.

같은 문단이 덧붙인다 — Q1 2026 에 AWS·OpenAI 가 기존 $38.0B 약정을 **$100.0B / 8.0년** 확대, Q2 2026 에 AWS·Anthropic 이 **$100.0B 초과 / 10.0년** 확대를 발표했다. **이 둘이 $496B 에 포함됐는지는 본문이 명시하지 않는다.**

### 3.2 B종 후보 — 약정표에 `Leases not yet commenced` 가 별도 행으로 있다

**2026-06-30 기준, 백만 달러**

| 항목 | 2026잔여 | 2027 | 2028 | 2029 | 2030 | Thereafter | **Total** | 종별 |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| Operating lease liabilities | 9,336 | 14,765 | 13,924 | 12,599 | 11,269 | 54,457 | 116,350 | **A종(개시)** |
| Finance lease liabilities (이자 포함) | 1,088 | 1,775 | 1,885 | 1,482 | 1,269 | 9,161 | 16,660 | **A종(개시)** |
| Financing obligations (이자 포함) | 352 | 682 | 694 | 706 | 720 | 7,916 | 11,070 | A종 성격 |
| **Leases not yet commenced** | 4,018 | 11,732 | 9,278 | 9,483 | 9,227 | 93,476 | **137,214** | **B종** |
| **Unconditional purchase obligations** | 23,452 | 33,026 | 9,326 | 7,961 | 7,659 | 48,641 | **130,065** | **B종 후보** |
| Other commitments | 2,145 | 2,044 | 1,212 | 1,008 | 963 | 10,994 | 18,366 | 판단 필요 |
| **Total commitments** | 42,752 | 78,084 | 53,406 | 46,767 | 42,219 | 386,806 | **650,034** | 혼합 |

**`Leases not yet commenced` 는 설계 지침 6.4 의 B종 정의에 문언 그대로 대응한다.** 미개시 확정 약정이다.

`Unconditional purchase obligations` 각주가 범위를 밝힌다 — 에너지 조달, 디지털 미디어 콘텐츠 취득·라이선스, 유형자산 취득, 소프트웨어 라이선스이며 **"not reflected on the consolidated balance sheets"** 다. 변동 조건이나 규제 승인 대상인 계약은 최소수량·최소가격·해지위약금을 넘는 총액을 추정하지 않는다고 명시한다.

**기존 관측의 `offbalance_B = 106,000M` 은 위 어느 행과도 일치하지 않는다.** 137,214 도 130,065 도 아니다. **그 수치의 출처를 확인하지 못했다.** 기존 값을 정답으로 쓰지 말라는 조건에 따라 여기서 맞추려 하지 않고 불일치 사실만 적는다.

### 3.3 못 찾은 것의 분류 — 이번 과제의 핵심

지시하신 세 구분을 적용한다. **마지막을 첫째로 승격하지 않았다.**

| 항목 | 분류 | 근거 |
|---|---|---|
| SPCX B종 | **찾았다** | Note 16, 연도별 명세 포함 |
| SPCX 계약 수입 | **찾았다** | 백로그 $47,461M |
| BABA B종 | **찾았다** | Note 27(a)(c), 연도 구간별 명세 |
| AMZN 계약 수입 | **찾았다** | $496B, 6.4년 |
| AMZN B종 | **찾았다** | 약정표 2개 행 |
| **BABA 계약 수입** | **② 공시했는데 우리가 못 찾았다 / ③ 어느 쪽인지 모르겠다 — 둘 사이. ①(회사 미공시)로 단정하지 않는다** | 아래 |
| SPCX B종의 현금/주식 분해 | **③ 모르겠다** | 주석이 분해를 제공하지 않음. 다른 문서 미확인 |
| AMZN `offbalance_B` 106,000 의 출처 | **③ 모르겠다** | 어느 공시 행과도 불일치 |

**BABA 계약 수입을 ① 로 적지 않는 이유.** 검색한 것은 **FY2026 20-F 한 건**이다. 그 안에 RPO·backlog 표현이 0건인 것은 사실이나, (가) BABA 는 6-K 를 361건 제출하며 그중 분기 실적 자료를 확인하지 않았고, (나) US GAAP ASC 606 에는 잔여 이행의무 공시의 실무적 간편법이 있어 **원계약 1년 이하 계약은 공시 대상에서 빠질 수 있다.** BABA 매출이 단기 상거래 중심이라는 점과 정합적이지만 **그것을 확인한 것은 아니다.** 따라서 "20-F 에는 없다" 까지가 내가 말할 수 있는 전부다.

## 4. 찾았다고 바로 나눌 수 없는 이유

G4 커버리지 = 계약 수입 ÷ B종 약정인데, **셋 다 기준이 어긋난다.**

| 축 | SPCX | BABA | AMZN |
|---|---|---|---|
| 기준일 | 2026-06-30 | **2026-03-31** | 2026-06-30 |
| 보고 주기 | 분기(10-Q) | **연간(20-F)** | 분기(10-Q) |
| 통화 | USD | **RMB** (US$ 환산 병기) | USD |
| 약정 기간 | 2026~2030 (명세) | ≤1y / 1–5y / >5y (구간) | 2026~Thereafter (명세) |
| 수입 기간 | 백로그, 56% 1년 내 | **미확보** | **가중평균 6.4년** |

**세 가지 함정이 실재한다.**

1. **기간 불일치.** AMZN 은 6.4년짜리 수입을 `Thereafter` 까지 뻗는 약정과 나누게 된다. 설계 지침 6.4 가 금지한 바로 그 형태다.
2. **기준일 불일치.** BABA 만 3개월 이르다. F6-FX-16 에서 각 20-F 가 자기 해 기말환율로만 환산한다는 것을 확인했는데, **여기서도 같은 종류의 함정이 반복된다** — 기준일이 다른 총액을 같은 표에 놓으면 비교처럼 보인다.
3. **지급수단 불일치.** SPCX 약정의 일부는 주식으로 지급된다. 현금 소진 커버리지의 분모로 쓰려면 현금분만 남겨야 하는데 분해가 공시되지 않았다.

## 5. 산출물

| 파일 | 내용 |
|---|---|
| `REPORT.md` | 이 보고서 |
| `probe_filings.py`, `filings-index.json` | 세 기업 SEC 제출 이력 |
| `search_commitments.py` | 약정·계약수입 문구 검색 |
| `raw/SPCX-10Q-2026Q2.html`, `.txt` | SPCX 10-Q 원문 (2.27MB) |
| `raw/AMZN-10Q-2026Q2.html`, `.txt` | AMZN 10-Q 원문 (1.59MB) |
| `raw/sec-*-submissions.json` | 제출 이력 원문 |
| BABA 20-F | `validation/f6-fx-16-2026-09-10/raw/20F-BABA-FY2026.txt` **재사용(신규 수집 없음)** |

## 6. 조건 준수

- 원천은 `data.sec.gov`·`www.sec.gov` 만. 다른 host 0건
- **총액만 가져오지 않았다.** 계약 기간·연도별 지출·취소 조건·대응 수입을 각각 기록했고, 없는 항목은 없다고 적었다
- **찾은 것과 못 찾은 것을 분리**했고, 못 찾은 것은 ①회사 미공시 / ②우리가 못 찾음 / ③모르겠음 으로 구분했다. **③ 을 ① 로 승격하지 않았다**
- 예상을 사실로 쓰지 않았다. "SPCX 주석에 약정 항목이 있을 가능성" 은 가능성으로 두고 실제 원문에서 확인했다
- 기존 F9 점수·`v1.5` 표를 정답 fixture 로 쓰지 않았다. AMZN `offbalance_B` 106,000 불일치도 맞추려 하지 않고 불일치로 남겼다
- 점수·규칙·승인·원자료 변경 없음. `worker`·`C-13` 산출물은 읽기 전용
- C-13 결과를 참조하거나 기다리지 않았다
- BABA 20-F 는 기존 스냅샷을 재사용해 중복 수집을 피했다
