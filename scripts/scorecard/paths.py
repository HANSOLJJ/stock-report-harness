# 실행 하나의 산출물 경로를 output/<run_id>/ 묶음 아래로 모아 돌려주는 경로 도우미
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from . import engine


@dataclass(frozen=True)
class RunPaths:
    slug: str
    run_dir: Path
    plan: Path
    research: Path
    draft: Path
    preview: Path
    review: Path
    review_parts: Path
    html: Path
    audit: Path
    evidence_dir: Path
    evidence: Path
    candidates: Path
    triggers: Path
    proposals: Path

    def rel(self, p: Path) -> str:
        """저장소 루트 기준 POSIX 문자열. 렌더러와 검증기가 같은 함수를 쓴다.

        기준은 `OUTPUT_DIR` 의 부모다. 실제로는 ROOT 와 같고, 테스트가 `engine.OUTPUT_DIR` 를 임시 폴더로
        바꿔도 frontmatter 문자열이 `output/<slug>/…` 로 같게 나온다.
        """
        return p.relative_to(self.run_dir.parent.parent).as_posix()


def run_paths(slug: str) -> RunPaths:
    """항상 `engine.OUTPUT_DIR / slug` 아래다. 파일명은 훅(scripts/hooks/guard.py)이 그대로 쓴다."""
    d = engine.run_dir(slug)
    evidence_dir = d / "evidence"
    return RunPaths(
        slug=slug,
        run_dir=d,
        plan=d / "plan.md",
        research=d / "research.md",
        draft=d / "draft.md",
        preview=d / "preview.md",
        review=d / "review.md",
        review_parts=d / "review-parts",
        html=d / "report.html",
        audit=d / "audit.md",
        evidence_dir=evidence_dir,
        evidence=evidence_dir / "evidence.json",
        candidates=evidence_dir / "candidates.json",
        triggers=d / "triggers.json",
        proposals=d / "proposals.json",   # 2026-10-01 판단 변경 제안(입력 해시 밖)
    )
