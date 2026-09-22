"""대상 파일 해시·수정시각 재확인 (읽기 전후 비교용). 읽기 전용."""
import hashlib
import os
import datetime

TARGETS = [
    r"C:\Users\noble\orca\workspaces\stock-report-harness\worker\scorecard\baseline\v1.5\scores.json",
    r"C:\Users\noble\orca\workspaces\stock-report-harness\worker\scorecard\baseline\v1.5\observations.json",
    r"C:\Users\noble\orca\workspaces\stock-report-harness\worker\scorecard\baseline\v1.5\triggers.json",
    r"C:\Users\noble\orca\workspaces\stock-report-harness\worker\scorecard\baseline\v1.5\import-report.md",
    r"C:\Users\noble\orca\workspaces\stock-report-harness\worker\scorecard\companies.json",
    r"C:\Users\noble\orca\workspaces\stock-report-harness\worker\scorecard\rules\v1.5.json",
    r"C:\Users\noble\orca\workspaces\stock-report-harness\worker\scorecard\runs\ai-scorecard-2026-09-baseline\sources.json",
    r"C:\Users\noble\orca\workspaces\stock-report-harness\worker\scorecard\runs\ai-scorecard-2026-09-baseline\observations.json",
    r"E:\sourcecode\01_side_project\stock-report-harness\AI_company_analysis_factor\AI기업_채점표_v1.5.md",
    r"E:\sourcecode\01_side_project\stock-report-harness\AI_company_analysis_factor\AI기업_채점표_v1.5.html",
    r"E:\sourcecode\01_side_project\stock-report-harness\AI_company_analysis_factor\AI기업_채점규칙_v1.5.md",
    r"E:\sourcecode\01_side_project\stock-report-harness\AI_company_analysis_factor\AI기업_채점표_HANDOVER.md",
    r"E:\sourcecode\01_side_project\stock-report-harness\AI_company_analysis_factor\AI기업_채점자동화_구현계획.md",
    r"E:\sourcecode\01_side_project\stock-report-harness\AI_company_analysis_factor\AGENTS.md",
]

# 검증 시작 시점(첫 해시 기록)에 측정한 값
BEFORE = {
    "scores.json": ("DAA46F7B26E4EE3C", "2026-09-08T01:47:31Z"),
    "observations.json": ("8F1B932850BA51E0", "2026-09-08T01:47:31Z"),
    "triggers.json": ("9784A48331021415", "2026-09-08T01:47:31Z"),
    "import-report.md": ("3AC20E1050FCFE20", "2026-09-08T01:47:31Z"),
    "companies.json": ("2BD6BAF36CA1B361", "2026-09-08T01:21:26Z"),
    "v1.5.json": ("D671F22D309B2826", "2026-09-08T01:22:54Z"),
    "AI기업_채점표_v1.5.md": ("D28C5416786B5D93", "2026-09-07T02:50:05Z"),
    "AI기업_채점규칙_v1.5.md": ("57BEB84AD8C291F3", "2026-09-07T02:50:49Z"),
    "AI기업_채점표_HANDOVER.md": ("3E5190C2CB4A4F8E", "2026-09-08T00:32:41Z"),
    "AI기업_채점자동화_구현계획.md": ("B921372B7EE9A5D2", "2026-09-07T08:07:13Z"),
    "AGENTS.md": ("0DA9F593F4BF8AE2", "2026-09-04T03:02:53Z"),
}

print("%-16s %-40s %-22s %s" % ("판정", "파일", "SHA-256(앞16)", "mtime(UTC)"))
changed = []
for p in TARGETS:
    if not os.path.exists(p):
        print("%-16s %-40s MISSING" % ("-", os.path.basename(p)))
        changed.append(p)
        continue
    h = hashlib.sha256(open(p, "rb").read()).hexdigest()
    m = datetime.datetime.utcfromtimestamp(os.path.getmtime(p)).strftime("%Y-%m-%dT%H:%M:%SZ")
    base = os.path.basename(p)
    # runs/observations.json 은 baseline/observations.json 과 이름이 같아 부모 디렉터리로 구분
    if base == "observations.json" and "runs" in p:
        b = None
    else:
        b = BEFORE.get(base)
    if b is None:
        verdict = "(사전기록없음)"
    elif b[0] == h[:16].upper() and b[1] == m:
        verdict = "UNCHANGED"
    else:
        verdict = "CHANGED"
        changed.append(p)
    print("%-16s %-40s %-22s %s" % (verdict, base, h[:16], m))

print("\n변경 감지: %d건 %s" % (len(changed), changed or ""))
