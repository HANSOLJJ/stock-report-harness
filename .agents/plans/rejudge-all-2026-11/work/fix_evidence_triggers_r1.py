# 1차 리뷰(사실·출처 A)가 지적한 근거 발췌·인용 위치·발행일과 트리거 상태·관찰 문장을 실행 파일에서 고친다
"""
사용: uv run --frozen python -X utf8 .agents/plans/rejudge-all-2026-11/work/fix_evidence_triggers_r1.py <slug> [--dry-run]

고치는 것(점수에 닿지 않음):
- EV-tsmc-041 발췌에 Intel 문단(기사 셋째 문단)을 더하고 인용 위치를 맞춘다.
- 인용 위치 6건(EV-alphabet-037·018, EV-amazon-053, EV-meta-053·054, EV-tsmc-027)과 관측 meta.top_customer_share 의 note 쪽 번호.
- EV-nvidia-009 발행일(8-K 제출일).
- TRG-001 발동(독립 측정 등재 확인), TRG-051 철회(판단이 그 규격에 기대지 않음), 낡은 관찰 문장 11건을 현재 판단에 맞춰 다시 쓴다.
바꾸려는 문자열이 없으면 그 자리에서 멈춘다.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "scripts"))
from scorecard.schema import load_json_strict, write_json  # noqa: E402

INTEL_PARA = ("Intel is conspicuous in its absence in this list of TSMC 2 nm-class nodes. The company currently uses TSMC 3 nm, "
              "specifically the N3B node, for the compute tiles of both its server and client processors. The company is next expected "
              "to use its in-house Intel 18A foundry node that implements RibbonFETs and PowerVia technologies for its frontline server "
              "and client processors.")


def sub(obj: dict, key: str, old: str, new: str, where: str) -> None:
    cur = obj.get(key) or ""
    if old not in cur:
        raise SystemExit(f"[{where}.{key}] '{old[:50]}' 가 없다: {cur[:120]}")
    obj[key] = cur.replace(old, new)


def main() -> int:
    slug = sys.argv[1]
    dry = "--dry-run" in sys.argv
    run = ROOT / "output" / slug
    ev_path, obs_path, trg_path = run / "evidence" / "evidence.json", run / "observations.json", run / "triggers.json"
    ev, obs, trg = load_json_strict(ev_path), load_json_strict(obs_path), load_json_strict(trg_path)
    E = {e["evidence_id"]: e for e in ev["items"]}
    T = {t["trigger_id"]: t for t in trg["items"]}

    # ---- 근거 ----
    e = E["EV-tsmc-041"]
    if INTEL_PARA not in e["excerpt"]:
        e["excerpt"] = e["excerpt"].rstrip() + " … " + INTEL_PARA
    e["locator"] = "기사 첫 문단 앞 세 문장과 셋째 문단(Intel) 앞 세 문장"
    E["EV-alphabet-037"]["locator"] = "기사 8번째 문단 둘째 문장"
    E["EV-alphabet-018"]["locator"] = "기사 7번째 문단"
    sub(E["EV-amazon-053"], "locator", "넷째 문단", "셋째 문단 둘째 문장", "EV-amazon-053")
    sub(E["EV-meta-053"], "locator", "100쪽", "101쪽", "EV-meta-053")
    E["EV-meta-054"]["locator"] = "블로그 둘째 문단 첫 문장, 'A thriving community' 절 첫 문단 둘째·셋째 문장, 같은 절 셋째 문단"
    sub(E["EV-tsmc-027"], "locator", "4번째 문단", "3번째 문단", "EV-tsmc-027")
    if not E["EV-nvidia-009"].get("published_at_utc"):
        E["EV-nvidia-009"]["published_at_utc"] = "2026-09-03T00:00:00Z"
    # 사실·출처 B 2: ARC Prize 순위표의 알리바바 행(2026-10-09 다시 열람, 같은 값)
    e = E["EV-anthropic-053"]
    qwen_row = "Qwen3.8-27B (XHigh) ; 2026-08-14 ; 87.5%, $0.215/task ; 42.4%, $0.447/task ; N/A"
    if qwen_row not in e["excerpt"]:
        e["excerpt"] = e["excerpt"].rstrip() + " … " + qwen_row
    if "Qwen3.8-27B (XHigh)" not in e["locator"]:
        e["locator"] = e["locator"].rstrip() + "·Qwen3.8-27B (XHigh) 행"

    # ---- 관측 note ----
    hit = [o for o in obs["items"] if o.get("observation_id") == "meta.top_customer_share.2025-12-31.rejudge"]
    if len(hit) != 1:
        raise SystemExit("관측 meta.top_customer_share.2025-12-31.rejudge 를 찾지 못했다")
    sub(hit[0], "note", "100쪽", "101쪽", "meta.top_customer_share")

    # ---- 트리거 ----
    t = T["TRG-001"]
    t["status"] = "fired"
    for eid in ("EV-anthropic-049", "EV-anthropic-051", "EV-anthropic-052"):
        if eid not in t["evidence_ids"]:
            t["evidence_ids"].append(eid)
    sub(t, "observation", "알파벳 ② 판단은 4점이고, Gemini 3.8 Flash 출시 뒤에도 프론티어 순위가 바뀌지 않았다는 것을 근거로 든다.",
        "알파벳 ② 판단은 4점이고, 성능 도약 부분(독립 측정에서 회사 기준 2위 안이지만 1위가 아님)·패러다임 적응 통과·표준 선점 통과를 근거로 든다.", "TRG-001")
    t["carry"]["checked_at"] = "2026-10-09"
    t["carry"]["finding"] = ("조건이 기준일 전에 충족됐다. 2026-10-08 열람한 Artificial Analysis 종합 지수 4.3.2판에 Gemini 4 Argon(high) 53, GDPval-AA 2.1판 21위, "
                             "Coding Agent Index 1.5판에 Antigravity CLI - Gemini 4 Argon 64 가 등재돼 있어 독립 측정 등재가 확인된다. 알파벳 ② 는 이 측정으로 "
                             "성능 도약 부분(어느 축에서도 1위가 아님, 세대 격차 없음)으로 매겼고 점수는 4 그대로다(검색 범위: 알파벳 뉴스 2026-10-06~10-08 후보 121건, "
                             "모델 기업 공통 순위표 2026-10-08 열람분).")

    t = T["TRG-007"]
    sub(t, "observation", "마이크로소프트 ① 판단은 5점(Copilot 유료 시트 3,000만, Windows·M365 기본 탑재)이다.",
        "마이크로소프트 ① 판단은 5점이고, 업무 채널(Microsoft 365 상업용 유료 좌석 4.5억 개 초과)의 전환비용 통과와 가격 실측 통과(16분기)를 근거로 들며, "
        "Windows·M365 기본 탑재는 배포 전략이라 회수 루프로 세지 않는다.", "TRG-007")
    t = T["TRG-008"]
    sub(t, "observation", "마이크로소프트 ⑤ 판단은 동맹 등급 +2, 적대 등급 -1(비용형: OpenAI 긴장·Azure 독점 소멸)로 4점이다.",
        "마이크로소프트 ⑤ 판단은 동맹 등급 +2, 적대 등급 −1(비용형: 지역신문 약 400곳의 저작권 소송)로 4점이고, OpenAI 와의 제품 경쟁은 ⑧ 에서 "
        "공급자=경쟁자 의존으로 세며 ⑤ 적대로 세지 않는다.", "TRG-008")
    t = T["TRG-009"]
    sub(t, "observation", "마이크로소프트 ② 판단은 3점이고, Arena 상위권에 자체 모델이 없고 모델을 OpenAI·Anthropic 양쪽에서 조달한다는 것을 근거로 든다.",
        "마이크로소프트 ② 판단은 성능 도약 실패, 패러다임 적응 통과, 표준 선점 통과로 4점이고, 자체 모델이 독립 측정 상위권에 없어 성능 도약이 실패다.", "TRG-009")
    t = T["TRG-011"]
    sub(t, "observation", "메타 ③ 판단은 별도 수익모델 통과, 모방 불가능성 부분, 후발 가속도(AI 귀속 지표의 성장률이 오르는가) 부분(“AI 매출 미공시, 채택 증거 아직 없음”), 문이 닫힌 증거 없음이다.",
        "메타 ③ 판단은 별도 수익모델 통과, 모방 불가능성 실패, 후발 가속도 미확인(같은 정의의 AI 귀속 지표 시계열이 없어 지표 단계 e)이라 점수를 만들지 않고, 문 닫힘은 실패다.", "TRG-011")
    t = T["TRG-013"]
    sub(t, "observation", "지금 NVIDIA ⑤ 판단은 동맹 등급 +1, 적대 등급 -2(구조형 — 주요 고객이 곧 경쟁자)다.",
        "지금 NVIDIA ⑤ 판단은 동맹 등급 +2(CoreWeave·Nebius 지분 동맹), 적대 등급 −2(구조형: 하이퍼스케일 고객 넷과 OpenAI 의 자체 칩 출하)로 3점이고, "
        "중국 수출 통제는 ⑧ 지정학 축에서 센다.", "TRG-013")
    t = T["TRG-015"]
    sub(t, "observation", "NVIDIA ① 판단은 종결되면 업무 채널(Hugging Face 엔터프라이즈)이 생겨 부품 채널 상한(지금 ① 값 2)을 넘길 유일한 경로로 보고, ⑤ 판단은 종결 전인 이 인수를 근거로 세지 않으며, ④ 는 최상단 값 5 다. 2026-09-03 NVIDIA 8-K(Item 8.01)가 이 거래의 발표로 보이나 본문은 열지 않았다.",
        "NVIDIA ① 판단은 4점이고 업무 채널의 CUDA 회수 루프 통과와 가격 실측 부분으로 매겼으며 Hugging Face 인수는 종결 전이라 판정에 넣지 않았다. "
        "⑤ 판단도 종결 전인 이 인수를 근거로 세지 않으며, ④ 는 칩·모델·클라우드·AI 밖 매출 네 자리로 4점이다. 2026-09-03 NVIDIA 8-K(Item 8.01)가 인수 계약 체결을 적는다(본문 확인).", "TRG-015")
    sub(t, "condition", "종결되면 ① 의 부품 채널 상한을 다시 보고,", "종결되면 ① 의 회수 루프·업무 채널 입력과 ④ 자리를 다시 보고,", "TRG-015")
    sub(t, "condition", "① 판단 근거에서 이 거래를 상한을 넘길 경로로 적은 문장을 고친다.", "판단에서 이 거래를 언급한 문장을 고친다.", "TRG-015")
    t = T["TRG-017"]
    sub(t, "observation", "지금 TSMC ② 판단은 최상단 값 5 이고 근거에 N2 양산 시작과 사상 최고 매출총이익률(가격 결정력)이 있다.",
        "지금 TSMC ② 판단은 3점이고(성능 도약은 독립 측정이 없어 부분으로 계산, 패러다임 적응 통과, 표준 선점 실패), 근거에 N2 양산 시작이 있다.", "TRG-017")
    sub(t, "observation", "TSMC ⑧ 판단은 -4 이고 근거에 HPC 매출 비중 66%, NVIDIA 단일 고객 비중 19% 가 있다.",
        "TSMC ⑧ 판단은 −4 이고 점수를 정한 축은 대만 생산 집중이며, 근거에 HPC 매출 비중 66%, NVIDIA 단일 고객 비중 19% 가 있다.", "TRG-017")
    t = T["TRG-020"]
    sub(t, "observation", "지금 Apple ① 판단은 최상단 값 5(25억 대 넘는 설치기반의 소비자 채널)다.",
        "지금 Apple ① 판단은 4점이고, 소비자 채널(25억 대 넘는 활성 기기 설치기반)의 회수 루프 통과와 가격 실측 부분으로 매겼다.", "TRG-020")
    t = T["TRG-041"]
    sub(t, "observation", "지금 NVIDIA ⑧ 판단은 -3 이고, 근거는 매출의 약 절반을 하이퍼스케일 고객이 내는 고객 집중과 공급·캐파 약정이고, 고객의 자체 칩 개발은 ⑤ 적대 등급에서 센다. ⑧ 판단은 오픈소스 확산에 따른 헤지가 이 비중이 실제로 올라와야 점수가 된다고 본다.",
        "지금 NVIDIA ⑧ 판단은 −4 이고 점수를 정한 축은 첨단 칩 생산을 대만에 주요 시설을 둔 TSMC 에 맡긴 공정 의존과 대만 생산 집중이 겹친 경로이며, "
        "하이퍼스케일 고객이 매출의 약 절반을 내는 고객 집중은 고객 비중과 물량을 돌릴 경로로만 세고 고객의 자체 칩 개발은 ⑤ 적대 등급에서 센다.", "TRG-041")
    t = T["TRG-051"]
    t["status"] = "withdrawn"
    sub(t, "observation", "아마존 ② 판단은 4점(표준 선점 경로 통과 — AWS Interconnect 규격의 사실상 표준화, 성능 도약 경로 통과 — Trainium3 에서 OpenAI·Anthropic 이 실제 학습)이다.",
        "아마존 ② 판단은 성능 도약 실패, 패러다임 적응 통과, 표준 선점 실패로 3점이고, AWS Interconnect 는 AI 에 귀속되는 규격이 아니라 표준 선점으로 세지 않는다.", "TRG-051")
    t["carry"]["checked_at"] = "2026-10-09"
    t["carry"]["finding"] = ("아마존 ② 판단이 AWS Interconnect 규격에 더는 기대지 않아(AI 귀속 규격이 아님) 정식 출시가 확인돼도 ② 입력이 바뀌지 않으므로 철회한다"
                             "(검색 범위: 아마존 뉴스 2026-10-06~10-08, 공시 2026-09-02~10-08).")
    t = T["TRG-091"]
    sub(t, "observation", "메타 ② 판단은 지금 점수 4 로 남아 있고 이번 실행에서 세 경로(성능 도약·패러다임 적응·표준 선점) 입력으로 다시 매긴다.",
        "메타 ② 판단은 성능 도약 실패, 패러다임 적응 통과, 표준 선점 통과(PyTorch)로 4점이고, 이 상거래 표준은 다른 회사의 채택이 확인되지 않아 판단에 쓰지 않았다.", "TRG-091")

    # 재무 계산 리뷰가 더 지목한 9건과 기준일 표기 2건
    t = T["TRG-014"]
    sub(t, "observation", "지금 NVIDIA ② 판단은 최상단 값 5 이고, Rubin 의 성능 수치는 NVIDIA 발표로만 근거에 들어 있다.",
        "지금 NVIDIA ② 판단은 4점이고(성능 도약은 MLPerf 독립 측정으로 통과하되 세대 격차는 없음, 패러다임 적응·표준 선점 통과), "
        "Rubin 의 성능 수치 가운데 NVIDIA 발표분은 방증으로만 둔다.", "TRG-014")
    for tid in ("TRG-037", "TRG-038"):
        sub(T[tid], "observation", "Anthropic ⑤ 판단의 적대 등급은 -1(비용형)이다.",
            "Anthropic ⑤ 판단의 적대 등급은 −2(구조형: 큰 고객 둘이 경쟁사 소유가 됨)이고, 정부 거래 배제나 규제 조사 같은 비용형 적대는 그 등급을 바꾸지 않는다.", tid)
    t = T["TRG-062"]
    sub(t, "observation", "OpenAI ⑤ 판단은 동맹 등급 +1, 적대 등급 -3(다발형)이고 이 소송이 다발형 근거의 하나다.",
        "OpenAI ⑤ 판단은 동맹 등급 +1, 적대 등급 −1(비용형: 전선은 많으나 모두 소송·조사라 비용형)로 3점이고 이 소송은 비용형 근거의 하나다.", "TRG-062")
    t = T["TRG-065"]
    sub(t, "observation", "Anthropic ① 판단은 4 이고, 주채널은 업무(기업 고객·전환비용), 보조 증거는 거래 채널의 가격 결정력이다 — OpenRouter 매출의 약 46% 를 가져간다는 보도가 있고, 토큰 점유율과 평균 단가는 기준일 이전 원문을 찾지 못했다.",
        "Anthropic ① 판단은 1점이고, 가장 강한 채널은 거래 채널(사용량 기반 API)이며 회수 루프 실패·전환비용 부분·대체 공급 실패·가격 실측 실패(정가 인하)로 매겼다. "
        "OpenRouter 매출 비중 보도는 참고로만 둔다.", "TRG-065")
    t = T["TRG-066"]
    sub(t, "observation", "OpenAI ③ 판단은 후발 가속도만 통과(ARR 이 2~4월 $25B 정체 뒤 7월 $40B 로 재가속)해 2 이고, ① 판단은 4(주채널 소비자, 거래 채널은 가격 결정력 없음), ⑥ 은 -4(post-money $852B ÷ 최근 1년 보정 매출 약 39배), ⑨ 는 -2(비상장 경로)다.",
        "OpenAI ③ 판단은 별도 수익모델·후발 가속도 통과(연환산 매출이 2~4월 $25B 정체 뒤 7월 $40B 로 재가속)로 3점이고, ① 판단은 0점(가장 강한 채널은 소비자, "
        "회수 루프 실패·대체 공급 실패·가격 실측 부분, 전환비용 미확인), ⑥ 은 −4(비상장 경로), ⑨ 는 −2(비상장 경로)다.", "TRG-066")
    t = T["TRG-070"]
    sub(t, "observation", "Anthropic ⑧ 판단은 -3 이고 근거는 컴퓨트 100% 외부에 공급자가 모두 경쟁자라는 것이다(고객 쪽 집중은 아직 근거에 없다).",
        "Anthropic ⑧ 판단은 −3 이고 점수를 정한 축은 공급 축(컴퓨트를 모델 경쟁자 넷에게서 빌리는 구조와 그 약정)이며, 고객 축은 매출의 약 4분의 1 이 고객 두 곳에서 "
        "나온다는 보도로 −2 를 따로 적는다.", "TRG-070")
    t = T["TRG-071"]
    sub(t, "observation", "Anthropic ④ 판단은 4, ⑧ 판단은 -3(컴퓨트 100% 외부)이다.",
        "Anthropic ④ 판단은 모델·AI 유통 두 자리로 2점, ⑧ 판단은 −3(컴퓨트를 모델 경쟁자 넷에게서 빌리는 공급 축)이다.", "TRG-071")
    t = T["TRG-077"]
    sub(t, "observation", "지금 테슬라 ③ 판단은 모방 불가능성 실패·별도 수익모델 통과·후발 가속도 통과로 3이다.",
        "지금 테슬라 ③ 판단은 모방 불가능성 실패·별도 수익모델 통과·후발 가속도 부분 통과(FSD 활성 이용 수의 직전 분기 대비 성장률 약 16.4% → 15.6%)로 3이다.", "TRG-077")
    t = T["TRG-079"]
    sub(t, "observation", "알리바바 ② 판단은 4(두 경로)다.", "알리바바 ② 판단은 패러다임 적응 한 경로 통과로 3점이다.", "TRG-079")
    sub(t, "observation", "지금 알리바바 ⑤ 판단은 동맹 등급 +1·적대 등급 -1(비용형)로 3이고 근거에 Anthropic 의 증류 주장이 이미 들어 있다.",
        "지금 알리바바 ⑤ 판단은 동맹 등급 +1·적대 등급 −1(비용형: EU 디지털서비스법 벌금)로 3이고 Anthropic 의 증류 주장은 비용형 재료로 이미 들어 있다.", "TRG-079")
    t = T["TRG-005"]
    sub(t, "observation", "기준일(2026-10-06) 현재", "기준일(2026-10-08) 현재", "TRG-005")
    t = T["TRG-043"]
    sub(t, "observation", "Apple 은 iOS 27 의 새 Siri 를 2026년 9월에 낼 예정이었으나, 기준일(2026-10-06)까지 출시도 공식 연기도 확인되지 않았다. 지금 Apple ③ 판단은 통과점 1(③ 값 2)이다. 모방 불가능성은 실패(설치기반은 ① 에서 이미 셈), 별도 수익모델은 통과, 후발 가속도는 실패(Siri 개편이 2년 연기됐고 고난도 추론은 Gemini 에 외주)다.",
        "Apple 은 iOS 27 의 새 Siri 를 2026년 9월에 내겠다고 했고, 2026-09-14 iOS 27 과 함께 Siri AI 를 영어 베타(대기자 등록, EU 미제공)로 배포했다. 지금 Apple ③ 판단은 "
        "통과점 1(③ 값 2)이다. 모방 불가능성은 실패(설치기반은 ① 에서 이미 셈), 별도 수익모델은 통과, 후발 가속도는 AI 귀속 지표가 없어 지표 단계 e 이고 새 Siri 가 2년 "
        "미뤄진 뒤 채택 지표 없이 베타로 나와 지연 조항(지연은 감속)으로 실패다.", "TRG-043")

    if dry:
        print("dry-run: 바꿀 문자열을 모두 찾았다"); return 0
    write_json(ev_path, ev)
    write_json(obs_path, obs)
    write_json(trg_path, trg)
    print("근거 8건·관측 1건·트리거 24건 고침")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
