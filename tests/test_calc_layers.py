# 규칙 v3.0 ④ 보유표 계산과 층 매출 몫(계획 S6) — 기준점·제외 줄·층 밖 사업·AI 사슬 조건·판정 대기를 잠근다
from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard.calc_layers import (_f3_layer, compute_f1_business, compute_f2_layers, compute_f3_layers,  # noqa: E402
                                   compute_f4_holdings, layer_weights)
from scorecard.engine import compute_company  # noqa: E402
from scorecard.inputs import JudgmentLookup, ObsLookup  # noqa: E402
from scorecard.rules import load_rules  # noqa: E402
from scorecard.schema import validate_companies, validate_judgments  # noqa: E402

V30 = load_rules("v3.0")
ORDER = V30.payload["layers"]["order"]
COMPANIES = validate_companies(json.loads((ROOT / "scorecard" / "companies.json").read_text(encoding="utf-8")))
AMAZON = COMPANIES["amazon"]


def line(line_id: str, layer: str, amount, non_ai: str = "yes") -> dict:
    return {"line": line_id, "label": line_id, "amount": amount, "period": "2025-07-01~2026-06-30", "layer": layer,
            "non_ai": non_ai, "evidence_ids": []}


def holdings(**kw) -> dict:
    """rules.md 2.10 의 설명용 예시: 온라인 스토어 40·제3자 판매자 30(사용자 플랫폼), AWS 30(클라우드)."""
    cells = {layer: {"cell": "none", "evidence_ids": []} for layer in ORDER}
    cells["cloud"] = {"cell": "sold", "evidence_ids": []}
    cells["user_platform"] = {"cell": "sold", "ai_chain": "yes", "evidence_ids": []}
    base = {"cells": cells, "currency": "USD", "non_ai_margin": 0.1, "non_ai_margin_source": "segment",
            "revenue_lines": [line("online_stores", "user_platform", 40), line("third_party", "user_platform", 30),
                              line("aws", "cloud", 30, "no")]}
    base.update(kw)
    return base


def judgment(inputs: dict, status: str = "new", kind: str = "holdings") -> dict:
    j = {"judgment_id": "amazon.F4", "company_id": "amazon", "factor": "F4", "kind": kind, "score": None, "inputs": inputs,
         "evidence": ["판정 문장이다."], "reviewer": "agent", "reviewed_at": "2026-10-14", "status": status}
    if status == "carried":
        j["carried_from"] = "x"
    return j


def compute(inputs: dict, **kw) -> dict:
    j = judgment(inputs, **kw)
    validate_judgments({"schema": "scorecard.judgments/1", "run_id": "t", "items": [j]}, COMPANIES, V30.payload, "t")
    return compute_f4_holdings(AMAZON, JudgmentLookup([j]), V30)


def set_cells(h: dict, **cells) -> dict:
    h = copy.deepcopy(h)
    for layer, value in cells.items():
        h["cells"][layer] = value if isinstance(value, dict) else {"cell": value, "evidence_ids": []}
    return h


class LayerWeightTest(unittest.TestCase):
    def test_40_30_30_example(self):
        w = layer_weights(holdings(), V30)
        self.assertTrue(w["ok"])
        self.assertAlmostEqual(w["weights"]["user_platform"], 0.7)
        self.assertAlmostEqual(w["weights"]["cloud"], 0.3)
        self.assertEqual(w["primary_layer"], "user_platform")

    def test_excluded_line_is_outside_the_denominator_and_outside_line_has_weight(self):
        h = holdings()
        h["revenue_lines"] += [line("launch", "rocket_launch", 50), line("starlink", "outside", 100)]
        w = layer_weights(h, V30)
        self.assertNotIn("rocket_launch", w["weights"])
        self.assertAlmostEqual(w["weights"]["outside"], 0.5)
        self.assertAlmostEqual(w["weights"]["user_platform"], 0.35)
        self.assertEqual(w["primary_layer"], "user_platform", "층 밖 사업은 주 층이 아니다")

    def test_sold_layer_without_lines_has_zero_weight(self):
        h = set_cells(holdings(), model="sold")
        w = layer_weights(h, V30)
        self.assertEqual((w["weights"]["model"], w["zero_weight_sold"]), (0.0, ["model"]))

    def test_unknown_amount_gives_no_weights(self):
        h = holdings()
        h["revenue_lines"][2]["amount"] = "unknown"
        w = layer_weights(h, V30)
        self.assertEqual((w["ok"], w["unknown_lines"], w["weights"]), (False, ["aws"], {}))


class HoldingsScoreTest(unittest.TestCase):
    def test_reference_points(self):
        # 칸 합 7(판매 6 + 자체 사용 2 칸) → 수직계열화 8, AI 무관 25% → 다각화 4, 이익률 10% → 힘 2
        h = set_cells(holdings(), foundry="self", chip_design="sold", systems="self", dev_platform="sold", model="sold",
                      application="sold")
        h["revenue_lines"] = [line("ads", "user_platform", 25), line("aws", "cloud", 75, "no")]
        r = compute(h)
        self.assertEqual((r["status"], r["basis"]), ("ok", "holdings"))
        c = r["calc"]
        self.assertEqual((c["vertical_raw"], c["vertical"], c["non_ai_share"], c["diversification"], c["field_strength"]),
                         (7, 8, 0.25, 4, 2))
        self.assertEqual(r["score"], 14)

    def test_vertical_proportional_and_cap(self):
        h = set_cells(holdings(), chip_design="self", model="self", dev_platform="self")   # 1 + 1 + 0.5 × 3 = 3.5
        r = compute(h)
        self.assertEqual((r["calc"]["vertical_raw"], r["calc"]["vertical"]), (3.5, 4))
        h = set_cells(holdings(), **{layer: "sold" for layer in ORDER if layer not in ("power", "data_platform", "device")})
        h["cells"]["user_platform"]["ai_chain"] = "yes"
        r = compute(h)
        self.assertEqual((r["calc"]["vertical_raw"], r["calc"]["vertical"]), (8, 8), "합 8 은 8 에서 자른다")

    def test_ai_chain_unmet_cell_is_not_vertical_but_keeps_weight(self):
        h = set_cells(holdings(), user_platform={"cell": "sold", "ai_chain": "no", "evidence_ids": []})
        r = compute(h)
        self.assertEqual(r["calc"]["vertical_counted"], {"cloud": 1})
        self.assertAlmostEqual(r["calc"]["layer_weights"]["user_platform"], 0.7)

    def test_power_layer_counts_only_when_it_feeds_ai_data_centers(self):
        # 2026-10-14 사용자 결정: 전력은 AI 사슬 조건 층이다. 전력회사에만 팔면 칸은 판매여도 수직계열화에 세지 않는다.
        utility = set_cells(holdings(), power={"cell": "sold", "ai_chain": "no", "evidence_ids": []})
        utility["revenue_lines"].append(line("storage", "power", 20))
        r = compute(utility)
        self.assertNotIn("power", r["calc"]["vertical_counted"])
        self.assertAlmostEqual(r["calc"]["layer_weights"]["power"], 0.2 / 1.2, places=6)
        feeds = set_cells(utility, power={"cell": "sold", "ai_chain": "yes", "evidence_ids": []})
        self.assertEqual(compute(feeds)["calc"]["vertical_counted"]["power"], 1)
        with self.assertRaisesRegex(Exception, "ai_chain\\(AI 사슬로 작동하는가\\)"):
            compute(set_cells(utility, power="sold"))

    def test_outside_and_excluded_lines_count_in_diversification_not_vertical(self):
        h = holdings()
        h["revenue_lines"] = [line("aws", "cloud", 50, "no"), line("launch", "rocket_launch", 25), line("starlink", "outside", 25)]
        r = compute(h)
        self.assertEqual(r["calc"]["non_ai_share"], 0.5)
        self.assertEqual(r["calc"]["diversification"], 8)
        self.assertEqual(r["calc"]["vertical_counted"], {"cloud": 1, "user_platform": 1})
        self.assertTrue(any("그 분야 순위 비교는 시장 정의표가 생긴 뒤" in w for w in r["warnings"]))

    def test_margin_substitute_and_no_non_ai_business(self):
        r = compute(holdings(non_ai_margin=0.3, non_ai_margin_source="company"))
        self.assertEqual(r["calc"]["field_strength"], 4)
        self.assertIn("회사 전체 영업이익률로 대신했다", " ".join(r["warnings"]))
        h = holdings(non_ai_margin=0.3)
        for x in h["revenue_lines"]:
            x["non_ai"] = "no"
        r = compute(h)
        self.assertEqual((r["calc"]["field_strength"], r["calc"]["field_strength_note"]), (0, "AI 무관 사업이 없다(해당 없음)"))

    def test_pending_cases(self):
        h_unknown_amount = holdings()
        h_unknown_amount["revenue_lines"][0]["amount"] = "unknown"
        h_unknown_non_ai = holdings()
        h_unknown_non_ai["revenue_lines"][1]["non_ai"] = "unknown"
        h_na = holdings(non_ai_margin="not_applicable")
        del h_na["non_ai_margin_source"]
        h_unknown_margin = holdings(non_ai_margin="unknown")
        del h_unknown_margin["non_ai_margin_source"]
        cases = [
            (set_cells(holdings(), model="unknown"), "보유표 칸 \\['model'\\] 이 미확인"),
            (set_cells(holdings(), user_platform={"cell": "sold", "ai_chain": "unknown", "evidence_ids": []}), "AI 를 나르는지 미확인"),
            (h_unknown_amount, "금액이나 AI 무관 여부가 미확인"),
            (h_unknown_non_ai, "금액이나 AI 무관 여부가 미확인"),
            (h_na, "이익률이 '해당 없음'"),
            (h_unknown_margin, "모두 확인하지 못했다"),
            (holdings(revenue_lines=[]), "매출 줄이 없다"),
        ]
        for inputs, pattern in cases:
            with self.subTest(pattern=pattern):
                r = compute(inputs)
                self.assertEqual((r["status"], r["score"]), ("needs_judgment", None))
                self.assertRegex(r["pending"]["message"], pattern)

    def test_carried_survival_judgment_is_not_scored(self):
        survival = {"layers": {k: "none" for k in ("chip", "server", "platform", "cloud", "model", "app")}, "primary_layer": None,
                    "non_ai_revenue_share": 0.3}
        r = compute_f4_holdings(AMAZON, JudgmentLookup([judgment(survival, status="carried", kind="survival")]), V30)
        self.assertEqual((r["status"], r["score"]), ("needs_judgment", None))
        self.assertIn("이어받은 점수는 쓰지 않는다", r["pending"]["message"])

    def test_engine_dispatches_holdings_mode(self):
        j = judgment(holdings())
        out = compute_company(AMAZON, ObsLookup([]), JudgmentLookup([j]), V30, {"as_of": "2026-10-14", "decisions": []})
        self.assertEqual((out["F4"]["basis"], out["F4"]["status"]), ("holdings", "ok"))


RUN = {"as_of": "2026-10-14", "decisions": []}
TEXT = ["판정 문장이다."]


def unit(factor: str, kind: str, layer: str, inputs: dict, status: str = "new") -> dict:
    j = {"judgment_id": f"amazon.{factor}.{layer}", "company_id": "amazon", "factor": factor, "layer": layer, "kind": kind,
         "score": None, "inputs": inputs, "evidence": TEXT, "reviewer": "agent", "reviewed_at": "2026-10-14", "status": status}
    if status == "carried":
        j["carried_from"] = "x"
    return j


def run_layers(fn, *units: dict, h: dict | None = None) -> dict:
    items = [judgment(h or holdings()), *units]
    validate_judgments({"schema": "scorecard.judgments/1", "run_id": "t", "items": items}, COMPANIES, V30.payload, "t")
    return fn(AMAZON, JudgmentLookup(items), V30, RUN)


def std(adopted_at: str | None, support: str = "three_plus") -> dict:
    return {"name": "규격", "holder": "neutral", "support": support, "first_adopted": "2023-01-01",
            "latest_new_major_adopter": None if adopted_at is None else "주요 회사", "latest_new_major_adopted_at": adopted_at,
            "evidence_ids": []}


def chip_holdings() -> dict:
    h = set_cells(holdings(), chip_design="sold")
    h["revenue_lines"] = [line("chips", "chip_design", 100, "no")]
    return h


class F2LayersTest(unittest.TestCase):
    def test_no_benchmark_layers_double_and_weighted_average(self):
        cloud = unit("F2", "layer_paths", "cloud", {"adaptation": "adopted", "standards": [std("2026-01-01")]})
        platform = unit("F2", "layer_paths", "user_platform", {"adaptation": "beta", "standards": []})
        r = run_layers(compute_f2_layers, cloud, platform)
        self.assertEqual((r["status"], r["basis"]), ("ok", "layer_paths"))
        self.assertEqual((r["calc"]["layers"]["cloud"]["score"], r["calc"]["layers"]["user_platform"]["score"]), (14, 4))
        self.assertEqual(r["score"], 7)   # 0.7 × 4 + 0.3 × 14

    def test_standard_counts_only_within_two_years(self):
        def standard_points(adopted_at):
            cloud = unit("F2", "layer_paths", "cloud", {"adaptation": "none", "standards": [std(adopted_at)]})
            platform = unit("F2", "layer_paths", "user_platform", {"adaptation": "none", "standards": []})
            return run_layers(compute_f2_layers, cloud, platform)["calc"]["layers"]["cloud"]["standard"]
        self.assertEqual(standard_points("2024-09-13"), 0, "25개월 전이면 굳은 규격")
        self.assertEqual(standard_points("2024-11-14"), 3, "23개월 전이면 퍼지는 중")
        self.assertEqual(standard_points("2024-10-14"), 3, "정확히 2년 전 같은 날은 창 안")
        self.assertEqual(standard_points("2026-10-15"), 0, "기준일 뒤 사건은 세지 않는다")

    def test_benchmark_layer_adds_leap(self):
        chip = unit("F2", "layer_paths", "chip_design",
                    {"leap": "generation_gap", "gap_months": 12, "adaptation": "doubled", "adoption_multiple": 2.1,
                     "standards": [std("2026-03-01", "must_be_compatible")]})
        r = run_layers(compute_f2_layers, chip, h=chip_holdings())
        self.assertEqual((r["calc"]["layers"]["chip_design"]["leap"], r["score"]), (10, 20))

    def test_missing_unknown_and_extra_layers(self):
        cloud = unit("F2", "layer_paths", "cloud", {"adaptation": "adopted", "standards": []})
        r = run_layers(compute_f2_layers, cloud)
        self.assertEqual((r["status"], r["score"]), ("needs_judgment", None))
        self.assertIn("층 ['user_platform'] 의 세 경로 판단이 없다", r["pending"]["message"])
        # 2026-10-14 사용자 결정: 미확인 경로는 판정 대기가 아니라 그 경로 만점의 40% 에 미확인 표시(rules.md 2.6)
        unknown = unit("F2", "layer_paths", "user_platform", {"adaptation": "unknown", "standards": []})
        r = run_layers(compute_f2_layers, cloud, unknown)
        layer = r["calc"]["layers"]["user_platform"]
        self.assertEqual((r["status"], layer["adaptation"], layer["score"], layer["unknown_parts"]), ("ok", 2, 4, ["adaptation"]))
        self.assertIn("user_platform: adaptation 미확인 — 그 경로 만점의 40%", r["warnings"])
        leap = unit("F2", "layer_paths", "chip_design", {"leap": "unknown", "adaptation": "none", "standards": []})
        self.assertEqual(run_layers(compute_f2_layers, leap, h=chip_holdings())["score"], 4)
        platform = unit("F2", "layer_paths", "user_platform", {"adaptation": "adopted", "standards": []})
        model = unit("F2", "layer_paths", "model", {"leap": "first", "adaptation": "adopted", "standards": []})
        h = set_cells(holdings(), device={"cell": "sold", "ai_chain": "yes", "evidence_ids": []})
        r = run_layers(compute_f2_layers, cloud, platform, model, h=h)
        self.assertEqual(r["status"], "ok")
        self.assertIn("판매 층이 아닌 층 ['model'] 의 판단은 계산에 쓰지 않는다", r["warnings"])
        self.assertIn("무게 0 판매 층 ['device'] 의 세 경로 판단이 없다", r["warnings"])

    def test_needs_holdings(self):
        r = compute_f2_layers(AMAZON, JudgmentLookup([]), V30, RUN)
        self.assertIn("④ 층별 보유표(holdings)가 있어야", r["pending"]["message"])


def cp(rm: str = "recovered", im: str = "blocked", prior=1.0, current=1.2, tier: str = "b", door=None, present: str = "yes",
       delayed: str = "no") -> dict:
    basis = "none" if prior is None else "yoy_quarter"
    return {"strategy": "전략", "counterparty": "상대" if present != "no" else None, "counterparty_present": present,
            "revenue_model": rm, "imitation": im, "door_closed_at": door,
            "acceleration": {"metric": None if prior is None else "지표", "tier": "e" if prior is None else tier, "basis": basis,
                             "prior_multiple": prior, "current_multiple": current, "delayed": delayed, "evidence_ids": []}}


def f3_layer(inputs: dict) -> tuple:
    return _f3_layer(unit("F3", "layer_cp", "cloud", inputs), V30, RUN["as_of"])


class F3LayersTest(unittest.TestCase):
    def test_acceleration_ratio_points(self):
        for prior, current, expected in ((1.409, 1.480, 4.51), (2.180, 2.166, 2.81), (9, 13, 6), (1.0, 0.85, 0)):
            with self.subTest(prior=prior, current=current):
                _score, detail, _p, _w = f3_layer(cp(prior=prior, current=current))
                self.assertAlmostEqual(detail["acceleration"], expected, places=2)

    def test_tier_c_cap_missing_values_and_delay(self):
        _s, detail, _p, warnings = f3_layer(cp(prior=9, current=13, tier="c"))
        self.assertEqual(detail["acceleration"], 3)
        _s, detail, _p, warnings = f3_layer(cp(prior=None, current=None))
        self.assertEqual((detail["acceleration"], detail["acceleration_no_data"], detail["unknown_parts"]), (2.4, True, ["acceleration"]))
        self.assertIn("가속도 자료 없음 — 2.4 로 계산", " ".join(warnings))
        _s, detail, _p, warnings = f3_layer(cp(delayed="yes"))
        self.assertEqual(detail["acceleration"], 0)
        self.assertIn("출시 지연은 감속", " ".join(warnings))

    def test_three_gates(self):
        slow = 0.9 + 2.9 / 30   # 가속도 2.9
        self.assertEqual(f3_layer(cp(prior=1.0, current=slow, door="2026-06-01"))[0], 12, "가속도 3 미만이면 최고 12")
        self.assertEqual(f3_layer(cp(im="conflict_pending", door="2026-06-01"))[0], 15, "모방 5 면 최고 15")
        self.assertEqual(f3_layer(cp())[0], 18, "문 닫힘 증거가 없으면 최고 18")
        self.assertEqual(f3_layer(cp(door="2023-01-01"))[0], 18, "2년 전보다 오래된 문 닫힘 증거는 세지 않는다")
        score, detail, _p, _w = f3_layer(cp(door="2026-06-01"))
        self.assertEqual((score, detail["caps_applied"]), (20, []))

    def test_finished_contest_zeroes_revenue_model_and_imitation(self):
        score, detail, _p, warnings = f3_layer(cp(present="no", door="2026-06-01"))
        self.assertEqual((detail["revenue_model"], detail["imitation"], detail["acceleration"], score), (0, 0, 6, 6))
        self.assertIn("끝난 싸움", " ".join(warnings))

    def test_unknown_parts_get_forty_percent_and_company_is_weighted(self):
        score, detail, pending, _w = f3_layer(cp(rm="unknown", im="unknown", door="2026-06-01"))
        self.assertIsNone(pending)
        self.assertEqual((detail["revenue_model"], detail["imitation"], detail["unknown_parts"]), (2.4, 3.2, ["revenue_model", "imitation"]))
        self.assertAlmostEqual(score, 2.4 + 3.2 + 6)   # 모방이 미확인이라 '8점일 때만 16 이상' 관문도 걸릴 수 있다
        self.assertEqual(f3_layer(cp(rm="recovered", im="unknown", door="2026-06-01"))[0], 15, "미확인 모방은 모방 관문을 통과하지 못한다")
        self.assertIsNotNone(f3_layer(cp(present="unknown"))[2], "상대가 지금 있는지 미확인이면 판정 대기")
        cloud = unit("F3", "layer_cp", "cloud", cp(door="2026-06-01"))                       # 20
        platform = unit("F3", "layer_cp", "user_platform", cp(prior=None, current=None))      # 6 + 8 + 0 → 작동 증거 관문 12
        r = run_layers(compute_f3_layers, cloud, platform)
        self.assertEqual((r["calc"]["layers"]["cloud"]["score"], r["calc"]["layers"]["user_platform"]["score"]), (20, 12))
        self.assertEqual(r["score"], 14.4)   # 0.7 × 12 + 0.3 × 20

    def test_engine_dispatches_layer_modes(self):
        items = [judgment(holdings()),
                 unit("F2", "layer_paths", "cloud", {"adaptation": "adopted", "standards": []}),
                 unit("F2", "layer_paths", "user_platform", {"adaptation": "adopted", "standards": []}),
                 unit("F3", "layer_cp", "cloud", cp()), unit("F3", "layer_cp", "user_platform", cp())]
        out = compute_company(AMAZON, ObsLookup([]), JudgmentLookup(items), V30, RUN)
        self.assertEqual((out["F2"]["basis"], out["F2"]["score"]), ("layer_paths", 8))
        self.assertEqual((out["F3"]["basis"], out["F3"]["score"]), ("layer_cp", 18))


def comp(name: str, layer: str, lines: list[str], customer: str = "consumer", ai: str = "partial") -> dict:
    return {"name": name, "layer": layer, "customer": customer, "lines": lines, "market": None, "ai_monetized": ai}


def business(bid: str, comps: list[dict], participant="partial", switching="stay_unmeasured", pricing="no_change",
             substitutes="gap_remains", **kw) -> dict:
    inputs = {"components": comps, "participant": participant, "switching": switching, "pricing": pricing,
              "substitutes": substitutes, **kw}
    if len(comps) > 1:
        inputs.setdefault("bundle_reason", "하나를 떠나면 다른 서비스의 편익도 잃는다")
    j = {"judgment_id": f"amazon.F1.{bid}", "company_id": "amazon", "factor": "F1", "business": bid, "kind": "business",
         "score": None, "inputs": inputs, "evidence": TEXT, "reviewer": "agent", "reviewed_at": "2026-10-14", "status": "new"}
    return j


def run_f1(*businesses: dict, h: dict | None = None, rules=V30) -> dict:
    items = [judgment(h or holdings()), *businesses]
    validate_judgments({"schema": "scorecard.judgments/1", "run_id": "t", "items": items}, COMPANIES, V30.payload, "t")
    return compute_f1_business(AMAZON, JudgmentLookup(items), rules, RUN)


class F1BusinessTest(unittest.TestCase):
    def test_layer_then_company_average_equals_business_revenue_average(self):
        # rules.md 2.10 예시의 구성: 온라인 스토어 40·제3자 판매자 30(사용자 플랫폼), AWS 30(클라우드). D·E 는 미확인 1.6 + 1.6
        stores = business("online_stores", [comp("온라인 스토어", "user_platform", ["online_stores"])],
                          participant="partial", pricing="no_change", substitutes="gap_remains")            # 4 + 2 + 1 + 3.2 = 10.2
        sellers = business("third_party", [comp("제3자 판매자", "user_platform", ["third_party"], "trade")],
                           participant="core_measured", pricing="sustained_or_short_explained", pricing_growth_quarters=8,
                           pricing_explained="no", substitutes="no_substitute")                                # 6 + 3 + 2 + 3.2 = 14.2
        aws = business("aws", [comp("AWS", "cloud", ["aws"], "work")], participant="none", switching="stay_unmeasured",
                       substitutes="no_substitute")                                                            # 4 + 2 + 2 + 3.2 = 11.2
        r = run_f1(stores, sellers, aws)
        self.assertEqual((r["status"], r["basis"]), ("ok", "business"))
        self.assertEqual([c["score"] for b in ("online_stores", "third_party", "aws") for c in r["calc"]["businesses"][b]["components"]],
                         [10.2, 14.2, 11.2])
        self.assertAlmostEqual(r["calc"]["layer_scores"]["user_platform"], (40 * 10.2 + 30 * 14.2) / 70, places=5)
        self.assertEqual(r["score"], 11.7)   # 0.7 × 11.914 + 0.3 × 11.2 = 0.4 × 10.2 + 0.3 × 14.2 + 0.3 × 11.2
        self.assertIn("시장 정의표가 없어 D·E 는 모든 사업이 미확인이다(각 1.6)", r["warnings"])

    def test_bundle_shares_a_to_c_across_layers(self):
        bundle = business("marketplace", [comp("온라인 스토어", "user_platform", ["online_stores", "third_party"]),
                                          comp("AWS", "cloud", ["aws"], "work")], participant="core_measured")
        r = run_f1(bundle)
        scores = [c["score"] for c in r["calc"]["businesses"]["marketplace"]["components"]]
        self.assertEqual(scores, [12.2, 12.2])   # 6 + 2 + 1 + 3.2, 묶음은 A~C 를 함께 쓴다
        self.assertEqual(r["score"], 12.2)

    def test_unknown_parts_get_forty_percent(self):
        b = business("all", [comp("전체", "user_platform", ["online_stores", "third_party"]), comp("AWS", "cloud", ["aws"], "work")],
                     participant="unknown", switching="unknown", pricing="unknown", substitutes="unknown")
        r = run_f1(b)
        d = r["calc"]["businesses"]["all"]
        self.assertEqual((d["A"], d["B"], d["C"], d["unknown_parts"]), (2.4, 1.6, 0.8, ["A", "B", "C", "D", "E"]))
        self.assertEqual(r["score"], 8)   # 2.4 + 1.6 + 0.8 + 1.6 + 1.6
        one_side = business("all", [comp("전체", "user_platform", ["online_stores", "third_party"]), comp("AWS", "cloud", ["aws"], "work")],
                            participant="unknown", switching="stay_measured")
        self.assertEqual(run_f1(one_side)["calc"]["businesses"]["all"]["A"], 6, "한쪽만 미확인이면 아는 쪽")

    def test_ai_cap_per_component(self):
        capped_rules = copy.deepcopy(V30)
        capped_rules.payload["factors"]["F1"]["ai_cap"]["cap"] = 10
        monetized = comp("AWS", "cloud", ["aws"], "work", ai="yes")
        monetized.update({"ai_monetized_measure": "revenue", "ai_monetized_share": 0.6, "ai_monetized_period": "2026Q2",
                          "ai_separate_billing_evidence": ["EV-amazon-001"], "ai_price_uplift_evidence": ["EV-amazon-002"]})
        b = business("all", [comp("전체", "user_platform", ["online_stores", "third_party"]), monetized], participant="core_measured")
        r = run_f1(b, rules=capped_rules)
        comps = r["calc"]["businesses"]["all"]["components"]
        self.assertEqual([(c["raw"], c["ai_cap_applied"], c["score"]) for c in comps], [(12.2, True, 10), (12.2, False, 12.2)])

    def test_pending_cases(self):
        r = run_f1(business("stores", [comp("온라인 스토어", "user_platform", ["online_stores"])]))
        self.assertIn("['aws', 'third_party'] 이 어느 사업에도 붙지 않았다", r["pending"]["message"])
        self.assertIn("사업 판단이 없다", run_f1()["pending"]["message"])
        self.assertIn("④ 층별 보유표(holdings)가 있어야", compute_f1_business(AMAZON, JudgmentLookup([]), V30, RUN)["pending"]["message"])

    def test_excluded_lines_need_no_business(self):
        h = holdings()
        h["revenue_lines"].append(line("launch", "rocket_launch", 50))
        b = business("all", [comp("전체", "user_platform", ["online_stores", "third_party"]), comp("AWS", "cloud", ["aws"], "work")])
        self.assertEqual(run_f1(b, h=h)["status"], "ok", "로켓 발사 줄은 ① 에서 빠진다")

    def test_engine_dispatches_business_mode(self):
        b = business("all", [comp("전체", "user_platform", ["online_stores", "third_party"]), comp("AWS", "cloud", ["aws"], "work")])
        out = compute_company(AMAZON, ObsLookup([]), JudgmentLookup([judgment(holdings()), b]), V30, RUN)
        self.assertEqual((out["F1"]["basis"], out["F1"]["status"]), ("business", "ok"))


if __name__ == "__main__":
    unittest.main()
