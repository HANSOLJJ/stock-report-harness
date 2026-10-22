# 실적 반영 실행 선언(계획 U2) — init 의 --update-companies, run.json 의 갱신 회사·마지막 전체 갱신일·범위 선언, 실행 종류 판별을 잠근다
from __future__ import annotations

import copy
import shutil
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard import engine, stages  # noqa: E402
from scorecard.schema import SchemaError, load_json_strict, validate_run  # noqa: E402
from scorecard.validate import is_regular_run, is_update_run  # noqa: E402
from tests.test_collect_stage import Sandbox  # noqa: E402

V30FULL = "ai-scorecard-2026-10-v30full"
NEW = "ai-scorecard-2026-10-q3t"
AS_OF = "2026-10-22"
REASON = "Alphabet·SpaceX-xAI 3분기 실적"


class UpdateRunBase(unittest.TestCase):
    def setUp(self) -> None:
        self.box = Sandbox(init=False)
        self.addCleanup(self.box.close)
        src = ROOT / "output" / V30FULL
        if not src.is_dir():
            self.skipTest(f"{V30FULL} 실행이 없다")
        shutil.copytree(src, engine.run_dir(V30FULL))
        self.prior = load_json_strict(engine.run_dir(V30FULL) / "run.json")

    def init(self, slug: str = NEW, **kw):
        args = dict(from_run=V30FULL, rule_version="v3.1", as_of=AS_OF, title="3분기 실적 반영",
                    update_companies=["alphabet", "spacex-xai"], update_reason=REASON)
        args.update(kw)
        return stages.init_run(slug, **args)

    def run_json(self, slug: str = NEW) -> dict:
        return load_json_strict(engine.run_dir(slug) / "run.json")


class InitDeclaresUpdateRunTest(UpdateRunBase):
    def test_run_json_records_the_update(self):
        self.init()
        run = self.run_json()
        self.assertEqual(run["continued_from"]["updated_companies"], ["alphabet", "spacex-xai"])
        self.assertEqual(run["continued_from"]["added_companies"], [])
        self.assertEqual(run["companies"], self.prior["companies"])
        self.assertEqual(run["update_scope"], {"reason": REASON, "extra": []})
        self.assertEqual(run["change_type"], "earnings-update")
        # 가격은 모든 회사를 새로 받는다(D2). 이전 실행의 가격 기준일(2026-10-09)을 물려받지 않는다.
        self.assertEqual((run["price_as_of"], run["info_cutoff"]), (AS_OF, AS_OF))
        self.assertNotEqual(self.prior["price_as_of"], AS_OF)
        self.assertTrue(is_update_run(run))
        self.assertFalse(is_regular_run(run))
        self.assertTrue(any(a.startswith("실적 반영 실행이다. 갱신 회사는") for a in run["assumptions"]))
        engine.load_context(NEW)

    def test_refreshed_at_moves_only_updated_companies(self):
        self.init()
        ref = self.run_json()["refreshed_at"]
        self.assertEqual(set(ref), set(self.prior["companies"]))
        self.assertEqual({c for c, d in ref.items() if d == AS_OF}, {"alphabet", "spacex-xai"})
        # v30full 에는 기록이 없으므로 그 실행의 기준일에 전부 다시 매긴 것으로 본다.
        self.assertEqual({d for c, d in ref.items() if c not in ("alphabet", "spacex-xai")}, {self.prior["as_of"]})

    def test_second_update_run_chains_refreshed_at(self):
        self.init()
        stages.init_run("ai-scorecard-2026-10-q3t2", from_run=NEW, as_of="2026-10-30", title="Microsoft 실적 반영",
                        update_companies=["microsoft"], update_reason="Microsoft 1분기 실적")
        ref = self.run_json("ai-scorecard-2026-10-q3t2")["refreshed_at"]
        self.assertEqual((ref["alphabet"], ref["spacex-xai"], ref["microsoft"], ref["tsmc"]),
                         (AS_OF, AS_OF, "2026-10-30", self.prior["as_of"]))

    def test_regular_run_under_v31_refreshes_everyone(self):
        stages.init_run(NEW, from_run=V30FULL, rule_version="v3.1", as_of=AS_OF, title="정기")
        run = self.run_json()
        self.assertEqual(set(run["refreshed_at"].values()), {AS_OF})
        self.assertNotIn("update_scope", run)
        self.assertNotIn("updated_companies", run["continued_from"])
        self.assertTrue(is_regular_run(run))
        self.assertFalse(is_update_run(run))

    def test_v30_rule_writes_no_refreshed_at(self):
        stages.init_run(NEW, from_run=V30FULL, as_of=AS_OF, title="정기")
        self.assertNotIn("refreshed_at", self.run_json())

    def test_set_as_of_moves_updated_companies_only(self):
        self.init()
        out = stages.move_as_of(NEW, "2026-10-24", reason="Tesla 실적 뒤 가격")
        ref = self.run_json()["refreshed_at"]
        self.assertEqual({c for c, d in ref.items() if d == "2026-10-24"}, {"alphabet", "spacex-xai"})
        self.assertEqual(ref["tsmc"], self.prior["as_of"])
        self.assertEqual(out["moved"]["refreshed_at.alphabet"], [AS_OF, "2026-10-24"])


class InitRefusesTest(UpdateRunBase):
    def refuse(self, needle: str, **kw):
        with self.assertRaisesRegex(SchemaError, needle):
            self.init(**kw)
        self.assertFalse(engine.run_dir(NEW).exists(), "거부하면 실행 폴더를 만들지 않는다")

    def test_needs_reason(self):
        self.refuse("--update-reason 이 필요하다", update_reason="  ")

    def test_not_with_add_or_companies(self):
        self.refuse("--add-companies·--companies 와 함께 쓰지 않는다", add_companies=["apple"])
        self.refuse("--add-companies·--companies 와 함께 쓰지 않는다", companies=["alphabet"])

    def test_needs_update_policy_in_rules(self):
        self.refuse("규칙 v3.0 에는 실적 반영 실행 정책", rule_version="v3.0")

    def test_needs_later_as_of(self):
        self.refuse("이전 실행 기준일 2026-10-14 보다 뒤여야 한다", as_of="2026-10-14")

    def test_companies_must_be_in_prior_run(self):
        self.refuse("이전 실행 .* 의 기업이 아닌 것이 있다: \\['amd'\\]", update_companies=["amd"])

    def test_needs_from_run(self):
        with self.assertRaisesRegex(SchemaError, "--update-companies 는 --from-run 과 함께 쓴다"):
            stages.init_run(NEW, as_of=AS_OF, title="t", request="r", rule_version="v3.1",
                            update_companies=["alphabet"], update_reason=REASON)


class RunSchemaTest(UpdateRunBase):
    def setUp(self) -> None:
        super().setUp()
        self.init()
        self.base = self.run_json()

    def reject(self, mutate, needle: str):
        run = copy.deepcopy(self.base)
        mutate(run)
        with self.assertRaisesRegex(SchemaError, needle):
            validate_run(run, NEW)

    def test_accepts_written_run(self):
        validate_run(copy.deepcopy(self.base), NEW)

    def test_scope_and_updated_companies_go_together(self):
        self.reject(lambda r: r.pop("update_scope"), "함께 둔다")
        self.reject(lambda r: r["continued_from"].pop("updated_companies"), "함께 둔다")

    def test_not_mixed_with_added_companies(self):
        self.reject(lambda r: r["continued_from"].update(added_companies=["apple"]), "한 실행에 섞지 않는다")

    def test_updated_companies_shape(self):
        self.reject(lambda r: r["continued_from"].update(updated_companies=["alphabet", "alphabet"]), "중복 기업")
        self.reject(lambda r: r["continued_from"].update(updated_companies=["amd"]), "run.companies 에 없는 기업")

    def test_refreshed_at_covers_every_company_and_not_after_as_of(self):
        self.reject(lambda r: r["refreshed_at"].pop("tsmc"), "실행 대상 기업마다 날짜 하나")
        self.reject(lambda r: r["refreshed_at"].update(tsmc="2026-10-23"), "기준일 2026-10-22 뒤일 수 없다")

    def test_extra_items(self):
        ok = {"company_id": "anthropic", "factor": "F5", "reason": "같은 층 경쟁사에 같은 잣대", "declared_at": AS_OF}
        run = copy.deepcopy(self.base)
        run["update_scope"]["extra"] = [ok]
        validate_run(run, NEW)
        self.reject(lambda r: r["update_scope"]["extra"].extend([ok, ok]), "두 번 선언했다")
        self.reject(lambda r: r["update_scope"]["extra"].append({**ok, "reason": " "}), "이유가 필요하다")
        self.reject(lambda r: r["update_scope"]["extra"].append({**ok, "factor": "F10"}), "factor")
        self.reject(lambda r: r["update_scope"]["extra"].append({**ok, "company_id": "amd"}), "실행 대상이 아닌 기업")


if __name__ == "__main__":
    unittest.main()
