# 1차 4영역 리뷰 수정 한 묶음: 판단 제안 파일(work/judge-fix1/)·트리거 문장·기업 요약 문장을 만든다
from __future__ import annotations

import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "scripts"))
from scorecard.paths import run_paths  # noqa: E402
from scorecard.schema import load_json_strict, validate_sources, write_json  # noqa: E402

WORK = Path(__file__).resolve().parent
OUT = WORK / "judge-fix1"
EV_RE = re.compile(r"EV-[a-z0-9-]+-\d{3}")


def judgments(slug):
    return {(j["company_id"], j["factor"]): j for j in load_json_strict(run_paths(slug).run_dir / "judgments.json")["items"]}


def replace_one(lines, needle, new, where):
    hits = [i for i, l in enumerate(lines) if needle in l]
    if len(hits) != 1:
        raise SystemExit(f"[{where}] '{needle[:40]}' 가 {len(hits)}번 나온다")
    out = list(lines)
    out[hits[0]] = new
    return out


def spec(j, *, changes=None, ev=None, up=None, down=None, reason, extra_cite=()):
    ev = ev if ev is not None else j["evidence"]
    up = up if up is not None else (j.get("evidence_up") or [])
    down = down if down is not None else (j.get("evidence_down") or [])
    cite = sorted({i for l in up + down for i in EV_RE.findall(l)} | set(extra_cite))
    return {"changes": changes or {}, "evidence_after": ev, "evidence_up_after": up, "evidence_down_after": down, "cite": cite, "reason": reason}


def write(name, s):
    (OUT / f"{name}.json").write_text(json.dumps(s, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> int:
    slug = sys.argv[1]
    J = judgments(slug)
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()

    # N1 microsoft ⑦ (규칙 일관성 리뷰)
    j = J[("microsoft", "F7")]
    ev = list(j["evidence"])
    ev[0] = "마이크로소프트 ⑦ 은 조달 의존 고객 비중 큼, 내 돈이 돌아옴 칸이라 −2 이며, 비중이 큰 쪽에서는 세로축이 점수를 가르지 않는다."
    ev = replace_one(ev, "마이크로소프트의 비율은 10-K 가 공시한 OpenAI 상업 거래 매출",
                     "10-K 가 공시한 OpenAI 상업 거래 매출(수익 배분 포함) $24.1B 는 같은 회계연도(2025-07-01~2026-06-30) 매출 $331.8B 의 7.3% 이지만, "
                     "이미 인식한 매출이라 앞으로 대금을 낼 약정의 몫을 좁히지 못한다.", "msft F7 J6")
    ev = replace_one(ev, "Anthropic 의 Azure 컴퓨트 $30B 구매 약정(회사 1차 발표)은 기간이 적혀 있지 않아",
                     "OpenAI 는 Azure 서비스 $250B 를 추가로 사기로 계약했고(회사 1차 발표) 기간은 밝혀지지 않았다. 기간이 공시되지 않은 약정은 한 해에 다 넣은 "
                     "상한으로 견주므로 Anthropic 의 Azure 컴퓨트 $30B 구매 약정(회사 1차 발표, 기간 미공시)을 더한 상한은 매출의 84.4% 이고, 이 몫을 작게 "
                     "좁힐 공시나 회사 1차 발표가 없어 가로축은 큼이다.", "msft F7 J7")
    ev = replace_one(ev, "OpenAI 가 Azure 를 추가로 사기로 한 약정의 금액·기간은",
                     "OpenAI 의 Azure 추가 약정이 2026-04-27 개정 계약 뒤에도 같은 금액으로 남아 있는지와 연도별 이행 일정은 확인하지 못했다(미확인). "
                     "기간이 공시되거나 약정이 줄었다는 회사 1차 자료가 나오면 가로축을 다시 잰다.", "msft F7 J8")
    down = list(j["evidence_down"]) + ["OpenAI 는 Azure 서비스 $250B 를 추가로 사기로 계약했고 기간은 밝히지 않았다. [EV-microsoft-045]"]
    write("F7-microsoft", spec(j, changes={"funding_dependent_share": "large"}, ev=ev, down=down,
                               reason="회사 1차 발표인 OpenAI 의 Azure $250B 추가 구매 계약을 분자에 넣어 가로축을 큼으로 고친다(규칙 일관성 리뷰 N1, Q03)"))

    # 재무 계산 리뷰 F1: openai ⑧ 약정 분자를 공유 정의(해지할 수 없거나 고정·보장된 약정)로 맞춘다
    j = J[("openai", "F8")]
    ev = list(j["evidence"])
    ev = replace_one(ev, "OpenAI ⑧ 은 −4 이고", "OpenAI ⑧ 은 −3 이고 점수를 정한 축은 공급 축이다. 약정과 컴퓨트 조달이 모두 −3 이다.", "openai F8 J6")
    ev = replace_one(ev, "약정은 −4 다.",
                     "약정은 −3 이다. 구속력이 공시나 회사 1차 발표로 확인되는 몫은 AWS 의 7년 $38B 와 8년 $100.0B 증액(Amazon 10-Q)과 Azure 서비스 $250B "
                     "추가 구매 계약(Microsoft 1차 발표)이고, 여기에 Oracle 5년 $300B(2차 보도)를 더한 약 $6,880억은 2026-09 말 회사 기준 연환산 매출 약 "
                     "$50B(회사가 투자자에게 알린 값을 전한 2차 보도)의 약 13.8배라 몇 배 구간이다(계산).", "openai F8 J7")
    ev = replace_one(ev, "구속력이 공시로 확인되는 몫만 보면",
                     "CEO 가 밝힌 향후 8년 약 $1.4T 의 컴퓨트 약정(회사 1차 발표)은 연환산 매출의 약 28배이지만, 그 가운데 해지할 수 없거나 고정·보장된 몫은 "
                     "확정 근거로 확인하지 못했다(미확인). 규칙 2.1 은 감점에 구속력 있는 약정까지 세므로 공유 정의에 맞는 위 몫으로 재고, 다른 회사에서 해지할 "
                     "수 있는 계약을 분자에서 뺀 것과 같은 잣대를 댄다. 구속력 있는 몫이 연환산 매출의 20배를 넘는다는 공시나 회사 1차 자료가 나오면 −4 로 다시 본다.",
                     "openai F8 J8")
    down = list(j["evidence_down"]) + ["OpenAI 는 Azure 서비스 $250B 를 추가로 사기로 계약했다. [EV-microsoft-045]"]
    write("F8-openai", spec(j, changes={"score": -3}, ev=ev, down=down,
                            reason="약정 분자를 열네 회사 공유 정의(해지할 수 없거나 고정·보장된 약정)로 맞춘다(재무 계산 리뷰 F1, 규칙 2.1)"))

    # 사실·출처 A·재무 계산 리뷰: alphabet ⑧ 약정 분자를 마이크로소프트·메타와 같은 범위(단기 계약·열린 구매 주문 포함 총액)로
    j = J[("alphabet", "F8")]
    ev = replace_one(j["evidence"], "알파벳 ⑧ 은 −2 이고",
                     "알파벳 ⑧ 은 −3 이고 점수를 정한 축은 약정 축, 곧 아직 개시되지 않은 데이터센터 리스와 구매 약정·기타 계약상 의무를 더한 약 $9,020억이 "
                     "최근 1년 매출의 약 2.02배인 것이다.", "alphabet F8 J6")
    ev = replace_one(ev, "약정 축은 −2 다. 2026-06-30 10-Q 주석 10",
                     "약정 축은 −3 이다. 2026-06-30 10-Q 경영진 논의의 구매 약정·기타 계약상 의무 $811.0B(1년 안에 끝나는 $200.7B 포함, 장기 공급 계약과 열린 "
                     "구매 주문)와 주석 4 의 미개시 리스 $85.2B·단기 리스 약정 $5.8B 를 더한 약 $9,020억은 최근 1년 매출 $4,458.66억(2025년 $4,028.36억 − "
                     "전년 상반기 $1,866.62억 + 올해 상반기 $2,296.92억)의 약 2.02배다(계산).", "alphabet F8 J7")
    ev = replace_one(ev, "같은 10-Q 경영진 논의의 구매 약정 총액 $811.0B",
                     "구매 약정의 범위는 마이크로소프트(열린 구매 주문과 인수 의무를 담은 구매 약정)·메타(단기·장기 해지 불가 약정)와 같게 단기 계약과 열린 구매 "
                     "주문까지 넣은 총액이다. 주석 10 의 고정·보장된 장기 약정 $707.0B 만 쓰면 약 1.79배로 −2 이고, 총액 기준 2.02배는 2배 경계 바로 위다(계산).",
                     "alphabet F8 J8")
    down = replace_one(j["evidence_down"], "2026-06-30 고정·보장된 장기 약정 $707.0B 와",
                       "2026-06-30 구매 약정·기타 계약상 의무 $811.0B 와 미개시 리스 $85.2B·단기 리스 약정 $5.8B 를 더한 약 $9,020억은 최근 1년 매출 "
                       "$4,458.66억의 약 2.02배다(계산). [EV-alphabet-075, EV-alphabet-074]", "alphabet F8 D1")
    down.insert(1, "구매 약정 가운데 고정·보장된 장기 약정은 $707.0B 다. [EV-alphabet-073]")
    write("F8-alphabet", spec(j, changes={"score": -3}, ev=ev, down=down,
                              reason="약정 분자를 마이크로소프트·메타와 같은 범위로 맞춘다(사실·출처 A 리뷰 1, 재무 계산 리뷰 F1, Q03)"))

    # 사실·출처 A 리뷰 3: microsoft ⑧ 고객 축을 회사 1차 발표(상업 RPO 의 약 45% 가 OpenAI)로 잰다
    j = J[("microsoft", "F8")]
    ev = replace_one(j["evidence"], "마이크로소프트 ⑧ 은 −2 이고",
                     "마이크로소프트 ⑧ 은 −2 이고 점수를 정한 축은 약정 축과 고객 축이다. 아직 개시되지 않은 데이터센터 리스와 구매·건설 약정을 더한 약 $5,578억이 "
                     "2026 회계연도 매출의 약 1.68배이고, OpenAI 계약 잔고의 12개월 인식분이 매출의 약 21~28% 다.", "msft F8 J6")
    ev = replace_one(ev, "고객 축은 −1 이다.",
                     "고객 축은 −2 다. 회사는 2025-12-31 상업 RPO $625B 의 약 45% 가 OpenAI 몫이고 상업 RPO 의 약 25% 를 12개월 안에 인식한다고 밝혔다(회사 "
                     "1차 발표). OpenAI 몫이 같은 비율로 인식된다고 보면 12개월 인식분은 약 $703억으로 2026 회계연도 매출 $3,318억의 약 21% 이고, 2026-06-30 상업 "
                     "RPO $678B 와 12개월 인식 약 30%(10-K)에 같은 45% 를 대면 약 $915억, 약 28% 다(추론 계산). 어느 쪽이든 10~30% 이고 범용 클라우드 설비라 "
                     "물량을 다른 고객에게 돌릴 수 있어 −2 다. 인식 매출 기준으로는 2026 회계연도 OpenAI 상업 계약 매출 $24.1B 가 약 7% 다.", "msft F8 J8")
    ev = replace_one(ev, "OpenAI 가 상업 RPO $678B 에서 차지하는 비중은",
                     "OpenAI 몫의 인식 일정과 2026-06-30 현재 비중은 따로 공시되지 않아 평균 비율로 추론했다(미확인). OpenAI 몫의 12개월 인식분이 매출의 30% 를 "
                     "넘는다는 공시나 회사 1차 자료가 나오면 고객 축을 −3 으로 다시 본다.", "msft F8 J12")
    down = list(j["evidence_down"])
    down.insert(2, "2025-12-31 상업 RPO $625B 의 약 45% 가 OpenAI 몫이고, 상업 RPO 의 약 25% 는 12개월 안에 매출로 인식된다. [EV-microsoft-046]")
    write("F8-microsoft", spec(j, ev=ev, down=down,
                               reason="회사 1차 발표인 OpenAI 의 상업 RPO 비중으로 고객 축을 잰다(사실·출처 A 리뷰 3). 점수는 그대로다"))

    # 출력 리뷰 B6 alphabet ⑤
    j = J[("alphabet", "F5")]
    ev = replace_one(j["evidence"], "Anthropic 약정의 고객 비중은 여기서 다시 세지 않는다",
                     "TSMC 대만 생산 의존은 ⑧ 에서 셌으므로 여기서 다시 세지 않는다. Anthropic 약정이 Google Cloud 백로그에서 차지하는 비중은 2차 보도뿐이라 "
                     "⑧ 고객 축도 등급을 가르는 수치로 쓰지 않았고, 여기서도 적대 등급의 재료로 쓰지 않는다.", "alphabet F5")
    write("F5-alphabet", spec(j, ev=ev, reason="⑧ 이 Anthropic 약정 비중을 세지 않게 된 뒤의 교차 참조로 고친다(출력 리뷰 B6)"))

    # 사실·출처 B 리뷰: palantir ⑤ 의 프랑스·독일 문장(EV-palantir-009 원문 본문에 있음)
    j = J[("palantir", "F5")]
    ev = replace_one(j["evidence"], "프랑스·독일 정부가 Palantir 계약을 끊었다는 사실은 확정 근거에 없어 미확인이다.",
                     "FT 를 인용한 SFG Media 기사는 프랑스·독일이 일부 Palantir 계약을 끊거나 사용을 제한했다고 적지만(2차 보도), 계약 이름과 시점이 없어 "
                     "어느 계약인지는 확인하지 못했다. 이 보도를 써도 다발형은 최대 파트너인 미 정부와의 긴장을 따로 요구하므로 적대 등급은 구조형에 머문다.",
                     "palantir F5")
    write("F5-palantir", spec(j, ev=ev, reason="원문 본문에 있는 프랑스·독일 계약 보도를 판정 칸에 반영한다(사실·출처 B 리뷰)"))

    # 출력 리뷰 B3 amazon ⑨
    j = J[("amazon", "F9")]
    down = replace_one(j["evidence_down"], "지연인출 약정은 기준일 2026-10-06 전인",
                       "지연인출 정기대출 $17.5B 는 2026-09-30 에 미인출 약정으로서의 시한이 끝났고, 364일 리볼빙 $5.0B 는 2026-10 에 만기가 온다. "
                       "[EV-amazon-011, EV-amazon-001, EV-amazon-010]", "amazon F9")
    write("F9-amazon", spec(j, down=down, reason="지난 실행의 기준일 표기를 뺀 현재 상태 문장으로 고친다(출력 리뷰 B3)"))

    # 출력 리뷰 B9 spacex-xai ③
    j = J[("spacex-xai", "F3")]
    down = replace_one(j["evidence_down"], "Grok 4.6 은 Artificial Analysis 지능 지수 61",
                       "2026-10-08 Artificial Analysis 종합 지수 4.3.2판에서 SpaceXAI 최고 모델 Grok 4.7(xhigh)은 46 으로 Anthropic(58)·OpenAI·Google(53)·"
                       "Meta(48) 모델보다 낮다. [EV-anthropic-049]", "spacex F3")
    write("F3-spacex-xai", spec(j, down=down, reason="② 와 같은 날짜의 지수 판으로 고친다(출력 리뷰 B9)"))

    # 트리거 문장(출력 리뷰 B1·B2·B4·B5·B8)
    p = run_paths(slug).triggers
    trg = load_json_strict(p)
    T = {t["trigger_id"]: t for t in trg["items"]}

    def sub(tid, old, new):
        if old not in T[tid]["observation"]:
            raise SystemExit(f"[{tid}] '{old[:40]}' 가 없다")
        T[tid]["observation"] = T[tid]["observation"].replace(old, new)

    sub("TRG-012", "메타 ④ 판단은 3(AI 광고 최적화는 증명됐으나 광고 의존 약 98%)이다.",
        "메타 ④ 판단은 자체 칩(MTIA)·자체 모델(Muse)·AI 유통·AI 밖 매출(광고) 네 자리로 4점이고, 기업용 AI 플랫폼은 매출·고객 배치가 공시되지 않아 자리로 세지 않았다.")
    sub("TRG-005", "기준일(2026-10-08) 현재", "기준일(2026-10-12) 현재")
    sub("TRG-006", "아마존이 메타 Muse 쇼핑 에이전트를 차단했다(제목 기준). 2026-10-06 UBS 조사에서 AI 챗봇이 쇼핑 추천 때 아마존보다 월마트·코스트코로 소비자를 "
                   "보낸다는 보도가 나왔다(제목 기준, 추천 비중이지 이탈 수치가 아니다).",
        "아마존과 월마트가 메타의 쇼핑 에이전트 Muse 의 접속을 막았다(2026-09-29 보도). 2026-10-05 UBS 조사에서 AI 챗봇이 쇼핑 추천 때 아마존보다 월마트·"
        "코스트코를 더 자주 권한다는 보도가 나왔으나, 이는 추천 비중이지 이탈 수치가 아니다.")
    sub("TRG-036", " 10월 1일 Bloomberg 는 추수감사절(11월 26일) 전 상장을 목표로 한다고, 10월 5일 WSJ 는 상장 절차를 계속 진행한다고 보도했다(제목 기준).", "")
    sub("TRG-037", "10월 5일 BBC 는 국방부가 Anthropic AI 도구 사용을 중단했다고 보도했다(제목 기준).",
        "10월 5일 국방부 관계자는 BBC 에 국방부가 Anthropic 제품 사용을 중단했다고 밝혔다.")
    sub("TRG-038", "FTC(미 연방거래위원회)가 Anthropic·OpenAI 등을 상대로 소비자 위해 조사를 열었다는 보도가 2026-09-30 쏟아졌고, 10월 1일에는 조사를 서두른다는 "
                   "보도가 나왔다(제목 기준).",
        "FTC(미 연방거래위원회)가 OpenAI·Anthropic 등 AI 회사의 제품 안전을 조사하고 있다는 보도(Bloomberg Law, 2026-09-30)가 있고, 2026-10-09 백악관 "
        "초지능 태스크포스는 모든 AI 회사에 사고 통보·시정 의무를 요구했으나 제재 수단은 밝히지 않았다(Axios).")
    T["TRG-039"]["observation"] = ("Bloomberg 는 OpenAI 가 기업가치 $1.4T(조달 전) 기준으로 $30B 이상 조달을 추진한다고 보도했고(09-29), 10월 9일에도 UAE 펀드 MGX 등과 "
                                   "협상 중이며 라운드가 마감되지 않았다고 전했다. FT 는 Altman 이 안전 문제가 풀릴 때까지 상장을 미룬다고 보도했다. 회사 자체 정의의 "
                                   "연환산 매출은 약 $50B(9월 말)이고, Axios 가 전한 $70B 는 투자자가 Anthropic 방식으로 환산한 값이다.")
    sub("TRG-091", "메타가 브렛 테일러의 시에라와 AI 에이전트 상거래 표준을 함께 내놓았다는 보도(SiliconANGLE 2026-10-07)가 있다. 제목만 확인했다.",
        "메타가 Walmart·Stripe·Sierra Technologies 와 AI 에이전트 상거래 표준 Personal Agent Protocol 을 함께 내놓았고(SiliconANGLE 2026-10-06), "
        "Sierra 공동창업자 브렛 테일러는 누구나 구현할 수 있는 개방 표준이라고 밝혔다.")
    sub("TRG-091", "다른 회사의 채택이 확인되지 않아", "공동 개발사 밖의 채택이 확인되지 않아")
    sub("TRG-025", "10월 1~6일에도 같은 칩의 성능 재보도만 있고 배치·출하 소식은 없다.",
        "기준일(2026-10-12)까지 같은 칩의 배치·출하 소식은 없고, 칩 공개 기사는 V900 을 2027년 1분기 양산·상용 출시 예정으로 적는다.")
    write_json(p, trg)

    # TRG-091 출처를 원문 주소로
    sp = run_paths(slug).run_dir / "sources.json"
    src = load_json_strict(sp)
    for s in src["items"]:
        if s["source_id"] == "SRC-NEWS-meta-20261007-c3c25276" and "news.google.com" in (s.get("url") or ""):
            s["relay_url"] = s["url"]
            s["url"] = "https://siliconangle.com/2026/10/06/meta-teams-up-with-bret-taylors-sierra-technologies-on-new-standards-for-ai-agent-commerce/"
    validate_sources(src, slug)
    write_json(sp, src)
    print(f"제안 파일 {len(list(OUT.glob('*.json')))}개, 트리거 9건 고침")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
