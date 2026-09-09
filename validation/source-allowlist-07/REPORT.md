# SOURCE-ALLOWLIST-07 — api.nasdaq.com 생산 배제와 v1.6 원천 allowlist

작성일 2026-09-09. 담당 worker(HANSOLJJ/worker). 요청 메시지 `msg_4dbc3ff96950`.

정책 결정("무료 `api.nasdaq.com` analyst earnings-forecast 를 생산 원천에서 영구 배제")을 규칙·코드·회귀 테스트에 반영했다.

## 1. 결과 요약

| 항목 | 결과 |
|---|---|
| 규칙 | **`scorecard/rules/v1.6.json` 신설** (status `draft`). v1.5 는 무변경 |
| 기존 승인 | **유지**. `approval hashes match current inputs` PASS |
| 기존 점수 | **불변**. `results.json` sha256 `4eb8c7d7…` |
| 산출 HTML | **바이트 단위 동일** |
| 테스트 | 73 건 → **91 건** 전부 통과 (신규 18 건) |
| 생산 입력의 Nasdaq 참조 | **없음**. `sources.json` 3 건 모두 `url: null` |

## 2. v1.5 를 고치지 않고 v1.6 을 만든 이유

승인 해시에 `rules` 가 들어 있다. `v1.5.json` 을 고치면 `rule_hash` 가 바뀌어 승인된 실행이 즉시 무효가 된다. 새 버전 파일을 만드는 것은 기존 실행에 영향이 없다. 실행은 `run.json.rule_version` 으로 자기 규칙을 고정하기 때문이다.

v1.6 은 **v1.5 의 채점 규칙을 그대로 복사하고 원천 정책만 더한 초안**이다. `scoring` · `factors` · `policies` · `checklist` · `decisions` 다섯 블록이 v1.5 와 바이트 단위로 같은지 테스트로 고정했다(`test_v16_keeps_v15_scoring_untouched`). 원천 정책을 넣다가 점수 규칙이 딸려 바뀌는 사고를 막는다.

`status` 는 `draft` 다. 아직 어떤 실행도 v1.6 을 쓰지 않는다.

## 3. 원천 정책 구조

`rules.sources` 블록이다.

### 3.1 배제 — `denied`

```json
{
  "host": "api.nasdaq.com",
  "reason": "생산 원천 영구 배제. robots.txt 가 User-agent * 에 Disallow / 이고
             이용약관이 automated or manual process 로 데이터를 캡처하는 것을 금지한다",
  "decided_at": "2026-09-09",
  "scope": "자동 수집·관측 등록·F6 점수 계산·HTML 리포트 근거 전부",
  "existing_samples": "이미 확보한 표본은 validation/ 보고서에 참고용 증거로만 보존하고
                       생산 입력(observations·sources)에 넣지 않는다",
  "evidence": "validation/nasdaq-eps-expansion-04/REPORT.md 3절"
}
```

요청의 네 가지 금지(자동 수집·관측 등록·F6 점수 계산·HTML 리포트 근거)를 `scope` 에 명시하고, 기존 표본의 취급을 `existing_samples` 에 남겼다.

### 3.2 조건부 후보 — `conditional_candidates`

```json
{
  "name": "Nasdaq Data Link ZACKS/EE·EEH",
  "host": "data.nasdaq.com",
  "status": "candidate_not_approved",
  "note": "무료 api.nasdaq.com 과 다른 별도 상품·별도 약관이다. 아래 다섯이 모두 서면 확정될 때만 후보로 승격한다",
  "required_written_conditions": ["정식 계약", "자동 수집 허용", "derived data 허용", "외부 배포 허용", "보관 조건"]
}
```

**후보는 허용이 아니다.** `data.nasdaq.com` URL 을 쓰면 검증기가 다섯 조건을 나열하며 막는다. 승격은 서면 확정 뒤에 규칙을 다시 고쳐야 한다.

### 3.3 허용 — `allowed`

| host | 근거 |
|---|---|
| `data.sec.gov` | User-Agent 표기·요청 한도 준수 조건으로 프로그램 접근 허용 |
| `www.sec.gov` | 같은 조건 |
| `finnhub.io` | API 키 발급 기반 |
| `financialmodelingprep.com` | API 키 발급 기반 |

**Yahoo(`query*.yahoo.com`)는 넣지 않았다.** `../f6-policy-decision-05/REPORT.md` 2.2 에서 상류 API 가 "personal use only" 임을 확인했고 약관 검토가 선행 조건으로 남아 있다. 검토 전에 등재하면 Nasdaq 에서 저지른 순서 실수를 반복한다. **가격 용도의 기존 yfinance 사용은 `AGENTS.md` 관행이며 이 allowlist 는 `sources.json` 에 등재되는 생산 원천을 대상으로 한다.** 이 구분을 4.3 에 적는다.

## 4. 구현

### 4.1 스키마 — `schema.py`

`validate_rules` 의 optional 키에 `sources` 를 추가하고 `_validate_source_policy` 를 넣었다. **정책이 모순되게 쓰이는 것을 막는다.**

- 같은 host 가 `allowed` 와 `denied` 에 동시에 있으면 거부. 판정이 갈린다.
- `denied` 항목은 `reason` 이 비어 있으면 거부. 사유 없는 배제를 남기지 않는다.
- 조건부 후보의 `status` 는 `candidate_not_approved` 만 허용. **미승인 후보를 승인된 것처럼 표기할 수 없다.**
- `required_written_conditions` 가 비면 거부.
- 후보 host 가 `allowed`/`denied` 와 겹치면 거부.

### 4.2 판정 — `rules.py`

```python
RuleSet.source_policy          # 정책 블록. 없는 버전은 None
RuleSet.source_violation(url)  # 위반이면 사유 문자열, 통과면 None
```

호스트 비교는 정확히 일치하거나 서브도메인일 때 걸린다(`x.api.nasdaq.com` 도 배제). `url` 이 `None` 이면 검사 대상이 아니다 — 내부 기준선 원천이 여기 해당한다.

판정 순서는 **denied → conditional → allowed → 미등재**다. 배제가 가장 먼저다.

### 4.3 검증기 배선 — `validate.py`

```python
def check_source_allowlist(rules, sources, result) -> bool:
    if not rules.source_policy:
        return False          # 정책 없는 버전은 검사 자체를 건너뛴다
    for item in sources.get("items", []):
        violation = rules.source_violation(item.get("url"))
        if violation:
            result.error(f"sources.json {item.get('source_id')}: {violation}")
    result.check("자료 원천 allowlist")
    return True
```

`validate_scorecard` 안에서 호출한다. 테스트를 위해 함수로 분리했다.

**검사 대상은 `sources.json` 에 등재된 생산 원천이다.** 조사 과정에서 무엇을 열어 봤는지가 아니라, 채점 근거로 선언된 것이 무엇인지를 본다. 이 경계가 명확해야 `validation/` 보고서의 참고 증거와 생산 입력이 섞이지 않는다.

## 5. 검증

### 5.1 회귀 테스트 — 신규 18 건

| 클래스 | 건수 | 고정하는 것 |
|---|---|---|
| `TestSourceAllowlist` | 8 | v1.5 무정책, api.nasdaq.com 배제, 서브도메인 매칭, data.nasdaq.com 미승인 후보와 다섯 조건, 허용 host 통과, 미등재 거부, null URL 예외, **v1.6 채점 규칙 = v1.5** |
| `TestSourcePolicySchema` | 6 | 유효 정책 통과, allowed∩denied 거부, 사유 없는 denied 거부, 승인 표기 후보 거부, 빈 조건 거부, 후보 host 중복 거부 |
| `TestSourceAllowlistEnforcement` | 4 | v1.5 는 검사 건너뜀, v1.6 은 배제 원천을 오류로 잡음, 허용·null 통과, 조건부 후보 차단 |

```
Ran 91 tests — OK   (기존 73 + 신규 18)
```

### 5.2 계약 검증과 산출물

```
[PASS] report contract: ai-scorecard-2026-09-baseline   (8개 항목)
  ok - results deterministic recompute      ← 점수 불변
  ok - approval hashes match current inputs ← 승인 유지
diff <이전 HTML> <재빌드 HTML>              → 차이 없음
sha256(results.json)                        → 4eb8c7d7… (불변)
```

기존 실행은 v1.5 를 쓰므로 allowlist 검사 항목이 아예 나타나지 않는다. 의도한 동작이다.

### 5.3 생산 입력의 Nasdaq 참조

```
grep -rn "api.nasdaq.com" scorecard/ output/
  → scorecard/rules/v1.6.json 의 denied 항목 2줄만 (배제 기록 자체)
```

`sources.json` 3 건은 모두 `url: null` 인 내부 기준선이다. **관측·산출 HTML 어디에도 Nasdaq 참조가 없다.** 이미 확보한 표본은 `../spacex-eps-source-03/REPORT.md` 와 `../nasdaq-eps-expansion-04/REPORT.md` 안에 참고 증거로만 남아 있다.

## 6. 하지 않은 것

- **v1.5 수정 없음.** 승인 보존을 위해서다.
- **v1.6 을 활성화하지 않음.** `status: draft` 이고 어떤 실행도 쓰지 않는다.
- **기존 Nasdaq 표본 삭제 없음.** 요청대로 참고용 증거로 보존했다. 생산 입력에는 없다.
- **Yahoo host 등재 없음.** 약관 검토가 선행 조건이다(3.3).
- **F6 채점 규칙 변경 없음.** `../f6-implement-06/REPORT.md` 6 절에서 제안한 v1.6 채점 개정(`accepted_ntm_methods` 정리, C-13 선택지 정리)은 **이번 범위가 아니다.** 이 요청은 원천 정책에 한정됐고, 채점 규칙 개정은 별도 결정이 필요하다. v1.6 초안에 원천 정책만 들어 있는 이유다.

## 7. 남은 작업

1. **v1.6 채점 규칙 개정 여부 결정.** `f6-implement-06` 6 절의 네 항목. 지금 v1.6 은 원천 정책만 담은 초안이다.
2. **Yahoo 약관 검토 후 등재 여부 결정.**
3. **Nasdaq Data Link 다섯 조건 문의.** 서면 확정 시 `conditional_candidates` 에서 `allowed` 로 옮기고 계약 근거를 남긴다.
4. **v1.6 활성화 시점 결정.** `status` 를 `active` 로 올리고 새 실행이 쓰게 하는 시점.

## 8. 재현 방법

```bash
cd worker
npm test                                                   # 91 건
python scripts/validate_report_contract.py ai-scorecard-2026-09-baseline

# 판정 직접 확인
python -X utf8 -c "
import sys; sys.path.insert(0,'scripts')
from scorecard.rules import load_rules
r = load_rules('v1.6')
for u in ['https://api.nasdaq.com/api/analyst/AAPL/earnings-forecast',
          'https://data.nasdaq.com/api/v3/datasets/ZACKS/EE',
          'https://data.sec.gov/submissions/CIK0000320193.json',
          'https://example.com/x']:
    print(u, '->', r.source_violation(u))
print('v1.5 정책:', load_rules('v1.5').source_policy)"

# 생산 입력에 Nasdaq 참조가 없는지
grep -rn "api.nasdaq.com" scorecard/runs output/
```
