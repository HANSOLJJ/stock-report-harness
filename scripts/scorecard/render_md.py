# 실행 원본(run·observations·judgments·results)에서 plan/research/draft/review 템플릿/preview Markdown 을 생성하는 렌더러
from __future__ import annotations

from typing import Any

from report_contract_lib import rel

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
        # 2026-09-16 FIX-57 2단계(6차 리뷰 A 분담): 출처별 문구 다섯을 ` / ` 로 이어 붙여 **실행 차원 고지가 맨 끝에 묻혔다.**
        # 읽는 사람이 먼저 알아야 하는 것은 채점자와 채점 대상이 같은 곳이라는 사실이다. 출처별 문구는 References 에 그대로 있다.
        flagged = len([s for s in ctx.sources.get("items", []) if s.get("conflict_of_interest")])
        lines += [f"- **이해상충 고지 — 채점 대상에 Anthropic 이 포함되고, 이 채점표를 Anthropic 이 만든 Claude 가 작성했다**"
                  f"(채점규칙 384행 · HANDOVER 75행 · 운영이력 긴장 #4·#11). 투자 판단에 사용할 경우 감안할 것. "
                  f"비상장 2사의 수치는 이해당사자 1차 발표에서 온다. 이해상충이 표기된 출처 {flagged}건의 개별 문구는 "
                  f"References 의 각 출처 줄에 있고, `알려진 한계` 절이 제3자 재검토 약속을 함께 적는다."]
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
    lines += [f"- {rc.card_evidence_note(run['baseline_id'])}", ""]
    for c in ordered:
        b = baseline_scores.get(c["company_id"])
        base_rank = f" · 기준선 {run['baseline_id']} {b['rank_raw']}위(14사)" if b and b.get("rank_raw") else ""
        head = f"{c['rank']}위(완료 {population['scored']}개사 기준)" if c["rank"] else "미완료"
        lines += [f"### {c['display_name']} — {head}{base_rank} · 조정 {fmt_score(c['total'])} (과점 {fmt_score(c['moat'])} / 함정 {fmt_score(c['trap'])})", ""]
        if b and b.get("tag"):
            lines += [f"> 기준선 {run['baseline_id']} 한 줄 요약(과거 기록): {b['tag']}", ""]
        lines += [table(["Factor", "점수", "상태", "근거 종류", "산식·경로"], [_factor_row(f, c["factors"][f]) for f in FACTOR_IDS]), ""]
        incompatible_g4 = rc.g4_incompatible(ctx.observations, c["company_id"])
        for f in FACTOR_IDS:
            fr = c["factors"][f]
            base_evidence = (b or {}).get("evidence", {}).get(f, []) if b else []
            block = rc.evidence_block(fr, judgments_by_id, base_evidence, run["baseline_id"], c["company_id"], reps)
            if block is not None:
                lines.append(f"- **{FACTOR_LABELS[f]}** {block['header']}:")
                # 2026-09-17 FIX-67: 근거 문장에 번호가 데이터로 들어 있다. 초안도 HTML 과 같은 이름을 쓴다.
                lines += [("  " * depth) + f"- {rc.rename_codes(text)}" for depth, text in block["lines"]]
                if f == "F9" and incompatible_g4:
                    lines.append(f"  - {rc.G4_INCOMPATIBLE_NOTE}")
            # 2026-09-17 FIX-77: 초안도 카드와 같은 규칙을 쓴다. 승계 표기는 근거 머리줄이 이미 말하고,
            # `⚠️` 는 글자로 밝히며, 작업 메모는 본문에서 내린다(감사 기록에 남는다).
            for w in fr["warnings"][:4]:
                if str(w).startswith("승계된 판단 — 원검토일"):
                    continue
                wbody, _note = rc.split_worknote(rc.readable_warning(str(w)))
                if wbody:
                    # HTML 카드가 `주의` 배지를 다는 자리다. 초안도 같은 말로 밝힌다.
                    head = "" if wbody.startswith("주의 —") else "주의 — "
                    lines.append(f"  - {head}{rc.rename_codes(wbody)}")
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
    lines += [f"- {x}" for x in rc.method_lines(ctx)] + [""]
    # 한계 — 2026-09-15 FIX-54 1단계 S4
    lines += ["## 알려진 한계", ""] + [x if x.startswith("  - ") else f"- {x}" for x in rc.limitations(ctx)] + [""]
    # 트리거
    lines += ["## 트리거", ""]
    if triggers:
        reps = rc.replacements(ctx)
        lines += [table(["ID", "항목", "왜 중요한가(v1.5 원문)", "영향(원문)"],
                        [[t["trigger_id"], t["title"], rc.trigger_why(ctx, t, reps), t["impact_raw"]] for t in triggers]), ""]
        lines += [f"- {x}" for x in rc.trigger_notes(ctx)] + [""]
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
        lines += ["", f"선택은 `scorecard/runs/{ctx.slug}/run.json` 의 `decisions` 에 `{{id, choice, rationale, decided_by, decided_at}}` 로 기록한 뒤 다시 `calculate` 한다.", ""]
    lines += ["## 변동 원인 분류", "", "- 기준선 이관 재계산이라 변동 원인은 📐규칙(미결 결정·엄격 계약)이며 기업 실적 변화가 아니다. 규칙 버전이 같은 실행끼리만 추세로 연결한다.", ""]
    return "\n".join(lines)
