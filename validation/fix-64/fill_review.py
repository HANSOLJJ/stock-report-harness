# FIX-64: 리뷰 파일을 최종 결과로 채운다 — 네 영역 pass · 재무 계산은 재판정 3회 끝에 pass
"""체크리스트 23행의 출처가 둘이다.

- Q04·Q06·Q10·Q11 — 9차 재무 계산 **최종 판정**(재판정 3회) `review-obsreg ce0fd57:reviews/_parts/…/financial-calc.md`
- 나머지 19행 — 8차 라운드 네 영역 part 기록(`review-obsreg e5a47d3`). 커밋된 판본에서 옮긴다.

재실행해도 같은 결과가 나온다. 파일은 LF 로 쓴다.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SLUG = "ai-scorecard-2026-09-obsreg"
REVIEW = ROOT / "reviews" / f"{SLUG}.md"
PART_REPO = ROOT.parent / "review-obsreg"
PART_COMMIT = "ce0fd57"        # review(part): financial-calc 최종 판정 — pass (기준 f313060)
PART_PATH = f"reviews/_parts/{SLUG}/financial-calc.md"
# 8차 19행의 출처를 커밋으로 고정한다 — `HEAD` 로 두면 이 반영을 커밋한 뒤 재실행할 때 자기 자신을 읽는다.
PREV_COMMIT = "8445619"        # chore(approve): 체크리스트 23행을 8차 part 기록으로 전사

ROW_RE = re.compile(r"^\| \*?\*?(Q\d\d)\*?\*? \| (.+?) \| (.+) \|$")
OLD_ROW_RE = re.compile(r"^\| (Q\d\d) \| (.+?) \| (.+?) \| (.+) \|$")


def git_show(repo: Path, ref: str, path: str) -> str:
    out = subprocess.run(["git", "-C", str(repo), "show", f"{ref}:{path}"], capture_output=True, check=True)
    return out.stdout.decode("utf-8")


AREAS = {
    "사실·출처": ("8차 · Gemini 독립 세션", "pass",
               "발견 사항 없음. 분담(부재 주장 전수, Claude 독립 세션)은 needs_fix 였고 FIX-58 2단계·FIX-59 로 전부 "
               "반영했다 — 상대방 제출본까지 범위를 넓혀 다시 훑었고 등록할 사실은 없었다."),
    "재무 계산": ("9차 · Claude 독립 세션(NTM-전망치조사 워크트리) · **재판정 3회** · 최종 기준 커밋 `f313060`",
              "pass",
              "**8차 needs_fix → FIX-59·61·63 반영 → 재판정 3회 끝에 pass.** 경과가 길었던 이유는 반영이 매번 "
              "새 문면 모순을 남겼기 때문이다 — 8차는 지적이 기록 수준이었고, 9차는 FIX-59 가 확정한 것을 세 자리가 "
              "`미결` 이라 적는 것과 순손실 상장사 트랙을 잡았으며(FIX-61), 재판정 2회는 FIX-61·62 가 남긴 자기모순 "
              "둘을 잡았다(FIX-63). **마지막 판정에서 리뷰어가 고쳤다는 주장을 믿지 않고 직접 다시 훑었다** — "
              "정규식 다섯 갈래로 산출물 10곳·코드 19파일·문서 전체를 독립 전수해 **살아 있는 잔존 0건**을 확인했고, "
              "재계산 14개사 불일치 0 · 새 해시 직접 계산 일치 · 점수 페이로드가 `96afd80` 과 **바이트 동일**인 것도 "
              "기계로 확인했다. 새 발견 low 하나(`bep_retreat` 의 도달 범위를 문면이 좁게 적음)는 **FIX-64 에서 "
              "닫았다** — 아래 판정 절에 적었다."),
    "규칙 일관성": ("8차 · Gemini 독립 세션", "pass",
                "발견 사항 없음. 7차에서 든 `선언에 소비자 없음` 세 건(C-11·C-13·C-24)은 FIX-57·FIX-58 에서 정리했다. "
                "**FIX-61~64 가 바꾼 규칙 문면은 이 영역이 아직 보지 않았다** — 재무 계산 영역이 자기 범위"
                "(F9 우선순위 서술·C-06·C-07·C-29·TEN-RA6-01)만 확인했다고 밝혔고, 그 밖의 변경은 전부 기록·서술이며 "
                "점수에 닿지 않는다."),
    "출력·가독성": ("8차 · Gemini 독립 세션", "pass",
                "low 둘 반영. 자동 산출 factor 의 기준선 참고 블록이 옛 점수로 시작하던 것을 FIX-59 에서 현재 점수가 "
                "첫 줄에 오게 고쳤고, HTML 이해상충 문구의 동적 연산은 정상 동작을 확인했다(조치 없음). "
                "**HTML 은 이 승인 뒤 build 단계에서 새로 만들어진다** — C-06 `summary` 가 방법 표에 실리므로 "
                "이번 라운드에 고친 문면이 그때 들어간다."),
}

CHECKLIST_NOTE = """**체크리스트 23행의 출처가 둘이다.** Q04·Q06·Q10·Q11 넷은 **9차 재무 계산 최종 판정**(재판정 3회,
`review-obsreg` 커밋 `ce0fd57`)의 기록이고, 나머지 19행은 **8차 라운드** 네 영역 part 기록(같은 저장소 `e5a47d3`)을
그대로 옮긴 것이다. 이 파일에서 체크리스트를 다시 돌리지는 않았다 — 각 행의 근거 칸 끝에 어느 기록인지 적혀 있다.
담당은 겹치지 않는다: 규칙 일관성 15문항 · 재무 계산 4문항 · 사실·출처 4문항.

**fail 이 11건이고 전부 승계 판단 예외다**(근거 칸에 긴장 번호가 있다). **Q11 은 9차 fail 에서 pass 로 바뀌었다** —
리뷰어가 C-28·C-29 반영을 합성 관측과 시뮬레이션으로 재현해 확인했고, 그 판정은 리뷰어의 것이지 우리가 고쳐 적은
것이 아니다."""

FINDINGS = """- **9라운드에 걸친 리뷰가 여기서 끝난다.** 네 영역이 모두 pass 이고 마지막 발견까지 닫았다.
- **마지막 판정의 새 발견 하나를 FIX-64 에서 고쳤다**(아래 판정 절에 판단 근거를 적었다).
- **이월 두 건은 이미 등록돼 있다.** 리뷰어가 `이월, 등록됨` 으로 분류한 것이고 새로 할 일이 없다.
  - oracle F6 P1 = 25.967109 가 밴드 경계 25 에서 **+3.87%** 로 허용폭 3% 밖이라 경계 표시가 안 붙는다. 이 한 칸이 oracle 총점 2 와 3 을 가른다. **미결 `C-27`** 에 alibaba G3(+3.32%)와 함께 **표본 둘**로 적혀 있다.
  - `oracle.undrawn_credit.fix54` 가 null 인데 `calc_f9._runway` 의 `undrawn or 0.0` 이 0 으로 센다. **결정 `C-04`** 가 완충을 `현금 + 확정 미인출 여신` 으로 좁혀 **설계대로**이고, 뒤집히려면 39,769M 이상이 필요하다는 크기까지 관측 `basis.null_counts_as_zero` 에 적혀 있다. 보존 ORCL companyfacts 에 해당 태그 사실이 없어 `unverified` 라벨도 맞다.
- **리뷰어가 확인하지 못한 것 여섯**이 최종 part 에 그대로 남아 있다 — oracle B종 약정 250,000M 의 출처(C-26) · alibaba `nonop_share` 저장값과 재계산의 차 · tsmc 20-F 원문 직접 대조 · `market_cap`·`ntm_per` 각 12건의 실측 · 비상장 2사의 `ps_ratio` · **FIX-61~64 가 바꾼 규칙 문면의 규칙 일관성 검토**. 어느 것도 이번 점수를 가르지 않는다.
- **리뷰어의 이해상충 고지**(그대로 옮긴다) — `openai F9 의 경로를 내가 고른 것이 아니다. 나는 9차에 체크리스트 Q11 을 fail 로 보고 승계 예외가 안 선다고만 적었고 점수는 건드리지 않았다. 이번에도 엔진이 사용자 결정(C-29)을 제대로 수행했는지만 확인했다. 결과가 Anthropic 경쟁사의 총점을 올리는 방향(2 → 4)이라는 점도 판정에 넣지 않았다.`
- **작성자 이해상충** — 이 채점표를 Anthropic 이 만든 Claude 가 작성했고 Anthropic 이 채점 대상에 들어 있다(채점규칙 384행). Anthropic 점수에 걸린 긴장은 비 Claude 세션이 재판정한다(TEN-RC-02 · TEN-RC3-01 · TEN-RA4-01 · TEN-RA5-01)."""

VERDICT = """- **네 영역이 모두 pass 이고 체크리스트 fail 11건은 전부 승계 판단 예외다**(근거 칸에 긴장 번호가 있다). `status: pass` 의 요건을 갖췄다.
- **마지막 새 발견(low)을 넘기지 않고 이번에 고쳤다.** 리뷰어 지적은 `bep_retreat` 가 미치는 범위를 문면이 실제보다 좁게 적는다는 것이었다 — 네 자리가 `손실률 밴드보다 앞선다` 로 **적자 맥락만** 서술하는데, `g1_pass = (not bep_retreat) and (margin is None or margin > 0)` 이라 실제로는 **영업흑자 회사의 G1 통과도 막는다.** 재현했다: microsoft(상장 · 측정 영업이익률 **+46.78%**)에 `bep_retreat` 만 `yes` 로 바꾸면 F9 가 **0 에서 -4 로** 떨어지고 경로에 `result: fail` 이 양수 마진과 함께 기록된다.
  - **고치는 쪽을 고른 이유** — 넘기면 리뷰어가 지적한 위험(`TEN-RA6-01` 이 흑자 경우를 빠뜨린 채 2026-11 에 판정된다)이 그대로 남는다. 반대로 고치는 비용은 문면 네 자리뿐이고 **코드를 손대지 않아 점수가 바뀔 수 없다.**
  - **고친 자리 넷** — `policies.f9.g1_bep_retreat_precedence.also_precedes_loss_band`(제목을 `G1 통과와 손실률 밴드 둘 다보다 앞선다` 로) · `decisions` C-06 `summary`(빌드 HTML 방법 표에 실린다) · `render_common.method_lines`(초안·HTML) · `TEN-RA6-01.also_covers_listed`(11월 재판정 범위에 흑자 경우를 넣었다). `calc_f9.py` 의 `영업적자 구간` 주석에도 흑자가 들어온다는 사실을 적었다.
  - **동작은 바꾸지 않았다.** 이 처리는 채점규칙 470행의 OR 조건 읽기와 어긋나지 않고 FIX-59 때부터 같다 — **새로 생긴 결함이 아니라 서술이 좁았던 것**이다. 근본 질문(전망이 측정된 실적을 덮어써도 되는가)은 `TEN-RA6-01`(open · 2026-11 · 비 Claude 재판정 확정)이 그대로 들고 있다.
  - **점수 불변을 두 겹으로 확인했다** — 14개사 총점이 그대로이고, `results.json` 의 `companies`·`ranking` 정렬 JSON 해시가 `f313060` 과 **동일**하다(`5ee4b01048acf647`). 바뀐 최상위 키는 `input_hashes`·`results_hash` 둘뿐이고 `warnings_count` 도 165 그대로다.
- **이월 두 건은 새로 할 일이 없다** — oracle F6 P1 경계 +3.87% 는 미결 `C-27` 의 표본으로, oracle 미인출 여신 null 을 0 으로 세는 것은 결정 `C-04` 의 설계대로로 각각 등록돼 있다(위 발견 사항).
- **9라운드 동안 점수를 바꾼 것은 일곱 자리뿐이다**(계획의 `규칙·자료 변경이 점수에 닿은 자리` 표). 나머지 반영은 전부 기록·서술이었고, 재무 계산 영역이 세 번 연속 잡은 것도 모두 문면이 코드보다 늦게 따라온 자리였다.
- results_hash `{results8}…` · draft_hash `{draft8}…` 기준 검토. 자료·규칙·판단·초안이 바뀌면 이 리뷰는 무효다(D-10).
- **두 해시의 뜻이 다르다.** `results_hash` 는 `results.json` 에서 `results_hash` 키를 뺀 내용의 정렬 JSON 해시이고(`engine.sha256_obj`) **파일 바이트 sha256 과 다르다.** `draft_hash` 는 초안 **파일 바이트**의 sha256 이다(`stages.sha256_file`). 승인 해시 대조는 `stages.current_hashes` 가 같은 규약으로 다시 계산해 비교한다.
- **`status: pass` 가 뜻하지 않는 것.** 체크리스트 Q01~Q23 을 이 파일에서 다시 돌린 것이 아니다 — 8차·9차 part 기록을 출처를 밝혀 옮겼다. 승계 판단 11건은 **긴장 등록과 재검토 시점만 기계로 확인**한 것이고, `이번 실행이 잣대를 바꾸지 않았다`는 조건은 리뷰어가 판정했다(AGENTS.md 71행)."""


def main() -> int:
    sys.path.insert(0, str(ROOT / "scripts"))
    from scorecard.stages import review_template
    review_template(SLUG, force=True)          # 채워진 파일에 다시 돌려도 같은 결과가 나오게 한다

    text = REVIEW.read_text(encoding="utf-8")
    part = {m.group(1): (m.group(2), m.group(3))
            for m in map(ROW_RE.match, git_show(PART_REPO, PART_COMMIT, PART_PATH).splitlines()) if m}
    prev = {m.group(1): (m.group(2), m.group(3), m.group(4))
            for m in map(OLD_ROW_RE.match, git_show(ROOT, PREV_COMMIT, f"reviews/{SLUG}.md").splitlines()) if m}
    assert sorted(part) == ["Q04", "Q06", "Q10", "Q11"], sorted(part)
    assert len(prev) == 23, len(prev)

    # 1) status · reviewers
    text = text.replace("status: needs_fix", "status: pass", 1)
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if line.startswith('  - "fact-sources:'):
            lines[i] = '  - "fact-sources: pass (8차 · Gemini 독립 세션)"'
        elif line.startswith('  - "financial-calc:'):
            lines[i] = ('  - "financial-calc: pass (9차 · Claude 독립 세션 · 재판정 3회 · 최종 기준 커밋 f313060) '
                        '— 8차 needs_fix 에서 FIX-59·61·63 반영을 거쳐 pass. 잔존 전수 0건 · 재계산 14개사 불일치 0 · '
                        '점수 페이로드 96afd80 과 바이트 동일"')
        elif line.startswith('  - "rule-consistency:'):
            lines[i] = '  - "rule-consistency: pass (8차 · Gemini 독립 세션 — FIX-61~64 의 규칙 문면 변경은 미검토)"'
        elif line.startswith('  - "output-readability:'):
            lines[i] = '  - "output-readability: pass (8차 · Gemini 독립 세션, low 둘 반영 — HTML 은 build 에서 재생성)"'
    text = "\n".join(lines) + "\n"

    # 2) 검토 영역 표
    for area, (who, result, note) in AREAS.items():
        pat = re.compile(rf"^(\| {re.escape(area)} \| [^|]+ \|) +\| pending \| +\|$", re.M)
        text, n = pat.subn(lambda m: f"{m.group(1)} {who} | {result} | {note} |", text)
        assert n == 1, f"{area} 행 {n}건"

    # 3) 체크리스트 23행. ID 칸은 평문으로 둔다 — 계약 검증이 `| Q11 |` 로 행을 찾는다.
    for qid in sorted(prev):
        if qid in part:
            result, basis = part[qid]
            src = "9차 재무 계산 최종 판정 · 재판정 3회(`review-obsreg` `ce0fd57`)"
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
    passes = len(re.findall(r"^\| [^|]+ \| [^|]+ \| [^|]+ \| pass \|", text, re.M))
    print(f"검토 영역 {passes}행 pass · 체크리스트 23행 기입(fail {fails}건) · status: pass")
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    sys.exit(main())
