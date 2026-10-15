# 규칙 v3.0 층·사업 판단의 생성·수정·제안·번복 경로와 init 의 단위 전환(계획 S5)을 잠근다
from __future__ import annotations

import json
import shutil
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard import engine, stages  # noqa: E402
from scorecard.schema import SchemaError, load_json_strict  # noqa: E402
from tests.test_collect_stage import SLUG, Sandbox  # noqa: E402
from tests.test_evidence_three_way import DOWN, UP  # noqa: E402
from tests.test_v20_judge import DAY, V20Base  # noqa: E402

TEXT = {"evidence": ["층 판정을 이번 실행의 근거로 매겼다"], "evidence_up": UP, "evidence_down": DOWN}
PATHS = {"leap": "first", "adaptation": "adopted", "standards": []}
CP = {"strategy": "자체 소프트웨어를 무료로 주고 칩으로 거둔다", "counterparty": "AMD", "counterparty_present": "yes",
      "revenue_model": "mechanism", "imitation": "costly", "door_closed_at": None,
      "acceleration": {"metric": "데이터센터 매출", "tier": "b", "basis": "yoy_quarter", "prior_multiple": 1.4, "current_multiple": 1.5,
                       "delayed": "no", "evidence_ids": ["EV-nvidia-001"]}}
V21 = "ai-scorecard-2026-10-v21"


class V30Base(V20Base):
    """규칙 v3.0 샌드박스 실행. 기준선에서 만들어 ①②③ 회사 단위 판단은 init 이 옮기지 않는다."""

    RULE = "v3.0"

    def items(self) -> list[dict]:
        return load_json_strict(self.jpath)["items"]

    def unit(self, factor: str, layer: str | None = None, business: str | None = None) -> dict | None:
        return next((j for j in self.items() if (j["company_id"], j["factor"], j.get("layer"), j.get("business"))
                     == ("nvidia", factor, layer, business)), None)


class InitUnitSwitchTest(V30Base):
    def test_company_level_f1_to_f3_are_not_carried(self):
        factors = {(j["company_id"], j["factor"]) for j in self.items()}
        for cid in ("nvidia", "openai"):
            self.assertFalse({(cid, f) for f in ("F1", "F2", "F3")} & factors)
            self.assertTrue({(cid, f) for f in ("F4", "F5", "F7", "F8", "F9")} <= factors)
        run = load_json_strict(self.box.run_dir / "run.json")
        self.assertTrue(any("F1, F2, F3 를 층·사업마다 매긴다" in a for a in run["assumptions"]))


class CreateAndReviseTest(V30Base):
    def test_judge_creates_then_revises_a_layer_judgment(self):
        out = self.judge("nvidia", "F2", {**PATHS, **TEXT}, layer="chip_design")
        self.assertTrue(out["created"])
        self.assertIsNone(out["previous"])
        j = self.unit("F2", "chip_design")
        self.assertEqual((j["judgment_id"], j["kind"], j["score"], j["status"], j["reviewer"], j["reviewed_at"]),
                         ("nvidia.F2.chip_design", "layer_paths", None, "new", "판단자", DAY))
        self.assertEqual(j["inputs"], PATHS)
        self.assertNotIn("revision_history", j)
        out = self.judge("nvidia", "F2", {"leap": "second"}, layer="chip_design")
        self.assertFalse(out["created"])
        j = self.unit("F2", "chip_design")
        self.assertEqual(j["inputs"]["leap"], "second")
        self.assertEqual(j["revision_history"][-1]["previous"]["inputs"]["leap"], "first")
        # 다른 층은 따로 만든다.
        self.judge("nvidia", "F2", {"adaptation": "beta", "standards": [], **TEXT}, layer="cloud")
        self.assertEqual(sorted(j["layer"] for j in self.items() if j["factor"] == "F2" and j["company_id"] == "nvidia"),
                         ["chip_design", "cloud"])

    def test_refusals_leave_the_file_untouched(self):
        before = self.jpath.read_bytes()
        cases = [
            (dict(company_id="nvidia", factor="F2", changes={**PATHS, **TEXT}), "nvidia F2 판단이 없다"),
            (dict(company_id="nvidia", factor="F2", changes=TEXT, layer="cloud"), "아직 없어 근거만 바꾸거나"),
            (dict(company_id="nvidia", factor="F2", changes={**PATHS, **TEXT}, layer="clould"), "층 'clould'"),
            (dict(company_id="nvidia", factor="F2", changes={**PATHS, **TEXT}, layer="cloud"), "알 수 없는 키 \\['leap'\\]"),
            (dict(company_id="nvidia", factor="F4", changes={**PATHS, **TEXT}, layer="cloud"), "판단이 없다|고칠 수 없는 키"),
            (dict(company_id="nvidia", factor="F2", changes={"adaptation": "adopted", "standards": [], "evidence": ["판정"]}, layer="cloud"),
             "세 칸"),
        ]
        for kw, pattern in cases:
            with self.subTest(pattern=pattern), self.assertRaisesRegex(SchemaError, pattern):
                stages.revise_judgment(SLUG, reason="시험", by="판단자", revised_at=DAY, **kw)
            self.assertEqual(self.jpath.read_bytes(), before, "거부되면 judgments.json 은 한 바이트도 바뀌지 않는다")

    def test_business_judgment_key(self):
        holdings_cells = {layer: {"cell": "none", "evidence_ids": []} for layer in
                          ("power", "foundry", "chip_design", "systems", "cloud", "dev_platform", "data_platform", "model", "application",
                           "user_platform", "device")}
        holdings_cells["chip_design"] = {"cell": "sold", "evidence_ids": ["EV-nvidia-001"]}
        holdings = {"cells": holdings_cells, "currency": "USD", "non_ai_margin": "not_applicable",
                    "revenue_lines": [{"line": "data_center", "label": "Data Center", "amount": 100, "period": "2025Q3~2026Q2",
                                       "layer": "chip_design", "non_ai": "no", "evidence_ids": ["EV-nvidia-001"]}]}
        self.judge("nvidia", "F4", {**holdings, **TEXT})
        business = {"components": [{"name": "Data Center", "layer": "chip_design", "customer": "work", "lines": ["data_center"],
                                    "market": None, "ai_monetized": "partial"}],
                    "participant": "partial", "switching": "stay_unmeasured", "pricing": "no_change", "substitutes": "gap_remains"}
        out = self.judge("nvidia", "F1", {**business, **TEXT}, business="data_center")
        self.assertEqual(out["judgment_id"], "nvidia.F1.data_center")
        bad = json.loads(json.dumps(business))
        bad["components"][0]["lines"] = ["gaming"]
        with self.assertRaisesRegex(SchemaError, "매출 줄 'gaming' 가 같은 회사 ④ 보유표에 없다"):
            self.judge("nvidia", "F1", {**bad, **TEXT}, business="gaming")


class CreateByProposalTest(V30Base):
    def propose_cp(self, layer: str = "chip_design", **kw) -> dict:
        return stages.add_proposal(SLUG, company_id="nvidia", factor="F3", layer=layer, changes=CP,
                                   evidence_after=TEXT["evidence"], evidence_up_after=UP, evidence_down_after=DOWN,
                                   reason="층 판정", evidence_ids=["EV-nvidia-001"], **kw)

    def test_accept_creates_and_undo_restores_bytes(self):
        original = self.jpath.read_bytes()
        p = self.propose_cp()
        self.assertEqual((p["layer"], p["before"]), ("chip_design", None))
        with self.assertRaisesRegex(SchemaError, "nvidia F3 chip_design 에 결정 전 제안이 이미 있다"):
            self.propose_cp()
        self.propose_cp(layer="cloud")   # 다른 층은 따로 제안한다
        out = stages.decide_proposal(SLUG, p["proposal_id"], accept=True, by="판단자")
        self.assertTrue(out["judgment"]["created"])
        j = self.unit("F3", "chip_design")
        self.assertEqual((j["kind"], j["status"], j["evidence_ids"]), ("layer_cp", "new", ["EV-nvidia-001"]))
        applied = load_json_strict(self.paths.proposals)["items"][0]["applied"]
        self.assertIsNone(applied["previous"])
        stages.undo_proposal(SLUG, p["proposal_id"], by="판단자")
        self.assertEqual(self.jpath.read_bytes(), original, "만든 판단을 지우면 반영 전 파일로 돌아간다")
        self.assertEqual(load_json_strict(self.paths.proposals)["items"][0]["status"], "pending")

    def test_created_meanwhile_makes_the_proposal_stale(self):
        p = self.propose_cp()
        self.judge("nvidia", "F3", {**CP, **TEXT}, layer="chip_design")
        with self.assertRaisesRegex(SchemaError, "판단이 바뀌었다"):
            stages.decide_proposal(SLUG, p["proposal_id"], accept=True, by="판단자")

    def test_company_level_proposal_still_needs_an_existing_judgment(self):
        with self.assertRaisesRegex(SchemaError, "nvidia F2 판단이 없다"):
            stages.add_proposal(SLUG, company_id="nvidia", factor="F2", changes=PATHS, evidence_after=TEXT["evidence"],
                                reason="r", evidence_ids=["EV-nvidia-001"])


class SummaryUnitTest(V30Base):
    def test_summary_carries_unit_for_layer_judgments_and_proposals(self):
        self.judge("nvidia", "F2", {"adaptation": "beta", "standards": [], **TEXT}, layer="cloud")
        self.judge("nvidia", "F2", {**PATHS, **TEXT}, layer="chip_design")
        stages.add_proposal(SLUG, company_id="nvidia", factor="F3", layer="cloud", changes=CP, evidence_after=TEXT["evidence"],
                            evidence_up_after=UP, evidence_down_after=DOWN, reason="층 판정", evidence_ids=["EV-nvidia-001"])
        s = stages.summary(SLUG)
        f2 = [(j["company_id"], j["unit"]) for j in s["judgments"] if j["factor"] == "F2"]
        self.assertEqual(f2, [("nvidia", "chip_design"), ("nvidia", "cloud")])
        self.assertTrue(all(j["unit"] is None for j in s["judgments"] if j["factor"] != "F2"))
        p = s["proposals"][0]
        self.assertEqual((p["unit"], p["before"]["kind"], p["stale"]), ("cloud", None, False))


class CliTest(V30Base):
    def test_judge_with_layer_prints_created(self):
        path = self.box.dir / "paths.json"
        path.write_text(json.dumps({**PATHS, **TEXT}, ensure_ascii=False), encoding="utf-8")
        out = self.cli("judge", SLUG, "--company", "nvidia", "--factor", "F2", "--layer", "chip_design", "--json", path,
                       "--reason", "층 판정", "--by", "판단자")
        self.assertIn("judge: nvidia.F2.chip_design (layer_paths) 생성", out)
        self.assertIn("inputs: null →", out)


class FromRunTest(unittest.TestCase):
    """승인된 v21 실행을 샌드박스로 복사해 init --from-run --rule v3.0 한다."""

    def setUp(self) -> None:
        self.box = Sandbox(init=False)
        self.addCleanup(self.box.close)
        src = ROOT / "output" / V21
        if not src.is_dir():
            self.skipTest(f"{V21} 실행이 없다")
        shutil.copytree(src, engine.run_dir(V21))

    def test_v21_to_v30_drops_company_level_f1_to_f3_only(self):
        prior = {(j["company_id"], j["factor"]): j for j in load_json_strict(engine.run_dir(V21) / "judgments.json")["items"]}
        stages.init_run("ai-scorecard-2026-10-v30t", from_run=V21, rule_version="v3.0", companies=["alphabet", "tsmc"])
        new = {(j["company_id"], j["factor"]): j for j in load_json_strict(engine.run_dir("ai-scorecard-2026-10-v30t") / "judgments.json")["items"]}
        for cid in ("alphabet", "tsmc"):
            self.assertFalse({(cid, f) for f in ("F1", "F2", "F3")} & set(new))
            for f in ("F4", "F5"):
                self.assertEqual(new[(cid, f)]["status"], "carried", f"{cid} {f} 는 v3.0 판정 재료가 아니라 승계로 넘어온다")
            for f in ("F7", "F8", "F9"):
                self.assertEqual(new[(cid, f)], prior[(cid, f)], f"{cid} {f} 는 한 글자도 바뀌지 않는다")
        engine.load_context("ai-scorecard-2026-10-v30t")   # 이어받은 입력이 v3.0 검증을 통과한다
        confirmed = {e["evidence_id"] for e in load_json_strict(engine.run_dir(V21) / "evidence" / "evidence.json")["items"]
                     if e["status"] == "confirmed"}
        carried = {e["evidence_id"] for e in load_json_strict(engine.run_dir("ai-scorecard-2026-10-v30t") / "evidence" / "evidence.json")["items"]}
        self.assertTrue(any(e.startswith("EV-meta-") for e in confirmed), "v21 에 고르지 않은 회사의 확정 근거가 있어야 검사가 뜻이 있다")
        self.assertLessEqual(confirmed, carried, "층 판단이 견줄 다른 회사의 확정 근거도 옮긴다")
        assumptions = load_json_strict(engine.run_dir("ai-scorecard-2026-10-v30t") / "run.json")["assumptions"]
        self.assertTrue(any("diff 로 견주지 못하므로 모든 기업을 다시 매기고" in a for a in assumptions))
        self.assertFalse(any("diff 로 확인한다" in a for a in assumptions), "diff 가 거부하는 실행에 diff 를 안내하지 않는다")
        from scorecard.compare import compare_runs
        with self.assertRaisesRegex(SchemaError, "diff 는 층·사업 단위 규칙\\(v3.0 이상\\) 실행을 아직 견주지 못한다: ai-scorecard-2026-10-v30t"):
            compare_runs("ai-scorecard-2026-10-v30t", V21)

    def test_layer_judgment_that_no_longer_fits_the_rule_is_not_carried(self):
        # 2026-10-15: 개발 플랫폼이 벤치마크 없는 층이 되자 그 층 판단의 leap 이 모양 검사에 걸려 이어받은 실행이 열리지 않았다
        stages.init_run("ai-scorecard-2026-10-v30t", from_run=V21, rule_version="v3.0", companies=["alphabet", "tsmc"])
        jpath = engine.run_dir("ai-scorecard-2026-10-v30t") / "judgments.json"
        payload = load_json_strict(jpath)
        payload["items"].append({"judgment_id": "alphabet.F2.dev_platform", "company_id": "alphabet", "factor": "F2",
                                 "layer": "dev_platform", "kind": "layer_paths", "score": None,
                                 "inputs": {"leap": "unknown", "adaptation": "adopted", "standards": []}, **TEXT,
                                 "reviewer": "agent", "reviewed_at": DAY, "status": "new"})
        jpath.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        stages.init_run("ai-scorecard-2026-10-v30t2", from_run="ai-scorecard-2026-10-v30t")
        d = engine.run_dir("ai-scorecard-2026-10-v30t2")
        ids = {j["judgment_id"] for j in load_json_strict(d / "judgments.json")["items"]}
        self.assertNotIn("alphabet.F2.dev_platform", ids)
        self.assertIn("alphabet.F4", ids, "모양에 맞는 판단은 그대로 옮긴다")
        notes = load_json_strict(d / "run.json")["assumptions"]
        self.assertTrue(any("판정 재료 모양에 맞지 않는 판단 1건(alphabet.F2.dev_platform)" in a for a in notes))
        engine.load_context("ai-scorecard-2026-10-v30t2")


if __name__ == "__main__":
    unittest.main()
