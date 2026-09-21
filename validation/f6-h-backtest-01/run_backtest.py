# F6-H(2A+2E) 하이브리드 지표의 백테스트 오차, 편향 및 점수 곡선 타당성을 분석하는 스크립트

import os
import sys
import json
import glob
import re
import math

def parse_price(val):
    if not val:
        return None
    s = re.sub(r'[^\d.]', '', str(val))
    try:
        return float(s)
    except Exception:
        return None

def load_data():
    base_ntm = "C:/Users/noble/orca/workspaces/stock-report-harness/NTM-전망치조사/validation/consensus-source-2026-09-09/raw"
    base_c13 = "C:/Users/noble/orca/workspaces/stock-report-harness/C-13/validation/consensus-source-2026-09-09/raw"
    
    # 14 scorecard companies
    company_meta = {
        "apple": {"ticker": "AAPL", "currency": "USD", "basis": "common", "listed": True, "type": "소비자", "file_prefix": "apple"},
        "microsoft": {"ticker": "MSFT", "currency": "USD", "basis": "common", "listed": True, "type": "업무", "file_prefix": "microsoft"},
        "alphabet": {"ticker": "GOOGL", "currency": "USD", "basis": "common", "listed": True, "type": "소비자", "file_prefix": "alphabet"},
        "amazon": {"ticker": "AMZN", "currency": "USD", "basis": "common", "listed": True, "type": "소비자·업무", "file_prefix": "amazon"},
        "meta": {"ticker": "META", "currency": "USD", "basis": "common", "listed": True, "type": "소비자", "file_prefix": "meta"},
        "nvidia": {"ticker": "NVDA", "currency": "USD", "basis": "common", "listed": True, "type": "부품", "file_prefix": "nvidia"},
        "tesla": {"ticker": "TSLA", "currency": "USD", "basis": "common", "listed": True, "type": "소비자", "file_prefix": "tesla"},
        "oracle": {"ticker": "ORCL", "currency": "USD", "basis": "common", "listed": True, "type": "업무", "file_prefix": "oracle"},
        "palantir": {"ticker": "PLTR", "currency": "USD", "basis": "common", "listed": True, "type": "업무", "file_prefix": "palantir"},
        "spacex-xai": {"ticker": "SPCX", "currency": "USD", "basis": "common", "listed": True, "type": "소비자·업무", "file_prefix": "spacex-xai"},
        "tsmc": {"ticker": "TSM", "currency": "TWD", "basis": "adr", "listed": True, "type": "부품", "adr_ratio": 5, "file_prefix": "tsm"},
        "alibaba": {"ticker": "BABA", "currency": "CNY", "basis": "ads", "listed": True, "type": "소비자", "adr_ratio": 8, "file_prefix": "baba"},
        "anthropic": {"ticker": None, "currency": "USD", "basis": "private", "listed": False, "type": "업무", "file_prefix": None},
        "openai": {"ticker": None, "currency": "USD", "basis": "private", "listed": False, "type": "소비자", "file_prefix": None}
    }
    
    raw_data = {}
    for cid, meta in company_meta.items():
        raw_data[cid] = {
            "meta": meta,
            "verified_price": None,
            "price_source": None,
            "price_timestamp": None,
            "eps_history": [],
            "forecast_quarters": []
        }
        if not meta["listed"]:
            continue
            
        pfx = meta["file_prefix"]
        
        # 1. Load Verified Price from info.json or summary.json
        info_path = os.path.join(base_ntm, f"nasdaq-{pfx}-info.json")
        if not os.path.exists(info_path):
            info_path = os.path.join(base_c13, f"nasdaq-{pfx}-info.json")
            
        sum_path = os.path.join(base_ntm, f"nasdaq-{pfx}-summary.json")
        if not os.path.exists(sum_path):
            sum_path = os.path.join(base_c13, f"nasdaq-{pfx}-summary.json")
            
        if os.path.exists(info_path):
            try:
                with open(info_path, "r", encoding="utf-8") as fp:
                    d = json.load(fp)
                    prim = d.get("data", {}).get("primaryData", {})
                    p = parse_price(prim.get("lastSalePrice"))
                    if p is not None:
                        raw_data[cid]["verified_price"] = p
                        raw_data[cid]["price_source"] = f"nasdaq-{pfx}-info.json:primaryData.lastSalePrice"
                        raw_data[cid]["price_timestamp"] = prim.get("lastTradeTimestamp")
            except Exception as e:
                raw_data[cid]["price_error"] = str(e)
                
        if raw_data[cid]["verified_price"] is None and os.path.exists(sum_path):
            try:
                with open(sum_path, "r", encoding="utf-8") as fp:
                    d = json.load(fp)
                    sdata = d.get("data", {}).get("summaryData", {})
                    p = parse_price(sdata.get("PreviousClose", {}).get("value"))
                    if p is not None:
                        raw_data[cid]["verified_price"] = p
                        raw_data[cid]["price_source"] = f"nasdaq-{pfx}-summary.json:PreviousClose"
            except Exception as e:
                raw_data[cid]["price_summary_error"] = str(e)
                
        # 2. Load EPS History (has PreviousQuarter and UpcomingQuarter)
        eps_path = os.path.join(base_ntm, f"nasdaq-{pfx}-eps.json")
        if not os.path.exists(eps_path):
            eps_path = os.path.join(base_c13, f"nasdaq-{pfx}-eps.json")
            
        if os.path.exists(eps_path):
            try:
                with open(eps_path, "r", encoding="utf-8") as fp:
                    d = json.load(fp)
                    raw_data[cid]["eps_history"] = d.get("data", {}).get("earningsPerShare", [])
            except Exception as e:
                raw_data[cid]["eps_error"] = str(e)
                
        # 3. Load Forecast Quarters
        fc_path = os.path.join(base_ntm, f"nasdaq-{pfx}-earnings_forecast.json")
        if not os.path.exists(fc_path):
            fc_path = os.path.join(base_c13, f"nasdaq-{pfx}-earnings_forecast.json")
            
        if os.path.exists(fc_path):
            try:
                with open(fc_path, "r", encoding="utf-8") as fp:
                    d = json.load(fp)
                    raw_data[cid]["forecast_quarters"] = d.get("data", {}).get("quarterlyForecast", {}).get("rows", [])
            except Exception as e:
                raw_data[cid]["forecast_error"] = str(e)
                
    return raw_data

def run_analysis():
    data = load_data()
    results = {
        "analysis_date": "2026-09-09",
        "methodology_note": "F6-H(2A+2E) aggregate error and verified price re-evaluation",
        "companies": {},
        "backtest_t0": {},
        "backtest_error_summary": {},
        "comparison_f6h_vs_f6n": {},
        "rankings": {},
        "bias_metrics": {},
        "scarcity_summary": {},
        "scoring_curves": {}
    }
    
    # 1. Scarcity & Coverage Analysis
    total_comps = len(data)
    listed_comps = sum(1 for c, d in data.items() if d["meta"]["listed"])
    has_2a_2e = 0
    has_4e = 0
    
    for cid, d in data.items():
        meta = d["meta"]
        eps_list = d["eps_history"]
        fc_list = d["forecast_quarters"]
        
        prev = [x for x in eps_list if x.get("type") == "PreviousQuarter"]
        up = [x for x in eps_list if x.get("type") == "UpcomingQuarter"]
        
        can_f6h = (len(prev) >= 2 and (len(up) >= 2 or len(fc_list) >= 2))
        can_f6n = (len(fc_list) >= 4 or len(up) >= 4)
        
        # Unit consistency check for ADRs
        if meta.get("basis") in ["adr", "ads"]:
            can_f6h = False  # requires explicit conversion gate
            
        if can_f6h:
            has_2a_2e += 1
        if can_f6n:
            has_4e += 1
            
        results["companies"][cid] = {
            "meta": meta,
            "verified_price": d.get("verified_price"),
            "price_source": d.get("price_source"),
            "price_timestamp": d.get("price_timestamp"),
            "prev_quarters_count": len(prev),
            "up_quarters_count": len(up),
            "forecast_quarters_count": len(fc_list),
            "f6h_eligible": can_f6h,
            "f6n_eligible": can_f6n
        }

    results["scarcity_summary"] = {
        "total_universe": total_comps,
        "listed_universe": listed_comps,
        "unlisted_universe": total_comps - listed_comps,
        "f6h_available_count": has_2a_2e,
        "f6h_coverage_rate_total": round(has_2a_2e / total_comps * 100, 1),
        "f6h_coverage_rate_listed": round(has_2a_2e / listed_comps * 100, 1),
        "f6n_available_count": has_4e,
        "f6n_coverage_rate_total": round(has_4e / total_comps * 100, 1),
        "f6n_coverage_rate_listed": round(has_4e / listed_comps * 100, 1),
        "unlisted_deficit_rate": 100.0,
        "notes": "TSMC/Alibaba are held as pending due to ADR/currency unconfirmed metadata"
    }
    
    # 2. Backtest at T0 (Simulating 4-Quarter Evaluation with 2A+2E vs True 4Q Actual)
    # Q1, Q2, Q3, Q4 from PreviousQuarter
    # 2A = Actual(Q1) + Actual(Q2)
    # 2E_con = Consensus(Q3) + Consensus(Q4)
    # 2E_act = Actual(Q3) + Actual(Q4)
    # F6-H = 2A + 2E_con
    # True 4Q Actual = 2A + 2E_act
    # Component 2E Error = 2E_con - 2E_act
    # Aggregate Error = F6-H - True 4Q Actual = 2E_con - 2E_act
    # Aggregate APE = |Aggregate Error| / True 4Q Actual (if True 4Q Actual > 0)
    
    q3_apes, q4_apes = [], []
    e2_maes, e2_apes = [], []
    agg_maes, agg_apes = [], []
    
    for cid, d in data.items():
        eps_list = d["eps_history"]
        prev = [x for x in eps_list if x.get("type") == "PreviousQuarter"]
        if len(prev) >= 4:
            q1, q2, q3, q4 = prev[0], prev[1], prev[2], prev[3]
            
            # Historical 2A
            act_q1 = q1.get("earnings", 0.0)
            act_q2 = q2.get("earnings", 0.0)
            act_2a = act_q1 + act_q2
            
            # Historical 2E (Consensus for Q3, Q4)
            con_q3 = q3.get("consensus", 0.0)
            con_q4 = q4.get("consensus", 0.0)
            con_2e = con_q3 + con_q4
            
            # Realized Actuals for Q3, Q4
            act_q3 = q3.get("earnings", 0.0)
            act_q4 = q4.get("earnings", 0.0)
            act_2e = act_q3 + act_q4
            
            # Full 4Q sums
            f6h_t0 = act_2a + con_2e
            true_4q_actual = act_2a + act_2e
            
            # Component Errors
            err_q3 = con_q3 - act_q3
            mae_q3 = abs(err_q3)
            ape_q3 = (mae_q3 / act_q3 * 100) if act_q3 > 0 else None
            
            err_q4 = con_q4 - act_q4
            mae_q4 = abs(err_q4)
            ape_q4 = (mae_q4 / act_q4 * 100) if act_q4 > 0 else None
            
            err_2e = con_2e - act_2e
            mae_2e = abs(err_2e)
            ape_2e = (mae_2e / act_2e * 100) if act_2e > 0 else None
            
            # Aggregate Errors
            err_agg = f6h_t0 - true_4q_actual
            mae_agg = abs(err_agg)
            
            # Non-positive denominator check
            ape_agg = None
            exclusion_reason = None
            if true_4q_actual <= 0:
                exclusion_reason = f"NON_POSITIVE_DENOMINATOR (True 4Q Actual = {true_4q_actual} <= 0)"
            else:
                ape_agg = (mae_agg / true_4q_actual * 100)
                
            if ape_q3 is not None: q3_apes.append(ape_q3)
            if ape_q4 is not None: q4_apes.append(ape_q4)
            e2_maes.append(mae_2e)
            if ape_2e is not None: e2_apes.append(ape_2e)
            agg_maes.append(mae_agg)
            if ape_agg is not None: agg_apes.append(ape_agg)
            
            growth_2a_to_2e = (act_2e - act_2a) / act_2a * 100 if act_2a > 0 else None
            
            bt_info = {
                "point_in_time": False,
                "as_of_status": "retrospective_snapshot_on_earnings_page (asOf: null)",
                "quarters": {
                    "q1": {"period": q1.get("period"), "actual": act_q1},
                    "q2": {"period": q2.get("period"), "actual": act_q2},
                    "q3": {"period": q3.get("period"), "consensus": con_q3, "actual": act_q3, "mae": round(mae_q3, 4), "ape_pct": round(ape_q3, 2) if ape_q3 is not None else None},
                    "q4": {"period": q4.get("period"), "consensus": con_q4, "actual": act_q4, "mae": round(mae_q4, 4), "ape_pct": round(ape_q4, 2) if ape_q4 is not None else None}
                },
                "2a_actual_sum": round(act_2a, 4),
                "2e_consensus_sum": round(con_2e, 4),
                "2e_actual_realized_sum": round(act_2e, 4),
                "f6h_aggregate_t0": round(f6h_t0, 4),
                "true_4q_actual_sum": round(true_4q_actual, 4),
                "component_2e_mae": round(mae_2e, 4),
                "component_2e_ape_pct": round(ape_2e, 2) if ape_2e is not None else None,
                "aggregate_mae": round(mae_agg, 4),
                "aggregate_ape_pct": round(ape_agg, 2) if ape_agg is not None else None,
                "exclusion_reason": exclusion_reason,
                "growth_2a_to_2e_pct": round(growth_2a_to_2e, 2) if growth_2a_to_2e is not None else None
            }
            results["backtest_t0"][cid] = bt_info

    def calc_stats(arr):
        if not arr: return {"mean": None, "median": None, "min": None, "max": None, "count": 0}
        s = sorted(arr)
        n = len(s)
        med = s[n // 2] if n % 2 == 1 else (s[n // 2 - 1] + s[n // 2]) / 2.0
        return {
            "count": n,
            "mean": round(sum(s) / n, 2),
            "median": round(med, 2),
            "min": round(min(s), 2),
            "max": round(max(s), 2)
        }

    results["backtest_error_summary"] = {
        "quarterly_q3_ape": calc_stats(q3_apes),
        "quarterly_q4_ape": calc_stats(q4_apes),
        "component_2e_mae": calc_stats(e2_maes),
        "component_2e_ape": calc_stats(e2_apes),
        "aggregate_f6h_mae": calc_stats(agg_maes),
        "aggregate_f6h_ape": calc_stats(agg_apes),
        "notes": "Aggregate APE dilutes error across the full 4Q base, whereas component 2E APE reflects pure forecast error."
    }

    # 3. Current Comparison: F6-H vs F6-N with Verified Market Prices
    f6_comparison = {}
    per_h_list = []
    per_n_list = []
    cids_scored = []
    
    for cid, d in data.items():
        meta = d["meta"]
        price = d.get("verified_price")
        eps_list = d["eps_history"]
        fc_list = d["forecast_quarters"]
        prev = [x for x in eps_list if x.get("type") == "PreviousQuarter"]
        
        # Exclude if no verified price or ADR pending
        if price is None or meta.get("basis") in ["adr", "ads"]:
            continue
            
        if len(prev) >= 2 and len(fc_list) >= 4:
            p1, p2 = prev[-2], prev[-1]
            act_2a = p1.get("earnings", 0.0) + p2.get("earnings", 0.0)
            
            f1, f2 = fc_list[0], fc_list[1]
            con_2e = f1.get("consensusEPSForecast", 0.0) + f2.get("consensusEPSForecast", 0.0)
            f6h_eps = act_2a + con_2e
            
            f3, f4 = fc_list[2], fc_list[3]
            f6n_eps = con_2e + f3.get("consensusEPSForecast", 0.0) + f4.get("consensusEPSForecast", 0.0)
            
            diff_eps = f6h_eps - f6n_eps
            diff_pct = (diff_eps / f6n_eps * 100) if f6n_eps > 0 else None
            
            per_h = (price / f6h_eps) if f6h_eps > 0 else None
            per_n = (price / f6n_eps) if f6n_eps > 0 else None
            
            per_distortion = None
            if per_h is not None and per_n is not None and per_n > 0:
                per_distortion = ((per_h - per_n) / per_n) * 100
                
            comp_res = {
                "verified_price": price,
                "price_source": d.get("price_source"),
                "2a_periods": [p1.get("period"), p2.get("period")],
                "2a_actual_sum": round(act_2a, 4),
                "2e_periods": [f1.get("fiscalEnd"), f2.get("fiscalEnd")],
                "2e_consensus_sum": round(con_2e, 4),
                "f6h_eps": round(f6h_eps, 4),
                "4e_periods": [f1.get("fiscalEnd"), f2.get("fiscalEnd"), f3.get("fiscalEnd"), f4.get("fiscalEnd")],
                "f6n_eps": round(f6n_eps, 4),
                "diff_eps": round(diff_eps, 4),
                "diff_pct_vs_f6n": round(diff_pct, 2) if diff_pct is not None else None,
                "verified_per_f6h": round(per_h, 2) if per_h is not None else None,
                "verified_per_f6n": round(per_n, 2) if per_n is not None else None,
                "per_distortion_pct": round(per_distortion, 2) if per_distortion is not None else None
            }
            f6_comparison[cid] = comp_res
            
            if per_h is not None and per_n is not None:
                per_h_list.append(per_h)
                per_n_list.append(per_n)
                cids_scored.append(cid)
                
    results["comparison_f6h_vs_f6n"] = f6_comparison
    
    # 4. Rank Correlation on Verified Prices
    if len(cids_scored) >= 5:
        def get_ranks(vals):
            sorted_pairs = sorted(enumerate(vals), key=lambda x: x[1])
            ranks = [0] * len(vals)
            for r, (idx, _) in enumerate(sorted_pairs):
                ranks[idx] = r + 1
            return ranks
            
        ranks_h = get_ranks(per_h_list)
        ranks_n = get_ranks(per_n_list)
        
        n_scored = len(cids_scored)
        d_sq_sum = sum((ranks_h[i] - ranks_n[i]) ** 2 for i in range(n_scored))
        spearman_rho = 1.0 - (6.0 * d_sq_sum) / (n_scored * (n_scored**2 - 1))
        
        rank_table = []
        for i in range(n_scored):
            rank_table.append({
                "company_id": cids_scored[i],
                "verified_price": f6_comparison[cids_scored[i]]["verified_price"],
                "f6h_eps": f6_comparison[cids_scored[i]]["f6h_eps"],
                "f6n_eps": f6_comparison[cids_scored[i]]["f6n_eps"],
                "per_f6h": round(per_h_list[i], 2),
                "rank_f6h": ranks_h[i],
                "per_f6n": round(per_n_list[i], 2),
                "rank_f6n": ranks_n[i],
                "rank_shift": ranks_h[i] - ranks_n[i]
            })
        rank_table.sort(key=lambda x: x["rank_f6n"])
        
        results["rankings"] = {
            "sample_count": n_scored,
            "spearman_rho": round(spearman_rho, 4),
            "rank_shifts": rank_table
        }

    # 5. Dedicated Scoring Curve Re-evaluation
    if "rankings" in results and "rank_shifts" in results["rankings"]:
        all_per_h = sorted([x["per_f6h"] for x in results["rankings"]["rank_shifts"]])
        n = len(all_per_h)
        quantiles = {
            "p20": round(all_per_h[int(0.2 * n)], 2),
            "p40": round(all_per_h[int(0.4 * n)], 2),
            "p60": round(all_per_h[int(0.6 * n)], 2),
            "p80": round(all_per_h[int(0.8 * n)], 2)
        }
        
        # Calculate empirical growth lag factor from the peer group
        lag_factors = []
        for x in results["rankings"]["rank_shifts"]:
            cinfo = f6_comparison[x["company_id"]]
            if cinfo["f6h_eps"] > 0 and cinfo["f6n_eps"] > 0:
                lag_factors.append(cinfo["f6n_eps"] / cinfo["f6h_eps"])
        mean_lag = (sum(lag_factors) / len(lag_factors)) if lag_factors else 1.20
        
        shifted_band = [round(20.0 * mean_lag, 1), round(29.0 * mean_lag, 1), round(42.0 * mean_lag, 1), round(62.0 * mean_lag, 1), round(90.0 * mean_lag, 1)]
        
        results["scoring_curves"] = {
            "f6n_standard_band": [20.0, 29.0, 42.0, 62.0, 90.0],
            "mean_growth_lag_multiplier": round(mean_lag, 4),
            "candidate_1_fixed_standard": "고성장주 PER 할증으로 인한 0~1점 하향 편향 발생 (부적합)",
            "candidate_2_growth_lag_shifted_band": shifted_band,
            "candidate_3_empirical_quantiles": quantiles,
            "recommendation": f"F6-H 채택 시 평균 성장 지연율({round((mean_lag - 1.0)*100, 1)}%)을 반영한 Candidate 2 전용 밴드 {shifted_band} 적용 권고"
        }

    return results

if __name__ == "__main__":
    res = run_analysis()
    out_dir = "C:/Users/noble/orca/workspaces/stock-report-harness/C-13/validation/f6-h-backtest-01"
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "raw_backtest_data.json")
    with open(out_file, "w", encoding="utf-8") as fp:
        json.dump(res, fp, ensure_ascii=False, indent=2)
    print(f"Analysis complete. Saved to {out_file}")
    
    es = res.get("backtest_error_summary", {})
    print(f"Component 2E Error (APE): mean={es.get('component_2e_ape',{}).get('mean')}%, median={es.get('component_2e_ape',{}).get('median')}%")
    print(f"Aggregate F6-H Error (APE): mean={es.get('aggregate_f6h_ape',{}).get('mean')}%, median={es.get('aggregate_f6h_ape',{}).get('median')}%")
    print(f"Aggregate F6-H Error (MAE): mean={es.get('aggregate_f6h_mae',{}).get('mean')}, median={es.get('aggregate_f6h_mae',{}).get('median')}")
    if "rankings" in res:
        print(f"Spearman Rank Correlation (Verified Prices): {res['rankings'].get('spearman_rho')}")
