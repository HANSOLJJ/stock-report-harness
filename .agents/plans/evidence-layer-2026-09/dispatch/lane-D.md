# 레인 D — 승인 페이지: `node server.js --approvals`

에이전트: Antigravity. 의존: `summary --json` 계약(아래에 고정). Python 쪽 명령(`summary`·`confirm`·`approve --via`·`revoke`)은 후속 과제 4.3 이 만든다. 이 레인은 가짜 CLI 로 개발하고 테스트한다. 공통 규약: `README.md` 를 먼저 읽는다.

## 배경

승인은 사람 행위다. 에이전트와 대화로 승인하지 않는다. 사람이 `node server.js --approvals` 로 서버를 띄우면 터미널에 6자리 일회용 코드가 찍히고, 브라우저 `http://127.0.0.1:3000/approve/<run_id>` 에서 실행 요약을 보고 근거를 확정하고 이름과 코드를 넣어 승인한다. **Node 는 화면과 라우팅만 한다.** 검증·지문·기록은 Python CLI 가 하고, 페이지는 그 명령을 자식 프로세스로 실행해 stdout 을 그대로 보여 준다.

## 소유 파일 (Ownership)

- 새 파일: `server/approvals.js`, `tests/node/approvals.test.js`, `tests/node/fake_scorecard_cli.js`, `tests/node/fixtures/summary.sample.json`
- 수정(최소): `server.js` 의 세 곳. (a) argv 파싱에서 `--approvals` 를 플래그로 읽고 `REQUESTED_REPORT` 후보에서 뺀다. (b) 요청 핸들러 첫 줄에 `if (approvals && approvals.handle(req, res)) return;`. (c) `server.listen` 콜백에서 승인 모드면 코드와 안내를 출력하고, 승인 모드일 때만 `127.0.0.1` 에 바인드한다. **그 밖의 함수(`findHtmlReports`, `safeResolve`, `normalizeRequestedReport`, `reportUrl`, MIME 표, 디렉터리 처리)는 레인 A 가 고치므로 건드리지 않는다.**
- 수정: `package.json` 의 `scripts` 에 `"test:node": "node --test \"tests/node/**/*.test.js\""` 한 줄 추가. (2026-09-30 질문 회신으로 확정. Windows 에서 npm 스크립트는 cmd.exe 로 돌아 디렉터리 인자가 MODULE_NOT_FOUND 를 내고 셸이 glob 을 펼치지 않으므로, 따옴표로 감싸 Node 가 직접 glob 을 해석하게 한다.)

만지지 않는 것: `scripts/**`, `tests/*.py`, `docs/**`, `.claude/**`, `.codex/**`.

## `summary --json` 계약 (4.3 이 이 형태를 낸다. 픽스처는 이 형태로 만든다)

```json
{ "run_id": "ai-scorecard-2026-11-x", "as_of": "2026-11-02", "rule_version": "v1.8",
  "companies": [{"company_id": "nvidia", "display_name": "NVIDIA",
                 "baseline": {"total": 9, "rank": 8}, "current": {"total": 10, "rank": 6},
                 "changed_factors": [{"factor": "F2", "from": 4, "to": 5}],
                 "carried_factors": ["F1", "F3"], "pending": ["F6: pending_rule_decision"]}],
  "review": {"status": "pass",
             "areas": [{"area": "fact-sources", "reviewer": "…", "result": "pass"}],
             "checklist_fail": 0},
  "evidence": {"candidates": 40, "selected": 12, "confirmed": 0,
               "items": [{"evidence_id": "EV-nvidia-001", "company_id": "nvidia", "factors": ["F2"],
                          "kind": "news", "title": "…", "url": "https://…",
                          "published_at_utc": "2026-10-30T12:00:00Z", "excerpt": "…", "status": "candidate"}]},
  "triggers": [{"trigger_id": "TRG-001", "company_id": "nvidia", "factors": ["F2"],
                "condition": "…", "deadline": "2027-02-01", "status": "watching"}],
  "pending_rule_decisions": ["C-03"],
  "hashes": {"rules": "…", "observations": "…", "judgments": "…", "run": "…", "results": "…", "draft": "…",
             "sources": "…", "evidence": "…", "triggers": "…"},
  "approval": {"exists": false, "valid": false, "approved_by": null, "approved_at": null} }
```

`hashes` 의 `sources`·`evidence`·`triggers` 는 없을 수 있다. 없는 키는 표시에서 뺀다. `review` 가 null 이면 "리뷰 없음" 으로 표시한다.

## CLI 호출 규약

- 기본 명령은 `uv run --frozen python -X utf8 scripts/scorecard_cli.py` 다. 환경변수 `SCORECARD_CLI` 가 있으면 그 문자열을 공백으로 나눠 대신 쓴다(테스트가 가짜 CLI 를 넣는다).
- 실행은 `child_process.execFile(cmd, [...args])` 로 하고 셸을 거치지 않는다. 인자는 배열로만 만든다.
- 하위 명령. `summary <run_id> --json` / `confirm <run_id> --evidence EV-…,EV-… [--reject EV-…,…]` / `approve <run_id> --by <이름> [--note <메모>] --via browser` / `revoke <run_id> --by <이름> --note <이유>`.
- `run_id` 는 `^[a-z0-9][a-z0-9-]{2,80}$` 만 허용한다. 아니면 400.
- stdout·stderr·exit code 를 그대로 페이지에 `<pre>` 로 보여 준다. Node 가 결과를 해석하거나 성공으로 꾸미지 않는다.

## 라우트

`server/approvals.js` 가 `createApprovals({ enabled, code, runCli, onApproved })` 로 객체를 만들고 `handle(req, res) -> boolean` 을 제공한다. 처리했으면 true.

- `--approvals` 없이 `/approve/…` 요청 → 404.
- 루프백이 아닌 `req.socket.remoteAddress`(`127.0.0.1`, `::1`, `::ffff:127.0.0.1` 밖) → 403.
- `GET /approve/<run_id>` → `summary --json` 실행 → HTML 페이지. CLI 실패면 500 과 stderr 표시.
- `POST /approve/<run_id>/confirm|approve|revoke` → 본문(`application/x-www-form-urlencoded`)의 `code` 가 서버 코드와 다르면 403 이고 CLI 를 부르지 않는다. 맞으면 해당 CLI 를 실행하고 결과 페이지(요약 다시 + `<pre>` 결과)를 낸다. `approve` 가 exit 0 이면 응답을 보낸 뒤 `onApproved()` 를 부른다. `server.js` 는 그 콜백에서 `server.close()` 하고 종료한다.
- 코드는 시작 시 `crypto.randomInt(0, 1e6)` 를 6자리로 채워 만들고 터미널에만 출력한다. 파일에 쓰지 않는다.

## 페이지

- 외부 리소스 없음(오프라인). 인라인 CSS. `lang="ko"`. 320px 폭에서 가로 스크롤 없이 읽힌다(표는 `overflow-x: auto` 래퍼 또는 카드형 접힘).
- 절 순서. (1) 실행 머리(run_id·as_of·rule_version·승인 상태). (2) 기업별 표(표시명, 기준선 점수·순위 → 이번 점수·순위, 바뀐 factor, 승계 factor, 미결). (3) 리뷰(상태, 4영역 결과, 체크리스트 fail 수). (4) 근거 후보 목록. 체크박스, `evidence_id`·기업·factor·kind·제목(링크는 `rel="noopener noreferrer"` 새 창)·발행시각·excerpt·status. 폼 하나로 "선택한 근거 확정" 과 "선택 제외". (5) 활성 트리거 표. (6) 미결 규칙 결정. (7) 지문(해시) 목록. (8) 승인 폼. 이름, 메모, 코드, "승인" 버튼. 승인이 이미 있으면 취소 폼(이름, 이유, 코드, "승인 취소").
- 투자 권유나 수익 관련 문구를 넣지 않는다. 문구는 한국어.
- `checklist_fail > 0` 이거나 `review.status !== "pass"` 면 승인 폼 위에 경고 문단을 보인다. 버튼은 막지 않는다. 막는 것은 Python 검증기다.
- 사용자 입력은 전부 HTML 이스케이프한다.

## 테스트 (`node --test tests/node/`)

- 포트는 0 으로 열어 임의 포트를 쓴다. 3000 을 점유하지 않는다.
- `fake_scorecard_cli.js`. `summary` 면 픽스처 JSON 을 출력한다. 그 밖은 받은 인자를 JSON 으로 stdout 에 찍고 exit 0. `FAKE_CLI_FAIL=1` 이면 exit 1 과 stderr.
- 승인 모드 꺼짐: `GET /approve/x` → 404.
- 승인 모드: `GET /approve/ai-scorecard-2026-09-obsreg` → 200, 본문에 기업 표시명·evidence_id·해시 일부가 있다.
- 잘못된 run_id(`../x`, 대문자, 빈 값) → 400.
- `POST …/approve` 코드 불일치 → 403, 가짜 CLI 가 호출되지 않는다.
- `POST …/approve` 코드 일치 → 200, 가짜 CLI 가 `approve <run_id> --by <이름> --via browser` 인자를 받았다(가짜 CLI 의 stdout 을 응답에서 확인). `onApproved` 가 한 번 불린다.
- `POST …/confirm` 이 `--evidence` 와 `--reject` 를 올바르게 만든다.
- 루프백 판별 함수 `isLoopback()` 단위 테스트.
- CLI 실패 시 500 과 stderr 표시.
- `node --check server.js` 와 `npm run check` 통과.

## 커밋

`feat(server): --approvals 승인 페이지와 일회용 코드` 하나. 본문에 "Node 는 화면만, 검증·지문·기록은 Python CLI" 와 "브라우저 도구를 가진 에이전트가 터미널 코드를 읽으면 누를 수 있다는 한계는 사용자가 알고 수용(2026-09-30)" 을 적는다.

## 검증 (Observable acceptance)

- `npm run test:node` 전부 통과. `npm run check` 통과. Python 테스트의 실패·오류 집합이 `baseline-failures.txt` 와 같다.
- `git diff --stat HANSOLJJ/revision_checker...HEAD` 가 소유 파일만 보인다. `server.js` 의 diff 는 argv 파싱·핸들러 첫 줄·listen 부근으로 30줄 이내다.
- 보고서 `validation/lane-D-approvals/REPORT.md` 에 수동 확인 결과를 적는다. 실제로 `SCORECARD_CLI="node tests/node/fake_scorecard_cli.js" node server.js --approvals` 를 띄워 페이지를 열고 코드 입력까지 해 본 결과다.
