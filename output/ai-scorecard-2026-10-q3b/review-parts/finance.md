---
reviewer_agent: claude-sonnet-5-5 재무 계산 리뷰어
session: claude-q3b-review-2026-10-23
reviewed_at: 2026-10-23
area: financial-calc
results_hash: 76e9bc29df34f1e57d56c5a96792eb322c2de068a3944bc07c776aebc77bc753
---
검토자: claude-sonnet-5-5 (재무 계산 영역, 별도 세션)
결과: pass

## RESULT

- 결과는 pass 다. Anthropic ⑤ 7 과 OpenAI ⑤ 6 은 규칙 JSON `scorecard/rules/v3.1.json` 의 F5 명세(지분 동맹 0곳 0·1곳 2·2곳 이상 3, 한 관계는 한 부분, 미확인 비율 40%)와 `results.json` 의 `factors.F5.calc` 가 같고, 판단 입력에서 손으로 다시 계산한 값과도 같다. 두 회사의 ⑥·⑨ 는 q3a 와 점수와 계산 경로가 한 글자도 다르지 않다.
- 묶임 증거의 금액(Amazon 금융 한도 최대 $200억·잔액 $150억, Google 조건부 $300억)은 원문 숫자·단위·기간과 모두 맞는다. 이 실행에서 새로 적힌 다른 금액(Microsoft $50억, AMD $50억, NVIDIA $100억, Microsoft 10-K 출자 약정 $130억 중 $119억, Amazon OpenAI 약정 $350억 중 남은 $213억 등)도 원문과 맞는다.
- 점수·순위·체크리스트 판정을 바꾸는 발견은 없다. 다만 F-01(승계한 트리거 TRG-163 이 "Anthropic ⑤ 의 동맹은 0 이다" 라고 적어 새 점수와 어긋남)은 확인 전에 정정하는 편이 좋다. 트리거를 고치면 트리거 해시가 바뀌어 `draft` 를 다시 렌더링해야 하므로, 사람이 확인을 누르기 전에 처리하면 비용이 가장 작다.
- 이 실행의 재무 관측은 새로 들어오지 않았다. `observations.json` 은 q3a 와 항목 1,086건이 통째로 같다. 가격·시가총액은 범위 밖이다.

### 재계산 결과

| 회사 | 중립 | 동맹 A | 적대 H | 합 | 반올림 | `results.json` |
| --- | --- | --- | --- | --- | --- | --- |
| Anthropic | 12 | 3 (지분 동맹 2곳 → 3, 경쟁사 편입 0, 상업 동맹 폭 0) | −8.32 | 6.68 | 7 | 7 |
| OpenAI | 12 | 2 (지분 동맹 1곳 → 2, 경쟁사 편입 0, 상업 동맹 폭 0) | −8.32 | 5.68 | 6 | 6 |

- **동맹 A 배정.** Anthropic 은 Amazon 과 Google 을 모두 `equity` 로만 적었고 `calc.assignment` 도 두 곳 모두 `equity` 다. 한 관계가 두 부분에 들어간 줄이 없고(`part_points` 는 equity 3.0, 나머지 0.0), 지분 동맹 칸 2곳 이상은 3 이라 A = 3 이다. OpenAI 는 SoftBank 합작(SB OAI Japan) 하나만 `equity` 이고 1곳은 2 라 A = 2 다. 받은 투자로 더한 투자자가 없다는 판단 문장과 `assignment` 가 같다.
- **적대 H, Anthropic.** 판단 입력의 비용형 전선은 넷(국방부·FTC·EU AI Office·Reservoir)이다. 구제 조치 진행은 국방부 하나가 `yes` 라 −2 가 붙고, 관할은 미국·EU 둘이라 3곳 조건(−2)은 서지 않는다. 그래서 구조형 전선을 빼면 기본 −2 + −2 = −4 다. 구조형인지 미확인인 전선 셋(Cursor·GitHub Copilot·Meta)을 모두 구조형으로 세면 구조형 전선이 셋이고 최대 파트너와의 긴장이 `unknown` 이라 −12 + 0.4 × (−10 − (−12)) = −11.2 다. 규칙 문언대로 나쁜 쪽 −11.2 에서 좋은 쪽 −4 로 40% 가면 −11.2 + 0.4 × 7.2 = −8.32 이고 `calc.H` 와 같다. Reservoir 전선이 q3a 보다 하나 늘었지만 관할이 미국이고 구제 조치가 없어 좋은 쪽 값 −4 는 q3a 와 같다.
- **적대 H, OpenAI.** 비용형 전선은 열다섯(미국 열셋, EU 하나, 캐나다 하나. `calc.ongoing` 열일곱 가운데 미확인 둘을 뺀 수)이다. 구제 조치 진행은 전부 `no` 라 −2 는 붙지 않고, 관할이 미국·EU·캐나다 셋이라 3곳 조건 −2 가 붙어 기본 −2 + −2 = −4 다. 미확인 전선 둘(Cursor, Musk 영리 전환 청구)을 구조형으로 세면 −11.2 이고 나머지 계산은 Anthropic 과 같아 −8.32 다. 판단 입력의 `ongoing` 이름 열일곱과 `calc.ongoing` 이 순서까지 같다.
- **미확인 비율.** 규칙 JSON `scoring.unknown_share` 는 0.4 이고 `calc_qual._hostility` 가 이 값 하나로 두 번(구조형 전선 둘 이상의 긴장 미확인, 전선의 구조형 여부 미확인) 쓴다. 금액은 어느 줄에도 들어가지 않는다(`amounts_used: false`, `calc` 에 금액 필드 없음).
- **반올림 경계.** 6.68 과 5.68 은 정수 경계(.5)에서 0.18 씩 떨어져 있어 사사오입 규칙에 따라 흔들리지 않는다.

### q3a 와 비교(전 회사 factor 전수)

`results.json` 두 파일을 회사 14곳 × 항목 9개 전부 대조했다.

- 점수가 바뀐 칸은 Anthropic ⑤ 4 → 7 하나다. 총점 −13 → −10, 과점 26 → 29, 함정 −39 그대로이고 순위 14위도 그대로다(OpenAI −6, 13위).
- OpenAI 는 ①~⑨ 점수와 `calc` 가 q3a 와 같다. ⑤ 는 6 → 6 이고 `calc` 도 같다(판단 입력은 SoftBank 줄의 설명 문장만 달라졌다).
- Anthropic ⑥ −11(P2 27.7, 포스트머니 $965.0B ÷ 런레이트 $65.0B 가 범위 중간값 27.7)과 ⑨ −8(G1 판정 보류, G2 비상장 미공시 −8)은 q3a 와 `calc` 까지 같다. OpenAI ⑥ −14(P2 34.92 → −13.948, 포스트머니 $852B ÷ 런레이트 $50B)와 ⑨ −8 도 같다.
- 상장사 12곳의 ⑥ `calc` 는 `p4.stale_asof.as_of` 한 필드만 2026-10-22 → 2026-10-23 으로 달라졌고 `hit: false`, 경과 개월 3(한도 6)이라 감점도 점수도 같다. 실행 기준일만 옮긴 효과이며 가격 관측은 q3a 것이다(범위 밖).
- 순위·총점·`ranking` 표는 draft.md 요약표(13행 OpenAI −6, 14행 Anthropic −10)와 같다.

### ⑤ 민감도(확인 리뷰가 알아야 할 것)

두 회사의 ⑤ 는 받은 투자 판정에 점수가 걸려 있다. 판정이 한 곳만 바뀌어도 한 칸이 움직인다.

| 가정 | Anthropic A → ⑤ | OpenAI A → ⑤ |
| --- | --- | --- |
| 지금 판정 | 3 → 6.68 → 7 | 2 → 5.68 → 6 |
| 받은 투자 한 곳을 더 센다(OpenAI 는 Microsoft·Amazon·NVIDIA 가운데 하나) | 변화 없음(상한 3) | 3 → 6.68 → 7 |
| Anthropic 에서 Amazon 또는 Google 한 곳을 뺀다 | 2 → 5.68 → 6 | — |
| Anthropic 에서 둘 다 뺀다(이전 규칙) | 0 → 3.68 → 4 | — |

OpenAI 에서 Microsoft 를 세지 않은 이유는 GitHub Copilot 에 자체 모델을 넣은 것이 헤지로 읽혔기 때문이다. 이 판정은 규칙 일관성 영역의 몫이고 이 영역은 계산이 판정을 그대로 따르는지만 본다.

## FINDINGS

### F-01 (중간, 표시 불일치, 점수 영향 없음) Anthropic TRG-163 이 새 ⑤ 와 반대로 적혀 있다

- **무엇이.** `triggers.json` 의 TRG-163(Anthropic ⑤)은 q3a 에서 승계한 트리거인데 관찰 문장이 "세 회사의 Anthropic 지분은 받은 투자라 동맹으로 세지 않는다. Anthropic ⑤ 의 동맹은 0 이다" 로 남아 있다. 이번 실행의 ⑤ 는 동맹 3(Amazon·Google 지분 동맹)이고, TRG-380·381 이 그 두 관계를 따로 적었다. draft.md 의 트리거 표(5808행)에도 이 문장이 그대로 실려 한 표 안에서 TRG-163 은 동맹 0, TRG-380·381 은 지분 동맹이라고 말한다. 승계 기록(`carry.finding`)은 갱신됐지만 관찰 문장은 q3a 때 것이다.
- **근거.** `results.json` Anthropic `factors.F5.calc.A` = 3.0, `assignment` = Amazon·Google `equity`. 판단 `anthropic.F5` 의 relations 두 줄. TRG-163 의 `observation` 마지막 두 문장. AGENTS.md 「판단 근거·근거 문장·트리거는 현재 상태 문장」 지침.
- **고치는 법.** TRG-163 관찰을 "Amazon·Google·Microsoft 가 Bedrock·Vertex AI·Foundry 로 Claude 를 되파는 관계는 세 회사 모두 자기 모델을 출하하고 여러 모델을 바꿔 쓰게 해 상업 동맹에 넣지 않는다. 세 회사의 Anthropic 지분 가운데 Amazon·Google 은 묶임 증거가 있어 지분 동맹으로 센다(TRG-380·381). Microsoft 는 묶임 증거가 없어 세지 않는다" 정도로 문장 전체를 다시 쓴다. 점수는 바뀌지 않으며 트리거 해시가 바뀌므로 `draft` 를 다시 렌더링한다.

### F-02 (낮음) EV-anthropic-171 이 어느 판단에서도 인용되지 않았고 ⑨ 근거 문장이 이를 다루지 않는다

- **무엇이.** 이 실행에서 확정한 EV-anthropic-171(Motley Fool 2026-10-22, 투자자 설명회에서 Anthropic 이 조정 기준 흑자 2분기 연속과 잉여현금흐름 흑자를 밝혔다는 2차 보도)은 `factors` 가 ⑥·⑨ 로 달려 있지만 판단 문장 어디에도 ID 가 나오지 않는다. 증거 자신의 `relevance` 는 "⑨ 게이트 2 의 입력으로 쓰지 않는다" 고 적는다. 그런데 `anthropic.F9` 판단은 "2026년 3분기 조정 기준 흑자를 투자자에게 알렸지만(2차 보도)" 라고만 쓰고 근거 표지가 없으며, 잉여현금흐름 흑자 주장은 언급하지 않고, 증거는 "2분기 연속"이라는데 "3분기"라고 쓴다.
- **근거.** `evidence.json` EV-anthropic-171 의 `excerpt`·`relevance`·`unverified`. `judgments.json` `anthropic.F9` 의 첫 근거 줄. `anthropic.F9` 의 `reconfirmed` 에 EV-171 이 빠져 있다.
- **영향.** 점수는 바뀌지 않는다. 게이트 2 는 금액과 기간이 없는 회사 발표의 2차 보도라 계속 "미공시 −8" 이 맞고, 보도에 잉여현금흐름 금액·기간·정의가 없다(증거 `unverified` 에 적혀 있다). 문제는 확정 증거가 쓰이지도 버려지지도 않은 채 남았다는 것이다.
- **고치는 법.** 다음 실행에서 ⑨ 판정 칸에 "회사가 잉여현금흐름 흑자를 말했다는 2차 보도가 있으나 금액·기간·정의가 없어 게이트 2 입력으로 쓰지 않는다(미확인)" 를 적고 EV-171 을 `reconfirmed` 에 올린다.

### F-03 (낮음) EV-anthropic-172 의 `relevance` 가 규칙의 좁은 헤지 읽기보다 넓다

- **무엇이.** 증거의 `relevance` 끝 문장은 "Google 이 자체 Gemini 를 주력으로 두는 헤지가 확인되면 지분 동맹으로 세지 않는다" 라고 적는다. 규칙 3절 ⑤ 는 "투자자가 자체 모델을 가졌다는 사실이나 다른 회사에도 출자했다는 사실만으로는 풀리지 않는다" 이고, 판단 문장 자체는 이 읽기를 지킨다(Claude 는 처음부터 Google 주력이 아니었고 제공을 넓히는 중이라 헤지가 아님). 증거 쪽 한 문장만 넓은 읽기를 닮았다.
- **영향.** 점수는 바뀌지 않는다. 다음 실행에서 증거를 읽는 사람이 Gemini 가 주력이라는 사실만으로 Google 동맹을 풀 위험이 있다.
- **고치는 법.** 다음 실행에서 그 문장을 "Google 이 Claude 를 Vertex AI·Antigravity 에서 내리거나 그 자리에 경쟁 모델을 올린 것이 확인되면" 으로 다시 쓴다.

### F-04 (참고, 규칙 일관성 영역으로 넘김) Amazon 금융 한도의 성격

- 금액·단위·기간은 원문과 정확히 같다. 다만 Amazon 10-Q 는 이 한도를 Anthropic 이 임의로 인출하는 금융 약정(인출분은 새 Anthropic 전환사채, 유동화 뒤에는 보유 한도 안의 보통주)으로 적고 "이정표 조건부 추가 출자 약정" 이라는 말은 판단 문장의 해석이다. 규칙 문언의 "이정표 조건부 추가 출자 약정" 에 드는지는 규칙 일관성 리뷰어가 가릴 문제이고, 가려진 결과가 점수에 닿는 정도는 위 민감도 표에 있다(Amazon 을 빼면 Anthropic ⑤ 7 → 6).

## 원문 대조 결과(오류 없음)

원문은 `evidence.json` 의 `excerpt` 와 `locator` 로 확인했다. 금액·단위를 하나씩 비교했다.

| 판단 문장의 숫자 | 원문 | 결과 |
| --- | --- | --- |
| Amazon 금융 한도 최대 $200억 | Amazon 10-Q(2026-06-30) Note 2 "aggregate facility not to exceed $20.0 billion" (EV-amazon-078) | 일치 |
| 잔액 $150억 | 같은 문장 "reduced the amount available under the facility to $15.0 billion" (EV-amazon-078·087) | 일치 |
| 시리즈 H $50억 | 10-Q "investing $5.0 billion in Anthropic Series H nonvoting preferred stock" (EV-amazon-087). 시리즈 G $5.0B 는 별개 투자(EV-amazon-018) | 일치 |
| 한도가 컴퓨트 인도 이정표에 걸림, 인출은 전환사채 또는 상장 뒤 보통주 | EV-amazon-086 "as we reach certain delivery milestones … Draws … convertible notes or … common stock" | 일치 |
| 유동화 뒤 30개월 만료 | EV-amazon-078 "expire 30 months after an Anthropic liquidity event" | 일치 |
| Amazon 이 지금 $50억, 앞으로 최대 $200억 | Anthropic 발표 2026-04-20 "investing $5 billion … up to an additional $20 billion" (EV-amazon-039) | 일치 |
| Google 지금 $100억 현금, 성과 목표 시 $300억 추가 | Bloomberg Law 2026-04-24 "invest $10 billion now in cash … another $30 billion if Anthropic hits performance targets" (EV-anthropic-172). Fortune 2026-07-22 도 "commitments of up to $30 billion more" (EV-alphabet-018) | 일치, 기준일(10-23) 전에 집행·종료 보도 없음 |
| 근거 등급 | EV-172 는 회사 발표를 전한 2차 보도, 판단 문장이 등급을 적었고 유출 문서가 아님 | 규칙 문언과 일치 |
| Amazon OpenAI 시리즈 C $150억 + 약정 $350억(합 $500억), 남은 $213억 모두 집행 | 10-Q "invested $15.0 billion … $35.0 billion … In Q2 2026, $13.7 billion … remaining $21.3 billion" (EV-amazon-019·020). 13.7 + 21.3 = 35.0 | 일치 |
| AWS–Anthropic 약정 10년 $1,000억 넘게 증액 | 10-Q "more than $100.0 billion over 10.0 years" (EV-amazon-017) | 일치 |
| Microsoft 최대 $50억, NVIDIA 최대 $100억 (Anthropic) | Anthropic 발표 2025-11-18 "up to $10 billion and up to $5 billion respectively" (EV-anthropic-121) | 일치 |
| AMD 최대 $50억 지분 투자 약속 | AMD 보도자료 2026-07-22 "strategic equity investment of up to $5 billion … in the future" (EV-anthropic-119) | 일치 |
| Microsoft OpenAI 지분 약 25%(전환 기준), 약정 $130억 중 $119억 | Microsoft 10-K FY2026 "approximate 25% … $13.0 billion … $11.9 billion" (EV-microsoft-014) | 일치 |
| Microsoft 완전 희석 약 27% | 2025-10-28 공동 발표 "roughly 27 percent" (EV-openai-121) | 일치 |
| Microsoft Anthropic 평가이익 $32억 | 2026-07-29 통화 "a $3.2 billion gain from our investment in Anthropic" (EV-microsoft-074) | 일치 |
| NVIDIA OpenAI $300억(2차 보도), 의향서 $1,000억 | EV-nvidia-043 "$30 billion check", EV-openai-124 "intends to invest up to $100 billion" | 일치, 의향서 문장 일치 |
| SoftBank OpenAI 직접 지분 약 13%(2차 집계) | EV-openai-030 "~13% direct OpenAI stake" | 일치 |
| OpenAI 합작 SB OAI Japan 50%·50% | EV-openai-165 "C Holdings Corporation: 50%, OpenAI: 50%" | 일치 |
| OpenAI 최대 $300억 라운드(UAE 주도) | EV-openai-182 "raising up to $30 billion" | 일치 |
| Reservoir 소송 2026-10-21 연방 소송 | EV-anthropic-164 "filed … Wednesday (Oct. 21)" | 일치 |

- 단위 환산(달러 억 단위 표기)은 모든 줄에서 맞다($20.0 billion → $200억, $15.0 billion → $150억, $30 billion → $300억).
- 기준일 처리. 이 판단들의 숫자는 모두 기준일(2026-10-23) 이전 원문이다. 기준일 뒤 일정(OpenAI 의 UAE 계약 서명 목표 2026-10-30, Cursor 공급 종료 통지 2026-11-12)은 점수에 넣지 않았다.

## CHECKLIST

재무 영역에 해당하는 문항만 적는다.

| 문항 | 결과 | 비고 |
| --- | --- | --- |
| Q04 시총 크기를 밸류에이션으로 착각했나 | 해당 없음 | 가격·시가총액은 이번 리뷰 범위 밖이고 q3a 와 같은 관측이다. 두 회사는 비상장이라 포스트머니와 런레이트로 센다 |
| Q09 미래 계획을 현재 점수에 넣었나 | pass | Google $300억·Amazon $150억 잔액은 살아 있는 조건부 약정으로 세는 규칙 문언에 따르고 금액은 점수에 들어가지 않는다. 집행 전 금액을 환산한 값은 없다 |
| Q11 순적자를 실격 사유로 썼나 | pass | Anthropic ⑨ 는 G1 판정 보류(통과도 실격도 아님)·G2 비상장 미공시 −8 이고 q3a 와 같다. 적자 자체로 실격시키지 않았다 |
| Q19 받은 투자를 곧바로 지분 동맹으로 셌나, 한 관계를 두 부분에서 셌나 | pass | 계산 경로 기준. Amazon·Google 은 묶임 증거(조건부 추가 출자 약정)를 근거 ID 와 함께 갖췄고, 한 관계는 `equity` 한 부분에만 들어가며 상업 동맹 폭에 다시 세지 않았다. 증거 해석(F-04)은 규칙 일관성 영역의 몫 |
| Q22 지분 평가이익을 ⑦ 순환금융 증거로 셌나 | pass | Microsoft Anthropic 평가이익 $32억은 OpenAI ⑤ 판단의 배경 줄로만 적혀 있다. ⑦ 입력 두 회사 모두 q3a 와 같다 |

## 다음 실행 과제

- 승계 트리거는 `carry.finding` 만 갱신하지 말고 관찰 문장이 새 점수와 맞는지도 함께 읽는다(F-01).
- 증거 `relevance` 문장은 규칙 문언이 바뀔 때 함께 다시 쓴다(F-03). 전 증거를 규칙 문언으로 거꾸로 훑는 전수 점검을 한 번 하는 편이 낫다.
- 확정한 증거가 판단에서 쓰이지 않으면 쓰지 않은 이유를 해당 항목 판정 칸에 한 줄 남긴다(F-02).
- 다른 영역 리뷰어가 볼 참고 두 가지다. ① OpenAI 판단 항목 아홉 개의 `reconfirmed` 마지막 기록이 모두 q3a 단계(실적 반영 2단계) 것이고 q3b 세션 기록은 없다. Anthropic 은 ②를 뺀 여덟 항목에 q3b 기록이 있다. ② Anthropic `F2.model` 은 입력 `gap_months` 가 0 에서 1 로 바뀌었는데 `reconfirmed` 기록이 없다. ②의 점수와 `calc` 는 q3a 와 같다(⑤ 이외에 바뀐 점수 칸이 없다는 위 대조로 확인).
- 확인 리뷰가 볼 것. OpenAI ⑥ 의 포스트머니 $852B 는 완결된 라운드 값이다. 10-23 Bloomberg 보도는 진행 중인 새 라운드를 $1.25조(신규 자금 제외)로 전하고 아직 마감 전이라 이번 실행의 입력은 그대로 맞다. 라운드가 마감되면 ⑥ 입력을 다시 읽는다.
