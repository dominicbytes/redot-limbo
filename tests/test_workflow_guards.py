from pathlib import Path
import unittest


WORKFLOWS = Path(__file__).resolve().parents[1] / ".github" / "workflows"


class WorkflowGuardTests(unittest.TestCase):
    def test_audit_pipeline_jobs_explicitly_select_bash(self):
        text = (WORKFLOWS / "redot-desktop.yml").read_text(encoding="utf-8")
        for job in ("linux-x86-64", "macos-universal"):
            block = text.split(f"  {job}:\n", 1)[1].split("    steps:", 1)[0]
            self.assertIn("        shell: bash\n", block)


if __name__ == "__main__":
    unittest.main()
