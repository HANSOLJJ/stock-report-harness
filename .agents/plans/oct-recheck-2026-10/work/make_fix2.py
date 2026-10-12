# 확인 리뷰 2차(confirm-r2) C1·R1·R4·R5·R7 수정: 판단 제안 파일(work/judge-fix2/)과 트리거 문장을 만든다
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from make_fix1 import judgments, replace_one, spec  # noqa: E402

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "scripts"))
from scorecard.paths import run_paths  # noqa: E402
from scorecard.schema import load_json_strict, write_json  # noqa: E402

OUT = Path(__file__).resolve().parent / "judge-fix2"


def write(name, s):
    (OUT / f"{name}.json").write_text(json.dumps(s, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> int:
    slug = sys.argv[1]
    J = judgments(slug)
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()

    # C1 microsoft ⑧ 고객 축: 공유 J2(연환산 계약액)대로 계약 기간으로 편다
    j = J[("microsoft", "F8")]
    ev = replace_one(j["evidence"], "마이크로소프트 ⑧ 은 −2 이고",
                     "마이크로소프트 ⑧ 은 −3 이고 점수를 정한 축은 고객 축, 곧 OpenAI 계약 잔고를 연환산한 값이 2026 회계연도 매출의 30% 를 넘는 것이다. "
                     "아직 개시되지 않은 데이터센터 리스와 구매·건설 약정을 더한 약 $5,578억은 매출의 약 1.68배로 약정 축은 −2 다.", "msft F8 J6")
    ev = replace_one(ev, "고객 축은 −2 다.",
                     "고객 축은 −3 이다. 회사는 2025-12-31 상업 RPO $625B 의 약 45%(약 $2,813억)가 OpenAI 몫이라고 밝혔고(회사 1차 발표), 그 가운데 Azure 서비스 "
                     "$250B 추가 구매 계약은 기간이 밝혀지지 않았다. 계약액을 계약 기간으로 펴되 OpenAI 몫의 기간은 공시되지 않아 회사가 밝힌 상업 RPO 가중평균 잔여 "
                     "기간(2025-12-31 약 2.5년, 2026-06-30 약 2.3년)으로 펴면 연환산은 약 $1,125억~$1,223억으로 2026 회계연도 매출 $3,318억의 약 34~37% 이고"
                     "(추론 계산), 기간이 공시되지 않은 약정을 한 해에 다 넣은 상한으로 견주면 $250B 만으로 약 75% 다(계산). 범용 클라우드 설비라 물량을 다른 고객에게 "
                     "돌릴 경로가 있어 −4 에는 대지 않는다. 인식 매출 기준으로는 2026 회계연도 OpenAI 상업 계약 매출 $24.1B 가 약 7% 다.", "msft F8 J8")
    ev = replace_one(ev, "OpenAI 몫의 인식 일정과 2026-06-30 현재 비중은",
                     "OpenAI 몫의 계약 기간과 2026-06-30 현재 금액은 따로 공시되지 않았다(미확인). 2026 회계연도 4분기 실적 콜은 그 분기의 상업 RPO 증가가 모두 "
                     "프론티어 모델 회사 밖에서 왔다고 밝혀, 6-30 의 OpenAI 몫이 12-31 보다 크지 않다. OpenAI 몫의 연환산이 매출의 30% 아래라는 공시나 회사 1차 "
                     "자료가 나오면 고객 축을 다시 잰다.", "msft F8 J12")
    down = list(j["evidence_down"])
    i = next(k for k, l in enumerate(down) if "EV-microsoft-046" in l)
    down.insert(i + 1, "2026-06-30 상업 RPO 는 $678B 이고 가중평균 잔여 기간은 약 2.3년이며 약 30% 를 12개월 안에 인식한다. [EV-microsoft-047]")
    up = list(j.get("evidence_up") or []) + ["2026 회계연도 4분기 상업 RPO 의 직전 분기 대비 증가는 모두 프론티어 모델 회사 밖 고객의 약정에서 왔다. [EV-microsoft-048]"]
    write("F8-microsoft", spec(j, changes={"score": -3}, ev=ev, up=up, down=down,
                               reason="고객 축을 열네 회사 공유 지표(연환산 계약액)대로 계약 기간으로 펴 다시 잰다(확인 리뷰 2차 C1, Q02·Q03)"))

    # R4·R5 alphabet ⑧
    j = J[("alphabet", "F8")]
    ev = replace_one(j["evidence"], "약정 축은 −3 이다. 2026-06-30 10-Q 경영진 논의의",
                     "약정 축은 −3 이다. 2026-06-30 10-Q 경영진 논의의 구매 약정·기타 계약상 의무 $811.0B(그 가운데 단기 몫 $200.7B, 장기 공급 계약과 열린 구매 "
                     "주문 포함)와 주석 4 의 미개시 리스 $85.2B·단기 리스 약정 $5.8B 를 더한 약 $9,020억은 최근 1년 매출 $4,458.66억(2025년 $4,028.36억 − 전년 "
                     "상반기 $1,866.62억 + 올해 상반기 $2,296.92억)의 약 2.02배다(계산).", "alphabet F8 J7")
    ev = replace_one(ev, "구매 약정의 범위는 마이크로소프트",
                     "10-Q 는 가변 조건 계약의 해지 불가 의무를 최소 수량까지만 센다고 밝혀, $811.0B 는 단기 몫과 열린 구매 주문을 포함한 해지할 수 없는 의무의 "
                     "총액이고 메타(단기·장기 해지 불가 약정)와 같은 범위다. 주석 10 의 1년 넘는 고정·보장 약정 $707.0B 만 쓰면 약 1.79배로 −2 이고, 총액 기준 "
                     "2.02배는 2배 경계 바로 위다(계산).", "alphabet F8 J8")
    write("F8-alphabet", spec(j, ev=ev, reason="약정 총액의 원문 표현과 해지 불가 근거를 적는다(확인 리뷰 2차 R4·R5)"))

    # R7 amazon ⑨
    j = J[("amazon", "F9")]
    down = replace_one(j["evidence_down"], "지연인출 정기대출 $17.5B 는 2026-09-30 에",
                       "지연인출 정기대출 $17.5B 는 2026-09-30 에 미인출 약정으로서의 시한이 끝났고, 364일 리볼빙 $5.0B 는 2026-10 에 만기가 온다. "
                       "[EV-amazon-011, EV-amazon-001, EV-amazon-002, EV-amazon-010]", "amazon F9")
    write("F9-amazon", spec(j, down=down, reason="$5.0B 를 받치는 근거 표지를 더한다(확인 리뷰 2차 R7)"))

    # R1 TRG-092
    p = run_paths(slug).triggers
    trg = load_json_strict(p)
    t = next(x for x in trg["items"] if x["trigger_id"] == "TRG-092")
    old = "OpenAI ⑧ 판단은 지금 −4, ⑨ 는 −2(비상장 경로)다."
    if old not in t["observation"]:
        raise SystemExit("TRG-092 문장이 없다")
    t["observation"] = t["observation"].replace(old, "OpenAI ⑧ 판단은 구속력이 공시·회사 1차 발표로 확인된 클라우드 약정이 연환산 매출의 2배 이상 20배 미만이라 "
                                                     "−3 이고, ⑨ 는 −2(비상장 경로)다.")
    write_json(p, trg)
    print(f"제안 파일 {len(list(OUT.glob('*.json')))}개, 트리거 1건 고침")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
