# 4차 확인 리뷰 L4 — Oracle 요약의 $300B 약정에 근거 등급(2차 보도)을 적는다
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BY = "claude (사용자 위임 2026-10-08)"
CLI = ["uv", "run", "--frozen", "python", "-X", "utf8", str(ROOT / "scripts" / "scorecard_cli.py")]
TEXT = ("Oracle 은 수십 년 대체재가 있는데도 고객이 남는 데이터베이스 전환비용(① 4)과 OCI 매출 가속(③ 3)으로 과점 15점이지만, 2차 보도된 OpenAI 의 5년 $300B 약정이 "
        "최근 1년 매출과 맞먹는 조달 의존 고객 집중(⑦ −2)과 매출의 약 4.5배에 이르는 미개시 데이터센터 리스·구매 약정(⑧ −3)에 밸류에이션 −1 과 적자 깊이 −3 을 더한 "
        "함정 −9 라 조정 6점, 공동 7위다.")


def main() -> int:
    slug = sys.argv[1]
    r = subprocess.run([*CLI, "propose", slug, "--company", "oracle", "--factor", "SUMMARY", "--evidence", TEXT,
                        "--reason", "요약의 $300B 약정에 근거 등급(2차 보도)을 적는다(4차 확인 리뷰 L4)", "--by", BY],
                       capture_output=True, text=True, encoding="utf-8", cwd=ROOT)
    if r.returncode != 0:
        print(r.stdout[-1500:]); print(r.stderr[-1500:]); return 1
    r = subprocess.run([*CLI, "proposal", slug, "--all-pending", "--accept", "--by", BY], capture_output=True, text=True, encoding="utf-8", cwd=ROOT)
    print(r.stdout[-800:]); return r.returncode


if __name__ == "__main__":
    raise SystemExit(main())
