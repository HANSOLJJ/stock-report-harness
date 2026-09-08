# factor 결과를 과점·함정·조정총점으로 합산하고 완료 기업만으로 동점 공동 순위를 계산
from __future__ import annotations

from typing import Any

from .schema import MOAT_FACTORS, TRAP_FACTORS

COMPLETE_STATUSES = {"ok", "carried_score"}


def summarize_company(company: dict[str, Any], factors: dict[str, dict[str, Any]]) -> dict[str, Any]:
    complete = all(factors[f]["status"] in COMPLETE_STATUSES for f in MOAT_FACTORS + TRAP_FACTORS)
    moat = sum(int(factors[f]["score"]) for f in MOAT_FACTORS) if all(factors[f]["score"] is not None for f in MOAT_FACTORS) else None
    trap = sum(int(factors[f]["score"]) for f in TRAP_FACTORS) if all(factors[f]["score"] is not None for f in TRAP_FACTORS) else None
    total = moat + trap if complete and moat is not None and trap is not None else None
    pending = [
        {"factor": f, "status": factors[f]["status"], **(factors[f]["pending"] or {})}
        for f in MOAT_FACTORS + TRAP_FACTORS
        if factors[f]["status"] not in COMPLETE_STATUSES
    ]
    carried = [f for f in MOAT_FACTORS + TRAP_FACTORS if factors[f]["status"] == "carried_score"]
    return {
        "company_id": company["company_id"],
        "display_name": company["display_name"],
        "type": company["type"],
        "listed": company["listed"],
        "reference": bool(company.get("reference", False)),
        "factors": factors,
        "moat": moat,
        "trap": trap,
        "total": total,
        "complete": complete,
        "pending": pending,
        "carried_factors": carried,
        "rank": None,
    }


def rank_companies(summaries: list[dict[str, Any]]) -> dict[str, Any]:
    scored = [s for s in summaries if s["complete"] and not s["reference"]]
    totals = [s["total"] for s in scored]
    for s in scored:
        s["rank"] = 1 + sum(1 for t in totals if t > s["total"])
    ranking = sorted(scored, key=lambda s: (-s["total"], -(s["moat"] or 0), s["company_id"]))
    incomplete = [s for s in summaries if not s["complete"] and not s["reference"]]
    return {
        "ranking": [
            {"rank": s["rank"], "company_id": s["company_id"], "display_name": s["display_name"], "moat": s["moat"], "trap": s["trap"], "total": s["total"]}
            for s in ranking
        ],
        "population": {
            "scored": len(scored),
            "incomplete": [
                {"company_id": s["company_id"], "display_name": s["display_name"], "reasons": s["pending"], "moat": s["moat"], "trap": s["trap"]}
                for s in incomplete
            ],
            "reference_excluded": [s["company_id"] for s in summaries if s["reference"]],
            "note": "미완료 기업은 0점으로 채우지 않고 공식 순위에서 제외한다. 동점은 공동 순위이며 다음 순위를 건너뛴다.",
        },
    }
