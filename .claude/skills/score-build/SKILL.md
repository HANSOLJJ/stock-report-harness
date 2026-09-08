---
name: score-build
description: 승인된 scorecard 실행을 단일 파일 대시보드 HTML(output/<slug>.html)과 scorecard/history.csv 로 빌드한다. /score-approve 뒤 /score-build <slug> 로 사용한다.
---

# 채점 빌드 스킬

## 절차

1. `python scripts/build_report.py <slug>` 를 실행한다. 빌더가 report_type 으로 분기해 승인 해시를 검증하고 HTML·history.csv 를 만든 뒤 사후 검증을 돌린다.
   - `awaiting_user` 메시지가 나오면 승인이 없거나 무효다. 사용자에게 `/score-approve <slug>` 를 요청한다.
2. `python scripts/validate_report_contract.py <slug> --require-html` 결과를 확인한다.
3. `node server.js <slug>` 로 미리보기 URL 을 안내한다.
4. 가능하면 Playwright 로 320/768/1280 폭에서 가로 넘침·탭 대상·순위표 모바일 열·행 탭 동작을 실측한다(dashboard-design 스킬 검증 절).

## 제약

- HTML 을 손으로 쓰거나 고치지 않는다. 렌더러(`scripts/scorecard/render_html.py`)를 고치고 다시 빌드한다.
- 빌드 중 새 가격·근거를 수집하지 않는다. 승인된 입력에서만 생성한다.

## 완료 보고

HTML 경로, history.csv 추가 행 수, 검증 결과, 미리보기 URL.
