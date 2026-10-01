#!/usr/bin/env python3
# AI 기업 9-factor 채점(ai_scorecard) 단계 CLI: add-company / import-baseline / init / collect / research / calculate / draft / review-template / diff / summary / confirm / judge / approve / revoke / status / resolve-cik
"""Usage:
  uv run --frozen python -X utf8 scripts/scorecard_cli.py add-company <company_id> --name "표시명" --type 업무 --scope "평가 범위" (--listed | --private) [--ticker NVDA --exchange NASDAQ] [--share-basis common|adr|ads|private] [--adr-ratio 5] [--currency USD] [--alias 별칭] [--reference] [--note "..."] [--status "..."] [--dry-run]
  uv run --frozen python -X utf8 scripts/scorecard_cli.py import-baseline [--html PATH] [--md PATH]
  uv run --frozen python -X utf8 scripts/scorecard_cli.py init <slug> --as-of 2026-09-02 --title "..." --request "..." [--purpose "..."] [--companies a,b] [--decision C-16=hold --rationale "..." --by NAME] [--force]
  uv run --frozen python -X utf8 scripts/scorecard_cli.py init <slug> --from-run <prior_slug> [--add-companies a,b] [--title "..." --request "..." --as-of ... --rule v1.7 --decision C-16=hold --no-carry-decisions]
  uv run --frozen python -X utf8 scripts/scorecard_cli.py collect <slug> [--company a,b] [--kind news|filings|prices|all] [--since YYYY-MM-DD] [--forms 8-K,10-Q] [--locale en-US] [--from-file PATH] [--dry-run]
  uv run --frozen python -X utf8 scripts/scorecard_cli.py research <slug> [--no-register]
  uv run --frozen python -X utf8 scripts/scorecard_cli.py calculate <slug>
  uv run --frozen python -X utf8 scripts/scorecard_cli.py draft <slug>
  uv run --frozen python -X utf8 scripts/scorecard_cli.py review-template <slug> [--force]
  uv run --frozen python -X utf8 scripts/scorecard_cli.py diff <slug> --against <prior_slug> [--json]
  uv run --frozen python -X utf8 scripts/scorecard_cli.py trigger-candidates <slug> [--json] [--limit N]
  uv run --frozen python -X utf8 scripts/scorecard_cli.py summary <slug> --json
  uv run --frozen python -X utf8 scripts/scorecard_cli.py confirm <slug> [--evidence EV-a-001,EV-a-002] [--reject EV-a-003] [--by NAME] [--take-lock]
  uv run --frozen python -X utf8 scripts/scorecard_cli.py judge <slug> --company <id> --factor F1..F9 (--set key=value … | --evidence "문장" … | --json PATH) --reason "…" --by NAME [--take-lock]
  uv run --frozen python -X utf8 scripts/scorecard_cli.py approve <slug> --by NAME [--note "..."] [--via browser|terminal]   (사람 셸에서만)
  uv run --frozen python -X utf8 scripts/scorecard_cli.py revoke <slug> --by NAME --note "..."                              (사람 셸에서만)
  uv run --frozen python -X utf8 scripts/scorecard_cli.py status <slug>

init·collect·research·calculate·draft·review-template 과 에이전트 세션의 confirm·judge 는 실행 잠금(output/<slug>/.lock)을
검사·기록한다. 다른 소유자의 잠금이면 거부하고 --take-lock 으로 인수한다.
  uv run --frozen python -X utf8 scripts/scorecard_cli.py resolve-cik [--company id] [--from-file PATH] [--apply] [--json]

build 는 기존 명령 `uv run --frozen python -X utf8 scripts/build_report.py <slug>` 가 report_type 으로 분기한다.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from report_contract_lib import rel
from scorecard.schema import SchemaError


def _claim(args: argparse.Namespace, stage: str) -> None:
    """실행 잠금(output/<slug>/.lock). 다른 소유자의 잠금이면 거부하고 --take-lock 이면 인수한다(2026-09-30 레인 F)."""
    from scorecard.stages import claim_lock

    claim_lock(args.slug, stage, take_lock=args.take_lock)


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
    from scorecard.baseline_import import BASELINE_ID, DEFAULT_HTML, DEFAULT_MD, import_baseline
    from scorecard.engine import BASELINE_DIR, load_companies

    # 2026-10-01: 기준선 소비 승인 실행 보호(레인 N V2-1)는 import_baseline 본체가 한다. CLI 에서 또 부르면 경고가 두 번 난다.
    html_path = Path(args.html) if args.html else DEFAULT_HTML
    md_path = Path(args.md) if args.md else DEFAULT_MD
    report = import_baseline(html_path, md_path, BASELINE_DIR / BASELINE_ID, load_companies())
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
    add_companies = [c.strip() for c in args.add_companies.split(",")] if args.add_companies else None
    # 2026-09-21 ADD-03. 제목은 실행마다 달라야 한다. 이어받기에서 기본값으로 떨어지면 두 실행이 같은 제목을 갖는다.
    if args.from_run and not args.title:
        print(f"[경고] --title 을 주지 않아 이전 실행 {args.from_run} 의 제목을 그대로 쓴다. 실행마다 제목을 달리하는 편이 낫다")
    from scorecard.stages import claim_lock

    claim_lock(args.slug, "init", take_lock=args.take_lock, write=False)
    # 승인된 실행을 --force 로 덮어쓸 때의 거부(에이전트)·경고(사람)는 init_run 의 protect_approved_run 이 낸다(2026-10-01 레인 N).
    paths = init_run(
        args.slug,
        as_of=args.as_of,
        title=args.title,
        request=args.request,
        purpose=args.purpose,
        companies=companies,
        baseline_id=args.baseline,
        rule_version=args.rule,
        decisions=decisions,
        price_as_of=args.price_as_of,
        info_cutoff=args.info_cutoff,
        force=args.force,
        from_run=args.from_run,
        add_companies=add_companies,
        carry_decisions=not args.no_carry_decisions,
    )
    claim_lock(args.slug, "init", take_lock=args.take_lock)
    for name, path in paths.items():
        print(f"{name}: {rel(path)}")
    if args.from_run:
        print(f"다음: research 로 새 기업만 조사한 뒤 "
              f"uv run --frozen python -X utf8 scripts/scorecard_cli.py diff {args.slug} --against {args.from_run} 으로 기존 기업 불변을 확인한다")
    print(f"다음: uv run --frozen python -X utf8 scripts/scorecard_cli.py collect {args.slug} → 후보 선별 → research {args.slug}")
    return 0


def cmd_collect(args: argparse.Namespace) -> int:
    """근거 후보를 모은다. 뉴스·공시는 후보 파일만, 가격은 관측·출처까지 쓴다(2026-09-30 레인 E)."""
    from scorecard.stages import COLLECT_KINDS, collect

    kinds = COLLECT_KINDS if args.kind == "all" else (args.kind,)
    _claim(args, "collect")
    out = collect(args.slug, companies=args.company.split(",") if args.company else None, kinds=kinds,
                  since=args.since, forms=args.forms.split(",") if args.forms else None, locale=args.locale,
                  from_file=args.from_file, dry_run=args.dry_run)
    print(f"collect: {args.slug} 창 {out['window']['since']} ~ {out['window']['until']}{' (dry-run)' if out['dry_run'] else ''}")
    for kind in COLLECT_KINDS:
        for row in out[kind]:
            extra = " ".join(f"{k}={v}" for k, v in row.items() if k not in ("company_id", "status", "urls"))
            print(f"  {kind:<8} {row['company_id']:<12} {row['status']}" + (f" {extra}" if extra else ""))
            for url in row.get("urls") or []:
                print(f"    {url}")
    if out.get("candidates"):
        print(f"candidates: {rel(out['candidates'])}")
    print(f"다음: 후보를 선별해 evidence/evidence.json·triggers.json 을 쓴 뒤 uv run --frozen python -X utf8 scripts/scorecard_cli.py research {args.slug}")
    return 0


def cmd_research(args: argparse.Namespace) -> int:
    from scorecard.stages import research

    _claim(args, "research")
    print(f"research: {rel(research(args.slug, register=not args.no_register))}")
    print(f"다음: uv run --frozen python -X utf8 scripts/scorecard_cli.py calculate {args.slug}")
    return 0


def cmd_calculate(args: argparse.Namespace) -> int:
    from scorecard.stages import calculate

    _claim(args, "calculate")
    path, preview, results = calculate(args.slug)
    print(f"results: {rel(path)} (hash {results['results_hash'][:16]}…)")
    print(f"preview: {rel(preview)}")
    print(f"순위 {results['population']['scored']}개사 · 미완료 {len(results['population']['incomplete'])}개사 · 미결 결정 {', '.join(results['pending_rule_decisions']) or '없음'}")
    for row in results["ranking"]:
        print(f"  {row['rank']:>2} {row['display_name']:<20} 과점 {row['moat']:>2} 함정 {row['trap']:>3} 조정 {row['total']:>3}")
    for item in results["population"]["incomplete"]:
        reasons = "; ".join(f"{p['factor']} {p['status']}" + (f"({p['decision_id']})" if p.get("decision_id") else "") for p in item["reasons"])
        print(f"  -- {item['display_name']:<20} 미완료: {reasons}")
    print(f"다음: uv run --frozen python -X utf8 scripts/scorecard_cli.py draft {args.slug}")
    return 0


def cmd_draft(args: argparse.Namespace) -> int:
    from scorecard.stages import draft

    _claim(args, "draft")
    print(f"draft: {rel(draft(args.slug))}")
    print(f"다음: uv run --frozen python -X utf8 scripts/scorecard_cli.py review-template {args.slug} → 4-way 리뷰 → "
          "승인 대기 보고(사람이 승인 페이지에서 승인한다)")
    return 0


def cmd_review_template(args: argparse.Namespace) -> int:
    from scorecard.stages import review_template

    _claim(args, "review-template")
    print(f"review template: {rel(review_template(args.slug, force=args.force))}")
    print("검토 영역 4개와 체크리스트 Q01~Q23 를 채우고 status 를 pass 로 바꾼 뒤 validate_report_contract.py 로 확인한다")
    return 0


def cmd_approve(args: argparse.Namespace) -> int:
    """에이전트 세션 거부는 `stages.approve` 본체가 한다(2026-10-01 레인 H, F-2)."""
    from scorecard.stages import approve

    print(f"approval: {rel(approve(args.slug, approved_by=args.by, note=args.note, via=args.via))}")
    print(f"다음: uv run --frozen python -X utf8 scripts/build_report.py {args.slug}")
    return 0


def cmd_revoke(args: argparse.Namespace) -> int:
    """에이전트 세션 거부는 `stages.revoke` 본체가 한다(2026-10-01 레인 H, F-2)."""
    from scorecard.stages import revoke

    print(f"revoked: approval.json 삭제, 기록 {rel(revoke(args.slug, by=args.by, note=args.note))}")
    print("다음: 다시 검토한 뒤 승인 페이지에서 승인한다")
    return 0


def _id_list(value: str | None) -> list[str]:
    return [v.strip() for v in value.split(",") if v.strip()] if value else []


def cmd_confirm(args: argparse.Namespace) -> int:
    """근거 확정·거부. 승인이 아니므로 에이전트도 부를 수 있다. 에이전트 세션일 때만 잠금을 검사·기록한다(2026-09-30 조율자 결정)."""
    from scorecard.stages import agent_session_markers, claim_lock, confirm

    agent = bool(agent_session_markers())
    if agent:   # 2026-10-01 V2-11: 다른 소유자 잠금은 먼저 검사하고, 기록은 성공한 뒤에 한다
        claim_lock(args.slug, "confirm", take_lock=args.take_lock, write=False)
    out = confirm(args.slug, evidence_ids=_id_list(args.evidence), reject_ids=_id_list(args.reject), reviewer=args.by,
                  revert_ids=_id_list(args.revert))
    if agent:
        _claim(args, "confirm")
    print(f"confirm: 확정 {len(out['confirmed'])} · 이미 확정 {len(out['already_confirmed'])} · 거부(삭제) {len(out['rejected'])} · 번복 {len(out['reverted'])}"
          f" (검토자 {out['reviewer']}, {out['reviewed_at']})")
    for key in ("confirmed", "already_confirmed", "rejected", "reverted"):
        if out[key]:
            print(f"  {key}: {', '.join(out[key])}")
    print(f"evidence 해시가 바뀌었다({out['evidence_hash'][:16]}…). research → calculate → draft → review 를 다시 돌린다: "
          f"uv run --frozen python -X utf8 scripts/scorecard_cli.py research {args.slug}")
    return 0


def _judge_value(text: str) -> object:
    """`--set` 값. 정수 모양이면 정수(score·A·H), 아니면 문자열이다. 형식 검증은 스키마가 한다."""
    return int(text) if re.fullmatch(r"-?\d+", text) else text


def cmd_judge(args: argparse.Namespace) -> int:
    """정성 판단 입력 수정(2026-10-01 레인 J). 승인이 아니므로 에이전트도 부를 수 있다. 잠금 규칙은 confirm 과 같다."""
    from scorecard.stages import agent_session_markers, claim_lock, revise_judgment

    agent = bool(agent_session_markers())
    if agent:   # 2026-10-01 V2-11: 다른 소유자 잠금은 먼저 검사하고, 기록은 성공한 뒤에 한다(거부된 수정이 잠금을 남기지 않게)
        claim_lock(args.slug, "judge", take_lock=args.take_lock, write=False)
    changes: dict[str, object] = {}
    if args.json:
        loaded = json.loads(Path(args.json).read_text(encoding="utf-8"))
        if not isinstance(loaded, dict):
            raise SchemaError(f"--json 은 {{키: 값}} 객체여야 한다: {args.json}")
        changes.update(loaded)
    for item in args.set or []:
        key, sep, value = item.partition("=")
        if not sep or not key.strip():
            raise SchemaError(f"--set 형식은 key=value: {item!r}")
        changes[key.strip()] = _judge_value(value.strip())
    if args.evidence:
        changes["evidence"] = list(args.evidence)
    out = revise_judgment(args.slug, company_id=args.company, factor=args.factor, changes=changes, reason=args.reason, by=args.by)
    if agent:
        _claim(args, "judge")
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(f"judge: {out['judgment_id']} ({out['kind']}) 수정 — 수정자 {out['current']['reviewer']}, {out['current']['reviewed_at']}")
    for key in ("score", "inputs"):
        if out["previous"][key] != out["current"][key]:
            print(f"  {key}: {json.dumps(out['previous'][key], ensure_ascii=False)} → {json.dumps(out['current'][key], ensure_ascii=False)}")
    if out["previous"]["evidence"] != out["current"]["evidence"]:
        print(f"  evidence: {len(out['previous']['evidence'])}문장 → {len(out['current']['evidence'])}문장")
    print(f"judgments 해시가 바뀌었다({out['judgments_hash'][:16]}…). 점수는 아직 그대로다 — research → calculate → draft → review 를 다시 돌린 뒤 승인한다: "
          f"uv run --frozen python -X utf8 scripts/scorecard_cli.py research {args.slug}")
    return 0


def cmd_propose(args: argparse.Namespace) -> int:
    """판단 변경 제안을 쓴다(2026-10-01). 에이전트도 쓴다. 반영·거부는 사람이 승인 페이지에서 한다."""
    from scorecard.stages import add_proposal

    changes: dict[str, object] = {}
    evidence_after = None
    if args.json:
        loaded = json.loads(Path(args.json).read_text(encoding="utf-8"))
        if not isinstance(loaded, dict):
            raise SchemaError(f"--json 은 {{changes, evidence_after}} 객체여야 한다: {args.json}")
        changes.update(loaded.get("changes") or {})
        evidence_after = loaded.get("evidence_after")
    for item in args.set or []:
        key, sep, value = item.partition("=")
        if not sep or not key.strip():
            raise SchemaError(f"--set 형식은 key=value: {item!r}")
        changes[key.strip()] = _judge_value(value.strip())
    if args.evidence:
        evidence_after = list(args.evidence)
    out = add_proposal(args.slug, company_id=args.company, factor=args.factor, changes=changes, evidence_after=evidence_after,
                       reason=args.reason, evidence_ids=_id_list(args.cite), by=args.by)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(f"propose: {out['proposal_id']} {out['company_id']} {out['factor']} — 사람이 승인 페이지의 '판단 변경 제안' 절에서 반영하거나 거부한다")
    return 0


def cmd_proposal(args: argparse.Namespace) -> int:
    """제안 반영·거부(2026-10-01). 사람 행위라 에이전트 세션이면 거부한다. 거부는 --note(사유) 필수."""
    from scorecard.stages import decide_proposal, undo_proposal

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if args.undo:
        undone = undo_proposal(args.slug, args.id, by=args.by)
        what = "반영을 번복해 판단을 반영 전으로 되돌렸다" if undone["undone"] == "accepted" else "거부를 번복했다"
        print(f"proposal: {args.id} {what} — 결정 전으로 돌아갔다")
        return 0
    out = decide_proposal(args.slug, args.id, accept=args.accept, by=args.by, note=args.note)
    p = out["proposal"]
    if out["accepted"]:
        print(f"proposal: {p['proposal_id']} 반영 — {p['company_id']} {p['factor']} 판단을 고쳤다(수정자 {p['decided_by']}). "
              f"research → calculate → draft → review 를 다시 돌린 뒤 승인한다: "
              f"uv run --frozen python -X utf8 scripts/scorecard_cli.py research {args.slug}")
    else:
        print(f"proposal: {p['proposal_id']} 거부 — 사유: {p['decision_note']}")
    return 0


def cmd_summary(args: argparse.Namespace) -> int:
    """승인 페이지용 요약. --json 은 tests/node/fixtures/summary.sample.json 과 같은 키 구조의 JSON 한 개다."""
    from scorecard.stages import summary

    data = summary(args.slug)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return 0
    appr = data["approval"]
    print(f"summary: {data['run_id']} (as_of {data['as_of']}, 규칙 {data['rule_version']})")
    print(f"승인: {'있음' if appr['exists'] else '없음'}{' · 유효' if appr['valid'] else (' · 무효' if appr['exists'] else '')}")
    print(f"기업 {len(data['companies'])} · 근거 {data['evidence']['selected']}(확정 {data['evidence']['confirmed']}) · 트리거 {len(data['triggers'])}"
          f" · 미결 결정 {', '.join(data['pending_rule_decisions']) or '없음'}")
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


def cmd_trigger_candidates(args: argparse.Namespace) -> int:
    """이전 트리거마다 확인할 수집 후보를 보여준다. 읽기만 하며 입력·점수를 바꾸지 않는다."""
    from scorecard import engine
    from scorecard.schema import SchemaError
    from scorecard.trigger_candidates import render_text, trigger_candidates_for_run

    if args.limit < 1:
        raise SchemaError(f"--limit 은 1 이상: {args.limit}")
    data = trigger_candidates_for_run(args.slug, limit=args.limit)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return 0
    print(render_text(data, engine.load_companies()), end="")
    return 0


def cmd_resolve_cik(args: argparse.Namespace) -> int:
    """티커로 SEC CIK 를 찾아 표로 낸다. `--apply` 는 `resolved` 인 것만 레지스트리에 쓴다.

    2026-09-30 레인 E. 조회는 `resolve_cik` 모듈이, 쓰기는 `registry.set_company_field` 가 한다.
    """
    from scorecard import engine
    from scorecard.registry import set_company_field
    from scorecard.resolve_cik import load_payload, load_ticker_map, resolve

    companies = list(engine.load_companies().values())
    if args.company:
        companies = [c for c in companies if c["company_id"] == args.company]
        if not companies:
            raise SchemaError(f"알 수 없는 company_id: {args.company}")
    try:
        payload = load_payload(from_file=args.from_file)
    except RuntimeError as exc:
        raise SchemaError(str(exc)) from exc
    rows = resolve(companies, load_ticker_map(payload))
    current = {c["company_id"]: c.get("cik") for c in companies}
    if not args.json:
        print("company_id\tticker\t현재 cik\t조회 cik\tstatus")
        for row in rows:
            print(f"{row['company_id']}\t{row['ticker']}\t{current[row['company_id']]}\t{row['cik']}\t{row['status']}")
    applied = []
    for row in rows if args.apply else []:
        if row["status"] == "resolved" and current[row["company_id"]] != row["cik"]:
            out = set_company_field(row["company_id"], "cik", row["cik"], path=engine.COMPANIES_PATH)
            applied.append(out)
            if not args.json:
                print(f"apply: {out['company_id']} cik {out['old']} → {out['new']} ({rel(engine.COMPANIES_PATH)} {out['line_no']}행)")
    if args.json:
        # 2026-10-01 레인 J(F-M-3): 모듈(`resolve_cik.main --json`)과 같은 행에 현재 cik 와 기록 결과를 더한다.
        print(json.dumps({"rows": [{**row, "current_cik": current[row["company_id"]]} for row in rows],
                          "applied": [{"company_id": o["company_id"], "old": o["old"], "new": o["new"]} for o in applied]},
                         ensure_ascii=False))
    elif args.apply:
        print(f"apply: {len(applied)}건 기록 (resolved 가 아닌 행은 쓰지 않는다)")
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    from scorecard.stages import status

    print(json.dumps(status(args.slug), ensure_ascii=False, indent=2))
    return 0


TAKE_LOCK_HELP = "다른 소유자의 실행 잠금(output/<slug>/.lock)을 인수한다"


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
    # `--from-run` 이면 셋 다 이전 실행에서 온다. "없으면 필수" 는 argparse 가 아니라 init_run 이 본다.
    p.add_argument("--as-of")
    p.add_argument("--title")
    p.add_argument("--request")
    p.add_argument("--from-run", help="이어받을 이전 실행의 slug. 관측·판단·출처·결정을 그대로 가져온다")
    p.add_argument("--add-companies", help="이어받기에 덧붙일 기업 ID(쉼표). --companies 는 통째 교체이고 이것은 덧붙이기다")
    p.add_argument("--no-carry-decisions", action="store_true", help="이전 실행의 규칙 결정을 이어받지 않는다")
    p.add_argument("--purpose")
    p.add_argument("--companies")
    p.add_argument("--baseline")
    p.add_argument("--rule")
    p.add_argument("--decision", action="append")
    p.add_argument("--rationale")
    p.add_argument("--by")
    p.add_argument("--price-as-of")
    p.add_argument("--info-cutoff")
    p.add_argument("--force", action="store_true")
    p.add_argument("--take-lock", action="store_true", help=TAKE_LOCK_HELP)
    p.set_defaults(func=cmd_init)

    p = sub.add_parser("collect", help="근거 후보 수집. research 앞에서만 돈다(build 는 재수집하지 않는다)")
    p.add_argument("slug")
    p.add_argument("--company", help="run.companies 가운데 일부(쉼표)")
    p.add_argument("--kind", choices=["news", "filings", "prices", "all"], default="all")
    p.add_argument("--since", help="후보 창 시작일(기본 as_of − 180일)")
    p.add_argument("--forms", help="공시 형식(쉼표). 기본 8-K,10-Q,10-K,20-F,6-K")
    p.add_argument("--locale", default="en-US")
    p.add_argument("--from-file", help="네트워크 대신 읽을 파일(--kind 하나와 함께)")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--take-lock", action="store_true", help=TAKE_LOCK_HELP)
    p.set_defaults(func=cmd_collect)

    p = sub.add_parser("research")
    p.add_argument("slug")
    p.add_argument("--no-register", action="store_true", help="evidence.json 이 인용한 후보의 출처를 sources.json 에 등록하지 않는다")
    p.add_argument("--take-lock", action="store_true", help=TAKE_LOCK_HELP)
    p.set_defaults(func=cmd_research)

    for name, func in (("calculate", cmd_calculate), ("draft", cmd_draft)):
        p = sub.add_parser(name)
        p.add_argument("slug")
        p.add_argument("--take-lock", action="store_true", help=TAKE_LOCK_HELP)
        p.set_defaults(func=func)

    p = sub.add_parser("status")
    p.add_argument("slug")
    p.set_defaults(func=cmd_status)

    p = sub.add_parser("review-template")
    p.add_argument("slug")
    # --force 는 템플릿 재생성만 뜻한다. 잠금 인수는 --take-lock 하나로 한다(두 의미를 한 플래그에 싣지 않는다).
    p.add_argument("--force", action="store_true")
    p.add_argument("--take-lock", action="store_true", help=TAKE_LOCK_HELP)
    p.set_defaults(func=cmd_review_template)

    p = sub.add_parser("diff", help="두 실행을 견준다. subtree 해시 차이는 실패 조건이 아니다 — "
                                    "`as_of` 만 바꿔도 달라지므로 이것으로 실패를 내지 않는다.")
    p.add_argument("slug")
    p.add_argument("--against", required=True, help="견줄 이전 실행의 slug")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_diff)

    p = sub.add_parser("approve", help="사람 셸에서만 된다. 에이전트 세션은 거부한다")
    p.add_argument("slug")
    p.add_argument("--by", required=True)
    p.add_argument("--note")
    p.add_argument("--via", choices=["browser", "terminal"], default="terminal", help="승인 경로(approval.json 의 approved_via)")
    p.set_defaults(func=cmd_approve)

    p = sub.add_parser("revoke", help="승인 취소. 사람 셸에서만 된다. approval.json 을 지우고 revocations.jsonl 에 남긴다")
    p.add_argument("slug")
    p.add_argument("--by", required=True)
    p.add_argument("--note", required=True)
    p.set_defaults(func=cmd_revoke)

    p = sub.add_parser("confirm", help="근거 확정(status: confirmed)·거부(삭제). 승인이 아니다")
    p.add_argument("slug")
    p.add_argument("--evidence", help="확정할 근거 ID(쉼표)")
    p.add_argument("--reject", help="거부해 지울 근거 ID(쉼표)")
    p.add_argument("--revert", help="확정을 번복해 후보로 되돌릴 근거 ID(쉼표)")
    p.add_argument("--by", help="검토자(없으면 SCORECARD_AGENT 또는 사용자명)")
    p.add_argument("--take-lock", action="store_true", help=TAKE_LOCK_HELP)
    p.set_defaults(func=cmd_confirm)

    p = sub.add_parser("propose", help="판단 변경 제안을 쓴다(에이전트도 쓴다). 반영·거부는 사람이 승인 페이지에서 한다")
    p.add_argument("slug")
    p.add_argument("--company", required=True)
    p.add_argument("--factor", required=True, choices=["F1", "F3", "F4", "F5", "F7", "F8", "F9"])
    p.add_argument("--set", action="append", help="바꿀 판정 재료 key=value (F1·F4·F8 은 score=N). 여러 번 준다")
    p.add_argument("--evidence", action="append", help="반영 뒤 근거 문장. 여러 번 주면 그 목록이 근거 전체가 된다")
    p.add_argument("--json", help="{changes: {...}, evidence_after: [...]} JSON 파일(--set·--evidence 가 덮어쓴다)")
    p.add_argument("--reason", required=True, help="제안 사유")
    p.add_argument("--cite", help="인용 근거 ID(쉼표). 반영하면 판단의 evidence_ids 에 더한다(확정 근거만)")
    p.add_argument("--by", help="제안자(기본 SCORECARD_AGENT 또는 사용자 이름)")
    p.set_defaults(func=cmd_propose)

    p = sub.add_parser("proposal", help="판단 변경 제안 반영·거부. 사람 셸에서만 된다. 거부는 --note 필수")
    p.add_argument("slug")
    p.add_argument("--id", required=True, help="PRP-NNN")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--accept", action="store_true", help="반영")
    g.add_argument("--reject", action="store_true", help="거부(--note 필수)")
    g.add_argument("--undo", action="store_true", help="결정 번복(결정 전으로 되돌림, 반영이었으면 판단도 되돌림)")
    p.add_argument("--by", help="결정자(기본 사용자 이름)")
    p.add_argument("--note", help="메모. 거부면 사유로 필수")
    p.set_defaults(func=cmd_proposal)

    p = sub.add_parser("judge", help="정성 판단 입력 수정(점수가 아니라 판단 입력). 승인이 아니다 — 고친 뒤 research 부터 다시 돈다")
    p.add_argument("slug")
    p.add_argument("--company", required=True)
    p.add_argument("--factor", required=True, choices=["F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9"])
    p.add_argument("--set", action="append", help="판정 재료 key=value (F1·F4·F8 은 score=N). 여러 번 준다")
    p.add_argument("--evidence", action="append", help="근거 문장. 여러 번 주면 그 목록으로 통째 바꾼다")
    p.add_argument("--json", help="고칠 값 {키: 값} JSON 파일(--set·--evidence 가 덮어쓴다)")
    p.add_argument("--reason", required=True, help="수정 사유(revision_history 에 남는다)")
    p.add_argument("--by", required=True, help="수정자. 승인 페이지는 사람 이름을 넣는다")
    p.add_argument("--take-lock", action="store_true", help=TAKE_LOCK_HELP)
    p.set_defaults(func=cmd_judge)

    p = sub.add_parser("summary", help="승인 페이지용 요약")
    p.add_argument("slug")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_summary)

    p = sub.add_parser("trigger-candidates", help="이전 트리거마다 확인할 수집 후보를 보여준다(읽기만)")
    p.add_argument("slug")
    p.add_argument("--json", action="store_true", help="사람용 출력 대신 같은 내용의 dict 를 JSON 으로")
    p.add_argument("--limit", type=int, default=5, help="트리거당 상위 N건(기본 5)")
    p.set_defaults(func=cmd_trigger_candidates)

    p = sub.add_parser("resolve-cik", help="티커 → SEC CIK 확인. --apply 는 resolved 인 것만 companies.json 에 쓴다")
    p.add_argument("--company")
    p.add_argument("--from-file", help="SEC company_tickers.json 캐시나 픽스처")
    p.add_argument("--apply", action="store_true")
    p.add_argument("--json", action="store_true", help="표 대신 JSON 한 줄({rows, applied})")
    p.set_defaults(func=cmd_resolve_cik)

    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except SchemaError as exc:
        print(f"[FAIL] {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
