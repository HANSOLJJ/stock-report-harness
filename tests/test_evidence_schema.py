# 근거 계층 스키마(sources·evidence·triggers·교차 참조)와 companies cik·news_queries·set_company_field·resolve-cik 를 잠근다
from __future__ import annotations

import copy
import io
import json
import shutil
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import scorecard_cli  # noqa: E402
from tests.test_collect_stage import copy_registry_without_collector_keys  # noqa: E402
from scorecard import engine, registry  # noqa: E402
from scorecard.schema import (  # noqa: E402
    SchemaError,
    load_json_strict,
    validate_companies,
    validate_cross_refs,
    validate_evidence,
    validate_judgments,
    validate_sources,
    validate_triggers,
)

EXISTING = ("ai-scorecard-2026-09-baseline", "ai-scorecard-2026-09-obsreg")
TICKERS = ROOT / "tests" / "fixtures" / "company_tickers.sample.json"
COMPANIES = {"nvidia": {"company_id": "nvidia"}, "openai": {"company_id": "openai"}}
SHA = "a" * 64


def source(sid: str = "SRC-NEWS-nvidia-20260901-abcdef12", **kw) -> dict:
    item = {"source_id": sid, "title": "제목", "publisher": "Reuters", "url": "https://example.com/a",
            "accessed_at": "2026-09-30T01:02:03Z", "sha256": SHA, "conflict_of_interest": None, "note": ""}
    item.update(kw)
    return item


def evidence(eid: str = "EV-nvidia-001", **kw) -> dict:
    item = {"evidence_id": eid, "company_id": "nvidia", "factors": ["F7"], "kind": "news",
            "source_id": "SRC-NEWS-nvidia-20260901-abcdef12", "published_at_utc": "2026-09-01T12:00:00Z",
            "title": "NVIDIA 공급 계약", "excerpt": "원문 발췌", "relevance": "(추론) 매출 집중도에 닿는다",
            "channel": "press", "conditional_impact": "계약이 해지되면 매출 집중이 커진다", "horizon": "2026Q4",
            "counter_evidence": [], "unverified": [], "change_vs_previous": "new"}
    item.update(kw)
    return item


def trigger(tid: str = "TRG-001", **kw) -> dict:
    item = {"trigger_id": tid, "company_id": "nvidia", "factors": ["F7"], "observation": "계약 발표",
            "condition": "계약 해지 공시", "deadline": "2026-12-31", "evidence_ids": ["EV-nvidia-001"],
            "source_ids": ["SRC-NEWS-nvidia-20260901-abcdef12"], "status": "watching",
            "recheck": {"factors": ["F7"], "what": "매출 집중도 재검토"}}
    item.update(kw)
    return item


def wrap(schema: str, items: list, run_id: str = "r") -> dict:
    return {"schema": schema, "run_id": run_id, "items": items}


class CompaniesCollectKeysTest(unittest.TestCase):
    def setUp(self) -> None:
        self.payload = load_json_strict(ROOT / "scorecard" / "companies.json")

    def _with(self, **kw) -> dict:
        p = copy.deepcopy(self.payload)
        p["companies"][0].update(kw)
        return p

    def test_registry_accepts_cik_and_queries(self):
        validate_companies(self._with(cik=1652044, news_queries=["Alphabet", "GOOGL"]))
        validate_companies(self._with(cik=None))

    def test_bad_values_rejected(self):
        for bad in ({"cik": "1652044"}, {"cik": True}, {"cik": 0}, {"news_queries": []},
                    {"news_queries": "Alphabet"}, {"news_queries": ["", "x"]}):
            with self.subTest(bad=bad), self.assertRaises(SchemaError):
                validate_companies(self._with(**bad))


class _RegistrySandbox(unittest.TestCase):
    def setUp(self) -> None:
        self.dir = Path(tempfile.mkdtemp())
        self.path = self.dir / "companies.json"
        copy_registry_without_collector_keys(ROOT / "scorecard" / "companies.json", self.path)
        self.saved = (engine.OUTPUT_DIR, engine.COMPANIES_PATH)
        engine.COMPANIES_PATH = self.path
        self.addCleanup(self._restore)

    def _restore(self) -> None:
        engine.OUTPUT_DIR, engine.COMPANIES_PATH = self.saved
        shutil.rmtree(self.dir, ignore_errors=True)


class SetCompanyFieldTest(_RegistrySandbox):
    def test_only_the_target_line_changes(self):
        before = self.path.read_text(encoding="utf-8").split("\n")
        out = registry.set_company_field("nvidia", "cik", 1045810, path=self.path)
        after = self.path.read_text(encoding="utf-8").split("\n")
        changed = [i for i, (a, b) in enumerate(zip(before, after)) if a != b]
        self.assertEqual(len(before), len(after))
        self.assertEqual(changed, [out["line_no"] - 1])
        self.assertEqual(json.loads(after[changed[0]].rstrip(","))["cik"], 1045810)
        self.assertEqual(after[changed[0]].endswith(","), before[changed[0]].endswith(","))
        # 값만 바꾸는 두 번째 호출도 한 줄 안에서 끝난다.
        registry.set_company_field("nvidia", "news_queries", ["NVIDIA", "NVDA"], path=self.path)
        registry.set_company_field("nvidia", "cik", 1045811, path=self.path)
        final = self.path.read_text(encoding="utf-8").split("\n")
        self.assertEqual([i for i, (a, b) in enumerate(zip(before, final)) if a != b], changed)
        item = json.loads(final[changed[0]].rstrip(","))
        self.assertEqual((item["cik"], item["news_queries"]), (1045811, ["NVIDIA", "NVDA"]))

    def test_last_line_without_comma(self):
        last = load_json_strict(self.path)["companies"][-1]["company_id"]
        registry.set_company_field(last, "cik", 123, path=self.path)
        self.assertEqual(load_json_strict(self.path)["companies"][-1]["cik"], 123)

    def test_refuses_other_keys_unknown_company_and_bad_value(self):
        original = self.path.read_bytes()
        with self.assertRaises(SchemaError):
            registry.set_company_field("nvidia", "ticker", "NVDA2", path=self.path)
        with self.assertRaises(SchemaError):
            registry.set_company_field("nobody", "cik", 1, path=self.path)
        with self.assertRaises(SchemaError):
            registry.set_company_field("nvidia", "cik", "1045810", path=self.path)
        self.assertEqual(self.path.read_bytes(), original)


class ResolveCikCliTest(_RegistrySandbox):
    def _run(self, *argv: str) -> tuple[int, str]:
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = scorecard_cli.main(["resolve-cik", "--from-file", str(TICKERS), *argv])
        return code, buf.getvalue()

    def test_table_without_apply_writes_nothing(self):
        original = self.path.read_bytes()
        code, out = self._run()
        self.assertEqual(code, 0)
        self.assertIn("nvidia\tNVDA\tNone\t1045810\tresolved", out)
        self.assertIn("spacex-xai\tSPCX\tNone\t1181412\tresolved", out)
        self.assertIn("openai\tNone\tNone\tNone\tunlisted", out)
        self.assertEqual(self.path.read_bytes(), original)

    def test_apply_writes_resolved_only(self):
        code, _out = self._run("--apply")
        self.assertEqual(code, 0)
        by_id = {c["company_id"]: c for c in load_json_strict(self.path)["companies"]}
        self.assertEqual(by_id["nvidia"]["cik"], 1045810)
        self.assertEqual(by_id["spacex-xai"]["cik"], 1181412)
        for cid in ("openai", "anthropic"):
            with self.subTest(cid=cid):
                self.assertNotIn("cik", by_id[cid])
        # 한 번 더 돌려도 이미 같은 값이면 쓰지 않는다.
        before = self.path.read_bytes()
        _code, out = self._run("--apply")
        self.assertIn("apply: 0건", out)
        self.assertEqual(self.path.read_bytes(), before)

    def test_json_output(self):
        """2026-10-01 레인 J(F-M-3): CLI 도 --json 을 받는다. 표 없이 JSON 한 줄이다."""
        original = self.path.read_bytes()
        code, out = self._run("--json")
        self.assertEqual(code, 0)
        data = json.loads(out)
        self.assertEqual(len(out.strip().splitlines()), 1)
        rows = {r["company_id"]: r for r in data["rows"]}
        self.assertEqual((rows["spacex-xai"]["cik"], rows["spacex-xai"]["status"], rows["spacex-xai"]["current_cik"]),
                         (1181412, "resolved", None))
        self.assertEqual(rows["openai"]["status"], "unlisted")
        self.assertEqual(data["applied"], [])
        self.assertEqual(self.path.read_bytes(), original)
        code, out = self._run("--json", "--apply", "--company", "nvidia")
        self.assertEqual(json.loads(out)["applied"], [{"company_id": "nvidia", "old": None, "new": 1045810}])

    def test_company_filter(self):
        code, out = self._run("--company", "nvidia", "--apply")
        self.assertEqual(code, 0)
        by_id = {c["company_id"]: c for c in load_json_strict(self.path)["companies"]}
        self.assertEqual(by_id["nvidia"]["cik"], 1045810)
        self.assertNotIn("cik", by_id["apple"])

    def test_real_registry_has_the_resolved_ciks(self):
        """2026-10-01 레인 J: 실제 SEC 조회(resolve-cik --apply)로 상장 12개사의 cik 를 넣었다. 픽스처(실응답 축약)와 같아야 한다."""
        from scorecard.resolve_cik import load_ticker_map, resolve

        real = {c["company_id"]: c for c in load_json_strict(ROOT / "scorecard" / "companies.json")["companies"]}
        rows = resolve(list(real.values()), load_ticker_map(load_json_strict(TICKERS)))
        self.assertEqual({r["company_id"]: real[r["company_id"]].get("cik") for r in rows},
                         {r["company_id"]: r["cik"] for r in rows})
        self.assertEqual(sum(1 for r in rows if r["status"] == "resolved"), 12)
        self.assertEqual(real["spacex-xai"]["cik"], 1181412)
        for cid in ("anthropic", "openai"):
            self.assertNotIn("cik", real[cid])


class ResultsHashInvariantTest(_RegistrySandbox):
    """cik·news_queries 는 calc·aggregate 가 읽지 않는다. 넣어도 results_hash 가 그대로다."""

    def test_obsreg_results_hash_unchanged(self):
        slug = "ai-scorecard-2026-09-obsreg"
        output = self.dir / "output"
        shutil.copytree(self.saved[0] / slug, output / slug)
        engine.OUTPUT_DIR = output
        before = engine.compute(engine.load_context(slug))["results_hash"]
        for cid, cik in (("nvidia", 1045810), ("apple", 320193)):
            registry.set_company_field(cid, "cik", cik, path=self.path)
            registry.set_company_field(cid, "news_queries", [cid.upper()], path=self.path)
        after = engine.compute(engine.load_context(slug))["results_hash"]
        self.assertEqual(before, after)
        self.assertEqual(after, engine.load_results(slug)["results_hash"])


class SourcesTest(unittest.TestCase):
    def test_existing_runs_pass(self):
        for slug in EXISTING:
            with self.subTest(slug=slug):
                validate_sources(load_json_strict(engine.run_dir(slug) / "sources.json"), slug)

    def test_collector_optional_keys(self):
        validate_sources(wrap("scorecard.sources/1", [source(kind="news", company_id="nvidia",
                         published_at_utc="2026-09-01T12:00:00Z", publisher_url="https://reuters.com",
                         raw_ref="data/nvidia/news/google/raw/x.xml")]), "r")
        validate_sources(wrap("scorecard.sources/1", [source("SRC-YF-2026-09-29", kind="price", sha256=None,
                         publisher_url=["https://finance.yahoo.com/quote/NVDA"])]), "r")

    def test_violations(self):
        cases = {
            "필수 키 누락": [{k: v for k, v in source().items() if k != "note"}],
            "알 수 없는 키": [source(extra=1)],
            "중복 id": [source(), source()],
            "sha 형식": [source(sha256="xyz")],
            "published 형식": [source(published_at_utc="2026-09-01")],
            "accessed 형식": [source(accessed_at="어제")],
            "kind 값": [source(kind="blog")],
        }
        for name, items in cases.items():
            with self.subTest(name=name), self.assertRaises(SchemaError):
                validate_sources(wrap("scorecard.sources/1", items), "r")
        with self.assertRaises(SchemaError):
            validate_sources(wrap("scorecard.sources/1", [source()], run_id="other"), "r")
        with self.assertRaises(SchemaError):
            validate_sources(wrap("scorecard.sources/2", [source()]), "r")


class EvidenceTest(unittest.TestCase):
    SRC = {"SRC-NEWS-nvidia-20260901-abcdef12"}

    def check(self, items: list) -> list:
        return validate_evidence(wrap("scorecard.evidence/1", items), COMPANIES, self.SRC, "r")

    def test_valid_candidate_and_confirmed(self):
        self.check([evidence(), evidence("EV-nvidia-002", status="confirmed", reviewer="user", reviewed_at="2026-09-30",
                                         conditional_impact=None, change_vs_previous=None, published_at_utc=None)])

    def test_violations(self):
        cases = {
            "필수 키 누락": {k: v for k, v in evidence().items() if k != "horizon"},
            "id 형식": evidence("EV-openai-001"),
            "id 자리수": evidence("EV-nvidia-1"),
            "factor 밖": evidence(factors=["F10"]),
            "factor 비어 있음": evidence(factors=[]),
            "kind": evidence(kind="price"),
            "출처 없음": evidence(source_id="SRC-X"),
            "발행시각 형식": evidence(published_at_utc="2026-09-01"),
            "excerpt 길이": evidence(excerpt="가" * 601),
            "channel": evidence(channel="blog"),
            "점수 이동": evidence(conditional_impact="F7 -3→-4 가능"),
            "점수 표기": evidence(conditional_impact="함정 -2점 추가"),
            "숫자 타입": evidence(conditional_impact=-1),
            "change": evidence(change_vs_previous="moved"),
            "counter 형식": evidence(counter_evidence="없음"),
            "status": evidence(status="selected"),
            "확정인데 검토자 없음": evidence(status="confirmed"),
            "알 수 없는 회사": evidence(company_id="nobody"),
        }
        for name, item in cases.items():
            with self.subTest(name=name), self.assertRaises(SchemaError):
                self.check([item])
        with self.assertRaises(SchemaError):
            self.check([evidence(), evidence()])

    def test_excerpt_limit_is_inclusive(self):
        self.check([evidence(excerpt="가" * 600)])


class TriggersTest(unittest.TestCase):
    EV = {"EV-nvidia-001"}
    SRC = {"SRC-NEWS-nvidia-20260901-abcdef12"}

    def check(self, items: list) -> list:
        return validate_triggers(wrap("scorecard.triggers/2", items), COMPANIES, self.EV, self.SRC, "r")

    def test_valid(self):
        self.check([trigger(), trigger("TRG-002", evidence_ids=[], source_ids=[], legacy_ref="T-07", note="")])

    def test_future_score_fields_rejected(self):
        for item in (trigger(score=-4), trigger(expected_score=-3), trigger(target_score=2),
                     {**trigger(), "recheck": {"factors": ["F7"], "what": "x", "score_after": -4}}):
            with self.subTest(item=item), self.assertRaisesRegex(SchemaError, "미래 점수"):
                self.check([item])

    def test_violations(self):
        cases = {
            "id 형식": trigger("T-001"),
            "근거 밖": trigger(evidence_ids=["EV-nvidia-009"]),
            "출처 밖": trigger(source_ids=["SRC-X"]),
            "status": trigger(status="active"),
            "deadline": trigger(deadline="2026Q4"),
            "recheck 키": trigger(recheck={"factors": ["F7"]}),
            "필수 키 누락": {k: v for k, v in trigger().items() if k != "condition"},
        }
        for name, item in cases.items():
            with self.subTest(name=name), self.assertRaises(SchemaError):
                self.check([item])
        with self.assertRaises(SchemaError):
            self.check([trigger(), trigger()])
        with self.assertRaises(SchemaError):
            validate_triggers(wrap("scorecard.triggers/1", [trigger()]), COMPANIES, self.EV, self.SRC, "r")


class CrossRefsTest(unittest.TestCase):
    SOURCES = [source(), source("SRC-v15-md")]

    def judgment(self, status: str = "new", **kw) -> dict:
        item = {"judgment_id": "j1", "company_id": "nvidia", "status": status, "source_ids": ["SRC-v15-md"]}
        item.update(kw)
        return item

    def test_existing_runs_pass(self):
        for slug in EXISTING:
            with self.subTest(slug=slug):
                ctx = engine.load_context(slug)
                self.assertIsNone(ctx.evidence)
                self.assertIsNone(ctx.triggers)
                validate_cross_refs(ctx.observations, ctx.judgments, None, ctx.sources["items"])

    def test_missing_sources(self):
        with self.assertRaisesRegex(SchemaError, "observations"):
            validate_cross_refs([{"source_id": "SRC-X"}], [], None, self.SOURCES)
        with self.assertRaisesRegex(SchemaError, "judgments"):
            validate_cross_refs([], [self.judgment(source_ids=["SRC-X"])], None, self.SOURCES)
        with self.assertRaisesRegex(SchemaError, "evidence"):
            validate_cross_refs([], [], [evidence(source_id="SRC-X")], self.SOURCES)

    def test_new_judgment_cites_confirmed_only(self):
        candidate = [evidence()]
        confirmed = [evidence(status="confirmed", reviewer="user", reviewed_at="2026-09-30")]
        with self.assertRaisesRegex(SchemaError, "확정되지 않은"):
            validate_cross_refs([], [self.judgment(evidence_ids=["EV-nvidia-001"])], candidate, self.SOURCES)
        validate_cross_refs([], [self.judgment(evidence_ids=["EV-nvidia-001"])], confirmed, self.SOURCES)
        # 승계 판단은 이 규칙 밖이다. 다만 근거가 실재해야 한다.
        validate_cross_refs([], [self.judgment("carried", evidence_ids=["EV-nvidia-001"])], candidate, self.SOURCES)
        with self.assertRaisesRegex(SchemaError, "evidence.json 에 없음"):
            validate_cross_refs([], [self.judgment("carried", evidence_ids=["EV-nvidia-009"])], candidate, self.SOURCES)
        with self.assertRaisesRegex(SchemaError, "evidence.json 에 없음"):
            validate_cross_refs([], [self.judgment(evidence_ids=["EV-nvidia-001"])], None, self.SOURCES)


class JudgmentEvidenceIdsTest(unittest.TestCase):
    def test_evidence_ids_type(self):
        ctx = engine.load_context("ai-scorecard-2026-09-obsreg")
        payload = load_json_strict(engine.run_dir(ctx.slug) / "judgments.json")
        good = copy.deepcopy(payload)
        good["items"][0]["evidence_ids"] = ["EV-nvidia-001"]
        validate_judgments(good, ctx.companies, ctx.rules.payload, ctx.slug)
        bad = copy.deepcopy(payload)
        bad["items"][0]["evidence_ids"] = "EV-nvidia-001"
        with self.assertRaises(SchemaError):
            validate_judgments(bad, ctx.companies, ctx.rules.payload, ctx.slug)


if __name__ == "__main__":
    unittest.main()
