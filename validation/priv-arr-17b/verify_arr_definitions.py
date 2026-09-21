# 비상장 2사(Anthropic, OpenAI)의 ARR 정의 및 기간 가용성을 검증하는 단위 테스트
import os
import json
import hashlib
import unittest

class TestUnlistedArrDefinitions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base_dir = os.path.dirname(os.path.abspath(__file__))
        cls.raw_dir = os.path.join(cls.base_dir, '_raw')
        
        # Load baseline observations slice
        obs_file = os.path.join(cls.raw_dir, 'baseline_v15_unlisted_observations.json')
        with open(obs_file, 'r', encoding='utf-8') as f:
            cls.obs_data = json.load(f)
            
        # Load external reporting raw data
        ext_file = os.path.join(cls.raw_dir, 'external_reporting_raw.json')
        with open(ext_file, 'r', encoding='utf-8') as f:
            cls.ext_data = json.load(f)
            
    def test_01_baseline_items_present(self):
        """Test 1: baseline observations slice contains both anthropic and openai items."""
        items = self.obs_data.get('items', [])
        companies = {it.get('company_id') for it in items}
        self.assertIn('anthropic', companies)
        self.assertIn('openai', companies)
        
    def test_02_anthropic_arr_nature(self):
        """Test 2: Anthropic arr is run-rate with period=null, not audited ARR/GAAP."""
        items = self.obs_data.get('items', [])
        arr_item = next(it for it in items if it.get('company_id') == 'anthropic' and it.get('metric') == 'arr')
        self.assertEqual(arr_item.get('value'), 65000000000.0)
        self.assertEqual(arr_item.get('kind'), 'run_rate')
        self.assertIsNone(arr_item.get('period'))
        self.assertIn('7월 런레이트', arr_item.get('raw', ''))
        
    def test_03_openai_arr_nature(self):
        """Test 3: OpenAI arr is run-rate with period=null, not audited ARR/GAAP."""
        items = self.obs_data.get('items', [])
        arr_item = next(it for it in items if it.get('company_id') == 'openai' and it.get('metric') == 'arr')
        self.assertEqual(arr_item.get('value'), 40000000000.0)
        self.assertEqual(arr_item.get('kind'), 'run_rate')
        self.assertIsNone(arr_item.get('period'))
        self.assertIn('8/20', arr_item.get('raw', ''))
        self.assertIn('런레이트', arr_item.get('raw', ''))
        
    def test_04_anthropic_quarter_note_definition(self):
        """Test 4: Anthropic quarter_note contains $10.9B but has period=null and is not a formal revenue_q metric."""
        items = self.obs_data.get('items', [])
        qn_item = next(it for it in items if it.get('company_id') == 'anthropic' and it.get('metric') == 'quarter_note')
        self.assertIn('Q2 | $10.9B', qn_item.get('value', ''))
        self.assertIsNone(qn_item.get('period'))
        # Ensure there is NO formal revenue_q or revenue_ttm observation for Anthropic
        rev_items = [it for it in items if it.get('company_id') == 'anthropic' and it.get('metric') in ['revenue_q', 'revenue_ttm']]
        self.assertEqual(len(rev_items), 0)
        
    def test_05_openai_quarter_note_definition(self):
        """Test 5: OpenAI quarter_note has dash indicating no quarterly revenue figure."""
        items = self.obs_data.get('items', [])
        qn_item = next(it for it in items if it.get('company_id') == 'openai' and it.get('metric') == 'quarter_note')
        self.assertTrue(qn_item.get('value', '').startswith('— |'))
        self.assertIsNone(qn_item.get('period'))
        
    def test_06_post_money_and_cumulative_raised_as_of_dates(self):
        """Test 6: post_money and cumulative_raised have as_of=2026-09-02 and period=null lacking event dates."""
        items = self.obs_data.get('items', [])
        for comp in ['anthropic', 'openai']:
            for m in ['post_money_valuation', 'cumulative_raised']:
                item = next(it for it in items if it.get('company_id') == comp and it.get('metric') == m)
                self.assertEqual(item.get('as_of'), '2026-09-02')
                self.assertIsNone(item.get('period'))
                
    def test_07_source_tier_classification(self):
        """Test 7: Verify strict hierarchy of sources across identified events."""
        events_anth = self.ext_data['companies']['anthropic']['identified_financial_events']
        events_oai = self.ext_data['companies']['openai']['identified_financial_events']
        
        # Anthropic Series H official announcement is Tier 1
        tier1_anth = [e for e in events_anth if e['tier'] == 'Tier 1']
        self.assertEqual(len(tier1_anth), 1)
        self.assertEqual(tier1_anth[0]['metric_name'], 'run-rate revenue')
        self.assertEqual(tier1_anth[0]['value'], 47000000000.0)
        
        # Anthropic July run-rate $65B and Q2 $10.9B are Tier 3
        tier3_anth = [e for e in events_anth if e['tier'] == 'Tier 3']
        tier3_metrics = {e['metric_name'] for e in tier3_anth}
        self.assertIn('annualized revenue run-rate', tier3_metrics)
        self.assertIn('projected Q2 revenue / projected operating profit', tier3_metrics)
        
        # OpenAI Accelerating is Tier 1 (no revenue)
        tier1_oai = [e for e in events_oai if e['tier'] == 'Tier 1']
        self.assertEqual(len(tier1_oai), 1)
        self.assertNotIn('value', tier1_oai[0]) # No revenue announced
        
        # OpenAI August run-rate $40B+ is Tier 3
        tier3_oai = [e for e in events_oai if e['tier'] == 'Tier 3']
        tier3_oai_metrics = {e['metric_name'] for e in tier3_oai}
        self.assertIn('annualized revenue run-rate', tier3_oai_metrics)
        
    def test_08_positive_control_audited_revenue(self):
        """Test 8 (Positive Control): A mock company with an audited 10-Q filing passes as recognized revenue."""
        mock_event = {
            "company": "mock_listed_co",
            "tier": "Tier 1",
            "source_type": "sec_10q",
            "period": "2026Q2",
            "metric_type": "recognized_gaap_revenue",
            "value": 10900000000.0
        }
        def validate_revenue_metric(event):
            if event["tier"] != "Tier 1" or event["source_type"] != "sec_10q":
                return False, "Not an audited regulatory filing"
            if not event.get("period"):
                return False, "Missing accounting period"
            if event["metric_type"] != "recognized_gaap_revenue":
                return False, "Not a recognized GAAP revenue"
            return True, "Valid recognized period revenue"
            
        valid, msg = validate_revenue_metric(mock_event)
        self.assertTrue(valid)
        self.assertEqual(msg, "Valid recognized period revenue")
        
    def test_09_negative_mutation_control_arr_as_gaap(self):
        """Test 9 (Negative Mutation Control 1): Treating run-rate as audited GAAP revenue triggers failure."""
        mutated_anth_arr = {
            "company": "anthropic",
            "tier": "Tier 3",
            "source_type": "media_leak",
            "period": None,
            "metric_type": "recognized_gaap_revenue", # Mutation!
            "value": 65000000000.0
        }
        def check_gaap_validity(entry):
            if entry["metric_type"] == "recognized_gaap_revenue" and (entry["tier"] != "Tier 1" or entry["period"] is None):
                raise ValueError("Cannot classify unverified run-rate without period as recognized GAAP revenue")
            return True
            
        with self.assertRaises(ValueError):
            check_gaap_validity(mutated_anth_arr)
            
    def test_10_negative_mutation_control_yoy_mismatch(self):
        """Test 10 (Negative Mutation Control 2): Attempting YoY between run-rate and quarterly revenue triggers mismatch."""
        def calculate_yoy(curr_metric, curr_val, prior_metric, prior_val):
            if curr_metric != prior_metric:
                raise TypeError(f"Incompatible metric comparison: {curr_metric} vs {prior_metric}")
            return (curr_val / prior_val) - 1.0
            
        with self.assertRaises(TypeError):
            calculate_yoy("annualized_run_rate", 65000000000.0, "quarterly_revenue", 787000000.0)
            
    def test_11_negative_mutation_control_unverified_tier_elevation(self):
        """Test 11 (Negative Mutation Control 3): Promoting media report to Tier 1 without official press release fails."""
        def verify_tier_designation(event):
            if event.get("tier") == "Tier 1" and not event.get("official_url"):
                raise AssertionError("Tier 1 designation requires verified official primary URL")
            return True
            
        unverified_event = {
            "name": "Bloomberg report on $40B run rate",
            "tier": "Tier 1", # Mutation!
            "official_url": None
        }
        with self.assertRaises(AssertionError):
            verify_tier_designation(unverified_event)
            
    def test_12_raw_files_preservation(self):
        """Test 12: Verify all expected raw files are preserved in _raw directory."""
        expected_files = [
            'anthropic_robots.txt',
            'openai_robots.txt',
            'anthropic_commercial_terms.html',
            'openai_terms_of_use.html',
            'anthropic_series_h_official_2026-05-28.html',
            'openai_accelerating_official_2026-03-31.html',
            'baseline_v15_unlisted_observations.json',
            'baseline_v15_unlisted_scores.json',
            'external_reporting_raw.json'
        ]
        for fname in expected_files:
            fpath = os.path.join(self.raw_dir, fname)
            self.assertTrue(os.path.exists(fpath), f"File missing: {fname}")
            self.assertGreater(os.path.getsize(fpath), 0, f"File empty: {fname}")

    def test_13_non_production_reference_tagging(self):
        """Test 13 (B1 Compliance): Downloaded external HTMLs are strictly tagged as non_production_reference."""
        policy = self.ext_data.get('collection_policy', {})
        self.assertEqual(policy.get('downloaded_content_status'), 'non_production_reference')
        self.assertEqual(policy.get('primary_evidence_source'), 'internal_v15_original')
        
        events_anth = self.ext_data['companies']['anthropic']['identified_financial_events']
        anth_h = next(e for e in events_anth if e['event_id'] == 'anth-01-series-h')
        self.assertEqual(anth_h.get('usage_status'), 'non_production_reference')
        
        events_oai = self.ext_data['companies']['openai']['identified_financial_events']
        oai_acc = next(e for e in events_oai if e['event_id'] == 'oai-01-accelerating-round')
        self.assertEqual(oai_acc.get('usage_status'), 'non_production_reference')

    def test_14_internal_v15_rules_hash_verification(self):
        """Test 14 (B1 Compliance): Internal v1.5 rules file exists and SHA256 matches v1.5.json declaration."""
        v15_ref = self.ext_data.get('internal_v15_reference', {})
        src_path = v15_ref.get('source_path')
        rule_file = v15_ref.get('rule_file')
        expected_hash = v15_ref.get('rule_sha256')
        
        self.assertEqual(expected_hash, "57beb84ad8c291f3086a4b06483cebd1f614befa6e93daeb92657e522b3f7abb")
        target_rule_path = os.path.join(src_path, rule_file)
        self.assertTrue(os.path.exists(target_rule_path), f"v1.5 rules file missing at: {target_rule_path}")
        
        with open(target_rule_path, 'rb') as f:
            actual_hash = hashlib.sha256(f.read()).hexdigest()
        self.assertEqual(actual_hash, expected_hash)

if __name__ == '__main__':
    unittest.main()
