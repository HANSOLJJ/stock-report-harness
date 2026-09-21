# F9-DECIDE-20B 보완: 자체 시뮬레이터가 아니라 출하 엔진 calc_f9.compute_f9 를 직접 불러
# 16개 조합을 돌린다. worker 파일은 읽기 전용으로 import 만 하고 수정하지 않는다.
import io
import itertools
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WORKER = os.path.abspath(os.path.join(HERE, "..", "..", "..", "worker"))
sys.path.insert(0, os.path.join(WORKER, "scripts"))

from scorecard import calc_f9  # noqa: E402
from scorecard.inputs import ObsLookup, JudgmentLookup  # noqa: E402
from scorecard.rules import RuleSet  # noqa: E402
from pathlib import Path  # noqa: E402

RUNDIR = os.path.join(WORKER, "scorecard", "runs", "ai-scorecard-2026-09-baseline")


def load(p):
    return json.load(io.open(p, encoding="utf-8"))


obs_doc = load(os.path.join(RUNDIR, "observations.json"))
res_doc = load(os.path.join(RUNDIR, "results.json"))
rules_doc = load(os.path.join(WORKER, "scorecard", "rules", "v1.5.json"))
comp_doc = load(os.path.join(WORKER, "scorecard", "companies.json"))

rules = RuleSet(rules_doc, Path(os.path.join(WORKER, "scorecard", "rules", "v1.5.json")))
obs = ObsLookup(obs_doc["items"])

# 판단(judgment) 입력은 results 의 F9.calc.inputs 에 보존돼 있다. 같은 형태로 되돌린다.
jitems = []
for c in res_doc["companies"]:
    f9 = c["factors"].get("F9") or {}
    inputs = (f9.get("calc") or {}).get("inputs")
    if inputs:
        jitems.append({"judgment_id": f9.get("judgment_id") or "%s.F9" % c["company_id"],
                       "company_id": c["company_id"], "factor": "F9",
                       "inputs": inputs, "score": None, "status": "carried",
                       "reviewer": "carried", "reviewed_at": "2026-09-02"})
judgments = JudgmentLookup(jitems)

companies = {c["company_id"]: c for c in comp_doc["companies"]}
order = [c["company_id"] for c in res_doc["companies"]]

AXES = {"C-05": ["diagnose_only", "apply"],
        "C-16": ["hold", "downgrade"],
        "C-04": ["exclude", "include_v15"],
        "C-06": ["proposed_v15_boundaries", "undecided"]}


def run_with(c05, c16, c04, c06):
    run = json.loads(json.dumps(res_doc))
    run["decisions"] = [{"id": "C-05", "choice": c05}, {"id": "C-16", "choice": c16},
                        {"id": "C-04", "choice": c04}]
    if c06 != "undecided":
        run["decisions"].append({"id": "C-06", "choice": c06})
    out = {}
    for cid in order:
        r = calc_f9.compute_f9(companies[cid], obs, judgments, rules, run)
        out[cid] = {"score": r.get("score"), "status": r.get("status")}
    return out


matrix = {}
for c05, c16, c04, c06 in itertools.product(*AXES.values()):
    key = "C05=%s|C16=%s|C04=%s|C06=%s" % (c05, c16, c04, c06)
    matrix[key] = run_with(c05, c16, c04, c06)

io.open(os.path.join(HERE, "engine-matrix.json"), "w", encoding="utf-8").write(
    json.dumps(matrix, ensure_ascii=False, indent=1))

L = []
L.append("출하 엔진 calc_f9.compute_f9 직접 호출 — 16개 조합")
L.append("=" * 92)

BASE = "C05=diagnose_only|C16=hold|C04=exclude|C06=proposed_v15_boundaries"


def diff(ka, kb, label):
    L.append("\n%s" % label)
    d = [(cid, matrix[ka][cid], matrix[kb][cid]) for cid in order
         if matrix[ka][cid] != matrix[kb][cid]]
    L.append("   변화 기업 %d개" % len(d))
    for cid, a, b in d:
        L.append("     %s: %s(%s) → %s(%s)" % (cid, a["score"], a["status"],
                                               b["score"], b["status"]))
    return d


diff(BASE, "C05=apply|C16=hold|C04=exclude|C06=proposed_v15_boundaries",
     "C-05  diagnose_only → apply")
diff(BASE, "C05=diagnose_only|C16=downgrade|C04=exclude|C06=proposed_v15_boundaries",
     "C-16  hold → downgrade")
diff(BASE, "C05=diagnose_only|C16=hold|C04=include_v15|C06=proposed_v15_boundaries",
     "C-04  exclude → include_v15")
diff("C05=diagnose_only|C16=hold|C04=exclude|C06=undecided", BASE,
     "C-06  미확정 → proposed_v15_boundaries")

L.append("\n" + "=" * 92)
L.append("C-05 × C-16 교차 (C-06 확정, C-04 exclude)")
for c05 in AXES["C-05"]:
    for c16 in AXES["C-16"]:
        k = "C05=%s|C16=%s|C04=exclude|C06=proposed_v15_boundaries" % (c05, c16)
        unres = [cid for cid in order if matrix[k][cid]["score"] is None]
        L.append("  %-14s %-11s 미완료 %d개: %s" % (c05, c16, len(unres), ", ".join(unres)))
        for cid in ("spacex-xai", "amazon", "openai", "oracle"):
            L.append("       %-11s %s (%s)" % (cid, matrix[k][cid]["score"],
                                               matrix[k][cid]["status"]))

L.append("\n" + "=" * 92)
L.append("전 16개 조합에서 한 번이라도 score 가 None 이 아니게 되는 기업")
ever = {cid for cid in order for k in matrix if matrix[k][cid]["score"] is not None}
never = [cid for cid in order if cid not in ever]
L.append("   never resolved: %s" % ", ".join(never))

txt = "\n".join(L)
io.open(os.path.join(HERE, "engine-matrix-output.txt"), "w", encoding="utf-8").write(txt)
print(txt)
