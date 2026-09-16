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

from datetime import date
from typing import Any

from .inputs import ObsLookup, factor_result, obs_note, pending_info
from .rules import RuleSet, decision_choice

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


def _nonop_share(cid: str, obs: ObsLookup, warnings: list[str],
                 obs_ids: list[str] | None = None) -> tuple[float | None, dict[str, Any]]:
    """영업외 비중 = **영업외손익 ÷ 세전이익** = `(세전 − 영업이익) / 세전`.

    원자료에서 재계산한다. 완제품 `nonop_share` 관측은 대조용으로만 쓴다.

    ## 산식이 두 군데 틀려 있었다 (NONOP-44 에서 정정)

        정정 전  (순이익 − 영업이익) / 순이익
        정정 후  (세전이익 − 영업이익) / 세전이익

    1. **분자에 법인세가 섞여 있었다.** `순이익 − 영업이익` 은 영업외손익에서 세금을 뺀 값이라
       영업외 항목이 없는 흑자 납세 기업은 늘 음수가 된다. **12개사 중 여섯의 부호가 뒤집혀 있었다.**
    2. **분모가 세전이익이 아니라 순이익이었다.** 크기만 바꾸지만 정의와 어긋난다.

    **저장값이 옳고 재계산이 틀렸다.** 보존 companyfacts 로 역산해 11개사 중 9개가 저장값과
    맞는 것을 확인했다(±0.02). 안 맞는 둘은 alibaba·oracle 이고 규칙에 사유와 함께 적어 두었다.
    """
    detail: dict[str, Any] = {}
    oi, oi_obs = obs.number(cid, "operating_income_ttm")
    pretax, pretax_obs = obs.number(cid, "pretax_income_ttm")
    ni, ni_obs = obs.number(cid, "net_income_ttm")
    stored, stored_obs = obs.number(cid, "nonop_share")
    if stored_obs is not None:
        detail["nonop_share_stored"] = stored
    # 2026-09-16 FIX-56 1단계(5차 리뷰 B): 이 조건이 alphabet·amazon 을 혼자 한 칸 끌어내리는데 입력 관측 id 가
    # F6 observation_ids 에 없었다. **점수를 만드는 입력은 감사 경로에 남아야 한다** — 관측이 교체되면 무엇을
    # 다시 계산해야 하는지 결과만 보고 알 수 있어야 한다.
    if obs_ids is not None:
        detail["nonop_share_observation_ids"] = [o["observation_id"] for o in (pretax_obs, oi_obs, ni_obs, stored_obs) if o is not None]
        obs_ids.extend(detail["nonop_share_observation_ids"])
    if pretax is not None and oi is not None and pretax < 0:
        # 2026-09-15 FIX-53 3단계: 전에는 경고만 붙이고 값을 돌려줘 P4 조건이 걸릴 수 있었다. 적자 기업은 분모가
        # 음수라 **부호 규약이 정의되지 않으므로 산출하지 않는다.** spacex-xai 세전이익을 등록하며 드러났다.
        detail["nonop_share"] = None
        detail["nonop_share_source"] = "incompatible_basis"
        detail["nonop_share_missing"] = f"세전이익 {pretax:,.0f} 이 음수 — 부호 규약이 서지 않아 산출하지 않는다"
        detail["nonop_share_inputs"] = {"pretax_income_ttm": pretax, "operating_income_ttm": oi, "net_income_ttm": ni}
        warnings.append(f"nonop_share 산출 안 함 ⚠️ {detail['nonop_share_missing']}")
        return None, detail
    if pretax is not None and oi is not None and pretax != 0:
        value = (pretax - oi) / pretax
        detail["nonop_share"] = value
        detail["nonop_share_source"] = "recomputed"
        detail["nonop_share_formula"] = "(pretax_income_ttm - operating_income_ttm) / pretax_income_ttm"
        detail["nonop_share_inputs"] = {"pretax_income_ttm": pretax, "operating_income_ttm": oi,
                                        "net_income_ttm": ni}
        if stored is not None and abs(stored - value) > 0.02:
            warnings.append(f"nonop_share 재계산 {value:.4f} 과 저장값 {stored:.4f} 이 다름 — "
                            "산식은 정정됐고 이 둘은 남은 불일치다(policies.f6.p4 nonop_share)")
        return value, detail
    # 세전이익이 없으면 **값을 만들지 않는다.** 옛 산식으로 되돌아가지 않는다 — 틀린 값이기 때문이다.
    detail["nonop_share"] = None
    detail["nonop_share_source"] = "unavailable"
    detail["nonop_share_missing"] = ("pretax_income_ttm 관측 없음" if pretax is None else
                                     "operating_income_ttm 관측 없음" if oi is None else "세전이익 0")
    if stored is not None:
        warnings.append(f"nonop_share 산출 불가 ⚠️ {detail['nonop_share_missing']} — 저장값 "
                        f"{stored:.4f} 이 있으나 **쓰지 않는다**. 저장값은 완제품이라 검증되지 않는다")
    return None, detail


def _months_elapsed(end: str, as_of: str) -> int:
    """**완결된 개월 수**다. 달 번호 차로 세면 한 달 더 나온다(2024-12-31→2026-09-02 은 20 이지 21 이 아니다)."""
    e, a = date.fromisoformat(end), date.fromisoformat(as_of)
    months = (a.year - e.year) * 12 + (a.month - e.month)
    return months - (1 if a.day < e.day else 0)


def _stale_asof(rev_obs: dict[str, Any] | None, period_basis: str | None, rules: RuleSet,
                run: dict[str, Any] | None) -> dict[str, Any]:
    """기준 시점 경과. **임계는 보고 주기에 상대적이다**(ttm·quarterly 6개월, annual 16개월).

    이 조건은 v1.7 에 선언돼 있었으나 읽는 코드가 없었다 — 임계값도 없었다. 그래서 F6-REG-28 직전까지
    TSM 이 20개월 묵어 있는 동안 한 번도 걸리지 않았다(F6-REG-28 에서 보고). 여기가 그 소비자다.
    """
    out: dict[str, Any] = {"checked": False}
    limit = rules.f6_stale_months(period_basis)
    as_of = (run or {}).get("as_of")
    if limit is None or not as_of or rev_obs is None:
        out["reason"] = ("임계 선언 없음" if limit is None else
                         "run.as_of 없음" if not as_of else "매출 관측 없음")
        return out
    end = ((rev_obs.get("period") or {}).get("end")) or rev_obs.get("as_of")
    if not end:
        out["reason"] = "창 종료일을 알 수 없음"
        return out
    months = _months_elapsed(end, as_of)
    out.update({"checked": True, "period_end": end, "as_of": as_of, "months_elapsed": months,
                "limit_months": limit, "period_basis": period_basis, "hit": months > limit})
    return out


def _p4(cid: str, obs: ObsLookup, rules: RuleSet, track: dict[str, Any],
        warnings: list[str], rev_obs: dict[str, Any] | None = None,
        period_basis: str | None = None, run: dict[str, Any] | None = None,
        obs_ids: list[str] | None = None) -> dict[str, Any]:
    spec = rules.f6_p4()
    declared = {c["id"]: c for c in spec.get("conditions", [])}
    hit: list[str] = []
    detail: dict[str, Any] = {}

    cond = declared.get("nonop_share")
    if cond is not None:
        value, d = _nonop_share(cid, obs, warnings, obs_ids)
        detail.update(d)
        if value is not None:
            threshold = float(cond.get("threshold", 0.30))
            # **P4 임계에도 경계를 표시한다.** P1·P2·P3 에만 있고 여기만 없었다. 비교 대상은
            # 부호가 아니라 크기(`abs`)라 경계도 크기로 잰다. 점수는 건드리지 않는다.
            boundary = rules.f6_threshold_boundary_flag(abs(value), threshold)
            detail["nonop_share_boundary"] = boundary
            if abs(value) >= threshold:
                hit.append("nonop_share")
            if boundary["flag"]:
                warnings.append(
                    f"P4 경계 ⚠️ nonop_share |{value:.4f}| 이 임계 {threshold:g} 에서 "
                    f"{boundary['distance_ratio'] * 100:+.1f}% — 점수는 그대로")

    if "stale_asof" in declared:
        stale = _stale_asof(rev_obs, period_basis, rules, run)
        detail["stale_asof"] = stale
        if stale.get("hit"):
            hit.append("stale_asof")
            warnings.append(f"기준 시점 경과 ⚠️ 창 종료 {stale['period_end']} 이 기준일 {stale['as_of']} "
                            f"로부터 {stale['months_elapsed']}개월 — {period_basis} 임계 {stale['limit_months']}개월 초과")

    # 2026-09-16 FIX-55 1단계(4차 리뷰 B): 규칙은 이 조건을 "관측 basis.period_basis 로 판정한다" 고 선언하는데
    # 트랙의 auto 목록으로만 붙고 있었다. 그래서 listed_newly 인 spacex-xai 는 관측이 스스로 quarterly_yoy 라고
    # 적는데도 빠졌다. 선언대로 **관측에서** 판정한다 — 트랙이 아니라 자료가 정한다.
    if "period_basis_not_ttm" in declared:
        detail["period_basis"] = period_basis
        if period_basis is not None and period_basis != "ttm":
            hit.append("period_basis_not_ttm")

    # 트랙이 구조적으로 지는 조건(이력 부족 등)은 규칙이 선언한 대로 자동 적용한다.
    for auto in track.get("auto_p4_conditions", []):
        if auto in declared and auto not in hit:
            hit.append(auto)

    detail["conditions_hit"] = hit
    detail["demotion_steps"] = int(spec.get("cap_steps", 1)) if hit else 0
    # **한 조건만 걸렸으면 그 조건이 강등을 혼자 정한 것이다.** 경계 표시가 실제로 점수를
    # 가르는 자리인지 여기서 갈린다 — 조건이 둘이면 하나가 빠져도 강등은 그대로다.
    detail["demotion_sole_cause"] = hit[0] if len(hit) == 1 else None
    return detail


def _excluded_reason(pid: str, cid: str, obs: ObsLookup, rules: RuleSet) -> dict[str, Any]:
    """트랙에 없는 파라미터가 **자료로도 성립하지 않는지** 확인해 사유를 남긴다(FIX-56 1단계).

    트랙에서 빼는 것과 입력이 없어서 못 만드는 것은 다르다. 둘을 갈라 적지 않으면 다음 사람이
    "트랙만 고치면 계산된다" 고 읽는다 — spacex-xai 의 P2 가 실제로 그런 경우였다.
    """
    spec = rules.f6_parameters()[pid]
    inputs: dict[str, Any] = {}
    for metric in spec["inputs"]:
        value, _o = obs.number(cid, metric)
        for alt in (spec.get("input_alternatives") or {}).get(metric, []):
            if value is None:
                value, _o = obs.number(cid, alt)
        inputs[metric] = value
    missing = [m for m, v in inputs.items() if v is None]
    if missing:
        return {"inputs": inputs, "would_compute": False, "why": f"입력 관측 없음 — {', '.join(missing)}"}
    nonpositive = [m for m in spec.get("requires_positive", []) if inputs[m] is not None and inputs[m] <= 0]
    if nonpositive:
        return {"inputs": inputs, "would_compute": False,
                "why": f"{', '.join(nonpositive)} 이 0 이하 — requires_positive 를 넘지 못한다(대체값으로 채우지 않음)"}
    return {"inputs": inputs, "would_compute": True,
            "why": "입력은 성립한다. 트랙이 이 파라미터를 쓰지 않는다 — 트랙 정의를 다시 볼 자리다"}


def _parameter_value(pid: str, cid: str, obs: ObsLookup, rules: RuleSet,
                     obs_ids: list[str],
                     unverified: dict[str, list[str]] | None = None
                     ) -> tuple[float | None, str | None, dict[str, Any]]:
    """(값, 미산출 사유, 입력 상세). **입력이 없으면 값을 만들지 않는다.**

    입력 중 `legacy_unverified` 가 있으면 `unverified` 에 모은다. **점수는 바꾸지 않는다** —
    자료를 우리가 아직 못 구한 것이지 그 기업의 성질이 아니기 때문이다(MISS-LABEL-23 원칙).
    다만 **그 사실이 산출물에 보여야** 한다. 지금 market_cap 12건이 전부 legacy 이고
    P1·P2 가 그 위에 서는데 결과 어디에도 안 나타나던 상태를 고친다(SCOPE-34 검토, 설계진행).
    """
    spec = rules.f6_parameters()[pid]
    raw: dict[str, Any] = {}
    used_alternatives: dict[str, str] = {}
    for metric in spec["inputs"]:
        value, o = obs.number(cid, metric)
        # 2026-09-16 FIX-56 1단계: 신규 상장사의 `revenue_ttm` 은 P3 의 전년 동기 대조를 세우려고 **분기값**으로 등록된다.
        # P2 는 12개월 매출이 필요하므로 규칙이 선언한 대체 지표를 먼저 본다. 없으면 원래 지표를 그대로 쓴다.
        for alt in (spec.get("input_alternatives") or {}).get(metric, []):
            alt_value, alt_obs = obs.number(cid, alt)
            if alt_value is not None:
                value, o = alt_value, alt_obs
                used_alternatives[metric] = alt
                break
        if o is not None:
            obs_ids.append(o["observation_id"])
            if unverified is not None and o.get("status") == "legacy_unverified":
                unverified.setdefault(metric, []).append(pid)
        raw[metric] = value
        if used_alternatives.get(metric):
            raw.setdefault("input_alternatives_used", {})[metric] = {"metric": used_alternatives[metric],
                                                                     "observation_id": (o or {}).get("observation_id")}
        if value is None:
            return None, f"{pid} 입력 {metric} 관측 없음", raw
        # 2026-09-15 FIX-54 1단계 FC-04: tsmc 는 연결 전체 순이익, alibaba 는 모회사 귀속분이라 같은 P1 의 분자 범위가 달랐다.
        # 규칙이 범위를 정하면 verified 관측은 basis.ownership_scope 로 그 범위를 밝혀야 한다. 다르면 값을 만들지 않는다.
        want = (spec.get("input_scope") or {}).get(metric)
        if want and o is not None and o.get("status") == "verified" and (o.get("basis") or {}).get("ownership_scope") != want:
            return None, (f"{pid} 입력 {metric} 의 소유 범위 {(o.get('basis') or {}).get('ownership_scope')!r} 가 규칙 {want!r} 와 다름 "
                          f"— {o['observation_id']}"), raw
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


# net_cash 처럼 **여러 관측을 합쳐 만드는 입력**은 구성요소 하나가 없으면 통째로 막힌다.
# 그 사실이 결과에 안 나타나면 다음 사람은 "왜 아직 legacy 인가" 를 처음부터 다시 조사한다.
# 구성요소 관측에 붙인 `missing_type` 을 여기서 읽어 올려 준다(NETCASH-37).
NET_CASH_COMPONENTS = ("lease_liabilities",)
MISSING_TYPE_LABEL = {
    "unverified": "아직 실측하지 못함",
    "not_disclosed_confirmed": "확인된 미공시 — 발행사가 그 시점에 공시하지 않는다",
    "not_applicable": "해당 없음",
    "indeterminate": "미공시인지 수집 실패인지 가리지 못함",
}


def _blocked_reasons(cid: str, obs: ObsLookup, rules: RuleSet,
                     metrics: list[str]) -> dict[str, Any]:
    """미검증 입력마다 **구성요소 쪽에 남긴 결측 라벨**을 찾아 붙인다. 점수는 건드리지 않는다."""
    out: dict[str, Any] = {}
    if "net_cash" not in metrics:
        return out
    blockers = []
    for metric in NET_CASH_COMPONENTS:
        o = obs.get(cid, metric)
        mtype = (o or {}).get("missing_type")
        if o is not None and o.get("value") is None and mtype:
            blockers.append({"metric": metric, "missing_type": mtype,
                             "label": MISSING_TYPE_LABEL.get(mtype, mtype),
                             "observation_id": o["observation_id"],
                             "note": o.get("note")})
    if blockers:
        out["net_cash"] = {
            "reason": "; ".join(f"{b['metric']} = {b['label']}" for b in blockers),
            "components": blockers,
            "definition_ref": "policies.f6.net_cash",
        }
    return out


def compute_listed(company: dict[str, Any], obs: ObsLookup, judgment: dict[str, Any] | None,
                   rules: RuleSet, run: dict[str, Any] | None = None) -> dict[str, Any]:
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
    unverified: dict[str, list[str]] = {}
    # 2026-09-16 FIX-56 1단계: 트랙이 쓰되 **입력이 있을 때만** 만드는 파라미터다. 입력이 없으면 지금까지처럼
    # 만들지 않고, 그 사실을 미산출로 적는다 — 없다고 F6 전체를 pending 으로 세우지 않는다.
    optional_pids = set(track.get("optional_parameters") or [])
    for pid in track["parameters"]:
        if pid == "P4":
            continue
        value, reason, raw = _parameter_value(pid, cid, obs, rules, obs_ids, unverified)
        if value is None and pid in optional_pids:
            calc.setdefault("parameters_optional_unmet", {})[pid] = {"inputs": raw, "why": reason}
            continue
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
        # P2 의 net_cash 는 **정의가 확정되지 않은 입력**이다. 값만 남기면 다음 사람이 어느 정의로
        # 뺀 순현금인지 알 수 없고, 설계 지침 6.4 의 '사용 가능한 현금' 을 여기로 옮겨 오기 쉽다.
        # 그래서 산식 옆에 정의와 상태를 같이 찍는다(NETCASH-37).
        if pid == "P2":
            spec = rules.f6_net_cash()
            if spec:
                entry["net_cash_definition"] = {
                    "status": spec.get("status"),
                    "definition": spec.get("definition"),
                    "provenance": (spec.get("provenance") or {}).get("kind"),
                }
                if spec.get("status") == "working_definition":
                    warnings.append("net_cash 작업 정의 ⚠️ legacy 역산으로 세운 정의 위에서 P2 를 계산한다 — "
                                    "확정 정의가 나오면 재계산 대상 (policies.f6.net_cash)")
        calc["parameters"][pid] = entry

    # 2026-09-16 FIX-56 1단계: 트랙이 쓰지 않는 파라미터는 **왜 빠졌는지**를 결과가 말해야 한다.
    # spacex-xai 는 P1 이 빠지는데(순이익 음수) 그 사실이 calc 어디에도 없어 "트랙이 그래서" 로만 읽혔다.
    excluded = {}
    for pid in rules.f6_parameters():
        if pid in track["parameters"]:
            continue
        excluded[pid] = _excluded_reason(pid, cid, obs, rules)
    if excluded:
        calc["parameters_not_in_track"] = excluded

    # 미검증 입력을 드러낸다. **점수에는 개입하지 않는다** — 우리 수집 공백을 기업 위험으로 바꾸지 않는다.
    if unverified:
        calc["unverified_inputs"] = {m: sorted(set(p)) for m, p in sorted(unverified.items())}
        blocked = _blocked_reasons(cid, obs, rules, sorted(unverified))
        if blocked:
            calc["unverified_blocked_by"] = blocked
        calc["unverified_inputs_note"] = (
            "이 파라미터들은 status=legacy_unverified 관측 위에 서 있다. **점수를 깎지 않는다** — "
            "자료를 아직 실측하지 못한 것이지 그 기업의 성질이 아니다. 실측으로 교체되면 이 표시가 사라진다.")
        for metric, pids in sorted(unverified.items()):
            why = (calc.get("unverified_blocked_by") or {}).get(metric)
            tail = f" — 실측이 막힌 이유: {why['reason']}" if why else " — 점수는 그대로"
            warnings.append(f"미검증 입력 ⚠️ {metric} 이 legacy_unverified 인데 "
                            f"{', '.join(sorted(set(pids)))} 가 그 위에 선다{tail}")

    if missing:
        return factor_result(FACTOR, score=None, status="pending_data", basis="computed",
                             observation_ids=obs_ids, calc=calc, warnings=warnings,
                             pending=pending_info("data", "; ".join(missing)))

    p4 = _p4(cid, obs, rules, track, warnings, rev_obs=rev_obs, period_basis=basis, run=run, obs_ids=obs_ids)
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


C12_IMPLEMENTED_CHOICE = "p2_with_capped_promotion"


def compute_private(company: dict[str, Any], obs: ObsLookup, judgment: dict[str, Any] | None,
                    rules: RuleSet, run: dict[str, Any]) -> dict[str, Any]:
    """비상장 F6 — **P2 가 점수를 내고 P3·P4 가 합쳐서 최대 한 칸 올린다** (C-12, 2026-09-11 확정).

    상장 P4 와 같은 장치이고 방향만 반대다. 밴드는 `private_bands`(v1.5 구간표), 보정은
    `private_correction` 에 선언돼 있고 **조건 둘이 다 성립해야** 한 칸이다 — 하나만으로 올리면
    성장률이 더 높고 자본효율이 나쁜 쪽이 보상받는다.

    분모는 `arr` 이 아니라 **TTM 보정 매출**이다. ARR 은 런레이트라 TTM 보다 과대하고, 보정 없이
    쓰면 비상장사가 부당하게 싸 보인다(v1.5 645~647행). 그래서 `ps_ratio` 를 읽는다.
    """
    cid = company["company_id"]
    track = rules.f6_track("private")
    spec = rules.f6_private_bands()
    calc: dict[str, Any] = {"mode": "parameters", "track": "private", "track_label": track["label"],
                            "floor": track["floor"], "ceiling": track.get("ceiling"),
                            "multiples": {}, "parameters": {}}
    obs_ids: list[str] = []
    warnings: list[str] = []
    if judgment is not None:
        warnings.append(f"{judgment['judgment_id']}: 비상장 F6 도 자동 산출이라 수동 판단을 무시함")

    values: dict[str, float | None] = {}
    obs_by_metric: dict[str, dict[str, Any] | None] = {}
    for metric in ("post_money_valuation", "arr", "arr_prior", "cumulative_raised", "ps_ratio"):
        value, o = obs.number(cid, metric)
        values[metric] = value
        obs_by_metric[metric] = o
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

    if not spec.get("bands"):
        return factor_result(FACTOR, score=None, status="needs_rule_decision", basis="computed",
                             observation_ids=obs_ids, calc=calc, warnings=warnings,
                             pending=pending_info("rule", "비상장 F6 밴드 미정 — 배수는 계산해 두고 점수는 만들지 않는다", "C-12"))
    # 2026-09-15 FIX-52: 결과의 decisions_applied 에 C-12 가 찍히는데 이 함수가 run 을 받지 않아 선택을 읽지 않았다.
    # 구현된 경로는 p2_with_capped_promotion 하나다. 다른 선택이거나 선택이 없으면 기본값으로 채우지 않는다.
    choice = decision_choice(run, rules, "C-12")
    calc["c12_choice"] = choice
    if choice != C12_IMPLEMENTED_CHOICE:
        return factor_result(FACTOR, score=None, status="needs_rule_decision", basis="computed",
                             observation_ids=obs_ids, calc=calc, warnings=warnings,
                             pending=pending_info("rule", f"C-12 선택 {choice!r} 는 구현된 경로가 없다 — 구현된 선택은 "
                                                          f"{C12_IMPLEMENTED_CHOICE} 하나", "C-12"))

    # ---------------- P2 — 점수를 내는 파라미터
    multiple = values["ps_ratio"]
    p2_obs = obs_by_metric["ps_ratio"]
    if multiple is None:
        calc["parameters"]["P2"] = {"value": None, "reason": "P2 입력 ps_ratio 관측 없음"}
        return factor_result(FACTOR, score=None, status="pending_data", basis="computed",
                             observation_ids=obs_ids, calc=calc, warnings=warnings,
                             pending=pending_info("data", "비상장 P2 입력 ps_ratio(밸류÷TTM 보정 매출) 관측 없음 — "
                                                          "arr 로 대체하지 않는다"))
    score, label = rules.f6_private_band(multiple)
    entry: dict[str, Any] = {"value": multiple, "score": score, "band": label,
                             "input": "ps_ratio", "formula": spec.get("input")}
    # 구간 추정이면 양 끝이 같은 밴드에 드는지 본다. 갈리면 값을 고르지 않는다.
    rng = ((p2_obs or {}).get("basis") or {}).get("estimate_range")
    if isinstance(rng, (list, tuple)) and len(rng) == 2:
        lo_score, lo_label = rules.f6_private_band(float(rng[0]))
        hi_score, hi_label = rules.f6_private_band(float(rng[1]))
        entry["estimate_range"] = {"low": rng[0], "high": rng[1],
                                   "low_band": lo_label, "high_band": hi_label,
                                   "spans_bands": lo_score != hi_score}
        if lo_score != hi_score:
            calc["parameters"]["P2"] = entry
            return factor_result(FACTOR, score=None, status="pending_data", basis="computed",
                                 observation_ids=obs_ids, calc=calc, warnings=warnings,
                                 pending=pending_info("data", f"P2 구간 추정 {rng[0]}~{rng[1]} 이 밴드를 가른다"
                                                              f"({lo_label} 대 {hi_label}) — 값을 고르지 않는다"))
        entry["range_note"] = f"구간 추정 {rng[0]}~{rng[1]} 의 양 끝이 모두 {lo_label} 라 판정이 갈리지 않는다"
    calc["parameters"]["P2"] = entry

    # ---------------- P3·P4 — 합쳐서 상한 1칸 보정
    corr = rules.f6_private_correction()
    detail: dict[str, Any] = {"mode": corr.get("mode"), "cap_steps": int(corr.get("cap_steps", 1)),
                              "require_all": bool(corr.get("require_all")), "conditions": {}}
    met: list[str] = []
    missing: list[str] = []
    for cond in corr.get("conditions", []):
        inputs = {m: values.get(m) for m in cond.get("inputs", [])}
        row: dict[str, Any] = {"formula": cond.get("formula"), "inputs": inputs,
                               "threshold": cond.get("threshold")}
        names = cond.get("inputs", [])
        if any(inputs.get(m) is None for m in names) or not inputs.get(names[-1]):
            row.update({"value": None, "met": None, "reason": "입력 관측 없음"})
            missing.append(cond["id"])
        else:
            value = inputs[names[0]] / inputs[names[1]] - (1 if cond["id"] == "arr_growth" else 0)
            row["value"] = value
            row["met"] = value >= float(cond["threshold"])
            # 2026-09-15 FIX-52 S2: 조건이 받는 관측 종류를 선언했으면 읽는다. 런레이트를 ARR 로 쓰면 성장률이
            # 과대해질 수 있어 사용자가 **진짜 ARR 만 인정**하기로 했다. 값은 표시용으로 남기고 조건은 불충족이다.
            accepted = cond.get("accepted_kinds")
            if accepted:
                kinds = {m: (obs_by_metric.get(m) or {}).get("kind") for m in names}
                rejected = {m: k for m, k in kinds.items() if k not in accepted}
                row["accepted_kinds"] = list(accepted)
                row["input_kinds"] = kinds
                if rejected:
                    row["met"] = False
                    row["value_met_threshold"] = value >= float(cond["threshold"])
                    row["reason"] = (f"입력 kind 불인정 — {', '.join(f'{m}={k}' for m, k in rejected.items())}. "
                                     f"이 조건은 kind {accepted} 만 받는다(런레이트는 ARR 이 아니다)")
            if row["met"]:
                met.append(cond["id"])
        detail["conditions"][cond["id"]] = row
    declared = [c["id"] for c in corr.get("conditions", [])]
    if detail["require_all"]:
        applied = bool(declared) and len(met) == len(declared)
    else:
        applied = bool(met)
    detail.update({"conditions_met": met, "conditions_missing": missing,
                   "promotion_steps": detail["cap_steps"] if applied else 0})
    if missing:
        warnings.append(f"비상장 보정 입력 부족 — {', '.join(missing)} 관측 없음. 보정을 적용하지 않는다")
    calc["correction"] = detail
    calc["subtotal_before_correction"] = score

    total = score + detail["promotion_steps"]
    floor, ceiling = int(track["floor"]), track.get("ceiling")
    if ceiling is not None and total > int(ceiling):
        calc["ceiling_applied"] = True
        warnings.append(f"비상장 천장 {ceiling} 로 절단 (보정 후 {total}) — 비상장에는 0·-1 칸이 없다")
        total = int(ceiling)
    if total < floor:
        calc["floor_applied"] = True
        total = floor
    calc["score"] = total
    if detail["promotion_steps"]:
        warnings.append(f"비상장 보정 한 칸 — 조건 {', '.join(met)} 충족")
    calc["boundary_rule"] = spec.get("boundary_rule")
    return factor_result(FACTOR, score=total, status="ok", basis="computed",
                         observation_ids=obs_ids, calc=calc, warnings=warnings)
