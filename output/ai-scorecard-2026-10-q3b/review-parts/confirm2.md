---
reviewer_agent: claude-opus-5-5 확인 리뷰어(보충)
session: claude-q3b-confirm2-2026-10-23
reviewed_at: 2026-10-23
area: confirm2
results_hash: 3063a73c56af7311e8a7cdc0f0ab58f2848ad88d3df6bc1f4014a5124779de64
draft_hash: c41adc70f02ad2dd5a12dc2d4b4ffb184d6bda62f9995ee11f4cfc0c4ba47d0f
---
검토자: claude-opus-5-5 (확인 리뷰 보충, 별도 세션)
결과: pass

## RESULT

- 결과는 pass 다. 이 리뷰는 앞선 확인 리뷰(`confirm.md`, pass)의 C-1·C-2 에 따라 범위에 넣은 `palantir.F5`·`apple.F5` 만 본다. 점수·순위·체크리스트 판정을 바꾸는 발견은 남지 않았다.
- 두 판단은 세 칸으로 쓰였다. 올릴·내릴 근거의 줄은 모두 `[EV-…]` 표지로 끝나고, 표지가 가리키는 근거는 모두 확정·출처 URL·제목과 다른 발췌·인용 위치를 갖췄다. 금지 표기(규칙 버전, 변경 표시, 작업 번호, 다른 판·다른 실행 참조)는 없다. `validate_report_contract.py ai-scorecard-2026-10-q3b` 는 review.md 상태 한 줄을 빼고 모두 통과했다.
- 새 근거 열 건(EV-palantir-067~071, EV-apple-097~101)은 sec-get 캐시 원문과 발췌 조각 25개가 모두 글자 그대로 맞고, 숫자와 쪽 표시도 맞다(아래 표).
- 점수는 규칙대로다. Palantir ⑤ 는 12 + (지분 2 + 상업 1) − 10 = 5, Apple ⑤ 는 12 + 3 − 6 = 9 이고 `results.json` 과 같다. `diff ai-scorecard-2026-10-q3b --against ai-scorecard-2026-10-q3a` 를 다시 돌렸고 1층·2층 모두 통과했다. 범위 항목의 변화는 Palantir ⑤ 3→5(조정 8→10) 하나이고 Apple 은 점수가 그대로다. `draft.md` 의 순위표(Alibaba·Palantir 공동 8위, 조정 10)와 두 카드의 점수 표·⑤ 줄이 `results.json` 과 같고, draft 머리말의 `results_hash` 도 같다.
- 잣대는 맞는다. Palantir 가 고객 Surf Air 에게서 소프트웨어 대금으로 받은 주식을 맺은 출자로 센 것은, 파는 쪽이 고객의 지분을 가진다는 점에서 NVIDIA ⑤ 의 CoreWeave·Nebius 와 같은 방향이다. 사는 쪽인 OpenAI 가 공급자 AMD·CoreWeave 에게서 받은 워런트·주식을 조달 대가로 뺀 것, Apple 이 공급자 Globalstar 에게서 받은 워런트를 뺀 것과도 네 질문의 방향 원칙("파는 쪽에게 고객은 동맹 후보, 사는 쪽에게 공급자는 조달")으로 한 읽기다. Apple 의 Globalstar SPE 를 조달로 읽은 것은 Meta 데이터센터 합작과 같은 원칙이고, SPE 의 조건(상업 영업 없음, 수동 지분, 상환 조항으로 부채 처리, 서비스 대금과 상계)이 원문으로 받쳐진다. 이름이 공시되지 않은 지분 묶음을 세지 않은 것은 Amazon(Rivian)·Oracle(TikTok 합작 밖의 비시장성 투자)·Alphabet(이름 있는 지분만 셈)과 같은 잣대다.
- **pass 이지만 사람이 확인 전에 알아야 할 것이 하나 있다(C2-1).** palantir.F5 는 Palantir 10-Q 가 같은 문서에 적은 합작법인 넷(일본 SOMPO, 한국 HD Hyundai, 중동·미국의 공동 소유 법인)을 다루지 않는다. 이번 범위를 넓힌 이유가 '합작법인 원칙을 같이 댄다'였으므로 판정 칸에 있어야 할 내용이다. 지금 확정 근거로 원칙을 대면 점수는 그대로다. 일본·한국은 Palantir 가 지배해 관계사이고, 두 파트너의 소수 지분은 받은 투자라 묶임 증거가 있어야 하는데 확인되지 않았다. 중동·미국 법인은 Palantir 가 지배하는지 공시에 없어 미확인이고, 미확인은 가점 쪽으로 풀지 않는다. 다만 중동·미국 법인 가운데 하나라도 Palantir 가 지배하지 않는다고 확인되면 맺은 출자 두 곳이 되어 Palantir ⑤ 는 6, 조정총점은 11 로 단독 8위가 된다. 그래서 blocked 로 올리지 않고 중간으로 적는다.
- 이 리뷰가 낸 발견은 여섯 건이다(중간 1, 낮음 5).

## FINDINGS

### C2-1 (중간, 지금 근거로는 점수 무관, 확인되면 순위에 닿음) Palantir 의 합작법인 넷이 palantir.F5 에 없다

- **무엇이.** Palantir 10-Q(2026-06-30, `data/_sec/docs/01188c16b36c3d0a-pltr-20260630.htm`) Part II Item 1A 위험 요인(p.51)은 2019-11 SOMPO Holdings 와 일본에 공동 지배 법인을 세워 2022-11 지배권을 얻었고, 2022-12 HD Hyundai 와 한국에 공동 소유 법인을 세워 지배권을 가지며, 중동과 미국에도 다른 공동 소유 법인들을 세웠다고 적는다. 중동·미국 법인 문장은 2026-03-31 10-Q(p.48)에 처음 나오고 2025-12-31 10-K 에는 없다. 연결손익에 비지배지분 이익(2026년 상반기 $9.9M)이 있다. palantir.F5 의 판정 칸·근거·`relations` 어디에도 이 법인들이 없고, 판단 세션 질문 파일도 다루지 않았다.
- **원칙으로 읽으면.** tsmc.F5 의 합작법인 원칙은 내가 지배하는 합작법인을 관계사로, 함께 출자한 상대의 소수 지분을 내 자회사로 들어온 받은 투자로 읽고, 내가 지배하지 않는 합작법인을 맺은 출자 한 곳으로 센다. 일본·한국 법인은 Palantir 가 지배하므로 동맹이 아니다. SOMPO·HD Hyundai 의 소수 지분은 묶임 증거(독점·우선 조항, 주력 편입, 조건부 추가 출자)가 확정 근거에 없어 세지 않는다. 10-Q 가 적는 제약("독자적으로 팔거나 일부 고객을 상대하지 못하게 한다")은 Palantir 를 묶는 조항이지 투자자를 묶는 조항이 아니다. 중동·미국 법인은 상대와 지배 여부가 공시에 없어 미확인이다. 그래서 지금 점수 5 는 원칙과 맞는다.
- **점수 영향.** 중동·미국 법인 가운데 Palantir 가 지배하지 않는 곳이 확인되면 지분 동맹이 Surf Air 와 합쳐 두 곳이 되어 3 점이고, Palantir ⑤ 는 6, 조정총점은 11 로 Alibaba(10)를 넘어 단독 8위가 된다.
- **고치는 법.** palantir.F5 판정 칸에 합작법인 문단을 하나 더한다(일본·한국은 지배해 관계사, 파트너 소수 지분은 묶임 증거 없어 세지 않음, 중동·미국은 지배 여부 미확인). 근거로 10-Q Item 1A 합작 문단(p.51)을 확정한다. 중동·미국 법인의 상대와 지분 구조를 회사 발표나 상대 회사 공시에서 찾고, 지배하지 않는다고 확인되면 맺은 출자로 더한다. 트리거로 "Palantir 공동 소유 법인의 지배 여부가 공시되면 Palantir ⑤ 지분 동맹을 다시 본다"를 둔다. 확인 전에 고칠지 다음 실행에서 고칠지는 사람이 정한다. 판정 칸 문장만 더하면 판단 해시가 바뀌므로 research 부터 다시 돌려야 한다.

### C2-2 (낮음, 점수 무관) Palantir 가 13G 로 신고한 지분 대상 둘이 판단에서 빠졌다

- **무엇이.** 판단 세션은 Palantir 의 이름 있는 지분 대상으로 Surf Air 와 MSP Recovery 만 찾았다고 적었다. Palantir 제출 목록(`CIK0001321655.json`, 2026-10-08 판)에는 두 곳이 더 있다. 이 리뷰가 sec-get 으로 받아 확인했다.
  - Faraday Future: Schedule 13G(2024-10-08 접수, 사건일 2024-10-02)는 Class A 보통주 1,080,294 주(8.7%)를 가졌고 그 가운데 827,526 주는 미수금 대가로 받았다고 적는다(`data/_sec/docs/65b50801f67cf0ad-schedule13g-ffie.htm`). 그 뒤 Palantir 의 신고는 없고, Faraday Future 의 2026-07-13 위임장 설명서(DEF 14A) 소유 표는 5% 넘는 보유자를 "N/A" 로 적는다(`a1d2b0f2dd791da8-ea0297588-def14a_faraday.htm`).
  - Rubicon Technologies: Schedule 13G/A 5호(2024-09-13 접수, 사건일 2024-09-06)는 Class A 보통주 9,003,517 주(13.1%)를 적는다(`47d65858f2d16e33-schedule13g_aamendmentnox5.htm`). Rubicon 은 2025-01-22 등록 말소(15-12G)를 냈다.
- **읽기.** 두 곳 모두 기준일 보유를 보이는 자료가 없어 MSP Recovery 와 같은 미확인이고 점수는 그대로다. 다만 판정 칸의 "이름이 확인된 지분은 Surf Air 하나"(EV-palantir-069 relevance)와 MSP 문단은 이름 있는 미확인 대상을 모두 적어야 다음 실행이 같은 탐색을 되풀이하지 않는다.
- **고치는 법.** 다음 실행에서 MSP 문단을 "기준일 보유가 확인되지 않은 이름 있는 지분(MSP Recovery·Faraday Future·Rubicon Technologies)"으로 넓히고, 두 13G 를 근거로 확정한다.

### C2-3 (낮음, 점수 무관) Apple 판정 칸의 Xintec 구분 근거가 OpenAI 의 CoreWeave 읽기와 문자 그대로는 어긋난다

- apple.F5 는 "TSMC ⑤ 가 공급자 Xintec 의 지분을 맺은 출자로 센 것은 Xintec 이 상장된 별도 영업 회사이기 때문"이라고 적는다. 그런데 OpenAI ⑤ 는 상장된 별도 영업 회사인 공급자 CoreWeave 의 주식을 조달 대가로 뺀다. 실제로 두 읽기를 가르는 것은 '상장 영업 회사인가'가 아니라 '매매 거래의 대가로 받은 지분인가, 따로 한 출자인가'다. 대가로 받은 지분은 거래 방향을 따르고(OpenAI 의 CoreWeave 주식·AMD 워런트, Apple 의 Globalstar 워런트는 조달, Palantir 의 Surf Air 주식은 파는 쪽이라 지분), 따로 한 출자는 그 자체로 세되 내가 쓸 설비를 짓는 자금 조달 구조만 뺀다(Meta 데이터센터 합작, Apple Globalstar SPE). 이 종합 문장은 어느 판단에도, 규칙에도 없다.
- 점수는 그대로다. TSMC 는 Xintec 을 빼도 세 곳이라 3 이고, OpenAI 가 CoreWeave 주식을 세면 ⑤ 6·조정 −6 이지만 SpaceX(−3) 아래 13위 그대로다.
- **고치는 법.** 규칙 3절 ⑤ 「아군 확보는 묶임이다」 뒤에 위 구분을 한 문장으로 두고, apple.F5 의 Xintec 문장을 그 구분으로 다시 쓴다(다음 실행).

### C2-4 (낮음, 점수 무관) 방향 칸에 미확인 결론이 같은 줄로 붙었다

- palantir.F5 올릴 근거의 EV-palantir-069·070 줄("투자 대상의 이름이 공시되지 않아 상대로 세지 않는다")과 EV-palantir-071 줄("기준일 보유가 확인되지 않아 점수에 넣지 않는다")은 사실은 원문으로 확인되지만 상대 수·기준일 보유는 미확인이다. guide 5.6 은 아직 판정 못 한 것을 판정 칸에 두라고 한다. 같은 내용이 판정 칸에도 있어 읽기에 해는 없다. 다음 실행에서 방향 칸에는 사실만 남기고 미확인 결론은 판정 칸으로 옮긴다.

### C2-5 (낮음, 점수 무관) 감사 기록

- 두 판단의 최상위 `evidence_ids` 에 새 근거가 없다(Palantir 067~071, Apple 097~101). palantir.F5 의 `reconfirmed` 마지막 기록은 2026-10-12 다(apple.F5 는 2026-10-23 기록이 있다). 두 판단의 `reviewer` 는 "claude 판단 세션(실적 반영 2단계)"로 q3a 세션과 이름이 같다. 앞선 확인 리뷰 C-5·다음 실행 과제 11 과 같은 부류다.
- 판단 세션이 제안한 트리거 셋(Surf Air 지분 전량 처분, 이름 있는 투자 대상·MSP 보유 확인, Globalstar–Amazon 합병 종결)이 `triggers.json` 에 없다.

### C2-6 (낮음, 점수 무관) 개요 문장이 범위 항목을 말하지 않는다

- `draft.md` 개요는 "Anthropic, OpenAI 의 판단은 전부 이 기준일에 다시 매겼고 … 나머지 회사의 판단은 각 회사 카드의 반영 기준일에 매긴 것을 이어받았다"고 적는다. 이번 실행은 범위 항목 넷(TSMC·SpaceX + xAI·Palantir·Apple ⑤)도 2026-10-23 에 다시 매겼다. 카드의 "반영 기준"은 마지막 전체 갱신일이라 Palantir·Apple 카드는 2026-10-14 로 나온다. 렌더러(`render_common.py` 2906~2920행)가 `update_scope.extra` 를 개요 한 줄에 싣게 고친다(앞선 확인 리뷰 C-3 과 함께).

### 새 근거 원문 대조

| 근거 | 원문(캐시) | 발췌 | 숫자 | 위치 |
|---|---|---|---|---|
| EV-palantir-067 | 13G 2026-07-01 `674cf7d32540377e-primary_doc.xml` | 네 조각 일치 | 8,248,989 주, 7.4%(110,994,594 주 기준), 사건일 2026-06-24 | 표지·Item 4 맞음. counter_evidence 의 3.5%(3,487,084 주)는 13G/A 8호 `6590e52a069aebe0` 와 같다 |
| EV-palantir-068 | Surf Air 10-Q `0cefe6edacffbc5c-srfm-20260630.htm` | 세 조각 일치 | $5.0M, 4,761,905 주, 계약 다섯 건 | Note 10 Software License Agreements, p.18 맞음 |
| EV-palantir-069 | Palantir 10-Q `01188c16b36c3d0a` | 두 조각 일치 | $184M, $167M | Item 3, p.34 맞음. 주석 4(p.13)도 "privately-held companies" $167M 을 적는다 |
| EV-palantir-070 | 같은 10-Q | 일치 | 투자 계약·Investee 정의 | Item 1A, p.55 맞음 |
| EV-palantir-071 | 13G/A 2025-04-08 `f9f9ebb090e02b0d` | 두 조각 일치 | 593,438 주, 13.4%, 188,406 주 | 맞음. "그 뒤 신고 없음"과 NT 10-Q 두 건(2026-05-18·08-26)은 MSP 제출 목록과 같다 |
| EV-apple-097 | Globalstar 10-Q `b20a9e8a49f074da` | 네 조각 일치 | 400,000 단위, $4억, 20%, 1,600,000 단위 80% | p.12(Customer 정의)·p.14 맞음. 2024 Closing Date 는 2024-11-05 다 |
| EV-apple-098 | 같은 10-Q | 세 조각 일치 | — | Note 3, p.13 맞음 |
| EV-apple-099 | 같은 10-Q | 세 조각 일치 | $4억 비유동 부채 | p.14 맞음. 원문 "Regardless of whether or not the Mergers are successfully consummated" 가 relevance 의 "합병 여부와 관계없이"를 받친다 |
| EV-apple-100 | 같은 10-Q | 일치 | 15% | Item 2, p.30 맞음 |
| EV-apple-101 | 같은 10-Q | 두 조각 일치 | 330만 주 | p.12·p.28 맞음 |

### 두 판단 점검 요약

| 판단 | 점수(재계산) | 세 칸·표지 | 금지 표기 | 비고 |
|---|---|---|---|---|
| palantir.F5 | 12 + 3 − 10 = 5 | 올릴 9줄·내릴 9줄 모두 표지, 확정 근거 | 없음 | Surf Air 는 연결하지 않고 10-Q 특수관계자 주석(Karp 항공기만)에도 없어 관계사가 아니다. 합작법인 넷 누락(C2-1), 13G 대상 둘 누락(C2-2) |
| apple.F5 | 12 + 3 − 6 = 9 | 올릴 10줄·내릴 13줄 모두 표지, 확정 근거 | 없음 | inputs 불변. Xintec 구분 문장(C2-3) |

## CHECKLIST

| ID | 결과 | 근거 |
|---|---|---|
| Q03 | pass | 맺은 출자를 그 자체로 세는 읽기를 Palantir 에 TSMC 와 같이 댔고(재무 투자·대가로 받은 주식인지를 가르지 않음), 대가로 받은 지분은 거래 방향을 따라 NVIDIA(고객 지분은 셈)·OpenAI·Apple 워런트(공급자 지분은 조달)와 한 읽기다. 이름 없는 지분 묶음은 Amazon·Oracle·Alphabet 처럼 세지 않았다. Apple SPE 는 Meta 데이터센터 합작과 같은 자금 조달 구조 원칙이다. Palantir 의 합작법인 넷은 판정 칸에 없지만 원칙을 대도 지금 확정 근거로는 점수가 같다(C2-1). NVIDIA 가 자기 출자를 '떠날 수 있다'로 뺀 옛 문장은 그대로이고 이미 3 이라 점수에 닿지 않는다(앞선 확인 리뷰 C-1) |
| Q18 | pass | Surf Air 는 Palantir 가 연결하지 않고 특수관계자 주석에도 없다. Palantir 가 지배하는 일본·한국 합작법인은 동맹으로 세지 않았다. Globalstar SPE 는 Globalstar 가 80% 를 갖고 연결하는 VIE 이고 Apple 의 관계사가 아니다 |
| Q19 | pass | Palantir 가 센 지분은 Palantir 가 가진 Surf Air 주식이라 받은 투자가 아니다. SOMPO·HD Hyundai 가 Palantir 자회사에 넣은 소수 지분은 세지 않았다. Surf Air 의 독점 판매 파트너 관계는 지분 동맹 한 부분에만 넣었다 |
| Q20 | pass | Apple 의 Globalstar SPE 지분은 Apple 이 쓸 위성망을 짓는 자금 조달 구조라, 워런트는 공급자가 준 서비스 계약 대가라 조달로 뺐다. Palantir 의 모델 공급자 관계는 조달로 뺐고, Surf Air 지분은 Palantir 가 파는 쪽이라 조달이 아니다 |
| Q21 | pass | Surf Air 지분은 ⑤ 에서만 센다. Palantir ⑦ 세로축은 투자 계약 대상의 상업 계약(Strategic Commercial Contracts)으로 서고 Surf Air 가 그 대상인지는 공시에 없으며, ⑤ 지분 동맹과 ⑦ 돌아옴을 함께 두는 것은 Oracle(TikTok 합작)·Alibaba(Moonshot AI)와 같은 짝이다. Apple 은 Globalstar 를 ⑤ 에 넣지 않았다 |

## 다음 실행 과제

1. palantir.F5 에 합작법인 문단을 더한다(C2-1). 일본(SOMPO)·한국(HD Hyundai)은 지배해 관계사, 파트너 소수 지분은 묶임 증거가 없어 세지 않음, 중동·미국 공동 소유 법인은 상대와 지배 여부를 찾아 지배하지 않으면 맺은 출자로 더한다. 10-Q Item 1A 합작 문단을 근거로 확정하고 트리거를 둔다. 순위에 닿을 수 있다(단독 8위).
2. 이름 있는 미확인 지분을 모두 적는다. MSP Recovery 에 Faraday Future(2024-10 8.7%, 2026-07 위임장 설명서에 5% 초과 보유자 없음)와 Rubicon Technologies(2024-09 13.1%, 2025-01 등록 말소)를 더하고, 두 13G 를 근거로 확정한다(C2-2). Palantir 제출 목록은 2026-10-08 판 캐시라 그 뒤 13G 정정이 있는지 다시 본다.
3. 규칙 3절 ⑤ 에 '대가로 받은 지분은 거래 방향을 따르고, 따로 한 출자는 그 자체로 세되 내가 쓸 설비를 짓는 자금 조달 구조만 뺀다'를 한 문장으로 두고, apple.F5 의 Xintec 문장을 이 구분으로 다시 쓴다(C2-3).
4. 이름이 공시되지 않은 지분 묶음을 상대로 셀지는 14개사에 한 번에 정한다. 지금 읽기(세지 않음)는 Amazon·Oracle·Alphabet 과 같다. 반대로 정하면 Palantir(주석 4 가 "privately-held companies" 를 적어 Surf Air 밖 비상장 회사가 확인됨, ⑤ 6·단독 8위)와 Oracle(TikTok 합작 밖 비시장성 투자, ⑤ 10·조정 6, 순위 그대로)이 움직이고, Apple·Tesla 등은 자기 공시를 다시 훑어야 한다.
5. 방향 칸의 미확인 결론을 판정 칸으로 옮긴다(C2-4). 두 판단의 최상위 `evidence_ids`·`reconfirmed`·`reviewer` 를 고치고, 판단 세션이 제안한 트리거 셋을 넣는다(C2-5).
6. 개요 문장이 범위 항목을 싣게 렌더러를 고친다(C2-6, 앞선 확인 리뷰 C-3 과 같은 자리).
