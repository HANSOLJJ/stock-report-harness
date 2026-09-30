# 규칙 v1.8 테스트(v1.7 대비 sources 제거·rule_version·note만 다름)
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard.engine import load_context, compute, load_results, recompute_matches  # noqa: E402
from scorecard.rules import load_rules  # noqa: E402
from scorecard.validate import check_source_allowlist  # noqa: E402

V17_SHA256 = "345c3353372d0f95d98eef5ed918c31e7a3f7878185a24f1e4edfa9870d58d21"
V18_NOTE_SUFFIX = " | v1.8: 원천 allowlist 폐지. 개인 사용 목적이라 host 등재 절차를 두지 않는다(사용자 결정 2026-09-30). 2026-09-30 구글 뉴스 robots·약관 검토 결과(robots 는 /rss 차단, 일반 약관은 robots 위반 자동 접근을 남용으로 정의, 뉴스 약관은 개인 피드 리더 용도 허용)를 알고 내린 결정이다. 수집기의 자제(식별 UA·낮은 빈도·본문 미수집)는 코드 상수로 지킨다. 프로즈 참조는 docs/scorecard/rules/AI기업_채점규칙_v1.7.md 를 계속 쓴다."


def rules(name: str) -> dict:
    return json.loads((ROOT / "scorecard" / "rules" / f"{name}.json").read_text(encoding="utf-8"))


class DiffTest(unittest.TestCase):
    def test_only_three_differences(self):
        v17, v18 = rules("v1.7"), rules("v1.8")
        self.assertEqual(set(v17) - set(v18), {"sources"})
        self.assertEqual(set(v18) - set(v17), set())
        for key in v18:
            if key in ("rule_version", "note"):
                continue
            self.assertEqual(v18[key], v17[key], f"v1.8.{key}가 v1.7과 다름")
        self.assertEqual(v18["rule_version"], "v1.8")
        self.assertEqual(v18["note"], v17["note"] + V18_NOTE_SUFFIX)

    def test_v17_untouched(self):
        import hashlib
        digest = hashlib.sha256(
            (ROOT / "scorecard" / "rules" / "v1.7.json").read_bytes()).hexdigest()
        self.assertEqual(digest, V17_SHA256)


class LoadTest(unittest.TestCase):
    def test_v18_loads_and_has_no_source_policy(self):
        ruleset = load_rules("v1.8")
        self.assertEqual(ruleset.version, "v1.8")
        self.assertFalse(ruleset.source_policy)

    def test_allowlist_check_not_called(self):
        class Result:
            def __init__(self) -> None:
                self.checks: list[str] = []
                self.errors: list[str] = []

            def check(self, name: str) -> None:
                self.checks.append(name)

            def error(self, msg: str) -> None:
                self.errors.append(msg)

        result = Result()
        called = check_source_allowlist(load_rules("v1.8"), {"items": []}, result)
        self.assertFalse(called)
        self.assertEqual(result.checks, [])


class RecomputeTest(unittest.TestCase):
    def test_obsreg_unchanged(self):
        # obsreg 실행은 v1.7 고정이라 v1.8 추가에 영향이 없어야 한다
        ok, stored, fresh = recompute_matches("ai-scorecard-2026-09-obsreg")
        self.assertTrue(ok, f"obsreg: {stored} != {fresh}")

    def test_baseline_totals_unchanged(self):
        # baseline 실행은 이 워크트리에서 results_hash가 이미 어긋나 있다(소유 밖,
        # F9 calc 경로 drift·총점은 동일). v1.8이 총점을 움직이지 않음을 본다.
        slug = "ai-scorecard-2026-09-baseline"
        ctx = load_context(slug)
        fresh = compute(ctx)
        stored = load_results(slug)
        self.assertEqual(
            {c["company_id"]: c["total"] for c in fresh["companies"]},
            {c["company_id"]: c["total"] for c in stored["companies"]})


if __name__ == "__main__":
    unittest.main()
