# 판단 근거 사슬(2026-10-07 사용자 지시 "URL 이 있어야 하지 않겠냐"): 올릴·내릴 근거 줄마다 원문 근거 표지와 그 근거의 URL·본문 발췌·위치를 잠근다
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard import engine, stages  # noqa: E402
from scorecard.schema import SchemaError  # noqa: E402
from scorecard.validate import citation_item_violations, citation_violations, cited_ids  # noqa: E402
from tests.test_collect_stage import SLUG  # noqa: E402
from tests.test_evidence_three_way import BODY, DOWN, UP, V19Base, render_both  # noqa: E402
from tests.test_proposals import ProposalBase  # noqa: E402


def revise(up: list[str], down: list[str] | None = None) -> dict:
    return stages.revise_judgment(SLUG, company_id="nvidia", factor="F5",
                                  changes={"evidence_up": up, "evidence_down": DOWN if down is None else down},
                                  reason="시험", by="사용자")


class CitedIdsTest(unittest.TestCase):
    def test_tail_marker_only(self):
        self.assertEqual(cited_ids("사실이다. [EV-nvidia-001]"), ["EV-nvidia-001"])
        self.assertEqual(cited_ids("사실이다. [EV-nvidia-001, EV-spacex-xai-012]"), ["EV-nvidia-001", "EV-spacex-xai-012"])
        self.assertEqual(cited_ids("사실이다(EV-nvidia-001)."), [], "괄호 안 언급은 표지가 아니다")
        self.assertEqual(cited_ids("[EV-nvidia-001] 사실이다."), [], "표지는 줄 끝에 둔다")


class WriteTimeTest(V19Base):
    def put(self, item: dict, *, confirm: bool = True) -> None:
        payload = json.loads(self.paths.evidence.read_text(encoding="utf-8"))
        payload["items"].append(item)
        self.paths.evidence.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        stages.register_evidence_sources(SLUG)
        if confirm:
            stages.confirm(SLUG, evidence_ids=[item["evidence_id"]], reviewer="사용자")

    def extra(self, eid: str, *, confirm: bool = True, **kw) -> None:
        self.put(self.evidence_item(eid, **kw), confirm=confirm)

    def test_marked_lines_citing_body_evidence_are_written(self):
        revise(UP)
        self.assertEqual(self.judgment()["evidence_up"], UP)

    def test_line_without_marker_is_refused(self):
        with self.assertRaisesRegex(SchemaError, r"올릴 근거\[0\]: 줄 끝에 근거 표지"):
            revise(["관측 지표가 좋아졌다(EV-nvidia-001)"])
        self.assertNotIn("evidence_up", self.judgment(), "거부된 수정은 파일을 바꾸지 않는다")

    def test_unknown_and_candidate_evidence_are_refused(self):
        with self.assertRaisesRegex(SchemaError, "EV-nvidia-009 — evidence.json 에 없는 근거"):
            revise(["사실이다. [EV-nvidia-009]"])
        self.extra("EV-nvidia-002", confirm=False)
        with self.assertRaisesRegex(SchemaError, "EV-nvidia-002 — 확정되지 않은 근거"):
            revise(["사실이다. [EV-nvidia-002]"])

    def test_title_only_excerpt_is_refused(self):
        self.extra("EV-nvidia-002", excerpt=self.cand["title"])
        with self.assertRaisesRegex(SchemaError, "excerpt 가 제목과 같다"):
            revise(["사실이다. [EV-nvidia-002]"])

    def test_missing_locator_is_refused(self):
        item = self.evidence_item("EV-nvidia-002")
        item.pop("locator")
        self.put(item)
        with self.assertRaisesRegex(SchemaError, "locator"):
            revise(["사실이다. [EV-nvidia-002]"])

    def test_every_id_in_a_marker_is_checked(self):
        self.extra("EV-nvidia-002", confirm=False)
        with self.assertRaisesRegex(SchemaError, "EV-nvidia-002 — 확정되지 않은"):
            revise(["사실이다. [EV-nvidia-001, EV-nvidia-002]"])

    def test_verdict_column_needs_no_marker(self):
        stages.revise_judgment(SLUG, company_id="nvidia", factor="F5",
                               changes={"evidence": ["결론은 비용형이다"], "evidence_up": UP, "evidence_down": []},
                               reason="시험", by="사용자")
        self.assertEqual(self.judgment()["evidence"], ["결론은 비용형이다"])


class V18Test(ProposalBase):
    def test_old_rule_runs_do_not_need_markers(self):
        stages.revise_judgment(SLUG, company_id="nvidia", factor="F5",
                               changes={"evidence_up": ["표지 없는 줄"], "evidence_down": []}, reason="시험", by="사용자")
        self.assertEqual(self.judgment()["evidence_up"], ["표지 없는 줄"])


class ValidatorTest(unittest.TestCase):
    EV = {"evidence_id": "EV-nvidia-001", "source_id": "S1", "status": "confirmed", "title": "제목", "excerpt": "본문 문장", "locator": "2문단"}

    def test_item_rules(self):
        ev = {"EV-nvidia-001": self.EV}
        ok = {"evidence_up": UP, "evidence_down": []}
        self.assertEqual(citation_item_violations(ok, ev, {"S1": "https://example.com/a"}), [])
        self.assertIn("URL 이 없다", citation_item_violations(ok, ev, {"S1": None})[0])
        self.assertIn("URL 이 없다", citation_item_violations(ok, ev, {"S1": "내부 문서"})[0])
        self.assertIn("제목과 같다", citation_item_violations(ok, {"EV-nvidia-001": {**self.EV, "excerpt": " 제목 "}},
                                                         {"S1": "https://example.com/a"})[0])

    def test_context_reports_every_judgment(self):
        ctx = SimpleNamespace(judgments=[{"judgment_id": "nvidia.F5", "evidence_up": UP, "evidence_down": ["표지 없음"]},
                                         {"judgment_id": "openai.F5", "evidence_up": ["표지 없음"], "evidence_down": []}],
                              evidence=[self.EV], sources={"items": [{"source_id": "S1", "url": "https://example.com/a"}]})
        bad = citation_violations(ctx)
        self.assertEqual(len(bad), 2)
        self.assertTrue(bad[0].startswith("nvidia.F5 내릴 근거[0]"))
        self.assertTrue(bad[1].startswith("openai.F5 올릴 근거[0]"))


class RenderTest(V19Base):
    def test_card_marker_and_cited_table_show_excerpt_and_locator(self):
        from scorecard import render_html
        revise(UP, [])
        draft, html = render_both(SLUG)
        card = html[html.index('id="card-nvidia"'):]
        self.assertIn('<span class="cite">[EV-nvidia-001]</span>', card[:card.index("</details>")])
        ctx = engine.load_context(SLUG)
        doc = render_html.link_cited_evidence(f"<html><body>{html}<!--CITED-EVIDENCE--></body></html>", ctx)
        self.assertIn('<a href="#ev-EV-nvidia-001">EV-nvidia-001</a>', doc)
        self.assertIn(f"“{BODY['excerpt']}”", doc)
        self.assertIn(f"위치: {BODY['locator']}", doc)
        self.assertIn("본문 발췌 · 위치", draft)
        self.assertIn(f"(위치: {BODY['locator']})", draft)


if __name__ == "__main__":
    unittest.main()
