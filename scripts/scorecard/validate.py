# ai_scorecard 계약 검증: plan·run 입력·results 결정론·draft 결속·review 4영역/체크리스트·승인 해시·HTML·이력을 검사한다
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from report_contract_lib import (
    REQUIRED_SCORECARD_PLAN_FRONTMATTER,
    artifact_paths,
    count_h1,
    frontmatter_value,
    has_required_section,
    has_source_markers,
    read_markdown,
    rel,
)

from .engine import HISTORY_CSV, compute, input_hashes, load_context, load_results, results_path, run_dir
from .render_md import REVIEW_AREAS
from .rules import load_rules
from .schema import SchemaError, load_json_strict, sha256_file, validate_approval

REQUIRED_DRAFT_SECTIONS_SCORECARD = ["개요", "종합 순위표", "기업별 상세", "지표 원자료", "방법과 규칙", "References"]
HTML_GENERATOR = "stock-report-harness scorecard-builder"
DISCLAIMER_TERMS = ("투자 조언", "투자 권유", "투자 자문", "교육 및", "매수", "매도")
ROW_RE = re.compile(r"^\|(?P<cells>.+)\|\s*$")
# 렌더러에서 f-string 접두사가 빠지면 파이썬 표현식이 리터럴로 출력된다. 오류가 안 나므로 검증기에서 막는다.
UNRENDERED_RE = re.compile(r"\{(?:esc|fmt_[a-z_]+|total_class|score_class|trap_class|head|c\[|results\[|run\[)[^{}]*\}")


def prel(path: Path) -> str:
    """frontmatter 의 source 경로는 POSIX 구분자로 쓴다. Windows 의 rel() 백슬래시와 비교하지 않도록 정규화한다."""
    return rel(path).replace("\\", "/")


def _table_rows(section: str) -> list[list[str]]:
    rows: list[list[str]] = []
    for line in section.splitlines():
        m = ROW_RE.match(line.strip())
        if not m:
            continue
        cells = [c.strip() for c in m.group("cells").split("|")]
        if all(re.fullmatch(r":?-{3,}:?", c) for c in cells if c):
            continue
        rows.append(cells)
    return rows


def _section(body: str, title: str) -> str:
    m = re.search(rf"^##\s+{re.escape(title)}\s*$(.*?)(?=^##\s+|\Z)", body, re.M | re.S)
    return m.group(1) if m else ""


def validate_scorecard(slug: str, *, require_html: bool = False, check_html_if_present: bool = True, result: Any) -> Any:
    paths = artifact_paths(slug)
    d = run_dir(slug)

    # plan ---------------------------------------------------------------
    if not paths.plan.is_file():
        result.error(f"필수 파일 없음: {prel(paths.plan)}")
        return result
    plan_fm, _plan_body, _raw, _text = read_markdown(paths.plan)
    missing = [k for k in REQUIRED_SCORECARD_PLAN_FRONTMATTER if plan_fm.get(k) in (None, "", [], {})]
    if missing:
        result.error(f"{prel(paths.plan)} frontmatter 필수 키 누락: {', '.join(missing)}")
    if frontmatter_value(plan_fm, "report_type") != "ai_scorecard":
        result.error(f"{prel(paths.plan)} report_type 은 ai_scorecard 여야 함")
    if frontmatter_value(plan_fm, "run_id") != slug:
        result.error(f"{prel(paths.plan)} run_id {frontmatter_value(plan_fm, 'run_id')!r} != slug")
    result.check("scorecard plan frontmatter")

    # run inputs ----------------------------------------------------------
    try:
        ctx = load_context(slug)
    except SchemaError as exc:
        result.error(f"실행 입력 검증 실패: {exc}")
        return result
    if frontmatter_value(plan_fm, "rule_version") != ctx.rules.version:
        result.error(f"plan rule_version {frontmatter_value(plan_fm, 'rule_version')!r} != run {ctx.rules.version!r}")
    if frontmatter_value(plan_fm, "rule_hash") and frontmatter_value(plan_fm, "rule_hash") != ctx.rules.hash:
        result.error("plan rule_hash 가 현재 규칙 파일 해시와 다름 — 규칙이 바뀌었으면 새 실행")
    if frontmatter_value(plan_fm, "as_of") != ctx.run["as_of"]:
        result.error("plan as_of 와 run.json as_of 불일치")
    result.check("run.json/observations/judgments strict schema")

    # research ------------------------------------------------------------
    if not paths.research.is_file():
        result.error(f"필수 파일 없음: {prel(paths.research)}")
    else:
        rfm, _b, _r, _t = read_markdown(paths.research)
        if frontmatter_value(rfm, "plan_source") != prel(paths.plan):
            result.error(f"{prel(paths.research)} plan_source 불일치")
        if frontmatter_value(rfm, "observations_hash") != ctx.hashes["observations"] or frontmatter_value(rfm, "judgments_hash") != ctx.hashes["judgments"]:
            result.error(f"{prel(paths.research)} 가 현재 입력 해시와 다름 — research 를 다시 생성")
        result.check("research bound to input hashes")

    # results -------------------------------------------------------------
    if not results_path(slug).is_file():
        result.error(f"results.json 없음: {rel(results_path(slug))} (calculate 필요)")
        return result
    try:
        results = load_results(slug)
    except SchemaError as exc:
        result.error(str(exc))
        return result
    if results["input_hashes"] != ctx.hashes:
        result.error("results.json 의 input_hashes 가 현재 입력과 다름 — calculate 를 다시 실행")
    fresh = compute(ctx)
    if fresh["results_hash"] != results["results_hash"]:
        result.error("재계산 결과가 저장된 results.json 과 다름 (결정론 위반 또는 규칙 변경)")
    else:
        result.check("results deterministic recompute")

    # draft ---------------------------------------------------------------
    if not paths.draft.is_file():
        result.error(f"필수 파일 없음: {prel(paths.draft)}")
        return result
    dfm, dbody, _r, _t = read_markdown(paths.draft)
    if count_h1(dbody) != 1:
        result.error(f"{prel(paths.draft)} H1 개수 오류")
    for section in REQUIRED_DRAFT_SECTIONS_SCORECARD:
        if not has_required_section(dbody, section):
            result.error(f"{prel(paths.draft)} 필수 섹션 누락: ## {section}")
    if frontmatter_value(dfm, "results_hash") != results["results_hash"]:
        result.error(f"{prel(paths.draft)} results_hash 가 results.json 과 다름 — draft 를 다시 생성")
    if frontmatter_value(dfm, "plan_source") != prel(paths.plan) or frontmatter_value(dfm, "research_source") != prel(paths.research):
        result.error(f"{prel(paths.draft)} plan_source/research_source 불일치")
    ranking_rows = _table_rows(_section(dbody, "종합 순위표"))
    for row in results["ranking"]:
        expected = f"**{row['total']}**"
        if not any(len(cells) >= 14 and cells[1] == row["display_name"] and cells[13] == expected for cells in ranking_rows):
            result.error(f"draft 순위표에 {row['display_name']} 조정총점 {row['total']} 행이 없음")
            break
    else:
        result.check("draft ranking table matches results")

    # review --------------------------------------------------------------
    if not paths.review.is_file():
        result.error(f"필수 파일 없음: {rel(paths.review)}")
        return result
    vfm, vbody, _r, _t = read_markdown(paths.review)
    status = frontmatter_value(vfm, "status")
    if status != "pass":
        result.error(f"{rel(paths.review)} review status 가 pass 가 아님: {status!r}")
    for key, expected in (("plan_source", prel(paths.plan)), ("research_source", prel(paths.research)), ("draft_source", prel(paths.draft))):
        if frontmatter_value(vfm, key) != expected:
            result.error(f"{rel(paths.review)} {key} 불일치")
    if frontmatter_value(vfm, "review_type") != "separate-session-4way":
        result.error("review_type 은 separate-session-4way 여야 함")
    if frontmatter_value(vfm, "review_execution") != "separate_subagent_sessions":
        result.error("review_execution 은 separate_subagent_sessions 여야 함")
    if frontmatter_value(vfm, "results_hash") != results["results_hash"]:
        result.error("review results_hash 가 results.json 과 다름 — 검토 대상이 바뀌었으므로 리뷰 무효")
    draft_hash = sha256_file(paths.draft)
    if frontmatter_value(vfm, "draft_hash") != draft_hash:
        result.error("review draft_hash 가 현재 draft 와 다름 — 초안이 바뀌었으므로 리뷰 무효")
    area_rows = _table_rows(_section(vbody, "검토 영역"))
    area_labels = {label for _, label, _ in REVIEW_AREAS}
    seen_areas: dict[str, str] = {}
    for cells in area_rows:
        if len(cells) >= 4 and cells[0] in area_labels:
            seen_areas[cells[0]] = cells[3]
    for label in area_labels:
        res = seen_areas.get(label)
        if res is None:
            result.error(f"리뷰 검토 영역 누락: {label}")
        elif status == "pass" and res != "pass":
            result.error(f"리뷰 영역 {label} 결과가 pass 가 아님: {res!r}")
    if status == "pass":
        for cells in area_rows:
            if len(cells) >= 4 and cells[0] in area_labels and not cells[2].strip():
                result.error(f"리뷰 영역 {cells[0]} 검토자 미기재 — 수행하지 않은 검토를 pass 로 표시할 수 없음")
    check_rows = _table_rows(_section(vbody, "체크리스트"))
    ids = {q["id"] for q in ctx.rules.checklist()}
    seen_q: dict[str, tuple[str, str]] = {}
    for cells in check_rows:
        if len(cells) >= 4 and cells[0] in ids:
            seen_q[cells[0]] = (cells[2], cells[3])
    for qid in sorted(ids):
        if qid not in seen_q:
            result.error(f"체크리스트 {qid} 행 누락")
            continue
        res, basis = seen_q[qid]
        if res not in {"pass", "fail", "not_applicable"} and status == "pass":
            result.error(f"체크리스트 {qid} 결과 {res!r} 는 pass/fail/not_applicable 이어야 함")
        if status == "pass" and res == "fail":
            result.error(f"체크리스트 {qid} 가 fail 인데 review status 가 pass")
        if status == "pass" and not basis.strip():
            result.error(f"체크리스트 {qid} 근거 없음 (not_applicable 도 사유 필요)")
    result.check("review 4-area + checklist structure")

    # approval / html / history (build gate) -------------------------------
    approval_path = d / "approval.json"
    if require_html or paths.html.is_file():
        if not approval_path.is_file():
            result.error("사용자 승인 없음: awaiting_user (scorecard_cli.py approve <slug> --by <name>)")
        else:
            try:
                approval = validate_approval(load_json_strict(approval_path), slug)
                from .stages import current_hashes

                if approval["hashes"] != current_hashes(slug):
                    result.error("승인 이후 규칙/자료/판단/결과/초안이 바뀜 — 승인 무효(awaiting_user)")
                else:
                    result.check("approval hashes match current inputs")
            except SchemaError as exc:
                result.error(f"approval.json 오류: {exc}")

    if require_html or (check_html_if_present and paths.html.is_file()):
        _validate_html(slug, paths.html, results, require_html, result)
    if require_html and paths.html.is_file():
        _validate_history(slug, approval_path, results, result)
    return result


def _validate_html(slug: str, html_path: Path, results: dict[str, Any], require_html: bool, result: Any) -> None:
    if not html_path.is_file():
        if require_html:
            result.error(f"HTML 없음: {rel(html_path)}")
        return
    text = html_path.read_text(encoding="utf-8")
    if has_source_markers(text):
        result.error("최종 HTML 에 [S1]/[N1]/[P1] 류 source marker 잔존")
    if HTML_GENERATOR not in text:
        result.error(f"HTML generator 메타 누락: {HTML_GENERATOR}")
    if f'name="results-hash" content="{results["results_hash"]}"' not in text:
        result.error("HTML 이 현재 results.json 해시를 가리키지 않음 — build 를 다시 실행")
    if not any(term in text for term in DISCLAIMER_TERMS):
        result.error("HTML footer 투자 유의 문구 없음")
    unrendered = UNRENDERED_RE.findall(text)
    if unrendered:
        result.error(f"HTML 에 렌더되지 않은 템플릿 표현식 {len(unrendered)}건 (f-string 접두사 누락 의심): {', '.join(sorted(set(unrendered))[:3])}")
    if 'name="viewport"' not in text:
        result.error("HTML viewport 메타 없음")
    for row in results["ranking"]:
        if f'data-company="{row["company_id"]}"' not in text:
            result.error(f"HTML 순위표에 {row['company_id']} 행 없음")
            break
    result.check("HTML exists, marker-free, bound to results")


def _validate_history(slug: str, approval_path: Path, results: dict[str, Any], result: Any) -> None:
    if not HISTORY_CSV.is_file() or not approval_path.is_file():
        result.error("history.csv 또는 approval.json 없음")
        return
    import csv

    approval = load_json_strict(approval_path)
    with HISTORY_CSV.open("r", encoding="utf-8", newline="") as fh:
        keys = {(r["run_id"], r["approval_id"], r["company_id"]) for r in csv.DictReader(fh)}
    missing = [c["company_id"] for c in results["companies"] if (slug, approval["approval_id"], c["company_id"]) not in keys]
    if missing:
        result.error(f"history.csv 에 승인본 행 누락: {', '.join(missing[:5])}")
    else:
        result.check("history.csv contains approved rows")
