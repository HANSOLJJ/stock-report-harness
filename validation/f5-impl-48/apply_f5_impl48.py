# F5-IMPL-48: 체크리스트 19 재판정(두 모델 독립 일치)으로 anthropic·openai F5 의 A 를 +2→+1 로 교체한다
"""옛 판단은 지우지 않고 새 판단의 `superseded` 에 문언 그대로 싣는다.

재실행해도 같은 결과가 나온다 — 이미 교체된 판단이면 `superseded` 에서 옛 판단을 복원한 뒤 다시 교체한다.
"""
from __future__ import annotations

import copy
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
DATE = "2026-09-14"
SUFFIX = "impl48"
REVIEWER = "설계진행(C-13 A-GRADE-45 · NTM A-GRADE-45B 독립 일치)"
WHY = ("체크리스트 19 적용(사용자 결정 ①). 받은 투자를 빼고 별표 G A 기준표에 다시 대입하니 +2 두 조항이 "
       "다 서지 않았다. C-13(a01f127)과 NTM(1aab1f2)이 서로 산출물을 보지 않고 같은 +1 을 냈다.")

COMMON = [
    "📐 **[F5-IMPL-48 재판정 2026-09-14] 체크리스트 19(채점규칙 727행)** `⑤에서 \"받은 투자\"를 곧바로 동맹 +2로 "
    "셌나? — 아군 확보는 능동태다. 피투자 관계는 ⑦⑧에서도 세므로 이중 계상 위험 — 별표 G의 A 기준으로 판정`",
    "별표 G A 기준표(188~195행) — `+2` 지분이 걸린 동맹이 **복수**이거나 **경쟁사까지** 내 매대·공정·플랫폼에 "
    "편입했다 · `+1` 의미 있는 상업 동맹이 있으나 소수이거나 한 방향이다 · `0` 확인되는 독립 상업 동맹이 없다",
]

NEW = {
    "anthropic": {
        "inputs": {"A": 1, "H": 0},
        "evidence": COMMON + [
            "제외 — 받은 투자: Amazon · Google · MS 의 Anthropic 지분 투자(체크리스트 19). 별표 H 288행이 관계를 "
            "`지분 + 유통` 으로 갈라 적으므로 투자를 빼면 유통 하나가 남는다",
            "남는 것 — 3대 하이퍼스케일러 유통(AWS Bedrock · Google Vertex AI · MS Azure Foundry) · 미 국방부 CDAO "
            "프론티어 AI 계약(2025-07, 4사 각각 상한 $200M, 4사 공통이라 ⑤ 변별력 없음)",
            "+2 첫 조항 불성립 — 유통을 지분 동맹으로 세면 **뺀 지분을 다시 세는 순환**이다. Anthropic 이 맺은 지분 "
            "동맹이 없다",
            "+2 둘째 조항 불성립 — 문언이 `경쟁사까지 **내** 매대·공정·플랫폼에 편입` 이다. Anthropic 은 **남의 매대에 "
            "오른 쪽**이라 방향이 반대다",
            "0 불성립 — 3사 유통은 공짜 사용자도 관계사도 아닌 독립 상업 동맹이다 → **A=+1**",
            "⑧-3 과 이중 계상 아님 — 262행 `금지선은 \"같은 관계\"가 아니라 \"같은 속성\"` · 264행 금지는 같은 *위험*을 "
            "양쪽에서 깎기 · 266행 `같은 관계를 ⑤(연동 이익)와 ⑧(대체 불가 위험)에 각각 한 번씩` 허용. 288행도 "
            "`동맹(+ ⑧-3 별도)` 로 적는다",
            "H=0 근거는 승계 — `적대세력 최소` (v1.5, 이번 과제의 재검토 대상 아님)",
            "✅ 3 + A +1 + H 0 = **4** (5 → 4)",
        ],
        "counter_evidence": [
            "원문 별표 G 판정표 214행은 `Anthropic | +2 | Amazon·Google·MS 3사 전원 투자+유통 | 0 | 적대 최소 | 5` 로 "
            "적는다. 이 재판정은 **같은 규칙서의 체크리스트 19 로 그 행의 A 를 뒤집은 것**이다 — 원문 판정표와 "
            "지금 판단이 다르다는 사실을 남긴다",
            "worker 관찰(두 재판정 산출물은 따로 다루지 않음) — 옛 근거 첫 줄의 `Amazon 5GW + Google 5GW TPU + MS 1GW` "
            "는 사는 쪽의 컴퓨트 확보라 197행 `조달 ≠ 동맹` 에 걸리고 ⑧-3 에서 따로 센다. +1 판정은 유통만으로 서므로 "
            "점수에 닿지 않는다",
        ],
        "note": ("[F5-IMPL-48] 체크리스트 19 적용 재판정(사용자 결정 ①). A +2→+1, F5 5→4. 두 모델 독립 일치 — "
                 "C-13(Gemini) a01f127 validation/a-grade-45 · NTM(Claude) 1aab1f2 validation/a-grade-45b, 확정 "
                 "02bcd90. 옛 판단은 superseded 에 문언 그대로 남겼다."),
    },
    "openai": {
        "inputs": {"A": 1, "H": -3},
        "evidence": COMMON + [
            "제외 — 받은 투자: Amazon $50B · SoftBank · MS 27% · NVIDIA(체크리스트 19). 제외 — 조달: Oracle $300B "
            "컴퓨트 계약 — 채점표 759행 `Oracle $300B 컴퓨트 계약 자체는 사는 쪽의 조달이라 동맹 근거가 아니다(별표 H)` "
            "· 197행 `조달 ≠ 동맹`",
            "별표 H 276행 `OpenAI → MS·Oracle·NVIDIA | … | 내가 못 떠남` — 이 관계들은 OpenAI 가 매달린 쪽이다",
            "남는 것 — Stargate LLC 공동 지분(OpenAI 40%·Oracle $7B·SoftBank 40%·MGX) · Broadcom Jalapeño 공동개발 · "
            "미 국방부 CDAO 계약(4사 공통이라 ⑤ 변별력 없음)",
            "+2 첫 조항 불성립 — 지분이 걸린 동맹은 Stargate **하나**다. 복수가 아니다",
            "+2 둘째 조항 불성립 — 경쟁사를 OpenAI 의 매대·공정·플랫폼에 편입한 사실이 없다",
            "0 불성립 — Broadcom(공동개발)과 DoD 가 남고 둘 다 공짜 사용자도 관계사도 아니다 → **A=+1**",
            "구분 주의(IMPL-46 승계) — 빠지는 것은 Oracle $300B 계약이지 Oracle 전체가 아니다. **Stargate $7B 지분은 "
            "동맹으로 남는다**",
            "H=-3 근거는 승계(v1.5, 이번 과제의 재검토 대상 아님) — MS와 긴장(Azure 독점 소멸) · Apple 상호 소송 · 머스크 "
            "반독점 계류 · NYT 등 MDL No. 3143 저작권 집단소송(6/24 지역신문 약 400곳 추가 제소, 7/10 Apple 제소). "
            "단 Bedrock 입점은 긍정 변수",
            "✅ 3 + A +1 + H -3 = **1** (2 → 1)",
        ],
        "counter_evidence": [
            "원문 별표 G 판정표 224행은 `OpenAI | +2 | Oracle $300B·Amazon $50B·SoftBank·DoD | -3 | … | 2` 로, 별표 H "
            "276행은 같은 줄에 `A+2` 로 적는다. 이 재판정은 **같은 규칙서의 체크리스트 19 와 197행으로 그 행들의 A 를 "
            "뒤집은 것**이다 — 원문 판정표와 지금 판단이 다르다는 사실을 남긴다",
        ],
        "note": ("[F5-IMPL-48] 체크리스트 19 적용 재판정(사용자 결정 ①). A +2→+1, F5 2→1. 두 모델 독립 일치 — "
                 "C-13(Gemini) a01f127 · NTM(Claude) 1aab1f2, 확정 02bcd90. | [IMPL-46 승계] **Oracle $300B 컴퓨트 "
                 "계약을 A 근거에서 뺀다** — 사는 쪽의 조달이고 동맹이 아니다(197행 · 221행 Apple 선례 · 채점표 759행). "
                 "**Stargate $7B 지분은 동맹으로 남는다.** | IMPL-46 당시 `점수는 그대로 2` · `체크리스트 19 는 반영하지 "
                 "않았다` 는 그때 사실이었고 이 과제로 대체됐다 — superseded.note 에 원문 그대로 있다."),
    },
}


def load(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def dump(p: Path, d: dict) -> None:
    raw = io.open(p, encoding="utf-8", newline="").read()
    out = json.dumps(d, ensure_ascii=False, indent=2) + ("\n" if raw.endswith("\n") else "")
    io.open(p, "w", encoding="utf-8", newline="").write(out)


def restore(item: dict) -> dict:
    """이미 교체된 판단이면 superseded 에서 옛 판단을 되살린다 (재실행 멱등)."""
    if "superseded" not in item:
        return item
    sup = item["superseded"]
    old = {"judgment_id": sup["judgment_id"], "company_id": item["company_id"], "factor": item["factor"],
           "kind": item["kind"], "score": sup.get("score"), "inputs": sup["inputs"], "evidence": sup["evidence"],
           "counter_evidence": sup.get("counter_evidence", []), "note": sup.get("note"),
           "reviewer": sup["reviewer"], "reviewed_at": sup["reviewed_at"], "status": sup.get("status", "carried")}
    if "carried_from" in sup:
        old["carried_from"] = sup["carried_from"]
    if "source_ids" in sup:
        old["source_ids"] = sup["source_ids"]
    return old


def main() -> int:
    path = RUN / "judgments.json"
    jud = load(path)
    for i, item in enumerate(jud["items"]):
        cid = item["company_id"]
        if item["factor"] != "F5" or cid not in NEW:
            continue
        old = restore(item)
        spec = NEW[cid]
        sup = {k: copy.deepcopy(old[k]) for k in ("judgment_id", "score", "inputs", "evidence", "reviewer",
                                                  "reviewed_at", "status", "carried_from", "note",
                                                  "counter_evidence", "source_ids") if k in old}
        sup["superseded_at"] = DATE
        sup["why"] = WHY
        new = {
            "judgment_id": f"{cid}.F5.{SUFFIX}",
            "company_id": cid,
            "factor": "F5",
            "kind": old["kind"],
            "score": None,
            "inputs": spec["inputs"],
            "evidence": spec["evidence"],
            "counter_evidence": spec["counter_evidence"],
            "note": spec["note"],
            "reviewer": REVIEWER,
            "reviewed_at": DATE,
            "status": "new",
            "source_ids": old.get("source_ids", ["SRC-v15-html"]),
            "previous_judgment_id": old["judgment_id"],
            "superseded": sup,
        }
        jud["items"][i] = new
        print(f"{cid:10} {old['judgment_id']} A {old['inputs']['A']:+d} H {old['inputs']['H']:+d}"
              f"  ->  {new['judgment_id']} A {spec['inputs']['A']:+d} H {spec['inputs']['H']:+d}")

    rules = load_rules("v1.7")
    registry = {c["company_id"]: c for c in load_json_strict(ROOT / "scorecard" / "companies.json")["companies"]}
    validate_judgments(jud, registry, rules.payload, RUN_ID)
    dump(path, jud)
    print("judgments.json 검증 통과·저장")
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    sys.exit(main())
