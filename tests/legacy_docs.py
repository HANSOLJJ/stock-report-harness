# 지운 옛 규칙·설계 문서를 git 이력에서 꺼내 읽는 테스트 도우미
"""2026-10-06 규칙 문서 재편으로 옛 문서(규칙 v1.5·v1.7 등)를 작업 폴더에서 지웠다.

규칙 JSON 과 이전 판단은 여전히 그 문서의 행 번호를 인용하므로, 인용한 행이 실제로 그 문장인지 보는
검사는 남겨야 한다. 파일이 없다고 검사를 건너뛰면 조용히 통과하므로, 문서가 들어온 커밋에서 꺼내 읽는다.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# 옛 문서들이 docs/scorecard/ 로 들어온 커밋(2026-10-01). 이 커밋에 다섯 원문이 바이트 그대로 있다.
LEGACY_COMMIT = "79e476bfa8a14c83dcaad035ebccd52e0939b690"
RULES_V15 = "docs/scorecard/rules/AI기업_채점규칙_v1.5.md"


def legacy_text(relpath: str) -> str | None:
    """옛 문서의 내용. git 을 부르지 못하거나 그 커밋에 파일이 없으면 None."""
    try:
        out = subprocess.run(["git", "-C", str(ROOT), "show", f"{LEGACY_COMMIT}:{relpath}"],
                             capture_output=True, check=True)
    except (OSError, subprocess.CalledProcessError):
        return None
    return out.stdout.decode("utf-8")
