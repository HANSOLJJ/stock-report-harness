# 재실행의 최종 점수로 기업 요약(카드 한 줄) 14건을 SUMMARY 제안으로 올리고 한꺼번에 반영한다
"""
사용: uv run --frozen python -X utf8 .agents/plans/rejudge-all-2026-11/work/summaries_r1.py <slug> [--dry-run] [--no-accept]
요약은 이 실행의 results·judgments 결론 줄에서 뽑은 완결된 현재 상태 문장이다(규칙 버전·변경 표시·이전 판 비교 없음).
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BY = "claude (사용자 위임 2026-10-08)"
CLI = ["uv", "run", "--frozen", "python", "-X", "utf8", str(ROOT / "scripts" / "scorecard_cli.py")]

SUMMARIES = {
    "microsoft": "Microsoft 는 Microsoft 365 업무 채널의 전환비용과 16분기 가격 실측(① 5), 다섯 자리를 모두 가진 다각화(④ 5), 지분·편입 동맹(⑤ 4)으로 과점 21점을 쌓고, "
                 "함정은 밸류에이션 −3 과 OpenAI 가 공급자이자 경쟁자인 의존 −1 을 합쳐 −6 에 그쳐 조정 15점으로 1위다.",
    "alphabet": "Alphabet 은 소비자·업무·거래 세 채널의 락인과 가격 실측(① 5), Gemini 4 Argon 의 독립 측정 2위 안과 TPU·표준 선점(② 4), 다섯 자리 다각화(④ 5), "
                "Anthropic 의 Google Cloud 편입(⑤ 4)으로 과점 20점이고, ③ 은 AI 귀속 지표의 가속이 확인되지 않아 2점이며 함정 −6 으로 조정 14점, 공동 2위다.",
    "amazon": "Amazon 은 Prime 요금 인상 뒤에도 구독 매출이 늘어난 가격 실측과 회수 루프(① 5), 다섯 자리 다각화(④ 5), Anthropic·OpenAI 에 건 지분 동맹(⑤ 4)으로 과점 20점이고, "
              "② 는 패러다임 적응 한 경로로 3점, 함정은 최근 1년 잉여현금흐름 마이너스의 ⑨ −2 를 포함해 −6 으로 조정 14점, 공동 2위다.",
    "nvidia": "NVIDIA 는 CUDA 개발자와 설치기반의 회수 루프(① 4), MLPerf 독립 측정의 성능 도약과 세 경로 통과(② 4), 칩·모델·클라우드·AI 밖 매출 네 자리(④ 4), "
              "CoreWeave·Nebius 지분 동맹(⑤ 3)으로 과점 17점이지만, 하이퍼스케일 고객 넷의 자체 칩 출하(⑤ 구조형 적대), 첨단 칩 생산을 대만의 TSMC 에 맡긴 의존(⑧ −4), "
              "조달 의존 고객에 투자·보증으로 돈을 넣는 구조(⑦ −2)로 함정 −8 이라 조정 9점, 공동 4위다.",
    "tsmc": "TSMC 는 N2 양산과 HPC 매출의 직전 분기 대비 성장(③ 4), 공정마다 묶이는 PDK·OIP 설계 생태계(① 3)와 OIP 공동개발 동맹(⑤ 3)으로 과점 15점이고, "
            "② 는 독립 측정이 없어 성능 도약이 부분으로 계산돼 3점, ④ 는 칩·AI 밖 매출 두 자리로 2점이며, 생산이 대만에 집중된 지정학 의존 ⑧ −4 로 함정 −6 이라 조정 9점, 공동 4위다.",
    "apple": "Apple 은 App Store 양면 구조와 늘어나는 설치기반의 회수 루프(① 4), Google 이 기본 검색 대가를 내며 플랫폼에 들어와 있는 경쟁사 편입(⑤ 4)으로 과점 15점이지만, "
             "새 Siri 가 2년 미뤄져 ③ 2점, 성능 도약과 표준 선점이 없어 ② 2점이고, 밸류에이션 −4 와 대만 생산 집중 −4 로 함정 −8 이라 조정 7점, 6위다.",
    "alibaba": "Alibaba 는 Zhenwu 칩·Qwen 모델·클라우드·AI 유통·커머스 다섯 자리를 모두 가진 다각화(④ 5)로 과점 17점이지만, 미국의 첨단 GPU 수출 금지·1260H 등재와 VIE 구조라는 "
               "지정학 의존(⑧ −3), 밸류에이션 −4, 최근 1년 잉여현금흐름 마이너스와 1~3년 런웨이로 게이트를 모두 지난 ⑨ −4 로 함정 −11 이라 조정 6점, 7위다.",
    "oracle": "Oracle 은 수십 년 대체재가 있는데도 고객이 남는 데이터베이스 전환비용(① 4)과 OCI 매출 가속(③ 3)으로 과점 15점이지만, OpenAI 의 5년 $300B 약정이 최근 1년 매출과 "
              "맞먹는 조달 의존 고객 집중(⑦ −2·⑧ −4)과 ⑨ −3 으로 함정 −10 이라 조정 5점, 공동 8위다.",
    "tesla": "Tesla 는 FSD 활성 이용 수가 분기마다 15% 안팎으로 늘고(③ 3) 칩·모델·AI 유통·차량 매출 네 자리(④ 4)로 과점 14점이지만, 동맹 없이 규제 조사만 있는 ⑤ 2점과 ① 2점에 "
             "밸류에이션 −5 를 포함한 함정 −9 로 조정 5점, 공동 8위다.",
    "spacex-xai": "SpaceX + xAI 는 네 자리 다각화(④ 4)와 Starshield 등 미 정부 다년 계약 동맹(⑤ 3)으로 과점 15점이지만, Anthropic 컴퓨트 계약이 최근 1년 매출의 대부분에 이르는 "
                  "조달 의존 고객 집중(⑦ −2·⑧ −3)과 ⑨ −3 으로 함정 −11 이라 조정 4점, 공동 10위다.",
    "palantir": "Palantir 는 미국 상업 매출의 가속(③ 3)과 계약 수준의 전환비용(① 3)으로 과점 11점이고, 사업의 정당성을 겨냥한 적대(⑤ 2)와 AI 플랫폼 한 자리뿐인 다각화(④ 1)에 "
                "밸류에이션 −4 와 미 정부 고객 집중 −3 을 더한 함정 −7 로 조정 4점, 공동 10위다.",
    "openai": "OpenAI 는 ARC 순위표 1위 모델과 패러다임 적응·표준 선점(② 4), 연환산 매출의 재가속(③ 3)으로 과점 12점이지만, 소비자 채널에서 회수 루프와 대체 공급이 실패하고 전환비용이 확인되지 않아 ① 0점이며, "
              "매출의 수십 배에 이르는 컴퓨트 약정(⑧ −4)과 비상장 밸류에이션 −4 로 함정 −10 이라 조정 2점, 공동 12위다.",
    "anthropic": "Anthropic 은 종합 지수 1위 모델(② 4)로 과점 11점이지만, 거래 채널의 정가 인하와 좁은 성능 격차로 ① 1점, 연환산 매출 성장률이 꺾여 ③ 2점, 큰 고객 둘이 경쟁사 소유가 된 "
                 "구조형 적대(⑤ 2)에 모델 경쟁자 넷에게서 컴퓨트를 빌리는 의존(⑧ −3)과 비상장 밸류에이션 −4 로 함정 −9 라 조정 2점, 공동 12위다.",
    "meta": "Meta 는 36억 명 일간 사용자의 소비자 채널 회수 루프와 광고 단가 실측(① 5), PyTorch 표준 선점(② 4), MTIA 칩·Muse 모델·AI 유통·광고 네 자리(④ 4)로 과점 항목이 강하지만, "
            "같은 정의로 세 분기 이상 이어지는 AI 귀속 지표가 없어 ③ 점수를 만들지 못해 순위에서 빠져 있다.",
}


def main() -> int:
    slug = sys.argv[1]
    dry = "--dry-run" in sys.argv
    accept = "--no-accept" not in sys.argv
    for cid, text in SUMMARIES.items():
        cmd = [*CLI, "propose", slug, "--company", cid, "--factor", "SUMMARY", "--evidence", text,
               "--reason", "전부 재판단한 이 실행의 점수·순위로 기업 요약을 새로 쓴다(1차 리뷰 출력·가독성 F5)", "--by", BY]
        print("→", cid)
        if dry:
            continue
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", cwd=ROOT)
        if r.returncode != 0:
            print(r.stdout[-1500:]); print(r.stderr[-2000:]); print(f"[실패] {cid}"); return 1
    if accept and not dry:
        r = subprocess.run([*CLI, "proposal", slug, "--all-pending", "--accept", "--by", BY], capture_output=True, text=True, encoding="utf-8", cwd=ROOT)
        print(r.stdout[-2000:]); print(r.stderr[-2000:])
        return r.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
