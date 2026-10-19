# 규칙 v3.0 초안·미리보기 최소 렌더(계획 S10) — 층 표·층·사업 판단 근거·v3.0 방법 절·척도 환산을 잠그고 옛 실행 출력에 새 문장이 없는지 본다
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard import engine, stages  # noqa: E402
from scorecard.render_common import RESCALED_NOTE  # noqa: E402
from scorecard.render_md import render_draft, render_preview  # noqa: E402
from tests.test_collect_stage import SLUG  # noqa: E402
from tests.test_rules_v30_unit_paths import CP, PATHS, TEXT, V30Base  # noqa: E402

LAYERS = ("power", "foundry", "chip_design", "systems", "cloud", "dev_platform", "data_platform", "model", "application",
          "user_platform", "device")


def line(lid: str, layer: str, amount: float, non_ai: str = "no") -> dict:
    return {"line": lid, "label": lid, "amount": amount, "period": "2025Q3~2026Q2", "layer": layer, "non_ai": non_ai,
            "evidence_ids": ["EV-nvidia-001"]}


def business(name: str, layer: str, lines: list[str], customer: str) -> dict:
    return {"components": [{"name": name, "layer": layer, "customer": customer, "lines": lines, "market": None, "ai_monetized": "partial"}],
            "participant": "core_measured", "switching": "stay_measured", "pricing": "no_change", "substitutes": "gap_remains"}


class V30RenderTest(V30Base):
    def setUp(self) -> None:
        super().setUp()
        cells = {layer: {"cell": "none", "evidence_ids": []} for layer in LAYERS}
        cells["chip_design"] = {"cell": "sold", "evidence_ids": []}
        cells["device"] = {"cell": "sold", "ai_chain": "yes", "evidence_ids": []}
        holdings = {"cells": cells, "currency": "USD", "non_ai_margin": 0.25, "non_ai_margin_source": "segment",
                    "revenue_lines": [line("data_center", "chip_design", 80), line("gaming", "device", 20, "yes")]}
        self.judge("nvidia", "F4", {**holdings, **TEXT})
        self.judge("nvidia", "F2", {**PATHS, **TEXT}, layer="chip_design")
        self.judge("nvidia", "F2", {"adaptation": "adopted", "standards": [], **TEXT}, layer="device")
        self.judge("nvidia", "F3", {**CP, **TEXT}, layer="chip_design")
        self.judge("nvidia", "F3", {**CP, "counterparty_present": "no", "counterparty": None, **TEXT}, layer="device")
        self.judge("nvidia", "F1", {**business("Data Center", "chip_design", ["data_center"], "work"), **TEXT}, business="data_center")
        self.judge("nvidia", "F1", {**business("Gaming", "device", ["gaming"], "consumer"), **TEXT}, business="gaming")
        self.judge("nvidia", "F5", {"relations": [{"counterparty": "TSMC", "qualifies": ["commercial"], "evidence_ids": ["EV-nvidia-001"]}],
                                    "fronts": [{"name": "수출 통제", "nature": "cost", "status": "ongoing", "jurisdiction": "US",
                                                "remedy_in_progress": "yes", "evidence_ids": ["EV-nvidia-001"]}],
                                    "partner_tension": "no", **TEXT})
        self.ctx = engine.load_context(SLUG)
        self.results = engine.compute(self.ctx)
        engine.write_results(SLUG, self.results)
        self.scores, _obs, _trig = stages.load_baseline(self.ctx.run["baseline_id"])

    def test_draft_shows_layers_units_and_v30_method(self):
        text = render_draft(self.ctx, self.results, self.scores, self.ctx.triggers)
        for needle in (
            "| ① 네트워크 | 12 | 이번 실행 산출 | 사업 단위 합산 | 사업 2개 → AI 칩 설계 12.2 × 80% + 기기 12.2 × 20% |",   # 항목 점수는 정수(2026-10-19)
            "| ② 게임체인저 | 10 | 이번 실행 산출 | 층별 세 경로 | AI 칩 설계 10 × 80% + 기기 8 × 20% |",
            "| ⑤ 아군 | 9 | 이번 실행 산출 | 동맹 세 부분·적대 띠 | 12 + 동맹 1 + 적대 -4(비용형) |",
            "| AI 칩 설계 | 80% | 12.2 | 10 | 11.14 |",
            "- **② 게임체인저 — AI 칩 설계** 근거",
            "- **① 네트워크 — Gaming** 근거",
            "- **① 네트워크.** 사업마다 A 락인",
            "- **⑦ 순환금융.** 두 축의 판정(조달 의존 고객 비중 · 내 돈 환류)을 조합표에서 찾는다. 비중 작음·환류 없음 0",
            "만점의 40% 로 계산하고 미확인을 표시한다",
            "항목 점수는 정수로 반올림하고 총점은 반올림한 항목 점수를 더한다",
            "| ① 네트워크 | 사업 단위 합산 | 0~20 |",
        ):
            with self.subTest(needle=needle[:40]):
                self.assertIn(needle, text)
        for stale in ("3 + A(", "제안된 새 구간", "| business |", "| layer_paths |", "한 칸을 조정한 값이다", "밸류/매출 구간표"):
            with self.subTest(stale=stale):
                self.assertNotIn(stale, text)

    def test_pilot9_output_review_fixes(self):
        """2026-10-19 pilot9 출력 리뷰: 방법 절의 옛 문장(N5), 산점도 폰 폭(N2), 현금 연결표 주당 기준, ⑨ 산식 끝수(N7)."""
        from scorecard import render_common as rc
        from scorecard.render_html import _scatter_wrap, render_method
        import dataclasses
        # 정보 컷오프 뒤에 검토한 이어받은 판단이 있을 때만 컷오프 단서를 적는다(컷오프 앞 기준선 판단은 뒤 사건을 담을 수 없다)
        cutoff = str(self.ctx.run.get("info_cutoff") or self.ctx.run["as_of"])
        first = self.ctx.judgments[0]
        for status, reviewed, shown in (("carried", "2099-01-01", True), ("carried", "2000-01-01", False), ("new", "2099-01-01", False)):
            js = [{**j, "status": "new"} for j in self.ctx.judgments[1:]] + [{**first, "status": status, "reviewed_at": reviewed}]
            variant = dataclasses.replace(self.ctx, judgments=js)
            with self.subTest(status=status, reviewed=reviewed, cutoff=cutoff):
                self.assertEqual("컷오프 이후 사건이" in render_method(variant, self.results), shown)
        ctx = dataclasses.replace(self.ctx, judgments=[{**j, "status": "new"} for j in self.ctx.judgments])
        draft = render_draft(ctx, self.results, self.scores, ctx.triggers)
        method = render_method(ctx, self.results)
        for text in (draft, method):
            self.assertNotIn("컷오프 이후 사건이", text)
        for stale in ("3 + 동맹등급", "이 둘만 점수에 개입", "NTM PER을 구간표에", "세 경로 중 하나면 된다"):
            with self.subTest(stale=stale):
                self.assertNotIn(stale, method)
        self.assertIn("<b>성장 조정 PER</b>(번 것과 성장에 비해 비싼가)", method)
        self.assertIn("비상장 EV/Sales·매출 성장률·입력 신뢰도", method)
        self.assertEqual(_scatter_wrap(self.ctx, "<svg></svg>"), '<div class="scwrap"><svg></svg></div>')
        chain = rc.cash_chain_table(self.ctx, self.results)
        self.assertTrue(any("최근 분기의 가중평균" in n for n in chain["notes"]))
        self.assertEqual(rc.f9_gate_text({"gate": "G1-after", "applied": True, "score": -12.318693333333334}), "본업 실패 뒤 정리 적용 → -12.32")

    def test_zero_weight_layer_judgment_is_not_shown_and_shares_keep_small_values(self):
        # 2026-10-15 시범 실행: 매출 몫 0 층의 판단이 근거로 실렸고, 0.34% 층이 '× 0%' 로 보였고, ⑥ 산식에 긴 소수가 나왔다
        from scorecard.render_common import _share_text
        holdings = next(j for j in self.ctx.judgments if j["judgment_id"] == "nvidia.F4")["inputs"]
        cells = {**holdings["cells"], "model": {"cell": "sold", "evidence_ids": []}}
        self.judge("nvidia", "F4", {**{k: v for k, v in holdings.items() if k not in ("evidence", "evidence_up", "evidence_down")},
                                    "cells": cells, **TEXT})
        self.judge("nvidia", "F2", {**PATHS, **TEXT}, layer="model")
        ctx = engine.load_context(SLUG)
        results = engine.compute(ctx)
        text = render_draft(ctx, results, self.scores, ctx.triggers)
        self.assertIn("- **② 게임체인저 — AI 칩 설계** 근거", text)
        self.assertNotIn("- **② 게임체인저 — 모델** 근거", text)
        self.assertEqual((_share_text(0.0034), _share_text(0.8227), _share_text(0)), ("0.3%", "82%", "0%"))
        self.assertNotRegex(text, r"→ -?\d+\.\d{3,}")

    def test_html_card_shows_layer_tables_and_unit_blocks(self):
        # 2026-10-19: v3.0 HTML 카드에 층·사업 판단 근거와 층 표가 없었다(초안에만 있었다)
        from scorecard import render_common as rc
        from scorecard.render_html import V3_CSS, css, render_cards
        html = render_cards(self.results, self.scores, self.ctx.companies, self.ctx.observations, self.ctx.judgments,
                            rc.replacements(self.ctx), self.ctx)
        card = html[html.index('id="card-nvidia"'):]
        for needle in ('<div class="cv3">', "층별 점수", "<td class=\"name\"><b>AI 칩 설계</b></td><td class=\"mono\">80%</td>",
                       '<span class="uname">AI 칩 설계</span><span class="usc">10</span>',
                       '<span class="uname">기기</span><span class="usc">8</span>',
                       '<span class="uname">Gaming</span><span class="usc">12.2</span>',
                       '<div class="fdh">올릴 근거</div>'):
            with self.subTest(needle=needle[:40]):
                self.assertIn(needle, card)
        self.assertNotIn("판단 기록 `nvidia.F2.", card, "판단 ID 는 감사 기록으로 보낸다")
        self.assertIn("details.unit", css(True))
        self.assertNotIn(V3_CSS.strip()[:20], css(False), "층 정의가 없는 옛 실행의 CSS 는 그대로다")

    def test_html_summary_holdings_table(self):
        # 2026-10-19: v3.0 요약에 열한 층 보유표가 없었다(v2.1 여섯 층 표만 있었다)
        from types import SimpleNamespace
        from scorecard.render_html import render_holdings_v3
        from scorecard.rules import load_rules
        html = render_holdings_v3(self.results, self.ctx)
        for needle in ("열한 층 보유표와 비교 그룹", "<th>전력</th>", '<td class="c-g5">판매<span class="lw">80%</span></td>',
                       '<td class="c-g0">없음</td>', "<td>AI 칩 설계</td>", "판매 1 · 자체 사용 0.5"):
            with self.subTest(needle=needle[:30]):
                self.assertIn(needle, html)
        self.assertNotIn("비교 그룹 안 순위", html, "순위가 확정되지 않은(미완료) 회사는 그룹 안 순위에 넣지 않는다")
        self.assertEqual(render_holdings_v3(self.results, SimpleNamespace(rules=load_rules("v2.1"))), "")

    def test_scatter_uses_rule_baselines(self):
        # 2026-10-19: v3.0 산점도에 25점 척도의 '과점 후보군 20점' 선이 그대로 그려졌다
        from scorecard.render_html import scatter_svg
        from scorecard.rules import load_rules
        one = {"companies": [{"company_id": "nvidia", "display_name": "NVIDIA", "complete": True, "reference": False, "moat": 41.3,
                              "trap": -22.7, "total": 18.6, "type": "부품", "factors": {"F4": {"calc": {"primary_layer": "chip_design"}}}}]}
        v3 = scatter_svg(one, {}, self.ctx.rules)
        for needle in ("과점 후보군 80점 (잠정)", "승자 되기 어려움 56점 (잠정)", ">80</text>", ">-24</text>"):
            with self.subTest(needle=needle):
                self.assertIn(needle, v3)
        self.assertNotIn("과점 후보군 20점", v3)
        old = scatter_svg({"companies": [{**one["companies"][0], "moat": 18, "trap": -6, "total": 12}]}, {}, load_rules("v2.1"))
        self.assertIn("과점 후보군 20점", old)
        self.assertEqual(old, scatter_svg({"companies": [{**one["companies"][0], "moat": 18, "trap": -6, "total": 12}]}, {}),
                         "옛 규칙의 그림은 규칙을 넘기든 안 넘기든 같다")

    def test_html_method_uses_v30_modes_and_criteria(self):
        # 2026-10-19: 방법 절 방식 칸에 business·layer_paths 같은 내부 이름이, '무엇을 보고 매기는가' 에 옛 규칙 지표 문장이 나왔다
        from scorecard.render_common import factor_criteria
        from scorecard.render_html import _mode_cell
        for mode, name in (("business", "사업마다 다섯 부분을 더한다"), ("layer_paths", "층마다 세 경로를 더한다"),
                           ("layer_cp", "층마다 카운터 포지셔닝을 잰다"), ("holdings", "보유표 세 부분을 더한다"),
                           ("alliance", "동맹 세 부분과 적대 띠")):
            with self.subTest(mode=mode):
                self.assertIn(name, _mode_cell(mode))
        criteria = {fid: " ".join(factor_criteria(self.ctx, fid)) for fid in ("F1", "F2", "F3", "F4", "F5")}
        self.assertIn("최근 2개 분기", criteria["F1"])
        self.assertIn("최근 24개월", criteria["F2"])
        self.assertIn("없으면 최고 8, 한 곳이면 최고 5, 두 곳 이상이면 0", criteria["F3"])
        self.assertIn("AI 사슬 조건 층(전력 · 데이터 플랫폼 · 사용자 플랫폼 · 기기)은", criteria["F4"])
        self.assertIn("회사가 원고인 소송", criteria["F5"])
        for stale in ("통과점", "상한 2점", "부품:"):
            with self.subTest(stale=stale):
                self.assertNotIn(stale, " ".join(criteria.values()))

    def test_score_colors_scale_with_the_v30_ranges(self):
        # 2026-10-19 pilot9 출력 리뷰 F-2: 0~5 눈금이라 ④ 만점 20 이 회색, ① 5 가 초록으로 칠해졌다
        from scorecard.render_html import score_class, total_class, trap_class
        rules = self.ctx.rules
        self.assertEqual([score_class(s, rules, "F4") for s in (20, 16, 12, 9, 3, 0)], ["g5", "g4", "g3", "g2", "g1", "g0"])
        self.assertEqual([trap_class(s, rules, "F8") for s in (0, -4, -8, -12, -16)], ["g5", "g4", "g3", "g2", "g1"])
        self.assertEqual([total_class(t, rules) for t in (60, 48, 43, 4, 0)], ["g5", "g4", "g3", "g2", "g1"])
        self.assertEqual((score_class(4), trap_class(-1), total_class(15)), ("g4", "g4", "g5"), "옛 규칙의 눈금은 그대로다")

    def test_html_notes_use_names_not_ids(self):
        # 2026-10-19: 카드의 '참고' 줄에 ['chip_design', …] 목록과 사업 id 앞머리가 그대로 보였다(HTML 표시만 바꾼다)
        from scorecard.render_html import _readable_note
        for raw, shown in (("매출 몫 0 층 ['model', 'device'] 의 세 경로 판단", "매출 몫 0 층 모델 · 기기 의 세 경로 판단"),
                           ("cloud: 지표 단계 c 의 가속도는 최고 3", "클라우드 — 지표 단계 c 의 가속도는 최고 3"),
                           ("gaming: 구성 Gaming 의 시장이 정해지지 않아", "구성 Gaming 의 시장이 정해지지 않아"),
                           ("전선 ['고객 A(경쟁사 소유)', '고객 B'] — 40% 지점", "전선 고객 A(경쟁사 소유) · 고객 B — 40% 지점"),
                           ("unknown_id: 그대로 둔다", "unknown_id: 그대로 둔다")):
            with self.subTest(raw=raw[:20]):
                self.assertEqual(_readable_note(self.ctx, "nvidia", raw), shown)

    def test_preview_rescales_old_scores(self):
        text = render_preview(self.ctx, self.results, self.scores)
        self.assertIn("① 네트워크 2(×4 환산 8)→12", text)
        self.assertIn(RESCALED_NOTE, text)


class LimitationsTest(unittest.TestCase):
    def test_correction_marker_is_dropped_only_for_layered_rules(self):
        """2026-10-19 pilot8 출력 리뷰 F-5: 규칙 파일 순현금 질문 앞의 '[정정 … FIX-53]' 표지가 v3.0 초안에 실렸다.
        v3.0 은 걷어 내고, 승인된 옛 실행(v2.1)의 초안은 바이트 그대로 둔다."""
        from types import SimpleNamespace
        from scorecard.render_common import limitations
        from scorecard.rules import load_rules
        rules = load_rules("v2.1")
        questions = rules.payload["policies"]["f6"]["net_cash"]["open_questions"]
        self.assertTrue(any("[정정" in q for q in questions), "규칙 파일에 표지가 있는 질문이 있어야 시험이 뜻을 갖는다")
        ctx = SimpleNamespace(rules=rules, run={"companies": []}, companies={}, observations=[], sources={"items": []})
        self.assertIn("[정정", " ".join(limitations(ctx)))
        # 2026-10-19: v3.0 규칙 파일은 질문을 현재 상태 문장으로 다시 썼다. 표지가 없어도 렌더러는 걷어 낸다.
        v30 = load_rules("v3.0")
        marked = json.loads(json.dumps(v30.payload))
        marked["policies"]["f6"]["net_cash"]["open_questions"] = ["[정정 2026-09-15 FIX-53] 담보 예금의 몫"]
        ctx = SimpleNamespace(rules=SimpleNamespace(payload=marked), run={"companies": []}, companies={}, observations=[],
                              sources={"items": []})
        text = " ".join(limitations(ctx))
        self.assertNotIn("[정정", text)
        self.assertIn("담보 예금의 몫", text)

    def test_questions_are_whole_and_only_for_companies_in_the_run(self):
        """2026-10-19 pilot9 출력 리뷰(N11): 160자에서 문장이 끊기고 이 실행에 없는 회사의 질문이 실렸다."""
        from types import SimpleNamespace
        from scorecard.render_common import limitations
        from scorecard.rules import load_rules
        payload = json.loads(json.dumps(load_rules("v3.0").payload))
        long_q = "TSMC " + "가" * 200 + " 끝."
        payload["policies"]["f6"]["net_cash"]["open_questions"] = [long_q, "Alibaba 의 혼합 줄", "회사를 들지 않는 질문"]
        companies = {"tsmc": {"display_name": "TSMC"}, "alibaba": {"display_name": "Alibaba"}}
        for run_companies, shown, hidden in ((["tsmc"], [long_q, "회사를 들지 않는 질문", "나머지 1건"], ["Alibaba 의 혼합 줄"]),
                                             (["alibaba"], ["Alibaba 의 혼합 줄"], [long_q])):
            ctx = SimpleNamespace(rules=SimpleNamespace(payload=payload), run={"companies": run_companies}, companies=companies,
                                  observations=[], sources={"items": []})
            text = "\n".join(limitations(ctx))
            with self.subTest(run=run_companies):
                for s in shown:
                    self.assertIn(s, text)
                for s in hidden:
                    self.assertNotIn(s, text)


class OldRunsUntouchedTest(unittest.TestCase):
    """v2.x 승인 실행의 초안에는 v3.0 문장이 들어가지 않는다(분기는 규칙의 layers 에만 묶인다)."""

    def test_v21_draft_has_no_v30_text(self):
        slug = "ai-scorecard-2026-10-v21"
        d = ROOT / "output" / slug
        if not d.is_dir():
            self.skipTest(f"{slug} 실행이 없다")
        ctx = engine.load_context(slug)
        results = json.loads((d / "results.json").read_text(encoding="utf-8"))
        scores, _o, _t = stages.load_baseline(ctx.run["baseline_id"])
        draft = render_draft(ctx, results, scores, ctx.triggers)
        preview = render_preview(ctx, results, scores)
        for needle in ("층 매출 몫", "사업 단위 합산", "만점의 40%", "배 환산 참고값", "(×4 환산", "| 층 |"):
            with self.subTest(needle=needle):
                self.assertFalse(needle in draft + preview, f"v2.1 출력에 v3.0 문장 {needle!r} 이 들어갔다")
        self.assertIn("과점 후보군(과점 20점 이상)", draft)


if __name__ == "__main__":
    unittest.main()
