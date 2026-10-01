# 채점표 하네스 운영 지침

## 목적
이 저장소는 AI 기업 9-factor 채점표를 재현 가능하게 계산하는 하네스이다.
원자료와 판단을 입력으로 받아 `plan → collect → research → calculate → draft → review → (사람) 승인 → build` 계약으로 처리하며, 점수는 규칙과 입력에서 프로그램이 산출한다.
승인은 사람이 승인 페이지에서 직접 하고, 승인 해시가 현재 입력과 다르면 build 는 멈춘다.

## AI Scorecard 계약 (report_type: ai_scorecard)
- 목적: AI 기업 9-factor 채점표를 같은 하네스 안에서 재현 가능하게 계산한다. 도메인 명세는 `docs/scorecard/design-guideline.md`, 구조 지침은 `docs/scorecard/structure.md`.
- 판별: `output/<run_id>/plan.md` frontmatter `report_type: ai_scorecard`, run_id(=slug)는 `ai-scorecard-` 접두.
- 단계 순서: `plan → collect → research → calculate → draft → review → (사람) 승인 → build`.
- 명령: `/score-plan`, `/score-add-company`, `/score-extend`, `/score-diff`, `/score-collect`, `/score-research`, `/score-calculate`, `/score-draft`, `/score-review`, `/score-approve`, `/score-build`, `/score-goal`. 실행기는 `uv run --frozen python -X utf8 scripts/scorecard_cli.py <stage> <run_id>`, 빌드는 `uv run --frozen python -X utf8 scripts/build_report.py <run_id>`. 새 실행은 `init --rule v1.8` 로 만든다. 인자는 `--help` 로 확인한다.
- 실행 하나의 산출물은 `output/<run_id>/` 한 폴더에 모인다. 파일은 `run.json observations.json judgments.json sources.json results.json approval.json plan.md research.md draft.md preview.md review.md review-parts/ evidence/{candidates.json,evidence.json} triggers.json report.html audit.md revocations.jsonl .lock` 이고, 경로 도우미는 `scripts/scorecard/paths.py` 이다. 수집한 원문 캐시는 `data/<company_id>/`(gitignore, `SCORECARD_DATA_ROOT` 로 바꿈)에 둔다.
- 공유 정의(rules, companies, baseline)와 `history.csv` 는 `scorecard/` 에 두고 추적한다. 실행 묶음의 md·html 은 생성물이며 손으로 고치지 않는다.
- 근거는 후보(`candidate`)로 들어오고 사람이 승인 페이지에서 확정(`confirmed`)한다. `status: new` 판단은 confirmed 근거만 인용한다. 트리거는 미래 점수를 저장하지 않는다(C-14). `not_disclosed`(발행사가 공시하지 않음을 확인)와 `unverified`(우리가 찾지 못함)를 섞지 않는다.
- 수집: `collect` 가 뉴스·공시·가격 후보를 모은다. 공시 수집에는 `SEC_UA` 가 필요하다(루트 `.env` 또는 환경변수, 사용자가 설정하며 영문으로 적는다). 가격은 `collect --kind prices` 가 yfinance 로 ⑥ `price`·`market_cap` 관측을 넣고 EPS·컨센서스는 받지 않는다. 종가가 NaN 이면 건너뛰고 직전 확정 종가를 쓰며, 가격 실패는 회사 단위다.
- 원자료·판단·규칙이 입력이고 점수는 결과다. 자동 산출 점수를 직접 수정하지 않는다. 모르는 값은 0으로 치환하지 않는다(unknown ≠ 0).
- 정성 판정(③ criteria, ⑤ A/H, ⑦ 매트릭스, ⑨ gate_inputs, ①④⑧ score)은 근거·검토자·검토일이 있어야 하고, 산식·사다리·구간 적용은 프로그램이 한다.
- 정성 판단을 고치는 길은 `scorecard_cli.py judge` 하나다(사람은 승인 페이지 8절에서, 에이전트는 판단 수정을 제안할 때 CLI 에서). F1·F4·F8 은 `score`, F3·F5·F7·F9 는 판정 재료 키(`criteria`·`grade`·`matrix`·`gate_inputs`)만 받고 점수 칸은 거부하며, F2·F6 은 대상이 아니다. 고치면 이전 값이 항목 안 `revision_history` 에 쌓이고 판단 해시가 바뀌므로 `research → calculate → draft → review` 를 다시 돌린 뒤 사람이 승인한다. 인자는 `--help` 로 확인한다.
- 미결 규칙 결정(C-03, C-05, C-06, C-13, C-16)은 `run.json.decisions` 로만 실행 단위에서 선택한다. 기본값을 조용히 채택하지 않으며 해당 기업은 순위에서 제외된다.
- 리뷰는 4 영역(사실·출처 / 재무 계산 / 규칙 일관성 / 출력·가독성) + 체크리스트 Q01~Q23. hero 이미지·뉴스 100건 요건은 적용하지 않는다.
- **리뷰 범위 — 승계 판단 예외.** 체크리스트 fail 의 사유가 `carried_score` 로 승계한 판단의 기존 논리이고, **이번 실행이 그 판단에 쓰인 잣대를 바꾸지 않았으며**, 규칙 파일 긴장 목록에 재검토 시점과 함께 등록됐다면 `status: pass` 를 막지 않는다. 리뷰 파일에 해당 fail 과 긴장 번호를 그대로 적는다. **이번 실행이 바꾼 잣대가 닿는 승계 판단은 이 예외가 아니다** — 한 회사에 새 잣대를 댔으면 같은 잣대가 닿는 모든 회사에 대야 한다(체크리스트 Q03). 2026-09-15 obsreg 2차 리뷰에서 A+2 엄격 읽기를 anthropic·openai 에만 대고 tsmc 에는 안 댄 것이 이 원칙으로 잡혔다.
- **리뷰 범위 — 기업 추가 실행의 축약.** 이전 실행을 이어받아(`init --from-run`) 기업만 더한 실행은 4 영역 리뷰를 **신규 기업과 잣대 일관성**으로 좁힌다. ① 신규 기업의 사실·출처·재무 계산·규칙 적용을 본다. ② 그 기업에 댄 잣대가 기존 기업에 댄 것과 같은지 본다(체크리스트 Q03 과 같은 원칙). **③ 기존 기업이 움직이지 않았다는 사실은 `uv run --frozen python -X utf8 scripts/scorecard_cli.py diff <run_id> --against <이전 run_id>` 의 출력으로 갈음하고 사람이 다시 읽지 않는다.** 그 명령은 입력 가법성(1층)과 점수 투영 불변(2층)을 기계로 판정하며, 위반이 하나라도 있으면 종료 코드 1 을 낸다. **1층·2층 위반이 있으면 이 축약을 쓸 수 없고 전체 리뷰로 돌아간다.** 조사 직후와 계산 직후에 각각 한 번씩 돌린다 — 1층은 조사 직후에, 2층은 계산 직후에 의미가 있다. subtree 해시 차이는 실패 조건이 아니다(기준일만 바꿔도 달라진다). 리뷰 파일에 `diff` 의 층별 결과와 신규 기업 목록을 그대로 옮긴다.
- 승인과 승인 취소는 사람 행위다. 사람이 `node server.js --approvals` 로 승인 페이지(`http://127.0.0.1:3000/approve/<run_id>`)를 띄우고, 터미널에 나온 6자리 일회용 코드로 근거 확정·승인·취소를 한다. 에이전트는 승인하지 않고 "승인 대기" 를 보고한다. 승인 해시(rules/observations/judgments/run/results/draft)가 현재와 다르면 build 는 `awaiting_user` 로 멈춘다.
- 상장사 ⑥은 v1.7 `parameters` 모드가 정본이다 — P1 TTM PER · P2 (시총−순현금)/매출 · P3 매출 성장 · P4 입력 신뢰도 보정. `bands` 모드(v1.5·v1.6, NTM PER 단일 구간표)는 구버전이며 실행 단위로만 선택한다. ⑨ G4 는 `coverage_comparable: yes` 일 때만 계산한다.
  <!-- 2026-09-14 전: "새 실행에서 상장사 ⑥은 NTM PER(4개 연속 미발표 분기 YYYYQn, 통화·주식 기준 일치)만 채점하고 근사치는 대기한다." — NTMPER-39 가 미발표 분기 컨센서스는 SEC 제출물에 구조적으로 없어 허용 원천으로 지킬 수 없는 계약임을 실증했고, 사용자가 parameters 를 정본으로 확정했다. -->
- 테스트: `uv run --frozen python -X utf8 -m unittest discover -s tests -t .`(T-01~T-12, R01~R06)와 `npm run test:node`. 코드 변경 후 반드시 실행한다.

## 금지·주의
- 임의 가격 데이터, 샘플링 차트, 조작한 기사 URL을 넣지 않는다.
- `browser-use`와 직접 LLM API 키 호출은 사용하지 않는다.
- 가격 데이터는 `yfinance`를 사용하고, 웹 리서치는 검증 가능한 출처나 Playwright MCP를 우선한다.
- `plan` 없이 `research` 를 실행하지 않는다. 근거가 필요한 실행은 `collect` 를 거친 뒤 `research` 로 간다.
- `review` 가 `pass` 가 아니면 `build` 를 실행하지 않는다. 승인 없이 `build` 하지 않는다.
- 에이전트는 승인과 승인 취소를 실행하지 않는다. 승인 페이지에 코드를 입력하지도 않는다.
- 근거 후보를 확정 근거처럼 인용하지 않는다. 새 판단은 사람이 확정한 근거만 인용한다.
- 훅·검증을 우회하지 않는다. 다른 소유자의 실행 잠금(`output/<run_id>/.lock`)은 이유 없이 `--take-lock` 으로 넘겨받지 않는다.

## 통제의 위치
- **통제는 코드가 한다.** 어느 하네스(Claude Code, Codex 등)로 돌리든 승인 해시 검증과 `scorecard.stages` 의 `approve`·`revoke` 함수 본체가 하는 거부(에이전트 세션이면 거부, CLI 든 import 든 같은 판정)가 첫 방어선이고, 훅(`scripts/hooks/guard.py`)은 둘째 방어선이다. 승인 있는 실행에 대한 `init --force` 도 에이전트 세션이면 `init_run` 이 거부하고 훅이 막는다. 훅이 통과시켰다고 검증이 끝난 것이 아니다.
- **훅은 도구 호출 밖을 막지 못한다.** 사람의 터미널에서 직접 실행하는 명령과 훅이 배선되지 않은 에이전트의 동작은 훅이 볼 수 없다. 훅 목록과 한계는 `scripts/hooks/README.md` 에 있다.
- **첫 방어선에도 한계가 있다.** 임의 Python 을 실행할 수 있는 에이전트가 작정하면 우회할 수 있다. 최종 보증은 사람이 git 이력에서 승인 파일의 변경을 확인하는 것이다.
- **승인 서버가 떠 있는 동안에는 열린 틈이 있다.** 브라우저 도구를 가진 에이전트가 터미널에 나온 6자리 코드를 읽으면 승인 페이지에서 승인을 누를 수 있다. 코드는 파일에 쓰이지 않고, 서버는 승인이 성공하면 내려간다. 사용자가 이 사실을 알고 수용했다(2026-09-30). 에이전트는 그 코드를 읽어 입력하지 않는다.

## Orca worktree 간 메시지와 작업 실행
- 이 규칙은 프로젝트의 모든 worktree와 에이전트에 적용한다. 새 worktree 생성 또는 기존 worktree 작업 시작 시 이 절이 있는지 확인하고, 오래된 분기에서 누락됐으면 원본 저장소의 공통 규칙을 반영한다. 실행 중인 에이전트에는 갱신된 AGENTS.md를 읽도록 터미널로 안내한다.
- 다른 worktree에 신규 작업·보완·재검증 등 추가 실행을 요청할 때는 **메시지 발송과 터미널 실행 안내를 반드시 함께 수행한다.** `orca orchestration send/reply`로 수신함에 저장한 것만으로 요청 처리를 끝내지 않는다.
- 메시지 발송 후 수신 에이전트의 현재 terminal handle과 입력 상태를 확인하고, `orca terminal send --terminal <handle> --text "<메시지 ID와 수신함 확인·작업 실행 안내>" --enter --json`으로 실행 안내를 제출한다. 기존 입력이나 진행 중인 작업을 지우거나 중단하지 않는다.
- 실행 안내에는 확인할 메시지 ID, 해야 할 작업, 수신 확인 및 완료 회신 방법을 포함한다. 최초 제출이 처리됐는지 확인하고, 이미 처리 중인 동일 요청은 중복 제출하지 않는다.
- **발송 성공·수신 확인·작업 착수·완료는 별개 상태다.** 도구의 `accepted: true`만으로 수신·착수·완료를 주장하지 않는다. 수신 확인 회신이 오면 사용자에게 알린다.
- 상대 CLI가 실행 승인이나 인증을 기다리면 해당 상태와 필요한 조치를 사용자에게 알린다. 메시지를 보냈다는 이유로 실행 중이라고 보고하지 않는다.
- **완료 보고 뒤 수신자의 검토·재검증·통합·다음 작업이 필요하면 완료 회신도 추가 실행 요청이다.** 발신자는 완료 메시지에 다음 담당자와 할 일을 적고, 해당 담당자의 현재 터미널에 메시지 ID와 실행 안내를 반드시 제출한다. 수신함 알림만으로 다음 담당자가 자동 실행된다고 가정하지 않는다.
- **작업을 요청하는 쪽이 지시서 끝에 자기 회신용 terminal handle을 적는다.** 받는 쪽이 `orca terminal list`로 찾게 하지 않는다. 한 worktree에 터미널이 둘 이상(예: claude와 codex)이면 어느 쪽이 담당자인지 목록만으로는 가릴 수 없고, 못 찾으면 터미널 안내가 조용히 생략된다. 2026-09-14에 완료 회신 네 건이 수신함에만 남아 조율자가 모른 채 워커가 놀았고, 원인이 그것이었다.
- **한 과제의 끝은 세 단계다** — 커밋 → `orca orchestration send`(본문) → `orca terminal send`(한두 줄 안내). 둘째까지만 하면 상대가 모른다. 터미널 안내 본문은 짧게 쓰고 전문은 수신함에 둔다.
- **AGENTS.md는 `main`에서만 고친다.** 각 worktree는 `git merge main`으로 받아온다. worktree마다 같은 수정을 따로 적용하지 않는다 — 그렇게 하면 같은 커밋이 브랜치 수만큼 다른 SHA로 생기고 파일이 갈라진다. 2026-09-11에 `docs: Review 계약 제목 오타 복구` 한 줄이 다섯 브랜치에 따로 존재하고 AGENTS.md가 세 버전으로 갈라진 것이 확인됐다.
- 작업 시작 전 `git log --oneline <branch>..main`으로 뒤처진 커밋이 있는지 확인한다. 있으면 머지부터 한다. 규칙만이 아니라 버그 수정도 거기 있다.
- `main` 머지 후 실행 중인 에이전트에는 메시지와 터미널 안내로 AGENTS.md 재읽기를 요청한다. 재읽기 확인 회신을 받아야 적용 확인으로 처리한다. 재시작은 필요하지 않으며 기존 작업과 입력을 보존한다.
- 단순 수신 확인이나 후속 작업이 전혀 없는 결과 공유만 터미널 실행 안내 대상에서 제외한다. 재읽기 확인 회신에는 다시 실행 안내를 보내지 않아 알림 순환을 방지한다.

## 원자료 조사 규율

모든 worktree의 조사·검증 작업에 적용한다. 지시서에 매번 적지 않아도 기본값이다.

- **밖에서 찾기 전에 저장소 안을 먼저 본다.** 보존된 원자료·이전 과제의 `_raw`·프로젝트 내 원본 문서를 먼저 연다. 2026-09-11에 "없다"고 적힌 값이 이미 저장소 안에 있던 사례가 세 번 나왔다.
- **출처가 여러 파일이면 전부 연다.** 값과 그 값을 소비하는 규칙이 다른 파일에 있을 수 있다.
- **값·문언·인용 위치를 셋 다 확인한다.** 연도 칸, 주석 번호, 페이지를 원문에서 그 번호로 실제 찾아지는지 본다. 값이 맞아도 위치가 틀리면 다음 사람이 그 자리에서 아무것도 못 찾는다.
- **재무표는 열 머리글에서 축을 먼저 확정한다.** 최신이 맨 왼쪽이라고 가정하지 않는다. 오름차순 표가 흔하다.
- **같은 제출본 안에서 수치가 갈리면 감사 재무제표 본문을 우선한다.** MD&A·서술부는 반올림하거나 다른 기준을 쓸 수 있다.
- **발행사가 준 두 번째 칸을 체크섬으로 쓴다.** 20-F의 편의환산 USD 칸처럼 같은 값의 다른 표현이 있으면 선언 환율로 역검산한다. 줄을 놓치면 합계가 안 맞아 드러난다.
- **없는 것은 세 갈래로 구분한다.** 회사가 공시하지 않았다 / 우리가 못 찾았다 / 어느 쪽인지 모르겠다. 마지막을 첫째로 승격하지 않는다.
- **값이 없으면 같은 원문에서 "왜 없는지"를 한 번 더 검색한다.** 회계정책 면제 선언 같은 근거가 같은 문서에 있을 수 있다.
- **0이 나오면 부재인지 탐색 실패인지 가른다.** 고정 후보 목록으로 태그를 찾으면 체계가 다른 발행사가 0으로 나온다.
- **결측을 0으로 반환하지 않는다.** 0은 유효한 값처럼 보여 결측이라는 사실이 사라진다.
- **기존 점수·파생값을 정답 fixture로 쓰지 않는다.** 어긋나면 어긋난 대로 보고한다.
- **범위를 한 값으로 좁히거나 갈린 것을 고를 때는 좁혔다는 사실과 근거를 함께 남긴다.**
- **보고서의 모든 단정을 자기 산출물과 역추적 대조한다.** 산출은 맞는데 요약이 그것과 어긋나는 일이 있다.
- **한 곳에서 확정한 정의를 같은 이름이라는 이유로 다른 소비자에 옮기지 않는다.** 같은 단어가 자리마다 다른 것을 가리킬 수 있다.

## Memory System
- 반복 실패 방지를 위해 `docs/memory-system.md` 규칙을 따른다.
- 실패/재시도 비용이 큰 관측은 `memory/_daily/YYYY-MM-DD.md`에 append한다.
- 같은 패턴 3회 이상 또는 재발 비용이 큰 실패는 `memory/topics/{slug}.md`로 추출한다.
- memory 변경 후 `uv run --frozen python -X utf8 scripts/validate_memory.py`를 실행한다.
- 지금 실재하는 topic 파일은 `memory/topics/guardrails.md` 하나다. 아래 목록은 주입 훅이 찾는 topic 이름이고, 없는 파일은 관측이 생길 때 만든다.
- 작업 시작 시 관련 topic만 읽는다: 시간/yfinance=`time-sync`, 외부 API=`external-api`, 이미지=`image-workflow`, 단계 순서=`pipeline-order`, 빌드=`build-errors`, git=`git-workflow`, hook/validator=`guardrails`.
