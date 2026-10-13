# (2026-10 v2.1 첫 실행) 리뷰 뒤 문장 치환 목록(work/subst-fix1.json)을 triggers.json·evidence.json 에 적용한다
"""
사용: uv run --frozen python -X utf8 .agents/plans/v21-first-run-2026-10/work/apply_subst.py <slug> <subst.json> [--dry-run] [--skip ID,ID]

목록 모양은 SUBST-INSTRUCTIONS.md 「출력」. 항목마다 old 가 그 칸 값 안에 정확히 한 번 나와야 하고, 하나라도 어긋나면 아무것도 쓰지 않는다.
적용 뒤 load_context 로 검증하고 실패하면 되돌린다.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard.engine import load_context  # noqa: E402
from scorecard.paths import run_paths  # noqa: E402

STEP = re.compile(r"([A-Za-z_]+)(?:\[(\d+)\])?")


def load(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def locate(item: dict, field: str):
    """점 경로의 부모 컨테이너와 마지막 키(또는 첨자)를 돌려준다."""
    node, parts = item, field.split(".")
    for i, part in enumerate(parts):
        m = STEP.fullmatch(part)
        if not m:
            raise SystemExit(f"경로 형식 오류 {field!r}")
        key, idx = m.group(1), m.group(2)
        last = i == len(parts) - 1
        if idx is None:
            if last:
                return node, key
            node = node[key]
        else:
            if last:
                return node[key], int(idx)
            node = node[key][int(idx)]
    raise SystemExit(f"빈 경로 {field!r}")


def main() -> int:
    args = sys.argv[1:]
    slug, subst_path = args[0], Path(args[1])
    dry = "--dry-run" in args
    skip = set(args[args.index("--skip") + 1].split(",")) if "--skip" in args else set()
    paths = run_paths(slug)
    files = {"triggers": (paths.triggers, "trigger_id"), "evidence": (paths.evidence, "evidence_id")}
    payloads = {k: load(p) for k, (p, _) in files.items()}
    index = {k: {it[idk]: it for it in payloads[k]["items"]} for k, (_, idk) in files.items()}

    errors, done = [], []
    for n, s in enumerate(load(subst_path)["items"]):
        if s["id"] in skip:
            continue
        item = index[s["file"]].get(s["id"])
        if item is None:
            errors.append(f"[{n}] {s['id']} 가 {s['file']} 에 없다"); continue
        try:
            parent, key = locate(item, s["field"])
            value = parent[key]
        except (KeyError, IndexError, TypeError):
            errors.append(f"[{n}] {s['id']}.{s['field']} 칸이 없다"); continue
        count = value.count(s["old"]) if isinstance(value, str) else 0
        if count != 1:
            errors.append(f"[{n}] {s['id']}.{s['field']}: old 가 {count}번 나온다"); continue
        parent[key] = value.replace(s["old"], s["new"])
        done.append(f"{s['id']}.{s['field']}" + (f" (depends_on {','.join(s['depends_on'])})" if s.get("depends_on") else ""))
    if errors:
        print("\n".join(errors)); print("[중단] 아무것도 쓰지 않았다"); return 1
    print(f"치환 {len(done)}건:\n  " + "\n  ".join(done))
    if dry:
        return 0
    backup = {p: p.read_bytes() for p, _ in files.values()}
    for k, (p, _) in files.items():
        p.write_text(json.dumps(payloads[k], ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    try:
        load_context(slug)
    except BaseException as exc:
        for p, b in backup.items():
            p.write_bytes(b)
        print(f"[실패] 검증 실패로 되돌렸다: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
