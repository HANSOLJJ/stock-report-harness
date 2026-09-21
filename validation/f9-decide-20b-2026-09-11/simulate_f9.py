# F9-DECIDE-20B: 미결 5건의 선택지 조합별로 F9 점수가 어떻게 달라지는지 실측한다.
#
# 계산 규약(스스로 세우고 근거를 적는다 — 기존 점수를 정답으로 쓰지 않는다):
#  R1. 게이트 순서와 동작은 design-guideline.md 6.2 표를 그대로 따른다.
#  R2. G1 은 operating_result_reviewed 로 진입한다. profit=통과, loss=밴드 산정,
#      unknown=pending. 단일 분기·조정 손익으로 대체하지 않는다(6.1).
#  R3. G3·G4 는 FCF 음수일 때만 도달한다. 6.2 가 G2 에서 "FCF 음수는 기본 -2 에서
#      G3 진행" 이라고 적어 양수 경로의 후속 진행을 규정하지 않기 때문이다.
#  R4. 하한은 -5(policies.f9.floor).
#  R5. 방향 완화는 direction_A·B 가 모두 unknown 이면 적용하지 않는다(6.3 마지막 문단).
#  R6. 값이 없으면 추정하지 않고 pending 으로 남긴다.
#
# 이 규약은 기존 엔진 출력과 독립적으로 세웠고, 검산은 §양성 대조에서 따로 한다.
import io
import itertools
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
W = os.path.join(HERE, "..", "..", "..", "worker", "scorecard")

state = json.load(io.open(os.path.join(HERE, "f9-current-state.json"), encoding="utf-8"))
inv = json.load(io.open(os.path.join(HERE, "f9-input-inventory.json"), encoding="utf-8"))
rules = json.load(io.open(os.path.join(W, "rules", "v1.5.json"), encoding="utf-8"))
P = rules["policies"]["f9"]

FLOOR = P["floor"]


def g1_band(m):
    """제안 밴드: -10% <= m < 0 → -3, -30% <= m < -10% → -4, m < -30% → -5"""
    if m is None:
        return None, "no_margin"
    if m >= 0:
        return None, "not_loss"
    if m >= -0.10:
        return -3, "-10%<=m<0"
    if m >= -0.30:
        return -4, "-30%<=m<-10%"
    return -5, "m<-30%"


def simulate(cid, c05, c16, c04, c06_bands=True):
    """c05: diagnose_only|apply, c16: hold|downgrade, c04: exclude|include_v15"""
    f = state[cid]
    inp = (f.get("calc") or {}).get("inputs", {})
    row = inv["rows"].get(cid, {})
    path = []
    score = 0

    # --- G1 ---
    opres = inp.get("operating_result_reviewed")
    if opres == "unknown":
        return {"score": None, "status": "pending_data", "path": ["G1 pending: 영업손익 미관측"],
                "blocked_by": "data"}
    if opres == "loss":
        if inp.get("bep_retreat") == "yes":
            score = P["g1_bep_retreat_score"]
            path.append("G1 fail: BEP 후퇴 → %d" % score)
        else:
            if not c06_bands:
                return {"score": None, "status": "needs_rule_decision",
                        "path": ["G1 fail: 손실률 밴드 미확정(C-06)"], "blocked_by": "C-06"}
            m = row.get("operating_margin_ttm")
            s, why = g1_band(m)
            if s is None:
                return {"score": None, "status": "pending_data",
                        "path": ["G1 fail: 손실률 수치 없음"], "blocked_by": "data"}
            score = s
            path.append("G1 fail: m=%s %s → %d" % (m, why, score))
        # 방향 완화 (R5)
        if inp.get("direction_A") == "unknown" and inp.get("direction_B") == "unknown":
            path.append("G1 방향완화: 판정 불가 → 미적용")
        # 완충 잠식 하한
        if inp.get("buffer_erosion") == "yes":
            score = min(score, P["g1_buffer_erosion_min_score"])
            path.append("G1 완충잠식 → 하한 %d" % P["g1_buffer_erosion_min_score"])
        g1_failed = True
    else:
        path.append("G1 pass (profit)")
        g1_failed = False

    # --- C-05: G1 실패 뒤 G3·G4 진행 여부 ---
    if g1_failed:
        if score <= FLOOR:
            path.append("G3/G4 skip: 이미 하한")
            return {"score": score, "status": "ok", "path": path, "blocked_by": None}
        if c05 == "diagnose_only":
            path.append("C-05=diagnose_only → G2~G4 진단만, 추가 감점 없음")
            return {"score": score, "status": "ok", "path": path, "blocked_by": None}
        path.append("C-05=apply → G2~G4 추가 감점 진행")

    # --- G2 ---
    fcf = row.get("fcf_ttm")
    trend = inp.get("fcf_trend")
    if fcf is None:
        if inp.get("fcf_not_disclosed_reason"):
            score = min(score, 0) + P["g2_private_not_disclosed"]
            path.append("G2 비공개 → %d" % P["g2_private_not_disclosed"])
            return {"score": max(score, FLOOR), "status": "ok", "path": path, "blocked_by": None}
        return {"score": None, "status": "pending_data", "path": path + ["G2 FCF 미관측"],
                "blocked_by": "data"}
    if fcf > 0:
        if trend == "stable":
            g2 = P["g2_fcf_positive_stable"]
        elif trend == "deteriorating":
            g2 = P["g2_fcf_positive_deteriorating"]
        else:
            return {"score": None, "status": "needs_judgment",
                    "path": path + ["G2 추세 unknown → 안정/악화 판정 불가"],
                    "blocked_by": "C-06(g2 정의)"}
        score = score + g2 if g1_failed else g2
        path.append("G2 positive/%s → %d" % (trend, g2))
        return {"score": max(score, FLOOR), "status": "ok", "path": path, "blocked_by": None}

    # FCF 음수
    score = (score + P["g2_fcf_negative"]) if g1_failed else P["g2_fcf_negative"]
    path.append("G2 negative → %d (누계 %d)" % (P["g2_fcf_negative"], score))

    # --- G3 ---
    cash = row.get("cash")
    undrawn = row.get("undrawn_credit_facility")  # 0/14 — 자료 없음
    buffer = cash if cash is not None else None
    c04_note = "C-04=%s" % c04
    if c04 == "include_v15":
        # 등급 기반 조달 여력을 완충에 산입하려 해도 수치 입력이 없다
        c04_note += " (등급 기반 조달 여력 수치 입력 없음 → 완충 변화 0)"
    if undrawn:
        buffer += undrawn
    burn = abs(fcf)
    if buffer is None or not burn:
        return {"score": None, "status": "pending_data", "path": path + ["G3 완충/소진 미관측"],
                "blocked_by": "data"}
    runway = buffer / burn
    if runway >= P["g3_runway_keep_years"]:
        step = 0
    elif runway >= P["g3_runway_one_step_years"]:
        step = -1
    else:
        step = -2
    score += step
    path.append("G3 runway=%.4fy step=%d → %d  [%s]" % (runway, step, score, c04_note))

    # --- G4 ---
    cr = row.get("contracted_revenue")
    ob = row.get("offbalance_B")
    cmp_ok = inp.get("coverage_comparable")
    if cmp_ok == "yes" and cr and ob:
        cov = cr / ob
        step = 0 if cov >= P["g4_coverage_keep"] else -1
        score += step
        path.append("G4 coverage=%.3f step=%d → %d" % (cov, step, score))
    elif ob and cmp_ok != "yes":
        # 판정 불가 — C-16
        if c16 == "hold":
            path.append("G4 판정 불가 → C-16=hold: 보류(점수 미확정)")
            return {"score": None, "status": "needs_judgment", "path": path,
                    "blocked_by": "C-16"}
        score += -1
        path.append("G4 판정 불가 → C-16=downgrade: -1 → %d" % score)
    else:
        path.append("G4 대상 약정 없음 → 해당 없음")

    return {"score": max(score, FLOOR), "status": "ok", "path": path, "blocked_by": None}


CIDS = list(state.keys())
combos = list(itertools.product(["diagnose_only", "apply"], ["hold", "downgrade"],
                                ["exclude", "include_v15"], [True, False]))

results = {}
for c05, c16, c04, c06 in combos:
    key = "C05=%s|C16=%s|C04=%s|C06bands=%s" % (c05, c16, c04, "확정" if c06 else "미확정")
    results[key] = {cid: simulate(cid, c05, c16, c04, c06) for cid in CIDS}

io.open(os.path.join(HERE, "f9-simulation.json"), "w", encoding="utf-8").write(
    json.dumps(results, ensure_ascii=False, indent=1))

# --- 어느 기업이 어느 선택지에 반응하는가 ---
print("=" * 100)
print("선택지별 민감 기업 (C-06 밴드 확정 전제)")
print("=" * 100)
base = results["C05=diagnose_only|C16=hold|C04=exclude|C06bands=확정"]
for axis, a, b in [("C-05", "diagnose_only", "apply"),
                   ("C-16", "hold", "downgrade"),
                   ("C-04", "exclude", "include_v15")]:
    ka = "C05=%s|C16=hold|C04=exclude|C06bands=확정" % a if axis == "C-05" else (
        "C05=diagnose_only|C16=%s|C04=exclude|C06bands=확정" % a if axis == "C-16" else
        "C05=diagnose_only|C16=hold|C04=%s|C06bands=확정" % a)
    kb = "C05=%s|C16=hold|C04=exclude|C06bands=확정" % b if axis == "C-05" else (
        "C05=diagnose_only|C16=%s|C04=exclude|C06bands=확정" % b if axis == "C-16" else
        "C05=diagnose_only|C16=hold|C04=%s|C06bands=확정" % b)
    diff = []
    for cid in CIDS:
        x, y = results[ka][cid], results[kb][cid]
        if (x["score"], x["status"]) != (y["score"], y["status"]):
            diff.append("%s: %s(%s) → %s(%s)" % (cid, x["score"], x["status"],
                                                 y["score"], y["status"]))
    print("\n%s  %s → %s" % (axis, a, b))
    print("   변화 기업 %d개" % len(diff))
    for d in diff:
        print("     " + d)

print("\n" + "=" * 100)
print("C-06 밴드 확정 여부")
print("=" * 100)
k1 = "C05=diagnose_only|C16=hold|C04=exclude|C06bands=미확정"
k2 = "C05=diagnose_only|C16=hold|C04=exclude|C06bands=확정"
for cid in CIDS:
    x, y = results[k1][cid], results[k2][cid]
    if (x["score"], x["status"]) != (y["score"], y["status"]):
        print("   %s: %s(%s) → %s(%s)" % (cid, x["score"], x["status"], y["score"], y["status"]))

print("\n" + "=" * 100)
print("C-05 × C-16 교차 (C-06 확정, C-04 exclude)")
print("=" * 100)
for c05 in ["diagnose_only", "apply"]:
    for c16 in ["hold", "downgrade"]:
        k = "C05=%s|C16=%s|C04=exclude|C06bands=확정" % (c05, c16)
        sc = {cid: results[k][cid]["score"] for cid in CIDS}
        unres = [cid for cid in CIDS if results[k][cid]["score"] is None]
        print("  %-14s %-11s  미완료 %d개: %s" % (c05, c16, len(unres), ", ".join(unres)))
        print("       spacex-xai=%s  amazon=%s  openai=%s  oracle=%s" % (
            sc["spacex-xai"], sc["amazon"], sc["openai"], sc["oracle"]))
print("\nsaved f9-simulation.json")
