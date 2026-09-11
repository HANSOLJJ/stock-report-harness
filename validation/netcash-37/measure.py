# net_cash 실측 — 보존 SEC companyfacts 와 보존 20-F 원문에서 현금·차입금·리스부채를 직접 뽑는다 (네트워크 없음)
"""**받은 값을 정답으로 쓰지 않는다.** MCAP-36(커밋 0eb113d)이 준 차입금을 보존 원자료에서 다시 뽑는다.

여기서 계산한 값을 `verify_netcash.py` 와 `apply_netcash.py` 가 같이 쓴다. 한 곳에서만 계산해야
검증기와 등록기가 다른 수를 볼 수 없다.

## 왜 개념 목록을 고정하지 않는가

고정 목록으로 돌렸더니 12개사 중 4개사가 MCAP-36 과 갈렸다. 원인은 전부 내 목록이었다 —
microsoft 의 금융리스는 `FinanceLeaseLiability` 한 줄이고 spacex 의 차입은
`LongTermDebtAndCapitalLeaseObligationsIncludingCurrentMaturities` 다. 회사마다 태그가 다르다.
그래서 **각 사가 실제로 쓴 개념**을 기준일 시점 사실에서 찾아 쓰고, 합계 태그와 구성요소 태그가
같이 있으면 합계 쪽 하나만 센다(이중계상 방지).
"""
from __future__ import annotations

import html
import json
import re
import subprocess
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
RAW = ROOT / "validation" / "f6-avail-15" / "_raw"

TICKER = {"tsmc": "TSM", "alibaba": "BABA", "apple": "AAPL", "microsoft": "MSFT", "amazon": "AMZN",
          "nvidia": "NVDA", "spacex-xai": "SPCX", "tesla": "TSLA", "palantir": "PLTR",
          "meta": "META", "oracle": "ORCL", "alphabet": "GOOGL"}

# 차입금 개념. 그룹 안은 **우선순위**(합계 태그가 있으면 구성요소를 다시 세지 않는다),
# 그룹 사이는 **합산**이다. MCAP-36 은 ST 그룹도 우선순위로 둬서 amazon 의 ShortTermBorrowings 를
# 놓쳤다 — LongTermDebtCurrent 가 먼저 걸리면 그 뒤를 보지 않는다. 여기서는 별도 그룹으로 뺀다.
DEBT_GROUPS: list[list[str]] = [
    ["LongTermDebtAndCapitalLeaseObligationsIncludingCurrentMaturities",
     "DebtLongtermAndShorttermCombinedAmount"],          # 총액 직접 태깅
    ["LongTermDebtNoncurrent", "LongTermNotesAndLoans", "LongTermDebt", "ConvertibleDebtNoncurrent"],
    ["LongTermLoansFromBank"],
    ["LongTermDebtCurrent", "DebtCurrent", "NotesPayableCurrent"],
    ["ShortTermBorrowings"],
    ["CommercialPaper"],
]
# 총액 태그가 걸리면 나머지 그룹은 그 안에 이미 들어 있다.
DEBT_TOTAL_TAGS = set(DEBT_GROUPS[0])
OP_LEASE = ["OperatingLeaseLiability", ("OperatingLeaseLiabilityNoncurrent", "OperatingLeaseLiabilityCurrent")]
FIN_LEASE = ["FinanceLeaseLiability", ("FinanceLeaseLiabilityNoncurrent", "FinanceLeaseLiabilityCurrent")]


def facts(cid: str) -> dict[str, Any]:
    return json.loads((RAW / f"{TICKER[cid]}.companyfacts.json").read_text(encoding="utf-8"))["facts"]


def at(f: dict[str, Any], tag: str, end: str, unit: str) -> float | None:
    """기준일 시점(instant) 사실. **결측은 None 이고 0 과 구분한다** — 0 으로 접으면 조용히 틀린다."""
    node = f.get("us-gaap", {}).get(tag)
    if not node:
        return None
    best = None
    for row in node["units"].get(unit, []):
        if row.get("end") == end and not row.get("start"):
            if best is None or str(row.get("filed", "")) >= str(best.get("filed", "")):
                best = row
    return None if best is None else float(best["val"])


def _lease(f: dict[str, Any], spec: list[Any], end: str, unit: str) -> tuple[float | None, list[str]]:
    for item in spec:
        if isinstance(item, str):
            v = at(f, item, end, unit)
            if v is not None:
                return v, [item]
        else:
            parts = [(t, at(f, t, end, unit)) for t in item]
            if any(v is not None for _, v in parts):
                return sum(v or 0 for _, v in parts), [t for t, v in parts if v is not None]
    return None, []


def measure_us(cid: str, end: str, unit: str = "USD") -> dict[str, Any]:
    """보존 companyfacts 로 차입금·리스부채를 센다."""
    f = facts(cid)
    used: list[str] = []
    debt: float | None = None
    total_hit = False
    for group in DEBT_GROUPS:
        if total_hit and not (set(group) & DEBT_TOTAL_TAGS):
            continue
        for tag in group:
            v = at(f, tag, end, unit)
            if v is None:
                continue
            debt = (debt or 0) + v
            used.append(tag)
            if tag in DEBT_TOTAL_TAGS:
                total_hit = True
            break
    op, op_tags = _lease(f, OP_LEASE, end, unit)
    fin, fin_tags = _lease(f, FIN_LEASE, end, unit)

    # 총액 태그가 자본리스를 이미 포함하면 금융리스를 다시 더하지 않는다.
    fin_in_debt = None
    if total_hit and fin is not None:
        bare = at(f, "LongTermDebt", end, unit)
        if bare is not None and debt is not None and abs((debt - bare) - fin) < 1.0:
            fin_in_debt = {"reason": f"{used[0]} {debt:,.0f} - LongTermDebt {bare:,.0f} = {fin:,.0f} "
                                     f"= FinanceLeaseLiability. 총액 태그가 자본리스를 이미 포함한다.",
                           "excluded": fin}
            fin = None
    lease = None if (op is None and fin is None) else (op or 0) + (fin or 0)
    return {"debt_ex_lease": debt, "debt_concepts": used,
            "operating_lease": op, "operating_lease_concepts": op_tags,
            "finance_lease": fin, "finance_lease_concepts": fin_tags,
            "finance_lease_already_in_debt": fin_in_debt,
            "lease_total": lease,
            "debt_incl_lease": None if (debt is None or lease is None) else debt + lease}


# 현금 + **시장성 있는** 유가증권. 설계진행 2026-09-11 결정.
# EV 조정은 팔아서 기업 청구권을 상환할 수 있는 자산만 대상이다. 지분법 투자와 비상장 지분은
# 전략적·영업적 보유라 유동성이 없고, 제한 현금은 애초에 우리 돈이 아니다.
CASH_TAG = "CashAndCashEquivalentsAtCarryingValue"
SEC_CURRENT = ["MarketableSecuritiesCurrent", "ShortTermInvestments", "DebtSecuritiesCurrent",
               "AvailableForSaleSecuritiesDebtSecuritiesCurrent"]
SEC_NONCURRENT = ["MarketableSecuritiesNoncurrent", "DebtSecuritiesNoncurrent",
                  "AvailableForSaleSecuritiesDebtSecuritiesNoncurrent"]
# **넣지 않는 개념.** 이름이 비슷해 잘못 들어오기 쉬운 것들을 명시해 둔다.
EXCLUDED_TAGS = {
    "EquityMethodInvestments": "지분법 투자 — 영업적 보유",
    "EquitySecuritiesWithoutReadilyDeterminableFairValueAmount": "비상장 지분 — 시장가가 없다",
    "LongTermInvestments": "지분 투자가 섞인 합계 줄",
    "OtherLongTermInvestments": "지분 투자가 섞인 합계 줄",
    "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents": "제한 현금 포함 합계",
    "RestrictedCashCurrent": "제한 현금",
    "AvailableForSaleSecuritiesDebtMaturitiesWithinOneYearFairValue":
        "**만기 버킷 공시다.** 현금성자산으로 분류된 증권까지 포함하므로 현금에 더하면 이중계상된다",
}


def cash_marketable_us(cid: str, end: str, unit: str = "USD") -> dict[str, Any]:
    """현금 + 시장성 유가증권(대차대조표 줄만). **합계·만기 버킷 공시를 쓰지 않는다.**

    C-13 이 nvidia 에 만기 1년 이내 버킷(41,000)을 현금에 더해 현금성자산 안의 증권 6,857 을
    이중계상했고, spacex 에는 증권 6,487 을 빼고 제한 현금 830 을 넣었다. 둘 다 대차대조표
    줄로 돌아오면 사라진다.
    """
    f = facts(cid)
    parts: list[tuple[str, float]] = []
    cash = at(f, CASH_TAG, end, unit)
    if cash is not None:
        parts.append((CASH_TAG, cash))
    for group in (SEC_CURRENT, SEC_NONCURRENT):
        for tag in group:
            v = at(f, tag, end, unit)
            if v is not None:
                parts.append((tag, v))
                break
    excluded = {t: at(f, t, end, unit) for t in EXCLUDED_TAGS}
    return {"total": sum(v for _, v in parts) if parts else None,
            "concepts": [{"tag": f"us-gaap:{t}", "value": v} for t, v in parts],
            "excluded_present": {f"us-gaap:{t}": {"value": v, "why": EXCLUDED_TAGS[t]}
                                 for t, v in excluded.items() if v}}


# ------------------------------------------------------------------ 보존 20-F 원문 (ADR 2사)
BLOBS = {"tsmc": ("f14a235", "validation/tsm-edgar-29/_raw/tsm-20251231.htm"),
         "alibaba": ("3cf9799", "validation/offb-24/_raw/baba-20260331.htm")}


def blob_text(cid: str) -> list[str]:
    commit, path = BLOBS[cid]
    out = subprocess.run(["git", "show", f"{commit}:{path}"], capture_output=True, cwd=ROOT)
    if out.returncode != 0:
        raise SystemExit(f"git show {commit}:{path} 실패")
    t = out.stdout.decode("utf-8", "replace")
    t = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", t)
    t = re.sub(r"(?is)</t[dh]>", " | ", t)
    t = re.sub(r"(?is)</tr>", "\n", t)
    t = re.sub(r"(?s)<[^>]+>", " ", t)
    t = re.sub(r"[ \t\u00a0]+", " ", html.unescape(t))
    return [l.strip() for l in t.split("\n")]


NUM = re.compile(r"^\(?\s*-?[\d,]+(?:\.\d+)?\s*\)?$")


def _num(cell: str) -> float | None:
    """`$ 1,234.5` · `( 986,625.2 )` 를 수로. **괄호는 음수다** — 벗기고 부호를 살린다."""
    c = cell.replace("$", "").strip()
    neg = c.startswith("(") and c.endswith(")")
    c = c.strip("()").strip()
    if not NUM.match(c):
        return None
    v = float(c.replace(",", ""))
    return -v if neg else v


ADR_FX = {"tsmc": 31.37, "alibaba": 6.8980}     # 발행사 20-F 선언 편의환산 환율 (F6-REG-28 과 동일)


def find_row(cid: str, label: str, values: list[float]) -> str:
    """보존 20-F 원문에서 `label` 뒤에 `values` 가 **그 순서로** 나오는 줄을 찾는다.

    표를 파싱해 열을 세지 않는다. TSM 은 같은 라벨이 유동·비유동에 두 번 나오고 결측 칸이 `-` 라서
    열 위치가 행마다 다르다. 대신 **내가 읽은 값이 문면에 그 순서로 있는지**를 증명한다. 값 하나가
    틀리면 줄을 못 찾아 즉시 터진다.

    반환은 찾은 줄(근거로 보고서에 싣는다). 못 찾으면 예외.
    """
    # 숫자 경계를 막는다. `100.2` 를 찾을 때 `1,100.25` 안에 걸리면 안 된다.
    edge_l, edge_r = r"(?<![\d,.])", r"(?![\d,.])"
    pat = re.compile(edge_l + (edge_r + r".*?" + edge_l).join(
        re.escape(f"{v:,.1f}" if cid == "tsmc" else f"{v:,.0f}") for v in values) + edge_r)
    for line in _searchable(cid):
        if line.startswith(label) and pat.search(line):
            return line.strip()
    raise SystemExit(f"{cid} 20-F 에 '{label}' + {values} 줄이 없음 — 전사(轉寫)가 원문과 다르다")


_FOLD_CACHE: dict[str, list[str]] = {}


def _searchable(cid: str) -> list[str]:
    """검색 대상 줄. TSM 은 한 줄에 한 행이 오지만 **BABA 는 셀이 줄마다 쪼개져 나온다.**

    BABA 쪽은 라벨 뒤에 이어지는 숫자들을 한 줄로 접어서 같은 방식으로 찾을 수 있게 만든다.
    """
    if cid != "alibaba":
        return blob_text(cid)
    if cid not in _FOLD_CACHE:
        folded, label, nums = [], None, []
        for raw in blob_text(cid):
            cell = raw.strip(" |")
            if not cell:
                continue
            if _num(cell) is not None:
                nums.append(cell)
            elif re.match(r"^[A-Za-z]", cell):
                if label:
                    folded.append(f"{label} | " + " | ".join(nums))
                label, nums = cell, []
        if label:
            folded.append(f"{label} | " + " | ".join(nums))
        _FOLD_CACHE[cid] = folded
    return _FOLD_CACHE[cid]


def check_fx(cid: str, native: float, usd: float, what: str) -> None:
    """현지통화 값을 발행사 선언 환율로 나눈 것이 20-F 의 USD 칸과 맞는지 본다. **열 대응의 증명이다.**"""
    got = native / ADR_FX[cid]
    if abs(got - usd) > max(abs(usd) * 2e-4, 0.6):
        raise SystemExit(f"{cid} {what}: {native:,} / {ADR_FX[cid]} = {got:,.1f} 인데 원문 USD 칸은 {usd:,} —"
                         f" 열 대응이 틀렸다")


def tsm_measure() -> dict[str, Any]:
    """TSMC 2025-12-31 (NT$ 백만). 보존 companyfacts 에 이 시점 금액 사실이 **0건**이라 20-F 를 읽는다.

    증권은 **주석까지 내려가야** 시장성 여부가 갈린다. 대차대조표 줄로만 보면
    `FVTPL 비유동 15,032.1` 안에 전환우선주 13,608.8 과 SAFE 125.8 이, `FVOCI 비유동 8,797.2` 에
    비공개거래 지분이 통째로 들어 있다. 셋 다 비상장 지분이라 EV 조정 대상이 아니다.
    """
    rows: list[tuple[str, str, float, float | None]] = [
        # (구분, 라벨, NT$백만, 원문 US$백만 칸 — 없으면 None)
        ("cash",  "Cash and cash equivalents", 2767856.4, 88232.6),
        # 주석 8 FVTPL — 비유동 15,032.1 중 시장성은 뮤추얼펀드뿐이다
        ("sec",   "Mutual funds", 1297.5, None),
        ("skip",  "Convertible preferred stocks", 13608.8, None),
        ("skip",  "Simple agreement for future equity", 125.8, None),
        ("skip",  "Forward exchange contracts", 100.2, None),
        # 주석 9 FVOCI — 유동 175,692.7 = 채무상품 171,736.6 + 상장주식 3,956.1 (전부 시장성)
        ("sec",   "Financial assets at fair value through other comprehensive income", 175692.7, 5600.7),
        ("skip",  "Non-publicly traded equity investments", 8797.2, None),
        # 주석 10 상각후원가 — 회사채·국공채. 전부 시장성
        ("sec",   "Financial assets at amortized cost", 124945.5, 3983.0),
        ("sec",   "Financial assets at amortized cost", 110507.8, 3522.7),
        ("sec",   "Other financial assets", 59702.9, 1903.2),
        ("debt",  "Bonds payable", 856227.5, 27294.5),
        ("debt",  "Long-term bank loans", 39834.5, 1269.8),
        ("debt",  "Long-term liabilities - current portion", 136925.7, 4364.9),
        ("lease", "Lease liabilities", 31595.0, 1007.2),
        ("lease", "Current portion (classified under accrued expenses and other current liabilities)",
                  3833.0, None),
    ]
    found, buckets = [], {"cash": 0.0, "sec": 0.0, "skip": 0.0, "debt": 0.0, "lease": 0.0}
    for kind, label, native, usd in rows:
        vals = [native] if usd is None else [native, usd]
        found.append({"kind": kind, "label": label, "ntd_million": native, "usd_million": usd,
                      "line": find_row("tsmc", label, vals)})
        if usd is not None:
            check_fx("tsmc", native, usd, label)
        buckets[kind] += native
    cash_all = buckets["cash"] + buckets["sec"]
    net = cash_all - buckets["debt"] - buckets["lease"]
    return {"currency": "TWD", "unit_scale": 1e6, "fx": ADR_FX["tsmc"], "rows": found,
            "cash_all_securities": cash_all, "excluded_nonmarketable": buckets["skip"],
            "debt_ex_lease": buckets["debt"], "lease_total": buckets["lease"],
            "debt_incl_lease": buckets["debt"] + buckets["lease"],
            "net_cash_native_million": net, "net_cash_usd": net * 1e6 / ADR_FX["tsmc"]}


def baba_measure() -> dict[str, Any]:
    """알리바바 2026-03-31 (RMB 백만). **주석 11 이 시장성 여부를 그대로 갈라 준다.**

    대차대조표의 `Equity securities and other investments` 두 줄(30,054 + 449,942 = 479,996)은
    주석 11 에서 상장주식 100,594 · 비상장 130,447 · 채무증권및대출 10,880 · 기타 자금운용
    238,075 로 쪼개진다. 앞의 100,594 와 238,075 만 시장성이다.
    """
    debt = [("Current bank borrowings", 28224.0, 4092.0),
            ("Non-current bank borrowings", 47450.0, 6879.0),
            ("Non-current unsecured senior notes", 117485.0, 17032.0),
            ("Non-current convertible unsecured senior notes", 55861.0, 8098.0),
            ("Non-current exchangeable bonds", 10976.0, 1591.0)]
    marketable = [("Cash and cash equivalents", 131530.0, 19068.0),
                  ("Short-term investments", 155310.0, 22515.0),
                  ("Listed equity securities", 100594.0, None),
                  ("Other treasury investments", 238075.0, None)]
    excluded = [("Investments in privately held companies", 130447.0, None,
                 "비상장 지분 — 시장가가 없고 팔아서 청구권을 상환할 수 없다"),
                ("Debt securities and loan investments", 10880.0, None,
                 "채무증권과 **대출**이 한 줄에 섞여 있다. 대출은 시장성이 없는데 20-F 가 나누지 "
                 "않는다. 시장성을 증명하지 못한 줄은 넣지 않는다"),
                ("Investments in equity method investees", 206803.0, 29980.0,
                 "지분법 투자 — 영업적 보유"),
                ("Restricted cash and escrow receivables", 42038.0, 6094.0,
                 "제한 현금. 주석에 따르면 35,965 가 판매자 구매자보호기금 예치금이라 **우리 돈이 "
                 "아니다.** 유가증권이 아니라 현금이지만 같은 논리로 제외한다")]
    rows = []
    for kind, group in (("debt", debt), ("marketable", marketable)):
        for label, native, usd in group:
            vals = [native] if usd is None else [native, usd]
            rows.append({"kind": kind, "label": label, "rmb_million": native, "usd_million": usd,
                         "line": find_row("alibaba", label, vals)})
            if usd is not None:
                check_fx("alibaba", native, usd, label)
    for label, native, usd, why in excluded:
        vals = [native] if usd is None else [native, usd]
        rows.append({"kind": "excluded", "label": label, "rmb_million": native, "usd_million": usd,
                     "why": why, "line": find_row("alibaba", label, vals)})
        if usd is not None:
            check_fx("alibaba", native, usd, label)
    lease = at(facts("alibaba"), "OperatingLeaseLiability", "2026-03-31", "CNY")
    d = sum(v for _, v, _ in debt)
    lease_m = (lease or 0) / 1e6
    cash_all = sum(v for _, v, _ in marketable)
    net = cash_all - d - lease_m
    return {"currency": "CNY", "unit_scale": 1e6, "fx": ADR_FX["alibaba"], "rows": rows,
            "debt_ex_lease": d, "lease_total": lease_m, "debt_incl_lease": d + lease_m,
            "cash_all_securities": cash_all,
            "excluded_nonmarketable": sum(v for _, v, _, _ in excluded),
            "net_cash_native_million": net, "net_cash_usd": net * 1e6 / ADR_FX["alibaba"]}
