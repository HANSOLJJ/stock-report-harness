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
- [x] 조율자 근거 추가 6건(EV-openai-070·071, EV-alphabet-073·074, EV-microsoft-044, EV-meta-058) 확정, TRG-112 추가
- [x] apply_judgments → proposal accept (98건)
- [x] research 통과(재판단·트리거·원문)

## 4. 계산·초안
- [x] calculate (바뀐 칸: alphabet·microsoft·meta ⑧, alibaba ⑥, openai ⑦)
- [x] 기업 요약 14건(init 이 이어받지 않아 새로 씀)
- [x] Tesla 신용한도 관측 basis 모양 수정(렌더러가 목록을 기대) → draft, review-template
- [x] 중간 커밋

## 5. 리뷰
- [x] 4영역 리뷰 다섯 세션 띄움
- [x] 1차 결과: 규칙 일관성·재무 계산·사실·출처 A needs_fix, 사실·출처 B·출력 pass (A·B 는 사용량 한도로 끊겼다가 이어서 끝냄)
- [x] 수정 한 묶음(make_fix1.py·summaries_r2.py, 근거 3건 추가) → research·calculate·draft·review-template --force → 커밋
- [x] 확인 리뷰 2차 blocked(C1) → 수정(make_fix2.py) → 확인 리뷰 3차 pass
- [x] 사용자 결정 ⑧ 약정 축 3배 경계 → make_fix3.py → 확인 리뷰 4차 pass(confirm-r4.md)
- [x] review.md 채움(확인 4차까지, fill_review.py)
- [x] 계약 검증 PASS
- [x] 사용자 결정: 승인 보류(v2.1 개정으로 대체, 11월 실행이 from-run 으로 이어받음). SpaceX 표시 이름은 11월 실행 init 때 run.json display_names 로
- [ ] (11월 실행 과제) confirm-r4 N2 Anthropic ⑧ 옛 2배 표현, N3 NVIDIA SB Energy 보증 문장. N1 은 v2.1 ⑧ 입력화에 흡수
