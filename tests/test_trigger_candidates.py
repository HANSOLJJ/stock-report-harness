# 트리거별 수집 후보 자동 연결(확인 보조)을 잠그는 테스트
from __future__ import annotations

import io
import json
import os
import sys
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
os.environ["SCORECARD_DOTENV"] = ""

import scorecard_cli  # noqa: E402
from scorecard import engine, stages  # noqa: E402
from scorecard.schema import load_json_strict  # noqa: E402
from scorecard.trigger_candidates import (  # noqa: E402
    collect_trigger_candidates,
    estimate_companies,
    match_trigger,
    resolve_trigger_companies,
    tokenize,
    trigger_candidates_for_run,
)
from tests.test_collect_stage import RSS, SLUG, Sandbox  # noqa: E402

NOW = "2026-09-30T00:00:00Z"

COMPANIES = {
    "nvidia": {"company_id": "nvidia", "display_name": "NVIDIA",
               "aliases": ["Nvidia", "NVDA"], "ticker": "NVDA"},
    "tsmc": {"company_id": "tsmc", "display_name": "TSMC",
             "aliases": ["Taiwan Semiconductor"], "ticker": "TSM"},
    "anthropic": {"company_id": "anthropic", "display_name": "Anthropic",
                  "aliases": [], "ticker": None},
}


def prev(ref: str = "baseline/v1.5:TRIG-005", title: str = "TSMC Q3 실적",
         company_id: str | None = None, deadline: str | None = None) -> dict:
    return {"ref": ref, "title": title, "company_id": company_id, "deadline": deadline}


def cand(cid: str, company: str, title: str, pub: str | None = "2026-09-28T00:00:00Z",
         filed: str | None = None) -> dict:
    return {"candidate_id": cid, "company_id": company, "kind": "news", "title": title,
            "url": f"https://example.com/{cid}", "published_at_utc": pub, "filed_at": filed}


class TokenTest(unittest.TestCase):
    def test_english_numeric_rules(self):
        self.assertEqual(tokenize("Oracle Q1 FY27 10-Q results"),
                         {"oracle", "q1", "fy27", "10", "results"})

    def test_short_alpha_and_stopwords_dropped(self):
        got = tokenize("The AI and MS deal")
        self.assertNotIn("the", got)
        self.assertNotIn("and", got)
        self.assertNotIn("ai", got)
        self.assertIn("deal", got)


class EstimateTest(unittest.TestCase):
    def test_company_id_direct(self):
        self.assertEqual(resolve_trigger_companies(prev(company_id="tsmc"), COMPANIES),
                         (["tsmc"], "company_id"))

    def test_estimate_by_name(self):
        self.assertEqual(resolve_trigger_companies(prev(title="TSMC Q3 실적"), COMPANIES),
                         (["tsmc"], "estimated"))

    def test_estimate_by_ticker(self):
        self.assertEqual(resolve_trigger_companies(prev(title="NVDA earnings preview"), COMPANIES),
                         (["nvidia"], "estimated"))

    def test_estimate_by_company_id_word(self):
        self.assertEqual(resolve_trigger_companies(prev(title="Anthropic IPO (10월 예상)"), COMPANIES),
                         (["anthropic"], "estimated"))

    def test_estimate_multiple(self):
        self.assertEqual(estimate_companies("NVIDIA–TSMC supply deal", COMPANIES),
                         ["nvidia", "tsmc"])

    def test_estimate_failure_targets_all(self):
        cids, source = resolve_trigger_companies(prev(title="Global chip supply update"), COMPANIES)
        self.assertEqual((cids, source), (["anthropic", "nvidia", "tsmc"], "all"))


class MatchTest(unittest.TestCase):
    def test_score_and_zero_excluded_and_company_scoped(self):
        trigger = prev(title="Oracle Q1 FY27 실적", company_id="nvidia")
        rows = match_trigger(trigger,
                             [cand("c1", "nvidia", "Oracle reports Q1 FY27 results"),
                              cand("c2", "nvidia", "Oracle opens a new office"),
                              cand("c3", "nvidia", "Unrelated banana harvest"),
                              cand("c4", "tsmc", "Oracle Q1 FY27 results for TSMC fans")],
                             ["nvidia"], tokenize("Oracle Q1 FY27 실적"), None, 5)
        self.assertEqual([(r["candidate_id"], r["score"]) for r in rows], [("c1", 3), ("c2", 1)])
        self.assertEqual(rows[0]["overlap_tokens"], ["fy27", "oracle", "q1"])

    def test_deterministic_order(self):
        trigger = prev(title="Oracle Q1 FY27", company_id="oracle")
        tokens = tokenize("Oracle Q1 FY27")
        rows = match_trigger(
            trigger,
            [cand("C-c1", "oracle", "Oracle Q1 results", "2026-09-28T00:00:00Z"),
             cand("C-c2", "oracle", "Oracle Q1 FY27 results", "2026-09-27T00:00:00Z"),
             cand("C-b", "oracle", "Oracle Q1 FY27 results beat", "2026-09-29T00:00:00Z"),
             cand("C-a", "oracle", "Oracle Q1 FY27 results beat", "2026-09-29T00:00:00Z")],
            ["oracle"], tokens, None, 5)
        self.assertEqual([r["candidate_id"] for r in rows], ["C-a", "C-b", "C-c2", "C-c1"])

    def test_limit_top_n(self):
        trigger = prev(title="Oracle Q1", company_id="oracle")
        tokens = tokenize("Oracle Q1")
        rows = match_trigger(
            trigger, [cand(f"C-{i:02d}", "oracle", f"Oracle Q1 story {i}") for i in range(7)],
            ["oracle"], tokens, None, 5)
        self.assertEqual(len(rows), 5)

    def test_after_deadline_mark(self):
        trigger = prev(title="Oracle Q1", company_id="oracle", deadline="2026-09-10")
        tokens = tokenize("Oracle Q1")
        rows = match_trigger(
            trigger,
            [cand("late", "oracle", "Oracle Q1 update", "2026-09-28T00:00:00Z"),
             cand("early", "oracle", "Oracle Q1 preview", "2026-09-01T00:00:00Z"),
             {**cand("nodate", "oracle", "Oracle Q1 rumor"), "published_at_utc": None},
             {**cand("file", "oracle", "Oracle 10-Q"), "published_at_utc": None,
              "filed_at": "2026-09-20", "kind": "filing"}],
            ["oracle"], tokens, "2026-09-10", 5)
        self.assertEqual({r["candidate_id"]: r["after_deadline"] for r in rows},
                         {"late": True, "early": False, "nodate": False, "file": True})


class CarrierTest(unittest.TestCase):
    def test_watching_text_deadline_and_carried_by(self):
        carrier = {"trigger_id": "TRG-001", "company_id": "amazon", "status": "watching",
                   "observation": "Hugging Face closing", "condition": "클로징 확인",
                   "deadline": "2026-12-31",
                   "carry": {"ref": "baseline/v1.5:TRIG-001", "checked_at": "2026-10-01",
                             "finding": "확인 중"}}
        out = collect_trigger_candidates(
            [prev("baseline/v1.5:TRIG-001", "클로징 임박")],
            [cand("c1", "nvidia", "Hugging Face closing soon")],
            COMPANIES, current_watching=[carrier], limit=5)
        # 제목에는 영문 토큰이 없어 이어받은 watching 문구로만 붙는다.
        self.assertEqual(out[0]["carried_by"], ["TRG-001"])
        self.assertEqual(out[0]["deadline"], "2026-12-31")
        self.assertEqual([(c["candidate_id"], c["score"]) for c in out[0]["candidates"]],
                         [("c1", 3)])

    def test_previous_deadline_wins(self):
        carrier = {"trigger_id": "TRG-002", "company_id": "tsmc", "status": "watching",
                   "observation": "TSMC Q3", "condition": "실적 확인", "deadline": "2026-12-31",
                   "carry": {"ref": "baseline/v1.5:TRIG-005", "checked_at": "2026-10-01",
                             "finding": "확인 중"}}
        out = collect_trigger_candidates(
            [prev("baseline/v1.5:TRIG-005", "TSMC Q3 실적", deadline="2026-10-20")],
            [], COMPANIES, current_watching=[carrier], limit=5)
        self.assertEqual(out[0]["deadline"], "2026-10-20")

    def test_guess_failed_flag(self):
        out = collect_trigger_candidates([prev(title="Global chip supply update")], [],
                                         COMPANIES, limit=5)
        self.assertTrue(out[0]["company_guess_failed"])
        self.assertEqual(out[0]["company_source"], "all")


class CliTest(unittest.TestCase):
    def setUp(self) -> None:
        self.box = Sandbox(("nvidia", "openai"))
        self.addCleanup(self.box.close)
        stages.collect(SLUG, kinds=("news",), from_file=str(RSS), now=NOW)
        run_dir = engine.run_dir(SLUG)
        (run_dir / "evidence" / "candidates.json").write_text(json.dumps(
            {"schema": "scorecard.candidates/1", "run_id": SLUG,
             "window": {"since": "2026-04-02", "until": "2026-09-29"},
             "items": [
                 {**cand("google:aaa", "nvidia", "Nvidia and Hugging Face close deal",
                         "2026-09-29T00:00:00Z"),
                  "source": {"name": "Reuters", "url": "https://www.reuters.com"},
                  "raw_ref": "test", "content_hash": "x" * 16, "source_id": "SRC-TEST-1"},
                 cand("google:bbb", "nvidia", "Completely unrelated banana harvest",
                      "2026-09-28T00:00:00Z"),
             ]}, ensure_ascii=False, indent=2), encoding="utf-8")
        self.before_hashes = stages.current_hashes(SLUG)
        self.before_files = sorted(p.relative_to(run_dir).as_posix()
                                   for p in run_dir.rglob("*") if p.is_file())

    def cli(self, *argv: str) -> tuple[int, str]:
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = scorecard_cli.main([str(a) for a in argv])
        return code, out.getvalue() + err.getvalue()

    def test_json_shape_and_limit(self):
        code, text = self.cli("trigger-candidates", SLUG, "--json")
        self.assertEqual(code, 0)
        data = json.loads(text)
        self.assertEqual((data["schema"], data["run_id"], data["limit"]), (
            "scorecard.trigger_candidates/1", SLUG, 5))
        self.assertEqual(len(data["items"]), 39)
        for entry in data["items"]:
            self.assertEqual(sorted(entry),
                             ["candidates", "carried_by", "company_guess_failed", "company_ids",
                              "company_source", "deadline", "ref", "title"])
            self.assertLessEqual(len(entry["candidates"]), 5)
            for row in entry["candidates"]:
                self.assertEqual(sorted(row),
                                 ["after_deadline", "candidate_id", "company_id", "date",
                                  "filed_at", "kind", "overlap_tokens", "published_at_utc",
                                  "score", "title", "url"])
                self.assertGreater(row["score"], 0)
                self.assertEqual(row["overlap_tokens"], sorted(row["overlap_tokens"]))
            rows = entry["candidates"]
            for left, right in zip(rows, rows[1:]):
                lp = left["published_at_utc"] or left["filed_at"] or ""
                rp = right["published_at_utc"] or right["filed_at"] or ""
                self.assertTrue(
                    (left["score"], lp) > (right["score"], rp)
                    or (left["score"] == right["score"] and lp == rp
                        and left["candidate_id"] <= right["candidate_id"]),
                    (left, right))
        first = next(e for e in data["items"] if e["ref"] == "baseline/v1.5:TRIG-001")
        self.assertEqual(first["company_ids"], ["nvidia"])
        self.assertEqual([(c["candidate_id"], c["score"]) for c in first["candidates"]],
                         [("google:aaa", 3)])
        code, text = self.cli("trigger-candidates", SLUG, "--json", "--limit", "1")
        self.assertEqual(code, 0)
        self.assertTrue(all(len(e["candidates"]) <= 1 for e in json.loads(text)["items"]))

    def test_real_registry_estimation(self):
        data = trigger_candidates_for_run(SLUG, limit=1)
        by_ref = {e["ref"]: e for e in data["items"]}
        self.assertEqual(by_ref["baseline/v1.5:TRIG-005"]["company_ids"], ["tsmc"])
        self.assertEqual(by_ref["baseline/v1.5:TRIG-006"]["company_ids"], ["amazon"])

    def test_human_output_and_input_hashes_unchanged(self):
        code, text = self.cli("trigger-candidates", SLUG)
        self.assertEqual(code, 0)
        self.assertIn("baseline/v1.5:TRIG-001", text)
        self.assertIn("기업", text)
        self.assertIn("겹침", text)
        run_dir = engine.run_dir(SLUG)
        self.assertEqual(stages.current_hashes(SLUG), self.before_hashes)
        self.assertEqual(sorted(p.relative_to(run_dir).as_posix()
                                for p in run_dir.rglob("*") if p.is_file()), self.before_files)
        for key in ("observations", "judgments", "evidence", "triggers", "sources", "run"):
            if key in self.before_hashes:
                self.assertEqual(stages.current_hashes(SLUG)[key], self.before_hashes[key])
        code, _ = self.cli("trigger-candidates", SLUG, "--json", "--limit", "0")
        self.assertEqual(code, 1)


if __name__ == "__main__":
    unittest.main()
