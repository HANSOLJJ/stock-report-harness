# 사용자 결정(2026-10-12): ⑧ 약정 축의 '몇 배(−3)' 경계를 3배로 — ⑧ 판단 14건 공유 문장과 배수 문장, Alphabet 점수를 고친다(work/judge-fix3/)
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from make_fix1 import judgments, replace_one, spec  # noqa: E402

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "scripts"))
from scorecard.paths import run_paths  # noqa: E402
from scorecard.schema import load_json_strict, write_json  # noqa: E402

OUT = Path(__file__).resolve().parent / "judge-fix3"
OLD_J3 = "20배 이상(수십 배)이면 −4, 2배 이상 20배 미만(몇 배)이면 −3, 0.5배 이상 2배 미만(1배 안팎)이면 −2 이며 0.5배 미만은 점수에 닿지 않는다."
NEW_J3 = ("20배 이상(수십 배)이면 −4, 3배 이상 20배 미만(몇 배)이면 −3, 0.5배 이상 3배 미만(1배 안팎에서 두어 배)이면 −2 이며 0.5배 미만은 점수에 닿지 않는다. "
          "3배 경계는 '몇 배' 의 말뜻과, 여러 해에 걸쳐 내는 약정을 한 해 부담으로 펴면 2~3배 약정은 매출의 일부라는 점을 보고 정했다.")


def write(name, s):
    (OUT / f"{name}.json").write_text(json.dumps(s, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> int:
    slug = sys.argv[1]
    J = judgments(slug)
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    companies = sorted(c for (c, f) in J if f == "F8")
    for cid in companies:
        j = J[(cid, "F8")]
        ev = list(j["evidence"])
        hits = [i for i, l in enumerate(ev) if OLD_J3 in l]
        if len(hits) != 1:
            raise SystemExit(f"[{cid}] 공유 경계 문장이 {len(hits)}번")
        ev[hits[0]] = ev[hits[0]].replace(OLD_J3, NEW_J3)
        up, down = list(j.get("evidence_up") or []), list(j.get("evidence_down") or [])
        changes: dict = {}
        reason = "⑧ 약정 축 경계를 3배로 정한 사용자 결정(2026-10-12)을 공유 문장에 반영한다. 점수는 그대로다"
        if cid in ("microsoft", "nvidia", "spacex-xai"):
            ev = [l.replace("0.5배 이상 2배 미만", "0.5배 이상 3배 미만") for l in ev]
        if cid == "alphabet":
            changes = {"score": -2}
            reason = "⑧ 약정 축 경계를 3배로 정한 사용자 결정(2026-10-12)에 따라 2.02배는 −2 다"
            ev = replace_one(ev, "알파벳 ⑧ 은 −3 이고",
                             "알파벳 ⑧ 은 −2 이고 점수를 정한 축은 약정 축, 곧 아직 개시되지 않은 데이터센터 리스와 구매 약정·기타 계약상 의무를 더한 약 $9,020억이 "
                             "최근 1년 매출의 약 2.02배인 것이다.", "alphabet J6")
            ev = replace_one(ev, "약정 축은 −3 이다. 2026-06-30 10-Q 경영진 논의의",
                             [l for l in ev if l.startswith("약정 축은 −3 이다. 2026-06-30 10-Q 경영진 논의의")][0]
                             .replace("약정 축은 −3 이다.", "약정 축은 −2 다.").replace("의 약 2.02배다(계산).", "의 약 2.02배로 0.5배 이상 3배 미만이다(계산)."),
                             "alphabet J7")
            ev = replace_one(ev, "주석 10 의 1년 넘는 고정·보장 약정 $707.0B 만 쓰면",
                             [l for l in ev if "주석 10 의 1년 넘는 고정·보장 약정 $707.0B 만 쓰면" in l][0]
                             .replace("약 1.79배로 −2 이고, 총액 기준 2.02배는 2배 경계 바로 위다(계산).", "약 1.79배이고, 어느 쪽이든 3배 미만이다(계산)."),
                             "alphabet J8")
        if cid == "meta":
            reason = "⑧ 약정 축 경계를 3배로 정한 사용자 결정에 맞춰, 기준일 전에 공시된 2026-07 추가 리스를 더한 3.05배로 −3 을 잰다(규칙 2.1)"
            ev = replace_one(ev, "Meta ⑧ 은 −3 이고",
                             "Meta ⑧ 은 −3 이고 점수를 정한 축은 약정 축, 곧 아직 개시되지 않은 리스와 해지할 수 없는 계약상 약정에 2026-07 에 더 맺은 데이터센터 리스를 "
                             "더한 약 $6,963억이 최근 1년 매출의 약 3.05배인 것이다.", "meta J6")
            ev = replace_one(ev, "약정 축은 −3 이다. 2026-06-30 10-Q 주석 9",
                             [l for l in ev if l.startswith("약정 축은 −3 이다. 2026-06-30 10-Q 주석 9")][0]
                             + " 같은 10-Q 는 2026-07 에 리스 의무 약 $680억의 데이터센터 리스를 더 맺었다고 밝혀, 이를 더한 약 $6,963억은 약 3.05배로 3배 이상 20배 "
                               "미만(몇 배)이다(계산). 감점은 구속력 있는 약정까지 세므로(규칙 2.1) 기준일 전에 공시된 추가 리스를 넣는다.", "meta J7")
            ev = replace_one(ev, "2026·2027년에 갚을 약정 $1,351.7억을 빼도",
                             "2026·2027년에 갚을 약정 $1,351.7억을 빼면 추가 리스를 더해도 약 2.46배이고 2026-06-30 몫만 보면 약 2.75배라, 3.05배는 3배 경계 바로 위다"
                             "(계산).", "meta J8")
            down.insert(1, "2026-07 에 리스 의무 약 $680억의 데이터센터 리스를 더 맺었다. [EV-meta-059]")
        if cid == "anthropic":
            ev = replace_one(ev, "약정 축은 −3 이고 받치는 근거의 등급을 바꿔도 같은 구간에 든다.",
                             [l for l in ev if l.startswith("약정 축은 −3 이고 받치는 근거의 등급을 바꿔도 같은 구간에 든다.")][0]
                             .replace("약정 축은 −3 이고 받치는 근거의 등급을 바꿔도 같은 구간에 든다.", "약정 축은 −3 이다.")
                             + " 2차 보도 수치는 등급을 적어 쓰므로 Google 보도분을 더한 5.1배로 재고, 공시·회사 1차 몫만으로는 2배를 넘는 하한이라 3배를 넘는지 확인되지 "
                               "않았으나(미확인) ⑧ 은 공급 축 −3 이 정해 점수는 같다.", "anthropic J8")
        write(f"F8-{cid}", spec(j, changes=changes, ev=ev, up=up, down=down, reason=reason))

    # TRG-092 의 경계 표현
    p = run_paths(slug).triggers
    trg = load_json_strict(p)
    t = next(x for x in trg["items"] if x["trigger_id"] == "TRG-092")
    old = "연환산 매출의 2배 이상 20배 미만이라 −3 이고"
    if old not in t["observation"]:
        raise SystemExit("TRG-092 문장이 없다")
    t["observation"] = t["observation"].replace(old, "연환산 매출의 3배 이상 20배 미만이라 −3 이고")
    write_json(p, trg)
    print(f"제안 파일 {len(list(OUT.glob('*.json')))}개, 트리거 1건 고침")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
