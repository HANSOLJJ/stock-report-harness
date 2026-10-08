# Meta 공식 블로그의 MTIA 데이터센터 배치 문장을 근거 후보(EV-meta-056)와 출처(SRC-WEB-meta-015)로 실행에 추가한다
"""
사용: uv run --frozen python -X utf8 .agents/plans/rejudge-all-2026-11/work/add_evidence_meta_mtia.py <slug>
확정은 따로 `scorecard_cli.py confirm <slug> --evidence EV-meta-056 --by "claude (사용자 위임 2026-10-08)"` 로 한다.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "scripts"))
from scorecard.schema import load_json_strict, write_json  # noqa: E402

EVIDENCE_ID = "EV-meta-056"
SOURCE_ID = "SRC-WEB-meta-015"
URL = "https://ai.meta.com/blog/next-generation-meta-training-inference-accelerator-AI-MTIA/"


def main() -> int:
    slug = sys.argv[1]
    run = ROOT / "output" / slug
    ev_path = run / "evidence" / "evidence.json"
    src_path = run / "sources.json"
    ev = load_json_strict(ev_path)
    src = load_json_strict(src_path)
    if any(e["evidence_id"] == EVIDENCE_ID for e in ev["items"]):
        print(f"{EVIDENCE_ID} 이미 있다"); return 0
    if any(s["source_id"] == SOURCE_ID for s in src["items"]):
        raise SystemExit(f"{SOURCE_ID} 가 이미 있다 — 번호를 다시 본다")
    src["items"].append({
        "source_id": SOURCE_ID,
        "title": "Our next-generation Meta Training and Inference Accelerator",
        "publisher": "Meta AI Blog",
        "url": URL,
        "accessed_at": "2026-10-09",
        "sha256": None,
        "conflict_of_interest": None,
        "note": "회사 공식 엔지니어링 블로그. 게시일 2024-04-10",
        "kind": "news",
        "company_id": "meta",
        "published_at_utc": "2024-04-10T00:00:00Z",
    })
    ev["items"].append({
        "evidence_id": EVIDENCE_ID,
        "company_id": "meta",
        "factors": ["F4"],
        "kind": "news",
        "source_id": SOURCE_ID,
        "published_at_utc": "2024-04-10T00:00:00Z",
        "title": "Our next-generation Meta Training and Inference Accelerator",
        "excerpt": ("MTIA has been deployed in the data center and is now serving models in production. We are already seeing the positive "
                    "results of this program as it's allowing us to dedicate and invest in more compute power for our more intensive AI workloads. "
                    "… This allowed us to land this next-generation MTIA silicon rapidly, going from first silicon to production models running "
                    "in 16 regions in less than nine months."),
        "locator": "블로그 본문 'Performance Results' 절 마지막 문단 첫 두 문장('MTIA has been deployed…')과 'The software stack' 절 마지막 문장('This allowed us to land…')",
        "relevance": ("추론: 메타 ④ 자체 칩 자리의 직접 근거다. 회사가 자체 AI 가속기 MTIA 를 데이터센터에 배치해 프로덕션 모델을 서빙하고 있다고 밝혀, "
                      "④ 사다리의 '자기 서비스에 배치했을 때' 조건을 1차 출처로 채운다. (선별 확신: 높음)"),
        "channel": "company_statement",
        "conditional_impact": "지금은 유지: 메타 ④ 칩 자리를 받친다. Meta 가 MTIA 배치를 중단하거나 외부 칩만 쓴다고 밝히면 자리를 다시 본다.",
        "horizon": "long — 회사가 MTIA 배치 상태를 바꿔 밝힐 때까지",
        "counter_evidence": ["배치 물량과 전체 추론 연산에서 MTIA 가 맡는 비중은 공시되지 않았다."],
        "unverified": [],
        "change_vs_previous": "new",
        "status": "candidate",
    })
    write_json(src_path, src)
    write_json(ev_path, ev)
    print(f"{EVIDENCE_ID} 후보·{SOURCE_ID} 추가")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
