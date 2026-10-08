# 규칙 v2.0 테스트: v1.9 대비 차이(① 락인 사다리·② 세대 격차 시간·③ 지표 단계·⑦ kind·rejudge 정책·C-30·긴장 정리)와 ① 사다리 계산을 잠근다
from __future__ import annotations

import copy
import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard.calc_qual import compute_f1, compute_manual  # noqa: E402
from scorecard.engine import compute_company, recompute_matches  # noqa: E402
from scorecard.inputs import JudgmentLookup, ObsLookup  # noqa: E402
from scorecard.rules import RULES_DIR, RuleSet, load_rules  # noqa: E402

V19_SHA256 = "0e4122094968754392e7be606f133378a86305598230d49fea40a55506dc602d"
RESOLVED_BY_V20 = {"TEN-RC-02", "TEN-RC3-03", "TEN-RC4-02"}
RECHECKER_PREFIX = "2026-10 v2.0 재실행의 판단자. 정기 실행은 정성 판단 전부를 다시 매긴다(rules.md 2.9) — "


def rules(name: str) -> dict:
    return json.loads((ROOT / "scorecard" / "rules" / f"{name}.json").read_text(encoding="utf-8"))


def company(cid: str = "acme", ctype: str = "업무") -> dict:
    return {"company_id": cid, "display_name": cid.title(), "aliases": [], "type": ctype, "listed": True, "ticker": "ACME",
            "exchange": "NASDAQ", "share_basis": "common", "adr_ratio": None, "reporting_currency": "USD", "scope": "test"}


def lockin(status: str = "new", **inputs) -> dict:
    base = {"channel_consumer": "no", "channel_work": "yes", "channel_trade": "no",
            "loop": "fail", "switching": "fail", "substitutes": "pass", "pricing": "unknown",
            "durability_discount": "no", "ai_monetized_in_channel": "unknown"}
    base.update(inputs)
    return {"judgment_id": "acme.F1", "company_id": "acme", "factor": "F1", "kind": "lockin", "score": None,
            "inputs": base, "evidence": ["시험"], "reviewer": "tester", "reviewed_at": "2026-10-08", "status": status,
            "carried_from": "run:prior" if status == "carried" else None}


class DiffTest(unittest.TestCase):
    """v1.9 와 v2.0 의 차이가 선언한 자리에만 있다."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.v19, cls.v20 = rules("v1.9"), rules("v2.0")

    def test_top_level_differs_only_where_declared(self):
        self.assertEqual(set(self.v19), set(self.v20))
        changed = {k for k in self.v20 if self.v20[k] != self.v19[k]}
        self.assertEqual(changed, {"rule_version", "note", "factors", "policies", "decisions", "open_tensions"})
        self.assertEqual(self.v20["rule_version"], "v2.0")
        self.assertTrue(self.v20["note"].startswith(self.v19["note"] + " | v2.0: "))

    def test_factors_f4_f5_f6_f8_f9_untouched(self):
        for fid in ("F4", "F5", "F6", "F8", "F9"):
            with self.subTest(factor=fid):
                self.assertEqual(self.v20["factors"][fid], self.v19["factors"][fid])

    def test_f1_is_lockin_ladder(self):
        f1, old = self.v20["factors"]["F1"], self.v19["factors"]["F1"]
        self.assertEqual(set(f1) - set(old), {"channels", "display_only_inputs", "double_count_rule", "durability_discount",
                                              "judgment_kinds", "ladder", "questions"})
        self.assertEqual(set(old) - set(f1), {"component_only_cap"})
        self.assertEqual(f1["label"], "① 락인과 가격결정력")
        self.assertEqual((f1["mode"], f1["judgment_kinds"], f1["range"]), ("lockin", ["lockin"], [0, 5]))
        ladder = f1["ladder"]
        self.assertEqual(ladder["strength_of"], ["loop", "switching"])
        self.assertEqual(ladder["base_by_strength"], {"pass": 4, "partial": 3, "fail": 1})
        self.assertEqual(ladder["pricing_step"], {"pass": 1, "fail": -1, "partial": 0, "unknown": 0})
        self.assertEqual(ladder["substitutes_step"], {"fail": -1, "pass": 0, "partial": 0, "unknown": 0})
        self.assertEqual((ladder["durability_discount_step"], ladder["pricing_pass_requires_quarters"]), (-1, 8))
        self.assertEqual(f1["channels"]["keys"], ["channel_consumer", "channel_work", "channel_trade"])
        self.assertEqual(f1["channels"]["none_score"], 0)
        self.assertEqual(f1["display_only_inputs"]["ai_monetized_in_channel"]["values"], ["yes", "partial", "no", "unknown"])

    def test_f2_adds_three_keys_and_note(self):
        f2, old = self.v20["factors"]["F2"], self.v19["factors"]["F2"]
        self.assertEqual(set(f2) - set(old), {"generation_gap_months", "judgment_kinds", "leap_requires_independent_measurement"})
        self.assertEqual(set(old) - set(f2), set())
        self.assertEqual({k for k in old if old[k] != f2[k]}, {"note"})
        self.assertEqual(f2["judgment_kinds"], ["paths"])
        self.assertEqual((f2["generation_gap_months"]["default"], f2["generation_gap_months"]["by_company_type"]), (6, {"부품": 12}))
        self.assertEqual(f2["leap_requires_independent_measurement"]["input"], "leap_independent")

    def test_f3_adds_acceleration_tiers_only(self):
        f3, old = self.v20["factors"]["F3"], self.v19["factors"]["F3"]
        self.assertEqual({k: v for k, v in f3.items() if k != "acceleration_tiers"}, old)
        tiers = f3["acceleration_tiers"]["tiers"]
        self.assertEqual({t: tiers[t]["max"] for t in tiers}, {"a": "pass", "b": "pass", "c": "partial", "d": "pass", "e": "unknown"})
        self.assertEqual(f3["acceleration_tiers"]["growth_rates_required"], 2)

    def test_f7_adds_judgment_kinds_only(self):
        f7, old = self.v20["factors"]["F7"], self.v19["factors"]["F7"]
        self.assertEqual({k: v for k, v in f7.items() if k != "judgment_kinds"}, old)
        self.assertEqual(f7["judgment_kinds"], ["matrix"])

    def test_policies_add_rejudge_only(self):
        p19, p20 = self.v19["policies"], self.v20["policies"]
        self.assertEqual({k: v for k, v in p20.items() if k != "rejudge"}, p19)
        rj = p20["rejudge"]
        self.assertEqual(rj["qualitative_factors"], ["F1", "F2", "F3", "F4", "F5", "F7", "F8"])
        for key in ("regular_run_rejudges_all", "carried_allowed_only_in_extend_runs", "reviewed_at_after_prior_as_of",
                    "review_carried_exception_only_in_extend_runs"):
            self.assertIs(rj[key], True, key)

    def test_decisions_append_c30(self):
        self.assertEqual(self.v20["decisions"][:-1], self.v19["decisions"])
        c30 = self.v20["decisions"][-1]
        self.assertEqual((c30["id"], c30["status"], c30["chosen"]), ("C-30", "resolved", "rejudge_all_and_structure_f1"))
        self.assertIn(c30["chosen"], c30["choices"])

    def test_open_tensions_three_resolved_rest_recheck_now(self):
        old = {t["id"]: t for t in self.v19["open_tensions"]}
        self.assertEqual([t["id"] for t in self.v20["open_tensions"]], list(old))
        for t in self.v20["open_tensions"]:
            o = old[t["id"]]
            with self.subTest(tension=t["id"]):
                if t["id"] in RESOLVED_BY_V20:
                    self.assertEqual((o["status"], t["status"], t["resolved_at"]), ("open", "resolved", "2026-10-08"))
                    self.assertEqual(set(t) - set(o), {"resolution", "resolved_at", "what_remains"})
                    self.assertEqual({k for k in o if o[k] != t[k]}, {"status"})
                elif o["status"] == "open":
                    self.assertEqual((o["recheck_at"], t["recheck_at"], t["status"]), ("2026-11", "2026-10", "open"))
                    self.assertEqual(t["rechecker"], RECHECKER_PREFIX + o["rechecker"])
                    self.assertEqual({k for k in set(o) | set(t) if o.get(k) != t.get(k)}, {"recheck_at", "rechecker"})
                else:
                    self.assertEqual(t, o)   # v1.9 에서 이미 닫힌 긴장은 그대로다

    def test_v19_untouched(self):
        digest = hashlib.sha256((RULES_DIR / "v1.9.json").read_bytes()).hexdigest()
        self.assertEqual(digest, V19_SHA256)

    def test_v20_loads(self):
        r = load_rules("v2.0")
        self.assertEqual(r.version, "v2.0")


class LockinLadderTest(unittest.TestCase):
    """① 사다리 A: 강도(회수 루프·전환비용 중 높은 쪽) 4/3/1, 가격 실측 ±1, 대체 공급 −1, 지속성 할인 −1, 0~5 로 자른다."""

    RULES = load_rules("v2.0")

    def f1(self, judgment: dict, ctype: str = "업무", rules: RuleSet | None = None) -> dict:
        return compute_f1(company(ctype=ctype), JudgmentLookup([judgment]), rules or self.RULES)

    def test_pass_with_pricing_pass_is_five(self):
        r = self.f1(lockin(loop="pass", pricing="pass", pricing_sustained_quarters=8))
        self.assertEqual((r["score"], r["status"], r["basis"]), (5, "ok", "lockin"))
        self.assertEqual(r["calc"]["steps"], {"base": 4, "pricing": 1, "substitutes": 0, "durability_discount": 0})
        self.assertEqual((r["calc"]["strength"], r["calc"]["strength_from"], r["calc"]["raw"]), ("pass", ["loop"], 5))

    def test_partial_is_three_and_fail_is_one(self):
        self.assertEqual(self.f1(lockin(loop="partial", switching="fail"))["score"], 3)
        self.assertEqual(self.f1(lockin(loop="fail", switching="fail"))["score"], 1)

    def test_stronger_of_loop_and_switching(self):
        r = self.f1(lockin(loop="partial", switching="pass"))
        self.assertEqual((r["score"], r["calc"]["strength"], r["calc"]["strength_from"]), (4, "pass", ["switching"]))

    def test_no_channel_is_zero_without_adjustments(self):
        r = self.f1(lockin(channel_work="no", loop="pass", pricing="pass", pricing_sustained_quarters=12,
                           substitutes="fail", durability_discount="yes"))
        self.assertEqual((r["score"], r["status"]), (0, "ok"))
        self.assertTrue(r["calc"]["no_channel"])
        self.assertEqual(r["calc"]["steps"], {"base": 0})

    def test_both_unknown_needs_judgment(self):
        r = self.f1(lockin(loop="unknown", switching="unknown", pricing="pass", pricing_sustained_quarters=8))
        self.assertEqual((r["score"], r["status"]), (None, "needs_judgment"))
        self.assertIn("둘 다 미확인", r["pending"]["message"])

    def test_one_unknown_uses_the_known_side(self):
        r = self.f1(lockin(loop="unknown", switching="partial"))
        self.assertEqual((r["score"], r["calc"]["strength"], r["calc"]["strength_from"]), (3, "partial", ["switching"]))

    def test_pricing_fail_substitutes_fail_and_discount_each_minus_one(self):
        self.assertEqual(self.f1(lockin(loop="pass", pricing="fail"))["score"], 3)
        self.assertEqual(self.f1(lockin(loop="pass", substitutes="fail"))["score"], 3)
        self.assertEqual(self.f1(lockin(loop="pass", durability_discount="yes"))["score"], 3)
        # 미확인은 실패가 아니다 — 보정 0
        self.assertEqual(self.f1(lockin(loop="pass", substitutes="unknown", durability_discount="unknown"))["score"], 4)

    def test_floor_is_zero(self):
        r = self.f1(lockin(pricing="fail", substitutes="fail", durability_discount="yes"))
        self.assertEqual((r["calc"]["raw"], r["score"]), (-2, 0))
        self.assertTrue(any("범위" in w for w in r["warnings"]))

    def test_ceiling_is_five(self):
        payload = copy.deepcopy(self.RULES.payload)
        payload["factors"]["F1"]["ladder"]["base_by_strength"]["pass"] = 5
        bigger = RuleSet(payload, RULES_DIR / "v2.0.json")
        r = self.f1(lockin(loop="pass", pricing="pass", pricing_sustained_quarters=8), rules=bigger)
        self.assertEqual((r["calc"]["raw"], r["score"]), (6, 5))

    def test_pricing_pass_below_quarters_counts_as_partial(self):
        r = self.f1(lockin(loop="pass", pricing="pass", pricing_sustained_quarters=4))
        self.assertEqual((r["score"], r["calc"]["pricing_used"], r["calc"]["steps"]["pricing"]), (4, "partial", 0))
        self.assertTrue(any("8분기" in w for w in r["warnings"]))
        r = self.f1(lockin(loop="pass", pricing="pass"))   # 분기 수 없음도 부분
        self.assertEqual(r["score"], 4)

    def test_ai_monetized_is_display_only(self):
        a = self.f1(lockin(loop="pass", ai_monetized_in_channel="yes"))
        b = self.f1(lockin(loop="pass", ai_monetized_in_channel="no"))
        self.assertEqual(a["score"], b["score"])
        self.assertEqual((a["calc"]["ai_monetized_in_channel"], b["calc"]["ai_monetized_in_channel"]), ("yes", "no"))

    def test_component_type_has_no_cap(self):
        """부품 채널 일괄 상한은 없다. 칩·파운드리도 업무 채널의 네 질문으로 잰다."""
        r = self.f1(lockin(loop="pass", pricing="pass", pricing_sustained_quarters=8), ctype="부품")
        self.assertEqual(r["score"], 5)

    def test_carried_score_kind_needs_judgment(self):
        j = {**lockin(status="carried"), "kind": "score", "score": 3, "inputs": {}}
        r = self.f1(j)
        self.assertEqual((r["score"], r["status"]), (None, "needs_judgment"))
        self.assertIn("이어받은 점수는 쓰지 않는다", r["pending"]["message"])

    def test_carried_lockin_is_carried_score(self):
        r = self.f1(lockin(status="carried", loop="partial"))
        self.assertEqual((r["score"], r["status"]), (3, "carried_score"))

    def test_missing_judgment(self):
        r = compute_f1(company(), JudgmentLookup([]), self.RULES)
        self.assertEqual((r["status"], r["basis"]), ("needs_judgment", "lockin"))


class EngineDispatchTest(unittest.TestCase):
    def test_v20_uses_lockin_and_v19_uses_manual(self):
        j = lockin(loop="partial")
        for version, basis in (("v2.0", "lockin"), ("v1.9", "manual")):
            with self.subTest(version=version):
                out = compute_company(company(), ObsLookup([]), JudgmentLookup([j]), load_rules(version),
                                      {"run_id": "t", "rule_version": version, "decisions": []})
                self.assertEqual(out["F1"]["basis"], basis)

    def test_manual_without_component_cap_key_does_not_crash(self):
        """규칙에 component_only_cap 이 없으면 상한을 대지 않는다(전에는 무조건 읽어 KeyError)."""
        j = {**lockin(), "kind": "score", "score": 4, "inputs": {}}
        r = compute_manual("F1", company(ctype="부품"), JudgmentLookup([j]), load_rules("v2.0"))
        self.assertEqual((r["score"], r["status"]), (4, "ok"))
        r = compute_manual("F1", company(ctype="부품"), JudgmentLookup([j]), load_rules("v1.9"))
        self.assertEqual(r["status"], "error")   # v1.9 는 부품 상한 2 그대로


class RecomputeTest(unittest.TestCase):
    """승인된 실행은 v1.9 이하라 v2.0 코드가 결과를 바꾸지 않는다."""

    def test_approved_runs_unchanged(self):
        for slug in ("ai-scorecard-2026-09-obsreg", "ai-scorecard-2026-10-test", "ai-scorecard-2026-10-rescore"):
            with self.subTest(slug=slug):
                ok, stored, fresh = recompute_matches(slug)
                self.assertTrue(ok, f"{slug}: {stored} != {fresh}")


if __name__ == "__main__":
    unittest.main()
