# 규칙 v2.0 렌더러(항목 이름·① 네 질문과 AI 수익화·② 세대 격차·③ 지표 단계·부품 상한 표기)를 메모리 판단으로 그려 잠근다
"""2026-10-08 규칙 v2.0 렌더러 작업.

실행 묶음 검증(스키마)을 거치지 않는다. 10월 재채점 실행(v1.9)을 읽어 규칙만 v2.0 으로 바꾸고, ① 판단을 `lockin` 입력으로
바꾼 뒤 결과의 ①②③ 은 실제 계산 함수(`calc_qual.compute_f1/f2/f3`)로 다시 만들어 렌더 함수에 넘긴다.
"""
from __future__ import annotations

import copy
import re
import sys
import unittest
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard import calc_qual, engine, stages  # noqa: E402
from scorecard import render_common as rc  # noqa: E402
from scorecard.inputs import JudgmentLookup  # noqa: E402
from scorecard import render_html as rh  # noqa: E402
from scorecard.render_md import render_draft  # noqa: E402
from scorecard.rules import load_rules  # noqa: E402

SLUG = "ai-scorecard-2026-10-rescore"
R19 = load_rules("v1.9")
R20 = load_rules("v2.0")

# 회사별 ① 입력과 그 입력이 사다리에서 내는 점수(계산 함수가 내는지 시험이 확인한다). 적지 않은 회사는 DEFAULT_LOCKIN 이고 3점이다.
LOCKIN = {
    "microsoft": (dict(channel_consumer="no", channel_work="yes", channel_trade="no", loop="partial", switching="pass",
                       substitutes="partial", pricing="pass", pricing_sustained_quarters=9, durability_discount="no",
                       ai_monetized_in_channel="yes"), 5),
    "apple": (dict(channel_consumer="yes", channel_work="no", channel_trade="no", loop="pass", switching="pass",
                   substitutes="pass", pricing="pass", pricing_sustained_quarters=12, durability_discount="no",
                   ai_monetized_in_channel="no"), 5),
    "nvidia": (dict(channel_consumer="no", channel_work="yes", channel_trade="no", loop="pass", switching="partial",
                    substitutes="partial", pricing="pass", pricing_sustained_quarters=9, durability_discount="yes",
                    ai_monetized_in_channel="yes"), 4),
}
DEFAULT_LOCKIN = (dict(channel_consumer="no", channel_work="yes", channel_trade="no", loop="partial", switching="partial",
                       substitutes="pass", pricing="unknown", durability_discount="no", ai_monetized_in_channel="unknown"), 3)
NVIDIA_PATHS = dict(performance_leap="pass", paradigm_adaptation="pass", standard_capture="partial", top_rank="no",
                    generation_gap="no", generation_gap_months=14, leap_independent="no")
MSFT_F3_EXTRA = {"acceleration_tier": "b", "acceleration_growth_rates": [0.12, 0.18]}


def build_v20(reviewed_at: str = "2026-10-09") -> tuple[engine.RunContext, dict, dict | None, list]:
    """v2.0 규칙의 가짜 실행. 판단은 모두 새 판단이고 ① 은 네 질문 입력이다."""
    ctx = engine.load_context(SLUG)
    results = copy.deepcopy(engine.load_results(SLUG))
    judgments = []
    for j in ctx.judgments:
        j = copy.deepcopy(j)
        j["status"], j["reviewed_at"] = "new", reviewed_at
        if j["factor"] == "F1":
            j["kind"], j["score"] = "lockin", None
            j["inputs"] = dict(LOCKIN.get(j["company_id"], DEFAULT_LOCKIN)[0])
        if j["factor"] == "F2" and j["company_id"] == "nvidia":
            j["kind"], j["score"], j["inputs"] = "paths", None, dict(NVIDIA_PATHS)
        if j["factor"] == "F3" and j["company_id"] == "microsoft":
            j["inputs"] = {**j["inputs"], **MSFT_F3_EXTRA}
        judgments.append(j)
    lookup = JudgmentLookup(judgments)
    for c in results["companies"]:
        for fr in c["factors"].values():
            if fr["status"] == "carried_score":
                fr["status"] = "ok"
        company = ctx.companies[c["company_id"]]
        c["factors"]["F1"] = calc_qual.compute_f1(company, lookup, R20)
        if c["company_id"] == "nvidia":
            c["factors"]["F2"] = calc_qual.compute_f2(company, lookup, R20, ctx.run)
        if c["company_id"] == "microsoft":
            c["factors"]["F3"] = calc_qual.compute_f3(company, lookup, R20)
    baseline, _obs, triggers = stages.load_baseline(ctx.run["baseline_id"])
    return replace(ctx, rules=R20, judgments=judgments), results, baseline, triggers


def f1_line(inputs: dict, cid: str = "microsoft") -> str:
    """판단 입력 하나로 계산 함수와 산식 줄을 거친 ① 의 한 줄."""
    fr = calc_qual.compute_f1({"company_id": cid, "type": "업무"},
                              JudgmentLookup([{"judgment_id": f"{cid}.F1", "company_id": cid, "factor": "F1", "kind": "lockin", "inputs": inputs,
                                               "status": "new", "score": None}]), R20)
    return rc.factor_calc_text("F1", fr, R20, inputs, "업무")


def render_full(ctx, results, baseline, triggers) -> str:
    return rh.render_document(ctx, results, baseline, triggers, {"review_type": "mem", "reviewers": []},
                              {"approval_id": "00000000-memory", "approved_by": "mem", "approved_at": "2026-10-09"}, None)


def frow(html: str, cid: str, label: str) -> str:
    card = re.search(rf'<details class="card" id="card-{re.escape(cid)}".*?</details>', html, re.S).group(0)
    return next(ch for ch in card.split('<div class="frow">')[1:] if f'<span class="flab">{label}</span>' in ch)


class FactorLabelTest(unittest.TestCase):
    def test_old_rules_keep_old_names_and_v20_renames_only_f1(self):
        self.assertEqual(rc.factor_label(R19, "F1"), "① 네트워크")
        self.assertEqual(rc.factor_label(None, "F1"), "① 네트워크")
        self.assertEqual(rc.factor_label(R20, "F1"), "① 락인")
        for fid in rc.FACTOR_LABELS:
            if fid != "F1":
                self.assertEqual(rc.factor_label(R20, fid), rc.FACTOR_LABELS[fid], fid)
                self.assertEqual(rc.factor_label(R19, fid), rc.FACTOR_LABELS[fid], fid)


class LockinCardTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.ctx, cls.results, cls.baseline, cls.triggers = build_v20()
        cls.cards = rh.render_cards(cls.results, cls.baseline, cls.ctx.companies, cls.ctx.observations, cls.ctx.judgments,
                                    [], cls.ctx)

    def test_card_shows_channels_four_questions_and_ai(self):
        row = frow(self.cards, "microsoft", "① 락인")
        for needle in ("채널 업무", "회수 루프 부분", "전환비용 통과", "대체 공급 부분", "가격 실측 통과(9분기 지속)",
                       "지속성 할인 없음", "AI 수익화 예(점수 밖 표시)", "네 질문 사다리", "사다리 강도 4, 가격 실측 +1 = 5"):
            self.assertIn(needle, row)
        self.assertIn("AI 수익화 아니오", frow(self.cards, "apple", "① 락인"))

    def test_durability_discount_shows_in_the_ladder(self):
        row = frow(self.cards, "nvidia", "① 락인")
        self.assertIn("지속성 할인 해당", row)
        self.assertIn("사다리 강도 4, 가격 실측 +1, 지속성 할인 -1 = 4", row)

    def test_engine_scores_match_the_fixture(self):
        for c in self.results["companies"]:
            with self.subTest(company=c["company_id"]):
                self.assertEqual(c["factors"]["F1"]["score"], LOCKIN.get(c["company_id"], DEFAULT_LOCKIN)[1])
        default = next(c for c in self.results["companies"] if c["company_id"] not in LOCKIN)
        self.assertIn("→ 사다리 강도 3 · AI", frow(self.cards, default["company_id"], "① 락인"))

    def test_ladder_line_comes_from_engine_steps_only(self):
        fr = {"basis": "lockin", "score": 5, "calc": {"inputs": LOCKIN["microsoft"][0]}, "pending": {}}
        text = rc.factor_calc_text("F1", fr, R20, None, "업무")
        self.assertIn("전환비용 통과", text, "입력은 calc.inputs 에서도 읽는다")
        self.assertNotIn("사다리", text, "엔진이 보정 단계를 남기지 않았으면 사다리 줄을 만들지 않는다")

    def test_pricing_short_of_quarters_is_shown_as_computed_partial(self):
        text = f1_line({**LOCKIN["microsoft"][0], "pricing_sustained_quarters": 6})
        self.assertIn("가격 실측 통과(6분기 지속, 부분으로 계산)", text)
        self.assertIn("→ 사다리 강도 4 · AI", text, "부분은 보정이 0 이라 강도가 곧 점수다")

    def test_clamp_and_no_channel(self):
        text = f1_line({**LOCKIN["apple"][0], "substitutes": "fail", "durability_discount": "yes", "loop": "fail",
                        "switching": "fail", "pricing": "fail"})
        self.assertIn("사다리 강도 1, 가격 실측 -1, 대체 공급 -1, 지속성 할인 -1 = 0(0~5 로 자름)", text)
        none = f1_line({**DEFAULT_LOCKIN[0], "channel_work": "no"})
        self.assertIn("채널 없음", none)
        self.assertIn("사다리 실질 채널 없음 0", none)

    def test_both_strength_unknown_gives_no_ladder(self):
        text = f1_line({**DEFAULT_LOCKIN[0], "loop": "unknown", "switching": "unknown"})
        self.assertIn("회수 루프 미확인", text)
        self.assertNotIn("사다리", text)
        self.assertIn("둘 다 미확인", text, "판단 대기 사유가 산식 줄 끝에 붙는다")

    def test_f2_generation_gap_and_independent_measurement(self):
        row = frow(self.cards, "nvidia", "② 게임체인저")
        self.assertIn("세대 격차 14개월(임계 12개월)", row)
        self.assertIn("독립 측정 아니오(성능 도약은 부분 통과로 계산)", row)
        fr = {"basis": "paths", "score": 4, "calc": {}, "pending": {}}
        self.assertIn("(임계 6개월)", rc.factor_calc_text("F2", fr, R20, {"generation_gap_months": 3}, "업무"))

    def test_f3_acceleration_tier_and_two_growth_rates(self):
        row = frow(self.cards, "microsoft", "③ Last Mover")
        self.assertIn("지표 단계 b — AI 지배 세그먼트·제품선(비AI 비중 표기)", row)
        self.assertIn("성장률 12.0% → 18.0%", row)
        fr = {"basis": "criteria", "pending": {},
              "calc": {"pass_points": 1.5, "ladder_note": "통과점 1.5 → 3", "criteria": {"acceleration": "partial"},
                       "acceleration_input": "pass", "acceleration_tier": "c"}}
        self.assertIn("가속도는 입력 통과를 단계 상한에 맞춰 부분으로 계산", rc.factor_calc_text("F3", fr, R20, {"acceleration": "pass"}, "업무"))

    def test_old_rules_and_old_inputs_add_nothing(self):
        fr = {"basis": "manual", "score": 2, "calc": {}, "pending": {}}
        self.assertEqual(rc.factor_calc_text("F1", fr, R19, {}, "부품"), "")
        self.assertEqual(rc.factor_calc_text("F2", {"basis": "carried", "calc": {}, "pending": {}}, R19, {}, "부품"), "")
        f3 = {"basis": "criteria", "calc": {"pass_points": 2, "ladder_note": "통과점 2 → 3"}, "pending": {}}
        self.assertEqual(rc.factor_calc_text("F3", f3, R20, {"imitation": "pass"}, "업무"), "통과점 2 → 3")

    def test_draft_factor_table_carries_the_same_line(self):
        md = render_draft(self.ctx, self.results, self.baseline, self.triggers)
        self.assertRegex(md, r"\| ① 락인 \| 5 \| [^|]+ \| 네 질문 사다리 \| 채널 업무 · 회수 루프 부분 · 전환비용 통과 .*AI 수익화 예")
        self.assertIn("- **① 락인** 근거", md)
        # 근거 문장(판단 파일의 데이터)에 옛 이름이 남아 있을 수 있다. 렌더러가 쓰는 표·머리줄에는 없어야 한다
        self.assertNotIn("| ① 네트워크 |", md)
        self.assertNotIn("- **① 네트워크**", md)


class LockinPageTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.ctx, cls.results, cls.baseline, cls.triggers = build_v20()
        cls.html = render_full(cls.ctx, cls.results, cls.baseline, cls.triggers)
        old = engine.load_context(SLUG)
        ob, _o, ot = stages.load_baseline(old.run["baseline_id"])
        cls.old_ctx, cls.old_results = old, engine.load_results(SLUG)
        cls.old_html = render_full(old, cls.old_results, ob, ot)

    def test_ranking_has_ai_column_that_splits_equal_f1_scores(self):
        head = re.search(r'<table id="mainTable"><thead>(.*?)</thead>', self.html, re.S).group(1)
        self.assertIn('data-k="F1">①락인</th><th scope="col" data-k="F1ai">AI 수익화</th>', head)
        for cid, shown in (("microsoft", "예"), ("apple", "아니오")):
            row = re.search(rf'<tr class="row" data-company="{cid}">(.*?)</tr>', self.html, re.S).group(1)
            self.assertIn('<td data-k="F1" data-v="5">', row)
            self.assertIn(f'<td data-k="F1ai" data-v="{shown}">', row)
        self.assertNotIn('data-k="F1ai"', self.old_html, "옛 규칙의 실행에는 AI 수익화 열이 없다")
        self.assertIn('data-k="F1">①네트워크</th>', self.old_html)

    def test_legend_has_cap_only_with_rule_key(self):
        legend = re.search(r'<div class="legend">(.*?)</div>', self.html, re.S).group(1)
        self.assertIn("부품", legend)
        self.assertNotIn("상한", legend)
        old_legend = re.search(r'<div class="legend">(.*?)</div>', self.old_html, re.S).group(1)
        self.assertIn("부품 (① 상한 2점)", old_legend)

    def test_method_and_index_use_v20_wording(self):
        f1 = " ".join(rc.factor_criteria(self.ctx, "F1"))
        for needle in ("실질 채널은 소비자·업무·거래 셋이다", "회수 루프", "전환비용", "대체 공급", "가격 실측",
                       "지속성 할인은 10-K 공시 매출 10% 이상 고객", "AI 수익화"):
            self.assertIn(needle, f1)
        self.assertNotIn("상한 2", f1)
        self.assertIn("상한", " ".join(rc.factor_criteria(self.old_ctx, "F1")), "옛 실행은 옛 규칙의 부품 상한 문장")
        method = dict(rc.method_sections(self.ctx, self.results))
        self.assertIn("채널과 네 질문의 판정", " ".join(method["F1"]))
        self.assertIn("2위가 그 수준에 도달하는 데 6개월(칩·파운드리는 대량 출하 기준 12개월)", " ".join(method["F2"]))
        self.assertIn("사람이 직접 매기는 둘(④⑧)은", self.html)
        self.assertIn("사람이 직접 매기는 셋(①④⑧)은", self.old_html)
        self.assertIn("규칙이 <code>mode: manual</code> 로 둔 칸이다(④⑧)", self.html)
        self.assertIn('id="idx-네-질문-사다리"', self.html)
        self.assertIn("엔진은 그 판정 입력으로 점수를 계산한다", self.html)
        self.assertNotIn("엔진은 그 판정 입력으로 점수를 계산한다", self.old_html)

    def test_component_cap_note_only_with_rule_key(self):
        fr = {"warnings": ["F1 부품 상한 2 적용 대상(실질 소비자·업무 채널 없음)"], "calc": {}}
        old = rc.factor_notes(self.old_ctx, "F1", fr)
        self.assertEqual([n["kind"] for n in old], ["cap"])
        new = rc.factor_notes(self.ctx, "F1", fr)
        self.assertNotIn("cap", [n["kind"] for n in new])

    def test_new_screen_sentences_are_self_contained(self):
        from scorecard.validate import SELF_CONTAINED_BANNED
        texts = [rc.factor_calc_text("F1", self.results["companies"][0]["factors"]["F1"], R20, LOCKIN["nvidia"][0], "부품"),
                 *rc.lockin_criteria(R20.factor("F1")), rh.BASIS_DOC["lockin"][1], rh.MODE_DOC["lockin"][1],
                 *dict(rc.method_sections(self.ctx, self.results))["F1"],
                 re.search(r'<div class="notice info" id="judgment-status".*?</div>', self.html, re.S).group(0)]
        for text in texts:
            for pat, why in SELF_CONTAINED_BANNED:
                self.assertIsNone(pat.search(text), f"{why}: {text[:80]}")


if __name__ == "__main__":
    unittest.main()
