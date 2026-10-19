from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


WORKFLOWS = Path(__file__).resolve().parents[1] / ".github" / "workflows"


class WorkflowGuardTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("pwsh") or shutil.which("powershell"), "PowerShell required")
    def test_windows_audit_rejection_cannot_be_masked_by_later_success(self):
        text = (WORKFLOWS / "redot-desktop.yml").read_text(encoding="utf-8")
        caller = text.split("          & scripts/audit_windows_binary.ps1", 1)[1]
        guard = caller.split("\n", 1)[1].split("          python scripts/run_fixture.py", 1)[0]
        script = "\n".join((
            'param($auditScript, $auditLog)',
            '$ErrorActionPreference = "Stop"',
            'try {',
            '& $auditScript -Library "missing-library.dll" | Tee-Object $auditLog',
            guard,
            "& python -c \"print('LATER_SUCCESS')\"",
            '} catch { [Console]::Error.WriteLine("CALLER_FAILED"); exit 1 }',
        ))
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            caller_path = root / "caller.ps1"
            caller_path.write_text(script, encoding="utf-8")
            result = subprocess.run([
                shutil.which("pwsh") or shutil.which("powershell"),
                "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(caller_path),
                "-auditScript", str(WORKFLOWS.parents[1] / "scripts/audit_windows_binary.ps1"),
                "-auditLog", str(root / "audit.log"),
            ], capture_output=True, text=True, timeout=90)
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("LATER_SUCCESS", result.stdout)
        self.assertIn("FAIL: Windows binary audit failed (", result.stderr)

    def test_audit_pipeline_jobs_explicitly_select_bash(self):
        text = (WORKFLOWS / "redot-desktop.yml").read_text(encoding="utf-8")
        for job in ("linux-x86-64", "macos-universal"):
            block = text.split(f"  {job}:\n", 1)[1].split("    steps:", 1)[0]
            self.assertIn("        shell: bash\n", block)

    def test_inherited_jobs_are_guarded_on_the_fork(self):
        import re
        for name in ("gdextension", "all_builds", "test_builds"):
            text = (WORKFLOWS / (name + ".yml")).read_text(encoding="utf-8")
            self.assertIn("unsupported on Redot", text.splitlines()[0])
            jobs = text.split("jobs:" + chr(10), 1)[1]
            blocks = re.split(r"^  [\w-]+:\n", jobs, flags=re.M)[1:]
            self.assertTrue(blocks)
            for block in blocks:
                self.assertIn("github.repository == 'limbonaut/limboai'", block.splitlines()[0])

    def test_uploads_are_gated_on_scanned_evidence_and_exclude_projects(self):
        text = (WORKFLOWS / "redot-desktop.yml").read_text(encoding="utf-8")
        for platform in ("windows", "linux", "macos"):
            self.assertIn(f"steps.scan_{platform}_evidence.outcome == 'success'", text)
            self.assertIn(f"ci/{platform}-*/run-summary.json", text)
            self.assertNotIn(f"ci/{platform}-*" + chr(10), text)


if __name__ == "__main__":
    unittest.main()
