# FIX-54 1단계 S3·S4 — HTML 과 초안이 같은 표시 규칙(render_common)을 쓰는지 메모리 렌더로 고정한다(빌드하지 않는다)
from __future__ import annotations

import html as html_lib
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard import render_common as rc  # noqa: E402
from scorecard.engine import load_context  # noqa: E402
from scorecard.render_html import load_availability, render_document  # noqa: E402
from scorecard.render_md import render_draft  # noqa: E402
from scorecard.stages import load_baseline  # noqa: E402

SLUG = "ai-scorecard-2026-09-obsreg"
RUN_DIR = ROOT / "scorecard" / "runs" / SLUG


def plain(fragment: str) -> str:
    """HTML 조각에서 태그를 걷고 엔티티를 풀어 초안 문장과 비교할 수 있게 한다."""
    return html_lib.unescape(re.sub(r"<[^>]+>", "", fragment))


class SharedRenderTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.ctx = load_context(SLUG)
        cls.results = json.loads((RUN_DIR / "results.json").read_text(encoding="utf-8"))
        cls.baseline, _obs, cls.triggers = load_baseline(cls.ctx.run["baseline_id"])
        cls.md = render_draft(cls.ctx, cls.results, cls.baseline, cls.triggers)
        cls.html = render_document(cls.ctx, cls.results, cls.baseline, cls.triggers, {"review_type": "mem", "reviewers": []},
                                   {"approval_id": "00000000-memory", "approved_by": "mem", "approved_at": "2026-09-15"},
                                   load_availability(SLUG))
        cls.html_text = plain(cls.html)

    def card(self, cid: str) -> str:
        i = self.html.index(f'id="card-{cid}"')
        return self.html[i:self.html.index("</details>", i)]

    def frow(self, cid: str, label: str) -> str:
        card = self.card(cid)
        i = card.index(f'<span class="flab">{label}</span>')
        j = card.find('<div class="frow">', i)
        return card[i:j if j != -1 else len(card)]

    # ---------------------------------------------------------------- S3 카드
    def test_html_card_uses_active_judgment_and_strikes_superseded(self):
        row = self.frow("tsmc", "⑤ 아군")
        self.assertIn("<code>tsmc.F5.strict54</code>", row)
        self.assertIn("대체된 판단 <code>tsmc.F5</code>", row)
        self.assertIn("<del>", row)
        self.assertNotIn("아래는 기준선 근거", self.html)

    def test_html_card_evidence_matches_draft_for_every_factor(self):
        """두 렌더러가 같은 근거 블록을 쓰는지 — 초안의 헤더가 HTML 카드에도 글자 그대로 있어야 한다."""
        judgments_by_id = {j["judgment_id"]: j for j in self.ctx.judgments}
        base = {b["company_id"]: b for b in self.baseline["companies"]}
        reps = rc.replacements(self.ctx)
        n = 0
        for c in self.results["companies"]:
            for f, fr in c["factors"].items():
                block = rc.evidence_block(fr, judgments_by_id, base.get(c["company_id"], {}).get("evidence", {}).get(f, []),
                                          self.ctx.run["baseline_id"], c["company_id"], reps)
                if block is None:
                    continue
                n += 1
                with self.subTest(cid=c["company_id"], f=f):
                    self.assertIn(f"- **{rc.FACTOR_LABELS[f]}** {block['header']}:", self.md)
                    # HTML 은 본문의 C-번호를 사전 링크로 바꾸므로 태그를 걷은 글자로 비교한다.
                    row = plain(self.frow(c["company_id"], rc.FACTOR_LABELS[f]))
                    self.assertIn(plain(rc.inline_html(block["header"])), row)
                    self.assertIn(plain(rc.inline_html(block["lines"][-1][1])), row)
        self.assertEqual(n, 126)

    def test_notice_817_no_longer_calls_everything_past_record(self):
        self.assertNotIn("원문을 그대로 옮긴 과거 기록이며", self.html)
        self.assertIn(rc.inline_html(rc.card_evidence_note("v1.5")), self.html)

    # ---------------------------------------------------------------- S4 judgment_id 로 찾기
    def test_auto_f6_does_not_borrow_carried_judgment_header(self):
        for cid in ("anthropic", "openai"):
            with self.subTest(cid=cid):
                self.assertNotIn(f"`{cid}.F6`", self.md)
                self.assertNotIn(f"<code>{cid}.F6</code>", self.html)
                self.assertIn("기준선 v1.5 서술(참고 — 이번 실행은 입력에서 자동 산출", self.frow(cid, "⑥ 가격"))

    # ---------------------------------------------------------------- S3 산식·경계
    def test_f6_parameters_text_is_not_empty(self):
        for c in self.results["companies"]:
            with self.subTest(cid=c["company_id"]):
                text = rc.factor_calc_text("F6", c["factors"]["F6"])
                self.assertTrue(text)
                self.assertIn(text, self.md)
                self.assertIn(html_lib.escape(text), self.frow(c["company_id"], "⑥ 가격"))
        tsmc = rc.factor_calc_text("F6", {c["company_id"]: c for c in self.results["companies"]}["tsmc"]["factors"]["F6"])
        self.assertIn("P1 PER", tsmc)
        self.assertIn("P4 -1(period_basis_not_ttm)", tsmc)

    def test_boundary_column_reads_parameters(self):
        calc = {"mode": "parameters", "parameters": {"P1": {"boundary": {"flag": False}}, "P2": {"boundary": {"flag": True}}}, "p4": {}}
        self.assertTrue(rc.f6_boundary_flag(calc))
        calc["parameters"]["P2"]["boundary"]["flag"] = False
        self.assertFalse(rc.f6_boundary_flag(calc))
        calc["p4"] = {"nonop_share_boundary": {"flag": True}}
        self.assertTrue(rc.f6_boundary_flag(calc))
        self.assertTrue(rc.f6_boundary_flag({"boundary": {"flag": True}}))   # v1.5 bands 경로

    def test_g3_boundary_in_both(self):
        text = "G3 런웨이 3.03년(임계 3년 대비 +0.9% ⚠️ 경계)"
        self.assertIn(text, self.md)
        self.assertIn(text, self.frow("spacex-xai", "⑨ 적자 깊이"))

    # ---------------------------------------------------------------- S3 원자료·방법·트리거
    def test_raw_tables_share_v17_wording(self):
        for stale in ("모든 값은 기준선", "NTM PER 만 ⑥ 점수에 개입", "NTM PER 20·29·42·62·90 반개방", "하한 -5"):
            with self.subTest(stale=stale):
                self.assertNotIn(stale, self.md)
                self.assertNotIn(stale, self.html)
        for shared in (rc.raw_caption(self.ctx), rc.price_notice(self.ctx), rc.cash_definition_note(self.ctx), rc.vendor_policy_note(self.ctx)):
            self.assertIn(shared, self.md)
            self.assertIn(rc.inline_html(shared), self.html)
        self.assertEqual(self.html_text.count("열별 관측 상태:"), 2)
        self.assertIn(f"하한 {rc.f9_policy(self.ctx, 'floor')}.", self.html_text)

    def test_offbalance_cell_and_replaced_values_in_html(self):
        self.assertIn("$267.3B B종(verified) · 원문 <del>미개시 리스 $106B</del> (superseded)", self.html)
        self.assertIn("⚠️ 원문 $106B 는 이번 실행 실측 $267.3B(amazon.offbalance_B.obsreg25", self.html_text)

    def test_triggers_share_corrections_and_warnings(self):
        reps = rc.replacements(self.ctx)
        corrected = 0
        for t in self.triggers:
            why = rc.trigger_why(self.ctx, t, reps)
            corrected += why != t["why"]
            with self.subTest(tid=t["trigger_id"]):
                self.assertIn(rc.inline_html(why), self.html)
        self.assertGreaterEqual(corrected, 2)       # TRIG-015 원문 정정 · 대체된 수치 ⚠️
        self.assertIn("왜 중요한가(v1.5 원문)", self.html)

    def test_private_multiples_filled_from_v17_calc(self):
        self.assertIn("| Anthropic | $965.0B | $65.0B | 14.8 | $125.0B | 0.52 | -4 |", self.md)
        self.assertNotIn("점수는 정성 예외(C-12)", self.md)

    def test_vendor_mark_only_on_cells_engine_uses(self):
        self.assertIn("| Apple | $39.5B | $136.7B | ∞ | $62.2B† |", self.md)          # apple.net_cash.v15 가 쓰인다
        self.assertIn("| TSMC | $88.2B | $32.0B | ∞ | $69.2B |", self.md)           # tsmc 는 verified nc37
        self.assertIn("원천 정책 밖 공급사 값 26건", self.md)

    def test_limitations_section_in_both(self):
        self.assertIn("## 알려진 한계", self.md)
        self.assertIn("<h3>알려진 한계</h3>", self.html)
        for line in rc.limitations(self.ctx):
            with self.subTest(line=line[:30]):
                self.assertIn(line if line.startswith("  - ") else f"- {line}", self.md)
                # HTML 은 본문의 C-번호를 사전 링크로 바꾼다(`TEN-RC-02` 안의 `C-02` 도 걸린다) — 태그를 걷고 비교한다.
                self.assertIn(plain(rc.inline_html(line.removeprefix("  - "))), self.html_text)
        self.assertIn("alibaba — 가리지 못했다", self.md)

    def test_decisions_applied_is_not_consumption_proof(self):
        self.assertIn("소비됐다는 증명은 아니다", self.md)
        self.assertIn("소비됐다는 증명은 아니다", self.html_text)


if __name__ == "__main__":
    unittest.main()
