# 정성 판정 → 점수 환산 factor 계산: F1·F4·F8 수동 점수, F2 경로 매핑(미결), F3 사다리, F5 산식, F7 매트릭스
from __future__ import annotations

from typing import Any

from .inputs import JudgmentLookup, carried_note, factor_result, pending_info
from .rules import RuleSet, decision_choice

COMPONENT_TYPE = "부품"


def _status_for(judgment: dict[str, Any]) -> str:
    return "carried_score" if judgment["status"] == "carried" else "ok"


def compute_manual(fid: str, company: dict[str, Any], judgments: JudgmentLookup, rules: RuleSet) -> dict[str, Any]:
    judgment = judgments.get(company["company_id"], fid)
    if judgment is None or judgment["kind"] != "score":
        return factor_result(fid, score=None, status="needs_judgment", basis="manual",
                             pending=pending_info("judgment", f"{rules.factor(fid)['label']} 점수·근거·검토자 입력 필요"))
    score = int(judgment["score"])
    warnings: list[str] = []
    if fid == "F1" and company["type"] == COMPONENT_TYPE:
        cap = int(rules.factor("F1")["component_only_cap"])
        if score > cap:
            return factor_result(fid, score=None, status="error", basis="manual", judgment=judgment,
                                 pending=pending_info("error", f"부품형 기업의 F1 은 상한 {cap} — 입력 {score}"))
        warnings.append(f"F1 부품 상한 {cap} 적용 대상(실질 소비자·업무 채널 없음)")
    warnings.extend(carried_note(judgment))
    return factor_result(fid, score=score, status=_status_for(judgment), basis="manual", judgment=judgment, warnings=warnings)


def compute_f2(company: dict[str, Any], judgments: JudgmentLookup, rules: RuleSet, run: dict[str, Any]) -> dict[str, Any]:
    fid = "F2"
    judgment = judgments.get(company["company_id"], fid)
    if judgment is None:
        return factor_result(fid, score=None, status="needs_judgment", basis="paths",
                             pending=pending_info("judgment", "세 경로(성능 도약·패러다임 적응·표준 선점) 판정 입력 필요"))
    choice = decision_choice(run, rules, "C-03")
    if judgment["kind"] == "score":
        # 2026-09-15 FIX-52: v1.7 은 C-03 이 확정됐다. 그래도 세대 격차는 판단 입력이라 엔진이 산출할 수 없어 승계한다.
        reason = ("C-03 확정(paths_with_generation_gap_5)이나 세대 격차는 판단 입력이라 경로 판정 전까지 승계 점수를 사용"
                  if choice == GENERATION_GAP_CHOICE else
                  "C-03: 경로→점수 매핑 미확정이라 승계 점수를 기준선 표시로 사용")
        return factor_result(fid, score=int(judgment["score"]), status="carried_score", basis="carried", judgment=judgment,
                             warnings=[reason] + carried_note(judgment))
    inputs = judgment["inputs"]
    paths = [inputs["performance_leap"], inputs["paradigm_adaptation"], inputs["standard_capture"]]
    passed = sum(1 for p in paths if p == "pass")
    partial = sum(1 for p in paths if p == "partial")
    calc = {"paths": inputs, "passed": passed, "partial": partial}
    if choice == GENERATION_GAP_CHOICE:
        return _f2_generation_gap(fid, inputs, paths, calc, judgment, rules)
    if "unknown" in paths or inputs["top_rank"] == "unknown":
        return factor_result(fid, score=None, status="needs_judgment", basis="paths", judgment=judgment,
                             pending=pending_info("judgment", "경로 판정에 unknown 이 있음 — 실패로 간주하지 않음"))
    # 아래는 v1.5·v1.6 의 후보 매핑 경로다. v1.7 규칙에는 path_mapping_candidate 가 없고 이 선택은 superseded 다.
    if choice != "activate_candidate_mapping":
        return factor_result(fid, score=None, status="needs_rule_decision", basis="paths", judgment=judgment, calc=calc,
                             pending=pending_info("rule", "경로 수→점수 매핑(3경로·0/1점·5점 자격)이 미확정", "C-03"))
    # 2026-09-15 FIX-54 1단계 S7(3차 리뷰 C RC3-09): v1.7 F2 에는 path_mapping_candidate 가 없어 옛 선택지로 오면 KeyError 였다.
    # 규칙이 이 선택을 받칠 매핑을 갖고 있지 않다는 사실을 오류 상태로 드러낸다 — 다른 매핑으로 대신 채우지 않는다.
    if "path_mapping_candidate" not in rules.factor(fid):
        return factor_result(fid, score=None, status="error", basis="paths", judgment=judgment, calc=calc,
                             pending=pending_info("error", f"C-03 선택 activate_candidate_mapping 은 규칙 {rules.version} 에서 쓸 수 없다 — "
                                                           "factor 에 path_mapping_candidate 가 없다(superseded 선택지)", "C-03"))
    mapping = rules.factor(fid)["path_mapping_candidate"]
    calc["mapping"] = mapping
    if str(passed) not in mapping and inputs["top_rank"] != "yes":
        # 후보 매핑에 없는 통과 수(3경로 전부 통과)는 기본값을 만들지 않고 미결로 남긴다.
        return factor_result(fid, score=None, status="needs_rule_decision", basis="paths", judgment=judgment, calc=calc,
                             pending=pending_info("rule", f"경로 {passed}개 통과 점수가 후보 매핑에 없음", "C-03"))
    score = 5 if inputs["top_rank"] == "yes" else int(mapping[str(passed)])
    return factor_result(fid, score=score, status="ok", basis="paths", judgment=judgment, calc=calc,
                         warnings=["C-03: 후보 매핑(0→2, 1→3, 2→4, 종합 1위→5)을 실행 단위 결정으로 적용"] + carried_note(judgment))


GENERATION_GAP_CHOICE = "paths_with_generation_gap_5"


def _f2_generation_gap(fid: str, inputs: dict[str, Any], paths: list[str], calc: dict[str, Any],
                       judgment: dict[str, Any], rules: RuleSet) -> dict[str, Any]:
    """C-03 확정 모델 — 경로 수 0·1·2 → 2·3·4, **성능 도약이 세대 격차 수준이면 5** (v1.7, 2026-09-14).

    5점 칸은 `AA 종합 1위`(top_rank)가 아니다. 세대 격차는 판단 입력 `generation_gap` 으로 받고, 없거나 unknown 이면
    추정하지 않는다. 세대 격차가 세 축 중 몇 개에서 서야 하는지는 원문 미규정이라 판단자가 근거란에 적는다.
    """
    if "unknown" in paths:
        return factor_result(fid, score=None, status="needs_judgment", basis="paths", judgment=judgment, calc=calc,
                             pending=pending_info("judgment", "경로 판정에 unknown 이 있음 — 실패로 간주하지 않음"))
    spec = rules.factor(fid)
    mapping = spec["path_mapping"]
    calc["mapping"] = mapping
    calc["choice"] = GENERATION_GAP_CHOICE
    gap = inputs.get("generation_gap", "unknown")
    calc["generation_gap"] = gap
    if inputs["performance_leap"] == "pass" and spec.get("score5_requires_generation_gap"):
        if gap == "unknown":
            return factor_result(fid, score=None, status="needs_judgment", basis="paths", judgment=judgment, calc=calc,
                                 pending=pending_info("judgment", "성능 도약이 통과인데 세대 격차(generation_gap) 판정이 없음 — "
                                                                  "5점 여부를 추정하지 않음"))
        if gap == "yes":
            return factor_result(fid, score=5, status="ok", basis="paths", judgment=judgment, calc=calc,
                                 warnings=["C-03 확정: 성능 도약이 세대 격차 수준 → 5"] + carried_note(judgment))
    passed = calc["passed"]
    if str(passed) not in mapping:
        return factor_result(fid, score=None, status="needs_rule_decision", basis="paths", judgment=judgment, calc=calc,
                             pending=pending_info("rule", f"경로 {passed}개 통과(세대 격차 없음) 점수가 매핑에 없음", "C-03"))
    return factor_result(fid, score=int(mapping[str(passed)]), status="ok", basis="paths", judgment=judgment, calc=calc,
                         warnings=[f"C-03 확정: 경로 {passed}개 → {mapping[str(passed)]}"] + carried_note(judgment))


def compute_f3(company: dict[str, Any], judgments: JudgmentLookup, rules: RuleSet) -> dict[str, Any]:
    fid = "F3"
    judgment = judgments.get(company["company_id"], fid)
    if judgment is None:
        return factor_result(fid, score=None, status="needs_judgment", basis="criteria",
                             pending=pending_info("judgment", "모방불가·수익모델·가속도 판정 입력 필요"))
    inputs = judgment["inputs"]
    weights = rules.factor(fid)["criteria_weights"]
    criteria = ("imitation", "revenue_model", "acceleration")
    if any(inputs[c] == "unknown" for c in criteria):
        return factor_result(fid, score=None, status="needs_judgment", basis="criteria", judgment=judgment,
                             pending=pending_info("judgment", "세 기준 중 unknown 이 있음 — 자동으로 0.5 를 주지 않음"))
    points = sum(float(weights[inputs[c]]) for c in criteria)
    imitation_pass = inputs["imitation"] == "pass"
    door = inputs["door_closed"]
    score, note = rules.f3_ladder(points, imitation_pass, door == "pass")
    warnings: list[str] = []
    if score == 4 and door == "unknown":
        warnings.append("문 닫힘 증거 미확인 → 상한 4 유지")
    calc = {"criteria": {c: inputs[c] for c in criteria}, "door_closed": door, "pass_points": points, "ladder_note": note}
    warnings.extend(carried_note(judgment))
    return factor_result(fid, score=score, status=_status_for(judgment), basis="criteria", judgment=judgment, calc=calc, warnings=warnings)


def compute_f5(company: dict[str, Any], judgments: JudgmentLookup, rules: RuleSet) -> dict[str, Any]:
    fid = "F5"
    judgment = judgments.get(company["company_id"], fid)
    if judgment is None:
        return factor_result(fid, score=None, status="needs_judgment", basis="grade",
                             pending=pending_info("judgment", "동맹 A 등급·적대 H 등급 입력 필요(별표 G)"))
    A = int(judgment["inputs"]["A"])
    H = int(judgment["inputs"]["H"])
    score = rules.f5_formula(A, H)
    return factor_result(fid, score=score, status=_status_for(judgment), basis="grade", judgment=judgment,
                         calc={"A": A, "H": H, "formula": "3 + A + H"}, warnings=carried_note(judgment))


def compute_f7(company: dict[str, Any], judgments: JudgmentLookup, rules: RuleSet) -> dict[str, Any]:
    fid = "F7"
    judgment = judgments.get(company["company_id"], fid)
    if judgment is None:
        return factor_result(fid, score=None, status="needs_judgment", basis="matrix",
                             pending=pending_info("judgment", "조달 의존 고객 비중(큼/작음)·자기 자금 환류(예/아니오) 판정 필요(별표 I)"))
    if judgment["kind"] == "score":
        return factor_result(fid, score=int(judgment["score"]), status="carried_score", basis="carried", judgment=judgment,
                             warnings=["C-09: 매트릭스 입력이 복원되지 않아 승계 점수를 기준선 표시로 사용"] + carried_note(judgment))
    share = judgment["inputs"]["funding_dependent_share"]
    returns = judgment["inputs"]["own_money_returns"]
    if share == "unknown" or returns == "unknown":
        return factor_result(fid, score=None, status="needs_judgment", basis="matrix", judgment=judgment,
                             pending=pending_info("judgment", "두 축 중 unknown 이 있음 — 환류 사실을 추정하지 않음"))
    score = rules.f7_matrix(share, returns)
    return factor_result(fid, score=score, status=_status_for(judgment), basis="matrix", judgment=judgment,
                         calc={"funding_dependent_share": share, "own_money_returns": returns}, warnings=carried_note(judgment))
