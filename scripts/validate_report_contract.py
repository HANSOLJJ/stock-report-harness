#!/usr/bin/env python3
"""ai_scorecard 실행 하나의 계약 산출물을 검증한다. 검사 본문은 scorecard.validate 에 있다.

Usage:
  uv run --frozen python -X utf8 scripts/validate_report_contract.py <slug>
  uv run --frozen python -X utf8 scripts/validate_report_contract.py <slug> --require-html
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass, field


@dataclass
class ValidationResult:
    slug: str
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    checks: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)

    def check(self, message: str) -> None:
        self.checks.append(message)


def validate_contract(slug: str, *, require_html: bool = False, check_html_if_present: bool = True) -> ValidationResult:
    from scorecard.validate import validate_scorecard

    return validate_scorecard(slug, require_html=require_html, check_html_if_present=check_html_if_present,
                              result=ValidationResult(slug=slug))


def print_result(result: ValidationResult) -> None:
    title = "PASS" if result.ok else "FAIL"
    print(f"[{title}] report contract: {result.slug}")
    for check in result.checks:
        print(f"  ok - {check}")
    for warning in result.warnings:
        print(f"  warn - {warning}")
    for error in result.errors:
        print(f"  error - {error}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("slug", help="Run slug, e.g. ai-scorecard-2026-09-obsreg")
    parser.add_argument("--require-html", action="store_true", help="Fail when the built HTML is missing")
    args = parser.parse_args(argv)

    result = validate_contract(args.slug, require_html=args.require_html)
    print_result(result)
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
