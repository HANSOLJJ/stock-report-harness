# scorecard 데이터 계약(companies·rules·observations·judgments·sources·evidence·triggers·run·approval)의 엄격 파서와 정규 해시 유틸
from __future__ import annotations

import hashlib
import json
import math
import os
import re
from pathlib import Path
from typing import Any, Iterable

FACTOR_IDS: tuple[str, ...] = ("F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9")
MOAT_FACTORS: tuple[str, ...] = ("F1", "F2", "F3", "F4", "F5")
TRAP_FACTORS: tuple[str, ...] = ("F6", "F7", "F8", "F9")

COMPANY_TYPES = {"소비자", "업무", "거래", "부품", "소비자·업무", "혼합"}
# 2026-09-21 ADD-01: 레지스트리 항목의 키 목록. `validate_companies` 와 `registry.add_company`·CLI 가
# **같은 상수**를 본다 — 두 곳에 따로 적으면 한쪽만 고쳐져 조용히 갈린다.
COMPANY_REQUIRED_KEYS = ["company_id", "display_name", "aliases", "type", "listed", "ticker",
                         "exchange", "share_basis", "adr_ratio", "reporting_currency", "scope"]
# 2026-09-30 레인 E: `cik`·`news_queries` 는 수집기만 읽는다. calc·aggregate 가 읽지 않으므로 results_hash 는 불변이다.
COMPANY_OPTIONAL_KEYS = ["reference", "note", "status", "cik", "news_queries"]
# `registry.set_company_field` 가 바꿀 수 있는 키. 나머지 키는 사람이 레지스트리를 직접 고친다.
COMPANY_SETTABLE_KEYS = ("cik", "news_queries")
SHARE_BASIS_VALUES = {"common", "adr", "ads", "private"}
OBSERVATION_STATUSES = {
    "verified",
    "legacy_unverified",
    "not_applicable",   # 산식 적용 대상이 아님(예: FCF 양수라 런웨이 계산 안 함). 사유를 note 에 남긴다
    "not_disclosed",
    "collection_failed",
    "source_conflict",
    "incompatible_basis",
    "parse_failed",
}
# B: 기간이 있어야 의미가 서는 흐름(flow) 지표. 신규 verified 관측은 period 를 요구한다.
PERIOD_REQUIRED_METRICS = {
    "revenue_ttm", "operating_income_ttm", "operating_margin_ttm",
    "ocf_ttm", "capex_ttm", "fcf_ttm", "net_borrowing_ttm",
    "net_income_ttm", "revenue_ttm_prior", "pretax_income_ttm", "revenue_ttm_full",
    # 분기 EPS 는 어느 분기인지가 값의 일부다. 기간 없이는 4분기 연속 판정을 할 수 없다.
    "ntm_eps_quarter",
}
OBSERVATION_KINDS = {"actual", "estimate", "run_rate", "derived", "text"}
# 결측 유형. status=not_disclosed 하나가 네 뜻(미확인·미공시·계산 대상 아님·산출 불가)으로 쓰여
# calc_f9._g4 의 C-16 진입 판별이 무너졌다(MISS-LABEL-23). 값이 없는 이유를 라벨이 직접 말하게 한다.
#
#   unverified              우리가 확인하지 않았다. 조사하면 값이 있을 수 있다
#   not_disclosed_confirmed 확인된 미공시. 회사가 내지 않는다 — **C-16 은 여기에만 걸린다**
#   not_applicable          산식 적용 대상이 아니다. 개념상 정의되지 않는다(FCF 양수의 런웨이, 적자의 PER)
#   indeterminate           산출 대상이나 선행 입력이 결측이라 만들 수 없다
MISSING_TYPES = {"unverified", "not_disclosed_confirmed", "not_applicable", "indeterminate"}
# C-16(약정 커버리지 결측 정책)이 걸리는 유일한 유형. 우리가 안 찾은 것을 그 기업의 위험으로 둔갑시키지 않는다.
MISSING_TYPE_FOR_DISCLOSURE_POLICY = "not_disclosed_confirmed"
JUDGMENT_KINDS = {"score", "grade", "criteria", "matrix", "paths", "gate_inputs"}
JUDGMENT_STATUSES = {"new", "carried"}
TRI = {"pass", "partial", "fail", "unknown"}
YES_NO = {"yes", "no", "unknown"}
PASS_FAIL = {"pass", "fail", "unknown"}

# factor별 허용 판단 종류. score는 정성 factor와 비상장 F6, 그리고 승계(carried) 전용 예외에만 허용한다.
FACTOR_JUDGMENT_KINDS: dict[str, set[str]] = {
    "F1": {"score"},
    "F2": {"paths", "score"},
    "F3": {"criteria"},
    "F4": {"score"},
    "F5": {"grade"},
    "F6": {"score"},
    "F7": {"matrix", "score"},
    "F8": {"score"},
    "F9": {"gate_inputs"},
}

# 2026-10-01 레인 J: 사람이 승인 페이지(`judge`)에서 고치는 정성 판단 입력. 점수가 아니라 판단 입력을 고친다.
# F1·F4·F8 은 score 와 근거를, 나머지는 판정 재료(inputs)를 고친다 — 그 factor 들의 점수는 규칙이 계산한다.
# F2(경로 매핑)·F6(가격·비상장) 은 이번 범위가 아니다.
JUDGMENT_EDIT_KIND: dict[str, str] = {
    "F1": "score", "F4": "score", "F8": "score",
    "F3": "criteria", "F5": "grade", "F7": "matrix", "F9": "gate_inputs",
}
# 판정 종류별로 고칠 수 있는 입력 키와 허용값. 검증은 `_validate_judgment_inputs` 가 하고 이 표는 입력란을 그린다.
JUDGMENT_INPUT_CHOICES: dict[str, dict[str, list[Any]]] = {
    "criteria": {"imitation": ["pass", "partial", "fail", "unknown"], "revenue_model": ["pass", "partial", "fail", "unknown"],
                 "acceleration": ["pass", "partial", "fail", "unknown"], "door_closed": ["pass", "fail", "unknown"]},
    "grade": {"A": [0, 1, 2], "H": [0, -1, -2, -3]},
    "matrix": {"funding_dependent_share": ["large", "small", "unknown"], "own_money_returns": ["yes", "no", "unknown"]},
    "gate_inputs": {"fcf_trend": ["stable", "deteriorating", "unknown"], "bep_retreat": ["yes", "no", "unknown"],
                    "buffer_erosion": ["yes", "no", "unknown"], "direction_A": ["pass", "fail", "unknown"],
                    "direction_B": ["pass", "fail", "unknown"], "coverage_comparable": ["yes", "no", "unknown"],
                    "operating_result_reviewed": ["profit", "loss", "unknown"]},
}
# revision_history 한 칸이 보존하는 이전 값의 키.
JUDGMENT_REVISION_FIELDS = ("kind", "score", "inputs", "evidence", "status", "reviewer", "reviewed_at")

# 지표 카탈로그. unit은 표시·검증용이고 number 지표만 계산에 쓴다.
METRICS: dict[str, dict[str, str]] = {
    "price": {"unit": "USD/share", "type": "number"},
    "market_cap": {"unit": "USD", "type": "number"},
    "ntm_eps": {"unit": "USD/share", "type": "number"},
    # 미발표 회계분기별 EPS 컨센서스. 4개가 모여야 NTM 이 되며 부분 확보는 점수를 만들지 않는다 (F6 정책).
    "ntm_eps_quarter": {"unit": "USD/share", "type": "number"},
    "ntm_per": {"unit": "ratio", "type": "number"},
    "ttm_per": {"unit": "ratio", "type": "number"},
    "nonop_share": {"unit": "ratio", "type": "number"},
    "ps_ratio": {"unit": "ratio", "type": "number"},
    "revenue_ttm": {"unit": "USD", "type": "number"},
    # 2026-09-16 FIX-56 1단계: `revenue_ttm` 이 신규 상장사에서 **분기값**으로 등록된다(P3 의 전년 동기 대조를 세우려고).
    # P2 는 12개월 매출이 필요하므로 같은 이름에 두 뜻을 담지 않고 지표를 나눈다.
    "revenue_ttm_full": {"unit": "USD", "type": "number"},
    "operating_income_ttm": {"unit": "USD", "type": "number"},
    # 세전이익. `nonop_share = (세전 − 영업이익) / 세전` 의 분모이자 분자 구성요소다.
    # 법인세를 순이익에 되더하는 대신 이것을 직접 들이면 지표 하나로 끝난다(NONOP-44).
    "pretax_income_ttm": {"unit": "USD", "type": "number"},
    # F6 v1.7 신규 3종. revenue_ttm·operating_income_ttm 은 이미 있어 다시 만들지 않는다.
    "net_income_ttm": {"unit": "USD", "type": "number"},
    "revenue_ttm_prior": {"unit": "USD", "type": "number"},
    "arr_prior": {"unit": "USD", "type": "number"},
    "operating_margin_ttm": {"unit": "ratio", "type": "number"},
    "ocf_ttm": {"unit": "USD", "type": "number"},
    "capex_ttm": {"unit": "USD", "type": "number"},
    "fcf_ttm": {"unit": "USD", "type": "number"},
    "cash": {"unit": "USD", "type": "number"},
    "undrawn_credit": {"unit": "USD", "type": "number"},
    "net_cash": {"unit": "USD", "type": "number"},
    # net_cash 의 구성요소. 값 자체는 P2 가 읽지 않고 **없을 때 왜 없는지**를 기록하려고 둔다.
    # apple 은 리스를 10-K 에만, palantir 는 유동분을 태깅하지 않아 net_cash 실측이 막힌다(NETCASH-37).
    "lease_liabilities": {"unit": "USD", "type": "number"},
    "net_borrowing_ttm": {"unit": "USD", "type": "number"},
    "debt_ebitda": {"unit": "ratio", "type": "number"},
    "credit_rating": {"unit": "text", "type": "text"},
    "cds_5y_bp": {"unit": "bp", "type": "number"},
    "offbalance_B": {"unit": "USD", "type": "number"},
    "offbalance_note": {"unit": "text", "type": "text"},
    "contracted_revenue": {"unit": "USD", "type": "number"},
    "runway_years": {"unit": "years", "type": "number"},
    "post_money_valuation": {"unit": "USD", "type": "number"},
    "arr": {"unit": "USD", "type": "number"},
    "ttm_revenue_est": {"unit": "USD", "type": "number"},
    "cumulative_raised": {"unit": "USD", "type": "number"},
    "quarter_note": {"unit": "text", "type": "text"},
}

NON_NEGATIVE_METRICS = {"price", "market_cap", "revenue_ttm", "revenue_ttm_full", "capex_ttm", "cash", "undrawn_credit", "offbalance_B", "contracted_revenue", "runway_years", "post_money_valuation", "arr", "ttm_revenue_est", "cumulative_raised", "cds_5y_bp"}
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class SchemaError(ValueError):
    """구조화 파일이 계약을 어길 때 발생. 임의 해석으로 통과시키지 않는다."""


def canonical_json(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_obj(obj: Any) -> str:
    return sha256_text(canonical_json(obj))


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _reject_constant(token: str) -> Any:
    # json 모듈은 기본적으로 NaN/Infinity 를 받아들인다. 계산 입력에 비유한 값을 허용하지 않는다 (R05).
    raise SchemaError(f"JSON 에 비유한 숫자 {token} 은 허용하지 않음")


APPROVAL_FILE = "approval.json"


def approval_file_present(run_dir: Path) -> bool:
    """폴더 목록에 이름이 **정확히** `approval.json` 인 항목이 있는가. 2026-10-01 레인 N(V2-3): Windows 는 대소문자를
    가리지 않아 `(d / "approval.json").is_file()` 이 `Approval.json` 에도 참이다. 승인 여부는 이 함수로 본다."""
    try:
        return APPROVAL_FILE in os.listdir(run_dir)
    except OSError:
        return False


def load_json_strict(path: Path) -> Any:
    if not path.is_file():
        raise SchemaError(f"파일 없음: {path}")
    # 2026-10-01 레인 N(V2-3): 승인 파일은 이름이 정확히 approval.json 일 때만 읽는다. 소유 밖 호출자(build·validate·compare)도
    # 여기를 지나므로 대소문자만 바꾼 파일은 승인으로 읽히지 않고 오류로 멈춘다.
    if path.name.lower() == APPROVAL_FILE and (path.name != APPROVAL_FILE or not approval_file_present(path.parent)):
        found = sorted(n for n in os.listdir(path.parent) if n.lower() == APPROVAL_FILE)
        raise SchemaError(f"승인 파일은 이름이 정확히 {APPROVAL_FILE} 이어야 한다: {path.parent} 에 있는 것은 {found}")
    try:
        return json.loads(path.read_text(encoding="utf-8"), parse_constant=_reject_constant)
    except json.JSONDecodeError as exc:
        raise SchemaError(f"JSON 파싱 실패: {path}: {exc}") from exc


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    # 2026-09-15 FIX-53 RC-07: 텍스트 모드 기본값은 Windows 에서 줄바꿈을 CRLF 로 바꿔 써서 해시가 플랫폼마다 갈렸다.
    # .gitattributes 가 이 파일들을 LF 로 고정하므로 생성기도 LF 로 쓴다.
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=False) + "\n", encoding="utf-8", newline="\n")


def _require(cond: bool, message: str) -> None:
    if not cond:
        raise SchemaError(message)


def _expect_keys(obj: Any, required: Iterable[str], where: str, optional: Iterable[str] = ()) -> dict[str, Any]:
    _require(isinstance(obj, dict), f"{where}: object 여야 함")
    required = list(required)
    optional = list(optional)
    missing = [key for key in required if key not in obj]
    _require(not missing, f"{where}: 필수 키 누락 {missing}")
    unknown = [key for key in obj if key not in required and key not in optional]
    _require(not unknown, f"{where}: 알 수 없는 키 {unknown}")
    return obj


def _is_number(value: Any) -> bool:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    return math.isfinite(value)


def _expect_date(value: Any, where: str, allow_none: bool = False) -> None:
    if value is None and allow_none:
        return
    _require(isinstance(value, str) and bool(DATE_RE.match(value)), f"{where}: YYYY-MM-DD 날짜 필요 ({value!r})")


# ------------------------------------------------------------------ companies

def validate_companies(payload: Any) -> dict[str, dict[str, Any]]:
    _expect_keys(payload, ["schema", "as_of", "companies"], "companies.json", optional=["note", "reference_policy"])
    _require(payload["schema"] == "scorecard.companies/1", "companies.json: schema 불일치")
    _expect_date(payload["as_of"], "companies.json.as_of")
    _require(isinstance(payload["companies"], list) and payload["companies"], "companies.json: companies 비어 있음")
    out: dict[str, dict[str, Any]] = {}
    for idx, item in enumerate(payload["companies"]):
        where = f"companies[{idx}]"
        _expect_keys(item, COMPANY_REQUIRED_KEYS, where, optional=COMPANY_OPTIONAL_KEYS)
        cid = item["company_id"]
        _require(isinstance(cid, str) and bool(ID_RE.match(cid)), f"{where}: company_id 형식 오류 {cid!r}")
        _require(cid not in out, f"{where}: company_id 중복 {cid!r}")
        _require(isinstance(item["display_name"], str) and item["display_name"].strip(), f"{where}: display_name 필요")
        _require(isinstance(item["aliases"], list) and all(isinstance(a, str) for a in item["aliases"]), f"{where}: aliases 는 문자열 배열")
        _require(item["type"] in COMPANY_TYPES, f"{where}: type {item['type']!r} 는 {sorted(COMPANY_TYPES)} 중 하나")
        _require(isinstance(item["listed"], bool), f"{where}: listed 는 bool")
        _require(item["ticker"] is None or isinstance(item["ticker"], str), f"{where}: ticker 는 문자열 또는 null")
        _require(item["share_basis"] in SHARE_BASIS_VALUES, f"{where}: share_basis 오류")
        _require(item["adr_ratio"] is None or _is_number(item["adr_ratio"]), f"{where}: adr_ratio 숫자 또는 null")
        _require(isinstance(item["reporting_currency"], str), f"{where}: reporting_currency 필요")
        _require(isinstance(item.get("reference", False), bool), f"{where}: reference 는 bool")
        _validate_company_collect_keys(item, where)
        out[cid] = item
    return out


def _validate_company_collect_keys(item: dict[str, Any], where: str) -> None:
    """수집기 전용 선택 키. `cik` 는 양의 정수 또는 null, `news_queries` 는 비어 있지 않은 문자열 배열."""
    if "cik" in item:
        cik = item["cik"]
        _require(cik is None or (isinstance(cik, int) and not isinstance(cik, bool) and cik > 0),
                 f"{where}: cik 는 양의 정수 또는 null ({cik!r})")
    if "news_queries" in item:
        queries = item["news_queries"]
        _require(isinstance(queries, list) and queries and all(isinstance(q, str) and q.strip() for q in queries),
                 f"{where}: news_queries 는 비어 있지 않은 문자열 배열 ({queries!r})")


def resolve_company_id(name: str, companies: dict[str, dict[str, Any]]) -> str | None:
    key = re.sub(r"\s+", " ", name).strip()
    for cid, company in companies.items():
        if key == company["display_name"] or key in company["aliases"]:
            return cid
    lowered = key.lower()
    for cid, company in companies.items():
        if lowered == company["display_name"].lower() or lowered in {a.lower() for a in company["aliases"]}:
            return cid
    return None


# ------------------------------------------------------------------ rules

def validate_rules(payload: Any) -> dict[str, Any]:
    _expect_keys(
        payload,
        ["schema", "rule_version", "status", "source", "scoring", "factors", "policies", "checklist", "decisions"],
        "rules.json",
        optional=["note", "sources", "open_tensions", "source_text_corrections"],
    )
    _require(payload["schema"] == "scorecard.rules/1", "rules.json: schema 불일치")
    _require(payload["status"] in {"active", "draft", "retired"}, "rules.json: status 오류")
    factors = payload["factors"]
    _require(set(factors.keys()) == set(FACTOR_IDS), f"rules.json: factors 키는 {FACTOR_IDS} 여야 함")
    for fid, spec in factors.items():
        _require(isinstance(spec, dict) and "range" in spec and "mode" in spec and "label" in spec, f"rules.json.factors.{fid}: label/range/mode 필요")
        lo, hi = spec["range"]
        _require(_is_number(lo) and _is_number(hi) and lo <= hi, f"rules.json.factors.{fid}: range 오류")
        # 2026-09-15 FIX-52: 매트릭스가 만드는 점수도 range 안이어야 한다. v1.7 함정 재배분에서 F7 range 가
        # [-2,0] 으로 줄었는데 `large|yes` 가 -3 에 남아 범위 밖 점수가 조용히 나갔다(리뷰 C codex 발견).
        for key, value in (spec.get("matrix") or {}).items():
            _require(_is_number(value) and lo <= value <= hi,
                     f"rules.json.factors.{fid}.matrix[{key}]: {value} 가 range [{lo}, {hi}] 밖")
    _validate_f6_policy(payload["policies"]["f6"], factors["F6"], f9=payload["policies"].get("f9"))
    _validate_f9_policy(payload["policies"]["f9"], factors["F9"])
    if "missing_types" in payload["policies"]:
        _validate_missing_types_policy(payload["policies"]["missing_types"])
    for item in payload["checklist"]:
        _expect_keys(item, ["id", "focus"], "rules.checklist", optional=["case"])
    ids = [d["id"] for d in payload["decisions"]]
    _require(len(ids) == len(set(ids)), "rules.json: decisions id 중복")
    for d in payload["decisions"]:
        # implementation_status: 결정은 미결이어도 **권고안이 이미 코드에 서 있는지**는 따로 기록한다.
        # 미결 목록만 보고 "아직 아무것도 안 됐다" 고 읽는 것을 막는다(F9-PEND-40).
        _expect_keys(d, ["id", "status", "summary"], f"rules.decisions[{d.get('id')}]",
                     optional=["recommendation", "affects", "choices", "blocking",
                               "implementation_status",
                               # 확정된 결정이 **무엇을 왜 골랐고 무엇을 밀어냈는지**를 같이 든다.
                               # 고른 것만 남기면 다음 사람이 밀린 안을 다시 들고 온다(C03-IMPL-43).
                               "chosen", "decided_at", "decided_by", "superseded_choice",
                               "confirmed_model", "why_the_source_wins_over_handover",
                               "generation_gap_constraints", "scope", "pending_recheck",
                               # 결정에 딸린 범위 변경. 무엇에서 무엇으로 왜 바꿨는지(IMPL-46).
                               "range_change",
                               # 이 결정이 잣대를 바꿔 승계 예외 요건을 못 채우게 된 자리(FIX-59). 점수는 그대로 두고 기록으로 메운다.
                               "succession_exception_gap",
                               # 결정을 닫으면서 **남는 물음**. 닫혔다고 다 풀린 것처럼 읽히지 않게 따로 적는다(FIX-61).
                               "remaining_question"])
        # 고른 것을 적었으면 **선택지 목록 안에 있어야** 한다. 밀린 안을 지우고 고른 것만 남기면
        # 다음 사람이 그 안을 다시 들고 온다 — 그래서 choices 에 둘 다 남긴다(C03-IMPL-43).
        if d.get("chosen"):
            _require(d["chosen"] in (d.get("choices") or []),
                     f"rules.decisions[{d.get('id')}]: chosen {d.get('chosen')!r} 이 choices 에 없음")
            _require(d["status"] == "resolved",
                     f"rules.decisions[{d.get('id')}]: chosen 이 있으면 status 는 resolved 여야 함")
        _require(d["status"] in {"documented", "pending", "resolved"}, f"rules.decisions[{d['id']}]: status 오류")
    if "sources" in payload:
        _validate_source_policy(payload["sources"])
    if "open_tensions" in payload:
        _validate_open_tensions(payload["open_tensions"], {d["id"] for d in payload["decisions"]})
    if "source_text_corrections" in payload:
        _validate_source_text_corrections(payload["source_text_corrections"])
    return payload


def _validate_source_text_corrections(items: Any) -> None:
    """불변 원천(v1.5 기준선 트리거 등) 문구에 렌더러가 덧붙이는 정정 목록(FIX-53 3단계 보완).

    원천 파일은 고치지 않는다. `match` 가 들어 있는 줄 끝에 `correction` 을 붙이고, 이미 `marker` 가 있는 줄은 건너뛴다.
    """
    _require(isinstance(items, list), "rules.source_text_corrections: 배열이어야 함")
    seen: set[str] = set()
    for idx, c in enumerate(items):
        where = f"rules.source_text_corrections[{idx}]"
        _expect_keys(c, ["id", "match", "correction", "marker", "applies_to", "why", "decided_at"], where, optional=["note"])
        _require(c["id"] not in seen, f"{where}.id: 중복 {c['id']}")
        seen.add(c["id"])
        for key in ("match", "correction", "marker", "why"):
            _require(isinstance(c[key], str) and c[key].strip(), f"{where}.{key}: 비워 둘 수 없음")
        _require(c["marker"] in c["correction"], f"{where}: correction 안에 marker 가 있어야 재적용을 막는다")
        _require(isinstance(c["applies_to"], list) and set(c["applies_to"]) <= {"triggers"} and c["applies_to"],
                 f"{where}.applies_to: 지금 소비자는 트리거 렌더러 하나다 — triggers 만 받는다")
        _expect_date(c["decided_at"], f"{where}.decided_at")


TENSION_ID_RE = re.compile(r"^TEN-[A-Z0-9-]+$")
# 제3자(비 Claude) 재검토의 갈래. committed 는 약속, partial 은 일부 판단만, recommended 는 권장일 뿐이다.
THIRD_PARTY_RECHECK = {"committed", "partial", "recommended"}
# 선택 파라미터를 못 만든 사유 중 factor 를 pending 으로 세우지 않는 것(FIX-61). calc_f6_params.OPTIONAL_CAUSES 와 같다.
OPTIONAL_CAUSES = {"missing_input", "requires_positive"}
RECHECK_RE = re.compile(r"^\d{4}-\d{2}$")


def _validate_open_tensions(items: Any, decision_ids: set[str]) -> None:
    """긴장 목록 — AGENTS.md 리뷰 범위의 승계 판단 예외가 기대는 장부다(FIX-53).

    예외는 **재검토 시점과 함께 등록된** 긴장에만 걸리므로 시점·관련 판단·리뷰 발견·방향이 비어 있으면 거부한다.
    리뷰 파일은 여기 id(TEN-…)를 근거 칸에 적는다.
    """
    _require(isinstance(items, list), "rules.open_tensions: 배열이어야 함")
    seen: set[str] = set()
    for idx, t in enumerate(items):
        where = f"rules.open_tensions[{idx}]"
        _expect_keys(t, ["id", "status", "recheck_at", "review_finding", "judgment_ids", "subject", "tension", "direction"],
                     where, optional=["decision_id", "rechecker", "why_carried_exception", "score_impact_now", "source_lines", "note",
                                      # 긴장에 기대는 회사별 모호함(FIX-53 2단계 A+2 재판정에서 드러난 것)
                                      "affected",
                                      # 같은 잣대 계열의 다른 긴장 — 재검토 때 함께 본다(FIX-54 1단계 S6, RC3-03·04)
                                      "related_tensions",
                                      # 재검토를 **무엇이 오면** 시작하는지. 시점(recheck_at)만으로는 조건이 남지 않는다(FIX-55 2단계).
                                      "trigger",
                                      # 제3자(비 Claude) 재검토가 **약속인지 권장인지**. 문장을 훑어 세면 둘이 한 덩어리가 된다(FIX-56 2단계).
                                      "third_party_recheck", "third_party_scope",
                                      # 해소된 긴장의 결론·시점·남는 질문(FIX-62 — TEN-RA5-02 가 첫 사례다).
                                      "resolution", "resolved_at", "what_remains",
                                      # 같은 충돌이 다른 조건(상장·비상장)에도 걸릴 때 그 범위(FIX-63 S2).
                                      "also_covers_listed"])
        for aidx, a in enumerate(t.get("affected") or []):
            _expect_keys(a, ["company_id", "why"], f"{where}.affected[{aidx}]", optional=["source_lines", "judgment_id"])
            _require(str(a["why"]).strip(), f"{where}.affected[{aidx}].why: 비워 둘 수 없음")
        _require(isinstance(t["id"], str) and TENSION_ID_RE.match(t["id"]), f"{where}.id: TEN- 로 시작해야 함 — {t['id']!r}")
        _require(t["id"] not in seen, f"{where}.id: 중복 {t['id']}")
        seen.add(t["id"])
        _require(t["status"] in {"open", "resolved"}, f"{where}.status: open/resolved")
        # 2026-09-17 FIX-62: `resolved` 로 바꾸면서 결론을 적지 않으면 긴장이 조용히 사라진다.
        # 무엇으로 닫혔는지와 언제 닫혔는지를 같이 요구한다.
        if t["status"] == "resolved":
            _require(isinstance(t.get("resolution"), str) and t["resolution"].strip(),
                     f"{where}.resolution: 해소된 긴장은 결론을 적어야 함")
            _require(isinstance(t.get("resolved_at"), str) and DATE_RE.match(t.get("resolved_at") or ""),
                     f"{where}.resolved_at: 해소 시점(YYYY-MM-DD)이 필요함 — {t.get('resolved_at')!r}")
        else:
            _require("resolution" not in t and "resolved_at" not in t,
                     f"{where}: 열린 긴장에는 결론·해소 시점을 적지 않는다")
        _require(isinstance(t["recheck_at"], str) and RECHECK_RE.match(t["recheck_at"]),
                 f"{where}.recheck_at: YYYY-MM 재검토 시점이 필요함 — {t['recheck_at']!r}")
        _require(isinstance(t["judgment_ids"], list) and t["judgment_ids"] and all(isinstance(j, str) and j for j in t["judgment_ids"]),
                 f"{where}.judgment_ids: 관련 판단 id 가 하나 이상 필요함")
        # 2026-09-16 FIX-56 2단계(5차 리뷰 D low): `rechecker` 문장에 `비 Claude` 가 있으면 산출물이 그것을 세는데,
        # **약속(committed)·부분(partial)·권장(recommended)** 이 한 문장으로 합쳐져 8건이 모두 약속처럼 보였다.
        # 문장을 훑지 말고 갈래를 선언하게 한다 — 선언이 없으면 거부한다.
        tp = t.get("third_party_recheck")
        mentions_third_party = "비 Claude" in (t.get("rechecker") or "")
        if mentions_third_party or tp is not None:
            _require(tp in THIRD_PARTY_RECHECK,
                     f"{where}.third_party_recheck: rechecker 가 비 Claude 세션을 말하면 {sorted(THIRD_PARTY_RECHECK)} 중 하나를 선언해야 함 ({tp!r})")
            scope = t.get("third_party_scope")
            if tp == "partial":
                _require(isinstance(scope, list) and scope and set(scope) < set(t["judgment_ids"]),
                         f"{where}.third_party_scope: partial 이면 judgment_ids 의 **진부분집합**이어야 함 — 전부면 committed 다")
            else:
                _require(scope is None, f"{where}.third_party_scope: {tp!r} 에는 범위를 적지 않는다 — 전체가 대상이다")
        for key in ("review_finding", "subject", "tension", "direction"):
            _require(isinstance(t[key], str) and t[key].strip(), f"{where}.{key}: 비워 둘 수 없음")
        if "decision_id" in t:
            _require(t["decision_id"] in decision_ids, f"{where}.decision_id: 규칙에 없는 결정 {t['decision_id']!r}")
    all_ids = {t["id"] for t in items}
    for idx, t in enumerate(items):
        for rid in t.get("related_tensions") or []:
            _require(rid in all_ids and rid != t["id"], f"rules.open_tensions[{idx}].related_tensions: 없는 긴장이거나 자기 자신 {rid!r}")


# 산출물 사용 범위. 원천 약관의 '개인 사용 허용' 조항이 우리에게 적용되는지를 가르는 값이라
# 자유 문자열로 두지 않는다. 2026-09-11 에 단일값에서 **허용 범위(집합)** 로 바뀌었다 — 개인 사용과
# 법인 내부 사용이 둘 다 실제 사용이기 때문이다(SRC-POLICY-32).
USAGE_SCOPES = frozenset({"personal_internal_only", "corporate_internal_only", "external_distribution"})


def normalize_usage_scopes(scope: dict[str, Any]) -> set[str]:
    """`scopes`(신규 배열)와 `scope`(과거 단일값)를 모두 받아 집합으로 정규화한다.

    과거 규칙 파일(v1.6·v1.7 초판)이 단일 문자열이므로 한쪽을 지우지 않는다. v1.5 는 sources
    블록 자체가 없어 이 경로를 타지 않는다.

    **집합은 합집합이다.** 어떤 원천이 적격이려면 라이선스가 원소를 **전부** 허용해야 하고
    하나라도 금지하면 부적격이다. 범위를 넓히는 것은 제약을 푸는 것이 아니라 조이는 것이다.
    """
    if "scopes" in scope:
        values = scope["scopes"]
        _require(isinstance(values, list) and values,
                 "rules.sources.usage_scope.scopes: 비어 있지 않은 배열이어야 함")
        _require(len(set(values)) == len(values),
                 "rules.sources.usage_scope.scopes: 중복은 허용하지 않음")
    else:
        _require("scope" in scope, "rules.sources.usage_scope: scopes 또는 scope 중 하나가 필요함")
        values = [scope["scope"]]
    unknown = [v for v in values if v not in USAGE_SCOPES]
    _require(not unknown,
             f"rules.sources.usage_scope: 알 수 없는 값 {unknown!r} — {sorted(USAGE_SCOPES)} 중에서 쓴다")
    return set(values)


def _validate_source_policy(policy: Any) -> None:
    """자료 원천 allowlist. 같은 host 가 allowed 와 denied 에 동시에 있으면 판정이 갈린다."""
    _require(isinstance(policy, dict), "rules.sources: object 여야 함")
    _expect_keys(policy, ["policy_note", "enforcement", "allowed", "denied"], "rules.sources",
                 optional=["conditional_candidates", "not_adopted", "usage_scope", "unlisted", "note"])
    hosts: dict[str, str] = {}
    for group, required in (("allowed", ["host", "note"]), ("denied", ["host", "reason"])):
        entries = policy[group]
        _require(isinstance(entries, list), f"rules.sources.{group}: 배열이어야 함")
        for idx, entry in enumerate(entries):
            where = f"rules.sources.{group}[{idx}]"
            _require(isinstance(entry, dict), f"{where}: object 여야 함")
            for key in required:
                _require(str(entry.get(key) or "").strip(), f"{where}: {key} 필요")
            host = entry["host"]
            _require(host not in hosts, f"{where}: host {host!r} 가 {hosts.get(host)} 에도 있음 — 한쪽에만 둔다")
            hosts[host] = group
    for idx, entry in enumerate(policy.get("conditional_candidates") or []):
        where = f"rules.sources.conditional_candidates[{idx}]"
        _expect_keys(entry, ["name", "host", "status", "required_written_conditions"], where, optional=["note"])
        # 승인 전 후보를 승인된 상태로 표기할 수 없다.
        _require(entry["status"] == "candidate_not_approved", f"{where}: 미승인 후보는 status 가 candidate_not_approved 여야 함")
        _require(isinstance(entry["required_written_conditions"], list) and entry["required_written_conditions"],
                 f"{where}: 서면 확정이 필요한 조건을 비워 둘 수 없음")
        _require(entry["host"] not in hosts, f"{where}: host {entry['host']!r} 는 allowed/denied 와 겹칠 수 없음")
    if "usage_scope" in policy:
        scope = policy["usage_scope"]
        # scope(과거)와 scopes(신규) 중 **정확히 하나**만 둔다. 둘 다 두면 어느 쪽이 정본인지 모르게 되고,
        # 그것이 '값을 좁혔는데 좁혔다는 사실이 안 남는' 이 프로젝트의 반복 실패 형태다.
        _require(("scope" in scope) != ("scopes" in scope),
                 "rules.sources.usage_scope: scope 와 scopes 중 정확히 하나만 둔다")
        _expect_keys(scope, ["decided_at", "statement", "condition"], "rules.sources.usage_scope",
                     optional=["scope", "scopes", "note", "evaluation_rule", "supersedes"])
        # 범위 선언은 조건과 짝이어야 한다. 조건 없는 선언은 범위가 바뀔 때 무엇을 다시 봐야 하는지를 남기지 않는다.
        for key in ("decided_at", "statement", "condition"):
            _require(str(scope.get(key) or "").strip(), f"rules.sources.usage_scope: {key} 를 비워 둘 수 없음")
        # 이 값은 판정을 가르는 스위치다(법인 사용이면 '개인 사용 허용' 조항이 우리에게 적용되지 않는다).
        # 자유 문자열로 두면 표기가 흔들리고 == 비교가 조용히 빗나간다.
        normalize_usage_scopes(scope)
    # 채택 안 함. denied 와 가르는 이유는 사유의 종류가 다르기 때문이다 —
    # denied 는 **쓸 자격이 없는** 것이고 not_adopted 는 **자격은 있으나 안 쓰기로 한** 것이다.
    for idx, entry in enumerate(policy.get("not_adopted") or []):
        where = f"rules.sources.not_adopted[{idx}]"
        _expect_keys(entry, ["host", "status", "reason_type", "reason", "decided_at",
                             "decided_by", "reopen_condition"], where,
                     optional=["name", "note", "prior_investigation"])
        for key in ("host", "reason", "decided_at", "decided_by", "reopen_condition"):
            _require(str(entry.get(key) or "").strip(), f"{where}: {key} 필요")
        _require(entry["status"] == "not_adopted", f"{where}: status 는 not_adopted 여야 함")
        # 사유를 뭉뚱그리지 않는다. 비용 판단과 약관 배제는 다른 결정이다.
        # legacy_upstream(2026-09-14 SRC-FLAG-49): 채택 검토를 한 적 없이 **legacy 관측의 상류라서 장부에만 올린** 원천.
        # 약관을 보고 안 쓰기로 한 것(terms)과 같은 칸에 두면 검토를 마친 것처럼 읽힌다.
        _require(entry["reason_type"] in ("cost", "technical", "terms", "redundant", "legacy_upstream"),
                 f"{where}: reason_type 은 cost/technical/terms/redundant/legacy_upstream 중 하나여야 함")
        _require(entry["host"] not in hosts, f"{where}: host {entry['host']!r} 는 allowed/denied 와 겹칠 수 없음")
        hosts[entry["host"]] = "not_adopted"

    for idx, entry in enumerate(policy.get("unlisted") or []):
        where = f"rules.sources.unlisted[{idx}]"
        _expect_keys(entry, ["host", "reason_type", "reason", "decided_at"], where, optional=["note", "evidence"])
        for key in ("host", "reason", "decided_at"):
            _require(str(entry.get(key) or "").strip(), f"{where}: {key} 필요")
        # 미등재 사유를 뭉뚱그리지 않는다. 기술적 부적격과 약관 미확인은 다른 판단이다.
        _require(entry["reason_type"] in ("technical", "terms", "both"),
                 f"{where}: reason_type 은 technical/terms/both 중 하나여야 함")
        _require(entry["host"] not in hosts, f"{where}: host {entry['host']!r} 는 allowed/denied 와 겹칠 수 없음")


# 순이익의 소유 범위. P1 분자는 시총·EPS 와 같은 모회사 보통주 범위여야 한다(FIX-54 1단계 FC-04).
OWNERSHIP_SCOPES = frozenset({"parent_attributable", "consolidated_incl_nci"})

# F6 는 두 모드가 공존한다. v1.5·v1.6 은 NTM PER 단일 구간표(bands), v1.7 은 네 파라미터(parameters)다.
# **정본은 parameters 다(사용자 확정 2026-09-14, IMPL-46).** bands 는 구버전이고 run.json.rule_version 으로
# v1.5·v1.6 을 고른 실행에서만 선택된다. 승인된 v1.5 실행이 bands 로 계산됐고 해시가 그 결과에 묶여
# 있으므로 한쪽을 지우지 않고 둘 다 검증한다.
P4_CONDITION_IDS = {"nonop_share", "period_basis_not_ttm", "short_history", "stale_asof"}
F6_COMPARISONS = {"upper_exclusive", "lower_inclusive"}


def _validate_f6_bands(bands: Any, where: str, comparison: str) -> None:
    """반개방 구간표. upper 는 오름차순·마지막 null, lower 는 내림차순·마지막 null 이다."""
    _require(isinstance(bands, list) and bands, f"{where}: bands 배열 필요")
    key = "upper" if comparison == "upper_exclusive" else "lower"
    for idx, b in enumerate(bands):
        _expect_keys(b, [key, "score"], f"{where}[{idx}]")
        _require(_is_number(b["score"]), f"{where}[{idx}]: score 는 숫자")
    _require(bands[-1][key] is None, f"{where}: 마지막 구간의 {key} 는 null (열린 끝)")
    edges = [b[key] for b in bands[:-1]]
    _require(all(_is_number(e) for e in edges), f"{where}: 경계는 숫자")
    ordered = sorted(edges) if key == "upper" else sorted(edges, reverse=True)
    _require(edges == ordered, f"{where}: {key} 경계 정렬 오류 — {'오름차순' if key == 'upper' else '내림차순'} 이어야 함")


def _validate_missing_types_policy(spec: Any) -> None:
    """`not_disclosed_confirmed` 가 성립하는 경로를 규칙이 선언한다(FIX-57 2단계, 6차 리뷰 A 분담).

    전에는 이 요건이 `validation/miss-label-23/reclassify.py` 안에만 있었다. 그 라벨은 C-16 으로 **한 칸 강등**을
    만드는데 근거가 규칙 밖에 있어 리뷰가 같은 질문을 되풀이했다. 여기 선언하고 `validate_observations` 가 읽는다 —
    선언만 두고 읽는 코드를 두지 않으면 C-11 과 같은 형태가 된다.
    """
    where = "rules.policies.missing_types"
    _expect_keys(spec, ["not_disclosed_confirmed"], where, optional=["note"])
    ndc = spec["not_disclosed_confirmed"]
    _expect_keys(ndc, ["routes", "otherwise"], f"{where}.not_disclosed_confirmed", optional=["why", "source", "consumers"])
    routes = ndc["routes"]
    _require(isinstance(routes, dict) and set(routes) == {"structural", "issuer_declared"},
             f"{where}.not_disclosed_confirmed.routes: structural·issuer_declared 둘을 선언해야 함")
    st = routes["structural"]
    _expect_keys(st, ["applies_to", "metrics", "why"], f"{where}...structural")
    _require(st["applies_to"] == "unlisted", f"{where}...structural.applies_to: 지금 성립하는 것은 비상장뿐이다")
    _require(isinstance(st["metrics"], list) and st["metrics"], f"{where}...structural.metrics: 비어 있을 수 없음")
    for m in st["metrics"]:
        _require(m in METRICS, f"{where}...structural.metrics: 알 수 없는 지표 {m!r}")
    isd = routes["issuer_declared"]
    _expect_keys(isd, ["applies_to", "required_basis_keys", "why"], f"{where}...issuer_declared", optional=["example"])
    _require(isinstance(isd["required_basis_keys"], list) and isd["required_basis_keys"],
             f"{where}...issuer_declared.required_basis_keys: 비어 있을 수 없음")


def _validate_f6_policy(f6: Any, factor: dict[str, Any], f9: Any = None) -> None:
    _require(isinstance(f6, dict), "rules.policies.f6: object 여야 함")
    mode = f6.get("mode", "per_band")
    if mode != "parameters":
        # v1.5·v1.6 경로. 기존 검증을 그대로 유지한다.
        bands = f6["bands"]
        _require(isinstance(bands, list) and bands[-1]["upper"] is None, "rules.json: f6 bands 마지막은 upper null")
        uppers = [b["upper"] for b in bands[:-1]]
        _require(uppers == sorted(uppers), "rules.json: f6 bands upper 는 오름차순")
        return

    params = f6.get("parameters")
    _require(isinstance(params, dict) and params, "rules.policies.f6.parameters: 비어 있을 수 없음")
    total_min = 0
    for pid, spec in params.items():
        where = f"rules.policies.f6.parameters.{pid}"
        _expect_keys(spec, ["label", "question", "score_range", "comparison", "unit", "formula", "inputs", "bands"],
                     where, optional=["requires_positive", "currency_note",
                                      # 입력 관측이 가져야 할 소유 범위(FIX-54 1단계 FC-04). calc_f6_params._parameter_value 가 읽는다.
                                      "input_scope", "input_scope_note",
                                      # 같은 뜻의 다른 지표로 대체해 읽는다(FIX-56 1단계). 신규 상장사의 revenue_ttm 이 분기값일 때 P2 가 12개월 매출을 찾는 길.
                                      "input_alternatives", "input_alternatives_note"])
        _require(spec["comparison"] in F6_COMPARISONS, f"{where}: comparison 은 {sorted(F6_COMPARISONS)} 중 하나")
        lo, hi = spec["score_range"]
        _require(_is_number(lo) and _is_number(hi) and lo <= hi <= 0, f"{where}: score_range 는 음수 구간이어야 함")
        _validate_f6_bands(spec["bands"], f"{where}.bands", spec["comparison"])
        scores = [b["score"] for b in spec["bands"]]
        _require(min(scores) == lo and max(scores) == hi, f"{where}: bands 점수가 score_range {spec['score_range']} 를 덮지 않음")
        # 입력 지표가 카탈로그에 있어야 한다. 없는 metric 을 산식에 적어 두면 영원히 pending 이 된다.
        for m in spec["inputs"]:
            _require(m in METRICS, f"{where}.inputs: 알 수 없는 metric {m!r}")
        for m in spec.get("requires_positive", []):
            _require(m in spec["inputs"], f"{where}.requires_positive: inputs 에 없는 {m!r}")
        for m, alts in (spec.get("input_alternatives") or {}).items():
            _require(m in spec["inputs"], f"{where}.input_alternatives: inputs 에 없는 {m!r}")
            _require(isinstance(alts, list) and alts, f"{where}.input_alternatives.{m}: 비어 있지 않은 배열이어야 함")
            for alt in alts:
                _require(alt in METRICS, f"{where}.input_alternatives.{m}: 알 수 없는 metric {alt!r}")
                _require(METRICS[alt]["unit"] == METRICS[m]["unit"],
                         f"{where}.input_alternatives.{m}: {alt!r} 의 단위가 {m!r} 과 다름 — 대체할 수 없다")
        for m, scope in (spec.get("input_scope") or {}).items():
            _require(m in spec["inputs"], f"{where}.input_scope: inputs 에 없는 {m!r}")
            _require(scope in OWNERSHIP_SCOPES, f"{where}.input_scope.{m}: {sorted(OWNERSHIP_SCOPES)} 중 하나")
        total_min += lo

    p4 = f6.get("p4")
    _expect_keys(p4, ["label", "question", "mode", "cap_steps", "note", "conditions"], "rules.policies.f6.p4")
    _require(p4["mode"] == "subtotal_demotion", "rules.policies.f6.p4: mode 는 subtotal_demotion")
    _require(isinstance(p4["cap_steps"], int) and p4["cap_steps"] >= 1, "rules.policies.f6.p4: cap_steps 는 1 이상 정수")
    seen: set[str] = set()
    for idx, cond in enumerate(p4["conditions"]):
        where = f"rules.policies.f6.p4.conditions[{idx}]"
        _expect_keys(cond, ["id", "note"], where,
                     optional=["threshold", "thresholds_months", "basis_map", "measured_from",
                               "why_not_single_threshold", "why_16", "why_6", "why_it_exists",
                               "decided_at", "decided_by",
                               # 임계 경계 표시와, 입력 정의가 갈렸다는 기록(NETCASH-37 재고 검산).
                               "boundary_display", "stored_vs_recomputed",
                               # 조건이 읽는 산식과 입력. 선언한 입력은 METRICS 에 있어야 한다(NONOP-44).
                               "formula", "inputs",
                               # 이 조건의 값이 어느 factor 에 속하는지. 다른 factor 로 이월하지 않는다는 선언(IMPL-50 C-11).
                               "scope", "scope_why",
                               # 조건을 무엇에서 판정하는지. 관측에서 판정하는 조건은 트랙 자동 목록에 두지 않는다(FIX-55 1단계).
                               "judged_from"])
        for metric in cond.get("inputs", []):
            _require(metric in METRICS, f"{where}.inputs: 알 수 없는 지표 {metric!r}")
        # 코드가 구현하지 않은 조건 id 를 규칙에 적어 두면 선언만 있고 걸리지 않는 조건이 생긴다.
        _require(cond["id"] in P4_CONDITION_IDS, f"{where}: 구현되지 않은 조건 id {cond['id']!r}")
        _require(cond["id"] not in seen, f"{where}: 조건 id 중복 {cond['id']!r}")
        seen.add(cond["id"])
        # 임계가 선언되면 읽을 수 있는 형태여야 한다. stale_asof 는 보고 주기마다 임계가 다르다.
        if "thresholds_months" in cond:
            tm = cond["thresholds_months"]
            _require(isinstance(tm, dict) and tm, f"{where}.thresholds_months: 비어 있을 수 없음")
            for key, months in tm.items():
                _require(isinstance(months, int) and months > 0,
                         f"{where}.thresholds_months.{key}: 양의 정수 필요 ({months!r})")
            for src, dst in (cond.get("basis_map") or {}).items():
                _require(dst in tm, f"{where}.basis_map.{src}: thresholds_months 에 없는 기준 {dst!r}")

    judged_from_observation = {c["id"] for c in p4["conditions"] if c.get("judged_from")}
    tracks = f6.get("tracks")
    _require(isinstance(tracks, dict) and tracks, "rules.policies.f6.tracks: 비어 있을 수 없음")
    factor_min = factor["range"][0]
    for tid, spec in tracks.items():
        where = f"rules.policies.f6.tracks.{tid}"
        _expect_keys(spec, ["label", "parameters", "floor", "select"], where,
                     optional=["auto_p4_conditions", "note", "ceiling", "p4_note",
                               # 트랙이 쓰지 않는 파라미터와 그 사유(FIX-56 1단계). 빠진 이유를 결과가 말하게 한다.
                               "parameters_excluded_note",
                               # 입력이 있을 때만 만드는 파라미터(FIX-56 1단계). 없으면 pending 이 아니라 미산출로 적는다.
                               "optional_parameters", "optional_parameters_note",
                               # 그 파라미터를 **어느 사유일 때** 넘길지(FIX-61). 선언이 없으면 scope_mismatch 만 뺀다.
                               "optional_parameters_causes"])
        # 2026-09-16 FIX-55 1단계: 관측에서 판정한다고 선언한 조건을 트랙 자동 목록에도 두면 두 경로가 갈린다.
        for auto in spec.get("auto_p4_conditions", []):
            _require(auto not in judged_from_observation,
                     f"{where}.auto_p4_conditions: {auto!r} 는 관측에서 판정한다고 선언된 조건이라 트랙 자동 목록에 둘 수 없음")
        _require(_is_number(spec["floor"]) and factor_min <= spec["floor"] <= 0,
                 f"{where}: floor 가 factor range {factor['range']} 밖")
        # 비상장은 0·-1 칸이 없다(v1.5 구간표). 천장을 선언하면 floor 와 factor range 안이어야 한다.
        if "ceiling" in spec:
            _require(_is_number(spec["ceiling"]) and spec["floor"] <= spec["ceiling"] <= 0,
                     f"{where}: ceiling {spec['ceiling']!r} 이 floor {spec['floor']} 와 0 사이가 아님")
        for pid in spec["parameters"]:
            _require(pid in params or pid == "P4", f"{where}.parameters: 알 수 없는 파라미터 {pid!r}")
        for pid in spec.get("optional_parameters", []):
            _require(pid in spec["parameters"],
                     f"{where}.optional_parameters: parameters 에 없는 {pid!r} — 선택 여부는 쓰는 파라미터에만 붙는다")
        for pid, causes in (spec.get("optional_parameters_causes") or {}).items():
            _require(pid in spec.get("optional_parameters", []),
                     f"{where}.optional_parameters_causes: optional_parameters 에 없는 {pid!r}")
            _require(isinstance(causes, list) and causes and set(causes) <= OPTIONAL_CAUSES,
                     f"{where}.optional_parameters_causes.{pid}: {sorted(OPTIONAL_CAUSES)} 의 비어 있지 않은 부분집합이어야 함 "
                     f"— `scope_mismatch` 는 자료 결함이라 넘길 수 없다 ({causes!r})")
        for cid in spec.get("auto_p4_conditions", []):
            _require(cid in seen, f"{where}.auto_p4_conditions: p4 에 없는 조건 {cid!r}")
    private_bands = f6.get("private_bands")
    if private_bands:
        where = "rules.policies.f6.private_bands"
        _require(isinstance(private_bands.get("bands"), list) and private_bands["bands"],
                 f"{where}.bands: 비어 있을 수 없음")
        scores = [b.get("score") for b in private_bands["bands"]]
        for sc in scores:
            _require(_is_number(sc) and factor_min <= sc <= 0, f"{where}: 점수 {sc!r} 가 factor range 밖")
        lowers = [b.get("lower") for b in private_bands["bands"]]
        _require(lowers[-1] is None, f"{where}: 마지막 밴드의 lower 는 null(전 구간 덮기)이어야 함")
        prev = None
        for low in lowers[:-1]:
            _require(_is_number(low) and (prev is None or low < prev),
                     f"{where}: lower 가 내림차순이어야 함 — {lowers}")
            prev = low
        _require(private_bands.get("input") in METRICS,
                 f"{where}.input: 알 수 없는 지표 {private_bands.get('input')!r}")
    correction = f6.get("private_correction")
    if correction:
        where = "rules.policies.f6.private_correction"
        _require(isinstance(correction.get("cap_steps"), int) and correction["cap_steps"] >= 1,
                 f"{where}.cap_steps: 1 이상 정수")
        conds = correction.get("conditions")
        _require(isinstance(conds, list) and conds, f"{where}.conditions: 비어 있을 수 없음")
        for idx, cond in enumerate(conds):
            cw = f"{where}.conditions[{idx}]"
            _require(str(cond.get("id") or "").strip(), f"{cw}: id 필요")
            _require(_is_number(cond.get("threshold")), f"{cw}: threshold 는 숫자")
            _require(isinstance(cond.get("inputs"), list) and len(cond["inputs"]) == 2,
                     f"{cw}.inputs: 지표 둘이 필요")
            for metric in cond["inputs"]:
                _require(metric in METRICS, f"{cw}.inputs: 알 수 없는 지표 {metric!r}")
            # 2026-09-15 FIX-52: 입력 관측의 kind 를 제한한다. 엔진이 읽으므로 관측이 실제로 가질 수 있는 값만 받는다.
            if "accepted_kinds" in cond:
                kinds = cond["accepted_kinds"]
                _require(isinstance(kinds, list) and kinds and all(k in OBSERVATION_KINDS for k in kinds),
                         f"{cw}.accepted_kinds: {sorted(OBSERVATION_KINDS)} 중에서 하나 이상 — {kinds!r}")
            # 답을 먼저 알고 정한 보정이라는 사실이 규칙 파일에 남아 있어야 한다(C-12).
            _require(str(cond.get("threshold_source") or "").strip(),
                     f"{cw}: threshold_source 를 비워 둘 수 없음 — 임계를 어디서 가져왔는지 적는다")
        _require(str(correction.get("weakness") or "").strip(),
                 f"{where}: weakness 를 비워 둘 수 없음 — 이 보정이 답을 먼저 알고 정해졌다는 사실을 남긴다")

    net_cash = f6.get("net_cash")
    # 2026-09-15 FIX-53 RC-01: `if net_cash:` 아래에서만 검사해서 블록을 통째로 지우면 통과했다(2차 리뷰 C).
    # 파라미터가 net_cash 를 입력으로 쓰는 한 그 정의 블록은 필수다. 소비자가 있는 선언을 지울 수 없게 한다.
    consumers = sorted(pid for pid, spec in (f6.get("parameters") or {}).items() if "net_cash" in (spec.get("inputs") or []))
    if consumers:
        _require(isinstance(net_cash, dict) and net_cash,
                 f"rules.policies.f6.net_cash: {', '.join(consumers)} 가 net_cash 를 입력으로 쓰므로 정의 블록이 반드시 있어야 함")
    if net_cash:
        # 2026-09-16 FIX-55 1단계(4차 리뷰 C low): 전에는 "서로 다른 등록 지표 둘" 만 봐서 cash/net_cash 를 arr/nonop_share 로
        # 바꿔도 통과했다. **선언된 자리의 지표가 실제 소비자가 읽는 지표인지**까지 본다 — 하나는 F9 G3 분자(policies.f9.g3_cash_scope.metric),
        # 하나는 net_cash 를 읽는 F6 파라미터의 입력이어야 한다. 스키마가 볼 수 있는 것은 여기까지다(코드를 직접 읽지는 못한다).
        _validate_net_cash(net_cash, g3_metric=((f9 or {}).get("g3_cash_scope") or {}).get("metric"), parameter_consumers=consumers)

    # 파라미터 합계 하한이 factor range 하한과 맞아야 배점 재배분이 규칙 안에서 검산된다.
    _require(total_min == factor_min,
             f"rules.policies.f6: 파라미터 합계 하한 {total_min} 이 factors.F6.range 하한 {factor_min} 과 다름")


NET_CASH_STATUSES = ("working_definition", "confirmed")
# net_cash 적용 범위를 가르는 두 축. **서로를 함의하지 않는다** — 만기 3년 회사채는 즉시성이
# 없어도 시장성이 있고, 비상장 지분은 만기가 없어도 시장성이 없다.
NET_CASH_AXES = ("immediacy", "marketability")


def _validate_net_cash(spec: Any, *, g3_metric: str | None = None, parameter_consumers: list[str] | None = None) -> None:
    """`policies.f6.net_cash` — 역산으로 세운 정의는 **대체 가능하다고 스스로 말해야** 통과한다.

    이 검사가 지키는 것 셋.

    1. 역산 출처(`legacy_reverse_engineered`)면 `provenance.warning` 과 `supersede` 가 비어 있을 수 없다.
       근거 없는 정의가 확정 정의처럼 굳는 것을 막는다.
    2. `evidence.matched.count` 가 실제 회사 수와 같아야 한다. 일치 개수를 손으로 적고 목록을 나중에
       고치면 숫자만 남아 거짓말이 된다.
    3. `scope_separation.sites` 가 **서로 다른 지표 둘 이상**을 가리켜야 한다. 이 블록의 존재 이유가
       `cash` 와 `net_cash` 를 가르는 것이라 하나로 접히면 의미가 사라진다.
    """
    where = "rules.policies.f6.net_cash"
    _require(spec.get("status") in NET_CASH_STATUSES,
             f"{where}.status: {NET_CASH_STATUSES} 중 하나여야 함 — {spec.get('status')!r}")
    _require(str(spec.get("definition") or "").strip(), f"{where}.definition: 비워 둘 수 없음")

    prov = spec.get("provenance") or {}
    _require(str(prov.get("kind") or "").strip(), f"{where}.provenance.kind: 비워 둘 수 없음")
    if prov.get("kind") == "legacy_reverse_engineered":
        _require(str(prov.get("warning") or "").strip(),
                 f"{where}.provenance.warning: 역산 정의는 원본 사양이 아니라는 경고가 필요함")
        _require(str(spec.get("supersede") or "").strip(),
                 f"{where}.supersede: 역산 정의는 확정 정의가 나오면 대체된다는 것을 적어야 함")

    matched = ((spec.get("evidence") or {}).get("matched")) or {}
    if matched:
        companies = matched.get("companies") or {}
        _require(matched.get("count") == len(companies),
                 f"{where}.evidence.matched: count {matched.get('count')!r} 가 목록 {len(companies)}개와 다름")

    scope = spec.get("securities_scope") or {}
    if scope:
        sw = f"{where}.securities_scope"
        _require(str(scope.get("criterion") or "").strip(), f"{sw}.criterion: 비워 둘 수 없음")
        _require(isinstance(scope.get("include"), list) and scope["include"],
                 f"{sw}.include: 무엇을 넣는지 비어 있을 수 없음")
        excl = scope.get("exclude")
        _require(isinstance(excl, list) and excl, f"{sw}.exclude: 무엇을 빼는지 비어 있을 수 없음")
        for idx, item in enumerate(excl):
            iw = f"{sw}.exclude[{idx}]"
            # **뺀 이유가 없으면 다음 사람이 되돌린다.** 경계는 값이 아니라 논거로 서 있어야 한다.
            for key in ("what", "why"):
                _require(str(item.get(key) or "").strip(), f"{iw}.{key}: 비워 둘 수 없음")

    # 2026-09-15 FIX-52: 아래 검사는 블록이 **있을 때만** 돌아서, 블록을 통째로 지우면 검사도 같이 사라졌다
    # (리뷰 C codex 발견, 설계진행 메모리 변조로 재현). 작업 정의인 동안에는 세 블록이 반드시 있어야 한다.
    if spec.get("status") == "working_definition":
        sep_required = spec.get("scope_separation")
        _require(isinstance(sep_required, dict) and sep_required,
                 f"{where}.scope_separation: 작업 정의(working_definition)는 적용 범위 구분 블록이 반드시 있어야 함")
        axes_required = sep_required.get("two_axes")
        _require(isinstance(axes_required, dict) and axes_required,
                 f"{where}.scope_separation.two_axes: 작업 정의는 두 축(즉시성·시장성) 블록이 반드시 있어야 함")
        _require(isinstance(axes_required.get("banned_word"), dict),
                 f"{where}.scope_separation.two_axes.banned_word: 작업 정의는 금지어 블록이 반드시 있어야 함")
        # 2026-09-15 FIX-54 1단계 S7(3차 리뷰 C RC3-07): 금지어만 남긴 사전도 통과했다. 두 축의 정의 문장 자체를 요구한다.
        for axis in NET_CASH_AXES:
            _require(str(axes_required.get(axis) or "").strip(),
                     f"{where}.scope_separation.two_axes.{axis}: 작업 정의는 이 축의 정의 문장이 반드시 있어야 함")

    sep = spec.get("scope_separation") or {}
    if sep:
        sites = sep.get("sites")
        _require(isinstance(sites, list) and len(sites) >= 2,
                 f"{where}.scope_separation.sites: 자리 둘 이상이 필요함")
        metrics = []
        for idx, site in enumerate(sites):
            sw = f"{where}.scope_separation.sites[{idx}]"
            _require(site.get("metric") in METRICS, f"{sw}.metric: 알 수 없는 지표 {site.get('metric')!r}")
            for key in ("site", "question", "counts", "why"):
                _require(str(site.get(key) or "").strip(), f"{sw}.{key}: 비워 둘 수 없음")
            # **자리마다 두 축을 각각 답해야 한다.** 즉시성과 시장성은 서로를 함의하지 않는데
            # '환금성' 같은 포괄어로 뭉치면 어느 축을 묻는지 흐려지고 문장이 실제 기준과 반대로
            # 읽힌다 — 2026-09-11 에 EV 자리에서 실제로 그랬다(NETCASH-37 3차 검토).
            axes = site.get("axes") or {}
            for axis in NET_CASH_AXES:
                _require(str(axes.get(axis) or "").strip(),
                         f"{sw}.axes.{axis}: 이 자리가 그 축을 묻는지 답해야 함")
            metrics.append(site["metric"])
        # 소비자와 묶는다. 자리 이름만 다르고 지표가 소비 경로와 무관하면 이 블록은 아무것도 지키지 못한다.
        if g3_metric:
            _require(g3_metric in metrics,
                     f"{where}.scope_separation.sites: F9 G3 분자 지표 {g3_metric!r} 를 가리키는 자리가 없음 — policies.f9.g3_cash_scope 와 갈린다")
        if parameter_consumers:
            _require("net_cash" in metrics,
                     f"{where}.scope_separation.sites: {', '.join(parameter_consumers)} 가 읽는 net_cash 를 가리키는 자리가 없음")
        _require(len(set(metrics)) >= 2,
                 f"{where}.scope_separation.sites: 서로 다른 지표 둘 이상을 가리켜야 함 — {metrics}")
        _check_banned_word(sep, where)


def _strings(node: Any, path: str):
    """중첩 구조 안의 모든 문자열을 경로와 함께 내놓는다."""
    if isinstance(node, dict):
        for key, value in node.items():
            yield from _strings(value, f"{path}.{key}")
    elif isinstance(node, list):
        for idx, value in enumerate(node):
            yield from _strings(value, f"{path}[{idx}]")
    elif isinstance(node, str):
        yield path, node


def _check_banned_word(sep: dict[str, Any], where: str) -> None:
    """`two_axes.banned_word` 가 선언한 낱말을 **실제로 막는다.**

    선언만 하면 아무것도 막지 못한다. `전체·모두·전부` 는 테스트가 막는데 `환금성` 만 선언에
    그쳐 다른 자리에 다시 써도 통과했다(설계진행 2026-09-11 지적). 예외 경로는 규칙이 데이터로
    들고 있다 — 6.4 원문을 인용하는 자리와 금지 규정 자신은 그 낱말을 담아야 하기 때문이다.
    """
    spec = (sep.get("two_axes") or {}).get("banned_word")
    if not isinstance(spec, dict):
        return
    word = str(spec.get("word") or "").strip()
    _require(word, f"{where}.scope_separation.two_axes.banned_word.word: 비워 둘 수 없음")
    _require(str(spec.get("why") or "").strip(),
             f"{where}.scope_separation.two_axes.banned_word.why: 왜 금지하는지 적어야 함")
    # 금지 규정 블록 자신은 **구조적으로** 제외한다. 그 낱말을 담아야 규정이 성립하므로
    # 스스로를 예외 목록에 적게 하면 순환이다. 내용 쪽 예외(6.4 원문 인용)만 데이터로 받는다.
    own = "scope_separation.two_axes.banned_word"
    allowed = set(spec.get("exceptions") or [])
    offenders = [p for p, text in _strings(sep, "scope_separation")
                 if word in text and p not in allowed and not p.startswith(own)]
    _require(not offenders,
             f"{where}.scope_separation: 금지어 {word!r} 가 예외 밖에서 쓰임 — {offenders}. "
             f"두 축(즉시성·시장성)을 한 낱말로 덮으면 어느 쪽을 묻는지 흐려진다")


# F9 도 F6 와 같은 형태로 정책과 factor range 를 로드 시점에 맞춘다.
# F6 는 파라미터 하한 합계를 맞추는데 F9 는 그런 검사가 없어 범위 밖 점수가 조용히 지나갔다(MISS-LABEL-23).
# 검사 대상은 **점수를 만들어 내는 값**이다. 임계치(연 수·배수)는 점수가 아니라 제외한다.
F9_SCORE_KEYS = ("floor", "g1_bep_retreat_score", "g1_buffer_erosion_min_score", "g1_direction_relief_cap",
                 "g2_fcf_positive_stable", "g2_fcf_positive_deteriorating", "g2_fcf_negative",
                 "g2_private_not_disclosed")


def _validate_f9_policy(f9: Any, factor: dict[str, Any]) -> None:
    _require(isinstance(f9, dict), "rules.policies.f9: object 여야 함")
    lo, hi = factor["range"]
    bad: list[str] = []
    for key in F9_SCORE_KEYS:
        if key not in f9:
            continue
        value = f9[key]
        if _is_number(value) and not (lo <= value <= hi):
            bad.append(f"{key}={value}")
    # 제안 밴드도 점수를 만드는 값이다. status 가 proposed 여도 범위를 벗어나면 채택 시 바로 깨진다.
    for idx, band in enumerate(f9.get("g1_bands_proposed") or []):
        score = band.get("score")
        if _is_number(score) and not (lo <= score <= hi):
            bad.append(f"g1_bands_proposed[{idx}].score={score}")
    _require(not bad,
             f"rules.policies.f9: factors.F9.range {factor['range']} 를 벗어나는 점수 — {', '.join(bad)}. "
             f"밴드 재척도는 C-06 결정 사항이므로 임의로 고쳐 통과시키지 않는다")


# ------------------------------------------------------------------ observations

def _require_ndc_route(item: dict[str, Any], company: dict[str, Any], policy: dict[str, Any], where: str) -> None:
    routes = policy["not_disclosed_confirmed"]["routes"]
    basis = item.get("basis") or {}
    if not company["listed"] and item["metric"] in routes["structural"]["metrics"]:
        return
    need = routes["issuer_declared"]["required_basis_keys"]
    if all(str(basis.get(k) or "").strip() for k in need):
        return
    _require(False, f"{where}: not_disclosed_confirmed 가 규칙이 선언한 두 경로 어느 쪽도 채우지 못함 — "
                    f"비상장 구조 기준이 아니고(listed={company['listed']}, metric={item['metric']!r}) "
                    f"발행사 선언 경로의 basis 키 {need} 도 비어 있다 (rules.policies.missing_types)")


def validate_observations(payload: Any, companies: dict[str, dict[str, Any]], run_id: str | None = None,
                          missing_policy: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    _expect_keys(payload, ["schema", "run_id", "items"], "observations.json", optional=["note", "as_of"])
    _require(payload["schema"] == "scorecard.observations/1", "observations.json: schema 불일치")
    if run_id is not None:
        _require(payload["run_id"] == run_id, f"observations.json: run_id 불일치 {payload['run_id']!r} != {run_id!r}")
    _require(isinstance(payload["items"], list), "observations.json: items 배열 필요")
    seen: set[str] = set()
    items: list[dict[str, Any]] = []
    for idx, item in enumerate(payload["items"]):
        where = f"observations[{idx}]"
        _expect_keys(
            item,
            ["observation_id", "company_id", "metric", "value", "unit", "as_of", "kind", "source_id", "status"],
            where,
            optional=["period", "basis", "raw", "note", "missing_type", "observed_at"],
        )
        # as_of 는 **자료 기준일**이고 observed_at 은 **관측 시점**이다. 두 뜻이 한 필드에 얹혀 있었고
        # 그 결과 값 없는 교체 관측이 승계 관측에 밀렸다 (F6-REG-28). 최신성 판정은 inputs.recency_key 가 한다.
        if "observed_at" in item:
            _expect_date(item["observed_at"], f"{where}.observed_at")
            _require(item["observed_at"] >= item["as_of"],
                     f"{where}: observed_at({item['observed_at']}) 이 as_of({item['as_of']}) 보다 앞섬 — "
                     f"자료 기준일보다 먼저 관측할 수는 없다")
        if "missing_type" in item:
            _require(item["missing_type"] in MISSING_TYPES,
                     f"{where}: missing_type 는 {sorted(MISSING_TYPES)} 중 하나 ({item['missing_type']!r})")
            # 값이 있는데 결측 유형을 다는 것은 모순이다.
            _require(item["value"] is None, f"{where}: value 가 있는데 missing_type 이 붙어 있음")
            # 2026-09-16 FIX-57 2단계: `확인된 미공시` 는 C-16 으로 한 칸을 깎는다. 규칙이 선언한 두 경로 중
            # 하나를 실제로 채우는지 여기서 확인한다 — 라벨만 붙이면 근거 없이 점수가 깎인다.
            if item["missing_type"] == MISSING_TYPE_FOR_DISCLOSURE_POLICY and missing_policy is not None:
                _require_ndc_route(item, companies[item["company_id"]], missing_policy, where)
        oid = item["observation_id"]
        _require(isinstance(oid, str) and oid and oid not in seen, f"{where}: observation_id 누락/중복 {oid!r}")
        seen.add(oid)
        _require(item["company_id"] in companies, f"{where}: 알 수 없는 company_id {item['company_id']!r}")
        metric = item["metric"]
        _require(metric in METRICS, f"{where}: 알 수 없는 metric {metric!r}")
        _require(item["status"] in OBSERVATION_STATUSES, f"{where}: status {item['status']!r} 오류")
        _require(item["kind"] in OBSERVATION_KINDS, f"{where}: kind {item['kind']!r} 오류")
        _expect_date(item["as_of"], f"{where}.as_of")
        value = item["value"]
        if METRICS[metric]["type"] == "number":
            _require(value is None or _is_number(value), f"{where}: {metric} 값은 숫자 또는 null")
            if metric in NON_NEGATIVE_METRICS and value is not None:
                _require(value >= 0, f"{where}: {metric} 은 음수일 수 없음 ({value})")
        else:
            _require(value is None or isinstance(value, str), f"{where}: {metric} 값은 문자열 또는 null")
        if value is None:
            _require(item["status"] != "verified", f"{where}: 값이 null 이면 status 는 verified 일 수 없음")
        if item["status"] == "not_applicable":
            _require(value is None, f"{where}: not_applicable 관측은 값을 가지지 않음")
            _require(str(item.get("note") or "").strip(), f"{where}: not_applicable 은 적용 제외 사유를 note 에 남겨야 함")
        _require(item["unit"] == METRICS[metric]["unit"], f"{where}: unit {item['unit']!r} != {METRICS[metric]['unit']!r}")
        period = item.get("period")
        if item["status"] == "verified" and metric in PERIOD_REQUIRED_METRICS and period is None:
            _require(False, f"{where}: {metric} 은 흐름 지표라 verified 관측에 period(start·end)가 필요함 — 과거 이관분은 legacy_unverified 로 두고 날짜를 지어내지 않는다")
        if period is not None:
            _expect_keys(period, ["start", "end"], f"{where}.period")
            _expect_date(period["start"], f"{where}.period.start")
            _expect_date(period["end"], f"{where}.period.end")
            # 존재만으로는 부족하다. 역전된 기간은 TTM·분기 계산의 분모를 조용히 망가뜨린다.
            _require(period["start"] <= period["end"], f"{where}.period: start 가 end 보다 뒤임 ({period['start']} > {period['end']})")
        basis = item.get("basis")
        _require(basis is None or isinstance(basis, dict), f"{where}: basis 는 object")
        _require(isinstance(item["source_id"], str) and item["source_id"], f"{where}: source_id 필요")
        items.append(item)
    # 같은 기업·지표·시점에 사용 가능한 값이 둘 이상이면 선택이 파일 순서에 의존한다. 충돌은 source_conflict 로 표시해야 한다.
    seen_values: dict[tuple[str, str, str, str | None, str | None], tuple[str, Any]] = {}
    for item in items:
        if item["status"] not in ("verified", "legacy_unverified") or item["value"] is None:
            continue
        # 같은 지표·같은 조회일이라도 회계기간이 다르면 서로 다른 값이다(분기 EPS). 기간을 키에 넣어야 오탐이 없다.
        period = item.get("period") or {}
        key = (item["company_id"], item["metric"], item["as_of"], period.get("start"), period.get("end"))
        if key in seen_values and seen_values[key][1] != item["value"]:
            raise SchemaError(f"observations: {key} 에 서로 다른 값의 관측이 둘 이상 ({seen_values[key][0]}, {item['observation_id']}) — 하나를 source_conflict 로 표시하거나 제거")
        seen_values.setdefault(key, (item["observation_id"], item["value"]))
    return items


# ------------------------------------------------------------------ judgments

def _validate_judgment_inputs(kind: str, inputs: Any, where: str) -> None:
    _require(isinstance(inputs, dict), f"{where}: inputs 는 object")
    if kind == "score":
        return
    if kind == "grade":
        _expect_keys(inputs, ["A", "H"], where)
        _require(inputs["A"] in (0, 1, 2) and not isinstance(inputs["A"], bool), f"{where}: A 는 0/1/2")
        _require(inputs["H"] in (0, -1, -2, -3) and not isinstance(inputs["H"], bool), f"{where}: H 는 0/-1/-2/-3")
        return
    if kind == "criteria":
        _expect_keys(inputs, ["imitation", "revenue_model", "acceleration", "door_closed"], where)
        for key in ("imitation", "revenue_model", "acceleration"):
            _require(inputs[key] in TRI, f"{where}: {key} 는 {sorted(TRI)}")
        _require(inputs["door_closed"] in PASS_FAIL, f"{where}: door_closed 는 {sorted(PASS_FAIL)}")
        return
    if kind == "matrix":
        _expect_keys(inputs, ["funding_dependent_share", "own_money_returns"], where)
        _require(inputs["funding_dependent_share"] in {"large", "small", "unknown"}, f"{where}: funding_dependent_share 오류")
        _require(inputs["own_money_returns"] in YES_NO, f"{where}: own_money_returns 오류")
        return
    if kind == "paths":
        # generation_gap: C-03 확정 모델(v1.7)의 5점 조건. top_rank(AA 종합 1위)는 v1.5·v1.6 후보 매핑의 입력이다.
        _expect_keys(inputs, ["performance_leap", "paradigm_adaptation", "standard_capture", "top_rank"], where,
                     optional=["generation_gap"])
        for key in ("performance_leap", "paradigm_adaptation", "standard_capture"):
            _require(inputs[key] in TRI, f"{where}: {key} 는 {sorted(TRI)}")
        _require(inputs["top_rank"] in YES_NO, f"{where}: top_rank 오류")
        _require(inputs.get("generation_gap", "unknown") in YES_NO, f"{where}: generation_gap 오류")
        return
    if kind == "gate_inputs":
        _expect_keys(
            inputs,
            ["fcf_trend", "bep_retreat", "buffer_erosion", "direction_A", "direction_B", "coverage_comparable"],
            where,
            optional=["fcf_not_disclosed_reason", "offbalance_class", "operating_result_reviewed"],
        )
        _require(inputs["fcf_trend"] in {"stable", "deteriorating", "unknown"}, f"{where}: fcf_trend 오류")
        _require(inputs.get("operating_result_reviewed", "unknown") in {"profit", "loss", "unknown"}, f"{where}: operating_result_reviewed 오류")
        for key in ("bep_retreat", "buffer_erosion", "coverage_comparable"):
            _require(inputs[key] in YES_NO, f"{where}: {key} 오류")
        for key in ("direction_A", "direction_B"):
            _require(inputs[key] in PASS_FAIL, f"{where}: {key} 오류")
        return
    raise SchemaError(f"{where}: 알 수 없는 kind {kind!r}")


def _validate_revision_history(history: Any, where: str) -> None:
    """2026-10-01 레인 J. 사람이 고친 판단의 이전 값·사유·누가·언제. 오래된 것이 앞이다."""
    _require(isinstance(history, list) and history, f"{where}: 비어 있지 않은 배열 필요")
    for idx, entry in enumerate(history):
        at = f"{where}[{idx}]"
        # 2026-10-01 V2-11: session 은 수정한 프로세스가 에이전트 세션이었는지(agent|human). 그 전 기록에는 없다.
        _expect_keys(entry, ["revised_at", "revised_by", "reason", "previous"], at, optional=["session"])
        _require(entry.get("session") in (None, "agent", "human"), f"{at}.session 은 agent|human")
        _expect_date(entry["revised_at"], f"{at}.revised_at")
        for key in ("revised_by", "reason"):
            _require(isinstance(entry[key], str) and entry[key].strip(), f"{at}: {key} 는 비어 있지 않은 문자열")
        _expect_keys(entry["previous"], list(JUDGMENT_REVISION_FIELDS), f"{at}.previous")


def validate_judgments(payload: Any, companies: dict[str, dict[str, Any]], rules: dict[str, Any], run_id: str | None = None) -> list[dict[str, Any]]:
    _expect_keys(payload, ["schema", "run_id", "items"], "judgments.json", optional=["note"])
    _require(payload["schema"] == "scorecard.judgments/1", "judgments.json: schema 불일치")
    if run_id is not None:
        _require(payload["run_id"] == run_id, f"judgments.json: run_id 불일치 {payload['run_id']!r} != {run_id!r}")
    _require(isinstance(payload["items"], list), "judgments.json: items 배열 필요")
    seen: set[str] = set()
    pairs: set[tuple[str, str]] = set()
    items: list[dict[str, Any]] = []
    for idx, item in enumerate(payload["items"]):
        where = f"judgments[{idx}]"
        _expect_keys(
            item,
            ["judgment_id", "company_id", "factor", "kind", "score", "inputs", "evidence", "reviewer", "reviewed_at", "status"],
            where,
            optional=["counter_evidence", "source_ids", "carried_from", "note", "previous_judgment_id", "superseded",
                      "evidence_ids", "revision_history"],
        )
        if "revision_history" in item:
            _validate_revision_history(item["revision_history"], f"{where}.revision_history")
        if "evidence_ids" in item:
            # 2026-09-30 레인 E: 판단이 인용하는 근거(evidence.json). 실재·확정 여부는 validate_cross_refs 가 본다.
            _require(isinstance(item["evidence_ids"], list) and all(isinstance(e, str) and e for e in item["evidence_ids"]),
                     f"judgments[{idx}]: evidence_ids 는 문자열 배열")
        if "superseded" in item:
            # 2026-09-14 F5-IMPL-48: 기업·factor 당 판단이 하나라 옛 판단을 별도 항목으로 둘 수 없다.
            # 교체된 판단의 문언은 지우지 않고 새 판단 안에 그대로 싣는다.
            sup = _expect_keys(
                item["superseded"],
                ["judgment_id", "inputs", "evidence", "reviewer", "reviewed_at", "superseded_at", "why"],
                f"{where}.superseded",
                optional=["score", "status", "carried_from", "note", "counter_evidence", "source_ids"],
            )
            _require(item.get("previous_judgment_id") == sup["judgment_id"],
                     f"{where}: superseded.judgment_id 가 previous_judgment_id 와 일치해야 함")
            _require(isinstance(sup["evidence"], list) and any(isinstance(e, str) and e.strip() for e in sup["evidence"]),
                     f"{where}.superseded: 옛 근거 문언이 비어 있음")
            _expect_date(sup["superseded_at"], f"{where}.superseded.superseded_at")
        jid = item["judgment_id"]
        _require(isinstance(jid, str) and jid and jid not in seen, f"{where}: judgment_id 누락/중복 {jid!r}")
        seen.add(jid)
        _require(item["company_id"] in companies, f"{where}: 알 수 없는 company_id {item['company_id']!r}")
        factor = item["factor"]
        _require(factor in FACTOR_IDS, f"{where}: factor {factor!r} 오류")
        pair = (item["company_id"], factor)
        _require(pair not in pairs, f"{where}: {pair} 판단 중복 — 기업·factor 당 하나")
        pairs.add(pair)
        kind = item["kind"]
        _require(kind in FACTOR_JUDGMENT_KINDS[factor], f"{where}: {factor} 에 kind {kind!r} 불허 (허용 {sorted(FACTOR_JUDGMENT_KINDS[factor])})")
        _require(item["status"] in JUDGMENT_STATUSES, f"{where}: status {item['status']!r} 오류")
        if item["status"] == "carried":
            _require(isinstance(item.get("carried_from"), str) and item["carried_from"], f"{where}: carried 판단은 carried_from 필요")
        _expect_date(item["reviewed_at"], f"{where}.reviewed_at")
        _require(isinstance(item["reviewer"], str) and item["reviewer"], f"{where}: reviewer 필요")
        _require(isinstance(item["evidence"], list) and all(isinstance(e, str) for e in item["evidence"]), f"{where}: evidence 는 문자열 배열")
        # 근거 없는 판단은 점수를 만들 수 없다 (R06). 승계 판단도 원문 근거를 함께 옮겨야 한다.
        _require(any(e.strip() for e in item["evidence"]), f"{where}: evidence 가 비어 있음 — 근거 없는 판단 불허")
        lo, hi = rules["factors"][factor]["range"]
        score = item["score"]
        if kind == "score":
            _require(_is_number(score) and float(score).is_integer(), f"{where}: score 는 정수 필요")
            _require(lo <= score <= hi, f"{where}: score {score} 가 {factor} 범위 [{lo}, {hi}] 밖")
            if factor == "F6":
                # 2026-09-14 IMPL-46: 문구가 bands 시절 'NTM PER 자동 산출' 이었다. 정본은 parameters 다.
                _require(not companies[item["company_id"]]["listed"], f"{where}: 상장사 F6 는 수동 score 불허 (parameters 자동 산출)")
            if factor in {"F2", "F7"}:
                _require(item["status"] == "carried", f"{where}: {factor} 의 수동 score 는 승계(carried) 판단에만 허용 — 신규는 paths/matrix 입력 필요")
        else:
            _require(score is None, f"{where}: kind {kind!r} 판단의 score 는 null (자동 산출)")
        _validate_judgment_inputs(kind, item["inputs"], f"{where}.inputs")
        if kind == "matrix":
            # 매트릭스 판단은 score 를 들지 않으므로 **입력이 가리키는 칸**의 점수를 range 와 대조한다(FIX-52).
            key = f"{item['inputs'].get('funding_dependent_share')}|{item['inputs'].get('own_money_returns')}"
            cell = (rules["factors"][factor].get("matrix") or {}).get(key)
            if cell is not None:
                _require(lo <= cell <= hi,
                         f"{where}: {item['company_id']} {factor} 매트릭스 출력 {key}={cell} 가 range [{lo}, {hi}] 밖")
        items.append(item)
    return items


# ------------------------------------------------------------------ sources / evidence / triggers
# 2026-09-30 레인 E. 근거 계층의 세 파일. 기존 두 실행의 sources.json 은 최상위 {schema, run_id, items} 와
# 항목 8키만 쓴다 — 그 모양을 그대로 받고, 수집기가 붙이는 선택 키만 더 허용한다.

SOURCE_REQUIRED_KEYS = ["source_id", "title", "publisher", "url", "accessed_at", "sha256", "conflict_of_interest", "note"]
SOURCE_OPTIONAL_KEYS = ["kind", "company_id", "published_at_utc", "publisher_url", "raw_ref"]
SOURCE_KINDS = {"news", "filing", "price"}
ISO_UTC_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
EVIDENCE_KINDS = {"news", "filing"}
EVIDENCE_CHANNELS = {"disclosure", "press", "company_statement", "secondary"}
EVIDENCE_STATUSES = {"candidate", "confirmed"}
EVIDENCE_CHANGES = {"new", "updated", "unchanged"}
EXCERPT_MAX = 600
TRIGGER_ID_RE = re.compile(r"^TRG-\d{3}$")
TRIGGER_STATUSES = {"watching", "fired", "expired", "withdrawn"}
# C-14: 트리거는 미래 점수를 저장하지 않는다(design-guideline 272행). 키 이름으로 점수처럼 보이는 필드를 막는다.
SCORE_LIKE_KEY_RE = re.compile(r"score|점수|rating|points|delta|expected|target", re.I)
# C-14: `conditional_impact` 에 점수 이동(-3→-4, +2점)을 적지 않는다. 사건의 조건부 영향은 말로 쓴다.
SCORE_TEXT_RE = re.compile(r"[-+−]?\d+\s*(?:→|->)\s*[-+−]?\d+|[-+−]?\d+\s*점")


def _expect_str(value: Any, where: str, *, allow_none: bool = False, nonempty: bool = False) -> None:
    if value is None and allow_none:
        return
    _require(isinstance(value, str) and (not nonempty or bool(value.strip())), f"{where}: 문자열 필요 ({value!r})")


def _expect_str_list(value: Any, where: str, *, nonempty: bool = False) -> None:
    _require(isinstance(value, list) and all(isinstance(v, str) and v for v in value), f"{where}: 문자열 배열 필요")
    _require(not nonempty or bool(value), f"{where}: 비어 있지 않아야 함")


def _expect_factors(value: Any, where: str) -> None:
    _expect_str_list(value, where, nonempty=True)
    bad = [f for f in value if f not in FACTOR_IDS]
    _require(not bad, f"{where}: 알 수 없는 factor {bad} (허용 {list(FACTOR_IDS)})")
    _require(len(set(value)) == len(value), f"{where}: factor 중복")


def _expect_iso_utc(value: Any, where: str) -> None:
    if value is None:
        return
    _require(isinstance(value, str) and bool(ISO_UTC_RE.match(value)), f"{where}: YYYY-MM-DDTHH:MM:SSZ 또는 null ({value!r})")


def _expect_top(payload: Any, schema: str, name: str, run_id: str | None) -> list[Any]:
    _expect_keys(payload, ["schema", "run_id", "items"], name, optional=["note"])
    _require(payload["schema"] == schema, f"{name}: schema 는 {schema!r} ({payload['schema']!r})")
    if run_id is not None:
        _require(payload["run_id"] == run_id, f"{name}: run_id 불일치 {payload['run_id']!r} != {run_id!r}")
    _require(isinstance(payload["items"], list), f"{name}: items 배열 필요")
    return payload["items"]


def validate_sources(payload: Any, run_id: str | None = None) -> list[dict[str, Any]]:
    items = _expect_top(payload, "scorecard.sources/1", "sources.json", run_id)
    seen: set[str] = set()
    for idx, item in enumerate(items):
        where = f"sources[{idx}]"
        _expect_keys(item, SOURCE_REQUIRED_KEYS, where, optional=SOURCE_OPTIONAL_KEYS)
        sid = item["source_id"]
        _require(isinstance(sid, str) and sid.strip(), f"{where}: source_id 필요")
        _require(sid not in seen, f"{where}: source_id 중복 {sid!r}")
        seen.add(sid)
        _expect_str(item["title"], f"{where}.title", nonempty=True)
        _expect_str(item["publisher"], f"{where}.publisher", allow_none=True)
        # URL 이 없는 내부 문서가 있다. 없는 URL 을 만들지 않으므로 null 을 허용한다.
        _expect_str(item["url"], f"{where}.url", allow_none=True)
        _expect_str(item["accessed_at"], f"{where}.accessed_at", nonempty=True)
        _require(bool(DATE_RE.match(item["accessed_at"]) or ISO_UTC_RE.match(item["accessed_at"])),
                 f"{where}.accessed_at: 날짜 또는 UTC ISO 시각 필요 ({item['accessed_at']!r})")
        _expect_sha(item["sha256"], f"{where}.sha256", allow_none=True)
        _expect_str(item["conflict_of_interest"], f"{where}.conflict_of_interest", allow_none=True)
        _expect_str(item["note"], f"{where}.note", allow_none=True)
        if "kind" in item:
            _require(item["kind"] in SOURCE_KINDS, f"{where}.kind 는 {sorted(SOURCE_KINDS)} 중 하나 ({item['kind']!r})")
        if "company_id" in item:
            _expect_str(item["company_id"], f"{where}.company_id", nonempty=True)
        if "published_at_utc" in item:
            _expect_iso_utc(item["published_at_utc"], f"{where}.published_at_utc")
        if "publisher_url" in item:
            pu = item["publisher_url"]
            _require(isinstance(pu, str) or (isinstance(pu, list) and all(isinstance(u, str) for u in pu)),
                     f"{where}.publisher_url: 문자열 또는 문자열 배열")
        if "raw_ref" in item:
            _expect_str(item["raw_ref"], f"{where}.raw_ref", nonempty=True)
    return items


def validate_evidence(payload: Any, companies: dict[str, dict[str, Any]], source_ids: set[str],
                      run_id: str | None = None) -> list[dict[str, Any]]:
    items = _expect_top(payload, "scorecard.evidence/1", "evidence.json", run_id)
    seen: set[str] = set()
    for idx, item in enumerate(items):
        where = f"evidence[{idx}]"
        _expect_keys(
            item,
            ["evidence_id", "company_id", "factors", "kind", "source_id", "published_at_utc", "title", "excerpt",
             "relevance", "channel", "conditional_impact", "horizon", "counter_evidence", "unverified", "change_vs_previous"],
            where,
            optional=["previous_evidence_id", "reviewer", "reviewed_at", "status"],
        )
        cid = item["company_id"]
        _require(cid in companies, f"{where}: 알 수 없는 company_id {cid!r}")
        eid = item["evidence_id"]
        _require(isinstance(eid, str) and bool(re.fullmatch(rf"EV-{re.escape(cid)}-\d{{3}}", eid)),
                 f"{where}: evidence_id 는 EV-{cid}-NNN 형식 ({eid!r})")
        _require(eid not in seen, f"{where}: evidence_id 중복 {eid!r}")
        seen.add(eid)
        _expect_factors(item["factors"], f"{where}.factors")
        _require(item["kind"] in EVIDENCE_KINDS, f"{where}.kind 는 {sorted(EVIDENCE_KINDS)} 중 하나 ({item['kind']!r})")
        _require(item["source_id"] in source_ids, f"{where}: source_id {item['source_id']!r} 가 sources.json 에 없음")
        _expect_iso_utc(item["published_at_utc"], f"{where}.published_at_utc")
        _expect_str(item["title"], f"{where}.title", nonempty=True)
        _expect_str(item["excerpt"], f"{where}.excerpt", nonempty=True)
        _require(len(item["excerpt"]) <= EXCERPT_MAX, f"{where}.excerpt: {EXCERPT_MAX}자 이하 ({len(item['excerpt'])}자)")
        _expect_str(item["relevance"], f"{where}.relevance", nonempty=True)
        _require(item["channel"] in EVIDENCE_CHANNELS, f"{where}.channel 는 {sorted(EVIDENCE_CHANNELS)} 중 하나 ({item['channel']!r})")
        impact = item["conditional_impact"]
        _expect_str(impact, f"{where}.conditional_impact", allow_none=True)
        _require(impact is None or not SCORE_TEXT_RE.search(impact),
                 f"{where}.conditional_impact: 점수 이동을 적지 않는다(C-14) ({impact!r})")
        _expect_str(item["horizon"], f"{where}.horizon", nonempty=True)
        _expect_str_list(item["counter_evidence"], f"{where}.counter_evidence")
        _expect_str_list(item["unverified"], f"{where}.unverified")
        _require(item["change_vs_previous"] is None or item["change_vs_previous"] in EVIDENCE_CHANGES,
                 f"{where}.change_vs_previous 는 {sorted(EVIDENCE_CHANGES)} 또는 null")
        if "previous_evidence_id" in item:
            _expect_str(item["previous_evidence_id"], f"{where}.previous_evidence_id", nonempty=True)
        status = item.get("status", "candidate")
        _require(status in EVIDENCE_STATUSES, f"{where}.status 는 {sorted(EVIDENCE_STATUSES)} 중 하나 ({status!r})")
        if "reviewer" in item:
            _expect_str(item["reviewer"], f"{where}.reviewer", nonempty=True)
        if "reviewed_at" in item:
            _expect_date(item["reviewed_at"], f"{where}.reviewed_at")
        if status == "confirmed":
            # 판단과 같은 규칙이다. 사람이 확인하지 않은 근거를 확정으로 올리지 않는다.
            _require("reviewer" in item and "reviewed_at" in item, f"{where}: confirmed 근거는 reviewer·reviewed_at 필요")
    return items


def _score_like_keys(node: Any, path: str) -> list[str]:
    hits: list[str] = []
    if isinstance(node, dict):
        for key, value in node.items():
            if SCORE_LIKE_KEY_RE.search(str(key)):
                hits.append(f"{path}.{key}")
            hits += _score_like_keys(value, f"{path}.{key}")
    elif isinstance(node, list):
        for i, value in enumerate(node):
            hits += _score_like_keys(value, f"{path}[{i}]")
    return hits


def validate_triggers(payload: Any, companies: dict[str, dict[str, Any]], evidence_ids: set[str], source_ids: set[str],
                      run_id: str | None = None) -> list[dict[str, Any]]:
    items = _expect_top(payload, "scorecard.triggers/2", "triggers.json", run_id)
    seen: set[str] = set()
    for idx, item in enumerate(items):
        where = f"triggers[{idx}]"
        scored = _score_like_keys(item, where)
        _require(not scored, f"{where}: 트리거는 미래 점수를 저장하지 않는다(C-14) — 점수처럼 보이는 키 {scored}")
        _expect_keys(
            item,
            ["trigger_id", "company_id", "factors", "observation", "condition", "deadline", "evidence_ids", "source_ids",
             "status", "recheck"],
            where,
            optional=["legacy_ref", "note"],
        )
        tid = item["trigger_id"]
        _require(isinstance(tid, str) and bool(TRIGGER_ID_RE.match(tid)), f"{where}: trigger_id 는 TRG-NNN 형식 ({tid!r})")
        _require(tid not in seen, f"{where}: trigger_id 중복 {tid!r}")
        seen.add(tid)
        _require(item["company_id"] in companies, f"{where}: 알 수 없는 company_id {item['company_id']!r}")
        _expect_factors(item["factors"], f"{where}.factors")
        _expect_str(item["observation"], f"{where}.observation", nonempty=True)
        _expect_str(item["condition"], f"{where}.condition", nonempty=True)
        _expect_date(item["deadline"], f"{where}.deadline")
        _expect_str_list(item["evidence_ids"], f"{where}.evidence_ids")
        unknown_ev = [e for e in item["evidence_ids"] if e not in evidence_ids]
        _require(not unknown_ev, f"{where}: evidence.json 에 없는 evidence_ids {unknown_ev}")
        _expect_str_list(item["source_ids"], f"{where}.source_ids")
        unknown_src = [s for s in item["source_ids"] if s not in source_ids]
        _require(not unknown_src, f"{where}: sources.json 에 없는 source_ids {unknown_src}")
        _require(item["status"] in TRIGGER_STATUSES, f"{where}.status 는 {sorted(TRIGGER_STATUSES)} 중 하나 ({item['status']!r})")
        recheck = _expect_keys(item["recheck"], ["factors", "what"], f"{where}.recheck")
        _expect_factors(recheck["factors"], f"{where}.recheck.factors")
        _expect_str(recheck["what"], f"{where}.recheck.what", nonempty=True)
        if "legacy_ref" in item:
            _expect_str(item["legacy_ref"], f"{where}.legacy_ref", nonempty=True)
        if "note" in item:
            _expect_str(item["note"], f"{where}.note")
    return items


# 2026-10-01 판단 변경 제안. 에이전트가 research 뒤 바꾸고 싶은 판단을 제안으로 쓰고, 사람이 승인 페이지에서 반영·거부한다.
# 입력 해시에 들지 않는다. 반영하면 judge(revise_judgment)를 거쳐 judgments 가 바뀐다. 거부는 사유가 필수다.
PROPOSAL_ID_RE = re.compile(r"^PRP-\d{3}$")
PROPOSAL_STATUSES = {"pending", "accepted", "rejected"}
PROPOSAL_SNAPSHOT_KEYS = ("kind", "score", "inputs", "evidence")


def validate_proposals(payload: Any, companies: dict[str, dict[str, Any]], evidence_ids: set[str],
                       run_id: str | None = None) -> list[dict[str, Any]]:
    items = _expect_top(payload, "scorecard.proposals/1", "proposals.json", run_id)
    seen: set[str] = set()
    for idx, item in enumerate(items):
        where = f"proposals[{idx}]"
        _expect_keys(item, ["proposal_id", "company_id", "factor", "changes", "evidence_after", "reason", "evidence_ids",
                            "before", "proposed_by", "proposed_at", "status"],
                     where, optional=["decided_by", "decided_at", "decision_note"])
        pid = item["proposal_id"]
        _require(isinstance(pid, str) and bool(PROPOSAL_ID_RE.match(pid)), f"{where}: proposal_id 는 PRP-NNN 형식 ({pid!r})")
        _require(pid not in seen, f"{where}: proposal_id 중복 {pid!r}")
        seen.add(pid)
        _require(item["company_id"] in companies, f"{where}: 알 수 없는 company_id {item['company_id']!r}")
        _require(item["factor"] in JUDGMENT_EDIT_KIND, f"{where}: {item['factor']!r} 는 제안 대상 factor 가 아니다")
        _require(isinstance(item["changes"], dict), f"{where}.changes 는 object")
        after = item["evidence_after"]
        _require(after is None or (isinstance(after, list) and bool(after) and all(isinstance(s, str) and s.strip() for s in after)),
                 f"{where}.evidence_after 는 null 이거나 비어 있지 않은 문장 목록")
        _require(bool(item["changes"]) or after is not None, f"{where}: 바꿀 값(changes)이나 근거 문장(evidence_after)이 있어야 한다")
        _expect_str(item["reason"], f"{where}.reason", nonempty=True)
        _expect_str_list(item["evidence_ids"], f"{where}.evidence_ids")
        unknown = [e for e in item["evidence_ids"] if e not in evidence_ids]
        _require(not unknown, f"{where}: evidence.json 에 없는 evidence_ids {unknown}")
        _expect_keys(item["before"], list(PROPOSAL_SNAPSHOT_KEYS), f"{where}.before")
        _expect_str(item["proposed_by"], f"{where}.proposed_by", nonempty=True)
        _expect_date(item["proposed_at"], f"{where}.proposed_at")
        status = item["status"]
        _require(status in PROPOSAL_STATUSES, f"{where}.status 는 {sorted(PROPOSAL_STATUSES)} 중 하나 ({status!r})")
        if status != "pending":
            _expect_str(item.get("decided_by"), f"{where}.decided_by", nonempty=True)
            _expect_date(item.get("decided_at"), f"{where}.decided_at")
        if status == "rejected":
            _expect_str(item.get("decision_note"), f"{where}.decision_note(거부 사유)", nonempty=True)
        if "decision_note" in item:
            _expect_str(item["decision_note"], f"{where}.decision_note", allow_none=True)
    return items


def validate_cross_refs(observations: list[dict[str, Any]], judgments: list[dict[str, Any]],
                        evidence: list[dict[str, Any]] | None, sources: list[dict[str, Any]]) -> None:
    """관측·판단·근거가 가리키는 출처와 근거가 장부에 실재하는지. 새 판단은 확정 근거만 인용한다."""
    source_ids = {s["source_id"] for s in sources}
    missing_obs = sorted({o["source_id"] for o in observations if o["source_id"] not in source_ids})
    _require(not missing_obs, f"교차 참조: observations 의 source_id {missing_obs} 가 sources.json 에 없음")
    missing_jud = sorted({s for j in judgments for s in (j.get("source_ids") or []) if s not in source_ids})
    _require(not missing_jud, f"교차 참조: judgments 의 source_ids {missing_jud} 가 sources.json 에 없음")
    ev_status = {e["evidence_id"]: e.get("status", "candidate") for e in (evidence or [])}
    missing_ev_src = sorted({e["source_id"] for e in (evidence or []) if e["source_id"] not in source_ids})
    _require(not missing_ev_src, f"교차 참조: evidence 의 source_id {missing_ev_src} 가 sources.json 에 없음")
    for j in judgments:
        cited = j.get("evidence_ids") or []
        unknown = [e for e in cited if e not in ev_status]
        _require(not unknown, f"교차 참조: {j['judgment_id']} 의 evidence_ids {unknown} 가 evidence.json 에 없음")
        if j["status"] == "new":
            unconfirmed = [e for e in cited if ev_status[e] != "confirmed"]
            _require(not unconfirmed,
                     f"교차 참조: 새 판단 {j['judgment_id']} 가 확정되지 않은 근거 {unconfirmed} 를 인용 — confirmed 근거만 인용한다")


# ------------------------------------------------------------------ run / approval

def validate_run(payload: Any, slug: str | None = None) -> dict[str, Any]:
    _expect_keys(
        payload,
        ["schema", "run_id", "report_type", "title", "as_of", "rule_version", "baseline_id", "companies", "decisions", "created_at", "purpose", "assumptions"],
        "run.json",
        optional=["price_as_of", "info_cutoff", "reference_companies", "rule_hash", "note", "sources_file", "continued_from"],
    )
    _require(payload["schema"] == "scorecard.run/1", "run.json: schema 불일치")
    _require(payload["report_type"] == "ai_scorecard", "run.json: report_type 은 ai_scorecard")
    if slug is not None:
        _require(payload["run_id"] == slug, f"run.json: run_id {payload['run_id']!r} != slug {slug!r}")
    _expect_date(payload["as_of"], "run.json.as_of")
    _expect_date(payload.get("price_as_of"), "run.json.price_as_of", allow_none=True)
    _expect_date(payload.get("info_cutoff"), "run.json.info_cutoff", allow_none=True)
    _expect_date(payload["created_at"], "run.json.created_at")
    _require(isinstance(payload["companies"], list) and payload["companies"], "run.json: companies 비어 있음")
    _require(isinstance(payload["assumptions"], list), "run.json: assumptions 는 배열")
    for idx, d in enumerate(payload["decisions"]):
        _expect_keys(d, ["id", "choice", "rationale", "decided_by", "decided_at"], f"run.decisions[{idx}]")
        _require(isinstance(d["rationale"], str) and d["rationale"].strip(), f"run.decisions[{idx}]: rationale 필요")
        _expect_date(d["decided_at"], f"run.decisions[{idx}].decided_at")
    if "continued_from" in payload:
        _validate_continued_from(payload["continued_from"], payload["companies"])
    return payload


def _validate_continued_from(value: Any, companies: list[str]) -> None:
    """2026-09-21 ADD-03. 이어받기는 어느 실행에서 무엇을 가져왔는지 run 수준에만 적는다.

    항목(판단·관측)에는 아무 표시도 찍지 않는다. `status: carried` 는 **기준선 승계**라는 뜻으로
    이미 점유돼 있고, 그것을 재작성하면 기존 기업의 factor 상태와 경고가 바뀐다.
    """
    where = "run.continued_from"
    _expect_keys(value, ["run_id", "as_of", "rule_hash", "hashes", "results_hash", "approval_id", "added_companies"], where)
    _require(isinstance(value["run_id"], str) and bool(ID_RE.match(value["run_id"])), f"{where}.run_id: 실행 slug 필요")
    _expect_date(value["as_of"], f"{where}.as_of")
    _expect_sha(value["rule_hash"], f"{where}.rule_hash")
    _expect_keys(value["hashes"], ["run", "observations", "judgments", "sources"], f"{where}.hashes")
    for key, digest in value["hashes"].items():
        _expect_sha(digest, f"{where}.hashes.{key}")
    _expect_sha(value["results_hash"], f"{where}.results_hash", allow_none=True)
    _require(value["approval_id"] is None or (isinstance(value["approval_id"], str) and value["approval_id"].strip()),
             f"{where}.approval_id: 문자열이거나 null")
    _require(isinstance(value["added_companies"], list), f"{where}.added_companies: 배열 필요")
    outside = [c for c in value["added_companies"] if c not in companies]
    _require(not outside, f"{where}.added_companies: run.companies 에 없는 기업 {outside}")


def _expect_sha(value: Any, where: str, allow_none: bool = False) -> None:
    if value is None and allow_none:
        return
    _require(isinstance(value, str) and bool(SHA256_RE.match(value)), f"{where}: sha256 16진 64자 필요 ({value!r})")


def validate_approval(payload: Any, run_id: str | None = None) -> dict[str, Any]:
    _expect_keys(payload, ["schema", "run_id", "approval_id", "approved_by", "approved_at", "hashes"], "approval.json", optional=["note", "approved_via"])
    _require(payload["schema"] == "scorecard.approval/1", "approval.json: schema 불일치")
    if run_id is not None:
        _require(payload["run_id"] == run_id, "approval.json: run_id 불일치")
    _require(isinstance(payload["approved_by"], str) and payload["approved_by"].strip(),
             f"approval.json: approved_by 는 비어 있지 않은 문자열이어야 함 ({payload['approved_by']!r})")
    _expect_date(payload["approved_at"], "approval.json.approved_at")
    # 2026-09-30 레인 F: 승인 경로는 선택 키다. 기존 두 실행의 승인에는 없다.
    if "approved_via" in payload:
        _require(payload["approved_via"] in APPROVAL_VIA, f"approval.json.approved_via 는 {list(APPROVAL_VIA)} 중 하나 ({payload['approved_via']!r})")
    # 2026-09-30 레인 E: sources·evidence·triggers 는 선택이다. 기존 두 실행의 승인은 6키만 담는다.
    # 대조 규칙은 `stages.approval_mismatches` 한 곳에 있다.
    _expect_keys(payload["hashes"], APPROVAL_REQUIRED_HASHES, "approval.hashes", optional=APPROVAL_OPTIONAL_HASHES)
    for key, digest in payload["hashes"].items():
        _require(isinstance(digest, str), f"approval.hashes.{key}: 문자열 필요 ({digest!r})")
    # 2026-10-01 레인 N(V2-3): approval_id 는 실행·결과·초안 해시에서 정해진다. 손으로 쓴 임의 값은 승인이 아니다.
    expected = approval_id_for(payload["run_id"], payload["hashes"])
    _require(payload["approval_id"] == expected,
             f"approval.json: approval_id {payload['approval_id']!r} 가 실행·결과·초안 해시로 다시 계산한 값 {expected!r} 와 다름")
    return payload


def approval_id_for(run_id: str, hashes: dict[str, str]) -> str:
    """승인 id. `stages.approve` 가 만들고 `validate_approval` 이 다시 계산해 대조한다. **계산은 여기 한 곳이다.**"""
    return sha256_text(f"{run_id}:{hashes['results']}:{hashes['draft']}")[:16]


APPROVAL_REQUIRED_HASHES = ["rules", "observations", "judgments", "run", "results", "draft"]
APPROVAL_OPTIONAL_HASHES = ["sources", "evidence", "triggers"]
APPROVAL_VIA = ("browser", "terminal")
