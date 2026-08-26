#!/usr/bin/env bash
# Common helpers for stock-report-harness Claude Code guardrail hooks.
# Hook scripts are intentionally dependency-light: Bash + Python stdlib only.

# Do not enable `set -e`; hooks should fail open unless they deliberately block.

repo_root() {
  git rev-parse --show-toplevel 2>/dev/null || pwd
}

json_block() {
  local reason="$1"
  python3 - "$reason" <<'PY'
import json, sys
reason = sys.argv[1]
print(json.dumps({"decision": "block", "reason": reason}, ensure_ascii=False))
PY
  exit 2
}

json_context() {
  local event="$1"
  local context="$2"
  python3 - "$event" "$context" <<'PY'
import json, sys
print(json.dumps({
    "hookSpecificOutput": {
        "hookEventName": sys.argv[1],
        "additionalContext": sys.argv[2],
    }
}, ensure_ascii=False))
PY
}

# Normalize a user/tool path to repo-relative POSIX form when possible.
normalize_repo_path() {
  local root="$1"
  local raw="$2"
  python3 - "$root" "$raw" <<'PY'
import os, sys
from pathlib import Path
root = Path(sys.argv[1]).resolve()
raw = sys.argv[2]
if not raw:
    sys.exit(0)
p = Path(raw).expanduser()
if not p.is_absolute():
    p = (root / p)
try:
    rel = p.resolve().relative_to(root)
    print(rel.as_posix())
except Exception:
    print(p.resolve().as_posix())
PY
}

# Extract file paths from Write/Edit/MultiEdit style hook payloads, one per line.
extract_tool_paths() {
  python3 -c 'import json, sys
try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)
ti = data.get("tool_input") or {}
paths = []
for key in ("file_path", "path", "notebook_path"):
    value = ti.get(key)
    if isinstance(value, str) and value.strip():
        paths.append(value.strip())
for key in ("file_paths", "paths"):
    value = ti.get(key)
    if isinstance(value, list):
        paths.extend(str(v).strip() for v in value if str(v).strip())
seen = set()
for p in paths:
    if p not in seen:
        print(p)
        seen.add(p)'
}

extract_bash_command() {
  python3 -c 'import json, sys
try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)
cmd = (data.get("tool_input") or {}).get("command")
if isinstance(cmd, str):
    print(cmd)'
}
