# (2026-10 v2.1 첫 실행) 실행을 다시 만들고 표시 이름·facts 관측·트리거 carry 를 다시 넣는다 — 규칙 파일이 바뀌어 실행을 새로 만들 때
"""
사용: uv run --frozen python -X utf8 .agents/plans/v21-first-run-2026-10/work/reinit.py

근거·관측 묶음의 산출물(work/out-*.json)과 판단 제안은 실행 폴더 밖에 있으므로 다시 만들어도 남는다. 합치기·반영은 그 뒤에 한다.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "scripts"))
SLUG, PRIOR = "ai-scorecard-2026-10-v21", "ai-scorecard-2026-10-recheck"
PY = ["uv", "run", "--frozen", "python", "-X", "utf8"]
CLI = [*PY, str(ROOT / "scripts" / "scorecard_cli.py")]


def run(cmd: list[str]) -> str:
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", cwd=ROOT)
    if r.returncode != 0:
        print(r.stdout[-2000:]); print(r.stderr[-2000:])
        raise SystemExit(f"[실패] {' '.join(cmd[6:9])}")
    return r.stdout


def main() -> int:
    run([*CLI, "init", SLUG, "--from-run", PRIOR, "--rule", "v2.1", "--change-type", "rule-change",
         "--title", "2026-10 규칙 v2.1 첫 실행(10월 사실)",
         "--request", "규칙 v2.1 첫 실행 — recheck 와 같은 사실(기준일 2026-10-12)에 규칙만 v2.1 로 바꾼다(v2.0→v2.1 다리 첫 단계)",
         "--purpose", "규칙 v2.1(① 만점 AI 수익화 조건, ④ 보유표 두 축, ⑥ 성장 조정 배수, ⑦ 네 칸 −3, ⑧ 네 축)로 14개사를 다시 매기고, "
                      "같은 사실에서 규칙 변경이 바꾼 점수를 가른다",
         "--decision", "C-12=growth_adjusted_ps",
         "--rationale", "비상장 ⑥ 은 P/S ÷ 보정 매출 성장으로 매긴다. 규칙 v2.1 은 이 선택만 계산한다(사용자 결정 2026-10-12, 계획 rule-v21-2026-10).",
         "--by", "사용자", "--force"])
    from scorecard.schema import load_json_strict, validate_run, write_json
    p = ROOT / "output" / SLUG / "run.json"
    r = load_json_strict(p)
    r["display_names"] = {"spacex-xai": "SpaceX"}
    validate_run(r, SLUG)
    write_json(p, r)
    out = run([*CLI, "collect", SLUG, "--kind", "facts"])
    print("\n".join(line for line in out.splitlines() if line.startswith("  facts")))
    print(run([*PY, str(Path(__file__).resolve().parent / "carry_triggers.py"), SLUG, PRIOR]).strip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
