# 판단 근거 세 칸(판정·올릴 근거·내릴 근거, 2026-10-07 사용자 지시): 제안·수정·번복·검증기·CLI 와 옛 형식 공존을 잠근다
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard import engine, stages  # noqa: E402
from scorecard.schema import SchemaError, load_json_strict, validate_judgments  # noqa: E402
from scorecard.validate import (self_contained_violations, three_way_item_violations,  # noqa: E402
                                three_way_violations)
from tests.test_collect_stage import SLUG  # noqa: E402
from tests.test_proposals import ProposalBase  # noqa: E402
from tests.test_run_lock import human_env  # noqa: E402

UP = ["관측 지표가 좋아졌다(EV-nvidia-001)"]
DOWN = ["주요 고객이 자체 칩을 만든다"]


class V19Base(ProposalBase):
    RULE = "v1.9"

    def propose3(self, **kw) -> dict:
        kw.setdefault("evidence_after", ["적대 등급은 비용형이다(EV-nvidia-001)"])
        kw.setdefault("evidence_up_after", UP)
        kw.setdefault("evidence_down_after", DOWN)
        return self.propose(**kw)


class ProposalThreeWayTest(V19Base):
    def test_accept_writes_three_columns_and_history(self):
        stages.confirm(SLUG, evidence_ids=["EV-nvidia-001"], reviewer="사용자")
        p = self.propose3()
        self.assertEqual((p["evidence_up_after"], p["evidence_down_after"]), (UP, DOWN))
        self.assertNotIn("evidence_up", p["before"], "방향 칸이 없던 판단의 스냅숏은 옛 4키다")
        self.decide(accept=True, by="사용자")
        j = self.judgment()
        self.assertEqual((j["evidence_up"], j["evidence_down"]), (UP, DOWN))
        prev = j["revision_history"][-1]["previous"]
        self.assertNotIn("evidence_up", prev, "없던 칸은 이력에 남기지 않는다")
        after = load_json_strict(self.ppath)["items"][0]["applied"]["after"]
        self.assertEqual((after["evidence_up"], after["evidence_down"]), (UP, DOWN))

    def test_evidence_only_keeps_carried_status(self):
        before = self.judgment()
        self.propose3(changes={})
        self.decide(accept=True, by="사용자")
        j = self.judgment()
        for k in ("kind", "score", "inputs", "status", "reviewer", "reviewed_at"):
            self.assertEqual(j[k], before[k], k)
        self.assertEqual(j["evidence_down"], DOWN)

    def test_direction_only_proposal_and_empty_column(self):
        self.propose3(changes={})
        self.decide(accept=True, by="사용자")
        # 판정 칸은 그대로 두고 올릴 근거만 '없음'으로 비운다. 내릴 근거가 남아 있어 세 칸 조건이 선다
        p = self.propose(changes={}, evidence_up_after=[])
        self.assertIsNone(p["evidence_after"])
        self.assertEqual(p["before"]["evidence_up"], UP, "방향 칸이 생긴 뒤의 스냅숏에는 그 칸이 든다")
        self.decide("PRP-002", accept=True, by="사용자")
        j = self.judgment()
        self.assertEqual((j["evidence_up"], j["evidence_down"]), ([], DOWN))
        self.assertEqual(j["revision_history"][-1]["previous"]["evidence_up"], UP)

    def test_undo_restores_and_removes_columns(self):
        original = self.judgment()
        self.propose3(changes={})
        self.decide(accept=True, by="사용자")
        stages.undo_proposal(SLUG, "PRP-001", by="사용자")
        j = self.judgment()
        self.assertNotIn("evidence_up", j)
        self.assertNotIn("evidence_down", j)
        self.assertEqual(j["evidence"], original["evidence"])
        self.assertEqual(load_json_strict(self.ppath)["items"][0]["status"], "pending")

    def test_v19_refuses_writing_a_judgment_without_three_columns(self):
        with self.assertRaisesRegex(SchemaError, "세 칸 형식 위반"):
            stages.revise_judgment(SLUG, company_id="nvidia", factor="F5", changes={"evidence": ["판정만 있다"]},
                                   reason="시험", by="사용자")
        with self.assertRaisesRegex(SchemaError, "둘 다 비었다"):
            stages.revise_judgment(SLUG, company_id="nvidia", factor="F5",
                                   changes={"evidence_up": [], "evidence_down": []}, reason="시험", by="사용자")
        self.assertNotIn("evidence_up", self.judgment(), "거부된 수정은 파일을 바꾸지 않는다")

    def test_clearing_counter_evidence_moves_it_to_history(self):
        path = self.box.run_dir / "judgments.json"
        payload = load_json_strict(path)
        item = next(j for j in payload["items"] if j["company_id"] == "nvidia" and j["factor"] == "F5")
        item["counter_evidence"] = ["옛 감사 문면"]
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        with self.assertRaisesRegex(SchemaError, "비우는 것"):
            stages.revise_judgment(SLUG, company_id="nvidia", factor="F5", changes={"counter_evidence": ["새 문장"]},
                                   reason="시험", by="사용자")
        with self.assertRaisesRegex(SchemaError, "counter_evidence 는 비워"):
            stages.revise_judgment(SLUG, company_id="nvidia", factor="F5",
                                   changes={"evidence_up": UP, "evidence_down": DOWN}, reason="시험", by="사용자")
        stages.revise_judgment(SLUG, company_id="nvidia", factor="F5",
                               changes={"evidence_up": UP, "evidence_down": DOWN, "counter_evidence": []}, reason="시험", by="사용자")
        j = self.judgment()
        self.assertEqual(j["counter_evidence"], [])
        self.assertEqual(j["revision_history"][-1]["previous"]["counter_evidence"], ["옛 감사 문면"])
        self.assertEqual(j["status"], "carried", "근거 칸만 바꾼 수정이라 승계 상태가 그대로다")

    def test_summary_proposal_has_no_direction_columns(self):
        with self.assertRaisesRegex(SchemaError, "요약 문장 하나만"):
            stages.add_proposal(SLUG, company_id="nvidia", factor="SUMMARY", evidence_after=["요약"],
                                evidence_up_after=UP, reason="시험")

    def test_summary_json_carries_three_columns(self):
        self.propose3(changes={})
        self.decide(accept=True, by="사용자")
        s = stages.summary(SLUG)
        j = next(x for x in s["judgments"] if x["company_id"] == "nvidia" and x["factor"] == "F5")
        self.assertEqual((j["evidence_up"], j["evidence_down"], j["three_way"]), (UP, DOWN, True))
        other = next(x for x in s["judgments"] if x["company_id"] == "nvidia" and x["factor"] == "F1")
        self.assertEqual((other["evidence_up"], other["three_way"]), ([], False))
        p = s["proposals"][0]
        self.assertEqual((p["evidence_up_after"], p["evidence_down_after"]), (UP, DOWN))


def render_both(slug: str) -> tuple[str, str]:
    from scorecard import render_common as rc
    from scorecard import render_html
    stages.research(slug)
    stages.calculate(slug)
    draft = stages.draft(slug).read_text(encoding="utf-8")
    ctx = engine.load_context(slug)
    results = engine.load_results(slug)
    baseline, _obs, _trig = stages.load_baseline(ctx.run["baseline_id"])
    html = render_html.render_cards(results, baseline, ctx.companies, ctx.observations, ctx.judgments, rc.replacements(ctx), ctx)
    return draft, html


class RenderThreeWayTest(V19Base):
    def test_draft_and_card_show_three_columns(self):
        self.propose3(changes={}, evidence_down_after=[])
        self.decide(accept=True, by="사용자")
        draft, html = render_both(SLUG)
        section = draft[draft.index("NVIDIA"):]
        for text in ("  - 판정", "  - 올릴 근거", f"    - {UP[0]}", "  - 내릴 근거", "    - 없음"):
            self.assertIn(text, section)
        card = html[html.index('id="card-nvidia"'):]
        card = card[:card.index("</details>")]
        self.assertIn('<div class="fdir">', card)
        self.assertIn('<div class="fdh">올릴 근거</div>', card)
        self.assertIn('<p class="none">없음</p>', card)
        self.assertIn("판단 근거는 세 칸이다", draft)


class WorknoteTest(unittest.TestCase):
    def test_benchmark_name_is_not_a_task_code(self):
        from scorecard import render_common as rc
        body, note = rc.split_worknote("τ³-Banking·SciCode·AA-LCR 이 2~3포인트 퇴행했다.")
        self.assertIn("AA-LCR", body)
        self.assertEqual(note, "")
        body, note = rc.split_worknote("값을 고쳤다(A-GRADE-45).")
        self.assertNotIn("A-GRADE-45", body)
        self.assertIn("A-GRADE-45", note)


class RenderOldFormatTest(ProposalBase):
    def test_v18_has_no_direction_labels(self):
        draft, html = render_both(SLUG)
        self.assertNotIn('class="fdir"', html)
        self.assertNotIn("  - 올릴 근거", draft)
        self.assertNotIn("판단 근거는 세 칸이다", draft)


class CliThreeWayTest(V19Base):
    def test_propose_and_judge_with_up_down(self):
        with human_env(CLAUDECODE="1"):
            self.cli("propose", SLUG, "--company", "nvidia", "--factor", "F5", "--evidence", "판정 문장",
                     "--up", UP[0], "--down", DOWN[0], "--reason", "시험")
        p = load_json_strict(self.ppath)["items"][0]
        self.assertEqual((p["evidence_after"], p["evidence_up_after"], p["evidence_down_after"]), (["판정 문장"], UP, DOWN))
        with human_env():
            self.cli("proposal", SLUG, "--id", "PRP-001", "--accept", "--by", "사용자")
            out = self.cli("judge", SLUG, "--company", "nvidia", "--factor", "F5", "--up", "", "--reason", "올릴 근거 비움",
                           "--by", "사용자")
        self.assertIn("올릴 근거: 1문장 → 0문장", out)
        j = self.judgment()
        self.assertEqual((j["evidence_up"], j["evidence_down"]), ([], DOWN))

    def test_propose_json_keys(self):
        path = self.box.dir / "p.json"
        path.write_text(json.dumps({"changes": {}, "evidence_up_after": UP, "evidence_down_after": []}, ensure_ascii=False),
                        encoding="utf-8")
        self.cli("propose", SLUG, "--company", "nvidia", "--factor", "F5", "--json", str(path), "--reason", "시험")
        p = load_json_strict(self.ppath)["items"][0]
        self.assertEqual((p["evidence_up_after"], p["evidence_down_after"]), (UP, []))


class ValidatorTest(unittest.TestCase):
    def item(self, **kw) -> dict:
        base = {"judgment_id": "nvidia.F5", "evidence": ["판정"], "evidence_up": UP, "evidence_down": [], "counter_evidence": []}
        base.update(kw)
        return base

    def test_item_rules(self):
        self.assertEqual(three_way_item_violations(self.item()), [])
        self.assertTrue(three_way_item_violations({"judgment_id": "x", "evidence": ["판정"]}))
        self.assertTrue(three_way_item_violations(self.item(evidence_up=[])))
        self.assertTrue(three_way_item_violations(self.item(counter_evidence=["반대"])))
        missing_down = self.item()
        missing_down.pop("evidence_down")
        self.assertIn("evidence_down", three_way_item_violations(missing_down)[0])

    def test_context_report_and_banned_text_in_direction_columns(self):
        ctx = SimpleNamespace(judgments=[self.item(), self.item(judgment_id="openai.F5", evidence_up=[], evidence_down=[])],
                              company_summaries={}, evidence=[], triggers=[])
        self.assertEqual(len(three_way_violations(ctx)), 1)
        ctx.judgments[0]["evidence_down"] = ["기준선 원문은 다르다"]
        self.assertIn("nvidia.F5 내릴 근거[0]", " ".join(self_contained_violations(ctx)))


class SchemaCompatTest(unittest.TestCase):
    """옛 형식(방향 칸 없음, 7키 이력, 4키 스냅숏)이 그대로 통과하고 새 칸의 형식은 막는다."""

    def test_old_runs_still_load(self):
        for slug in ("ai-scorecard-2026-09-obsreg", "ai-scorecard-2026-10-test", "ai-scorecard-2026-10-rescore"):
            with self.subTest(slug=slug):
                engine.load_context(slug)
                stages._load_proposals(slug)

    def test_direction_column_shape(self):
        ctx = engine.load_context("ai-scorecard-2026-10-test")
        payload = load_json_strict(engine.run_dir("ai-scorecard-2026-10-test") / "judgments.json")
        payload["items"][0]["evidence_up"] = ["  "]
        with self.assertRaisesRegex(SchemaError, "evidence_up"):
            validate_judgments(payload, ctx.companies, ctx.rules.payload, "ai-scorecard-2026-10-test")
        payload["items"][0]["evidence_up"] = []
        validate_judgments(payload, ctx.companies, ctx.rules.payload, "ai-scorecard-2026-10-test")


if __name__ == "__main__":
    unittest.main()
