# 1차 리뷰 수정 묶음 뒤 기업 요약 여섯 건(점수·순위가 바뀐 회사와 Alibaba 성분 표기)을 다시 쓴다
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BY = "claude (사용자 위임 2026-10-12)"
CLI = ["uv", "run", "--frozen", "python", "-X", "utf8", str(ROOT / "scripts" / "scorecard_cli.py")]
TEXT = {
    "amazon": "Amazon 은 Prime 요금 인상 뒤에도 구독 매출이 늘어난 가격 실측과 회수 루프(① 5), 다섯 자리 다각화(④ 5), Anthropic·OpenAI 에 건 지분 동맹(⑤ 4)으로 "
              "과점 20점이고, ② 는 패러다임 적응 한 경로로 3점, 함정은 최근 1년 잉여현금흐름 마이너스의 ⑨ −2 를 포함해 −6 으로 조정 14점, 1위다.",
    "microsoft": "Microsoft 는 Microsoft 365 업무 채널의 전환비용과 16분기 가격 실측(① 5), 다섯 자리를 모두 가진 다각화(④ 5), 지분·편입 동맹(⑤ 4)으로 "
                 "과점 21점을 쌓지만, OpenAI 의 Azure $250B 추가 구매 계약으로 조달 의존 고객 몫이 커진 ⑦ −2, 매출의 약 1.7배인 데이터센터 약정과 OpenAI "
                 "계약 잔고에 기댄 ⑧ −2, 밸류에이션 −3, 적자 깊이 −1 로 함정 −8 이라 조정 13점, 2위다.",
    "alphabet": "Alphabet 은 검색·지도·Gmail·YouTube 소비자 채널의 락인과 8분기 가격 실측(① 5), 독립 측정 상위 모델과 A2A 표준 선점(② 4), 다섯 자리 다각화(④ 5), "
                "Anthropic 의 Google Cloud 편입(⑤ 4)으로 과점 20점이고, ③ 은 AI 귀속 지표의 가속이 확인되지 않아 2점이며, 매출의 약 2배인 구매 약정·미개시 "
                "리스(⑧ −3)를 포함한 함정 −8 로 조정 12점, 3위다.",
    "openai": "OpenAI 는 ARC 순위표 1위 모델과 패러다임 적응·표준 선점(② 4), 회사 기준 연환산 매출의 재가속(③ 3)으로 과점 12점이지만, 소비자 채널에서 회수 루프와 "
              "대체 공급이 실패해 ① 0점이며, 구속력이 확인된 클라우드 약정만으로도 매출의 약 14배인 의존(⑧ −3), 비상장 밸류에이션 −4, 기준일에 아직 고객인 "
              "조달 의존 고객 Cursor 의 몫을 좁힐 실측이 없어 큼으로 둔 ⑦ −2, 적자 깊이 −2 로 함정 −11 이라 조정 1점, 공동 12위다.",
    "anthropic": "Anthropic 은 종합 지수 1위 모델(② 4)과 AWS·Google 재판매 동맹(⑤ 3)으로 과점 12점이지만(거래 채널의 정가 인하와 좁은 성능 격차로 ① 1점, "
                 "2분기 영업이익 전환 보도로 별도 수익모델은 통과했으나 연환산 매출 성장률이 꺾여 ③ 2점), 비상장 밸류에이션 −4, 모델 경쟁자 넷에게서 컴퓨트를 "
                 "빌리는 의존 −3, 조달 의존 고객 Cursor 의 몫을 좁힐 실측이 없어 큼으로 둔 ⑦ −2, 적자 깊이 −2 로 함정 −11 이라 조정 1점, 공동 12위다.",
    "alibaba": "Alibaba 는 Zhenwu 칩·Qwen 모델·클라우드·AI 유통·커머스 다섯 자리를 모두 가진 다각화(④ 5)로 과점 17점이지만, 최근 1년 매출 성장 4.4%(−3)와 "
               "2026-10-09 종가로 25배를 넘은 최근 1년 PER(−1), 세전이익의 약 70% 가 본업 밖에서 나온 입력 신뢰도 감점(−1)을 더한 밸류에이션 −5, 미국의 첨단 "
               "GPU 수출 금지·1260H 등재와 VIE 구조라는 지정학 의존(⑧ −3), 최근 1년 잉여현금흐름 마이너스와 1~3년 런웨이로 게이트를 모두 지난 ⑨ −4 로 함정 "
               "−12 라 조정 5점, 공동 8위다.",
}


def main() -> int:
    slug = sys.argv[1]
    for cid, text in TEXT.items():
        r = subprocess.run([*CLI, "propose", slug, "--company", cid, "--factor", "SUMMARY", "--evidence", text,
                            "--reason", "1차 리뷰 수정 묶음의 점수·순위와 ⑥ 성분을 기업 요약에 반영한다", "--by", BY],
                           capture_output=True, text=True, encoding="utf-8", cwd=ROOT)
        if r.returncode != 0:
            print(cid); print(r.stdout[-1500:]); print(r.stderr[-1500:]); return 1
    r = subprocess.run([*CLI, "proposal", slug, "--all-pending", "--accept", "--by", BY], capture_output=True, text=True, encoding="utf-8", cwd=ROOT)
    print(r.stdout[-600:]); print(r.stderr[-600:]); return r.returncode


if __name__ == "__main__":
    raise SystemExit(main())
