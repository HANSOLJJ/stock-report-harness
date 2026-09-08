# 규칙 원본(scorecard/rules/*.json) 로드·해시와 구간표·사다리·매트릭스·실행 단위 결정 조회 헬퍼
from __future__ import annotations

from pathlib import Path
from typing import Any

from report_contract_lib import ROOT

from .schema import SchemaError, load_json_strict, sha256_file, validate_rules

RULES_DIR = ROOT / "scorecard" / "rules"


class RuleSet:
    def __init__(self, payload: dict[str, Any], path: Path):
        self.payload = validate_rules(payload)
        self.path = path
        self.version: str = payload["rule_version"]
        self.hash: str = sha256_file(path)

    # ------------------------------------------------------------ lookups
    def factor(self, fid: str) -> dict[str, Any]:
        return self.payload["factors"][fid]

    def factor_range(self, fid: str) -> tuple[int, int]:
        lo, hi = self.factor(fid)["range"]
        return int(lo), int(hi)

    @property
    def f6(self) -> dict[str, Any]:
        return self.payload["policies"]["f6"]

    @property
    def f9(self) -> dict[str, Any]:
        return self.payload["policies"]["f9"]

    def decision(self, decision_id: str) -> dict[str, Any] | None:
        for item in self.payload["decisions"]:
            if item["id"] == decision_id:
                return item
        return None

    def pending_decisions(self) -> list[dict[str, Any]]:
        return [d for d in self.payload["decisions"] if d["status"] == "pending"]

    def checklist(self) -> list[dict[str, Any]]:
        return list(self.payload["checklist"])

    # ------------------------------------------------------------ F6 band
    def f6_band(self, per: float) -> tuple[int, str]:
        """PER 을 반개방 구간표에 넣어 (점수, 구간 라벨) 반환. 표시 반올림은 개입하지 않는다."""
        lower = 0.0
        for band in self.f6["bands"]:
            upper = band["upper"]
            if upper is None or per < upper:
                label = f"{lower:g}~{upper:g}" if upper is not None else f"{lower:g}+"
                return int(band["score"]), label
            lower = float(upper)
        raise SchemaError("f6 bands 가 구간을 덮지 못함")

    def f6_boundaries(self) -> list[float]:
        return [float(b["upper"]) for b in self.f6["bands"] if b["upper"] is not None]

    def f6_boundary_flag(self, per: float) -> dict[str, Any]:
        tol = float(self.f6["boundary_tolerance"])
        nearest = min(self.f6_boundaries(), key=lambda b: abs(per - b) / b)
        distance = (per - nearest) / nearest
        # 정확히 3% 인 경우도 경계 대상(T-02). 부동소수 오차로 빠지지 않게 12자리에서 반올림해 비교한다.
        return {
            "flag": round(abs(distance), 12) <= tol,
            "nearest_boundary": nearest,
            "distance_ratio": distance,
            "tolerance": tol,
        }

    # ------------------------------------------------------------ F3 ladder
    def f3_ladder(self, points: float, imitation_pass: bool, door_closed_pass: bool) -> tuple[int, str]:
        spec = self.factor("F3")
        for rung in spec["ladder"]:
            if points in rung["points"]:
                score = int(rung["score"])
                note = f"통과점 {points:g} → {score}"
                if rung.get("requires_imitation_pass") and not imitation_pass:
                    score = 3
                    note += " (모방불가 완전 pass 아님 → 상한 3)"
                elif rung.get("requires_imitation_pass") and spec.get("score5_requires_door_closed") and door_closed_pass:
                    score = 5
                    note += " + 문 닫힘 증거 → 5"
                return score, note
        raise SchemaError(f"F3 통과점 {points!r} 은 사다리에 없음")

    # ------------------------------------------------------------ F5 / F7
    def f5_formula(self, A: int, H: int) -> int:
        spec = self.factor("F5")
        if A not in spec["A_allowed"] or H not in spec["H_allowed"]:
            raise SchemaError(f"F5 입력 범위 밖: A={A}, H={H}")
        return 3 + A + H

    def f7_matrix(self, share: str, returns: str) -> int:
        key = f"{share}|{returns}"
        matrix = self.factor("F7")["matrix"]
        if key not in matrix:
            raise SchemaError(f"F7 매트릭스 키 없음: {key}")
        return int(matrix[key])


def load_rules(version: str) -> RuleSet:
    path = RULES_DIR / f"{version}.json"
    payload = load_json_strict(path)
    ruleset = RuleSet(payload, path)
    if ruleset.version != version:
        raise SchemaError(f"규칙 파일 rule_version {ruleset.version!r} != 요청 {version!r}")
    return ruleset


def run_decision(run: dict[str, Any], decision_id: str) -> dict[str, Any] | None:
    for item in run.get("decisions", []):
        if item["id"] == decision_id:
            return item
    return None


def decision_choice(run: dict[str, Any], rules: RuleSet, decision_id: str) -> str | None:
    """실행 단위 결정이 있으면 그 선택을, 없으면 None. 규칙의 choices 밖 선택은 오류."""
    item = run_decision(run, decision_id)
    if item is None:
        return None
    spec = rules.decision(decision_id)
    if spec is None:
        raise SchemaError(f"run.decisions: 규칙에 없는 결정 ID {decision_id}")
    choices = spec.get("choices") or []
    if choices and item["choice"] not in choices:
        raise SchemaError(f"run.decisions[{decision_id}]: choice {item['choice']!r} 는 {choices} 중 하나")
    return str(item["choice"])
