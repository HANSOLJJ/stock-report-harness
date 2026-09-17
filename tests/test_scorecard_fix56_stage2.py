# FIX-56 2단계 — 5차 리뷰 A 분담·C 반영(하네스 표기 같은 잣대 · 가정문 정정 · 생성 코드)을 고정한다
from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard import render_common as rc  # noqa: E402
from scorecard.engine import load_context  # noqa: E402
from scorecard.render_md import render_draft  # noqa: E402
from scorecard.rules import load_rules  # noqa: E402
from scorecard.schema import SchemaError, validate_rules  # noqa: E402
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

    def test_totals_same_as_stage1(self):
        self.assertEqual({c: r["total"] for c, r in self.res.items()},
                         {"alphabet": 15, "amazon": 15, "meta": 15, "microsoft": 14, "tsmc": 10, "anthropic": 10,
                          "spacex-xai": 9, "nvidia": 9, "apple": 8, "alibaba": 7, "palantir": 6, "tesla": 5,
                          "openai": 2, "oracle": 2})

    # ---------------------------------------------------------------- S1 하네스 표기
    def test_harness_mark_is_applied_to_every_model_comparison(self):
        """자사 판단 하나에만 대면 같은 잣대가 아니다 — 네 줄이 같은 표기를 단다."""
        marked = {jid: [e for e in j["evidence"] if "하네스 미표기" in e]
                  for jid, j in self.j.items() if any("하네스 미표기" in e for e in j["evidence"])}
        self.assertEqual(sorted(marked), ["alibaba.F2", "anthropic.F2", "meta.F2", "openai.F2"])
        for jid, frag in (("meta.F2", "Tau3-Bench Banking 52%로 전 모델 1위"),
                          ("alibaba.F2", "HLE 43.6%로 프론티어 미달"),
                          ("openai.F2", "FrontierMath Tier 4 v2 97.6%(Fable 5.1 87.8%)")):
            with self.subTest(jid=jid):
                line = marked[jid][0]
                self.assertIn(frag, line)                                  # 원 문장은 그대로 두고 뒤에 붙인다
                self.assertIn("비교는 같은 하네스끼리만", line)
                self.assertIn("하네스 사실을 새로 판정하지 않았고 점수는 그대로다", line)
                self.assertIn("SRC-v15-rule", self.j[jid]["source_ids"])   # 인용한 문서를 출처로 든다
                self.assertIn("SRC-v15-md", self.j[jid]["source_ids"])
        self.assertIn("meta.F2·alibaba.F2·openai.F2", " ".join(self.j["anthropic.F2"]["evidence"]))
        self.assertIn("하네스 미표기", self.md)

    def test_f2_scores_unchanged(self):
        for cid, want in (("meta", 4), ("alibaba", 4), ("openai", 4), ("anthropic", 5)):
            with self.subTest(cid=cid):
                self.assertEqual(self.res[cid]["factors"]["F2"]["score"], want)

    # ---------------------------------------------------------------- S2·S3 가정문과 검색 범위
    def test_credit_assumption_states_the_real_reason(self):
        a = " ".join(self.run_json["assumptions"])
        self.assertIn("전에 적은 `인용할 보존 원문·source_id 가 없어서` 는 **더 이상 성립하지 않는다**", a)
        self.assertIn("SRC-ANTHROPIC-SERIESH-2026", a)
        self.assertIn("The facility remains undrawn at close", a)
        self.assertIn("approximately", a)
        self.assertIn("C-20 경로라 G3", a)

    def test_private_input_assumption_names_the_company_release(self):
        a = " ".join(self.run_json["assumptions"])
        self.assertIn("anthropic.arr_prior.priv31", a)
        self.assertIn("이해당사자의 감사받지 않은 1차 발표가 F6 P3 입력에 들어가 있다", a)
        self.assertEqual(self.o["anthropic.arr_prior.priv31"]["source_id"], "SRC-ANTHROPIC-SERIESH-2026")
        self.assertEqual(self.o["anthropic.arr_prior.priv31"]["status"], "legacy_unverified")

    def test_search_scope_now_covers_credit_vocabulary(self):
        for metric in ("fcf_ttm", "cash", "net_cash", "debt_ebitda", "operating_margin_ttm"):
            with self.subTest(metric=metric):
                oai = self.o[f"openai.{metric}.priv31"]["basis"]["checked_scope"]["preserved_release"]
                self.assertIn("revolving credit facility to approximately $4.7 billion", oai)
                self.assertIn("The facility remains undrawn at close", oai)
                self.assertIn("그래도 여신 관측을 만들지 않았다", oai)
                ant = self.o[f"anthropic.{metric}.priv31"]["basis"]["checked_scope"]["preserved_release"]
                self.assertIn("`credit` · `facility` · `revolving` · `undrawn` · `unused` · `borrow` · `loan` · `syndicate` **전부 0건**", ant)
                self.assertIn("원시 파일 7건 · 태그를 걷은 본문 6건", ant)
        self.assertNotIn("undrawn_credit", {o["metric"] for o in load("observations.json")["items"]
                                            if o["company_id"] in ("openai", "anthropic")})

    # ---------------------------------------------------------------- S4 라벨 단정
    def test_palantir_lease_matches_apple_wording(self):
        pal = self.o["palantir.lease_liabilities.nc37"]["basis"]
        app = self.o["apple.lease_liabilities.nc37"]["basis"]
        phrase = "**데이터셋의 표준 태그 결측이지 발행사 미공시 확인이 아니다**"
        self.assertIn(phrase, pal["why"])
        self.assertIn(phrase, app["why"])
        self.assertNotIn("발행사가 따로 공시하지 않는다", pal["why"])
        self.assertIn("발행사가 따로 공시하지 않는다", pal["why_superseded"])     # 지우지 않고 취소선으로 남긴다
        self.assertEqual(pal["label_correction"]["is"], "unverified")

    # ---------------------------------------------------------------- S5 생성 코드와 표시
    def test_new_run_would_carry_the_conflict_notice(self):
        """데이터만 고치면 다음 실행에서 다시 빈다 — 생성 코드가 고지를 들어야 한다."""
        text = (SRC / "stages.py").read_text(encoding="utf-8")
        self.assertIn("채점규칙 384행 이해상충 고지", text)
        self.assertNotIn('"conflict_of_interest": None', text)
        registered = {s["source_id"]: s for s in self.ctx.sources["items"]}
        self.assertIn("채점규칙 384행", registered["SRC-v15-rule"]["conflict_of_interest"])

    def test_third_party_recheck_is_split_by_kind(self):
        kinds: dict[str, list[str]] = {}
        for t in RULES.payload["open_tensions"]:
            if t.get("third_party_recheck"):
                kinds.setdefault(t["third_party_recheck"], []).append(t["id"])
        # 2026-09-16 FIX-57 2단계: TEN-RA4-01 이 meta·alibaba·openai 의 F2 를 받으면서 partial 로 옮겨 갔다
        # — 비 Claude 재판정 약속은 anthropic.F2 하나에만 걸린다. 갈래가 사실을 따라 움직인다는 것이 요점이다.
        # 2026-09-17 FIX-58 2단계: TEN-RA5-01(anthropic.F8 근거 확인 불가)이 committed 로 들어왔다 — Anthropic 점수다.
        # 2026-09-17 FIX-59: TEN-RA5-02(openai.F9 경로)가 committed 로 들어왔다 — 비 Claude 판정자가 이미 반대 의견을 냈다.
        self.assertEqual(sorted(kinds["committed"]),
                         ["TEN-RA5-01", "TEN-RA5-02", "TEN-RC-02", "TEN-RC-03", "TEN-RC3-01"])
        self.assertEqual(sorted(kinds["partial"]), ["TEN-RA4-01", "TEN-RC4-01"])
        self.assertEqual(sorted(kinds["recommended"]), ["TEN-RA3-01", "TEN-RC-05", "TEN-RC3-03"])
        lines = rc.conflict_lines(self.ctx)
        head = next(x for x in lines if "제3자 재검토 약속" in x)
        self.assertIn("**확정**된 긴장 5건", head)
        partial = next(x for x in lines if "일부만 확정" in x)
        self.assertIn("TEN-RC4-01(anthropic.F3, 2026-11)", partial)        # 셋 중 anthropic 만
        self.assertIn("TEN-RA4-01(anthropic.F2, 2026-11)", partial)        # 넷 중 anthropic 만
        rec = next(x for x in lines if "권장일 뿐 약속이 아닌 것" in x)
        self.assertIn("3건", rec)
        for line in lines:
            self.assertIn(line if line.startswith("  - ") else f"- {line}", self.md)

    def test_schema_rejects_undeclared_or_wrong_third_party_scope(self):
        bad = copy.deepcopy(RULES.payload)
        t = next(x for x in bad["open_tensions"] if x["id"] == "TEN-RC-02")
        del t["third_party_recheck"]
        with self.assertRaises(SchemaError):
            validate_rules(bad)                                            # rechecker 가 말하면 선언이 필수다
        bad2 = copy.deepcopy(RULES.payload)
        t2 = next(x for x in bad2["open_tensions"] if x["id"] == "TEN-RC4-01")
        t2["third_party_scope"] = list(t2["judgment_ids"])                 # 전부면 partial 이 아니라 committed 다
        with self.assertRaises(SchemaError):
            validate_rules(bad2)

    def test_g2_reason_label_is_distinguishable_from_an_observation_id(self):
        # 이 칸을 실제로 찍는 회사는 anthropic 하나다 — openai 는 G1 에서 이미 하한 -4 라 G2 를 지나가지 않는다.
        g2 = next(p for p in self.res["anthropic"]["factors"]["F9"]["calc"]["path"]
                  if p["gate"] == "G2" and p.get("result") == "not_disclosed")
        self.assertEqual(g2["reason_id"], "reason:anthropic.fcf_not_disclosed")
        self.assertEqual(g2["reason_observation_id"], "anthropic.fcf_ttm.priv31")
        self.assertIn(g2["reason_observation_id"], self.res["anthropic"]["factors"]["F9"]["observation_ids"])
        self.assertNotIn(g2["reason_id"], self.o)                          # 관측으로 오인될 id 가 아니다
        self.assertNotIn("anthropic.fcf_not_disclosed", self.o)
        for cid in ("anthropic", "openai"):
            with self.subTest(cid=cid):
                self.assertEqual(self.j[f"{cid}.F9"]["inputs"]["fcf_not_disclosed_reason"],
                                 f"reason:{cid}.fcf_not_disclosed")
        self.assertIn('f"reason:{cid}.fcf_not_disclosed"', (SRC / "calc_f9.py").read_text(encoding="utf-8"))
        self.assertIn('"reason:openai.fcf_not_disclosed"', (SRC / "baseline_import.py").read_text(encoding="utf-8"))

    def test_amazon_covenant_sentence_is_narrowed(self):
        note = self.o["amazon.undrawn_credit.fix54"]["basis"]["conditions_note"]
        self.assertIn("**여신 시설의** 재무 약정(covenant) 문장은 원문에 없다", note)
        self.assertIn("We are not subject to any financial covenants under the Notes.", note)

    def test_tsmc_search_terms_widened_without_changing_the_conclusion(self):
        o = self.o["tsmc.undrawn_credit.fix54"]
        self.assertIn("NT$ 438.7 million", o["basis"]["why"])
        self.assertIn("`letters of credit` 2", o["basis"]["why"])
        self.assertIn("unused tax losses", o["basis"]["why"])
        self.assertIn("**결론은 그대로다 — 확정 미인출 여신은 확인되지 않았다.**", o["basis"]["why"])
        self.assertEqual((o["value"], o["missing_type"]), (None, "unverified"))

    def test_palantir_offbalance_evidence_widened(self):
        why = self.o["palantir.offbalance_note.v15"]["basis"]["label_correction"]["why"]
        self.assertIn("LongTermPurchaseCommitmentAmount", why)
        self.assertIn("US$1,950,000,000", why)
        self.assertIn("기간형 사실(start 2023-09-01 · end 2023-09-30)이라 기준일 잔고가 아니다", why)
        self.assertIn("US$707,000,000,000", why)
        self.assertTrue(self.o["palantir.offbalance_note.v15"]["value"].startswith("미확인"))
        self.assertEqual(self.o["alphabet.offbalance_note.v15"]["value"], "총 약정 $707B")

    def test_pending_decisions_say_whether_code_reads_them(self):
        d = {x["id"]: x for x in RULES.payload["decisions"]}
        self.assertEqual(d["C-11"]["implementation_status"]["verdict"], "declared_without_consumer")
        self.assertEqual(d["C-13"]["implementation_status"]["verdict"], "branch_not_reached_in_parameters_mode")
        # C-04 의 기존 기록은 덮지 않고 행 번호와 코드 주석 사실만 보탰다.
        self.assertEqual(d["C-04"]["implementation_status"]["verdict"], "already_implemented")
        self.assertIn("같은 사실을 코드 주석으로도 남겼다", d["C-04"]["implementation_status"]["include_v15_reads_but_does_not_use"])
        f9 = (SRC / "calc_f9.py").read_text(encoding="utf-8")
        self.assertIn("두 갈래가 같은 산식을 쓴다", f9)
        self.assertIn("bands 모드에서만 실행된다", (SRC / "calc_f6.py").read_text(encoding="utf-8"))
        # C-11 은 정말로 읽는 코드가 없다 — 선언만 있는 상태를 검사로 고정한다.
        for path in SRC.glob("*.py"):
            self.assertNotIn('"C-11"', path.read_text(encoding="utf-8"), msg=str(path))

    def test_f3_range_note_explains_the_gap(self):
        note = RULES.payload["factors"]["F3"]["range_note"]
        self.assertIn("사다리가 낼 수 있는 값", note)
        self.assertIn("통과점 0", note)
        self.assertEqual(sorted({c["factors"]["F3"]["score"] for c in self.results["companies"]}), [2, 3])
        self.assertEqual(RULES.payload["factors"]["F3"]["range"], [1, 5])


if __name__ == "__main__":
    unittest.main()
