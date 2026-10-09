# 3차 확인 리뷰(confirm-r3) 발견 B1~B5 반영: Anthropic ⑦ 큼, Oracle ⑧ 고객 축 미확인, OpenAI ⑦①③ 문장, Palantir ⑤ 규칙 문언 — work/judge-fix4/
"""
사용: uv run --frozen python -X utf8 .agents/plans/rejudge-all-2026-11/work/make_fix4.py <slug>
반영은 apply_judgments.py --dir judge-fix4 로 한다. 바꾸려는 문장이 없거나 인용 근거가 확정이 아니면 멈춘다.
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent / "judge-fix4"


def load(slug: str):
    run = ROOT / "output" / slug
    d = json.loads((run / "judgments.json").read_text(encoding="utf-8"))
    ev = json.loads((run / "evidence" / "evidence.json").read_text(encoding="utf-8"))
    return {f'{j["factor"]}:{j["company_id"]}': j for j in d["items"]}, {e["evidence_id"]: e for e in ev["items"]}


def replace_line(lines, needle, new, where):
    hits = [i for i, l in enumerate(lines) if needle in l]
    if len(hits) != 1:
        raise SystemExit(f"[{where}] '{needle[:40]}…' 가 {len(hits)}번 나온다")
    out = list(lines)
    if new is None:
        del out[hits[0]]
    else:
        out[hits[0]] = new
    return out


def sub_in_line(lines, needle, old, new, where):
    hits = [i for i, l in enumerate(lines) if needle in l]
    if len(hits) != 1:
        raise SystemExit(f"[{where}] '{needle[:40]}…' 가 {len(hits)}번 나온다")
    if old not in lines[hits[0]]:
        raise SystemExit(f"[{where}] 줄 안에 '{old[:40]}' 가 없다")
    out = list(lines)
    out[hits[0]] = lines[hits[0]].replace(old, new)
    return out


def write(factor, company, spec):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{factor}-{company}.json").write_text(json.dumps(spec, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> int:
    J, E = load(sys.argv[1])
    if OUT.exists():
        shutil.rmtree(OUT)
    for eid in ("EV-spacex-xai-013", "EV-spacex-xai-048", "EV-anthropic-048", "EV-anthropic-060", "EV-microsoft-010"):
        if E.get(eid, {}).get("status") != "confirmed":
            raise SystemExit(f"{eid} 가 확정 근거가 아니다")
    print("EV-spacex-xai-013:", E["EV-spacex-xai-013"]["excerpt"][:160])
    print("EV-spacex-xai-048:", E["EV-spacex-xai-048"]["excerpt"][:160])

    # ---------- B1 anthropic ⑦: 큼 ----------
    j = J["F7:anthropic"]
    ev = replace_line(j["evidence"], "Anthropic ⑦ 은 조달 의존 고객 비중 작음, 내 돈이 돌아오지 않음 칸이라 0점이다.",
                      "Anthropic ⑦ 은 조달 의존 고객 비중 큼, 내 돈이 돌아오지 않음 칸이라 −2 이다.", "F7:anthropic")
    ev = replace_line(ev, "Anthropic 은 비상장이라 계약 잔고와 최근 1년 매출을 공시하지 않아, 보도된 매출 구성비로 잰다.",
                      "Anthropic 은 비상장이라 계약 잔고와 최근 1년 매출을 공시하지 않는다.", "F7:anthropic")
    ev = replace_line(ev, "Cursor 와 GitHub Copilot 두 고객이 매출의 4분의 1 가까이를 내고",
                      "조달 의존 고객인 Cursor 는 2026-08-14 SpaceX 에 인수돼 영업손실을 내는 SpaceX 의 자금으로 대금을 내고, Anthropic 은 Cursor 의 Claude 사용을 위해 "
                      "컴퓨트를 늘리겠다고 밝혔다. 두 고객이 매출의 4분의 1 가까이를 낸다는 수치는 유출된 상장 신청서 초안과 2차 보도에 기대 Cursor 몫을 작게 좁히는 "
                      "실측이 되지 못하고, 작음은 감점을 덜어 주는 판정이라 실측이 있어야 하므로(규칙 2.1) 가로축은 큼이다. GitHub Copilot 은 마이크로소프트 제품이라 "
                      "자기 영업이익으로 내는 쪽이다.", "F7:anthropic")
    down = replace_line(j["evidence_down"], "Cursor 와 GitHub Copilot 두 고객이 Anthropic 매출의 4분의 1 가까이를 낸다.",
                        "Cursor 와 GitHub Copilot 두 고객이 Anthropic 매출의 4분의 1 가까이를 낸다는 보도가 있다. [EV-anthropic-048, EV-anthropic-060]", "F7:anthropic")
    down = [*down, "SpaceX 는 2026-08-14 Cursor 인수를 마쳤다. [EV-spacex-xai-013]",
            "Anthropic 은 SpaceX 에 인수된 Cursor 의 Claude 모델 지원을 위해 컴퓨트를 계속 늘리겠다고 밝혔다. [EV-spacex-xai-048]"]
    up = replace_line(j["evidence_up"], "Cursor 와 함께 매출의 큰 몫을 내는 GitHub Copilot 은 마이크로소프트 제품이다.",
                      "Anthropic 의 고객 GitHub Copilot 은 마이크로소프트 제품이라 자기 영업이익으로 대금을 내는 쪽이다. [EV-anthropic-048, EV-microsoft-010]", "F7:anthropic")
    write("F7", "anthropic", {"changes": {"funding_dependent_share": "large"}, "evidence_after": ev, "evidence_up_after": up, "evidence_down_after": down,
                              "reason": "조달 의존 고객 Cursor 가 확인되고 그 몫을 작게 좁힐 실측(유출 초안·2차 보도 제외)이 없어 nvidia 와 같은 잣대로 큼이다(3차 확인 리뷰 B1, 규칙 2.1)"})

    # ---------- B2 oracle ⑧: 고객 축 미확인, 약정 축 −3 ----------
    j = J["F8:oracle"]
    ev = replace_line(j["evidence"], "Oracle ⑧ 은 −4 이고 점수를 정한 축은 고객 축의 계약 기준 OpenAI 집중과 그 고객을 위해 묶인 장기 리스다.",
                      "Oracle ⑧ 은 −3 이고 점수를 정한 축은 약정 축, 곧 아직 개시되지 않은 데이터센터 리스와 무조건 구매 약정을 더한 약 $3,222억이 최근 1년 매출의 약 4.5배인 것이다.",
                      "F8:oracle")
    ev = replace_line(ev, "고객 축은 −4 다. 인식 매출 기준 10% 이상 고객은 없지만",
                      "고객 축은 미확인이다. 인식 매출 기준 10% 이상 고객은 없고 회사는 일부 OCI 사업이 소수 대형 고객에 집중돼 있다고 밝히지만 고객별 RPO 비중을 공시하지 않는다. "
                      "OpenAI 계약을 5년 $300B 로 전한 것은 2차 보도라 고객 축을 재지 않았고, 15~19년 데이터센터 리스가 고객 계약과 기간·가격이 맞지 않아 돌리지 못할 수 있다는 "
                      "점은 약정 축에 든다.", "F8:oracle")
    ev = replace_line(ev, "Oracle 은 RPO 의 고객별 비중을 공시하지 않아 OpenAI 몫은 보도된 계약액으로 계산한 추정이다(미확인).",
                      "OpenAI 의 RPO 몫이 공시나 회사 1차 발표로 확인되면 고객 축을 다시 잰다. Tencent 계약 약 $7B 는 보도된 계약액이고 RPO 의 1% 남짓이라 집중을 바꾸지 못한다(추론).",
                      "F8:oracle")
    down = sub_in_line(j["evidence_down"], "2026-08-31 RPO 는 $664B 라 OpenAI 계약 $300B 는 그 약 45% 다(계산).",
                       "2026-08-31 RPO 는 $664B 라 OpenAI 계약 $300B 는 그 약 45% 다(계산).",
                       "2026-08-31 RPO 는 $664B 이고, 보도된 OpenAI 계약액 $300B 로 계산하면 그 약 45% 다(2차 보도 기준 계산).", "F8:oracle")
    down = sub_in_line(down, "OpenAI 가 Oracle 컴퓨트에 쓰기로 한 연 약 $60B 는", "OpenAI 가 Oracle 컴퓨트에 쓰기로 한 연 약 $60B 는",
                       "보도된 OpenAI 의 Oracle 컴퓨트 지출 연 약 $60B 로 계산하면", "F8:oracle")
    down = sub_in_line(down, "보도된 OpenAI 의 Oracle 컴퓨트 지출 연 약 $60B 로 계산하면", "의 약 84% 다(계산).", "의 약 84% 다(2차 보도 기준 계산).", "F8:oracle")
    write("F8", "oracle", {"changes": {"score": -3}, "evidence_after": ev, "evidence_down_after": down,
                           "reason": "고객 축의 OpenAI 집중이 2차 보도 계약액에만 서서 미확인으로 두고(Anthropic·Microsoft 와 같은 잣대), 점수는 약정 축 −3 이 정한다(3차 확인 리뷰 B2)"})

    # ---------- B3 openai ⑦ 문장 ----------
    j = J["F7:openai"]
    ev = replace_line(j["evidence"], "조달 의존 고객인 AI 스타트업은 그 기업 매출의 일부라",
                      "2026-03-31 현재 기업 매출이 매출의 40% 를 넘고 소비자 매출보다 작다고 회사가 밝혔다. 기업 고객 가운데 투자 유치나 차입으로 대금을 내는 고객은 이 실행의 확정 근거로 "
                      "확인되지 않았고 OpenAI 는 2026-08-29 SpaceX 에 인수된 Cursor 의 모델 접근을 끊어, 조달 의존 고객이 확인되지 않아 가로축은 작음이다.", "F7:openai")
    write("F7", "openai", {"changes": {}, "evidence_after": ev, "reason": "작음의 사유를 공유 잣대의 '조달 의존 고객이 확인되지 않음' 가지로 적는다(3차 확인 리뷰 B3). 입력은 그대로다"})

    # ---------- B4 openai ①·③ 문장(2차 보도 등급 표시) ----------
    j = J["F1:openai"]
    ev = replace_line(j["evidence"], "총마진(2025년 33%, 2024년 40%)은 2차 보도 수치이고 가격 실측의 재료(정가·구독자·단가)가 아니라",
                      "총마진(2025년 33%, 2024년 40%)은 익명 소식통을 인용한 2차 보도 수치라 가격 실측을 가르는 사실로 쓰지 않고, ③ 별도 수익모델의 단위경제 확인에는 "
                      "근거 등급(2차 보도)을 적어 쓴다. 구독자 이탈률과 업무당 비용 비교는 미확인이다.", "F1:openai")
    write("F1", "openai", {"changes": {}, "evidence_after": ev, "reason": "총마진의 근거 등급과 쓰임을 규칙 ① 표·2.7 에 맞게 적는다(3차 확인 리뷰 B4, 과제 47)"})
    j = J["F3:openai"]
    ev = sub_in_line(j["evidence"], "별도 수익모델은 통과다. 매출 대부분이 모델·구독 매출이지만 2차 보도된 매출총이익률이",
                     "2차 보도된 매출총이익률이", "2차 보도(익명 소식통 인용, 회사 1차 발표 없음)된 매출총이익률이", "F3:openai")
    ev = sub_in_line(ev, "후발 가속도는 지표 단계 a(연환산 매출)로 판정했다.", "저장한 성장률은 0.0 과 0.2 다.",
                     "저장한 성장률은 0.0 과 0.2 다. 이 시계열은 회사 1차 발표가 없어 2차 보도(익명 소식통 인용·외부 집계)에 기대며 그 등급을 적는다.", "F3:openai")
    write("F3", "openai", {"changes": {}, "evidence_after": ev, "reason": "③ 지표 수치의 근거 등급(2차 보도)을 판정 칸에 적는다(3차 확인 리뷰 B4, 규칙 2.7). 입력은 그대로다"})

    # ---------- B5 palantir ⑤: 규칙 ⑤ 표 문언으로 ----------
    j = J["F5:palantir"]
    ev = sub_in_line(j["evidence"], "고객에게 관계를 끊으라는 정당성 공격으로 실제 이탈이 생기면 구조형이다.",
                     "고객에게 관계를 끊으라는 정당성 공격으로 실제 이탈이 생기면 구조형이다.",
                     "고객에게 관계를 끊으라는 공격이 사업의 정당성 자체를 겨냥하면 규칙 ⑤ 표대로 구조형이며 이탈의 인과는 요건이 아니다.", "F5:palantir")
    ev = replace_line(ev, "영국 이탈의 직접 사유는 경찰 예산 중단과 자체 시스템 구축으로 보도돼",
                      "영국 이탈의 직접 사유는 경찰 예산 중단과 자체 시스템 구축으로 보도돼 정당성 공격이 이탈을 낳았다는 인과는 확인하지 못했으나, 규칙 ⑤ 표의 구조형은 사업의 "
                      "정당성 자체를 겨냥한 적대 자체로 서므로 인과 없이도 구조형이다.", "F5:palantir")
    write("F5", "palantir", {"changes": {}, "evidence_after": ev,
                             "reason": "구조형의 근거를 규칙 ⑤ 표 문언(사업의 정당성 자체를 겨냥한 적대)에 두고, 인과 미확인이 등급을 가르지 않음을 적는다(3차 확인 리뷰 B5). 입력은 그대로다"})
    print(f"제안 파일 {len(list(OUT.glob('*.json')))}개 → {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
