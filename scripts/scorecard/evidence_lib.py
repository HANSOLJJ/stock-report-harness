# 근거 수집 공용 라이브러리(fetch·상태·id·출처 항목)
from __future__ import annotations

import hashlib
import json
import os
import time
import urllib.request
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any

from report_contract_lib import ROOT

DATA_ROOT = Path(os.environ["SCORECARD_DATA_ROOT"]) if os.environ.get("SCORECARD_DATA_ROOT") else ROOT / "data"

TOOL_NAME = "stock-report-harness-scorecard"
GOOGLE_MAX_FETCH_PER_QUERY_PER_DAY = 4
SEC_SLEEP_S = 1.0


def user_agent_for(kind: str) -> str:
    """SEC 조회는 SEC_UA 값을 그대로, 그 밖은 식별 UA를 돌려준다."""
    sec_ua = os.environ.get("SEC_UA", "").strip()
    if kind == "sec":
        return sec_ua
    contact = sec_ua if sec_ua else "contact unset"
    return f"{TOOL_NAME}/0.1 ({contact})"


def fetch_bytes(url: str, *, user_agent: str, timeout: int = 20, retries: int = 2) -> bytes:
    """저장소에서 유일한 urllib 사용 지점. 실패는 예외로 올리고 빈 바이트를 돌려주지 않는다."""
    last: Exception | None = None
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": user_agent})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                body = resp.read()
            if not body:
                raise ValueError(f"빈 응답: {url}")
            return body
        except Exception as exc:  # noqa: BLE001 — 재시도 뒤 마지막 예외를 그대로 올린다
            last = exc
            if attempt < retries:
                time.sleep(1)
    raise last  # type: ignore[misc]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_rfc2822(text: str) -> str | None:
    """RFC 2822 날짜를 UTC ISO 8601(YYYY-MM-DDTHH:MM:SSZ)로. 파싱 실패는 None."""
    try:
        dt = parsedate_to_datetime(text)
    except (TypeError, ValueError):
        return None
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_state(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {"runs": [], "counts": {}}
    return json.loads(path.read_text(encoding="utf-8"))


def save_state(path: Path, state: dict[str, Any], keep_runs: int = 20) -> Path:
    state = dict(state)
    state["runs"] = list(state.get("runs") or [])[-keep_runs:]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    return path


_STAMP_KEYS = ("first_seen_utc", "updated_utc")


def _content_equal(old: dict[str, Any], new: dict[str, Any]) -> bool:
    strip = lambda d: {k: v for k, v in d.items() if k not in _STAMP_KEYS}  # noqa: E731
    return strip(old) == strip(new)


def merge_items(existing: list[dict[str, Any]], incoming: list[dict[str, Any]], key: str) -> list[dict[str, Any]]:
    """key 기준 upsert. first_seen_utc 보존, 내용 변경 시 updated_utc 갱신, key 정렬."""
    merged: dict[Any, dict[str, Any]] = {item[key]: dict(item) for item in existing}
    for item in incoming:
        k = item[key]
        if k in merged and _content_equal(merged[k], item):
            continue
        entry = dict(item)
        if k in merged:
            entry["first_seen_utc"] = merged[k].get("first_seen_utc", entry.get("first_seen_utc"))
            entry["updated_utc"] = utc_now_iso()
        else:
            entry.setdefault("first_seen_utc", utc_now_iso())
        merged[k] = entry
    return [merged[k] for k in sorted(merged)]


def source_id_for_article(
    company_id: str, published_at_utc: str | None, content_hash: str, *, first_seen_utc: str | None = None
) -> str:
    stamp = published_at_utc or first_seen_utc or utc_now_iso()
    return f"SRC-NEWS-{company_id}-{stamp[:10].replace('-', '')}-{content_hash[:8]}"


def source_id_for_filing(accession_nodash: str) -> str:
    return f"SRC-EDGAR-{accession_nodash}"


def source_entry(item: dict[str, Any], *, kind: str, raw_sha256: str, accessed_at: str) -> dict[str, Any]:
    """sources.json 항목. 필수 8키 + kind·company_id·published_at_utc·publisher_url·raw_ref(있을 때)."""
    entry: dict[str, Any] = {
        "source_id": item["source_id"],
        "title": item["title"],
        "publisher": item["publisher"],
        "url": item["url"],
        "accessed_at": accessed_at,
        "sha256": raw_sha256,
        "conflict_of_interest": None,
        "note": item.get("note", ""),
    }
    entry["kind"] = kind
    for opt in ("company_id", "published_at_utc", "publisher_url", "raw_ref"):
        if item.get(opt) is not None:
            entry[opt] = item[opt]
    return entry


def upsert_sources(sources_payload: dict[str, Any], entries: list[dict[str, Any]]) -> dict[str, Any]:
    """추가만 한다. 같은 source_id가 있으면 기존 항목을 바꾸지 않는다."""
    seen = {item["source_id"] for item in sources_payload.get("items", [])}
    for entry in entries:
        if entry["source_id"] not in seen:
            sources_payload.setdefault("items", []).append(entry)
            seen.add(entry["source_id"])
    return sources_payload
