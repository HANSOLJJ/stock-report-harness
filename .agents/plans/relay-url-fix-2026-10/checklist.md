# 체크리스트 — 중계 주소·제목뿐인 근거 막기

- [x] evidence_lib.fetch_bytes: data·headers 인자
- [x] collect_news: is_google_relay_url, resolve_google_news_url
- [x] stages: resolve_source_urls(slug), confirm 거부, research 거부, 판단 "제목만" 거부
- [x] validate: excerpt_is_title / unread_evidence_violation / unread_evidence_findings
- [x] schema: sources 선택 키 relay_url
- [x] CLI resolve-urls (실주소 시험: Fortune 기사로 풀림)
- [x] 테스트 15건 추가(tests/test_relay_url_guard.py), v2.0 시험 자료를 원문 주소로(before_confirm) → Python 1,474·Node 24 통과
- [x] 10월 승인본 계약 검증 그대로 통과
- [x] 스킬(score-research·score-review)·AGENTS·guide 문서
- [x] 커밋(코드·문서 나눠서)
- [ ] 다음 실행: 10월 근거를 이어받으면 research 가 83건(중계 주소 47·제목뿐 30·'제목만' 판단 6)을 막는다 → resolve-urls 뒤 원문 읽고 발췌 채우기
