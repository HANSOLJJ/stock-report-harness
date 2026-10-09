# 승인 취소 뒤 수정(2026-10-09): Anthropic ⑤ 구조형 → 비용형, ⑧ 고객 축 미확인, OpenAI ① 2차 보도 문장 — work/judge-fix3/
"""
사용: uv run --frozen python -X utf8 .agents/plans/rejudge-all-2026-11/work/make_fix3.py <slug>
반영은 apply_judgments.py --dir judge-fix3 로 한다. 바꾸려는 문장이 없으면 멈춘다.

잣대: ⑤ 구조형(−2)은 '주요 고객' 이 공개 제출본의 집중 공시로 확정될 때만 매긴다. 유출된 상장 신청서 초안·2차 보도는 미확인이다.
같은 잣대를 OpenAI(고객 집중 미공개 → 비용형)에도 댄다. 사용자 지시(2026-10-09): 같은 사건(Microsoft 의 자체 모델 투입, SpaceX 의
Cursor 인수)이 두 회사에 다르게 읽혀서는 안 된다.
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent / "judge-fix3"


def load(slug: str) -> dict[str, dict]:
    d = json.loads((ROOT / "output" / slug / "judgments.json").read_text(encoding="utf-8"))
    return {f'{j["factor"]}:{j["company_id"]}': j for j in d["items"]}


def replace_line(lines: list[str], needle: str, new: str | None, where: str) -> list[str]:
    hits = [i for i, l in enumerate(lines) if needle in l]
    if len(hits) != 1:
        raise SystemExit(f"[{where}] '{needle[:40]}…' 가 {len(hits)}번 나온다")
    out = list(lines)
    if new is None:
        del out[hits[0]]
    else:
        out[hits[0]] = new
    return out


def write(factor: str, company: str, spec: dict) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{factor}-{company}.json").write_text(json.dumps(spec, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> int:
    J = load(sys.argv[1])
    if OUT.exists():
        shutil.rmtree(OUT)

    # ---------- anthropic ⑤: 구조형 −2 → 비용형 −1 ----------
    j = J["F5:anthropic"]
    ev = replace_line(j["evidence"], "Anthropic ⑤ 는 3 + 동맹 등급 +1 + 적대 등급 −2 로 2점이다.",
                      "Anthropic ⑤ 는 3 + 동맹 등급 +1 + 적대 등급 −1 로 3점이다.", "F5:anthropic")
    ev = replace_line(ev, "적대 등급 −2 는 구조형이다.",
                      "적대 등급 −1 은 비용형이다. 국방부 거래 배제의 유지와 사용 중단은 정부 시장 일부의 차단이고 FTC 조사는 업계 공통의 규제 조사라 져도 본업 수요가 남는다. "
                      "큰 고객 둘(Cursor·GitHub Copilot)은 자체 모델을 내는 경쟁사 소유이고 Microsoft 는 GitHub Copilot 에 자체 모델을 넣어 Claude 물량을 대신하기 시작했지만, "
                      "두 고객이 매출의 4분의 1 가까이를 낸다는 수치는 공개 제출본이 아니라 유출된 상장 신청서 초안과 2차 보도에 기대 구조형의 전제인 '주요 고객' 을 확정하지 "
                      "못했다(미확인). 같은 잣대로 OpenAI 도 고객 집중 미공개라 비용형에 둔다.", "F5:anthropic")
    ev = replace_line(ev, "다발형은 최대 유통 파트너 Amazon 과의 긴장이 보이지 않아 서지 않는다.",
                      "다발형은 구조형 전선이 없고 최대 유통 파트너 Amazon 과의 긴장이 보이지 않아 서지 않는다.", "F5:anthropic")
    ev = replace_line(ev, "큰 고객 둘의 매출 비중은 공개 제출본이 아니라 보도와 유출된 상장 신청서 초안에 기댄다.", None, "F5:anthropic")
    ev = replace_line(ev, "⑧ 에서 센 것, 곧 컴퓨트 공급자가 모두 모델 경쟁자라는 공급자=경쟁자 의존과 고객 둘의 매출 비중 크기는 여기서 다시 세지 않는다.",
                      "⑧ 에서 센 것, 곧 컴퓨트 공급자가 모두 모델 경쟁자라는 공급자=경쟁자 의존은 여기서 다시 세지 않는다. ⑤ 는 큰 고객이 경쟁사로서 대체품을 내는 속성만 세며, "
                      "두 고객의 매출 비중이 공개 제출본으로 확인되면 구조형으로 올린다.", "F5:anthropic")
    write("F5", "anthropic", {"changes": {"H": -1}, "evidence_after": ev,
                              "reason": "구조형의 전제인 '주요 고객' 이 공개 제출본이 아니라 유출 초안·2차 보도에 기대 미확인이라 비용형으로 둔다. 같은 사건(Microsoft 자체 모델 투입·Cursor 인수)을 "
                                        "OpenAI 와 같은 잣대로 읽는다(2026-10-09 사용자 지시, 규칙 2.1·Q03)"})

    # ---------- anthropic ⑧: 고객 축 −2 → 미확인(점수는 공급 축 −3 그대로) ----------
    j = J["F8:anthropic"]
    ev = replace_line(j["evidence"], "고객 축은 −2 다. 매출의 약 4분의 1 이 고객 두 곳에서 나온다는 보도(공개 제출본이 아니다)가 있어",
                      "고객 축은 미확인이다. 매출의 약 4분의 1 이 고객 두 곳에서 나온다는 보도가 있으나 공개 제출본의 집중 공시가 아니라 축을 재지 않았고, 재더라도 공급 축 −3 보다 가볍다.",
                      "F8:anthropic")
    write("F8", "anthropic", {"changes": {}, "evidence_after": ev,
                              "reason": "고객 집중을 유출 초안·2차 보도로 재지 않는다(⑤ 와 같은 잣대). 점수를 정한 공급 축은 그대로다"})

    # ---------- openai ①: ③ 과 모순되는 2차 보도 문장 ----------
    j = J["F1:openai"]
    ev = replace_line(j["evidence"], "총마진(2025년 33%, 2024년 40%)은 The Information 을 인용한 2차 보도라 판정에 쓰지 않았다.",
                      "총마진(2025년 33%, 2024년 40%)은 2차 보도 수치이고 가격 실측의 재료(정가·구독자·단가)가 아니라 ① 에서는 쓰지 않으며, ③ 별도 수익모델의 단위경제 확인에 쓴다. "
                      "구독자 이탈률과 업무당 비용 비교는 미확인이다.", "F1:openai")
    write("F1", "openai", {"changes": {}, "evidence_after": ev,
                           "reason": "① 과 ③ 이 같은 2차 보도 총마진을 두고 다른 말을 하던 것을 맞춘다(점수 무관)"})
    print(f"제안 파일 {len(list(OUT.glob('*.json')))}개 → {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
