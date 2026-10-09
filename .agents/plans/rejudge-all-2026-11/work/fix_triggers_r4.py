# 3차 확인 리뷰 반영: Oracle ⑧ 변경을 트리거 TRG-022 관찰 문장에 반영한다
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "scripts"))
from scorecard.schema import load_json_strict, write_json  # noqa: E402


def main() -> int:
    slug = sys.argv[1]
    dry = "--dry-run" in sys.argv
    p = ROOT / "output" / slug / "triggers.json"
    trg = load_json_strict(p)
    T = {t["trigger_id"]: t for t in trg["items"]}
    old = "지금 Oracle ⑧ 판단은 -4(단일 고객이 백로그의 절반)"
    new = "지금 Oracle ⑧ 판단은 −3(약정 축: 미개시 데이터센터 리스와 무조건 구매 약정이 최근 1년 매출의 약 4.5배. OpenAI 의 백로그 몫은 2차 보도뿐이라 고객 축은 미확인)"
    if old not in T["TRG-022"]["observation"]:
        raise SystemExit("TRG-022 문장을 찾지 못했다")
    T["TRG-022"]["observation"] = T["TRG-022"]["observation"].replace(old, new)
    if dry:
        print("dry-run: 찾았다"); return 0
    write_json(p, trg); print("TRG-022 고침"); return 0


if __name__ == "__main__":
    raise SystemExit(main())
