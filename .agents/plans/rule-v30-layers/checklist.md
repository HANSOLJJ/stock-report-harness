# 규칙 v3.0 체크리스트

설계는 `plan.md`(2026-10-14 대화의 설계안 사본, 규칙 문언의 원본은 rules.md), 구현 순서는 `implementation.md`(2026-10-14 승인된 구현 계획)를 따른다. 단계 하나가 커밋 하나다. 이정표(기반 S0~S5, 계산 S6~S9, 출력·시범 S10~P1)마다 사용자에게 보고한다. 단계마다 `uv run --frozen python -X utf8 -m unittest discover -s tests -t .` 와 `npm run test:node` 를 돌린다.

## 문서
- [x] v2.2 초안의 커밋하지 않은 ②③ 수정과 context-notes 를 `draft/rules-v2.2` 에 기록용으로 커밋
- [x] `draft/rules-v3.0` 브랜치 생성
- [x] 계획 폴더(plan·checklist·context-notes) 생성
- [x] S1b rules.md 를 v3.0 으로 절 단위 개정(머리말, 1 총점, 2.10 층과 단위·2.11 끝난 싸움, 3 ①~⑤, 4 ⑥~⑨, 5 합산, 7 체크리스트 Q24·Q25, 8 미결). `test_scorecard_fix52_docs` 는 v3.0.json 이 생길 때(S2)까지 빨강

## 코드 (시험 실행까지 최소 경로)
### 이정표 1: 기반
- [x] S0 승인된 rejudge(v2.0)·v21(v2.1) 실행을 재계산 해시 테스트에 넣기(main e1e4d30, `tests/test_approved_runs_recompute.py`)
- [x] S0b 승인 페이지의 중첩 재료 `[object Object]` 표시 고치기(main 29e1167)
- [x] main 을 `draft/rules-v3.0` 에 병합
- [x] S2 `scorecard/rules/v3.0.json` 과 스키마 수용(layers, unit, curve, 새 judgment kind, 체크리스트 Q24·Q25). v2.1.json 을 출발점으로 생성했고 함정 구간표는 ×4 값을 함께 둔다. 계산은 아직 옛 경로(S3~S9 에서 붙임)
- [x] S3 연속 구간 도우미와 ⑥·⑨ 곡선, ⑦·⑧ ×4. 비상장 기업가치가 범위면 `policies.f6.estimate_range_end`(low·high·mid)가 정할 때만 점수, 없으면 needs_rule_decision(P0 에서 정함)
- [x] S4 판단 키에 layer·business, 다섯 판정 재료의 모양 검사, 매출 줄 교차 검사, `JudgmentLookup.units`, 중첩 근거 교차 참조, 제안의 layer·business 키(`rejudge_findings` 는 이미 판단 ID 단위라 테스트로만 잠금)
- [x] S5 층·사업 판단 생성·수정 경로, init 단위 전환, 트리거·근거 교차 참조 처리(다른 회사 근거 인용 결함 수정), CLI `--layer`·`--business`, v3.0 실행의 `diff` 거부, 승인 페이지 카드 id 와 층·사업 판단 읽기 전용
- [x] 이정표 1 보고(2026-10-14, ④ 부문 이익률 미공시·기업용 소프트웨어 결정 받음)
### 이정표 2: 계산
- [x] S6 ④ 보유표와 층 무게(`calc_layers.py`). 로켓 발사의 그 분야 순위 비교는 시장 정의표가 생긴 뒤(경고만)
- [x] S7 ②③ 층 계산(`calc_layers._layered`·`compute_f2_layers`·`compute_f3_layers`). 미확인 경로는 판정 대기, ③ 가속도 결측만 0 + 자료 없음
- [x] S8 ① 사업 단위 계산(시장 자료 전, D·E 는 미확인 1.6 씩). AI 상한 16 은 시장 자료 전에는 걸릴 수 없다(최고 15.2)
- [ ] S9 ⑤ 동맹 세 부분·적대 띠
- [ ] 이정표 2 보고
### 이정표 3: 출력·문서·시범 실행
- [ ] S10 초안·미리보기 렌더 최소
- [ ] S11 structure·guide·score-research·score-review 문서
- [ ] P0 시범 init 전 규칙 값 확정(rules.md 8절, implementation.md 「구현 전에 정할 것」)

## 시험 실행
- [ ] P1 시범 `init ai-scorecard-2026-10-v30pilot --from-run ai-scorecard-2026-10-v21 --rule v3.0 --companies alphabet,apple,tsmc,spacex-xai,anthropic` 으로 draft 까지
- [ ] 전체 14개사 시험 실행

## 뒤로 미룸
- [ ] 시장 정의표 `scorecard/markets/`·`calc_market.py`·규칙 sha256 연결(그 전까지 ① D·E 는 정책 기본값 0)
- [ ] HTML 리포트(산점도 축·80점 선·방법 카드·층별 화면), 승인 페이지 층별 수정 화면
- [ ] AGENTS.md 문구(main)
