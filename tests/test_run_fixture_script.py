from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "run_fixture.py"
SPEC = importlib.util.spec_from_file_location("run_fixture", SCRIPT_PATH)
assert SPEC is not None and SPEC.loader is not None
RUN_FIXTURE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RUN_FIXTURE)


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
        output = (
            "Redot Engine LTS\n"
            'LIMBOAI_FIXTURE_RESULT {"case_count":13,"failures":[],"passed":true}\n'
        )

        result = RUN_FIXTURE.parse_result_from_output(output)

        self.assertEqual(result["case_count"], 13)
        self.assertTrue(result["passed"])

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


if __name__ == "__main__":
    unittest.main()
