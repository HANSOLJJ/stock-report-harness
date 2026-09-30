# 가드레일 훅 9개의 판단 논리를 한 모듈로 모은 진입점 (uv run python scripts/hooks/guard.py <훅이름>)
"""훅 하나가 함수 하나다. 함수는 페이로드 dict 와 저장소 루트를 받아 Decision 을 돌려준다.

stdin 읽기, 출력 형식, exit code 는 main 만 맡는다. 예기치 않은 예외는 stderr 에 한 줄 남기고
exit 0 으로 끝낸다(fail-open). 훅 인프라 오류가 모든 도구를 막는 일을 없애기 위해서다.
"""
from __future__ import annotations

import hashlib
import io
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, TextIO

GUARD_REL = "scripts/hooks/guard.py"

# 도구 이름 별칭 표. 모르는 이름은 어느 쪽에도 없으므로 allow 된다. Antigravity·Muse 배선 때 여기를 채운다.
SHELL_TOOLS = {"Bash", "PowerShell"}
FILE_TOOLS = {"Write", "Edit", "MultiEdit", "NotebookEdit"}

MAX_TOPIC_CHARS = 6000
MAX_TOTAL_CHARS = 18000


# ------------------------------------------------------------------ 결정
@dataclass(frozen=True)
class Decision:
    kind: str  # allow | block | warn | context
    text: str = ""


def allow() -> Decision:
    return Decision("allow")


def block(reason: str) -> Decision:
    return Decision("block", reason)


def warn(message: str) -> Decision:
    return Decision("warn", message)


def context(text: str) -> Decision:
    return Decision("context", text)


# ------------------------------------------------------------------ 공통 유틸
def relpath(value: str, root: Path) -> str:
    """경로를 저장소 상대 POSIX 형태로 바꾼다. 저장소 밖이면 절대 POSIX 경로를 돌려준다."""
    p = Path(value).expanduser()
    if not p.is_absolute():
        p = root / p
    try:
        return p.resolve().relative_to(root).as_posix()
    except Exception:
        return p.resolve().as_posix()


def extract_command(payload: dict) -> str:
    """셸 계열 도구의 명령 문자열을 돌려준다. 다른 도구이거나 없으면 빈 문자열이다."""
    if payload.get("tool_name") not in SHELL_TOOLS:
        return ""
    cmd = (payload.get("tool_input") or {}).get("command")
    return cmd if isinstance(cmd, str) else ""


def extract_paths(payload: dict, root: Path) -> list[str]:
    """파일 계열 도구가 건드리는 경로를 저장소 상대 경로로 돌려준다. 중복은 뺀다."""
    if payload.get("tool_name") not in FILE_TOOLS:
        return []
    ti = payload.get("tool_input") or {}
    raw: list[str] = []
    for key in ("file_path", "path", "notebook_path"):
        value = ti.get(key)
        if isinstance(value, str) and value.strip():
            raw.append(value.strip())
    for key in ("file_paths", "paths"):
        value = ti.get(key)
        if isinstance(value, list):
            raw.extend(str(v).strip() for v in value if str(v).strip())
    out: list[str] = []
    for value in raw:
        rp = relpath(value, root)
        if rp not in out:
            out.append(rp)
    return out


def read_frontmatter(path: Path) -> dict[str, str]:
    """파일 맨 앞 --- 블록의 `키: 값` 최상위 줄을 읽는다. 블록이 없거나 파일이 없으면 빈 dict 다."""
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return {}
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    out: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return out
        m = re.match(r"^([A-Za-z0-9_]+):\s*(.*?)\s*$", line)
        if m:
            out[m.group(1)] = m.group(2).strip("\"'")
    return {}  # 닫는 --- 가 없으면 frontmatter 로 보지 않는다


def _slug_dir_parts(rp: str) -> tuple[str, str] | None:
    """`output/<slug>/<나머지>` 이면 (slug, 나머지) 를 돌려준다."""
    parts = rp.split("/", 2)
    if len(parts) == 3 and parts[0] == "output" and parts[1] and parts[2]:
        return parts[1], parts[2]
    return None


# ------------------------------------------------------------------ 1. 위험 명령 차단
_DANGEROUS = [
    (
        re.compile(r"(?:^|[;&|()\s])rm\s+(?:-[^\s]*[rR][^\s]*[fF][^\s]*|-[^\s]*[fF][^\s]*[rR][^\s]*)(?:\s+--[^\s]+)*\s+(?:/|/\*|['\"]?/['\"]?)(?:\s|$)"),
        "루트 디렉터리를 대상으로 한 rm -rf 계열 명령은 되돌릴 수 없어 차단합니다.",
    ),
    (
        re.compile(r"\brm\b[^\n]*--no-preserve-root"),
        "rm --no-preserve-root 옵션은 시스템 파괴 위험이 있어 차단합니다.",
    ),
    (
        re.compile(r"(?:^|[;&|()\s])sudo(?:\s|$)"),
        "sudo 실행은 권한 상승을 동반하므로 이 프로젝트 훅에서 차단합니다.",
    ),
    (
        re.compile(r"\b(?:curl|wget)\b[^\n|;]*(?:https?://|www\.)[^\n|;]*\|\s*(?:env\s+)?(?:sh|bash|zsh|ksh|fish|python(?:3)?|ruby|perl|node)\b", re.I),
        "원격 스크립트를 다운로드해 셸/인터프리터로 바로 파이프 실행하는 패턴은 차단합니다. 파일로 저장해 검토한 뒤 실행하세요.",
    ),
    (
        re.compile(r"\bgit\s+push\b[^\n]*(?:--force(?:-with-lease|-if-includes)?\b|-f\b)"),
        "강제 push(git push --force/-f/--force-with-lease)는 원격 히스토리를 덮어쓸 수 있어 차단합니다.",
    ),
    (
        re.compile(r"\bgit\s+push\b[^\n]*\s\+[^\s]+"),
        "강제 refspec(git push +branch)은 원격 히스토리를 덮어쓸 수 있어 차단합니다.",
    ),
]


def block_dangerous_bash(payload: dict, *, root: Path) -> Decision:
    cmd = extract_command(payload)
    if not cmd:
        return allow()
    for pattern, reason in _DANGEROUS:
        if pattern.search(cmd):
            return block(reason)
    return allow()


# ------------------------------------------------------------------ 2. 보호 경로
# docs/output-spec.md 는 2026-09-30 에 보호 목록에서 뺐다. 근거 수집 계층 도입으로 이 문서를 계속 고쳐야 한다.
_PROTECTED_LITERALS = ["docs/finance-style-guide.md", ".env", ".git", ".github/workflows"]


def _is_protected(path: str) -> bool:
    path = path.replace("\\", "/")
    return (
        path == ".env" or path.startswith(".env.") or path.startswith(".env/")
        or path == ".git" or path.startswith(".git/")
        or path == ".github/workflows" or path.startswith(".github/workflows/")
        or path == "docs/finance-style-guide.md"
    )


_MUTATING = re.compile(r"(^|[;&|]\s*)(cat\s*>|printf\b|echo\b|tee\b|sed\s+-i\b|perl\s+-pi\b|python\b|python3\b|node\b|rm\b|mv\b|cp\b|install\b|touch\b|truncate\b|chmod\b|chown\b|git\s+checkout\b|git\s+restore\b|git\s+reset\b)")
_REDIRECT = re.compile(r"(^|[^<>])>{1,2}\s*[^&]")


def protect_sensitive_files(payload: dict, *, root: Path) -> Decision:
    violations: list[str] = []
    for rp in extract_paths(payload, root):
        if _is_protected(rp):
            violations.append(rp)
    cmd = extract_command(payload)
    # 셸 명령은 보호 경로를 언급하면서 파일을 바꾸는 것처럼 보일 때만 막는다.
    if cmd and (_MUTATING.search(cmd) or _REDIRECT.search(cmd)):
        for literal in _PROTECTED_LITERALS:
            if re.search(r"(?<![\w./-])" + re.escape(literal) + r"(?:/|\b)", cmd):
                violations.append(literal)
    if not violations:
        return allow()
    uniq: list[str] = []
    for v in violations:
        if v not in uniq:
            uniq.append(v)
    return block("보호 경로 수정 시도를 차단합니다: " + ", ".join(uniq) + ". 보호 대상: .env*, .git/, .github/workflows/, docs/finance-style-guide.md.")


# ------------------------------------------------------------------ 3. 단계 순서
_BUILD_CMD = re.compile(r"(?:uv\s+run\s+(?:--frozen\s+)?)?python3?(?:\s+-X\s+utf8)?\s+scripts/build_report\.py\s+(\S+)")

# 파일 이름 → 먼저 있어야 하는 같은 폴더의 파일. plan.md 와 그 밖의 산출물은 게이트가 없다.
_REQUIRES = {
    "research.md": ["plan.md"],
    "draft.md": ["plan.md", "research.md"],
    "review.md": ["plan.md", "research.md", "draft.md"],
}
_BUILD_ONLY = {"report.html", "audit.md"}


def _review_is_pass(review: Path) -> bool:
    fm = read_frontmatter(review)
    return (
        fm.get("status") == "pass"
        and fm.get("review_type") == "separate-session-4way"
        and fm.get("review_execution") == "separate_subagent_sessions"
    )


def enforce_plan(payload: dict, *, root: Path) -> Decision:
    problems: list[str] = []
    for rp in extract_paths(payload, root):
        parsed = _slug_dir_parts(rp)
        if not parsed:
            continue
        slug, rest = parsed
        base = root / "output" / slug
        if rest in _BUILD_ONLY:
            problems.append(f"{rp}: 직접 쓰기 금지(빌드 명령으로만 생성)")
        elif rest in _REQUIRES:
            missing = [name for name in _REQUIRES[rest] if not (base / name).is_file()]
            if missing:
                problems.append(f"{rp}: 선행 산출물 누락({', '.join(missing)})")
    cmd = extract_command(payload)
    for m in _BUILD_CMD.finditer(cmd):
        slug = m.group(1).strip("\"'`;&|)")
        if not _review_is_pass(root / "output" / slug / "review.md"):
            problems.append(f"output/{slug}/report.html: 빌드 전 pass 상태의 separate-session-4way 리뷰 필요(output/{slug}/review.md)")
    if not problems:
        return allow()
    return block("파이프라인 순서(plan → research → draft → review → build)를 위반해 차단합니다. " + "; ".join(problems[:6]))


# ------------------------------------------------------------------ 4. 투자 권유 표현 금지
_ADVICE_PATTERNS = [
    r"지금\s*사야\s*합니다", r"반드시\s*사(?:세요|야)", r"사야\s*합니다",
    r"매수\s*적기", r"매수\s*(?:추천|권장)", r"지금\s*매수",
    r"100\s*%\s*수익", r"확실한\s*수익", r"보장된\s*수익", r"수익\s*보장", r"무조건\s*수익",
    r"원금\s*손실\s*없음", r"원금\s*보장", r"리스크\s*없는",
    r"마지막\s*기회", r"지금\s*안\s*사면\s*후회", r"놓치면\s*후회",
    r"guaranteed\s+returns?", r"risk[-\s]?free\s+(?:profit|return|investment)", r"\bbuy\s+now\b", r"last\s+chance",
]
_ADVICE_RX = [re.compile(p, re.I) for p in _ADVICE_PATTERNS]
_POLICY_LINE = re.compile(r"(아닙니다|아님|하지\s*않|목적으로\s*하지|금지|차단|피해야|사용하지\s*않|not\s+(?:investment\s+)?advice|not\s+guarantee)", re.I)
_ADVICE_GLOBS = ("output/*/draft.md", "output/*/judgments.json", "output/*/evidence/*.json")


def _advice_target(rp: str) -> bool:
    rp = rp.replace("\\", "/")
    parts = rp.split("/")
    name = parts[-1]
    if len(parts) == 3 and parts[0] == "output" and name == "draft.md":
        return True
    if name == "judgments.json":
        return True
    return name.endswith(".json") and len(parts) >= 2 and parts[-2] == "evidence"


def _policy_context(text: str, start: int, end: int) -> bool:
    line_start = text.rfind("\n", 0, start) + 1
    line_end = text.find("\n", end)
    if line_end == -1:
        line_end = len(text)
    return bool(_POLICY_LINE.search(text[line_start:line_end]))


def forbid_financial_advice(payload: dict, *, root: Path) -> Decision:
    ti = payload.get("tool_input") or {}
    candidates: dict[str, str] = {}
    # PreToolUse 는 쓰려는 문자열을, PostToolUse 는 실제 파일을 본다.
    for rp in extract_paths(payload, root):
        if not _advice_target(rp):
            continue
        for key in ("content", "new_string"):
            value = ti.get(key)
            if isinstance(value, str) and value:
                candidates[f"{rp} (proposed {key})"] = value
        edits = ti.get("edits")
        if isinstance(edits, list):
            combined = "\n".join(str(e.get("new_string") or "") for e in edits if isinstance(e, dict))
            if combined:
                candidates[f"{rp} (proposed edits)"] = combined
        file_path = root / rp
        if file_path.is_file():
            try:
                candidates[rp] = file_path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                pass
    # 셸 명령 뒤에는 무엇이 바뀌었는지 모르므로 대상 파일 전체를 훑는다.
    if payload.get("tool_name") in SHELL_TOOLS:
        for pattern in _ADVICE_GLOBS:
            for path in root.glob(pattern):
                try:
                    candidates[path.relative_to(root).as_posix()] = path.read_text(encoding="utf-8")
                except Exception:
                    continue
    findings: list[tuple[str, str]] = []
    for name, text in candidates.items():
        for rx in _ADVICE_RX:
            m = rx.search(text)
            while m and _policy_context(text, m.start(), m.end()):
                m = rx.search(text, m.end())
            if m:
                findings.append((name, m.group(0)))
                break
    if not findings:
        return allow()
    preview = "; ".join(f'{name}: "{match}"' for name, match in findings[:5])
    return block("투자 권유/수익 보장/FOMO 금지 표현을 차단합니다. " + preview)


# ------------------------------------------------------------------ 5. 리뷰 무효화 경고
_REVIEW_INPUT_NAMES = {"draft.md", "judgments.json", "observations.json"}


def _review_input(rest: str) -> bool:
    if rest in _REVIEW_INPUT_NAMES:
        return True
    return rest.startswith("evidence/") and rest.endswith(".json") and rest.count("/") == 1


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _results_hash(path: Path) -> str | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    value = data.get("results_hash") if isinstance(data, dict) else None
    return value if isinstance(value, str) else None


def remind_review(payload: dict, *, root: Path) -> Decision:
    if payload.get("tool_name"):
        slugs: list[str] = []
        for rp in extract_paths(payload, root):
            parsed = _slug_dir_parts(rp)
            if parsed and _review_input(parsed[1]) and parsed[0] not in slugs:
                slugs.append(parsed[0])
        if not slugs:
            return allow()
        return warn("; ".join(f"output/{s}: 리뷰 해시가 무효화됨. /score-review {s} 가 필요하다." for s in slugs))
    # Stop: 도구 없이 불린다. 리뷰가 가리키는 해시가 지금 산출물과 다른 폴더를 찾는다.
    problems: list[str] = []
    for review in sorted((root / "output").glob("*/review.md")):
        slug = review.parent.name
        fm = read_frontmatter(review)
        results = _results_hash(review.parent / "results.json")
        if fm.get("results_hash") and results and fm["results_hash"] != results:
            problems.append(f"output/{slug}: review.md 의 results_hash 가 results.json 과 다름")
        draft = review.parent / "draft.md"
        if fm.get("draft_hash") and draft.is_file() and fm["draft_hash"] != _sha256_file(draft):
            problems.append(f"output/{slug}: review.md 의 draft_hash 가 draft.md 와 다름")
    if not problems:
        return allow()
    slugs = sorted({p.split(":")[0].split("/")[1] for p in problems})
    return warn("리뷰 해시가 무효화됨. " + "; ".join(problems[:6]) + ". " + ", ".join(f"/score-review {s}" for s in slugs) + " 가 필요하다.")


# ------------------------------------------------------------------ 6. memory 검증
def enforce_memory(payload: dict, *, root: Path) -> Decision:
    hit = [rp for rp in extract_paths(payload, root) if rp.startswith(("memory/_daily/", "memory/topics/"))]
    if not hit:
        return allow()
    validator = root / "scripts" / "validate_memory.py"
    if not validator.is_file():
        return allow()
    proc = subprocess.run(
        [sys.executable, "-X", "utf8", str(validator)],
        cwd=root, text=True, capture_output=True, encoding="utf-8", errors="replace",
    )
    if proc.returncode == 0:
        return allow()
    detail = (proc.stdout + proc.stderr).strip()
    return block("memory 파일 변경 후 scripts/validate_memory.py 검증 실패. " + detail[:1200])


# ------------------------------------------------------------------ 7. memory 문맥 주입
_DOMAIN_RULES: list[dict[str, Any]] = [
    {
        "name": "날짜/기간/yfinance 시간 동기화",
        "file": "time-sync.md",
        "patterns": [
            r"\b(period_start|period_end|created_at|interval=1d|yfinance|price-chart)\b",
            r"최근\s*\d+\s*(일|개월|년)",
            r"기간|날짜|거래일|일봉|차트|주가|가격",
        ],
    },
    {
        "name": "외부 API 호출",
        "file": "external-api.md",
        "patterns": [
            r"\b(OpenAI|ElevenLabs|API|image_gen|imagegen|yfinance|requests|fetch|curl)\b",
            r"뉴스|토스증권|Google News|외부\s*호출|API\s*호출",
        ],
    },
    {
        "name": "hero 이미지 워크플로",
        "file": "image-workflow.md",
        "patterns": [
            r"\b(hero|selected-image|image-manifest|image_gen|imagegen)\b",
            r"이미지|프롬프트|후보\s*3|선택된\s*이미지|비주얼",
        ],
    },
    {
        "name": "경제리포트 파이프라인 순서",
        "file": "pipeline-order.md",
        "patterns": [
            r"/score-(?:plan|research|calculate|draft|review|approve|build|goal|extend|diff|add-company)\b",
            r"\b(plan|research|drafts|reviews|output)/",
            r"빌드|리서치|드래프트|리뷰|경제리포트|HTML|파이프라인",
        ],
    },
    {
        "name": "빌드/설치 오류",
        "file": "build-errors.md",
        "patterns": [
            r"\b(uv sync|pnpm install|npm install|pip install|node|python|build|lint|typecheck|pytest)\b",
            r"빌드|설치|의존성|패키지|테스트|검증",
        ],
    },
    {
        "name": "git workflow",
        "file": "git-workflow.md",
        "patterns": [
            r"\b(git|commit|push|pull request|PR|branch|merge|rebase)\b",
            r"커밋|푸시|브랜치|병합",
        ],
    },
    {
        "name": "guardrails/hook/schema",
        "file": "guardrails.md",
        "patterns": [
            r"\b(hook|validator|schema|AGENTS\.md|CLAUDE\.md|settings\.json)\b",
            r"가드레일|검증기|스키마|차단|훅|메모리|memory",
        ],
    },
]


def _extract_prompt(payload: dict) -> str:
    for key in ("prompt", "message", "user_prompt", "input"):
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value
    return json.dumps(payload, ensure_ascii=False)


def _compact_topic(path: Path) -> str:
    text = path.read_text(encoding="utf-8").strip()
    if len(text) <= MAX_TOPIC_CHARS:
        return text
    return text[:MAX_TOPIC_CHARS].rstrip() + "\n\n... (topic이 길어 앞부분만 자동 주입함)"


def inject_memory_context(payload: dict, *, root: Path) -> Decision:
    prompt = _extract_prompt(payload)
    matched = [r for r in _DOMAIN_RULES if any(re.search(p, prompt, re.I) for p in r["patterns"])]
    if not matched:
        return context(
            "[Memory System]\n"
            "관련 memory topic 자동 매칭 없음. 실패/고비용 재시도 관측이 생기면 "
            "memory/_daily/YYYY-MM-DD.md에 1 entry = 1 관측으로 기록함."
        )
    loaded: list[tuple[str, str, str]] = []
    missing: list[tuple[str, str]] = []
    for rule in matched:
        path = root / "memory" / "topics" / rule["file"]
        rel = f"memory/topics/{rule['file']}"
        if path.is_file():
            content = _compact_topic(path)
            if content:
                loaded.append((rule["name"], rel, content))
            else:
                missing.append((rule["name"], f"{rel} (빈 파일)"))
        else:
            missing.append((rule["name"], f"{rel} (없음)"))
    lines = [
        "[Memory System 자동 주입]",
        "작업 전 아래 topic 관측을 우선 적용함. 무관한 topic은 로드하지 않았음.",
    ]
    total = sum(len(line) + 1 for line in lines)
    for name, rel, content in loaded:
        block_text = f"\n--- {name}: {rel} ---\n{content}\n"
        if total + len(block_text) > MAX_TOTAL_CHARS:
            lines.append("\n... (memory 자동 주입 총량 제한으로 일부 topic 생략함)")
            break
        lines.append(block_text)
        total += len(block_text)
    if missing:
        lines.append("\n[Memory topic 상태]")
        for name, rel in missing:
            lines.append(f"- {name}: {rel}")
    lines.append(
        "\n[기록 규칙] 실패/재시도 비용이 큰 관측은 memory/_daily/YYYY-MM-DD.md에 append하고, "
        "반복/고비용 패턴은 memory/topics/{slug}.md로 추출함."
    )
    return context("\n".join(lines))


# ------------------------------------------------------------------ 진입점
HOOKS: dict[str, Callable[..., Decision]] = {
    "block_dangerous_bash": block_dangerous_bash,
    "protect_sensitive_files": protect_sensitive_files,
    "enforce_plan": enforce_plan,
    "forbid_financial_advice": forbid_financial_advice,
    "remind_review": remind_review,
    "enforce_memory": enforce_memory,
    "inject_memory_context": inject_memory_context,
}


def find_root() -> Path | None:
    """cwd 기준 git 루트를 찾는다. 루트에 guard.py 가 없으면 이 저장소가 아니므로 None 이다."""
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if proc.returncode != 0 or not proc.stdout.strip():
        return None
    root = Path(proc.stdout.strip()).resolve()
    return root if (root / GUARD_REL).is_file() else None


def _emit(decision: Decision, payload: dict, out: TextIO) -> int:
    if decision.kind == "block":
        print(json.dumps({"decision": "block", "reason": decision.text}, ensure_ascii=False), file=out)
        print(decision.text, file=sys.stderr)  # exit 2 에서는 stderr 가 모델에게 전달된다
        return 2
    if decision.kind == "warn":
        event = payload.get("hook_event_name") or payload.get("hookEventName") or ("PostToolUse" if payload.get("tool_name") else "Stop")
        if event == "Stop":
            print(json.dumps({"systemMessage": decision.text}, ensure_ascii=False), file=out)
        else:
            print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": decision.text}}, ensure_ascii=False), file=out)
        return 0
    if decision.kind == "context":
        print(json.dumps({"hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": decision.text}}, ensure_ascii=False), file=out)
        return 0
    return 0


def main(argv: list[str], *, stdin: TextIO | None = None, stdout: TextIO | None = None, root: Path | None = None) -> int:
    out = stdout or sys.stdout
    try:
        name = argv[0] if argv else ""
        func = HOOKS.get(name)
        if func is None:
            print(f"guard: 알 수 없는 훅 '{name}'", file=sys.stderr)
            return 0
        if root is None:
            root = find_root()
            if root is None:
                return 0
        raw = (stdin or io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8", errors="replace")).read()
        try:
            payload = json.loads(raw) if raw.strip() else {}
        except ValueError:
            payload = {"prompt": raw}
        if not isinstance(payload, dict):
            payload = {}
        return _emit(func(payload, root=root), payload, out)
    except Exception as exc:  # fail-open: 훅 오류로 도구가 막히지 않게 한다
        print(f"guard: {argv[0] if argv else ''} 오류를 무시하고 통과시킴: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass
    raise SystemExit(main(sys.argv[1:]))
