# 규칙 v2.1 첫 실행 — 10월 사실(2026-10-12)로 v2.1 입력 채우기

## 무엇을, 왜
- 사용자 지시(2026-10-12): "실행 — 서브에이전트 룰 참고". TODO 1(규칙 v2.1 첫 실행)을 시작한다.
- 지금은 3분기 실적 전이다. 그래서 이 실행은 TODO 1 의 v2.0→v2.1 다리 첫 단계, 곧 **recheck 와 같은 사실(기준일 2026-10-12, 가격 10-09, 정보 마감 10-12)에 규칙만 v2.1 로 바꾼 실행**이다. 이 실행과 recheck 의 점수 차이는 규칙 변경 몫이다. 11월 사실로 다시 판정하는 둘째 단계는 3분기 실적 뒤 별도 실행이다.
- slug `ai-scorecard-2026-10-v21`, `init --from-run ai-scorecard-2026-10-recheck --rule v2.1 --change-type rule-change`, C-12 = `growth_adjusted_ps`(사용자 결정 2026-10-12, v2.1 은 다른 선택을 계산하지 않음), SpaceX 표시 이름은 `display_names`.

## 단계와 맡는 자리(AGENTS.md 「서브에이전트 모델」)
1. **준비(조율자)**: init, display_names, `collect --kind facts`(ocf·capex·법인세 최근 1년, 바스켓 분기 설비투자·금융리스, NVIDIA 분기 매출총이익·매출), 이전 트리거 carry(같은 정보 마감이라 새 창 없음).
2. **근거·관측 묶음(Sonnet, 기본 노력) 다섯**: A nvidia·tsmc·apple / B alphabet·amazon·microsoft / C meta·oracle·palantir / D anthropic·openai / E alibaba·tesla·spacex-xai. 맡은 회사의 ④ 여섯 층 칸 근거(판매·자체 사용·준비 중), ④ AI 무관 매출 몫 근거, ① AI 수익화 측정값(과반 몫·별도 과금·가격 상승) 근거, ⑧ 네 축 입력 근거와 새 관측(지분 평가손익·비상장 보정 매출·국면 지표 수동 관측)을 원문에서 확인해 낸다. CLI 는 sec-get·resolve-urls 만.
3. **합치기·확정(조율자)**: merge → 원문 확인된 근거 confirm.
4. **판단(Opus, high) 다섯**: J1 ①(14사, v2.1 수익화 재료 포함) · J2 ④ 보유표(14사 × 6층) · J3 ⑧ 네 축(J2 뒤, 공급 축 안전장치가 보유표를 읽음) · J4 ②③ · J5 ⑤⑦. 정기 실행이라 전부 `status: new`, 입력이 같으면 reconfirm.
5. **반영·계산(조율자)**: apply_judgments → research → calculate → 기업 요약 14건 → draft → review-template.
6. **리뷰**: 사실·출처(fact-checker, Sonnet), 근거 불릿(evidence-editor, Sonnet), 출력·가독성(report-designer, Sonnet), 재무 계산(Sonnet), 규칙 일관성(Opus high, 교차표 셋 + v2.1 교차표: ① 수익화 비율, ④ 보유표 같은 층 같은 판정). 수정 한 묶음 → 확인 리뷰 1회(Opus high).
7. **마감**: 계약 검증, review.md, 커밋, "승인 대기" 보고. 승인·빌드는 하지 않는다.

## 이어받은 과제
- confirm-r4 N2(Anthropic ⑧ 옛 '2배' 표현) → J3, N3(NVIDIA SB Energy 보증은 ⑦ 소관) → J3·J5. recheck 에서 넘긴 이름 변경(SpaceX)은 display_names.

## 하지 않는 것
- 승인·승인 취소·빌드, `.env`·approval.json·history.csv·규칙 파일 수정, push.
