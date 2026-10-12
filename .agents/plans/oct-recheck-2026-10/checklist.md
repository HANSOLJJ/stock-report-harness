# 체크리스트 — 2026-10 정기 재실행(recheck)

## 1. 준비
- [x] init(from-run rejudge, as-of 10-12, price 10-09, cutoff 10-12)
- [x] collect all since 2026-10-06 (후보 3,076, 10-08 이후 1,671)
- [x] TSMC·Alibaba 시총: 주말 신선도 수정(커밋) 뒤 10-09 관측 재수집
- [x] resolve-urls <slug> (74건 풀림, 실패 0)
- [x] 작업 지시서(GROUP·JUDGE) 이 실행용으로 작성, 도구 복사(merge·apply)

## 2. 근거·트리거·관측 (묶음 A~E)
- [x] 묶음 다섯 띄움
- [x] 산출물 합치기(근거 +49, 발췌 교체 30, 트리거 67/67 + 새 10, 관측 +12, 출처 +68) → resolve-urls(8) → 확정 49 → 옛 미확인 문장 정리(clean_fixed_evidence.py)
- [x] 원문 미독 검사: 근거 0, 남은 것은 '제목만' 판단 문장 6건(재판단이 고친다)

## 3. 판단 (①②③④⑤⑦⑧ × 14)
- [x] 판단 세션 일곱 띄움(group-notes.md 로 묶음 사실 전달)
- [ ] apply_judgments → proposal accept
- [ ] research 통과(재판단·트리거·원문)

## 4. 계산·초안
- [ ] diff --against rejudge, calculate
- [ ] 기업 요약 14건
- [ ] draft, review-template

## 5. 리뷰
- [ ] 4영역 리뷰 다섯 세션
- [ ] review.md 채움, 수정 한 묶음
- [ ] 확인 리뷰 → pass
- [ ] 계약 검증 → 승인 대기 보고
