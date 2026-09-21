# TSM-EDGAR-29B: 조건 2 — FY2024 를 companyfacts 와 EDGAR 원문 두 경로로 검산한다.
# 두 값이 모두 일치할 때만 FY2025 를 채택한다. 다르면 채택하지 않고 차이를 보고한다.
import datetime as dt
import io
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "..", "f6-fx-16-2026-09-10", "raw")
R4 = os.path.join(RAW, "edgar-R4-FY2025-income-statement.htm")
CF = os.path.join(RAW, "sec-TSM-companyfacts.json")
NBSP = "\u00a0"

# 열 순서는 머리글 행에서 읽는다(가정하지 않는다).
COLS = None


def strip_tags(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s)).replace(NBSP, " ").strip()


def cell_number(raw):
    t = raw.replace(NBSP, " ").strip()
    neg = "(" in t
    t = t.replace(",", "").replace("$", "").replace("(", "").replace(")", "").strip()
    if re.fullmatch(r"-?\d+(?:\.\d+)?", t):
        v = float(t)
        return -v if neg else v
    return None


def parse(html):
    """각 행을 (개념, 라벨, 숫자열) 로 묶는다. 개념은 행 안의 defref_ 에서 가져온다."""
    rows = []
    for r in re.findall(r"(?is)<tr[^>]*>(.*?)</tr>", html):
        refs = re.findall(r"defref_([A-Za-z0-9_-]+)", r)
        cells = [strip_tags(c) for c in re.findall(r"(?is)<t[dh][^>]*>(.*?)</t[dh]>", r)]
        if not cells:
            continue
        nums = [n for n in (cell_number(c) for c in cells[1:]) if n is not None]
        concept = refs[0].replace("_", ":", 1) if refs else None
        rows.append({"concept": concept, "label": cells[0], "nums": nums, "cells": cells[1:]})
    return rows


html = io.open(R4, encoding="utf-8").read()
rows = parse(html)

# --- 열 머리글을 실제로 읽어 순서를 확정한다 ---
hdr = None
for r in rows:
    if r["label"].startswith("Dec.") or any(c.startswith("Dec.") for c in r["cells"]):
        hdr = [r["label"]] + r["cells"]
        break
COLS = []
for h in hdr:
    m = re.match(r"(\w{3})\.\s+(\d+),\s+(\d{4})\s+([A-Z]{3})", h)
    COLS.append({"header": h, "year": int(m.group(3)) if m else None,
                 "currency": m.group(4) if m else None})
print("열 순서(원문 머리글에서 읽음)")
for i, c in enumerate(COLS):
    print("   col%d  year=%s  currency=%s   | %s" % (i, c["year"], c["currency"], c["header"]))


def col_of(year, cur):
    for i, c in enumerate(COLS):
        if c["year"] == year and c["currency"] == cur:
            return i
    return None


def row_by_concept(concept):
    for r in rows:
        if r["concept"] == concept and r["nums"]:
            return r
    return None


TARGETS = {
    "revenue": "ifrs-full:RevenueFromContractsWithCustomers",
    "operating": "ifrs-full:ProfitLossFromOperatingActivities",
}

# --- companyfacts 쪽 FY2024 ---
cf = json.load(io.open(CF, encoding="utf-8"))
facts = cf["facts"]


def cf_annual(concept, end_year):
    tax, cname = concept.split(":")
    body = facts.get(tax, {}).get(cname)
    if not body:
        return None, "개념 없음"
    hits = []
    for u, entries in (body.get("units") or {}).items():
        if u != "TWD":
            continue
        for e in entries:
            s, en = e.get("start"), e.get("end")
            if not s or not en:
                continue
            d = (dt.date.fromisoformat(en) - dt.date.fromisoformat(s)).days
            if 350 <= d <= 380 and en.startswith(str(end_year)):
                hits.append(e)
    if not hits:
        return None, "TWD 연간 관측 없음"
    hits.sort(key=lambda e: e.get("filed") or "")
    return hits[-1], None


print("\n조건 2 — FY2024 두 경로 검산 (단위: TWD)")
print("-" * 104)
print("%-11s %-22s %-22s %-10s %s" % ("항목", "EDGAR 원문 20-F", "companyfacts", "차이", "판정"))
gate = {}
c24 = col_of(2024, "TWD")
for key, concept in TARGETS.items():
    r = row_by_concept(concept)
    edgar = r["nums"][c24] * 1e6 if r else None      # 표시 단위는 백만
    e, err = cf_annual(concept, 2024)
    cfv = e["val"] if e else None
    diff = (edgar - cfv) if (edgar is not None and cfv is not None) else None
    ok = diff is not None and abs(diff) < 1.0
    gate[key] = {"concept": concept, "label": r["label"] if r else None,
                 "edgar_fy2024": edgar, "companyfacts_fy2024": cfv,
                 "cf_period": ("%s~%s" % (e["start"], e["end"])) if e else None,
                 "cf_accn": e.get("accn") if e else None,
                 "cf_form": e.get("form") if e else None,
                 "cf_filed": e.get("filed") if e else None,
                 "diff": diff, "match": ok, "cf_error": err}
    print("%-11s %-22s %-22s %-10s %s" % (
        key,
        "{:,.0f}".format(edgar) if edgar is not None else "없음",
        "{:,.0f}".format(cfv) if cfv is not None else ("없음(%s)" % err),
        "{:,.0f}".format(diff) if diff is not None else "-",
        "일치" if ok else "불일치"))

passed = all(v["match"] for v in gate.values())
print("\n관문: %s" % ("통과 — FY2025 채택 진행" if passed else "실패 — FY2025 를 뽑지 않고 차이를 보고"))

out = {"gate_fy2024": gate, "gate_passed": passed, "columns": COLS}

if passed:
    c25t, c25u, c23 = col_of(2025, "TWD"), col_of(2025, "USD"), col_of(2023, "TWD")
    fy25 = {}
    for key, concept in TARGETS.items():
        r = row_by_concept(concept)
        fy25[key] = {
            "concept": concept, "statement_label": r["label"],
            "fy2025_twd": r["nums"][c25t] * 1e6,
            "fy2025_usd_convenience": r["nums"][c25u] * 1e6,
            "fy2024_twd": r["nums"][c24] * 1e6,
            "fy2023_twd": r["nums"][c23] * 1e6,
        }
    rev, op = fy25["revenue"], fy25["operating"]
    fy25["operating_margin_fy2025"] = op["fy2025_twd"] / rev["fy2025_twd"]
    fy25["operating_margin_fy2024"] = op["fy2024_twd"] / rev["fy2024_twd"]
    fy25["implied_rate_from_revenue"] = rev["fy2025_twd"] / rev["fy2025_usd_convenience"]
    fy25["implied_rate_from_operating"] = op["fy2025_twd"] / op["fy2025_usd_convenience"]
    out["fy2025"] = fy25
    print("\nFY2025 (2025-01-01 ~ 2025-12-31, 현지통화 TWD)")
    print("-" * 104)
    for key in ("revenue", "operating"):
        v = fy25[key]
        print("  %-10s %-42s %22s TWD" % (key, v["statement_label"][:42],
                                          "{:,.0f}".format(v["fy2025_twd"])))
        print("  %-10s %-42s %22s (편의환산 USD)" % ("", v["concept"],
                                                "{:,.0f}".format(v["fy2025_usd_convenience"])))
    print("\n  영업이익률 FY2025 = %.4f%%   (FY2024 = %.4f%%)" % (
        fy25["operating_margin_fy2025"] * 100, fy25["operating_margin_fy2024"] * 100))
    print("  내재 환산율: 매출 %.4f / 영업손익 %.4f  (NT$ per US$1)" % (
        fy25["implied_rate_from_revenue"], fy25["implied_rate_from_operating"]))

io.open(os.path.join(HERE, "tsm-fy2025-extract.json"), "w", encoding="utf-8").write(
    json.dumps(out, ensure_ascii=False, indent=1))
print("\nsaved tsm-fy2025-extract.json")
