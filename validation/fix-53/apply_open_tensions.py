# FIX-53: 2차 리뷰 C 의 RC-02·RC-03·RC-05 를 규칙 v1.7 open_tensions 에 2026-11 재검토 긴장으로 등록한다 (점수 무영향)
"""AGENTS.md 리뷰 범위 — 승계 판단 예외는 체크리스트 fail 이 **규칙 파일 긴장 목록에 재검토 시점과 함께 등록**됐을 때만
pass 를 막지 않는다. 그 목록을 만든다. 판정은 하지 않는다 — 방향과 재검토 조건만 적는다.

재실행해도 같은 결과가 나온다. 파일 줄끝은 원래 것을 유지한다(HASH-EOL).
"""
from __future__ import annotations

import io
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from scorecard.rules import load_rules  # noqa: E402
from scorecard.schema import validate_rules  # noqa: E402

RULES = ROOT / "scorecard" / "rules" / "v1.7.json"
RUN = ROOT / "scorecard" / "runs" / "ai-scorecard-2026-09-obsreg"
REVIEW = "obsreg 2차 리뷰 C(codex 새 세션, review-obsreg b2825ac)"

TENSIONS = [
    {
        "id": "TEN-RC-02",
        "status": "open",
        "recheck_at": "2026-11",
        "review_finding": f"RC-02 · {REVIEW} · 체크리스트 Q02·Q16 fail",
        "judgment_ids": ["anthropic.F1"],
        "subject": "anthropic F1 — 주채널을 업무로 적고도 개인 사용자 절대수 열세로 5점을 막는다",
        "tension": ("anthropic.F1(승계 4점) 근거가 `[주채널: 업무 — 기업 고객·전환비용]` 이라 적고 `5점이 아닌 이유: 개인 사용자 "
                    "절대수가 OpenAI(WAU 9억)에 크게 열세` 로 최고점을 막는다. 채점규칙 398행 별표 A `가장 강한 락인으로 매긴다`·"
                    "400행 `얕은 채널이 깊은 채널을 깎지 않는다` 와 어긋나고, 같은 업무 채널의 microsoft.F1 은 5 다."),
        "direction": "상향 가능(4 → 5 검토). 4 가 옳은지 5 가 옳은지는 이 등록이 판정하지 않는다.",
        "rechecker": ("**비 Claude 세션이 재판정한다.** 이 판단은 anthropic 점수이고 조율자(설계진행)·worker 가 Claude 라 "
                      "이해상충이다(SRC-v15-html·md·rule·handover 이해상충 고지와 같은 사유)."),
        "why_carried_exception": ("승계 판단의 기존 논리이고 이번 실행이 F1 의 잣대를 바꾸지 않았다. 재검토 시점과 함께 등록했으므로 "
                                  "AGENTS.md 리뷰 범위 — 승계 판단 예외에 해당한다."),
        "score_impact_now": "없다.",
        "source_lines": ["채점규칙 398행", "채점규칙 400행"],
    },
    {
        "id": "TEN-RC-03",
        "status": "open",
        "recheck_at": "2026-11",
        "review_finding": f"RC-03 · {REVIEW} · 체크리스트 Q03·Q20 fail",
        "judgment_ids": ["nvidia.F5", "openai.F5.impl48", "amazon.F5", "meta.F5", "anthropic.F5.impl48"],
        "decision_id": "C-08",
        "subject": "C-08 — 별표 H 이탈 조건의 허용·제외 기준이 F5 전사에 통일되지 않았다",
        "tension": ("채점규칙 239행 별표 H 3문 `떠날 수 있으면 ⑤ 동맹 제외` 인데 같은 별표 예시표에서 NVIDIA ← 하이퍼스케일러(275행, "
                    "떠날 수 있음 → 불인정)는 제외하고 OpenAI → MS·Oracle·NVIDIA(276행)·Amazon → Bedrock 18사(277행)·"
                    "Meta ← 광고주(278행)는 떠날 수 있어도 가점한다. Anthropic → 3사(273행)는 지분으로 묶여 허용. F5-IMPL-48 은 "
                    "받은 투자·조달을 뺐지만 남은 제휴를 어떤 이탈 기준으로 허용하는지는 전사에 통일하지 않았다."),
        "direction": "기준 통일 후 전사 재대입. 어느 쪽으로 통일하느냐에 따라 F5 A 가 오르거나 내릴 수 있다 — 방향 미정.",
        "rechecker": "C-08 결정(사용자) 뒤 비 Claude 세션이 전사 재대입.",
        "why_carried_exception": ("승계 판단 다수의 기존 논리다. 단 A+2 엄격 읽기는 이번 실행이 바꾼 잣대라 이 긴장과 별개로 FIX-53 2단계 "
                                  "(+2 여섯 회사 재판정, 비 Claude 두 세션)에서 전사에 댄다 — 그 부분은 예외가 아니다."),
        "score_impact_now": "없다.",
        "source_lines": ["채점규칙 239행", "채점규칙 273~278행"],
    },
    {
        "id": "TEN-RC-05",
        "status": "open",
        "recheck_at": "2026-11",
        "review_finding": f"RC-05 · {REVIEW} · 체크리스트 Q01·Q21 fail",
        "judgment_ids": ["nvidia.F5", "nvidia.F8"],
        "subject": "nvidia F5·F8 — 고객 40% 자체 칩 이탈이라는 같은 속성이 F5 H -2 와 F8 -3 에 반복된다",
        "tension": ("nvidia.F5(H -2) 근거 `매출 약 40%인 하이퍼스케일러 4곳이 전원 자체 칩 개발 중` 과 nvidia.F8(-3) 근거 `고객 40% "
                    "집중 + 전원 자체칩 개발으로 방향성 악화` 가 같은 속성이다. 채점규칙 262행 금지선은 `같은 관계` 가 아니라 "
                    "`같은 속성` 이다. F5 는 구조형 적대, F8 은 집중·대체 불가 위험으로 갈라 설명돼 있지 않다."),
        "direction": ("속성 분리 설명 또는 한쪽 감점 축소. 수동 판단에 배분이 없어 그 속성이 -3·-2 중 몇 점을 만들었는지 **중복 폭을 "
                      "확인하지 못했다.**"),
        "rechecker": "2026-11 재채점 때 판단자(비 Claude 세션 권장 — Anthropic 과 무관하나 같은 잣대 대조를 위해).",
        "why_carried_exception": "승계 판단의 기존 논리이고 이번 실행이 F5 H·F8 잣대를 바꾸지 않았다.",
        "score_impact_now": "없다.",
        "source_lines": ["채점규칙 262행"],
    },
]


def main() -> int:
    raw = io.open(RULES, encoding="utf-8", newline="").read()
    nl = "\r\n" if "\r\n" in raw else "\n"
    rules = json.loads(raw)
    rules["open_tensions"] = TENSIONS
    validate_rules(rules)
    out = json.dumps(rules, ensure_ascii=False, indent=2) + ("\n" if raw.endswith("\n") else "")
    io.open(RULES, "w", encoding="utf-8", newline="").write(out.replace("\n", nl))
    run_path = RUN / "run.json"
    rraw = io.open(run_path, encoding="utf-8", newline="").read()
    old = json.loads(rraw)["rule_hash"]
    new = load_rules("v1.7").hash
    if old != new:
        io.open(run_path, "w", encoding="utf-8", newline="").write(rraw.replace(old, new))
    print("open_tensions:", [t["id"] for t in TENSIONS], f"rule_hash {old[:12]} -> {new[:12]}")
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    sys.exit(main())
