# FIX-53 3단계: 리뷰 A 2차 반영 — 관측 설명 정정 · spacex-xai 세전이익 등록 · 판단 근거란 정정 · nvidia.F2 긴장 (점수 무영향)
"""원자료는 전부 보존 사본에서 다시 확인했다(validation/fix-53c/verify-sources-output.txt 참조).

재실행해도 같은 결과가 나온다. 파일은 LF 로 쓴다(.gitattributes eol=lf).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard.rules import load_rules  # noqa: E402
from scorecard.schema import load_json_strict, validate_judgments, validate_observations, validate_rules, validate_run  # noqa: E402

RUN_ID = "ai-scorecard-2026-09-obsreg"
RUN = ROOT / "scorecard" / "runs" / RUN_ID
RULES = ROOT / "scorecard" / "rules" / "v1.7.json"
DATE = "2026-09-15"
MARK = "[FIX-53 3단계]"


def load(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def dump(p: Path, d: dict) -> None:
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def once(text: str | None, addition: str) -> str:
    text = text or ""
    return text if addition in text else (text + (" | " if text else "") + addition)


# ================================================================== 관측
def alibaba_contracted(o: dict) -> None:
    b = o["basis"]
    old_note = o["note"]
    if "note_superseded" not in b:
        b["note_superseded"] = {"text": old_note, "superseded_at": DATE,
                                "why": "면제 선언의 범위를 실제 문면보다 넓게 적었다(리뷰 A 2차 high)."}
    b["exemption_scope"] = ("20-F `Practical expedients and exemptions` 문단의 면제는 **두 갈래뿐**이다 — (1) 원래 예상 기간 1년 "
                            "이하 계약, (2) right-to-invoice 금액으로 수익을 인식하는 계약. 원문: `The Company applies the practical "
                            "expedient to not disclose the value of unsatisfied performance obligations for contracts with an "
                            "original expected duration of one year or less and contracts for which revenue is recognized at the "
                            "amount to which the Company has the right to invoice for services performed`. **1년 초과 계약 전부가 "
                            "여기 든다는 근거는 없다.**")
    b["absence_by_full_text_search"] = ("문서 전문 검색으로 RPO 수치 부재를 확인했다 — `unsatisfied performance obligation` 은 위 "
                                        "면제 문장 1건뿐, `remaining performance obligation`·`backlog` 0건. 잔여 수행의무 금액은 "
                                        "20-F 어디에도 없다(3cf9799:validation/offb-24/_raw/baba-20260331.htm).")
    b["classification_basis"] = ("`not_disclosed_confirmed` 는 **면제 선언(두 갈래) + 전문 검색으로 확인한 수치 부재** 위에 선다. "
                                 "C-16 강등 한 칸이 이 분류에 걸리므로 근거 문장을 이 둘로 한정한다.")
    o["note"] = ("OBS-REG-25 · " + MARK + " **확인된 미공시.** 20-F 가 두 갈래(1년 이하 계약 · right-to-invoice 계약) 면제를 선언하고, "
                 "문서 전문 검색에서 잔여 수행의무 금액이 없다. 1년 초과 계약이 전부 면제에 든다는 근거는 없으므로 '찾아도 없을 것이 "
                 "선언돼 있다' 가 아니라 '선언된 면제 + 전문에서 수치 부재 확인' 이다. C-16 대상.")


def spacex_pretax(obs: dict) -> None:
    oid = "spacex-xai.pretax_income_ttm.fix53"
    obs["items"] = [o for o in obs["items"] if o["observation_id"] != oid]
    obs["items"].append({
        "observation_id": oid, "company_id": "spacex-xai", "metric": "pretax_income_ttm",
        "value": -7623000000.0, "unit": "USD", "as_of": "2026-06-30", "observed_at": DATE,
        "period": {"start": "2025-07-01", "end": "2026-06-30"}, "kind": "derived",
        "source_id": "SRC-SEC-SPCX-10Q-2026Q2", "status": "verified",
        "basis": {
            "period_basis": "ttm", "method": "FY2025 + H1'2026 - H1'2025 (net_income_ttm·operating_income_ttm 과 같은 방식)",
            "components": {"fy2025_s1a": -4219000000, "h1_2026_10q": -4788000000, "h1_2025_10q": -1384000000},
            "sources": {
                "fy2025": ("S-1/A 0001628280-26-040364 감사 연결손익계산서 `Income (loss) before income taxes (4,219)` — "
                           "3cf9799:validation/offb-24/_raw/spcx_s1a_20260603.htm"),
                "half_years": ("10-Q 0001628280-26-052535 companyfacts "
                               "`IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest`"),
            },
            "cross_check_tax": {"fy2025_s1a": 718000000, "h1_2026": 29000000, "h1_2025": 152000000, "tax_ttm": 595000000,
                                "closes_to_net_income_ttm": "-7,623 − 595 = -8,218 = spacex-xai.net_income_ttm.f6reg28"},
            "why_now": ("run.json 이 `세전이익을 복원하지 못해` 라고 적었는데 세전이익은 공시돼 있었다(리뷰 A 2차). 복원 가능해서 "
                        "등록한다. nonop_share 는 세전이익이 음수라 부호 규약이 서지 않아 여전히 산출하지 않는다."),
        },
        "raw": "TTM 세전손실 -7,623M", "note": "FIX-53 3단계. S-1/A FY2025 + 10-Q 반기 복원. 순이익과 세금으로 닫힌다.",
    })
    ns = next(o for o in obs["items"] if o["observation_id"] == "spacex-xai.nonop_share.v15")
    ns["status"] = "incompatible_basis"
    ns["basis"] = {"why": ("세전이익(-7,623M, spacex-xai.pretax_income_ttm.fix53)이 음수라 `(세전 − 영업이익) / 세전` 의 **부호 규약이 "
                           "서지 않는다.** 산출하지 않는다. 전에는 `not_disclosed` 였으나 세전이익은 공시돼 있어 미공시가 아니다."),
                   "status_correction": {"from": "not_disclosed", "to": "incompatible_basis", "at": DATE, "task": "FIX-53 3단계"}}
    ns["note"] = "FIX-53 3단계. 세전이익 음수 — 부호 규약 미정이라 산출 안 함. P4 강등은 short_history 한 칸으로 이미 걸려 점수 불변."


def spacex_cash(o: dict) -> None:
    b = o["basis"]
    pw = b["preserved_wider_definitions"]
    comp = pw["components"]
    comp["short_term_marketable_securities"] = 6487000000
    comp["sti_concept"] = "us-gaap:MarketableSecuritiesCurrent"
    comp["liquid_cash_buffer"] = 100009000000
    comp["cash_plus_restricted"] = 94352000000
    comp["total_cash_and_all_securities"] = 100009000000
    comp["total_note"] = ("유동성 버퍼 + 비유동 증권. SPCX companyfacts 에 2026-06-30 `MarketableSecuritiesNoncurrent` 이 없어 버퍼와 같다. "
                          "이전 값 94,352M 은 현금 93,522 + 제한현금 830(RestrictedCashCurrent 210 + Noncurrent 620)이라 필드 정의와 "
                          "달랐다 — cash_plus_restricted 로 옮겼다.")
    pw["liquid_cash_buffer"] = 100009000000.0
    pw["total_including_noncurrent"] = 100009000000
    pw["correction"] = {"at": DATE, "task": "FIX-53 3단계 (리뷰 A 2차)",
                        "what": ("시장성 증권 6,487M(us-gaap:MarketableSecuritiesCurrent, 10-Q 0001628280-26-052535)을 0 으로 적었다. "
                                 "같은 실행 spacex-xai.net_cash.nc37 은 이 값을 넣는다. 등록된 cash 93,522M 은 순수 현금이라 맞다.")}
    lc = b["legacy_comparison"]
    lc["legacy_equaled"] = "유동성 버퍼"
    lc["diff_vs_buffer_pct"] = round((100000 - 100009) / 100009 * 100, 4)
    lc["equaled_correction"] = "이전 판정 `어느 쪽도 아님` 은 버퍼를 93,522M 으로 잘못 둔 결과였다. legacy $100.0B 는 버퍼 100,009M 과 0.009% 차."


LEGACY_SPLIT_OLD = "7개사는 유동성 버퍼, 3개사는 비유동 증권까지 포함한 총계, 2개사는 어느 쪽도 아니다"
LEGACY_SPLIT_NEW = ("8개사는 유동성 버퍼, 3개사는 비유동 증권까지 포함한 총계, 1개사(nvidia)는 어느 쪽도 아니다 "
                    "[FIX-53 3단계 정정: 전에는 7/3/2 — spacex-xai 버퍼를 시장성 증권 누락으로 잘못 계산했다]")


def fix_legacy_split(obs: dict) -> int:
    n = 0
    for o in obs["items"]:
        lc = ((o.get("basis") or {}).get("legacy_comparison") or {})
        if LEGACY_SPLIT_OLD in (lc.get("note") or ""):
            lc["note"] = lc["note"].replace(LEGACY_SPLIT_OLD, LEGACY_SPLIT_NEW)
            n += 1
    return n


def anthropic_straddle(o: dict) -> None:
    b = o["basis"]
    old = b["straddle_note"]
    if "straddle_note_superseded" not in b:
        b["straddle_note_superseded"] = {"text": old, "superseded_at": DATE,
                                         "why": "FIX-52 S2 이후 사실이 아니다 — arr_growth 가 run_rate 로 불충족이라 보정이 어떤 시나리오에서도 붙지 않는다."}
    b["straddle_note"] = ("**모순 구간이 보정 임계 0.50 을 가로지르지만 지금은 점수를 가르지 않는다.** 세 시나리오의 자본효율이 0.41~0.72 이고 "
                          "그중 하나(65B 포함 가정)만 임계 미달이다. 그러나 FIX-52 S2 로 arr_growth 가 kind=run_rate 라 불충족이고 보정은 "
                          "require_all 이라 **세 시나리오 모두 anthropic F6 = -4** 다. 진짜 ARR(kind=actual)이 들어오면 이 갈림이 다시 "
                          "점수를 가를 수 있다. 값을 고르지 않았다.")


def oracle_net_cash(o: dict) -> None:
    ex = o["basis"]["components"]["excluded_nonmarketable_present"]
    item = ex["us-gaap:EquitySecuritiesWithoutReadilyDeterminableFairValueAmount"]
    item["why"] = ("**이중 태깅으로 보인다 — `비상장 지분` 설명은 확인되지 않는다.** 포함 쪽 "
                   "`us-gaap:AvailableForSaleSecuritiesDebtSecuritiesCurrent` 605,000,000 과 값·접수번호(0001193125-26-277521, 10-K)·"
                   "직전 회계연도 값(2025-05-31 둘 다 417,000,000)이 같다. 같은 대차대조표 줄에 두 개념이 붙은 것으로 보이며 원문 "
                   "대차대조표가 보존돼 있지 않아 어느 개념이 맞는지 확정하지 못한다. net_cash 는 605 를 포함 쪽으로 한 번만 더하므로 "
                   "값 -135,538M 은 그대로다.")
    item["why_superseded"] = "비상장 지분 — 시장가가 없다 (FIX-53 3단계 전 설명)"


def spacex_revenue(o: dict) -> None:
    b = o["basis"]
    b["period_label"] = "**2026Q2 단일 분기(2026-04-01~2026-06-30) — TTM 아님.** metric 이름은 revenue_ttm 이지만 값은 분기다."
    b["same_company_other_revenue"] = ("같은 회사 spacex-xai.operating_margin_ttm.f6reg28 의 분모는 TTM 매출 23,044M(FY2025 18,674 + "
                                       "H1'26 12,508 − H1'25 8,138)이다. 관측 id 는 다른 참조가 있어 바꾸지 않았다.")
    o["note"] = once(o.get("note"), f"{MARK} **분기값(2026Q2) — TTM 아님.** P3 분기 YoY 전용.")
    o["raw"] = "2026Q2 분기 매출 7,814M (TTM 아님)"


def palantir_lease(o: dict) -> None:
    b = o["basis"]
    b["why_not_unverified"] = ("보존 PLTR companyfacts 에서 end=2026-06-30 인 사실 **148건**(시점형 52건·52개 태그, 기간형 96건)을 "
                               "전수 확인했다. 유동 리스부채를 가리키는 시점 사실이 없다 — `OperatingLeaseLiabilityNoncurrent` 211,400,000 은 "
                               "있고 `OperatingLeaseLiabilityCurrent`·상위 합계 `OperatingLeaseLiability` 의 최근값은 2025-12-31 이다.")
    b["count_correction"] = {"at": DATE, "was": "2026-06-30 시점 사실 44건", "is": "end=2026-06-30 사실 148건(시점형 52)",
                             "why": "44 는 재현되지 않았다(리뷰 A 2차). 결론은 같다."}


RESTRICTED_ADD = {
    "amazon.net_cash.nc37": {"us-gaap:RestrictedCashNoncurrent": 2431000000.0, "us-gaap:RestrictedCashAndInvestments": 2714000000.0},
    "meta.net_cash.nc37": {"us-gaap:RestrictedCashAndCashEquivalentsAtCarryingValue": 702000000.0,
                           "us-gaap:RestrictedCashAndCashEquivalentsNoncurrent": 13107000000.0},
    "tesla.net_cash.nc37": {"us-gaap:RestrictedCashNoncurrent": 710000000.0},
    "spacex-xai.net_cash.nc37": {"us-gaap:RestrictedCashNoncurrent": 620000000.0},
}


def net_cash_restricted(obs: dict) -> None:
    for o in obs["items"]:
        add = RESTRICTED_ADD.get(o["observation_id"])
        if not add:
            continue
        comp = o["basis"]["components"]
        ex = comp["excluded_nonmarketable_present"]
        for tag, value in add.items():
            ex[tag] = {"value": value, "why": "제한 현금 — FIX-53 3단계에서 누락을 채웠다(리뷰 A 2차, 같은 기준일 companyfacts)"}
        comp["excluded_completeness"] = ("**`전부 남겼다` 는 성립하지 않았다.** 같은 기준일 제한현금 태그 일부가 빠져 있어 채웠다. 제한현금은 "
                                         "어차피 빼므로 net_cash 값은 그대로다. 이 목록은 제외 판단에 쓴 개념이며 companyfacts 전 개념의 "
                                         "전수 목록은 아니다.")


def tsmc_pretax(o: dict) -> None:
    b = o["basis"]
    if "보존 20-F 916행" in b["how_reconstructed"]:
        b["how_reconstructed_superseded"] = b["how_reconstructed"]
    b["how_reconstructed"] = ("보존 20-F(f14a235:validation/tsm-edgar-29/_raw/tsm-20251231.htm) 감사 재무제표 `CONSOLIDATED STATEMENTS OF "
                              "PROFIT OR LOSS AND OTHER COMPREHENSIVE INCOME` 표의 `INCOME BEFORE INCOME TAX` 행 — "
                              "`979,316.5 1,405,840.0 2,041,654.7 65,083.0` 에서 2025 열 2,041,654.7 NT$백만")
    b["location_correction"] = ("`916행` 은 재현되지 않는다 — 보존 htm 은 6줄이다(리뷰 A 2차). 행 번호 대신 표 제목과 행 이름으로 적는다.")


# ================================================================== run.json
def fix_run(run: dict) -> None:
    a = run["assumptions"]
    for i, text in enumerate(a):
        if text.startswith("anthropic Series H 조달액이 원본 안에서") and "FIX-53" not in text:
            a[i] = (text + " — **[FIX-53 3단계] 지금은 점수를 가르지 않는다.** FIX-52 S2 로 arr_growth 가 run_rate 로 불충족이라 세 "
                    "시나리오 모두 F6 -4 다. 진짜 ARR 이 들어오면 다시 가를 수 있다")
        elif text.startswith("legacy cash 의 정의는 12개사 안에서 세 갈래였다") and "FIX-53" not in text:
            a[i] = ("legacy cash 의 정의는 12개사 안에서 세 갈래였다 — 8개사는 유동성 버퍼, 3개사는 비유동 증권까지 포함한 총계, "
                    "1개사(nvidia)는 어느 쪽도 아니다. 단일 정의가 아니었다 [FIX-53 3단계 정정: 전에는 7/3/2 — spacex-xai 유동성 "
                    "버퍼를 시장성 증권 6,487M 누락으로 잘못 계산했다]")
        elif "제외 내역은 관측 basis.components 에 전부 남겼다" in text:
            a[i] = text.replace("제외 내역은 관측 basis.components 에 전부 남겼다",
                                "제외 판단에 쓴 개념을 관측 basis.components 에 남겼다(전수 목록은 아니다 — FIX-53 3단계에서 제한현금 "
                                "태그 누락 넷을 채웠다)")
        elif text.startswith("[NONOP-44] spacex-xai 는 세전이익을 복원하지 못해"):
            a[i] = ("[NONOP-44 → FIX-53 3단계 정정] spacex-xai 는 세전이익이 **음수**(-7,623M, S-1/A FY2025 + 10-Q 반기 복원)라 "
                    "`(세전 − 영업이익) / 세전` 의 부호 규약이 서지 않아 nonop_share 를 산출하지 않는다(incompatible_basis). 전에 적은 "
                    "`세전이익을 복원하지 못해` 는 사실이 아니었다. 강등은 short_history 가 유지하므로 점수는 그대로다")


# ================================================================== 판단
F2_NOTE_OLD = "C-03: 경로 매핑 미확정 — 승계 점수"
F2_NOTE_NEW = ("~~C-03: 경로 매핑 미확정 — 승계 점수~~ C-03 확정(paths_with_generation_gap_5), 세대 격차는 판단 입력이라 경로 판정 "
               "전까지 승계 [FIX-53 3단계]")


def fix_judgments(jud: dict) -> None:
    by = {j["judgment_id"]: j for j in jud["items"]}
    for j in jud["items"]:
        if j["factor"] == "F2" and F2_NOTE_OLD in (j.get("note") or "") and F2_NOTE_NEW not in j["note"]:
            j["note"] = j["note"].replace(F2_NOTE_OLD, F2_NOTE_NEW, 1)

    a = by["anthropic.F2"]
    ev = a["evidence"]
    frag = "+ Artificial Analysis Index 1위"
    struck = "~~+ Artificial Analysis Index 1위~~ (superseded [FIX-53 3단계] — C-03 확정 전 잣대)"
    if ev[0].endswith(frag):
        ev[0] = ev[0][: -len(frag)] + struck
    if ev[1].startswith("🆕 GPT-6 Astra 출시 후에도 1위 방어") and not ev[1].startswith("(superseded"):
        ev[1] = "(superseded [FIX-53 3단계] — `AA 종합 1위` 방어는 C-03 확정 전 5점 잣대) " + ev[1]
    add = ("📐 [FIX-53 3단계] **C-03 확정 기준(혼합 모델)** — 5점은 `AA 종합 1위` 가 아니라 **성능 도약이 세대 격차 수준일 때**다. 경로 수 "
           "0·1·2 → 2·3·4. openai.F2 가 `Anthropic 이 AA 종합 1위로 받은 점수` 라고 지목한 잣대가 이 근거란 첫 두 줄이라 같은 방식으로 "
           "superseded 표시했다. 점수 5 는 승계 그대로이고 세대 격차 판정은 이번 실행에서 하지 않았다(긴장 #11).")
    if add not in ev:
        ev.append(add)
    a["note"] = once(a.get("note"), f"{MARK} 근거란의 AA 종합 1위 잣대에 superseded 표시(meta·openai 와 같은 방식). 점수·status 불변.")

    f8 = by["anthropic.F8.f8anth33"]
    for i, e in enumerate(f8["evidence"]):
        if "AWS $100B/10년(연 ~$10B)" in e and "FIX-53 3단계 라벨 정정" not in e:
            e = e.replace("AWS $100B/10년(연 ~$10B)",
                          "AWS $100B/10년(연 ~$10B) [FIX-53 3단계 라벨 정정: 10-Q Note 1 문면은 `expansion of … existing multi-year "
                          "commitment by more than $100.0 billion over 10.0 years` — 기존 다년 약정 **위의 증액**이고 `more than` 이라 "
                          "**하한**이다. $100B/10년은 약정 총액이 아니다. $300B 합계는 v1.5 기준선 값(HANDOVER 51행)]", 1)
        if "(v1.5 원본 188·198·217·350행에서 확인)" in e:
            e = e.replace("(v1.5 원본 188·198·217·350행에서 확인)",
                          "(채점표_v1.5.md 188·198·350행 · 채점규칙_v1.5.md 217행에서 확인 — FIX-53 3단계 문서명 분리)")
        f8["evidence"][i] = e
    f8["note"] = once(f8.get("note"), f"{MARK} AWS $100B 라벨을 공시 문면(기존 약정 위 증액·하한)에 맞추고 v1.5 인용 행을 문서별로 나눴다. 점수 불변.")

    n = by["nvidia.F2"]
    if n["evidence"][0].startswith("Vera Rubin 양산") and "(발표 — NVIDIA 보도자료)" not in n["evidence"][0]:
        n["evidence"][0] = "(발표 — NVIDIA 보도자료) " + n["evidence"][0]
    if not n["evidence"][1].startswith("(출처 없음)"):
        n["evidence"][1] = "(출처 없음) " + n["evidence"][1]
    n["note"] = once(n.get("note"), (
        f"{MARK} TEN-RA-02 등록. **Rubin 줄은 발표다** — 출처가 NVIDIA 자체 보도자료(research/nvidia-recent-4m-2026-05.md 12·15·36·39행, "
        "2026-01-05 공개·2026-03-16 GTC 공개)이고 저장소 어느 자료도 2026-09-02 기준 양산을 말하지 않는다. 같은 실행 초안 TRIG-016 은 "
        "`Vera Rubin 출하가 Blackwell 담보 가치를 깎는` 것을 **미발동 미래 사건**으로 둬 시점이 모순된다. 채점규칙 382행 `벤더 발표 벤치마크는 "
        "1차 근거가 아니다` · 349행 `(실측)/(발표)를 표기` 가 지켜지지 않았다. 점유율 70~75% 는 구간만 있고 출처가 없다. 점수 5 는 승계 그대로."))


# ================================================================== 긴장
def add_tension(rules: dict) -> None:
    tens = rules["open_tensions"]
    tens[:] = [t for t in tens if t["id"] != "TEN-RA-02"]
    tens.append({
        "id": "TEN-RA-02",
        "status": "open",
        "recheck_at": "2026-11",
        "review_finding": "RA-02 · obsreg 2차 리뷰 A(qwen) · 체크리스트 Q05·Q09 fail",
        "judgment_ids": ["nvidia.F2"],
        "subject": "nvidia F2 5점의 성능 근거가 벤더 발표이고 같은 실행 안에서 시점이 반증된다",
        "tension": ("nvidia.F2 근거 `Vera Rubin 양산(R100 3,360억 트랜지스터, Blackwell 대비 추론 5배·토큰당 비용 1/10)` 의 출처가 NVIDIA 자체 "
                    "보도자료다. 저장소 어느 자료도 2026-09-02 기준 양산을 말하지 않고, 초안 TRIG-016 은 Rubin 출하를 미발동 미래 사건으로 "
                    "둔다. 채점규칙 382행 `벤더 발표 벤치마크는 1차 근거가 아니다 — 독립 측정을 우선한다` · 349행 `근거마다 (실측)/(발표)를 "
                    "표기한다` 를 어긴다. 점유율 70~75% 는 출처가 없다."),
        "direction": "하향 가능(5 → 4 검토). 세대 격차의 독립 측정 근거가 확인되면 유지.",
        "rechecker": "2026-11 재채점 때 판단자.",
        "why_carried_exception": ("승계 판단의 기존 논리이고 이번 실행이 F2 잣대를 새로 대지 않았다 — anthropic F2 의 독립 측정 재검토도 점수 "
                                  "변경 없이 넘어갔다. 재검토 시점과 함께 등록했으므로 승계 판단 예외에 해당한다."),
        "score_impact_now": "없다.",
        "source_lines": ["채점규칙 349행", "채점규칙 382행", "research/nvidia-recent-4m-2026-05.md 12·15·36·39행"],
        "note": "관련 긴장 #11 — 세대 격차가 몇 축에서 서야 하는지와 독립 측정 요건이 원문 미규정이다(decisions C-03 generation_gap_constraints).",
    })


def main() -> int:
    registry = {c["company_id"]: c for c in load_json_strict(ROOT / "scorecard" / "companies.json")["companies"]}
    rules = load(RULES)
    obs = load(RUN / "observations.json")
    jud = load(RUN / "judgments.json")
    run = load(RUN / "run.json")
    by = {o["observation_id"]: o for o in obs["items"]}

    alibaba_contracted(by["alibaba.contracted_revenue.obsreg25"])
    spacex_cash(by["spacex-xai.cash.cashfcf35"])
    n_split = fix_legacy_split(obs)
    anthropic_straddle(by["anthropic.cumulative_raised.priv31"])
    oracle_net_cash(by["oracle.net_cash.nc37"])
    spacex_revenue(by["spacex-xai.revenue_ttm.f6reg28"])
    palantir_lease(by["palantir.lease_liabilities.nc37"])
    net_cash_restricted(obs)
    tsmc_pretax(by["tsmc.pretax_income_ttm.nonop44"])
    spacex_pretax(obs)
    fix_run(run)
    fix_judgments(jud)
    add_tension(rules)

    validate_rules(rules)
    validate_observations(obs, registry, RUN_ID)
    validate_judgments(jud, registry, rules, RUN_ID)
    dump(RULES, rules)
    dump(RUN / "observations.json", obs)
    dump(RUN / "judgments.json", jud)
    run["rule_hash"] = load_rules("v1.7").hash
    validate_run(run, RUN_ID)
    dump(RUN / "run.json", run)
    print(f"관측 정정 · legacy 정의 분포 문장 {n_split}건 갱신 · spacex 세전이익 등록 · 판단 정정 · TEN-RA-02 · rule_hash {run['rule_hash'][:12]}")
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    sys.exit(main())
