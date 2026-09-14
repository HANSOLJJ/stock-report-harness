# F5-IMPL-48 검토 — anthropic·openai A +2→+1 반영

- 검토일. 2026-09-14. 대상 worker `5bfd6e9`(+ `5209311` · `8e3af1d`). 판정 **pass.**

```
338건 OK · behind main 0
anthropic  F5 5→4 (A 2→1, H 0)    총점 12→11   tsmc 와 공동 5위
openai     F5 2→1 (A 2→1, H -3)   총점  3→2    13위
나머지 12개사 불변 — 사전 시뮬레이션과 정확히 일치
```

판단 파일: 검토자 `설계진행(C-13 A-GRADE-45 · NTM A-GRADE-45B 독립 일치)` · 2026-09-14 · 근거 행 727/188~195/262~266/288·276/759 · 옛 판단 `superseded` 보존 · status `carried_score`→`ok`.

## 5209311 — 스스로 잡은 것, 그리고 그 아래

bfb4fbd 가 **LF 바이트로 rule_hash 를 고정하고 재계산을 안 돌렸다.** worker 가 되잡았다. 그런데 사고가 가능한 구조가 남는다 — 해시가 파일 바이트에 걸리고 Windows git 이 LF↔CRLF 를 만진다(세션 내내 경고). **내용 불변이어도 줄바꿈이 바뀌면 해시가 갈리고 승인이 멈춘다.** approval 정책 note + 다음 손볼 때 정규화 검토 항목으로 남기게 했다.

## 미결 7건 — 전부 처리됨

```
C-03 확정(혼합 모델)     C-04 이미 구현     C-07 이미 구현
C-08 A 반영 · B 반영(이 건)   C-09 승계 유지+경고   C-11 IMPL-50   C-13 reject_proxy
```

## 남은 큐

worker `SRC-FLAG-49` → `IMPL-50`. 둘 다 점수 무영향.
