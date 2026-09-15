# FIX-52: 설계 지침 4.1 범위표를 v1.7 값으로, Meta·OpenAI F2 근거란의 'AA 종합 1위 = 5' 잣대에 superseded 표시
"""점수 무영향. 옛 값과 옛 문장은 지우지 않고 낡음·superseded 표시로 남긴다.

재실행해도 같은 결과가 나온다. 파일 줄끝은 원래 것을 유지한다(HASH-EOL).
"""
from __future__ import annotations

import io
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard.rules import load_rules  # noqa: E402
from scorecard.schema import load_json_strict, validate_judgments  # noqa: E402

RUN_ID = "ai-scorecard-2026-09-obsreg"
RUN = ROOT / "scorecard" / "runs" / RUN_ID
GUIDE = ROOT / "docs" / "scorecard" / "design-guideline.md"
MARK = "[FIX-52 2026-09-15]"

ROWS = {
    "| F2 | ② 신기술 게임체인저 | 0~5 |": "| F2 | ② 신기술 게임체인저 | **2~5** (v1.7) · 낡음: 0~5 (v1.5·v1.6) |",
    "| F6 | ⑥ 가격 | -5~0 |": "| F6 | ⑥ 가격 | **-7~0** (v1.7) · 낡음: -5~0 (v1.5·v1.6) |",
    "| F7 | ⑦ 순환금융 | **-3~0** |": "| F7 | ⑦ 순환금융 | **-2~0** (v1.7) · 낡음: -3~0 (v1.5·v1.6) |",
    "| F9 | ⑨ 적자 깊이 | -5~0 |": "| F9 | ⑨ 적자 깊이 | **-4~0** (v1.7) · 낡음: -5~0 (v1.5·v1.6) |",
}
TABLE_NOTE = ("\n> **[낡음 표시 2026-09-15 FIX-52]** 범위 열은 v1.7 `scorecard/rules/v1.7.json` factors.*.range 기준이다. "
              "F2 는 사다리 바닥 2(C-03·IMPL-46), F6·F7·F9 는 함정 재배분(F6 -5→-7 · F7 -3→-2 · F9 -5→-4, 합 -18 보존)으로 "
              "바뀌었다. 옛 값은 v1.5·v1.6 실행의 범위라 지우지 않았다. 같은 표의 자동 산출·사람 입력 열 문구는 이번에 "
              "고치지 않았다(예: F6 `상장사 NTM PER 점수` 는 v1.7 parameters 정본과 다르다 — 5.1절 배너 참조).\n")
TABLE_ANCHOR = "| F9 | ⑨ 적자 깊이 |"

F2 = {
    "meta": {
        "old": "②5는 불가 — AA 종합 1위(Anthropic)가 5의 기준이고 Spark 1.3은 3위",
        "add": ("📐 " + MARK + " **C-03 확정 기준(혼합 모델)** — 5점은 `AA 종합 1위` 가 아니라 **성능 도약이 세대 격차 "
                "수준일 때**다. 경로 수 0·1·2 → 2·3·4. 위 근거의 `AA 종합 1위가 5의 기준` 문장은 C-03 확정 전 잣대라 "
                "superseded 다. 점수 4 는 승계 그대로이고, 세대 격차 판정은 이번 실행에서 하지 않았다."),
    },
    "openai": {
        "old": "②5는 Anthropic이 \"AA 종합 1위\"로 받은 점수라 같은 잣대로 불가",
        "add": ("📐 " + MARK + " **C-03 확정 기준(혼합 모델)** — 5점은 `AA 종합 1위` 가 아니라 **성능 도약이 세대 격차 "
                "수준일 때**다. 경로 수 0·1·2 → 2·3·4. 위 근거의 `AA 종합 1위로 받은 점수라 같은 잣대로 불가` 문장은 C-03 "
                "확정 전 잣대라 superseded 다. 점수 4 는 승계 그대로이고, 세대 격차 판정은 이번 실행에서 하지 않았다."),
    },
}


def update_guide() -> int:
    raw = io.open(GUIDE, encoding="utf-8", newline="").read()
    nl = "\r\n" if "\r\n" in raw else "\n"
    s = raw.replace("\r\n", "\n")
    n = 0
    for old, new in ROWS.items():
        if new in s:
            continue
        assert s.count(old) == 1, old
        s = s.replace(old, new, 1)
        n += 1
    if TABLE_NOTE.strip() not in s:
        lines = s.split("\n")
        idx = next(i for i, line in enumerate(lines) if line.startswith(TABLE_ANCHOR))
        lines.insert(idx + 1, TABLE_NOTE.rstrip("\n"))
        s = "\n".join(lines)
    io.open(GUIDE, "w", encoding="utf-8", newline="").write(s.replace("\n", nl))
    return n


def update_f2(jud: dict) -> list[str]:
    done = []
    for j in jud["items"]:
        cid = j["company_id"]
        if j["factor"] != "F2" or cid not in F2:
            continue
        spec = F2[cid]
        struck = f"~~{spec['old']}~~ (superseded {MARK} — C-03 확정 전 잣대)"
        ev = []
        for e in j["evidence"]:
            if spec["old"] in e and struck not in e:
                e = e.replace(spec["old"], struck, 1)
            ev.append(e)
        if spec["add"] not in ev:
            ev.append(spec["add"])
        j["evidence"] = ev
        if MARK not in (j.get("note") or ""):
            j["note"] = ((j.get("note") or "") + f" | {MARK} 근거란의 `AA 종합 1위 = 5` 잣대에 superseded 표시, "
                         "C-03 확정 기준 문장 추가. 점수·status 불변.")
        assert any(struck in e for e in ev), cid
        done.append(cid)
    return done


def main() -> int:
    n = update_guide()
    path = RUN / "judgments.json"
    raw = io.open(path, encoding="utf-8", newline="").read()
    nl = "\r\n" if "\r\n" in raw else "\n"
    jud = json.loads(raw)
    done = update_f2(jud)
    registry = {c["company_id"]: c for c in load_json_strict(ROOT / "scorecard" / "companies.json")["companies"]}
    validate_judgments(jud, registry, load_rules("v1.7").payload, RUN_ID)
    out = json.dumps(jud, ensure_ascii=False, indent=2) + ("\n" if raw.endswith("\n") else "")
    io.open(path, "w", encoding="utf-8", newline="").write(out.replace("\n", nl))
    print(f"설계 지침 범위표 {n}행 갱신 · F2 근거란 {', '.join(done)}")
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    sys.exit(main())
