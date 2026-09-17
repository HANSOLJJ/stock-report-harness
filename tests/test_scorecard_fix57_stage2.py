# FIX-57 2단계 — 6차 리뷰 A 분담 반영(긴장 등록 범위 · 생성 코드 · 결측 라벨과 그 요건)을 고정한다
from __future__ import annotations

import copy
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
from scorecard.schema import SchemaError, validate_observations, validate_rules  # noqa: E402
from scorecard.stages import load_baseline  # noqa: E402

RULES = load_rules("v1.7")
SLUG = "ai-scorecard-2026-09-obsreg"
RUN_DIR = ROOT / "scorecard" / "runs" / SLUG
SRC = ROOT / "scripts" / "scorecard"


def load(name: str) -> dict:
    return json.loads((RUN_DIR / name).read_text(encoding="utf-8"))


class Stage2Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.o = {x["observation_id"]: x for x in load("observations.json")["items"]}
        cls.j = {x["judgment_id"]: x for x in load("judgments.json")["items"]}
        cls.results = load("results.json")
        cls.res = {c["company_id"]: c for c in cls.results["companies"]}
        cls.run_json = load("run.json")
        cls.ctx = load_context(SLUG)
        base, _obs, triggers = load_baseline(cls.ctx.run["baseline_id"])
        cls.md = render_draft(cls.ctx, cls.results, base, triggers)
        cls.registry = {c["company_id"]: c for c in json.loads(
            (ROOT / "scorecard" / "companies.json").read_text(encoding="utf-8"))["companies"]}

    def test_totals_unchanged(self):
        self.assertEqual({c: r["total"] for c, r in self.res.items()},
                         {"alphabet": 15, "amazon": 15, "meta": 15, "microsoft": 14, "tsmc": 10, "anthropic": 10,
                          "spacex-xai": 9, "nvidia": 9, "apple": 8, "alibaba": 7, "palantir": 6, "tesla": 5,
                          "openai": 4, "oracle": 2})

    # ---------------------------------------------------------------- S1 긴장 등록 범위
    def test_every_judgment_with_the_harness_mark_is_registered_in_a_tension(self):
        """근거란 표기만으로는 AGENTS.md 승계 예외가 서지 않는다 — 표기한 판단이 전부 긴장에 있어야 한다."""
        marked = {jid for jid, j in self.j.items() if any("하네스 미표기" in e for e in j["evidence"])}
        self.assertEqual(marked, {"anthropic.F2", "meta.F2", "alibaba.F2", "openai.F2"})
        registered = {jid for t in RULES.payload["open_tensions"] for jid in t["judgment_ids"]}
        self.assertEqual(marked - registered, set())
        t = {x["id"]: x for x in RULES.payload["open_tensions"]}["TEN-RA4-01"]
        self.assertEqual(sorted(t["judgment_ids"]), ["alibaba.F2", "anthropic.F2", "meta.F2", "openai.F2"])
        self.assertEqual(t["recheck_at"], "2026-11")
        self.assertIn("하네스", t["subject"])

    def test_recheck_owner_differs_between_anthropic_and_the_rest(self):
        t = {x["id"]: x for x in RULES.payload["open_tensions"]}["TEN-RA4-01"]
        self.assertEqual(t["third_party_recheck"], "partial")
        self.assertEqual(t["third_party_scope"], ["anthropic.F2"])
        self.assertIn("나머지 셋은 그 제약이 필요 없다", t["rechecker"])
        affected = {a["judgment_id"]: a for a in t["affected"]}
        self.assertEqual(sorted(affected), ["alibaba.F2", "meta.F2", "openai.F2"])
        for jid in affected:
            self.assertIn("채점규칙 22행", affected[jid]["source_lines"])
        # 표시도 그 사실을 따른다.
        partial = next(x for x in rc.conflict_lines(self.ctx) if "일부만 확정" in x)
        self.assertIn("TEN-RA4-01(anthropic.F2, 2026-11)", partial)

    def test_f2_scores_unchanged(self):
        for cid, want in (("anthropic", 5), ("meta", 4), ("alibaba", 4), ("openai", 4)):
            with self.subTest(cid=cid):
                self.assertEqual(self.res[cid]["factors"]["F2"]["score"], want)

    # ---------------------------------------------------------------- S2 생성 코드
    def test_new_run_would_create_the_handover_source(self):
        code = (SRC / "stages.py").read_text(encoding="utf-8")
        self.assertIn("SRC_HANDOVER", code)
        self.assertIn("HANDOVER 75행", code)
        from scorecard.baseline_import import SRC_HANDOVER, SRC_HANDOVER_SHA256
        registered = {s["source_id"]: s for s in self.ctx.sources["items"]}
        self.assertEqual(registered[SRC_HANDOVER]["sha256"], SRC_HANDOVER_SHA256)
        cited = {sid for j in self.j.values() for sid in j["source_ids"]}
        self.assertIn(SRC_HANDOVER, cited)                     # 인용하는 판단이 실제로 있다

    def test_every_baseline_source_is_in_the_generation_code(self):
        """생성 코드에 없는 기준선 출처가 남아 있지 않은지 전수로 본다."""
        code = (SRC / "stages.py").read_text(encoding="utf-8")
        consts = dict(re.findall(r'^(SRC_[A-Z]+)\s*=\s*"([^"]+)"',
                                 (SRC / "baseline_import.py").read_text(encoding="utf-8"), re.M))
        generated = {consts[g] for g in re.findall(r'"source_id": (SRC_[A-Z]+)', code) if g in consts}
        baseline_sources = {s["source_id"] for s in self.ctx.sources["items"] if s["source_id"].startswith("SRC-v15-")}
        self.assertEqual(baseline_sources, {"SRC-v15-html", "SRC-v15-md", "SRC-v15-rule", "SRC-v15-handover"})
        self.assertEqual(baseline_sources - generated, set())
        # 나머지는 실행 중 수집한 출처라 init 이 미리 만들 대상이 아니다.
        run_sources = {s["source_id"] for s in self.ctx.sources["items"]} - baseline_sources
        self.assertTrue(all(s.startswith(("SRC-SEC-", "SRC-ANTHROPIC-", "SRC-OPENAI-")) for s in run_sources))

    # ---------------------------------------------------------------- S3 비상장 계약 수입 라벨
    def test_private_contracted_revenue_is_an_absence_not_an_arr(self):
        for cid, arr in (("anthropic", 65000000000.0), ("openai", 40000000000.0)):
            with self.subTest(cid=cid):
                o = self.o[f"{cid}.contracted_revenue.v15"]
                self.assertIsNone(o["value"])
                self.assertEqual((o["status"], o["missing_type"]), ("not_disclosed", "not_disclosed_confirmed"))
                moved = o["basis"]["value_moved"]
                self.assertEqual(moved["was"]["value"], arr)
                self.assertEqual(self.o[moved["same_value_lives_in"]]["value"], arr)   # 값은 ARR 칸에 그대로
                self.assertEqual(self.o[moved["same_value_lives_in"]]["metric"], "arr")
                self.assertIn("RPO", o["basis"]["checked_scope"]["preserved_release"])
                # C-07 판정은 다른 곳이 담는다.
                self.assertEqual(self.j[f"{cid}.F9"]["inputs"]["coverage_comparable"], "no")
                self.assertEqual(self.o[f"{cid}.offbalance_B.v15"]["status"], "incompatible_basis")

    def test_private_g4_route_is_unchanged(self):
        """라벨을 고쳐도 C-16 한 칸 강등에 닿지 않는다 — 점수가 그대로인 이유."""
        ant = self.res["anthropic"]["factors"]["F9"]
        g4 = next(p for p in ant["calc"]["path"] if p["gate"] == "G4")
        self.assertEqual(g4["result"], "incompatible")
        self.assertIn("no_extra_penalty_because", g4)
        self.assertNotIn("step", g4)
        self.assertEqual(ant["score"], -2)
        # 2026-09-17 FIX-62: openai 가 C-20 비상장 경로로 옮겨 가 anthropic 과 같은 네 게이트를 밟는다.
        oai = self.res["openai"]["factors"]["F9"]
        self.assertEqual([p["gate"] for p in oai["calc"]["path"]], ["G1", "G2", "G3", "G4"])
        self.assertEqual(oai["score"], -2)
        oai_g4 = next(p for p in oai["calc"]["path"] if p["gate"] == "G4")
        self.assertEqual(oai_g4["result"], "incompatible")
        self.assertNotIn("step", oai_g4)
        self.assertTrue(any("C-16 한 칸 강등에 닿지 않는다" in a for a in self.run_json["assumptions"]))

    # ---------------------------------------------------------------- S4 결측 요건 · 낡은 이유 · 표시
    def test_not_disclosed_confirmed_requirement_lives_in_the_rules(self):
        pol = RULES.payload["policies"]["missing_types"]["not_disclosed_confirmed"]
        self.assertEqual(sorted(pol["routes"]), ["issuer_declared", "structural"])
        self.assertEqual(pol["routes"]["structural"]["applies_to"], "unlisted")
        self.assertIn("contracted_revenue", pol["routes"]["structural"]["metrics"])
        self.assertEqual(pol["routes"]["issuer_declared"]["required_basis_keys"], ["statement", "location"])
        self.assertIn("unverified", pol["otherwise"])
        # 선언이 실제로 읽힌다 — 11건이 두 경로 중 하나를 채운다.
        labeled = [o for o in self.o.values() if o.get("missing_type") == "not_disclosed_confirmed"]
        self.assertEqual(len(labeled), 13)
        for o in labeled:
            with self.subTest(oid=o["observation_id"]):
                listed = self.registry[o["company_id"]]["listed"]
                structural = (not listed) and o["metric"] in pol["routes"]["structural"]["metrics"]
                declared = all((o["basis"] or {}).get(k) for k in pol["routes"]["issuer_declared"]["required_basis_keys"])
                self.assertTrue(structural or declared)
        ali = self.o["alibaba.contracted_revenue.obsreg25"]
        self.assertTrue(self.registry["alibaba"]["listed"])
        self.assertIn("발행사 선언 경로", ali["basis"]["label_route"])

    def test_schema_rejects_a_label_that_fills_neither_route(self):
        doc = copy.deepcopy(load("observations.json"))
        bad = next(x for x in doc["items"] if x["observation_id"] == "alibaba.contracted_revenue.obsreg25")
        del bad["basis"]["statement"]                                  # 상장사인데 발행사 선언이 없다
        policy = RULES.payload["policies"]["missing_types"]
        with self.assertRaises(SchemaError):
            validate_observations(doc, self.registry, SLUG, missing_policy=policy)
        # 정책을 안 넘기면 예전처럼 통과한다 — 검사는 선언이 있을 때만 걸린다.
        validate_observations(doc, self.registry, SLUG)

    def test_schema_rejects_a_malformed_missing_types_policy(self):
        bad = copy.deepcopy(RULES.payload)
        del bad["policies"]["missing_types"]["not_disclosed_confirmed"]["routes"]["issuer_declared"]
        with self.assertRaises(SchemaError):
            validate_rules(bad)

    def test_spacex_basis_mismatch_reason_is_current(self):
        for metric in ("operating_income_ttm", "net_income_ttm"):
            with self.subTest(metric=metric):
                note = self.o[f"spacex-xai.{metric}.f6reg28"]["basis"]["basis_mismatch_note"]
                self.assertIn("C-24 가 그 트랙에 P2 를 넣었다", note)
                self.assertIn("기준이 섞여 계산되는 자리는 여전히 없다", note)
        # 결론이 실제로 서는지 결과에서 본다 — P2 는 손익을 읽지 않고 P1 은 트랙에 없다.
        calc = self.res["spacex-xai"]["factors"]["F6"]["calc"]
        self.assertEqual(sorted(calc["parameters"]), ["P2", "P3"])
        self.assertEqual(sorted(calc["parameters"]["P2"]["inputs"]),
                         ["input_alternatives_used", "market_cap", "net_cash", "revenue_ttm"])
        self.assertFalse(calc["parameters_not_in_track"]["P1"]["would_compute"])
        self.assertIsNone(calc["p4"]["nonop_share"])

    def test_overview_conflict_notice_leads_with_the_run_level_fact(self):
        line = next(x for x in self.md.splitlines() if x.startswith("- **이해상충 고지"))
        self.assertIn("채점 대상에 Anthropic 이 포함되고", line)
        self.assertIn("References 의 각 출처 줄에 있고", line)
        self.assertNotIn(" / ", line)                                  # 출처별 문구를 이어 붙이지 않는다
        flagged = [s for s in self.ctx.sources["items"] if s.get("conflict_of_interest")]
        self.assertIn(f"출처 {len(flagged)}건", line)
        for s in flagged:                                              # 개별 문구는 References 에 그대로 있다
            self.assertIn(s["conflict_of_interest"], self.md)


if __name__ == "__main__":
    unittest.main()
