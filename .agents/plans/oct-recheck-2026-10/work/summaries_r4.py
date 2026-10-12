# ⑧ 약정 축 3배 경계 결정 뒤 기업 요약 세 건(Alphabet 2위, Microsoft 3위, Meta ⑧ 3.05배)을 다시 쓴다
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BY = "claude (사용자 위임 2026-10-12)"
CLI = ["uv", "run", "--frozen", "python", "-X", "utf8", str(ROOT / "scripts" / "scorecard_cli.py")]
TEXT = {
    "alphabet": "Alphabet 은 검색·지도·Gmail·YouTube 소비자 채널의 락인과 8분기 가격 실측(① 5), 독립 측정 상위 모델과 A2A 표준 선점(② 4), 다섯 자리 다각화(④ 5), "
                "Anthropic 의 Google Cloud 편입(⑤ 4)으로 과점 20점이고, ③ 은 AI 귀속 지표의 가속이 확인되지 않아 2점이며, 매출의 약 2배인 구매 약정·미개시 "
                "리스(⑧ −2)를 포함한 함정 −7 로 조정 13점, 2위다.",
    "microsoft": "Microsoft 는 Microsoft 365 업무 채널의 전환비용과 16분기 가격 실측(① 5), 다섯 자리를 모두 가진 다각화(④ 5), 지분·편입 동맹(⑤ 4)으로 "
                 "과점 21점을 쌓지만, OpenAI 의 Azure $250B 추가 구매 계약으로 조달 의존 고객 몫이 커진 ⑦ −2, OpenAI 계약 잔고를 연환산하면 매출의 30% 를 "
                 "넘는 고객 집중(⑧ −3), 밸류에이션 −3, 적자 깊이 −1 로 함정 −9 라 조정 12점, 3위다.",
    "meta": "Meta 는 일간 사용자 36억 명 소비자 채널의 회수 루프와 광고 단가 실측(① 5), PyTorch 표준 선점(② 4), MTIA 칩·Muse 모델·AI 유통·광고 네 자리(④ 4)로 "
            "과점 항목이 강하고, 2026-07 추가 리스까지 더하면 매출의 약 3배인 미개시 리스·해지 불가 약정으로 ⑧ −3 을 받지만, 같은 정의로 이어지는 회사 공시 "
            "AI 지표가 없어 ③ 점수를 만들지 못해 순위에서 빠져 있다.",
}


def main() -> int:
    slug = sys.argv[1]
    for cid, text in TEXT.items():
        r = subprocess.run([*CLI, "propose", slug, "--company", cid, "--factor", "SUMMARY", "--evidence", text,
                            "--reason", "⑧ 약정 축 3배 경계 결정(2026-10-12)의 점수·순위를 기업 요약에 반영한다", "--by", BY],
                           capture_output=True, text=True, encoding="utf-8", cwd=ROOT)
        if r.returncode != 0:
            print(cid); print(r.stdout[-1500:]); print(r.stderr[-1500:]); return 1
    r = subprocess.run([*CLI, "proposal", slug, "--all-pending", "--accept", "--by", BY], capture_output=True, text=True, encoding="utf-8", cwd=ROOT)
    print(r.stdout[-600:]); print(r.stderr[-600:]); return r.returncode


if __name__ == "__main__":
    raise SystemExit(main())
