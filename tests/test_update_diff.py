# diff 의 층 규칙 지원과 실적 반영 실행 모드(계획 U4) — 범위 안 변화는 허용하고 범위 밖이 움직이면 위반으로 잡는지 본다
from __future__ import annotations

import copy
import shutil
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard import engine, stages  # noqa: E402
from scorecard.compare import compare_runs  # noqa: E402
from scorecard.schema import SchemaError, load_json_strict, sha256_obj, write_json  # noqa: E402
from tests.test_collect_stage import Sandbox  # noqa: E402

V30FULL = "ai-scorecard-2026-10-v30full"
NEW = "ai-scorecard-2026-10-q3t"
AS_OF = "2026-10-22"
UPDATED = ["alphabet", "spacex-xai"]


def calculate(slug: str) -> None:
    engine.write_results(slug, engine.compute(engine.load_context(slug)))


class DiffBase(unittest.TestCase):
    def setUp(self) -> None:
        self.box = Sandbox(init=False)
        self.addCleanup(self.box.close)
        src = ROOT / "output" / V30FULL
        if not src.is_dir():
            self.skipTest(f"{V30FULL} 실행이 없다")
        shutil.copytree(src, engine.run_dir(V30FULL))

    def edit(self, slug: str, name: str, mutate) -> None:
        path = engine.run_dir(slug) / name
        payload = load_json_strict(path)
        mutate(payload["items"])
        write_json(path, payload)


class LayeredExtendRunTest(DiffBase):
    def test_layered_company_add_pair_is_compared(self):
        stages.init_run("ai-scorecard-2026-10-sub", from_run=V30FULL, companies=["alphabet", "tsmc"], as_of="2026-10-14", title="부분")
        calculate("ai-scorecard-2026-10-sub")
        stages.init_run("ai-scorecard-2026-10-ext", from_run="ai-scorecard-2026-10-sub", add_companies=["apple"], title="추가")
        calculate("ai-scorecard-2026-10-ext")
        out = compare_runs("ai-scorecard-2026-10-ext", "ai-scorecard-2026-10-sub")
        self.assertEqual((out["mode"], out["new_companies"]), ("extend", ["apple"]))
        self.assertTrue(out["ok"], out["inputs"]["violations"] + out["scores"]["violations"])
        self.assertEqual(out["scores"]["compared"], 2)
        # 기존 기업의 층 판단 하나를 고치면 1층이 잡는다.
        self.edit("ai-scorecard-2026-10-ext", "judgments.json",
                  lambda items: next(j for j in items if j["judgment_id"] == "alphabet.F2.cloud")["evidence"].append("고친 문장"))
        out = compare_runs("ai-scorecard-2026-10-ext", "ai-scorecard-2026-10-sub")
        self.assertFalse(out["ok"])
        self.assertTrue(any("judgments: 기존 항목 1건의 내용이 고쳐졌다 (alphabet.F2.cloud)" in v for v in out["inputs"]["violations"]))


class UpdateRunDiffTest(DiffBase):
    def setUp(self) -> None:
        super().setUp()
        stages.init_run(NEW, from_run=V30FULL, rule_version="v3.1", as_of=AS_OF, title="3분기 실적 반영",
                        update_companies=UPDATED, update_reason="Alphabet·SpaceX-xAI 3분기 실적")
        calculate(NEW)

    def test_untouched_update_run_passes(self):
        out = compare_runs(NEW, V30FULL)
        self.assertEqual((out["mode"], out["updated_companies"]), ("update", UPDATED))
        self.assertTrue(out["ok"], out["inputs"]["violations"] + out["scores"]["violations"])
        self.assertIn("실적 반영 실행이다", out["note"])

    def test_must_compare_with_the_run_it_continued(self):
        stages.init_run("ai-scorecard-2026-10-other", from_run=V30FULL, as_of="2026-10-14", title="다른")
        calculate("ai-scorecard-2026-10-other")
        with self.assertRaisesRegex(SchemaError, "이어받은 실행 ai-scorecard-2026-10-v30full 과 견준다"):
            compare_runs(NEW, "ai-scorecard-2026-10-other")

    def test_out_of_scope_judgment_edit_is_a_violation_until_declared(self):
        def touch(items):
            next(j for j in items if j["judgment_id"] == "tesla.F5")["evidence"].append("범위 밖에서 고친 문장")
        self.edit(NEW, "judgments.json", touch)
        out = compare_runs(NEW, V30FULL)
        self.assertFalse(out["ok"])
        self.assertTrue(any("(tesla.F5)" in v for v in out["inputs"]["violations"]))
        stages.declare_scope_extra(NEW, [("tesla", "F5")], reason="Alphabet ⑤ 의 새 잣대가 닿는다")
        out = compare_runs(NEW, V30FULL)
        self.assertTrue(out["ok"], out["inputs"]["violations"])
        self.assertIn("tesla.F5", out["inputs"]["by_file"]["judgments"]["allowed"])
        self.assertEqual([r["company_id"] for r in out["scope_items"]], ["tesla"])

    def test_updated_company_judgment_edit_is_allowed(self):
        self.edit(NEW, "judgments.json",
                  lambda items: next(j for j in items if j["judgment_id"] == "alphabet.F4")["evidence"].append("갱신 회사 문장"))
        out = compare_runs(NEW, V30FULL)
        self.assertTrue(out["ok"], out["inputs"]["violations"])
        self.assertIn("alphabet.F4", out["inputs"]["by_file"]["judgments"]["allowed"])

    def test_price_observations_are_allowed_for_everyone_but_other_metrics_are_not(self):
        def add(metric: str, oid: str):
            def go(items):
                base = copy.deepcopy(next(o for o in items if o["company_id"] == "tsmc" and o["metric"] == metric))
                base.update(observation_id=oid, as_of=AS_OF)
                if "observed_at" in base:
                    base["observed_at"] = AS_OF
                items.append(base)
            return go
        self.edit(NEW, "observations.json", add("price", "tsmc.price.q3t"))
        out = compare_runs(NEW, V30FULL)
        self.assertTrue(out["inputs"]["ok"], out["inputs"]["violations"])
        self.assertIn("tsmc.price.q3t", out["inputs"]["by_file"]["observations"]["allowed"])
        self.edit(NEW, "observations.json", add("revenue_ttm", "tsmc.revenue_ttm.q3t"))
        out = compare_runs(NEW, V30FULL)
        self.assertFalse(out["inputs"]["ok"])
        self.assertTrue(any("신규 기업이 아닌 곳에 1건이 더해졌다 (tsmc.revenue_ttm.q3t)" in v for v in out["inputs"]["violations"]))

    def test_sources_for_touched_companies_are_allowed(self):
        # 2026-10-23: 선언한 항목의 회사(tesla)에 새 보도 출처가 더해진다. 범위 밖 회사(oracle)의 출처는 위반이다.
        stages.declare_scope_extra(NEW, [("tesla", "F5")], reason="리뷰가 찾은 DMV 보도")
        def add(cid: str, sid: str):
            def go(items):
                items.append({"source_id": sid, "title": "t", "publisher": "p", "url": "https://example.com/" + cid,
                              "accessed_at": "2026-10-23T00:00:00Z", "sha256": "0" * 64, "conflict_of_interest": None,
                              "note": None, "kind": "news", "company_id": cid, "published_at_utc": "2026-10-20T00:00:00Z"})
            return go
        self.edit(NEW, "sources.json", add("tesla", "SRC-WEB-tesla-900"))
        out = compare_runs(NEW, V30FULL)
        self.assertTrue(out["inputs"]["ok"], out["inputs"]["violations"])
        self.assertIn("SRC-WEB-tesla-900", out["inputs"]["by_file"]["sources"]["allowed"])
        self.edit(NEW, "sources.json", add("oracle", "SRC-WEB-oracle-900"))
        out = compare_runs(NEW, V30FULL)
        self.assertFalse(out["inputs"]["ok"])
        self.assertTrue(any("(SRC-WEB-oracle-900)" in v for v in out["inputs"]["violations"]))

    def forge(self, mutate) -> None:
        """결과 파일의 점수를 바꾸고 자가 해시를 맞춘다(2층만 시험하려고)."""
        path = engine.results_path(NEW)
        payload = load_json_strict(path)
        mutate({c["company_id"]: c for c in payload["companies"]})
        payload["results_hash"] = sha256_obj({k: v for k, v in payload.items() if k != "results_hash"})
        write_json(path, payload)

    def test_scores_outside_scope_may_move_only_in_f6(self):
        def f6(cs):
            cs["tesla"]["factors"]["F6"]["score"] = (cs["tesla"]["factors"]["F6"]["score"] or 0) - 1
            cs["tesla"]["total"] = (cs["tesla"]["total"] or 0) - 1
        self.forge(f6)
        out = compare_runs(NEW, V30FULL)
        self.assertTrue(out["scores"]["ok"], out["scores"]["violations"])
        self.assertEqual([r["company_id"] for r in out["scores"]["allowed"]], ["tesla"])
        self.forge(lambda cs: cs["tesla"]["factors"]["F1"].update(score=(cs["tesla"]["factors"]["F1"]["score"] or 0) + 1))
        out = compare_runs(NEW, V30FULL)
        self.assertFalse(out["scores"]["ok"])
        self.assertTrue(out["scores"]["violations"][0].startswith("tesla: F1 score"))

    def test_updated_company_scores_may_move(self):
        self.forge(lambda cs: cs["alphabet"]["factors"]["F1"].update(score=(cs["alphabet"]["factors"]["F1"]["score"] or 0) + 1))
        out = compare_runs(NEW, V30FULL)
        self.assertTrue(out["scores"]["ok"], out["scores"]["violations"])
        self.assertEqual(out["scores"]["allowed"][0]["why"], "갱신 회사")


if __name__ == "__main__":
    unittest.main()
