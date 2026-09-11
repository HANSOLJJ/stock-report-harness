# OBS-REG-25 — 실측 관측 등록·교체와 coverage_comparable 판정

작성일 2026-09-11. 담당 worker(HANSOLJJ/worker). 요청 `msg_e3e7320d8227` + `msg_87e5e0ba5488`(G1-TTM-26 추가분).
선행 설계진행 `9c546e2` `validation/offb-24-review.md`. 원자료 C-13 `3cf9799` · `HANSOLJJ/C-13`.

## 결론

**과제 넷 다 끝냈습니다. 그리고 승인을 막는 것이 하나 나왔습니다 — v1.7 로 돌리면 F6 가 14개사 전부 미완료입니다.**

| | 결과 |
|---|---|
| 지시값 대조 | **34건 · 불일치 0건.** 보존 SEC 원문에서 직접 재확인 |
| 문면 차이 | **2건** — AMZN 각주(3)는 원문에 있고, BABA 간편법은 Note 2(t)가 아니라 **2(g)** (4 절) |
| 관측 | 신규 **9건**(지시 6 + alibaba 3) · 승계 대체 표시 **6건** |
| 판정 | `coverage_comparable` **3건** yes · alibaba `operating_result_reviewed` **profit** |
| 새 실행 | `ai-scorecard-2026-09-obsreg` (v1.7 · C-05 apply · C-06 proposed_v15_boundaries) |
| 예상 대조 | **셋 다 맞습니다** — openai −5→−4, spacex-xai 값 나옴, amazon 값 나옴 (6 절) |
| **승인 차단** | **v1.7 F6 가 전 기업 pending — 순위 0개사.** 관측 등록과 무관한 규칙 쪽 원인 (7 절) |
| 승인 실행 | **6종 해시 전부 불변** (8 절) |

신규 네트워크 호출 없음. `api.nasdaq.com` 미호출. `v1.5`·승인 실행 파일 미변경.

---

## 1. 지시값을 원문에서 다시 뽑았습니다

`verify_values.py` 가 형제 워크트리의 **커밋**에서 blob 을 직접 읽어(`git show <commit>:<path>`) 문면을 다시 뽑습니다. 작업 트리 상태에 기대지 않고 sha256 을 같이 찍어 다음 사람이 같은 바이트를 봤는지 확인할 수 있게 했습니다.

```
대조 34건 · 불일치 0건
```

| 항목 | 지시값 | 원문 |
|---|---|---|
| SPCX 백로그 | 47,461 / 2026-06-30 / Note 3 | `Backlog totaled $ 47,461 million as of June 30, 2026` · `Note 3 - Revenue` ✅ |
| SPCX 구매약정 | 27,955 | `Total $ 27,955` · 연도별 2,728/22,244/2,172/809/2 · non-cancelable ✅ |
| SPCX 미개시 리스 | 1,627 / 2025-12-31 | S-1/A `$1,627 million ... average lease term of 7.2 years` · **as of December 31, 2025** ✅ |
| AMZN RPO | 약 496B / 2026-06-30 / Note 1 | `approximately $ 496 billion as of June 30, 2026` · `Note 1 — ACCOUNTING POLICIES` ✅ |
| AMZN 약정표 | 137,214 · 130,065 | 같은 표에 18,366 과 총계 650,034 까지 ✅ |
| BABA 약정 | 54,136 + 200,062, 투자 14,501 제외 | Note 27(a)/(c)/(b) ✅ |
| BABA 계약수입 | 미공시 (ASC 606 면제) | 간편법 선언 문면 확인 · 전문에 RPO·backlog·not yet commenced **0건** ✅ |
| alibaba FY2026 | 매출 1,023,670 / 영업이익 50,150 CNY | companyfacts `us-gaap:Revenues`·`OperatingIncomeLoss`, accession `0001193125-26-231755` ✅ |

alibaba 영업이익률 **+4.899%** 입니다(50,150 / 1,023,670). USD 편의환산으로 계산해도 7,270/148,401 = 4.899% 로 같습니다.

---

## 2. 판단이 필요했던 둘

### 2.1 SPCX — 기준일이 섞인 합계

**단일 관측 + `basis.components` 로 갔습니다.** 구성요소를 관측 둘로 쪼갤 수 없습니다.

> `ObsLookup.number()` 는 기업·지표당 값을 **하나만** 돌려줍니다. 둘로 두면 한쪽이 조용히 버려집니다.

그래서 합계 29,582 을 값으로 두고 `basis` 에 이렇게 남겼습니다.

```json
"basis": {
  "measured_as_of": "2026-06-30", "aggregation": "sum_of_components", "mixed_as_of": true,
  "components": [
    {"label": "미개시 운용리스", "value": 1627000000, "as_of": "2025-12-31",
     "source_id": "SRC-SEC-SPCX-S1A-2026", "location": "S-1/A Note 11 Leases (F-36)",
     "note": "10-Q 에는 이 수치가 없다. 10-Q 는 리스 포트폴리오에 중요한 변동이 없다고만 적는다"},
    {"label": "무조건적 비취소 구매약정", "value": 27955000000, "as_of": "2026-06-30",
     "by_year": {"2027": 22244, "...": "..."},
     "note": "Spectrum 거래분은 현금과 Class A 보통주 혼합 지급이고 분해가 미공시다"}],
  "as_of_span": {"earliest": "2025-12-31", "latest": "2026-06-30", "stale_component_share": 0.055}
}
```

**합계만 남고 섞였다는 사실이 사라지는 형태가 아닙니다.** 합계를 읽는 쪽(엔진)은 값을 얻고, 감사하는 쪽은 `mixed_as_of: true` 와 구성요소별 기준일을 봅니다.

### 2.2 BABA — 통화

**스키마가 `unit == METRICS[metric]["unit"]` 를 강제합니다.** `offbalance_B` 의 단위는 `USD` 이고, `unit: "RMB"` 는 검증에서 걸립니다. RMB 를 그대로 둘 자리가 없습니다.

**20-F 가 스스로 선언한 환율로 환산하고 원 통화를 `basis` 에 남겼습니다.**

> Unless otherwise stated, all translations of Renminbi ... were made at a rate of **RMB6.8980 to US$1.00** ... the respective exchange rates on March 31, 2026 set forth in the **H.10 statistical release of the Federal Reserve Board**

**외부 환율 출처를 쓰지 않았습니다.** 환산 근거가 문서 안에 있고, 두 가지로 검산됩니다.

| 검산 | 결과 |
|---|---|
| 20-F 가 자본약정 RMB54,136M 을 US$7,848M 으로 스스로 환산 | 54,136 / 6.8980 = **7,848.07** ✅ |
| companyfacts FY2026 Revenues CNY 1,023,670M / USD 148,401M 역산 | **6.8980** ✅ |

RMB254,198M → **US$36,851M**(백만 단위 반올림, 20-F 편의환산 표기와 같은 자리). `basis` 에 `original_currency: "CNY"` · `original_value` · `fx_rate` · `fx_rate_source` 를 전부 남겼습니다. **통화가 사라지지 않습니다.**

같은 이유로 alibaba 의 매출·영업이익도 **20-F 자체 편의환산값**(companyfacts 의 USD 단위 값)을 썼습니다. 우리가 환산한 값이 아닙니다.

---

## 3. 작업 중 찾은 결함 하나 — `as_of` 는 기준일이 아닙니다

**처음에 `as_of` 에 공시 기준일(2026-06-30 등)을 넣었더니 새 관측이 엔진에 닿지 않았습니다.**

```python
# inputs.py — 기업별 관측을 지표로 조회한다. 같은 지표가 여럿이면 verified 를 우선하고, 그다음 as_of 최신을 고른다
def key(obs): return (2 if status == "verified" else 1 if "legacy_unverified" else 0), obs["as_of"]
```

`as_of` 는 **최신성 키**입니다. `alibaba.contracted_revenue` 는 값이 없어 `status` 등급이 0 이고, 기준일 `2026-03-31` 이 승계 관측의 `2026-09-02` 보다 **작아서 승계 쪽이 뽑혔습니다.** 그 결과 새로 붙인 `missing_type: not_disclosed_confirmed` 가 `_g4` 에 닿지 않고 `결측유형 미분류` 로 떨어졌습니다.

**고친 형태** — `as_of` 는 **원문을 연 날**(2026-09-11), 공시 기준일은 `basis.measured_as_of`. 승계 관측이 전부 `as_of: "2026-09-02"`(기준선 날짜)인 것과도 맞습니다.

자료 자체는 전부 정보 컷오프(2026-09-02) 이전 접수분입니다 — 10-Q 2026-08-04 · 20-F 2026-05-20 · S-1/A 2026-06-03.

**이건 `missing_type` 이 도입되면서 새로 생긴 함정입니다.** 값이 있는 관측은 `verified` 등급으로 승계를 이기지만, **값이 없는 교체 관측은 `as_of` 로만 이깁니다.** 라벨만 바꾸는 교체가 앞으로도 생길 테니 보고 대상으로 남깁니다.

---

## 4. 지시서와 다른 것 둘 — 숫자는 아니고 문면입니다

**숫자는 전부 일치합니다.** 다음 둘은 근거 표기 쪽입니다.

### 4.1 AMZN `Other commitments` 각주 (3) 는 원문에 있습니다

지시서는 "각주 3의 내용을 확인하지 못했으므로 넣지 마십시오" 라고 했는데, 10-Q 본문에 그대로 있습니다.

> (3) Includes **asset retirement obligations**, the estimated timing and amounts of payments for **rent and tenant improvements associated with build-to-suit lease arrangements that are under construction**, and liabilities associated with **digital media content agreements with initial terms greater than one year**. Excludes approximately $ 7.1 billion of income tax contingencies ...

**지시대로 18,366 을 제외해 등록했습니다.** 임의로 넣지 않았습니다. 다만 제외 사유가 해소됐으니 판단을 요청합니다.

| | 값 | 커버리지 |
|---|---|---|
| 현재 등록 (137,214 + 130,065) | 267,279 | **1.856** |
| 18,366 을 넣으면 | 285,645 | 1.736 |

제 의견은 **넣는 쪽**입니다. 세 항목 다 미래 현금 유출 약정이고 G4 가 묻는 것이 미래 지출 전체입니다. 넣으면 분모가 커져 커버리지가 낮아지므로 **우리에게 불리한 방향**이기도 합니다. 다만 소득세 우발채무 7.1B 는 원문이 명시적으로 제외하고 있어 그건 애초에 들어 있지 않습니다. `basis.excluded[0]` 에 각주 전문과 `if_included: 285,645` 를 같이 남겨 뒀으니 결정만 주시면 한 줄입니다.

### 4.2 BABA ASC 606 간편법은 Note 2(t) 가 아니라 **2(g)** 입니다

쪽수(F-21)와 문면은 지시서와 같습니다. 소항목 문자만 다릅니다 — 선언은 **`2. Summary of significant accounting policies` 의 `(g) Revenue recognition`** 안 `Practical expedients and exemptions` 문단입니다. (g) 와 문단 사이에 다른 소항목 머리글이 없음을 기계로 확인했습니다. 관측 `basis.location` 에 `2(g)` 로 적고 `note_on_location` 에 차이를 남겼습니다.

**면제의 한계도 같이 적었습니다.** 선언된 면제는 1년 이하 계약과 청구권 기준 계약만 덮습니다. 1년 초과 계약분은 면제로 설명되지 않고 Note 5 의 "중요하지 않다" 서술이 그 자리를 메웁니다. 6-K 361건은 확인하지 않았습니다.

---

## 5. `coverage_comparable` 을 판단 쪽에 어떻게 넣었나

세 기업의 F9 판단을 `status: "new"` 로 교체하고 `previous_judgment_id` 로 승계 판단을 가리킵니다. 근거는 **지우지 않고 덧붙였습니다** — 기존 evidence 뒤에 판정 근거와 판정 주체를 추가합니다.

| 기업 | `coverage_comparable` | 커버리지 | 근거란에 남긴 것 |
|---|---|---|---|
| spacex-xai | `yes` | **1.604** | 기준일 혼재(분모 5.5%) · 주식 지급분 미분해 · 2027 편중 80% · 백로그 내 이연수익 14,286 · **그럼에도 yes 인 이유**(주식 지급분은 분모를 키워 보수적) |
| amazon | `yes` | **1.856** | 분자 과소(1년 초과분만) · 분모 과대(Thereafter 포함) · **양쪽 편의가 다 보수적** · 분모 선택(미개시 리스만 쓰면 3.615) |
| alibaba | `yes` | — | **분모만 있고 분자가 없다.** 판정의 뜻은 "두 수치가 확보됐다면 비교 가능" 이고 분자 부재는 별개 사실 |

alibaba 는 `operating_result_reviewed: "profit"` 도 같이 넣었습니다. 근거란에 **연간 기준이라는 한계는 F6 P4 가 이미 한 칸 내리므로 F9 에서 다시 세지 않는다**고 적었습니다.

### 5.1 물으신 것 — 필드를 갈라야 하나

**지금은 가르지 마십시오. 다만 이름이 틀렸습니다.**

`coverage_comparable` 은 이름이 "비교 가능한가" 인데 실제로는 **"결측 유형 분기까지 내려갈 자격이 있는가"** 라는 관문으로 쓰이고 있습니다. BABA 가 그걸 드러냅니다 — 분자가 아예 없는데 `yes` 를 줘야 C-16 이 제 일을 합니다.

가르지 말자는 이유는 셋입니다.

1. **가르면 `_g4` 가 두 관문이 됩니다.** `comparable` 과 `both_present` 를 따로 물으면 분기가 넷이 되고, 지금 하나로 충분한 판정을 사람이 두 번 하게 됩니다.
2. **자료 보유 여부는 이미 관측이 말합니다.** `contracted_revenue` 가 `None` 인지 아닌지가 그 답이고, `missing_type` 이 그 이유까지 말합니다. **필드를 새로 만들면 같은 사실을 두 곳에서 관리하게 됩니다** — 어긋나면 어느 쪽이 참인지 규칙이 없습니다.
3. MISS-LABEL-23 에서 배운 것과 같은 형태입니다. **한 라벨이 두 뜻을 담으면 가르되, 이미 다른 데서 말하고 있는 것을 복제하지는 않습니다.**

**대신 이름과 주석을 고치는 쪽을 제안합니다.** `coverage_comparable` → `coverage_basis_comparable` 로 두고, 정책 주석에 "**두 수치가 확보됐다면** 같은 범위·기간으로 비교 가능한가를 묻는다. 자료 보유 여부는 묻지 않는다" 를 박습니다. 지금 근거란으로 구분하는 것과 뜻은 같은데, **다음 사람이 근거란을 안 읽어도 이름에서 압니다.** 이번에 고치지 않았습니다.

---

## 6. 점수 영향 — 예상과 대조

바꾼 것이 셋(결정·관측·규칙)이라 한 번에 비교하면 원인이 섞입니다. **네 열로 갈랐습니다**(`compare_scores.py`).

```
A   승인 실행       v1.5 · 승계 관측 · 결정 없음
A'  결정만          v1.5 · 승계 관측 · C-05 apply, C-06
B   관측까지        v1.5 · 새 관측·판단 · 결정
C   새 실행         v1.7 · 새 관측·판단 · 결정
```

### 6.1 A→A' — C-05·C-06 확정의 효과

| 기업 | 전 | 후 |
|---|---|---|
| spacex-xai F9 | `needs_rule_decision(C-06)` | `needs_judgment` |

**결정만으로는 값이 나오지 않습니다.** C-06 이 풀리자 다음 관문인 `coverage_comparable` 에서 멈춥니다.

### 6.2 A'→B — 관측 등록·판정 기록의 효과 *(이번 과제의 몫)*

| 기업 | 전 | 후 |
|---|---|---|
| **amazon F9** | `needs_judgment` | **−2** |
| **spacex-xai F9** | `needs_judgment` | **−4** |
| **alibaba F9** | `pending_data` | **`needs_rule_decision(C-16)`** |

**순위가 9개사에서 11개사로 늘어납니다.** amazon 이 2위(조정 16), spacex-xai 가 7위(조정 6)로 들어옵니다.

alibaba 는 **C-16 하나만 남습니다** — 회신에 적으신 그대로입니다. G1 통과(+4.899%) → G2 FCF 음수 −2 → G3 런웨이 → G4 에서 C-16 이 가릅니다.

### 6.3 B→C — 규칙 v1.7 전환의 효과

| 기업 | 전 | 후 |
|---|---|---|
| **openai F9** | −5 | **−4** |
| **spacex-xai F9** | −4 | **−3** |
| F6 12개사 | 값 또는 `rule(C-13)` | **전부 `pending_data`** |
| F6 anthropic·openai | 승계 −3 · −4 | **`rule(C-12)`** |

### 6.4 예상과의 대조

| 예상 | 결과 |
|---|---|
| openai −5 → −4 | ✅ **맞습니다.** 단 원인은 관측이 아니라 **C-06 재척도**입니다(B→C) |
| spacex-xai `needs_rule_decision` → 값 | ✅ **맞습니다.** v1.5+결정에서 **−4**, v1.7 에서 **−3** |
| amazon `needs_judgment` → 값 | ✅ **맞습니다. −2** |

**셋 다 맞았습니다.** 다만 spacex-xai 와 openai 의 변화는 **관측 등록이 아니라 C-06 재척도가 만든 것**이라 원인이 다릅니다. 관측 등록이 단독으로 만든 것은 amazon −2 와 spacex-xai 의 `needs_judgment` 해소, alibaba 의 C-16 도달 셋입니다.

---

## 7. 승인을 막는 것 — v1.7 F6 가 전 기업 미완료입니다

```
C  새 실행(v1.7·새 관측) — 완주 0/14개사
   (완주 0개사 — 순위를 만들지 않는다)
```

**관측 등록 때문이 아닙니다.** B(v1.5·같은 관측)에서는 11개사가 완주합니다. 원인은 규칙 쪽입니다.

| 사유 | 기업 |
|---|---|
| `revenue_ttm 관측에 basis.period_basis 가 없음` | 상장 11개사 |
| `P1 입력 net_income_ttm 관측 없음; P3 입력 revenue_ttm_prior 관측 없음` | alibaba (period_basis 는 이번에 넣었습니다) |
| `비상장 F6 밴드 미정 (C-12)` | anthropic · openai |

**v1.7 의 F6 파라미터 모드는 관측 넷을 요구하는데 그중 셋이 어느 실행에도 등록된 적이 없습니다.**

| 입력 | 지금 상태 |
|---|---|
| `revenue_ttm` | 있으나 **`basis.period_basis` 선언이 없음**(승계 관측) |
| `net_income_ttm` | **관측 없음** (v1.7 신설) |
| `revenue_ttm_prior` | **관측 없음** (v1.7 신설) |
| `operating_income_ttm` | 일부만 |

**필요한 값은 이미 계산돼 있습니다.** `validation/f6-spec-18/collect_ttm.py` 가 보존된 SEC `companyfacts` 로 12개사 TTM 을 재구성했고 `score_check.py` 가 실제 `compute_f6` 로 **9/9 일치**를 확인했습니다. 관측으로 등록만 안 된 상태입니다.

**이번 과제 범위가 아니라 등록하지 않았습니다.** 지시서는 관측 6건(+alibaba 3건)을 명시했고 14개사 × 4지표는 다른 과제 몫입니다. 다만 **이대로는 "승인 직전" 이 아닙니다** — 순위가 0개사인 실행을 승인할 수는 없습니다. 셋 중 하나를 골라 주십시오.

1. **F6 입력 등록 과제를 하나 더 배정한다** (제 의견). `collect_ttm.py` 출력이 있으므로 신규 수집 없이 12개사가 채워집니다. 남는 것은 C-12(비상장 밴드) 둘.
2. **새 실행을 v1.5 로 둔다.** 관측 등록 효과만 반영하고 v1.7 전환은 F6 입력이 갖춰진 뒤로 미룹니다. 그러면 지금 바로 11개사 순위가 나옵니다(6.2 의 B 열).
3. **v1.7 로 두고 F6 전면 미완료 상태로 승인한다.** 권하지 않습니다.

---

## 8. 반영 경로와 해시

**기존 실행 `ai-scorecard-2026-09-baseline` 의 파일은 하나도 고치지 않았습니다.**

| 대상 | 승인된 baseline | 현재 baseline | 새 실행 |
|---|---|---|---|
| `rules` | `9231b3a05ba5c766…` | **동일** | `cc820f2dfa629498…` (v1.7) |
| `observations` | `37435ae2989236f5…` | **동일** | `9b84660fc5c4b1ea…` |
| `judgments` | `685069767e0cf919…` | **동일** | `5dc79ac34c617267…` |
| `run` | `50b063a5a12e84a6…` | **동일** | `6107eea3b0cedf62…` |
| `results` | `0942c342f010781e…` | **동일** | `9bb47f1c5d463185…` |
| `draft` | `574841bc7c26f225…` | **동일** | `412da9d2327c5273…` |

여섯 전부 새 실행에서 바뀝니다. 당연합니다 — 규칙·관측·판단·결정이 다 달라졌습니다. **중요한 것은 왼쪽 두 열이 같다는 것**이고, 그것이 승인된 실행이 그대로 보존됐다는 뜻입니다.

**승인은 하지 않았습니다.** `score-approve` 는 사용자 지시가 있어야 도는 명령이고, 지금은 7 절의 결정이 먼저입니다.

### 8.1 승계 관측을 지우지 않았습니다

교체 대상 6건은 남겨 두고 `note` 앞에 `[OBS-REG-25 대체됨 → <새 관측 id>]` 를 붙였습니다. `ObsLookup` 이 `verified` 를 `legacy_unverified` 보다 우선하므로 계산에는 새 값이 쓰이고 이력은 보존됩니다.

한 가지 예외 상황이 3 절입니다 — **값이 없는 교체 관측은 등급으로 이기지 못하고 `as_of` 로만 이깁니다.**

### 8.2 새 실행과 승인 실행의 관측 차이 14건은 제 것이 아닙니다

`init` 이 기준선 v1.5 에서 승계하는데, 그 기준선의 `runway_years` 14건이 `not_disclosed` → `not_applicable` 로 이미 바뀌어 있습니다(앞선 과제 결과). 점수에는 영향이 없습니다(6.1 의 A→A' 에 나타나지 않습니다). **제가 만든 차이가 아니라는 것만 적어 둡니다.**

---

## 9. 확인된 것과 미확인인 것

### 9.1 확인된 것

1. 지시값 **34건 대조 · 불일치 0건**. 보존 SEC 원문 직접 확인.
2. AMZN 각주(3) 본문은 **원문에 있다**. BABA 간편법은 **Note 2(g)** 다.
3. BABA 환산 근거는 **20-F 자체 선언**(RMB6.8980, 연준 H.10)이고 문서 자체로 두 번 검산된다.
4. `as_of` 는 기준일이 아니라 **최신성 키**다. 값 없는 교체 관측은 여기에 걸린다.
5. 예상 셋 다 맞았고, 그중 둘은 **원인이 관측이 아니라 C-06 재척도**다.
6. 관측 등록만으로 순위가 **9 → 11개사**가 된다.
7. alibaba 에 남는 것은 **C-16 하나**다.
8. **v1.7 F6 는 전 기업 미완료**이고 원인은 등록된 적 없는 입력 셋이다.
9. 승인 대상 **6종 전부 보존**.

### 9.2 미확인 — 추측하지 않습니다

1. **AMZN `Other commitments` 18,366 의 포함 여부.** 각주는 확인했으나 결정은 설계진행 몫이라 제외한 채 뒀습니다(4.1).
2. **BABA 미개시 리스.** 20-F 에 `not yet commenced` 0건이나 미공시인지 중요성 미달인지 갈리지 않습니다. `basis.not_disclosed` 에 그대로 적었습니다.
3. **BABA 6-K 361건.** 확인하지 않았습니다.
4. **alibaba `fcf_ttm` −11.4B 와 `cash` 56.8B 가 여전히 `legacy_unverified` 이고 기간 정의가 없습니다.** 런웨이 4.98년이 G3 무감점을 만드는데 근거가 legacy 입니다. **영업손익을 연간으로 선언한 이상 이 둘도 같은 연간 기준으로 다시 뽑아야 합니다.** 이번에 고치지 않았고 `run.assumptions` 에도 적어 뒀습니다.
5. **SPCX 약정의 현금/주식 분해.** 미공시입니다.

## 10. 재현 방법

```bash
python validation/obs-reg-25/verify_values.py        # 지시값 대조 34건
python scripts/scorecard_cli.py init ai-scorecard-2026-09-obsreg --rule v1.7 ...  # 실행 생성
python validation/obs-reg-25/apply_registrations.py  # 관측·판단·출처 반영
python scripts/scorecard_cli.py research  ai-scorecard-2026-09-obsreg
python scripts/scorecard_cli.py calculate ai-scorecard-2026-09-obsreg
python scripts/scorecard_cli.py draft     ai-scorecard-2026-09-obsreg
python validation/obs-reg-25/compare_scores.py       # 4열 대조
```

**네트워크를 쓰지 않습니다.** 원자료는 전부 형제 워크트리 커밋의 blob 입니다.

| 파일 | 내용 |
|---|---|
| `verify_values.py` · `verify-output.txt` | 지시값 대 원문 대조 34건 |
| `apply_registrations.py` · `apply-output.txt` | 관측 9건 · 판단 3건 · 출처 5건 반영 |
| `compare_scores.py` · `compare-output.txt` | 4열 factor 대조와 순위 |
| `scorecard/runs/ai-scorecard-2026-09-obsreg/` | 새 실행 (승인 전) |
