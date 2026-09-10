# F6-FX-16: P3 매출성장률에서 환율이 약분되는지 실제 값으로 검증한다.
# 결론이 아니라 계산으로 보인다. 값은 SEC companyfacts 스냅샷에서만 가져온다.
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))

rates = json.load(io.open(os.path.join(HERE, "implied-rates.json"), encoding="utf-8"))


def growth(a, b):
    return (b / a - 1.0) * 100.0


out = {}
lines = []
for key in ["TSM/Revenue", "BABA/Revenues"]:
    rows = rates[key]
    prev, cur = rows[-2], rows[-1]
    g_local = growth(prev["local_val"], cur["local_val"])
    g_usd = growth(prev["usd_val"], cur["usd_val"])
    r_prev = prev["implied_rate_local_per_usd"]
    r_cur = cur["implied_rate_local_per_usd"]
    fx_move = growth(r_cur, r_prev)  # 현지통화 절상률(= USD 환산 시 가산되는 부분)

    # 같은 환율(최신 기준일 환율)로 두 해를 모두 환산하면?
    usd_prev_same = prev["local_val"] / r_cur
    usd_cur_same = cur["local_val"] / r_cur
    g_usd_same = growth(usd_prev_same, usd_cur_same)

    rec = {
        "prev_period": prev["period"], "cur_period": cur["period"],
        "growth_local_pct": round(g_local, 4),
        "growth_usd_as_filed_pct": round(g_usd, 4),
        "growth_usd_single_rate_pct": round(g_usd_same, 4),
        "rate_prev": r_prev, "rate_cur": r_cur,
        "fx_contribution_pct_points": round(g_usd - g_local, 4),
        "single_rate_equals_local": abs(g_usd_same - g_local) < 1e-6,
    }
    out[key] = rec
    lines.append("=" * 76)
    lines.append("%s   %s -> %s" % (key, prev["period"], cur["period"]))
    lines.append("  현지통화 성장률           %8.3f %%   (환율 무관)" % g_local)
    lines.append("  USD 성장률 (공시값 그대로) %8.3f %%   환율 %.4f -> %.4f" % (g_usd, r_prev, r_cur))
    lines.append("  차이(=환율 기여분)         %8.3f %%p" % (g_usd - g_local))
    lines.append("  USD 성장률 (두 해 모두 %.4f 로 환산) %8.3f %%   현지통화와 일치: %s"
                 % (r_cur, g_usd_same, "예" if rec["single_rate_equals_local"] else "아니오"))

txt = "\n".join(lines)
io.open(os.path.join(HERE, "p3-fx-check.txt"), "w", encoding="utf-8").write(txt)
io.open(os.path.join(HERE, "p3-fx-check.json"), "w", encoding="utf-8").write(
    json.dumps(out, ensure_ascii=False, indent=1))
print(txt)
