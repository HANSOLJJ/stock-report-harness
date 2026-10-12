# 실행별 표시 이름(run.json display_names, 2026-10-12 사용자 지시): 덮어쓰기·검증·키가 없는 실행의 불변을 잠근다
from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard import engine  # noqa: E402
from scorecard.schema import SchemaError, validate_run  # noqa: E402

RUN = json.loads((ROOT / "output" / "ai-scorecard-2026-10-rejudge" / "run.json").read_text(encoding="utf-8"))


class CompaniesForRunTest(unittest.TestCase):
    def test_override_changes_only_that_name(self):
        run = {**RUN, "display_names": {"spacex-xai": "SpaceX"}}
        got = engine.companies_for_run(run)
        base = engine.load_companies()
        self.assertEqual(got["spacex-xai"]["display_name"], "SpaceX")
        self.assertEqual({k: v for k, v in got["spacex-xai"].items() if k != "display_name"},
                         {k: v for k, v in base["spacex-xai"].items() if k != "display_name"})
        self.assertEqual(got["nvidia"], base["nvidia"])
        self.assertEqual(base["spacex-xai"]["display_name"], "SpaceX + xAI", "공유 목록은 바뀌지 않는다")

    def test_runs_without_the_key_are_unchanged(self):
        self.assertEqual(engine.companies_for_run(RUN), engine.load_companies())

    def test_unknown_company_is_refused(self):
        with self.assertRaisesRegex(SchemaError, "알 수 없는 기업"):
            engine.companies_for_run({**RUN, "display_names": {"no-such": "X"}})


class ValidateRunTest(unittest.TestCase):
    def test_shape_and_scope(self):
        ok = copy.deepcopy(RUN)
        ok["display_names"] = {"spacex-xai": "SpaceX"}
        self.assertIs(validate_run(ok), ok)
        for bad, pattern in (({"spacex-xai": ""}, "비어 있지 않은"), ({"spacex-xai": 3}, "비어 있지 않은"), (["SpaceX"], "비어 있지 않은"),
                             ({"no-such": "X"}, "실행 대상이 아닌")):
            run = copy.deepcopy(RUN)
            run["display_names"] = bad
            with self.subTest(bad=bad), self.assertRaisesRegex(SchemaError, pattern):
                validate_run(run)


if __name__ == "__main__":
    unittest.main()
