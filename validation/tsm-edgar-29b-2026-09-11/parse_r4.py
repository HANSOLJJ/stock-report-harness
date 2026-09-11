# TSM-EDGAR-29B: EDGAR 렌더링 손익계산서(R4.htm)에서 연도별 열을 파싱한다.
# 조건 2 를 먼저 — FY2024 를 companyfacts 와 대조하고, 일치할 때만 FY2025 를 채택한다.
import io
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "..", "f6-fx-16-2026-09-10", "raw")
R4 = os.path.join(RAW, "edgar-R4-FY2025-income-statement.htm")

NBSP = " "


def strip_tags(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s)).replace(NBSP, " ").strip()


def cell_number(raw):
    """표 셀 문자열을 수치로. 괄호는 음수, 숫자가 아니면 None."""
    t = raw.replace(NBSP, " ").strip()
    neg = "(" in t
    t = t.replace(",", "").replace("$", "").replace("(", "").replace(")", "").strip()
    if re.fullmatch(r"-?\d+(?:\.\d+)?", t):
        v = float(t)
        return -v if neg else v
    return None


def parse_rows(html):
    """R4 표를 행 단위로 파싱한다. 각 행 = 줄 이름 + 숫자 열들 + 원문 셀."""
    out = []
    for r in re.findall(r"(?is)<tr[^>]*>(.*?)</tr>", html):
        cells = [strip_tags(c) for c in
                 re.findall(r"(?is)<t[dh][^>]*>(.*?)</t[dh]>", r)]
        if not cells:
            continue
        label, rest = cells[0], cells[1:]
        nums = [n for n in (cell_number(c) for c in rest) if n is not None]
        out.append({"label": label, "cells": rest, "nums": nums})
    return out


html = io.open(R4, encoding="utf-8").read()
rows = parse_rows(html)

# 표 제목과 열 머리글
flat = strip_tags(html)
print("문서 머리:", flat[:260])
print()
print("머리글 행 (숫자 없는 상단 행):")
for r in rows[:6]:
    if not r["nums"]:
        print("   label=%r cells=%r" % (r["label"], r["cells"]))
print()

print("전체 행 목록 (label | 숫자열)")
print("-" * 110)
for r in rows:
    if r["nums"]:
        print("  %-46s %s" % (r["label"][:46], r["nums"]))
    elif r["label"]:
        print("  %-46s" % r["label"][:46])

io.open(os.path.join(HERE, "r4-parsed.json"), "w", encoding="utf-8").write(
    json.dumps(rows, ensure_ascii=False, indent=1))
print("\nsaved r4-parsed.json (%d rows)" % len(rows))
