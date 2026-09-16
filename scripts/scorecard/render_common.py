# 초안(render_md)과 HTML(render_html)이 함께 쓰는 표시 규칙 — 한쪽만 고쳐져 두 산출물이 갈리는 것을 구조적으로 막는다
"""2026-09-15 FIX-54 1단계 S3. FIX-53 에서 초안 렌더러만 고쳐 HTML 이 통째로 뒤처졌다(3차 리뷰 D).

여기 함수는 **마크업을 모른다.** 문장은 초안과 같은 인라인 마크다운(`**굵게**`·`~~취소선~~`·백틱)으로 돌려주고
HTML 렌더러는 `inline_html` 로 바꿔 쓴다. 표시 규칙을 고칠 때는 이 파일만 고친다.
"""
from __future__ import annotations

import html as html_lib
import re
from typing import Any

FACTOR_LABELS = {
    "F1": "① 네트워크", "F2": "② 게임체인저", "F3": "③ Last Mover", "F4": "④ 호황 이후", "F5": "⑤ 아군",
    "F6": "⑥ 가격", "F7": "⑦ 순환금융", "F8": "⑧ 비대칭 의존", "F9": "⑨ 적자 깊이",
}
METHOD_LABELS = {
    "consensus_4q_sum": "미발표 4개 분기 컨센서스 합",
    # 이 키 이름은 기준선 이관 코드의 문자열이다. NTM 적격성이 검증됐다는 뜻이 아니므로 라벨로 그렇게 읽히면 안 된다.
    "vendor_forward_pe_verified_ntm": "공급사 forward PE(이관 코드 명칭 · 기간 미확인 · NTM 적격성 미검증)",
    "annual_weighted_proxy": "연간 EPS 가중 근사(정밀도 열위)",
}
SHARE_LABELS = {"large": "큼", "small": "작음", "unknown": "미확인"}
YESNO_LABELS = {"yes": "있음", "no": "없음", "unknown": "미확인"}
GATE_LABELS = {
    "pass": "통과", "fail": "실패", "positive_stable": "FCF 흑자·추세 안정", "positive_deteriorating": "FCF 흑자·추세 악화",
    "negative": "FCF 마이너스", "not_disclosed": "미공시", "zero": "0", "pending": "대기", "skipped": "생략",
    "computed": "산출", "undetermined": "판정 불가", "incompatible": "비교 불가", "no_obligations": "약정 없음",
}
F6_PARAM_LABELS = {"P1": "P1 PER", "P2": "P2 EV/매출", "P3": "P3 매출 성장"}
VENDOR_MARK = "†"


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


def inline_html(text: str) -> str:
    """이스케이프한 뒤 백틱·`~~`·`**` 만 태그로 바꾼다. 나머지 마크다운 기호는 글자 그대로 둔다."""
    out = html_lib.escape(str(text), quote=True)
    out = re.sub(r"`([^`]+)`", r"<code>\1</code>", out)
    out = re.sub(r"~~(.+?)~~", r"<del>\1</del>", out)
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", out)


def struck(text: str) -> str:
    """취소선. 본문에 `~` 가 있으면 마크다운 취소선이 깨지므로 표시어로 대신한다."""
    return f"~~{text}~~ (superseded)" if "~" not in text else f"(superseded) {text}"


# ------------------------------------------------------------------ 대체된 수치

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


def replacements(ctx: Any) -> list[dict[str, Any]]:
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


def annotate_replaced(text: str, company_id: str, reps: list[dict[str, Any]] | None) -> str:
    """서술 한 줄에 대체된 legacy 수치가 그대로 있으면 끝에 ⚠️ 와 실측값을 붙인다. 원문 문장은 고치지 않는다."""
    notes = []
    if text.startswith("📐"):
        return text                                     # 이번 실행이 붙인 설명 줄은 이미 대체 사실을 적는다
    for r in reps or []:
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


def apply_text_corrections(ctx: Any, text: str, target: str) -> str:
    """rules.source_text_corrections 중 target 에 해당하는 것을 줄 끝에 붙인다. 이미 marker 가 있으면 건너뛴다."""
    for c in ctx.rules.payload.get("source_text_corrections") or []:
        if target in c["applies_to"] and c["match"] in text and c["marker"] not in text:
            text = f"{text} {c['correction']}"
    return text


def trigger_why(ctx: Any, trigger: dict[str, Any], reps: list[dict[str, Any]]) -> str:
    """트리거 `왜 중요한가` 칸. 원문 뒤에 대체된 수치 ⚠️(트리거에 이름이 나온 회사만)와 규칙 원문 정정을 붙인다."""
    why = trigger["why"]
    text = trigger["title"] + " " + why
    extra = ""
    for cid, company in ctx.companies.items():
        names = [company.get("display_name", "")] + list(company.get("aliases") or [])
        if any(n and len(n) > 2 and n in text for n in names):
            extra += annotate_replaced(why, cid, reps)[len(why):]
    return apply_text_corrections(ctx, why + extra, "triggers")


def trigger_notes(ctx: Any) -> list[str]:
    return ["트리거의 예상 점수는 저장값이 아니라 원문 문장이다(C-14). 사건 확인 후 현재 규칙으로 재계산한다.",
            f"`왜 중요한가` 의 날짜·금액·수치는 기준선 {ctx.run['baseline_id']} 원문(2026-09-02 기준)이다. 이번 실행이 실측으로 "
            "대체한 수치는 그 칸 끝에 ⚠️ 로 적었다. 사건 사실 자체의 뉴스 출처는 sources.json 에 등재돼 있지 않다."]


# ------------------------------------------------------------------ 근거 블록

G4_INCOMPATIBLE_NOTE = "(원문 커버리지 계산은 ARR·연환산 약정 기반이라 C-07 로 이번 실행 미적용)"


def card_evidence_note(baseline_id: str) -> str:
    return (f"근거 불릿은 이번 실행 결과에 연결된 판단의 근거란을 먼저 보인다. 승계 판단은 기준선 {baseline_id} 문면에 이번 실행이 붙인 "
            "superseded 표시·정정이 함께 있고, 이번 실행 판단은 새 근거 뒤에 대체된 옛 판단을 취소선으로 둔다. 판단이 연결되지 않은 "
            "자동 산출 factor 는 기준선 서술을 참고로만 보인다. 카드의 한 줄 요약은 기준선 원문이며 이번 실행에서 재검증하지 않았다.")


def g4_incompatible(observations: list[dict[str, Any]], cid: str) -> bool:
    return any(o["company_id"] == cid and o["metric"] in ("contracted_revenue", "offbalance_B") and o["status"] == "incompatible_basis"
               for o in observations)


def evidence_block(fr: dict[str, Any], judgments_by_id: dict[str, dict[str, Any]], base_evidence: list[str],
                   baseline_id: str, company_id: str, reps: list[dict[str, Any]] | None) -> dict[str, Any] | None:
    """factor 하나의 근거 블록 `{kind, header, lines: [(depth, text)]}`. 보일 것이 없으면 None.

    2026-09-15 FIX-54 1단계 S4: (회사, factor) 쌍으로 판단을 찾아 자동 산출 F6(anthropic·openai, judgment_id 없음)에
    옛 승계 판단 문구가 찍혔다. **factor 결과의 judgment_id 로만** 찾는다. 판단이 연결되지 않은 factor 는 기준선 참고 라벨이다.

    - 승계 판단(carried): 근거란 자체가 기준선 문면이다. 이번 실행이 붙인 superseded 표시·추가 문장까지 보이도록 판단 파일의 evidence 를 찍는다.
    - 이번 실행 판단(new): 새 근거를 먼저 찍고, 대체된 옛 판단(superseded)이나 기준선 서술을 과거 기록으로 따로 찍는다.
    """
    judgment = judgments_by_id.get(fr.get("judgment_id") or "")
    if judgment is None:
        if not base_evidence:
            return None
        return {"kind": "baseline_reference",
                "header": f"기준선 {baseline_id} 서술(참고 — 이번 실행은 입력에서 자동 산출, 원문 판단은 미적용)",
                "lines": [(1, annotate_replaced(e, company_id, reps)) for e in base_evidence[:6]]}
    jid = judgment["judgment_id"]
    evidence = [annotate_replaced(e, company_id, reps) for e in (judgment.get("evidence") or [])]
    if judgment["status"] == "carried":
        return {"kind": "carried", "header": f"근거(승계 판단 `{jid}` · 기준선 {baseline_id} · 검토 {judgment['reviewed_at']})",
                "lines": [(1, e) for e in evidence]}
    lines = [(1, e) for e in evidence]
    sup = judgment.get("superseded")
    if sup:
        lines.append((1, f"대체된 판단 `{sup['judgment_id']}` (superseded {sup['superseded_at']}) — {sup['why']}"))
        lines += [(2, struck(e)) for e in sup.get("evidence", [])[:6]]
        if len(sup.get("evidence", [])) > 6:
            lines.append((2, f"(외 {len(sup['evidence']) - 6}줄은 judgments.json superseded 에 있다)"))
    elif base_evidence and base_evidence != list(judgment.get("evidence") or []):
        old = [e for e in base_evidence if e not in (judgment.get("evidence") or [])]
        if old:
            lines.append((1, f"과거 기록(기준선 {baseline_id} 서술 — 이번 실행 판단으로 대체):"))
            lines += [(2, struck(e)) for e in old[:6]]
    return {"kind": "new", "header": f"근거(이번 실행 판단 `{jid}` · {judgment['reviewer']} · {judgment['reviewed_at']})",
            "lines": lines}


# ------------------------------------------------------------------ 산식 텍스트

def f9_gate_text(p: dict[str, Any]) -> str:
    label = (GATE_LABELS.get(p.get("result"), p.get("result") or "") or p.get("adjust")
             or (f"적용 → {p['score']}" if p.get("applied") and p.get("score") is not None else ""))
    text = f"{p['gate']} {label}".rstrip()
    # 2026-09-15 FIX-53 2단계: G3 런웨이와 가장 가까운 임계까지의 거리를 보인다. 경계 표시(⚠️)는 F6 와 같은 허용폭 안일 때만.
    if p.get("runway_years") is not None:
        text += f" 런웨이 {p['runway_years']:.2f}년"
        boundary = p.get("boundary") or {}
        if boundary.get("nearest_boundary"):
            text += (f"(임계 {boundary['nearest_boundary']:g}년 대비 {boundary['distance_ratio']:+.1%}"
                     f"{' ⚠️ 경계' if boundary.get('flag') else ''})")
    if p.get("coverage") is not None:
        text += f" 커버리지 {p['coverage']:.2f}"
    return text


def f6_boundary_flag(calc: dict[str, Any]) -> bool:
    """경계 열. v1.7 parameters 는 P1~P3 각자와 P4 영업외 비중 임계를 본다. v1.5 bands 는 calc.boundary 하나다."""
    if calc.get("mode") == "parameters":
        flags = [((p or {}).get("boundary") or {}).get("flag") for p in (calc.get("parameters") or {}).values()]
        flags.append(((calc.get("p4") or {}).get("nonop_share_boundary") or {}).get("flag"))
        return any(bool(x) for x in flags)
    return bool((calc.get("boundary") or {}).get("flag"))


def _f6_parameters_text(calc: dict[str, Any]) -> str:
    parts = []
    labels = dict(F6_PARAM_LABELS, P2="P2 밸류/매출") if calc.get("track") == "private" else F6_PARAM_LABELS
    for pid, p in (calc.get("parameters") or {}).items():
        value = p.get("value")
        if value is None:
            parts.append(f"{labels.get(pid, pid)} —")
            continue
        shown = f"{value * 100:.1f}%" if pid == "P3" else (f"{fmt_num(value)}x" if pid == "P2" else fmt_num(value))
        parts.append(f"{labels.get(pid, pid)} {shown} → {p.get('score')}"
                     + (" ⚠️ 경계" if (p.get("boundary") or {}).get("flag") else ""))
    text = " + ".join(parts)
    if "subtotal_before_p4" in calc:
        p4 = calc.get("p4") or {}
        steps = p4.get("demotion_steps") or 0
        hit = ", ".join(p4.get("conditions_hit") or []) or "해당 없음"
        text += f" = 소계 {calc['subtotal_before_p4']} · P4 {-steps if steps else 0}({hit})"
        # 2026-09-16 FIX-55 1단계(4차 리뷰 D): 조건 하나가 강등을 혼자 정했다는 사실이 이름으로 보이지 않았다.
        if p4.get("demotion_sole_cause"):
            text += f" — `{p4['demotion_sole_cause']}` 하나가 강등을 정한다"
        if ((p4.get("nonop_share_boundary") or {}).get("flag")):
            text += " ⚠️ 영업외 비중 경계"
    if "subtotal_before_correction" in calc:
        text += f" = 소계 {calc['subtotal_before_correction']} · 비상장 보정 +{(calc.get('correction') or {}).get('promotion_steps', 0)}"
    if calc.get("unverified_inputs"):
        text += " · 승계 입력 " + ", ".join(f"{k}({'·'.join(v)})" for k, v in calc["unverified_inputs"].items())
    return text


def factor_calc_text(f: str, fr: dict[str, Any]) -> str:
    calc = fr.get("calc") or {}
    text = ""
    cov = calc.get("coverage") if f == "F6" else None
    if cov:
        # 부분 확보를 숨기지 않는다. 몇 개를 확보했고 어느 분기가 있는지 그대로 보여준다.
        text = f"분기 컨센서스 {cov['secured']}/{cov['required']} 확보"
        if cov.get("quarters"):
            text += f" ({', '.join(cov['quarters'])})"
        if cov.get("sources"):
            text += f" · 원천 {', '.join(cov['sources'])}"
        if calc.get("ntm_per") is not None:
            text += f" → NTM PER {fmt_num(calc['ntm_per'])}"
            if calc.get("band"):
                text += f" · 구간 {calc['band']}"
            if (calc.get("boundary") or {}).get("flag"):
                text += " ⚠️ 구간 경계 ±3% 이내"
        if calc.get("requires_reapproval"):
            text += " · 재승인 필요"
        pending = fr.get("pending") or {}
        if pending:
            text += " · " + pending.get("message", "")
        return text
    if f == "F6" and calc.get("mode") == "parameters" and calc.get("parameters"):
        text = _f6_parameters_text(calc)
    elif f == "F6" and calc.get("ntm_per") is not None:
        text = f"NTM PER {fmt_num(calc['ntm_per'])} ({METHOD_LABELS.get(calc.get('method'), calc.get('method', ''))})"
        if calc.get("band"):
            text += f" → 구간 {calc['band']}"
        if (calc.get("boundary") or {}).get("flag"):
            text += " ⚠️ 구간 경계 ±3% 이내"
    elif f == "F6" and "valuation_over_arr" in calc:
        text = f"밸류÷ARR {fmt_num(calc['valuation_over_arr'])}x · ARR÷조달 {fmt_num(calc.get('arr_over_cumulative_raised'), 2)}"
    elif f == "F3" and "pass_points" in calc:
        text = str(calc.get("ladder_note") or f"통과점 {calc['pass_points']:g}")
    elif f == "F5" and "A" in calc:
        text = f"3 + A({calc['A']}) + H({calc['H']})"
    elif f == "F7" and "funding_dependent_share" in calc:
        text = f"조달 의존 고객 비중 {SHARE_LABELS.get(calc['funding_dependent_share'], calc['funding_dependent_share'])} · 내 돈 환류 {YESNO_LABELS.get(calc['own_money_returns'], calc['own_money_returns'])}"
    elif f == "F9" and calc.get("path"):
        text = " → ".join(f9_gate_text(p) for p in calc["path"])
    pending = fr.get("pending") or {}
    if pending:
        text = (text + " · " if text else "") + pending.get("message", "")
    return text


def private_multiples(calc: dict[str, Any]) -> tuple[float | None, float | None]:
    """비상장 표의 밸류÷ARR · ARR÷조달. v1.7 은 calc.multiples 에, v1.5 는 calc 바로 아래에 있다."""
    m = calc.get("multiples") or {}
    return (calc.get("valuation_over_arr", m.get("post_money_over_arr")),
            calc.get("arr_over_cumulative_raised", m.get("arr_over_cumulative_raised")))


# ------------------------------------------------------------------ 원자료 표

def status_summary(obs: Any, cids: list[str], columns: list[tuple[str, str]]) -> str:
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


PRICE_STATUS_COLUMNS = [("주가", "price"), ("시총", "market_cap"), ("NTM PER", "ntm_per"), ("TTM PER", "ttm_per"), ("영업외 비중", "nonop_share"), ("P/S", "ps_ratio")]
FIN_STATUS_COLUMNS = [("현금", "cash"), ("TTM FCF", "fcf_ttm"), ("순현금/순부채", "net_cash"), ("D/EBITDA", "debt_ebitda"), ("신용", "credit_rating")]
OFFBALANCE_HEADER = "부외 약정(B종 실측 · 없으면 v1.5 원문)"
CREDIT_NOTE = "신용등급·CDS 는 점수 입력이 아니라 교차검증 지표다(별표 J)."


def vendor_mark(obs: Any, cid: str, metric: str) -> str:
    """엔진이 고르는 관측에 `vendor_not_in_source_policy` 가 있으면 칸 옆에 † 를 붙인다."""
    o = obs.get(cid, metric)
    return VENDOR_MARK if o is not None and (o.get("basis") or {}).get("vendor_not_in_source_policy") else ""


def raw_caption(ctx: Any) -> str:
    legacy_n = sum(1 for o in ctx.observations if o["status"] == "legacy_unverified")
    # 2026-09-15 FIX-52: '모든 값은 legacy_unverified' 라고 적었는데 재무 표의 현금·TTM FCF·순현금은 verified 였다(리뷰 A).
    return (f"기준선 {ctx.run['baseline_id']} 승계 관측(`legacy_unverified` {legacy_n}건, SRC-v15-html·SRC-v15-md·SRC-v15-rule)은 "
            "이번 실행에서 재검증되지 않았다(D-08). **표마다 실측(verified)과 승계가 섞여 있다** — 각 표 아래에 열별 관측 상태를 적는다. "
            "상장사 주가는 USD 이고 TSMC 는 ADR(1주=보통주 5주, 재무 TWD), Alibaba 는 ADS(재무 CNY) 기준이다. `—` 는 관측 없음, "
            "원문 상태(미공시·적자·∞)는 그대로 표기한다.")


def price_notice(ctx: Any) -> str:
    if ctx.rules.f6_mode == "parameters":
        return ("⑥ 상장 점수는 P1 TTM PER · P2 (시총−순현금)/매출 · P3 매출 성장의 합에 P4 입력 신뢰도 보정을 더한 값이다(parameters 정본). "
                "NTM PER·TTM PER·P/S·영업외 비중 열은 v1.5 승계 참고값이며 점수는 이 열이 아니라 원자료에서 다시 계산한다. "
                "경계 열의 ⚠️ 는 P1~P3 구간 경계나 P4 영업외 비중 임계까지 거리가 ±3% 이내라는 표시이며 점수를 바꾸지 않는다.")
    return ("NTM PER 만 ⑥ 점수에 개입한다. TTM PER·P/S·영업외 비중은 참고·왜곡 탐지용이며 영업외 30% 이상이면 TTM PER 은 무효로 본다. "
            "경계 열의 ⚠️ 는 구간 경계(20·29·42·62·90)까지 거리가 ±3% 이내라는 표시이며 점수를 바꾸지 않는다.")


def private_notice(ctx: Any) -> str:
    if ctx.rules.f6_mode == "parameters":
        return ("비상장 배수는 상장사 PER 과 직접 비교할 수 없다. 점수는 P2 구간표에 P3·P4 조건을 모두 채울 때만 한 칸 올리는 보정(C-12)이며 "
                "경계 표시를 적용하지 않는다.")
    return "비상장 배수는 상장사 PER 과 직접 비교할 수 없다. 점수는 정성 예외(C-12)이며 경계 표시를 적용하지 않는다."


def vendor_policy_note(ctx: Any) -> str:
    """2026-09-15 FIX-54 1단계 S4: `vendor_not_in_source_policy` 관측 26건이 초안·HTML 에 드러나지 않았다(3차 리뷰 D)."""
    flagged = [o for o in ctx.observations if (o.get("basis") or {}).get("vendor_not_in_source_policy")]
    if not flagged:
        return ""
    by_metric: dict[str, int] = {}
    for o in flagged:
        by_metric[o["metric"]] = by_metric.get(o["metric"], 0) + 1
    detail = " · ".join(f"{m} {n}건" for m, n in sorted(by_metric.items()))
    return (f"{VENDOR_MARK} **원천 정책 밖 공급사 값 {len(flagged)}건**({detail}). 관측 basis 에 `vendor_not_in_source_policy` 가 붙은 v1.5 승계 값이다 — "
            "상류가 StockAnalysis 이거나 그 주가로 계산한 값이고, StockAnalysis 는 원천 장부에 `not_adopted · legacy_upstream` 으로만 올라 있다. "
            "표에서는 엔진이 실제로 고른 칸에만 † 를 붙인다. 시총은 P1·P2 입력이라 † 가 붙은 기업의 ⑥ 은 실측 전 값 위에 서 있다(점수를 깎지는 않는다).")


def cash_definition_note(ctx: Any) -> str:
    """`현금` 열과 `순현금/순부채` 열은 다른 것을 센다. 같은 행에서 맞춰 볼 수 없다는 사실을 규칙 블록에서 읽어 적는다."""
    sep = ((ctx.rules.payload.get("policies", {}).get("f6") or {}).get("net_cash") or {}).get("scope_separation") or {}
    sites = {s.get("metric"): s for s in sep.get("sites", [])}
    cash, net = sites.get("cash", {}), sites.get("net_cash", {})
    return ("**현금 두 정의** — `현금` 열은 `cash` 관측(" + (cash.get("site") or "런웨이") + ", 질문 `" + (cash.get("question") or "") +
            "`)이고, `순현금/순부채` 열은 `net_cash` 관측(" + (net.get("site") or "EV 조정") + ", 질문 `" + (net.get("question") or "") +
            "`)으로 시장성 유가증권을 포함한다. **같은 행의 두 열은 서로 맞춰 볼 수 없다** — 순현금은 현금 열에서 차입을 뺀 값이 아니다"
            "(규칙 policies.f6.net_cash.scope_separation). 비상장·일부 기업은 원문 기준이 달라 제한현금 포함 여부도 다를 수 있다.")


def credit_lines(ctx: Any, results: dict[str, Any]) -> list[str]:
    """확정 미인출 여신 설명. 2026-09-15 FIX-54 2단계: amazon 지연인출 $17.5B 가 기준일 28일 뒤 소멸한다는 조건이 초안에 없었다.

    런웨이 분자에 들어간 verified `undrawn_credit` 만 적는다. 구성요소에 `undrawn_terminates_on`(미인출분 소멸일) ·
    `matures_on_month`(만기 월)가 있으면 실행 기준일에서 며칠·몇 달 뒤인지 붙인다.
    """
    from datetime import date

    as_of = date.fromisoformat(ctx.run["as_of"])
    names = {c["company_id"]: c["display_name"] for c in results["companies"]}
    out = []
    for o in ctx.observations:
        if o["metric"] != "undrawn_credit" or o["status"] != "verified" or o.get("value") is None:
            continue
        notes = []
        for comp in (o.get("basis") or {}).get("components") or []:
            label = f"{comp.get('facility', '')} {fmt_usd(comp.get('capacity'))}".strip()
            if comp.get("undrawn_terminates_on"):
                end = date.fromisoformat(comp["undrawn_terminates_on"])
                notes.append(f"{label} 는 {end.isoformat()} 까지 인출하지 않으면 미인출분이 소멸한다 — 기준일({as_of.isoformat()}) {(end - as_of).days}일 뒤")
            elif comp.get("matures_on_month"):
                notes.append(f"{label} 는 {comp['matures_on_month']} 만기다(연장은 대주 승인 조건)")
        tail = (" " + " · ".join(notes) + ". 런웨이는 기준일 현재 유효한 약정으로 계산했다.") if notes else ""
        out.append(f"확정 미인출 여신 — {names.get(o['company_id'], o['company_id'])} {fmt_usd(o['value'])}({o['observation_id']}, {o['as_of']}).{tail}")
    return out


def c04_line(ctx: Any) -> str:
    """C-04 가 실제로 무엇을 바꾸는지. 선택을 조회해도 G3 산술은 같다(calc_f9, 3차 리뷰 C RC3-06)."""
    has_credit = any(o["metric"] == "undrawn_credit" and o["status"] == "verified" for o in ctx.observations)
    return ("정책 기본값 적용: C-04 완충 산정은 exclude(설계 권고) — 완충은 현금 + 조건이 확인된 확정 미인출 여신(`undrawn_credit` 관측)뿐이다. "
            "include_v15 를 골라도 경고 문구만 바뀌고 G3 산술은 같다(등급 기반 조달 여력은 숫자 관측으로만 들어오고 추정치는 넣지 않는다). "
            "G1 실패 진단 경로에서는 이 선택을 조회하지 않는다."
            + (" 이번 실행의 여신 관측은 선택과 무관하게 런웨이에 들어간다." if has_credit else ""))


def offbalance_cell(obs: Any, cid: str) -> str:
    """2026-09-15 FIX-53 3단계: 엔진이 G4 에 쓰는 verified offbalance_B 가 있으면 그 값을 찍는다.

    legacy `offbalance_note` 는 v1.5 원문 문구라 amazon 이 `미개시 리스 $106B` 로 나왔는데 엔진은 267,279M 을 썼다.
    원문 문구는 지우지 않고 대체 표시로 뒤에 둔다.
    """
    legacy = ((obs.get(cid, "offbalance_note") or {}).get("value") or "—")[:60]
    b = obs.get(cid, "offbalance_B")
    if b is not None and b["status"] == "verified" and b.get("value") is not None:
        return f"{fmt_usd(b['value'])} B종(verified) · 원문 {struck(legacy)}"
    return legacy


# ------------------------------------------------------------------ 방법·한계

def f9_policy(ctx: Any, key: str) -> Any:
    return (ctx.rules.payload.get("policies", {}).get("f9") or {}).get(key)


def method_lines(ctx: Any) -> list[str]:
    """방법 절의 factor 설명. 2026-09-15 FIX-52 에서 초안만 규칙에서 읽게 고쳤고 FIX-54 에서 HTML 도 이 목록을 쓴다."""
    f6 = ("⑥ 상장: P1 TTM PER · P2 (시총−순현금)/매출 · P3 매출 성장 · P4 입력 신뢰도 보정(parameters 정본). "
          "비상장: P2 밸류÷TTM 보정 매출에 P3·P4 합쳐 최대 한 칸 보정(C-12)."
          if ctx.rules.f6_mode == "parameters" else
          "⑥ 상장: NTM PER 20·29·42·62·90 반개방 구간, 경계 ±3% 는 표시만. 비상장: 배수 자동 계산·점수는 정성 예외.")
    return [
        f"C-06 중 BEP 후퇴→{f9_policy(ctx, 'g1_bep_retreat_score')} 는 원문 OR 조건 그대로 적용하며(경고 표시), 손실률 경계·우선순위 명문화만 미결이다.",
        f6,
        f"⑨: G1 본업(TTM 영업손익) → G2 현금(TTM FCF) → G3 런웨이(현금+확정 여신 ÷ 연 소진, 임계 ±3% 는 경계 표시만) → G4 약정 커버리지(계약 수입 ÷ B종). 하한 {f9_policy(ctx, 'floor')}.",
        "③ 사다리, ⑤ `3 + A + H`, ⑦ 2×2 매트릭스는 판정 입력에서 자동 환산. ①④⑧은 정성 점수. 모르는 값은 0으로 치환하지 않는다.",
        # 2026-09-15 FIX-54 1단계 S7 RC3-06: 목록에 있다고 계산이 그 선택을 읽었다는 뜻이 아니다.
        "`실행 단위 결정` 목록은 run.json 에 기록된 선택이다. 각 선택이 이번 계산에서 실제로 소비됐다는 증명은 아니다(소비 여부는 factor 산식·경고에서 확인한다).",
    ]


def limitations(ctx: Any) -> list[str]:
    """2026-09-15 FIX-54 1단계 S4: 한 줄 경고로만 있던 한계를 짧은 절 하나로. 문장은 규칙 파일에서 읽는다."""
    out = []
    f6 = ctx.rules.payload.get("policies", {}).get("f6") or {}
    cond = {c["id"]: c for c in ((f6.get("p4") or {}).get("conditions") or [])}.get("nonop_share") or {}
    sv = cond.get("stored_vs_recomputed") or {}
    if sv:
        ex = sv.get("exceptions") or {}
        explained = "; ".join(f"{k} — {v}" for k, v in (ex.get("explained") or {}).items()) or "없음"
        unexplained = "; ".join(f"{k} — {v}" for k, v in (ex.get("unexplained") or {}).items()) or "없음"
        out.append(f"**영업외 비중 저장값과 재계산값이 다르다**(status `{sv.get('status')}`). 원자료 표의 `영업외 비중` 열은 v1.5 저장값이고 "
                   f"P4 는 원자료에서 다시 계산한 값(`{cond.get('formula', '')}`)을 쓴다. 설명된 차이: {explained} 설명 못 한 차이: {unexplained}")
    nc = f6.get("net_cash") or {}
    if nc:
        questions = nc.get("open_questions") or []
        out.append(f"**순현금은 작업 정의다**(status `{nc.get('status')}`). legacy 값에서 역산해 세운 정의라 확정 정의가 나오면 P2 를 다시 계산한다. "
                   f"남은 질문 {len(questions)}건(규칙 policies.f6.net_cash.open_questions)은 아래와 같다.")
        for q in questions:
            # 취소한 문장은 빼고, 자를 때 강조·코드 표시가 반쯤 남지 않게 기호를 걷어 낸 뒤 자른다.
            q = re.sub(r"~~.*?~~\s*", "", q).replace("**", "").replace("`", "").strip()
            out.append("  - " + (q if len(q) <= 160 else q[:157] + "…"))
    return out
