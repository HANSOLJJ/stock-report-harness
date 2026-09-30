# collect_news 단위 테스트(네트워크 금지, DATA_ROOT는 tempfile)
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard import collect_news, evidence_lib  # noqa: E402
from scorecard.collect_news import (  # noqa: E402
    build_query_url,
    collect_company_news,
    normalize_article,
    parse_rss,
)

FIXTURE = ROOT / "tests" / "fixtures" / "google_news_rss.sample.xml"
NVIDIA = {"company_id": "nvidia", "display_name": "NVIDIA", "ticker": "NVDA"}


class QueryUrlTest(unittest.TestCase):
    def test_build_query_url(self):
        url = build_query_url("NVIDIA")
        self.assertTrue(url.startswith("https://news.google.com/rss/search?q="))
        self.assertIn("hl=en-US", url)
        self.assertIn("NVIDIA", url)


class ParseRssTest(unittest.TestCase):
    def test_fixture_items(self):
        items = parse_rss(FIXTURE.read_bytes())
        self.assertEqual(len(items), 5)
        first = items[0]
        self.assertTrue(first["title"])
        self.assertTrue(first["link"].startswith("https://news.google.com/rss/articles/"))
        self.assertTrue(first["guid"])
        self.assertTrue(first["pubDate"])
        self.assertTrue(first["source_name"])


class NormalizeTest(unittest.TestCase):
    def test_fields(self):
        raw = parse_rss(FIXTURE.read_bytes())[0]
        art = normalize_article(raw, company_id="nvidia", query="NVIDIA",
                                fetched_at="2026-09-30T01:00:00Z", raw_ref="rr")
        self.assertTrue(art["article_id"].startswith("google:"))
        self.assertNotIn("revisions", art)
        self.assertNotIn("published_at_local", art)
        self.assertEqual(art["provider"], "google_news_rss")
        self.assertEqual(art["published_at_utc"], "2026-09-29T15:50:51Z")
        self.assertEqual(art["url_kind"], "google_redirect")
        self.assertFalse(art["url_is_fallback"])
        self.assertNotIn("unverified", art)
        self.assertIn("<", raw["description"])
        self.assertNotIn("<", art["summary"])
        self.assertRegex(art["source_id"], r"^SRC-NEWS-nvidia-20260929-[0-9a-f]{8}$")

    def test_missing_pubdate(self):
        art = normalize_article({"title": "t", "link": "l", "guid": "g", "pubDate": "???",
                                 "description": "d", "source_name": "s", "source_url": ""},
                                company_id="nvidia", query="q",
                                fetched_at="2026-09-30T01:00:00Z", raw_ref="rr")
        self.assertIsNone(art["published_at_utc"])
        self.assertEqual(art["unverified"], ["published_at"])
        self.assertTrue(art["source_id"].startswith("SRC-NEWS-nvidia-20260930-"))

    def test_deterministic(self):
        raw = parse_rss(FIXTURE.read_bytes())[1]
        kw = {"company_id": "nvidia", "query": "q", "fetched_at": "2026-09-30T01:00:00Z",
              "raw_ref": "rr"}
        self.assertEqual(normalize_article(raw, **kw), normalize_article(raw, **kw))


class CollectTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.old = evidence_lib.DATA_ROOT
        evidence_lib.DATA_ROOT = Path(self.tmp.name)
        self.addCleanup(setattr, evidence_lib, "DATA_ROOT", self.old)

    def test_from_file_and_state(self):
        out = collect_company_news(NVIDIA, from_file=FIXTURE, now="2026-09-30T01:00:00Z")
        self.assertEqual(len(out["raw_files"]), 2)  # display_name + ticker 질의
        norm = json.loads(Path(out["normalized_path"]).read_text(encoding="utf-8"))
        # 두 질의가 같은 기사 5건을 돌려주면 article_id 기준으로 합쳐져 5건이다
        self.assertEqual(len(norm["items"]), 5)
        # 같은 입력(같은 now) 재수집은 같은 출력. now가 다르면 raw_ref 파일명만 달라진다
        again = collect_company_news(NVIDIA, from_file=FIXTURE, now="2026-09-30T01:00:00Z")
        norm2 = json.loads(Path(again["normalized_path"]).read_text(encoding="utf-8"))
        self.assertEqual(norm, norm2)
        state = json.loads(Path(out["state_path"]).read_text(encoding="utf-8"))
        self.assertEqual(len(state["runs"]), 2)

    def test_rate_limit(self):
        state_path = evidence_lib.DATA_ROOT / "nvidia" / "news" / "google" / "state.json"
        state_path.parent.mkdir(parents=True, exist_ok=True)
        state_path.write_text(json.dumps(
            {"runs": [], "counts": {"2026-09-30": {"NVIDIA": 4, "NVDA": 4}}}), encoding="utf-8")
        calls: list[str] = []

        def fetch(url: str, **kw: object) -> bytes:
            calls.append(url)
            raise AssertionError("한도 초과 시 조회하지 않는다")

        out = collect_company_news(NVIDIA, fetch=fetch, now="2026-09-30T03:00:00Z")
        self.assertEqual(calls, [])
        self.assertEqual(sorted(out["skipped_rate_limit"]), ["NVDA", "NVIDIA"])

    def test_dry_run(self):
        out = collect_company_news(NVIDIA, dry_run=True)
        self.assertTrue(out["dry_run"])
        self.assertEqual(len(out["urls"]), 2)
        self.assertTrue(all(u.startswith("https://news.google.com/rss/search?q=") for u in out["urls"]))

    def test_default_queries_from_company(self):
        out = collect_company_news({"company_id": "x", "display_name": "Foo Bar", "ticker": "FB"},
                                   dry_run=True)
        self.assertEqual(out["queries"], ["Foo Bar", "FB"])


if __name__ == "__main__":
    unittest.main()
