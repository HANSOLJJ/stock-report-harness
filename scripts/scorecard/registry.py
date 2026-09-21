# 채점 대상 기업 레지스트리(scorecard/companies.json)에 기업을 **추가만** 하는 편집기
"""2026-09-21 ADD-01. 레지스트리는 **한 줄 = 한 기업** 형식이고 14줄 전부가 `render_company_line` 으로
바이트 재현된다. `schema.write_json` 은 `indent=2` 라 그것으로 다시 쓰면 14개 기업이 모두 여러 줄로
펼쳐져 `git diff` 가 **`추가만 했다`** 를 증명하지 못한다. 그래서 텍스트 삽입으로 더한다.

검증은 새로 쓰지 않는다 — 중복 `company_id`·ID 정규식·`type`·`share_basis`·`adr_ratio`·알 수 없는 키는
전부 `schema.validate_companies` 가 잡는다. 이 파일은 **형식 보존과 사후 확인**만 맡는다.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .engine import COMPANIES_PATH
from .schema import SchemaError, load_json_strict, resolve_company_id, validate_companies


def render_company_line(item: dict[str, Any]) -> str:
    """레지스트리의 한 줄 형식. 현재 14줄이 이 함수로 바이트 재현된다(테스트가 잠근다)."""
    return "    " + json.dumps(item, ensure_ascii=False)


def _validate_or_raise(payload: Any, where: str) -> dict[str, dict[str, Any]]:
    try:
        return validate_companies(payload)
    except SchemaError as exc:
        raise SchemaError(f"{where}: {exc}") from exc


def find_name_conflict(item: dict[str, Any], companies: dict[str, dict[str, Any]]) -> str | None:
    """표시명·별칭이 기존 기업과 겹치는지 본다.

    스키마는 `company_id` 중복만 본다. 그런데 `schema.resolve_company_id` 가 `display_name`·`aliases` 를
    조회 키로 쓰므로 겹치면 이름 해석이 **조용히** 엉킨다.
    """
    for name in [item["display_name"], *item.get("aliases", [])]:
        hit = resolve_company_id(name, companies)
        if hit is not None and hit != item["company_id"]:
            return f"{name!r} 는 이미 {hit!r} 의 표시명·별칭이다"
    return None


def plan_company_line(item: dict[str, Any], *, path: Path = COMPANIES_PATH) -> dict[str, Any]:
    """삽입될 줄과 위치를 계산한다. 파일은 쓰지 않는다(`--dry-run` 이 이것만 쓴다)."""
    original = path.read_text(encoding="utf-8")
    payload = load_json_strict(path)
    before = _validate_or_raise(payload, "추가 전 companies.json 이 이미 계약을 어긴다")
    conflict = find_name_conflict(item, before)
    if conflict:
        raise SchemaError(f"표시명·별칭 충돌 — {conflict}")

    merged = dict(payload)
    merged["companies"] = [*payload["companies"], item]
    after = _validate_or_raise(merged, "추가 뒤 companies.json 이 계약을 어긴다")

    anchor = render_company_line(payload["companies"][-1])
    lines = original.split("\n")
    hits = [i for i, line in enumerate(lines) if line == anchor]
    if len(hits) != 1:
        raise SchemaError("companies.json 이 이 명령이 쓰는 형식과 다르게 손으로 편집돼 있다 — 사람이 먼저 정리한다")
    return {"company_id": item["company_id"], "line_no": hits[0] + 2, "anchor_index": hits[0],
            "line": render_company_line(item), "count_before": len(before), "count_after": len(after),
            "original": original, "lines": lines}


def add_company(item: dict[str, Any], *, path: Path = COMPANIES_PATH) -> dict[str, Any]:
    """기업 한 줄을 레지스트리 끝에 더한다. 기존 줄은 앞 항목의 쉼표 하나 말고는 바뀌지 않는다."""
    plan = plan_company_line(item, path=path)
    lines = list(plan["lines"])
    idx = plan["anchor_index"]
    lines[idx] = lines[idx] + ","
    lines.insert(idx + 1, plan["line"])
    path.write_text("\n".join(lines), encoding="utf-8", newline="\n")

    # 사후 검증 — 하나라도 어기면 원문을 되돌려 쓴다.
    try:
        _validate_or_raise(load_json_strict(path), "쓴 뒤 companies.json 이 계약을 어긴다")
        written = path.read_text(encoding="utf-8").split("\n")
        if written[:idx] != plan["lines"][:idx]:
            raise SchemaError("삽입 지점 앞 줄이 바뀌었다 — 이 명령은 추가만 한다")
        if written[idx] != plan["lines"][idx] + "," or written[idx + 1] != plan["line"]:
            raise SchemaError("삽입한 줄이 계획과 다르다")
    except SchemaError:
        path.write_text(plan["original"], encoding="utf-8", newline="\n")
        raise
    return {"company_id": plan["company_id"], "line_no": plan["line_no"],
            "count_before": plan["count_before"], "count_after": plan["count_after"]}
