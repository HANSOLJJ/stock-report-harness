# 확인 리뷰 L4·L5 — 트리거 조건·재검토 칸에 남은 지난 점수와 옛 ① 이름, TRG-077 의 Waymo 대수를 현재 판단에 맞춘다
"""
사용: uv run --frozen python -X utf8 .agents/plans/rejudge-all-2026-11/work/fix_triggers_r2.py <slug> [--dry-run]
바꾸려는 문자열이 없으면 멈춘다.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "scripts"))
from scorecard.schema import load_json_strict, write_json  # noqa: E402


def sub(obj: dict, key: str, old: str, new: str, where: str) -> None:
    cur = obj.get(key) or ""
    if old not in cur:
        raise SystemExit(f"[{where}.{key}] '{old[:50]}' 가 없다")
    obj[key] = cur.replace(old, new)


def main() -> int:
    slug = sys.argv[1]
    dry = "--dry-run" in sys.argv
    p = ROOT / "output" / slug / "triggers.json"
    trg = load_json_strict(p)
    T = {t["trigger_id"]: t for t in trg["items"]}
    R = {k: T[k]["recheck"] for k in T}

    sub(R["TRG-025"], "what", "알리바바 ④ 판단(지금 4, 클라우드 성장·AI 제품·해외 데이터센터로 폭을 셈)", "알리바바 ④ 판단(지금 5, 칩·모델·클라우드·AI 유통·커머스 다섯 자리)", "TRG-025")
    sub(R["TRG-025"], "what", "알리바바 ② 판단(지금 4, 프론티어 미달로 적음)", "알리바바 ② 판단(지금 3, 성능 도약 실패)", "TRG-025")
    sub(R["TRG-026"], "what", "알리바바 ⑧ 판단(지금 -4)", "알리바바 ⑧ 판단(지금 −3)", "TRG-026")
    sub(R["TRG-027"], "what", "알리바바 ④ 판단(지금 4)이 센 사업 부문과 해외 배치", "알리바바 ④ 판단(지금 5, 다섯 자리)이 센 자리와 해외 배치", "TRG-027")
    sub(R["TRG-030"], "what", "테슬라 ④ 판단(지금 3, 배치 전인 Optimus·Terafab 은 폭에서 뺐다)", "테슬라 ④ 판단(지금 4, 배치 전인 Optimus·Terafab 은 자리에서 뺐다)", "TRG-030")
    sub(R["TRG-030"], "what", "테슬라 ② 판단(지금 3, 성능 판정 불가·적응 경로 통과)", "테슬라 ② 판단(지금 3, 성능 도약 실패·패러다임 적응 통과)", "TRG-030")
    sub(R["TRG-031"], "what", "테슬라 ③ 판단(지금 3, 후발 가속도는 FSD 구독 148만·+56% 로 이미 통과)", "테슬라 ③ 판단(지금 3, 후발 가속도는 FSD 활성 이용 수의 직전 분기 대비 성장률로 부분)", "TRG-031")
    sub(T["TRG-034"], "condition", "스페이스X ④ 판단은 이미 범위 맨 위다", "스페이스X ④ 판단은 4점이다", "TRG-034")
    sub(R["TRG-034"], "what", "스페이스X ② 판단(지금 4, 성능·적응 두 경로)", "스페이스X ② 판단(지금 3, 패러다임 적응 한 경로)", "TRG-034")
    sub(R["TRG-035"], "what", "스페이스X ① 판단(지금 3, Starlink 는 가격 결정력이 있으나 사용자 간 연결이 약하고 X 는 이탈·수익화가 약함)",
        "스페이스X ① 판단(지금 2, 소비자 채널의 회수 루프 부분·전환비용 실패·대체 공급 부분·가격 실측 실패)", "TRG-035")
    sub(T["TRG-062"], "condition", "(적대 등급은 이미 가장 낮은 다발형이라 등급은 그대로이고 근거 문장을 고친다)", "(적대 등급은 지금 비용형 −1 이라 구조형이면 −2 로 내린다)", "TRG-062")
    sub(T["TRG-065"], "condition", "①(네트워크 효과)의 보조 증거(가격 결정력)가 약해진 것으로 보고 한 단계 내릴지 검토한다. 유지되면 가격 결정력을 재확인한 것으로 근거 문장을 갱신한다. ①은 가장 강한 채널이 점수를 정하므로 보조 증거만 약해지고 업무 채널이 그대로면 판단은 유지될 수 있다.",
        "①(락인과 가격결정력)의 가격 실측 방증이 약해진 것으로 보고 근거 문장을 갱신한다. ① 의 가격 실측은 정가 인하가 실패를 정하므로 점유율 변화만으로 판단이 움직이지 않는다.", "TRG-065")
    sub(T["TRG-066"], "condition", "①(네트워크 효과): 가격 인상 뒤 OpenRouter 점유율·평균 단가가 유지되면 거래 채널의 가격 결정력이 실측된 것으로 보고 근거를 고치고, 이탈하면 가격 결정력 없음 판단을 재확인한다. 가장 강한 채널(소비자)이 점수를 정하므로 거래 채널 변화만으로 판단이 움직이지 않을 수 있다.",
        "①(락인과 가격결정력): 가격 인상 뒤 OpenRouter 점유율·평균 단가는 거래 채널의 방증으로만 적는다. 가장 강한 채널(소비자)의 네 질문이 점수를 정하므로 거래 채널 변화만으로 판단이 움직이지 않는다.", "TRG-066")
    sub(T["TRG-077"], "observation", "Waymo(약 3,000대·주 50만 유료 탑승·10개 도시)", "Waymo(4,000대 넘게·주 50만 유료 탑승·10개 도시)", "TRG-077")
    sub(R["TRG-079"], "what", "알리바바 ② 판단(지금 4)", "알리바바 ② 판단(지금 3)", "TRG-079")

    if dry:
        print("dry-run: 바꿀 문자열을 모두 찾았다"); return 0
    write_json(p, trg)
    print("트리거 12건 고침")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
