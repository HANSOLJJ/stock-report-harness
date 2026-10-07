# 체크리스트 — 근거 사슬(URL) · 판단 정정 · 문서 정리

## A. 문서·표기
- [x] guide.md 흐름도·시퀀스의 근거 확정·제안 반영 주체를 에이전트로
- [x] structure.md 수정 경로의 옛 역할 설명
- [x] guide.md 11월 예시가 최신 실행(rescore)을 이어받게
- [x] 리포트 함정 범위 표기를 규칙에서 읽은 실제 하한으로(리드·카드)
- [x] ⑥ 가격의 뜻 설명(리드 또는 방법 탭)
- [x] 테스트 통과 → 커밋

## B. 근거 사슬 장치
- [x] evidence 스키마: 선택 키 `locator`
- [x] validate: v1.9 이상 방향 칸 줄마다 표지, 표지 근거는 confirmed·URL·본문 발췌·locator
- [x] revise_judgment 쓰는 시점 강제
- [x] 렌더러: 표지 → 인용 근거 링크(HTML), 초안 표기
- [x] 승인 페이지 표시 확인
- [x] 테스트 신규·수정, Python·node 통과
- [x] guide 5.6·AGENTS.md·스킬(score-research·score-review·score-collect)·.agents 사본
- [x] 커밋

## C. 승인 취소(사용자)
- [x] 사용자가 승인 페이지에서 승인 취소

## D. 원문 연결
- [x] 지시서 LINK-INSTRUCTIONS.md
- [x] 서브에이전트 7묶음 산출 + 2차 탐색 2묶음
- [x] 기계 검사(URL·발췌·위치·사실 보존·표지 형식, 변조 사본으로 검사기 확인)
- [x] evidence·sources 기록, confirm
- [x] propose → proposal 반영, 위반 0
- [x] 원문 못 찾은 사실 목록과 점수 영향 정리

## E. 판단 정정
- [x] oracle.F7·openai.F5 Stargate
- [x] anthropic.F2 잣대 일치
- [x] TEN-RC-05·TEN-RC3-04 판정
- [x] Amazon 런웨이 표시

## F. 재계산·리뷰
- [x] research → calculate → draft, 점수 변화표
- [x] review-template, 4영역 1차 리뷰
- [x] 수정 한 묶음, 확인 리뷰, pass
- [x] validate_report_contract, "승인 대기" 보고

## G. 빌드(승인 뒤)
- [ ] build_report → --require-html → 화면 확인 → 커밋
