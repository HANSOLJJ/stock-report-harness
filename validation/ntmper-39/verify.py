# NTMPER-39: (2) SEC 허용 원천에 미발표 분기 컨센서스가 있는지 실증 (3) 가중 근사 재현
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "g1-fill-27b-2026-09-11"))
from build_ttm import SOURCES, load  # noqa: E402

print("=" * 100)
print("(2) SEC companyfacts 에 '미래 추정치' 성격의 개념이 있는가 — 전수 탐색")
print("=" * 100)
# 이름으로 먼저 훑는다. 0 이 나오면 부재인지 탐색 실패인지 가르기 위해 패턴을 넓게 잡는다.
PAT = re.compile(r"(?i)forecast|estimat|guidance|projec|outlook|consensus|analyst|expected|future")
hits = {}
for cid in SOURCES:
    d, _, _ = load(cid)
    names = []
    for tax, cs in d["facts"].items():
        for cname in cs:
            if PAT.search(cname):
                names.append("%s:%s" % (tax, cname))
    hits[cid] = sorted(names)

allnames = sorted({n for v in hits.values() for n in v})
print("이름에 미래·추정 어휘가 든 개념 (12개사 합집합) %d개" % len(allnames))
for n in allnames:
    owners = [c for c in hits if n in hits[c]]
    print("   %-72s %d개사" % (n[:72], len(owners)))

print()
print("판정 근거 — 위 개념들이 '향후 분기 EPS 컨센서스' 인가")
print("   전부 회계 추정(충당금·공정가치·내용연수) 또는 미래 현금흐름 할인 가정이다.")
print("   애널리스트 컨센서스는 발행사가 제출하는 것이 아니므로 SEC 제출물의 대상이 아니다.")

print()
print("=" * 100)
print("(3) 연간 EPS 가중 근사 재현")
print("=" * 100)


def approx(label, price, terms, divisor=None, target=None):
    eps = 0.0
    parts = []
    for name, val, w in terms:
        c = val * w
        eps += c
        parts.append("%s %s × %d/12 = %.4f" % (name, "{:,.2f}".format(val), round(w * 12), c))
    shown = eps
    if divisor:
        shown = eps / divisor
    per = price / shown
    print("  [%s]" % label)
    for p in parts:
        print("     %s" % p)
    print("     NTM EPS 합 = %.4f%s" % (eps, (" TWD → ÷%.1f = $%.4f" % (divisor, shown)) if divisor else ""))
    print("     PER = %s ÷ %.4f = %.4f" % ("{:,.2f}".format(price), shown, per))
    if target is not None:
        d = per - target
        print("     원문 값 %.1f 대비 %+.4f (%+.2f%%) → %s" % (
            target, d, d / target * 100, "재현됨" if abs(d) < 0.05 else "★재현 실패"))
    print()
    return per


# 원문 문언 그대로. 채점표 L822·L823
tsm = approx("TSMC — 채점표 L822",
             price=415.50,
             terms=[("FY26 107.64×5", 107.64 * 5, 4 / 12), ("FY27 142.13×5", 142.13 * 5, 8 / 12)],
             divisor=30.5, target=19.4)
baba = approx("Alibaba — 채점표 L823",
              price=111.76,
              terms=[("FY27 $5.71", 5.71, 7 / 12), ("FY28 $8.03", 8.03, 5 / 12)],
              target=16.7)

print("=" * 100)
print("가중의 정체 — 무엇에 대한 가중인가")
print("=" * 100)
print("  기준일 2026-09-02 에서 '현 회계연도의 남은 개월수 : 차기 회계연도에서 끌어오는 개월수' 다.")
print("  TSMC 는 12월 결산이라 9·10·11·12 = 4개월 남아 4/12 + 8/12.")
print("  Alibaba 는 3월 결산이라 FY2027(2026-04~2027-03)이 9월부터 7개월 남아 7/12 + 5/12.")
print("  즉 회계연도 EPS 두 개를 달력 개월수로 선형 안분한 것이다. 분기 컨센서스가 아니다.")

io.open(os.path.join(HERE, "verify-output.json"), "w", encoding="utf-8").write(
    json.dumps({"sec_future_concepts": hits, "tsmc_per": tsm, "alibaba_per": baba},
               ensure_ascii=False, indent=1))
print("\nsaved verify-output.json")
