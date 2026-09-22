"""QWEN-CLI-DOC-02: 검토 대상 인벤토리 + 시작/종료 해시 기록. 읽기 전용."""
import glob
import hashlib
import io
import json
import os
import subprocess
import sys

W = r"C:\Users\noble\orca\workspaces\stock-report-harness\worker"
HERE = os.path.dirname(os.path.abspath(__file__))
STAGE = sys.argv[1] if len(sys.argv) > 1 else "start"

PATTERNS = [
    "README.md", "AGENTS.md", "CLAUDE.md", "package.json",
    "docs/scorecard/*.md", "docs/*.md",
    ".claude/commands/score-*.md", ".claude/commands/*.md",
    ".claude/skills/score-*/SKILL.md", ".claude/skills/*/SKILL.md",
    ".claude/settings.json",
    "scripts/scorecard_cli.py", "scripts/scorecard/*.py",
    "scripts/build_report.py", "scripts/validate_report_contract.py",
    "scripts/report_contract_lib.py",
    "scorecard/companies.json", "scorecard/rules/*.json",
    "scorecard/baseline/*/*.json", "scorecard/baseline/*/*.md",
    "scorecard/runs/*/*.json",
    "tests/*.js", "tests/*.py",
]

seen = {}
for pat in PATTERNS:
    for p in sorted(glob.glob(os.path.join(W, pat))):
        if os.path.isfile(p):
            seen[p] = True

rows = []
for p in sorted(seen):
    with open(p, "rb") as f:
        raw = f.read()
    try:
        nlines = raw.decode("utf-8").count("\n") + 1
    except UnicodeDecodeError:
        nlines = -1
    rel = os.path.relpath(p, W).replace("\\", "/")
    rows.append(dict(rel=rel, sha256=hashlib.sha256(raw).hexdigest(),
                     bytes=len(raw), lines=nlines))

head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=W, capture_output=True,
                      text=True).stdout.strip()
status = subprocess.run(["git", "status", "--porcelain"], cwd=W,
                        capture_output=True, text=True).stdout.strip()

out = dict(stage=STAGE, head=head, status=status.splitlines(), files=rows)
path = os.path.join(HERE, "hashes-%s.json" % STAGE)
with io.open(path, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)

print("stage=%s HEAD=%s files=%d -> %s" % (STAGE, head[:12], len(rows), path))
print("git status --porcelain:")
for l in out["status"]:
    print("   " + l)
print()
print("%-52s %8s %7s  %s" % ("relpath", "bytes", "lines", "sha256[:16]"))
for r in rows:
    print("%-52s %8d %7d  %s" % (r["rel"], r["bytes"], r["lines"], r["sha256"][:16]))
