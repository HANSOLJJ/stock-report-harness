# 규칙 v3.0 ⑤ 동맹 세 부분·적대 띠 계산(계획 S9) — 한 관계 한 부분 배정·정부 나라 단위·진행 중 전선·미확인 처리를 잠근다
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard.calc_qual import compute_f5_alliance  # noqa: E402
from scorecard.engine import compute_company  # noqa: E402
from scorecard.inputs import JudgmentLookup, ObsLookup  # noqa: E402
from scorecard.rules import load_rules  # noqa: E402
from scorecard.schema import validate_companies, validate_judgments  # noqa: E402

V30 = load_rules("v3.0")
COMPANIES = validate_companies(json.loads((ROOT / "scorecard" / "companies.json").read_text(encoding="utf-8")))
AMAZON = COMPANIES["amazon"]


def rel(counterparty: str, *qualifies: str, country: str | None = None) -> dict:
    r = {"counterparty": counterparty, "qualifies": list(qualifies), "evidence_ids": ["EV-amazon-001"]}
    if country:
        r["government_country"] = country
    return r


def front(name: str, nature: str = "cost", status: str = "ongoing", jurisdiction: str = "US", remedy: str = "no") -> dict:
    f = {"name": name, "nature": nature, "status": status, "evidence_ids": ["EV-amazon-002"]}
    if nature == "cost":
        f.update(jurisdiction=jurisdiction, remedy_in_progress=remedy)
    return f


def compute(relations=(), fronts=(), tension: str = "no", status: str = "new", kind: str = "alliance", inputs: dict | None = None) -> dict:
    j = {"judgment_id": "amazon.F5", "company_id": "amazon", "factor": "F5", "kind": kind, "score": None,
         "inputs": inputs or {"relations": list(relations), "fronts": list(fronts), "partner_tension": tension},
         "evidence": ["판정 문장이다."], "reviewer": "agent", "reviewed_at": "2026-10-14", "status": status}
    if status == "carried":
        j["carried_from"] = "x"
    validate_judgments({"schema": "scorecard.judgments/1", "run_id": "t", "items": [j]}, COMPANIES, V30.payload, "t")
    return compute_f5_alliance(AMAZON, JudgmentLookup([j]), V30)


class AllianceTest(unittest.TestCase):
    def test_amazon_onboard_plus_equity(self):
        r = compute([rel("Anthropic", "equity", "competitor_onboard"), rel("OpenAI", "equity")])
        self.assertEqual(r["calc"]["assignment"], {"Anthropic": "competitor_onboard", "OpenAI": "equity"})
        self.assertEqual((r["calc"]["A"], r["score"]), (5, 17))   # 12 + 3 + 2 + 적대 0

    def test_alphabet_onboard_only(self):
        r = compute([rel("Anthropic", "equity", "competitor_onboard")])
        self.assertEqual((r["calc"]["assignment"], r["calc"]["A"]), ({"Anthropic": "competitor_onboard"}, 3))

    def test_government_counts_once_per_country(self):
        same = [rel("국방부", "commercial", country="US"), rel("에너지부", "commercial", country="US"), rel("Acme", "commercial")]
        self.assertEqual(compute(same)["calc"]["part_points"]["commercial"], 1, "미국 정부 둘은 한 상대 — 상대 둘")
        three = same + [rel("영국 정부", "commercial", country="UK")]
        self.assertEqual(compute(three)["calc"]["part_points"]["commercial"], 2)

    def test_saturation_and_max(self):
        r = compute([rel("A", "equity"), rel("B", "equity"), rel("C", "equity")])
        self.assertEqual(r["calc"]["A"], 3, "지분 동맹 2곳 이상은 3")
        full = [rel("A", "equity"), rel("B", "equity"), rel("C", "competitor_onboard"),
                rel("D", "commercial"), rel("E", "commercial"), rel("F", "commercial")]
        self.assertEqual(compute(full)["calc"]["A"], 8)

    def test_one_relation_one_part_picks_the_best_assignment(self):
        # 셋 다 지분·상업을 채우면 둘은 지분(3), 하나는 상업(1) → 4. 셋 다 지분이면 3, 셋 다 상업이면 1 + 경쟁사 0
        r = compute([rel("A", "equity", "commercial"), rel("B", "equity", "commercial"), rel("C", "equity", "commercial")])
        self.assertEqual(r["calc"]["A"], 4)
        self.assertEqual(sorted(r["calc"]["assignment"].values()), ["commercial", "equity", "equity"])


class HostilityTest(unittest.TestCase):
    def h(self, fronts, tension: str = "no") -> dict:
        return compute(fronts=fronts, tension=tension)["calc"]

    def test_cost_band(self):
        self.assertEqual(self.h([front("FTC", remedy="yes", jurisdiction="US"), front("EU", jurisdiction="EU"),
                                 front("KFTC", jurisdiction="KR")])["H"], -6)
        self.assertEqual(self.h([front("FTC")])["H"], -2)
        self.assertEqual(self.h([front("FTC", remedy="unknown")])["H"], -3.2, "미확인 구제 조치는 감점의 60%")

    def test_structural_bands_and_partner_tension(self):
        two = [front("주요 고객의 자체 모델", "structural"), front("저작권 소송", "structural")]
        self.assertEqual(self.h(two)["H"], -10)
        self.assertEqual(self.h(two, "yes")["H"], -12)
        self.assertEqual(self.h(two, "unknown")["H"], -11.2)
        one = self.h([front("주요 고객의 자체 모델", "structural"), front("FTC", remedy="yes")])
        self.assertEqual((one["band"], one["H"]), ("structural", -8), "구조형이 있으면 비용형 조건은 더하지 않는다")

    def test_ended_fronts_do_not_count(self):
        c = self.h([front("옛 소송", status="ended"), front("옛 구조형", "structural", status="ended")])
        self.assertEqual((c["band"], c["H"], c["ended_ignored"]), ("minimal", 0, ["옛 소송", "옛 구조형"]))

    def test_floor_and_clamp(self):
        r = compute(fronts=[front("a", "structural"), front("b", "structural")], tension="yes")
        self.assertEqual(r["score"], 0)   # 12 + 0 − 12


class StatusTest(unittest.TestCase):
    def test_carried_grade_is_not_scored(self):
        r = compute(status="carried", kind="grade", inputs={"A": 1, "H": -1})
        self.assertEqual((r["status"], r["score"]), ("needs_judgment", None))

    def test_engine_dispatches_alliance_mode(self):
        j = {"judgment_id": "amazon.F5", "company_id": "amazon", "factor": "F5", "kind": "alliance", "score": None,
             "inputs": {"relations": [rel("Anthropic", "competitor_onboard")], "fronts": [], "partner_tension": "no"},
             "evidence": ["판정 문장이다."], "reviewer": "agent", "reviewed_at": "2026-10-14", "status": "new"}
        out = compute_company(AMAZON, ObsLookup([]), JudgmentLookup([j]), V30, {"as_of": "2026-10-14", "decisions": []})
        self.assertEqual((out["F5"]["basis"], out["F5"]["score"]), ("alliance", 15))


if __name__ == "__main__":
    unittest.main()
