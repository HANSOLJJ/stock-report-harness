# 초안(render_md)과 HTML(render_html)이 함께 쓰는 표시 규칙 — 한쪽만 고쳐져 두 산출물이 갈리는 것을 구조적으로 막는다
"""2026-09-15 FIX-54 1단계 S3. FIX-53 에서 초안 렌더러만 고쳐 HTML 이 통째로 뒤처졌다(3차 리뷰 D).

여기 함수는 **마크업을 모른다.** 문장은 초안과 같은 인라인 마크다운(`**굵게**`·`~~취소선~~`·백틱)으로 돌려주고
HTML 렌더러는 `inline_html` 로 바꿔 쓴다. 표시 규칙을 고칠 때는 이 파일만 고친다.
"""
from __future__ import annotations

import html as html_lib
import re
from pathlib import Path
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
    "computed": "산식 계산", "manual": "사람 판단", "carried": "앞서 매긴 점수만",
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
    "legacy_unverified": "사용자 원본 값·다시 확인 안 함", "not_disclosed_confirmed": "확인된 미공시",
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


# 2026-09-18 FIX-79 S2: 본문이 결정 번호(`C-03`)를 칩·링크로 걸어 두었는데, 사용자가 사전을 열어 보고
# 뜻이 읽히지 않는다고 했다. 결정 기록은 감사 기록으로 옮기고 **본문 문장은 번호 없이 읽히게** 한다.
# 번호를 그냥 지우면 문장이 끊긴다 — 번호가 문장 안에서 맡은 뜻을 말로 옮긴 뒤 남은 것만 뗀다.
# `TEN-RC-03` 의 꼬리를 번호로 잡지 않도록 앞에 영문자·붙임표가 없는 것만 본다.
_C = r"(?<![A-Za-z-])"
DECISION_PHRASES = [
    (_C + r"C-03 확정 전 (5점 )?잣대", r"② 기준이 확정되기 전 \1잣대"),
    (_C + r"C-03 확정 기준", "확정된 ② 기준"),
    (_C + r"C-03 확정\(", "확정된 ② 기준("),
    (r"\(" + _C + r"C-03 이 재검토 대기로 걸어 둔 항목이다\)", "(② 5점 기준을 정한 결정이 재검토 대기로 걸어 둔 항목이다)"),
    (_C + r"C-03\(경로 판정\)", "경로 판정"),
    (_C + r"C-09\(매트릭스 입력\)가", "매트릭스 입력이"),
    (_C + r"C-09\(매트릭스 입력\)", "매트릭스 입력"),
    (r"\((F\d)·C-\d+\)", r"(\1)"),
    # `C-13` 은 이 자리들에서 결정이 아니라 **독립 검토 세션의 이름**이다.
    (_C + r"C-13\s+(이|에서)(?=\s)", r"독립 검토 세션\1"),
    (_C + r"C-13(?![/\w-])", "독립 검토 세션"),
    (_C + r"C-16 실행 결정으로", "확인된 미공시 처리 결정으로"),
    (_C + r"C-16 이 ", "확인된 미공시 처리 결정이 "),
    (_C + r"C-06 `?(?:제안된 손실률 구간 적용|proposed_v15_boundaries)`? 로", "제안된 손실률 구간을 적용해"),
    (_C + r"C-06 재척도 전", "손실률 구간 재척도 전"),
    (r"사용자가 " + _C + r"C-29 로 ", "사용자가 "),
    (r"\(" + _C + r"C-20 비상장 경로\)", "(비상장 경로)"),
    (_C + r"C-20 비상장", "비상장"),
    (r"\(" + _C + r"C-17 은 셋을 따로 기록하라는 권고이고, ", "(셋을 따로 기록하라는 권고가 있지만 "),
    (r"이라 " + _C + r"C-07 로 이번 실행 미적용", "이라 수주잔고 기준과 달라 이번 실행에는 쓰지 않았다"),
    (_C + r"C-\d+ — ", ""),
    (r"\s*\(" + _C + r"C-\d+\)", ""),
    (_C + r"C-\d+\s*[:：]\s*", ""),
]
_DECISION_RES = [(re.compile(a), b) for a, b in DECISION_PHRASES]
# 뒤에 `/` 가 붙으면 경로 앞머리(`C-13/validation/…`)라 번호가 아니다.
_LEFTOVER_C = re.compile(_C + r"C-\d+(?![/\w-])\s*")


# 2026-09-18 FIX-79: 관측 ID(`amazon.offbalance_B.obsreg25`)가 근거 문장에 그대로 찍혔다. 무엇인지는 문장이
# 이미 말하므로(`실측 $267.3B`) 본문에서는 뗀다. ID 는 감사 기록의 작업 이력으로 간다.
# 셋째 조각에 숫자가 있는 것만 잡는다 — `data.sec.gov` 같은 도메인과 구별된다. 가운데가 `F5` 인 것은
# 판단 기록 식별자(`openai.F5.impl48`)라 추적용으로 남긴다(FIX-77).
OBS_ID_RE = re.compile(r"(?<![\w./-])[a-z][a-z0-9-]*\.(?!F\d\.)[A-Za-z][A-Za-z_]*\.[a-z]*\d+[a-z0-9]*(?![\w.])")


def strip_obs_ids(text: str) -> str:
    """관측 ID 를 떼고 남은 괄호·구분자를 정리한다."""
    if "." not in text or not OBS_ID_RE.search(text):
        return text
    out = re.sub(r"\s*—\s*" + OBS_ID_RE.pattern + r"\s+basis\.\w+", "", text)
    out = OBS_ID_RE.sub("\x00", out)
    out = re.sub(r"\x00(\s*[·,]\s*\x00)*", "\x00", out)          # 연달아 붙은 ID 는 하나로
    out = re.sub(r"\s*,\s*\x00\s*—\s*", " — ", out)              # (기간, ID — 설명)
    out = re.sub(r"\(\x00\)", "", out)                             # (ID)
    out = re.sub(r"\(\x00\s*[,·—]\s*", "(", out)                   # (ID, 검증 완료 …) · (ID — …)
    out = re.sub(r"\s*[,·]\s*\x00(?=\))", "", out)                 # (…, ID)
    out = out.replace("\x00", "")
    out = re.sub(r"\(\s*\)", "", out)
    return re.sub(r"[ \t]{2,}", " ", out)


def strip_decision_codes(text: str) -> str:
    """본문 문장에서 결정 번호를 걷는다. 뜻을 말로 옮긴 뒤 남은 번호만 뗀다."""
    if "C-" not in text:
        return text
    for rx, rep in _DECISION_RES:
        text = rx.sub(rep, text)
    return _LEFTOVER_C.sub("", text)


# 2026-09-18 FIX-80 S3: 긴장 번호(`TEN-RC-02`)·리뷰 기록(`2차 리뷰 C RC-04`·`체크리스트 Q03`·`AGENTS.md`)·
# 행 번호(`채점규칙 22행`)·판단 ID(`anthropic.F2`)가 본문에 남았다. 읽는 사람에게 필요한 것은 **무엇을 언제
# 다시 보는지**와 **어느 문서에 있는지**다. 번호는 감사 기록으로 보내고 본문에서는 말로 옮기거나 뗀다.
# 회사 이름은 렌더러가 실행 자료에서 채운다(`set_company_names`).
COMPANY_NAMES: dict[str, str] = {}
FACTOR_MARKS_BY_ID = {f"F{i}": "①②③④⑤⑥⑦⑧⑨"[i - 1] for i in range(1, 10)}
JUDGMENT_ID_RE = re.compile(r"(?<![\w./-])([a-z][a-z0-9-]*)\.(F[1-9])(?:\.[a-z0-9]+)?(?![\w.])")
INTERNAL_REF_PHRASES = [
    # 번호만 굵게 쓴 자리(`재검토는 **TEN-RA5-01**(2026-11 · …`). 번호를 떼면 빈 강조가 남아 짝이 깨진다.
    (r"재검토는 \*\*TEN-[A-Z0-9-]+\*\*\s*\((\d{4}-\d{2}) · ", r"\1 에 다시 본다("),
    (r"\*\*TEN-[A-Z0-9-]+\*\*\s*", ""),
    (r"재검토는 TEN-[A-Z0-9-]+ \((\d{4}-\d{2})\)", r"\1 에 다시 본다"),
    (r"재검토는 TEN-[A-Z0-9-]+ \((\d{4}-\d{2}) · ", r"\1 에 다시 본다("),
    (r"TEN-[A-Z0-9-]+ 로 (\d{4}-\d{2}) 재검토한다", r"\1 에 다시 본다"),
    (r"\(체크리스트 Q\d+ · \d+차 리뷰 [A-Z] RC-\d+\)", ""),
    (r"\(\d+차 리뷰 [A-Z] RC-\d+ · AGENTS\.md 리뷰 범위 — ", "("),
    # 리뷰 기록 꼬리는 그 모양대로만 잡는다 — 다음 마침표까지 넘기면 강조의 여는 기호를 먹는다.
    (r"\s*obsreg \d+차 리뷰 [A-Z](?: 분담)?\([^)]*\)(?:\s+(?:medium|low|high))?(?:\s*·\s*\d+차 재판정 Q\d+)?\.?", ""),
    (r"\[\s*정정\s*·?\s*\]\s*", ""),
    (r"\s*·?\s*\d+차 재판정 Q\d+\.?", ""),
    (r"\d+차 리뷰 [A-Z] RC-\d+\s*[·,]?\s*", ""),
    (r"체크리스트 Q\d+\s*[·,]?\s*", ""),
    (r"AGENTS\.md 리뷰 범위\s*—?\s*", ""),
    (r"TEN-[A-Z0-9-]+\s*", ""),
    # 행 번호 — 문서 이름은 남기고 몇째 줄인지만 뗀다.
    (r"(?<=[^\s(\d·~,])\s*\d+(?:[·~,]\d+)*행", ""),
    (r"\(\s*\d+(?:[·~,]\d+)*행\s*\)", ""),
    (r"(?<=· )\d+(?:[·~,]\d+)*행\s*", ""),
    (r"\(IMPL-\d+ 승계\)", ""),
    (r"근거는 승계", "근거는 앞서 매긴 것"),
    (r"승계 근거란", "앞서 매긴 근거란"),
    (r"은 승계 그대로다", "은 앞서 매긴 그대로다"),
    (r"을 승계했고", "을 그대로 이어받았고"),
    # 2026-09-18 FIX-81: 정정 꼬리는 태그만 떼고 **정정된 현재 내용**을 남긴다. 원문은 감사 기록의 `정정 이력` 에 있다.
    (r"\[정정 \d{4}-\d{2}-\d{2} FIX-\d+\]\s*", ""),
    (r"\[FIX-\d+(?: \d단계)? (?=[^\]]{6,}\])", "["),
    # 커밋 해시(글자가 하나는 섞인 7자리)와 보존 경로. 근거가 어디 보존됐는지는 감사 기록의 이력으로 간다.
    (r"`((?=[0-9a-f]*[a-f])[0-9a-f]{7}:[\w./-]+)`", r"\1"),   # 코드 표기로 감싼 보존 경로는 먼저 벗긴다
    (r"보존 원문 독립 검토 세션 (?=[0-9a-f]*[a-f])[0-9a-f]{7}:[\w./-]+ 에서", "보존 원문에서"),
    (r"\(\s*(?=[0-9a-f]*[a-f])[0-9a-f]{7}:[\w./-]+\s*\)", ""),
    (r"(?<=\()\s*(?=[0-9a-f]*[a-f])[0-9a-f]{7}:[\w./-]+\s*,\s*", ""),
    (r"\s*,\s*(?=[0-9a-f]*[a-f])[0-9a-f]{7}(?=\))", ""),
    (r"\(\s*(?=[0-9a-f]*[a-f])[0-9a-f]{7}\s*\)", ""),
    # 앞서 매긴 것을 이어받았다는 말은 FIX-77·78 의 표기와 맞춘다.
    (r"는 승계 그대로", "는 앞서 매긴 그대로"),
]
_INTERNAL_RES = [(re.compile(a), b) for a, b in INTERNAL_REF_PHRASES]
# 감사 기록 이력에 모을 조각 — 본문에서 떼거나 말로 옮긴 것들이다.
INTERNAL_REF_RE = re.compile(
    r"TEN-[A-Z0-9-]+|\d+차 리뷰 [A-Z](?: RC-\d+)?|체크리스트 Q\d+|AGENTS\.md 리뷰 범위"
    r"|(?:채점규칙|채점표(?:_v1\.5\.md)?|별표 [A-Z]|HANDOVER)\s*\d+(?:[·~,]\d+)*행"
    r"|(?<![\w./-])[a-z][a-z0-9-]*\.F[1-9](?:\.[a-z0-9]+)?(?![\w.])"
    r"|\b(?=[0-9a-f]*[a-f])[0-9a-f]{7}(?::[\w./-]+)?\b")


def set_company_names(companies: dict[str, dict[str, Any]]) -> None:
    COMPANY_NAMES.clear()
    COMPANY_NAMES.update({cid: str(c.get("display_name") or cid).split(" / ")[0] for cid, c in companies.items()})


def judgment_label(jid_match: re.Match[str]) -> str:
    """`anthropic.F2` → `Anthropic ②`. 회사 이름표가 비어 있으면 그대로 둔다."""
    cid, fid = jid_match.group(1), jid_match.group(2)
    if cid not in COMPANY_NAMES:
        return jid_match.group(0)
    return f"{COMPANY_NAMES[cid]} {FACTOR_MARKS_BY_ID[fid]}"


def strip_internal_refs(text: str) -> str:
    """긴장·리뷰·행 번호·판단 ID 를 본문 문장에서 걷거나 말로 옮긴다."""
    if not any(k in text for k in ("TEN-", "리뷰", "체크리스트", "행", "AGENTS", ".F", "승계", "HANDOVER", "FIX-", "(", ":")):
        return text
    text = source_names(text)
    for rx, rp in _INTERNAL_RES:
        text = rx.sub(rp, text)
    text = JUDGMENT_ID_RE.sub(judgment_label, text)
    text = re.sub(r"\(\s*—\s*", "(", text)            # 괄호 첫머리의 리뷰 기록을 떼면 줄표만 남는다
    text = re.sub(r"\(\s*\)", "", text)
    text = re.sub(r"\(\s*([^()]*?)\s+\)", r"(\1)", text)
    return re.sub(r"[ \t]{2,}", " ", text)


def inline_html(text: str) -> str:
    """이스케이프한 뒤 백틱·`~~`·`**` 만 태그로 바꾼다. 나머지 마크다운 기호는 글자 그대로 둔다."""
    text = strip_internal_refs(strip_obs_ids(strip_decision_codes(str(text))))
    out = html_lib.escape(rename_codes(str(text)), quote=True)
    out = re.sub(r"`([^`]+)`", r"<code>\1</code>", out)
    out = re.sub(r"~~(.+?)~~", r"<del>\1</del>", out)
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", out)


def struck(text: str) -> str:
    """취소선. 본문에 `~` 가 있으면 마크다운 취소선이 깨지므로 표시어로 대신한다."""
    return f"~~{text}~~ (대체됨)" if "~" not in text else f"(대체됨) {text}"


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


def card_evidence_note(baseline_id: str, html: bool = False) -> str:
    # 2026-09-18 FIX-80 S2: HTML 카드는 관측에서 계산한 항목의 옛 참고 서술을 싣지 않는다(감사 기록으로 보냈다).
    # 초안은 리뷰어가 대조하는 문서라 그대로 싣는다 — 안내문도 둘을 갈라 말한다.
    ref = ("관측에서 계산한 항목에는 옛 참고 서술을 싣지 않는다 — 산식과 사유가 점수 근거이고, 옛 서술은 감사 기록에 있다."
           if html else "관측에서 계산한 항목은 기준선 서술을 참고로만 보인다.")
    return (f"근거 불릿은 이번 실행 결과에 연결된 판단의 근거란을 먼저 보인다. 사용자가 앞서 매긴 판단은 기준선 {baseline_id} "
            "문면에 이번 실행이 붙인 대체 표시·정정이 함께 있고, 이번 실행에서 다시 매긴 판단은 새 근거 뒤에 대체된 옛 판단을 "
            f"취소선으로 둔다. {ref} 카드의 한 줄 요약은 기준선 원문이며 이번 실행에서 재검증하지 않았다.")


def g4_incompatible(observations: list[dict[str, Any]], cid: str) -> bool:
    return any(o["company_id"] == cid and o["metric"] in ("contracted_revenue", "offbalance_B") and o["status"] == "incompatible_basis"
               for o in observations)


# ------------------------------------------------------------------ 작업 메모 분리
# 2026-09-17 FIX-77: 기업 카드의 근거 문장에 **작업 메모**가 그대로 실렸다(사용자 지적).
# `[FIX-52 재척도 2026-09-15]` 처럼 언제 어느 과제로 표기가 바뀌었는지는 근거가 아니라 이력이다.
# 사용자가 고른 것은 `메모만 걷어내기` — 근거의 내용과 출처는 남기고 작업 표기만 내린다.
# 내린 것은 지우지 않고 감사 기록으로 보낸다.
_WORK_TOKEN = (r"FIX-\d+|OBS-[A-Z0-9-]+|G\d-[A-Z0-9-]+|F\d-[A-Z0-9-]+|P\d-[A-Z0-9-]+"
               r"|A-[A-Z0-9-]+|AV-[A-Z0-9-]+|TRIG-\d+|HANDOVER")
_WORK_BRACKET = re.compile(r"\[[^\]]*?(?:" + _WORK_TOKEN + r")[^\]]*\]")
# 대괄호 **안**에서 뗄 것 — 과제 번호, 단계 표시, 붙어 있는 날짜다. 그 밖의 내용은 근거이므로 남긴다.
# `[FIX-53 3단계 라벨 정정: 10-Q Note 1 문면은 …]` 에서 정정 내용까지 떼면 근거가 사라진다.
_WORK_INNER = re.compile(r"(?:" + _WORK_TOKEN + r")|\d단계|\d{4}-\d{2}-\d{2}|재척도 표시|재척도")
# 대괄호를 떼고 남은 것이 이만큼도 안 되면 그 대괄호는 통째로 이력이다.
_KEEP_MIN_CHARS = 6
# 원본이 쓰던 그림 표시. 뜻이 있는 것은 글자로 밝히고 나머지는 뺀다.
_MARK_LABELS = {"⚠️": "주의 — ", "⚠": "주의 — ", "📐": "", "🆕": "", "🔧": ""}
# `⚠️` 는 코드포인트 둘(U+26A0 U+FE0F)이라 문자 클래스로는 앞 글자만 잡힌다. 긴 것부터 대안으로 쓴다.
_MARKS_RE = re.compile("|".join(re.escape(k) for k in sorted(_MARK_LABELS, key=len, reverse=True)))
# 영어 표기도 본문에서는 이름으로 옮겨 그린다(FIX-73 과 같은 처리).
_SUPERSEDED_RE = re.compile(r"\bsuperseded\s*다")
_SUPERSEDED_ANY = re.compile(r"\bsuperseded\b")


# 2026-09-17 FIX-78 S2: 엔진이 찍은 경고가 코드 쓰는 사람의 말로 남아 있었다
# (`승계 점수를 사용` · `legacy 역산` · `policies.f6.net_cash`). 데이터(`results.json` 의
# `warnings`)는 고치지 않고 **표시할 때** 옮겨 그린다. 긴 구절이라 낱말 이름표와 따로 둔다.
WARNING_PHRASES = {
    "승계 점수를 기준선 표시로 사용": "앞서 매긴 점수를 참고 표시로만 쓴다",
    "승계 점수를 사용": "앞서 매긴 점수를 그대로 쓴다",
    "legacy 역산으로 세운 정의": "기준선에서 거꾸로 세운 정의",
    "legacy_unverified": "사용자 원본 값·다시 확인 안 함",
    "제안값(proposed)": "제안값",
    "이번 실행 재검토 아님": "이번 실행에서 다시 매기지 않았다",
    "수동 판단을 무시함": "사람이 적어 둔 점수를 쓰지 않는다",
}
# 규칙 파일 안의 경로 표기. 어디를 보라는 뜻이라 **읽을 수 있는 이름**으로 바꾼다.
# 2026-09-17 FIX-78 S3: `HANDOVER 120행` 은 파일 이름과 행 번호라 읽는 사람에게 뜻이 서지 않는다.
# 문서 이름으로 옮기고 행 번호는 감사 기록으로 보낸다(`split_worknote` 가 그 일을 한다).
SOURCE_NAMES = {
    "HANDOVER": "인수인계 문서",
    "채점표": "사용자 원본 채점표",
    "채점규칙": "채점규칙 원문",
    "구현계획": "자동화 구현계획",
}
RULE_PATHS = {
    "policies.f6.p4 nonop_share": "⑥ 입력 신뢰도 규칙의 영업외 비중 항목",
    "policies.f6.net_cash": "⑥ 순현금 정의 규칙",
    "policies.f6.p4": "⑥ 입력 신뢰도 규칙",
    "policies.f6": "⑥ 가격 규칙",
    "policies.f9": "⑨ 적자 깊이 규칙",
}
_WARN_RE = re.compile("|".join(
    re.escape(k) for k in sorted(list(WARNING_PHRASES) + list(RULE_PATHS), key=len, reverse=True)))


def source_names(text: str) -> str:
    """출처 표기를 읽을 수 있는 문서 이름으로 옮긴다. 행 번호는 `split_worknote` 가 이력으로 보낸다."""
    out = re.sub(r"\b(HANDOVER|채점표|채점규칙|구현계획)\s*\d+행",
                 lambda m: SOURCE_NAMES[m.group(1)], text)
    return re.sub(r"\b(HANDOVER)\b", lambda m: SOURCE_NAMES[m.group(1)], out)


def readable_warning(text: str) -> str:
    """경고문을 읽는 사람의 말로 옮긴다. 뜻은 바꾸지 않고 표현만 바꾼다."""
    both = {**WARNING_PHRASES, **RULE_PATHS}
    return _WARN_RE.sub(lambda m: both[m.group(0)], text)


# ------------------------------------------------------------------ 카드의 사유·참고 문구
# 2026-09-18 FIX-79 S1: 카드가 계산 기록의 라벨을 그대로 찍었다(`입력 신뢰도 보정 한 칸 — 조건 영업외 비중`).
# **무엇이 기준을 넘었는지(값과 기준)와 그래서 왜 문제인지**가 둘 다 빠졌다(사용자 지적).
# 문장은 `results.json` 의 `calc` 에서 값을 읽어 만든다. 경고 원문은 데이터라 고치지 않는다.
NOTE_KINDS = {"cut": "감점 사유", "cap": "점수 상한", "note": "참고"}
# 관측 ID 대신 화면에 쓰는 이름. 관측 ID 는 감사 기록으로 간다.
OBS_METRIC_NAMES = {
    "post_money_valuation": "투자 후 기업가치", "arr": "연간 반복 매출(ARR)",
    "arr_prior": "1년 전 연간 반복 매출", "cumulative_raised": "누적 조달액",
    "ps_ratio": "매출 대비 기업가치 배수", "offbalance_B": "장부 밖 지출 약정(B종)",
    "market_cap": "시가총액", "net_cash": "순현금", "lease_liabilities": "리스부채",
}
# 입력 신뢰도 조건마다 **읽는 사람이 알아들을 이유**.
_P4_REASONS = {
    "period_basis_not_ttm": {
        "annual": "최근 1년(TTM) 값이 없어 회계연도 값을 썼다 — 기간이 어긋나 다른 회사와 견주기가 덜 정확하다",
        "quarterly_yoy": "최근 1년치가 없어 한 분기를 전년 같은 분기와 견준 값을 썼다 — 기간이 짧아 비교가 덜 정확하다",
    },
    "short_history": "상장한 지 얼마 안 돼 비교할 전년 1년치 실적이 없다",
}
_OBS_ID_RE = re.compile(r"^([a-z0-9-]+)\.([A-Za-z_]+)\.([a-z0-9]+)\s*:")


def _obs_name(metric: str) -> str:
    return OBS_METRIC_NAMES.get(metric, TERM_NAMES.get(metric, metric))


def _pct(x: float) -> str:
    return f"{x:.0%}"


def _p4_note(ctx: Any, fr: dict[str, Any]) -> dict[str, Any] | None:
    """⑥ 입력 신뢰도로 한 칸 깎은 사유. 값과 기준을 `calc.p4` 와 규칙에서 읽는다."""
    calc = fr.get("calc") or {}
    p4 = calc.get("p4") or {}
    hit = p4.get("conditions_hit") or []
    steps = int(p4.get("demotion_steps") or 0)
    if not hit or not steps:
        return None
    conds = {c["id"]: c for c in ctx.rules.payload["policies"]["f6"]["p4"]["conditions"]}
    reasons = []
    for cid in hit:
        if cid == "nonop_share" and p4.get("nonop_share") is not None:
            thr = float(conds["nonop_share"]["threshold"])
            reasons.append(f"최근 1년 세전이익의 **{_pct(p4['nonop_share'])}** 가 본업 밖에서 나왔다(기준 {_pct(thr)}) — "
                           "이익 가운데 본업이 아닌 몫이 커서 PER 이 실제보다 싸 보일 수 있다")
        elif cid == "period_basis_not_ttm":
            reasons.append(_P4_REASONS[cid].get(p4.get("period_basis"), "최근 1년(TTM)이 아닌 기간의 값을 썼다"))
        elif cid in _P4_REASONS:
            reasons.append(str(_P4_REASONS[cid]))
        elif cid == "stale_asof":
            st = p4.get("stale_asof") or {}
            reasons.append(f"자료 기준일이 {st.get('months_elapsed')}개월 지나 오래됐다(기준 {st.get('limit_months')}개월)")
        else:
            reasons.append(TERM_NAMES.get(cid, cid))
    # FIX-55 가 지킨 사실(조건 하나가 강등을 혼자 정했다)은 이제 이 문장이 말한다.
    if len(hit) == 1 and p4.get("demotion_sole_cause"):
        reasons[-1] += " — 걸린 조건은 이 하나다"
    if (p4.get("nonop_share_boundary") or {}).get("flag"):
        reasons.append("영업외 비중이 기준에 아주 가깝다(경계)")
    sub, score = calc.get("subtotal_before_p4"), fr.get("score")
    tail = (f" 그래서 소계 {sub} 에서 {_count(steps)} 칸 낮춰 점수는 **{score}**." if sub is not None else "")
    if len(hit) > 1:
        tail += " 조건이 여럿 걸려도 한 칸까지만 깎는다."
    return {"kind": "cut", "text": f"입력 신뢰도 −{steps} — " + " · ".join(reasons) + "." + tail}


def factor_notes(ctx: Any, fid: str, fr: dict[str, Any]) -> list[dict[str, Any]]:
    """카드 한 칸의 사유·참고 문구. `{kind, text, ids}` 이고 `ids` 는 감사 기록으로 보낼 관측 ID 다.

    엔진 경고는 계산 기록의 라벨이다. 알려진 종류는 `calc` 의 값으로 다시 쓰고, 방법 절이 이미 모두에게
    한 번 말하는 공통 문구는 카드에서 뺀다. 모르는 종류는 읽을 수 있게 옮겨 참고로 남긴다 — 버리지 않는다.
    """
    calc = fr.get("calc") or {}
    out: list[dict[str, Any]] = []
    unverified: list[str] = []
    unverified_ids: list[str] = []
    blocked: list[str] = []
    used_p4 = False
    for raw in fr.get("warnings") or []:
        w = str(raw)
        if w.startswith("승계된 판단 — 원검토일"):
            continue                                   # 상태 칸과 근거 머리줄이 이미 말한다
        if w.startswith("C-03 확정") or w.startswith("net_cash 작업 정의"):
            continue                                   # 전체 기업·상장사 공통이라 방법 절에 한 번 적는다
        if w.startswith("P4 보정"):
            note = _p4_note(ctx, fr)
            if note and not used_p4:
                out.append(note)
                used_p4 = True
            continue
        if w.startswith("미검증 입력"):
            m = re.search(r"(market_cap|net_cash)\s*이 legacy_unverified 인데 ([P\d, ]+?) 가", w)
            if m:
                params = [F6_PARAM_LABELS.get(x.strip(), x.strip()) for x in m.group(2).split(",")]
                unverified.append(f"{_obs_name(m.group(1))}({'·'.join(params)} 계산에 들어감)")
            b = re.search(r"실측이 막힌 이유: (\w+)", w)
            if b:
                blocked.append(_obs_name(b.group(1)))
            continue
        mo = _OBS_ID_RE.match(w)
        if mo and "legacy_unverified" in w:
            unverified.append(_obs_name(mo.group(2)))
            unverified_ids.append(f"{mo.group(1)}.{mo.group(2)}.{mo.group(3)}")
            continue
        if w.startswith("nonop_share 재계산"):
            p4 = calc.get("p4") or {}
            if p4.get("nonop_share") is not None and p4.get("nonop_share_stored") is not None:
                out.append({"kind": "note", "text":
                            f"영업외 비중을 공시 숫자로 다시 계산하면 {_pct(p4['nonop_share'])} 다. 사용자 원본 표에는 "
                            f"{_pct(p4['nonop_share_stored'])} 로 적혀 있었고, 점수에는 다시 계산한 값을 썼다."})
                continue
        if w.startswith("nonop_share 산출 안 함"):
            pretax = ((calc.get("p4") or {}).get("nonop_share_inputs") or {}).get("pretax_income_ttm")
            shown = f"({fmt_usd(pretax)})" if pretax is not None else ""
            out.append({"kind": "note", "text":
                        f"세전이익이 적자{shown}라 영업외 비중을 계산할 수 없다 — 이익이 없으면 그중 본업 밖 몫을 "
                        "나눌 수 없어서다. 그래서 이 조건은 보지 않았다."})
            continue
        if "G3 런웨이" in w and "±" in w:
            g3 = next((q for q in calc.get("path") or [] if q.get("runway_years") is not None), None)
            bd = (g3 or {}).get("boundary") or {}
            if g3 and bd.get("nearest_boundary"):
                y, b, d = g3["runway_years"], bd["nearest_boundary"], bd["distance_ratio"]
                side = ("넘었으므로 이 관문에서 더 깎지 않았다" if d >= 0 else "조금 못 미쳐 이 관문 기준으로는 한 칸이 깎인다")
                out.append({"kind": "note", "text":
                            f"런웨이 {y:.2f}년 — 기준 {b:g}년과 {abs(d):.1%} 차이라 경계에 아주 가깝다. 기준을 {side}."})
                continue
        if w.startswith("F1 부품 상한"):
            cap = ctx.rules.factor("F1").get("component_only_cap")
            out.append({"kind": "cap", "text": f"소비자·업무 채널이 없는 부품 공급형이라 이 항목은 최고 {cap}점까지다."})
            continue
        if w.startswith("C-04"):
            out.append({"kind": "note", "text": "런웨이를 잴 때 완충에는 현금과 조건이 확인된 확정 미인출 여신만 넣었다 — "
                                               "신용등급이 좋아 더 빌릴 수 있다는 추정은 넣지 않는다."})
            continue
        if w.startswith("C-06"):
            bands = ctx.rules.payload["policies"]["f9"].get("g1_bands_proposed") or []
            txt = " · ".join(f"손실률 {abs(b['min_margin']):.0%} 까지 {b['score']}" for b in bands if b.get("min_margin") is not None)
            out.append({"kind": "note", "text": "본업 손실률 구간은 제안된 새 구간을 이번 실행에서 적용했다"
                                               + (f"({txt}, 그보다 깊으면 {min(b['score'] for b in bands)})" if txt else "") + "."})
            continue
        if w.startswith("C-20"):
            out.append({"kind": "note", "text": "영업손익을 공시하지 않는 비상장사라 본업 관문을 판정하지 않고 비상장사용 경로로 "
                                               "보냈다 — 본업 관문을 **통과했다는 뜻이 아니다**."})
            continue
        if w.startswith("C-29"):
            when = re.search(r"사용자 결정 (\d{4}-\d{2}-\d{2})", w)
            out.append({"kind": "note", "text": "흑자 전환 시점을 뒤로 미뤘다는 기록이 있지만, 영업손익이 공시되지 않은 비상장사라 "
                                               "비상장사용 경로가 먼저다" + (f"(사용자 결정 {when.group(1)})" if when else "")
                                               + ". 전망이나 목표만으로 손실을 단정하지 않는다."})
            continue
        if w.startswith("C-09"):
            out.append({"kind": "note", "text": f"조합표의 두 축 판정이 남아 있지 않아 앞서 매긴 점수({fr.get('score')})를 "
                                               "그대로 쓴다. 조합표를 다시 태우지 못한다."})
            continue
        if "수동 판단을 무시함" in w:
            out.append({"kind": "note", "text": "판단 기록에 사람이 적어 둔 ⑥ 점수가 있지만, 이번 규칙은 그 점수를 쓰지 않고 "
                                               "관측에서 다시 계산했다."})
            continue
        # 모르는 종류 — 버리지 않고 읽을 수 있게 옮겨 참고로 둔다.
        body, _n = split_worknote(readable_warning(w))
        if body:
            out.append({"kind": "note", "text": rename_codes(body)})
    if unverified:
        seen = list(dict.fromkeys(unverified))
        text = ("**사용자 원본 값이고 이번에 다시 확인하지 않았다** — " + " · ".join(seen) + ". "
                + (f"{'·'.join(dict.fromkeys(blocked))}를 아직 새로 재지 못해 다시 계산할 수 없었다. " if blocked else "")
                + "자료를 새로 재지 못한 것이지 회사의 성질이 아니라서 점수는 깎지 않았다.")
        out.append({"kind": "note", "text": fix_josa_in(text), "ids": unverified_ids})
    # 점수를 움직인 사유가 먼저 오고 참고는 뒤에 온다 — 둘이 같은 딱지로 섞여 있었다.
    order = {"cut": 0, "cap": 1, "note": 2}
    return sorted(out, key=lambda n: order[n["kind"]])


def fix_josa_in(text: str) -> str:
    """`리스부채를`·`시가총액를` 처럼 이름 뒤에 붙인 조사를 받침에 맞춘다."""
    return re.sub(r"([가-힣A-Za-z)]+)(를|을)(?= )", lambda m: fix_josa(m.group(1), "", m.group(2)), text)


def split_worknote(text: str) -> tuple[str, str]:
    """근거 문장을 `(본문, 이력)` 으로 가른다. 이력이 없으면 둘째 값이 빈 문자열이다.

    본문에서 내리는 것은 **작업 표기**뿐이다 — 과제 번호, 지시서 번호, 단계 표시가 그것이다.
    `채점규칙 22행` 같은 출처와 검토 결과 문장은 근거의 일부라 남긴다.
    """
    notes: list[str] = []

    def one_bracket(m: re.Match[str]) -> str:
        """대괄호 안에서 작업 표기만 뗀다. 내용이 남으면 그 내용은 근거이므로 되돌린다."""
        inner = _WORK_INNER.sub(" ", m.group(0)[1:-1])
        inner = re.sub(r"[ \t]{2,}", " ", inner).strip(" ·,—:·")
        notes.append(m.group(0))
        return f"[{inner}]" if len(inner) >= _KEEP_MIN_CHARS else " "

    body = _WORK_BRACKET.sub(one_bracket, text)
    # 대괄호 밖에 남은 작업 표기(`OBS-REG-25 지시서 · G1-TTM-26`)도 이력으로 보낸다.
    loose = re.compile(r"[(（·,]?\s*(?:" + _WORK_TOKEN + r")(?:[^\s,)）·]*)(?:\s*지시서)?")
    extra = [m.group(0).strip(" (（·,") for m in loose.finditer(body)]
    if extra:
        notes += extra
        body = loose.sub("", body)
    body = _MARKS_RE.sub(lambda m: _MARK_LABELS[m.group(0)], body)
    body = re.sub(r"주의 —\s*—\s*", "주의 — ", body)
    body = _SUPERSEDED_RE.sub("대체된 것이다", body)   # `superseded 다` → `대체된 것이다`
    body = _SUPERSEDED_ANY.sub("대체됨", body)
    body = re.sub(r"\(\s*[·,]?\s*\)", "", body)
    body = re.sub(r"\s*—\s*(?=[)）])", "", body)
    # 대괄호를 떼면서 **여는** 강조 기호 뒤가 비었다(`** A+2 …**`). 그 자리만 붙인다 —
    # 쌍으로 잡으면 `**A** · **B**` 의 가운데 ` · ` 까지 강조 안쪽으로 보고 먹는다.
    body = re.sub(r"(?<![*\S])\*\*\s+(?=\S)", "**", body)
    body = re.sub(r"[ \t]{2,}", " ", body).strip(" ·,—")
    if body.count("**") % 2:
        body = body[::-1].replace("**", "", 1)[::-1]
    return body, " ".join(notes)


def reviewer_label(judgment: dict[str, Any], with_owner: bool = True) -> str:
    """판단을 **누가 언제** 매겼는지. 검토자 칸의 작업 표기는 떼고 이름과 날짜만 남긴다.

    2026-09-17 FIX-77: `승계된 판단 — 원검토일 …, 이번 실행 재검토 아님` 은 읽는 사람에게
    기계 상태처럼 들렸다. **승계는 사용자가 앞서 매긴 판단**이고, 이번 실행에서 다시 매긴 것은
    따로 보여야 한다 — 뭉뚱그리면 거짓이 된다.
    """
    # 검토자 칸은 이름만 쓴다. 괄호 안 부연(`(리뷰 C codex 발견 · 사용자 결정)`)과 커밋 해시는 이력이다.
    who = re.split(r"\s*[(（—]", str(judgment.get("reviewer") or ""), maxsplit=1)[0].strip(" ·—")
    if who.startswith("worker"):
        who = "작업자"
    when = judgment.get("reviewed_at") or ""
    if judgment.get("status") == "carried":
        # 2026-09-17 FIX-78 S1: 상태 칸이 `사용자의 판단` 을 말하는 자리에서는 같은 말을 되풀이하지
        # 않는다. 근거 머리줄은 **언제 매겼는지**만 더한다.
        return f"사용자의 판단 · {when}" if with_owner else f"원검토 {when}"
    return f"이번 실행에서 다시 매김 · {who or '검토자 미기재'} · {when}"


def _split_block(block: dict[str, Any]) -> dict[str, Any]:
    """근거 줄에서 작업 메모를 떼어 `notes` 로 옮긴다. 본문만 남은 줄이 `lines` 다.

    2026-09-17 FIX-77: 메모만 걷어내고 근거는 남긴다(사용자 선택). 뗀 것은 버리지 않고
    감사 기록으로 보내 기업·항목별로 찾을 수 있게 한다.
    """
    lines, notes = [], []
    for depth, text in block["lines"]:
        body, note = split_worknote(str(text))
        if note:
            notes.append(note)
        if body:
            lines.append((depth, body))
    block["lines"] = lines
    block["notes"] = notes
    return block


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
        return _split_block({"kind": "baseline_reference",
                             "header": "참고 서술 — 이번 실행은 관측에서 계산했고 이 문장은 점수 근거가 아니다",
                             "lines": [(1, head)] + [(1, annotate_replaced(e, company_id, reps))
                                                     for e in base_evidence[:6]]})
    jid = judgment["judgment_id"]
    evidence = [annotate_replaced(e, company_id, reps) for e in (judgment.get("evidence") or [])]
    if judgment["status"] == "carried":
        return _split_block({"kind": "carried", "header": f"근거 · {reviewer_label(judgment, with_owner=False)} · 판단 기록 `{jid}`",
                             "lines": [(1, e) for e in evidence]})
    lines = [(1, e) for e in evidence]
    sup = judgment.get("superseded")
    if sup:
        lines.append((1, f"대체된 판단 `{sup['judgment_id']}` — {sup['superseded_at']} 에 바뀌었다. {sup['why']}"))
        lines += [(2, struck(e)) for e in sup.get("evidence", [])[:6]]
        if len(sup.get("evidence", [])) > 6:
            lines.append((2, f"(외 {len(sup['evidence']) - 6}줄은 판단 기록의 대체 항목에 있다)"))
    elif base_evidence and base_evidence != list(judgment.get("evidence") or []):
        old = [e for e in base_evidence if e not in (judgment.get("evidence") or [])]
        if old:
            lines.append((1, f"과거 기록(기준선 {baseline_id} 서술 — 이번 실행 판단으로 대체):"))
            lines += [(2, struck(e)) for e in old[:6]]
    return _split_block({"kind": "new", "header": f"근거 · {reviewer_label(judgment, with_owner=False)} · 판단 기록 `{jid}`",
                         "lines": lines})


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
        # 2026-09-18 FIX-80 S1: 산식 줄 꼬리(`· 입력 신뢰도 -1(영업외 비중) — 영업외 비중 하나가 강등을 정한다`)가
        # 바로 아래 감점 사유와 같은 말을 사용자가 뜻을 모르겠다던 형태로 한 번 더 했다. 소계까지만 적고
        # 입력 신뢰도는 감점 사유 한 곳에서 값·기준·이유와 함께 말한다(`_p4_note`).
        text += f" = 소계 {calc['subtotal_before_p4']}"
    if "subtotal_before_correction" in calc:
        text += f" = 소계 {calc['subtotal_before_correction']} · 비상장 보정 +{(calc.get('correction') or {}).get('promotion_steps', 0)}"
    # 2026-09-18 FIX-79: `승계 입력 시가총액(PER·EV/매출)` 은 카드의 참고 문구가 무엇이 왜 그런지 말한다.
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
    return (f"기준선 {ctx.run['baseline_id']} 에서 넘어온 관측(`legacy_unverified` {legacy_n}건, SRC-v15-html·SRC-v15-md·SRC-v15-rule)은 "
            "이번 실행에서 재검증되지 않았다(D-08). **표마다 실측(verified)과 사용자 원본 값이 섞여 있다** — 각 표 아래에 열별 관측 상태를 적는다. "
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
    return (f"{VENDOR_MARK} **원천 정책 밖 공급사 값 {len(flagged)}건**({detail}). 관측 basis 에 `vendor_not_in_source_policy` 가 붙은 v1.5 에서 넘어온 값이다 — "
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
# 기준 사다리의 판정값과 조합표 칸이 화면에서 무엇으로 읽혀야 하는지. 규칙은 키만 들고 있다.
CRITERIA_WEIGHT_LABELS = {"pass": "통과", "partial": "부분 통과", "fail": "실패"}
MATRIX_AXIS_LABELS = {
    "small|no": "의존 작음/환류 없음", "small|yes": "의존 작음/환류 있음",
    "large|no": "의존 큼/환류 없음", "large|yes": "의존 큼/환류 있음",
}
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


# 2026-09-17 FIX-76 S2: 본문에 실리면 안 되는 **작업 메모** 표기. 결정 번호·과제 번호·이관 도구 이름·
# 내부 상태값이다. 출처 표기(`별표 A`)는 남긴다 — 읽는 사람이 원문을 찾아갈 수 있어야 한다.
_WORKNOTE_RE = re.compile(
    r"\s*(?:\(|（)?(?:C-\d+[^)）.]*|FIX-\d+[^)）.]*|HANDOVER[^)）.]*|carried_score|"
    r"pending_rule_decision|needs_rule_decision)(?:\)|）)?")


def strip_worknotes(text: str) -> str:
    """결정 번호·과제 번호·내부 상태값을 덜어 낸다. 남은 겹공백과 빈 괄호도 정리한다.

    원본이 자기 화면 배치를 가리키는 말(`↓ 판정 흐름은 바로 아래`)도 뗀다 — 우리 리포트에서는
    가리키는 것이 없어 틀린 말이 된다. `별표 A` 같은 **출처 표기는 남긴다.**
    """
    out = _WORKNOTE_RE.sub(" ", text)
    out = re.sub(r"[↓↑][^\n]*?(?:바로 아래|바로 위|아래에|위에)[^\n]*", "", out)
    out = re.sub(r"^\s*지표\s*—\s*", "", out)          # 카드에 제목이 따로 있어 겹친다
    out = re.sub(r"\(\s*[,·]?\s*\)", "", out)
    out = re.sub(r"\s*—\s*(?=[.,]|$)", "", out)
    out = re.sub(r"[ \t]{2,}", " ", out).strip(" ·,—\n")
    # 강조 표시가 홀수로 남으면 뒤가 통째로 굵게 나온다. 짝이 안 맞으면 마지막 하나를 뗀다.
    if out.count("**") % 2:
        out = out[::-1].replace("**", "", 1)[::-1]
    return out.strip(" ·,—")


_CONCEPTS: dict[str, Any] | None = None


def factor_concepts() -> dict[str, Any]:
    """사용자 원본 `02 9가지 factor 뜯어보기` 를 옮겨 둔 자료를 읽는다.

    2026-09-17 FIX-76: **이 항목이 무엇을 재는가**가 산출물에 통째로 빠져 있었다(사용자 지적).
    채점 기준·환산 방법과는 다른 층이라 섞지 않는다. 문장은 원본 그대로이고 여기서 짓지 않는다.
    """
    global _CONCEPTS
    if _CONCEPTS is None:
        import json
        path = Path(__file__).resolve().parents[2] / "scorecard" / "factor-concepts.json"
        _CONCEPTS = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {"items": {}}
    return _CONCEPTS


def factor_concept(ctx: Any, fid: str) -> dict[str, Any]:
    """그 항목의 개념 설명. 지금 규칙과 달라진 자리에는 `stale`·`renamed` 가 붙어 있다."""
    item = dict(factor_concepts().get("items", {}).get(fid) or {})
    if not item:
        return {}
    # 2026-09-17 FIX-77: 원본의 그림 표시(`🆕`·`⚠️`)는 v1.5 안에서만 뜻이 서던 것이다.
    # 본문과 같은 규칙으로 밝히거나 뺀다.
    for key in ("definition", "question", "metrics"):
        if item.get(key):
            item[key] = split_worknote(str(item[key]))[0]
    item["examples"] = [split_worknote(str(x))[0] for x in (item.get("examples") or [])]
    # 이름이 바뀌었으면 **지금 이름**을 제목으로 쓰고 원본 이름은 아래에 남긴다.
    now = str(ctx.rules.factor(fid)["label"])
    src = f"{item.get('mark', '')} {item.get('name', '')}".strip()
    if src.replace(" ", "") != now.replace(" ", ""):
        item["renamed"] = {"now": now, "source": src}
    else:
        item.pop("renamed", None)
    return item


def factor_criteria(ctx: Any, fid: str) -> list[str]:
    """그 항목을 **무엇을 보고 매기는지**를 규칙에서 읽는다.

    2026-09-17 FIX-75: 규칙 `note` 에 적힌 채점 기준(② 의 세 경로 이름, ① 의 부품형 상한,
    ④ 의 출하만 인정, ③ 의 기준 배점)이 산출물 어디에도 나오지 않아 **점수를 만드는 방식만 보이고
    무엇을 보고 매기는지는 보이지 않았다**(사용자 지적). 문장을 새로 짓지 않고 규칙 값을 옮긴다.
    """
    f = ctx.rules.factor(fid)
    out: list[str] = []
    # 2026-09-17 FIX-76 S2: 여기 규칙 `note` 를 그대로 실었더니 `HANDOVER 사다리`·`C-03 확정`·
    # `carried_score` 같은 **작업 메모**가 본문에 실렸다(사용자 지적). 기준은 **별표 원문**에서 가져오고
    # 규칙 `note` 는 감사 기록으로 보낸다.
    metrics = (factor_concept(ctx, fid) or {}).get("metrics") or ""
    if metrics:
        out.append(strip_worknotes(metrics))
    cap = f.get("component_only_cap")
    # 같은 말이 `note` 에 이미 있으면 두 번 적지 않는다.
    if cap is not None and f"상한 {cap}" not in str(f.get("note", "")):
        out.append(f"소비자·업무 채널이 없는 부품형 회사는 이 항목의 상한이 **{cap}점**이다.")
    weights = f.get("criteria_weights")
    if weights:
        out.append("기준마다 " + " · ".join(
            f"{CRITERIA_WEIGHT_LABELS.get(k, k)} {v:g}점" for k, v in weights.items())
            + " 을 주고, 그 합으로 사다리 칸을 고른다.")
    ladder = f.get("ladder")
    if ladder:
        def _pts(step: dict[str, Any]) -> str:
            lo, hi = step["points"][0], step["points"][-1]
            return f"{lo:g}점" if lo == hi else f"{lo:g}~{hi:g}점"
        out.append("사다리는 " + " · ".join(f"{_pts(x)} → {x['score']}점" for x in ladder) + " 다."
                   + (" **맨 윗칸은 모방불가를 통과해야 열린다.**"
                      if any(x.get("requires_imitation_pass") for x in ladder) else ""))
    if f.get("score5_requires_door_closed"):
        out.append("최고점 5점은 사다리만으로 닿지 않는다 — **문이 닫혔는지**를 따로 통과해야 한다.")
    if f.get("score5_requires_generation_gap"):
        out.append("최고점 5점은 통과 수만으로 닿지 않는다 — **세대 격차**를 따로 채워야 한다.")
    if f.get("formula"):
        out.append(f"산식은 `{f['formula']}` 이고 동맹 A 는 "
                   + "·".join(f"{x:g}" for x in f.get("A_allowed", []))
                   + ", 적대 H 는 " + "·".join(f"{x:g}" for x in f.get("H_allowed", [])) + " 중 하나다.")
    if f.get("matrix"):
        out.append("조합표는 " + " · ".join(
            f"{MATRIX_AXIS_LABELS.get(k, k)} {v}점" for k, v in f["matrix"].items()) + " 다.")
    # **기준이 규칙에 없는 항목이 있다.** 비어 있다는 사실 자체가 읽는 사람에게 필요한 정보다.
    if not out:
        out.append("**이 항목은 규칙이 채점 기준을 적어 두지 않았다.** 범위와 점수를 만드는 방식만 정해져 "
                   "있어, 무엇을 보고 그 점수를 주었는지는 각 회사 카드의 근거 문장에서 읽어야 한다.")
    return out


def method_sections(ctx: Any, results: dict[str, Any]) -> list[tuple[str | None, list[str]]]:
    """방법 절을 **항목별로 갈라** 돌려준다. `(factor_id, 문장들)` 이고 `None` 은 여러 항목에 걸치는 문단이다.

    2026-09-17 FIX-67 전면 재작성 → FIX-68·69 정정. **문장이 규칙을 잘못 말하지 않게** 숫자와 칸 수를
    규칙·계산 코드에서 읽어 쓴다(FIX-69 L1). 결정 번호는 문장에서 빼 `관련 결정` 줄로 보낸다.
    2026-09-17 FIX-75: 평평한 목록이라 어느 문장이 어느 항목 것인지 읽는 사람이 알 수 없었다.
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
    population_count = int(results["population"]["scored"]) + len(results["population"]["incomplete"])
    newly_listed_count = sum(
        1 for company in results["companies"]
        if (((company.get("factors") or {}).get("F6") or {}).get("calc") or {}).get("track") == "listed_newly"
    )
    bep_retreat_count = sum(
        1 for company in results["companies"]
        if any(
            step.get("gate") == "G1" and str(step.get("band", "")).startswith("BEP 후퇴")
            for step in ((((company.get("factors") or {}).get("F9") or {}).get("calc") or {}).get("path") or [])
        )
    )
    f6_judgment_count = len({j["company_id"] for j in ctx.judgments if j["factor"] == "F6"})
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
        + (f" 판단 기록에는 비상장 {_count(f6_judgment_count)} 곳의 점수가 남아 있지만 **이번 규칙은 그 점수를 쓰지 않고 관측에서 "
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
        f"분기끼리 견준다. 이번 {population_count}개사 중 {_count(newly_listed_count)} 곳이 그 경우다."
        + (" 어느 회사가 여기 드는지는 상장 시점이 아니라 **그 회사 매출 관측이 어느 기간 단위인지**로 가른다."
           if newly_by_basis else ""),
        f"  - 구간 경계에서 {tol:.0%} 안에 든 값에는 표시를 달지만 **점수는 바꾸지 않는다.**",
        # 2026-09-18 FIX-79 S1: 상장사 카드마다 같은 경고로 찍히던 것을 여기 한 번만 적는다.
        *(["  - **EV/매출의 순현금은 아직 확정되지 않은 작업 정의로 잰다.** 사용자 원본 값에서 거꾸로 세운 "
           "정의라, 정의가 확정되면 EV/매출을 다시 계산한다. 상장사 전부에 해당하는 사정이라 기업 카드에는 "
           "적지 않는다."] if (f6p.get("net_cash") or {}).get("status") == "working_definition" else []),
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
        f"**이 처리가 맞는지는 2026년 11월에 다시 본다.** 이번 {population_count}개사 중 이 조항이 걸린 회사는 "
        + ("없다." if bep_retreat_count == 0 else f"{_count(bep_retreat_count)} 곳이다."),
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
    judged_company_sets = [
        {j["company_id"] for j in ctx.judgments if j["factor"] == fid}
        for fid in judged
    ]
    judged_company_count = len(set.intersection(*judged_company_sets)) if judged_company_sets else 0

    def _names(ids: list[str]) -> str:
        return " · ".join(FACTOR_LABELS[f] for f in ids)

    def carried_note(fid: str) -> str:
        """같은 항목 안에서 판정 입력이 남지 않아 숫자만 넘어온 회사가 있으면 그 수를 적는다."""
        n = sum(1 for j in ctx.judgments if j["factor"] == fid and j["kind"] == "score")
        return (f" 다만 {_count(n)} 곳은 그 판정이 남아 있지 않아 **점수 숫자만 넘어왔고** 엔진이 "
                "다시 환산하지 못한다." if n else "")

    overview = [
        f"**{_names(judged)} {_count(len(judged))} 항목은 모두 사람 판단에서 나온다.** 판단 기록을 세어 보면 "
        f"이번 실행 {population_count}개사 "
        + ("전부가" if judged_company_count == population_count else f"중 {_count(judged_company_count)}곳이")
        + " 이 항목들에 사람이 적은 판단을 입력으로 갖는다. **사다리·산식·조합표는 사람이 매긴 것을 "
        "정해진 표로 환산하는 장치이지 판단을 대신하는 것이 아니다.** 그래서 이 항목들은 모두 점수보다 근거 "
        "문장을 읽어야 한다. 항목마다 사람이 무엇을 적고 엔진이 무엇을 했는지는 아래 각 칸에 적는다.",
    ]
    # 2026-09-17 FIX-75: 문장이 어느 항목 것인지 표시가 없어 한 덩어리로 읽혔다(사용자 지적).
    # 항목마다 갈라 두고 `method_lines` 는 이것을 펴서 돌려준다 — 초안과 HTML 이 같은 원천을 쓴다.
    scored = {f: [f"사람이 **{JUDGMENT_ROLES['score']}**를 적는다. 환산할 산식이 아예 없어 적힌 점수가 "
                  "그대로 이 항목의 점수가 된다. **점수보다 근거 문장을 읽어야 한다.**"] for f in plain}
    for f, kind in converted:
        if f not in CONVERSION_NOTES:
            continue
        inputs = judgment_input_names(ctx, f)
        scored[f] = [f"사람이 **{fix_josa(JUDGMENT_ROLES[kind], '', '을')}** 정하고"
                     + (f"({' · '.join(inputs)})" if len(inputs) > 1 else "")
                     + f", {CONVERSION_NOTES[f]}." + carried_note(f)]
    # 2026-09-17 FIX-71 N3: 규칙이 정한 방식과 이번 실행에서 실제로 쓴 방식을 함께 드러낸다.
    f2_judged = {j["company_id"] for j in ctx.judgments if j["factor"] == "F2"}
    f2_carried = {j["company_id"] for j in ctx.judgments if j["factor"] == "F2" and j["kind"] == "score"}
    f2_rule = (
        "규칙은 조건을 몇 개 통과했는지 세어 점수로 바꾸도록 "
        f"정해 두었다({', '.join(f'{k}개 {v}점' for k, v in sorted(ctx.rules.factor('F2')['path_mapping'].items()))}, "
        "최고점은 통과 수만으로 닿지 않고 세대 격차를 따로 채워야 한다)."
    )
    if f2_carried:
        if f2_carried == f2_judged:
            execution = (
                "**이번 실행에서는 규칙 방식으로 계산하지 않았다.** "
                f"② 판단 {len(f2_carried)}개사 모두 어느 경로를 통과했는지가 기준선에서 넘어오지 않아 "
                "기준선 점수를 그대로 쓴다."
            )
        else:
            execution = (
                "**이번 실행에서는 두 방식이 함께 쓰였다.** "
                f"② 판단 {len(f2_judged)}개사 중 {len(f2_carried)}곳은 어느 경로를 통과했는지가 기준선에서 "
                f"넘어오지 않아 기준선 점수를 그대로 썼고, 나머지 {len(f2_judged - f2_carried)}곳은 경로 판정을 "
                "입력으로 규칙 방식에 따라 계산했다."
            )
        scored.setdefault("F2", []).append(
            f"{execution} {f2_rule} 카드의 ② 점수를 보고 통과 수를 거꾸로 셈하면 안 된다.")
    else:
        scored.setdefault("F2", []).append(f2_rule)
    scored["F6"] = f6
    scored["F9"] = [c04_line(ctx)] + g1
    common = [
        "**모르는 값을 0 으로 바꾸지 않는다.** 자료가 없으면 그 항목은 점수를 만들지 않고 대기 상태로 남으며, "
        "그 회사는 공식 순위에서 빠진다. **예외가 하나 있다** — 런웨이를 잴 때 미인출 여신이 확인되지 않으면 "
        "0 으로 센다. 완충은 확인된 것만 세기로 했기 때문이고, 없는 여신을 있다고 보지 않으려는 처리다.",
    ]
    return ([(None, overview)]
            + [(f, scored[f]) for f in FACTOR_LABELS if scored.get(f)]
            + [(None, common)])


def method_lines(ctx: Any, results: dict[str, Any]) -> list[str]:
    """방법 절의 문장을 한 줄씩 편 목록. 절 경계를 모르는 쪽(초안 본문)이 쓴다."""
    return [line for _fid, lines in method_sections(ctx, results) for line in lines]


def conflict_lines(ctx: Any) -> list[str]:
    """이해상충과 제3자 재검토 약속. 2026-09-16 FIX-55 2단계(4차 리뷰 A 분담): 재검토 대상·시점·발동 조건이 산출물 어디에도 없었다.

    문장을 손으로 적지 않고 출처·규칙에서 읽는다 — 규칙이 바뀌면 이 절도 따라 바뀌어야 한다.
    """
    out = []
    # 2026-09-16 FIX-56 1단계(5차 리뷰 B): 문구 집합의 크기를 세어 문구가 같은 두 출처가 하나로 합쳐졌다(6건 → 5종).
    # 읽는 사람이 세고 싶은 것은 **표기된 출처의 수**이므로 출처 건수로 센다.
    flagged = [s for s in ctx.sources.get("items", []) if s.get("conflict_of_interest")]
    if flagged:
        private_count = sum(1 for cid in ctx.run["companies"] if not ctx.companies[cid]["listed"])
        out.append(f"**이해상충** — 이 채점표는 Anthropic 이 만든 Claude 가 작성했고 Anthropic 이 채점 대상에 들어 있다. 이해상충이 표기된 출처가 "
                   f"{len(flagged)}건이고 문장은 References 의 각 출처 줄에 있다. 비상장 {private_count}사의 수치는 회사 자체 발표(이해당사자 1차 자료)에서 온다.")
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

    # 2026-09-18 FIX-80 S3: `TEN-RC-02(anthropic.F1, 2026-11)` 처럼 번호로 적어 무엇을 다시 보는지 읽히지
    # 않았다. 긴장의 제목과 시점을 말로 적는다. 번호와 판단 ID 는 감사 기록의 `다시 볼 것` 표에 있다.
    def _ids(items: list[dict[str, Any]], scope_key: str | None = None) -> str:
        return " · ".join(f"{str(t.get('subject') or t['id']).rstrip('. ')} — {t['recheck_at']} 에 다시 본다"
                          for t in items)

    committed = by_kind.get("committed") or []
    if committed:
        out.append(f"**제3자 재검토 약속**(채점규칙 384행) — 비 Claude 세션 재판정이 **확정**된 긴장 {len(committed)}건: {_ids(committed)}.")
    partial = by_kind.get("partial") or []
    if partial:
        out.append(f"  - **일부만 확정** {len(partial)}건 — {_ids(partial, 'third_party_scope')}. 이 가운데 일부 판단만 "
                   "비 Claude 세션이 보고, 나머지는 재채점 때 판단자가 본다.")
    recommended = by_kind.get("recommended") or []
    if recommended:
        out.append(f"  - **권장일 뿐 약속이 아닌 것** {len(recommended)}건 — {_ids(recommended)}. "
                   "규칙이 `비 Claude 세션 권장` 으로 적은 자리이고 재판정자를 정해 두지 않았다.")
    if done:
        out.append(f"  - **이미 해소된 긴장** {len(done)}건 — " +
                   " · ".join(f"{str(t.get('subject') or t['id']).rstrip('. ')} — {t['resolved_at']} 에 결론이 났다"
                              for t in done) +
                   ". 재판정이 끝나 남은 약속에서 뺐다. 결론은 규칙 `open_tensions` 의 `resolution` 에 있다.")
    c03 = next((d for d in ctx.rules.payload.get("decisions", []) if d["id"] == "C-03"), None)
    recheck = (c03 or {}).get("pending_recheck") or {}
    if recheck:
        # 2026-09-17 FIX-78 S3: `HANDOVER 120행`·`pending_recheck` 가 그대로 실렸다. 출처는 문서 이름으로
        # 적고 행 번호와 내부 상태값은 감사 기록으로 보낸다.
        what = source_names(str(recheck.get("what", "")))
        trigger = source_names(str(recheck.get("trigger", "")))
        when = source_names(str(recheck.get("when", "")))
        out.append(f"  - anthropic ②5 재검토 — {what} 시점 {when} · 발동 조건 `{trigger}` "
                   "(C-03 이 재검토 대기로 걸어 둔 항목이다). 이번 실행은 이 판단을 재판정하지 않았다.")
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
