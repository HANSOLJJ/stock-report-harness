# 이전 트리거 처리 강제(carry)·기한 초과 검사·발동 트리거 재검토 표를 잠그는 테스트
from __future__ import annotations

import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard import engine, stages  # noqa: E402
from scorecard.paths import run_paths  # noqa: E402
from scorecard.schema import SchemaError, load_json_strict, write_json  # noqa: E402
from tests.test_approval_commands import SLUG, FlowBase  # noqa: E402


class TriggerCarryTest(FlowBase):
    def load(self) -> dict:
        return load_json_strict(run_paths(SLUG).triggers)

    def save(self, payload: dict) -> None:
        write_json(run_paths(SLUG).triggers, payload)

    def test_previous_set_is_the_baseline_39(self):
        refs = [p["ref"] for p in stages.previous_triggers(load_json_strict(engine.run_dir(SLUG) / "run.json"))]
        self.assertEqual((len(refs), refs[0], refs[-1]), (39, "baseline/v1.5:TRIG-001", "baseline/v1.5:TRIG-039"))

    def test_fully_covered_run_passes(self):
        stages.research(SLUG)
        text = run_paths(SLUG).research.read_text(encoding="utf-8")
        self.assertIn("## 이전 트리거 처리", text)
        self.assertIn("| baseline/v1.5:TRIG-011 | 🆕 Oracle Q1 FY27 실적 (9/10) | 철회 | 시험 실행이라 철회로 처리 |", text)

    def test_missing_carry_stops_research(self):
        payload = self.load()
        payload["items"] = [t for t in payload["items"] if t.get("carry", {}).get("ref") != "baseline/v1.5:TRIG-011"]
        self.save(payload)
        with self.assertRaisesRegex(SchemaError, r"이전 트리거 1건.*baseline/v1\.5:TRIG-011 🆕 Oracle Q1 FY27"):
            stages.research(SLUG)

    def test_copied_record_with_old_check_date_does_not_count(self):
        payload = self.load()
        for t in payload["items"]:
            if t.get("carry", {}).get("ref") == "baseline/v1.5:TRIG-005":
                t["carry"]["checked_at"] = "2026-01-01"
        self.save(payload)
        with self.assertRaisesRegex(SchemaError, r"이전 트리거 1건.*TRIG-005"):
            stages.research(SLUG)

    def test_one_previous_trigger_may_split_by_company(self):
        payload = self.load()
        first = next(t for t in payload["items"] if t.get("carry", {}).get("ref") == "baseline/v1.5:TRIG-037")
        payload["items"].append({**first, "trigger_id": f"TRG-{len(payload['items']) + 1:03d}", "company_id": "openai",
                                 "carry": {**first["carry"], "finding": "OpenAI 몫 확인"}})
        self.save(payload)
        stages.research(SLUG)
        rows = [line for line in run_paths(SLUG).research.read_text(encoding="utf-8").splitlines()
                if line.startswith("| baseline/v1.5:TRIG-037 |")]
        self.assertEqual(len(rows), 2)

    def test_overdue_watching_trigger_stops_research(self):
        payload = self.load()
        payload["items"][0]["deadline"] = "2026-01-31"
        self.save(payload)
        with self.assertRaisesRegex(SchemaError, r"기한이 지났는데 계속 관찰\(watching\)인 트리거 1건: TRG-001\(기한 2026-01-31\)"):
            stages.research(SLUG)
        payload["items"][0]["status"] = "expired"
        self.save(payload)
        stages.research(SLUG)

    def test_fired_trigger_lists_recheck_targets(self):
        payload = self.load()
        payload["items"][0]["status"] = "fired"
        self.save(payload)
        stages.research(SLUG)
        text = run_paths(SLUG).research.read_text(encoding="utf-8")
        self.assertIn("### 발동 트리거 재검토 대상", text)
        row = next(line for line in text.splitlines() if line.startswith("| TRG-001 |") and "다시 볼 것" not in line
                   and "업무 채널 형성 여부 |" in line and "수정" in line)
        self.assertIn("수정하지 않음", row)

    def test_fired_needs_evidence_or_source(self):
        payload = self.load()
        payload["items"][0].update(status="fired", evidence_ids=[], source_ids=[])
        self.save(payload)
        with self.assertRaisesRegex(SchemaError, r"발동\(fired\) 트리거는 .*evidence_ids 나 source_ids"):
            engine.load_context(SLUG)

    def test_carry_ref_format(self):
        payload = self.load()
        payload["items"][-1]["carry"]["ref"] = "TRIG-001"
        self.save(payload)
        with self.assertRaisesRegex(SchemaError, r"carry\.ref 는"):
            engine.load_context(SLUG)


class ChainTest(FlowBase):
    """2026-10-02 이어받은 실행이 처리하지 않은 더 이전 트리거는 다음 실행에도 남는다."""

    NEW = "ai-scorecard-2026-11-chain"

    def test_unhandled_baseline_triggers_survive_one_more_run(self):
        payload = load_json_strict(run_paths(SLUG).triggers)
        payload["items"] = [t for t in payload["items"] if "carry" not in t]   # 이 장치 전의 10월 시험 실행처럼
        write_json(run_paths(SLUG).triggers, payload)
        stages.init_run(self.NEW, from_run=SLUG, title="이어받기")
        refs = [p["ref"] for p in stages.previous_triggers(load_json_strict(engine.run_dir(self.NEW) / "run.json"))]
        self.assertEqual(refs[0], f"{SLUG}:TRG-001")
        self.assertEqual((len(refs), refs[1], refs[-1]), (40, "baseline/v1.5:TRIG-001", "baseline/v1.5:TRIG-039"))

    def test_handled_ones_do_not_come_back(self):
        stages.init_run(self.NEW, from_run=SLUG, title="이어받기")
        refs = [p["ref"] for p in stages.previous_triggers(load_json_strict(engine.run_dir(self.NEW) / "run.json"))]
        self.assertEqual(refs, [f"{SLUG}:TRG-001"])


class AppliesTest(unittest.TestCase):
    def test_only_rule_v18_and_up_with_triggers_file(self):
        ctx = lambda version, triggers: SimpleNamespace(rules=SimpleNamespace(version=version), triggers=triggers)  # noqa: E731
        self.assertFalse(stages.trigger_carry_applies(ctx("v1.7", [])))
        self.assertFalse(stages.trigger_carry_applies(ctx("v1.8", None)))
        self.assertTrue(stages.trigger_carry_applies(ctx("v1.8", [])))
        self.assertTrue(stages.trigger_carry_applies(ctx("v1.10", [])))


if __name__ == "__main__":
    unittest.main()
