# FIX-63: 재생성된 리뷰 템플릿을 9차 재판정 2회 결과로 채운다 (재무 계산 영역은 pass 로 적지 않는다)
"""체크리스트 23행의 출처가 둘이다.

- Q04·Q06·Q10·Q11 — 9차 재무 계산 재판정 2회 `review-obsreg 6878e79:reviews/_parts/…/financial-calc.md`
- 나머지 19행 — 8차 라운드 네 영역 part 기록(`review-obsreg e5a47d3`). 직전 리뷰 파일에서 그대로 옮긴다.

재실행해도 같은 결과가 나온다. 파일은 LF 로 쓴다.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REVIEW = ROOT / "reviews" / "ai-scorecard-2026-09-obsreg.md"
PART_REPO = ROOT.parent / "review-obsreg"
PART_COMMIT = "6878e79"
PART_PATH = "reviews/_parts/ai-scorecard-2026-09-obsreg/financial-calc.md"
# 8차 19행의 출처를 커밋으로 고정한다 — `HEAD` 로 두면 이 반영을 커밋한 뒤 재실행할 때 자기 자신을 읽는다.
PREV_COMMIT = "8445619"       # chore(approve): 체크리스트 23행을 8차 part 기록으로 전사

ROW_RE = re.compile(r"^\| \*?\*?(Q\d\d)\*?\*? \| (.+?) \| (.+) \|$")
OLD_ROW_RE = re.compile(r"^\| (Q\d\d) \| (.+?) \| (.+?) \| (.+) \|$")


def git_show(repo: Path, ref: str, path: str) -> str:
    out = subprocess.run(["git", "-C", str(repo), "show", f"{ref}:{path}"],
                         capture_output=True, check=True)
    return out.stdout.decode("utf-8")


def rows_from_part(text: str) -> dict[str, tuple[str, str]]:
    out: dict[str, tuple[str, str]] = {}
    for line in text.splitlines():
        m = ROW_RE.match(line)
        if m:
            out[m.group(1)] = (m.group(2), m.group(3))
    return out


def rows_from_prev(text: str) -> dict[str, tuple[str, str, str]]:
    out: dict[str, tuple[str, str, str]] = {}
    for line in text.splitlines():
        m = OLD_ROW_RE.match(line)
        if m:
            out[m.group(1)] = (m.group(2), m.group(3), m.group(4))
    return out


AREAS = {
    "사실·출처": ("8차 Gemini 독립 세션", "pass",
               "8차 결과를 그대로 둔다 — 그 뒤 반영(FIX-59~63)이 이 영역의 대상을 바꾸지 않았다. "
               "분담(부재 주장 전수, Claude 독립 세션)은 needs_fix 였고 FIX-58 2단계·FIX-59 로 전부 반영했다."),
    "재무 계산": ("9차 재판정 2회 · Claude 독립 세션(NTM-전망치조사 워크트리) · 기준 커밋 `96afd80`",
              "**needs_fix — FIX-63 으로 반영, 리뷰어 재확인 예정**",
              "**pass 가 아니다.** 재계산은 14개사 전부 불일치 0 이고 `results_hash`·`draft_hash` 도 리뷰어가 직접 "
              "계산해 맞췄다. **체크리스트 Q11 은 9차 fail 에서 pass 로 바뀌었다** — C-28·C-29 반영을 합성 관측과 "
              "시뮬레이션으로 재현해 확인했다. 그런데도 영역이 `needs_fix` 인 것은 **FIX-61·FIX-62 가 9차 지적을 "
              "고치면서 새 모순 둘을 남겼기 때문**이다(C-06 `summary` 의 자기모순 · `also_precedes_loss_band` 의 "
              "틀린 닫음). **이번 반영(FIX-63)으로 둘 다 고쳤고 전수로 훑어 같은 계열을 둘 더 고쳤다** — "
              "그 결과를 리뷰어가 다시 볼 예정이며, 이 칸은 그때까지 재판정 2회의 결과를 그대로 적는다."),
    "규칙 일관성": ("8차 Gemini 독립 세션", "pass",
                "8차 결과를 그대로 둔다. 7차에서 든 `선언에 소비자 없음` 세 건(C-11·C-13·C-24)은 FIX-57·FIX-58 에서 "
                "정리했다. **이 영역이 다시 볼 자리가 생겼다** — FIX-61~63 이 규칙 파일을 세 번 더 고쳤고 그중 "
                "자기모순 둘은 재무 계산 영역이 잡았다."),
    "출력·가독성": ("8차 Gemini 독립 세션", "pass",
                "8차 결과를 그대로 둔다. low 둘은 FIX-59 에서 반영했다. **빌드 HTML 은 이번 반영 뒤 다시 만들지 "
                "않았다** — C-06 `summary` 가 방법 표에 실리므로 build 단계에서 새 문면이 들어간다."),
}

CHECKLIST_NOTE = """**체크리스트 23행의 출처가 둘이다.** Q04·Q06·Q10·Q11 넷은 **9차 재무 계산 재판정 2회**(`review-obsreg`
커밋 `6878e79`, `reviews/_parts/ai-scorecard-2026-09-obsreg/financial-calc.md`)의 기록이고, 나머지 19행은 **8차 라운드**
네 영역 part 기록(같은 저장소 `e5a47d3`)을 그대로 옮긴 것이다. 이 파일에서 체크리스트를 다시 돌리지는 않았다 —
각 행의 근거 칸 끝에 어느 기록인지 적혀 있다. 담당은 겹치지 않는다: 규칙 일관성 15문항 · 재무 계산 4문항 ·
사실·출처 4문항.

**fail 이 11건이고 전부 승계 판단 예외다**(근거 칸에 긴장 번호가 있다). **Q11 은 9차 fail 에서 pass 로 바뀌었다** —
리뷰어가 C-28·C-29 반영을 합성 관측과 시뮬레이션으로 재현해 확인했고, 그 판정은 리뷰어의 것이지 우리가 고쳐 적은
것이 아니다. 바뀐 범위는 아래 발견 사항에 리뷰어의 문장 그대로 적었다."""

FINDINGS = """- **9차 재판정 2회의 발견 다섯 중 넷을 FIX-63 에서 반영했다.** 점수를 바꾼 것은 하나도 없다.
  - **[medium] 규칙이 스스로 모순됐다** — decisions C-06 `summary` 가 `BEP 후퇴가 … C-20 비상장 경로보다 앞선다` 로 적혀 있었다. FIX-61 이 그렇게 고쳐 넣었고 **같은 날 FIX-62 가 그 순서를 뒤집었다**(C-29). `policies.f9.g1_bep_retreat_precedence.what_is_true_now` 와 정반대였고, **이 문자열은 빌드 HTML 의 방법 표에 실린다**(`render_html.render_method`). 현재 사실로 고쳤다.
  - **[medium] `also_precedes_loss_band` 의 `순서가 관측되지 않는다` 가 사실이 아니었다** — `calc_f9.py` 의 `if bep_retreat:` 가 밴드를 아예 보지 않고 단락시켜, 손실률이 최심 밴드가 아니면 두 순서의 결과가 다르다. 리뷰어가 시뮬레이션으로 확인했고 우리도 재현했다(spacex-xai 에 `bep_retreat` 만 `yes` 로 바꾸면 F9 -3 → -4). 문면을 사실로 고치고 **틀린 주장을 굳혀 놓았던 테스트**(`tests/test_scorecard_fix61.py`)도 같이 고쳤다. **미결로 새로 등재하지 않고** TEN-RA6-01 의 범위에 상장사 자리를 명시해 넣었다(사유는 `g1_bep_retreat_precedence.why_no_new_pending_decision`).
  - **[low] FIX-62 의 재배열이 문서보다 한 칸 더 갔다** — 새 코드는 C-20 탐지를 `reviewed_sign == "profit"` 보다도 앞에 둔다. 리뷰어가 **새 순서가 더 맞다**고 봤으므로 코드는 그대로 두고 C-29 `scope.what_changed` 에 이 변화를 적었다. 이번 실행에 해당 기업은 없다.
  - **[low] 계획의 결정 표가 세 세대 전 문면이었다** — 머리말 해시만 손으로 고쳐 오는 동안 본문 표가 `BEP 후퇴→-5 … 명문화만 미결` 로 남아 있었다. 표를 현재 규칙에서 다시 만들었고(C-05·C-06·C-16 셋), `rule_hash_history` 와 손으로 쌓은 절은 유지했다.
  - **[low] 이 파일의 frontmatter 가 8차 값이었다** — 이번 재생성으로 맞췄다.
- **전수 조사에서 리뷰어가 짚지 않은 자리를 둘 더 찾아 고쳤다.** 재판정 2회가 `같은 종류를 전수로 훑으라` 고 해서 규칙·코드·문서에서 `bep_retreat`·`C-20`·우선순위를 말하는 문장을 모두 대조했다.
  - decisions **C-07** `implementation_status.routes.openai` 가 `G4 에 아예 닿지 않는다 — G1 에서 BEP 후퇴로 실패해 하한 -4` 로 적었다. C-29 뒤로 openai 는 anthropic 과 같은 경로이고 F9 는 -2 다. C-07 의 판정 자체는 바뀌지 않는다(`coverage_comparable=no` 로 두 겹 차단이 그대로 선다).
  - `render_common.method_lines` 가 `두 경로가 만나도 결과는 같다` 를 그대로 말해 초안·HTML 까지 흘렀다. 위 medium 둘째와 같은 오추론이다.
- **Q11 이 pass 로 바뀐 범위**(리뷰어 문장) — `실현된 노출이 없어졌다는 뜻이고 조항이 가리키는 자리가 전부 사라졌다는 뜻은 아니다. 상장사에 bep_retreat: yes 가 들어오면 측정된 손실률 밴드를 전망이 덮어쓰는 경로가 남아 있다. 오늘 그런 회사가 없고, 조항 충돌 자체는 TEN-RA6-01(open · recheck_at 2026-11 · 비 Claude 재판정 확정)로 등록돼 있다.`
- **리뷰어의 이해상충 고지**(그대로 옮긴다) — `openai F9 의 경로를 내가 고른 것이 아니다. 나는 9차에 체크리스트 Q11 을 fail 로 보고 승계 예외가 안 선다고만 적었고 점수는 건드리지 않았다. 이번에도 엔진이 사용자 결정(C-29)을 제대로 수행했는지만 확인했다. 결과가 Anthropic 경쟁사의 총점을 올리는 방향(2 → 4)이라는 점도 판정에 넣지 않았다.`
- **리뷰어가 확인하지 못한 것 여섯**이 part 에 그대로 남아 있다(oracle B종 약정 250,000M 의 출처 · alibaba `nonop_share` 저장값과 재계산의 차 · tsmc 20-F 원문 직접 대조 · `market_cap`·`ntm_per` 각 12건의 실측 · 비상장 2사의 `ps_ratio` · openai `operating_result_reviewed: loss` 의 근거). 어느 것도 이번 점수를 가르지 않는다."""

VERDICT = """- **재무 계산 영역은 아직 pass 가 아니다.** 9차 재판정 2회가 `needs_fix` 로 판정했고 사유였던 모순 둘을 이번 반영으로 고쳤다. **그 결과를 리뷰어가 다시 볼 예정이고, 그때까지 이 표의 결과를 바꿔 적지 않는다.**
- `status` 가 `needs_fix` 인 이유가 그것 하나다. 체크리스트 fail 11건은 전부 승계 판단 예외이고(근거 칸에 긴장 번호가 있다), **9차 fail 이던 Q11 은 리뷰어 재판정으로 pass 가 됐다.**
- **점수는 이번 반영에서 한 칸도 바뀌지 않았다.** 14개사 총점이 alphabet 15 · amazon 15 · meta 15 · microsoft 14 · anthropic 10 · tsmc 10 · spacex-xai 9 · nvidia 9 · apple 8 · alibaba 7 · palantir 6 · tesla 5 · openai 4 · oracle 2 그대로다.
- **같은 실수가 세 번째였다.** 8차·9차·재판정 2회가 연달아 `확정한 것을 미결이라고 적는다`·`뒤집은 것을 반대로 적는다`·`틀린 근거로 닫는다` 를 잡았다. 셋 다 규칙 문면이 코드보다 늦게 따라온 자리이고, **점수에는 한 번도 닿지 않았다.** 이번에는 전수로 훑어 리뷰어가 짚지 않은 둘을 더 찾았다.
- results_hash `{results8}…` · draft_hash `{draft8}…` 기준 검토. 자료·규칙·판단·초안이 바뀌면 이 리뷰는 무효다(D-10).
- **두 해시의 뜻이 다르다.** `results_hash` 는 `results.json` 에서 `results_hash` 키를 뺀 내용의 정렬 JSON 해시이고(`engine.sha256_obj`) **파일 바이트 sha256 과 다르다.** `draft_hash` 는 초안 **파일 바이트**의 sha256 이다(`stages.sha256_file`). 승인 해시 대조는 `stages.current_hashes` 가 같은 규약으로 다시 계산해 비교한다.
- `approval.json` 은 아직 만들어지지 않았다. **승인은 리뷰어 재확인 뒤에 간다.**"""


def main() -> int:
    # 템플릿 재생성부터 한다 — 채워진 파일에 다시 돌려도 같은 결과가 나오게 하기 위해서다.
    sys.path.insert(0, str(ROOT / "scripts"))
    from scorecard.stages import review_template
    review_template("ai-scorecard-2026-09-obsreg", force=True)

    text = REVIEW.read_text(encoding="utf-8")
    part = rows_from_part(git_show(PART_REPO, PART_COMMIT, PART_PATH))
    # 8차 19행은 커밋된 판본에서 읽는다 — 위에서 작업 트리를 덮어썼기 때문이다.
    prev = rows_from_prev(git_show(ROOT, PREV_COMMIT, "reviews/ai-scorecard-2026-09-obsreg.md"))
    assert sorted(part) == ["Q04", "Q06", "Q10", "Q11"], sorted(part)
    assert len(prev) == 23, len(prev)

    # 1) reviewers 네 줄
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if line.startswith('  - "fact-sources:'):
            lines[i] = '  - "fact-sources: pass (8차 · Gemini 독립 세션 — 그 뒤 반영이 이 영역 대상을 바꾸지 않았다)"'
        elif line.startswith('  - "financial-calc:'):
            lines[i] = ('  - "financial-calc: 9차 재판정 2회 needs_fix — Q11 은 fail 에서 pass 로. 영역 사유는 '
                        'FIX-61·62 가 남긴 규칙 자기모순 둘이고 FIX-63 으로 반영했다(리뷰어 재확인 예정). '
                        '재계산 14개사 불일치 0"')
        elif line.startswith('  - "rule-consistency:'):
            lines[i] = '  - "rule-consistency: pass (8차 · Gemini 독립 세션 — FIX-61~63 의 규칙 변경은 아직 안 봤다)"'
        elif line.startswith('  - "output-readability:'):
            lines[i] = '  - "output-readability: pass (8차 · Gemini 독립 세션, low 둘 반영 — HTML 재빌드는 build 단계)"'
    text = "\n".join(lines) + "\n"

    # 2) 검토 영역 표
    for area, (who, result, note) in AREAS.items():
        pat = re.compile(rf"^(\| {re.escape(area)} \| [^|]+ \|) +\| pending \| +\|$", re.M)
        text, n = pat.subn(lambda m: f"{m.group(1)} {who} | {result} | {note} |", text)
        assert n == 1, f"{area} 행 {n}건"

    # 3) 체크리스트 23행
    for qid in sorted(prev):
        # ID 칸은 평문으로 둔다 — 계약 검증이 `| Q11 |` 로 행을 찾는다. 강조는 결과 칸에 남는다.
        if qid in part:
            result, basis = part[qid]
            src = "9차 재무 계산 재판정 2회(`review-obsreg` `6878e79`)"
        else:
            _focus, result, basis = prev[qid]
            basis = re.sub(r"\s*—\s*8차[^|]*기록을 그대로 옮[^|]*$", "", basis).rstrip()
            src = "8차 part 기록(`review-obsreg` `e5a47d3`)"
        pat = re.compile(rf"^\| {qid} \| ([^|]+) \| pending \| +\|$", re.M)
        text, n = pat.subn(lambda m: f"| {qid} | {m.group(1).strip()} | {result} | {basis} — {src}. |", text)
        assert n == 1, f"{qid} 행 {n}건"

    # 4) 체크리스트 머리말 · 발견 사항 · 판정
    text = text.replace("## 체크리스트\n\n| ID |", f"## 체크리스트\n\n{CHECKLIST_NOTE}\n\n| ID |", 1)
    fm = dict(re.findall(r"^(results_hash|draft_hash): (\w+)$", text, re.M))
    verdict = VERDICT.format(results8=fm["results_hash"][:16], draft8=fm["draft_hash"][:16])
    for head, body in (("## 발견 사항", FINDINGS), ("## 판정", verdict)):
        pat = re.compile(rf"^{re.escape(head)}\n\n.*?(?=\n## |\Z)", re.S | re.M)
        text, n = pat.subn(f"{head}\n\n{body}\n", text)
        assert n == 1, f"{head} {n}건"

    REVIEW.write_text(text, encoding="utf-8", newline="\n")
    fails = len(re.findall(r"^\| Q\d\d \| [^|]+ \| fail \|", text, re.M))
    print(f"체크리스트 23행 기입 · fail {fails}건")
    print("검토 영역 4행 기입 · 재무 계산은 needs_fix 그대로")
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    sys.exit(main())
