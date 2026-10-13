# 리포트 상단 탭(2026-10-07 사용자 요청): 탭 6개와 패널 연결, 앵커 무결성, 패널별 내용, JS 없는 경우를 메모리 렌더로 잠근다
from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard import engine, stages  # noqa: E402
from scorecard.render_html import TABS, js, load_availability, render_document  # noqa: E402

SLUGS = ("ai-scorecard-2026-09-obsreg", "ai-scorecard-2026-10-rescore")
MARKERS = {
    "tab-summary": ('id="kpis"', 'id="judgment-status"', 'id="mainTable"'),
    "tab-companies": ('class="cards"', 'id="card-'),
    "tab-raw": ("지표 원자료",),
    "tab-triggers": ("다음 재채점 트리거",),
    "tab-method": ("채점 방법과 규칙", 'id="code-index"'),
    "tab-sources": ("References",),
}


def render(slug: str) -> str:
    ctx = engine.load_context(slug)
    results = engine.load_results(slug)
    baseline, _obs, triggers = stages.load_baseline(ctx.run["baseline_id"])
    return render_document(ctx, results, baseline, triggers, {"review_type": "mem", "reviewers": []},
                           {"approval_id": "00000000-memory", "approved_by": "mem", "approved_at": "2026-10-07"},
                           load_availability(slug))


def panels(html: str) -> dict[str, str]:
    return {m.group(1): m.group(2) for m in re.finditer(r'<section class="tabpanel" id="(tab-[a-z]+)"[^>]*>(.*?)</section>', html, re.S)}


class ReportTabsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.html = {slug: render(slug) for slug in SLUGS}

    def test_six_tabs_control_existing_panels(self):
        for slug, html in self.html.items():
            with self.subTest(slug=slug):
                buttons = re.findall(r'<button type="button" role="tab" id="tabbtn-([a-z]+)" data-tab="(tab-[a-z]+)" '
                                     r'aria-controls="(tab-[a-z]+)"', html)
                self.assertEqual([b[0] for b in buttons], [t for t, _l in TABS])
                self.assertTrue(all(b[1] == b[2] == f"tab-{b[0]}" for b in buttons))
                self.assertEqual(list(panels(html)), [f"tab-{t}" for t, _l in TABS])
                # 첫 탭이 선택돼 있고, JS 가 없으면 탭 바는 숨고 패널은 모두 보인다(hidden 은 JS 가 세운다)
                self.assertIn('id="tabbtn-summary" data-tab="tab-summary" aria-controls="tab-summary" aria-selected="true"', html)
                self.assertIn('<nav class="tabs" role="tablist" aria-label="리포트 구역" hidden>', html)
                self.assertNotRegex(html, r'<section class="tabpanel"[^>]*\shidden')

    def test_every_in_page_anchor_has_a_target(self):
        for slug, html in self.html.items():
            with self.subTest(slug=slug):
                ids = set(re.findall(r'\sid="([^"]+)"', html))
                targets = {h for h in re.findall(r'href="#([^"]+)"', html)}
                self.assertTrue(targets, "앵커가 하나는 있어야 한다")
                self.assertEqual(sorted(targets - ids), [])

    def test_panels_hold_their_sections(self):
        for slug, html in self.html.items():
            with self.subTest(slug=slug):
                got = panels(html)
                for pid, needles in MARKERS.items():
                    for needle in needles:
                        self.assertIn(needle, got[pid], f"{pid} 에 {needle!r} 가 없다")
                if slug.endswith("rescore"):   # obsreg 는 triggers.json 이 없어 기준선 트리거 표를 그린다
                    self.assertIn('class="trig"', got["tab-triggers"])
                self.assertNotIn('id="mainTable"', got["tab-companies"])
                # 요약 탭은 순위표가 지도보다 먼저다
                s = got["tab-summary"]
                self.assertLess(s.index('id="mainTable"'), s.index("과점 × 함정 지도"))

    def test_no_section_heading_outside_panels(self):
        for slug, html in self.html.items():
            with self.subTest(slug=slug):
                outside = re.sub(r'<section class="tabpanel".*?</section>', "", html, flags=re.S)
                self.assertNotIn("<h2", outside)
                self.assertIn('<footer id="disclaimer"', outside, "투자 유의 문구는 탭 밖에서 늘 보인다")

    def test_script_switches_tabs_before_following_anchors(self):
        code = js()
        for needle in ("window.reportShow", "closest('.tabpanel')", "addEventListener('hashchange'",
                       "a[href^=\"#\"]", "history.replaceState"):
            self.assertIn(needle, code)
        # 순위표 행 클릭과 해시 펼침이 스크롤 전에 탭을 연다
        self.assertIn("window.reportShow(card); card.open=true", code)
        self.assertIn("window.reportShow(el);\n    el.open=true", code)
        # 좁은 화면에서 뒤쪽 탭이 잘려 있으면 .more 로 오른쪽 끝을 흐리게 한다(round 6 출력 리뷰)
        self.assertIn("classList.toggle('more'", code)
        # 해시를 달고 처음 열 때도 그 요소의 패널 하나만 연다(round 9 출력 리뷰). reportShow 는 숨긴 패널이 있을 때만 움직인다
        self.assertIn("const p=el.classList.contains('tabpanel')?el:el.closest('.tabpanel');", code)
        self.assertIn("if(!fromHash(true)) activate(panels[0].id,false);", code)

    def test_lede_reads_factor_ranges_from_rules(self):
        # 2026-10-07 외부 분석: '함정 각 0~-5' 는 ⑥ -7·⑦ -2·⑨ -4 와 달랐다
        for slug, html in self.html.items():
            with self.subTest(slug=slug):
                lede = re.search(r'<p class="lede">(.*?)</p>', html, re.S).group(1)
                for needle in ("② 2~5점", "③ 1~5점", "⑥ 0~-7점", "⑦ 0~-2점", "⑨ 0~-4점", "영업외 이익 비중"):
                    self.assertIn(needle, lede)
                self.assertNotIn("각 0~", html)

    def test_screen_names_drop_the_second_brand(self):
        # 2026-10-07 사용자 요청: 'Alphabet / Google'·'Amazon / AWS'·'SpaceX + xAI' 가 순위표 칸을 넓혔다
        html = self.html["ai-scorecard-2026-10-rescore"]
        rows = re.findall(r'<td class="name keep" data-k="name" data-v="([^"]+)">', html)
        cards = re.findall(r'<div class="cname">([^<]+)<', html)
        trigs = re.findall(r'<td class="tmeta"><div class="mono">[^<]+</div><div>([^<]+)</div>', html)
        for names in (rows, cards, trigs):
            self.assertTrue({"Alphabet", "Amazon", "SpaceX"} <= set(names), names)
            self.assertFalse([n for n in names if " / " in n or "xAI" in n], names)

    def test_header_has_no_conflict_notice_box(self):
        # 2026-10-08 사용자 지시: 리포트 머리의 이해상충 고지 상자를 싣지 않는다
        for slug, html in self.html.items():
            with self.subTest(slug=slug):
                self.assertNotIn("<b>이해상충 고지</b>", html)

    def test_judgment_status_box_counts_match_results(self):
        # 2026-10-08 사용자 결정: 첫 화면에 "이 점수는 언제 매겨졌나" 상자. 이어받은 칸 수가 results 와 같고,
        # 이전 실행이 있는 실행에만 "지난 실행 대비" 줄이 붙는다
        for slug, html in self.html.items():
            with self.subTest(slug=slug):
                box = re.search(r'<div class="notice info" id="judgment-status"([^>]*)>(.*?)</div>', html, re.S)
                self.assertIsNotNone(box, "판단 현황 상자 없음")
                attrs, body = box.group(1), box.group(2)
                results = engine.load_results(slug)
                cells = [c["factors"][f] for c in results["companies"] if not c["reference"] for f in c["factors"]]
                carried = sum(1 for fr in cells if fr["status"] == "carried_score")
                self.assertIn(f'data-carried="{carried}"', attrs)
                self.assertIn(f'data-total="{len(cells)}"', attrs)
                self.assertIn("이어받았다" if carried else "모두 이번 실행에서 매겼다", body)
                has_prev = bool((engine.load_context(slug).run.get("continued_from") or {}).get("run_id"))
                self.assertEqual("지난 실행(기준일" in body, has_prev)
                # 숫자만 남은 칸(② 경로 입력 없음)이 있으면 그 사실을 적는다
                if any(fr.get("basis") == "carried" for fr in cells):
                    self.assertIn("점수 숫자만 기록돼 있어", body)

    def test_draft_notes_of_a_factor_without_evidence_get_their_own_header(self):
        from scorecard.render_md import render_draft
        slug = "ai-scorecard-2026-10-rescore"
        ctx = engine.load_context(slug)
        baseline, _obs, triggers = stages.load_baseline(ctx.run["baseline_id"])
        lines = render_draft(ctx, engine.load_results(slug), baseline, triggers).splitlines()
        # 상장사 ⑥ 은 관측에서 계산해 근거 블록이 없다. 그 사유 줄은 ⑤ 블록이 아니라 ⑥ 머리줄 바로 아래에 온다
        heads = [i for i, line in enumerate(lines) if line == "- **⑥ 가격**:"]
        self.assertTrue(heads, "근거 블록이 없는 ⑥ 의 머리줄이 없다")
        for i in heads:
            self.assertTrue(lines[i + 1].startswith("  - "), lines[i + 1])


V21 = "ai-scorecard-2026-10-v21"


@unittest.skipUnless((ROOT / "output" / V21 / "results.json").is_file(), "v2.1 실행 없음")
class V21LayoutTest(unittest.TestCase):
    """2026-10-13 사용자 지시: 국면 지표는 자기 탭, 순위표 # 열 제거, ① AI 수익화 두 조건 설명 상자와 (가)·(나) 색 표지."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.html = render(V21)
        cls.old = render("ai-scorecard-2026-10-rescore")

    def test_regime_has_its_own_tab_after_summary(self):
        buttons = re.findall(r'role="tab" id="tabbtn-([a-z]+)"', self.html)
        self.assertEqual(buttons, ["summary", "regime", *[t for t, _l in TABS[1:]]])
        got = panels(self.html)
        self.assertIn("<h2>국면 지표 — 점수 없음</h2>", got["tab-regime"])
        self.assertIn("<h3>트리거 조건</h3>", got["tab-regime"])
        self.assertNotIn("설비투자 가속도", got["tab-summary"])
        self.assertNotIn('id="tabbtn-regime"', self.old, "국면 지표 선언이 없는 실행에는 탭이 없다")

    def test_token_index_is_a_hero_card_at_top_of_regime_tab(self):
        tab = panels(self.html)["tab-regime"]
        hero = re.search(r'<div class="tokhero">(.*?)</div>\s*<p class="sub">', tab, re.S)
        self.assertIsNotNone(hero, "토큰 단가 카드가 없다")
        self.assertLess(tab.index('class="tokhero"'), tab.index("설비투자 가속도"), "카드가 국면 지표 탭 맨 위에 있어야 한다")
        self.assertIn('<div class="v">$0.97<span class="u"> / 100만 토큰</span></div>', tab)
        self.assertIn('href="https://www.silicondata.com/products/silicon-index/llm-token-expenditure-index"', tab)
        self.assertEqual(tab.count("토큰 단가 지수</h3>"), 1, "아래쪽의 한 줄 문장 절은 없어졌다")

    def test_ranking_has_no_rank_column(self):
        head = re.search(r'<table id="mainTable"><thead>(.*?)</thead>', self.html, re.S).group(1)
        self.assertNotIn('data-k="rank"', head)
        self.assertTrue(head.startswith('<tr><th scope="col" class="name keep" data-k="name">기업</th>'), head[:80])
        self.assertNotIn('data-k="rank"', re.search(r'<table id="mainTable">.*?</table>', self.html, re.S).group(0))

    def test_ai_conditions_box_and_marks(self):
        got = panels(self.html)
        for pid in ("tab-summary", "tab-companies"):
            self.assertIn('<div class="condbox"><h3>① AI 수익화 \'예\' 의 두 조건</h3>', got[pid])
        self.assertIn("최고 4점이다", got["tab-summary"])
        # 카드의 ① 판정 줄 표지가 색을 입었고, 태그 속성 안에는 들어가지 않았다
        self.assertIn('<span class="cond cond-b">(나)</span>는 선다', got["tab-companies"])
        self.assertNotRegex(self.html, r'="[^"]*<span class="cond')
        self.assertNotIn('class="condbox"', self.old, "5점 조건이 없는 규칙의 실행에는 상자가 없다")

    def test_ai_column_is_shown_as_factor1_addon(self):
        # 2026-10-13 사용자 지시: AI 수익화는 ① 의 부가 조건이라 독립 열처럼 보이지 않게 ① 열에 붙인다.
        head = re.search(r'<table id="mainTable"><thead>(.*?)</thead>', self.html, re.S).group(1)
        self.assertRegex(head, r'<th[^>]*data-k="F1"[^>]*class="f1grp"')
        self.assertIn('<span class="subof">① 부가 조건</span>AI 수익화</th>', head)
        self.assertLess(head.index('data-k="F1"'), head.index('data-k="F1ai"'))
        self.assertLess(head.index('data-k="F1ai"'), head.index('data-k="F2"'))
        self.assertNotIn('data-k="F1ai"', self.old, "AI 수익화 표시 필드가 없는 옛 실행에는 열이 없다")

    def test_method_table_links_have_factor_cards(self):
        # 2026-10-13 사용자 지적: 규칙 v2.1 에서 ④⑧ 카드가 빠져 방법 절 표의 두 링크가 갈 곳이 없었다.
        for html in (self.html, self.old):
            links = re.findall(r'href="#method-(F\d)"', html)
            self.assertEqual(sorted(set(links)), [f"F{i}" for i in range(1, 10)])
            for fid in links:
                self.assertIn(f'id="method-{fid}"', html, f"{fid} 카드가 없다")


if __name__ == "__main__":
    unittest.main()
