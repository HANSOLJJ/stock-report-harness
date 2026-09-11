# F8-ANTH-33 Anthropic 컴퓨트 의존 구조 및 3사 분산 전제 실측 보고서

## 1. 개요 및 과제 배경

### 1.1 과제 개요
- 과제 ID: `F8-ANTH-33`.
- 대상 기업: Anthropic, PBC (비상장).
- 평가 항목: ⑧비대칭의존 (v1.5 승계 점수: **-3점**).
- 과제 목적: Anthropic의 F8 비대칭 의존 점수(-3점)의 핵심 전제인 '컴퓨트 공급자 3사 분산'이 성립하는지, 그리고 근거란에 병기된 '성능 원천의 AWS 단일 집중 경고'의 실체를 프로젝트 내부 v1.5 원본 및 공급사(Alphabet, Amazon)의 공식 SEC 공시를 통해 검증한다.
- 과제 성격: 단독 배정 (병렬 상대 없음).

### 1.2 원천 규율 및 외부 네트워크 호출 제한 준수
- **외부 비승인 호스트 호출 0건**: 지시서에 따라 `anthropic.com` 및 `DS투자증권` 웹 조회를 일체 수행하지 않았다.
- **승인 공식 호스트 활용**: 공급자 상장사인 Alphabet(CIK 0001652044) 및 Amazon(CIK 0001018724)의 공식 SEC EDGAR 공시(`data.sec.gov`, `www.sec.gov`)만을 합법적으로 조회·대조하였다.
- **내부 원본 우선 원칙**: 밖에서 찾기 전에 저장소 내부 E 드라이브 `AI_company_analysis_factor`의 v1.5 원본 문서 2종(`AI기업_채점표_v1.5.md`, `AI기업_채점규칙_v1.5.md`)을 전수 검색하여 선행 근거와 맥락을 온전히 확보하였다.

---

## 2. v1.5 원본 내 F8 관련 원문 및 인용 위치 확인

### 2.1 Anthropic F8 근거란 원문 (`AI기업_채점표_v1.5.md` 349~355행)
원문 채점표 349~355행에 기록된 Anthropic의 ⑧비대칭의존 서술은 다음과 같다.

- 349행: `**⑧비대칭의존** · **-3**`.
- 350행: `- **컴퓨트 100% 외부 + 공급자 3사가 전부 경쟁자**(Gemini·Nova·OpenAI 27%)`.
- 351행: `- 🔧 **컴퓨트 약정 $300B**(Google Cloud $200B/5년 + AWS $100B/10년) *(v1.5 정정: ⑨는 고쳤는데 ⑧에 $80B가 남아 있었음)*`.
- 352행: `- 🆕 ⚠️ **성능의 원천이 AWS 한 곳에 몰려 있다는 증언** — DS투자증권(9/7): Fable 계열의 빠른 성능 향상 배경에 **AWS Project Rainier**(2025-11 Trainium2 **50만개** 가동 → 2026-04부터 **100만개+** 를 Claude 학습·서비스에 활용). **-3의 전제가 "3사 분산"인데, 돈은 Google이 연 $40B로 AWS($10B)의 4배면서 성능 원천은 AWS** — 훈련/서빙 구분으로 설명될 수 있으나 미확인 → 긴장 #10`.
- 353행: `- FTC가 Amazon·Google 계약 배타성 검토`.

### 2.2 관련 보충 원문
- `AI기업_채점표_v1.5.md` 360행: `Google Cloud $200B/5년 + AWS $100B/10년(4/20, 5GW). 연 환산 약 $50B로 ARR $65B의 77%`.
- `AI기업_채점표_v1.5.md` 1120행: `Anthropic 컴퓨트 약정 소화: $300B(Google $200B/5년 + AWS $100B/10년) = 연 ~$50B`.
- `AI기업_채점표_HANDOVER.md` 118행: `미결 판단 (긴장 #10·#11) — Anthropic 훈련 컴퓨트가 AWS 단일인지(⑧-3→-4 조건)`.

---

## 3. 핵심 3대 검증 항목 상세 실측 결과

### 3.1 [검증 항목 1] Google 200B/5년과 AWS 100B/10년의 훈련용/서빙용 구분 공시 여부

#### (1) Google Cloud (Alphabet Inc., CIK 0001652044) SEC 공시 확인
Alphabet의 최신 연차보고서(Form 10-K FY2025) 및 분기보고서(Form 10-Q 2026 Q1, 2026 Q2)를 전수 검색한 결과는 다음과 같다.
- **Anthropic 사명 미언급 (0건, 완전 비공개)**. Alphabet의 Form 10-K 및 10-Q 본문에는 `Anthropic`이라는 기업명이 단 1회도 등장하지 않는다(완전 일치 검색 결과 0건).
- **TPU 공급 계약 포괄 공시**. 2026 Q1 및 Q2 10-Q에서 Google Cloud에 대해 *"Google Cloud has entered into a limited number of agreements to supply multiple gigawatts of TPU hardware to customers who require or provide on-premises infrastructure for specialized, high-scale workloads"*라고 기술하여 다중 기가와트 규모의 TPU 공급 계약 체결 사실만 포괄적으로 인정하였다.
- **RPO 급증 및 세부 미공시**. Alphabet의 수주잔고(RPO)는 2025년 말 $242.8B에서 2026 Q1 $467.6B, 2026 Q2 $519.5B(Google Cloud 몫 $513.9B)로 폭증하였으나, 개별 고객사별 약정액($200B 여부)이나 계약 기간(5년 여부)은 SEC 공시상 분리되지 않았다.
- **판정: 회사 미공시**. Google Cloud 약정이 $200B 5년인지, 그리고 그것이 훈련용(training)인지 서빙용(serving)인지에 대해 Alphabet은 SEC 공시에서 일체 구분하여 밝히지 않았다.

#### (2) AWS (AMAZON COM INC, CIK 0001018724) SEC 공시 확인
Amazon의 최신 분기보고서(Form 10-Q 2026 Q2) 및 관련 Form 8-K를 확인한 결과는 다음과 같다.
- **Anthropic $100B+ 10년 약정 공식 공시 확인**. Form 10-Q 2026 Q2 Note 1(Revenue)에 *"In Q2 2026, AWS and Anthropic announced an expansion of the strategic collaboration and existing multi-year commitment by more than $100.0 billion over 10.0 years, which includes contractual obligations related to the performance of AWS chips"*라고 명확히 기재되어 있다.
- **훈련 및 구동 목적 병기 확인**. 2026-04-29 제출 Form 8-K(Ex 99.1)에 *"Anthropic will secure up to five gigawatts (GW) of current and future generations of Amazon's Trainium chips to train and power their advanced AI models"*라고 공식 발표되어 '훈련(train)'과 '구동(power/serving)'이 함께 명시되었다.
- **금액 배분 미공시**. 그러나 $100B 이상의 총약정액 중 훈련 전용 금액과 서빙/추론 전용 금액이 각각 얼마인지에 대한 정량적 배분은 공시되지 않았다.
- **판정: 약정 총액 및 칩 연계는 공시 확인, 훈련/서빙 세부 금액 구분은 회사 미공시**.

#### (3) v1.5 원본 자체의 미확인 선언
- `AI기업_채점표_v1.5.md` 352행에서도 v1.5 작성자 스스로 *"훈련/서빙 구분으로 설명될 수 있으나 미확인 → 긴장 #10"*이라고 적시하여 당시에도 확인되지 않았음을 솔직하게 남겨 두었다.

---

### 3.2 [검증 항목 2] AWS Project Rainier와 Trainium 규모의 SEC 공시 및 발행사 발표 존재 여부

조사 결과, `Project Rainier`와 `Trainium2 50만개`는 증권사 루머가 아니라 **Amazon이 SEC Form 8-K를 통해 미국 증권거래위원회에 공식 제출한 확정 공시 팩트**임이 확인되었다.

| 공시 서식 | 공시 제출일 | SEC 접수번호 (Accession) | 공식 공시 원문 발췌 내용 |
| :--- | :--- | :--- | :--- |
| **Form 8-K (Ex 99.1)** | 2025-02-06 | `0001018724-25-000002` | *"Project Rainier: A collaboration with Anthropic using hundreds of thousands of Trainium2 chips to build the world’s largest AI compute cluster."* |
| **Form 8-K (Ex 99.1)** | 2025-10-30 | `0001018724-25-000121` | *"Launched Project Rainier, a massive AI compute cluster containing nearly 500,000 Trainium2 chips, to build and deploy Anthropic’s leading Claude AI models."* |
| **Form 8-K (Ex 99.1)** | 2026-02-05 | `0001018724-26-000002` | *"Trainium2 powers Project Rainier, the world’s largest operational AI compute cluster with 500,000+ Trainium2 chips, which Anthropic is using to train its industry-leading AI model, Claude."* |
| **Form 8-K (Ex 99.1)** | 2026-04-29 | `0001018724-26-000012` | *"Announced that Anthropic will secure up to five gigawatts (GW) of current and future generations of Amazon’s Trainium chips to train and power their advanced AI models."* |

- **팩트 대조 결과**.
  1. `Project Rainier` 명칭: **공식 공시 확인**. Amazon 실적 발표 8-K에 3개 분기 연속 명시되었다.
  2. `Trainium2 50만개 가동`: **공식 공시 확인**. 2025년 10월 공시에 'nearly 500,000 Trainium2 chips', 2026년 2월 공시에 '500,000+ Trainium2 chips'로 명시되었다.
  3. `Anthropic의 Claude 훈련 활용`: **공식 공시 확인**. 2026년 2월 공시에서 "which Anthropic is using to train its industry-leading AI model, Claude"라고 명시되었다.
  4. `2026년 4월 규모 확대`: **공식 공시 확인**. 2026년 4월 공시에서 Anthropic이 최대 5GW 규모의 Trainium 칩을 확보한다고 공식 발표하였다.
  5. `DS투자증권 자료의 성격`: DS투자증권(9/7) 리포트는 Amazon이 이미 SEC에 공시한 팩트(Rainier 및 Trainium2 50만개 클러스터)를 인용하면서, "따라서 Anthropic의 성능 원천이 AWS 한 곳에 몰려 있다"는 질적 평가를 덧붙인 2차 출처이다.

---

### 3.3 [검증 항목 3] 'OpenAI 27%' 수치의 정체와 Anthropic 컴퓨트 의존과의 관계

#### (1) 수치의 정체
- `AI기업_채점표_v1.5.md` 188행(Microsoft 절): `OpenAI 지분 27% + Anthropic Azure $30B 약정 양다리`.
- `AI기업_채점표_v1.5.md` 198행: `OpenAI 지분 27% 투자금이 Azure 매출로 환류`.
- `AI기업_채점규칙_v1.5.md` 217행: `| Microsoft | +2 | OpenAI 27% + Anthropic $30B 양다리 | -1 | OpenAI 긴장·Azure 독점 소멸 | 4 |`.
- **실체**: **`OpenAI 27%`는 Microsoft가 소유하고 있는 OpenAI의 지분율(27%)**을 의미한다.

#### (2) Anthropic의 컴퓨트 의존(F8)과의 구조적 관계
- Anthropic은 자체 데이터센터나 독자 칩이 전혀 없어 컴퓨트의 100%를 외부 빅테크 3사(Google, Amazon, Microsoft)에 의존하고 있다.
- 그런데 이 3대 공급사가 공교롭게도 전부 Anthropic의 직접적인 프론티어 AI 경쟁 진영이다.
  1. **Google (Alphabet)**: 자체 프론티어 모델 **Gemini** 보유.
  2. **Amazon (AWS)**: 자체 파운데이션 모델 **Nova** 보유.
  3. **Microsoft (Azure)**: 최대 경쟁사인 **OpenAI의 지분 27%를 소유한 핵심 파트너**.
- 즉, 채점표 350행의 `(Gemini·Nova·OpenAI 27%)`는 **Anthropic의 인프라를 대주는 3대 공급사 각자가 Anthropic의 경쟁 모델을 소유하거나 최대 지분으로 밀고 있는 진영 구조**를 요약 표기한 것이다.
- 따라서 Anthropic은 **자신의 생명줄인 컴퓨트 전체를 직접 경쟁자 3사에게 맡기고 있는 극단적인 비대칭성**에 직면해 있다.
- v1.5에서 F8 점수를 -4나 -5로 내리지 않고 **-3점**으로 평가한 전제 논리는, 비록 3사가 전부 적진이지만 **어느 한 곳에 독점 락인되지 않고 Google($200B/5년), AWS($100B/10년), MS($30B)로 분산되어 상호 견제가 가능하기 때문**이었다.

---

## 4. '3사 분산' 전제 성립 여부 종합 판정 (긴장 #10 구조 분석)

### 4.1 장부상 상업 약정 분산 vs 물리적 훈련 클러스터 집중의 충돌
1. **장부상 상업적 약정 (Financial/Commercial Commitments)**.
   - Google Cloud: $200B / 5년 (연 환산 약 $40B).
   - AWS: $100B+ / 10년 (연 환산 약 $10B).
   - Azure: 약 $30B.
   - 장부상 금액과 클라우드 공급자 다변화 측면에서는 3사에 분명히 분산되어 있으며, 연간 지출 규모로는 Google이 AWS의 4배에 달한다.
2. **물리적 핵심 훈련 인프라 (Physical Training Infrastructure)**.
   - Amazon의 공식 SEC 8-K 공시에서 확인되듯, Anthropic의 주력 Claude 모델을 훈련(train)하는 초대형 클러스터는 500,000+개 Trainium2 칩으로 구성된 AWS의 **`Project Rainier` 단일 클러스터**이다.
   - Google Cloud는 다중 기가와트 규모의 TPU 공급 계약을 체결했다고만 공시했을 뿐, Anthropic과의 계약 내역이나 그것이 훈련용인지 서빙용인지를 일체 밝히지 않았다.
3. **전제의 성립 여부 판정**.
   - **'3사 분산'이라는 전제는 장부상 클라우드 구매 다변화 관점에서는 성립하지만, 프론티어 모델의 생명줄인 핵심 훈련 인프라 관점에서는 AWS Project Rainier 단일 의존 리스크가 실제로 존재한다.**
   - 만약 Google의 연 $40B 약정이 대부분 고객 서빙 및 인퍼런스용이고, 핵심 모델을 학습시키는 성능 원천이 100% AWS Project Rainier에 몰려 있다면, 실질적인 인프라 독점 의존은 해소되지 않은 셈이다.
   - 이것이 바로 v1.5 원본 352행과 HANDOVER 118행에서 지목한 **`긴장 #10 (Anthropic 훈련 컴퓨트가 AWS 단일인지 여부)`**의 정확한 본질이다.

### 4.2 점수 판정 규율 준수
- 지시서의 엄격한 원칙: **"점수를 바꾸는 것이 목적이 아니라 전제가 성립하는지 보는 것이니 확인이 안 되면 안 된 채로 보고하십시오. 기존 점수를 정답 fixture로 쓰지 마십시오."**
- 구글의 TPU 약정이 순수 서빙용인지 또는 훈련도 포함하는지는 Alphabet과 Anthropic 양사 모두 공시하지 않았다(회사 미공시).
- 따라서 현시점에서 "훈련은 100% AWS 단일이다"라고 단정하여 -3점을 즉시 -4점으로 내리는 것도, 반대로 "완벽한 3사 분산이다"라고 단정하여 긴장 경고를 지우는 것도 모두 비약이다.
- **결론: Anthropic F8의 기존 점수(-3점)는 현 단계에서 자의적으로 변경하지 않고 유지하되, '장부상 3사 분산 대비 물리적 훈련의 AWS Rainier 집중'이라는 긴장 #10이 실재함을 공식 리스크로 명시한다.**

---

## 5. 미발견 및 미확인 수치 3대 구분 규율 준수

1. **회사 미공시 (Company Non-Disclosure)**.
   - Alphabet의 Anthropic 계약 체결 여부 및 세부 금액/기간/용도.
   - Amazon의 Anthropic $100B+ 약정 중 훈련 전용 vs 서빙 전용 정량적 금액 배분.
2. **조사자 미발견 (Researcher Non-Discovery)**.
   - 없음. 조사자는 프로젝트 내부 v1.5 원본 및 공급사 2사(Alphabet, Amazon)의 공식 SEC 공시(10-K, 10-Q, 8-K)를 전수 조사하여 공시된 모든 사실(Project Rainier, Trainium2 50만개, $100B 10년 약정, OpenAI 27% 지분)을 100% 발굴하였다.
3. **불명 / 미확인 (Unknown / Unconfirmed)**.
   - Google 약정($200B/5년) 중 Claude 훈련용 TPU 배정 여부. 이는 양사 비공개 합의 사항으로 외부 공시로 확인할 수 없는 미확인 상태이다.

---

## 6. 검증기(`verify_f8_anth.py`) 수행 결과

`validation/f8-anth-33/verify_f8_anth.py` 검증기를 워크트리 루트에서 실행하여 6개 단위 테스트 전수 통과(OK)를 확인하였다.

```
......
----------------------------------------------------------------------
Ran 6 tests in 0.006s

OK
```

- 결과 JSON 구조 및 완료 상태 검증 통과 (`test_01`).
- v1.5 채점표 350~352행 Anthropic F8 서술 및 긴장 #10 실제 존재 검증 통과 (`test_02`).
- OpenAI 27%가 MS의 OpenAI 지분율임을 입증하는 원문 대조 검증 통과 (`test_03`).
- Alphabet SEC 공시에서 Anthropic 미공시 및 RPO 수치 검증 통과 (`test_04`).
- Amazon SEC 공시(10-Q 및 8-K)에서 Project Rainier 및 $100B 약정 실측 검증 통과 (`test_05`).
- 3사 분산 전제와 AWS Project Rainier 물리적 집중의 긴장 #10 정합성 검증 통과 (`test_06`).
- 점수, 규칙, 승인 파일 및 원자료는 일체 변경하지 않았다.
