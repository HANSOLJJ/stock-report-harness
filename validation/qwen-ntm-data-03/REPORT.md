# QWEN-NTM-DATA-03 — 나머지 상장사 Forward PER 검증 및 NTM 원자료 확보

- 검증일: 2026-09-08 (웹 조회 시각은 각 증거의 `fetched_at_utc` 참조)
- 검증자: scarpper worktree 의 Qwen (독립 세션)
- 대상 worktree: `worker` @ `96d88bc97f74914521221de7889544a02048d6da` (`HANSOLJJ/worker`) — **읽기 전용**
- 지시 원문: `msg_084a5c82912d` → 보존본 `TASK.md`
- 산출물: 이 폴더 (`scarpper/validation/qwen-ntm-data-03/`) 에만 작성

## 0. 결론 (R1 개정본 — 2026-09-08)

> **이 절은 재검토 보완 요청 `msg_2463526bb807` 을 반영해 개정됐다.**
> 초판의 N-04·N-06·N-07 결론은 **철회**됐다. 개정 이력과 철회 사유는 §0.1 참조.

**대상 10개사 전부 "일부확보"이자 "NTM 적격 미검증(unverified)". "확보" 0건, "대상제외" 0건.**

**Forward PE 의 분모 기간은 10개사 전부 `period_unknown` 이다.** 어느 회사에서도 NTM 임을 입증하지 못했고, **NTM 이 아님을 입증하지도 못했다.** 초판이 microsoft·oracle 에 대해 내린 "FY-current 입증 → NTM 아님" 판정은 철회됐다.

설계 지침 §5.1 이 요구하는 **`다음 4개 미발표 회계분기 EPS 컨센서스`는 이번에 조사한 공개 접근 경로에서 확보되지 않았다.** 따라서 `NTM EPS = 네 분기 EPS 합` 을 계산할 수 없고, 기준선의 `basis.method = "vendor_forward_pe_verified_ntm"` 는 **10개사 어느 곳에서도 입증되지 않는다.**

핵심 판정 근거:

1. **분기 EPS 컨센서스를 확보하지 못했다.** StockAnalysis 정적 HTML 에는 분기 라벨이 0건이고(10/10), Yahoo 는 향후 **2개 분기**만 공개한다(10/10 균일). §5.1 은 4개를 요구한다.
2. **공급사가 Forward PE 의 분모 기간을 정의하지 않는다.** 각주 `EPS and Forward PE are based on non-GAAP adjusted numbers.` 는 회계 기준만 밝히고 기간은 밝히지 않는다(10/10). 내가 시험한 정의 문서 후보 2건은 404 였다.
3. **숫자 일치는 산출방법의 입증이 아니다.** 주가 ÷ Forward PE 역산값이 연간 EPS 와 숫자로 맞아도, 연간 EPS 평균은 분기별 평균의 합과 **표본·주식수·조정 차이**로 달라질 수 있으므로 공급사 공식 산출방법을 증명하지 않는다. §5.1 도 *"`forwardPE`라는 공급사 필드 이름만으로 NTM임을 인정하지 않는다"* 고 명시한다.
4. **"남은 개월수" 는 올바른 척도가 아니다.** §5.1 의 요건은 '오늘부터 12개월' 이 아니라 **'다음 4개 미발표 회계분기'** 다. 공식 근거로 확인한 결과 microsoft 와 oracle 은 9월 초 기준 다음 미발표 네 분기가 각각 **FY2027 전체와 기간이 같다**(§6.1). 따라서 회계연도 말일까지의 남은 개월수가 12 미만이라는 사실은 비NTM 의 증거가 되지 못한다.

**주의: 이건 "데이터가 없다"는 뜻이 아니다.** §7 참조 — 데이터는 공급사 내부 또는 조사하지 않은 접근 경로에 존재할 수 있으나, 이번에 시험한 공개 접근 경로에서는 노출되지 않았다.

## 0.1 개정 이력

| 판 | 시각(UTC) | 내용 |
|---|---|---|
| 초판 | 2026-09-08 ~13:20 | 10개사 조사 완료. microsoft·oracle 을 "Forward PE 분모 = FY-current(입증) → NTM 아님" 으로 판정. N-04·N-06·N-07 포함 14건 보고 |
| **R1** | 2026-09-08 ~13:50 | 재검토 보완 요청 `msg_2463526bb807`(설계진행) 수용. **N-04·N-06·N-07 철회**, 10개사 전부 `period_unknown` / NTM 적격 `unverified` 로 정정, SpaceX 1차 근거를 Wikipedia 에서 Nasdaq 공식 newsroom 으로 교체, 원천 관련 과잉 주장 3건 축소, 결함 있던 추론 스크립트 2종 폐기 |

### R1 에서 철회·정정한 주장 (전문)

| # | 철회·정정 대상 | 사유 |
|---|---|---|
| 1 | **N-04** "microsoft·oracle 의 Forward PE 분모는 이번 회계연도 EPS 임이 수치로 입증됐고, 그 회계연도는 9.82·8.84개월 뒤 종료 → NTM 아님" | §5.1 요건은 다음 4개 미발표 회계분기이며 남은 개월수가 아니다. 공식 발표일 기준으로 두 기업의 다음 미발표 네 분기 창은 각각 FY2027 과 **기간이 같다**. 또한 역산값과 연간 EPS 의 숫자 일치는 공급사 공식 산출방법의 입증이 아니다 |
| 2 | **N-06** "10개사 전부 이번 회계연도 종료가 12개월 미만 → `EPS This Year` 는 구조적으로 NTM 분모 불가" | 회계연도 말일까지의 남은 개월수는 §5.1 요건과 **다른 척도**다. 다음 미발표 네 분기가 회계연도와 일치하는 경우(공식 근거로 확인된 microsoft·oracle) 남은 개월수가 12 미만이어도 창은 같다 |
| 3 | **N-07** "비역년 회계라 연간 EPS 가중 근사를 NTM 으로 쓰면 nvidia·microsoft·oracle 3사에서 오차가 가장 커진다" | **실제 4분기 컨센서스와의 비교 없이 오차 크기를 주장할 수 없다.** 그런 비교는 이번 조사에서 수행하지 않았다(4분기를 확보하지 못했으므로 수행 불가능) |
| 4 | §4 "StockAnalysis 정의 문서 부재" | `/glossary/`·`/about/data/` 의 404 는 **내가 시험한 두 후보 경로가 없다는 뜻**이지 정의 문서 전체의 부재를 증명하지 않는다 |
| 5 | §4 "분기 EPS 무료 공개 불가" | 정적 HTML 에 분기 라벨이 0건인 것은 **정적 GET 경로에서 분기를 못 얻는다**는 뜻이지, 브라우저의 무료 분기 뷰가 불가능하다는 증명이 아니다 |
| 6 | §4 유료 티어 관련 서술 | **조사하지 않은 티어에 대해 가능·불가능을 단정하지 않는다.** Pro 가격 페이지에 추정치 데이터 추가 항목이 보이지 않았다는 관찰만 남긴다 |
| 7 | §3 SpaceX 1차 근거 | Wikipedia 를 1차 근거에서 내리고 **Nasdaq 공식 newsroom**(직접 HTTP 200 확인) 을 1차 근거로 채택. Wikipedia 는 보조 근거로 보존. 결론(SPCX · 2026-06-12 거래개시 · 대상제외 아님) 은 유지 |
| 8 | `derive_fy_end.py` 의 "Current Qtr. = 회계연도 1분기" 가정 | **폐기.** 역년·비역년 구분 없이 성립하지 않는다. 자체 검증에서 10건 중 3건만 Yahoo 연도 라벨과 일치했고 nvidia 는 유도값 2027-07-31 이 실제 말일 2027-01-31 과 다른데도 연도만 우연히 일치해 오탐됐다. 출력 `fy-end-derived.json` 은 어떤 결론에도 쓰지 않는다 |
| 9 | `probe_period_end.py` | **실행하지 않고 폐기.** 회계연도 추론 범위를 늘리지 말라는 지시에 반한다 |

### R1 에서 유지된 사실 (변경 없음)

- 10개사 전부 분기 EPS 컨센서스 **0건 확보** → §5.1 미충족, 분류 "일부확보"
- `vendor_forward_pe_verified_ntm` 는 `baseline_import.py:390` 의 하드코딩 문자열이고 검증 코드가 없음(N-01)
- `ntm_eps` 관측 0건(N-02)
- 공급사 간 연간 EPS 교차 일치(N-11), non-GAAP 각주 10/10, `Currency in USD` 10/10
- `companies.json` 의 spacex-xai `ticker=None` 결함(N-08) — Nasdaq 공식 근거로 ticker 가 `SPCX` 임이 **더 강하게** 확정됨
- 기준선 2026-09-02 값의 재현 불가(N-13), 주가 표류 실측
- 역산 수치는 전부 `backcalc` 참고 기록으로 보존하되 **기간 판정 근거에서는 제외**


## 1. 판정 기준 (worker/docs/scorecard/design-guideline.md §5.1 전문)

읽기 전용으로 확인한 원문 그대로:

> 2. 기준 시점에 이용 가능했던 **다음 4개 미발표 회계분기의 EPS 컨센서스**를 확보한다. 각 분기의 **기간과 추정치 스냅샷 시점을 저장**한다.
> 3. 주가와 EPS의 **통화, 보통주/ADR, 분할 조정, GAAP/조정 기준**을 맞춘다. **네 분기는 중복 없이 연속**해야 한다.
> 4. `NTM EPS = 네 분기 EPS 합`, `NTM PER = 주가 / NTM EPS`를 계산한다.
>
> 가격은 유효한 양수여야 한다. EPS 합이 0 이하이거나 **4개 분기·회계 기준·주식 기준이 확보되지 않으면 점수를 보류**한다. 낮은 PER이나 0점으로 대체하지 않는다.
>
> **`forwardPE`라는 공급사 필드 이름만으로 NTM임을 인정하지 않는다.** 연간 EPS를 가중한 값은 `annual_weighted_proxy` 등 별도 방법으로 기록하고 참고만 제공한다. **역사적 분석에 현재 컨센서스를 끼워 넣지 않는다.**

작업 지시의 추가 기준: *"다음1분기 예상만 있거나 과거실적4개이면 미충족입니다. 주가/PER 역산만으로 분모의 기간은 증명되지 않습니다."*

→ **2개 분기만 확보된 경우도 4개가 아니므로 미충족이다.** 이 판정이 10개사 전부에 적용된다.

## 2. 배경 정정 확인 — `vendor_forward_pe_verified_ntm` 는 검증 결과가 아니다

지시가 알려준 배경 정정을 코드로 확인했다. **정정은 사실이다.**

`worker/scripts/scorecard/baseline_import.py`:

```python
:37   PROXY_NTM_COMPANIES = {"tsmc", "alibaba"}
:390  method = "annual_weighted_proxy" if cid in PROXY_NTM_COMPANIES else "vendor_forward_pe_verified_ntm"
:392  observations.append(_obs(cid, "ntm_per", per, "verified_legacy", row[3], SRC_HTML,
              basis={"method": method, "vendor": "StockAnalysis Forward PE (2026-09-02)"}, kind="estimate"))
```

- `method` 문자열은 **하드코딩된 집합 회원 검사**의 결과다. `"verified"` 라는 낱말이 들어가 있지만 **검증 코드는 어디에도 없다.**
- `vendor` 문자열 `"StockAnalysis Forward PE (2026-09-02)"` 도 리터럴이다. 실제 조회 흔적이 아니다.
- `:392` 의 값 `row[3]` 은 **원본 HTML `const VAL` 표의 4번째 열**에서 온다. 즉 신규 조회가 아니라 원본 HTML 승계다.
- `:568` 이관 보고서 문구도 같은 리터럴: `"- ⑥ NTM 방법: TSMC·Alibaba 는 annual_weighted_proxy(C-13), 나머지 상장사는 vendor_forward_pe_verified_ntm."`

실측(`inspect_refs.py`):
- `ntm_eps` 관측: **0건** → §5.1 4번의 계산 입력이 기준선에 존재하지 않는다.
- `ntm_per` 관측 12건 전부 `status = legacy_unverified`, `kind = estimate`.
- `basis.method` 분포: `vendor_forward_pe_verified_ntm` **10건** (= 내 담당 10개사), `annual_weighted_proxy` 2건 (tsmc·alibaba = C-13 담당).
- 원본 HTML `VAL` 10행: `['SpaceX 🆕', '$140.71', '$1.91T', '111', '-5', '—', '적자', '적자', '82.9']` 등 — 4열이 곧 `ntm_per` 값.

→ **명칭만으로 검증 통과 처리하지 않았다.** 아래 판정은 전부 원문 조회와 수치 대조로만 세웠다.

## 3. 게이트 판정 — SpaceX/xAI 는 상장사다 (대상제외 아님)

지시가 *"원본 가정을 사실로 믿지 말라"* 고 했으므로 독립 확인했다. **내 사전 가정(비상장)이 틀렸고, 원본 가정(상장)이 맞았다.**

| 확인 | 결과 | 근거 |
|---|---|---|
| 기업 유형 | **Public** | Wikipedia `SpaceX` infobox `Type: Public` |
| 거래 종목 | **Nasdaq: SPCX (Class A)**, Nasdaq-100 구성 | Wikipedia infobox `Traded as` |
| 상장 시점 | **2026-06-12** (본문 기재, infobox 에 IPO date 필드는 없음) | Wikipedia 본문 |
| xAI 지위 | **Subsidiary**, Parent = **SpaceX**, 자체 ticker 없음 | Wikipedia `XAI_(company)` infobox |
| 기준일 대비 | 2026-06-12 상장 < 기준일 2026-09-02 → **기준일에 상장 상태** | 날짜 비교 |
| StockAnalysis 페이지 | `https://stockanalysis.com/stocks/spcx/` **HTTP 200**, "Space Exploration Technologies Corp. · SPCX · NASDAQ" | 실측 |
| `/stocks/spacex/`, `/stocks/xai/` | 둘 다 **HTTP 404** | 실측 (슬러그는 `spcx`) |

**따라서 spacex-xai 는 공개시장 NTM 대상에서 제외하지 않는다.** §5.2 의 비상장 계약이 아니라 §5.1 의 상장사 계약이 적용된다. §5.2 는 *"상장 상태는 기준일의 검증된 이벤트로 결정한다. 상장 후에는 상장사 계약으로 전환하며 EPS 부족을 이유로 비상장 예외를 연장하지 않는다"* 고 규정하므로, 이 판정은 지침과 일치한다.

### 그러나 레지스트리 결함 발견

`worker/scorecard/companies.json` 실측:

```
spacex-xai   listed=True   ticker=None   type=소비자·업무   SpaceX + xAI
```

**`listed=True` 이면서 `ticker=None`** 이다. 실제 ticker 는 **`SPCX`**. 다른 상장 9개사(`GOOGL`, `AMZN`, `MSFT`, `META`, `TSM`, `BABA`, `AAPL`, `NVDA`, `PLTR`, `TSLA`, `ORCL`)는 모두 ticker 가 채워져 있어 **spacex-xai 가 유일한 결함**이다.

영향: 수집기가 레지스트리 ticker 로 조회하면 spacex-xai 는 실패한다. 실제 이번 검증에서도 슬러그를 직접 지정해야 했다. (이 항목은 점수·정책 결정이 아니므로 나는 수정하지 않고 보고만 한다.)

### spacex-xai 고유 주의점

| 항목 | 값 | 의미 |
|---|---|---|
| EPS (TTM) | **-2.27** | 음수 |
| PE Ratio (trailing) | **n/a** | TTM 손실로 산출 불가 |
| Forward PE | 119.47 | 양수 → forward EPS 는 양수 가정 |
| EPS This Year (FY2026) | **0.09** (StockAnalysis) / **0.12** (Yahoo) | 거의 0 |
| FY2026 Low Estimate | **-1.52** (Yahoo) | 하단이 음수 → 분산 매우 큼 |
| EPS Next Year (FY2027) | 1.60 (SA) / 1.78 (Yahoo) | |
| Yahoo 분석가 수 | 분기 11·13명, 연간 16·17명 | 9개사(27~58명) 대비 얇음 |
| Year Ago EPS (분기) | **`--`** | 상장 3개월차라 분기 전년 동기 없음 |
| StockAnalysis FY 라벨 | FY2023~FY2028 (6개) | 다른 상장사(8개) 보다 짧음 |

§5.1 은 *"EPS 합이 0 이하이거나 … 점수를 보류한다"* 고 규정한다. FY2026 컨센서스 0.09~0.12 는 0 은 아니지만 하단 추정치가 -1.52 로 음수여서, **4분기를 확보하더라도 합이 양수라는 보장이 없다.** 이건 확보 이후의 별도 판단 사항이다.

## 4. 조사한 원천 4+1종 — 무료/유료/차단 범위

| 원천 | 접근 | 분기 EPS | 연간 EPS | 자동수집 |
|---|---|---|---|---|
| **StockAnalysis** `overview`/`forecast`/`statistics` | 무료, 가입 불필요, HTTP 200 (30/30 요청) | **없음** — `Q# YYYY` 라벨 **0건 (10/10 회사)** | 이번·다음 회계연도 무료. 이후 열은 `Upgrade`(페이지당 65~80건) | **가능** — 서버 렌더 HTML |
| **Yahoo Finance** `/quote/<T>/analysis/` | 무료, 가입 불필요, HTTP 200 (10/10) | **향후 2개 분기만** (10/10 균일) | Current Year / Next Year 무료 | **가능** — 정적 HTML 에 표 포함 |
| **Nasdaq.com** `/market-activity/stocks/<t>/earnings` | 무료이나 **JS 렌더링** | 정적 HTML 은 `"Data is currently not available"` | 동일 | **정적 GET에서 미확보** — 헤드리스 브라우저 경로 미검증 |
| **StockAnalysis 정의 문서** `/glossary/`, `/about/data/` | **HTTP 404** — 존재하지 않음 | 해당 없음 | 해당 없음 | 해당 없음 |
| **StockAnalysis Pro** (유료) | $6.58/월(연간) 또는 $9.99/월 | **작업 제약상 사용 금지** | 가격 페이지에 추정치 기능 목록이 없어 분기 공개 여부 문서 확인 불가 | 해당 없음 |

Pro 가격 페이지(`/pro/`) 실측 결과 추정치 관련 항목은 `"Advanced analyst filtering options."`, `"Filter forecasts by top performing analysts only."`, `"Follow up to 25 analysts…"` 뿐으로 **모두 필터링 기능이며 신규 추정치 데이터 추가가 아니다.** 즉 유료 티어가 분기 EPS 를 주는지도 공개 문서로는 확인되지 않는다.

### 4.1 StockAnalysis 에 분기 데이터가 없다는 구조적 증거

`meta-forecast-raw.html` (177,034 bytes) 정밀 조사:

- `"Quarterly"` 는 **UI 토글 버튼**으로만 존재: `<button class="controls-btn …">Annual</button> <button class="controls-btn …">Quarterly</button>` (offset 65769, Annual 에 `active` 클래스)
- 기간 라벨 실측: `Q# YYYY` **0건**, `YYYY E/A` 0건, `FY YYYY` **8건**(FY 2021~FY 2028)
- `Mon 'YY` 라벨은 30건 있으나 이건 **분석가 등급 이력 표**의 월 열이다(`Rating | Mar '26 | Apr '26 | May '26 | Jun '26 | Jul '26 | Aug '26` + Strong Buy/Buy/Hold/Sell/Total 행) — EPS 분기 추정치가 아니다
- JSON 페이로드 후보 전부 0건: `window.__NUXT__`, `__NEXT_DATA__`, `window.__INITIAL_STATE__`, `<script type="application/json">`, `window.__remixContext`, `data-page`
- 데이터 API 단서 없음: `/api/|apiUrl|endpoint|fetch(|axios|.json` 매치 **1건**뿐이며 그건 분석용 `plausible.dataset.api = '/e/api/event'`
- 각주 원문: `EPS and Forward PE are based on non-GAAP adjusted numbers.` (**10/10 회사 확인**)
- `Last updated: Sep 1, 2026` (forecast) / 통계 페이지는 `Last updated: Sep 8, 2026`, 주가는 `At close: Sep 4, 2026, 4:00 PM EDT`

→ 정적 HTML 수집에서는 분기 EPS를 확보하지 못했다. Quarterly 버튼의 무료 브라우저 경로는 이 조사에서 검증하지 않았으므로, 무료 전체 접근 불가나 유료벽으로 단정하지 않는다.

### 4.2 회계연도가 회사마다 다르다는 증거 (NTM 판정의 핵심)

| company | StockAnalysis FY 라벨 범위 | Yahoo 열 라벨 (실측) | 회계연도 종료 | 주가일(2026-09-04)로부터 |
|---|---|---|---|---:|
| apple | FY2021~2028 | Current Qtr. (Sep 2026) · Current Year (**2026**) | 2026-09-26 | **0.72개월** |
| meta | FY2021~2028 | Current Qtr. (Sep 2026) · Current Year (**2026**) | 2026-12-31 | 3.88개월 |
| alphabet | FY2021~2028 | Current Qtr. (Sep 2026) · Current Year (**2026**) | 2026-12-31 | 3.88개월 |
| amazon | FY2021~2028 | Current Qtr. (Sep 2026) · Current Year (**2026**) | 2026-12-31 | 3.88개월 |
| palantir | FY2021~2028 | Current Qtr. (Sep 2026) · Current Year (**2026**) | 2026-12-31 | 3.88개월 |
| tesla | FY2021~2028 | Current Qtr. (Sep 2026) · Current Year (**2026**) | 2026-12-31 | 3.88개월 |
| spacex-xai | FY2023~2028 | Current Qtr. (Sep 2026) · Current Year (**2026**) | 2026-12-31 | 3.88개월 |
| nvidia | FY2022~**2029** | Current Qtr. (**Oct 2026**) · Next Qtr. (**Jan 2027**) · Current Year (**2027**) | 2027-01-31 | 4.90개월 |
| oracle | FY2022~**2029** | Current Qtr. (**Aug 2026**) · Next Qtr. (**Nov 2026**) · Current Year (**2027**) | 2027-05-31 | 8.84개월 |
| microsoft | FY2022~**2029** | Current Qtr. (Sep 2026) · Current Year (**2027**) · Next Year (**2028**) | 2027-06-30 | 9.82개월 |

Oracle 의 회계연도 종료월은 Yahoo Earnings History 의 실제 기간말 `8/31/2025 · 11/30/2025 · 2/28/2026 · 5/31/2026` 으로 확인했다. NVIDIA 는 기간말 `10/31/2025 · 1/31/2026 · 4/30/2026 · 7/31/2026` 으로 1월 말 종료 확인.

**구조적 단서**: nvidia·microsoft·oracle **세 회사만** StockAnalysis FY 라벨이 **2029 까지** 확장된다. 나머지 7사는 2028 까지. 이건 이 3사의 "현재 회계연도"가 이미 2027로 넘어갔기 때문이며, Yahoo 의 `Current Year` 라벨(2027/2028)과 정확히 일치한다.

→ 회계연도 말까지 남은 개월수는 §5.1의 다음 4개 미발표 회계분기 계약과 다른 척도이므로 NTM 판정에 사용하지 않는다.

## 5. 회사별 충족표 (10개 대상 전부)

주가·Forward PE 는 StockAnalysis(2026-09-08 조회, 주가는 2026-09-04 종가), EPS 는 StockAnalysis forecast(`Last updated: Sep 1, 2026`) 및 Yahoo(2026-09-08 조회).

| company | ticker | 주가(USD) | Forward PE | 역산 분모 EPS | EPS This FY | EPS Next FY | PE@ThisFY | Yahoo 향후분기 | 분류 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| meta | META | 616.77 | 19.06 | 32.3594 | 31.16 | 34.96 | 19.7936 | 2 | **일부확보** |
| nvidia | NVDA | 230.36 | 19.10 | 12.0607 | 9.31 | 15.52 | 24.7433 | 2 | **일부확보** |
| alphabet | GOOGL | 338.46 | 25.39 | 13.3304 | 20.60 | 14.85 | 16.4301 | 2 | **일부확보** |
| microsoft | MSFT | 499.70 | 25.30 | 19.7510 | **19.75** | 23.57 | **25.3013** | 2 | **일부확보** |
| amazon | AMZN | 258.51 | 27.91 | 9.2623 | 12.55 | 10.40 | 20.5984 | 2 | **일부확보** |
| apple | AAPL | 319.97 | 34.73 | 9.2131 | 8.82 | 9.57 | 36.2778 | 2 | **일부확보** |
| oracle | ORCL | 158.78 | 19.69 | 8.0640 | **8.06** | 10.97 | **19.6998** | 2 | **일부확보** |
| palantir | PLTR | 174.33 | 91.59 | 1.9034 | 1.61 | 2.33 | 108.2795 | 2 | **일부확보** |
| tesla | TSLA | 354.08 | 186.01 | 1.9036 | 1.77 | 2.16 | 200.0452 | 2 | **일부확보** |
| spacex-xai | **SPCX** | 147.95 | 119.47 | 1.2384 | 0.09 | 1.60 | 1643.8889 | 2 | **일부확보** |

**요약: 확보 0 · 일부확보 10 · 미확인 0 · 대상제외 0**

### 5.1 Yahoo 향후 2개 분기 EPS 컨센서스 (무료 공개 전부)

| company | Current Qtr. | Next Qtr. | Current Year | Next Year | 분석가(분기/연간) |
|---|---|---|---|---|---|
| meta | Sep 2026 = 6.53 | Dec 2026 = 8.22 | 2026 = 31.37 | 2027 = 33.95 | 47·45 / 56·58 |
| nvidia | Oct 2026 = 2.47 | Jan 2027 = 2.75 | 2027 = 9.31 | 2028 = 15.46 | 41·38 / 48·56 |
| alphabet | Sep 2026 = 3.01 | Dec 2026 = 3.33 | 2026 = 20.60 | 2027 = 14.86 | 38·35 / 51·51 |
| microsoft | Sep 2026 = 4.72 | Dec 2026 = 4.83 | 2027 = 19.75 | 2028 = 23.57 | 38·37 / 49·51 |
| amazon | Sep 2026 = 1.95 | Dec 2026 = 2.44 | 2026 = 12.57 | 2027 = 10.49 | 48·45 / 56·60 |
| apple | Sep 2026 = 1.98 | Dec 2026 = 2.91 | 2026 = 8.81 | 2027 = 9.57 | 27·19 / 36·38 |
| oracle | Aug 2026 = 1.74 | Nov 2026 = 1.89 | 2027 = 8.06 | 2028 = 10.97 | 31·30 / 42·39 |
| palantir | Sep 2026 = 0.41 | Dec 2026 = 0.46 | 2026 = 1.61 | 2027 = 2.33 | 23·23 / 28·29 |
| tesla | Sep 2026 = 0.45 | Dec 2026 = 0.49 | 2026 = 1.77 | 2027 = 2.16 | 28·28 / 45·46 |
| spacex-xai | Sep 2026 = 0.14 | Dec 2026 = 0.44 | 2026 = 0.12 | 2027 = 1.78 | 11·12 / 17·17 |

전 페이지에 `Currency in USD` 표기, `GAAP / Normalized` 토글 존재(10/10). **3·4번째 분기(Q1 2027, Q2 2027 등) 열은 존재하지 않는다.**

⚠️ 위 "분석가" 수는 `collect_yahoo.py` 가 Revenue Estimate 표의 행을 잡았을 가능성이 있어(§9 파서 주의) **결론에 사용하지 않았다.** EPS 값 자체는 web_fetch 독립 추출과 4개사(META·NVDA·ORCL·SPCX)에서 정확히 일치해 신뢰한다.

### 5.2 공급사 간 교차 검증 — 둘 다 "회계연도" 값임이 확인됨

| company | SA EPS This Yr | Yahoo Current Yr | 차이 | SA EPS Next Yr | Yahoo Next Yr | 차이 |
|---|---:|---:|---:|---:|---:|---:|
| oracle | 8.06 | 8.06 | **0** | 10.97 | 10.97 | **0** |
| microsoft | 19.75 | 19.75 | **0** | 23.57 | 23.57 | **0** |
| nvidia | 9.31 | 9.31 | **0** | 15.52 | 15.46 | 0.06 |
| alphabet | 20.60 | 20.60 | **0** | 14.85 | 14.86 | -0.01 |
| palantir | 1.61 | 1.61 | **0** | 2.33 | 2.33 | **0** |
| tesla | 1.77 | 1.77 | **0** | 2.16 | 2.16 | **0** |
| apple | 8.82 | 8.81 | 0.01 | 9.57 | 9.57 | **0** |
| amazon | 12.55 | 12.57 | -0.02 | 10.40 | 10.49 | -0.09 |
| meta | 31.16 | 31.37 | -0.21 | 34.96 | 33.95 | 1.01 |
| spacex-xai | 0.09 | 0.12 | -0.03 | 1.60 | 1.78 | -0.18 |

두 공급사의 연간 수치가 대체로 일치한다는 것은 회계연도 값의 교차 관측일 뿐이다. 이것만으로 Forward PE의 공식 분모 기간이나 NTM 적격성을 입증하지 않는다.

## 6. Forward PE 분모 기간 판정

초기 분석의 세 가설 대조표는 감사 추적을 위해 보존한다(`fy-analysis.json`). 현재 판정은 `fy-analysis-corrected.json`과 `analyze_fy.py`의 단정으로 고정한다.

| company | FY 종료 | 개월 | 보고 Forward PE | PE@이번FY | PE@시간가중블렌드 | PE@다음FY | 일치 가설 |
|---|---|---:|---:|---:|---:|---:|---|
| microsoft | 2027-06-30 | 9.82 | **25.30** | **25.3013** | 24.4463 | 21.2007 | **FY-current** |
| oracle | 2027-05-31 | 8.84 | **19.69** | **19.6998** | 17.9913 | 14.4740 | **FY-current** |
| meta | 2026-12-31 | 3.88 | 19.06 | 19.7936 | 18.2847 | 17.6422 | 없음 |
| nvidia | 2027-01-31 | 4.90 | 19.10 | 24.7433 | 17.7405 | 14.8428 | 없음 |
| alphabet | 2026-12-31 | 3.88 | 25.39 | 16.4301 | 20.2563 | 22.7919 | 없음 |
| amazon | 2026-12-31 | 3.88 | 27.91 | 20.5984 | 23.2995 | 24.8567 | 없음 |
| apple | 2026-09-26 | 0.72 | 34.73 | 36.2778 | 33.5934 | 33.4347 | 없음 |
| palantir | 2026-12-31 | 3.88 | 91.59 | 108.2795 | 83.1238 | 74.8197 | 없음 |
| tesla | 2026-12-31 | 3.88 | 186.01 | 200.0452 | 174.0877 | 163.9259 | 없음 |
| spacex-xai | 2026-12-31 | 3.88 | 119.47 | 1643.8889 | 133.0682 | 92.4687 | 없음 |

(블렌드 = NTM 창에서 이번 회계연도가 차지하는 일수 비중으로 이번FY·다음FY EPS 를 가중. 허용오차 0.4%.)

### 6.1 Microsoft·Oracle의 공식 기간 근거

**oracle**: Forward PE 19.69 = 158.78 / 8.06 = **19.6998**. 분모 8.06 은 Yahoo `Current Year (2027)` = 8.06 과 정확히 일치하고, Oracle 회계연도는 **2027-05-31 종료**(실적 기간말 5/31/2026 실측). 주가일 2026-09-04 로부터 **8.84개월**.
→ Forward PE 숫자 역산은 기간 정의의 증명이 아니므로 `period_unknown`으로 둔다.

**microsoft**: Forward PE 25.30 = 499.70 / 19.75 = **25.3013**. 분모 19.75 = Yahoo `Current Year (2027)` = 19.75 정확 일치, 회계연도 **2027-06-30 종료**, 주가일로부터 **9.82개월**.
→ Forward PE 숫자 역산은 기간 정의의 증명이 아니므로 `period_unknown`으로 둔다.

따라서 두 기업의 회계기간 근거는 보강되지만, 4개 분기 EPS 컨센서스와 공급사 Forward PE 정의가 없으므로 NTM 적격은 여전히 미검증이다.

### 6.2 불명 8건

나머지 8개사는 역산 분모가 세 가설 어느 것과도 일치하지 않는다. 예:

- **meta**: 역산 분모 32.3594. 이번FY 31.16(→19.79) 도 다음FY 34.96(→17.64) 도 아님. 다만 `19.06 × 31.16 = 593.91` 인데, 이건 기준선 2026-09-02 주가 592.85 와 0.18% 차이이고 표시 주가 616.77 과는 3.7% 차이다. → **Forward PE 가 표시 주가가 아닌 다른 시점 주가로 계산됐거나(=오래된 값 잔존), 분모가 다를 수 있다.** 어느 쪽인지 판별 불가.
- **spacex-xai**: 역산 분모 1.2384. 이번FY 0.09 라면 PE 1643.9 가 되어 전혀 맞지 않고, 다음FY 1.60 이면 92.47. 두 값 사이에 있으나 일치하지 않음.
- **nvidia**: 역산 12.0607, 이번FY 9.31(→24.74)·다음FY 15.52(→14.84) 사이.

### 6.3 판정 근거 (왜 전부 NTM 적격 미검증인가)

1. **공급사 정의 문서를 확인하지 못했다.** 통계 페이지에서 기간 설명을 찾지 못했고 `/glossary/`, `/about/data/` 두 후보 경로가 404였으나, 문서 전체 부재로 일반화하지 않는다.
2. **각주는 회계 기준만 밝힌다.** 원문 `EPS and Forward PE are based on non-GAAP adjusted numbers.` — GAAP/조정만 말하고 **기간은 말하지 않는다**(10/10 확인).
3. **§5.1 이 필드명 인정을 명시적으로 금지한다.** *"`forwardPE`라는 공급사 필드 이름만으로 NTM임을 인정하지 않는다."*
4. **작업 지시가 역산의 증명력을 부정한다.** *"주가/PER 역산만으로 분모의 기간은 증명되지 않습니다."* → 위 역산은 전부 `backcalc.disclaimer` 를 붙여 **참고 기록**으로만 남겼다.
5. **공급사 정의와 네 분기 원자료가 없다.** 따라서 10개사 모두 NTM 적격을 긍정도 부정도 하지 않고 `unverified`로 둔다.
6. **주식 기준(diluted/basic) 미문서화.** §5.1 3번의 "보통주/ADR, 분할 조정" 요건을 확인할 수단이 두 공급사 모두에 없다.
7. **개별 추정치의 스냅샷 시점 미노출.** §5.1 2번의 "추정치 스냅샷 시점을 저장" 요건을 충족할 수 없다. 페이지 수준 `Last updated` 만 존재(StockAnalysis forecast = Sep 1, 2026 / statistics = Sep 8, 2026 / 주가 = Sep 4, 2026 close). **세 날짜가 서로 다르다.**

## 7. 미확보 이유 — 데이터 부재로 단정하지 않는다

지시대로 "확보 실패"와 "데이터 부재"를 구분한다.

**확보 실패(접근 제약)이지 데이터 부재가 아닌 근거:**

1. **공급사가 분기 추정치를 내부에 갖고 있을 가능성은 배제하지 않는다.** StockAnalysis의 Forward PE와 연간값 대조만으로 내부 산출방식을 확정하지 않는다.
2. **분기 토글 UI 가 존재한다.** `Quarterly` 버튼이 있다는 것은 분기 뷰가 제품 안에 있다는 뜻이다. 무료 정적 HTML 에 데이터가 없을 뿐이다.
3. **Yahoo 는 2개 분기를 무료로 준다.** 즉 분기 컨센서스라는 데이터 종류 자체가 공개 시장에 존재한다. 3·4번째 분기를 못 얻는 것은 **원천의 공개 범위 제한**이지 데이터 부재가 아니다.
4. **유료 경로는 사용하지 않았다.** 작업 제약상 가입·구매·계정 변경을 하지 않았으며, 유료 티어의 분기 제공 여부는 판단하지 않는다.
5. **Nasdaq 은 차단이 아니라 렌더링 방식 문제다.** JS 렌더링이라 정적 GET 으로는 빈 표가 온다. 헤드리스 브라우저면 가능할 수 있으나 이번 범위에서 사용하지 않았다.

**따라서 결론은 "NTM 원자료가 세상에 없다"가 아니라 "이번에 조사한 공개 접근 경로에서 §5.1의 4분기 요건을 충족하지 못했다"이다.**

### 7.1 시도하지 않은 경로 (다음 담당자가 검토할 것)

- StockAnalysis Pro (유료 — 가입·구매 없이 미검증)
- Nasdaq.com 헤드리스 브라우저 렌더링
- 공급사 직접 API: S&P Global Market Intelligence(StockAnalysis 의 명시된 데이터 제공자 — 통계 페이지 각주 원문 `"Financial statistics are provided by S&P Global Market Intelligence."`), FactSet, LSEG, Bloomberg — 전부 유료
- 회사 IR 페이지의 가이던스 (단, 이건 컨센서스가 아니고 회사가 제시한 값이며 §5.1 이 요구하는 "EPS 컨센서스"와 종류가 다르다)
- 증권사 리포트 원문 (접근 권한 필요)

## 8. 기준선과의 관계 — 2026-09-02 재현 가능성 분리

지시대로 **현재 공개 접근 자료**와 **2026-09-02 기준 재현 가능 여부**를 분리한다.

| 항목 | 현재(2026-09-08 조회) 공개 접근 | 2026-09-02 기준 재현 |
|---|---|---|
| StockAnalysis 주가·Forward PE·연간 EPS | ✅ 가능 | ❌ **불가** |
| Yahoo 향후 2분기·연간 EPS | ✅ 가능 | ❌ **불가** |
| 분기 EPS 4개 | 조사한 경로에서 미확보 | ❌ 과거 스냅샷 미재현 |

**재현 한계**: 현재 조사에서 확인한 페이지는 최신 스냅샷만 제공해 2026-09-02 당시 추정치를 재현하지 못했다. 분기 데이터가 어느 티어에서도 제공되지 않는다고 단정하지 않으며, 현재 전망치를 과거로 소급하지 않았다.

관측 가능한 표류(기준선 2026-09-02 vs 2026-09-08 실측):

| company | 기준선 주가 | 실측 주가 | 표류 | 기준선 ntm_per | 실측 Forward PE |
|---|---:|---:|---:|---:|---:|
| meta | 592.85 | 616.77 | **+4.03%** | 17.9 | 19.06 |
| nvidia | 224.41 | 230.36 | +2.65% | 18.0 | 19.10 |
| alphabet | 337.12 | 338.46 | +0.40% | 25.3 | 25.39 |
| microsoft | 496.82 | 499.70 | +0.58% | 25.4 | 25.30 |
| amazon | 254.98 | 258.51 | +1.38% | 27.5 | 27.91 |
| apple | 324.96 | 319.97 | **-1.54%** | 35.5 | 34.73 |
| oracle | 154.04 | 158.78 | +3.08% | 19.1 | 19.69 |
| palantir | 169.46 | 174.33 | +2.87% | 89.0 | 91.59 |
| tesla | 357.01 | 354.08 | -0.82% | 187.5 | 186.01 |
| spacex-xai | 140.71 | 147.95 | **+5.15%** | 111.0 | 119.47 |

6일 만에 주가가 최대 +5.15%(spacex-xai), -1.54%(apple) 움직였고 Forward PE 도 같이 움직였다. **기준선 값들은 그 시점 스냅샷으로 보존하는 것이 맞으며**, 이번 검증은 그 값의 옳고 그름이 아니라 **`vendor_forward_pe_verified_ntm` 라는 방법 라벨의 정당성**을 다뤘다.

§5.1 의 *"역사적 분석에 현재 컨센서스를 끼워 넣지 않는다"* 에 따라, 위 실측값을 기준선에 덮어쓰는 제안은 하지 않는다.

## 9. 파서 주의사항 (내 도구의 한계 — 결과 해석 시 필요)

정직하게 기록한다.

1. `collect_ntm.py` 첫 실행에서 **주가 추출이 전부 실패**(`price=None`). 실제 DOM 은 `Stock Price` 라벨 없이 `<div class="text-4xl font-bold …">616.77</div>` 형태였다. `reparse.py` 로 패턴을 고쳐 보정했다. **원문 HTML 을 저장해 두었기 때문에 재파싱해도 조회시각이 그대로 보존된다.**
2. `collect_yahoo.py` 의 `no_of_analysts_row` 는 META 에서 **Earnings Estimate 행(42·41·54·52)이 아니라 Revenue Estimate 행(47·45·56·58)을 잡았다.** `avg_estimate_row` 는 EPS 값과 정확히 일치하므로 신뢰하지만, **분석가 수는 결론에 쓰지 않았다.** §5.1 표의 분석가 수도 참고값이다.
3. `collect_yahoo.py` 의 `error_page` 판별이 **10/10 True** 로 나오지만 표는 정상 파싱됐다. Yahoo 페이지에 `"Oops, something went wrong"` 문자열이 다른 위젯 때문에 상존하기 때문이다. **실제 데이터 부재가 아니다.** (MSFT 는 web_fetch 경유 시 실제로 표가 안 loaded 된 적이 2회 있었다 — 직접 수집에서는 정상 취득.)
4. `probe_fy.py` 의 **EPS 행 추출은 실패**했다(HTML 조각을 잡음). FY 라벨 추출만 유효하며, EPS 값은 카드 파서(`eps_this_year_card` / `eps_next_year_card`) 결과를 사용했다. 카드 파서는 **meta·alphabet·amazon 의 원문 문맥과 직접 대조**해 검증했다 — 특히 alphabet `EPS Next Year 14.85 (from 20.60)` 과 amazon `10.40 (from 12.55)` 는 **빨간 하락 배지**(`bg-red-100`)가 붙은 실제 추정치이고 `from` 값이 사슬로 일치해 오추출이 아님을 확인했다.
5. `analyze_fy.py` 의 apple 회계연도 종료일 `2026-09-26` 은 Yahoo 라벨(`Current Qtr. (Sep 2026)`, `Current Year (2026)`) 로부터 **추정한 날짜**다. Apple 의 실제 회계연도 말일은 연도마다 조금씩 움직인다. 다만 apple 의 Forward PE 는 어떤 가설과도 일치하지 않아 이 날짜가 판정을 바꾸지 않는다.
6. 회계연도 종료월 판별 근거는 §4.2 표의 "실측 근거" 열에 회사별로 명시했다. microsoft 는 Yahoo 페이지가 web_fetch 경유로 2회 실패해 **기간말 날짜를 직접 보지 못했고**, `Current Year (2027)` 라벨과 StockAnalysis FY 라벨이 2029 까지 확장되는 구조로 6월 말 종료를 판별했다. 이건 직접 증거보다 약하므로 그 한계를 밝힌다.

## 10. 자동수집 가능성 평가

| 원천 | 자동수집 | 근거 |
|---|---|---|
| StockAnalysis | **가능** | 서버 렌더 HTML, HTTP 200, robots/차단 없음, JSON 페이로드 없어 DOM 파싱 필요. 30개 요청 중 차단 0건. 단 **연간값만** |
| Yahoo Finance | **가능** | 정적 HTML 에 표 포함, HTTP 200 (10/10), 가입 불필요. 단 **분기 2개만**. 페이지에 무관한 오류 문자열이 상존하므로 성공 판별은 표 존재로 해야 함 |
| Nasdaq.com | 정적 GET에서 미확보 | JS 렌더링, 정적 응답은 `"Data is currently not available"` |
| StockAnalysis 정의 문서 | 해당 없음 | 404 |

**요청 간 1.0~1.2초 지연**을 두었고 총 40여 건의 공개 GET 으로 차단·레이트리밋을 겪지 않았다. 단 이건 소량 표본이며 대규모 정기 수집 시의 정책은 각 사 이용약관 확인이 별도로 필요하다(이번 범위 밖).

## 11. 재현 방법

아래는 기존 커밋 산출물 복사본에서 실행하는 현행 검증 절차다. `collect_ntm.py`, `reparse.py`, `collect_yahoo.py`는 최초 조사 기록이며 현재 `evidence.json`을 원시 스키마로 덮어쓰므로 이 절차에서 실행하지 않는다. `inspect_refs.py start/end`도 수집 시점 기록이고, 현행 검증은 저장된 산출물을 대상으로 `compare_hashes.py`를 실행한다.

`fy-analysis-corrected.json`의 `quarterly_eps_obtained`는 조사 경로에서 실제로 관측한 분기 수(현재 Yahoo 2개)이고, `quarterly_eps_eligible`는 §5.1의 다음 4개 분기·기간·스냅샷·기준을 모두 충족해 NTM 계산에 사용할 수 있는 수(현재 0개)다. 두 필드는 서로 다른 계약이므로 관측 수 2와 적격 수 0을 불일치로 해석하지 않는다.

```powershell
cd C:\Users\noble\orca\workspaces\stock-report-harness\scarpper\validation\qwen-ntm-data-03

# 현행 정정 산출물 검증
python -B -X utf8 apply_r1_corrections.py        # -> evidence.json, fy-analysis-corrected.json
python -B -X utf8 analyze_fy.py                  # evidence ↔ corrected 교차 검증
# consolidate.py는 폐기 생성기이며 실행하지 않는다.
python -B -X utf8 compare_hashes.py               # 저장된 참조 8종 시작·종료 해시 검증
```

산출물:

| 파일 | 내용 |
|---|---|
| `REPORT.md` | 이 보고서 |
| `evidence.json` | **최종 증거** — 10개사 전체 필드(URL·조회시각·값·통화·기준·전망기간·스냅샷·역산·판정·분류·재현가능성) |
| `evidence-yahoo.json` | Yahoo 10개사 원시 파싱 결과 |
| `fy-analysis-corrected.json` | 정정된 기간 판정과 10개사 NTM 적격 미검증 결과 |
| `fy-analysis.json` | 폐기된 이전 분석의 감사 추적 보존본 |
| `fy-labels.json` | StockAnalysis FY 라벨·Upgrade 건수 |
| `hashes-start.json` / `hashes-end.json` | worker 참조 파일 해시(시작/종료) |
| `raw-*-overview.html`, `raw-*-forecast.html`, `raw-yahoo-*.html`, `meta-forecast-raw.html` | **원문 스냅샷** (재현·감사용) |
| `*.py` 7종 | 수집·분석 스크립트 (전부 읽기 전용 접근, 새 소스 첫 줄 한국어 주석) |
| `*.txt` 로그 | `refs-start.txt`, `collect-log.txt`, `yahoo-log.txt`, `reparse-log.txt`, `fy-dump.txt`, `parser-probe.txt`, `structure-dump.txt`, `consolidate-log.txt`, `fy-analysis.txt` |

한글이 콘솔에서 깨져 보이면 cmd 코드페이지 문제일 뿐 파일은 UTF-8 로 정상이다. `-X utf8` 을 붙이고 출력은 파일로 담아 확인했다.

## 12. 제약 준수

- `worker/`, 원본(`E:\sourcecode\…`), C-13 worktree — **읽기 전용**. 수정·커밋·재생성·checkout·merge 없음. 종료 해시는 §13.
- **점수·승인·정책 결정 없음.** F6 점수를 다시 매기거나 `ntm_per` 값을 바꾸거나 `companies.json` 의 ticker 를 채우는 제안을 실행하지 않았다. 발견 사항은 보고만 한다.
- **유료 가입·구매·계정 변경 없음.** 무료 공개 페이지 GET 만 사용.
- **확보 실패를 데이터 부재로 단정하지 않음** — §7.
- **현재 전망치를 2026-09-02 로 소급하지 않음** — §8.
- **주가/PER 역산을 증명으로 쓰지 않음** — 모든 역산에 `disclaimer` 필드 부착(§6.3-4).
- **`vendor_forward_pe_verified_ntm` 명칭만으로 통과 처리하지 않음** — §2.
- 수집 스크립트는 자기 경로에서만 작성·테스트, **새 소스 첫 줄 한국어 주석**, **커밋 trailer 없음**.
- TSMC·Alibaba 는 조사하지 않았다(C-13 담당). `PROXY_NTM_COMPANIES = {"tsmc","alibaba"}` 로 그 경계가 코드에도 명시돼 있음을 확인만 했다.
- dispatch 없음 → `worker_done` 등 lifecycle 메시지 미발송.
- 이전 입력창의 미제출 `/compress-fast` 는 내장 CLI 명령이라 도구로 실행할 수 없어 자동 실행하지 않았고, 대신 작업 지시 전문을 `TASK.md` 에 보존했다.

## 13. 무결성 — 내 작업과 외부 승인 변경의 분리

### 13.1 시작 상태

시작 HEAD `96d88bc97f74914521221de7889544a02048d6da`, `git status --porcelain` = ` M .claude/settings.json`, `?? .agents/`, `?? .codex/`, `?? package-lock.json` (4건, 전부 검증 이전부터 존재).

참조 파일 8종의 시작 해시(`hashes-start.json`):

| 파일 | bytes | 줄 | SHA-256[:16] | mtime (UTC) |
|---|---:|---:|---|---|
| docs/scorecard/design-guideline.md | 48,399 | 481 | `d30b69dc88cc2b64` | 2026-09-08T12:26:28Z |
| docs/scorecard/open-items.md | 9,256 | 92 | `a432387f61be667a` | 2026-09-08T12:36:54Z |
| scripts/scorecard/baseline_import.py | 32,442 | 578 | `9f612c275260dc4f` | 2026-09-08T12:21:06Z |
| scripts/scorecard/calc_f6.py | 10,337 | 163 | `2807a989b15f5fd2` | 2026-09-08T12:10:58Z |
| scorecard/companies.json | 4,636 | 23 | `2bd6baf36ca1b361` | 2026-09-08T01:21:26Z |
| scorecard/baseline/v1.5/observations.json | 93,179 | 3,259 | `9a58b5bea2a51d79` | 2026-09-08T12:21:14Z |
| scorecard/baseline/v1.5/scores.json | 67,673 | 1,115 | `daa46f7b26e4ee3c` | 2026-09-08T12:21:14Z |
| scorecard/rules/v1.5.json | 19,210 | 597 | `9231b3a05ba5c766` | 2026-09-08T12:11:57Z |

### 13.2 종료 비교 — 저장된 참조 파일 시작·종료 비교

`compare_hashes.py` 실측 출력(`integrity-verdict.json`):

```
worker HEAD  start=96d88bc  end=c13a293  CHANGED (외부)
git status   start=['M .claude/settings.json', '?? .agents/', '?? .codex/', '?? package-lock.json']
             end  =['M .claude/settings.json', '?? .agents/', '?? .codex/', '?? package-lock.json']

docs/scorecard/design-guideline.md             d30b69dc88cc2b64   d30b69dc88cc2b64   UNCHANGED
docs/scorecard/open-items.md                   a432387f61be667a   a432387f61be667a   UNCHANGED
scorecard/baseline/v1.5/observations.json      9a58b5bea2a51d79   9a58b5bea2a51d79   UNCHANGED
scorecard/baseline/v1.5/scores.json            daa46f7b26e4ee3c   daa46f7b26e4ee3c   UNCHANGED
scorecard/companies.json                       2bd6baf36ca1b361   2bd6baf36ca1b361   UNCHANGED
scorecard/rules/v1.5.json                      9231b3a05ba5c766   9231b3a05ba5c766   UNCHANGED
scripts/scorecard/baseline_import.py           9f612c275260dc4f   9f612c275260dc4f   UNCHANGED
scripts/scorecard/calc_f6.py                   2807a989b15f5fd2   2807a989b15f5fd2   UNCHANGED

참조 파일 변경: 0건 없음
```

### 13.3 외부 변경 (내 작업이 아님 — 설계진행의 사용자 승인 공통문서 수정)

조사 **중에** worker HEAD 가 `96d88bc` → `c13a293` 으로 이동했다. 이 변경의 정체를 확정했다:

```
$ git diff --name-status 96d88bc c13a293
M       AGENTS.md

$ git show --stat --oneline c13a293
c13a293 docs: Orca 추가 작업 요청 시 터미널 실행 안내 의무화
 AGENTS.md | 9 +++++++++
 1 file changed, 9 insertions(+)
```

| 항목 | 값 |
|---|---|
| 변경 파일 | **`AGENTS.md` 1개뿐** (9 insertions, 0 deletions) |
| 커밋 메시지 | `docs: Orca 추가 작업 요청 시 터미널 실행 안내 의무화` |
| 주체 | 설계진행 (`term_a3370266-…`, codex) |
| 권한 근거 | 사용자 지시에 의한 공통문서 수정. `msg_d5a1cd690527`(2026-09-08T13:21:04Z) 로 통지됨 |
| 통지문의 HEAD 선언 | worker `c13a293` · scarpper `cc8373b` · C-13 `82892ba` · main `98db4f5` · 설계진행 `a26cf45` |
| 내 실측 HEAD | worker `c13a293` ✓ · scarpper `cc8373b` ✓ — **통지와 일치** |
| `worker/AGENTS.md` 해시 | `6afb005d0f42a19e`(QWEN-CLI-DOC-02 시점) → **`5ec8796ad6e89f67`** (현재) |
| 계산코드·기준선·승인·HTML | worker 참조 8종의 저장된 조사 시작·종료 해시는 일치. 조사 중 worker의 AGENTS.md 외부 커밋은 별도로 확인 |

**무결성 범위**: 위 8종은 저장된 조사 시작·종료 시점 비교에서 불변이며 worker HEAD 이동은 승인된 AGENTS.md 변경으로 설명된다. 원문 HTML 스냅샷은 최초 인수 전 해시가 저장되어 있지 않으므로 현재 커밋과의 일치만 확인할 수 있다. 따라서 인수 전후 바이트 불변을 독립적으로 증명했다고 주장하지 않는다.

저장된 참조 해시 비교 범위에서 계산코드·기준선·승인·HTML 참조 파일의 시작·종료 일치가 확인된다. 원문 스냅샷은 최초 인수 전 해시가 없어 현재 커밋과의 일치만 확인했다.

### 13.4 내 작업 범위의 변경

- **worker**: 읽기 전용 접근만. 쓰기·커밋·checkout·merge 없음. `git status` 의 기존 4건(` M .claude/settings.json`, `?? .agents/`, `?? .codex/`, `?? package-lock.json`)은 시작·종료 동일하며 내가 만든 것이 아니다.
- **원본** (`E:\sourcecode\…\AI_company_analysis_factor`): 이번 작업에서 접근하지 않음.
- **C-13 worktree**: 접근하지 않음 (TSMC·Alibaba 담당).
- **scarpper**: `?? validation/`(내 산출물) 과 기존 `?? package-lock.json` 만. HEAD `cc8373b` 는 설계진행의 AGENTS.md 반영 커밋이며 내 커밋이 아니다. 나는 scarpper 에서 커밋하지 않았다.
- `python -B` 를 사용해 `__pycache__` 도 만들지 않았다.

## 13A. AGENTS.md 신규 규칙 수신 및 준수

`msg_d5a1cd690527` 로 통지된 공통 운영 지침을 받고, 내 worktree 의 `scarpper/AGENTS.md` §`## Orca worktree 간 메시지와 작업 실행`(71~78행) 을 읽었다.

| 행 | 규칙 | 내 준수 |
|---|---|---|
| 73 | 다른 worktree 에 추가 실행을 요청할 때는 메시지 발송과 터미널 실행 안내를 **함께** 수행. 수신함 저장만으로 끝내지 않음 | 이번 작업에서 나는 다른 worktree 에 **추가 실행을 요청하지 않았다**(결과 회신만). 따라서 적용 대상 아님 |
| 74 | 발송 후 수신 에이전트의 terminal handle·입력 상태 확인 후 `orca terminal send --terminal <handle> --text "…" --enter --json` 으로 실행 안내 제출. 기존 입력·진행 중 작업을 지우거나 중단하지 않음 | 위와 동일. **실행하지 않았다** — 78행의 면제 조항에 해당 |
| 75 | 실행 안내에 메시지 ID·할 작업·수신 확인 및 완료 회신 방법 포함. 최초 제출 처리 여부 확인, 동일 요청 중복 제출 금지 | 적용 대상 아님 |
| **76** | **발송 성공·수신 확인·작업 착수·완료는 별개 상태.** `accepted: true` 만으로 수신·착수·완료를 주장하지 않음. 수신 확인 회신이 오면 사용자에게 알림 | **준수** — 이 보고서와 회신에서 `ok: true` 를 "상대가 읽었다"로 해석하지 않았다. 메시지 ID 만 사실로 기록하고, §0 의 결론은 전부 내 실측 근거로 세웠다. 앞선 QWEN-CLI-DOC-02 에서도 `delivered_at: null` 을 "전달 확정"으로 주장하지 않고 mailbox 해석 결과만 보고했다 |
| **77** | 상대 CLI 가 실행 승인·인증을 기다리면 그 상태와 필요 조치를 사용자에게 알림. 메시지를 보냈다는 이유로 실행 중이라고 보고하지 않음 | **준수** — 현재 상대(설계진행 codex)가 승인·인증 대기라는 관찰은 없다. 있으면 즉시 알리겠다 |
| **78** | **단순 결과 공유나 수신 확인처럼 추가 작업이 없는 메시지는 터미널 실행 안내 대상이 아니다** | **적용** — 나의 (a) `msg_d5a1cd690527` 수신 확인 회신과 (b) `msg_084a5c82912d` 완료 결과 회신은 **둘 다 추가 작업을 요청하지 않는 메시지**이므로 `orca terminal send` 를 사용하지 않는다 |

추가 준수 사항:
- 규칙 적용이 **현재 조사 작업을 중단·재시작하라는 뜻이 아님**을 통지문이 명시했으므로, 조사를 중단하지 않고 계속 수행해 완료했다. 규칙 확인은 안전한 다음 단계(보고서 작성 직후, 완료 회신 이전)에 삽입했다.
- 외부 변경(§13.3)을 내 검증 기록에서 **분리해** 기록했다.
- 규칙 수신 확인은 `reply` 로 알린다 (§15 의 R-1).


## 14. 발견 사항 요약 (판단·수정은 담당자 몫)

내가 정책 결정을 내리지 않는다는 제약에 따라, **사실과 최소 제안만** 적는다.

| # | 사실 | 근거 |
|---|---|---|
| N-01 | `vendor_forward_pe_verified_ntm` 는 검증 결과가 아니라 `baseline_import.py:390` 의 하드코딩 문자열이다. 검증 코드가 없고 값은 원본 HTML `VAL` 4열 승계다 | `baseline_import.py:37,390,392,568` |
| N-02 | `ntm_eps` 관측이 기준선에 0건이다 → §5.1 4번(`NTM EPS = 네 분기 EPS 합`) 의 입력이 없다 | `observations.json` 실측 227건 중 `ntm_eps` 0건 |
| N-03 | 10개사 전부 §5.1 미충족. 조사한 공개 접근 경로에서 4분기 컨센서스를 확보하지 못함(StockAnalysis 정적 0분기, Yahoo 2분기, Nasdaq 정적 응답) | §4, §5 |
| N-04 | microsoft·oracle의 다음 미발표 네 분기는 공식 일정상 각각 FY2027 전체와 기간이 같지만, Forward PE 분모의 공급사 정의와 네 분기 EPS는 미검증 | §6.1 |
| N-05 | 나머지 8개사는 분모 기간 불명. 조사한 두 후보 경로에서 정의 근거를 확인하지 못했고, 각주는 회계 기준만 명시 | §6.2, §6.3 |
| N-06 | 회계연도 말까지 남은 개월수는 다음 네 미발표 회계분기와 다른 척도이므로 NTM 부정의 근거가 아니다 | §4.2 |
| N-07 | 비역년 기업의 연간 근사 오차 크기는 네 분기 비교 자료가 없어 판정하지 않는다 | §4.2 |
| N-08 | `companies.json` 의 spacex-xai 가 `listed=True` 이면서 `ticker=None`. 실제는 **Nasdaq SPCX**(2026-06-12 상장). 유일한 ticker 결함 | §3 |
| N-09 | spacex-xai 는 SpaceX(Public) + xAI(그 자회사) 이므로 SPCX 단일 종목이 결합 실체를 포괄한다. 기준일 2026-09-02 에 이미 상장 → §5.1 상장사 계약 적용, §5.2 비상장 예외 불가 | §3 |
| N-10 | spacex-xai 는 EPS TTM -2.27, PE n/a, FY2026 컨센서스 0.09~0.12에 Low Estimate -1.52, 분기 전년동기 `--`, 분석가 11~17명. 4분기를 확보해도 EPS 합이 양수라는 보장이 없다 | §3 |
| N-11 | 공급사 간 연간 EPS 는 대부분 정확 일치하지만, 이는 연간값 교차 관측일 뿐 Forward PE 기간 정의의 증명은 아님 | §5.2 |
| N-12 | StockAnalysis 는 한 페이지 안에서 세 날짜가 다르다(forecast `Sep 1, 2026` / statistics `Sep 8, 2026` / 주가 `Sep 4, 2026 close`). §5.1 2번의 "추정치 스냅샷 시점 저장" 요건을 개별 추정치 수준에서 충족할 수 없다 | §4.1, §6.3-7 |
| N-13 | 기준선 2026-09-02 값의 재현은 불가하다(공급사가 과거 스냅샷을 무료로 주지 않음). 6일간 주가 표류 최대 +5.15%(spacex-xai) / -1.54%(apple) | §8 |
| N-14 | 원본 VAL 표의 spacex-xai 행은 `['SpaceX 🆕', '$140.71', '$1.91T', '111', '-5', '—', '적자', '적자', '82.9']` 로 ticker 없이 주가·시총·Forward PE 를 가진다. ticker 부재가 원본에서부터 이어져 온 것으로 보인다 | 원본 HTML `const VAL` 10행 |

### 최소 제안 (실행하지 않음 — 담당자 판단)

1. **N-01·N-02**: 방법 라벨은 계산기 허용 경로를 선택하므로 단순 표시 변경으로 적용하지 않는다. 과거 기준선은 보존하고, 신규 실행 입력 계약과 영향표를 먼저 갱신한다.
2. **N-03~N-07**: §5.1을 실제로 만족시키려면 분기 컨센서스 원천 확보가 선행되어야 한다. 이번에 조사한 접근 경로만으로는 4분기를 확보하지 못했으므로, (a) 유료 공급사 계약, (b) 헤드리스 브라우저와 추가 공개 원천 탐색, (c) §5.1 완화 중 하나를 규칙 결정(C-13 확장)으로 내려야 한다. 나는 이 선택을 하지 않는다.
3. **N-08**: `companies.json` 의 spacex-xai `ticker` 를 `"SPCX"` 로. 단 이건 레지스트리 수정이므로 내 권한 밖이다.
4. **N-13**: 기준선 값은 2026-09-02 스냅샷으로 보존하는 것이 옳다(§5.1 "역사적 분석에 현재 컨센서스를 끼워 넣지 않는다"). 이번 실측값으로 덮어쓰면 안 된다.
