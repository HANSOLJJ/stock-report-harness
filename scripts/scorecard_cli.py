#!/usr/bin/env python3
# AI 기업 9-factor 채점(ai_scorecard) 단계 CLI: add-company / import-baseline / init / research / calculate / draft / review-template / diff / approve / status
"""Usage:
  python scripts/scorecard_cli.py add-company <company_id> --name "표시명" --type 업무 --scope "평가 범위" (--listed | --private) [--ticker NVDA --exchange NASDAQ] [--share-basis common|adr|ads|private] [--adr-ratio 5] [--currency USD] [--alias 별칭] [--reference] [--note "..."] [--status "..."] [--dry-run]
  python scripts/scorecard_cli.py import-baseline [--html PATH] [--md PATH]
  python scripts/scorecard_cli.py init <slug> --as-of 2026-09-02 --title "..." --request "..." [--purpose "..."] [--companies a,b] [--decision C-16=hold --rationale "..." --by NAME] [--force]
  python scripts/scorecard_cli.py research <slug>
  python scripts/scorecard_cli.py calculate <slug>
  python scripts/scorecard_cli.py draft <slug>
  python scripts/scorecard_cli.py review-template <slug> [--force]
  python scripts/scorecard_cli.py diff <slug> --against <prior_slug> [--json]
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


def cmd_add_company(args: argparse.Namespace) -> int:
    """채점 대상 기업을 레지스트리에 등록한다(추가만 한다).

    2026-09-21 ADD-01. 스키마가 못 잡는 **짝 모순**은 여기서 막는다 — 비상장인데 ticker 가 있다거나,
    `adr`·`ads` 인데 비율이 없는 경우다. 공용 검증기(`schema.validate_companies`)에는 넣지 않는다.
    """
    from scorecard.engine import COMPANIES_PATH, load_companies
    from scorecard.registry import add_company, plan_company_line, render_company_line

    listed = bool(args.listed)
    share_basis = args.share_basis or ("common" if listed else "private")
    if listed:
        if share_basis == "private":
            raise SchemaError("--listed 인데 --share-basis private 다 — 짝이 맞지 않는다")
        if not args.ticker or not args.exchange:
            raise SchemaError("상장사는 --ticker 와 --exchange 가 필요하다")
    else:
        if share_basis != "private":
            raise SchemaError(f"--private 인데 --share-basis {share_basis} 다 — 비상장은 private 이어야 한다")
        if args.ticker or args.exchange:
            raise SchemaError("--private 에는 --ticker·--exchange 를 줄 수 없다 — 둘 다 null 로 적는다")
    if share_basis in {"adr", "ads"} and args.adr_ratio is None:
        raise SchemaError(f"--share-basis {share_basis} 는 --adr-ratio 가 필요하다(보통주 몇 주가 1증서인지)")
    if share_basis not in {"adr", "ads"} and args.adr_ratio is not None:
        raise SchemaError(f"--adr-ratio 는 --share-basis adr|ads 에서만 쓴다(지금은 {share_basis})")

    item = {
        "company_id": args.company_id,
        "display_name": args.name,
        "aliases": list(args.alias or []),
        "type": args.type,
        "listed": listed,
        "ticker": args.ticker or None,
        "exchange": args.exchange or None,
        "share_basis": share_basis,
        "adr_ratio": args.adr_ratio,
        "reporting_currency": args.currency,
        "scope": args.scope,
    }
    for key, value in (("reference", args.reference or None), ("note", args.note), ("status", args.status)):
        if value:
            item[key] = value

    if args.dry_run:
        plan = plan_company_line(item)
        print(f"[DRY-RUN] {rel(COMPANIES_PATH)} {plan['line_no']}행에 넣는다 (기업 {plan['count_before']} → {plan['count_after']})")
        print(f"  {plan['anchor_index'] + 1}행 끝에 `,` 를 붙이고 그 아래에:")
        print(render_company_line(item))
        return 0

    out = add_company(item)
    print(f"add-company: {out['company_id']} → {rel(COMPANIES_PATH)} {out['line_no']}행 "
          f"(기업 {out['count_before']} → {out['count_after']})")
    print(f"등록만 했다. 조사·채점은 별도 단계다 — 등록된 기업 {len(load_companies())}곳.")
    return 0


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


def cmd_diff(args: argparse.Namespace) -> int:
    """두 실행을 견주어 **기존 기업이 안 움직였음**을 확인한다.

    2026-09-21 ADD-02. 1층(입력 가법성)과 2층(점수 투영 불변)만 실패로 본다.
    subtree 해시 차이는 실패 조건이 아니다. `as_of` 만 바꿔도 달라지므로 이것으로 실패를 내지 않는다.
    기준일 판정(`period_gap`)은 권고이므로 종료 코드를 바꾸지 않는다.
    """
    from scorecard.compare import compare_runs, period_gap

    out = compare_runs(args.slug, args.against)
    gap = period_gap(args.slug, args.against)
    if args.json:
        print(json.dumps({**out, "period_gap": gap}, ensure_ascii=False, indent=2))
        return 0 if out["ok"] else 1

    print(f"diff: {args.slug} ← {args.against}")
    print(f"신규 기업: {', '.join(out['new_companies']) or '없음'}")
    if out["note"]:
        print(f"※ {out['note']}")

    inputs = out["inputs"]
    print(f"\n[1층] 입력 가법성: {'통과' if inputs['ok'] else '실패'}")
    for name, row in inputs["by_file"].items():
        print(f"  {name} {row['prior']} → {row['new']} | 사라짐 {len(row['removed'])} · "
              f"고쳐짐 {len(row['edited'])} · "
              f"더함 {len(row['added'])}(신규 기업 {len(row['added_for_new_companies'])} · "
              f"기존 기업 {len(row['added_for_existing_companies'])} · "
              f"기업 표기 없음 {len(row['added_without_company'])})")
    for line in inputs["violations"]:
        print(f"  · {line}")

    scores = out["scores"]
    print(f"\n[2층] 점수 불변: {'통과' if scores['ok'] else '실패'} (공통 {scores['compared']}개사 비교)")
    for line in scores["violations"]:
        print(f"  · {line}")

    rank = out["ranking"]
    print(f"\n[3층] 순위 이동(정보): {'같다' if rank['same_order'] else '달라졌다'}")
    if not rank["same_order"]:
        print(f"  이전: {' > '.join(rank['prior'])}")
        print(f"  이후: {' > '.join(rank['new'])}")

    sub = out["subtrees"]
    print(f"\n[참고] subtree 해시가 다른 기업 {len(sub['differing'])}곳 "
          f"(기준일 {sub['as_of']['prior']} → {sub['as_of']['new']})")
    print(f"  {sub['note']}")
    for row in sub["detail"][:5]:
        print(f"  · {row['company_id']}: 다른 경로 {row['path_count']}개 — {row['reason']}")
    if len(sub["detail"]) > 5:
        print(f"  · … 외 {len(sub['detail']) - 5}곳")

    appr = out["prior_approval"]
    print(f"\n[덤] 이전 실행의 승인: {'유효' if appr['valid'] else '무효'}"
          + (f" (달라진 것: {', '.join(appr['differing'])})" if appr.get("differing") else ""))

    print(f"\n[기준일] {gap['verdict']} — {gap['advice']}")
    for row in gap["ahead"]:
        print(f"  · {row['company_id']} 가 {row['quarter']}({row['period_end']}) 로 앞서 있다")
    if gap["missing_period"]:
        unlisted = f" (이 가운데 비상장: {', '.join(gap['missing_unlisted'])})" if gap["missing_unlisted"] else ""
        print(f"  · `revenue_ttm` 기간이 없는 기업: {', '.join(gap['missing_period'])}{unlisted}")

    violations = len(inputs["violations"]) + len(scores["violations"])
    print(f"\n판정: {'통과 — 기존 기업이 움직이지 않았다' if out['ok'] else f'실패 — 1층·2층 위반 {violations}건'}")
    return 0 if out["ok"] else 1


def cmd_status(args: argparse.Namespace) -> int:
    from scorecard.stages import status

    print(json.dumps(status(args.slug), ensure_ascii=False, indent=2))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("add-company")
    p.add_argument("company_id")
    p.add_argument("--name", required=True)
    p.add_argument("--type", required=True)
    p.add_argument("--scope", required=True)
    # 상장 여부는 상호배타 **필수** 그룹이다. `--listed true` 꼴로 받으면 오타가 조용히 False 가 되고
    # `isinstance(bool)` 검사를 통과해 버린다.
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--listed", action="store_true")
    g.add_argument("--private", dest="listed", action="store_false")
    p.add_argument("--ticker")
    p.add_argument("--exchange")
    p.add_argument("--share-basis")
    p.add_argument("--adr-ratio", type=float)
    p.add_argument("--currency", default="USD")
    p.add_argument("--alias", action="append")
    p.add_argument("--reference", action="store_true")
    p.add_argument("--note")
    p.add_argument("--status")
    p.add_argument("--dry-run", action="store_true")
    p.set_defaults(func=cmd_add_company)

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

    p = sub.add_parser("diff", help="두 실행을 견준다. subtree 해시 차이는 실패 조건이 아니다 — "
                                    "`as_of` 만 바꿔도 달라지므로 이것으로 실패를 내지 않는다.")
    p.add_argument("slug")
    p.add_argument("--against", required=True, help="견줄 이전 실행의 slug")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_diff)

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
