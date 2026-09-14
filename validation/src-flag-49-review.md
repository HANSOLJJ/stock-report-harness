# SRC-FLAG-49 검토 — StockAnalysis 장부 등재

- 검토일. 2026-09-14. 대상 worker `5c7b77d` + `be9176a`. 판정 **pass.** 348건 · 순위 불변.

## 지시와 다른 셋 — 전부 worker 가 맞다

| 다른 점 | 판정 |
|---|---|
| market_cap 11 → **12** (spacex-xai 포함) | 내 11 은 점수 경로 수. 표시는 상류 기준 — worker 가 맞다 |
| tsmc·alibaba `author_computed` | 46 과 일관. NTM ✱ 표식과 일치 |
| `reason_type: legacy_upstream` 신설 | **핵심.** 아래 |

## legacy_upstream — 선언에 소비자가 있다

```
schema.py 356행      reason_type ∈ (cost, …, legacy_upstream) 검사
rules.py 59행        source_violation 이 별도 분기

stockanalysis.com → "legacy 관측의 상류로만 장부에 올린 원천 — 채택 검토를 하지 않았고 새 수집에 쓰지 않는다 …"
FMP               → "검토를 마치고 채택하지 않기로 결정된 원천 …"   (기존)
data.sec.gov      → None
```

**두 함정을 다 피했다.** 기존 not_adopted 문구 `검토를 마치고` 를 StockAnalysis 에 쓰면 거짓이고(검토한 적 없음), fallback 으로 떨어지면 `약관 확인 후 등재하고 쓴다` 가 나와 재개를 지시한다(SRC-POLICY-32 에서 잡은 결함). 새 분기는 **새로 쓰지 않는다는 것만** 말한다. 주석에 그 이유가 있다.

## HASH-EOL (be9176a)

내가 "note 한 줄" 을 요청했는데 worker 가 **기제**를 찾았다 — `sha256_file = read_bytes` · `.gitattributes` 없음 · `core.autocrlf=true`(Git for Windows 시스템 설정). 고치지 않고 등재. 승인 흐름 손볼 때 정규화 검토 항목으로.

## 확인된 표시

market_cap 12건 `vendor_not_in_source_policy` · net_cash apple·palantir `source_mixed` · sources 블록에 `source_id 는 검사 밖` note.

## 남은 큐

worker `IMPL-50`(C-11) — 마지막. 끝나면 큐가 빈다.
