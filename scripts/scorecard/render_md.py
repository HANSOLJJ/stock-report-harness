# 실행 원본(run·observations·judgments·results)에서 plan/research/draft/review 템플릿/preview Markdown 을 생성하는 렌더러
from __future__ import annotations

from typing import Any

from report_contract_lib import rel

from .paths import run_paths

from . import render_common as rc
from .render_common import FACTOR_LABELS, fmt_num, fmt_usd
from .schema import FACTOR_IDS, MOAT_FACTORS, TRAP_FACTORS

# 2026-09-17 FIX-78 S1: `승계` 가 근거 머리줄의 `사용자의 판단` 과 **같은 화면에** 있어 둘이
# 다른 것처럼 읽혔다(사용자 지적). 같은 것은 같은 말로 부른다. `status` 값은 그대로이고 표시만 바꾼다.
STATUS_LABEL = {
    "ok": "이번 실행 산출", "carried_score": "사용자의 판단", "needs_judgment": "판단 대기",
    "needs_rule_decision": "규칙 결정 대기",
    "pending_data": "자료 대기", "error": "오류",
    # 2026-09-16 FIX-58 1단계(7차 리뷰 D): factor status 에 쓰일 수 있는 키인데 라벨이 없었다.
    "unavailable": "산출 불가",
}
REVIEW_AREAS = [
    # 2026-10-02 사용자 지시: 이해상충 표기는 리뷰 대상에서 뺀다(AGENTS.md 금지·주의). 이전 문구는 끝에 `·이해상충` 이 있었다.
    ("fact-sources", "사실·출처", "숫자·기업 귀속·기준 시점·공시·뉴스·부재 주장"),
    ("financial-calc", "재무 계산", "EPS·환율·ADR·TTM·FCF·런웨이·약정·단위·부호"),
    ("rule-consistency", "규칙 일관성", "factor 정의·상하한·예외·중복 속성·정성 승계·전 기업 동일 기준"),
    ("output-readability", "출력·가독성", "표·카드·근거·차트·이력 일치, 낡은 비교 문장, 모바일·단일 HTML"),
]
DISCLAIMER = (
    "이 채점표는 교육 및 정보 제공 목적의 정성 분석입니다. 특정 종목의 매수·매도를 권유하지 않으며 투자 자문이 아닙니다. "
    "점수는 규칙과 입력에서 계산된 결과이며 수익률 예측이나 검증된 승리 확률이 아닙니다."
)


# ------------------------------------------------------------------ 포맷

def fmt_pct(value: float | None) -> str:
    if value is None:
        return "—"
    return f"{value * 100:.0f}%"


def fmt_score(value: int | None) -> str:
    return "—" if value is None else str(int(value))


def yaml_str(value: Any) -> str:
    text = str(value)
    if any(ch in text for ch in ":#'\"[]{}") or text.strip() != text:
        return '"' + text.replace('"', '\\"') + '"'
    return text


def frontmatter(fields: list[tuple[str, Any]]) -> str:
    lines = ["---"]
    for key, value in fields:
        if isinstance(value, list):
            lines.append(f"{key}:")
            lines.extend(f"  - {yaml_str(item)}" for item in value)
        else:
            lines.append(f"{key}: {yaml_str(value)}")
    lines.append("---")
    return "\n".join(lines)


def table(headers: list[str], rows: list[list[Any]], align: list[str] | None = None) -> str:
    align = align or ["---"] * len(headers)
    out = ["| " + " | ".join(headers) + " |", "| " + " | ".join(align) + " |"]
    for row in rows:
        out.append("| " + " | ".join(str(c).replace("|", "\\|").replace("\n", " ") for c in row) + " |")
    return "\n".join(out)


# ------------------------------------------------------------------ plan

def render_plan(run: dict[str, Any], rules: Any, companies: dict[str, dict[str, Any]], *, request: str, baseline_note: str) -> str:
    paths = run_paths(run["run_id"])
    fm = frontmatter([
        ("slug", run["run_id"]), ("report_type", "ai_scorecard"), ("topic", run["title"]), ("request", request),
        ("output_type", "scorecard"), ("audience", "intermediate"), ("run_id", run["run_id"]), ("as_of", run["as_of"]),
        ("price_as_of", run.get("price_as_of") or run["as_of"]), ("info_cutoff", run.get("info_cutoff") or run["as_of"]),
        ("rule_version", rules.version), ("rule_hash", rules.hash), ("baseline_id", run["baseline_id"]),
        ("companies", run["companies"]), ("created_at", run["created_at"]), ("assumptions", run["assumptions"]),
    ])
    factor_rows = [[FACTOR_LABELS[f], rules.factor(f)["mode"], f"{rules.factor(f)['range'][0]}~{rules.factor(f)['range'][1]}", ", ".join(rules.factor(f).get("decision_ids", [])) or "—"] for f in FACTOR_IDS]
    company_rows = [[cid, companies[cid]["display_name"], companies[cid]["type"], "상장" if companies[cid]["listed"] else "비상장", companies[cid]["scope"]] for cid in run["companies"]]
    pending = [d for d in rules.pending_decisions() if d.get("blocking")]
    decision_rows = [[d["id"], d["summary"], ", ".join(d.get("affects", [])), next((r["choice"] for r in run["decisions"] if r["id"] == d["id"]), "미결")] for d in pending]
    body = f"""
# Planning Brief — {run['title']}

## 요청 해석

- 대상: AI 기업 {len(run['companies'])}개사 9-factor 채점 (`report_type: ai_scorecard`)
- 요청 원문: {request}
- 산출물: `{paths.rel(paths.run_dir)}/` 묶음(research.md·draft.md·review.md·report.html·audit.md)·`scorecard/history.csv`
- 흐름: plan → collect → research → calculate → draft → review → awaiting_user → build

## 분석 목적과 기준 시점

- 목적: {run['purpose']}
- 분석 기준일 `as_of` {run['as_of']} · 가격 기준일 {run.get('price_as_of') or run['as_of']} · 정보 컷오프 {run.get('info_cutoff') or run['as_of']} (C-17: 셋을 분리 기록)
- 규칙 `{rules.version}` (해시 `{rules.hash[:16]}…`) — 실행 중 규칙이 바뀌어도 이 실행은 이 해시를 유지한다

## 대상 기업과 연결 범위

{table(['company_id', '표시명', '유형', '상장', '평가 범위'], company_rows)}

## 규칙 버전과 자동화 범위

{table(['Factor', '자동화 모드', '범위', '관련 결정'], factor_rows)}

- 정성 판정(등급·경로·분류)은 사람이 입력하고 산식·사다리·구간 적용은 프로그램이 한다(D-03). 모르는 값은 0으로 치환하지 않는다(D-04).

## 기준선

- {baseline_note}
- 승계된 판단은 원검토일과 이번 실행 재검토 여부를 함께 표시한다. 기준선 점수는 새로 검증된 사실이 아니다(D-08).

## 미결 규칙 결정

{table(['ID', '요약', '영향 factor', '이번 실행 선택'], decision_rows) if decision_rows else '- 없음'}

- 미결 결정이 걸린 factor 는 `needs_rule_decision` 으로 남고 해당 기업은 공식 순위에서 제외된다. 실행 단위 선택은 `{paths.rel(paths.run_dir / 'run.json')}` 의 `decisions` 에 근거·결정자와 함께 기록한다.

## 리뷰 기준

- 4개 검토 영역: 사실·출처 / 재무 계산 / 규칙 일관성 / 출력·가독성 (설계 지침 10.1)
- 체크리스트 Q01~Q23 각 항목 pass / fail / not_applicable + 근거
- `uv run --frozen python -X utf8 scripts/validate_report_contract.py {run['run_id']}` 통과

## 완료/차단 조건

완료는 results.json 결정론 검증 통과, draft 와 review pass, 사용자 승인(approval.json) 해시 일치, HTML·history.csv 생성이다.

기업이 순위에 못 들어가는 사유는 factor 상태로 구분한다. 규칙 결정이 없으면 `needs_rule_decision`, 사람의 판정이 없으면 `needs_judgment`, 관측이 없거나 수집·파싱에 실패했으면 `pending_data` 다. 셋 다 0점으로 채우지 않고 공식 순위에서만 제외한다.

`awaiting_user` 는 이 셋과 다르다. 리뷰가 pass 이고 계산이 끝났는데 사용자 승인이 없거나, 승인 뒤 규칙·자료·판단·결과·초안 중 하나가 바뀌어 승인이 무효가 된 상태를 가리키며 build 단계에서만 나온다.
"""
    return fm + "\n" + body.lstrip("\n")


# ------------------------------------------------------------------ research

def _evidence_lines(ctx: Any) -> list[str]:
    """`## 근거 자료` — 기업별 표. relevance 는 사람이 쓴 추론이라 그렇게 표시한다."""
    lines = ["## 근거 자료", ""]
    if ctx.evidence is None:
        return lines + ["- evidence.json 없음 — collect 뒤 선별 전이거나 근거 계층을 쓰지 않는 실행이다", ""]
    if not ctx.evidence:
        return lines + ["- 선별된 근거 0건", ""]
    urls = {s["source_id"]: s.get("url") for s in ctx.sources.get("items", [])}
    for cid in ctx.run["companies"]:
        items = sorted((e for e in ctx.evidence if e["company_id"] == cid), key=lambda e: e["evidence_id"])
        if not items:
            continue
        rows = []
        for e in items:
            url = urls.get(e["source_id"])
            title = f"[{e['title']}]({url})" if url else e["title"]
            relevance = e["relevance"] if e["relevance"].startswith("(추론)") else f"(추론) {e['relevance']}"
            rows.append([e["evidence_id"], ", ".join(FACTOR_LABELS[f] for f in e["factors"]), e["kind"], title,
                         e["published_at_utc"] or "—", e.get("status", "candidate"), relevance])
        lines += [f"### {ctx.companies[cid]['display_name']}", "",
                  table(["근거 ID", "Factor", "종류", "제목", "발행시각(UTC)", "상태", "관련성"], rows), ""]
    lines += ["- `candidate` 근거는 새 판단(`status: new`)이 인용할 수 없다. 사람이 확인해 `confirmed` 로 올린 근거만 인용한다.", ""]
    return lines


TRIGGER_COLUMNS = ["ID", "기업", "Factor", "관찰 사실", "조건", "기한", "근거", "재검토"]
TRIGGER_C14_NOTE = "트리거는 미래 점수를 저장하지 않는다(C-14). 조건이 성립하면 현재 규칙으로 다시 계산한다."


def active_trigger_rows(ctx: Any) -> tuple[list[list[str]], int]:
    """triggers.json 의 감시 중(watching) 트리거 행과 그 밖의 상태 건수. 연구·초안·HTML 이 같은 열을 쓴다."""
    active = sorted((t for t in ctx.triggers if t["status"] == "watching"), key=lambda t: t["trigger_id"])
    rows = [[t["trigger_id"], ctx.companies[t["company_id"]]["display_name"], ", ".join(FACTOR_LABELS[f] for f in t["factors"]),
             t["observation"], t["condition"], t["deadline"], ", ".join(t["evidence_ids"]) or "—", t["recheck"]["what"]]
            for t in active]
    return rows, len(ctx.triggers) - len(active)


def _active_trigger_lines(ctx: Any) -> list[str]:
    rows, others = active_trigger_rows(ctx)
    lines = [table(TRIGGER_COLUMNS, rows) if rows else "- 감시 중인 트리거 없음", ""]
    if others:
        lines += [f"- 그 밖의 상태(fired·expired·withdrawn) {others}건은 triggers.json 에 있다.", ""]
    return lines + [f"- {TRIGGER_C14_NOTE}", ""]


def _trigger_lines(ctx: Any, legacy_triggers: list[dict[str, Any]] | None) -> list[str]:
    """`## 트리거(활성)` — triggers.json 이 있으면 그것을, 없으면 기준선 트리거 서술을 초안과 같은 모양으로 싣는다."""
    lines = ["## 트리거(활성)", ""]
    if ctx.triggers is not None:
        return lines + _active_trigger_lines(ctx)
    if not legacy_triggers:
        return lines + ["- 등록된 트리거 없음", ""]
    reps = rc.replacements(ctx)
    lines += [table(["ID", "항목", "왜 중요한가(v1.5 원문)", "영향(원문)"],
                    [[t["trigger_id"], t["title"], rc.trigger_why(ctx, t, reps), t["impact_raw"]] for t in legacy_triggers]), ""]
    return lines + [f"- {x}" for x in rc.trigger_notes(ctx)] + [""]


TRIGGER_STATUS_KO = {"watching": "계속 관찰", "fired": "발동", "expired": "만료", "withdrawn": "철회"}


def _carry_lines(ctx: Any, previous: list[dict[str, Any]] | None) -> list[str]:
    """2026-10-01 `## 이전 트리거 처리` — 이전 트리거마다 이번 실행의 결론과 확인 내용, 발동한 것이 가리키는 판단."""
    if previous is None:
        return []
    by_ref: dict[str, list[dict[str, Any]]] = {}
    for trg in ctx.triggers:
        if "carry" in trg:
            by_ref.setdefault(trg["carry"]["ref"], []).append(trg)
    rows = []
    for prev in previous:
        for trg in sorted(by_ref.get(prev["ref"], []), key=lambda x: x["trigger_id"]):
            rows.append([prev["ref"], prev["title"], TRIGGER_STATUS_KO[trg["status"]], trg["carry"]["finding"],
                         trg["carry"]["checked_at"], trg["trigger_id"], ctx.companies[trg["company_id"]]["display_name"]])
    lines = ["## 이전 트리거 처리", "", f"- 이전 트리거 {len(previous)}건을 이번 실행에서 확인했다. 한 이전 트리거를 기업별 항목 여럿이 나눠 가리킬 수 있다.", ""]
    lines += [table(["이전 트리거", "항목", "결론", "확인 내용", "확인일", "이번 항목", "기업"], rows) if rows else "- 처리 기록 없음", ""]
    fired = sorted((x for x in ctx.triggers if x["status"] == "fired"), key=lambda x: x["trigger_id"])
    if fired:
        since = ctx.run["created_at"][:10]
        judgments = {(j["company_id"], j["factor"]): j for j in ctx.judgments}
        rows = []
        for trg in fired:
            for factor in trg["recheck"]["factors"]:
                j = judgments.get((trg["company_id"], factor))
                if j is None:
                    state = "판단 없음(자동 산출 factor)"
                elif any(r["revised_at"] >= since for r in j.get("revision_history", [])):
                    state = "이번 실행에서 수정함"
                else:
                    state = "수정하지 않음 — 유지 이유를 리뷰에서 확인"
                rows.append([trg["trigger_id"], ctx.companies[trg["company_id"]]["display_name"], FACTOR_LABELS[factor],
                             trg["recheck"]["what"], state])
        lines += ["### 발동 트리거 재검토 대상", "", table(["트리거", "기업", "Factor", "다시 볼 것", "이번 실행"], rows), ""]
    return lines


def render_research(ctx: Any, *, hashes: dict[str, str], legacy_triggers: list[dict[str, Any]] | None = None,
                    previous_triggers: list[dict[str, Any]] | None = None) -> str:
    run = ctx.run
    paths = run_paths(ctx.slug)
    # 2026-09-30 레인 E: 근거·트리거 해시는 파일이 있을 때만 싣는다(validate.py 도 있을 때만 대조한다).
    optional = [(f"{k}_hash", hashes[k]) for k in ("evidence", "triggers") if k in hashes]
    fm = frontmatter([
        ("slug", ctx.slug), ("report_type", "ai_scorecard"), ("plan_source", paths.rel(paths.plan)), ("run_id", ctx.slug),
        ("as_of", run["as_of"]), ("rule_version", ctx.rules.version), ("observations_hash", hashes["observations"]),
        ("judgments_hash", hashes["judgments"]), *optional, ("created_at", run["created_at"]),
    ])
    lines = [f"# 리서치 — {run['title']}", "", f"실행 `{ctx.slug}` 의 원자료·판단 입력·출처를 정리한다. 관측 {len(ctx.observations)}건, 판단 {len(ctx.judgments)}건.", ""]
    lines += ["## 원자료", ""]
    by_company: dict[str, list[dict[str, Any]]] = {}
    for o in ctx.observations:
        by_company.setdefault(o["company_id"], []).append(o)
    for cid in run["companies"]:
        company = ctx.companies[cid]
        lines += [f"### {company['display_name']}", ""]
        rows = []
        for o in sorted(by_company.get(cid, []), key=lambda x: (x["metric"], x["observation_id"])):
            value = o["value"]
            if isinstance(value, (int, float)) and o["unit"] == "USD":
                shown = fmt_usd(float(value))
            elif isinstance(value, (int, float)) and o["unit"] == "ratio":
                shown = fmt_pct(float(value)) if o["metric"] in ("nonop_share", "operating_margin_ttm") else fmt_num(float(value))
            elif value is None:
                shown = "—"
            else:
                shown = str(value)
            rows.append([o["metric"], shown, o["status"], o["kind"], o["source_id"], (o.get("raw") or "")[:80], (o.get("note") or "")[:80]])
        lines += [table(["지표", "값", "상태", "종류", "출처", "원문", "비고"], rows), ""]
    lines += ["## 판단 입력", ""]
    by_c_j: dict[str, list[dict[str, Any]]] = {}
    for j in ctx.judgments:
        by_c_j.setdefault(j["company_id"], []).append(j)
    for cid in run["companies"]:
        company = ctx.companies[cid]
        rows = []
        for j in sorted(by_c_j.get(cid, []), key=lambda x: x["factor"]):
            inputs = ", ".join(f"{k}={v}" for k, v in j["inputs"].items()) or "—"
            rows.append([FACTOR_LABELS[j["factor"]], j["kind"], fmt_score(j["score"]), inputs, j["status"], f"{j['reviewer']} {j['reviewed_at']}", (j.get("note") or "")[:80]])
        lines += [f"### {company['display_name']}", "", table(["Factor", "종류", "점수", "입력", "상태", "검토", "비고"], rows), ""]
    lines += _evidence_lines(ctx)
    lines += _trigger_lines(ctx, legacy_triggers)
    lines += _carry_lines(ctx, previous_triggers)
    lines += ["## 출처", ""]
    src_rows = [[s.get("source_id"), s.get("title"), s.get("publisher") or "—", s.get("url") or "(URL 없음 — 만들지 않음)", s.get("accessed_at") or "—", s.get("conflict_of_interest") or "—"] for s in ctx.sources.get("items", [])]
    lines += [table(["ID", "제목", "발행", "URL", "접근일", "이해상충"], src_rows) if src_rows else "- 등록된 출처 없음", ""]
    lines += ["## 미결 항목", ""]
    pending_rows = []
    for o in ctx.observations:
        if o["status"] not in ("verified", "legacy_unverified"):
            pending_rows.append([o["company_id"], o["metric"], o["status"], (o.get("note") or o.get("raw") or "")[:100]])
    for j in ctx.judgments:
        unknowns = [k for k, v in j["inputs"].items() if v == "unknown"]
        if unknowns:
            pending_rows.append([j["company_id"], FACTOR_LABELS[j["factor"]], "unknown 입력", ", ".join(unknowns)])
    legacy = sum(1 for o in ctx.observations if o["status"] == "legacy_unverified")
    lines += [table(["기업", "항목", "상태", "내용"], pending_rows) if pending_rows else "- 없음", "",
              f"- legacy_unverified 관측 {legacy}건은 기준선 열람용이며 이번 실행에서 재검증되지 않았다.",
              f"- 미결 규칙 결정: {', '.join(d['id'] for d in ctx.rules.pending_decisions() if d.get('blocking')) or '없음'} (실행 선택: {', '.join(d['id'] + '=' + d['choice'] for d in run['decisions']) or '없음'})", ""]
    return fm + "\n" + "\n".join(lines)


# ------------------------------------------------------------------ draft

def _factor_row(f: str, fr: dict[str, Any]) -> list[Any]:
    # 2026-09-15 FIX-54 1단계 S3: 산식 텍스트를 HTML 과 같은 함수로. v1.7 parameters(P1~P4)가 초안에서도 비어 있었다.
    return [FACTOR_LABELS[f], fmt_score(fr["score"]), STATUS_LABEL.get(fr["status"], fr["status"]), rc.BASIS_LABELS.get(fr["basis"], fr["basis"]),
            rc.rename_codes(rc.factor_calc_text(f, fr))]


def render_draft(ctx: Any, results: dict[str, Any], baseline: dict[str, Any] | None, triggers: list[dict[str, Any]]) -> str:
    run = ctx.run
    title = run["title"]
    ranking = results["ranking"]
    population = results["population"]
    companies_by_id = {c["company_id"]: c for c in results["companies"]}
    paths = run_paths(ctx.slug)
    fm = frontmatter([
        ("slug", ctx.slug), ("report_type", "ai_scorecard"), ("title", title),
        ("subtitle", f"규칙 {ctx.rules.version} · 기준일 {run['as_of']} · {population['scored']}개사 순위"),
        ("run_id", ctx.slug), ("as_of", run["as_of"]), ("price_as_of", run.get("price_as_of") or run["as_of"]), ("info_cutoff", run.get("info_cutoff") or run["as_of"]),
        ("rule_version", ctx.rules.version), ("rule_hash", ctx.rules.hash),
        ("baseline_id", run["baseline_id"]), ("plan_source", paths.rel(paths.plan)), ("research_source", paths.rel(paths.research)),
        ("results_hash", results["results_hash"]), ("level", "intermediate"), ("duration_minutes", 15), ("created_at", run["created_at"]),
    ])
    conflicts = sorted({src["conflict_of_interest"] for src in ctx.sources.get("items", []) if src.get("conflict_of_interest")})
    lines = [f"# {title}", ""]
    # 개요
    lines += ["## 개요", ""]
    if ranking:
        top = [r for r in ranking if r["rank"] == 1]
        top_names = " · ".join(r["display_name"] for r in top)
        moat_pool = [c for c in results["companies"] if not c["reference"] and c["moat"] is not None]
        max_moat = max(c["moat"] for c in moat_pool)
        moat_top = " · ".join(c["display_name"] + ("" if c["complete"] else "(미완료)") for c in moat_pool if c["moat"] == max_moat)
        # 2026-10-01 출력·가독성 리뷰(high): 동점 가운데 첫 기업만 적었다. 같은 함정 점수의 기업을 모두 적는다.
        worst_trap = min(r["trap"] for r in ranking)
        worst_all = [r for r in ranking if r["trap"] == worst_trap]
        candidates = [c["display_name"] + ("" if c["complete"] else "(미완료)") for c in moat_pool if c["moat"] >= 20]
        lines += [
            f"- 조정총점 1위: {top_names} ({top[0]['total']}점){' — 공동' if len(top) > 1 else ''}",
            f"- 과점 factor 최고: {moat_top} ({max_moat}점) — 과점이 완결된 전 기업 기준",
            f"- 함정 최심(완료 {population['scored']}개사 기준): {worst_trap}점 — "
            + " · ".join(f"{r['display_name']}(조정 {r['total']}점)" for r in worst_all) + (" — 공동" if len(worst_all) > 1 else ""),
            f"- 과점 후보군(과점 20점 이상): {', '.join(candidates) if candidates else '없음'}",
        ]
    lines += [f"- 모집단: 완료 {population['scored']}개사 순위 / 미완료 {len(population['incomplete'])}개사 제외 (미완료는 0점으로 채우지 않는다)."]   # 2026-10-06: 기준선 순위 비교 안내를 싣지 않는다
    lines += [f"- 기준 시점: 분석 기준일 {run['as_of']} · 가격 기준일 {run.get('price_as_of') or run['as_of']} · 정보 컷오프 {run.get('info_cutoff') or run['as_of']} (C-17). 승계 근거·트리거 일부는 원문에 컷오프 이후 사건이 그대로 있으며 이번 실행에서 재검증하지 않았다."]
    if conflicts:
        # 2026-09-16 FIX-57 2단계(6차 리뷰 A 분담): 출처별 문구 다섯을 ` / ` 로 이어 붙여 **실행 차원 고지가 맨 끝에 묻혔다.**
        # 읽는 사람이 먼저 알아야 하는 것은 채점자와 채점 대상이 같은 곳이라는 사실이다. 출처별 문구는 References 에 그대로 있다.
        flagged = len([s for s in ctx.sources.get("items", []) if s.get("conflict_of_interest")])
        private_count = sum(1 for company in results["companies"] if not company["listed"])
        lines += [f"- **이해상충 고지 — 채점 대상에 Anthropic 이 포함되고, 이 채점표를 Anthropic 이 만든 Claude 가 작성했다**"
                  f"(채점 규칙 머리말 · 긴장 #4·#11). 투자 판단에 사용할 경우 감안할 것. "
                  f"비상장 {private_count}사의 수치는 이해당사자 1차 발표에서 온다. 이해상충이 표기된 출처 {flagged}건의 개별 문구는 "
                  f"References 의 각 출처 줄에 있고, 제3자 재검토 약속은 감사 기록(audit.md)에 있다."]
    if results["pending_rule_decisions"]:
        lines.append(f"- 미결 규칙 결정: {', '.join(results['pending_rule_decisions'])} — 사용자 결정 전에는 해당 기업을 순위에 넣지 않는다")
    lines += ["", "과점 = ①~⑤ 합, 함정 = ⑥~⑨ 합(음수 또는 0), 조정총점 = 과점 + 함정. 순위는 1 + (조정총점이 더 높은 완료 기업 수)이며 동점은 공동 순위다.", ""]
    # 순위표
    lines += ["## 종합 순위표", ""]
    rows = []
    for r in ranking:
        c = companies_by_id[r["company_id"]]
        f = c["factors"]
        rows.append([r["rank"], r["display_name"]] + [fmt_score(f[x]["score"]) for x in MOAT_FACTORS] + [r["moat"]] + [fmt_score(f[x]["score"]) for x in TRAP_FACTORS] + [r["trap"], f"**{r['total']}**"])
    lines += [table(["순위", "기업", "①", "②", "③", "④", "⑤", "과점", "⑥", "⑦", "⑧", "⑨", "함정", "조정총점"], rows,
                    ["---:", "---"] + ["---:"] * 12), ""]
    if population["incomplete"]:
        inc_rows = [[i["display_name"], fmt_score(i["moat"]), fmt_score(i["trap"]), "; ".join(f"{FACTOR_LABELS[p['factor']]} {STATUS_LABEL.get(p['status'], p['status'])}" + (f"({p['decision_id']})" if p.get("decision_id") else "") for p in i["reasons"])] for i in population["incomplete"]]
        lines += ["미완료(순위 제외):", "", table(["기업", "과점(부분)", "함정(부분)", "대기 사유"], inc_rows), ""]
    # 기업별 상세
    lines += ["## 기업별 상세", ""]
    ordered = sorted(results["companies"], key=lambda c: (c["rank"] is None, c["rank"] or 0, -(c["moat"] or 0), c["company_id"]))
    baseline_scores = {b["company_id"]: b for b in (baseline or {}).get("companies", [])}
    # 2026-09-15 FIX-54 1단계 S4: (회사, factor) 쌍으로 찾아 자동 산출 F6(anthropic·openai)에 승계 판단 문구가 찍혔다.
    judgments_by_id = {j["judgment_id"]: j for j in ctx.judgments}
    reps = rc.replacements(ctx)
    lines += [f"- {rc.card_evidence_note(run['baseline_id'], three_way=rc.has_three_way(ctx))}", ""]
    for c in ordered:
        b = baseline_scores.get(c["company_id"])
        # 2026-10-06 사용자 지시: 기준선 순위·기준선 요약을 싣지 않는다. 요약은 이 실행에서 확정한 기업 요약뿐이다.
        head = f"{c['rank']}위(완료 {population['scored']}개사 기준)" if c["rank"] else "미완료"
        lines += [f"### {c['display_name']} — {head} · 조정 {fmt_score(c['total'])} (과점 {fmt_score(c['moat'])} / 함정 {fmt_score(c['trap'])})", ""]
        summary = ((getattr(ctx, "company_summaries", None) or {}).get(c["company_id"]) or {}).get("text")
        if summary:
            lines += [f"> {summary}", ""]
        lines += [table(["Factor", "점수", "상태", "근거 종류", "산식·경로"], [_factor_row(f, c["factors"][f]) for f in FACTOR_IDS]), ""]
        incompatible_g4 = rc.g4_incompatible(ctx.observations, c["company_id"])
        for f in FACTOR_IDS:
            fr = c["factors"][f]
            base_evidence = (b or {}).get("evidence", {}).get(f, []) if b else []
            block = rc.evidence_block(fr, judgments_by_id, base_evidence, run["baseline_id"], c["company_id"], reps,
                                      run_created=run.get("created_at"))
            if block is not None:
                lines.append(f"- **{FACTOR_LABELS[f]}** {block['header']}:")
                # 2026-09-17 FIX-67: 근거 문장에 번호가 데이터로 들어 있다. 초안도 HTML 과 같은 이름을 쓴다.
                if block.get("three_way"):
                    # 2026-10-07 사용자 지시: 세 칸 판단은 판정·올릴 근거·내릴 근거를 소제목으로 나눈다. 빈 칸은 '없음'.
                    for label, rows in (("판정", block["lines"]),
                                        *((lab, block.get(key) or []) for key, lab in rc.EVIDENCE_DIRECTION_LABELS)):
                        lines.append(f"  - {label}")
                        lines += [f"    - {rc.rename_codes(text)}" for _depth, text in rows] or ["    - 없음"]
                else:
                    lines += [("  " * depth) + f"- {rc.rename_codes(text)}" for depth, text in block["lines"]]
                if f == "F9" and incompatible_g4:
                    lines.append(f"  - {rc.G4_INCOMPATIBLE_NOTE}")
            # 2026-09-17 FIX-77: 초안도 카드와 같은 규칙을 쓴다. 승계 표기는 근거 머리줄이 이미 말하고,
            # `⚠️` 는 글자로 밝히며, 작업 메모는 본문에서 내린다(감사 기록에 남는다).
            # 2026-09-18 FIX-79 S1: HTML 카드와 같은 문장이다 — 한쪽만 고치면 둘이 갈린다.
            notes = rc.factor_notes(ctx, f, fr)      # 사유가 앞에 오도록 factor_notes 가 정렬해 준다
            if notes and block is None:
                # 2026-10-07 출력 리뷰: 근거 블록이 없는 항목(관측에서 계산한 ⑥ 등)의 사유가 앞 항목 아래에 붙었다.
                lines.append(f"- **{FACTOR_LABELS[f]}**:")
            for n in notes:
                lines.append(f"  - {rc.NOTE_KINDS[n['kind']]} — {n['text']}")
        lines.append("")
    # 원자료
    lines += ["## 지표 원자료", ""]
    lines += _raw_tables(ctx, results)
    # 방법
    lines += ["## 방법과 규칙", ""]
    lines += [
        f"- 규칙 파일 `scorecard/rules/{ctx.rules.version}.json` 해시 `{ctx.rules.hash}` · 원문 규칙 `{ctx.rules.payload['source']['file']}` 은 sha256 `{ctx.rules.payload['source']['sha256'][:12]}…`(SRC-v15-rule)",
        f"- 입력 해시: observations `{ctx.hashes['observations'][:16]}…`, judgments `{ctx.hashes['judgments'][:16]}…`, results `{results['results_hash'][:16]}…`",
        f"- 실행 단위 결정: {', '.join(results['decisions_applied']) or '없음'}",
        f"- 미결 결정: {', '.join(results['pending_rule_decisions']) or '없음'}",
        # 2026-09-15 FIX-54 2단계: 'undrawn_credit 관측이 있어 선택에 따라 런웨이가 달라질 수 있다' 는 실제 동작과 달랐다(RC3-06).
        f"- {rc.c04_line(ctx)}",
        "",
        table(["Factor", "자동화", "범위"], [[FACTOR_LABELS[f], ctx.rules.factor(f)["mode"], f"{ctx.rules.factor(f)['range'][0]}~{ctx.rules.factor(f)['range'][1]}"] for f in FACTOR_IDS]),
        "",
        # 2026-09-15 FIX-52: v1.5 문구(NTM PER 구간표 · 하한 -5)가 박혀 있었다. FIX-54 에서 HTML 과 같은 목록(render_common)으로 옮겼다.
    ]
    lines += [f"- {x}" for x in rc.method_lines(ctx, results)] + [""]
    # 한계 — 2026-09-15 FIX-54 1단계 S4
    lines += ["## 알려진 한계", ""] + [x if x.startswith("  - ") else f"- {x}" for x in rc.limitations(ctx)] + [""]
    # 트리거 — 2026-09-30 레인 F: triggers.json 이 있으면 연구 단계와 같은 열로 그것을 그린다. 없으면 기준선 트리거(기존 두 실행).
    lines += ["## 트리거", ""]
    if ctx.triggers is not None:
        lines += _active_trigger_lines(ctx)
    elif triggers:
        reps = rc.replacements(ctx)
        lines += [table(["ID", "항목", "왜 중요한가(v1.5 원문)", "영향(원문)"],
                        [[t["trigger_id"], t["title"], rc.trigger_why(ctx, t, reps), t["impact_raw"]] for t in triggers]), ""]
        lines += [f"- {x}" for x in rc.trigger_notes(ctx)] + [""]
    else:
        lines += ["- 등록된 트리거 없음", ""]
    # 2026-10-01 출력·가독성 리뷰(medium): 초안이 근거 ID 를 인용하지만 찾아갈 곳이 없었다. 본문이 인용한 근거를 표로 붙인다.
    import re as _re

    cited = sorted(set(_re.findall(r"EV-[a-z0-9-]+-\d{3}", "\n".join(lines))))
    if ctx.evidence and cited:
        ev_by_id = {e["evidence_id"]: e for e in ctx.evidence}
        urls = {s["source_id"]: s.get("url") for s in ctx.sources.get("items", [])}
        rows = []
        for eid in cited:
            e = ev_by_id.get(eid)
            if e is None:
                rows.append([eid, "—", "evidence.json 에 없음", "—", "—"])
                continue
            url = urls.get(e["source_id"])
            title = f"[{e['title']}]({url})" if url else e["title"]
            rows.append([eid, ctx.companies[e["company_id"]]["display_name"], title, (e["published_at_utc"] or "—")[:10],
                         {"confirmed": "확정", "candidate": "후보"}.get(e.get("status", "candidate"), e.get("status", "candidate"))])
        lines += ["## 인용 근거", "", f"본문이 인용한 근거 {len(cited)}건. 전체 목록과 선별 이유는 `research.md` 의 근거 자료 절에 있다.", "",
                  table(["근거 ID", "기업", "제목(원문)", "발행일", "상태"], rows), ""]
    # References
    lines += ["## References", ""]
    for src in ctx.sources.get("items", []):
        url = src.get("url") or "URL 미제공"
        coi = f" · 이해상충: {src['conflict_of_interest']}" if src.get("conflict_of_interest") else ""
        sha = f" · sha256 {src['sha256'][:12]}…" if src.get("sha256") else ""
        lines.append(f"- {src.get('source_id')} — {src.get('title')} · {src.get('publisher') or ''} · {src.get('accessed_at') or ''} · {url}{sha}{coi}")
    lines += ["", f"_{DISCLAIMER}_", ""]
    return fm + "\n" + "\n".join(lines)


def _raw_if_missing(obs: Any, cid: str, metric: str) -> str | None:
    o = obs.get(cid, metric)
    if o is None:
        return None
    return (o.get("raw") or o["status"]) if o.get("value") is None else None


def _usd_or_raw(obs: Any, cid: str, metric: str) -> str:
    value = obs.number(cid, metric)[0]
    return fmt_usd(value) if value is not None else (_raw_if_missing(obs, cid, metric) or "—")


def _num_or_raw(obs: Any, cid: str, metric: str) -> str:
    value = obs.number(cid, metric)[0]
    return fmt_num(value) if value is not None else (_raw_if_missing(obs, cid, metric) or "—")


def _pct_or_raw(obs: Any, cid: str, metric: str) -> str:
    value = obs.number(cid, metric)[0]
    return fmt_pct(value) if value is not None else (_raw_if_missing(obs, cid, metric) or "—")


def _runway_text(c: dict[str, Any], obs: Any) -> str:
    """G3 계산값 우선, 없으면 관측값. 값이 없으면 원문 상태(∞·판정 불가)를 그대로 보여준다."""
    value = _runway(c, obs)
    return fmt_num(value) if value is not None else (_raw_if_missing(obs, c["company_id"], "runway_years") or "—")


def _runway(c: dict[str, Any], obs: Any) -> float | None:
    for p in (c["factors"]["F9"].get("calc") or {}).get("path", []):
        if p.get("gate") == "G3" and p.get("runway_years") is not None:
            return float(p["runway_years"])
    return obs.number(c["company_id"], "runway_years")[0]


def _raw_tables(ctx: Any, results: dict[str, Any]) -> list[str]:
    from .inputs import ObsLookup

    obs = ObsLookup(ctx.observations)
    lines: list[str] = []
    val_rows, fin_rows, borr_rows, priv_rows = [], [], [], []
    for c in results["companies"]:
        cid = c["company_id"]
        name = c["display_name"]
        if c["listed"]:
            per, per_obs = obs.number(cid, "ntm_per")
            method = ((per_obs or {}).get("basis") or {}).get("method", "")
            f6 = c["factors"]["F6"]
            if f6["status"] == "needs_rule_decision":
                flag = f"보류({(f6.get('pending') or {}).get('decision_id', '')})"
            else:
                flag = "⚠️" if rc.f6_boundary_flag(f6.get("calc") or {}) else "—"
            val_rows.append([name, fmt_usd(obs.number(cid, "price")[0], 2), fmt_usd(obs.number(cid, "market_cap")[0], 2) + rc.vendor_mark(obs, cid, "market_cap"),
                             fmt_num(per) + rc.vendor_mark(obs, cid, "ntm_per"), method or "—", fmt_score(f6["score"]), flag, _num_or_raw(obs, cid, "ttm_per"),
                             _pct_or_raw(obs, cid, "nonop_share"), fmt_num(obs.number(cid, "ps_ratio")[0])])
        else:
            calc = c["factors"]["F6"].get("calc") or {}
            v_arr, arr_raised = rc.private_multiples(calc)
            priv_rows.append([name, fmt_usd(obs.number(cid, "post_money_valuation")[0]), fmt_usd(obs.number(cid, "arr")[0]), fmt_num(v_arr), fmt_usd(obs.number(cid, "cumulative_raised")[0]), fmt_num(arr_raised, 2), fmt_score(c["factors"]["F6"]["score"])])
        fcf, fcf_obs = obs.number(cid, "fcf_ttm")
        rating = obs.get(cid, "credit_rating")
        fin_rows.append([name, _usd_or_raw(obs, cid, "cash"), fmt_usd(fcf) if fcf is not None else ((fcf_obs or {}).get("raw") or "—"), _runway_text(c, obs),
                         fmt_usd(obs.number(cid, "net_cash")[0]) + rc.vendor_mark(obs, cid, "net_cash"), fmt_num(obs.number(cid, "debt_ebitda")[0], 2),
                         (rating or {}).get("value") or "—", rc.offbalance_cell(obs, cid), fmt_score(c["factors"]["F9"]["score"])])
        nb, nb_obs = obs.number(cid, "net_borrowing_ttm")
        if nb_obs is not None:
            borr_rows.append([name, fmt_usd(nb) if nb is not None else (nb_obs.get("raw") or "—"), fmt_usd(obs.number(cid, "capex_ttm")[0])])
    cids = [c["company_id"] for c in results["companies"]]
    listed = [c["company_id"] for c in results["companies"] if c["listed"]]
    lines += [rc.raw_caption(ctx), ""]
    lines += ["### 가격 — ⑥ 원자료", "", table(["기업", "주가", "시총", "NTM PER", "산출 방법", "⑥", "경계", "TTM PER", "영업외 비중", "P/S"], val_rows), "",
              "- 열별 관측 상태: " + rc.status_summary(obs, listed, rc.PRICE_STATUS_COLUMNS),
              f"- {rc.price_notice(ctx)}"]
    vendor = rc.vendor_policy_note(ctx)
    lines += ([f"- {vendor}"] if vendor else []) + [""]
    if priv_rows:
        lines += ["### 비상장 — ⑥ 배수", "", table(["기업", "post-money", "ARR", "밸류÷ARR", "누적 조달", "ARR÷조달", "⑥"], priv_rows), "", f"- {rc.private_notice(ctx)}", ""]
    lines += ["### 재무 — ⑨ 원자료", "", table(["기업", "현금", "TTM FCF", "런웨이(년)", "순현금/순부채", "D/EBITDA", "신용", rc.OFFBALANCE_HEADER, "⑨"], fin_rows), "",
              "- 열별 관측 상태: " + rc.status_summary(obs, cids, rc.FIN_STATUS_COLUMNS),
              f"- {rc.cash_definition_note(ctx)}"]
    lines += [f"- {x}" for x in rc.credit_lines(ctx, results)]
    lines += [f"- {rc.CREDIT_NOTE}", ""]
    if borr_rows:
        lines += ["### TTM 순차입", "", table(["기업", "TTM 순차입", "TTM capex"], borr_rows), ""]
    return lines


# ------------------------------------------------------------------ review template

def render_review_template(ctx: Any, results: dict[str, Any], *, draft_hash: str) -> str:
    paths = run_paths(ctx.slug)
    fm = frontmatter([
        ("slug", ctx.slug), ("report_type", "ai_scorecard"), ("status", "needs_fix"), ("created_at", ctx.run["created_at"]),
        ("plan_source", paths.rel(paths.plan)), ("research_source", paths.rel(paths.research)), ("draft_source", paths.rel(paths.draft)),
        ("results_hash", results["results_hash"]), ("draft_hash", draft_hash),
        ("review_type", "separate-session-4way"), ("review_execution", "separate_subagent_sessions"),
        ("reviewers", [f"{key}: pending" for key, _, _ in REVIEW_AREAS]),
    ])
    lines = [f"# 리뷰 — {ctx.run['title']}", "",
             "각 영역은 가능하면 독립 세션에서 검토하고 실제 수행자·결과를 남긴다. 수행하지 않은 검토를 pass 로 표시하지 않는다.", "",
             "## 검토 영역", "",
             table(["영역", "검토 대상", "검토자", "결과", "요약"], [[label, scope, "", "pending", ""] for _, label, scope in REVIEW_AREAS]), "",
             "결과는 pass / needs_fix / blocked 중 하나. 네 영역이 모두 pass 이고 체크리스트에 fail 이 없을 때만 frontmatter `status: pass`.",
             "**승계 판단 예외(AGENTS.md 리뷰 범위)** — 체크리스트 fail 의 사유가 `carried_score` 로 승계한 판단의 기존 논리이고, 이번 실행이 그 판단에 쓰인 잣대를 바꾸지 않았으며, 규칙 파일 `open_tensions` 에 재검토 시점과 함께 등록됐다면 `status: pass` 를 막지 않는다. 이때 해당 fail 과 **긴장 번호**(예: `TEN-RC-02`)를 근거 칸에 그대로 적는다. 이번 실행이 바꾼 잣대가 닿는 승계 판단은 이 예외가 아니다 — 한 회사에 새 잣대를 댔으면 같은 잣대가 닿는 모든 회사에 대야 한다(Q03).", "",
             "## 체크리스트", "",
             table(["ID", "검사 초점", "결과", "근거"], [[q["id"], q["focus"], "pending", ""] for q in ctx.rules.checklist()]), "",
             "결과는 pass / fail / not_applicable. not_applicable 도 근거가 필요하다.", "",
             "## 발견 사항", "", "- (파일·섹션 단위로 기록)", "",
             "## 판정", "", f"- results_hash `{results['results_hash'][:16]}…` · draft_hash `{draft_hash[:16]}…` 기준 검토. 자료·규칙·판단·초안이 바뀌면 이 리뷰는 무효다(D-10).",
             # 2026-09-16 FIX-57 1단계(6차 리뷰 A): 리뷰어가 results_hash 를 파일 바이트 해시로 알고 대조하다 어긋났다.
             "- **두 해시의 뜻이 다르다.** `results_hash` 는 `results.json` 에서 `results_hash` 키를 뺀 내용의 정렬 JSON 해시이고(`engine.sha256_obj`) "
             "**파일 바이트 sha256 과 다르다.** `draft_hash` 는 초안 **파일 바이트 sha256** 이다. 대조할 때 섞지 않는다.", ""]
    return fm + "\n" + "\n".join(lines)


# ------------------------------------------------------------------ preview

def render_preview(ctx: Any, results: dict[str, Any], baseline: dict[str, Any] | None) -> str:
    lines = [f"# 변경 미리보기 — {ctx.slug}", "", f"기준선 `{ctx.run['baseline_id']}` 대비 이번 계산 결과. 승인 전 검토용이며 이력을 바꾸지 않는다.", ""]
    base = {b["company_id"]: b for b in (baseline or {}).get("companies", [])}
    rows = []
    for c in sorted(results["companies"], key=lambda x: (x["rank"] is None, x["rank"] or 0, x["company_id"])):
        b = base.get(c["company_id"])
        changed = []
        for f in FACTOR_IDS:
            new = c["factors"][f]["score"]
            old = (b or {}).get("scores", {}).get(f)
            if b and new is not None and old is not None and new != old:
                changed.append(f"{FACTOR_LABELS[f]} {old}→{new}")
            elif new is None:
                changed.append(f"{FACTOR_LABELS[f]} 대기")
        rows.append([c["display_name"], f"{fmt_score((b or {}).get('total'))} / {fmt_score((b or {}).get('rank_raw'))}", f"{fmt_score(c['total'])} / {fmt_score(c['rank'])}",
                     "; ".join(changed) or "변경 없음", ", ".join(FACTOR_LABELS[f] for f in c["carried_factors"]) or "—"])
    lines += [table(["기업", "기준선 조정/순위", "이번 조정/순위", "변경·대기 factor", "승계 점수"], rows), ""]
    if results["pending_rule_decisions"]:
        lines += ["## 필요한 규칙 결정", ""]
        for did in results["pending_rule_decisions"]:
            spec = ctx.rules.decision(did) or {}
            affected = sorted({c["display_name"] for c in results["companies"] for p in c["pending"] if p.get("decision_id") == did})
            lines.append(f"- **{did}** {spec.get('summary', '')} — 선택지: {', '.join(spec.get('choices', [])) or '(기술)'} — 영향: {', '.join(affected)}")
        lines += ["", f"선택은 `{run_paths(ctx.slug).rel(run_paths(ctx.slug).run_dir / 'run.json')}` 의 `decisions` 에 `{{id, choice, rationale, decided_by, decided_at}}` 로 기록한 뒤 다시 `calculate` 한다.", ""]
    # 2026-10-01 출력·가독성 리뷰(medium): 변동 원인을 '규칙 이관' 으로 고정했고 이전 실행과 비교하지 않았다.
    # 이전 실행을 이어받은 실행은 이전 실행 대비 바뀐 factor 와 원인을 따로 보인다.
    prior = (ctx.run.get("continued_from") or {}).get("run_id")
    causes: dict[str, int] = {}
    if prior:
        from .engine import load_results

        try:
            prev = {c["company_id"]: c for c in load_results(prior)["companies"]}
        except Exception:  # noqa: BLE001 — 이전 실행 결과가 없으면 이 표만 뺀다
            prev = {}
        if prev:
            created = ctx.run.get("created_at") or ""
            # 2026-10-06 출력·가독성 리뷰(medium): 근거 문장만 바꾼 수정(PRP-003)도 '판단 수정' 으로 분류했다.
            # 이번 실행 중 수정 가운데 판정 재료(inputs·score)를 실제로 바꾼 것만 판단 수정으로 본다.
            revised = {(j["company_id"], j["factor"]) for j in ctx.judgments
                       if any(str(h.get("revised_at") or "") >= created
                              and ((h.get("previous") or {}).get("inputs") != j.get("inputs")
                                   or (h.get("previous") or {}).get("score") != j.get("score"))
                              for h in (j.get("revision_history") or []))}
            prow = []
            for c in sorted(results["companies"], key=lambda x: (x["rank"] is None, x["rank"] or 0, x["company_id"])):
                p = prev.get(c["company_id"])
                if p is None:
                    continue
                diffs = []
                for f in FACTOR_IDS:
                    new, old = c["factors"][f]["score"], p["factors"][f]["score"]
                    if new == old:
                        continue
                    # 2026-10-06: 규칙 v1.9 처럼 ⑥ 트랙이 바뀌면 관측 변화와 함께 규칙 변경도 원인이다.
                    old_track = (p["factors"][f].get("calc") or {}).get("track")
                    new_track = (c["factors"][f].get("calc") or {}).get("track")
                    if (c["company_id"], f) in revised:
                        cause = "✍️ 판단 수정"
                    elif f == "F6" and old_track and new_track and old_track != new_track:
                        cause = f"📐 규칙(트랙 {old_track}→{new_track})·📊 관측"
                    elif f in ("F6", "F9"):
                        cause = "📊 관측(가격·재무)"
                    else:
                        cause = "📐 규칙"
                    causes[cause] = causes.get(cause, 0) + 1
                    diffs.append(f"{FACTOR_LABELS[f]} {fmt_score(old)}→{fmt_score(new)} ({cause})")
                if diffs or p.get("total") != c["total"] or p.get("rank") != c["rank"]:
                    prow.append([c["display_name"], f"{fmt_score(p.get('total'))} / {fmt_score(p.get('rank'))}",
                                 f"{fmt_score(c['total'])} / {fmt_score(c['rank'])}", "; ".join(diffs) or "factor 같음(순위만 이동)"])
            lines += [f"## 이전 실행 `{prior}` 대비", "",
                      table(["기업", "이전 조정/순위", "이번 조정/순위", "바뀐 factor (원인)"], prow) if prow else "- 바뀐 점수 없음", ""]
    if causes:
        summary = " · ".join(f"{k} {v}건" for k, v in sorted(causes.items()))
        lines += ["## 변동 원인 분류", "", f"- 이전 실행 대비 바뀐 factor 의 원인: {summary}. 원인은 판단 수정 이력·자동 산출 factor 로 추정한 분류다.", ""]
    else:
        lines += ["## 변동 원인 분류", "", "- 기준선 이관 재계산이라 변동 원인은 📐규칙(미결 결정·엄격 계약)이며 기업 실적 변화가 아니다. 규칙 버전이 같은 실행끼리만 추세로 연결한다.", ""]
    return "\n".join(lines)
