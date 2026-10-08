# ai_scorecard 계약 검증: plan·run 입력·results 결정론·draft 결속·review 4영역/체크리스트·승인 해시·HTML·이력을 검사한다
from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Mapping

from report_contract_lib import (
    REQUIRED_SCORECARD_PLAN_FRONTMATTER,
    count_h1,
    frontmatter_value,
    has_required_section,
    has_source_markers,
    read_markdown,
    rel,
)

from .engine import HISTORY_CSV, compute, input_hashes, load_context, load_results, results_path
from .paths import RunPaths, run_paths
from .render_md import REVIEW_AREAS
from .rules import load_rules
from .schema import SchemaError, load_json_strict, sha256_file, validate_approval

REQUIRED_DRAFT_SECTIONS_SCORECARD = ["개요", "종합 순위표", "기업별 상세", "지표 원자료", "방법과 규칙", "References"]
HTML_GENERATOR = "stock-report-harness scorecard-builder"
DISCLAIMER_TERMS = ("투자 조언", "투자 권유", "투자 자문", "교육 및", "매수", "매도")
ROW_RE = re.compile(r"^\|(?P<cells>.+)\|\s*$")
# 2026-09-17 FIX-60: 체크리스트 fail 의 근거 칸에서 긴장 번호를 찾는다. **문자열만 보고 통과시키지 않는다** —
# 규칙 파일의 open_tensions 와 대조해 실재하고 recheck_at 이 있는 것만 예외로 인정한다(오타가 예외를 만들지 않게).
TENSION_RE = re.compile(r"TEN-[A-Z0-9-]+")
# 2026-09-30 레인 A: 실행 묶음(output/<slug>/)으로 옮긴 기존 실행 둘은 research·draft·review frontmatter 에
# 옛 경로 문자열을 갖고 있다. draft 는 승인 해시 대상이라 고칠 수 없으므로 **이 두 실행에만** 옛 문자열을 허용한다.
# 다른 실행에 옛 문자열이 나오면 불일치 오류다.
LEGACY_RUNS = frozenset({"ai-scorecard-2026-09-baseline", "ai-scorecard-2026-09-obsreg"})
LEGACY_SOURCE_STRINGS = {"plan": "plan/{slug}.md", "research": "research/{slug}.md", "draft": "drafts/{slug}.md"}

# 렌더러에서 f-string 접두사가 빠지면 파이썬 표현식이 리터럴로 출력된다. 오류가 안 나므로 검증기에서 막는다.
UNRENDERED_RE = re.compile(r"\{(?:esc|fmt_[a-z_]+|total_class|score_class|trap_class|head|c\[|results\[|run\[)[^{}]*\}")


def prel(path: Path) -> str:
    """frontmatter 의 source 경로는 POSIX 구분자로 쓴다. Windows 의 rel() 백슬래시와 비교하지 않도록 정규화한다."""
    return rel(path).replace("\\", "/")


def source_matches(paths: RunPaths, kind: str, actual: str) -> bool:
    """frontmatter 의 `<kind>_source` 가 묶음 경로와 같은지. 옮긴 기존 실행만 옛 문자열도 받는다."""
    if actual == paths.rel(getattr(paths, kind)):
        return True
    return paths.slug in LEGACY_RUNS and actual == LEGACY_SOURCE_STRINGS[kind].format(slug=paths.slug)


def _carried_exception(basis: str, tensions: dict[str, dict[str, Any]]) -> tuple[bool, list[str], str]:
    """승계 판단 예외가 서는지 (AGENTS.md 「리뷰 범위 — 승계 판단 예외」 · 리뷰 템플릿 본문).

    예외는 **긴장으로 등록되고 재검토 시점이 있을 때만** 선다. 셋을 가른다 —
    번호가 없다 / 번호가 규칙에 없다 / 번호는 있는데 recheck_at 이 없다. 어느 쪽이든 막는다.

    선언은 AGENTS.md 와 템플릿에 있는데 **읽는 코드가 없어** 승인이 막혔다(2026-09-17). 선언대로 구현한다.
    """
    ids = list(dict.fromkeys(TENSION_RE.findall(basis or "")))   # 본문이 같은 번호를 여러 번 적어도 한 번만 센다
    if not ids:
        return False, [], "근거 칸에 긴장 번호(TEN-…)가 없음"
    unknown = [t for t in ids if t not in tensions]
    if unknown:
        return False, ids, f"규칙 open_tensions 에 없는 긴장 번호 {unknown}"
    ok = [t for t in ids if (tensions[t].get("recheck_at") or "").strip()]
    if not ok:
        return False, ids, f"긴장 {ids} 에 recheck_at 이 없음"
    return True, ok, ""


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


def check_source_allowlist(rules: Any, sources: dict[str, Any], result: Any) -> bool:
    """규칙에 원천 정책이 있는 버전에서만 검사한다. 정책이 없는 v1.5 실행은 그대로 통과한다."""
    if not rules.source_policy:
        return False
    for item in sources.get("items", []):
        violation = rules.source_violation(item.get("url"))
        if violation:
            result.error(f"sources.json {item.get('source_id')}: {violation}")
    result.check("자료 원천 allowlist")
    return True


# 2026-10-06 사용자 지시(AGENTS.md 「금지·주의」): 화면에 실리는 문장은 완결된 현재 상태 문장이다. 규칙 버전 표기,
# 변경 표시, 작업 번호, 이전 판·다른 문장·다른 트리거를 가리키는 표현을 막는다. 규칙 v1.9 이상 실행에만 댄다
# (옛 승인 실행은 그때 문면 그대로 둔다). 트리거 carry.finding 과 근거 excerpt(원문 제목)는 대상이 아니다.
SELF_CONTAINED_MIN_RULE = (1, 9)
SELF_CONTAINED_BANNED = [
    (re.compile(r"\bv1\.\d"), "규칙 버전 표기"),
    (re.compile(r"[🆕📈📉🔧📐📏]"), "변경 표시 기호"),
    (re.compile(r"~~"), "취소선"),
    (re.compile(r"superseded", re.I), "대체 표시"),
    (re.compile(r"\b(?:FIX|IMPL|MISS-LABEL|OBS-REG|G1-FILL|NONOP|CASH-FCF|NETCASH|F6-REG|F6-SPEC|F6-FX)-\d+"), "작업 번호"),
    (re.compile(r"obsreg", re.I), "작업 번호"),
    (re.compile(r"기준선|시험 실행|이전 실행에서|위 줄|아래 줄|다음 줄|윗줄"), "다른 판·다른 문장 참조"),
    (re.compile(r"별표\s*[A-J](?![A-Za-z0-9])"), "폐지된 별표 이름"),
]
TRIGGER_CROSS_REF = re.compile(r"\bTRIG-\d{3}|\bTRG-\d{3}|기준선 트리거")


def self_contained_violations(ctx: Any) -> list[str]:
    """화면 문장의 금지 표기 목록. `기업·위치: 사유 — 문장 앞부분` 형태."""
    def hits(text: str, extra: tuple[tuple[re.Pattern[str], str], ...] = ()) -> list[str]:
        return [why for pat, why in (*SELF_CONTAINED_BANNED, *extra) if pat.search(text or "")]

    out: list[str] = []

    def add(where: str, text: str, extra: tuple[tuple[re.Pattern[str], str], ...] = ()) -> None:
        for why in hits(text, extra):
            out.append(f"{where}: {why} — {str(text)[:60]}")

    for j in ctx.judgments:
        for i, e in enumerate(j.get("evidence") or []):
            add(f"{j['judgment_id']} 근거[{i}]", str(e))
        for key, label in (("evidence_up", "올릴 근거"), ("evidence_down", "내릴 근거")):
            for i, e in enumerate(j.get(key) or []):
                add(f"{j['judgment_id']} {label}[{i}]", str(e))
    for cid, s in (ctx.company_summaries or {}).items():
        add(f"{cid} 기업 요약", s["text"])
    for e in ctx.evidence or []:
        for key in ("relevance", "conditional_impact"):
            add(f"{e['evidence_id']}.{key}", e[key])
        for key in ("counter_evidence", "unverified"):
            for i, s in enumerate(e[key]):
                add(f"{e['evidence_id']}.{key}[{i}]", s)
    cross = ((TRIGGER_CROSS_REF, "다른 트리거 참조"),)
    for t in ctx.triggers or []:
        for key in ("observation", "condition"):
            add(f"{t['trigger_id']}.{key}", t[key], cross)
        add(f"{t['trigger_id']}.recheck.what", t["recheck"]["what"], cross)
    return out


def _rule_at_least(version: str, minimum: tuple[int, ...]) -> bool:
    return tuple(int(x) for x in re.findall(r"\d+", version)) >= minimum


# 2026-10-07 사용자 지시: 판단 근거는 판정(evidence)·올릴 근거(evidence_up)·내릴 근거(evidence_down) 세 칸으로 쓴다.
# 규칙 v1.9 이상 실행에만 댄다. 같은 검사를 판단을 쓰는 시점(stages.revise_judgment)과 검증기가 함께 쓴다.
THREE_WAY_MIN_RULE = (1, 9)


def three_way_item_violations(item: Mapping[str, Any]) -> list[str]:
    """판단 하나의 세 칸 형식 위반. 판정 칸이 비지 않는 것은 스키마가 본다."""
    out: list[str] = []
    missing = [k for k in ("evidence_up", "evidence_down") if k not in item]
    if missing:
        out.append(f"{'·'.join(missing)} 칸이 없다(빈 칸이면 빈 목록으로 둔다)")
    elif not (item["evidence_up"] or item["evidence_down"]):
        out.append("올릴 근거와 내릴 근거가 둘 다 비었다(방향이 있는 사실이 하나는 있어야 한다)")
    if item.get("counter_evidence"):
        out.append("counter_evidence 는 비워 두고 반대 방향 사실은 올릴·내릴 근거 칸에 쓴다")
    return out


def three_way_violations(ctx: Any) -> list[str]:
    return [f"{j['judgment_id']}: {why}" for j in ctx.judgments for why in three_way_item_violations(j)]


# 2026-10-07 사용자 지시("URL 이 있어야 하지 않겠냐"): 외부 분석이 확정 근거 72건 전부 excerpt 가 제목과 같고 판단 문장이
# URL 없는 내부 기준선 문서만 가리킨다는 것을 짚었다. 올릴·내릴 근거의 모든 줄은 끝에 근거 표지 `[EV-…]` 를 달고,
# 표지가 가리키는 근거는 확정됐고 출처 URL·본문 발췌(제목과 다름)·인용 위치(locator)를 갖춰야 한다.
# 판정 칸(결론·저울질·미확인)은 표지를 요구하지 않는다. 같은 검사를 쓰는 시점과 검증기가 함께 쓴다.
CITATION_MIN_RULE = (1, 9)
_EV = r"EV-[a-z0-9-]+-\d{3}"
CITE_TAIL_RE = re.compile(rf"\[({_EV}(?:\s*,\s*{_EV})*)\]\s*$")


def cited_ids(line: str) -> list[str]:
    m = CITE_TAIL_RE.search(line or "")
    return re.findall(_EV, m.group(1)) if m else []


def citable_evidence_violation(e: Mapping[str, Any] | None, url: str | None) -> str | None:
    """판단 문장이 인용할 수 있는 근거인지. 안 되면 사유."""
    if e is None:
        return "evidence.json 에 없는 근거"
    if e.get("status") != "confirmed":
        return "확정되지 않은 근거"
    if not (url or "").startswith(("https://", "http://")):
        return "출처에 URL 이 없다"
    if " ".join(e["excerpt"].split()).casefold() == " ".join(e["title"].split()).casefold():
        return "excerpt 가 제목과 같다(본문에서 발췌한다)"
    if not (e.get("locator") or "").strip():
        return "인용 위치(locator)가 없다"
    return None


def citation_item_violations(item: Mapping[str, Any], evidence: Mapping[str, Mapping[str, Any]],
                             urls: Mapping[str, str | None]) -> list[str]:
    out: list[str] = []
    for key, label in (("evidence_up", "올릴 근거"), ("evidence_down", "내릴 근거")):
        for i, line in enumerate(item.get(key) or []):
            ids = cited_ids(line)
            if not ids:
                out.append(f"{label}[{i}]: 줄 끝에 근거 표지 [EV-…] 가 없다 — {line[:40]}")
                continue
            for eid in ids:
                e = evidence.get(eid)
                why = citable_evidence_violation(e, urls.get(e["source_id"]) if e else None)
                if why:
                    out.append(f"{label}[{i}]: {eid} — {why}")
    return out


def citation_violations(ctx: Any) -> list[str]:
    evidence = {e["evidence_id"]: e for e in (ctx.evidence or [])}
    urls = {s["source_id"]: s.get("url") for s in ctx.sources.get("items", [])}
    return [f"{j['judgment_id']} {why}" for j in ctx.judgments for why in citation_item_violations(j, evidence, urls)]


# 2026-10-08 사용자 결정(규칙 v2.0 policies.rejudge, rules.md 2.9): 정기 실행은 정성 판단 일곱 항목을 모든 기업에 대해 그 실행의
# 근거로 다시 매긴다. 승계(status: carried)는 기업 추가 실행의 기존 기업에만 남는다. 정책이 없는 규칙(v1.9 이하)은 보지 않는다.
# 판단을 고치는 단계(init·judge·propose·proposal)는 막지 않고, 이 검사가 계약 검증(리뷰·승인·빌드)에서 막는다.
def is_regular_run(run: Mapping[str, Any]) -> bool:
    """정기 실행인가. 이어받지 않았거나(continued_from 없음) 이어받았어도 더한 기업이 없으면 정기 실행이다."""
    cont = run.get("continued_from")
    return not cont or not cont.get("added_companies")


def rejudge_findings(ctx: Any) -> list[tuple[str, str]]:
    """rejudge 정책 위반을 (판단 ID, 사유) 로 돌려준다. 정기 실행은 모든 기업, 기업 추가 실행은 더한 기업의 정성 판단만 본다.
    계약 검증(validate_scorecard)과 research 단계(stages.research)가 이 함수를 같이 부른다(2026-10-08)."""
    policy = ctx.rules.payload["policies"].get("rejudge")
    if not policy:
        return []
    factors = set(policy.get("qualitative_factors") or [])
    cont = ctx.run.get("continued_from") or {}
    added = set(cont.get("added_companies") or [])
    regular = is_regular_run(ctx.run)
    prior_as_of = cont.get("as_of")
    out: list[tuple[str, str]] = []
    for j in ctx.judgments:
        if j["factor"] not in factors or not (regular or j["company_id"] in added):
            continue
        if policy.get("carried_allowed_only_in_extend_runs") and j["status"] == "carried":
            where = "정기 실행" if regular else "기업 추가 실행의 신규 기업"
            out.append((j["judgment_id"], f"{where}에 승계 판단(status: carried)이 남아 있다 — 이번 실행의 근거로 다시 매긴다"))
            continue
        if prior_as_of and policy.get("reviewed_at_after_prior_as_of"):
            reconfirmed = (j.get("reconfirmed") or [{}])[-1].get("at")
            if max(d for d in (j["reviewed_at"], reconfirmed) if d) <= prior_as_of:
                out.append((j["judgment_id"], f"이번 실행에서 다시 매기지 않은 판단 — 검토일 {j['reviewed_at']}"
                            + (f"·재확인 {reconfirmed}" if reconfirmed else "")
                            + f" 이 이전 실행 기준일 {prior_as_of} 보다 뒤가 아니다"))
    return out


def rejudge_violations(ctx: Any) -> list[str]:
    """rejudge 정책 위반 목록(`판단 ID: 사유`)."""
    return [f"{jid}: {why}" for jid, why in rejudge_findings(ctx)]


def validate_scorecard(slug: str, *, require_html: bool = False, check_html_if_present: bool = True, result: Any) -> Any:
    paths = run_paths(slug)
    d = paths.run_dir

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

    # 완결된 문장 ----------------------------------------------------------
    if _rule_at_least(ctx.rules.version, SELF_CONTAINED_MIN_RULE):
        bad = self_contained_violations(ctx)
        for line in bad[:20]:
            result.error(f"완결된 문장이 아니다(AGENTS.md 「금지·주의」) — {line}")
        if len(bad) > 20:
            result.error(f"완결된 문장이 아닌 곳이 {len(bad) - 20}건 더 있다")
        if not bad:
            result.check("display text is self-contained")

    # 근거 세 칸 ------------------------------------------------------------
    if _rule_at_least(ctx.rules.version, THREE_WAY_MIN_RULE):
        bad = three_way_violations(ctx)
        for line in bad[:20]:
            result.error(f"판단 근거가 세 칸(판정·올릴 근거·내릴 근거)이 아니다(guide.md 5.6) — {line}")
        if len(bad) > 20:
            result.error(f"세 칸이 아닌 판단이 {len(bad) - 20}건 더 있다")
        if not bad:
            result.check("judgment evidence is three-way")

    # 근거 표지 -------------------------------------------------------------
    if _rule_at_least(ctx.rules.version, CITATION_MIN_RULE):
        bad = citation_violations(ctx)
        for line in bad[:20]:
            result.error(f"올릴·내릴 근거가 원문 근거와 이어지지 않는다(guide.md 5.7) — {line}")
        if len(bad) > 20:
            result.error(f"원문 근거와 이어지지 않는 줄이 {len(bad) - 20}건 더 있다")
        if not bad:
            result.check("judgment direction lines cite source evidence")

    # 정기 실행 재판단 -------------------------------------------------------
    rejudge = ctx.rules.payload["policies"].get("rejudge")
    regular_run = is_regular_run(ctx.run)
    if rejudge:
        bad = rejudge_violations(ctx)
        for line in bad[:20]:
            result.error(f"정기 실행은 정성 판단을 모두 다시 매긴다(rules.md 2.9) — {line}")
        if len(bad) > 20:
            result.error(f"다시 매기지 않은 정성 판단이 {len(bad) - 20}건 더 있다")
        if not bad:
            result.check("rejudge policy: all qualitative judgments are new for this run" if regular_run else
                         "rejudge policy: added companies' qualitative judgments are new for this run")

    # 자료 원천 allowlist --------------------------------------------------
    check_source_allowlist(ctx.rules, ctx.sources, result)

    # research ------------------------------------------------------------
    if not paths.research.is_file():
        result.error(f"필수 파일 없음: {prel(paths.research)}")
    else:
        rfm, _b, _r, _t = read_markdown(paths.research)
        if not source_matches(paths, "plan", frontmatter_value(rfm, "plan_source")):
            result.error(f"{prel(paths.research)} plan_source 불일치")
        if frontmatter_value(rfm, "observations_hash") != ctx.hashes["observations"] or frontmatter_value(rfm, "judgments_hash") != ctx.hashes["judgments"]:
            result.error(f"{prel(paths.research)} 가 현재 입력 해시와 다름 — research 를 다시 생성")
        # 2026-09-30 레인 E: 근거·트리거 파일이 있을 때만 대조한다. 파일은 없는데 해시가 적혀 있어도 낡은 research 다.
        for key in ("evidence", "triggers"):
            if frontmatter_value(rfm, f"{key}_hash") != ctx.hashes.get(key, ""):
                result.error(f"{prel(paths.research)} {key}_hash 가 현재 {key} 와 다름 — research 를 다시 생성")
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
    if not (source_matches(paths, "plan", frontmatter_value(dfm, "plan_source"))
            and source_matches(paths, "research", frontmatter_value(dfm, "research_source"))):
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
    for kind in ("plan", "research", "draft"):
        key = f"{kind}_source"
        if not source_matches(paths, kind, frontmatter_value(vfm, key)):
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
    review_errors_before = len(result.errors)
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
    # 2026-09-17 FIX-60: 승계 판단 예외를 규칙의 open_tensions 와 대조해 판정한다.
    tensions = {t["id"]: t for t in (ctx.rules.payload.get("open_tensions") or [])}
    carried: list[str] = []
    for qid in sorted(ids):
        if qid not in seen_q:
            result.error(f"체크리스트 {qid} 행 누락")
            continue
        res, basis = seen_q[qid]
        if res not in {"pass", "fail", "not_applicable"} and status == "pass":
            result.error(f"체크리스트 {qid} 결과 {res!r} 는 pass/fail/not_applicable 이어야 함")
        if status == "pass" and res == "fail":
            excepted, cited, why = _carried_exception(basis, tensions)
            if excepted and rejudge and rejudge.get("review_carried_exception_only_in_extend_runs") and regular_run:
                # 2026-10-08 사용자 결정(rules.md 2.9): 승계 판단 예외는 기업 추가 실행에만 있다. 정기 실행의 fail 은 막는다.
                excepted, why = False, "정기 실행에는 승계 판단 예외를 적용하지 않는다(rules.md 2.9)"
            if excepted:
                # **조용히 넘어가지 않는다.** 예외로 통과한 것을 세어 경고로 남긴다.
                carried.append(f"{qid}({'·'.join(cited)})")
            else:
                result.error(f"체크리스트 {qid} 가 fail 인데 review status 가 pass — 승계 판단 예외가 서지 않음: {why}")
        if status == "pass" and not basis.strip():
            result.error(f"체크리스트 {qid} 근거 없음 (not_applicable 도 사유 필요)")
    if carried:
        result.warn(f"승계 예외로 통과한 체크리스트 fail {len(carried)}건: {' · '.join(carried)}")
        # 이 검사가 기계로 확인하는 것은 **등록과 재검토 시점**뿐이다. AGENTS.md 「리뷰 범위 — 승계 판단 예외」의 나머지 조건
        # (`이번 실행이 그 판단에 쓰인 잣대를 바꾸지 않았다`)은 사람이 판정한다 — 자동 통과로 읽지 않는다.
        result.warn("위 예외는 긴장 등록·재검토 시점만 기계로 확인한 것이다. "
                    "`이번 실행이 잣대를 바꾸지 않았다`는 조건은 리뷰어가 판정한다(AGENTS.md 「리뷰 범위 — 승계 판단 예외」)")
    if len(result.errors) == review_errors_before:
        result.check("review 4-area + checklist structure")

    # approval / html / history (build gate) -------------------------------
    approval_path = d / "approval.json"
    # 2026-10-07: 승인 전 검증(approve·승인 페이지, check_html_if_present=False)은 승인 여부를 묻지 않는다. 이전 빌드의
    # report.html 이 남은 실행에서 '사용자 승인 없음' 이 막힌 이유로 나와 다시 승인할 수 없었다.
    if require_html or (check_html_if_present and paths.html.is_file()):
        if not approval_path.is_file():
            result.error("사용자 승인 없음: awaiting_user (사람이 `node server.js --approvals` 승인 페이지에서 승인한다)")
        else:
            try:
                approval = validate_approval(load_json_strict(approval_path), slug)
                from .stages import approval_mismatches, current_hashes

                if approval_mismatches(approval["hashes"], current_hashes(slug)):
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
    # 2026-10-08 사용자 결정: 첫 화면의 판단 현황 상자가 있고, 이어받은(carried_score) 칸 수가 results 와 같아야 한다.
    carried_cells = sum(1 for c in results["companies"] if not c["reference"]
                        for fid in c["factors"] if c["factors"][fid]["status"] == "carried_score")
    if 'id="judgment-status"' not in text:
        result.error("HTML 첫 화면에 판단 현황 상자(id=judgment-status) 없음")
    elif f'data-carried="{carried_cells}"' not in text:
        result.error(f"HTML 판단 현황 상자의 이어받은 칸 수가 results 와 다름 (results {carried_cells}칸)")
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
