# 원본 v1.5 HTML(D/VAL/EARN/FIN/BORR/TRIG 배열)과 MD 순위표를 파싱해 기준선(scores·observations·triggers)과 이관 보고서를 만든다
from __future__ import annotations

import html as html_lib
import re
from pathlib import Path
from typing import Any

from .schema import METRICS, SchemaError, resolve_company_id, sha256_file, write_json

# 2026-10-01: 원천 자료를 AI_company_analysis_factor/ 에서 docs/scorecard/source/ 로 옮기며 절대 경로를 저장소 기준으로 바꿨다.
# 2026-10-06 규칙 문서 재편: 기준선은 이미 scorecard/baseline/v1.5/ 에 이관돼 있고 원천 자료를 작업 폴더에서 지웠다.
# 다시 이관해야 하면 아래 커밋에서 원본을 꺼내 경로를 인자로 준다(scorecard_cli.py import-baseline --html … --md …).
# DEFAULT_SOURCE_DIR = Path(__file__).resolve().parents[2] / "docs" / "scorecard" / "source"
# DEFAULT_HTML = DEFAULT_SOURCE_DIR / "AI기업_채점표_v1.5.html"
# DEFAULT_MD = DEFAULT_SOURCE_DIR / "AI기업_채점표_v1.5.md"
SOURCE_COMMIT = "79e476bfa8a14c83dcaad035ebccd52e0939b690"
SOURCE_PATHS = {"html": "docs/scorecard/source/AI기업_채점표_v1.5.html", "md": "docs/scorecard/source/AI기업_채점표_v1.5.md"}
BASELINE_ID = "v1.5"
BASELINE_AS_OF = "2026-09-02"
FACTORS = ("F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9")

SRC_HTML = "SRC-v15-html"
SRC_MD = "SRC-v15-md"
SRC_RULE = "SRC-v15-rule"
# 2026-09-16 FIX-57 2단계(6차 리뷰 A 분담): 판단이 HANDOVER 행 번호를 인용하는데 생성 코드가 이 출처를 만들지 않아
# 새 실행에서는 인용 대상이 사라졌다. 파일은 저장소에 커밋되지 않고 v1.5 원본 셋과 같은 곳에 보존돼 있어
# 해시를 여기 상수로 둔다 — 다른 셋처럼 기준선·규칙 payload 에서 읽어 올 자리가 없다.
SRC_HANDOVER = "SRC-v15-handover"
SRC_HANDOVER_SHA256 = "3e5190c2cb4a4f8ebee2f72d4599929b79a5d4625b1d046c346627edf63b7cc1"

# 규칙 v1.5 ⑨ 게이트 3·4 적용표(별표)에서 읽은 B종 약정·계약 수입. HTML 배열에는 숫자 분리가 없어 규칙 원문 값으로 이관하며 상태를 명시한다.
LEGACY_GATE4: dict[str, dict[str, Any]] = {
    "oracle": {"offbalance_B": (250e9, "verified_legacy", "리스 $250B(15~20년)"), "contracted_revenue": (638e9, "verified_legacy", "RPO $638B")},
    "amazon": {"offbalance_B": (106e9, "verified_legacy", "미개시 리스 $106B(3/31)"), "contracted_revenue": (None, "parse_failed", "AWS 백로그(수백 $B급) — 숫자 미공시")},
    "alibaba": {"offbalance_B": (None, "not_disclosed", "미확인"), "contracted_revenue": (None, "not_disclosed", "—")},
    "spacex-xai": {"offbalance_B": (None, "not_disclosed", "미확인"), "contracted_revenue": (47.5e9, "verified_legacy", "백로그 $47.5B")},
    "anthropic": {"offbalance_B": (300e9, "incompatible_basis", "컴퓨트 약정 $300B(연 ~$50B) — 기간·범위가 RPO 와 다름(C-07)"), "contracted_revenue": (65e9, "incompatible_basis", "ARR $65B — 계약 수입 아님(C-07)")},
    "openai": {"offbalance_B": (338e9, "incompatible_basis", "컴퓨트 약정 $338B+(연 ~$60B) (C-07)"), "contracted_revenue": (40e9, "incompatible_basis", "ARR $40B — 계약 수입 아님(C-07)")},
}
# 비상장 2사 원자료(규칙 ⑥ 비상장 절)
LEGACY_PRIVATE: dict[str, dict[str, tuple[float | None, str, str]]] = {
    "anthropic": {"post_money_valuation": (965e9, "verified_legacy", "$965B"), "arr": (65e9, "verified_legacy", "ARR $65B(7월 런레이트)"), "cumulative_raised": (125e9, "verified_legacy", "약 $125B(2021년~)")},
    "openai": {"post_money_valuation": (852e9, "verified_legacy", "$852B"), "arr": (40e9, "verified_legacy", "런레이트 $40B+(8/20)"), "cumulative_raised": (185e9, "verified_legacy", "약 $180~190B(중간값)")},
}
# ⑥ NTM PER 산출 방법(규칙 ⑥ 절): TSMC·Alibaba 는 연간 EPS 가중 근사, 나머지는 StockAnalysis Forward PE 를 역산으로 NTM 확인
PROXY_NTM_COMPANIES = {"tsmc", "alibaba"}
# ⑨ 게이트 판단 입력(규칙 ⑨ v1.5 적용표)
LEGACY_GATE_INPUTS: dict[str, dict[str, str]] = {
    "nvidia": {"fcf_trend": "stable", "operating_result_reviewed": "profit"},
    "tsmc": {"fcf_trend": "stable", "operating_result_reviewed": "profit"},
    "apple": {"fcf_trend": "stable", "operating_result_reviewed": "profit"},
    "microsoft": {"fcf_trend": "stable", "operating_result_reviewed": "profit"},
    "palantir": {"fcf_trend": "stable", "operating_result_reviewed": "profit"},
    "meta": {"fcf_trend": "deteriorating", "operating_result_reviewed": "profit"},
    "alphabet": {"fcf_trend": "deteriorating", "operating_result_reviewed": "profit"},
    "tesla": {"fcf_trend": "deteriorating", "operating_result_reviewed": "profit"},
    "amazon": {"fcf_trend": "unknown", "operating_result_reviewed": "profit", "coverage_comparable": "unknown"},
    "alibaba": {"fcf_trend": "unknown", "operating_result_reviewed": "unknown", "coverage_comparable": "unknown"},  # 6월 분기 흑자 복귀는 단일 분기 → TTM 부호 미확인(C-20, Anthropic 과 같은 잣대)
    "oracle": {"fcf_trend": "unknown", "operating_result_reviewed": "profit", "coverage_comparable": "yes"},
    "spacex-xai": {"fcf_trend": "unknown", "operating_result_reviewed": "loss", "coverage_comparable": "unknown"},
    "anthropic": {"fcf_trend": "unknown", "operating_result_reviewed": "unknown", "coverage_comparable": "no", "fcf_not_disclosed_reason": "reason:anthropic.fcf_not_disclosed"},
    "openai": {"fcf_trend": "unknown", "operating_result_reviewed": "loss", "bep_retreat": "yes", "coverage_comparable": "no", "fcf_not_disclosed_reason": "reason:openai.fcf_not_disclosed"},
}
# 2026-09-16 FIX-56 2단계: `fcf_not_disclosed_reason` 은 **표시용 라벨**이고 관측 id 가 아니다.
# `reason:` 접두사로 구별한다 — 실재 관측 id 는 calc_f9 가 reason_observation_id 로 따로 찍는다.
# ③ 사다리 판정표(규칙 ③ 절) — ✅ pass / ⚠️ partial / ❌ fail
LEGACY_F3: dict[str, tuple[str, str, str]] = {
    "amazon": ("fail", "pass", "pass"), "microsoft": ("fail", "pass", "pass"), "alphabet": ("fail", "pass", "partial"),
    "meta": ("partial", "pass", "partial"), "anthropic": ("partial", "pass", "fail"), "alibaba": ("partial", "pass", "pass"),
    "palantir": ("partial", "partial", "pass"), "apple": ("fail", "pass", "fail"), "nvidia": ("fail", "pass", "fail"),
    "spacex-xai": ("partial", "pass", "pass"), "tesla": ("fail", "pass", "pass"), "openai": ("fail", "fail", "pass"),
    "tsmc": ("pass", "fail", "pass"), "oracle": ("fail", "pass", "pass"),
}
# ⑤ 별표 G 판정표 — (A, H)
LEGACY_F5: dict[str, tuple[int, int]] = {
    "anthropic": (2, 0), "alphabet": (2, -1), "amazon": (2, -1), "microsoft": (2, -1), "tsmc": (2, -1), "meta": (1, -1),
    "alibaba": (1, -1), "apple": (1, -1), "spacex-xai": (1, -1), "palantir": (1, -2), "openai": (2, -3), "tesla": (0, -1),
    "nvidia": (1, -2), "oracle": (1, -1),
}
# ⑦ 별표 I 판정표 — (조달 의존 비중, 자기 자금 환류). Anthropic·OpenAI 는 환류 축 근거가 원문에 없어 승계 점수만(C-09)
LEGACY_F7: dict[str, tuple[str, str]] = {
    "meta": ("small", "no"), "alibaba": ("small", "no"), "apple": ("small", "no"), "tsmc": ("small", "no"), "palantir": ("small", "no"), "spacex-xai": ("small", "no"),
    "alphabet": ("small", "yes"), "microsoft": ("small", "yes"), "amazon": ("small", "yes"), "tesla": ("small", "yes"),
    "nvidia": ("large", "yes"), "oracle": ("large", "yes"),
}


# ---------------------------------------------------------------- JS 리터럴 파서

class _JS:
    def __init__(self, text: str, pos: int):
        self.text = text
        self.pos = pos

    def peek(self) -> str:
        return self.text[self.pos] if self.pos < len(self.text) else ""

    def skip(self) -> None:
        while self.pos < len(self.text):
            ch = self.text[self.pos]
            if ch in " \t\r\n":
                self.pos += 1
            elif self.text.startswith("//", self.pos):
                end = self.text.find("\n", self.pos)
                self.pos = len(self.text) if end == -1 else end + 1
            else:
                break

    def value(self) -> Any:
        self.skip()
        ch = self.peek()
        if ch == "[":
            return self.array()
        if ch == "{":
            return self.obj()
        if ch in "'\"":
            return self.string()
        if ch == "-" or ch.isdigit():
            return self.number()
        for literal, py in (("true", True), ("false", False), ("null", None)):
            if self.text.startswith(literal, self.pos):
                self.pos += len(literal)
                return py
        raise SchemaError(f"JS 리터럴 파싱 실패 @{self.pos}: {self.text[self.pos:self.pos + 30]!r}")

    def array(self) -> list[Any]:
        assert self.peek() == "["
        self.pos += 1
        out: list[Any] = []
        while True:
            self.skip()
            if self.peek() == "]":
                self.pos += 1
                return out
            out.append(self.value())
            self.skip()
            if self.peek() == ",":
                self.pos += 1

    def obj(self) -> dict[str, Any]:
        assert self.peek() == "{"
        self.pos += 1
        out: dict[str, Any] = {}
        while True:
            self.skip()
            if self.peek() == "}":
                self.pos += 1
                return out
            match = re.match(r"[A-Za-z_$][\w$]*", self.text[self.pos:])
            if match:
                key = match.group(0)
                self.pos += len(key)
            else:
                key = str(self.string())
            self.skip()
            if self.peek() != ":":
                raise SchemaError(f"JS 객체 키 뒤 ':' 없음 @{self.pos}")
            self.pos += 1
            out[key] = self.value()
            self.skip()
            if self.peek() == ",":
                self.pos += 1

    def string(self) -> str:
        quote = self.peek()
        self.pos += 1
        buf: list[str] = []
        while self.pos < len(self.text):
            ch = self.text[self.pos]
            if ch == "\\":
                nxt = self.text[self.pos + 1]
                buf.append({"n": "\n", "t": "\t"}.get(nxt, nxt))
                self.pos += 2
                continue
            if ch == quote:
                self.pos += 1
                return "".join(buf)
            buf.append(ch)
            self.pos += 1
        raise SchemaError("JS 문자열이 닫히지 않음")

    def number(self) -> float | int:
        match = re.match(r"-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?", self.text[self.pos:])
        if not match:
            raise SchemaError(f"숫자 파싱 실패 @{self.pos}")
        self.pos += len(match.group(0))
        raw = match.group(0)
        return float(raw) if ("." in raw or "e" in raw or "E" in raw) else int(raw)


def extract_js_array(text: str, name: str) -> list[Any]:
    match = re.search(rf"const\s+{re.escape(name)}\s*=\s*\[", text)
    if not match:
        raise SchemaError(f"HTML 에 const {name}=[ 없음")
    parser = _JS(text, match.end() - 1)
    value = parser.value()
    if not isinstance(value, list):
        raise SchemaError(f"{name} 은 배열이어야 함")
    return value


# ---------------------------------------------------------------- 문자열 정규화

TAG_RE = re.compile(r"<[^>]+>")
MARK_RE = re.compile(r"[✱⚠️🆕✅❌⭐ᵃᵇᶜ]|\u2009|\u200b")


def strip_html(value: str) -> str:
    text = TAG_RE.sub("", value)
    text = html_lib.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def clean_cell(value: Any) -> str:
    return strip_html(str(value))


_SCALE = {"T": 1e12, "B": 1e9, "M": 1e6, "K": 1e3}
MONEY_RE = re.compile(r"([+\-−]?)\s*\$\s*([\d,]+(?:\.\d+)?)\s*([TBMK])?")


def parse_money(value: Any) -> float | None:
    text = clean_cell(value)
    match = MONEY_RE.search(text)
    if not match:
        return None
    sign, digits, scale = match.groups()
    number = float(digits.replace(",", "")) * _SCALE.get(scale or "", 1.0)
    return -number if sign in ("-", "−") else number


def parse_number(value: Any) -> float | None:
    text = MARK_RE.sub("", clean_cell(value)).strip()
    match = re.match(r"^[+\-−]?\d+(?:\.\d+)?", text)
    if not match:
        return None
    return float(match.group(0).replace("−", "-"))


def parse_pct(value: Any) -> float | None:
    text = clean_cell(value)
    match = re.search(r"([+\-−]?\d+(?:\.\d+)?)\s*%", text)
    if not match:
        return None
    return float(match.group(1).replace("−", "-")) / 100.0


def parse_years(value: Any) -> float | None:
    text = clean_cell(value)
    match = re.search(r"(\d+(?:\.\d+)?)\s*년", text)
    return float(match.group(1)) if match else None


def standard_fcf(ocf: float, capex: float) -> float:
    """표준 FCF = OCF - 현금 CapEx. CapEx 는 원출처 부호와 무관하게 지출 크기(양수)로 정규화한다 (T-07)."""
    return ocf - abs(capex)


def split_points(text: str) -> list[str]:
    """원본 splitPts 이식: ' · ' 로 나누되 <b>/<i>/괄호 균형이 깨지면 다음 조각과 합친다."""
    raw = [part.strip() for part in text.split(" · ")]

    def balanced(chunk: str) -> bool:
        return (
            chunk.count("<b>") == chunk.count("</b>")
            and chunk.count("<i>") == chunk.count("</i>")
            and chunk.count("(") == chunk.count(")")
        )

    out: list[str] = []
    buf = ""
    for part in raw:
        buf = f"{buf} · {part}" if buf else part
        if balanced(buf):
            out.append(buf)
            buf = ""
    if buf:
        out.append(buf)
    return [p for p in out if p]


# ---------------------------------------------------------------- MD 순위표

def parse_md_ranking(md_text: str) -> dict[str, dict[str, Any]]:
    section = md_text.split("## 1. 종합 순위표", 1)[1].split("\n## ", 1)[0]
    rows: dict[str, dict[str, Any]] = {}
    for line in section.splitlines():
        if not line.startswith("|") or "---" in line or "순위" in line:
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 14:
            continue
        name = clean_cell(cells[1]).replace("*", "").strip()
        nums = [parse_number(c.replace("*", "")) for c in cells[2:14]]
        rows[name] = {
            "rank": parse_number(cells[0].replace("*", "")),
            "scores": {f: nums[i] for i, f in enumerate(("F1", "F2", "F3", "F4", "F5"))} | {f: nums[i + 6] for i, f in enumerate(("F6", "F7", "F8", "F9"))},
            "moat": nums[5],
            "trap": nums[10],
            "total": nums[11],
        }
    return rows


# ---------------------------------------------------------------- 이관

def _obs(cid: str, metric: str, value: Any, status: str, raw: Any, source_id: str, *, basis: dict[str, Any] | None = None, kind: str = "actual", note: str | None = None, suffix: str = "") -> dict[str, Any]:
    if status == "verified_legacy":
        status = "legacy_unverified"
    if value is None and status in ("verified", "legacy_unverified"):
        status = "parse_failed"
    return {
        "observation_id": f"{cid}.{metric}{suffix}.v15",
        "company_id": cid,
        "metric": metric,
        "value": value,
        "unit": METRICS[metric]["unit"],
        "as_of": BASELINE_AS_OF,
        "kind": kind,
        "source_id": source_id,
        "status": status,
        "basis": basis,
        "raw": None if raw is None else clean_cell(raw),
        "note": note,
    }


def import_baseline(html_path: Path, md_path: Path, out_dir: Path, companies: dict[str, dict[str, Any]]) -> dict[str, Any]:
    # 2026-10-01 레인 N 소유 밖 발견 2: 판정이 CLI 에만 있으면 import 로 이 함수를 직접 부를 때 지나간다. 본체에서 판정한다.
    # stages 가 이 모듈을 import 하므로 함수 안에서 가져온다. 기준선 id 는 기록할 폴더 이름(v1.5)이다.
    from .stages import protect_baseline_consumers

    protect_baseline_consumers(out_dir.name)
    text = html_path.read_text(encoding="utf-8")
    md_text = md_path.read_text(encoding="utf-8")
    D = extract_js_array(text, "D")
    VAL = extract_js_array(text, "VAL")
    EARN = extract_js_array(text, "EARN")
    FIN = extract_js_array(text, "FIN")
    BORR = extract_js_array(text, "BORR")
    TRIG = extract_js_array(text, "TRIG")
    md_rows = parse_md_ranking(md_text)
    report: dict[str, Any] = {"issues": [], "parse_failed": [], "matched": 0, "companies": []}

    def issue(message: str) -> None:
        report["issues"].append(message)

    scores: list[dict[str, Any]] = []
    observations: list[dict[str, Any]] = []
    seen: set[str] = set()
    for entry in D:
        raw_name = str(entry["name"])
        cid = resolve_company_id(strip_html(raw_name), companies)
        if cid is None:
            issue(f"D: 알 수 없는 기업명 {raw_name!r}")
            continue
        if cid in seen:
            issue(f"D: 기업 중복 {cid}")
        seen.add(cid)
        s = [int(v) for v in entry["s"]]
        t = [int(v) for v in entry["t"]]
        factor_scores = {f: s[i] for i, f in enumerate(("F1", "F2", "F3", "F4", "F5"))} | {f: t[i] for i, f in enumerate(("F6", "F7", "F8", "F9"))}
        moat, trap = sum(s), sum(t)
        evidence = {f: [strip_html(p) for p in split_points(entry["r"][i])] for i, f in enumerate(("F1", "F2", "F3", "F4", "F5"))}
        evidence |= {f: [strip_html(p) for p in split_points(entry["rt"][i])] for i, f in enumerate(("F6", "F7", "F8", "F9"))}
        md_row = md_rows.get(companies[cid]["display_name"]) or next((row for name, row in md_rows.items() if resolve_company_id(name, companies) == cid), None)
        md_status = "missing"
        if md_row:
            md_status = "match"
            for f in FACTORS:
                if md_row["scores"][f] != factor_scores[f]:
                    md_status = "mismatch"
                    issue(f"{cid} {f}: HTML {factor_scores[f]} != MD {md_row['scores'][f]}")
            if md_row["total"] != moat + trap:
                md_status = "mismatch"
                issue(f"{cid} 조정총점: HTML {moat + trap} != MD {md_row['total']}")
            if md_row["rank"] != entry.get("rank"):
                issue(f"{cid} 순위: HTML {entry.get('rank')} != MD {md_row['rank']}")
        else:
            issue(f"{cid}: MD 순위표에 행 없음")
        scores.append({
            "company_id": cid,
            "display_name_raw": raw_name,
            "type_raw": entry.get("type"),
            "cap_usd_t": entry.get("cap"),
            "rank_raw": entry.get("rank"),
            "tag": strip_html(str(entry.get("tag", ""))),
            "scores": factor_scores,
            "moat": moat,
            "trap": trap,
            "total": moat + trap,
            "evidence": evidence,
            "md_crosscheck": md_status,
        })
        report["matched"] += 1
        # D.cap 은 표시용 반올림 시총이라 관측으로 넣지 않는다(VAL 표가 원자료). 비상장사는 post_money_valuation 으로 이관한다.

    # VAL: [기업, 주가, 시총, NTM PER, ⑥, 경계, TTM PER, 영업외 비중, P/S]
    for row in VAL:
        cid = resolve_company_id(strip_html(str(row[0])), companies)
        if cid is None:
            issue(f"VAL: 알 수 없는 기업 {row[0]!r}")
            continue
        observations.append(_obs(cid, "price", parse_money(row[1]), "verified_legacy", row[1], SRC_HTML, basis={"share_basis": companies[cid]["share_basis"], "currency": "USD"}))
        observations.append(_obs(cid, "market_cap", parse_money(row[2]), "verified_legacy", row[2], SRC_HTML))
        method = "annual_weighted_proxy" if cid in PROXY_NTM_COMPANIES else "vendor_forward_pe_verified_ntm"
        per = parse_number(row[3])
        observations.append(_obs(cid, "ntm_per", per, "verified_legacy", row[3], SRC_HTML, basis={"method": method, "vendor": "StockAnalysis Forward PE (2026-09-02)"}, kind="estimate"))
        ttm = parse_number(row[6])
        observations.append(_obs(cid, "ttm_per", ttm, "verified_legacy" if ttm is not None else "not_disclosed", row[6], SRC_HTML, note=None if ttm is not None else "적자"))
        nonop = parse_pct(row[7])
        observations.append(_obs(cid, "nonop_share", nonop, "verified_legacy" if nonop is not None else "not_disclosed", row[7], SRC_HTML))
        observations.append(_obs(cid, "ps_ratio", parse_number(row[8]), "verified_legacy", row[8], SRC_HTML))

    # FIN: [기업, 현금, TTM FCF, 런웨이, 순현금/순부채, 상환 연수, D/EBITDA, 부외 포함, 신용, 부외 약정, 매출대비, 비상장]
    for row in FIN:
        cid = resolve_company_id(strip_html(str(row[0])), companies)
        if cid is None:
            issue(f"FIN: 알 수 없는 기업 {row[0]!r}")
            continue
        private = int(row[11]) == 1
        cash = parse_money(row[1])
        observations.append(_obs(cid, "cash", cash, "not_disclosed" if cash is None else "verified_legacy", row[1], SRC_HTML))
        fcf = parse_money(row[2])
        observations.append(_obs(cid, "fcf_ttm", fcf, "not_disclosed" if fcf is None else "verified_legacy", row[2], SRC_HTML, note="비상장 FCF 미공시" if private and fcf is None else None))
        runway = parse_years(row[3])
        runway_raw = clean_cell(row[3])
        if runway is not None:
            runway_status, runway_note = "verified_legacy", "원본 계산값(현금 ÷ 연 소진)"
        elif "∞" in runway_raw:
            # FCF 양수라 소진율이 없다. 미공시가 아니라 산식 적용 대상이 아니다.
            runway_status, runway_note = "not_applicable", "TTM FCF 흑자라 런웨이 산식 적용 대상 아님(원문 ∞)"
        else:
            runway_status, runway_note = "not_disclosed", f"FCF 미공시로 소진율을 만들 수 없음(원문 {runway_raw or '미상'})"
        observations.append(_obs(cid, "runway_years", runway, runway_status, row[3], SRC_HTML, kind="derived", note=runway_note))
        net_cash = parse_money(row[4])
        observations.append(_obs(cid, "net_cash", net_cash, "verified_legacy" if net_cash is not None else "not_disclosed", row[4], SRC_HTML))
        de = parse_number(row[6])
        observations.append(_obs(cid, "debt_ebitda", de, "verified_legacy" if de is not None else "not_disclosed", row[6], SRC_HTML))
        rating = clean_cell(row[8])
        observations.append(_obs(cid, "credit_rating", rating or None, "verified_legacy" if rating else "not_disclosed", row[8], SRC_HTML, kind="text", note="별표 J 교차검증 전용 — 점수 입력 아님"))
        observations.append(_obs(cid, "offbalance_note", clean_cell(row[9]) or None, "verified_legacy", row[9], SRC_HTML, kind="text", note="부외 약정 원문(A/B/C 분류 전)"))

    # BORR: [기업, 순차입, capex, 비율]
    for row in BORR:
        cid = resolve_company_id(strip_html(str(row[0])), companies)
        if cid is None:
            issue(f"BORR: 알 수 없는 기업 {row[0]!r}")
            continue
        nb = parse_money(row[1])
        observations.append(_obs(cid, "net_borrowing_ttm", nb, "verified_legacy" if nb is not None else "not_disclosed", row[1], SRC_HTML, note="차환 제외 순증"))
        observations.append(_obs(cid, "capex_ttm", parse_money(row[2]), "verified_legacy", row[2], SRC_HTML))

    # EARN: [기업, 분기, 매출, EPS, FCF, ⑨] — 분기 원문은 텍스트로 보존, ⑨ 열은 교차검증
    earn_f9: dict[str, float | None] = {}
    for row in EARN:
        cid = resolve_company_id(strip_html(str(row[0])), companies)
        if cid is None:
            issue(f"EARN: 알 수 없는 기업 {row[0]!r}")
            continue
        observations.append(_obs(cid, "quarter_note", " | ".join(clean_cell(c) for c in row[1:5]), "verified_legacy", None, SRC_HTML, kind="text", note="최근 분기 실적 원문(③⑨ 참고). TTM 대체 금지"))
        earn_f9[cid] = parse_number(row[5])
        if cid == "spacex-xai":
            margin = parse_pct(clean_cell(row[3]).split("영업적자")[-1]) if "영업적자" in clean_cell(row[3]) else None
            observations.append(_obs(cid, "operating_margin_ttm", margin, "verified_legacy" if margin is not None else "parse_failed", row[3], SRC_HTML, note="EARN 열의 영업적자율. 규칙 ⑨ 표는 -14.9% 를 TTM 손실률로 사용"))

    # 규칙 원문 표에서 온 G4·비상장 원자료
    for cid, metrics in LEGACY_GATE4.items():
        for metric, (value, status, raw) in metrics.items():
            observations.append(_obs(cid, metric, value, status, raw, SRC_RULE, note="규칙 v1.5 ⑨ 게이트 4 적용표"))
    for cid, metrics in LEGACY_PRIVATE.items():
        for metric, (value, status, raw) in metrics.items():
            observations.append(_obs(cid, metric, value, status, raw, SRC_RULE, kind="run_rate" if metric == "arr" else "actual", note="규칙 v1.5 ⑥ 비상장 절"))

    for obs in observations:
        if obs["status"] == "parse_failed":
            report["parse_failed"].append(f"{obs['observation_id']}: {obs['raw']!r}")

    for entry in scores:
        cid = entry["company_id"]
        if cid in earn_f9 and earn_f9[cid] is not None and int(earn_f9[cid]) != entry["scores"]["F9"]:
            issue(f"{cid} F9: D {entry['scores']['F9']} != EARN 표 {earn_f9[cid]}")

    triggers = [
        {"trigger_id": f"TRIG-{idx + 1:03d}", "title": strip_html(str(row[0])), "why": strip_html(str(row[1])), "impact_raw": strip_html(str(row[2])),
         "status": "legacy", "note": "impact_raw 의 예상 점수는 저장값이 아니라 원문 문장(C-14). 사건 확인 후 현재 규칙으로 재계산"}
        for idx, row in enumerate(TRIG)
    ]

    baseline = {
        "schema": "scorecard.baseline/1",
        "baseline_id": BASELINE_ID,
        "as_of": BASELINE_AS_OF,
        "rule_version": "v1.5",
        "source": {"html": html_path.name, "html_sha256": sha256_file(html_path), "md": md_path.name, "md_sha256": sha256_file(md_path)},
        "status": "legacy_unverified",
        "companies": sorted(scores, key=lambda s: (-s["total"], s["company_id"])),
    }
    obs_payload = {"schema": "scorecard.observations/1", "run_id": f"baseline-{BASELINE_ID}", "as_of": BASELINE_AS_OF, "items": observations,
                   "note": "v1.5 HTML/규칙 원문에서 이관. status=legacy_unverified 는 이번 실행에서 재검증되지 않은 과거 기록"}
    trig_payload = {"schema": "scorecard.triggers/1", "baseline_id": BASELINE_ID, "items": triggers}
    out_dir.mkdir(parents=True, exist_ok=True)
    write_json(out_dir / "scores.json", baseline)
    write_json(out_dir / "observations.json", obs_payload)
    write_json(out_dir / "triggers.json", trig_payload)
    report["companies"] = [{"company_id": s["company_id"], "total": s["total"], "md": s["md_crosscheck"]} for s in baseline["companies"]]
    status_counts: dict[str, int] = {}
    for obs in observations:
        status_counts[obs["status"]] = status_counts.get(obs["status"], 0) + 1
    report["status_summary"] = " · ".join(f"`{k}` {v}건" for k, v in sorted(status_counts.items(), key=lambda kv: -kv[1]))
    report["observations"] = len(observations)
    report["triggers"] = len(triggers)
    (out_dir / "import-report.md").write_text(render_import_report(report, baseline), encoding="utf-8")
    return report


def baseline_judgments(baseline: dict[str, Any], run_id: str, companies: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    """기준선 점수·규칙 판정표를 승계 판단으로 변환한다. 산식 factor 는 입력을, 정성 factor 는 점수를 승계한다."""
    items: list[dict[str, Any]] = []
    for entry in baseline["companies"]:
        cid = entry["company_id"]
        sc = entry["scores"]
        ev = entry["evidence"]
        common = {"reviewer": "legacy:v1.5", "reviewed_at": BASELINE_AS_OF, "status": "carried", "carried_from": f"baseline:{BASELINE_ID}", "source_ids": [SRC_HTML]}

        def add(factor: str, kind: str, inputs: dict[str, Any], score: int | None, note: str | None = None) -> None:
            items.append({"judgment_id": f"{cid}.{factor}", "company_id": cid, "factor": factor, "kind": kind, "score": score, "inputs": inputs,
                          "evidence": ev.get(factor, []), "counter_evidence": [], "note": note, **common})

        add("F1", "score", {}, sc["F1"])
        add("F2", "score", {}, sc["F2"], "C-03: 경로 매핑 미확정 — 승계 점수")
        im, rm, ac = LEGACY_F3[cid]
        add("F3", "criteria", {"imitation": im, "revenue_model": rm, "acceleration": ac, "door_closed": "fail"}, None, "규칙 v1.5 ③ 판정표")
        add("F4", "score", {}, sc["F4"])
        A, H = LEGACY_F5[cid]
        add("F5", "grade", {"A": A, "H": H}, None, "규칙 v1.5 별표 G 판정표")
        if not companies[cid]["listed"]:
            add("F6", "score", {"private": True}, sc["F6"], "C-12: 비상장 정성 예외(TTM 보정·자본효율 근거는 원문)")
        if cid in LEGACY_F7:
            share, returns = LEGACY_F7[cid]
            add("F7", "matrix", {"funding_dependent_share": share, "own_money_returns": returns}, None, "규칙 v1.5 별표 I 판정표")
        else:
            add("F7", "score", {}, sc["F7"], "C-09: 매트릭스 입력(환류 여부) 원문 없음 — 승계 점수")
        add("F8", "score", {}, sc["F8"])
        gi = {"fcf_trend": "unknown", "bep_retreat": "no", "buffer_erosion": "no", "direction_A": "unknown", "direction_B": "unknown", "coverage_comparable": "unknown"}
        gi.update(LEGACY_GATE_INPUTS.get(cid, {}))
        add("F9", "gate_inputs", gi, None, "규칙 v1.5 ⑨ 적용표(추세·BEP·커버리지 비교 가능성)")
    return items


def render_import_report(report: dict[str, Any], baseline: dict[str, Any]) -> str:
    lines = [
        f"# 기준선 이관 보고 — {baseline['baseline_id']}",
        "",
        f"- 원본 HTML SHA-256: `{baseline['source']['html_sha256']}`",
        f"- 원본 MD SHA-256: `{baseline['source']['md_sha256']}`",
        f"- 기업 {report['matched']}개, 관측 {report['observations']}건, 트리거 {report['triggers']}건을 이관했다.",
        "- 관측 상태 분포: " + report["status_summary"] + ". 어느 것도 이번 실행에서 재검증된 사실이 아니며 점수 정정도 하지 않았다(D-08).",
        "- `not_applicable` 은 산식 적용 대상이 아님(FCF 흑자의 런웨이)이고 `not_disclosed` 는 실제 미공시다. 둘을 한 상태로 묶지 않는다.",
        "",
        "## HTML D ↔ MD 순위표 대조",
        "",
        "| 기업 | 조정총점 | 대조 |",
        "|---|---:|---|",
    ]
    for row in report["companies"]:
        lines.append(f"| {row['company_id']} | {row['total']} | {row['md']} |")
    lines += ["", "## 불일치·주의", ""]
    notes = list(report["issues"])
    notes.append("시총: HTML D.cap(예: Alphabet 4.173T)과 3-1a 표(VAL, $4.12T)가 9개사에서 다르다. 차이의 원인은 원문에 적혀 있지 않으므로 반올림으로 단정하지 않고, 원자료 표가 있는 VAL 값을 선택 정책으로 채택해 D.cap 은 관측으로 넣지 않았다")
    notes.append("Menlo Ventures 보고서: 원문 MD 에만 이해상충 사유와 함께 ①채점 제외로 언급되고 HTML 배열에는 없다. 관측·판단 어느 쪽으로도 이관하지 않았다")
    notes.append("Meta ⑨: 원문이 TTM FCF +$41B 와 분기 +$0.78B(-91%)를 함께 적는다. 이관은 TTM 만 관측으로 두고 분기 수치는 근거 문장에 남겼다")
    notes.append("⑥ 경계 트리거: 원문 트리거는 경계 ⚠️ 를 TSMC·Palantir 2개사로 적지만, 활성 경계(20·29·42·62·90)로 재계산하면 이번 실행에서 플래그가 서는 곳과 다를 수 있다. 트리거 문장은 원문 그대로 두고 재계산 결과와 대조해 읽는다")
    lines += [f"- {item}" for item in notes]
    lines += ["", "## 파싱 실패(원문 보존)", ""]
    if report["parse_failed"]:
        lines += [f"- {item}" for item in report["parse_failed"]]
    else:
        lines.append("- 없음")
    lines += [
        "",
        "## 이관 시 적용한 분류(규칙 원문 표에서 읽음)",
        "",
        "- ⑥ NTM 방법: TSMC·Alibaba 는 `annual_weighted_proxy`(C-13), 나머지 상장사는 `vendor_forward_pe_verified_ntm`.",
        "- 시총: D.cap 과 VAL 의 차이는 원천이 다른 값으로 보고 VAL 만 이관한다(위 불일치·주의 참고).",
        "- 런웨이: FCF 흑자 8사의 원문 `∞` 는 `not_applicable`, 비상장 2사의 `판정 불가` 는 `not_disclosed` 로 나눠 이관한다.",
        "- ⑨ G4: Oracle(리스 $250B / RPO $638B)·Amazon(미개시 리스 $106B / 백로그 숫자 미공시)은 규칙 표 값. Anthropic·OpenAI 의 ARR·컴퓨트 약정은 `incompatible_basis`(C-07).",
        "- ⑨ G1: Anthropic·Alibaba 는 단일 분기 흑자(전환)라 TTM 부호 `unknown`(C-20). SpaceX 손실률 -14.9% 는 EARN 열에서 이관.",
        "- ⑨ G4: coverage_comparable 은 검토 입력이라 Oracle 만 `yes`(RPO vs 리스, 원문 판정). Amazon·Alibaba·SpaceX 는 `unknown`(판단 대기), Anthropic·OpenAI 는 `no`(C-07).",
        "- ③·⑤·⑦ 입력은 규칙 v1.5 판정표(③ 사다리, 별표 G, 별표 I)를 승계. Anthropic·OpenAI ⑦은 환류 축 근거가 없어 승계 점수(C-09).",
        "",
    ]
    return "\n".join(lines)
