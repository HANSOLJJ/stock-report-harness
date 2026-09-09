# NTM-SOURCE-05: 공급사 EPS 를 SEC 공시 GAAP 기본/희석과 대조해 회계·주식 기준을 검증한다.
# 수치 일치는 근거의 하나일 뿐이며 공급사 공식 정의가 없으면 확정으로 쓰지 않는다.
import datetime as dt
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))

sec = json.load(io.open(os.path.join(HERE, "sec-05.json"), encoding="utf-8"))
ev = json.load(io.open(os.path.join(HERE, "evidence.json"), encoding="utf-8"))
extra = json.load(io.open(os.path.join(HERE, "collect-extra.json"), encoding="utf-8"))
raw = json.load(io.open(os.path.join(HERE, "collect-raw.json"), encoding="utf-8"))
vmeta = json.load(io.open(os.path.join(HERE, "vendor-meta-05.json"), encoding="utf-8"))

sa_by_cid = {c["company_id"]: c["stockanalysis"] for c in raw["companies"]}


def close(a, b, tol=0.005):
    return isinstance(a, (int, float)) and isinstance(b, (int, float)) and abs(a - b) <= tol


out = {"generated_at_utc": ev["generated_at_utc"], "companies": {}}
lines = []

for c in ev["companies"]:
    cid = c["company_id"]
    s = sec["companies"][cid]
    rec = {}

    # --- 1. 법인 정체성과 공식 회계연도 ---
    rec["sec_entity_name"] = s.get("entity_name")
    rec["sec_tickers"] = s.get("tickers")
    rec["sec_exchanges"] = s.get("exchanges")
    rec["sec_fiscal_year_end_mmdd"] = s.get("fiscal_year_end_mmdd")
    rec["sec_cik"] = s.get("cik")

    # --- 2. 마지막 발표 분기: 공급사 라벨 vs SEC 공식 기간 ---
    bd = c["basis_divergence_last_reported_quarter"]
    dil = (s.get("quarterly") or {}).get("EarningsPerShareDiluted") or []
    bas = (s.get("quarterly") or {}).get("EarningsPerShareBasic") or []
    sa_end = bd["period_end_stockanalysis"]

    def pick(rows, end):
        cands = [r for r in rows if end and abs(
            (dt.date.fromisoformat(r["end"]) - dt.date.fromisoformat(end)).days) <= 7]
        return cands[-1] if cands else None

    d_row = pick(dil, sa_end)
    b_row = pick(bas, sa_end)
    rec["sec_last_quarter"] = {
        "matched_to_vendor_period_end": sa_end,
        "sec_period": (d_row or {}).get("start", None) and
                      "%s~%s" % (d_row["start"], d_row["end"]) or None,
        "gaap_diluted": (d_row or {}).get("val"),
        "gaap_basic": (b_row or {}).get("val"),
        "form": (d_row or {}).get("form"),
        "filed": (d_row or {}).get("filed"),
        "fy_fp": "%s %s" % ((d_row or {}).get("fy"), (d_row or {}).get("fp")) if d_row else None,
        "units": (s.get("xbrl_units") or {}).get("EarningsPerShareDiluted"),
    }

    # --- 3. 공급사 값과 SEC GAAP 대조 ---
    nq = bd["actual_eps_nasdaq"]
    tv = bd["actual_eps_tradingview"]
    sa_adj = bd["actual_eps_stockanalysis_adjusted"]
    sa_eps = bd["actual_eps_stockanalysis_gaap_column"]
    gd = rec["sec_last_quarter"]["gaap_diluted"]
    gb = rec["sec_last_quarter"]["gaap_basic"]
    rec["vendor_vs_sec"] = {
        "nasdaq_equals_gaap_diluted": close(nq, gd),
        "nasdaq_equals_gaap_basic": close(nq, gb),
        "tradingview_equals_gaap_diluted": close(tv, gd),
        "stockanalysis_epsCol_equals_gaap_diluted": close(sa_eps, gd),
        "stockanalysis_adjCol_equals_gaap_diluted": close(sa_adj, gd),
        "nasdaq_value": nq, "tradingview_value": tv,
        "stockanalysis_eps_col": sa_eps, "stockanalysis_adj_col": sa_adj,
        "sec_gaap_diluted": gd, "sec_gaap_basic": gb,
        "nasdaq_minus_gaap_diluted": (round(nq - gd, 4)
                                      if isinstance(nq, (int, float)) and isinstance(gd, (int, float))
                                      else None),
    }

    # --- 4. 분할/재작성 흔적: 같은 기간이 서로 다른 값으로 재보고됐는가 ---
    restated = []
    seen = {}
    for r in dil:
        k = (r["start"], r["end"])
        if k in seen and not close(seen[k]["val"], r["val"], 1e-9):
            restated.append({"period": "%s~%s" % k, "values": [seen[k]["val"], r["val"]],
                             "forms": [seen[k]["form"], r["form"]],
                             "filed": [seen[k]["filed"], r["filed"]]})
        seen[k] = r
    rec["restatement_or_split_signal"] = {
        "same_period_different_value_count": len(restated),
        "examples": restated[:3],
        "note": ("같은 기간이 다른 값으로 재보고되면 분할·정정 가능성을 본다. "
                 "0건은 조사 구간에서 재작성이 관측되지 않았다는 뜻이며 분할 부재의 증명이 아니다."),
    }

    # --- 5. 통화·주식 기준 선언 ---
    vm = vmeta.get(cid, {})
    rec["currency_and_share_basis"] = {
        "stockanalysis_declared_currency": vm.get("currency_declared"),
        "stockanalysis_adr_price_divisor": vm.get("adr_price_divisor"),
        "stockanalysis_exchange_rate": vm.get("exchange_rate"),
        "sec_xbrl_eps_unit": (s.get("xbrl_units") or {}).get("EarningsPerShareDiluted"),
        "nasdaq_declared_currency": "미표기(quote info 의 currency 필드 null)",
        "share_class_per_sec": s.get("tickers"),
        "is_adr": (vm.get("adr_price_divisor") is not None),
    }

    # --- 6. 공급사 표기 ---
    rec["vendor_attribution"] = {
        "stockanalysis_estimates_source_code": vm.get("estimates_source_code"),
        "stockanalysis_declared_sources": vm.get("declared_data_sources"),
        "nasdaq_provider_declared": None,
        "nasdaq_header_label": (c["sources"]["nasdaq_api"].get("header_labels") or {}).get(
            "consensusEPSForecast"),
    }

    out["companies"][cid] = rec

    v = rec["vendor_vs_sec"]
    lines.append("%-11s SEC %s dil=%s bas=%s | nasdaq=%s(%s) tv=%s(%s) saEps=%s(%s) | 재작성=%d" % (
        cid, rec["sec_last_quarter"]["sec_period"], gd, gb,
        nq, "GAAP희석일치" if v["nasdaq_equals_gaap_diluted"] else "불일치",
        tv, "일치" if v["tradingview_equals_gaap_diluted"] else "불일치",
        sa_eps, "일치" if v["stockanalysis_epsCol_equals_gaap_diluted"] else "불일치",
        len(restated)))

io.open(os.path.join(HERE, "basis-verification-05.json"), "w", encoding="utf-8").write(
    json.dumps(out, ensure_ascii=False, indent=1))
txt = "\n".join(lines)
io.open(os.path.join(HERE, "basis-verification-05.txt"), "w", encoding="utf-8").write(txt)
print(txt)
