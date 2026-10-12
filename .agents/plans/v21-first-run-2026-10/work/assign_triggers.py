# (2026-10 v2.1 첫 실행) 판단 세션이 쓴 새 트리거(work/judge/triggers-*.json)에 TRG ID 를 붙여 triggers.json 에 더하고, 판단 파일의 "NEW:<key>" 를 그 ID 로 바꾼다
"""
사용: uv run --frozen python -X utf8 .agents/plans/v21-first-run-2026-10/work/assign_triggers.py <slug> [--dry-run]

트리거 파일 모양: {"group": "J1", "new_triggers": [{"key": "...", "company_id", "factors", "observation", "condition", "deadline",
"source_ids", "evidence_ids", "status", "recheck": {"factors", "what"}}]}. key 는 (group, key) 로 유일해야 한다. 판단 파일(F*-<회사>.json)의
문자열 값 가운데 "NEW:<key>" 를 찾아 바꾼다(그 회사의 트리거 key 를 먼저, 없으면 그룹 전체에서 찾는다). 적용 뒤 load_context 로 검증하고
실패하면 triggers.json 을 되돌린다(판단 파일은 바꾼 뒤라 다시 돌리면 이미 ID 가 들어 있다).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "scripts"))
from scorecard.engine import load_context  # noqa: E402
from scorecard.paths import run_paths  # noqa: E402

JUDGE = Path(__file__).resolve().parent / "judge"
KEYS = ("trigger_id", "company_id", "factors", "observation", "condition", "deadline", "evidence_ids", "source_ids", "status", "recheck", "note")


def replace(obj, mapping):
    if isinstance(obj, str) and obj.startswith("NEW:"):
        if obj[4:] not in mapping:
            raise SystemExit(f"트리거 key {obj[4:]!r} 를 찾지 못했다")
        return mapping[obj[4:]]
    if isinstance(obj, list):
        return [replace(x, mapping) for x in obj]
    if isinstance(obj, dict):
        return {k: replace(v, mapping) for k, v in obj.items()}
    return obj


def main() -> int:
    slug = sys.argv[1]
    dry = "--dry-run" in sys.argv
    path = run_paths(slug).triggers
    backup = path.read_bytes()
    payload = json.loads(backup.decode("utf-8"))
    nxt = max(int(t["trigger_id"].split("-")[1]) for t in payload["items"]) + 1
    mapping: dict[str, str] = {}
    added = []
    for f in sorted(JUDGE.glob("triggers-*.json")):
        for t in json.loads(f.read_text(encoding="utf-8")).get("new_triggers") or []:
            key = t["key"]
            if key in mapping:
                raise SystemExit(f"트리거 key 중복 {key!r} ({f.name})")
            tid = f"TRG-{nxt:03d}"
            nxt += 1
            mapping[key] = tid
            item = {"trigger_id": tid, **{k: t[k] for k in KEYS if k in t and k != "trigger_id"}}
            item.setdefault("evidence_ids", [])
            item.setdefault("source_ids", [])
            item.setdefault("status", "watching")
            added.append(item)
    print(f"새 트리거 {len(added)}건: " + ", ".join(f"{k}→{v}" for k, v in mapping.items()))
    if dry:
        return 0
    payload["items"].extend(added)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    patched = 0
    for jf in sorted(JUDGE.glob("F*-*.json")):
        if jf.name.endswith(".propose.json"):
            continue
        spec = json.loads(jf.read_text(encoding="utf-8"))
        new = replace(spec, mapping)
        if new != spec:
            jf.write_text(json.dumps(new, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
            patched += 1
    try:
        load_context(slug)
    except BaseException as exc:
        path.write_bytes(backup)
        print(f"[실패] triggers.json 을 되돌렸다: {exc}")
        return 1
    print(f"판단 파일 {patched}개에서 NEW:<key> 를 바꿨다")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
