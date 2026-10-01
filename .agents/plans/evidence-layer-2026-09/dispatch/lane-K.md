# 레인 K — 문서: 첫 방어선 위치, 판단 수정 사용법, 수집기 변경 반영

에이전트: Claude Sonnet 5.5. 의존: 레인 H·J 병합 완료. 공통 규약: `README.md` 를 먼저 읽는다. 레인 L(Muse)이 동시에 `tests/fixtures/evidence/` 를 만든다. 소유가 겹치지 않는다. **지금 코드가 사실이다. 명령과 인자는 `--help` 로 확인해 적는다.**

## 근거

- `validation/lane-H-review-fixes/REPORT.md` 의 "남은 것": 문서의 "첫 방어선 위치" 문구(`AGENTS.md`·`README.md`·`docs/scorecard/structure.md`). 승인·취소의 에이전트 거부는 이제 CLI 가 아니라 `stages` 의 승인·취소 함수 본체에 있다. `init --force` 는 승인 있는 실행에서 에이전트 세션이면 거부되고 훅도 막는다. 보호 훅은 쓰기 대상일 때만 막고 읽기는 통과한다. `scorecard/baseline/**` 도 보호한다.
- `validation/lane-J-judgment-edit/REPORT.md`: 판단 수정 기능(`judge` 명령, 승인 페이지의 판단 수정 절, `revision_history`, 점수 직접 수정 금지, 수정 뒤 재계산·리뷰·승인), 수집기 변경(NaN 종가 건너뛰기, 회사별 실패, `resolve-cik --json`, `SEC_UA` 영문 검사, `news_queries`, CIK 기입), 보호 훅의 PowerShell cmdlet·`find -delete`·`xargs`·글롭 판정, Muse 표지.
- `context-notes.md` 의 판단 수정 결정.

## 소유 파일

`README.md`, `AGENTS.md`, `docs/scorecard/structure.md`, `docs/scorecard/open-items.md`(이번 작업과 직접 관련된 줄만), `.claude/skills/score-approve/SKILL.md`, `.claude/skills/score-review/SKILL.md`, `.claude/skills/score-collect/SKILL.md`, `.claude/commands/score-*.md`(필요 시). 그 밖은 고치지 않는다(`scripts/hooks/README.md` 는 레인 H·J 가 이미 고쳤다).

## 할 일

1. 첫 방어선 위치 문구를 지금 구조로 고친다(위 근거).
2. 승인 절차 안내(README, `score-approve` 스킬)에 판단 수정을 넣는다. 사람이 승인 페이지에서 판단 입력을 고치는 방법, factor 별로 고칠 수 있는 것(F1·F4·F8 점수와 근거, F3 criteria, F5 등급, F7 매트릭스, F9 gate_inputs), 수정 뒤 해시가 바뀌어 에이전트에게 다시 계산·리뷰를 시킨 뒤 승인한다는 흐름, 같은 factor 의 다른 기업 판단을 함께 보라는 점. 에이전트가 판단을 제안할 때 `judge` 명령을 쓰는 방법은 `score-review` 와 `score-research` 쪽에 짧게.
3. 수집기 변경을 README 와 `score-collect` 스킬에 반영한다. NaN 종가는 직전 확정 종가로 기록된다는 것, 가격 실패가 회사 단위라는 것, `SEC_UA` 는 영문으로 적는다는 것, `news_queries` 로 질의를 좁힌다는 것, `companies.json` 에 12개사 CIK 가 들어갔다는 것.
4. README 훅 표를 지금 `scripts/hooks/guard.py` 와 맞춘다(PowerShell cmdlet 등 쓰기 형태, Muse 표지).

## 검증

- 문서에 적은 명령·인자가 `--help` 출력과 맞다.
- 에이전트에게 approve·revoke 를 시키는 문구 0건. 사람 절차로 적는 것은 괜찮다.
- 테스트 기준(unittest 1146건 중 실패 1·오류 14)에서 증가 없음. `npm run check` 통과.
- 보고서 `validation/lane-K-docs/REPORT.md` 를 커밋에 포함. 한국어 커밋, Co-Authored-By 금지, git push 금지, git stash 금지. 통합 브랜치 merge 가 거부되면 보고만.
- 문서는 Write·Edit 도구로 고친다. 셸 명령에 보호 경로 문자열이나 승인 명령을 넣지 않는다.
- 완료는 preamble 의 `worker_done`(--outcome 명시) 뒤 조율자 터미널 `term_be1eaaf8-815c-4231-a858-7229d925e5fe` 에 한 줄 안내.
