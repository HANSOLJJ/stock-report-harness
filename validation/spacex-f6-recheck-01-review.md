# SPACEX-F6-RECHECK-01 재검토 및 결정

- 검토 대상: worker 커밋 `ae77787`
- 판정: `pass`

## 검토 결과

- `SPCX`가 NASDAQ 상장 보통주이고 현재 ticker·exchange·basis 보완이 승인 해시에 영향을 주지 않는다는 점을 확인했다.
- Finnhub `calendar/earnings`의 SPCX 조회가 빈 배열이며 coverage `0/4`인 점을 확인했다. F6 자동 점수나 2분기 proxy는 생성하지 않는다.
- `spacex-xai`의 기존 관측·판단이 합산 범위이므로 company_id와 라벨을 현재 실행에서 SpaceX 단독으로 바꾸지 않는다.

## 결정 사항

1. 현재 승인 실행은 `spacex-xai` 합산 범위를 유지한다. SpaceX 단독 전환은 관측·판단을 새로 분리하는 별도 실행에서만 한다.
2. xAI는 별도 티커와 독립 재무자료가 확인되기 전까지 별도 기업 점수를 만들지 않고 합산 범위의 구성요소 메모로 남긴다.
3. SPCX는 첫 실적 발표일이 공식 공시된 뒤 Finnhub 캘린더를 재조회한다. 그 전에는 반복 조회하지 않는다.
4. F6 재개 전 기준선 주가·시가총액의 출처를 SPCX 단독 기준으로 재검증한다. 검증 전에는 기존 legacy 값을 F6 입력으로 승격하지 않는다.
