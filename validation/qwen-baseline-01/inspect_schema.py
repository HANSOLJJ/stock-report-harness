"""QWEN-BASELINE-01 검증 보조: 기준선 JSON 스키마/키 인벤토리 파악 (읽기 전용)."""
import json
import io
import os
from collections import Counter, OrderedDict

BASE = r"C:\Users\noble\orca\workspaces\stock-report-harness\worker\scorecard"
BL = os.path.join(BASE, "baseline", "v1.5")


def load(p):
    with io.open(p, encoding="utf-8") as f:
        return json.load(f)


def keypaths(obj, prefix="", depth=0, out=None, maxdepth=4):
    if out is None:
        out = OrderedDict()
    if depth > maxdepth:
        return out
    if isinstance(obj, dict):
        for k, v in obj.items():
            kp = prefix + "." + k if prefix else k
            out[kp] = type(v).__name__
            keypaths(v, kp, depth + 1, out, maxdepth)
    elif isinstance(obj, list) and obj:
        keypaths(obj[0], prefix + "[]", depth + 1, out, maxdepth)
    return out


for name in ["scores.json", "observations.json", "triggers.json"]:
    d = load(os.path.join(BL, name))
    print("=" * 70)
    print(name, "top type:", type(d).__name__)
    if isinstance(d, dict):
        for k, v in d.items():
            if isinstance(v, (list, dict)):
                print("   %-24s %-6s len=%s" % (k, type(v).__name__, len(v)))
            else:
                print("   %-24s = %r" % (k, v))
    print("--- key paths (depth<=4) ---")
    for kp, t in keypaths(d).items():
        print("   %-60s %s" % (kp, t))
    print()

obs = load(os.path.join(BL, "observations.json"))
olist = obs["items"]
print("=" * 70)
print("observations count:", len(olist))
print("sample[0]:")
print(json.dumps(olist[0], ensure_ascii=False, indent=2))
print("sample[1]:")
print(json.dumps(olist[1], ensure_ascii=False, indent=2))

allkeys = Counter()
for o in olist:
    for k in o.keys():
        allkeys[k] += 1
print("observation field frequency:")
for k, c in allkeys.most_common():
    print("   %-28s %4d / %d" % (k, c, len(olist)))

trg = load(os.path.join(BL, "triggers.json"))
tlist = trg["items"]
print("=" * 70)
print("triggers count:", len(tlist))
print("sample[0]:")
print(json.dumps(tlist[0], ensure_ascii=False, indent=2))
allkeys = Counter()
for o in tlist:
    for k in o.keys():
        allkeys[k] += 1
print("trigger field frequency:")
for k, c in allkeys.most_common():
    print("   %-28s %4d / %d" % (k, c, len(tlist)))
