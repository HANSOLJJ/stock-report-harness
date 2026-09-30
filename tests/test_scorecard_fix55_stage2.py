# FIX-55 2단계 — 4차 리뷰 A 분담 반영(tesla 여신 · 보도자료 출처 · anthropic.F2 긴장 · 결측 서술)을 고정한다
from __future__ import annotations

import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard import render_common as rc  # noqa: E402
from scorecard.engine import load_context  # noqa: E402
from scorecard.render_md import render_draft  # noqa: E402
from scorecard.rules import load_rules  # noqa: E402
from scorecard.stages import load_baseline  # noqa: E402

RULES = load_rules("v1.7")
SLUG = "ai-scorecard-2026-09-obsreg"
RUN_DIR = ROOT / "output" / SLUG
RAW = ROOT / "validation" / "f6-avail-15" / "_raw"
CREDIT_TAG_RE = re.compile(r"Unused|Undrawn|RemainingBorrowingCapacity|LineOfCreditFacility", re.I)


def load(name: str) -> dict:
    return json.loads((RUN_DIR / name).read_text(encoding="utf-8"))


class Stage2Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.o = {x["observation_id"]: x for x in load("observations.json")["items"]}
        cls.j = {x["judgment_id"]: x for x in load("judgments.json")["items"]}
        cls.results = load("results.json")
        cls.res = {c["company_id"]: c for c in cls.results["companies"]}
        cls.src = {s["source_id"]: s for s in load("sources.json")["items"]}
        cls.run_json = load("run.json")
        ctx = load_context(SLUG)
        base, _obs, triggers = load_baseline(ctx.run["baseline_id"])
        cls.ctx = ctx
        cls.md = render_draft(ctx, cls.results, base, triggers)

    def test_totals_unchanged(self):
        # 2026-09-16 FIX-56 1단계: spacex-xai 11 → 9 (C-24 로 listed_newly 트랙이 P2 를 계산 — F6 -1 → -3). 다른 13개사는 불변이다.
        self.assertEqual({c: r["total"] for c, r in self.res.items()},
                         {"alphabet": 15, "amazon": 15, "meta": 15, "microsoft": 14, "spacex-xai": 9, "tsmc": 10, "anthropic": 10,
                          "nvidia": 9, "apple": 8, "alibaba": 7, "palantir": 6, "tesla": 5, "openai": 4, "oracle": 2})

    # S1 tesla
    def test_tesla_credit_registered_without_score_change(self):
        o = self.o["tesla.undrawn_credit.fix55"]
        self.assertEqual((o["value"], o["status"], o["as_of"]), (5000000000.0, "verified", "2026-06-30"))
        self.assertEqual(o["basis"]["tag"], "DebtInstrumentUnusedBorrowingCapacityAmount")
        self.assertEqual(o["basis"]["accession"], "0001628280-26-049270")
        self.assertIn("태그 자체가 미인출액이다", o["basis"]["why_no_arithmetic"])
        self.assertIn("tesla.undrawn_credit.fix55", self.o["tesla.undrawn_credit.fix54"]["basis"]["superseded_by"]["by"])
        f9 = self.res["tesla"]["factors"]["F9"]
        self.assertEqual(f9["score"], -1)
        self.assertEqual([p["gate"] for p in f9["calc"]["path"]], ["G1", "G2"])      # G3 는 계산되지 않는다
        self.assertNotIn("tesla.undrawn_credit.fix55", f9["observation_ids"])
        self.assertIn("확정 미인출 여신 — Tesla $5.0B(tesla.undrawn_credit.fix55, 2026-06-30)", self.md)

    def test_broad_tag_sweep_finds_only_tesla(self):
        """고정 후보가 아니라 정규식으로 다시 훑는다 — 기준일 이후 값이 있는 회사는 tesla 하나다."""
        recent = {}
        for path in sorted(RAW.glob("*.companyfacts.json")):
            doc = json.loads(path.read_text(encoding="utf-8"))
            hits = [(tag, r) for _tax, tags in doc["facts"].items() for tag, node in tags.items() if CREDIT_TAG_RE.search(tag)
                    for _unit, rows in node["units"].items() for r in rows if not r.get("start") and r["end"] >= "2026-01-01"]
            if hits:
                recent[path.name.split(".")[0]] = hits
        self.assertEqual(sorted(recent), ["TSLA"])
        self.assertEqual({r["val"] for _tag, r in recent["TSLA"] if r["end"] == "2026-06-30"}, {5000000000})
        sweep = (ROOT / "validation" / "fix-55" / "credit-tag-sweep.md").read_text(encoding="utf-8")
        self.assertIn("| ORCL | 0 |", sweep)
        census = (ROOT / "validation" / "fix-54" / "undrawn-credit-census.md").read_text(encoding="utf-8")
        self.assertIn("[정정 2026-09-16 FIX-55 2단계]", census)
        self.assertIn("verified 5,000M", census)

    # S2 출처·긴장·한계
    def test_private_releases_registered_as_sources(self):
        for sid, host in (("SRC-ANTHROPIC-SERIESH-2026", "www.anthropic.com"), ("SRC-OPENAI-FUNDING-2026", "openai.com")):
            with self.subTest(sid=sid):
                s = self.src[sid]
                self.assertIsNone(s["url"])                       # host 가 원천 정책에 없어 url 을 넣지 않는다
                self.assertIn("회사 자체 발표다", s["conflict_of_interest"])
                self.assertIn("ffaf318:", s["note"])
                self.assertRegex(s["sha256"], r"^[0-9a-f]{64}$")
                entry = next(u for u in RULES.payload["sources"]["unlisted"] if u["host"] == host)
                self.assertEqual(entry["reason_type"], "terms")
        self.assertEqual(self.o["anthropic.arr_prior.priv31"]["source_id"], "SRC-ANTHROPIC-SERIESH-2026")
        self.assertIn("run-rate revenue crossed $47 billion", self.o["anthropic.arr_prior.priv31"]["basis"]["source_correction"]["quote"])
        for cid, sid in (("anthropic", "SRC-ANTHROPIC-SERIESH-2026"), ("openai", "SRC-OPENAI-FUNDING-2026")):
            for metric in ("fcf_ttm", "cash", "net_cash", "debt_ebitda", "operating_margin_ttm"):
                self.assertEqual(self.o[f"{cid}.{metric}.priv31"]["basis"]["checked_scope"]["preserved_release_source_id"], sid)
        self.assertIn("SRC-ANTHROPIC-SERIESH-2026", self.md)      # References 에 나온다

    def test_anthropic_f2_tension(self):
        t = {x["id"]: x for x in RULES.payload["open_tensions"]}["TEN-RA4-01"]
        # 2026-09-16 FIX-57 2단계: 같은 잣대를 댄 meta·alibaba·openai 의 F2 도 이 긴장에 들어왔다(judgment_ids 넷).
        # **anthropic.F2 가 등록돼 있고 시점·결정·방향이 그대로인지**가 이 검사의 뜻이라 그것을 본다.
        self.assertIn("anthropic.F2", t["judgment_ids"])
        self.assertEqual((t["recheck_at"], t["decision_id"]), ("2026-11", "C-03"))
        self.assertIn("5 → 4", t["direction"])
        self.assertIn("비 Claude 세션", t["rechecker"])
        self.assertIn("독립 기관", t["trigger"])
        j = self.j["anthropic.F2"]
        self.assertEqual((j["score"], j["status"]), (5, "carried"))
        self.assertIn("SRC-v15-rule", j["source_ids"])
        self.assertTrue(any("하네스 미표기" in e for e in j["evidence"]))
        self.assertIn("하네스 미표기", self.md)

    def test_limitations_carry_conflict_and_recheck(self):
        lines = rc.conflict_lines(self.ctx)
        self.assertTrue(any("이해상충" in x for x in lines))
        # 2026-09-16 FIX-57 2단계: TEN-RA4-01 의 judgment_ids 가 넷이 되고 비 Claude 재판정은 anthropic.F2 하나뿐이라
        # 갈래가 committed → partial 로 바뀌었다. **그 줄에 시점과 함께 나오는지**가 이 검사의 뜻이다.
        third = [x for x in lines if "제3자 재검토 약속" in x][0]
        self.assertIn("제3자 재검토 약속", third)
        partial = [x for x in lines if "일부만 확정" in x][0]
        # 2026-09-18 FIX-80 S3: 긴장은 번호 대신 제목과 시점으로 적는다. 번호는 감사 기록의 `다시 볼 것` 표에 있다.
        self.assertIn("어느 하네스로 잰 값인지 적지 않는다", partial)
        self.assertIn("2026-11 에 다시 본다", partial)
        self.assertNotIn("TEN-", partial)
        self.assertTrue(any("발동 조건" in x for x in lines))
        for line in lines:
            self.assertIn(line if line.startswith("  - ") else f"- {line}", self.md)

    # S3 서술
    def test_descriptions_fixed(self):
        self.assertTrue(self.o["palantir.offbalance_note.v15"]["value"].startswith("미확인"))
        self.assertIn("| Palantir |", self.md)
        self.assertIn("미확인 — v1.5 원표기 `없음`", self.md)
        self.assertIn("기간이 어긋난다", self.o["tsmc.undrawn_credit.fix54"]["basis"]["period_mismatch"])
        self.assertIn("신용장은 약정 여신이 아니다", self.o["tsmc.undrawn_credit.fix54"]["basis"]["next_collection_guide"])
        amzn = self.o["amazon.contracted_revenue.obsreg25"]
        self.assertEqual(amzn["raw"], "those commitments not yet recognized were approximately $496 billion (2026-06-30)")
        self.assertEqual(amzn["value"], 496000000000.0)
        self.assertIn("$2B in revenue per month", self.o["openai.cash.priv31"]["basis"]["checked_scope"]["preserved_release"])
        self.assertIn("이중 계산이 아니다", self.o["spacex-xai.undrawn_credit.fix54"]["basis"]["no_double_count_with_restricted_cash"])
        self.assertFalse(any("missing_type=not_disclosed_confirmed" in a for a in self.run_json["assumptions"]))
        self.assertTrue(any("missing_type=unverified" in a for a in self.run_json["assumptions"]))


if __name__ == "__main__":
    unittest.main()
