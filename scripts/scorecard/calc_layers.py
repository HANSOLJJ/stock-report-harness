# 규칙 v3.0 층 단위 계산: ④ 보유표의 매출 줄로 층 매출 몫(①②③ 의 무게)을 내고 ④ 수직계열화·다각화·그 분야의 힘을 계산한다
from __future__ import annotations

from calendar import monthrange
from datetime import date
from typing import Any, Callable

from .calc_qual import _kind_mismatch, _status_for
from .inputs import JudgmentLookup, carried_note, factor_result, pending_info
from .rules import RuleSet, piecewise


def layer_weights(holdings: dict[str, Any], rules: RuleSet) -> dict[str, Any]:
    """층 매출 몫(rules.md 2.10). 열 층과 층 밖 사업에 붙은 매출 줄 합으로 나눈다. 제외 줄(로켓 발사)은 분모 밖이다.

    판매 칸인데 붙은 줄이 없는 층은 무게 0 으로 싣는다(점수는 매기되 무게가 없다). 금액이 미확인인 줄이 있으면 몫을 내지 않는다
    (어림이나 균등 비중으로 채우지 않는다). 돌려주는 값: ok, weights{층: 몫}, zero_weight_sold, unknown_lines, primary_layer."""
    spec = rules.payload["layers"]
    order = list(spec["order"])
    units = [*order, spec["outside"]["id"]]
    lines = [line for line in holdings["revenue_lines"] if line["layer"] in units]
    sold = [layer for layer in order if holdings["cells"][layer]["cell"] == "sold"]
    unknown = [line["line"] for line in lines if line["amount"] == "unknown"]
    if unknown:
        return {"ok": False, "weights": {}, "zero_weight_sold": [], "unknown_lines": unknown, "primary_layer": None}
    amounts = {u: sum(float(line["amount"]) for line in lines if line["layer"] == u) for u in units}
    total = sum(amounts.values())
    if total <= 0:
        return {"ok": False, "weights": {}, "zero_weight_sold": sold, "unknown_lines": [], "primary_layer": None}
    weights = {u: amounts[u] / total for u in units if amounts[u] > 0 or u in sold}
    # 주 층 = 층 매출 몫이 가장 큰 판매 층(④ 비교 그룹). 층 밖 사업은 비교 그룹이 아니다. 동률이면 층 순서가 앞선 쪽.
    ranked = [layer for layer in order if layer in sold and weights.get(layer, 0) > 0]
    primary = max(ranked, key=lambda layer: (weights[layer], -order.index(layer))) if ranked else None
    return {"ok": True, "weights": weights, "zero_weight_sold": [layer for layer in sold if amounts[layer] == 0],
            "unknown_lines": [], "primary_layer": primary}


def _tidy(value: float) -> float | int:
    """calc 표시용으로 부동소수 찌꺼기만 정리한다. 점수 반올림은 합에서 한 번 한다(RuleSet.round_score)."""
    value = round(float(value), 6)
    return int(value) if value.is_integer() else value


def compute_f4_holdings(company: dict[str, Any], judgments: JudgmentLookup, rules: RuleSet) -> dict[str, Any]:
    """④ 호황 이후 비전(규칙 v3.0). 수직계열화 0~8 + 다각화 매출 몫 0~8 + 그 분야의 힘 0~4.

    수직계열화는 AI 사슬 조건을 채운 칸 값(판매 1·자체 사용 0.5) 합 ÷ full_at × max 를 max 에서 자른다. 다각화는 AI 무관 매출 몫
    (제외 줄·층 밖 사업을 포함한 전체 매출 줄 기준)을 곡선으로, 그 분야의 힘은 AI 무관 부문 영업이익률을 곡선으로 바꾼다.
    칸·AI 사슬 조건·매출 금액·AI 무관 여부가 미확인이면 점수를 만들지 않는다(rules.md ④, 2.6)."""
    fid, basis = "F4", "holdings"
    spec = rules.factor(fid)
    judgment = judgments.get(company["company_id"], fid)
    if judgment is None:
        return factor_result(fid, score=None, status="needs_judgment", basis=basis,
                             pending=pending_info("judgment", "층별 보유표와 매출 줄 판정 입력 필요"))
    mismatch = _kind_mismatch(fid, judgment, rules, basis, "층별 보유표와 매출 줄 입력(holdings)")
    if mismatch is not None:
        return mismatch
    inputs = judgment["inputs"]
    layers = rules.payload["layers"]
    order = list(layers["order"])
    conditional = set(layers.get("ai_chain_conditional") or {})
    cells = inputs["cells"]
    calc: dict[str, Any] = {"cells": {layer: cells[layer]["cell"] for layer in order}}

    def pending(message: str) -> dict[str, Any]:
        return factor_result(fid, score=None, status="needs_judgment", basis=basis, judgment=judgment, calc=calc,
                             pending=pending_info("judgment", message))

    unknown = [layer for layer in order if cells[layer]["cell"] == "unknown"]
    if unknown:
        return pending(f"보유표 칸 {unknown} 이 미확인 — 칸 값을 추정하지 않는다")
    chain_unknown = [layer for layer in order if layer in conditional and cells[layer]["cell"] in ("sold", "self")
                     and cells[layer].get("ai_chain") == "unknown"]
    if chain_unknown:
        return pending(f"AI 사슬 조건 층 {chain_unknown} 이 AI 를 나르는지 미확인 — 수직계열화에 넣거나 빼지 않는다")
    lines = inputs["revenue_lines"]
    bad_lines = [line["line"] for line in lines if line["amount"] == "unknown" or line["non_ai"] == "unknown"]
    if bad_lines:
        return pending(f"매출 줄 {bad_lines} 의 금액이나 AI 무관 여부가 미확인 — AI 무관 몫을 어림하지 않는다")
    total = sum(float(line["amount"]) for line in lines)
    if total <= 0:
        return pending("매출 줄이 없다 — 층 매출 몫과 AI 무관 몫을 낼 수 없다")

    values = layers["cell_values"]
    counted = {layer: float(values[cells[layer]["cell"]]) for layer in order
               if float(values.get(cells[layer]["cell"], 0)) > 0 and (layer not in conditional or cells[layer].get("ai_chain") == "yes")}
    vertical_raw = sum(counted.values())
    v = spec["vertical"]
    vertical = min(float(v["max"]), vertical_raw / float(v["full_at"]) * float(v["max"]))
    share = sum(float(line["amount"]) for line in lines if line["non_ai"] == "yes") / total
    diversification = piecewise(spec["diversification"]["curve"], share)

    warnings: list[str] = []
    margin = inputs["non_ai_margin"]
    if share == 0:
        field, field_note = 0.0, "AI 무관 사업이 없다(해당 없음)"
    elif margin == "not_applicable":
        return pending("AI 무관 매출이 있는데 이익률이 '해당 없음'이다 — 부문 이익률이나 회사 전체 이익률을 적는다")
    elif margin == "unknown":
        return pending("AI 무관 부문 이익률과 회사 전체 이익률을 모두 확인하지 못했다")
    else:
        field = piecewise(spec["field_strength"]["curve"], float(margin))
        field_note = None
        if inputs.get("non_ai_margin_source") == "company":
            warnings.append("AI 무관 부문 이익률을 공시하지 않아 회사 전체 영업이익률로 대신했다")
    excluded = sorted({line["layer"] for line in lines if line["layer"] in (layers.get("excluded_lines") or {})})
    if excluded and spec["field_strength"].get("launch_uses_rank"):
        warnings.append(f"제외 줄 {excluded} 의 그 분야 순위 비교는 시장 정의표가 생긴 뒤 적용한다 — 지금은 이익률만 쓴다")

    weights = layer_weights(inputs, rules)
    if weights["zero_weight_sold"]:
        warnings.append(f"판매 칸 {weights['zero_weight_sold']} 에 붙은 매출 줄이 없어 층 매출 몫이 0 이다")
    preparing = {layer: cells[layer].get("trigger") for layer in order if cells[layer]["cell"] == "preparing"}
    lo, hi = rules.factor_range(fid)
    score = rules.round_score(max(lo, min(hi, vertical + diversification + field)))
    calc.update({
        "vertical_counted": {layer: _tidy(x) for layer, x in counted.items()},
        "vertical_raw": _tidy(vertical_raw), "vertical": _tidy(vertical),
        "non_ai_share": _tidy(share), "diversification": _tidy(diversification),
        "non_ai_margin": margin, "non_ai_margin_source": inputs.get("non_ai_margin_source"),
        "field_strength": _tidy(field), "field_strength_note": field_note,
        "layer_weights": {u: _tidy(w) for u, w in weights["weights"].items()},
        "primary_layer": weights["primary_layer"], "preparing": preparing, "score": score,
    })
    warnings.extend(carried_note(judgment))
    return factor_result(fid, score=score, status=_status_for(judgment), basis=basis, judgment=judgment, calc=calc,
                         warnings=warnings)


def within_window(day: str | None, as_of: str, months: int) -> bool:
    """`day` 가 기준일로부터 `months` 개월 안(기준일 포함, 기준일 뒤는 아님)인가. 끝난 싸움과 진행 중인 싸움을 가르는 창(rules.md 2.11)."""
    if day is None:
        return False
    end = date.fromisoformat(as_of)
    years, month0 = divmod(end.month - 1 - months, 12)
    year, month = end.year + years, month0 + 1
    start = date(year, month, min(end.day, monthrange(year, month)[1]))
    return start <= date.fromisoformat(day) <= end


LayerScore = tuple[float | None, dict[str, Any], str | None, list[str]]


def _layered(fid: str, basis: str, what: str, company: dict[str, Any], judgments: JudgmentLookup, rules: RuleSet,
             score_layer: Callable[[dict[str, Any], str], LayerScore]) -> dict[str, Any]:
    """층 단위 항목(②③)의 공통 합치기. 판매 층마다 판단 하나를 점수로 바꾸고 층 매출 몫으로 가중 평균해 한 번 반올림한다(rules.md 2.10).

    무게가 있는 층의 판단이 없거나 어느 층이 판정 대기면 항목 전체가 판정 대기다. 무게 0 판매 층의 판단 누락은 계산을 막지 않고
    경고로 남긴다(계약 검증이 막는다). 판매 층이 아닌 층의 판단은 계산에 쓰지 않는다."""
    cid = company["company_id"]
    holdings = judgments.get(cid, "F4")
    if holdings is None or holdings["kind"] != "holdings":
        return factor_result(fid, score=None, status="needs_judgment", basis=basis,
                             pending=pending_info("judgment", "④ 층별 보유표(holdings)가 있어야 층 매출 몫을 낸다"))
    w = layer_weights(holdings["inputs"], rules)
    if not w["ok"]:
        message = (f"④ 매출 줄 {w['unknown_lines']} 의 금액이 미확인 — 층 매출 몫을 어림하지 않는다" if w["unknown_lines"]
                   else "④ 보유표에 층에 붙은 매출 줄이 없다 — 층 매출 몫을 낼 수 없다")
        return factor_result(fid, score=None, status="needs_judgment", basis=basis, pending=pending_info("judgment", message))
    weights = w["weights"]
    spec = rules.payload["layers"]
    order = [*spec["order"], spec["outside"]["id"]]
    units = {j["layer"]: j for j in judgments.units(cid, fid)}
    calc: dict[str, Any] = {"layer_weights": {u: _tidy(x) for u, x in weights.items()}, "layers": {}}
    warnings: list[str] = []
    extra = [u for u in order if u in units and u not in weights]
    if extra:
        warnings.append(f"판매 층이 아닌 층 {extra} 의 판단은 계산에 쓰지 않는다")
    zero_missing = [u for u in order if u in weights and weights[u] == 0 and u not in units]
    if zero_missing:
        warnings.append(f"무게 0 판매 층 {zero_missing} 의 {what} 판단이 없다")
    missing = [u for u in order if weights.get(u, 0) > 0 and u not in units]
    if missing:
        return factor_result(fid, score=None, status="needs_judgment", basis=basis, calc=calc, warnings=warnings,
                             pending=pending_info("judgment", f"층 {missing} 의 {what} 판단이 없다"))
    scores: dict[str, float] = {}
    pendings: list[str] = []
    for u in order:
        if u not in weights or u not in units:
            continue
        score, detail, pending_message, layer_warnings = score_layer(units[u], u)
        calc["layers"][u] = {"judgment_id": units[u]["judgment_id"], "weight": _tidy(weights[u]), **detail,
                             "score": None if score is None else _tidy(score)}
        warnings.extend(f"{u}: {x}" for x in layer_warnings)
        warnings.extend(f"{u}: {x}" for x in carried_note(units[u]))
        if pending_message is not None:
            pendings.append(f"{u}: {pending_message}")
        else:
            scores[u] = float(score)
    if pendings:
        return factor_result(fid, score=None, status="needs_judgment", basis=basis, calc=calc, warnings=warnings,
                             pending=pending_info("judgment", "; ".join(pendings)))
    counted = [u for u in scores if weights[u] > 0]
    value = sum(weights[u] * scores[u] for u in counted) / sum(weights[u] for u in counted)
    lo, hi = rules.factor_range(fid)
    total = rules.round_score(max(lo, min(hi, value)))
    calc["score"] = total
    status = "carried_score" if any(units[u]["status"] == "carried" for u in counted) else "ok"
    return factor_result(fid, score=total, status=status, basis=basis, calc=calc, warnings=warnings)


def _f2_layer(j: dict[str, Any], layer: str, rules: RuleSet, as_of: str) -> LayerScore:
    """② 한 층의 세 경로. 벤치마크가 없는 층은 (패러다임 적응 + 표준 선점) × 배수다. 표준은 최근 2년 안에 새로 지원한 주요
    회사가 있을 때만 센다(rules.md ② 「표준의 시점」). 미확인 경로가 있으면 그 층은 판정 대기다."""
    spec = rules.factor("F2")
    inputs = j["inputs"]
    no_bench = layer in set(spec.get("no_benchmark_layers") or [])
    unknown = [k for k in ("leap", "adaptation") if inputs.get(k) == "unknown"]
    detail: dict[str, Any] = {"no_benchmark": no_bench}
    if unknown:
        return None, detail, f"경로 {unknown} 이 미확인 — 0 으로 두지 않는다", []
    months = int(rules.payload["layers"]["time_window_months"])
    standards = []
    for std in inputs["standards"]:
        active = within_window(std["latest_new_major_adopted_at"], as_of, months)
        standards.append({"name": std["name"], "support": std["support"], "holder": std["holder"],
                          "latest_new_major_adopted_at": std["latest_new_major_adopted_at"], "active": active,
                          "points": float(spec["standard"][std["support"]]) if active else 0.0})
    standard = max((s["points"] for s in standards), default=0.0)
    adaptation = float(spec["adaptation"][inputs["adaptation"]])
    detail.update(adaptation=_tidy(adaptation), standard=_tidy(standard), standards=standards)
    if no_bench:
        formula = spec["no_benchmark_formula"]
        parts = {"adaptation": adaptation, "standard": standard}
        score = sum(parts[k] for k in formula["sum_of"]) * float(formula["multiplier"])
        detail["multiplier"] = formula["multiplier"]
    else:
        leap = float(spec["leap"][inputs["leap"]])
        detail["leap"] = _tidy(leap)
        score = leap + adaptation + standard
    return score, detail, None, []


def compute_f2_layers(company: dict[str, Any], judgments: JudgmentLookup, rules: RuleSet, run: dict[str, Any]) -> dict[str, Any]:
    """② 게임체인저(규칙 v3.0). 판매 층마다 세 경로를 더하고 층 매출 몫으로 가중 평균한다."""
    return _layered("F2", "layer_paths", "세 경로", company, judgments, rules,
                    lambda j, layer: _f2_layer(j, layer, rules, run["as_of"]))


def _f3_layer(j: dict[str, Any], rules: RuleSet, as_of: str) -> LayerScore:
    """③ 한 층의 카운터 포지셔닝. 별도 수익모델 + 모방 불가능성 + 가속도에 관문 셋(작동 증거·모방·문 닫힘)을 댄다.

    상대가 지금 그 시장에 없으면(진행 중이 아님) 수익모델·모방은 0 이다. 가속도는 두 성장 배수의 비를 곡선으로 바꾸고, 값이 없으면
    0 에 '자료 없음', 출시 지연이면 0(감속)이다. 상대 유무·수익모델·모방이 미확인이면 그 층은 판정 대기다(rules.md ③, 2.11)."""
    spec = rules.factor("F3")
    inputs = j["inputs"]
    detail: dict[str, Any] = {"counterparty": inputs["counterparty"]}
    unknown = [k for k in ("counterparty_present", "revenue_model", "imitation") if inputs[k] == "unknown"]
    if unknown:
        return None, detail, f"{unknown} 이 미확인 — 0 으로 두지 않는다", []
    warnings: list[str] = []
    active = inputs["counterparty_present"] == "yes"
    revenue_model = float(spec["revenue_model"][inputs["revenue_model"]]) if active else 0.0
    imitation = float(spec["imitation"][inputs["imitation"]]) if active else 0.0
    if not active:
        warnings.append("수입원이 위협받는 상대가 지금 시장에 없다(끝난 싸움) — 수익모델·모방 불가능성 0")
    acc_spec = spec["acceleration"]
    a = inputs["acceleration"]
    ratio = None
    no_data = False
    if a["delayed"] == "yes":
        acceleration = 0.0
        warnings.append("출시 지연은 감속으로 본다 — 가속도 0")
    elif a["prior_multiple"] is None:
        acceleration, no_data = float(acc_spec.get("missing_points", 0)), True
        warnings.append("가속도 자료 없음 — 0 으로 계산하고 다음 수집에서 채운다")
    else:
        ratio = float(a["current_multiple"]) / float(a["prior_multiple"])
        acceleration = piecewise(acc_spec["curve"], ratio)
        cap = (acc_spec.get("tier_caps") or {}).get(a["tier"])
        if cap is not None and acceleration > float(cap):
            warnings.append(f"지표 단계 {a['tier']} 의 가속도는 최고 {cap}")
            acceleration = float(cap)
    raw = revenue_model + imitation + acceleration
    gates = spec["gates"]
    caps: dict[str, float] = {}
    if acceleration < float(gates["slow_cap"]["below"]):
        caps["slow"] = float(gates["slow_cap"]["cap"])
    if inputs["imitation"] != gates["imitation_gate"]["requires"]:
        caps["imitation"] = float(gates["imitation_gate"]["cap"])
    door = within_window(inputs["door_closed_at"], as_of, int(rules.payload["layers"]["time_window_months"]))
    if not door:
        caps["door_closed"] = float(gates["door_closed_gate"]["cap"])
    score = min([raw, *caps.values()])
    detail.update(active=active, revenue_model=_tidy(revenue_model), imitation=_tidy(imitation),
                  acceleration_ratio=None if ratio is None else _tidy(ratio), acceleration=_tidy(acceleration),
                  acceleration_no_data=no_data, raw=_tidy(raw), door_closed=door,
                  caps_applied=sorted(k for k, c in caps.items() if c < raw))
    return score, detail, None, warnings


def compute_f3_layers(company: dict[str, Any], judgments: JudgmentLookup, rules: RuleSet, run: dict[str, Any]) -> dict[str, Any]:
    """③ Last Mover (카운터 포지셔닝)(규칙 v3.0). 판매 층마다 매기고 층 매출 몫으로 가중 평균한다."""
    return _layered("F3", "layer_cp", "카운터 포지셔닝", company, judgments, rules,
                    lambda j, layer: _f3_layer(j, rules, run["as_of"]))
