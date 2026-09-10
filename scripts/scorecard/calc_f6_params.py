# ⑥ 가격 v1.7 파라미터 모드: P1 PER·P2 EV/Sales·P3 매출성장률 합계에 P4 입력신뢰도 보정을 적용한다
"""NTM PER 단일 지표를 네 파라미터로 분해한 계산기다.

`calc_f6.py` 의 per_band 경로(v1.5·v1.6)는 그대로 두고 여기서 갈라진다. 규칙 파일의
`policies.f6.mode` 가 `parameters` 일 때만 이 모듈이 쓰인다.

## 트랙은 선언된 기간 기준으로 정한다

**자료가 없다고 더 무른 트랙으로 내려보내지 않는다.** 입력이 없으면 `pending_data` 이지
트랙 변경이 아니다. 티커로 분기하지도 않는다 — SPCX 가 첫 10-K 를 내면 관측의
`basis.period_basis` 가 바뀌고 트랙도 따라 바뀌어야 한다.

## P4 는 소계에 걸린다

개별 파라미터가 아니라 F6 소계를 한 칸 내린다. 개별에 물리면 P1·P2 가 미산출인
트랙에서 적용 대상이 사라진다. 조건이 여럿 걸려도 한 칸이다.
"""
from __future__ import annotations

from typing import Any

from .inputs import ObsLookup, factor_result, obs_note, pending_info
from .rules import RuleSet

FACTOR = "F6"

# 트랙마다 기대하는 기간 기준. 관측이 다른 기준을 선언하면 조용히 넘기지 않고 pending 으로 세운다.
TRACK_EXPECTED_BASIS = {
    "listed_ttm": "ttm",
    "listed_annual": "annual",
    "listed_newly": "quarterly_yoy",
}


def _period_basis(o: dict[str, Any] | None) -> str | None:
    return ((o or {}).get("basis") or {}).get("period_basis")


def track_id_for(company: dict[str, Any], period_basis: str | None) -> str:
    if not company["listed"]:
        return "private"
    if company.get("share_basis") in ("adr", "ads"):
        return "listed_annual"
    if period_basis == "quarterly_yoy":
        return "listed_newly"
    return "listed_ttm"


def _nonop_share(cid: str, obs: ObsLookup, warnings: list[str]) -> tuple[float | None, dict[str, Any]]:
    """영업외 비중을 **원자료에서 재계산**한다. 완제품 `nonop_share` 관측은 대조용으로만 쓴다.

    `ttm_per`·`ps_ratio`·`nonop_share` 가 원자료 없이 완제품으로만 들어와 재계산도 검증도
    안 되던 상태를 반복하지 않는다.
    """
    detail: dict[str, Any] = {}
    ni, _ = obs.number(cid, "net_income_ttm")
    oi, _ = obs.number(cid, "operating_income_ttm")
    stored, stored_obs = obs.number(cid, "nonop_share")
    if stored_obs is not None:
        detail["nonop_share_stored"] = stored
    if ni is not None and oi is not None and ni != 0:
        value = (ni - oi) / ni
        detail["nonop_share"] = value
        detail["nonop_share_source"] = "recomputed"
        detail["nonop_share_inputs"] = {"net_income_ttm": ni, "operating_income_ttm": oi}
        if stored is not None and abs(stored - value) > 0.01:
            # 두 값이 다르면 조용히 고르지 않는다. 재계산값을 쓰되 차이를 남긴다.
            warnings.append(f"nonop_share 재계산 {value:.4f} 과 저장값 {stored:.4f} 이 다름 — 재계산값을 쓴다")
        return value, detail
    if stored is not None:
        detail["nonop_share"] = stored
        detail["nonop_share_source"] = "stored_only"
        warnings.append("nonop_share 를 재계산하지 못해 저장된 완제품 값을 썼다 — "
                        "원자료(net_income_ttm·operating_income_ttm) 필요")
        return stored, detail
    detail["nonop_share"] = None
    detail["nonop_share_source"] = "unavailable"
    return None, detail


def _p4(cid: str, obs: ObsLookup, rules: RuleSet, track: dict[str, Any],
        warnings: list[str]) -> dict[str, Any]:
    spec = rules.f6_p4()
    declared = {c["id"]: c for c in spec.get("conditions", [])}
    hit: list[str] = []
    detail: dict[str, Any] = {}

    cond = declared.get("nonop_share")
    if cond is not None:
        value, d = _nonop_share(cid, obs, warnings)
        detail.update(d)
        if value is not None and abs(value) >= float(cond.get("threshold", 0.30)):
            hit.append("nonop_share")

    # 트랙이 구조적으로 지는 조건(연간 대체·이력 부족)은 규칙이 선언한 대로 자동 적용한다.
    for auto in track.get("auto_p4_conditions", []):
        if auto in declared and auto not in hit:
            hit.append(auto)

    detail["conditions_hit"] = hit
    detail["demotion_steps"] = int(spec.get("cap_steps", 1)) if hit else 0
    return detail


def _parameter_value(pid: str, cid: str, obs: ObsLookup, rules: RuleSet,
                     obs_ids: list[str]) -> tuple[float | None, str | None, dict[str, Any]]:
    """(값, 미산출 사유, 입력 상세). **입력이 없으면 값을 만들지 않는다.**"""
    spec = rules.f6_parameters()[pid]
    raw: dict[str, Any] = {}
    for metric in spec["inputs"]:
        value, o = obs.number(cid, metric)
        if o is not None:
            obs_ids.append(o["observation_id"])
        raw[metric] = value
        if value is None:
            return None, f"{pid} 입력 {metric} 관측 없음", raw
    for metric in spec.get("requires_positive", []):
        if raw[metric] <= 0:
            return None, f"{pid} 입력 {metric} 이 0 이하({raw[metric]!r}) — 대체값으로 채우지 않음", raw
    if pid == "P1":
        return raw["market_cap"] / raw["net_income_ttm"], None, raw
    if pid == "P2":
        return (raw["market_cap"] - raw["net_cash"]) / raw["revenue_ttm"], None, raw
    if pid == "P3":
        return raw["revenue_ttm"] / raw["revenue_ttm_prior"] - 1, None, raw
    return None, f"{pid} 산식이 구현되지 않음", raw


def compute_listed(company: dict[str, Any], obs: ObsLookup, judgment: dict[str, Any] | None,
                   rules: RuleSet) -> dict[str, Any]:
    cid = company["company_id"]
    warnings: list[str] = []
    obs_ids: list[str] = []
    if judgment is not None:
        warnings.append(f"{judgment['judgment_id']}: 상장사 F6 는 자동 산출이라 수동 판단을 무시함")

    _, rev_obs = obs.number(cid, "revenue_ttm")
    basis = _period_basis(rev_obs)
    tid = track_id_for(company, basis)
    track = rules.f6_track(tid)
    calc: dict[str, Any] = {"mode": "parameters", "track": tid, "track_label": track["label"],
                            "period_basis": basis, "floor": track["floor"], "parameters": {}}

    if basis is None:
        return factor_result(FACTOR, score=None, status="pending_data", basis="computed",
                             observation_ids=obs_ids, calc=calc,
                             pending=pending_info("data", "revenue_ttm 관측에 basis.period_basis 가 없음 — "
                                                          "기간 기준이 선언돼야 트랙이 정해진다"))
    expected = TRACK_EXPECTED_BASIS.get(tid)
    if expected and basis != expected:
        return factor_result(FACTOR, score=None, status="pending_data", basis="computed",
                             observation_ids=obs_ids, calc=calc,
                             pending=pending_info("data", f"트랙 {tid} 은 period_basis {expected!r} 를 기대하는데 "
                                                          f"관측은 {basis!r} — 기준 불일치"))

    subtotal = 0
    missing: list[str] = []
    for pid in track["parameters"]:
        if pid == "P4":
            continue
        value, reason, raw = _parameter_value(pid, cid, obs, rules, obs_ids)
        entry: dict[str, Any] = {"inputs": raw}
        if value is None:
            entry["value"] = None
            entry["reason"] = reason
            missing.append(reason or pid)
        else:
            score, band = rules.f6_parameter_band(pid, value)
            boundary = rules.f6_parameter_boundary_flag(pid, value)
            entry.update({"value": value, "score": score, "band": band, "boundary": boundary})
            subtotal += score
            if boundary["flag"]:
                warnings.append(f"{pid} 경계 ⚠️ {boundary['nearest_boundary']:g} 선까지 "
                                f"{boundary['distance_ratio'] * 100:+.1f}% — 점수는 그대로")
        calc["parameters"][pid] = entry

    if missing:
        return factor_result(FACTOR, score=None, status="pending_data", basis="computed",
                             observation_ids=obs_ids, calc=calc, warnings=warnings,
                             pending=pending_info("data", "; ".join(missing)))

    p4 = _p4(cid, obs, rules, track, warnings)
    calc["p4"] = p4
    calc["subtotal_before_p4"] = subtotal
    total = subtotal - p4["demotion_steps"]
    floor = int(track["floor"])
    if total < floor:
        calc["floor_applied"] = True
        warnings.append(f"트랙 하한 {floor} 로 절단 (보정 전 {total})")
        total = floor
    calc["score"] = total
    if p4["conditions_hit"]:
        warnings.append(f"P4 보정 한 칸 — 조건 {', '.join(p4['conditions_hit'])}")
    return factor_result(FACTOR, score=total, status="ok", basis="computed",
                         observation_ids=obs_ids, calc=calc, warnings=warnings)


def compute_private(company: dict[str, Any], obs: ObsLookup, judgment: dict[str, Any] | None,
                    rules: RuleSet) -> dict[str, Any]:
    """비상장 배수는 자동 계산하되 **밴드가 미정이라 점수를 만들지 않는다.**"""
    cid = company["company_id"]
    track = rules.f6_track("private")
    calc: dict[str, Any] = {"mode": "parameters", "track": "private", "track_label": track["label"],
                            "floor": track["floor"], "multiples": {}}
    obs_ids: list[str] = []
    warnings: list[str] = []
    if judgment is not None:
        warnings.append(f"{judgment['judgment_id']}: 밴드가 정해지기 전에는 정성 점수도 받지 않는다")
    values: dict[str, float | None] = {}
    for metric in ("post_money_valuation", "arr", "arr_prior", "cumulative_raised"):
        value, o = obs.number(cid, metric)
        values[metric] = value
        if o is not None:
            obs_ids.append(o["observation_id"])
            warnings.extend(obs_note(o))
            if metric in ("arr", "arr_prior") and o.get("kind") == "run_rate":
                # 이름은 arr 인데 종류는 run_rate 다. kind 를 안 보면 ARR 로 오독한다(PRIV-ARR-17).
                calc.setdefault("kind_notes", []).append(f"{metric} kind=run_rate — ARR 이 아니라 런레이트")
    calc["inputs"] = values
    if values["post_money_valuation"] is not None and values["arr"]:
        calc["multiples"]["post_money_over_arr"] = values["post_money_valuation"] / values["arr"]
    if values["arr"] is not None and values["arr_prior"]:
        calc["multiples"]["arr_growth"] = values["arr"] / values["arr_prior"] - 1
    if values["arr"] is not None and values["cumulative_raised"]:
        calc["multiples"]["arr_over_cumulative_raised"] = values["arr"] / values["cumulative_raised"]
    calc["note"] = rules.f6.get("private_note")
    return factor_result(FACTOR, score=None, status="needs_rule_decision", basis="computed",
                         observation_ids=obs_ids, calc=calc, warnings=warnings,
                         pending=pending_info("rule", "비상장 F6 밴드 미정 — 배수는 계산해 두고 점수는 만들지 않는다", "C-12"))
