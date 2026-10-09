# 승인 취소 뒤 수정(2026-10-09): Anthropic ⑤⑧ 판단 변경을 트리거 관찰 문장 세 건에 반영한다
"""
사용: uv run --frozen python -X utf8 .agents/plans/rejudge-all-2026-11/work/fix_triggers_r3.py <slug> [--dry-run]
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "scripts"))
from scorecard.schema import load_json_strict, write_json  # noqa: E402


def sub(obj: dict, key: str, old: str, new: str, where: str) -> None:
    cur = obj.get(key) or ""
    if old not in cur:
        raise SystemExit(f"[{where}.{key}] '{old[:50]}' 가 없다")
    obj[key] = cur.replace(old, new)


def main() -> int:
    slug = sys.argv[1]
    dry = "--dry-run" in sys.argv
    p = ROOT / "output" / slug / "triggers.json"
    trg = load_json_strict(p)
    T = {t["trigger_id"]: t for t in trg["items"]}
    for tid in ("TRG-037", "TRG-038"):
        sub(T[tid], "observation",
            "Anthropic ⑤ 판단의 적대 등급은 −2(구조형: 큰 고객 둘이 경쟁사 소유가 됨)이고, 정부 거래 배제나 규제 조사 같은 비용형 적대는 그 등급을 바꾸지 않는다.",
            "Anthropic ⑤ 판단의 적대 등급은 −1(비용형)이다. 큰 고객 둘이 경쟁사 소유가 된 사실은 그 고객의 매출 비중이 공개 제출본으로 확인되지 않아 구조형으로 올리지 않았고, "
            "정부 거래 배제나 규제 조사는 비용형이라 등급을 바꾸지 않는다.", tid)
    sub(T["TRG-070"], "observation",
        "고객 축은 매출의 약 4분의 1 이 고객 두 곳에서 나온다는 보도로 −2 를 따로 적는다.",
        "고객 축은 매출의 약 4분의 1 이 고객 두 곳에서 나온다는 보도가 공개 제출본의 집중 공시가 아니라 미확인으로 둔다.", "TRG-070")
    if dry:
        print("dry-run: 바꿀 문자열을 모두 찾았다"); return 0
    write_json(p, trg)
    print("트리거 3건 고침")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
