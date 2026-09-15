# FIX-53 단계마다 research·calculate·draft 를 다시 돌리고 before.json 대비 바뀐 칸을 출력한다
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
SLUG = "ai-scorecard-2026-09-obsreg"


def main() -> int:
    for stage in ("research", "calculate", "draft"):
        proc = subprocess.run([sys.executable, "-X", "utf8", str(ROOT / "scripts" / "scorecard_cli.py"), stage, SLUG],
                              capture_output=True, text=True, encoding="utf-8", cwd=ROOT)
        if proc.returncode != 0:
            print(f"[{stage}] 실패\n{proc.stdout}\n{proc.stderr}")
            return 1
    before = json.loads((HERE / "before.json").read_text(encoding="utf-8"))["companies"]
    res = json.loads((ROOT / "scorecard" / "runs" / SLUG / "results.json").read_text(encoding="utf-8"))
    changed = []
    for c in res["companies"]:
        cid = c["company_id"]
        b = before[cid]
        if b["total"] != c["total"]:
            changed.append(f"{cid} total {b['total']} -> {c['total']}")
        for f, v in c["factors"].items():
            if b["factors"][f]["score"] != v["score"] or b["factors"][f]["status"] != v["status"]:
                changed.append(f"{cid} {f} {b['factors'][f]['score']}({b['factors'][f]['status']}) -> "
                               f"{v['score']}({v['status']})")
    print("바뀐 칸:", len(changed))
    for line in changed:
        print("  " + line)
    print("순위:", " · ".join(f"{r['rank']} {r['company_id']} {r['total']}" for r in res["ranking"]))
    print("incomplete:", res["population"].get("incomplete"), "pending:", res["pending_rule_decisions"])
    print("results_hash:", res["results_hash"])
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    sys.exit(main())
