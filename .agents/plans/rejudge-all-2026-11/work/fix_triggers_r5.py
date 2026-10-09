# 4차 확인 리뷰 L2 — Oracle ⑧ 의 낡은 진술이 남은 트리거 셋(TRG-058 관찰, TRG-023·022 재검토)을 고친다
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "scripts"))
from scorecard.schema import load_json_strict, write_json  # noqa: E402


def sub(obj, key, old, new, where):
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
    sub(T["TRG-058"], "observation", "⑧ -4, ⑨ -3", "⑧ −3, ⑨ −3", "TRG-058")
    sub(T["TRG-023"]["recheck"], "what", "⑦ 의 '조달 의존 큼' 과 ⑧ 의 단일 고객 의존 판정을 뒤집을 만큼인지가 기준이다",
        "⑦ 의 '조달 의존 큼' 을 뒤집을 만큼인지, ⑧ 에서 미확인으로 둔 고객 축을 잴 공시나 회사 1차 자료가 나왔는지가 기준이다", "TRG-023")
    sub(T["TRG-022"]["recheck"], "what", "⑧ 의 단일 고객 설비 의존 근거가 달라지는지 본다",
        "⑧ 의 약정 축(미개시 리스와 무조건 구매 약정 ÷ 최근 1년 매출) 근거가 달라지는지 본다", "TRG-022")
    if dry:
        print("dry-run: 찾았다"); return 0
    write_json(p, trg); print("트리거 3건 고침"); return 0


if __name__ == "__main__":
    raise SystemExit(main())
