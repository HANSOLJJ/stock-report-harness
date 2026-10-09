# 3차 확인 리뷰 반영 뒤 점수·순위로 기업 요약 5건(Anthropic·OpenAI·Oracle·Alibaba·Tesla)을 다시 쓴다
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
                 "빌리는 의존 −3, 조달 의존 고객 Cursor 의 몫을 좁힐 실측이 없어 큼으로 둔 ⑦ −2, 적자 깊이 −2 로 함정 −11 이라 조정 1점, 13위다.",
    "openai": "OpenAI 는 ARC 순위표 1위 모델과 패러다임 적응·표준 선점(② 4), 연환산 매출의 재가속(③ 3)으로 과점 12점이지만, 소비자 채널에서 회수 루프와 대체 공급이 실패하고 "
              "전환비용이 확인되지 않아 ① 0점이며, 매출의 수십 배에 이르는 컴퓨트 약정(⑧ −4), 비상장 밸류에이션 −4, 적자 깊이 −2 로 함정 −10 이라 조정 2점, 12위다.",
    "oracle": "Oracle 은 수십 년 대체재가 있는데도 고객이 남는 데이터베이스 전환비용(① 4)과 OCI 매출 가속(③ 3)으로 과점 15점이지만, OpenAI 의 5년 $300B 약정이 최근 1년 매출과 "
              "맞먹는 조달 의존 고객 집중(⑦ −2)과 매출의 약 4.5배에 이르는 미개시 데이터센터 리스·구매 약정(⑧ −3)에 밸류에이션 −1 과 적자 깊이 −3 을 더한 함정 −9 라 조정 6점, 공동 7위다.",
    "alibaba": "Alibaba 는 Zhenwu 칩·Qwen 모델·클라우드·AI 유통·커머스 다섯 자리를 모두 가진 다각화(④ 5)로 과점 17점이지만, 미국의 첨단 GPU 수출 금지·1260H 등재와 VIE 구조라는 "
               "지정학 의존(⑧ −3), 밸류에이션 −4, 최근 1년 잉여현금흐름 마이너스와 1~3년 런웨이로 게이트를 모두 지난 ⑨ −4 로 함정 −11 이라 조정 6점, 공동 7위다.",
    "tesla": "Tesla 는 FSD 활성 이용 수가 분기마다 15% 안팎으로 늘고(③ 3) 칩·모델·AI 유통·차량 매출 네 자리(④ 4)로 과점 14점이지만, 동맹 없이 규제 조사만 있는 ⑤ 2점과 ① 2점에 "
             "밸류에이션 −5 를 포함한 함정 −9 로 조정 5점, 9위다.",
}


def main() -> int:
    slug = sys.argv[1]
    for cid, text in SUMMARIES.items():
        cmd = [*CLI, "propose", slug, "--company", cid, "--factor", "SUMMARY", "--evidence", text,
               "--reason", "3차 확인 리뷰 반영(Anthropic ⑦·Oracle ⑧) 뒤의 점수·순위로 요약을 다시 쓴다", "--by", BY]
        print("→", cid)
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", cwd=ROOT)
        if r.returncode != 0:
            print(r.stdout[-1500:]); print(r.stderr[-2000:]); return 1
    r = subprocess.run([*CLI, "proposal", slug, "--all-pending", "--accept", "--by", BY], capture_output=True, text=True, encoding="utf-8", cwd=ROOT)
    print(r.stdout[-1500:]); print(r.stderr[-1500:])
    return r.returncode


if __name__ == "__main__":
    raise SystemExit(main())
