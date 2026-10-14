# 규칙 v3.0 층 단위 계산: ④ 보유표의 매출 줄로 층 매출 몫(①②③ 의 무게)을 내고 ④ 수직계열화·다각화·그 분야의 힘을 계산한다
from __future__ import annotations

from typing import Any

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
