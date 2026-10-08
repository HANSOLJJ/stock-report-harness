# 판단 세션의 산출물(work/judge/<F>-<company>.json)을 순서대로 propose 하고 한꺼번에 반영한다
"""
사용: uv run --frozen python -X utf8 .agents/plans/rejudge-all-2026-11/work/apply_judgments.py <slug> [--only F1,F3] [--dry-run] [--no-accept]

파일 모양은 REJUDGE-INSTRUCTIONS.md 5번. propose 가 하나라도 실패하면 그 자리에서 멈추고(이미 쓴 제안은 남는다) 실패 파일을 적는다.
--no-accept 면 제안만 쓰고 반영은 하지 않는다. 반영은 `proposal --all-pending --accept` 한 번이다.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]   # work → rejudge-all-2026-11 → plans → .agents → 저장소 루트
WORK = Path(__file__).resolve().parent / "judge"
BY = "claude (사용자 위임 2026-10-08)"
CLI = ["uv", "run", "--frozen", "python", "-X", "utf8", str(ROOT / "scripts" / "scorecard_cli.py")]


def main() -> int:
    args = sys.argv[1:]
    slug = args[0]
    only = None
    dry = "--dry-run" in args
    accept = "--no-accept" not in args
    if "--only" in args:
        only = set(args[args.index("--only") + 1].split(","))
    files = sorted(f for f in WORK.glob("F*-*.json") if not f.name.endswith(".propose.json"))
    if only:
        files = [f for f in files if f.name.split("-", 1)[0] in only]
    if not files:
        print("반영할 파일이 없다"); return 1
    done = 0
    for f in files:
        factor, company = f.stem.split("-", 1)
        spec = json.loads(f.read_text(encoding="utf-8"))
        payload = {
            "changes": dict(spec.get("changes") or {}),
            "evidence_after": spec.get("evidence_after"),
            "evidence_up_after": spec.get("evidence_up_after"),
            "evidence_down_after": spec.get("evidence_down_after"),
        }
        if spec.get("reconfirm"):
            payload["changes"]["reconfirmed"] = {"evidence_ids": list(spec["reconfirm"])}
        tmp = f.with_suffix(".propose.json")
        tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        cmd = [*CLI, "propose", slug, "--company", company, "--factor", factor, "--json", str(tmp),
               "--reason", spec.get("reason") or f"{factor} 재판단(규칙 v2.0)", "--by", BY]
        if spec.get("cite"):
            cmd += ["--cite", ",".join(spec["cite"])]
        print(f"→ {f.name}")
        if dry:
            print("   ", " ".join(cmd[7:]))
            continue
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", cwd=ROOT)
        if r.returncode != 0:
            print(r.stdout[-2000:]); print(r.stderr[-3000:])
            print(f"[실패] {f.name} 에서 멈춤 (반영된 제안 {done}건은 결정 전 상태로 남아 있다)")
            return 1
        done += 1
    print(f"제안 {done}건 작성")
    if accept and not dry and done:
        r = subprocess.run([*CLI, "proposal", slug, "--all-pending", "--accept", "--by", BY],
                           capture_output=True, text=True, encoding="utf-8", cwd=ROOT)
        print(r.stdout[-4000:]); print(r.stderr[-3000:])
        return r.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
