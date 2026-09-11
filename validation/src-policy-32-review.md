# SRC-POLICY-32 재검토 — 원천 정책

- 검토일. 2026-09-11.
- 대상. NTM `04d9091`.
- 판정. **`pass`.** **내 지시서 전제가 틀렸고 NTM 이 원문으로 뒤집었다.**

## 0. 결론부터 — 세 원천을 `allowed` 에서 내린다

**사용자 결정을 다시 묻지 않는다.** 다시 물을 일도 아니다.

---

## 내 전제가 틀렸다

지시서에 이렇게 적었다.

> Alpha Vantage 와 FMP 의 배제 사유를 철회하십시오. **둘 다 개인 사용이 허용되면 성립하지 않습니다.**

**성립한다.** NTM 이 한 줄로 뒤집었다.

> **`scopes` 는 합집합이므로 라이선스는 우리 범위의 *전부* 를 허용해야 한다.** 개인 사용을 *더해도* `corporate_internal_only` 가 범위에서 빠지는 것이 아니다.

세 조항이 전부 **포괄 배제** 형식이다. 원문을 확인했다.

| 원천 | 조항 | 형식 |
|---|---|---|
| Alpha Vantage | `commercial use if **any** of the following criteria apply` | 어느 하나라도 |
| FMP | `**In no event** may the Customer use this licence on behalf of a company` | 어떤 경우에도 |
| Finnhub | `Personal plan can't be used by any business **even internally**` | 내부적으로도 |

**범위에 법인이 남아 있는 한 셋 다 걸린다.** NTM 이 실측으로 방향까지 확인했다.

```
이전: 법인만       →  AV 부적격 · FMP 부적격 · Finnhub 부적격
확정: 개인+법인    →  똑같이 셋 다 부적격        ← 결과가 바뀌지 않는다
가정: 개인 전용    →  셋 다 적격
```

> **범위를 넓히는 것은 제약을 푸는 것이 아니라 조이는 것이다.**

**정확하다. 그리고 내가 반대로 생각했다.**

## Finnhub 약관을 처음으로 읽었다

**`allowed` 에 등재된 채로 아무도 약관을 안 읽은 상태가 오늘까지 왔다.** `robots.txt` 가 `/terms-of-service` 를 막았고, 내가 `PRIV-ARR-17` 에서 "약관 문서는 확인 목적으로 조회할 수 있다" 를 표준으로 정해 놓고도 그 표준을 이 건에 잇지 못했다.

**NTM 이 읽었고 `FMP`·`AV` 보다 강한 조항이 나왔다.** 보존된 원문에서 확인했다.

> You hereby agree to **not redistribute or share access to data or derived results** from the data obtained from Finnhub with anyone or any 3rd party without written approval.

**`derived results` 가 들어 있다.** 우리 채점표·HTML 리포트가 바로 파생 결과다. **개인 전용이어도 누구에게든 보여주는 순간 걸린다.** 다른 둘은 사용 주체만 제한하는데 **Finnhub 은 산출물의 유통까지 제한한다.**

## 그래서 — 쓰지 않는 것을 내린다

**셋 다 실제로 아무 데도 안 쓰인다.**

| | 왜 안 쓰나 |
|---|---|
| Alpha Vantage | 향후 분기 전망이 **2개뿐**이라 F6 부적격 (`av-source-11`) |
| FMP | `period=quarter` 가 유료라 **0/12** |
| Finnhub | basis 미확인으로 보류 중 |

**지금 F6·F9 가 먹는 것은 `data.sec.gov`·`www.sec.gov`·연준 H.10·프로젝트 내 v1.5 원본뿐이다.**

**따라서 사용자에게 "개인 전용으로 선언할까요" 를 되묻지 않는다.** 쓰지도 않는 원천 때문에 `usage_scope` 를 좁히는 것은 **꼬리가 몸통을 흔드는 것**이고, 오늘 `guardrails ENTRY-004` 에 적은 실수를 한 번 더 하는 것이다.

### 확정

```
alpha_vantage       →  내린다.  사유: 자료 부적격(분기 전망 2개) + 법인 사용 포괄 배제
financialmodelingprep.com →  내린다.  사유: 무료 등급 분기 미제공(0/12) + 법인 사용 포괄 배제
finnhub.io          →  내린다.  사유: basis 미확인 + 법인 사용 배제 + 파생 결과 재배포 제한
```

**되살리려면 두 조건이 먼저다** — `usage_scope` 를 **개인 전용**으로 좁히고, Finnhub 은 **파생 결과 공유에 대한 서면 승인**까지 받아야 한다. **그 조건을 등재 사유란에 적어 둔다.** 다음 사람이 "왜 뺐나" 를 되묻지 않게.

`usage_scope` 를 **개인+법인 합집합으로 넓히는 것 자체는 확정대로 간다.** 사용자 결정이고, 세 원천을 안 쓰는 이상 그것 때문에 잃는 것이 없다.

---

## 코드 결함 — `conditional_candidates` 키를 바꾸면 안내가 뒤집힌다

NTM 이 5절에서 짚었다. `rules.py` 의 `source_violation` 이 **`conditional_candidates` 를 직접 읽는다.**

```python
for entry in policy.get("conditional_candidates", []):
    ... return f"{host} 는 미승인 후보 — 서면 확정 필요: {need}"
```

`data.nasdaq.com` 을 `not_adopted` 로 옮기면 **이 분기를 안 타고 마지막 fallback 으로 떨어진다.**

```python
return f"{host} 는 원천 allowlist 에 없음 — 약관 확인 후 규칙에 등재하고 쓴다"
```

**"약관 확인 후 등재하고 쓰라" 는 안내가 나온다.** 우리는 `$1,200` 가격 때문에 **채택하지 않기로 한 것**인데, 안내가 **재조사를 지시한다.** 닫으려던 것이 다시 열리는 문구가 자동으로 나온다.

**`rules.py` 패치가 같이 가야 한다는 지적이 맞다.** 키만 바꾸는 것은 결함이다.

## 제안까지만 하고 멈춘 판단

> worker 가 `v1.7.json` 과 `schema.py` 를 **미커밋 수정 중**이고 제 브랜치에는 `scorecard` 트리가 없어 편집을 멈추고 제안까지만 했습니다.

**옳다.** 지시서에 "충돌 우려가 있으면 제안만 하고 멈춘 뒤 보고" 라고 적었고 그 조건에 정확히 해당한다. **영역 충돌은 없고 파일 충돌만 있다** 는 구분도 정확하다 — worker diff 에 `sources`·`USAGE_SCOPES` 가 없음을 확인한 뒤 내린 판단이다.

제안을 **즉시 적용 가능한 형태**(`proposal-sources-v1.7.json` 완성 블록 + `proposal-code.md` 패치 3건)로 낸 것도 맞다. **멈추되 다음 사람이 바로 쓸 수 있게 뒀다.**

## 후속

| 건 | 처리 |
|---|---|
| **세 원천 하향** | worker — 되살림 조건을 사유란에 |
| **`usage_scope` 합집합** | worker — 확정대로 |
| **`not_adopted` + `rules.py` 패치** | worker — 키만 바꾸면 안내가 뒤집힌다 |
| 적용 시점 | worker `PRIV-IMPL-31` 보완과 함께 |
