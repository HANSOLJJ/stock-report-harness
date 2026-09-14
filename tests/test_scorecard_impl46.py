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

    def test_stockanalysis_is_listed_only_as_legacy_upstream(self):
        """**허용 목록 밖이라는 사실은 그대로이고, 장부에는 legacy 상류로만 올라 있다.**

        원래 이 자리는 `네 목록(allowed·denied·not_adopted·unlisted) 어디에도 없다` 를 고정했다. IMPL-46 시점에는
        사실이었다. SRC-FLAG-49 가 관측이 어디서 왔는지 가리키려고 not_adopted 에 `legacy_upstream` 으로 올렸다 —
        되살린 것이 아니므로 allowed·denied·unlisted 에는 여전히 없다.
        """
        src = RULES.payload["sources"]
        for key in ("allowed", "denied", "unlisted"):
            with self.subTest(list=key):
                hosts = " ".join(str(e.get("host", "")) for e in src.get(key, []))
                self.assertNotIn("stockanalysis", hosts.lower())
        na = [e for e in src["not_adopted"] if "stockanalysis" in e["host"]]
        self.assertEqual(len(na), 1)
        self.assertEqual(na[0]["reason_type"], "legacy_upstream")
        for cid, o in self.ntm.items():
            with self.subTest(cid=cid):
                self.assertIn("IMPL-46 시점 기록", o["basis"]["vendor_policy_status"])

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
    """IMPL-46 의 조달 배제는 F5-IMPL-48 교체 뒤에도 **새 판단에 승계돼** 있어야 한다.

    원래 이 클래스는 `judgment_id == "openai.F5"` 를 찾아 A=+2 · 점수 2 · `체크리스트 19 는 반영하지 않았다` 를
    고정했다. F5-IMPL-48 이 체크리스트 19 를 적용해 판단을 `openai.F5.impl48`(A=+1, 점수 1)로 교체했으므로
    기업·factor 로 찾고, IMPL-46 당시 문언은 `superseded` 에서 확인한다.
    """

    @classmethod
    def setUpClass(cls) -> None:
        jud = json.loads((RUN_DIR / "judgments.json").read_text(encoding="utf-8"))["items"]
        cls.j = next(x for x in jud if x["company_id"] == "openai" and x["factor"] == "F5")
        res = json.loads((RUN_DIR / "results.json").read_text(encoding="utf-8"))
        cls.score = next(c for c in res["companies"] if c["company_id"] == "openai")["factors"]["F5"]["score"]

    def test_oracle_300b_exclusion_is_carried_into_the_new_judgment(self):
        self.assertIn("Oracle $300B 컴퓨트", self.j["note"])
        self.assertIn("A 근거에서 뺀다", self.j["note"])
        self.assertEqual(self.j["inputs"], {"A": 1, "H": -3})            # F5-IMPL-48 로 A +2→+1
        self.assertEqual(self.score, 1)

    def test_stargate_equity_is_not_confused_with_the_contract(self):
        """빠지는 것은 $300B 계약이지 Oracle 전체가 아니다."""
        self.assertIn("Stargate $7B 지분은 동맹으로 남는다", self.j["note"])

    def test_impl46_wording_survives_in_superseded(self):
        """IMPL-46 당시 `체크리스트 19 는 반영하지 않았다` 는 그때 사실이었다 — 지우지 않고 superseded 에 둔다."""
        old = self.j["superseded"]
        self.assertEqual(old["judgment_id"], "openai.F5")
        self.assertIn("체크리스트 19(받은 투자)는 반영하지 않았다", old["note"])
        self.assertIn("점수는 그대로 2 다", old["note"])


if __name__ == "__main__":
    unittest.main()
