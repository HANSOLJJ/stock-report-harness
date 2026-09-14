# IMPL-46 사용자 확정 4건(F6 정본 parameters · C-13 reject_proxy · F2 [2,5] · openai F5 조달 배제)을 고정한다
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard.rules import load_rules  # noqa: E402

RULES = load_rules("v1.7")
RUN_DIR = ROOT / "scorecard" / "runs" / "ai-scorecard-2026-09-obsreg"


class F6CanonicalModeTest(unittest.TestCase):
    def test_parameters_is_declared_canonical(self):
        c = RULES.payload["policies"]["f6"]["canonical_mode"]
        self.assertEqual(c["mode"], "parameters")
        self.assertEqual(RULES.payload["policies"]["f6"]["mode"], "parameters")

    def test_bands_is_legacy_and_kept_not_deleted(self):
        legacy = RULES.payload["policies"]["f6"]["canonical_mode"]["legacy_mode"]
        self.assertEqual(legacy["mode"], "bands")
        self.assertIn("구버전", legacy["status"])
        self.assertIn("지우지 않는다", legacy["do_not_delete"])

    def test_v15_bands_path_still_loads(self):
        """정본을 바꿔도 **승인된 v1.5 실행을 재현할 수 있어야** 한다."""
        v15 = load_rules("v1.5")
        self.assertIn("bands", v15.payload["policies"]["f6"])


class C13DecisionTest(unittest.TestCase):
    def setUp(self) -> None:
        self.d = {x["id"]: x for x in RULES.payload["decisions"]}["C-13"]

    def test_resolved_as_reject_proxy_with_three_reasons(self):
        self.assertEqual(self.d["status"], "resolved")
        self.assertEqual(self.d["chosen"], "reject_proxy")
        self.assertIn("accept_proxy_with_flag", self.d["choices"])
        self.assertEqual(len(self.d["confirmed_model"]["reasons"]), 3)

    def test_scope_is_bands_mode_only(self):
        self.assertIn("bands 모드에서만", self.d["scope"]["what_this_is"])


class NtmPerVendorTest(unittest.TestCase):
    """`ntm_per` 12건이 **원천이 정책 목록 밖이라는 사실을 스스로 들고** 있어야 한다."""

    @classmethod
    def setUpClass(cls) -> None:
        items = json.loads((RUN_DIR / "observations.json").read_text(encoding="utf-8"))["items"]
        cls.ntm = {o["company_id"]: o for o in items if o["metric"] == "ntm_per"}

    def test_all_twelve_kept_and_flagged(self):
        self.assertEqual(len(self.ntm), 12)
        for cid, o in self.ntm.items():
            with self.subTest(cid=cid):
                self.assertIsNotNone(o["value"])                             # 삭제하지 않는다
                self.assertTrue(o["basis"]["vendor_not_in_source_policy"])

    def test_stockanalysis_is_in_none_of_the_four_policy_lists(self):
        src = RULES.payload["sources"]
        for key in ("allowed", "denied", "not_adopted", "unlisted"):
            with self.subTest(list=key):
                hosts = " ".join(str(e.get("host", "")) for e in src.get(key, []))
                self.assertNotIn("stockanalysis", hosts.lower())

    def test_alibaba_and_tsmc_are_author_computed_not_vendor_values(self):
        """**원문이 StockAnalysis 값을 버리고 직접 계산했다** — 12건 전부 StockAnalysis 가 아니다."""
        for cid in ("alibaba", "tsmc"):
            with self.subTest(cid=cid):
                b = self.ntm[cid]["basis"]
                self.assertEqual(b["source_vendor"], "author_computed")
                self.assertEqual(b["method"], "annual_eps_weighted_proxy")
                self.assertIn("C-13 이 거부한 바로 그 근사", b["is_the_proxy_c13_rejects"])
        others = {cid for cid, o in self.ntm.items() if o["basis"]["source_vendor"] == "StockAnalysis"}
        self.assertEqual(len(others), 10)


class OpenaiF5Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        jud = json.loads((RUN_DIR / "judgments.json").read_text(encoding="utf-8"))["items"]
        cls.j = next(x for x in jud if x["judgment_id"] == "openai.F5")
        res = json.loads((RUN_DIR / "results.json").read_text(encoding="utf-8"))
        cls.score = next(c for c in res["companies"] if c["company_id"] == "openai")["factors"]["F5"]["score"]

    def test_oracle_300b_excluded_but_score_unchanged(self):
        self.assertIn("Oracle $300B 컴퓨트 계약을 뺀다", self.j["note"])
        self.assertEqual(self.j["inputs"], {"A": 2, "H": -3})
        self.assertEqual(self.score, 2)

    def test_stargate_equity_is_not_confused_with_the_contract(self):
        """빠지는 것은 $300B 계약이지 Oracle 전체가 아니다."""
        self.assertIn("Stargate $7B 지분은 동맹으로 남는다", self.j["note"])

    def test_checklist_19_is_explicitly_not_applied(self):
        self.assertIn("체크리스트 19(받은 투자)는 반영하지 않았다", self.j["note"])


if __name__ == "__main__":
    unittest.main()
