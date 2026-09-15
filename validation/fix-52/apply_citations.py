# FIX-52 인용·출처 표기 — 판단 source_ids·관측 source_id 를 인용 문서에 맞추고 HANDOVER 등재·접수번호·경로 규약을 바로잡는다
"""리뷰 A(qwen) 발견. 점수 무영향이다. 설계진행이 전부 원자료에서 확인했고 worker 도 다시 확인했다.

1. 판단 source_ids — 근거란이 인용한 문서의 source_id 를 전부 단다.
2. 관측 26건 source_id — 값이 실린 채점표 .md 행을 인용하는 legacy 관측을 SRC-v15-md 로.
3. sources.json — HANDOVER 등재, SRC-v15-rule 이해상충, SRC-SEC-FACTS-F6·BABA-FACTS 경로 규약.
4. apple·spacex-xai 접수번호.
5. run.json assumption 의 낡은 alibaba 문장.

재실행해도 같은 결과가 나온다. 파일 줄끝은 원래 것을 유지한다(HASH-EOL).
"""
from __future__ import annotations

import copy
import io
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard.rules import load_rules  # noqa: E402
from scorecard.schema import load_json_strict, validate_judgments, validate_observations, validate_rules, validate_run  # noqa: E402

RUN_ID = "ai-scorecard-2026-09-obsreg"
RUN = ROOT / "scorecard" / "runs" / RUN_ID
BASE = ROOT / "scorecard" / "runs" / "ai-scorecard-2026-09-baseline"
RULES = ROOT / "scorecard" / "rules" / "v1.7.json"
DATE = "2026-09-15"

HTML, MD, RULE, HANDOVER = "SRC-v15-html", "SRC-v15-md", "SRC-v15-rule", "SRC-v15-handover"
RE_RULE = re.compile(r"채점규칙|별표 [A-J]|체크리스트\s*\d+")
RE_MD = re.compile(r"채점표(?!_HANDOVER)|v1\.5 원본 \d")          # 'v1.5 원본 188·198·217·350행' 은 채점표 .md 행이다
RE_HANDOVER = re.compile(r"HANDOVER")


def load(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def dump(p: Path, d: dict) -> None:
    raw = io.open(p, encoding="utf-8", newline="").read()
    nl = "\r\n" if "\r\n" in raw else "\n"
    out = json.dumps(d, ensure_ascii=False, indent=2) + ("\n" if raw.endswith("\n") else "")
    io.open(p, "w", encoding="utf-8", newline="").write(out.replace("\n", nl))


# ------------------------------------------------------------------ 1. 판단 source_ids
def fix_judgments(jud: dict) -> dict:
    base_lines: dict[tuple[str, str], set[str]] = {}
    for j in load(BASE / "judgments.json")["items"]:
        base_lines.setdefault((j["company_id"], j["factor"]), set()).update(j["evidence"])
    stats = {"changed": 0, "by_set": {}}
    for j in jud["items"]:
        text = json.dumps({k: j.get(k) for k in ("evidence", "counter_evidence", "note")}, ensure_ascii=False)
        carries_v15_text = j["status"] == "carried" or bool(
            set(j["evidence"]) & base_lines.get((j["company_id"], j["factor"]), set()))
        ids: list[str] = []
        if carries_v15_text:
            ids.append(HTML)                         # 근거 문면을 v1.5 HTML 판정표에서 이관했다
        if RE_RULE.search(text):
            ids.append(RULE)
        if RE_MD.search(text):
            ids.append(MD)
        if RE_HANDOVER.search(text):
            ids.append(HANDOVER)
        for sid in j.get("source_ids") or []:
            if sid not in (HTML, MD, RULE, HANDOVER) and sid not in ids:
                ids.append(sid)                      # SEC 등 기존 1차 출처는 유지
        if not ids:
            ids = [HTML]
        if ids != j.get("source_ids"):
            stats["changed"] += 1
            j["source_ids"] = ids
        key = " + ".join(ids)
        stats["by_set"][key] = stats["by_set"].get(key, 0) + 1
    return stats


# ------------------------------------------------------------------ 2. 관측 source_id
def fix_observations(obs: dict) -> list[str]:
    done = []
    for o in obs["items"]:
        if o["source_id"] != HTML or o["status"] != "legacy_unverified":
            continue
        b = o.get("basis") or {}
        metric = o["metric"]
        if metric == "market_cap" and "source_citation" in b:
            cited = [MD]
        elif metric == "ntm_per" and "vendor_source_text" in b:
            cited = [MD, RULE, HANDOVER]
        elif metric == "net_cash" and "source_mixed" in b:
            cited = [MD, HANDOVER]
        else:
            continue
        b["cited_source_ids"] = cited
        b["source_id_correction"] = {
            "from": HTML, "to": MD, "corrected_at": DATE, "task": "FIX-52 (리뷰 A qwen 발견)",
            "why": ("basis 가 인용하는 행 번호(채점표 L794·L8xx 등)는 AI기업_채점표_v1.5.md 의 행이고 .html 의 같은 행에는 "
                    "그 내용이 없다. 값이 실린 표 행이 .md 에 있으므로 source_id 를 .md 로 옮긴다. 채점규칙·HANDOVER 인용은 "
                    "cited_source_ids 에 함께 적는다."),
        }
        o["basis"] = b
        o["source_id"] = MD
        done.append(o["observation_id"])
    return done


# ------------------------------------------------------------------ 4. 접수번호
ACCESSIONS = {
    "apple.cash.cashfcf35": ("0000320193-26-000070", "0000320193-26-000020"),
    "apple.fcf_ttm.cashfcf35": ("0000320193-26-000070", "0000320193-26-000020"),
    "spacex-xai.cash.cashfcf35": ("0001193125-26-235805", "0001628280-26-040364"),
    "spacex-xai.fcf_ttm.cashfcf35": ("0001193125-26-235805", "0001628280-26-040364"),
}


def fix_accessions(obs: dict) -> list[str]:
    done = []
    for o in obs["items"]:
        b = o.get("basis") or {}
        acc = b.get("accession")
        if not isinstance(acc, str):
            continue
        for wrong, right in (("0000320193-26-000070", "0000320193-26-000020"),
                             ("0001193125-26-235805", "0001628280-26-040364")):
            if wrong in acc:
                b["accession"] = acc.replace(wrong, right)
                b["accession_correction"] = {
                    "wrong": wrong, "right": right, "corrected_at": DATE, "task": "FIX-52 (리뷰 A qwen 발견)",
                    "evidence": ({"0000320193-26-000020": "보존 AAPL companyfacts 에 283건, form 10-Q · fy 2026 Q3 · "
                                                          "filed 2026-07-31 · CashAndCashEquivalentsAtCarryingValue "
                                                          "2026-06-27 = 39,544,000,000. 틀린 번호는 0건",
                                  "0001628280-26-040364": "보존 SPCX companyfacts 에 5건, form S-1/A · filed 2026-06-03. "
                                                          "sources.json SRC-SEC-SPCX-S1A-2026 과 같은 런 f6reg28 관측도 이 "
                                                          "번호다. 틀린 번호는 0건"}[right]),
                    "value_unchanged": "값·성분·산식은 맞았고 접수번호 인용만 틀렸다.",
                }
                acc = b["accession"]
                done.append(o["observation_id"])
    return done


# ------------------------------------------------------------------ 3. sources.json
def fix_sources(src: dict, facts_sha: dict) -> None:
    items = {s["source_id"]: s for s in src["items"]}
    items[RULE]["conflict_of_interest"] = ("작성자 Claude=Anthropic — 채점규칙 384행 이해상충 고지(ARC-AGI 하네스 규칙이 결과적으로 "
                                           "Anthropic ②5 를 지켰다, 운영이력 긴장 #4·#11, 제3자 재검토 예정)")
    items[RULE]["note"] = items[RULE]["note"].split(" | [FIX-52]")[0] + " | [FIX-52] 이해상충 칸이 null 이었다(리뷰 A 발견)."
    if HANDOVER not in items:
        src["items"].insert(3, {
            "source_id": HANDOVER,
            "title": "AI기업_채점표_HANDOVER.md (자동화 핸드오버 — 원자료 출처표·기계화 재고·작성자 이해상충)",
            "publisher": "내부 기준선",
            "url": None,
            "accessed_at": "2026-09-14",
            "sha256": "3e5190c2cb4a4f8ebee2f72d4599929b79a5d4625b1d046c346627edf63b7cc1",
            "conflict_of_interest": "작성자 Claude=Anthropic — HANDOVER 75행 `3-7. 작성자 이해상충. Claude=Anthropic` (긴장 #4·#11)",
            "note": ("2026-09-07 작성 · v1.5 기준(문서 2행). 이 실행이 IMPL-46(2026-09-14)부터 행 번호로 인용했는데 항목이 없었다 "
                     "(리뷰 A 발견, FIX-52 등재). 인용 행 33~45·75. 보존 위치는 v1.5 원본 셋과 같은 "
                     "E:/sourcecode/01_side_project/stock-report-harness/AI_company_analysis_factor/ 이고 저장소에 커밋되지 않았다. "
                     "accessed_at 은 이 실행이 처음 인용한 날이다."),
        })
    rule = ("**원자료 경로 규약(FIX-52)** — 커밋된 사본을 `<커밋>:<경로>` 로 적고 브랜치를 괄호에 둔다. 작업 트리에만 있는 "
            "경로(gitignore)는 다른 워크트리·브랜치에서 재현되지 않으므로 규약 경로로 쓰지 않는다.")
    f6 = items["SRC-SEC-FACTS-F6"]
    f6["note"] = (
        "원문 보존 cbada75:validation/f6-avail-15b/_raw/CIK{10자리}_{TICKER}.json (HANSOLJJ/C-13 브랜치, 12개사, "
        "http_metadata.json timestamp 2026-09-10T15:37). " + rule + " | **이 원자료는 이 브랜치와 main 에 커밋되지 않았다.** "
        "worker 작업 트리의 validation/f6-avail-15/_raw/{TICKER}.companyfacts.json 은 gitignore 로 막혀 있고(수집 "
        "2026-09-10T06:38Z), 12개 파일 전부 15b 사본과 **바이트 단위로 같다** — sha256 12건은 "
        "validation/fix-52/facts_f6_sha256.json. 재구성 스크립트(validation/f6-spec-18/collect_ttm.py 등)는 작업 트리 "
        "경로를 읽으므로 이 워크트리 밖에서는 15b 사본으로 대체해야 돈다. 이번 과제에서 신규 호출 없음.")
    baba = items["SRC-SEC-BABA-FACTS"]
    baba["note"] = ("원문 보존 cbada75:validation/f6-avail-15b/_raw/CIK0001577552_BABA.json (HANSOLJJ/C-13). "
                    "SRC-SEC-FACTS-F6 과 같은 경로 규약. 신규 네트워크 호출 없음")


# ------------------------------------------------------------------ 5. run.json
OLD_ASSUMPTION = "alibaba 의 fcf_ttm·cash 는 여전히 legacy_unverified 이고 기간 정의가 없다."


def fix_run(run: dict, obs: dict) -> bool:
    by_id = {o["observation_id"]: o for o in obs["items"]}
    cash, fcf = by_id["alibaba.cash.cashfcf35"], by_id["alibaba.fcf_ttm.cashfcf35"]
    for i, a in enumerate(run["assumptions"]):
        if a.startswith(OLD_ASSUMPTION):
            run["assumptions"][i] = (
                f"~~{a}~~ **[낡음 {DATE} FIX-52]** alibaba 의 cash·fcf_ttm 은 cashfcf35 에서 verified 로 등록됐다 — "
                f"cash {cash['value'] / 1e6:,.0f}M USD(as_of {cash['as_of']}) · fcf_ttm {fcf['value'] / 1e6:,.0f}M USD"
                f"(FY2026 연간 {fcf['period']['start']}~{fcf['period']['end']}). legacy 판본(alibaba.cash.v15 · fcf_ttm.v15)은 "
                "별도로 남아 있다.")
            return True
    return False


def fix_rules_note(rules: dict, obs: dict) -> None:
    counts = {}
    for o in obs["items"]:
        if o["source_id"].startswith("SRC-v15-"):
            counts[o["source_id"]] = counts.get(o["source_id"], 0) + 1
    total = sum(counts.values())
    note = rules["sources"]["note"]
    new = f"이관 관측 {total}건(obsreg 기준 html {counts.get(HTML, 0)} + rule {counts.get(RULE, 0)} + md {counts.get(MD, 0)}"
    note = re.sub(r"이관 관측 \d+건\(obsreg 기준 [^)]*", new, note, count=1)
    marker = " | [FIX-52] 관측 26건의 source_id 를 html → md 로 바로잡아 내역이 209+18+15 에서 바뀌었다(합계 불변)."
    if marker not in note:
        note += marker
    rules["sources"]["note"] = note


def main() -> int:
    registry = {c["company_id"]: c for c in load_json_strict(ROOT / "scorecard" / "companies.json")["companies"]}
    rules = load(RULES)

    jud = load(RUN / "judgments.json")
    jstats = fix_judgments(jud)
    validate_judgments(jud, registry, rules, RUN_ID)

    obs = load(RUN / "observations.json")
    moved = fix_observations(obs)
    accs = fix_accessions(obs)
    validate_observations(obs, registry, RUN_ID)

    src = load(RUN / "sources.json")
    facts_sha = load(Path(__file__).resolve().parent / "facts_f6_sha256.json")
    fix_sources(src, facts_sha)
    ids = {s["source_id"] for s in src["items"]}
    missing = sorted({sid for j in jud["items"] for sid in j["source_ids"] if sid not in ids}
                     | {o["source_id"] for o in obs["items"] if o["source_id"] not in ids})
    assert not missing, f"sources.json 에 없는 source_id: {missing}"

    run = load(RUN / "run.json")
    changed_run = fix_run(run, obs)

    fix_rules_note(rules, obs)
    validate_rules(rules)

    dump(RUN / "judgments.json", jud)
    dump(RUN / "observations.json", obs)
    dump(RUN / "sources.json", src)
    dump(RULES, rules)
    run["rule_hash"] = load_rules("v1.7").hash
    validate_run(run, RUN_ID)
    dump(RUN / "run.json", run)

    print(f"1. 판단 source_ids 변경 {jstats['changed']}건")
    for key, n in sorted(jstats["by_set"].items(), key=lambda kv: -kv[1]):
        print(f"     {n:3} × {key}")
    print(f"2. 관측 source_id html → md {len(moved)}건")
    print(f"3. sources.json HANDOVER 등재 · rule COI · FACTS-F6/BABA 경로 규약")
    print(f"4. 접수번호 정정 {len(accs)}건: {', '.join(accs)}")
    print(f"5. run.json alibaba assumption 낡음 표시: {changed_run}")
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    sys.exit(main())
