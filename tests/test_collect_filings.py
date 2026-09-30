# collect_filings 단위 테스트(네트워크 금지, DATA_ROOT는 tempfile)
from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard import evidence_lib  # noqa: E402
from scorecard.collect_filings import (  # noqa: E402
    ARCHIVE_BASE,
    collect_company_filings,
    normalize_filing,
    parse_submissions,
    require_user_agent,
)

FIXTURE = ROOT / "tests" / "fixtures" / "edgar_submissions.CIK0001045810.sample.json"
NVIDIA = {"company_id": "nvidia", "cik": 1045810}


def payload() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


class UserAgentTest(unittest.TestCase):
    def test_missing_sec_ua_raises(self):
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("SEC_UA", None)
            with self.assertRaises(RuntimeError):
                require_user_agent()

    def test_no_fetch_without_sec_ua(self):
        calls: list[str] = []

        def fetch(url: str, **kw: object) -> bytes:
            calls.append(url)
            raise AssertionError("SEC_UA 없이 조회하지 않는다")

        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("SEC_UA", None)
            with self.assertRaises(RuntimeError):
                collect_company_filings(NVIDIA, fetch=fetch)
        self.assertEqual(calls, [])


class ParseTest(unittest.TestCase):
    def test_form_and_since_filter(self):
        rows = parse_submissions(payload())
        self.assertEqual(len(rows), 9)  # S-8 1건 제외
        self.assertTrue(all(r["form"] in {"8-K", "10-Q", "10-K", "20-F", "6-K"} for r in rows))
        rows = parse_submissions(payload(), since="2026-01-01")
        self.assertEqual(len(rows), 7)
        self.assertTrue(all(r["filingDate"] >= "2026-01-01" for r in rows))

    def test_deterministic(self):
        self.assertEqual(parse_submissions(payload()), parse_submissions(payload()))


class NormalizeTest(unittest.TestCase):
    def test_fields(self):
        row = parse_submissions(payload())[0]
        filing = normalize_filing(row, company_id="nvidia", cik=1045810, raw_ref="rr")
        self.assertEqual(filing["filing_id"], "edgar:000104581026000150")
        self.assertEqual(filing["source_id"], "SRC-EDGAR-000104581026000150")
        self.assertEqual(filing["items"], ["2.02", "9.01"])
        self.assertEqual(filing["primary_doc_url"],
                         ARCHIVE_BASE.format(cik=1045810, accession_nodash="000104581026000150",
                                             primary_document="nvda-20260910_8k.htm"))
        self.assertEqual(normalize_filing(parse_submissions(payload())[1], company_id="nvidia",
                                          cik=1045810, raw_ref="rr")["items"], [])


class CollectTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.old = evidence_lib.DATA_ROOT
        evidence_lib.DATA_ROOT = Path(self.tmp.name)
        self.addCleanup(setattr, evidence_lib, "DATA_ROOT", self.old)

    def test_from_file(self):
        sleeps: list[float] = []
        out = collect_company_filings(NVIDIA, from_file=FIXTURE, sleep=sleeps.append,
                                      now="2026-09-30T01:00:00Z")
        self.assertEqual(out["filings"], 9)
        index = json.loads(Path(out["index_path"]).read_text(encoding="utf-8"))
        self.assertEqual(len(index["items"]), 9)
        again = collect_company_filings(NVIDIA, from_file=FIXTURE, sleep=sleeps.append,
                                        now="2026-09-30T02:00:00Z")
        index2 = json.loads(Path(again["index_path"]).read_text(encoding="utf-8"))
        self.assertEqual(index, index2)

    def test_sleep_between_fetches(self):
        sleeps: list[float] = []
        with mock.patch.dict(os.environ, {"SEC_UA": "Tester test@example.com"}):
            collect_company_filings(NVIDIA, fetch=lambda url, **kw: FIXTURE.read_bytes(),
                                    sleep=sleeps.append)
        self.assertEqual(sleeps, [evidence_lib.SEC_SLEEP_S])

    def test_skipped_no_cik(self):
        out = collect_company_filings({"company_id": "anthropic"})
        self.assertEqual(out, {"company_id": "anthropic", "skipped_no_cik": True})

    def test_dry_run(self):
        out = collect_company_filings(NVIDIA, dry_run=True)
        self.assertTrue(out["dry_run"])
        self.assertEqual(out["urls"], ["https://data.sec.gov/submissions/CIK0001045810.json"])


if __name__ == "__main__":
    unittest.main()
