# 원천별 수집 결과를 기업x분기x지표x원천 관측으로 정규화하고 검증 항목을 채점 없이 기록한다.
import datetime as dt
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REF_DATE = "2026-09-09"

# scarpper qwen-ntm-data-03 (2026-09-08 조회) 의 Yahoo 관측을 재사용한다. 재수집하지 않고 원문 그대로 인용한다.
YAHOO_2026_09_08 = {
    "meta": (["Sep 2026", "Dec 2026"], ["6.53", "8.22"]),
    "nvidia": (["Oct 2026", "Jan 2027"], ["2.47", "2.75"]),
    "alphabet": (["Sep 2026", "Dec 2026"], ["3.01", "3.33"]),
    "microsoft": (["Sep 2026", "Dec 2026"], ["4.72", "4.83"]),
    "amazon": (["Sep 2026", "Dec 2026"], ["1.95", "2.44"]),
    "apple": (["Sep 2026", "Dec 2026"], ["1.98", "2.91"]),
    "oracle": (["Aug 2026", "Nov 2026"], ["1.74", "1.89"]),
    "palantir": (["Sep 2026", "Dec 2026"], ["0.41", "0.46"]),
    "tesla": (["Sep 2026", "Dec 2026"], ["0.45", "0.49"]),
    "spacex-xai": (["Sep 2026", "Dec 2026"], ["0.14", "0.44"]),
}
YAHOO_SRC = ("scarpper/validation/qwen-ntm-data-03/evidence.json "
             "(yahoo_fetched_at_utc 2026-09-08, 무료 2개 분기)")

MONTHS = {m: i + 1 for i, m in enumerate(
    ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])}

PRO = "[PRO]"


def month_key(label):
    """'Oct 2026' -> (2026, 10). 공급사 월 라벨을 정렬·대조용 키로만 쓴다."""
    try:
        mon, yr = label.split()
        return (int(yr), MONTHS[mon[:3]])
    except Exception:
        return None


def date_key(iso):
    try:
        d = dt.date.fromisoformat(iso)
        return (d.year, d.month)
    except Exception:
        return None


def at(seq, idx):
    if isinstance(seq, list) and 0 <= idx < len(seq):
        return seq[idx]
    return None


def main():
    raw = json.load(io.open(os.path.join(HERE, "collect-raw.json"), encoding="utf-8"))
    extra = json.load(io.open(os.path.join(HERE, "collect-extra.json"), encoding="utf-8"))

    out = {
        "task": "NTM-SOURCE-04",
        "reference_date": REF_DATE,
        "generated_at_utc": raw["generated_at_utc"],
        "method_doc": "설계진행/validation/consensus-research-method.md",
        "observation_unit": "기업 x 회계분기 x 지표 x 원천 x 추정 시점",
        "rules_applied": [
            "원천별 묶음을 분리 보존한다. 서로 다른 공급사의 분기를 이어 붙이지 않는다.",
            "평균과 중간값을 바꾸어 부르지 않는다. 중간값 미제공은 보조 정보 결측으로 기록한다.",
            "최소/최대는 관측된 전망 범위이며 확률 구간이 아니다.",
            "현재 자료를 2026-09-02 기준선에 소급 적용하지 않는다.",
            "EPS 평균에 전망치 수를 재가중해 분기간 합산하지 않는다.",
            "조회 시각은 공급사 추정치 갱신 시각의 증명이 아니다.",
        ],
        "companies": [],
    }

    for c in raw["companies"]:
        cid = c["company_id"]
        ex = extra["companies"].get(cid, {})
        rec = {"company_id": cid, "ticker": c["ticker"]}

        # --- 상장 여부 / 종목 정체성 ---
        info = (c["nasdaq"].get("info") or {})
        rec["listing"] = {
            "company_name_per_vendor": info.get("companyName"),
            "stock_type": info.get("stockType"),
            "exchange": info.get("exchange"),
            "is_nasdaq_listed": info.get("isNasdaqListed"),
            "last_trade_timestamp": (info.get("primaryData") or {}).get("lastTradeTimestamp"),
            "last_sale_price": (info.get("primaryData") or {}).get("lastSalePrice"),
            "source_url": c["nasdaq"]["urls"].get("info"),
            "fetched_at_utc": c["nasdaq"]["fetched_at_utc"].get("info"),
        }

        # --- 발표/미발표 경계 ---
        eps_data = ((ex.get("nasdaq_eps") or {}).get("data") or {}).get("earningsPerShare") or []
        prev = [x for x in eps_data if x.get("type") == "PreviousQuarter"]
        upc = [x for x in eps_data if x.get("type") == "UpcomingQuarter"]
        sa_q = c["stockanalysis"].get("quarterly") or {}
        sa_dates = sa_q.get("dates") or []
        sa_last = sa_q.get("lastDate")
        sa_last_reported = at(sa_dates, sa_last) if isinstance(sa_last, int) else None
        sa_next4 = sa_dates[sa_last + 1: sa_last + 5] if isinstance(sa_last, int) else []

        rec["reported_boundary"] = {
            "last_reported_quarter_vendor_label": prev[-1]["period"] if prev else None,
            "last_reported_actual_eps": prev[-1]["earnings"] if prev else None,
            "last_reported_consensus_at_report": prev[-1]["consensus"] if prev else None,
            "nasdaq_eps_endpoint": (ex.get("nasdaq_eps") or {}).get("url"),
            "nasdaq_eps_fetched_at_utc": (ex.get("nasdaq_eps") or {}).get("fetched_at_utc"),
            "stockanalysis_last_reported_period_end": sa_last_reported,
            "stockanalysis_next4_period_end": sa_next4,
            "note": "공급사가 표시한 발표/미발표 구분이다. 회사 공식 발표일과 별도 대조 대상이다.",
        }

        # --- 다음 4개 미발표 회계분기 (Nasdaq 원천 단독 묶음) ---
        fc = ((c["nasdaq"].get("earnings_forecast") or {}).get("quarterlyForecast") or {})
        rows = fc.get("rows") or []
        upc_labels = [x["period"] for x in upc]
        n4 = [r for r in rows if r["fiscalEnd"] in upc_labels][:4]
        obs = []
        for i, r in enumerate(n4):
            obs.append({
                "seq": i + 1,
                "period_label_vendor": r["fiscalEnd"],
                "period_end_stockanalysis": at(sa_next4, i),
                "metric": "EPS",
                "mean": r["consensusEPSForecast"],
                "median": None,
                "min": r["lowEPSForecast"],
                "max": r["highEPSForecast"],
                "estimate_count": r["noOfEstimates"],
                "revisions_up_4w": r.get("up"),
                "revisions_down_4w": r.get("down"),
            })
        means = [o["mean"] for o in obs if isinstance(o["mean"], (int, float))]

        rec["sources"] = {}
        rec["sources"]["nasdaq_api"] = {
            "vendor": "Nasdaq (api.nasdaq.com) — 분기 추정치가 Zacks 공개 표와 일치함을 NVDA 로 확인",
            "url_forecast": c["nasdaq"]["urls"].get("earnings_forecast"),
            "url_eps": (ex.get("nasdaq_eps") or {}).get("url"),
            "access": "공개 (로그인·구독 불필요, JSON GET)",
            "fetched_at_utc": c["nasdaq"]["fetched_at_utc"].get("earnings_forecast"),
            "vendor_asof": fc.get("asOf"),
            "vendor_asof_note": "asOf 필드가 null 이다. 공급사 추정치 갱신 시각 미확인.",
            "header_labels": fc.get("headers"),
            "currency": "공급사 미표기. 미국 상장 종목이나 통화 필드가 null 이므로 미확인으로 둔다.",
            "share_basis": "미확인 — 공급사가 희석/기본 주식 기준을 명시하지 않음",
            "accounting_basis": "미확인 — 머리글 'Consensus EPS* Forecast' 의 별표 정의를 공개 경로에서 찾지 못함",
            "quarters_obtained": len(obs),
            "observations": obs,
            "mean_sum_4q": round(sum(means), 4) if len(means) == 4 else None,
            "mean_sum_note": "같은 원천 4분기 평균의 단순 합이다. 기준 검증 전이므로 계산 후보이며 채점 입력이 아니다.",
            "extra_quarters_beyond_4": [
                {"period_label_vendor": r["fiscalEnd"], "mean": r["consensusEPSForecast"],
                 "min": r["lowEPSForecast"], "max": r["highEPSForecast"],
                 "estimate_count": r["noOfEstimates"]}
                for r in rows if r["fiscalEnd"] not in upc_labels],
            "annual_rows": ((c["nasdaq"].get("earnings_forecast") or {}).get("yearlyForecast") or {}).get("rows"),
        }

        # --- StockAnalysis 묶음 (무료는 2분기) ---
        sa_obs = []
        if isinstance(sa_last, int):
            for i in range(1, 5):
                idx = sa_last + i
                if idx >= len(sa_dates):
                    break
                v = at(sa_q.get("adjustedEps"), idx)
                g = at(sa_q.get("eps"), idx)
                a = at(sa_q.get("analysts"), idx)
                sa_obs.append({
                    "seq": i,
                    "period_end_vendor": sa_dates[idx],
                    "fiscal_quarter": at(sa_q.get("fiscalQuarter"), idx),
                    "adjusted_eps_mean": v,
                    "eps_mean": g,
                    "estimate_count": a,
                    "paywalled": (v == PRO),
                })
        got = [o for o in sa_obs if isinstance(o["adjusted_eps_mean"], (int, float))]
        rec["sources"]["stockanalysis"] = {
            "vendor": "StockAnalysis.com",
            "url": c["stockanalysis"].get("page_url"),
            "url_data": (c["stockanalysis"].get("urls") or {}).get("forecast_data"),
            "access": "공개 페이지. 3번째 이후 분기는 [PRO] 로 표시되는 구독 구간",
            "fetched_at_utc": (c["stockanalysis"].get("fetched_at_utc") or {}).get("forecast_data"),
            "quarters_obtained": len(got),
            "observations": sa_obs,
            "accounting_basis": "non-GAAP adjusted (공급사 각주: EPS and Forward PE are based on non-GAAP adjusted numbers.)",
            "min_max_median": "미제공",
            "note": "회계분기 종료일과 마지막 발표 분기 인덱스를 제공해 미발표 창 확정에 사용했다.",
        }

        # --- Yahoo (2026-09-08 기존 조사 재사용) ---
        ylab, yval = YAHOO_2026_09_08.get(cid, ([], []))
        rec["sources"]["yahoo_2026_09_08_reused"] = {
            "vendor": "Yahoo Finance",
            "access": "공개 (무료는 2개 분기)",
            "observed_at_utc": "2026-09-08",
            "source_record": YAHOO_SRC,
            "quarters_obtained": len(yval),
            "observations": [{"seq": i + 1, "period_label_vendor": ylab[i], "mean": yval[i]}
                             for i in range(len(yval))],
            "note": "이번에 재수집하지 않았다. 기존 조사 기록을 그대로 인용한다.",
        }

        # --- TradingView (독립 3사, 1분기) ---
        tv = (ex.get("tradingview") or {})
        tvd = tv.get("data") or {}
        nrd = tvd.get("earnings_release_next_date")
        rec["sources"]["tradingview"] = {
            "vendor": "TradingView 스캐너",
            "url": tv.get("url"),
            "access": "공개 JSON GET",
            "fetched_at_utc": tv.get("fetched_at_utc"),
            "quarters_obtained": 1 if tvd.get("earnings_per_share_forecast_next_fq") is not None else 0,
            "next_fq_mean": tvd.get("earnings_per_share_forecast_next_fq"),
            "last_fq_actual": tvd.get("earnings_per_share_fq"),
            "last_fq_consensus": tvd.get("earnings_per_share_forecast_fq"),
            "next_release_epoch": nrd,
            "next_release_utc": (dt.datetime.fromtimestamp(nrd, dt.timezone.utc).strftime("%Y-%m-%d")
                                 if isinstance(nrd, (int, float)) else None),
            "min_max_median_count": "미제공",
        }

        # --- 회계 기준 차이 진단: 같은 '마지막 발표 분기'의 실적 EPS 를 원천별로 나란히 둔다 ---
        sa_adj_last = at(sa_q.get("adjustedEps"), sa_last) if isinstance(sa_last, int) else None
        sa_gaap_last = at(sa_q.get("eps"), sa_last) if isinstance(sa_last, int) else None
        tv_last_actual = tvd.get("earnings_per_share_fq")
        tv_fq_end = tvd.get("fiscal_period_end_fq")
        tv_fq_end_utc = (dt.datetime.fromtimestamp(tv_fq_end, dt.timezone.utc).strftime("%Y-%m-%d")
                         if isinstance(tv_fq_end, (int, float)) else None)
        nq_last_actual = prev[-1]["earnings"] if prev else None
        vals = [v for v in (nq_last_actual, tv_last_actual, sa_adj_last) if isinstance(v, (int, float))]
        periods_match = (tv_fq_end_utc is not None and sa_last_reported is not None
                         and abs((dt.date.fromisoformat(tv_fq_end_utc)
                                  - dt.date.fromisoformat(sa_last_reported)).days) <= 7)
        rec["basis_divergence_last_reported_quarter"] = {
            "purpose": "같은 분기의 확정 실적을 원천별로 비교해 회계 기준 차이를 드러낸다. 전망치 자체의 오류 판정이 아니다.",
            "period_label_nasdaq": prev[-1]["period"] if prev else None,
            "period_end_stockanalysis": sa_last_reported,
            "period_end_tradingview": tv_fq_end_utc,
            "periods_match_within_7d": periods_match,
            "actual_eps_nasdaq": nq_last_actual,
            "actual_eps_tradingview": tv_last_actual,
            "actual_eps_stockanalysis_adjusted": sa_adj_last,
            "actual_eps_stockanalysis_gaap_column": sa_gaap_last,
            "max_abs_gap": round(max(vals) - min(vals), 4) if len(vals) >= 2 else None,
            "vendors_agree_within_0_01": (len(vals) >= 2 and (max(vals) - min(vals)) <= 0.01),
            "interpretation": (
                "같은 기간인데 값이 다르면 공급사의 조정(adjusted) 정의가 서로 다르다는 뜻이다. "
                "이 경우 해당 기업은 원천 간 EPS 를 바꿔 쓰거나 분기를 이어 붙일 수 없다."),
        }

        # --- 검증 항목 ---
        checks = {}
        checks["nasdaq_two_endpoints_agree_on_next4_labels"] = (
            len(obs) == 4 and [o["period_label_vendor"] for o in obs] == upc_labels[:4])
        eps_map = {x["period"]: x["consensus"] for x in upc}
        checks["nasdaq_two_endpoints_agree_on_means"] = (
            len(obs) == 4 and all(
                isinstance(eps_map.get(o["period_label_vendor"]), (int, float))
                and abs(eps_map[o["period_label_vendor"]] - o["mean"]) < 1e-9 for o in obs))
        checks["min_le_mean_le_max_all_quarters"] = all(
            o["min"] <= o["mean"] <= o["max"] for o in obs
            if all(isinstance(o[k], (int, float)) for k in ("min", "mean", "max")))
        checks["estimate_count_positive_all_quarters"] = all(
            isinstance(o["estimate_count"], int) and o["estimate_count"] > 0 for o in obs)
        a1 = month_key(obs[0]["period_label_vendor"]) if obs else None
        b1 = date_key(sa_next4[0]) if sa_next4 else None
        checks["first_unreported_quarter_matches_stockanalysis"] = (a1 is not None and a1 == b1)
        checks["last_reported_period_matches_across_sources"] = periods_match
        checks["last_reported_actual_matches_across_sources"] = (
            rec["basis_divergence_last_reported_quarter"]["vendors_agree_within_0_01"])
        q1 = obs[0]["mean"] if obs else None
        y1 = float(yval[0]) if yval else None
        s1 = got[0]["adjusted_eps_mean"] if got else None
        t1 = tvd.get("earnings_per_share_forecast_next_fq")
        gaps = [abs(q1 - v) for v in (y1, s1, t1)
                if isinstance(v, (int, float)) and isinstance(q1, (int, float))]
        checks["q1_vendor_spread"] = {
            "nasdaq": q1, "yahoo_2026_09_08": y1, "stockanalysis": s1, "tradingview": t1,
            "max_abs_gap_vs_nasdaq": round(max(gaps), 4) if gaps else None,
            "max_rel_gap_vs_nasdaq_pct": (round(max(gaps) / abs(q1) * 100, 2)
                                          if gaps and isinstance(q1, (int, float)) and q1 else None),
        }
        checks["sum_4q_mean_positive"] = (
            rec["sources"]["nasdaq_api"]["mean_sum_4q"] is not None
            and rec["sources"]["nasdaq_api"]["mean_sum_4q"] > 0)
        rec["checks"] = checks

        # --- 확보 수준 / 채점 적격성 ---
        # 2원천 교차는 '커버'와 '수치 합치'를 나눠 센다. 커버만으로 교차검증됐다고 하지 않는다.
        covered = min(len(got), len(obs))
        agreed = 0
        for i in range(covered):
            v1, v2 = obs[i]["mean"], got[i]["adjusted_eps_mean"]
            if isinstance(v1, (int, float)) and isinstance(v2, (int, float)) and v1:
                if abs(v1 - v2) / abs(v1) <= 0.05:
                    agreed += 1
        rec["acquisition"] = {
            "next_4_quarter_eps_mean": "%d/4" % len(obs),
            "single_source_for_all_4": "nasdaq_api" if len(obs) == 4 else None,
            "min_max_count": "%d/4 (nasdaq_api)" % len(obs),
            "median": "0/4 — 조사한 공개 원천 어디에서도 중간값을 제공하지 않음(보조 정보 결측)",
            "quarters_covered_by_second_source": covered,
            "quarters_second_source_agrees_within_5pct": agreed,
            "quarters_single_source_only": max(0, len(obs) - covered),
            "corroboration_note": (
                "커버는 다른 원천이 같은 분기를 제공했다는 뜻이고, 합치는 값이 5%% 이내로 같다는 뜻이다. "
                "커버 %d/4, 합치 %d/4." % (covered, agreed)),
        }
        # --- 계산 후보 (검증 대기) ---
        px_raw = (info.get("primaryData") or {}).get("lastSalePrice")
        px = None
        if isinstance(px_raw, str):
            try:
                px = float(px_raw.replace("$", "").replace(",", ""))
            except ValueError:
                px = None
        s4 = rec["sources"]["nasdaq_api"]["mean_sum_4q"]
        rec["per_candidate"] = {
            "status": "검증 대기",
            "price": px,
            "price_label": (info.get("primaryData") or {}).get("lastTradeTimestamp"),
            "price_source": c["nasdaq"]["urls"].get("info"),
            "eps_sum_4q": s4,
            "eps_source": "nasdaq_api (같은 공급사 4분기 평균의 단순 합)",
            "price_div_eps_sum": (round(px / s4, 4)
                                  if isinstance(px, (int, float)) and isinstance(s4, (int, float)) and s4 > 0
                                  else None),
            "note": (
                "주가와 EPS 를 같은 공급사 화면에서 취해 만든 계산 후보다. 회계·주식 기준이 미확인이므로 "
                "채점 입력이 아니며 2026-09-02 기준선에 소급하지 않는다. 합이 0 이하면 계산을 보류한다."),
        }

        reasons = [
            "공급사 추정치 갱신 시각이 미확인이다(Nasdaq asOf=null).",
            "회계 기준(별표 정의)과 주식 기준(희석/기본)이 공급사 문서로 확인되지 않았다.",
            "3·4번째 분기는 현재 단일 원천에서만 확보되어 교차검증이 없다.",
            "분기 라벨은 공급사 월 표기이며 회사 공식 회계기간과의 대조가 남아 있다.",
            "채점 정책 결정은 이 조사의 범위가 아니다.",
        ]
        bd = rec["basis_divergence_last_reported_quarter"]
        if bd["periods_match_within_7d"] and not bd["vendors_agree_within_0_01"]:
            reasons.insert(2, (
                "같은 마지막 발표 분기의 확정 EPS 가 원천 간 %s 만큼 다르다(Nasdaq %s / TradingView %s / "
                "StockAnalysis %s). 조정 정의가 서로 달라 이 기업은 원천 간 EPS 를 대체할 수 없다."
                % (bd["max_abs_gap"], bd["actual_eps_nasdaq"], bd["actual_eps_tradingview"],
                   bd["actual_eps_stockanalysis_adjusted"])))
        rec["scoring_eligibility"] = {
            "usable_for_automatic_scoring": False,
            "reasons": reasons,
            "note": "자료 확보와 채점 적격성은 분리한다. 위 사유는 미확보가 아니라 미검증이다.",
        }
        out["companies"].append(rec)

    io.open(os.path.join(HERE, "evidence.json"), "w", encoding="utf-8").write(
        json.dumps(out, ensure_ascii=False, indent=1))
    print("wrote evidence.json  companies=%d" % len(out["companies"]))


if __name__ == "__main__":
    main()
