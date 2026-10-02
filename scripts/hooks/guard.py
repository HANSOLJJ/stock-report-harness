# 가드레일 훅 5개의 판단 논리를 한 모듈로 모은 진입점 (uv run python scripts/hooks/guard.py <훅이름>)
"""훅 하나가 함수 하나다. 함수는 페이로드 dict 와 저장소 루트를 받아 Decision 을 돌려준다.

stdin 읽기, 출력 형식, exit code 는 main 만 맡는다. 예기치 않은 예외는 stderr 에 한 줄 남기고
exit 0 으로 끝낸다(fail-open). 훅 인프라 오류가 모든 도구를 막는 일을 없애기 위해서다.
"""
from __future__ import annotations

import fnmatch
import getpass
import glob
import hashlib
import io
import json
import os
import re
import shlex
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, TextIO

GUARD_REL = "scripts/hooks/guard.py"

# 도구 이름 별칭 표. 모르는 이름은 어느 쪽에도 없으므로 allow 된다. Antigravity·Muse 배선 때 여기를 채운다.
SHELL_TOOLS = {"Bash", "PowerShell"}
FILE_TOOLS = {"Write", "Edit", "MultiEdit", "NotebookEdit"}


# ------------------------------------------------------------------ 결정
@dataclass(frozen=True)
class Decision:
    kind: str  # allow | block | warn
    text: str = ""


def allow() -> Decision:
    return Decision("allow")


def block(reason: str) -> Decision:
    return Decision("block", reason)


def warn(message: str) -> Decision:
    return Decision("warn", message)


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
# docs/output-spec.md 는 2026-09-30 에 보호 목록에서 뺐다. 종목 리포트 출력 명세라 채점표 전환과 함께 삭제한다.
# 2026-09-30 레인 F: 승인된 실행이 쓰는 규칙(v1.5~v1.7), 이동한 기존 실행 두 폴더, 이력 파일을 더했다.
# v1.8 은 아직 승인된 실행이 없어 넣지 않는다. 첫 실행이 v1.8 로 승인되면 여기에 더한다.
# 2026-10-01 레인 H(F-3): 기준선은 승인 해시 밖의 재빌드 입력이다(실행에 triggers.json 이 없으면 기준선 트리거를 그린다). 폴더째 보호한다.
_PROTECTED_RUN_DIRS = ["output/ai-scorecard-2026-09-baseline", "output/ai-scorecard-2026-09-obsreg"]
_PROTECTED_TREES = [*_PROTECTED_RUN_DIRS, "scorecard/baseline"]
# 2026-10-02 docs/finance-style-guide.md(종목 리포트 시절 문체 지침)는 읽는 곳이 없어 파일과 함께 보호 목록에서 뺐다.
_PROTECTED_FILES = [
    "scorecard/rules/v1.5.json", "scorecard/rules/v1.6.json", "scorecard/rules/v1.7.json",
    "scorecard/history.csv",
]
_PROTECTED_LITERALS = [*_PROTECTED_FILES, *_PROTECTED_TREES, ".env", ".git", ".github/workflows"]
# 2026-10-01 레인 N(V2-3): 보호 경로 대조는 대소문자를 가리지 않는다. Windows 파일 시스템은 `Approval.json`·`.ENV` 를
# 같은 파일로 열고, 승인 검증은 `approval.json` 으로 읽는다.
_APPROVAL_FILE = re.compile(r"(^|/)approval\.json$", re.I)
_APPROVAL_FILE_IN_CMD = re.compile(r"(?<![\w.-])approval\.json\b", re.I)


def _is_protected(path: str) -> bool:
    path = path.replace("\\", "/").lower()
    return (
        path == ".env" or path.startswith(".env.") or path.startswith(".env/")
        or path == ".git" or path.startswith(".git/")
        or path == ".github/workflows" or path.startswith(".github/workflows/")
        or path in _PROTECTED_FILES
        or any(path == d or path.startswith(d + "/") for d in _PROTECTED_TREES)
        or bool(_APPROVAL_FILE.search(path))
    )


# 2026-10-01 레인 H(F-7): 셸 명령은 보호 경로가 "쓰기 대상" 일 때만 막는다. 쓰기 대상은 리다이렉션(`>`, `>>`)의 대상과
# 변경 동사의 인자다. 읽기만 하는 명령(cat·rg·git show 등)의 경로 언급은 통과한다. 인터프리터(python·node·uv run)는
# 스크립트 안의 쓰기를 셸에서 가릴 수 없으므로 보호 경로 문자열을 담기만 해도 막는다.
_WRITE_VERBS = {"rm", "mv", "cp", "tee", "touch", "truncate", "install", "chmod", "chown"}
# 2026-10-01 레인 J: PowerShell 쓰기 cmdlet 과 기본 별칭. 경로 인자(`-Path x`, `-Path:x`, 위치 인자)는 전부 쓰기 대상이다.
_PS_WRITE = {"set-content", "add-content", "out-file", "remove-item", "move-item", "copy-item", "new-item", "rename-item",
             "clear-content", "sc", "ac", "ri", "del", "erase", "rd", "rmdir", "mi", "move", "cpi", "copy", "ni", "rni",
             "ren", "clc"}
# 지우거나 옮기는 동사는 보호 경로를 품은 상위 폴더(`rm -rf output`, `Remove-Item -Recurse .`)도 쓰기 대상으로 본다.
_REMOVE_VERBS = {"rm", "rmdir", "rd", "remove-item", "ri", "del", "erase"}
_MOVE_VERBS = {"mv", "move-item", "mi", "move", "rename-item", "rni", "ren"}
# 복사는 원본을 읽기만 한다. 목적지만 쓰기 대상이다.
_COPY_VERBS = {"cp", "copy-item", "cpi", "copy", "install"}
_DEST_PARAM = re.compile(r"^-(?:dest(?:ination)?|newn(?:ame)?|t$|-target-directory)", re.I)
_GLOB_CHARS = set("*?[")
_XARGS_VALUE_OPTS = {"-n", "-I", "-i", "-L", "-l", "-P", "-d", "-E", "-e", "-s", "-a"}
_GIT_WRITE = {"checkout", "restore", "reset"}
_INTERPRETER = re.compile(r"^(?:python(?:3(?:\.\d+)?)?|py|node)$")
# 2026-10-01 레인 N(V2-4): 중첩 셸과 awk·dd 도 인자 안의 쓰기를 셸 단어로 가릴 수 없다. 인터프리터와 같이 보호 경로를 담기만 해도 막는다.
_NESTED = {"bash", "sh", "zsh", "dash", "ksh", "fish", "powershell", "pwsh", "cmd", "awk", "gawk", "mawk", "nawk", "dd"}
# 출력을 버리거나 다른 스트림으로 돌리는 리다이렉션 대상. 파일 쓰기가 아니다.
_NULL_SINKS = {"/dev/null", "nul", "$null", "&1", "&2", "1", "2", "-"}
# 쓰기 명령이 있을 때 경로가 숨는 자리: 따옴표 안, 명령 치환(`$(…)`·백틱), 변수 대입값(셸 `NAME=값`, PowerShell `$name = 값`).
_QUOTED = re.compile(r"'([^']*)'|\"((?:[^\"\\]|\\.)*)\"")
_SUBST = re.compile(r"\$\(([^()]*)\)|`([^`]*)`")
_ASSIGN_VALUE = re.compile(r"(?:^|[\s;&|(])(?:export\s+|local\s+|readonly\s+|declare\s+(?:-\w+\s+)*)?[A-Za-z_][A-Za-z0-9_]*=(\S+)")
_PS_ASSIGN_VALUE = re.compile(r"\$(?:env:)?[A-Za-z_][A-Za-z0-9_]*\s*=\s*([^;|\n]+)", re.I)


def _indirect_mentions(cmd: str) -> list[str]:
    """따옴표 안·명령 치환·변수 대입값에 나오는 보호 경로. 쓰기 명령이 있는 명령에서만 부른다(2026-10-01 레인 N, V2-4)."""
    parts: list[str] = []
    for rx in (_QUOTED, _SUBST, _ASSIGN_VALUE, _PS_ASSIGN_VALUE):
        parts += [g for m in rx.finditer(cmd) for g in m.groups() if g]
    return _protected_mentions(" ".join(parts))
_PREFIX_WORDS = {"env", "command", "exec", "nohup", "time"}
_CD_WORDS = {"cd", "pushd", "chdir", "set-location", "sl"}
_SHELL_PUNCT = ";&|()<>\n"
_ASSIGN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")


def _protected_mentions(text: str) -> list[str]:
    """문자열에 나오는 보호 경로 리터럴과 approval.json."""
    hits = [lit for lit in _PROTECTED_LITERALS if re.search(r"(?<![\w./-])" + re.escape(lit) + r"(?:/|\b)", text, re.I)]
    if _APPROVAL_FILE_IN_CMD.search(text):
        hits.append("approval.json")
    return hits


def _shell_segments(cmd: str) -> list[list[str]] | None:
    """명령을 제어 연산자(`;` `&&` `||` `|` `&` 괄호 줄바꿈)로 나눈 단어 목록들. 리다이렉션 기호는 단어로 남긴다. 따옴표가 맞지 않으면 None."""
    lex = shlex.shlex(cmd.replace("\\", "/"), posix=True, punctuation_chars=_SHELL_PUNCT)
    lex.whitespace = " \t\r"
    lex.whitespace_split = True
    lex.commenters = ""
    try:
        tokens = list(lex)
    except ValueError:
        return None
    segments: list[list[str]] = [[]]
    for tok in tokens:
        if tok and set(tok) <= set(_SHELL_PUNCT) and not set(tok) & set("<>"):
            segments.append([])
        else:
            segments[-1].append(tok)
    return [s for s in segments if s]


def _is_redirect(tok: str) -> bool:
    return bool(tok) and set(tok) <= set(_SHELL_PUNCT) and bool(set(tok) & set("<>"))


def _protected_anchors() -> list[str]:
    """보호 리터럴(파일·폴더)과 그 상위 폴더들. 글롭·상위 폴더 판정이 대조한다."""
    out: list[str] = []
    for lit in _PROTECTED_LITERALS:
        parts = lit.split("/")
        for i in range(1, len(parts) + 1):
            anchor = "/".join(parts[:i])
            if anchor not in out:
                out.append(anchor)
    return out


def _covers_protected(path: Path, root: Path) -> str | None:
    """`path` 가 보호 경로를 품은 상위 폴더(또는 저장소 루트·그 위)이면 품은 보호 경로 하나. 아니면 None."""
    try:
        p = path.resolve()
    except (OSError, ValueError):
        return None
    if p == root or p in root.parents:
        return "저장소 루트 아래 전체"
    try:
        rp = p.relative_to(root).as_posix().lower()
    except ValueError:
        return None
    for lit in _PROTECTED_LITERALS:
        if lit.startswith(rp + "/"):
            return lit
    if p.is_dir():
        found = next((f for f in p.rglob("*") if f.name.lower() == "approval.json"), None)
        if found is not None:
            return relpath(str(found), root)
    return None


def _glob_hits(target: str, base: Path, root: Path, *, covers: bool) -> list[str]:
    """글롭 단어가 가리킬 수 있는 보호 경로. 보호 리터럴(아직 없는 파일 포함)과 대조하고 파일 시스템에서 전개한다."""
    hits: list[str] = []
    rel_base = relpath(str(base), root)
    pattern = target if target.startswith("/") or rel_base in (".", "") else f"{rel_base}/{target}"
    pat_parts = pattern.removeprefix("./").lower().split("/")
    for anchor in _protected_anchors() if covers else _PROTECTED_LITERALS:
        parts = anchor.split("/")
        # 셸 글롭의 `*` 는 `/` 를 넘지 않는다. `**` 가 있을 때만 경로 전체를 한 번에 대조한다.
        if "**" in pattern:
            matched = fnmatch.fnmatchcase(anchor, "/".join(pat_parts))
        else:
            matched = len(parts) == len(pat_parts) and all(fnmatch.fnmatchcase(a, p) for a, p in zip(parts, pat_parts))
        if matched:
            hits.append(next((lit for lit in _PROTECTED_LITERALS if lit == anchor or lit.startswith(anchor + "/")), anchor))
    try:
        matches = glob.glob(str(base / target), recursive=True, include_hidden=True)
    except (OSError, ValueError):
        matches = []
    for m in matches:
        rp = relpath(m, root)
        if _is_protected(rp):
            hits.append(rp)
        elif covers:
            inside = _covers_protected(Path(m), root)
            if inside:
                hits.append(inside)
    return hits


def _target_hits(targets: list[str], base: Path, root: Path, *, covers: bool = False) -> list[str]:
    """쓰기 대상 단어 가운데 보호 경로. `cd` 뒤의 상대 경로는 바뀐 폴더 기준으로 푼다.

    2026-10-01 레인 J: 글롭(`*?[`)은 보호 경로와 맞으면 대상이다. `covers` 는 지우기·옮기기의 원본이라 보호 경로를 품은
    상위 폴더도 대상이다."""
    hits: list[str] = []
    for target in targets:
        found = _protected_mentions(target)
        if not found:
            try:
                rp = relpath(str(base / target), root)
            except (OSError, ValueError):
                rp = ""
            if rp and _is_protected(rp):
                found = [rp]
            elif covers:
                inside = _covers_protected(base / target, root)
                found = [inside] if inside else []
        if not found and set(target) & _GLOB_CHARS:
            found = _glob_hits(target, base, root, covers=covers)
        hits += found
    return hits


def _verb_of(words: list[str]) -> str:
    return words[0].rsplit("/", 1)[-1].lower().removesuffix(".exe") if words else ""


def _path_args(args: list[str]) -> tuple[list[str], list[str], list[str]]:
    """변경 동사의 인자를 (전부, 원본, 목적지) 로 나눈다. `-Name:값`·`--name=값` 은 값을 꺼내고, 목적지(`-Destination`·
    `-NewName`·`-t`·위치 인자 둘 이상일 때의 마지막)는 원본에서 뺀다. 스위치(`-f`, `-Recurse`)는 경로가 아니다."""
    every: list[str] = []
    positional: list[str] = []
    dests: list[str] = []
    want_dest = False
    for a in args:
        if a.startswith("-") and len(a) > 1:
            name, sep, value = a.partition("=") if a.startswith("--") else a.partition(":")
            is_dest = bool(_DEST_PARAM.match(name))
            if sep and value:
                every.append(value)
                (dests if is_dest else positional).append(value)
            want_dest = is_dest and not sep
            continue
        every.append(a)
        (dests if want_dest else positional).append(a)
        want_dest = False
    if not dests and len(positional) > 1:
        return every, positional[:-1], positional[-1:]
    return every, positional, dests


def _write_command(words: list[str]) -> tuple[list[str], list[str]] | None:
    """한 명령이 파일을 바꾸면 (쓰기 대상, 상위 폴더까지 보는 원본). 바꾸지 않으면 None."""
    verb, args = _verb_of(words), words[1:]
    if verb in _WRITE_VERBS or verb in _PS_WRITE:
        every, sources, dests = _path_args(args)
        if verb in _REMOVE_VERBS:
            return every, every
        if verb in _MOVE_VERBS:
            return every, sources
        if verb in _COPY_VERBS:
            return dests or every, []
        return every, []
    if verb == "sed" and any(a.startswith(("-i", "--in-place")) for a in args):
        return args, []
    if verb == "perl" and any(re.match(r"^-[A-Za-z]*i", a) for a in args):
        return args, []
    if verb == "find":
        starts = []
        for a in args:
            if a.startswith("-") or a in ("(", "!", ")"):
                break
            starts.append(a)
        expr = args[len(starts):]
        deletes = "-delete" in expr
        for i, a in enumerate(expr):
            if a in ("-exec", "-execdir", "-ok", "-okdir") and _write_command(expr[i + 1:]) is not None:
                deletes = True
        if deletes:
            return [*starts, *[a for a in expr if not a.startswith("-")]], starts or ["."]
    return None


def _xargs_inner(words: list[str]) -> list[str]:
    """`xargs [옵션] 명령 …` 의 명령 부분."""
    rest = words[1:]
    while rest and rest[0].startswith("-"):
        rest = rest[2:] if rest[0] in _XARGS_VALUE_OPTS else rest[1:]
    return rest


def _shell_violations(cmd: str, root: Path) -> list[str]:
    segments = _shell_segments(cmd)
    if segments is None:  # 나눌 수 없으면 쓰기 대상을 가릴 수 없다. 보호 경로를 언급하기만 해도 막는다
        return _protected_mentions(cmd.replace("\\", "/"))
    out: list[str] = []
    base = root
    parsed: list[tuple[list[str], list[str], Path]] = []
    writes = False   # 명령 어딘가에 쓰기(변경 동사·파일로 가는 리다이렉션)가 있는가
    for seg in segments:
        words: list[str] = []
        targets: list[str] = []
        i = 0
        while i < len(seg):
            if _is_redirect(seg[i]):
                if ">" in seg[i] and i + 1 < len(seg):  # 입력 리다이렉션(`<`, heredoc)은 읽기다
                    targets.append(seg[i + 1])
                    writes = writes or seg[i + 1].lower() not in _NULL_SINKS
                i += 2
                continue
            words.append(seg[i])
            i += 1
        while words and (_ASSIGN.match(words[0]) or words[0] in _PREFIX_WORDS):
            env = words[0] == "env"
            words = words[1:]
            while env and words and (words[0].startswith("-") or _ASSIGN.match(words[0])):
                words = words[2:] if words[0] in ("-u", "--unset") else words[1:]
        parsed.append((seg, words, base))
        verb = _verb_of(words)
        args = words[1:]
        write = _write_command(words)
        if verb in _CD_WORDS and args:
            base = base / args[-1]
        elif (verb == "uv" and args[:1] == ["run"]) or verb == "uvx" or _INTERPRETER.match(verb) or verb in _NESTED:
            out += _protected_mentions(" ".join(seg))
        elif write is not None:
            writes = True
            targets += write[0]
            out += _target_hits(write[1], base, root, covers=True)
        elif verb == "xargs" and _write_command(_xargs_inner(words)) is not None:
            # 2026-10-01 레인 J: xargs 로 이어지는 변경은 대상이 앞 명령의 출력이라 셸에서 알 수 없다. 명령 전체의
            # 보호 경로 언급과, 같은 명령의 다른 명령이 받은 경로(find·ls·git ls-files 의 시작 경로 등)가 보호 경로를
            # 품는지를 본다. 경로 인자가 없는 find·ls 는 현재 폴더를 훑는다.
            inner = _write_command(_xargs_inner(words))
            writes = True
            out += _protected_mentions(cmd.replace("\\", "/"))
            targets += inner[0]
            out += _target_hits(inner[1], base, root, covers=True)
            for _seg, other, other_base in parsed[:-1]:
                paths = [a for a in other[1:] if not a.startswith("-") and not set(a) & _GLOB_CHARS]
                if not paths and _verb_of(other) in ("find", "ls", "dir", "get-childitem", "gci"):
                    paths = ["."]
                out += _target_hits(paths, other_base, root, covers=True)
        elif verb == "git":
            git_base, rest = base, args
            while rest and rest[0].startswith("-"):
                if rest[0] in ("-C", "-c") and len(rest) > 1:
                    git_base = git_base / rest[1] if rest[0] == "-C" else git_base
                    rest = rest[2:]
                else:
                    rest = rest[1:]
            if rest and rest[0] in _GIT_WRITE:
                writes = True
                out += _target_hits(rest[1:], git_base, root)
        out += _target_hits(targets, base, root)
    # 2026-10-01 레인 N(V2-4): 쓰기가 있는 명령에서는 단어로 나눈 쓰기 대상 밖에 숨은 보호 경로도 막는다
    # (`RUN=<보호 실행>; rm -rf "$RUN"`, `rm $(echo <보호 경로>)`). 읽기만 하는 명령은 여기에 오지 않는다(F-7).
    if writes:
        out += _indirect_mentions(cmd.replace("\\", "/"))
    return out


def _init_force_approved(cmd: str, root: Path) -> list[str]:
    """`scorecard_cli.py init <slug> … --force` 가 승인 파일이 있는 실행을 가리키면 그 승인 파일들. 2026-10-01 레인 H(F-1).

    슬러그는 맨 이름이든 `output/<slug>` 경로든 마지막 경로 조각을 실행 폴더 이름으로 본다. argparse 는 옵션을
    줄여 쓸 수 있으므로(`--fo`) `--force` 의 접두도 같이 본다."""
    hits: list[str] = []
    for words in _shell_segments(cmd) or []:
        for i, word in enumerate(words):
            if word.rsplit("/", 1)[-1] != "scorecard_cli.py" or words[i + 1:i + 2] != ["init"]:
                continue
            rest = words[i + 2:]
            if not any(len(a) >= 4 and "--force".startswith(a) for a in rest):
                continue
            for name in sorted({a.rstrip("/").rsplit("/", 1)[-1] for a in rest if not a.startswith("-")}):
                if name and (root / "output" / name / "approval.json").is_file():
                    hits.append(f"output/{name}/approval.json")
    return hits


# 2026-10-01 레인 N(V2-1): 실행의 입력·산출물을 바꾸는 단계 명령. 맨 실행 이름도 `output/<이름>` 폴더로 풀어, 그 폴더에
# 유효한 승인이 있으면 막는다. 무효 승인은 막지 않는다 — 사람이 승인 페이지에서 판단을 고친 뒤 에이전트가 다시 돌리는 흐름이다.
_STAGE_WRITES = {"judge", "confirm", "calculate", "draft", "research", "review-template", "collect"}


def _option_value(rest: list[str], name: str) -> str | None:
    """argparse 처럼 줄여 쓴 옵션(`--k prices`, `--kind=prices`)의 값."""
    for i, a in enumerate(rest):
        key, sep, value = a.partition("=")
        if len(key) >= 3 and key.startswith("--") and name.startswith(key):
            return value if sep else (rest[i + 1] if i + 1 < len(rest) else "")
    return None


def _stage_changes_run(stage: str, rest: list[str]) -> bool:
    """이 단계 명령이 실행 폴더의 승인 대상 파일을 바꾸는가. CLI 의 `protect_approved_run` 호출 조건과 같다."""
    if stage == "review-template":
        return any(len(a) >= 3 and "--force".startswith(a) for a in rest)
    if stage == "collect":
        if any(len(a) >= 3 and "--dry-run".startswith(a) for a in rest):
            return False
        return (_option_value(rest, "--kind") or "all") in ("prices", "all")
    return stage in _STAGE_WRITES


def _approval_is_valid(root: Path, name: str) -> bool:
    """`output/<name>` 의 승인이 유효한가. 판정은 `scorecard.stages.approval_is_valid` 한 곳에 맡긴다(승인 해시 대조를
    훅에 다시 쓰지 않는다). 판정하지 못하면 예외가 난다 — 호출자가 막는다."""
    scripts = str(root / "scripts")
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    from scorecard import stages
    from scorecard.schema import load_json_strict

    d = stages.run_dir(name)
    if d.resolve() != (root / "output" / name).resolve():
        raise RuntimeError(f"훅 루트의 output/{name} 와 scorecard 가 읽는 실행 폴더 {d} 가 다르다")
    return stages.approval_is_valid(name, load_json_strict(d / "approval.json"))


def _stage_on_approved(cmd: str, root: Path) -> list[str]:
    """`scorecard_cli.py <단계> <실행>` 이 유효 승인 실행을 가리키면 그 이유들. 단계 명령일 때만 해시를 센다.

    판정 중 예외는 여기서 잡아 막는다(fail-closed). `main` 까지 올라가면 fail-open 으로 통과되기 때문이다."""
    hits: list[str] = []
    for words in _shell_segments(cmd) or []:
        for i, word in enumerate(words):
            stage = words[i + 1] if i + 1 < len(words) else ""
            if word.rsplit("/", 1)[-1] != "scorecard_cli.py" or not _stage_changes_run(stage, words[i + 2:]):
                continue
            for name in sorted({a.rstrip("/").rsplit("/", 1)[-1] for a in words[i + 2:] if not a.startswith("-")}):
                d = root / "output" / name
                try:
                    if not name or not d.is_dir() or not any(n.lower() == "approval.json" for n in os.listdir(d)):
                        continue
                    if _approval_is_valid(root, name):
                        hits.append(f"output/{name}: 승인이 유효한 실행에 {stage}")
                except Exception as exc:  # noqa: BLE001 — 판정하지 못하면 막는다
                    hits.append(f"output/{name}: 승인 유효성을 판정하지 못함({type(exc).__name__}: {exc}) — {stage}")
    return hits


# 승인·취소는 사람 행위다. 변경 기호가 없어도 명령 문자열에 있으면 막는다. confirm 은 막지 않는다 —
# 근거 확정은 승인이 아니고, 확정하면 해시가 바뀌어 사람이 다시 승인해야 한다.
_APPROVAL_CMD = re.compile(r"scorecard_cli\.py\s+(?:approve|revoke)\b|stages\.(?:approve|revoke)\b")
_IMPORT_BASELINE = re.compile(r"scorecard_cli\.py\s+import-baseline\b")


def protect_sensitive_files(payload: dict, *, root: Path) -> Decision:
    violations: list[str] = []
    for rp in extract_paths(payload, root):
        if _is_protected(rp):
            violations.append(rp)
    cmd = extract_command(payload)
    if cmd and _APPROVAL_CMD.search(cmd.replace("\\", "/")):
        return block("승인·취소는 사람이 `node server.js --approvals` 승인 페이지에서 한다. 에이전트는 approve·revoke 를 실행하지 않는다.")
    if cmd:
        approved = _init_force_approved(cmd, root)
        if approved:
            return block("승인된 실행을 init --force 로 덮어쓰면 승인 기록이 지워져 차단합니다: " + ", ".join(approved)
                         + ". 새 slug 로 init 한다. 승인된 실행의 재작성은 사람이 한다.")
        staged = _stage_on_approved(cmd, root)
        if staged:
            return block("승인이 유효한 실행의 입력·산출물을 바꾸는 단계 명령이라 차단합니다(승인이 무효가 되거나 지워진다): "
                         + "; ".join(staged) + ". 새 slug 로 init --from-run 해서 이어 간다. 승인된 실행의 재작성은 사람이 한다.")
        if _IMPORT_BASELINE.search(cmd.replace("\\", "/")):
            return block("import-baseline 은 보호 트리 scorecard/baseline/ 를 다시 쓴다. 기준선은 승인 해시 밖의 재빌드 입력이라 "
                         "승인된 실행의 재빌드 리포트가 승인 없이 바뀐다. 사람이 한다.")
        violations += _shell_violations(cmd, root)
    if not violations:
        return allow()
    uniq: list[str] = []
    for v in violations:
        if v not in uniq:
            uniq.append(v)
    return block("보호 경로 수정 시도를 차단합니다: " + ", ".join(uniq) + ". 보호 대상: .env*, .git/, .github/workflows/, "
                 "**/approval.json, scorecard/rules/v1.5~v1.7.json, scorecard/history.csv, scorecard/baseline/, "
                 "output/ai-scorecard-2026-09-baseline/, output/ai-scorecard-2026-09-obsreg/.")


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


def lock_owner() -> str:
    """실행 잠금의 소유자. `scorecard.stages.lock_owner` 와 같은 규칙이다(훅은 scorecard 를 import 하지 않는다)."""
    for key in ("SCORECARD_AGENT", "ORCA_TERMINAL_HANDLE"):
        value = os.environ.get(key, "").strip()
        if value:
            return value
    return getpass.getuser()


def _lock_holder(base: Path) -> str | None:
    """`output/<slug>/.lock` 의 소유자. 잠금이 없으면 None, 읽을 수 없으면 빈 문자열(누구의 것도 아니다)."""
    lock = base / ".lock"
    if not lock.is_file():
        return None
    try:
        data = json.loads(lock.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return ""
    owner = data.get("owner") if isinstance(data, dict) else None
    return owner if isinstance(owner, str) else ""


def enforce_plan(payload: dict, *, root: Path) -> Decision:
    problems: list[str] = []
    locked: list[str] = []
    me: str | None = None
    for rp in extract_paths(payload, root):
        parsed = _slug_dir_parts(rp)
        if not parsed:
            continue
        slug, rest = parsed
        base = root / "output" / slug
        holder = _lock_holder(base)
        if holder is not None:
            me = me if me is not None else lock_owner()
            if holder != me:
                locked.append(f"output/{slug}: 다른 소유자({holder or '알 수 없음'})의 실행 잠금이 있음")
                continue
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
    if locked:
        return block("다른 에이전트가 맡은 실행 묶음이라 쓰기를 차단합니다. " + "; ".join(locked[:6]) + ". 인수하려면 CLI 단계를 --take-lock 으로 실행한다.")
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
# 2026-10-02 전: ("output/*/draft.md", "output/*/judgments.json", "output/*/evidence/*.json") 이었고 대상 판정
# `_advice_target` 은 어느 폴더든 `judgments.json` 과 `evidence/*.json` 을 받았다. 수집 원문 `candidates.json` 의 뉴스 제목
# "Buy Now" 에 걸려 셸 명령마다 block 이 났고, `tests/fixtures/evidence/` 의 라벨 표본도 대상이었다. 우리가 쓴 글만 본다.
_ADVICE_GLOBS = ("output/*/draft.md", "output/*/judgments.json", "output/*/evidence/evidence.json")
_ADVICE_KINDS = {"draft.md": "draft", "judgments.json": "text", "evidence/evidence.json": "evidence"}
# evidence.json 에서 우리가 쓰는 칸. title·excerpt 는 원문 그대로라 보지 않는다.
_OUR_EVIDENCE_FIELDS = ("relevance", "conditional_impact", "counter_evidence", "unverified", "horizon")
_VERBATIM_LINE = re.compile(r'^\s*"(?:title|excerpt)"\s*:.*$', re.M)
# 초안에서 기사 제목을 그대로 옮기는 절(render_md.render_draft).
_QUOTED_SECTIONS = {"인용 근거", "References"}


def _advice_kind(rp: str) -> str | None:
    """검사 대상이면 종류(draft·text·evidence), 아니면 None. `output/<run>/` 아래의 세 파일만 본다."""
    parts = rp.replace("\\", "/").split("/")
    if len(parts) < 3 or parts[0] != "output":
        return None
    return _ADVICE_KINDS.get("/".join(parts[2:]))


def _evidence_text(text: str) -> str:
    """evidence.json 에서 우리가 쓴 칸만 모은다. JSON 으로 읽지 못하면(Edit 조각 등) 원문 칸 줄만 빼고 돌려준다."""
    try:
        items = json.loads(text)["items"]
        if not isinstance(items, list):
            raise TypeError
    except (ValueError, KeyError, TypeError):
        return _VERBATIM_LINE.sub("", text)
    out: list[str] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        for key in _OUR_EVIDENCE_FIELDS:
            value = item.get(key)
            if isinstance(value, str):
                out.append(value)
            elif isinstance(value, list):
                out += [v for v in value if isinstance(v, str)]
    return "\n".join(out)


def _draft_text(text: str) -> str:
    """초안에서 기사 제목을 옮긴 절을 뺀다."""
    out: list[str] = []
    skip = False
    for line in text.splitlines():
        if line.startswith("## "):
            skip = line[3:].strip() in _QUOTED_SECTIONS
        if not skip:
            out.append(line)
    return "\n".join(out)


def _advice_text(kind: str, text: str) -> str:
    if kind == "evidence":
        return _evidence_text(text)
    return _draft_text(text) if kind == "draft" else text


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
        kind = _advice_kind(rp)
        if kind is None:
            continue
        for key in ("content", "new_string"):
            value = ti.get(key)
            if isinstance(value, str) and value:
                candidates[f"{rp} (proposed {key})"] = _advice_text(kind, value)
        edits = ti.get("edits")
        if isinstance(edits, list):
            combined = "\n".join(str(e.get("new_string") or "") for e in edits if isinstance(e, dict))
            if combined:
                candidates[f"{rp} (proposed edits)"] = _advice_text(kind, combined)
        file_path = root / rp
        if file_path.is_file():
            try:
                candidates[rp] = _advice_text(kind, file_path.read_text(encoding="utf-8"))
            except (UnicodeDecodeError, OSError):
                pass
    # 셸 명령 뒤에는 무엇이 바뀌었는지 모르므로 대상 파일 전체를 훑는다.
    if payload.get("tool_name") in SHELL_TOOLS:
        for pattern in _ADVICE_GLOBS:
            for path in root.glob(pattern):
                try:
                    rel = path.relative_to(root).as_posix()
                    candidates[rel] = _advice_text(_advice_kind(rel) or "text", path.read_text(encoding="utf-8"))
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


# ------------------------------------------------------------------ 진입점
HOOKS: dict[str, Callable[..., Decision]] = {
    "block_dangerous_bash": block_dangerous_bash,
    "protect_sensitive_files": protect_sensitive_files,
    "enforce_plan": enforce_plan,
    "forbid_financial_advice": forbid_financial_advice,
    "remind_review": remind_review,
}
# 2026-10-02 저장소 메모리(memory/ 폴더, enforce_memory·inject_memory_context 훅, 검증기)를 없앴다. 쓰는 기준이 모호했고
# 일지는 주입되지 않았으며 한 세션에 약 12만 자를 문맥에 넣었다. 교훈은 AGENTS.md 와 스킬에 규칙 한 줄로 적는다.


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
