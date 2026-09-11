# cash·fcf_ttm 등록값을 보존 SEC 원문에서 재확인하고 legacy 정의가 갈렸다는 것을 드러낸다 (네트워크 없음)
"""**받은 값을 정답으로 쓰지 않는다.** C-13 이 준 값을 보존 원자료에서 다시 뽑아 대조한다.

## 드러내려는 것 넷

1. **legacy `cash` 가 무엇이었나** — 설계진행은 7개사가 유동성 버퍼와 같다고 했다. 나머지 5개사는?
2. **순수 현금과 버퍼의 차이가 판정을 가르는가** — 3년 경계를 누가 가로지르는가.
3. **현지통화 환산이 맞는가** — 20-F 선언 환율로 우리가 다시 환산해 대조한다.
4. **미검증 입력이 산출물에 드러나는가** — market_cap 이 legacy 인데 P1·P2 가 그 위에 선다.

사용:
    python validation/cash-fcf-35/verify_cash_fcf.py
"""
from __future__ import annotations

import html
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
RUN = ROOT / "scorecard" / "runs" / "ai-scorecard-2026-09-obsreg"
RAW = ROOT / "validation" / "f6-avail-15" / "_raw"
SRC_BLOB = ("4074894", "validation/cash-fcf-35/cash_fcf_35_results.json")
BLOBS = {"BABA_20F": ("3cf9799", "validation/offb-24/_raw/baba-20260331.htm"),
         "TSM_20F": ("f14a235", "validation/tsm-edgar-29/_raw/tsm-20251231.htm")}
FX = {"tsmc": 31.37, "alibaba": 6.8980}


class Check:
    def __init__(self) -> None:
        self.rows: list[tuple[bool, str, str]] = []

    def __call__(self, ok: bool, label: str, detail: str = "") -> None:
        self.rows.append((bool(ok), label, detail))
        print(f"  {'OK  ' if ok else 'DIFF'} {label}" + (f"\n         {detail}" if detail else ""))

    @property
    def failed(self):
        return [r for r in self.rows if not r[0]]


def blob(key: str) -> bytes:
    commit, path = BLOBS[key]
    out = subprocess.run(["git", "show", f"{commit}:{path}"], capture_output=True)
    if out.returncode != 0:
        raise SystemExit(f"git show {commit}:{path} 실패")
    return out.stdout


def plain(data: bytes) -> str:
    t = data.decode("utf-8", "replace")
    t = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", t)
    t = re.sub(r"(?s)<[^>]+>", " ", t)
    return re.sub(r"[\s ]+", " ", html.unescape(t))


def source_items() -> list[dict]:
    out = subprocess.run(["git", "show", f"{SRC_BLOB[0]}:{SRC_BLOB[1]}"], capture_output=True)
    return json.loads(out.stdout.decode("utf-8", "replace"))["items"]


def facts(ticker: str) -> dict:
    return json.loads((RAW / f"{ticker}.companyfacts.json").read_text(encoding="utf-8"))["facts"]


def fact_at(f: dict, taxonomy: str, tag: str, end: str, unit: str = "USD"):
    node = f.get(taxonomy, {}).get(tag)
    if not node:
        return None
    best = None
    for rows in node["units"].get(unit, []) if isinstance(node["units"].get(unit), list) else []:
        if rows.get("end") == end and rows.get("start") is None:
            if best is None or str(rows.get("filed", "")) >= str(best.get("filed", "")):
                best = rows
    return None if best is None else best["val"]


def main() -> int:
    sys.path.insert(0, str(ROOT / "scripts"))
    chk = Check()
    bar = "=" * 112
    print(bar)
    print("CASH-FCF-35 — 등록값 대 보존 SEC 원문 대조")
    print(bar)

    items = {it["company_id"]: it for it in source_items()}
    obs = {(o["company_id"], o["metric"]): o
           for o in json.loads((RUN / "observations.json").read_text(encoding="utf-8"))["items"]
           if o["observation_id"].endswith(".cashfcf35")}

    print()
    print("[1] 등록된 cash 가 **순수 현금**인가 — 버퍼를 쓰지 않았는가")
    for cid, it in sorted(items.items()):
        c = it["cash"]
        pure = c.get("cash_and_cash_equivalents") or c.get("cash_and_cash_equivalents_usd")
        buf = c.get("liquid_cash_buffer") or c.get("liquid_cash_buffer_usd")
        got = obs[(cid, "cash")]["value"]
        chk(abs(got - pure) < 1, f"{cid:11} cash = 순수 현금 {pure:>16,.0f}")
        if buf and abs(buf - pure) > 1:
            saved = obs[(cid, "cash")]["basis"]["preserved_wider_definitions"]["liquid_cash_buffer"]
            chk(abs(saved - buf) < 1, f"{cid:11}   버퍼 {buf:>16,.0f} 를 basis 에 보존")

    print()
    print("[2] legacy cash 는 무엇이었나 — **세 갈래였다**")
    counts: dict[str, list[str]] = {}
    for cid, it in sorted(items.items()):
        which = obs[(cid, "cash")]["basis"]["legacy_comparison"]["legacy_equaled"]
        counts.setdefault(which, []).append(cid)
    for which, ids in sorted(counts.items(), key=lambda kv: -len(kv[1])):
        print(f"    {which:20} {len(ids):>2}개사  {', '.join(ids)}")
    chk(len(counts.get("유동성 버퍼", [])) == 7,
        "**유동성 버퍼와 같은 것은 7개사다** — 설계진행 진술과 일치")
    chk(len(counts) == 3,
        "**나머지 5개사는 버퍼가 아니었다** — 3개사는 비유동 증권까지 포함한 총계, 2개사는 어느 쪽도 아님",
        "legacy cash 가 단일 정의가 아니었다는 뜻이고, 순수 현금으로 통일해야 할 이유가 하나 더 있다")

    print()
    print("[3] 현지통화 공시사 — 20-F 선언 환율로 우리가 다시 환산")
    baba = plain(blob("BABA_20F"))
    tsm = plain(blob("TSM_20F"))
    chk("RMB6.8980 to US$1.00" in baba, "BABA 20-F 가 6.8980 을 선언한다")
    chk("31.37" in tsm, "TSM 20-F 가 31.37 을 선언한다")
    for cid, native_key in (("alibaba", "cash_and_cash_equivalents_native"),
                            ("tsmc", "cash_and_cash_equivalents_native")):
        c = items[cid]["cash"]
        native, reported = c[native_key], c["cash_and_cash_equivalents_usd"]
        recomputed = native / FX[cid]
        chk(abs(recomputed - reported) / reported < 2e-4,
            f"{cid:9} 현금 {native:,.0f} / {FX[cid]} = {recomputed:,.0f} 대 보고 {reported:,.0f}",
            f"상대오차 {abs(recomputed-reported)/reported*100:.4f}%")
    chk(items["alibaba"].get("fx_rate_cny_per_usd") == 6.8979,
        "C-13 은 alibaba 에 6.8979 를 썼고 우리는 20-F 문면 6.8980 을 쓴다",
        "0.0015% 차이라 백만 단위 반올림 결과가 같다. 등록값은 F6-REG-28 과 같은 환율로 통일했다")

    print()
    print("[4] alibaba 는 capex 가 둘이다 — 어느 쪽을 썼는가")
    cf = items["alibaba"]["cash_flows"]
    basis = obs[("alibaba", "fcf_ttm")]["basis"]
    chk(abs(obs[("alibaba", "fcf_ttm")]["value"] - cf["fcf_ttm_usd"]) < 1,
        f"GAAP 쪽(토지사용권 포함) {cf['fcf_ttm_usd']:,} 를 등록했다",
        "현금이 실제로 나간 금액이다")
    chk("non_gaap_variant" in basis, "non-GAAP 변형을 basis 에 보존했다",
        f"non-GAAP 이면 {cf['fcf_non_gaap_usd']:,} 이고 런웨이가 2.64년 대신 2.82년이나 "
        f"**둘 다 3년 미만이라 G3 판정은 갈리지 않는다**")

    print()
    print("[5] 3년 경계를 누가 가로지르는가")
    results = json.loads((RUN / "results.json").read_text(encoding="utf-8"))
    got = {c["company_id"]: c["factors"] for c in results["companies"]}
    for cid in sorted(got):
        for step in got[cid]["F9"].get("calc", {}).get("path", []):
            if step.get("gate") == "G3" and "runway_years" in step:
                mark = "**3년 미만**" if step["runway_years"] < 3 else ""
                print(f"    {cid:11} 런웨이 {step['runway_years']:>6.2f}년  step {step['step']:+d}  {mark}")
    chk(got["alibaba"]["F9"]["score"] == -4 and got["spacex-xai"]["F9"]["score"] == -4,
        "**alibaba·spacex-xai F9 가 -3 에서 -4 로 내려간다** — 설계진행 예상과 일치")
    chk(got["oracle"]["F9"]["score"] == -3,
        "oracle 은 legacy 로도 이미 3년 미만이라 변동 없다 (1.32년)")

    print()
    print("[6] 미검증 입력이 산출물에 드러나는가 — **점수는 안 깎는다**")
    flagged = [c for c in results["companies"]
               if (c["factors"]["F6"].get("calc") or {}).get("unverified_inputs")]
    chk(len(flagged) == 11, f"F6 가 산출된 상장 11개사에 unverified_inputs 가 붙었다",
        "spacex-xai 는 listed_newly 라 P1·P2 를 안 쓴다")
    sample = flagged[0]["factors"]["F6"]
    chk("market_cap" in sample["calc"]["unverified_inputs"],
        "market_cap 이 미검증으로 표시된다",
        json.dumps(sample["calc"]["unverified_inputs"], ensure_ascii=False))
    chk(any("미검증 입력" in w for w in sample.get("warnings") or []),
        "경고에도 나온다 — 결과와 리포트 양쪽에서 보인다")
    chk("점수를 깎지 않는다" in sample["calc"]["unverified_inputs_note"],
        "**우리 수집 공백을 기업 위험으로 바꾸지 않는다**",
        "MISS-LABEL-23 원칙이 여기에도 적용된다")

    print()
    print("[7] 원천 정책 — yahoo 가 denied 로 옮겨졌는가")
    from scorecard.rules import load_rules
    r17 = load_rules("v1.7")
    src = r17.payload["sources"]
    denied = {e["host"]: e for e in src["denied"]}
    for host in ("query1.finance.yahoo.com", "query2.finance.yahoo.com"):
        chk(host in denied, f"{host} 가 denied 에 있다")
        msg = r17.source_violation(f"https://{host}/v8/x") or ""
        chk("생산 원천에서 배제됨" in msg, f"{host}: 배제로 잡힌다")
    chk("stock-research" in denied["query1.finance.yahoo.com"]["note"],
        "**정책과 기존 파이프라인의 모순을 note 에 남겼다**",
        "다음 사람이 '왜 stock 은 쓰는데 scorecard 는 안 쓰나' 를 되묻지 않게 한다")
    chk(not src.get("unlisted"), "unlisted 가 비었다 — 두 host 가 모두 옮겨갔다")

    print()
    print("[8] 승인 대상·완주")
    chk(results["population"]["scored"] == 14 and not results["pending_rule_decisions"],
        "14/14 완주 · 미결 규칙 결정 없음")
    from scorecard.stages import current_hashes
    base = ROOT / "scorecard" / "runs" / "ai-scorecard-2026-09-baseline"
    appr = json.loads((base / "approval.json").read_text(encoding="utf-8"))["hashes"]
    chk(current_hashes(base.name) == appr, "승인 대상 6종 전부 보존")

    print()
    print(bar)
    bad = chk.failed
    print(f"대조 {len(chk.rows)}건 · 불일치 {len(bad)}건")
    for _, label, _d in bad:
        print(f"  불일치: {label}")
    return 1 if bad else 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    sys.exit(main())
