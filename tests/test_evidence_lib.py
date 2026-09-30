# evidence_lib 단위 테스트(네트워크 금지, DATA_ROOT는 tempfile)
from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard import evidence_lib  # noqa: E402
from scorecard.evidence_lib import (  # noqa: E402
    fetch_bytes,
    merge_items,
    parse_rfc2822,
    sha256_bytes,
    source_entry,
    source_id_for_article,
    source_id_for_filing,
    upsert_sources,
    user_agent_for,
    utc_now_iso,
)


class FetchBytesTest(unittest.TestCase):
    def _resp(self, body: bytes):
        resp = mock.MagicMock()
        resp.read.return_value = body
        resp.__enter__.return_value = resp
        return resp

    def test_success(self):
        with mock.patch.object(evidence_lib.urllib.request, "urlopen",
                               return_value=self._resp(b"abc")) as m:
            self.assertEqual(fetch_bytes("http://x", user_agent="ua"), b"abc")
            self.assertEqual(m.call_count, 1)

    def test_retry_then_success(self):
        with mock.patch.object(evidence_lib.urllib.request, "urlopen",
                               side_effect=[OSError("down"), self._resp(b"ok")]), \
             mock.patch.object(evidence_lib.time, "sleep") as sl:
            self.assertEqual(fetch_bytes("http://x", user_agent="ua"), b"ok")
            sl.assert_called_once_with(1)

    def test_empty_body_raises(self):
        with mock.patch.object(evidence_lib.urllib.request, "urlopen",
                               return_value=self._resp(b"")), \
             mock.patch.object(evidence_lib.time, "sleep"):
            with self.assertRaises(ValueError):
                fetch_bytes("http://x", user_agent="ua", retries=0)

    def test_failure_reraises(self):
        with mock.patch.object(evidence_lib.urllib.request, "urlopen",
                               side_effect=OSError("down")), \
             mock.patch.object(evidence_lib.time, "sleep"):
            with self.assertRaises(OSError):
                fetch_bytes("http://x", user_agent="ua", retries=1)


class HelpersTest(unittest.TestCase):
    def test_sha256_bytes(self):
        self.assertEqual(sha256_bytes(b"abc"),
                         "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad")

    def test_parse_rfc2822(self):
        self.assertEqual(parse_rfc2822("Tue, 29 Sep 2026 15:50:51 GMT"), "2026-09-29T15:50:51Z")
        self.assertEqual(parse_rfc2822("Mon, 28 Sep 2026 09:00:02 +0900"), "2026-09-28T00:00:02Z")
        self.assertIsNone(parse_rfc2822("not a date"))
        self.assertIsNone(parse_rfc2822(""))

    def test_utc_now_iso_format(self):
        stamp = utc_now_iso()
        self.assertRegex(stamp, r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")


class StateTest(unittest.TestCase):
    def test_roundtrip_and_trim(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "state.json"
            from scorecard.evidence_lib import load_state, save_state
            self.assertEqual(load_state(path), {"runs": [], "counts": {}})
            save_state(path, {"runs": [{"n": i} for i in range(25)], "counts": {}}, keep_runs=20)
            state = load_state(path)
            self.assertEqual(len(state["runs"]), 20)
            self.assertEqual(state["runs"][-1], {"n": 24})


class MergeTest(unittest.TestCase):
    def test_upsert_preserves_first_seen_and_updates_on_change(self):
        old = [{"article_id": "a", "v": 1, "first_seen_utc": "2026-01-01T00:00:00Z",
                "updated_utc": None}]
        same = merge_items(old, [{"article_id": "a", "v": 1}], "article_id")
        self.assertEqual(same, old)
        changed = merge_items(old, [{"article_id": "a", "v": 2}], "article_id")
        self.assertEqual(changed[0]["first_seen_utc"], "2026-01-01T00:00:00Z")
        self.assertIsNotNone(changed[0]["updated_utc"])

    def test_sorted_and_deterministic(self):
        first = merge_items([], [{"article_id": "b", "v": 1}, {"article_id": "a", "v": 1}],
                            "article_id")
        self.assertEqual([i["article_id"] for i in first], ["a", "b"])
        second = merge_items(first, [{"article_id": "a", "v": 1}, {"article_id": "b", "v": 1}],
                             "article_id")
        self.assertEqual(first, second)


class SourceIdTest(unittest.TestCase):
    def test_article_id(self):
        sid = source_id_for_article("nvidia", "2026-09-29T15:50:51Z", "abcdef1234567890")
        self.assertEqual(sid, "SRC-NEWS-nvidia-20260929-abcdef12")

    def test_article_id_without_published_uses_first_seen(self):
        sid = source_id_for_article("nvidia", None, "abcdef1234567890",
                                    first_seen_utc="2026-09-30T01:00:00Z")
        self.assertEqual(sid, "SRC-NEWS-nvidia-20260930-abcdef12")

    def test_filing_id(self):
        self.assertEqual(source_id_for_filing("000104581026000150"), "SRC-EDGAR-000104581026000150")


class SourceEntryTest(unittest.TestCase):
    def test_required_and_optional_keys(self):
        item = {"source_id": "s1", "title": "t", "publisher": "p", "url": "u",
                "company_id": "c", "published_at_utc": "2026-09-29T00:00:00Z",
                "publisher_url": "pu", "raw_ref": "rr", "note": "n"}
        entry = source_entry(item, kind="news", raw_sha256="h" * 64, accessed_at="2026-09-30")
        for key in ("source_id", "title", "publisher", "url", "accessed_at", "sha256",
                    "conflict_of_interest", "note"):
            self.assertIn(key, entry)
        self.assertIsNone(entry["conflict_of_interest"])
        self.assertEqual(entry["kind"], "news")
        self.assertEqual(entry["raw_ref"], "rr")

    def test_upsert_add_only(self):
        payload = {"schema": "scorecard.sources/1", "items": [{"source_id": "s1", "title": "old"}]}
        upsert_sources(payload, [{"source_id": "s1", "title": "new"},
                                 {"source_id": "s2", "title": "added"}])
        self.assertEqual(payload["items"][0]["title"], "old")
        self.assertEqual(len(payload["items"]), 2)


class UserAgentTest(unittest.TestCase):
    def test_sec_returns_env_value(self):
        with mock.patch.dict(os.environ, {"SEC_UA": "Name contact@example.com"}):
            self.assertEqual(user_agent_for("sec"), "Name contact@example.com")
            self.assertIn("contact@example.com", user_agent_for("news"))

    def test_other_without_sec_ua(self):
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("SEC_UA", None)
            self.assertIn("contact unset", user_agent_for("news"))


class ImportPinTest(unittest.TestCase):
    def test_urllib_importers_are_pinned(self):
        """네트워크 지점(urllib.request)은 evidence_lib 하나다. urllib.parse는
        기존 rules.py(urlsplit)와 collect_news.py(질의 URL 인코딩)만 허용한다."""
        import re
        network, parse = set(), set()
        for path in sorted((ROOT / "scripts").rglob("*.py")):
            for line in path.read_text(encoding="utf-8").splitlines():
                if re.match(r"\s*(import urllib\.request|from urllib\.request)\b", line):
                    network.add(path.relative_to(ROOT).as_posix())
                elif re.match(r"\s*(import urllib|from urllib)\b", line):
                    parse.add(path.relative_to(ROOT).as_posix())
        self.assertEqual(network, {"scripts/scorecard/evidence_lib.py"})
        self.assertEqual(parse, {"scripts/scorecard/rules.py",
                                 "scripts/scorecard/collect_news.py"})


if __name__ == "__main__":
    unittest.main()
