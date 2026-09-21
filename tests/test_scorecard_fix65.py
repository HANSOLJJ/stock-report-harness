# FIX-65 — HTML 가독성 넷(라벨 색 버그 · 글자 크기 · 방법과 규칙 배치 · 과점/함정 막대)을 고정한다
from __future__ import annotations

import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard import render_common as rc  # noqa: E402
from scorecard import render_html as rh  # noqa: E402
from scorecard.engine import load_context  # noqa: E402
from scorecard.rules import load_rules  # noqa: E402
from scorecard.stages import current_hashes  # noqa: E402

RULES = load_rules("v1.7")
SLUG = "ai-scorecard-2026-09-obsreg"
RUN_DIR = ROOT / "scorecard" / "runs" / SLUG
HTML = ROOT / "output" / f"{SLUG}.html"

TOTALS = {"alphabet": 15, "amazon": 15, "meta": 15, "microsoft": 14, "tsmc": 10, "anthropic": 10,
          "spacex-xai": 9, "nvidia": 9, "apple": 8, "alibaba": 7, "palantir": 6, "tesla": 5,
          "openai": 4, "oracle": 2}


class Fix65Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.results = json.loads((RUN_DIR / "results.json").read_text(encoding="utf-8"))
        cls.approval = json.loads((RUN_DIR / "approval.json").read_text(encoding="utf-8"))
        cls.ctx = load_context(SLUG)
        cls.html = HTML.read_text(encoding="utf-8")
        cls.bars = re.search(r'<div class="mtwrap">(<svg viewBox="0 0 (\d+) (\d+)".*?</svg>)</div>',
                             cls.html, re.S)

    # ---------------------------------------------------------------- 경계: 승인이 유지된다
    def test_scores_and_approval_untouched(self):
        self.assertEqual({c["company_id"]: c["total"] for c in self.results["companies"]}, TOTALS)
        # 2026-09-17 FIX-67: 방법 문장 재작성으로 draft 만 바뀌었다(승인은 재검토 뒤 되살린다).
        cur = current_hashes(SLUG)
        self.assertEqual({k: v for k, v in self.approval["hashes"].items() if k != "draft"},
                         {k: v for k, v in cur.items() if k != "draft"})
        self.assertEqual(self.approval["approval_id"], "0b054d597be5bf87")
        self.assertEqual(self.results["results_hash"],
                         "4a3f6c05b206ef81f370ac7765a1a948fe1e9cf6d1999c142bac4f124e04910b")
        self.assertNotEqual(self.approval["hashes"]["draft"], cur["draft"])

    # ---------------------------------------------------------------- S1 라벨 색 버그
    def test_svg_labels_are_filled_not_colored(self):
        """SVG `<text>`·`<tspan>` 은 `color` 가 아니라 `fill` 로 칠해진다 — 점수가 검게 떨어졌다."""
        self.assertIn("svg .c-g5{fill:var(--g5)}", self.html)
        self.assertIn("svg .c-g0{fill:var(--tx3)}", self.html)
        # 산점도 점수 tspan 이 등급 클래스를 그대로 달고 있고, 위 규칙이 그것을 받는다.
        labels = re.findall(r'<tspan class="(c-g\d)"[^>]*>(\d+)점</tspan>', self.html)
        self.assertEqual(len(labels), 13)                      # 공동 순위 하나가 한 라벨로 묶인다
        for cls, _score in labels:
            with self.subTest(cls=cls):
                self.assertIn(f"svg .{cls}{{fill:", self.html)

    def test_no_svg_element_relies_on_color_alone(self):
        """전수 — SVG 안에서 class 로만 색을 주는 자리가 더 있는지 본다."""
        src = (ROOT / "scripts" / "scorecard" / "render_html.py").read_text(encoding="utf-8")
        marked = re.findall(r'<(?:text|tspan)[^>]*class="([^"]+)"', src)
        # 클래스를 다는 자리는 등급 색뿐이고 나머지는 전부 style="fill:…" 을 직접 준다.
        self.assertTrue(marked)
        for cls in marked:
            with self.subTest(cls=cls):
                self.assertTrue(cls.startswith("c-{total_class") or cls.startswith("c-g"), cls)

    # ---------------------------------------------------------------- S2 글자 크기와 여백
    def test_type_scale_and_spacing_grew(self):
        scale = dict(re.findall(r"--fs-(\w+):(\d+)px", self.html))
        self.assertGreaterEqual(int(scale["base"]), 16)         # 본문 16px 이상
        self.assertEqual(int(scale["md"]), int(scale["base"]) - 1)   # 표는 한 단계 아래까지만
        self.assertGreater(int(scale["md"]), int(scale["sm"]))
        self.assertIn("th,td{padding:14px 12px;", self.html)
        self.assertIn("line-height:1.7;-webkit-font-smoothing", self.html)
        self.assertIn("ul.tight li{margin:8px 0;", self.html)
        # 차트 글자도 같이 올렸다 — 본문만 키우면 차트 글자만 작게 남는다.
        sizes = {int(x) for x in re.findall(r'font-size="(\d+)"', self.html)}
        self.assertEqual(sizes, {14, 15})

    def test_long_tokens_wrap_in_cards(self):
        """`Apple·NVIDIA·AMD·…` 가 한 낱말로 취급돼 좁은 화면에서 카드 밖으로 잘렸다."""
        self.assertIn("overflow-wrap:anywhere", re.search(r"\.fpts li\{[^}]*\}", self.html).group(0))

    # ---------------------------------------------------------------- S3 방법과 규칙
    def test_method_lines_are_separate_blocks_with_factor_headings(self):
        # 2026-09-17 FIX-67: 문장을 줄 단위로 잘게 나눠 블록 수가 늘었다. 요지는 **줄마다 블록**이다.
        # 2026-09-17 FIX-75: 항목 카드가 그 일을 한다 — 항목에 딸린 문장은 카드 안 목록으로 가고
        # `mblk` 에는 여러 항목에 걸치는 문단과 한계만 남는다. **한 덩어리로 쏟아지지 않는다**가 요지다.
        top_limits = [x for x in rc.limitations(self.ctx) if not x.startswith("  ")]
        loose = [x for fid, ls in rc.method_sections(self.ctx, self.results) if fid is None for x in ls]
        self.assertEqual(self.html.count('<div class="mblk">'), len(loose) + len(top_limits))
        # 항목에 딸린 문장은 아홉 카드 안에 있고, 카드 수는 factor 수와 같다.
        self.assertEqual(self.html.count('<details class="fcard"'), len(rh.FACTOR_IDS))
        for fid, lines in rc.method_sections(self.ctx, self.results):
            if fid:
                with self.subTest(factor=fid):
                    self.assertIn(f'id="method-{fid}"', self.html)
                    self.assertTrue(lines, "항목 카드가 비었다")
        # 맨 앞이 factor 표시이고 그 줄이 한 factor 만 다룰 때만 제목을 세운다.
        tags = re.findall(r'<span class="mtag">(.)</span>', self.html)
        self.assertTrue(set(tags) <= set(rh.FACTOR_MARKS), tags)
        multi = next(x for x in rc.method_lines(self.ctx, self.results) if "③ Last Mover" in x)
        self.assertGreater(len({ch for ch in multi if ch in rh.FACTOR_MARKS}), 1)
        self.assertNotIn('<span class="mtag">③</span>', self.html)

    def test_decision_codes_show_their_meaning_in_place(self):
        """코드만 봐서는 뜻을 알 수 없었다.

        2026-09-18 FIX-79 S2: 칩으로 요약을 펴 보여도 규칙 파일의 설계 기록이라 뜻이 읽히지 않았다(사용자 지적).
        본문은 번호 없이 **결정의 효과를 말로** 적고, 결정 기록은 감사 기록으로 옮겼다.
        """
        self.assertNotIn('<details class="mdec"', self.html)
        self.assertNotIn("관련 결정", self.html)
        audit = (ROOT / "output" / f"{SLUG}-audit.md").read_text(encoding="utf-8")
        self.assertIn("## 결정 기록", audit)
        # 요약 문구는 규칙 파일 그대로다 — 새로 쓰지 않는다.
        d = RULES.decision("C-03")
        self.assertIn(" ".join(str(d["summary"]).split())[:40], audit)

    def test_no_markdown_marks_leak_into_the_report(self):
        """규칙 파일 문면의 `**`·백틱·`~~` 가 독자 화면에 그대로 보이던 자리를 전수로 훑었다."""
        body = self.html.split("</style>", 1)[1]               # CSS 주석의 한국어 설명은 제외
        self.assertEqual(re.findall(r"\*\*", body), [])
        self.assertEqual(re.findall(r"~~", body), [])
        self.assertEqual(body.count("`"), 0)
        self.assertIn("<code>", body)                           # 백틱은 사라진 것이 아니라 태그가 됐다

    def test_limitations_use_the_same_blocks(self):
        marker = "알려진 한계</h3>"
        after = self.html.split(marker, 1)[1][:4000]
        self.assertIn('<div class="mblk">', after)

    # ---------------------------------------------------------------- S4 과점·함정 막대
    def test_bar_chart_is_added_not_replacing_the_scatter(self):
        self.assertIsNotNone(self.bars)
        self.assertIn("과점 × 함정 지도", self.html)            # 산점도 절이 그대로 있다
        self.assertIn('aria-label="과점 factor 대비 함정 감점 산점도', self.html)
        self.assertIn("기업별 과점 합계와 함정 합계", self.html)

    def test_bars_read_moat_trap_total_as_recorded(self):
        svg = self.bars.group(1)
        order = [c for c in sorted(self.results["companies"],
                                   key=lambda c: (-c["total"], -c["moat"], c["display_name"]))]
        names = re.findall(r'style="fill:var\(--tx\)" font-size="14" text-anchor="end">([^<]+)</text>', svg)
        self.assertEqual(names, [rh.short_name(c["display_name"]) for c in order])
        moats = [int(x) for x in re.findall(r'style="fill:var\(--g4\)" font-size="14" font-weight="700">(-?\d+)</text>', svg)]
        traps = [int(x) for x in re.findall(
            r'style="fill:var\(--g1\)" font-size="14" font-weight="700" text-anchor="end">(-?\d+)</text>', svg)]
        totals = [int(x) for x in re.findall(r'class="c-g\d" font-size="15" font-weight="800" text-anchor="end">(-?\d+)</text>', svg)]
        self.assertEqual(moats, [c["moat"] for c in order])
        self.assertEqual(traps, [c["trap"] for c in order])
        self.assertEqual(totals, [c["total"] for c in order])

    def test_bars_share_one_scale_and_stay_inside_the_box(self):
        svg, W = self.bars.group(1), int(self.bars.group(2))
        rects = [(float(a), float(b)) for a, b in re.findall(r'<rect x="([\d.]+)"[^>]*width="([\d.]+)"', svg)]
        self.assertEqual(len(rects), 28)                        # 14개사 × 과점·함정
        xs = [x for x, _ in rects] + [x + w for x, w in rects]
        texts = [float(x) for x in re.findall(r'<text x="([\d.-]+)"', svg)]
        self.assertGreaterEqual(min(xs + texts), 0)
        self.assertLessEqual(max(xs + texts), W)                # 잘리는 글자가 없다
        # **좌우 축척이 하나여야** 같은 길이가 같은 값을 뜻한다. 좌표는 소수 첫째 자리로 반올림돼 있다.
        order = sorted(self.results["companies"], key=lambda c: (-c["total"], -c["moat"], c["display_name"]))
        units = [w / c["moat"] for (_x, w), c in zip(rects[0::2], order)]
        units += [w / -c["trap"] for (_x, w), c in zip(rects[1::2], order)]
        self.assertLess(max(units) - min(units), 0.02, units)

    def test_bar_chart_stays_readable_on_a_phone(self):
        """14행을 폰 폭에 비율로 욱여넣으면 글자가 6px 로 줄어든다 — 칸 안에서만 가로로 스크롤한다."""
        self.assertIn(".mtwrap{overflow-x:auto}", self.html)
        m = re.search(r"\.mtwrap svg\{min-width:(\d+)px;max-width:(\d+)px", self.html)
        lo, hi = int(m.group(1)), int(m.group(2))
        W = int(self.bars.group(2))
        self.assertGreaterEqual(14 * lo / W, 12)                # 폰에서도 12px 이상으로 보인다
        self.assertLess(hi / W, 1.45)                           # 데스크톱에서 지나치게 커지지 않는다

    def test_bar_colors_reuse_existing_tokens(self):
        svg = self.bars.group(1)
        used = set(re.findall(r"var\((--[\w-]+)\)", svg))
        known = set(re.findall(r"(--[\w-]+):#", self.html)) | {"--tx", "--tx2", "--tx3"}
        self.assertTrue(used <= known, used - known)            # 새 색을 만들지 않았다


if __name__ == "__main__":
    unittest.main()
