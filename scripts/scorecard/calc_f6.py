# ⑥ 가격 factor 계산: 상장사 NTM PER 구간·경계 표시, 비상장사 배수 계산과 정성 점수 접수
from __future__ import annotations

import re
from typing import Any

from . import calc_f6_params
from .inputs import JudgmentLookup, ObsLookup, carried_note, factor_result, obs_note, pending_info
from .rules import RuleSet, decision_choice

FACTOR = "F6"
QUARTER_RE = re.compile(r"^(\d{4})Q([1-4])$")


def _quarters_problem(quarters: list[str]) -> str | None:
    """4개 분기가 서로 다르고, YYYYQn 형식이면 연속(중복·건너뜀 없음)인지 검사한다 (R01)."""
    if len(set(quarters)) != 4:
        return f"분기 중복 {quarters}"
    parsed = [QUARTER_RE.match(q) for q in quarters]
    if not all(parsed):
        # 식별 불가한 라벨("A"·"Q1" 등)로는 미발표 4개 분기인지 확인할 수 없다. YYYYQn 만 허용한다.
        return f"분기 식별 불가(YYYYQn 형식 필요) {quarters}"
    indices = sorted(int(m.group(1)) * 4 + int(m.group(2)) - 1 for m in parsed if m)
    if any(b - a != 1 for a, b in zip(indices, indices[1:])):
        return f"분기가 연속하지 않음 {quarters}"
    return None


def _basis_alignment(company: dict[str, Any], price_basis: dict[str, Any], eps_basis: dict[str, Any]) -> str | None:
    """주가와 EPS 의 통화·주식 기준이 서로(그리고 기업 레지스트리와) 맞는지 검사한다 (R01)."""
    for key in ("currency", "share_basis"):
        p, e = price_basis.get(key), eps_basis.get(key)
        if p is None or e is None:
            return f"{key} 미기재(price={p!r}, eps={e!r})"
        if p != e:
            return f"{key} 불일치(price={p!r}, eps={e!r})"
    if company.get("share_basis") and price_basis.get("share_basis") != company["share_basis"]:
        return f"share_basis 가 기업 레지스트리({company['share_basis']!r})와 다름"
    return None


REQUIRED_QUARTERS = 4
QUARTER_METRIC = "ntm_eps_quarter"


def _quarter_label(period: dict[str, Any] | None) -> str | None:
    """회계분기 종료일에서 YYYYQn 라벨을 만든다. 종료 월이 분기를 정한다(3·6·9·12 로 맞추지 않는다)."""
    end = (period or {}).get("end")
    if not isinstance(end, str) or len(end) < 7:
        return None
    year, month = int(end[:4]), int(end[5:7])
    return f"{year}Q{(month - 1) // 3 + 1}"


def _quarterly_gates(company: dict[str, Any], rows: list[dict[str, Any]], price_obs: dict[str, Any] | None) -> str | None:
    """4분기 후보를 정식 NTM 으로 올리기 전의 관문. 하나라도 걸리면 사유를 돌려준다."""
    if any(o["status"] != "verified" for o in rows):
        bad = sorted({o["status"] for o in rows if o["status"] != "verified"})
        return f"분기 관측 상태가 verified 가 아님({', '.join(bad)})"
    sources = {o["source_id"] for o in rows}
    if len(sources) != 1:
        # 서로 다른 공급사의 분기를 이어 붙여 검증된 NTM 을 만들지 않는다.
        return f"공급사 혼합 금지 — 분기별 source_id 가 {len(sources)}종({', '.join(sorted(sources))})"
    currencies = {(o.get("basis") or {}).get("currency") for o in rows}
    shares = {(o.get("basis") or {}).get("share_basis") for o in rows}
    if len(currencies) != 1 or None in currencies:
        return f"분기별 통화가 하나로 확정되지 않음({sorted(str(c) for c in currencies)})"
    if len(shares) != 1 or None in shares:
        return f"분기별 주식 기준이 하나로 확정되지 않음({sorted(str(s) for s in shares)})"
    currency, share_basis = currencies.pop(), shares.pop()
    if company.get("share_basis") and share_basis != company["share_basis"]:
        return f"주식 기준 {share_basis!r} 가 기업 레지스트리({company['share_basis']!r})와 다름"
    pb = price_obs.get("basis") or {}
    if pb.get("currency") != currency or pb.get("share_basis") != share_basis:
        return f"주가 기준(currency={pb.get('currency')!r}, share_basis={pb.get('share_basis')!r})과 EPS 기준({currency!r}, {share_basis!r})이 다름"
    accounting = {(o.get("basis") or {}).get("accounting") for o in rows}
    if len(accounting) != 1 or accounting == {None}:
        # GAAP 과 조정치를 섞으면 실적과 추정이 다른 잣대가 된다. 정의가 확인되기 전에는 점수를 만들지 않는다.
        return f"회계 기준(GAAP/비GAAP)이 확정되지 않음({sorted(str(a) for a in accounting)})"
    if company.get("share_basis") in ("adr", "ads") and not all((o.get("basis") or {}).get("basis_verified") for o in rows):
        # ADR/ADS 는 공급사마다 통화·주식 단위가 갈린다. 순이익÷EPS 역산 검산 기록이 있어야 한다.
        return "ADR/ADS 종목은 basis 검산(basis_verified)이 기록된 관측만 채점에 쓴다"
    return None


def _quarterly(company: dict[str, Any], obs: ObsLookup, rules: RuleSet) -> dict[str, Any] | None:
    """분기 EPS 관측이 있으면 이 경로가 F6 를 결정한다. 4분기 미만은 점수를 만들지 않는다."""
    cid = company["company_id"]
    rows = [o for o in obs.all(cid, QUARTER_METRIC) if o["status"] != "not_applicable"]
    if not rows:
        return None
    by_label: dict[str, dict[str, Any]] = {}
    for o in rows:
        label = _quarter_label(o.get("period"))
        if label and o["value"] is not None:
            by_label.setdefault(label, o)
    labels = sorted(by_label)
    obs_ids = [by_label[x]["observation_id"] for x in labels]
    coverage = {"secured": len(labels), "required": REQUIRED_QUARTERS, "quarters": labels,
                "sources": sorted({by_label[x]["source_id"] for x in labels})}
    if len(labels) < REQUIRED_QUARTERS:
        # 부분 확보는 보존하되 합산·배수 근사로 점수를 만들지 않는다 (2Q×2 금지).
        return factor_result(FACTOR, score=None, status="pending_data", basis="computed", observation_ids=obs_ids,
                             calc={"coverage": coverage},
                             pending=pending_info("data", f"NTM EPS {REQUIRED_QUARTERS}개 분기 중 {len(labels)}개 확보 — 나머지 {REQUIRED_QUARTERS - len(labels)}개 필요. 부분 합계를 배수로 늘려 쓰지 않는다"))
    if len(labels) > REQUIRED_QUARTERS:
        return factor_result(FACTOR, score=None, status="pending_data", basis="computed", observation_ids=obs_ids,
                             calc={"coverage": coverage},
                             pending=pending_info("data", f"분기 관측이 {len(labels)}개로 {REQUIRED_QUARTERS}개를 넘음 — 채점 대상 창을 하나로 확정해야 함"))
    problem = _quarters_problem(labels)
    if problem:
        return factor_result(FACTOR, score=None, status="pending_data", basis="computed", observation_ids=obs_ids,
                             calc={"coverage": coverage}, pending=pending_info("data", f"분기 구성 오류: {problem}"))
    price, price_obs = obs.number(cid, "price")
    if price is None or price_obs is None:
        return factor_result(FACTOR, score=None, status="pending_data", basis="computed", observation_ids=obs_ids,
                             calc={"coverage": coverage}, pending=pending_info("data", "주가 관측 없음 — PER 산출 불가"))
    rows4 = [by_label[x] for x in labels]
    gate = _quarterly_gates(company, rows4, price_obs)
    if gate:
        return factor_result(FACTOR, score=None, status="pending_data", basis="computed",
                             observation_ids=obs_ids + [price_obs["observation_id"]], calc={"coverage": coverage},
                             pending=pending_info("data", f"4분기 확보했으나 채점 관문 미통과: {gate}"))
    eps = sum(float(o["value"]) for o in rows4)
    calc: dict[str, Any] = {"coverage": coverage, "ntm_eps": eps, "method": "consensus_4q_sum",
                            "requires_reapproval": True}
    if eps <= 0:
        return factor_result(FACTOR, score=None, status="pending_data", basis="computed",
                             observation_ids=obs_ids + [price_obs["observation_id"]], calc=calc,
                             pending=pending_info("data", "NTM EPS 합이 0 이하 — 낮은 PER·0점으로 대체하지 않음"))
    per = price / eps
    score, band = rules.f6_band(per)
    boundary = rules.f6_boundary_flag(per)
    calc.update({"ntm_per": per, "band": band, "boundary": boundary})
    warnings = [f"분기 컨센서스 {REQUIRED_QUARTERS}개 합산({coverage['sources'][0]}) — 입력이 바뀐 실행이므로 재계산·재검토·재승인을 거쳐야 확정된다"]
    for o in rows4:
        warnings.extend(obs_note(o))
    if boundary["flag"]:
        warnings.append(f"경계 ⚠️ {boundary['nearest_boundary']:g} 선까지 {boundary['distance_ratio'] * 100:+.1f}% — 점수는 그대로")
    return factor_result(FACTOR, score=score, status="ok", basis="computed",
                         observation_ids=obs_ids + [price_obs["observation_id"]], calc=calc, warnings=warnings)


def _listed(company: dict[str, Any], obs: ObsLookup, judgment: dict[str, Any] | None, rules: RuleSet, run: dict[str, Any]) -> dict[str, Any]:
    cid = company["company_id"]
    # 분기 EPS 관측이 있으면 그 경로가 F6 를 결정한다. 없으면 기존 승계 경로를 그대로 쓴다.
    quarterly = _quarterly(company, obs, rules)
    if quarterly is not None:
        return quarterly
    warnings: list[str] = []
    obs_ids: list[str] = []
    if judgment is not None:
        warnings.append(f"{judgment['judgment_id']}: 상장사 F6 는 자동 산출이라 수동 판단을 무시함")

    per_value, per_obs = obs.number(cid, "ntm_per")
    method: str | None = None
    if per_obs is not None:
        obs_ids.append(per_obs["observation_id"])
        method = (per_obs.get("basis") or {}).get("method")
    if per_value is None:
        price, price_obs = obs.number(cid, "price")
        eps, eps_obs = obs.number(cid, "ntm_eps")
        if price is not None and eps is not None and price_obs and eps_obs:
            obs_ids.extend([price_obs["observation_id"], eps_obs["observation_id"]])
            eps_basis = eps_obs.get("basis") or {}
            price_basis = price_obs.get("basis") or {}
            quarters = eps_basis.get("quarters")
            if not isinstance(quarters, list) or len(quarters) != 4:
                return factor_result(FACTOR, score=None, status="pending_data", basis="computed", observation_ids=obs_ids,
                                     pending=pending_info("data", "NTM EPS 는 미발표 4개 분기 컨센서스 합이어야 함(basis.quarters 4개 필요)"))
            problem = _quarters_problem([str(q) for q in quarters])
            if problem:
                return factor_result(FACTOR, score=None, status="pending_data", basis="computed", observation_ids=obs_ids,
                                     pending=pending_info("data", f"NTM EPS 분기 구성 오류: {problem}"))
            alignment = _basis_alignment(company, price_basis, eps_basis)
            if alignment:
                return factor_result(FACTOR, score=None, status="pending_data", basis="computed", observation_ids=obs_ids,
                                     pending=pending_info("data", f"주가·EPS 기준 불일치: {alignment} — 통화·보통주/ADR·분할·회계 기준을 맞춘 뒤 채점"))
            if eps <= 0:
                return factor_result(FACTOR, score=None, status="pending_data", basis="computed", observation_ids=obs_ids,
                                     pending=pending_info("data", "NTM EPS 합이 0 이하 — 낮은 PER·0점으로 대체하지 않음"))
            per_value = price / eps
            method = "consensus_4q_sum"
            warnings.extend(obs_note(price_obs) + obs_note(eps_obs))
        else:
            reason = "NTM PER 관측 없음"
            if per_obs is not None and per_obs["status"] not in ("verified", "legacy_unverified"):
                reason = f"NTM PER 관측 상태 {per_obs['status']}"
            return factor_result(FACTOR, score=None, status="pending_data", basis="computed", observation_ids=obs_ids,
                                 pending=pending_info("data", reason))
    else:
        warnings.extend(obs_note(per_obs))

    policy = rules.f6
    if method is None:
        return factor_result(FACTOR, score=None, status="pending_data", basis="computed", observation_ids=obs_ids,
                             pending=pending_info("data", "NTM PER basis.method 미기재 — forwardPE 필드명만으로 NTM 인정 불가"))
    if method in policy["proxy_methods"]:
        choice = decision_choice(run, rules, "C-13")
        proxy_calc = {"ntm_per": per_value, "method": method}
        if choice == "accept_proxy_with_flag":
            # 승인된 F6 정책: 근사 방법은 정식 점수를 만들지 않는다. 결정은 기록으로 남고 값은 참고로만 보존한다.
            return factor_result(FACTOR, score=None, status="pending_data", basis="computed", observation_ids=obs_ids, calc=proxy_calc,
                                 pending=pending_info("data", "C-13 을 accept_proxy_with_flag 로 두었으나 F6 정책상 근사(annual_weighted_proxy)는 점수를 만들지 않는다 — 미발표 4개 분기 컨센서스(consensus_4q_sum) 필요"))
        elif choice == "reject_proxy":
            # 거절은 확정된 선택이다. 규칙 미결이 아니라 정확한 4분기 컨센서스를 확보해야 하는 자료 대기로 남긴다.
            return factor_result(FACTOR, score=None, status="pending_data", basis="computed", observation_ids=obs_ids, calc=proxy_calc,
                                 pending=pending_info("data", "C-13 결정에 따라 근사 NTM 을 채점에 쓰지 않음 — 미발표 4개 분기 컨센서스(consensus_4q_sum) 관측 필요"))
        else:
            return factor_result(FACTOR, score=None, status="needs_rule_decision", basis="computed", observation_ids=obs_ids, calc=proxy_calc,
                                 pending=pending_info("rule", "NTM PER 이 근사 방법(annual_weighted_proxy)이라 자동 채점 보류", "C-13"))
    elif method not in policy["accepted_ntm_methods"]:
        return factor_result(FACTOR, score=None, status="pending_data", basis="computed", observation_ids=obs_ids,
                             pending=pending_info("data", f"허용되지 않은 NTM 방법 {method!r}"))

    if per_value <= 0:
        return factor_result(FACTOR, score=None, status="pending_data", basis="computed", observation_ids=obs_ids,
                             pending=pending_info("data", "PER 이 0 이하(EPS 합 0 이하) — 자동 채점 보류"))

    score, band = rules.f6_band(per_value)
    boundary = rules.f6_boundary_flag(per_value)
    calc: dict[str, Any] = {"ntm_per": per_value, "method": method, "band": band, "boundary": boundary}
    for ref_metric in ("ttm_per", "nonop_share", "ps_ratio", "market_cap", "price"):
        value, ref_obs = obs.number(cid, ref_metric)
        if ref_obs is not None:
            calc[ref_metric] = value
            calc[f"{ref_metric}_observation_id"] = ref_obs["observation_id"]
    if boundary["flag"]:
        warnings.append(f"경계 ⚠️ {boundary['nearest_boundary']:g} 선까지 {boundary['distance_ratio'] * 100:+.1f}% — 점수는 그대로")
    nonop = calc.get("nonop_share")
    if isinstance(nonop, (int, float)) and nonop >= 0.30:
        warnings.append(f"영업외 비중 {nonop:.0%} — TTM PER 참고 무효(⑥ 점수 개입 없음)")
    return factor_result(FACTOR, score=score, status="ok", basis="computed", observation_ids=obs_ids, calc=calc, warnings=warnings)


def _private(company: dict[str, Any], obs: ObsLookup, judgment: dict[str, Any] | None, rules: RuleSet) -> dict[str, Any]:
    cid = company["company_id"]
    calc: dict[str, Any] = {"listed": False}
    obs_ids: list[str] = []
    warnings: list[str] = []
    val, val_obs = obs.number(cid, "post_money_valuation")
    arr, arr_obs = obs.number(cid, "arr")
    ttm, ttm_obs = obs.number(cid, "ttm_revenue_est")
    raised, raised_obs = obs.number(cid, "cumulative_raised")
    for o in (val_obs, arr_obs, ttm_obs, raised_obs):
        if o is not None:
            obs_ids.append(o["observation_id"])
            warnings.extend(obs_note(o))
    if val is not None and arr:
        calc["valuation_over_arr"] = val / arr
    if val is not None and ttm:
        calc["valuation_over_ttm_revenue"] = val / ttm
        calc["ttm_revenue_is_estimate"] = (ttm_obs or {}).get("kind") == "estimate"
    if arr is not None and raised:
        calc["arr_over_cumulative_raised"] = arr / raised
    calc["note"] = "비상장 배수는 자동 계산, 최종 점수는 정성 예외(C-12). 상장사 PER 구간 재사용 금지, 경계 표시 미적용"
    if judgment is None or judgment["kind"] != "score":
        return factor_result(FACTOR, score=None, status="needs_judgment", basis="manual", observation_ids=obs_ids, calc=calc, warnings=warnings,
                             pending=pending_info("judgment", "비상장 F6 점수·보정 사유·검토자 입력 필요"))
    warnings.append("C-12: 비상장 F6 점수는 정성 예외 — 자료·보정 근거·검토자 확인")
    warnings.extend(carried_note(judgment))
    status = "carried_score" if judgment["status"] == "carried" else "ok"
    return factor_result(FACTOR, score=int(judgment["score"]), status=status, basis="manual", judgment=judgment,
                         observation_ids=obs_ids, calc=calc, warnings=warnings)


def compute_f6(company: dict[str, Any], obs: ObsLookup, judgments: JudgmentLookup, rules: RuleSet, run: dict[str, Any]) -> dict[str, Any]:
    judgment = judgments.get(company["company_id"], FACTOR)
    # v1.7 은 F6 를 네 파라미터로 분해한다. v1.5·v1.6 실행은 아래 per_band 경로를 그대로 쓴다.
    if rules.f6_mode == "parameters":
        if company["listed"]:
            return calc_f6_params.compute_listed(company, obs, judgment, rules, run)
        return calc_f6_params.compute_private(company, obs, judgment, rules)
    if company["listed"]:
        return _listed(company, obs, judgment, rules, run)
    return _private(company, obs, judgment, rules)
