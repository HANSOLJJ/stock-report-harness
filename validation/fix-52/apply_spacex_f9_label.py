# FIX-52: spacex-xai.F9.obsreg25 근거란의 v1.5 수치에 인용 라벨을 붙이고 이 실행의 verified 값을 함께 적는다
"""리뷰 A(qwen) 발견. status new 판단인데 -14.9%·순손실 -$8.9B·FCF -$32.5B·현금 $100B·3년 런웨이가 v1.5 문면 그대로다.
점수는 verified 값으로 이미 계산되고 있다(results F9 calc). 원문 문장은 지우지 않고 라벨만 붙인다.

재실행해도 같은 결과가 나온다.
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
MARK = "[FIX-52 2026-09-15]"
LABELS = {
    "게이트 1 ❌ — 영업손실률 -14.9%": "(v1.5 인용 · 채점표_v1.5.md 671·673행) ",
    "FCF -$32.5B(capex $42B": "(v1.5 인용 · 채점표_v1.5.md 672행) ",
    "완충: 현금 $100B(IPO), 3년 런웨이": "(v1.5 인용 · 채점표_v1.5.md 674행) ",
}


def main() -> int:
    path = RUN / "judgments.json"
    raw = io.open(path, encoding="utf-8", newline="").read()
    nl = "\r\n" if "\r\n" in raw else "\n"
    jud = json.loads(raw)
    obs = {o["observation_id"]: o for o in json.loads((RUN / "observations.json").read_text(encoding="utf-8"))["items"]}
    res = next(c for c in json.loads((RUN / "results.json").read_text(encoding="utf-8"))["companies"]
               if c["company_id"] == "spacex-xai")
    runway = next(p["runway_years"] for p in res["factors"]["F9"]["calc"]["path"] if p.get("gate") == "G3")
    j = next(x for x in jud["items"] if x["judgment_id"] == "spacex-xai.F9.obsreg25")
    ev = []
    for e in j["evidence"]:
        for start, label in LABELS.items():
            if e.startswith(start):
                e = label + e
        ev.append(e)
    om = obs["spacex-xai.operating_margin_ttm.f6reg28"]
    ni = obs["spacex-xai.net_income_ttm.f6reg28"]
    fcf = obs["spacex-xai.fcf_ttm.cashfcf35"]
    cash = obs["spacex-xai.cash.cashfcf35"]
    header = (f"📐 {MARK} **이 실행의 verified 값** — 영업손실률 {om['value'] * 100:.3f}%(TTM {om['period']['start']}~"
              f"{om['period']['end']}) · 순손실 {ni['value'] / 1e6:,.0f}M(TTM) · FCF {fcf['value'] / 1e6:,.0f}M(TTM) · "
              f"현금 {cash['value'] / 1e6:,.0f}M({cash['as_of']}) · 런웨이 {runway:.2f}년(G3 계산). 점수는 이 값으로 계산된다. "
              "아래 `(v1.5 인용)` 라벨이 붙은 줄의 -14.9%·-$8.9B·-$32.5B·$100B·3년은 v1.5 채점표 문면이다.")
    if not any(e.startswith(f"📐 {MARK}") for e in ev):
        ev.insert(0, header)
    j["evidence"] = ev
    if MARK not in (j.get("note") or ""):
        j["note"] = (j.get("note") or "") + f" | {MARK} v1.5 수치 줄에 인용 라벨, verified 값 머리줄 추가(리뷰 A). 점수·입력 불변."
    registry = {c["company_id"]: c for c in load_json_strict(ROOT / "scorecard" / "companies.json")["companies"]}
    validate_judgments(jud, registry, load_rules("v1.7").payload, RUN_ID)
    out = json.dumps(jud, ensure_ascii=False, indent=2) + ("\n" if raw.endswith("\n") else "")
    io.open(path, "w", encoding="utf-8", newline="").write(out.replace("\n", nl))
    print(header)
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    sys.exit(main())
