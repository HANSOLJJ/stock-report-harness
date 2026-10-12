# (2026-10 v2.1 첫 실행) work/summaries.json 의 기업 요약을 SUMMARY 제안으로 쓰고 한꺼번에 반영한다
"""
사용: uv run --frozen python -X utf8 .agents/plans/v21-first-run-2026-10/work/apply_summaries.py <slug> [--reason "…"]
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BY = "claude (사용자 위임 2026-10-12)"
CLI = ["uv", "run", "--frozen", "python", "-X", "utf8", str(ROOT / "scripts" / "scorecard_cli.py")]


def main() -> int:
    slug = sys.argv[1]
    reason = sys.argv[sys.argv.index("--reason") + 1] if "--reason" in sys.argv else "이 실행의 점수·순위로 기업 요약을 쓴다"
    texts = json.loads((Path(__file__).resolve().parent / "summaries.json").read_text(encoding="utf-8"))
    for cid, text in texts.items():
        r = subprocess.run([*CLI, "propose", slug, "--company", cid, "--factor", "SUMMARY", "--evidence", text,
                            "--reason", reason, "--by", BY], capture_output=True, text=True, encoding="utf-8", cwd=ROOT)
        if r.returncode != 0:
            print(cid); print(r.stdout[-1500:]); print(r.stderr[-1500:])
            return 1
    r = subprocess.run([*CLI, "proposal", slug, "--all-pending", "--accept", "--by", BY],
                       capture_output=True, text=True, encoding="utf-8", cwd=ROOT)
    print(r.stdout[-600:]); print(r.stderr[-600:])
    return r.returncode


if __name__ == "__main__":
    raise SystemExit(main())
