from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest
import sys
import json
from copy import deepcopy


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


if __name__ == "__main__":
    unittest.main()
