"""QWEN-NTM-DATA-03: 수집 증거를 통합해 회사별 충족 판정표와 최종 evidence.json 을 만든다.

판정 기준은 worker/docs/scorecard/design-guideline.md §5.1 의 NTM 계약이다.
  - 충족(확보): 다음 4개 미발표 회계분기 EPS 컨센서스(각 분기 기간·스냅샷 시점 포함) 확보,
    또는 NTM 정의가 입증된 공급사 PER 확보
  - 미충족: 다음 1분기 예상만 있거나 과거 실적 4개인 경우, 또는 분기 수가 4개 미만인 경우
  - 주가/PER 역산은 참고 기록일 뿐 분모 기간의 증명으로 쓰지 않는다
"""
raise SystemExit("consolidate.py is deprecated; use apply_r1_corrections.py and analyze_fy.py")
import io
import json
import os
from collections import OrderedDict
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
load = lambda n: json.load(io.open(os.path.join(HERE, n), encoding="utf-8"))

sa = load("evidence.json")
yh = load("evidence-yahoo.json")
fy = load("fy-labels.json")

yh_by = {r["company_id"]: r for r in yh["companies"]}

# Yahoo 의 Current Year 라벨이 회계연도 몇 년도인지 → 회계연도 종료월 판별 근거
FY_END = {
    "nvidia": "1월 말 (Yahoo Current Qtr.=Oct 2026·Next Qtr.=Jan 2027, Current Year=2027; StockAnalysis FY 라벨이 2029 까지)",
    "microsoft": "6월 말 (Yahoo Current Year=2027·Next Year=2028; StockAnalysis FY 라벨이 2029 까지)",
    "oracle": "5월 31일 (Yahoo Earnings History 기간말 8/31/2025·11/30/2025·2/28/2026·5/31/2026; Current Year=2027)",
    "apple": "9월 말 추정 (Yahoo Current Qtr.=Sep 2026·Next Qtr.=Dec 2026, Current Year=2026)",
}

rows = []
for rec in sa["companies"]:
    cid = rec["company_id"]
    ov = rec.get("overview") or {}
    st = rec.get("statistics") or {}
    fc = rec.get("forecast") or {}
    bc = rec.get("backcalc") or {}
    y = (yh_by.get(cid) or {}).get("parsed") or {}
    f = fy.get(cid) or {}

    price = bc.get("price")
    fpe = bc.get("forward_pe_statistics") or bc.get("forward_pe_overview")
    imp = bc.get("implied_denominator_eps_from_statistics")
    eth = bc.get("eps_this_year")
    eny = bc.get("eps_next_year")
    pe_this = bc.get("pe_if_denominator_is_this_fy")
    pe_next = bc.get("pe_if_denominator_is_next_fy")

    exact_this = (imp is not None and eth not in (None, 0)
                  and abs(imp - eth) / abs(eth) < 0.002)
    exact_next = (imp is not None and eny not in (None, 0)
                  and abs(imp - eny) / abs(eny) < 0.002)

    nq = y.get("n_forward_quarters")
    q_periods = (y.get("quarter_periods") or [])[:2]
    yahoo_avg = (y.get("avg_estimate_row") or [])[:4]

    # 공급사 간 연간 추정치 교차 검증
    xcheck = None
    if yahoo_avg and len(yahoo_avg) >= 4 and eth is not None:
        try:
            y_this = float(yahoo_avg[2])
            y_next = float(yahoo_avg[3])
            xcheck = OrderedDict([
                ("stockanalysis_this_year", eth), ("yahoo_current_year", y_this),
                ("diff_this", round(eth - y_this, 4)),
                ("stockanalysis_next_year", eny), ("yahoo_next_year", y_next),
                ("diff_next", round((eny or 0) - y_next, 4)),
                ("yahoo_year_label", (y.get("year_periods") or [None])[0]),
            ])
        except (TypeError, ValueError):
            pass

    row = OrderedDict()
    row["company_id"] = cid
    row["ticker_used"] = rec["ticker_used"]
    row["registry_ticker"] = rec["registry_ticker"]
    row["registry_defect"] = (rec["registry_ticker"] is None)
    row["baseline_ntm_per_2026_09_02"] = rec["baseline_ntm_per_2026_09_02"]
    row["baseline_price_2026_09_02"] = rec["baseline_price_2026_09_02"]

    row["urls"] = [f["url"] for f in rec["fetches"] if f.get("url")]
    row["fetched_at_utc"] = [f.get("fetched_at_utc") for f in rec["fetches"] if f.get("fetched_at_utc")]
    row["yahoo_url"] = (yh_by.get(cid) or {}).get("url")
    row["yahoo_fetched_at_utc"] = (yh_by.get(cid) or {}).get("fetched_at_utc")
    row["http_status"] = [f.get("status") for f in rec["fetches"]]

    row["value"] = OrderedDict([
        ("price_usd", price),
        ("price_date_label", ov.get("price_date_label")),
        ("forward_pe", fpe),
        ("pe_ratio_trailing", bc.get("pe_ratio_reported")),
        ("eps_ttm", bc.get("eps_ttm")),
        ("trailing_check_price_div_eps_ttm", bc.get("trailing_check_price_div_eps_ttm")),
        ("currency", "USD (Yahoo 'Currency in USD' 표기 / StockAnalysis 헤더 'Real-Time Price · USD')"),
        ("share_unit", "미문서화 — 두 공급사 모두 diluted/basic 주식 기준을 명시하지 않음"),
        ("accounting_basis", "non-GAAP adjusted (StockAnalysis 각주 'EPS and Forward PE are based on "
                             "non-GAAP adjusted numbers.' 10/10 확인; Yahoo 는 GAAP/Normalized 토글 존재)"),
    ])

    row["forecast_period"] = OrderedDict([
        ("yahoo_forward_quarters_free", nq),
        ("yahoo_quarter_periods", q_periods),
        ("yahoo_avg_estimate_row", yahoo_avg),
        ("stockanalysis_quarterly_labels_in_free_html", (f.get("quarter_labels_Q"))),
        ("stockanalysis_quarterly_is_ui_toggle_only", fc.get("quarterly_is_ui_toggle_only")),
        ("stockanalysis_fy_labels", f.get("fy_labels")),
        ("stockanalysis_eps_this_year", eth),
        ("stockanalysis_eps_next_year", eny),
        ("stockanalysis_upgrade_marker_count", f.get("upgrade_count")),
        ("stockanalysis_nongaap_footnote", f.get("nongaap")),
        ("fiscal_year_end_evidence", FY_END.get(cid, "12월 말 (역년) — Yahoo Current Year 라벨이 2026")),
        ("estimate_snapshot_time", OrderedDict([
            ("stockanalysis_forecast_last_updated", fc.get("last_updated")),
            ("yahoo_fetch_time_utc", (yh_by.get(cid) or {}).get("fetched_at_utc")),
            ("note", "공급사는 개별 추정치의 스냅샷 시점을 노출하지 않는다. 페이지 'Last updated' 만 확인 가능."),
        ])),
    ])

    row["period_verdict"] = OrderedDict([
        ("forward_pe_period", "FY-current(입증)" if exact_this else
                              ("FY-next(입증)" if exact_next else "불명(indeterminate)")),
        ("backcalc_implied_denominator_eps", imp),
        ("backcalc_pe_if_this_fy", pe_this),
        ("backcalc_pe_if_next_fy", pe_next),
        ("exact_match_to_this_fy", exact_this),
        ("exact_match_to_next_fy", exact_next),
        ("cross_vendor_check", xcheck),
        ("is_ntm_proven", False),
        ("reason", [
            "통계 페이지에 Forward PE 기간 정의 문구 없음(실측)",
            "정의 문서 후보 /glossary/ · /about/data/ 모두 HTTP 404(실측)",
            "각주는 회계 기준(non-GAAP adjusted) 만 밝히고 전망 기간은 밝히지 않음",
            ("역산 분모 %.4f 가 'EPS This Year' %.2f 와 0.2%% 이내 일치 → 분모는 이번 회계연도 추정치"
             % (imp, eth)) if exact_this else
            ("역산 분모가 이번·다음 회계연도 어느 것과도 정확히 일치하지 않음 → 기간 특정 불가" % ()),
            "설계 지침 §5.1: 'forwardPE 라는 공급사 필드 이름만으로 NTM임을 인정하지 않는다'",
            "작업 지시: '주가/PER 역산만으로 분모의 기간은 증명되지 않습니다'",
        ]),
    ])

    # §5.1 요구 충족 여부
    req = OrderedDict()
    req["가격_유효양수"] = bool(price and price > 0)
    req["다음4개_미발표분기_EPS"] = False
    req["각분기_기간_기록"] = (nq == 4)
    req["추정치_스냅샷_시점_기록"] = False
    req["통화_일치"] = True
    req["보통주_ADR_주식기준_확인"] = False
    req["GAAP_조정_기준_확인"] = True
    req["4분기_중복없고_연속"] = False
    req["EPS합_양수"] = None
    row["contract_5_1"] = req
    row["satisfied"] = all(v is True for k, v in req.items() if v is not None) and \
        req["다음4개_미발표분기_EPS"]

    # 분류
    if row["satisfied"]:
        cls = "확보"
    elif (price and price > 0) and (nq or 0) >= 1 and (eth is not None):
        cls = "일부확보"
    elif price is None:
        cls = "미확인"
    else:
        cls = "일부확보"
    row["classification"] = cls
    row["classification_reason"] = (
        "유효 양수 주가·향후 2개 분기 EPS·이번/다음 회계연도 EPS·non-GAAP 기준·USD 통화는 확보했으나, "
        "§5.1 이 요구하는 '다음 4개 미발표 회계분기 EPS 컨센서스' 는 어느 무료 공개 원천에서도 확보되지 않았다. "
        "따라서 NTM EPS 를 계산할 수 없고 Forward PE 의 분모 기간도 입증되지 않았다."
    )
    row["missing_for_satisfaction"] = [
        "향후 3·4번째 분기 EPS 컨센서스 (Yahoo 무료는 2개 분기만 공개)",
        "주식 기준(diluted/basic) 명시",
        "개별 추정치의 스냅샷 시점",
        "Forward PE 분모 기간의 공급사 정의 문서",
    ]
    rows.append(row)

# ---- 전역 관찰
glob = OrderedDict()
glob["sources_tested"] = [
    OrderedDict([("name", "StockAnalysis (overview / forecast / statistics)"),
                 ("access", "무료, 가입 불필요, HTTP 200"),
                 ("quarterly_eps", "없음 — 서빙 HTML 에 Q# YYYY 라벨 0건 (10/10)"),
                 ("annual_eps", "이번·다음 회계연도 무료. 그 이후 열은 'Upgrade' (65~80건/페이지)"),
                 ("automation", "가능 — 서버 렌더 HTML, JSON 페이로드 없음(실측: __NUXT__/__NEXT_DATA__ 0건), "
                                "데이터 API 단서 없음(plausible 분석 엔드포인트 1건뿐)"),
                 ("url_example", "https://stockanalysis.com/stocks/meta/forecast/")]),
    OrderedDict([("name", "Yahoo Finance /quote/<T>/analysis/"),
                 ("access", "무료, 가입 불필요, HTTP 200 (10/10)"),
                 ("quarterly_eps", "향후 2개 분기만 (Current Qtr. / Next Qtr.) — 10/10 균일"),
                 ("annual_eps", "Current Year / Next Year 무료"),
                 ("automation", "가능 — 정적 HTML 에 표 포함. 단 'Oops, something went wrong' 문자열이 "
                                "페이지에 상존하므로 오류 판별은 표 존재 여부로 해야 한다"),
                 ("url_example", "https://finance.yahoo.com/quote/META/analysis/")]),
    OrderedDict([("name", "Nasdaq.com /market-activity/stocks/<t>/earnings"),
                 ("access", "무료이나 JS 렌더링 — 정적 HTML 은 'Data is currently not available'"),
                 ("quarterly_eps", "정적 수집 불가"),
                 ("automation", "불가(정적 GET) — 헤드리스 브라우저 필요"),
                 ("url_example", "https://www.nasdaq.com/market-activity/stocks/meta/earnings")]),
    OrderedDict([("name", "StockAnalysis 정의 문서 (/glossary/, /about/data/)"),
                 ("access", "HTTP 404 — 존재하지 않음"),
                 ("quarterly_eps", "해당 없음"),
                 ("automation", "해당 없음")]),
    OrderedDict([("name", "StockAnalysis Pro 유료 티어"),
                 ("access", "$6.58/월(연간 결제) 또는 $9.99/월 — 작업 제약상 사용 금지"),
                 ("quarterly_eps", "가격 페이지에는 추정치 관련 기능 목록이 없어 분기 공개 여부를 문서로 확인 불가"),
                 ("note", "Pro 기능 목록 실측: 'Advanced analyst filtering options.', "
                          "'Filter forecasts by top performing analysts only.', "
                          "'Follow up to 25 analysts…' — 모두 필터링 기능이며 신규 추정치 데이터 추가가 아님")]),
]
glob["uniform_findings"] = OrderedDict([
    ("stockanalysis_quarterly_labels", "10/10 회사에서 Q# YYYY 라벨 0건 → 분기 EPS 컨센서스가 무료 HTML 에 존재하지 않음"),
    ("stockanalysis_quarterly_toggle", "'Quarterly' 는 UI 토글 버튼으로만 존재하고 서빙 HTML 에 분기 데이터 없음"),
    ("yahoo_forward_quarters", "10/10 회사에서 정확히 2개 분기만 공개"),
    ("yahoo_currency_note", "10/10 'Currency in USD'"),
    ("yahoo_gaap_toggle", "10/10 GAAP/Normalized 토글 존재"),
    ("stockanalysis_nongaap_footnote", "10/10 'EPS and Forward PE are based on non-GAAP adjusted numbers.'"),
    ("stockanalysis_upgrade_markers", "페이지당 65~80건 → 이후 회계연도 열은 유료"),
    ("non_calendar_fy", "nvidia·microsoft·oracle 만 StockAnalysis FY 라벨이 2029 까지 확장되고 "
                        "Yahoo 'Current Year' 가 2027/2028 → 회계연도가 역년이 아님. "
                        "이 3사는 'EPS This Year' 가 12개월 미만의 기간을 덮으므로 NTM 이 될 수 없다."),
    ("cross_vendor_agreement", "StockAnalysis 'EPS This/Next Year' 는 Yahoo 'Current/Next Year' 와 "
                               "대부분 정확히 일치(ORCL 8.06/10.97, MSFT 19.75/23.57, NVDA 9.31, GOOGL 20.60, "
                               "PLTR 1.61/2.33, TSLA 1.77/2.16, AAPL 9.57) → 두 공급사 모두 '회계연도' 컨센서스"),
])
glob["parser_caveats"] = [
    "collect_ntm.py 의 첫 실행에서 주가 추출이 실패(price=None) → 실제 DOM 패턴 "
    "(text-4xl font-bold ...\">VALUE) 에 맞게 reparse.py 로 보정. 원문 HTML 을 저장해 두었기 때문에 "
    "재파싱해도 조회시각이 보존된다.",
    "collect_yahoo.py 의 no_of_analysts_row 는 META 에서 Earnings Estimate(42·41·54·52) 가 아닌 "
    "Revenue Estimate(47·45·56·58) 행을 집었다. avg_estimate_row 는 EPS 값과 정확히 일치하므로 신뢰하나, "
    "분석가 수는 결론에 사용하지 않았다.",
    "collect_yahoo.py 의 error_page 판별이 10/10 True 로 나오지만 표는 정상 파싱됐다. "
    "'Oops, something went wrong' 문자열이 페이지에 상존하기 때문이며 실제 데이터 부재가 아니다.",
    "probe_fy.py 의 EPS 행 추출은 HTML 조각을 잡아 실패했다. FY 라벨 추출만 유효하며, "
    "EPS 값은 카드 파서(eps_this_year_card / eps_next_year_card) 결과를 사용했다. "
    "카드 파서는 meta·alphabet·amazon 의 원문 문맥과 직접 대조해 검증했다.",
]

out = OrderedDict()
out["task"] = "QWEN-NTM-DATA-03"
out["generated_at_utc"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
out["worker_head_at_start"] = "96d88bc97f74914521221de7889544a02048d6da"
out["baseline_reference_date"] = "2026-09-02"
out["contract_source"] = "worker/docs/scorecard/design-guideline.md §5.1 (F6 가격 자동 산출 계약)"
out["contract_verbatim"] = [
    "2. 기준 시점에 이용 가능했던 다음 4개 미발표 회계분기의 EPS 컨센서스를 확보한다. "
    "각 분기의 기간과 추정치 스냅샷 시점을 저장한다.",
    "3. 주가와 EPS의 통화, 보통주/ADR, 분할 조정, GAAP/조정 기준을 맞춘다. "
    "네 분기는 중복 없이 연속해야 한다.",
    "4. `NTM EPS = 네 분기 EPS 합`, `NTM PER = 주가 / NTM EPS`를 계산한다.",
    "가격은 유효한 양수여야 한다. EPS 합이 0 이하이거나 4개 분기·회계 기준·주식 기준이 "
    "확보되지 않으면 점수를 보류한다. 낮은 PER이나 0점으로 대체하지 않는다.",
    "`forwardPE`라는 공급사 필드 이름만으로 NTM임을 인정하지 않는다. 연간 EPS를 가중한 값은 "
    "`annual_weighted_proxy` 등 별도 방법으로 기록하고 참고만 제공한다.",
]
out["scope_note"] = ("대상 10개사(나머지 상장사). TSMC·Alibaba 는 C-13 worktree 의 Antigravity 담당이라 제외. "
                     "이 증거는 '현재(2026-09-08 조회) 공개 접근 가능 자료' 이며, "
                     "2026-09-02 기준 재현 가능성은 각 회사 reproducibility_as_of_baseline 필드로 분리 기록한다.")
out["sources"] = glob["sources_tested"]
out["uniform_findings"] = glob["uniform_findings"]
out["parser_caveats"] = glob["parser_caveats"]

# 2026-09-02 재현 가능성 분리 기록
for row in rows:
    row["reproducibility_as_of_baseline"] = OrderedDict([
        ("current_public_access", True),
        ("reproducible_as_of_2026_09_02", False),
        ("reason", "공급사는 과거 시점의 컨센서스 스냅샷을 무료로 제공하지 않는다. "
                   "현재 조회값은 2026-09-08 기준이며, 2026-09-02 당시 추정치와 다를 수 있다. "
                   "현재 전망치를 과거로 소급해 2026-09-02 값으로 기록하지 않았다."),
        ("observable_drift_example", None),
    ])
    bp = row["baseline_price_2026_09_02"]
    cp = row["value"]["price_usd"]
    if bp and cp:
        row["reproducibility_as_of_baseline"]["observable_drift_example"] = OrderedDict([
            ("metric", "price"),
            ("baseline_2026_09_02", bp), ("observed_2026_09_08", cp),
            ("drift_pct", round((cp - bp) / bp * 100, 3)),
        ])

out["companies"] = rows
out["summary"] = OrderedDict([
    ("total", len(rows)),
    ("확보", len([r for r in rows if r["classification"] == "확보"])),
    ("일부확보", len([r for r in rows if r["classification"] == "일부확보"])),
    ("미확인", len([r for r in rows if r["classification"] == "미확인"])),
    ("대상제외", len([r for r in rows if r["classification"] == "대상제외"])),
    ("forward_pe_period_입증_FY_current", [r["company_id"] for r in rows
                                          if r["period_verdict"]["exact_match_to_this_fy"]]),
    ("forward_pe_period_불명", [r["company_id"] for r in rows
                               if r["period_verdict"]["forward_pe_period"] == "불명(indeterminate)"]),
    ("registry_ticker_결함", [r["company_id"] for r in rows if r["registry_defect"]]),
])

with io.open(os.path.join(HERE, "evidence.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)

print("%-12s %8s %8s %9s %9s %9s %9s %6s %6s %s" % (
    "company", "price", "fwdPE", "impEPS", "epsThisY", "PE@thisY", "PE@nextY", "YfwdQ", "SA Q", "판정"))
for r in rows:
    v, pv, fp = r["value"], r["period_verdict"], r["forecast_period"]
    print("%-12s %8s %8s %9s %9s %9s %9s %6s %6s %s" % (
        r["company_id"], v["price_usd"], v["forward_pe"],
        pv["backcalc_implied_denominator_eps"], fp["stockanalysis_eps_this_year"],
        pv["backcalc_pe_if_this_fy"], pv["backcalc_pe_if_next_fy"],
        fp["yahoo_forward_quarters_free"], fp["stockanalysis_quarterly_labels_in_free_html"],
        pv["forward_pe_period"]))
print()
print("요약:", json.dumps(out["summary"], ensure_ascii=False))
print("\nevidence.json 최종 저장 완료 (%d 회사)" % len(rows))
