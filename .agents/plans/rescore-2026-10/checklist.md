# 2026-10 정기 재채점 체크리스트

## 0. 준비
- [x] 10월 시험 실행 묶음과 history.csv 14행 커밋(`b170b9e`)
- [x] `init --from-run ai-scorecard-2026-10-test --rule v1.8 --as-of 2026-10-06`
- [x] 트리거 처리 방침 확정(plan.md)
- [x] SDLLMTK 를 TODO 13번으로(`ccd3816`)

## 1. 수집
- [x] init 다시 함(price_as_of 2026-10-05, info_cutoff 2026-10-06)
- [x] collect (news·filings·prices) — 가격 12사 10-05 종가, 공시 12사(anthropic·openai CIK 없음)
- [x] 후보 선별(근거 34건 candidate) — 서브에이전트 5개(A nvidia·tsmc·apple / B alphabet·amazon·microsoft / C meta·oracle·palantir / D anthropic·openai / E alibaba·tesla·spacex-xai)가 스크래치 `work/out-<그룹>.json` 으로 냄. 공통 지시서 `work/INSTRUCTIONS.md`, 합치기 `merge_outputs.py`(새 항목 TRG-041~). 대상: 뉴스 10-01~10-06, 공시 09-02~10-06

## 2. 트리거
- [x] 79항목 반영(관찰 56, 철회 22, 만료 1, 발동 0). 기준선에서 만든 항목은 TRG-041~079(대응은 스크래치 `work/trigger-id-mapping.json`)
- [x] `*` 건: 004·006·031 모두 확인 못 해 watching(031 은 기한 11-06)
- [x] research 통과(gaps 0, overdue 0)

## 3. 계산·초안
- [x] calculate — TSMC ⑥ −3→−5, Oracle ⑥ −2→−3(가격 갱신으로 P1 경계 통과). 나머지 12사 동일
- [x] 규칙 v1.9 와 코드·테스트(`f0d6aa5`), 버전 번호를 rules.md 머리말 한 곳에(`dbe3098`)
- [x] 실행을 v1.9 로 다시 만듦 → collect → 근거·트리거 재반영(출처 ID 3건 대응) → research·calculate(점수 v1.8 때와 같음)
- [ ] 1년 전 문서 2건 받기(TSMC 2025-08 6-K 재무제표, Alibaba 2025-08 실적)
- [ ] Oracle·TSMC·Alibaba 관측 만들기(서브에이전트 3) → 기계 대조 → 반영
- [ ] calculate → 비교 → ⑨ 판정 입력 제안·트리거 finding(TRG-057 등) 수정
- [ ] draft

## 4. 리뷰
- [ ] 1차 리뷰(4 영역 + Q01~Q23)
- [ ] 수정 한 묶음
- [ ] 확인 리뷰 1회
- [ ] 승인 대기 보고
