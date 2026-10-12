# 사용자 지시(2026-10-12): 이 실행의 spacex-xai 표시 이름을 'SpaceX' 로 — run.json display_names 와 기업 요약 문장을 고친다
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "scripts"))
from scorecard.schema import load_json_strict, validate_run, write_json  # noqa: E402

BY = "claude (사용자 위임 2026-10-12)"
CLI = ["uv", "run", "--frozen", "python", "-X", "utf8", str(ROOT / "scripts" / "scorecard_cli.py")]


def main() -> int:
    slug = sys.argv[1]
    rp = ROOT / "output" / slug / "run.json"
    run = load_json_strict(rp)
    run["display_names"] = {"spacex-xai": "SpaceX"}
    validate_run(run, slug)
    write_json(rp, run)
    j = load_json_strict(ROOT / "output" / slug / "judgments.json")
    s = next(x for x in j.get("company_summaries") or [] if x["company_id"] == "spacex-xai")
    if "SpaceX + xAI" not in s["text"]:
        raise SystemExit("요약에 옛 이름이 없다")
    text = s["text"].replace("SpaceX + xAI", "SpaceX")
    r = subprocess.run([*CLI, "propose", slug, "--company", "spacex-xai", "--factor", "SUMMARY", "--evidence", text,
                        "--reason", "표시 이름을 SpaceX 로 고친다(사용자 지시 2026-10-12)", "--by", BY],
                       capture_output=True, text=True, encoding="utf-8", cwd=ROOT)
    if r.returncode != 0:
        print(r.stdout[-1500:]); print(r.stderr[-1500:]); return 1
    r = subprocess.run([*CLI, "proposal", slug, "--all-pending", "--accept", "--by", BY], capture_output=True, text=True, encoding="utf-8", cwd=ROOT)
    print(r.stdout[-400:]); print(r.stderr[-400:])
    return r.returncode


if __name__ == "__main__":
    raise SystemExit(main())
