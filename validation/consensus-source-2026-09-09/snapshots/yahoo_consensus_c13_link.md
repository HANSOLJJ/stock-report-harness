# 기존 C13-DATA-01-R8 관측치 원문 연계 스냅샷

- **참조 태스크**: `C13-DATA-01-R8`
- **참조 파일**: `validation/c13-data-01/evidence.json`
- **원천**: Yahoo Finance Analysis API (`https://finance.yahoo.com/quote/TSM/analysis/`, `https://finance.yahoo.com/quote/BABA/analysis/`)
- **수집 기준 시각**: 2026-09-08T22:08:00+09:00

---

## 1. TSMC 관측치 (Yahoo Finance)
- 주가: $428.91 USD
- `0q` (2026 Q3): 평균 **$4.45297 USD** (표본 5개)
- `+1q` (2026 Q4): 평균 **$4.95689 USD** (표본 4개)
- `+2q` (2027 Q1): 결측 (`None`)
- `+3q` (2027 Q2): 결측 (`None`)
- `+1y` (FY2027 연간): 평균 $21.86117 USD
- `forwardPE`: 19.56251, `forwardEps`: $21.9251 USD

## 2. Alibaba 관측치 (Yahoo Finance)
- 주가: $113.24 USD
- `0q` (FY27 Q2): 평균 **10.98 CNY** (통화: CNY)
- `+1q` (FY27 Q3): 평균 **14.87 CNY** (통화: CNY)
- `+2q` (FY27 Q4): 결측 (`None`)
- `+3q` (FY28 Q1): 결측 (`None`)
- `+1y` (FY2028 연간): 평균 62.73 CNY
- `forwardPE`: 12.196245, `forwardEps`: $9.284824 USD

## 3. 검증 연계 소견
- 조사 대상 두 기업 모두 공개 무료 채널에서는 차기 2개 분기만 수신되며, 차차기 2개 분기(`+2q`, `+3q`)가 결측됨.
- 본 신규 조사(C13-SOURCE-02)의 타 대체 원천(Barchart, MarketBeat 등)에서도 해당 2개 분기가 결측됨을 교차 확인하였음.
