# SPACEX-EPS-SOURCE-03 재검토

- 검토 대상: worker 커밋 `7526446`
- 판정: `pass`

## 검토 결과

- Nasdaq API에서 SPCX의 2026 Q3부터 2027 Q2까지 4개 분기 컨센서스와 최고·최저·추정치 수를 확보한 사실을 승인한다.
- SEC fiscalYearEnd와 XBRL USD/shares로 분기 창과 실적 기준을 대조한 점을 승인한다.
- Finnhub은 SPCX를 일부 endpoint에서 커버하지만 calendar/earnings에는 행이 없다는 정정으로 이전의 공급사 전체 미커버 판정을 대체한다.

## 결정

1. Nasdaq 채택 전 GAAP/비GAAP 기준, 추정 갱신 시각, 이용 약관·요청 한도를 먼저 확인한다. 세 항목 중 하나라도 미확인이면 관측 등록과 F6 점수화를 하지 않는다.
2. 위 게이트를 통과한 뒤 Nasdaq 동일 endpoint로 12개사 확장 조사를 수행한다. 기업별 회계 캘린더·통화·ADR/ADS·주식 기준을 별도로 검증하고 공급사를 섞지 않는다.
3. 이번 보고서의 1.16 EPS 합계와 132.3 PER는 후보 계산일 뿐 승인 점수가 아니다.
