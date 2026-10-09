# 4차 확인 리뷰(confirm-r4) L1·L3·L4·L5 — 점수 무관 문장 수정 제안을 만든다(work/judge-fix5/)
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent / "judge-fix5"


def load(slug: str):
    d = json.loads((ROOT / "output" / slug / "judgments.json").read_text(encoding="utf-8"))
    return {f'{j["factor"]}:{j["company_id"]}': j for j in d["items"]}


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
    J = load(sys.argv[1])
    if OUT.exists():
        shutil.rmtree(OUT)
    # L1 oracle ⑤
    j = J["F5:oracle"]
    ev = sub_in_line(j["evidence"], "⑧ 에서 센 OpenAI 계약 집중과 장기 리스 약정은 여기서 다시 세지 않는다.",
                     "⑧ 에서 센 OpenAI 계약 집중과 장기 리스 약정은 여기서 다시 세지 않는다. 같은 OpenAI 관계를 ⑤ 에서는 동맹으로, ⑧ 에서는 의존으로 따로 센다.",
                     "⑧ 에서 센 미개시 데이터센터 리스와 무조건 구매 약정은 여기서 다시 세지 않는다. 같은 OpenAI 관계를 ⑤ 에서는 동맹으로 세고, ⑧ 에서는 OpenAI 고객 집중을 "
                     "2차 보도뿐이라 재지 않았다.", "F5:oracle")
    write("F5", "oracle", {"changes": {}, "evidence_after": ev, "reason": "⑧ 이 OpenAI 고객 집중을 재지 않게 된 뒤의 교차 참조로 고친다(4차 확인 리뷰 L1)"})
    # L4 oracle ⑦
    j = J["F7:oracle"]
    ev = sub_in_line(j["evidence"], "Oracle 의 비율은 OpenAI 가 Oracle 클라우드에 5년 동안 낼 $300B 를",
                     "Oracle 의 비율은 OpenAI 가 Oracle 클라우드에 5년 동안 낼 $300B 를",
                     "Oracle 의 비율은 2차 보도된 OpenAI 의 Oracle 클라우드 5년 $300B 약정을", "F7:oracle")
    write("F7", "oracle", {"changes": {}, "evidence_after": ev, "reason": "⑦ 가로축에 쓴 약정 수치의 근거 등급(2차 보도)을 적는다(4차 확인 리뷰 L4, 규칙 2.1 둘째 줄)"})
    # L3 openai ①
    j = J["F1:openai"]
    ev = sub_in_line(j["evidence"], "총마진(2025년 33%, 2024년 40%)은 익명 소식통을 인용한 2차 보도 수치라 가격 실측을 가르는 사실로 쓰지 않고",
                     "총마진(2025년 33%, 2024년 40%)은 익명 소식통을 인용한 2차 보도 수치라 가격 실측을 가르는 사실로 쓰지 않고, ③ 별도 수익모델의 단위경제 확인에는 "
                     "근거 등급(2차 보도)을 적어 쓴다.",
                     "총마진(2025년 33%, 2024년 40%)은 익명 소식통을 인용한 2차 보도 수치이고, 2025년 추론 비용의 절반 가까이를 돈을 내지 않는 이용자에게 쓴 원가 요인과 가격 효과를 "
                     "가르지 못해 ① 가격 실측에 쓰지 않는다. ③ 별도 수익모델에서는 같은 수치를 근거 등급(2차 보도)을 적어 단위경제 확인에 쓴다.", "F1:openai")
    write("F1", "openai", {"changes": {}, "evidence_after": ev, "reason": "총마진을 ① 에서 빼는 사유를 원가 요인(다른 ① 판단과 같은 잣대)으로 적는다(4차 확인 리뷰 L3)"})
    # L5 openai ⑦
    j = J["F7:openai"]
    ev = sub_in_line(j["evidence"], "회사가 밝힌 매출 구성비로 잰다", "", "", "F7:openai")  # 존재 확인만
    lines = list(ev)
    idx = next(i for i, l in enumerate(lines) if "회사가 밝힌 매출 구성비로 잰다" in l)
    lines[idx] = "OpenAI 는 비상장이라 계약 잔고와 최근 1년 매출을 공시하지 않는다."
    lines = sub_in_line(lines, "OpenAI 는 2026-08-29 SpaceX 에 인수된 Cursor 의 모델 접근을 끊어",
                        "OpenAI 는 2026-08-29 SpaceX 에 인수된 Cursor 의 모델 접근을 끊어",
                        "OpenAI 는 2026-08-29 SpaceX 에 인수된 Cursor 의 모델 접근을 끊기로 했고 그 뒤 접근이 이어졌다는 확정 근거가 없어", "F7:openai")
    write("F7", "openai", {"changes": {}, "evidence_after": lines, "reason": "판정 경로와 맞지 않는 측정 문장을 줄이고 Cursor 접근 종료를 근거 수준(종료 결정)대로 적는다(4차 확인 리뷰 L5)"})
    print(f"제안 파일 {len(list(OUT.glob('*.json')))}개 → {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
