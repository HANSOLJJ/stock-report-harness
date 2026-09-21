# evidence.json 을 원문 스냅샷과 대조해 검증한다. 채점하지 않고 검증 결과만 남긴다.
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw")

fails = []
warns = []
lines = []


def ck(cond, msg, warn=False):
    if cond:
        lines.append("  PASS  %s" % msg)
    else:
        (warns if warn else fails).append(msg)
        lines.append("  %s  %s" % ("WARN", msg) if warn else "  FAIL  %s" % msg)
    return cond


ev = json.load(io.open(os.path.join(HERE, "evidence.json"), encoding="utf-8"))
lines.append("검증 대상: evidence.json  기업 %d개  기준일 %s" % (len(ev["companies"]), ev["reference_date"]))

for c in ev["companies"]:
    cid = c["company_id"]
    lines.append("\n== %s (%s)" % (cid, c["ticker"]))
    nq = c["sources"]["nasdaq_api"]
    obs = nq["observations"]

    # 1) evidence 의 값이 원문 스냅샷과 같은가 (재파싱 대조)
    fn = os.path.join(RAW, "nasdaq-%s-earnings_forecast.json" % cid)
    src = json.load(io.open(fn, encoding="utf-8"))
    rows = {r["fiscalEnd"]: r for r in src["data"]["quarterlyForecast"]["rows"]}
    same = all(
        rows.get(o["period_label_vendor"], {}).get("consensusEPSForecast") == o["mean"]
        and rows.get(o["period_label_vendor"], {}).get("lowEPSForecast") == o["min"]
        and rows.get(o["period_label_vendor"], {}).get("highEPSForecast") == o["max"]
        and rows.get(o["period_label_vendor"], {}).get("noOfEstimates") == o["estimate_count"]
        for o in obs)
    ck(same, "%s: evidence 4분기 값이 원문 스냅샷과 일치" % cid)

    # 2) 4분기 확보
    ck(len(obs) == 4, "%s: 다음 4개 미발표 분기 EPS 평균 4/4 확보" % cid)

    # 3) 두 Nasdaq 엔드포인트 교차 일치
    ck(c["checks"]["nasdaq_two_endpoints_agree_on_next4_labels"],
       "%s: earnings-forecast 와 /eps 의 미발표 4분기 라벨 일치" % cid)
    ck(c["checks"]["nasdaq_two_endpoints_agree_on_means"],
       "%s: 두 엔드포인트의 분기 평균 일치" % cid)

    # 4) 통계 정합성
    ck(c["checks"]["min_le_mean_le_max_all_quarters"], "%s: 모든 분기에서 최소<=평균<=최대" % cid)
    ck(c["checks"]["estimate_count_positive_all_quarters"], "%s: 모든 분기 전망치 수 > 0" % cid)

    # 5) 분기 연속성 (중복 없음, 3개월 간격)
    labs = [o["period_label_vendor"] for o in obs]
    ck(len(set(labs)) == 4, "%s: 4개 분기 라벨 중복 없음 (%s)" % (cid, ", ".join(labs)))
    M = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    idx = [int(l.split()[1]) * 12 + M.index(l.split()[0]) for l in labs]
    ck(all(idx[i + 1] - idx[i] == 3 for i in range(3)),
       "%s: 4개 분기가 3개월 간격으로 연속" % cid)

    # 6) 미발표 창의 시작이 기준일 이후 발표인가
    tv = c["sources"]["tradingview"]
    ck(tv.get("next_release_utc") is not None and tv["next_release_utc"] >= ev["reference_date"],
       "%s: 독립 원천 기준 다음 실적 발표일(%s)이 기준일 이후" % (cid, tv.get("next_release_utc")))

    # 7) 마지막 발표 분기의 '기간'이 원천 간 같은가 (값이 아니라 기간 정합성이 검증 대상)
    bd = c["basis_divergence_last_reported_quarter"]
    ck(c["checks"]["last_reported_period_matches_across_sources"],
       "%s: 마지막 발표 분기 기간이 원천 간 일치 (Nasdaq %s / SA %s / TV %s)" % (
           cid, bd["period_label_nasdaq"], bd["period_end_stockanalysis"], bd["period_end_tradingview"]))

    # 7b) 같은 기간의 확정 실적값이 원천 간 같은가 — 다르면 회계 기준 차이 진단으로 기록한다
    if not bd["vendors_agree_within_0_01"]:
        warns.append(
            "%s: 같은 마지막 발표 분기(%s) 확정 EPS 가 원천 간 %s 차이 — Nasdaq %s / TV %s / SA조정 %s / SA GAAP열 %s"
            % (cid, bd["period_label_nasdaq"], bd["max_abs_gap"], bd["actual_eps_nasdaq"],
               bd["actual_eps_tradingview"], bd["actual_eps_stockanalysis_adjusted"],
               bd["actual_eps_stockanalysis_gaap_column"]))
        lines.append("  DIAG  %s: 확정 실적 EPS 원천 간 불일치 %s (조정 정의 상이) — 원천 대체·혼합 금지 근거"
                     % (cid, bd["max_abs_gap"]))
    else:
        lines.append("  PASS  %s: 같은 분기 확정 실적 EPS 가 원천 간 일치 (%s)" % (cid, bd["actual_eps_nasdaq"]))

    # 8) 합계 재계산
    s = round(sum(o["mean"] for o in obs), 4)
    ck(abs(s - nq["mean_sum_4q"]) < 1e-9, "%s: 4분기 평균 합 재계산 일치 (%s)" % (cid, s))

    # 9) EPS 합 양수 여부 (음수/0 도 유효 관측이므로 보류 사유로만 기록)
    if not c["checks"]["sum_4q_mean_positive"]:
        warns.append("%s: 4분기 평균 합이 0 이하 — 채점 보류 사유이며 자료 미확보가 아님" % cid)
        lines.append("  WARN  %s: 4분기 평균 합 %s <= 0" % (cid, s))

    # 10) 공급사 간 1분기 격차
    sp = c["checks"]["q1_vendor_spread"]
    if sp.get("max_rel_gap_vs_nasdaq_pct") is not None and sp["max_rel_gap_vs_nasdaq_pct"] > 10:
        warns.append("%s: 1분기 평균의 공급사 간 상대격차 %.2f%% — 원천 혼합 금지 근거" % (
            cid, sp["max_rel_gap_vs_nasdaq_pct"]))
        lines.append("  WARN  %s: 1분기 공급사 격차 %.2f%% (nasdaq=%s, sa=%s, yahoo=%s, tv=%s)" % (
            cid, sp["max_rel_gap_vs_nasdaq_pct"], sp["nasdaq"], sp["stockanalysis"],
            sp["yahoo_2026_09_08"], sp["tradingview"]))

    # 11) 미검증 항목이 명시돼 있는가
    ck(c["scoring_eligibility"]["usable_for_automatic_scoring"] is False
       and len(c["scoring_eligibility"]["reasons"]) >= 3,
       "%s: 채점 적격성 미검증 사유가 기록됨" % cid)

    # 12) 상장 확인
    ck(c["listing"]["exchange"] is not None and c["listing"]["last_sale_price"] is not None,
       "%s: 기준시점 상장·거래 확인 (%s, %s)" % (
           cid, c["listing"]["exchange"], c["listing"]["last_sale_price"]))

lines.append("\n" + "=" * 60)
lines.append("FAIL %d건 / WARN %d건" % (len(fails), len(warns)))
for f in fails:
    lines.append("  FAIL: %s" % f)
for w in warns:
    lines.append("  WARN: %s" % w)

txt = "\n".join(lines)
io.open(os.path.join(HERE, "verify-output.txt"), "w", encoding="utf-8").write(txt)
print(txt)
