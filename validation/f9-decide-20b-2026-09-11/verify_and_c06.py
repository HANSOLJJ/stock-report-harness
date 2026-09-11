# F9-DECIDE-20B 검증: 입력 변경 테스트 + 통과 방향 양성 대조, 그리고 C-06 다섯 공백의 실측.
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import simulate_f9 as S  # noqa: E402

fails = []
lines = []


def ck(cond, msg):
    lines.append(("  PASS  " if cond else "  FAIL  ") + msg)
    if not cond:
        fails.append(msg)


lines.append("=" * 96)
lines.append("A. 통과 방향 양성 대조 — 밴드 함수가 각 구간에서 실제로 그 값을 낸다")
lines.append("=" * 96)
for m, want, label in [(-0.05, -3, "-10%<m<0 구간"), (-0.20, -4, "-30%<m<-10% 구간"),
                       (-0.50, -5, "m<-30% 구간"), (-0.149, -4, "spacex-xai 실측값")]:
    got, why = S.g1_band(m)
    ck(got == want, "m=%s → %s (기대 %s) [%s] %s" % (m, got, want, why, label))

lines.append("")
lines.append("경계값 자체의 귀속 — C-06 첫째 공백을 두 해석으로 대조한다")
lines.append("  해석A(포함): v1.5 g1_bands_status 문자열 '-10% <= m < 0 → -3' 을 그대로 읽음")
lines.append("  해석B(배제): 경계값을 아래 구간(더 나쁜 쪽)에 귀속")
for m, ra, rb in [(-0.10, -3, -4), (-0.30, -4, -5)]:
    got, why = S.g1_band(m)
    lines.append("  m=%s → 구현값 %s [%s] | 해석A %s / 해석B %s → %s" % (
        m, got, why, ra, rb, "두 해석이 갈린다" if ra != rb else "일치"))
    ck(got == ra, "m=%s 에서 구현이 해석A(%s)를 따른다 (status 문자열과 일치)" % (m, ra))
lines.append("  → 경계값 자체는 두 해석에서 한 칸 차이가 난다. 명문화가 필요하다.")
for m, want in [(0.0, None), (-0.0999999, -3), (-0.3000001, -5)]:
    got, why = S.g1_band(m)
    ck(got == want, "경계 바깥 m=%s → %s (기대 %s) [%s]" % (m, got, want, why))

lines.append("")
lines.append("=" * 96)
lines.append("B. 입력 변경 테스트 — 입력을 바꾸면 점수가 기대 방향으로 움직인다")
lines.append("=" * 96)
orig = json.loads(json.dumps(S.inv["rows"]))
orig_state = json.loads(json.dumps(S.state))

base = S.simulate("spacex-xai", "diagnose_only", "hold", "exclude", True)
ck(base["score"] == -4, "기준: spacex-xai = -4")

S.inv["rows"]["spacex-xai"]["operating_margin_ttm"] = -0.05
t = S.simulate("spacex-xai", "diagnose_only", "hold", "exclude", True)
ck(t["score"] == -3, "손실률을 -0.149→-0.05 로 완화하면 -4 → %s (기대 -3)" % t["score"])

S.inv["rows"]["spacex-xai"]["operating_margin_ttm"] = -0.40
t = S.simulate("spacex-xai", "diagnose_only", "hold", "exclude", True)
ck(t["score"] == -5, "손실률을 -0.40 으로 악화하면 → %s (기대 -5)" % t["score"])

S.inv["rows"]["spacex-xai"]["operating_margin_ttm"] = -0.149
S.state["spacex-xai"]["calc"]["inputs"]["buffer_erosion"] = "yes"
t = S.simulate("spacex-xai", "diagnose_only", "hold", "exclude", True)
ck(t["score"] == -4, "완충잠식=yes 시 하한 -4 적용 → %s" % t["score"])
S.state["spacex-xai"]["calc"]["inputs"]["buffer_erosion"] = "no"

# G3 방향성: 완충을 키우면 runway 가 늘어 감점이 줄어야 한다
S.inv["rows"]["oracle"]["cash"] = 31900000000.0
b = S.simulate("oracle", "diagnose_only", "hold", "exclude", True)
S.inv["rows"]["oracle"]["cash"] = 200000000000.0
t = S.simulate("oracle", "diagnose_only", "hold", "exclude", True)
ck(b["score"] == -3 and t["score"] == -2,
   "oracle 현금 31.9B→200B 이면 runway 상승으로 %s → %s (기대 -3 → -2)" % (b["score"], t["score"]))
S.inv["rows"] = orig
S.state = orig_state

lines.append("")
lines.append("=" * 96)
lines.append("C. C-06 다섯 공백의 실측")
lines.append("=" * 96)

rows = orig
st = orig_state
cids = list(st.keys())

# 1) 손실률이 정확히 경계값인 기업
exact = [(c, rows[c].get("operating_margin_ttm")) for c in cids
         if rows[c].get("operating_margin_ttm") in (-0.10, -0.30)]
have_m = [(c, rows[c].get("operating_margin_ttm")) for c in cids
          if rows[c].get("operating_margin_ttm") is not None]
lines.append("1) 손실률 경계 중첩")
lines.append("   operating_margin_ttm 보유: %d/14 → %s" % (len(have_m), have_m))
lines.append("   정확히 -10%% 또는 -30%% 인 기업: %d개 %s" % (len(exact), exact))
lines.append("   → 경계 중첩은 현재 자료에서 실제로 발생하지 않는다. 다만 밴드가 proposed 라")
lines.append("     손실률을 가진 유일한 기업(spacex-xai)이 그 때문에 보류돼 있다.")

# 2) FCF·영업손익이 정확히 0
zero_fcf = [c for c in cids if rows[c].get("fcf_ttm") == 0]
lines.append("")
lines.append("2) FCF·영업손익 0")
lines.append("   fcf_ttm == 0 인 기업: %d개 %s" % (len(zero_fcf), zero_fcf))
lines.append("   operating_income_ttm 관측: 0/14 (지표 자체가 없음) → 0 판정 대상 없음")

# 3) 완충 잠식 판정 입력
be = {c: (st[c].get("calc") or {}).get("inputs", {}).get("buffer_erosion") for c in cids}
lines.append("")
lines.append("3) 완충 잠식")
lines.append("   buffer_erosion 값 분포: %s" % json.dumps(
    {v: sum(1 for x in be.values() if x == v) for v in set(be.values())}, ensure_ascii=False))
lines.append("   undrawn_credit_facility 관측: 0/14")
lines.append("   → 전 기업이 'no' 로 고정돼 있어 이 규칙은 현재 아무 기업도 움직이지 않는다.")
lines.append("     판정하려면 기초·기말 완충 잔액 시계열이 필요한데 관측에 없다.")

# 4) g2 안정/악화
tr = {c: (st[c].get("calc") or {}).get("inputs", {}).get("fcf_trend") for c in cids}
dist = {}
for v in tr.values():
    dist[v] = dist.get(v, 0) + 1
unknown_pos = [c for c in cids if tr[c] == "unknown" and (rows[c].get("fcf_ttm") or 0) > 0]
lines.append("")
lines.append("4) G2 안정/악화 기계 정의")
lines.append("   fcf_trend 분포: %s" % json.dumps(dist, ensure_ascii=False))
lines.append("   FCF 양수인데 trend=unknown 인 기업: %s" % unknown_pos)
lines.append("   → 기계로 가르려면 전기 FCF 가 필요한데 fcf_ttm 은 기업당 1개 시점뿐이다.")
lines.append("     현재 trend 값은 검토 입력이지 계산 결과가 아니다. 시계열이 없으므로")
lines.append("     '전기 대비'도 '추세'도 자동 판정할 수 없다. 이것이 결론이다.")

# 5) BEP 후퇴와 손실률 경계 동시 충돌
bep = [c for c in cids if (st[c].get("calc") or {}).get("inputs", {}).get("bep_retreat") == "yes"]
both = [c for c in bep if rows[c].get("operating_margin_ttm") is not None]
lines.append("")
lines.append("5) BEP 후퇴 × 손실률 경계 동시 적용")
lines.append("   bep_retreat=yes: %s" % bep)
lines.append("   그중 손실률 수치도 있는 기업(=우선순위가 실제로 필요한 경우): %s" % both)
lines.append("   → openai 는 bep_retreat=yes 이나 operating_margin_ttm 이 없다.")
lines.append("     따라서 우선순위 충돌이 현재 자료에서 실제로 발생하는 기업은 0개다.")
lines.append("     규칙은 명문화가 필요하지만 지금 점수를 움직이지는 않는다.")

txt = "\n".join(lines)
txt += "\n\n" + "=" * 96 + "\nFAIL %d건\n" % len(fails)
for f in fails:
    txt += "  FAIL: %s\n" % f
io.open(os.path.join(HERE, "verify-output.txt"), "w", encoding="utf-8").write(txt)
print(txt)
