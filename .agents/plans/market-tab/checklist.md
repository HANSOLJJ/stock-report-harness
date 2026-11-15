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

## 추이 (2026-11-15 2차)

- [x] 하네스: market_now·스키마·MARKET_ROWS 에 BAA10Y(`baa_spread`) 추가, 테스트
- [x] 하네스: market_live.js 를 시계열 JSON 읽기 + 차트(1년·3년·10년)로 바꾸고, 서버가 쓸 시계열 빌더 함수를 같은 파일에 둔다. Node 테스트
- [x] finance: server/lib/market-series.js(매일 수집, data/market-series.json), /reports/market-series.json 경로
- [x] finance: 로컬에서 수집·경로 확인, node --check, lint(실원천 11곳 실패 0, 라우터 200·없을 때 404)
- [x] 하네스 렌더 확인(같은 경로로 시계열을 낸 임시 서버), 320px·기간 버튼 44px·10년 범위·폭 바뀜에도 기간 유지
- [ ] 커밋 두 곳, finance main 푸시, 맥미니 git pull·pm2 restart, 공개 주소에서 JSON 확인
- [~] vast.ai 프록시 허용 목록: 공개 리포트가 /api 를 못 불러 이 방식을 버렸다
