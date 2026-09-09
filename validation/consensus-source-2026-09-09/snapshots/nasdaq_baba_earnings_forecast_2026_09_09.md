# Alibaba Nasdaq API 컨센서스 원문 스냅샷 (2026-09-09)

- **출처 엔드포인트**: `https://api.nasdaq.com/api/analyst/BABA/earnings-forecast`
- **보조 엔드포인트**: `https://api.nasdaq.com/api/quote/BABA/info?assetclass=stocks`
- **조회 시각**: 2026-09-09T02:11:00Z (11:11 KST)
- **종목**: Alibaba Group Holding Limited (NYSE: `BABA`)
- **주식 형태 (stockType)**: `American Depositary Shares each representing 8 Ordinary share`
- **상장 거래소**: `NYSE`
- **최근 거래가**: `$112.66 USD` (lastTradeTimestamp: Sep 8, 2026)
- **로컬 원자료 JSON**: `raw/nasdaq-baba-earnings_forecast.json`, `raw/nasdaq-baba-info.json`

---

## 1. 분기별 EPS 전망치 관측 데이터 (quarterlyForecast)

| 분기 종료 (fiscalEnd) | 회계분기 매핑 | 컨센서스 EPS (consensus) | 최고치 (high) | 최저치 (low) | 표본수 (noOfEstimates) | 4주 상향 (up) | 4주 하향 (down) |
|---|---|---|---|---|---|---|---|
| **Sep 2026** | FY27 Q2 (`0q`) | **$1.42** | $2.16 | $0.81 | 3개 | 2 | 1 |
| **Dec 2026** | FY27 Q3 (`+1q`) | **$1.89** | $2.75 | $1.31 | 3개 | 2 | 1 |
| **Mar 2027** | FY27 Q4 (`+2q`) | **$1.81** | $2.21 | $1.05 | 3개 | 2 | 0 |
| **Jun 2027** | FY28 Q1 (`+3q`) | **$2.45** | $3.13 | $1.76 | 2개 | 0 | 0 |
| **Sep 2027** | FY28 Q2 (`+4q`) | **$2.35** | $3.13 | $1.57 | 2개 | 1 | 0 |

- **차기 연속 4분기 산술 합산 (`0q ~ +3q`)**:
  $$1.42 + 1.89 + 1.81 + 2.45 = \mathbf{7.57\text{ (단위 추정)}}$$

---

## 2. 연간 EPS 전망치 관측 데이터 (yearlyForecast)

| 연도 종료 (fiscalEnd) | 회계연도 매핑 | 컨센서스 EPS | 최고치 | 최저치 | 표본수 | 비고 |
|---|---|---|---|---|---|---|
| **Mar 2027** | FY2027 | **5.88** | 8.26 | 4.92 | 6개 | FactSet 중간값($6.55) 대비 낮음 |
| **Mar 2028** | FY2028 | **8.61** | 13.29 | 6.80 | 6개 | |
| **Mar 2029** | FY2029 | **12.82** | 16.01 | 9.62 | 2개 | |

---

## 3. 단위 및 기준 검증 평가
1. **자료 확보 완료 (4/4 Fulfilled)**:
   - 이전 다른 공개 웹에서 결측되었던 **FY27 Q4 (`+2q`, Mar 2027)와 FY28 Q1 (`+3q`, Jun 2027) 수치가 Nasdaq 공개 API에서 최초로 확보**됨.
   - 단일 원천 내에서 차기 연속 4개 분기 EPS 수치가 완전하게 제공됨.
2. **단위 및 회계 기준 분리 유지 (`currency_and_gaap_unconfirmed`)**:
   - `stockType`은 `American Depositary Shares each representing 8 Ordinary share`로 보통주 8주 배율이 명시됨.
   - 그러나 EPS 필드의 통화 코드(`USD` 추정되나 명시 코드 부재) 및 회계 기준(`GAAP` vs `Non-GAAP`)은 JSON 내부에 명시적 필드로 제공되지 않음.
   - 따라서 자료 확보(4/4 확보 완료)와 단위 검증(메타데이터 미확인에 따른 채점 보류)을 엄격히 분리함.
