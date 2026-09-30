#!/usr/bin/env bash
# UserPromptSubmit: inject relevant memory topics for the requested domain.
ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT" 2>/dev/null || exit 0
if [ ! -f scripts/memory_context.py ]; then
  exit 0
fi
# 2026-09-30: 프로젝트 Python 은 uv 가 관리한다. uv 가 없는 환경에서는 시스템 python3 로 되돌아간다.
if command -v uv >/dev/null 2>&1; then
  uv run --frozen python -X utf8 scripts/memory_context.py
else
  python3 -X utf8 scripts/memory_context.py
fi
