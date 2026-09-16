# net_cash 작업 정의와 '6.4 를 P2 로 옮기지 말 것' 적용범위 구분을 고정한다 (NETCASH-37)
"""이 테스트가 지키는 계약 넷.

1. **역산 정의는 스스로 역산이라고 말해야 한다.** `provenance.kind` 가 `legacy_reverse_engineered`
   이면 경고와 `supersede` 가 비어 있을 수 없다. 근거 없는 정의가 확정 정의처럼 굳는 것을 막는다.
2. **근거 숫자가 목록과 맞아야 한다.** 일치 개수를 손으로 적고 목록을 나중에 고치면 숫자만 거짓말로 남는다.
3. **두 자리가 다른 지표를 가리켜야 한다.** 이 블록의 존재 이유가 `cash`(6.4 런웨이)와
   `net_cash`(P2 EV 조정)를 가르는 것이라 하나로 접히면 의미가 사라진다.
4. **P2 산출물에 정의가 드러나야 한다.** 선언만 하고 읽는 코드가 없으면 다음 사람은 값만 본다.
"""
from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard.calc_f6 import compute_f6  # noqa: E402
from scorecard.inputs import JudgmentLookup, ObsLookup  # noqa: E402
from scorecard.rules import load_rules  # noqa: E402
from scorecard.schema import SchemaError, validate_rules  # noqa: E402

RULES = load_rules("v1.7")
RUN_DIR = ROOT / "scorecard" / "runs" / "ai-scorecard-2026-09-obsreg"


def company(cid: str = "acme") -> dict:
    return {"company_id": cid, "display_name": cid.title(), "aliases": [], "type": "업무",
            "listed": True, "ticker": "ACME", "exchange": "NASDAQ", "share_basis": "common",
            "adr_ratio": None, "reporting_currency": "USD", "scope": "test"}


def obs(metric: str, value, *, basis=None, status="verified") -> dict:
    return {"observation_id": f"acme.{metric}.t", "company_id": "acme", "metric": metric,
            "value": value, "unit": "USD" if metric != "price" else "USD/share",
            "as_of": "2026-09-02", "kind": "actual", "source_id": "SRC-t", "status": status,
            "period": None, "basis": basis, "raw": None, "note": None}


def mutated_rules(mutate) -> dict:
    payload = copy.deepcopy(RULES.payload)
    mutate(payload["policies"]["f6"]["net_cash"], payload)
    return payload


class NetCashDefinitionTest(unittest.TestCase):
    """규칙 블록 자체의 계약."""

    def setUp(self) -> None:
        self.spec = RULES.f6_net_cash()

    def test_accessor_returns_working_definition(self):
        self.assertEqual(self.spec["status"], "working_definition")
        self.assertEqual(self.spec["provenance"]["kind"], "legacy_reverse_engineered")
        self.assertIn("현금", self.spec["definition"])

    def test_reverse_engineered_must_declare_it_is_replaceable(self):
        for key, drop in (("warning", lambda s, p: s["provenance"].pop("warning")),
                          ("supersede", lambda s, p: s.pop("supersede"))):
            with self.subTest(key=key), self.assertRaises(SchemaError) as cm:
                validate_rules(mutated_rules(drop))
            self.assertIn("net_cash", str(cm.exception))

    def test_unknown_status_rejected(self):
        with self.assertRaises(SchemaError):
            validate_rules(mutated_rules(lambda s, p: s.update(status="final")))

    def test_matched_count_must_equal_list(self):
        """개수만 고치고 목록을 안 고치는 실수를 로드 시점에 잡는다."""
        def drop_one(spec, _payload):
            spec["evidence"]["matched"]["companies"].pop("tesla")
        with self.assertRaises(SchemaError) as cm:
            validate_rules(mutated_rules(drop_one))
        self.assertIn("count", str(cm.exception))

    def test_matched_list_is_what_we_actually_measured(self):
        """규칙이 주장하는 7개사가 실제 검증 결과와 같아야 한다.

        라운드 1 에서는 여섯이었다. **유가증권 경계를 적용하자 spacex-xai 가 일치 쪽으로 넘어왔다** —
        독립인 두 정정(금융리스 이중계상 제거·제한현금 대신 시장성 증권)이 legacy 값 하나로 수렴한다.
        """
        self.assertEqual(set(self.spec["evidence"]["matched"]["companies"]),
                         {"microsoft", "tesla", "meta", "oracle", "alphabet", "palantir",
                          "spacex-xai"})
        self.assertEqual(set(self.spec["evidence"]["differs"]["companies"]),
                         {"amazon", "nvidia", "tsmc", "alibaba"})
        self.assertEqual(set(self.spec["evidence"]["undecidable"]), {"apple"})

    def test_unknown_cause_is_stated_not_hidden(self):
        """**왜 안 맞는지 모른다는 것을 적어 둔다.** 모르는 것을 아는 척하면 다음 사람이 조사하지 않는다."""
        self.assertIn("아직 모른다", self.spec["evidence"]["differs"]["note"])
        self.assertTrue(self.spec["open_questions"])


class ScopeSeparationTest(unittest.TestCase):
    """6.4(런웨이)와 P2(EV 조정)를 가르는 계약. **같은 '현금' 이라는 말이 두 자리에서 다른 것을 가리킨다.**"""

    def setUp(self) -> None:
        self.sep = RULES.f6_net_cash()["scope_separation"]

    def test_two_sites_name_different_metrics(self):
        self.assertEqual({s["metric"] for s in self.sep["sites"]}, {"cash", "net_cash"})

    def test_runway_site_counts_only_usable_cash(self):
        site = next(s for s in self.sep["sites"] if s["metric"] == "cash")
        self.assertIn("6.4", site["site"])
        self.assertIn("환금성", site["counts"])

    def test_ev_site_counts_marketable_assets_only(self):
        """EV 자리는 **시장성 있는** 재무적 자산만 센다.

        원래 이 테스트는 `환금성은 여기서 묻는 질문이 아니다` 라는 문장을 고정하고 있었다. 그 문장이
        지키려던 것은 **6.4 의 즉시성 제약이 P2 로 상속되지 않는다**는 것이고 그 뜻은 지금도 유효하다.
        문제는 낱말이었다 — `환금성` 이 즉시성과 시장성을 한꺼번에 덮어, 시장성까지 안 묻는 것으로
        읽혔다. 그 줄만 읽고 지분법 투자를 넣으면 alibaba net_cash 가 498억에서 987억 달러가 된다.
        그래서 같은 불변식을 **두 축으로 갈라서** 고정한다.
        """
        site = next(s for s in self.sep["sites"] if s["metric"] == "net_cash")
        self.assertIn("EV", site["site"])
        self.assertIn("시장성", site["counts"])
        self.assertIn("묻지 않고", site["why"])       # 즉시성
        self.assertIn("팔 시장이 있는지는 묻는다", site["why"])   # 시장성

    def test_each_site_answers_both_axes(self):
        """**두 축은 서로를 함의하지 않는다.** 자리마다 각각 답해야 포괄어로 뭉개지지 않는다."""
        for site in self.sep["sites"]:
            with self.subTest(metric=site["metric"]):
                for axis in ("immediacy", "marketability"):
                    self.assertTrue(str(site["axes"].get(axis) or "").strip())
        runway = next(s for s in self.sep["sites"] if s["metric"] == "cash")
        ev = next(s for s in self.sep["sites"] if s["metric"] == "net_cash")
        self.assertIn("묻는다", runway["axes"]["immediacy"])
        self.assertIn("묻지 않는다", ev["axes"]["immediacy"])
        self.assertIn("묻는다", ev["axes"]["marketability"])

    def test_missing_axis_is_rejected(self):
        def drop(spec, _payload):
            spec["scope_separation"]["sites"][1]["axes"].pop("marketability")
        with self.assertRaises(SchemaError) as cm:
            validate_rules(mutated_rules(drop))
        self.assertIn("marketability", str(cm.exception))

    def test_banned_word_is_declared_with_its_own_reason(self):
        """같은 결함이 세 번 나왔다. **금지한 낱말과 왜 금지했는지를 규칙이 들고 있어야** 한다."""
        banned = self.sep["two_axes"]["banned_word"]
        self.assertEqual(banned["word"], "환금성")
        self.assertIn("987", banned["why"])      # 잘못 읽었을 때의 값까지 적혀 있어야 한다
        self.assertEqual(banned["exceptions"], ["scope_separation.sites[0].counts"])

    def test_banned_word_is_actually_enforced_not_just_declared(self):
        """**선언만 하면 아무것도 막지 못한다.** 다른 자리에 다시 쓰면 로드가 거부돼야 한다.

        `전체·모두·전부` 는 테스트가 막는데 `환금성` 만 선언에 그쳐 있었다(설계진행 지적).
        금지어를 세운 자리가 그 금지를 강제하는지를 여기서 검사한다.
        """
        for path, mutate in (
            ("sites[1].why", lambda s: s["sites"][1].__setitem__(
                "why", s["sites"][1]["why"] + " 환금성은 여기서 묻지 않는다.")),
            ("rule", lambda s: s.__setitem__("rule", s["rule"] + " 환금성 기준으로 본다.")),
        ):
            with self.subTest(path=path), self.assertRaises(SchemaError) as cm:
                validate_rules(mutated_rules(lambda spec, _p: mutate(spec["scope_separation"])))
            self.assertIn("환금성", str(cm.exception))

    def test_six_four_quote_keeps_the_word(self):
        """6.4 원문을 인용하는 자리는 그 낱말이 문면에 있어야 한다 — 예외가 실제로 쓰인다."""
        runway = next(s for s in self.sep["sites"] if s["metric"] == "cash")
        self.assertIn("환금성", runway["counts"])

    def test_two_axes_comes_before_the_sites(self):
        """**순서가 이 블록에서는 내용이다.** '어느 축을 묻는지 먼저 보라' 가 뒤에 있으면 안 된다.

        이 건의 결함 기제가 블록을 위에서 읽다가 틀린 줄을 먼저 만나는 것이었다.
        """
        keys = list(self.sep)
        self.assertLess(keys.index("two_axes"), keys.index("sites"))
        self.assertLess(keys.index("warning"), keys.index("two_axes"))

    def test_no_unqualified_blanket_claim_in_the_ev_site(self):
        """EV 자리 문장에 한정 없는 '전체·모두·전부' 가 남아 있으면 안 된다."""
        ev = next(s for s in self.sep["sites"] if s["metric"] == "net_cash")
        for key in ("counts", "why", *(f"axes.{a}" for a in ("immediacy", "marketability"))):
            text = ev["axes"][key.split(".")[1]] if key.startswith("axes.") else ev[key]
            with self.subTest(key=key):
                for word in ("전체", "모두", "전부"):
                    self.assertNotIn(word, text)

    def test_collapsing_to_one_metric_is_rejected(self):
        """두 자리가 같은 지표를 가리키면 이 블록은 아무것도 구분하지 않는다.

        2026-09-16 FIX-55 1단계(4차 리뷰 C low): 이제 **소비자와도 묶어서** 본다 — 한 자리는 F9 G3 분자,
        한 자리는 net_cash 를 읽는 F6 파라미터를 가리켜야 한다. 그래서 한쪽으로 뭉개면 빠진 소비자 이름이 먼저 나온다.
        """
        def collapse_to(metric):
            def mutate(spec, _payload):
                for site in spec["scope_separation"]["sites"]:
                    site["metric"] = metric
            return mutate
        with self.assertRaises(SchemaError) as cm:
            validate_rules(mutated_rules(collapse_to("cash")))
        self.assertIn("net_cash 를 가리키는 자리가 없음", str(cm.exception))
        with self.assertRaises(SchemaError) as cm:
            validate_rules(mutated_rules(collapse_to("net_cash")))
        self.assertIn("G3 분자 지표", str(cm.exception))

    def test_unknown_metric_rejected(self):
        def bad(spec, _payload):
            spec["scope_separation"]["sites"][0]["metric"] = "free_cash"
        with self.assertRaises(SchemaError):
            validate_rules(mutated_rules(bad))

    def test_f9_side_cross_references_the_same_block(self):
        """6.4 를 고치러 온 사람도 걸려야 한다 — **한쪽에만 적으면 반쪽이다.**"""
        g3 = RULES.payload["policies"]["f9"]["g3_cash_scope"]
        self.assertEqual(g3["see"], "policies.f6.net_cash.scope_separation")
        self.assertEqual(g3["metric"], "cash")

    def test_alphabet_illustration_is_the_registered_gap(self):
        ill = self.sep["alphabet_illustration"]
        self.assertEqual(ill["all_securities_usd"] - ill["pure_cash_usd"], ill["gap_usd"])
        self.assertEqual(ill["gap_usd"], 186_563_000_000)


class P2EmitsDefinitionTest(unittest.TestCase):
    """**선언한 값은 읽는 코드가 있어야 한다.** P2 계산이 정의와 상태를 같이 찍는다."""

    def _f6(self):
        items = [obs("market_cap", 1_000e9), obs("net_income_ttm", 50e9),
                 obs("net_cash", 100e9), obs("revenue_ttm", 200e9, basis={"period_basis": "ttm"}),
                 obs("revenue_ttm_prior", 150e9)]
        run = {"run_id": "t", "as_of": "2026-09-02", "rule_version": "v1.7", "decisions": []}
        return compute_f6(company(), ObsLookup(items), JudgmentLookup([]), RULES, run)

    def test_p2_carries_definition_and_status(self):
        p2 = self._f6()["calc"]["parameters"]["P2"]
        got = p2["net_cash_definition"]
        self.assertEqual(got["status"], "working_definition")
        self.assertEqual(got["provenance"], "legacy_reverse_engineered")
        self.assertEqual(got["definition"], RULES.f6_net_cash()["definition"])

    def test_working_definition_raises_a_warning_but_not_a_penalty(self):
        """경고는 내되 **점수는 건드리지 않는다.** 정의 미확정은 기업의 성질이 아니다."""
        result = self._f6()
        self.assertTrue(any("net_cash 작업 정의" in w for w in result["warnings"]))
        p2 = result["calc"]["parameters"]["P2"]
        self.assertEqual(p2["value"], (1_000e9 - 100e9) / 200e9)    # EV/Sales 4.5
        self.assertEqual(p2["score"], 0)                            # 8 미만이라 0 칸. 경고가 있어도 그대로다


class SecuritiesScopeTest(unittest.TestCase):
    """유가증권 경계(설계진행 2026-09-11). **EV 조정은 팔아서 청구권을 상환할 수 있는 자산만 뺀다.**"""

    def setUp(self) -> None:
        self.scope = RULES.f6_net_cash()["securities_scope"]

    def test_criterion_is_stated_not_implied(self):
        self.assertIn("시장성", self.scope["criterion"])
        self.assertIn("청구권", self.scope["criterion"])

    def test_every_exclusion_carries_a_reason(self):
        """**뺀 이유가 없으면 다음 사람이 되돌린다.** 경계는 값이 아니라 논거로 서 있어야 한다."""
        self.assertGreaterEqual(len(self.scope["exclude"]), 5)
        for item in self.scope["exclude"]:
            with self.subTest(what=item.get("what")):
                self.assertTrue(str(item.get("why") or "").strip())

    def test_named_exclusions_cover_the_four_traps(self):
        what = " ".join(e["what"] for e in self.scope["exclude"])
        for trap in ("지분법", "비상장", "제한 현금", "만기 버킷"):
            self.assertIn(trap, what)

    def test_exclusion_without_reason_is_rejected(self):
        def drop(spec, _payload):
            spec["securities_scope"]["exclude"][0].pop("why")
        with self.assertRaises(SchemaError) as cm:
            validate_rules(mutated_rules(drop))
        self.assertIn("securities_scope", str(cm.exception))

    def test_empty_exclude_is_rejected(self):
        with self.assertRaises(SchemaError):
            validate_rules(mutated_rules(lambda s, p: s["securities_scope"].update(exclude=[])))


class RegisteredObservationsTest(unittest.TestCase):
    """실행에 등록된 실측 관측의 계약. **등록한 10개사와 안 한 2개사가 뒤섞이면 안 된다.**"""

    @classmethod
    def setUpClass(cls) -> None:
        cls.obs = json.loads((RUN_DIR / "observations.json").read_text(encoding="utf-8"))["items"]
        cls.results = json.loads((RUN_DIR / "results.json").read_text(encoding="utf-8"))
        cls.by_id = {o["observation_id"]: o for o in cls.obs}

    def test_ten_measured_registrations(self):
        got = {o["company_id"] for o in self.obs if o["observation_id"].endswith(".net_cash.nc37")}
        self.assertEqual(got, {"microsoft", "amazon", "nvidia", "spacex-xai", "tesla", "meta",
                               "oracle", "alphabet", "tsmc", "alibaba"})

    def test_measured_observations_carry_the_criterion(self):
        for o in self.obs:
            if not o["observation_id"].endswith(".net_cash.nc37"):
                continue
            with self.subTest(cid=o["company_id"]):
                self.assertEqual(o["status"], "verified")
                self.assertEqual(o["basis"]["definition_status"], "working_definition")
                self.assertIn("시장성", o["basis"]["securities_criterion"])
                self.assertIn("scope_warning", o["basis"])

    def test_two_companies_keep_legacy_and_stay_flagged(self):
        """등록하지 못한 둘은 **legacy 그대로 남고 미검증 표시가 유지돼야** 한다."""
        flagged = {c["company_id"] for c in self.results["companies"]
                   if "net_cash" in ((c["factors"]["F6"].get("calc") or {})
                                     .get("unverified_inputs") or {})}
        self.assertEqual(flagged, {"apple", "palantir"})

    def test_market_cap_still_flagged_on_every_listed_company(self):
        """net_cash 를 실측해도 **P2 는 여전히 미검증 시총 위에 선다.** 그 사실이 사라지면 안 된다."""
        flagged = {c["company_id"] for c in self.results["companies"]
                   if "market_cap" in ((c["factors"]["F6"].get("calc") or {})
                                       .get("unverified_inputs") or {})}
        # 2026-09-16 FIX-56 1단계: spacex-xai 가 P2 를 계산하게 되면서 12번째로 들어왔다(시총 v15 는 여전히 legacy_unverified).
        self.assertEqual(len(flagged), 12)

    def test_nvidia_maturity_bucket_double_count_removed(self):
        """**만기 버킷은 대차대조표 줄이 아니다.** 현금에 더하면 현금성자산 안의 증권이 두 번 세어진다."""
        o = self.by_id["nvidia.net_cash.nc37"]
        comp = o["basis"]["components"]
        self.assertEqual(comp["cash_and_marketable_securities"], 56_586_000_000)
        fix = next(f for f in o["basis"]["corrections"] if "총계" in f["what"])
        self.assertEqual(fix["c13_value"], 63_443_000_000)
        self.assertIn("만기", fix["why"])

    def test_spacex_two_corrections_converge_on_legacy(self):
        """**이 일치가 경계의 가장 강한 증거다.** 독립인 두 정정이 legacy 값 하나로 수렴한다."""
        o = self.by_id["spacex-xai.net_cash.nc37"]
        self.assertEqual(o["basis"]["components"]["cash_and_marketable_securities"], 100_009_000_000)
        self.assertEqual(o["basis"]["components"]["finance_lease"], None)   # 총액 태그에 이미 포함
        self.assertAlmostEqual(o["value"], 60_301_000_000, delta=1)
        self.assertTrue(o["basis"]["legacy_comparison"]["matched"])
        self.assertIn("수렴", o["basis"]["why_this_match_matters"])

    def test_amazon_short_term_borrowings_added(self):
        o = self.by_id["amazon.net_cash.nc37"]
        self.assertEqual(o["basis"]["components"]["debt_ex_lease"], 132_549_000_000)
        self.assertIn("us-gaap:ShortTermBorrowings", o["basis"]["components"]["debt_concepts"])

    def test_no_registration_contains_an_excluded_concept(self):
        """배제 개념이 총계에 섞이면 EV 가 과소계상된다."""
        excluded_names = {"EquityMethodInvestments",
                          "EquitySecuritiesWithoutReadilyDeterminableFairValueAmount"}
        for o in self.obs:
            if not o["observation_id"].endswith(".net_cash.nc37"):
                continue
            used = {c["tag"].split(":")[-1]
                    for c in o["basis"]["components"].get("cash_and_marketable_securities_concepts", [])}
            with self.subTest(cid=o["company_id"]):
                self.assertFalse(used & excluded_names)

    def test_tsmc_excludes_private_equity_from_the_notes(self):
        """대차대조표 줄만 보면 비상장 지분이 FVTPL·FVOCI 비유동에 통째로 숨는다."""
        o = self.by_id["tsmc.net_cash.nc37"]
        self.assertEqual(o["source_id"], "SRC-SEC-TSM-20F-FY2025")
        self.assertAlmostEqual(o["basis"]["components"]["excluded_nonmarketable"], 22_632.0, places=1)
        self.assertIn("금액 사실이 0건", o["basis"]["why_not_companyfacts"])

    def test_alibaba_registered_with_note11_split(self):
        o = self.by_id["alibaba.net_cash.nc37"]
        self.assertEqual(o["source_id"], "SRC-SEC-BABA-20F-FY2026")
        self.assertAlmostEqual(o["basis"]["components"]["cash_and_marketable_securities"],
                               625_509.0, places=1)
        self.assertAlmostEqual(o["basis"]["components"]["debt_ex_lease"], 259_996.0, places=1)
        self.assertIn("주석 11", o["basis"]["how_securities_were_split"])

    def test_alibaba_excludes_equity_method_and_private_stakes(self):
        o = self.by_id["alibaba.net_cash.nc37"]
        excluded = {r["label"]: r for r in o["basis"]["components"]["rows"] if r["kind"] == "excluded"}
        self.assertEqual(excluded["Investments in equity method investees"]["rmb_million"], 206_803.0)
        self.assertEqual(excluded["Investments in privately held companies"]["rmb_million"], 130_447.0)
        for row in excluded.values():
            self.assertTrue(str(row.get("why") or "").strip())


class LeaseGapMissingTypeTest(unittest.TestCase):
    """리스 태깅 공백에 **정확한 결측 유형**을 달고, 그 라벨이 엔진에 닿는지 본다."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.by_id = {o["observation_id"]: o for o in
                     json.loads((RUN_DIR / "observations.json").read_text(encoding="utf-8"))["items"]}
        cls.results = json.loads((RUN_DIR / "results.json").read_text(encoding="utf-8"))

    def test_value_is_not_invented(self):
        for cid in ("apple", "palantir"):
            o = self.by_id[f"{cid}.lease_liabilities.nc37"]
            with self.subTest(cid=cid):
                self.assertIsNone(o["value"])
                self.assertEqual(o["status"], "not_disclosed")

    def test_missing_type_matches_data_scope(self):
        """2026-09-15 FIX-54 2단계(3차 리뷰 A codex): 원래 `not_disclosed_confirmed` 였다. 전수 확인한 것은 companyfacts 표준 태그뿐이고
        10-Q 전문은 보존·검색하지 않았으므로 발행사 미공시로 올릴 수 없다 — `unverified` 로 내렸다. 옛 논거는 superseded 키에 남는다."""
        for cid in ("apple", "palantir"):
            o = self.by_id[f"{cid}.lease_liabilities.nc37"]
            with self.subTest(cid=cid):
                self.assertEqual(o["missing_type"], "unverified")
                self.assertIn("전수", o["basis"]["why_not_unverified_superseded"])
                self.assertIn("10-Q 전문", o["basis"]["label_correction"]["why"])
                self.assertEqual(o["basis"]["blocks_metric"], "net_cash")

    def test_label_reaches_the_output(self):
        """선언한 라벨은 읽는 코드가 있어야 한다. F6 calc 과 경고 양쪽에 나와야 한다."""
        for c in self.results["companies"]:
            if c["company_id"] not in ("apple", "palantir"):
                continue
            calc = c["factors"]["F6"]["calc"]
            with self.subTest(cid=c["company_id"]):
                blocked = calc["unverified_blocked_by"]["net_cash"]
                self.assertIn("lease_liabilities", blocked["reason"])
                self.assertEqual(blocked["components"][0]["missing_type"], "unverified")   # FIX-54 2단계 라벨 정정
                self.assertTrue(any("실측이 막힌 이유" in w for w in c["factors"]["F6"]["warnings"]))

    def test_other_companies_have_no_blocked_entry(self):
        for c in self.results["companies"]:
            if c["company_id"] in ("apple", "palantir"):
                continue
            with self.subTest(cid=c["company_id"]):
                self.assertNotIn("unverified_blocked_by", c["factors"]["F6"].get("calc") or {})


class P4ThresholdBoundaryTest(unittest.TestCase):
    """P4 임계에도 경계를 표시한다. **점수는 건드리지 않는다.**

    `boundary_note` 가 '파라미터마다 각자의 경계에 대해 계산한다' 고 말하는데 P1·P2·P3 에만 있고
    P4 임계에는 없었다. amazon 의 `nonop_share` 가 임계에서 2.4% 인데 표시가 없었고, 그 한 칸이
    총점 15 공동 1위를 만든다(설계진행 2026-09-11 발견).
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.results = json.loads((RUN_DIR / "results.json").read_text(encoding="utf-8"))
        cls.p4 = {c["company_id"]: (c["factors"]["F6"].get("calc") or {}).get("p4") or {}
                  for c in cls.results["companies"]}

    def test_same_tolerance_as_the_other_parameters(self):
        """자리마다 다른 관대함을 두지 않는다."""
        tol = RULES.f6["boundary_tolerance"]
        for cid, p4 in self.p4.items():
            if "nonop_share_boundary" in p4:
                with self.subTest(cid=cid):
                    self.assertEqual(p4["nonop_share_boundary"]["tolerance"], tol)

    def test_boundary_is_measured_on_magnitude(self):
        """비교가 `abs(value) >= threshold` 라 경계도 크기로 잰다 — 부호로 재면 음수가 늘 멀어진다.

        표본을 meta 에서 oracle 로 바꿨다. 산식 정정으로 meta 가 양수(0.0068)가 되면서 음수 표본이
        oracle 하나만 남았다. **검사하려던 것은 음수에서도 크기로 재는가** 이고 그 뜻은 그대로다.
        """
        p4 = self.p4["oracle"]
        self.assertLess(p4["nonop_share"], 0)
        got = p4["nonop_share_boundary"]["distance_ratio"]
        self.assertAlmostEqual(got, (abs(p4["nonop_share"]) - 0.30) / 0.30, places=9)

    def test_no_company_is_near_the_threshold_after_the_fix(self):
        """**경계 우려가 산식 정정으로 해소됐다.**

        원래 이 자리는 `amazon 이 임계에서 +2.4% 라 플래그가 뜬다` 를 고정하고 있었다. 그 표시를
        붙인 이유가 `저장값과 재계산이 갈리는데 어느 쪽이 옳은지 모른다` 였고, 저장값이 옳은 것으로
        밝혀지면서 amazon 이 +55.3% 로 멀어졌다. **표시 장치는 그대로 두고** 지금 아무도 경계에 없다는
        것을 고정한다 — 다음에 또 붙을 수 있다.
        """
        flagged = [cid for cid, p4 in self.p4.items()
                   if (p4.get("nonop_share_boundary") or {}).get("flag")]
        self.assertEqual(flagged, [])
        amazon = self.p4["amazon"]["nonop_share_boundary"]
        self.assertGreater(amazon["distance_ratio"], 0.5)

    def test_flag_does_not_move_the_score(self):
        """**표시는 점수를 바꾸지 않는다.** amazon 은 임계 위라 그대로 걸린다."""
        p4 = self.p4["amazon"]
        self.assertIn("nonop_share", p4["conditions_hit"])
        self.assertEqual(p4["demotion_steps"], 1)
        amazon = next(c for c in self.results["companies"] if c["company_id"] == "amazon")
        self.assertEqual(amazon["factors"]["F6"]["score"], -2)
        self.assertEqual(amazon["total"], 15)

    def test_sole_cause_marks_where_the_condition_decides(self):
        """조건이 둘이면 하나가 빠져도 강등은 그대로다. **혼자 정하는 자리만 표시한다.**"""
        sole = {cid: p4.get("demotion_sole_cause") for cid, p4 in self.p4.items()}
        self.assertEqual({cid for cid, v in sole.items() if v == "nonop_share"},
                         {"amazon", "alphabet"})
        self.assertIsNone(sole["alibaba"])                       # period_basis_not_ttm 이 같이 걸림
        # 2026-09-16 FIX-55 1단계: period_basis_not_ttm 을 관측에서 판정하게 고쳐 spacex-xai 는 조건이 둘이 됐다 — 단독 원인이 없다.
        self.assertIsNone(sole["spacex-xai"])

    def test_spacex_loses_the_condition_but_keeps_the_demotion(self):
        """세전이익을 복원 못 해 조건이 빠지지만 `short_history` 가 강등을 유지한다 — 점수 불변."""
        p4 = self.p4["spacex-xai"]
        self.assertIsNone(p4["nonop_share"])
        self.assertNotIn("nonop_share", p4["conditions_hit"])
        self.assertEqual(p4["demotion_steps"], 1)
        spx = next(c for c in self.results["companies"] if c["company_id"] == "spacex-xai")
        # 2026-09-16 FIX-56 1단계: P2 가 붙어 F6 는 -3 이다. **이 검사의 뜻(조건은 빠지고 강등 한 칸은 남는다)은 그대로**다.
        self.assertEqual(spx["factors"]["F6"]["score"], -3)


class NonopShareDivergenceTest(unittest.TestCase):
    """저장값과 재계산값이 갈린 것이 **규칙에 기록돼 있어야** 한다. 값을 고르는 것이 아니다."""

    def setUp(self) -> None:
        conds = {c["id"]: c for c in RULES.f6_p4()["conditions"]}
        self.spec = conds["nonop_share"]["stored_vs_recomputed"]

    def test_divergence_is_now_resolved_in_favour_of_the_stored_value(self):
        """**저장값이 옳고 재계산이 틀렸다.**

        원래 이 자리는 `divergent_unresolved` 와 `재계산값을 쓴다` 를 고정하고 있었다. 그때는 어느
        쪽이 옳은지 몰랐고 재계산이 검증 가능하다는 이유로 그쪽을 썼다. 보존 companyfacts 로
        세전이익을 복원해 맞춰 보니 **저장값 쪽이 표준 정의**였다(NONOP-44).
        """
        self.assertEqual(self.spec["status"], "resolved_stored_was_right")
        self.assertIn("저장값이 옳고", self.spec["resolution"]["verdict"])
        self.assertIn("영업외손익 ÷ 세전이익", self.spec["resolution"]["definition"])

    def test_exceptions_sit_right_next_to_the_resolved_status(self):
        """**resolved 가 "다 맞는 줄" 로 읽히면 안 된다.** 예외를 상태 바로 다음 키에 이름으로 둔다.

        처음에는 oracle·alibaba 둘 다 미해결로 두었다. oracle 이 풀려 **설명됨과 미설명**으로 갈랐다 —
        풀렸어도 엔진 값과 저장값은 여전히 다르므로 예외 목록에서 빼지 않는다.
        """
        keys = list(self.spec)
        self.assertEqual(keys[keys.index("status") + 1], "exceptions")
        ex = self.spec["exceptions"]
        self.assertEqual(set(ex["companies"]), {"oracle", "alibaba"})
        self.assertEqual(set(ex["explained"]), {"oracle"})
        self.assertEqual(set(ex["unexplained"]), {"alibaba"})
        self.assertIn("alibaba 는 안 풀렸다", ex["warning"])

    def test_oracle_window_was_checked_and_ruled_out(self):
        """창 네 개로는 -0.15 가 안 나온다. **두 회계연도 평균 관찰은 우연이었다고 스스로 정정한다.**"""
        w = self.spec["remaining_mismatch"]["oracle"]["window_check"]
        self.assertEqual(len(w["results"]), 4)
        self.assertIn("-0.15 가 나오지 않는다", w["verdict"])
        self.assertIn("우연이었다", w["observation_not_conclusion"])

    def test_both_errors_of_the_old_formula_are_named(self):
        errs = self.spec["resolution"]["two_errors_in_the_old_formula"]
        self.assertEqual(len(errs), 2)
        self.assertIn("법인세가 섞여", errs[0])
        self.assertIn("세전이익이 아니라 순이익", errs[1])

    def test_oracle_is_explained_by_the_operating_income_definition(self):
        """**영업이익 정의 차이다.** 원천이 구조조정비를 되더한 조정 영업이익을 썼다.

        원래 이 자리는 `저장값 쪽이 어긋난다` 를 고정했다. 세전이익이 두 경로로 확인돼 복원이 옳다는 것까지는
        맞았으나, 채점표 각주 ᶜ 의 `영업이익($22.39B)` 을 찾으면서 **어긋남의 원인이 영업이익 쪽**이라는 게
        드러났다. GAAP 20,606 + 구조조정비 1,779 = 22,385.
        """
        o = self.spec["remaining_mismatch"]["oracle"]
        self.assertIn("영업이익 정의 차이다", o["verdict"])
        a = o["resolution"]["arithmetic"]
        self.assertEqual(a["gaap_operating_income"] + a["restructuring_charges"], a["sum"])
        self.assertLess(abs(a["sum"] - a["author_operating_income"]), 10_000_000)
        self.assertIn("−0.15", o["resolution"]["stored_value_reproduced"])
        self.assertEqual(len(o["candidates_tried"]), 4)                  # 산식 후보 넷은 기록으로 남는다

    def test_engine_keeps_gaap_operating_income(self):
        """원천마다 조정 항목이 달라 **엔진은 GAAP 을 유지한다.** 판정도 같다."""
        o = self.spec["remaining_mismatch"]["oracle"]
        self.assertIn("GAAP 영업이익을 유지한다", o["resolution"]["engine_keeps_gaap"])
        self.assertIn("판정도 같다", o["resolution"]["engine_keeps_gaap"])

    def test_boundary_risk_resolution_is_recorded(self):
        s = self.spec["score_impact_of_the_fix"]
        self.assertIn("한 곳도 안 바뀐다", s["hits_unchanged"])
        self.assertIn("+55.3%", s["boundary_risk_gone"])

    def test_the_lesson_is_written_down(self):
        """`basis 없음` 이 `알아낼 수 없음` 이 아니라는 것."""
        self.assertIn("알아낼 수 없다", self.spec["lesson"])
        self.assertIn("net_cash", self.spec["lesson"])

    def test_sign_flips_are_listed_with_their_cause(self):
        self.assertEqual(set(self.spec["sign_flipped"]),
                         {"apple", "meta", "microsoft", "nvidia", "tesla", "tsmc"})
        # **왜 뒤집히는지**가 있어야 다음 사람이 값을 다시 세지 않는다.
        self.assertIn("세금", self.spec["why_signs_flip"])

    def test_table_is_marked_as_the_old_formula(self):
        """`table` 은 **정정 전** 값이다. 그대로 두되 무엇인지 알 수 있어야 한다.

        원래 이 테스트는 표의 둘째 열이 엔진 산출과 같은지를 검사했다. 산식이 정정돼 더 이상 같지
        않으므로, 검사 대상을 **표가 무엇의 기록인지**로 옮긴다. 표를 지우지 않는 이유는 부호가
        뒤집혀 있던 상태를 남겨 두기 위해서다.
        """
        self.assertIn("정의가 갈린 것", self.spec["what"])
        self.assertEqual(set(self.spec["sign_flipped"]),
                         {"apple", "meta", "microsoft", "nvidia", "tesla", "tsmc"})

    def test_corrected_values_no_longer_flip_sign(self):
        """정정 후 그 여섯은 전부 0 근처 양수가 된다 — 부호 뒤집힘이 사라졌다."""
        results = json.loads((RUN_DIR / "results.json").read_text(encoding="utf-8"))
        by = {c["company_id"]: (c["factors"]["F6"].get("calc") or {}).get("p4") or {}
              for c in results["companies"]}
        for cid in self.spec["sign_flipped"]:
            with self.subTest(cid=cid):
                self.assertGreater(by[cid]["nonop_share"], 0)
                self.assertLess(by[cid]["nonop_share"], 0.30)

    def test_it_says_where_the_condition_actually_decides(self):
        self.assertIn("amazon", self.spec["where_it_does_decide"])
        self.assertIn("alphabet", self.spec["where_it_does_decide"])
        self.assertIn("2.4%", self.spec["where_it_does_decide"])

    def test_stored_provenance_is_recorded_including_what_is_missing(self):
        """**복원 불가라는 것도 사실이다.** 없는 것을 없다고 적어야 다음 사람이 다시 찾지 않는다."""
        prov = self.spec["stored_provenance"]
        self.assertIn("SRC-v15-html", prov)
        self.assertIn("null", prov)
        self.assertIn("복원 불가", prov)

    def test_it_refuses_to_pick_silently(self):
        self.assertIn("조용히 고르지 않는다", self.spec["do_not"])


class NonopShareHypothesisTest(unittest.TestCase):
    """가설 검정 결과가 규칙에 남아야 한다. **정의를 확정한 것이 아니다.**"""

    def setUp(self) -> None:
        conds = {c["id"]: c for c in RULES.f6_p4()["conditions"]}
        self.h = conds["nonop_share"]["stored_vs_recomputed"]["hypothesis_test"]

    def test_both_variants_are_recorded_with_the_winner(self):
        self.assertIn("A", self.h["variants"])
        self.assertIn("B", self.h["variants"])
        self.assertIn("B 가 이긴다", self.h["result"])

    def test_numerator_is_the_same_in_both(self):
        """**다른 것은 분모뿐이다.** 이것을 안 적으면 다음 사람이 둘을 별개 산식으로 본다."""
        self.assertIn("분자는 둘이 같다", self.h["variants"]["note"])

    def test_it_names_the_two_deviations(self):
        """현재 산식이 두 군데 벗어난다 — 부호를 바꾸는 것은 분자 쪽이다."""
        what = self.h["what_it_means"]
        self.assertIn("법인세를 되더하지 않는다", what)
        self.assertIn("부호가 뒤집히는 원인", what)

    def test_score_impact_is_stated_as_none(self):
        """확정해도 판정이 안 바뀐다는 것과, **amazon 의 경계 위험이 사라진다**는 것이 핵심이다."""
        s = self.h["score_impact_if_confirmed"]
        self.assertIn("하나도 안 바뀐다", s)
        self.assertIn("+54.7%", s)

    def test_it_refuses_to_call_the_hypothesis_confirmed(self):
        self.assertIn("가설이지 확정이 아니다", self.h["still_open"])
        self.assertEqual(set(self.h["unmatched_B"]), {"alibaba", "oracle", "tesla"})

    def test_tsmc_tax_came_from_the_preserved_20f(self):
        """companyfacts 에 2025 금액 사실이 0건이라 20-F 로 갔다는 것이 적혀 있어야 한다."""
        self.assertIn("20-F", self.h["method"])
        self.assertIn("346,529.8", self.h["method"])


class PendingDecisionImplementationTest(unittest.TestCase):
    """**미결이어도 권고안이 이미 코드에 서 있을 수 있다.** 그 구분을 규칙이 들고 있어야 한다."""

    def setUp(self) -> None:
        self.dec = {x["id"]: x for x in RULES.payload["decisions"]}

    def test_c04_c07_are_marked_implemented_while_still_pending(self):
        for did in ("C-04", "C-07"):
            with self.subTest(did=did):
                self.assertEqual(self.dec[did]["status"], "pending")   # 결정은 안 적었다
                self.assertEqual(self.dec[did]["implementation_status"]["verdict"],
                                 "already_implemented")
                self.assertIn("결정은 적지 않았다",
                              self.dec[did]["implementation_status"]["not_decided_here"])

    def test_c04_carries_the_source_text_and_where_it_lives(self):
        """원문이 워크트리에 없다는 사실까지 적어야 다음 사람이 다시 찾지 않는다."""
        st = self.dec["C-04"]["implementation_status"]
        self.assertIn("어느 factor의 입력으로도 쓸 수 없다", st["source_text"])
        self.assertIn("worker 워크트리에 없다", st["source_location"])

    def test_c04_records_that_include_v15_is_forbidden_by_the_source(self):
        st = self.dec["C-04"]["implementation_status"]
        self.assertIn("원문이 금지한 것을 선택지로 둔 것이다",
                      st["include_v15_is_not_a_valid_choice"])

    def test_c04_distinguishes_unread_from_read_but_unused(self):
        """**안 읽는 것과 읽고 안 쓰는 것은 다른 결함이다.** 후자가 더 나쁘다."""
        st = self.dec["C-04"]["implementation_status"]["include_v15_reads_but_does_not_use"]
        self.assertIn("읽기는 읽는다", st)
        self.assertIn("후자가 더 나쁘다", st)

    def test_c07_records_the_double_block(self):
        st = self.dec["C-07"]["implementation_status"]
        self.assertEqual(len(st["double_block"]), 3)
        self.assertEqual(st["incompatible_basis_observations"]["count"], 4)
        self.assertIn("G4 에 아예 닿지 않는다", st["routes"]["openai"])


if __name__ == "__main__":
    unittest.main()
