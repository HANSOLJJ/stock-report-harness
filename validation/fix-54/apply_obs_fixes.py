# FIX-54 1단계 S5: 3차 리뷰 B 관측 정정 — spacex net_cash 부분 합 표시 · P1 분자 모회사 귀속 · apple TTM 시작일 · TTM 성분 accession (점수 무영향)
"""보존 원자료만 읽는다(validation/f6-avail-15/_raw companyfacts · f14a235 tsm-20251231.htm · 3cf9799 spcx 원문). 신규 조회 없음.

- FC-03 spacex-xai.net_cash.nc37: 운용리스 비유동분이 2026-06-30 에 없어 유동 344M 만 뺐다. 값은 두고 **완전 합산이 아니라고** 표시한다.
  S-1/A 2025-12-31 비유동 1,136M 은 다른 시점이라 대신 넣지 않는다. 규칙 net_cash evidence 에 부분 리스 기준 일치를 적는다.
- FC-04 P1 분자: 모회사 귀속 순이익으로 정의한다. tsmc 는 연결 전체(1,695,124.9)에서 모회사 귀속(1,697,604.0 NT$백만)으로 바꾼다.
  나머지 11개사는 이미 귀속분(us-gaap NetIncomeLoss = Attributable to Parent)이라 범위만 적는다. 소비자: calc_f6_params P1.
- FC-05 apple: 복원 Q4 가 누계 종료일에 시작해 하루가 겹쳤다. TTM 2025-06-28 → 06-29, prior 2024-06-29 → 06-30.
  (지시서는 prior 를 `2024-06-30 → 06-29` 로 적었으나 보존 companyfacts 의 전기 누계 종료가 2024-06-29 라 복원 Q4 는 06-30 에 시작한다.)
- FC-06 TTM 복원 관측 전부: 성분마다 (개념·기간·값) 이 일치하는 보존 사실의 accession 을 basis.component_accessions 에 적고 산술을 검산한다.

재실행해도 같은 결과가 나온다. 산술이 맞지 않거나 성분을 못 찾으면 쓰지 않고 멈춘다. 파일은 LF 로 쓴다.
"""
from __future__ import annotations

import json
import re
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "validation" / "f6-spec-18"))

import collect_ttm  # noqa: E402
from scorecard.rules import load_rules  # noqa: E402
from scorecard.schema import validate_observations, validate_rules, validate_run  # noqa: E402

RUN_ID = "ai-scorecard-2026-09-obsreg"
RUN = ROOT / "scorecard" / "runs" / RUN_ID
RULES = ROOT / "scorecard" / "rules" / "v1.7.json"
DATE = "2026-09-15"
MARKER = "FIX-54 1단계"
TICKER = {v: k for k, v in collect_ttm.TICKER_TO_ID.items()}
PERIODIC_FORMS = {"10-Q", "10-K", "10-Q/A", "10-K/A", "20-F", "20-F/A", "S-1", "S-1/A"}
US = ["alphabet", "amazon", "apple", "meta", "microsoft", "nvidia", "oracle", "palantir", "tesla", "spacex-xai"]


def load(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def dump(p: Path, d: dict) -> None:
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def days(s: str, e: str) -> int:
    return (date.fromisoformat(e) - date.fromisoformat(s)).days


class Facts:
    def __init__(self, cid: str) -> None:
        self.cid = cid
        self.doc = collect_ttm.load_facts(TICKER[cid])

    def rows(self, tag: str) -> list[dict]:
        node = self.doc["facts"].get("us-gaap", {}).get(tag) or {}
        return [r for r in node.get("units", {}).get("USD", []) if r.get("start") and r.get("end")]

    def find(self, tags: list[str], *, end: str, val: float | None = None, start: str | None = None,
             span: tuple[int, int] | None = None, role: str) -> dict:
        """(개념, 기간, 값) 이 맞는 사실. 같은 사실을 여러 제출본이 실으면 **처음 보고한 정기 보고서**를 성분의 accession 으로 적는다."""
        hits = []
        for tag in tags:
            for r in self.rows(tag):
                if r["end"] != end or (start and r["start"] != start):
                    continue
                if span and not span[0] <= days(r["start"], r["end"]) <= span[1]:
                    continue
                if val is not None and r["val"] != val:
                    continue
                hits.append((tag, r))
        periods = {(t, r["start"], r["end"], r["val"]) for t, r in hits}
        if not hits or len({(p[1], p[2], p[3]) for p in periods}) != 1:
            raise SystemExit(f"{self.cid} {role}: 성분을 하나로 특정하지 못함 tags={tags} end={end} val={val} start={start} → {sorted(periods)[:4]}")
        # 성분의 출처는 **그 기간을 처음 보고한 정기 보고서**다. 뒤 보고서의 비교 기간 재수록·위임장(DEF 14A) 재인용은 also_filed_in 에 둔다.
        # 값을 맞춰 찾으므로 재작성된 값이면 그 재작성 보고서가 처음 보고한 것이 된다.
        periodic = [h for h in hits if h[1].get("form") in PERIODIC_FORMS] or hits
        tag, best = min(periodic, key=lambda h: str(h[1].get("filed", "")))
        same_period = [r for t, r in hits]
        later = [r for r in self.rows(tag) if r["start"] == best["start"] and r["end"] == best["end"]
                 and str(r.get("filed", "")) > str(best.get("filed", "")) and r["val"] != best["val"]]
        out = {"role": role, "tag": f"us-gaap:{tag}", "start": best["start"], "end": best["end"], "val": best["val"],
               "accession": best.get("accn"), "form": best.get("form"), "filed": best.get("filed")}
        others = sorted({r.get("accn") for r in same_period} - {best.get("accn")})
        if others:
            out["also_filed_in"] = others
        if later:
            out["restated_later"] = [{"accession": r.get("accn"), "val": r["val"], "filed": r.get("filed")} for r in later]
        return out


def ytd_formula(fx: Facts, tags: list[str], *, curr_end: str, fy_end: str, prior_end: str,
                curr: float | None, fy: float | None, prior: float | None) -> list[dict]:
    fy_c = fx.find(tags, end=fy_end, val=fy, span=(350, 380), role="prior_fy")
    prior_c = fx.find(tags, end=prior_end, val=prior, start=fy_c["start"], role="prior_ytd")
    curr_rows = [r for t in tags for r in fx.rows(t) if r["end"] == curr_end and 1 <= days(fy_end, r["start"]) <= 7
                 and (curr is None or r["val"] == curr)]
    if not curr_rows:
        raise SystemExit(f"{fx.cid}: 당기 누계 성분 없음 end={curr_end}")
    curr_c = fx.find(tags, end=curr_end, val=curr_rows[0]["val"], start=curr_rows[0]["start"], role="curr_ytd")
    return [curr_c, fy_c, prior_c]


def check_sum(parts: list[dict], signs: list[int], expected: float, where: str) -> dict:
    got = sum(s * p["val"] for s, p in zip(signs, parts))
    if abs(got - expected) > 0.5:
        raise SystemExit(f"{where}: 성분 산술 {got} ≠ 관측 {expected}")
    return {"formula": " ".join(("+ " if s > 0 else "− ") + p["role"] for s, p in zip(signs, parts)).lstrip("+ "),
            "sum": got, "matches_value": True}


def attach(o: dict, items: list[dict], arithmetic: dict, how: str) -> None:
    o["basis"]["component_accessions"] = {
        "rule": "policies.f6.ttm_window.restatement_generation — 각 성분의 accession 을 관측 근거에 보존한다(accession_role: 감사 근거)",
        "resolved_by": f"validation/fix-54/apply_obs_fixes.py ({MARKER}, 3차 리뷰 B FC-06) — {how}. 같은 사실을 여러 제출본이 실으면 그 기간을 처음 보고한 정기 보고서를 적고 나머지는 also_filed_in 에 둔다",
        "items": items,
        "arithmetic": arithmetic,
    }


# ------------------------------------------------------------------ FC-06 성분 accession

def components_quarter_sum(o: dict, fx: Facts, rules) -> None:
    metric = o["metric"]
    base = "revenue_ttm" if metric == "revenue_ttm_prior" else metric
    tags_q = collect_ttm.METRIC_TAGS[base]
    unit = collect_ttm.pick_unit(fx.doc, tags_q, None)
    rows, mix = collect_ttm.coalesce_series(fx.doc, tags_q, unit)
    series, _ = collect_ttm.quarter_series(rows, rules, mix)
    win = collect_ttm.trailing(series, offset=4 if metric == "revenue_ttm_prior" else 0)
    if win is None or (win["start"], win["end"]) != (o["period"]["start"], o["period"]["end"]) or win["value"] != o["value"]:
        raise SystemExit(f"{o['observation_id']}: 수집기 창 {win and (win['start'], win['end'], win['value'])} ≠ 관측 {o['period']} {o['value']}")
    tags = [t for tax, t in tags_q if tax == "us-gaap"]
    items = []
    for q in collect_ttm.trailing(series, offset=4 if metric == "revenue_ttm_prior" else 0)["quarters"]:
        item = next(r for r in series if r["end"] == q["end"] and r["val"] == q["val"])
        if item["kind"] == "Q":
            items.append(fx.find(tags, end=item["end"], val=item["val"], start=item["start"], role="quarter"))
            continue
        fy_row = next(r for r in rows if r["kind"] == "FY" and r["end"] == item["end"])
        inside = [r for r in rows if r["kind"] == "Q" and fy_row["start"] <= r["start"] and r["end"] < fy_row["end"]]
        fy_c = fx.find(tags, end=fy_row["end"], val=fy_row["val"], start=fy_row["start"], role="fy")
        q_cs = [fx.find(tags, end=r["end"], val=r["val"], start=r["start"], role="quarter_in_fy") for r in inside]
        chk = check_sum([fy_c] + q_cs, [1, -1, -1, -1], item["val"], o["observation_id"] + " Q4")
        items.append({"role": "q4_derived", "start": item["start"], "end": item["end"], "val": item["val"],
                      "derived_from": [fy_c] + q_cs, "arithmetic": chk})
    attach(o, items, check_sum(items, [1] * len(items), o["value"], o["observation_id"]),
           "수집기(collect_ttm) 창의 네 분기. 복원 Q4 는 FY − 세 분기의 성분을 derived_from 에 둔다")


def components_ttm_formula(o: dict, fx: Facts) -> None:
    c = o["basis"]["components"]
    pre = "revenue" if o["metric"] == "revenue_ttm" else "operating_income"
    tags = ["RevenueFromContractWithCustomerExcludingAssessedTax", "Revenues"] if pre == "revenue" else ["OperatingIncomeLoss"]
    if c["method"].startswith("ttm_formula"):
        parts = ytd_formula(fx, tags, curr_end=c["anchor_curr"], fy_end=c["fy_prior"], prior_end=c["anchor_prior"],
                            curr=c[f"{pre}_curr_ytd"], fy=c[f"{pre}_prior_fy"], prior=c[f"{pre}_prior_ytd"])
        attach(o, parts, check_sum(parts, [1, 1, -1], o["value"], o["observation_id"]), "당기 누계 + 전기 FY − 전기 동일 누계")
    elif c["method"] == "direct_fy_is_ttm":
        fy_c = fx.find(tags, end=c["fy_end"], val=c[f"{pre}_fy"], span=(350, 380), role="fy")
        ytd_c = fx.find(tags, end=c["q3_ytd_end"], val=c[f"{pre}_q3_ytd"], start=fy_c["start"], role="q3_ytd(교차 확인)")
        attach(o, [fy_c, ytd_c], check_sum([fy_c], [1], o["value"], o["observation_id"]), "공시 FY 가 TTM 과 같은 기간. 3분기 누계는 복원 Q4 교차 확인용")
    else:
        raise SystemExit(f"{o['observation_id']}: 모르는 method {c['method']}")


def components_pretax(o: dict, fx: Facts) -> None:
    b = o["basis"]
    how = b["how_reconstructed"]
    concept = b["concept"]
    if m := re.match(r"당기누계 (\S+) \+ 전기연간 (\S+) − 전기동일누계 (\S+)", how):
        parts = ytd_formula(fx, [concept], curr_end=m.group(1), fy_end=m.group(2), prior_end=m.group(3), curr=None, fy=None, prior=None)
        attach(o, parts, check_sum(parts, [1, 1, -1], o["value"], o["observation_id"]), "당기 누계 + 전기 FY − 전기 동일 누계")
    elif m := re.match(r"단일 12개월 (\S+)~(\S+)", how):
        one = fx.find([concept], end=m.group(2), start=m.group(1), role="direct_12m")
        attach(o, [one], check_sum([one], [1], o["value"], o["observation_id"]), "단일 12개월 사실")
    elif "Domestic" in concept:
        p = o["period"]
        dom = fx.find(["IncomeLossFromContinuingOperationsBeforeIncomeTaxesDomestic"], end=p["end"], start=p["start"], role="domestic_12m")
        fgn = fx.find(["IncomeLossFromContinuingOperationsBeforeIncomeTaxesForeign"], end=p["end"], start=p["start"], role="foreign_12m")
        attach(o, [dom, fgn], check_sum([dom, fgn], [1, 1], o["value"], o["observation_id"]), "국내 + 해외 12개월 사실")
    else:
        raise SystemExit(f"{o['observation_id']}: 모르는 재구성 {how}")


def components_fcf(o: dict, fx: Facts) -> None:
    b = o["basis"]
    end = o["period"]["end"]
    items, total = [], []
    for side, sign in (("ocf", 1), ("capex", -1)):
        tag = b[f"{side}_concept"].split(":", 1)[1]
        comp = b["components"][f"{side}_components"]
        formula = b[f"{side}_formula"]
        if formula == "direct_fy_filed_is_ttm":
            one = fx.find([tag], end=end, val=comp["direct_fy"], span=(350, 380), role=f"{side}_fy")
            parts, signs = [one], [1]
        elif formula == "direct_ttm_disclosed":
            one = fx.find([tag], end=end, val=comp["direct_ttm_disclosed"], span=(350, 380), role=f"{side}_ttm_disclosed")
            parts, signs = [one], [1]
        elif fx.cid == "spacex-xai":
            # FY2025 는 S-1/A 감사 현금흐름표에만 있고 companyfacts 에 없다 — 원문 행을 성분으로 적는다.
            fy = SPCX_S1A_FY[side]
            if fy["val"] != comp["prior_fy_12m"]:
                raise SystemExit(f"{o['observation_id']} {side}: S-1/A FY {fy['val']} ≠ basis {comp['prior_fy_12m']}")
            curr_c = fx.find([tag], end=end, val=comp["curr_ytd_6m"], start="2026-01-01", role="curr_ytd")
            prior_c = fx.find([tag], end="2025-06-30", val=comp["prior_ytd_6m"], start="2025-01-01", role="prior_ytd")
            parts, signs = [curr_c, dict(fy, role="prior_fy"), prior_c], [1, 1, -1]
            for p in parts:
                p["role"] = f"{side}_{p['role']}"
        else:
            ytd_key = next(k for k in comp if k.startswith("curr_ytd"))
            prior_key = next(k for k in comp if k.startswith("prior_ytd"))
            fy_rows = [r for r in fx.rows(tag) if r["val"] == comp["prior_fy_12m"] and 350 <= days(r["start"], r["end"]) <= 380 and r["end"] < end]
            if not fy_rows:
                raise SystemExit(f"{o['observation_id']} {side}: 전기 FY 성분 없음")
            fy_end = max(r["end"] for r in fy_rows)
            prior_rows = [r for r in fx.rows(tag) if r["val"] == comp[prior_key] and r["end"] < fy_end and 150 <= days(r["start"], r["end"]) <= 290]
            if not prior_rows:
                raise SystemExit(f"{o['observation_id']} {side}: 전기 누계 성분 없음")
            parts = ytd_formula(fx, [tag], curr_end=end, fy_end=fy_end, prior_end=max(r["end"] for r in prior_rows),
                                curr=comp[ytd_key], fy=comp["prior_fy_12m"], prior=comp[prior_key])
            for p in parts:
                p["role"] = f"{side}_{p['role']}"
            signs = [1, 1, -1]
        items += parts
        total.append((sign, sum(s * p["val"] for s, p in zip(signs, parts))))
    got = sum(s * v for s, v in total)
    if abs(got - o["value"]) > 0.5:
        raise SystemExit(f"{o['observation_id']}: OCF − CapEx {got} ≠ 관측 {o['value']}")
    attach(o, items, {"formula": "ocf − capex (각 쪽은 role 접두어의 성분 산식)", "sum": got, "matches_value": True},
           "OCF·CapEx 각각의 누계·FY 성분")


SPCX_S1A_FY = {
    side: {"tag": "S-1/A 연결현금흐름표(companyfacts 미등재)", "start": "2025-01-01", "end": "2025-12-31", "val": val,
           "accession": "0001628280-26-040364", "form": "S-1/A", "filed": "2026-06-03",
           "quote": quote, "location": "3cf9799:validation/offb-24/_raw/spcx_s1a_20260603.htm — CONSOLIDATED STATEMENTS OF CASH FLOWS"}
    for side, val, quote in (
        ("ocf", 6_785_000_000, "Net cash provided by operating activities ........................ $ 6,785 $ 5,776 $ 4,520"),
        ("capex", 20_737_000_000, "Purchases of property, plant, and equipment (related party of $666, $171, and $11 …) … (20,737) (11,163) (4,415)"),
    )
}


# ------------------------------------------------------------------ FC-03 · FC-04 · FC-05

SPCX_COMPLETENESS = {
    "complete_sum": False,
    "what": ("**리스부채가 완전 합산이 아니다.** 2026-06-30 운용리스는 유동 344M(10-Q `Accrued expenses and other current liabilities` 표의 "
             "`Operating lease liabilities, current 344`)만 있고 비유동분 개념(`OperatingLeaseLiabilityNoncurrent`)과 합계 개념이 이 기준일에 없다. "
             "10-Q 는 기타 비유동부채를 나누지 않는다."),
    "not_substituted": ("S-1/A 감사 주석의 2025-12-31 `Operating lease liabilities, net of current 1,136`(3cf9799:validation/offb-24/_raw/spcx_s1a_20260603.htm)은 "
                        "다른 시점이라 **대신 빼지 않았다.** 비유동분이 0 이라는 근거도 아니다."),
    "direction": "비유동 운용리스만큼 순현금이 **과대**다. 크기는 확인하지 못했다.",
    "why_value_kept": ("listed_newly 트랙은 P2 를 계산하지 않아 이 값이 점수에 들어가는 자리가 없다(results F6 parameters 에 P2 없음). "
                       "지우지 않고 한계를 적어 둔다. palantir 는 같은 결함(유동분 결측)으로 관측 등록 자체를 하지 않았다 — 두 회사의 처리가 다르다는 사실도 여기 남긴다."),
    "legacy_match_caveat": ("basis.why_this_match_matters 의 legacy 60,300 일치는 이 부분 합 기준이다. 비유동분이 0 이 아니면 그 일치는 성립하지 않는다 — "
                            "legacy 도 같은 공백을 가졌을 가능성이 있으나 확인할 수 없다."),
    "code_fix": "validation/netcash-37/measure.py _lease 가 구성요소 결측을 0 으로 합산하던 것을 고쳤다 — 이제 합계를 만들지 않고 빠진 개념을 돌려준다.",
    "review": "3차 리뷰 B FC-03",
    "recorded_at": DATE,
}

PARTIAL_LEASE_BASIS = {
    "companies": ["palantir", "spacex-xai"],
    "note": (f"[{MARKER} FC-03] 두 회사의 일치는 **리스 구성요소 하나가 빠진 부분 합 기준**이다 — palantir 는 운용리스 유동분, spacex-xai 는 비유동분이 "
             "기준일에 없다. 완전 합산 기준의 일치로 읽지 않는다. spacex_note 의 `가장 강한 증거` 도 이 한정 아래서만 성립한다."),
}

TSMC_PARENT = 1_697_604.0e6
TSMC_NCI = -2_479.1e6
TSMC_CONSOLIDATED = 1_695_124.9e6


def fix_tsmc_ni(o: dict) -> bool:
    b = o["basis"]
    if b.get("original_value") == TSMC_PARENT:
        return False
    rate = b["fx_rate"]
    o["value"] = round(TSMC_PARENT / rate, 3)
    b["original_value"] = TSMC_PARENT
    b["cross_check_filed_usd"] = {"filed": 54_115_500_000, "recomputed": o["value"],
                                  "rel_diff": abs(o["value"] - 54_115_500_000) / 54_115_500_000}
    mcap = 2_150_000_000_000
    b["band_sensitivity"]["used"]["value"] = round(mcap / o["value"], 3)
    alt = b["band_sensitivity"]["alternative"]
    alt["value"] = round(mcap / (TSMC_PARENT / alt["rate"]), 3)
    b["ownership_correction"] = {
        "corrected_at": DATE, "task": f"{MARKER} S5 (3차 리뷰 B FC-04)",
        "was": {"original_value": TSMC_CONSOLIDATED, "value_usd": round(TSMC_CONSOLIDATED / rate, 3), "scope": "consolidated_incl_nci",
                "p1": round(mcap / (TSMC_CONSOLIDATED / rate), 6)},
        "is": {"original_value": TSMC_PARENT, "value_usd": o["value"], "scope": "parent_attributable", "p1": round(mcap / o["value"], 6)},
        "quote": ("F-6 `NET INCOME (LOSS) ATTRIBUTABLE TO: Shareholders of the parent $ 851,740.0 $ 1,158,380.2 $ 1,697,604.0 $ 54,115.5 "
                  "Non-controlling interests ( 712.3 ) ( 856.3 ) ( 2,479.1 ) ( 79.0 ) $ 851,027.7 $ 1,157,523.9 $ 1,695,124.9 $ 54,036.5` · "
                  "주석 27 EPS `Net income available to common shareholders of the parent (in millions) … $ 1,697,604.0`"),
        "location": "f14a235:validation/tsm-edgar-29/_raw/tsm-20251231.htm — 연결손익계산서(F-6) 귀속 구분 · 주석 27 EARNINGS PER SHARE",
        "why": "시총·EPS 는 모회사 보통주 범위다. 같은 범위의 순이익으로 나눠야 PER 이다. 비지배지분 손실(−2,479.1)이 있어 연결 전체가 귀속분보다 작았다.",
        "score_impact": "P1 39.788 → 39.730, 밴드 25~45 그대로(-1).",
    }
    o["raw"] = "FY2025 모회사 귀속 순이익 NT$1,697,604.0백만 (연결 1,695,124.9 · 비지배 −2,479.1)"
    return True


def ownership(o: dict) -> dict:
    cid = o["company_id"]
    if cid == "tsmc":
        return {"scope": "parent_attributable", "evidence": "F-6 `Shareholders of the parent 1,697,604.0` — basis.ownership_correction"}
    if cid == "alibaba":
        return {"scope": "parent_attributable",
                "evidence": "us-gaap NetIncomeLoss(companyfacts label `Net Income (Loss) Attributable to Parent`) 103,592,000,000 CNY — 20-F 0001193125-26-231755"}
    tag_note = "us-gaap NetIncomeLoss — companyfacts label `Net Income (Loss) Attributable to Parent`"
    nci = {"oracle", "palantir", "tesla"}
    return {"scope": "parent_attributable",
            "evidence": tag_note + ("; 이 회사는 ProfitLoss·NetIncomeLossAttributableToNoncontrollingInterest 도 태깅해 연결 전체와 귀속분이 갈린다 — 귀속분을 썼다"
                                    if cid in nci else "; 비지배지분 개념 태깅 없음")}


APPLE_FIX = {"apple.revenue_ttm.f6reg28": ("2025-06-28", "2025-06-29"), "apple.operating_income_ttm.f6reg28": ("2025-06-28", "2025-06-29"),
             "apple.net_income_ttm.f6reg28": ("2025-06-28", "2025-06-29"), "apple.pretax_income_ttm.nonop44": ("2025-06-28", "2025-06-29"),
             "apple.revenue_ttm_prior.f6reg28": ("2024-06-29", "2024-06-30")}


def fix_apple(o: dict) -> bool:
    was, new = APPLE_FIX[o["observation_id"]]
    if o["period"]["start"] == new:
        return False
    assert o["period"]["start"] == was, o["period"]
    o["period"]["start"] = new
    if o.get("raw"):
        o["raw"] = o["raw"].replace(was, new)
    o["basis"]["period_correction"] = {
        "corrected_at": DATE, "task": f"{MARKER} S5 (3차 리뷰 B FC-05)", "was": was, "is": new,
        "why": (f"복원 Q4 는 직전 누계 종료일({(date.fromisoformat(new) - timedelta(days=1)).isoformat()}) **다음 날** 시작한다. 시작일을 누계 종료일로 적어 하루가 겹쳤다. "
                "값은 같다 — 기간 표기만 틀렸다. 원인은 validation/f6-spec-18/collect_ttm.py 복원 Q4 시작일이라 그 줄도 고쳤다."),
        "same_company_fcf": "apple.fcf_ttm.cashfcf35 는 이미 2025-06-29 시작이었다 — F6·F9 창이 이제 같다.",
    }
    return True


def main() -> int:
    rules = load_rules("v1.7")
    doc = load(RUN / "observations.json")
    by = {o["observation_id"]: o for o in doc["items"]}
    changed: list[str] = []

    # FC-03
    nc = by["spacex-xai.net_cash.nc37"]
    if nc["basis"].get("completeness") != SPCX_COMPLETENESS:
        nc["basis"]["completeness"] = SPCX_COMPLETENESS
        nc["raw"] = "현금+시장성증권 100.0B − 차입 39.4B − 리스 0.3B(운용리스 유동분만 — 비유동 결측) = 60.3B"
        changed.append("spacex-xai.net_cash.nc37 completeness")

    # FC-05 (FC-06 보다 먼저 — 수집기 창과 기간을 맞춘다)
    for oid in APPLE_FIX:
        if fix_apple(by[oid]):
            changed.append(f"{oid} period")

    # FC-04
    if fix_tsmc_ni(by["tsmc.net_income_ttm.f6reg28"]):
        changed.append("tsmc.net_income_ttm.f6reg28 모회사 귀속")
    for o in doc["items"]:
        if o["metric"] == "net_income_ttm" and o["status"] == "verified" and o.get("value") is not None:
            own = ownership(o)
            if o["basis"].get("ownership_scope") != own["scope"] or o["basis"].get("ownership_evidence") != own["evidence"]:
                o["basis"]["ownership_scope"] = own["scope"]
                o["basis"]["ownership_evidence"] = own["evidence"]
                changed.append(f"{o['observation_id']} ownership_scope")

    # FC-06
    facts = {cid: Facts(cid) for cid in US}
    n = 0
    for o in doc["items"]:
        oid, cid = o["observation_id"], o["company_id"]
        if cid not in US or o["status"] != "verified" or o.get("value") is None or not o.get("period"):
            continue
        b = o["basis"] or {}
        before = json.dumps(b.get("component_accessions"), ensure_ascii=False, sort_keys=True)
        if oid.endswith(".f6reg28") and b.get("period_basis") == "ttm" and cid != "spacex-xai":
            if o["metric"] in ("net_income_ttm", "revenue_ttm_prior"):
                components_quarter_sum(o, facts[cid], rules)
            elif o["metric"] in ("revenue_ttm", "operating_income_ttm"):
                components_ttm_formula(o, facts[cid])
            else:
                continue
        elif oid.endswith(".nonop44"):
            components_pretax(o, facts[cid])
        elif oid.endswith("fcf_ttm.cashfcf35"):
            components_fcf(o, facts[cid])
        else:
            continue
        n += 1
        if json.dumps(o["basis"].get("component_accessions"), ensure_ascii=False, sort_keys=True) != before:
            changed.append(f"{oid} component_accessions")

    validate_observations(doc, {c["company_id"]: c for c in load(ROOT / "scorecard" / "companies.json")["companies"]}, RUN_ID)
    dump(RUN / "observations.json", doc)

    # 규칙 — P1 분자 범위 · net_cash 부분 리스 기준 일치
    r = load(RULES)
    p1 = r["policies"]["f6"]["parameters"]["P1"]
    scope = {"net_income_ttm": "parent_attributable"}
    if p1.get("input_scope") != scope:
        p1["input_scope"] = scope
        p1["input_scope_note"] = (f"[{MARKER} FC-04] P1 분자는 **모회사 귀속 순이익**이다 — 시총·EPS 가 모회사 보통주 범위라서다. 연결 전체(비지배 포함)를 쓰면 "
                                  "범위가 어긋난다. calc_f6_params 가 관측 basis.ownership_scope 를 읽어 다르면 P1 을 만들지 않는다.")
        changed.append("rules P1 input_scope")
    matched = r["policies"]["f6"]["net_cash"]["evidence"]["matched"]
    if matched.get("partial_lease_basis") != PARTIAL_LEASE_BASIS:
        matched["partial_lease_basis"] = PARTIAL_LEASE_BASIS
        changed.append("rules net_cash evidence.matched.partial_lease_basis")
    validate_rules(r)
    dump(RULES, r)
    run = load(RUN / "run.json")
    run["rule_hash"] = load_rules("v1.7").hash
    validate_run(run, RUN_ID)
    dump(RUN / "run.json", run)

    print(f"TTM 복원 관측 {n}건 성분 대조")
    print("변경:", len(changed))
    for c in changed:
        print("  " + c)
    print("rule_hash", run["rule_hash"][:12])
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    sys.exit(main())
