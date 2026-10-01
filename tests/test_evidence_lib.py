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
# 2026-10-01 V2-8: 이 파일을 직접 실행하면 tests/__init__.py 가 돌지 않는다. 실제 .env(SEC_UA)를 읽지 않게 여기서도 끈다.
os.environ["SCORECARD_DOTENV"] = ""

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

    def test_non_ascii_sec_ua_is_refused_before_any_request_without_the_value(self):
        """2026-10-01 레인 J(F-M-1): 영문 밖 글자는 urllib 머리글 인코딩에서 터진다. 요청 전에 막고 값은 메시지에 넣지 않는다."""
        value = "Harness 홍길동 hong@example.com"
        with mock.patch.dict(os.environ, {"SEC_UA": value}), \
                mock.patch.object(evidence_lib.urllib.request, "urlopen", side_effect=AssertionError("요청하면 안 된다")):
            for kind in ("sec", "news"):
                with self.subTest(kind=kind), self.assertRaises(RuntimeError) as ctx:
                    user_agent_for(kind)
                self.assertIn("SEC_UA 는 영문으로 적는다(HTTP 머리글 제약)", str(ctx.exception))
                self.assertNotIn("홍길동", str(ctx.exception))
                self.assertNotIn("hong@example.com", str(ctx.exception))


class LocalSettingTest(unittest.TestCase):
    """2026-09-30: SEC_UA 는 환경변수가 먼저이고, 없으면 gitignore 된 .env 에서 읽는다."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dotenv = Path(self.tmp.name) / "local.env"
        self.dotenv.write_text("# 개인 설정\nOTHER=x\nSEC_UA = \"Name file@example.com\"\n", encoding="utf-8")

    def test_reads_dotenv_when_env_missing(self):
        with mock.patch.dict(os.environ, {"SCORECARD_DOTENV": str(self.dotenv)}):
            os.environ.pop("SEC_UA", None)
            self.assertEqual(evidence_lib.sec_user_agent(), "Name file@example.com")
            self.assertEqual(user_agent_for("sec"), "Name file@example.com")

    def test_env_wins_over_dotenv(self):
        with mock.patch.dict(os.environ, {"SCORECARD_DOTENV": str(self.dotenv), "SEC_UA": "Env env@example.com"}):
            self.assertEqual(evidence_lib.sec_user_agent(), "Env env@example.com")

    def test_disabled_or_missing_file_is_empty(self):
        for path in ("", str(Path(self.tmp.name) / "none.env")):
            with self.subTest(path=path), mock.patch.dict(os.environ, {"SCORECARD_DOTENV": path}):
                os.environ.pop("SEC_UA", None)
                self.assertEqual(evidence_lib.sec_user_agent(), "")

    def test_tests_do_not_read_the_real_dotenv(self):
        # tests/__init__.py 가 끈다. 사용자가 실제 .env 를 만들어도 SEC_UA 없는 경로의 테스트가 흔들리지 않는다.
        self.assertEqual(os.environ.get("SCORECARD_DOTENV"), "")

    def test_worktree_falls_back_to_main_checkout(self):
        # 2026-10-01: 워크트리 루트에 .env 가 없으면 원본 체크아웃 루트의 .env 를 읽는다.
        main = Path(self.tmp.name) / "repo"
        wt = Path(self.tmp.name) / "wt"
        (main / ".git" / "worktrees" / "lane-x").mkdir(parents=True)
        wt.mkdir()
        (wt / ".git").write_text(f"gitdir: {main / '.git' / 'worktrees' / 'lane-x'}\n", encoding="utf-8")
        (main / ".env").write_text("SEC_UA=Main main@example.com\n", encoding="utf-8")
        env = {k: v for k, v in os.environ.items() if k not in ("SEC_UA", "SCORECARD_DOTENV")}
        with mock.patch.object(evidence_lib, "ROOT", wt), mock.patch.dict(os.environ, env, clear=True):
            self.assertEqual(evidence_lib._dotenv_paths(), [wt / ".env", main / ".env"])
            self.assertEqual(evidence_lib.sec_user_agent(), "Main main@example.com")
            (wt / ".env").write_text("SEC_UA=Wt wt@example.com\n", encoding="utf-8")
            self.assertEqual(evidence_lib.sec_user_agent(), "Wt wt@example.com")

    def test_filings_uses_the_same_reader(self):
        from scorecard.collect_filings import require_user_agent
        with mock.patch.dict(os.environ, {"SCORECARD_DOTENV": str(self.dotenv)}):
            os.environ.pop("SEC_UA", None)
            self.assertEqual(require_user_agent(), "Name file@example.com")


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



class DirectRunDotenvTest(unittest.TestCase):
    """2026-10-01 V2-8: tests 패키지를 거치지 않고 파일로 불러와도 설정 파일 읽기가 꺼진다(직접 실행과 같은 조건)."""

    FILES = ("test_collect_filings.py", "test_collect_news.py", "test_collect_prices.py", "test_collect_stage.py",
             "test_evidence_lib.py", "test_resolve_cik.py")

    def test_each_collector_test_file_disables_dotenv_on_its_own(self):
        import subprocess

        env = {k: v for k, v in os.environ.items() if k not in ("SCORECARD_DOTENV", "SEC_UA")}
        for name in self.FILES:
            code = ("import importlib.util, os, sys; "
                    f"spec = importlib.util.spec_from_file_location('_direct', r'{ROOT / 'tests' / name}'); "
                    "mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); "
                    "print(repr(os.environ.get('SCORECARD_DOTENV')))")
            with self.subTest(name=name):
                out = subprocess.run([sys.executable, "-X", "utf8", "-c", code], cwd=str(ROOT), env=env,
                                     capture_output=True, text=True, encoding="utf-8")
                self.assertEqual(out.returncode, 0, out.stderr)
                self.assertEqual(out.stdout.strip().splitlines()[-1], "''")

if __name__ == "__main__":
    unittest.main()
