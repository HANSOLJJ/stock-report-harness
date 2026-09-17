# FIX-58 2단계 — 7차 리뷰 A 분담 반영(부재 주장의 검색 범위를 상대방 제출본까지)을 고정한다
from __future__ import annotations

import html
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard import render_common as rc  # noqa: E402
from scorecard.engine import load_context  # noqa: E402
from scorecard.rules import load_rules  # noqa: E402

RULES = load_rules("v1.7")
SLUG = "ai-scorecard-2026-09-obsreg"
RUN_DIR = ROOT / "scorecard" / "runs" / SLUG
PRIV = ("fcf_ttm", "cash", "net_cash", "debt_ebitda", "operating_margin_ttm")


def load(name: str) -> dict:
    return json.loads((RUN_DIR / name).read_text(encoding="utf-8"))


def preserved_text(ref: str) -> str:
    """보존 원문을 `git show` 로 읽어 태그를 걷는다 — 작업 트리 사본이 아니라 커밋된 사본을 본다."""
    raw = subprocess.run(["git", "-C", str(ROOT), "show", ref], capture_output=True, check=True).stdout
    t = html.unescape(re.sub(r"<[^>]+>", " ", raw.decode("utf-8", "replace")))
    return re.sub(r"\s+", " ", t)


class Stage2Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.o = {x["observation_id"]: x for x in load("observations.json")["items"]}
        cls.j = {x["judgment_id"]: x for x in load("judgments.json")["items"]}
        cls.results = load("results.json")
        cls.res = {c["company_id"]: c for c in cls.results["companies"]}
        cls.run_json = load("run.json")
        cls.ctx = load_context(SLUG)

    def test_totals_unchanged(self):
        self.assertEqual({c: r["total"] for c, r in self.res.items()},
                         {"alphabet": 15, "amazon": 15, "meta": 15, "microsoft": 14, "tsmc": 10, "anthropic": 10,
                          "spacex-xai": 9, "nvidia": 9, "apple": 8, "alibaba": 7, "palantir": 6, "tesla": 5,
                          "openai": 2, "oracle": 2})

    # ---------------------------------------------------------------- S1 amazon 계약 수입
    def test_amazon_carried_row_no_longer_asserts_non_disclosure(self):
        o = self.o["amazon.contracted_revenue.v15"]
        self.assertEqual((o["status"], o["missing_type"]), ("not_disclosed", "unverified"))
        self.assertIsNone(o["value"])
        self.assertEqual(o["raw"], "AWS 백로그(수백 $B급) — 숫자 미공시")          # v1.5 원문은 고치지 않는다
        lc = o["basis"]["label_correction"]
        self.assertEqual(lc["was"]["status"], "parse_failed")
        self.assertIn("496 billion", lc["why"])
        # 대체 관측이 실제로 숫자를 들고 있고 엔진이 그것을 읽는다.
        self.assertEqual(self.o["amazon.contracted_revenue.obsreg25"]["value"], 496000000000.0)
        g4 = next(p for p in self.res["amazon"]["factors"]["F9"]["calc"]["path"] if p["gate"] == "G4")
        self.assertEqual((g4["contracted_revenue"], g4["step"]), (496000000000.0, 0))

    # ---------------------------------------------------------------- S2 상대방 제출본
    def test_amazon_10q_discloses_the_anthropic_facility(self):
        t = preserved_text("3cf9799:validation/offb-24/_raw/amzn-20260630.htm")
        self.assertIn("aggregate facility not to exceed $ 20.0 billion", t)
        self.assertIn("At inception, there is no amount available to be drawn against", t)
        self.assertIn("reduced the amount available under the facility to $ 15.0 billion", t)
        credit = next(a for a in self.run_json["assumptions"] if "확정 미인출 여신(FIX-54 S2)" in a)
        self.assertIn("회사 자체 발표에 없을 뿐 상대방 제출본에는 있다", credit)
        for frag in ("no amount available to be drawn against", "convertible notes",
                     "30 months after an Anthropic liquidity event", "C-20 경로라 G3"):
            self.assertIn(frag, credit)
        # 등록하지 않았다.
        self.assertEqual([x for x in self.o if x.startswith("anthropic.undrawn_credit")], [])

    def test_counterparty_sweep_recorded_on_every_absence_claim(self):
        sweep = self.o["anthropic.fcf_ttm.priv31"]["basis"]["checked_scope"]["counterparty_filings"]
        for cid in ("anthropic", "openai"):
            for metric in PRIV:
                with self.subTest(oid=f"{cid}.{metric}"):
                    self.assertEqual(self.o[f"{cid}.{metric}.priv31"]["basis"]["checked_scope"]["counterparty_filings"], sweep)
        self.assertEqual(sweep["hits"]["amzn-20260630.htm"], {"Anthropic": 31, "OpenAI": 15})
        self.assertFalse(any(f["registered"] for f in sweep["found"]))       # 어느 것도 등록하지 않았다
        self.assertIn("상대방 제출본에도 없다", sweep["not_found"])
        self.assertIn("Alphabet·Microsoft 제출본이 보존돼 있지 않다", sweep["gap"])
        self.assertTrue(any("상대방 제출본까지 넓혀" in a for a in self.run_json["assumptions"]))

    def test_sweep_counts_are_reproducible_from_the_preserved_filings(self):
        sweep = self.o["openai.cash.priv31"]["basis"]["checked_scope"]["counterparty_filings"]
        refs = {"amzn-20260630.htm": "3cf9799:validation/offb-24/_raw/amzn-20260630.htm",
                "spcx-20260630.htm": "3cf9799:validation/offb-24/_raw/spcx-20260630.htm"}
        for name, ref in refs.items():
            t = preserved_text(ref)
            with self.subTest(name=name):
                for who, n in sweep["hits"][name].items():
                    self.assertEqual(len(re.findall(re.escape(who), t, re.I)), n)

    def test_fourth_compute_supplier_recorded_without_changing_the_value(self):
        b = self.o["anthropic.offbalance_B.v15"]["basis"]
        self.assertIn("$1.25 billion per month through May 2029", b["fourth_supplier_not_counted"])
        self.assertIn("무조건 약정이 아니다", b["fourth_supplier_not_counted"])
        self.assertEqual(self.o["anthropic.offbalance_B.v15"]["value"], 300000000000.0)   # 값 불변
        t = preserved_text("3cf9799:validation/offb-24/_raw/spcx_s1a_20260603.htm")
        self.assertIn("Cloud Services Agreements with Anthropic PBC", t)
        self.assertIn("$1.25 billion per month through May 2029", t)
        self.assertIn("terminated by either party upon 90 days", t)
        f8 = self.j["anthropic.F8.f8anth33"]
        self.assertTrue(any("네 번째 외부 공급자" in e for e in f8["evidence"]))
        self.assertEqual(self.res["anthropic"]["factors"]["F8"]["score"], -3)

    # ---------------------------------------------------------------- S3 openai 1차 출처
    def test_openai_primary_source_link_explains_the_asymmetry(self):
        link = self.o["openai.arr_prior.priv31"]["basis"]["primary_source_link"]
        self.assertEqual(self.o["openai.arr_prior.priv31"]["source_id"], "SRC-v15-md")
        self.assertEqual(link["related_primary_source"], "SRC-OPENAI-FUNDING-2026")
        self.assertIn("그대로 적은 문장이 없다", link["why_not_moved"])
        self.assertIn("$2B in revenue per month", link["what_it_says"])
        self.assertIn("둘 다 사실이 아니다", link["absence_claim_that_was_wrong"])
        # anthropic 쪽은 값이 그대로 인용돼 옮겼다 — 두 처리의 차이가 근거로 남는다.
        self.assertEqual(self.o["anthropic.arr_prior.priv31"]["source_id"], "SRC-ANTHROPIC-SERIESH-2026")
        # 이번 실행은 그 틀린 부재 주장을 **근거로** 쓰지 않는다 — 파일 이름이 나오는 곳은 틀렸다고 적는 이 한 자리뿐이다.
        where = [oid for oid, o in self.o.items() if "external_reporting_raw" in json.dumps(o, ensure_ascii=False)]
        self.assertEqual(where, ["openai.arr_prior.priv31"])
        for name in ("judgments.json", "run.json"):
            self.assertNotIn("external_reporting_raw", (RUN_DIR / name).read_text(encoding="utf-8"))

    # ---------------------------------------------------------------- S4 anthropic.F8
    def test_f8_records_that_its_blocking_evidence_is_unverifiable(self):
        f8 = self.j["anthropic.F8.f8anth33"]
        head = f8["evidence"][0]
        self.assertIn("이 하향 차단의 근거를 확인할 수 없다", head)
        self.assertIn("TEN-RA5-01", head)
        self.assertIn("다음 수집 **1순위**", head)
        self.assertEqual(self.res["anthropic"]["factors"]["F8"]["score"], -3)     # 하향하지 않는다
        t = {x["id"]: x for x in RULES.payload["open_tensions"]}["TEN-RA5-01"]
        self.assertEqual((t["judgment_ids"], t["recheck_at"], t["status"]), (["anthropic.F8"], "2026-11", "open"))
        self.assertEqual(t["third_party_recheck"], "committed")
        self.assertIn("알파벳 제출본", t["trigger"])
        self.assertIn("하향 가능(-3 → -4)", t["direction"])
        self.assertIn("RA5-01", t["review_finding"])
        head_line = next(x for x in rc.conflict_lines(self.ctx) if "제3자 재검토 약속" in x)
        self.assertIn("TEN-RA5-01(anthropic.F8, 2026-11)", head_line)

    def test_alphabet_filings_are_really_absent_from_the_repo(self):
        """긴장의 전제를 저장소에서 직접 확인한다 — 보존됐는데 못 찾은 것이 아니다."""
        names = subprocess.run(["git", "-C", str(ROOT), "log", "--all", "--diff-filter=A",
                                "--name-only", "--format="], capture_output=True, check=True).stdout.decode("utf-8", "replace")
        preserved = {x for x in names.splitlines() if "/_raw/" in x and x.endswith((".htm", ".html"))}
        self.assertTrue(any("amzn-20260630" in x for x in preserved))
        self.assertFalse(any(re.search(r"googl|goog-", x, re.I) for x in preserved))

    # ---------------------------------------------------------------- S5 검색 범위·문면
    def test_oracle_sweep_wording_is_scoped_to_the_regex(self):
        why = self.o["oracle.undrawn_credit.fix54"]["basis"]["broad_tag_sweep"]
        self.assertIn("그 정규식 기준 0건", why)
        self.assertIn("us-gaap:LineOfCredit", why)
        self.assertIn("결론은 그대로다", why)
        facts = json.loads((ROOT / "validation" / "f6-avail-15" / "_raw" / "ORCL.companyfacts.json").read_text(encoding="utf-8"))["facts"]
        rows = [r for tax, tags in facts.items() if "LineOfCredit" in tags
                for unit, rs in tags["LineOfCredit"]["units"].items() for r in rs]
        self.assertEqual([(r["end"], r["val"]) for r in rows], [("2011-03-14", 0)])
        self.assertEqual(self.res["oracle"]["factors"]["F9"]["score"], -3)

    def test_palantir_offbalance_search_widened_to_three_tags(self):
        why = self.o["palantir.offbalance_note.v15"]["basis"]["label_correction"]["why"]
        self.assertIn("LesseeOperatingLeaseLiabilityUndiscountedExcessAmount", why)
        self.assertIn("63,201천", why)
        self.assertIn("내재이자(할인차금)", why)
        self.assertIn("결론 `미확인` 은 그대로다", why)
        self.assertTrue(self.o["palantir.offbalance_note.v15"]["value"].startswith("미확인"))

    def test_apple_retracted_assertion_is_struck(self):
        ws = self.o["apple.lease_liabilities.nc37"]["basis"]["why_superseded"]
        self.assertTrue(ws.startswith("~~"))
        self.assertIn("(superseded", ws)
        self.assertIn("발행사가 분기에는 공시하지 않는다", ws)               # 지우지 않고 남긴다
        pal = self.o["palantir.lease_liabilities.nc37"]["basis"]["why_superseded"]
        self.assertTrue(pal.startswith("~~"))                                # 둘이 같은 형태다

    def test_run_records_the_author_conflict(self):
        line = next(a for a in self.run_json["assumptions"] if "작성자 이해상충" in a)
        self.assertIn("Anthropic 이 만든 Claude 가 작성", line)
        self.assertIn("채점규칙 384행", line)
        for tid in ("TEN-RC-02", "TEN-RC3-01", "TEN-RA4-01", "TEN-RA5-01"):
            self.assertIn(tid, line)

    def test_spacex_f7_carries_the_counter_direction_fact(self):
        f7 = self.j["spacex-xai.F7"]
        # 2026-09-17 FIX-59 S3: 같은 계약이라는 단정을 철회하고 Valor 리스를 문면에 넣었다 — 보존 사실이 근거란에
        # 남는다는 이 검사의 뜻은 그대로다.
        add = next(e for e in f7["evidence"] if "Anthropic 클라우드 계약이 있다" in e)
        self.assertIn("Cloud Services Agreements with Anthropic PBC", add)
        self.assertIn("were immaterial", add)
        self.assertIn("$295M", add)
        self.assertIn("동일성을 보존 원문이 주지 않는다", add)
        self.assertIn("Valor Equity Partners", add)
        t = preserved_text("3cf9799:validation/offb-24/_raw/spcx-20260630.htm")
        self.assertIn("Other transactions with Tesla and other related parties", t)
        self.assertIn("were immaterial", t)
        self.assertEqual(self.res["spacex-xai"]["factors"]["F7"]["score"], 0)


if __name__ == "__main__":
    unittest.main()
