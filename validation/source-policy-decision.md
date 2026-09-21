# 원천 정책 — `usage_scope` 는 하나가 아니다

- 결정일. 2026-09-11.
- 결정자. 사용자.
- 선행. `scope-personal-use-decision.md` · `f6-spec-18-review.md` · `f6-source-round2-review.md`

## 사용자 결정

> **personal use 든 corporate_internal_only 든 둘 다 된다.**

## 지금 규칙이 그것을 담지 못한다

```json
"usage_scope": {"scope": "corporate_internal_only", "decided_at": "2026-09-10", ...}
```

`schema.py` 의 `USAGE_SCOPES` 가 **셋 중 하나를 고르는 enum** 이라 **한쪽을 고르면 다른 쪽 조항이 자동으로 배제된다.** 그 `note` 가 결과를 스스로 적어 뒀다.

> 2026-09-10 에 `personal_internal_only` 에서 바뀌었다. … **Alpha Vantage 무료 티어 적격이 사라진다** — ToS 2.a.ii 가 법인 사용을 commercial 로 분류하므로

**같은 이유로 FMP 도 배제 후보가 됐다.** `2.2.1 Personal Use` 가 `In no event … on behalf of a company` 라고 적기 때문이다.

**사용자 결정은 그 배제가 성립하지 않는다는 뜻이다.** 산출물이 개인 열람과 법인 내부 업무 양쪽에 쓰이고, **어느 쪽 조항이든 만족하면 쓸 수 있다.**

## 설계진행이 이것을 오래 붙잡고 있었다

`f6-spec-18-review.md` 에서 FMP·Finnhub 를 **"사용자 결정 필요"** 로 에스컬레이션했고, 오늘 다시 **"정책 파일이 사실과 다르다"** 며 첫 번째 급한 건으로 올렸다.

**사용자는 이미 답했었다.** 세션 초반에 `personal use only야 지금` 이라고 했고, 그 뒤 `scope-personal-use-decision.md` 를 만들었다가 **내가 법인으로 정정했다.** 그 정정이 두 원천을 배제하는 부작용을 낳았고, 나는 그 부작용을 **새 미결 안건으로 다시 올렸다.**

**내가 만든 문제를 사용자에게 결정하라고 되물은 셈이다.**

## Finnhub 는 애초에 문제가 아니었다

`robots.txt` 가 `/terms-of-service` 를 `Disallow` 해서 약관을 못 읽는다고 보고했다. 그런데 **`PRIV-ARR-17` 검토에서 내가 표준을 정해 뒀다.**

> **허용한다. 표준으로 정한다 — `robots.txt` 와 약관·정책 문서는 확인 목적으로 조회할 수 있고, 그 외 내용 페이지는 약관 확인 후에만 조회한다.**

**읽으면 된다.** 워커가 그때 안 읽었고 나도 그 표준을 이 건에 잇지 못했다.

## `data.nasdaq.com` 은 닫는다

`v1.7` 에 `conditional_candidates` 로 남아 있다. **`ZACKS/EE`·`EEH` 가 그 경로였고 구독가 `$1,200` 으로 채택을 접었다.**

`conditional_candidates` 는 "조건만 갖추면 쓸 수 있다" 로 읽히므로 **다음 사람이 D1~D5 를 다시 판다.** `채택 안 함(가격)` 으로 닫는다.

**따라서 `f6-source-round2-review.md` 의 D1~D5 는 전부 소멸한다.**

| | 내용 | 상태 |
|---|---|---|
| D1 | LLM 에이전트 경유가 1.4(e) 에 걸리는지 | **소멸** |
| D2 | 개인 자격인가 법인 내부인가 | **소멸** — 둘 다 된다 |
| D3 | 무료 계정 생성 허용 여부 | **소멸** |
| D4 | Order Form · 자동갱신 · 감사권 감수 | **소멸** |
| D5 | 2026-11-01 약관 개정 | **소멸** |

## 확정

| 건 | 처리 |
|---|---|
| `usage_scope` | **단일값 → 허용 범위.** 개인·법인 내부 둘 다 |
| Alpha Vantage | 배제 사유 철회. 다만 **분기 전망 2개뿐이라 F6 부적격은 그대로** |
| FMP | 배제 사유 철회. `allowed` 유지 |
| Finnhub | **약관을 읽는다.** 우리 표준상 조회 가능 |
| `data.nasdaq.com` | **`채택 안 함(가격)`** 으로 닫음 |
| 외부 배포 | **여전히 전제하지 않는다.** 배포하면 전부 재검토 |

**변하지 않는 것** — `robots.txt` 의 전면 `Disallow` 는 어느 신분으로도 무르지 않는다. `api.nasdaq.com` 영구 배제는 그대로다.
