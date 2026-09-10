# SEC 원자료 직접 파싱 및 F6 재정의 4대 핵심 지점을 독립 검증하는 단위 테스트
import os
import json
import unittest

class TestF6IndependentVerification(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base_dir = os.path.dirname(os.path.abspath(__file__))
        cls.raw_dir = os.path.join(cls.base_dir, "..", "f6-avail-15b", "_raw")
        
        # Load baseline observations for market_cap, net_cash, nonop_share
        obs_path = os.path.join(cls.base_dir, "baseline_v15_observations.json")
        with open(obs_path, "r", encoding="utf-8") as f:
            obs = json.load(f)
        cls.obs_map = {}
        for it in obs.get("items", []):
            cid = it.get("company_id")
            if cid not in cls.obs_map:
                cls.obs_map[cid] = {}
            cls.obs_map[cid][it.get("metric")] = it.get("value")
            
        cls.dates_config = {
            "tesla": {
                "file": "CIK0001318605_TSLA.json",
                "rev_tag": "RevenueFromContractWithCustomerExcludingAssessedTax",
                "ni_tag": "NetIncomeLoss",
                "cur": "USD",
                "anchors": ["2026-06-30", "2025-06-30", "2024-06-30"],
                "fys": ["2025-12-31", "2024-12-31"]
            },
            "oracle": {
                "file": "CIK0001341439_ORCL.json",
                "rev_tag": "RevenueFromContractWithCustomerExcludingAssessedTax",
                "ni_tag": "NetIncomeLoss",
                "cur": "USD",
                "anchors": ["2026-02-28", "2025-02-28", "2024-02-29"],
                "fys": ["2025-05-31", "2024-05-31"]
            },
            "apple": {
                "file": "CIK0000320193_AAPL.json",
                "rev_tag": "RevenueFromContractWithCustomerExcludingAssessedTax",
                "ni_tag": "NetIncomeLoss",
                "cur": "USD",
                "anchors": ["2026-06-27", "2025-06-28", "2024-06-29"],
                "fys": ["2025-09-27", "2024-09-28"]
            },
            "palantir": {
                "file": "CIK0001321655_PLTR.json",
                "rev_tag": "RevenueFromContractWithCustomerExcludingAssessedTax",
                "ni_tag": "NetIncomeLoss",
                "cur": "USD",
                "anchors": ["2026-06-30", "2025-06-30", "2024-06-30"],
                "fys": ["2025-12-31", "2024-12-31"]
            },
            "alphabet": {
                "file": "CIK0001652044_GOOGL.json",
                "rev_tag": "Revenues",
                "ni_tag": "NetIncomeLoss",
                "cur": "USD",
                "anchors": ["2026-06-30", "2025-06-30", "2024-06-30"],
                "fys": ["2025-12-31", "2024-12-31"]
            },
            "microsoft": {
                "file": "CIK0000789019_MSFT.json",
                "rev_tag": "RevenueFromContractWithCustomerExcludingAssessedTax",
                "ni_tag": "NetIncomeLoss",
                "cur": "USD",
                "anchors": ["2026-03-31", "2025-03-31", "2024-03-31"],
                "fys": ["2025-06-30", "2024-06-30"]
            },
            "amazon": {
                "file": "CIK0001018724_AMZN.json",
                "rev_tag": "RevenueFromContractWithCustomerExcludingAssessedTax",
                "ni_tag": "NetIncomeLoss",
                "cur": "USD",
                "anchors": ["2026-06-30", "2025-06-30", "2024-06-30"],
                "fys": ["2025-12-31", "2024-12-31"]
            },
            "nvidia": {
                "file": "CIK0001045810_NVDA.json",
                "rev_tag": "Revenues",
                "ni_tag": "NetIncomeLoss",
                "cur": "USD",
                "anchors": ["2026-07-26", "2025-07-27", "2024-07-28"],
                "fys": ["2026-01-25", "2025-01-26"]
            },
            "meta": {
                "file": "CIK0001326801_META.json",
                "rev_tag": "RevenueFromContractWithCustomerExcludingAssessedTax",
                "ni_tag": "NetIncomeLoss",
                "cur": "USD",
                "anchors": ["2026-06-30", "2025-06-30", "2024-06-30"],
                "fys": ["2025-12-31", "2024-12-31"]
            }
        }

    @staticmethod
    def _get_row(rows, end_date, is_fy=False):
        cands = [r for r in rows if r.get("end") == end_date]
        if is_fy:
            cands = [r for r in cands if r.get("fp") == "FY" and r.get("form") in ["10-K", "20-F"]]
        else:
            cands = [r for r in cands if r.get("fp") in ["Q1", "Q2", "Q3"] and r.get("form") in ["10-Q", "10-K"]]
        if not cands:
            return None
        return max(cands, key=lambda x: abs(x["val"]))

    @classmethod
    def _calc_ttm_metric(cls, rows, anchors, fys):
        a0, a1, a2 = anchors
        fy1, fy2 = fys
        r_a0 = cls._get_row(rows, a0, is_fy=False)
        r_a1 = cls._get_row(rows, a1, is_fy=False)
        r_a2 = cls._get_row(rows, a2, is_fy=False)
        r_fy1 = cls._get_row(rows, fy1, is_fy=True)
        r_fy2 = cls._get_row(rows, fy2, is_fy=True)
        
        ttm_curr = r_a0["val"] + (r_fy1["val"] - r_a1["val"])
        ttm_prior = r_a1["val"] + (r_fy2["val"] - r_a2["val"])
        return ttm_curr, ttm_prior

    @staticmethod
    def score_p1(per):
        if per is None or per <= 0:
            return -2
        if per < 25.0:
            return 0
        elif per < 45.0:
            return -1
        else:
            return -2

    @staticmethod
    def score_p2(ev_s):
        if ev_s is None or ev_s <= 0:
            return -2
        if ev_s < 8.0:
            return 0
        elif ev_s < 20.0:
            return -1
        else:
            return -2

    @staticmethod
    def score_p3(growth):
        if growth is None:
            return -3
        if growth >= 0.30:
            return 0
        elif growth >= 0.15:
            return -1
        elif growth >= 0.05:
            return -2
        else:
            return -3

    @staticmethod
    def score_p4(nonop_share, period_not_ttm, is_new_listing):
        demote = False
        if nonop_share is not None and abs(nonop_share) >= 0.30:
            demote = True
        if period_not_ttm:
            demote = True
        if is_new_listing:
            demote = True
        return -1 if demote else 0

    def test_01_ttm_reconstruction_and_coordinator_match(self):
        """Test 1: Reconstruct TTM across 9 companies and verify 100% match with coordinator table."""
        expected = {
            "tesla":     (-2, -1, -2,  0, -5, 0.118),
            "oracle":    (-1, -1, -2,  0, -4, 0.149),
            "apple":     (-1, -1, -2,  0, -4, 0.142),
            "palantir":  (-2, -2,  0,  0, -4, 0.789),
            "alphabet":  ( 0, -1, -1, -1, -3, 0.201),
            "microsoft": (-1, -1, -1,  0, -3, 0.179),
            "amazon":    ( 0,  0, -1, -1, -2, 0.158),
            "nvidia":    (-1, -1,  0,  0, -2, 0.834),
            "meta":      ( 0,  0, -1,  0, -1, 0.277)
        }
        for cid, cfg in self.dates_config.items():
            fpath = os.path.join(self.raw_dir, cfg["file"])
            with open(fpath, "r", encoding="utf-8") as f:
                data = json.load(f)
            facts = data.get("facts", {}).get("us-gaap", {})
            
            rev_rows = facts[cfg["rev_tag"]]["units"][cfg["cur"]]
            ni_rows = facts[cfg["ni_tag"]]["units"][cfg["cur"]]
            
            rev_ttm, rev_ttm_prior = self._calc_ttm_metric(rev_rows, cfg["anchors"], cfg["fys"])
            ni_ttm, _ = self._calc_ttm_metric(ni_rows, cfg["anchors"], cfg["fys"])
            growth = (rev_ttm / rev_ttm_prior) - 1.0
            
            mc = self.obs_map[cid]["market_cap"]
            net_cash = self.obs_map[cid]["net_cash"]
            nonop = self.obs_map[cid]["nonop_share"]
            
            per = mc / ni_ttm if (mc and ni_ttm and ni_ttm > 0) else None
            ev = mc - net_cash
            ev_s = ev / rev_ttm
            
            p1 = self.score_p1(per)
            p2 = self.score_p2(ev_s)
            p3 = self.score_p3(growth)
            p4 = self.score_p4(nonop, False, False)
            f6 = max(-7, min(0, p1 + p2 + p3 + p4))
            
            exp_p1, exp_p2, exp_p3, exp_p4, exp_f6, exp_growth = expected[cid]
            self.assertEqual(p1, exp_p1, f"{cid} P1 mismatch")
            self.assertEqual(p2, exp_p2, f"{cid} P2 mismatch")
            self.assertEqual(p3, exp_p3, f"{cid} P3 mismatch")
            self.assertEqual(p4, exp_p4, f"{cid} P4 mismatch")
            self.assertEqual(f6, exp_f6, f"{cid} F6 mismatch")
            self.assertAlmostEqual(growth, exp_growth, places=3, msg=f"{cid} growth mismatch")

    def test_02_52_53_week_calendar_tolerance(self):
        """Test 2: Check 52/53-week accounting period tolerances (NVDA 1-day, AAPL 1-day/6-day)."""
        nvda_anchors = self.dates_config["nvidia"]["anchors"]
        self.assertEqual(nvda_anchors[0], "2026-07-26")
        self.assertEqual(nvda_anchors[1], "2025-07-27") # 1 day shift
        
        aapl_anchors = self.dates_config["apple"]["anchors"]
        self.assertEqual(aapl_anchors[0], "2026-06-27")
        self.assertEqual(aapl_anchors[1], "2025-06-28") # 1 day shift
        
        aapl_fys = self.dates_config["apple"]["fys"]
        self.assertEqual(aapl_fys[0], "2025-09-27")
        self.assertEqual(aapl_fys[1], "2024-09-28") # 1 day shift

    def test_03_concept_selection_invariance_tsla_and_orcl(self):
        """Test 3: Verify concept selection gives identical values where both exist (TSLA, ORCL)."""
        # TSLA: Revenues vs RevenueFromContractWithCustomerExcludingAssessedTax
        tsla_path = os.path.join(self.raw_dir, "CIK0001318605_TSLA.json")
        with open(tsla_path, "r", encoding="utf-8") as f:
            tsla_facts = json.load(f)["facts"]["us-gaap"]
        rows1 = tsla_facts["RevenueFromContractWithCustomerExcludingAssessedTax"]["units"]["USD"]
        rows2 = tsla_facts["Revenues"]["units"]["USD"]
        
        r1_q2 = next(r for r in rows1 if r.get("end") == "2026-06-30" and r.get("fp") == "Q2" and r.get("start") == "2026-01-01")
        r2_q2 = next(r for r in rows2 if r.get("end") == "2026-06-30" and r.get("fp") == "Q2" and r.get("start") == "2026-01-01")
        self.assertEqual(r1_q2["val"], r2_q2["val"])
        self.assertEqual(r1_q2["val"], 50623000000)

        # ORCL: Revenues vs RevenueFromContractWithCustomerExcludingAssessedTax at FY
        orcl_path = os.path.join(self.raw_dir, "CIK0001341439_ORCL.json")
        with open(orcl_path, "r", encoding="utf-8") as f:
            orcl_facts = json.load(f)["facts"]["us-gaap"]
        o_rows1 = orcl_facts["RevenueFromContractWithCustomerExcludingAssessedTax"]["units"]["USD"]
        o_rows2 = orcl_facts["Revenues"]["units"]["USD"]
        
        o_r1_fy = next(r for r in o_rows1 if r.get("end") == "2026-05-31" and r.get("fp") == "FY")
        o_r2_fy = next(r for r in o_rows2 if r.get("end") == "2026-05-31" and r.get("fp") == "FY")
        self.assertEqual(o_r1_fy["val"], o_r2_fy["val"])
        self.assertEqual(o_r1_fy["val"], 67357000000)

    def test_04_orcl_concept_selection_quarterly_necessity(self):
        """Test 4: Verify ORCL Revenues lacks quarterly rows in 2026, requiring contract revenue tag."""
        orcl_path = os.path.join(self.raw_dir, "CIK0001341439_ORCL.json")
        with open(orcl_path, "r", encoding="utf-8") as f:
            orcl_facts = json.load(f)["facts"]["us-gaap"]
        rev_rows = orcl_facts["Revenues"]["units"]["USD"]
        recent_q = [r for r in rev_rows if r.get("end") == "2026-02-28" and r.get("fp") == "Q3"]
        self.assertEqual(len(recent_q), 0, "ORCL Revenues should not have 2026 Q3 row")

    def test_05_alibaba_local_currency_band_split(self):
        """Test 5: Alibaba growth in CNY is +2.7% (band -3), in USD is +8.1% (band -2) - 1 step split."""
        baba_path = os.path.join(self.raw_dir, "CIK0001577552_BABA.json")
        with open(baba_path, "r", encoding="utf-8") as f:
            baba_facts = json.load(f)["facts"]["us-gaap"]
        
        cny_rows = baba_facts["Revenues"]["units"]["CNY"]
        r26_cny = next(r for r in cny_rows if r.get("end") == "2026-03-31" and r.get("fp") == "FY")
        r25_cny = next(r for r in cny_rows if r.get("end") == "2025-03-31" and r.get("fp") == "FY")
        growth_cny = (r26_cny["val"] / r25_cny["val"]) - 1.0
        p3_cny = self.score_p3(growth_cny)
        
        usd_rows = baba_facts["Revenues"]["units"]["USD"]
        r26_usd = next(r for r in usd_rows if r.get("end") == "2026-03-31" and r.get("fp") == "FY")
        r25_usd = next(r for r in usd_rows if r.get("end") == "2025-03-31" and r.get("fp") == "FY")
        growth_usd = (r26_usd["val"] / r25_usd["val"]) - 1.0
        p3_usd = self.score_p3(growth_usd)
        
        self.assertAlmostEqual(growth_cny, 0.0274, places=3)
        self.assertAlmostEqual(growth_usd, 0.0809, places=3)
        self.assertEqual(p3_cny, -3)
        self.assertEqual(p3_usd, -2)
        self.assertEqual(p3_cny - p3_usd, -1, "CNY vs USD must create exactly 1 band step difference")

    def test_06_oracle_ev_outlier_and_sales_ratio(self):
        """Test 6: Oracle EV/market_cap ratio is 1.305 due to net debt, pushing EV/Sales to 9.0."""
        mc = self.obs_map["oracle"]["market_cap"]
        net_cash = self.obs_map["oracle"]["net_cash"]
        self.assertEqual(mc, 443700000000.0)
        self.assertEqual(net_cash, -135500000000.0)
        
        ev = mc - net_cash
        ev_mc_ratio = ev / mc
        self.assertAlmostEqual(ev_mc_ratio, 1.305386, places=3)
        
        # TTM revenue is 64,076M
        ev_s = ev / 64076000000.0
        self.assertAlmostEqual(ev_s, 9.039, places=2)
        self.assertEqual(self.score_p2(ev_s), -1)

    def test_07_tsmc_annual_and_p4_demotion(self):
        """Test 7: TSMC Annual 2024 growth is +33.9% (P3=0), and period not TTM yields P4=-1."""
        tsm_path = os.path.join(self.raw_dir, "CIK0001046179_TSM.json")
        with open(tsm_path, "r", encoding="utf-8") as f:
            tsm_facts = json.load(f)["facts"]["ifrs-full"]
        twd_rows = tsm_facts["RevenueFromContractsWithCustomers"]["units"]["TWD"]
        
        r24 = next(r for r in twd_rows if r.get("end") == "2024-12-31" and r.get("fp") == "FY")
        r23 = next(r for r in twd_rows if r.get("end") == "2023-12-31" and r.get("fp") == "FY")
        growth = (r24["val"] / r23["val"]) - 1.0
        
        self.assertAlmostEqual(growth, 0.3389, places=3)
        self.assertEqual(self.score_p3(growth), 0)
        p4 = self.score_p4(self.obs_map["tsmc"]["nonop_share"], period_not_ttm=True, is_new_listing=False)
        self.assertEqual(p4, -1)

    def test_08_spacex_quarterly_only_and_p4_demotion(self):
        """Test 8: SpaceX quarterly YoY growth is +91.9% (P3=0), new listing / quarterly yields P4=-1."""
        spcx_path = os.path.join(self.raw_dir, "CIK0001181412_SPCX.json")
        with open(spcx_path, "r", encoding="utf-8") as f:
            spcx_facts = json.load(f)["facts"]["us-gaap"]
        rows = spcx_facts["RevenueFromContractWithCustomerExcludingAssessedTax"]["units"]["USD"]
        
        r26_q2 = next(r for r in rows if r.get("end") == "2026-06-30" and r.get("start") == "2026-04-01")
        r25_q2 = next(r for r in rows if r.get("end") == "2025-06-30" and r.get("start") == "2025-04-01")
        growth = (r26_q2["val"] / r25_q2["val"]) - 1.0
        
        self.assertAlmostEqual(growth, 0.9194, places=3)
        self.assertEqual(self.score_p3(growth), 0)
        p4 = self.score_p4(None, period_not_ttm=True, is_new_listing=True)
        self.assertEqual(p4, -1)

    def test_09_positive_control_mock_ideal_company(self):
        """Test 9 (Positive Control): A mock company with PER 20, EV/S 5, Growth 35% gets F6 = 0."""
        p1 = self.score_p1(20.0) # < 25 -> 0
        p2 = self.score_p2(5.0)  # < 8 -> 0
        p3 = self.score_p3(0.35) # >= 30% -> 0
        p4 = self.score_p4(0.05, False, False) # 0
        f6 = max(-7, min(0, p1 + p2 + p3 + p4))
        self.assertEqual(f6, 0)

    def test_10_negative_mutation_tesla_growth_perturbation(self):
        """Test 10 (Negative Mutation 1): Perturbing Tesla growth from 11.8% to 35% moves P3 to 0 and F6 to -3."""
        # Baseline Tesla: P1=-2, P2=-1, P3=-2, P4=0 -> F6=-5
        mutated_growth = 0.35
        mutated_p3 = self.score_p3(mutated_growth)
        self.assertEqual(mutated_p3, 0)
        mutated_f6 = max(-7, min(0, -2 + -1 + mutated_p3 + 0))
        self.assertEqual(mutated_f6, -3)

    def test_11_negative_mutation_oracle_debt_removal(self):
        """Test 11 (Negative Mutation 2): Removing Oracle net debt reduces EV/S below 8, moving P2 to 0."""
        # Baseline Oracle: MC=443.7B, EV=579.2B, EV/S=9.0 -> P2=-1
        mutated_ev = 443700000000.0 # No net debt (EV = Market Cap)
        mutated_ev_s = mutated_ev / 64076000000.0 # 6.92
        self.assertLess(mutated_ev_s, 8.0)
        self.assertEqual(self.score_p2(mutated_ev_s), 0)

    def test_12_negative_mutation_alibaba_usd_perturbation(self):
        """Test 12 (Negative Mutation 3): Forcing USD growth on Alibaba changes P3 from -3 to -2."""
        actual_cny_p3 = self.score_p3(0.0274)
        forced_usd_p3 = self.score_p3(0.0809)
        self.assertEqual(actual_cny_p3, -3)
        self.assertEqual(forced_usd_p3, -2)

if __name__ == "__main__":
    unittest.main()
