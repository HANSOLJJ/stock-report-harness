# 승인 취소 뒤 수정(2026-10-09): Anthropic ⑤ 변경에 따라 Anthropic·OpenAI 기업 요약을 다시 쓴다(SUMMARY 제안 → 반영)
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BY = "claude (사용자 위임 2026-10-08)"
CLI = ["uv", "run", "--frozen", "python", "-X", "utf8", str(ROOT / "scripts" / "scorecard_cli.py")]

SUMMARIES = {
    "anthropic": "Anthropic 은 종합 지수 1위 모델(② 4)과 AWS·Google 재판매 동맹(⑤ 3)으로 과점 12점이지만(거래 채널의 정가 인하와 좁은 성능 격차로 ① 1점, 연환산 매출 성장률이 "
                 "꺾여 ③ 2점, 큰 고객 둘이 경쟁사 소유가 된 사실은 고객 비중이 공시되지 않아 구조형 적대로 올리지 않음), 비상장 밸류에이션 −4, 모델 경쟁자 넷에게서 컴퓨트를 "
                 "빌리는 의존 −3, 적자 깊이 −2 로 함정 −9 라 조정 3점, 12위다.",
    "openai": "OpenAI 는 ARC 순위표 1위 모델과 패러다임 적응·표준 선점(② 4), 연환산 매출의 재가속(③ 3)으로 과점 12점이지만, 소비자 채널에서 회수 루프와 대체 공급이 실패하고 "
              "전환비용이 확인되지 않아 ① 0점이며, 매출의 수십 배에 이르는 컴퓨트 약정(⑧ −4), 비상장 밸류에이션 −4, 적자 깊이 −2 로 함정 −10 이라 조정 2점, 13위다.",
}


def main() -> int:
    slug = sys.argv[1]
    for cid, text in SUMMARIES.items():
        cmd = [*CLI, "propose", slug, "--company", cid, "--factor", "SUMMARY", "--evidence", text,
               "--reason", "Anthropic ⑤ 적대를 비용형으로 고친 뒤의 점수·순위로 요약을 다시 쓴다", "--by", BY]
        print("→", cid)
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", cwd=ROOT)
        if r.returncode != 0:
            print(r.stdout[-1500:]); print(r.stderr[-2000:]); return 1
    r = subprocess.run([*CLI, "proposal", slug, "--all-pending", "--accept", "--by", BY], capture_output=True, text=True, encoding="utf-8", cwd=ROOT)
    print(r.stdout[-1500:]); print(r.stderr[-1500:])
    return r.returncode


if __name__ == "__main__":
    raise SystemExit(main())
