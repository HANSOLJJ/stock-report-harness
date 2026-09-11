# scorecard 데이터 계약(companies·rules·observations·judgments·run·approval)의 엄격 파서와 정규 해시 유틸
from __future__ import annotations

import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any, Iterable

FACTOR_IDS: tuple[str, ...] = ("F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9")
MOAT_FACTORS: tuple[str, ...] = ("F1", "F2", "F3", "F4", "F5")
TRAP_FACTORS: tuple[str, ...] = ("F6", "F7", "F8", "F9")

COMPANY_TYPES = {"소비자", "업무", "거래", "부품", "소비자·업무", "혼합"}
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
    "net_income_ttm", "revenue_ttm_prior",
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
    "operating_income_ttm": {"unit": "USD", "type": "number"},
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

NON_NEGATIVE_METRICS = {"price", "market_cap", "revenue_ttm", "capex_ttm", "cash", "undrawn_credit", "offbalance_B", "contracted_revenue", "runway_years", "post_money_valuation", "arr", "ttm_revenue_est", "cumulative_raised", "cds_5y_bp"}
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*$")


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


def load_json_strict(path: Path) -> Any:
    if not path.is_file():
        raise SchemaError(f"파일 없음: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"), parse_constant=_reject_constant)
    except json.JSONDecodeError as exc:
        raise SchemaError(f"JSON 파싱 실패: {path}: {exc}") from exc


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=False) + "\n", encoding="utf-8")


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
        _expect_keys(
            item,
            ["company_id", "display_name", "aliases", "type", "listed", "ticker", "exchange", "share_basis", "adr_ratio", "reporting_currency", "scope"],
            where,
            optional=["reference", "note", "status"],
        )
        cid = item["company_id"]
        _require(isinstance(cid, str) and bool(ID_RE.match(cid)), f"{where}: company_id 형식 오류 {cid!r}")
        _require(cid not in out, f"{where}: company_id 중복 {cid!r}")
        _require(isinstance(item["display_name"], str) and item["display_name"].strip(), f"{where}: display_name 필요")
        _require(isinstance(item["aliases"], list) and all(isinstance(a, str) for a in item["aliases"]), f"{where}: aliases 는 문자열 배열")
        _require(item["type"] in COMPANY_TYPES, f"{where}: type {item['type']!r} 는 {sorted(COMPANY_TYPES)} 중 하나")
        _require(isinstance(item["listed"], bool), f"{where}: listed 는 bool")
        _require(item["ticker"] is None or isinstance(item["ticker"], str), f"{where}: ticker 는 문자열 또는 null")
        _require(item["share_basis"] in {"common", "adr", "ads", "private"}, f"{where}: share_basis 오류")
        _require(item["adr_ratio"] is None or _is_number(item["adr_ratio"]), f"{where}: adr_ratio 숫자 또는 null")
        _require(isinstance(item["reporting_currency"], str), f"{where}: reporting_currency 필요")
        _require(isinstance(item.get("reference", False), bool), f"{where}: reference 는 bool")
        out[cid] = item
    return out


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
        optional=["note", "sources"],
    )
    _require(payload["schema"] == "scorecard.rules/1", "rules.json: schema 불일치")
    _require(payload["status"] in {"active", "draft", "retired"}, "rules.json: status 오류")
    factors = payload["factors"]
    _require(set(factors.keys()) == set(FACTOR_IDS), f"rules.json: factors 키는 {FACTOR_IDS} 여야 함")
    for fid, spec in factors.items():
        _require(isinstance(spec, dict) and "range" in spec and "mode" in spec and "label" in spec, f"rules.json.factors.{fid}: label/range/mode 필요")
        lo, hi = spec["range"]
        _require(_is_number(lo) and _is_number(hi) and lo <= hi, f"rules.json.factors.{fid}: range 오류")
    _validate_f6_policy(payload["policies"]["f6"], factors["F6"])
    _validate_f9_policy(payload["policies"]["f9"], factors["F9"])
    for item in payload["checklist"]:
        _expect_keys(item, ["id", "focus"], "rules.checklist", optional=["case"])
    ids = [d["id"] for d in payload["decisions"]]
    _require(len(ids) == len(set(ids)), "rules.json: decisions id 중복")
    for d in payload["decisions"]:
        _expect_keys(d, ["id", "status", "summary"], f"rules.decisions[{d.get('id')}]", optional=["recommendation", "affects", "choices", "blocking"])
        _require(d["status"] in {"documented", "pending", "resolved"}, f"rules.decisions[{d['id']}]: status 오류")
    if "sources" in payload:
        _validate_source_policy(payload["sources"])
    return payload


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
                 optional=["conditional_candidates", "not_adopted", "usage_scope", "unlisted"])
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
        _require(entry["reason_type"] in ("cost", "technical", "terms", "redundant"),
                 f"{where}: reason_type 은 cost/technical/terms/redundant 중 하나여야 함")
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


# F6 는 두 모드가 공존한다. v1.5·v1.6 은 NTM PER 단일 구간표(bands), v1.7 은 네 파라미터(parameters)다.
# 과거 규칙 파일을 계속 읽을 수 있어야 하므로 한쪽을 지우지 않고 둘 다 검증한다.
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


def _validate_f6_policy(f6: Any, factor: dict[str, Any]) -> None:
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
                     where, optional=["requires_positive", "currency_note"])
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
                               "decided_at", "decided_by"])
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

    tracks = f6.get("tracks")
    _require(isinstance(tracks, dict) and tracks, "rules.policies.f6.tracks: 비어 있을 수 없음")
    factor_min = factor["range"][0]
    for tid, spec in tracks.items():
        where = f"rules.policies.f6.tracks.{tid}"
        _expect_keys(spec, ["label", "parameters", "floor", "select"], where,
                     optional=["auto_p4_conditions", "note", "ceiling"])
        _require(_is_number(spec["floor"]) and factor_min <= spec["floor"] <= 0,
                 f"{where}: floor 가 factor range {factor['range']} 밖")
        # 비상장은 0·-1 칸이 없다(v1.5 구간표). 천장을 선언하면 floor 와 factor range 안이어야 한다.
        if "ceiling" in spec:
            _require(_is_number(spec["ceiling"]) and spec["floor"] <= spec["ceiling"] <= 0,
                     f"{where}: ceiling {spec['ceiling']!r} 이 floor {spec['floor']} 와 0 사이가 아님")
        for pid in spec["parameters"]:
            _require(pid in params or pid == "P4", f"{where}.parameters: 알 수 없는 파라미터 {pid!r}")
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
            # 답을 먼저 알고 정한 보정이라는 사실이 규칙 파일에 남아 있어야 한다(C-12).
            _require(str(cond.get("threshold_source") or "").strip(),
                     f"{cw}: threshold_source 를 비워 둘 수 없음 — 임계를 어디서 가져왔는지 적는다")
        _require(str(correction.get("weakness") or "").strip(),
                 f"{where}: weakness 를 비워 둘 수 없음 — 이 보정이 답을 먼저 알고 정해졌다는 사실을 남긴다")

    net_cash = f6.get("net_cash")
    if net_cash:
        _validate_net_cash(net_cash)

    # 파라미터 합계 하한이 factor range 하한과 맞아야 배점 재배분이 규칙 안에서 검산된다.
    _require(total_min == factor_min,
             f"rules.policies.f6: 파라미터 합계 하한 {total_min} 이 factors.F6.range 하한 {factor_min} 과 다름")


NET_CASH_STATUSES = ("working_definition", "confirmed")
# net_cash 적용 범위를 가르는 두 축. **서로를 함의하지 않는다** — 만기 3년 회사채는 즉시성이
# 없어도 시장성이 있고, 비상장 지분은 만기가 없어도 시장성이 없다.
NET_CASH_AXES = ("immediacy", "marketability")


def _validate_net_cash(spec: Any) -> None:
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
        _require(len(set(metrics)) >= 2,
                 f"{where}.scope_separation.sites: 서로 다른 지표 둘 이상을 가리켜야 함 — {metrics}")


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

def validate_observations(payload: Any, companies: dict[str, dict[str, Any]], run_id: str | None = None) -> list[dict[str, Any]]:
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
        _expect_keys(inputs, ["performance_leap", "paradigm_adaptation", "standard_capture", "top_rank"], where)
        for key in ("performance_leap", "paradigm_adaptation", "standard_capture"):
            _require(inputs[key] in TRI, f"{where}: {key} 는 {sorted(TRI)}")
        _require(inputs["top_rank"] in YES_NO, f"{where}: top_rank 오류")
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
            optional=["counter_evidence", "source_ids", "carried_from", "note", "previous_judgment_id"],
        )
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
                _require(not companies[item["company_id"]]["listed"], f"{where}: 상장사 F6 는 수동 score 불허 (NTM PER 자동 산출)")
            if factor in {"F2", "F7"}:
                _require(item["status"] == "carried", f"{where}: {factor} 의 수동 score 는 승계(carried) 판단에만 허용 — 신규는 paths/matrix 입력 필요")
        else:
            _require(score is None, f"{where}: kind {kind!r} 판단의 score 는 null (자동 산출)")
        _validate_judgment_inputs(kind, item["inputs"], f"{where}.inputs")
        items.append(item)
    return items


# ------------------------------------------------------------------ run / approval

def validate_run(payload: Any, slug: str | None = None) -> dict[str, Any]:
    _expect_keys(
        payload,
        ["schema", "run_id", "report_type", "title", "as_of", "rule_version", "baseline_id", "companies", "decisions", "created_at", "purpose", "assumptions"],
        "run.json",
        optional=["price_as_of", "info_cutoff", "reference_companies", "rule_hash", "note", "sources_file"],
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
    return payload


def validate_approval(payload: Any, run_id: str | None = None) -> dict[str, Any]:
    _expect_keys(payload, ["schema", "run_id", "approval_id", "approved_by", "approved_at", "hashes"], "approval.json", optional=["note"])
    _require(payload["schema"] == "scorecard.approval/1", "approval.json: schema 불일치")
    if run_id is not None:
        _require(payload["run_id"] == run_id, "approval.json: run_id 불일치")
    _require(isinstance(payload["approved_by"], str) and payload["approved_by"].strip(),
             f"approval.json: approved_by 는 비어 있지 않은 문자열이어야 함 ({payload['approved_by']!r})")
    _expect_date(payload["approved_at"], "approval.json.approved_at")
    _expect_keys(payload["hashes"], ["rules", "observations", "judgments", "run", "results", "draft"], "approval.hashes")
    return payload
