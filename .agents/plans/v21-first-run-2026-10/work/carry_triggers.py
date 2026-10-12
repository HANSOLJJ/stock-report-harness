# (2026-10 v2.1 첫 실행) recheck 의 관찰 중 트리거를 이 실행에서 처리했다고 carry 로 적는다 — 정보 마감이 같아 새로 볼 창이 없다
"""
사용: uv run --frozen python -X utf8 .agents/plans/v21-first-run-2026-10/work/carry_triggers.py <slug> <prior_slug>

이 실행은 recheck 와 기준일·정보 마감(2026-10-12)이 같다. 그래서 이전 트리거마다 새 후보를 볼 창이 없고, recheck 가 같은 날
원문으로 확인한 상태를 유지한다. 관찰 중 항목의 carry 를 prior 의 같은 트리거로 바꾸고, 나머지 항목은 손대지 않는다.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "scripts"))
from scorecard.engine import load_context  # noqa: E402
from scorecard.paths import run_paths  # noqa: E402

FINDING = ("이전 실행과 기준일·정보 마감(2026-10-12)이 같아 새로 볼 후보 창이 없다. 이전 실행이 같은 날 후보와 원문으로 확인한 "
           "상태를 그대로 두고 관찰을 이어 간다.")


def main() -> int:
    slug, prior = sys.argv[1:3]
    path = run_paths(slug).triggers
    payload = json.loads(path.read_text(encoding="utf-8"))
    prior_ids = {t["trigger_id"] for t in json.loads(run_paths(prior).triggers.read_text(encoding="utf-8"))["items"]
                 if t["status"] == "watching"}
    created = json.loads((ROOT / "output" / slug / "run.json").read_text(encoding="utf-8"))["created_at"][:10]
    n = 0
    for t in payload["items"]:
        if t["status"] == "watching" and t["trigger_id"] in prior_ids:
            t["carry"] = {"ref": f"{prior}:{t['trigger_id']}", "checked_at": created, "finding": FINDING}
            n += 1
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=False) + "\n", encoding="utf-8", newline="\n")
    load_context(slug)   # 깨지면 여기서 멈춘다
    print(f"carry {n}건 / 이전 관찰 중 {len(prior_ids)}건")
    return 0 if n == len(prior_ids) else 1


if __name__ == "__main__":
    raise SystemExit(main())
