# SEC 문서를 SEC_UA 로 받아 캐시하는 sec-get(함수·CLI)을 잠그는 테스트(네트워크 금지)
from __future__ import annotations

import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
os.environ["SCORECARD_DOTENV"] = ""

import scorecard_cli  # noqa: E402
from scorecard import collect_filings, evidence_lib  # noqa: E402
from scorecard.collect_filings import sec_get  # noqa: E402

URL = "https://www.sec.gov/Archives/edgar/data/1341439/000095017026000123/orcl-20260831.htm"
UA = "Test User test@example.com"


class SecGetTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.addCleanup(setattr, evidence_lib, "DATA_ROOT", evidence_lib.DATA_ROOT)
        evidence_lib.DATA_ROOT = Path(self.tmp.name)
        saved = os.environ.get("SEC_UA")
        self.addCleanup(lambda: os.environ.__setitem__("SEC_UA", saved) if saved is not None else os.environ.pop("SEC_UA", None))
        os.environ["SEC_UA"] = UA
        sleep = mock.patch.object(collect_filings.time, "sleep")
        self.sleep = sleep.start()
        self.addCleanup(sleep.stop)
        self.calls: list[tuple[str, str]] = []

    def fetch(self, url: str, *, user_agent: str, **kw: object) -> bytes:
        self.calls.append((url, user_agent))
        return b"<html>10-Q</html>"

    def test_fetches_with_sec_ua_then_serves_from_cache(self):
        first = sec_get(URL, fetch=self.fetch, now="2026-10-02T00:00:00Z")
        self.assertEqual(self.calls, [(URL, UA)])
        self.assertFalse(first["cached"])
        self.assertEqual(Path(first["path"]).read_bytes(), b"<html>10-Q</html>")
        self.assertTrue(Path(first["path"]).is_relative_to(Path(self.tmp.name) / "_sec" / "docs"))
        self.assertTrue(first["path"].endswith("-orcl-20260831.htm"))
        self.sleep.assert_called_once_with(evidence_lib.SEC_SLEEP_S)
        second = sec_get(URL, fetch=self.fetch)
        self.assertEqual(len(self.calls), 1)   # 같은 주소는 다시 요청하지 않는다
        self.assertTrue(second["cached"])
        self.assertEqual((second["path"], second["sha256"], second["fetched_at"]),
                         (first["path"], first["sha256"], "2026-10-02T00:00:00Z"))
        self.assertNotIn(UA, json.dumps([first, second], ensure_ascii=False))

    def test_only_sec_https_urls(self):
        for url in ("https://example.com/a.htm", "http://www.sec.gov/a.htm", "https://sec.gov.evil.com/a.htm", "file:///etc/x"):
            with self.subTest(url=url):
                with self.assertRaisesRegex(ValueError, "SEC 주소"):
                    sec_get(url, fetch=self.fetch)
        self.assertEqual(self.calls, [])

    def test_missing_sec_ua_stops_before_request(self):
        os.environ.pop("SEC_UA")
        with self.assertRaisesRegex(RuntimeError, "SEC_UA 가 필요하다"):
            sec_get(URL, fetch=self.fetch)
        self.assertEqual(self.calls, [])

    def cli(self, *argv: str) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = scorecard_cli.main(list(argv))
        return code, out.getvalue(), err.getvalue()

    def test_cli_json_and_failure(self):
        # fetch 기본값은 정의 때 묶이므로 CLI 가 부르는 sec_get 자체를 가짜 fetch 로 감싼다
        with mock.patch.object(collect_filings, "sec_get", lambda url: sec_get(url, fetch=self.fetch)):
            code, out, _ = self.cli("sec-get", URL, "--json")
        self.assertEqual(code, 0)
        data = json.loads(out)
        self.assertEqual((data["url"], data["cached"]), (URL, False))
        self.assertNotIn(UA, out)
        code, out, err = self.cli("sec-get", "https://example.com/a.htm")
        self.assertEqual((code, out), (1, ""))
        self.assertIn("[FAIL] SEC 주소", err)


if __name__ == "__main__":
    unittest.main()
