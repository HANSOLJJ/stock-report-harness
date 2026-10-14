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
from .rules import RuleSet, decision_choice, piecewise

FACTOR = "F6"
# 선택 파라미터를 만들지 못한 사유 중 **factor 를 pending 으로 세우지 않는 것**(FIX-61).
# `scope_mismatch` 는 일부러 뺐다 — 소유 범위가 어긋난 것은 자료 결함이라 드러나야 한다(FC-04).
OPTIONAL_CAUSES = {"missing_input", "requires_positive"}

# 트랙마다 기대하는 기간 기준. 관측이 다른 기준을 선언하면 조용히 넘기지 않고 pending 으로 세운다.
TRACK_EXPECTED_BASIS = {
    "listed_ttm": "ttm",
    "listed_annual": "annual",
    "listed_newly": "quarterly_yoy",
}


def _period_basis(o: dict[str, Any] | None) -> str | None:
    return ((o or {}).get("basis") or {}).get("period_basis")


def track_id_for(company: dict[str, Any], period_basis: str | None, *, by_period_basis: bool = False) -> str:
    """2026-10-06 v1.9: 규칙이 `policies.f6.track_by_period_basis` 를 켜면 예탁증서 상장사도 관측 기간으로 가른다.
    키가 없는 v1.5~v1.8 은 예탁증서를 연간 트랙에 고정한다(승인 실행 재계산 불변)."""
    if not company["listed"]:
        return "private"
    if company.get("share_basis") in ("adr", "ads"):
        if by_period_basis and period_basis == "ttm":
            return "listed_ttm"
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
        obs_ids: list[str] | None = None, p1_adjusted: bool = False) -> dict[str, Any]:
    spec = rules.f6_p4()
    declared = {c["id"]: c for c in spec.get("conditions", [])}
    hit: list[str] = []
    detail: dict[str, Any] = {}

    cond = declared.get("nonop_share")
    if cond is not None:
        value, d = _nonop_share(cid, obs, warnings, obs_ids)
        detail.update(d)
        # 2026-10-12 규칙 v2.1: P1 이 평가손익을 세후로 빼 조정했으면 같은 왜곡을 두 번 깎지 않는다. 값은 표시용으로 남긴다.
        if value is not None and cond.get("skip_when_p1_adjusted") and p1_adjusted:
            detail["nonop_share_skipped"] = "P1 이 지분증권 평가손익을 세후로 빼 조정했다 — 이 조건을 보지 않는다"
            value = None
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
            raw["not_computed_cause"] = "missing_input"
            return None, f"{pid} 입력 {metric} 관측 없음", raw
        # 2026-09-15 FIX-54 1단계 FC-04: tsmc 는 연결 전체 순이익, alibaba 는 모회사 귀속분이라 같은 P1 의 분자 범위가 달랐다.
        # 규칙이 범위를 정하면 verified 관측은 basis.ownership_scope 로 그 범위를 밝혀야 한다. 다르면 값을 만들지 않는다.
        want = (spec.get("input_scope") or {}).get(metric)
        if want and o is not None and o.get("status") == "verified" and (o.get("basis") or {}).get("ownership_scope") != want:
            # 2026-09-17 FIX-61: **이 사유는 선택 파라미터로도 넘기지 않는다.** 범위가 어긋난 것은 자료 결함이라
            # 조용히 빠지면 FC-04 가 세운 가드가 무력해진다 — 예전처럼 factor 를 pending 으로 세운다.
            raw["not_computed_cause"] = "scope_mismatch"
            return None, (f"{pid} 입력 {metric} 의 소유 범위 {(o.get('basis') or {}).get('ownership_scope')!r} 가 규칙 {want!r} 와 다름 "
                          f"— {o['observation_id']}"), raw
    for metric in spec.get("requires_positive", []):
        if raw[metric] <= 0:
            # 2026-09-17 FIX-61: 이 사유만 **선택 파라미터 경로**로 보낸다. 관측 없음·소유 범위 불일치는
            # 자료 결함이라 조용히 넘기면 안 된다 — 사유를 기계가 읽게 raw 에 원인을 적는다.
            raw["not_computed_cause"] = "requires_positive"
            return None, f"{pid} 입력 {metric} 이 0 이하({raw[metric]!r}) — 대체값으로 채우지 않음", raw
    if pid == "P1":
        if "growth_adjusted" in spec:
            # 2026-10-12 규칙 v2.1: 성장 조정 PER 은 이익 조정·이익 부호·성장 문턱을 거쳐 점수가 정해진다. 입력만 모아 넘긴다.
            return None, None, {**raw, "growth_adjusted": True}
        return raw["market_cap"] / raw["net_income_ttm"], None, raw
    if pid == "P2":
        return (raw["market_cap"] - raw["net_cash"]) / raw["revenue_ttm"], None, raw
    if pid == "P3":
        return raw["revenue_ttm"] / raw["revenue_ttm_prior"] - 1, None, raw
    return None, f"{pid} 산식이 구현되지 않음", raw


def _adjusted_net_income(cid: str, net_income: float, spec: dict[str, Any] | None, obs: ObsLookup,
                         obs_ids: list[str], warnings: list[str]) -> tuple[float, dict[str, Any]]:
    """2026-10-12 규칙 v2.1 ⑥: 지분증권 평가·처분 손익을 세후로 뺀 모회사 귀속 순이익. (쓸 순이익, 상세)를 돌려준다.

    실효세율은 **공시 법인세 ÷ 연결 세전이익**이다. 세전 − 모회사 귀속 순이익으로 유도하지 않는다 — 비지배주주 몫이 법인세에
    섞인다(외부 검토 3차). 조정할 수 없으면 보고 순이익을 그대로 쓰고 P4 영업외 비중 조건이 살아 있게 `applied: False` 로 둔다.
    """
    detail: dict[str, Any] = {"applied": False, "net_income_reported": net_income}
    if not spec:
        detail["reason"] = "규칙에 이익 조정이 없음"
        return net_income, detail
    gains, g_obs = obs.number(cid, spec["gains_metric"])
    if g_obs is None or gains is None:
        detail["reason"] = f"{spec['gains_metric']} 관측 없음 — 보고 순이익을 쓴다"
        return net_income, detail
    obs_ids.append(g_obs["observation_id"])
    detail["gains"] = gains
    components = ((g_obs.get("basis") or {}).get("components") or [])
    tags = [c.get("tag") if isinstance(c, dict) else c for c in components]
    if len(tags) != len(set(tags)):
        detail["reason"] = f"평가손익 구성 태그가 겹친다 {tags} — 조정하지 않는다"
        warnings.append(f"이익 조정 불가 ⚠️ {detail['reason']}")
        return net_income, detail
    pretax, p_obs = obs.number(cid, spec["pretax_metric"])
    tax, t_obs = obs.number(cid, spec["tax_metric"])
    for o in (p_obs, t_obs):
        if o is not None:
            obs_ids.append(o["observation_id"])
    if pretax is None or tax is None:
        missing = [m for m, v in ((spec["pretax_metric"], pretax), (spec["tax_metric"], tax)) if v is None]
        detail["reason"] = f"{', '.join(missing)} 관측 없음 — 실효세율을 만들 수 없어 조정하지 않는다"
        warnings.append(f"이익 조정 불가 ⚠️ {detail['reason']}")
        return net_income, detail
    scopes = {((o or {}).get("basis") or {}).get("ownership_scope") for o in (p_obs, t_obs)} - {None}
    if len(scopes) > 1:
        detail["reason"] = f"세전이익·법인세 관측의 소유 범위가 다름 {sorted(scopes)} — 조정하지 않는다"
        warnings.append(f"이익 조정 불가 ⚠️ {detail['reason']}")
        return net_income, detail
    detail.update({"pretax": pretax, "tax": tax})
    if pretax <= 0:
        detail["reason"] = f"세전이익 {pretax:,.0f} 이 0 이하 — 실효세율이 서지 않아 조정하지 않는다"
        warnings.append(f"이익 조정 불가 ⚠️ {detail['reason']}")
        return net_income, detail
    rate = tax / pretax
    lo, hi = spec["effective_tax_rate_range"]
    detail["effective_tax_rate"] = rate
    if not (lo <= rate <= hi):
        detail["reason"] = f"실효세율 {rate:.3f} 이 {lo:g}~{hi:g} 밖 — 조정하지 않는다"
        warnings.append(f"이익 조정 불가 ⚠️ {detail['reason']}")
        return net_income, detail
    adjusted = net_income - gains * (1 - rate)
    detail.update({"applied": True, "net_income_adjusted": adjusted, "formula": spec.get("formula"),
                   "assumption": spec.get("assumption_note")})
    return adjusted, detail


def _growth_adjusted_p1(cid: str, raw: dict[str, Any], spec: dict[str, Any], obs: ObsLookup, rules: RuleSet,
                        obs_ids: list[str], warnings: list[str]) -> dict[str, Any]:
    """2026-10-12 규칙 v2.1 ⑥ P1: (시가총액 ÷ 조정 순이익) ÷ (매출 성장률 × 100). 결과 항목(점수 포함)을 돌려준다.

    조정 순이익이 0 이하면 −3, 성장이 문턱(5%) 미만이면 −3 이다. 이익이 0 으로 다가가면 PER 이 끝없이 커져 −3 이 되므로
    0 이하도 −3 으로 이어 붙인다 — 이익이 나빠져서 ⑥ 이 좋아지는 일이 없다(외부 검토 2차의 단조성 요구).
    """
    ga = spec["growth_adjusted"]
    inputs = {k: v for k, v in raw.items() if k != "growth_adjusted"}
    growth = raw["revenue_ttm"] / raw["revenue_ttm_prior"] - 1
    net_income, adj = _adjusted_net_income(cid, raw["net_income_ttm"], spec.get("earnings_adjustment"), obs, obs_ids, warnings)
    entry: dict[str, Any] = {"inputs": inputs, "revenue_growth": growth, "earnings_adjustment": adj,
                             "net_income_used": net_income,
                             "per_reported": (raw["market_cap"] / raw["net_income_ttm"]) if raw["net_income_ttm"] > 0 else None}
    if net_income <= 0:
        score = int(ga["nonpositive_earnings_score"])
        entry.update({"value": None, "score": score, "band": "이익 0 이하",
                      "why": f"조정 순이익 {net_income:,.0f} 이 0 이하 — PER 이 서지 않아 가장 나쁜 칸 {score}"})
        return entry
    per = raw["market_cap"] / net_income
    entry["per_used"] = per
    floor = float(ga["growth_floor"])
    if growth < floor:
        score = int(ga["below_floor_score"])
        entry.update({"value": None, "score": score, "band": f"성장 {floor * 100:g}% 미만",
                      "why": f"매출 성장 {growth * 100:.1f}% 가 문턱 {floor * 100:g}% 미만 — 성장으로 정당화할 수 없어 {score}"})
        return entry
    value = per / (growth * float(ga["growth_multiplier"]))
    # 2026-10-14 규칙 v3.0: 파라미터에 curve 가 있으면 연속값이다. 없으면 지금 구간표 그대로.
    score, band = rules.f6_parameter_score("P1", value)
    boundary = rules.f6_parameter_boundary_flag("P1", value)
    entry.update({"value": value, "score": score, "band": band, "boundary": boundary})
    if boundary["flag"]:
        warnings.append(f"P1 경계 ⚠️ {boundary['nearest_boundary']:g} 선까지 {boundary['distance_ratio'] * 100:+.1f}% — 점수는 그대로")
    return entry


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
    tid = track_id_for(company, basis,
                       by_period_basis=bool(rules.payload["policies"]["f6"].get("track_by_period_basis")))
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
    # 2026-09-16 FIX-58 1단계(7차 리뷰 C): 규칙의 `optional_parameters` 만 읽어 run.json 의 C-24 선택을 감지하지 못했다.
    # 실행이 `p3_only_v17` 을 고르면 선택 파라미터를 만들지 않는다 — 선언에 소비자가 없는 형태(C-11 계열)를 없앤다.
    # 2026-09-17 FIX-61(9차 재판정 S2): 선택 파라미터가 세 트랙으로 넓어졌다. **C-24 는 신규 상장 트랙의 P2 만
    # 가리키는 결정**이므로 그 범위 밖(예: listed_ttm 의 P1)까지 끄지 않도록 트랙·파라미터를 함께 본다.
    optional_pids = set(track.get("optional_parameters") or [])
    c24 = decision_choice(run, rules, "C-24")
    if tid == "listed_newly" and "P2" in optional_pids:
        if c24 == "p3_only_v17":
            calc["c24_choice"] = {"choice": c24, "effect": "선택 파라미터 P2 를 만들지 않는다", "suppressed": ["P2"]}
            optional_pids.discard("P2")
        else:
            calc["c24_choice"] = {"choice": c24 or "compute_p2_when_inputs_exist(규칙 기본)",
                                  "effect": "입력이 성립하면 선택 파라미터를 만든다", "optional": ["P2"]}
    p1_adjusted = False
    for pid in track["parameters"]:
        if pid == "P4":
            continue
        value, reason, raw = _parameter_value(pid, cid, obs, rules, obs_ids, unverified)
        if raw.get("growth_adjusted") and reason is None:
            # 2026-10-12 규칙 v2.1: 성장 조정 PER 은 이익이 0 이하이거나 성장이 문턱 미만이어도 점수(−3)를 낸다.
            entry = _growth_adjusted_p1(cid, raw, rules.f6_parameters()[pid], obs, rules, obs_ids, warnings)
            # 2026-10-14 규칙 v3.0: 연속값이면 끝수가 있다. 구간표 규칙에서는 점수가 이미 정수라 결과가 같다.
            subtotal += entry["score"]
            p1_adjusted = bool(entry["earnings_adjustment"].get("applied"))
            calc["parameters"][pid] = entry
            continue
        # 선택 파라미터라도 **모든 사유를 넘기지는 않는다.** 입력이 없는 것(missing_input)과 그 기업의 성질인
        # 순손실(requires_positive)은 넘기지만, **소유 범위 불일치는 자료 결함**이라 예전처럼 factor 를 pending 으로
        # 세운다(FC-04 가드). 사유를 문자열로 재지 않고 _parameter_value 가 적은 원인을 읽는다.
        cause = raw.get("not_computed_cause")
        # 트랙이 사유를 좁힐 수 있다 — `listed_ttm` 의 P1 은 순손실일 때만 넘긴다. 순이익 관측이 아예 없는 것은
        # 수집 공백이라 예전처럼 pending 이다. 선언이 없으면 scope_mismatch 를 뺀 둘 다 허용한다(FIX-56 그대로).
        allowed = set((track.get("optional_parameters_causes") or {}).get(pid) or OPTIONAL_CAUSES)
        if value is None and pid in optional_pids and cause in allowed:
            calc.setdefault("parameters_optional_unmet", {})[pid] = {"inputs": raw, "why": reason, "cause": cause}
            continue
        entry: dict[str, Any] = {"inputs": raw}
        if value is None:
            entry["value"] = None
            entry["reason"] = reason
            missing.append(reason or pid)
        else:
            score, band = rules.f6_parameter_score(pid, value)
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
    absorbed = track.get("parameters_absorbed") or {}
    for pid in rules.f6_parameters():
        if pid in track["parameters"]:
            continue
        if pid in absorbed:
            # 2026-10-12 규칙 v2.1: 다른 파라미터에 흡수돼 쓰지 않는 것이다. "트랙 정의를 다시 볼 자리" 로 읽히지 않게 사유를 그대로 적는다.
            excluded[pid] = {"absorbed": True, "why": absorbed[pid]}
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

    p4 = _p4(cid, obs, rules, track, warnings, rev_obs=rev_obs, period_basis=basis, run=run, obs_ids=obs_ids,
             p1_adjusted=p1_adjusted)
    calc["p4"] = p4
    calc["subtotal_before_p4"] = subtotal
    total = subtotal - p4["demotion_steps"]
    floor = int(track["floor"])
    if total < floor:
        calc["floor_applied"] = True
        warnings.append(f"트랙 하한 {floor} 로 절단 (보정 전 {total})")
        total = floor
    total = rules.round_score(total)
    calc["score"] = total
    if p4["conditions_hit"]:
        warnings.append(f"P4 보정 한 칸 — 조건 {', '.join(p4['conditions_hit'])}")
    return factor_result(FACTOR, score=total, status="ok", basis="computed",
                         observation_ids=obs_ids, calc=calc, warnings=warnings)


C12_IMPLEMENTED_CHOICE = "p2_with_capped_promotion"
# 2026-10-12 규칙 v2.1: 비상장 ⑥ 을 P/S ÷ 보정 매출 성장률로 잰다. 승격 보정은 없다.
C12_GROWTH_ADJUSTED_CHOICE = "growth_adjusted_ps"


def _upper_band(bands: list[dict[str, Any]], value: float) -> tuple[int, str]:
    lower = 0.0
    for band in bands:
        upper = band["upper"]
        if upper is None or value < upper:
            return int(band["score"]), (f"{lower:g}~{upper:g}" if upper is not None else f"{lower:g}+")
        lower = float(upper)
    raise ValueError("bands 가 구간을 덮지 못함")


def _pga_score(pga: dict[str, Any], value: float) -> tuple[int | float, str]:
    """2026-10-14 규칙 v3.0: 성장 조정 P/S 에 curve 가 있으면 연속값, 없으면 지금 구간표."""
    curve = pga.get("curve")
    if curve is None:
        return _upper_band(pga["bands"], value)
    return piecewise(curve, value), f"연속값 {value:.4g}"


# 2026-10-14 규칙 v3.0: 배수가 범위 추정이면 연속값에서는 양 끝 점수가 거의 늘 갈린다. 어느 끝을 쓸지는 규칙
# `policies.f6.estimate_range_end` 가 정한다(rules.md ⑥ 비상장, 8절 미결). 정하지 않았으면 값을 고르지 않는다.
RANGE_END_LABELS = {"low": "낮은 끝 배수", "high": "높은 끝 배수", "mid": "양 끝의 가운데"}


def _range_end_score(f6: dict[str, Any], lo_score: float, hi_score: float) -> tuple[float | None, str | None]:
    end = f6.get("estimate_range_end")
    if end == "low":
        return lo_score, RANGE_END_LABELS[end]
    if end == "high":
        return hi_score, RANGE_END_LABELS[end]
    if end == "mid":
        return (lo_score + hi_score) / 2, RANGE_END_LABELS[end]
    return None, None


RANGE_END_PENDING = "어느 끝을 쓸지 규칙(policies.f6.estimate_range_end)이 정하지 않았다 — 값을 고르지 않는다(rules.md 8절 미결)"


def _private_growth_adjusted(cid: str, pga: dict[str, Any], multiple: float, rng: Any, p2_entry: dict[str, Any],
                             obs: ObsLookup, track: dict[str, Any], calc: dict[str, Any], obs_ids: list[str],
                             warnings: list[str], bands_spec: dict[str, Any], rules: RuleSet) -> dict[str, Any]:
    """2026-10-12 규칙 v2.1 비상장 ⑥: P/S ÷ (보정 매출 성장률 × 100). 상장 P1 과 같은 질문(성장에 비해 비싼가)을 매출 배수로 묻는다.

    보정 매출이나 전년 보정 매출 관측이 없으면 P/S 구간표(private_bands)로 점수를 낸다. 보정 매출이 0 이하면 성장률이 서지
    않아 자료 대기다. 성장이 문턱(5%) 미만이면(0·음수 포함) 가장 나쁜 칸이다 — 음수 성장이 가장 유리한 구간에 들어가지 않게.
    ARR·런레이트는 쓰지 않는다(상장사와 같은 잣대).
    """
    rev_metric, prior_metric = pga["growth_inputs"]
    rev, r_obs = obs.number(cid, rev_metric)
    prior, p_obs = obs.number(cid, prior_metric)
    for o in (r_obs, p_obs):
        if o is not None:
            obs_ids.append(o["observation_id"])
    detail: dict[str, Any] = {"label": pga.get("label"), "inputs": {rev_metric: rev, prior_metric: prior}}
    calc["growth_adjusted"] = detail
    floor, ceiling = int(track["floor"]), track.get("ceiling")
    if rev is None or prior is None:
        detail["path"] = "fallback_private_bands"
        detail["why"] = f"{rev_metric if rev is None else prior_metric} 관측 없음 — P/S 구간표로 점수를 낸다(승격 보정 없음)"
        warnings.append(f"비상장 성장 조정 불가 — {detail['why']}")
        if (p2_entry.get("estimate_range") or {}).get("spans_bands"):
            if bands_spec.get("curve") is not None:
                return factor_result(FACTOR, score=None, status="needs_rule_decision", basis="computed",
                                     observation_ids=obs_ids, calc=calc, warnings=warnings,
                                     pending=pending_info("rule", f"P2 범위 추정 {rng[0]}~{rng[1]} 의 양 끝 점수가 다르다 — {RANGE_END_PENDING}"))
            return factor_result(FACTOR, score=None, status="pending_data", basis="computed",
                                 observation_ids=obs_ids, calc=calc, warnings=warnings,
                                 pending=pending_info("data", f"P2 구간 추정 {rng[0]}~{rng[1]} 이 P/S 구간표 밴드를 가른다 — 값을 고르지 않는다"))
        # 2026-10-14 규칙 v3.0: 연속값이면 끝수가 있다. 구간표 규칙에서는 이미 정수다.
        score = p2_entry["score"]
    elif rev <= 0 or prior <= 0:
        detail["path"] = "pending"
        return factor_result(FACTOR, score=None, status="pending_data", basis="computed",
                             observation_ids=obs_ids, calc=calc, warnings=warnings,
                             pending=pending_info("data", f"보정 매출 {rev!r}·전년 {prior!r} 가 0 이하 — 성장률이 서지 않는다"))
    else:
        growth = rev / prior - 1
        detail["revenue_growth"] = growth
        g_floor = float(pga["growth_floor"])
        if growth < g_floor:
            detail["path"] = "below_growth_floor"
            score = int(pga["below_floor_score"])
            detail["why"] = f"보정 매출 성장 {growth * 100:.1f}% 가 문턱 {g_floor * 100:g}% 미만 — 가장 나쁜 칸 {score}"
        else:
            mult = float(pga["growth_multiplier"])
            value = multiple / (growth * mult)
            score, label = _pga_score(pga, value)
            detail.update({"path": "growth_adjusted", "value": value, "band": label})
            if isinstance(rng, (list, tuple)) and len(rng) == 2:
                lo_v, hi_v = float(rng[0]) / (growth * mult), float(rng[1]) / (growth * mult)
                lo_s, lo_l = _pga_score(pga, lo_v)
                hi_s, hi_l = _pga_score(pga, hi_v)
                detail["estimate_range"] = {"low": lo_v, "high": hi_v, "low_band": lo_l, "high_band": hi_l,
                                            "spans_bands": lo_s != hi_s}
                if lo_s != hi_s and pga.get("curve") is not None:
                    picked, how = _range_end_score(rules.f6, lo_s, hi_s)
                    detail["estimate_range"].update({"low_score": lo_s, "high_score": hi_s})
                    if picked is None:
                        return factor_result(FACTOR, score=None, status="needs_rule_decision", basis="computed",
                                             observation_ids=obs_ids, calc=calc, warnings=warnings,
                                             pending=pending_info("rule", f"P/S 범위 추정 {rng[0]}~{rng[1]} 을 성장으로 나눈 값의 양 끝 점수가 "
                                                                          f"{lo_s:.2f} 대 {hi_s:.2f} — {RANGE_END_PENDING}"))
                    score = picked
                    detail["estimate_range"].update({"spans_bands": False, "picked": how})
                elif lo_s != hi_s:
                    return factor_result(FACTOR, score=None, status="pending_data", basis="computed",
                                         observation_ids=obs_ids, calc=calc, warnings=warnings,
                                         pending=pending_info("data", f"P/S 구간 추정 {rng[0]}~{rng[1]} 을 성장으로 나눈 값이 밴드를 가른다"
                                                                      f"({lo_l} 대 {hi_l}) — 값을 고르지 않는다"))
    calc["subtotal_before_correction"] = score
    total = score
    if ceiling is not None and total > int(ceiling):
        calc["ceiling_applied"] = True
        warnings.append(f"비상장 천장 {ceiling} 로 절단 ({total}) — 비상장에는 0·-1 칸이 없다")
        total = int(ceiling)
    if total < floor:
        calc["floor_applied"] = True
        total = floor
    total = rules.round_score(total)
    calc["score"] = total
    calc["boundary_rule"] = bands_spec.get("boundary_rule")
    return factor_result(FACTOR, score=total, status="ok", basis="computed",
                         observation_ids=obs_ids, calc=calc, warnings=warnings)


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
    # 2026-10-12 규칙 v2.1: 성장 조정 P/S 를 선언한 규칙에서는 그 선택만 구현돼 있다. 승격 보정 경로는 v2.0 이하를 재현하는 데만 쓴다.
    pga = rules.f6.get("private_growth_adjusted")
    implemented = C12_GROWTH_ADJUSTED_CHOICE if pga else C12_IMPLEMENTED_CHOICE
    if choice != implemented:
        return factor_result(FACTOR, score=None, status="needs_rule_decision", basis="computed",
                             observation_ids=obs_ids, calc=calc, warnings=warnings,
                             pending=pending_info("rule", f"C-12 선택 {choice!r} 는 구현된 경로가 없다 — 규칙 {rules.version} 에서 "
                                                          f"구현된 선택은 {implemented} 하나", "C-12"))

    # ---------------- P2 — 점수를 내는 파라미터
    multiple = values["ps_ratio"]
    p2_obs = obs_by_metric["ps_ratio"]
    if multiple is None:
        calc["parameters"]["P2"] = {"value": None, "reason": "P2 입력 ps_ratio 관측 없음"}
        return factor_result(FACTOR, score=None, status="pending_data", basis="computed",
                             observation_ids=obs_ids, calc=calc, warnings=warnings,
                             pending=pending_info("data", "비상장 P2 입력 ps_ratio(밸류÷TTM 보정 매출) 관측 없음 — "
                                                          "arr 로 대체하지 않는다"))
    # 2026-10-14 규칙 v3.0: 비상장 구간표에 curve 가 있으면 연속값이다. 없으면 지금 구간표 그대로.
    score, label = rules.f6_private_score(multiple)
    entry: dict[str, Any] = {"value": multiple, "score": score, "band": label,
                             "input": "ps_ratio", "formula": spec.get("input")}
    # 구간 추정이면 양 끝이 같은 밴드에 드는지 본다. 갈리면 값을 고르지 않는다.
    rng = ((p2_obs or {}).get("basis") or {}).get("estimate_range")
    if isinstance(rng, (list, tuple)) and len(rng) == 2:
        lo_score, lo_label = rules.f6_private_score(float(rng[0]))
        hi_score, hi_label = rules.f6_private_score(float(rng[1]))
        entry["estimate_range"] = {"low": rng[0], "high": rng[1],
                                   "low_band": lo_label, "high_band": hi_label,
                                   "spans_bands": lo_score != hi_score}
        if lo_score != hi_score and spec.get("curve") is not None:
            picked, how = _range_end_score(rules.f6, lo_score, hi_score)
            entry["estimate_range"].update({"low_score": lo_score, "high_score": hi_score})
            if picked is not None:
                entry["score"] = score = picked
                entry["estimate_range"].update({"spans_bands": False, "picked": how})
            elif not pga:
                calc["parameters"]["P2"] = entry
                return factor_result(FACTOR, score=None, status="needs_rule_decision", basis="computed",
                                     observation_ids=obs_ids, calc=calc, warnings=warnings,
                                     pending=pending_info("rule", f"P2 범위 추정 {rng[0]}~{rng[1]} 의 양 끝 점수가 다르다 — {RANGE_END_PENDING}"))
        # 2026-10-12 규칙 v2.1: 성장 조정 경로는 자기 밴드에서 구간을 다시 본다. 여기서는 P/S 구간표 경로만 멈춘다.
        if lo_score != hi_score and not pga and spec.get("curve") is None:
            calc["parameters"]["P2"] = entry
            return factor_result(FACTOR, score=None, status="pending_data", basis="computed",
                                 observation_ids=obs_ids, calc=calc, warnings=warnings,
                                 pending=pending_info("data", f"P2 구간 추정 {rng[0]}~{rng[1]} 이 밴드를 가른다"
                                                              f"({lo_label} 대 {hi_label}) — 값을 고르지 않는다"))
        if lo_score == hi_score:
            entry["range_note"] = f"구간 추정 {rng[0]}~{rng[1]} 의 양 끝이 모두 {lo_label} 라 판정이 갈리지 않는다"
    calc["parameters"]["P2"] = entry

    if pga:
        return _private_growth_adjusted(cid, pga, multiple, rng, entry, obs, track, calc, obs_ids, warnings, spec, rules)

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
    total = rules.round_score(total)
    calc["score"] = total
    if detail["promotion_steps"]:
        warnings.append(f"비상장 보정 한 칸 — 조건 {', '.join(met)} 충족")
    calc["boundary_rule"] = spec.get("boundary_rule")
    return factor_result(FACTOR, score=total, status="ok", basis="computed",
                         observation_ids=obs_ids, calc=calc, warnings=warnings)
