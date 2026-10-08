# 첫 화면 판단 현황 상자가 규칙 v2.0 정기 실행에서 "재판단으로 닫힌 쟁점" 을 바르게 세는지 메모리 판단으로 잠근다
from __future__ import annotations

import copy
import re
import sys
import unittest
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard import engine  # noqa: E402
from scorecard.render_html import render_judgment_status  # noqa: E402
from tests.test_v20_render_lockin import R20, SLUG, build_v20  # noqa: E402

PRIOR_AS_OF = "2026-10-07"


def box(ctx, results) -> tuple[str, str]:
    m = re.search(r'<div class="notice info" id="judgment-status"([^>]*)>(.*?)</div>', render_judgment_status(ctx, results), re.S)
    return m.group(1), m.group(2)


def with_prior(ctx, as_of: str | None):
    run = copy.deepcopy(ctx.run)
    if as_of is None:
        run.pop("continued_from", None)
    else:
        run["continued_from"] = {**run["continued_from"], "as_of": as_of}
    return replace(ctx, run=run)


def edit(ctx, pair: tuple[str, str], **fields):
    judgments = [dict(j, **fields) if (j["company_id"], j["factor"]) == pair else j for j in ctx.judgments]
    return replace(ctx, judgments=judgments)


class RejudgeStatusTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.ctx, cls.results, _b, _t = build_v20()
        cls.open = [t for t in R20.payload["open_tensions"] if t.get("status") == "open"]

    def test_zero_carried_run_reads_as_all_judged_and_all_tensions_closed(self):
        attrs, body = box(with_prior(self.ctx, PRIOR_AS_OF), self.results)
        self.assertIn('data-carried="0"', attrs)
        self.assertIn("모두 이번 실행에서 매겼다", body)
        self.assertNotIn("이어받았다", body)
        self.assertIn(f"리뷰에서 지적된 쟁점 {len(self.open)}건 가운데 이번 실행의 재판단으로 닫힌 것은 <b>{len(self.open)}건</b>, "
                      "남은 것은 <b>0건</b>이다.", body)
        self.assertNotIn("재검토로 넘긴", body)

    def test_carried_old_and_reconfirmed_judgments_are_counted_apart(self):
        ids = {t["id"] for t in self.open}
        if not {"TEN-RA5-01", "TEN-RC4-04", "TEN-RC3-01"} <= ids:
            self.skipTest("규칙 긴장 목록이 이 시험의 전제와 다르다")
        ctx = with_prior(self.ctx, PRIOR_AS_OF)
        # 승계 판단 → 닫히지 않는다(TEN-RA5-01 은 anthropic.F8 하나만 걸려 있다)
        ctx = edit(ctx, ("anthropic", "F8"), status="carried", reviewed_at="2026-09-02")
        # 검토일은 옛날이지만 이번 실행 기간에 다시 확인했다 → 닫힌다(TEN-RC3-01 의 openai.F7)
        ctx = edit(ctx, ("openai", "F7"), reviewed_at="2026-09-02",
                   reconfirmed=[{"at": "2026-10-09", "by": "에이전트", "evidence_ids": ["EV-openai-001"]}])
        # 다시 확인한 날이 이어받은 실행의 기준일보다 앞선다 → 닫히지 않는다(TEN-RC4-04 의 tsmc.F3)
        ctx = edit(ctx, ("tsmc", "F3"), reviewed_at="2026-09-02",
                   reconfirmed=[{"at": "2026-10-05", "by": "에이전트", "evidence_ids": ["EV-tsmc-001"]}])
        _attrs, body = box(ctx, self.results)
        self.assertIn(f"리뷰에서 지적된 쟁점 {len(self.open)}건 가운데 이번 실행의 재판단으로 닫힌 것은 <b>{len(self.open) - 2}건</b>, "
                      "남은 것은 <b>2건</b>이다.", body)
        months = sorted({t["recheck_at"] for t in self.open if t["id"] in ("TEN-RA5-01", "TEN-RC4-04")})
        self.assertIn(f"남은 쟁점은 {' · '.join(months)} 에 다시 본다.", body)
        # 다시 확인한 날은 검토일 범위에도 들어간다
        self.assertIn("2026-10-09", body)

    def test_same_day_as_prior_as_of_is_not_after(self):
        ctx = edit(with_prior(self.ctx, PRIOR_AS_OF), ("anthropic", "F8"), reviewed_at=PRIOR_AS_OF)
        _attrs, body = box(ctx, self.results)
        self.assertIn("남은 것은 <b>1건</b>이다", body)

    def test_without_continued_from_keeps_the_old_sentence(self):
        _attrs, body = box(with_prior(self.ctx, None), self.results)
        self.assertIn(f"재검토로 넘긴 쟁점은 <b>{len(self.open)}건</b>", body)
        self.assertNotIn("재판단으로 닫힌", body)

    def test_old_rules_keep_the_old_sentence_even_with_continued_from(self):
        ctx = engine.load_context(SLUG)
        self.assertTrue((ctx.run.get("continued_from") or {}).get("as_of"))
        _attrs, body = box(ctx, engine.load_results(SLUG))
        self.assertIn("재검토로 넘긴 쟁점은", body)
        self.assertNotIn("재판단으로 닫힌", body)
        # 2026-10-09: ⑨ 게이트 판정 입력 줄은 재판단 조항이 있는 규칙에서만 나온다(옛 실행 HTML 불변)
        self.assertNotIn("게이트 판정 입력을 판단으로 함께 받고", body)

    def test_gate_input_cells_are_named_with_their_review_dates(self):
        # 2026-10-09 출력·가독성 리뷰: 관측 계산 칸 가운데 ⑨ 는 판단(게이트 입력)을 받으므로 그 수와 검토일을 상자에 적는다
        n_gate = sum(1 for c in self.results["companies"] if not c["reference"]
                     if c["factors"]["F9"]["status"] == "ok" and c["factors"]["F9"].get("basis") == "computed"
                     and c["factors"]["F9"].get("judgment_id"))
        self.assertGreater(n_gate, 0)
        _attrs, body = box(with_prior(self.ctx, PRIOR_AS_OF), self.results)
        self.assertIn(f"⑨{n_gate} {n_gate}칸은 게이트 판정 입력을 판단으로 함께 받고, 그 판단의 검토일은 2026-10-09 이다(재판단 범위 밖이다).", body)
        self.assertNotIn("이어받았고", body)
        # 이어받은 ⑨ 판단이 있으면 그 수를 따로 적고 검토일 범위가 넓어진다
        ctx = edit(with_prior(self.ctx, PRIOR_AS_OF), ("alphabet", "F9"), status="carried", reviewed_at="2026-09-02")
        _attrs, body = box(ctx, self.results)
        self.assertIn(f"⑨{n_gate} {n_gate}칸은 게이트 판정 입력을 판단으로 함께 받고, 그 판단의 검토일은 2026-09-02 ~ 2026-10-09 이다. "
                      "그중 1칸은 이전 실행의 판단을 그대로 이어받았고 재판단 범위 밖이다.", body)
        self.assertIn("모두 이번 실행에서 매겼다", body)


class CardEvidenceNoteTest(unittest.TestCase):
    def test_summary_sentence_only_when_the_run_has_company_summaries(self):
        # 2026-10-09 출력·가독성 리뷰: 기업 요약이 없는 실행에 "한 줄 요약은 … 기업 요약이다" 가 실렸다
        from scorecard import render_common as rc
        with_s = rc.card_evidence_note("baseline", has_summaries=True)
        without = rc.card_evidence_note("baseline", has_summaries=False)
        self.assertIn("카드의 한 줄 요약은 이 실행에서 확정한 기업 요약이다.", with_s)
        self.assertNotIn("기업 요약", without)
        self.assertTrue(without.startswith("근거는 각 판단에 적힌 현재 근거 문장이다."))
        self.assertIn("카드의 한 줄 요약은", rc.card_evidence_note("baseline"))


if __name__ == "__main__":
    unittest.main()
