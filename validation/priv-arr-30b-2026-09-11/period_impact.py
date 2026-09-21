# PRIV-ARR-30B: 기간 라벨이 P3(직전 대비 arr 증가율)에 미치는 영향을 실측한다.
# 원문이 밝힌 시점만 쓰고, 추정은 추정이라고 표시해 분리한다.
import io
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
E = json.load(io.open(os.path.join(HERE, "priv-arr-extract.json"), encoding="utf-8"))["extracted"]

print("=" * 100)
print("1. P3 = 직전 대비 arr 증가율 — 원문 값 그대로")
print("=" * 100)
rows = []
for cid in ("anthropic", "openai"):
    a, p = E[cid]["arr"], E[cid]["arr_prior"]
    g = a["value"] / p["value"] - 1
    rows.append((cid, p["value"], a["value"], g, p["period_label"], a["period_label"]))
    print("   %-9s %s → %s  =  %+.1f%%" % (
        cid, "{:,.0f}".format(p["value"]), "{:,.0f}".format(a["value"]), g * 100))
    print("   %-9s 직전 시점: %s" % ("", p["period_label"] or "★원문이 밝히지 않음"))
    print("   %-9s 현재 시점: %s" % ("", a["period_label"]))
    print()

print("   ⚠ 두 증가율은 같은 기간의 것이 아니다. 직접 비교하면 안 된다.")
print("     anthropic 은 직전 시점이 없어 기간 자체를 알 수 없고,")
print("     openai 는 정체 구간(2~4월)이라 시작점이 한 점이 아니다.")

print()
print("=" * 100)
print("2. 원문의 월증가율 서술과 대조 — 같은 원문 안에서 앞뒤가 맞는가")
print("=" * 100)
# 원문 서술: anthropic 약 +14%/월 (5월중순~7월말), openai +20%/월 (7월 복귀)
for cid, mom, span_note in (("anthropic", 0.14, "5월중순~7월말"), ("openai", 0.20, "7월 MoM 복귀")):
    a, p = E[cid]["arr"], E[cid]["arr_prior"]
    ratio = a["value"] / p["value"]
    months = math.log(ratio) / math.log(1 + mom)
    print("   %-9s %s→%s 를 월 %+.0f%% 로 채우면 %.2f 개월치 (원문 서술 구간: %s)" % (
        cid, p["raw"], a["raw"], mom * 100, months, span_note))
print()
print("   ★ 위 개월수는 내 역산이지 원문 진술이 아니다. 관측에 넣지 않는다.")
print("     anthropic 이 약 2.5개월로 나오는 것은 '5월중순~7월말'(약 2.5개월) 과 부합하나,")
print("     원문이 $47B 에 시점을 붙이지 않았으므로 추정으로 채우지 않는다.")

print()
print("=" * 100)
print("3. openai arr 시점이 7월이냐 8/20 이냐 — 원문이 둘 다 쓴다")
print("=" * 100)
for c in E["openai"]["arr"]["cites"]:
    print("   L%-5d %s" % (c["line"], c["text"][:150]))
print()
print("   기존 관측 raw 는 '런레이트 $40B+(8/20)' 로 8/20 을 골랐다(L917 표현).")
print("   그러나 증가율 서술(L165·L745)은 7월 기준이다. P3 를 쓰려면 어느 쪽인지 정해야 한다.")
print("   값은 $40B 로 같으므로 값이 아니라 기간 라벨만의 문제다.")

print()
print("=" * 100)
print("4. openai cumulative_raised — 원문은 범위, 기존 관측은 중간값")
print("=" * 100)
cr = E["openai"]["cumulative_raised"]
print("   원문      : %s (단일값 아님, 시점 라벨 없음)" % cr["raw"])
print("   기존 관측 : 185,000,000,000  raw='약 $180~190B(중간값)'")
print("   → 중간값 185B 는 원문에 없는 유도값이다. raw 에 '(중간값)' 으로 표시는 돼 있다.")
p4 = [(40e9 / x, x) for x in (180e9, 185e9, 190e9)]
print("   P4(자본효율 = arr ÷ cumulative_raised) 범위:")
for v, x in p4:
    print("      %s → %.4f" % ("{:,.0f}".format(x), v))
print("   폭 %.4f (원문 표기 0.22 와 대조)" % (p4[0][0] - p4[2][0]))
print("   anthropic: %.4f (원문 표기 0.52)" % (65e9 / 125e9))

out = {"p3_rows": [{"company_id": c, "arr_prior": pv, "arr": av, "growth": g,
                    "prior_period": pp, "arr_period": ap} for c, pv, av, g, pp, ap in rows]}
io.open(os.path.join(HERE, "period-impact.json"), "w", encoding="utf-8").write(
    json.dumps(out, ensure_ascii=False, indent=1))
print("\nsaved period-impact.json")
