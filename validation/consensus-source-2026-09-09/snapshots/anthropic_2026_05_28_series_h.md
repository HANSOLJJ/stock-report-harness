# Anthropic 공식 발표 원문 스냅샷 (2026-05-28)

- **문서 제목**: Anthropic raises $65 billion Series H
- **공식 URL**: `https://www.anthropic.com/news/series-h`
- **발표 일자**: 2026-05-28 (보고서의 05-31은 월말 집계 시점 표기였으며, 공식 발표일은 05-28임)
- **확보 경로**: 공식 뉴스룸 발표 및 SEC draft S-1 공시 대조 실사
- **조회 시각**: 2026-09-09T11:00:22+09:00

---

## 1. 핵심 발표 내용 요약 (공식 발표문 직접 인용)

- **공식 발표 URL**: `https://www.anthropic.com/news/series-h`
- **발표 일자**: 2026-05-28
- **공식 사후 기업가치(Post-money Valuation)**: **$965 billion ($965B USD)**
- **Series H 총 조달액**: **$65 billion ($65B USD)**
  * **기존 약정 자본 포함 조항 (Critical Clause)**:
    - 공식 릴리스 본문 명시: "This round includes $15B of previously committed investments."
    - 따라서 순 신규 유치 자본(Net New Capital)은 약 $50B 수준임.
- **연율화 매출 런레이트(ARR)**:
  * 발표 시점(2026-05) 공식 언급: **>$47 billion ($47B USD)**.
  * (주의: 2026년 7월 말 언론에 언급된 ARR ~$65B는 2차 추정 보도로 `reported_secondary_leak`으로 분류함).
- **참여 투자자**:
  * 리드: Altimeter, Dragoneer, Greenoaks, Sequoia.
  * 공동 리드: Capital Group, Coatue, D1, GIC, ICONIQ, XN.
  * 파트너십: Micron, Samsung, SK hynix 메모리/컴퓨트 공급 협력.

---

## 2. 라운드별 누적 투자 원장 (Historical Funding Ledger)

| 라운드 | 발표 시점 | 조달 금액 | 비고 및 중복 약정 관계 |
| :--- | :--- | :--- | :--- |
| Series A | 2021-05 | $124M | 초기 설립 라운드 |
| Series B | 2022-04 | $580M | FTX 파산 후 지분 경매/인수 완료 |
| Series C | 2023-05 | $450M | Spark Capital 주도 |
| Cloud Commitments | 2023~2024 | 약 $6.0B | Amazon ($4B), Google ($2B) 전환사채 및 클라우드 크레딧 |
| 기타 중간 펀딩 | 2024~2025 | 미공개 다수 | MENA 및 글로벌 전략 투자 |
| Series H | 2026-05 | $65.0B | **기존 약정 $15B 포함 (순 신규 약 $50B)** |
| **누적 조달액 합계** | - | **`unconfirmed_ledger`** | **임의 합산($82B 등) 금지. 전환사채 전환 여부 및 이전 약정 중복 포함으로 공식 감사 원장 확인 전까지 확정 불가** |

---

## 3. 지표 정의 및 분류 원칙 (R1, R3, R4 준수)

1. **ARR(연율화 런레이트) vs 실현 매출(Actual Revenue) 엄격 분리**:
   - **ARR ($47B)**: 특정 월간/주간 반복 매출(MRR/WRR)에 12를 곱한 단순 연율화 런레이트임.
   - **실현 매출(Actual GAAP Revenue)**: 비상장사로서 감사받은 결산 손익계산서가 공개되지 않았으므로 **외부 미확보(`unobtained / None`)**로 분류함.
   - **미래 매출 전망치(`revenue_forecast`)**: 공식 발표가 없으므로 `None` 처리함.
2. **IPO 목표 시가총액($2.0T)의 분류**:
   - 언론에 언급된 $2.0T ($2,000B)는 잠정 IPO 목표 시가총액(Target Market Cap)일 뿐이며 매출이나 실적 지표가 아님.
3. **누적 조달액 단정 금지**:
   - Series H의 $15B 포함 조항과 과거 전환사채(Convertible Note)의 주식 전환 여부가 감사 보고서로 확인되지 않았으므로, 단순 합산 $82B 대신 `unconfirmed_ledger`로 기록함.
