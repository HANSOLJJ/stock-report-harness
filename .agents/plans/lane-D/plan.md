# 레인 D — 승인 페이지 구현 계획

## 목적과 배경
- `node server.js --approvals` 플래그로 실행 시 승인 모드로 동작.
- 터미널에 6자리 일회용 코드를 출력하고 127.0.0.1(루프백) 접근만 허용.
- `GET /approve/<run_id>`에서 `summary --json` 실행 결과를 HTML로 렌더링.
- `POST /approve/<run_id>/confirm|approve|revoke`에서 코드 검증 후 Python CLI(`child_process.execFile`)를 실행하고 결과를 출력.
- Node는 UI/라우팅만 담당하며 검증·지문·기록은 Python CLI가 수행.
- 승인 성공(`approve` exit 0) 시 `onApproved` 콜백으로 서버를 안전하게 종료.

## 소유 파일 및 수정 범위
1. 신규 파일
   - `server/approvals.js`: 승인 라우터, 루프백 검사, CLI 실행기, HTML 렌더러
   - `tests/node/fixtures/summary.sample.json`: 지시서 17-38행의 `summary --json` 계약 픽스처
   - `tests/node/fake_scorecard_cli.js`: Node 단위 테스트용 모의 CLI
   - `tests/node/approvals.test.js`: Node 내장 테스트 러너(`node --test`) 기반 테스트 스위트
   - `validation/lane-D-approvals/REPORT.md`: 최종 검증 및 수동 테스트 보고서
2. 수정 파일
   - `server.js`: 세 곳(argv 파싱, 핸들러 첫 줄, listen 콜백) 30줄 이내 최소 변경
   - `package.json`: scripts에 `"test:node": "node --test tests/node/"` 추가

## 단계별 세부 계획
1. 계획, 체크리스트, 컨텍스트 노트 수립.
2. 픽스처 `summary.sample.json` 작성 (지시서 필드 일치 확인).
3. 가짜 CLI `fake_scorecard_cli.js` 구현 (summary 출력, confirm/approve/revoke 인자 반환, 오류 주입).
4. 승인 모듈 `server/approvals.js` 구현.
   - `isLoopback(ip)` 함수 (127.0.0.1, ::1, ::ffff:127.0.0.1 허용)
   - run_id 유효성 검증 (`^[a-z0-9][a-z0-9-]{2,80}$`)
   - CLI 실행기 (`SCORECARD_CLI` 환경변수 지원, `execFile` 사용)
   - HTML 렌더러 (외부 리소스 없는 인라인 CSS, 320px 리플로우, HTML 이스케이프)
   - `handle(req, res)` 라우터
5. `server.js` 최소 변경 및 `package.json` 스크립트 추가.
6. `tests/node/approvals.test.js` 작성 및 `npm run test:node` 검증.
7. `npm run check`, Python unittest, pytest 기준선 일치 검증.
8. 수동 서버 실행 및 기능 확인.
9. 통합 브랜치 병합 확인 후 커밋 1건 생성.
10. 보고서 작성 및 조율자 보고.
