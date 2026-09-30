# SRC-FLAG-49 legacy 관측 상류(StockAnalysis) 표시와 not_adopted 장부 등재를 고정한다
"""이 테스트가 지키는 계약 넷.

1. **market_cap legacy 관측은 전부 상류를 가리킨다.** tsmc·alibaba 는 원문이 직접 계산했다고 적는다.
2. **장부 등재는 되살림이 아니다.** stockanalysis.com 은 legacy_upstream 이고 안내 문구가 검토를 마친 것처럼,
   또는 '약관 확인 후 등재하고 쓴다' 로 읽히면 안 된다.
3. **net_cash apple·palantir 는 SEC 가 아니라 StockAnalysis + 공시 혼합이다.**
4. **관측 source_id 는 정책 검사 밖이라는 사실이 sources 에 적혀 있다.**
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
from scorecard.schema import SchemaError, validate_rules  # noqa: E402

RULES = load_rules("v1.7")
RUN_DIR = ROOT / "output" / "ai-scorecard-2026-09-obsreg"


def observations() -> list[dict]:
    return json.loads((RUN_DIR / "observations.json").read_text(encoding="utf-8"))["items"]


class MarketCapUpstreamTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.mc = {o["company_id"]: o for o in observations()
                  if o["metric"] == "market_cap" and o["status"] == "legacy_unverified"}

    def test_every_legacy_market_cap_is_flagged(self):
        """지시서는 11건이다. 관측은 12건이고 12번째 spacex-xai 는 점수 경로 밖이라 그 사실까지 적는다."""
        self.assertEqual(len(self.mc), 12)
        for cid, o in self.mc.items():
            with self.subTest(cid=cid):
                b = o["basis"]
                self.assertIsNotNone(o["value"])                               # 삭제하지 않는다
                self.assertTrue(b["vendor_not_in_source_policy"])
                self.assertIn("채점표 L794 절 제목", b["source_citation"])
                self.assertIn("legacy_upstream", b["vendor_policy_status"])
        self.assertIn("점수 경로 밖", self.mc["spacex-xai"]["basis"]["on_score_path"])
        on_path = [c for c, o in self.mc.items() if "on_score_path" not in o["basis"]]
        self.assertEqual(len(on_path), 11)

    def test_ten_are_stockanalysis_values_two_are_author_computed(self):
        vendors = {cid: o["basis"]["source_vendor"] for cid, o in self.mc.items()}
        self.assertEqual({c for c, v in vendors.items() if v == "author_computed"}, {"tsmc", "alibaba"})
        self.assertEqual(sum(v == "StockAnalysis" for v in vendors.values()), 10)
        for cid in ("tsmc", "alibaba"):
            with self.subTest(cid=cid):
                b = self.mc[cid]["basis"]
                self.assertEqual(b["author_computed"], "직접 계산, 주가 입력은 같은 절 (L822·L823)")
                self.assertEqual(b["price_input_vendor"], "StockAnalysis")

    def test_tsmc_vendor_value_was_rejected_by_the_source(self):
        b = self.mc["tsmc"]["basis"]
        self.assertIn("$1.95T", b["vendor_value_rejected"])
        self.assertAlmostEqual(5.19e9 * 415.50 / 1e12, 2.15, delta=0.01)

    def test_alibaba_narrowing_is_on_record(self):
        """**원문은 alibaba 시총을 `직접 계산` 이라고 적지 않는다** — 산술로 읽었다는 사실을 남긴다."""
        b = self.mc["alibaba"]["basis"]
        self.assertIn("직접 계산` 이라고 적지 않는다", b["author_computed_narrowing"])
        self.assertAlmostEqual(2.42e9 * 111.76 / 1e9, self.mc["alibaba"]["value"] / 1e9, delta=1.0)


class NetCashMixedTest(unittest.TestCase):
    def test_apple_and_palantir_are_mixed_not_sec(self):
        nc = {o["company_id"]: o for o in observations() if o["metric"] == "net_cash"}
        for cid in ("apple", "palantir"):
            with self.subTest(cid=cid):
                b = nc[cid]["basis"]
                self.assertEqual(nc[cid]["status"], "legacy_unverified")
                self.assertEqual(b["source_mixed"], "StockAnalysis 9/2 + 공시 (채점표 L848 · HANDOVER L41)")
                self.assertIn("SEC 관측이 아니다", b["not_sec"])


class LedgerEntryTest(unittest.TestCase):
    def setUp(self) -> None:
        self.entry = next(e for e in RULES.payload["sources"]["not_adopted"] if e["host"] == "stockanalysis.com")

    def test_entry_is_legacy_upstream_with_the_given_reason(self):
        self.assertEqual(self.entry["reason_type"], "legacy_upstream")
        self.assertEqual(self.entry["reason"], "v1.5 legacy 관측의 상류. 원천 정책 수립 전 자료. 재조회하지 않는다. 약관 미검토.")
        self.assertIn("되살리는 것이 아니다", self.entry["note"])

    def test_violation_message_does_not_claim_review_or_invite_use(self):
        """SRC-POLICY-32·SCOPE-34 에서 고친 함정 — 안내가 우리가 막으려는 행동을 지시하면 안 된다."""
        msg = RULES.source_violation("https://stockanalysis.com/stocks/aapl/financials/")
        self.assertIsNotNone(msg)
        self.assertIn("채택 검토를 하지 않았고 새 수집에 쓰지 않는다", msg)
        self.assertNotIn("검토를 마치고", msg)
        self.assertNotIn("약관 확인 후 규칙에 등재하고 쓴다", msg)

    def test_other_not_adopted_entries_keep_their_message(self):
        msg = RULES.source_violation("https://finnhub.io/api/v1/quote")
        self.assertIn("검토를 마치고 채택하지 않기로 결정된 원천", msg)

    def test_unknown_reason_type_is_rejected(self):
        payload = copy.deepcopy(RULES.payload)
        next(e for e in payload["sources"]["not_adopted"] if e["host"] == "stockanalysis.com")["reason_type"] = "legacy"
        with self.assertRaises(SchemaError):
            validate_rules(payload)

    def test_source_id_scope_note(self):
        note = RULES.payload["sources"]["note"]
        self.assertIn("관측 source_id 는 원천 정책 검사를 받지 않는다", note)
        self.assertIn("242건", note)          # SRC-FLAG-49 당시 수는 기록으로 남는다
        self.assertIn("241건", note)          # FIX-55 2단계에서 한 건이 회사 보도자료 출처로 옮겨졌다
        src_v15 = sum(o["source_id"].startswith("SRC-v15-") for o in observations())
        self.assertEqual(src_v15, 241)


if __name__ == "__main__":
    unittest.main()
