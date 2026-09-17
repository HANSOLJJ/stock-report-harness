# FIX-74 — 사람 판단과 기계 계산의 경계를 `judgments.json` 의 kind 에서 읽는다는 것을 고정한다
from __future__ import annotations

import json
import sys
import unittest
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard import render_common as rc  # noqa: E402
from scorecard import render_html as rh  # noqa: E402
from scorecard.engine import load_context  # noqa: E402

SLUG = "ai-scorecard-2026-09-obsreg"
RUN_DIR = ROOT / "scorecard" / "runs" / SLUG
HTML = ROOT / "output" / f"{SLUG}.html"

TOTALS = {"alphabet": 15, "amazon": 15, "meta": 15, "microsoft": 14, "tsmc": 10, "anthropic": 10,
          "spacex-xai": 9, "nvidia": 9, "apple": 8, "alibaba": 7, "palantir": 6, "tesla": 5,
          "openai": 4, "oracle": 2}


class Fix74Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.ctx = load_context(SLUG)
        cls.results = json.loads((RUN_DIR / "results.json").read_text(encoding="utf-8"))
        cls.lines = rc.method_lines(cls.ctx)
        cls.html = HTML.read_text(encoding="utf-8")

    def line(self, needle: str) -> str:
        return next(x for x in self.lines if needle in x)

    def sec(self, fid: str) -> str:
        """2026-09-17 FIX-75: 문장이 항목별로 갈려 이름 접두사가 빠졌다. 절에서 찾는다."""
        return " ".join(next(ls for f, ls in rc.method_sections(self.ctx) if f == fid))

    # ---------------------------------------------------------------- 사실 확인
    def test_seven_factors_are_all_human_judgment(self):
        """사용자 지적의 근거다 — ①~⑤·⑦·⑧ 은 14개사 전부가 사람 판단을 입력으로 갖는다."""
        by_factor: dict[str, Counter] = defaultdict(Counter)
        for j in self.ctx.judgments:
            by_factor[j["factor"]][j["kind"]] += 1
        for fid in ("F1", "F2", "F3", "F4", "F5", "F7", "F8"):
            with self.subTest(factor=fid):
                self.assertEqual(sum(by_factor[fid].values()), 14)
        # ⑨ 는 사람 판단과 관측이 섞이고, ⑥ 만 판단이 14건에 못 미친다.
        self.assertEqual(by_factor["F9"], Counter({"gate_inputs": 14}))
        self.assertLess(sum(by_factor["F6"].values()), 14)

    def test_f6_judgments_exist_but_are_not_used(self):
        """⑥ 은 판단 기록에 비상장 둘의 점수가 남아 있어도 이번 규칙이 관측에서 다시 계산한다."""
        f6 = [j for j in self.ctx.judgments if j["factor"] == "F6"]
        self.assertEqual({j["company_id"] for j in f6}, {"anthropic", "openai"})
        self.assertTrue(all(j["kind"] == "score" and j["score"] is not None for j in f6))
        self.assertEqual(self.ctx.rules.f6_mode, "parameters")
        # 그런데 결과의 근거는 14건 모두 계산이고, 무시했다는 경고가 남는다.
        basis = Counter(c["factors"]["F6"]["basis"] for c in self.results["companies"])
        self.assertEqual(basis, Counter({"computed": 14}))
        warned = [w for c in self.results["companies"] if c["company_id"] in ("anthropic", "openai")
                  for w in (c["factors"]["F6"].get("warnings") or []) if "무시함" in w]
        self.assertEqual(len(warned), 2)

    # ---------------------------------------------------------------- 문장
    def test_the_sentence_names_every_judged_factor_not_just_three(self):
        head = self.line("사람 판단에서 나온다")
        for name in ("① 네트워크", "② 게임체인저", "③ Last Mover", "④ 호황 이후", "⑤ 아군",
                     "⑦ 순환금융", "⑧ 비대칭 의존"):
            with self.subTest(name=name):
                self.assertIn(name, head)
        self.assertNotIn("⑥ 가격", head)
        self.assertIn("판단을 대신하는 것이 아니다", head)
        # 경고가 셋이 아니라 일곱 전부에 걸린다.
        self.assertIn("이 항목들은 모두 점수보다 근거 문장을 읽어야 한다", head)

    def test_the_engine_side_is_still_written(self):
        """사다리·산식·조합표가 어떻게 환산하는지는 지우지 않았다."""
        self.assertIn("사다리에 태워 칸을 고른다", self.sec("F3"))
        self.assertIn("기본 3점에 동맹을 더하고 적대를 뺀다", self.sec("F5"))
        self.assertIn("그 조합을 표에서 찾아 칸을 고른다", self.sec("F7"))
        # 그리고 그 입력이 사람 판단이라는 사실이 앞에 선다.
        for fid in ("F3", "F5", "F7"):
            with self.subTest(factor=fid):
                self.assertIn("사람이 **", self.sec(fid))

    def test_judgment_inputs_never_leak_internal_keys(self):
        """이름표에 없는 입력 키를 그대로 내보내면 내부 코드가 화면에 실린다(FIX-73 과 같은 종류)."""
        for fid in ("F3", "F5", "F7", "F9"):
            with self.subTest(factor=fid):
                for name in rc.judgment_input_names(self.ctx, fid):
                    self.assertIn(name, set(rc.JUDGMENT_INPUT_NAMES.values()))
        # ⑤ 의 A·H 처럼 이름표에 없는 것은 조용히 빠진다 — 키가 새어 나가지 않는다.
        self.assertEqual(rc.judgment_input_names(self.ctx, "F5"), [])
        self.assertNotIn("door_closed", self.sec("F3"))

    def test_f7_carried_two_are_named(self):
        """⑦ 열둘은 두 축 판정이고 둘은 숫자만 넘어왔다 — 그 갈림이 문장에 있다."""
        line = self.sec("F7")
        self.assertIn("두 곳은 그 판정이 남아 있지 않아", line)
        self.assertIn("점수 숫자만 넘어왔고", line)
        kinds = Counter(j["kind"] for j in self.ctx.judgments if j["factor"] == "F7")
        self.assertEqual(kinds, Counter({"matrix": 12, "score": 2}))

    def test_f6_is_the_only_measured_factor(self):
        line = self.line("이 항목 하나뿐이다")
        self.assertIn("사람이 판단을 적지 않는 것은", line)
        self.assertIn("이번 규칙은 그 점수를 쓰지 않고 관측에서 다시 계산한다", line)

    def test_f9_lists_its_human_inputs_read_from_judgments(self):
        line = self.line("관측 수치만으로 나오지 않는다")
        keys = {k for j in self.ctx.judgments if j["kind"] == "gate_inputs" for k in j["inputs"]}
        self.assertTrue(keys <= set(rc.JUDGMENT_INPUT_NAMES), f"이름표에 없는 키: {keys - set(rc.JUDGMENT_INPUT_NAMES)}")
        for key in keys:
            with self.subTest(key=key):
                self.assertIn(rc.JUDGMENT_INPUT_NAMES[key], line)

    def test_the_lists_are_read_not_hardcoded(self):
        """판단 기록이 바뀌면 문장도 따라 바뀐다 — 항목 이름을 문장에 박지 않았다."""
        import copy

        ctx = copy.deepcopy(self.ctx)
        ctx.judgments = [j for j in ctx.judgments if j["factor"] != "F3"]
        head = next(x for x in rc.method_lines(ctx) if "사람 판단에서 나온다" in x)
        self.assertNotIn("③ Last Mover", head)
        self.assertIn("① 네트워크", head)

    # ---------------------------------------------------------------- 색인
    def test_the_index_no_longer_says_only_manual_is_judgment(self):
        self.assertIn("아래 네 방식도 사람 판단을 입력으로 받는다", rh.MODE_DOC["manual"][1])
        for mode in ("ladder", "formula", "matrix", "paths"):
            with self.subTest(mode=mode):
                self.assertIn("사람", rh.MODE_DOC[mode][1])
        # ⑥ 만 사람 판단이 들어가지 않는다는 사실이 방식 색인에도 있다.
        self.assertIn("사람 판단이 들어가지 않는", rh.MODE_DOC["parameters"][1])
        self.assertIn("재무 수치와 사람 판정이 함께 들어간다", rh.MODE_DOC["gates"][1])

    def test_the_basis_index_separates_f6_from_f9(self):
        doc = rh.BASIS_DOC["computed"][1]
        self.assertIn("⑥ 는 넣는 값이 전부 등록된 관측이지만 ⑨ 는 다르다", doc)
        for basis in ("criteria", "grade", "matrix"):
            with self.subTest(basis=basis):
                self.assertIn("사람", rh.BASIS_DOC[basis][1])

    def test_the_built_html_carries_it(self):
        for needle in ("일곱 항목은 모두 사람 판단에서 나온다", "판단을 대신하는 것이 아니다",
                       "관측 수치만으로 나오지 않는다", "이 항목 하나뿐이다"):
            with self.subTest(needle=needle):
                self.assertIn(needle, self.html)
        self.assertNotIn("셋은 사람이 직접 매긴다", self.html)

    # ---------------------------------------------------------------- 점수 불변
    def test_scores_unchanged(self):
        self.assertEqual({c["company_id"]: c["total"] for c in self.results["companies"]}, TOTALS)
        self.assertEqual(self.results["results_hash"],
                         "4a3f6c05b206ef81f370ac7765a1a948fe1e9cf6d1999c142bac4f124e04910b")


if __name__ == "__main__":
    unittest.main()
