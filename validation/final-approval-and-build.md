# 최종 승인·빌드 검증 — ai-scorecard-2026-09-obsreg

- 일시: 2026-09-17
- 검증자: 조율자(설계진행)
- 대상: 워커의 최종 과제(`msg_724d32022fcd`) 수행 결과
- 판정: **pass**

## 조율자가 직접 확인한 것

1. **점수 126칸 불변.** `f313060` 시점 `results.json` 과 현재 파일을 평탄화해 전 키를 대조했다.
   바뀐 키는 셋뿐이고 전부 해시다 — `input_hashes/rules` · `input_hashes/run` · `results_hash`.
   14개사 총점과 factor 값은 하나도 움직이지 않았다.

2. **코드 변경은 동작에 닿지 않는다.** `calc_f9.py` 의 diff 는 **주석 세 줄뿐**이고 로직이 없다.
   `render_common.py` 는 방법 표 문면이며, 규칙 변경은 `also_precedes_loss_band` · C-06 `summary` ·
   `TEN-RA6-01.also_covers_listed` 의 서술이다.

3. **계약 검증기 통과.** `scripts/validate_report_contract.py` 가 `[PASS]`, **오류 0 · 경고 2**.
   경고는 승계 예외 11건 목록과, 그 예외가 `잣대 불변` 조건까지 기계로 확인한 것은 아니라는 고지다.

4. **테스트 677개 전부 통과.** 처음에 11건이 실패했으나 원인은 `tests/__pycache__` 의 낡은 바이트코드였다.
   `PYTHONPATH=scripts:. python -m unittest discover -s tests -t .` 로 돌리면 `OK` 다.
   워커가 고친 테스트 4파일의 diff 를 전부 읽었고, 옛 시점 상태를 고정하던 단언을 현재 사실로 바꾼 것이며
   실질 단언(체크리스트 fail 행마다 긴장 번호가 있는지, 경고 11건과 Q 목록)은 오히려 강해졌다.

5. **승인 해시 여섯이 현재 입력과 일치.** `approval.json` 의 `results` 가 `results.json` 내부
   `results_hash` 와 같고(`4a3f6c05…`), 검증기의 `approval hashes match current inputs` 도 ok 다.
   `approved_by: 사용자` · `approval_id: 0b054d597be5bf87`.

6. **리뷰 파일이 사실대로다.** 재무 계산 영역에 `8차 needs_fix → FIX-59·61·63 반영 → 재판정 3회 끝에 pass`
   경과가 적혔고, 규칙 일관성 칸은 `FIX-61~64 가 바꾼 규칙 문면은 이 영역이 아직 보지 않았다` 를 명시한다.
   리뷰어가 확인하지 못한 여섯 가지도 그대로 남겼다.

7. **산출물.** `output/ai-scorecard-2026-09-obsreg.html` 273,253 bytes.
   방법 표에 FIX-64 로 고친 문면(`G1 통과와 손실률 밴드 둘 다보다 앞선다`)이 실렸고 미치환 마커가 없다.
   `history.csv` 에 14개사 줄이 `approval_id 0b054d597be5bf87` 로 기록됐다(openai 13위 · oracle 14위).

## 남긴 사실

- 워커가 FIX-64 로 리뷰어의 마지막 low 를 **넘기지 않고 고치는 쪽**을 골랐다. 지시서가 준 두 선택지 중 하나이며
  코드를 건드리지 않아 점수가 바뀔 수 없다는 근거를 붙였다.
- 이 시점에 워커 작업 트리는 아직 커밋 전이었다. 커밋은 별도로 확인한다.

## 커밋 확인 (추가)

- 워커 커밋 `befdfbe` — `feat(fix-64): 네 영역 pass — 마지막 발견 반영 · 사용자 승인 · 리포트 생성 (점수 불변)`.
- trailer 없음, `.claude/settings.json` 은 커밋에서 제외됐다(작업 트리에 변경으로 남아 있다).
- 커밋 시점에 캐시를 지우고 다시 돌린 전체 테스트는 **688건 OK** 로 워커가 회신에 적은 수와 같다.
