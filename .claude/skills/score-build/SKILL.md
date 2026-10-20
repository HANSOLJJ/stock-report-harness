---
name: score-build
description: 확인된 scorecard 실행을 단일 파일 대시보드 HTML(output/<run_id>/report.html)과 scorecard/history.csv 로 빌드한다. 확인 페이지에서 확인하면 곧바로 돌고, 확인된 실행을 다시 빌드할 때 /score-build <run_id> 로 쓴다.
---

# 채점 빌드 스킬

## 절차

1. `uv run --frozen python -X utf8 scripts/build_report.py <run_id>` 를 실행한다. 빌더가 report_type 으로 분기해 확인 기록 해시를 검증하고 `output/<run_id>/report.html`, `output/<run_id>/audit.md`, `scorecard/history.csv` 를 만든 뒤 사후 검증을 돌린다.
   - `awaiting_user` 메시지가 나오면 확인이 없거나 무효다. 에이전트가 확인하지 않는다. 사용자에게 확인 페이지(`node server.js --approvals` 후 `http://127.0.0.1:3000/approve/<run_id>`)에서 확인하도록 안내하고 멈춘다. 확인하면 빌드는 곧바로 돈다. 초안 해시만 다른 경우는 확인이 유지돼 이 메시지가 나오지 않는다.
2. `uv run --frozen python -X utf8 scripts/validate_report_contract.py <run_id> --require-html` 결과를 확인한다.
3. `node server.js` 로 미리보기를 띄우고 URL 을 안내한다. 미리보기 주소는 `http://localhost:3000/<run_id>/report.html` 이다.
   - 포트 3000 이 이미 쓰이고 있으면 기존 프로세스를 죽이지 않는다. `PORT=<빈 포트>` 환경변수로 다른 포트에 띄우고 그 포트로 URL 을 안내한다.
4. 가능하면 Playwright 로 320/768/1280 폭에서 가로 넘침·탭 대상·순위표 모바일 열·행 탭 동작을 실측한다(dashboard-design 스킬 검증 절).

## 제약

- HTML 을 손으로 쓰거나 고치지 않는다. 렌더러(`scripts/scorecard/render_html.py`)를 고치고 다시 빌드한다.
- 빌드 중 새 가격·근거를 수집하지 않는다. 확인된 입력에서만 생성한다.

## 완료 보고

HTML 경로, audit 경로, history.csv 추가 행 수, 검증 결과, 미리보기 URL.
