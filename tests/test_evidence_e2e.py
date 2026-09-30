# init(v1.8) → collect(뉴스·가격 픽스처, SEC_UA 없는 공시) → 근거 선별 → research → calculate → draft → review-template 종단 흐름을 CLI 로 잠근다
from __future__ import annotations

import io
import sys
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import scorecard_cli  # noqa: E402
from report_contract_lib import frontmatter_value, read_markdown  # noqa: E402
from scorecard import engine, evidence_lib  # noqa: E402
from scorecard.paths import run_paths  # noqa: E402
from scorecard.schema import load_json_strict, sha256_file, write_json  # noqa: E402
from scorecard.stages import current_hashes  # noqa: E402
from tests.test_collect_stage import QUOTES, RSS, SLUG, Sandbox  # noqa: E402


class EvidenceE2ETest(unittest.TestCase):
    def setUp(self) -> None:
        self.box = Sandbox(("nvidia", "openai"), init=False)
        self.addCleanup(self.box.close)
        self.paths = run_paths(SLUG)

    def cli(self, *argv: str, code: int = 0) -> str:
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            got = scorecard_cli.main([str(a) for a in argv])
        self.assertEqual(got, code, f"{argv}\n{out.getvalue()}\n{err.getvalue()}")
        return out.getvalue() + err.getvalue()

    def _init_and_collect(self) -> dict:
        self.cli("init", SLUG, "--as-of", "2026-09-29", "--title", "근거 종단", "--request", "근거 종단",
                 "--companies", "nvidia,openai", "--rule", "v1.8")
        self.cli("collect", SLUG, "--kind", "news", "--from-file", RSS)
        prices = self.cli("collect", SLUG, "--kind", "prices", "--from-file", QUOTES)
        self.assertIn("openai       skipped_unlisted", prices)
        filings = self.cli("collect", SLUG, "--kind", "filings")
        self.assertIn("nvidia       skipped_no_user_agent", filings)
        cands = [c for c in load_json_strict(self.paths.candidates)["items"] if c["company_id"] == "nvidia"]
        self.assertTrue(cands)
        return cands[0]

    def _write_evidence(self, cand: dict, **kw) -> None:
        item = {"evidence_id": "EV-nvidia-001", "company_id": "nvidia", "factors": ["F1"], "kind": "news",
                "source_id": cand["source_id"], "published_at_utc": cand["published_at_utc"], "title": cand["title"],
                "excerpt": cand["title"], "relevance": "개발자 생태계 확장 신호", "channel": "secondary",
                "conditional_impact": "플랫폼이 채택되면 사용자 접점이 넓어진다", "horizon": "2027H1",
                "counter_evidence": [], "unverified": ["기사 본문 미확인"], "change_vs_previous": "new", "status": "candidate"}
        item.update(kw)
        write_json(self.paths.evidence, {"schema": "scorecard.evidence/1", "run_id": SLUG, "items": [item]})

    def _write_triggers(self, cand: dict) -> None:
        write_json(self.paths.triggers, {"schema": "scorecard.triggers/2", "run_id": SLUG, "items": [
            {"trigger_id": "TRG-001", "company_id": "nvidia", "factors": ["F1"], "observation": "소프트웨어 플랫폼 발표",
             "condition": "엔터프라이즈 채택 공시", "deadline": "2027-06-30", "evidence_ids": ["EV-nvidia-001"],
             "source_ids": [cand["source_id"]], "status": "watching",
             "recheck": {"factors": ["F1"], "what": "업무 채널 형성 여부"}}]})

    def _cite_in_new_judgment(self) -> None:
        path = self.box.run_dir / "judgments.json"
        payload = load_json_strict(path)
        for j in payload["items"]:
            if j["judgment_id"] == "nvidia.F1":
                j.update(status="new", evidence_ids=["EV-nvidia-001"], reviewer="user", reviewed_at="2026-09-30")
                j.pop("carried_from", None)
        write_json(path, payload)

    def test_full_flow(self):
        cand = self._init_and_collect()
        self._write_evidence(cand)
        self._write_triggers(cand)
        self.cli("research", SLUG)

        # research 가 인용된 후보의 출처를 등록했다(추가만).
        sources = {s["source_id"]: s for s in load_json_strict(self.box.run_dir / "sources.json")["items"]}
        registered = sources[cand["source_id"]]
        self.assertEqual((registered["kind"], registered["company_id"]), ("news", "nvidia"))
        raw = evidence_lib.DATA_ROOT / cand["raw_ref"].split("/", 1)[1]
        self.assertEqual(registered["sha256"], sha256_file(raw))
        self.assertIn("SRC-YF-2026-09-29", sources)

        fm, body, _raw, _text = read_markdown(self.paths.research)
        self.assertEqual(frontmatter_value(fm, "evidence_hash"), sha256_file(self.paths.evidence))
        self.assertEqual(frontmatter_value(fm, "triggers_hash"), sha256_file(self.paths.triggers))
        for text in ("## 근거 자료", "EV-nvidia-001", "(추론) 개발자 생태계 확장 신호", "## 트리거(활성)", "TRG-001"):
            self.assertIn(text, body)

        # candidate 근거를 인용한 새 판단은 거부된다.
        self._cite_in_new_judgment()
        self.assertIn("확정되지 않은 근거", self.cli("calculate", SLUG, code=1))
        # confirmed 로 올리면 통과한다.
        self._write_evidence(cand, status="confirmed", reviewer="user", reviewed_at="2026-09-30")
        self.cli("research", SLUG)
        self.cli("calculate", SLUG)
        self.cli("draft", SLUG)
        self.cli("review-template", SLUG)

        results = engine.load_results(SLUG)
        self.assertEqual(results["input_hashes"]["evidence"], sha256_file(self.paths.evidence))
        self.assertEqual(results["input_hashes"]["triggers"], sha256_file(self.paths.triggers))
        nvidia = next(c for c in results["companies"] if c["company_id"] == "nvidia")
        self.assertEqual(nvidia["factors"]["F1"]["status"], "ok")
        self.assertTrue(self.paths.review.is_file())

        # 근거를 고치면 current_hashes 가 바뀐다(나머지는 그대로).
        before = current_hashes(SLUG)
        self.assertIn("evidence", before)
        self._write_evidence(cand, status="confirmed", reviewer="user", reviewed_at="2026-09-30", horizon="2027H2")
        after = current_hashes(SLUG)
        self.assertEqual(sorted(k for k in before if before[k] != after.get(k)), ["evidence"])
        # research 도 낡은 것으로 잡힌다.
        from validate_report_contract import ValidationResult
        from scorecard.validate import validate_scorecard

        errors = validate_scorecard(SLUG, result=ValidationResult(slug=SLUG)).errors
        self.assertTrue(any("evidence_hash" in e for e in errors), errors)

    def test_no_register_leaves_sources_alone(self):
        cand = self._init_and_collect()
        self._write_evidence(cand)
        before = (self.box.run_dir / "sources.json").read_bytes()
        out = self.cli("research", SLUG, "--no-register", code=1)
        self.assertIn("sources.json 에 없음", out)
        self.assertEqual((self.box.run_dir / "sources.json").read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
