# SPACEX-F6-RECHECK-01 — SpaceX 단독 매핑과 Finnhub 분기 EPS 재조회

작성일 2026-09-09. 담당 worker(HANSOLJJ/worker). 요청 메시지 `msg_b0bd8773997e`.

Finnhub 무료 등급 키로 실제 조회했다. **키는 환경변수와 저장소 밖 스크래치 파일로만 다뤘고 이 보고서·커밋·Orca 메시지 어디에도 남기지 않았다.**

> **정정 안내 (2026-09-09, `msg_c31d219bc7a9`).** 아래 1~8 절 중 **4.2 절의 근거와 3.3 절의 유보 판정이 9 절에서 뒤집힌다.** SpaceX 와 xAI 는 두 기업의 합산이 아니라 **합병된 단일 법인**이며, Finnhub 의 SPCX 미수록은 "일정 미공시" 가 아니라 **미커버**로 좁혀졌다. 원문은 기록으로 남기되 판단은 **9 절을 따른다.**

## 1. 결론

세 줄로 요약한다.

1. **SPCX 는 실재한다.** Space Exploration Technologies Corp, NASDAQ, IPO 2026-06-12, USD·보통주. 티커 미확인 상태를 해소했다.
2. **분기 EPS 추정치는 0 건이다.** Finnhub 실적 캘린더에 SPCX 행이 과거·미래 통틀어 없다. 2 분기 proxy 후보조차 만들 수 없다. **coverage 0/4.**
3. **`company_id` 개명은 하지 않았다.** 승인 해시 5 종을 전부 무효화하기 때문이다(4.1). 개명하지 않는다는 결론은 유지되지만 그 두 번째 근거는 9.1 에서 정정한다.

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

함의 주식수가 135.7 억주 대 131.6 억주로 근접한다. **기준선의 시세 항목은 이미 SPCX 단독에 가까운 값이었던 것으로 보인다.** 다만 기준선 관측은 `legacy_unverified` 이고 원문 출처를 이번에 재검증하지 않았으므로 단정하지 않는다. → **9.2·9.3 에서 정정한다. 판단·근거도 합산이 아니라 단일 법인 연결 시각으로 쓰여 있다.**

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

> ⚠️ **9.5 에서 미커버로 좁혀진다.** 아래는 정정 전 기록이다.

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

> ⚠️ **이 절의 전제는 틀렸다. 9.1 에서 정정한다.** 아래는 정정 전 기록이다.

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

---

# 9. 정정 — 합병 후 SpaceX 단일 법인 범위 (SPACEX-SCOPE-CORRECTION-02)

정정 요청 `msg_c31d219bc7a9` 에 따라 추가한다. **1~8 절의 판단 중 하나를 뒤집는다.**

## 9.1 무엇이 틀렸나

4.2 절에서 나는 이렇게 썼다.

> "이 항목의 관측 38 건과 판단 16 건은 **SpaceX + xAI 합산 범위로 작성된 자료**다. … 지금의 'SpaceX + xAI' 라벨이 오히려 정확하다."

**틀렸다.** 자료는 두 기업을 더한 합산이 아니라 **xAI 를 흡수한 SpaceX 단일 법인의 연결 자료**다. 따라서 부정확한 쪽은 자료가 아니라 라벨이다. "SpaceX + xAI" 는 두 기업의 병렬 합산으로 읽히므로 합병 후 기준에서 쓰지 않는다.

**다만 결론(개명하지 않음)은 유지된다.** 이유가 4.1 의 승인 해시 하나로 충분하기 때문이다. 4.2 는 그 결론을 뒷받침하는 근거로는 무효이며, 아래 9.6~9.7 로 대체한다.

## 9.2 근거 — 우리 자료가 이미 단일 법인 연결이다

기준선 v1.5 원문(`scorecard/baseline/v1.5/scores.json`, `SRC-v15-html`)에서 확인된다.

| 근거 | 원문 | 의미 |
|---|---|---|
| 분기 실적 | `quarter_note` — "Q2 (8/4) \| $7.8B (+92%) · Starlink 1,200만 · **AI 세그먼트 $2.56B(+247%)** \| -$0.09 (컨센 -$0.26 상회) · 영업적자 -14.9% \| TTM -$32.5B · 현금 $100B" | 하나의 상장사가 하나의 손익을 발표하고, xAI 는 그 안의 **세그먼트**다 |
| 지분 구조 | F7 근거 — "xAI **흡수**($250B)·Cursor 인수($60B) 전부 자사주" | 합병이며 대가는 SpaceX 주식이다 |
| 주식 수 | F6 근거 — "주식 수 YoY +41.8%(IPO + xAI $250B + Cursor $60B **전량 주식교환**)" | xAI 지분이 SpaceX 주식으로 치환됐다 |
| 설비투자 | F9 근거 — "FCF -$32.5B(capex $42B — **Starship·xAI DC**)" | xAI 데이터센터가 SpaceX capex 로 계상된다 |
| 시가총액 | `market_cap` 1.91 조 USD | 2.1 절에서 확인했듯 SPCX 단일 종목 시총과 정합적이다 |

두 기업을 따로 평가해 더한 흔적은 없다. **하나의 연결 재무제표에서 나온 값들이다.**

## 9.3 합병 전후 범위 구분 — 날짜와 근거

### 확인된 사건 연표

| 날짜 | 사건 | 근거 |
|---|---|---|
| 2026-06-12 | SpaceX NASDAQ 상장(SPCX), $75B 조달 | Finnhub `profile2.ipo`, 기준선 F4 근거 "6/12 나스닥 상장 $75B 조달(사상 최대 IPO)" |
| 시점 미상 | xAI 흡수, 대가 $250B 전량 주식 | 기준선 F6·F7 근거. **날짜가 원문에 없다** |
| 2026-08-04 | Q2 실적 발표(연결, AI 세그먼트 포함) | 기준선 `quarter_note` "Q2 (8/4)" |
| 2026-08-14 | Cursor 인수 완료 $60B | 기준선 F1 근거 "Cursor(8/14 $60B 인수 완료)" |
| 2026-09-02 | 기준선 관측 기준일 | 관측 19 건 전부 `as_of=2026-09-02` |

**xAI 흡수 완료일이 원문에 없다.** 이 값은 미확인이며 추정하지 않는다. 다만 2026-08-04 Q2 발표에 AI 세그먼트가 연결로 잡혀 있으므로 **늦어도 Q2 회계기간 종료 시점에는 흡수가 반영돼 있었다**고 볼 수 있다.

### 관측 19 건의 범위 분류

| 구분 | 지표 | 합병 범위 판정 |
|---|---|---|
| **시점 값 — 합병 후 단일 법인 확정** | `price` 140.71, `market_cap` 1.91e12, `ps_ratio` 82.9, `ntm_per` 111.0, `cash` 1.0e11, `net_cash` 6.03e10, `credit_rating` 무등급 | 기준일 2026-09-02 는 상장(6/12)·Q2 발표(8/4)·Cursor 완료(8/14) 이후다. 단일 법인 값이다 |
| **기간 값 — 합병 전후가 섞인다** | `fcf_ttm` -3.25e10, `capex_ttm` 4.24e10, `net_borrowing_ttm` 1.02e11, `operating_margin_ttm` -0.149, `debt_ebitda` 5.78, `runway_years` 3.1(derived) | TTM 창은 2026-09-02 기준 약 2025-09~2026-09 다. **상장 전과 흡수 전 기간을 반드시 포함한다.** 그 구간의 xAI 실적이 소급 연결됐는지 여부는 자료로 알 수 없다 |
| **미공시** | `ttm_per`, `nonop_share`, `offbalance_B` | `not_disclosed` |
| **원문 서술** | `quarter_note`, `offbalance_note` | Q2 분기 값(합병 후)과 TTM 값(혼재)이 한 문장에 섞여 있다 |

**핵심 문제: 관측 19 건 전부 `period` 가 `null` 이다.** TTM 지표의 창이 기록돼 있지 않아, 합병 전 구간을 어떻게 처리했는지(소급 연결인지 인수일 이후만인지) 판정할 근거가 없다. 이는 스키마 결함이 아니라 **기준선 이관 시 원문에 기간 정보가 없었기 때문**이며, 모든 관측이 `legacy_unverified` 인 이유이기도 하다.

### 판단 8 건의 범위

`F1 F2 F3 F4 F5 F7 F8 F9` 여덟 건 전부 `status=carried`, `reviewer=legacy:v1.5` 다. 근거 불릿은 합병 전후 사실이 섞여 있다. 예를 들어 F4 는 "Starlink·Starship·xAI(Grok)·X·Cursor·Terafab" 을 **하나의 사업 포트폴리오**로 나열하는데 이는 합병 후 시각이고, F2 의 "Grok 4.6", F3 의 "Colossus GPU 20만" 은 xAI 가 독립 회사이던 시기의 자산이 그대로 SpaceX 자산으로 편입된 서술이다.

**즉 판단은 이미 단일 법인 시각으로 쓰여 있다.** 두 회사를 따로 채점해 더한 구조가 아니다.

## 9.4 건수 정정

4.1·4.2 절에서 쓴 "관측 38 건, 판단 16 건" 은 **문자열 출현 수이지 레코드 수가 아니다.** `spacex-xai` 가 `observation_id` 와 `company_id` 두 곳에 들어가 두 배로 세졌다.

| | 실제 레코드 | 문자열 출현 |
|---|---|---|
| 관측 | **19** | 38 |
| 판단 | **8** | 16 |

승인 해시 다섯이 걸린다는 4.1 의 결론은 건수와 무관하게 유지된다.

## 9.5 Finnhub 미커버 판정 강화

3.3 절에서 나는 SPCX 의 실적 캘린더가 빈 이유를 "커버리지 미형성 또는 일정 미공시" 로 두고 확인된 사실이 아니라고 했다. **이제 더 좁힐 수 있다.**

기준선 `quarter_note` 가 SpaceX 의 **2026-08-04 Q2 실적 발표**를 기록하고 있다. EPS -$0.09 이며 컨센서스 -$0.26 을 상회했다고 적혀 있으므로, 그 시점에 **실제 발표와 컨센서스가 모두 존재했다.**

그런데 Finnhub 는 2024-01-01~2029-12-31 창에서 SPCX 행을 **한 건도** 돌려주지 않는다. 이미 지나간 8/4 발표조차 없다. 따라서 "일정이 아직 안 잡혀서" 는 설명이 되지 않는다.

**판정: Finnhub 가 SPCX 를 커버하지 않는다.** 시간이 지나도 채워질 것으로 기대하기 어렵다. 8 절 결정 사항 (3) "재조회 시점" 은 Finnhub 에 한해서는 실익이 낮으며, 다른 원천을 찾는 편이 낫다.

## 9.6 xAI 처리 기준

정정 요청대로 다음을 기준으로 삼는다.

1. **분석 대상 법인은 SPCX 단일 상장사 SpaceX 하나다.** 두 기업의 합산으로 표현하지 않는다.
2. **xAI 는 SpaceX 내부 사업·합병 구성요소로 기록한다.** 독립 평가 대상이 아니다.
3. **xAI 별도 점수를 만들지 않는다.** 9 개 factor 어디에도 xAI 단독 점수를 두지 않는다.
4. **xAI 유래 자산·실적은 SpaceX 의 것으로 센다.** Grok·Colossus·AI 세그먼트 매출·xAI 데이터센터 capex 는 SpaceX 항목이다. 기준선 판단이 이미 이렇게 쓰여 있다(9.3).
5. **세그먼트 수준 값이 필요하면 SpaceX 관측에 세그먼트 범위를 명시해 넣는다.** 예를 들어 AI 세그먼트 매출은 별도 기업이 아니라 `spacex` 의 관측으로 두고 `basis` 에 세그먼트 범위를 적는다.
6. **합병 전 xAI 단독 수치를 SpaceX 시계열에 소급 혼입하지 않는다.** 혼입 여부가 불명확한 TTM 값은 `period` 를 채워 창을 명시하기 전까지 검증 대기로 둔다.

## 9.7 새 실행에서의 법인 범위 정규화 방안

현재 승인 실행(`ai-scorecard-2026-09-baseline`)은 **그대로 보존한다.** 아래는 다음 `init` 에서 적용할 안이다.

### 안 — 신규 실행에서 `spacex` 로 정규화하고 별칭으로 이력을 잇는다

| 항목 | 현재 승인 실행 | 새 실행 |
|---|---|---|
| `company_id` | `spacex-xai` (동결) | `spacex` |
| `display_name` | `SpaceX + xAI` (동결) | `SpaceX` |
| `ticker` / `exchange` | `SPCX` / `NASDAQ` (4.3 에서 반영 완료) | 동일 |
| `aliases` | — | `["SpaceX + xAI", "spacex-xai", "SpaceX", "xAI"]` 를 포함해 과거 표기와 연결 |
| `scope` | 합산 서술 | "SpaceX 단일 법인 연결. xAI 는 2026 년 주식교환으로 흡수된 내부 사업이며 별도 채점 대상이 아니다" |

**필요한 작업은 넷이다.**

1. **`companies.json` 에 `spacex` 항목을 새로 만들고 `aliases` 에 `spacex-xai` 를 넣는다.** 기존 `spacex-xai` 항목은 지우지 않는다. 과거 승인 실행이 그 키로 결속돼 있다.
2. **`history.csv` 이력 연결을 처리한다.** 이 파일은 `company_id` 로 키를 잡으므로(헤더 8 번째 열) 개명하면 시계열이 끊긴다. 별칭 해석 계층을 두거나, 이력 조회 시 `spacex-xai → spacex` 매핑을 적용하는 방식 중 하나를 택해야 한다. **이 선택은 구현 결정이므로 별도 합의가 필요하다.**
3. **새 관측을 SPCX 기준으로 수집한다.** 정정 요청대로 SpaceX 단독 F6 관측은 SPCX 기준으로만 새로 수집한다. 기준선 값을 개명해 재사용하지 않는다.
4. **TTM 지표에 `period` 를 채운다.** 9.3 에서 드러난 공백이다. 새 관측은 창을 명시해 합병 전후 혼입 여부를 판정 가능하게 만든다.

### 하지 않을 것

- 승인 해시를 깨는 `company_id` 일괄 개명 (4.1)
- 자료를 그대로 두고 라벨만 바꾸는 조작 — 정정 요청도 이를 금지한다
- 기준선 v1.5 스냅샷 수정. `scorecard/baseline/v1.5/` 는 과거 기록이며 D-08 에 따라 보존한다

## 9.8 이번 정정에서 하지 않은 것

- **점수·승인·정책·규칙 변경 없음.** `results.json` 해시 `4eb8c7d7…` 유지, 재빌드 HTML 이전과 동일.
- **`companies.json` 추가 변경 없음.** 4.3 에서 넣은 `ticker`·`exchange`·`scope`·`note` 가 전부이며 이번 정정으로 더 고치지 않았다. 새 `spacex` 항목 신설은 새 실행 작업이라 여기서 하지 않는다.
- **xAI 흡수 완료일 확정 없음.** 원문에 없어 미확인으로 남긴다.
- **TTM 창의 합병 전 구간 처리 방식 확정 없음.** 소급 연결 여부를 판정할 자료가 없다.

## 9.9 남은 결정 사항 (8 절 갱신)

8 절의 (1)(2) 는 이번 정정으로 해소됐다. xAI 는 분리 대상이 아니라 내부 사업이며 별도 점수를 만들지 않는다. 나머지를 갱신해 남긴다.

1. **`history.csv` 이력 연결 방식.** 9.7 의 2 번. 별칭 해석 계층인지 조회 시 매핑인지 결정이 필요하다.
2. **SPCX 관측의 새 원천.** Finnhub 는 커버하지 않는다(9.5). FMP 무료는 분기가 막혀 있다(`../fmp-estimates-02/REPORT.md`). SPCX 분기 EPS 를 줄 원천을 따로 찾아야 한다.
3. **TTM 지표의 합병 전 구간 처리 규칙.** 소급 연결값을 쓸지, 인수일 이후만 셀지, 아니면 창이 걸치는 동안 검증 대기로 둘지.
4. **기준선 시세 항목의 출처 재검증.** 2.1 에서 SPCX 단독에 가까워 보였으나 `legacy_unverified` 라 확인하지 않았다.
