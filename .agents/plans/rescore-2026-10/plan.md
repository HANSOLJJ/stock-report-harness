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

## 추가: 규칙 v1.9 와 재무 관측 갱신 (2026-10-06 사용자 승인)

계산해 보니 재무 관측이 낡은 회사가 셋이다. Oracle 은 일반 트랙인데 2026-05-31 분기에 머물러 있다(8-31 분기 10-Q 있음). TSMC·Alibaba 는 v1.8 이 예탁증서 상장사를 무조건 연간 트랙으로 둬서 2025 연간·FY2026(3월 결산) 값을 쓰고 P4 한 칸 감점을 받는데, 둘 다 6-K 로 분기 숫자를 낸다. 사용자 결정: v1.9 로 가되 문서를 늘리지 않는다.

1. **규칙 v1.9 와 코드.** `v1.9.json` = v1.8 복사 + `rule_version`·`note`·`tracks.listed_ttm/listed_annual.select` 문구·새 키 `policies.f6.track_by_period_basis: true`. `calc_f6_params.track_id_for` 는 새 키가 있을 때만 예탁증서 + ttm 을 `listed_ttm` 으로 보낸다(v1.5~v1.8 불변). 테스트 `test_rules_v19.py` 와 트랙 판정 테스트.
2. **버전 번호를 한 곳에만.** 현행 버전은 `rules.md` 머리말과 JSON 만 갖는다. AGENTS 12행, guide 69·91행, structure 33·130행, score-plan 15·17행(+사본), README 42행을 "현행 버전(rules.md 머리말)" 으로. 사실 기록은 그대로.
3. **실행을 v1.9 로 다시 만들기.** 폴더를 스크래치로 옮기고(훅 오탐 때문에 --force 대신) init --rule v1.9 + 같은 날짜 → collect → `merge_outputs.py --write`(TRIG-011 finding 수정) → research.
4. **재무 관측.** 1년 전 문서 2건(TSMC 2025-08 6-K 재무제표, Alibaba 2025-08 실적) 추가로 받는다. 세 회사 `revenue_ttm`·`revenue_ttm_prior`·`operating_income_ttm`·`net_income_ttm`·`pretax_income_ttm`·`fcf_ttm`·`cash`·`net_cash`(+TSMC·Alibaba `operating_margin_ttm`, Oracle `contracted_revenue`·미인출 여신). 최근 1년 = 직전 연간 − 전년 같은 기간 + 올해 같은 기간, 성분 접수번호·위치 기록, 20-F 선언 환율 하나로 당해·전년 환산. 옛 관측은 두고 `observed_at 2026-10-06` 으로 덧붙임. 서브에이전트 3개(회사별)가 스크래치에 내고 조율자가 기계 대조 후 반영.
5. **계산·판단.** calculate → 회사별 비교 → 어긋나는 ⑨ 판정 입력은 propose 로 제안 → 관련 트리거 finding 수정 → draft → 리뷰 → 승인 대기.

## 추가 2: 완결된 문장만 싣기 (2026-10-06 사용자 지시)

사용자 지시: 리포트에는 최종 결과만, 문장은 그 자체로 읽히게 쓴다. "v1.5 에서 어쩌고", 취소선, 작업 번호, 다른 판·다른 문장을 가리키는 끝없는 참조 구조를 쓰지 않는다. 지금 실행에서 고치고 다음 실행도 그렇게 나오게 준비한다.

현황: 판단 114개(승계 102) 가운데 47개, 근거 줄 96개에 v1.5·🆕·FIX·취소선·superseded 표기. 렌더러는 그 위에 대체된 옛 판단(취소선)·기준선 과거 기록·기준선 요약(`tag`)·기준선 순위·기준선 트리거 표를 덧붙인다.

1. **규칙**: AGENTS.md 「금지·주의」와 score-collect·score-review 스킬에 한 줄. 판단·근거·트리거·요약 문장은 완결된 현재 상태 문장으로 쓰고, 규칙 버전·변경 표시·작업 ID·이전 판·다른 문장·다른 트리거를 가리키는 표현을 쓰지 않는다. 경위는 revision_history·커밋.
2. **코드**: ① 판단 파일에 기업별 현재 한 줄 요약(`company_summaries`)을 두고, 제안(`propose --factor SUMMARY`)과 반영으로만 바꾼다. 카드는 이것만 쓰고 기준선 `tag`·기준선 순위를 쓰지 않는다. ② 근거 블록은 판단의 현재 문장만 싣는다(대체된 옛 판단·기준선 과거 기록·기준선 참고 서술·교체 주석 없음, 이력은 감사 기록으로). ③ 리포트·초안에서 기준선 트리거 표와 그 안내문을 뺀다. ④ 검증기(v1.9 이상)가 판단 근거·요약·근거 문장·트리거 관측·조건에서 금지 표기를 찾으면 실패한다. ⑤ `proposal --all-pending --accept`(사람 셸 전용) 로 대기 제안을 한 번에 반영. 테스트.
3. **데이터**: 서브에이전트 5개(기업 묶음)가 판단 114개의 근거를 현재 상태 문장으로 다시 쓰고 기업 요약 14개를 쓴다(점수·판정 재료 불변, 숫자는 확정 관측과 대조). 조율자가 금지 표기·숫자 대조 후 제안으로 올린다. 근거(evidence.json)·트리거 문장은 조율자가 직접 고친다.
4. **사람**: 제안 일괄 반영 → research·calculate·draft → 1차 리뷰(사실 영역은 다시 쓴 문장 전수 대조) → 확인 1회 → 재승인 → 재빌드.

검증: 전체 테스트, 승인 실행 두 개 `validate_report_contract` 재계산 통과, 관측 기계 대조(변조 사본 포함), 세 회사 트랙 `listed_ttm`·나머지 11사 불변, 지시 문서의 v1.8 하드코딩이 사실 기록뿐인지 `rg`.
