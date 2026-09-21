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
        # 2026-09-17 FIX-67: 방법 문장 재작성으로 draft 만 바뀌었다(승인은 재검토 뒤 되살린다).
        cur = current_hashes(SLUG)
        self.assertEqual({k: v for k, v in self.approval["hashes"].items() if k != "draft"},
                         {k: v for k, v in cur.items() if k != "draft"})
        self.assertEqual(self.approval["approval_id"], "0b054d597be5bf87")
        self.assertEqual(self.results["results_hash"],
                         "4a3f6c05b206ef81f370ac7765a1a948fe1e9cf6d1999c142bac4f124e04910b")
        self.assertNotEqual(self.approval["hashes"]["draft"], cur["draft"])

    # ---------------------------------------------------------------- S1 색인
    def test_index_has_every_group(self):
        # 2026-09-17 FIX-67: `점수를 만드는 방식`(mode) 묶음이 들어왔고, P·G 는 번호가 아니라 이름으로 선다.
        self.assertEqual(re.findall(r'<details class="ixblk" id="ix-(\w+)"', self.index),
                         ["factor", "mode", "param", "gate", "status", "basis"])   # 2026-09-18 FIX-80: 긴장 번호 묶음은 감사 기록으로
        ids = re.findall(r'<div class="ixrow" id="idx-([^"]+)"', self.index)
        for code in [f"F{i}" for i in range(1, 10)]:
            with self.subTest(code=code):
                self.assertIn(code, ids)
        # 번호는 본문에서 사라졌고 색인에는 `내부 표기` 로만 남는다.
        for num in ("P1", "P2", "P3", "P4", "G1", "G2", "G3", "G4"):
            with self.subTest(num=num):
                self.assertNotIn(num, ids)
                self.assertIn(f"<code>{num}</code>", self.index)
        for t in RULES.payload["open_tensions"]:
            self.assertNotIn(t["id"], ids)                                  # 2026-09-18 FIX-80 S3
        audit = (ROOT / "output" / f"{SLUG}-audit.md").read_text(encoding="utf-8")
        for t in RULES.payload["open_tensions"]:
            self.assertIn(f"| `{t['id']}` |", audit)

    def test_factor_and_parameter_names_come_from_the_rules(self):
        """**문구를 지어내지 않는다** — 규칙 파일에 있는 것을 그대로 쓴다."""
        for fid in rh.FACTOR_IDS:
            with self.subTest(fid=fid):
                row = self._row(fid)
                self.assertIn(RULES.factor(fid)["label"], row)
                # 2026-09-17 FIX-68 S3: `자동화 manual` 로 나가던 것을 한국어 이름으로 옮겼다.
                self.assertIn(rc.MODE_LABELS[RULES.factor(fid)["mode"]], row)
                self.assertNotIn(f"자동화 {RULES.factor(fid)['mode']}", row)
        params = RULES.payload["policies"]["f6"]["parameters"]
        for pid, spec in params.items():
            with self.subTest(pid=pid):
                row = self._row(rc.F6_PARAM_LABELS[pid], "param")   # 색인 행은 이름으로 선다
                self.assertIn(spec["label"], row)
                self.assertIn(spec["question"], row)
                self.assertIn(f"<code>{pid}</code>", row)     # 번호는 내부 표기로만
        p4 = RULES.payload["policies"]["f6"]["p4"]
        self.assertIn(p4["label"], self._row(rc.F6_P4_LABEL, "param"))
        self.assertIn(p4["question"], self._row(rc.F6_P4_LABEL, "param"))

    def test_gate_names_come_from_the_method_line(self):
        """규칙 파일에 게이트 이름 키가 **없어서** ⑨ 설명 줄에서 읽는다. 그 줄은 바꾸지 않는다."""
        f9 = RULES.payload["policies"]["f9"]
        self.assertEqual([k for k in f9 if re.fullmatch(r"g[1-4]_(label|name|title)", k)], [])
        # 2026-09-17 FIX-67: 이름은 render_common.F9_GATE_LABELS 가 들고, 설명은 관문 줄에서 읽는다.
        lines = rc.method_lines(self.ctx, self.results)
        docs = rh._gate_docs(self.ctx, self.results)
        self.assertEqual([d[0] for d in docs], ["G1", "G2", "G3", "G4"])
        self.assertEqual([d[1] for d in docs], list(rc.F9_GATE_LABELS.values()))
        for code, name, note in docs:
            with self.subTest(code=code):
                self.assertTrue(note, f"{code} 설명이 비었다")
                self.assertTrue(any(note in x for x in lines))   # 문장에서 그대로 떼 왔다
                self.assertIn(f"<code>{code}</code>", self._row(name, "gate"))

    def test_body_codes_link_into_the_index_without_burying_the_text(self):
        links = re.findall(r'<a class="tcode(?: first)?" href="#idx-([^"]+)">', self.html)
        self.assertTrue(links)
        # 앵커가 전부 실재한다.
        for code in set(links):
            with self.subTest(code=code):
                self.assertIn(f'id="idx-{code}"', self.index)
        # 본문에 F 201 · G 111 · P 152 회가 나오지만 링크는 그보다 훨씬 적어야 한다.
        # 2026-09-17 FIX-67: P·G 는 본문에서 사라졌다. 남은 코드는 factor 와 긴장이다.
        text = re.sub(r"<[^>]+>", " ", self.html.split("</style>", 1)[1])
        raw = len(re.findall(r"(?<![.\w가-힣])F[1-9](?![\w.-])", text))
        self.assertGreater(raw, 20)      # 2026-09-18 FIX-80: 긴장 번호·코드 경로가 빠져 원래 수가 줄었다. 요지는 링크 < 원래 수
        self.assertLess(len(links), raw)

    def test_first_mention_shows_the_name_only_where_it_is_missing(self):
        named = re.findall(r'<a class="tcode first" href="#idx-([^"]+)">[^<]*<span class="tname">([^<]+)</span>',
                           self.html)
        # 2026-09-17 FIX-67: P·G 는 이름으로 바뀌어 링크 대상에서 빠졌다. 이름을 붙이는 자리는
        # Factor 표의 `점수를 만드는 방식` 칸뿐이다 — 영어 값을 내부 표기로 달고 한국어를 앞세운다.
        codes = {c for c, _n in named}
        self.assertEqual(codes, {rh._anchor_id(rc.MODE_LABELS[m]) for m in rh.MODE_DOC
                                 if any(RULES.factor(f)["mode"] == m for f in rh.FACTOR_IDS)})
        for _code, name in named:
            self.assertIn(name, set(rc.MODE_LABELS.values()))

    def test_work_codes_and_judgment_ids_are_not_linked(self):
        """`F5-IMPL-48`(작업 코드)과 `alphabet.F9`(판단 id)는 factor 코드가 아니다."""
        self.assertNotIn('<a class="tcode" href="#idx-F5">F5</a>-IMPL', self.html)
        # 2026-09-17 FIX-77: 작업 코드는 본문에서 내려 감사 기록으로 갔다. 링크로 잘못 잇지 않는다는
        # 사실은 아래 두 줄이 계속 지킨다.
        self.assertNotIn("F5-IMPL-48", re.sub(r"<[^>]+>", "", self.html))
        self.assertNotRegex(self.html, r'\.<a class="tcode[^"]*" href="#idx-F\d">')

    # ---------------------------------------------------------------- S2 상태·근거
    def test_status_and_basis_are_shown_as_two_things(self):
        """붙여 쓰면 `승계 manual` 이 한 단어로 읽혔다."""
        self.assertIn('<span class="k">상태</span>', self.html)
        self.assertIn('<span class="k">근거</span>', self.html)
        self.assertIn('<span class="sep">|</span>', self.html)
        self.assertEqual(self.html.count('<span class="fst">'), 14 * 9)

    def test_carried_is_marked_as_the_weakest_basis(self):
        # 2026-09-17 FIX-68 S3: 근거 값도 한국어로 옮겼다. `carried` 는 이름 자체가 근거의 약함을 말한다.
        mark = f'<span class="b weak">{rc.BASIS_LABELS["carried"]}</span>'
        self.assertIn(mark, self.html)
        n = sum(1 for c in self.results["companies"] for f in rh.FACTOR_IDS
                if c["factors"][f]["basis"] == "carried")
        self.assertEqual(self.html.count(mark), n)
        self.assertEqual(n, 16)
        row = self._row(rc.BASIS_LABELS["carried"], "basis")
        self.assertIn("근거가 가장 약한 칸이다", row)
        # 2026-09-18 FIX-80 S3: 코드 위치는 읽는 사람의 정보가 아니라 색인에서 뺐다.
        self.assertNotIn("calc_qual.py", row)

    def test_every_basis_in_use_is_documented_with_its_source(self):
        used = {c["factors"][f]["basis"] for c in self.results["companies"] for f in rh.FACTOR_IDS}
        self.assertEqual(used, {"computed", "manual", "carried", "grade", "matrix", "criteria"})
        for basis in used:
            with self.subTest(basis=basis):
                row = self._row(rc.BASIS_LABELS.get(basis, basis), "basis")
                self.assertIn(rh.BASIS_DOC[basis][0], row)
                self.assertIn(f"<code>{basis}</code>", row)     # 영어 값은 내부 표기로만
                self.assertNotRegex(row, r"calc_\w+\.py:\d+")   # 2026-09-18 FIX-80 S3: 코드 위치는 색인에서 뺐다

    def test_statuses_in_use_are_documented(self):
        used = {c["factors"][f]["status"] for c in self.results["companies"] for f in rh.FACTOR_IDS}
        for status in used:
            with self.subTest(status=status):
                self.assertIn(STATUS_LABEL[status], self._row(status, "status"))

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
        # 2026-09-18 FIX-79 S2: 사전을 감사 기록으로 옮겼다. 원문 요약은 거기 그대로 있고, 본문은 그 뜻을
        # 번호 없이 **문장 안에서** 말한다.
        audit = (ROOT / "output" / f"{SLUG}-audit.md").read_text(encoding="utf-8")
        self.assertIn(c17["summary"], audit)
        plain = re.sub(r"<[^>]+>", "", self.html)
        self.assertIn("셋을 따로 기록하라는 권고가 있지만 이번 실행은 값이 같아 한 번만 적는다", plain)
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

    def _row(self, code: str, group: str = "") -> str:
        # 2026-09-17 FIX-68: `조합표`·`사람 판단` 처럼 방식과 근거가 같은 이름을 쓴다 — 묶음으로 가른다.
        prefix = f"idx-{group}" if group else r"idx(?:-\w+)?"
        m = re.search(rf'<div class="ixrow" id="{prefix}-{re.escape(rh._anchor_id(code))}">(.*?)</div>\s*(?=<div class="ixrow"|</div>)',
                      self.index, re.S)
        self.assertIsNotNone(m, f"색인에 {code} 행이 없다")
        return m.group(1)


if __name__ == "__main__":
    unittest.main()
