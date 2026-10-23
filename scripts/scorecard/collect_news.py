# Google News RSS 수집기(기사 메타데이터만, 본문 조회 없음)와 중계 주소를 원문 주소로 푸는 도우미
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


# 2026-10-12 사용자 지시: RSS 의 기사 링크는 Google News 중계 주소라 그대로 열면 원문으로 넘어가지 않는다. 그래서 10월 재실행에
# 발췌가 제목뿐인 확정 근거 29건이 남았고, 판단은 "제목만 확인"이라며 미확인으로 돌렸다. 근거로 올리는 기사는 원문 주소로 바꾼다.
# 방식: 기사 페이지의 서명(data-n-a-sg)·시각(data-n-a-ts)으로 batchexecute 의 Fbv4je 요청을 보내면 원문 URL 이 돌아온다.
GOOGLE_RELAY_RE = re.compile(r"^https?://news\.google\.com/(?:rss/)?articles/([^?/#]+)")
GOOGLE_BATCH_URL = "https://news.google.com/_/DotsSplashUi/data/batchexecute"


def is_google_relay_url(url: str | None) -> bool:
    return bool(GOOGLE_RELAY_RE.match(url or ""))


# 2026-10-23 사용자 결정: 스크립트 요청이 자주 막히는 매체는 처음부터 앱 안 브라우저로 연다(재시도를 줄인다). 그 밖의 매체는
# 스크립트 먼저, 403 이면 브라우저다(AGENTS.md 「원자료 조사 규율」). 브라우저에서도 봇 확인 화면이면 우회하지 않는다.
# q3a 실행에서 403·429 를 낸 매체 가운데 브라우저로는 열린 곳만 넣는다. 유료 벽(WSJ·FT·Bloomberg)은 브라우저로도 본문이 없어 넣지 않는다.
BROWSER_FIRST_HOSTS = ("yahoo.com", "reuters.com", "apnews.com", "benzinga.com", "seekingalpha.com", "axios.com", "stocktwits.com")


def browser_first(url: str | None) -> bool:
    """원문 주소의 매체가 브라우저 우선 목록에 있는가(서브도메인 포함)."""
    host = (urllib.parse.urlparse(url or "").hostname or "").lower()
    return any(host == h or host.endswith("." + h) for h in BROWSER_FIRST_HOSTS)


def resolve_google_news_url(url: str, *, fetch: Callable[..., bytes] = fetch_bytes, user_agent: str | None = None) -> str:
    """Google News 중계 주소를 원문 URL 로 푼다. 풀지 못하면 ValueError(중계 주소를 원문처럼 돌려주지 않는다)."""
    m = GOOGLE_RELAY_RE.match(url or "")
    if not m:
        raise ValueError(f"Google News 중계 주소가 아니다: {url}")
    aid = m.group(1)
    ua = user_agent if user_agent is not None else evidence_lib.user_agent_for("news")
    page = fetch(f"https://news.google.com/rss/articles/{aid}", user_agent=ua).decode("utf-8", "replace")
    sig = re.search(r'data-n-a-sg="([^"]+)"', page)
    ts = re.search(r'data-n-a-ts="(\d+)"', page)
    if not sig or not ts:
        raise ValueError(f"기사 페이지에 서명·시각이 없다: {url}")
    inner = ('["garturlreq",[["X","X",["X","X"],null,null,1,1,"US:en",null,1,null,null,null,null,null,0,1],'
             f'"X","X",1,[1,1,1],1,1,null,0,0,null,0],"{aid}",{ts.group(1)},"{sig.group(1)}"]')
    body = urllib.parse.urlencode({"f.req": json.dumps([[["Fbv4je", inner, None, "generic"]]])}).encode()
    raw = fetch(GOOGLE_BATCH_URL, user_agent=ua, data=body,
                headers={"Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"}).decode("utf-8", "replace")
    try:
        payload = json.loads(raw.split("\n\n", 1)[1])
        original = json.loads(payload[0][2])[1]
    except (IndexError, TypeError, ValueError) as exc:
        raise ValueError(f"원문 URL 응답을 읽지 못했다: {url}") from exc
    if not isinstance(original, str) or not original.startswith(("https://", "http://")) or is_google_relay_url(original):
        raise ValueError(f"원문 URL 이 아니다: {original!r}")
    return original


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
    # 파일에서 읽을 때는 요청이 없으므로 UA(와 그 SEC_UA 검사)를 거치지 않는다(2026-10-01 레인 J).
    user_agent = evidence_lib.user_agent_for("news") if from_file is None else ""
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
    merged = merge_items(existing, articles, "article_id", now=fetched_at)
    norm_path.write_text(json.dumps({"items": merged}, ensure_ascii=False, indent=2) + "\n",
                         encoding="utf-8", newline="\n")
    state.setdefault("runs", []).append(
        {"at": fetched_at, "kind": "news", "fetched": result["fetched"],
         "skipped_rate_limit": result["skipped_rate_limit"], "articles": len(articles)})
    save_state(state_path, state)
    result["normalized_path"] = str(norm_path)
    result["state_path"] = str(state_path)
    return result
