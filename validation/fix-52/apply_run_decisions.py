# FIX-52: 규칙에서 resolved 된 C-03·C-11·C-13 을 run.json.decisions 에 올린다 — decision_choice 는 run 만 읽는다
"""리뷰 C(codex) 결정 반영 대조에서 C-03·C-11·C-13 이 `run.json` 누락으로 fail/pass 가 갈렸다. 규칙 파일의
`chosen` 은 선언이고 엔진이 읽는 것은 실행 단위 `run.decisions` 다.

재실행해도 같은 결과가 나온다. 파일 줄끝은 원래 것을 유지한다(HASH-EOL).
"""
from __future__ import annotations

import io
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard.schema import validate_run  # noqa: E402

RUN = ROOT / "scorecard" / "runs" / "ai-scorecard-2026-09-obsreg"

ADD = [
    {"id": "C-03", "choice": "paths_with_generation_gap_5",
     "rationale": ("F2 경로 수 0·1·2 → 2·3·4, 성능 도약이 세대 격차 수준이면 5(혼합 모델). 규칙 v1.7 decisions C-03 "
                   "resolved 를 실행 단위로 옮긴다. 14개사 F2 는 승계 score 판단이라 이 선택으로 점수가 바뀌지 않는다 — "
                   "세대 격차는 판단 입력이라 경로 판정이 들어올 때 compute_f2 가 이 선택으로 산출한다. FIX-52."),
     "decided_by": "사용자", "decided_at": "2026-09-14"},
    {"id": "C-11", "choice": "block_carryover",
     "rationale": ("영업외 비중은 F6 P4 전용이고 ⑦ 로 이월하지 않는다. 규칙 v1.7 decisions C-11 resolved 를 실행 단위로 "
                   "옮긴다. 이 선택을 읽는 코드 분기는 없다 — F7 엔진은 두 축만 읽어 원래 이월 경로가 없다. 결정자는 "
                   "규칙과 같게 사용자 확인 전이다. FIX-52."),
     "decided_by": "설계진행 제안 · 사용자 확인 전", "decided_at": "2026-09-14"},
    {"id": "C-13", "choice": "reject_proxy",
     "rationale": ("근사 NTM PER 을 받지 않는다. **bands 모드에서만 효력이 있다** — 이 실행은 v1.7 parameters 모드라 "
                   "calc_f6 가 per-band 경로에 들어가지 않고 NTM 을 점수에 쓰지 않으므로 결과에 영향이 없다. 규칙 v1.7 "
                   "decisions C-13 resolved 를 실행 단위로 옮긴다. FIX-52."),
     "decided_by": "사용자", "decided_at": "2026-09-14"},
]


def main() -> int:
    path = RUN / "run.json"
    raw = io.open(path, encoding="utf-8", newline="").read()
    nl = "\r\n" if "\r\n" in raw else "\n"
    run = json.loads(raw)
    ids = {d["id"] for d in ADD}
    run["decisions"] = [d for d in run["decisions"] if d["id"] not in ids] + ADD
    validate_run(run, "ai-scorecard-2026-09-obsreg")
    out = json.dumps(run, ensure_ascii=False, indent=2) + ("\n" if raw.endswith("\n") else "")
    io.open(path, "w", encoding="utf-8", newline="").write(out.replace("\n", nl))
    print("run.decisions:", [f"{d['id']}:{d['choice']}" for d in run["decisions"]])
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    sys.exit(main())
