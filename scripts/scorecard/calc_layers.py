# 규칙 v3.0 층 단위 계산: ④ 보유표의 매출 줄로 층 매출 몫(①②③ 의 무게)을 내고 ④ 수직계열화·다각화·그 분야의 힘을 계산한다
from __future__ import annotations

import re
from calendar import monthrange
from datetime import date
from typing import Any, Callable

from .calc_qual import _kind_mismatch, _status_for
from .calc_market import market_position
from .inputs import JudgmentLookup, ObsLookup, carried_note, factor_result, pending_info
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


_PART_NAMES = {"leap": "성능 도약", "adaptation": "패러다임 적응", "revenue_model": "수익모델", "imitation": "모방 불가능성"}


def _unit_names(rules: RuleSet, ids: list[str]) -> str:
    """경고 문구에 쓰는 층 이름. 2026-10-19 pilot9 출력 리뷰(N3): 초안 참고 줄에 층 id 목록이 파이썬 목록 그대로 실렸다.
    이름 안에 가운뎃점이 있어(시스템·네트워크) 목록은 쉼표로 잇는다(pilot10 출력 리뷰 F-2)."""
    spec = rules.payload["layers"]
    names = {**spec["labels"], spec["outside"]["id"]: spec["outside"]["label"]}
    return ", ".join(names.get(u, u) for u in ids)


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
    bad_lines = [line["line"] for line in lines if line["amount"] == "unknown"]
    if bad_lines:
        return pending(f"매출 줄 {bad_lines} 의 금액이 미확인 — AI 무관 몫을 어림하지 않는다")
    total = sum(float(line["amount"]) for line in lines)
    if total <= 0:
        return pending("매출 줄이 없다 — 층 매출 몫과 AI 무관 몫을 낼 수 없다")

    values = layers["cell_values"]
    counted = {layer: float(values[cells[layer]["cell"]]) for layer in order
               if float(values.get(cells[layer]["cell"], 0)) > 0 and (layer not in conditional or cells[layer].get("ai_chain") == "yes")}
    vertical_raw = sum(counted.values())
    v = spec["vertical"]
    vertical = min(float(v["max"]), vertical_raw / float(v["full_at"]) * float(v["max"]))
    # 2026-10-19 사용자 결정: 금액은 확인했지만 AI 무관 여부를 모르는 줄은 나쁜 쪽(AI 수요)에서 좋은 쪽으로 40% 간 값으로,
    # 그 금액의 40% 를 AI 무관으로 센다(rules.md 2.6·④). TSMC '기타' 줄은 구성이 공시되지 않는다.
    unknown_share = float(rules.payload["scoring"].get("unknown_share", 0))
    unsure = [line for line in lines if line["non_ai"] == "unknown"]
    share = (sum(float(line["amount"]) for line in lines if line["non_ai"] == "yes")
             + unknown_share * sum(float(line["amount"]) for line in unsure)) / total
    diversification = piecewise(spec["diversification"]["curve"], share)

    warnings: list[str] = []
    if unsure:
        warnings.append(f"매출 줄 {', '.join(line.get('label') or line['line'] for line in unsure)} 의 AI 무관 여부가 미확인 — 그 금액의 "
                        f"{unknown_share * 100:g}% 를 AI 무관으로 셌다")
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
        # 2026-10-19 pilot9 출력 리뷰(N3): '정의표가 생긴 뒤 적용한다' 는 미래 서술이고 미적용이 어느 쪽 결과인지 적지 않았다.
        labels = ", ".join(sorted({line.get("label") or line["layer"] for line in lines if line["layer"] in excluded}))
        warnings.append(f"제외 줄 {labels} 의 그 분야 순위는 이 실행에 그 시장의 정의표가 없어 재지 않았다 — 순위와 이익률 가운데 "
                        "높은 쪽을 쓰는 자리라 이익률만 쓴 지금 값은 낮은 쪽일 수 있다")

    weights = layer_weights(inputs, rules)
    if weights["zero_weight_sold"]:
        warnings.append(f"판매 칸 {_unit_names(rules, weights['zero_weight_sold'])} 에 붙은 매출 줄이 없어 층 매출 몫이 0 이다")
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

    무게가 있는 층의 판단이 없거나 어느 층이 판정 대기면 항목 전체가 판정 대기다. 무게 0 판매 층은 매기지 않는다(2026-10-15 사용자
    결정, ④ 보유표로만 센다). 그 층이나 판매 층이 아닌 층에 판단이 있어도 계산에 쓰지 않는다."""
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
        warnings.append(f"판매 층이 아닌 층 {_unit_names(rules, extra)} 의 판단은 계산에 쓰지 않는다")
    unused = [u for u in order if u in units and weights.get(u) == 0]
    if unused:
        warnings.append(f"매출 몫 0 층 {_unit_names(rules, unused)} 의 {what} 판단은 계산에 쓰지 않는다(④ 보유표로만 센다)")
    missing = [u for u in order if weights.get(u, 0) > 0 and u not in units]
    if missing:
        return factor_result(fid, score=None, status="needs_judgment", basis=basis, calc=calc, warnings=warnings,
                             pending=pending_info("judgment", f"층 {_unit_names(rules, missing)} 의 {what} 판단이 없다"))
    scores: dict[str, float] = {}
    pendings: list[str] = []
    for u in order:
        if not weights.get(u) or u not in units:
            continue
        score, detail, pending_message, layer_warnings = score_layer(units[u], u)
        calc["layers"][u] = {"judgment_id": units[u]["judgment_id"], "weight": _tidy(weights[u]), **detail,
                             "score": None if score is None else _tidy(score)}
        name = _unit_names(rules, [u])
        warnings.extend(f"{name}: {x}" for x in layer_warnings)
        warnings.extend(f"{name}: {x}" for x in carried_note(units[u]))
        if pending_message is not None:
            pendings.append(f"{name}: {pending_message}")
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
    detail: dict[str, Any] = {"no_benchmark": no_bench, "unknown_parts": unknown}
    warnings = [f"{_PART_NAMES[k]} 미확인 — 그 경로 만점의 {rules.payload['scoring']['unknown_share']:.0%}" for k in unknown]
    if unknown and rules.unknown_points(1) is None:
        return None, detail, f"경로 {unknown} 이 미확인 — 0 으로 두지 않는다", []

    def points(key: str) -> float:
        table = spec[key]
        return rules.unknown_points(max(table.values())) if inputs[key] == "unknown" else float(table[inputs[key]])

    months = int(rules.payload["layers"]["time_window_months"])
    standards = []
    for std in inputs["standards"]:
        active = within_window(std["latest_new_major_adopted_at"], as_of, months)
        standards.append({"name": std["name"], "support": std["support"], "holder": std["holder"],
                          "latest_new_major_adopted_at": std["latest_new_major_adopted_at"], "active": active,
                          "points": float(spec["standard"][std["support"]]) if active else 0.0})
    standard = max((s["points"] for s in standards), default=0.0)
    adaptation = points("adaptation")
    detail.update(adaptation=_tidy(adaptation), standard=_tidy(standard), standards=standards)
    if no_bench:
        formula = spec["no_benchmark_formula"]
        parts = {"adaptation": adaptation, "standard": standard}
        score = sum(parts[k] for k in formula["sum_of"]) * float(formula["multiplier"])
        detail["multiplier"] = formula["multiplier"]
    else:
        leap = points("leap")
        detail["leap"] = _tidy(leap)
        score = leap + adaptation + standard
    return score, detail, None, warnings


def compute_f2_layers(company: dict[str, Any], judgments: JudgmentLookup, rules: RuleSet, run: dict[str, Any]) -> dict[str, Any]:
    """② 게임체인저(규칙 v3.0). 판매 층마다 세 경로를 더하고 층 매출 몫으로 가중 평균한다."""
    return _layered("F2", "layer_paths", "세 경로", company, judgments, rules,
                    lambda j, layer: _f2_layer(j, layer, rules, run["as_of"]))


def _f3_layer(j: dict[str, Any], rules: RuleSet, as_of: str) -> LayerScore:
    """③ 한 층의 카운터 포지셔닝. 별도 수익모델 + 모방 불가능성 + 가속도에 관문 셋(작동 증거·모방·문 닫힘)을 댄다.

    상대가 지금 그 시장에 없으면(진행 중이 아님) 수익모델·모방은 0 이다. 가속도는 두 성장 배수의 비를 곡선으로 바꾸고, 값이 없으면
    만점의 40% 에 '자료 없음', 출시 지연이면 0(감속)이다. 수익모델·모방이 미확인이면 만점의 40% 이고(rules.md 2.6), 상대가 지금
    있는지가 미확인이면 진행 중인 싸움인지 가를 수 없어 그 층은 판정 대기다(rules.md ③, 2.11)."""
    spec = rules.factor("F3")
    inputs = j["inputs"]
    detail: dict[str, Any] = {"counterparty": inputs["counterparty"]}
    if inputs["counterparty_present"] == "unknown":
        return None, detail, "상대가 지금 시장에 있는지 미확인 — 진행 중인 싸움인지 가를 수 없다", []
    unknown = [k for k in ("revenue_model", "imitation") if inputs[k] == "unknown"]
    if unknown and rules.unknown_points(1) is None:
        return None, detail, f"{unknown} 이 미확인 — 0 으로 두지 않는다", []
    share = rules.payload["scoring"].get("unknown_share")
    warnings: list[str] = [f"{_PART_NAMES[k]} 미확인 — 만점의 {share:.0%}" for k in unknown]
    active = inputs["counterparty_present"] == "yes"

    def points(key: str) -> float:
        table = spec[key]
        return rules.unknown_points(max(table.values())) if inputs[key] == "unknown" else float(table[inputs[key]])

    revenue_model = points("revenue_model") if active else 0.0
    imitation = points("imitation") if active else 0.0
    if not active:
        warnings.append("수입원이 위협받는 상대가 지금 시장에 없다(끝난 싸움이거나 카운터 포지셔닝이 없음) — 수익모델·모방 불가능성 0")
    acc_spec = spec["acceleration"]
    a = inputs["acceleration"]
    ratio = None
    no_data = False
    if a["delayed"] == "yes":
        acceleration = 0.0
        warnings.append("출시 지연은 감속으로 본다 — 가속도 0")
    elif a["prior_multiple"] is None:
        missing = rules.unknown_points(acc_spec["max"])
        acceleration, no_data = (0.0 if missing is None else missing), True
        unknown.append("acceleration")
        warnings.append(f"가속도 자료 없음 — {_tidy(acceleration)} 로 계산하고 다음 수집에서 채운다")
    else:
        ratio = float(a["current_multiple"]) / float(a["prior_multiple"])
        acceleration = piecewise(acc_spec["curve"], ratio)
        cap = (acc_spec.get("tier_caps") or {}).get(a["tier"])
        if cap is not None and acceleration > float(cap):
            # 단계 이름의 괄호 예시('클라우드 전체 등')는 층마다 맞지 않아 뺀다(반도체 제조 층에도 붙었다).
            tier = re.sub(r"\(.*?\)", "", (spec["acceleration_tiers"]["tiers"].get(a["tier"]) or {}).get("label") or a["tier"]).strip()
            warnings.append(f"가속도 지표가 {tier} 단계라 최고 {cap}")
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
    detail.update(active=active, unknown_parts=unknown, revenue_model=_tidy(revenue_model), imitation=_tidy(imitation),
                  acceleration_ratio=None if ratio is None else _tidy(ratio), acceleration=_tidy(acceleration),
                  acceleration_no_data=no_data, raw=_tidy(raw), door_closed=door,
                  caps_applied=sorted(k for k, c in caps.items() if c < raw))
    return score, detail, None, warnings


def _f1_shared(inputs: dict[str, Any], parts: dict[str, Any], rules: RuleSet) -> tuple[float, dict[str, Any], list[str]]:
    """① 사업(묶음)의 A·B·C. A 는 참여자 효과·전환비용 가운데 높은 쪽, 한쪽만 미확인이면 아는 쪽, 둘 다 미확인이면 만점의 40%.
    B·C 가 미확인이면 각 만점의 40% 다(rules.md ①, 2.6)."""
    a = parts["A"]
    known = [float(a[k][inputs[k]]) for k in ("participant", "switching") if a[k][inputs[k]] is not None]
    unknown: list[str] = []
    if known:
        a_points = max(known)
    else:
        a_points = rules.unknown_points(a["max"])
        unknown.append("A")
    b_points = float(parts["B"]["levels"][inputs["pricing"]]) if inputs["pricing"] != "unknown" else None
    c_points = float(parts["C"]["levels"][inputs["substitutes"]]) if inputs["substitutes"] != "unknown" else None
    if b_points is None:
        b_points = rules.unknown_points(parts["B"]["max"])
        unknown.append("B")
    if c_points is None:
        c_points = rules.unknown_points(parts["C"]["max"])
        unknown.append("C")
    detail = {"participant": inputs["participant"], "switching": inputs["switching"], "A": _tidy(a_points),
              "pricing": inputs["pricing"], "B": _tidy(b_points), "substitutes": inputs["substitutes"], "C": _tidy(c_points)}
    return a_points + b_points + c_points, detail, unknown


def _partial_weight(comp: dict[str, Any], market: dict[str, Any], markets: dict[str, Any]) -> float:
    """2026-10-15 사용자 결정: 시장이 사업 매출의 일부만 재거나(coverage), 정의표가 시장의 일부만 재는 간접 자료(measure_fit proxy)면
    재는 만큼만 반영한다. 덮는 비율을 알면 그 비율, 모르면 규칙의 고정 비율이고 둘이 함께 걸리면 곱한다(rules.md ① 「부분 반영」)."""
    fixed = float(markets["partial_weight"])
    cov = comp.get("coverage")
    weight = 1.0 if cov is None else (fixed if cov == "partial" else float(cov))
    return weight * fixed if market.get("measure_fit") == "proxy" else weight


def _market_summary(pos: dict[str, Any] | None) -> dict[str, Any] | None:
    """결과에 남길 시장 위치 요약(점유율·순위·1년 변화·기간·관측 ID)."""
    if pos is None:
        return None
    keep = ("market_id", "label", "measure", "constituent", "period", "prior_period", "rank", "D_level", "outside", "observation_ids")
    out = {k: pos[k] for k in keep if k in pos}
    for k in ("share", "share_prior", "change_pp", "change_pp_low"):
        if k in pos:
            out[k] = _tidy(pos[k])
    return out


def compute_f1_business(company: dict[str, Any], judgments: JudgmentLookup, rules: RuleSet, run: dict[str, Any],
                        obs: ObsLookup | None = None) -> dict[str, Any]:
    """① 네트워크 효과(규칙 v3.0). 사업 점수 = A + B + C(사업·묶음 공유) + D + E(구성 사업마다), AI 수익화가 '예'가 아닌 구성
    사업은 상한 16. 층 점수는 그 층 구성 사업 점수의 매출 몫 평균, 회사 ① 은 층 점수의 층 매출 몫 가중 평균이다(rules.md 2.10, ①).

    D·E 는 구성 사업의 시장(규칙이 해시로 묶은 정의표)과 시장 관측으로 calc_market 이 잰다. 정의표가 없거나 시장을 정하지 않았거나
    자료가 모자라면 그 부분은 미확인(만점의 40%)이다. 판매 층의 매출 줄이 어느 사업에도 붙지 않았으면 판정 대기다."""
    fid, basis = "F1", "business"
    spec = rules.factor(fid)
    parts = spec["parts"]
    cid = company["company_id"]
    holdings = judgments.get(cid, "F4")
    if holdings is None or holdings["kind"] != "holdings":
        return factor_result(fid, score=None, status="needs_judgment", basis=basis,
                             pending=pending_info("judgment", "④ 층별 보유표(holdings)가 있어야 사업 매출 몫을 낸다"))
    w = layer_weights(holdings["inputs"], rules)
    if not w["ok"]:
        message = (f"④ 매출 줄 {w['unknown_lines']} 의 금액이 미확인 — 사업 매출 몫을 어림하지 않는다" if w["unknown_lines"]
                   else "④ 보유표에 층에 붙은 매출 줄이 없다 — 사업 매출 몫을 낼 수 없다")
        return factor_result(fid, score=None, status="needs_judgment", basis=basis, pending=pending_info("judgment", message))
    layers = rules.payload["layers"]
    order = [*layers["order"], layers["outside"]["id"]]
    lines = {line["line"]: line for line in holdings["inputs"]["revenue_lines"] if line["layer"] in order}
    businesses = judgments.units(cid, fid)
    attached = {line_id for b in businesses for comp in b["inputs"]["components"] for line_id in comp["lines"]}
    loose = sorted(line_id for line_id, line in lines.items() if float(line["amount"]) > 0 and line_id not in attached)
    calc: dict[str, Any] = {"layer_weights": {u: _tidy(x) for u, x in w["weights"].items()}, "businesses": {}}
    if not businesses or loose:
        message = (f"판매 층의 매출 줄 {loose} 이 어느 사업에도 붙지 않았다 — 사업 판단을 더한다" if businesses
                   else "사업 판단이 없다 — 판매 층의 매출 줄을 사업으로 나눠 판정한다")
        return factor_result(fid, score=None, status="needs_judgment", basis=basis, calc=calc, pending=pending_info("judgment", message))
    markets = spec.get("markets")
    cap = spec["ai_cap"]
    warnings: list[str] = []
    if not markets:
        warnings.append(f"시장 정의표가 없어 D·E 는 모든 사업이 미확인이다(각 {_tidy(rules.unknown_points(parts['D']['max']))})")
    by_layer: dict[str, list[tuple[float, float]]] = {}
    for b in businesses:
        shared, detail, unknown = _f1_shared(b["inputs"], parts, rules)
        comps = []
        de_unknown: set[str] = set()
        for comp in b["inputs"]["components"]:
            revenue = sum(float(lines[line_id]["amount"]) for line_id in comp["lines"])
            # 2026-10-15: 시장이 정해진 구성은 calc_market 이 D·E 를 잰다. 잴 수 없는 부분은 미확인(만점의 40%, rules.md 2.6).
            market = rules.market(comp["market"]) if markets and comp.get("market") else None
            pos = market_position(market, obs, cid, run["as_of"], rules) if market is not None and obs is not None else None
            weight = _partial_weight(comp, market, markets) if market is not None else 1.0
            points = {}
            for k in ("D", "E"):
                unknown_k = rules.unknown_points(parts[k]["max"])
                measured = pos[k] if pos is not None else None
                # 부분 반영: 반영 비율 × 잰 점수 + (1 − 반영 비율) × 미확인 점수. 잴 수 없으면 미확인 점수 그대로다.
                points[k] = unknown_k if measured is None else weight * measured + (1 - weight) * unknown_k
            d_points, e_points = points["D"], points["E"]
            de_unknown |= {k for k in ("D", "E") if pos is None or pos[k] is None}
            if markets and not comp.get("market"):
                warnings.append(f"구성 {comp['name']} 의 시장이 정해지지 않아 D·E 는 미확인이다")
            if pos is not None:
                warnings.extend(f"{comp['name']} — {n}" for n in pos["notes"])
            raw = shared + d_points + e_points
            capped = comp["ai_monetized"] != cap["requires"] and raw > float(cap["cap"])
            score = min(raw, float(cap["cap"])) if comp["ai_monetized"] != cap["requires"] else raw
            comps.append({"name": comp["name"], "layer": comp["layer"], "customer": comp["customer"], "lines": list(comp["lines"]),
                          "revenue": _tidy(revenue), "D": _tidy(d_points), "E": _tidy(e_points), "ai_monetized": comp["ai_monetized"],
                          # 2026-10-19: 묶음 안에서 구성마다 미확인 여부가 다르다(iPhone 은 측정, Services 는 미확인).
                          "unknown_parts": [k for k in ("D", "E") if pos is None or pos[k] is None],
                          "market": _market_summary(pos),
                          **({"weight": _tidy(weight), "D_measured": _tidy(pos["D"]) if pos and pos["D"] is not None else None,
                              "E_measured": _tidy(pos["E"]) if pos and pos["E"] is not None else None} if weight < 1 else {}),
                          "raw": _tidy(raw), "ai_cap_applied": capped, "score": _tidy(score)})
            by_layer.setdefault(comp["layer"], []).append((revenue, score))
        calc["businesses"][b["business"]] = {"judgment_id": b["judgment_id"], **detail, "shared": _tidy(shared),
                                            "unknown_parts": [*unknown, *sorted(de_unknown)], "components": comps}
        warnings.extend(f"{b['business']}: {x}" for x in carried_note(b))
    layer_scores = {}
    for layer, rows in by_layer.items():
        total = sum(r for r, _s in rows)
        layer_scores[layer] = sum(r * s for r, s in rows) / total if total > 0 else None
    calc["layer_scores"] = {u: (None if s is None else _tidy(s)) for u, s in layer_scores.items()}
    weights = w["weights"]
    counted = [u for u, s in layer_scores.items() if s is not None and weights.get(u, 0) > 0]
    value = sum(weights[u] * layer_scores[u] for u in counted) / sum(weights[u] for u in counted)
    lo, hi = rules.factor_range(fid)
    total = rules.round_score(max(lo, min(hi, value)))
    calc["score"] = total
    status = "carried_score" if any(b["status"] == "carried" for b in businesses) else "ok"
    return factor_result(fid, score=total, status=status, basis=basis, calc=calc, warnings=warnings)


def compute_f3_layers(company: dict[str, Any], judgments: JudgmentLookup, rules: RuleSet, run: dict[str, Any]) -> dict[str, Any]:
    """③ Last Mover (카운터 포지셔닝)(규칙 v3.0). 판매 층마다 매기고 층 매출 몫으로 가중 평균한다."""
    return _layered("F3", "layer_cp", "카운터 포지셔닝", company, judgments, rules,
                    lambda j, layer: _f3_layer(j, rules, run["as_of"]))
