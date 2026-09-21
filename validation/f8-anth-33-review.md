# F8-ANTH-33 재검토 — anthropic 컴퓨트 의존

- 검토일. 2026-09-11.
- 대상. C-13 `8ddb0ae`.
- 판정. **`pass`.** **"증권사 증언" 이던 것이 SEC 8-K 확정 공시로 밝혀졌다.** 그리고 **전제가 반만 성립한다.**

## 가장 값진 것 — 2차 출처인 줄 알았던 것이 1차 공시였다

근거란은 이렇게 적혀 있었다.

> 🆕 ⚠️ 성능의 원천이 AWS 한 곳에 몰려 있다는 **증언** — **DS투자증권(9/7)**: … Project Rainier(Trainium2 50만개 → 100만개+) … **미확인**

**Amazon 이 SEC 에 직접 제출한 8-K 였다.** C-13 이 네 건을 찾았다.

```
2025-02-06  0001018724-25-000002  "Project Rainier: A collaboration with Anthropic using hundreds of
                                   thousands of Trainium2 chips to build the world's largest AI compute cluster."
2025-10-30  0001018724-25-000121  "nearly 500,000 Trainium2 chips, to build and deploy Anthropic's Claude"
2026-02-05  0001018724-26-000002  "500,000+ Trainium2 chips, which Anthropic is using to TRAIN its
                                   industry-leading AI model, Claude."
2026-04-29  0001018724-26-000012  "Anthropic will secure up to five gigawatts (GW) of … Amazon's Trainium
                                   chips to TRAIN AND POWER their advanced AI models."
```

**`train` 이 공급사 공시 원문에 있다.** v1.5 가 `훈련/서빙 구분으로 설명될 수 있으나 미확인` 이라고 남긴 그 구분이, **AWS 쪽에 한해서는 확인된다.**

**DS투자증권은 이미 공시된 팩트를 인용하고 질적 평가를 덧붙인 2차 출처**라는 정리도 정확하다. **인용 금지 원천에 기대지 않고 같은 사실을 1차로 다시 세웠다.**

## Google 쪽은 정반대다 — 아무것도 공시되지 않는다

```
Alphabet 10-K FY2025 · 10-Q 2026 Q1·Q2 에서  "Anthropic"  →  0건
```

**사명이 단 한 번도 안 나온다.** 있는 것은 포괄 서술뿐이다.

> Google Cloud has entered into a limited number of agreements to supply **multiple gigawatts of TPU hardware** to customers who require or provide on-premises infrastructure

RPO 가 `$242.8B → $467.6B → $519.5B` 로 폭증했으나 **고객사별 분리가 없다.** `$200B/5년` 도 훈련·서빙 구분도 **확인 불가**다.

## `OpenAI 27%` 의 정체

**Microsoft 가 가진 OpenAI 지분율**이다. v1.5 원본 세 곳에서 확인했다(채점표 188·198행, 규칙 217행).

즉 근거란의 `공급자 3사가 전부 경쟁자(Gemini·Nova·OpenAI 27%)` 는 **Google · Amazon · Microsoft** 를 말하고, 셋째가 Microsoft 인 이유로 **그 회사가 OpenAI 지분 27% 를 들고 있다**는 사실을 든 것이다. Anthropic 쪽 연결은 `Anthropic Azure $30B 약정` 이다.

**근거란만 읽고는 이 연결이 안 보인다.** 규명한 것이 값을 한다.

---

## 그래서 전제는 반만 성립한다

```
약정액 기준       Google $200B/5년(≈$40B/년) · AWS $100B/10년(≈$10B/년) · Azure $30B
                  → 3사 분산. 성립한다

훈련 컴퓨트 기준   AWS   Trainium2 500,000+ · 최대 5GW · "train" 공시 확정
                  Google 미공시 (사명 0건)
                  Azure  미공시
                  → 확인된 훈련 원천은 AWS 하나뿐
```

**"돈은 분산, 훈련은 AWS" 라는 v1.5 의 긴장이 한쪽만 확정됐다.**

**그러나 `Google 이 훈련에 안 쓰인다` 는 증거는 없다.** 공시가 없을 뿐이다. **없음을 확인한 것이 아니라 확인이 안 된 것**이고, 그 둘을 가르는 것이 오늘 하루 종일 한 일이다.

## F8 점수 판정 — **−3 을 유지한다**

**내릴 근거가 부족하다.**

`−4` 로 내리려면 **"실질은 단일 의존"** 이 서야 하는데, 그러려면 **Google 몫이 훈련이 아니라는 것**이 필요하다. 지금 있는 것은 **Alphabet 이 아무 말도 안 한다**는 사실뿐이다. **미공시를 "아니다" 로 읽으면 오늘 `not_disclosed` 에서 고친 실수를 F8 에서 반복한다.**

**`−3` 을 유지하되 근거란을 고쳐 쓴다.**

| 지금 | 고칠 것 |
|---|---|
| "DS투자증권(9/7) 증언" | **Amazon 8-K 4건**(접수번호 포함) |
| "미확인 → 긴장 #10" | **AWS 훈련은 공시 확정 · Google 은 사명 0건으로 확인 불가** |
| `OpenAI 27%` | **Microsoft 의 OpenAI 지분율**임을 명시 |

**증거의 등급이 2차 증언에서 1차 공시로 올라갔는데 점수는 그대로다.** 그 사실 자체를 적어야 다음 사람이 "또 미확인이네" 하고 같은 조사를 반복하지 않는다.

## 재판정 조건을 명시한다

```
F8 -4 로 내리는 조건
  Alphabet 이 Anthropic 관련 약정을 고객사별로 분리 공시하거나
  Anthropic 이 훈련 컴퓨트 구성을 공시하거나
  Google 몫이 서빙 전용임이 1차 자료로 확인될 때
```

**조건을 적어 두면 그때 자동으로 걸린다.** `HANDOVER` 118행이 이미 `Anthropic 훈련 컴퓨트가 AWS 단일인지(⑧-3→-4 조건)` 라고 적어 뒀는데, **조건만 있고 무엇이 확인되면 성립하는지가 없었다.**

## 조사 규율

`anthropic.com`·DS투자증권 **조회 0건**. 공급사가 상장사라는 점을 이용해 **SEC 로 우회한 것**이 이번 설계의 핵심이고, 지시서에 적은 대로다. v1.5 원본을 먼저 훑어 인용 행 번호(채점표 349~355·360·1120행, HANDOVER 118행)를 남긴 것도 맞다.

검증기 6건 통과.

## 후속

| 건 | 처리 |
|---|---|
| **F8 점수** | **−3 유지** |
| **근거란 교체** | worker — 8-K 접수번호 4건 · `OpenAI 27%` 규명 · 확인/미확인 분리 |
| **재판정 조건 등재** | 위 셋 중 하나가 확인되면 −4 재검토 |
| 승인 실행 반영 | `PRIV-IMPL-31` 보완과 함께 |
