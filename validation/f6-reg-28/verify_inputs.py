# F6 입력으로 등록할 값을 보존 원자료에서 직접 재확인하고 환산·복원의 함정 넷을 드러낸다 (네트워크 없음)
"""**받은 값을 정답으로 쓰지 않는다.** 두 선행 조사와 내 수집기를 서로 대조하고 원문으로 판정한다.

    G1-FILL-27   C-13 1badc57 · NTM 795ed3d   revenue_ttm · operating_income_ttm (12개사)
    F6-SPEC-18   내 워크트리 validation/f6-spec-18  net_income_ttm · revenue_ttm_prior (12개사)
    원자료        validation/f6-avail-15/_raw/*.companyfacts.json · C-13 3cf9799 S-1/A

## 이 스크립트가 드러내려는 것 넷

1. **두 조사의 TTM 이 어디서 갈리는가** — meta·nvidia 가 1백만 달러 어긋난다. 방법 차이다.
2. **SPCX 전년 TTM 은 복원되지 않는다** — 2024년 상반기 사실이 어느 문서에도 없다.
3. **공시 USD 환산치를 두 해 그대로 쓰면 성장률 밴드가 바뀐다** — alibaba 가 -3 에서 -2 로 뜬다.
4. **재작성 세대가 섞이면 Q4 복원이 깨진다** — MSFT FY2016 이 5,834 백만 어긋난다.

사용:
    python validation/f6-reg-28/verify_inputs.py
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
RAW = ROOT / "validation" / "f6-avail-15" / "_raw"
SPEC18 = ROOT / "validation" / "f6-spec-18" / "_derived" / "ttm_inputs.json"

G1_BLOB = ("1badc57", "validation/g1-fill-27/g1_fill_27_results.json")

# 20-F 가 스스로 선언한 convenience translation 환율.
#   BABA  FY2026 20-F  "RMB6.8980 to US$1.00 ... H.10 statistical release of the Federal Reserve Board"
#   TSM   FY2024 20-F  선언 문구는 이 워크트리에 원문이 없어 companyfacts 의 TWD/USD 쌍에서 역산한다
FX = {"alibaba": ("CNY", 6.8980), "tsmc": ("TWD", 32.79)}
# TSM FY2025 원문. companyfacts 미등재라 EDGAR 원문 우회 건이다 (C-13 TSM-EDGAR-29).
BLOBS = {"TSM_20F_FY2025": ("f14a235", "validation/tsm-edgar-29/_raw/tsm-20251231.htm")}


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


def blob_json(commit: str, path: str):
    out = subprocess.run(["git", "show", f"{commit}:{path}"], capture_output=True)
    if out.returncode != 0:
        raise SystemExit(f"git show {commit}:{path} 실패")
    return json.loads(out.stdout.decode("utf-8", "replace"))


def plain(data: bytes) -> str:
    import html
    import re
    t = data.decode("utf-8", "replace")
    t = re.sub(r"(?is)<(script|style).*?</>", " ", t)
    t = re.sub(r"(?s)<[^>]+>", " ", t)
    return re.sub(r"[\s ]+", " ", html.unescape(t))


def facts(ticker: str) -> dict:
    return json.loads((RAW / f"{ticker}.companyfacts.json").read_text(encoding="utf-8"))["facts"]


def rows_for(f: dict, taxonomy: str, tag: str):
    t = f.get(taxonomy, {}).get(tag)
    if not t:
        return []
    return [dict(r, unit=u) for u, rs in t["units"].items() for r in rs if r.get("start")]


def pick(f: dict, taxonomy: str, tag: str, start: str, end: str, unit: str | None = None):
    for r in rows_for(f, taxonomy, tag):
        if r["start"] == start and r["end"] == end and (unit is None or r["unit"] == unit):
            return r
    return None


def p3_band(growth: float) -> int:
    """v1.7 P3 밴드. lower_inclusive."""
    for lower, score in ((0.30, 0), (0.15, -1), (0.05, -2)):
        if growth >= lower:
            return score
    return -3


def p1_band(per: float) -> int:
    for upper, score in ((25, 0), (45, -1)):
        if per < upper:
            return score
    return -2


def p2_band(ev_sales: float) -> int:
    for upper, score in ((8, 0), (20, -1)):
        if ev_sales < upper:
            return score
    return -2


def main() -> int:
    chk = Check()
    bar = "=" * 110
    print(bar)
    print("F6-REG-28 — 등록값 대 보존 원자료 대조")
    print(bar)

    g1 = {it["company_id"]: it for it in blob_json(*G1_BLOB)["items"]}
    spec18 = {x["company_id"]: x for x in json.loads(SPEC18.read_text(encoding="utf-8"))}

    # ---------------------------------------------------------------- [1]
    print()
    print("[1] 두 조사의 revenue_ttm·operating_income_ttm 대조 (12개사)")
    print(f"  {'회사':11} {'G1-FILL-27':>20} {'F6-SPEC-18':>20} {'차':>14}  비고")
    method_gap = []
    for cid in sorted(g1):
        a = g1[cid]["revenue_ttm"]
        b = (spec18.get(cid, {}).get("metrics", {}).get("revenue_ttm") or {}).get("value")
        if b is None:
            continue
        diff = a - b
        note = "" if diff == 0 else ("기간 기준 자체가 다름" if abs(diff) > 1_000_000 else "방법 차 1백만")
        if diff and abs(diff) <= 1_000_000:
            method_gap.append(cid)
        print(f"  {cid:11} {a:>20,} {b:>20,} {diff:>14,}  {note}")
    chk(set(method_gap) == {"meta", "nvidia"},
        "두 조사가 갈리는 곳은 meta·nvidia 1백만 달러뿐 (SPCX 는 기준 자체가 다름)",
        "원인은 회사 자체 XBRL 반올림이다 — 분기 태그 합과 YTD 태그가 1백만 다르다. 아래 [1b] 참조")

    print()
    print("[1b] meta 1백만 차의 출처 — 회사 XBRL 안에서 이미 어긋나 있다")
    f = facts("META")
    tag = "RevenueFromContractWithCustomerExcludingAssessedTax"
    q1 = pick(f, "us-gaap", tag, "2026-01-01", "2026-03-31")
    q2 = pick(f, "us-gaap", tag, "2026-04-01", "2026-06-30")
    h1 = pick(f, "us-gaap", tag, "2026-01-01", "2026-06-30")
    if q1 and q2 and h1:
        chk(q1["val"] + q2["val"] != h1["val"],
            f"분기 합 {q1['val'] + q2['val']:,} != 상반기 YTD 태그 {h1['val']:,}",
            f"차 {q1['val'] + q2['val'] - h1['val']:,} — 어느 쪽도 틀리지 않았고 반올림 자리가 다르다. "
            f"228,248 대 228,247 은 0.0004% 이고 P3·P2 밴드를 가르지 않는다")

    # ---------------------------------------------------------------- [2]
    print()
    print("[2] SPCX — 현재 TTM 은 복원되고 전년 TTM 은 복원되지 않는다")
    fs = facts("SPCX")
    comp = {}
    for label, tag in (("revenue", "RevenueFromContractWithCustomerExcludingAssessedTax"),
                       ("operating", "OperatingIncomeLoss"), ("net", "NetIncomeLoss")):
        comp[label] = {
            "h1_2026": pick(fs, "us-gaap", tag, "2026-01-01", "2026-06-30"),
            "h1_2025": pick(fs, "us-gaap", tag, "2025-01-01", "2025-06-30"),
            "h1_2024": pick(fs, "us-gaap", tag, "2024-01-01", "2024-06-30"),
        }
    # S-1/A 감사 손익계산서(백만 USD). 원문 대조는 verify_values 형태로 [2b] 에서 다시 본다.
    S1A = {"revenue": {2025: 18_674, 2024: 14_015, 2023: 10_387},
           "operating": {2025: -2_589, 2024: 466, 2023: -3_505},
           "net": {2025: -4_937, 2024: 791, 2023: -4_628}}
    ttm = {}
    for label in ("revenue", "operating", "net"):
        fy = S1A[label][2025] * 1_000_000
        ttm[label] = fy + comp[label]["h1_2026"]["val"] - comp[label]["h1_2025"]["val"]
        print(f"  {label:10} FY2025 {fy:>16,} + H1'26 {comp[label]['h1_2026']['val']:>16,} "
              f"- H1'25 {comp[label]['h1_2025']['val']:>16,} = {ttm[label]:>16,}")
    chk(ttm["revenue"] == 23_044_000_000, "TTM 매출 23,044", f"지시서 값과 일치")
    chk(ttm["operating"] == -3_732_000_000, "TTM 영업손익 -3,732")
    margin = ttm["operating"] / ttm["revenue"]
    chk(abs(margin - (-0.16195)) < 1e-5, f"TTM 영업손실률 {margin*100:.3f}%",
        "지시서 -16.20% 와 일치. 승계 legacy 값 -14.9% 와 1.30%p 차")
    chk(comp["revenue"]["h1_2024"] is None,
        "**전년 TTM 은 복원 불가** — 2024년 상반기 사실이 companyfacts 에 없다",
        "전년 TTM(2024-07-01~2025-06-30) = FY2024 + H1'25 - H1'24 인데 H1'24 가 어느 문서에도 없다. "
        "S-1/A 는 연간 3개년과 1분기만, 10-Q 는 2025·2026 상반기만 준다")

    # ---------------------------------------------------------------- [3]
    print()
    print("[3] 통화 함정 — 공시 USD 환산치를 두 해 그대로 쓰면 성장률 밴드가 바뀐다")
    print("    P3 는 규칙이 '현지통화로 계산한다'고 적어 두었다(policies.f6.parameters.P3.currency_note).")
    for cid, ticker, tax, tag, cur, (p_start, p_end), (c_start, c_end) in (
            ("alibaba", "BABA", "us-gaap", "Revenues", "CNY",
             ("2024-04-01", "2025-03-31"), ("2025-04-01", "2026-03-31")),
            ("tsmc", "TSM", "ifrs-full", "Revenue", "TWD",
             ("2023-01-01", "2023-12-31"), ("2024-01-01", "2024-12-31"))):
        f = facts(ticker)
        cur_loc = pick(f, tax, tag, c_start, c_end, cur)
        pri_loc = pick(f, tax, tag, p_start, p_end, cur)
        cur_usd = pick(f, tax, tag, c_start, c_end, "USD")
        pri_usd = pick(f, tax, tag, p_start, p_end, "USD")
        rate = FX[cid][1]
        g_local = cur_loc["val"] / pri_loc["val"] - 1
        g_usd_filed = cur_usd["val"] / pri_usd["val"] - 1
        g_same_rate = (cur_loc["val"] / rate) / (pri_loc["val"] / rate) - 1
        print(f"  {cid}")
        print(f"    현지통화        {cur_loc['val']:>18,} / {pri_loc['val']:>18,} = {g_local*100:+7.3f}%  밴드 {p3_band(g_local):+d}")
        print(f"    공시 USD 그대로 {cur_usd['val']:>18,} / {pri_usd['val']:>18,} = {g_usd_filed*100:+7.3f}%  밴드 {p3_band(g_usd_filed):+d}"
              f"   (환율 {cur_loc['val']/cur_usd['val']:.4f} 대 {pri_loc['val']/pri_usd['val']:.4f} — accession 이 다르다)")
        print(f"    같은 환율 {rate}  {cur_loc['val']/rate:>18,.0f} / {pri_loc['val']/rate:>18,.0f} = {g_same_rate*100:+7.3f}%  밴드 {p3_band(g_same_rate):+d}")
        chk(p3_band(g_local) == p3_band(g_same_rate),
            f"{cid}: 같은 환율로 환산하면 밴드가 현지통화와 같다", "환율이 분자·분모에서 상쇄된다")
        if p3_band(g_usd_filed) != p3_band(g_local):
            chk(True, f"**{cid}: 공시 USD 를 그대로 쓰면 밴드가 {p3_band(g_local):+d} 에서 {p3_band(g_usd_filed):+d} 로 뜬다**",
                "두 해의 convenience translation 환율이 서로 다른 20-F 에서 왔기 때문이다. 함정이 실재한다")
        else:
            chk(True, f"{cid}: 공시 USD 를 그대로 써도 이번에는 밴드가 같다", "다만 값은 왜곡된다")

    print()
    print("[3b] 환산 결과가 발행사 자체 USD 공시와 맞는지")
    f = facts("TSM")
    for tag, filed_usd in (("Revenue", 88_268_000_000), ("ProfitLoss", 35_301_100_000),
                           ("ProfitLossFromOperatingActivities", 40_318_800_000)):
        loc = pick(f, "ifrs-full", tag, "2024-01-01", "2024-12-31", "TWD")
        got = loc["val"] / FX["tsmc"][1]
        chk(abs(got - filed_usd) / filed_usd < 1e-4,
            f"TSM {tag}: TWD/{FX['tsmc'][1]} = {got:,.0f} 대 공시 USD {filed_usd:,}",
            f"상대오차 {abs(got-filed_usd)/filed_usd*100:.4f}%")
    f = facts("BABA")
    for tag, filed_usd in (("Revenues", 148_401_000_000), ("NetIncomeLoss", 15_018_000_000),
                           ("OperatingIncomeLoss", 7_270_000_000)):
        loc = pick(f, "us-gaap", tag, "2025-04-01", "2026-03-31", "CNY")
        got = loc["val"] / FX["alibaba"][1]
        chk(abs(got - filed_usd) / abs(filed_usd) < 1e-3,
            f"BABA {tag}: CNY/{FX['alibaba'][1]} = {got:,.0f} 대 공시 USD {filed_usd:,}",
            f"상대오차 {abs(got-filed_usd)/abs(filed_usd)*100:.4f}%")

    print()
    print("[3c] P2 는 환산을 안 하면 무너진다 — TSM 으로 확인")
    obs = json.loads((ROOT / "scorecard" / "runs" / "ai-scorecard-2026-09-obsreg"
                      / "observations.json").read_text(encoding="utf-8"))["items"]
    got = {(o["company_id"], o["metric"]): o for o in obs if o["value"] is not None}
    mc = got[("tsmc", "market_cap")]["value"]
    nc = got[("tsmc", "net_cash")]["value"]
    twd = 2_894_307_700_000
    for label, rev in (("TWD 를 그대로 넣으면", twd),
                       (f"{FX['tsmc'][1]} 로 환산하면", twd / FX["tsmc"][1]),
                       ("H.10 현물 31.37 이면", twd / 31.37)):
        ev_s = (mc - nc) / rev
        print(f"    {label:24} EV/Sales = {ev_s:>8.3f}  밴드 {p2_band(ev_s):+d}")
    chk(p2_band((mc - nc) / twd) != p2_band((mc - nc) / (twd / FX["tsmc"][1])),
        "**환산하지 않으면 P2 가 -2 에서 0 으로 뜬다** — 두 칸이다")
    chk(p2_band((mc - nc) / (twd / FX["tsmc"][1])) == p2_band((mc - nc) / (twd / 31.37)),
        "환율을 32.79 로 쓰든 31.37 로 쓰든 P2 밴드는 같다",
        "환율 선택이 점수를 가르지 않는다는 것까지 확인한다")

    # ---------------------------------------------------------------- [4]
    print()
    print("[4] 재작성 세대 — MSFT FY2016 은 Q4 복원을 깨뜨린다")
    f = facts("MSFT")
    fy606 = pick(f, "us-gaap", "RevenueFromContractWithCustomerExcludingAssessedTax",
                 "2015-07-01", "2016-06-30")
    fy605 = [r for r in rows_for(f, "us-gaap", "SalesRevenueNet")
             if r["start"] == "2015-07-01" and r["end"] == "2016-06-30"]
    q3_605 = [r for r in rows_for(f, "us-gaap", "SalesRevenueNet")
              if r["start"] == "2015-07-01" and r["end"] == "2016-03-31"]
    chk(fy606 is not None and fy606["val"] == 91_154_000_000,
        f"FY2016 매출 91,154 (ASC 606 재작성) accn={fy606['accn']} form={fy606['form']} fy={fy606['fy']}",
        "FY2018 10-K 에서 온 값이다 — FY2016 당시 공시가 아니다")
    chk(bool(fy605) and fy605[0]["val"] == 85_320_000_000,
        f"같은 기간 원래 공시 85,320 (ASC 605) accn={fy605[0]['accn']}",
        f"두 세대 차 {91_154_000_000 - 85_320_000_000:,} ({(91_154_000_000/85_320_000_000-1)*100:.2f}%)")
    if fy606 and fy605 and q3_605:
        bad = fy606["val"] - q3_605[0]["val"]
        good = fy605[0]["val"] - q3_605[0]["val"]
        chk(abs(bad - good) == 5_834_000_000,
            f"세대를 섞은 Q4 복원 {bad:,} 대 같은 세대 복원 {good:,}",
            f"오차 {bad-good:,} ({(bad/good-1)*100:.1f}%). 9개월 누계는 ASC 605 이고 FY 는 ASC 606 이다")

    # ---------------------------------------------------------------- [5]
    print()
    print("[5] TSM FY2025 — EDGAR 원문 우회 건 (TSM-EDGAR-29)")
    import datetime as dt

    def months_elapsed(end: dt.date, asof: dt.date) -> int:
        """**완결된 개월 수**다. 달 번호 차로 세면 한 달 더 나온다(2024-12-31→2026-09-02 은 20 이지 21 이 아니다)."""
        m = (asof.year - end.year) * 12 + (asof.month - end.month)
        return m - (1 if asof.day < end.day else 0)

    asof = dt.date(2026, 9, 2)
    chk(months_elapsed(dt.date(2024, 12, 31), asof) == 20, "FY2024 였다면 20개월 경과")
    chk(months_elapsed(dt.date(2025, 12, 31), asof) == 8, "FY2025 는 8개월 경과 — 12개월 단축")

    tsm25 = plain(blob("TSM_20F_FY2025"))
    i = tsm25.find("NET REVENUE")
    row = tsm25[i:i + 200]
    chk("2,161,735.8 $ 2,894,307.7 $ 3,809,054.3" in row.replace("  ", " "),
        "**표는 2023·2024·2025 오름차순이고 최신은 셋째 NT$ 열이다**",
        "그 오른쪽이 US$ (Note 3) 열이다. 열을 잘못 읽으면 FY2023 을 최신으로 등록하게 된다")
    for label, needle, twd, usd_filed in (
            ("매출 NET REVENUE", "NET REVENUE", 3_809_054_300_000, 121_423_500_000),
            ("영업이익 INCOME FROM OPERATIONS", "INCOME FROM OPERATIONS", 1_936_091_700_000, 61_717_900_000),
            ("순이익 NET INCOME", "NET INCOME ", 1_695_124_900_000, 54_036_500_000)):
        j = tsm25.find(needle)
        seg = tsm25[j:j + 220]
        got = f"{twd / 1e6:,.1f}"
        chk(got in seg, f"FY2025 {label} NT${got}백만", seg[:140].strip())
        chk(f"{usd_filed / 1e6:,.1f}" in seg, f"  같은 행 US$ 열 {usd_filed/1e6:,.1f}백만 (Note 3, 31.37)")
    chk(abs(1_936_091_700_000 / 3_809_054_300_000 - 0.508287) < 1e-5,
        "FY2025 영업이익률 50.829%",
        "지시서 초판의 1,936,092 는 MD&A 반올림이고 감사 손익계산서 본문은 1,936,091.7 이다(정정 반영)")
    chk(abs(3_809_054_300_000 / 121_423_500_000 - 31.37) < 1e-3,
        "선언 환율 31.37 이 표에서 역산된다")
    chk("31.37" in tsm25 and "H.10 statistical release" in tsm25,
        "20-F 가 환율 출처로 연준 H.10 을 명시한다")
    for label, cur, prior in (("FY2024 두 경로 검산 매출", 2_894_307_700_000, None),
                              ("FY2024 두 경로 검산 영업이익", 1_322_053_000_000, None)):
        f = facts("TSM")
        tag = "Revenue" if "매출" in label else "ProfitLossFromOperatingActivities"
        cf = pick(f, "ifrs-full", tag, "2024-01-01", "2024-12-31", "TWD")
        chk(cf["val"] == cur, f"{label} — companyfacts {cf['val']:,} 대 원문 {cur:,}",
            "우회 조건 (2) 충족. 원문 파싱 경로가 companyfacts 와 정확히 일치한다")
    g25 = 3_809_054_300_000 / 2_894_307_700_000 - 1
    chk(p3_band(g25) == 0, f"FY2025 성장률 {g25*100:+.2f}% — P3 밴드 {p3_band(g25):+d}",
        "지시서 예상 +31.61% 와 일치")
    mc = json.loads((ROOT / "scorecard" / "runs" / "ai-scorecard-2026-09-obsreg"
                     / "observations.json").read_text(encoding="utf-8"))["items"]
    got = {(o["company_id"], o["metric"]): o["value"] for o in mc if o["value"] is not None}
    m, n = got[("tsmc", "market_cap")], got[("tsmc", "net_cash")]
    per = m / (1_695_124_900_000 / 31.37)
    evs = (m - n) / (3_809_054_300_000 / 31.37)
    chk(p1_band(per) == -1 and p2_band(evs) == -1,
        f"**FY2025 로 P1·P2 가 각각 한 칸 올라온다** — PER {per:.1f}({p1_band(per):+d}) · EV/S {evs:.2f}({p2_band(evs):+d})",
        "FY2024 였다면 PER 60.9(-2) · EV/S 23.5(-2) 였다. 분모가 한 해 새것이 되며 움직였다")

    # ---------------------------------------------------------------- [6]
    print()
    print("[6] net_income_ttm · revenue_ttm_prior (F6-SPEC-18 수집기)")
    print(f"  {'회사':11} {'net_income_ttm':>20} {'revenue_ttm_prior':>20} {'basis':14}")
    for cid in sorted(spec18):
        m = spec18[cid]["metrics"]
        ni = (m.get("net_income_ttm") or {}).get("value")
        rp = (m.get("revenue_ttm_prior") or {}).get("value")
        pb = (m.get("revenue_ttm_prior") or {}).get("period_basis")
        print(f"  {cid:11} {ni:>20,} {rp:>20,} {pb:14}")
    chk(all((spec18[c]['metrics'].get('net_income_ttm') or {}).get('value') is not None for c in spec18),
        "12개사 모두 net_income_ttm 이 수집돼 있다")

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
