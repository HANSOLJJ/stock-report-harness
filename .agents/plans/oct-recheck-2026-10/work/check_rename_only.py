# 표시 이름 변경 전후의 results.json·draft.md 를 대조해 이름 말고는 바뀐 것이 없음을 확인한다(git 의 이전 판과 비교)
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]


def git_show(ref: str, path: str) -> str:
    return subprocess.run(["git", "show", f"{ref}:{path}"], capture_output=True, text=True, encoding="utf-8", cwd=ROOT, check=True).stdout


def strip(obj, drop=("display_name", "results_hash", "input_hashes")):
    if isinstance(obj, dict):
        return {k: strip(v) for k, v in obj.items() if k not in drop}
    if isinstance(obj, list):
        return [strip(v) for v in obj]
    return obj


def main() -> int:
    slug, ref = sys.argv[1], sys.argv[2]
    base = f"output/{slug}"
    old = json.loads(git_show(ref, f"{base}/results.json"))
    new = json.loads((ROOT / base / "results.json").read_text(encoding="utf-8"))
    same_results = strip(old) == strip(new)
    names = sorted({(c["company_id"], c["display_name"]) for c in new["companies"]} - {(c["company_id"], c["display_name"]) for c in old["companies"]})
    old_d = git_show(ref, f"{base}/draft.md").replace("SpaceX + xAI", "SpaceX")
    new_d = (ROOT / base / "draft.md").read_text(encoding="utf-8")
    same_draft = old_d.replace("\r\n", "\n") == new_d.replace("\r\n", "\n")
    print(f"results(이름·해시 제외) 같음: {same_results}, 바뀐 이름: {names}")
    print(f"draft(옛 이름을 새 이름으로 바꾼 뒤) 같음: {same_draft}")
    if not same_draft:
        a, b = old_d.splitlines(), new_d.replace("\r\n", "\n").splitlines()
        diff = [(i, x, y) for i, (x, y) in enumerate(zip(a, b)) if x != y][:10]
        for i, x, y in diff:
            print(f"  {i}: - {x[:140]}\n     + {y[:140]}")
        print(f"  줄 수 {len(a)} → {len(b)}")
    return 0 if same_results and same_draft else 1


if __name__ == "__main__":
    raise SystemExit(main())
