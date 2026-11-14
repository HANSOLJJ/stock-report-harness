# 지금 시장 탭 체크리스트

- [x] 모양 결정: 리포트 안 탭, 기준일 값·지금 값·변화 (2026-11-15)
- [ ] 시작 시점 결정
- [x] 원천 접근 확인: FRED(fredgraph.csv 키 없음, API 는 키 필요), vast.ai bundles(키 없음), OpenRouter models(키 없음, CORS 허용). DRAM·HBM 현물, CDS 는 공개 원천이 없어 뺐다
- [x] collect --kind market 이 기준일 값을 `_market` 관측으로 찍기(market_now.py), diff 허용
- [x] 지금 값 경로: 공개 사이트의 기존 /api/proxy(FRED 키 주입)와 OpenRouter 직접 호출. 새 서버 코드 없음
- [ ] vast.ai 를 공개 사이트 프록시 허용 목록에 넣을지(finance 저장소, 사용자 결정)
- [x] 초안 국면 절과 HTML 국면 탭에 표, 지금 값 받기 버튼(44px, aria-live), 320px 넘침 없음. 관측 없는 실행은 바이트 불변
- [x] 테스트: tests/test_market_now.py, tests/node/market_live.test.js(같은 고정 자료)
- [ ] 다음 실행에서 collect --kind all 로 기준일 값을 찍고 빌드·배포
