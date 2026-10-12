# 중계 주소·제목뿐인 근거 막기(2026-10-12 사용자 지시): 원문 주소 풀기, 확정·research·판단 쓰기의 거부를 잠근다
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard import stages  # noqa: E402
from scorecard.collect_news import is_google_relay_url, resolve_google_news_url  # noqa: E402
from scorecard.schema import SchemaError, load_json_strict, write_json  # noqa: E402
from tests.test_collect_stage import SLUG  # noqa: E402
from tests.test_evidence_three_way import DOWN, UP, V19Base  # noqa: E402
from tests.test_v20_judge import V20Base  # noqa: E402
from tests.test_v20_reconfirm import rejudge_all  # noqa: E402

RELAY = "https://news.google.com/rss/articles/CBMiAbc123?oc=5"
PAGE = b'<c-wiz><div jscontroller="x" data-n-a-sg="SIG42" data-n-a-ts="1759200000"></div></c-wiz>'
TITLE_ONLY = "9월 말 연환산 매출 보도는 제목만 확인돼 쓰지 않았다(미확인)."


def batch_reply(url: str) -> bytes:
    inner = json.dumps(["garturlres", url, 1])
    return (")]}'\n\n" + json.dumps([["wrb.fr", "Fbv4je", inner, None, None, None, "generic"]])).encode()


class FakeFetch:
    def __init__(self, page: bytes = PAGE, reply: bytes = batch_reply("https://www.axios.com/2026/09/29/scoop")) -> None:
        self.page, self.reply, self.calls = page, reply, []

    def __call__(self, url: str, *, user_agent: str, data: bytes | None = None, headers: dict | None = None) -> bytes:
        self.calls.append({"url": url, "data": data, "headers": headers})
        return self.reply if data is not None else self.page


class ResolveTest(unittest.TestCase):
    def test_resolves_through_signature_and_batch_request(self):
        fetch = FakeFetch()
        self.assertEqual(resolve_google_news_url(RELAY, fetch=fetch, user_agent="t"), "https://www.axios.com/2026/09/29/scoop")
        self.assertEqual(fetch.calls[0]["url"], "https://news.google.com/rss/articles/CBMiAbc123")
        body = fetch.calls[1]["data"].decode()
        self.assertIn("CBMiAbc123", body)
        self.assertIn("SIG42", body)
        self.assertIn("1759200000", body)
        self.assertIn("x-www-form-urlencoded", fetch.calls[1]["headers"]["Content-Type"])

    def test_failures_raise_instead_of_returning_the_relay(self):
        with self.assertRaisesRegex(ValueError, "중계 주소가 아니다"):
            resolve_google_news_url("https://www.reuters.com/a", fetch=FakeFetch(), user_agent="t")
        with self.assertRaisesRegex(ValueError, "서명·시각이 없다"):
            resolve_google_news_url(RELAY, fetch=FakeFetch(page=b"<html></html>"), user_agent="t")
        with self.assertRaisesRegex(ValueError, "원문 URL 이 아니다"):
            resolve_google_news_url(RELAY, fetch=FakeFetch(reply=batch_reply(RELAY)), user_agent="t")
        with self.assertRaisesRegex(ValueError, "응답을 읽지 못했다"):
            resolve_google_news_url(RELAY, fetch=FakeFetch(reply=b"garbage"), user_agent="t")

    def test_relay_detection(self):
        self.assertTrue(is_google_relay_url(RELAY))
        self.assertTrue(is_google_relay_url("https://news.google.com/articles/CBMiXyz"))
        self.assertFalse(is_google_relay_url("https://news.google.com/rss/search?q=nvidia"))
        self.assertFalse(is_google_relay_url("https://www.axios.com/2026/09/29/scoop"))
        self.assertFalse(is_google_relay_url(None))


class RelayMixin:
    def set_source_url(self, url: str) -> None:
        sid = self.cand["source_id"]
        for path in (self.paths.candidates, self.box.run_dir / "sources.json"):
            if path.is_file():
                payload = load_json_strict(path)
                for item in payload["items"]:
                    if item["source_id"] == sid:
                        item["url"] = url
                write_json(path, payload)

    def add_evidence(self, eid: str, **kw) -> None:
        payload = load_json_strict(self.paths.evidence)
        payload["items"].append(self.evidence_item(eid, **kw))
        write_json(self.paths.evidence, payload)


class ConfirmGuardTest(RelayMixin, V20Base):
    def test_relay_source_is_not_confirmed(self):
        self.set_source_url(RELAY)
        self.add_evidence("EV-nvidia-002")
        before = self.paths.evidence.read_bytes()
        with self.assertRaisesRegex(SchemaError, "EV-nvidia-002: 출처 URL 이 Google News 중계 주소다"):
            stages.confirm(SLUG, evidence_ids=["EV-nvidia-002"], reviewer="사용자")
        self.assertEqual(self.paths.evidence.read_bytes(), before)

    def test_title_only_excerpt_is_not_confirmed(self):
        self.add_evidence("EV-nvidia-002", excerpt=self.cand["title"])
        with self.assertRaisesRegex(SchemaError, "EV-nvidia-002: 발췌가 제목과 같다"):
            stages.confirm(SLUG, evidence_ids=["EV-nvidia-002"], reviewer="사용자")

    def test_read_evidence_is_confirmed(self):
        self.add_evidence("EV-nvidia-002")
        self.assertEqual(stages.confirm(SLUG, evidence_ids=["EV-nvidia-002"], reviewer="사용자")["confirmed"], ["EV-nvidia-002"])


class V19UnaffectedTest(RelayMixin, V19Base):
    def test_v19_keeps_its_contract(self):
        self.set_source_url(RELAY)
        self.add_evidence("EV-nvidia-002", excerpt=self.cand["title"])
        self.assertEqual(stages.confirm(SLUG, evidence_ids=["EV-nvidia-002"], reviewer="사용자")["confirmed"], ["EV-nvidia-002"])
        stages.revise_judgment(SLUG, company_id="nvidia", factor="F5",
                               changes={"evidence": [TITLE_ONLY], "evidence_up": UP, "evidence_down": DOWN}, reason="시험", by="사용자")


class ResearchGuardTest(RelayMixin, V20Base):
    def setUp(self) -> None:
        super().setUp()
        rejudge_all(self.jpath)

    def edit_confirmed(self, **kw) -> None:
        payload = load_json_strict(self.paths.evidence)
        next(e for e in payload["items"] if e["evidence_id"] == "EV-nvidia-001").update(kw)
        write_json(self.paths.evidence, payload)

    def assert_stops(self, pattern: str) -> None:
        with self.assertRaisesRegex(SchemaError, pattern):
            stages.research(SLUG)

    def test_clean_run_passes(self):
        self.assertTrue(stages.research(SLUG).is_file())

    def test_inherited_title_only_evidence_stops(self):
        self.edit_confirmed(excerpt=self.cand["title"])
        self.assert_stops(r"원문을 읽지 않은 근거·판단 1건: EV-nvidia-001: 발췌가 제목과 같다.*resolve-urls")

    def test_relay_url_stops(self):
        stages.register_evidence_sources(SLUG)
        self.set_source_url(RELAY)
        self.assert_stops("EV-nvidia-001: 출처 URL 이 Google News 중계 주소다")

    def test_title_only_reason_in_judgment_stops(self):
        payload = load_json_strict(self.jpath)
        next(j for j in payload["items"] if (j["company_id"], j["factor"]) == ("nvidia", "F3"))["evidence"].append(TITLE_ONLY)
        write_json(self.jpath, payload)
        self.assert_stops(r"nvidia\.F3.*'제목만' 을 사유로 쓴 문장")


class JudgeGuardTest(V20Base):
    def test_title_only_reason_is_refused(self):
        self.assert_refused("nvidia", "F5", {"evidence": [TITLE_ONLY], "evidence_up": UP, "evidence_down": DOWN}, "'제목만' 을 사유로")

    def test_paywall_reason_is_accepted(self):
        line = "9월 말 연환산 매출 보도는 유료 기사라 본문을 열지 못해 미확인으로 둔다."
        self.judge("nvidia", "F5", {"evidence": [line], "evidence_up": UP, "evidence_down": DOWN})
        self.assertEqual(self.judgment("nvidia", "F5")["evidence"], [line])


class ResolveSourceUrlsTest(RelayMixin, V20Base):
    def source(self) -> dict:
        return next(s for s in load_json_strict(self.box.run_dir / "sources.json")["items"] if s["source_id"] == self.cand["source_id"])

    def test_relay_sources_are_rewritten_and_the_relay_is_kept(self):
        stages.register_evidence_sources(SLUG)
        self.set_source_url(RELAY)
        out = stages.resolve_source_urls(SLUG, resolve=lambda u: "https://www.reuters.com/a", pause=0)
        self.assertEqual(out, {"resolved": [{"source_id": self.cand["source_id"], "url": "https://www.reuters.com/a"}], "failed": []})
        self.assertEqual((self.source()["url"], self.source()["relay_url"]), ("https://www.reuters.com/a", RELAY))

    def test_failure_leaves_the_source_and_is_reported(self):
        stages.register_evidence_sources(SLUG)
        self.set_source_url(RELAY)

        def boom(_url: str) -> str:
            raise ValueError("막힘")
        out = stages.resolve_source_urls(SLUG, resolve=boom, pause=0)
        self.assertEqual(out["resolved"], [])
        self.assertIn("막힘", out["failed"][0]["reason"])
        self.assertEqual(self.source()["url"], RELAY)
        self.assertNotIn("relay_url", self.source())


if __name__ == "__main__":
    unittest.main()
