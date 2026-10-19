from pathlib import Path
import unittest


WORKFLOWS = Path(__file__).resolve().parents[1] / ".github" / "workflows"


class WorkflowGuardTests(unittest.TestCase):
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
                self.assertTrue(block.startswith("    if: ${{ github.repository == 'limbonaut/limboai' }}\n"))


if __name__ == "__main__":
    unittest.main()
