# F6-H 공급원별 일괄 조사 재검토

- 대상 커밋: `2bc6274`
- 판정: 조사 PASS, 단일 공급원 정식 채택 불가

6개 공급원을 12개 상장사에 일괄 적용한 결과 최고 F6-H 충족률은 Nasdaq 9/12와 Finnhub 9/12(75%)였다. StockAnalysis·FMP·TradingView·Yahoo/Valley는 0/12로 정식 조건을 충족하지 못했다.

Nasdaq은 2E와 표본 통계를 제공하지만 2A의 TSMC·Alibaba ADR/통화 기준과 SPCX 실적 부족이 남는다. Finnhub도 TSMC·Alibaba 단위와 SPCX 결측이 병목이다. 모든 공급원에서 `asOf` point-in-time과 외부 재배포 권한이 미확정이다. 따라서 종목별로 서로 다른 사이트를 선택해 조합하는 방식은 비교 기준을 깨뜨리므로 배제한다.

현재 12개사 전체에 동일한 2A+2E 기준을 충족하는 공급원은 없다. F6-H 자동 점수 활성화는 보류하고, 허가·기준 통일·SPCX 자료 확보가 완료된 단일 공급원이 생길 때 재검토한다.
