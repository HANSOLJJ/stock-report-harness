# F9 미결 규칙 5건의 시뮬레이션 결과를 구조화된 JSON으로 생성하는 스크립트
import json
import os
from datetime import datetime
from verify_f9_independent import TestF9DecideIndependent

base_dir = os.path.dirname(os.path.abspath(__file__))
tester = TestF9DecideIndependent()
TestF9DecideIndependent.setUpClass()

combos = [
    ("diagnose_only", "hold"),
    ("diagnose_only", "downgrade"),
    ("apply", "hold"),
    ("apply", "downgrade"),
]

matrix_results = {}
for c05, c16 in combos:
    combo_key = f"C05_{c05}__C16_{c16}"
    dec = {
        "C-04": "exclude",
        "C-05": c05,
        "C-06": "proposed_v15_boundaries",
        "C-16": c16
    }
    comp_map = {}
    for cid in sorted(tester.companies_info.keys()):
        score, status, _ = tester.run_f9(cid, dec)
        comp_map[cid] = {
            "score": score,
            "status": status
        }
    matrix_results[combo_key] = comp_map

results = {
    "generated_at": datetime.now().isoformat(),
    "task": "F9-DECIDE-20",
    "core_conclusions": {
        "current_baseline_score_mover": {
            "rule_combination": "C-06 (proposed_v15_boundaries) + C-05 (diagnose_only)",
            "affects_company": "spacex-xai",
            "impact": "현재 기준선 자료에서 유일하게 점수를 움직이고 차단을 해제하는 조합. spacex-xai를 needs_rule_decision에서 -4 (status: ok)로 완료"
        },
        "score_moving_issues_conditional": [
            {
                "issue": "C-05",
                "blocking": True,
                "affects_companies": ["spacex-xai"],
                "impact": "G1 실패 기업(spacex-xai)에 대해 diagnose_only는 -4 확정 및 즉시 완료(ok), apply는 G4 판단 대기(needs_judgment)로 넘어가 C-16에 따라 -4(hold) 또는 -5(downgrade)로 강등"
            },
            {
                "issue": "C-16",
                "blocking": True,
                "current_data_impact": "0개사 변동 (11개사가 coverage_comparable: unknown으로 C-16 도달 전 needs_judgment로 차단)",
                "conditional_affects_companies": ["alibaba (profit + coverage=yes 입력 시)", "spacex-xai (C-05 apply + coverage=yes 입력 시)"],
                "impact": "현재 자료 기준으로는 0개사. Alibaba에 operating_result_reviewed=profit과 coverage_comparable=yes의 2대 입력이 모두 확보되었을 때 hold는 -2, downgrade는 -3으로 1칸 분기"
            }
        ],
        "zero_numeric_impact_issues_in_current_data": [
            {
                "issue": "C-16",
                "blocking": True,
                "impact": "현재 자료 기준 0개사 변동. coverage_comparable 검토 입력(yes) 없이는 아무도 C-16에 닿지 못함"
            },
            {
                "issue": "C-04",
                "blocking": False,
                "impact": "관측치에 undrawn_credit이 0건이므로 exclude와 include_v15 간 점수 차이 0개사"
            },
            {
                "issue": "C-07",
                "blocking": False,
                "impact": "Anthropic과 OpenAI의 ARR 대체 금지(incompatible_basis) 원칙 확인. OpenAI는 이미 바닥(-5)이고 Anthropic은 G1 미해결이라 점수 변동 없음"
            }
        ],
        "unblocking_issues": [
            {
                "issue": "C-06",
                "blocking": True,
                "affects_companies": ["spacex-xai"],
                "impact": "proposed_v15_boundaries 채택 시 spacex-xai를 needs_rule_decision에서 즉시 해제"
            }
        ],
        "unblocked_companies_summary": {
            "spacex-xai": "C-06 proposed_v15_boundaries + C-05 diagnose_only 채택 시 점수 -4 (status: ok)로 즉시 완료 (현재 자료에서 유일하게 풀리는 기업)",
            "alibaba": "SEC 20-F TTM 영업흑자(profit) + coverage_comparable=yes 2대 입력 확보 후 C-16(hold 시 -2, downgrade 시 -3) 결정 시 완료",
            "amazon": "AWS 백로그 정성 확인(미개시 리스 상회)을 G4 유지(step 0)로 인정하는 규칙 명시 시 -2로 완료",
            "anthropic": "비상장 TTM 영업손익 미공시 처리 규칙 결정 시 완료 가능 (단위경제 흑자 인정 시 -2, 영업적자 간주 시 -4/-5)"
        }
    },
    "matrix_simulation": matrix_results,
    "company_details": {
        "spacex-xai": {
            "g1_operating_margin": -0.149,
            "c06_proposed_g1_score": -4,
            "g3_runway_years": 3.077,
            "g3_step": 0,
            "g4_status": "coverage_comparable: unknown",
            "outcomes": {
                "C05_diagnose_only": {"score": -4, "status": "ok", "unblocked": True},
                "C05_apply_with_hold": {"score": -4, "status": "needs_judgment_then_ok", "requires_judgment": True},
                "C05_apply_with_downgrade": {"score": -5, "status": "needs_judgment_then_ok", "requires_judgment": True}
            }
        },
        "alibaba": {
            "g1_sec_operating_income": "FY2026 113,391M CNY (강한 흑자)",
            "g2_fcf": -11400000000.0,
            "g2_score": -2,
            "g3_runway_years": 4.98,
            "g3_step": 0,
            "g4_metrics": "contracted_revenue: not_disclosed, offbalance_B: not_disclosed",
            "outcomes": {
                "C16_hold": {"score": -2, "status": "ok"},
                "C16_downgrade": {"score": -3, "status": "ok"}
            }
        },
        "amazon": {
            "g1_status": "pass",
            "g2_fcf": -11600000000.0,
            "g2_score": -2,
            "g3_runway_years": 10.6,
            "g3_step": 0,
            "g4_metrics": "contracted_revenue: parse_failed (AWS 백로그 수백 $B급), offbalance_B: 106B",
            "block_reason": "coverage_comparable unknown 및 parse_failed로 인해 C-16 미적용",
            "resolution_path": "백로그가 미개시 리스를 상회하는 정성적 확인 인정 시 -2(유지)로 완료"
        },
        "anthropic": {
            "g1_status": "pending_data (TTM 영업손익 미공시)",
            "g2_fcf": "not_disclosed",
            "g4_metrics": "incompatible_basis (ARR vs 컴퓨트)",
            "resolution_path": "비상장 영업손익 판정 규칙 필요 (흑자 인정 시 -2, 적자 간주 시 -4/-5)"
        },
        "openai": {
            "g1_status": "bep_retreat=yes -> score = -5",
            "g3_g4": "skipped (already at floor -5)",
            "final_score": -5,
            "status": "ok"
        },
        "oracle": {
            "g1_status": "pass",
            "g2_score": -2,
            "g3_runway_years": 1.346,
            "g3_step": -1,
            "g4_coverage": 2.552,
            "g4_step": 0,
            "final_score": -3,
            "status": "ok"
        }
    }
}

out_path = os.path.join(base_dir, "f9_decision_simulation_results.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"Generated {out_path} successfully.")
