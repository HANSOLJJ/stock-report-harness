# 레인 K 문서 보고서 (2026-10-01)

지시서 `.agents/plans/evidence-layer-2026-09/dispatch/lane-K.md` 를 따랐다. 코드는 고치지 않았고 문서와 스킬·명령 파일만 고쳤다.
명령과 인자는 `scorecard_cli.py {judge,collect,resolve-cik,add-company} --help` 와 `--help` 전체 출력으로 확인해 적었다.

## 한 일

| 파일 | 변경 |
| --- | --- |
| `AGENTS.md` | 통제의 위치: 첫 방어선을 `scorecard.stages` 의 `approve`·`revoke` 함수 본체 거부(CLI 든 import 든 같은 판정)로, `init --force` 거부 추가. 정성 판단 수정 길(`judge`) 한 줄 추가. 수집 줄에 `SEC_UA` 영문, NaN 종가 대체, 회사 단위 가격 실패 추가 |
| `README.md` | 쓰는 법 표에 판단 수정 행. 근거 계층에 NaN 종가·회사별 실패·`SEC_UA` 영문·`news_queries`·12개사 CIK·`resolve-cik --json`. 승인 페이지 절에 「판단 수정」(factor 별 표, 같은 factor 의 다른 기업 비교, 해시 변경 뒤 재계산·리뷰·승인)과 옛 문장 "판단을 입력하는 명령은 아직 없습니다" 삭제. 훅 표의 `protect_sensitive_files` 에 PowerShell cmdlet·복사 목적지·`find`·`xargs`·글롭·상위 폴더 판정. 첫 방어선 문단에 함수 본체 거부와 환경변수 표지(Muse `MUSE_TOOL_USE_ID` 포함). 다음 할 일 6번을 현황에 맞게 고침 |
| `docs/scorecard/structure.md` | 판단 스키마에 `revision_history`, 흐름도에 판단 수정, 잠금 줄에 `confirm`·`judge`, 수집기 변경, 「판단 수정」 절, 승인 절과 훅 절의 첫 방어선 문구 |
| `.claude/skills/score-approve/SKILL.md` | 첫 방어선 위치, 사람 절차에 판단 수정 단계와 「판단 수정」 절, 해시 변경 절 |
| `.claude/skills/score-collect/SKILL.md` | `SEC_UA` 영문, NaN 종가, 회사 단위 가격 실패, `news_queries`, CIK·`resolve-cik` |
| `.claude/skills/score-review/SKILL.md` | 「판단 수정을 제안할 때」 절(`judge` 인자, factor 별 키, 같은 factor 비교, 수정 뒤 재계산) |
| `.claude/commands/score-research.md` | `judge` 로 판단 입력을 고치라는 한 줄(스킬 본문은 소유 밖이라 명령 파일에 둠) |

README 훅 표는 `scripts/hooks/guard.py` 의 `_PROTECTED_*` 목록과 `scripts/hooks/README.md` 의 판정 표를 대조해 맞췄다. 보호 목록 자체(`.env*`, `.git/`, `.github/workflows/`, `docs/finance-style-guide.md`, `approval.json`, `v1.5~v1.7.json`, `history.csv`, `scorecard/baseline/**`, 두 실행 폴더)는 이미 맞아 있었다.
Muse 표지는 `guard.py` 가 아니라 `stages.AGENT_ENV_MARKERS` 에 있어 첫 방어선 문단에 적었다.

## 검증

| 항목 | 결과 |
| --- | --- |
| 명령·인자가 `--help` 와 맞음 | `judge`(`--company --factor --set --evidence --json --reason --by --take-lock`), `collect`, `resolve-cik`(`--company --from-file --apply --json`)를 대조했다. 판정 재료 키와 허용값은 `schema.JUDGMENT_EDIT_KIND`·`JUDGMENT_INPUT_CHOICES` 와 맞춘다 |
| 에이전트에게 승인·취소를 시키는 문구 | 0건. `README.md`·`AGENTS.md`·`docs/**`·`.claude/**` 에서 `scorecard_cli.py approve\|revoke`, `stages.approve\|revoke` 실행 문구를 검색해 무일치 |
| `unittest discover` (merge 뒤) | 1146건, 실패 1·오류 14. 기준선과 같다(원자료 부재). 늘어난 실패 없음 |
| `pytest -q` (merge 뒤) | 15 failed, 1133 passed. 레인 J 보고서 수치와 같다 |
| `npm run check` | 종료 코드 0 |
| `git diff --stat HANSOLJJ/revision_checker...HEAD` | 위 7개 소유 파일(보고서 커밋 전) |
| `git merge HANSOLJJ/revision_checker` | 성공, 충돌 없음(`checklist.md` 한 파일 문서 커밋 1건) |

## 소유 밖에서 발견한 문제 (고치지 않음)

- `.claude/skills/score-research/SKILL.md` 는 소유 파일 목록에 없어 고치지 않았다. 지시서 2번은 `score-research` 쪽에도 `judge` 안내를 요구하므로, 필요하면 조율자가 소유를 열어 주거나 그 스킬에 한 절을 옮긴다.
- `docs/scorecard/open-items.md` 는 이번 작업과 직접 관련된 줄이 없어(판단 입력·수집기·방어선 언급 없음) 고치지 않았다. D-07(`--by` 확보 절차)은 승인자 문제라 별개다.
- README 「지금 상태」 표(테스트 797건, 재승인 대기)는 2026-09-21 값이라 낡았다. 이번 지시 범위가 아니어서 두었다.
- 레인 J 가 적은 `validation/recheck_worker_final.py` 의 승인 함수 호출 문제는 그대로다.

## 남긴 것

- 승인 페이지 8절을 실제 브라우저로 열어 문서의 단계와 맞대지는 않았다(레인 J 보고서의 수동 확인과 `server/approvals.js` 문구로 대조했다).
- 최종 커밋 SHA 는 이 보고서 커밋이다(worker_done 본문에 적는다).
