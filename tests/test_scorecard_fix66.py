# FIX-66 — 코드 색인(F·G·P·상태·근거·긴장)과 C-17 날짜 반복 정리를 고정한다
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
from scorecard.render_md import STATUS_LABEL  # noqa: E402
from scorecard.rules import load_rules  # noqa: E402
from scorecard.stages import current_hashes  # noqa: E402

RULES = load_rules("v1.7")
SLUG = "ai-scorecard-2026-09-obsreg"
RUN_DIR = ROOT / "scorecard" / "runs" / SLUG
HTML = ROOT / "output" / f"{SLUG}.html"

TOTALS = {"alphabet": 15, "amazon": 15, "meta": 15, "microsoft": 14, "tsmc": 10, "anthropic": 10,
          "spacex-xai": 9, "nvidia": 9, "apple": 8, "alibaba": 7, "palantir": 6, "tesla": 5,
          "openai": 4, "oracle": 2}


class Fix66Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.results = json.loads((RUN_DIR / "results.json").read_text(encoding="utf-8"))
        cls.approval = json.loads((RUN_DIR / "approval.json").read_text(encoding="utf-8"))
        cls.ctx = load_context(SLUG)
        cls.html = HTML.read_text(encoding="utf-8")
        cls.index = cls.html.split('id="code-index"', 1)[1].split('id="c-glossary"', 1)[0]

    # ---------------------------------------------------------------- 경계
    def test_scores_and_approval_untouched(self):
        self.assertEqual({c["company_id"]: c["total"] for c in self.results["companies"]}, TOTALS)
        self.assertEqual(self.approval["hashes"], current_hashes(SLUG))
        self.assertEqual(self.approval["approval_id"], "0b054d597be5bf87")
        self.assertEqual(self.results["results_hash"],
                         "4a3f6c05b206ef81f370ac7765a1a948fe1e9cf6d1999c142bac4f124e04910b")
        self.assertEqual(self.approval["hashes"]["draft"],
                         "7eddab49d6adf56fe8ffd5becdd063ee075f2378370da9e33cd207d73ef4a782")

    # ---------------------------------------------------------------- S1 색인
    def test_index_has_every_group(self):
        self.assertEqual(re.findall(r'<details class="ixblk" id="ix-(\w+)"', self.index),
                         ["factor", "param", "gate", "status", "basis", "ten"])
        ids = re.findall(r'<div class="ixrow" id="idx-([^"]+)"', self.index)
        for code in [f"F{i}" for i in range(1, 10)] + [f"P{i}" for i in range(1, 5)] + [f"G{i}" for i in range(1, 5)]:
            with self.subTest(code=code):
                self.assertIn(code, ids)
        for t in RULES.payload["open_tensions"]:
            self.assertIn(t["id"], ids)

    def test_factor_and_parameter_names_come_from_the_rules(self):
        """**문구를 지어내지 않는다** — 규칙 파일에 있는 것을 그대로 쓴다."""
        for fid in rh.FACTOR_IDS:
            with self.subTest(fid=fid):
                row = self._row(fid)
                self.assertIn(RULES.factor(fid)["label"], row)
                self.assertIn(RULES.factor(fid)["mode"], row)
        params = RULES.payload["policies"]["f6"]["parameters"]
        for pid, spec in params.items():
            with self.subTest(pid=pid):
                row = self._row(pid)
                self.assertIn(spec["label"], row)
                self.assertIn(spec["question"], row)
        p4 = RULES.payload["policies"]["f6"]["p4"]
        self.assertIn(p4["label"], self._row("P4"))
        self.assertIn(p4["question"], self._row("P4"))

    def test_gate_names_come_from_the_method_line(self):
        """규칙 파일에 게이트 이름 키가 **없어서** ⑨ 설명 줄에서 읽는다. 그 줄은 바꾸지 않는다."""
        f9 = RULES.payload["policies"]["f9"]
        self.assertEqual([k for k in f9 if re.fullmatch(r"g[1-4]_(label|name|title)", k)], [])
        line = next(x for x in rc.method_lines(self.ctx) if x.startswith("⑨"))
        docs = rh._gate_docs(self.ctx)
        self.assertEqual([d[0] for d in docs], ["G1", "G2", "G3", "G4"])
        for code, name, note in docs:
            with self.subTest(code=code):
                self.assertIn(f"{code} {name}({note})", line)   # 줄에서 그대로 떼 왔다
                self.assertIn(name, self._row(code))

    def test_body_codes_link_into_the_index_without_burying_the_text(self):
        links = re.findall(r'<a class="tcode(?: first)?" href="#idx-([^"]+)">', self.html)
        self.assertTrue(links)
        # 앵커가 전부 실재한다.
        for code in set(links):
            with self.subTest(code=code):
                self.assertIn(f'id="idx-{code}"', self.index)
        # 본문에 F 201 · G 111 · P 152 회가 나오지만 링크는 그보다 훨씬 적어야 한다.
        text = re.sub(r"<[^>]+>", " ", self.html.split("</style>", 1)[1])
        raw = len(re.findall(r"(?<![.\w가-힣])(F[1-9]|G[1-4]|P[1-4])(?![\w.-])", text))
        self.assertGreater(raw, 300)
        self.assertLess(len(links), raw / 2)

    def test_first_mention_shows_the_name_only_where_it_is_missing(self):
        named = re.findall(r'<a class="tcode first" href="#idx-([^"]+)">[^<]*<span class="tname">([^<]+)</span>',
                           self.html)
        codes = {c for c, _n in named}
        # 이름이 어디에도 없는 코드에만 붙인다. P1~P3 은 본문이 `P1 PER` 처럼 이미 달고 나온다.
        self.assertEqual(codes, {"G1", "G2", "G3", "G4", "P4"})
        for code, name in named:
            with self.subTest(code=code):
                self.assertEqual(name, rh.index_terms(self.ctx)[code])

    def test_work_codes_and_judgment_ids_are_not_linked(self):
        """`F5-IMPL-48`(작업 코드)과 `alphabet.F9`(판단 id)는 factor 코드가 아니다."""
        self.assertNotIn('<a class="tcode" href="#idx-F5">F5</a>-IMPL', self.html)
        self.assertIn("F5-IMPL-48", re.sub(r"<[^>]+>", "", self.html))
        self.assertNotRegex(self.html, r'\.<a class="tcode[^"]*" href="#idx-F\d">')

    # ---------------------------------------------------------------- S2 상태·근거
    def test_status_and_basis_are_shown_as_two_things(self):
        """붙여 쓰면 `승계 manual` 이 한 단어로 읽혔다."""
        self.assertIn('<span class="k">상태</span>', self.html)
        self.assertIn('<span class="k">근거</span>', self.html)
        self.assertIn('<span class="sep">|</span>', self.html)
        self.assertEqual(self.html.count('<span class="fst">'), 14 * 9)

    def test_carried_is_marked_as_the_weakest_basis(self):
        self.assertIn('<span class="b weak">carried 숫자만 승계</span>', self.html)
        n = sum(1 for c in self.results["companies"] for f in rh.FACTOR_IDS
                if c["factors"][f]["basis"] == "carried")
        self.assertEqual(self.html.count('<span class="b weak">carried 숫자만 승계</span>'), n)
        self.assertEqual(n, 16)
        row = self._row("carried")
        self.assertIn("근거가 가장 약한 칸이다", row)
        self.assertIn("calc_qual.py:45", row)
        self.assertIn("calc_qual.py:157", row)

    def test_every_basis_in_use_is_documented_with_its_source(self):
        used = {c["factors"][f]["basis"] for c in self.results["companies"] for f in rh.FACTOR_IDS}
        self.assertEqual(used, {"computed", "manual", "carried", "grade", "matrix", "criteria"})
        for basis in used:
            with self.subTest(basis=basis):
                row = self._row(basis)
                self.assertIn(rh.BASIS_DOC[basis][0], row)
                self.assertIn("근거 ", row)                     # 파일·행이 붙는다
                self.assertRegex(row, r"calc_\w+\.py:\d+")

    def test_statuses_in_use_are_documented(self):
        used = {c["factors"][f]["status"] for c in self.results["companies"] for f in rh.FACTOR_IDS}
        for status in used:
            with self.subTest(status=status):
                self.assertIn(STATUS_LABEL[status], self._row(status))

    # ---------------------------------------------------------------- S3 C-17
    def test_identical_dates_are_written_once(self):
        base, price, cutoff = rh._asof_dates(self.ctx)
        self.assertEqual((base, price), (cutoff, cutoff))       # 이번 실행은 셋이 같다
        line = re.search(r"기준일[^<]*정보 컷오프[^<]*", self.html)
        self.assertIsNotNone(line)
        self.assertIn("모두", rh._asof_line(self.ctx))
        self.assertEqual(rh._asof_line(self.ctx).count(base), 1)
        # 값이 다르면 셋을 펼친다.
        class Fake:
            run = {"as_of": "2026-09-02", "price_as_of": "2026-09-01", "info_cutoff": "2026-09-07"}
        spread = rh._asof_line(Fake())
        for d in ("2026-09-02", "2026-09-01", "2026-09-07"):
            self.assertIn(d, spread)

    def test_c17_internal_memo_gets_a_reader_facing_note(self):
        """규칙 요약이 내부 메모라 그대로는 뜻이 통하지 않는다. **원문은 지우지 않고** 옆에 덧붙인다."""
        c17 = RULES.decision("C-17")
        self.assertEqual(c17["summary"], "기준일 9/2 인데 9/3~9/7 사건이 섞임")     # 규칙은 그대로다
        self.assertIn(c17["summary"], re.sub(r"<[^>]+>", "", self.html))
        note = re.search(r'<span class="runnote">(.*?)</span>', self.html, re.S)
        self.assertIsNotNone(note)
        plain = re.sub(r"<[^>]+>", "", note.group(1))
        self.assertIn("계기를 적은 기록이다", plain)
        self.assertIn("모두", plain)
        self.assertIn(rh._asof_dates(self.ctx)[0], plain)
        self.assertEqual(rh._decision_run_note(self.ctx, "C-13"), "")   # 다른 결정에는 안 붙는다

    # ---------------------------------------------------------------- 표시 회귀
    def test_no_regression_from_the_previous_round(self):
        body = self.html.split("</style>", 1)[1]
        self.assertEqual(re.findall(r"\*\*", body), [])          # FIX-65 에서 닫은 자리
        self.assertEqual(body.count("`"), 0)
        self.assertIn("svg .c-g5{fill:var(--g5)}", self.html)
        self.assertIn(".mtwrap{overflow-x:auto}", self.html)
        # 문장 속 링크도 24px 를 채운다.
        self.assertIn("min-width:24px;min-height:24px", re.search(r"\.tcode\{[^}]*\}", self.html).group(0))

    def _row(self, code: str) -> str:
        m = re.search(rf'<div class="ixrow" id="idx-{re.escape(code)}">(.*?)</div>\s*(?=<div class="ixrow"|</div>)',
                      self.index, re.S)
        self.assertIsNotNone(m, f"색인에 {code} 행이 없다")
        return m.group(1)


if __name__ == "__main__":
    unittest.main()
