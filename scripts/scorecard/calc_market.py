# 규칙 v3.0 ① D·E: 시장 정의표와 시장 관측으로 사업의 시장 순위(D)와 1년 사이 점유율 방향(E)을 잰다
from __future__ import annotations

from datetime import date
from typing import Any

from .inputs import ObsLookup
from .rules import RuleSet, piecewise
from .schema import MARKET_COMPANY_ID, MARKET_MEASURES

# 1년 전 기간은 최근 기간의 시작·끝에서 365일 앞이고, 달력 분기와 회계 분기의 어긋남을 이만큼 받는다.
YEAR_TOLERANCE_DAYS = 31
# 2026-10-15: 반올림 폭과 견줄 때 부동소수 끝자리를 지운다(0.23 − 0.22 = 0.010000000000000009 가 폭 0.01 보다 크게 나왔다).
DIGITS = 9


def _metric(market: dict[str, Any]) -> str:
    return "market_share" if market["value_kind"] == "share" else MARKET_MEASURES[market["measure"]]


def _periods(market: dict[str, Any], obs: ObsLookup, as_of: str) -> dict[tuple[str, str], dict[str, tuple[float, str]]]:
    """기준일까지 끝난 기간마다 {구성 회사: (값, 관측 ID)}. 검증된(verified) 값만 쓴다."""
    members = {m["key"] for m in market["constituents"]}
    out: dict[tuple[str, str], dict[str, tuple[float, str]]] = {}
    for o in obs.all(MARKET_COMPANY_ID, _metric(market)):
        basis = o.get("basis") or {}
        period = o.get("period") or {}
        if basis.get("market_id") != market["market_id"] or o["value"] is None or o["status"] != "verified":
            continue
        if basis.get("constituent") not in members or not period.get("end") or period["end"] > as_of:
            continue
        out.setdefault((period["start"], period["end"]), {})[basis["constituent"]] = (float(o["value"]), o["observation_id"])
    return out


def _year_before(latest: tuple[str, str], periods: list[tuple[str, str]]) -> tuple[str, str] | None:
    start, end = (date.fromisoformat(x) for x in latest)
    for p in periods:
        ps, pe = (date.fromisoformat(x) for x in p)
        if abs((start - ps).days - 365) <= YEAR_TOLERANCE_DAYS and abs((end - pe).days - 365) <= YEAR_TOLERANCE_DAYS:
            return p
    return None


def _shares(market: dict[str, Any], values: dict[str, tuple[float, str]]) -> tuple[dict[str, float] | None, str | None]:
    """구성 회사 점유율. 금액·대수면 구성 회사 합으로 나누므로 한 곳이라도 빠지면 낼 수 없다."""
    if market["value_kind"] == "share":
        return {k: v for k, (v, _oid) in values.items()}, None
    missing = [m["key"] for m in market["constituents"] if m["key"] not in values]
    if missing:
        return None, f"구성 회사 {missing} 의 값이 없어 공시 합산 점유율을 낼 수 없다"
    total = sum(v for v, _oid in values.values())
    if total <= 0:
        return None, "구성 회사 합이 0 이하다"
    return {k: v / total for k, (v, _oid) in values.items()}, None


def _groups(market: dict[str, Any]) -> dict[str, list[str]]:
    """회사별 구성 회사 묶음. company_id 가 있으면 그 회사로 묶고, 없으면 구성 회사 하나가 한 묶음이다.

    2026-10-15: 시장 순위는 회사끼리 견준다. 소셜 미디어의 Facebook·Instagram 처럼 한 회사가 여러 구성 회사로 잡히면 합친다."""
    groups: dict[str, list[str]] = {}
    for m in market["constituents"]:
        groups.setdefault(m.get("company_id") or m["key"], []).append(m["key"])
    return groups


def _grouped(shares: dict[str, float], groups: dict[str, list[str]]) -> dict[str, float]:
    """구성 회사가 모두 있는 묶음의 합친 점유율."""
    return {g: sum(shares[k] for k in keys) for g, keys in groups.items() if all(k in shares for k in keys)}


def _rank_level(shares: dict[str, float], me: str, spec: dict[str, Any], err: dict[str, float]) -> tuple[str | None, int | None, str | None]:
    """D 칸. 반올림 폭 안에서 순위나 지배 조건이 갈리면 확정하지 않는다(rules.md ① 「반올림 경계」).

    `err` 는 묶음마다 반올림 오차의 끝(구성 회사 수 × 반올림 폭의 절반)이다. 두 값의 차이는 두 오차를 더한 만큼 흔들린다."""
    mine = shares[me]
    others = sorted(((g, v) for g, v in shares.items() if g != me), key=lambda x: -x[1])
    rank = 1 + sum(1 for _g, v in others if v > mine)
    # 2026-10-15: 두 반올림 구간이 한 점에서 맞닿기만 하면 겹치지 않는다(23% → [22.5, 23.5), 22% → [21.5, 22.5)).
    # 차이가 오차 합보다 작을 때만 순위가 바뀔 수 있다. 값이 똑같으면(공시 합산의 동률) 공동 순위라 확정하지 않는다.
    if any(round(abs(v - mine), DIGITS) < round(err[me] + err[g], DIGITS) or round(abs(v - mine), DIGITS) == 0 for g, v in others):
        return None, rank, "다른 회사와 점유율 차이가 반올림 폭 안이라 순위를 확정하지 않는다"
    if rank > 1:
        return {2: "second", 3: "third"}.get(rank, "other"), rank, None
    g2, second = others[0] if others else (me, 0.0)
    e_me, e_2 = err[me], (err[g2] if others else 0.0)
    dom = spec["dominant_if"]
    lead, floor = float(dom["lead_multiple"]), float(dom["share_at_least"])
    sure = (round(mine - e_me - lead * (second + e_2), DIGITS) >= 0 or round(mine - e_me - floor, DIGITS) >= 0)
    maybe = (round(mine + e_me - lead * max(second - e_2, 0.0), DIGITS) >= 0 or round(mine + e_me - floor, DIGITS) >= 0)
    if sure:
        return "dominant", rank, None
    if not maybe:
        return "first", rank, None
    return None, rank, "1위이나 2배·50% 조건이 반올림 폭 안에서 갈려 4 와 3 가운데 확정하지 않는다"


def market_position(market: dict[str, Any], obs: ObsLookup, company_id: str, as_of: str, rules: RuleSet) -> dict[str, Any]:
    """한 구성 사업의 D·E. 값을 낼 수 없는 부분은 None 이고 이유를 notes 에 적는다(호출하는 쪽이 만점의 40% 로 바꾼다)."""
    parts = rules.factor("F1")["parts"]
    out: dict[str, Any] = {"market_id": market["market_id"], "label": market["label"], "measure": market["measure"],
                           "D": None, "E": None, "notes": [], "observation_ids": [],
                           "outside": [o["name"] for o in market.get("outside") or []]}
    groups = _groups(market)
    me = company_id if company_id in groups and any(m.get("company_id") == company_id for m in market["constituents"]) else None
    if me is None:
        # 2026-10-15: 구성 회사가 출처의 상위 N 목록이면 목록 밖 회사는 N 위 밖이다. D 는 "그 밖"으로 확정하고 E 는 잴 수 없다.
        if market.get("lists_top_n"):
            out["D_level"], out["D"] = "other", float(parts["D"]["levels"]["other"])
            out["notes"].append(f"출처의 상위 {len(groups)}곳 목록에 없어 {len(groups)}위 밖이다(D 그 밖). 점유율 방향은 잴 수 없다")
        else:
            out["notes"].append(f"이 회사가 시장 {market['market_id']} 의 구성 회사에 없다")
        return out
    out["constituent"] = "+".join(groups[me])
    periods = _periods(market, obs, as_of)
    if not periods:
        out["notes"].append(f"기준일 {as_of} 까지 시장 {market['market_id']} 의 검증된 관측이 없다")
        return out
    latest = max(periods, key=lambda p: (p[1], p[0]))
    out["period"] = {"start": latest[0], "end": latest[1]}
    precision = float(market.get("precision", 0.001 if market["value_kind"] == "share" else 0.0))
    err = {g: len(keys) * precision / 2 for g, keys in groups.items()}
    raw, why = _shares(market, periods[latest])
    shares = _grouped(raw, groups) if raw is not None else None
    if shares is None or me not in shares:
        out["notes"].append(why or f"최근 기간 {latest[1]} 에 이 회사의 값이 없다")
        return out
    out["observation_ids"] += [oid for _v, oid in periods[latest].values()]
    out["share"] = shares[me]
    complete = len(shares) == len(groups)
    if complete:
        level, rank, note = _rank_level(shares, me, parts["D"], err)
        out["rank"] = rank
        if level is not None:
            out["D_level"] = level
            out["D"] = float(parts["D"]["levels"][level])
        else:
            out["notes"].append(note)
    else:
        missing = [m["key"] for m in market["constituents"] if m["key"] not in raw]
        out["notes"].append(f"최근 기간에 구성 회사 {missing} 의 점유율이 없어 순위를 확정하지 않는다")
    prior = _year_before(latest, list(periods))
    if prior is None:
        out["notes"].append(f"최근 기간 {latest[0]}~{latest[1]} 의 1년 전 기간 관측이 없어 점유율 방향을 잴 수 없다")
        return out
    prior_raw, why = _shares(market, periods[prior])
    prior_shares = _grouped(prior_raw, groups) if prior_raw is not None else None
    if prior_shares is None or me not in prior_shares:
        out["notes"].append(why or f"1년 전 기간 {prior[1]} 에 이 회사의 값이 없다")
        return out
    out["observation_ids"] += [oid for _v, oid in periods[prior].values()]
    out["prior_period"] = {"start": prior[0], "end": prior[1]}
    out["share_prior"] = prior_shares[me]
    change = (shares[me] - prior_shares[me]) * 100
    low = change - 2 * err[me] * 100   # 두 기간의 반올림 오차 끝을 더한 낮은 쪽
    out["change_pp"], out["change_pp_low"] = change, low
    # 반올림 폭이 있으면 두 끝을 함께 적고 낮은 쪽으로 잰다(rules.md ① 「반올림 경계」).
    out["E"] = piecewise(parts["E"]["curve"], low)
    if market["period_basis"] == "annual":
        out["notes"].append("연간 자료라 같은 연도끼리 견줬다(1년 늦음)")
    return out
