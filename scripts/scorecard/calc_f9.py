# ⑨ 적자 깊이 factor 계산: G1 본업 → G2 현금 → G3 런웨이 → G4 약정 커버리지 게이트를 정책 파라미터와 결정 오버라이드로 적용
from __future__ import annotations

from typing import Any

from .inputs import JudgmentLookup, ObsLookup, factor_result, obs_note, pending_info
from .rules import RuleSet, decision_choice
from .schema import MISSING_TYPE_FOR_DISCLOSURE_POLICY

FACTOR = "F9"
UNKNOWN_INPUTS = {
    "fcf_trend": "unknown",
    "bep_retreat": "unknown",
    "buffer_erosion": "unknown",
    "direction_A": "unknown",
    "direction_B": "unknown",
    "coverage_comparable": "unknown",
}


def _pending_status(pending: dict[str, Any] | None) -> str:
    """G4 등에서 올라온 pending 의 kind 로 factor 상태를 정한다: data → pending_data, judgment → needs_judgment, rule → needs_rule_decision."""
    kind = (pending or {}).get("kind")
    return {"data": "pending_data", "judgment": "needs_judgment"}.get(kind, "needs_rule_decision")


def _clamp(score: int, floor: int) -> int:
    return max(floor, score)


def _g1_loss_band(margin: float, rules: RuleSet) -> int:
    for band in rules.f9["g1_bands_proposed"]:
        lower = band["min_margin"]
        if lower is None or margin >= lower:
            return int(band["score"])
    return int(rules.f9["floor"])


def _runway(cash: float, undrawn: float, burn: float) -> float:
    return (cash + undrawn) / burn


def _runway_step(runway: float, rules: RuleSet) -> int:
    if runway >= float(rules.f9["g3_runway_keep_years"]):
        return 0
    if runway >= float(rules.f9["g3_runway_one_step_years"]):
        return -1
    return -2


def compute_f9(company: dict[str, Any], obs: ObsLookup, judgments: JudgmentLookup, rules: RuleSet, run: dict[str, Any]) -> dict[str, Any]:
    cid = company["company_id"]
    pol = rules.f9
    floor = int(pol["floor"])
    judgment = judgments.get(cid, FACTOR)
    gi = dict(UNKNOWN_INPUTS)
    if judgment is not None:
        gi.update(judgment["inputs"])
    path: list[dict[str, Any]] = []
    warnings: list[str] = []
    obs_ids: list[str] = []

    def use(o: dict[str, Any] | None) -> None:
        if o is not None:
            obs_ids.append(o["observation_id"])
            warnings.extend(obs_note(o))

    def done(score: int | None, status: str, pending: dict[str, Any] | None = None, extra: dict[str, Any] | None = None) -> dict[str, Any]:
        calc = {"path": path, "inputs": gi}
        if extra:
            calc.update(extra)
        return factor_result(FACTOR, score=score, status=status, basis="computed", judgment=judgment,
                             observation_ids=obs_ids, calc=calc, warnings=warnings, pending=pending)

    # ------------------------------------------------------------------ G1 본업이 버는가
    margin, margin_obs = obs.number(cid, "operating_margin_ttm")
    use(margin_obs)
    if margin is None:
        op_income, op_obs = obs.number(cid, "operating_income_ttm")
        revenue, rev_obs = obs.number(cid, "revenue_ttm")
        use(op_obs)
        use(rev_obs)
        if op_income is not None and revenue is not None:
            if revenue <= 0:
                return done(None, "pending_data", pending_info("data", "TTM 매출 0 이하 — 손실률 산식 무효"))
            margin = op_income / revenue
    bep_retreat = gi["bep_retreat"] == "yes"
    reviewed_sign = gi.get("operating_result_reviewed", "unknown")
    if margin is None and not bep_retreat:
        if reviewed_sign == "profit":
            # 손실률 수치는 없지만 검토된 TTM 영업흑자 부호만으로 G1 통과. 수치 확보 전까지 경고를 남긴다.
            path.append({"gate": "G1", "result": "pass", "operating_margin_ttm": None, "basis": "operating_result_reviewed=profit"})
            warnings.append("G1: TTM 영업손익 수치 없이 검토된 부호(profit)로 통과 — TTM 수치 확보 권고")
        elif _private_undisclosed_operating(company, obs, rules, run):
            # C-20. **통과가 아니라 판정 보류다.** 단일 분기 영업흑자를 G1 통과 근거로 쓰지 않되,
            # 비상장이고 구조적으로 미공시면 영구 보류로 두지도 않고 G2 비상장 조항으로 보낸다.
            path.append({"gate": "G1", "result": "undetermined",
                         "reason": "비상장이라 TTM 영업손익이 구조적 미공시 — 판정 보류(통과 아님). "
                                   "단일 분기 영업흑자를 통과 근거로 쓰지 않는다",
                         "route": "G2 비상장 경로", "decision_id": "C-20"})
            warnings.append("C-20: G1 판정 보류 후 비상장 경로 — 통과로 읽지 않는다")
        else:
            path.append({"gate": "G1", "result": "pending", "reason": "TTM 영업손익·손실률 관측 없음(단일 분기·조정 손익으로 대체하지 않음, C-20)"})
            return done(None, "pending_data", pending_info("data", "TTM 영업손익 관측 필요(손실이면 손실률 수치 필요)"))

    if margin is not None and margin == 0 and not bep_retreat:
        path.append({"gate": "G1", "result": "zero", "reason": "영업손익 0 처리 미결(C-06)"})
        return done(None, "needs_rule_decision", pending_info("rule", "영업손익 0 의 처리 규칙 미확정(FCF 0 과 동일)", "C-06"))
    # 판정 보류(C-20)는 통과가 아니다. 다만 G1 실패 경로로도 보내지 않고 아래 G2 로 흘려보낸다.
    g1_deferred = any(p.get("gate") == "G1" and p.get("result") == "undetermined" for p in path)
    g1_pass = (not bep_retreat) and (margin is None or margin > 0)
    if g1_pass and not g1_deferred:
        if margin is not None:
            path.append({"gate": "G1", "result": "pass", "operating_margin_ttm": margin})
    elif g1_deferred:
        pass                                    # 이미 경로 기록을 남겼다. G2 로 내려간다
    else:
        # 영업적자 구간
        if bep_retreat:
            base = int(pol["g1_bep_retreat_score"])
            path.append({"gate": "G1", "result": "fail", "operating_margin_ttm": margin, "band": "BEP 후퇴 → -5", "score": base})
            warnings.append("C-06: BEP 후퇴 -5 는 원문 OR 조건을 적용(우선순위 명문화는 결정 대기)")
        else:
            choice = decision_choice(run, rules, "C-06")
            if choice != "proposed_v15_boundaries":
                path.append({"gate": "G1", "result": "fail", "operating_margin_ttm": margin, "band": "미결(C-06)"})
                return done(None, "needs_rule_decision", pending_info("rule", "영업손실률 구간 경계(-10%·-30%)가 미확정이라 G1 점수 보류", "C-06"))
            base = _g1_loss_band(float(margin), rules)
            path.append({"gate": "G1", "result": "fail", "operating_margin_ttm": margin, "band": "proposed_v15_boundaries", "score": base})
            warnings.append("C-06: 손실률 경계는 제안값(proposed)을 실행 단위 결정으로 적용")
        if gi["buffer_erosion"] == "yes":
            base = min(base, int(pol["g1_buffer_erosion_min_score"]))
            path.append({"gate": "G1", "adjust": "완충 잠식 → 최소 -4", "score": base})
        if gi["direction_A"] == "pass" and gi["direction_B"] == "pass":
            relieved = min(base + int(pol["g1_direction_relief_step"]), int(pol["g1_direction_relief_cap"]))
            path.append({"gate": "G1", "adjust": "방향 완화 A·B 충족 → 한 단계(상한 -3)", "score": relieved})
            base = relieved
        elif "unknown" in (gi["direction_A"], gi["direction_B"]):
            path.append({"gate": "G1", "adjust": "방향 완화 판정 불가 → 유지"})
        score = _clamp(base, floor)
        if score <= floor:
            # 이미 하한이면 G3·G4 를 적용하든 진단만 하든 결과가 같다 — C-05 결정을 요구하지 않는다.
            path.append({"gate": "G3/G4", "result": "skipped", "reason": "G1 점수가 이미 하한(-5)이라 추가 감점 불가"})
            return done(score, "ok", extra={"gate1_fail": True})
        # G3·G4 진단 (C-05: 추가 감점 여부 미결)
        diag_score = score
        fcf, fcf_obs = obs.number(cid, "fcf_ttm")
        use(fcf_obs)
        cash, cash_obs = obs.number(cid, "cash")
        use(cash_obs)
        undrawn, undrawn_obs = obs.number(cid, "undrawn_credit")
        use(undrawn_obs)
        if fcf is None or (fcf < 0 and cash is None):
            # 소진율(TTM FCF)이나 완충(현금) 관측이 없으면 런웨이 진단이 불가능하다. 조용히 건너뛰지 않는다.
            missing = "TTM FCF 관측 " + ((fcf_obs["status"] if fcf_obs else "없음") if fcf is None else "확보") + " / 현금 관측 " + ("없음" if cash is None else "확보")
            path.append({"gate": "G3", "mode": "diagnostic", "result": "pending", "reason": missing})
            if decision_choice(run, rules, "C-05") != "diagnose_only":
                return done(None, "pending_data", pending_info("data", f"G1 실패 뒤 런웨이 진단 자료 부족 — {missing}"))
        elif fcf is not None and fcf < 0 and cash is not None:
            runway = _runway(cash, undrawn or 0.0, -fcf)
            step = _runway_step(runway, rules)
            diag_score = _clamp(diag_score + step, floor)
            path.append({"gate": "G3", "mode": "diagnostic", "runway_years": runway, "step": step})
        g4 = _g4(cid, obs, gi, rules, run, use)
        path.append({"gate": "G4", "mode": "diagnostic", **{k: v for k, v in g4.items() if k != "step"}})
        if g4["step"] is None:
            g4_pending = g4.get("pending")
        else:
            g4_pending = None
            diag_score = _clamp(diag_score + g4["step"], floor)
        choice = decision_choice(run, rules, "C-05")
        if choice == "apply":
            if g4_pending:
                return done(None, _pending_status(g4_pending), g4_pending)
            score = diag_score
            path.append({"gate": "G1-after", "applied": True, "score": score})
        elif choice == "diagnose_only":
            # 명시된 결정: G1 점수를 확정하고 G3·G4 는 진단 기록만 남긴다 (R03).
            path.append({"gate": "G1-after", "applied": False, "policy": "diagnose_only (C-05 실행 결정)", "diagnostic_score": diag_score if not g4_pending else None})
        elif g4_pending and g4_pending.get("kind") != "rule":
            # 진단 자체가 자료·판단 대기라면 C-05 이전에 그 대기를 먼저 드러낸다.
            return done(None, _pending_status(g4_pending), g4_pending)
        elif diag_score != score or g4_pending:
            return done(None, "needs_rule_decision", pending_info("rule", "G1 실패 뒤 G3·G4 를 추가 감점할지(apply) 진단만 할지(diagnose_only) 미결이며 결과가 달라짐", "C-05"))
        return done(score, "ok", extra={"gate1_fail": True})

    # ------------------------------------------------------------------ G2 현금이 새는가
    fcf, fcf_obs = obs.number(cid, "fcf_ttm")
    use(fcf_obs)
    if fcf is None:
        # 확인된 비공개와 미수집(관측 없음·collection_failed·미확인)을 구분한다 (R04).
        # G4 와 같은 라벨을 읽는다 — status 는 네 뜻을 담고 있어 "우리가 안 찾은 것"을 비공개로 둔갑시킨다 (MISS-LABEL-23).
        if (not company["listed"] and fcf_obs is not None
                and fcf_obs.get("missing_type") == MISSING_TYPE_FOR_DISCLOSURE_POLICY):
            score = int(pol["g2_private_not_disclosed"])
            reason_id = gi.get("fcf_not_disclosed_reason") or f"{cid}.fcf_not_disclosed"
            path.append({"gate": "G2", "result": "not_disclosed", "score": score, "reason_id": reason_id,
                         "note": "비상장 FCF 미공시 + 완충이 외부 조달뿐 → 보수적으로 -2"})
            path.append({"gate": "G3", "result": "skipped", "reason": "FCF 미공시라 소진율 없음"})
            g4 = _g4(cid, obs, gi, rules, run, use)
            if g4["step"] is None:
                path.append({"gate": "G4", "result": "undetermined", "dedupe": reason_id,
                             "note": "같은 미공시 사유를 G2·G4 에서 두 번 세지 않음", **{k: v for k, v in g4.items() if k not in ("step", "pending")}})
            else:
                path.append({"gate": "G4", **{k: v for k, v in g4.items() if k != "pending"}})
                score = _clamp(score + g4["step"], floor)
            return done(score, "ok")
        mtype_text = (fcf_obs or {}).get("missing_type") or ((fcf_obs["status"] if fcf_obs else "없음") + "/결측유형 미분류")
        path.append({"gate": "G2", "result": "pending", "reason": f"TTM FCF 관측 {mtype_text}"})
        hint = (f"비상장이면 확인된 비공개는 missing_type={MISSING_TYPE_FOR_DISCLOSURE_POLICY} 로 기록"
                if not company["listed"] else "상장사 TTM FCF 관측 필요")
        return done(None, "pending_data", pending_info("data", f"TTM FCF 관측 {mtype_text} — 미수집과 확인된 비공개를 구분한다. {hint}"))
    if fcf > 0:
        trend = gi["fcf_trend"]
        if trend == "stable":
            path.append({"gate": "G2", "result": "positive_stable", "fcf_ttm": fcf, "score": 0})
            return done(int(pol["g2_fcf_positive_stable"]), "ok")
        if trend == "deteriorating":
            path.append({"gate": "G2", "result": "positive_deteriorating", "fcf_ttm": fcf, "score": -1})
            return done(int(pol["g2_fcf_positive_deteriorating"]), "ok")
        path.append({"gate": "G2", "result": "pending", "fcf_ttm": fcf, "reason": "추세 안정/악화 판정 입력 필요"})
        return done(None, "needs_judgment", pending_info("judgment", "TTM FCF 흑자 — 추세(stable/deteriorating) 검토 입력 필요"))
    if fcf == 0:
        path.append({"gate": "G2", "result": "zero", "reason": "FCF 0 처리 미결(C-06)"})
        return done(None, "needs_rule_decision", pending_info("rule", "FCF 0 의 처리 규칙 미확정", "C-06"))
    score = int(pol["g2_fcf_negative"])
    path.append({"gate": "G2", "result": "negative", "fcf_ttm": fcf, "score": score})

    # ------------------------------------------------------------------ G3 얼마나 버티는가
    cash, cash_obs = obs.number(cid, "cash")
    use(cash_obs)
    if cash is None:
        path.append({"gate": "G3", "result": "pending", "reason": "현금 관측 없음"})
        return done(None, "pending_data", pending_info("data", "사용 가능 현금 관측 필요(런웨이)"))
    undrawn, undrawn_obs = obs.number(cid, "undrawn_credit")
    use(undrawn_obs)
    capacity_choice = decision_choice(run, rules, "C-04") or str(pol["g3_rating_capacity"])
    if capacity_choice == "include_v15":
        warnings.append("C-04: include_v15 선택 — 등급 기반 조달 여력은 숫자 관측(undrawn_credit)으로만 산입되며 추정치는 넣지 않음")
    else:
        warnings.append("C-04: 완충은 현금+확정 미인출 여신만(등급 기반 조달 여력 제외, 설계 권고)")
    runway = _runway(cash, undrawn or 0.0, -fcf)
    step = _runway_step(runway, rules)
    score = _clamp(score + step, floor)
    path.append({"gate": "G3", "runway_years": runway, "buffer": cash + (undrawn or 0.0), "annual_burn": -fcf, "step": step, "score": score})

    # ------------------------------------------------------------------ G4 미래 지출이 덮이는가
    g4 = _g4(cid, obs, gi, rules, run, use)
    if g4["step"] is None:
        path.append({"gate": "G4", **{k: v for k, v in g4.items() if k not in ("step", "pending")}})
        return done(None, _pending_status(g4["pending"]), g4["pending"])
    score = _clamp(score + g4["step"], floor)
    path.append({"gate": "G4", **{k: v for k, v in g4.items() if k != "pending"}, "score": score})
    return done(score, "ok")



def _private_undisclosed_operating(company: dict[str, Any], obs: ObsLookup, rules: RuleSet,
                                   run: dict[str, Any]) -> bool:
    """비상장 + TTM 영업손익이 **구조적 미공시** 인가 (C-20).

    **자료가 없다는 것만으로는 부족하다.** `missing_type == not_disclosed_confirmed` 라는 라벨이
    관측에 있어야 한다 — 우리가 안 찾은 것과 회사가 낼 의무가 없는 것을 가르는 장치이고
    MISS-LABEL-23 이 세운 것이다. 규칙에 경로 선언이 없거나 실행이 C-20 을 선택하지 않으면 False.
    """
    if company["listed"]:
        return False
    spec = (rules.f9 or {}).get("g1_private_undisclosed_route")
    if not spec:
        return False
    if decision_choice(run, rules, "C-20") != spec.get("choice_required"):
        return False
    for metric in ("operating_margin_ttm", "operating_income_ttm"):
        o = obs.get(company["company_id"], metric)
        if o is not None and o.get("missing_type") == MISSING_TYPE_FOR_DISCLOSURE_POLICY:
            return True
    return False

def _g4(cid: str, obs: ObsLookup, gi: dict[str, Any], rules: RuleSet, run: dict[str, Any], use) -> dict[str, Any]:
    """약정 커버리지. step: 0 유지 / -1 하향 / None 미결(pending 포함)."""
    contracted, c_obs = obs.number(cid, "contracted_revenue")
    offb, b_obs = obs.number(cid, "offbalance_B")
    use(c_obs)
    use(b_obs)
    out: dict[str, Any] = {}
    comparable = gi.get("coverage_comparable", "unknown")
    if comparable == "no":
        # 기간·범위가 다른 자료(ARR·연환산 약정 등)는 비교하지 않는다. 같은 범위의 계약 자료를 확보해야 하는 자료 대기다 (C-07).
        out.update({"result": "incompatible", "reason": "계약 수입과 B종 약정의 기간·범위가 달라 비교 불가(C-07) — 동일 범위 자료 확보 전 미완료", "step": None,
                    "pending": pending_info("data", "같은 범위·기간의 계약 수입/B종 약정 자료 필요(C-07, ARR 대체 금지)")})
        return out
    if comparable != "yes":
        # 비교 가능성(기간·범위·성격)은 검토 입력이다. 숫자가 있어도 확정하지 않고, 결측 정책(C-16)으로도 보내지 않는다 (R02).
        out.update({"result": "undetermined", "reason": "coverage_comparable 미확인", "contracted_revenue": contracted, "offbalance_B": offb, "step": None,
                    "pending": pending_info("judgment", "G4: 계약 수입과 B종 약정이 같은 범위·기간인지(coverage_comparable) 검토 입력 필요")})
        return out
    if contracted is not None and offb is not None:
        if offb == 0:
            out.update({"result": "no_obligations", "coverage": None, "step": 0, "note": "B종 약정 0"})
            return out
        coverage = contracted / offb
        step = 0 if coverage >= float(rules.f9["g4_coverage_keep"]) else -1
        out.update({"result": "computed", "coverage": coverage, "contracted_revenue": contracted, "offbalance_B": offb, "step": step})
        return out
    # 결측 유형을 구분한다: 수집 실패·파싱 실패·관측 부재는 자료 대기, 확인된 미공시만 C-16 정책 대상이다 (설계 지침 6.4).
    missing = []
    types = []
    for name, value, o in (("contracted_revenue", contracted, c_obs), ("offbalance_B", offb, b_obs)):
        if value is None:
            # status 하나로는 갈리지 않는다. not_disclosed 가 미확인·미공시·계산 대상 아님을 다 담고 있었다.
            mtype = (o or {}).get("missing_type")
            label = mtype or ((o["status"] if o else "관측 없음") + "/결측유형 미분류")
            missing.append(f"{name}({label})")
            types.append(mtype)
    if any(mt != MISSING_TYPE_FOR_DISCLOSURE_POLICY for mt in types):
        # 미분류(None)도 여기로 온다. 확인된 미공시라는 증거가 없으면 C-16 으로 보내지 않는다 (설계 지침 6.4).
        unlabeled = [m for m, mt in zip(missing, types) if mt is None]
        extra = " — 결측 유형이 분류되지 않아 확인된 미공시인지 판별 불가" if unlabeled else ""
        out.update({"result": "undetermined", "missing": missing, "step": None,
                    "pending": pending_info("data", "G4 자료 미수집/파싱 실패: " + ", ".join(missing)
                                            + " — 수집 실패를 미공시 위험으로 둔갑시키지 않음" + extra)})
        return out
    out.update({"result": "undetermined", "missing": missing,
                "reason": f"확인된 미공시({MISSING_TYPE_FOR_DISCLOSURE_POLICY})"})
    choice = decision_choice(run, rules, "C-16")
    if choice == "downgrade":
        out["step"] = -1
        out["policy"] = "downgrade (C-16 실행 결정)"
    elif choice == "hold":
        out["step"] = 0
        out["policy"] = "hold (C-16 실행 결정)"
    else:
        out["step"] = None
        out["pending"] = pending_info("rule", "약정 커버리지 판정 불가 시 하향/유지 규칙 미확정", "C-16")
    return out
