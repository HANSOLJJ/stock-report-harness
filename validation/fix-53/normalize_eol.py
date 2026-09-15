# FIX-53 RC-07: .gitattributes 의 eol 속성대로 작업 트리 파일 줄끝을 맞춘다 — 새 checkout 과 같은 바이트가 되게 한다
"""대상은 git 추적 파일과 drafts/ 생성물 중 eol 속성이 붙은 것. 내용은 바꾸지 않고 줄끝만 바꾼다.
어떤 파일이 바뀌었는지 출력한다. 재실행하면 바뀌는 파일이 없다."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def eol_attr(paths: list[str]) -> dict[str, str]:
    out = subprocess.run(["git", "check-attr", "eol", "--"] + paths, capture_output=True, text=True, cwd=ROOT,
                         encoding="utf-8").stdout
    attrs = {}
    for line in out.splitlines():
        path, _, value = line.rpartition(": eol: ")
        attrs[path] = value.strip()
    return attrs


def main() -> int:
    tracked = subprocess.run(["git", "ls-files", "scorecard", "research", "reviews"], capture_output=True, text=True,
                             cwd=ROOT, encoding="utf-8").stdout.split()
    drafts = [str(p.relative_to(ROOT)).replace("\\", "/") for p in (ROOT / "drafts").glob("*.md")]
    attrs = eol_attr(tracked + drafts)
    changed = []
    for rel, value in sorted(attrs.items()):
        if value not in ("lf", "crlf"):
            continue
        path = ROOT / rel
        if not path.is_file():
            continue
        data = path.read_bytes()
        lf = data.replace(b"\r\n", b"\n")
        target = lf if value == "lf" else lf.replace(b"\n", b"\r\n")
        if target != data:
            path.write_bytes(target)
            changed.append(f"{value.upper():4} {rel}")
    print(f"줄끝 변경 {len(changed)}건")
    for line in changed:
        print("  " + line)
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    sys.exit(main())
