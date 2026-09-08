# worker 수정 완료본 재검증

검증일 2026-09-08. 검토 기준은 worker `34eeff87643b146af9942cda0e428eef31561ab1`이다. 수정 구현은 `7a05b3d`, 남은 작업 문서는 `34eeff8`이다.

**판정은 수정 7건 확인, 추가 수정 4건 전달이다.** 기존 승인 실행의 계산 결과·승인 해시·HTML 포함 계약은 통과했다. 신규 관측 입력 검증과 문서 정합성에 남은 문제가 있어 전체 구현의 최종 통합 승인을 의미하지 않는다.

## 검증 범위와 재현

- worker에서 `python -X utf8 -B -m unittest discover -s tests -v` 실행. 35건 통과.
- 설계진행에서 `python -X utf8 -B validation/test_scorecard_review.py` 실행. 독립 회귀 10건 통과.
- 설계진행에서 `python -X utf8 -B validation/recheck_worker_final.py` 실행. 증거는 `worker-final-recheck-evidence.json`에 기록한다. 이 스크립트는 추가 문제도 관측 결과로 저장하므로 종료 코드 0만으로 모든 항목이 해결됐다고 판단하지 않는다.
- worker에서 `python -X utf8 -B scripts/validate_report_contract.py ai-scorecard-2026-09-baseline --require-html` 실행. 9항목 통과.
- 원본 HTML/MD 재이관은 설계진행의 임시 디렉터리에서 수행했다. worker의 기준선·실행·승인·HTML·이력 파일에 쓰지 않았다. 감시 대상 47개 파일과 HEAD는 종합 감사 실행 전후 변화가 없었다.
- 승인자 음성 검증은 잘못된 값만 쓰기 단계에 전달하고 쓰기 함수를 감시했다. 새 승인 파일은 만들지 않았다. C-05/C-06/C-13 분기 검증은 메모리 안의 테스트 선택이며 사용자 결정이 아니다.

## 전달한 수정 7건의 결과

| 출처 | 확인 결과 |
| --- | --- |
| REVIEW-02/A | 흑자 8사의 런웨이를 `not_applicable`, 값 null, 사유 포함으로 이관한다. 신규 기준선은 legacy_unverified 198, not_disclosed 16, not_applicable 8, incompatible_basis 4, parse_failed 1로 총 227건이다 |
| REVIEW-02/B | verified FCF의 period 누락은 거부하고 정상 기간은 허용한다. 기존 이관 기록은 미상 기간을 유지한다. 역전 기간 허용은 아래 추가 문제로 분리한다 |
| REVIEW-02/C | 상태별 건수, 시총 VAL 선택 정책, Menlo·Meta 분기/TTM·경계 트리거 차이를 기록한다. 재이관한 scores/observations/triggers JSON 및 import-report가 현재 기준선과 일치한다 |
| REVIEW-03/D-01 | 새 plan 렌더링에 pending_data·needs_judgment·needs_rule_decision 및 승인 전용 awaiting_user 구분이 들어간다 |
| REVIEW-03/D-02 | 승인 스키마와 쓰기 진입점에서 빈 문자열·공백·null·숫자를 거부한다. 실제 사용자 신원 인증 기능을 검증한 것은 아니다 |
| REVIEW-03/D-04 | T-08 미구현을 structure/open-items에 명시했다. 문서 정정 완료이며 T-08 구현 완료는 아니다 |
| REVIEW-03/D-05 | 메모리에서 Q07 행을 제거하면 오류가 발생하고 review 구조 성공 라벨은 붙지 않는다 |

## 기준선과 승인본

원본 MD의 14사 factor 점수·합계·과거 순위와 이관 점수의 불일치는 0건이다. incompatible_basis 4건은 원값을 보존하면서 계산 입력에서 제외된다. 원본 트리거 39건의 내용도 유지된다.

승인 실행은 수정 전 자료 상태 분포(legacy_unverified 198, not_disclosed 24, incompatible_basis 4, parse_failed 1)를 보존한다. 신규 기준선과 승인 실행을 같은 데이터라고 표시하면 안 된다. 승인 실행의 저장 결과는 현재 코드로 메모리 재계산한 결과와 완전히 일치한다.

| 메모리 선택 | 순위 포함 | 미결 규칙 | SpaceX 상태 |
| --- | --- | --- | --- |
| 없음 | 9사 | C-06, C-13 | 미완료 |
| C-13 reject_proxy | 9사 | C-06 | 미완료. TSMC F6는 pending_data |
| C-13 accept_proxy_with_flag | 10사 | C-06 | 미완료 |
| C-06 경계 수용 + C-05 apply | 9사 | C-13 | 비교 가능성 판단이 없어 미완료 |
| C-06 경계 수용 + C-05 diagnose_only | 10사 | C-13 | 완료 |

## 추가 문제와 요청

| ID | 중요도 | 근거와 요청 |
| --- | --- | --- |
| REVIEW-04/R1 | medium | verified fcf_ttm에 start=2026-06-30, end=2025-07-01을 넣어도 스키마가 허용한다. 기간 존재 확인과 별도로 start <= end를 검증하고 역전 기간 회귀를 추가해야 한다. 신규 자료 입력 전 필요하다 |
| REVIEW-04/R2 | low | 저장 HTML과 현재 입력으로 메모리 재렌더한 HTML은 References의 output-readability 수행자 설명 1줄이 다르다. 저장본은 1차+main Playwright, 현재 review는 별도 세션 1차·2차다. 실제 이력에 맞춰 문서와 출력의 정합성을 회복해야 한다. 점수 차이는 없다. 현재 계약 검증만으로 이 불일치를 잡지는 못한다 |
| REVIEW-04/R3 | medium | open-items C-05 행은 두 선택 모두 C-06과 함께면 SpaceX 완료처럼 읽힌다. 실제 현재 입력에서는 diagnose_only만 완료하고 apply는 G4 비교 가능성 판단 대기다. 선택별 조건을 구분해야 한다 |
| REVIEW-04/R4 | medium | 서로 다른 factor의 경계값 방향 차이를 Q03 위반으로 단정한 설명은 근거가 없다. Q03은 기업 간 동일 잣대다(설계 지침 376행). 각 factor의 구간을 기업마다 동일하게 적용하는지 검토해야 하며 이 설명만으로 점수 구간을 변경하면 안 된다 |

추가 분류 의견은 다음과 같다.

- REVIEW-03/D-10은 동일 입력의 단순 재실행을 막을 이유는 없다. 데이터·판단·규칙·가격 변경을 반영하는 재채점 이력을 저장하기 전에 실제 변경 사유 계약이 필요하다.
- C-06에 여러 쟁점이 묶여 있다는 지적은 타당하다. 경계 선택 하나가 FCF 0·영업손익 0·정성 정의까지 해결했다고 표시하지 않는다. 분리 방식과 채점 정책은 아직 확정하지 않았다.
- REVIEW-02/P2·P6·P7, REVIEW-03 문서 보완, T-08은 해당 기능 활성화 전 요구로 계속 추적한다. 원자료 이관 회귀를 통과했다고 신규 재무 수집 전체가 검증된 것은 아니다.
- 7a05b3d의 Co-Authored-By trailer가 사용자 금지 지침과 충돌하는 점도 worker에 알렸다. 기존 이력은 임의 재작성하지 않았다.

## 전달 기록과 한계

worker의 open-items 전달 `msg_1bc7b87721e8`을 읽고 수신 처리했다. 재검증 결과와 추가 4건은 같은 스레드의 `msg_2ad4d2647c8b`로 발송했다. 발송 성공과 worker의 실제 열람·수정 완료는 구분한다.

이번에는 브라우저 시각 검증이나 Qwen 별도 세션 재실행을 하지 않았다. HTML 계약과 렌더링 결과를 직접 대조했으며, Qwen 지적의 재검증은 설계진행 감사 스크립트로 수행했다. 원문에 담긴 시장 사실을 최신 외부 자료로 재검증하지 않았다.
