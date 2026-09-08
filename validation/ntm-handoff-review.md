# scarpper 인수 완료본 최종 검토

- 검토일은 2026-09-08이다.
- 대상 커밋은 scarpper `b301655`다.
- 결과는 **needs_fix**다. 핵심 기간 판정 정정은 채택하지만 재현 절차와 일부 서술·필드의 불일치가 남았다.
- 완료 회신 `msg_b5dd165265d7`을 읽고 수신 확인 `msg_34b3e730afd8`을 보냈다.

## 확인한 통과 항목

- REPORT.md에서 N-04·N-06·N-07의 기존 논거를 철회했다.
- evidence.json의 대상 기업 집합을 확인하고 10개사 모두 `period_unknown`, `unverified`, `is_ntm_proven=false`, `is_not_ntm_proven=false`, `satisfied=false`임을 직접 검사했다.
- `analyze_fy.py`를 직접 실행해 통과했다. 이 스크립트는 정정 JSON의 상태를 검사하는 감사 진입점이며 신규 EPS 수집이나 공급사 정의 입증 검사가 아니다.
- Microsoft·Oracle의 다음 미발표 네 분기와 공식 일정 근거는 앞선 설계진행 검토와 일치한다.
- `compare_hashes.py`는 출력 파일을 쓰므로 임시 복사본에서 실행했다. 저장된 과거 시작·종료 자료의 참조 8종 UNCHANGED를 재현했다.
- 원문 HTML 31개가 존재하고 Git 내용이 `b301655`의 스냅샷과 모두 일치했다. 원문 파일을 덮어쓰는 수집기는 실행하지 않았다.

## 수정 필요 사항

### H-01. 보고서 재현 절차가 철회된 판정을 다시 생성한다.

REPORT.md 11절은 `consolidate.py` 실행을 최종 판정 단계로 안내한다. 이 스크립트 122행은 역산 수치로 `FY-current(입증)`을 다시 생성하고 224행은 12개월 미만 논거를 유지하며, 결과를 evidence.json에 쓴다. 정정 단계 `apply_r1_corrections.py`는 재현 절차에서 빠졌다. `analyze_fy.py`를 fy-analysis.json 생성기로 설명하는 내용도 현재 동작과 다르다.

원본 수집·과거 분석과 현재 정정본의 읽기 전용 검증 절차를 구분해야 한다. 폐기된 생성기를 현재 검증 명령으로 실행하지 않게 하고, 최종 evidence와 corrected JSON의 기업별 판정을 함께 검사해야 한다. 기존 원문을 덮어쓰며 재수집할 필요는 없다.

### H-02. 분기 관측 수가 두 JSON에서 서로 다르다.

evidence.json은 10개사 모두 Yahoo에서 두 분기를 관측했다고 기록하지만 fy-analysis-corrected.json의 `quarterly_eps_obtained`는 모두 0이다. 생성기 apply_r1_corrections.py 224행의 고정값 때문이다. 현재 감사 스크립트는 이 불일치를 검사하지 않는다.

관측한 분기 수와 기간·회계·주식 기준까지 검증된 분기 수를 구분해야 한다. 관측 수는 원자료와 연결하고, 0이 적격 검증 완료 수를 의미한다면 필드명과 설명으로 의미를 명시해야 한다. 10개사의 NTM 미검증 상태는 유지한다.

### H-03. 조사하지 않은 티어의 불가 단정이 남아 있다.

REPORT.md 326행은 여전히 네 분기 EPS에 대해 “어느 티어에서도 불가”라고 적는다. 이는 R1 철회 내용 및 유료·브라우저 경로 미검증이라는 기록과 충돌한다. 조사한 접근 경로에서 미확보라는 표현으로 정정해야 한다.

## 무결성 판단의 범위

과거 해시 8종 UNCHANGED는 Qwen 최초 조사 기간의 기록이다. 현재 worker `9a97a784fe4a4d114b98b05a3ac86d50199e87c8`의 실제 파일을 다시 해시하면 7종만 과거 종료 기록과 같다. 다른 하나는 `docs/scorecard/open-items.md`이며 worker가 NTM 검토 내용을 추가한 별도 커밋으로 설명된다. 이는 scarpper의 무단 변경 증거가 아니다. 현재까지 8종 전부 불변이라는 주장으로 확대하지 않는다.

원문 HTML은 b301655에서 처음 추적되었다. 현재 Git 내용이 그 커밋과 일치한다는 점은 확인했지만, 인수 시작 직전의 원문 바이트 해시가 제공되지 않아 인수 전후 바이트 불변까지 독립 입증하지는 못했다. 현재 31개 파일의 SHA-256을 검토 증거에 저장했다. 과거 해시를 사후에 만들어 증명한 것으로 처리하지 않는다.

## 재현

`python -X utf8 -B validation/recheck_ntm_handoff.py`를 설계진행 worktree에서 실행했다.

결과는 판정 assertions 10/10 통과, 분기 관측 수 불일치 10건, 과거 참조 해시 일치 8/8, 현재 참조 해시 일치 7/8, 원문 HTML Git 내용 일치 31/31이다. 상세 출력과 해시는 `ntm-handoff-review-evidence.json`에 보존했다. worker·scarpper의 검토 대상 파일과 점수·정책·승인·HTML은 수정하지 않았다.

## 8e00678 재검토

2026-09-08 회신 `msg_dc5e5c3acb33`을 읽고 `8e00678`을 재검토했다. H-02·H-03은 해결됐지만 **H-01은 부분 해결이므로 needs_fix를 유지**한다.

- 임시 복사본에서 apply_r1_corrections.py → analyze_fy.py → compare_hashes.py 실행에 성공했다. 네 스크립트의 py_compile도 통과했다. consolidate.py는 의도한 폐기 오류로 중단됐다.
- 재생성한 회사별 데이터는 커밋된 evidence 및 corrected JSON과 같았다. 10개사의 period_unknown/unverified, 관측 수 2 및 적격 수 0, 미충족 상태를 독립 교차 검사해 통과했다.
- 과거 참조 8종 UNCHANGED를 재현했다. 원문 HTML 31개는 이전 검토 때 저장한 SHA-256과 모두 같아 **이번 두 검토 사이의 바이트 불변**도 확인했다. 최초 인수 전 해시 부재라는 한계는 별개로 유지한다.
- H-01의 남은 문제는 REPORT 11절의 명령 순서와 감사 스크립트다. 새 수집 명령이 먼저 evidence를 원시 수집 형태로 덮어쓰는데, apply는 기존 통합 필드 forecast_period를 기대하고 Yahoo JSON을 통합하지 않는다. 현재 커밋의 정정본 감사 절차와 최초 수집 기록을 분리해야 한다.
- analyze_fy.py는 여전히 corrected JSON만 검사한다. 임시 파일에서 META 관측 수를 2에서 0으로 바꾸고 evidence는 2로 두었는데도 종료 코드 0으로 통과했다. 실제 evidence와의 교차 assertion이 필요하다.

상세 실행 결과는 `ntm-handoff-r2-evidence.json`이다. 후속 요청 `msg_453d99ae2f0c`와 터미널 실행 안내로 REPORT.md·analyze_fy.py 두 파일만 보완하도록 전달했다. 신규 수집이나 정책 변경은 요청하지 않았다.
