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


if __name__ == "__main__":
    unittest.main()
