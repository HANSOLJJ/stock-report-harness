#!/usr/bin/env python3
"""Shared helpers for stock-report-harness contract validation/building.

The helpers are deliberately small and dependency-light.  PyYAML is used when
available for frontmatter fidelity, but the fallback parser is enough for the
flat scalar keys that the pipeline contracts depend on.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PLAN_DIR = ROOT / "plan"
RESEARCH_DIR = ROOT / "research"
DRAFT_DIR = ROOT / "drafts"
REVIEW_DIR = ROOT / "reviews"
OUTPUT_DIR = ROOT / "output"

FRONTMATTER_RE = re.compile(r"\A---\s*\r?\n(?P<frontmatter>.*?)\r?\n---\s*(?:\r?\n)?", re.DOTALL)
H1_RE = re.compile(r"^#(?!#)\s+.+$", re.MULTILINE)
H2_RE = re.compile(r"^##\s+(?P<title>.+?)\s*$", re.MULTILINE)
# SOURCE_MARKER_RE = re.compile(r"\[(?:S|N|P)\d+\]")  # 2026-09-07 변경 전
# 2026-09-07: enforce-citations.sh 훅은 [H1](yfinance 보유자 데이터) 표식도 허용하는데 검증기·빌더는
# S/N/P만 제거해 최종 HTML에 [H1]이 남았음(tesla 리포트에서도 사용). 훅과 같은 집합으로 맞춤.
SOURCE_MARKER_RE = re.compile(r"\[(?:S|N|P|H)\d+\]")

REQUIRED_SCORECARD_PLAN_FRONTMATTER = [
    "slug",
    "report_type",
    "topic",
    "request",
    "output_type",
    "audience",
    "run_id",
    "as_of",
    "rule_version",
    "rule_hash",
    "baseline_id",
    "companies",
    "created_at",
    "assumptions",
]


@dataclass(frozen=True)
class ArtifactPaths:
    slug: str
    plan: Path
    research: Path
    draft: Path
    review: Path
    html: Path


def artifact_paths(slug: str) -> ArtifactPaths:
    return ArtifactPaths(
        slug=slug,
        plan=PLAN_DIR / f"{slug}.md",
        research=RESEARCH_DIR / f"{slug}.md",
        draft=DRAFT_DIR / f"{slug}.md",
        review=REVIEW_DIR / f"{slug}.md",
        html=OUTPUT_DIR / f"{slug}.html",
    )


def rel(path: Path) -> str:
    try:
        # return str(path.relative_to(ROOT))  # 2026-09-07 변경 전
        # 2026-09-07: Windows에서는 relative_to()가 'plan\\slug.md'를 돌려줘 frontmatter의
        # 'plan/slug.md'와 문자열 비교(_expect_source_path)가 항상 실패했음. POSIX 구분자로 고정함.
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def _stringify_scalar(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if value is None:
        return ""
    if isinstance(value, dict):
        return {str(k): _stringify_scalar(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_stringify_scalar(v) for v in value]
    return value


def _fallback_yamlish_parse(raw: str) -> dict[str, Any]:
    data: dict[str, Any] = {}
    current_key: str | None = None
    for line in raw.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith((" ", "\t")):
            if current_key and line.strip().startswith("- "):
                data.setdefault(current_key, [])
                if isinstance(data[current_key], list):
                    data[current_key].append(line.strip()[2:].strip().strip('"\''))
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        current_key = key
        if value == "":
            data[key] = []
        elif value.lower() in {"true", "false"}:
            data[key] = value.lower() == "true"
        else:
            data[key] = value.strip('"\'')
    return data


def parse_frontmatter_text(text: str) -> tuple[dict[str, Any], str, str]:
    """Return (frontmatter, body, raw_frontmatter)."""
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}, text, ""

    raw = match.group("frontmatter")
    parsed: Any
    try:
        import yaml  # type: ignore

        parsed = yaml.safe_load(raw) or {}
        if not isinstance(parsed, dict):
            parsed = {}
    except Exception:
        parsed = _fallback_yamlish_parse(raw)

    parsed = {str(k): _stringify_scalar(v) for k, v in parsed.items()}
    return parsed, text[match.end() :], raw


def read_markdown(path: Path) -> tuple[dict[str, Any], str, str, str]:
    text = path.read_text(encoding="utf-8")
    frontmatter, body, raw = parse_frontmatter_text(text)
    return frontmatter, body, raw, text


def frontmatter_value(frontmatter: dict[str, Any], key: str) -> str:
    value = frontmatter.get(key)
    if value is None:
        return ""
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    return str(value).strip()


def heading_titles(body: str) -> list[str]:
    return [m.group("title").strip().rstrip("#").strip() for m in H2_RE.finditer(body)]


def has_required_section(body: str, section: str) -> bool:
    return any(title == section for title in heading_titles(body))


def count_h1(body: str) -> int:
    return len(H1_RE.findall(body))


def has_source_markers(text: str) -> bool:
    return bool(SOURCE_MARKER_RE.search(text))
