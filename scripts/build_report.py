#!/usr/bin/env python3
"""승인된 ai_scorecard 실행을 결정론적으로 HTML 로 빌드하는 진입점.

빌더는 조사를 하지 않고 새 주장을 더하지 않는다. `scorecard.render_html.build_scorecard` 가 승인 해시를
검증한 뒤 대시보드 HTML·감사 기록·history.csv 를 쓰고 사후 계약 검증을 돈다.
스킬·문서·훅이 이 경로를 가리키므로 파일은 진입점으로 남긴다.
"""
from __future__ import annotations

import argparse

from report_contract_lib import OUTPUT_DIR, rel
from scorecard.render_html import build_scorecard


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("slug")
    args = parser.parse_args(argv)

    html_path, generated, _image = build_scorecard(args.slug)
    print("Build complete")
    print(f"HTML: {rel(html_path)}")
    print("Generated files:")
    for path in generated:
        print(f"- {rel(path)}")
    print(f"Preview: http://localhost:3000/{html_path.relative_to(OUTPUT_DIR).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
