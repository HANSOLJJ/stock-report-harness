# 매출에서 주당 현금까지 이어지는 현금 연결표를 관측에서 계산하는 진단(점수 없음, 규칙 v2.1 2-E)
"""회사마다 매출 → 영업이익 → 영업현금흐름 → 설비투자 → FCF → 주식보상 → 희석 주식 → 주당 FCF 를 한 줄로 만든다.

점수에 넣지 않고 results.json 에도 넣지 않는다. 리포트를 그릴 때 관측에서 바로 계산하므로 결과 해시에 닿지 않는다.
FCF 는 ⑨ 가 읽는 것과 같은 관측이다 — `ObsLookup.number` 의 같은 선택 규칙(verified 우선, 그다음 최신)을 쓴다. 그래서 연결표의
FCF 와 ⑨ 의 FCF 는 어긋날 수 없다. 대신 OCF − 설비투자를 그 FCF 와 대조해 기간이나 정의가 다르면 표시한다. AI 기여분은 공시로 가를 수
없어 만들지 않는다.
"""
from __future__ import annotations

from typing import Any

from .inputs import ObsLookup
from .schema import PERIOD_REQUIRED_METRICS

CHAIN_METRICS = ("revenue_ttm", "operating_income_ttm", "ocf_ttm", "capex_ttm", "fcf_ttm", "sbc_ttm", "shares_diluted")
CHECK_METRICS = ("ocf_ttm", "capex_ttm", "fcf_ttm")


def cash_chain_spec(rules: Any) -> dict[str, Any] | None:
    """규칙의 `policies.diagnostics.cash_chain`. 없으면 이 진단을 그리지 않는다(v2.0 이하 실행의 초안이 그대로 남는다)."""
    return ((rules.payload.get("policies") or {}).get("diagnostics") or {}).get("cash_chain")


def _end(metric: str, obs: dict[str, Any]) -> str | None:
    """흐름 지표는 회계기간 끝, 시점 지표(희석 주식)는 기준일. 기간이 없는 옛 흐름 관측은 None 이다 — as_of 는 이관 기준일이라
    회계기간 끝처럼 보이면 안 된다."""
    if metric in PERIOD_REQUIRED_METRICS:
        return (obs.get("period") or {}).get("end")
    return obs["as_of"]


def fcf_check(values: dict[str, float | None], ends: dict[str, str], tolerance: float) -> dict[str, Any]:
    """OCF − 설비투자와 ⑨ 의 FCF 대조. status: match | mismatch | period_mismatch | period_unknown | unavailable."""
    missing = [m for m in CHECK_METRICS if values.get(m) is None]
    if missing:
        return {"status": "unavailable", "missing": missing}
    unknown = [m for m in CHECK_METRICS if ends.get(m) is None]
    if unknown:
        return {"status": "period_unknown", "missing": unknown}
    if len({ends[m] for m in CHECK_METRICS}) > 1:
        return {"status": "period_mismatch", "ends": {m: ends[m] for m in CHECK_METRICS}}
    derived = values["ocf_ttm"] - values["capex_ttm"]
    diff = derived - values["fcf_ttm"]
    ok = abs(diff) <= tolerance * max(abs(values["fcf_ttm"]), 1.0)
    return {"status": "match" if ok else "mismatch", "derived": derived, "diff": diff}


def cash_chain_rows(observations: list[dict[str, Any]], companies: list[dict[str, Any]], spec: dict[str, Any]) -> list[dict[str, Any]]:
    """회사 한 줄씩. 값이 없는 칸은 None 이다 — 0 으로 채우지 않는다."""
    obs = ObsLookup(observations)
    out = []
    for c in companies:
        cid = c["company_id"]
        values: dict[str, float | None] = {}
        ends: dict[str, str | None] = {}
        missing_status: dict[str, str] = {}   # 값은 없지만 관측이 있는 칸의 상태(not_disclosed 면 '미공시' 로 적는다)
        for m in CHAIN_METRICS:
            v, o = obs.number(cid, m)
            values[m] = v
            if v is not None:
                ends[m] = _end(m, o)
            elif o is not None:
                missing_status[m] = o["status"]
        fcf, sbc, shares = values["fcf_ttm"], values["sbc_ttm"], values["shares_diluted"]
        per_share = fcf / shares if fcf is not None and shares else None
        per_share_after_sbc = (fcf - sbc) / shares if fcf is not None and sbc is not None and shares else None
        out.append({"company_id": cid, "display_name": c["display_name"], "values": values, "ends": ends, "missing_status": missing_status,
                    "fcf_per_share": per_share, "fcf_less_sbc_per_share": per_share_after_sbc,
                    "check": fcf_check(values, ends, spec["fcf_check_tolerance"])})
    return out
