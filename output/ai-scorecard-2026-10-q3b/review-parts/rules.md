---
reviewer_agent: claude-opus-5-5 규칙 일관성 리뷰어
session: claude-q3b-review-2026-10-23
reviewed_at: 2026-10-23
area: rule-consistency
results_hash: 76e9bc29df34f1e57d56c5a96792eb322c2de068a3944bc07c776aebc77bc753
---
검토자: claude-opus-5-5 (규칙 일관성 영역, 별도 세션)
결과: needs_fix

## RESULT

needs_fix. Anthropic ⑤ 는 새 규칙(묶임 증거 셋, 좁은 헤지)을 문언대로 댔다. OpenAI ⑤ 는 좁은 헤지 결정(커밋 553186f, 2026-10-23 14:03) 전에 쓴 판단을 그대로 두어, Microsoft·Amazon 줄이 넓은 헤지 읽기로 서 있다. Microsoft 줄은 고치는 방법에 따라 점수가 6 → 7 로 바뀔 수 있다(F1). 같은 OpenAI–Microsoft 관계를 Microsoft ⑤ 는 "최대 파트너와 긴장 있음", OpenAI ⑤ 는 "긴장 미확인"으로 읽어 OpenAI ⑤ 점수에 닿는다(F2). 받은 투자 규칙이 바뀌었는데 받은 투자를 옛 규칙("받은 투자라 세지 않는다")으로 판정한 SpaceX ⑤·TSMC ⑤ 가 범위 밖에 남았고, TSMC 는 다시 매기면 순위 3·4위가 뒤바뀔 수 있다(F3). 그래서 Q03 은 fail 이다. 받은 투자와 맺은 투자를 양쪽에서 세는 것은 Q21 에 걸리지 않는다(아래 2절).

판단 파일은 조율자 알림대로 그대로이고, 트리거 TRG-163 과 EV-anthropic-172·165·169 의 relevance·conditional_impact 는 고친 뒤 파일 기준으로 다시 읽었다. 다시 읽은 문장에 새 어긋남은 없다. `diff ai-scorecard-2026-10-q3b --against ai-scorecard-2026-10-q3a` 를 다시 돌렸고 1층·2층 통과, 범위 안 판단 변화 18건, 점수 변화는 Anthropic ⑤ 4 → 7 하나다.

## FINDINGS

### F1 (높음, needs_fix) — OpenAI ⑤ Microsoft·Amazon 줄이 좁은 헤지가 아니라 넓은 헤지로 서 있다

- **무엇이.** OpenAI ⑤ 판정 칸 셋째 문장이 규칙을 "투자자가 자체 모델이나 다른 회사 모델을 주력에 올린 헤지가 확인되면 세지 않는다"로 옮겨 적는다. 넷째 문장은 "규칙은 투자자가 주력에서 내 제품을 내리거나 헤지가 확인되면 묶임이 풀린 것으로 보므로, Copilot 이 OpenAI 모델을 내리지 않았어도 헤지가 확인된 Microsoft 는 주력 편입이 있어도 세지 않는다"고 적는다. 둘 다 2026-10-23 첫 결정(커밋 367f7f5)의 문언이다. 현행 규칙(rules.md ⑤ 「아군 확보는 묶임이다」)은 "투자자가 내 제품을 자기 주력에서 내렸거나 그 자리에 경쟁 모델·제품을 올린 것이 확인될 때만 풀린 것으로 보고 … 투자자가 자체 모델을 가졌다는 사실이나 다른 회사에도 출자했다는 사실만으로는 풀리지 않는다"이다. 판단의 수정 기록(revision_history 마지막 줄)도 사유를 "⑤ 받은 투자 절충안"으로만 적고 좁은 읽기를 적지 않는다. Anthropic ⑤ 만 후속 명세(`judge_spec_followup.json`)로 좁은 읽기를 받았다.
- **Microsoft 줄의 헤지 근거 넷을 좁은 읽기에 대면 이렇다.**
  - Qwen 을 후학습한 결정 모델(EV-alibaba-073)과 Anthropic 지분 평가이익(EV-microsoft-074)은 규칙이 "그것만으로는 풀리지 않는다"고 적은 자체 모델 보유와 다른 회사 출자다.
  - Copilot 제품군에 Claude 를 계속 제공한다는 약속(EV-microsoft-015)은 Anthropic ⑤ 가 같은 근거를 "다른 모델과 나란히 Claude 를 계속 올린다는 것"이라 주력 편입이 아니라고 읽은 사건이다. 한 사건을 Anthropic 쪽에서는 '나란히 올림'으로, OpenAI 쪽에서는 'OpenAI 자리에 경쟁 모델을 올림'으로 읽었다.
  - GitHub Copilot 의 MAI-Code-1-Flash(EV-microsoft-010)의 원문은 수백만 개발자가 MAI 를 쓰면서도 "still having access to frontier capabilities from OpenAI and Anthropic"이라고 적는다. 나란히 올렸다는 것만 확인되고 OpenAI 가 맡던 자리(기본 모델·코드 완성)를 MAI 가 넘겨받았다는 것은 확인되지 않는다. Anthropic ⑤ 는 Amazon 이 OpenAI 를 Bedrock Managed Agents 와 자기 서비스에 들인 것(EV-amazon-102·091)을 "Claude 가 맡던 자리를 바꿨다는 확정 근거가 없어" 헤지가 아니라고 읽었다. 같은 모양의 사실이 두 회사에서 반대로 풀렸다. 확인되지 않은 교체를 Anthropic 에서는 묶임 유지 쪽으로, OpenAI 에서는 풀림 쪽으로 풀었다(미확인 방향표 U4).
- **판단 안의 어긋남.** 같은 판단의 상업 동맹 문장은 Microsoft 가 "GitHub Copilot 에 자체 모델을 넣고 … 상대가 떠날 수 있어" 상업 동맹에서 뺀다고 적는다. Microsoft 는 EV-microsoft-010 에서 자기 제품의 "every model is substitutable"이라고 밝혔다. 그런데 지분 동맹 문장은 주력 편입(투자자 제품의 핵심에 넣어 '바꾸기 어려움')을 "확인된다"고 적는다. 한 판단 안에서 Microsoft 가 떠날 수 있다는 읽기와 바꾸기 어렵다는 읽기가 함께 선다.
- **Amazon 줄.** "Amazon 은 Anthropic 에도 출자했으며 AWS 는 Anthropic 과의 약정을 10년 $1,000억 넘게 늘렸다. … 헤지가 확인된다"는 규칙이 풀림 사유에서 뺀 다른 회사 출자를 헤지로 읽는다. 같은 Amazon 의 이중 출자를 Anthropic ⑤ 는 헤지가 아니라고 읽었다(사건 교차표 E1). 결론(세지 않음)은 남은 약정 없음·재량 매수(EV-amazon-019·020), AWS 독점 유통이 OpenAI 를 묶는 조항(EV-openai-123), 주력 편입 미확인만으로 선다. 그래서 이 줄은 점수에 닿지 않고 문장만 고치면 된다.
- **점수 영향.** 판단이 스스로 적은 대로 주력 편입이 서고 좁은 읽기로 헤지가 확인되지 않으면, Microsoft 가 지분 동맹 둘째 곳이 된다. 지분 동맹 3 → A 3 → ⑤ = 12 + 3 − 8.32 = 6.68 → 7 이다(조정총점 −6 → −5, 순위 13 그대로). F2 와 함께 바뀌면 5~7 사이다.
- **고치는 법.** 판단 세션(Opus, high)이 OpenAI ⑤ 의 받은 투자 문장을 현행 좁은 읽기로 다시 쓴다. 셋 가운데 하나로 정하고, 정한 이유를 Anthropic ⑤ 의 같은 사건 읽기와 나란히 적는다.
  - (가) 주력 편입은 서고 'OpenAI 자리에 경쟁 모델을 올림'은 확인되지 않는다 → Microsoft 를 지분 동맹으로 센다(⑤ 7).
  - (나) 'OpenAI 자리'를 MAI 가 넘겨받았다는 원문(기본 모델 교체 등)을 공시·Microsoft 1차 발표로 확정해 인용한다 → 헤지(⑤ 6). 이때 Qwen·Claude 병행·Anthropic 평가이익은 헤지 근거에서 뺀다.
  - (다) 주력 편입의 '바꾸기 어려움'이 서지 않는다고 다시 판정한다(EV-microsoft-010 "every model is substitutable", EV-microsoft-071 Maia 가 OpenAI·MAI·오픈소스를 함께 돌림, 같은 판단의 상업 동맹 문장과 일치) → 묶임 증거 없음(⑤ 6).
  - 리뷰어는 (다)가 1차 근거와 판단 안의 다른 문장에 가장 잘 맞는다고 본다. 다만 조율자 메모(context-notes D8 줄)는 "Microsoft 가 GitHub Copilot 에 자체 모델을 '그 자리에' 넣었다"로 (나)를 전제했다. 그 전제를 받치는 원문은 확정 근거에 없다.
  - 어느 쪽이든 Amazon 줄에서 "헤지가 확인된다"와 Anthropic 출자·AWS 약정 확대 근거를 빼고 묶임 증거 부재로만 적는다. 판정 칸 셋째 문장의 규칙 요약도 현행 문언으로 다시 쓴다.

### F2 (중간, needs_fix) — 같은 OpenAI–Microsoft 관계의 '최대 파트너와의 긴장'을 두 회사가 반대로 읽었다

- **무엇이.** Microsoft ⑤ 는 `partner_tension: yes` 다. 근거는 "OpenAI 의 Amazon 계약에 Microsoft 가 법적 대응을 경고했다는 FT 보도"(EV-microsoft-018, EV-openai-041)와 "OpenAI 는 Microsoft 365 와 겹치는 문서 도구 Pages 를 냈다"(EV-microsoft-003, 2026-09-29)이다. OpenAI ⑤ 는 같은 쌍의 긴장을 `unknown` 으로 두고 FT 보도는 2026-04 개정 합의로 정리됐다고만 적는다. Pages(EV-microsoft-003)는 다루지 않는다. 같은 관계의 같은 속성을 회사마다 다르게 읽었고, 이유는 관계의 종류도 자료의 유무도 아니다(사건 교차표 E5). Q03 fail 이다.
- **점수 영향.** OpenAI ⑤ 는 구조형인지 미확인인 전선이 둘이라 긴장이 다발형(−12)과 −10 을 가른다. 긴장 '있음'이면 H = −12 + 0.4 × 8 = −8.8 → ⑤ 5.2 → 5 이고(A 2 기준), A 3 이면 6.2 → 6 이다. Microsoft ⑤ 는 구조형 전선이 없어 어느 쪽이든 점수가 그대로다.
- **고치는 법.** 판단 세션이 두 회사에 같은 읽기를 댄다. Pages 출시 같은 경쟁 행위를 긴장으로 보면 OpenAI ⑤ 를 `yes` 로 고친다. 긴장이 아니라고 보면 Microsoft ⑤ 를 `scope ai-scorecard-2026-10-q3b --add microsoft:F5 --reason "OpenAI ⑤ 와 같은 관계의 최대 파트너 긴장을 같은 근거로 읽는다"` 로 범위에 넣고 FT 보도(개정으로 정리)와 Pages 의 읽기를 OpenAI ⑤ 와 맞춘다. 판정 칸에 상대 회사 판단과 같은 읽기임을 적는다.

### F3 (중간, needs_fix) — 받은 투자 규칙이 바뀌었는데 SpaceX ⑤·TSMC ⑤ 가 옛 규칙으로 남았다

- **무엇이.** 규칙 2.3 은 "한 회사에 새 잣대를 댔으면 같은 잣대가 닿는 모든 회사에 댄다"이다. 받은 투자는 이제 묶임 증거가 있으면 센다. 그런데 범위 밖에서 이어받은 두 판단은 받은 투자를 옛 문언 그대로 판정한다.
  - SpaceX ⑤: "Alphabet·NVIDIA 가 가진 SpaceX 지분과 Tesla 가 가진 SpaceX 보통주 … 는 받은 투자라 세지 않는다." Tesla 는 관계사(Q18)라 어느 규칙으로도 빠진다. Alphabet 은 SpaceX 컴퓨트를 32개월 사는 고객이다(2차 보도). NVIDIA 는 xAI 시절 투자자다. 두 곳의 묶임 증거를 가른 문장이 없다. 리뷰어가 확정 근거를 훑은 바로는 독점·우선 조항, 주력 편입(SpaceX ⑤ 스스로 Google 이 TPU 로 떠날 수 있다고 적음), 조건부 추가 출자를 보인 근거가 없다. 점수는 그대로일 가능성이 크다.
  - TSMC ⑤: "JASM(Sony·DENSO 등 소수 지분)과 ESMC(Bosch·Infineon·NXP 각 10%)는 … 받은 투자라 지분 동맹으로 세지 않는다"(EV-tsmc-102). 투자자가 TSMC 공정으로 자기 칩을 만드는 고객이라, 우선 배정이나 주력 편입 같은 묶임 증거가 있는지가 바로 쟁점이다. 그런데 갈라 본 적이 없다.
  - 합작 구조의 읽기도 회사마다 갈린다. OpenAI ⑤ 는 SoftBank 계열과 50% 씩 가진 합작법인 SB OAI Japan 을 "OpenAI 가 맺은 출자"로 지분 동맹에 센다(EV-openai-165). Oracle ⑤ 는 15% 를 가진 TikTok USDS 합작법인을 지분 동맹으로 센다. TSMC ⑤ 는 고객과 함께 가진 합작 자회사(TSMC 약 72.6%·70%)를 상대가 넣은 받은 투자로 읽는다. 지배 여부(연결 자회사 대 50% 합작)로 가를 수는 있다. 하지만 세 판단 어디에도 그 이유가 적혀 있지 않다.
- **점수 영향.** TSMC 가 지분 동맹 한 곳 이상을 얻으면 A 가 2 → 4 이상이 되어 ⑤ 12 → 14~15, 조정총점 32 → 34~35 다. Amazon(33, 3위)과 순위가 뒤바뀐다. SpaceX 는 바뀔 것으로 보이지 않는다.
- **고치는 법.** `scope ai-scorecard-2026-10-q3b --add tsmc:F5 --add spacex-xai:F5 --reason "⑤ 받은 투자 묶임 규칙(2026-10-23)이 두 회사의 받은 투자 판정에도 닿는다"` 로 범위에 넣는다. 판단 세션이 두 판단의 받은 투자를 묶임 증거 셋과 좁은 헤지로 다시 가른다. TSMC 는 합작 자회사를 받은 투자로 볼지 맺은 출자로 볼지를 OpenAI(SB OAI Japan)·Oracle(TikTok USDS)과 같은 기준으로 적는다. 묶임 증거가 공시·1차 발표에 없으면 세지 않는다.

### F4 (낮음, 점수 무관 — 같은 수정 묶음에서 고치기를 권함) — Anthropic ⑤ Google 약정 금액과 근거 등급

- Anthropic ⑤ 판정 칸과 TRG-381 은 Google 의 조건부 추가 출자를 "$300억 … 집행됐거나 끝났다는 근거가 없어 기준일에 살아 있는 약정"으로 적는다. 저장소 캐시의 Alphabet 10-Q 두 개는 이 수치와 다르다.
  - 2026-03-31 분기 10-Q(`data/_sec/docs/219b85127ea7ff73-goog-20260331.htm`, Note 5 VIE 와 MD&A 유동성 절): 비상장 회사 한 곳에 $10.0B 확정 출자와 "$30.0 billion of future capital funding contingent upon the achievement of specified operational and financial milestones through 2030"을 약정했다.
  - 2026-06-30 분기 10-Q(`…/46bdf3f925a3e8e7-goog-20260630.htm`, Note 5): 같은 조건부 약정이 "$20.0 billion"으로 줄었다.
  - 10-Q 는 회사 이름을 적지 않는다. 금액·시기(2026-03 약정, 2030 까지 이정표)가 Anthropic 발표(EV-anthropic-172)와 맞아 Anthropic 으로 읽는 것은 추론이다.
- 약정은 2030 까지 살아 있으므로 묶임 판정과 점수는 그대로다. 다만 "집행 근거 없음"과 "$300억"은 저장소 안 공시와 어긋난다. Amazon 쪽이 10-Q 로 선 것과 맞추려면 이 10-Q 를 근거로 확정해 등급을 공시로 올리고(이름 미기재는 같은 줄에 단서로), 금액을 2026-06-30 잔액 $200억으로 다시 쓴다. TRG-381 조건 문장도 같이 고친다.

### F5 (낮음, 점수 무관) — 확정된 F5 근거 EV-openai-185 가 어느 판단에도 인용되지 않았다

- Google Cloud 가 2026-10-21 OpenAI 모델을 Model Garden 에 들였다(EV-openai-185, factors F5, 비공개 시험). 근거의 relevance 는 이 사실이 OpenAI ⑤ 의 상업 유통과 Anthropic ⑤ 의 Google 관계 둘 다에 닿는다고 적는다. 그런데 두 판단 모두 이 사실을 다루지 않는다.
- 같은 잣대를 대면 결론은 바뀌지 않는다. OpenAI ⑤ 에서는 Google 이 Gemini 를 내 떠날 수 있어 상업 동맹이 아니다(Bedrock·Azure 재판매와 같다). Anthropic ⑤ 에서는 나란히 들인 것이라 Claude 자리 교체가 아니다. Google 의 묶임은 살아 있는 조건부 약정이라 헤지와 무관하기도 하다. 같은 사건이 Alphabet ⑤ 에도 닿지만 Alphabet 의 경쟁사 편입은 이미 3 이라 점수가 그대로다.
- 두 판단을 다시 쓸 때(F1) 이 사건을 판정 칸에 한 줄씩 넣기를 권한다. Amazon 의 같은 행동(OpenAI 를 Bedrock 에 들임)을 Anthropic ⑤ 가 다룬 것과 짝이 맞는다.

### F6 (낮음, 점수 무관) — 좁은 읽기에서 '풀리지 않는 사실'이 내릴 근거 칸에 있다

- 좁은 읽기로는 투자자의 다른 회사 출자·자체 모델 보유가 그것만으로 점수를 내리지 않는다. 그런데 다음 사실이 내릴 근거 칸에 있다.
  - Anthropic ⑤: Amazon 의 OpenAI 출자(EV-amazon-019·020), OpenAI 공동 협력(EV-amazon-091), Bedrock Managed Agents(EV-amazon-102), Gemini agent 의 모델 선택(EV-alphabet-070), Antigravity 목록의 Gemini(EV-anthropic-160).
  - OpenAI ⑤: Amazon 의 Anthropic 출자·약정(EV-amazon-018·017), Microsoft 의 Anthropic 평가이익(EV-microsoft-074), Qwen 결정 모델(EV-alibaba-073).
- guide 5.6 기준("이 사실 하나만 보면 점수가 오르는가 내리는가")으로는 판정 칸이 맞다. 두 회사가 같은 모양이라 Q03 문제는 아니다. F1 을 고칠 때 OpenAI 쪽은 옮기고, Anthropic 쪽은 다음 실행에서 맞춘다.

## 1. 투자자별 교차표 (Anthropic ⑤ ↔ OpenAI ⑤)

| 투자자 | Anthropic ⑤ 의 읽기 | OpenAI ⑤ 의 읽기 | 같은 원칙인가 |
|---|---|---|---|
| Amazon | 지분 동맹. 묶임 = 이정표 조건부 금융 한도 최대 $200억·잔액 $150억, 유동화 뒤 30개월(10-Q, EV-amazon-086·078·087). OpenAI 출자·공동 협력·Bedrock Managed Agents 는 Claude 를 내리거나 자리를 바꾼 근거가 없어 헤지 아님 | 세지 않음. 추가 약정 $350억 전액 납입·재량 매수, 이정표 조건 없음(10-Q). AWS 독점 유통은 OpenAI 를 묶음. 주력 편입 미확인. 판정 칸이 Anthropic 출자·AWS 약정 확대를 "헤지가 확인된다"로 덧붙임 | 결론은 같은 원칙(묶임 증거 유무)으로 선다. 덧붙인 헤지 문장만 좁은 읽기에 어긋난다(F1) |
| Google | 지분 동맹. 묶임 = 성과 목표 조건부 $300억(2차, EV-anthropic-172). Claude 는 Google 주력이 아니었으므로 내린 것이 아님. 조건부 약정이 살아 있는 동안 묶임 | 투자자 아님. Google Cloud 의 OpenAI 모델 제공(EV-openai-185)은 다루지 않음 | 같다. 금액·등급은 F4, 누락은 F5 |
| Microsoft | 세지 않음. 최대 $50억 약정에 조건·이정표 없음. Copilot 의 Claude 계속 제공은 나란히 올림이라 주력 편입 아님 | 세지 않음. 주력 편입은 확인(10-K IP 권리, Maia 가 Copilot 에서 OpenAI 모델 구동). 헤지를 넓게 읽어 풂(MAI 병행, Claude 병행, Qwen, Anthropic 평가이익) | 같지 않다. EV-microsoft-015 를 한쪽은 '나란히', 다른 쪽은 '교체'로 읽었다(F1) |
| NVIDIA | 세지 않음. 최대 $100억 약정에 조건·이정표·독점 없음. Claude 를 NVIDIA 제품에 넣는 관계 아님 | 세지 않음. 시스템 배치당 최대 $1,000억은 의향서이고 10-K 가 체결을 보장하지 않음(EV-openai-124·125). 10-Q 에 출자 약정 문장 없음 | 같다(묶임 증거 없음) |
| AMD | 세지 않음. 최대 $50억 약정에 조건 없음. AMD 는 GPU 공급자이고 엔지니어링 협력은 AMD 가 Claude 를 쓰는 것 | 받은 투자 아님. OpenAI 가 AMD 워런트를 받은 것은 공급 계약의 대가라 조달 | 같다(공급자에게서 오는 지분·약속은 묶임이 아님) |
| SoftBank | 해당 없음 | SB OAI Japan 50% 합작 = OpenAI 가 맺은 출자 한 곳. SoftBank 의 직접 지분은 같은 상대라 따로 세지 않음 | 해당. 합작 읽기는 TSMC 와 갈린다(F3) |

"Amazon 의 Anthropic 출자가 OpenAI 쪽 헤지가 아니고, Amazon 의 OpenAI 출자가 Anthropic 쪽 헤지가 아니다"는 현행 규칙 문언("다른 회사에도 출자했다는 사실만으로는 풀리지 않는다")이 정한 같은 원칙이다. Anthropic ⑤ 는 이 원칙대로 썼고, OpenAI ⑤ 는 반대 문장을 적었다(F1). Anthropic 의 두 묶임은 모두 조건부 추가 출자 약정이라, 규칙상 약정이 살아 있는 동안 헤지 여부와 무관하게 묶인다. 그래서 Anthropic 쪽은 헤지 읽기가 어떻게 정해져도 점수가 그대로다. OpenAI 쪽 Microsoft 만 주력 편입이 묶임 근거라 헤지 읽기가 점수를 가른다.

## 2. Q21 판정 — 받은 투자를 세는 쪽과 맺은 투자를 세는 쪽

- **회사 사이.** Anthropic ⑤ 는 Amazon·Google 을 받은 투자의 지분 동맹으로 센다. Amazon ⑤ 와 Alphabet ⑤ 는 Anthropic 을 맺은 출자와 경쟁사 편입으로 센다. 규칙은 "돈의 방향이 아니라 상대가 나를 떠나기 어려운지"를 각 회사의 ⑤ 에서 센다. Amazon ⑤ 의 속성은 'Anthropic 이 Amazon 을 떠나기 어렵다'(AWS 10년 약정, 자기 칩 미출하)이다. Anthropic ⑤ 의 속성은 'Amazon 이 Anthropic 을 떠나기 어렵다'(이정표 조건부 금융 한도)이다. 방향이 다른 두 속성이 각자 다른 회사의 점수에 들어가고, 2.2 의 이중 계산 금지는 한 회사 점수 안의 같은 속성에 걸린다. 그래서 Q21 에 걸리지 않는다. Alphabet–Anthropic 도 같다(TPU 약정 대 성과 목표 조건부 출자).
- **회사 안.** Anthropic ⑤(Amazon·Google 이 떠날 수 있나 = 네 질문의 3번)와 Anthropic ⑧ 공급·약정 축(Anthropic 이 AWS·Google 을 떠날 수 있나 = 4번)은 규칙이 "한 관계가 ⑤ 가점과 ⑧ 감점을 동시에 받을 수 있다"고 허용한 짝이다. Anthropic ⑤ 는 "컴퓨트 공급자가 모두 모델 경쟁자라는 의존은 ⑧ 에서만 센다"고 적어 공급자 경쟁 위험을 ⑤ 에서 다시 깎지 않는다. ⑦ 은 "Amazon·Google·Microsoft 가 Anthropic 에 투자하고 Anthropic 이 그 클라우드를 사는 구조는 투자자 쪽 ⑦ 과 Anthropic ⑧ 에서 다루고 여기서는 세지 않는다"고 적는다. 규칙의 "받은 투자가 투자자 매출로 돌아가는 것은 ⑦ 에서, 투자자에게 의존하는 것은 ⑧ 에서" 문언과 맞는다.
- 금융 한도의 인출 조건이 AWS 컴퓨트 인도라 ⑤(Amazon 의 지급 의무)와 ⑧(Anthropic 의 구매 약정)이 같은 계약에서 나온다. 하지만 한쪽은 상대의 의무, 다른 쪽은 나의 의무라 같은 속성이 아니다. Q21 pass.

## 3. 사건 교차표 (갱신 범위의 사건)

| # | 사건 | 회사·항목: 읽은 성격 → 방향 | 갈림의 이유 | 판정 |
|---|---|---|---|---|
| E1 | Amazon 이 OpenAI 와 Anthropic 에 모두 출자 | Anthropic ⑤: 헤지 아님 → Amazon 지분 동맹 유지 / OpenAI ⑤: "헤지가 확인된다" → 세지 않음(결론은 묶임 부재로 섬) / Amazon ⑤: 두 회사 모두 맺은 출자 | 투자자 쪽은 돈의 방향(관계의 종류). 두 피투자사 사이에서는 규칙 읽기의 차이 | OpenAI 문장만 fail(F1) |
| E2 | Microsoft 가 GitHub Copilot 에 MAI-Code-1-Flash 를 넣음(EV-microsoft-010) | Anthropic ⑤: 경쟁사 소유 고객 전선(구조형 미확인) / OpenAI ⑤: 헤지 → 세지 않음, 전선 아님(Microsoft 는 OpenAI 의 고객이 아님) / Microsoft ⑤: 사는 쪽의 일이라 넣지 않음 | 전선 여부는 관계의 종류(고객인가)로 갈리고 이유가 적혀 있다. 헤지 여부는 Anthropic 쪽 Amazon 의 같은 모양 사실과 반대로 풀렸다 | 헤지 읽기 fail(F1) |
| E3 | Microsoft 가 Copilot 제품군에 Claude 계속 제공(EV-microsoft-015) | Anthropic ⑤: 나란히 올림 → 주력 편입 아님 / OpenAI ⑤: 헤지 근거 | 같은 사실을 '병행'과 '교체'로 | fail(F1) |
| E4 | Google Cloud 가 OpenAI 모델 제공(EV-openai-185), Claude Anthropic 운영 배포 일반 출시(EV-anthropic-165) | Anthropic ⑤: 165 만 인용(제공 확대) / OpenAI ⑤: 다루지 않음 / Alphabet ⑤: 범위 밖 | 누락 | 점수 무관(F5) |
| E5 | OpenAI–Microsoft 최대 파트너 긴장(FT 법적 대응 경고 보도, Pages 출시) | Microsoft ⑤: 긴장 있음 / OpenAI ⑤: 미확인 | 이유 없음(같은 쌍, 같은 근거) | fail(F2) |
| E6 | Cursor(SpaceX 소유)가 두 모델사의 고객 | Anthropic ⑤·OpenAI ⑤: 둘 다 구조형 미확인 전선. Anthropic ⑦·OpenAI ⑦: 둘 다 조달 의존 큼 | 같다 | pass |
| E7 | FTC 제품 안전 조사, EU AI Office 에이전트 사고 조사 | 두 회사 ⑤: 둘 다 구제 조치 없는 비용형 | 같다 | pass |
| E8 | 저작권 소송(Anthropic: 작가 합의 종결·Reservoir 신규 / OpenAI: MDL 3143·USA TODAY) | 둘 다 비용형, 구제 청구는 판결 전이라 구제 조치 진행 아님. 끝난 작가 합의는 세지 않음 | 같다 | pass |
| E9 | 국방부 CDAO 프런티어 AI 계약(네 회사 공동) | 두 회사 ⑤: 경쟁사도 함께 받은 계약이라 세지 않음 | 같다 | pass |
| E10 | 받은 투자 규칙 변경 자체 | Anthropic·OpenAI: 새 규칙 / SpaceX·TSMC: 옛 규칙("받은 투자라 세지 않는다") | 잣대 적용 범위 누락 | fail(F3) |
| E11 | 합작법인 지분(SB OAI Japan·TikTok USDS·JASM/ESMC) | OpenAI·Oracle: 맺은 출자로 지분 동맹 / TSMC: 받은 투자 | 지배 여부로 가를 수 있으나 어느 판단에도 이유가 없음 | fail(F3 에 포함) |

## 4. 미확인 방향표

| # | 회사·항목 | 미확인 | 해소 방향 | 판정 |
|---|---|---|---|---|
| U1 | Anthropic ⑤ | 최대 파트너 Amazon 과의 긴장 | 2.6 대로 −12 와 −10 사이 40%(−11.2), 나쁜 쪽 기점 | pass |
| U2 | OpenAI ⑤ | 최대 파트너 Microsoft 와의 긴장 | 같은 40% 규칙. 그러나 Microsoft ⑤ 는 같은 쌍을 '있음'으로 확정 | fail(F2) |
| U3 | 두 회사 ⑤ | Cursor·GitHub Copilot·Meta(Anthropic), Cursor·Musk 영리 전환 청구(OpenAI)의 구조형 여부 | 둘 다 structural_unknown 40% 규칙, 유출·2차 수치로 등급을 가르지 않음 | pass |
| U4 | Anthropic ⑤ / OpenAI ⑤ | 투자자가 '그 자리'를 경쟁 모델로 바꿨는지 | Anthropic(Amazon): 확인 안 됨 → 묶임 유지(좁은 읽기 문언대로) / OpenAI(Microsoft): 확인 안 됨 → 풀림 | fail(F1). 같은 종류의 미확인이 반대로 풀렸고, OpenAI 쪽은 감점 쪽이라 규칙 문언("확인될 때만 풀린 것")과 어긋난다 |
| U5 | OpenAI ⑤ | Microsoft 남은 출자 약정 $11억의 조건 | 지분 동맹 쪽으로 풀지 않음(가점 엄격) | pass. Anthropic 쪽 AMD·NVIDIA·Microsoft 약정도 조건이 확인되지 않으면 세지 않아 같다 |
| U6 | Anthropic ⑤ | Google 성과 목표의 내용 | 약정의 존재로 묶임 판정. 내용은 점수에 닿지 않음 | pass |
| U7 | OpenAI ⑤ | SB OAI Japan 외부 상용 제공 개시 | 맺은 출자는 그 자체로 센다는 문언으로 셈(지분은 지금 존재) | pass |
| U8 | OpenAI ⑤ | Stargate LLC 출자 실행 | 세지 않음(가점 엄격). Oracle ⑤ 의 Stargate 도 같은 이유로 세지 않음 | pass |
| U9 | Anthropic ⑧ / OpenAI ⑧ 고객 축 | 최대 고객 비중(유출 초안 수치만 있음) | 둘 다 탐색 미완 −1 기본값, 비공개로 올리지 않음 | pass |

## 5. 결정적 사실의 근거 등급표

| 입력 | Anthropic | OpenAI | 같은 등급인가 |
|---|---|---|---|
| 받은 투자의 조건부 추가 출자 약정 | Amazon: 공시(Amazon 10-Q). Google: 회사 발표를 전한 2차 보도(Bloomberg, EV-anthropic-172) + 2차(EV-alphabet-018). 공시(Alphabet 10-Q, 이름 미기재)를 쓰지 않음 | Amazon: 공시(10-Q, 약정 소진). NVIDIA: 1차 발표(의향서) + 공시(10-K, 체결 미보장). Microsoft: 공시(10-K, 조건 미기재) | 규칙이 허용하는 등급 안이다. Google 만 저장소 안 공시를 두고 2차를 썼다(F4, 점수 무관) |
| 주력 편입 | 해당 없음(묶임 근거로 쓰지 않음) | Microsoft: 공시(10-K) + 1차(Maia 블로그) | — |
| 헤지(교체) | Amazon: 교체 확정 근거 없음(공시·1차 탐색) | Microsoft: 1차(실적 통화)지만 원문은 '병행'만 보인다 | 등급은 같고 읽기가 다르다(F1) |
| ⑤ 구조형의 '주요 고객' | 공개 제출본·1차 발표 없음. 2차·유출 수치는 "보도가 있다"로만 | 공개 제출본·1차 발표 없음. Cursor CEO 의 5% 는 트래픽 몫이라 쓰지 않음 | 같다 |
| ⑧ 고객 집중 | 유출 초안 수치 쓰지 않음(EV-anthropic-167·168 은 어느 판단도 인용하지 않음) | 같은 잣대 | 같다 |
| 맺은 합작 출자 | — | SB OAI Japan: 회사 1차 발표(EV-openai-165) | TSMC 합작은 공시(20-F)로 지분을 확인했으나 읽기가 다르다(F3) |

## 6. 직접 경쟁사 쌍 (Anthropic ↔ OpenAI, q3b 점수)

| 항목 | Anthropic | OpenAI | 차이의 이유 |
|---|---|---|---|
| ① | 4 | 6 | 참여자 효과(OpenAI anecdotal, Anthropic none)와 D·E 시장 관측 차이. 재료는 이번 실행에서 바뀌지 않았다 |
| ② 모델 | 15 | 12 | 성능 도약 1위 단독(31일, 1개월) 대 2위. 표준은 MCP(중립·대부분 지원) 대 OpenAI API 규격(회사 보유·셋 이상 지원) |
| ③ 모델 | 0 | 8 | 별도 수익모델(같은 구독·토큰 대 광고로 회수) 차이. 가속도는 Anthropic 이 연속 분기 실측으로 감속(1.448 < 2.493)이라 0, OpenAI 는 같은 길이의 두 기간이 없어 미확인 40%(2.4). 둘 다 규칙 2.6 대로다 |
| ④ | 3 | 4 | 판매 칸 셋(개발 플랫폼·모델·응용) 대 넷(사용자 플랫폼 더함) |
| ⑤ | 7 | 6 | 받은 투자의 묶임 증거(Amazon·Google 의 살아 있는 조건부 약정) 대 합작 한 곳. Microsoft 줄은 이유를 한 줄로 쓰지 못한다(F1). 긴장 읽기도 갈린다(F2) |
| ⑥ | −11 | −14 | 가격은 이번 리뷰에서 보지 않는다(확인 리뷰) |
| ⑦ | −8 | −8 | 같다(Cursor 조달 의존 큼, 돌아옴 없음) |
| ⑧ | −12 | −12 | 같다(공급 −3 또는 약정 −3, 고객 축 탐색 미완) |
| ⑨ | −8 | −8 | 같다(비상장 경로) |

## 7. 나머지 항목의 형식 재확인 (anthropic·openai ①~④·⑥~⑨)

- 18건 모두 `status: new`, 검토일 2026-10-23 이다. 마지막 `reconfirmed` 는 2026-10-23 이고 anthropic.F2.model 은 입력 변경으로 새로 적혔다. 판정 칸은 비어 있지 않고, 올릴·내릴 근거가 함께 빈 판단은 없다(openai.F9 의 올릴 근거 0줄은 허용). `counter_evidence` 는 비어 있다.
- 올릴·내릴 근거의 모든 줄이 `[EV-…]` 표지로 끝나고, 표지가 가리키는 근거는 모두 `confirmed` 다(스크립트로 전수 확인).
- 금지 표기(규칙 버전 표기, 변경 표시, 작업 번호, 다른 판·실행 참조, "사용자 결정" 같은 경위 문구)는 18건의 세 칸과 입력 메모에 없다. 입력의 `trigger` 칸(TRG-071·119·360)은 필드값이라 해당하지 않는다.
- 입력이 바뀐 것은 anthropic.F2.model 의 `gap_months` 0 → 1(2026-09-22 → 2026-10-23, 31일)뿐이다. '3개월 미만' 칸이 같아 점수 15 가 그대로이고 문장도 맞게 고쳐졌다. openai ⑥·⑦·⑧ 은 기준일 문구만 2026-10-23 으로 고쳤다.
- 판단 최상위 `evidence_ids` 는 세 칸 표지와 맞지 않는다(OpenAI ①②③⑥⑨ 는 0건). 검증기가 읽지 않는 옛 필드로 보여 규칙 판정에는 닿지 않는다(다음 실행 과제).

## CHECKLIST

| ID | 결과 | 근거 |
|---|---|---|
| Q01 | pass | Anthropic·OpenAI 모두 공급자 경쟁 위험은 ⑧ 공급 축에서만 센다. 국방부 지정은 ⑤ 에서만 세고 ⑧ 지정학에서 다시 세지 않는다. ⑦ 은 받은 투자 환류를 투자자 쪽으로 넘긴다 |
| Q02 | pass | ⑤ 묶임 판정이 규칙의 증거 셋(독점·우선, 주력 편입, 조건부 추가 출자)으로 서 있다. 금액은 점수에 쓰지 않았다 |
| Q03 | **fail** | F1(OpenAI ⑤ Microsoft·Amazon 헤지 읽기가 Anthropic ⑤ 와 반대, 같은 근거 EV-microsoft-015 를 반대로 읽음), F2(OpenAI–Microsoft 긴장을 두 회사가 반대로 읽음), F3(SpaceX·TSMC 받은 투자를 옛 규칙으로 판정, 합작 읽기 갈림) |
| Q04 | 해당 없음 | ⑥ 가격은 10-23 종가로 다시 계산한 뒤 확인 리뷰가 본다(지시서) |
| Q05 | pass | 출처의 이해관계는 결과 칸만 채운다. 이해상충 표기는 판정 사유로 삼지 않았다 |
| Q06 | 해당 없음 | 두 회사 ① 의 판정 재료는 q3a 와 같다(입력 동일). 볼륨·가치 구분(토큰 점유는 D·E 부분 반영)은 이어받은 판정대로이고, 이 리뷰는 형식만 다시 봤다 |
| Q07 | 해당 없음 | ③ 판정 재료 불변. 두 회사 모두 '안 만든 것'을 ③ 으로 세지 않았다(전략 문장 확인) |
| Q08 | pass | 두 회사 모두 전선을 성격으로 센다. OpenAI 비용형 열다섯은 관할 수(3)로만 더 깎고 수로 띠를 올리지 않았다 |
| Q09 | pass | Workday(Anthropic)·Synopsys(OpenAI)는 출시 전이라 넣지 않았다. UAE 라운드·컴퓨트 계약은 트리거(TRG-379)로만 둔다. Google 조건부 약정은 지금 맺어진 약정이라 계획이 아니다 |
| Q10 | 해당 없음 | ③ 가속도 재료 불변(Anthropic 연속 분기 배수, OpenAI 자료 없음) |
| Q11 | 해당 없음 | ⑨ 는 비상장 경로이고 적자를 실격 사유로 쓰지 않았다(재료 불변) |
| Q12 | pass | 두 회사 ③ 모두 16 미만이다(0·8). 모방 불가능성 8 관문에 닿지 않는다 |
| Q13 | pass | OpenAI ③ 의 무료·Go 요금제는 광고 회수 장치와 함께 세고, 공짜만으로 세지 않았다(재료 불변) |
| Q14 | pass | 두 회사 ②③ 어느 층도 20 이 아니고 문 닫힘 날짜가 없다 |
| Q15 | pass | 오픈웨이트·개발자 수를 ⑤ 동맹으로 세지 않았다 |
| Q16 | 해당 없음 | 두 회사 모두 매출 줄 하나·판매 층 하나(모델)로 재료 불변 |
| Q17 | 해당 없음 | ② 표준 재료 불변 |
| Q18 | pass | SpaceX–Tesla 는 양쪽 모두 관계사로 세지 않는다. Microsoft·Amazon·Google 은 Anthropic·OpenAI 와 지배주주가 다르다 |
| Q19 | pass | Anthropic 은 Amazon·Google 을 묶임 증거(공시·등급을 적은 2차)로만 셌고, 한 관계를 지분 동맹에만 넣었다(Bedrock·Vertex 재판매·Antigravity 를 다시 세지 않음). OpenAI 는 받은 투자를 곧바로 세지 않았다. 묶임을 반대 방향으로 잘못 푼 것은 Q03(F1)에 적었다 |
| Q20 | pass | 두 회사의 클라우드·칩 구매, AMD 워런트·CoreWeave 주식은 조달로 뺐다. Oracle ⑤ 가 OpenAI 를 상업 동맹으로 세는 것은 파는 쪽이라 방향이 맞다 |
| Q21 | pass | 2절. 회사 사이의 받은/맺은 투자는 서로 다른 회사의 다른 방향 속성이고, 회사 안의 ⑤(상대가 떠날 수 있나)와 ⑧(내가 떠날 수 있나)은 규칙이 허용한 짝이다 |
| Q22 | pass | OpenAI ⑤ 가 Microsoft 의 Anthropic 평가이익을 인용하지만 ⑦ 입력이 아니다. 두 회사 ⑦ 에 평가이익을 넣지 않았다 |
| Q23 | 해당 없음 | ② 성능 도약 재료 불변(독립 측정 지수) |
| Q24 | pass | 작가 집단소송 합의(항소·이행 감시 없음)는 세지 않았고, X.AI 영업비밀(항소 중)·Musk v. Altman(최종 판결 전)·캐나다(이행 감시)는 진행 중으로 셌다 |
| Q25 | 해당 없음 | 두 회사 모두 판매 층이 하나라 다른 층으로 옮겨 센 강점이 없다 |

## 다음 실행 과제

1. NVIDIA ⑤ 는 자기가 지분을 넣은 OpenAI·Anthropic·Intel 을 "떠날 수 있다"는 이유로 지분 동맹에서 뺀다. 현행 규칙은 "내가 맺은 출자는 그 자체로 센다"이고, Alphabet(SpaceX·Jio)·Meta(Scale AI·Jio)·Alibaba(Moonshot)·Oracle(TikTok USDS)은 맺은 지분을 떠날 수 있는지 따지지 않고 센다. NVIDIA 의 지분 동맹은 CoreWeave·Nebius 로 이미 3 이라 점수는 그대로다. 다음 정기 실행에서 맺은 출자의 읽기를 맞춘다.
2. Palantir ⑤ 는 투자 계약으로 지분을 산 회사들을 이름 미공시·일부 파산·계약 매출 $3M 을 이유로 세지 않는다. "그 자체로 센다" 문언과 견주어, 상대를 특정할 수 없다는 것만으로 빼는지 문장을 맞춘다.
3. OpenAI ⑥ 은 "2026-10-09 보도된 $1.4T"를 적는다. 확정 근거 EV-openai-183 은 협상 밸류가 $1.25T 로 내려갔다고 전한다. 마감 전이라 점수 재료는 아니지만, 10-23 종가로 다시 계산할 때 확인 리뷰가 문장을 본다.
4. OpenAI 판단 9건의 `reviewer` 가 "claude 판단 세션(실적 반영 2단계)"으로 q3a 판단 세션과 같은 이름이다. Anthropic 은 "(q3b)"를 붙였다. 감사 추적에서 어느 세션이 판단했는지 갈리게 이름을 맞춘다.
5. 판단 최상위 `evidence_ids` 가 세 칸 표지와 맞지 않는다(7절). 소비자가 없으면 필드를 정리하고, 있으면 apply 경로가 인용 ID 를 넘기게 한다(q3b-anthropic questions.md 6번과 같은 문제).
6. F6 의 Anthropic ⑤ 방향 칸 정리(좁은 읽기에서 풀리지 않는 사실을 판정 칸으로 옮김).
