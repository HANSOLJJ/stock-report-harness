#!/usr/bin/env python3
# AI 기업 9-factor 채점(ai_scorecard) 단계 CLI: import-baseline / init / research / calculate / draft / review-template / approve / status
"""Usage:
  python scripts/scorecard_cli.py import-baseline [--html PATH] [--md PATH]
  python scripts/scorecard_cli.py init <slug> --as-of 2026-09-02 --title "..." --request "..." [--purpose "..."] [--companies a,b] [--decision C-16=hold --rationale "..." --by NAME] [--force]
  python scripts/scorecard_cli.py research <slug>
  python scripts/scorecard_cli.py calculate <slug>
  python scripts/scorecard_cli.py draft <slug>
  python scripts/scorecard_cli.py review-template <slug> [--force]
  python scripts/scorecard_cli.py approve <slug> --by NAME [--note "..."]
  python scripts/scorecard_cli.py status <slug>

build 는 기존 명령 `python scripts/build_report.py <slug>` 가 report_type 으로 분기한다.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from report_contract_lib import rel
from scorecard.schema import SchemaError


def cmd_import_baseline(args: argparse.Namespace) -> int:
    from scorecard.baseline_import import DEFAULT_HTML, DEFAULT_MD, import_baseline
    from scorecard.engine import BASELINE_DIR, load_companies

    html_path = Path(args.html) if args.html else DEFAULT_HTML
    md_path = Path(args.md) if args.md else DEFAULT_MD
    report = import_baseline(html_path, md_path, BASELINE_DIR / "v1.5", load_companies())
    print(f"기준선 이관: 기업 {report['matched']} · 관측 {report['observations']} · 트리거 {report['triggers']}")
    for issue in report["issues"]:
        print(f"  불일치 - {issue}")
    for item in report["parse_failed"]:
        print(f"  파싱실패 - {item}")
    print(f"보고서: {rel(BASELINE_DIR / 'v1.5' / 'import-report.md')}")
    return 0


def cmd_init(args: argparse.Namespace) -> int:
    from scorecard.stages import init_run, today

    decisions = []
    for item in args.decision or []:
        if "=" not in item:
            raise SystemExit(f"--decision 형식은 ID=choice: {item!r}")
        did, choice = item.split("=", 1)
        if not args.rationale or not args.by:
            raise SystemExit("--decision 을 쓰면 --rationale 과 --by 가 필요하다")
        decisions.append({"id": did.strip(), "choice": choice.strip(), "rationale": args.rationale, "decided_by": args.by, "decided_at": today()})
    companies = [c.strip() for c in args.companies.split(",")] if args.companies else None
    paths = init_run(
        args.slug,
        as_of=args.as_of,
        title=args.title,
        request=args.request,
        purpose=args.purpose or "기준선 승계 재계산과 규칙·자료·판단의 일관성 확인",
        companies=companies,
        baseline_id=args.baseline,
        rule_version=args.rule,
        decisions=decisions,
        price_as_of=args.price_as_of,
        info_cutoff=args.info_cutoff,
        force=args.force,
    )
    for name, path in paths.items():
        print(f"{name}: {rel(path)}")
    print(f"다음: python scripts/scorecard_cli.py research {args.slug}")
    return 0


def cmd_research(args: argparse.Namespace) -> int:
    from scorecard.stages import research

    print(f"research: {rel(research(args.slug))}")
    print(f"다음: python scripts/scorecard_cli.py calculate {args.slug}")
    return 0


def cmd_calculate(args: argparse.Namespace) -> int:
    from scorecard.stages import calculate

    path, preview, results = calculate(args.slug)
    print(f"results: {rel(path)} (hash {results['results_hash'][:16]}…)")
    print(f"preview: {rel(preview)}")
    print(f"순위 {results['population']['scored']}개사 · 미완료 {len(results['population']['incomplete'])}개사 · 미결 결정 {', '.join(results['pending_rule_decisions']) or '없음'}")
    for row in results["ranking"]:
        print(f"  {row['rank']:>2} {row['display_name']:<20} 과점 {row['moat']:>2} 함정 {row['trap']:>3} 조정 {row['total']:>3}")
    for item in results["population"]["incomplete"]:
        reasons = "; ".join(f"{p['factor']} {p['status']}" + (f"({p['decision_id']})" if p.get("decision_id") else "") for p in item["reasons"])
        print(f"  -- {item['display_name']:<20} 미완료: {reasons}")
    print(f"다음: python scripts/scorecard_cli.py draft {args.slug}")
    return 0


def cmd_draft(args: argparse.Namespace) -> int:
    from scorecard.stages import draft

    print(f"draft: {rel(draft(args.slug))}")
    print(f"다음: python scripts/scorecard_cli.py review-template {args.slug} → 4-way 리뷰 → approve")
    return 0


def cmd_review_template(args: argparse.Namespace) -> int:
    from scorecard.stages import review_template

    print(f"review template: {rel(review_template(args.slug, force=args.force))}")
    print("검토 영역 4개와 체크리스트 Q01~Q23 를 채우고 status 를 pass 로 바꾼 뒤 validate_report_contract.py 로 확인한다")
    return 0


def cmd_approve(args: argparse.Namespace) -> int:
    from scorecard.stages import approve

    print(f"approval: {rel(approve(args.slug, approved_by=args.by, note=args.note))}")
    print(f"다음: python scripts/build_report.py {args.slug}")
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    from scorecard.stages import status

    print(json.dumps(status(args.slug), ensure_ascii=False, indent=2))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("import-baseline")
    p.add_argument("--html")
    p.add_argument("--md")
    p.set_defaults(func=cmd_import_baseline)

    p = sub.add_parser("init")
    p.add_argument("slug")
    p.add_argument("--as-of", required=True)
    p.add_argument("--title", required=True)
    p.add_argument("--request", required=True)
    p.add_argument("--purpose")
    p.add_argument("--companies")
    p.add_argument("--baseline", default="v1.5")
    p.add_argument("--rule", default="v1.5")
    p.add_argument("--decision", action="append")
    p.add_argument("--rationale")
    p.add_argument("--by")
    p.add_argument("--price-as-of")
    p.add_argument("--info-cutoff")
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=cmd_init)

    for name, func in (("research", cmd_research), ("calculate", cmd_calculate), ("draft", cmd_draft), ("status", cmd_status)):
        p = sub.add_parser(name)
        p.add_argument("slug")
        p.set_defaults(func=func)

    p = sub.add_parser("review-template")
    p.add_argument("slug")
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=cmd_review_template)

    p = sub.add_parser("approve")
    p.add_argument("slug")
    p.add_argument("--by", required=True)
    p.add_argument("--note")
    p.set_defaults(func=cmd_approve)

    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except SchemaError as exc:
        print(f"[FAIL] {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
