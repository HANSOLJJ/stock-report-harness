# 리뷰 2차 A 사실·출처 판정 — 점수 무영향 16건, nvidia F2 는 긴장

- 일시. 2026-09-15. 리뷰어 qwen 새 세션, part `review-obsreg` 커밋 `dcfc3a9`. 기준 해시 results `5e8ce6fc…` · draft `931f5632…` (2차 템플릿 `8305d8a`).
- 판정. **needs_fix.** 체크리스트 Q05·Q09 fail.
- 반영. worker FIX-53 3단계로 발송(2026-09-15). 반영 뒤 템플릿 재생성, 3차 리뷰 기준.

## 분류

| 발견 | 심각도 | 성격 | 처리 |
|---|---|---|---|
| 초안 anthropic ⑧ DS투자증권 | high | 렌더러 | **1단계(RC-06)로 이미 해소** |
| 재무 표 부외 칸이 legacy `offbalance_note` (amazon `미개시 리스 $106B`, 엔진은 verified 267,279M) | high | 렌더러 | 3단계 §1 |
| v1.5 서술 절의 대체된 수치가 표시 없이 남음 (amazon ⑨ 게이트 4) | medium | 렌더러 | 3단계 §1 |
| alibaba contracted_revenue note — 면제 문면은 두 갈래(≤1년·right-to-invoice)뿐인데 "찾아도 없을 것이 선언" 으로 적음 | high | 이번 실행 관측 설명 | 3단계 §2. 분류 `not_disclosed_confirmed` 유지, 근거 문장만 교체 (C-16 강등이 이 문장 위에 선다) |
| spacex-xai pretax_income_ttm 미등록 · nonop_share 사유 불일치 | medium | 이번 실행 관측 | 3단계 §2. TTM -7,623M, 세금 595M 으로 순이익 -8,218M 과 닫힘. P4 short_history 로 점수 불변 |
| spacex-xai cash basis 필드 (시장성 증권 0 → 6,487M 등) | medium | 이번 실행 관측 | 3단계 §2. 등록값 93,522M 은 맞음 |
| anthropic cumulative_raised straddle_note 가 FIX-52 이전 서술 | medium | 이번 실행 관측 | 3단계 §2. 세 시나리오 모두 -4 |
| oracle net_cash 605M 이중 태깅 설명 | low | 이번 실행 관측 | 3단계 §2. 값 불변 |
| spacex-xai revenue_ttm 가 분기 | low | 명명 | 3단계 §2. P2 미사용 트랙 |
| palantir "44건 전수" · "전부 남겼다" | low | 서술 | 3단계 §2 |
| tsmc pretax "916행" 재현 불가 (보존 htm 6줄) | low | 인용 | 3단계 §2. 앵커 문자열로 |
| anthropic.F2 첫 줄 "AA Index 1위" 에 superseded 표시 없음 | medium | FIX-52 누락 | 3단계 §3 |
| F2 14건 note "C-03 미확정" | low | 낡은 note (2차 C 와 중복) | 3단계 §3 |
| f8anth33 "AWS $100B/10년" 과 인용 행 문서명 없음 | low 둘 | 인용 | 3단계 §3. 원문은 기존 약정 위 "more than $100.0 billion" 증액 |
| **nvidia.F2 = 5 가 NVIDIA 보도자료(Rubin 양산·추론 5배)에 섬** | high | **승계 판단** | 긴장 `TEN-RA-02`, recheck 2026-11, 하향 가능. 근거란 `(발표)` 표기 |

## nvidia.F2 를 긴장으로 둔 이유

- 채점규칙 382행 "벤더 발표는 1차 근거가 아니다" 와 349행 "(실측)/(발표) 표기" 를 어겼고, 같은 초안 TRIG-016 은 Rubin 출하를 미발동 미래 사건으로 둔다. 문제 자체는 사실이다.
- 그러나 판단은 v1.5 승계이고 이번 실행은 F2 에 새 잣대를 대지 않았다. C-03 은 경로 매핑을 확정했을 뿐 세대 격차 판정은 승계로 남겼고, anthropic F2 독립 측정 재검토도 점수를 바꾸지 않았다.
- 따라서 AGENTS.md `리뷰 범위 — 승계 판단 예외` 에 해당한다. 긴장 등록과 근거란 표기로 Q05·Q09 fail 은 pass 를 막지 않는다.

## 조율자 메모

- 16건 중 이번 실행이 만든 관측·판단의 설명 정정이 대부분이고 **점수에 닿는 것은 없다.** worker 3단계 예상 총점은 2단계와 같다.
- 렌더러 두 건은 1단계에서 RC-06 을 "근거 불릿" 에만 댄 결과다. 같은 원인(legacy 필드를 직접 읽음)이 재무 표와 서술 절에도 있었다. 3단계에서 14개사 전부 대조를 요구했다.
