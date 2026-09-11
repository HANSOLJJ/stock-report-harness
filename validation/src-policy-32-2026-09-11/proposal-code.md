# SRC-POLICY-32 — 코드 변경 제안 (적용하지 않음)

worker 가 `PRIV-IMPL-31` 로 `scripts/scorecard/schema.py` 와 `scorecard/rules/v1.7.json` 을 **미커밋 수정 중**이라 적용하지 않고 제안으로만 낸다. 각 패치는 worker 의 현재 수정 영역과 겹치지 않는다(§0 확인).

---

## P1. `schema.py` — `usage_scope` 를 허용 범위로

### 현재 (`worker/scripts/scorecard/schema.py:250-291`)

```python
# 산출물 사용 범위. 원천 약관의 '개인 사용 허용' 조항이 우리에게 적용되는지를 가르는 값이라
# 자유 문자열로 두지 않는다. personal_internal_only 는 2026-09-10 에 폐기됐으나 과거 규칙
# 파일을 읽을 수 있어야 하므로 남긴다.
USAGE_SCOPES = frozenset({"personal_internal_only", "corporate_internal_only", "external_distribution"})
...
    if "usage_scope" in policy:
        scope = policy["usage_scope"]
        _expect_keys(scope, ["scope", "decided_at", "statement", "condition"], "rules.sources.usage_scope",
                     optional=[...])
        for key in (...):
            _require(str(scope.get(key) or "").strip(), f"rules.sources.usage_scope: {key} 를 비워 둘 수 없음")
        _require(scope["scope"] in USAGE_SCOPES,
                 f"rules.sources.usage_scope: scope 는 {sorted(USAGE_SCOPES)} 중 하나여야 함 — {scope['scope']!r}")
```

### 제안

```python
# 산출물 사용 범위. 원천 약관의 '개인 사용 허용' 조항이 우리에게 적용되는지를 가르는 값이라
# 자유 문자열로 두지 않는다. 2026-09-11 에 단일값에서 허용 범위(집합)로 바뀌었다 — 개인 사용과
# 법인 내부 사용이 둘 다 실제 사용이기 때문이다(SRC-POLICY-32).
USAGE_SCOPES = frozenset({"personal_internal_only", "corporate_internal_only", "external_distribution"})


def normalize_usage_scopes(scope: dict) -> set[str]:
    """scopes(신규 배열)와 scope(과거 단일값)를 모두 받아 집합으로 정규화한다.
    과거 규칙 파일(v1.6·v1.7 초판)이 단일 문자열이므로 한쪽을 지우지 않는다.
    v1.5 는 sources 블록 자체가 없어 이 경로를 타지 않는다."""
    if "scopes" in scope:
        values = scope["scopes"]
        _require(isinstance(values, list) and values,
                 "rules.sources.usage_scope.scopes: 비어 있지 않은 배열이어야 함")
        _require(len(set(values)) == len(values),
                 "rules.sources.usage_scope.scopes: 중복은 허용하지 않음")
    else:
        _require("scope" in scope,
                 "rules.sources.usage_scope: scopes 또는 scope 중 하나가 필요함")
        values = [scope["scope"]]
    unknown = [v for v in values if v not in USAGE_SCOPES]
    _require(not unknown,
             f"rules.sources.usage_scope: 알 수 없는 값 {unknown!r} — {sorted(USAGE_SCOPES)} 중에서 쓴다")
    return set(values)
```

그리고 검증부를 이렇게 바꾼다.

```python
    if "usage_scope" in policy:
        scope = policy["usage_scope"]
        # scope(과거)와 scopes(신규) 중 하나는 있어야 하고 둘 다 있으면 안 된다.
        _require(("scope" in scope) != ("scopes" in scope),
                 "rules.sources.usage_scope: scope 와 scopes 중 정확히 하나만 둔다")
        _expect_keys(scope, ["decided_at", "statement", "condition"], "rules.sources.usage_scope",
                     optional=["scope", "scopes", "note", "evaluation_rule"])
        for key in ("decided_at", "statement", "condition"):
            _require(str(scope.get(key) or "").strip(),
                     f"rules.sources.usage_scope: {key} 를 비워 둘 수 없음")
        normalize_usage_scopes(scope)
```

**핵심은 `!=` 로 배타를 강제하는 줄이다.** 둘 다 두면 어느 쪽이 정본인지 모르게 되고, 그 상태가 바로 [값을 좁혔는데 좁혔다는 사실이 안 남는] 이번 라운드의 반복 실패 형태다.

`_expect_keys` 의 필수 목록에서 `scope` 를 빼고 optional 로 내린 것이 하위호환의 전부다.

---

## P2. `rules.py` — `not_adopted` 를 `source_violation()` 이 읽게

### 왜 필요한가

현재 `source_violation()` 은 `conditional_candidates` 를 직접 읽는다.

```python
        for entry in policy.get("conditional_candidates", []):
            if host == entry["host"] or host.endswith("." + entry["host"]):
                need = ", ".join(entry["required_written_conditions"])
                return f"{host} 는 미승인 후보 — 서면 확정 필요: {need}"
```

`conditional_candidates` 를 `not_adopted` 로 바꾸기만 하고 이 코드를 안 고치면 `data.nasdaq.com` 은 **마지막 fallback 으로 떨어진다.**

```python
        return f"{host} 는 원천 allowlist 에 없음 — 약관 확인 후 규칙에 등재하고 쓴다"
```

**이 메시지가 정확히 우리가 막으려는 행동을 지시한다** — "약관 확인 후 등재하고 쓴다". 다음 사람이 D1~D5 를 다시 파게 된다. 상태 이름만 바꾸면 문제가 되레 악화된다.

### 제안

```python
        for entry in policy.get("not_adopted", []):
            if host == entry["host"] or host.endswith("." + entry["host"]):
                return (f"{host} 는 검토를 마치고 채택하지 않기로 결정된 원천 — "
                        f"{entry['reason']} (결정 {entry['decided_at']}, {entry['decided_by']}). "
                        f"재조사 불필요. 재개 조건: {entry['reopen_condition']}")
        # 과거 규칙 파일 호환. v1.6·v1.7 초판은 conditional_candidates 를 쓴다.
        for entry in policy.get("conditional_candidates", []):
            if host == entry["host"] or host.endswith("." + entry["host"]):
                need = ", ".join(entry["required_written_conditions"])
                return f"{host} 는 미승인 후보 — 서면 확정 필요: {need}"
```

**두 블록을 다 둔다.** `not_adopted` 를 먼저 보고, 없으면 과거 키를 본다. v1.6 을 그대로 읽을 수 있어야 하므로 옛 블록을 지우지 않는다.

---

## P3. `schema.py` — `not_adopted` 검증

`_validate_source_policy` 의 `optional` 에 `not_adopted` 를 더하고 검증을 추가한다.

```python
    _expect_keys(policy, ["policy_note", "enforcement", "allowed", "denied"], "rules.sources",
                 optional=["conditional_candidates", "not_adopted", "usage_scope", "unlisted"])
```

```python
    # 채택 안 함. denied 와 가르는 이유는 사유의 종류가 다르기 때문이다 —
    # denied 는 쓸 자격이 없는 것이고 not_adopted 는 자격은 있으나 안 쓰기로 한 것이다.
    for idx, entry in enumerate(policy.get("not_adopted") or []):
        where = f"rules.sources.not_adopted[{idx}]"
        _expect_keys(entry, ["host", "status", "reason_type", "reason", "decided_at",
                             "decided_by", "reopen_condition"], where,
                     optional=["name", "note", "prior_investigation"])
        for key in ("host", "reason", "decided_at", "decided_by", "reopen_condition"):
            _require(str(entry.get(key) or "").strip(), f"{where}: {key} 필요")
        _require(entry["status"] == "not_adopted", f"{where}: status 는 not_adopted 여야 함")
        # 사유를 뭉뚱그리지 않는다. 비용 판단과 약관 배제는 다른 결정이다.
        _require(entry["reason_type"] in ("cost", "technical", "terms", "redundant"),
                 f"{where}: reason_type 은 cost/technical/terms/redundant 중 하나여야 함")
        _require(entry["host"] not in hosts,
                 f"{where}: host {entry['host']!r} 는 allowed/denied 와 겹칠 수 없음")
        hosts[entry["host"]] = "not_adopted"
```

`reopen_condition` 을 **필수**로 둔 것이 이 제안의 요점이다. 닫되 **어떤 조건에서 다시 여는지**를 적게 강제하면 "영구 배제" 와 "지금은 안 함" 이 섞이지 않는다.

---

## P4. `schema.py` — `unlisted` 에 `relist_condition` (검토 확정 반영, v2)

확정 처리로 Alpha Vantage·FMP·Finnhub 세 원천이 `allowed` 에서 `unlisted` 로 내려간다. 설계진행이 "되살리려면 무엇이 필요한지를 등재 사유란에 적는다" 를 요구했으므로 전용 필드를 둔다.

```python
    for idx, entry in enumerate(policy.get("unlisted") or []):
        where = f"rules.sources.unlisted[{idx}]"
        _expect_keys(entry, ["host", "reason_type", "reason", "decided_at"], where,
                     optional=["note", "evidence", "relist_condition"])
```

`optional` 에 `relist_condition` 한 항목을 더하는 것이 전부다. 필수가 아닌 이유는 **되살릴 길이 없는 미등재도 있기 때문**이다(기술적으로 영구 부적격인 경우). 조건이 있으면 적고 없으면 비운다.

`not_adopted` 의 `reopen_condition` 과 이름을 다르게 둔 것은 의도적이다. **`unlisted` 는 애초에 등재된 적이 없으니 `relist`(등재) 이고, `not_adopted` 는 후보였다가 닫힌 것이니 `reopen`(재개) 이다.** 같은 이름을 쓰면 두 상태의 차이가 흐려진다.

### 적용 순서 주의

`proposal-sources-v1.7-v2.json` 의 `unlisted` 항목 셋은 `relist_condition` 을 갖는다. **P4 를 먼저 넣지 않으면 `_expect_keys` 가 알 수 없는 키로 거부한다.** 규칙 파일보다 스키마를 먼저 고친다.
