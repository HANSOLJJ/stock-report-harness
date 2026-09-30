# 결정 기록 — 근거 수집 계층 도입

한 결정 = 한 항목. 날짜·결정·이유·영향 순.

## 2026-09-30

- **대상은 채점표만, 종목 리포트는 폐기.** 사용자: "종목 리포트는 딱히 필요 없어 채점표가 중요한거임". 영향: stock-* 스킬·산출물·공유 스크립트의 종목 코드 약 1,200줄 삭제.
- **작업 위치는 이 워크트리(HANSOLJJ/revision_checker).** 워크트리가 2026-08-26 커밋 0df7d6e 에서 생성돼 채점표가 없었음. 원인은 GitHub origin/main 이 그 커밋에 멈춰 있었기 때문. 로컬 main 을 fork(HANSOLJJ)에 push 하고 이 워크트리를 ff-merge 로 b07334a 에 맞춤. origin 은 fork, upstream 은 원작자(wnghdcjfe, push 권한 없음)로 재설정.
- **uv 로 Python 환경 통일.** 시스템 python3/python 혼용과 cp949 출력 깨짐이 원인. 훅 논리도 4단계에서 guard.py 로 모으고 모든 배선을 `uv run --frozen python -X utf8` 한 줄로.
- **첫 원천: Google News RSS + SEC EDGAR + yfinance 가격.** yfinance 는 ⑥ price·market_cap 관측 전용(handoff 정책 4). 종목 차트용 yfinance 코드는 삭제.
- **원천 allowlist 폐지(규칙 v1.8).** 구글 뉴스 robots(/rss 차단)·일반 약관(robots 위반 자동 접근을 남용으로 정의)·뉴스 약관(개인 피드 리더 허용) 검토 결과를 보고 사용자가 "personal use 이니 허용 관련 규칙 전부 제거" 결정. nasdaq.com·Yahoo 배제도 함께 사라짐. 수집기는 식별 UA·낮은 빈도·본문 미수집을 코드 상수로 유지. 이 주제를 사용자에게 다시 올리지 않는다(guardrails ENTRY-004).
- **수집 키는 company_id.** 비상장 2사(anthropic, openai)에 티커가 없고 TSMC·Alibaba·Alphabet 은 티커가 여럿. 채점표 관측·판단·해시가 이미 company_id 로 묶여 있음.
- **실행 묶음은 output/<run_id>/, 수집 데이터는 data/<company_id>/.** 사용자가 "최종 결과 묶음에 다 넣자" 제안. output 은 종목 시절부터 최종 결과 자리. 기존 실행 2개도 새 양식으로 이동(과거 이력). 이동 시 .gitattributes CRLF 고정과 frontmatter 옛 경로 문자열 허용이 필요.
- **git 추적: 묶음의 텍스트·JSON·HTML 전부.** 승인 해시가 가리키는 draft 가 git 밖에 있던 문제 해소.
- **종목 코드는 삭제.** 9월 7일 "주석 처리" 규칙은 살아 있는 기능의 계약 변경에 적용하는 것으로 범위를 좁힘. 사유는 커밋 메시지에.
- **승인 UX는 브라우저 페이지(방식 2).** `node server.js --approvals` 로 사람이 띄운 서버만 승인 라우트를 열고 일회용 코드를 터미널에 찍음. Node 는 화면만, 판단·지문은 Python CLI. 브라우저 도구를 가진 에이전트가 누를 수 있는 위험은 사용자가 알고 수용.
- **에이전트 배정.** Codex 토큰 소진으로 제외. 복잡 = Opus 5.5, 단순 = Sonnet 5.5, 중간 = Antigravity·Muse, 최종 검증·조율 = Fable(이 세션). Antigravity 에는 판단 과제를 주지 않음.
- **훅 재사용.** enforce-citations 만 종목 전용이라 삭제. 나머지는 guard.py 로 이식하며 경로만 묶음으로. remind-review 는 조율자·워커 구조에서 워커 턴 종료를 잘못 막으므로 경고로 바꿈.
- **memory validator 수정은 형식만.** 2026-09-11 일지와 guardrails ENTRY-002~004 의 내용은 그대로 두고 헤더·절 구조만 스키마에 맞춤.
- **워커는 Orca orchestration 의 `worker-start --worktree new-child` 로 띄운다.** 통합 브랜치 `HANSOLJJ/revision_checker` 에서 자식 워크트리를 만들고 레인마다 한 에이전트. 네 레인이 파일을 지우고 커밋하므로 한 checkout 공유는 위험. 완료 신호는 preamble 의 `worker_done` 이고, 덧붙여 조율자 터미널(`term_be1eaaf8-…`)에 한 줄 안내(AGENTS.md 3단계 완료 규칙).
- **`.agents/plans/` 만 추적으로 전환.** `.gitignore` 의 `.agents/` 가 계획·체크리스트·지시서를 무시해 새 워크트리에 지시서가 들어가지 않았다. `.agents/*` + `!.agents/plans/` 로 바꿈. `.agents/skills`(종목, 삭제 예정)는 계속 무시.
- **레인 B 의 `resolve_cik` 는 모듈만, CLI 서브커맨드와 `--apply` 는 3.1·3.4 로.** `scorecard_cli.py` 는 레인 A 가 만지고, `companies.json` 에 `cik` 를 넣으면 엄격 스키마(`_expect_keys`)가 3.1 전까지 거부한다. 충돌·검증 실패를 피하려고 경계를 이렇게 그음.
- **레인 D 는 `server/approvals.js` 새 모듈 + `server.js` 최소 삽입(argv·핸들러 첫 줄·listen).** 레인 A 가 같은 파일의 경로 함수를 고치므로 영역을 함수 단위로 갈랐다. Python `summary` 가 아직 없으니 `SCORECARD_CLI` 환경변수로 가짜 CLI 를 주입해 개발·테스트.
- **`docs/output-spec.md` 삭제는 조율자가 레인 C 병합 뒤 직접.** 현재 protect-sensitive-files 훅이 그 경로를 보호해 워커의 `git rm` 이 막힌다. 훅이 guard.py 로 바뀌고 보호 목록에서 빠진 뒤 지운다.
- **approval.json·이동 실행 폴더·규칙 파일 보호는 4.2(A 병합 뒤)로 미룸.** 레인 C 가 지금 넣으면, C 가 먼저 병합될 경우 레인 A 의 `git mv scorecard/runs/… output/…` 와 draft 복사가 새 훅에 막힌다. remind-review 경고화와 output-spec 보호 해제는 사양이 고정돼 C 에 포함.
- **SEC 픽스처는 `SEC_UA` 가 있을 때만 실조회.** SEC 는 이름·연락처가 든 User-Agent 를 요구하고 그 값은 사용자가 준다(저장소에 넣지 않음). 없으면 문서 형식대로 합성 픽스처를 만들고 README 에 합성이라 적는다. 구글 RSS·yfinance 는 1회 실조회로 픽스처를 만든다.
- **워커는 통합 브랜치 merge 를 못 한다.** S·C 모두 `git merge HANSOLJJ/revision_checker` 가 권한 분류기에 거부됐다. 워커 브랜치가 통합 브랜치 뒤에 있어도 조율자가 `--no-ff` 로 병합하고 병합 뒤 전체 테스트를 다시 돈다. 레인 A 지시에도 "거부되면 우회하지 말고 보고" 를 넣었다.
- **레인 D 의 `.agents/plans/lane-D/` 3개는 병합에서 뺐다.** 글로벌 규칙 7 에 따라 워커가 자기 계획 파일을 만들었지만 소유 밖이고 통합 계획과 겹친다. 브랜치에는 남아 있다.
- **baseline recompute 불일치는 기존 상태로 판정.** 원본 폴더에서도 저장 results_hash 0942c342… 와 재계산 200d7b01… 가 다르다. 총점·입력 해시는 같고 F9 calc 경로 기록만 다르다. 승인 뒤 엔진이 바뀐 결과라 이번 과제에서 고치지 않고, 레인 A 의 완료 조건을 "이동 전후 같은 값" 으로 바꿨다. approval_valid 는 저장 파일 바이트 기준이라 여전히 필수.
- **가격 수집기의 시점 결함은 병합을 막지 않았다.** vendor market_cap 이 조회 시점 값인데 종가 날짜로 기록되는 문제는 아직 이 값을 읽는 코드가 없어서 3.4 에서 고친다.
- **레인 B 가 공유 stash 스택을 썼다.** `git stash -u` 를 한 번 쓰고 즉시 pop 했다고 보고했고, 조율자가 `git stash list` 가 비어 있음을 확인했다.
- **승인 해시 비교는 `stages.approval_mismatches` 하나로 모은다.** 레인 E 가 발견했다. `render_html.build_scorecard` 와 `compare.approval_state` 가 승인 해시를 dict 전체로 비교해서, 현재 해시에 sources·evidence·triggers 키가 늘면 6키로 승인된 기존 두 실행이 재빌드·diff 에서 무효가 된다. 규칙은 "승인에 있는 키만 대조, 현재에 evidence·triggers 가 있는데 승인에 없으면 불일치, sources 는 승인에 있을 때만 대조". 레인 E 소유를 두 호출부까지 넓혔고 dict 등호 비교 0건을 grep 테스트로 고정한다.
- **레인 A 는 draft 줄끝을 먼저 판정.** obsreg draft 가 renderer 산출물이라 LF 로 알려져 있지만 확인하지 않았다. approval.json 의 draft 해시와 바이트를 대조해 `.gitattributes` 예외를 정한다. baseline 은 CRLF 예외 유지.
