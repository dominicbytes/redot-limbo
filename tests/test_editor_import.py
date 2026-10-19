import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import editor_import as gate


class EditorImportTests(unittest.TestCase):
    def test_only_exact_pinned_editor_shutdown_is_tolerated(self):
        banner = "Redot Engine v" + gate.TEMPORARY["engine_version"] + "\n"
        leaks = "\n".join(gate.TEMPORARY["diagnostics"])
        crash = gate.TEMPORARY["crash_marker"]
        with patch.object(gate, "completed_import", return_value=True):
            for code, output in ((0, banner + leaks), (3221225477, banner + crash)):
                result = gate.assess_import(code, output, False, Path("project"))
                self.assertTrue(result["passed"])
                self.assertTrue(result["temporary_tolerance"])
                for changed in (output + "\nERROR: unexpected diagnostic", output.replace("26.3", "26.2"),
                                output.replace("85e520394", "000000000")):
                    self.assertFalse(gate.assess_import(code, changed, False, Path("project"))["passed"])
                self.assertFalse(gate.assess_import(code, output, True, Path("project"))["passed"])
            self.assertFalse(gate.assess_import(1, banner + crash, False, Path("project"))["passed"])
            self.assertFalse(gate.assess_import(0, banner + leaks + "\n" + leaks, False, Path("project"))["passed"])
        with patch.object(gate, "completed_import", return_value=False):
            self.assertFalse(gate.assess_import(3221225477, banner + crash, False, Path("project"))["passed"])

    def test_completed_import_requires_outputs_and_completion_marker(self):
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            cache = project / ".godot"
            icons = project / "addons/limboai/icons"
            icons.mkdir(parents=True)
            (cache / "imported").mkdir(parents=True)
            (cache / "extension_list.cfg").write_text("res://addons/limboai/bin/limboai.gdextension\n")
            (cache / "global_script_class_cache.cfg").write_text("list=[]")
            (icons / "icon.svg").write_text("<svg/>")
            (icons / "icon.svg.import").write_text('path="res://.godot/imported/icon.ctex"\n')
            marker = "[ DONE ] reimport"
            self.assertFalse(gate.completed_import(project, marker))
            imported = cache / "imported/icon.ctex"
            imported.write_bytes(b"texture")
            self.assertTrue(gate.completed_import(project, marker))
            self.assertFalse(gate.completed_import(project, "not complete"))
            imported.write_bytes(b"")
            self.assertFalse(gate.completed_import(project, marker))

    def test_editor_regression_requires_exact_complete_success(self):
        with patch.object(gate, "completed_import", return_value=True):
            for record in (None, {"passed": True}, {"passed": True, "checks": 0, "failures": []},
                           {"passed": False, "checks": 89, "failures": ["broken"]}):
                output = "" if record is None else "LIMBOAI_EDITOR_RESULT " + json.dumps(record)
                self.assertFalse(gate.assess_import(0, output, False, Path("project"), True)["passed"])
            output = 'LIMBOAI_EDITOR_RESULT {"passed":true,"checks":89,"failures":[]}'
            self.assertTrue(gate.assess_import(0, output, False, Path("project"), True)["passed"])




if __name__ == "__main__":
    unittest.main()
