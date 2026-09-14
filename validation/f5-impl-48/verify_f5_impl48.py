# F5-IMPL-48 적용 뒤 바뀐 칸이 지시서의 예상과 정확히 같은지, 승인된 baseline 이 그대로인지 대조한다
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard.stages import current_hashes  # noqa: E402

RUN = ROOT / "scorecard" / "runs" / "ai-scorecard-2026-09-obsreg"
BASE = "ai-scorecard-2026-09-baseline"

# 지시서 msg_75f62ec9d7c0 의 예상. 이것 말고 바뀐 칸이 하나라도 있으면 실패다.
EXPECTED = {
    ("anthropic", "F5"): (5, 4),
    ("anthropic", "total"): (12, 11),
    ("openai", "F5"): (2, 1),
    ("openai", "total"): (3, 2),
    ("tsmc", "rank"): (6, 5),
}


def snapshot(results: dict) -> dict:
    return {c["company_id"]: {"total": c["total"], "rank": c["rank"],
                              "factors": {f: v["score"] for f, v in c["factors"].items()}}
            for c in results["companies"]}


def main() -> int:
    before = json.loads((HERE / "before.json").read_text(encoding="utf-8"))["companies"]
    after = snapshot(json.loads((RUN / "results.json").read_text(encoding="utf-8")))
    changed = {}
    for cid, b in before.items():
        a = after[cid]
        for key in ("total", "rank"):
            if b[key] != a[key]:
                changed[(cid, key)] = (b[key], a[key])
        for f, s in b["factors"].items():
            if s != a["factors"][f]:
                changed[(cid, f)] = (s, a["factors"][f])
    fails = 0
    for k, v in sorted(changed.items()):
        ok = EXPECTED.get(k) == v
        fails += not ok
        print(f"  {'ok ' if ok else 'XX '} {k[0]:10} {k[1]:5} {v[0]} -> {v[1]}")
    for k in EXPECTED.keys() - changed.keys():
        fails += 1
        print(f"  XX  예상했으나 안 바뀜 {k}")
    print(f"바뀐 칸 {len(changed)} · 예상 {len(EXPECTED)} · 어긋남 {fails}")
    print(f"anthropic 순위 {after['anthropic']['rank']} · tsmc 순위 {after['tsmc']['rank']} · "
          f"openai 순위 {after['openai']['rank']}")

    approval = json.loads((ROOT / "scorecard" / "runs" / BASE / "approval.json").read_text(encoding="utf-8"))["hashes"]
    base_ok = current_hashes(BASE) == approval
    fails += not base_ok
    print(f"baseline 승인 해시 6종 보존: {base_ok}")

    old = json.loads((HERE / "hashes-before.json").read_text(encoding="utf-8"))["ai-scorecard-2026-09-obsreg"]
    new = current_hashes("ai-scorecard-2026-09-obsreg")
    print("obsreg 해시 (승인 전 실행 — 바뀌는 것이 예상):")
    for k in new:
        print(f"  {k:12} {old[k][:12]} -> {new[k]}{'' if old[k] != new[k] else '  (불변)'}")
    print("판정:", "예상과 일치" if not fails else "예상과 다름 — 멈춤")
    return 1 if fails else 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    sys.exit(main())
