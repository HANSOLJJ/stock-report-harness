# 규칙 v2.1 체크리스트

## 1부. 10월 recheck(완료)
- [x] confirm-r4.md 저장, review.md pass, 계약 검증 PASS, 커밋(승인 보류)

## 2-A. ① 만점 조건 · ⑥ P1′ · ⑦ 네 칸 · 두 축 그림
- [x] scorecard/rules/v2.1.json (v2.0 복사, rule_version·note)
- [ ] ⑦ matrix large|yes −3, range [−3,0], matrix_rescale 후속 기록, C-09 갱신 → 테스트
- [x] ① ladder 만점 조건 키 + compute_f1 상한 → 테스트(부분·아니오·미확인 4 상한, 예+가격 실측 통과 5, v2.0 불변)
- [x] ① 구조화 입력 스키마(채널·측정 단위·share>0.5·기간·별도 과금 EV·가격 상승 EV), CLI 전용 키(--json) → 테스트, 교차 참조(확정 근거)
- [ ] ⑥ 관측 equity_investment_gains_ttm·income_tax_ttm 스키마
- [ ] ⑥ 조정 순이익(조정 불가 네 경우), P1′(조정 PER ÷ 성장×100, 이익 ≤0 → −3), P3 삭제, P4 영업외 조건(조정 없을 때만), 범위 −5 → 테스트(단조성 포함)
- [ ] ⑥ 비상장 P/S ÷ 보정 매출 성장(5% 미만 −5, 매출 ≤0 자료 대기, 전년 없으면 P/S 구간표), 승격 조건 삭제, C-12 갱신 → 테스트
- [ ] recheck 관측으로 14사 ⑥ 계산표 → 사용자에게 보이고 P1′ 경계 확정
- [ ] rules.md 1절(함정 바닥 −17, 배점 원칙 한 줄)·①·⑥·⑦ 절, 머리말 v2.1
- [ ] 두 축 그림: 비교 그룹은 2-B 보유표가 정하므로 색은 2-B 로 미룸(2-A 에서는 draft 과점·함정 표만)
- [ ] 전체 테스트(unittest·node), 승인된 실행 계약 검증 불변 → 커밋 → 보고

## 2-B. 층별 보유표 · ④⑧ 입력화
- [ ] 보유표 자리(별도 kind 우선) 설계, 수요 분류표, 최소 조건(5%)
- [ ] ④ 두 축 사다리 초안 + 14사 계산표 → 사용자 확정
- [ ] compute_f4·compute_f8, 스키마, propose 키, '준비 중' + trigger_id 검사
- [ ] ⑧ 세 상태(부재 확인 0 · 비공개 −1 · 탐색 미완 −1), axes·basis·assessment_complete
- [ ] 리포트: 전 기업 보유표, 카드별 행·근거 표지, 그룹 안 순위, 산점도 그룹 색
- [ ] rules.md ③④⑧ 절, 2.6 표, 체크리스트 한 줄 → 테스트 → 커밋 → 보고

## 2-D. 다리 · change_type
- [ ] init --change-type, 스키마 허용값 → 테스트
- [ ] 다리 표 방법(11월 판단 세션이 10월 사실로 v2.1 입력을 먼저 채움)을 11월 실행 계획에 적기

## 2-E. 현금 연결표
- [ ] ocf_ttm 관측, 연결표 계산(results 밖), 렌더 → ⑨ 와 숫자 대조 → 테스트

## 2-C. 국면 지표
- [ ] 2-C-1 설비투자 분기 시계열·금융리스·장부 밖, NVIDIA 공급자 지원, SDLLMTK
- [ ] 2-C-2 모집단 밖 회사·클라우드 세그먼트 마진

## 운영
- [ ] .claude/agents/*.md model: sonnet, 스킬·AGENTS.md 에 모델 분담 한 줄
- [ ] score-research·score-review·guide.md 갱신
- [ ] TODO 5·13 닫기, ASIC 침투율·⑦ 숫자 입력(v2.2) 새 항목
