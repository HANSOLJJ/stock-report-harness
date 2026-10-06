# 2026-10 정기 재채점 체크리스트

## 0. 준비
- [x] 10월 시험 실행 묶음과 history.csv 14행 커밋(`b170b9e`)
- [x] `init --from-run ai-scorecard-2026-10-test --rule v1.8 --as-of 2026-10-06`
- [x] 트리거 처리 방침 확정(plan.md)
- [x] SDLLMTK 를 TODO 13번으로(`ccd3816`)

## 1. 수집
- [ ] collect (news·filings·prices)
- [ ] 후보 선별

## 2. 트리거
- [ ] trigger-candidates 확인
- [ ] 시험 실행 40건 carry·결론
- [ ] 기준선 관찰 유지 15건 새 항목
- [ ] 기준선 중복 철회 19건(12 + 7)
- [ ] 날짜 경과 2건(011, 031*), 철회 3건(002, 030, 038)
- [ ] `*` 건(004, 006, 031) 발동 여부 판정
- [ ] trigger_carry_gaps 0건, overdue 0건 확인

## 3. 계산·초안
- [ ] research → calculate → draft

## 4. 리뷰
- [ ] 1차 리뷰(4 영역 + Q01~Q23)
- [ ] 수정 한 묶음
- [ ] 확인 리뷰 1회
- [ ] 승인 대기 보고
