# 레인 D — 컨텍스트 노트 및 결정 기록

## 초기 결정 사항 (2026-09-30)
1. Python 실행 규칙.
   - 기본 CLI 실행은 `uv run --frozen python -X utf8 scripts/scorecard_cli.py` 배열로 실행.
   - 환경변수 `SCORECARD_CLI`가 주어지면 공백으로 split하여 실행 인자로 사용.
   - 모든 CLI 호출은 `child_process.execFile`을 사용하며 셸(`shell: true`)을 통하지 않음.
2. 루프백 판별 (`isLoopback`).
   - `127.0.0.1`, `::1`, `::ffff:127.0.0.1` 및 `localhost` 유래 로컬 소켓 주소 허용.
   - 루프백 이외의 접근은 403 Forbidden 응답.
3. 승인 모드 및 종료 라이프사이클.
   - `--approvals`가 없을 때 `/approve/` 요청은 404 Not Found.
   - `approve` 명령 성공(exit 0) 시 클라이언트에 결과를 전송한 뒤 `onApproved` 콜백을 호출하여 서버 종료 처리.
4. UI 및 렌더링 규칙.
   - 외부 CDN/리소스 금지(인라인 스타일만 사용).
   - 모든 사용자 입력 및 동적 데이터는 HTML 이스케이프 적용.
   - 모바일 320px 리플로우 지원 (`overflow-x: auto`, 반응형 카드/테이블 레이아웃).
   - 투자 권유나 수익 관련 문구 배제.
