# 레인 P — 재검증 발견 V2-5: 문서 속 재실행 순서 안내 고치기 (기계적 변경)

에이전트: Antigravity. 의존: 레인 V2 보고서 병합 완료. 공통 규약: `README.md` 를 먼저 읽는다. 레인 N(Opus)이 동시에 코드를 고친다. **코드 파일은 고치지 않는다.**

## 무엇이 문제인가

판단을 고치거나 근거를 확정한 뒤 다시 돌릴 단계 안내가 `calculate → draft → review` 로 적혀 있다. 실제로는 `research` 도 다시 돌려야 한다. 안내대로만 하면 승인 단계에서 "research 가 낡았다" 며 거부된다. 근거: `validation/lane-V2-recheck/REPORT.md` 의 V2-5 절.

## 할 일

아래 위치에서 판단 수정·근거 확정 뒤 재실행 순서를 `research → calculate → draft → review` 로 고친다. 문장의 다른 내용은 바꾸지 않는다.

- `AGENTS.md` 19행 근처
- `README.md` 78행·86행 근처
- `.claude/skills/score-approve/SKILL.md` 32행·36행 근처
- `.claude/skills/score-review/SKILL.md` 37행 근처
- `.claude/skills/score-collect/SKILL.md` 43행 근처
- `docs/scorecard/structure.md` 137행 근처
- 이 밖에 같은 순서(`calculate → draft → review`, `calculate·draft·review`, `/score-calculate` 부터 다시 등)를 판단 수정·근거 확정 맥락에서 적은 곳을 Grep 도구로 모두 찾아 같이 고친다. 처음 채점의 정상 순서를 적은 곳(plan → collect → research → calculate …)은 이미 research 가 있으므로 건드리지 않는다.

## 소유 파일

`AGENTS.md`, `README.md`, `docs/scorecard/structure.md`, `.claude/skills/score-*/SKILL.md`, `.claude/commands/score-*.md`, 보고서. **`scripts/**`·`server/**`·`tests/**` 는 고치지 않는다**(코드 속 같은 문구는 레인 N 이 고친다).

## 검증

- 고친 위치마다 전후 문장을 보고서에 표로 적는다. Grep 으로 판단 수정·근거 확정 맥락의 `calculate → draft → review` 가 남지 않았는지 확인한 명령과 결과를 붙인다.
- 테스트 기준(unittest 1146건 OK, 건너뛰기 13)에서 실패 0 유지. `npm run check` 통과.
- 문서는 Write·Edit 도구로 고친다. 셸 명령에 보호 경로 문자열이나 승인 명령을 넣지 않는다.
- 보고서 `validation/lane-P-rerun-order/REPORT.md`. 한국어 커밋 하나, Co-Authored-By 금지, git push 금지, git stash 금지. 통합 브랜치 merge 가 거부되면 보고만.
- 완료는 preamble 의 `worker_done`(--outcome 명시) 뒤 조율자 터미널 `term_be1eaaf8-815c-4231-a858-7229d925e5fe` 에 한 줄 안내.
