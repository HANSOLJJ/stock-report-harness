# 2026-10 정기 재채점 (ai-scorecard-2026-10-rescore)

## 목표

규칙 문서 재편(2026-10-06) 뒤 10월 시험 실행(`ai-scorecard-2026-10-test`)을 이어받아 14개사를 다시 채점한다.
`plan → collect → research → calculate → draft → review` 까지 진행하고 "승인 대기"에서 멈춘다(`score-goal`).

- 실행: `ai-scorecard-2026-10-rescore`, 규칙 v1.8, 기준일 2026-10-06, `init --from-run ai-scorecard-2026-10-test` (2026-10-06 생성)
- research 는 이전 트리거 79건(기준선 39 + 시험 실행 40)을 모두 처리해야 진행된다(`stages.trigger_carry_gaps`).

## 트리거 처리 방침 (2026-10-06 사용자 확정)

새 `triggers.json` 의 항목 하나는 이전 트리거 하나만 `carry {ref, checked_at, finding}` 로 가리킨다. 그래서 79건마다 항목이 하나씩 있다.
ref 형식은 `baseline/v1.5:TRIG-NNN`, `ai-scorecard-2026-10-test:TRG-NNN`. `checked_at` 은 2026-10-06 이후.
`*` 는 수집 결과로 발동(`fired`) 여부를 정한다. fired 는 evidence_ids 나 source_ids 가 있어야 한다.

### 기준선 — 관찰 유지 (15)

| 트리거 | 새 항목 | 비고 |
|---|---|---|
| TRIG-003 NVIDIA ACIE 비중 | nvidia F8 | 025 흡수 |
| TRIG-004* Meta Muse Spark 1.2 오픈웨이트 | meta F3 | 출시됐으면 발동 |
| TRIG-006* AWS–Azure Interconnect GA | amazon F2 | GA 됐으면 발동 |
| TRIG-008 Azure 달러 공시 2개 분기 | microsoft F3 | 033 의 MS 부분 흡수 |
| TRIG-009 OpenAI MDL 3143 | openai F5·F9 | |
| TRIG-012 신용 지표 교차검증 | oracle F7·F8·F9 | 018 흡수. 점수 입력 아님(rules 2.8) |
| TRIG-016 NVIDIA 우발 보증 발동 | nvidia F9 | 017 흡수 |
| TRIG-019 Anthropic 단가 프리미엄 | anthropic F1 | 039 흡수 |
| TRIG-020 GPT-6 Astra 매출·채택 | openai F1·F3·F6·F9 | 021·023 흡수 |
| TRIG-024 SpaceX 영업손실률 4분기 | spacex-xai F9 | 현행 ⑨ 방향 완화 조건(rules 323행)으로 다시 씀 |
| TRIG-027 Cursor 의 Claude 사용 비중 | anthropic F8 | |
| TRIG-028 Cybercab·Starlink V5 | tesla F3 | |
| TRIG-034 Anthropic 자체 칩 | anthropic F4·F8 | |
| TRIG-036 증류 소송 | alibaba F2·F5 | |
| TRIG-037 하이퍼스케일러 FCF | alphabet F9 | 아마존 부분은 TRG-005 |

### 기준선 — 시험 실행 트리거로 잇고 중복 철회 (12)

001→TRG-015(항목에 F1 추가), 005→TRG-017, 007→TRG-004, 010→TRG-036, 013→TRG-010, 014→TRG-010, 015→TRG-036,
022→TRG-040, 026→TRG-033, 029→TRG-030(Tesla)·TRG-034(SpaceX), 032→TRG-021, 035→TRG-036.

### 기준선 — 기준선 안에서 잇고 중복 철회 (7)

025→003, 017→016, 018→012, 021→020, 023→020, 039→019, 033→008(MS)·TRG-011(Meta).

### 기준선 — 날짜가 지나 결론 (2)

- TRIG-011 Oracle Q1 FY27 실적(9/10): 만료. 실적은 시험 실행 관측에 들어갔고 RPO·약정 변화는 TRG-022·024 가 이어서 본다.
- TRIG-031* Apple iOS 27 새 Siri(9월): 출시면 발동(③ 2→3 후보), 연기면 만료.

### 기준선 — 철회 (3)

- TRIG-002 NVIDIA $500B 커밋 분해: ⑦ 판정표에서 가로축이 "큼"이면 세로축이 점수를 가르지 않는다. NVIDIA 는 −2(하한). 판단 근거의 "분해 대기"만 남긴다.
- TRIG-030 ⑥ 구간 경계: v1.7 부터 구간표를 쓰지 않는다.
- TRIG-038 SDLLMTK 추가 하락: 쓰는 방식은 `TODO.md` 13번에서 정한다.

### 시험 실행 40건

모두 자기 자신을 가리키는 carry 를 달고, 수집 후보로 기준일까지 조건 충족 여부를 확인해 결론을 적는다. 기본은 관찰 유지.
흡수한 항목(TRG-004·010·015·017·021·030·033·034·036·040)은 조건에 흡수 내용을 더한다.
TRG-007·012·019·021 문장의 "별표 D" 는 "계획 0점 원칙"으로 바꾼다.

## 단계

1. collect (뉴스·공시·가격) → 후보 선별
2. `trigger-candidates` 로 트리거별 기사 확인 → triggers.json 79항목 작성
3. research → calculate → draft → review(1차 리뷰·수정 한 묶음·확인 리뷰 1회) → 승인 대기
