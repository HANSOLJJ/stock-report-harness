# F9-DECIDE-20B: 현재 F9 상태(게이트 실행 경로·보류 사유)를 읽는다.
# 기존 F9 점수를 정답으로 쓰지 않는다. 여기서 읽는 것은 '상태와 사유'이지 '정답'이 아니다.
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
W = os.path.join(HERE, "..", "..", "..", "worker", "scorecard")

r = json.load(io.open(os.path.join(W, "runs", "ai-scorecard-2026-09-baseline",
                                   "results.json"), encoding="utf-8"))

out = {}
print("%-12s %-7s %-16s %-10s %s" % ("company", "score", "status", "basis", "pending/warnings"))
print("-" * 110)
for c in r["companies"]:
    f9 = c["factors"].get("F9")
    if not f9:
        continue
    cid = c["company_id"]
    out[cid] = f9
    p = f9.get("pending")
    ptxt = ""
    if p:
        ptxt = json.dumps(p, ensure_ascii=False)[:70]
    w = "; ".join(f9.get("warnings") or [])[:70]
    print("%-12s %-7s %-16s %-10s %s" % (
        cid, str(f9.get("score")), f9.get("status"), f9.get("basis"), ptxt or w))

print()
print("=" * 110)
print("게이트 계산 경로(calc) 전문")
print("=" * 110)
for cid, f9 in out.items():
    calc = f9.get("calc") or {}
    print("\n== %s  score=%s status=%s" % (cid, f9.get("score"), f9.get("status")))
    print(json.dumps(calc, ensure_ascii=False, indent=1))
    if f9.get("warnings"):
        for w in f9["warnings"]:
            print("   ! %s" % w)
    if f9.get("pending"):
        print("   PENDING:", json.dumps(f9["pending"], ensure_ascii=False))

io.open(os.path.join(HERE, "f9-current-state.json"), "w", encoding="utf-8").write(
    json.dumps(out, ensure_ascii=False, indent=1))
print("\nsaved f9-current-state.json")
