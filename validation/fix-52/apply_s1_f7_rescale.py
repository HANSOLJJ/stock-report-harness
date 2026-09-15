# FIX-52 S1: F7 매트릭스 large|yes 를 -3 → -2 로 재척도하고 nvidia·oracle F7 판단을 교체한다 (사용자 결정)
"""v1.7 함정 재배분(F7 -3→-2)에서 range 만 줄고 매트릭스와 승계 판단이 따라가지 않았다(리뷰 C codex 발견).
사용자 결정은 **range 를 유지하고 매트릭스를 재척도**하는 것이다.

재실행해도 같은 결과가 나온다. 파일 줄끝은 원래 것을 유지한다(HASH-EOL).
"""
from __future__ import annotations

import copy
import io
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard.rules import load_rules  # noqa: E402
from scorecard.schema import load_json_strict, validate_judgments, validate_rules  # noqa: E402

RUN_ID = "ai-scorecard-2026-09-obsreg"
RUN = ROOT / "scorecard" / "runs" / RUN_ID
RULES = ROOT / "scorecard" / "rules" / "v1.7.json"
DATE = "2026-09-15"
SUFFIX = "fix52"
REVIEWER = "설계진행(리뷰 C codex 발견 · 사용자 결정)"
TARGETS = ("nvidia", "oracle")


def load(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def dump(p: Path, d: dict) -> None:
    raw = io.open(p, encoding="utf-8", newline="").read()
    nl = "\r\n" if "\r\n" in raw else "\n"
    out = json.dumps(d, ensure_ascii=False, indent=2) + ("\n" if raw.endswith("\n") else "")
    io.open(p, "w", encoding="utf-8", newline="").write(out.replace("\n", nl))


def update_rules(rules: dict) -> None:
    f7 = rules["factors"]["F7"]
    f7["matrix"]["large|yes"] = -2
    f7["matrix_rescale"] = {
        "decided_at": DATE,
        "decided_by": "사용자 (리뷰 C codex 발견 · FIX-52)",
        "change": "`large|yes` -3 → -2. 나머지 세 칸(small|no 0 · small|yes -1 · large|no -2)은 그대로다.",
        "why": ("v1.7 함정 재배분(F6 -5→-7 · F7 -3→-2 · F9 -5→-4, 합 -18 보존)에서 range 는 [-2,0] 으로 줄었는데 "
                "매트릭스와 승계 판단이 따라가지 않아 nvidia·oracle 이 range 밖 -3 을 받았다. 스키마가 F6·F9 정책만 "
                "검사해서 통과했다. **range 를 유지하고 매트릭스를 맞춘다.**"),
        "discrimination_loss": ("**변별력 손실이 있다.** `large|no` 와 `large|yes` 가 둘 다 -2 가 되어, 조달 의존 고객 "
                                "비중이 큰 쪽에서는 세로축(내 돈이 고객 주머니로 갔다가 내 매출로 돌아오나)이 점수를 "
                                "가르지 못한다. 별표 I 317행이 세로축을 두는 이유(`돌아오면 그 매출은 내가 만든 것이라 더 "
                                "가짜다`)가 큰 쪽에서는 점수에 반영되지 않는다."),
        "current_impact": ("**현재 14개사 점수에는 영향이 없다.** v1.5 판정표(채점규칙 339행)에서 `large|no`(-2)는 "
                           "`(v1.5 해당 없음 — 예약)` 이었다. large 칸에 있는 기업은 nvidia·oracle 둘이고 둘 다 "
                           "`large|yes` 라, 두 칸이 같아져도 서로 다른 점수를 받던 기업이 같은 점수로 합쳐지는 일은 "
                           "없다. 두 기업의 F7 은 -3 → -2 로 한 칸씩 오른다."),
        "reopen_condition": "`large|no` 에 해당하는 기업이 생기면 세로축 변별력 손실이 실제 점수에 닿으므로 다시 본다.",
    }


def restore(item: dict) -> dict:
    if "superseded" not in item:
        return item
    sup = item["superseded"]
    old = {"judgment_id": sup["judgment_id"], "company_id": item["company_id"], "factor": item["factor"],
           "kind": item["kind"], "score": sup.get("score"), "inputs": sup["inputs"], "evidence": sup["evidence"],
           "counter_evidence": sup.get("counter_evidence", []), "note": sup.get("note"),
           "reviewer": sup["reviewer"], "reviewed_at": sup["reviewed_at"], "status": sup.get("status", "carried")}
    for key in ("carried_from", "source_ids"):
        if key in sup:
            old[key] = sup[key]
    return old


def update_judgments(jud: dict) -> list[str]:
    done = []
    for i, item in enumerate(jud["items"]):
        cid = item["company_id"]
        if item["factor"] != "F7" or cid not in TARGETS:
            continue
        old = restore(item)
        sup = {k: copy.deepcopy(old[k]) for k in ("judgment_id", "score", "inputs", "evidence", "reviewer",
                                                  "reviewed_at", "status", "carried_from", "note",
                                                  "counter_evidence", "source_ids") if k in old}
        sup["superseded_at"] = DATE
        sup["why"] = ("F7 매트릭스 재척도(사용자 결정, FIX-52). 두 축 입력(large|yes)은 그대로이고 그 칸의 점수가 "
                      "-3 → -2 로 바뀌었다. 옛 근거 첫 줄의 `-3` 은 재척도 전 점수다.")
        header = (f"📐 **[FIX-52 재척도 {DATE}] F7 = -2.** 매트릭스 `large|yes` 칸이 -3 → -2 로 바뀌었다(v1.7 range "
                  "[-2,0], 사용자 결정). 두 축 판정(조달 의존 고객 비중 큼 · 내 돈이 돌아옴)은 바뀌지 않았다. 아래 첫 줄의 "
                  "`-3` 은 v1.5 문면이며 재척도 전 점수다.")
        new = {
            "judgment_id": f"{cid}.F7.{SUFFIX}",
            "company_id": cid,
            "factor": "F7",
            "kind": old["kind"],
            "score": None,
            "inputs": copy.deepcopy(old["inputs"]),
            "evidence": [header] + copy.deepcopy(old["evidence"]),
            "counter_evidence": copy.deepcopy(old.get("counter_evidence", [])),
            "note": ((old.get("note") or "") + " | [FIX-52] 매트릭스 재척도로 -3 → -2. **large 쪽에서 세로축이 점수를 "
                     "가르지 못한다** — factors.F7.matrix_rescale 참조. 옛 판단은 superseded 에 있다."),
            "reviewer": REVIEWER,
            "reviewed_at": DATE,
            "status": "new",
            "source_ids": copy.deepcopy(old.get("source_ids", ["SRC-v15-html"])),
            "previous_judgment_id": old["judgment_id"],
            "superseded": sup,
        }
        jud["items"][i] = new
        done.append(cid)
    return done


def main() -> int:
    rules = load(RULES)
    update_rules(rules)
    validate_rules(rules)
    dump(RULES, rules)

    jpath = RUN / "judgments.json"
    jud = load(jpath)
    done = update_judgments(jud)
    registry = {c["company_id"]: c for c in load_json_strict(ROOT / "scorecard" / "companies.json")["companies"]}
    validate_judgments(jud, registry, rules, RUN_ID)
    dump(jpath, jud)

    run_path = RUN / "run.json"
    raw = io.open(run_path, encoding="utf-8", newline="").read()
    old = json.loads(raw)["rule_hash"]
    new = load_rules("v1.7").hash
    if old != new:
        io.open(run_path, "w", encoding="utf-8", newline="").write(raw.replace(old, new))
    print(f"F7 matrix large|yes = {rules['factors']['F7']['matrix']['large|yes']}")
    print(f"판단 교체: {', '.join(done)}")
    print(f"rule_hash {old[:12]} -> {new[:12]}")
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    sys.exit(main())
