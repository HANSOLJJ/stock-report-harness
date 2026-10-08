# 확인 리뷰(confirm-r2)의 점수 무관 발견 L1~L3 을 반영할 제안 파일을 현재 판단에서 생성한다 — work/judge-fix2/
"""
사용: uv run --frozen python -X utf8 .agents/plans/rejudge-all-2026-11/work/make_fix2.py <slug>
반영은 apply_judgments.py --dir judge-fix2 로 한다. 바꾸려는 문장이 없으면 멈춘다.
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent / "judge-fix2"


def load(slug: str) -> dict[str, dict]:
    d = json.loads((ROOT / "output" / slug / "judgments.json").read_text(encoding="utf-8"))
    return {f'{j["factor"]}:{j["company_id"]}': j for j in d["items"]}


def replace_line(lines: list[str], needle: str, new: str, where: str) -> list[str]:
    hits = [i for i, l in enumerate(lines) if needle in l]
    if len(hits) != 1:
        raise SystemExit(f"[{where}] '{needle[:40]}…' 가 {len(hits)}번 나온다")
    out = list(lines)
    out[hits[0]] = new
    return out


def sub_in_line(lines: list[str], needle: str, old: str, new: str, where: str) -> list[str]:
    hits = [i for i, l in enumerate(lines) if needle in l]
    if len(hits) != 1:
        raise SystemExit(f"[{where}] '{needle[:40]}…' 가 {len(hits)}번 나온다")
    if old not in lines[hits[0]]:
        raise SystemExit(f"[{where}] 줄 안에 '{old}' 가 없다")
    out = list(lines)
    out[hits[0]] = lines[hits[0]].replace(old, new)
    return out


def write(factor: str, company: str, spec: dict) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{factor}-{company}.json").write_text(json.dumps(spec, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> int:
    J = load(sys.argv[1])
    if OUT.exists():
        shutil.rmtree(OUT)

    # L1: anthropic ③ 인용 위치
    j = J["F3:anthropic"]
    ev = sub_in_line(j["evidence"], "규칙 ③ 의 '공개 자료로 확인할 수 없으면 판정 보류",
                     "규칙 ③ 의 '공개 자료로 확인할 수 없으면 판정 보류(감점하되 실격은 아님)' 에 따라",
                     "규칙 2.5 의 단위경제 조건 '공개 자료로 확인할 수 없으면 판정 보류(감점하되 실격은 아님)' 에 따라", "F3:anthropic")
    write("F3", "anthropic", {"changes": {}, "evidence_after": ev, "reason": "판정 보류 문언의 위치를 규칙 2.5 로 바로 적는다(확인 리뷰 L1)"})

    # L2: tsmc ⑤ Intel 줄의 시점
    j = J["F5:tsmc"]
    ev = sub_in_line(j["evidence"], "경쟁 파운드리 Intel 은 서버·클라이언트 프로세서의 compute tile 을 TSMC N3B 로 만들지만",
                     "경쟁 파운드리 Intel 은 서버·클라이언트 프로세서의 compute tile 을 TSMC N3B 로 만들지만",
                     "경쟁 파운드리 Intel 은 2025년 서버·클라이언트 프로세서의 compute tile 을 TSMC N3B 로 만들었지만", "F5:tsmc")
    down = replace_line(j["evidence_down"], "Intel 은 서버·클라이언트 프로세서의 compute tile 을 TSMC N3B 로 만들지만",
                        "Intel 은 2025년 서버·클라이언트 프로세서의 compute tile 을 TSMC N3B 로 만들었고 TSMC 2나노 첫 고객 명단에 없으며, "
                        "2026년 초 자사 18A 공정 제품을 대량 생산하기 시작했다. [EV-tsmc-041, EV-tsmc-072]", "F5:tsmc")
    write("F5", "tsmc", {"changes": {}, "evidence_after": ev, "evidence_down_after": down,
                         "reason": "Intel 줄을 발췌 안의 사실(2025년 N3B 사용, 2026년 초 18A 대량 생산)만으로 다시 쓴다(확인 리뷰 L2)"})

    # L3: oracle ⑤ 동맹 출처 문구 — 유형 요소 없는 고객 관계는 판매(tsmc 와 같은 잣대)
    j = J["F5:oracle"]
    ev = replace_line(j["evidence"], "동맹 등급 +1 은 TikTok 미국 합작법인 지분 15% 와",
                      "동맹 등급 +1 은 TikTok 미국 합작법인 지분 15%, OpenAI 와의 Stargate 공동 구축·운영, 정부 클라우드 계약에서 나온다. OpenAI 는 5년 $300B 로 "
                      "보도된 계약과 Stargate 공동 구축·운영으로 묶여 떠날 수 없는 관계다. Meta·NVIDIA·TikTok·xAI·AMD 같은 OCI 대형 고객의 계약 수요와 Tencent 의 "
                      "칩 임차는 지분·공동개발·재판매·수수료 분배가 걸리지 않은 판매라 동맹 등급에 넣지 않는다.", "F5:oracle")
    up = [l for l in j["evidence_up"] if "[EV-oracle-030]" not in l and "[EV-oracle-005]" not in l]
    if len(up) != len(j["evidence_up"]) - 2:
        raise SystemExit("F5:oracle 올릴 근거에서 뺄 줄 둘을 찾지 못했다")
    write("F5", "oracle", {"changes": {}, "evidence_after": ev, "evidence_up_after": up,
                           "reason": "유형 요소 없는 OCI 고객 수요·Tencent 임차는 판매라 동맹 출처에서 빼고 올릴 근거에서도 뺀다. +1 은 TikTok 합작법인 지분·Stargate 공동 구축·정부 계약으로 선다(확인 리뷰 L3, tsmc 와 같은 잣대)"})
    print(f"제안 파일 {len(list(OUT.glob('*.json')))}개 → {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
