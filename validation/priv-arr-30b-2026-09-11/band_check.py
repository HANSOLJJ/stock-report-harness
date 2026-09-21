# PRIV-ARR-30B: v1.5 비상장 구간표가 실제 배정 점수를 재현하는지 확인한다.
# C-12(비상장 F6 밴드 vs 정성 예외) 의견의 근거이므로 단정 전에 기계로 검산한다.
BANDS = [("-2", "~20x"), ("-3", "20x대"), ("-4", "30x+"), ("-5", "100x+")]
CASES = [("Anthropic", 14.8, "~30~39", "흑자 전환 $559M", 0.52, "-3"),
         ("OpenAI", 21.3, "~39", "적자 · BEP 2030", 0.22, "-4")]

print("v1.5 비상장 구간표 (규칙 L609~615)")
for s, r in BANDS:
    print("   %-4s %s" % (s, r))
print("   0 과 -1 은 '—' 로 비어 있다 → 20x 미만을 받을 칸이 없다")
print()
print("실제 배정 (규칙 L673~676 '비상장 3사 판정')")
print("%-10s %-9s %-9s %-18s %-9s %-6s %s" % (
    "기업", "ARR배수", "TTM추정", "이익", "자본효율", "배정⑥", "구간표가 주는 값"))
print("-" * 104)
for name, mult, ttm, prof, ce, assigned in CASES:
    if mult < 20:
        band = "해당 칸 없음(<20x)"
    elif mult < 30:
        band = "-3 (20x대)"
    elif mult < 100:
        band = "-4 (30x+)"
    else:
        band = "-5 (100x+)"
    ok = band.startswith(assigned)
    print("%-10s %-9s %-9s %-18s %-9s %-6s %-20s %s" % (
        name, "%.1fx" % mult, ttm, prof, ce, assigned, band,
        "재현" if ok else "★재현 실패"))
print()
print("결론 — 구간표는 두 기업 중 어느 쪽도 재현하지 못한다.")
print("  Anthropic 14.8x 는 표에 받을 칸 자체가 없는데 -3 이 배정됐다.")
print("  OpenAI 21.3x 는 표대로면 -3 인데 -4 가 배정됐다.")
print("  즉 v1.5 의 비상장 점수는 구간표가 아니라 TTM 보정치와 이익·자본효율을 함께 본 판단이다.")
print()
print("구간 정의 자체의 결함")
print("  '~20x' 와 '20x대' 와 '30x+' 는 경계가 겹치거나 비어 있다.")
print("  '~20x'(-2) 와 '20x대'(-3) 사이, '30x+'(-4) 와 '100x+'(-5) 사이가 모호하고")
print("  20x 미만 구간은 아예 정의가 없다.")
