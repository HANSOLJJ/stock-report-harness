# 리뷰 1차 판정 — needs_fix (A·C), 사용자 결정 2건, FIX-52 배정

- 일시. 2026-09-15. 기준 해시 results `cc696e35…` · draft `a19beb99…`.

## 1차 결과

| 영역 | 세션 | 결과 | 요지 |
|---|---|---|---|
| C 규칙 일관성 | codex gpt-5.6-sol high | needs_fix | fail 5 · 발견 13 · 미확인 3. **F7 범위 밖 점수 2건, run_rate 승격** |
| A 사실·출처 | qwen qwen3.8-max | needs_fix | verified 101건 전수 대조 **값 오류 0건**. 인용·출처 표기 결함, 초안 낡은 문장 |
| B 재무 계산 | — | 미실행 | 수정 후 처음 돈다 |
| D 출력·가독성 | — | 미실행 | 수정 후 처음 돈다 |

## 조율자 재검증 — 핵심 주장 전부 사실

C: F7 range `[-2,0]` vs nvidia·oracle `-3` · `arr` kind=run_rate 승격 · C-03 코드가 폐기 choice·삭제 키 참조 · C-12 `compute_private` 에 run 미전달 · 스키마 블록 삭제 통과(메모리 변조 셋 다 재현).
A: 판단 113/114 `SRC-v15-html` 단독 · apple `-26-000070` companyfacts 0건(실제 `-26-000020` 283건) · spacex `235805` 전무(`040364` 가 맞음) · run.json alibaba 가정문 낡음 · `_raw` gitignore.

## 사용자 결정 (2026-09-15)

1. **F7 — 매트릭스를 range 에 맞춘다.** `large|yes` -3→-2. nvidia 8→9, oracle 1→2. `large|no` 와 같아져 큰 쪽 세로축 변별력 손실 — 현재 해당 기업 없음을 규칙에 기록.
2. **anthropic 승격 — 진짜 ARR 만 인정.** `accepted_kinds: ["arr"]`. anthropic F6 -3→-4, 총점 11→10. **나는 Claude 이고 이 결정은 anthropic 점수를 내린다.** 발견은 codex(비 Claude)가 했다.

예상 총점: alphabet·amazon·meta 15 · microsoft 14 · tsmc 11 · anthropic·spacex-xai 10 · nvidia 9 · apple 8 · alibaba·palantir 6 · tesla 5 · openai·oracle 2.

## 내가 놓친 것 셋

- **F7 range.** F9 의 range/floor 불일치는 잡았는데 같은 재배분에서 F7 을 안 봤다.
- **C-03 코드.** C03-IMPL-43 을 pass 하며 규칙 등재만 보고 코드 경로를 안 봤다.
- **스키마 강제.** 금지어 **주입**만 시험하고 블록 **삭제**는 안 시험했다.

## 이관 운영 결함 — 다음 라운드 전에 고친다

리뷰 워크트리에 gitignore 대상이 안 따라온다. 1차에서 `drafts/`·`plan/` 누락(C 가 초안 대조 못 함, 복사로 해결), `validation/f6-avail-15/_raw/` 누락(A 가 C-13 브랜치 15b 로 우회). **2차 전에 셋 다 review-obsreg 로 복사하고 해시 대조.**

## 다음

worker FIX-52 → 새 해시 템플릿 → review-obsreg 를 새 커밋으로 이동 + 생성물·원자료 복사 → A·B·C·D 네 영역 새 대화로 재실행.
