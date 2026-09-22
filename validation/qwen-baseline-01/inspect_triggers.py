"""QWEN-BASELINE-01 v4: 트리거 39건 3-way 대조(MD §5 표 / HTML const TRIG / triggers.json)
+ 신용표 '우리 함정' 열 전체 매핑."""
import io
import json
import os
import re
from collections import Counter, OrderedDict

WORKER = r"C:\Users\noble\orca\workspaces\stock-report-harness\worker"
BL = os.path.join(WORKER, "scorecard", "baseline", "v1.5")
ORIG = r"E:\sourcecode\01_side_project\stock-report-harness\AI_company_analysis_factor"
HERE = os.path.dirname(os.path.abspath(__file__))
load = lambda p: json.load(io.open(p, encoding="utf-8"))
read = lambda p: io.open(p, encoding="utf-8").read()

trg = load(os.path.join(BL, "triggers.json"))["items"]
scores = load(os.path.join(BL, "scores.json"))
BLC = OrderedDict((c["company_id"], c) for c in scores["companies"])
html = load(os.path.join(HERE, "html-arrays.json"))
md = read(os.path.join(ORIG, "AI기업_채점표_v1.5.md"))
mdlines = md.split("\n")


def clean(x):
    x = re.sub(r"<[^>]+>", "", str(x) if x is not None else "")
    return x.replace("**", "").replace("✱", "").strip()


def key(s):
    s = clean(s)
    s = re.sub(r"^[🆕🔑📏🔧⚠️📌\s]+", "", s)
    return re.sub(r"[\s·\-—–()()/,]'?", "", s)


# ---- MD §5 트리거 표
t0 = next(k for k, l in enumerate(mdlines) if l.startswith("## 5. 다음 분기"))
MDT = []
for k in range(t0, len(mdlines)):
    if not mdlines[k].startswith("|"):
        continue
    c = [x.strip() for x in mdlines[k].strip().strip("|").split("|")]
    if len(c) < 3 or c[0] in ("항목", "") or set(c[0]) <= set("-: "):
        continue
    MDT.append(OrderedDict(item=clean(c[0]), why=clean(c[1]), impact=clean(c[2]), line=k + 1))

HTRIG = [clean(r[0]) for r in html["TRIG"]]
BJ = [t["title"] for t in trg]

print("=" * 90)
print("트리거 건수: MD §5 표 %d행 / HTML const TRIG %d행 / triggers.json %d건"
      % (len(MDT), len(HTRIG), len(BJ)))

mk = OrderedDict((key(t["item"]), t) for t in MDT)
hk = OrderedDict((key(x), x) for x in HTRIG)
bk = OrderedDict((key(x), x) for x in BJ)
print("정규화 키 중복: MD %d→%d, HTML %d→%d, JSON %d→%d"
      % (len(MDT), len(mk), len(HTRIG), len(hk), len(BJ), len(bk)))

print("\n[1] triggers.json 에 있고 HTML TRIG 에 없는 항목")
for k, v in bk.items():
    if k not in hk:
        print("   - %s" % v)
print("[2] HTML TRIG 에 있고 triggers.json 에 없는 항목")
for k, v in hk.items():
    if k not in bk:
        print("   - %s" % v)
print("[3] triggers.json 에 있고 MD §5 표에 없는 항목 (HTML 전용)")
for k, v in bk.items():
    if k not in mk:
        print("   - %s" % v)
print("[4] MD §5 표에 있고 triggers.json 에 없는 항목")
for k, v in mk.items():
    if k not in bk:
        print("   - line %d: %s" % (v["line"], v["item"]))

print("\n" + "=" * 90)
print("[5] ⑥ 경계 트리거 원문 3-way (MD §5 vs HTML TRIG vs triggers.json)")
for lbl, coll in [("MD §5", [t["item"] + " || " + t["why"] + " || " + t["impact"] for t in MDT]),
                  ("HTML TRIG", [" || ".join(clean(x) for x in r) for r in html["TRIG"]]),
                  ("triggers.json", [t["title"] + " || " + t["why"] + " || " + t["impact_raw"] for t in trg])]:
    for s in coll:
        if "경계" in s and ("개사" in s or "20선" in s or "25선" in s):
            print("   [%s] %s" % (lbl, s[:300]))

print("\n" + "=" * 90)
print("[6] MD §5 표 vs triggers.json 본문(why/impact) 문구 차이 — 표본 전수")
ndiff = 0
for k, jt in zip([key(t["title"]) for t in trg], trg):
    if k in mk:
        m = mk[k]
        for jf, mf in [("why", "why"), ("impact_raw", "impact")]:
            a, b = clean(jt[jf]), clean(m[mf])
            if re.sub(r"\s+", "", a) != re.sub(r"\s+", "", b):
                ndiff += 1
                print("   DIFF %s [%s vs %s.%s]" % (jt["trigger_id"], jf, "MD", mf))
                print("      JSON: %s" % a[:230])
                print("      MD  : %s" % b[:230])
print("   본문 문구 차이: %d건" % ndiff)

print("\n" + "=" * 90)
print("[7] MD §3-1a-2 신용표 '우리 함정' 열 전체 매핑(· 구분 처리)")
NAME2ID = {"Apple": "apple", "NVIDIA": "nvidia", "Microsoft": "microsoft", "Alphabet": "alphabet",
           "Meta": "meta", "TSMC": "tsmc", "Tesla": "tesla", "Palantir": "palantir",
           "Amazon": "amazon", "Alibaba": "alibaba", "SpaceX": "spacex-xai", "Oracle": "oracle",
           "Anthropic": "anthropic", "OpenAI": "openai", "MS": "microsoft"}
i0 = next(k for k, l in enumerate(mdlines) if l.startswith("### 3-1a-2"))
i1 = next(k for k, l in enumerate(mdlines) if l.startswith("### 3-1a-3"))
n = bad = 0
for k in range(i0, i1):
    if not mdlines[k].startswith("|"):
        continue
    c = [x.strip() for x in mdlines[k].strip().strip("|").split("|")]
    if len(c) < 6 or c[0] in ("기업", "") or set(c[0]) <= set("-: "):
        continue
    cell = clean(c[0])
    toks = [t.strip() for t in re.split(r"[·,]", cell)]
    cids = [NAME2ID[t] for t in toks if t in NAME2ID]
    trap_txt = clean(c[4])
    vals = [int(x) for x in re.findall(r"-?\d+", trap_txt)]
    if not cids:
        print("   [미매핑] %r (함정=%s)" % (cell, trap_txt))
        continue
    for cid in cids:
        n += 1
        t = BLC[cid]["trap"]
        ok = (t == vals[0]) if len(vals) == 1 else (min(vals) <= t <= max(vals))
        print("   %-12s 표=%-10s 기준선 trap=%-4s %s" % (cid, trap_txt, t, "OK" if ok else "MISMATCH"))
        if not ok:
            bad += 1
print("   대조 %d개, 문제 %d건" % (n, bad))

print("\n" + "=" * 90)
print("[8] triggers.json 39건 전체 목록 (title / status)")
for t in trg:
    print("   %-9s %-8s %s" % (t["trigger_id"], t["status"], t["title"][:78]))
