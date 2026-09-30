# 워커 공통 규약 — 근거 수집 계층 도입 (2026-09-30)

이 폴더의 `lane-*.md` 가 각 레인의 지시서다. 이 문서는 모든 레인에 공통으로 적용된다. 계획 전문은 `../plan.md`, 결정 기록은 `../context-notes.md`, 진행 상황은 `../checklist.md` 다. 지시서와 계획이 다르면 지시서가 우선하고, 그 사실을 보고서에 적는다.

## 저장소와 브랜치

- 통합 브랜치는 `HANSOLJJ/revision_checker` 다. 조율자(Fable 세션, 워크트리 `revision_checker`)가 이 브랜치를 소유하고 워커 브랜치를 검증한 뒤 병합한다.
- 워커는 자기 워크트리의 브랜치에서만 커밋한다. 통합 브랜치나 `main` 에 직접 커밋하지 않는다.
- `git push` 는 하지 않는다. 원격 반영은 사용자가 직접 한다.
- 원본 폴더 `E:/sourcecode/01_side_project/stock-report-harness` 는 읽기 전용 참고 자료다. 거기에 쓰지 않는다.
- 워크트리 setup 이 `npm install` 을 돈다. 그로 인한 `node_modules/`·`package-lock.json` 변경은 커밋하지 않는다.

## 환경

- Python 은 uv 로만 실행한다. `uv run --frozen python -X utf8 <스크립트>` 형식이다. 시스템 `python`·`python3` 를 직접 부르지 않는다.
- 첫 `uv run` 이 `.venv` 를 만든다. 수 초 걸린다.
- 테스트 러너 둘을 모두 돌린다.
  - `uv run --frozen python -X utf8 -m unittest discover -s tests -t .`
  - `uv run --frozen pytest -q`
- 기준선: 이 브랜치의 새 워크트리에서는 757건 실행에 실패 7·오류 30 이 난다. 원인은 gitignore 된 `plan/`·`drafts/` 파일 부재이고 레인 A 의 2.2 가 해소한다. 목록은 `baseline-failures.txt` 다. **내 변경으로 이 집합이 늘면 안 된다.** 줄어드는 것은 좋다.
- `npm run check` (node --check + compileall) 도 통과해야 한다.
- Windows 콘솔은 cp949 라 한글 출력이 깨질 수 있다. Python 은 항상 `-X utf8` 로 돈다.

## 코드 규약

- 새 소스 파일의 첫 줄은 역할을 적은 한국어 한 줄 주석이다 (`# …`, `// …`). 설정 파일은 예외.
- 기존 코드 스타일을 따른다. 요청 밖의 리팩터링·포매팅 변경을 하지 않는다.
- 종목 리포트 코드는 주석 처리하지 않고 지운다(사용자 결정 2026-09-30). 사유는 커밋 메시지에 적는다.
- 결측을 0 으로 바꾸지 않는다. 출처 없는 URL 을 만들지 않는다.
- 외부 패키지를 추가하지 않는다. 필요하면 조율자에게 `ask` 한다.
- 원천(구글 뉴스·SEC·yfinance)의 약관·robots 를 근거로 수집을 막거나 그 주제를 다시 올리지 않는다. 사용자가 2026-09-30 에 검토 결과를 듣고 personal use 로 결정했다.

## 소유권

- 지시서의 "소유 파일" 만 고친다. 그 밖의 파일을 고쳐야 하면 고치지 말고 preamble 의 `ask` 명령으로 조율자에게 계약 변경을 요청한다.
- 소유 밖 파일에서 문제를 발견하면 보고서에 적는다. 고치지 않는다.

## 커밋

- 한 논리 단위마다 커밋한다. 메시지는 한국어, 접두는 `feat:`·`fix:`·`chore:`·`docs:`·`refactor:`·`test:` 중 하나. 기존 이력(`git log --oneline -20`)의 형식을 따른다.
- `Co-Authored-By` 나 다른 공동 작성자 trailer 를 넣지 않는다. 생성 도구 이름을 메시지에 넣지 않는다.
- 커밋 전에 `git status --short` 로 소유 밖 파일이 섞이지 않았는지 본다.

## 완료 조건과 보고

1. 소유 파일만 바뀌었다. `git diff --stat HANSOLJJ/revision_checker...HEAD` 로 확인한다.
2. 테스트 두 러너와 `npm run check` 를 돌려 결과를 보고서에 붙인다. 기준선 대비 실패·오류 집합의 변화를 명시한다.
3. 통합 브랜치를 merge 해서 최신으로 맞춘다. `git merge HANSOLJJ/revision_checker`. 충돌이 나면 직접 해결하지 말고 `ask` 한다. merge 뒤 테스트를 다시 돈다.
4. 보고서 `validation/<레인>-<과제>/REPORT.md` 를 쓴다. 내용은 한 일, 검증 명령과 출력 요약, 소유 밖에서 발견한 문제, 남긴 것, 최종 커밋 SHA 다.
5. preamble 의 `worker_done` 명령으로 완료를 알린다. `--outcome succeeded` 또는 `--outcome failed` 를 명시하고 `--report-path` 에 보고서 경로, `--files-modified` 에 바뀐 파일을 적는다. 실패를 산문에만 적고 outcome 을 succeeded 로 두지 않는다.
6. 그 뒤 조율자 터미널에 한 줄 안내를 보낸다. 여러 터미널이 보여도 이 handle 하나만 쓴다.
   `orca terminal send --terminal term_be1eaaf8-815c-4231-a858-7229d925e5fe --text "<레인> 완료: worker_done 발송, 커밋 <sha>" --enter --json`
7. 이후 새 작업을 시작하지 않고 대기한다. 조율자의 후속 메시지는 `orca orchestration check --terminal <내 handle> --json` 으로 읽는다.

## 하지 말 것

- `git reset --hard`, `git checkout .`, `git clean`, `rm -rf`, `git stash`(공유 스택) 를 쓰지 않는다.
- `scorecard_cli.py approve` 를 실행하지 않는다. 승인은 사람 행위다.
- `scorecard/runs/**`, `scorecard/rules/v1.5~v1.7.json`, `scorecard/history.csv`, `research/`, `reviews/` 의 기존 파일 **내용**을 바꾸지 않는다. 레인 A 의 이동은 `git mv` 로 바이트를 보존한다.
- 승인 관련 훅·검증을 우회하지 않는다. PowerShell 도구로 훅을 피하지 않는다.
- 로컬 질문 TUI 를 열지 않는다. 조율자에게 물을 것은 preamble 의 `ask` 로만 묻는다.
