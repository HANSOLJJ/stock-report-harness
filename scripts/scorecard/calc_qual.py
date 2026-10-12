# 정성 판정 → 점수 환산 factor 계산: F1 락인 사다리(v2.0)·수동 점수, F4·F8 수동 점수, F2 경로 매핑, F3 사다리, F5 산식, F7 매트릭스
from __future__ import annotations

from typing import Any

from .inputs import JudgmentLookup, carried_note, factor_result, pending_info
from .rules import RuleSet, decision_choice

COMPONENT_TYPE = "부품"


def _status_for(judgment: dict[str, Any]) -> str:
    return "carried_score" if judgment["status"] == "carried" else "ok"


def compute_manual(fid: str, company: dict[str, Any], judgments: JudgmentLookup, rules: RuleSet) -> dict[str, Any]:
    judgment = judgments.get(company["company_id"], fid)
    if judgment is None or judgment["kind"] != "score":
        return factor_result(fid, score=None, status="needs_judgment", basis="manual",
                             pending=pending_info("judgment", f"{rules.factor(fid)['label']} 점수·근거·검토자 입력 필요"))
    score = int(judgment["score"])
    warnings: list[str] = []
    # 2026-10-08 규칙 v2.0: 부품 채널 일괄 상한을 없앴다(지속성 할인으로 대체). 상한은 규칙에 키가 있을 때만 댄다.
    if fid == "F1" and company["type"] == COMPONENT_TYPE and "component_only_cap" in rules.factor("F1"):
        cap = int(rules.factor("F1")["component_only_cap"])
        if score > cap:
            return factor_result(fid, score=None, status="error", basis="manual", judgment=judgment,
                                 pending=pending_info("error", f"부품형 기업의 F1 은 상한 {cap} — 입력 {score}"))
        warnings.append(f"F1 부품 상한 {cap} 적용 대상(실질 소비자·업무 채널 없음)")
    warnings.extend(carried_note(judgment))
    return factor_result(fid, score=score, status=_status_for(judgment), basis="manual", judgment=judgment, warnings=warnings)


def _lower_band(bands: list[dict[str, Any]], value: float) -> float:
    """lower 이상이면 그 칸. 위에서부터 본다(마지막 칸 lower null 이 나머지를 덮는다)."""
    for band in bands:
        if band["lower"] is None or value >= band["lower"]:
            return band["score"]
    raise ValueError("bands 가 구간을 덮지 못함")


def _half_step(value: float) -> float | int:
    """0.5 단위 점수를 정수면 int 로 돌려준다(결과 JSON 이 13 과 13.0 으로 갈리지 않게)."""
    return int(value) if float(value).is_integer() else float(value)


def compute_f4(company: dict[str, Any], judgments: JudgmentLookup, rules: RuleSet) -> dict[str, Any]:
    """④ 호황 이후 비전(규칙 v2.1, 2026-10-12 사용자 결정). 수직계열화 축 + 다각화 축.

    수직계열화 축은 층별 보유표의 칸 값 합(판매 1 · 자체 사용 0.5 · 없음·준비 중 0)을 상한으로 자르고, 다각화 축은 AI 와 무관한
    최종 수요에서 나오는 매출 몫을 구간으로 바꿔 상한으로 자른다. 둘을 더한다(0.5 단위). 미확인 칸이나 몫이 미확인이면 점수를 만들지 않는다.
    """
    fid = "F4"
    spec = rules.factor(fid)
    judgment = judgments.get(company["company_id"], fid)
    if judgment is None:
        return factor_result(fid, score=None, status="needs_judgment", basis="survival",
                             pending=pending_info("judgment", "층별 보유표·주 레이어·AI 무관 매출 몫 판정 입력 필요"))
    mismatch = _kind_mismatch(fid, judgment, rules, "survival", "층별 보유표 입력(survival)")
    if mismatch is not None:
        return mismatch
    inputs = judgment["inputs"]
    layers = inputs["layers"]
    calc: dict[str, Any] = {"layers": dict(layers), "primary_layer": inputs.get("primary_layer"),
                            "non_ai_revenue_share": inputs.get("non_ai_revenue_share")}
    unknown = sorted(k for k, v in layers.items() if v == "unknown")
    if unknown:
        return factor_result(fid, score=None, status="needs_judgment", basis="survival", judgment=judgment, calc=calc,
                             pending=pending_info("judgment", f"보유표 칸 {unknown} 이 미확인 — 칸 값을 추정하지 않는다"))
    share = inputs["non_ai_revenue_share"]
    if share == "unknown":
        return factor_result(fid, score=None, status="needs_judgment", basis="survival", judgment=judgment, calc=calc,
                             pending=pending_info("judgment", "AI 무관 매출 몫이 미확인 — 세그먼트 공시로 최종 수요를 가른다"))
    values = spec["cell_values"]
    vertical_raw = sum(float(values[v]) for v in layers.values())
    vertical = min(float(spec["vertical_cap"]), vertical_raw)
    diversification = min(float(spec["diversification_cap"]), float(_lower_band(spec["non_ai_share_tiers"], float(share))))
    lo, hi = rules.factor_range(fid)
    score = _half_step(max(lo, min(hi, vertical + diversification)))
    calc.update({"vertical_raw": vertical_raw, "vertical": vertical, "diversification": diversification, "score": score,
                 "preparing": sorted(k for k, v in layers.items() if v == "preparing"),
                 "layer_triggers": dict(inputs.get("layer_triggers") or {})})
    return factor_result(fid, score=score, status=_status_for(judgment), basis="survival", judgment=judgment, calc=calc,
                         warnings=carried_note(judgment))


AXIS_DEFAULT_STATUSES = {"not_disclosed", "not_found"}


def _f8_axis(axis: str, a: dict[str, Any], spec: dict[str, Any]) -> tuple[int, str]:
    """축 하나의 사다리 칸과 근거 종류. 확인됨이면 재료로, 부재 확인·해당 없음이면 0, 비공개·탐색 미완이면 정책 기본값."""
    status = a["status"]
    if status in ("absent_disclosed", "not_applicable"):
        return 0, status
    if status in AXIS_DEFAULT_STATUSES:
        return int(spec["unknown_default"]), status
    if axis == "customer":
        c = spec["customer"]
        share = max(float(a.get("recognized_share") or 0), float(a.get("contract_share") or 0))
        if a.get("dedicated_assets") == "yes":
            if share >= c["dedicated_nearly_all"]["lower"]:
                return int(c["dedicated_nearly_all"]["score"]), status
            if share >= c["dedicated_majority"]["lower"]:
                return int(c["dedicated_majority"]["score"]), status
        return int(_lower_band(c["bands"], share)), status
    if axis == "commitment":
        return int(_lower_band(spec["commitment"]["bands"], float(a["multiple"]))), status
    return int(a["rung"]), status


def compute_f8(company: dict[str, Any], judgments: JudgmentLookup, rules: RuleSet) -> dict[str, Any]:
    """⑧ 비대칭 의존(규칙 v2.1, 2026-10-12 사용자 결정). 고객·약정·공급·지정학 네 축을 같은 사다리에 놓고 가장 낮은 칸을 쓴다.

    고객 축은 최대 고객 비중(인식 매출과 연환산 계약액 중 큰 값)과 전용 자산, 약정 축은 약정 ÷ 매출 배수로 계산하고, 공급·지정학 축은
    판단이 고른 칸을 쓴다. 비공개·탐색 미완 축은 정책 기본값(−1)이고, 네 축이 모두 그렇다면 점수를 만들지 않는다.
    """
    fid = "F8"
    spec = rules.factor(fid)
    judgment = judgments.get(company["company_id"], fid)
    if judgment is None:
        return factor_result(fid, score=None, status="needs_judgment", basis="axes",
                             pending=pending_info("judgment", "고객·약정·공급·지정학 네 축 판정 입력 필요"))
    mismatch = _kind_mismatch(fid, judgment, rules, "axes", "네 축 입력(axes)")
    if mismatch is not None:
        return mismatch
    inputs = judgment["inputs"]
    axes: dict[str, Any] = {}
    for axis in spec["axes"]:
        score, basis = _f8_axis(axis, inputs[axis], spec)
        axes[axis] = {"score": score, "basis": basis, "inputs": dict(inputs[axis]),
                      "policy_default": basis in AXIS_DEFAULT_STATUSES}
    calc: dict[str, Any] = {"axes": axes}
    if all(a["policy_default"] for a in axes.values()):
        calc["assessment_complete"] = False
        return factor_result(fid, score=None, status="needs_judgment", basis="axes", judgment=judgment, calc=calc,
                             pending=pending_info("judgment", "네 축이 모두 비공개·탐색 미완 — 기본값만으로 점수를 만들지 않는다"))
    lo, hi = rules.factor_range(fid)
    worst = min(a["score"] for a in axes.values())
    score = max(lo, min(hi, worst))
    calc.update({"score": score, "deciding_axes": [k for k, a in axes.items() if a["score"] == worst],
                 "assessment_complete": not any(a["policy_default"] for a in axes.values())})
    labels = {"not_disclosed": "비공개", "not_found": "탐색 미완"}
    warnings = [f"⑧ {spec['axis_labels'][k]} 축은 {labels[a['basis']]} — 정책 기본값 {a['score']}(실제 위험을 확인한 값이 아니다)"
                for k, a in axes.items() if a["policy_default"]]
    return factor_result(fid, score=score, status=_status_for(judgment), basis="axes", judgment=judgment, calc=calc,
                         warnings=warnings + carried_note(judgment))


STRENGTH_RANK = {"fail": 0, "partial": 1, "pass": 2}


def _kind_mismatch(fid: str, judgment: dict[str, Any], rules: RuleSet, basis: str, what: str) -> dict[str, Any] | None:
    """규칙이 새 판단의 kind 를 선언했는데(`judgment_kinds`) 판단이 그 밖이면(이어받은 score) 점수를 만들지 않는다.

    2026-10-08 설계 보완: 재실행은 옛 판단을 이어받은 뒤 하나씩 판정 입력으로 바꾼다. 그동안의 calculate 가
    터지지 않게 error 가 아니라 needs_judgment 로 두고, 이어받은 점수는 쓰지 않는다."""
    declared = rules.factor(fid).get("judgment_kinds")
    if not declared or judgment["kind"] in declared:
        return None
    return factor_result(fid, score=None, status="needs_judgment", basis=basis, judgment=judgment,
                         pending=pending_info("judgment", f"{what} 필요 — 이어받은 점수는 쓰지 않는다"))


def compute_f1(company: dict[str, Any], judgments: JudgmentLookup, rules: RuleSet) -> dict[str, Any]:
    """① 락인과 가격결정력(규칙 v2.0, 2026-10-08 사용자 결정). 판정 입력을 규칙의 사다리로 환산한다.

    락인 강도 = 회수 루프·전환비용 중 높은 판정(통과 > 부분 > 실패). 둘 다 미확인이면 점수를 만들지 않고, 한쪽만 미확인이면
    아는 쪽을 쓴다. 실질 채널이 하나도 없으면 none_score 이고 보정을 적용하지 않는다. 기본 점수에 가격 실측·대체 공급·지속성
    할인 보정을 더해 factor range 로 자른다. `ai_monetized_in_channel` 은 v2.0 에서는 점수에 넣지 않고 calc 에만 옮긴다(표시 전용).
    규칙 v2.1 은 사다리에 `top_score_requires_ai_monetized` 를 두어 그 값이 '예' 가 아니면 상한(4)을 댄다(2026-10-12 사용자 결정).
    """
    fid = "F1"
    spec = rules.factor(fid)
    judgment = judgments.get(company["company_id"], fid)
    if judgment is None:
        return factor_result(fid, score=None, status="needs_judgment", basis="lockin",
                             pending=pending_info("judgment", "채널 목록과 네 질문(회수 루프·전환비용·대체 공급·가격 실측) 판정 입력 필요"))
    if judgment["kind"] != "lockin":
        return factor_result(fid, score=None, status="needs_judgment", basis="lockin", judgment=judgment,
                             pending=pending_info("judgment", "네 질문 입력(lockin) 필요 — 이어받은 점수는 쓰지 않는다"))
    inputs = judgment["inputs"]
    ladder = spec["ladder"]
    channels = spec["channels"]
    lo, hi = rules.factor_range(fid)
    warnings: list[str] = []
    calc: dict[str, Any] = {"inputs": dict(inputs), "ai_monetized_in_channel": inputs.get("ai_monetized_in_channel"),
                            "range": [lo, hi]}
    if all(inputs.get(k) == "no" for k in channels["keys"]):
        score = int(channels["none_score"])
        calc.update(no_channel=True, strength=None, strength_from=[], steps={"base": score}, raw=score, score=score)
        warnings.extend(carried_note(judgment))
        return factor_result(fid, score=score, status=_status_for(judgment), basis="lockin", judgment=judgment, calc=calc,
                             warnings=[f"실질 채널(소비자·업무·거래)이 없다 → {score}, 보정을 적용하지 않음"] + warnings)
    known = {k: inputs[k] for k in ladder["strength_of"] if inputs.get(k) in STRENGTH_RANK}
    if not known:
        return factor_result(fid, score=None, status="needs_judgment", basis="lockin", judgment=judgment, calc=calc,
                             pending=pending_info("judgment", "회수 루프·전환비용이 둘 다 미확인 — 락인 강도를 추정하지 않음"))
    strength = max(known.values(), key=lambda v: STRENGTH_RANK[v])
    pricing = inputs["pricing"]
    need = int(ladder["pricing_pass_requires_quarters"])
    quarters = inputs.get("pricing_sustained_quarters")
    if pricing == "pass" and (quarters is None or quarters < need):
        # 스키마가 새 판단에서 먼저 막는다. 이어받은 판단 등 그 밖의 길로 들어오면 통과로 세지 않는다.
        pricing = "partial"
        warnings.append(f"가격 실측 통과는 {need}분기 이상 지속이 필요한데 입력 {quarters}분기 — 부분으로 계산")
    steps = {
        "base": int(ladder["base_by_strength"][strength]),
        "pricing": int(ladder["pricing_step"][pricing]),
        "substitutes": int(ladder["substitutes_step"][inputs["substitutes"]]),
        "durability_discount": int(ladder["durability_discount_step"]) if inputs["durability_discount"] == "yes" else 0,
    }
    raw = sum(steps.values())
    score = max(lo, min(hi, raw))
    calc.update(no_channel=False, strength=strength, strength_from=sorted(k for k, v in known.items() if v == strength),
                pricing_used=pricing, pricing_pass_requires_quarters=need, steps=steps, raw=raw, score=score)
    if score != raw:
        warnings.append(f"사다리 합 {raw} 를 범위 [{lo}, {hi}] 로 자름 → {score}")
    # 2026-10-12 규칙 v2.1: 5점은 가장 강한 채널의 AI 수익화가 '예' 일 때만 준다. 키가 없는 규칙(v2.0 이하)은 지나간다.
    gate = ladder.get("top_score_requires_ai_monetized")
    if gate:
        value = inputs.get(gate["input"])
        cap = int(gate["cap"])
        calc["ai_monetization_gate"] = {"input": gate["input"], "value": value, "requires": gate["requires"], "cap": cap,
                                        "applied": value != gate["requires"] and score > cap}
        if calc["ai_monetization_gate"]["applied"]:
            warnings.append(f"AI 수익화 {value!r} — 5점은 {gate['requires']!r} 일 때만이라 {score} → {cap}")
            score = cap
            calc["score"] = score
    warnings.extend(carried_note(judgment))
    return factor_result(fid, score=score, status=_status_for(judgment), basis="lockin", judgment=judgment, calc=calc,
                         warnings=warnings)


def compute_f2(company: dict[str, Any], judgments: JudgmentLookup, rules: RuleSet, run: dict[str, Any]) -> dict[str, Any]:
    fid = "F2"
    judgment = judgments.get(company["company_id"], fid)
    if judgment is None:
        return factor_result(fid, score=None, status="needs_judgment", basis="paths",
                             pending=pending_info("judgment", "세 경로(성능 도약·패러다임 적응·표준 선점) 판정 입력 필요"))
    choice = decision_choice(run, rules, "C-03")
    mismatch = _kind_mismatch(fid, judgment, rules, "paths", "세 경로 입력(paths)")
    if mismatch is not None:
        return mismatch
    if judgment["kind"] == "score":
        # 2026-09-15 FIX-52: v1.7 은 C-03 이 확정됐다. 그래도 세대 격차는 판단 입력이라 엔진이 산출할 수 없어 승계한다.
        reason = ("C-03 확정(paths_with_generation_gap_5)이나 세대 격차는 판단 입력이라 경로 판정 전까지 승계 점수를 사용"
                  if choice == GENERATION_GAP_CHOICE else
                  "C-03: 경로→점수 매핑 미확정이라 승계 점수를 기준선 표시로 사용")
        return factor_result(fid, score=int(judgment["score"]), status="carried_score", basis="carried", judgment=judgment,
                             warnings=[reason] + carried_note(judgment))
    inputs = judgment["inputs"]
    leap = inputs["performance_leap"]
    leap_warnings: list[str] = []
    if rules.factor(fid).get("leap_requires_independent_measurement") and leap == "pass" and inputs.get("leap_independent") != "yes":
        # 2026-10-08 규칙 v2.0(2.7): 벤더 발표만 있는 성능 주장은 부분 통과다. 경로 수와 5점 판정 모두 부분으로 센다.
        leap = "partial"
        leap_warnings.append("성능 도약이 통과로 적혔으나 독립 측정(leap_independent)이 yes 가 아니다 — 부분 통과로 계산(2.7)")
    paths = [leap, inputs["paradigm_adaptation"], inputs["standard_capture"]]
    passed = sum(1 for p in paths if p == "pass")
    partial = sum(1 for p in paths if p == "partial")
    calc = {"paths": inputs, "passed": passed, "partial": partial}
    if leap_warnings:
        calc["performance_leap_used"] = leap
    if choice == GENERATION_GAP_CHOICE:
        return _f2_generation_gap(fid, inputs, paths, calc, judgment, rules, company=company, warnings=leap_warnings)
    if "unknown" in paths or inputs["top_rank"] == "unknown":
        return factor_result(fid, score=None, status="needs_judgment", basis="paths", judgment=judgment,
                             pending=pending_info("judgment", "경로 판정에 unknown 이 있음 — 실패로 간주하지 않음"))
    # 아래는 v1.5·v1.6 의 후보 매핑 경로다. v1.7 규칙에는 path_mapping_candidate 가 없고 이 선택은 superseded 다.
    if choice != "activate_candidate_mapping":
        return factor_result(fid, score=None, status="needs_rule_decision", basis="paths", judgment=judgment, calc=calc,
                             pending=pending_info("rule", "경로 수→점수 매핑(3경로·0/1점·5점 자격)이 미확정", "C-03"))
    # 2026-09-15 FIX-54 1단계 S7(3차 리뷰 C RC3-09): v1.7 F2 에는 path_mapping_candidate 가 없어 옛 선택지로 오면 KeyError 였다.
    # 규칙이 이 선택을 받칠 매핑을 갖고 있지 않다는 사실을 오류 상태로 드러낸다 — 다른 매핑으로 대신 채우지 않는다.
    if "path_mapping_candidate" not in rules.factor(fid):
        return factor_result(fid, score=None, status="error", basis="paths", judgment=judgment, calc=calc,
                             pending=pending_info("error", f"C-03 선택 activate_candidate_mapping 은 규칙 {rules.version} 에서 쓸 수 없다 — "
                                                           "factor 에 path_mapping_candidate 가 없다(superseded 선택지)", "C-03"))
    mapping = rules.factor(fid)["path_mapping_candidate"]
    calc["mapping"] = mapping
    if str(passed) not in mapping and inputs["top_rank"] != "yes":
        # 후보 매핑에 없는 통과 수(3경로 전부 통과)는 기본값을 만들지 않고 미결로 남긴다.
        return factor_result(fid, score=None, status="needs_rule_decision", basis="paths", judgment=judgment, calc=calc,
                             pending=pending_info("rule", f"경로 {passed}개 통과 점수가 후보 매핑에 없음", "C-03"))
    score = 5 if inputs["top_rank"] == "yes" else int(mapping[str(passed)])
    return factor_result(fid, score=score, status="ok", basis="paths", judgment=judgment, calc=calc,
                         warnings=["C-03: 후보 매핑(0→2, 1→3, 2→4, 종합 1위→5)을 실행 단위 결정으로 적용"] + carried_note(judgment))


GENERATION_GAP_CHOICE = "paths_with_generation_gap_5"


def _f2_generation_gap(fid: str, inputs: dict[str, Any], paths: list[str], calc: dict[str, Any],
                       judgment: dict[str, Any], rules: RuleSet, *, company: dict[str, Any] | None = None,
                       warnings: list[str] | None = None) -> dict[str, Any]:
    """C-03 확정 모델 — 경로 수 0·1·2 → 2·3·4, **성능 도약이 세대 격차 수준이면 5** (v1.7, 2026-09-14).

    5점 칸은 `AA 종합 1위`(top_rank)가 아니다. 세대 격차는 판단 입력 `generation_gap` 으로 받고, 없거나 unknown 이면
    추정하지 않는다. 세대 격차가 세 축 중 몇 개에서 서야 하는지는 원문 미규정이라 판단자가 근거란에 적는다.

    2026-10-08 규칙 v2.0: `paths[0]` 은 독립 측정 규칙을 반영한 성능 도약이다. 규칙에 `generation_gap_months` 가 있으면
    세대 격차 yes 도 회사 유형별 개월 수 임계 이상일 때만 5 이고, 미만이면 경로 수 매핑으로 내린다.
    """
    warnings = list(warnings or [])
    if "unknown" in paths:
        return factor_result(fid, score=None, status="needs_judgment", basis="paths", judgment=judgment, calc=calc,
                             pending=pending_info("judgment", "경로 판정에 unknown 이 있음 — 실패로 간주하지 않음"))
    spec = rules.factor(fid)
    mapping = spec["path_mapping"]
    calc["mapping"] = mapping
    calc["choice"] = GENERATION_GAP_CHOICE
    gap = inputs.get("generation_gap", "unknown")
    calc["generation_gap"] = gap
    if paths[0] == "pass" and spec.get("score5_requires_generation_gap"):
        if gap == "unknown":
            return factor_result(fid, score=None, status="needs_judgment", basis="paths", judgment=judgment, calc=calc,
                                 pending=pending_info("judgment", "성능 도약이 통과인데 세대 격차(generation_gap) 판정이 없음 — "
                                                                  "5점 여부를 추정하지 않음"))
        months_spec = spec.get("generation_gap_months")
        if gap == "yes" and months_spec:
            ctype = (company or {}).get("type")
            threshold = int((months_spec.get("by_company_type") or {}).get(ctype, months_spec["default"]))
            months = inputs.get("generation_gap_months")
            calc["generation_gap_months_threshold"] = threshold
            calc["generation_gap_months"] = months
            if months is None:
                return factor_result(fid, score=None, status="needs_judgment", basis="paths", judgment=judgment, calc=calc,
                                     pending=pending_info("judgment", "세대 격차 yes 인데 개월 수(generation_gap_months)가 없음 — "
                                                                      "5점 여부를 추정하지 않음"))
            if months < threshold:
                warnings.append(f"세대 격차 {months}개월 < 임계 {threshold}개월(회사 유형 {ctype}) — 5 를 주지 않고 경로 수로 계산")
                gap = "below_threshold"
        if gap == "yes":
            return factor_result(fid, score=5, status="ok", basis="paths", judgment=judgment, calc=calc,
                                 warnings=warnings + ["C-03 확정: 성능 도약이 세대 격차 수준 → 5"] + carried_note(judgment))
    passed = calc["passed"]
    if str(passed) not in mapping:
        # 2026-10-08 재판단에서 Anthropic·NVIDIA 가 세 경로를 다 통과했는데 세대 격차가 아니라 걸렸다. 매핑은 0·1·2 칸뿐인데
        # 5 는 세대 격차에만 주기로 했으므로(score5_requires_generation_gap), 세 경로 통과는 매핑의 가장 높은 칸(두 경로 4)과 같다.
        # 통과 수가 매핑의 최대 키보다 크면 그 칸으로 자르고, 작은데 없으면(0·1 이 빠진 규칙) 지금처럼 규칙 결정 대기다.
        top = max(int(k) for k in mapping)
        if passed > top and spec.get("score5_requires_generation_gap"):
            calc["mapping_capped_from"] = passed
            return factor_result(fid, score=int(mapping[str(top)]), status="ok", basis="paths", judgment=judgment, calc=calc,
                                 warnings=warnings + [f"C-03 확정: 경로 {passed}개 통과는 세대 격차가 아니라 두 경로와 같은 {mapping[str(top)]} "
                                                      "— 5 는 세대 격차에만"] + carried_note(judgment))
        return factor_result(fid, score=None, status="needs_rule_decision", basis="paths", judgment=judgment, calc=calc,
                             pending=pending_info("rule", f"경로 {passed}개 통과(세대 격차 없음) 점수가 매핑에 없음", "C-03"))
    return factor_result(fid, score=int(mapping[str(passed)]), status="ok", basis="paths", judgment=judgment, calc=calc,
                         warnings=warnings + [f"C-03 확정: 경로 {passed}개 → {mapping[str(passed)]}"] + carried_note(judgment))


def compute_f3(company: dict[str, Any], judgments: JudgmentLookup, rules: RuleSet) -> dict[str, Any]:
    fid = "F3"
    judgment = judgments.get(company["company_id"], fid)
    if judgment is None:
        return factor_result(fid, score=None, status="needs_judgment", basis="criteria",
                             pending=pending_info("judgment", "모방불가·수익모델·가속도 판정 입력 필요"))
    inputs = judgment["inputs"]
    weights = rules.factor(fid)["criteria_weights"]
    criteria = ("imitation", "revenue_model", "acceleration")
    # 2026-10-08 규칙 v2.0: 가속도 지표 단계의 상한(c 는 최대 부분, e 는 미확인)을 판정에 댄다. 스키마가 새 판단에서 먼저 막고
    # 여기는 그 밖의 길로 들어온 입력을 막는 방어다. 단계 키가 없는 규칙(v1.9 이하)은 아무것도 바꾸지 않는다.
    effective = {c: inputs[c] for c in criteria}
    tier_calc: dict[str, Any] = {}
    warnings: list[str] = []
    tiers_spec = rules.factor(fid).get("acceleration_tiers")
    if tiers_spec:
        tier = inputs.get("acceleration_tier")
        tier_calc = {"acceleration_tier": tier, "acceleration_growth_rates": inputs.get("acceleration_growth_rates")}
        cap = ((tiers_spec.get("tiers") or {}).get(tier) or {}).get("max")
        acc = effective["acceleration"]
        if tier is None:
            warnings.append("가속도 지표 단계(acceleration_tier)가 적히지 않은 판단 — 같은 단계끼리 비교할 수 없음")
        elif cap == "unknown" and acc not in ("unknown", "fail"):
            # 지표가 없는 단계는 통과·부분을 줄 수 없다. 실패는 규칙 ③ 판정 지침의 지연 조항(지연은 감속)이라 그대로 센다.
            effective["acceleration"] = "unknown"
            warnings.append(f"지표 단계 {tier} 는 가속도를 통과·부분으로 판정할 수 없다 — 입력 {acc} 를 미확인으로 계산")
        elif cap in STRENGTH_RANK and acc in STRENGTH_RANK and STRENGTH_RANK[acc] > STRENGTH_RANK[cap]:
            effective["acceleration"] = cap
            warnings.append(f"지표 단계 {tier} 의 가속도는 최대 {cap} — 입력 {acc} 를 {cap} 로 계산")
        if effective["acceleration"] != acc:
            tier_calc["acceleration_input"] = acc
    if any(effective[c] == "unknown" for c in criteria):
        return factor_result(fid, score=None, status="needs_judgment", basis="criteria", judgment=judgment,
                             calc=tier_calc or None, warnings=warnings,
                             pending=pending_info("judgment", "세 기준 중 unknown 이 있음 — 자동으로 0.5 를 주지 않음"))
    points = sum(float(weights[effective[c]]) for c in criteria)
    imitation_pass = inputs["imitation"] == "pass"
    door = inputs["door_closed"]
    score, note = rules.f3_ladder(points, imitation_pass, door == "pass")
    if score == 4 and door == "unknown":
        warnings.append("문 닫힘 증거 미확인 → 상한 4 유지")
    calc = {"criteria": effective, "door_closed": door, "pass_points": points, "ladder_note": note, **tier_calc}
    warnings.extend(carried_note(judgment))
    return factor_result(fid, score=score, status=_status_for(judgment), basis="criteria", judgment=judgment, calc=calc, warnings=warnings)


def compute_f5(company: dict[str, Any], judgments: JudgmentLookup, rules: RuleSet) -> dict[str, Any]:
    fid = "F5"
    judgment = judgments.get(company["company_id"], fid)
    if judgment is None:
        return factor_result(fid, score=None, status="needs_judgment", basis="grade",
                             pending=pending_info("judgment", "동맹 A 등급·적대 H 등급 입력 필요(별표 G)"))
    A = int(judgment["inputs"]["A"])
    H = int(judgment["inputs"]["H"])
    score = rules.f5_formula(A, H)
    return factor_result(fid, score=score, status=_status_for(judgment), basis="grade", judgment=judgment,
                         calc={"A": A, "H": H, "formula": "3 + A + H"}, warnings=carried_note(judgment))


def compute_f7(company: dict[str, Any], judgments: JudgmentLookup, rules: RuleSet) -> dict[str, Any]:
    fid = "F7"
    judgment = judgments.get(company["company_id"], fid)
    if judgment is None:
        return factor_result(fid, score=None, status="needs_judgment", basis="matrix",
                             pending=pending_info("judgment", "조달 의존 고객 비중(큼/작음)·자기 자금 환류(예/아니오) 판정 필요(별표 I)"))
    # 2026-10-08 규칙 v2.0: ⑦ 은 매트릭스 입력으로만 판단한다. 이어받은 score 판단은 점수를 만들지 않는다.
    mismatch = _kind_mismatch(fid, judgment, rules, "matrix", "두 축 입력(matrix)")
    if mismatch is not None:
        return mismatch
    if judgment["kind"] == "score":
        return factor_result(fid, score=int(judgment["score"]), status="carried_score", basis="carried", judgment=judgment,
                             warnings=["C-09: 매트릭스 입력이 복원되지 않아 승계 점수를 기준선 표시로 사용"] + carried_note(judgment))
    share = judgment["inputs"]["funding_dependent_share"]
    returns = judgment["inputs"]["own_money_returns"]
    if share == "unknown" or returns == "unknown":
        return factor_result(fid, score=None, status="needs_judgment", basis="matrix", judgment=judgment,
                             pending=pending_info("judgment", "두 축 중 unknown 이 있음 — 환류 사실을 추정하지 않음"))
    score = rules.f7_matrix(share, returns)
    return factor_result(fid, score=score, status=_status_for(judgment), basis="matrix", judgment=judgment,
                         calc={"funding_dependent_share": share, "own_money_returns": returns}, warnings=carried_note(judgment))
