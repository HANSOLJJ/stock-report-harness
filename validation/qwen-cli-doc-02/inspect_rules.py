"""QWEN-CLI-DOC-02: rules/v1.5.json 의 체크리스트·결정·factor 모드 인벤토리 (읽기 전용)."""
import io
import json
import os
import re
from collections import Counter

W = r"C:\Users\noble\orca\workspaces\stock-report-harness\worker"
r = json.load(io.open(os.path.join(W, "scorecard", "rules", "v1.5.json"), encoding="utf-8"))

print("top-level keys:", sorted(r.keys()))
print("schema:", r.get("schema"), "| version:", r.get("version"), "| as_of:", r.get("as_of"))

cl = r.get("checklist") or []
print("\nchecklist count:", len(cl))
ids = [q.get("id") for q in cl]
print("checklist ids:", ids)
expect = ["Q%02d" % i for i in range(1, 24)]
print("Q01~Q23 기대 23개 vs 실제 %d개" % len(ids))
print("기대에 없는데 있는 것:", sorted(set(ids) - set(expect)))
print("기대하는데 없는 것:", sorted(set(expect) - set(ids)))

d = r.get("decisions")
print("\ndecisions type:", type(d).__name__)
items = d if isinstance(d, list) else list(d.values()) if isinstance(d, dict) else []
if isinstance(d, dict):
    for k, v in d.items():
        print("  %-6s status=%-10s blocking=%-6s summary=%s"
              % (k, v.get("status"), v.get("blocking"), (v.get("summary") or "")[:70]))
else:
    for v in items:
        print("  %-6s status=%-10s blocking=%-6s summary=%s"
              % (v.get("id"), v.get("status"), v.get("blocking"), (v.get("summary") or "")[:70]))
print("  개수:", len(items))

f = r.get("factors") or {}
print("\nfactors:")
for k in sorted(f):
    v = f[k]
    print("  %-4s mode=%-16s range=%-10s pending=%s" % (k, v.get("mode"), v.get("range"), v.get("pending")))

print("\npolicies keys:", sorted((r.get("policies") or {}).keys()))
src = r.get("source") or {}
print("source:", json.dumps(src, ensure_ascii=False)[:300])

# 문서가อ้าง한 미결 결정 목록과 대조
DOC_CLAIM = ["C-03", "C-05", "C-06", "C-13", "C-16"]
have = set()
if isinstance(d, dict):
    for k, v in d.items():
        if v.get("status") in ("pending", "open", "needs_decision") or v.get("blocking"):
            have.add(k)
else:
    for v in items:
        if v.get("status") in ("pending", "open", "needs_decision") or v.get("blocking"):
            have.add(v.get("id"))
print("\n문서(README/AGENTS)가 미결로 주장: %s" % DOC_CLAIM)
print("rules 에서 pending/blocking 인 것: %s" % sorted(have))
print("문서에 있는데 rules 에 pending 아님:", sorted(set(DOC_CLAIM) - have))
print("rules 에 pending 인데 문서에 없음:", sorted(have - set(DOC_CLAIM)))

# factor mode 에 걸린 pending 결정
print("\nfactor 별 pending 결정 연결:")
for k in sorted(f):
    p = f[k].get("pending")
    if p:
        print("  %-4s %s" % (k, json.dumps(p, ensure_ascii=False)[:200]))
