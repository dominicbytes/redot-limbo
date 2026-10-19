from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest
import sys
import json
from copy import deepcopy
from unittest.mock import patch
import contextlib
import io


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "run_fixture.py"
sys.path.insert(0, str(SCRIPT_PATH.parent))
SPEC = importlib.util.spec_from_file_location("run_fixture", SCRIPT_PATH)
assert SPEC is not None and SPEC.loader is not None
RUN_FIXTURE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RUN_FIXTURE)


def successful_result():
    from fixture_result import EXPECTED_CASE_NAMES
    return {"schema_version": 1, "passed": True, "failures": [],
            "engine": {"string": "test-engine"}, "fixed_delta": 0.016,
            "cases": [{"name": name, "passed": True, "details": {}}
                      for name in sorted(EXPECTED_CASE_NAMES)]}


class ForceReleaseLibraryTests(unittest.TestCase):
    def test_editor_settle_window_is_bounded_and_not_immediate(self) -> None:
        self.assertGreaterEqual(RUN_FIXTURE.EDITOR_SETTLE_FRAMES, 120)

    def test_macos_framework_mapping_selects_inner_binary(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            project = Path(temporary_directory)
            bin_dir = project / "addons" / "limboai" / "bin"
            framework = bin_dir / "liblimboai.macos.template_release.framework"
            framework.mkdir(parents=True)
            binary = framework / "liblimboai.macos.template_release"
            binary.write_bytes(b"macho")
            manifest = bin_dir / "limboai.gdextension"
            manifest.write_text(
                '[libraries]\n\n'
                'macos.debug = "res://addons/limboai/bin/liblimboai.macos.editor.framework"\n'
                'macos.release = "res://addons/limboai/bin/liblimboai.macos.template_release.framework"\n',
                encoding="utf-8",
            )

            selected = RUN_FIXTURE.force_release_library(project, "macos")

            self.assertEqual(selected, binary)
            self.assertIn(
                'macos.debug = "res://addons/limboai/bin/liblimboai.macos.template_release.framework"',
                manifest.read_text(encoding="utf-8"),
            )

    def test_isolated_environment_covers_windows_and_xdg_state(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            state_root = Path(temporary_directory)

            environment = RUN_FIXTURE.isolated_environment(state_root)

            expected = {
                "APPDATA": state_root / "Roaming",
                "LOCALAPPDATA": state_root / "Local",
                "XDG_DATA_HOME": state_root / "share",
                "XDG_CONFIG_HOME": state_root / "config",
                "XDG_CACHE_HOME": state_root / "cache",
            }
            for name, location in expected.items():
                self.assertEqual(Path(environment[name]), location)
                self.assertTrue(location.is_dir())

    def test_parses_exactly_one_machine_readable_stdout_result(self) -> None:
        document = successful_result()
        result = RUN_FIXTURE.parse_result_from_output("Redot Engine LTS\nLIMBOAI_FIXTURE_RESULT " + json.dumps(document))
        self.assertEqual(result, document)

    def test_stdout_result_rejects_missing_or_duplicate_payloads(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "found 0"):
            RUN_FIXTURE.parse_result_from_output("Redot Engine LTS\n")

        duplicate = (
            'LIMBOAI_FIXTURE_RESULT {"passed":true}\n'
            'LIMBOAI_FIXTURE_RESULT {"passed":true}\n'
        )
        with self.assertRaisesRegex(RuntimeError, "found 2"):
            RUN_FIXTURE.parse_result_from_output(duplicate)

    def test_stdout_result_requires_a_json_object(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "must be a JSON object"):
            RUN_FIXTURE.parse_result_from_output("LIMBOAI_FIXTURE_RESULT true\n")


class ResultContractTests(unittest.TestCase):
    def test_empty_failed_compact_and_malformed_results_are_rejected(self):
        from fixture_result import validate_result
        documents = [{}, [], {"passed": True, "case_count": 13, "failures": []}]
        for key, value in (("passed", False), ("cases", []), ("engine", {}),
                           ("fixed_delta", None), ("fixed_delta", True), ("fixed_delta", float("nan")),
                           ("failures", ["failed"]), ("schema_version", 2)):
            result = successful_result()
            result[key] = value
            documents.append(result)
        for document in documents:
            with self.subTest(document=document):
                with self.assertRaises(ValueError):
                    validate_result(document)
                with self.assertRaises((ValueError, RuntimeError)):
                    RUN_FIXTURE.parse_result_from_output(RUN_FIXTURE.RESULT_PREFIX + json.dumps(document))

    def test_inventory_reports_missing_extra_and_duplicates(self):
        from fixture_result import validate_result
        result = successful_result()
        removed = result["cases"].pop()["name"]
        with self.assertRaisesRegex(ValueError, "missing=.*" + removed):
            validate_result(result)
        result = successful_result()
        result["cases"].append({"name": "unexpected_case", "passed": True, "details": {}})
        with self.assertRaisesRegex(ValueError, "extra=.*unexpected_case"):
            validate_result(result)
        result["cases"][-1] = deepcopy(result["cases"][0])
        with self.assertRaisesRegex(ValueError, "duplicate"):
            validate_result(result)

    def test_failed_and_incomplete_cases_are_rejected(self):
        from fixture_result import validate_result
        for key in ("passed", "details", "name"):
            result = successful_result()
            del result["cases"][0][key]
            with self.assertRaises(ValueError):
                validate_result(result)

    def test_comparator_cli_rejects_matching_empty_failed_and_compact_documents(self):
        import compare_fixture_results as compare
        documents = [{}, {"passed": False, "result": successful_result()},
                     {"passed": True, "case_count": 13, "failures": []}]
        missing = successful_result()
        missing["cases"].pop()
        documents.append(missing)
        for document in documents:
            with self.subTest(document=document), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                left, right, output = root / "left.json", root / "right.json", root / "comparison.json"
                left.write_text(json.dumps(document))
                right.write_text(json.dumps(document))
                with patch.object(sys, "argv", ["compare", str(left), str(right), "--output", str(output)]), \
                     contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(compare.main(), 1)
                self.assertFalse(json.loads(output.read_text())["passed"])

    def test_comparator_rejects_failed_outer_run_and_invalid_json(self):
        import compare_fixture_results as compare
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "result.json"
            for document in ({}, {"passed": False, "result": successful_result()},
                             {"passed": True, "result": {"passed": True}}, []):
                path.write_text(json.dumps(document))
                with self.assertRaises(ValueError):
                    compare.load_result(path)
            path.write_text('{"passed":')
            with self.assertRaises(ValueError):
                compare.load_result(path)
            path.write_text(json.dumps(successful_result()))
            self.assertEqual(compare.load_result(path), successful_result())


class EvidenceWriterTests(unittest.TestCase):
    def test_file_and_stdout_paths_use_identical_validation_and_safe_evidence(self):
        from content_policy import text_categories
        for route in ("file", "stdout", "unreadable-file"):
            for valid in (False, True):
                with self.subTest(route=route, valid=valid), tempfile.TemporaryDirectory() as temporary:
                    root = Path(temporary)
                    source = root / "source"
                    fixture = source / "tests/fixture"
                    fixture.mkdir(parents=True)
                    (fixture / "project.godot").write_text("config_version=5")
                    addon = root / "addon"
                    bin_dir = addon / "addons/limboai/bin"
                    bin_dir.mkdir(parents=True)
                    (bin_dir / "limboai.gdextension").write_text("[configuration]")
                    engine = root / "engine"
                    engine.write_bytes(b"engine")
                    output = root / "build/redot-limboai/run"
                    document = successful_result() if valid else {"passed": True, "case_count": 13}
                    if valid:
                        document["cases"][0]["details"]["path"] = str(source)
                    commands = []
                    def run(command, project, environment, timeout):
                        commands.append(command)
                        if "--editor" in command:
                            return 0, "Imported " + str(source), False, 0.1
                        if route in ("file", "unreadable-file"):
                            result_file = output / "state/Roaming/Redot/app_userdata/fixture-result.json"
                            result_file.parent.mkdir(parents=True, exist_ok=True)
                            result_file.write_text(json.dumps(document))
                        return 0, RUN_FIXTURE.RESULT_PREFIX + json.dumps(document), False, 0.1
                    original_read = Path.read_text
                    def read(path, *args, **kwargs):
                        if route == "unreadable-file" and path.name == "fixture-result.json":
                            raise OSError("simulated inaccessible result file")
                        return original_read(path, *args, **kwargs)
                    argv = ["run_fixture.py", "--engine", str(engine), "--addon-project", str(addon),
                            "--output", str(output), "--label", "test"]
                    with patch.object(RUN_FIXTURE, "__file__", str(source / "scripts/run_fixture.py")), \
                         patch.object(RUN_FIXTURE, "run_command", side_effect=run), \
                         patch.object(Path, "read_text", read), \
                         patch.object(sys, "argv", argv), contextlib.redirect_stdout(io.StringIO()):
                        code = RUN_FIXTURE.main()
                    summary = json.loads((output / "run-summary.json").read_text())
                    self.assertEqual(code, 0 if valid else 1)
                    self.assertEqual(summary["passed"], valid)
                    self.assertEqual(summary["result_source"], "file" if route == "file" else "stdout" if valid else None)
                    for name in ("run-summary.json", "fixture.log", "editor-import.log"):
                        text = (output / name).read_text()
                        self.assertFalse(text_categories(text) - {"fixture-evidence"}, name)
                    for command in commands:
                        self.assertIn("--audio-driver", command)
                        self.assertEqual(command[command.index("--audio-driver") + 1], "Dummy")
                        self.assertGreaterEqual(int(command[command.index("--quit-after") + 1]), 2)
                        self.assertNotIn("-d", command)


class ContextDiagnosticTests(unittest.TestCase):
    ERROR = "ERROR: BTTask: Agent or scene root no longer exists."

    def result(self):
        return {"cases": [{"name": "player_context_loss", "passed": True,
                           "details": {"error_counts": [1, 1]}}]}

    def test_counted_context_errors_are_accepted(self):
        self.assertEqual(RUN_FIXTURE.unexpected_diagnostics("", (self.ERROR + "\n") * 2, self.result()), [])

    def test_missing_or_repeated_errors_fail(self):
        for count in [0, 1, 3, 8]:
            self.assertTrue(RUN_FIXTURE.unexpected_diagnostics("", (self.ERROR + "\n") * count, self.result()))

    def test_other_errors_and_import_errors_are_not_hidden(self):
        log = (self.ERROR + "\n") * 2
        for editor, runtime in [(self.ERROR, log), ("", log + "WARNING: unrelated")]:
            self.assertTrue(RUN_FIXTURE.unexpected_diagnostics(editor, runtime, self.result()))

    def test_failed_case_cannot_allow_diagnostics(self):
        result = self.result()
        result["cases"][0]["passed"] = False
        self.assertTrue(RUN_FIXTURE.unexpected_diagnostics("", (self.ERROR + "\n") * 2, result))

    def test_malformed_results_cannot_allow_errors(self):
        for result in [None, {}, {"cases": None}, {"cases": [None]},
                       {"cases": [{"name": "player_context_loss", "passed": True, "details": None}]}]:
            self.assertTrue(RUN_FIXTURE.unexpected_diagnostics("", self.ERROR, result))


if __name__ == "__main__":
    unittest.main()
