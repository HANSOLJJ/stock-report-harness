---
reviewer_agent: claude-opus-5-5 확인 리뷰어
session: claude-q3b-confirm-2026-10-23
reviewed_at: 2026-10-23
area: confirm
results_hash: 7a150813fbb1d0f9a2756c147764ff804ffc02ab80bc456139407dfea3d89294
draft_hash: 612890a49bd1039aa8994e78b1ec420de256f4483731fac6894aa055ba4e1f66
---
검토자: claude-opus-5-5 (확인 리뷰, 별도 세션)
결과: pass

## RESULT

- 결과는 pass 다. 1차 네 영역의 needs_fix 발견 여덟 건(facts F-1·F-2, rules F1·F2·F3, finance F-01, output F-01·F-02) 가운데 점수·순위·체크리스트에 닿는 여섯 건은 지금 파일로 모두 닫혔다. output F-01·F-02 는 점수에 닿지 않는 문장 문제였고, 각각 일부가 남았다(C-3, 다음 실행 과제).
- 수정된 판단 넷(openai.F5, tsmc.F5, spacex-xai.F5, anthropic.F5)은 세 칸으로 쓰였다. 올릴·내릴 근거의 줄은 모두 `[EV-…]` 표지로 끝나고 표지는 확정 근거를 가리킨다. 금지 표기(규칙 버전, 변경 표시, 작업 번호, 다른 판 참조)는 없다. 계약 검사(`validate_report_contract.py`)도 review.md 상태 한 줄을 빼고 모두 통과했다.
- 새 근거 EV-tsmc-130~132 는 sec-get 캐시 원문(6-K 2026-08-14 첨부 99.1 주석 13·주석 4, 20-F FY2025 Item 4)에서 발췌·숫자·위치가 모두 맞다.
- 합작법인 원칙은 OpenAI(SB OAI Japan 50%)·Oracle(TikTok USDS 15%)·TSMC(SSMC 39%) 세 판단에서 같고, 지배하는 JASM·ESMC 는 관계사로, 소수 주주는 받은 투자로 갈랐다. Microsoft–OpenAI 최대 파트너 긴장은 두 판단 모두 '있음'이고 같은 근거(FT 보도 EV-openai-041/EV-microsoft-018, Pages EV-microsoft-003)를 쓴다. TSMC ⑤ 15 는 규칙대로다. 지분 동맹 네 곳(맺은 출자는 그 자체로 센다)은 3점, 상업 동맹 세 상대는 2점이고, 두 묶음의 상대가 겹치지 않아 한 관계를 한 부분에서만 센다는 규칙에도 맞는다.
- `draft.md` 숫자는 맞다. 순위표 14행, Anthropic·OpenAI·TSMC 카드, 카드 머리줄의 반영 기준 14개, 개요의 가격 기준일 10-22 줄이 `results.json`·`run.json` 과 같다. `diff ai-scorecard-2026-10-q3b --against ai-scorecard-2026-10-q3a` 를 다시 돌렸고 1층·2층 모두 통과했다. 점수 변화는 Anthropic ⑤ 4→7, OpenAI ⑤ 6→5, TSMC ⑤ 12→15 셋이고, 순위는 TSMC 와 Amazon 의 3·4위만 바뀌었다.
- **pass 이지만 사람이 확인 전에 알아야 할 것이 둘 있다.** 둘 다 이 실행의 범위 밖에서 이어받은 판단이고, 그 판단을 다시 매기면 순위가 바뀔 수 있다. 하나는 tsmc.F5 가 이번에 명시한 "맺은 출자는 재무 투자에 그쳐도 센다"는 읽기와 Palantir ⑤ 의 출자 제외 사유가 맞지 않는 것이다(C-1). 이 읽기로 다시 매기면 Palantir 가 9위에서 8위로 오를 수 있다. 다른 하나는 Apple 이 가진 Globalstar SPE 지분 20% 를 Apple ⑤ 가 다루지 않은 것이다(C-2). 이 지분을 맺은 출자로 읽으면 Apple 과 Microsoft 의 5·6위가 뒤바뀐다. 두 건을 blocked 로 올리지 않은 이유는 셋이다. 첫째, 둘 다 diff 가 움직이지 않았음을 증명한 범위 밖 판단이다. 둘째, Palantir 는 자기 공시에 투자 대상 이름이 없어, 몇 곳으로 셀지 판단 세션이 정해야 한다. 셋째, Globalstar SPE 는 이번 실행이 정한 원칙(내가 쓸 설비를 짓는 자금 조달 구조는 조달이다)으로 읽으면 조달이라 점수가 그대로다. Q03 을 범위 밖까지 엄격히 읽으려면 확인 전에 `scope --add palantir:F5 --add apple:F5` 로 다시 매기는 길이 있다.
- 리뷰 파일에서 이 리뷰가 낸 발견은 여섯 건이다(중간 3, 낮음 3). 점수·순위·체크리스트를 바꾸는 발견은 남지 않았다.

## FINDINGS

### 1차 needs_fix 발견의 닫힘

| 발견 | 내용 | 지금 상태 | 확인한 곳 |
|---|---|---|---|
| facts F-1 | OpenAI ⑤ Microsoft 헤지 근거가 '그 자리에 올림'을 받치지 못함 | 닫힘 | openai.F5 판정 칸은 이제 Microsoft 를 "주력 편입의 바꾸기 어려움이 확인되지 않는다", "헤지가 아니라 묶임 증거가 없다"로 뺀다. EV-microsoft-010 은 '나란히 올림·서로 바꿔 씀'의 근거로만 쓰고, Anthropic ⑤ 의 Copilot 읽기(나란히 올림이라 주력 편입 아님)와 같은 잣대라고 적는다. 상업 동맹 문장(떠날 수 있음)과도 한 읽기가 됐다 |
| facts F-2 | Amazon 줄 "헤지가 확인된다" | 닫힘 | 판정 칸에서 "헤지가 확인" 문구가 사라졌고, Amazon 은 남은 약정 없음·AWS 독점 조항은 OpenAI 를 묶음·주력 편입 미확인으로만 뺀다. Anthropic 출자·AWS 약정 확대·Microsoft 평가이익·Qwen 결정 모델은 "좁은 읽기로 묶임을 풀지 않아 점수에 넣지 않았다"는 판정 칸 문단으로 옮겨졌고 내릴 근거 칸에서 빠졌다 |
| rules F1 | OpenAI ⑤ 가 넓은 헤지 읽기 | 닫힘 | 규칙 요약 문장이 현행 문언(내렸거나 그 자리에 올린 것이 확인될 때만, 자체 모델·다른 출자만으로는 풀리지 않음)으로 바뀌었다. 리뷰어가 권한 (다)를 택했고 ⑤ 동맹은 2 그대로다 |
| rules F2 | Microsoft–OpenAI 긴장을 두 회사가 반대로 읽음 | 닫힘 | openai.F5 `partner_tension: yes`. 같은 FT 보도와 Pages 를 인용하고 "Microsoft ⑤ 가 같은 두 사실로 … 있다고 읽은 것과 같은 읽기"라고 적는다. H = −12 + 0.4 × 8 = −8.8, ⑤ = 12 + 2 − 8.8 = 5.2 → 5 가 `results.json` 과 같다 |
| rules F3 | SpaceX·TSMC ⑤ 가 옛 받은 투자 규칙, 합작 읽기 갈림 | 닫힘 | `run.json update_scope.extra` 에 tsmc:F5·spacex-xai:F5 가 들어갔다. 두 판단은 2026-10-23 `status: new` 로 다시 쓰였다. TSMC 는 JASM·ESMC 소수 주주 여섯 곳을 묶임 증거가 없어 빼고, 빠져 있던 관계기업 지분을 맺은 출자로 더했다. SpaceX 는 Tesla 를 관계사로, Alphabet·NVIDIA 를 묶임 증거 없음으로 빼 5 그대로다. 합작법인 지배 여부 원칙은 tsmc.F5 에 문장으로 있다 |
| finance F-01 | TRG-163 관찰이 "동맹 0" | 닫힘 | 관찰이 "Amazon·Google 은 … 지분 동맹으로 세고, Microsoft 는 … 세지 않는다. 동맹은 지분 2곳으로 3"으로 다시 쓰였다 |
| output F-01 | 개요가 "실적 반영 실행이다" | 대부분 닫힘 | 개요는 "일부 회사만 다시 매긴 실행이다"로 바뀌었다(커밋 fe4e9f3). `research.md` 「갱신 범위」 표에 두 행이 생겨 빈 예고문 문제도 없어졌다. 제목 "실적 반영 (2차)", 정의 없는 "절충안", `run.json assumptions` 둘째 줄("실적 반영 실행이다 … 가격은 모든 회사를 새로 받는다")은 남았다. 점수와 무관하다(다음 실행 과제) |
| output F-02 | 가격 기준일 10-23 과 "새로 받았다" | 일부 닫힘 | `run.json price_as_of` 와 개요의 기준 시점 줄은 2026-10-22 이고, 가격 관측도 12개사 모두 10-22 다. 그러나 개요 다음 줄의 "가격은 모든 회사를 이 기준일에 새로 받았으며"는 그대로라 사실과 다르다(C-3) |

### C-1 (중간, 범위 밖 이어받은 판단, 순위에 닿을 수 있음) 맺은 출자 읽기가 TSMC 와 Palantir·NVIDIA 사이에서 갈린다

- **무엇이.** tsmc.F5 는 "내가 맺은 출자는 그 자체로 세므로 상대가 떠날 수 있는지와 지분이 사업 협력 없이 재무 투자에 그치는지는 가르지 않는다"고 적는다. 그래서 유의적 영향력을 잃고 기타포괄손익 공정가치 금융자산으로 옮긴 VIS 지분 19% 까지 지분 동맹으로 센다(규칙 3절 ⑤ "내가 맺은 출자는 그 자체로 센다", 2026-10-23 문언). 이어받은 두 판단은 같은 문언과 맞지 않는다.
  - Palantir ⑤ 는 "투자 계약으로 지분을 산 회사들이 … 회사 이름이 공시되지 않았고, 일부는 파산하거나 계약을 끝냈으며 2026년 상반기 그 계약 매출은 $3M 이다"를 이유로 지분 동맹을 0 으로 둔다. 근거 표지는 달지 않았다. 확정 근거 EV-palantir-051 은 투자 계약과 전략 상업 계약을 받친다. 매출 크기를 이유로 빼는 것은 "금액은 쓰지 않는다"는 규칙과도 어긋난다. Palantir 10-Q(2026-06-30, `data/_sec/docs/01188c16b36c3d0a-pltr-20260630.htm`)는 기말에 상장 지분증권(미실현 이익 $66M, 대부분 단기 매도 제한)과 비상장 회사 지분증권 $167M 을 가졌다고 적는다. 비상장 쪽은 "privately-held companies" 처럼 여러 회사를 가리킨다.
  - NVIDIA ⑤ 는 자기가 출자한 OpenAI·Anthropic·Intel 을 "떠날 수 있다"는 이유로 지분 동맹에서 뺀다(rules 다음 실행 과제 1). NVIDIA 는 이미 지분 동맹이 3 이라 점수는 그대로다.
- **점수 영향.** Palantir 가 맺은 출자 두 곳 이상으로 세어지면 ⑤ 는 3 에서 6 이 되고, 조정총점이 8 에서 11 로 올라 Alibaba(10)를 넘어 8위가 된다. 한 곳이면 10 으로 Alibaba 와 공동 8위다.
- **blocked 로 올리지 않은 이유.** Palantir ⑤ 는 범위 밖에서 이어받은 판단이고 diff 가 움직이지 않았음을 증명했다. 게다가 Palantir 자신의 공시에는 투자 대상의 이름이 없다. 그래서 '상대'를 특정하지 못한 지분을 몇 곳으로 셀지, 한 관계가 한 부분인지·관계사인지를 어떻게 가를지는 판단 세션이 정할 일이다. 확정 근거만으로 몇 곳인지가 서지 않는다.
- **고치는 법.** 맺은 출자 읽기를 14개사에 한 번에 맞춘다(다음 실행 과제 1). 사람이 이번 실행에서 맞추기를 원하면 확인 전에 `scope ai-scorecard-2026-10-q3b --add palantir:F5 --add nvidia:F5 --reason "⑤ 맺은 출자를 그 자체로 세는 읽기를 TSMC 와 맞춘다"` 로 넣고 다시 매긴다.

### C-2 (중간, 범위 밖 이어받은 판단, 읽기에 따라 순위에 닿음) Apple 의 Globalstar SPE 지분 20% 가 Apple ⑤ 에 없다

- **무엇이.** Globalstar 10-Q(2026-06-30, sec-get 으로 받음, `data/_sec/docs/b20a9e8a49f074da-gsat-20260630.htm`)는 Apple 이 2024-11-05 Globalstar SPE 의 Class B 지분 400,000 단위를 $4억에 사 지분 20% 를 갖는다고 적는다. Globalstar 가 80% 를 갖고 연결하며, Amazon 과의 합병이 끝나면 Amazon 자회사가 Apple 지분을 사들인다(합병은 미종결). Apple ⑤ 는 "지분 동맹 … 은 확정 근거에 없다"고만 적고 이 지분을 다루지 않는다. Apple 의 10-K·10-Q 원문에는 Globalstar 가 나오지 않는다.
- **읽기.** tsmc.F5 가 정한 합작법인 원칙으로 보면, 내가 지배하지 않는 법인의 지분은 맺은 출자다. 다만 그 법인이 내가 쓸 설비를 짓는 자금 조달 구조라면 조달이다(Meta 의 데이터센터 합작). Globalstar SPE 는 Apple 에게 서비스를 대는 위성망 자산(설비·선급 망 비용)을 담은 법인이다. 그래서 조달로 읽는 쪽이 이번 실행의 원칙에 맞고, 그러면 점수는 그대로다. 맺은 출자로 읽으면 Apple ⑤ 가 9 에서 11 이 되고 조정총점이 23 에서 25 로 올라 Microsoft(24)를 넘는다(5·6위가 뒤바뀜).
- **고치는 법.** 다음 실행에서 Apple ⑤ 판정 칸에 이 지분과 그 읽기를 한 줄로 적는다. 근거로는 Globalstar 10-Q 를 확정한다.

### C-3 (중간, 점수 무관, 확인 전에 고치기를 권함) 개요의 "가격은 모든 회사를 이 기준일에 새로 받았으며"가 사실과 다르다

- `draft.md` 30행에 남아 있다. 가격은 이어받은 2026-10-22 종가이고(관측 12개사 모두 `as_of` 2026-10-22), 같은 개요의 앞줄도 가격 기준일을 2026-10-22 로 적는다. 문장은 `scripts/scorecard/render_common.py` 2918~2919행에 고정돼 있다. 렌더러가 `run.json price_as_of` 가 `as_of` 와 다를 때 "가격은 이어받은 {price_as_of} 종가다"로 쓰게 고친다. 초안만 다시 렌더링하면 확인은 유지되지만 draft_hash 가 바뀌므로 review.md 의 해시를 맞춰야 한다.

### C-4 (낮음, 점수 무관) Anthropic ⑤ 의 Google "$300억 … 집행됐거나 끝났다는 근거가 없어"가 저장소 안 공시와 어긋난다

- Alphabet 10-Q 두 개를 원문으로 다시 확인했다. 2026-03-31 분기는 비상장 회사 한 곳에 $10.0B 확정 출자와 "$30.0 billion of future capital funding contingent upon the achievement of specified operational and financial milestones through 2030" 을 적는다. 2026-06-30 분기는 같은 조건부 약정을 $20.0B 로 적는다. 회사 이름은 적지 않는다. 금액·시기가 EV-anthropic-172 와 맞아 Anthropic 으로 읽는 것은 추론이다. 2030년까지 $200억이 살아 있어 묶임 판정과 점수는 그대로다. 판정 칸과 TRG-381 조건("조건부 $300억이 집행되거나 끝났다는 공시")은 잔액 $200억과 공시 등급으로 다시 쓴다(rules F4 를 이어 확인했다).

### C-5 (낮음, 점수 무관) 범위 선언·감사 기록의 표기

- `run.json update_scope.extra` 의 spacex-xai 사유가 TSMC 사유를 그대로 옮겨 "합작법인(JASM·ESMC)"을 적는다. 그 문장이 "규칙 일관성 리뷰 F3" 이라는 작업 표지와 함께 `research.md` 「갱신 범위」 표(1467·1468행)에 실린다. `draft.md` 에는 나오지 않는다.
- tsmc.F5·spacex-xai.F5·openai.F5 의 `reviewer` 는 "claude 판단 세션(실적 반영 2단계)"으로 q3a 판단 세션과 이름이 같다. spacex-xai.F5 의 `reconfirmed` 마지막 기록은 2026-10-12 이다. EV-tsmc-102 는 relevance 가 다시 쓰였는데 `reviewed_at` 은 2026-10-19 그대로다. EV-anthropic-170 `conditional_impact` 는 "Anthropic ⑤ 판단은 바꾸지 않는다 … 확인되면 받은 투자를 지분 동맹으로 다시 센다"로 남아, Amazon·Google 을 이미 센 현재 판정과 맞지 않는다.

### C-6 (낮음, 점수 무관) openai.F5 에 남은 문장

- "NVIDIA 는 2026-03 라운드를 이끈 투자자이고 OpenAI 에 $300억을 넣었다고 보도됐다"는 EV-nvidia-043 을 인용하지 않고, "라운드를 이끈"은 확인되지 않았다(facts F-4).
- "2026-10-23 에 NVIDIA 의 … 10-Q 본문에서 OpenAI 를 찾았을 때"는 작업 서술이다. "정부 계약 사업 자체를 끝내라는 반대 운동을 정당성 공격으로 센 다른 회사 판단"은 어느 회사인지 적지 않았다(output F-07).

### 수정된 판단 넷 점검 요약

| 판단 | 점수(재계산) | 세 칸·표지 | 금지 표기 | 비고 |
|---|---|---|---|---|
| openai.F5 | 12 + 2 − 8.8 = 5.2 → 5 | 올릴 14줄·내릴 31줄 모두 표지, 확정 근거 | 없음 | 작업 서술 한 문장(C-6). EV-openai-185 를 올릴 근거에 넣어 rules F5 의 OpenAI 쪽도 닫힘 |
| anthropic.F5 | 12 + 3 − 8.32 = 6.68 → 7 | 모두 표지, 확정 근거 | 없음 | 내릴 근거 칸에 좁은 읽기로는 풀리지 않는 Amazon–OpenAI 사실이 단서 없이 남음(rules F6, output F-05, 다음 실행). 음악 출판사 문장은 facts F-3 그대로 |
| tsmc.F5 | 12 + 5 − 2 = 15 | 모두 표지, EV-tsmc-130~132 확정·원문 일치 | 없음 | VIS 를 빼도 세 곳이라 3점은 같다. Xintec 은 TSMC 공급자이지만 상장 별도 회사 지분이라 맺은 출자로 센다는 이유가 판정 칸에 있다 |
| spacex-xai.F5 | 12 + 0 − 7.2 = 4.8 → 5 | 모두 표지 | 없음 | Alphabet 지분 6%·NVIDIA 투자는 묶임 증거 없음, Tesla 는 관계사. reconfirmed 미갱신(C-5) |

### EV-tsmc-130~132 원문 대조

| 근거 | 원문(캐시) | 발췌 | 숫자 | 위치 |
|---|---|---|---|---|
| EV-tsmc-130 | `6742744e39d8c375-a2026q2consolidatedreport-.htm` 주석 13 | 관계기업 표의 SSMC·Xintec·GUC 행과 VIS 처분 문단이 글자 그대로 있다 | SSMC 39%·Xintec 41%·GUC 35%(세 시점 같음), VIS 처분 152,000 천 주 → 19%, 유의적 영향력 상실·FVTOCI 재분류 | 주석 13 은 "- 20 -" 쪽 표시 바로 뒤에서 시작해 p.21 과 맞다 |
| EV-tsmc-131 | `2e22450d8b642b75-tsm-20251231.htm` Item 4 Our Subsidiaries and Affiliates | VIS(1994 설립, 2004 전문 파운드리)·SSMC(1999 Philips·EDB 합작) 문장이 그대로 있다 | SSMC 38.8%, GUC 34.8%(원문은 'approximatel y 34.8 % o f'), VIS 27.6%(2026-02-28, 처분 전) | locator 의 p.25~26 과 원문 쪽 표시 '25' 의 위치가 맞다 |
| EV-tsmc-132 | 같은 6-K 주석 4 연결 자회사 표 | JASM·ESMC 행이 그대로 있다 | JASM 73%, ESMC 70% | 주석 4 연결 자회사 표 |

## CHECKLIST

| ID | 결과 | 근거 |
|---|---|---|
| Q01 | pass | Anthropic·OpenAI 의 공급자 경쟁 위험은 ⑧ 공급 축에서만 센다. 국방부 지정은 ⑤ 에서만 센다. TSMC 는 관세를 ⑤ 비용형으로, 대만 집중·장비 의존을 ⑧ 에서 센다. 같은 감점을 두 칸에서 세지 않았다 |
| Q02 | pass | 받은 투자는 규칙의 묶임 증거 셋(독점·우선, 주력 편입, 조건부 추가 출자)으로만 셌다. TSMC 지분 동맹은 관계기업·보유 지분이라 칸 정의(맺은 출자)에 맞다. 금액은 어느 계산에도 들어가지 않았다(`amounts_used: false`) |
| Q03 | pass | 갱신 범위 안의 어긋남 셋이 닫혔다. 첫째, Copilot 의 Claude·OpenAI 병행을 두 회사 모두 '나란히 올림'으로 읽는다. 둘째, Microsoft–OpenAI 긴장을 두 회사 모두 '있음'으로 읽는다. 셋째, 받은 투자 규칙을 SpaceX·TSMC 에도 댔고 합작법인 원칙이 OpenAI·Oracle·TSMC 에서 같다. 범위 밖에서 이어받은 Palantir·NVIDIA 의 맺은 출자 읽기는 C-1 에 적었다(Palantir 는 순위에 닿을 수 있음) |
| Q04 | pass | ⑥ 는 14개사 모두 q3a 와 점수가 같다(가격은 사용자 결정으로 10-22 종가를 이어받음). 상장사 ⑥ 는 성장 조정 PER·EV/매출·성장으로 재고, 시총 크기를 점수에 쓰지 않는다. 비상장 두 곳은 포스트머니 ÷ 런레이트다 |
| Q05 | pass | 출처 이해관계는 결과 칸만 채운다. 표기 누락을 판정 사유로 삼지 않았다 |
| Q06 | not_applicable | 두 갱신 회사 ① 의 판정 재료는 q3a 와 같다. 이번 수정은 ⑤ 에 한정된다 |
| Q07 | not_applicable | ③ 재료 불변. '안 만든 것'을 ③ 으로 세지 않은 판정은 이어받았다 |
| Q08 | pass | 적대를 성격으로 센다. Anthropic 의 Reservoir 전선을 더해도 관할 수(미국·EU)만 보고 띠를 올리지 않았다. OpenAI 비용형 열다섯도 관할 셋으로만 더 깎는다 |
| Q09 | pass | Sony 이미지 센서 합작(종결 전), Terafab, Synopsys 공동 개발, Workday 연동, UAE 라운드는 점수에 넣지 않았다. Google·Amazon 조건부 약정은 지금 맺어진 약정이다 |
| Q10 | not_applicable | ③ 가속도 재료 불변 |
| Q11 | pass | 두 비상장사 ⑨ 는 G1 판정 보류·G2 비상장 미공시 −8 이고 적자를 실격 사유로 쓰지 않았다 |
| Q12 | pass | 갱신 회사 ③ 은 0·8 이라 모방 불가능성 8 관문에 닿지 않는다 |
| Q13 | pass | OpenAI ③ 의 무료·Go 요금제는 광고 회수 장치와 함께 셌다(재료 불변) |
| Q14 | pass | 두 회사 ②③ 어느 층도 20 이 아니고 문 닫힘 날짜가 없다 |
| Q15 | pass | 오픈웨이트·개발자 수·Grok 파트너 네트워크 참여 수를 ⑤ 동맹으로 세지 않았다 |
| Q16 | not_applicable | 두 갱신 회사는 사업 하나·판매 층 하나이고 재료 불변이다 |
| Q17 | not_applicable | ② 표준 재료 불변 |
| Q18 | pass | Tesla–SpaceX 는 양쪽 모두 관계사로 뺐다. TSMC 가 지배하는 JASM·ESMC 는 관계사라 동맹이 아니다. SSMC·GUC·Xintec·VIS 는 TSMC 가 연결하지 않는 회사다 |
| Q19 | pass | 받은 투자를 곧바로 세지 않았다. Anthropic 의 Amazon·Google 은 묶임 증거가 원문으로 확인돼 셌다. OpenAI 의 Microsoft·Amazon·NVIDIA, TSMC 의 JASM·ESMC 소수 주주 여섯 곳, SpaceX 의 Alphabet·NVIDIA 는 묶임 증거가 없어 뺐다. Amazon·Google 은 지분 동맹 한 부분에만 넣었다 |
| Q20 | pass | GlobalFoundries 인터포저, 웨이퍼 매매, 두 모델사의 클라우드·칩 구매, AMD 워런트·CoreWeave 주식은 조달로 뺐다. 범위 밖 Apple 의 Globalstar SPE 지분 읽기는 C-2 에 적었다 |
| Q21 | pass | 받은 투자(Anthropic ⑤, 투자자가 떠나기 어려움)와 맺은 출자(Amazon·Alphabet ⑤, Anthropic 이 떠나기 어려움)는 방향이 다른 속성이고, 회사 안의 ⑤ 와 ⑧ 은 규칙이 허용한 짝이다. TSMC 의 지분 동맹 상대와 상업 동맹 상대는 겹치지 않는다 |
| Q22 | pass | Microsoft 의 Anthropic 평가이익, TSMC 의 VIS 처분 이익은 ⑦ 입력이 아니다 |
| Q23 | not_applicable | ② 성능 도약 재료 불변 |
| Q24 | pass | Marlin ITC 조사(2026-08-06 종료)와 Anthropic 작가 집단소송 합의는 세지 않았다. X.AI 영업비밀 항소·Musk v. Altman 은 진행 중으로 셌다 |
| Q25 | not_applicable | 두 갱신 회사는 판매 층이 하나이고, TSMC 도 반도체 제조 한 층이라 다른 층으로 옮겨 센 강점이 없다 |

## 다음 실행 과제

1. **맺은 출자 읽기를 14개사에 맞춘다(C-1·C-2, 순위에 닿을 수 있음).** 관계기업·합작·보유 지분이 확정 근거에서 빠졌는지 회사마다 공시로 훑는다. 같은 읽기를 대면 순위에 닿을 수 있는 곳은 둘이다. Palantir(투자 대상 지분, 두 곳 이상이면 8위로 오름)와 Apple(Globalstar SPE 20%, 맺은 출자로 읽으면 Microsoft 를 넘음)이다. 순위에 닿지 않는 곳도 같이 본다. Amazon(Rivian 보유 미확인, 한 곳 더해도 34 로 TSMC 35 아래), Microsoft(G42), Oracle(Stargate LLC), NVIDIA(OpenAI·Anthropic·Intel 을 '떠날 수 있다'로 뺌, 이미 3)가 그렇다. 합작법인은 tsmc.F5 의 지배 여부 원칙과 Meta 데이터센터 합작의 자금 조달 구조 예외로 가른다.
2. 개요의 가격 문장을 렌더러에서 고친다(C-3, `render_common.py` 2918~2919행). 정의 없는 "절충안", 제목 "실적 반영 (2차)", `run.json assumptions` 둘째 줄을 실행 종류(실적 / 규칙 해석)에 맞게 쓴다. 방법 절 ⑤ 줄에 받은 투자 조건과 지분 동맹 계단을 싣고, "반영 기준"의 뜻을 카드 도입에 적는다(output F-01·F-03·F-10).
3. Anthropic ⑤ 의 Google 약정을 Alphabet 10-Q 잔액 $200억(2026-06-30, 2030년까지, 회사 이름 미기재는 단서로)으로 다시 쓰고 근거 등급을 공시로 올린다. TRG-381 조건도 같이 고친다(C-4, rules F4, facts 다음 실행 1).
4. Anthropic ⑤ 방향 칸을 정리한다. 좁은 읽기로 풀리지 않는 Amazon–OpenAI 사실(EV-amazon-061·019·020·091·102), Gemini agent·Antigravity 의 Gemini 병행을 판정 칸으로 옮긴다. EV-amazon-039($200억 추가)와 금융 한도 잔액 $150억이 같은 돈임을 한 줄로 가른다. 판정 칸 불릿 순서를 규칙 → 투자자별 판정 → 계산으로 바꾼다. EV-openai-185(Google Cloud 의 OpenAI 모델 입점)를 판정 칸에 한 줄 넣는다(rules F5·F6, output F-05·F-06).
5. Anthropic ⑤ 의 "다른 음악 출판사 소송은 확정 근거에 없다"를 Billboard 원문(진행 중 소송이 더 있다는 서술, 내용 미상)에 맞춰 쓰고, EV-anthropic-164 `unverified` 에 같은 문장을 더한다(facts F-3).
6. openai.F5 의 NVIDIA $300억 문장에 EV-nvidia-043 을 달고 "이끈"을 뺀다. 작업 서술("찾았을 때")과 이름 없는 "다른 회사 판단" 문장을 현재 상태 문장으로 쓴다. Anthropic·OpenAI ⑤ 의 "같은 잣대" 괄호는 이유를 문장 안에서 말하게 쓴다(C-6, facts F-4, output F-07).
7. 트리거 문장을 다듬는다. TRG-036 carry 는 "Anthropic PBC 의 제출인은 나오지 않아"로 쓴다. TRG-380 조건은 "집행으로 줄어드는 것은 제외, 만료·철회·감액이 공시되면"으로, TRG-380·381 의 결론("푼다")은 "다시 본다"로 쓴다. TRG-380 관찰의 "내려간 적이 없다"는 "내렸다는 확정 근거가 없다"로 쓴다. TRG-380·381 `source_ids` 를 채운다(facts F-4, output F-09).
8. 근거 문장을 현재 판정에 맞춘다. EV-anthropic-170 `conditional_impact` 를 고치고, EV-tsmc-102 의 `reviewed_at` 을 갱신한다. 규칙 문언이 바뀔 때 모든 근거의 relevance·conditional_impact 를 규칙 쪽에서 거꾸로 훑는 점검을 한 번 한다(C-5, output F-04, finance F-03).
9. 승계 트리거는 `carry.finding` 만이 아니라 관찰 문장이 새 점수와 맞는지도 함께 읽는다(finance F-01 의 재발 방지).
10. EV-anthropic-171(투자자 설명회의 흑자·잉여현금흐름 흑자 2차 보도)을 ⑨ 판정 칸에서 "금액·기간·정의가 없어 게이트 2 입력으로 쓰지 않는다(미확인)"로 다루고 `reconfirmed` 에 올린다. "3분기"와 "2분기 연속"의 표기도 맞춘다(finance F-02).
11. 감사 추적을 정리한다. 판단 `reviewer` 에 실행 이름을 넣어 q3a·q3b 세션을 가르고, spacex-xai.F5·OpenAI 판단에 이번 실행의 `reconfirmed` 기록을 남긴다. spacex-xai 범위 사유를 바로잡는다. 판단 최상위 `evidence_ids` 가 세 칸 표지와 맞지 않는 문제는 소비자가 없으면 필드를 정리한다(C-5, rules 다음 실행 4·5, finance 다음 실행).
12. 판단 ID `openai.F5.impl48` 을 `openai.F5` 로 바꾸고, 관측 ID 꼬리의 실행 이름(`*.undrawn_credit.q3a`)과 `research.md` 관측 비고의 FIX-·PRIV-IMPL-·NETCASH- 표지를 현재 상태 문장으로 바꾼다(output F-08).
13. 후보 두 건을 가린다. Claude Duet 출시(2026-10-22)가 Anthropic ④·① 에 닿는지, OpenAI 에이전트 감시 시스템 오작동 보고와 외부 평가자 지적(2026-10-22)이 OpenAI ⑤ 전선에 닿는지 본다(facts 다음 실행 2).
14. 유출 상장 신청서 수치를 옮긴 근거(EV-anthropic-167·168·171)는 공개 S-1 이 나오면 공시 값으로 바꾼다. EV-anthropic-172 의 Anthropic 1차 발표 원문을 찾는다(facts 다음 실행 1·4).
15. OpenAI ⑥ 의 "2026-10-09 보도된 $1.4T" 문장을 EV-openai-183($1.25T, 마감 전)과 맞춘다. 라운드가 마감되면 ⑥ 분자와 ⑨ 완충을 다시 계산한다(rules 다음 실행 3, finance·output 다음 실행).
16. 빌드 뒤 `validate_report_contract.py ai-scorecard-2026-10-q3b --require-html` 로 HTML 을 검증한다. 320·768·1280px 가로 넘침, 탭 대상, 순위표 모바일 표시, 다크 모드, audit 링크를 보고, HTML 렌더러가 개요 문장(C-3)을 같은 방식으로 쓰는지도 본다(output 다음 실행).
