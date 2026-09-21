# IMPL-46 검토 — 사용자 확정 4건 반영

- 검토일. 2026-09-14. 대상 worker `82d0aa8` + `bfb4fbd`. 판정 **pass.**
- 328건 직접 실행 OK · 순위 불변 · 승인 해시 변경(예상됨).

| 확정 | 반영 | 확인 |
|---|---|---|
| F6 정본 = parameters | `canonical_mode` 블록 (2026-09-14, 사용자). bands 는 구버전 표시 | ✓ |
| C-13 = reject_proxy | `resolved`. 옛 선택지 보존 | ✓ |
| F2 range [2,5] | 근거: 사다리 바닥 2 · 14개사 0·1 무발생. F3 전례 아님 | ✓ |
| 별표 G 조달 배제(A) | openai.F5 note. Amazon·SoftBank 남아 A=2 유지 — **점수 무영향** | ✓ |

## 부수 — oracle nonop_share 예외 해소

```
채점표 3-1a 각주 ᶜ   "세전($19.55B)이 영업이익($22.39B)보다 작다"
(19.55 − 22.39) / 19.55 = −0.145  ≈  저장값 −0.15
GAAP OperatingIncomeLoss 20,606 + 구조조정비 1,779 = 22,385
```

**원문이 조정 영업이익(구조조정 제외)을 썼고 엔진은 GAAP 를 쓴다. 엔진이 맞다.** 산식은 같고 입력 정의가 달랐다. 12/12 전부 설명됨. worker 가 `resolved 여도 alibaba(0.54 vs 0.6124)는 안 풀렸다` 를 warning 으로 남겼다 — 정직.

## ntm_per tsmc·alibaba

`source_vendor: author_computed` 로 분리, `vendor_value_rejected` 에 StockAnalysis 값(13.92)을 버린 이유(CNY/USD 혼재) 기재. NTM 의 ✱ 표식 발견과 일치.

## 다음

worker: main 머지 → F5-IMPL-48 → SRC-FLAG-49.
