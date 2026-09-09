# F6-IMPLEMENT-06 — 승인된 F6 정책 구현

작성일 2026-09-09. 담당 worker(HANSOLJJ/worker). 요청 메시지 `msg_dd16d7f46560`.

`../f6-policy-decision-05/REPORT.md` 에서 권고하고 승인받은 정책을 코드·테스트·HTML 렌더에 반영했다.

## 1. 결과 요약

| 항목 | 결과 |
|---|---|
| 기존 baseline 승인 | **유지**. `approval hashes match current inputs` PASS |
| 기존 점수 | **불변**. `results.json` sha256 `4eb8c7d7…` 그대로 |
| 산출 HTML | **바이트 단위 동일** (`diff` 무차이) |
| 테스트 | 54 건 → **73 건** 전부 통과 (신규 19 건) |
| 규칙 파일 | **건드리지 않음**. `v1.5.json` 무변경 |
| C-06 · C-13 | **결정값 미확정**. `run.json.decisions` 무변경, 규칙 status 무변경 |

**변경 파일 4 개.** `scripts/scorecard/schema.py`, `scripts/scorecard/calc_f6.py`, `scripts/scorecard/render_html.py`, `tests/*` 2 개.

## 2. 왜 규칙 파일을 고치지 않았는가

승인 해시는 `rules` · `observations` · `judgments` · `run` · `results` · `draft` 여섯이다. `scorecard/rules/v1.5.json` 을 한 글자라도 고치면 `rule_hash` 가 바뀌어 **기존 승인이 즉시 무효**가 된다. 이 세션에서 이미 한 번 겪은 사고다.

따라서 정책을 **계산기 코드**에 구현했다. 코드 파일은 승인 해시 대상이 아니다. 다만 계산 결과가 달라지면 `results deterministic recompute` 검사가 실패하므로, **기존 실행의 결과를 바꾸지 않는 범위**로 설계해야 했다. 3.6 에서 그 조건을 어떻게 만족했는지 적는다.

정책을 규칙 파일에 반영하는 것은 **새 규칙 버전(v1.6)의 일**이다. 별도 과제로 남긴다(6 절).

## 3. 구현 내용

### 3.1 분기 EPS 관측 도입 — `schema.py`

```python
"ntm_eps_quarter": {"unit": "USD/share", "type": "number"},
```

`PERIOD_REQUIRED_METRICS` 에 추가했다. **분기 EPS 는 어느 분기인지가 값의 일부**이므로 `verified` 관측에 `period` 를 강제한다. 기간 없이는 4 분기 연속 판정이 불가능하다.

#### 중복 검사 키 확장

기존 중복 검사는 `(company_id, metric, as_of)` 를 키로 삼았다. 같은 날 수집한 4 개 분기 EPS 는 **값이 서로 다르므로 충돌로 오판**된다. 키에 기간을 넣어 해결했다.

```python
period = item.get("period") or {}
key = (item["company_id"], item["metric"], item["as_of"], period.get("start"), period.get("end"))
```

기존 관측은 전부 `period` 가 `null` 이라 키가 그대로다. **baseline 영향 없음.**

### 3.2 분기 경로 — `calc_f6.py`

`_listed` 진입 직후에 분기 경로를 둔다.

```python
quarterly = _quarterly(company, obs, rules)
if quarterly is not None:
    return quarterly
```

**분기 관측이 하나라도 있으면 그 경로가 F6 를 결정한다.** 승계 `ntm_per` 로 우회 채점되지 않는다(테스트 `test_quarterly_path_overrides_legacy_ntm_per`). 분기 관측이 없으면 기존 로직 그대로다.

분기 라벨은 `period.end` 의 **종료 월**에서 `YYYYQn` 으로 유도한다. 3·6·9·12 월로 맞추지 않으므로 NVDA(1 월 결산)·ORCL(5 월 결산)처럼 어긋난 회계연도도 그대로 처리된다.

### 3.3 부분 확보 — 점수 없음, 보존은 함

```
확보 < 4  →  status = pending_data,  score = None
             calc.coverage = {secured, required, quarters, sources}
             pending.message = "… N개 확보 — 나머지 (4-N)개 필요. 부분 합계를 배수로 늘려 쓰지 않는다"
```

**2Q×2 는 구현하지 않았다.** 코드에 합산·배수 경로 자체가 없다. 테스트 `test_two_quarters_never_doubled` 가 `calc` 에 `ntm_eps` 와 `ntm_per` 가 **없음**을 고정한다. 값이 틀리는지가 아니라 **존재하지 않는지**를 검사하므로 나중에 누가 추가하면 즉시 깨진다.

### 3.4 4분기 채점 관문

4 개가 모여도 아래를 모두 통과해야 점수가 된다. 하나라도 걸리면 `pending_data` 에 구체적 사유가 남는다.

| # | 관문 | 사유 |
|---|---|---|
| 1 | 4 개 정확히 | 초과하면 채점 창이 하나로 확정되지 않는다 |
| 2 | 연속 분기 | 기존 `_quarters_problem` 재사용 |
| 3 | 전부 `verified` | 승계·미검증 관측은 정식 점수에 못 들어간다 |
| 4 | **공급사 단일** | `source_id` 가 2 종 이상이면 차단 |
| 5 | 통화 단일·주가와 일치 | 분기별로 갈리면 차단 |
| 6 | 주식 기준 단일·레지스트리·주가와 일치 | ADR/ADS 혼입 차단 |
| 7 | **회계 기준 확정** | `basis.accounting` 이 없거나 갈리면 차단 (GAAP/비GAAP) |
| 8 | **ADR/ADS 는 basis 검산 기록** | `basis.basis_verified` 없으면 차단 |
| 9 | EPS 합 > 0 | 0 이하를 낮은 PER·0 점으로 바꾸지 않는다 |

4·7·8 이 이번에 새로 추가한 관문이다. 각각 공급사 혼합 금지, GAAP 정의 확인, TSM·BABA 기준 검산에 대응한다.

### 3.5 근사(proxy) 차단

```python
if choice == "accept_proxy_with_flag":
    return factor_result(..., status="pending_data", calc=proxy_calc,
                         pending=pending_info("data", "C-13 을 accept_proxy_with_flag 로 두었으나 "
                             "F6 정책상 근사(annual_weighted_proxy)는 점수를 만들지 않는다 — "
                             "미발표 4개 분기 컨센서스(consensus_4q_sum) 필요"))
```

**C-13 을 확정하지 않았다.** 결정을 기록하는 경로는 그대로 살아 있고, 미결이면 여전히 `needs_rule_decision` 으로 결정을 요구한다. 다만 `accept_proxy_with_flag` 를 골라도 **정식 점수는 만들어지지 않고** 근사값이 `calc` 에 참고로 보존된다.

**솔직한 유보.** 이 구현은 `accept_proxy_with_flag` 의 실질 효과를 없앤다. 규칙 파일의 선택지 정의와 코드 동작이 어긋난 상태이므로, **v1.6 에서 선택지 자체를 정리하는 것이 옳다**(6 절). 지금은 승인 보존이 우선이라 코드에만 반영했다.

### 3.6 기존 실행에 영향이 없는 이유

| 변경 | baseline 영향 |
|---|---|
| `ntm_eps_quarter` 추가 | 기존 관측에 없음 → 분기 경로 미진입 |
| 중복 키에 기간 추가 | 기존 관측은 `period=null` → 키 동일 |
| `PERIOD_REQUIRED_METRICS` 추가 | 새 지표에만 적용 |
| proxy 차단 | TSMC·Alibaba 는 C-13 **미결**이라 기존에도 `needs_rule_decision` → 동일 |
| `vendor_forward_pe_verified_ntm` | **건드리지 않음**. 10 개사 F6 점수 그대로 |
| 렌더 coverage 분기 | `coverage` 없으면 기존 문구 그대로 |

`vendor_forward_pe_verified_ntm` 을 차단하지 않은 것은 의도적이다. 요청은 "2Q×2 및 `annual_weighted_proxy` 차단" 이었고, 승계 공급사 forward PE 까지 막으면 상장 10 개사 점수가 전부 바뀌어 기존 승인이 깨진다. 새 실행에서는 분기 관측이 우선하므로(3.2) 자연히 대체된다.

### 3.7 재승인 게이트

자동 승격이 없다. 4 분기 관문을 통과한 결과에는 표식이 붙는다.

```python
calc["requires_reapproval"] = True
warnings = ["분기 컨센서스 4개 합산(<원천>) — 입력이 바뀐 실행이므로 재계산·재검토·재승인을 거쳐야 확정된다"]
```

실제 차단은 기존 기구가 한다. 분기 관측을 넣으면 `observations` 해시가 바뀌고, `current_hashes` 와 `approval.json` 이 어긋나 빌드가 `awaiting_user` 로 멈춘다. **표식은 화면과 결과 JSON 에 그 사실을 남기는 역할**이다.

### 3.8 SPCX 단일 법인

`companies.json` 은 앞선 과제(`../spacex-f6-recheck-01/`)에서 이미 갱신했다. 이번에는 **회귀 테스트로 고정**했다.

- `ticker == "SPCX"`, `exchange == "NASDAQ"`, `listed == True`
- `scope` 에 "단일 법인" 포함, **"합산 평가 범위" 미포함**
- `share_basis == "common"`, `reporting_currency == "USD"`

라벨이 다시 "합산" 으로 돌아가면 테스트가 깨진다.

### 3.9 HTML 렌더

`factor_calc_text` 에 coverage 분기를 추가했다.

```
분기 컨센서스 2/4 확보 (2026Q3, 2026Q4) · 원천 SRC-q · <미충족 사유>
분기 컨센서스 4/4 확보 (…) · 원천 SRC-q → NTM PER 25.0 · 구간 20~29 · 재승인 필요
```

**부분 확보를 숨기지 않는다.** 몇 개를 확보했고 어느 분기가 있으며 원천이 무엇인지 그대로 보여준다.

## 4. 검증

### 4.1 회귀 테스트

```
Ran 73 tests — OK   (기존 54 + 신규 19)
```

신규 19 건의 내역이다.

| 클래스 | 건수 | 고정하는 것 |
|---|---|---|
| `TestF6QuarterlyPolicy` | 12 | 2Q·3Q pending, 2Q×2 부재, 4Q 채점, 공급사 혼합·비연속·미검증·회계기준·통화·ADR 검산 차단, 합 0 이하 차단, 분기 경로 우선 |
| `TestSpacexSingleEntity` | 3 | SPCX 티커·거래소·단일 법인 scope·통화·주식 기준 |
| `TestF6CoverageRender` | 3 | 부분/완전 coverage 문구, 기존 경로 불변 |
| `TestF6` 수정 | 1 | `accept_proxy_with_flag` 가 더는 점수를 만들지 않음 |

기존 테스트 `test_c13_proxy_requires_decision` 은 옛 동작(proxy → 점수 0)을 고정하고 있어 **정책에 맞게 갱신**했다. 미결 시 `needs_rule_decision` 을 요구하는 부분은 그대로 두고, 결정 시 점수가 나던 부분을 `test_c13_accept_proxy_no_longer_scores` 로 분리해 새 동작을 고정했다.

### 4.2 계약 검증

```
[PASS] report contract: ai-scorecard-2026-09-baseline
  ok - scorecard plan frontmatter
  ok - run.json/observations/judgments strict schema
  ok - research bound to input hashes
  ok - results deterministic recompute      ← 점수 불변
  ok - draft ranking table matches results
  ok - review 4-area + checklist structure
  ok - approval hashes match current inputs ← 승인 유지
  ok - HTML exists, marker-free, bound to results
```

### 4.3 산출물 대조

```
python scripts/build_report.py ai-scorecard-2026-09-baseline  → Build complete
diff <이전 HTML> <재빌드 HTML>                                → 차이 없음
sha256(results.json)                                          → 4eb8c7d7… (불변)
```

## 5. 하지 않은 것

- **규칙 파일 수정 없음.** `v1.5.json` 무변경(2 절).
- **C-06 · C-13 결정 미확정.** `run.json.decisions` 는 빈 배열 그대로이고 규칙의 `status: pending` 도 그대로다.
- **관측 추가 없음.** 분기 EPS 관측을 실제로 넣지 않았다. 스키마와 계산 경로만 열었다. 실제 수집은 원천 약관 문제가 남아 있다(`../nasdaq-eps-expansion-04/`, `../f6-policy-decision-05/`).
- **`vendor_forward_pe_verified_ntm` 차단 없음.** 3.6 의 이유.
- **점수·승인 변경 없음.**

## 6. 남은 작업 제안

1. **v1.6 규칙 개정.** 코드에 넣은 정책을 규칙 파일로 올린다. `accepted_ntm_methods` 에서 `vendor_forward_pe_verified_ntm` 을 빼고, C-13 선택지를 정리하며, 관문 4·7·8 을 명문화한다. 새 규칙 버전이므로 기존 승인은 그대로 보존된다.
2. **`accept_proxy_with_flag` 정리.** 3.5 의 유보. 규칙 정의와 코드 동작이 어긋난 상태를 오래 두지 않는다.
3. **분기 관측 수집.** 원천 약관이 정리되어야 시작할 수 있다.
4. **`basis_verified` 기록 방법 표준화.** 지금은 불리언만 요구한다. 검산 근거(역산 주식수·비교 대상)를 어디에 남길지 정하면 좋겠다.

## 7. 재현 방법

```bash
cd worker
npm test                                                   # 73 건
python scripts/validate_report_contract.py ai-scorecard-2026-09-baseline
python scripts/build_report.py ai-scorecard-2026-09-baseline
sha256sum scorecard/runs/ai-scorecard-2026-09-baseline/results.json   # 4eb8c7d7…

# 정책 동작 직접 확인
python -X utf8 -m unittest tests.test_scorecard_calc.TestF6QuarterlyPolicy -v
python -X utf8 -m unittest tests.test_scorecard_render.TestF6CoverageRender -v
```
