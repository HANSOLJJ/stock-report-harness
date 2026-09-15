# 리뷰 3차 착수 — 04439f7 기준, 네 영역 새 세션

- 일시. 2026-09-15.
- 기준. worker `04439f7` (FIX-53 1~3단계 + 보완). results_hash `598055f51c4b02fe1e8bccb0e34f16d6a43ed12f5ed4aa429e874b5dca9db3f8` · draft_hash `2cbc0eac338ccf2bad8ed05f488279a6400177a82fa914923cf99f1843651709`.
- 보완 검토. 테스트 447 OK. results.json 을 `5990a0b` 와 대조해 전 칸 점수·상태·calc 차이 0, 입력 해시 run·judgments·rules 만 변경. 초안 활성 AWS 라벨 셋(397·417·1271행)에 정정 한 번씩, 취소선 408행 그대로. 불변 원천 triggers.json 은 건드리지 않고 규칙 `source_text_corrections` 와 스키마 검사로 렌더러가 덧붙임. **pass.**

## 리뷰 트리 준비

- 2차 part·판정은 `HANSOLJJ/review-obsreg-r2`(`dcfc3a9`)에 보존하고 `HANSOLJJ/review-obsreg` 를 `04439f7` 로 옮겼다.
- gitignore 입력 16개(plan·obsreg draft·companyfacts 원자료)를 worker 에서 복사, 바이트 해시 일치. obsreg draft sha256 = 템플릿 draft_hash.
- **리뷰 트리 줄끝 문제.** 옮긴 뒤 결과 해시 재계산이 `686cba53…` 로 어긋났다. 원인은 `sources.json` 을 포함한 추적 파일 10개의 작업 사본이 `.gitattributes` 이전에 받은 CRLF 로 남은 것이다. blob 이 바뀌지 않아 `reset --hard` 가 다시 쓰지 않았다. worker 트리에는 어긋난 파일이 0개다. 작업 사본을 지우고 다시 받아 재계산 `598055f5…` 일치를 확인했다. 저장소 결함은 아니고 **줄끝 규칙 추가 전에 만든 기존 checkout 을 이어 쓸 때의 함정**이다.
- 승인 baseline 테스트가 draft 해시 공란으로 실패했다. gitignore 대상 `drafts/ai-scorecard-2026-09-baseline.md` 가 없어서였고, 복사 후 `574841bc…` 로 승인값 일치. 최종 447건 중 442 통과, 5건은 빌드된 HTML 부재로 건너뜀(빌드 금지라 정상).

## 배정

| 영역 | 세션 | 비고 |
|---|---|---|
| A 사실·출처 | qwen3.8-max 새 대화 | |
| C 규칙 일관성 | codex gpt-5.6-sol 새 대화 | 끝나면 같은 창에서 B |
| D 출력·가독성 | Gemini 3.8 Flash 새 대화(C-13 창) | **첫 실행.** C-13 트리 사본을 근거로 쓰지 말라고 앞머리에 명시. 완결성은 조율자가 따로 본다 |
| B 재무 계산 | codex, C 뒤 새 대화 | |

프롬프트에 3차 변경 범위, 총점, `리뷰 범위 — 승계 판단 예외` 절 적용, UTF-8(BOM 없음), 기준 커밋과 테스트 상태를 넣었다.
