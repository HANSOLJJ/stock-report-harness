# 확인 리뷰 2차 수정 뒤 기업 요약 세 건(Microsoft·Alphabet 공동 2위, OpenAI ⑧ 근거 등급)을 다시 쓴다
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BY = "claude (사용자 위임 2026-10-12)"
CLI = ["uv", "run", "--frozen", "python", "-X", "utf8", str(ROOT / "scripts" / "scorecard_cli.py")]
TEXT = {
    "microsoft": "Microsoft 는 Microsoft 365 업무 채널의 전환비용과 16분기 가격 실측(① 5), 다섯 자리를 모두 가진 다각화(④ 5), 지분·편입 동맹(⑤ 4)으로 "
                 "과점 21점을 쌓지만, OpenAI 의 Azure $250B 추가 구매 계약으로 조달 의존 고객 몫이 커진 ⑦ −2, OpenAI 계약 잔고를 연환산하면 매출의 30% 를 "
                 "넘는 고객 집중(⑧ −3), 밸류에이션 −3, 적자 깊이 −1 로 함정 −9 라 조정 12점, 공동 2위다.",
    "alphabet": "Alphabet 은 검색·지도·Gmail·YouTube 소비자 채널의 락인과 8분기 가격 실측(① 5), 독립 측정 상위 모델과 A2A 표준 선점(② 4), 다섯 자리 다각화(④ 5), "
                "Anthropic 의 Google Cloud 편입(⑤ 4)으로 과점 20점이고, ③ 은 AI 귀속 지표의 가속이 확인되지 않아 2점이며, 매출의 약 2배인 구매 약정·미개시 "
                "리스(⑧ −3)를 포함한 함정 −8 로 조정 12점, 공동 2위다.",
    "openai": "OpenAI 는 ARC 순위표 1위 모델과 패러다임 적응·표준 선점(② 4), 회사 기준 연환산 매출의 재가속(③ 3)으로 과점 12점이지만, 소비자 채널에서 회수 루프와 "
              "대체 공급이 실패해 ① 0점이며, 구속력이 확인된 AWS·Azure 약정만으로 연환산 매출의 약 8배이고 2차 보도된 Oracle 계약을 더하면 약 14배인 "
              "의존(⑧ −3), 비상장 밸류에이션 −4, 기준일에 아직 고객인 조달 의존 고객 Cursor 의 몫을 좁힐 실측이 없어 큼으로 둔 ⑦ −2, 적자 깊이 −2 로 "
              "함정 −11 이라 조정 1점, 공동 12위다.",
}


def main() -> int:
    slug = sys.argv[1]
    for cid, text in TEXT.items():
        r = subprocess.run([*CLI, "propose", slug, "--company", cid, "--factor", "SUMMARY", "--evidence", text,
                            "--reason", "확인 리뷰 2차 수정의 점수·순위와 근거 등급을 기업 요약에 반영한다", "--by", BY],
                           capture_output=True, text=True, encoding="utf-8", cwd=ROOT)
        if r.returncode != 0:
            print(cid); print(r.stdout[-1500:]); print(r.stderr[-1500:]); return 1
    r = subprocess.run([*CLI, "proposal", slug, "--all-pending", "--accept", "--by", BY], capture_output=True, text=True, encoding="utf-8", cwd=ROOT)
    print(r.stdout[-600:]); print(r.stderr[-600:]); return r.returncode


if __name__ == "__main__":
    raise SystemExit(main())
