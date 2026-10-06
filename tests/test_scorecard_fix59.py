# FIX-59 마지막 반영 — 8차 리뷰 전부 + openai.F9 경로 결정(사용자) + 승인 준비를 고정한다
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
from scorecard.render_md import render_draft  # noqa: E402
from scorecard.rules import load_rules  # noqa: E402
from scorecard.stages import load_baseline  # noqa: E402

RULES = load_rules("v1.7")
SLUG = "ai-scorecard-2026-09-obsreg"
RUN_DIR = ROOT / "output" / SLUG
SRC = ROOT / "scripts" / "scorecard"
# 2026-10-06 규칙 문서 재편으로 v1.5 규칙 문서를 작업 폴더에서 지웠다. 인용 행 대조는 git 이력에서 꺼낸 원문으로
# 한다(파일이 없다고 건너뛰면 조용히 통과한다).
from tests.legacy_docs import RULES_V15, legacy_text  # noqa: E402


def load(name: str) -> dict:
    return json.loads((RUN_DIR / name).read_text(encoding="utf-8"))


def preserved(ref: str) -> str:
    raw = subprocess.run(["git", "-C", str(ROOT), "show", ref], capture_output=True, check=True).stdout
    t = html.unescape(re.sub(r"<[^>]+>", " ", raw.decode("utf-8", "replace")))
    return re.sub(r"\s+", " ", t)


class Fix59Test(unittest.TestCase):
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

    def test_totals_unchanged(self):
        self.assertEqual({c: r["total"] for c, r in self.res.items()},
                         {"alphabet": 15, "amazon": 15, "meta": 15, "microsoft": 14, "tsmc": 10, "anthropic": 10,
                          "spacex-xai": 9, "nvidia": 9, "apple": 8, "alibaba": 7, "palantir": 6, "tesla": 5,
                          "openai": 4, "oracle": 2})

    # ---------------------------------------------------------------- S1 openai.F9 경로
    # 2026-09-17 FIX-62: 사용자가 같은 날 이 결정을 뒤집었다(C-29). 아래 둘은 **당시 결정이 지워지지 않고
    # 보존 기록으로 남았는지**를 본다. 뒤집힌 뒤의 사실은 tests/test_scorecard_fix62.py 가 고정한다.
    def test_bep_retreat_precedence_is_kept_as_a_superseded_record(self):
        spec = RULES.payload["policies"]["f9"]["g1_bep_retreat_precedence"]
        self.assertEqual(spec["status"], "superseded")
        old = spec["superseded_record"]
        self.assertIn("C-20 비상장 판정보다 앞선다", old["rule"])
        self.assertIn("and not bep_retreat", old["where_in_code"])
        self.assertEqual(old["decided_by"], "사용자 (2026-09-17)")
        # 인용한 v1.5 행이 실제로 그 문장인지 원문에서 확인한다.
        v15 = legacy_text(RULES_V15)
        if v15 is None:
            self.skipTest("git 이력에서 v1.5 규칙 원문을 꺼내지 못했다")
        else:
            lines = v15.splitlines()
            self.assertIn("BEP 목표가 후퇴", lines[469])
            self.assertIn("OpenAI", lines[493])
            self.assertIn("BEP 자체가 후퇴", lines[602])
            self.assertIn("계획·발표·포지션은 0점", lines[389])

    def test_the_tension_that_predicted_the_reversal(self):
        t = {x["id"]: x for x in RULES.payload["open_tensions"]}["TEN-RA5-02"]
        self.assertEqual((t["judgment_ids"], t["recheck_at"]), (["openai.F9"], "2026-11"))
        self.assertIn("별표 D 388~390행", t["tension"])
        self.assertIn("assume_loss", t["tension"])
        self.assertEqual(t["third_party_recheck"], "committed")
        # FIX-59 가 예고한 상향이 그대로 일어났다.
        self.assertIn("총점 2 → **4**", t["direction"])
        self.assertEqual(t["status"], "resolved")
        self.assertEqual(self.res["openai"]["factors"]["F9"]["score"], -2)
        self.assertEqual(self.res["openai"]["total"], 4)
        # anthropic 과의 차이를 만들던 입력 한 칸은 그대로이나 이제 경로를 가르지 않는다.
        self.assertEqual(self.j["openai.F9"]["inputs"]["bep_retreat"], "yes")
        self.assertEqual(self.j["anthropic.F9"]["inputs"]["bep_retreat"], "no")
        self.assertTrue(any("bep_retreat` no 대 yes" in a for a in self.run_json["assumptions"]))
        for cid in ("openai", "anthropic"):
            with self.subTest(cid=cid):
                self.assertEqual(self.res[cid]["factors"]["F9"]["calc"]["path"][0]["decision_id"], "C-20")

    # ---------------------------------------------------------------- S2 B 8차
    def test_how_to_measure_no_longer_contradicts_the_note_split(self):
        scope = RULES.payload["policies"]["f6"]["net_cash"]["securities_scope"]
        how = scope["how_to_measure"]
        self.assertIn("한 줄 안에 시장성과 비시장성이 섞이면 주석으로 내려가 가른다", how)
        self.assertNotIn("**대차대조표 줄만 쓴다.**", how)
        self.assertIn("만기·공정가치 버킷", how)
        # nvidia 는 주석 분할로 들어갔고 만기 버킷은 여전히 안 쓴다.
        comp = self.o["nvidia.net_cash.nc37"]["basis"]["components"]
        self.assertEqual(comp["marketable_equity_added"]["tag"], "us-gaap:EquitySecuritiesFvNi")
        tags = {c["tag"] for c in comp["cash_and_marketable_securities_concepts"]}
        self.assertNotIn("us-gaap:AvailableForSaleSecuritiesDebtMaturitiesWithinOneYearFairValue", tags)

    def test_remainder_sensitivity_recorded_and_bands_hold(self):
        sens = RULES.payload["policies"]["f6"]["net_cash"]["securities_scope"]["remainder_sensitivity"]
        self.assertEqual(sorted(sens["cases"]), ["alphabet", "microsoft", "nvidia", "oracle"])
        for cid, case in sens["cases"].items():
            with self.subTest(cid=cid):
                self.assertFalse(case["changes"])
                p2 = self.res[cid]["factors"]["F6"]["calc"]["parameters"]["P2"]
                self.assertAlmostEqual(p2["value"], case["p2_now"], places=4)
                self.assertEqual(p2["band"], case["band"])
        self.assertIn("만기 버킷은 쓰지 않는다", sens["why_not_added"])
        self.assertIn("oracle", sens["oracle_is_closest"])

    def test_c26_records_the_as_of_and_nature_gap(self):
        c26 = {d["id"]: d for d in RULES.payload["decisions"]}["C-26"]
        self.assertIn("분자와 분모는 기준일도 성질도 다르다", c26["recommendation"])
        self.assertEqual(self.o["oracle.contracted_revenue.fix57"]["as_of"], "2026-05-31")
        self.assertEqual(self.o["oracle.offbalance_B.v15"]["as_of"], "2026-09-02")
        g4 = next(p for p in self.res["oracle"]["factors"]["F9"]["calc"]["path"] if p["gate"] == "G4")
        self.assertEqual((g4["coverage"], g4["step"]), (2.552, 0))

    def test_private_correction_asymmetry_left_as_recorded(self):
        """규칙이 이미 `not_changed` 로 적어 둔 자리다 — 그대로 두고 점수가 갈릴 조건만 확인한다."""
        corr = RULES.payload["policies"]["f6"]["private_correction"]
        self.assertIn("not_changed", json.dumps(corr, ensure_ascii=False))
        # 지금은 run_rate 라 보정이 걸리지 않는다.
        self.assertEqual(self.o["anthropic.arr.v15"]["value"], 65000000000.0)
        self.assertIn("kind_note", self.o["anthropic.arr_prior.priv31"]["basis"])
        self.assertEqual(self.res["anthropic"]["factors"]["F6"]["score"], -4)

    # ---------------------------------------------------------------- S3 A 분담 8차
    def test_f7_no_longer_asserts_the_contracts_are_the_same(self):
        add = next(e for e in self.j["spacex-xai.F7"]["evidence"] if "Anthropic 클라우드 계약이 있다" in e)
        self.assertIn("동일성을 보존 원문이 주지 않는다", add)
        self.assertIn("`상대 미공시` 는 그대로 남는다", add)
        self.assertIn("Valor Equity Partners", add)
        self.assertIn("$11,290M", add)
        self.assertIn("로 뭉갤 수 없다", add)          # 옛 서술은 인용으로만 남고 뒤집힌다
        t = preserved("3cf9799:validation/offb-24/_raw/spcx-20260630.htm")
        self.assertIn("equipment lease agreement with Valor Equity Partners", t)
        self.assertIn("failed sale-leaseback transaction", t)
        self.assertIn("$ 2,039 million and $ 11,290 million", t)
        self.assertEqual(self.res["spacex-xai"]["factors"]["F7"]["score"], 0)

    def test_widened_raw_sweep_found_nothing_new(self):
        sweep = self.o["anthropic.cash.priv31"]["basis"]["checked_scope"]["counterparty_filings"]["widened_sweep"]
        self.assertIn("새로 나오는 사실이 없다", sweep["result"])
        self.assertEqual(len(sweep["files"]), 8)
        # 넓힌 범위가 실제로 커밋에 있고 건수가 재현된다.
        for ref, hits in sweep["files"].items():
            with self.subTest(ref=ref):
                t = preserved(ref)
                for who in ("Anthropic", "OpenAI", "xAI"):
                    if who in hits:
                        self.assertEqual(len(re.findall(who, t, re.I)), hits[who])
        self.assertIn("표지 조각은 있다", sweep["alphabet_correction"])

    def test_alphabet_cover_fragment_exists_but_is_only_a_cover(self):
        t = preserved("ff75add:validation/mcap-36-2026-09-11/raw/cover-alphabet-R1.htm.htm")
        self.assertIn("COVER PAGE", t)
        self.assertIn("Alphabet Inc.", t)
        self.assertEqual(len(re.findall("Anthropic", t, re.I)), 0)
        head = self.j["anthropic.F8.f8anth33"]["evidence"][0]
        self.assertIn("알파벳 제출본 본문이 저장소 어느 커밋에도 보존돼 있지 않다", head)
        self.assertIn("cover-alphabet-R1.htm.htm", head)
        self.assertEqual(self.res["anthropic"]["factors"]["F8"]["score"], -3)
        t5 = {x["id"]: x for x in RULES.payload["open_tensions"]}["TEN-RA5-01"]
        self.assertIn("알파벳 제출본", t5["trigger"])                       # 발동 조건은 그대로다

    def test_aws_anthropic_expansion_is_in_the_found_list(self):
        found = self.o["openai.net_cash.priv31"]["basis"]["checked_scope"]["counterparty_filings"]["found"]
        whats = [f["what"] for f in found]
        self.assertIn("anthropic 컴퓨트 약정(AWS 증액)", whats)
        self.assertIn("openai 컴퓨트 약정(AWS 몫)", whats)
        aws = next(f for f in found if f["what"] == "anthropic 컴퓨트 약정(AWS 증액)")
        self.assertFalse(aws["registered"])
        t = preserved("3cf9799:validation/offb-24/_raw/amzn-20260630.htm")
        self.assertIn("expansion of the strategic collaboration and existing multi-year commitment by more than "
                      "$ 100.0 billion over 10.0 years", t)

    def test_tag_strip_method_is_recorded(self):
        scope = self.o["anthropic.fcf_ttm.priv31"]["basis"]["checked_scope"]["preserved_release"]
        self.assertIn("어휘 건수의 재현 방법", scope)
        self.assertIn("git show <commit>:<path>", scope)
        self.assertIn("html.unescape", scope)

    def test_c03_succession_exception_gap_recorded(self):
        gap = {d["id"]: d for d in RULES.payload["decisions"]}["C-03"]["succession_exception_gap"]
        self.assertIn("엄밀히는 못 채운다", gap["what"])
        self.assertIn("점수는 바꾸지 않는다", gap["why_scores_unchanged"])
        self.assertIn("TEN-RA4-01", gap["how_it_is_handled"])
        ra4 = {x["id"]: x for x in RULES.payload["open_tensions"]}["TEN-RA4-01"]
        self.assertIn("승계 예외를 대신 메우는 자리", ra4["note"])
        for cid in ("anthropic", "meta", "alibaba", "openai"):
            with self.subTest(cid=cid):
                self.assertEqual(self.j[f"{cid}.F2"]["status"], "carried")

    # ---------------------------------------------------------------- S4 D 8차
    def test_auto_factor_block_leads_with_the_current_score(self):
        judgments_by_id = {j["judgment_id"]: j for j in self.ctx.judgments}
        reps = rc.replacements(self.ctx)
        base, _obs, _tr = load_baseline(self.ctx.run["baseline_id"])
        base_by_cid = {b["company_id"]: b for b in base["companies"]}
        seen = 0
        for c in self.results["companies"]:
            for f, fr in c["factors"].items():
                block = rc.evidence_block(fr, judgments_by_id, base_by_cid.get(c["company_id"], {}).get("evidence", {}).get(f, []),
                                          self.ctx.run["baseline_id"], c["company_id"], reps)
                if block is None or block["kind"] != "baseline_reference":
                    continue
                seen += 1
                with self.subTest(cid=c["company_id"], f=f):
                    first = block["lines"][0][1]
                    self.assertIn("이번 실행 점수는", first)
                    self.assertIn(f"{fr['score']:+d}", first)
                    self.assertIn("점수 근거가 아니다", first)
        self.assertGreaterEqual(seen, 2)                                 # anthropic·openai F6
        anth = rc.evidence_block(self.res["anthropic"]["factors"]["F6"], judgments_by_id,
                                 base_by_cid["anthropic"]["evidence"]["F6"], self.ctx.run["baseline_id"], "anthropic", reps)
        self.assertIn("이번 실행 점수는 -4", anth["lines"][0][1])
        self.assertIn("-3 (v1.5", anth["lines"][1][1])                   # 옛 수는 둘째 줄로 밀린다
        self.assertIn("이번 실행 점수는 -4", self.md)

    # ---------------------------------------------------------------- S5 종료 기록
    def test_round_closing_decision_recorded(self):
        closing = next(a for a in self.run_json["assumptions"] if "이 라운드는 여기서 끝난다" in a)
        self.assertIn("2026-09-17", closing)
        self.assertIn("FIX-59 만 하고 승인", closing)
        self.assertIn("6·7·8차 연속 점수 변경이 0", closing)
        self.assertIn("2026-11 재채점의 입력", closing)
        # 미결과 긴장이 실제로 그만큼 있다.
        pending = {d["id"] for d in RULES.payload["decisions"] if d["status"] == "pending"}
        # 2026-09-17 FIX-61 이 C-28 을 구현해 닫았다 — 나머지 넷은 그대로 미결이다.
        self.assertLessEqual({"C-23", "C-25", "C-26", "C-27"}, pending)
        self.assertNotIn("C-28", pending)
        tensions = {t["id"] for t in RULES.payload["open_tensions"]}
        self.assertLessEqual({"TEN-RA5-01", "TEN-RA5-02"}, tensions)
        self.assertTrue(all(t["recheck_at"] == "2026-11" for t in RULES.payload["open_tensions"]))


if __name__ == "__main__":
    unittest.main()
