# SRC-POLICY-32 — 원천 정책 정리

## 0. 결론 — 두 가지를 먼저 보고한다

### 0-1. 충돌이 실재해 편집을 멈추고 제안으로 냈다

지시서가 "충돌 우려가 있으면 제안만 하고 멈춘 뒤 보고" 라고 했고 **그 조건에 해당한다.**

| 확인 | 결과 |
|---|---|
| worker 워크트리 상태 | `scorecard/rules/v1.7.json` 과 `scripts/scorecard/schema.py` **둘 다 미커밋 수정 중** |
| worker 수정이 내 담당 영역에 닿는가 | **닿지 않는다.** v1.7 diff 에 `sources`·`usage_scope` 없음, schema diff 에 `USAGE_SCOPES` 없음 |
| 내 워크트리에 대상 파일이 있는가 | **없다.** 내 브랜치(`HANSOLJJ/NTM-전망치조사`)에는 `scorecard/` 트리 자체가 없다 |

즉 **영역 충돌은 없고 파일 충돌만 있다.** 그러나 대상 파일이 내 브랜치에 존재하지 않으므로 편집하려면 worker 워크트리를 직접 고쳐야 하고, 그쪽이 같은 두 파일을 미커밋 상태로 들고 있는 동안 그렇게 하는 것은 상대 작업을 깨뜨릴 수 있다. **제안까지만 하고 멈췄다.**

제안은 즉시 적용 가능한 형태로 냈다 — `proposal-sources-v1.7.json`(완성된 블록), `proposal-code.md`(schema.py·rules.py 패치 3건).

### 0-2. 과제 2의 전제가 성립하지 않는다 — 배제 사유는 철회되지 않는다

**이것이 이번 과제의 실질 결과다.** 지시서는 "둘 다 개인 사용이 허용되면 성립하지 않는다" 고 했으나, 원문을 읽으면 **철회되지 않는다.**

이유는 한 줄이다. **`scopes` 는 합집합이므로 라이선스는 우리 범위의 *전부* 를 허용해야 한다.** 개인 사용을 *더해도* `corporate_internal_only` 가 범위에서 빠지는 것이 아니다. 세 원천 모두 법인 사용을 명시적으로 금지하므로 그 금지는 그대로 문다.

| 원천 | 조항 | 법인 사용 금지 표현 | 개인 추가로 철회되나 |
|---|---|---|---|
| Alpha Vantage | ToS §2.a + ii | `Usage falls under "commercial use" if **any** of the following criteria apply` — ii 가 법인 명의·대리 | **아니오** |
| FMP | §2.2.1 | `**In no event** may the Customer use this licence on behalf of a company` | **아니오** |
| Finnhub | ToS *Redistribution Rights and Personal Use* | `Personal plan can't be used by any business **even internally** without a written approval` | **아니오** |

세 조항 모두 "어느 하나라도" / "어떤 경우에도" / "내부적으로도" 라는 **포괄 배제** 형식이다. 범위에 법인이 남아 있는 한 해당한다.

실측으로 방향을 확인했다(`proto_scope.py` §3).

| 선언 범위 | AV | FMP | Finnhub | SEC·연준 |
|---|---|---|---|---|
| 이전: 법인만 | 부적격 | 부적격 | 부적격 | 적격 |
| **확정: 개인+법인** | **부적격** | **부적격** | **부적격** | 적격 |
| 가정: 개인만 | 적격 | 적격 | 적격 | 적격 |

**범위를 넓히는 것은 제약을 푸는 것이 아니라 조이는 것이다.** 이전(법인만)과 확정(개인+법인)의 결과가 같고, 풀리는 경우는 개인 *전용* 일 때뿐이다.

따라서 **철회 대신 사유를 정확히 다시 적는 쪽**으로 제안했다. 사용자가 실제로 원하는 것이 이 원천들을 쓰는 것이라면 선택지는 셋이다 — (a) 개인 전용으로 범위를 좁히거나, (b) 유료·서면 승인 경로를 밟거나, (c) 안 쓴다. **이 결정은 제 몫이 아니라 사용자 몫이라 판단해 제안에서 열어 두었다.**

## 1. 원천별 현재 상태·근거·확인 일자 (완료 조건 1)

| host | 상태 | 근거 | 확인 일자 | 이번 변경 |
|---|---|---|---|---|
| `data.sec.gov` | **allowed** | User-Agent 표기·요청 한도 준수 조건으로 프로그램 접근 허용 | 2026-09-09 | 없음 |
| `www.sec.gov` | **allowed** | 같은 조건 | 2026-09-09 | 없음 |
| `www.federalreserve.gov` | **allowed** | H.10 Foreign Exchange Rates. TWD·CNY 수록 확인 | 2026-09-10 | 없음 |
| `finnhub.io` | **allowed (약관 확인 완료 · 무료 등급 부적격)** | ToS 가 법인 내부 사용을 `even internally` 로 명시 배제 | **2026-09-11 (이번 최초 확인)** | note 갱신 |
| `financialmodelingprep.com` | **allowed (무료 등급 부적격)** | §2.2.1 `In no event ... on behalf of a company` | 2026-09-11 재확인 | note 갱신 — **철회 안 됨** 명시 |
| `alphavantage.co` | **미등재** | §2.a.ii 로 commercial · **그와 별개로 향후 분기 전망 2개뿐이라 F6 부적격** | 2026-09-10 | 기술 사유 유지, 약관 사유 재서술 |
| `data.nasdaq.com` | **not_adopted (신설)** | 구독가 연 $1,200 로 사용자가 채택 접음 | **2026-09-11** | `conditional_candidates` 에서 이동 |
| `api.nasdaq.com` | **denied (영구)** | robots.txt `User-agent: *` / `Disallow: /` + 약관이 자동·수동 캡처 금지 | 2026-09-09 | 없음 |
| `query1/2.finance.yahoo.com` | **unlisted (검토 후 미등재)** | 기술적 부적격 — 회계분기 창 특정 0/12, 전망 2분기 | 2026-09-10 | 없음 |

**Alpha Vantage 의 F6 부적격 사유는 그대로 남겼다.** 지시서 지시대로다 — 배제 사유가 바뀐 것이지 적격이 된 것이 아니다. 다만 §0-2 대로 **약관 사유도 아직 살아 있다.**

## 2. 과제 1 — `usage_scope` 를 허용 범위로

`scope`(단일 문자열) → `scopes`(배열) + `evaluation_rule` 신설. 전체 블록은 `proposal-sources-v1.7.json`, 코드 패치는 `proposal-code.md` P1.

핵심은 **`evaluation_rule` 을 함께 넣는 것**이다.

> `scopes` 는 합집합이다. 어떤 원천이 적격이려면 그 라이선스가 `scopes` 의 **모든** 원소를 허용해야 한다. 하나라도 금지하면 부적격이다. 따라서 범위를 넓히는 것은 제약을 푸는 것이 아니라 조이는 것이다.

이 문장이 없으면 다음 사람이 §0-2 와 정확히 같은 오해를 반복한다 — "개인도 되니까 개인 사용 조항을 쓸 수 있다". **집합을 도입하면서 집합의 해석 규칙을 같이 적지 않으면 그 집합은 읽는 사람마다 다르게 읽힌다.**

### 하위호환 — 테스트로 확인 (완료 조건 3)

`proto_scope.py` §1·§2 실측.

| 파일 | 형태 | 결과 |
|---|---|---|
| `v1.5.json` | `sources` 블록 **없음** | 이 경로를 타지 않음 — 정책 미적용 버전, 그대로 통과 |
| `v1.6.json` | `scope` 단일 | `scope(legacy)` → `{corporate_internal_only}` 로 승격 |
| `v1.7.json` | `scope` 단일 | 같음 |
| 신규형 | `scopes` 배열 | `{personal_internal_only, corporate_internal_only}` |

거부 경로도 확인했다 — 빈 배열·알 수 없는 값·중복·둘 다 없음 **4건 모두 거부**.

**v1.5 는 불변이다.** 손대지 않았고 손댈 필요도 없다 — `sources` 블록이 아예 없어 `source_policy` 가 `None` 이고 `check_source_allowlist` 가 곧바로 `return False` 한다.

## 3. 과제 2 — Alpha Vantage·FMP

§0-2 대로 **철회하지 않았다.** 대신 note 를 다시 썼다.

- **FMP** — "usage_scope 에 `personal_internal_only` 를 더해도 이 사유는 철회되지 않는다. `scopes` 가 합집합이라 `corporate_internal_only` 가 남아 있는 한 `In no event` 조항이 그대로 적용된다" 를 명시.
- **Alpha Vantage** — 미등재 상태 유지. **기술 사유(향후 분기 2개·basis 4필드 부재)가 주된 사유**이고 약관 사유는 그와 독립적으로 살아 있다. 두 사유를 분리해 적었다 — 하나가 해소돼도 다른 하나가 남는다는 것이 기록에 남아야 한다.

**지시서와 다른 결론을 낸 것이므로 적용 전에 판단을 받아야 한다.** 제안 파일에만 반영했고 규칙 파일은 건드리지 않았다.

## 4. 과제 3 — Finnhub 약관 (이번 과제 최대 발견)

PRIV-ARR-17 표준("robots.txt 와 약관·정책 문서는 확인 목적으로 조회할 수 있다")을 적용해 **2026-09-11 에 조회하고 원문을 보존했다**(`raw/finnhub-terms-of-service.html`, `raw/finnhub-terms-rendered.txt`, `raw/finnhub-robots.txt`, `raw/finnhub-privacy-policy.html`, 메타는 `fetch-meta.json`).

`robots.txt` 전문은 넉 줄이다.

```
User-agent: *
Disallow: /terms-of-service
Disallow: /faq
Allow: /
```

### 결정적 조항 — *Redistribution Rights and Personal Use*

> You hereby agree to **not redistribute or share access to data or derived results from the data** obtained from Finnhub with anyone or any 3rd party without written approval from Finnhub. All plan listed on Finnhub website is **strictly for personal use** unless explicitly stated otherwise. **Personal plan can't be used by any business even internally without a written approval.**

> You are also **not qualified for any personal use plans** if you fall into ONE of the following categories:
> - You are securities professional (registered with FINRA, SEC, CFTC or relevant regulatory bodies)
> - **You are using this data for your business or registering under your business name regardless of the industry**
> - **You are going to deduct this expense as a business expense**

**우리 사용 형태에 걸리는 조항이 셋이다.**

1. **`even internally`** — 법인 내부 사용이라는 우리 범위의 절반을 **명시적으로** 배제한다. FMP·AV 보다 강한 표현이다. 저 둘은 "on behalf of a company" / "commercial use" 로 분류하는 방식인데, Finnhub 은 *내부적으로도 안 된다* 고 직접 적는다.
2. **`derived results from the data`** — 재배포 제한이 원자료뿐 아니라 **파생 결과**까지 미친다. 우리 산출물(점수·판정·HTML 리포트)이 정확히 파생 결과다.
3. **부적격 사유 목록 2번** — `regardless of the industry` 라 업종 예외가 없다.

### 그래서 상태가 바뀐다

Finnhub 은 **allowed 에 있으면서 약관을 한 번도 확인한 적이 없었다.** v1.6 에서 등재됐고 v1.7 note 가 "약관 확인 없이 등재된 상태라는 사실을 기록한다" 고 적은 채로 이어졌다. 이번에 확인했고 **무료·개인 플랜 전제가 우리 사용에 대해 깨져 있음이 확인됐다.**

강등 여부는 사용자 결정 사항이라 note 갱신까지만 제안했다(FMP 와 같은 처리). 실질 영향은 없다 — **현재 F6·F9 는 SEC 만 쓴다**(§6 에서 실측 확인).

**약관 확인 없이 allowlist 에 있는 host 가 남아 있는지** 전수 확인했다. `data.sec.gov`·`www.sec.gov`·`www.federalreserve.gov` 는 공공기관 공개 자료이고, `finnhub.io`·`financialmodelingprep.com` 이 상업 공급사 둘이었으며 **이번으로 둘 다 확인이 끝났다.**

## 5. 과제 4 — `data.nasdaq.com` 닫기

`conditional_candidates` → **`not_adopted`** 신설로 옮기는 것을 제안한다.

### 왜 `denied` 가 아닌가

지시서 지적에 동의한다. 둘은 **사유의 종류가 다르다.**

| | `denied` (api.nasdaq.com) | `not_adopted` (data.nasdaq.com) |
|---|---|---|
| 성격 | **쓸 자격이 없다** | **자격은 있으나 안 쓰기로 했다** |
| 근거 | robots.txt 전면 Disallow + 약관 위반 | 구독가 연 $1,200 — 비용 대비 효용 판단 |
| 누가 정했나 | 약관이 정한다 | **사용자가 정한다** |
| 되돌릴 수 있나 | 공급사가 약관을 바꿔야 | **예산 승인이나 가격 변동이면** |

같은 통에 넣으면 나중에 "왜 배제됐나" 를 물을 때 사유가 섞인다. 그리고 **`denied` 에 넣으면 "약관 위반 원천" 이라는 사실과 다른 낙인이 남는다.**

### 필수 필드로 재조사를 막는다

제안 항목은 `status`·`decided_at`·`decided_by`·`reason_type`·`reason`·**`reopen_condition`**·`prior_investigation` 을 갖는다.

> `reopen_condition`: 가격이 바뀌거나 사용자가 예산을 승인하면 그때 다시 연다. **그 전에는 D1~D5 를 다시 조사하지 않는다 — 조건이 미충족인 것이 아니라 결정이 끝났다.**

`conditional_candidates` 라는 이름이 "조건만 갖추면 쓸 수 있다" 로 읽혀 같은 조사가 반복된 것이 문제였으므로, **결정이 끝났다는 것과 어떤 조건에서 다시 여는지를 둘 다 적게** 강제한다.

### ★ 이름만 바꾸면 오히려 나빠진다 — 코드가 함께 바뀌어야 한다

`source_violation()` 이 `conditional_candidates` 를 **직접 읽는다.**

```python
        for entry in policy.get("conditional_candidates", []):
            ...
                need = ", ".join(entry["required_written_conditions"])
                return f"{host} 는 미승인 후보 — 서면 확정 필요: {need}"
```

키 이름만 `not_adopted` 로 바꾸면 이 블록이 안 걸리고 `data.nasdaq.com` 은 **마지막 fallback 으로 떨어진다.**

```python
        return f"{host} 는 원천 allowlist 에 없음 — 약관 확인 후 규칙에 등재하고 쓴다"
```

**이 메시지가 정확히 우리가 막으려는 행동을 지시한다.** 다음 사람이 "약관 확인하고 등재하면 되는구나" 로 읽고 D1~D5 를 다시 판다. 규칙 파일만 고치면 문제가 되레 악화되므로 `rules.py` 패치(`proposal-code.md` P2)가 **함께 가야 한다.** 과거 키를 읽는 블록은 v1.6 호환을 위해 남긴다.

이 지점이 제 편집 범위(sources 블록 + `USAGE_SCOPES`)를 **넘는다.** `rules.py` 는 지시서가 허락한 범위 밖이라 제안으로만 냈다.

## 6. 점수가 바뀌는가 (완료 조건 2) — 실측

예상에 기대지 않고 확인했다. **바뀌지 않는다.** 근거는 둘이다.

### 6-1. `usage_scope` 를 읽는 코드가 없다

```
scripts/scorecard/schema.py:260   optional=[..., "usage_scope", ...]
scripts/scorecard/schema.py:281   if "usage_scope" in policy:
scripts/scorecard/schema.py:282-291   (형태 검증만)
```

**전수 grep 결과 `schema.py` 밖에서 `usage_scope` 를 읽는 코드가 하나도 없다.** 형태 검증 외에 판정에 개입하지 않으므로 값이나 구조를 바꿔도 점수가 움직일 수 없다.

이것은 [[declaration-needs-a-consumer]] 의 "소비자 없는 선언" 에 해당한다. 다만 **여기서는 결함이 아니다** — 이 값의 소비자는 코드가 아니라 **원천을 검토하는 사람**이고, 그 용도가 `statement`·`condition`·(신설)`evaluation_rule` 에 적혀 있다. 사람이 소비자라는 사실 자체를 적어 두는 것이 맞다고 보아 `evaluation_rule` 을 넣었다.

### 6-2. 실행이 인용하는 host 에 해당 원천이 없다

| 실행 | sources.json 의 host |
|---|---|
| `ai-scorecard-2026-09-baseline` | url 없는 항목 3건뿐 |
| `ai-scorecard-2026-09-obsreg` | `www.sec.gov` 5, `data.sec.gov` 2, url 없음 3 |

`finnhub.io`·`financialmodelingprep.com`·`data.nasdaq.com` 을 인용하는 항목이 **하나도 없다.** `check_source_allowlist` 는 `sources.json` 의 url 만 검사하므로 `data.nasdaq.com` 을 어느 그룹에 넣든 현재 실행의 검증 결과가 달라지지 않는다.

**설계진행 예상("F6 도 F9 도 SEC 만 쓴다")이 맞다.** 다만 근거를 F6·F9 산식이 아니라 실행이 실제로 인용한 host 로 확인했다.

## 7. 조회 기록 (완료 조건 4)

| 파일 | URL | status | bytes | 조회 일자 |
|---|---|---|---|---|
| `raw/finnhub-robots.txt` | `https://finnhub.io/robots.txt` | 200 | 65 | 2026-09-11 |
| `raw/finnhub-terms-of-service.html` | `https://finnhub.io/terms-of-service` | 200 | 16,106 | 2026-09-11 |
| `raw/finnhub-privacy-policy.html` | `https://finnhub.io/privacy-policy` | 200 | 6,593 | 2026-09-11 |
| `raw/finnhub-terms-rendered.txt` | (위 HTML 에서 태그 제거) | — | 5,816자 | 2026-09-11 |

메타는 `fetch-meta.json`. **`api.nasdaq.com` 은 호출하지 않았다.** 조회한 host 는 `finnhub.io` 하나뿐이고 모두 약관·정책·robots 경로다.

## 8. 조건 준수

| 조건 | 결과 |
|---|---|
| 편집 범위 = sources 블록 + `USAGE_SCOPES` | 지켰다. **`policies.f6`·`policies.f9` 는 열지 않았다** |
| worker 충돌 회피 | **편집 0건.** 제안 파일로만 냄 |
| v1.5 불변 | 손대지 않음. `sources` 블록이 없어 영향도 없음 |
| 점수·승인·실행 원자료 변경 금지 | 변경 없음 |
| `api.nasdaq.com` 호출 금지 | 호출 안 함 |
| 다른 워크트리 | `worker/` 는 읽기만 |

## 9. 남는 판단 셋 — 사용자·설계진행 몫

1. **§0-2 의 결론을 받아들일 것인가.** 배제 사유가 철회되지 않는다는 것이 제 판정이고 지시서와 다르다. 받아들인다면 과제 2는 "철회" 가 아니라 "사유 재서술" 이 된다.
2. **범위를 개인 전용으로 좁힐 것인가.** 좁히면 세 원천이 모두 적격이 된다(§0-2 표 마지막 줄). 다만 산출물이 실제로 법인 업무에 쓰인다면 신고와 실제가 어긋나고, 그 문제는 `usage_scope` note 가 이미 "약관상 분류는 신고가 아니라 실제 사용을 따른다" 로 적어 두었다.
3. **`rules.py` 패치를 누가 넣을 것인가.** §5 대로 규칙 파일만 고치면 상태가 나빠진다. 제 범위 밖이라 worker 또는 별도 과제로 배정돼야 한다.

## 10. 산출물

| 파일 | 내용 |
|---|---|
| `fetch_finnhub.py` | Finnhub robots·약관·정책 조회와 보존 |
| `proto_scope.py` | `scopes` 정규화 프로토타입 · **하위호환 테스트** · 적격 방향 실측 |
| `make_proposal.py` | 제안 sources 블록 생성 |
| `proposal-sources-v1.7.json` | **제안 블록 전문 (적용 안 함)** |
| `proposal-code.md` | **schema.py·rules.py 패치 3건 (적용 안 함)** |
| `fetch-meta.json` | 조회 메타 + 일자 |
| `raw/finnhub-*` | 약관·정책·robots 원문 보존 |

## 11. 검토 확정 반영 (2026-09-11, 판정 pass)

설계진행 커밋 `e291e21`. **§0-2 의 판정이 채택됐고 지시서 전제가 정정됐다.** 결론 문장은 "범위를 넓히는 것은 제약을 푸는 것이 아니라 조이는 것이다" 다.

### 11-1. 확정된 처리 — 세 원천을 `allowed` 에서 내린다

| host | 이동 | 사유 종류 |
|---|---|---|
| `www.alphavantage.co` | (미등재 유지) → `unlisted` 명시 | 기술 + 약관 |
| `financialmodelingprep.com` | `allowed` → `unlisted` | 기술 + 약관 |
| `finnhub.io` | `allowed` → `unlisted` | 기술 + 약관 |

셋 다 **실제로 아무 데도 쓰이지 않는다.** 현재 F6·F9 가 먹는 것은 SEC·연준 H.10·프로젝트 내 v1.5 원본뿐이다(§6-2 실측과 일치).

**사용자에게 "개인 전용으로 선언할까요" 를 되묻지 않는다.** 쓰지도 않는 원천 때문에 `usage_scope` 를 좁히는 것은 꼬리가 몸통을 흔드는 것이다. `usage_scope` 를 개인+법인 합집합으로 넓히는 것은 사용자 확정대로 간다 — 세 원천을 안 쓰는 이상 그것 때문에 잃는 것이 없다.

§9 에 열어 둔 판단 셋 중 1·2 가 이렇게 닫혔다. 3(`rules.py` 를 누가 넣나)은 worker 로 간다.

### 11-2. ★ 초판 제안 파일이 확정과 어긋난다 — v2 를 만들었다

**자체 발견이다.** `proposal-sources-v1.7.json` 은 이 결정 **이전에** 만들어져 `finnhub.io`·`financialmodelingprep.com` 을 `allowed` 에 남긴 채 note 만 갱신한 형태다. 그대로 적용하면 확정과 정반대가 된다.

| | 초판 `allowed` | v2 `allowed` |
|---|---|---|
| | sec×2, **finnhub**, **fmp**, 연준 | sec×2, 연준 |

`proposal-sources-v1.7-v2.json` 을 만들고 초판 최상단에 `_SUPERSEDED` 표식을 달았다. **적용은 v2 를 쓴다.**

제안을 넘기는 시점과 결정이 내려진 시점이 어긋나면 이런 일이 생긴다. 제안 파일은 만들어진 순간의 전제를 그대로 굳혀 들고 있으므로, **전제가 바뀌면 제안도 같이 갱신하거나 최소한 낡았다는 표식을 달아야 한다.** 표식 없이 넘기면 받는 쪽이 확정된 내용인 줄 알고 적용한다.

### 11-3. 되살릴 조건을 `relist_condition` 에 적었다

설계진행 요구대로 "되살리려면 무엇이 필요한지" 를 각 항목에 적었다. **Finnhub 만 조건이 셋**이다.

| host | 조건 |
|---|---|
| Alpha Vantage | (1) 향후 분기 4개 + basis 4필드 (2) 범위를 개인 전용으로 좁히거나 상업 계약 |
| FMP | (1) `period=quarter` 접근권 (2) 범위를 개인 전용으로 좁히거나 법인 라이선스 |
| **Finnhub** | (1) basis 확인 (2) 범위를 좁히거나 written approval (3) **파생 결과 공유에 대한 별도 written approval** |

**(3)은 다른 둘에 없다.** 다른 두 원천은 *사용 주체*만 제한하는데 Finnhub 은 **산출물의 유통까지** 제한한다(`derived results from the data`). 그래서 `usage_scope` 를 개인 전용으로 좁히는 것만으로는 Finnhub 이 해소되지 않는다. 이 비대칭을 조건란에 명시했다.

`unlisted` 에 `relist_condition` 을 optional 로 추가하는 스키마 패치가 `proposal-code.md` **P4** 다. 필수가 아닌 이유는 되살릴 길이 없는 영구 부적격도 있기 때문이고, `not_adopted` 의 `reopen_condition` 과 이름을 다르게 둔 것은 **등재된 적 없음(relist)과 후보였다 닫힘(reopen)의 차이**를 이름이 지키게 하려는 것이다.

### 11-4. 적용 순서

worker 가 적용할 때 순서가 있다.

1. `schema.py` — P1(`scopes`) · P3(`not_adopted`) · **P4(`relist_condition`)**
2. `rules.py` — P2(`source_violation` 의 `not_adopted` 분기)
3. `v1.7.json` — `proposal-sources-v1.7-v2.json` 의 `sources` 블록

**스키마를 먼저 고치지 않으면 규칙 파일이 알 수 없는 키로 거부된다.** 그리고 2를 빼면 §5 대로 닫으려던 것이 다시 열리는 안내가 나온다.
