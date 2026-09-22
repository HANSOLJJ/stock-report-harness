"""QWEN-BASELINE-01 v5: 트리거 3-way(MD §5 / HTML TRIG / triggers.json) 본문 대조.
차이가 '원본 내부 불일치(HTML vs MD)' 인지 '이관 중 변경(JSON vs HTML)' 인지 구분한다."""
import io
import json
import os
import re
from collections import OrderedDict

WORKER = r"C:\Users\noble\orca\workspaces\stock-report-harness\worker"
BL = os.path.join(WORKER, "scorecard", "baseline", "v1.5")
ORIG = r"E:\sourcecode\01_side_project\stock-report-harness\AI_company_analysis_factor"
HERE = os.path.dirname(os.path.abspath(__file__))
load = lambda p: json.load(io.open(p, encoding="utf-8"))
read = lambda p: io.open(p, encoding="utf-8").read()

trg = load(os.path.join(BL, "triggers.json"))["items"]
html = load(os.path.join(HERE, "html-arrays.json"))
md = read(os.path.join(ORIG, "AI기업_채점표_v1.5.md"))
html_raw = read(os.path.join(ORIG, "AI기업_채점표_v1.5.html"))
mdlines = md.split("\n")


def clean(x):
    x = re.sub(r"<[^>]+>", "", str(x) if x is not None else "")
    x = x.replace("**", "").replace("✱", "").replace("*", "")
    return re.sub(r"\s+", " ", x).strip()


def key(s):
    s = clean(s)
    s = re.sub(r"^[🆕🔑📏🔧⚠️📌\s]+", "", s)
    return re.sub(r"[\s·\-—–()']/", "", s)


t0 = next(k for k, l in enumerate(mdlines) if l.startswith("## 5. 다음 분기"))
MDT = OrderedDict()
for k in range(t0, len(mdlines)):
    if not mdlines[k].startswith("|"):
        continue
    c = [x.strip() for x in mdlines[k].strip().strip("|").split("|")]
    if len(c) < 3 or c[0] in ("항목", "") or set(c[0]) <= set("-: "):
        continue
    MDT[key(c[0])] = OrderedDict(item=clean(c[0]), why=clean(c[1]), impact=clean(c[2]), line=k + 1)

HTR = OrderedDict()
for r in html["TRIG"]:
    cells = [clean(x) for x in r]
    while len(cells) < 3:
        cells.append("")
    HTR[key(cells[0])] = OrderedDict(item=cells[0], why=cells[1], impact=cells[2])

print("=" * 94)
print("트리거 3-way 본문 대조 — (a) JSON vs HTML  (b) HTML vs MD")
print("=" * 94)
a_diff = b_diff = 0
for t in trg:
    k = key(t["title"])
    h = HTR.get(k)
    m = MDT.get(k)
    if not h:
        print("\n!! JSON 항목이 HTML TRIG 에 없음: %s" % t["title"])
        continue
    ja, ha, ma = clean(t["why"]), h["why"], (m["why"] if m else None)
    ji, hi, mi = clean(t["impact_raw"]), h["impact"], (m["impact"] if m else None)
    rows = []
    if ja != ha:
        rows.append(("why", "JSON≠HTML(이관 중 변경)", ja, ha))
    if ji != hi:
        rows.append(("impact", "JSON≠HTML(이관 중 변경)", ji, hi))
    if ma is not None and ha != ma:
        rows.append(("why", "HTML≠MD(원본 내부 불일치)", ha, ma))
    if mi is not None and hi != mi:
        rows.append(("impact", "HTML≠MD(원본 내부 불일치)", hi, mi))
    if ma is None:
        rows.append(("item", "MD §5 에 없음(HTML 전용)", t["title"], "-"))
    if rows:
        print("\n--- %s | %s" % (t["trigger_id"], t["title"]))
        for f, kind, x, y in rows:
            tag = "A" if kind.startswith("JSON") else ("B" if kind.startswith("HTML") else "C")
            if tag == "A":
                a_diff += 1
            elif tag == "B":
                b_diff += 1
            print("    [%s] %-7s %s" % (tag, f, kind))
            print("        1: %s" % x[:250])
            print("        2: %s" % y[:250])

print("\n" + "=" * 94)
print("요약: [A] JSON≠HTML (이관 중 변경) %d건 · [B] HTML≠MD (원본 내부 불일치) %d건" % (a_diff, b_diff))

print("\n" + "=" * 94)
print("MD §5 에 있고 JSON/HTML 에 없는 트리거")
for k, v in MDT.items():
    if k not in HTR:
        print("   - MD line %d: %s | why=%s | impact=%s" % (v["line"], v["item"], v["why"], v["impact"]))

print("\n" + "=" * 94)
print("'Menlo' 원문 등장 위치")
for lbl, txt, lines in [("MD", md, mdlines), ("HTML", html_raw, html_raw.split("\n"))]:
    hits = [i + 1 for i, l in enumerate(lines) if "Menlo" in l]
    print("   %s: %d곳 %s" % (lbl, len(hits), hits[:10]))
for o in load(os.path.join(BL, "observations.json"))["items"]:
    if "Menlo" in json.dumps(o, ensure_ascii=False):
        print("   observations: %s" % o["observation_id"])
print("   triggers.json 에 Menlo 포함: %s"
      % [t["trigger_id"] for t in trg if "Menlo" in json.dumps(t, ensure_ascii=False)])
print("   rules/v1.5.json 에 Menlo 포함: %s"
      % ("Menlo" in read(os.path.join(WORKER, "scorecard", "rules", "v1.5.json"))))
