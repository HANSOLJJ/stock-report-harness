# 국면 탭의 시장 지표(금리·회사채 스프레드·GPU 임대료·토큰 단가)를 원천에서 받아 계산하고 기준일 관측으로 만든다(점수 밖)
"""2026-11-15 사용자 요청: 점수를 매긴 뒤 시장이 어떻게 움직였는지 리포트 국면 탭에서 본다.

- 실행의 collect(`--kind market`)가 이 모듈로 기준일 값을 관측(`_market`)으로 찍는다. 점수·순위에는 쓰지 않는다.
- 리포트의 "지금 값" 칸은 브라우저가 `assets/market_live.js` 로 같은 정의를 계산한다. 두 구현은 같은 고정 자료로
  같은 값을 내야 한다(tests/test_market_now.py · tests/node/market_live.test.js).
- 자료가 없으면 값을 만들지 않는다. 미확인을 0 으로 두지 않는다.
"""
from __future__ import annotations

import csv
import io
import json
import urllib.parse
from datetime import date, datetime, timedelta, timezone
from typing import Any, Callable

from .schema import MARKET_COMPANY_ID, MARKET_SNAPSHOT_METRICS

# (지표, FRED 계열, 이름). 단위는 모두 퍼센트(스프레드는 퍼센트포인트).
FRED_SERIES = (
    ("ust10y_yield", "DGS10", "미국채 10년물 금리"),
    ("ig_oas", "BAMLC0A0CM", "투자등급 회사채 스프레드"),
    ("hy_oas", "BAMLH0A0HYM2", "하이일드 회사채 스프레드"),
    ("baa_spread", "BAA10Y", "무디스 Baa 회사채 − 10년물 스프레드"),
)
FRED_LOOKBACK_DAYS = 30
GPU_TYPES = ("H100 SXM", "H200", "B200")
TOKEN_LABS = ("openai", "anthropic", "google", "x-ai", "deepseek", "qwen", "moonshotai")
TOKEN_WINDOW_DAYS = 180
SNAPSHOT_METRICS = frozenset(MARKET_SNAPSHOT_METRICS)
UNITS = {"ust10y_yield": "percent", "ig_oas": "percent", "hy_oas": "percent", "baa_spread": "percent",
         "gpu_rent_hourly": "USD/GPU-hour", "token_blended_price": "USD/1M tokens"}

OPENROUTER_URL = "https://openrouter.ai/api/v1/models"


def fred_csv_url(series: str, until: str) -> str:
    start = (date.fromisoformat(until) - timedelta(days=FRED_LOOKBACK_DAYS)).isoformat()
    return f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series}&cosd={start}&coed={until}"


def vast_url(gpu: str) -> str:
    q = {"gpu_name": {"eq": gpu}, "rentable": {"eq": True}, "type": "on-demand", "limit": 500}
    return "https://console.vast.ai/api/v0/bundles/?q=" + urllib.parse.quote(json.dumps(q))


def fred_latest(text: str, until: str) -> tuple[str, float] | None:
    """FRED CSV(observation_date,<계열>)에서 until 이하 가장 최근 값. 빈 칸과 "." 는 값이 없는 날이다."""
    best: tuple[str, float] | None = None
    for row in csv.reader(io.StringIO(text)):
        if len(row) < 2 or row[0] == "observation_date":
            continue
        day, raw = row[0].strip(), row[1].strip()
        if not raw or raw == "." or day > until:
            continue
        if best is None or day > best[0]:
            best = (day, float(raw))
    return best


def median(values: list[float]) -> float | None:
    if not values:
        return None
    xs = sorted(values)
    mid = len(xs) // 2
    return xs[mid] if len(xs) % 2 else (xs[mid - 1] + xs[mid]) / 2


def gpu_rent(offers: list[dict[str, Any]]) -> dict[str, Any] | None:
    """GPU 한 장 시간당 단가(dph_total ÷ num_gpus)의 GPU 수 가중 중간값. 호가가 없으면 None."""
    prices: list[float] = []
    count = 0
    for o in offers:
        n, dph = o.get("num_gpus"), o.get("dph_total")
        if not isinstance(n, int) or n <= 0 or not isinstance(dph, (int, float)):
            continue
        prices += [dph / n] * n
        count += 1
    value = median(prices)
    return None if value is None else {"value": value, "gpus": len(prices), "offers": count}


def _usd_per_m(raw: Any) -> float | None:
    try:
        v = float(raw)
    except (TypeError, ValueError):
        return None
    return v * 1e6 if v > 0 else None


def token_picks(models: list[dict[str, Any]], ref: str) -> list[dict[str, Any]]:
    """연구소마다 최근 TOKEN_WINDOW_DAYS 일 안에 나온 비배치 유료 텍스트 모델 가운데 혼합 단가(입력 3 : 출력 1)가 가장 높은 것.
    혼합 단가가 같으면 더 최근에 나온 모델, 그것도 같으면 이름이 앞선 모델이다."""
    floor = date.fromisoformat(ref) - timedelta(days=TOKEN_WINDOW_DAYS)
    best: dict[str, dict[str, Any]] = {}
    for m in models:
        mid = m.get("id") or ""
        lab = mid.split("/", 1)[0]
        if lab not in TOKEN_LABS or ":" in mid:
            continue
        if (m.get("architecture") or {}).get("output_modalities") != ["text"]:
            continue
        created = m.get("created")
        if not isinstance(created, (int, float)):
            continue
        made = datetime.fromtimestamp(created, tz=timezone.utc).date()
        if made < floor or made > date.fromisoformat(ref):
            continue
        pi, po = _usd_per_m((m.get("pricing") or {}).get("prompt")), _usd_per_m((m.get("pricing") or {}).get("completion"))
        if pi is None or po is None:
            continue
        blended = (3 * pi + po) / 4
        cur = best.get(lab)
        if (cur is None or blended > cur["blended"]
                or (blended == cur["blended"] and (created > cur["created"] or (created == cur["created"] and mid < cur["model"])))):
            best[lab] = {"lab": lab, "model": mid, "blended": blended, "created": created}
    return [{k: v for k, v in best[lab].items() if k != "created"} for lab in TOKEN_LABS if lab in best]


def _obs(metric: str, value: float | None, as_of: str, source_id: str, observed_at: str, basis: dict[str, Any],
         note: str | None = None) -> dict[str, Any]:
    suffix = f".{basis['gpu'].lower().replace(' ', '-')}" if "gpu" in basis else ""
    item: dict[str, Any] = {
        "observation_id": f"{MARKET_COMPANY_ID}.{metric}{suffix}.{as_of}", "company_id": MARKET_COMPANY_ID, "metric": metric,
        "value": value, "unit": UNITS[metric], "as_of": as_of, "observed_at": observed_at, "kind": "actual",
        "source_id": source_id, "status": "verified" if value is not None else "collection_failed", "basis": basis,
    }
    if note:
        item["note"] = note
    return item


def _source(source_id: str, title: str, publisher: str, url: str, accessed_at: str, note: str) -> dict[str, Any]:
    return {"source_id": source_id, "title": title, "publisher": publisher, "url": url, "accessed_at": accessed_at,
            "sha256": None, "conflict_of_interest": None, "note": note}


def snapshot(price_as_of: str, *, today: str, now: str, get: Callable[[str], bytes]) -> dict[str, Any]:
    """기준일 관측과 출처. FRED 는 가격 기준일 이하 최근 값이고, 과거를 다시 받을 수 없는 vast.ai·OpenRouter 는 받은 날(today) 값이다.
    원천 하나가 실패해도 나머지는 남기고 그 원천의 실패를 rows 에 적는다."""
    obs: list[dict[str, Any]] = []
    sources: list[dict[str, Any]] = []
    rows: list[dict[str, Any]] = []

    src = f"SRC-FRED-{price_as_of}"
    got = 0
    for metric, series, _name in FRED_SERIES:
        url = fred_csv_url(series, price_as_of)
        try:
            hit = fred_latest(get(url).decode("utf-8"), price_as_of)
        except Exception as exc:  # noqa: BLE001 — 원천 하나의 실패로 나머지를 멈추지 않는다
            rows.append({"metric": metric, "status": "failed", "error": str(exc)})
            continue
        if hit is None:
            rows.append({"metric": metric, "status": "failed", "error": f"{series}: {price_as_of} 이전 {FRED_LOOKBACK_DAYS}일에 값이 없다"})
            continue
        obs.append(_obs(metric, hit[1], hit[0], src, now[:10], {"series": series}))
        rows.append({"metric": metric, "status": "collected", "as_of": hit[0], "value": hit[1]})
        got += 1
    if got:
        sources.append(_source(src, f"FRED 금리·회사채 스프레드({price_as_of} 이하 최근 값)", "Federal Reserve Bank of St. Louis (FRED)",
                               fred_csv_url(FRED_SERIES[0][1], price_as_of), now,
                               "국면 탭 시장 지표 전용(점수 밖). 계열 " + ", ".join(s for _m, s, _n in FRED_SERIES)))

    src = f"SRC-VAST-{today}"
    got = 0
    for gpu in GPU_TYPES:
        try:
            offers = json.loads(get(vast_url(gpu)).decode("utf-8")).get("offers") or []
        except Exception as exc:  # noqa: BLE001
            rows.append({"metric": "gpu_rent_hourly", "gpu": gpu, "status": "failed", "error": str(exc)})
            continue
        rent = gpu_rent(offers)
        basis = {"gpu": gpu, "gpus": rent["gpus"] if rent else 0, "offers": rent["offers"] if rent else 0,
                 "method": "gpu_weighted_median_on_demand"}
        obs.append(_obs("gpu_rent_hourly", rent["value"] if rent else None, today, src, today, basis,
                        None if rent else f"{gpu} 대여 가능 호가가 없다"))
        rows.append({"metric": "gpu_rent_hourly", "gpu": gpu, "status": "collected" if rent else "empty",
                     "value": rent["value"] if rent else None})
        got += 1
    if got:
        sources.append(_source(src, f"vast.ai 대여 장터 on-demand 호가({today} 조회)", "Vast.ai", vast_url(GPU_TYPES[0]), now,
                               "국면 탭 시장 지표 전용(점수 밖). 공개 장터 호가라 표본이 얇다. GPU 종류 " + ", ".join(GPU_TYPES)))

    src = f"SRC-OPENROUTER-{today}"
    try:
        models = json.loads(get(OPENROUTER_URL).decode("utf-8")).get("data") or []
        picks = token_picks(models, today)
        value = median([p["blended"] for p in picks])
        obs.append(_obs("token_blended_price", value, today, src, today,
                        {"segment": "frontier", "labs": list(TOKEN_LABS), "window_days": TOKEN_WINDOW_DAYS,
                         "mix": "input3_output1", "picks": picks}))
        rows.append({"metric": "token_blended_price", "status": "collected" if value is not None else "empty", "value": value})
        sources.append(_source(src, f"OpenRouter 모델 가격 목록({today} 조회)", "OpenRouter", OPENROUTER_URL, now,
                               "국면 탭 시장 지표 전용(점수 밖). 공시 정가이고 실제 거래 단가가 아니다"))
    except Exception as exc:  # noqa: BLE001
        rows.append({"metric": "token_blended_price", "status": "failed", "error": str(exc)})
    return {"observations": obs, "sources": sources, "rows": rows}
