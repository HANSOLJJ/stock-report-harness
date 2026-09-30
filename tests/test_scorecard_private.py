# 비상장 F6(C-12)과 F9 G1 비상장 경로(C-20) 고정 테스트 (PRIV-IMPL-31)
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard.calc_f6 import compute_f6  # noqa: E402
from scorecard.calc_f9 import compute_f9  # noqa: E402
from scorecard.inputs import JudgmentLookup, ObsLookup  # noqa: E402
from scorecard.rules import load_rules  # noqa: E402
from scorecard.schema import SchemaError, validate_rules  # noqa: E402

RULES = load_rules("v1.7")
RUN_DIR = ROOT / "output" / "ai-scorecard-2026-09-obsreg"


def company(cid: str = "acme") -> dict:
    return {"company_id": cid, "display_name": cid.title(), "aliases": [], "type": "업무",
            "listed": False, "ticker": None, "exchange": None, "share_basis": "private",
            "adr_ratio": None, "reporting_currency": "USD", "scope": "test"}


def obs(metric: str, value, cid="acme", *, unit="USD", kind="actual", status="legacy_unverified",
        basis=None, missing_type=None) -> dict:
    item = {"observation_id": f"{cid}.{metric}.t", "company_id": cid, "metric": metric,
            "value": value, "unit": unit, "as_of": "2026-09-02", "kind": kind,
            "source_id": "SRC-t", "status": status, "period": None, "basis": basis,
            "raw": None, "note": None}
    if missing_type:
        item["missing_type"] = missing_type
    return item


def run(decisions=("C-12",)) -> dict:
    choice = {"C-12": "p2_with_capped_promotion", "C-20": "defer_to_private_g2",
              "C-06": "proposed_v15_boundaries", "C-05": "apply"}
    return {"run_id": "t", "as_of": "2026-09-02", "rule_version": "v1.7",
            "decisions": [{"id": d, "choice": choice[d], "rationale": "t",
                           "decided_by": "t", "decided_at": "2026-09-02"} for d in decisions]}


def f6obs(cid="acme", *, ps_ratio=30.0, arr=65e9, arr_prior=47e9, raised=125e9,
          valuation=965e9, estimate_range=None, arr_kind="run_rate") -> ObsLookup:
    """기본 arr_kind 는 실제 데이터와 같은 run_rate 다.

    FIX-52 S2 로 arr_growth 가 kind=actual 만 받게 되어 run_rate 로는 보정 장치가 돌지 않는다. 보정 **장치**
    자체를 보는 테스트는 arr_kind="actual" 을 넘긴다.
    """
    items = []
    if ps_ratio is not None:
        items.append(obs("ps_ratio", ps_ratio, cid, unit="ratio", kind="estimate",
                         basis={"estimate_range": estimate_range} if estimate_range else None))
    for metric, value, kind in (("arr", arr, arr_kind), ("arr_prior", arr_prior, arr_kind),
                                ("cumulative_raised", raised, "actual"),
                                ("post_money_valuation", valuation, "actual")):
        if value is not None:
            items.append(obs(metric, value, cid, kind=kind))
    return ObsLookup(items)


class TestPrivateBandsMatchV15(unittest.TestCase):
    """v1.5 비상장 구간표를 옮겨 적으며 바꾸지 않았는지 본다."""

    def test_band_mapping(self):
        for value, expected in ((14.8, -2), (19.9, -2), (20.0, -3), (29.9, -3),
                                (30.0, -4), (99.9, -4), (100.0, -5), (150.0, -5)):
            self.assertEqual(RULES.f6_private_band(value)[0], expected, f"{value}x")

    def test_no_zero_or_minus_one_band(self):
        """**비상장에는 0·-1 칸이 없다.** 원본 표가 그 두 칸을 '—' 로 비워 두었다."""
        scores = {b["score"] for b in RULES.f6_private_bands()["bands"]}
        self.assertEqual(scores, {-2, -3, -4, -5})
        self.assertEqual(RULES.f6_track("private")["ceiling"], -2)

    def test_input_is_ps_ratio_not_arr(self):
        """**분모는 arr 이 아니라 TTM 보정 매출이다.** 이것을 틀리면 비상장사가 부당하게 싸 보인다."""
        self.assertEqual(RULES.f6_private_bands()["input"], "ps_ratio")
        self.assertIn("TTM 보정", RULES.f6_private_bands()["input_note"])

    def test_boundary_rule_not_applied(self):
        self.assertIn("미적용", RULES.f6_private_bands()["boundary_rule"])


class TestPrivateCorrection(unittest.TestCase):
    """P2 가 점수를 내고 P3·P4 가 합쳐서 최대 한 칸 올린다."""

    def score(self, **kw):
        # 원래 이 헬퍼는 run_rate arr 로 보정 장치를 시험했다. FIX-52 S2 이후 run_rate 는 arr_growth 를 충족하지 못해
        # 장치가 돌지 않으므로 **장치 시험은 진짜 ARR(kind=actual) 로** 한다. run_rate 경로는 아래 두 테스트가 본다.
        kw.setdefault("arr_kind", "actual")
        return compute_f6(company(), f6obs(**kw), JudgmentLookup([]), RULES, run())

    def test_anthropic_shape_gets_one_step(self):
        """진짜 ARR 이면 anthropic 모양(성장 0.383 · 자본효율 0.52)은 한 칸 오른다."""
        r = self.score()
        self.assertEqual(r["calc"]["subtotal_before_correction"], -4)
        self.assertEqual(r["calc"]["correction"]["promotion_steps"], 1)
        self.assertEqual(r["score"], -3)

    def test_run_rate_arr_does_not_promote(self):
        """**FIX-52 S2 — 런레이트는 ARR 이 아니다.** 같은 숫자라도 kind=run_rate 면 arr_growth 불충족이다(사용자 결정)."""
        r = self.score(arr_kind="run_rate")
        row = r["calc"]["correction"]["conditions"]["arr_growth"]
        self.assertFalse(row["met"])
        self.assertTrue(row["value_met_threshold"])                 # 값은 임계를 넘었지만 kind 로 막힌다
        self.assertIn("kind 불인정", row["reason"])
        self.assertEqual(row["input_kinds"], {"arr": "run_rate", "arr_prior": "run_rate"})
        self.assertEqual(r["calc"]["correction"]["promotion_steps"], 0)
        self.assertEqual(r["score"], -4)

    def test_one_run_rate_input_is_enough_to_block(self):
        items = [obs("ps_ratio", 30.0, unit="ratio", kind="estimate"), obs("arr", 65e9, kind="actual"),
                 obs("arr_prior", 47e9, kind="run_rate"), obs("cumulative_raised", 125e9),
                 obs("post_money_valuation", 965e9)]
        r = compute_f6(company(), ObsLookup(items), JudgmentLookup([]), RULES, run())
        self.assertFalse(r["calc"]["correction"]["conditions"]["arr_growth"]["met"])

    def test_accepted_kinds_must_be_observation_kinds(self):
        payload = json.loads((ROOT / "scorecard" / "rules" / "v1.7.json").read_text(encoding="utf-8"))
        cond = {c["id"]: c for c in payload["policies"]["f6"]["private_correction"]["conditions"]}["arr_growth"]
        self.assertEqual(cond["accepted_kinds"], ["actual"])
        cond["accepted_kinds"] = ["arr"]                 # 지표 이름은 kind 가 아니다 — 충족 불가능한 선언
        with self.assertRaises(SchemaError):
            validate_rules(payload)

    def test_openai_shape_gets_none(self):
        """**성장률이 더 높은데도 보정이 없다.** 자본효율이 임계 미달이기 때문이다."""
        r = self.score(ps_ratio=39.0, arr=40e9, arr_prior=25e9, raised=185e9, valuation=852e9)
        corr = r["calc"]["correction"]
        self.assertAlmostEqual(corr["conditions"]["arr_growth"]["value"], 0.60, places=4)
        self.assertTrue(corr["conditions"]["arr_growth"]["met"])
        self.assertFalse(corr["conditions"]["capital_efficiency"]["met"])
        self.assertEqual(corr["promotion_steps"], 0)
        self.assertEqual(r["score"], -4)

    def test_one_condition_alone_is_not_enough(self):
        """require_all 이 아니면 openai 가 걸린다. 그 사실을 고정한다."""
        self.assertTrue(RULES.f6_private_correction()["require_all"])
        r = self.score(arr_prior=64e9)          # 성장률 1.6% — 자본효율만 충족
        self.assertTrue(r["calc"]["correction"]["conditions"]["capital_efficiency"]["met"])
        self.assertFalse(r["calc"]["correction"]["conditions"]["arr_growth"]["met"])
        self.assertEqual(r["calc"]["correction"]["promotion_steps"], 0)

    def test_cap_is_one_step(self):
        """조건이 둘 다 크게 넘어도 한 칸이다."""
        r = self.score(arr=200e9, arr_prior=20e9, raised=100e9)
        self.assertEqual(r["calc"]["correction"]["promotion_steps"], 1)

    def test_ceiling_clamps(self):
        """~20x 에 보정이 붙어도 -2 를 넘지 않는다."""
        r = self.score(ps_ratio=10.0, arr=200e9, arr_prior=20e9, raised=100e9)
        self.assertEqual(r["calc"]["subtotal_before_correction"], -2)
        self.assertEqual(r["score"], -2)
        self.assertTrue(r["calc"]["ceiling_applied"])

    def test_missing_correction_inputs_do_not_promote(self):
        """입력이 없으면 보정을 만들지 않는다. 조용히 올리지 않는다."""
        r = self.score(arr_prior=None)
        self.assertIsNone(r["calc"]["correction"]["conditions"]["arr_growth"]["met"])
        self.assertEqual(r["calc"]["correction"]["promotion_steps"], 0)
        self.assertEqual(r["score"], -4)

    def test_capital_efficiency_threshold_straddle(self):
        """**Series H 모순이 이 임계를 가로지른다.**

        원본 안에서 Series H 가 $30B·$65B 로 갈리고, 그것이 cumulative_raised 를 통해
        자본효율을 0.41~0.72 로 벌린다. 임계 0.50 이 그 구간 안에 있어 **한 시나리오에서만
        보정이 사라진다.** 그때 anthropic F6 가 -3 이 아니라 -4 다.
        """
        self.assertEqual(self.score(raised=90e9)["score"], -3)     # Series H 30B 가정
        self.assertEqual(self.score(raised=125e9)["score"], -3)    # 원본 표기
        self.assertEqual(self.score(raised=160e9)["score"], -4)    # Series H 65B 가정


class TestPrivateP2Guards(unittest.TestCase):
    def test_missing_ps_ratio_pends_and_does_not_fall_back_to_arr(self):
        r = compute_f6(company(), f6obs(ps_ratio=None), JudgmentLookup([]), RULES, run())
        self.assertEqual(r["status"], "pending_data")
        self.assertIn("arr 로 대체하지 않는다", r["pending"]["message"])

    def test_estimate_range_within_one_band_is_used(self):
        # 보정까지 포함한 점수를 본다 — FIX-52 S2 이후 보정은 진짜 ARR 에서만 붙으므로 arr_kind="actual".
        r = compute_f6(company(), f6obs(estimate_range=[30.0, 39.0], arr_kind="actual"), JudgmentLookup([]), RULES, run())
        rng = r["calc"]["parameters"]["P2"]["estimate_range"]
        self.assertFalse(rng["spans_bands"])
        self.assertEqual(r["score"], -3)

    def test_estimate_range_spanning_bands_is_held(self):
        """**범위가 밴드를 가르면 값을 고르지 않는다.**"""
        r = compute_f6(company(), f6obs(ps_ratio=25.0, estimate_range=[25.0, 35.0]),
                       JudgmentLookup([]), RULES, run())
        self.assertEqual(r["status"], "pending_data")
        self.assertTrue(r["calc"]["parameters"]["P2"]["estimate_range"]["spans_bands"])
        self.assertIn("값을 고르지 않는다", r["pending"]["message"])

    def test_undecided_c12_still_pends(self):
        """밴드 선언이 없으면 예전처럼 점수를 만들지 않는다."""
        payload = json.loads((ROOT / "scorecard" / "rules" / "v1.7.json").read_text(encoding="utf-8"))
        payload["policies"]["f6"]["private_bands"] = None
        from scorecard.rules import RuleSet
        r = compute_f6(company(), f6obs(), JudgmentLookup([]),
                       RuleSet(payload, ROOT / "scorecard" / "rules" / "v1.7.json"), run())
        self.assertEqual(r["status"], "needs_rule_decision")
        self.assertEqual(r["pending"]["decision_id"], "C-12")


class TestC12WeaknessIsRecorded(unittest.TestCase):
    """**답을 먼저 알고 보정 방향을 정했다**는 사실이 규칙 파일에 남아 있어야 한다."""

    def test_weakness_required_by_schema(self):
        payload = json.loads((ROOT / "scorecard" / "rules" / "v1.7.json").read_text(encoding="utf-8"))
        validate_rules(payload)
        payload["policies"]["f6"]["private_correction"]["weakness"] = ""
        with self.assertRaises(SchemaError):
            validate_rules(payload)

    def test_threshold_source_required(self):
        payload = json.loads((ROOT / "scorecard" / "rules" / "v1.7.json").read_text(encoding="utf-8"))
        payload["policies"]["f6"]["private_correction"]["conditions"][0]["threshold_source"] = ""
        with self.assertRaises(SchemaError):
            validate_rules(payload)

    def test_weakness_names_the_coincidence(self):
        w = RULES.f6_private_correction()["weakness"]
        self.assertIn("v1.5 발표 점수", w)
        self.assertIn("답을 먼저 알고", w)


class TestC20PrivateRoute(unittest.TestCase):
    """비상장 + TTM 영업손익 구조적 미공시 → G1 판정 보류 후 G2 비상장 경로."""

    def f9(self, *, missing_type="not_disclosed_confirmed", listed=False, decisions=("C-20", "C-06", "C-05")):
        items = [obs("operating_margin_ttm", None, unit="ratio", kind="derived",
                     status="not_disclosed", missing_type=missing_type),
                 obs("fcf_ttm", None, status="not_disclosed",
                     missing_type="not_disclosed_confirmed")]
        c = company()
        c["listed"] = listed
        jud = JudgmentLookup([{"judgment_id": "acme.F9", "company_id": "acme", "factor": "F9",
                               "kind": "gate_inputs", "score": None, "status": "new",
                               "reviewer": "t", "reviewed_at": "2026-09-02", "evidence": ["t"],
                               "inputs": {"fcf_trend": "unknown", "bep_retreat": "no",
                                          "buffer_erosion": "no", "direction_A": "unknown",
                                          "direction_B": "unknown", "coverage_comparable": "unknown",
                                          "operating_result_reviewed": "unknown"}}])
        return compute_f9(c, ObsLookup(items), jud, RULES, run(decisions))

    def test_deferred_then_private_g2(self):
        r = self.f9()
        first = r["calc"]["path"][0]
        self.assertEqual(first["result"], "undetermined")
        self.assertNotEqual(first["result"], "pass")
        self.assertIn("통과 아님", first["reason"])
        self.assertEqual(first["decision_id"], "C-20")
        self.assertEqual(r["score"], -2)
        self.assertEqual(r["status"], "ok")

    def test_path_records_g3_skip_and_no_extra_g4_penalty(self):
        """G4 에서 또 깎지 않는다는 것이 경로에 남아야 한다.

        원래 이 테스트는 `dedupe` 키의 존재만 봤다. 그 키가 지키려던 것은 **G2 에서 깎은 것을 G4 에서
        또 깎지 않는다**는 것이고 그 뜻은 지금도 유효하다. 문제는 그 키에 붙어 있던 문구가 **G4 가
        막힌 사유까지 G2 와 같다고 단정**한 것이었다 — G2 는 회사가 공시하지 않은 것이고 G4 는 우리가
        같은 범위 자료를 못 구한 것이라 다를 수 있다. 오늘 세운 missing_type 구분과 같은 자리다.
        """
        gates = {p["gate"]: p for p in self.f9()["calc"]["path"]}
        self.assertEqual(gates["G3"]["result"], "skipped")
        g4 = gates["G4"]
        self.assertIn("no_extra_penalty_because", g4)
        self.assertEqual(g4["g2_reason"], "fcf_not_disclosed(확인된 미공시)")

    def test_g4_reason_is_not_conflated_with_g2(self):
        """**두 사유가 다르면 다르다고 적어야 한다.** 여기서 G4 는 coverage_comparable 미확인이다."""
        g4 = {p["gate"]: p for p in self.f9()["calc"]["path"]}["G4"]
        self.assertFalse(g4["g4_reason_same_as_g2"])
        self.assertIn("coverage_comparable", g4["reason"])
        self.assertIn("다른 사유", g4["note"])

    def test_label_is_required_not_just_absence(self):
        """**자료가 없다는 것만으로는 부족하다.** 구조적 미공시 라벨이 있어야 한다."""
        r = self.f9(missing_type=None)
        self.assertEqual(r["status"], "pending_data")
        self.assertEqual(r["calc"]["path"][0]["result"], "pending")

    def test_listed_company_never_takes_this_route(self):
        r = self.f9(listed=True)
        self.assertEqual(r["status"], "pending_data")

    def test_requires_the_decision(self):
        """C-20 을 선택하지 않은 실행은 예전 동작 그대로다."""
        r = self.f9(decisions=("C-06", "C-05"))
        self.assertEqual(r["status"], "pending_data")


class TestRunIsComplete(unittest.TestCase):
    """새 실행이 14/14 완주하고 미결 결정이 없다."""

    def setUp(self):
        self.results = json.loads((RUN_DIR / "results.json").read_text(encoding="utf-8"))

    def test_all_fourteen_scored(self):
        self.assertEqual(self.results["population"]["scored"], 14)
        self.assertEqual(self.results["population"]["incomplete"], [])
        self.assertEqual(self.results["pending_rule_decisions"], [])

    def test_private_scores(self):
        got = {c["company_id"]: c["factors"] for c in self.results["companies"]}
        # 원래 -3(런레이트 arr 로 한 칸 승격)이었다. FIX-52 S2 로 승격이 막혀 -4 다.
        self.assertEqual(got["anthropic"]["F6"]["score"], -4)
        self.assertEqual(got["anthropic"]["F9"]["score"], -2)
        self.assertEqual(got["openai"]["F6"]["score"], -4)

    def test_approved_run_untouched(self):
        """승인 실행은 건드리지 않았다."""
        base = ROOT / "output" / "ai-scorecard-2026-09-baseline"
        approved = json.loads((base / "approval.json").read_text(encoding="utf-8"))["hashes"]
        from scorecard.stages import current_hashes
        self.assertEqual(current_hashes("ai-scorecard-2026-09-baseline"), approved)
