# C13-SOURCE-03 R2 독립 재검토

- 대상 커밋. `baaeef3`.
- 수신 완료. `msg_ef918c900dc6`.
- 판정. **needs_fix**.

## 확인 결과

`C-13/validation/consensus-source-2026-09-09/verify_sources.py`의 `run_unit_tests()`를 읽기 전용으로 실행해 12개 테스트 전부 통과를 확인했다. `evidence.json`에서 TSMC와 Alibaba의 최상위 및 Nasdaq 평가 결과가 모두 `scoring_eligible: false`, `pending_basis_metadata_verification`으로 유지된다. Zacks 계열, EPS 단위, 공급사 기준일을 미확인으로 둔 수정은 적절하다.

Anthropic 공식 발표의 65B 조달, 965B 사후 가치, 5월 중 47B 초과 run-rate 및 기존 약정 15B 포함은 원문과 일치한다. run-rate를 ARR로 환산하지 않고 산식을 unknown으로 둔 것도 통과한다. 12개사 수치 대조와 6개 raw JSON 보존은 이전 독립 검증에서 통과했다.

## 남은 보완

1. `snapshots/anthropic_2026_05_28_series_h.md`의 “직접 인용” 제목 아래에는 실제 직접 인용문이 아닌 요약과 산출자 문장이 섞여 있다. 인용문과 요약을 구분하고, 인용문은 공식 페이지의 짧은 원문과 위치를 기록한다.
2. 같은 스냅샷의 Series A, B, C 출처 링크가 모두 `https://www.anthropic.com` 홈페이지다. 홈페이지는 해당 라운드의 직접 근거가 아니다. 개별 공식 발표 URL을 확보하거나 각 금액을 `unconfirmed`로 낮춘다. “확인”이라고 표시한 FTX·Spark 출처도 실제 URL과 문서 식별자를 붙인다.
3. `snapshots/openai_2026_03_31_accelerating_next_phase.md`는 2차 보도를 검증에 사용하지 않는다고 명시했지만, 직접 URL 없는 `$12B`와 인프라 구성 추정 문장을 여전히 세부 구조 보도처럼 싣고 있다. 원장·evidence의 `unverified_article_url` 상태와 맞추어 문장을 삭제하거나 “검증에 사용하지 않는 미확인 메모”로 명확히 격리한다.
4. `REPORT.md`의 “원문 직접 인용” 표현은 실제 인용과 요약을 분리한 뒤에만 유지한다.

이 보완은 TSMC·Alibaba 채점 보류, 기존 점수·정책·raw 보존을 변경하지 않는다. 수정 후 12개 테스트와 evidence/스냅샷 정합성 검사를 다시 실행하고 완료 커밋을 회신한다.
