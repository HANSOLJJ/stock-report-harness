# TSMC Nasdaq API 컨센서스 원문 스냅샷 (2026-09-09)

- **출처 엔드포인트**: `https://api.nasdaq.com/api/analyst/TSM/earnings-forecast`
- **보조 엔드포인트**: `https://api.nasdaq.com/api/quote/TSM/info?assetclass=stocks`
- **조회 시각**: 2026-09-09T02:11:00Z (11:11 KST)
- **종목**: Taiwan Semiconductor Manufacturing Company Ltd. (NYSE: `TSM`)
- **주식 형태 (stockType)**: `American Depositary Shares`
- **상장 거래소**: `NYSE`
- **최근 거래가**: `$439.00 USD` (lastTradeTimestamp: Sep 8, 2026)
- **로컬 원자료 JSON**: `raw/nasdaq-tsm-earnings_forecast.json`, `raw/nasdaq-tsm-info.json`

---

## 1. 분기별 EPS 전망치 관측 데이터 (quarterlyForecast)

| 분기 종료 (fiscalEnd) | 회계분기 매핑 | 컨센서스 EPS (consensus) | 최고치 (high) | 최저치 (low) | 표본수 (noOfEstimates) | 4주 상향 (up) | 4주 하향 (down) |
|---|---|---|---|---|---|---|---|
| **Sep 2026** | 2026 Q3 (`0q`) | **$4.45** | $4.70 | $4.24 | 6개 | 0 | 0 |
| **Dec 2026** | 2026 Q4 (`+1q`) | **$4.68** | $4.93 | $4.22 | 5개 | 0 | 0 |
| **Mar 2027** | 2027 Q1 (`+2q`) | **$4.64** | $4.97 | $4.36 | 4개 | 0 | 0 |
| **Jun 2027** | 2027 Q2 (`+3q`) | **$5.10** | $5.49 | $4.90 | 4개 | 0 | 0 |
| **Sep 2027** | 2027 Q3 (`+4q`) | **$5.65** | $5.94 | $5.43 | 4개 | 0 | 0 |

- **차기 연속 4분기 산술 합산 (`0q ~ +3q`)**:
  $$4.45 + 4.68 + 4.64 + 5.10 = \mathbf{18.87\text{ (단위 추정)}}$$

---

## 2. 연간 EPS 전망치 관측 데이터 (yearlyForecast)

| 연도 종료 (fiscalEnd) | 회계연도 매핑 | 컨센서스 EPS | 최고치 | 최저치 | 표본수 | 비고 |
|---|---|---|---|---|---|---|
| **Dec 2026** | FY2026 | **16.52** | 17.38 | 13.08 | 9개 | Zacks 연간 수치와 정확히 일치 |
| **Dec 2027** | FY2027 | **21.09** | 23.77 | 16.71 | 9개 | Zacks 연간 수치와 정확히 일치 |
| **Dec 2028** | FY2028 | **25.92** | 28.83 | 20.39 | 3개 | |
| **Dec 2029** | FY2029 | **24.08** | 24.08 | 24.08 | 1개 | |

---

## 3. 단위 및 기준 검증 평가
1. **자료 확보 완료 (4/4 Fulfilled)**:
   - 이전 다른 공개 웹에서 결측되었던 **2027 Q1 (`+2q`)과 2027 Q2 (`+3q`) 수치가 Nasdaq 공개 API에서 최초로 확보**됨.
   - 단일 원천 내에서 차기 연속 4개 분기 EPS 수치가 완전하게 제공됨.
2. **단위 및 회계 기준 분리 유지 (`currency_and_gaap_unconfirmed`)**:
   - `stockType`은 `American Depositary Shares`로 명시되어 있으나, EPS 필드 자체의 통화 코드(`USD`) 및 회계 기준(`GAAP` vs `Non-GAAP`)은 JSON 내부에 명시적 필드로 제공되지 않음 (`EPS*` 표시).
   - 따라서 자료 확보(4/4 확보 완료)와 단위 검증(메타데이터 미확인에 따른 채점 보류)을 엄격히 분리함.
