# Google News RSS 수집기(기사 메타데이터만, 본문 조회 없음)
from __future__ import annotations

import hashlib
import html
import json
import re
import urllib.parse
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Callable

from . import evidence_lib
from .evidence_lib import (
    fetch_bytes,
    load_state,
    merge_items,
    parse_rfc2822,
    save_state,
    sha256_bytes,
    source_id_for_article,
    utc_now_iso,
)

TAG_RE = re.compile(r"<[^>]+>")


# 하이픈 없이 언어만 준 locale 의 기본 국가(Google 의 gl 은 국가 코드를 기대한다)
LANG_DEFAULT_REGION = {"en": "US", "ko": "KR", "ja": "JP", "zh": "CN", "de": "DE", "fr": "FR"}


def split_locale(locale: str) -> tuple[str, str]:
    lang, _, region = locale.partition("-")
    if not region:
        region = LANG_DEFAULT_REGION.get(lang, "")
    if not lang or not region:
        raise ValueError("locale 은 xx-YY 형식으로 준다")
    return lang, region


def build_query_url(query: str, *, hl: str = "en-US", gl: str = "US", ceid: str = "US:en") -> str:
    params = urllib.parse.urlencode({"q": query, "hl": hl, "gl": gl, "ceid": ceid})
    return f"https://news.google.com/rss/search?{params}"


def _text(elem: Any) -> str:
    return (elem.text or "").strip() if elem is not None else ""


def parse_rss(xml_bytes: bytes) -> list[dict[str, Any]]:
    """item의 title·link·guid·pubDate·description·source(텍스트와 url 속성)를 뽑는다."""
    root = ET.fromstring(xml_bytes)
    items: list[dict[str, Any]] = []
    for node in root.iter("item"):
        source = node.find("source")
        items.append({
            "title": _text(node.find("title")),
            "link": _text(node.find("link")),
            "guid": _text(node.find("guid")),
            "pubDate": _text(node.find("pubDate")),
            "description": _text(node.find("description")),
            "source_name": _text(source),
            "source_url": (source.get("url") or "").strip() if source is not None else "",
        })
    return items


def strip_html(text: str) -> str:
    return re.sub(r"\s+", " ", TAG_RE.sub("", html.unescape(text or ""))).strip()


def normalize_article(
    raw_item: dict[str, Any], *, company_id: str, query: str, fetched_at: str, raw_ref: str
) -> dict[str, Any]:
    guid = raw_item.get("guid") or raw_item.get("link", "")
    summary = strip_html(raw_item.get("description", ""))
    source_url = raw_item.get("source_url", "")
    content_hash = hashlib.sha256(
        f"{raw_item.get('title', '')}\n{summary}\n{source_url}".encode("utf-8")
    ).hexdigest()
    published_at_utc = parse_rfc2822(raw_item.get("pubDate", "")) if raw_item.get("pubDate") else None
    article: dict[str, Any] = {
        "article_id": "google:" + guid,
        "provider": "google_news_rss",
        "company_id": company_id,
        "query": query,
        "title": raw_item.get("title", ""),
        "summary": summary,
        "source": {"name": raw_item.get("source_name", ""), "url": source_url},
        "published_at_utc": published_at_utc,
        "first_seen_utc": fetched_at,
        "updated_utc": None,
        "url": raw_item.get("link", ""),
        "url_kind": "google_redirect",
        "url_is_fallback": False,
        "content_hash": content_hash,
        "raw_ref": raw_ref,
        "source_id": source_id_for_article(company_id, published_at_utc, content_hash, first_seen_utc=fetched_at),
    }
    if published_at_utc is None:
        article["unverified"] = ["published_at"]
        article["note"] = "published_at 미확인, first_seen 날짜로 source_id 생성"
    return article


def default_queries(company: dict[str, Any]) -> list[str]:
    queries = list(company.get("news_queries") or [])
    if not queries:
        if company.get("display_name"):
            queries.append(str(company["display_name"]))
        if company.get("ticker"):
            queries.append(str(company["ticker"]))
    return queries


def collect_company_news(
    company: dict[str, Any],
    *,
    fetch: Callable[..., bytes] = fetch_bytes,
    from_file: str | Path | None = None,
    dry_run: bool = False,
    now: str | None = None,
    locale: str = "en-US",
) -> dict[str, Any]:
    company_id = company["company_id"]
    queries = default_queries(company)
    # 2026-09-30 레인 E: `collect --locale` 연결. `en-US` → hl=en-US, gl=US, ceid=US:en.
    lang, region = split_locale(locale)
    urls = [build_query_url(q, hl=locale, gl=region, ceid=f"{region}:{lang}") for q in queries]
    fetched_at = now or utc_now_iso()
    if dry_run:
        return {"company_id": company_id, "dry_run": True, "queries": queries, "urls": urls}
    base = evidence_lib.DATA_ROOT / company_id / "news" / "google"
    state_path = base / "state.json"
    state = load_state(state_path)
    day = fetched_at[:10]
    counts = state.setdefault("counts", {}).setdefault(day, {})

    result: dict[str, Any] = {
        "company_id": company_id, "queries": queries, "urls": urls,
        "fetched": [], "skipped_rate_limit": [], "raw_files": [],
    }
    articles: list[dict[str, Any]] = []
    user_agent = evidence_lib.user_agent_for("news")
    for query, url in zip(queries, urls):
        if counts.get(query, 0) >= evidence_lib.GOOGLE_MAX_FETCH_PER_QUERY_PER_DAY:
            result["skipped_rate_limit"].append(query)
            continue
        if from_file is not None:
            raw = Path(from_file).read_bytes()
        else:
            raw = fetch(url, user_agent=user_agent)
            counts[query] = counts.get(query, 0) + 1
        stamp = fetched_at.replace(":", "").replace("-", "")
        raw_name = f"{stamp}-{sha256_bytes(raw)[:8]}.xml"
        raw_path = base / "raw" / raw_name
        raw_path.parent.mkdir(parents=True, exist_ok=True)
        raw_path.write_bytes(raw)
        result["raw_files"].append(str(raw_path))
        raw_ref = f"data/{company_id}/news/google/raw/{raw_name}"
        for raw_item in parse_rss(raw):
            articles.append(normalize_article(
                raw_item, company_id=company_id, query=query, fetched_at=fetched_at, raw_ref=raw_ref))
        result["fetched"].append(query)

    norm_path = base / "normalized.json"
    existing: list[dict[str, Any]] = []
    if norm_path.is_file():
        existing = json.loads(norm_path.read_text(encoding="utf-8")).get("items", [])
    merged = merge_items(existing, articles, "article_id")
    norm_path.write_text(json.dumps({"items": merged}, ensure_ascii=False, indent=2) + "\n",
                         encoding="utf-8", newline="\n")
    state.setdefault("runs", []).append(
        {"at": fetched_at, "kind": "news", "fetched": result["fetched"],
         "skipped_rate_limit": result["skipped_rate_limit"], "articles": len(articles)})
    save_state(state_path, state)
    result["normalized_path"] = str(norm_path)
    result["state_path"] = str(state_path)
    return result
