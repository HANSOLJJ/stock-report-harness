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
- [x] 1년 전 문서 2건 받기(+ TSMC 대만 IFRS 연간 2건, Oracle 10-K)
- [x] Oracle·TSMC·Alibaba 관측 29건 → 독립 검산 → 반영 → research·calculate(세 회사 listed_ttm, 나머지 11사 불변)
- [x] calculate → 비교 → 근거 문장 제안 PRP-001~004(Oracle ⑨·⑦, Alibaba ⑨, TSMC ⑨, 판정 재료·점수 불변) → 트리거 TRG-024·057 문장 수정
- [x] draft
- [x] 사람: 근거 34건 확정(72건 모두 confirmed), 제안 PRP-001~004 반영(`3ef3c01`)
- [x] research → calculate(점수 그대로) → draft → review-template
- [x] 1차 리뷰 4영역 모두 pass, 점수 영향 발견 0(`cf958b4`)
- [x] 사용자 결정으로 사실 오류 한 묶음 수정(렌더러 `08bfc90`, 트리거·근거 `6ae2ac9`, PRP-005 `96d522f`)
- [x] 확인 리뷰(2차) 4영역 모두 pass → review.md status pass → validate_report_contract PASS
- [x] 사람: 승인 페이지에서 승인(approval_valid)
- [x] 빌드 → report.html·audit.md·history.csv 14행, `validate_report_contract --require-html` PASS
- [x] (추가 2) 규칙 한 줄(`4ac450f`), 코드: 현재 문장만 렌더·기업 요약 필드·SUMMARY 제안·일괄 반영·검증기(`6a991ee`), 근거만 바꾸는 수정은 승계 유지(`5a284f5`)
- [x] (추가 2) 서브에이전트 5개가 판단 114개·요약 14개·근거·트리거 문장을 다시 씀 → `apply_rewrite.py` 검사 → 제안·직접 반영
- [x] (추가 2) 사람: `proposal --all-pending --accept` → research·calculate·draft(`9e336b6`) → 1차 리뷰(사실·재무·출력 pass, 규칙 needs_fix 4건)
- [x] (추가 2) 사용자 결정 "네 건 모두 다시 판정": 제안 PRP-134~137(`proposals.json`), 렌더러 꼬리표·여신 주석 수정
- [x] (추가 2) 사람: PRP-134~137 반영 → research·calculate·draft → 확인 리뷰(needs_fix: 요약 넷, oracle.F5 Stargate 원문 없음, openai.F4 Q03)
- [x] (추가 2) 사용자 결정 "한 묶음 더 고치고 좁은 확인": PRP-138~147, 근거·트리거 두 곳, 렌더러 ⑦ 메모 → 좁은 확인 4영역 pass → review.md pass
- [x] (추가 2) 사용자 지시 "나는 최종승인만": 근거 확정·제안 반영을 에이전트가 맡게 바꿈(사용자가 stages.py 두 줄 주석 처리, 문서·테스트 갱신)
- [x] (추가 2) 사람: 최종 승인(903d6cc9) → 재빌드(report.html) → `validate_report_contract --require-html` PASS → 화면 검사(320·768·1280px 넘침 0). 승인 전 검증이 옛 report.html 때문에 재승인을 막던 버그를 고침
- [ ] 다음 실행: 머리말·색인의 "앞서 매긴 판단" 3곳, References 의 "(긴장 #4·#11)" 표기, 리뷰 영역 파일의 「다음 실행 과제」 전부
- [x] 화면 검사(Playwright): 320·768·1280px 가로 넘침 없음, 넓은 차트는 가로 스크롤 상자(.mtwrap) 안. factor 탐색 링크 높이 19px(24px 미만, 렌더러는 시험 실행과 같음)는 다음 실행 과제

## 4. 리뷰
- [ ] 1차 리뷰(4 영역 + Q01~Q23)
- [ ] 수정 한 묶음
- [ ] 확인 리뷰 1회
- [ ] 승인 대기 보고
