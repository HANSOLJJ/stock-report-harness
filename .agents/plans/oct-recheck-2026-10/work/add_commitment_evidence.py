# ⑧ 약정 축 공시 근거(Alphabet·Microsoft·Meta 10-Q/10-K 주석)를 근거 후보로 넣고 ⑧ 판단 파일에 내릴 근거 줄을 더한다
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "scripts"))
from scorecard.paths import run_paths  # noqa: E402
from scorecard.schema import load_json_strict, write_json  # noqa: E402

JUDGE = Path(__file__).resolve().parent / "judge"
ITEMS = [
    ("alphabet", "SRC-EDGAR-000165204426000071", "2026-07-23T00:00:00Z", "Alphabet 10-Q (2026-06-30)",
     "As of June 30, 2026, expected future fixed or guaranteed commitments under these agreements were $ 707.0 billion, the significant "
     "majority of which related to long-term supply agreements. We expect contractual commitments under the long-term supply agreements "
     "and content licenses to generally be fulfilled through 2030.",
     "Part I Item 1, Note 10 Commitments and Contingencies 의 Commitments 문단"),
    ("alphabet", "SRC-EDGAR-000165204426000071", "2026-07-23T00:00:00Z", "Alphabet 10-Q (2026-06-30)",
     "As of June 30, 2026, we have entered into leases, primarily related to data centers, that have not yet commenced with future lease "
     "payments of $ 85.2 billion that are not yet recorded. These leases will commence between 2026 and 2031 with non-cancelable lease terms "
     "between one and 26 years. Additionally, in June 2026, we entered into a short-term lease agreement with a non-cancelable commitment of "
     "approximately $ 5.8 billion, which will commence in the third quarter of 2026.",
     "Part I Item 1, Note 4 Leases 의 미래 리스 지급액 표 다음 문단"),
    ("microsoft", "SRC-EDGAR-000119312526323660", "2026-07-29T00:00:00Z", "Microsoft 10-K (FY2026)",
     "As of June 30, 2026, we had additional leases, primarily for datacenters, that had not yet commenced of $ 329.1 billion, with some "
     "arrangements subject to certain contractual conditions being met. … Construction commitments (b) 29,848 4,718 34,566 … Purchase "
     "commitments (d) 169,008 25,052 194,060 … (d) Purchase commitments primarily relate to datacenters and include open purchase orders and "
     "take-or-pay contracts that are not presented as construction commitments above.",
     "Part II Item 8 Note 13 Leases 마지막 문단과 Item 7 Contractual Obligations 표(백만 달러, 2027·이후·합계 열)"),
    ("meta", "SRC-EDGAR-000162828026050705", "2026-07-30T00:00:00Z", "Meta 10-Q (2026-06-30)",
     "These lease obligations were approximately $ 278.99 billion, consisting of data centers, colocations, and certain network "
     "infrastructure, which will commence during the remainder of 2026 through 2036 with lease terms ranging from greater than one year to "
     "30 years. … As of June 30, 2026, we had $ 349.31 billion of non-cancelable contractual commitments, comprising both short-term and "
     "long-term arrangements. These commitments mostly relate to third-party cloud capacity arrangements and investments in servers and "
     "network infrastructure, data centers, and consumer hardware products in Reality Labs",
     "Part I Item 1, Note 9 Commitments and Contingencies 의 Leases and Contractual Commitments 문단"),
]
LINES = {
    "alphabet": ("2026-06-30 고정·보장된 장기 약정 $707.0B 와 미개시 리스 $85.2B·단기 리스 약정 $5.8B 를 더한 약 $7,980억은 최근 1년 매출 "
                 "$4,458.66억의 약 1.79배다(계산). [{a}, {b}]"),
    "microsoft": ("2026-06-30 미개시 리스 $329.1B 와 구매 약정 $194.06B·건설 약정 $34.57B 를 더한 약 $5,578억은 2026 회계연도 매출 "
                  "$3,318.39억의 약 1.68배다(계산). [{a}]"),
    "meta": ("2026-06-30 미개시 리스 약 $278.99B 와 해지할 수 없는 약정 $349.31B 를 더한 약 $6,283억은 최근 1년 매출 $2,282.47억의 "
             "약 2.75배다(계산). [{a}]"),
}


def main() -> int:
    slug = sys.argv[1]
    p = run_paths(slug).evidence
    d = load_json_strict(p)
    nxt = {}
    for e in d["items"]:
        c = e["company_id"]
        nxt[c] = max(nxt.get(c, 0), int(e["evidence_id"].rsplit("-", 1)[1]))
    ids: dict[str, list[str]] = {}
    for cid, sid, pub, title, excerpt, loc in ITEMS:
        nxt[cid] += 1
        eid = f"EV-{cid}-{nxt[cid]:03d}"
        ids.setdefault(cid, []).append(eid)
        d["items"].append({"evidence_id": eid, "company_id": cid, "factors": ["F8"], "kind": "filing", "source_id": sid,
                           "published_at_utc": pub, "title": title, "excerpt": excerpt, "locator": loc,
                           "relevance": "사실: 공시가 아직 개시되지 않은 데이터센터 리스와 해지할 수 없거나 고정·보장된 구매 약정의 금액을 밝힌다. "
                                        "추론: ⑧ 약정 축(약정 합계 ÷ 최근 1년 매출)의 분자다.",
                           "channel": "disclosure", "conditional_impact": "지금은 유지: 이 실행의 ⑧ 약정 축 판정에 쓰는 공시 수치다.",
                           "horizon": "2026Q3", "counter_evidence": [], "unverified": [], "change_vs_previous": "new", "status": "candidate"})
    write_json(p, d)
    for cid, line in LINES.items():
        f = JUDGE / f"F8-{cid}.json"
        s = json.loads(f.read_text(encoding="utf-8"))
        new = line.format(a=ids[cid][0], b=ids[cid][1] if len(ids[cid]) > 1 else "")
        s["evidence_down_after"].insert(0, new)
        s["cite"] = sorted(set(s.get("cite") or []) | set(ids[cid]))
        f.write_text(json.dumps(s, ensure_ascii=False, indent=2), encoding="utf-8")
    print(",".join(i for v in ids.values() for i in v))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
