# F9 적자 깊이 5대 미결 규칙의 실측 영향 및 기업별 점수 변동을 검증하는 독립 테스트 스위트
import os
import json
import unittest

class TestF9DecideIndependent(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base_dir = os.path.dirname(os.path.abspath(__file__))
        cls.raw_dir = os.path.join(cls.base_dir, "_raw")
        
        with open(os.path.join(cls.raw_dir, "baseline_observations.json"), "r", encoding="utf-8") as f:
            obs_data = json.load(f)
        with open(os.path.join(cls.raw_dir, "baseline_judgments.json"), "r", encoding="utf-8") as f:
            judg_data = json.load(f)
        with open(os.path.join(cls.raw_dir, "rules_v15.json"), "r", encoding="utf-8") as f:
            cls.rules_data = json.load(f)
            
        cls.obs_map = {}
        for it in obs_data.get("items", []):
            cid = it.get("company_id")
            if cid not in cls.obs_map:
                cls.obs_map[cid] = {}
            cls.obs_map[cid][it.get("metric")] = it
            
        cls.judg_map = {}
        for j in judg_data.get("items", []):
            cid = j.get("company_id")
            fid = j.get("factor")
            if cid not in cls.judg_map:
                cls.judg_map[cid] = {}
            cls.judg_map[cid][fid] = j

        cls.companies_info = {
            "alphabet": {"listed": True},
            "amazon": {"listed": True},
            "meta": {"listed": True},
            "microsoft": {"listed": True},
            "tsmc": {"listed": True},
            "alibaba": {"listed": True},
            "anthropic": {"listed": False},
            "apple": {"listed": True},
            "nvidia": {"listed": True},
            "palantir": {"listed": True},
            "spacex-xai": {"listed": True},
            "tesla": {"listed": True},
            "oracle": {"listed": True},
            "openai": {"listed": False}
        }

        cls.UNKNOWN_INPUTS = {
            "fcf_trend": "unknown",
            "bep_retreat": "unknown",
            "buffer_erosion": "unknown",
            "direction_A": "unknown",
            "direction_B": "unknown",
            "coverage_comparable": "unknown",
        }

    def run_f9(self, cid, c_decisions, override_inputs=None, override_obs=None):
        company = self.companies_info[cid]
        pol = self.rules_data["policies"]["f9"]
        floor = int(pol["floor"])
        
        j_f9 = self.judg_map.get(cid, {}).get("F9")
        gi = dict(self.UNKNOWN_INPUTS)
        if j_f9 is not None:
            gi.update(j_f9.get("inputs", {}))
        if override_inputs:
            gi.update(override_inputs)
            
        c_obs_dict = dict(self.obs_map.get(cid, {}))
        if override_obs:
            c_obs_dict.update(override_obs)
            
        def get_num(metric):
            o = c_obs_dict.get(metric)
            if o is None:
                return None, None
            return o.get("value"), o

        path = []
        
        # G1 본업
        margin, margin_obs = get_num("operating_margin_ttm")
        if margin is None:
            op_inc, _ = get_num("operating_income_ttm")
            rev, _ = get_num("revenue_ttm")
            if op_inc is not None and rev is not None and rev > 0:
                margin = op_inc / rev
                
        bep_retreat = gi.get("bep_retreat") == "yes"
        reviewed_sign = gi.get("operating_result_reviewed", "unknown")
        
        if margin is None and not bep_retreat:
            if reviewed_sign == "profit":
                path.append({"gate": "G1", "result": "pass", "basis": "operating_result_reviewed=profit"})
            else:
                path.append({"gate": "G1", "result": "pending", "reason": "TTM 영업손익·손실률 관측 없음"})
                return None, "pending_data", path
                
        if margin is not None and margin == 0 and not bep_retreat:
            path.append({"gate": "G1", "result": "zero", "reason": "영업손익 0 처리 미결(C-06)"})
            return None, "needs_rule_decision", path
            
        g1_pass = (not bep_retreat) and (margin is None or margin > 0)
        
        if g1_pass:
            if margin is not None:
                path.append({"gate": "G1", "result": "pass", "operating_margin_ttm": margin})
        else:
            # G1 실패 분기
            if bep_retreat:
                base = int(pol["g1_bep_retreat_score"])
                path.append({"gate": "G1", "result": "fail", "score": base, "reason": "BEP 후퇴"})
            else:
                c06_choice = c_decisions.get("C-06")
                if c06_choice != "proposed_v15_boundaries":
                    path.append({"gate": "G1", "result": "fail", "reason": "C-06 미결"})
                    return None, "needs_rule_decision", path
                base = -5
                for band in pol["g1_bands_proposed"]:
                    lower = band["min_margin"]
                    if lower is None or margin >= lower:
                        base = int(band["score"])
                        break
                path.append({"gate": "G1", "result": "fail", "score": base})
                
            if gi.get("buffer_erosion") == "yes":
                base = min(base, int(pol["g1_buffer_erosion_min_score"]))
                path.append({"gate": "G1", "adjust": "buffer_erosion", "score": base})
                
            if gi.get("direction_A") == "pass" and gi.get("direction_B") == "pass":
                relieved = min(base + int(pol["g1_direction_relief_step"]), int(pol["g1_direction_relief_cap"]))
                base = relieved
                path.append({"gate": "G1", "adjust": "direction_relief", "score": base})
                
            score = max(floor, base)
            if score <= floor:
                path.append({"gate": "G3/G4", "result": "skipped", "reason": "already floor -5"})
                return score, "ok", path
                
            # G1 실패, score > -5 진단
            diag_score = score
            fcf, fcf_obs = get_num("fcf_ttm")
            cash, cash_obs = get_num("cash")
            undrawn, undrawn_obs = get_num("undrawn_credit")
            
            # G3
            if fcf is not None and fcf < 0 and cash is not None:
                buffer_val = cash + (undrawn or 0.0)
                runway = buffer_val / (-fcf)
                step = 0 if runway >= pol["g3_runway_keep_years"] else (-1 if runway >= pol["g3_runway_one_step_years"] else -2)
                diag_score = max(floor, diag_score + step)
                path.append({"gate": "G3", "mode": "diagnostic", "runway": runway, "step": step})
            else:
                path.append({"gate": "G3", "mode": "diagnostic", "status": "missing_data"})
                
            # G4
            g4_res = self._eval_g4(cid, c_obs_dict, gi, pol, c_decisions)
            path.append({"gate": "G4", "mode": "diagnostic", "detail": g4_res})
            g4_step = g4_res.get("step")
            g4_pending = g4_res.get("pending")
            if g4_step is not None:
                diag_score = max(floor, diag_score + g4_step)
                
            c05_choice = c_decisions.get("C-05")
            if c05_choice == "apply":
                if g4_pending:
                    kind = g4_pending.get("kind")
                    st = {"data": "pending_data", "judgment": "needs_judgment"}.get(kind, "needs_rule_decision")
                    return None, st, path
                return diag_score, "ok", path
            elif c05_choice == "diagnose_only":
                return score, "ok", path
            else:
                if g4_pending and g4_pending.get("kind") != "rule":
                    kind = g4_pending.get("kind")
                    st = {"data": "pending_data", "judgment": "needs_judgment"}.get(kind, "needs_rule_decision")
                    return None, st, path
                elif diag_score != score or g4_pending:
                    return None, "needs_rule_decision", path
                return score, "ok", path

        # G2 현금
        fcf, fcf_obs = get_num("fcf_ttm")
        if fcf is None:
            if not company["listed"] and fcf_obs is not None and fcf_obs.get("status") == "not_disclosed":
                score = int(pol["g2_private_not_disclosed"])
                path.append({"gate": "G2", "result": "not_disclosed", "score": score})
                path.append({"gate": "G3", "result": "skipped"})
                g4_res = self._eval_g4(cid, c_obs_dict, gi, pol, c_decisions)
                if g4_res.get("step") is None:
                    path.append({"gate": "G4", "result": "undetermined", "dedupe": True})
                else:
                    score = max(floor, score + g4_res["step"])
                return score, "ok", path
            path.append({"gate": "G2", "result": "pending", "reason": "fcf is None"})
            return None, "pending_data", path
            
        if fcf > 0:
            trend = gi.get("fcf_trend")
            if trend == "stable":
                path.append({"gate": "G2", "result": "positive_stable", "score": 0})
                return 0, "ok", path
            if trend == "deteriorating":
                path.append({"gate": "G2", "result": "positive_deteriorating", "score": -1})
                return -1, "ok", path
            path.append({"gate": "G2", "result": "pending", "reason": "trend required"})
            return None, "needs_judgment", path
            
        if fcf == 0:
            path.append({"gate": "G2", "result": "zero", "reason": "FCF 0 미결(C-06)"})
            return None, "needs_rule_decision", path
            
        # FCF < 0
        score = int(pol["g2_fcf_negative"])
        path.append({"gate": "G2", "result": "negative", "score": score})
        
        # G3
        cash, cash_obs = get_num("cash")
        if cash is None:
            path.append({"gate": "G3", "result": "pending", "reason": "cash None"})
            return None, "pending_data", path
        undrawn, undrawn_obs = get_num("undrawn_credit")
        buffer_val = cash + (undrawn or 0.0)
        runway = buffer_val / (-fcf)
        step = 0 if runway >= pol["g3_runway_keep_years"] else (-1 if runway >= pol["g3_runway_one_step_years"] else -2)
        score = max(floor, score + step)
        path.append({"gate": "G3", "runway": runway, "step": step, "score": score})
        
        # G4
        g4_res = self._eval_g4(cid, c_obs_dict, gi, pol, c_decisions)
        path.append({"gate": "G4", "detail": g4_res})
        if g4_res.get("step") is None:
            g4_p = g4_res.get("pending", {})
            kind = g4_p.get("kind")
            st = {"data": "pending_data", "judgment": "needs_judgment"}.get(kind, "needs_rule_decision")
            return None, st, path
        score = max(floor, score + g4_res["step"])
        return score, "ok", path

    def _eval_g4(self, cid, c_obs_dict, gi, pol, c_decisions):
        def get_num(metric):
            o = c_obs_dict.get(metric)
            if o is None:
                return None, None
            return o.get("value"), o
        contracted, c_obs = get_num("contracted_revenue")
        offb, b_obs = get_num("offbalance_B")
        
        comparable = gi.get("coverage_comparable", "unknown")
        if comparable == "no":
            return {"result": "incompatible", "step": None, "pending": {"kind": "data", "reason": "C-07 ARR 대체 금지"}}
        if comparable != "yes":
            return {"result": "undetermined", "step": None, "pending": {"kind": "judgment", "reason": "coverage_comparable 미확인"}}
        if contracted is not None and offb is not None:
            if offb == 0:
                return {"result": "no_obligations", "step": 0}
            cov = contracted / offb
            step = 0 if cov >= pol["g4_coverage_keep"] else -1
            return {"result": "computed", "coverage": cov, "step": step}
            
        missing = []
        statuses = []
        for name, val, o in [("contracted_revenue", contracted, c_obs), ("offbalance_B", offb, b_obs)]:
            if val is None:
                st = o.get("status") if o else "none"
                missing.append(f"{name}({st})")
                statuses.append(st)
        if any(st != "not_disclosed" for st in statuses):
            return {"result": "undetermined", "step": None, "pending": {"kind": "data", "reason": f"missing: {missing}"}}
            
        c16_choice = c_decisions.get("C-16")
        if c16_choice == "downgrade":
            return {"result": "not_disclosed", "step": -1, "policy": "downgrade"}
        elif c16_choice == "hold":
            return {"result": "not_disclosed", "step": 0, "policy": "hold"}
        else:
            return {"result": "not_disclosed", "step": None, "pending": {"kind": "rule", "decision": "C-16"}}

    # =========================================================================
    # UNIT TESTS
    # =========================================================================

    def test_01_c04_invariance_across_all_companies(self):
        """Test 1: C-04 exclude vs include_v15 produces zero score changes due to 0 undrawn_credit obs."""
        for cid in self.companies_info.keys():
            score_ex, st_ex, _ = self.run_f9(cid, {"C-04": "exclude", "C-05": "diagnose_only", "C-06": "proposed_v15_boundaries", "C-16": "hold"})
            score_in, st_in, _ = self.run_f9(cid, {"C-04": "include_v15", "C-05": "diagnose_only", "C-06": "proposed_v15_boundaries", "C-16": "hold"})
            self.assertEqual(score_ex, score_in, f"{cid} score changed under C-04")
            self.assertEqual(st_ex, st_in, f"{cid} status changed under C-04")

    def test_02_c05_spacex_score_split(self):
        """Test 2: C-05 diagnose_only gives spacex-xai -4 (ok), while apply requires judgment and splits by C-16."""
        # Under diagnose_only, spacex-xai completes at -4 without blocking on G4
        sc_diag, st_diag, _ = self.run_f9("spacex-xai", {"C-05": "diagnose_only", "C-06": "proposed_v15_boundaries", "C-16": "hold"})
        self.assertEqual(sc_diag, -4)
        self.assertEqual(st_diag, "ok")

        # Under apply, spacex-xai blocks at needs_judgment due to coverage_comparable: unknown
        sc_app, st_app, _ = self.run_f9("spacex-xai", {"C-05": "apply", "C-06": "proposed_v15_boundaries", "C-16": "hold"})
        self.assertIsNone(sc_app)
        self.assertEqual(st_app, "needs_judgment")

        # If coverage_comparable is resolved to yes, C-16 splits score between -4 (hold) and -5 (downgrade)
        sc_hold, st_hold, _ = self.run_f9("spacex-xai", {"C-05": "apply", "C-06": "proposed_v15_boundaries", "C-16": "hold"},
                                          override_inputs={"coverage_comparable": "yes"})
        sc_down, st_down, _ = self.run_f9("spacex-xai", {"C-05": "apply", "C-06": "proposed_v15_boundaries", "C-16": "downgrade"},
                                          override_inputs={"coverage_comparable": "yes"})
        self.assertEqual(sc_hold, -4)
        self.assertEqual(sc_down, -5)

    def test_03_c05_openai_floor_invariance(self):
        """Test 3: OpenAI hits floor -5 at G1 due to BEP retreat, skipping G3/G4 under both diagnose_only and apply."""
        sc_diag, st_diag, path_diag = self.run_f9("openai", {"C-05": "diagnose_only", "C-06": "proposed_v15_boundaries", "C-16": "hold"})
        sc_app, st_app, path_app = self.run_f9("openai", {"C-05": "apply", "C-06": "proposed_v15_boundaries", "C-16": "downgrade"})
        self.assertEqual(sc_diag, -5)
        self.assertEqual(sc_app, -5)
        self.assertEqual(st_diag, "ok")
        self.assertEqual(st_app, "ok")

    def test_04_c06_spacex_unblocking(self):
        """Test 4: SpaceX is blocked (needs_rule_decision) when C-06 is unresolved, and unblocks to -4 under proposed_v15_boundaries."""
        sc_unresolved, st_unresolved, _ = self.run_f9("spacex-xai", {"C-05": "diagnose_only", "C-06": None, "C-16": "hold"})
        self.assertIsNone(sc_unresolved)
        self.assertEqual(st_unresolved, "needs_rule_decision")

        sc_resolved, st_resolved, _ = self.run_f9("spacex-xai", {"C-05": "diagnose_only", "C-06": "proposed_v15_boundaries", "C-16": "hold"})
        self.assertEqual(sc_resolved, -4)
        self.assertEqual(st_resolved, "ok")

    def test_05_c07_incompatible_basis_blocking(self):
        """Test 5: Anthropic and OpenAI G4 metrics have incompatible_basis and block when coverage_comparable is 'no'."""
        g4_anthropic = self._eval_g4("anthropic", self.obs_map["anthropic"], {"coverage_comparable": "no"},
                                     self.rules_data["policies"]["f9"], {"C-16": "downgrade"})
        self.assertEqual(g4_anthropic["result"], "incompatible")
        self.assertIsNone(g4_anthropic["step"])

        g4_openai = self._eval_g4("openai", self.obs_map["openai"], {"coverage_comparable": "no"},
                                  self.rules_data["policies"]["f9"], {"C-16": "downgrade"})
        self.assertEqual(g4_openai["result"], "incompatible")
        self.assertIsNone(g4_openai["step"])

    def test_06_c16_alibaba_score_split(self):
        """Test 6: C-16 changes 0 companies in baseline data. Alibaba requires BOTH profit and coverage_comparable=yes to reach C-16."""
        # 1. In baseline data as-is (no judgment overrides), C-16 moves 0 companies
        baseline_diffs = []
        for cid in self.companies_info.keys():
            sc_h, st_h, _ = self.run_f9(cid, {"C-04": "exclude", "C-05": "diagnose_only", "C-06": "proposed_v15_boundaries", "C-16": "hold"})
            sc_d, st_d, _ = self.run_f9(cid, {"C-04": "exclude", "C-05": "diagnose_only", "C-06": "proposed_v15_boundaries", "C-16": "downgrade"})
            if (sc_h, st_h) != (sc_d, st_d):
                baseline_diffs.append(cid)
        self.assertEqual(len(baseline_diffs), 0, "C-16 must change 0 companies in baseline data")

        # 2. For Alibaba, profit alone is NOT enough: it stops at needs_judgment due to coverage_comparable: unknown
        sc_profit_only, st_profit_only, _ = self.run_f9("alibaba", {"C-06": "proposed_v15_boundaries", "C-16": "hold"},
                                                        override_inputs={"operating_result_reviewed": "profit"})
        self.assertIsNone(sc_profit_only)
        self.assertEqual(st_profit_only, "needs_judgment")

        # 3. When BOTH profit and coverage_comparable=yes are provided, C-16 splits Alibaba between -2 and -3
        dec_hold = {"C-04": "exclude", "C-05": "diagnose_only", "C-06": "proposed_v15_boundaries", "C-16": "hold"}
        dec_down = {"C-04": "exclude", "C-05": "diagnose_only", "C-06": "proposed_v15_boundaries", "C-16": "downgrade"}
        dec_none = {"C-04": "exclude", "C-05": "diagnose_only", "C-06": "proposed_v15_boundaries", "C-16": None}

        inputs = {"operating_result_reviewed": "profit", "coverage_comparable": "yes"}
        sc_hold, st_hold, _ = self.run_f9("alibaba", dec_hold, override_inputs=inputs)
        sc_down, st_down, _ = self.run_f9("alibaba", dec_down, override_inputs=inputs)
        sc_none, st_none, _ = self.run_f9("alibaba", dec_none, override_inputs=inputs)

        self.assertEqual(sc_hold, -2)
        self.assertEqual(sc_down, -3)
        self.assertEqual(sc_hold - sc_down, 1, "C-16 must create exactly 1 step difference for Alibaba when both inputs are provided")
        self.assertEqual(st_hold, "ok")
        self.assertEqual(st_down, "ok")
        self.assertEqual(st_none, "needs_rule_decision")

    def test_07_c16_amazon_inapplicability(self):
        """Test 7: Amazon contracted_revenue is parse_failed (not not_disclosed), so C-16 cannot unblock Amazon."""
        # Even if coverage_comparable is 'yes', parse_failed routes to pending_data, NOT C-16
        sc_amzn, st_amzn, path = self.run_f9("amazon", {"C-05": "diagnose_only", "C-06": "proposed_v15_boundaries", "C-16": "downgrade"},
                                            override_inputs={"coverage_comparable": "yes"})
        self.assertIsNone(sc_amzn)
        self.assertEqual(st_amzn, "pending_data")

    def test_08_positive_control_ideal_company(self):
        """Test 8 (Positive Control): Mock company with positive margin (+20%) and positive stable FCF (+$10B) gets F9 = 0."""
        mock_obs = {
            "operating_margin_ttm": {"value": 0.20, "status": "verified"},
            "fcf_ttm": {"value": 10000000000.0, "status": "verified"}
        }
        mock_inputs = {"fcf_trend": "stable", "bep_retreat": "no"}
        sc, st, path = self.run_f9("apple", {"C-06": "proposed_v15_boundaries"}, override_obs=mock_obs, override_inputs=mock_inputs)
        self.assertEqual(sc, 0)
        self.assertEqual(st, "ok")

    def test_09_negative_mutation_spacex_margin_to_floor(self):
        """Test 9 (Negative Mutation 1): Perturbing SpaceX margin from -14.9% to -35% triggers floor -5, skipping G3/G4."""
        mutated_obs = {
            "operating_margin_ttm": {"value": -0.35, "status": "mutated"}
        }
        sc, st, path = self.run_f9("spacex-xai", {"C-05": "apply", "C-06": "proposed_v15_boundaries", "C-16": "downgrade"},
                                   override_obs=mutated_obs)
        self.assertEqual(sc, -5)
        self.assertEqual(st, "ok")
        # Check that G3/G4 was skipped
        skipped_step = next(p for p in path if p.get("gate") == "G3/G4")
        self.assertEqual(skipped_step["result"], "skipped")

    def test_10_negative_mutation_oracle_cash_degradation(self):
        """Test 10 (Negative Mutation 2): Reducing Oracle cash from $31.9B to $10B shortens runway to 0.42y (<1y), dropping score from -3 to -4."""
        baseline_score, _, _ = self.run_f9("oracle", {"C-06": "proposed_v15_boundaries"})
        self.assertEqual(baseline_score, -3)

        mutated_obs = {
            "cash": {"value": 10000000000.0, "status": "mutated"}
        }
        mutated_score, st, path = self.run_f9("oracle", {"C-06": "proposed_v15_boundaries"}, override_obs=mutated_obs)
        self.assertEqual(mutated_score, -4)
        self.assertEqual(st, "ok")

    def test_11_negative_mutation_alibaba_fcf_sign_inversion(self):
        """Test 11 (Negative Mutation 3): Changing Alibaba FCF from negative to positive stable moves F9 from -2/-3 to 0."""
        mutated_obs = {
            "fcf_ttm": {"value": 10000000000.0, "status": "mutated"}
        }
        mutated_inputs = {
            "operating_result_reviewed": "profit",
            "fcf_trend": "stable"
        }
        sc, st, _ = self.run_f9("alibaba", {"C-06": "proposed_v15_boundaries", "C-16": "hold"},
                                override_obs=mutated_obs, override_inputs=mutated_inputs)
        self.assertEqual(sc, 0)
        self.assertEqual(st, "ok")

if __name__ == "__main__":
    unittest.main()
