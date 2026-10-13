# (2026-10 v2.1 첫 실행) 리뷰 뒤 수정 묶음의 새 출처·근거·트리거를 실행 묶음에 덧붙이고, 수정 판단 파일의 NEW:<key> 를 새 번호로 바꾼다
"""
사용: uv run --frozen python -X utf8 .agents/plans/v21-first-run-2026-10/work/add_fix_items.py <slug> <items.json> [--dir judge-fix1] [--dry-run]

merge_group_outputs.py 는 트리거를 이전 실행의 관찰 항목으로 다시 만들어 이 실행이 새로 붙인 트리거를 지우므로, 수정 묶음에는 이 도구를 쓴다.
덧붙이기만 하고 기존 항목은 고치지 않는다.

items.json 모양
{
  "sources": [ sources.json 항목(source_id 를 비우면 SRC-WEB-<company>-NNN 부여) ],
  "evidence": [ {"key": "maia-primary", evidence.json 항목에서 evidence_id·status 를 뺀 것} ],
  "new_triggers": [ {"key": "maia-nvda", triggers.json 항목에서 trigger_id 를 뺀 것} ]
}
key 는 근거·트리거를 통틀어 유일하다. items.json 자신과 --dir 폴더의 F*-*.json 안의 문자열에서 "NEW:<key>" 를 새 ID 로 바꾼다
(문장 속 표지 "[NEW:maia-primary]" 도 바꾼다). 근거는 candidate 로 들어가므로 원문을 확인한 뒤 `scorecard_cli.py confirm` 으로 확정한다.
"""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard.engine import load_context, run_dir  # noqa: E402
from scorecard.paths import run_paths  # noqa: E402

WORK = Path(__file__).resolve().parent
TODAY = "2026-10-13"
TOKEN = re.compile(r"NEW:([A-Za-z0-9_-]+)")


def load(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def dump(p: Path, obj) -> None:
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def replace(obj, mapping):
    if isinstance(obj, str):
        def sub(m):
            if m.group(1) not in mapping:
                raise SystemExit(f"key {m.group(1)!r} 를 찾지 못했다")
            return mapping[m.group(1)]
        return TOKEN.sub(sub, obj)
    if isinstance(obj, list):
        return [replace(x, mapping) for x in obj]
    if isinstance(obj, dict):
        return {k: replace(v, mapping) for k, v in obj.items()}
    return obj


def main() -> int:
    args = sys.argv[1:]
    slug, items_path = args[0], Path(args[1])
    dry = "--dry-run" in args
    fix_dir = WORK / (args[args.index("--dir") + 1] if "--dir" in args else "judge-fix1")
    paths = run_paths(slug)
    d = run_dir(slug)
    evidence, triggers, sources = load(paths.evidence), load(paths.triggers), load(d / "sources.json")
    spec = load(items_path)

    ev_max: dict[str, int] = defaultdict(int)
    for e in evidence["items"]:
        ev_max[e["company_id"]] = max(ev_max[e["company_id"]], int(e["evidence_id"].rsplit("-", 1)[1]))
    src_ids = {s["source_id"] for s in sources["items"]}
    web_max: dict[str, int] = defaultdict(int)
    for sid in src_ids:
        m = re.fullmatch(r"SRC-WEB-([a-z0-9-]+)-(\d{3})", sid)
        if m:
            web_max[m.group(1)] = max(web_max[m.group(1)], int(m.group(2)))
    trg_max = max(int(t["trigger_id"].split("-")[1]) for t in triggers["items"])

    mapping: dict[str, str] = {}
    new_sources, new_evidence, new_trg = [], [], []
    for s in spec.get("sources") or []:
        s = dict(s)
        if not s.get("source_id"):
            web_max[s["company_id"]] += 1
            s["source_id"] = f"SRC-WEB-{s['company_id']}-{web_max[s['company_id']]:03d}"
        if s["source_id"] in src_ids:
            raise SystemExit(f"출처 ID 중복 {s['source_id']}")
        if s.get("key"):
            mapping[s.pop("key")] = s["source_id"]
        s.setdefault("sha256", None); s.setdefault("conflict_of_interest", None); s.setdefault("note", None)
        s.setdefault("accessed_at", TODAY)
        src_ids.add(s["source_id"]); new_sources.append(s)
    for e in spec.get("evidence") or []:
        e = dict(e)
        key = e.pop("key")
        if key in mapping:
            raise SystemExit(f"key 중복 {key!r}")
        cid = e["company_id"]
        ev_max[cid] += 1
        mapping[key] = e["evidence_id"] = f"EV-{cid}-{ev_max[cid]:03d}"
        e["status"] = "candidate"
        e.setdefault("change_vs_previous", "new"); e.setdefault("counter_evidence", []); e.setdefault("unverified", [])
        new_evidence.append(e)
    for t in spec.get("new_triggers") or []:
        t = dict(t)
        key = t.pop("key")
        if key in mapping:
            raise SystemExit(f"key 중복 {key!r}")
        trg_max += 1
        mapping[key] = t["trigger_id"] = f"TRG-{trg_max:03d}"
        t.setdefault("evidence_ids", []); t.setdefault("source_ids", []); t.setdefault("status", "watching")
        new_trg.append(t)

    new_sources, new_evidence, new_trg = (replace(x, mapping) for x in (new_sources, new_evidence, new_trg))
    print("새 번호: " + ", ".join(f"{k}→{v}" for k, v in mapping.items()))
    if dry:
        return 0

    sources["items"].extend(new_sources)
    evidence["items"].extend(new_evidence)
    triggers["items"].extend(new_trg)
    targets = [paths.evidence, paths.triggers, d / "sources.json"]
    judge_files = sorted(f for f in fix_dir.glob("F*-*.json") if not f.name.endswith(".propose.json"))
    backup = {p: p.read_bytes() for p in targets + judge_files}
    dump(paths.evidence, evidence); dump(paths.triggers, triggers); dump(d / "sources.json", sources)
    patched = 0
    for jf in judge_files:
        old = load(jf)
        new = replace(old, mapping)
        if new != old:
            dump(jf, new); patched += 1
    try:
        load_context(slug)
    except BaseException as exc:
        for p, b in backup.items():
            p.write_bytes(b)
        print(f"[실패] 검증 실패로 되돌렸다: {exc}")
        return 1
    print(f"출처 +{len(new_sources)}, 근거 +{len(new_evidence)}, 트리거 +{len(new_trg)}, 판단 파일 {patched}개에서 NEW:<key> 를 바꿨다")
    print("confirm:", ",".join(e["evidence_id"] for e in new_evidence))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
