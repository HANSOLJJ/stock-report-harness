# collect 단계(후보 파일 결정론, 창 C-17, SEC_UA 없는 공시, 가격 관측·출처 등록과 중복 거부)를 임시 샌드박스에서 잠근다
from __future__ import annotations

import json
import os
import random
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard import engine, evidence_lib, registry, schema, stages  # noqa: E402
from scorecard.paths import run_paths  # noqa: E402
from scorecard.schema import SchemaError, load_json_strict  # noqa: E402

FIXTURES = ROOT / "tests" / "fixtures"
RSS = FIXTURES / "google_news_rss.sample.xml"
EDGAR = FIXTURES / "edgar_submissions.CIK0001045810.sample.json"
QUOTES = FIXTURES / "yfinance_quotes.sample.json"
SLUG = "ai-scorecard-2026-09-evidence"
NOW = "2026-09-30T00:00:00Z"


def copy_registry_without_collector_keys(src: Path, dst: Path) -> None:
    """레지스트리를 복사하되 수집기 전용 키(cik·news_queries)를 뺀다. 한 줄 = 한 기업 형식은 그대로다.

    2026-10-01 레인 J: 실제 레지스트리에 12개사 cik 와 일반 단어 회사의 news_queries 가 들어갔다. 샌드박스 테스트는
    키가 없는 상태에서 시작해야 skipped_no_cik·set_company_field·resolve-cik --apply 를 검사할 수 있다.
    """
    lines = []
    for line in src.read_text(encoding="utf-8").split("\n"):
        body = line.strip().rstrip(",")
        if body.startswith('{"company_id"'):
            item = {k: v for k, v in json.loads(body).items() if k not in schema.COMPANY_SETTABLE_KEYS}
            line = registry.render_company_line(item) + ("," if line.rstrip().endswith(",") else "")
        lines.append(line)
    dst.write_text("\n".join(lines), encoding="utf-8", newline="\n")


class Sandbox:
    """출력 묶음·레지스트리·수집 캐시를 임시 폴더로 돌린다. 정본은 읽기만 한다."""

    def __init__(self, companies: tuple[str, ...] = ("nvidia", "tsmc", "openai"), *, as_of: str = "2026-09-29",
                 slug: str = SLUG, init: bool = True) -> None:
        self.dir = Path(tempfile.mkdtemp())
        self.slug = slug
        self.saved = (engine.OUTPUT_DIR, engine.COMPANIES_PATH, evidence_lib.DATA_ROOT, os.environ.get("SEC_UA"))
        self.companies = self.dir / "companies.json"
        copy_registry_without_collector_keys(self.saved[1], self.companies)
        engine.OUTPUT_DIR = self.dir / "output"
        engine.COMPANIES_PATH = self.companies
        evidence_lib.DATA_ROOT = self.dir / "data"
        os.environ.pop("SEC_UA", None)
        registry.set_company_field("nvidia", "cik", 1045810, path=self.companies)
        if not init:
            return
        stages.init_run(slug, as_of=as_of, title="근거 계층 시험", request="근거 계층 시험", purpose="근거 계층 시험",
                        companies=list(companies), rule_version="v1.8")

    @property
    def run_dir(self) -> Path:
        return engine.run_dir(self.slug)

    def close(self) -> None:
        engine.OUTPUT_DIR, engine.COMPANIES_PATH, evidence_lib.DATA_ROOT, sec_ua = self.saved
        if sec_ua is not None:
            os.environ["SEC_UA"] = sec_ua
        shutil.rmtree(self.dir, ignore_errors=True)


class _SandboxTest(unittest.TestCase):
    companies: tuple[str, ...] = ("nvidia", "tsmc", "openai")

    def setUp(self) -> None:
        self.box = Sandbox(self.companies)
        self.addCleanup(self.box.close)

    def candidates(self) -> dict:
        return load_json_strict(run_paths(SLUG).candidates)


class WindowTest(_SandboxTest):
    def test_news_window_is_since_to_info_cutoff(self):
        out = stages.collect(SLUG, companies=["nvidia"], kinds=("news",), from_file=str(RSS), now=NOW)
        self.assertEqual(out["window"], {"since": "2026-04-02", "until": "2026-09-29"})
        items = self.candidates()["items"]
        days = sorted(i["published_at_utc"][:10] for i in items)
        # 09-30 기사 셋은 정보 컷오프(09-29) 뒤라 버린다(C-17).
        self.assertEqual(days, ["2026-09-28", "2026-09-29"])
        self.assertEqual({i["company_id"] for i in items}, {"nvidia"})
        # 창 시작을 좁히면 그 앞 기사도 버린다.
        stages.collect(SLUG, companies=["nvidia"], kinds=("news",), since="2026-09-29", from_file=str(RSS), now=NOW)
        self.assertEqual([i["published_at_utc"][:10] for i in self.candidates()["items"]], ["2026-09-29"])

    def test_candidate_fields_have_no_fetch_time(self):
        stages.collect(SLUG, kinds=("news",), from_file=str(RSS), now=NOW)
        payload = self.candidates()
        self.assertEqual(payload["schema"], "scorecard.candidates/1")
        blob = json.dumps(payload)
        for stamp_key in ("first_seen_utc", "updated_utc", "accessed_at", "query"):
            self.assertNotIn(stamp_key, blob)
        news = payload["items"][0]
        self.assertEqual(set(news), {"candidate_id", "company_id", "kind", "title", "url", "published_at_utc", "source",
                                     "raw_ref", "content_hash", "source_id"})
        self.assertTrue(news["candidate_id"].startswith("google:"))

    def test_news_and_filings_do_not_touch_sources(self):
        before = (self.box.run_dir / "sources.json").read_bytes()
        stages.collect(SLUG, kinds=("news",), from_file=str(RSS), now=NOW)
        stages.collect(SLUG, kinds=("filings",), from_file=str(EDGAR), now=NOW)
        self.assertEqual((self.box.run_dir / "sources.json").read_bytes(), before)

    def test_filings_from_file_respect_window_and_forms(self):
        stages.collect(SLUG, kinds=("filings",), from_file=str(EDGAR), now=NOW)
        filings = [i for i in self.candidates()["items"] if i["kind"] == "filing"]
        self.assertTrue(filings)
        for f in filings:
            self.assertGreaterEqual(f["filed_at"], "2026-04-02")
            self.assertLessEqual(f["filed_at"], "2026-09-29")
            self.assertIn(f["form"], {"8-K", "10-Q", "10-K", "20-F", "6-K"})
            self.assertIsNone(f["published_at_utc"])   # 시각을 지어내지 않는다
        only_8k = stages.collect(SLUG, kinds=("filings",), forms=["8-K"], from_file=str(EDGAR), now=NOW)
        self.assertEqual(only_8k["filings"][0]["status"], "collected")

    def test_filings_without_user_agent_are_skipped_not_failed(self):
        out = stages.collect(SLUG, now=NOW, kinds=("filings",))
        by_id = {r["company_id"]: r["status"] for r in out["filings"]}
        self.assertEqual(by_id, {"nvidia": "skipped_no_user_agent", "tsmc": "skipped_no_cik", "openai": "skipped_no_cik"})
        self.assertTrue(run_paths(SLUG).candidates.is_file())

    def test_non_ascii_sec_ua_fails_per_company_before_requests(self):
        """2026-10-01 레인 J(F-M-1): 영문이 아닌 SEC_UA 는 요청 전에 회사별 failed 다. 가격(파일)은 영향받지 않는다."""
        os.environ["SEC_UA"] = "Harness 홍길동 hong@example.com"   # Sandbox.close 가 원래 값으로 되돌린다
        self.addCleanup(os.environ.pop, "SEC_UA", None)
        with mock.patch.object(evidence_lib.urllib.request, "urlopen", side_effect=AssertionError("요청하면 안 된다")):
            out = stages.collect(SLUG, now=NOW, kinds=("news", "filings"))
            prices = stages.collect(SLUG, kinds=("prices",), from_file=str(QUOTES), now=NOW)
        rows = [*out["news"], *out["filings"]]
        failed = sorted(r["company_id"] for r in rows if r["status"] == "failed"
                        and r["error"].startswith("SEC_UA 는 영문으로 적는다(HTTP 머리글 제약)"))
        self.assertEqual(failed, ["nvidia", "nvidia", "openai", "tsmc"])   # 뉴스 셋 + 공시(cik 있는 nvidia)
        self.assertTrue(all("홍길동" not in r.get("error", "") for r in rows))
        self.assertEqual({r["company_id"]: r["status"] for r in prices["prices"]},
                         {"nvidia": "collected", "tsmc": "collected", "openai": "skipped_unlisted"})

    def test_argument_errors(self):
        with self.assertRaises(SchemaError):
            stages.collect(SLUG, kinds=("news", "prices"), from_file=str(RSS))
        with self.assertRaises(SchemaError):
            stages.collect(SLUG, kinds=("blogs",))
        with self.assertRaises(SchemaError):
            stages.collect(SLUG, companies=["apple"], kinds=("news",))
        with self.assertRaises(SchemaError):
            stages.collect(SLUG, kinds=("news",), since="2026-10-01")

    def test_dry_run_writes_nothing(self):
        out = stages.collect(SLUG, dry_run=True)
        self.assertEqual({r["status"] for r in out["news"]}, {"dry_run"})
        self.assertIn("hl=en-US", out["news"][0]["urls"][0])
        self.assertFalse(run_paths(SLUG).candidates.exists())
        self.assertFalse((self.box.dir / "data").exists())


class DeterminismTest(unittest.TestCase):
    def _collect_bytes(self, companies: tuple[str, ...]) -> bytes:
        box = Sandbox(companies)
        try:
            stages.collect(SLUG, kinds=("news",), from_file=str(RSS), now=NOW)
            stages.collect(SLUG, kinds=("filings",), from_file=str(EDGAR), now=NOW)
            return run_paths(SLUG).candidates.read_bytes()
        finally:
            box.close()

    def test_same_input_same_bytes(self):
        self.assertEqual(self._collect_bytes(("nvidia", "openai")), self._collect_bytes(("nvidia", "openai")))

    def test_input_order_does_not_matter(self):
        self.assertEqual(self._collect_bytes(("nvidia", "tsmc", "openai")), self._collect_bytes(("openai", "tsmc", "nvidia")))

    def test_shuffled_cache_same_bytes(self):
        box = Sandbox(("nvidia", "openai"))
        self.addCleanup(box.close)
        stages.collect(SLUG, kinds=("news",), from_file=str(RSS), now=NOW)
        stages.collect(SLUG, kinds=("filings",), from_file=str(EDGAR), now=NOW)
        first = run_paths(SLUG).candidates.read_bytes()
        for rel_path in ("nvidia/news/google/normalized.json", "nvidia/filings/index.json"):
            path = evidence_lib.DATA_ROOT / rel_path
            payload = json.loads(path.read_text(encoding="utf-8"))
            random.Random(7).shuffle(payload["items"])
            path.write_text(json.dumps(payload), encoding="utf-8")
        run = load_json_strict(box.run_dir / "run.json")
        stages.write_candidates(SLUG, since="2026-04-02", until="2026-09-29", company_ids=list(reversed(run["companies"])))
        self.assertEqual(run_paths(SLUG).candidates.read_bytes(), first)


class PricesTest(_SandboxTest):
    def test_prices_add_observations_and_source(self):
        before = load_json_strict(self.box.run_dir / "observations.json")["items"]
        out = stages.collect(SLUG, kinds=("prices",), from_file=str(QUOTES), now=NOW)
        rows = {r["company_id"]: r for r in out["prices"]}
        self.assertEqual(rows["openai"]["status"], "skipped_unlisted")
        self.assertEqual(rows["nvidia"]["status"], "collected")
        items = load_json_strict(self.box.run_dir / "observations.json")["items"]
        added = items[len(before):]
        self.assertEqual(items[:len(before)], before)   # 기존 관측은 그대로다
        self.assertEqual(sorted(o["observation_id"] for o in added),
                         ["nvidia.market_cap.2026-09-29", "nvidia.price.2026-09-29",
                          "tsmc.market_cap.2026-09-29", "tsmc.price.2026-09-29"])
        by_id = {o["observation_id"]: o for o in added}
        # 픽스처에는 조회일이 없다. 시점을 증명할 수 없으니 벤더 시총을 쓰지 않고, ADR 은 추정으로 채우지 않는다.
        self.assertEqual(by_id["nvidia.market_cap.2026-09-29"]["basis"]["method"], "price_x_shares")
        self.assertEqual(by_id["tsmc.market_cap.2026-09-29"]["status"], "collection_failed")
        sources = load_json_strict(self.box.run_dir / "sources.json")["items"]
        yf = [s for s in sources if s["source_id"] == "SRC-YF-2026-09-29"]
        self.assertEqual(len(yf), 1)
        self.assertEqual(yf[0]["accessed_at"], NOW)
        engine.load_context(SLUG)   # 교차 참조 포함 엄격 검증 통과

    def test_same_observation_twice_is_refused(self):
        stages.collect(SLUG, kinds=("prices",), from_file=str(QUOTES), now=NOW)
        obs_before = (self.box.run_dir / "observations.json").read_bytes()
        src_before = (self.box.run_dir / "sources.json").read_bytes()
        # 2026-10-01 V2-7: 같은 출처로 이미 기록된 회사는 실패가 아니라 skipped_existing 이다. 기록할 것이 없으면 파일을 쓰지 않는다.
        out = stages.collect(SLUG, kinds=("prices",), from_file=str(QUOTES), now=NOW)
        rows = {r["company_id"]: r for r in out["prices"]}
        for cid in ("nvidia", "tsmc"):
            self.assertEqual(rows[cid]["status"], "skipped_existing")
            self.assertNotIn("error", rows[cid])
        self.assertEqual((self.box.run_dir / "observations.json").read_bytes(), obs_before)
        self.assertEqual((self.box.run_dir / "sources.json").read_bytes(), src_before)

    def test_retry_after_partial_failure_records_only_the_missing_company(self):
        """레인 M 재시도 상황. 먼저 수집된 회사가 중복으로 빠져도 나머지는 기록된다."""
        quotes = json.loads(QUOTES.read_text(encoding="utf-8"))
        only_nvda = self.box.dir / "nvda.json"
        only_nvda.write_text(json.dumps({"NVDA": quotes["NVDA"]}), encoding="utf-8")
        stages.collect(SLUG, kinds=("prices",), from_file=str(only_nvda), now=NOW)
        later = "2026-09-30T01:00:00Z"
        out = stages.collect(SLUG, kinds=("prices",), from_file=str(QUOTES), now=later)
        self.assertEqual({r["company_id"]: r["status"] for r in out["prices"]},
                         {"nvidia": "skipped_existing", "tsmc": "collected", "openai": "skipped_unlisted"})
        ids = [o["observation_id"] for o in load_json_strict(self.box.run_dir / "observations.json")["items"]]
        self.assertEqual(ids.count("nvidia.price.2026-09-29"), 1)
        self.assertIn("tsmc.price.2026-09-29", ids)
        # 2026-10-01 V2-7: 나중에 들어간 회사의 시세 주소가 같은 출처 항목에 덧붙고, 첫 조회 시각은 그대로다.
        yf = [s for s in load_json_strict(self.box.run_dir / "sources.json")["items"] if s["source_id"] == "SRC-YF-2026-09-29"]
        self.assertEqual(len(yf), 1)
        self.assertEqual(yf[0]["url"], "https://finance.yahoo.com/quote/NVDA")
        self.assertEqual(yf[0]["publisher_url"], ["https://finance.yahoo.com/quote/NVDA", "https://finance.yahoo.com/quote/TSM"])
        self.assertEqual(yf[0]["accessed_at"], NOW)
        self.assertIn(f"재조회 {later}: TSM", yf[0]["note"])
        engine.load_context(SLUG)

    def test_invalid_observation_fails_that_company_only(self):
        """한 회사의 관측이 스키마를 어기면(NaN 종가) 그 회사만 failed 이고 나머지는 기록된다(F-M-2)."""
        quotes = json.loads(QUOTES.read_text(encoding="utf-8"))
        quotes["TSM"]["close"] = float("nan")
        path = self.box.dir / "nan.json"
        path.write_text(json.dumps(quotes), encoding="utf-8")   # json 은 NaN 을 리터럴로 쓴다
        out = stages.collect(SLUG, kinds=("prices",), from_file=str(path), now=NOW)
        rows = {r["company_id"]: r for r in out["prices"]}
        self.assertEqual((rows["nvidia"]["status"], rows["tsmc"]["status"]), ("collected", "failed"))
        self.assertIn("price", rows["tsmc"]["error"])
        ids = {o["observation_id"] for o in load_json_strict(self.box.run_dir / "observations.json")["items"]}
        self.assertIn("nvidia.price.2026-09-29", ids)
        self.assertNotIn("tsmc.price.2026-09-29", ids)
        engine.load_context(SLUG)

    def test_missing_ticker_in_file_fails_that_company_only(self):
        quotes = self.box.dir / "quotes.json"
        quotes.write_text(json.dumps({"NVDA": json.loads(QUOTES.read_text(encoding="utf-8"))["NVDA"]}), encoding="utf-8")
        out = stages.collect(SLUG, kinds=("prices",), from_file=str(quotes), now=NOW)
        rows = {r["company_id"]: r["status"] for r in out["prices"]}
        self.assertEqual(rows, {"nvidia": "collected", "tsmc": "failed", "openai": "skipped_unlisted"})


if __name__ == "__main__":
    unittest.main()
