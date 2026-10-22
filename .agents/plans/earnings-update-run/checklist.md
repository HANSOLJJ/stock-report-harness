# 실적 반영 실행 체크리스트

## 결정
- [x] D1 실행 종류 A
- [x] D2 가격 전부 새로
- [x] D3 범위는 자료가 정한다
- [x] D4 판단 나이 상한 120일
- [x] D5 리뷰 범위
- [x] 흐름 문서(guide.md mermaid·workflow.html) 커밋 01d7009
- [x] 계획 사용자 확인 (2026-10-22 "좋아")

## U1 규칙 v3.1
- [x] v3.1.json (v3.0 + policies.rejudge.update_runs)
- [x] schema.validate_rules 새 키 (`_validate_update_runs_policy`)
- [x] rules.md 머리말·2.9 (개정 이력 절은 없다 — 경위는 커밋에 남긴다)
- [x] 테스트: v3.0 해시 불변·v30full 확인 유효, v3.1 점수 규칙 동일, 문서 대조 (1,818개 통과)
- [x] 커밋
- [ ] 선언한 키의 소비자: price_refresh(U4 diff)·manual_check_forms(U3·U5)·나머지(U3) — 끝까지 읽는 코드가 없으면 뺀다

## U2 실행 선언
- [x] init --update-companies --update-reason (from-run 필수, add·companies 와 배타, v3.1 이상, 기준일은 이전보다 뒤, 가격일·컷오프는 물려받지 않음)
- [x] run.json continued_from.updated_companies, refreshed_at(v3.1 이상 모든 실행), update_scope{reason, extra}
- [x] validate_run, is_update_run, update_runs_policy, refreshed_here(set-as-of 도 갱신일을 옮긴다)
- [x] 리뷰 승계 예외는 기업 추가 실행에만 (실적 반영 실행도 막음)
- [x] 테스트 (test_update_run_init 18개 + test_v20_validate 1개, 전체 1,837개)
- [x] 커밋
- [ ] U4 에서: `_inputs_from_run` 의 규칙 변경 경고("층·사업 단위 규칙이라 diff 로 견주지 못하므로…")를 diff 지원에 맞게 고친다

## U3 범위 계산과 검사
- [ ] update_scope.py (필수 판단, 추가 항목, 실적 감지, 나이)
- [ ] collect_filings 후보에 items·report_period
- [ ] rejudge_findings·research·previous_triggers 연결
- [ ] scorecard_cli.py scope
- [ ] 테스트 (걸려야 할 값·걸리면 안 될 값·일부 행만)
- [ ] 커밋 → 이정표 1 보고

## U4 diff
- [ ] 층 규칙 가드 해제 + v3.0 판단 ID 유일성 테스트
- [ ] 실적 반영 실행 모드
- [ ] 테스트
- [ ] 커밋

## U5 출력
- [ ] research.md 갱신 범위 절
- [ ] 초안·HTML 반영 기준일
- [ ] history.csv change_type
- [ ] 테스트 (v30full 초안 해시 불변)
- [ ] 커밋 → 이정표 2 보고

## U6 리뷰·문서·스킬
- [ ] score-review 실적 반영 실행 범위
- [ ] score-update 스킬
- [ ] AGENTS.md, guide.md, structure.md, workflow.html
- [ ] .agents/skills 동기화
- [ ] 커밋

## P 첫 실적 반영 실행
- [ ] init (v30full → q3a, v3.1)
- [ ] 가격·공시 전부 수집, 실적 감지로 범위 확정
- [ ] 판단 세션 (Opus high)
- [ ] research → calculate → draft → diff
- [ ] 리뷰 (D5 범위)
- [ ] 확인 대기 보고 → 이정표 3 보고
