# 회사 묶음 에이전트의 산출물(work/out-<G>.json)을 재실행 묶음(evidence·triggers·observations·sources)에 합친다
"""
사용: uv run --frozen python -X utf8 .agents/plans/rejudge-all-2026-11/work/merge_group_outputs.py <slug> <prior_slug> out-A.json [out-B.json …]

입력 파일 모양
{
  "group": "A",
  "sources": [ sources.json 항목(source_id 는 SRC-WEB-<company>-NNN 으로 새로 부여해도 되고 비워 두면 여기서 부여) ],
  "evidence": [ evidence.json 항목에서 evidence_id 를 뺀 것 + "verified_original": true|false ],
  "triggers": [ {"trigger_id": "TRG-001", "status", "deadline", "finding", "evidence_ids", "source_ids", "note"?, "condition"?, "observation"?} ],
  "new_triggers": [ triggers.json 항목에서 trigger_id 를 뺀 것 ],
  "observations": [ observations.json 항목에서 observation_id 를 뺀 것(있으면 그대로) ]
}
합친 뒤 load_context 로 검증하고, 실패하면 아무 파일도 쓰지 않는다. verified_original 인 근거 ID 목록을 출력한다(confirm 용).
"""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]   # work → rejudge-all-2026-11 → plans → .agents → 저장소 루트
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard.engine import load_context, run_dir  # noqa: E402
from scorecard.paths import run_paths  # noqa: E402

TODAY = "2026-10-08"


def load(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def dump(p: Path, obj) -> None:
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def main() -> int:
    slug, prior, *files = sys.argv[1:]
    paths = run_paths(slug)
    d = run_dir(slug)
    evidence = load(paths.evidence)
    triggers = load(paths.triggers)
    observations = load(d / "observations.json")
    sources = load(d / "sources.json")
    prior_triggers = {t["trigger_id"]: t for t in load(run_paths(prior).triggers)["items"]}

    ev_max: dict[str, int] = defaultdict(int)
    existing_keys: dict[tuple[str, str], str] = {}
    for e in evidence["items"]:
        ev_max[e["company_id"]] = max(ev_max[e["company_id"]], int(e["evidence_id"].rsplit("-", 1)[1]))
        existing_keys[(e["source_id"], e["title"])] = e["evidence_id"]
    src_ids = {s["source_id"] for s in sources["items"]}
    web_max: dict[str, int] = defaultdict(int)
    for sid in src_ids:
        m = re.fullmatch(r"SRC-WEB-([a-z0-9-]+)-(\d{3})", sid)
        if m:
            web_max[m.group(1)] = max(web_max[m.group(1)], int(m.group(2)))
    trg_max = max(int(t["trigger_id"].split("-")[1]) for t in triggers["items"])
    obs_ids = {o["observation_id"] for o in observations["items"]}

    # 이번 실행의 트리거는 이전 실행의 관찰 중 항목만 이어받는다. 이전 실행에서 결론이 난 항목(철회·발동·만료)은 그 실행의 기록이다.
    kept = {t["trigger_id"]: dict(t) for t in triggers["items"] if prior_triggers.get(t["trigger_id"], {}).get("status") == "watching"}
    handled: set[str] = set()
    to_confirm: list[str] = []
    new_evidence: list[dict] = []
    new_sources: list[dict] = []
    new_obs: list[dict] = []
    new_trg: list[dict] = []

    for f in files:
        out = load(Path(f))
        # 출처
        for s in out.get("sources") or []:
            s = dict(s)
            if not s.get("source_id"):
                web_max[s["company_id"]] += 1
                s["source_id"] = f"SRC-WEB-{s['company_id']}-{web_max[s['company_id']]:03d}"
            if s["source_id"] in src_ids:
                continue
            s.setdefault("sha256", None); s.setdefault("conflict_of_interest", None); s.setdefault("note", None)
            s.setdefault("publisher", None); s.setdefault("accessed_at", TODAY)
            src_ids.add(s["source_id"]); new_sources.append(s)
        # 근거
        for e in out.get("evidence") or []:
            e = dict(e)
            verified = bool(e.pop("verified_original", False))
            cid = e["company_id"]
            dup = existing_keys.get((e["source_id"], e["title"]))
            if dup and not e.get("previous_evidence_id"):
                # 묶음이 56건짜리 파일을 보고 중복 검사를 했을 수 있다. 같은 출처·제목이 이미 있으면 알리고, 본문 발췌로 보강한 것이면
                # previous_evidence_id 로 잇는다(change_vs_previous: updated). 그냥 중복이면 사람이 지운다.
                print(f"[중복 의심] {f}: {cid} '{e['title'][:60]}' 는 {dup} 과 출처·제목이 같다 → previous_evidence_id={dup}, change_vs_previous=updated 로 잇는다")
                e["previous_evidence_id"] = dup
                e["change_vs_previous"] = "updated"
            ev_max[cid] += 1
            e["evidence_id"] = f"EV-{cid}-{ev_max[cid]:03d}"
            e.setdefault("status", "candidate")
            e.setdefault("change_vs_previous", "new")
            e.setdefault("counter_evidence", []); e.setdefault("unverified", [])
            new_evidence.append(e)
            if verified:
                to_confirm.append(e["evidence_id"])
        # 이전 트리거 carry
        for t in out.get("triggers") or []:
            tid = t["trigger_id"]
            if tid not in kept:
                raise SystemExit(f"{f}: {tid} 는 이전 실행의 관찰 중 트리거가 아니다")
            item = kept[tid]
            for k in ("status", "deadline", "condition", "observation", "note"):
                if t.get(k) is not None:
                    item[k] = t[k]
            item["evidence_ids"] = sorted(set(item.get("evidence_ids") or []) | set(t.get("evidence_ids") or []))
            item["source_ids"] = sorted(set(item.get("source_ids") or []) | set(t.get("source_ids") or []))
            item["carry"] = {"ref": f"{prior}:{tid}", "checked_at": t.get("checked_at") or TODAY, "finding": t["finding"]}
            handled.add(tid)
        # 새 트리거
        for t in out.get("new_triggers") or []:
            t = dict(t); trg_max += 1
            t["trigger_id"] = f"TRG-{trg_max:03d}"
            t.setdefault("evidence_ids", []); t.setdefault("source_ids", []); t.setdefault("status", "watching")
            new_trg.append(t)
        # 관측
        for o in out.get("observations") or []:
            o = dict(o)
            if not o.get("observation_id"):
                o["observation_id"] = f"{o['company_id']}.{o['metric']}.{o['as_of']}.rejudge"
            if o["observation_id"] in obs_ids:
                raise SystemExit(f"{f}: 관측 ID 중복 {o['observation_id']}")
            obs_ids.add(o["observation_id"])
            o.setdefault("kind", "actual"); o.setdefault("status", "verified"); o.setdefault("observed_at", TODAY)
            new_obs.append(o)

    missing = sorted(set(kept) - handled)
    if missing:
        print(f"[경고] carry 가 없는 이전 관찰 트리거 {len(missing)}건: {', '.join(missing)}")

    evidence["items"].extend(new_evidence)
    triggers["items"] = list(kept.values()) + new_trg
    observations["items"].extend(new_obs)
    sources["items"].extend(new_sources)

    backup = {p: p.read_bytes() for p in (paths.evidence, paths.triggers, d / "observations.json", d / "sources.json")}
    dump(paths.evidence, evidence); dump(paths.triggers, triggers)
    dump(d / "observations.json", observations); dump(d / "sources.json", sources)
    try:
        load_context(slug)
    except BaseException as exc:
        for p, b in backup.items():
            p.write_bytes(b)
        print(f"[실패] 검증 실패로 되돌렸다: {exc}")
        return 1
    print(f"근거 +{len(new_evidence)} (확정 대상 {len(to_confirm)}), 트리거 이어받음 {len(handled)}/{len(kept)} + 새 {len(new_trg)}, "
          f"관측 +{len(new_obs)}, 출처 +{len(new_sources)}")
    print("confirm:", ",".join(to_confirm))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
