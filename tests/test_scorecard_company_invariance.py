# ADD-02 — 기업을 더해도 기존 기업의 **점수**가 움직이지 않음을 잠근다(subtree 해시가 아니라 점수 투영으로)
from __future__ import annotations

import copy
import dataclasses
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard import compare, engine  # noqa: E402
from scorecard.schema import load_json_strict, sha256_obj  # noqa: E402
from scorecard.stages import current_hashes  # noqa: E402

SLUG = "ai-scorecard-2026-09-obsreg"
PRIOR = "ai-scorecard-2026-09-baseline"
CLI = ROOT / "scripts" / "scorecard_cli.py"

# 15번째 기업. 디스크의 레지스트리에는 넣지 않는다 — `compute` 는 컨텍스트만 보므로 메모리에서 더하면 된다.
# 항목 형태는 `add-company` 가 만드는 것과 같다(ADD-01).
NEWCOMER = {
    "company_id": "samsung",
    "display_name": "Samsung Electronics",
    "aliases": ["삼성전자"],
    "type": "부품",
    "listed": True,
    "ticker": "005930",
    "exchange": "KRX",
    "share_basis": "common",
    "adr_ratio": None,
    "reporting_currency": "KRW",
    "scope": "반도체·디바이스 전반",
}


def projections(results: dict) -> dict[str, str]:
    return {c["company_id"]: compare.projection_hash(c) for c in results["companies"]}


def subtrees(results: dict) -> dict[str, str]:
    return {c["company_id"]: sha256_obj(c) for c in results["companies"]}


class ProjectionInvarianceTest(unittest.TestCase):
    """승인된 실행을 기준으로, **무엇을 바꾸면 점수가 움직이고 무엇을 바꾸면 안 움직이는지** 고정한다."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.ctx = engine.load_context(SLUG)
        cls.base = engine.compute(cls.ctx)

    def test_recompute_reproduces_the_approved_results(self):
        """기준선부터 세운다. 다시 계산한 결과가 승인된 `results.json` 과 같아야 나머지 비교가 뜻을 가진다."""
        self.assertEqual(self.base["results_hash"], engine.load_results(SLUG)["results_hash"])
        self.assertEqual(self.base["population"]["scored"], 14)

    def test_fifteenth_company_does_not_move_the_fourteen(self):
        """관측도 판단도 없는 기업을 더한다. 기존 14개사의 투영은 한 글자도 달라지지 않아야 한다."""
        companies = {**self.ctx.companies, NEWCOMER["company_id"]: dict(NEWCOMER)}
        run = copy.deepcopy(self.ctx.run)
        run["companies"] = [*run["companies"], NEWCOMER["company_id"]]
        after = engine.compute(dataclasses.replace(self.ctx, companies=companies, run=run))

        before_proj = projections(self.base)
        after_proj = projections(after)
        self.assertEqual({k: v for k, v in after_proj.items() if k != "samsung"}, before_proj)
        self.assertEqual(after["population"]["scored"], 14)          # 신규는 채점 인구에 들지 않는다
        self.assertIn("samsung", [x["company_id"] for x in after["population"]["incomplete"]])

        newcomer = next(c for c in after["companies"] if c["company_id"] == "samsung")
        self.assertFalse(newcomer["complete"])
        self.assertIsNone(newcomer["total"])
        self.assertTrue(all(f["score"] is None for f in newcomer["factors"].values()))

    def test_as_of_shift_keeps_the_projection_but_moves_the_subtree(self):
        """**이 과제의 핵심이다.** 기준일만 옮겨도 subtree 해시는 갈리지만 점수는 하나도 안 바뀐다.

        그래서 불변 판정에 subtree 해시를 쓰면 안 된다.
        """
        run = copy.deepcopy(self.ctx.run)
        run["as_of"] = "2026-12-02"                                   # 석 달 뒤로 옮긴다
        after = engine.compute(dataclasses.replace(self.ctx, run=run))

        self.assertEqual(projections(after), projections(self.base))  # 점수는 그대로
        moved = [cid for cid, h in subtrees(after).items() if h != subtrees(self.base)[cid]]
        self.assertEqual(len(moved), 12)                              # 상장 12개사의 subtree 는 갈린다
        for cid in moved:
            self.assertTrue(self.ctx.companies[cid]["listed"], cid)

        # 갈린 자리는 전부 F6 의 기준일 검사 기록이다. 날짜와 경과 개월이 계산 기록에 박히기 때문이다.
        for cid in moved:
            before = next(c for c in self.base["companies"] if c["company_id"] == cid)
            paths = compare._diff_paths(before, next(c for c in after["companies"] if c["company_id"] == cid))
            self.assertTrue(paths)
            self.assertTrue(all(p.startswith("factors.F6.calc.p4.stale_asof.") for p in paths), (cid, paths))
            self.assertIn("factors.F6.calc.p4.stale_asof.as_of", paths)

    def test_projection_does_not_read_rank(self):
        """신규 기업이 끼면 기존 기업의 `rank` 는 정당하게 밀린다. 투영이 그것을 보면 안 된다."""
        company = next(c for c in self.base["companies"] if c["company_id"] == "alphabet")
        self.assertIn("rank", company)
        self.assertNotIn("rank", compare.score_projection(company))
        demoted = {**company, "rank": company["rank"] + 5}
        self.assertEqual(compare.projection_hash(demoted), compare.projection_hash(company))

    def test_judgment_status_flip_changes_the_projection(self):
        """반대쪽도 잠근다. 판단의 `status` 를 건드리면 투영은 반드시 반응해야 한다.

        다만 **점수가 판단에서 나오는 factor 만** 반응한다. `F9` 는 `basis=computed` 라 점수가 관측에서
        나오고 판단은 게이트 입력(`kind=gate_inputs`)만 주므로, 그 판단의 승계 여부는 상태에 실리지 않는다.
        """
        judgments = copy.deepcopy(self.ctx.judgments)
        flipped = [j for j in judgments if j["status"] == "new"]
        self.assertTrue(flipped)
        for judgment in flipped:
            judgment["status"] = "carried"
        after = engine.compute(dataclasses.replace(self.ctx, judgments=judgments))

        moved = [cid for cid, h in projections(after).items() if h != projections(self.base)[cid]]
        scoring = {j["company_id"] for j in flipped if j["kind"] != "gate_inputs"}
        self.assertEqual(sorted(moved), sorted(scoring))
        for judgment in flipped:                                      # 안 움직인 쪽의 사유를 함께 잠근다
            if judgment["kind"] == "gate_inputs":
                company = next(c for c in after["companies"] if c["company_id"] == judgment["company_id"])
                self.assertEqual(company["factors"][judgment["factor"]]["basis"], "computed")
        # 점수는 그대로여도 상태가 `carried_score` 로 바뀐다 — 투영이 상태까지 담는 이유다.
        cid = moved[0]
        before = compare.score_projection(next(c for c in self.base["companies"] if c["company_id"] == cid))
        after_one = compare.score_projection(next(c for c in after["companies"] if c["company_id"] == cid))
        self.assertEqual(before["total"], after_one["total"])
        self.assertNotEqual(before["factors"], after_one["factors"])


class ApprovalHashTest(unittest.TestCase):
    """승인된 실행의 입력이 그대로인지 본다."""

    def test_prior_approval_matches_except_the_draft(self):
        """초안(`drafts/`)은 git 이 추적하지 않으므로 검사하지 않는다. 나머지 다섯은 승인 시점 그대로여야 한다."""
        approval = load_json_strict(engine.run_dir(SLUG) / "approval.json")
        current = current_hashes(SLUG)
        for key in ("rules", "observations", "judgments", "run", "results"):
            with self.subTest(key=key):
                self.assertEqual(approval["hashes"][key], current[key])
        self.assertEqual(current["results"], "4a3f6c05b206ef81f370ac7765a1a948fe1e9cf6d1999c142bac4f124e04910b")

        state = compare.approval_state(SLUG)
        self.assertEqual(state["approved_results_hash"], state["current_results_hash"])
        self.assertEqual([k for k in state["differing"] if k != "draft"], [])


class CompareRunsTest(unittest.TestCase):
    """실물 두 실행으로 3층 비교가 무엇을 실패로 보는지 고정한다."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.out = compare.compare_runs(SLUG, PRIOR)

    def test_failure_comes_only_from_layers_one_and_two(self):
        self.assertEqual(self.out["ok"], self.out["inputs"]["ok"] and self.out["scores"]["ok"])

    def test_the_two_runs_are_a_re_survey_not_an_addition(self):
        """이 두 실행은 기업을 더한 사이가 아니라 같은 기업을 다시 조사한 사이다. 그 사실을 출력이 말해야 한다."""
        self.assertEqual(self.out["new_companies"], [])
        self.assertIn("기업 추가", self.out["note"])
        self.assertFalse(self.out["ok"])
        self.assertEqual(self.out["scores"]["compared"], 14)
        self.assertEqual(self.out["scores"]["dropped"], [])
        changed = {c["company_id"] for c in self.out["scores"]["changed"]}
        self.assertIn("alphabet", changed)                            # F6 재조사로 함정 점수가 움직였다

    def test_subtree_difference_is_reported_but_never_fails(self):
        sub = self.out["subtrees"]
        self.assertEqual(len(sub["differing"]), 14)
        self.assertIn("실패 조건이 아니다", sub["note"])
        self.assertIn("as_of", sub["note"])
        for row in sub["detail"]:
            self.assertGreater(row["path_count"], 0)

    def test_inputs_layer_splits_removal_from_edit(self):
        """사라진 것과 내용이 고쳐진 것은 사유가 다르므로 따로 센다."""
        obs = self.out["inputs"]["by_file"]["observations"]
        self.assertEqual(obs["removed"], [])                          # 지워진 관측은 없다
        self.assertEqual(len(obs["edited"]), 98)                      # 기준선 관측 98건이 실측으로 교체됐다
        self.assertTrue(all(i.endswith(".v15") for i in obs["edited"]))
        self.assertEqual(obs["added_for_new_companies"], [])

    def test_sources_have_no_company_attribution(self):
        """`sources.json` 항목에는 `company_id` 가 없다. 그래서 더해진 출처는 귀속을 따지지 않는다."""
        src = self.out["inputs"]["by_file"]["sources"]
        self.assertEqual(src["added_for_new_companies"], [])
        self.assertEqual(src["added_for_existing_companies"], [])
        self.assertEqual(len(src["added_without_company"]), len(src["added"]))

    def test_same_slug_is_refused(self):
        with self.assertRaises(Exception):
            compare.compare_runs(SLUG, SLUG)


class PeriodGapTest(unittest.TestCase):
    """기준일 판정은 **권고**다. 종료 코드를 바꾸지 않는다."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.gap = compare.period_gap(SLUG, PRIOR)

    def test_verdict_when_no_company_was_added(self):
        self.assertEqual(self.gap["new_companies"], [])
        self.assertEqual(self.gap["verdict"], "해당 없음")
        self.assertEqual(self.gap["ahead"], [])

    def test_period_ends_come_from_revenue_observations(self):
        self.assertEqual(self.gap["quarters"]["nvidia"], "2026Q3")
        self.assertEqual(self.gap["quarters"]["tsmc"], "2025Q4")      # 연간 결산이라 한 해 뒤처져 보인다
        self.assertEqual(self.gap["existing"]["alphabet"], "2026-06-30")

    def test_companies_without_a_period_are_the_unlisted_ones(self):
        """기간이 없는 것이 결함이 아닌 경우를 갈라 둔다. 비상장사는 분기 실적을 내지 않는다."""
        self.assertEqual(sorted(self.gap["missing_period"]), ["anthropic", "openai"])
        self.assertEqual(sorted(self.gap["missing_unlisted"]), ["anthropic", "openai"])

    def test_gap_is_not_part_of_the_pass_fail_decision(self):
        self.assertNotIn("period_gap", compare.compare_runs(SLUG, PRIOR))


class DiffCliTest(unittest.TestCase):
    def run_cli(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, "-X", "utf8", str(CLI), "diff", *args],
                              capture_output=True, text=True, encoding="utf-8", cwd=str(ROOT))

    def test_human_output_reports_each_layer(self):
        res = self.run_cli(SLUG, "--against", PRIOR)
        self.assertEqual(res.returncode, 1, res.stderr)
        for marker in ("[1층]", "[2층]", "[3층]", "[참고]", "[기준일]", "판정:"):
            self.assertIn(marker, res.stdout)
        self.assertIn("실패 조건이 아니다", res.stdout)                 # subtree 경고문이 그대로 실린다
        self.assertIn("1층·2층 위반", res.stdout)                      # 실패 사유는 두 층에서만 온다

    def test_json_output_carries_the_gap_and_the_same_verdict(self):
        res = self.run_cli(SLUG, "--against", PRIOR, "--json")
        self.assertEqual(res.returncode, 1, res.stderr)
        payload = json.loads(res.stdout)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["period_gap"]["verdict"], "해당 없음")
        self.assertEqual(payload["prior_approval"]["differing"], [])

    def test_unknown_run_is_refused_without_a_traceback(self):
        res = self.run_cli(SLUG, "--against", "ai-scorecard-없는실행")
        self.assertEqual(res.returncode, 1)
        self.assertIn("[FAIL]", res.stderr)
        self.assertNotIn("Traceback", res.stderr)


if __name__ == "__main__":
    unittest.main()
