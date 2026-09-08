"""QWEN-NTM-DATA-03: 저장된 원문 HTML 에서 evidence.json 을 보정·완성한다.

collect_ntm.py 가 받아 둔 raw-*.html 을 다시 파싱하므로 조회시각이 그대로 보존된다.
주가 추출 패턴을 실제 DOM(text-4xl font-bold) 에 맞게 고치고, 추정치 개정 이력(from 값)과
증감 배지 색, 분기 라벨 부재 여부를 함께 기록한다.
"""
import io
import json
import os
import re
from collections import OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
NUM = r"([-+]?\d[\d,]*\.?\d*)"


def read(name):
    p = os.path.join(HERE, name)
    return io.open(p, encoding="utf-8").read() if os.path.isfile(p) else None


def strip_tags(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s)).strip()


def price_from_overview(html):
    m = re.search(r'text-4xl font-bold[^"]*"[^>]*>\s*' + NUM, html)
    if m:
        return float(m.group(1).replace(",", ""))
    m = re.search(r'text-4xl font-bold[^>]*>\s*\$?\s*' + NUM, html)
    return float(m.group(1).replace(",", "")) if m else None


def price_date_from_overview(html):
    m = re.search(r"At close:\s*</span>\s*([^<]{4,45})", html)
    return m.group(1).strip() if m else None


def change_from_overview(html):
    m = re.search(r'font-semibold block text-lg[^"]*"[^>]*>\s*([-+][\d.]+)\s*\(([-+][\d.]+)%\)', html)
    return {"change": m.group(1), "change_pct": m.group(2)} if m else None


def label_after(html, label, window=900):
    i = html.find(label)
    if i < 0:
        return None
    seg = html[i + len(label): i + len(label) + window]
    m = re.search(r">\s*" + NUM + r"\s*(?:<|\s)", seg)
    return m.group(1).replace(",", "") if m else None


def eps_card(html, label):
    """EPS This/Next Year 카드에서 값·직전값(from)·배지 색을 함께 뽑는다."""
    i = html.find(">%s</div>" % label)
    if i < 0:
        return None
    seg = html[i: i + 1400]
    val = re.search(r"text-2xl font-semibold[^>]*>\s*" + NUM, seg)
    frm = re.search(r"lg:hidden\">\s*from\s*" + NUM, seg)
    badge = "decline" if "bg-red-100" in seg else ("growth" if "bg-green-100" in seg else None)
    out = OrderedDict()
    out["value"] = float(val.group(1).replace(",", "")) if val else None
    out["revised_from"] = float(frm.group(1).replace(",", "")) if frm else None
    out["badge"] = badge
    return out


def fy_table(html):
    """Financial Forecast 표의 FY 열과 EPS 행 값을 Upgrade 여부 포함으로 뽑는다."""
    fys = re.findall(r"FY\s*(20\d\d)", html)
    seen = []
    for y in fys:
        if y not in seen:
            seen.append(y)
    return seen


def main():
    ev = json.load(io.open(os.path.join(HERE, "evidence.json"), encoding="utf-8"))
    for rec in ev["companies"]:
        cid = rec["company_id"]
        ov = read("raw-%s-overview.html" % cid)
        fc = read("raw-%s-forecast.html" % cid)
        rec["raw_saved"] = {"overview": bool(ov), "forecast": bool(fc)}
        if ov:
            rec["overview"]["price"] = price_from_overview(ov)
            rec["overview"]["price_date_label"] = price_date_from_overview(ov)
            rec["overview"]["change"] = change_from_overview(ov)
            rec["overview"]["price_parse_pattern"] = 'text-4xl font-bold ...">VALUE'
        if fc:
            rec["forecast"]["eps_this_year_card"] = eps_card(fc, "EPS This Year")
            rec["forecast"]["eps_next_year_card"] = eps_card(fc, "EPS Next Year")
            rec["forecast"]["fy_years_in_page"] = fy_table(fc)
            rec["forecast"]["quarter_label_count"] = {
                "Q#_YYYY": len(re.findall(r"\bQ[1-4]\s*20\d\d\b", fc)),
                "Mon_YYYY_or_Mon_'YY": len(re.findall(
                    r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s*'?\d\d\b", fc)),
            }
            rec["forecast"]["quarterly_is_ui_toggle_only"] = (
                rec["forecast"]["quarter_label_count"]["Q#_YYYY"] == 0
                and rec["forecast"].get("has_quarterly_toggle"))
        # 참고 계산 갱신
        price = (rec.get("overview") or {}).get("price")
        fpe = None
        for k in ("forward_pe",):
            v = (rec.get("overview") or {}).get(k)
            try:
                fpe = float(v)
            except (TypeError, ValueError):
                fpe = None
        st = rec.get("statistics") or {}
        try:
            fpe_stat = float(st.get("forward_pe"))
        except (TypeError, ValueError):
            fpe_stat = None
        eps_ttm = None
        try:
            eps_ttm = float((rec.get("overview") or {}).get("eps_ttm"))
        except (TypeError, ValueError):
            pass
        pe_rep = None
        try:
            pe_rep = float((rec.get("overview") or {}).get("pe_ratio"))
        except (TypeError, ValueError):
            pass
        eth = ((rec.get("forecast") or {}).get("eps_this_year_card") or {}).get("value")
        eny = ((rec.get("forecast") or {}).get("eps_next_year_card") or {}).get("value")
        rec["backcalc"] = OrderedDict([
            ("disclaimer", "주가/PER 역산만으로 분모의 기간은 증명되지 않는다(작업 지시·설계 지침 §5.1). "
                           "아래는 참고 계산이며 NTM/FY1 판정의 근거로 쓰지 않는다."),
            ("price", price),
            ("forward_pe_overview", fpe),
            ("forward_pe_statistics", fpe_stat),
            ("implied_denominator_eps_from_statistics",
             round(price / fpe_stat, 4) if (price and fpe_stat) else None),
            ("eps_ttm", eps_ttm),
            ("pe_ratio_reported", pe_rep),
            ("trailing_check_price_div_eps_ttm",
             round(price / eps_ttm, 4) if (price and eps_ttm and eps_ttm > 0) else None),
            ("eps_this_year", eth),
            ("eps_next_year", eny),
            ("pe_if_denominator_is_this_fy", round(price / eth, 4) if (price and eth and eth > 0) else None),
            ("pe_if_denominator_is_next_fy", round(price / eny, 4) if (price and eny and eny > 0) else None),
        ])
        # 기간 판정
        imp = rec["backcalc"]["implied_denominator_eps_from_statistics"]
        verdict = "indeterminate"
        why = []
        if imp and eth:
            why.append("역산 분모 %.4f vs 이번 회계연도 EPS %.2f → PER %.2f (보고 Forward PE %.2f)"
                       % (imp, eth, rec["backcalc"]["pe_if_denominator_is_this_fy"] or 0, fpe_stat or 0))
        if imp and eny:
            why.append("역산 분모 %.4f vs 다음 회계연도 EPS %.2f → PER %.2f"
                       % (imp, eny, rec["backcalc"]["pe_if_denominator_is_next_fy"] or 0))
        why.append("통계 페이지에 Forward PE 기간 정의 문구 없음(실측)")
        why.append("정의 문서 후보 /glossary/ · /about/data/ 모두 404(실측)")
        why.append("각주는 'EPS and Forward PE are based on non-GAAP adjusted numbers.' 로 "
                   "회계 기준만 밝히고 기간은 밝히지 않음")
        rec["period_verdict"] = OrderedDict([
            ("forward_pe_period", verdict),
            ("reason", why),
            ("quarterly_eps_obtainable_free", False),
            ("fy_next_visible_free", None),
        ])
    # FY 다음연도 무료 공개 여부 표기
    for rec in ev["companies"]:
        fc = rec.get("forecast") or {}
        rows = fc.get("fy_rows") or []
        nxt = [r for r in rows if r.get("fy") == "2027"]
        vals = (nxt[0]["first_values"] if nxt else []) or []
        rec["period_verdict"]["fy_next_visible_free"] = not any(
            v in ("Upgrade", "Pro") for v in vals) if vals else False
        rec["period_verdict"]["fy2027_first_values"] = vals[:6]

    with io.open(os.path.join(HERE, "evidence.json"), "w", encoding="utf-8") as f:
        json.dump(ev, f, ensure_ascii=False, indent=1)

    print("%-12s %9s %8s %8s %8s %8s %8s %8s  %s" % (
        "company", "price", "fwdPE", "epsTTM", "epsThisY", "epsNextY",
        "imp EPS", "PE@thisY", "Q라벨/Upgrade"))
    for rec in ev["companies"]:
        b = rec["backcalc"]
        fc = rec.get("forecast") or {}
        print("%-12s %9s %8s %8s %8s %8s %8s %8s  %s/%s" % (
            rec["company_id"], b["price"], b["forward_pe_statistics"], b["eps_ttm"],
            b["eps_this_year"], b["eps_next_year"],
            b["implied_denominator_eps_from_statistics"], b["pe_if_denominator_is_this_fy"],
            (fc.get("quarter_label_count") or {}).get("Q#_YYYY"), fc.get("upgrade_count")))
    print("\nevidence.json 보정 완료")


if __name__ == "__main__":
    main()
