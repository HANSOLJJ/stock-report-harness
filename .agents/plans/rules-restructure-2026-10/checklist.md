# 체크리스트 — 채점 규칙 문서 재편

## 0. 준비

- [x] 원본 저장소에만 있던 `output/ai-scorecard-2026-10-test/` 를 워크트리로 복사 (`approval.json` 제외)
- [x] 원본 저장소에만 있던 `validation/*/_raw` 세 폴더를 워크트리로 복사
- [x] 계획·체크리스트·결정 기록·조사 지시서 작성

## 1. 참조 조사

- [x] Run `run_aec0079c28ff` 생성 (감독형 dispatch)
- [x] muse 작업자 시작, 착수 확인 — task_4b40444d61b6 / ctx_670cefdda3c9 / term_977fa82f-f35a-4332-8267-ebeb4776e96c
- [x] agy 작업자 시작, 착수 확인 — task_f0b31824e118 / ctx_83c4de3af637 / term_80d31b11-4485-4f74-884f-aa7898010eef
- [x] `survey-muse.md` 수신, 핵심 주장 5건 직접 확인, 작업자 해제
- [x] `survey-agy.md` 수신, 작업자 해제 (정리 대상 터미널 0)
- [x] 두 결과를 `rg` 건수와 대조하고 어긋난 부분 확인 (어긋난 5건을 해당 행을 열어 판정)
- [x] 수정 위치 목록 확정 후 사용자 보고
- [x] 삭제 대상 문서 3개(구현계획, HANDOVER, design-guideline) 정독, 살릴 내용 추림

### 문서 현황 조사

- [x] md 파일 354개를 묶음별로 집계
- [x] `README`, `TODO`, `guide`, `structure`, 훅 설명서, 스킬 12개, 리뷰어 3개 정독
- [x] `validation/` 분류와 참조 관계 조사 (탐색 에이전트, 조율자 재확인 안 함)
- [x] 원본과 워크트리가 같은 커밋이고 md 내용이 같음을 확인
- [x] 계획 폴더를 원본 저장소로 이동 (2026-10-02)
- [x] 조사 결과를 `plan.md` 에 기록

## 2. 방침 확정

- [x] 문서별 처리안 제시
- [x] 새 규칙 문서 목차안 제시
- [x] `structure.md` 1절: 종목 리포트 기능이 살아 있는지 확인 (2026-10-06, 없다. `build_report.py` 는 `ai_scorecard` 전용)
- [x] `.claude/commands/` 없이 스킬만으로 명령이 동작하는지 확인 (2026-10-06, 동작한다)
- [x] 완료된 계획 폴더 두 개 삭제 (2026-10-02, `hook-fixes` 는 커밋 `140fd05`)
- [x] `.claude/commands/` 12개 삭제 (2026-10-06, 커밋 `3a3d697`)
- [x] 계획 재정리와 외부 피드백 다섯 가지 반영 (2026-10-06)
- [x] 사용자 확정 (2026-10-06, 여섯 가지 모두 권장안대로)

## 3. 채점표 v1.5 정독

- [x] `docs/scorecard/source/AI기업_채점표_v1.5.md`(1,145줄) 정독 (2026-10-06. 머리말·3~5절 전부, 1~2절 기업 카드는 규칙 표지어 전수 검색)
- [x] 살릴 내용을 `context-notes.md` 에 추가 (v1.7 에 없는 일반 원칙 네 가지)

## 4. 새 규칙 문서 `rules.md` 작성

- [ ] 현행 규칙 작성 (머리말, 공통 원칙, ①~⑨, 합산, 채택하지 않은 항목, 체크리스트, 미결)
- [ ] 옛 문서에서 살릴 내용 반영
- [ ] 문서 수치와 `v1.8.json` 키의 기계 대조
- [ ] 옛 조항 대응표(규칙 v1.7·`design-guideline` 의 절·조항 → 새 위치 또는 삭제 사유)

## 5. structure.md · guide.md 정리

- [ ] D-01~D-10, T-01~T-20 표를 `structure.md` 로 이동, 수용 기준의 현행·구버전 구분(T-01, T-10)
- [ ] 머리말 경위, 1절 비교표, 낡은 결정 표, 실측 기록 정리
- [ ] HANDOVER 7절 내용을 `guide.md` 로 이동, 3행 경로 수정
- [ ] `tests/test_scorecard_fix54_code.py` 통과

## 6. 코드·테스트 수정

- [ ] 표시 대응표(`render_common.py` `SOURCE_NAMES`·`WARNING_PHRASES`)에 별표 → 새 절 이름 추가. 저장 문구는 그대로
- [ ] 렌더러 문구(`render_common.py` 982·1600, `render_html.py` 1023·1122, `render_md.py` 359)
- [ ] 승인 페이지 용어집
- [ ] `factor-concepts.json` 과 `test_scorecard_fix76.py`
- [ ] 문서를 읽는 테스트 5개, 지우거나 생략된 검사의 대체 장부
- [ ] 이미 어긋난 참조 (`AGENTS.md 71행` → 절 이름, `design-guideline 272행`)
- [ ] 기준선 이관 명령의 기본 경로
- [ ] Python·Node 테스트 통과
- [ ] 승인 실행 두 개의 `validate_report_contract.py` 통과

## 7. 스킬과 리뷰어

- [ ] 재리뷰 상한을 1회로 통일 (`score-goal` 5번, `score-review` 상태 절의 `blocked` 정의, `score-review` 절차 4번)
- [ ] `score-goal` 5번에 "제안 반영 대기" 멈춤 지점 추가
- [ ] `score-plan` 3단계, `score-research` 2단계의 낡은 문구
- [ ] `score-collect` 의 별표 인용과 문서 경로
- [ ] `.agents/skills` 사본 갱신, `diff -rq .agents/skills .claude/skills` 빈 출력

## 8. 옛 문서 삭제

- [ ] 삭제 대상마다 `커밋 + 경로 + sha256` 대응표를 `rules.md` 에 기록
- [ ] `git show` 로 복원한 내용의 sha256 과 승인 실행 `sources.json` 등록 해시 대조
- [ ] 옛 문서 삭제 (한 커밋)

## 9. README · TODO · AGENTS.md 정리

- [ ] `README.md` 축소, 「아홉 항목」 표 다섯 곳 수정, 106·113·153행 경로
- [ ] `TODO.md` 4번·11번
- [ ] `AGENTS.md` 9행 경로, 추가 축소(결정 6)
- [ ] 가리킨 절이 실제로 있는지 전수 확인

## 10. validation

- [ ] `validation/` 을 사용자 방침대로 처리, 6개 파일과 `_raw` 보존 확인

## 11. 최종 검증

- [ ] Python·Node 전체 테스트
- [ ] 승인 실행 두 개의 `validate_report_contract.py`
- [ ] 지운 문서 경로·별표 이름·옛 행 번호 `rg` 전수 검색
- [ ] 대체 장부 확인, `.agents/skills` 일치 재확인
- [ ] 계획 폴더(`survey-*.md` 포함) 삭제
