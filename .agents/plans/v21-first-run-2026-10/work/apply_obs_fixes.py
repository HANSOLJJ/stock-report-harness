# (2026-10 v2.1 첫 실행) 보강 세션의 observation_fixes(이미 있는 관측을 고치거나 빼기)를 실행 관측에 적용한다 — 합치기 도구가 다루지 않는 부분
"""
사용: uv run --frozen python -X utf8 .agents/plans/v21-first-run-2026-10/work/apply_obs_fixes.py <slug> <out-S.json>

replace 는 관측 ID 를 그대로 두고 replacement 의 키로 덮는다. remove 는 그 관측을 뺀다. 적용 뒤 load_context 로 검증하고,
실패하면 되돌린다.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "scripts"))
from scorecard.engine import load_context, run_dir  # noqa: E402


def main() -> int:
    slug, src = sys.argv[1:3]
    path = run_dir(slug) / "observations.json"
    backup = path.read_bytes()
    payload = json.loads(backup.decode("utf-8"))
    fixes = json.loads(Path(src).read_text(encoding="utf-8")).get("observation_fixes") or []
    by_id = {o["observation_id"]: i for i, o in enumerate(payload["items"])}
    removed = []
    for f in fixes:
        idx = by_id.get(f["observation_id"])
        if idx is None:
            raise SystemExit(f"관측 {f['observation_id']} 가 없다")
        if f["action"] == "replace":
            item = payload["items"][idx]
            allowed = {"company_id", "metric", "value", "unit", "as_of", "kind", "source_id", "status", "period", "basis",
                       "raw", "note", "missing_type", "observed_at"}
            rep = dict(f["replacement"])
            extra = {k: rep.pop(k) for k in list(rep) if k not in allowed and k != "observation_id"}
            item.update({k: v for k, v in rep.items() if k != "observation_id"})
            if extra:   # 관측이 받지 않는 최상위 키는 basis 로 옮긴다
                item["basis"] = {**(item.get("basis") or {}), **extra}
            item.setdefault("note", "")
            item["note"] = (item["note"] + " · " if item["note"] else "") + f"보강 세션 고침: {f['reason']}"
        elif f["action"] == "remove":
            removed.append(f["observation_id"])
        else:
            raise SystemExit(f"알 수 없는 action {f['action']!r}")
    payload["items"] = [o for o in payload["items"] if o["observation_id"] not in removed]
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    try:
        load_context(slug)
    except BaseException as exc:
        path.write_bytes(backup)
        print(f"[실패] 되돌렸다: {exc}")
        return 1
    print(f"고침 {len(fixes) - len(removed)}건, 뺌 {len(removed)}건: {', '.join(removed)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
