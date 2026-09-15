# 실행 원본(run·observations·judgments·results)에서 plan/research/draft/review 템플릿/preview Markdown 을 생성하는 렌더러
from __future__ import annotations

import re
from typing import Any

from report_contract_lib import rel

from .schema import FACTOR_IDS, MOAT_FACTORS, TRAP_FACTORS

FACTOR_LABELS = {
    "F1": "① 네트워크", "F2": "② 게임체인저", "F3": "③ Last Mover", "F4": "④ 호황 이후", "F5": "⑤ 아군",
    "F6": "⑥ 가격", "F7": "⑦ 순환금융", "F8": "⑧ 비대칭 의존", "F9": "⑨ 적자 깊이",
}
STATUS_LABEL = {
    "ok": "산출", "carried_score": "승계", "needs_judgment": "판단 대기", "needs_rule_decision": "규칙 결정 대기",
    "pending_data": "자료 대기", "error": "오류",
}
REVIEW_AREAS = [
    ("fact-sources", "사실·출처", "숫자·기업 귀속·기준 시점·공시·뉴스·부재 주장·이해상충"),
    ("financial-calc", "재무 계산", "EPS·환율·ADR·TTM·FCF·런웨이·약정·단위·부호"),
    ("rule-consistency", "규칙 일관성", "factor 정의·상하한·예외·중복 속성·정성 승계·전 기업 동일 기준"),
    ("output-readability", "출력·가독성", "표·카드·근거·차트·이력 일치, 낡은 비교 문장, 모바일·단일 HTML"),
]
DISCLAIMER = (
    "이 채점표는 교육 및 정보 제공 목적의 정성 분석입니다. 특정 종목의 매수·매도를 권유하지 않으며 투자 자문이 아닙니다. "
    "점수는 규칙과 입력에서 계산된 결과이며 수익률 예측이나 검증된 승리 확률이 아닙니다."
)


# ------------------------------------------------------------------ 포맷

def fmt_usd(value: float | None, digits: int = 1) -> str:
    if value is None:
        return "—"
    sign = "-" if value < 0 else ""
    v = abs(value)
    if v >= 1e12:
        return f"{sign}${v / 1e12:.{max(digits, 2)}f}T"
    if v >= 1e9:
        return f"{sign}${v / 1e9:.{digits}f}B"
    if v >= 1e6:
        return f"{sign}${v / 1e6:.0f}M"
    return f"{sign}${v:,.2f}"


def fmt_num(value: float | None, digits: int = 1) -> str:
    if value is None:
        return "—"
    return f"{value:.{digits}f}"


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
- 산출물: `research/`·`drafts/`·`reviews/`·`output/{run['run_id']}.html`·`scorecard/history.csv`
- 흐름: plan → research → calculate → draft → review → awaiting_user → build

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

- 미결 결정이 걸린 factor 는 `needs_rule_decision` 으로 남고 해당 기업은 공식 순위에서 제외된다. 실행 단위 선택은 `scorecard/runs/{run['run_id']}/run.json` 의 `decisions` 에 근거·결정자와 함께 기록한다.

## 리뷰 기준

- 4개 검토 영역: 사실·출처 / 재무 계산 / 규칙 일관성 / 출력·가독성 (설계 지침 10.1)
- 체크리스트 Q01~Q23 각 항목 pass / fail / not_applicable + 근거
- `python scripts/validate_report_contract.py {run['run_id']}` 통과

## 완료/차단 조건

완료는 results.json 결정론 검증 통과, draft 와 review pass, 사용자 승인(approval.json) 해시 일치, HTML·history.csv 생성이다.

기업이 순위에 못 들어가는 사유는 factor 상태로 구분한다. 규칙 결정이 없으면 `needs_rule_decision`, 사람의 판정이 없으면 `needs_judgment`, 관측이 없거나 수집·파싱에 실패했으면 `pending_data` 다. 셋 다 0점으로 채우지 않고 공식 순위에서만 제외한다.

`awaiting_user` 는 이 셋과 다르다. 리뷰가 pass 이고 계산이 끝났는데 사용자 승인이 없거나, 승인 뒤 규칙·자료·판단·결과·초안 중 하나가 바뀌어 승인이 무효가 된 상태를 가리키며 build 단계에서만 나온다.
"""
    return fm + "\n" + body.lstrip("\n")


# ------------------------------------------------------------------ research

def render_research(ctx: Any, *, hashes: dict[str, str]) -> str:
    run = ctx.run
    fm = frontmatter([
        ("slug", ctx.slug), ("report_type", "ai_scorecard"), ("plan_source", f"plan/{ctx.slug}.md"), ("run_id", ctx.slug),
        ("as_of", run["as_of"]), ("rule_version", ctx.rules.version), ("observations_hash", hashes["observations"]),
        ("judgments_hash", hashes["judgments"]), ("created_at", run["created_at"]),
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

def _f9_gate_text(p: dict[str, Any]) -> str:
    text = f"{p['gate']}:{p.get('result') or p.get('adjust') or p.get('mode') or ''}"
    # 2026-09-15 FIX-53 2단계: G3 런웨이와 가장 가까운 임계까지의 거리를 보인다. 경계 표시(⚠️)는 F6 와 같은 허용폭 안일 때만.
    boundary = p.get("boundary") or {}
    if p.get("gate") == "G3" and p.get("runway_years") is not None and boundary.get("nearest_boundary"):
        text += (" " if not text.endswith(":") else "") + (f"런웨이 {p['runway_years']:.2f}년(임계 {boundary['nearest_boundary']:g}년 대비 {boundary['distance_ratio']:+.1%}"
                 f"{' ⚠️ 경계' if boundary.get('flag') else ''})")
    return text


def _factor_row(f: str, fr: dict[str, Any]) -> list[Any]:
    calc = fr.get("calc") or {}
    detail = ""
    if f == "F6" and calc.get("ntm_per") is not None:
        detail = f"NTM PER {fmt_num(calc['ntm_per'])} → 구간 {calc.get('band', '')}"
        if (calc.get("boundary") or {}).get("flag"):
            detail += " ⚠️ 경계"
    elif f == "F6" and "valuation_over_arr" in calc:
        detail = f"밸류÷ARR {fmt_num(calc['valuation_over_arr'])}x"
    elif f == "F3" and "pass_points" in calc:
        detail = f"통과점 {calc['pass_points']:g}"
    elif f == "F5" and "A" in calc:
        detail = f"3 + {calc['A']} + {calc['H']}"
    elif f == "F7" and "funding_dependent_share" in calc:
        detail = f"{calc['funding_dependent_share']} / {calc['own_money_returns']}"
    elif f == "F9" and calc.get("path"):
        detail = " → ".join(_f9_gate_text(p) for p in calc["path"])
    pending = fr.get("pending") or {}
    if pending:
        detail = (detail + " · " if detail else "") + pending.get("message", "")
    return [FACTOR_LABELS[f], fmt_score(fr["score"]), STATUS_LABEL.get(fr["status"], fr["status"]), fr["basis"], detail]


def render_draft(ctx: Any, results: dict[str, Any], baseline: dict[str, Any] | None, triggers: list[dict[str, Any]]) -> str:
    run = ctx.run
    title = run["title"]
    ranking = results["ranking"]
    population = results["population"]
    companies_by_id = {c["company_id"]: c for c in results["companies"]}
    fm = frontmatter([
        ("slug", ctx.slug), ("report_type", "ai_scorecard"), ("title", title),
        ("subtitle", f"규칙 {ctx.rules.version} · 기준일 {run['as_of']} · {population['scored']}개사 순위"),
        ("run_id", ctx.slug), ("as_of", run["as_of"]), ("price_as_of", run.get("price_as_of") or run["as_of"]), ("info_cutoff", run.get("info_cutoff") or run["as_of"]),
        ("rule_version", ctx.rules.version), ("rule_hash", ctx.rules.hash),
        ("baseline_id", run["baseline_id"]), ("plan_source", f"plan/{ctx.slug}.md"), ("research_source", f"research/{ctx.slug}.md"),
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
        worst = min(ranking, key=lambda r: r["trap"])
        candidates = [c["display_name"] + ("" if c["complete"] else "(미완료)") for c in moat_pool if c["moat"] >= 20]
        lines += [
            f"- 조정총점 1위: {top_names} ({top[0]['total']}점){' — 공동' if len(top) > 1 else ''}",
            f"- 과점 factor 최고: {moat_top} ({max_moat}점) — 과점이 완결된 전 기업 기준",
            f"- 함정 최심(완료 {population['scored']}개사 기준): {worst['display_name']} ({worst['trap']}점, 조정 {worst['total']}점)",
            f"- 과점 후보군(과점 20점 이상): {', '.join(candidates) if candidates else '없음'}",
        ]
    lines += [f"- 모집단: 완료 {population['scored']}개사 순위 / 미완료 {len(population['incomplete'])}개사 제외 (미완료는 0점으로 채우지 않는다). 모집단이 다르므로 기준선 {run['baseline_id']} 의 14사 순위와 직접 비교하지 않는다(기업별 상세에 기준선 순위를 병기)."]
    lines += [f"- 기준 시점: 분석 기준일 {run['as_of']} · 가격 기준일 {run.get('price_as_of') or run['as_of']} · 정보 컷오프 {run.get('info_cutoff') or run['as_of']} (C-17). 승계 근거·트리거 일부는 원문에 컷오프 이후 사건이 그대로 있으며 이번 실행에서 재검증하지 않았다."]
    if conflicts:
        lines += [f"- 이해상충 고지: {' / '.join(conflicts)}. 채점 대상에 Anthropic 이 포함된다. 투자 판단에 사용할 경우 감안할 것."]
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
    judgments_by_pair = {(j["company_id"], j["factor"]): j for j in ctx.judgments}
    reps = _replacements(ctx)
    for c in ordered:
        b = baseline_scores.get(c["company_id"])
        base_rank = f" · 기준선 {run['baseline_id']} {b['rank_raw']}위(14사)" if b and b.get("rank_raw") else ""
        head = f"{c['rank']}위(완료 {population['scored']}개사 기준)" if c["rank"] else "미완료"
        lines += [f"### {c['display_name']} — {head}{base_rank} · 조정 {fmt_score(c['total'])} (과점 {fmt_score(c['moat'])} / 함정 {fmt_score(c['trap'])})", ""]
        if b and b.get("tag"):
            lines += [f"> 기준선 {run['baseline_id']} 한 줄 요약(과거 기록): {b['tag']}", ""]
        lines += [table(["Factor", "점수", "상태", "근거 종류", "산식·경로"], [_factor_row(f, c["factors"][f]) for f in FACTOR_IDS]), ""]
        incompatible_g4 = any(o["company_id"] == c["company_id"] and o["metric"] in ("contracted_revenue", "offbalance_B") and o["status"] == "incompatible_basis" for o in ctx.observations)
        for f in FACTOR_IDS:
            fr = c["factors"][f]
            base_evidence = (b or {}).get("evidence", {}).get(f, []) if b else []
            # 2026-09-15 FIX-53 RC-06: 원래 기준선 v1.5 근거만 찍어서 이번 실행이 갱신한 판단(impl48·fix52 등)의 근거가
            # 초안에 나오지 않았다. 활성 판단이 있으면 그 evidence 를 먼저 찍고, 기준선 서술은 '과거 기록' 으로 따로 둔다.
            judgment = judgments_by_pair.get((c["company_id"], f))
            if judgment is not None:
                lines += _judgment_evidence_lines(f, judgment, base_evidence, run["baseline_id"], reps)
                if f == "F9" and incompatible_g4:
                    lines.append("  - (원문 커버리지 계산은 ARR·연환산 약정 기반이라 C-07 로 이번 실행 미적용)")
            elif base_evidence:
                header = f"기준선 {run['baseline_id']} 서술(참고 — 이번 실행은 입력에서 자동 산출, 원문 판단은 미적용)"
                lines += [f"- **{FACTOR_LABELS[f]}** {header}:"]
                lines += [f"  - {_annotate_replaced(e, c['company_id'], reps)}" for e in base_evidence[:6]]
                if f == "F9" and incompatible_g4:
                    lines.append("  - (원문 커버리지 계산은 ARR·연환산 약정 기반이라 C-07 로 이번 실행 미적용)")
            for w in fr["warnings"][:4]:
                lines.append(f"  - ⚠️ {w}")
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
        "- 정책 기본값 적용: C-04 완충 산정은 exclude(설계 권고). " + ("이번 실행에는 undrawn_credit 관측이 없어 include 를 골라도 결과가 같다." if not any(o["metric"] == "undrawn_credit" for o in ctx.observations) else "undrawn_credit 관측이 있어 선택에 따라 런웨이가 달라질 수 있다."),
        f"- C-06 중 BEP 후퇴→{_f9_policy(ctx, 'g1_bep_retreat_score')} 는 원문 OR 조건 그대로 적용하며(경고 표시), 손실률 경계·우선순위 명문화만 미결이다.",
        "",
        table(["Factor", "자동화", "범위"], [[FACTOR_LABELS[f], ctx.rules.factor(f)["mode"], f"{ctx.rules.factor(f)['range'][0]}~{ctx.rules.factor(f)['range'][1]}"] for f in FACTOR_IDS]),
        "",
        # 2026-09-15 FIX-52: 두 줄이 v1.5 문구(NTM PER 구간표 · 하한 -5)로 박혀 v1.7 결과와 모순됐다. 규칙에서 읽는다.
        ("- ⑥ 상장: P1 TTM PER · P2 (시총−순현금)/매출 · P3 매출 성장 · P4 입력 신뢰도 보정(parameters 정본). "
         "비상장: P2 밸류÷TTM 보정 매출에 P3·P4 합쳐 최대 한 칸 보정(C-12)."
         if ctx.rules.f6_mode == "parameters" else
         "- ⑥ 상장: NTM PER 20·29·42·62·90 반개방 구간, 경계 ±3% 는 표시만. 비상장: 배수 자동 계산·점수는 정성 예외."),
        f"- ⑨: G1 본업(TTM 영업손익) → G2 현금(TTM FCF) → G3 런웨이(현금+확정 여신 ÷ 연 소진) → G4 약정 커버리지(계약 수입 ÷ B종). 하한 {_f9_policy(ctx, 'floor')}.",
        "- ③ 사다리, ⑤ `3 + A + H`, ⑦ 2×2 매트릭스는 판정 입력에서 자동 환산. ①④⑧은 정성 점수.",
        "",
    ]
    # 트리거
    lines += ["## 트리거", ""]
    if triggers:
        replaced = _trigger_replacements(ctx, triggers)
        lines += [table(["ID", "항목", "왜 중요한가(v1.5 원문)", "영향(원문)"],
                        [[t["trigger_id"], t["title"], _apply_text_corrections(ctx, t["why"] + replaced.get(t["trigger_id"], ""), "triggers"),
                          t["impact_raw"]] for t in triggers]), "",
                  "- 트리거의 예상 점수는 저장값이 아니라 원문 문장이다(C-14). 사건 확인 후 현재 규칙으로 재계산한다.",
                  f"- `왜 중요한가` 의 날짜·금액·수치는 기준선 {ctx.run['baseline_id']} 원문(2026-09-02 기준)이다. 이번 실행이 실측으로 "
                  "대체한 수치는 그 칸 끝에 ⚠️ 로 적었다. 사건 사실 자체의 뉴스 출처는 sources.json 에 등재돼 있지 않다.", ""]
    else:
        lines += ["- 등록된 트리거 없음", ""]
    # References
    lines += ["## References", ""]
    for src in ctx.sources.get("items", []):
        url = src.get("url") or "URL 미제공"
        coi = f" · 이해상충: {src['conflict_of_interest']}" if src.get("conflict_of_interest") else ""
        sha = f" · sha256 {src['sha256'][:12]}…" if src.get("sha256") else ""
        lines.append(f"- {src.get('source_id')} — {src.get('title')} · {src.get('publisher') or ''} · {src.get('accessed_at') or ''} · {url}{sha}{coi}")
    lines += ["", f"_{DISCLAIMER}_", ""]
    return fm + "\n" + "\n".join(lines)


def _struck(text: str) -> str:
    """취소선. 본문에 `~` 가 있으면 마크다운 취소선이 깨지므로 표시어로 대신한다."""
    return f"~~{text}~~ (superseded)" if "~" not in text else f"(superseded) {text}"


def _judgment_evidence_lines(f: str, judgment: dict[str, Any], base_evidence: list[str], baseline_id: str,
                             reps: list[dict[str, Any]] | None = None) -> list[str]:
    """활성 판단 근거를 먼저, 대체된 판단·기준선 서술을 뒤에 따로 찍는다.

    - 승계 판단(carried): 근거란 자체가 기준선 문면이다. 이번 실행이 근거란에 붙인 superseded 표시·추가 문장까지
      그대로 보이도록 **판단 파일의 evidence** 를 찍는다.
    - 이번 실행 판단(new): 새 근거를 먼저 찍고, 대체된 옛 판단(superseded)과 기준선 서술을 과거 기록으로 따로 찍는다.
    """
    label = FACTOR_LABELS[f]
    jid = judgment["judgment_id"]
    evidence = [_annotate_replaced(e, judgment["company_id"], reps) for e in (judgment.get("evidence") or [])]
    if judgment["status"] == "carried":
        out = [f"- **{label}** 근거(승계 판단 `{jid}` · 기준선 {baseline_id} · 검토 {judgment['reviewed_at']}):"]
        out += [f"  - {e}" for e in evidence]
        return out
    out = [f"- **{label}** 근거(이번 실행 판단 `{jid}` · {judgment['reviewer']} · {judgment['reviewed_at']}):"]
    out += [f"  - {e}" for e in evidence]
    sup = judgment.get("superseded")
    if sup:
        out.append(f"  - 대체된 판단 `{sup['judgment_id']}` (superseded {sup['superseded_at']}) — {sup['why']}")
        out += [f"    - {_struck(e)}" for e in sup.get("evidence", [])[:6]]
        if len(sup.get("evidence", [])) > 6:
            out.append(f"    - (외 {len(sup['evidence']) - 6}줄은 judgments.json superseded 에 있다)")
    elif base_evidence and base_evidence != list(judgment.get("evidence") or []):
        old = [e for e in base_evidence if e not in (judgment.get("evidence") or [])]
        if old:
            out.append(f"  - 과거 기록(기준선 {baseline_id} 서술 — 이번 실행 판단으로 대체):")
            out += [f"    - {_struck(e)}" for e in old[:6]]
    return out


def _f9_policy(ctx: Any, key: str) -> Any:
    return (ctx.rules.payload.get("policies", {}).get("f9") or {}).get(key)


def _status_summary(obs: Any, cids: list[str], columns: list[tuple[str, str]]) -> str:
    """열마다 엔진이 고르는 관측(ObsLookup 우선순위)의 status 를 센다. 관측이 없으면 `관측 없음`."""
    parts = []
    for label, metric in columns:
        counts: dict[str, int] = {}
        for cid in cids:
            o = obs.get(cid, metric)
            key = o["status"] if o is not None else "관측 없음"
            counts[key] = counts.get(key, 0) + 1
        order = ["verified", "legacy_unverified"]
        items = sorted(counts.items(), key=lambda kv: (order.index(kv[0]) if kv[0] in order else 9, kv[0]))
        parts.append(f"{label} " + " · ".join(f"{k} {v}" for k, v in items))
    return " | ".join(parts)


def _cash_definition_note(ctx: Any) -> str:
    """`현금` 열과 `순현금/순부채` 열은 다른 것을 센다 — 같은 행에서 맞춰 볼 수 없다는 사실을 규칙 블록으로 적는다."""
    sep = ((ctx.rules.payload.get("policies", {}).get("f6") or {}).get("net_cash") or {}).get("scope_separation") or {}
    sites = {s.get("metric"): s for s in sep.get("sites", [])}
    cash, net = sites.get("cash", {}), sites.get("net_cash", {})
    return ("- **현금 두 정의** — `현금` 열은 `cash` 관측(" + (cash.get("site") or "런웨이") + ", 질문 `" + (cash.get("question") or "") +
            "`)이고, `순현금/순부채` 열은 `net_cash` 관측(" + (net.get("site") or "EV 조정") + ", 질문 `" + (net.get("question") or "") +
            "`)으로 시장성 유가증권을 포함한다. **같은 행의 두 열은 서로 맞춰 볼 수 없다** — 순현금은 현금 열에서 차입을 뺀 값이 아니다"
            "(규칙 policies.f6.net_cash.scope_separation). 비상장·일부 기업은 원문 기준이 달라 제한현금 포함 여부도 다를 수 있다.")


LEGACY_ID_RE = re.compile(r"[a-z-]+\.[A-Za-z_]+\.v15\b")


def _legacy_texts(legacy: dict[str, Any]) -> list[str]:
    """legacy 값이 원문 서술에 적혔을 법한 표기들. 비율은 소수 첫째 자리 %, 달러는 $NB·$N.NB·$NT 형태."""
    v = float(legacy["value"])
    if legacy.get("unit") == "ratio":
        return [f"{v * 100:.1f}%"]
    if legacy.get("unit") == "USD" and abs(v) >= 1e9:
        b = abs(v) / 1e9
        sign = "-" if v < 0 else ""
        forms = {f"{sign}${b:.1f}B", f"{sign}${b:.2f}B"}
        if float(b).is_integer():
            forms.add(f"{sign}${b:.0f}B")
        if abs(v) >= 1e12:
            forms.add(f"{sign}${abs(v) / 1e12:.2f}T")
        return sorted(forms, key=len, reverse=True)
    return []


def _replacements(ctx: Any) -> list[dict[str, Any]]:
    """이번 실행의 verified 관측이 대체한 legacy 관측(basis.replaces 또는 note 에 id 로 적힘, 같은 지표)을 모은다.

    2026-09-15 FIX-53 3단계: 트리거에만 붙이던 대체 표시를 기준선 서술·승계 근거에도 붙이려고 떼어 냈다. note 만 보는
    관측(amazon.offbalance_B.obsreg25 ← .v15 $106B)이 있어 basis.replaces 만으로는 모자랐다.
    """
    by_id = {o["observation_id"]: o for o in ctx.observations}
    out = []
    for o in ctx.observations:
        if o["status"] != "verified" or o.get("value") is None:
            continue
        text = " ".join(str(x) for x in ((o.get("basis") or {}).get("replaces"), o.get("note")) if x)
        for lid in sorted(set(LEGACY_ID_RE.findall(text))):
            legacy = by_id.get(lid)
            if legacy is None or legacy["metric"] != o["metric"] or legacy.get("value") is None:
                continue
            olds = [t for t in _legacy_texts(legacy) if t]
            if olds:
                out.append({"company_id": o["company_id"], "old_texts": olds, "obs": o, "legacy_id": lid})
    return out


def _new_value_text(o: dict[str, Any]) -> str:
    if o.get("unit") == "ratio":
        return f"{o['value'] * 100:.3f}%"
    return fmt_usd(o["value"])


def _annotate_replaced(text: str, company_id: str, reps: list[dict[str, Any]]) -> str:
    """서술 한 줄에 대체된 legacy 수치가 그대로 있으면 끝에 ⚠️ 와 실측값을 붙인다. 원문 문장은 고치지 않는다."""
    notes = []
    if text.startswith("📐"):
        return text                                     # 이번 실행이 붙인 설명 줄은 이미 대체 사실을 적는다
    for r in reps:
        if r["company_id"] != company_id:
            continue
        hit = next((t for t in r["old_texts"] if t in text), None)
        if hit:
            o = r["obs"]
            period = o.get("period") or {}
            when = f"{period['start']}~{period['end']}" if period else o["as_of"]
            new = _new_value_text(o)
            if new == hit and o.get("unit") == "USD":
                new = fmt_usd(o["value"], 3)            # 반올림 표기가 원문과 같으면 자릿수를 늘려 차이를 보인다
            notes.append(f"⚠️ 원문 {hit} 는 이번 실행 실측 {new}({o['observation_id']}, verified, {when})로 대체됐다")
    return text + ("".join(f" {n}." for n in notes))


def _apply_text_corrections(ctx: Any, text: str, target: str) -> str:
    """rules.source_text_corrections 중 target 에 해당하는 것을 줄 끝에 붙인다. 이미 marker 가 있으면 건너뛴다."""
    for c in ctx.rules.payload.get("source_text_corrections") or []:
        if target in c["applies_to"] and c["match"] in text and c["marker"] not in text:
            text = f"{text} {c['correction']}"
    return text


def _trigger_replacements(ctx: Any, triggers: list[dict[str, Any]]) -> dict[str, str]:
    """이번 실행의 verified 관측이 대체한 legacy 값이 트리거 원문에 그대로 있으면 표시한다(회사 이름이 트리거에 있을 때)."""
    reps = _replacements(ctx)
    notes: dict[str, str] = {}
    for t in triggers:
        text = t["title"] + " " + t["why"]
        for cid, company in ctx.companies.items():
            names = [company.get("display_name", "")] + list(company.get("aliases") or [])
            if not any(n and len(n) > 2 and n in text for n in names):
                continue
            annotated = _annotate_replaced(t["why"], cid, reps)
            if annotated != t["why"]:
                notes[t["trigger_id"]] = notes.get(t["trigger_id"], "") + annotated[len(t["why"]):]
    return notes


def _offbalance_cell(obs: Any, cid: str, note: dict[str, Any] | None) -> str:
    """2026-09-15 FIX-53 3단계: 엔진이 G4 에 쓰는 verified offbalance_B 가 있으면 그 값을 찍는다.

    legacy `offbalance_note` 는 v1.5 원문 문구라 amazon 이 `미개시 리스 $106B` 로 나왔는데 엔진은 267,279M 을 썼다.
    원문 문구는 지우지 않고 대체 표시로 뒤에 둔다.
    """
    legacy = ((note or {}).get("value") or "—")[:60]
    b = obs.get(cid, "offbalance_B")
    if b is not None and b["status"] == "verified" and b.get("value") is not None:
        return f"{fmt_usd(b['value'])} B종(verified) · 원문 {_struck(legacy)}"
    return legacy


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
                flag = "⚠️" if ((f6.get("calc") or {}).get("boundary") or {}).get("flag") else "—"
            val_rows.append([name, fmt_usd(obs.number(cid, "price")[0], 2), fmt_usd(obs.number(cid, "market_cap")[0], 2), fmt_num(per), method or "—", fmt_score(f6["score"]), flag, _num_or_raw(obs, cid, "ttm_per"), _pct_or_raw(obs, cid, "nonop_share"), fmt_num(obs.number(cid, "ps_ratio")[0])])
        else:
            calc = c["factors"]["F6"].get("calc") or {}
            priv_rows.append([name, fmt_usd(obs.number(cid, "post_money_valuation")[0]), fmt_usd(obs.number(cid, "arr")[0]), fmt_num(calc.get("valuation_over_arr")), fmt_usd(obs.number(cid, "cumulative_raised")[0]), fmt_num(calc.get("arr_over_cumulative_raised"), 2), fmt_score(c["factors"]["F6"]["score"])])
        fcf, fcf_obs = obs.number(cid, "fcf_ttm")
        rating = obs.get(cid, "credit_rating")
        note = obs.get(cid, "offbalance_note")
        fin_rows.append([name, _usd_or_raw(obs, cid, "cash"), fmt_usd(fcf) if fcf is not None else ((fcf_obs or {}).get("raw") or "—"), _runway_text(c, obs), fmt_usd(obs.number(cid, "net_cash")[0]), fmt_num(obs.number(cid, "debt_ebitda")[0], 2), (rating or {}).get("value") or "—", _offbalance_cell(obs, cid, note), fmt_score(c["factors"]["F9"]["score"])])
        nb, nb_obs = obs.number(cid, "net_borrowing_ttm")
        if nb_obs is not None:
            borr_rows.append([name, fmt_usd(nb) if nb is not None else (nb_obs.get("raw") or "—"), fmt_usd(obs.number(cid, "capex_ttm")[0])])
    legacy_n = sum(1 for o in ctx.observations if o["status"] == "legacy_unverified")
    # 2026-09-15 FIX-52: '모든 값은 legacy_unverified' 라고 적었는데 재무 표의 현금·TTM FCF·순현금은 verified 였다(리뷰 A).
    # 표마다 열별로 엔진이 실제로 고른 관측의 status 를 센다.
    cids = [c["company_id"] for c in results["companies"]]
    listed = [c["company_id"] for c in results["companies"] if c["listed"]]
    lines += [f"기준선 {ctx.run['baseline_id']} 승계 관측(`legacy_unverified` {legacy_n}건, SRC-v15-html·SRC-v15-md·SRC-v15-rule)은 이번 실행에서 재검증되지 않았다(D-08). **표마다 실측(verified)과 승계가 섞여 있다** — 각 표 아래에 열별 관측 상태를 적는다. 상장사 주가는 USD 이고 TSMC 는 ADR(1주=보통주 5주, 재무 TWD), Alibaba 는 ADS(재무 CNY) 기준이다. `—` 는 관측 없음, 원문 상태(미공시·적자·∞)는 그대로 표기한다.", ""]
    lines += ["### 가격 — ⑥ 원자료", "", table(["기업", "주가", "시총", "NTM PER", "산출 방법", "⑥", "경계", "TTM PER", "영업외 비중", "P/S"], val_rows), "",
              "- 열별 관측 상태: " + _status_summary(obs, listed, [("주가", "price"), ("시총", "market_cap"), ("NTM PER", "ntm_per"), ("TTM PER", "ttm_per"), ("영업외 비중", "nonop_share"), ("P/S", "ps_ratio")]), ""]
    if priv_rows:
        lines += ["### 비상장 — ⑥ 배수", "", table(["기업", "post-money", "ARR", "밸류÷ARR", "누적 조달", "ARR÷조달", "⑥"], priv_rows), "", "- 비상장 배수는 상장사 PER 과 직접 비교할 수 없다. 점수는 정성 예외(C-12).", ""]
    lines += ["### 재무 — ⑨ 원자료", "", table(["기업", "현금", "TTM FCF", "런웨이(년)", "순현금/순부채", "D/EBITDA", "신용", "부외 약정(B종 실측 · 없으면 v1.5 원문)", "⑨"], fin_rows), "",
              "- 열별 관측 상태: " + _status_summary(obs, cids, [("현금", "cash"), ("TTM FCF", "fcf_ttm"), ("순현금/순부채", "net_cash"), ("D/EBITDA", "debt_ebitda"), ("신용", "credit_rating")]),
              _cash_definition_note(ctx),
              "- 신용등급·CDS 는 점수 입력이 아니라 교차검증 지표다(별표 J).", ""]
    if borr_rows:
        lines += ["### TTM 순차입", "", table(["기업", "TTM 순차입", "TTM capex"], borr_rows), ""]
    return lines


# ------------------------------------------------------------------ review template

def render_review_template(ctx: Any, results: dict[str, Any], *, draft_hash: str) -> str:
    fm = frontmatter([
        ("slug", ctx.slug), ("report_type", "ai_scorecard"), ("status", "needs_fix"), ("created_at", ctx.run["created_at"]),
        ("plan_source", f"plan/{ctx.slug}.md"), ("research_source", f"research/{ctx.slug}.md"), ("draft_source", f"drafts/{ctx.slug}.md"),
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
             "## 판정", "", f"- results_hash `{results['results_hash'][:16]}…` · draft_hash `{draft_hash[:16]}…` 기준 검토. 자료·규칙·판단·초안이 바뀌면 이 리뷰는 무효다(D-10).", ""]
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
        lines += ["", f"선택은 `scorecard/runs/{ctx.slug}/run.json` 의 `decisions` 에 `{{id, choice, rationale, decided_by, decided_at}}` 로 기록한 뒤 다시 `calculate` 한다.", ""]
    lines += ["## 변동 원인 분류", "", "- 기준선 이관 재계산이라 변동 원인은 📐규칙(미결 결정·엄격 계약)이며 기업 실적 변화가 아니다. 규칙 버전이 같은 실행끼리만 추세로 연결한다.", ""]
    return "\n".join(lines)
