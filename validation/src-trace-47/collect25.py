# SRC-TRACE-47: 점수 경로에 실제로 들어가는 legacy_unverified 25쌍을 확정한다.
# results.json 이 참조한 observation_id 와 9지표 legacy 의 교집합.
import io
import json
import os

W = "C:/Users/noble/orca/workspaces/stock-report-harness/worker"
RUN = "ai-scorecard-2026-09-obsreg"
HERE = os.path.dirname(os.path.abspath(__file__))
M = ("market_cap", "arr_prior", "cumulative_raised", "arr", "post_money_valuation",
     "net_cash", "ps_ratio", "offbalance_B", "contracted_revenue")

obs = {o["observation_id"]: o for o in
       json.load(io.open("%s/scorecard/runs/%s/observations.json" % (W, RUN), encoding="utf-8"))["items"]}
res = json.load(io.open("%s/scorecard/runs/%s/results.json" % (W, RUN), encoding="utf-8"))
cs = res.get("companies") or res.get("items")
if isinstance(cs, dict):
    cs = list(cs.values())

ref = set()
where = {}


def walk(o, cid=None, fid=None):
    if isinstance(o, dict):
        cid = o.get("company_id", cid)
        fid = o.get("factor", fid)
        for k, v in o.items():
            if k == "observation_ids" and isinstance(v, list):
                for i in v:
                    ref.add(i); where.setdefault(i, set()).add(fid)
            elif k.endswith("observation_id") and isinstance(v, str):
                ref.add(v); where.setdefault(v, set()).add(fid)
            else:
                walk(v, cid, fid)
    elif isinstance(o, list):
        for v in o:
            walk(v, cid, fid)


walk(cs)
rows = [obs[i] for i in ref if i in obs and obs[i].get("metric") in M
        and obs[i].get("status") == "legacy_unverified"]
rows.sort(key=lambda o: (M.index(o["metric"]), o["company_id"]))
out = []
for o in rows:
    out.append({"observation_id": o["observation_id"], "metric": o["metric"],
                "company_id": o["company_id"], "value": o.get("value"),
                "raw": o.get("raw"), "source_id": o.get("source_id"),
                "basis": o.get("basis"), "note": o.get("note"),
                "used_by_factors": sorted(x for x in (where.get(o["observation_id"]) or set()) if x)})
io.open(os.path.join(HERE, "targets-25.json"), "w", encoding="utf-8").write(
    json.dumps({"run": RUN, "count": len(out), "items": out}, ensure_ascii=False, indent=1))
print("대상 %d건" % len(out))
print("%-22s %-11s %-20s %-14s %s" % ("metric", "company", "raw", "source_id", "쓰는 factor"))
print("-" * 92)
for r in out:
    print("%-22s %-11s %-20s %-14s %s" % (r["metric"], r["company_id"], str(r["raw"])[:20],
                                          r["source_id"], ",".join(r["used_by_factors"])))
