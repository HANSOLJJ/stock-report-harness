# SEC company_tickers.json으로 companies.json 기업의 CIK를 확인한다
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from report_contract_lib import ROOT

from . import evidence_lib
from .evidence_lib import fetch_bytes, sha256_bytes
from .engine import load_companies

COMPANY_TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"


def load_ticker_map(payload: dict[str, Any]) -> dict[str, int]:
    """SEC company_tickers 형식({ 일련: {cik_str, ticker, title} })을 대문자 티커 → cik으로."""
    mapping: dict[str, int] = {}
    for entry in payload.values():
        if isinstance(entry, dict) and entry.get("ticker") and entry.get("cik_str"):
            mapping[str(entry["ticker"]).upper()] = int(entry["cik_str"])
    return mapping


def resolve(companies: list[dict[str, Any]], ticker_map: dict[str, int]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for company in companies:
        ticker = company.get("ticker")
        if not company.get("listed") or not ticker:
            rows.append({"company_id": company["company_id"], "ticker": ticker,
                         "cik": None, "status": "unlisted"})
        elif str(ticker).upper() in ticker_map:
            rows.append({"company_id": company["company_id"], "ticker": ticker,
                         "cik": ticker_map[str(ticker).upper()], "status": "resolved"})
        else:
            rows.append({"company_id": company["company_id"], "ticker": ticker,
                         "cik": None, "status": "not_found"})
    return rows


def load_payload(*, from_file: str | Path | None) -> dict[str, Any]:
    if from_file is not None:
        return json.loads(Path(from_file).read_text(encoding="utf-8"))
    from .collect_filings import require_user_agent  # noqa: E402

    raw = fetch_bytes(COMPANY_TICKERS_URL, user_agent=require_user_agent())
    cache = evidence_lib.DATA_ROOT / "_sec" / "company_tickers.json"
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_bytes(raw)
    return json.loads(raw.decode("utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="티커 → SEC CIK 확인(읽기 전용, companies.json에 쓰지 않음)")
    parser.add_argument("--from-file", default=None, help="캐시나 픽스처 JSON 경로")
    parser.add_argument("--company", default=None, help="company_id 필터")
    parser.add_argument("--json", action="store_true", help="JSON 한 줄 출력")
    args = parser.parse_args(argv)

    companies = list(load_companies().values())
    if args.company:
        companies = [c for c in companies if c["company_id"] == args.company]
        if not companies:
            print(f"알 수 없는 company_id: {args.company}", file=sys.stderr)
            return 1
    rows = resolve(companies, load_ticker_map(load_payload(from_file=args.from_file)))
    if args.json:
        print(json.dumps(rows, ensure_ascii=False))
    else:
        for row in rows:
            print(f"{row['company_id']}\t{row['ticker']}\t{row['cik']}\t{row['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
