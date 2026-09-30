# 레인 D 검증 보고서: 승인 페이지 (`node server.js --approvals`)

- 작업자: Antigravity (Lane-D Worker)
- 대상: `node server.js --approvals` 승인 모드 및 일회용 코드 기반 웹 승인 화면 구현
- 일자: 2026-09-30

## 1. 수행 작업 요약
1. **승인 코어 모듈 (`server/approvals.js`) 구현**:
   - `createApprovals({ enabled, code, runCli, onApproved })` 팩토리 및 `handle(req, res)` 라우터 구현.
   - 루프백 주소(`127.0.0.1`, `::1`, `::ffff:127.0.0.1`) 전용 403 차단 및 상위 경로 조작(`..`) 차단(400 Bad Request).
   - `child_process.execFile`을 통한 scorecard CLI 자식 프로세스 호출(셸 우회 방지).
   - 외부 리소스가 없는 인라인 CSS 오프라인 HTML 렌더러 구현 (모바일 320px 리플로우 지원, 지문 해시, 리뷰 결과, 근거 후보 확정/제외 폼, 실행 승인/취소 폼).
   - 승인 성공(`exit 0`) 시 `onApproved` 콜백 비동기 호출을 통한 서버 정상 종료 처리.
2. **`server.js` 최소 변경 (30줄 이내 요건 충족: 25줄 수정)**:
   - argv 파싱에서 `--approvals` 플래그 분리 및 `REQUESTED_REPORT` 후보 제외, 6자리 일회용 코드 생성 및 approvals 인스턴스 초기화.
   - 요청 핸들러 최상단에 `if (approvals && approvals.handle(req, res)) return;` 추가.
   - `server.listen`에서 승인 모드일 때만 `127.0.0.1` 바인드 및 터미널에 6자리 코드 및 URL 출력.
3. **가짜 CLI 및 테스트 픽스처 구현**:
   - `tests/node/fake_scorecard_cli.js`: `summary` 시 픽스처 반환, `confirm`/`approve`/`revoke` 시 인자 JSON 출력, `FAKE_CLI_FAIL=1` 시 오류 반환.
   - `tests/node/fixtures/summary.sample.json`: 지시서 계약과 일치하는 스키마 픽스처 생성.
4. **Node 단위 테스트 구현 (`tests/node/approvals.test.js`)**:
   - 루프백 판별(`isLoopback`), run_id 유효성 검사, 404/400/403/200/500 응답, 일회용 코드 검증, 인자 조립, `onApproved` 1회 호출 등 9개 테스트 케이스 구현.
5. **`package.json` 테스트 스크립트 추가**:
   - 조율자 승인 지침에 따라 Windows `cmd.exe`의 glob 미확장 문제를 방지하기 위해 `"test:node": "node --test \"tests/node/**/*.test.js\""` 로 설정 (sh/cmd 크로스 플랫폼 지원).

## 2. 검증 명령 및 결과

### 2.1 `npm run test:node`
```
> stock-report-harness@0.1.0 test:node
> node --test "tests/node/**/*.test.js"

✔ isLoopback() 단위 테스트 (0.5117ms)
✔ isValidRunId() 단위 테스트 (0.1265ms)
✔ 승인 모드 비활성화: GET /approve/<run_id> → 404 (17.9171ms)
✔ 잘못된 run_id: 400 Bad Request (6.2345ms)
✔ 승인 모드 활성화: GET /approve/<run_id> → 200 및 요약 필드 렌더링 확인 (43.6688ms)
✔ POST /approve: 코드 불일치 시 403 Forbidden 및 가짜 CLI 미호출 (2.5657ms)
✔ POST /approve: 코드 일치 시 200, 올바른 인자 전달, onApproved 1회 호출 (283.1963ms)
✔ POST /confirm: --evidence 와 --reject 를 올바르게 생성 (3.5099ms)
✔ CLI 실패 시 500 및 stderr 표시 (37.7006ms)
ℹ tests 9
ℹ suites 0
ℹ pass 9
ℹ fail 0
ℹ cancelled 0
ℹ skipped 0
ℹ todo 0
ℹ duration_ms 465.1656
```
결과: 9개 테스트 전체 통과.

### 2.2 `npm run check`
```
> stock-report-harness@0.1.0 check
> node --check server.js && uv run --frozen python -X utf8 -m compileall -q scripts
```
결과: 종료 코드 0 (정상 통과).

### 2.3 Python 테스트 기준선 검증
- 명령: `uv run --frozen python -X utf8 -m unittest discover -s tests -t .`
- 결과: `FAILED (failures=7, errors=30, skipped=5)` (757개 테스트 실행)
- `baseline-failures.txt`와 실패 7건 및 오류 30건 목록이 100% 동일함을 확인. 신규 회귀 없음.

### 2.4 수동 실기 검증 (`node server.js --approvals`)
- 명령: `SCORECARD_CLI="node tests/node/fake_scorecard_cli.js" node server.js --approvals`
- 검증 로그:
  1. 서버 기동:
     ```
     [승인 모드] 일회용 코드: 737726
     승인 페이지: http://127.0.0.1:3000/approve/<run_id>
     ```
  2. `GET http://127.0.0.1:3000/approve/ai-scorecard-2026-11-x`:
     - 응답: 200 OK, HTML 10,029 바이트 렌더링.
     - 기업명(NVIDIA), 근거 ID(EV-nvidia-001), 무결성 해시 정상 출력 확인.
  3. `POST http://127.0.0.1:3000/approve/ai-scorecard-2026-11-x/approve` (코드: 000000):
     - 응답: 403 Forbidden (잘못된 승인 코드 차단).
  4. `POST http://127.0.0.1:3000/approve/ai-scorecard-2026-11-x/approve` (코드: 737726):
     - 응답: 200 OK, HTML 10,626 바이트 (가짜 CLI 표준 출력에 `--by 홍길동 --via browser` 반영 확인).
  5. 서버 라이프사이클:
     - 콘솔에 `Approval confirmed. Shutting down server...` 출력 후 프로세스 정상 종료 (Exit code 0).

## 3. 소유 밖 파일 및 계약 변경 사항
- `package.json`의 `test:node`: Windows `cmd.exe` 환경에서 디렉터리 경로 직접 지정 시 발생하는 CJS loader 충돌(`MODULE_NOT_FOUND`)을 해결하고 크로스 플랫폼 호환성을 확보하기 위해 조율자 승인 하에 `node --test "tests/node/**/*.test.js"` 따옴표 glob 패턴으로 지정함.
- 그 외 소유 밖 파일(`scripts/**`, `tests/*.py`, `docs/**` 등)은 일절 변경하지 않음.

## 4. 남긴 것
- 남은 이슈 없음. 구현 및 검증 완료.
