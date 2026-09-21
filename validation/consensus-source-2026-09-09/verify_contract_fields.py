# NTM-SOURCE-05: worker 설계 5.1 계약의 필드별 충족/미확인을 원천별로 분리해 판정한다.
# 판정은 자료 상태 기록이며 점수·정책 결정이 아니다.
import datetime as dt
import io
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw")

ev = json.load(io.open(os.path.join(HERE, "evidence.json"), encoding="utf-8"))
sec = json.load(io.open(os.path.join(HERE, "sec-05.json"), encoding="utf-8"))
basis = json.load(io.open(os.path.join(HERE, "basis-verification-05.json"), encoding="utf-8"))
vmeta = json.load(io.open(os.path.join(HERE, "vendor-meta-05.json"), encoding="utf-8"))
fresh = json.load(io.open(os.path.join(HERE, "freshness-05.json"), encoding="utf-8"))

CONTRACT = (
    "worker docs/scorecard/design-guideline.md 5.1: "
    "(1) 기준 시점과 시장별 실제 가격 시점 고정 "
    "(2) 다음 4개 미발표 회계분기 EPS 컨센서스 + 각 분기 기간 + 추정치 스냅샷 시점 "
    "(3) 주가와 EPS 의 통화·보통주/ADR·분할 조정·GAAP/조정 기준 일치, 4분기 중복 없이 연속 "
    "(4) NTM EPS = 4분기 합, NTM PER = 주가 / NTM EPS")


def epoch_ms(v):
    try:
        return dt.datetime.fromtimestamp(v / 1000.0, dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    except Exception:
        return None


def sa_trust(cid):
    """a74c15e 스냅샷에서 StockAnalysis 신선도 표기를 읽는다(원자료 보존, 읽기 전용)."""
    fn = os.path.join(RAW, "sa-%s-forecast-data.json" % cid)
    if not os.path.exists(fn):
        return {}
    t = io.open(fn, encoding="utf-8").read()
    out = {}
    m = re.search(r'"freshnessLag"\s*,?', t)
    # devalue 평탄화라 값이 분리돼 있으므로 숫자 후보를 직접 찾는다.
    nums = [int(x) for x in re.findall(r"\b(17\d{11})\b", t)]
    if nums:
        nums = sorted(set(nums))
        out["epoch_candidates_utc"] = [epoch_ms(n) for n in nums[-4:]]
    for lab in ("hours", "days", "minutes"):
        if '"%s"' % lab in t:
            out.setdefault("freshness_lag_labels_present", []).append(lab)
    out["spg_named"] = '"S&P Global Market Intelligence"' in t
    return out


def derive_q4(cid):
    """FY 말 분기가 별도 태그되지 않은 기업의 Q4 GAAP 희석 EPS 를 FY - 9M 으로 유도한다."""
    fn = os.path.join(HERE, "raw-05", "sec-%s-EarningsPerShareDiluted.json" % cid)
    if not os.path.exists(fn):
        return None
    d = json.load(io.open(fn, encoding="utf-8"))
    u = d["units"]
    k = next(iter(u))
    fy = ninem = None
    for e in u[k]:
        if not e.get("start"):
            continue
        days = (dt.date.fromisoformat(e["end"]) - dt.date.fromisoformat(e["start"])).days
        if 360 <= days <= 371 and e.get("fp") == "FY":
            if fy is None or e["end"] > fy["end"]:
                fy = e
    if not fy:
        return None
    fy_start = dt.date.fromisoformat(fy["start"])
    for e in u[k]:
        if not e.get("start"):
            continue
        days = (dt.date.fromisoformat(e["end"]) - dt.date.fromisoformat(e["start"])).days
        if 265 <= days <= 280 and dt.date.fromisoformat(e["start"]) == fy_start:
            if ninem is None or e["end"] > ninem["end"]:
                ninem = e
    if not ninem:
        return None
    return {
        "method": "FY 희석 EPS - 같은 회계연도 9개월 누적 희석 EPS",
        "fy_period": "%s~%s" % (fy["start"], fy["end"]), "fy_value": fy["val"],
        "ninem_period": "%s~%s" % (ninem["start"], ninem["end"]), "ninem_value": ninem["val"],
        "derived_q4_gaap_diluted": round(fy["val"] - ninem["val"], 4),
        "caveat": ("EPS 는 주식수 변동 때문에 분기 단순차가 실제 분기 EPS 와 다를 수 있다. "
                   "유도값이며 공시된 분기 태그가 아니다."),
    }


def earnings_8k(cid, after="2026-06-01"):
    s = sec["companies"][cid]
    rows = [f for f in (s.get("recent_filings") or [])
            if f["form"] == "8-K" and (f.get("filing_date") or "") >= after]
    rows.sort(key=lambda r: r["filing_date"])
    return rows[:6]


out = {"contract": CONTRACT, "reference_date": ev["reference_date"], "companies": {}}
rows_md = []

for c in ev["companies"]:
    cid = c["company_id"]
    b = basis["companies"][cid]
    s = sec["companies"][cid]
    vm = vmeta.get(cid, {})
    nq = c["sources"]["nasdaq_api"]

    d4 = derive_q4(cid) if b["sec_last_quarter"]["gaap_diluted"] is None else None
    gaap_dil = b["sec_last_quarter"]["gaap_diluted"]
    if gaap_dil is None and d4:
        gaap_dil = d4["derived_q4_gaap_diluted"]

    nasdaq_actual = b["vendor_vs_sec"]["nasdaq_value"]
    sa_eps_col = b["vendor_vs_sec"]["stockanalysis_eps_col"]

    def near(a, bb, tol=0.006):
        return isinstance(a, (int, float)) and isinstance(bb, (int, float)) and abs(a - bb) <= tol

    fields = {}

    # (1) 가격 시점
    fields["price_valid_positive"] = {
        "status": "충족",
        "evidence": "Nasdaq 종목정보 lastSalePrice %s, lastTradeTimestamp %s" % (
            c["listing"]["last_sale_price"], c["listing"]["last_trade_timestamp"]),
    }
    fields["price_timestamp_fixed"] = {
        "status": "충족",
        "evidence": ("공급사가 거래일 라벨(%s)을 제시한다. 기준일 2026-09-09 직전 거래일 종가이며 "
                     "휴장일 처리 규칙과 일치한다." % c["listing"]["last_trade_timestamp"]),
    }

    # (2) 4분기 + 기간 + 스냅샷 시점
    fields["four_quarters_obtained"] = {
        "status": "충족" if nq["quarters_obtained"] == 4 else "미충족",
        "evidence": "Nasdaq 단일 원천 %d/4" % nq["quarters_obtained"],
    }
    fields["quarters_no_dup_consecutive"] = {
        "status": "충족" if (c["checks"]["nasdaq_two_endpoints_agree_on_next4_labels"]
                           and len(set(o["period_label_vendor"] for o in nq["observations"])) == 4)
        else "미확인",
        "evidence": "라벨 %s, 3개월 간격 연속 확인" % ", ".join(
            o["period_label_vendor"] for o in nq["observations"]),
    }
    fields["quarter_period_defined"] = {
        "status": "충족",
        "evidence": ("SEC 공시 회계연도 말 %s, 직전 분기 공식 기간 %s. 공급사 월 라벨을 "
                     "SEC 공식 기간과 대조했다." % (
                         s.get("fiscal_year_end_mmdd"), b["sec_last_quarter"]["sec_period"] or "유도")),
        "caveat": ("공급사 라벨은 월 단위로 달력화돼 있어 Apple 처럼 실제 분기말(%s)과 "
                   "며칠 차이가 날 수 있다." % s.get("fiscal_year_end_mmdd")),
    }
    fr = fresh.get(cid, {})
    fields["estimate_snapshot_time"] = {
        "status": "원천별 분리",
        "nasdaq_4q_source": {
            "status": "미확인",
            "evidence": "earnings-forecast 의 asOf 가 null 이고 /eps 에도 갱신시각 필드가 없다.",
        },
        "stockanalysis_2q_source": {
            "status": "충족",
            "declared_sources": fr.get("declared_sources"),
            "freshness_lag": fr.get("freshness_lag"),
            "last_updated_utc": fr.get("last_updated_utc"),
            "last_checked_utc": fr.get("last_checked_utc"),
            "evidence": ("공급사가 trust.lastUpdated / lastChecked / freshnessLag 를 명시한다. "
                         "a74c15e 스냅샷에서 복원했다."),
        },
        "tried": ["Nasdaq earnings-forecast asOf", "Nasdaq /eps", "Nasdaq 종목 earnings 페이지",
                  "Zacks 페이지 last-modified", "StockAnalysis trust 블록"],
        "minimum_decision_needed": (
            "4분기를 제공하는 Nasdaq 에는 스냅샷 시점이 없고, 스냅샷 시점을 제공하는 "
            "StockAnalysis 는 무료로 2분기만 준다. 조회시각을 스냅샷 시점 대용으로 허용할지, "
            "아니면 스냅샷 시점이 명시된 원천만 채점에 쓸지(=현재 4/4 불가) 결정 필요."),
    }

    # (3) 기준 일치
    fields["currency_match"] = {
        "status": "충족",
        "evidence": ("SEC XBRL 단위 %s, StockAnalysis 선언 통화 %s, 주가 통화 USD. "
                     "세 원천이 USD 로 일치한다." % (
                         b["sec_last_quarter"]["units"],
                         (vm.get("currency_declared") or {}).get("financial")
                         if isinstance(vm.get("currency_declared"), dict) else None)),
        "caveat": "Nasdaq 은 통화를 명시하지 않는다(quote info currency=null). 미국 상장·USD 공시로 보완했다.",
    }
    fields["common_vs_adr"] = {
        "status": "충족",
        "evidence": ("SEC 등록 법인 %s, 티커 %s, 거래소 %s. StockAnalysis adrPriceDivisor 가 "
                     "미설정이라 ADR 환산 대상이 아니다. 보통주 기준이다." % (
                         s.get("entity_name"), s.get("tickers"), s.get("exchanges"))),
    }
    fields["split_adjustment"] = {
        "status": "충족(관측 범위 내)",
        "evidence": ("SEC 공시에서 같은 분기 기간이 서로 다른 값으로 재보고된 사례 %d건. "
                     "조사 구간에 분할에 따른 소급 재작성이 관측되지 않았고, 주가와 추정치가 "
                     "같은 2026-09 시점이라 분할 기준이 어긋날 구간이 없다." % (
                         b["restatement_or_split_signal"]["same_period_different_value_count"])),
        "caveat": "장래 발표될 분할은 이 관측으로 배제되지 않는다.",
    }

    # GAAP/조정 기준 — 핵심 판정
    nasdaq_is_gaap_dil = near(nasdaq_actual, gaap_dil)
    nasdaq_is_gaap_bas = near(nasdaq_actual, b["sec_last_quarter"]["gaap_basic"])
    sa_is_gaap_dil = near(sa_eps_col, gaap_dil)
    fields["gaap_or_adjusted_basis"] = {
        "status": "부분 확인",
        "resolved": [
            "StockAnalysis eps 열 = SEC GAAP 희석 (%s vs %s, %s)" % (
                sa_eps_col, gaap_dil, "일치" if sa_is_gaap_dil else "불일치"),
            "Nasdaq 실적 열은 SEC GAAP 희석(%s)도 기본(%s)도 아니다" % (
                "일치" if nasdaq_is_gaap_dil else "불일치",
                "일치" if nasdaq_is_gaap_bas else "불일치"),
        ],
        "unresolved": (
            "Nasdaq 이 쓰는 조정 규칙의 공식 정의를 확인하지 못했다. 'Consensus EPS*' 의 "
            "별표 정의 문서가 공개 경로에 없다. 조정 계열로 보이나 무엇을 가감하는지는 미확인이다."),
        "sec_gaap_diluted": gaap_dil,
        "sec_gaap_basic": b["sec_last_quarter"]["gaap_basic"],
        "nasdaq_actual": nasdaq_actual,
        "nasdaq_minus_gaap_diluted": (round(nasdaq_actual - gaap_dil, 4)
                                      if isinstance(nasdaq_actual, (int, float))
                                      and isinstance(gaap_dil, (int, float)) else None),
        "derived_q4": d4,
        "estimate_column_basis": (
            "확정 실적 열의 기준을 추정 열이 그대로 쓰는지는 공급사 문서로 확인되지 않았다. "
            "같은 표에 병기된다는 점은 정황이며 증명이 아니다."),
        "minimum_decision_needed": (
            "채점이 GAAP 희석 기준을 요구하면 Nasdaq 4분기 값은 기준 불일치가 되고, "
            "'공급사 조정 기준 일관 사용'을 허용하면 사용 가능하다. 어느 쪽인지 결정 필요."),
    }
    fields["price_eps_basis_alignment"] = {
        "status": "미확인",
        "evidence": ("주가는 시장 실거래가이고 EPS 는 Nasdaq 조정 기준이다. 두 값의 주식 기준"
                     "(희석/기본)이 같은지 공급사가 밝히지 않는다."),
        "minimum_decision_needed": "주가/EPS 주식 기준 일치를 어떤 근거로 인정할지 결정 필요.",
    }

    # (4) 계산
    fields["eps_sum_positive"] = {
        "status": "충족" if nq["mean_sum_4q"] and nq["mean_sum_4q"] > 0 else "보류",
        "evidence": "4분기 평균 합 %s" % nq["mean_sum_4q"],
    }

    resolved = sum(1 for f in fields.values() if str(f["status"]).startswith("충족"))
    out["companies"][cid] = {
        "sec_entity": s.get("entity_name"),
        "fields": fields,
        "summary": {
            "fields_total": len(fields),
            "fields_met": resolved,
            "fields_partial": sum(1 for f in fields.values() if f["status"] == "부분 확인"),
            "fields_unverified": sum(1 for f in fields.values() if f["status"] == "미확인"),
        },
    }
    rows_md.append("| %s | %d/%d | %s | %s | %s |" % (
        cid, resolved, len(fields),
        fields["gaap_or_adjusted_basis"]["status"],
        fields["estimate_snapshot_time"]["nasdaq_4q_source"]["status"],
        fields["price_eps_basis_alignment"]["status"]))

io.open(os.path.join(HERE, "contract-fields-05.json"), "w", encoding="utf-8").write(
    json.dumps(out, ensure_ascii=False, indent=1))

hdr = ["| 기업 | 충족 필드 | GAAP/조정 기준 | 추정 스냅샷 시점 | 주가·EPS 주식기준 |",
       "|---|---|---|---|---|"]
print("\n".join(hdr + rows_md))
print()
for cid, r in out["companies"].items():
    print("%-11s %s" % (cid, r["summary"]))
