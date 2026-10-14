# 규칙 v3.0 판단 키(층·사업)와 다섯 판정 재료의 검증(계획 S4) — 단위·중복·입력 모양·매출 줄 교차·근거 교차·조회·재판단 검사를 잠근다
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard.inputs import JudgmentLookup  # noqa: E402
from scorecard.rules import load_rules  # noqa: E402
from scorecard.schema import SchemaError, validate_companies, validate_cross_refs, validate_judgments, validate_proposals  # noqa: E402
from scorecard.validate import rejudge_findings  # noqa: E402

V30 = load_rules("v3.0")
V21 = load_rules("v2.1")
ORDER = V30.payload["layers"]["order"]
COMPANIES = validate_companies(json.loads((ROOT / "scorecard" / "companies.json").read_text(encoding="utf-8")))


def judgment(jid: str, factor: str, kind: str, inputs: dict, status: str = "new", company: str = "amazon", **keys) -> dict:
    j = {"judgment_id": jid, "company_id": company, "factor": factor, "kind": kind, "score": None, "inputs": inputs,
         "evidence": ["판정 문장이다."], "reviewer": "agent", "reviewed_at": "2026-10-14", "status": status, **keys}
    if status == "carried":
        j["carried_from"] = "ai-scorecard-2026-10-v21"
    return j


def validate(items: list[dict], rules=V30) -> list[dict]:
    return validate_judgments({"schema": "scorecard.judgments/1", "run_id": "t", "items": items}, COMPANIES, rules.payload, "t")


def line(line_id: str, layer: str, amount=10, non_ai: str = "yes") -> dict:
    return {"line": line_id, "label": line_id, "amount": amount, "period": "2025-07-01~2026-06-30", "layer": layer,
            "non_ai": non_ai, "evidence_ids": ["EV-amazon-004"]}


def holdings_inputs() -> dict:
    cells = {layer: {"cell": "none", "evidence_ids": []} for layer in ORDER}
    cells["cloud"] = {"cell": "sold", "evidence_ids": ["EV-amazon-001"]}
    cells["user_platform"] = {"cell": "sold", "ai_chain": "yes", "evidence_ids": ["EV-amazon-002"]}
    cells["chip_design"] = {"cell": "self", "evidence_ids": ["EV-amazon-003"]}
    return {"cells": cells,
            "revenue_lines": [line("aws", "cloud", 30, "no"), line("online_stores", "user_platform", 40), line("third_party", "user_platform", 30)],
            "currency": "USD", "non_ai_margin": 0.1, "non_ai_margin_source": "segment"}


def business_inputs(lines=("aws",), layer: str = "cloud", **kw) -> dict:
    base = {"components": [{"name": "AWS", "layer": layer, "customer": "work", "lines": list(lines), "market": None, "ai_monetized": "partial"}],
            "participant": "none", "switching": "stay_measured", "pricing": "no_change", "substitutes": "gap_remains"}
    base.update(kw)
    return base


def standard(**kw) -> dict:
    base = {"name": "MCP", "holder": "neutral", "support": "most_major_or_neutral", "first_adopted": "2024-11-25",
            "latest_new_major_adopter": "Google", "latest_new_major_adopted_at": "2025-04-09", "evidence_ids": ["EV-anthropic-001"]}
    base.update(kw)
    return base


def cp_inputs(**acc_kw) -> dict:
    acc = {"metric": "Gemini 앱 월간 사용자", "tier": "d", "basis": "yoy_quarter", "prior_multiple": 1.4, "current_multiple": 1.5,
           "delayed": "no", "evidence_ids": ["EV-alphabet-001"]}
    acc.update(acc_kw)
    return {"strategy": "검색에 AI 답변을 무료로 넣고 광고로 거둔다", "counterparty": "OpenAI", "counterparty_present": "yes",
            "revenue_model": "recovered", "imitation": "conflict_pending", "door_closed_at": None, "acceleration": acc}


def alliance_inputs() -> dict:
    return {"relations": [{"counterparty": "Anthropic", "qualifies": ["equity", "competitor_onboard"], "evidence_ids": ["EV-amazon-010"]},
                          {"counterparty": "미국 정부", "qualifies": ["commercial"], "government_country": "US", "evidence_ids": ["EV-amazon-011"]}],
            "fronts": [{"name": "FTC 반독점 소송", "nature": "cost", "status": "ongoing", "jurisdiction": "US", "remedy_in_progress": "yes",
                        "evidence_ids": ["EV-amazon-012"]}],
            "partner_tension": "no"}


class UnitKeyTest(unittest.TestCase):
    def test_distinct_layers_pass_and_same_layer_twice_is_rejected(self):
        a = judgment("J-1", "F2", "layer_paths", {"adaptation": "adopted", "standards": []}, layer="cloud")
        b = judgment("J-2", "F2", "layer_paths", {"leap": "first", "adaptation": "adopted", "standards": []}, layer="chip_design")
        validate([a, b])
        dup = judgment("J-3", "F2", "layer_paths", {"adaptation": "beta", "standards": []}, layer="cloud")
        with self.assertRaisesRegex(SchemaError, r"judgments\[2\]: \('amazon', 'F2', 'cloud'\) 판단 중복 — 기업·factor·층 당 하나"):
            validate([a, b, dup])
        # 다른 회사의 같은 층은 중복이 아니다.
        validate([a, b, judgment("J-3", "F2", "layer_paths", {"adaptation": "beta", "standards": []}, company="alphabet", layer="cloud")])

    def test_company_level_duplicate_message_is_unchanged(self):
        h = judgment("J-1", "F4", "holdings", holdings_inputs())
        with self.assertRaisesRegex(SchemaError, r"\('amazon', 'F4'\) 판단 중복 — 기업·factor 당 하나"):
            validate([h, dict(h, judgment_id="J-2")])

    def test_unit_key_required_and_forbidden(self):
        with self.assertRaisesRegex(SchemaError, "layer 단위라 판단에 layer 키가 있어야 한다"):
            validate([judgment("J-1", "F2", "layer_paths", {"adaptation": "adopted", "standards": []})])
        with self.assertRaisesRegex(SchemaError, "company 단위라 layer 키를 둘 수 없다"):
            validate([judgment("J-1", "F4", "holdings", holdings_inputs(), layer="cloud")])
        with self.assertRaisesRegex(SchemaError, "layer 단위라 business 키를 둘 수 없다"):
            validate([judgment("J-1", "F3", "layer_cp", cp_inputs(), layer="cloud", business="aws")])
        with self.assertRaisesRegex(SchemaError, "business 단위라 판단에 business 키가 있어야 한다"):
            validate([judgment("J-1", "F1", "business", business_inputs())])

    def test_old_rules_reject_unit_keys(self):
        lockin = {"channel_consumer": "yes", "channel_work": "no", "channel_trade": "no", "loop": "pass", "switching": "pass",
                  "substitutes": "pass", "pricing": "partial", "durability_discount": "no", "ai_monetized_in_channel": "partial"}
        validate([judgment("J-1", "F1", "lockin", lockin)], V21)
        with self.assertRaisesRegex(SchemaError, "company 단위라 layer 키를 둘 수 없다"):
            validate([judgment("J-1", "F1", "lockin", lockin, layer="cloud")], V21)
        with self.assertRaisesRegex(SchemaError, "층 정의\\(layers\\)가 있는 규칙에서만"):
            validate([judgment("J-1", "F4", "holdings", holdings_inputs(), status="carried")], V21)

    def test_layer_id_and_business_id(self):
        with self.assertRaisesRegex(SchemaError, "층 'clould' 는 규칙의 층"):
            validate([judgment("J-1", "F2", "layer_paths", {"adaptation": "adopted", "standards": []}, layer="clould")])
        validate([judgment("J-1", "F2", "layer_paths", {"adaptation": "adopted", "standards": []}, layer="outside")])
        with self.assertRaisesRegex(SchemaError, "business 는 소문자 사업 id"):
            validate([judgment("J-1", "F1", "business", business_inputs(), business="AWS")])

    def test_carried_company_level_kind_is_rejected_for_layer_units(self):
        paths = {"performance_leap": "pass", "paradigm_adaptation": "pass", "standard_capture": "fail", "top_rank": "yes"}
        with self.assertRaisesRegex(SchemaError, "layer 단위 F2 판단은 승계여도 kind \\['layer_paths'\\] 만"):
            validate([judgment("J-1", "F2", "paths", paths, status="carried", layer="model")])


class HoldingsInputTest(unittest.TestCase):
    def check(self, inputs: dict) -> None:
        validate([judgment("J-1", "F4", "holdings", inputs)])

    def test_valid(self):
        self.check(holdings_inputs())
        h = holdings_inputs()
        h["revenue_lines"][0]["amount"] = "unknown"
        h["revenue_lines"].append(line("launch", "rocket_launch", 5))
        h["revenue_lines"].append(line("starlink", "outside", 5))
        h["non_ai_margin"] = "not_applicable"
        del h["non_ai_margin_source"]
        self.check(h)
        h = holdings_inputs()
        h["non_ai_margin_source"] = "company"   # 2026-10-14: 부문 이익률 미공시면 회사 전체 이익률로 대신한다
        self.check(h)

    def test_rejections(self):
        cases = []
        h = holdings_inputs(); del h["cells"]["device"]; cases.append((h, "열 칸을 모두 적는다"))
        h = holdings_inputs(); h["cells"]["model"] = {"cell": "preparing", "evidence_ids": []}; cases.append((h, "트리거\\(TRG-NNN\\)"))
        h = holdings_inputs(); h["cells"]["cloud"]["ai_chain"] = "yes"; cases.append((h, "ai_chain 은 AI 사슬 조건 층"))
        h = holdings_inputs(); del h["cells"]["user_platform"]["ai_chain"]; cases.append((h, "ai_chain\\(AI 사슬로 작동하는가\\)을 적는다"))
        h = holdings_inputs(); h["cells"]["cloud"]["cell"] = "rented"; cases.append((h, "cells.cloud.cell"))
        h = holdings_inputs(); h["revenue_lines"].append(line("ads", "model")); cases.append((h, "칸은 판매\\(sold\\)여야 한다"))
        h = holdings_inputs(); h["revenue_lines"][1]["amount"] = -1; cases.append((h, "어림이나 균등 비중으로 채우지 않는다"))
        h = holdings_inputs(); h["revenue_lines"].append(line("aws", "cloud")); cases.append((h, "매출 줄 id 중복"))
        h = holdings_inputs(); h["revenue_lines"][0]["non_ai"] = "maybe"; cases.append((h, "non_ai"))
        h = holdings_inputs(); h["non_ai_margin"] = "10%"; cases.append((h, "non_ai_margin"))
        h = holdings_inputs(); del h["non_ai_margin_source"]; cases.append((h, "이익률이 숫자면 출처를 적는다"))
        h = holdings_inputs(); h["non_ai_margin_source"] = "estimate"; cases.append((h, "non_ai_margin_source"))
        h = holdings_inputs(); h["non_ai_margin"] = "unknown"; cases.append((h, "이익률이 숫자일 때만"))
        h = holdings_inputs(); h["cells"]["cloud"]["evidence_ids"] = ["EV-1"]; cases.append((h, "근거 ID"))
        for inputs, pattern in cases:
            with self.subTest(pattern=pattern), self.assertRaisesRegex(SchemaError, pattern):
                self.check(inputs)

    def test_only_the_seventh_of_fourteen_lines_is_named(self):
        h = holdings_inputs()
        h["revenue_lines"] = [line(f"seg{i}", "user_platform") for i in range(14)]
        h["revenue_lines"][6]["layer"] = "user_platfrom"
        with self.assertRaisesRegex(SchemaError, r"revenue_lines\[6\]\.layer"):
            self.check(h)
        h["revenue_lines"][6]["layer"] = "user_platform"
        self.check(h)


class BusinessInputTest(unittest.TestCase):
    def check(self, inputs: dict, with_holdings: bool = True) -> None:
        items = [judgment("J-1", "F1", "business", inputs, business="aws")]
        if with_holdings:
            items.append(judgment("J-2", "F4", "holdings", holdings_inputs()))
        validate(items)

    def test_valid_and_bundle(self):
        self.check(business_inputs())
        bundle = business_inputs(lines=("online_stores",), layer="user_platform", bundle_reason="장터를 떠나면 Prime 배송 편익도 잃는다")
        bundle["components"].append({"name": "Prime", "layer": "user_platform", "customer": "consumer", "lines": ["third_party"],
                                     "market": "us-ecommerce", "ai_monetized": "no"})
        self.check(bundle)
        del bundle["bundle_reason"]
        with self.assertRaisesRegex(SchemaError, "bundle_reason"):
            self.check(bundle)

    def test_monetization_yes_needs_six_materials_and_majority(self):
        b = business_inputs()
        b["components"][0]["ai_monetized"] = "yes"
        with self.assertRaisesRegex(SchemaError, "AI 수익화 '예' 는 판정 재료"):
            self.check(b)
        b["components"][0].update({"ai_monetized_measure": "revenue", "ai_monetized_share": 0.5, "ai_monetized_period": "2026Q2",
                                   "ai_separate_billing_evidence": ["EV-amazon-020"], "ai_price_uplift_evidence": ["EV-amazon-021"]})
        with self.assertRaisesRegex(SchemaError, "과반"):
            self.check(b)
        b["components"][0]["ai_monetized_share"] = 0.6
        self.check(b)
        b["components"][0]["ai_price_uplift_evidence"] = []
        with self.assertRaisesRegex(SchemaError, "ai_price_uplift_evidence 에 확정 근거"):
            self.check(b)

    def test_pricing_levels_are_backed_by_quarters(self):
        self.check(business_inputs(pricing="sustained_explained", pricing_growth_quarters=8, pricing_explained="yes"))
        self.check(business_inputs(pricing="sustained_or_short_explained", pricing_growth_quarters=5, pricing_explained="yes"))
        self.check(business_inputs(pricing="sustained_or_short_explained", pricing_growth_quarters=9, pricing_explained="no"))
        for kw, pattern in [
            ({"pricing": "sustained_explained", "pricing_growth_quarters": 6, "pricing_explained": "yes"}, "가격 실측 4 는 8분기"),
            ({"pricing": "sustained_explained", "pricing_growth_quarters": 9, "pricing_explained": "no"}, "가격 실측 4 는 8분기"),
            ({"pricing": "sustained_or_short_explained", "pricing_growth_quarters": 5, "pricing_explained": "no"}, "가격 실측 3 은"),
            ({"pricing": "sustained_or_short_explained", "pricing_growth_quarters": 3, "pricing_explained": "yes"}, "가격 실측 3 은"),
            ({"pricing": "sustained_explained"}, "pricing_growth_quarters"),
            ({"participant": "strong"}, "participant"),
            ({"substitutes": "none"}, "substitutes"),
        ]:
            with self.subTest(kw=kw), self.assertRaisesRegex(SchemaError, pattern):
                self.check(business_inputs(**kw))

    def test_lines_must_exist_match_layer_and_belong_to_one_business(self):
        with self.assertRaisesRegex(SchemaError, "매출 줄 'ads' 가 같은 회사 ④ 보유표에 없다"):
            self.check(business_inputs(lines=("ads",)))
        with self.assertRaisesRegex(SchemaError, "층 'user_platform' 에 붙었는데 구성 사업의 층은 'cloud'"):
            self.check(business_inputs(lines=("online_stores",)))
        # 보유표가 없으면 교차 검사는 하지 않는다(계산이 판정 대기로 둔다).
        self.check(business_inputs(lines=("ads",)), with_holdings=False)
        other = judgment("J-3", "F1", "business", business_inputs(), business="aws_marketplace")
        with self.assertRaisesRegex(SchemaError, "매출 줄 'aws' 가 사업 'aws' 에도 붙었다"):
            validate([judgment("J-1", "F1", "business", business_inputs(), business="aws"),
                      judgment("J-2", "F4", "holdings", holdings_inputs()), other])


class LayerPathsInputTest(unittest.TestCase):
    def check(self, inputs: dict, layer: str) -> None:
        validate([judgment("J-1", "F2", "layer_paths", inputs, company="anthropic", layer=layer)])

    def test_leap_only_on_benchmark_layers(self):
        self.check({"leap": "second", "adaptation": "adopted", "standards": [standard()]}, "model")
        with self.assertRaisesRegex(SchemaError, "성능 도약\\(leap\\)을 적는다"):
            self.check({"adaptation": "adopted", "standards": []}, "model")
        with self.assertRaisesRegex(SchemaError, "알 수 없는 키 \\['leap'\\]"):
            self.check({"leap": "first", "adaptation": "adopted", "standards": []}, "cloud")

    def test_gap_months_by_layer(self):
        self.check({"leap": "generation_gap", "gap_months": 6, "adaptation": "none", "standards": []}, "model")
        self.check({"leap": "generation_gap", "gap_months": 12, "adaptation": "none", "standards": []}, "chip_design")
        self.check({"leap": "first_3m", "gap_months": 3, "adaptation": "none", "standards": []}, "model")
        for inputs, layer, pattern in [
            ({"leap": "generation_gap", "gap_months": 5, "adaptation": "none", "standards": []}, "model", "6개월 이상"),
            ({"leap": "generation_gap", "gap_months": 11, "adaptation": "none", "standards": []}, "chip_design", "12개월 이상"),
            ({"leap": "first_3m", "gap_months": 2, "adaptation": "none", "standards": []}, "model", "3개월 이상"),
            ({"leap": "generation_gap", "adaptation": "none", "standards": []}, "model", "gap_months"),
        ]:
            with self.subTest(inputs=inputs), self.assertRaisesRegex(SchemaError, pattern):
                self.check(inputs, layer)

    def test_adaptation_doubled_and_standards(self):
        self.check({"adaptation": "doubled", "adoption_multiple": 2.0, "standards": []}, "application")
        with self.assertRaisesRegex(SchemaError, "2배 이상"):
            self.check({"adaptation": "doubled", "adoption_multiple": 1.8, "standards": []}, "application")
        with self.assertRaisesRegex(SchemaError, "함께 적거나 함께 비운다"):
            self.check({"adaptation": "adopted", "standards": [standard(latest_new_major_adopted_at=None)]}, "application")
        self.check({"adaptation": "adopted", "standards": [standard(support="own_only", latest_new_major_adopter=None,
                                                                     latest_new_major_adopted_at=None, holder="company")]}, "application")
        with self.assertRaisesRegex(SchemaError, r"standards\[1\]\.support"):
            self.check({"adaptation": "adopted", "standards": [standard(), standard(name="A2A", support="everyone")]}, "application")


class LayerCpInputTest(unittest.TestCase):
    def check(self, inputs: dict) -> None:
        validate([judgment("J-1", "F3", "layer_cp", inputs, company="alphabet", layer="user_platform")])

    def test_valid_and_missing_values(self):
        self.check(cp_inputs())
        self.check(cp_inputs(basis="none", prior_multiple=None, current_multiple=None, tier="e", metric=None))
        none_rival = cp_inputs()
        none_rival.update(counterparty=None, counterparty_present="no", revenue_model="same", imitation="copied")
        self.check(none_rival)

    def test_rejections(self):
        rival = cp_inputs()
        rival.update(counterparty=None)
        for inputs, pattern in [
            (cp_inputs(prior_multiple=None), "함께 적거나 함께 비운다"),
            (cp_inputs(basis="none"), "기간 기준이 none"),
            (cp_inputs(tier="e"), "단계 e"),
            (cp_inputs(current_multiple=0), "양수 성장 배수"),
            (cp_inputs(metric=None), "지표\\(metric\\)"),
            (cp_inputs(delayed="unknown"), "delayed"),
            (rival, "counterparty_present 는 no"),
        ]:
            with self.subTest(pattern=pattern), self.assertRaisesRegex(SchemaError, pattern):
                self.check(inputs)


class AllianceInputTest(unittest.TestCase):
    def check(self, inputs: dict) -> None:
        validate([judgment("J-1", "F5", "alliance", inputs)])

    def test_valid(self):
        self.check(alliance_inputs())
        empty = {"relations": [], "fronts": [], "partner_tension": "unknown"}
        self.check(empty)

    def test_rejections(self):
        cases = []
        a = alliance_inputs(); a["relations"][0]["qualifies"] = ["equity", "supplier"]; cases.append((a, "qualifies"))
        a = alliance_inputs(); a["relations"][0]["qualifies"] = []; cases.append((a, "qualifies"))
        a = alliance_inputs(); a["relations"][1]["counterparty"] = "Anthropic"; cases.append((a, "상대 'Anthropic' 중복"))
        a = alliance_inputs(); a["relations"][0]["evidence_ids"] = []; cases.append((a, "확정 근거가 하나 이상"))
        a = alliance_inputs(); del a["fronts"][0]["jurisdiction"]; cases.append((a, "비용형은 관할"))
        a = alliance_inputs(); a["fronts"].append({"name": "주요 고객의 자체 모델", "nature": "structural", "status": "ongoing",
                                                   "remedy_in_progress": "no", "evidence_ids": ["EV-amazon-013"]}); cases.append((a, "비용형 전선에만"))
        a = alliance_inputs(); a["fronts"][0]["status"] = "settled"; cases.append((a, "status"))
        for inputs, pattern in cases:
            with self.subTest(pattern=pattern), self.assertRaisesRegex(SchemaError, pattern):
                self.check(inputs)


class SupplyFloorTest(unittest.TestCase):
    """⑧ 공급 축 하한: 같은 회사 ④ 보유표에서 AI 칩 설계나 클라우드가 '없음'이면 공급 축을 0 으로 적을 수 없다(v3.0 은 holdings 칸)."""

    AXES = {"customer": {"status": "not_applicable"}, "commitment": {"status": "not_applicable"},
            "supply": {"status": "absent_disclosed"}, "geopolitics": {"status": "not_applicable"}}

    def test_floor_reads_holdings_cells(self):
        f8 = judgment("J-8", "F8", "axes", self.AXES)
        none_chip = holdings_inputs()   # chip_design 은 자체 사용, cloud 는 판매
        none_chip["cells"]["chip_design"] = {"cell": "none", "evidence_ids": []}
        with self.assertRaisesRegex(SchemaError, "\\['chip_design'\\] 가 '없음'이라 공급 축을 0 으로 적을 수 없다"):
            validate([judgment("J-4", "F4", "holdings", none_chip), f8])
        validate([judgment("J-4", "F4", "holdings", holdings_inputs()), f8])


class CrossRefsTest(unittest.TestCase):
    SOURCES = [{"source_id": "SRC-1"}]

    def evidence(self, *ids: str, status: str = "confirmed") -> list[dict]:
        return [{"evidence_id": e, "source_id": "SRC-1", "status": status} for e in ids]

    def test_nested_ids_must_exist_and_be_confirmed_for_new(self):
        h = judgment("J-1", "F4", "holdings", holdings_inputs())
        ids = ["EV-amazon-001", "EV-amazon-002", "EV-amazon-003", "EV-amazon-004"]
        validate_cross_refs([], [h], self.evidence(*ids), self.SOURCES)
        with self.assertRaisesRegex(SchemaError, "판정 재료 근거 \\['EV-amazon-003'\\] 가 evidence.json 에 없음"):
            validate_cross_refs([], [h], self.evidence(*[e for e in ids if e != "EV-amazon-003"]), self.SOURCES)
        mixed = self.evidence(*ids[:3]) + self.evidence(ids[3], status="candidate")
        with self.assertRaisesRegex(SchemaError, "판정 재료 근거 \\['EV-amazon-004'\\] 가 확정되지 않았다"):
            validate_cross_refs([], [h], mixed, self.SOURCES)
        carried = dict(h, status="carried", carried_from="x")
        validate_cross_refs([], [carried], mixed, self.SOURCES)

    def test_each_kind_exposes_its_nested_ids(self):
        cases = [
            (judgment("J-1", "F5", "alliance", alliance_inputs()), ["EV-amazon-010", "EV-amazon-011", "EV-amazon-012"]),
            (judgment("J-1", "F3", "layer_cp", cp_inputs(), layer="cloud"), ["EV-alphabet-001"]),
            (judgment("J-1", "F2", "layer_paths", {"adaptation": "adopted", "standards": [standard()]}, layer="cloud"), ["EV-anthropic-001"]),
        ]
        for j, ids in cases:
            with self.subTest(kind=j["kind"]):
                validate_cross_refs([], [j], self.evidence(*ids), self.SOURCES)
                with self.assertRaisesRegex(SchemaError, "evidence.json 에 없음"):
                    validate_cross_refs([], [j], self.evidence(*ids[1:]), self.SOURCES)


class LookupTest(unittest.TestCase):
    def test_units_are_kept_out_of_get(self):
        f4 = judgment("J-0", "F4", "holdings", holdings_inputs())
        b = judgment("J-1", "F2", "layer_paths", {"adaptation": "adopted", "standards": []}, layer="user_platform")
        a = judgment("J-2", "F2", "layer_paths", {"adaptation": "adopted", "standards": []}, layer="cloud")
        lookup = JudgmentLookup([f4, b, a])
        self.assertIs(lookup.get("amazon", "F4"), f4)
        self.assertIsNone(lookup.get("amazon", "F2"))
        self.assertEqual([j["judgment_id"] for j in lookup.units("amazon", "F2")], ["J-2", "J-1"])
        self.assertEqual(lookup.units("amazon", "F4"), [])
        self.assertEqual(lookup.units("alphabet", "F2"), [])


class RejudgeTest(unittest.TestCase):
    def test_layer_judgments_are_checked_one_by_one(self):
        fresh = judgment("J-1", "F2", "layer_paths", {"adaptation": "adopted", "standards": []}, layer="cloud")
        stale = judgment("J-2", "F2", "layer_paths", {"adaptation": "adopted", "standards": []}, layer="user_platform", status="carried")
        old = judgment("J-3", "F3", "layer_cp", cp_inputs(), layer="cloud")
        old["reviewed_at"] = "2026-10-10"
        run = {"continued_from": {"run_id": None, "as_of": "2026-10-12", "added_companies": []}}
        ctx = SimpleNamespace(rules=V30, run=run, judgments=[fresh, stale, old])
        found = dict(rejudge_findings(ctx))
        self.assertEqual(sorted(found), ["J-2", "J-3"])
        self.assertIn("승계 판단", found["J-2"])
        self.assertIn("2026-10-10", found["J-3"])


class ProposalKeyTest(unittest.TestCase):
    def proposal(self, **kw) -> dict:
        p = {"proposal_id": "PRP-001", "company_id": "amazon", "factor": "F2", "changes": {}, "evidence_after": ["판정 문장이다."],
             "reason": "다시 읽었다", "evidence_ids": [], "before": {"kind": "layer_paths", "score": None, "inputs": {}, "evidence": ["옛 문장."]},
             "proposed_by": "agent", "proposed_at": "2026-10-14", "status": "pending"}
        p.update(kw)
        return {"schema": "scorecard.proposals/1", "run_id": "t", "items": [p]}

    def test_layer_and_business_keys(self):
        validate_proposals(self.proposal(layer="cloud"), COMPANIES, set(), "t", V30)
        validate_proposals(self.proposal(factor="F1", business="aws"), COMPANIES, set(), "t", V30)
        with self.assertRaisesRegex(SchemaError, "소문자 층 id"):
            validate_proposals(self.proposal(layer="Cloud"), COMPANIES, set(), "t", V30)
        with self.assertRaisesRegex(SchemaError, "함께 둘 수 없다"):
            validate_proposals(self.proposal(layer="cloud", business="aws"), COMPANIES, set(), "t", V30)


if __name__ == "__main__":
    unittest.main()
