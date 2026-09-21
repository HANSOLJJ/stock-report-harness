---
name: score-extend
description: 이전 실행의 입력을 이어받아 새 기업을 추가하는 채점 실행을 생성한다. /score-extend <새 slug> --from-run <이전 slug> --add-companies a,b 처럼 사용한다.
---

# 기업 추가 실행 생성 스킬

이전 실행의 관측·판단·출처를 계승하고 새 기업을 추가하여 새 실행 디렉터리를 초기화한다.

## 절차

1. 이어받을 이전 실행(`--from-run`)과 더할 기업(`--add-companies`)을 확인한다.
2. slug 는 `ai-scorecard-<YYYY-MM>-<label>` 형식으로 정한다 (예: `ai-scorecard-2026-09-extend`).
3. 실행한다:
   ```
   python scripts/scorecard_cli.py init <새 slug> --from-run <이전 slug> [--add-companies a,b] [--as-of <YYYY-MM-DD>] [--title "<제목>"] [--purpose "..."]
   ```
4. 여기서 멈춘다 (research 로 진행하지 않는다).

## 제약

- slug 는 `ai-scorecard-<YYYY-MM>-<label>` 형식이다.
- 이어받은 관측·판단은 이번 실행에서 재검증되지 않았다. 그 사실이 `assumptions` 에 적힌다.
- 새로 조사할 대상은 더한 기업뿐이다. 기존 기업의 관측·판단을 고치면 `diff` 가 위반으로 잡는다.
- `--add-companies` 는 덧붙이기이고 `--companies` 는 통째 교체다. 헷갈리지 말 것.

## 완료 보고

새 실행 경로, 이어받은 관측·판단·출처 건수, 더한 기업, 다음 명령 `/score-research <slug>`.
