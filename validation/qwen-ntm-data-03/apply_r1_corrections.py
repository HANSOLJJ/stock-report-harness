"""QWEN-NTM-DATA-03-R1 정정: '남은 개월수' 논리를 폐기하고 '다음 4개 미발표 회계분기' 기준으로 교체한다.

재검토 보완 요청 msg_2463526bb807 이 지적한 오류를 정정한다.

철회하는 논리:
  - 설계 지침 §5.1 의 요건은 '오늘부터 12개월' 이 아니라 '다음 4개 미발표 회계분기' 다.
    따라서 '회계연도 종료까지 남은 개월수가 12 미만' 은 비NTM 증명이 아니다.
  - '주가 / Forward PE 역산값이 연간 EPS 와 숫자로 일치한다' 는 것은 공급사의 공식
    산출방법 입증이 아니다. 연간 EPS 평균은 분기별 평균의 합과 표본·주식수·조정
    차이로 달라질 수 있다.
  - Current Qtr. 를 회계연도 1분기로 일반화하지 않는다. 공식 회계기간·공식 발표일만 쓴다.

정정 후 판정: 10개사 전부 period_unknown (NTM 적격 미검증).
"""
import io
import json
import os
from collections import OrderedDict
from datetime import date, datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
load = lambda n: json.load(io.open(os.path.join(HERE, n), encoding="utf-8"))

BASELINE_REF = date(2026, 9, 2)
QUERY_DATE = date(2026, 9, 8)

# ---------------------------------------------------------------------------
# 공식 근거로 회계기간이 확정된 회사만 기록한다.
# 공식 근거가 없는 회사는 추론하지 않고 official_evidence=None 으로 둔다.
# ---------------------------------------------------------------------------
OFFICIAL = {
    "microsoft": OrderedDict([
        ("fy_end_month", "6월 30일"),
        ("last_reported_quarter", "FY2026 Q4 (회계기간말 2026-06-30)"),
        ("last_report_announce_date", "2026-07-29"),
        ("official_source", "https://www.microsoft.com/en-us/Investor/earnings/FY-2026-Q4/press-release-webcast"),
        ("official_source_title", "Microsoft Cloud and AI Strength Fuels Fourth Quarter Results"),
        ("official_source_verified_by_me", True),
        ("official_source_http", "200 OK, 810,645 bytes, 조회 2026-09-08"),
        ("next_4_unreported_quarters", ["FY27 Q1 (2026-09 말)", "FY27 Q2 (2026-12 말)",
                                        "FY27 Q3 (2027-03 말)", "FY27 Q4 (2027-06 말)"]),
        ("next_4_window_equals_fy2027", True),
        ("note", "9월 초 기준 마지막 발표 분기가 FY26Q4(2026-06-30 말) 이므로, 다음 미발표 네 분기는 "
                 "FY27 Q1~Q4 다. 이 창은 FY2027 전체와 기간이 같다. 따라서 'FY2027 은 9.82개월 뒤 "
                 "종료이므로 NTM 이 아니다' 라는 기존 논거는 성립하지 않으며 철회한다."),
    ]),
    "oracle": OrderedDict([
        ("fy_end_month", "5월 31일"),
        ("last_reported_quarter", "FY2026 Q4 (회계기간말 2026-05-31) — 기준일 2026-09-02 시점"),
        ("next_announce_date", "2026-09-10 (FY2027 Q1, 회계기간말 2026-08-31)"),
        ("official_source", "https://investor.oracle.com/investor-news/news-details/2026/"
                            "Oracle-Sets-the-Date-for-its-First-Quarter-Fiscal-Year-2027-Earnings-Announcement/default.aspx"),
        ("official_source_verified_by_me", False),
        ("official_source_http", "403 Forbidden — 내가 직접 확인하지 못했다. "
                                 "재검토 요청자(설계진행)가 공식 근거로 제시한 값을 채택한다."),
        ("corroborating_evidence", "Yahoo Finance ORCL analysis 의 Earnings History 기간말 "
                                   "8/31/2025 · 11/30/2025 · 2/28/2026 · 5/31/2026 (내가 직접 수집, HTTP 200) "
                                   "→ 회계연도 5월 31일 종료와 분기말 8·11·2·5월을 독립 확인"),
        ("next_4_unreported_quarters", ["FY27 Q1 (2026-08-31 말, 발표 2026-09-10)",
                                        "FY27 Q2 (2026-11-30 말)", "FY27 Q3 (2027-02-28 말)",
                                        "FY27 Q4 (2027-05-31 말)"]),
        ("next_4_window_equals_fy2027", True),
        ("note", "기준일 2026-09-02 에 FY27Q1(2026-08-31 말) 은 아직 미발표(발표일 2026-09-10) 였다. "
                 "따라서 다음 미발표 네 분기는 2026-08, 2026-11, 2027-02, 2027-05 이고 이 창은 FY2027 과 같다. "
                 "'FY2027 은 8.84개월 뒤 종료이므로 NTM 이 아니다' 라는 기존 논거는 성립하지 않으며 철회한다."),
    ]),
    "spacex-xai": OrderedDict([
        ("listing_primary_source", "https://www.nasdaq.com/newsroom/spacex-ipo-rocket-company-launches-historic-ipo"),
        ("listing_primary_source_verified_by_me", True),
        ("listing_primary_http", "200 OK, 172,955 bytes, 조회 2026-09-08, 기사 시각 'Jun 12, 2026 10:15AM EDT'"),
        ("ticker", "SPCX"),
        ("exchange", "Nasdaq Stock Market (+ Nasdaq Texas 이중상장)"),
        ("trading_start", "2026-06-12 (Friday)"),
        ("open_price_usd", 150.0),
        ("ipo_price_usd", 135.0),
        ("raised_usd", "75 billion"),
        ("implied_valuation_usd", "약 1.77 trillion (Nasdaq 기사 기재)"),
        ("verbatim", [
            "SpaceX (SPCX): Rocket Company Launches Historic IPO",
            "SpaceX (SPCX) opened trading on the Nasdaq Stock Market on Friday at $150 per share",
            "Simultaneous to its IPO on the Nasdaq exchange, SpaceX is also dual-listing on Nasdaq Texas",
            "marking an 11% increase over its IPO price of $135 and completing the most anticipated and "
            "largest initial public offering in Wall Street history",
            "raised a historic $75 billion, resulting in an unprecedented implied valuation of "
            "approximately $1.77 trillion",
        ]),
        ("demoted_source", "Wikipedia SpaceX infobox (Type: Public, Traded as: Nasdaq: SPCX (Class A)) 와 "
                           "XAI_(company) infobox (Type: Subsidiary, Parent: SpaceX) 는 1차 근거에서 내리고 "
                           "보조 근거로 보존한다. 재검토 요청에 따른 근거 위계 정정."),
        ("valuation_note", "Nasdaq 기사의 implied valuation 약 $1.77T 는 IPO 개시가 $150 기준이고, "
                           "기준선 원본 HTML 의 시총 $1.91T 는 StockAnalysis Shares Out 13.57B × $140.71 "
                           "= $1.909T 와 일치한다. 두 값은 기준 주가·주식수가 다르므로 모순이 아니다. "
                           "이번 정정 범위(회계기간·근거 위계) 밖이므로 대조만 기록한다."),
    ]),
}

# ---------------------------------------------------------------------------
# evidence.json 정정
# ---------------------------------------------------------------------------
ev = load("evidence.json")

RETRACTED = [
    "N-04: 'microsoft·oracle 의 Forward PE 분모는 이번 회계연도 EPS 임이 수치로 입증됐고 그 회계연도는 "
    "9.82·8.84개월 뒤 종료 → NTM 아님' — 철회. §5.1 의 요건은 오늘부터 12개월이 아니라 다음 4개 미발표 "
    "회계분기이며, 공식 발표일 기준으로 두 기업의 다음 미발표 네 분기 창은 각각 FY2027 과 기간이 같다. "
    "또한 역산값과 연간 EPS 의 숫자 일치는 공급사 공식 산출방법의 입증이 아니다.",
    "N-06: '10개사 전부 이번 회계연도 종료가 12개월 미만 → EPS This Year 는 구조적으로 NTM 분모 불가' — 철회. "
    "회계연도 말일까지의 남은 개월수는 §5.1 요건과 다른 척도다. 다음 미발표 네 분기가 회계연도와 일치하는 "
    "경우(microsoft·oracle 이 공식 근거로 확인된 사례) 남은 개월수가 12 미만이어도 창은 같다.",
    "N-07: '비역년 회계라 연간 EPS 가중 근사를 NTM 으로 쓰면 이 3사에서 오차가 가장 커진다' — 철회. "
    "실제 4분기 컨센서스와의 비교 없이 오차 크기를 주장할 수 없다. 그런 비교는 이번 조사에서 수행하지 않았다.",
    "§4 의 'StockAnalysis 정의 문서 부재' 주장 축소 — /glossary/ 와 /about/data/ 의 404 는 내가 시험한 두 "
    "후보 경로가 없다는 뜻이지 정의 문서 전체의 부재를 증명하지 않는다.",
    "§4 의 '분기 EPS 무료 공개 불가' 주장 축소 — 정적 HTML 에 분기 라벨이 0건인 것은 정적 GET 경로에서 "
    "분기를 못 얻는다는 뜻이지, 브라우저의 무료 분기 뷰가 불가능하다는 증명이 아니다.",
    "§4 의 유료 티어 관련 '분기 EPS 를 주는지 확인 불가' 문구를 정정 — 조사하지 않은 티어에 대해 불가능이나 "
    "가능을 단정하지 않는다. Pro 가격 페이지에 추정치 데이터 추가 항목이 보이지 않았다는 관찰만 남긴다.",
    "derive_fy_end.py 의 'Current Qtr. = 회계연도 1분기' 가정 — 폐기. 이 가정은 역년·비역년 구분 없이 "
    "성립하지 않으며, 자체 검증(10건 중 3건만 Yahoo 연도 라벨과 일치, nvidia 는 연도만 우연히 일치한 오탐) "
    "에서 결함이 드러났다. 이 스크립트의 출력(fy-end-derived.json) 은 어떤 결론에도 쓰지 않는다.",
    "probe_period_end.py — 실행하지 않고 폐기. 회계연도 추론 범위를 늘리지 말라는 재검토 지시에 따라 "
    "공식 회계기간·발표일만 사용한다.",
]

now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
for rec in ev["companies"]:
    cid = rec["company_id"]
    off = OFFICIAL.get(cid)
    pv = rec.get("period_verdict") or {}
    pv["forward_pe_period"] = "period_unknown"
    pv["is_ntm_proven"] = False
    pv["is_not_ntm_proven"] = False
    pv["ntm_eligibility"] = "unverified"
    pv["exact_match_to_this_fy"] = None
    pv["exact_match_to_next_fy"] = None
    pv["retracted_verdict_2026_09_08"] = (
        "이전 판정 'FY-current(입증)' 은 철회됐다. 근거: (a) §5.1 요건은 다음 4개 미발표 회계분기이며 "
        "남은 개월수가 아니다. (b) 역산값과 연간 EPS 의 숫자 일치는 공급사 공식 산출방법 입증이 아니며, "
        "연간 EPS 평균은 분기별 평균의 합과 표본·주식수·조정 차이로 달라질 수 있다."
        if cid in ("microsoft", "oracle") else
        "이전 판정 '불명(indeterminate)' 은 유지되나 근거 문구를 정정했다: 정의 문서 후보 2건의 404 는 "
        "문서 전체 부재의 증명이 아니고, 정적 HTML 0분기는 브라우저 무료 분기 뷰 불가의 증명이 아니다."
    )
    pv["reason"] = [
        "공급사가 Forward PE 의 분모 기간을 공개 문서로 정의하지 않았다(내가 시험한 경로 기준).",
        "각주 'EPS and Forward PE are based on non-GAAP adjusted numbers.' 는 회계 기준만 밝히고 기간은 밝히지 않는다.",
        "설계 지침 §5.1: 'forwardPE 라는 공급사 필드 이름만으로 NTM임을 인정하지 않는다'.",
        "주가/PER 역산은 참고 계산일 뿐 분모 기간의 증명이 될 수 없다(작업 지시 및 재검토 요청).",
        "연간 EPS 평균은 분기별 평균의 합과 표본·주식수·조정 차이로 달라질 수 있으므로, "
        "역산값과 연간값의 일치는 산출방법 동일성을 의미하지 않는다.",
        "§5.1 이 요구하는 '다음 4개 미발표 회계분기 EPS 컨센서스' 를 확보하지 못했다. "
        "확보하지 못한 상태에서 기간 적격 여부를 긍정도 부정도 할 수 없다.",
    ]
    pv["official_fiscal_period_evidence"] = off if (off and "fy_end_month" in off) else None
    pv["next_4_unreported_quarters_known"] = bool(off and off.get("next_4_unreported_quarters"))
    rec["period_verdict"] = pv
    rec["classification"] = "일부확보"
    rec["classification_reason"] = (
        "유효 양수 주가·향후 2개 분기 EPS·이번/다음 회계연도 EPS·non-GAAP 기준·USD 통화는 확보했으나, "
        "§5.1 이 요구하는 '다음 4개 미발표 회계분기 EPS 컨센서스' 는 확보하지 못했다. "
        "따라서 NTM 적격 여부는 미검증(unverified) 이다 — NTM 이라고도 NTM 이 아니라고도 판정하지 않는다."
    )
    if cid == "spacex-xai":
        rec["listing_evidence"] = OFFICIAL["spacex-xai"]

ev["revisions"] = OrderedDict([
    ("revision_id", "QWEN-NTM-DATA-03-R1"),
    ("requested_by", "msg_2463526bb807 (설계진행, term_a3370266-4d39-4c5c-95a7-38ce1a1b744c)"),
    ("acknowledged_by", "msg_290a1edb780a"),
    ("revised_at_utc", now),
    ("scope", "오류 정정에 한정. 재조사 범위 확장 없음. 원본 스냅샷 보존. worker 읽기 전용. 점수·정책 변경 없음."),
    ("verdict_change", "microsoft·oracle 의 'FY-current(입증)' → 'period_unknown'. 나머지 8개사는 '불명' 유지. "
                       "10개사 전부 NTM 적격 미검증(unverified)."),
    ("retracted_claims", RETRACTED),
    ("official_sources_added", [
        OrderedDict([("company", "microsoft"),
                     ("url", OFFICIAL["microsoft"]["official_source"]),
                     ("verified_by_me", True), ("http", "200 OK")]),
        OrderedDict([("company", "oracle"),
                     ("url", OFFICIAL["oracle"]["official_source"]),
                     ("verified_by_me", False),
                     ("http", "403 Forbidden — 재검토 요청자의 공식 근거 인용을 채택")]),
        OrderedDict([("company", "spacex-xai"),
                     ("url", OFFICIAL["spacex-xai"]["listing_primary_source"]),
                     ("verified_by_me", True), ("http", "200 OK")]),
    ]),
])
ev["summary"] = OrderedDict([
    ("total", len(ev["companies"])),
    ("확보", 0), ("일부확보", len(ev["companies"])), ("미확인", 0), ("대상제외", 0),
    ("ntm_eligibility", "10개사 전부 unverified"),
    ("forward_pe_period", "10개사 전부 period_unknown"),
    ("registry_ticker_결함", [r["company_id"] for r in ev["companies"] if r.get("registry_defect")]),
    ("official_fiscal_period_evidence_확보", [c for c in OFFICIAL if "fy_end_month" in OFFICIAL[c]]),
])

with io.open(os.path.join(HERE, "evidence.json"), "w", encoding="utf-8") as f:
    json.dump(ev, f, ensure_ascii=False, indent=1)

# ---------------------------------------------------------------------------
# 정정된 분석 결과 파일 (잘못된 개월수 논리를 제거)
# ---------------------------------------------------------------------------
out = OrderedDict([
    ("revision_id", "QWEN-NTM-DATA-03-R1"),
    ("generated_at_utc", now),
    ("supersedes", "fy-analysis.json 의 months_price_date_to_fy_end 논리와 "
                   "current_fy_shorter_than_12m 판정, fy-end-derived.json 전체"),
    ("contract_requirement_verbatim",
     "설계 지침 §5.1 2항: '기준 시점에 이용 가능했던 다음 4개 미발표 회계분기의 EPS 컨센서스를 확보한다. "
     "각 분기의 기간과 추정치 스냅샷 시점을 저장한다.'"),
    ("rejected_metric", "회계연도 말일까지의 남은 개월수 — §5.1 요건과 다른 척도이므로 판정에 쓰지 않는다."),
    ("rejected_inference", "Current Qtr. 를 회계연도 1분기로 일반화하는 유도 — 폐기."),
    ("companies", OrderedDict()),
])
for rec in ev["companies"]:
    cid = rec["company_id"]
    off = OFFICIAL.get(cid)
    out["companies"][cid] = OrderedDict([
        ("forward_pe_period", "period_unknown"),
        ("ntm_eligibility", "unverified"),
        ("official_fiscal_period_evidence", bool(off and "fy_end_month" in off)),
        ("next_4_unreported_quarters", (off or {}).get("next_4_unreported_quarters")),
        ("next_4_window_equals_current_fy", (off or {}).get("next_4_window_equals_fy2027")),
        ("quarterly_eps_obtained", 0),
        ("quarterly_eps_required", 4),
        ("satisfied", False),
        ("backcalc_reference_only",
         (rec.get("period_verdict") or {}).get("backcalc_implied_denominator_eps")),
    ])

with io.open(os.path.join(HERE, "fy-analysis-corrected.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)

print("=" * 88)
print("정정 완료 (QWEN-NTM-DATA-03-R1)")
print("=" * 88)
print("판정 변경: microsoft·oracle 'FY-current(입증)' → 'period_unknown'")
print("          나머지 8개사 '불명' → 'period_unknown' (용어 통일)")
print("          10개사 전부 NTM 적격 = unverified")
print()
print("공식 근거로 회계기간이 확정된 회사:")
for cid in ("microsoft", "oracle"):
    o = OFFICIAL[cid]
    print("  %-10s 회계연도 말=%s  마지막 발표=%s" % (cid, o["fy_end_month"],
          o.get("last_report_announce_date") or o.get("next_announce_date")))
    print("             다음 미발표 4분기 = %s" % ", ".join(o["next_4_unreported_quarters"]))
    print("             그 창이 회계연도와 같은가 = %s" % o["next_4_window_equals_fy2027"])
    print("             공식 URL 직접 확인 = %s (%s)" % (o["official_source_verified_by_me"],
                                                        o["official_source_http"]))
print()
print("SpaceX 1차 근거 교체:")
o = OFFICIAL["spacex-xai"]
print("  1차: %s" % o["listing_primary_source"])
print("       직접 확인 = %s (%s)" % (o["listing_primary_source_verified_by_me"], o["listing_primary_http"]))
print("       SPCX / %s / 거래개시 %s / 개시가 $%s / IPO가 $%s" % (
    o["exchange"], o["trading_start"], o["open_price_usd"], o["ipo_price_usd"]))
print("  보조로 강등: %s" % o["demoted_source"][:60])
print()
print("철회한 주장 %d건:" % len(RETRACTED))
for i, r in enumerate(RETRACTED, 1):
    print("  %d. %s" % (i, r[:120]))
print()
print("저장: evidence.json (정정), fy-analysis-corrected.json (신규)")
print("보존: fy-analysis.json, fy-end-derived.json (폐기 대상이나 감사 추적을 위해 원본 보존)")
