# F5-IMPL-48 체크리스트 19 재판정(anthropic·openai A +2→+1)과 옛 판단 문언 보존을 고정한다
"""이 테스트가 지키는 계약 넷.

1. **바뀐 것은 A 하나다.** H 는 승계 그대로이고 F5 가 한 칸씩 내려간다.
2. **옛 판단은 지우지 않는다.** 기업·factor 당 판단이 하나라 새 판단의 `superseded` 에 문언 그대로 싣는다.
3. **근거는 행번호로 원문을 가리킨다.** 체크리스트 19(727) · 별표 G A 기준표(188~195) · 이중계상 금지선
   (262·264·266) · 별표 H(anthropic 288 / openai 276) · 채점표 759(openai).
4. **원문 판정표와 다르다는 사실을 숨기지 않는다.** 214·224행은 여전히 +2 로 적는다.
"""
from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard.rules import load_rules  # noqa: E402
from scorecard.schema import SchemaError, load_json_strict, validate_judgments  # noqa: E402

RULES = load_rules("v1.7")
RUN_ID = "ai-scorecard-2026-09-obsreg"
RUN_DIR = ROOT / "output" / RUN_ID
REGISTRY = {c["company_id"]: c for c in load_json_strict(ROOT / "scorecard" / "companies.json")["companies"]}


def judgments() -> dict:
    return json.loads((RUN_DIR / "judgments.json").read_text(encoding="utf-8"))


def f5(payload: dict, cid: str) -> dict:
    return next(x for x in payload["items"] if x["company_id"] == cid and x["factor"] == "F5")


class ReassessedGradeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.jud = judgments()
        res = json.loads((RUN_DIR / "results.json").read_text(encoding="utf-8"))
        cls.res = {c["company_id"]: c for c in res["companies"]}

    def test_only_a_moves_and_h_is_carried(self):
        for cid, a, h, score in (("anthropic", 1, 0, 4), ("openai", 1, -3, 1)):
            with self.subTest(cid=cid):
                j = f5(self.jud, cid)
                self.assertEqual(j["inputs"], {"A": a, "H": h})
                self.assertEqual(j["superseded"]["inputs"], {"A": 2, "H": h})
                self.assertEqual(self.res[cid]["factors"]["F5"]["score"], score)
                self.assertEqual(self.res[cid]["factors"]["F5"]["status"], "ok")   # 승계가 아니라 이번 검토

    def test_reviewer_and_date_are_filled(self):
        for cid in ("anthropic", "openai"):
            with self.subTest(cid=cid):
                j = f5(self.jud, cid)
                self.assertEqual(j["judgment_id"], f"{cid}.F5.impl48")
                self.assertEqual(j["previous_judgment_id"], f"{cid}.F5")
                self.assertEqual(j["status"], "new")
                self.assertNotIn("carried_from", j)
                self.assertEqual(j["reviewer"], "설계진행(C-13 A-GRADE-45 · NTM A-GRADE-45B 독립 일치)")
                self.assertEqual(j["reviewed_at"], "2026-09-14")

    def test_expected_ranking(self):
        """F5-IMPL-48 이 만든 칸은 F5 한 칸씩이다.

        원래 이 자리는 그 시점 총점·순위(anthropic 11 로 tsmc 와 공동 5위 · openai 2 로 13위)를 고정했다.
        FIX-52 S2 가 anthropic F6 를 -3 → -4 로 바꿔 총점이 10 이 됐으므로, 48 의 몫인 F5 점수와
        그 뒤에도 유지되는 openai 순위만 본다(총점은 FIX-62 가 2 → 4 로 바꿨다).
        """
        self.assertEqual(self.res["anthropic"]["factors"]["F5"]["score"], 4)
        self.assertEqual(self.res["openai"]["factors"]["F5"]["score"], 1)
        # 2026-09-17 FIX-62: 사용자가 openai.F9 경로를 뒤집어 총점이 4 가 됐다. 순위 13 은 그대로다.
        self.assertEqual((self.res["openai"]["total"], self.res["openai"]["rank"]), (4, 13))


class EvidenceCitesLinesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        jud = judgments()
        cls.text = {cid: " ".join(f5(jud, cid)["evidence"]) for cid in ("anthropic", "openai")}

    def test_common_citations(self):
        for cid, text in self.text.items():
            with self.subTest(cid=cid):
                self.assertIn("727행", text)
                self.assertIn("188~195행", text)

    def test_anthropic_cites_double_count_lines_and_288(self):
        t = self.text["anthropic"]
        for line in ("262행", "264행", "266행", "288행"):
            self.assertIn(line, t)
        self.assertIn("남의 매대", t)
        self.assertIn("순환", t)

    def test_openai_cites_276_and_759(self):
        t = self.text["openai"]
        self.assertIn("276행", t)
        self.assertIn("759행", t)
        self.assertIn("Stargate **하나**", t)

    def test_source_table_disagreement_is_on_record(self):
        jud = judgments()
        self.assertIn("214행", " ".join(f5(jud, "anthropic")["counter_evidence"]))
        self.assertIn("224행", " ".join(f5(jud, "openai")["counter_evidence"]))


class SupersededWordingTest(unittest.TestCase):
    """**옛 A=+2 근거 문언은 지우지 않는다.**"""

    def test_old_evidence_is_kept_verbatim(self):
        jud = judgments()
        a = f5(jud, "anthropic")["superseded"]
        self.assertIn("Amazon 5GW + Google 5GW TPU + MS 1GW — 3대 하이퍼스케일러 전원 동맹은 유일", a["evidence"])
        self.assertEqual((a["reviewer"], a["reviewed_at"], a["status"]), ("legacy:v1.5", "2026-09-02", "carried"))
        o = f5(jud, "openai")["superseded"]
        self.assertIn("🆕 Amazon $50B 투자(3월, $35B는 IPO/AGI 조건부)도 지분 동맹", o["evidence"])
        for sup in (a, o):
            self.assertEqual(sup["superseded_at"], "2026-09-14")
            self.assertIn("체크리스트 19", sup["why"])

    def test_superseded_must_point_at_previous_judgment(self):
        payload = copy.deepcopy(judgments())
        f5(payload, "openai")["superseded"]["judgment_id"] = "openai.F5.other"
        with self.assertRaises(SchemaError) as cm:
            validate_judgments(payload, REGISTRY, RULES.payload, RUN_ID)
        self.assertIn("previous_judgment_id 와 일치", str(cm.exception))

    def test_superseded_cannot_drop_the_old_wording(self):
        payload = copy.deepcopy(judgments())
        f5(payload, "anthropic")["superseded"]["evidence"] = []
        with self.assertRaises(SchemaError) as cm:
            validate_judgments(payload, REGISTRY, RULES.payload, RUN_ID)
        self.assertIn("옛 근거 문언이 비어 있음", str(cm.exception))


if __name__ == "__main__":
    unittest.main()
