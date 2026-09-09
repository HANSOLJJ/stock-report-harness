# SPACEX-F6-RECHECK-01 — SpaceX 단독 매핑과 Finnhub 분기 EPS 재조회

작성일 2026-09-09. 담당 worker(HANSOLJJ/worker). 요청 메시지 `msg_b0bd8773997e`.

Finnhub 무료 등급 키로 실제 조회했다. **키는 환경변수와 저장소 밖 스크래치 파일로만 다뤘고 이 보고서·커밋·Orca 메시지 어디에도 남기지 않았다.**

## 1. 결론

세 줄로 요약한다.

1. **SPCX 는 실재한다.** Space Exploration Technologies Corp, NASDAQ, IPO 2026-06-12, USD·보통주. 티커 미확인 상태를 해소했다.
2. **분기 EPS 추정치는 0 건이다.** Finnhub 실적 캘린더에 SPCX 행이 과거·미래 통틀어 없다. 2 분기 proxy 후보조차 만들 수 없다. **coverage 0/4.**
3. **`company_id` 개명은 하지 않았다.** 승인 해시 5 종을 전부 무효화하기 때문이다. 그리고 개명만으로는 SpaceX 와 xAI 가 분리되지 않는다 — 이쪽이 더 큰 문제다(4절).

요청하신 것 중 **안전한 범위만 반영**했다. `companies.json` 에 `ticker: "SPCX"`, `exchange: "NASDAQ"` 를 넣고 `scope`·`note` 를 갱신했다. 승인·점수·정책은 그대로다.

## 2. SPCX 실재 확인

`GET https://finnhub.io/api/v1/stock/profile2?symbol=SPCX`

```json
{"ticker":"SPCX","name":"Space Exploration Technologies Corp","country":"US",
 "currency":"USD","estimateCurrency":"USD","exchange":"NASDAQ NMS - GLOBAL MARKET",
 "ipo":"2026-06-12","marketCapitalization":2082751.960025416,
 "shareOutstanding":13159.2,"floatingShare":6064.39,
 "finnhubIndustry":"Telecommunication","weburl":"https://www.spacex.com"}
```

`GET /quote?symbol=SPCX` → `{"c":153.47,"d":5.52,"dp":3.731,"h":155,"l":145.14,"o":149.045,"pc":147.95,"t":1788897600}` (t = 2026-09-08 20:00 UTC)

**basis 는 명확하다.** `currency: USD`, `estimateCurrency: USD`, 미국 상장 보통주다. Finnhub 이 TSM 을 `2330.TW` 로 되돌리던 것과 달리 SPCX 는 티커가 유지된다. ADR/ADS 문제가 없다.

검산도 맞는다. `153.47 × 13,159.2M주 = 약 2.02 조 USD` 이고 profile2 의 `marketCapitalization` 2,082,752(백만 USD) = 약 2.08 조와 정합적이다(시각 차이).

### 2.1 기준선 값과의 대조

| 항목 | 기준선 v1.5 (as_of 2026-09-02) | Finnhub SPCX (2026-09-08) |
|---|---|---|
| 주가 | 140.71 USD (`legacy_unverified`) | 153.47 USD |
| 시가총액 | 1.91 조 USD | 약 2.08 조 USD |
| 함의 주식수 | 1.91e12 ÷ 140.71 = **135.7 억주** | **131.6 억주** |
| NTM PER | 111.0 (`vendor_forward_pe_verified_ntm`) | 산출 불가 (EPS 추정치 없음) |
| P/S | 82.9 | — |

함의 주식수가 135.7 억주 대 131.6 억주로 근접한다. **기준선의 시세 항목은 이미 SPCX 단독에 가까운 값이었던 것으로 보인다.** 다만 기준선 관측은 `legacy_unverified` 이고 원문 출처를 이번에 재검증하지 않았으므로 단정하지 않는다. 시세 쪽과 달리 판단·근거 쪽은 여전히 합산 범위다(4절).

## 3. 분기 EPS 추정치 재조회 — 0 건

### 3.1 조회 결과

`GET /calendar/earnings?from=2024-01-01&to=2029-12-31&symbol=SPCX`

```json
{"earningsCalendar":[]}
```

과거 실적(`epsActual`)도, 미래 추정치(`epsEstimate`)도 **한 건도 없다.** 조회 창은 IPO(2026-06-12) 이전부터 3 년 뒤까지 덮는다.

같은 키·같은 endpoint 로 다른 11 개 종목은 정상 응답한다(`../finnhub-earnings-03/REPORT.md` 3.2). 인증·형식 문제가 아니다.

### 3.2 방법상 주의 — 무필터 조회는 부재 근거가 못 된다

교차 확인을 위해 심볼 없이 전체 캘린더를 조회해 SPCX 를 찾아봤다.

| 조회 창 | 반환 행 수 | SPCX |
|---|---|---|
| 2026-06-01 ~ 2027-06-30 | 1500 | 0 |
| 2026-08-01 ~ 2026-09-30 | 1500 | 0 |

두 창 모두 **정확히 1500 행**이다. 창 길이가 7 배 차이인데 같은 수가 나온다는 것은 응답이 1500 행에서 잘렸다는 뜻이다. 따라서 **무필터 조회의 "SPCX 없음" 은 부재의 근거로 쓸 수 없다.**

이 보고서의 0 건 판정은 **심볼 지정 조회**(`symbol=SPCX`)에만 근거한다. 그쪽은 빈 배열을 명시적으로 돌려주므로 유효하다.

### 3.3 왜 없는가 — 추정과 사실 구분

IPO 가 2026-06-12 로 약 3 개월 전이다. 신규 상장사는 애널리스트 커버리지가 붙기 전이거나 첫 실적 발표 일정이 아직 공시되지 않았을 수 있다. `../finnhub-earnings-03/REPORT.md` 3.2 에서 확인했듯 이 endpoint 는 **일정이 확정된 발표 건만** 돌려준다.

다만 이는 **개연성 있는 설명이지 확인된 사실이 아니다.** Finnhub 이 이 종목을 커버하지 않는 것인지, 일정이 아직 없는 것인지 구분하지 못했다. 시간이 지나면 채워질 가능성은 있으나 시점을 특정할 수 없다.

## 4. `company_id` 를 바꾸지 않은 이유

요청은 `company_id=spacex`, `display_name=SpaceX` 로의 매핑을 포함했다. **하지 않았다.** 이유가 둘이고, 두 번째가 더 중요하다.

### 4.1 승인 해시 5 종이 전부 무효화된다

`spacex-xai` 문자열이 들어 있는 파일과 건수다.

| 파일 | 건수 | 승인 해시 대상 |
|---|---|---|
| `scorecard/runs/<slug>/run.json` | 1 | **예** |
| `scorecard/runs/<slug>/observations.json` | 38 | **예** |
| `scorecard/runs/<slug>/judgments.json` | 16 | **예** |
| `scorecard/runs/<slug>/results.json` | 19 | **예** |
| `drafts/ai-scorecard-2026-09-baseline.md` | 2 | **예** |
| `scorecard/companies.json` | 1 | 아니오 |
| `scorecard/baseline/v1.5/observations.json` | 38 | 아니오(기준선) |
| `scorecard/baseline/v1.5/scores.json` | 1 | 아니오(기준선) |
| `scripts/scorecard/baseline_import.py` | 6 | 아니오 |
| `plan/`·`research/` 문서 | 6 | 아니오 |

승인 해시는 `rules` · `observations` · `judgments` · `run` · `results` · `draft` 여섯이다(`scripts/scorecard/stages.py:190-202`). `company_id` 를 바꾸려면 그중 **다섯을 동시에 고쳐야** 하고, 그 순간 `approval.json` 의 해시와 어긋나 빌드가 `awaiting_user` 로 멈춘다. 요청 본문의 "기존 점수·승인·정책은 임의 변경하지 말고" 와 정면으로 충돌한다.

이는 이 프로젝트에서 이미 확립된 취급이다. 승인된 실행은 불변 스냅샷이고, 입력 구조 변경은 **다음 `init`** 부터 적용한다.

### 4.2 개명해도 SpaceX 와 xAI 는 분리되지 않는다

이쪽이 본질이다.

이 항목의 관측 38 건과 판단 16 건은 **SpaceX + xAI 합산 범위로 작성된 자료**다. `display_name` 만 "SpaceX" 로 바꾸면 합산 내용이 SpaceX 단독 평가인 것처럼 표시된다. **지금의 "SpaceX + xAI" 라벨이 오히려 정확하다.** 라벨만 바꾸는 것은 정정이 아니라 오표기를 새로 만드는 일이다.

실제로 분리하려면 다음이 필요하다.

1. 어떤 관측·판단이 SpaceX 단독이고 어떤 것이 xAI 몫인지 원문 수준에서 재분류
2. ①②③④⑤⑦⑧ 의 정성 판단을 SpaceX 단독 기준으로 재작성(근거·검토자·검토일 포함)
3. xAI 를 별도 기업으로 둘지, 평가 범위에서 뺄지 결정
4. 새 `init` 으로 실행을 만들고 `calculate → draft → review → approve` 재수행

즉 **라벨 작업이 아니라 자료 작업이다.** 이 판단은 사용자·설계진행의 결정 사항이라 제 임의로 진행하지 않았다.

### 4.3 실제로 반영한 것

`scorecard/companies.json` 의 `spacex-xai` 항목에만, 승인에 영향이 없는 필드를 갱신했다.

```
ticker    : null → "SPCX"
exchange  : null → "NASDAQ"
scope     : "…티커·거래소는 원문에 없어 미확인"
          → "…SpaceX 는 2026-06-12 SPCX 로 NASDAQ 상장(Finnhub profile2 확인, USD·보통주).
             xAI 는 별도 상장 티커가 확인되지 않아 이 항목의 판단·근거는 여전히 합산 범위다"
note      : "ticker 는 검증된 출처 확보 후 입력"
          → "ticker 는 SpaceX 단독 SPCX 다. company_id·display_name 의 SpaceX 단독 분리는
             기준선 관측·판단이 합산 범위라 새 실행(init)에서 입력을 분리해 처리한다"
```

요청 중 "xAI 결합 티커 부재 사유는 제거하되 합병 맥락은 메모로 남기세요" 를 이 형태로 반영했다. 티커 미확인 사유는 없앴고, xAI 합산 맥락은 남겼다.

**검증 결과 승인은 유지된다.** `results deterministic recompute` 와 `approval hashes match current inputs` 를 포함해 8 개 항목 전부 PASS 이고, 재빌드한 HTML 은 이전과 바이트 단위로 동일하다.

## 5. F6 적용 가능성

**적용 불가.** 자동 점수를 확정하지 않는다.

| 요건 | 상태 |
|---|---|
| 미발표 4 개 연속 분기 EPS | ❌ **0/4**. 관측 0 건 |
| 2 분기 proxy 후보 | ❌ 만들 수 없음. 1 건도 없다 |
| 통화 기준 | ✅ USD (profile2 `currency`·`estimateCurrency`) |
| 주식 기준 | ✅ 미국 보통주. ADR/ADS 아님 |
| basis 검증 상태 | 통화·주식 기준은 확인. **EPS 값 자체가 없어 basis 를 붙일 대상이 없음** |

coverage 와 proxy 를 분리해 기록하라는 요청에 따라 명시한다.

- **coverage: 0/4** — 확보한 미래 분기 EPS 추정치 0 건
- **2Q proxy 후보: 없음** — 후보를 구성할 관측 자체가 없다
- **basis: 통화·주식 기준은 확정(USD·보통주), 값 미확보**

현행 실행의 F6 는 `ok / -5` 로 이미 산출돼 있고 근거는 기준선 승계 관측 `ntm_per 111.0`(`vendor_forward_pe_verified_ntm`, `legacy_unverified`)이다. **이번 조사는 이 값을 대체하지도, 검증하지도 못했다.** 점수는 그대로 둔다.

참고로 이 기업의 미완료 사유는 F6 가 아니라 ⑨ 적자 깊이의 C-06 규칙 결정 대기다. F6 자료가 채워져도 순위 편입은 C-06 결정에 달려 있다.

## 6. 검증

| 항목 | 결과 |
|---|---|
| `python scripts/validate_report_contract.py` | 8 개 항목 **PASS** (승인 해시 일치 포함) |
| `npm test` | 54 건 통과 |
| `results.json` sha256 | `4eb8c7d7…` 변경 없음 |
| 재빌드 HTML | 이전과 **동일**(`diff` 무차이) |
| 변경 파일 | `scorecard/companies.json` (ticker·exchange·scope·note), 이 보고서 |

점수·승인·정책·규칙은 변경하지 않았다.

## 7. 재현 방법

```bash
export FINNHUB_KEY='...'

# 2 — SPCX 실재와 basis
curl -s "https://finnhub.io/api/v1/stock/profile2?symbol=SPCX&token=$FINNHUB_KEY" -o spcx.json
python -c "import json;d=json.load(open('spcx.json'));print(d['ticker'],d['exchange'],d['currency'],d['estimateCurrency'],d['ipo'],d['shareOutstanding'])"
#   → SPCX  NASDAQ NMS - GLOBAL MARKET  USD  USD  2026-06-12  13159.2

# 3.1 — 분기 EPS 0 건 (이 조회만이 부재의 근거다)
curl -s "https://finnhub.io/api/v1/calendar/earnings?from=2024-01-01&to=2029-12-31&symbol=SPCX&token=$FINNHUB_KEY"
#   → {"earningsCalendar":[]}

# 3.2 — 무필터 조회가 1500 행에서 잘리는 것 확인 (부재 근거로 쓰지 말 것)
curl -s "https://finnhub.io/api/v1/calendar/earnings?from=2026-08-01&to=2026-09-30&token=$FINNHUB_KEY" -o all.json
python -c "import json;print(len(json.load(open('all.json'))['earningsCalendar']))"   # 1500

# 4.1 — 개명이 건드리는 승인 해시 대상
grep -rc "spacex-xai" scorecard/runs/ai-scorecard-2026-09-baseline/*.json drafts/ai-scorecard-2026-09-baseline.md
```

## 8. 남은 결정 사항

제 판단으로 진행하지 않고 남긴다.

1. **SpaceX 와 xAI 를 실제로 분리할 것인가.** 분리한다면 4.2 의 네 단계가 필요하고 새 실행이 전제다. 라벨만 바꾸는 안은 권하지 않는다.
2. **분리 시 xAI 처리.** 별도 기업으로 채점할지, 평가 범위에서 뺄지.
3. **SPCX EPS 추정치 재조회 시점.** 첫 실적 발표 일정이 공시되면 캘린더에 나타날 수 있다. 다음 실행 준비 때 재조회를 권한다.
4. **기준선 시세 항목의 출처 재검증.** 2.1 에서 기준선 주가·시총이 SPCX 단독에 가까워 보였으나 `legacy_unverified` 라 확인하지 않았다.
