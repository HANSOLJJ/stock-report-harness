"""QWEN-NTM-DATA-03: 참조 파일 시작/종료 해시 기록 + ntm 관측 현황 (읽기 전용)."""
import datetime
import hashlib
import io
import json
import os
import subprocess
import sys
from collections import Counter

W = r"C:\Users\noble\orca\workspaces\stock-report-harness\worker"
HERE = os.path.dirname(os.path.abspath(__file__))
STAGE = sys.argv[1] if len(sys.argv) > 1 else "start"

REFS = [
    "docs/scorecard/design-guideline.md",
    "docs/scorecard/open-items.md",
    "scripts/scorecard/baseline_import.py",
    "scripts/scorecard/calc_f6.py",
    "scorecard/companies.json",
    "scorecard/baseline/v1.5/observations.json",
    "scorecard/baseline/v1.5/scores.json",
    "scorecard/rules/v1.5.json",
]

rows = []
for rel in REFS:
    p = os.path.join(W, rel)
    if not os.path.isfile(p):
        rows.append({"rel": rel, "missing": True})
        print("MISSING  " + rel)
        continue
    raw = open(p, "rb").read()
    text = raw.decode("utf-8", "replace")
    mt = os.path.getmtime(p)
    row = {
        "rel": rel,
        "sha256": hashlib.sha256(raw).hexdigest(),
        "bytes": len(raw),
        "lines": text.count("\n") + 1,
        "mtime": datetime.datetime.utcfromtimestamp(mt).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    rows.append(row)

head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=W,
                      capture_output=True, text=True).stdout.strip()
status = subprocess.run(["git", "status", "--porcelain"], cwd=W,
                        capture_output=True, text=True).stdout.strip().splitlines()

out = {
    "stage": STAGE,
    "head": head,
    "status": status,
    "refs": rows,
    "taken_at": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
}
with io.open(os.path.join(HERE, "hashes-" + STAGE + ".json"), "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)

print("stage={}  worker HEAD={}  refs={}".format(STAGE, head[:7], len(rows)))
for line in status:
    print("   git: " + line)
for r in rows:
    if not r.get("missing"):
        print("   {:46s} {:8d} bytes {:5d} lines  {}  {}".format(
            r["rel"], r["bytes"], r["lines"], r["sha256"][:16], r["mtime"]))

# ---- companies.json 레지스트리
with io.open(os.path.join(W, "scorecard", "companies.json"), encoding="utf-8") as f:
    comp = json.load(f)
print("")
print("=== companies.json ===")
print("as_of:", comp.get("as_of"), "| count:", len(comp["companies"]))
for c in comp["companies"]:
    print("  {:12s} listed={:<6} ticker={!r:8} type={:12s} {}".format(
        c["company_id"], str(c.get("listed")), c.get("ticker"),
        str(c.get("type")), c["display_name"]))

# ---- observations
with io.open(os.path.join(W, "scorecard", "baseline", "v1.5", "observations.json"),
             encoding="utf-8") as f:
    obs = json.load(f)["items"]
print("")
print("=== observations.json total={} ===".format(len(obs)))
print("metric 분포:", dict(Counter(o["metric"] for o in obs).most_common()))
print("")
print("--- NTM/PER/EPS/forward 관련 관측 전수 ---")
for o in obs:
    low = o["metric"].lower()
    if ("ntm" in low) or ("per" in low) or ("eps" in low) or ("forward" in low):
        print("  {:46s} {:12s} value={!r:12} unit={:12s} kind={:9s} status={}".format(
            o["observation_id"], o["company_id"], o["value"], str(o["unit"]),
            str(o["kind"]), o["status"]))
        if o.get("basis"):
            print("      basis=" + json.dumps(o["basis"], ensure_ascii=False))
        if o.get("raw"):
            print("      raw=" + repr(o["raw"][:110]))
        if o.get("note"):
            print("      note=" + repr(o["note"][:110]))

print("")
print("--- ntm_eps 관측 존재 여부 ---")
print("ntm_eps 관측: {}건".format(len([o for o in obs if o["metric"] == "ntm_eps"])))

print("")
print("--- basis.method 분포 ---")
bm = Counter()
for o in obs:
    b = o.get("basis")
    if isinstance(b, dict) and b.get("method"):
        bm[(o["metric"], b["method"])] += 1
for (m, meth), c in sorted(bm.items()):
    print("  {:14s} {:40s} {}건".format(m, meth, c))
