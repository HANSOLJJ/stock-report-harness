# resolve_cik 단위 테스트(네트워크 금지)
from __future__ import annotations

import io
import json
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard.resolve_cik import load_ticker_map, main, resolve  # noqa: E402

FIXTURE = ROOT / "tests" / "fixtures" / "company_tickers.sample.json"


def ticker_map() -> dict[str, int]:
    return load_ticker_map(json.loads(FIXTURE.read_text(encoding="utf-8")))


COMPANIES = [
    {"company_id": "nvidia", "ticker": "NVDA", "listed": True},
    {"company_id": "spacex-xai", "ticker": "SPCX", "listed": True},
    {"company_id": "anthropic", "ticker": None, "listed": False},
]


class MapTest(unittest.TestCase):
    def test_upper_keys(self):
        mapping = ticker_map()
        self.assertEqual(mapping["NVDA"], 1045810)
        self.assertEqual(len(mapping), 11)


class ResolveTest(unittest.TestCase):
    def test_statuses(self):
        rows = {r["company_id"]: r for r in resolve(COMPANIES, ticker_map())}
        self.assertEqual(rows["nvidia"]["status"], "resolved")
        self.assertEqual(rows["nvidia"]["cik"], 1045810)
        # SPCX는 목록에 없어 not_found로 둔다
        self.assertEqual(rows["spacex-xai"]["status"], "not_found")
        self.assertIsNone(rows["spacex-xai"]["cik"])
        self.assertEqual(rows["anthropic"]["status"], "unlisted")

    def test_deterministic(self):
        self.assertEqual(resolve(COMPANIES, ticker_map()), resolve(COMPANIES, ticker_map()))


class MainTest(unittest.TestCase):
    def test_from_file_json(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = main(["--from-file", str(FIXTURE), "--company", "nvidia", "--json"])
        self.assertEqual(code, 0)
        rows = json.loads(buf.getvalue())
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["cik"], 1045810)

    def test_unknown_company(self):
        with mock.patch("scorecard.resolve_cik.load_companies", return_value={}):
            self.assertEqual(main(["--company", "nope"]), 1)

    def test_no_apply_option(self):
        # companies.json에 쓰는 --apply는 만들지 않는다
        with self.assertRaises(SystemExit):
            main(["--apply"])


if __name__ == "__main__":
    unittest.main()
