# 체크리스트 — 규칙 v2.1 첫 실행(ai-scorecard-2026-10-v21)

## 1. 준비
- [x] init(from-run recheck, v2.1, rule-change, C-12 growth_adjusted_ps) → display_names
- [x] collect --kind facts → 결과 확인(수집 회사·빠진 지표)
- [x] 이전 트리거 carry(같은 정보 마감, 새 창 없음)
- [x] 묶음·판단 지시서(GROUP·JUDGE), 도구 복사(merge·apply)

## 2. 근거·관측 묶음 A~E (Sonnet)
- [x] A·B·C 끝 → 합치기(근거 +165, 관측 +31, 출처 +15) → 확정 165
- [x] D·E 끝 → 합치기 → 확정(E +43, D +156) / 보강 세션 S(지분 평가손익 같은 정의, Alibaba 법인세, 근거 +13)

## 3. 판단 (Opus high)
- [x] J4 ②③ · J5 ⑤⑦ · J1 ① · J2 ④ · J3 ⑧ 끝(J1·J2 는 사용량 한도로 한 번 멈춤)
- [x] apply_judgments(98건) → 트리거 8건 번호 → research 통과

## 4. 계산·초안
- [x] calculate → 기업 요약 14 → draft → review-template → 중간 커밋 1258437

## 5. 리뷰
- [x] 1차 여섯 영역 끝(needs_fix: 규칙 일관성 N1, 사실 b ⑦ 셋 / pass: 사실 a·재무·근거 불릿·출력)
- [x] Maia 발표(사용자 지시 2026-10-13) 근거 4건 확정 EV-microsoft-070~073
- [x] 수정 한 묶음: 판단 세션(Opus) → add_fix_items·confirm(원문 대조 뒤 12건) → apply_judgments --dir judge-fix1(19건) / 치환 70건 → apply_subst
- [x] research → calculate → 기업 요약 4건 → draft → review-template --force → 중간 커밋 4580197(코드 59d59e3)
- [x] 확인 리뷰 1회(Opus high) pass → review.md(fill_review.py) → 계약 검증 PASS
- [x] 커밋, 승인 대기 보고

## 6. 막혔던 원문 다시 열기(사용자 지시 2026-10-13, 403 규칙 변경 뒤)
- [x] 브라우저로 원문 아홉 건 열기(Sonnet, REOPEN-INSTRUCTIONS.md) → work/reopen1/ (여덟 건 열림, 소장은 사용자 PDF)
- [x] 원문 대조 확인 → add_fix_items → confirm (EV-openai-160 + 9건)
- [x] 인용 판단 수정(Opus high) → 새 근거 2건 대조·확정 → apply_judgments --dir reopen1(9건) → 치환 16건
- [x] research → calculate(점수 불변, 요약 변경 없음) → draft → review-template --force
- [x] 바뀐 부분 확인 리뷰 1회(Opus high, confirm-r2 pass) → review.md → 계약 검증 PASS → 커밋 → 승인 대기 보고
