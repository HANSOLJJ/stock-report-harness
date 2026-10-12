# 규칙 v2.1 체크리스트

## 1부. 10월 recheck(완료)
- [x] confirm-r4.md 저장, review.md pass, 계약 검증 PASS, 커밋(승인 보류)

## 2-A. ① 만점 조건 · ⑥ P1′ · ⑦ 네 칸 · 두 축 그림
- [x] scorecard/rules/v2.1.json (v2.0 복사, rule_version·note)
- [x] ⑦ matrix large|yes −3, range [−3,0], matrix_restore 기록(C-09 는 다른 쟁점이라 건드리지 않음) → 테스트
- [x] ① ladder 만점 조건 키 + compute_f1 상한 → 테스트(부분·아니오·미확인 4 상한, 예+가격 실측 통과 5, v2.0 불변)
- [x] ① 구조화 입력 스키마(채널·측정 단위·share>0.5·기간·별도 과금 EV·가격 상승 EV), CLI 전용 키(--json) → 테스트, 교차 참조(확정 근거)
- [x] ⑥ 관측 equity_investment_gains_ttm·income_tax_ttm 스키마
- [x] ⑥ 조정 순이익(조정 불가 네 경우), P1′(조정 PER ÷ 성장×100, 이익 ≤0 → −3), 일반 상장 P3 흡수(신규 상장 트랙은 P3 유지), P4 영업외 조건(조정 없을 때만), 범위 −5 → 테스트(단조성 포함)
- [x] ⑥ 비상장 P/S ÷ 보정 매출 성장(5% 미만 −5, 매출 ≤0 자료 대기, 전년 없으면 P/S 구간표), 승격 조건 삭제, C-12 growth_adjusted_ps → 테스트
- [x] recheck 관측으로 14사 ⑥ 계산표 → 사용자 확정: P1′·비상장 경계 1·2·4(미만)
- [x] rules.md 1절(함정 바닥 −17, 배점 원칙 한 줄)·①·⑥·⑦ 절, 8절 C-12, 머리말 v2.1
- [x] 두 축 그림: 산점도와 draft 순위표(과점·함정 열)가 이미 있다. 비교 그룹 색·그룹 표는 2-B 로
- [x] 전체 테스트(unittest 1,516·node 24), 승인된 실행 계약 검증 불변 → 커밋 → 보고

## 2-B. 층별 보유표 · ④⑧ 입력화
- [x] 보유표 자리: F4 판단 안(survival kind). ④ 다각화는 수요 분류 대신 AI 무관 매출 몫 구간(사용자 결정)
- [x] ④ 두 축 사다리 → 사용자 확정(수직 상한 2.5 + AI 무관 몫 80·50·20·5%, 0.5 단위)
- [x] compute_f4·compute_f8, 스키마, CLI 전용 키(object), '준비 중' + trigger_id 검사, 0.5 단위 합산·표시
- [x] ⑧ 네 축(지정학 추가) · 상태(부재 확인 0 · 해당 없음 0 · 비공개 −1 · 탐색 미완 −1) · 칩·클라우드 '없음'이면 공급 0 금지 · axes·deciding_axes·assessment_complete
- [x] 리포트: 전 기업 보유표(초안·HTML, 모바일은 기업명 고정 가로 스크롤), 카드 ④ 산식 줄에 칸별 근거 표지(layer_evidence), 그룹 안 순위, 산점도 그룹 색. v2.0 초안 재렌더 동일(테스트)
- [x] rules.md ③④⑧ 절, 2.6 ⑧ 기본값, 5절 0.5 단위, 체크리스트는 번호를 늘리지 않고 Q01 사례에 보유표 이중 계산을 더함 → 테스트 → 커밋

## 2-D. 다리 · change_type
- [x] init --change-type, 스키마 허용값(baseline-recompute·rule-change·fact-update·correction·company-add) → 테스트
- [x] 다리 표 방법을 TODO 1(11월 실행)에 적음

## 2-E. 현금 연결표
- [x] E1 `collect --kind facts`: companyfacts 에서 ocf_ttm·capex_ttm·income_tax_ttm 최근 1년 복원(누계 산식), 제출일 ≤ 정보 기준일, USD 보고 회사만,
      sec_get 캐시가 정보 기준일보다 오래되면 다시 받음 → 실제 캐시 12사로 FCF basis 성분과 대조, T-08(누계·분기 혼재, 재작성, 52/53주) 테스트 → 커밋
- [x] E2 현금 연결표: `cash_chain.py`(관측 → 행), v2.1 `policies.diagnostics.cash_chain` 이 있을 때만 draft·HTML 렌더, OCF − 설비투자 ≈ FCF 대조 → 테스트 → 커밋

## 2-C. 국면 지표
- [x] 2-C-1 설비투자 분기 시계열·금융리스·장부 밖, NVIDIA 공급자 지원, SDLLMTK
  - [x] C1-a 수집기 분기 시계열(capex_quarterly·finance_lease_additions_quarterly, 바스켓만) + 스키마 지표 → 테스트 → 커밋
  - [x] C1-b 수동 지표(residual_value_guarantee·supplier_* 셋·token_price_index, `_market` ID), from-run·research.md → 테스트
  - [x] C1-c regime.py 계산 + v2.1 policies.regime_indicators + 초안·HTML 국면 지표 절 + rules.md → 캐시 자료 미리보기 → 테스트 → 커밋
- [ ] 2-C-2 모집단 밖 회사·클라우드 세그먼트 마진
  - [x] 마진 두 수열(NVIDIA 총마진 수집, 클라우드 세그먼트 수동 관측), 달력 분기를 분기 가운데 날짜로 맞춤
  - [ ] 참고 회사(CoreWeave·AMD) — 사용자 결정 대기

## 운영
- [x] .claude/agents/*.md model: sonnet, AGENTS.md 「서브에이전트 모델」, score-review·score-research 에 분담
- [x] score-research(v2.1 판정 재료)·score-review(교차표 셋 추가)·score-approve·guide.md 5.5·structure.md 갱신
- [x] TODO 5·9·13 닫기, 1(11월 v2.1 실행 준비) 다시 씀, 14~17 새 항목(남은 단계·ASIC 보류·⑦ 숫자 입력·바스켓 대기)
