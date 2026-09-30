# HTML 표시 계층(자료 확보 현황·C-번호 사전·코드 링크) 회귀를 고정하는 렌더러 테스트
from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard.render_html import (  # noqa: E402
    GLOSSARY_SLOT,
    factor_calc_text,
    link_decision_codes,
    load_availability,
    render_availability,
    render_glossary,
)
from scorecard.rules import load_rules  # noqa: E402

RULES = load_rules("v1.5")
SLUG = "ai-scorecard-2026-09-baseline"


def obs(cid: str, metric: str, value: float, as_of: str, status: str = "legacy_unverified", method: str = "consensus_4q_sum") -> dict:
    return {
        "observation_id": f"{cid}.{metric}", "company_id": cid, "metric": metric, "value": value,
        "unit": "x", "as_of": as_of, "kind": "actual", "source_id": "SRC-T", "status": status,
        "basis": {"method": method}, "raw": str(value), "note": None,
    }


def avail_fixture(surveyed_at: str = "2026-09-08") -> dict:
    return {
        "schema": "scorecard/data-availability@1", "surveyed_at": surveyed_at, "scope": "상장사 F6",
        "required_quarters": 4, "companies_with_full_quarters": 0,
        "headline": "머리말", "score_effect": "점수 영향 없음", "not_re_surveyed": "다른 factor 는 범위 밖",
        "collection_note": "합친 기록",
        "materials": [{"item": "자료", "secured": "확보", "missing": "부족", "usable": "참고"}],
        "companies": [
            {"company_id": "old", "quarter_ends": ["2026-09", "2026-12"], "secured_quarters": 2, "missing": "나머지 2분기", "survey": "s1"},
            {"company_id": "new", "quarter_ends": ["2026-09", "2026-12"], "secured_quarters": 2, "missing": "나머지 2분기", "survey": "s1"},
        ],
        "surveys": {"s1": "조사 1"},
        "sources": [{"name": "Yahoo", "secured": "2분기", "limit": "나머지 없음"}],
        "cautions": ["주의"], "references": [{"label": "보고서", "path": "a/b.md"}],
    }


def results_fixture() -> dict:
    def c(cid: str, listed: bool = True) -> dict:
        return {"company_id": cid, "display_name": cid.upper(), "listed": listed, "pending": []}
    return {"companies": [c("old"), c("new"), c("private", listed=False)], "pending_rule_decisions": []}


class TestDecisionCodeLinks(unittest.TestCase):
    def test_links_text_codes_only(self) -> None:
        # 2026-09-18 FIX-79 S2: 결정 사전을 감사 기록으로 옮겨 본문은 번호를 잇지 않고 걷는다.
        doc = '<p>규칙 C-13 을 본다</p>'
        out = link_decision_codes(doc, {"C-13"}, GLOSSARY_SLOT)
        self.assertNotIn("C-13", out)
        self.assertNotIn('class="ccode"', out)

    def test_leaves_attributes_untouched(self) -> None:
        doc = '<p data-note="C-13">본문</p>'
        self.assertEqual(link_decision_codes(doc, {"C-13"}, GLOSSARY_SLOT), doc)

    def test_skips_script_and_style(self) -> None:
        doc = '<style>.x{content:"C-13"}</style><script>var a="C-13";</script>'
        self.assertEqual(link_decision_codes(doc, {"C-13"}, GLOSSARY_SLOT), doc)

    def test_does_not_link_path_prefix(self) -> None:
        doc = '<code>C-13/validation/report.md</code>'
        self.assertEqual(link_decision_codes(doc, {"C-13"}, GLOSSARY_SLOT), doc)

    def test_unknown_code_is_not_linked(self) -> None:
        doc = '<p>C-99 는 규칙에 없다</p>'
        self.assertEqual(link_decision_codes(doc, {"C-13"}, GLOSSARY_SLOT), doc)

    def test_glossary_slot_region_is_preserved(self) -> None:
        doc = f'<p>C-13</p>{GLOSSARY_SLOT}<p>C-13</p>'
        out = link_decision_codes(doc, {"C-13"}, GLOSSARY_SLOT)
        self.assertIn(GLOSSARY_SLOT, out)
        # 2026-09-18 FIX-79 S2: 자리표 양옆의 본문 번호는 걷히고, 자리표 자체는 그대로 남는다.
        self.assertEqual(out.count('class="ccode"'), 0)
        self.assertNotIn("<p>C-13</p>", out)


class TestGlossary(unittest.TestCase):
    def _ctx(self, decisions: list[dict] | None = None) -> SimpleNamespace:
        return SimpleNamespace(rules=RULES, run={"decisions": decisions or []}, observations=[])

    def test_one_entry_per_used_code(self) -> None:
        html = render_glossary(self._ctx(), {"companies": [], "pending_rule_decisions": []}, ["C-13", "C-17"])
        self.assertIn('id="dec-C-13"', html)
        self.assertIn('id="dec-C-17"', html)
        self.assertEqual(html.count('<details class="cdec"'), 2)

    def test_pending_decision_is_marked_undecided(self) -> None:
        results = {"companies": [{"display_name": "TSMC", "pending": [{"factor": "F6", "status": "needs_rule_decision", "decision_id": "C-13"}]}],
                   "pending_rule_decisions": ["C-13"]}
        html = render_glossary(self._ctx(), results, ["C-13"])
        self.assertIn("결정하지 않았다", html)
        self.assertIn("TSMC", html)
        self.assertIn("순위에서 제외", html)

    def test_applied_decision_reports_choice(self) -> None:
        ctx = self._ctx([{"id": "C-13", "choice": "accept_proxy_with_flag"}])
        html = render_glossary(ctx, {"companies": [], "pending_rule_decisions": []}, ["C-13"])
        self.assertIn("accept_proxy_with_flag", html)

    def test_unknown_code_yields_no_entry(self) -> None:
        self.assertEqual(render_glossary(self._ctx(), {"companies": [], "pending_rule_decisions": []}, ["C-99"]), "")


class TestAvailability(unittest.TestCase):
    def _ctx(self, observations: list[dict]) -> SimpleNamespace:
        return SimpleNamespace(observations=observations)

    def test_older_observation_is_reported_as_not_reflected(self) -> None:
        ctx = self._ctx([obs("old", "ntm_per", 25.3, "2026-09-02")])
        html = render_availability(avail_fixture(), ctx, results_fixture())
        self.assertIn("미반영", html)
        self.assertIn("2026-09-02", html)
        self.assertIn("반영된 기업 0개사", html)

    def test_observation_from_survey_day_counts_as_reflected(self) -> None:
        ctx = self._ctx([obs("old", "ntm_per", 25.3, "2026-09-02"), obs("new", "ntm_per", 30.0, "2026-09-08", status="verified")])
        html = render_availability(avail_fixture(), ctx, results_fixture())
        self.assertIn("반영된 기업 1개사", html)

    def test_company_outside_survey_is_listed_as_out_of_scope(self) -> None:
        html = render_availability(avail_fixture(), self._ctx([]), results_fixture())
        self.assertIn("PRIVATE", html)
        self.assertIn("이번 조사 범위 밖", html)

    def test_observation_status_is_shown_in_korean(self) -> None:
        ctx = self._ctx([obs("old", "ntm_per", 25.3, "2026-09-02")])
        html = render_availability(avail_fixture(), ctx, results_fixture())
        self.assertIn("사용자 원본 값·다시 확인 안 함", html)   # 2026-09-18 FIX-80 S4


class TestBuiltDocument(unittest.TestCase):
    """실제 실행의 산출 HTML 이 있으면 링크와 앵커가 짝을 이루는지 확인한다."""

    def setUp(self) -> None:
        self.html_path = ROOT / "output" / SLUG / "report.html"
        if not self.html_path.is_file():
            self.skipTest("빌드된 HTML 이 없다")
        self.html = self.html_path.read_text(encoding="utf-8")

    def test_every_code_link_has_an_anchor(self) -> None:
        linked = set(re.findall(r'class="ccode" href="#dec-(C-\d{2})"', self.html))
        self.assertTrue(linked)
        for code in sorted(linked):
            self.assertIn(f'id="dec-{code}"', self.html)

    def test_no_unlinked_code_left_in_body(self) -> None:
        """사전 앞의 본문에서는 규칙에 있는 C-번호가 모두 링크로 감싸져 있어야 한다."""
        body = self.html.split('<h3 id="c-glossary">')[0]
        stripped = re.sub(r'<a class="ccode" href="#dec-C-\d{2}">C-\d{2}</a>', "", body)
        leftover = {c for c in re.findall(r"C-\d{2}(?![\d\w/-])", stripped) if RULES.decision(c) is not None}
        self.assertEqual(leftover, set())

    def test_glossary_slot_is_consumed(self) -> None:
        self.assertNotIn(GLOSSARY_SLOT, self.html)

    def test_availability_section_is_present(self) -> None:
        self.assertIn('id="availability"', self.html)
        self.assertIn('id="availTable"', self.html)

    def test_availability_fixture_matches_run(self) -> None:
        avail = load_availability(SLUG)
        self.assertIsNotNone(avail)
        assert avail is not None
        self.assertEqual(avail["companies_with_full_quarters"], 0)
        self.assertTrue(all(c["secured_quarters"] < avail["required_quarters"] for c in avail["companies"]))


if __name__ == "__main__":
    unittest.main()


class TestF6CoverageRender(unittest.TestCase):
    """분기 확보 현황이 화면 문구로 나오는지 고정한다 (F6-IMPLEMENT-06)."""

    def test_partial_coverage_shows_counts_and_reason(self):
        fr = {"status": "pending_data", "score": None,
              "calc": {"coverage": {"secured": 2, "required": 4, "quarters": ["2026Q3", "2026Q4"], "sources": ["SRC-q"]}},
              "pending": {"kind": "data", "message": "나머지 2개 필요"}, "warnings": []}
        text = factor_calc_text("F6", fr)
        self.assertIn("2/4 확보", text)
        self.assertIn("2026Q3, 2026Q4", text)
        self.assertIn("원천 SRC-q", text)
        self.assertIn("나머지 2개 필요", text)
        self.assertNotIn("NTM PER", text)

    def test_full_coverage_shows_per_and_reapproval(self):
        fr = {"status": "ok", "score": -1,
              "calc": {"coverage": {"secured": 4, "required": 4, "quarters": ["2026Q3", "2026Q4", "2027Q1", "2027Q2"], "sources": ["SRC-q"]},
                       "ntm_per": 25.0, "band": "20~29", "boundary": {"flag": False}, "requires_reapproval": True},
              "pending": {}, "warnings": []}
        text = factor_calc_text("F6", fr)
        self.assertIn("4/4 확보", text)
        self.assertIn("NTM PER", text)
        self.assertIn("재승인 필요", text)

    def test_legacy_path_unchanged_without_coverage(self):
        fr = {"status": "ok", "score": -1,
              "calc": {"ntm_per": 25.3, "method": "vendor_forward_pe_verified_ntm", "band": "20~29", "boundary": {"flag": False}},
              "pending": {}, "warnings": []}
        text = factor_calc_text("F6", fr)
        self.assertIn("NTM PER", text)
        self.assertNotIn("확보", text)
