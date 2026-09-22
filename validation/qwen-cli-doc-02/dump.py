"""QWEN-CLI-DOC-02: 소형 문서 파일 행번호 덤프 (읽기 전용)."""
import glob
import io
import os
import sys

W = r"C:\Users\noble\orca\workspaces\stock-report-harness\worker"
pats = sys.argv[1:] or [
    ".claude/commands/score-*.md",
    ".claude/skills/score-*/SKILL.md",
    "package.json",
    "CLAUDE.md",
]
for pat in pats:
    for f in sorted(glob.glob(os.path.join(W, pat))):
        rel = os.path.relpath(f, W).replace("\\", "/")
        lines = io.open(f, encoding="utf-8").read().split("\n")
        print("")
        print("##### FILE: %s  (%d lines) #####" % (rel, len(lines)))
        for i, l in enumerate(lines, 1):
            print("%4d| %s" % (i, l))
