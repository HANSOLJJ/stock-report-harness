# POLICY-12 — v1.6 원천 정책 개정 (사용 범위 personal/internal only 반영)

작성일 2026-09-10. 담당 worker(HANSOLJJ/worker). 요청 `msg_bf7185886336`.

**개정 대상은 `scorecard/rules/v1.6.json` 하나다.** `status: "draft"` 이므로 개정 가능하고, 승인 해시 대상인 `v1.5.json` 은 건드리지 않았다.

C-13 담당인 공문 초안 폐기와 Yahoo 판정 기록은 다루지 않았다. `api.nasdaq.com` 은 호출하지 않았다.

## 1. 전제

사용자가 이 저장소 산출물의 사용 범위를 **personal / internal only** 로 확정했다. 외부 일반 대중 배포를 전제하지 않는다.

이 전제는 지금까지 정책 판단의 근거 중 **하나만** 무효화한다. 배포를 전제로 만든 조건이 그것이다. 나머지는 배포와 무관한 근거 위에 서 있어 그대로 남는다. 아래 네 항목이 그 구분이다.

## 2. 개정 넷

### 2.1 사용 범위 선언 추가 — `sources.usage_scope`

```json
"usage_scope": {
  "scope": "personal_internal_only",
  "decided_at": "2026-09-10",
  "statement": "이 저장소의 산출물(점수·판정·HTML 리포트·파생 자료)은 개인 및 내부 용도로만 쓴다. 외부 일반 대중 배포를 전제하지 않는다.",
  "condition": "산출물을 외부에 배포하면 이 전제가 깨진다. 그때는 원천별로 재배포 라이선스를 다시 확보해야 하고 allowed·denied·conditional_candidates 를 전부 재검토해야 한다. 배포 여부가 바뀌면 이 선언을 먼저 고친다.",
  "note": "이 선언은 원천별 이용 조건을 대체하지 않는다. 각 host 의 robots.txt 와 이용약관이 여전히 우선한다. 개인 사용이라는 사실이 robots.txt 의 전면 Disallow 를 무르지 않는다 — denied 의 api.nasdaq.com 을 보라."
}
```

**선언과 조건을 짝으로 묶은 것이 핵심이다.** 범위만 적고 조건을 안 적으면 나중에 배포로 전환할 때 무엇을 되짚어야 하는지가 남지 않는다. 스키마도 `condition` 을 필수로 강제한다(3 절).

`note` 를 둔 이유는 이 선언이 만능 면허로 읽히는 것을 막기 위해서다. 개인 사용은 **약관이 개인 사용을 허가하는 원천**에만 효력이 있다.

### 2.2 ZACKS 승격 조건에서 "외부 배포 허용" 제거

`conditional_candidates` 의 Nasdaq Data Link ZACKS/EE·EEH 항목이다.

| 개정 전 (5) | 개정 후 (4) |
|---|---|
| 정식 계약 | 정식 계약 |
| 자동 수집 허용 | 자동 수집 허용 |
| derived data 허용 | derived data 허용 |
| ~~외부 배포 허용~~ | **제거** |
| 보관 조건 | 보관 조건 |

`status` 는 `candidate_not_approved` 그대로다. **조건이 하나 줄었을 뿐 승격한 것이 아니다.** `note` 에 제거 사유와 복원 조건을 함께 적었다.

> 사용 범위는 usage_scope 대로 personal/internal only 이므로 '외부 배포 허용'은 승격 조건에서 제외했다(2026-09-10). 외부 배포로 범위가 바뀌면 그 조건을 되살려야 한다.

### 2.3 `api.nasdaq.com` — denied 유지. 완화하지 않는다

**그대로 두었다.** 배제 근거가 배포 여부와 무관하기 때문이다.

> `"reason": "생산 원천 영구 배제. robots.txt 가 User-agent * 에 Disallow / 이고 이용약관이 automated or manual process 로 데이터를 캡처하는 것을 금지한다"`

두 근거 모두 개인·상업을 가르지 않는다. `Disallow: /` 는 크롤러 전체에 대한 지시이고, "automated **or manual** process" 는 수집 방식을 금지한 것이지 용도를 조건으로 달지 않았다. **개인 사용이라는 사실이 이 금지를 무르지 않는다.** 회귀 테스트로 고정했다(3 절 `test_nasdaq_stays_denied`).

### 2.4 Yahoo — allowlist 미등재 유지, 사유를 기술적 사유로 정정

**allowlist 에 넣지 않았다.** 다만 미등재 사유가 약관만인 것처럼 남아 있던 것을 바로잡았다.

기존 기록(`../source-allowlist-07/REPORT.md` 3.3)은 "상류 API 가 personal use only 이고 약관 검토가 선행 조건" 이라고만 적었다. **사용 범위가 personal 로 확정된 지금, 그 서술만 남으면 "이제 약관 문제가 풀렸으니 등재해도 되는가" 로 읽힐 수 있다. 그렇지 않다.**

정책 파일에 `unlisted` 항목을 새로 두고 이렇게 적었다.

```json
{
  "host": "query1.finance.yahoo.com",
  "reason_type": "technical",
  "reason": "F6 원천으로 기술적 부적격. 회계분기 창 특정 0/12 이고 향후 전망이 2개 분기뿐이라 미발표 4개 분기를 만들 수 없다.",
  "decided_at": "2026-09-10",
  "evidence": "C-13 2026-09-10 검증 결과",
  "note": "query2.finance.yahoo.com 도 같은 서비스로 같은 판정이다. 약관 미검토(상류 Yahoo API 가 personal use only)는 별개의 미해결 항목이며 미등재의 주된 사유가 아니다. 기술적 사유만으로 이미 F6 원천이 되지 못한다. …"
}
```

**약관이 해소돼도 Yahoo 는 F6 원천이 되지 못한다.** 회계분기를 특정하지 못하면 창을 연결할 수 없고, 전망 2 분기로는 미발표 4 개 분기를 만들 수 없다. 약관은 부차적 항목으로 내렸고 지운 것은 아니다.

Yahoo 판정 자체의 기록은 C-13 담당이라 손대지 않았다. 이 정책 파일에는 **판정 결과와 그 출처만** 적었다.

## 3. `unlisted` 는 판정에 쓰이지 않는다 — 배선을 확인했다

새 항목이 집행 경로를 바꾸면 안 된다. `RuleSet.source_violation()` 은 denied → conditional_candidates → allowed 순으로만 보고 `unlisted` 를 읽지 않는다. 따라서 Yahoo host 는 **여전히 "allowlist 에 없음" 으로 걸린다.**

```python
rules.source_violation("https://query1.finance.yahoo.com/v7/finance/quote?symbols=NVDA")
# → "query1.finance.yahoo.com 는 원천 allowlist 에 없음 — 약관 확인 후 규칙에 등재하고 쓴다"
```

이 동작을 `test_yahoo_unlisted_does_not_change_enforcement` 로 고정했다. `unlisted` 는 **왜 안 넣었는지를 남기는 문서 항목**이지 새로운 허용 등급이 아니다.

## 4. 스키마와 회귀 테스트

`sources` 의 키 검사는 `_expect_keys` 로 엄격하다. 새 키 둘을 **optional 로만** 열었고, 열면서 검사도 함께 넣었다. 값 없이 이름만 있는 선언을 막기 위해서다.

`scripts/scorecard/schema.py` `_validate_source_policy()`.

| 검사 | 이유 |
|---|---|
| `usage_scope` 는 `scope`·`decided_at`·`statement`·`condition` 필수 | 조건 없는 범위 선언은 범위가 바뀔 때 무엇을 다시 볼지 남기지 않는다 |
| 네 값 모두 공백 불가 | 빈 문자열로 형식만 맞추는 것을 막는다 |
| `unlisted[].reason_type` 은 `technical`/`terms`/`both` | 기술적 부적격과 약관 미확인을 뭉뚱그리지 않는다. 2.4 가 정확히 이 구분의 문제였다 |
| `unlisted[].host` 는 allowed/denied 와 겹칠 수 없다 | 같은 host 가 두 판정을 갖는 것을 막는다 |

테스트는 91 → **104 건**이다. 추가 13 건 중 하나는 기존 테스트 수정이다.

| 테스트 | 고정하는 것 |
|---|---|
| `test_usage_scope_is_optional` | v1.5 처럼 선언이 없는 규칙도 통과한다 |
| `test_usage_scope_valid_passes` | 정상 선언 통과 |
| `test_usage_scope_requires_condition` · `_requires_statement` | 빈 값 거부 |
| `test_unlisted_valid_passes` | 정상 항목 통과 |
| `test_unlisted_reason_type_must_be_known` | 임의 사유 문자열 거부 |
| `test_unlisted_requires_reason` | 빈 사유 거부 |
| `test_unlisted_host_cannot_overlap_allowed` | host 중복 거부 |
| `test_usage_scope_is_personal_internal_only` | 실제 v1.6 의 범위 값과 조건 존재 |
| `test_zacks_no_longer_requires_external_distribution` | 조건 4 개 정확히 일치, status 는 미승인 유지 |
| `test_nasdaq_stays_denied` | denied 유지 |
| `test_yahoo_is_unlisted_for_technical_reason` | 사유 유형이 technical, allowed 에 없음 |
| `test_yahoo_unlisted_does_not_change_enforcement` | 집행 경로 불변 |

**기존 테스트 수정 1 건.** `test_data_nasdaq_is_candidate_not_approved` 가 승격 조건 5 개를 문자열로 고정하고 있었다. 승인된 정책 변경에 맞춰 4 개로 고치고, `"외부 배포 허용"` 이 **더 이상 나오지 않는다**는 단언을 추가했다. 조건을 줄인 것이 조용히 통과하지 않도록 양방향으로 고정했다.

```
Ran 104 tests in 0.022s
OK
```

## 5. 불변 확인

요청하신 넷을 개정 전후로 대조했다.

| 대상 | 방식 | 결과 |
|---|---|---|
| `v1.5.json` | `git diff` | **변경 없음** |
| 승인 해시 6 종 | `approval.json` 과 현재 값 대조 | **6/6 일치** |
| `results.json` | 파일 바이트 sha256 | **`4eb8c7d7…`** (요청서가 인용한 값 그대로) |
| HTML 바이트 | `git diff` + sha256 | **변경 없음** · 213,851 B · `e6cc960c1c50f412` |

```
rules          일치  9231b3a05ba5c766
observations   일치  37435ae2989236f5
judgments      일치  685069767e0cf919
run            일치  50b063a5a12e84a6
results        일치  0942c342f010781e
draft          파일 미변경             574841bc7c26f225
```

### 5.1 해시 두 값에 대한 주의 — 둘 다 정상이다

요청서는 `results.json` 해시를 `4eb8c7d7` 로 인용했고 `approval.json` 은 `0942c342…` 를 적고 있다. **다른 값이지만 둘 다 맞다. 서로 다른 것을 재는 값이다.**

- `4eb8c7d7…` — `results.json` **파일 바이트**의 sha256. 작업 트리 기준이다.
- `0942c342…` — `results.json` **안의 `results_hash` 필드**. `current_hashes()` 가 승인 대조에 쓰는 값이다(`scripts/scorecard/stages.py` `results` 항목이 `load_results(slug)["results_hash"]` 를 읽는다).

파일 바이트 해시는 체크아웃의 개행 처리에 따라 달라진다. 실제로 이 저장소에서 커밋된 blob(LF)은 `6182cdb1…`, 작업 트리(CRLF)는 `4eb8c7d7…` 로 같은 내용에 값이 둘이다. **승인 대조에는 파일 바이트를 쓰면 안 된다.** 이번 확인은 두 방식 모두로 했고 둘 다 불변이다.

## 6. 하지 않은 것

- **Alpha Vantage 를 정책 파일에 넣지 않았다.** `AV-SOURCE-11` 의 권고는 "지금 채택하지 않는다" 이지만, 무료 키 발급 여부가 사용자 결정으로 열려 있다. 지금 `unlisted` 에 적으면 그 결정을 앞질러 못박는 셈이다. 결정이 나온 뒤 별도 과제로 처리하는 것이 맞다고 본다.
- **C-13 담당 범위.** 공문 초안 폐기, Yahoo 판정 기록 자체는 손대지 않았다.
- **v1.6 활성화.** `status` 는 `draft` 그대로다. 활성화 시점은 별도 결정 사항이다.
- **`../source-allowlist-07/REPORT.md` 3.3 의 Yahoo 서술.** 그 문서는 Yahoo 판정 기록에 해당해 C-13 담당이다. 정정된 사유는 정책 파일과 이 문서에만 적었다.

## 7. 재현 방법

```bash
cd worker
python -m unittest discover -s tests -q       # 104건 통과
python -c "import sys,json,pathlib; sys.path.insert(0,'scripts'); \
  from scorecard.schema import validate_rules; \
  validate_rules(json.loads(pathlib.Path('scorecard/rules/v1.6.json').read_text(encoding='utf-8')))"
```

변경 파일은 셋이다.

| 파일 | 내용 |
|---|---|
| `scorecard/rules/v1.6.json` | `usage_scope` 추가 · ZACKS 조건 4 개 · `unlisted` 추가 |
| `scripts/scorecard/schema.py` | 두 새 키의 optional 허용과 값 검사 |
| `tests/test_scorecard_calc.py` | 회귀 12 건 추가 · 기존 1 건 수정 |
