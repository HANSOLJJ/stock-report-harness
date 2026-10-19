# 규칙 v3.0 ① D·E: 시장 정의표 검증·해시 결속과 시장 순위·점유율 방향 계산(calc_market)을 잠근다
from __future__ import annotations

import copy
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard import rules as rules_mod  # noqa: E402
from scorecard.calc_layers import compute_f1_business  # noqa: E402
from scorecard.calc_market import market_position  # noqa: E402
from scorecard.inputs import JudgmentLookup, ObsLookup  # noqa: E402
from scorecard.rules import RuleSet, load_rules  # noqa: E402
from scorecard.schema import SchemaError, sha256_file, validate_judgments, validate_market_definition  # noqa: E402
from tests.test_calc_layers import AMAZON, COMPANIES, RUN, business, comp, holdings, judgment  # noqa: E402

V30 = load_rules("v3.0")


def definition(market_id: str = "cloud_infra", value_kind: str = "share", measure: str = "revenue", **kw) -> dict:
    d = {"schema": "scorecard.market/1", "market_id": market_id, "label": "클라우드 인프라 서비스 매출", "measure": measure,
         "value_kind": value_kind, "period_basis": "quarter_yoy", "source_priority": "research_firm", "scope_basis": "research_firm_unit",
         "sources": [{"label": "조사기관 분기 보도자료", "url": "https://example.com/q", "role": "primary"}],
         "constituents": [{"key": "aws", "name": "AWS", "company_id": "amazon"}, {"key": "azure", "name": "Microsoft Azure"},
                          {"key": "gcp", "name": "Google Cloud"}, {"key": "oracle", "name": "Oracle"}],
         "outside": [{"name": "Alibaba Cloud", "note": "중국 시장 위주라 조사기관 표에 따로 있다"}], "precision": 0.001}
    d.update(kw)
    return d


def mobs(constituent: str, value: float, start: str, end: str, *, market_id: str = "cloud_infra", metric: str = "market_share",
         status: str = "verified") -> dict:
    return {"observation_id": f"_market.{market_id}.{constituent}.{end}", "company_id": "_market", "metric": metric, "value": value,
            "unit": "ratio" if metric == "market_share" else "USD", "as_of": end, "kind": "actual", "source_id": "SRC-T",
            "status": status, "period": {"start": start, "end": end}, "basis": {"market_id": market_id, "constituent": constituent}}


Q_NOW, Q_PRIOR = ("2026-04-01", "2026-06-30"), ("2025-04-01", "2025-06-30")


def shares(now: dict[str, float], prior: dict[str, float] | None = None, **kw) -> ObsLookup:
    items = [mobs(k, v, *Q_NOW, **kw) for k, v in now.items()]
    items += [mobs(k, v, *Q_PRIOR, **kw) for k, v in (prior or {}).items()]
    return ObsLookup(items)


def position(market: dict, obs: ObsLookup, company_id: str = "amazon") -> dict:
    return market_position(market, obs, company_id, "2026-10-14", V30)


class DefinitionTest(unittest.TestCase):
    def test_valid_and_rejections(self):
        validate_market_definition(definition(), "cloud_infra")
        for change, pattern in [
            ({"market_id": "foundry"}, "파일 이름과 다름"),
            ({"measure": "users"}, "measure"),
            ({"sources": [{"label": "a", "url": "u", "role": "alternate"}]}, "1순위\\(primary\\) 출처는 하나"),
            ({"constituents": [{"key": "aws", "name": "AWS"}]}, "구성 회사 둘 이상"),
            ({"constituents": [{"key": "aws", "name": "AWS"}, {"key": "aws", "name": "AWS2"}]}, "겹치지 않는 소문자 id"),
            ({"precision": 0.2}, "precision"),
            ({"measure_fit": "indirect"}, "measure_fit"),
        ]:
            with self.subTest(change=change), self.assertRaisesRegex(SchemaError, pattern):
                validate_market_definition(definition(**change), "cloud_infra")


class HashBindingTest(unittest.TestCase):
    """규칙이 정의표의 sha256 을 품는다. 파일을 바꾸면 거부한다(점수를 본 뒤 시장을 바꿀 수 없다)."""

    def setUp(self) -> None:
        self.dir = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.dir, True)
        (self.dir / "markets").mkdir()
        self.file = self.dir / "markets" / "cloud_infra.json"
        self.file.write_bytes((json.dumps(definition(), ensure_ascii=False, indent=2) + "\n").encode())
        patcher = mock.patch.object(rules_mod, "ROOT", self.dir)
        patcher.start()
        self.addCleanup(patcher.stop)

    def ruleset(self, digest: str) -> RuleSet:
        payload = copy.deepcopy(V30.payload)
        payload["factors"]["F1"]["markets"] = {"dir": "markets", "files": {"cloud_infra": digest}, "partial_weight": 0.5}
        return RuleSet(payload, V30.path)

    def test_matching_hash_loads_and_changed_file_is_refused(self):
        rs = self.ruleset(sha256_file(self.file))
        self.assertEqual(rs.market("cloud_infra")["label"], "클라우드 인프라 서비스 매출")
        stale = self.ruleset(sha256_file(self.file))
        self.file.write_bytes(self.file.read_bytes().replace("AWS".encode(), "Amazon".encode()))
        with self.assertRaisesRegex(SchemaError, "해시.*규칙에 적힌 값.*다르다"):
            stale.market("cloud_infra")
        with self.assertRaisesRegex(SchemaError, "시장 정의표 'foundry' 가 없다"):
            rs.market("foundry")

    def test_bad_digest_in_rules_is_refused(self):
        with self.assertRaisesRegex(SchemaError, "sha256"):
            self.ruleset("abc")

    def test_partial_weight_must_be_between_zero_and_one(self):
        # 2026-10-15 사용자 결정: 일부만 재는 자료의 고정 반영 비율. 빠지거나 0·1·문자열이면 거부한다.
        digest = sha256_file(self.file)
        for bad in (None, 0, 1, 1.5, "0.5"):
            payload = copy.deepcopy(V30.payload)
            payload["factors"]["F1"]["markets"] = {"dir": "markets", "files": {"cloud_infra": digest}}
            if bad is not None:
                payload["factors"]["F1"]["markets"]["partial_weight"] = bad
            with self.subTest(bad=bad), self.assertRaisesRegex(SchemaError, "partial_weight"):
                RuleSet(payload, V30.path)
        self.assertEqual(V30.payload["factors"]["F1"]["markets"]["partial_weight"], 0.5)


class PositionTest(unittest.TestCase):
    def test_rank_levels(self):
        m = definition()
        cases = [
            ({"aws": 0.60, "azure": 0.20, "gcp": 0.12, "oracle": 0.03}, "dominant", 4),   # 50% 이상
            ({"aws": 0.40, "azure": 0.19, "gcp": 0.12, "oracle": 0.03}, "dominant", 4),   # 2위의 2배 이상
            ({"aws": 0.40, "azure": 0.25, "gcp": 0.12, "oracle": 0.03}, "first", 3),
            ({"aws": 0.25, "azure": 0.40, "gcp": 0.12, "oracle": 0.03}, "second", 2),
            ({"aws": 0.12, "azure": 0.40, "gcp": 0.25, "oracle": 0.03}, "third", 1),
            ({"aws": 0.02, "azure": 0.40, "gcp": 0.25, "oracle": 0.03}, "other", 0),
        ]
        for now, level, points in cases:
            with self.subTest(level=level, now=now):
                r = position(m, shares(now))
                self.assertEqual((r.get("D_level"), r["D"]), (level, points))

    def test_rounding_boundaries_are_not_settled(self):
        m = definition()
        tie = position(m, shares({"aws": 0.300, "azure": 0.2995, "gcp": 0.12, "oracle": 0.03}))
        self.assertIsNone(tie["D"])
        self.assertTrue(any("반올림 폭" in n for n in tie["notes"]))
        double = position(m, shares({"aws": 0.30, "azure": 0.15, "gcp": 0.12, "oracle": 0.03}))   # 정확히 2배
        self.assertIsNone(double["D"])
        # 2026-10-15: 정수 % 출처(반올림 폭 1%p)에서 23% 와 22% 는 구간이 22.5 한 점에서만 닿아 순위가 정해진다.
        # 0.23 − 0.22 의 부동소수 끝자리(0.0100…09)에도 속지 않는다. 차이가 폭보다 작으면(22.5% 와 23%) 확정하지 않는다.
        coarse = definition(precision=0.01)
        self.assertEqual(position(coarse, shares({"aws": 0.22, "azure": 0.23, "gcp": 0.12, "oracle": 0.09}))["D"], 2)
        self.assertIsNone(position(coarse, shares({"aws": 0.225, "azure": 0.23, "gcp": 0.12, "oracle": 0.09}))["D"])

    def test_share_direction_uses_the_low_end(self):
        m = definition()
        now = {"aws": 0.30, "azure": 0.21, "gcp": 0.13, "oracle": 0.03}
        for prior_aws, expected in ((0.30, 1.9), (0.25, 4.0), (0.33, 0.0), (0.31, 0.9)):
            with self.subTest(prior=prior_aws):
                r = position(m, shares(now, {**now, "aws": prior_aws}))
                self.assertAlmostEqual(r["E"], expected, places=6)
                self.assertAlmostEqual(r["change_pp_low"], r["change_pp"] - 0.1, places=6)

    def test_disclosure_sum_needs_every_constituent(self):
        m = definition(value_kind="amount", precision=None)
        del m["precision"]
        now = {"aws": 30.0, "azure": 30.0, "gcp": 15.0, "oracle": 5.0}
        r = position(m, shares(now, {k: v * 0.8 for k, v in now.items()}, metric="market_revenue"))
        self.assertAlmostEqual(r["share"], 30 / 80)
        self.assertIsNone(r["D"], "AWS 와 Azure 가 같아 순위를 확정하지 않는다(공시 합산은 반올림 폭 0 이라 정확히 같을 때만)")
        self.assertEqual(r["E"], 2.0)
        missing = position(m, shares({k: v for k, v in now.items() if k != "oracle"}, metric="market_revenue"))
        self.assertEqual((missing["D"], missing["E"]), (None, None))
        self.assertTrue(any("['oracle']" in n for n in missing["notes"]))

    def test_outside_a_top_n_list_is_other_and_usage_needs_share(self):
        now = {"aws": 0.30, "azure": 0.21, "gcp": 0.13, "oracle": 0.03}
        top = position(definition(lists_top_n=True), shares(now), company_id="apple")
        self.assertEqual((top["D_level"], top["D"], top["E"]), ("other", 0, None))
        self.assertIsNone(position(definition(), shares(now), company_id="apple")["D"], "상위 목록이 아니면 확정하지 않는다")
        validate_market_definition(definition(measure="usage"), "cloud_infra")
        for change, pattern in [({"measure": "usage", "value_kind": "amount"}, "사용량"), ({"lists_top_n": False}, "lists_top_n")]:
            with self.subTest(change=change), self.assertRaisesRegex(SchemaError, pattern):
                validate_market_definition(definition(**change), "cloud_infra")

    def test_one_company_with_several_constituents_is_ranked_as_one(self):
        # 2026-10-15: 소셜 미디어의 Facebook·Instagram 은 Meta 한 회사다. 따로 세면 X 가 4위, 합치면 3위(D 1)다.
        members = [{"key": "facebook", "name": "Facebook", "company_id": "meta"}, {"key": "instagram", "name": "Instagram", "company_id": "meta"},
                   {"key": "youtube", "name": "YouTube", "company_id": "alphabet"}, {"key": "twitter", "name": "X", "company_id": "spacex-xai"},
                   {"key": "pinterest", "name": "Pinterest"}]
        m = definition(market_id="social_media", measure="usage", constituents=members, precision=0.0001)
        now = {"facebook": 0.72, "instagram": 0.0713, "youtube": 0.0837, "twitter": 0.0687, "pinterest": 0.0299}
        prior = {"facebook": 0.733, "instagram": 0.0908, "youtube": 0.0431, "twitter": 0.0744, "pinterest": 0.0398}
        obs = shares(now, prior, market_id="social_media")
        x = position(m, obs, company_id="spacex-xai")
        self.assertEqual((x["rank"], x["D_level"], x["D"]), (3, "third", 1))
        meta = position(m, obs, company_id="meta")
        self.assertAlmostEqual(meta["share"], 0.7913)
        self.assertEqual((meta["constituent"], meta["D"]), ("facebook+instagram", 4))
        # 두 구성 회사의 반올림 오차가 더해져 낮은 끝이 두 배로 내려간다: (0.7913 − 0.8238) × 100 − 2 × 0.0001 × 100
        self.assertAlmostEqual(meta["change_pp_low"], (0.7913 - 0.8238) * 100 - 0.02, places=6)
        apart = definition(market_id="social_media", measure="usage", precision=0.0001,
                           constituents=[{k: v for k, v in c.items() if not (c["key"] in ("facebook", "instagram") and k == "company_id")} for c in members])
        self.assertEqual(position(apart, obs, company_id="spacex-xai")["rank"], 4, "회사를 표시하지 않으면 따로 센다")

    def test_unknown_cases(self):
        m = definition()
        now = {"aws": 0.30, "azure": 0.21, "gcp": 0.13, "oracle": 0.03}
        self.assertIsNone(position(m, shares(now))["E"], "1년 전 기간이 없으면 방향을 잴 수 없다")
        self.assertTrue(position(m, shares(now), company_id="apple")["notes"][0].startswith("이 회사가 시장 cloud_infra 의 구성 회사에 없다"))
        self.assertIsNone(position(m, shares(now, status="legacy_unverified"))["D"], "검증되지 않은 관측은 쓰지 않는다")
        partial = position(m, shares({k: v for k, v in now.items() if k != "gcp"}))
        self.assertIsNone(partial["D"])
        late = ObsLookup([mobs(k, v, "2026-10-01", "2026-12-31") for k, v in now.items()])
        self.assertTrue(position(m, late)["notes"][0].startswith("기준일 2026-10-14 까지"))


class F1IntegrationTest(unittest.TestCase):
    """구성 사업이 시장을 가리키면 D·E 가 미확인 1.6 대신 계산값이 된다."""

    def setUp(self) -> None:
        self.dir = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.dir, True)
        (self.dir / "markets").mkdir()
        f = self.dir / "markets" / "cloud_infra.json"
        f.write_bytes((json.dumps(definition(), ensure_ascii=False, indent=2) + "\n").encode())
        patcher = mock.patch.object(rules_mod, "ROOT", self.dir)
        patcher.start()
        self.addCleanup(patcher.stop)
        payload = copy.deepcopy(V30.payload)
        payload["factors"]["F1"]["markets"] = {"dir": "markets", "files": {"cloud_infra": sha256_file(f)}, "partial_weight": 0.5}
        self.rules = RuleSet(payload, V30.path)

    def test_market_replaces_unknown_points(self):
        aws_comp = comp("AWS", "cloud", ["aws"], "work")
        aws_comp["market"] = "cloud_infra"
        items = [judgment(holdings()),
                 business("stores", [comp("온라인 스토어", "user_platform", ["online_stores"]),
                                     comp("제3자 판매자", "user_platform", ["third_party"], "trade")]),
                 business("aws", [aws_comp], participant="none", substitutes="no_substitute")]
        validate_judgments({"schema": "scorecard.judgments/1", "run_id": "t", "items": items}, COMPANIES, self.rules.payload, "t")
        obs = shares({"aws": 0.30, "azure": 0.21, "gcp": 0.13, "oracle": 0.03}, {"aws": 0.32, "azure": 0.20, "gcp": 0.12, "oracle": 0.03})
        r = compute_f1_business(AMAZON, JudgmentLookup(items), self.rules, RUN, obs)
        aws = r["calc"]["businesses"]["aws"]
        c = aws["components"][0]
        # 1위이나 2배·50% 미달 → D 3, 점유율 −2%p(낮은 끝 −2.1) → E 0
        self.assertEqual((c["D"], c["E"], c["market"]["rank"], c["market"]["D_level"]), (3, 0, 1, "first"))
        self.assertNotIn("D", aws["unknown_parts"])
        stores = r["calc"]["businesses"]["stores"]["components"]
        self.assertEqual([x["D"] for x in stores], [1.6, 1.6], "시장을 정하지 않은 구성은 미확인 1.6")
        self.assertTrue(any("시장이 정해지지 않아" in w for w in r["warnings"]))
        without = compute_f1_business(AMAZON, JudgmentLookup(items), self.rules, RUN)   # 관측을 넘기지 않으면 미확인
        self.assertEqual(without["calc"]["businesses"]["aws"]["components"][0]["D"], 1.6)
        from scorecard.render_common import market_table_rows
        self.assertEqual(market_table_rows({"F1": r}), [["AWS", "클라우드 인프라 서비스 매출", "1위", "30.0% ← 32.0%", "-2.0%p", "100%", "3", "0"]],
                         "시장이 정해진 구성만 표에 싣는다")


class PartialWeightTest(unittest.TestCase):
    """2026-10-15 사용자 결정(rules.md ① 「부분 반영」): 시장이 사업의 일부만 재거나 정의표가 간접 자료면
    반영 비율 × 잰 점수 + (1 − 반영 비율) × 미확인 1.6 이다. 덮는 비율을 알면 그 비율, 모르면 0.5, 둘이 걸리면 곱한다."""

    OBS = {"aws": 0.30, "azure": 0.21, "gcp": 0.13, "oracle": 0.03}, {"aws": 0.32, "azure": 0.20, "gcp": 0.12, "oracle": 0.03}

    def rules_for(self, market: dict) -> RuleSet:
        d = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, d, True)
        (d / "markets").mkdir()
        f = d / "markets" / "cloud_infra.json"
        f.write_bytes((json.dumps(market, ensure_ascii=False, indent=2) + "\n").encode())
        patcher = mock.patch.object(rules_mod, "ROOT", d)
        patcher.start()
        self.addCleanup(patcher.stop)
        payload = copy.deepcopy(V30.payload)
        payload["factors"]["F1"]["markets"] = {"dir": "markets", "files": {"cloud_infra": sha256_file(f)}, "partial_weight": 0.5}
        rules = RuleSet(payload, V30.path)
        rules.market("cloud_infra")   # 이 임시 폴더에서 읽어 둔다(다음 rules_for 가 ROOT 를 다시 바꾼다)
        return rules

    def run_aws(self, rules: RuleSet, coverage=None, obs: ObsLookup | None = None) -> tuple[dict, dict]:
        aws_comp = comp("AWS", "cloud", ["aws"], "work")
        aws_comp["market"] = "cloud_infra"
        if coverage is not None:
            aws_comp["coverage"] = coverage
        items = [judgment(holdings()),
                 business("stores", [comp("온라인 스토어", "user_platform", ["online_stores"]),
                                     comp("제3자 판매자", "user_platform", ["third_party"], "trade")]),
                 business("aws", [aws_comp], participant="none", substitutes="no_substitute")]
        validate_judgments({"schema": "scorecard.judgments/1", "run_id": "t", "items": items}, COMPANIES, rules.payload, "t")
        r = compute_f1_business(AMAZON, JudgmentLookup(items), rules, RUN, obs if obs is not None else shares(*self.OBS))
        return r, r["calc"]["businesses"]["aws"]["components"][0]

    def test_weights(self):
        direct, proxy = self.rules_for(definition()), self.rules_for(definition(measure_fit="proxy"))
        # 잰 값은 D 3(1위)·E 0(−2%p). 반영 비율별 기대값.
        for rules, coverage, weight, d, e in [
            (direct, None, None, 3, 0),
            (direct, 0.58, 0.58, 2.412, 0.672),      # 0.58 × 3 + 0.42 × 1.6, 0.42 × 1.6
            (direct, "partial", 0.5, 2.3, 0.8),
            (proxy, None, 0.5, 2.3, 0.8),
            (proxy, "partial", 0.25, 1.95, 1.2),     # 0.5 × 0.5, 0.25 × 3 + 0.75 × 1.6
            (proxy, 0.58, 0.29, 2.006, 1.136),      # 0.29 × 3 + 0.71 × 1.6
        ]:
            with self.subTest(coverage=coverage, proxy=rules is proxy):
                r, c = self.run_aws(rules, coverage)
                self.assertEqual((c.get("weight"), c["D"], c["E"]), (weight, d, e))
                if weight is not None:
                    self.assertEqual((c["D_measured"], c["E_measured"]), (3, 0))
                stores = r["calc"]["businesses"]["stores"]["components"]
                self.assertEqual([x["D"] for x in stores], [1.6, 1.6], "부분 반영은 그 구성에만 걸린다")

    def test_unmeasurable_part_stays_unknown(self):
        # 잴 수 없으면(관측 없음) 반영 비율과 무관하게 미확인 1.6 이고 미확인으로 표시한다.
        r, c = self.run_aws(self.rules_for(definition(measure_fit="proxy")), "partial", obs=ObsLookup([]))
        self.assertEqual((c["D"], c["E"], c["D_measured"], c["E_measured"]), (1.6, 1.6, None, None))
        self.assertIn("D", r["calc"]["businesses"]["aws"]["unknown_parts"])

    def test_table_shows_weight(self):
        from scorecard.render_common import market_table_rows
        r, _c = self.run_aws(self.rules_for(definition()), 0.58)
        self.assertEqual(market_table_rows({"F1": r})[0][5:], ["58%", "2.41", "0.67"])

    def test_unknown_marker_is_per_component(self):
        # 2026-10-19 pilot8 출력 리뷰 F-2: 묶음에서 한 구성(Services)만 미확인이어도 다른 구성(iPhone) 행에 (미확인)이 붙었다.
        from scorecard.render_common import market_table_rows
        aws_comp = comp("AWS", "cloud", ["aws"], "work")
        aws_comp["market"] = "cloud_infra"
        rules = self.rules_for(definition())
        items = [judgment(holdings()),
                 business("stores", [comp("온라인 스토어", "user_platform", ["online_stores"])]),
                 business("aws", [aws_comp, comp("제3자 판매자", "user_platform", ["third_party"], "trade")], participant="none",
                          substitutes="no_substitute", bundle_reason="묶음 시험")]
        validate_judgments({"schema": "scorecard.judgments/1", "run_id": "t", "items": items}, COMPANIES, rules.payload, "t")
        r = compute_f1_business(AMAZON, JudgmentLookup(items), rules, RUN, shares(*self.OBS))
        comps = r["calc"]["businesses"]["aws"]["components"]
        self.assertEqual([c["unknown_parts"] for c in comps], [[], ["D", "E"]])
        self.assertEqual(market_table_rows({"F1": r})[0][6:], ["3", "0"], "측정한 구성 행에는 (미확인)을 달지 않는다")

    def test_coverage_rejections(self):
        rules = self.rules_for(definition())
        for bad, pattern in [(0, "coverage"), (1, "coverage"), (1.2, "coverage"), ("half", "coverage"), (True, "coverage")]:
            with self.subTest(bad=bad), self.assertRaisesRegex(SchemaError, pattern):
                self.run_aws(rules, bad)
        no_market = comp("온라인 스토어", "user_platform", ["online_stores"])
        no_market["coverage"] = "partial"
        items = [judgment(holdings()), business("stores", [no_market, comp("제3자 판매자", "user_platform", ["third_party"], "trade")])]
        with self.assertRaisesRegex(SchemaError, "시장이 없는 구성은 덮는 비율"):
            validate_judgments({"schema": "scorecard.judgments/1", "run_id": "t", "items": items}, COMPANIES, rules.payload, "t")


if __name__ == "__main__":
    unittest.main()
