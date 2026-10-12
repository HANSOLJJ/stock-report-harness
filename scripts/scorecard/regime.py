# AI 사이클 국면 지표(설비투자 가속도·공급자 지원 비중·토큰 단가 지수·트리거 조건)를 관측에서 계산하는 점수 밖 표시(규칙 v2.1 2-C-1)
"""규칙 v2.1 `policies.regime_indicators` 가 있을 때만 리포트 머리에 싣는다. results.json 에 넣지 않고 렌더할 때 계산한다.

- 국면에 이름(1국면·2국면)을 붙이지 않는다. 원값과 전년 대비 증가율, 그 변화만 보인다. Z 점수는 쓰지 않는다(2023년 이후 한 국면뿐인
  이력으로 기준 분포를 만들면 임의 숫자가 된다).
- 분기 값은 달력 분기로 맞춘다. 회계 분기의 가운데 날짜가 속한 달력 분기에 넣는다(Oracle 3~5월 → 2분기, NVIDIA 5~7월 → 2분기).
  끝 달로 맞추면 NVIDIA 처럼 분기 끝이 달 초·말에 걸친 회사가 한 칸 어긋난다.
- 사는 쪽 금융리스 취득 자산은 그 회사의 금융리스 분기 값이 필요한 분기에 모두 있을 때만 더한다. 모자라면 현금 설비투자만 쓰고 표시한다.
- 자료가 모자라면 값을 만들지 않는다. 미확인을 0 으로 보지 않는다.
"""
from __future__ import annotations

from datetime import date
from typing import Any

from .inputs import USABLE_STATUSES, ObsLookup, recency_key
from .schema import MARKET_COMPANY_ID

SUPPLIER_COMPONENTS = ("supplier_guarantees", "supplier_customer_investments", "supplier_capacity_buyback")
TRIGGER_IDS = {"capex_decel_2q", "supplier_support_rising"}


def regime_spec(rules: Any) -> dict[str, Any] | None:
    return (rules.payload.get("policies") or {}).get("regime_indicators")


def calendar_key(start: str, end: str) -> tuple[int, int]:
    """회계 분기 → (연도, 달력 분기). 분기의 가운데 날짜가 속한 달력 분기다."""
    s, e = date.fromisoformat(start), date.fromisoformat(end)
    mid = s + (e - s) / 2
    return mid.year, (mid.month - 1) // 3 + 1


def shift(key: tuple[int, int], back: int) -> tuple[int, int]:
    n = key[0] * 4 + (key[1] - 1) - back
    return n // 4, n % 4 + 1


def key_label(key: tuple[int, int]) -> str:
    return f"{key[0]}Q{key[1]}"


def _usable(o: dict[str, Any]) -> bool:
    v = o.get("value")
    return o["status"] in USABLE_STATUSES and isinstance(v, (int, float)) and not isinstance(v, bool) and bool(o.get("period"))


def quarter_values(obs: ObsLookup, cid: str, metric: str, segment: str | None = None) -> dict[tuple[int, int], dict[str, Any]]:
    """달력 분기 → 관측. 같은 분기에 관측이 여럿이면(다시 수집해 재작성된 값) verified 를 먼저, 그다음 최신을 고른다.
    `segment` 를 주면 basis.segment 가 그것인 관측만 본다."""
    best: dict[tuple[int, int], dict[str, Any]] = {}
    for o in obs.all(cid, metric):
        if not _usable(o) or (segment is not None and (o.get("basis") or {}).get("segment") != segment):
            continue
        k = calendar_key(o["period"]["start"], o["period"]["end"])
        rank = (o["status"] == "verified", recency_key(o))
        prev = best.get(k)
        if prev is None or rank > (prev["status"] == "verified", recency_key(prev)):
            best[k] = o
    return best


def company_capex(obs: ObsLookup, cid: str, keep: int) -> dict[str, Any]:
    """한 회사의 분기 설비투자 시계열(최근 keep 개 분기). 금융리스를 더할 수 있으면 더한다."""
    capex = quarter_values(obs, cid, "capex_quarterly")
    keys = sorted(capex)[-keep:]
    fl = quarter_values(obs, cid, "finance_lease_additions_quarterly")
    with_fl = bool(keys) and all(k in fl for k in keys)
    values = {k: capex[k]["value"] + (fl[k]["value"] if with_fl else 0) for k in keys}
    return {"values": values, "ends": {k: capex[k]["period"]["end"] for k in keys},
            "definition": "cash_plus_finance_lease" if with_fl else "cash_only",
            "finance_lease_partial": bool(fl) and not with_fl}


def growth(values: dict[tuple[int, int], float], key: tuple[int, int]) -> float | None:
    base = values.get(shift(key, 4))
    cur = values.get(key)
    if cur is None or base is None or base <= 0:
        return None
    return cur / base - 1


def direction(change: float, band: float) -> str:
    return "accelerating" if change > band else ("decelerating" if change < -band else "steady")


def acceleration(values: dict[tuple[int, int], float], spec: dict[str, Any]) -> dict[str, Any]:
    """최근 분기의 전년 대비 증가율, 직전 분기의 것, 그 변화와 방향, 2개 분기 연속 감속 여부."""
    keys = sorted(values)
    if len(keys) < spec["min_quarters"]:
        return {"status": "insufficient", "quarters": len(keys), "need": spec["min_quarters"]}
    t = keys[-1]
    g0, g1, g2 = growth(values, t), growth(values, shift(t, 1)), growth(values, shift(t, 2))
    if g0 is None or g1 is None:
        return {"status": "insufficient", "quarters": len(keys), "need": spec["min_quarters"], "gap": True}
    band = spec["flat_band"]
    out = {"status": "ok", "latest": t, "value": values[t], "growth": g0, "growth_prev": g1, "change": g0 - g1,
           "direction": direction(g0 - g1, band), "quarters": len(keys)}
    # 증가율 셋(7개 분기)이 있어야 '2개 분기 연속 감속' 을 판정한다. 모자라면 None(자료 부족)이다.
    out["two_quarter_deceleration"] = (None if g2 is None else
                                       out["direction"] == "decelerating" and direction(g1 - g2, band) == "decelerating")
    return out


def capex_board(obs: ObsLookup, run_companies: list[str], spec: dict[str, Any]) -> dict[str, Any]:
    cs = spec["capex"]
    keep = cs["quarters_kept"]
    members = [c for c in cs["basket"] if c in run_companies]
    rows = []
    series = {}
    for cid in members:
        s = company_capex(obs, cid, keep)
        series[cid] = s
        rows.append({"company_id": cid, **s, "indicator": acceleration(s["values"], cs)})
    keys = set().union(*(s["values"] for s in series.values())) if series else set()
    basket_values = {k: sum(series[c]["values"][k] for c in members) for k in keys
                     if all(k in series[c]["values"] for c in members)}
    return {"rows": rows, "basket": {"members": members, "values": basket_values, "indicator": acceleration(basket_values, cs)},
            "missing_from_run": [c for c in cs["basket"] if c not in run_companies]}


def offbalance(obs: ObsLookup, run_companies: list[str]) -> list[dict[str, Any]]:
    """장부 밖 설비 잔존가치 보증. 설비투자에 더하지 않고 따로 보인다."""
    out = []
    for cid in run_companies:
        v, o = obs.number(cid, "residual_value_guarantee")
        if v is not None:
            out.append({"company_id": cid, "value": v, "as_of": o["as_of"]})
    return out


def supplier_support(obs: ObsLookup, run_companies: list[str], spec: dict[str, Any]) -> list[dict[str, Any]]:
    """공급자 지원 비중 = (보증 + 고객 출자 + 용량 되사기) ÷ 최근 1년 매출. 기준일마다 셋이 다 있을 때만 합을 만든다."""
    out = []
    for cid in [c for c in spec["supplier_support"]["companies"] if c in run_companies]:
        by_date: dict[str, dict[str, float]] = {}
        for m in SUPPLIER_COMPONENTS:
            for o in obs.all(cid, m):
                if o["status"] in USABLE_STATUSES and isinstance(o.get("value"), (int, float)):
                    by_date.setdefault(o["as_of"], {})[m] = o["value"]
        revenue = {(o.get("period") or {}).get("end"): o["value"] for o in obs.all(cid, "revenue_ttm")
                   if o["status"] in USABLE_STATUSES and isinstance(o.get("value"), (int, float)) and o.get("period")}
        points = []
        for d in sorted(by_date):
            comps = by_date[d]
            total = sum(comps[m] for m in SUPPLIER_COMPONENTS) if all(m in comps for m in SUPPLIER_COMPONENTS) else None
            rev = revenue.get(d)
            points.append({"as_of": d, "components": comps, "total": total, "revenue": rev,
                           "ratio": total / rev if total is not None and rev else None})
        ratios = [p for p in points if p["ratio"] is not None]
        latest = points[-1] if points else None
        out.append({"company_id": cid, "latest": latest, "previous_ratio": ratios[-2]["ratio"] if len(ratios) >= 2 else None,
                    "rising": (ratios[-1]["ratio"] > ratios[-2]["ratio"]) if len(ratios) >= 2 and latest is ratios[-1] else None})
    return out


def token_index(obs: ObsLookup) -> list[dict[str, Any]]:
    """구간별 최신 값과 그 앞 관측. 실행마다 한 점씩 쌓인다."""
    by_segment: dict[str, list[dict[str, Any]]] = {}
    for o in obs.all(MARKET_COMPANY_ID, "token_price_index"):
        if o["status"] in USABLE_STATUSES and isinstance(o.get("value"), (int, float)):
            by_segment.setdefault((o.get("basis") or {}).get("segment"), []).append(o)
    out = []
    for seg, items in sorted(by_segment.items()):
        items.sort(key=lambda o: o["as_of"])
        cur, prev = items[-1], (items[-2] if len(items) >= 2 else None)
        out.append({"segment": seg, "value": cur["value"], "as_of": cur["as_of"], "source_id": cur["source_id"],
                    "previous": None if prev is None else {"value": prev["value"], "as_of": prev["as_of"]},
                    "change": None if prev is None or not prev["value"] else cur["value"] / prev["value"] - 1})
    return out


def _ratio(num: dict[tuple[int, int], dict[str, Any]], den: dict[tuple[int, int], dict[str, Any]]) -> dict[tuple[int, int], float]:
    """같은 달력 분기·같은 회계기간의 분자 ÷ 분모. 분모가 0 이하면 만들지 않는다."""
    return {k: num[k]["value"] / den[k]["value"] for k in num
            if k in den and den[k]["value"] > 0 and num[k]["period"] == den[k]["period"]}


def margin_board(obs: ObsLookup, run_companies: list[str], spec: dict[str, Any]) -> dict[str, Any]:
    """마진 두 수열: 공급자 분기 총마진과 클라우드 세그먼트 분기 영업이익률. 비용 범위가 달라 나누지 않고 나란히 둔다."""
    m = spec["margins"]
    rows = []
    for cid in [c for c in spec["supplier_support"]["companies"] if c in run_companies]:
        rows.append({"company_id": cid, "kind": "gross_margin", "segment": None,
                     "values": _ratio(quarter_values(obs, cid, "gross_profit_quarterly"), quarter_values(obs, cid, "revenue_quarterly"))})
    for cid, segment in m["cloud_segments"].items():
        if cid in run_companies:
            rows.append({"company_id": cid, "kind": "segment_operating_margin", "segment": segment,
                         "values": _ratio(quarter_values(obs, cid, "cloud_segment_operating_income_quarterly", segment),
                                          quarter_values(obs, cid, "cloud_segment_revenue_quarterly", segment))})
    keys = sorted(set().union(*(r["values"] for r in rows)))[-m["quarters_shown"]:] if rows else []
    return {"keys": keys, "rows": rows}


def trigger_status(trigger_id: str, board: dict[str, Any], supplier: list[dict[str, Any]]) -> str:
    """met | not_met | insufficient."""
    if trigger_id == "capex_decel_2q":
        flag = board["basket"]["indicator"].get("two_quarter_deceleration")
    else:
        flags = [s["rising"] for s in supplier]
        flag = None if not flags or any(f is None for f in flags) else any(flags)
    return "insufficient" if flag is None else ("met" if flag else "not_met")


def regime_board(observations: list[dict[str, Any]], run_companies: list[str], spec: dict[str, Any]) -> dict[str, Any]:
    obs = ObsLookup(observations)
    board = capex_board(obs, run_companies, spec)
    supplier = supplier_support(obs, run_companies, spec)
    return {"capex": board, "offbalance": offbalance(obs, run_companies), "supplier": supplier, "token": token_index(obs),
            "margins": margin_board(obs, run_companies, spec),
            "triggers": [{**t, "status": trigger_status(t["id"], board, supplier)} for t in spec["trigger_conditions"]]}
