# SEC EDGAR submissions 수집기(SEC_UA 필수, 조회 사이 대기)
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Callable

from . import evidence_lib
from .evidence_lib import (
    fetch_bytes,
    load_state,
    merge_items,
    save_state,
    sha256_bytes,
    source_id_for_filing,
    utc_now_iso,
)

SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik:010d}.json"
DEFAULT_FORMS = {"8-K", "10-Q", "10-K", "20-F", "6-K"}
ARCHIVE_BASE = "https://www.sec.gov/Archives/edgar/data/{cik}/{accession_nodash}/{primary_document}"


def require_user_agent() -> str:
    sec_ua = evidence_lib.sec_user_agent()
    if not sec_ua:
        raise RuntimeError("SEC_UA 가 필요하다 — 저장소 루트 .env 에 `SEC_UA=이름 이메일` 을 적거나 환경변수로 설정한다")
    return sec_ua


def parse_submissions(
    payload: dict[str, Any], *, forms: set[str] = DEFAULT_FORMS, since: str | None = None
) -> list[dict[str, Any]]:
    """filings.recent 병렬 배열을 행으로 묶고 form·since로 거른다."""
    recent = (payload.get("filings") or {}).get("recent") or {}
    keys = ("accessionNumber", "filingDate", "reportDate", "form", "primaryDocument", "items")
    cols = [recent.get(k) or [] for k in keys]
    rows: list[dict[str, Any]] = []
    for values in zip(*cols):
        row = dict(zip(keys, values))
        if row["form"] not in forms:
            continue
        if since is not None and (row.get("filingDate") or "") < since:
            continue
        rows.append(row)
    return rows


def normalize_filing(row: dict[str, Any], *, company_id: str, cik: int, raw_ref: str) -> dict[str, Any]:
    accession = row.get("accessionNumber", "")
    accession_nodash = accession.replace("-", "")
    primary_document = row.get("primaryDocument", "")
    items_raw = (row.get("items") or "").strip()
    return {
        "filing_id": "edgar:" + accession_nodash,
        "company_id": company_id,
        "cik": cik,
        "form": row.get("form", ""),
        "filed_at": row.get("filingDate", ""),
        "report_period": row.get("reportDate") or None,
        "accession": accession,
        "primary_document": primary_document,
        "primary_doc_url": ARCHIVE_BASE.format(
            cik=cik, accession_nodash=accession_nodash, primary_document=primary_document),
        "items": [part.strip() for part in items_raw.split(",") if part.strip()],
        "first_seen_utc": utc_now_iso(),
        "raw_ref": raw_ref,
        "source_id": source_id_for_filing(accession_nodash),
    }


def collect_company_filings(
    company: dict[str, Any],
    *,
    fetch: Callable[..., bytes] = fetch_bytes,
    from_file: str | Path | None = None,
    dry_run: bool = False,
    since: str | None = None,
    forms: set[str] = DEFAULT_FORMS,
    sleep: Callable[[float], None] = time.sleep,
    now: str | None = None,
) -> dict[str, Any]:
    company_id = company["company_id"]
    cik = company.get("cik")
    if not cik:
        return {"company_id": company_id, "skipped_no_cik": True}
    cik = int(cik)
    url = SUBMISSIONS_URL.format(cik=cik)
    fetched_at = now or utc_now_iso()
    if dry_run:
        return {"company_id": company_id, "dry_run": True, "cik": cik, "urls": [url]}
    base = evidence_lib.DATA_ROOT / company_id / "filings"
    state_path = base / "state.json"
    state = load_state(state_path)

    if from_file is not None:
        raw = Path(from_file).read_bytes()
    else:
        sleep(evidence_lib.SEC_SLEEP_S)
        raw = fetch(url, user_agent=require_user_agent())
    raw_name = f"CIK{cik:010d}-{sha256_bytes(raw)[:8]}.json"
    raw_path = base / "raw" / raw_name
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    raw_path.write_bytes(raw)
    raw_ref = f"data/{company_id}/filings/raw/{raw_name}"

    payload = json.loads(raw.decode("utf-8"))
    rows = parse_submissions(payload, forms=forms, since=since)
    filings = [normalize_filing(row, company_id=company_id, cik=cik, raw_ref=raw_ref) for row in rows]
    index_path = base / "index.json"
    existing: list[dict[str, Any]] = []
    if index_path.is_file():
        existing = json.loads(index_path.read_text(encoding="utf-8")).get("items", [])
    merged = merge_items(existing, filings, "filing_id")
    index_path.write_text(json.dumps({"items": merged}, ensure_ascii=False, indent=2) + "\n",
                          encoding="utf-8", newline="\n")
    state.setdefault("runs", []).append(
        {"at": fetched_at, "kind": "filings", "cik": cik, "filings": len(filings)})
    save_state(state_path, state)
    return {"company_id": company_id, "cik": cik, "urls": [url],
            "raw_files": [str(raw_path)], "filings": len(filings),
            "index_path": str(index_path), "state_path": str(state_path)}
