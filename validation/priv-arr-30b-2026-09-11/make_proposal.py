# PRIV-ARR-30B: 관측 제안 파일을 만든다. 등록은 worker 몫이므로 제안까지만 한다.
# 기간 라벨을 반드시 남기고 원문이 안 밝힌 것은 null 로 두되 사유를 적는다.
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
E = json.load(io.open(os.path.join(HERE, "priv-arr-extract.json"), encoding="utf-8"))
SRCS = E["sources"]

RULE_SRC = "SRC-v15-rule"
TABLE_SRC = "SRC-v15-table"

props = []


def add(cid, metric, value, raw, kind, period_label, period_stated, cites,
        action, note, extra=None):
    p = {
        "observation_id": "%s.%s.priv-arr-30b" % (cid, metric),
        "company_id": cid, "metric": metric, "value": value, "unit": "USD",
        "kind": kind, "raw": raw,
        "period_label": period_label, "period_stated_in_source": period_stated,
        "source_files": [{"file": c["file"], "line": c["line"]} for c in cites],
        "proposed_action": action, "note": note,
    }
    if extra:
        p.update(extra)
    props.append(p)


A, O = E["extracted"]["anthropic"], E["extracted"]["openai"]

add("anthropic", "arr_prior", 47e9, "$47B", "run_rate", None, False,
    A["arr_prior"]["cites"], "add_new",
    "원문이 $47B 에 시점을 붙이지 않았다. 추정해 채우지 않는다. "
    "arr(7월) 과의 간격을 알 수 없으므로 P3 를 기간 정규화된 증가율로 쓸 수 없다.",
    {"period_missing_reason": "source_states_value_without_date",
     "interval_to_arr": None})

add("openai", "arr_prior", 25e9, "$25B", "run_rate", "2~4월(정체 구간)", True,
    O["arr_prior"]["cites"], "add_new",
    "원문이 '2~4월 $25B 정체' 로 적어 단일 시점이 아니라 구간이다. "
    "구간 끝(4월)을 직전으로 보면 arr(7월)까지 약 3개월이다.",
    {"period_is_range": True, "range_label": "2026-02~2026-04"})

add("openai", "arr", 40e9, "$40B / $40B+", "run_rate",
    "원문이 7월 과 8/20 을 함께 쓴다", True, O["arr"]["cites"], "amend_period_label",
    "값은 $40B 로 일치해 변경 없음. 기간 라벨만 문제다. 기존 관측 raw 는 8/20(L917) 을 "
    "골랐으나 증가율 서술(L165·L745)은 7월 기준이다. P3 를 계산하려면 어느 쪽인지 정해야 한다.",
    {"existing_observation_id": "openai.arr.v15", "value_changed": False,
     "candidate_labels": ["7월", "8/20"]})

add("openai", "cumulative_raised", None, "약 $180~190B", "actual", None, False,
    O["cumulative_raised"]["cites"], "flag_derived_value",
    "원문은 범위만 준다. 기존 관측의 185B 는 원문에 없는 중간값 유도치다(raw 에 표시는 돼 있다). "
    "원문 자신의 자본효율 0.22 는 범위 상단과 어긋난다 — 40/190=0.2105 는 0.21 로 반올림된다. "
    "0.22 가 성립하려면 누적 조달이 약 186B 이하여야 하므로 원문 범위 상단이 자기 표기와 충돌한다.",
    {"range": [180e9, 190e9], "existing_observation_id": "openai.cumulative_raised.v15",
     "existing_value": 185e9,
     "self_consistency": {"source_states": 0.22, "at_180B": 0.2222,
                          "at_185B": 0.2162, "at_190B": 0.2105,
                          "max_consistent_with_0_22": 186.05e9}})

# 기존과 값이 같아 변경 제안이 없는 것들도 확인 결과로 남긴다
for cid, metric, d in (("anthropic", "arr", A["arr"]),
                       ("anthropic", "post_money_valuation", A["post_money_valuation"]),
                       ("anthropic", "cumulative_raised", A["cumulative_raised"]),
                       ("openai", "post_money_valuation", O["post_money_valuation"])):
    add(cid, metric, d["value"], d["raw"], d["kind"], d["period_label"], d["period_stated"],
        d["cites"], "confirm_unchanged",
        "원문과 기존 관측이 일치한다. 값 변경 제안 없음. status 는 legacy_unverified 에서 "
        "verified 로 올릴 수 있다 — 출처 파일 해시가 확인됐고 인용 위치를 직접 대조했다.",
        {"existing_observation_id": "%s.%s.v15" % (cid, metric)})

out = {
    "task": "PRIV-ARR-30B",
    "generated": "2026-09-11",
    "registration": "제안만 함. 등록은 worker 몫이다.",
    "network_calls": 0,
    "sources": {
        "AI기업_채점규칙_v1.5.md": {"sha256": SRCS["files"]["AI기업_채점규칙_v1.5.md"],
                                 "declared_in_v1.5.json": True,
                                 "matches_declaration": SRCS["declared_match"],
                                 "source_id": RULE_SRC},
        "AI기업_채점표_v1.5.md": {"sha256": SRCS["files"]["AI기업_채점표_v1.5.md"],
                                "declared_in_v1.5.json": False,
                                "note": "v1.5.json 에 선언이 없다. 이번이 최초 해시 기록이다.",
                                "source_id": TABLE_SRC},
    },
    "kind_note": "arr 과 arr_prior 는 metric 이름이 ARR 이지만 실제 내용은 런레이트다. "
                 "원문이 '특정 시점 월매출 × 12' 로 명시한다(규칙 L647). TTM 매출보다 과대하다. "
                 "kind=run_rate 가 그 사실을 담고 있으니 소비하는 쪽이 반드시 읽어야 한다.",
    "proposals": props,
}
io.open(os.path.join(HERE, "observation-proposals.json"), "w", encoding="utf-8").write(
    json.dumps(out, ensure_ascii=False, indent=1))

print("%-9s %-22s %-18s %-22s %s" % ("회사", "metric", "action", "기간 라벨", "값"))
print("-" * 104)
for p in props:
    print("%-9s %-22s %-18s %-22s %s" % (
        p["company_id"], p["metric"], p["proposed_action"],
        p["period_label"] or "★원문 미기재",
        "{:,.0f}".format(p["value"]) if p["value"] is not None else "범위/변경없음"))
print("\nsaved observation-proposals.json (%d건)" % len(props))
