# POLICY-12 — v1.6 원천 정책 개정 (사용 범위 personal/internal only 반영)

작성일 2026-09-10. 담당 worker(HANSOLJJ/worker). 요청 `msg_bf7185886336`.

**개정 대상은 `scorecard/rules/v1.6.json` 하나다.** `status: "draft"` 이므로 개정 가능하고, 승인 해시 대상인 `v1.5.json` 은 건드리지 않았다.

C-13 담당인 공문 초안 폐기와 Yahoo 판정 기록은 다루지 않았다. `api.nasdaq.com` 은 호출하지 않았다.

## 1. 전제

사용자가 이 저장소 산출물의 사용 범위를 확정했다. **외부 일반 대중 배포를 전제하지 않는다.**

이 전제는 지금까지 정책 판단의 근거 중 **하나만** 무효화한다. 배포를 전제로 만든 조건이 그것이다. 나머지는 배포와 무관한 근거 위에 서 있어 그대로 남는다. 아래가 그 구분이다.

> **범위 정정 (2026-09-10).** 이 문서는 처음에 범위를 `personal_internal_only` 로 적었다. **사실과 달랐다.** 산출물이 사용자가 대표로 있는 회사의 업무에 쓰이고, 사용자가 그 회사의 CEO 다. 개인 투자 참고 열람이 병행되지만 **약관상 분류는 신고가 아니라 실제 사용을 따르므로 법인 내부 사용이 구속 기준이다.** 현재 값은 `corporate_internal_only` 이고 결과는 2.1 에 적었다. 외부 배포를 전제하지 않는다는 점은 두 값에서 같아 2.2~2.6 의 판단은 바뀌지 않는다.

## 1.1 수집 개시의 선을 어디에 긋는가

`AV-SOURCE-11` 에서 "약관 확인이 수집보다 먼저" 라는 순서를 지킬 때 실제로 갈린 질문이다. 공급사가 문서에 게시한 예시 URL 을 눌러 응답 스키마를 보는 것은 수집인가.

**아니다. 수집 개시는 유니버스 종목을 대상으로 한 반복 호출의 개시다.**

- 문서 예시 URL 로 응답 스키마·필드 목록을 확인하는 것은 **약관 검토의 일부**다. 무엇을 수집하게 되는지 모르면 파생 데이터·보존 조항을 판단할 수 없다.
- **우리 12 개사를 돌기 시작하는 순간이 수집이다.** 거기서부터는 약관 판정이 먼저 끝나 있어야 한다.

### 보호 조건 셋 — 연언으로 강제한다

위반하면 실제로 해를 끼치는 것들이다. **하나라도 빠지면 스키마 확인도 하지 않는다.**

1. robots.txt 와 약관 확인이 **선행**됐다.
2. robots.txt 가 이 호출을 막지 않는다.
3. **유니버스 종목 수집이 아니다.** 우리를 지키는 것은 결국 이 조건이다.

### 증거 조건 — 공개된 문서화 표면임을 보인다

앞의 셋과 성격이 다르다. **이 조건 자체가 보호하는 것은 없고**, 호출 대상이 공개된 문서화 표면이라는 것을 입증할 뿐이다. 그래서 한 가지 형식으로 못박지 않는다. 아래 중 **하나면 증거가 된다.**

- 문서에 게시된 예시 URL (`AV-SOURCE-11` 이 쓴 형식)
- 공식 SDK·클라이언트 라이브러리의 샘플 코드
- OpenAPI·Swagger 명세
- 파라미터까지 문서화된 endpoint

**초판은 이 조건을 "문서 게시 예시 URL" 하나로 적어 보호 조건과 동등한 연언에 묶었다.** 그러면 예시를 안 싣는 공급사에서 보호 조건 셋이 다 성립해도 스키마 확인이 막힌다 — **보호와 무관한 이유로 막히는 것이다.** 위 넷 중 무엇도 없으면 **유니버스 밖 종목 하나로 1 회 호출**을 허용하고 목적을 기록에 남긴다.

### 단서 — 문서 부재는 우회 대상이 아니라 배제 신호다

**예시가 없는 것과 문서가 없는 것은 다르다.** 파라미터 명세도 SDK 도 어떤 문서도 없는 endpoint 라면, 그것은 예시만 없는 공개 상품이 아니라 **애초에 공개 상품이 아니라는 신호**다.

`api.nasdaq.com` 이 정확히 그랬다. 웹사이트 UI 를 그리는 내부 백엔드였고 문서가 없었다. **문서가 없으면 위의 "1 회 호출" 로 내려가는 것이 아니라 배제 쪽을 본다.** 이 단서를 빼면 일반화한 증거 조건이 나중에 "문서가 없으니 1 회 호출로 확인하자" 는 근거로 뒤집혀 쓰인다.

## 2. 개정 여섯

### 2.1 사용 범위 선언 추가 — `sources.usage_scope`

```json
"usage_scope": {
  "scope": "corporate_internal_only",
  "decided_at": "2026-09-10",
  "statement": "…사용자가 대표로 있는 회사의 업무에 쓰인다. 개인 투자 참고 열람이 병행되더라도 약관상 분류는 신고가 아니라 실제 사용을 따르므로 법인 내부 사용이 구속 기준이다. 외부 일반 대중 배포는 여전히 전제하지 않는다.",
  "condition": "산출물을 외부에 배포하면 이 전제가 깨진다. 그때는 원천별로 재배포 라이선스를 다시 확보해야 하고 allowed·denied·conditional_candidates 를 전부 재검토해야 한다. …",
  "note": "2026-09-10 에 personal_internal_only 에서 바뀌었다. … Alpha Vantage 무료 티어 적격이 사라진다 — ToS 2.a.ii 가 법인 또는 법인 대리 사용을 commercial use 로 분류하므로 … 다만 향후 분기 전망이 2개뿐이라 이미 F6 부적격이므로 실질 손실은 없다. …"
}
```

**선언과 조건을 짝으로 묶은 것이 핵심이다.** 범위만 적고 조건을 안 적으면 나중에 배포로 전환할 때 무엇을 되짚어야 하는지가 남지 않는다. 스키마도 `condition` 을 필수로 강제한다(4 절).

`note` 를 둔 이유는 이 선언이 만능 면허로 읽히는 것을 막기 위해서다.

#### 법인 값으로 바꾼 결과 — Alpha Vantage 무료 티어가 닫힌다

범위 값이 바뀌면 **그 결과를 선언 옆에 적어야 한다.** 안 적으면 다음 세션이 같은 원천을 다시 검토하며 개인 사용 조항을 근거로 삼는다.

- Alpha Vantage ToS §2.a 의 무료 라이선스는 **"for personal, non-commercial use"** 다. 같은 조항 **ii** 가 "as or on behalf of a corporation, firm, partnership, trust or any other association and not as an individual" 을 **commercial use 로 분류**한다.
- 법인 내부 사용은 ii 에 해당한다. **따라서 무료 티어 적격이 사라진다.** 쓰려면 `premium@alphavantage.co` 상업 계약 경로다.
- **실질 손실은 없다.** Alpha Vantage 는 향후 분기 전망이 2 개뿐이라 이미 F6 부적격이었다(`../av-source-11/REPORT.md` 4.3).

일반화하면 이렇다. **"개인 사용 허용" 조항은 이제 우리에게 적용되지 않는다.** 원천을 새로 검토할 때 그 점부터 확인한다. `note` 에 같은 문장을 넣었다.

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

> 사용 범위는 usage_scope 대로 외부 일반 대중 배포를 전제하지 않으므로 '외부 배포 허용'은 승격 조건에서 제외했다(2026-09-10). 외부 배포로 범위가 바뀌면 그 조건을 되살려야 한다.

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

### 2.5 `unlisted` 는 "검토 후 미등재" 만 담는다

목록에 없다는 사실이 두 뜻으로 갈리면 안 된다. `policy_note` 에 정의를 못박았다.

> unlisted 는 **검토를 마치고 안 넣기로 한 host** 만 담는다. 아직 검토하지 않은 host 는 담지 않는다. 그래서 '목록에 없다' 는 '미검토' 를 뜻하며 '검토 후 미등재' 와 다르다. unlisted 는 문서 항목이고 source_violation() 은 읽지 않는다 — 등재되지 않은 host 는 그대로 allowlist 미등재로 걸린다.

이 정의가 6 절의 Alpha Vantage 처리와 직결된다. AV 는 검토를 마쳤지만 **판정이 사용자 결정에 걸려 있어** 아직 "안 넣기로 함" 이 아니다. 그래서 `unlisted` 에 넣지 않았다.

### 2.6 robots.txt 와 라이선스 접근을 구분한다

`DATALINK-14` 검토에서 나온 정책 일관성 문제다. `data.nasdaq.com` 의 robots.txt 에 `Disallow /api/*.json*` 과 `Disallow /api/v3/databases/*/data` 가 있다. **우리가 `api.nasdaq.com` 을 robots.txt 근거로 denied 했으므로, 같은 규칙을 기계적으로 적용하면 정식 라이선스를 사도 정책이 자기 발목을 잡는다.**

ZACKS 후보의 `note` 에 구분을 명문화했다.

> robots.txt 와 라이선스 접근을 구분한다. … robots.txt 는 **인증 없는 크롤러**를 대상으로 한 지시이고 Order Form 과 API 키로 접근하는 **라이선스 클라이언트는 계약이 규율한다.** denied 의 api.nasdaq.com 과 다른 점이 여기다. 그쪽은 계약 경로 자체가 없어 robots.txt 와 약관이 유일한 규율이고, 이쪽은 정식 계약이 그 자리를 대신한다. 이 구분은 승격 시 서면으로 확정해야 하며 지금 승격 근거가 아니다.

**초판은 이것을 "두 host 를 가르는 것은 계약 경로의 유무다" 라고 적었다. 그 문장은 샌다.** 느슨하게 읽으면 "이 공급사도 유료 데이터 상품을 판다, 그러니 무료 endpoint 를 써도 된다" 가 된다. 방향이 거꾸로다. **Yahoo 도 유료 데이터 상품이 있지만 그것이 `query1.finance.yahoo.com` 스크래핑을 정당화하지 않는다.**

가르는 사실은 **세상에 계약 경로가 존재하는가**가 아니라 **우리가 지금 그 계약 아래에서 접근하고 있는가**다. 계약이 robots.txt 를 대신하는 것은 아래 셋을 **모두** 만족할 때뿐이다.

1. 그 공급사가 **우리에게 발급한 자격증명**으로 접근하고,
2. 그 데이터와 그 접근 방식을 포괄하는 **체결된 계약**이 있으며,
3. 호출하는 **host·경로가 그 계약이 지목한 것**일 것.

**하나라도 없으면 robots.txt 와 약관이 규율한다.** 그리고 계약이 있어도 **같은 host 에 대한 인증 없는 크롤링에는 robots.txt 가 그대로 적용된다** — 예외는 host 전체가 아니라 인증된 라이선스 호출에만 걸린다.

이 셋으로 좁히면 `api.nasdaq.com` 은 어느 것도 만족하지 못한다. 자격증명도, 계약도, 계약이 지목한 host 도 없다. **denied 를 무르는 근거가 아니다.** `data.nasdaq.com` 도 지금은 셋 다 없다 — 그래서 `candidate_not_approved` 이고, 이 구분은 **승격 시 서면으로 확정할 항목**이지 지금 승격 근거가 아니다. `status` 는 그대로이며 테스트로 고정했다.

## 3. `unlisted` 는 판정에 쓰이지 않는다 — 배선을 확인했다

새 항목이 집행 경로를 바꾸면 안 된다. `RuleSet.source_violation()` 은 denied → conditional_candidates → allowed 순으로만 보고 `unlisted` 를 읽지 않는다. 따라서 Yahoo host 는 **여전히 "allowlist 에 없음" 으로 걸린다.**

```python
rules.source_violation("https://query1.finance.yahoo.com/v7/finance/quote?symbols=NVDA")
# → "query1.finance.yahoo.com 는 원천 allowlist 에 없음 — 약관 확인 후 규칙에 등재하고 쓴다"
```

이 동작을 테스트 셋으로 고정했다. `test_yahoo_unlisted_does_not_change_enforcement` 는 실제 Yahoo host 를 보고, `test_unlisted_is_never_read_by_enforcement` 는 **임의의 host 를 `unlisted` 에 넣어도 판정 문구가 그대로**임을 본다. 둘째 것은 Yahoo 한 종목이 아니라 `unlisted` 라는 개념 자체가 집행 경로에 없다는 것을 고정한다 — 넣었다고 허용되지도, 새로운 배제 사유가 붙지도 않는다.

**다만 그 둘은 "결과가 같다" 를 보일 뿐 "키를 읽지 않는다" 를 보이지 않는다.** 나중에 누가 `unlisted` 를 읽어 문구를 덧붙이되 이 케이스의 결과만 유지하도록 고치면 그대로 통과한다. 그래서 `test_unlisted_key_is_never_touched` 를 더했다. `unlisted` 자리에 **접근하면 `AssertionError` 를 던지는 객체**를 넣고(스키마 검증을 통과시킨 뒤 오염시킨다) 미등재·denied·미승인 후보·allowed 네 경로를 모두 호출한다. **키를 안 건드리면 아무 일도 없고, 읽는 순간 터진다.** 음성 대조로 그 객체가 실제로 터지는 것도 확인했다.

`unlisted` 는 **왜 안 넣었는지를 남기는 문서 항목**이지 새로운 허용 등급이 아니다.

## 4. 스키마와 회귀 테스트

`sources` 의 키 검사는 `_expect_keys` 로 엄격하다. 새 키 둘을 **optional 로만** 열었고, 열면서 검사도 함께 넣었다. 값 없이 이름만 있는 선언을 막기 위해서다.

`scripts/scorecard/schema.py` `_validate_source_policy()`.

| 검사 | 이유 |
|---|---|
| `usage_scope` 는 `scope`·`decided_at`·`statement`·`condition` 필수 | 조건 없는 범위 선언은 범위가 바뀔 때 무엇을 다시 볼지 남기지 않는다 |
| 네 값 모두 공백 불가 | 빈 문자열로 형식만 맞추는 것을 막는다 |
| `unlisted[].reason_type` 은 `technical`/`terms`/`both` | 기술적 부적격과 약관 미확인을 뭉뚱그리지 않는다. 2.4 가 정확히 이 구분의 문제였다 |
| `unlisted[].host` 는 allowed/denied 와 겹칠 수 없다 | 같은 host 가 두 판정을 갖는 것을 막는다 |

테스트는 91 → **109 건**이다. 추가 18 건 중 하나는 기존 테스트 수정이다.

| 테스트 | 고정하는 것 |
|---|---|
| `test_usage_scope_is_optional` | v1.5 처럼 선언이 없는 규칙도 통과한다 |
| `test_usage_scope_valid_passes` | 정상 선언 통과 |
| `test_usage_scope_requires_condition` · `_requires_statement` | 빈 값 거부 |
| `test_unlisted_valid_passes` | 정상 항목 통과 |
| `test_unlisted_reason_type_must_be_known` | 임의 사유 문자열 거부 |
| `test_unlisted_requires_reason` | 빈 사유 거부 |
| `test_unlisted_host_cannot_overlap_allowed` | host 중복 거부 |
| `test_usage_scope_is_corporate_internal` | 실제 v1.6 의 범위 값이 법인이고 조건이 있음 |
| `test_usage_scope_note_records_alpha_vantage_consequence` | 범위 변경의 결과(AV 2.a.ii)가 선언 옆에 남아 있음 |
| `test_zacks_no_longer_requires_external_distribution` | 조건 4 개 정확히 일치, status 는 미승인 유지 |
| `test_nasdaq_stays_denied` | denied 유지 |
| `test_yahoo_is_unlisted_for_technical_reason` | 사유 유형이 technical, allowed 에 없음 |
| `test_yahoo_unlisted_does_not_change_enforcement` | 집행 경로 불변(실제 host) |
| `test_unlisted_is_never_read_by_enforcement` | 집행 경로 불변(임의 host — 개념 자체가 경로에 없음) |
| `test_unlisted_key_is_never_touched` | **키를 읽지 않음을 직접 증명** — 접근 시 터지는 값을 넣고 네 경로 모두 통과 |
| `test_policy_note_separates_unreviewed_from_reviewed_unlisted` | '미검토' 와 '검토 후 미등재' 의 구분이 정의로 남아 있음 |
| `test_zacks_note_separates_robots_from_licensed_access` | 3 요건 연언(자격증명·체결된 계약·계약이 지목한 host)과 인증 없는 크롤링 단서가 남아 있고 status 는 미승인 유지 |

**기존 테스트 수정 1 건.** `test_data_nasdaq_is_candidate_not_approved` 가 승격 조건 5 개를 문자열로 고정하고 있었다. 승인된 정책 변경에 맞춰 4 개로 고치고, `"외부 배포 허용"` 이 **더 이상 나오지 않는다**는 단언을 추가했다. 조건을 줄인 것이 조용히 통과하지 않도록 양방향으로 고정했다.

```
Ran 109 tests in 0.027s
OK
```

## 5. 불변 확인

요청하신 넷을 개정 전후로 대조했다.

| 대상 | 방식 | 결과 |
|---|---|---|
| `v1.5.json` | `git diff` | **변경 없음** |
| 승인 해시 6 종 | `approval.json` 과 현재 값 대조 | **6/6 일치** |
| `results.json` | **`results_hash` 필드**(승인 대조 기준) | **`0942c342…`** · `approval.json` 과 일치 |
| HTML 바이트 | `git diff` + sha256 | **변경 없음** · 213,851 B · `e6cc960c1c50f412` |

```
rules          일치  9231b3a05ba5c766
observations   일치  37435ae2989236f5
judgments      일치  685069767e0cf919
run            일치  50b063a5a12e84a6
results        일치  0942c342f010781e
draft          파일 미변경             574841bc7c26f225
```

### 5.1 승인 불변의 기준값은 `results_hash` 다

`results.json` 을 두고 값이 셋 돌아다녔다. **셋 다 같은 내용이고 재는 대상이 다를 뿐이다.**

| 값 | 무엇을 재나 | 승인 대조에 쓰나 |
|---|---|---|
| **`0942c342…`** | `results.json` **안의 `results_hash` 필드** | **그렇다 — 이것이 기준이다** |
| `4eb8c7d7…` | 파일 바이트 sha256 · 작업 트리(CRLF) | 아니다 |
| `6182cdb1…` | 파일 바이트 sha256 · 커밋 blob(LF) | 아니다 |

근거는 `scripts/scorecard/stages.py` `current_hashes()` 다. `results` 항목이 `load_results(slug)["results_hash"]` 를 읽는다. 파일 바이트가 아니다.

**파일 바이트 해시를 승인 기준으로 인용하면 체크아웃마다 어긋난다.** 개행 처리가 값을 바꾸기 때문이다. 앞으로 승인 불변은 `results_hash` 로 인용한다.

같은 함정이 이 팀의 산출물에도 있었다. `../av-source-11/analyze_demo.py` 가 `_raw/` 지문을 파일 바이트로 찍고 있어서, 커밋 트리에서 돌리면 `documentation.html` 이 1,059,116 → 1,079,968 바이트로 갈렸다. 재현자가 "원자료가 바뀌었나" 로 오해할 값이다. **크기·해시를 개행 정규화(CRLF→LF) 기준으로 바꿨다.**

## 6. 하지 않은 것

- **Alpha Vantage 를 정책 파일에 넣지 않았다.** **Yahoo 는 `unlisted` 인데 AV 는 없는 이유는 하나다. Yahoo 는 판정이 끝났고 AV 는 사용자 결정이 열려 있다.** Yahoo 의 기술적 부적격(회계분기 창 특정 0/12 · 전망 2 분기)은 더 확인할 것이 없는 확정 사실이라 "검토 후 미등재" 다. AV 는 무료 키 발급 여부가 사용자 결정으로 남아 있고 키 하나면 미확인 3 건이 풀린다 — 지금 `unlisted` 에 적으면 그 결정을 앞질러 못박는 셈이다. `unlisted` 가 **검토를 마치고 안 넣기로 한 host 만** 담는다는 정의(2.5)와도 어긋난다. 결정이 나온 뒤 별도 과제로 처리한다.
- **C-13 담당 범위.** 공문 초안 폐기, Yahoo 판정 기록 자체는 손대지 않았다.
- **v1.6 활성화.** `status` 는 `draft` 그대로다. 활성화 시점은 별도 결정 사항이다.
- **`../source-allowlist-07/REPORT.md` 3.3 의 Yahoo 서술.** 그 문서는 Yahoo 판정 기록에 해당해 C-13 담당이다. 정정된 사유는 정책 파일과 이 문서에만 적었다.

## 7. 재현 방법

```bash
cd worker
python -m unittest discover -s tests -q       # 109건 통과
python -c "import sys,json,pathlib; sys.path.insert(0,'scripts'); \
  from scorecard.schema import validate_rules; \
  validate_rules(json.loads(pathlib.Path('scorecard/rules/v1.6.json').read_text(encoding='utf-8')))"
```

변경 파일은 셋이다.

| 파일 | 내용 |
|---|---|
| `scorecard/rules/v1.6.json` | `usage_scope` 추가 · ZACKS 조건 4 개 · `unlisted` 추가 · `policy_note` 와 ZACKS `note` 보강 |
| `scripts/scorecard/schema.py` | 두 새 키의 optional 허용과 값 검사 |
| `tests/test_scorecard_calc.py` | 회귀 17 건 추가 · 기존 1 건 수정 |
