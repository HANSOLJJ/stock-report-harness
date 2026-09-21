# ADD-03 — 이전 실행 이어받기(`init --from-run`)가 **기존 기업을 한 글자도 건드리지 않는지** 잠근다
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard import compare, engine, registry, stages  # noqa: E402
from scorecard.rules import load_rules  # noqa: E402
from scorecard.schema import SchemaError, canonical_json, load_json_strict, validate_run  # noqa: E402

PRIOR = "ai-scorecard-2026-09-obsreg"
CLI = ROOT / "scripts" / "scorecard_cli.py"

NEWCOMER = {
    "company_id": "samsung", "display_name": "Samsung Electronics", "aliases": ["삼성전자"],
    "type": "부품", "listed": True, "ticker": "005930", "exchange": "KRX",
    "share_basis": "common", "adr_ratio": None, "reporting_currency": "KRW", "scope": "반도체·디바이스 전반",
}


class _Sandbox:
    """실행을 임시 디렉터리 안에서만 만든다. 승인된 실행과 레지스트리 정본은 읽기만 한다."""

    def __init__(self) -> None:
        self.dir = Path(tempfile.mkdtemp())
        self.saved = (engine.RUNS_DIR, engine.COMPANIES_PATH, stages.PLAN_DIR, stages.RESEARCH_DIR)
        runs = self.dir / "runs"
        runs.mkdir()
        shutil.copytree(self.saved[0] / PRIOR, runs / PRIOR)
        self.companies = self.dir / "companies.json"
        shutil.copyfile(self.saved[1], self.companies)
        engine.RUNS_DIR = runs
        engine.COMPANIES_PATH = self.companies
        stages.PLAN_DIR = self.dir / "plan"
        stages.RESEARCH_DIR = self.dir / "research"

    def close(self) -> None:
        engine.RUNS_DIR, engine.COMPANIES_PATH, stages.PLAN_DIR, stages.RESEARCH_DIR = self.saved
        shutil.rmtree(self.dir, ignore_errors=True)

    def build(self, slug: str, **kwargs) -> dict[str, Path]:
        paths = stages.init_run(slug, from_run=PRIOR, title=f"이어받기 {slug}", **kwargs)
        stages.research(slug)
        stages.calculate(slug)
        return paths


class ContinueRunTest(unittest.TestCase):
    """이어받기가 무엇을 그대로 옮기고 무엇을 새로 쓰는지 고정한다."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.box = _Sandbox()
        try:
            cls.prior_dir = engine.RUNS_DIR / PRIOR
            cls.prior_run = load_json_strict(cls.prior_dir / "run.json")
            registry.add_company(dict(NEWCOMER), path=cls.box.companies)
            cls.box.build("ai-scorecard-2026-10-carry")
            cls.box.build("ai-scorecard-2026-10-add", add_companies=["samsung"])
        except Exception:
            cls.box.close()
            raise

    @classmethod
    def tearDownClass(cls) -> None:
        cls.box.close()

    def read(self, slug: str, name: str) -> dict:
        return load_json_strict(engine.RUNS_DIR / slug / f"{name}.json")

    def test_judgment_items_are_copied_character_for_character(self):
        """**가장 위험한 자리다.** `status` 를 재작성하면 기존 기업의 factor 상태와 경고가 움직인다."""
        before = self.read(PRIOR, "judgments")["items"]
        after = self.read("ai-scorecard-2026-10-carry", "judgments")["items"]
        self.assertEqual(canonical_json(after), canonical_json(before))
        self.assertEqual(len(after), 114)
        # 이어받았다는 표시를 항목에 찍지 않았다 — `carried` 는 기준선 승계라는 뜻으로 이미 점유돼 있다.
        for item in after:
            self.assertIn(item["status"], {"carried", "new"})
            self.assertNotIn(item.get("carried_from"), {PRIOR, f"run:{PRIOR}"})

    def test_observation_items_are_copied_unchanged(self):
        before = self.read(PRIOR, "observations")["items"]
        after = self.read("ai-scorecard-2026-10-carry", "observations")["items"]
        self.assertEqual(canonical_json(after), canonical_json(before))
        self.assertEqual(len(after), 363)

    def test_sources_are_copied_whole_not_rebuilt_from_the_baseline(self):
        """기준선 4건으로 덮으면 실행 도중 늘어난 출처가 사라져 관측의 `source_id` 가 장부에서 사라진다."""
        before = self.read(PRIOR, "sources")
        after = self.read("ai-scorecard-2026-10-carry", "sources")
        self.assertEqual(canonical_json(after["items"]), canonical_json(before["items"]))
        self.assertEqual(len(after["items"]), 13)
        self.assertEqual(after["run_id"], "ai-scorecard-2026-10-carry")   # run_id 만 새것이다

        cited = {o["source_id"] for o in self.read("ai-scorecard-2026-10-carry", "observations")["items"]}
        listed = {s["source_id"] for s in after["items"]}
        self.assertFalse(cited - listed, "관측이 인용한 출처가 장부에 없다")

    def test_run_carries_the_prior_settings(self):
        run = validate_run(self.read("ai-scorecard-2026-10-carry", "run"), "ai-scorecard-2026-10-carry")
        for key in ("as_of", "price_as_of", "info_cutoff", "baseline_id", "rule_version", "purpose", "companies"):
            with self.subTest(key=key):
                self.assertEqual(run[key], self.prior_run[key])
        self.assertEqual(run["baseline_id"], "v1.5")     # 점수 비교 기준선은 그대로다
        self.assertEqual(run["rule_version"], self.prior_run["rule_version"])

    def test_rule_hash_is_recomputed_from_the_rule_file(self):
        """옛 해시를 옮기면 `engine.load_context` 의 등호 검사가 막는다."""
        run = self.read("ai-scorecard-2026-10-carry", "run")
        self.assertEqual(run["rule_hash"], load_rules(run["rule_version"]).hash)
        engine.load_context("ai-scorecard-2026-10-carry")                # 막히지 않는다

    def test_decisions_are_carried(self):
        run = self.read("ai-scorecard-2026-10-carry", "run")
        self.assertTrue(self.prior_run["decisions"])
        self.assertEqual(canonical_json(run["decisions"]), canonical_json(self.prior_run["decisions"]))

    def test_dropping_decisions_creates_pending_rule_decisions(self):
        """반례로 고정한다. 결정을 안 이어받으면 기존 기업 여러 factor 가 미결로 떨어진다."""
        with_decisions = engine.load_results("ai-scorecard-2026-10-carry")
        self.assertEqual(with_decisions["pending_rule_decisions"], [])

        self.box.build("ai-scorecard-2026-10-nodec", carry_decisions=True, decisions=[])
        self.assertEqual(engine.load_results("ai-scorecard-2026-10-nodec")["pending_rule_decisions"], [])

        self.box.build("ai-scorecard-2026-10-drop", carry_decisions=False)
        dropped = engine.load_results("ai-scorecard-2026-10-drop")
        self.assertEqual(self.read("ai-scorecard-2026-10-drop", "run")["decisions"], [])
        self.assertTrue(dropped["pending_rule_decisions"])
        statuses = {f["status"] for c in dropped["companies"] for f in c["factors"].values()}
        self.assertIn("needs_rule_decision", statuses)

    def test_decision_override_replaces_only_the_same_id(self):
        first = self.prior_run["decisions"][0]
        # 선택지는 규칙이 정한 것만 쓸 수 있다. 여기서 보는 것은 **같은 id 만 덮인다**는 사실이다.
        override = {**first, "rationale": "이어받기 확인용으로 근거만 다시 적었다", "decided_by": "시험"}
        self.box.build("ai-scorecard-2026-10-over", decisions=[override])
        after = self.read("ai-scorecard-2026-10-over", "run")["decisions"]
        self.assertEqual(len(after), len(self.prior_run["decisions"]))
        self.assertEqual([d for d in after if d["id"] == override["id"]], [override])
        kept = [d for d in after if d["id"] != override["id"]]
        self.assertEqual(canonical_json(kept),
                         canonical_json([d for d in self.prior_run["decisions"] if d["id"] != override["id"]]))

    def test_title_and_purpose_fall_back_to_the_prior_run(self):
        stages.init_run("ai-scorecard-2026-10-title", from_run=PRIOR)
        run = self.read("ai-scorecard-2026-10-title", "run")
        self.assertEqual(run["title"], self.prior_run["title"])
        self.assertEqual(run["purpose"], self.prior_run["purpose"])

    def test_continued_from_records_what_was_inherited(self):
        run = self.read("ai-scorecard-2026-10-add", "run")
        cf = run["continued_from"]
        self.assertEqual(cf["run_id"], PRIOR)
        self.assertEqual(cf["as_of"], self.prior_run["as_of"])
        self.assertEqual(cf["added_companies"], ["samsung"])
        self.assertEqual(cf["hashes"], {k: v for k, v in engine.input_hashes(PRIOR).items()
                                        if k in ("run", "observations", "judgments", "sources")})
        self.assertEqual(cf["results_hash"], engine.load_results(PRIOR)["results_hash"])
        self.assertEqual(cf["approval_id"], load_json_strict(self.prior_dir / "approval.json")["approval_id"])
        validate_run(run, "ai-scorecard-2026-10-add")

    def test_assumptions_name_the_prior_run_and_the_new_work(self):
        carry = self.read("ai-scorecard-2026-10-carry", "run")["assumptions"]
        self.assertIn(f"이전 실행 {PRIOR} 의 관측·판단·출처를 그대로 이어받았다", carry[0])
        self.assertIn("재검증되지 않았다", carry[0])
        self.assertIn("기업을 더하지 않았", carry[1])
        self.assertIn("C-17", carry[2])

        added = self.read("ai-scorecard-2026-10-add", "run")["assumptions"]
        self.assertIn("Samsung Electronics", added[1])
        self.assertIn("새로 조사한 대상", added[1])

    def test_added_company_does_not_move_the_fourteen(self):
        """이 과제의 목적이다. ADD-02 의 1층·2층이 둘 다 통과해야 한다."""
        out = compare.compare_runs("ai-scorecard-2026-10-add", PRIOR)
        self.assertTrue(out["ok"], out["inputs"]["violations"] + out["scores"]["violations"])
        self.assertEqual(out["new_companies"], ["samsung"])
        self.assertEqual(out["scores"]["compared"], 14)
        self.assertEqual(out["subtrees"]["differing"], [])
        self.assertIsNone(out["note"])                    # 위반이 없으면 덧붙일 말이 없다

        results = engine.load_results("ai-scorecard-2026-10-add")
        self.assertEqual(results["population"]["scored"], 14)
        self.assertIn("samsung", [c["company_id"] for c in results["population"]["incomplete"]])

    def test_plan_note_names_the_prior_run_and_keeps_the_baseline(self):
        text = (stages.PLAN_DIR / "ai-scorecard-2026-10-add.md").read_text(encoding="utf-8")
        self.assertIn(f"이전 실행 `{PRIOR}`", text)
        self.assertIn("점수 비교 기준선은 `v1.5` 를 유지한다", text)


class GuardTest(unittest.TestCase):
    """짝이 맞지 않는 호출을 막는다."""

    def setUp(self) -> None:
        self.box = _Sandbox()
        self.addCleanup(self.box.close)

    def test_self_continuation_is_refused(self):
        with self.assertRaises(SchemaError):
            stages.init_run(PRIOR, from_run=PRIOR, force=True)

    def test_add_companies_without_from_run_is_refused(self):
        with self.assertRaises(SchemaError) as cm:
            stages.init_run("ai-scorecard-2026-10-x", as_of="2026-09-02", title="x", request="x",
                            add_companies=["samsung"])
        self.assertIn("--from-run", str(cm.exception))

    def test_unknown_added_company_is_refused(self):
        with self.assertRaises(SchemaError) as cm:
            stages.init_run("ai-scorecard-2026-10-x", from_run=PRIOR, add_companies=["없는회사"])
        self.assertIn("알 수 없는 기업", str(cm.exception))

    def test_missing_prior_run_is_refused(self):
        with self.assertRaises(SchemaError) as cm:
            stages.init_run("ai-scorecard-2026-10-x", from_run="ai-scorecard-없는실행")
        self.assertIn("이어받을 실행이 없다", str(cm.exception))

    def test_as_of_is_required_without_from_run(self):
        with self.assertRaises(SchemaError) as cm:
            stages.init_run("ai-scorecard-2026-10-x", title="x", request="x")
        self.assertIn("--as-of", str(cm.exception))


class BaselinePathRegressionTest(unittest.TestCase):
    """`--from-run` 이 없으면 기존 경로가 한 줄도 달라지면 안 된다."""

    def setUp(self) -> None:
        self.box = _Sandbox()
        self.addCleanup(self.box.close)
        stages.init_run("ai-scorecard-2026-09-probe", as_of="2026-09-02", title="확인용 제목",
                        request="확인용 요청", purpose="확인용 목적")

    def read(self, name: str) -> dict:
        return load_json_strict(engine.RUNS_DIR / "ai-scorecard-2026-09-probe" / f"{name}.json")

    def test_baseline_path_writes_no_continued_from(self):
        run = self.read("run")
        self.assertNotIn("continued_from", run)
        self.assertEqual(list(run), [
            "schema", "run_id", "report_type", "title", "as_of", "price_as_of", "info_cutoff",
            "rule_version", "rule_hash", "baseline_id", "companies", "reference_companies",
            "decisions", "created_at", "purpose", "assumptions",
        ])
        self.assertEqual(run["baseline_id"], "v1.5")
        self.assertEqual(run["rule_version"], "v1.5")

    def test_baseline_assumptions_are_unchanged(self):
        assumptions = self.read("run")["assumptions"]
        self.assertEqual(len(assumptions), 3)
        self.assertTrue(assumptions[0].startswith("원자료와 정성 판단은 기준선 v1.5("))
        self.assertIn("legacy_unverified", assumptions[0])
        self.assertEqual(assumptions[1], "미결 규칙 결정(C-xx)은 run.json.decisions 에 명시된 것만 적용한다")
        self.assertEqual(assumptions[2], "가격 기준일·재무 기간·정보 컷오프는 분리 기록한다(C-17)")

    def test_baseline_inputs_are_the_baseline_ones(self):
        self.assertEqual(len(self.read("observations")["items"]), 227)
        self.assertEqual(len(self.read("judgments")["items"]), 114)
        self.assertEqual([s["source_id"] for s in self.read("sources")["items"]],
                         ["SRC-v15-html", "SRC-v15-md", "SRC-v15-rule", "SRC-v15-handover"])
        self.assertTrue(all(j["status"] == "carried" for j in self.read("judgments")["items"]))

    def test_plan_note_still_points_at_the_baseline(self):
        text = (stages.PLAN_DIR / "ai-scorecard-2026-09-probe.md").read_text(encoding="utf-8")
        self.assertIn("기준선 `v1.5`", text)
        self.assertIn("점수·판정표·원자료를 승계", text)


class PastRunsStillValidateTest(unittest.TestCase):
    """`continued_from` 을 optional 로 더했다. 그 키가 없는 과거 run.json 이 전부 그대로 통과해야 한다."""

    def test_every_committed_run_still_validates(self):
        slugs = sorted(p.name for p in engine.RUNS_DIR.iterdir() if (p / "run.json").is_file())
        self.assertIn(PRIOR, slugs)
        for slug in slugs:
            with self.subTest(slug=slug):
                run = validate_run(load_json_strict(engine.RUNS_DIR / slug / "run.json"), slug)
                self.assertNotIn("continued_from", run)

    def test_broken_continued_from_is_refused(self):
        base = load_json_strict(engine.RUNS_DIR / PRIOR / "run.json")
        good = {
            "run_id": PRIOR, "as_of": "2026-09-02", "rule_hash": "a" * 64,
            "hashes": {k: "b" * 64 for k in ("run", "observations", "judgments", "sources")},
            "results_hash": None, "approval_id": None, "added_companies": [],
        }
        validate_run({**base, "continued_from": good}, PRIOR)
        cases = {
            "키 누락": {k: v for k, v in good.items() if k != "approval_id"},
            "알 수 없는 키": {**good, "note": "x"},
            "해시 형식": {**good, "rule_hash": "짧다"},
            "hashes 키 누락": {**good, "hashes": {"run": "b" * 64}},
            "날짜 형식": {**good, "as_of": "2026-09"},
            "없는 기업": {**good, "added_companies": ["없는회사"]},
        }
        for name, cf in cases.items():
            with self.subTest(case=name):
                with self.assertRaises(SchemaError):
                    validate_run({**base, "continued_from": cf}, PRIOR)


class InitCliTest(unittest.TestCase):
    def run_cli(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, "-X", "utf8", str(CLI), "init", *args],
                              capture_output=True, text=True, encoding="utf-8", cwd=str(ROOT))

    def test_as_of_is_no_longer_an_argparse_requirement(self):
        """`--from-run` 이면 기준일이 이전 실행에서 온다. 그래서 argparse 가 아니라 함수가 본다."""
        res = self.run_cli("ai-scorecard-2026-10-x", "--title", "x", "--request", "x")
        self.assertEqual(res.returncode, 1, res.stderr)        # argparse 의 2 가 아니다
        self.assertIn("--as-of", res.stderr)
        self.assertIn("[FAIL]", res.stderr)

    def test_usage_line_documents_from_run(self):
        res = subprocess.run([sys.executable, "-X", "utf8", str(CLI), "--help"],
                             capture_output=True, text=True, encoding="utf-8", cwd=str(ROOT))
        self.assertIn("--from-run", res.stdout)
        self.assertIn("--add-companies", res.stdout)

    def test_nothing_is_written_when_the_prior_run_is_missing(self):
        before = sorted(p.name for p in (ROOT / "scorecard" / "runs").iterdir())
        res = self.run_cli("ai-scorecard-2026-10-x", "--from-run", "ai-scorecard-없는실행")
        self.assertEqual(res.returncode, 1)
        self.assertEqual(sorted(p.name for p in (ROOT / "scorecard" / "runs").iterdir()), before)


if __name__ == "__main__":
    unittest.main()
