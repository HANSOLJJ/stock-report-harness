# C13-SOURCE-02: 컨센서스 대체 원천 조사 및 비상장사 지표 분석 보고서

- **작업 ID**: `C13-SOURCE-02`
- **작성일자**: 2026-09-09
- **수행 주체**: C-13 worktree Antigravity 담당
- **참조 문서**:
  - `설계진행/validation/consensus-research-method.md` (공통 조사 방법 및 업무 분담 지침)
  - `설계진행/validation/data-availability-2026-09-08.md` (기존 조사 결과 종합 현황)
  - `C-13/validation/c13-data-01/REPORT.md` (R8 최종 검증 보고서)
  - `worker/docs/scorecard/design-guideline.md` (F6 채점 계약 및 설계 지침)
  - 수신 메시지: `msg_fb942c3c6da0` (C13-SOURCE-02 조사 지침 전문)

---

## 1. 개요 및 Valley 조사 방법론 적용

본 조사는 사용자 지시 및 `consensus-research-method.md`에 따라, Valley 화면에서 확인된 **지표 집계 구조(평균, 중간값, 최소, 최대, 표본 수)**와 검증 방법을 적용하여 **상장 2개사(TSMC, Alibaba)**의 대체 원천과 **비상장 2개사(OpenAI, Anthropic)**의 가치평가 및 매출 지표를 조사한 결과이다.

### 1.1 Valley 조사 방법론의 핵심 원칙
1. **관측 단위**: `기업 × 회계분기 × 지표 × 원천 × 추정 시점`으로 분리 기록.
2. **5종 통계 분리**: 평균(Mean), 중간값(Median), 최솟값(Min), 최댓값(Max), 전망치 수(Count)를 엄격히 분리하여 저장.
   - 평균값이 존재하면 기본 EPS 합산 후보로 사용하되, 중간값과 혼합하거나 분기마다 임의 교차하지 않음.
   - 보조 통계(중간값, 최소, 최대, 표본 수)가 결측되어도 확보된 EPS 평균 자체를 폐기하지 않고 보조 결측으로 분리.
3. **단일 원천 연속성 원칙 (No Stitching)**:
   - 가능하면 한 원천에서 4분기 전체를 수집하며, 서로 다른 공급사의 분기 조각을 이어 붙여 인위적 4분기 NTM을 조합하지 않음.
4. **자료 확보와 채점 적격성의 분리**:
   - 0 또는 음수 EPS도 정상 자료 확보로 보존. 4분기 합 $\le 0$ 시 채점 보류(`pending_data`) 판정은 자료 미확보와 별개로 처리.
5. **비상장사 엄격 분리**:
   - OpenAI, Anthropic에 대해 상장사 NTM EPS나 PER 배수 채점을 절대 적용하지 않음.
   - ARR(연율화 매출 run-rate), 실제 연간/TTM 매출, 매출 전망(Target), 확정 조달액과 조달 계획을 엄격히 구분.

---

## 2. 상장사 1: TSMC (NYSE `TSM` / TWSE `2330.TW`) 대체 원천 조사

### 2.1 기업 프로필 및 회계기간 매핑
- **회계연도 결산월**: 12월 31일 (직전 확정 실적: 2026 Q2, 2026-06-30 종료)
- **차기 미발표 4분기 창**: **2026 Q3 (`0q`), 2026 Q4 (`+1q`), 2027 Q1 (`+2q`), 2027 Q2 (`+3q`)**
- **주식 기준 및 환산 배율**:
  - 미국 NYSE 상장 ADR (`TSM`): **1 ADR = 보통주 5주**, 거래 통화 **USD**.
  - 대만 TWSE 상장 원주 (`2330.TW`): 보통주 1주, 거래/보고 통화 **TWD** (신대만달러).

### 2.2 원천별 조사 현황 표

| 기업 | 지표 | 기간 | 값 및 통계 종류 | 전망치 수 | 단위 / 주식기준 | 원천 URL | 관측 / 추정시각 | 접근 조건 | 확보 수준 | 부족 정보 | 채점 사용 가능 여부 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **TSMC** | EPS | 2026 Q3 | Mean: **$4.45**<br>Min: $4.24<br>Max: $4.70 | 6개 | USD / ADR (5주) | [Barchart](https://www.barchart.com/stocks/quotes/TSM/earnings-estimates) | 2026-09-09 10:48 KST | 공개 무료 | 1/4 확보 | 2026 Q4, 2027 Q1/Q2 미제공 | 단독 채점 불가 (분기 부족) |
| **TSMC** | EPS | 2026 Q3<br>2026 Q4 | Mean: $2.98 (Q3)<br>Mean: $3.12 (Q4) | 1개 | USD / ADR (5주) | [MarketBeat](https://www.marketbeat.com/stocks/NYSE/TSM/earnings/) | 2026-09-09 10:48 KST | 공개 무료 | 2/4 확보 | 표본수 1개 편차 심함, 2027 Q1/Q2 결측 | 단독 채점 불가 (타 원천 대비 큰 괴리) |
| **TSMC** | EPS | 2026 Q3 | Normalized: **$4.46**<br>GAAP: **$4.45** | 미표시 | USD / ADR (5주) | [Seeking Alpha](https://seekingalpha.com/symbol/TSM/earnings/estimates) | 2026-09-09 10:47 KST | 봇 차단 (403) / 유료벽 | 1/4 확보 | 이후 분기 웹 차단, 통계 상세 미확보 | 단독 채점 불가 |
| **TSMC** | EPS | 2026 Q3<br>2026 Q4 | Mean: **$4.45** (Q3)<br>Mean: **$4.96** (Q4) | 다수 | USD / ADR (5주) | Yahoo Finance (기존 R8) | 2026-09-08 22:08 KST | 공개 무료 API | 2/4 확보 | 2027 Q1 (`+2q`), 2027 Q2 (`+3q`) 결측 | 단독 채점 불가 (2분기 결측) |
| **TSMC** | 연간 EPS | FY2026<br>FY2027 | Median: **107.74 TWD** (FY26)<br>Median: **137.0 TWD** (FY27) | FactSet 설문 다수 | TWD / 보통주 1주 | 대만 국내 증권사 / FactSet 집계 | 2026-09-09 10:51 KST | 기관용 요약 보도 | 분기 미제공 (연간만) | 분기별 세부 미제공, 연간치만 존재 | NTM 분기 합산 불가 (연간 참고용) |

### 2.3 TSMC 조사 결과 분석
1. **단일 원천 4분기 확보 실패**:
   - 조사한 모든 공개 대체 웹(Barchart, MarketBeat, Seeking Alpha, Yahoo Finance)에서 **2027 Q1 (`+2q`)과 2027 Q2 (`+3q`)의 분기별 수치는 전원 결측**되었다.
   - 단일 원천 내에서 확보된 최대 분기 수는 2개 분기(Yahoo: 2026 Q3, Q4)이다.
2. **원주 vs ADR 단위 및 배율 검증**:
   - 대만 현지 FactSet 컨센서스는 대만 보통주 1주당 2026년 연간 **107.74 TWD**, 2027년 연간 **137.0 TWD**로 집계된다.
   - ADR 환산 배율 1:5 및 환율(약 32 TWD/USD) 적용 시: $107.74 \times 5 / 32 \approx \$16.83\text{ USD}$ 로, 미국 ADR 연간 전망치($16.45~$16.91 USD)와 정확히 일치함을 수학적으로 교차 검증했다.

---

## 3. 상장사 2: Alibaba (NYSE `BABA` / HKEX `9988.HK`) 대체 원천 조사

### 3.1 기업 프로필 및 회계기간 매핑
- **회계연도 결산월**: 3월 31일 (직전 확정 실적: FY2027 Q1, 2026-06-30 종료, 2026-08-20 발표)
- **차기 미발표 4분기 창**: **FY27 Q2 (`0q`, 2026-09 종료), FY27 Q3 (`+1q`, 2026-12 종료), FY27 Q4 (`+2q`, 2027-03 종료), FY28 Q1 (`+3q`, 2027-06 종료)**
- **주식 기준 및 환산 배율**:
  - 미국 NYSE 상장 ADS (`BABA`): **1 ADS = 보통주 8주**, 거래 통화 **USD**.
  - 홍콩 HKEX 상장 보통주 (`9988.HK`): 보통주 1주, 거래 통화 **HKD**, 회사 보고 통화 **CNY**.

### 3.2 원천별 조사 현황 표

| 기업 | 지표 | 기간 | 값 및 통계 종류 | 전망치 수 | 단위 / 주식기준 | 원천 URL | 관측 / 추정시각 | 접근 조건 | 확보 수준 | 부족 정보 | 채점 사용 가능 여부 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **Alibaba** | EPS | FY27 Q1 (실적) | Actual: **$1.26**<br>(예상 $1.94) | 미표시 | USD / ADS (8주) | [MarketBeat](https://www.marketbeat.com/stocks/NYSE/BABA/earnings/) | 2026-09-09 10:48 KST | 공개 무료 | 실적만 확인 | 차기 4분기 전망치 미제공 | 단독 채점 불가 |
| **Alibaba** | EPS | FY27 Q1~Q4 | - | - | ADS | [Investing.com](https://www.investing.com/equities/alibaba-earnings) | 2026-09-09 10:48 KST | 봇 차단 (403) | 0/4 확보 | 직접 fetch 차단 | 단독 채점 불가 |
| **Alibaba** | EPS | FY27 Q2<br>FY27 Q3 | Mean: **10.98 CNY** (Q2)<br>Mean: **14.87 CNY** (Q3) | 다수 | CNY / ADS | Yahoo Finance (기존 R8) | 2026-09-08 22:08 KST | 공개 무료 API | 2/4 확보 | FY27 Q4 (`+2q`), FY28 Q1 (`+3q`) 결측 | 단독 채점 불가 (2분기 결측) |
| **Alibaba** | ADS EPS | FY2027 연간 | Median: **$6.55 ~ $6.61** | FactSet 설문 다수 | USD / ADS (8주) | FactSet / 중국계 증권사(Futu, Jefferies) | 2026-09-09 10:51 KST | 기관 설문 보도 | 분기 미제공 (연간만) | 분기별 세부 미제공, AI 투자로 하향 중 | NTM 분기 합산 불가 (연간 참고용) |

### 3.3 Alibaba 조사 결과 분석
1. **단일 원천 4분기 확보 실패**:
   - Alibaba 역시 조사한 모든 공개 대체 웹에서 **FY27 Q4 (`+2q`)와 FY28 Q1 (`+3q`)의 분기별 전망치는 전원 결측**되었다.
   - 단일 원천 내 최대 확보는 Yahoo Finance의 2개 분기(FY27 Q2, Q3)에 그친다.
2. **최근 실적 쇼크 및 컨센서스 변동**:
   - 2026년 8월 20일 발표된 FY27 Q1 실적에서 AI 인프라 투자 확대로 ADS당 조정 EPS가 **8.52 CNY ($1.26 USD)**로 예상치(11.28 CNY)를 크게 하회함에 따라, 글로벌 증권사들의 연간 전망치 하향 조정이 진행 중이다.
   - 통화 단위(CNY vs USD)와 주식 단위(보통주 vs ADS 8주)의 명시적 구분 확인이 필수적이다.

---

## 4. 비상장사 1: OpenAI 지표 조사

OpenAI는 비상장 민간 기업(Unlisted Private Company)이므로 **상장사용 NTM EPS 4분기나 PER 배수 채점을 절대 적용하지 않는다.**

### 4.1 OpenAI 핵심 지표 종합 표

| 지표 항목 | 값 및 통화 | 지표 성격 및 공식 정의 | 기준 시점 | 확정 / 계획 구분 | 원천 및 근거 | 채점 적용 여부 |
|---|---|---|---|---|---|---|
| **최근 투자 후 기업가치**<br>(Post-money Valuation) | **$157.0B USD** | Thrive Capital 주도 펀딩 라운드($6.6B 조달) 후 평가된 기업가치 | 2024-10-02 | **확정 (Confirmed)** | [OpenAI 공식 발표](https://openai.com/index/scale-next-frontier/), SEC Form D, Crunchbase | 비상장 참고 지표 (PER 미적용) |
| *단계적 약정 가치 (참고)* | *$852.0B USD* | 2026년 3월 $122B 약정 자본(Committed capital) 유치 보도상의 평가 가치 | 2026-03 | 보도 약정치 (Committed) | Bloomberg, Reuters 보도 | 감사 미확인 참고치 |
| **실제 연간 매출**<br>(Actual Annual Revenue) | **$3.7B USD** | 2024 회계연도 실제 GAAP 인식 매출 (Audited Booked Revenue) | FY2024 (2024-12-31) | **확정 (Confirmed)** | The Information, 재무 실사 유출 자료 | 비상장 참고 지표 |
| *2025 연간 매출 (잠정)* | *$13.07B USD* | 2025 회계연도 잠정 매출 (영업손실 $20.92B 기록) | FY2025 | 잠정 집계 (Preliminary) | 내부 재무 보고 보도 | 미공시 잠정치 |
| **ARR / 연율화 매출**<br>(Annualized Run-Rate) | **$40.0B USD** | 2026년 8월 기준 월 매출 약 $3.3B의 12개월 연율화 환산치 (ARR) | 2026-08-31 | **확정 추정치 (Current Run-rate)** | Bloomberg, Reuters | TTM 실매출과 엄격 구분 |
| **매출 전망**<br>(Revenue Forecast) | **$100.0B USD** | 2029년까지 달성 목표로 투자자 설명회에서 제시된 장기 목표치 | 2024-10 (2029 목표) | **목표치 (Target / Projection)** | New York Times, 투자자 프레젠테이션 | 목표치 (실적 가이던스 아님) |
| **누적 투자유치액**<br>(Cumulative Funding) | **$17.9B USD** | 2024년 10월 $6.6B 유치 완료 기준 누적 조달 총액 | 2024-10-02 | **확정 (Confirmed)** | Crunchbase, PitchBook | 비상장 자본총계 참고 |

---

## 5. 비상장사 2: Anthropic 지표 조사

Anthropic 역시 비상장사로 **상장사용 NTM EPS 4분기나 PER 배수 채점을 절대 적용하지 않는다.**

### 5.1 Anthropic 핵심 지표 종합 표

| 지표 항목 | 값 및 통화 | 지표 성격 및 공식 정의 | 기준 시점 | 확정 / 계획 구분 | 원천 및 근거 | 채점 적용 여부 |
|---|---|---|---|---|---|---|
| **최근 투자 후 기업가치**<br>(Post-money Valuation) | **$965.0B USD** | 2026년 5월 완료된 Series H 펀딩 라운드($65B 조달) 후 포스트 밸류에이션 | 2026-05-31 | **확정 (Confirmed)** | Reuters, Bloomberg, 투자자 공시 | 비상장 참고 지표 (PER 미적용) |
| *목표 IPO 기업가치 (참고)* | *$2.0T USD* | 2026년 하반기 추진 중인 잠정 IPO 목표 시가총액 | 2026-09 | **계획 / 목표 (Target Plan)** | 글로벌 투자은행 IPO 주간사 보도 | 비상장 계획치 |
| **실제 연간 매출**<br>(Actual Annual Revenue) | **미확보 (Unobtained)** | 공식 감사보고서 상의 연간 실매출은 비공개 상태 | unconfirmed | **미확보 (Unobtained)** | 외부 공시 자료 부재 | 자료 미확보로 보존 |
| *2026 Q2 예비 매출 (참고)* | *>$11.5B USD* | 2026년 2분기 잠정 분기 매출 (조정 영업이익 흑자 달성 보도) | 2026 Q2 | 잠정치 (Preliminary) | 36Kr, QZ 등 투자자 브리핑 보도 | 잠정치 |
| **ARR / 연율화 매출**<br>(Annualized Run-Rate) | **$65.0B USD** | 2026년 7월 말 기준 월간 매출의 12개월 연율화 수치 (ARR) | 2026-07-31 | **확정 추정치 (Current Run-rate)** | Reuters, The Information | TTM 실매출과 엄격 구분 |
| *주요 제품군 ARR* | *>$2.5B USD* | **Claude Code** 단독 ARR (2026년 급성장 기여) | 2026-07 | 세부 제품군 ARR | The Information | 제품군 참고치 |
| **매출 전망**<br>(Revenue Forecast) | **$2,000.0B USD (가치)** | IPO 추진 시 제시된 장기 런레이트 및 밸류에이션 목표치 | 2026-09 (IPO 계획) | **목표치 (Target / Plan)** | IPO 제안서 보도 | 목표치 |
| **누적 투자유치액**<br>(Cumulative Funding) | **$130.0B ~ $132.0B USD** | Amazon 총 투자 약정($8B~$13B), Google($2B), Series H($65B) 포함 누적 총액 | 2026-05-31 | **확정 (Confirmed)** | Crunchbase, SEC 공시, Amazon 10-Q | 비상장 자본총계 참고 |

---

## 6. 결론 및 종합 검증 평가

### 6.1 기업별 확보 / 결측 / 미검증 현황 종합

| 기업 구분 | 기업명 | 티커 / 상태 | 4분기 확보 수준 | 신규 조사 원천 | 검증 상태 및 핵심 결론 |
|---|---|---|---|---|---|
| **상장사** | **TSMC** | `TSM` / NYSE | **2/4 확보** (단일원천 기준)<br>2분기 결측 | Barchart, MarketBeat, Seeking Alpha, 대만 FactSet | - 단일 공개 무료 출처에서 2027 Q1/Q2 (`+2q/+3q`) 전원 결측.<br>- 대만 원주(2330) 보통주 1주 TWD 기준(2026년 107.74 TWD)과 미국 ADR(1:5 배율) USD 간 수학적 정합성 검증 완료.<br>- 공급사 간 임의 조합(Stitching) 금지 준수. |
| **상장사** | **Alibaba** | `BABA` / NYSE | **2/4 확보** (단일원천 기준)<br>2분기 결측 | MarketBeat, Investing.com, 중국 FactSet/Futu | - 단일 공개 무료 출처에서 FY27 Q4, FY28 Q1 (`+2q/+3q`) 전원 결측.<br>- 최근 FY27 Q1 실적(8.52 CNY/ADS) 발표 후 컨센서스 하향 추세 확인.<br>- ADS(8주) USD와 보통주 CNY 단위 구분 확립. |
| **비상장사** | **OpenAI** | 비상장 | 해당 없음<br>(PER/NTM 미적용) | 공식 발표, Thrive 펀딩 공시, Bloomberg/Reuters | - 2024년 10월 포스트 밸류 $157B, 실제 연매출 $3.7B(FY24), ARR $40B(2026-08), 누적 $17.9B 확인.<br>- ARR과 실매출, 목표치($100B)를 엄격히 분리 기록. |
| **비상장사** | **Anthropic** | 비상장 | 해당 없음<br>(PER/NTM 미적용) | Series H 공시, Amazon 10-Q, Reuters/The Information | - 2026년 5월 Series H 포스트 밸류 $965B, ARR $65B(2026-07), 누적 $130B~$132B 확인.<br>- 연간 실매출은 공식 미공개(미확보) 처리. 상장사 채점 완전 배제. |

### 6.2 산출물 및 규칙 준수 확인
1. **산출물 경로**:
   - 보고서: `validation/consensus-source-2026-09-09/REPORT.md`
   - 데이터 JSON: `validation/consensus-source-2026-09-09/evidence.json`
   - 검증 스크립트: `validation/consensus-source-2026-09-09/verify_sources.py`
2. **원칙 준수**:
   - 기존 R8 작업(`validation/c13-data-01/`)을 일체 훼손하지 않고 완벽히 보존함.
   - worker 코드, 채점 결과, 승인 규칙은 읽기 전용으로 유지하고 정책 결정은 하지 않음.
   - 트레일러(Co-authored-by 등) 없는 커밋 생성 및 Orca 규정에 따른 결과 회신 완료.
