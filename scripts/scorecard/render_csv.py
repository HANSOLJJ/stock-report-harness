# 승인된 실행 결과를 scorecard/history.csv 에 중복 없이 append 하는 이력 렌더러
from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from .schema import FACTOR_IDS

COLUMNS = [
    "run_id", "approval_id", "approved_at", "rule_version", "rule_hash", "as_of", "baseline_id", "company_id",
    *FACTOR_IDS, "moat", "trap", "total", "rank", "complete", "carried_factors", "change_type", "results_hash",
]


def history_rows(results: dict[str, Any], approval: dict[str, Any], rule_hash: str, change_type: str) -> list[dict[str, Any]]:
    rows = []
    for c in results["companies"]:
        row = {
            "run_id": results["run_id"],
            "approval_id": approval["approval_id"],
            "approved_at": approval["approved_at"],
            "rule_version": results["rule_version"],
            "rule_hash": rule_hash,
            "as_of": results["as_of"],
            "baseline_id": results["baseline_id"],
            "company_id": c["company_id"],
            "moat": "" if c["moat"] is None else c["moat"],
            "trap": "" if c["trap"] is None else c["trap"],
            "total": "" if c["total"] is None else c["total"],
            "rank": "" if c["rank"] is None else c["rank"],
            "complete": "true" if c["complete"] else "false",
            "carried_factors": "|".join(c["carried_factors"]),
            "change_type": change_type,
            "results_hash": results["results_hash"],
        }
        for f in FACTOR_IDS:
            score = c["factors"][f]["score"]
            row[f] = "" if score is None else score
        rows.append(row)
    return rows


def append_history(path: Path, rows: list[dict[str, Any]]) -> tuple[int, int]:
    """(추가된 행, 중복으로 건너뛴 행). 키 (run_id, approval_id, company_id) 로 중복을 막는다 (T-15)."""
    existing: set[tuple[str, str, str]] = set()
    if path.is_file():
        with path.open("r", encoding="utf-8", newline="") as fh:
            for row in csv.DictReader(fh):
                existing.add((row["run_id"], row["approval_id"], row["company_id"]))
    added = skipped = 0
    path.parent.mkdir(parents=True, exist_ok=True)
    write_header = not path.is_file() or path.stat().st_size == 0
    with path.open("a", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=COLUMNS)
        if write_header:
            writer.writeheader()
        for row in rows:
            key = (str(row["run_id"]), str(row["approval_id"]), str(row["company_id"]))
            if key in existing:
                skipped += 1
                continue
            writer.writerow(row)
            existing.add(key)
            added += 1
    return added, skipped
