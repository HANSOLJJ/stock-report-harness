# 실행 입력(원자료·판단)을 기업·지표별로 조회하는 인덱스와 factor 결과 객체 생성 헬퍼
from __future__ import annotations

from typing import Any

USABLE_STATUSES = ("verified", "legacy_unverified")


class ObsLookup:
    """기업별 관측을 지표로 조회한다. 같은 지표가 여럿이면 verified 를 우선하고, 그다음 as_of 최신을 고른다."""

    def __init__(self, observations: list[dict[str, Any]]):
        self._by_company: dict[str, dict[str, list[dict[str, Any]]]] = {}
        for item in observations:
            self._by_company.setdefault(item["company_id"], {}).setdefault(item["metric"], []).append(item)

    def all(self, company_id: str, metric: str) -> list[dict[str, Any]]:
        return list(self._by_company.get(company_id, {}).get(metric, []))

    def get(self, company_id: str, metric: str) -> dict[str, Any] | None:
        items = self.all(company_id, metric)
        if not items:
            return None
        def key(obs: dict[str, Any]) -> tuple[int, str]:
            rank = 2 if obs["status"] == "verified" else 1 if obs["status"] == "legacy_unverified" else 0
            return rank, obs["as_of"]
        return sorted(items, key=key, reverse=True)[0]

    def number(self, company_id: str, metric: str) -> tuple[float | None, dict[str, Any] | None]:
        """(값, 관측). 값이 있고 status 가 사용 가능할 때만 숫자를 돌려준다."""
        obs = self.get(company_id, metric)
        if obs is None:
            return None, None
        value = obs["value"]
        if obs["status"] in USABLE_STATUSES and isinstance(value, (int, float)) and not isinstance(value, bool):
            return float(value), obs
        return None, obs


class JudgmentLookup:
    def __init__(self, judgments: list[dict[str, Any]]):
        self._by_pair: dict[tuple[str, str], dict[str, Any]] = {}
        for item in judgments:
            self._by_pair[(item["company_id"], item["factor"])] = item

    def get(self, company_id: str, factor: str) -> dict[str, Any] | None:
        return self._by_pair.get((company_id, factor))


def factor_result(
    factor: str,
    *,
    score: int | None,
    status: str,
    basis: str,
    judgment: dict[str, Any] | None = None,
    observation_ids: list[str] | None = None,
    calc: dict[str, Any] | None = None,
    warnings: list[str] | None = None,
    pending: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """factor 결과의 단일 형태. status: ok | carried_score | needs_judgment | needs_rule_decision | pending_data | error."""
    return {
        "factor": factor,
        "score": score,
        "status": status,
        "basis": basis,
        "judgment_id": judgment["judgment_id"] if judgment else None,
        "observation_ids": sorted(observation_ids or []),
        "calc": calc or {},
        "warnings": list(warnings or []),
        "pending": pending,
    }


def pending_info(kind: str, message: str, decision_id: str | None = None) -> dict[str, Any]:
    info: dict[str, Any] = {"kind": kind, "message": message}
    if decision_id:
        info["decision_id"] = decision_id
    return info


def carried_note(judgment: dict[str, Any] | None) -> list[str]:
    """승계 판단이면 원검토일과 이번 실행 재검토 아님을 경고로 남긴다 (설계 지침 4.1)."""
    if judgment is None or judgment.get("status") != "carried":
        return []
    return [f"승계된 판단 — 원검토일 {judgment['reviewed_at']}({judgment.get('carried_from') or ''}), 이번 실행 재검토 아님"]


def obs_note(obs: dict[str, Any] | None) -> list[str]:
    """legacy 원자료 사용 시 경고 문자열."""
    if obs is None:
        return []
    if obs["status"] == "legacy_unverified":
        return [f"{obs['observation_id']}: legacy_unverified 원자료(이번 실행에서 재검증되지 않음)"]
    return []
