# 원문을 다시 읽어 발췌를 고친 근거에서 '제목만 보고 판정함' 류의 미확인·반론 문장을 빼고 관련성 문장의 '제목' 표현을 고친다
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "scripts"))
from scorecard.paths import run_paths  # noqa: E402
from scorecard.schema import load_json_strict, write_json  # noqa: E402

TITLE_UNV = re.compile(r"제목|본문 미열람|원문 미열람|본문·웹|웹 조회|웹 미조회|Item 번호만|양식·")
TITLE_CE = re.compile(r"제목만으로|제목에 |제목 기준|제목은 |제목으로")
REL_SUBS = [("제목이다", "보도다"), ("제목이 ", "보도가 "), ("제목에 따르면", "보도에 따르면"), ("제목으로만", "보도로만"),
            ("제목으로", "보도로"), ("제목뿐", "보도"), ("제목", "보도")]


def main() -> int:
    slug = sys.argv[1]
    dry = "--dry-run" in sys.argv
    ids = [e["evidence_id"] for v in json.loads((Path(__file__).parent / "title-only-evidence.json").read_text(encoding="utf-8")).values()
           for e in v]
    p = run_paths(slug).evidence
    payload = load_json_strict(p)
    changed = 0
    for e in payload["items"]:
        if e["evidence_id"] not in ids or e.get("status") != "confirmed":
            continue
        before = json.dumps([e["unverified"], e["counter_evidence"], e["relevance"]], ensure_ascii=False)
        e["unverified"] = [u for u in e.get("unverified") or [] if not TITLE_UNV.search(u)]
        e["counter_evidence"] = [c for c in e.get("counter_evidence") or [] if not TITLE_CE.search(c)]
        rel = e["relevance"]
        for old, new in REL_SUBS:
            rel = rel.replace(old, new)
        e["relevance"] = rel
        if json.dumps([e["unverified"], e["counter_evidence"], e["relevance"]], ensure_ascii=False) != before:
            changed += 1
            print(f"{e['evidence_id']}: rel={rel[:90]} | unv={e['unverified']} | ce={e['counter_evidence']}")
    if not dry:
        write_json(p, payload)
    print(f"고친 근거 {changed}건")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
