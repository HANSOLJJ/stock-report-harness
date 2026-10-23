# 실적 반영 실행의 갱신 범위와 막는 검사(계획 U3) — 범위 계산, 범위 재판단, 실적 감지, 판단 나이, research 연결, scope 선언을 잠근다
from __future__ import annotations

import copy
import json
import shutil
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard import engine, evidence_lib, stages, update_scope  # noqa: E402
from scorecard.paths import run_paths  # noqa: E402
from scorecard.rules import load_rules  # noqa: E402
from scorecard.schema import SchemaError, load_json_strict, validate_companies, write_json  # noqa: E402
from scorecard.validate import rejudge_findings  # noqa: E402
from tests.test_collect_stage import Sandbox  # noqa: E402

V30FULL = "ai-scorecard-2026-10-v30full"
NEW = "ai-scorecard-2026-10-q3t"
AS_OF = "2026-10-22"
UPDATED = ["alphabet", "spacex-xai"]
REGISTRY = validate_companies(load_json_strict(ROOT / "scorecard" / "companies.json"))
SEC = sorted(c for c, rec in REGISTRY.items() if rec.get("cik"))


def filing(cid: str, form: str, day: str, items: list[str] | None = None, *, title_only: bool = False) -> dict:
    c = {"candidate_id": f"edgar:{cid}-{form}-{day}", "company_id": cid, "kind": "filing", "form": form, "filed_at": day,
         "title": f"{form} {day}" + (f" · Items {', '.join(items)}" if items else ""), "url": f"https://www.sec.gov/{cid}/{day}"}
    if not title_only:
        c["items"] = list(items or [])
    return c


class ScopeBase(unittest.TestCase):
    def setUp(self) -> None:
        self.box = Sandbox(init=False)
        self.addCleanup(self.box.close)
        src = ROOT / "output" / V30FULL
        if not src.is_dir():
            self.skipTest(f"{V30FULL} 실행이 없다")
        shutil.copytree(src, engine.run_dir(V30FULL))
        stages.init_run(NEW, from_run=V30FULL, rule_version="v3.1", as_of=AS_OF, title="3분기 실적 반영",
                        update_companies=UPDATED, update_reason="Alphabet·SpaceX-xAI 3분기 실적")
        self.d = engine.run_dir(NEW)

    def ctx(self, **over) -> SimpleNamespace:
        d = self.d
        ev = d / "evidence" / "evidence.json"
        tr = d / "triggers.json"
        base = dict(slug=NEW, run=load_json_strict(d / "run.json"), rules=load_rules("v3.1"), companies=REGISTRY,
                    judgments=load_json_strict(d / "judgments.json")["items"],
                    evidence=load_json_strict(ev)["items"] if ev.is_file() else None,
                    triggers=load_json_strict(tr)["items"] if tr.is_file() else None)
        base.update(over)
        return SimpleNamespace(**base)

    def rejudge(self, judgments: list[dict], ids: set[str]) -> list[dict]:
        """ids 의 판단을 이번 실행에서 다시 매긴 것처럼 바꾼다(검토일을 생성일로)."""
        created = load_json_strict(self.d / "run.json")["created_at"]
        out = copy.deepcopy(judgments)
        for j in out:
            if j["judgment_id"] in ids:
                j["reviewed_at"] = created
        return out

    QUAL = {"F1", "F2", "F3", "F4", "F5", "F7", "F8"}

    def qual(self, judgments: list[dict], pred) -> set[str]:
        """범위 판단 ID. 갱신 회사는 ⑥⑨ 까지 전 항목, 그 밖은 정성 항목만(2026-10-23)."""
        return {j["judgment_id"] for j in judgments if (j["factor"] in self.QUAL or j["company_id"] in UPDATED) and pred(j)}

    def qual_only(self, judgments: list[dict], pred) -> set[str]:
        return {j["judgment_id"] for j in judgments if j["factor"] in self.QUAL and pred(j)}

    def write_candidates(self, items: list[dict], fetched: dict[str, str] | None = None) -> None:
        payload = {"schema": "scorecard.candidates/1", "run_id": NEW, "window": {"since": "2026-04-25", "until": AS_OF},
                   "filings_fetched_at": {c: f"{AS_OF}T09:00:00Z" for c in SEC} if fetched is None else fetched,
                   "items": items}
        path = run_paths(NEW).candidates
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


class ComputeScopeTest(ScopeBase):
    def test_updated_companies_only_by_default(self):
        sc = update_scope.compute(self.ctx())
        self.assertEqual(sc.updated, UPDATED)
        self.assertEqual((sc.touched, sc.extra), ({}, {}))
        self.assertEqual(sc.why("alphabet", "F4"), "갱신 회사")
        self.assertIsNone(sc.why("anthropic", "F7"))

    def test_new_confirmed_evidence_touches_its_company_and_factors(self):
        ctx = self.ctx()
        new = {"evidence_id": "EV-anthropic-901", "company_id": "anthropic", "factors": ["F7", "F6"], "status": "confirmed"}
        cand = {"evidence_id": "EV-meta-901", "company_id": "meta", "factors": ["F3"], "status": "candidate"}
        old = next(e for e in ctx.evidence if e["company_id"] == "tesla" and e["status"] == "confirmed")
        sc = update_scope.compute(self.ctx(evidence=ctx.evidence + [new, cand]))
        self.assertEqual(sc.touched, {("anthropic", "F7"): ["EV-anthropic-901"]}, "후보·이어받은 확정 근거·정성 항목 밖(F6)은 범위가 아니다")
        self.assertIn(old["evidence_id"], {e["evidence_id"] for e in ctx.evidence})
        self.assertTrue(sc.why("anthropic", "F7").startswith("새 근거·트리거가 닿음 — EV-anthropic-901"))

    def test_candidate_confirmed_in_this_run_counts_as_new(self):
        ctx = self.ctx()
        prior = load_json_strict(engine.run_dir(V30FULL) / "evidence" / "evidence.json")["items"]
        target = next(e for e in prior if e["company_id"] == "oracle" and e["status"] == "confirmed")
        evidence = copy.deepcopy(ctx.evidence)
        # 이전 실행에서 후보였던 근거를 이번에 확정한 상황을 만든다.
        prior_path = engine.run_dir(V30FULL) / "evidence" / "evidence.json"
        payload = load_json_strict(prior_path)
        for e in payload["items"]:
            if e["evidence_id"] == target["evidence_id"]:
                e["status"] = "candidate"
        write_json(prior_path, payload)
        sc = update_scope.compute(self.ctx(evidence=evidence))
        self.assertIn(target["evidence_id"], sum(sc.touched.values(), []))

    def test_newly_fired_trigger_touches_recheck_factors(self):
        ctx = self.ctx()
        triggers = copy.deepcopy(ctx.triggers)
        t = next(t for t in triggers if t["company_id"] == "tesla" and t["status"] == "watching")
        t["status"] = "fired"
        already = next(t for t in triggers if t["status"] == "fired")
        sc = update_scope.compute(self.ctx(triggers=triggers))
        want = {(t["company_id"], f) for f in (t["recheck"]["factors"] or t["factors"]) if f not in ("F6", "F9")}
        self.assertTrue(want)
        self.assertTrue(want <= set(sc.touched))
        self.assertFalse(any(already["trigger_id"] in refs for refs in sc.touched.values()), "이전 실행에서 이미 발동한 트리거는 새것이 아니다")

    def test_declared_extra(self):
        run = load_json_strict(self.d / "run.json")
        run["update_scope"]["extra"] = [{"company_id": "meta", "factor": "F3", "reason": "Alphabet ③ 의 새 잣대", "declared_at": AS_OF}]
        sc = update_scope.compute(self.ctx(run=run))
        self.assertEqual(sc.why("meta", "F3"), "선언한 추가 항목 — Alphabet ③ 의 새 잣대")


class RejudgeInScopeTest(ScopeBase):
    def test_flags_exactly_the_scope_judgment_left_unchanged(self):
        judgments = self.ctx().judgments
        scope_ids = self.qual(judgments, lambda j: j["company_id"] in UPDATED)
        self.assertGreater(len(scope_ids), 20)
        left = sorted(scope_ids)[len(scope_ids) // 2]
        found = rejudge_findings(self.ctx(judgments=self.rejudge(judgments, scope_ids - {left})))
        self.assertEqual([jid for jid, _ in found], [left])
        self.assertIn("이전 실행 ai-scorecard-2026-10-v30full 의 판단과 같다", found[0][1])
        self.assertIn("범위: 갱신 회사", found[0][1])

    def test_updated_company_covers_f9_but_touched_items_stay_qualitative(self):
        """2026-10-23 q3a 출력 리뷰: 갱신 회사의 ⑨ 판정 재료가 옛 분기 숫자로 남았다. 갱신 회사는 ⑥⑨ 판단도 범위다."""
        judgments = self.ctx().judgments
        qual_ids = self.qual_only(judgments, lambda j: j["company_id"] in UPDATED)
        found = {jid for jid, _ in rejudge_findings(self.ctx(judgments=self.rejudge(judgments, qual_ids)))}
        self.assertEqual(found, {"alphabet.F9", "spacex-xai.F9"}, "갱신 회사의 ⑨ 는 정성 항목이 아니어도 다시 매긴다")
        all_ids = self.qual(judgments, lambda j: j["company_id"] in UPDATED)
        new = {"evidence_id": "EV-tesla-901", "company_id": "tesla", "factors": ["F9"], "status": "confirmed"}
        found = {jid for jid, _ in rejudge_findings(self.ctx(judgments=self.rejudge(judgments, all_ids), evidence=self.ctx().evidence + [new]))}
        self.assertEqual(found, set(), "닿은 항목은 정성 항목만 범위다 — 범위 밖 회사의 ⑨ 근거는 범위를 만들지 않는다")

    def test_out_of_scope_carried_and_unchanged_pass(self):
        judgments = self.ctx().judgments
        scope_ids = self.qual(judgments, lambda j: j["company_id"] in UPDATED)
        changed = self.rejudge(judgments, scope_ids)
        for j in changed:
            if j["company_id"] == "tesla" and j["factor"] == "F5":
                j["status"] = "carried"
        self.assertEqual(rejudge_findings(self.ctx(judgments=changed)), [])

    def test_carried_in_scope_is_flagged(self):
        judgments = self.ctx().judgments
        scope_ids = self.qual(judgments, lambda j: j["company_id"] in UPDATED)
        changed = self.rejudge(judgments, scope_ids)
        target = next(j for j in changed if j["judgment_id"] == "alphabet.F5")
        target["status"] = "carried"
        found = rejudge_findings(self.ctx(judgments=changed))
        self.assertEqual([jid for jid, _ in found], ["alphabet.F5"])
        self.assertIn("실적 반영 실행의 갱신 범위(갱신 회사)에 승계 판단", found[0][1])

    def test_touched_item_requires_every_layer_judgment(self):
        judgments = self.ctx().judgments
        scope_ids = self.qual(judgments, lambda j: j["company_id"] in UPDATED)
        new = {"evidence_id": "EV-microsoft-901", "company_id": "microsoft", "factors": ["F1"], "status": "confirmed"}
        ctx = self.ctx(judgments=self.rejudge(judgments, scope_ids), evidence=self.ctx().evidence + [new])
        found = {jid for jid, _ in rejudge_findings(ctx)}
        ms_f1 = self.qual(judgments, lambda j: j["company_id"] == "microsoft" and j["factor"] == "F1")
        self.assertGreater(len(ms_f1), 1, "사업 판단이 여럿이어야 검사가 뜻이 있다")
        self.assertEqual(found, ms_f1)

    def test_date_alone_is_not_enough(self):
        """내용이 같으면 검토일이 생성일 뒤여도 다시 매긴 것이 아니다 — 반대로 내용이 달라도 검토일이 생성일 앞이면 아니다."""
        judgments = self.ctx().judgments
        scope_ids = self.qual(judgments, lambda j: j["company_id"] in UPDATED)
        changed = self.rejudge(judgments, scope_ids)
        target = next(j for j in changed if j["judgment_id"] == "alphabet.F4")
        target["reviewed_at"] = "2026-10-01"
        target["evidence"] = target["evidence"] + ["문장만 바꾸고 날짜는 옛 날짜"]
        found = rejudge_findings(self.ctx(judgments=changed))
        self.assertEqual([jid for jid, _ in found], ["alphabet.F4"])
        self.assertIn("이번 실행 생성일", found[0][1])

    def test_regular_v31_run_closes_the_prior_as_of_hole(self):
        """v30full 판단은 기준일(10-14) 뒤에 매겼다. v3.1 정기 실행은 이어받기만 한 판단을 전부 잡는다."""
        stages.init_run("ai-scorecard-2026-10-reg", from_run=V30FULL, rule_version="v3.1", as_of=AS_OF, title="정기")
        d = engine.run_dir("ai-scorecard-2026-10-reg")
        ctx = SimpleNamespace(slug="ai-scorecard-2026-10-reg", run=load_json_strict(d / "run.json"), rules=load_rules("v3.1"),
                              companies=REGISTRY, judgments=load_json_strict(d / "judgments.json")["items"], evidence=None, triggers=None)
        found = {jid for jid, _ in rejudge_findings(ctx)}
        self.assertEqual(found, self.qual_only(ctx.judgments, lambda j: True))


class EarningsDetectionTest(ScopeBase):
    def test_flags_earnings_filers_outside_update(self):
        self.write_candidates([
            filing("microsoft", "8-K", "2026-10-21", ["2.02", "9.01"]),       # 실적 발표 8-K → 막힘
            filing("oracle", "8-K", "2026-10-21", ["5.02"]),                 # 인사 8-K → 통과
            filing("meta", "10-Q", "2026-10-23"),                             # 가격 기준일 뒤 → 통과
            filing("apple", "10-K", "2026-10-14"),                            # 마지막 전체 갱신일 당일 → 이미 반영
            filing("tesla", "8-K", "2026-10-20", ["2.02", "9.01"], title_only=True),   # 옛 후보(제목만) → 막힘
            filing("nvidia", "10-Q/A", "2026-10-16"),                         # 정정 10-Q → 막힘
            filing("alphabet", "10-Q", "2026-10-21"),                         # 갱신 회사 → 통과
            filing("tsmc", "6-K", "2026-10-16"),                              # 기계로 못 가름 → 리뷰 목록
        ])
        blocked, manual = update_scope.earnings_findings(self.ctx())
        self.assertEqual(sorted(line.split(":")[0] for line in blocked), ["microsoft", "nvidia", "tesla"])
        self.assertTrue(any("8-K 2026-10-21 Item 2.02, 9.01" in line for line in blocked))
        self.assertEqual([(m["company_id"], m["form"]) for m in manual], [("tsmc", "6-K")])

    def test_filing_list_must_be_fetched_after_price_day(self):
        fetched = {c: f"{AS_OF}T09:00:00Z" for c in SEC}
        fetched.pop("apple")
        fetched["meta"] = "2026-10-21T23:00:00Z"
        fetched["alphabet"] = "2026-10-01T00:00:00Z"   # 갱신 회사는 감지 대상이 아니다
        self.write_candidates([], fetched)
        blocked, _ = update_scope.earnings_findings(self.ctx())
        self.assertEqual(sorted(line.split(":")[0] for line in blocked), ["apple", "meta"])
        self.assertTrue(all("anthropic" not in line and "openai" not in line for line in blocked), "CIK 없는 비상장사는 감지하지 않는다")

    def test_missing_candidates_file_blocks(self):
        blocked, _ = update_scope.earnings_findings(self.ctx())
        self.assertEqual(len(blocked), 1)
        self.assertIn("공시 후보 파일이 없다", blocked[0])


class AgeLimitTest(ScopeBase):
    def test_121_days_blocks_and_120_passes(self):
        run = load_json_strict(self.d / "run.json")
        run["refreshed_at"]["openai"] = "2026-06-23"
        run["refreshed_at"]["anthropic"] = "2026-06-24"
        found = update_scope.age_findings(self.ctx(run=run))
        self.assertEqual(len(found), 1)
        self.assertTrue(found[0].startswith("openai: 마지막 전체 갱신 2026-06-23 로부터 121일"))

    def test_updated_company_is_exempt(self):
        run = load_json_strict(self.d / "run.json")
        run["refreshed_at"]["alphabet"] = "2026-01-01"
        self.assertEqual(update_scope.age_findings(self.ctx(run=run)), [])


class WiringTest(ScopeBase):
    def test_research_stops_before_rejudge_when_update_is_incomplete(self):
        with self.assertRaisesRegex(SchemaError, "실적 반영 실행의 갱신 회사가 모자란다.*공시 후보 파일이 없다"):
            stages.research(NEW)

    def test_previous_triggers_are_only_updated_companies(self):
        run = load_json_strict(self.d / "run.json")
        prev = stages.previous_triggers(run)
        self.assertTrue(prev)
        self.assertEqual({p["company_id"] for p in prev} - {None}, set(UPDATED))
        all_prev = stages.previous_triggers({**run, "continued_from": {**run["continued_from"], "updated_companies": []}})
        self.assertGreater(len(all_prev), len(prev), "갱신 회사가 아니면 모든 회사의 트리거를 요구한다")

    def test_declare_scope_extra(self):
        out = stages.declare_scope_extra(NEW, [("anthropic", "F5"), ("meta", "F3")], reason="Alphabet ⑤ 의 새 잣대가 닿는다")
        self.assertEqual(out["added"], [("anthropic", "F5"), ("meta", "F3")])
        extra = load_json_strict(self.d / "run.json")["update_scope"]["extra"]
        self.assertEqual([(x["company_id"], x["factor"]) for x in extra], [("anthropic", "F5"), ("meta", "F3")])
        before = (self.d / "run.json").read_bytes()
        for items, reason, needle in [
            ([("anthropic", "F5")], "다시", "이미 선언했다"),
            ([("anthropic", "F6")], "가격", "다시 매기는 정성 항목"),
            ([("amd", "F5")], "없는 회사", "실행 대상이 아닌 기업"),
            ([("tesla", "F5")], " ", "--reason 이 비었다"),
        ]:
            with self.assertRaisesRegex(SchemaError, needle):
                stages.declare_scope_extra(NEW, items, reason=reason)
        self.assertEqual((self.d / "run.json").read_bytes(), before, "거부하면 run.json 을 고치지 않는다")

    def test_declare_refuses_non_update_run(self):
        with self.assertRaisesRegex(SchemaError, "실적 반영 실행이 아니다"):
            stages.declare_scope_extra(V30FULL, [("anthropic", "F5")], reason="x")


class CandidateFieldsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.box = Sandbox(("nvidia", "tsmc", "openai"), rule_version="v3.1")
        self.addCleanup(self.box.close)

    def test_filing_candidates_keep_items_and_report_period_and_fetch_time(self):
        base = evidence_lib.DATA_ROOT / "nvidia" / "filings"
        base.mkdir(parents=True)
        (base / "index.json").write_text(json.dumps({"items": [{
            "filing_id": "edgar:0001", "form": "8-K", "filed_at": "2026-09-20", "report_period": "2026-09-19",
            "accession": "0001", "primary_document": "a.htm", "primary_doc_url": "https://www.sec.gov/a.htm",
            "items": ["2.02", "9.01"], "raw_ref": "data/nvidia/filings/raw/x.json", "source_id": "SRC-EDGAR-0001"}]}), encoding="utf-8")
        (base / "state.json").write_text(json.dumps({"runs": [{"at": "2026-09-21T01:00:00Z", "kind": "filings"},
                                                             {"at": "2026-09-28T01:00:00Z", "kind": "filings"}]}), encoding="utf-8")
        path = stages.write_candidates(self.box.slug, since="2026-04-01", until="2026-09-29", company_ids=["nvidia", "tsmc", "openai"])
        payload = load_json_strict(path)
        self.assertEqual(payload["filings_fetched_at"], {"nvidia": "2026-09-28T01:00:00Z"})
        c = payload["items"][0]
        self.assertEqual((c["items"], c["report_period"], c["title"]), (["2.02", "9.01"], "2026-09-19", "8-K 2026-09-20 · Items 2.02, 9.01"))


if __name__ == "__main__":
    unittest.main()
