# 세 회사 공시 캐시(HTML)에서 ⑧ 약정 축 문장을 찾아 원문 그대로 보여 준다(근거 등록 전 대조용)
from __future__ import annotations

import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
DOCS = ROOT / "data" / "_sec" / "docs"
TARGETS = {
    "goog": ["fixed or guaranteed commitments under these agreements were", "that have not yet commenced with future lease payments of",
             "short-term lease agreement with a non-cancelable commitment"],
    "msft": ["that had not yet commenced of", "Construction commitments", "Purchase commitments"],
    "meta": ["These lease obligations were approximately", "non-cancelable contractual commitments"],
}


def text_of(path: Path) -> str:
    raw = path.read_text(encoding="utf-8", errors="replace")
    raw = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", raw, flags=re.S | re.I)
    t = html.unescape(re.sub(r"<[^>]+>", " ", raw))
    return re.sub(r"\s+", " ", t)


def main() -> int:
    for key, needles in TARGETS.items():
        f = next(DOCS.glob(f"*-{key}-20260630.htm"))
        t = text_of(f)
        print(f"===== {f.name}")
        for n in needles:
            hits = [m.start() for m in re.finditer(re.escape(n), t)]
            print(f"-- '{n}' {len(hits)}건")
            for h in hits[:3]:
                print("   ", t[max(0, h - 250):h + 350])
    return 0


if __name__ == "__main__":
    sys.exit(main())
