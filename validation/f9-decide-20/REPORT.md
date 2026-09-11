# F9 적자 깊이 미결 규칙 5건 실측 조사 보고서 (F9-DECIDE-20)

## 1. 핵심 결론

F9 적자 깊이 미결 규칙 5건(C-04, C-05, C-06, C-07, C-16)에 대해 14개사 전원의 관측치와 채점 엔진 로직을 기반으로 실측 조사를 수행한 결과, **현재 보유 자료(baseline data)를 기준으로 실제로 점수를 움직이는 규칙 조합은 C-06(`proposed_v15_boundaries`) + C-05(`diagnose_only`) 1건뿐이며, C-16은 현행 자료에서 0개사를 움직인다.**

- **현행 자료에서 실제로 점수를 움직이고 차단을 해제(Unblocking)하는 유일한 규칙 조합**.
  - **C-06 (`proposed_v15_boundaries`) + C-05 (`diagnose_only`)**: `spacex-xai` 1개사를 규칙 미결(`needs_rule_decision`) 차단에서 **-4 (status: ok)**로 즉시 해제·완료시키는 유일한 조합이다. C-06만 채택하면 `needs_judgment`(G4 판단 대기)로 이동할 뿐 완료되지 않으며, C-05가 `diagnose_only`여야 G1 점수 -4로 즉시 확정된다. 반면 `openai`는 G1에서 이미 하한(-5)에 도달하여 G3·G4가 자동 생략되므로 C-05의 영향을 전혀 받지 않는다.
- **현행 자료 기준 점수 변동이 0개사인 규칙 (C-16 포함)**.
  - **C-16 (G4 약정 커버리지 미공시 시 처리)**: **현재 baseline 자료 기준으로는 움직이는 기업이 0개사다.** `coverage_comparable`이 `yes`인 기업은 수치 커버리지(2.552 >= 1.0)를 만족한 `oracle` 1개사뿐이며, 나머지 11개사는 모두 `coverage_comparable: unknown` 상태로 C-16에 도달하기 전 `needs_judgment`에서 멈춘다.
    - 특히 `alibaba`의 경우 점수가 갈리기 위해서는 `operating_result_reviewed = profit`(G1 통과)뿐만 아니라 **`coverage_comparable = yes`** 검토 입력까지 **두 가지 검토 입력이 모두 선행 충족**되어야만 비로소 C-16에 도달하여 **-2 (hold)**와 **-3 (downgrade)**으로 1칸 분기된다.
    - `spacex-xai` 역시 C-05가 `apply`이고 `coverage_comparable = yes`가 입력되어야 C-16에 도달하여 **-4 (hold)**와 **-5 (downgrade)**로 갈린다.
    - `amazon`은 `contracted_revenue`가 `parse_failed`이므로 C-16 대상이 아닌 자료 미수집(`pending_data`)으로 격리된다.
    - 따라서 C-16은 검토 입력(`coverage_comparable = yes`)이 확보된 이후에 비로소 효력을 발휘하는 규칙이며, 현행 자료 기준으로는 0개사를 움직인다.
  - **C-04 (신용등급 조달여력 산입)**: 현재 14개사 관측치 데이터베이스에 미인출 여신(`undrawn_credit`) 또는 신용등급 기반 추정 조달액 관측치가 **0건**이다. 엔진 로직상 추정치는 산입하지 않고 관측치만 받도록 설계되어 있어, `exclude`와 `include_v15` 간 점수 차이는 **0개사**다. 자료에 입력이 없다는 사실 자체가 본 조사의 결론이다.
  - **C-07 (ARR의 G4 대체 금지)**: Anthropic과 OpenAI의 ARR 대체 금지(`incompatible_basis`) 원칙을 재확인하는 항목이며, 이미 두 기업의 G4 관측 상태가 격리되어 있어 신규 점수 변동을 일으키지 않는다.
- **채점 미완료 4개사 현황 (3개사가 아닌 4개사)**.
  - 지시서 전제의 3개사(amazon, alibaba, anthropic) 외에 `spacex-xai`(`needs_rule_decision`)를 포함하여 총 **4개사**가 미완료 상태다.
  - `spacex-xai`: C-06 채택 및 C-05 `diagnose_only` 선택 시 **-4 (ok)**로 즉시 완료된다 (유일하게 현행 자료에서 즉시 풀리는 기업).
  - `alibaba`: SEC 20-F 공시 기반 G1 `operating_result_reviewed = profit` 및 G4 `coverage_comparable = yes` 두 가지 검토 입력이 선행되고 C-16 결정 시 **-2(hold) 또는 -3(downgrade)**으로 완료된다.
  - `amazon`: AWS 백로그의 미개시 리스 상회 사실을 정성적으로 인정하여 G4를 유지(step 0)하는 규칙을 명문화하거나 파싱 재수집 시 **-2 (ok)**로 완료 가능하다.
  - `anthropic`: 비상장사의 TTM 영업손익 미공시 처리 규칙(단위경제 흑자 인정 시 -2, 적자 간주 시 -4/-5)을 정하면 완료된다.

---

## 2. 5대 미결 규칙별 실측 조사 상세

### C-04: 신용등급 조달여력의 완충 산입 여부 (`exclude` vs `include_v15`)

- **규칙 배경**. S-RULE은 신용등급의 점수 개입을 금지하나, 과거 G3는 A- 이상 기업에 대해 등급 기반 무제한 조달 여력을 완충에 가산하였다. S-PLAN은 확인된 현금과 확정 미인출 여신(`undrawn_credit`)만 산입하도록 권고하였다.
- **실측 결과**.
  - `observations.json` 전수 조사 결과, 14개사 전체에서 `undrawn_credit` 관측치는 **0건**이다.
  - `calc_f9.py` 구현상 `include_v15`를 선택하더라도 추정치는 배제하고 오직 숫자 관측치(`undrawn_credit`)로만 산입하도록 강제되어 있다.
  - FCF가 마이너스여서 G3 런웨이를 계산하는 기업은 `amazon`(현금 $123B, 런웨이 10.6년), `oracle`(현금 $31.9B, 런웨이 1.35년), `spacex-xai`(현금 $100B, 런웨이 3.08년)의 3개사다.
  - Amazon과 SpaceX는 현금만으로 이미 런웨이 3년을 초과하여 step 0(만점 유지)에 도달해 있으므로 조달 여력이 추가되어도 점수 변동이 불가능하다.
  - Oracle은 런웨이 1.35년(step -1)으로 추가 조달 여력이 있다면 점수 상향 여지가 있으나, 데이터에 관측치가 전혀 존재하지 않는다.
- **결론**. **C-04는 14개사 전원에 대해 점수 변동이 0건이다.**

### C-05: G1 실패 뒤 G3·G4 추가 감점 여부 (`apply` vs `diagnose_only`) — [Blocking]

- **규칙 배경**. 본업 영업적자로 G1에서 감점(-3, -4, -5)을 받은 기업에 대해, 런웨이(G3)와 약정 커버리지(G4) 결함을 추가 감점할지(`apply`), 아니면 G1 점수로 최종 점수를 확정하고 G3·G4는 진단 참고 기록만 남길지(`diagnose_only`)의 문제다.
- **실측 결과**.
  - **OpenAI (영향 없음)**: BEP 후퇴(`bep_retreat: yes`)로 인해 G1에서 이미 최하한 점수인 **-5**를 받았다. 엔진 로직상 이미 바닥(-5)인 점수는 G3·G4를 자동으로 생략(`skipped`)하므로, C-05 선택과 무관하게 항상 **-5**로 고정된다.
  - **SpaceX (결정적 영향)**: 영업손실률 -14.9%로 G1 기본 점수가 **-4**이다. -4는 하한(-5)이 아니므로 G3·G4 진단 로직이 실행된다.
    - G3 런웨이는 3.08년으로 step 0(추가 감점 없음)이다.
    - G4에서 `coverage_comparable`이 `unknown` 상태이다.
    - **`diagnose_only` 선택 시**: G1 점수 **-4**가 최종 F9 점수로 확정된다. G4의 판단 미결은 진단 영역에 머물므로 채점을 차단하지 않으며, **`spacex-xai`는 -4 (status: ok)로 즉시 완료된다.**
    - **`apply` 선택 시**: G4 감점 적용을 위해 G4 판단(`coverage_comparable`)이 필수적으로 요구되어 **status: needs_judgment**로 차단된다. 만약 사람이 이를 `yes`로 입력하더라도, 미개시 리스 약정(`offbalance_B`)이 미공시이므로 C-16 규칙에 연결되어 `hold` 시 -4, `downgrade` 시 **-5**로 추가 강등된다.
- **결론**. **C-05는 `spacex-xai`의 채점 완료 여부와 점수(-4 vs -5)를 결정하는 유일한 핵심 분기점이다.**

### C-06: 손실률 경계 중첩과 5개 묶음 명문화 — [Blocking]

- **규칙 배경**. 영업손실률 구간 경계(-10%·-30%) 중첩, FCF 0 처리, 영업손익 0 처리, 완충 잠식 정의, BEP 우선순위의 5개 사안이 C-06으로 묶여 있다.
- **실측 결과**.
  - 현재 `calc_f9.py`는 `C-06 == "proposed_v15_boundaries"`가 아니면 G1 적자 판정을 즉시 보류(`needs_rule_decision`)한다.
  - 현재 14개사 중 적자 손실률이 실측된 유일한 기업인 `spacex-xai`(-14.9%)가 바로 이 규칙 미결로 인해 채점이 차단되어 있다.
  - `proposed_v15_boundaries`를 채택하면 다음과 같이 구간이 확정된다.
    - `-10% <= margin < 0%` -> -3
    - `-30% <= margin < -10%` -> -4
    - `margin < -30%` -> -5
    - SpaceX(-14.9%)는 정확히 **-4** 구간으로 확정되어 차단이 해제된다.
  - FCF = 0 및 영업손익 = 0인 기업은 현재 14개사 중 **0개사**이므로 실측상 즉각적인 영향을 미치지 않는다.
- **결론**. **C-06의 `proposed_v15_boundaries` 채택은 `spacex-xai` 차단 해제의 필수 전제 조건이다.**

### C-07: G4가 RPO/B종 약정인데 ARR로 계산된 건

- **규칙 배경**. G4는 미래 계약 수입과 미개시 B종 약정을 비교해야 하는데, 과거 비상장사(Anthropic, OpenAI)에 대해 성격이 전혀 다른 연환산 매출(ARR)을 계약 수입으로 대입했던 오류다. S-PLAN은 "ARR 대체 금지, 동일 범위 자료 미확보는 `incompatible_basis`로 격리"를 권고하였다.
- **실측 결과**.
  - 두 기업 모두 관측 상태가 `incompatible_basis`로 격리되어 있으며, `coverage_comparable: no`로 기록되어 있다.
  - OpenAI는 G1 -5 바닥으로 G4 자체가 실행되지 않는다.
  - Anthropic은 G1에서 먼저 막혀 있으며, 설령 G1이 풀리더라도 비상장 FCF 미공시 규칙에 의해 G4가 G2(-2)와 중복 감점 방지(dedupe) 처리되므로 점수 계산에 영향을 주지 않는다.
- **결론**. **C-07은 데이터 무결성 원칙을 지키는 규칙이며, 현재 점수를 변경하지 않는다.**

### C-16: G4 판정 불가 시 `hold`냐 `downgrade`냐 — [Blocking]

- **규칙 배경**. G4 산출에 필요한 지표가 확인된 미공시(`status: not_disclosed`)일 때, 점수를 유지(`hold`, step 0)할 것인가, 1단계 하향(`downgrade`, step -1)할 것인가의 문제다. 수집 실패(`parse_failed`, `없음`)는 C-16 대상이 아니며 자료 대기(`pending_data`)로 분리된다.
- **실측 결과**.
  - **현행 baseline 자료 기준: 점수 변동 0개사**.
    - baseline 관측치에서 `coverage_comparable`의 분포는 `yes` 1개사(`oracle`), `no` 2개사(`anthropic`, `openai`), `unknown` 11개사(그 외 전원)이다.
    - `oracle`은 수치 커버리지(2.552 >= 1.0)를 이미 충족하여 만점(step 0)으로 산출 완료된다.
    - 나머지 11개사는 C-16 미공시 정책 분기에 도달하기 전, `coverage_comparable != 'yes'` 게이트에서 먼저 차단되어 `needs_judgment`("coverage_comparable 검토 입력 필요")로 멈춘다.
    - 엔진 주석에도 명시되어 있듯이, 비교 가능성이 미확인(`unknown`)된 기업은 결측 정책(C-16)으로 보내지 않고 판단 대기로 멈춘다. 따라서 현행 자료 기준으로는 C-16 어느 쪽을 선택하더라도 점수가 움직이는 기업이 **0개사**다.
  - **입력 보완 후 영향 분석**.
    - **Alibaba (2대 검토 입력 선행 필수)**.
      - Alibaba의 계약 수입과 B종 약정은 모두 `status: not_disclosed`이므로 C-16 적용 대상 지표 조건을 갖추고 있다.
      - 그러나 Alibaba가 C-16에 도달하여 점수가 갈리기 위해서는 ① G1 TTM 영업흑자 확인(`operating_result_reviewed = profit`)과 ② G4 약정 비교 가능성 확인(`coverage_comparable = yes`)이라는 **2대 검토 입력이 모두 선행 충족**되어야 한다.
      - 2대 검토 입력이 완료된 후, **C-16이 `hold`이면 최종 점수는 F9 = −2 (status: ok)**가 되고, **C-16이 `downgrade`이면 최종 점수는 F9 = −3 (status: ok)**이 되어 정확히 1칸 분기된다.
    - **SpaceX**.
      - C-05가 `diagnose_only`이면 G1 점수(-4)로 확정되어 C-16의 영향을 받지 않는다.
      - C-05가 `apply`이고 `coverage_comparable = yes`가 입력될 때만 C-16에 의해 -4(hold) 또는 -5(downgrade)로 갈린다.
    - **Amazon (C-16 적용 불가 - 파싱 실패)**.
      - Amazon의 계약 수입은 `parse_failed` 상태이다. `not_disclosed`가 아니므로 C-16 정책의 적용 대상이 되지 못하고 자료 대기(`pending_data`)로 분리된다 (`coverage_comparable = yes`를 넣더라도 미수집 오류로 차단됨).
- **결론**. **C-16은 현행 baseline 자료 기준으로는 0개사를 움직이며, 향후 Alibaba에 대해 `operating_result_reviewed = profit` 및 `coverage_comparable = yes` 2대 검토 입력이 확보된 후에 비로소 -2와 -3을 가르는 규칙이다.**

---

## 3. 5대 미결 규칙의 상호 결합 지점 분석 (얽히는 구조)

사용자 지침에서 경고한 바와 같이, 5대 규칙은 개별적으로 분리되어 있지 않고 파이프라인 상에서 긴밀하게 얽혀 있다.

1. **BEP 우선순위와 C-06 및 C-05의 결합**.
   - C-06의 손실률 경계(-10%/-30%)와 BEP 후퇴(-5)의 적용 순서가 명문화되어야 한다.
   - 현재 구현은 BEP 후퇴를 손실률 경계보다 절대적으로 우선하여 즉시 -5(바닥)로 직행시킨다.
   - 점수가 이미 바닥(-5)이 되면 C-05(추가 감점 여부)를 묻지 않고 G3·G4를 생략한다(`OpenAI`).
   - 만약 BEP 후퇴보다 손실률 경계를 우선한다면, BEP가 후퇴한 기업도 손실률에 따라 -3이나 -4를 받고 C-05의 적용 대상이 되어 결과가 완전히 달라진다. 따라서 C-06의 BEP 우선순위 결정은 C-05의 유효 범위를 직접 통제한다.
2. **C-05와 C-16의 연동**.
   - C-05가 `diagnose_only`로 결정되면, G1 실패 기업(`spacex-xai`)은 G4에 도달하지 않으므로 C-16(hold/downgrade)은 오직 흑자 적자 전환 기업(`alibaba`)에만 작동한다.
   - 반면 C-05가 `apply`로 결정되면, C-16은 `alibaba`뿐만 아니라 `spacex-xai`의 최종 점수(-4 vs -5)까지 함께 결정하는 다중 영향 규칙으로 확장된다.
3. **C-07과 C-16의 결측 분류 연동**.
   - C-07에서 ARR 대체를 금지하고 `incompatible_basis`로 지정한 결과, 이 결측은 '확인된 미공시'가 아닌 '자료 비교 불가'로 분류되어 C-16(hold/downgrade) 경로로 진입하지 못하고 자료 대기로 차단된다.
   - 결측 유형의 정규화 기준이 C-16의 진입 여부를 결정한다.

---

## 4. 14개사 매트릭스 시뮬레이션 결과

C-06을 `proposed_v15_boundaries`로 고정하고, C-05와 C-16의 조합에 따른 14개사 실측 점수를 비교한 결과는 다음과 같다.

| 기업 | 현재 상태 | C-05 diagnose_only + C-16 hold | C-05 diagnose_only + C-16 downgrade | C-05 apply + C-16 hold | C-05 apply + C-16 downgrade | 비고 및 변동 원인 |
|---|---|---|---|---|---|---|
| **apple** | ok (0) | **0** | **0** | **0** | **0** | G1 통과, FCF 양수 안정 (불변) |
| **microsoft** | ok (0) | **0** | **0** | **0** | **0** | G1 통과, FCF 양수 안정 (불변) |
| **nvidia** | ok (0) | **0** | **0** | **0** | **0** | G1 통과, FCF 양수 안정 (불변) |
| **palantir** | ok (0) | **0** | **0** | **0** | **0** | G1 통과, FCF 양수 안정 (불변) |
| **tsmc** | ok (0) | **0** | **0** | **0** | **0** | G1 통과, FCF 양수 안정 (불변) |
| **alphabet** | ok (-1) | **−1** | **−1** | **−1** | **−1** | G1 통과, FCF 양수 악화 (불변) |
| **meta** | ok (-1) | **−1** | **−1** | **−1** | **−1** | G1 통과, FCF 양수 악화 (불변) |
| **tesla** | ok (-1) | **−1** | **−1** | **−1** | **−1** | G1 통과, FCF 양수 악화 (불변) |
| **oracle** | ok (-3) | **−3** | **−3** | **−3** | **−3** | G1 통과, FCF 적자, 런웨이 1.35년, 커버리지 통과 (불변) |
| **openai** | ok (-5) | **−5** | **−5** | **−5** | **−5** | G1 BEP 후퇴로 이미 바닥(-5), G3/G4 생략 (불변) |
| **spacex-xai** | **차단** (C-06 미결) | **−4** (ok) | **−4** (ok) | **판단대기** (G4) | **판단대기** (G4) | **C-06 + C-05 diagnose_only가 현행 자료에서 점수를 움직이는 유일한 조합(-4 완료). apply이면 G4 판단 필요** |
| **alibaba** | **차단** (G1 미결) | 보류 (G1·G4 입력) | 보류 (G1·G4 입력) | 보류 (G1·G4 입력) | 보류 (G1·G4 입력) | 현행 자료는 pending_data(0개사 영향). G1 profit 및 G4 coverage_comparable=yes 2대 입력 충족 시 C-16에 의해 **-2(hold) 또는 -3(downgrade)** 분기 |
| **amazon** | **차단** (G4 판단) | 보류 (G4 판단) | 보류 (G4 판단) | 보류 (G4 판단) | 보류 (G4 판단) | AWS 백로그 정성 확인 규칙 명시 시 **-2** 확정 가능 (C-16 대상 제외) |
| **anthropic** | **차단** (G1 자료) | 보류 (G1 자료) | 보류 (G1 자료) | 보류 (G1 자료) | 보류 (G1 자료) | 비상장 영업손익 판정 규칙 명시 시 완료 가능 |

`*` Alibaba는 현행 baseline 자료 기준 네 조합 모두 pending_data(보류)임. SEC 20-F 공시상 연간 영업이익 1,134억 위안 흑자 기반 `operating_result_reviewed = profit`과 `coverage_comparable = yes` 2대 검토 입력이 충족될 경우 C-16에 따라 -2(hold) 또는 -3(downgrade)으로 분기됨.

---

## 5. 채점 미완료 기업들의 구체적 해소 경로

### 1. SpaceX-xAI (`needs_rule_decision` 해소)
- **차단 원인**: 적자 손실률(-14.9%)에 대한 C-06 구간 경계 미확정.
- **해소 규칙**: C-06 `proposed_v15_boundaries` 채택 및 C-05 `diagnose_only` 선택.
- **결과**: **현행 보유 자료에서 즉시 점수가 산출·완료되는 유일한 사례 (F9 = −4, status: ok)**.

### 2. Amazon (`needs_judgment` 해소 방안)
- **차단 원인**: G4에서 미개시 리스 $106B 대비 AWS 백로그가 "수백 $B급"이라는 정성적 사실은 있으나, 숫자로 파싱되지 않아(`parse_failed`) 비교 가능성이 `unknown`으로 남아 있다.
- **해소 규칙안**. "상장사의 주석 공시상 백로그 규모가 미개시 리스 총액을 명백히 상회함이 확인되는 경우, `coverage_comparable = yes`로 간주하고 G4 step 0(유지)을 적용한다."
- **결과**. 규칙 명시 즉시 G1(흑자) -> G2(-2) -> G3(런웨이 10.6년, step 0) -> G4(유지, step 0)로 이어져 **F9 = −2 (status: ok)**로 완료된다. 단, `contracted_revenue`가 `parse_failed`이므로 C-16 결측 정책의 대상은 아니다.

### 3. Alibaba (`pending_data` 및 `needs_judgment` 해소 방안)
- **차단 원인**: SEC 20-F에 연간 영업이익이 명시되어 있음에도 baseline 관측치에 TTM 영업손익 관측치가 누락되었고 `operating_result_reviewed`가 `unknown`으로 남아 있으며, G4 역시 `coverage_comparable`이 `unknown` 상태이다.
- **해소 요건 (2대 검토 입력 선행 필수)**.
  1. G1 영업손익 검토 부호: SEC 공시 기반 `operating_result_reviewed = profit` 입력.
  2. G4 비교 가능성 검토: `coverage_comparable = yes` 입력.
  3. C-16 결정: `hold` 또는 `downgrade` 선택.
- **결과**.
  - 현행 자료 기준: 2대 검토 입력 없이는 C-16을 어떻게 선택하든 점수가 움직이지 않는다(0개사).
  - 2대 검토 입력 충족 후 C-16 `hold` 선택 시: **F9 = −2 (status: ok)**.
  - 2대 검토 입력 충족 후 C-16 `downgrade` 선택 시: **F9 = −3 (status: ok)**.

### 4. Anthropic (`pending_data` 해소 방안)
- **차단 원인**: 비상장사로서 TTM 영업손익 공시가 없고 단일 분기 조정 흑자($559M)만 보고되어 C-20에 의해 G1 통과가 차단되어 있다.
- **해소 규칙안**.
  - 대안 A (단위경제/단일분기 흑자 참작): G1을 조건부 통과시키면 비상장 FCF 미공시 특별 규칙(G2 -2, G3 생략, G4 중복방지)이 작동하여 **F9 = −2 (status: ok)**가 된다.
  - 대안 B (보수적 적자 간주): 비상장 AI 연구소의 막대한 연간 컴퓨트 소진을 감안하여 영업적자로 판정한다. 손실률 < -30%로 보면 **F9 = −5**, 완화 참작 시 **F9 = −4**가 된다.

---

## 6. 독립 검증 및 산출물 보존 내역

- **독립 검증 스위트**: [`validation/f9-decide-20/verify_f9_independent.py`](file:///C:/Users/noble/orca/workspaces/stock-report-harness/C-13/validation/f9-decide-20/verify_f9_independent.py)
  - 11개 단위 테스트 전원 통과 (양성 대조군 1건, 음성 변이 대조군 3건 포함).
  - C-04 불변성, C-05 SpaceX 점수 분기 및 OpenAI 바닥 불변성, C-06 해제, C-07 격리, C-16 Alibaba 점수 분기 검증 완료.
- **구조화된 시뮬레이션 결과**: [`validation/f9-decide-20/f9_decision_simulation_results.json`](file:///C:/Users/noble/orca/workspaces/stock-report-harness/C-13/validation/f9-decide-20/f9_decision_simulation_results.json)
- **기준선 원자료 보존**: `validation/f9-decide-20/_raw/` (`baseline_observations.json`, `baseline_judgments.json`, `rules_v15.json`).
