# 보호 훅의 쓰기 대상 판정(2026-10-01 레인 J): PowerShell cmdlet·find -delete·xargs·글롭·상위 폴더 삭제를 잠근다. 읽기는 통과한다
from __future__ import annotations

import unittest

from tests.test_hooks import TempRootCase, guard, shell

OBS = "output/ai-scorecard-2026-09-obsreg"
APPROVAL = f"{OBS}/approval.json"
RULE = "scorecard/rules/v1.7.json"
BASELINE = "scorecard/baseline/v1.5/triggers.json"


class WriteFormsTest(TempRootCase):
    def setUp(self) -> None:
        super().setUp()
        for rel in (APPROVAL, f"{OBS}/draft.md", RULE, "scorecard/rules/v1.8.json", BASELINE, "scorecard/history.csv",
                    "output/ai-scorecard-2026-10-new/draft.md", "output/ai-scorecard-2026-10-done/approval.json",
                    "tmp-lane-j/a.pyc", "docs/finance-style-guide.md", "notes.md"):
            self.put(rel)

    def kind(self, cmd: str, tool: str = "PowerShell") -> str:
        return guard.protect_sensitive_files(shell(tool, cmd), root=self.root).kind

    def assert_kinds(self, expected: str, cmds: list[str], tool: str = "PowerShell") -> None:
        for cmd in cmds:
            with self.subTest(tool=tool, cmd=cmd):
                self.assertEqual(self.kind(cmd, tool), expected)

    def test_powershell_cmdlets_writing_protected_paths_blocked(self):
        win = APPROVAL.replace("/", "\\")
        self.assert_kinds("block", [
            f"Set-Content -Path {win} -Value x",
            f"Set-Content {RULE} x",
            f"Add-Content -LiteralPath scorecard\\history.csv -Value x",
            f"'x' | Out-File -FilePath {BASELINE}",
            f"'x' | Out-File -FilePath:{BASELINE} -Encoding utf8",
            f"Remove-Item {win}",
            f"Remove-Item -Path {OBS}\\draft.md -Force",
            f"Move-Item -Path {RULE} -Destination x.json",
            f"Copy-Item x.json -Destination {APPROVAL}",
            f"Copy-Item -Path x.json -Destination:{APPROVAL}",
            f"New-Item -ItemType File -Path .env -Force",
            f"Rename-Item -Path {RULE} -NewName v1.7.bak.json",
            f"Clear-Content {BASELINE}",
            f"del {win}",
            f"ri {RULE}",
            f"sc {RULE} x",
            f"Get-Content a.json | Set-Content {RULE}",
        ])

    def test_powershell_reads_and_unprotected_writes_pass(self):
        self.assert_kinds("allow", [
            f"Get-Content {APPROVAL}",
            f"Get-ChildItem {OBS}",
            f"Select-String -Path {BASELINE} -Pattern x",
            f"Copy-Item -Path {APPROVAL} -Destination C:\\tmp\\approval-copy.txt",
            "Set-Content -Path scorecard\\rules\\v1.8.json -Value x",
            "Remove-Item -Recurse -Force tmp-lane-j",
            "Move-Item -Path notes.md -Destination output\\",
            "New-Item -ItemType Directory -Force output\\ai-scorecard-2026-10-new\\evidence",
        ])

    def test_removing_a_folder_that_holds_protected_paths_blocked(self):
        for tool in ("Bash", "PowerShell"):
            self.assert_kinds("block", [
                "rm -rf output", "rm -rf scorecard/rules", "rm -rf .", "rm -rf ..", "Remove-Item -Recurse -Force output",
                "Remove-Item -Recurse scorecard", "mv output output-old", "Move-Item -Path scorecard -Destination x",
                "rm -rf output/ai-scorecard-2026-10-done",   # 승인 파일이 든 실행 폴더
                f"cd {OBS} && rm -rf ..",
            ], tool=tool)
        self.assert_kinds("allow", ["rm -rf output/ai-scorecard-2026-10-new", "mv notes.md output/notes.md",
                                    "cp -r output/ai-scorecard-2026-09-obsreg /tmp/copy"], tool="Bash")

    def test_find_delete_and_exec(self):
        self.assert_kinds("block", [
            "find . -name '*.pyc' -delete",          # 저장소 전체 — 보호 경로를 품는다
            "find output -name draft.md -delete",
            f"find {OBS} -type f -delete",
            "find scorecard -path '*/baseline/*' -delete",
            f"find {OBS} -name '*.md' -exec rm {{}} +",
            "find scorecard/rules -name 'v1.*' -exec mv {} /tmp \\;",
        ], tool="Bash")
        self.assert_kinds("allow", [
            "find tmp-lane-j -name '*.pyc' -delete",
            f"find {OBS} -name '*.md'",
            "find . -name '*.json' -exec cat {} +",
        ], tool="Bash")

    def test_xargs_into_a_write_command(self):
        self.assert_kinds("block", [
            f"find {OBS} -name '*.md' | xargs rm",
            "find . -name '*.json' | xargs rm -f",
            f"ls {OBS} | xargs -I{{}} rm {OBS}/{{}}",
            "git ls-files scorecard/rules | xargs sed -i s/a/b/",
            "echo x | xargs -n 1 cp -t scorecard/baseline/v1.5",
            f"cat list.txt | xargs -0 Remove-Item -Path {RULE}",
        ], tool="Bash")
        self.assert_kinds("allow", [
            "find tmp-lane-j -name '*.pyc' | xargs rm",
            f"find {OBS} -name '*.md' | xargs wc -l",
            f"echo {APPROVAL} | xargs cat",
        ], tool="Bash")

    def test_globs_matching_protected_paths(self):
        for tool in ("Bash", "PowerShell"):
            self.assert_kinds("block", [
                "rm scorecard/rules/v1.*.json",
                "rm scorecard/rules/*",
                "rm -rf output/*",
                "rm -rf output/ai-scorecard-2026-09-*",
                "Remove-Item -Recurse sc*",
                "cp x.json scorecard/rules/v1.[5-7].json",
                "rm .env*",
                "rm docs/*.md",
                "rm -rf scorecard/**/triggers.json",
            ], tool=tool)
            self.assert_kinds("allow", [
                "rm *.md",                                # 루트의 md 만 — docs/ 아래로 넘어가지 않는다
                "rm tmp-lane-j/*.pyc",
                "rm scorecard/rules/v1.8*",
                "rm -rf output/ai-scorecard-2026-10-new/*",
                "cat scorecard/rules/*.json",
            ], tool=tool)


if __name__ == "__main__":
    unittest.main()
