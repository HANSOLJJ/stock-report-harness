# G1-FILL-27B: 분기 시계열을 만들고 Q4 를 복원해 TTM 매출·영업손익을 산출한다.
# 규약 1·2·3 을 영업손익에 적용하며 어긋나는 지점을 기록한다.
import datetime as dt
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_ttm import SOURCES, build, days  # noqa: E402

TOL = 0.005  # 복원 Q4 와 공시값 대조 허용 오차(상대)


def inside(fy, q):
    """분기 q 가 회계연도 fy 창 안에 완전히 들어가는가."""
    return fy[0] <= q[0] and q[1] <= fy[1]


def restore_q4(quarters, annuals):
    """규약 2: 최신 회계연도 Q4 는 직접 태깅되지 않으므로 FY - (Q1+Q2+Q3) 로 복원한다.
    복원 결과가 이미 태깅된 분기와 같으면 복원이 아니라 공시값이므로 그렇게 표시한다."""
    restored = {}
    notes = []
    for fy, fyv in sorted(annuals.items()):
        inner = sorted([k for k in quarters if inside(fy, k)])
        if len(inner) == 4:
            s = sum(quarters[k]["val"] for k in inner)
            ok = abs(s - fyv["val"]) <= abs(fyv["val"]) * TOL
            notes.append({"fy": "%s~%s" % fy, "case": "4분기 모두 태깅됨",
                          "sum_quarters": s, "fy_value": fyv["val"], "matches": ok})
            continue
        if len(inner) != 3:
            notes.append({"fy": "%s~%s" % fy, "case": "분기 %d개 — 복원 불가" % len(inner)})
            continue
        s3 = sum(quarters[k]["val"] for k in inner)
        q4_start = inner[-1][1]
        q4_start = (dt.date.fromisoformat(q4_start) + dt.timedelta(days=1)).isoformat()
        q4_key = (q4_start, fy[1])
        val = fyv["val"] - s3
        restored[q4_key] = {
            "val": val, "restored": True,
            "formula": "FY(%s) - (Q1+Q2+Q3)(%s)" % (fyv["val"], s3),
            "fy_period": "%s~%s" % fy, "fy_value": fyv["val"],
            "q123": [{"period": "%s~%s" % k, "val": quarters[k]["val"],
                      "concept": quarters[k]["concept"]} for k in inner],
            "concept": fyv["concept"], "taxonomy": fyv["taxonomy"],
            "source_accn": fyv["accn"], "source_form": fyv["form"],
        }
        notes.append({"fy": "%s~%s" % fy, "case": "Q4 복원", "q4_period": "%s~%s" % q4_key,
                      "q4_value": val})
    return restored, notes


def ttm(quarters, restored, annuals):
    """규약 1: TTM 창의 끝점은 복원 Q4 를 포함한 최신 확보 분기."""
    allq = dict(quarters)
    for k, v in restored.items():
        allq.setdefault(k, v)
    keys = sorted(allq, key=lambda k: k[1])
    if len(keys) < 4:
        return None, {"reason": "분기 %d개 — 4개 미만" % len(keys), "available": len(keys)}
    last4 = keys[-4:]
    # 연속성 확인: 앞 분기 끝 + 1일 == 다음 분기 시작 (±5일 허용, 회계 달력 변동)
    gaps = []
    for a, b in zip(last4, last4[1:]):
        gap = (dt.date.fromisoformat(b[0]) - dt.date.fromisoformat(a[1])).days
        gaps.append(gap)
    contiguous = all(-2 <= g <= 6 for g in gaps)
    total = sum(allq[k]["val"] for k in last4)
    window = (last4[0][0], last4[-1][1])
    span = days(*window)
    # 규약 3의 부수 확인: 이 창이 태깅된 FY 와 같으면 TTM 이 아니라 공시 연간값이다
    equals_fy = None
    for fy, fyv in annuals.items():
        if abs((dt.date.fromisoformat(fy[0]) - dt.date.fromisoformat(window[0])).days) <= 10 and \
           abs((dt.date.fromisoformat(fy[1]) - dt.date.fromisoformat(window[1])).days) <= 10:
            match = abs(total - fyv["val"]) <= abs(fyv["val"]) * TOL
            equals_fy = {"fy_period": "%s~%s" % fy, "fy_value": fyv["val"],
                         "ttm_sum": total, "matches": match}
            break
    return {
        "window_start": window[0], "window_end": window[1], "span_days": span,
        "value": total, "contiguous": contiguous, "gaps_days": gaps,
        "quarters": [{"period": "%s~%s" % k, "val": allq[k]["val"],
                      "restored": bool(allq[k].get("restored")),
                      "concept": allq[k].get("concept")} for k in last4],
        "equals_tagged_fy": equals_fy,
    }, None


def run(cid):
    rec, s = build(cid)
    out = dict(rec)
    res = {}
    for label, q, a in (("revenue", s["rq"], s["ra"]), ("operating", s["oq"], s["oa"])):
        restored, notes = restore_q4(q, a)
        t, err = ttm(q, restored, a)
        res[label] = {"restored_q4": {("%s~%s" % k): v for k, v in restored.items()},
                      "restore_notes": notes, "ttm": t, "error": err,
                      "quarterly_count": len(q), "annual_count": len(a)}
    out["result"] = res
    # 영업이익률
    tr = (res["revenue"].get("ttm") or {})
    to = (res["operating"].get("ttm") or {})
    if tr and to and tr.get("value") and to.get("value") is not None:
        same = (tr["window_start"] == to["window_start"] and tr["window_end"] == to["window_end"])
        out["operating_margin_ttm"] = (to["value"] / tr["value"]) if same else None
        out["margin_window_aligned"] = same
    else:
        out["operating_margin_ttm"] = None
        out["margin_window_aligned"] = None
    return out


if __name__ == "__main__":
    allout = {}
    print("%-12s %-5s %-24s %-16s %-16s %-9s %-6s" % (
        "company", "통화", "TTM 창", "TTM 매출", "TTM 영업손익", "영업이익률", "창일치"))
    print("-" * 110)
    for cid in SOURCES:
        o = run(cid)
        allout[cid] = o
        tr = (o["result"]["revenue"].get("ttm") or {})
        to = (o["result"]["operating"].get("ttm") or {})
        win = ("%s~%s" % (tr.get("window_start"), tr.get("window_end"))) if tr else "-"
        m = o["operating_margin_ttm"]
        print("%-12s %-5s %-24s %-16s %-16s %-9s %-6s" % (
            cid, o["currency"], win,
            "{:,}".format(tr["value"]) if tr else "불가",
            "{:,}".format(to["value"]) if to else "불가",
            ("%.4f%%" % (m * 100)) if m is not None else "-",
            str(o["margin_window_aligned"])))
    io.open(os.path.join(HERE, "ttm-result.json"), "w", encoding="utf-8").write(
        json.dumps(allout, ensure_ascii=False, indent=1, default=str))
    print("\nsaved ttm-result.json")
