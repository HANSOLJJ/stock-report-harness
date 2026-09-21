# 수정 이력 — NTM-SOURCE-05

기준일 2026-09-09. 원 지시 `msg_98cbddbdac15`. 선행 산출물 커밋 `a74c15e`.

## 원자료 보존 원칙

`a74c15e` 로 커밋한 수집 원자료는 **수정하지 않았다.** 이번 조사의 새 조회는 별도 디렉터리 `raw-05/` 와 별도 파일(`sec-05.json`, `vendor-meta-05.json`, `basis-verification-05.json`, `contract-fields-05.json`)에 별도 시점으로 기록했다.

| 파일 | 상태 |
|---|---|
| `raw/` (Nasdaq·StockAnalysis·TradingView 스냅샷 74건) | 무변경. 읽기 전용으로 재사용 |
| `collect-raw.json`, `collect-extra.json` | 무변경 |
| `evidence.json`, `tables.md`, `verify-output.txt` | 무변경 |
| `REPORT.md` | §5.1 만 개정 (아래 R1) |
| `raw-05/`, `sec-05.json`, `vendor-meta-05.json`, `basis-verification-05.json`, `contract-fields-05.json`, `REPORT-05.md`, 이 파일 | 신규 |

## R1 — REPORT.md §5.1 단정 철회 (2026-09-09)

**철회한 문장**

> 기간은 일치하므로 기간 오정렬이 아니라 조정(adjusted) 정의 차이다.

**철회 사유**

기간 일치는 "기간 불일치" 가설 하나만 배제한다. 주식 기준(기본/희석), 통화, 분할 조정, 추정 갱신 시점 등 다른 원인은 배제하지 않았는데도 원인을 조정 정의 차이로 단정했다. 배제한 가설 하나로 원인을 확정한 오류다. 지적 출처는 설계진행 `msg_1ade3bfe39e8`.

**대체 서술**

원인을 미확인으로 되돌리고, SEC 공시 대조로 확인된 범위만 남겼다. 확인된 것은 (a) StockAnalysis `eps` 열이 SEC GAAP 희석과 10/10 일치, (b) Nasdaq 확정 실적 열이 GAAP 희석도 기본도 아님, (c) Nasdaq 의 조정 규칙 정의와 추정 열의 기준 동일성은 미확인이라는 세 가지다.

**함께 정정한 것**

초판의 "Meta·Alphabet·Microsoft·NVIDIA·SpaceX 는 원천 간 일치한다" 중 NVIDIA 부분을 정정했다. NVIDIA 의 Nasdaq 값 2.22 는 StockAnalysis **조정열**과 일치할 뿐이며 GAAP 희석 2.46 과는 다르다. 초판은 비교 대상 열을 명시하지 않아 일치 여부를 잘못 일반화했다.

**영향 범위**

§5.1 의 실무적 결론(원천 혼합 금지, 4분기 묶음은 Nasdaq 원천 그대로만 유효)은 유지된다. 이 결론은 원인 규명이 아니라 값이 다르다는 관측만으로 성립하기 때문이다. 표 A~F 의 수치, 확보 수준 4/4, 채점 적격성 미검증 판정은 변경 없다.

## R2 — 미확인 항목의 재분류 (2026-09-09)

NTM-SOURCE-04 가 "미확인"으로 묶어 둔 항목 중 아래는 이번에 근거를 확보해 재분류했다. 상세는 `REPORT-05.md` §2 다.

| 항목 | NTM-SOURCE-04 | NTM-SOURCE-05 | 새 근거 |
|---|---|---|---|
| 통화 | 미확인 | 충족 | SEC XBRL 단위 `USD/shares`, StockAnalysis 선언 통화 `USD` |
| 보통주/ADR | 미확인 | 충족 | SEC 등록 법인·티커·거래소, StockAnalysis `adrPriceDivisor` 미설정 |
| 분할 조정 | 미확인 | 충족(관측 범위 내) | SEC 공시에서 같은 분기 재보고값 불일치 0건 |
| 회사 공식 회계기간 | 미확인 | 충족 | SEC `fiscalYearEnd` 와 분기 `start~end` 대조 |
| GAAP/조정 기준 | 미확인 | 부분 확인 | Nasdaq 이 GAAP 희석·기본 아님을 확정. 조정 규칙 자체는 미확인 |
| 추정치 스냅샷 시점 | 미확인 | 미확인 유지 | 4분기 원천(Nasdaq) `asOf`=null. StockAnalysis 는 제공하나 2/4 분기만 |
| 주가·EPS 주식기준 일치 | 미확인 | 미확인 유지 | 공급사가 희석/기본을 밝히지 않음 |

## R3 — 새 필수요건을 추가하지 않았음을 명시 (2026-09-09)

"모든 분기에 두 번째 공급사가 없다"는 사실은 관측으로만 기록하고 채점 요건으로 승격하지 않았다. worker 설계 5.1 은 복수 공급사 교차검증을 요구하지 않는다. `evidence.json` 의 `quarters_covered_by_second_source` / `quarters_second_source_agrees_within_5pct` 는 참고 지표이며 충족 판정에 쓰지 않는다.

## 변경하지 않은 것

- 점수, 채점 정책, 경계값, worker 코드·문서는 손대지 않았다. `worker` 는 읽기 전용으로만 읽었다.
- `설계진행`, `scarpper`, `C-13` worktree 는 읽기 전용으로만 다뤘다.
- 2026-09-02 기준선에 이번 자료를 소급하지 않았다.
