# 원자료 부재 시 테스트를 사유와 함께 건너뛰는 데코레이터 도우미
from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def require_raw(*paths: Path | str):
    """지정된 원자료 경로가 하나라도 없으면 사유를 밝히고 건너뛴다."""
    for p in paths:
        path = Path(p)
        if not path.is_absolute():
            path = ROOT / path
        if not path.exists():
            try:
                rel = path.relative_to(ROOT).as_posix()
            except ValueError:
                rel = str(path).replace("\\", "/")
            return unittest.skip(f"원자료 없음: {rel} (원본 폴더에서만 실행)")
    return lambda fn: fn
