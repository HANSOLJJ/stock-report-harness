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
    # 2026-09-17 FIX-67: 실제 데이터 키는 이쪽인데 표에 없어 영어 그대로 나왔다.
    "annual_eps_weighted_proxy": "연간 EPS 가중 근사(정밀도 열위)",
}
SHARE_LABELS = {"large": "큼", "small": "작음", "unknown": "미확인"}
YESNO_LABELS = {"yes": "있음", "no": "없음", "unknown": "미확인"}
GATE_LABELS = {
    "pass": "통과", "fail": "실패", "positive_stable": "FCF 흑자·추세 안정", "positive_deteriorating": "FCF 흑자·추세 악화",
    "negative": "FCF 마이너스", "not_disclosed": "미공시", "zero": "0", "pending": "대기", "skipped": "생략",
    "computed": "산출", "undetermined": "판정 불가", "incompatible": "비교 불가", "no_obligations": "약정 없음",
}
# 2026-09-17 FIX-67: 사용자 지시로 본문에서 `P1`·`G3` 같은 번호를 쓰지 않고 이름을 그대로 쓴다.
# 번호는 `results.json`·규칙·감사 기록에만 남는다 — 아래 표가 데이터의 번호를 화면 이름으로 옮긴다.
# 이름 출처: 규칙 `policies.f6.parameters[].label`·`policies.f6.p4.label` 과 ⑨ 게이트 순서.
F6_PARAM_LABELS = {"P1": "PER", "P2": "EV/매출", "P3": "매출 성장"}
F6_P4_LABEL = "입력 신뢰도"
F9_GATE_LABELS = {"G1": "본업", "G2": "현금", "G3": "런웨이", "G4": "약정 커버리지"}
# 2026-09-17 FIX-71 N1: `G1-after` 라는 내부 코드가 카드에 그대로 나왔다. 관문이 아니라 **첫째 관문 실패 뒤
# 진단값을 점수로 확정하는 자리**다. `G3/G4` 는 둘을 한꺼번에 건너뛸 때 쓰는 합성 키다.
F9_STAGE_LABELS = {"G1-after": "본업 실패 뒤 정리", "G3/G4": "런웨이·약정 커버리지"}
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


# 2026-09-17 FIX-67: `results.json` 의 경고와 판단 근거 문장에 번호가 **데이터로** 들어 있다
# (`market_cap 이 legacy_unverified 인데 P1, P2 가 …`). 데이터를 고치면 results_hash 가 바뀌므로
# **표시할 때 이름으로 옮겨 그린다.** 번호 뒤에 이름의 끝 낱말이 이미 붙어 있으면(`G4 커버리지`)
# 둘을 합쳐 한 번만 쓴다.
CODE_NAMES = {**F6_PARAM_LABELS, "P4": F6_P4_LABEL, **F9_GATE_LABELS}
# 2026-09-17 FIX-68 S3: 상태는 한국어로 옮겨 놓고 근거(basis)만 영어로 나갔다. 같은 이름을 초안·HTML 이 쓴다.
# 뜻풀이는 색인(render_html.BASIS_DOC)에 있고 여기 있는 것은 **화면에 찍는 짧은 이름**이다.
BASIS_LABELS = {
    "computed": "산식 계산", "manual": "사람 판단", "carried": "숫자만 승계",
    "grade": "등급 산식", "matrix": "조합표", "criteria": "기준 사다리", "paths": "조건 통과 수",
}
MODE_LABELS = {
    "manual": "사람 판단", "paths": "조건 통과 수", "ladder": "기준 사다리", "formula": "산식",
    "parameters": "수치 합산", "matrix": "조합표", "gates": "관문 통과",
}
# 관측 지표·상태·조건의 내부 이름도 화면에서는 한국어로 옮긴다. **긴 이름부터** 바꾼다
# (`not_disclosed_confirmed` 가 `not_disclosed` 를 품는다). 결정 선택지와 코드·규칙 경로는 감사 기록·
# 색인과 대조해야 하므로 **그대로 남긴다.**
TERM_NAMES = {
    "market_cap": "시가총액", "net_cash": "순현금", "lease_liabilities": "리스부채",
    "revenue_ttm_prior": "전년 매출", "revenue_ttm_full": "12개월 매출", "revenue_ttm": "최근 1년 매출",
    "net_income_ttm": "최근 1년 순이익", "pretax_income_ttm": "세전이익",
    "operating_income_ttm": "영업이익", "operating_margin_ttm": "영업손익률",
    "fcf_ttm": "잉여현금흐름", "undrawn_credit": "미인출 여신", "ntm_per": "예상 PER",
    "contracted_revenue": "계약 수입", "offbalance_B": "부외 B종 약정", "debt_ebitda": "차입÷EBITDA",
    "nonop_share": "영업외 비중", "period_basis_not_ttm": "기간 단위 불일치",
    "short_history": "이력 부족", "stale_asof": "기준 시점 경과",
    "annual_eps_weighted_proxy": "연간 EPS 가중 근사",
    "legacy_unverified": "기준선 승계·미검증", "not_disclosed_confirmed": "확인된 미공시",
    "not_disclosed": "미공시", "incompatible_basis": "기준 비교 불가", "not_applicable": "해당 없음",
    "working_definition": "작업 정의", "collection_failed": "수집 실패", "parse_failed": "파싱 실패",
    # `verified` 는 낱말 하나라 아래 정규식(밑줄이 있는 이름)에 걸리지 않는다. 상태 요약에서만 쓴다.
    "verified": "검증 완료",
}
# 2026-09-17 FIX-73: 결정 선택지 이름이 경고 문구에 영어로 실렸다(`results.json` 의 warnings 안이라
# 데이터를 고칠 수 없다). **뜻은 규칙 `decisions` 의 해당 항목에서 가져왔고 여기서 새로 짓지 않았다.**
# 식별자는 감사 기록과 결정 사전에 그대로 남아 대조할 수 있다.
CHOICE_NAMES = {
    # C-03 — 경로 수 매핑을 쓰되 세대 격차면 최고점(recommendation·note)
    "paths_with_generation_gap_5": "경로 수 매핑 + 세대 격차 최고점",
    "activate_candidate_mapping": "후보 매핑 적용",
    # C-05 — G1 실패 뒤 추가 감점인가 진단만인가(summary)
    "apply": "뒤 관문 값을 점수에 반영", "diagnose_only": "진단만 하고 점수는 유지",
    # C-06 — 제안된 손실률 구간을 쓴다(recommendation: g1_bands_proposed)
    "proposed_v15_boundaries": "제안된 손실률 구간 적용",
    # C-11 — 영업외 비중을 ⑦ 로 이월하지 않는다(confirmed_model.rule)
    "block_carryover": "⑦ 로 이월 금지", "allow_carryover": "⑦ 로 이월 허용",
    # C-12 — 비상장은 배수 구간표에 한 칸 상한 보정(choices)
    "p2_with_capped_promotion": "배수 구간표 + 한 칸 상한 보정",
    "manual_with_rationale": "근거를 적은 정성 판단",
    # C-13 — 연간 EPS 가중 근사를 NTM 으로 받지 않는다(summary)
    "reject_proxy": "근사값 불인정", "accept_proxy_with_flag": "근사값을 표시와 함께 인정",
    # C-16 — 판정 불가를 하향할 것인가 유지할 것인가(summary)
    "downgrade": "판정 불가면 한 칸 하향", "hold": "판정 불가면 유지",
    # C-20 — 비상장 미공시는 G2 비상장 조항으로(choices·rule)
    "defer_to_private_g2": "비상장 경로로 보냄", "permanent_pending": "영구 보류",
    "assume_loss": "적자로 단정",
    # C-24 — 입력이 있으면 P2 를 계산한다(recommendation)
    "compute_p2_when_inputs_exist": "입력이 있으면 계산", "p3_only_v17": "매출 성장만 계산",
    # C-28 — 상장 트랙에 선택 파라미터를 둔다(recommendation)
    "optional_parameters_for_all_listed_tracks": "상장 트랙에 선택 파라미터",
    "keep_pending_data": "자료 대기로 유지", "explicit_loss_track": "순손실 트랙 신설",
    # C-29 — 비상장 경로가 BEP 후퇴보다 앞선다(recommendation)
    "c20_private_route_first": "비상장 경로 우선", "bep_retreat_first": "흑자 전환 후퇴 우선",
}
TERM_NAMES.update(CHOICE_NAMES)

_TERM_RE = re.compile(r"(?<![A-Za-z0-9_./-])(" + "|".join(
    sorted((re.escape(k) for k in TERM_NAMES), key=len, reverse=True))
    + r")(?![A-Za-z0-9_])(\s*)([가-힣]+)?")
_CODE_RE = re.compile(r"(?<![A-Za-z0-9_./-])([PG][1-4])(?![A-Za-z0-9_.-])(\s*)([가-힣A-Za-z/]+)?")
# 2026-09-17 FIX-73 S2: `G3/G4` 는 `_CODE_RE` 가 `G3` 만 잡고 `/G4` 는 lookbehind 에 걸려 남겼다.
# 복합 단계 이름은 낱개 번호보다 **먼저** 통째로 옮겨 그린다.
_STAGE_RE = re.compile("|".join(
    re.escape(k) for k in sorted(F9_STAGE_LABELS, key=len, reverse=True)))


# 2026-09-17 FIX-68 S4: `P2 가` 를 `EV/매출 가` 로 바꾸니 조사가 맞지 않았다. 이름의 **끝 글자 받침**으로
# 조사를 고른다. `EV/매출`(ㄹ 받침)·`PER`(R 은 소리로 `얼` 이라 받침 있음)·`런웨이`(받침 없음)가 갈린다.
JOSA_PAIRS = {"이": "가", "은": "는", "을": "를", "과": "와", "으로": "로", "이나": "나", "이라": "라",
              "이란": "란", "이며": "며", "이면": "면", "이다": "다"}
# 서술격 활용형(`인데`·`이고`·`이지만`)은 받침으로 갈리지 않는다 — 빈칸만 붙여 쓴다.
JOSA_GLUE = ("인데", "이고", "이지만", "이라서", "이었다", "인지", "이라는")
JOSA_ALT = {**JOSA_PAIRS, **{v: k for k, v in JOSA_PAIRS.items()}}
# 영문·숫자로 끝나는 이름의 받침. 소리대로 읽어 정한다(PER → 퍼, EV/매출 → 출).
_ALPHA_BATCHIM = {"l": True, "m": True, "n": True, "r": True, "g": True, "b": True, "k": True,
                  "p": True, "t": True, "c": True, "d": True, "s": True, "x": True, "z": True,
                  "a": False, "e": False, "i": False, "o": False, "u": False, "h": False,
                  "j": False, "q": False, "v": False, "w": False, "y": False, "f": True}
_NUM_BATCHIM = {"0": True, "1": True, "3": True, "6": True, "7": True, "8": True,
                "2": False, "4": False, "5": False, "9": False}


def has_batchim(word: str) -> bool | None:
    """낱말 끝소리에 받침이 있는가. 판단할 수 없으면 None."""
    for ch in reversed(word):
        if "가" <= ch <= "힣":
            return (ord(ch) - 0xAC00) % 28 != 0
        if ch.isdigit():
            return _NUM_BATCHIM.get(ch)
        if ch.isalpha():
            return _ALPHA_BATCHIM.get(ch.lower())
    return None


def fix_josa(name: str, gap: str, josa: str) -> str:
    """이름 뒤 조사를 받침에 맞게 고르고 사이 빈칸도 정리한다."""
    if josa in JOSA_GLUE:
        return name + josa            # 받침과 무관하다. 빈칸만 없앤다
    bat = has_batchim(name)
    if bat is None or josa not in JOSA_ALT:
        return name + gap + josa
    with_bat, without = (josa, JOSA_ALT[josa]) if josa in JOSA_PAIRS else (JOSA_ALT[josa], josa)
    return name + (with_bat if bat else without)


def rename_codes(text: str) -> str:
    def one(m: re.Match[str]) -> str:
        name = CODE_NAMES[m.group(1)]
        gap, nxt = m.group(2) or "", m.group(3) or ""
        if nxt and nxt == (name.split() or [""])[-1]:
            return name          # 뒤 공백은 매치 밖에 남아 있다 — 여기서 더하면 두 칸이 된다
        if nxt in JOSA_ALT or nxt in JOSA_GLUE:
            return fix_josa(name, gap, nxt)
        return name + gap + nxt

    def term(m: re.Match[str]) -> str:
        name = TERM_NAMES[m.group(1)]
        gap, nxt = m.group(2) or "", m.group(3) or ""
        if nxt in JOSA_ALT or nxt in JOSA_GLUE:
            return fix_josa(name, gap, nxt)
        return name + gap + nxt

    text = _STAGE_RE.sub(lambda m: F9_STAGE_LABELS[m.group(0)], text)
    return _TERM_RE.sub(term, _CODE_RE.sub(one, text))


def inline_html(text: str) -> str:
    """이스케이프한 뒤 백틱·`~~`·`**` 만 태그로 바꾼다. 나머지 마크다운 기호는 글자 그대로 둔다."""
    out = html_lib.escape(rename_codes(str(text)), quote=True)
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
        # 2026-09-17 FIX-59 S4(8차 리뷰 D low): 기준선 문면의 첫 줄이 옛 점수로 시작해(anthropic F6 `-3 (v1.5: …)`)
        # 현재 점수(-4)와 다른 수가 근거란 맨 앞에 왔다. **현재 점수를 첫 줄로 세운다** — 라벨만으로는 첫인상이 안 바뀐다.
        now = "미산출" if fr.get("score") is None else f"{fr['score']:+d}"
        head = (f"**이번 실행 점수는 {now} 이고 입력에서 자동 산출한 값이다**(위 산식 참조). "
                f"아래는 기준선 {baseline_id} 문면이라 다른 수가 섞여 있을 수 있다 — 점수 근거가 아니다.")
        return {"kind": "baseline_reference",
                "header": f"기준선 {baseline_id} 서술(참고 — 이번 실행은 입력에서 자동 산출, 원문 판단은 미적용)",
                "lines": [(1, head)] + [(1, annotate_replaced(e, company_id, reps)) for e in base_evidence[:6]]}
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
    gate = p["gate"]
    name = F9_STAGE_LABELS.get(gate) or F9_GATE_LABELS.get(gate, gate)
    # 2026-09-17 FIX-71 N1: 경로의 `mode` 를 읽지 않아 진단으로 계산한 칸이 본경로처럼 보였다.
    if p.get("mode") == "diagnostic":
        name += " 진단"
    text = f"{name} {label}".rstrip()
    # 2026-09-15 FIX-53 2단계: G3 런웨이와 가장 가까운 임계까지의 거리를 보인다. 경계 표시(⚠️)는 F6 와 같은 허용폭 안일 때만.
    if p.get("runway_years") is not None:
        # 관문 이름이 이미 `런웨이` 라 그대로 붙이면 말이 겹친다.
        text += f" {p['runway_years']:.2f}년" if name.startswith("런웨이") else f" 런웨이 {p['runway_years']:.2f}년"
        boundary = p.get("boundary") or {}
        if boundary.get("nearest_boundary"):
            text += (f"(임계 {boundary['nearest_boundary']:g}년 대비 {boundary['distance_ratio']:+.1%}"
                     f"{' ⚠️ 경계' if boundary.get('flag') else ''})")
    if p.get("coverage") is not None:
        text += f" {p['coverage']:.2f}배" if "커버리지" in name else f" 커버리지 {p['coverage']:.2f}"
    return text


def f6_boundary_flag(calc: dict[str, Any]) -> bool:
    """경계 열. v1.7 parameters 는 세 파라미터 각자와 입력 신뢰도의 영업외 비중 임계를 본다. v1.5 bands 는 calc.boundary 하나다."""
    if calc.get("mode") == "parameters":
        flags = [((p or {}).get("boundary") or {}).get("flag") for p in (calc.get("parameters") or {}).values()]
        flags.append(((calc.get("p4") or {}).get("nonop_share_boundary") or {}).get("flag"))
        return any(bool(x) for x in flags)
    return bool((calc.get("boundary") or {}).get("flag"))


def _f6_parameters_text(calc: dict[str, Any]) -> str:
    parts = []
    labels = dict(F6_PARAM_LABELS, P2="밸류/매출") if calc.get("track") == "private" else F6_PARAM_LABELS
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
        text += f" = 소계 {calc['subtotal_before_p4']} · {F6_P4_LABEL} {-steps if steps else 0}({hit})"
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
        # 2026-09-17 FIX-67: 상태 키를 영어 그대로 찍어 `legacy_unverified 12` 로 나왔다.
        parts.append(f"{label} " + " · ".join(f"{TERM_NAMES.get(k, k)} {v}" for k, v in items))
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
        return ("⑥ 상장 점수는 **PER · EV/매출(시총에서 순현금을 뺀 값 ÷ 매출) · 매출 성장** 셋을 더한 뒤 "
                "**입력 신뢰도**로 한 칸을 조정한 값이다. "
                "아래 표의 NTM PER·TTM PER·P/S·영업외 비중 열은 기준선에서 넘어온 참고값이고 점수는 이 열이 아니라 원자료에서 다시 계산한다. "
                "경계 열의 ⚠️ 는 구간 경계까지 거리가 ±3% 이내라는 표시이며 점수를 바꾸지 않는다.")
    return ("NTM PER 만 ⑥ 점수에 개입한다. TTM PER·P/S·영업외 비중은 참고·왜곡 탐지용이며 영업외 30% 이상이면 TTM PER 은 무효로 본다. "
            "경계 열의 ⚠️ 는 구간 경계(20·29·42·62·90)까지 거리가 ±3% 이내라는 표시이며 점수를 바꾸지 않는다.")


def private_notice(ctx: Any) -> str:
    if ctx.rules.f6_mode == "parameters":
        return ("비상장 배수는 상장사 PER과 직접 견줄 수 없다. 점수는 **밸류/매출 구간표**로 내고, "
                "**매출 성장과 자본 효율을 둘 다 채울 때만** 한 칸 올려 준다. 경계 표시는 붙이지 않는다.")
    return "비상장 배수는 상장사 PER과 직접 비교할 수 없다. 점수는 정성 예외(C-12)이며 경계 표시를 적용하지 않는다."


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
            "표에서는 엔진이 실제로 고른 칸에만 † 를 붙인다. 시가총액은 **PER과 EV/매출 두 곳 모두의 입력**이라 "
            "† 가 붙은 기업의 ⑥ 은 우리가 실측하지 않은 값 위에 서 있다(그렇다고 점수를 깎지는 않는다).")


def cash_definition_note(ctx: Any) -> str:
    """`현금` 열과 `순현금/순부채` 열은 다른 것을 센다. 같은 행에서 맞춰 볼 수 없다는 사실을 규칙 블록에서 읽어 적는다."""
    sep = ((ctx.rules.payload.get("policies", {}).get("f6") or {}).get("net_cash") or {}).get("scope_separation") or {}
    sites = {s.get("metric"): s for s in sep.get("sites", [])}
    cash, net = sites.get("cash", {}), sites.get("net_cash", {})
    # 규칙의 `site` 문구가 `F9 G3 런웨이`·`F6 P2 → EV 조정` 처럼 번호를 담고 있다. 표시할 때 이름으로 옮긴다.
    body = ("**현금 두 정의** — `현금` 열은 `cash` 관측(" + (cash.get("site") or "런웨이") + ", 질문 `" + (cash.get("question") or "") +
            "`)이고, `순현금/순부채` 열은 `net_cash` 관측(" + (net.get("site") or "EV 조정") + ", 질문 `" + (net.get("question") or "") +
            "`)으로 시장성 유가증권을 포함한다. **같은 행의 두 열은 서로 맞춰 볼 수 없다** — 순현금은 현금 열에서 차입을 뺀 값이 아니다"
            "(규칙 policies.f6.net_cash.scope_separation). 비상장·일부 기업은 원문 기준이 달라 제한현금 포함 여부도 다를 수 있다.")
    return rename_codes(body)


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
    """런웨이 계산에 무엇을 완충으로 넣는지.

    2026-09-17 FIX-67 재작성. 뜻은 그대로다 — 완충은 현금과 확정 미인출 여신뿐이고, 신용등급으로 추정한
    조달 여력은 넣지 않는다(`calc_f9._runway` 가 `undrawn_credit` 관측만 더한다).
    """
    has_credit = any(o["metric"] == "undrawn_credit" and o["status"] == "verified" for o in ctx.observations)
    return ("**런웨이를 잴 때 완충으로 세는 것은 현금과 조건이 확인된 확정 미인출 여신뿐이다.** "
            "신용등급이 좋아 더 빌릴 수 있을 것이라는 추정은 넣지 않는다 — 금액과 조건이 공시로 확인된 것만 센다."
            # 2026-09-17 FIX-69 M3: `확인된 여신은 런웨이에 들어가 있다` 가 tesla 에서 거짓이었다 —
            # 현금흐름이 흑자라 런웨이를 아예 계산하지 않는다. 전체를 싸잡지 않는다.
            + (" 다만 여신이 확인된 기업이라도 **현금흐름이 흑자로 판정되면 런웨이를 계산하지 않아** "
               "그 여신이 점수에 닿지 않는다." if has_credit else ""))


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


# 2026-09-17 FIX-72 M2: 칸 수를 세는 표가 두 곳에 있었고 한쪽이 인라인 인덱싱이라 값이 표를 벗어나면
# 방법 절 렌더가 IndexError 로 죽었다(`cap_steps=4`). **표는 한 벌만 두고 범위 밖은 숫자로 적는다.**
_COUNT_WORDS = ("", "한", "두", "세", "네", "다섯", "여섯", "일곱", "여덟", "아홉")


def _count(n: int) -> str:
    """칸 수를 세는 말. 표 범위를 벗어나면 숫자를 그대로 쓴다 — 죽지 않는다."""
    n = abs(int(n))
    return _COUNT_WORDS[n] if 0 < n < len(_COUNT_WORDS) else str(n)


def _steps(step: int) -> str:
    """감점 칸 수를 한국어 구로. 문장에 숫자를 박지 않고 계산 코드가 돌려준 값을 옮긴다.

    2026-09-17 FIX-71 R2: 전에는 0 일 때 `감점이 없고` 를 돌려줘 뒤에 `을 깎는다` 를 이어 붙이면
    문장이 깨졌다. **서술을 통째로** 돌려줘 이어 붙일 일이 없게 한다.
    """
    return "감점이 없다" if int(step) == 0 else f"{_count(step)} 칸을 깎는다"


def _band_text(bands: list[dict[str, Any]], unit: str = "%") -> str:
    """구간표를 문장으로. 숫자를 박지 않고 규칙의 `bands` 를 그대로 읽는다."""
    parts = []
    for b in bands:
        edge = b.get("upper", b.get("lower"))
        if edge is None:
            parts.append(f"그 밖은 {b['score']}")
        elif "upper" in b:
            parts.append(f"{edge:g}{unit} 미만이면 {b['score']}")
        else:
            parts.append(f"{edge:g}{unit} 이상이면 {b['score']}")
    return " · ".join(parts)


# 2026-09-17 FIX-74: 사다리·산식·조합표가 기계 계산인 것처럼 적혀 있었다. **그 입력이 전부 사람 판단이다.**
# 어느 항목이 어떤 방식인지 문장에 박지 않고 `judgments.json` 의 `kind` 에서 읽는다.
# `kind` 는 사람이 **무엇을 적었는지**를 말한다 — 점수 자체인지, 판정 입력인지.
JUDGMENT_ROLES = {
    "score": "점수 자체",
    "criteria": "기준마다 통과 여부",
    "grade": "동맹과 적대 등급",
    "matrix": "두 축의 판정",
    "gate_inputs": "관문 입력",
}
# 사람이 매긴 것을 엔진이 어떤 장치로 환산하는지. 규칙의 산식 자체는 아래 `mode` 색인에 있고
# 여기서는 **판단과 점수 사이에 무엇이 끼어 있는지**만 한 마디로 적는다.
CONVERSION_NOTES = {
    "F3": "엔진은 그 결과를 사다리에 태워 칸을 고른다",
    "F5": "엔진은 기본 3점에 동맹을 더하고 적대를 뺀다",
    "F7": "엔진은 그 조합을 표에서 찾아 칸을 고른다",
}
# 사람이 정하는 **판단 입력**이 각각 무엇을 묻는지. ⑨ 의 뜻은 `calc_f9` 가 그 값을 읽어 무엇을
# 가르는지에서 가져왔고 이 절의 관문 설명과 같은 말을 쓴다. ⑦ 의 두 축은 `factors.F7.matrix` 의
# `small|no` 꼴 키가 가리키는 것이다.
JUDGMENT_INPUT_NAMES = {
    # ⑨ 관문 입력 — 첫째 관문부터 넷째 관문 순서다.
    "bep_retreat": "흑자 전환 시점을 뒤로 미뤘는지",
    "operating_result_reviewed": "영업손익이 흑자인지 적자인지",
    "fcf_trend": "잉여현금흐름 추세가 안정인지 나빠지는지",
    "buffer_erosion": "현금 완충이 깎이고 있는지",
    "direction_A": "적자 폭이 줄고 있다는 첫째 판정",
    "direction_B": "적자 폭이 줄고 있다는 둘째 판정",
    "coverage_comparable": "계약 수입과 약정을 견줄 수 있는지",
    "fcf_not_disclosed_reason": "현금흐름을 공시하지 않은 사유",
    # ⑦ 조합표의 두 축.
    "funding_dependent_share": "조달 의존 고객 비중",
    "own_money_returns": "자기 자금 환류",
    # ③ 사다리의 기준 넷. 이름은 `calc_qual` 의 대기 사유와 `rules.f3_ladder` 의 주석이 쓰는 말이다.
    "imitation": "모방불가",
    "revenue_model": "수익모델",
    "acceleration": "가속도",
    "door_closed": "문이 닫혔는지",
}


def judgment_roles(ctx: Any) -> dict[str, list[str]]:
    """factor 별로 사람이 무엇을 적었는지 `judgments.json` 의 `kind` 를 세어 돌려준다.

    규칙의 `mode` 가 아니라 **실제 판단**을 본다. 규칙이 산식을 정해 두어도 그 산식에 들어가는 값을
    사람이 적었다면 그 점수는 사람 판단에서 나온 것이다.
    """
    out: dict[str, dict[str, int]] = {}
    for j in ctx.judgments:
        out.setdefault(j["factor"], {})
        out[j["factor"]][j["kind"]] = out[j["factor"]].get(j["kind"], 0) + 1
    return {f: sorted(k, key=lambda x: -out[f][x]) for f, k in out.items()}


def judgment_input_names(ctx: Any, factor: str) -> list[str]:
    """그 항목에서 사람이 정하는 입력이 무엇인지 `judgments.json` 의 `inputs` 키로 읽어 나열한다."""
    keys = {k for j in ctx.judgments if j["factor"] == factor for k in (j.get("inputs") or {})}
    # **이름표에 뜻이 있는 것만 내보낸다.** 없는 키를 그대로 쓰면 내부 코드가 화면에 실린다(FIX-73).
    order = list(JUDGMENT_INPUT_NAMES)
    return [JUDGMENT_INPUT_NAMES[k] for k in sorted(keys & set(order), key=order.index)]


def method_lines(ctx: Any) -> list[str]:
    """방법 절의 factor 설명.

    2026-09-17 FIX-67 전면 재작성 → FIX-68·69 정정. **문장이 규칙을 잘못 말하지 않게** 숫자와 칸 수를
    규칙·계산 코드에서 읽어 쓴다(FIX-69 L1). 결정 번호는 문장에서 빼 `관련 결정` 줄로 보낸다.
    """
    from .calc_f9 import G4_MISSING_DOWNGRADE_STEP, _coverage_step, _runway_step
    f9 = ctx.rules.payload["policies"]["f9"]
    f6p = ctx.rules.payload["policies"]["f6"]
    floor = f9_policy(ctx, "floor")
    bep = f9_policy(ctx, "g1_bep_retreat_score")
    keep = f9_policy(ctx, "g3_runway_keep_years")
    one_step = f9_policy(ctx, "g3_runway_one_step_years")
    cover = f9_policy(ctx, "g4_coverage_keep")
    tol = f6p["boundary_tolerance"]
    runway_mid = _runway_step((float(keep) + float(one_step)) / 2, ctx.rules)
    runway_deep = _runway_step(float(one_step) / 2, ctx.rules)
    coverage_short = _coverage_step(float(cover) / 2, ctx.rules)
    bands = f9["g1_bands_proposed"]
    deep = min(b["score"] for b in bands)
    mid = next((b for b in bands if b["score"] == deep + 1), None)
    shallow = next((b for b in bands if b["score"] == deep + 2), None)
    params = f6p["parameters"]
    # 2026-09-17 FIX-72 M1: 신규 상장 트랙은 P3 를 분기 대 전년 동기 분기로 잰다. 판정 기준도 규칙에서 읽는다.
    newly = f6p["tracks"].get("listed_newly") or {}
    newly_params = newly.get("parameters") or []
    newly_by_basis = "period_basis" in str(newly.get("select", ""))
    newly_names = [rc_name for pid, rc_name in F6_PARAM_LABELS.items() if pid in newly_params]
    p4 = f6p["p4"]
    nonop = next(c for c in p4["conditions"] if c["id"] == "nonop_share")
    # 비상장 승격 조건 — 실측만 받는 제한이 있는지 규칙에서 읽는다(FIX-69 H2).
    pc = f6p["private_correction"]
    growth_cond = next((c for c in pc["conditions"] if c["id"] == "arr_growth"), {})
    actual_only = "actual" in (growth_cond.get("accepted_kinds") or [])
    # C-16 이 판정 불가를 어떻게 처리하는지(FIX-69 H1).
    c16 = next((r["choice"] for r in ctx.run.get("decisions", []) if r["id"] == "C-16"), None)
    # 2026-09-17 FIX-71 R3: `한 칸` 이 박혀 있어 `_g4` 의 감점과 서로를 읽지 않았다. 코드에서 읽는다.
    c16_text = (_steps(G4_MISSING_DOWNGRADE_STEP) if c16 == "downgrade" else
                "그대로 둔다" if c16 == "hold" else "아직 정해지지 않아 점수를 만들지 않는다")
    # 2026-09-17 FIX-70: 첫째 관문에서 막힌 뒤 계산한 값을 점수에 넣는지(C-05). 선택을 읽어 쓴다.
    c05 = next((r["choice"] for r in ctx.run.get("decisions", []) if r["id"] == "C-05"), None)
    c05_text = ("**이번 실행은 그 값을 점수에 반영한다.**" if c05 == "apply" else
                "**이번 실행은 그 값을 기록만 하고 점수에 넣지 않는다.**" if c05 == "diagnose_only" else
                "**점수에 넣을지가 정해지지 않아 그 회사는 점수를 만들지 않는다.**")

    f6 = ([
        "**⑥ 가격은 지금 값이 비싼지를 본다.** 상장사는 아래 잣대를 각각 재서 더하고, 마지막에 입력을 "
        "믿을 수 있는지로 한 칸을 조정한다.",
        # 2026-09-17 FIX-74: 아홉 항목 가운데 사람 판단을 거치지 않는 것이 이 하나뿐이라는 사실이
        # 어디에도 적혀 있지 않았다. 판단 기록에 남은 비상장 점수를 이번 규칙이 쓰지 않는 것도 함께 적는다.
        "  - **아홉 항목 가운데 사람이 판단을 적지 않는 것은 이 항목 하나뿐이다.** 여기 들어가는 값은 모두 "
        "등록된 관측이고, 어느 회사가 어떤 잣대를 받는지도 관측의 기간 단위가 정한다."
        + (" 판단 기록에는 비상장 두 곳의 점수가 남아 있지만 **이번 규칙은 그 점수를 쓰지 않고 관측에서 "
           "다시 계산한다.**" if ctx.rules.f6_mode == "parameters" and any(
               j["factor"] == "F6" for j in ctx.judgments) else ""),
        f"  - **PER** — 시가총액을 최근 1년 순이익으로 나눈다. {_band_text(params['P1']['bands'], '배')}.",
        f"  - **EV/매출** — 시가총액에서 순현금을 뺀 값을 최근 1년 매출로 나눈다. {_band_text(params['P2']['bands'], '배')}.",
        f"  - **매출 성장** — 최근 1년 매출을 그 전 1년과 견준다. "
        + " · ".join(f"{b['lower']:.0%} 이상이면 {b['score']}" if b.get("lower") is not None else f"그 아래는 {b['score']}"
                     for b in params["P3"]["bands"]) + ". "
        + ("**아래 신규 상장 트랙에서는 1년치가 없어 가장 최근 분기를 전년 같은 분기와 견준다.** "
           "구간은 같은 것을 쓴다." if "P3" in newly_params else ""),
        f"  - **입력 신뢰도** — 앞의 것들을 더한 값에서 한 칸을 더 깎는 자리다. **영업외 손익의 크기가** 세전이익의 "
        f"{float(nonop['threshold']):.0%} **이상**이거나(마이너스 쪽으로 큰 경우도 걸린다), 최근 1년이 아닌 기간"
        "(회계연도 값이나 전년 동기 대비 분기 값)을 썼거나, 비교할 전년이 없거나, 자료가 너무 오래됐을 때 걸린다."
        + (f" 여러 개가 걸려도 {_count(p4['cap_steps'])} 칸까지만 깎는다."
           if int(p4["cap_steps"]) else " 다만 이번 규칙에서는 이 자리로 깎지 않는다."),
        "  - **다만 상장한 지 얼마 안 돼 전년 1년치 매출을 복원할 수 없는 회사는 "
        + "·".join(newly_names) + " 둘로만 소계를 낸다.** PER 은 재지 않고, 매출 성장은 앞서 적은 대로 "
        "분기끼리 견준다. 이번 14개사 중 한 곳이 그 경우다."
        + (" 어느 회사가 여기 드는지는 상장 시점이 아니라 **그 회사 매출 관측이 어느 기간 단위인지**로 가른다."
           if newly_by_basis else ""),
        f"  - 구간 경계에서 {tol:.0%} 안에 든 값에는 표시를 달지만 **점수는 바꾸지 않는다.**",
        # 2026-09-17 FIX-71 R1: 한 문단 안에서 `매출` 이 세 가지를 가리켰다(P2 의 매출 · P3 의 매출 · ARR).
        "  - **비상장사는 다르게 본다.** 기업가치를 **연 매출**로 나눈 배수 하나로 점수를 내고, "
        "**연 매출 성장**과 자본 효율이 **둘 다** 좋을 때만 한 칸 올려 준다. "
        + ("여기서 성장을 재는 값은 매출액이 아니라 **연간 반복 매출(ARR)** 이고, **실제로 거둔 ARR 만 센다** — "
           "최근 실적을 열두 달로 늘려 잡은 런레이트는 받지 않아, 수치가 기준을 넘어도 그것이 런레이트면 "
           "올려 주지 않는다. " if actual_only else " ")
        + "이 배수는 상장사의 PER과 직접 견줄 수 없는 수치다.",
    ] if ctx.rules.f6_mode == "parameters" else [
        "**⑥ 가격은 지금 값이 비싼지를 본다.** 상장사는 예상 PER 구간으로, 비상장사는 배수를 계산하되 점수는 정성 예외로 정한다.",
    ])

    g1 = [
        "**⑨ 적자 깊이는 관문 네 개를 차례로 지난다.** 앞 관문의 결과에 따라 뒤 관문이 달라진다.",
        "  - 관문을 지나면 다음 관문으로 간다. 관문마다 깎인 것을 더한 값이 이 항목의 점수다.",
        # 2026-09-17 FIX-74: 관문을 수치로만 지나는 것처럼 읽혔다. 관문마다 사람이 정한 값이 함께 들어간다.
        "  - **이 항목은 관측 수치만으로 나오지 않는다.** 재무 수치와 함께 **사람이 정한 값이 관문마다 들어간다.** "
        "판단 기록에 등록된 것은 " + " · ".join(f"`{x}`" for x in judgment_input_names(ctx, "F9")) + " 다. "
        "그래서 아래 구간과 칸 수는 기계가 정하지만, **그 구간에 들어갈 값 가운데 일부는 사람이 정한 것**이다.",
        "  - **앞 관문에서 잴 것이 없으면 뒤 관문을 건너뛴다.** 기업 카드에는 `생략` 으로 나온다. "
        "현금흐름을 공시하지 않아 한 해 소진액을 알 수 없으면 런웨이를 계산할 방법이 없는 경우가 그것이다.",
        "  - **첫째 관문은 본업이다.** 최근 1년 영업손익으로 판정한다.",
        f"    - 회사가 흑자 전환 시점을 뒤로 미뤘다고 밝히면 이 항목은 최저점 {bep} 를 준다. 채점규칙 원문이 손실 폭과 "
        "**무관한 독립 조건**으로 적어 놓았다. 그래서 손실이 얕아도, 영업이익이 나고 있어도 최저점이 된다. "
        "**이 처리가 맞는지는 2026년 11월에 다시 본다.** 이번 14개사 중 이 조항이 걸린 회사는 없다.",
        "    - 다만 비상장사가 영업손익을 아예 공시하지 않으면 이 조항을 쓰지 않고 비상장사용 경로로 보낸다. "
        "공시 의무가 없어 못 본 것을 적자로 셀 수는 없기 때문이다.",
        "    - 그 밖에는 영업손익률로 나눈다. "
        + (f"{shallow['min_margin']:.0%} 까지의 손실은 {shallow['score']}, " if shallow else "")
        + (f"{mid['min_margin']:.0%} 까지는 {mid['score']}, " if mid else "")
        + f"그보다 깊으면 {deep} 다. 영업이익이 나면 이 관문을 통과한다.",
        f"  - **둘째 관문은 현금이다.** 최근 1년 잉여현금흐름을 본다. 흑자이고 추세가 안정이면 "
        f"{_steps(f9['g2_fcf_positive_stable'])}. 흑자라도 나빠지고 있으면 {_steps(f9['g2_fcf_positive_deteriorating'])}. "
        f"마이너스면 {_steps(f9['g2_fcf_negative'])}. 비상장사가 공시하지 않으면 "
        f"{_steps(f9['g2_private_not_disclosed'])}.",
        f"  - **셋째 관문은 런웨이다.** 현금과 조건이 확인된 확정 미인출 여신을 더해 한 해 소진액으로 나눈다. "
        f"{keep:g}년 이상이면 {_steps(0)}. {one_step:g}년 이상 {keep:g}년 미만이면 {_steps(runway_mid)}. "
        f"{one_step:g}년 밑이면 {_steps(runway_deep)}. 여기서도 경계 {tol:.0%} 안은 표시만 한다. "
        "**앞 관문에서 현금흐름이 흑자로 판정되면 이 관문에 닿지 않는다** — 버틸 기간을 물을 일이 없기 때문이다.",
        f"  - **넷째 관문은 약정 커버리지다.** 계약으로 확보한 수입을 갚기로 한 약정으로 나눈다.",
        f"    - 숫자가 둘 다 있으면 {cover:g}배 이상일 때 {_steps(0)}. 그 아래면 {_steps(coverage_short)}.",
        "    - 기간이나 범위가 서로 달라 견줄 수 없으면 숫자를 만들지 않는다.",
        f"    - **회사가 공시하지 않았다는 것이 확인되면** 숫자가 없어도 {c16_text}. 이 처리는 아직 확정되지 않은 "
        "규칙이고 이번 실행에서 고른 선택이다.",
        "    - 다만 **우리가 수집하지 못했거나 미공시인지 확인되지 않은 경우**는 여기로 보내지 않고 자료 대기로 "
        "남긴다. 수집 공백을 기업의 위험으로 바꾸지 않기 위해서다.",
        f"  - 이 항목의 최저점은 {floor} 이며 그보다 더 내려가지 않는다.",
        f"    - 적자로 판정돼도 **적자 폭이 줄고 있다는 판정이 둘 다 서면 {_count(f9['g1_direction_relief_step'])} 칸을 "
        f"되돌려 준다**(되돌려도 {f9['g1_direction_relief_cap']} 보다 위로는 못 간다). 이번 실행에서는 그 판정이 "
        "서지 않아 점수가 바뀐 회사가 없다. 기업 카드에는 `방향 완화` 로 나온다.",
        "  - **첫째 관문에서 막힌 회사는 둘째 관문을 건너뛰고 셋째·넷째만 따로 계산한다.** 본업이 이미 "
        "적자로 판정됐으므로 현금흐름의 방향을 다시 묻지 않는다. 기업 카드에는 `진단` 으로 나온다. "
        + c05_text
        + " 기록만 남기는 쪽도 선택지에 있고 **어느 쪽이 맞는지는 아직 정해지지 않았다.** "
        "다만 이미 최저점이면 더 내려갈 곳이 없어 계산하지 않는다.",
        "  - **아직 정하지 못한 것이 셋이다.** 수치가 정확히 0 일 때 어떻게 볼지, 현금 완충이 깎이는 속도를 "
        "어떻게 셀지, 현금흐름 추세의 안정과 악화를 기계가 어떻게 가를지다.",
    ]

    # 2026-09-17 FIX-74: 사다리·산식·조합표를 기계 계산처럼 적고 ①④⑧ 만 판단인 것처럼 갈라 놓았다.
    # **실제로는 일곱이 전부 사람 판단에서 나온다.** 어느 항목이 어느 쪽인지 `kind` 를 세어 읽는다.
    roles = judgment_roles(ctx)
    # ⑥ 은 판단 기록에 점수가 남아 있어도 이번 규칙이 관측에서 다시 계산한다(`compute_private` 가
    # 그 판단을 무시하고 경고만 남긴다). 판단 파일에 있다는 것과 그 점수가 쓰였다는 것은 다르다.
    ignored = {"F6"} if ctx.rules.f6_mode == "parameters" else set()
    judged = [f for f in FACTOR_LABELS if f in roles and f not in ignored and f != "F9"]
    plain = [f for f in judged if roles[f][0] == "score" and f != "F2"]
    converted = [(f, roles[f][0]) for f in judged if roles[f][0] != "score"]

    def _names(ids: list[str]) -> str:
        return " · ".join(FACTOR_LABELS[f] for f in ids)

    def carried_note(fid: str) -> str:
        """같은 항목 안에서 판정 입력이 남지 않아 숫자만 넘어온 회사가 있으면 그 수를 적는다."""
        n = sum(1 for j in ctx.judgments if j["factor"] == fid and j["kind"] == "score")
        return (f" 다만 {_count(n)} 곳은 그 판정이 남아 있지 않아 **점수 숫자만 넘어왔고** 엔진이 "
                "다시 환산하지 못한다." if n else "")

    rest = [
        f"**{_names(judged)} {_count(len(judged))} 항목은 모두 사람 판단에서 나온다.** 판단 기록을 세어 보면 "
        "이 항목들은 14개사 전부가 사람이 적은 판단을 입력으로 갖는다. **사다리·산식·조합표는 사람이 매긴 것을 "
        "정해진 표로 환산하는 장치이지 판단을 대신하는 것이 아니다.** 그래서 이 항목들은 모두 점수보다 근거 "
        "문장을 읽어야 한다. 엔진이 무엇을 했는지는 이렇다.",
    ] + ([f"  - **{_names(plain)}** — 사람이 **{JUDGMENT_ROLES['score']}**를 적는다. 환산할 산식이 아예 없어 "
          "적힌 점수가 그대로 이 항목의 점수가 된다."] if plain else []) + [
        f"  - **{FACTOR_LABELS[f]}** — 사람이 **{fix_josa(JUDGMENT_ROLES[kind], '', '을')}** 정하고"
        + (f"({' · '.join(judgment_input_names(ctx, f))})" if len(judgment_input_names(ctx, f)) > 1 else "")
        + f", {CONVERSION_NOTES[f]}." + carried_note(f)
        for f, kind in converted if f in CONVERSION_NOTES
    ] + [
        # 2026-09-17 FIX-71 N3: 규칙이 정한 방식을 적었으나 **이번 실행에서 그 방식으로 매겨진 회사가 없다.**
        # 둘이 다르면 둘 다 드러나야 한다.
        "**② 게임체인저는 이번 실행에서 계산하지 않았다.** 규칙은 조건을 몇 개 통과했는지 세어 점수로 바꾸도록 "
        f"정해 두었고({', '.join(f'{k}개 {v}점' for k, v in sorted(ctx.rules.factor('F2')['path_mapping'].items()))}, "
        "최고점은 통과 수만으로 닿지 않고 세대 격차를 따로 채워야 한다), **그런데 어느 경로를 통과했는지가 "
        "기준선에서 넘어오지 않아 14개사 모두 기준선 점수를 그대로 쓴다.** 카드의 ② 점수를 보고 통과 수를 "
        "거꾸로 셈하면 안 된다.",
        "**모르는 값을 0 으로 바꾸지 않는다.** 자료가 없으면 그 항목은 점수를 만들지 않고 대기 상태로 남으며, "
        "그 회사는 공식 순위에서 빠진다. **예외가 하나 있다** — 런웨이를 잴 때 미인출 여신이 확인되지 않으면 "
        "0 으로 센다. 완충은 확인된 것만 세기로 했기 때문이고, 없는 여신을 있다고 보지 않으려는 처리다.",
    ]
    return f6 + g1 + rest


def conflict_lines(ctx: Any) -> list[str]:
    """이해상충과 제3자 재검토 약속. 2026-09-16 FIX-55 2단계(4차 리뷰 A 분담): 재검토 대상·시점·발동 조건이 산출물 어디에도 없었다.

    문장을 손으로 적지 않고 출처·규칙에서 읽는다 — 규칙이 바뀌면 이 절도 따라 바뀌어야 한다.
    """
    out = []
    # 2026-09-16 FIX-56 1단계(5차 리뷰 B): 문구 집합의 크기를 세어 문구가 같은 두 출처가 하나로 합쳐졌다(6건 → 5종).
    # 읽는 사람이 세고 싶은 것은 **표기된 출처의 수**이므로 출처 건수로 센다.
    flagged = [s for s in ctx.sources.get("items", []) if s.get("conflict_of_interest")]
    if flagged:
        out.append(f"**이해상충** — 이 채점표는 Anthropic 이 만든 Claude 가 작성했고 Anthropic 이 채점 대상에 들어 있다. 이해상충이 표기된 출처가 "
                   f"{len(flagged)}건이고 문장은 References 의 각 출처 줄에 있다. 비상장 2사의 수치는 회사 자체 발표(이해당사자 1차 자료)에서 온다.")
    # 2026-09-16 FIX-56 2단계(5차 리뷰 D low): 전에는 `비 Claude` 가 든 긴장을 통째로 세어 **권장까지 약속으로** 읽혔다.
    # 이제 긴장이 스스로 선언한 갈래(third_party_recheck)를 읽는다.
    tensions = sorted((ctx.rules.payload.get("open_tensions") or []), key=lambda x: x["id"])
    by_kind: dict[str, list[dict[str, Any]]] = {}
    # 2026-09-17 FIX-62: 해소된 긴장은 아직 남은 약속이 아니다. 건수에서 빼되 이행된 사실은 아래에 따로 적는다.
    done = [t for t in tensions if t.get("status") == "resolved"]
    for t in tensions:
        kind = t.get("third_party_recheck")
        if kind and t.get("status") != "resolved":
            by_kind.setdefault(kind, []).append(t)

    def _ids(items: list[dict[str, Any]], scope_key: str | None = None) -> str:
        return " · ".join(f"{t['id']}({', '.join(t.get(scope_key) or t['judgment_ids'])}, {t['recheck_at']})" for t in items)

    committed = by_kind.get("committed") or []
    if committed:
        out.append(f"**제3자 재검토 약속**(채점규칙 384행) — 비 Claude 세션 재판정이 **확정**된 긴장 {len(committed)}건: {_ids(committed)}.")
    partial = by_kind.get("partial") or []
    if partial:
        out.append(f"  - **일부만 확정** {len(partial)}건 — {_ids(partial, 'third_party_scope')} 만 비 Claude 세션이 본다. "
                   "같은 긴장의 나머지 판단은 재채점 때 판단자가 본다.")
    recommended = by_kind.get("recommended") or []
    if recommended:
        out.append(f"  - **권장일 뿐 약속이 아닌 것** {len(recommended)}건 — {_ids(recommended)}. "
                   "규칙이 `비 Claude 세션 권장` 으로 적은 자리이고 재판정자를 정해 두지 않았다.")
    if done:
        out.append(f"  - **이미 해소된 긴장** {len(done)}건 — " +
                   " · ".join(f"{t['id']}({', '.join(t['judgment_ids'])}, {t['resolved_at']})" for t in done) +
                   ". 재판정이 끝나 남은 약속에서 뺐다. 결론은 규칙 `open_tensions` 의 `resolution` 에 있다.")
    c03 = next((d for d in ctx.rules.payload.get("decisions", []) if d["id"] == "C-03"), None)
    recheck = (c03 or {}).get("pending_recheck") or {}
    if recheck:
        out.append(f"  - anthropic ②5 재검토 — {recheck.get('what', '')} 시점 {recheck.get('when', '')} · 발동 조건 `{recheck.get('trigger', '')}`"
                   "(C-03 pending_recheck). 이번 실행은 이 판단을 재판정하지 않았다.")
    return out


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
        # 2026-09-17 FIX-67: 내부 상태값(`resolved_stored_was_right`)과 번호를 그대로 찍던 것을 풀어 쓴다.
        out.append("**원자료 표의 `영업외 비중` 열은 점수에 쓰지 않는다.** 그 열은 기준선에서 넘어온 값이고, "
                   "입력 신뢰도 판정은 원자료에서 다시 계산한 값(세전이익에서 영업이익을 뺀 뒤 세전이익으로 나눈 값)을 쓴다. "
                   f"두 값이 다른 회사가 있다. 설명된 차이: {explained} 설명 못 한 차이: {unexplained}")
    nc = f6.get("net_cash") or {}
    if nc:
        questions = nc.get("open_questions") or []
        out.append("**순현금의 정의가 아직 확정되지 않았다.** 지금은 기준선 값에서 거꾸로 맞춰 세운 작업용 정의"
                   "(현금과 시장성 유가증권을 더하고 총차입금과 리스부채를 뺀 값)를 쓴다. 확정 정의가 나오면 "
                   f"⑥ 의 EV/매출을 다시 계산해야 한다. 아직 답하지 못한 질문이 {len(questions)}건이다.")
        for q in questions:
            # 취소한 문장은 빼고, 자를 때 강조·코드 표시가 반쯤 남지 않게 기호를 걷어 낸 뒤 자른다.
            q = re.sub(r"~~.*?~~\s*", "", q).replace("**", "").replace("`", "").strip()
            out.append("  - " + (q if len(q) <= 160 else q[:157] + "…"))
    out += conflict_lines(ctx)
    return out
