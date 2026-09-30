# FIX-52 인용·출처 표기 — 판단·관측 source_id 가 인용 문서를 가리키고 HANDOVER·접수번호·경로 규약이 바로잡혔는지 고정한다
"""이 테스트가 지키는 계약 넷.

1. **행 번호를 인용하면 그 문서의 source_id 가 붙는다.** 채점규칙·별표·체크리스트 → SRC-v15-rule, 채점표 → SRC-v15-md,
   HANDOVER → SRC-v15-handover. 판단·관측이 가리키는 source_id 는 전부 sources.json 에 있다.
2. **HANDOVER 는 sources.json 에 있고 이해상충(75행)이 채워져 있다.** SRC-v15-rule 도 384행 고지를 싣는다.
3. **존재하지 않는 접수번호를 인용하지 않는다.** apple 은 -26-000020, spacex-xai S-1/A 는 0001628280-26-040364.
4. **원자료 경로는 커밋된 사본을 가리킨다.** 작업 트리 gitignore 경로는 규약 경로가 아니다.
"""
from __future__ import annotations

import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUN_DIR = ROOT / "output" / "ai-scorecard-2026-09-obsreg"


def load(name: str) -> dict:
    return json.loads((RUN_DIR / name).read_text(encoding="utf-8"))


class JudgmentSourceIdsTest(unittest.TestCase):
    def test_cited_documents_are_listed(self):
        for j in load("judgments.json")["items"]:
            text = json.dumps({k: j.get(k) for k in ("evidence", "counter_evidence", "note")}, ensure_ascii=False)
            with self.subTest(jid=j["judgment_id"]):
                if re.search(r"채점규칙|별표 [A-J]|체크리스트\s*\d+", text):
                    self.assertIn("SRC-v15-rule", j["source_ids"])
                if re.search(r"채점표(?!_HANDOVER)", text):
                    self.assertIn("SRC-v15-md", j["source_ids"])
                if j["status"] == "carried":
                    self.assertIn("SRC-v15-html", j["source_ids"])

    def test_impl48_headline_change_points_at_rule_and_md(self):
        items = {j["judgment_id"]: j for j in load("judgments.json")["items"]}
        self.assertEqual(items["openai.F5.impl48"]["source_ids"], ["SRC-v15-rule", "SRC-v15-md"])
        self.assertIn("SRC-v15-rule", items["anthropic.F5.impl48"]["source_ids"])

    def test_every_source_id_is_registered(self):
        ids = {s["source_id"] for s in load("sources.json")["items"]}
        used = {sid for j in load("judgments.json")["items"] for sid in j["source_ids"]}
        used |= {o["source_id"] for o in load("observations.json")["items"]}
        self.assertEqual(used - ids, set())


class ObservationSourceIdTest(unittest.TestCase):
    def test_md_row_citations_moved_to_md(self):
        moved = [o for o in load("observations.json")["items"] if "source_id_correction" in (o.get("basis") or {})]
        self.assertEqual(len(moved), 26)
        for o in moved:
            with self.subTest(oid=o["observation_id"]):
                self.assertEqual(o["source_id"], "SRC-v15-md")
                self.assertIn("SRC-v15-md", o["basis"]["cited_source_ids"])
        ntm = next(o for o in moved if o["observation_id"] == "meta.ntm_per.v15")
        self.assertEqual(ntm["basis"]["cited_source_ids"], ["SRC-v15-md", "SRC-v15-rule", "SRC-v15-handover"])

    def test_v15_total_unchanged(self):
        # 2026-09-16 FIX-55 2단계: anthropic.arr_prior.priv31 의 $47B 는 회사 보도자료가 1차 문면이라 그 출처로 옮겼다 — 242 → 241.
        n = sum(o["source_id"].startswith("SRC-v15-") for o in load("observations.json")["items"])
        self.assertEqual(n, 241)
        moved = {o["observation_id"]: o["source_id"] for o in load("observations.json")["items"]}["anthropic.arr_prior.priv31"]
        self.assertEqual(moved, "SRC-ANTHROPIC-SERIESH-2026")


class SourcesRegistryTest(unittest.TestCase):
    def setUp(self) -> None:
        self.items = {s["source_id"]: s for s in load("sources.json")["items"]}

    def test_handover_registered_with_conflict_of_interest(self):
        h = self.items["SRC-v15-handover"]
        self.assertEqual(h["sha256"], "3e5190c2cb4a4f8ebee2f72d4599929b79a5d4625b1d046c346627edf63b7cc1")
        self.assertIn("75행", h["conflict_of_interest"])
        self.assertTrue(h["accessed_at"])

    def test_rule_conflict_of_interest_filled(self):
        self.assertIn("384행", self.items["SRC-v15-rule"]["conflict_of_interest"])

    def test_raw_path_convention_uses_committed_copy(self):
        for sid in ("SRC-SEC-FACTS-F6", "SRC-SEC-BABA-FACTS"):
            with self.subTest(sid=sid):
                note = self.items[sid]["note"]
                self.assertIn("cbada75:validation/f6-avail-15b/_raw/", note)
        self.assertIn("커밋되지 않았다", self.items["SRC-SEC-FACTS-F6"]["note"])
        sha = json.loads((ROOT / "validation" / "fix-52" / "facts_f6_sha256.json").read_text(encoding="utf-8"))
        self.assertEqual(len(sha), 12)
        self.assertTrue(all(v["identical_to_15b"] for v in sha.values()))


class AccessionTest(unittest.TestCase):
    def test_no_nonexistent_accession_remains(self):
        text = (RUN_DIR / "observations.json").read_text(encoding="utf-8")
        for wrong in ('"accession": "0000320193-26-000070"', "0001193125-26-235805 (S-1/A)"):
            with self.subTest(wrong=wrong):
                self.assertNotIn(wrong, text)
        obs = {o["observation_id"]: o for o in load("observations.json")["items"]}
        self.assertEqual(obs["apple.cash.cashfcf35"]["basis"]["accession"], "0000320193-26-000020")
        self.assertIn("0001628280-26-040364 (S-1/A)", obs["spacex-xai.net_cash.nc37"]["basis"]["accession"])


class RunAssumptionTest(unittest.TestCase):
    def test_alibaba_assumption_marked_stale(self):
        run = load("run.json")
        row = next(a for a in run["assumptions"] if "alibaba 의 fcf_ttm·cash" in a)
        self.assertTrue(row.startswith("~~"))
        self.assertIn("verified", row)


if __name__ == "__main__":
    unittest.main()
