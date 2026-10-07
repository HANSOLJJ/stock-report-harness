# 체크리스트 — 근거 세 칸 · 트리거 표 · 탭 (plan.md 의 단계 순서)

구현 세션(Sonnet 5.5 또는 Opus)이 위에서부터 진행하며 체크한다. 각 단계는 한 커밋이다. 단계 끝마다 전체 테스트를 돌린다.

## 0단계 — 준비

- [x] 계획 파일 세 개(plan·checklist·context-notes)를 이 폴더에 만들고 커밋 (Fable 세션, 2026-10-07)
- [x] `git log --oneline -3` 으로 시작점 확인(바로 앞 커밋이 이 계획 파일 커밋)
- [x] 사용자에게 승인 취소 요청(`http://127.0.0.1:3000/approve/ai-scorecard-2026-10-rescore`, 6자리 코드). 6단계 전까지만 되면 된다

## 1단계 — 자료 구조·검증·CLI·승인 페이지

- [x] `schema.py`: `JUDGMENT_DIRECTION_FIELDS`, 항목 선택 키 `evidence_up`·`evidence_down`, `_validate_revision_history` 선택 키 완화, `validate_proposals` 의 `*_after` 두 키와 스냅숏 선택 키
- [x] `stages.py`: `_judgment_snapshot`·`_check_judgment_changes`·`revise_judgment`(v1.9 이상 쓰기 전 세 칸 검사)·`undo_proposal`·`add_proposal`·`decide_proposal`·`_summary_*`
- [x] `validate.py`: `THREE_WAY_MIN_RULE`, `three_way_item_violations`, `three_way_violations`, `self_contained_violations` 가 up/down 줄도 검사, `validate_scorecard` 에 check 추가
- [x] `scorecard_cli.py`: `propose`·`judge` 에 `--up`·`--down`, `--json` 키, 출력 문구
- [x] `tests/test_collect_stage.py` Sandbox 에 `rule_version` 인자(기본 v1.8)
- [x] `tests/test_evidence_three_way.py` 신규(plan.md 1단계 케이스 전부)
- [x] Python 테스트 전부 통과 → 커밋 `feat(judgments): 판단 근거를 판정·올릴 근거·내릴 근거 세 칸으로…`
- [x] `server/approvals.js` 판단 수정 폼 세 칸·`buildJudgeArgs`·제안 diff·판단 카드
- [x] `tests/node/fixtures/summary.sample.json`·`tests/node/approvals.test.js` 갱신, `tests/test_approval_commands.py` SummaryShapeTest 통과
- [x] `npm run test:node` 통과 → 커밋 `feat(approvals): 승인 페이지가 근거 세 칸을…`

## 2단계 — 렌더러(카드·초안 세 칸)

- [x] `render_common.evidence_block` 에 `verdict`·`up`·`down` 추가(`lines` 는 판정 줄로 유지)
- [x] `render_html.render_cards` 세 칸 마크업 + CSS(860px 두 열), 옛 모양은 그대로
- [x] `render_md` 초안 카드 `판정 / 올릴 근거 / 내릴 근거` 소제목, 옛 모양은 그대로
- [x] 색인(`BASIS_DOC`·`render_code_index`)에 세 칸 설명 한 줄
- [x] 테스트 추가(v1.9 박스 렌더 라벨·"없음", v1.8 박스 라벨 없음) → 전체 통과 → 커밋

## 3단계 — 트리거 표 두 덩어리

- [x] `_render_active_triggers` 두 칸 마크업(`class="trig"`, `td.tmeta`), 마크다운 표는 그대로
- [x] CSS: `.trig td.tmeta`, 640px 이하 세로 쌓기, `.narrow` 선택자 구체성 수정
- [x] `tests/test_trigger_render.py` 보강 → 전체 통과 → 커밋

## 4단계 — 탭

- [x] `render_document` 를 6개 `section.tabpanel` 로 묶고 절 번호 재부여, 머리·꼬리는 탭 밖
- [x] 탭 바 마크업 + sticky CSS + 인쇄 CSS + `.js .tabpanel[hidden]`
- [x] JS: `activate`, 초기 탭 판정, 앵커 클릭 캡처, `hashchange`, 순위표 행 클릭
- [x] `tests/test_report_tabs.py` 신규(탭 6개, 앵커 무결성, 패널 표지, 패널 밖 h2 없음)
- [x] 기존 메모리 렌더 테스트(fix54_render·fix66·add04a·hash_binding) 통과 → 커밋

## 5단계 — 문서·스킬

- [x] `docs/scorecard/guide.md` 5.5 「근거 세 칸」 절(분류 기준 표 포함)
- [x] `docs/scorecard/structure.md` 63·162행
- [x] `AGENTS.md` 「금지·주의」 한 줄
- [x] 스킬 `score-research`·`score-review`·`score-approve` + `.agents/skills` 사본 동기화
- [x] 커밋

## 6단계 — 판단 114개 재분류 → 리뷰 → 승인 대기

- [x] (전제) 사용자가 승인 취소함(2026-10-07)
- [ ] `SPLIT-INSTRUCTIONS.md` 작성(이 폴더)
- [ ] 서브에이전트 5개가 기업 묶음별 JSON 산출
- [ ] 기계 검사 스크립트(토큰 보존·금지 표기·up+down≥1·점수 표기는 판정 칸만·중복 0) + 변조 사본으로 검사가 걸리는지 확인
- [ ] `propose --json` 114건 → `proposal --all-pending --accept` → `three_way_violations` 0
- [ ] `research → calculate → draft`, 14개사 total·rank 불변 확인, `review-template --force`
- [ ] 4영역 1차 리뷰 → 수정 한 묶음 → 확인 리뷰 1회 → `review.md` pass → `validate_report_contract.py`
- [ ] "승인 대기" 보고
- [ ] (사람) 최종 승인 → `build_report.py` → `--require-html` → Playwright(320·768·1280, 탭, 앵커 세 갈래, 트리거 표 폭) → 커밋
- [ ] 이 폴더 checklist·context-notes 마무리
