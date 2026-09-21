# git 이 추적하지 않는 산출물(output·plan·drafts)을 작업 워크트리에서 원본 저장소로 복사한다
"""
`output/` · `plan/` · `drafts/` 는 `.gitignore` 대상이라 브랜치를 병합해도 따라오지 않는다.
워커가 빌드한 리포트를 원본 저장소에서 보려면 파일을 직접 옮겨야 한다.

    python scripts/sync_outputs.py                     # 워커 → 원본, 무엇이 바뀌는지만 보여준다
    python scripts/sync_outputs.py --apply             # 실제로 복사한다
    python scripts/sync_outputs.py --from <경로> --to <경로> --apply

`validation/**/_raw/` 는 검증 원자료라 리포트를 보는 것과 무관해서 넣지 않았다.
필요하면 DIRS 에 더하면 된다.
"""
import argparse
import hashlib
import shutil
import sys
from pathlib import Path

SRC = Path("C:/Users/noble/orca/workspaces/stock-report-harness/worker")
DST = Path("E:/sourcecode/01_side_project/stock-report-harness")
DIRS = ("output", "plan", "drafts")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--from", dest="src", type=Path, default=SRC, help="복사해 올 워크트리")
    ap.add_argument("--to", dest="dst", type=Path, default=DST, help="복사해 넣을 원본 저장소")
    ap.add_argument("--apply", action="store_true", help="실제로 복사한다. 없으면 보여주기만 한다")
    args = ap.parse_args()

    if not args.src.is_dir():
        sys.exit(f"원본 워크트리가 없습니다: {args.src}")
    if not args.dst.is_dir():
        sys.exit(f"대상 저장소가 없습니다: {args.dst}")

    added = changed = same = 0
    for name in DIRS:
        root = args.src / name
        if not root.is_dir():
            continue
        for src_file in sorted(p for p in root.rglob("*") if p.is_file()):
            rel = src_file.relative_to(args.src)
            dst_file = args.dst / rel
            if not dst_file.exists():
                mark, added = "신규", added + 1
            elif digest(src_file) != digest(dst_file):
                mark, changed = "갱신", changed + 1
            else:
                same += 1
                continue
            print(f"  {mark}  {rel.as_posix()}  ({src_file.stat().st_size:,} bytes)")
            if args.apply:
                dst_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_file, dst_file)

    print(f"\n신규 {added} · 갱신 {changed} · 그대로 {same}")
    if not args.apply and (added or changed):
        print("실제로 복사하려면 --apply 를 붙이십시오.")


if __name__ == "__main__":
    main()
