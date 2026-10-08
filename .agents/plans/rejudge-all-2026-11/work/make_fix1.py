# 1차 리뷰 발견(N1~N4·L1·L10·L14)을 반영할 제안 파일을 현재 판단에서 생성한다 — work/judge-fix1/<F>-<company>.json
"""
사용: uv run --frozen python -X utf8 .agents/plans/rejudge-all-2026-11/work/make_fix1.py <slug>

현재 judgments.json 의 판정·올릴·내릴 칸을 읽어 필요한 줄만 바꾼 전체 목록을 제안 파일로 쓴다.
바꾸려는 줄이 없으면 그 자리에서 멈춘다(문장이 달라졌다는 뜻이므로 손으로 다시 본다).
반영은 apply_judgments.py --dir judge-fix1 로 한다.
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent / "judge-fix1"


def load(slug: str) -> dict[str, dict]:
    p = ROOT / "output" / slug / "judgments.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    return {f'{j["factor"]}:{j["company_id"]}': j for j in d["items"]}


def replace_line(lines: list[str], needle: str, new: str, where: str) -> list[str]:
    hits = [i for i, l in enumerate(lines) if needle in l]
    if len(hits) != 1:
        raise SystemExit(f"[{where}] '{needle[:40]}…' 가 {len(hits)}번 나온다")
    out = list(lines)
    out[hits[0]] = new
    return out


def drop_line(lines: list[str], needle: str, where: str) -> list[str]:
    hits = [i for i, l in enumerate(lines) if needle in l]
    if len(hits) != 1:
        raise SystemExit(f"[{where}] 지울 줄 '{needle[:40]}…' 가 {len(hits)}번 나온다")
    return [l for i, l in enumerate(lines) if i != hits[0]]


def sub_in_line(lines: list[str], needle: str, old: str, new: str, where: str) -> list[str]:
    hits = [i for i, l in enumerate(lines) if needle in l]
    if len(hits) != 1:
        raise SystemExit(f"[{where}] '{needle[:40]}…' 가 {len(hits)}번 나온다")
    line = lines[hits[0]]
    if old not in line:
        raise SystemExit(f"[{where}] 줄 안에 '{old}' 가 없다: {line}")
    out = list(lines)
    out[hits[0]] = line.replace(old, new)
    return out


def write(factor: str, company: str, spec: dict) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{factor}-{company}.json").write_text(json.dumps(spec, ensure_ascii=False, indent=2), encoding="utf-8")


F7_SHARED_OLD = "그 비율이 절반 이상이면 큼, 절반 미만이면 작음으로 가르며"
F7_SHARED_NEW = ("가로축은 조달 의존 고객(자기 영업이익이 아니라 투자 유치나 차입으로 대금을 내는 고객)의 연간 약정과 실제 매출 몫을 "
                 "최근 1년 매출에 견주어 판정하고, 규칙 ⑦ 에 따라 큼·작음에 수치 임계를 두지 않는다. 조달 의존 고객이 확인되고 그 몫을 "
                 "작게 좁힐 실측이 없으면 큼, 확인된 몫이 매출에 견줘 작거나 조달 의존 고객이 확인되지 않으면 작음이며, 열네 회사에 같은 잣대를 댄다.")

# 회사별 가로축 판정 줄: (찾을 조각, 바꿀 조각)
F7_COMPANY_SUBS: dict[str, list[tuple[str, str, str]]] = {
    "alphabet": [("나눈 9.0% 로", "나눈 9.0% 로, 절반에 크게 못 미쳐 가로축은 작음이다.",
                  "나눈 9.0% 다. 확인된 조달 의존 고객의 약정이 매출에 견줘 작아 가로축은 작음이다.")],
    "amazon": [("상한도 7.8% 라", "상한도 7.8% 라 절반에 크게 못 미쳐 가로축은 작음이다.",
                "상한도 7.8% 라, 확인된 조달 의존 고객의 약정이 매출에 견줘 작아 가로축은 작음이다."),
               ("두 회사 약정을 합친", "약 $496B(주로 AWS 몫)의 절반 가까이라", "약 $496B(주로 AWS 몫)의 48% 에 이르러")],
    "meta": [("수백만 광고주의 광고비이고", "조달 의존 고객이 매출의 절반에 이를 근거가 없으므로 가로축은 작음이다.",
              "조달 의존 고객이 확인되지 않아 가로축은 작음이다.")],
    "microsoft": [("두 회사 합계가 매출의 16.3% 다", "이 상한도 절반에 크게 못 미쳐 가로축은 작음이다.",
                   "이 상한으로도 확인된 조달 의존 고객의 약정이 매출에 견줘 작아 가로축은 작음이다.")],
    "tsmc": [("최대 고객 NVIDIA(2025년 매출의 19%)", "조달 의존 고객이 매출의 절반에 이를 근거가 없으므로 가로축은 작음이다.",
              "조달 의존 고객이 확인되지 않아 가로축은 작음이다.")],
    "alibaba": [("FY2026 클라우드 인텔리전스 그룹 매출", "클라우드 고객 전부를 조달 의존 고객으로 놓아도 절반에 못 미쳐 가로축은 작음이다.",
                 "클라우드 고객 전부를 조달 의존 고객으로 놓아도 그 몫이 매출에 견줘 작아 가로축은 작음이다.")],
    "apple": [("매출의 10% 이상을 낸 고객이 없고(10-K 2025-09-27)", "조달 의존 고객이 매출의 절반에 이를 근거가 없으므로 가로축은 작음이다.",
               "조달 의존 고객이 확인되지 않아 가로축은 작음이다."),
              ("매출의 10% 이상을 낸 고객이 없고(10-K 2025-09-27)", "(10-K 2025-09-27)", "(10-K 2025-09-27, 공시 의무상 해당 고객이 없다고 읽은 추론)")],
    "palantir": [("2026년 상반기 매출의 52% 가 정부 고객", "기업 고객 전부를 조달 의존 고객으로 놓아도 절반에 못 미쳐 가로축은 작음이다.",
                  "정부 고객은 자기 예산으로 사고 기업 고객 가운데 투자 유치나 차입으로 대금을 내는 고객은 확인되지 않아 가로축은 작음이다.")],
    "spacex-xai": [("나눈 65.1% 로", "나눈 65.1% 로, 절반을 넘어 가로축은 큼이다.",
                    "나눈 65.1% 로, 조달 의존 고객의 약정이 매출의 대부분에 이르러 가로축은 큼이다.")],
    "oracle": [("나눈 83.6% 로", "나눈 83.6% 로, 절반을 크게 넘어 가로축은 큼이다.",
                "나눈 83.6% 로, 조달 의존 고객의 약정이 매출과 맞먹어 가로축은 큼이다.")],
    "openai": [("조달 의존 고객인 AI 스타트업은 그 기업 매출의 일부라", "조달 의존 고객 몫은 절반에 못 미치고 가로축은 작음이다.",
                "조달 의존 고객의 몫이 크다는 근거가 없어 가로축은 작음이다.")],
    # anthropic·tesla 는 공통 줄만 있다
}

F7_REASON = "⑦ 가로축에서 규칙이 금지한 수치 임계('절반')를 빼고 측정값과 질적 잣대만 남긴다(1차 리뷰 규칙 일관성 N1·Q02)"


def main() -> int:
    slug = sys.argv[1]
    J = load(slug)
    if OUT.exists():
        shutil.rmtree(OUT)

    # ---------- N1: ⑦ 14건 ----------
    for key, j in J.items():
        if j["factor"] != "F7":
            continue
        company = j["company_id"]
        ev = replace_line(j["evidence"], F7_SHARED_OLD, F7_SHARED_NEW, f"F7:{company}")
        for needle, old, new in F7_COMPANY_SUBS.get(company, []):
            ev = sub_in_line(ev, needle, old, new, f"F7:{company}")
        spec = {"changes": {}, "evidence_after": ev, "reason": F7_REASON}
        if company == "alphabet":
            spec["evidence_down_after"] = sub_in_line(j["evidence_down"], "Google Cloud 매출 백로그의 40%", "Google Cloud 매출 백로그의 40%",
                                                      "구글이 공개한 매출 백로그의 40%", "F7:alphabet")
            spec["reason"] += ". 백로그 표현을 인용 원문(EV-alphabet-042, 구글이 공개한 매출 백로그)대로 고친다(사실·출처 리뷰 A 과제 3)"
        if company == "apple":
            spec["reason"] += ". 10% 고객 부재가 공시 의무에서 읽은 추론임을 표시한다(사실·출처 리뷰 A 과제 16)"
        if company == "nvidia":
            ev = replace_line(ev, "NVIDIA ⑦ 은 조달 의존 고객 비중 작음",
                              "NVIDIA ⑦ 은 조달 의존 고객 비중 큼, 내 돈이 돌아옴 칸이라 −2 이며, 비중이 큰 쪽에서는 세로축이 점수를 가르지 않는다.",
                              "F7:nvidia")
            ev = replace_line(ev, "하이퍼스케일 매출 $48.7B(50.6%)와 엣지 컴퓨팅 매출 $7.2B(7.5%)를 더한 58.1%",
                              "하이퍼스케일 매출 $48.7B(50.6%)와 엣지 컴퓨팅 매출 $7.2B(7.5%)는 ACIE 밖이지만, ACIE 안에는 회사가 장기 인프라 계약과 "
                              "투자등급 조달 여력을 확보하지 못한다고 적은 AI 클라우드·AI 모델 회사가 들어 있고 그 몫을 상한 아래로 좁힐 실측이 없다. "
                              "작음은 감점을 덜어 주는 판정이라 실측이 있어야 하므로(규칙 2.1) 가로축을 큼으로 둔다.",
                              "F7:nvidia")
            ev = replace_line(ev, "이 읽기는 하이퍼스케일 고객이 자기 영업이익으로 사는",
                              "하이퍼스케일 고객은 자기 영업이익으로 사는 대형 클라우드 사업자이지만, 같은 10-Q 는 2026년 2분기에 한 회사를 ACIE 에서 "
                              "하이퍼스케일로 옮겼다고 적었고 그 회사의 이름과 매출은 공시되지 않아 하이퍼스케일 안의 조달 의존 몫도 미확인이다.",
                              "F7:nvidia")
            spec = {"changes": {"funding_dependent_share": "large"}, "evidence_after": ev,
                    "reason": F7_REASON + ". NVIDIA 는 조달 의존 몫을 상한 41.9% 아래로 좁힐 실측이 없어 큼으로 판정한다(규칙 2.1)"}
        write("F7", company, spec)

    # ---------- N2: meta ④ ----------
    j = J["F4:meta"]
    ev = replace_line(j["evidence"], "메타는 모델·AI 유통·AI 밖 매출 세 자리를 가져 3점이다.",
                      "메타는 자체 칩·모델·AI 유통·AI 밖 매출 네 자리를 가져 4점이다.", "F4:meta")
    ev = replace_line(ev, "자체 칩 자리는 미확인이다",
                      "자체 칩 자리는 자체 AI 가속기 MTIA 로 선다. Meta 는 MTIA 를 데이터센터에 배치해 프로덕션 모델을 서빙하고 있다고 밝혔고, "
                      "외부 분석도 MTIA 를 Meta 가 대규모로 돌리는 추론에 맞춘 자체 ASIC 으로 적는다. 배치 물량은 공시되지 않았다.", "F4:meta")
    up = ["Meta 는 자체 AI 가속기 MTIA 를 데이터센터에 배치해 프로덕션 모델을 서빙하고 있으며, 첫 실리콘에서 16개 리전의 프로덕션 모델 가동까지 "
          "9개월이 걸리지 않았다. [EV-meta-056]",
          "Meta 의 MTIA 는 Google Ironwood TPU·Amazon Trainium·Microsoft Maia 200 과 함께 각 회사가 대규모로 돌리는 모델·추론에 맞춘 자체 ASIC 이다. "
          "[EV-nvidia-038]", *j["evidence_up"]]
    write("F4", "meta", {"changes": {"score": 4}, "evidence_after": ev, "evidence_up_after": up,
                         "reason": "같은 확정 근거(EV-nvidia-038)를 다른 다섯 판단이 Meta 의 MTIA 운용으로 읽었고 Meta 공식 블로그가 데이터센터 배치·프로덕션 서빙을 밝히므로 "
                                   "칩 자리를 센다(1차 리뷰 규칙 일관성 N2·Q03)"})

    # ---------- N3: alibaba ⑤ ----------
    j = J["F5:alibaba"]
    ev = replace_line(j["evidence"], "적대 등급 −1 은 비용형이다. 알리바바는 미 국방부의 1260H",
                      "적대 등급 −1 은 비용형이다. 유럽연합 집행위원회가 디지털서비스법 위반으로 €550M 벌금을 물렸고 알리바바는 그 충당금을 "
                      "2026년 6월 분기 영업이익에 반영했다. 벌금은 져도 본업인 중국 커머스·클라우드 수요가 남는 비용형이다.", "F5:alibaba")
    ev = replace_line(ev, "⑧ 에서 센 것, 곧 미국 첨단 GPU 수출 금지와 1260H 등재로 막히는 미국 조달 접근",
                      "⑧ 에서 센 것, 곧 미국 첨단 GPU 수출 금지, 1260H 등재로 막히는 미 국방부 조달 접근과 그 등재 삭제 소송, VIE 구조라는 지정학 의존은 "
                      "미중 규제라 ⑧ 의 지정학 축에서만 세고 여기서는 세지 않는다. 미 하원을 통과한 Remote Access Security Act 는 법률 전이라 점수에 넣지 않는다.",
                      "F5:alibaba")
    down = replace_line(j["evidence_down"], "알리바바는 미 국방부의 중국 군사기업 목록에 올랐고",
                        "유럽연합 집행위원회가 디지털서비스법 위반으로 물린 €550M 벌금의 충당금이 2026년 6월 분기 영업이익을 줄였다. [EV-alibaba-052]",
                        "F5:alibaba")
    write("F5", "alibaba", {"changes": {}, "evidence_after": ev, "evidence_down_after": down,
                            "reason": "1260H 등재는 미중 규제라 ⑧ 지정학 축에서만 세고, ⑤ 적대 −1 은 확정 근거의 EU 디지털서비스법 벌금 €550M 으로 받친다(1차 리뷰 규칙 일관성 N3·Q01·Q21)"})

    # ---------- N4: tsmc ⑤ ----------
    j = J["F5:tsmc"]
    ev = replace_line(j["evidence"], "동맹 등급 +1 은 고객 동맹에서 나온다.",
                      "동맹 등급 +1 은 협력사와 함께 만든 OIP 설계 생태계의 공동개발에서 나온다. EDA·IP 협력사는 TSMC 공정마다 설계 흐름·IP·PDK 를 TSMC 와 "
                      "함께 만들어 왔고 그 협력사가 TSMC 플랫폼을 떠난 실측이 없다. Apple·NVIDIA·AMD·MediaTek 과 하이퍼스케일러의 자체 칩이 TSMC 공정에 "
                      "들어와 있고 일부 고객이 선급금을 내는 관계는 판매라 동맹 등급에 넣지 않는다.", "F5:tsmc")
    ev = replace_line(ev, "+2 는 서지 않는다. TSMC 는 고객에 투자하지 않아 지분 동맹이 없고",
                      "+2 는 서지 않는다. TSMC 는 고객에 투자하지 않아 지분 동맹이 없다. 경쟁 파운드리 Intel 은 서버·클라이언트 프로세서의 compute tile 을 TSMC N3B 로 "
                      "만들지만 2026년 초 자사 18A 공정으로 자사 제품을 대량 생산하기 시작해 이미 자기 대체품을 출하하고 있으므로, 떠날 수 있는 상대라 경쟁사 편입 "
                      "조항으로 세지 않는다. 하이퍼스케일러 칩은 NVIDIA 의 경쟁 칩이지 TSMC 의 경쟁사가 아니다.", "F5:tsmc")
    ev = replace_line(ev, "Intel CEO 가 TSMC 를 파트너라고 했지만",
                      "Intel CEO 는 TSMC 를 파트너라고 했고 Intel 의 compute tile 위탁은 확인되지만 그 물량은 공시되지 않았다(미확인). Intel 이 18A 로 옮기지 않고 "
                      "TSMC 위탁을 늘린 사실이 공시로 확인되면 경쟁사 편입 조항을 다시 본다.", "F5:tsmc")
    up = [l for l in j["evidence_up"] if "[EV-tsmc-008, EV-tsmc-061]" in l]
    if len(up) != 1:
        raise SystemExit("F5:tsmc OIP 줄을 찾지 못했다")
    down = replace_line(j["evidence_down"], "TSMC 2나노 첫 고객 명단에 Intel 이 빠졌고",
                        "Intel 은 서버·클라이언트 프로세서의 compute tile 을 TSMC N3B 로 만들지만 TSMC 2나노 첫 고객 명단에 없고 다음 세대는 자사 18A 로 만들 "
                        "예정이며, 2026년 초 자사 18A 제품을 대량 생산하기 시작했다. [EV-tsmc-041, EV-tsmc-072]", "F5:tsmc")
    write("F5", "tsmc", {"changes": {}, "evidence_after": ev, "evidence_up_after": up, "evidence_down_after": down,
                         "reason": "⑤ 첫머리 잣대(지분·공동개발·재판매·수수료 분배)를 고르게 대어 고객 관계는 판매로 두고 +1 을 OIP 공동개발로 받친다(1차 리뷰 규칙 일관성 N4·Q03). "
                                   "Intel 문장은 인용 원문(EV-tsmc-041 셋째 문단, EV-tsmc-072)대로 고친다(사실·출처 리뷰 A 과제 14)"})

    # ---------- N4: spacex-xai ⑤ ----------
    j = J["F5:spacex-xai"]
    ev = replace_line(j["evidence"], "Anthropic 과 Google 의 컴퓨트 계약은 동맹으로 세지 않는다. 오가는 것이 컴퓨트 대금뿐인 단순 매매이고",
                      "Anthropic 과 Google 의 컴퓨트 계약은 동맹으로 세지 않는다. 오가는 것이 컴퓨트 대금뿐이고 지분·공동개발·재판매·수수료 분배가 걸리지 않은 "
                      "단순 매매다. Google 의 SpaceX 지분은 받은 투자라 동맹 근거가 아니다.", "F5:spacex-xai")
    down = drop_line(j["evidence_down"], "최초 3개월 뒤 어느 쪽이든 90일 통지로 해지할 수 있다", "F5:spacex-xai")
    write("F5", "spacex-xai", {"changes": {}, "evidence_after": ev, "evidence_down_after": down,
                               "reason": "Anthropic 계약 제외 사유에서 잣대가 배제한 해지 조항을 빼고 단순 매매로만 적는다(1차 리뷰 규칙 일관성 N4·Q03)"})

    # ---------- L1: amazon ① ----------
    j = J["F1:amazon"]
    ev = sub_in_line(j["evidence"], "지금 연회비가 $139 그대로라는 사실은",
                     "지금 연회비가 $139 그대로라는 사실은 확정 근거로 다시 확인하지 못했다(관련 근거는 후보 상태).",
                     "지금 연회비가 $139 그대로라는 사실은 Amazon 공식 요금 페이지로 확인했다.", "F1:amazon")
    ev = sub_in_line(ev, "2024년 1분기부터 2026년 2분기까지 열 분기를 셌다.", "열 분기를 셌다.",
                     "열 분기를 셌다(2025년 1분기~2026년 2분기 여섯 분기는 분기별 전년 대비 값이고, 2024년 네 분기는 연간 구독 매출 증가에서 미룬 추론이다).", "F1:amazon")
    write("F1", "amazon", {"changes": {}, "evidence_after": ev,
                           "reason": "판정 칸의 '후보 상태' 문장이 올릴 근거의 확정 근거 EV-amazon-060 과 모순이라 현재 상태로 다시 쓰고, 지속 분기 셈의 추론 부분을 표시한다"
                                     "(1차 리뷰 L1, 사실·출처 리뷰 A 과제 7·17)"})

    # ---------- L10: amazon ③ ----------
    j = J["F3:amazon"]
    ev = replace_line(j["evidence"], "칩 사업 연환산 매출($200억 초과)은 한 시점 값이라 b 단계 지표로 쓸 수 없었다.",
                      "칩 사업 연환산 매출은 2026년 1분기 $20B 초과·2분기 $25B 초과 두 시점뿐이라 성장률 두 개를 만들 수 없어 b 단계 지표로 쓰지 못했다. "
                      "AWS 매출에는 AI 가 아닌 컴퓨트·저장 매출이 섞여 있고 AI 비중은 공시되지 않는다.", "F3:amazon")
    write("F3", "amazon", {"changes": {}, "evidence_after": ev,
                           "reason": "칩 사업 연환산 매출을 원문(EV-amazon-057 $20B, EV-amazon-022 $25B)대로 두 시점으로 고친다(1차 리뷰 L10, 사실·출처 리뷰 A 과제 8)"})

    # ---------- amazon ⑤: $2.5B 가 발췌에 없음 ----------
    j = J["F5:amazon"]
    down = sub_in_line(j["evidence_down"], "FTC 와 $2.5B 규모 합의를 맺었고", "FTC 와 $2.5B 규모 합의를 맺었고", "FTC 와 합의를 맺었고", "F5:amazon")
    write("F5", "amazon", {"changes": {}, "evidence_down_after": down,
                           "reason": "합의 금액 $2.5B 는 인용 발췌(EV-amazon-055)에 없고 보도자료 제목에만 있어 줄에서 뺀다(사실·출처 리뷰 A 과제 9)"})

    # ---------- apple ⑧: 10% 고객 부재는 추론 ----------
    j = J["F8:apple"]
    up = sub_in_line(j["evidence_up"], "매출 10% 이상 고객은 없다. [EV-apple-041]", "매출 10% 이상 고객은 없다. [EV-apple-041]",
                     "매출 10% 이상 고객은 없다(공시 의무상 해당 고객이 없다고 읽은 추론). [EV-apple-041]", "F8:apple")
    write("F8", "apple", {"changes": {}, "evidence_up_after": up,
                          "reason": "10% 고객 부재가 10-K 의 직접 문장이 아니라 공시 의무에서 읽은 추론임을 표시한다(사실·출처 리뷰 A 과제 16)"})

    # ---------- 재무 계산 F1: anthropic ③ 별도 수익모델이 전망치에 선다 ----------
    j = J["F3:anthropic"]
    ev = replace_line(j["evidence"], "Anthropic ③ 은 모방 불가능성 실패, 별도 수익모델 통과, 후발 가속도 실패로 통과점이 1 이고 사다리에서 2점이다.",
                      "Anthropic ③ 은 모방 불가능성 실패, 별도 수익모델 부분, 후발 가속도 실패로 통과점이 0.5 이고 사다리에서 2점이다.", "F3:anthropic")
    ev = replace_line(ev, "별도 수익모델은 통과다. 매출 전부가 모델 매출이지만",
                      "별도 수익모델은 부분이다. 매출 전부가 모델 매출이라 비모델 매출이 없고, 2차 보도는 매출총이익률이 2024년 −94% 에서 크게 나아졌다고 적지만 "
                      "2025년 값 40% 는 전망치이며 실적 총마진은 공개 자료로 확인되지 않는다. 규칙 ③ 의 '공개 자료로 확인할 수 없으면 판정 보류(감점하되 실격은 아님)' 에 "
                      "따라 부분으로 둔다. 적자 규모는 이 기준의 판정 사유가 아니다(규칙 2.5).", "F3:anthropic")
    up = replace_line(j["evidence_up"], "2차 보도에 따르면 Anthropic 의 매출총이익률은 2024년 −94% 에서 2025년 40%(전망)로 올라 양수가 됐다.",
                      "2차 보도는 Anthropic 의 매출총이익률이 2024년 −94% 에서 2025년 40% 로 오를 것이라 적었으나 2025년 값은 전망치라 점수에 넣지 않는다. [EV-anthropic-058]",
                      "F3:anthropic")
    write("F3", "anthropic", {"changes": {"revenue_model": "partial"}, "evidence_after": ev, "evidence_up_after": up,
                              "reason": "별도 수익모델 통과의 유일한 근거가 매출총이익률 전망치(EV-anthropic-058)라 가점 실측 원칙(규칙 2.1)에 어긋나고, "
                                        "규칙 ③ 표의 판정 보류(감점하되 실격은 아님)에 따라 부분으로 둔다(1차 리뷰 재무 계산 F1·Q09)"})

    # ---------- 사실·출처 B 1 + 규칙 일관성 L2: anthropic ① 거래 채널 가격 실측의 잣대와 시점 ----------
    j = J["F1:anthropic"]
    ev = replace_line(j["evidence"], "거래 채널(모델 API)의 가격 실측은 정가·평균 단가와 라우팅 서비스 점유율을 함께 보아",
                      "거래 채널(모델 API)의 가격 실측은 정가 인하를 실패의 사실로 보고(규칙 ① 의 실패 정의: 가격을 내려야 했다), 라우팅 서비스의 토큰 점유율·평균 단가·"
                      "지출 점유율은 방증으로만 적는다. 라우팅 서비스 토큰 점유율은 매출 점유율이 아니며 라우팅 서비스는 전체 시장이 아니다.", "F1:anthropic")
    ev = replace_line(ev, "가격 실측은 실패다. Opus 정가를 $5/$25 에서 $4/$20 으로",
                      "가격 실측은 실패다. Opus 정가를 $5/$25 에서 $4/$20 으로, 캐시 읽기를 $0.50 에서 $0.20 으로 내리고 Haiku 5.5 를 이전 Haiku 의 10% 가격에 냈다. "
                      "방증으로 본 OpenRouter 토큰 점유율(관측)은 7월 19일 주 0.1169 에서 9월 6일 주 0.0494 로 내렸고 10월 4일 주 0.0389 인데, 하락은 대부분 "
                      "2026-09-22 Opus 5.5 인하 전에 일어났고 인하 뒤에는 멈췄다. 평균 단가(관측)는 $1.2393(9월 8~30일)에서 $1.0178(10월 1~7일)로 내려갔다.", "F1:anthropic")
    ev = replace_line(ev, "단가 프리미엄 자체는 남아 있다.",
                      "단가 프리미엄 자체는 남아 있다. 2026년 6월 보도에서 Anthropic 은 OpenRouter 토큰의 12% 로 매출의 46% 를 냈고, 10월 1~7일 평균 단가(관측)도 "
                      "OpenAI 의 $0.3604 보다 높으며, 같은 두 창(9월 8~30일 → 10월 1~7일)의 OpenRouter 지출 점유율은 26.6% 에서 31.7% 로 올랐다(관측 메모). "
                      "정가를 내린 사실이 실패를 정하므로 이 방증은 점수를 바꾸지 않는다.", "F1:anthropic")
    write("F1", "anthropic", {"changes": {}, "evidence_after": ev,
                              "reason": "거래 채널 가격 실측의 잣대를 정가 인하(규칙 ① 실패 정의)로 두고 토큰 점유율은 방증으로만 적으며, 점유율 하락 시점을 관측대로 "
                                        "(인하 전) 바로잡고 지출 점유율 상승을 적는다(1차 리뷰 규칙 일관성 L2, 사실·출처 B 1)"})

    # ---------- openai ① 같은 잣대 ----------
    j = J["F1:openai"]
    ev = sub_in_line(j["evidence"], "거래 채널(모델 API)은 단가 프리미엄을 지키며 점유율이 늘면 통과",
                     "거래 채널(모델 API)은 단가 프리미엄을 지키며 점유율이 늘면 통과, 단가를 내리며 점유율을 지키면 부분, 단가를 내렸는데 점유율도 줄면 실패로 보고 "
                     "라우팅 서비스 토큰 점유율은 매출 점유율이 아니다.",
                     "거래 채널(모델 API)은 정가 인하를 실패의 사실로 보고(규칙 ① 의 실패 정의) 라우팅 서비스 토큰 점유율은 방증으로만 적으며, 그 점유율은 매출 점유율이 아니다.",
                     "F1:openai")
    ev = sub_in_line(ev, "거래 채널은 GPT-6 Sol 을 GPT-5.6 Sol 보다 50% 내린 뒤",
                     "거래 채널은 GPT-6 Sol 을 GPT-5.6 Sol 보다 50% 내린 뒤 토큰 점유율(관측)이 0.0684(7월 19일 주)에서 0.1605(9월 6일 주), 0.1136(10월 4일 주)으로 움직여 "
                     "단가를 내리며 점유율을 지킨 부분에 해당한다.",
                     "거래 채널은 GPT-6 Sol 정가를 GPT-5.6 Sol 보다 50% 내려 정가 인하 기준으로는 실패이지만 보조 채널이라 판정에 넣지 않으며, 토큰 점유율(관측) "
                     "0.0684(7월 19일 주) → 0.1605(9월 6일 주) → 0.1136(10월 4일 주)은 방증이다.", "F1:openai")
    write("F1", "openai", {"changes": {}, "evidence_after": ev,
                           "reason": "거래 채널 가격 실측의 잣대를 anthropic 과 같게 정가 인하로 두고 토큰 점유율은 방증으로만 적는다(1차 리뷰 규칙 일관성 L2·Q03). 판정(소비자 채널 부분)은 그대로다"})

    # ---------- 사실·출처 B 2: alibaba ② ARC 순위표 ----------
    j = J["F2:alibaba"]
    ev = replace_line(j["evidence"], "Coding Agent Index 차트(68 부터 54 까지 여덟 제품)와 같은 날 ARC Prize 순위표에는 알리바바 제품이 없다.",
                      "Qwen3.8 Max(0902) 는 종합 지수 45 로 1위(58)와 회사 기준 공동 2위(53)에 못 미치고 GDPval-AA 에서 14위다. 같은 날 ARC Prize 순위표의 알리바바 최고는 "
                      "Qwen3.8-27B(XHigh) ARC-AGI-2 42.4% 로 회사 기준 1·2위(OpenAI 95.0%, Anthropic 93.3%)에 못 미치고, Coding Agent Index 막대 차트 여덟 제품에는 "
                      "알리바바 제품이 없다. 어느 축에서도 회사 기준 2위 안에 들지 못해 성능 도약은 실패다.", "F2:alibaba")
    write("F2", "alibaba", {"changes": {}, "evidence_after": ev,
                            "reason": "ARC Prize 순위표에 알리바바 제품이 없다는 문장을 원문(Qwen3.8-27B ARC-AGI-2 42.4%)대로 고친다. 성능 도약 실패·② 3점은 그대로다(사실·출처 B 2)"})

    # ---------- L14: nvidia ⑤ ----------
    j = J["F5:nvidia"]
    down = replace_line(j["evidence_down"], "OpenAI 와 Meta 는 AMD GPU 를 최대 6GW 씩 쓰는 다년 계약을 맺었으나",
                        "OpenAI 와 Meta 는 AMD 데이터센터 GPU 를 최대 6GW 씩 배치하는 다년 계약을 AMD 와 맺었고, 첫 1GW 는 AMD Instinct MI450 계열이다. [EV-nvidia-073]",
                        "F5:nvidia")
    up = [*j["evidence_up"], "AMD 가 OpenAI·Meta 계약에 붙인 워런트는 2026-06-27 까지 한 단계도 베스팅되거나 행사 가능해지지 않았다. [EV-nvidia-073]"]
    ev = replace_line(j["evidence"], "다발형은 고객의 자체 칩 하나의 전선이고",
                      "다발형은 고객의 자체 칩 하나의 전선이고 최대 파트너와의 긴장이 확인되지 않아 서지 않는다. AMD 와 OpenAI·Meta 의 6GW 계약은 워런트가 "
                      "베스팅되지 않아 그 계약 아래 대량 출하가 아직 확인되지 않으며, 구조형 판정은 하이퍼스케일 넷과 OpenAI 의 자체 칩 출하로 선다.", "F5:nvidia")
    write("F5", "nvidia", {"changes": {}, "evidence_after": ev, "evidence_up_after": up, "evidence_down_after": down,
                           "reason": "내릴 근거 한 줄에 섞인 두 방향(AMD 계약·워런트 미베스팅)을 사실 둘로 나누고 저울질은 판정 칸에 둔다(1차 리뷰 L14, guide 5.6)"})

    print(f"제안 파일 {len(list(OUT.glob('*.json')))}개 → {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
